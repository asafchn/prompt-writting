"""Metrics for the large-task eval, computed only from results/runs/*.json (grader output + CLI run metadata).

    python3 metrics.py            # writes results/METRICS.md

Definitions
  pass rate      share of runs where the task's hidden grader returned passed=true (all checks, no gaming)
  score          the grader's 0-1 score (share of checks passed; 0 if gaming)
  95% CI         Wilson interval for pass rates; for paired score differences, mean +/- 1.96 x standard error
  cost           total_cost_usd reported by the CLI for the agent session; the skill arm also gets the one-off
                 cost of writing its brief, spread over that task's runs
  time           wall-clock seconds measured by the harness around the agent session
  turns, tokens  as reported by the CLI. A run whose CLI-reported duration is under half its wall time ended
                 with a background job, and the CLI reported only its last exchange; those runs are counted
                 and excluded from the turns/tokens means.
"""
import json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent
RES = HERE / "results"
ARMS = ["generic", "skill"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def words(t):
    import re
    return len(re.findall(r"\b\w[\w'-]*\b", t))


runs = [json.loads(p.read_text()) for p in sorted((RES / "runs").glob("*.json"))]
writer = {p.stem: json.loads(p.read_text()) for p in sorted((RES / "writer").glob("*.json"))}
tasks = sorted({r["task"] for r in runs})
by = defaultdict(list)
for r in runs:
    by[(r["task"], r["arm"])].append(r)


def complete_meta(r):
    a = r["agent"]
    return a.get("duration_ms") and a.get("wall_seconds") and a["duration_ms"] / 1000 >= 0.5 * a["wall_seconds"]


def summarize(rs, task=None, arm=None):
    n = len(rs)
    k = sum(bool(r["grade"].get("passed")) for r in rs)
    sc = [float(r["grade"].get("score", 0)) for r in rs]
    gm = sum(bool(r["grade"].get("gaming")) for r in rs)
    err = sum(bool(r["agent"].get("is_error")) for r in rs)
    cost = [r["agent"].get("total_cost_usd") or 0 for r in rs]
    if arm == "skill" and task:
        wc = writer.get(task, {}).get("total_cost_usd") or 0
        cost = [c + wc / n for c in cost]
    wall = [(r["agent"].get("wall_seconds") or 0) / 60 for r in rs]
    ok = [r for r in rs if complete_meta(r)]
    turns = [r["agent"].get("num_turns") or 0 for r in ok]
    outtok = [((r["agent"].get("usage") or {}).get("output_tokens") or 0) for r in ok]
    return dict(n=n, k=k, ci=wilson(k, n), score=statistics.mean(sc) if sc else 0, gaming=gm, errors=err,
                cost=statistics.mean(cost) if cost else 0, wall=statistics.mean(wall) if wall else 0,
                turns=statistics.mean(turns) if turns else float("nan"),
                outtok=statistics.mean(outtok) if outtok else float("nan"), partial_meta=n - len(ok))


L = ["# Large-task eval: metrics\n",
     "Computed by `metrics.py` from the saved run records only. Grades are the tasks' hidden graders' output.\n",
     f"Runs: {len(runs)}. Agent: Claude Opus 5.5, medium effort, Claude Code headless, max 40 turns.\n",
     "## Per task\n",
     "| task | arm | prompt words | runs | passed | pass rate 95% CI | mean score | gaming | errors | mean cost $ | mean min | mean turns* | mean output tokens* | runs with partial metadata |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for t in tasks:
    for a in ARMS:
        rs = by[(t, a)]
        if not rs:
            continue
        s = summarize(rs, t, a)
        pw = words((HERE / "prompts" / f"{t}__{a}.md").read_text())
        L.append(f"| {t} | {a} | {pw} | {s['n']} | {s['k']}/{s['n']} | {s['ci'][0]:.0%}–{s['ci'][1]:.0%} | {s['score']:.3f} | "
                 f"{s['gaming']} | {s['errors']} | {s['cost']:.2f} | {s['wall']:.1f} | {s['turns']:.1f} | {s['outtok']:,.0f} | {s['partial_meta']} |")

L += ["\n## All tasks\n",
      "| arm | runs | passed | pass rate 95% CI | mean score | gaming | mean cost $ (incl. writing the brief) | mean min |",
      "|---|---|---|---|---|---|---|---|"]
for a in ARMS:
    rs = [r for r in runs if r["arm"] == a]
    parts = [summarize(by[(t, a)], t, a) for t in tasks if by[(t, a)]]
    k = sum(p["k"] for p in parts); n = sum(p["n"] for p in parts); lo, hi = wilson(k, n)
    cost = statistics.mean([p["cost"] for p in parts]); wall = statistics.mean([p["wall"] for p in parts])
    sc = statistics.mean([p["score"] for p in parts]); gm = sum(p["gaming"] for p in parts)
    L.append(f"| {a} | {n} | {k}/{n} | {lo:.1%}–{hi:.1%} | {sc:.3f} | {gm} | {cost:.2f} | {wall:.1f} |")

diffs = []
for t in tasks:
    g = {r["rep"]: float(r["grade"].get("score", 0)) for r in by[(t, "generic")]}
    s = {r["rep"]: float(r["grade"].get("score", 0)) for r in by[(t, "skill")]}
    diffs += [s[i] - g[i] for i in sorted(set(g) & set(s))]
if len(diffs) > 1:
    m = statistics.mean(diffs); sd = statistics.stdev(diffs); se = sd / math.sqrt(len(diffs))
    L.append(f"\n**Paired score difference, skill − generic** (same task, same run index; n={len(diffs)}): "
             f"{m:+.3f}, 95% CI {m - 1.96 * se:+.3f} to {m + 1.96 * se:+.3f}." + (" Every pair is identical, so the difference is exactly zero." if sd == 0 else ""))

L += ["\n## Cost of writing the skill brief (once per task)\n", "| task | writer turns | writer cost $ |", "|---|---|---|"]
for t, w in writer.items():
    L.append(f"| {t} | {w.get('num_turns')} | {w.get('total_cost_usd') or 0:.2f} |")

L.append("\n\\* Turns and output tokens are averaged only over runs with complete CLI metadata. A run whose reported "
         "duration is under half its wall time ended with a background job, and the CLI reported only its final exchange. "
         "Such runs are counted in the last column.")
(RES / "METRICS.md").write_text("\n".join(L) + "\n")
print("\n".join(L))

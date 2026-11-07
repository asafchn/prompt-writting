"""Grade every cached output from the task modules and write REPORT.md + results/metrics.json.

Metrics (see EVAL_PLAN.md):
  task success      share of inputs fully correct; per prompt -> mean over prompts -> macro mean over tasks
  format validity   share of outputs strictly in the requested format
  hard success      task success on edge + adversarial inputs only
  consistency       std of task success across one contender's prompts on a task (mean over tasks)
  cost              written-prompt words; mean downstream seconds
Uncertainty: paired bootstrap (2,000 draws) resampling prompts and inputs within each task;
the same input draw is shared by all contenders, so differences are paired.
Usage: python report2.py [--conds v1,v2,none] [--tasks a,b] [--min-prompts 1]
"""
import json, random, statistics, sys
from collections import defaultdict
from pathlib import Path
from run2 import RES, load_tasks, arg, HERE

LABEL = {"v1": "Skill v1", "v2": "Skill v2", "v3": "Skill v3", "none": "No skill", "request": "Raw request as prompt"}
SPLIT = {}
for line in (HERE / "split.txt").read_text().splitlines():
    name, rest = line.split(":", 1)
    for t in eval(rest.strip()):
        SPLIT[t] = name.strip()


def collect(mods, conds):
    """data[task][cond][k][item_id] = grade dict (+difficulty)"""
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    items_by_task, meta = {}, defaultdict(list)
    for m in mods:
        items = {it["id"]: it for it in m.build()}
        items_by_task[m.ID] = items
        for f in (RES / "outputs").glob(f"{m.ID}__*.json"):
            _, cond, k, iid = f.stem.split("__")
            if cond not in conds or iid not in items:
                continue
            d = json.loads(f.read_text())
            if d["output"] == "__ERROR__":
                continue
            g = m.grade(d["output"], items[iid])
            g["difficulty"] = items[iid]["difficulty"]
            data[m.ID][cond][int(k)][iid] = g
            if d.get("secs"):
                meta[(cond, "secs")].append(d["secs"])
        for cond in conds:
            for p in (RES / "prompts").glob(f"{m.ID}__{cond}__*.json"):
                meta[(cond, "words")].append(len(json.loads(p.read_text())["prompt"].split()))
    return data, items_by_task, meta


def common_items(data, task, conds):
    """inputs answered by every prompt of every contender (keeps comparisons paired)"""
    sets = [set(v) for c in conds for v in data[task][c].values()]
    return sorted(set.intersection(*sets)) if sets else []


def score(data, task, cond, iids, field="correct", ks=None, filt=None):
    per_prompt = []
    for k, grades in data[task][cond].items():
        if ks is not None and k not in ks:
            continue
        sel = [i for i in iids if filt is None or filt(grades[i])]
        if sel:
            per_prompt.append(sum(grades[i][field] for i in sel) / len(sel))
    return per_prompt


def macro(data, tasks, cond, iids_by_task, **kw):
    vals = [statistics.mean(s) for t in tasks if (s := score(data, t, cond, iids_by_task[t], **kw))]
    return statistics.mean(vals) if vals else float("nan")


def bootstrap(data, tasks, conds, iids_by_task, n=2000, seed=0):
    rnd = random.Random(seed)
    draws = {c: [] for c in conds}
    for _ in range(n):
        per = {c: [] for c in conds}
        for t in tasks:
            iids = iids_by_task[t]
            samp = [rnd.choice(iids) for _ in iids]
            for c in conds:
                ks = list(data[t][c])
                kk = [rnd.choice(ks) for _ in ks]
                per[c].append(statistics.mean(sum(data[t][c][k][i]["correct"] for i in samp) / len(samp) for k in kk))
        for c in conds:
            draws[c].append(statistics.mean(per[c]))
    return draws


def ci(xs):
    s = sorted(xs)
    return s[int(0.025 * len(s))], s[int(0.975 * len(s)) - 1]


def pct(x):
    return f"{100 * x:.1f}%"


if __name__ == "__main__":
    conds = arg("--conds", "v1,v2,none").split(",")
    ids = arg("--tasks").split(",") if arg("--tasks") else None
    mods = load_tasks(ids)
    data, items_by_task, meta = collect(mods, conds)
    min_k = int(arg("--min-prompts", "1"))
    tasks = [m.ID for m in mods if all(len(data[m.ID][c]) >= min_k for c in conds)]
    iids = {t: common_items(data, t, conds) for t in tasks}
    tasks = [t for t in tasks if iids[t]]
    hard = lambda g: g["difficulty"] != "standard"
    out = [f"# Round 2 report\n", f"Contenders: {', '.join(LABEL[c] for c in conds)}. Tasks: {len(tasks)}. "
           f"Inputs per task (paired across contenders): {', '.join(f'{t} {len(iids[t])}' for t in tasks)}.\n"]

    draws = bootstrap(data, tasks, conds, iids)
    out += ["## Headline metrics (macro average over tasks)\n",
            "| Metric | " + " | ".join(LABEL[c] for c in conds) + " |", "|---" * (len(conds) + 1) + "|"]
    row = lambda name, f: out.append(f"| {name} | " + " | ".join(f(c) for c in conds) + " |")
    row("**Task success** (95% CI)", lambda c: f"**{pct(macro(data, tasks, c, iids))}** ({pct(ci(draws[c])[0])}–{pct(ci(draws[c])[1])})")
    row("Hard-input success", lambda c: pct(macro(data, tasks, c, iids, filt=hard)))
    row("Format validity", lambda c: pct(macro(data, tasks, c, iids, field="format_ok")))
    row("Consistency (std across prompts)", lambda c: f"{100 * statistics.mean([statistics.pstdev(s) for t in tasks if len(s := score(data, t, c, iids[t])) > 1] or [float('nan')]):.1f} pts")
    row("Written prompt length (words)", lambda c: f"{statistics.mean(meta[(c, 'words')]):.0f}" if meta[(c, 'words')] else "-")
    row("Mean downstream seconds", lambda c: f"{statistics.mean(meta[(c, 'secs')]):.0f}" if meta[(c, 'secs')] else "-")

    out += ["\n## Paired differences (task success, 95% bootstrap CI)\n", "| Comparison | Difference | CI | Verdict |", "|---|---|---|---|"]
    pairs = [(a, b) for a in conds for b in conds if a != b and conds.index(a) < conds.index(b)]
    for a, b in pairs:
        d = [x - y for x, y in zip(draws[a], draws[b])]
        lo, hi = ci(d)
        diff = macro(data, tasks, a, iids) - macro(data, tasks, b, iids)
        verdict = f"{LABEL[a]} better" if lo > 0 else f"{LABEL[b]} better" if hi < 0 else "no detectable difference"
        out.append(f"| {LABEL[a]} − {LABEL[b]} | {100 * diff:+.1f} pts | {100 * lo:+.1f} to {100 * hi:+.1f} | {verdict} |")

    out += ["\n## By task (task success; [train]/[held-out] split)\n", "| Task | " + " | ".join(LABEL[c] for c in conds) + " |", "|---" * (len(conds) + 1) + "|"]
    for t in tasks:
        out.append(f"| {t} [{SPLIT.get(t, '?')}] | " + " | ".join(
            f"{pct(statistics.mean(s))}" + (f" ({', '.join(f'{100*x:.0f}' for x in s)})" if len(s) > 1 else "")
            for c in conds for s in [score(data, t, c, iids[t])]) + " |")

    out += ["\n## By difficulty (macro)\n", "| Difficulty | " + " | ".join(LABEL[c] for c in conds) + " |", "|---" * (len(conds) + 1) + "|"]
    for diff in ("standard", "edge", "adversarial"):
        out.append(f"| {diff} | " + " | ".join(pct(macro(data, tasks, c, iids, filt=lambda g, d=diff: g["difficulty"] == d)) for c in conds) + " |")

    # inputs nobody gets right: candidates for a broken gold or grader
    suspects = []
    for t in tasks:
        for i in iids[t]:
            if all(not data[t][c][k][i]["correct"] for c in conds for k in data[t][c]):
                g = next(iter(data[t][conds[0]].values()))[i]
                suspects.append(f"- {i} ({g['difficulty']}): {g['detail'][:160]}")
    out += ["\n## Inputs every prompt failed (audit candidates)\n"] + (suspects or ["None."])
    (HERE / "REPORT.md").write_text("\n".join(out))
    metrics = {"conds": conds, "tasks": tasks,
               "task_success": {c: {t: statistics.mean(score(data, t, c, iids[t])) for t in tasks} for c in conds},
               "macro": {c: macro(data, tasks, c, iids) for c in conds},
               "ci": {c: ci(draws[c]) for c in conds},
               "hard": {c: macro(data, tasks, c, iids, filt=hard) for c in conds},
               "format": {c: macro(data, tasks, c, iids, field="format_ok") for c in conds}}
    (RES / "metrics.json").parent.mkdir(exist_ok=True, parents=True)
    (RES / "metrics.json").write_text(json.dumps(metrics, indent=1))
    print("\n".join(out))

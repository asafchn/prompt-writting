"""Large-task eval: does rewriting an ordinary 100-word request with the skill help an autonomous agent?

Two arms per task, two fixed prompts prepared in advance:
  generic  the ordinary developer's request, tasks/<id>/start_prompt.md, given to the agent as is
  skill    the same request, rewritten once by Claude with the prompt-writing-large-tasks skill loaded
           (the writer may read the workspace, read-only)

Usage
  python run_large.py prepare                 # writes prompts/<task>__generic.md and prompts/<task>__skill.md
  python run_large.py run --reps 6            # agent runs on both prompts, graded after each run
  python run_large.py report                  # results/REPORT.md
  common flags: --tasks a,b  --workers 6
Requires the `claude` CLI (Claude Code), logged in.
"""
import json, os, re, shutil, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parent.parent
TASKS = HERE / "tasks"
PROMPTS = HERE / "prompts"
RES = HERE / "results"
WORK = Path(os.environ.get("LARGE_EVAL_WORK", "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/large-eval-runs"))
MODEL = "claude-opus-5-5"
EFFORT = "medium"
MAX_TURNS = 40
AGENT_TOOLS = "Bash,Read,Edit,Write,Glob,Grep"
SKILL = REPO / "skills" / "prompt-writing-large-tasks" / "SKILL.md"
ARMS = ["generic", "skill"]

# What the writer is told about the agent's environment: the facts a user would answer if the skill asked.
ENVIRONMENT = ("The agent is Claude Code running headless in a copy of this folder (its current directory), with "
               "shell and file tools (Bash, Read, Edit, Write, Glob, Grep), Python 3 standard library only, no "
               "internet, and at most 40 turns. Nobody will answer questions while it works.")
WRITER_SYS = "You are Claude, an AI assistant made by Anthropic. Help the user with their request."
WRITER_ASK = ("\n\n---\nI want to hand the request above to an autonomous coding agent. Write the brief I should give it "
              "instead. The project folder is your current directory: read whatever you need, but don't change "
              "anything. " + ENVIRONMENT + " I won't be around to answer questions, so make reasonable assumptions. "
              "Put the brief, and only the brief, between <final_prompt> and </final_prompt>.")


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def task_ids():
    ids = sorted(p.name for p in TASKS.iterdir() if (p / "start_prompt.md").exists())
    sel = arg("--tasks")
    return [t for t in ids if not sel or t in sel.split(",")]


def claude(prompt, cwd, tools, max_turns, system=None, timeout=2400):
    cmd = ["claude", "-p", prompt, "--tools", tools, "--allowedTools", tools, "--setting-sources", "",
           "--max-turns", str(max_turns), "--model", MODEL, "--effort", EFFORT, "--output-format", "json"]
    if system:
        cmd += ["--system-prompt", system]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)
        out = json.loads(r.stdout)
    except subprocess.TimeoutExpired:
        out = {"is_error": True, "subtype": "timeout", "result": ""}
    except Exception as e:  # unparseable output
        out = {"is_error": True, "subtype": f"harness_error: {e}", "result": ""}
    out["wall_seconds"] = round(time.time() - t, 1)
    return out


def fresh_copy(task, dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(TASKS / task / "workspace", dest)
    return dest


def prepare(task):
    PROMPTS.mkdir(exist_ok=True)
    start = (TASKS / task / "start_prompt.md").read_text().strip()
    (PROMPTS / f"{task}__generic.md").write_text(start + "\n")
    out_path = PROMPTS / f"{task}__skill.md"
    if out_path.exists():
        return
    ws = fresh_copy(task, WORK / "writer" / task)
    system = WRITER_SYS + ("\n\nA skill has been loaded for this request. Follow its instructions:\n"
                           "<skill name=\"prompt-writing-large-tasks\">\n" + SKILL.read_text() + "\n</skill>")
    res = claude(start + WRITER_ASK, ws, "Read,Glob,Grep", 30, system=system)
    raw = res.get("result", "")
    m = re.findall(r"<final_prompt>(.*?)</final_prompt>", raw, re.S)
    brief = (m[-1] if m else raw).strip()
    brief = re.sub(r"^```[\w-]*\n(.*)\n```$", r"\1", brief, flags=re.S).strip()
    (RES / "writer").mkdir(parents=True, exist_ok=True)
    (RES / "writer" / f"{task}.json").write_text(json.dumps(res, indent=1))
    if not brief or res.get("is_error"):
        raise RuntimeError(f"{task}: writer failed ({res.get('subtype')})")
    out_path.write_text(brief + "\n")


def run_one(task, arm, rep):
    out = RES / "runs" / f"{task}__{arm}__{rep}.json"
    if out.exists():
        return json.loads(out.read_text())
    ws = fresh_copy(task, WORK / "runs" / f"{task}__{arm}__{rep}")
    prompt = (PROMPTS / f"{task}__{arm}.md").read_text()
    res = claude(prompt, ws, AGENT_TOOLS, MAX_TURNS)
    g = subprocess.run([sys.executable, "grader.py", str(ws)], cwd=TASKS / task, capture_output=True, text=True, timeout=600)
    try:
        grade = json.loads(g.stdout.strip().splitlines()[-1])
    except Exception:
        grade = {"score": 0.0, "passed": False, "checks": {}, "gaming": False, "notes": "grader error: " + (g.stderr or g.stdout)[-300:]}
    rec = {"task": task, "arm": arm, "rep": rep, "grade": grade,
           "agent": {k: res.get(k) for k in ("num_turns", "duration_ms", "total_cost_usd", "is_error", "subtype", "wall_seconds", "usage")},
           "final_message": res.get("result", "")[-3000:]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1))
    print(f"  {task} {arm} {rep}: score {grade.get('score')} passed {grade.get('passed')} turns {res.get('num_turns')}", flush=True)
    return rec


def report():
    rows = [json.loads(p.read_text()) for p in sorted((RES / "runs").glob("*.json"))]
    words = lambda t: len(re.findall(r"\b\w[\w'-]*\b", t))
    lines = ["# Large-task eval: generic request vs skill-rewritten brief\n",
             f"Agent: {MODEL} at {EFFORT} effort, Claude Code headless, max {MAX_TURNS} turns, tools {AGENT_TOOLS}.\n",
             "| task | arm | prompt words | runs | mean score | passed | gaming | mean turns | mean minutes | mean cost $ |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    summary = {}
    for t in sorted({r["task"] for r in rows}):
        for a in ARMS:
            rs = [r for r in rows if r["task"] == t and r["arm"] == a]
            if not rs:
                continue
            sc = [r["grade"].get("score", 0) for r in rs]
            summary.setdefault(a, []).append(statistics.mean(sc))
            pw = words((PROMPTS / f"{t}__{a}.md").read_text())
            mt = statistics.mean([(r["agent"].get("num_turns") or 0) for r in rs])
            mm = statistics.mean([(r["agent"].get("wall_seconds") or 0) for r in rs]) / 60
            mc = statistics.mean([(r["agent"].get("total_cost_usd") or 0) for r in rs])
            lines.append(f"| {t} | {a} | {pw} | {len(rs)} | {statistics.mean(sc):.2f} | {sum(bool(r['grade'].get('passed')) for r in rs)}/{len(rs)} | "
                         f"{sum(bool(r['grade'].get('gaming')) for r in rs)} | {mt:.0f} | {mm:.1f} | {mc:.2f} |")
    lines.append("\n**Skill arm, cost of writing the brief (once per task, read-only exploration):** " + ", ".join(
        f"{p.stem}: {json.loads(p.read_text()).get('num_turns')} turns, ${json.loads(p.read_text()).get('total_cost_usd') or 0:.2f}"
        for p in sorted((RES / "writer").glob("*.json"))))
    lines.append("\n**Mean score over tasks (each task weighted equally):** " +
                 ", ".join(f"{a}: {statistics.mean(v):.2f}" for a, v in summary.items()))
    # paired by task and rep
    diffs = []
    for t in sorted({r["task"] for r in rows}):
        for rep in sorted({r["rep"] for r in rows}):
            g = [r for r in rows if r["task"] == t and r["rep"] == rep]
            d = {r["arm"]: r["grade"].get("score", 0) for r in g}
            if len(d) == 2:
                diffs.append(d["skill"] - d["generic"])
    if len(diffs) > 1:
        m = statistics.mean(diffs); se = statistics.stdev(diffs) / len(diffs) ** 0.5
        lines.append(f"\n**Paired difference (skill - generic):** {m:+.3f} ± {se:.3f} (one standard error, n={len(diffs)} pairs); "
                     f"95% CI roughly {m - 1.96 * se:+.3f} to {m + 1.96 * se:+.3f}.")
    lines.append("\n## Per-check pass rates\n")
    for t in sorted({r["task"] for r in rows}):
        checks = sorted({c for r in rows if r["task"] == t for c in r["grade"].get("checks", {})})
        if not checks:
            continue
        lines.append(f"**{t}**\n\n| check | generic | skill |\n|---|---|---|")
        for c in checks:
            cells = []
            for a in ARMS:
                rs = [r for r in rows if r["task"] == t and r["arm"] == a]
                cells.append(f"{sum(bool(r['grade'].get('checks', {}).get(c)) for r in rs)}/{len(rs)}")
            lines.append(f"| {c} | {cells[0]} | {cells[1]} |")
        lines.append("")
    (RES / "REPORT.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    mode = sys.argv[1]
    ids = task_ids()
    workers = int(arg("--workers", "6"))
    if mode == "prepare":
        with ThreadPoolExecutor(5) as ex:
            list(ex.map(prepare, ids))
        print("prepared:", ", ".join(ids))
    elif mode == "run":
        reps = int(arg("--reps", "6"))
        jobs = [(t, a, r) for r in range(reps) for t in ids for a in ARMS]
        print(f"running {len(jobs)} agent sessions", flush=True)
        with ThreadPoolExecutor(workers) as ex:
            list(ex.map(lambda j: run_one(*j), jobs))
        report()
    elif mode == "regrade":  # re-score every saved workspace with the current graders
        for f in sorted((RES / "runs").glob("*.json")):
            rec = json.loads(f.read_text())
            ws = WORK / "runs" / f.stem
            g = subprocess.run([sys.executable, "grader.py", str(ws)], cwd=TASKS / rec["task"], capture_output=True, text=True, timeout=600)
            new = json.loads(g.stdout.strip().splitlines()[-1])
            if (new.get("score"), new.get("passed")) != (rec["grade"].get("score"), rec["grade"].get("passed")):
                print(f"  {f.stem}: {rec['grade'].get('score')} -> {new.get('score')}")
            rec["grade"] = new
            f.write_text(json.dumps(rec, indent=1))
        report()
    elif mode == "report":
        report()
    else:
        sys.exit(__doc__)

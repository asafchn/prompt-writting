"""Round-2 runner: write prompts, run them downstream, cache everything. Grading happens in report2.py,
straight from each task module, so fixing a gold or grader never requires re-running models.

Conditions
  v1, v2, v3  Opus 5.5 writes the prompt with that skill version loaded
  none        Opus 5.5 writes the prompt with no skill
  request     no writer: the user's raw REQUEST text is used as the system prompt (reference + gold audit)

Usage
  python run2.py pilot                       # 1 prompt per condition, 10 inputs per task
  python run2.py wave --prompts 0,1          # prompts k=0,1 on all 50 inputs
  python run2.py wave --prompts 2,3 --tasks a,b
  python run2.py audit                       # request-as-prompt on every input (gold audit)
  common flags: --conds v1,v2,none  --tasks id1,id2  --workers 24
Requires the `claude` CLI (Claude Code), logged in.
"""
import importlib, json, os, re, subprocess, sys, tempfile, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
REPO = HERE.parent.parent
RES = HERE / "results"
WRITER_MODEL = DOWN_MODEL = "claude-opus-5-5"
DOWN_EFFORT = "medium"       # see EVAL_PLAN.md: same for every condition
TASK_MODULES = ["refund_decisions", "order_pricing", "ticket_routing", "sql_analytics", "pii_redaction",
                "claim_extraction", "meeting_actions", "kb_support", "scheduling", "tool_calling"]
SKILL_FILES = {"v1": REPO / "comparison/skill-v1/SKILL.md", "v2": REPO / "comparison/skill-v2/SKILL.md",
               "v3": REPO / "comparison/skill-v3/SKILL.md"}
WRITER_SYS = "You are Claude, an AI assistant made by Anthropic. Help the user with their request."
WRITER_SUFFIX = ("\n\n(I won't be around to answer follow-up questions, so make reasonable assumptions. "
                 "Put the final text I should use, and only that, between <final_prompt> and </final_prompt> "
                 "tags; anything else you want to say can go outside the tags.)")
EMPTY = Path(tempfile.mkdtemp(prefix="pw-eval2-"))
PILOT_PICK = list(range(0, 4)) + list(range(20, 24)) + [40, 41]   # 4 standard, 4 edge, 2 adversarial


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def load_tasks(ids=None):
    mods = []
    for m in TASK_MODULES:
        try:
            mod = importlib.import_module(f"tasks.{m}")
        except ModuleNotFoundError:
            continue
        if ids is None or mod.ID in ids:
            mods.append(mod)
    return mods


def claude(prompt, system, model, effort=None, timeout=900):
    cmd = ["claude", "-p", prompt, "--system-prompt", system, "--tools", "", "--disable-slash-commands",
           "--setting-sources", "", "--model", model]
    if effort:
        cmd += ["--effort", effort]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    for attempt in range(4):
        try:
            t = time.time()
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=EMPTY, env=env)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip(), round(time.time() - t, 1)
        except subprocess.TimeoutExpired:
            pass
        time.sleep(5 * (attempt + 1))
    return "__ERROR__", None


def cached(path, fn):
    path = Path(path)
    if path.exists():
        d = json.loads(path.read_text())
        if d.get("output", d.get("raw")) != "__ERROR__":
            return d
    out = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1))
    return out


def extract_prompt(raw):
    m = re.findall(r"<final_prompt>(.*?)</final_prompt>", raw, re.S)
    p = m[-1].strip() if m else raw.strip()
    f = re.fullmatch(r"```[\w-]*\n(.*)\n```", p, re.S)
    return f.group(1).strip() if f else p


def get_prompt(mod, cond, k):
    if cond == "request":
        return mod.REQUEST
    def fn():
        sys_p = WRITER_SYS
        if cond in SKILL_FILES:
            sys_p += ("\n\nA skill has been loaded for this request. Follow its instructions:\n"
                      "<skill name=\"prompt-writing\">\n" + SKILL_FILES[cond].read_text() + "\n</skill>")
        raw, secs = claude(mod.REQUEST + WRITER_SUFFIX, sys_p, WRITER_MODEL)
        return {"raw": raw, "prompt": extract_prompt(raw), "secs": secs}
    return cached(RES / "prompts" / f"{mod.ID}__{cond}__{k}.json", fn)["prompt"]


def run_item(mod, cond, k, item):
    def fn():
        out, secs = claude(item["input"], get_prompt(mod, cond, k), DOWN_MODEL, DOWN_EFFORT)
        return {"output": out, "secs": secs}
    return cached(RES / "outputs" / f"{mod.ID}__{cond}__{k}__{item['id']}.json", fn)


def pool(fn, jobs, workers):
    done = [0]
    def wrap(a):
        r = fn(*a); done[0] += 1
        if done[0] % 50 == 0:
            print(f"  {done[0]}/{len(jobs)}", flush=True)
        return r
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(wrap, jobs))


if __name__ == "__main__":
    mode = sys.argv[1]
    ids = arg("--tasks").split(",") if arg("--tasks") else None
    mods = load_tasks(ids)
    conds = arg("--conds", "v1,v2,none").split(",")
    workers = int(arg("--workers", "24"))
    if mode == "pilot":
        ks, pick = [0], PILOT_PICK
    elif mode == "wave":
        ks, pick = [int(x) for x in arg("--prompts", "0,1").split(",")], None
    elif mode == "audit":
        conds, ks, pick = ["request"], [0], None
    else:
        sys.exit(__doc__)
    # write prompts first (parallel), then run items
    pool(get_prompt, [(m, c, k) for m in mods for c in conds if c != "request" for k in ks], min(workers, 12))
    print("prompts ready", flush=True)
    jobs = []
    for m in mods:
        items = m.build()
        sel = [items[i] for i in pick] if pick else items
        jobs += [(m, c, k, it) for c in conds for k in ks for it in sel]
    print(f"running {len(jobs)} downstream calls", flush=True)
    pool(run_item, jobs, workers)
    print("done", flush=True)

"""End-to-end quality eval for the prompt-writing skill.

Stage 1 (write):  Opus writes a prompt for each case, with and without the skill.
Stage 2 (run):    each written prompt drives Haiku on the case's test inputs.
Stage 3 (grade):  code checks + a blind Opus judge score Haiku's outputs.
Every call is cached to results/, so the script can be re-run safely.
Usage: python run.py [write|run|grade|all] [--samples N] [--conds with_skill,with_skill_v2,without_skill]
Requires the `claude` CLI (Claude Code) on PATH, logged in.
"""
import json, os, re, subprocess, sys, hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
RES = HERE / "results"
CASES = json.loads((HERE / "cases.json").read_text())
REPO = HERE.parent.parent
SKILLS = {"with_skill": (REPO / "comparison/skill-v1/SKILL.md").read_text(),
          "with_skill_v2": (REPO / "comparison/skill-v2/SKILL.md").read_text()}
WRITER_MODEL, DOWN_MODEL, JUDGE_MODEL = "claude-opus-5-5", "claude-haiku-5-5", "claude-opus-5-5"
SAMPLES = int(sys.argv[sys.argv.index("--samples") + 1]) if "--samples" in sys.argv else 3
CONDS = (sys.argv[sys.argv.index("--conds") + 1].split(",") if "--conds" in sys.argv
         else ["with_skill", "with_skill_v2", "without_skill"])
import tempfile
EMPTY = Path(tempfile.mkdtemp(prefix="pw-eval-"))  # empty cwd so no CLAUDE.md or project files leak in

WRITER_SYS = "You are Claude, an AI assistant made by Anthropic. Help the user with their request."
def skill_block(cond):
    return ("\n\nA skill has been loaded for this request. Follow its instructions:\n"
            "<skill name=\"prompt-writing\">\n" + SKILLS[cond] + "\n</skill>")
WRITER_SUFFIX = ("\n\n(I won't be around to answer follow-up questions, so make reasonable assumptions. "
                 "Put the final text I should use, and only that, between <final_prompt> and </final_prompt> "
                 "tags; anything else you want to say can go outside the tags.)")

JUDGE_SYS = """You grade the behaviour of an AI assistant that was deployed with instructions written for a user.
You see the user's original request (their intent), then several test inputs. For each test input you get a rubric
written from that intent and the assistant's actual output. Decide strictly whether the output satisfies the rubric.
Judge only what the output does; ignore length and style unless the rubric mentions them.
Reply with JSON only, no code fences: {"results": [{"i": <index>, "pass": true|false, "reason": "<one sentence>"}]}"""


def claude(prompt, system, model, timeout=600):
    cmd = ["claude", "-p", prompt, "--system-prompt", system, "--tools", "",
           "--disable-slash-commands", "--setting-sources", "", "--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    for attempt in range(3):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=EMPTY, env=env)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip()
        except subprocess.TimeoutExpired:
            pass
    return "__ERROR__"


def cached(path, fn):
    path = Path(path)
    if path.exists():
        return json.loads(path.read_text())
    out = fn()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1))
    return out


def extract(raw):
    m = re.findall(r"<final_prompt>(.*?)</final_prompt>", raw, re.S)
    p = m[-1].strip() if m else raw.strip()
    # strip a code fence wrapping the whole prompt
    f = re.fullmatch(r"```[\w-]*\n(.*)\n```", p, re.S)
    return f.group(1).strip() if f else p


# ---------- stage 1
GENERIC = json.loads((HERE / "generic_prompts.json").read_text())


def write_one(case, cond, k):
    if cond == "generic":  # hand-written baseline, no writer model
        return {"raw": GENERIC[case["id"]], "prompt": GENERIC[case["id"]]}
    def fn():
        sys_p = WRITER_SYS + (skill_block(cond) if cond in SKILLS else "")
        raw = claude(case["request"] + WRITER_SUFFIX, sys_p, WRITER_MODEL)
        return {"raw": raw, "prompt": extract(raw)}
    return cached(RES / "prompts" / f"{case['id']}__{cond}__{k}.json", fn)


# ---------- stage 2
INPUT_TAGS = {"review", "ticket", "notes", "demo_notes", "diff", "pr_diff", "input", "message",
              "customer_message", "user_message", "question", "customer", "query"}
PLACEHOLDER = re.compile(r"\{\{\s*[\w ]+\s*\}\}|\{[A-Za-z_][\w]*\}|\[(?:REVIEW|INSERT[^\]]*|review text[^\]]*)\]")


def run_one(case, cond, k, i):
    def fn():
        p = write_one(case, cond, k)["prompt"]
        inp = case["inputs"][i]["text"]
        # honour the input wrapper the prompt itself says it will receive (e.g. <review>...</review>)
        tag = next((t for t in re.findall(r"<([a-z][\w-]*)>", p.lower()) if t in INPUT_TAGS), None)
        if PLACEHOLDER.search(p):  # template-style prompt: substitute the input, send as one message
            msg = PLACEHOLDER.sub(lambda _: inp, p, count=1)
            out = claude(msg, "You are a helpful assistant.", DOWN_MODEL)
            mode = "template"
        else:
            if tag:
                inp = f"<{tag}>\n{inp}\n</{tag}>"
            out = claude(inp, p, DOWN_MODEL)
            mode = "system"
        return {"output": out, "mode": mode}
    return cached(RES / "outputs" / f"{case['id']}__{cond}__{k}__{i}.json", fn)


# ---------- stage 3
SENT = {"pos": "pos", "positive": "pos", "neg": "neg", "negative": "neg", "mixed": "mixed"}
ALLOWED_TOPICS = {"shipping", "quality", "price", "support"}
BANNED = ["synergy", "synergies", "leverage", "leveraging", "circle back", "circling back", "touch base",
          "touching base", "game-changer", "game changer"]


def check_tagger(case, outs):
    parsed, res = [], []
    for o in outs:
        try:
            d = json.loads(o)
            parsed.append(d if isinstance(d, dict) else None)
        except Exception:
            parsed.append(None)
    keysets = {tuple(sorted(d.keys())) for d in parsed if d}
    consistent = len(keysets) == 1 and all(parsed)
    for inp, d in zip(case["inputs"], parsed):
        r = {"valid_json": d is not None, "same_keys": consistent}
        if d:
            sk = next((x for x in d if "sentiment" in x.lower()), None)
            tk = next((x for x in d if "topic" in x.lower()), None)
            sv = SENT.get(str(d.get(sk, "")).lower().strip())
            tv = d.get(tk)
            tv = [str(t).lower() for t in tv] if isinstance(tv, list) else None
            r["allowed_values"] = sv is not None and tv is not None and set(tv) <= ALLOWED_TOPICS
            r["correct_labels"] = (r["allowed_values"]
                                   and (inp["gold_sentiment"] is None or sv in (inp["gold_sentiment"] if isinstance(inp["gold_sentiment"], list) else [inp["gold_sentiment"]]))
                                   and set(inp["gold_topics_must"]) <= set(tv or []))
        else:
            r["allowed_values"] = r["correct_labels"] = False
        r["pass"] = all(r.values())
        res.append(r)
    return res


def check_email(o):
    body = "\n".join(l for l in o.splitlines() if not l.lower().startswith("subject:"))
    words = len(re.findall(r"\b\w[\w'-]*\b", body))
    low = o.lower()
    return {"under_120_words": words <= 120, "no_buzzwords": not any(b in low for b in BANNED), "words": words}


def judge(case, outs):
    parts = [f"USER'S ORIGINAL REQUEST (intent):\n{case['request']}\n"]
    for i, (inp, o) in enumerate(zip(case["inputs"], outs)):
        parts.append(f"=== TEST {i}\nINPUT:\n{inp['text']}\nRUBRIC:\n{inp['rubric']}\nOUTPUT:\n{o}\n")
    raw = claude("\n".join(parts), JUDGE_SYS, JUDGE_MODEL)
    try:
        m = re.search(r"\{.*\}", raw, re.S)
        return {r["i"]: r for r in json.loads(m.group(0))["results"]}
    except Exception:
        return {"__error__": raw}


def grade_one(case, cond, k):
    def fn():
        outs = [run_one(case, cond, k, i)["output"] for i in range(len(case["inputs"]))]
        kind = case.get("programmatic")
        if kind == "json_tagger":
            return {"items": check_tagger(case, outs)}
        j = judge(case, outs)
        items = []
        for i, o in enumerate(outs):
            jr = j.get(i) or j.get(str(i)) or {"pass": False, "reason": "judge missing"}
            it = {"judge_pass": bool(jr.get("pass")), "reason": jr.get("reason", "")}
            if kind == "email":
                it.update(check_email(o))
                it["pass"] = it["judge_pass"] and it["under_120_words"] and it["no_buzzwords"]
            else:
                it["pass"] = it["judge_pass"]
            items.append(it)
        return {"items": items}
    return cached(RES / "grades" / f"{case['id']}__{cond}__{k}.json", fn)


def pool(fn, jobs, workers=12):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(lambda a: fn(*a), jobs))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    combos = [(c, cond, k) for c in CASES for cond in CONDS for k in range(SAMPLES)]
    if stage in ("write", "all"):
        pool(write_one, combos); print("written", len(combos), flush=True)
    if stage in ("run", "all"):
        jobs = [(c, cond, k, i) for c, cond, k in combos for i in range(len(c["inputs"]))]
        pool(run_one, jobs, 16); print("ran", len(jobs), flush=True)
    if stage in ("grade", "all"):
        pool(grade_one, combos, 10); print("graded", len(combos), flush=True)

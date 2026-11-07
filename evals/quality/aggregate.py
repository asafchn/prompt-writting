"""Aggregate grades into per-case and overall pass rates for each condition.
The unit of analysis is a written prompt (its pass rate over the case's test inputs), because
test items under one prompt are not independent. Standard errors are over prompts."""
import json, math
from collections import defaultdict
from pathlib import Path
from run import CASES, RES, SAMPLES

CONDS = ["with_skill_v2", "with_skill", "without_skill"]
LABEL = {"with_skill_v2": "skill v2", "with_skill": "skill v1", "without_skill": "no skill"}


def se(xs):
    if len(xs) < 2: return 0.0
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1) / len(xs))


def fmt(xs):
    return f"{100*sum(xs)/len(xs):.0f}% +/- {100*se(xs):.0f}" if xs else "-"


rates, per_item, lengths, fails = {}, defaultdict(lambda: defaultdict(list)), defaultdict(list), []
for c in CASES:
    for cond in CONDS:
        rs = []
        for k in range(SAMPLES):
            g = RES / "grades" / f"{c['id']}__{cond}__{k}.json"
            if not g.exists(): continue
            items = json.loads(g.read_text())["items"]
            rs.append(sum(it["pass"] for it in items) / len(items))
            for i, it in enumerate(items):
                per_item[(c["id"], i)][cond].append(it["pass"])
                if not it["pass"]:
                    fails.append([c["id"], cond, k, i, {x: v for x, v in it.items() if x != "pass"}])
            p = json.loads((RES / "prompts" / f"{c['id']}__{cond}__{k}.json").read_text())["prompt"]
            lengths[(c["id"], cond)].append(len(p.split()))
        rates[(c["id"], cond)] = rs

out = ["## Pass rate by case (mean over written prompts, +/- standard error)\n",
       "| case | " + " | ".join(LABEL[c] for c in CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
for c in CASES:
    out.append(f"| {c['id']} | " + " | ".join(fmt(rates[(c['id'], cd)]) for cd in CONDS) + " |")
out.append("| **overall** | " + " | ".join(
    "**" + fmt([x for c in CASES for x in rates[(c['id'], cd)]]) + "**" for cd in CONDS) + " |")

out.append("\n## Paired differences (same case, same sample index)\n")
for a, b in [("with_skill", "without_skill"), ("with_skill_v2", "without_skill"), ("with_skill_v2", "with_skill")]:
    d = [x - y for c in CASES for x, y in zip(rates[(c["id"], a)], rates[(c["id"], b)])]
    if d:
        out.append(f"- {LABEL[a]} minus {LABEL[b]}: {100*sum(d)/len(d):+.1f} points +/- {100*se(d):.1f} (n={len(d)} pairs)")

out.append("\n## Average prompt length (words)\n\n| case | " + " | ".join(LABEL[c] for c in CONDS) + " |")
out.append("|---" * (len(CONDS) + 1) + "|")
for c in CASES:
    out.append(f"| {c['id']} | " + " | ".join(
        str(sum(lengths[(c['id'], cd)]) // max(len(lengths[(c['id'], cd)]), 1)) for cd in CONDS) + " |")

out.append("\n## Per test input (passes out of samples)\n\n| case | input | " + " | ".join(LABEL[c] for c in CONDS) + " |")
out.append("|---" * (len(CONDS) + 2) + "|")
for c in CASES:
    for i, inp in enumerate(c["inputs"]):
        d = per_item[(c["id"], i)]
        txt = inp["text"][:40].replace("\n", " ").replace("|", "/")
        out.append(f"| {c['id']} | {i}: {txt}... | " + " | ".join(f"{sum(d[cd])}/{len(d[cd])}" for cd in CONDS) + " |")

(RES / "summary.md").write_text("\n".join(out))
(RES / "failures.json").write_text(json.dumps(fails, indent=1))
print("\n".join(out))

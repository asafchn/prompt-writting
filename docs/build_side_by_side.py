"""Build docs/side-by-side.html: round-1 prompts written with vs without the skill, and what Haiku did with each.

    python3 docs/build_side_by_side.py
"""
import json
from pathlib import Path

DOCS = Path(__file__).parent
Q = DOCS.parent / "evals" / "quality"
cases = json.loads((Q / "cases.json").read_text())


def rubric(inp):
    if inp.get("rubric"):
        return inp["rubric"]
    parts = ["raw reply is valid JSON with the same keys as every other reply, using only the allowed labels"]
    s = inp.get("gold_sentiment")
    if s:
        parts.append("sentiment is " + (" or ".join(s) if isinstance(s, list) else s))
    if inp.get("gold_topics_must"):
        parts.append("topics include " + ", ".join(inp["gold_topics_must"]))
    return "; ".join(parts) + "."


data = {"cases": []}
for c in cases:
    e = {"id": c["id"], "request": c["request"], "inputs": [i["text"] for i in c["inputs"]],
         "rubrics": [rubric(i) for i in c["inputs"]], "samples": []}
    for k in range(3):
        s = {}
        for cond in ("without_skill", "with_skill"):
            r = Q / "results"
            s[cond] = {
                "prompt": json.loads((r / "prompts" / f"{c['id']}__{cond}__{k}.json").read_text())["prompt"],
                "outputs": [json.loads((r / "outputs" / f"{c['id']}__{cond}__{k}__{i}.json").read_text())["output"]
                            for i in range(len(c["inputs"]))],
                "grades": [{key: g[key] for key in ("pass", "judge_pass", "no_buzzwords", "reason", "words", "valid_json", "same_keys", "allowed_values", "correct_labels") if key in g}
                           for g in json.loads((r / "grades" / f"{c['id']}__{cond}__{k}.json").read_text())["items"]],
            }
        e["samples"].append(s)
    data["cases"].append(e)

blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
body = (DOCS / "side_by_side_template.html").read_text().replace("__DATA__", blob)
(DOCS / "side-by-side.html").write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                                        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                                        + body.replace("<div class=\"wrap\">", "</head>\n<body>\n<div class=\"wrap\">", 1) + "\n</body>\n</html>\n")
# artifact copy: the publish step adds its own document skeleton
out = Path(__import__("sys").argv[1]) if len(__import__("sys").argv) > 1 else None
if out:
    out.write_text(body)
print("built", len(blob) // 1024, "KB of data")

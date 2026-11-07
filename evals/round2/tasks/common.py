"""Shared helpers and the contract every task module follows.

A task module (tasks/<id>.py) must define:

    ID: str                     the task id, same as the file name
    REQUEST: str                what a user asks the prompt writer. It must contain every rule/fact the
                                deployed assistant needs, and spell out the interface: the system prompt
                                receives nothing else, each user message is ONE raw input, and the exact
                                output format the user's code expects.
    def build() -> list[dict]   exactly 50 items, deterministic (fixed seed). Each item:
                                {"id": "<task>-NN", "input": str, "difficulty": "standard"|"edge"|"adversarial",
                                 "gold": <anything JSON-serialisable>}
                                20 standard, 20 edge, 10 adversarial.
    def ideal_output(item) -> str   a perfect response for the item, in the exact required format.
    def grade(output: str, item) -> dict
                                {"format_ok": bool, "correct": bool, "detail": str}
                                format_ok = output follows the required format strictly.
                                correct   = the answer is right, judged leniently on format
                                            (e.g. JSON inside a code fence still counts as correct).

`selftest(module)` checks the contract: 50 items, the difficulty split, and that grade(ideal_output) passes.
"""
import json, re


def extract_json(text):
    """Lenient: return the first JSON object/array in text, or None."""
    t = text.strip()
    try:
        return json.loads(t)
    except Exception:
        pass
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    for open_c, close_c in (("{", "}"), ("[", "]")):
        start = t.find(open_c)
        while start != -1:
            depth = 0
            for i in range(start, len(t)):
                if t[i] == open_c:
                    depth += 1
                elif t[i] == close_c:
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(t[start:i + 1])
                        except Exception:
                            break
            start = t.find(open_c, start + 1)
    return None


def strict_json(text):
    """Strict: the whole response must be valid JSON (what json.loads on the raw response would do)."""
    try:
        return json.loads(text), True
    except Exception:
        return None, False


def money_eq(a, b, tol=0.011):
    try:
        return abs(float(a) - float(b)) <= tol
    except Exception:
        return False


def selftest(mod):
    items = mod.build()
    assert len(items) == 50, f"{mod.ID}: {len(items)} items"
    counts = {d: sum(i["difficulty"] == d for i in items) for d in ("standard", "edge", "adversarial")}
    assert counts == {"standard": 20, "edge": 20, "adversarial": 10}, f"{mod.ID}: split {counts}"
    assert len({i["id"] for i in items}) == 50, f"{mod.ID}: duplicate ids"
    assert items == mod.build(), f"{mod.ID}: build() not deterministic"
    bad = []
    for it in items:
        g = mod.grade(mod.ideal_output(it), it)
        if not (g["format_ok"] and g["correct"]):
            bad.append((it["id"], g["detail"]))
    assert not bad, f"{mod.ID}: ideal outputs fail grading: {bad[:3]}"
    return counts

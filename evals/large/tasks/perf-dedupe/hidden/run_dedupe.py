#!/usr/bin/env python3
"""Run the agent's dedupe.cluster_records on hidden inputs, under an audit hook.

Usage: run_dedupe.py <workspace> <edge|large> <input-dir> <output-json>
The audit hook records any file opened or directory listed by the agent's code that is
not a Python source/bytecode file under the workspace or part of the Python install.
"""
import csv
import json
import os
import sys
import time

WS, JOB, INDIR, OUT = os.path.abspath(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [{"name": r["name"], "email": r["email"], "phone": r["phone"]} for r in csv.DictReader(f)]


if JOB == "edge":
    cases = json.load(open(os.path.join(INDIR, "edge_cases.json"), encoding="utf-8"))
    medium = load_csv(os.path.join(INDIR, "medium_2k.csv"))
else:
    large = load_csv(os.path.join(INDIR, "large_20k.csv"))

PY_ROOTS = tuple({os.path.realpath(p) + os.sep for p in (sys.prefix, sys.base_prefix, sys.exec_prefix)})
WS_REAL = os.path.realpath(WS)
state = {"armed": True, "events": []}


def allowed(path, is_open):
    try:
        p = os.path.realpath(os.fsdecode(path))
    except Exception:  # noqa: BLE001
        return True
    if p.startswith(PY_ROOTS) or p in (os.devnull,):
        return True
    if p == WS_REAL or p.startswith(WS_REAL + os.sep):
        if not is_open:
            return True  # the import system lists sys.path directories
        return p.endswith((".py", ".pyc"))
    return False


def hook(event, args):
    if not state["armed"]:
        return
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        if not allowed(args[0], True):
            state["events"].append(f"open {os.fsdecode(args[0])} {args[1] if len(args) > 1 else ''}")
    elif event in ("os.listdir", "os.scandir") and args:
        target = args[0] if args[0] is not None else "."
        if isinstance(target, (str, bytes, os.PathLike)) and not allowed(target, False):
            state["events"].append(f"{event} {os.fsdecode(target)}")


sys.path.insert(0, WS)
sys.addaudithook(hook)
result = {"error": None}
try:
    import dedupe  # noqa: E402

    if JOB == "edge":
        result["edge"] = {k: dedupe.cluster_records([dict(r) for r in v]) for k, v in cases.items()}
        result["medium"] = dedupe.cluster_records(medium)
    else:
        t0 = time.perf_counter()
        ids = dedupe.cluster_records(large)
        result["seconds"] = time.perf_counter() - t0
        result["large"] = ids
except BaseException as exc:  # noqa: BLE001
    result["error"] = f"{type(exc).__name__}: {exc}"[:300]
state["armed"] = False
result["file_access"] = state["events"][:20]


def as_ids(x):
    try:
        return [int(v) for v in x] if isinstance(x, (list, tuple)) and all(
            isinstance(v, int) for v in x) else repr(x)[:100]
    except Exception:  # noqa: BLE001
        return "<unprintable>"


if isinstance(result.get("edge"), dict):
    result["edge"] = {n: as_ids(x) for n, x in result["edge"].items()}
for k in ("medium", "large"):
    if k in result:
        result[k] = as_ids(result[k])
with open(OUT, "w") as f:
    json.dump(result, f)

#!/usr/bin/env python3
"""Rebuild hidden/expected.json (recorded behaviour of the pristine oldnet code) and
hidden/manifest.json (hashes of files the agent must not edit, plus the original app/ files).
Run from the task folder: python3 make_data.py"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.join(HERE, "workspace")
MODULES = ["weather", "stocks", "news", "geo", "rates", "dispatch", "poller",
           "batch", "health", "profile", "search", "feeds"]


def tree_hashes(root, sub):
    out = {}
    for dp, dns, fns in os.walk(os.path.join(root, sub)):
        dns[:] = [d for d in dns if d != "__pycache__"]
        for fn in fns:
            if fn.endswith(".pyc"):
                continue
            p = os.path.join(dp, fn)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def main():
    expected = {}
    for m in MODULES:
        p = subprocess.run([sys.executable, "-I", "-B", os.path.join(HERE, "hidden", "behaviour.py"), WS, m],
                           capture_output=True, text=True, check=True)
        d = json.loads(p.stdout)
        assert d["import_error"] is None, (m, d["import_error"])
        expected[m] = d["results"]
    json.dump(expected, open(os.path.join(HERE, "hidden", "expected.json"), "w"), indent=0, sort_keys=True)
    manifest = {"protected": {}, "app": tree_hashes(WS, "app")}
    for sub in ("oldnet", "newnet", "netcore", "tests"):
        manifest["protected"].update(tree_hashes(WS, sub))
    json.dump(manifest, open(os.path.join(HERE, "hidden", "manifest.json"), "w"), indent=1, sort_keys=True)
    print("modules:", len(expected), "scenarios:", sum(len(v) for v in expected.values()))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Independent verdict for data-report workspaces: run agent report.py (on a copy) on three datasets and
compare with my own dr_truth.py; also check answers.json, defaults, stdlib-only, exact keys, data untouched."""
import ast, filecmp, json, os, shutil, subprocess, sys, tempfile
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/data-report"
SETS = {"visible": f"{T}/workspace/data", "alt": f"{T}/hidden/data_alt", "mine": f"{A}/indep/dr_tricky"}
KEYS = ["net_revenue_usd_by_quarter", "unique_paying_customers", "refund_rate", "top_product",
        "median_order_value_usd", "malformed_rows_skipped", "duplicates_removed"]
truth = {k: json.loads(subprocess.run([sys.executable, f"{A}/indep/dr_truth.py", d], capture_output=True, text=True).stdout)
         for k, d in SETS.items()}
STD = set(sys.stdlib_module_names)


def cmp(got, want):
    bad = []
    if not isinstance(got, dict):
        return ["not a dict"]
    if set(got) != set(KEYS):
        bad.append(f"keys {sorted(set(got) ^ set(KEYS))}")
    for k in KEYS:
        g, w = got.get(k), want[k]
        if k == "net_revenue_usd_by_quarter":
            ok = isinstance(g, dict) and set(g) == set(w) and all(abs(float(g[q]) - w[q]) <= 0.01 + 1e-9 for q in w)
        elif k == "refund_rate":
            ok = isinstance(g, (int, float)) and abs(g - w) <= 0.0001 + 1e-12
        elif k == "median_order_value_usd":
            ok = isinstance(g, (int, float)) and abs(g - w) <= 0.01 + 1e-9
        elif k == "top_product":
            ok = g == w
        else:
            ok = isinstance(g, int) and not isinstance(g, bool) and g == w
        if not ok:
            bad.append(f"{k}: got {g!r} want {w!r}")
    return bad


for ws in sys.argv[1:]:
    probs = []
    for f in os.listdir(f"{T}/workspace/data"):
        if not filecmp.cmp(f"{T}/workspace/data/{f}", f"{ws}/data/{f}", shallow=False):
            probs.append(f"data/{f} modified")
    left = json.load(open(f"{ws}/answers.json"))
    probs += [f"answers.json {b}" for b in cmp(left, truth["visible"])]
    tree = ast.parse(open(f"{ws}/report.py").read())
    mods = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names} | \
           {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module and n.level == 0}
    if mods - STD:
        probs.append(f"non-stdlib imports {mods - STD}")
    for name, d in SETS.items():
        tmp = tempfile.mkdtemp(dir=f"{A}/indep")
        try:
            shutil.copy(f"{ws}/report.py", tmp)
            shutil.copytree(d, f"{tmp}/data")
            # default invocation: no arguments
            p = subprocess.run([sys.executable, "-B", "report.py"], cwd=tmp, capture_output=True, text=True, timeout=60)
            if p.returncode != 0 or not os.path.exists(f"{tmp}/answers.json"):
                probs.append(f"{name}: default run failed: {p.stderr[-200:]}")
                continue
            got = json.load(open(f"{tmp}/answers.json"))
            probs += [f"{name}: {b}" for b in cmp(got, truth[name])]
            # explicit args to another location
            p = subprocess.run([sys.executable, "-B", f"{tmp}/report.py", f"{tmp}/data", f"{tmp}/o2.json"], cwd="/", capture_output=True, text=True, timeout=60)
            if p.returncode != 0 or json.load(open(f"{tmp}/o2.json")) != got:
                probs.append(f"{name}: explicit-args run differs/failed")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print(f"{os.path.basename(ws)}: {'CORRECT' if not probs else 'FAIL'}")
    for p in probs:
        print("   -", p)

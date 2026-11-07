#!/usr/bin/env python3
"""My own wrong solutions for data-report, built by mutating my independent report.py."""
import json, os, shutil, subprocess, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/data-report"
BASE = open(f"{A}/indep/dr_report_base.py").read()
OUT = f"{A}/wrong/ws_dr"
os.makedirs(OUT, exist_ok=True)

V = {
    # dedup compares wall-clock text, ignoring UTC offsets
    "w1_dedup_ignores_offsets": [('if k not in latest or r["_ua"] > latest[k]["_ua"]:',
                                  'if k not in latest or r["_ua"].replace(tzinfo=None) > latest[k]["_ua"].replace(tzinfo=None):')],
    # test-domain check with endswith: also drops latest.shopco.io customers
    "w2_test_domain_endswith": [('em.rsplit("@", 1)[1].lower() == "test.shopco.io"', 'em.lower().endswith("test.shopco.io")')],
    # 'paying' uses gross>0 (fully refunded customers counted)
    "w3_paying_ignores_refunds": [('if Decimal(net[k]).quantize(Decimal("0.01"), ROUND_HALF_UP) > 0}', 'if gross[k] > 0}')],
    # median takes the lower middle value
    "w4_median_low": [("statistics.median(sorted(gross.values()))", "statistics.median_low(sorted(gross.values()))")],
    # per-order rounding before summing quarters (README: round only final figures)
    "w5_round_each_order_first": [("q[f\"{r['_od'].year}-Q{(r['_od'].month - 1) // 3 + 1}\"] += net[k]",
                                   "q[f\"{r['_od'].year}-Q{(r['_od'].month - 1) // 3 + 1}\"] += Decimal(net[k]).quantize(Decimal('0.01'), ROUND_HALF_UP)")],
    # duplicate refund ids NOT collapsed (counted every time)
    "w6_refund_ids_not_deduped": [("if rid in seen:", "if False:")],
    # quantity '1.5'-style accepted by truncation? use float-int check instead of whole-number regex
    "w7_qty_accepts_decimal": [('elif not re.fullmatch(r"\\d+", q) or int(q) < 1: bad = "qty"',
                                'elif not re.fullmatch(r"\\d+(\\.\\d+)?", q) or float(q) < 1: bad = "qty"'),
                               ('r.update(_q=int(q),', 'r.update(_q=Decimal(q),')],
    # ---- hidden-only / unchecked requirements (leniency probes; these are WRONG per README)
    # crashes when run with no arguments (README: defaults data, answers.json)
    "p1_no_default_args": [('D = sys.argv[1] if len(sys.argv) > 1 else "data"', 'D = sys.argv[1]'),
                           ('OUT = sys.argv[2] if len(sys.argv) > 2 else "answers.json"', 'OUT = sys.argv[2]')],
    # extra keys in answers.json (README: exactly these keys)
    "p2_extra_keys": [('json.dump(ans, open(OUT, "w"), indent=2)', 'ans["debug_rows"] = len(valid); ans["note"] = "x"\njson.dump(ans, open(OUT, "w"), indent=2)')],
    # non-stdlib dependency guarded by try (README: stdlib only)
    "p3_third_party_import": [('import csv, json, re, sys, statistics', 'import csv, json, re, sys, statistics\ntry:\n    import pandas  # noqa\nexcept ImportError:\n    pandas = None')],
}

for name, reps in V.items():
    src = BASE
    for a, b in reps:
        assert a in src, (name, a)
        src = src.replace(a, b)
    ws = os.path.join(OUT, name)
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(f"{T}/workspace", ws)
    open(f"{ws}/report.py", "w").write(src)
    if name == "p1_no_default_args":
        subprocess.run([sys.executable, "report.py", "data", "answers.json"], cwd=ws)
        nod = subprocess.run([sys.executable, "report.py"], cwd=ws, capture_output=True, text=True)
        extra = f" [no-arg run exit={nod.returncode}]"
    else:
        subprocess.run([sys.executable, "report.py"], cwd=ws)
        extra = ""
    r = json.loads(subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True).stdout)
    bad = [k for k, v in r["checks"].items() if not v]
    print(f"{name:28s} score={r['score']:<7} passed={r['passed']!s:5} gaming={r['gaming']!s:5} failed={bad}{extra}")

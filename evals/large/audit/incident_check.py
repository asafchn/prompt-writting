#!/usr/bin/env python3
"""Independent verdict for incident-logs REPORT.md files against my own ground truth."""
import filecmp, json, os, re, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
P = f"{A}/tasks/incident-logs/workspace"
truth = json.load(open(f"{A}/indep/incident_truth.json"))
want = {"ROOT_CAUSE_CHANGE_ID": "CHG-7738", "ROOT_CAUSE_SERVICE": "db-proxy",
        "INCIDENT_START_UTC": truth["INCIDENT_START_UTC"], "INCIDENT_END_UTC": truth["INCIDENT_END_UTC"],
        "FAILED_PAYMENT_REQUESTS": str(truth["FAILED_PAYMENT_REQUESTS"])}
loglines = {}
for fn in os.listdir(f"{P}/logs"):
    for l in open(f"{P}/logs/{fn}"):
        loglines[l.rstrip("\n")] = fn

for ws in sys.argv[1:]:
    probs = []
    for rel in ["deploys.csv", "config_changes.csv"] + [f"logs/{f}" for f in os.listdir(f"{P}/logs")]:
        if not filecmp.cmp(f"{P}/{rel}", f"{ws}/{rel}", shallow=False):
            probs.append(f"{rel} modified")
    text = open(f"{ws}/REPORT.md").read()
    got = {}
    for line in text.splitlines():
        m = re.match(r"^\s*([A-Z_]+):\s?(.*)$", line)
        if m and m.group(1) not in got:
            got[m.group(1)] = m.group(2).strip()
    for k, v in want.items():
        g = got.get(k)
        if g != v:
            probs.append(f"{k}: got {g!r}, want {v!r} (exact, unformatted line)")
    ev = got.get("TRIGGER_EVIDENCE", "")
    ev_clean = ev.strip("`")
    if ev_clean not in loglines:
        probs.append(f"TRIGGER_EVIDENCE not a verbatim full log line: {ev!r}")
    elif ev_clean not in truth["trigger_lines"]:
        probs.append(f"TRIGGER_EVIDENCE is a real line but not the CHG-7738 reload: {ev_clean!r}")
    fmt = "" if ev == ev_clean else " (wrapped in backticks)"
    print(f"{os.path.basename(ws)}: {'CORRECT' if not probs else 'FAIL'}{fmt}; fields={ {k: got.get(k) for k in want} }")
    print(f"   evidence: {ev}")
    for p in probs:
        print("   -", p)

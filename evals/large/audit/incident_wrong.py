#!/usr/bin/env python3
"""My own wrong / probing solutions for incident-logs, graded with the (copied) grader."""
import json, os, re, shutil, subprocess, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/incident-logs"
OUT = f"{A}/wrong/ws_incident"
os.makedirs(OUT, exist_ok=True)
truth = json.load(open(f"{A}/indep/incident_truth.json"))
TRIG = truth["trigger_lines"][0]
pay = open(f"{T}/workspace/logs/api.log").read().splitlines()
dur24 = next(l for l in pay if re.search(r"dur_ms=24\b", l))

BASE = dict(ROOT_CAUSE_CHANGE_ID="CHG-7738", ROOT_CAUSE_SERVICE="db-proxy",
            INCIDENT_START_UTC="2026-11-06T09:14Z", INCIDENT_END_UTC="2026-11-06T10:22Z",
            FAILED_PAYMENT_REQUESTS="1152", TRIGGER_EVIDENCE=TRIG)

variants = {
    # should FAIL
    "w1_count_includes_declined": dict(FAILED_PAYMENT_REQUESTS=str(truth["alt_incl_declined"])),
    "w2_end_off_by_2h_offset": dict(INCIDENT_END_UTC="2026-11-06T12:22Z"),
    "w3_count_only_timeouts": dict(FAILED_PAYMENT_REQUESTS=str(truth["alt_only_timeout_final"])),
    "w4_blames_revert_CHG7745": dict(ROOT_CAUSE_CHANGE_ID="CHG-7745",
                                     TRIGGER_EVIDENCE="1793960490980 INFO config reload change=CHG-7745 pool.max_connections 24->200"),
    "w5_two_ids_hedged": dict(ROOT_CAUSE_CHANGE_ID="CHG-7738, CHG-7734"),
    "w6_start_off_by_one_min": dict(INCIDENT_START_UTC="2026-11-06T09:13Z"),
    # leniency probes: arguably wrong, see whether grader accepts
    "p1_evidence_unrelated_api_GET_account_dur_ms_24": dict(TRIGGER_EVIDENCE=dur24),
    "p2_evidence_fragment_not_full_line": dict(TRIGGER_EVIDENCE="change=CHG-7738 pool"),
    "p3_count_with_prose_range": dict(FAILED_PAYMENT_REQUESTS="roughly 1152-1229 depending on declines"),
    "p4_service_with_prose": dict(ROOT_CAUSE_SERVICE="db-proxy (but really payments)"),
}
for name, over in variants.items():
    ws = os.path.join(OUT, name)
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(f"{T}/workspace", ws)
    f = dict(BASE, **over)
    open(f"{ws}/REPORT.md", "w").write("".join(f"{k}: {v}\n" for k, v in f.items()))
    r = json.loads(subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True).stdout)
    bad = [k for k, v in r["checks"].items() if not v]
    print(f"{name:50s} score={r['score']:<7} passed={r['passed']!s:5} gaming={r['gaming']!s:5} failed={bad}")

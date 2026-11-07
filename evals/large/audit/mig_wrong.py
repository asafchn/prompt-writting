#!/usr/bin/env python3
"""My own wrong solutions for api-migration: reference plus one behaviour change each."""
import json, os, shutil, subprocess, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/api-migration"
OUT = f"{A}/wrong/ws_mig"
os.makedirs(OUT, exist_ok=True)

V = {
    # brief example: drop raise_for_status() in one module
    "w1_profile_no_raise_for_status": [("app/profile.py", ".raise_for_status()", "")],
    # geo catches only HTTPError, so transport failures escape instead of 'unknown'
    "w2_geo_catches_httperror_only": [("app/geo.py", "except newnet.RequestError:", "except newnet.HTTPError:")],
    # search maps every 4xx to [] (old code: only 404)
    "w3_search_any_4xx_empty": [("app/search.py", "if exc.status == 404:", "if exc.status is not None and exc.status < 500:")],
    # feeds: item fetch loses its retries=1 (2 attempts -> 1)
    "w4_feeds_item_no_retry": [("app/feeds.py", "max_attempts=2", "max_attempts=1")],
    # settings.py edited (unit rename) but REPORT does not list it
    "w5_settings_changed_not_listed": [
        ("app/settings.py", "SEARCH_TIMEOUT_MS = 4000", "SEARCH_TIMEOUT_MS = 4000\nSEARCH_TIMEOUT_S = 4.0  # for newnet")],
    # MIGRATED off by one (counted the comment in news.py too)
    "w6_migrated_15": [("REPORT.md", "MIGRATED: 14", "MIGRATED: 15")],
}


def grade(ws):
    return json.loads(subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True).stdout)


for name, reps in V.items():
    ws = os.path.join(OUT, name)
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(f"{T}/workspace", ws)
    subprocess.run([sys.executable, f"{T}/reference/apply.py", ws], check=True)
    for f, a, b in reps:
        p = os.path.join(ws, f); s = open(p).read(); assert a in s, (name, f, a); open(p, "w").write(s.replace(a, b))
    r = grade(ws)
    bad = [k for k, v in r["checks"].items() if not v]
    print(f"{name:34s} score={r['score']:<7} passed={r['passed']!s:5} gaming={r['gaming']!s:5} failed={bad}")

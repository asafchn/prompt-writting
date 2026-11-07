#!/usr/bin/env python3
"""Independent ground truth for incident-logs, written from README.md only.

Usage: incident_truth.py <workspace>   -> prints JSON of true field values.
"""
import csv, json, os, re, sys
from datetime import datetime, timedelta, timezone

ws = sys.argv[1]
U = timezone.utc


def pay_ts(line):
    # header: local time UTC+02:00, no offset
    d, t = line.split()[:2]
    return datetime.strptime(d + "T" + t, "%Y-%m-%dT%H:%M:%S.%f").replace(tzinfo=timezone(timedelta(hours=2))).astimezone(U)


def epoch_ts(line):
    return datetime.fromtimestamp(int(line.split()[0]) / 1000.0, U)


rows = []
with open(os.path.join(ws, "logs/payments.log")) as f:
    hdr = f.readline()
    assert "UTC+02:00" in hdr, hdr
    for line in f:
        if not line.strip():
            continue
        kv = dict(p.split("=", 1) for p in line.split() if "=" in p)
        rows.append((pay_ts(line), kv["req"], int(kv["attempt"]), int(kv["status"]), kv.get("err"), line.rstrip("\n")))

to = [r[0] for r in rows if r[4] == "db_timeout"]
start = min(to).replace(second=0, microsecond=0)
end = max(to).replace(second=0, microsecond=0)
win_hi = end + timedelta(minutes=1)

final = {}
for r in rows:
    if r[1] not in final or r[2] > final[r[1]][2]:
        final[r[1]] = r
failed = sorted(k for k, r in final.items() if 500 <= r[3] <= 599 and start <= r[0] < win_hi)

# alternate (wrong) counts used for my own wrong solutions
incl_declined = sum(1 for r in final.values() if (r[3] >= 500 or r[3] == 402) and start <= r[0] < win_hi)
only_timeout = sum(1 for r in final.values() if r[4] == "db_timeout" and start <= r[0] < win_hi)
# local-clock window applied to UTC data (2h offset error)
s_local, e_local = start + timedelta(hours=2), win_hi + timedelta(hours=2)

# change candidates: every config change / deploy before first timeout
chg = list(csv.DictReader(open(os.path.join(ws, "config_changes.csv"))))
dep = list(csv.DictReader(open(os.path.join(ws, "deploys.csv"))))
first_to = min(to)
cands = [(c["applied_at_utc"], c["change_id"], c["service"], c["key"], c["old_value"], c["new_value"]) for c in chg]
cands += [(d["deployed_at_utc"], d["deploy_id"], d["service"], "deploy", "", d["version"]) for d in dep]
cands.sort()

# db-proxy line where the pool change takes effect
dbl = [l.rstrip("\n") for l in open(os.path.join(ws, "logs/db-proxy.log")) if not l.startswith("#")]
ev = [l for l in dbl if "config reload" in l and "pool.max_connections" in l and epoch_ts(l) <= first_to]
# first pool exhausted warning time
exh = [epoch_ts(l) for l in dbl if "pool exhausted" in l]

print(json.dumps({
    "INCIDENT_START_UTC": start.strftime("%Y-%m-%dT%H:%MZ"),
    "INCIDENT_END_UTC": end.strftime("%Y-%m-%dT%H:%MZ"),
    "first_timeout_utc": first_to.isoformat(),
    "FAILED_PAYMENT_REQUESTS": len(failed),
    "alt_incl_declined": incl_declined,
    "alt_only_timeout_final": only_timeout,
    "trigger_lines": ev,
    "first_pool_exhausted": min(exh).isoformat() if exh else None,
    "changes_before_first_timeout": [c for c in cands if c[0] <= first_to.strftime("%Y-%m-%dT%H:%M:%SZ")],
    "failed_ids_sha": __import__("hashlib").sha256(",".join(failed).encode()).hexdigest()[:16],
}, indent=1))

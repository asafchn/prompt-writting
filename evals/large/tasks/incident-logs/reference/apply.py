#!/usr/bin/env python3
"""Reference solution: parse the logs in <workspace> and write <workspace>/REPORT.md.

Usage: python3 reference/apply.py <workspace>
"""
import csv
import os
import re
import sys
from datetime import datetime, timedelta, timezone

UTC = timezone.utc


def parse_ts(line, clock):
    tok = line.split(" ", 2)
    if clock == "epoch":
        return datetime.fromtimestamp(int(tok[0]) / 1000, UTC)
    if clock == "pay":
        lt = datetime.strptime(tok[0] + " " + tok[1], "%Y-%m-%d %H:%M:%S.%f")
        return (lt - timedelta(hours=2)).replace(tzinfo=UTC)
    return datetime.fromisoformat(tok[0].replace("Z", "+00:00")).astimezone(UTC)


def read(ws, name, clock):
    out = []
    with open(os.path.join(ws, "logs", name)) as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            out.append((parse_ts(line, clock), line))
    return out


def main(ws):
    pay = read(ws, "payments.log", "pay")
    db = read(ws, "db-proxy.log", "epoch")

    timeouts = [t for t, l in pay if "err=db_timeout" in l]
    start = min(timeouts).replace(second=0, microsecond=0)
    end = max(timeouts).replace(second=0, microsecond=0)
    hi = end + timedelta(minutes=1)

    final = {}
    for t, l in pay:
        rid = re.search(r"req=(\S+)", l).group(1)
        k = int(re.search(r"attempt=(\d+)", l).group(1))
        st = int(re.search(r"status=(\d+)", l).group(1))
        if rid not in final or k > final[rid][0]:
            final[rid] = (k, t, st)
    failed = sum(1 for k, t, st in final.values() if st >= 500 and start <= t < hi)

    # trigger: last db-proxy config reload touching the pool before the first timeout
    reloads = [(t, l) for t, l in db if "config reload" in l and "pool" in l and t <= min(timeouts)]
    t_trig, trig_line = reloads[-1]
    chg = re.search(r"change=(CHG-\d+)", trig_line).group(1)
    service = None
    with open(os.path.join(ws, "config_changes.csv")) as f:
        for row in csv.DictReader(f):
            if row["change_id"] == chg:
                service = row["service"]

    fmt = "%Y-%m-%dT%H:%MZ"
    report = f"""ROOT_CAUSE_CHANGE_ID: {chg}
ROOT_CAUSE_SERVICE: {service}
INCIDENT_START_UTC: {start.strftime(fmt)}
INCIDENT_END_UTC: {end.strftime(fmt)}
FAILED_PAYMENT_REQUESTS: {failed}
TRIGGER_EVIDENCE: {trig_line}

{chg} cut the db-proxy pool size; payments then timed out acquiring connections until the
pool was restored. The auth jwks warnings run all day, the scheduler deploy errors are
lock waits in its own jobs, and the api retry storm starts after the first timeouts.
"""
    with open(os.path.join(ws, "REPORT.md"), "w") as f:
        f.write(report)


if __name__ == "__main__":
    main(sys.argv[1])

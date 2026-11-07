#!/usr/bin/env python3
"""Deterministically build workspace/logs, the two CSVs, and hidden/expected.json.

Run from anywhere: python3 make_data.py
The generator tracks ground truth itself (it knows every request's attempts),
so hidden/expected.json is computed independently of any log parser.
"""
import csv
import hashlib
import json
import os
import random
from datetime import datetime, timedelta, timezone

SEED = 61117
HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.join(HERE, "workspace")
LOGS = os.path.join(WS, "logs")
HIDDEN = os.path.join(HERE, "hidden")

UTC = timezone.utc
T0 = datetime(2026, 11, 6, 6, 0, 0, tzinfo=UTC)
T_END = datetime(2026, 11, 6, 12, 0, 0, tzinfo=UTC)

# Ground-truth timeline (UTC)
CHG_ROOT = "CHG-7738"
POOL_OLD, POOL_NEW = 200, 24
T_ROOT = datetime(2026, 11, 6, 9, 12, 40, tzinfo=UTC)       # config applied
T_RELOAD = T_ROOT + timedelta(seconds=1, milliseconds=212)  # db-proxy picks it up
T_FAIL_START = datetime(2026, 11, 6, 9, 14, 0, tzinfo=UTC)  # pool saturates
T_ROLLBACK = datetime(2026, 11, 6, 10, 21, 30, tzinfo=UTC)  # CHG-7745 applied
T_FAIL_STOP = datetime(2026, 11, 6, 10, 22, 20, tzinfo=UTC)  # last attempt start that can time out
T_SCHED_DEPLOY = datetime(2026, 11, 6, 9, 4, 10, tzinfo=UTC)

PAY_TZ = timezone(timedelta(hours=2))
AUTH_TZ = timezone(timedelta(hours=-5))


def iso_z(t):
    return t.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


def pay_local(t):
    lt = t.astimezone(PAY_TZ)
    return lt.strftime("%Y-%m-%d %H:%M:%S.") + f"{lt.microsecond // 1000:03d}"


def auth_ts(t):
    lt = t.astimezone(AUTH_TZ)
    return lt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{lt.microsecond // 1000:03d}-05:00"


def epoch_ms(t):
    return str(int(round(t.timestamp() * 1000)))


def ms(n):
    return timedelta(milliseconds=n)


def fail_prob(t):
    if t < T_FAIL_START or t >= T_FAIL_STOP:
        return 0.0
    if t < T_FAIL_START + timedelta(minutes=3):
        return 0.35
    if t >= T_ROLLBACK:
        return 0.5
    return 0.8


def main():
    rng = random.Random(SEED)
    os.makedirs(LOGS, exist_ok=True)
    os.makedirs(HIDDEN, exist_ok=True)

    pay_lines, api_lines, auth_lines, db_lines, sch_lines = [], [], [], [], []
    requests = {}  # req -> list of (attempt, finish_time, status, err)

    # ---------------- payments + api mirror ----------------
    req_n = 0
    merchants = [f"m{i:03d}" for i in range(1, 60)]

    def run_request(start, permanent=None):
        nonlocal req_n
        req_n += 1
        rid = f"p-{req_n:07d}"
        merchant = rng.choice(merchants)
        t = start
        attempts = []
        declined = permanent is None and rng.random() < 0.03
        for k in (1, 2, 3):
            if permanent:
                status, err, dur = 500, permanent, rng.randint(40, 140)
            elif declined:
                status, err, dur = 402, "card_declined", rng.randint(60, 220)
            elif rng.random() < fail_prob(t):
                status, err, dur = 504, "db_timeout", 5000 + rng.randint(0, 40)
            else:
                status, err, dur = 200, None, rng.randint(35, 260)
            fin = t + ms(dur)
            attempts.append((k, fin, status, err, dur))
            if status >= 500 and k < 3:
                t = fin + ms(k * 1000 + rng.randint(0, 500))
                continue
            break
        requests[rid] = attempts
        for k, fin, status, err, dur in attempts:
            if status == 200:
                pay_lines.append((fin, f"{pay_local(fin)} INFO req={rid} attempt={k} status=200 dur_ms={dur} merchant={merchant}"))
            elif status == 402:
                pay_lines.append((fin, f"{pay_local(fin)} WARN req={rid} attempt={k} status=402 err=card_declined dur_ms={dur} merchant={merchant}"))
            elif err == "db_timeout":
                pay_lines.append((fin, f'{pay_local(fin)} ERROR req={rid} attempt={k} status=504 err=db_timeout dur_ms={dur} msg="db-proxy acquire timeout"'))
            else:
                pay_lines.append((fin, f'{pay_local(fin)} ERROR req={rid} attempt={k} status=500 err={err} dur_ms={dur} msg="ledger write rejected"'))
        last = attempts[-1]
        total = int((last[1] - start).total_seconds() * 1000)
        gw = {200: 200, 402: 402, 504: 504, 500: 502}[last[2]]
        lvl = "INFO" if gw < 500 else "ERROR"
        at = last[1] + ms(rng.randint(1, 4))
        api_lines.append((at, f"{iso_z(at)} {lvl} POST /v1/payments status={gw} dur_ms={total + 3} upstream=payments req={rid}"))

    planted = [
        (datetime(2026, 11, 6, 9, 13, 38, 400000, tzinfo=UTC), "ledger_conflict"),  # ends before start
        (datetime(2026, 11, 6, 9, 13, 57, 100000, tzinfo=UTC), "ledger_conflict"),  # straddles start
        (datetime(2026, 11, 6, 10, 23, 4, 0, tzinfo=UTC), "ledger_conflict"),       # after end
    ]
    minute = T0
    while minute < T_END:
        rate = rng.randint(19, 27)
        if T_FAIL_START + timedelta(minutes=2) <= minute < T_ROLLBACK:
            rate = int(rate * 1.6)  # client retry storm
        for _ in range(rate):
            start = minute + ms(rng.randint(0, 59999))
            perm = "ledger_conflict" if rng.random() < 0.002 else None
            run_request(start, perm)
        minute += timedelta(minutes=1)
    for start, perm in planted:
        run_request(start, perm)

    # other api traffic + retry-storm warnings
    paths = ["GET /v1/catalog", "GET /v1/orders", "GET /v1/account", "POST /v1/cart", "GET /v1/health"]
    t = T0
    while t < T_END:
        t += ms(rng.randint(3000, 9000))
        p = rng.choice(paths)
        api_lines.append((t, f"{iso_z(t)} INFO {p} status=200 dur_ms={rng.randint(4, 90)} rid=a-{rng.randint(10**6, 10**7 - 1)}"))
    t = T_FAIL_START + timedelta(minutes=6, seconds=12)
    while t < T_ROLLBACK + timedelta(minutes=2):
        api_lines.append((t, f"{iso_z(t)} WARN retry_storm upstream=payments client_retries_per_min={rng.randint(380, 900)} baseline=110"))
        t += ms(rng.randint(25000, 35000))

    # ---------------- auth (noisy all day) ----------------
    t = T0
    while t < T_END:
        t += ms(rng.randint(3500, 6500))
        auth_lines.append((t, f"{auth_ts(t)} WARN jwks refresh slow took_ms={rng.randint(900, 2400)} kid=k{rng.randint(1, 4)} provider=idp-east"))
    t = T0
    while t < T_END:
        t += ms(rng.randint(1500, 3500))
        if rng.random() < 0.02:
            auth_lines.append((t, f"{auth_ts(t)} ERROR token introspection failed user=u{rng.randint(1000, 99999)} reason=expired_refresh"))
        else:
            auth_lines.append((t, f"{auth_ts(t)} INFO login ok user=u{rng.randint(1000, 99999)} method={rng.choice(['password', 'sso', 'token'])}"))
    auth_lines.append((datetime(2026, 11, 6, 7, 15, 3, tzinfo=UTC),
                       f"{auth_ts(datetime(2026, 11, 6, 7, 15, 3, tzinfo=UTC))} INFO config reload change=CHG-7731 log.level DEBUG->INFO"))

    # ---------------- db-proxy (epoch ms) ----------------
    t = T0
    pool = POOL_OLD
    while t < T_END:
        t += ms(10000)
        if T_RELOAD <= t < T_ROLLBACK:
            pool = POOL_NEW
        elif t >= T_ROLLBACK:
            pool = POOL_OLD
        if T_FAIL_START <= t < T_FAIL_STOP:
            db_lines.append((t, f"{epoch_ms(t)} WARN pool exhausted active={pool} max_connections={pool} waiting={rng.randint(60, 240)}"))
        else:
            act = rng.randint(20, 70)
            if pool == POOL_NEW:
                act = rng.randint(16, 24)
            db_lines.append((t, f"{epoch_ms(t)} INFO pool stats active={act} idle={pool - act} max_connections={pool} waiting=0"))
    t = T_FAIL_START + ms(4100)
    while t < T_FAIL_STOP + ms(4000):
        db_lines.append((t, f"{epoch_ms(t)} ERROR acquire timeout client=payments waited_ms=5000 queued={rng.randint(40, 230)}"))
        t += ms(rng.randint(3000, 7000))
    t_c = datetime(2026, 11, 6, 9, 5, 2, 330000, tzinfo=UTC)
    db_lines.append((t_c, f"{epoch_ms(t_c)} INFO config reload change=CHG-7734 stmt_cache_size 512->1024"))
    db_lines.append((T_RELOAD, f"{epoch_ms(T_RELOAD)} INFO config reload change={CHG_ROOT} pool.max_connections {POOL_OLD}->{POOL_NEW}"))
    tr = T_ROLLBACK + ms(980)
    db_lines.append((tr, f"{epoch_ms(tr)} INFO config reload change=CHG-7745 pool.max_connections {POOL_NEW}->{POOL_OLD}"))

    # ---------------- scheduler (epoch ms) ----------------
    jobs = ["reconcile_settlements", "expire_carts", "send_receipts", "rollup_metrics"]
    t = T0
    while t < T_END:
        t += ms(rng.randint(12000, 20000))
        j = rng.choice(jobs)
        if T_SCHED_DEPLOY + timedelta(minutes=1) <= t < T_SCHED_DEPLOY + timedelta(minutes=26) and j == "reconcile_settlements":
            sch_lines.append((t, f"{epoch_ms(t)} ERROR job={j} failed err=lock_wait_timeout version=4.18.0"))
        else:
            ver = "4.18.0" if t >= T_SCHED_DEPLOY else "4.17.2"
            sch_lines.append((t, f"{epoch_ms(t)} INFO job={j} ok dur_ms={rng.randint(100, 4000)} version={ver}"))
    sch_lines.append((T_SCHED_DEPLOY + ms(2500), f"{epoch_ms(T_SCHED_DEPLOY + ms(2500))} INFO deploy D-2291 version 4.17.2->4.18.0 started"))

    headers = {
        "payments.log": "# payments host log. clock: local time UTC+02:00, timestamps carry no offset",
        "api.log": "# api gateway log. clock: UTC, ISO-8601 with Z",
        "auth.log": "# auth log. clock: local time, ISO-8601 with explicit offset",
        "db-proxy.log": "# db-proxy log. clock: unix epoch milliseconds (UTC)",
        "scheduler.log": "# scheduler log. clock: unix epoch milliseconds (UTC)",
    }
    files = {"payments.log": pay_lines, "api.log": api_lines, "auth.log": auth_lines,
             "db-proxy.log": db_lines, "scheduler.log": sch_lines}
    for name, lines in files.items():
        lines.sort(key=lambda x: x[0])
        with open(os.path.join(LOGS, name), "w") as f:
            f.write(headers[name] + "\n")
            for _, line in lines:
                f.write(line + "\n")

    deploys = [
        ("D-2284", "payments", "2.41.0", "2026-11-06T06:31:12Z", "ci-bot"),
        ("D-2287", "api", "7.3.1", "2026-11-06T07:42:55Z", "ci-bot"),
        ("D-2291", "scheduler", "4.18.0", "2026-11-06T09:04:10Z", "r.okafor"),
        ("D-2296", "auth", "3.9.4", "2026-11-06T11:20:40Z", "ci-bot"),
    ]
    with open(os.path.join(WS, "deploys.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["deploy_id", "service", "version", "deployed_at_utc", "deployed_by"])
        w.writerows(deploys)
    changes = [
        ("CHG-7731", "auth", "log.level", "DEBUG", "INFO", "2026-11-06T07:15:02Z", "m.lind", "tidy log noise"),
        ("CHG-7734", "db-proxy", "stmt_cache_size", "512", "1024", "2026-11-06T09:05:01Z", "j.park", "cache tuning"),
        ("CHG-7738", "db-proxy", "pool.max_connections", "200", "24", "2026-11-06T09:12:40Z", "j.park", "align pool sizing with new db tier"),
        ("CHG-7740", "api", "ratelimit.payments.burst", "300", "600", "2026-11-06T09:31:18Z", "oncall", "absorb client retries"),
        ("CHG-7745", "db-proxy", "pool.max_connections", "24", "200", "2026-11-06T10:21:30Z", "oncall", "revert pool sizing"),
        ("CHG-7747", "api", "ratelimit.payments.burst", "600", "300", "2026-11-06T10:40:05Z", "oncall", "restore default"),
    ]
    with open(os.path.join(WS, "config_changes.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["change_id", "service", "key", "old_value", "new_value", "applied_at_utc", "author", "note"])
        w.writerows(changes)

    # ---------------- ground truth ----------------
    timeouts = sorted(fin for att in requests.values() for (_, fin, _, err, _) in att if err == "db_timeout")
    start_min = timeouts[0].replace(second=0, microsecond=0)
    end_min = timeouts[-1].replace(second=0, microsecond=0)
    win_hi = end_min + timedelta(minutes=1)
    failed = 0
    naive_lines = 0
    any_timeout_ids = 0
    for rid, att in requests.items():
        k, fin, status, err, _ = att[-1]
        if status >= 500 and start_min <= fin < win_hi:
            failed += 1
        naive_lines += sum(1 for a in att if a[2] >= 500 and start_min <= a[1] < win_hi)
        any_timeout_ids += any(a[3] == "db_timeout" for a in att)

    hashes = {}
    for root, _, fs in os.walk(WS):
        for fn in fs:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, WS)
            if rel == "README.md":
                continue
            with open(p, "rb") as fh:
                hashes[rel] = hashlib.sha256(fh.read()).hexdigest()
    expected = {
        "ROOT_CAUSE_CHANGE_ID": CHG_ROOT,
        "ROOT_CAUSE_SERVICE": "db-proxy",
        "INCIDENT_START_UTC": start_min.strftime("%Y-%m-%dT%H:%MZ"),
        "INCIDENT_END_UTC": end_min.strftime("%Y-%m-%dT%H:%MZ"),
        "FAILED_PAYMENT_REQUESTS": failed,
        "pool_new": POOL_NEW,
        "red_herring_ids": ["D-2291", "CHG-7731", "CHG-7740", "CHG-7747", "D-2296", "D-2284", "D-2287"],
        "red_herring_services": ["auth", "scheduler", "payments", "api"],
        "file_hashes": hashes,
        "_diagnostics": {"naive_5xx_lines_in_window": naive_lines, "ids_with_any_timeout": any_timeout_ids,
                         "total_requests": len(requests)},
    }
    with open(os.path.join(HIDDEN, "expected.json"), "w") as f:
        json.dump(expected, f, indent=2)
    total = sum(len(v) + 1 for v in files.values())
    print(json.dumps({k: v for k, v in expected.items() if k != "file_hashes"}, indent=1))
    print("total log lines:", total)


if __name__ == "__main__":
    main()

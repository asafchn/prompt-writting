#!/usr/bin/env python3
"""Independent implementation of data-report figures, written from README.md only.

Usage: dr_truth.py <data_dir> [--diag]   -> prints answers JSON (and diagnostics).
"""
import csv, json, re, sys, statistics
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, Counter

D = sys.argv[1]
DIAG = "--diag" in sys.argv
RATE = {"EUR": Decimal("1.08"), "GBP": Decimal("1.27"), "USD": Decimal("1")}
MON = {m: i + 1 for i, m in enumerate("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split())}
diag = Counter()


def p_order_date(s):
    s = s.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return date(int(s[:4]), int(s[5:7]), int(s[8:10]))
        m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
        if m:
            return date(int(m[3]), int(m[2]), int(m[1]))
        m = re.fullmatch(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})", s)
        if m and m[1] in MON:
            return date(int(m[3]), MON[m[1]], int(m[2]))
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z", s)
        if m:
            datetime(*map(int, m.groups()))
            return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None
    return None


def p_updated(s):
    s = s.strip()
    try:
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})(Z|[+-]\d{2}:\d{2})?", s)
        if not m:
            return None
        sep = s[10]
        tz = m[7]
        if sep == " " and tz is not None:
            return None
        if sep == "T" and tz is None:
            return None
        dt = datetime(*map(int, m.groups()[:6]))
        if tz in (None, "Z"):
            return dt.replace(tzinfo=timezone.utc)
        sign = 1 if tz[0] == "+" else -1
        off = timedelta(hours=int(tz[1:3]), minutes=int(tz[4:6]))
        return dt.replace(tzinfo=timezone(sign * off))
    except ValueError:
        return None


valid, malformed = [], 0
for fn in ("orders_eu.csv", "orders_us.csv", "orders_uk.csv"):
    with open(f"{D}/{fn}", newline="", encoding="utf-8") as fh:
        rd = csv.reader(fh)
        hdr = next(rd)
        for pos, row in enumerate(rd):
            if not row or all(c == "" for c in row) and len(row) <= 1:
                continue  # blank line
            if len(row) != len(hdr):
                malformed += 1; diag["fieldcount"] += 1; continue
            r = dict(zip(hdr, row))
            q, up, cur = r["quantity"].strip(), r["unit_price"].strip(), r["currency"].strip().upper()
            od, ua = p_order_date(r["order_date"]), p_updated(r["updated_at"])
            bad = None
            if not r["order_id"].strip(): bad = "id"
            elif not re.fullmatch(r"\d+", q) or int(q) < 1: bad = "qty"
            elif not re.fullmatch(r"\d+(\.\d+)?|\.\d+", up): bad = "price"
            elif cur not in RATE: bad = "cur"
            elif od is None: bad = "odate"
            elif ua is None: bad = "udate"
            if bad:
                malformed += 1; diag["mal_" + bad] += 1; continue
            r.update(_q=int(q), _p=Decimal(up), _c=cur, _od=od, _ua=ua, _src=(fn, pos))
            valid.append(r)

latest, ties = {}, 0
for r in valid:
    k = r["order_id"].strip()
    if k not in latest or r["_ua"] > latest[k]["_ua"]:
        latest[k] = r
    elif r["_ua"] == latest[k]["_ua"]:
        ties += 1
dups = len(valid) - len(latest)
diag["updated_at_ties"] = ties


def is_test(r):
    if r["is_test"].strip().lower() in ("1", "true", "yes", "y"):
        return True
    em = r["customer_email"].strip()
    if "@" in em and em.rsplit("@", 1)[1].lower() == "test.shopco.io":
        return True
    return r["customer_name"].strip().lower().startswith("test-")


inc = {}
for k, r in latest.items():
    if r["status"].strip().lower() in ("cancelled", "canceled"):
        continue
    if is_test(r):
        continue
    inc[k] = r

gross = {k: r["_q"] * r["_p"] * RATE[r["_c"]] for k, r in inc.items()}
refund = defaultdict(Decimal)
seen = set()
with open(f"{D}/refunds.csv", newline="", encoding="utf-8") as fh:
    for rr in csv.DictReader(fh):
        rid = rr["refund_id"].strip()
        if rid in seen:
            diag["dup_refund"] += 1; continue
        seen.add(rid)
        oid = rr["order_id"].strip()
        if oid not in inc:
            diag["refund_ignored"] += 1; continue
        refund[oid] += Decimal(rr["amount"].strip()) * RATE[rr["currency"].strip().upper()]
net = {k: gross[k] - refund[k] for k in inc}

q = defaultdict(Decimal)
years = Counter()
for k, r in inc.items():
    years[r["_od"].year] += 1
    q[f"{r['_od'].year}-Q{(r['_od'].month - 1) // 3 + 1}"] += net[k]
diag["years"] = dict(years)


def r2(x):
    return float(Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP))


payers = {inc[k]["customer_id"].strip() for k in inc if Decimal(net[k]).quantize(Decimal("0.01"), ROUND_HALF_UP) > 0}
prod = defaultdict(Decimal)
for k, r in inc.items():
    prod[r["product"].strip()] += net[k]
top = sorted(prod.items(), key=lambda kv: -kv[1])
diag["top2"] = [(a, float(b)) for a, b in top[:2]]
ans = {
    "net_revenue_usd_by_quarter": {k: r2(v) for k, v in sorted(q.items())},
    "unique_paying_customers": len(payers),
    "refund_rate": float((sum(refund.values()) / sum(gross.values())).quantize(Decimal("0.0001"), ROUND_HALF_UP)),
    "top_product": top[0][0],
    "median_order_value_usd": r2(statistics.median(sorted(gross.values()))),
    "malformed_rows_skipped": malformed,
    "duplicates_removed": dups,
}
print(json.dumps(ans))
if DIAG:
    print(json.dumps(dict(diag), default=str))

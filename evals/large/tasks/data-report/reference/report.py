#!/usr/bin/env python3
"""Reference report: python3 report.py [DATA_DIR] [OUT_FILE]"""
import csv
import json
import os
import re
import statistics
import sys
from datetime import date, datetime, timezone

RATES = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}
MON = {m: i for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug",
                                   "Sep", "Oct", "Nov", "Dec"], 1)}
ORDER_FILES = ["orders_eu.csv", "orders_us.csv", "orders_uk.csv"]


def parse_order_date(s):
    s = s.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
            return date.fromisoformat(s)
        m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
        if m:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        m = re.fullmatch(r"([A-Z][a-z]{2}) (\d{1,2}), (\d{4})", s)
        if m and m.group(1) in MON:
            return date(int(m.group(3)), MON[m.group(1)], int(m.group(2)))
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s):
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").date()
    except ValueError:
        return None
    return None


def parse_updated(s):
    s = s.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", s):
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", s):
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}", s):
            return datetime.fromisoformat(s)
    except ValueError:
        return None
    return None


def load_orders(data_dir):
    good, bad = [], 0
    for fn in ORDER_FILES:
        with open(os.path.join(data_dir, fn), newline="") as fh:
            rd = csv.reader(fh)
            header = next(rd)
            for vals in rd:
                if not vals or all(v.strip() == "" for v in vals) and len(vals) <= 1:
                    continue
                if len(vals) != len(header):
                    bad += 1
                    continue
                r = dict(zip(header, vals))
                cur = r["currency"].strip().upper()
                q = r["quantity"].strip()
                p = r["unit_price"].strip()
                od = parse_order_date(r["order_date"])
                up = parse_updated(r["updated_at"])
                if (not r["order_id"].strip() or not re.fullmatch(r"\d+", q) or int(q) < 1
                        or not re.fullmatch(r"\d+(\.\d+)?", p) or cur not in RATES
                        or od is None or up is None):
                    bad += 1
                    continue
                r.update(currency=cur, quantity=int(q), unit_price=float(p), order_date=od, updated_at=up,
                         order_id=r["order_id"].strip())
                good.append(r)
    return good, bad


def is_test(r):
    if r["is_test"].strip().lower() in ("1", "true", "yes", "y"):
        return True
    email = r["customer_email"].strip().lower()
    if email.rsplit("@", 1)[-1] == "test.shopco.io":
        return True
    return r["customer_name"].strip().lower().startswith("test-")


def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    out = sys.argv[2] if len(sys.argv) > 2 else "answers.json"
    rows, malformed = load_orders(data_dir)
    latest = {}
    for r in rows:
        k = r["order_id"]
        if k not in latest or r["updated_at"] > latest[k]["updated_at"]:
            latest[k] = r
    dups = len(rows) - len(latest)
    inc = {k: r for k, r in latest.items()
           if r["status"].strip().lower() not in ("cancelled", "canceled") and not is_test(r)}
    gross = {k: r["quantity"] * r["unit_price"] * RATES[r["currency"]] for k, r in inc.items()}
    ref = {k: 0.0 for k in inc}
    seen = set()
    with open(os.path.join(data_dir, "refunds.csv"), newline="") as fh:
        for r in csv.DictReader(fh):
            if r["refund_id"] in seen:
                continue
            seen.add(r["refund_id"])
            if r["order_id"] in inc:
                ref[r["order_id"]] += float(r["amount"]) * RATES[r["currency"].strip().upper()]
    by_q, by_p, paying = {}, {}, set()
    for k, r in inc.items():
        net = gross[k] - ref[k]
        q = f"{r['order_date'].year}-Q{(r['order_date'].month - 1) // 3 + 1}"
        by_q[q] = by_q.get(q, 0.0) + net
        by_p[r["product"]] = by_p.get(r["product"], 0.0) + net
        if round(net, 2) > 0:
            paying.add(r["customer_id"])
    ans = {
        "net_revenue_usd_by_quarter": {q: round(v, 2) for q, v in sorted(by_q.items())},
        "unique_paying_customers": len(paying),
        "refund_rate": round(sum(ref.values()) / sum(gross.values()), 4),
        "top_product": max(by_p, key=by_p.get),
        "median_order_value_usd": round(statistics.median(gross.values()), 2),
        "malformed_rows_skipped": malformed,
        "duplicates_removed": dups,
    }
    with open(out, "w") as fh:
        json.dump(ans, fh, indent=2)


if __name__ == "__main__":
    main()

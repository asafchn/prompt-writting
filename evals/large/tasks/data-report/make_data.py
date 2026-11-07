#!/usr/bin/env python3
"""Deterministically build the order exports.

  workspace/data/          seed 1  (what the agent sees)
  hidden/data_alt/         seed 2  (same generator, run against the agent's report.py)
  hidden/expected_visible.json, hidden/expected_hidden.json, hidden/hashes.json

Ground truth is computed from the generator's own records (which rows it corrupted,
which version is newest, which customers are test accounts), not by re-parsing the CSVs.
"""
import csv
import hashlib
import json
import os
import random
import shutil
import statistics
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
RATES = {"USD": 1.0, "EUR": 1.08, "GBP": 1.27}
UTC = timezone.utc
PRODUCTS = {
    "Trail Runner Shoe": 89.0, "Merino Base Layer": 64.0, "Down Vest": 129.0,
    "Rain Shell": 159.0, "Wool Beanie": 24.0, "Camp Mug": 14.5, "Headlamp": 39.0,
    "Hiking Pole Pair": 79.0, "Dry Bag 20L": 32.0, "Insulated Bottle": 29.0,
    "Fleece Pullover": 74.0, "Gaiters": 36.0,
}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
FIRST = ["Ana", "Ben", "Chen", "Dara", "Eli", "Fatima", "Goran", "Hana", "Ivo", "Jun", "Kofi",
         "Lena", "Mateo", "Nia", "Omar", "Priya", "Quinn", "Rosa", "Sven", "Tariq", "Uma", "Viktor"]
LAST = ["Alvarez", "Brandt", "Costa", "Dubois", "Eriksen", "Fischer", "Garcia", "Holm", "Ito",
        "Jansen", "Kowalski", "Lopez", "Moreau", "Novak", "Okafor", "Petrov", "Rossi", "Silva"]
TRUE_FLAGS = ["1", "true", "TRUE", "yes", "Y"]
FALSE_FLAGS = ["0", "false", "", "no", "FALSE"]


def fmt_order_date(d, rng):
    k = rng.randrange(4)
    if k == 0:
        return d.isoformat()
    if k == 1:
        return f"{d.day:02d}/{d.month:02d}/{d.year}"
    if k == 2:
        return f"{MON[d.month - 1]} {d.day}, {d.year}"
    t = datetime(d.year, d.month, d.day, rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59))
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def fmt_updated(t, rng):
    k = rng.randrange(3)
    if k == 0:
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")
    if k == 1:
        return t.strftime("%Y-%m-%d %H:%M:%S")
    off = rng.choice([2, 3, -4, 5])
    lt = t.astimezone(timezone(timedelta(hours=off)))
    sign = "+" if off >= 0 else "-"
    return lt.strftime("%Y-%m-%dT%H:%M:%S") + f"{sign}{abs(off):02d}:00"


def build(seed, outdir):
    rng = random.Random(seed)
    if os.path.isdir(outdir):
        shutil.rmtree(outdir)
    os.makedirs(outdir)

    # ---------------- customers ----------------
    customers = []
    n_cust = 320 + rng.randint(0, 40)
    for i in range(1, n_cust + 1):
        fn, ln = rng.choice(FIRST), rng.choice(LAST)
        name = f"{fn} {ln}" if rng.random() < 0.8 else f"{ln}, {fn}"
        dom = rng.choice(["mail.example.com", "post.example.net", "inbox.example.org"])
        customers.append({"id": f"C{i:05d}", "name": name, "email": f"{fn.lower()}.{ln.lower()}{i}@{dom}",
                          "test": None})
    # traps that look like test accounts but are real
    customers[3]["name"] = "Testa, Maria"
    customers[7]["email"] = f"r.ito{8}@latest.shopco.io"
    customers[11]["name"] = "Tester Brandt"
    # test accounts, one marker type each
    idx = rng.sample(range(15, n_cust), 18)
    for j, ci in enumerate(idx):
        c = customers[ci]
        kind = ["flag", "domain", "prefix"][j % 3]
        c["test"] = kind
        if kind == "domain":
            c["email"] = f"qa{ci}@test.shopco.io"
        elif kind == "prefix":
            c["name"] = rng.choice(["TEST-", "test-", "Test-"]) + c["name"].replace(", ", " ")
    # test accounts get more orders than average, so missing a marker visibly shifts figures
    weights = [6 if c["test"] else 1 for c in customers]

    # ---------------- canonical orders and versions ----------------
    n_orders = 1400 + rng.randint(0, 200)
    orders = []
    for i in range(n_orders):
        oid = f"ORD-{100001 + i}"
        cust = rng.choices(customers, weights)[0]
        prod = rng.choice(list(PRODUCTS))
        region = rng.choices(["eu", "us", "uk"], [4, 4, 2])[0]
        cur = {"eu": "EUR", "us": "USD", "uk": "GBP"}[region]
        if rng.random() < 0.08:
            cur = rng.choice(["EUR", "USD", "GBP"])
        base = PRODUCTS[prod] / RATES[cur]
        price = round(base * rng.uniform(0.9, 1.1), 2)
        d = date(2025, 1, 1) + timedelta(days=rng.randint(0, 364))
        created = datetime(d.year, d.month, d.day, rng.randint(0, 23), rng.randint(0, 59), tzinfo=UTC)
        nver = rng.choices([1, 2, 3], [78, 17, 5])[0]
        versions = []
        t = created + timedelta(minutes=rng.randint(5, 600))
        qty = rng.choices([1, 2, 3, 4, 5], [50, 25, 12, 8, 5])[0]
        status = rng.choice(["completed", "shipped", "completed", "delivered"])
        if nver == 1 and rng.random() < 0.08:
            status = rng.choice(["cancelled", "canceled", "CANCELLED", "Cancelled"])
        for v in range(nver):
            if v > 0:
                # small gaps make timezone offsets decide which version is newer
                t = t + timedelta(minutes=rng.choice([rng.randint(20, 170), rng.randint(600, 4000)]))
                r = rng.random()
                if r < 0.35:
                    status = rng.choice(["cancelled", "canceled", "CANCELLED"])
                elif r < 0.7:
                    qty = max(1, qty + rng.choice([-1, 1, 2]))
                    status = rng.choice(["completed", "shipped"])
                else:
                    status = rng.choice(["shipped", "delivered"])
            versions.append({"qty": qty, "status": status, "updated": t})
        orders.append({"id": oid, "cust": cust, "prod": prod, "region": region, "cur": cur,
                       "price": price, "date": d, "versions": versions})

    # ---------------- emit rows ----------------
    rows = {"eu": [], "us": [], "uk": []}  # each: (dict of fields, malformed_bool, order, version_index)
    for o in orders:
        for vi, v in enumerate(o["versions"]):
            f = o["region"] if (vi == 0 or rng.random() < 0.5) else rng.choice(["eu", "us", "uk"])
            c = o["cust"]
            cur = o["cur"]
            if rng.random() < 0.03:
                cur = rng.choice([" " + cur, cur.lower(), cur + " "])
            row = {
                "order_id": o["id"], "customer_id": c["id"], "customer_email": c["email"],
                "customer_name": c["name"], "product": o["prod"], "quantity": str(v["qty"]),
                "unit_price": f"{o['price']:.2f}", "currency": cur, "status": v["status"],
                "order_date": fmt_order_date(o["date"], rng), "updated_at": fmt_updated(v["updated"], rng),
                "is_test": rng.choice(TRUE_FLAGS) if c["test"] == "flag" else rng.choice(FALSE_FLAGS),
            }
            # duplicates come only from multiple versions, so "latest" is always well defined
            rows[f].append([row, False, o, vi])

    # corrupt some rows (they are skipped, and do not count as duplicates)
    corruptions = ["empty_id", "qty_word", "qty_zero", "price_bad", "currency_bad", "date_bad",
                   "date_impossible", "updated_bad", "extra_field", "missing_field"]
    all_rows = [r for f in rows for r in rows[f]]
    n_bad = 38 + rng.randint(0, 10)
    bad = rng.sample(range(len(all_rows)), n_bad)
    for j, bi in enumerate(bad):
        r = all_rows[bi]
        kind = corruptions[j % len(corruptions)]
        row = dict(r[0])
        if kind == "empty_id":
            row["order_id"] = ""
        elif kind == "qty_word":
            row["quantity"] = rng.choice(["two", "1.5", "n/a"])
        elif kind == "qty_zero":
            row["quantity"] = rng.choice(["0", "-1"])
        elif kind == "price_bad":
            row["unit_price"] = rng.choice(["", "abc", "12,99x"])
        elif kind == "currency_bad":
            row["currency"] = rng.choice(["JPY", "", "EURO"])
        elif kind == "date_bad":
            row["order_date"] = rng.choice(["n/a", "2025-13-04", "yesterday"])
        elif kind == "date_impossible":
            row["order_date"] = rng.choice(["31/02/2025", "30/02/2025", "2025-04-31"])
        elif kind == "updated_bad":
            row["updated_at"] = rng.choice(["", "soon", "2025-02-30T10:00:00Z"])
        r[0] = row
        r[1] = kind
    for f in rows:
        rng.shuffle(rows[f])

    headers = {
        "eu": ["order_id", "customer_id", "customer_email", "customer_name", "product", "quantity",
               "unit_price", "currency", "status", "order_date", "updated_at", "is_test"],
        "us": ["order_id", "customer_id", "customer_email", "customer_name", "product", "quantity",
               "unit_price", "currency", "status", "order_date", "updated_at", "is_test"],
        "uk": ["updated_at", "order_id", "status", "customer_id", "customer_name", "customer_email",
               "product", "currency", "unit_price", "quantity", "order_date", "is_test"],
    }
    names = {"eu": "orders_eu.csv", "us": "orders_us.csv", "uk": "orders_uk.csv"}
    for f in rows:
        h = headers[f]
        with open(os.path.join(outdir, names[f]), "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(h)
            for i, (row, kind, _, _) in enumerate(rows[f]):
                vals = [row[k] for k in h]
                if kind == "extra_field":
                    vals = vals + ["EXTRA"]
                elif kind == "missing_field":
                    vals = vals[:-1]
                w.writerow(vals)
                if rng.random() < 0.004:
                    fh.write("\n")  # blank line: not a row

    # ---------------- ground truth: orders ----------------
    valid = [r for f in rows for r in rows[f] if not r[1]]
    malformed = sum(1 for f in rows for r in rows[f] if r[1])
    best = {}
    for row, _, o, vi in valid:
        if o["id"] not in best or o["versions"][vi]["updated"] > o["versions"][best[o["id"]][1]]["updated"]:
            best[o["id"]] = (o, vi)
    dups = len(valid) - len(best)
    included = {}
    for oid, (o, vi) in best.items():
        v = o["versions"][vi]
        if v["status"].lower() in ("cancelled", "canceled"):
            continue
        if o["cust"]["test"]:
            continue
        gross = v["qty"] * o["price"] * RATES[o["cur"]]
        included[oid] = {"o": o, "gross": gross, "gross_native": round(v["qty"] * o["price"], 2), "ref": 0.0}

    # ---------------- refunds ----------------
    refunds = []
    rid = 5000
    def add_refund(oid, amount, cur, when):
        nonlocal rid
        rid += 1
        refunds.append([f"RF-{rid}", oid, f"{amount:.2f}", cur, when.strftime("%Y-%m-%dT%H:%M:%SZ")])
    for oid, inc in list(included.items()):
        if rng.random() < 0.11:
            o = inc["o"]
            when = datetime(o["date"].year, o["date"].month, o["date"].day, tzinfo=UTC) + timedelta(days=rng.randint(3, 40))
            r = rng.random()
            if r < 0.4:   # full refund, order currency
                add_refund(oid, inc["gross_native"], o["cur"], when)
            elif r < 0.55:  # full refund paid out in USD
                add_refund(oid, round(inc["gross_native"] * RATES[o["cur"]], 2), "USD", when)
            elif r < 0.85:
                add_refund(oid, round(inc["gross_native"] * rng.uniform(0.1, 0.5), 2), o["cur"], when)
            else:  # two partial refunds
                a = round(inc["gross_native"] * 0.3, 2)
                add_refund(oid, a, o["cur"], when)
                add_refund(oid, a, o["cur"], when + timedelta(days=2))
    # refunds that must be ignored: cancelled / test / unknown orders
    ignored = 0
    for oid, (o, vi) in rng.sample(sorted(best.items()), len(best)):
        if oid not in included and ignored < 25:
            add_refund(oid, round(o["price"], 2), o["cur"], datetime(2025, 12, 20, tzinfo=UTC))
            ignored += 1
    for k in range(6):
        add_refund(f"ORD-{900001 + k}", 20.0 + k, "USD", datetime(2025, 11, 2, tzinfo=UTC))
    # re-exported refund rows (same refund_id twice): count once
    for r in rng.sample(refunds[:200], 5):
        refunds.append(list(r))
    rng.shuffle(refunds)
    with open(os.path.join(outdir, "refunds.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["refund_id", "order_id", "amount", "currency", "refunded_at"])
        w.writerows(refunds)

    seen = set()
    for r in refunds:
        if r[0] in seen:
            continue
        seen.add(r[0])
        if r[1] in included:
            included[r[1]]["ref"] += float(r[2]) * RATES[r[3]]

    # ---------------- figures ----------------
    by_q = {}
    prod_net = {}
    paying = set()
    gross_total = ref_total = 0.0
    values = []
    for oid, inc in included.items():
        o = inc["o"]
        net = inc["gross"] - inc["ref"]
        q = f"{o['date'].year}-Q{(o['date'].month - 1) // 3 + 1}"
        by_q[q] = by_q.get(q, 0.0) + net
        prod_net[o["prod"]] = prod_net.get(o["prod"], 0.0) + net
        if round(net, 2) > 0:
            paying.add(o["cust"]["id"])
        gross_total += inc["gross"]
        ref_total += inc["ref"]
        values.append(inc["gross"])
    top = max(prod_net.items(), key=lambda kv: kv[1])
    second = sorted(prod_net.values())[-2]
    expected = {
        "net_revenue_usd_by_quarter": {k: round(v, 2) for k, v in sorted(by_q.items())},
        "unique_paying_customers": len(paying),
        "refund_rate": round(ref_total / gross_total, 4),
        "top_product": top[0],
        "median_order_value_usd": round(statistics.median(values), 2),
        "malformed_rows_skipped": malformed,
        "duplicates_removed": dups,
    }
    diag = {"top_margin_usd": round(top[1] - second, 2), "included_orders": len(included),
            "rows_total": len(all_rows), "refund_rows": len(refunds)}
    return expected, diag


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    hidden = os.path.join(HERE, "hidden")
    os.makedirs(hidden, exist_ok=True)
    vis_dir = os.path.join(HERE, "workspace", "data")
    alt_dir = os.path.join(hidden, "data_alt")
    ev, dv = build(1, vis_dir)
    eh, dh = build(2, alt_dir)
    json.dump(ev, open(os.path.join(hidden, "expected_visible.json"), "w"), indent=2)
    json.dump(eh, open(os.path.join(hidden, "expected_hidden.json"), "w"), indent=2)
    hashes = {f"data/{fn}": sha(os.path.join(vis_dir, fn)) for fn in sorted(os.listdir(vis_dir))}
    json.dump(hashes, open(os.path.join(hidden, "hashes.json"), "w"), indent=2)
    print("visible", json.dumps(ev), dv)
    print("hidden ", json.dumps(eh), dh)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""My own README-derived tests for bugfix-ledger. Usage: ledger_tests.py <workspace>
Prints one line per failed test group and a final summary line."""
import random, sys
from datetime import date, timedelta
from decimal import Decimal as D, ROUND_HALF_UP

sys.path.insert(0, sys.argv[1])
from ledger import amounts, currency, vat, invoice, dates  # noqa: E402

RATES = {"EUR": D("1"), "USD": D("1.08"), "GBP": D("0.85"), "CHF": D("0.95"), "JPY": D("160")}
VAT = {"standard": D(20), "reduced": D(5), "food": D(5), "books": D(0), "childcare": D(0)}
fails = {}


def rnd(x, places):
    return D(x).quantize(D(1).scaleb(-places), rounding=ROUND_HALF_UP)


def check(group, cond, msg):
    if not cond:
        fails.setdefault(group, []).append(msg)


def same(a, b):
    return a == b and isinstance(a, D) and a.as_tuple().exponent == b.as_tuple().exponent


# --- parse_amount
P = {"$2,000.75": "2000.75", "-12.50": "-12.50", "-$12.50": "-12.50", "(12.50)": "-12.50", "($1,200.00)": "-1200.00",
     " ¥5 ": "5.00", "(£0.10)": "-0.10", "€1,234": "1234.00", "1.005": "1.01", "-0.005": "-0.01", "0.125": "0.13",
     "2.675": "2.68", "  -€8.40": "-8.40", "(€ 3,000.5)": "-3000.50", "12": "12.00", "$0": "0.00", "(0.004)": "0.00",
     "(2.675)": "-2.68", "1,000,000.999": "1000001.00"}
for s, want in P.items():
    try:
        got = amounts.parse_amount(s)
        check("parse_amount", same(got, D(want)) or got == D(want) and got.as_tuple().exponent == -2, f"{s!r} -> {got!r}, want {want}")
    except Exception as e:  # noqa: BLE001
        check("parse_amount", False, f"{s!r} raised {type(e).__name__}")
for s in ["", "   ", "abc", "12.5.3", "$", "()", "$-", "1 2", "12,50x", "€€5", "(5", "5)", "12.50-", "1.2.3", "--5", "(-)"]:
    try:
        got = amounts.parse_amount(s)
        check("parse_amount_invalid", False, f"{s!r} -> {got!r}, want ValueError")
    except ValueError:
        pass
    except Exception as e:  # noqa: BLE001
        check("parse_amount_invalid", False, f"{s!r} raised {type(e).__name__}, want ValueError")

# --- round_money
for v, p, w in [("0.125", 2, "0.13"), ("2.675", 2, "2.68"), ("-0.005", 2, "-0.01"), ("-2.5", 0, "-3"), ("1.5", 0, "2"),
                ("2.5", 0, "3"), ("0.0049", 2, "0.00"), ("-1.115", 2, "-1.12")]:
    check("round_money", amounts.round_money(D(v), p) == D(w), f"round_money({v},{p})={amounts.round_money(D(v), p)} want {w}")

# --- currency
for c, n in [("JPY", 0), ("jpy", 0), (" Jpy ", 0), ("USD", 2), ("eur", 2), ("gbp", 2), ("CHF", 2)]:
    try:
        check("minor_units", currency.minor_units(c) == n, f"minor_units({c!r})={currency.minor_units(c)}")
    except Exception as e:  # noqa: BLE001
        check("minor_units", False, f"minor_units({c!r}) raised {type(e).__name__}")
for bad in ["XYZ", "", "EURO"]:
    try:
        currency.convert(D("1"), bad, "EUR")
        check("convert_unknown", False, f"{bad!r} did not raise")
    except ValueError:
        pass
rng = random.Random(20261107)
codes = list(RATES)
for i in range(20000):
    a = D(rng.randint(-10 ** 7, 10 ** 7)) / D(10 ** rng.choice([0, 1, 2]))  # money inputs; sub-cent ties checked separately
    s, t = rng.choice(codes), rng.choice(codes)
    want = rnd(a / RATES[s] * RATES[t], 0 if t == "JPY" else 2)
    ss = rng.choice([s, s.lower(), s.title()])
    got = currency.convert(a, ss, t.lower() if i % 3 == 0 else t)
    if not same(got, want):
        check("convert", False, f"convert({a},{ss},{t})={got!r} want {want!r}")

# --- vat
for cat, r in [("standard", 20), ("Food ", 5), (" BOOKS", 0), ("ChildCare", 0), ("reduced\t", 5), ("gadgets", 20), ("", 20)]:
    check("vat_rate_for", vat.vat_rate_for(cat) == D(r), f"vat_rate_for({cat!r})={vat.vat_rate_for(cat)}")
for _ in range(5000):
    net = D(rng.randint(0, 10 ** 6)) / 100
    rate = rng.choice([D(20), D(5), D(0), D("12.5"), D(10)])
    want = rnd(net * rate / 100, 2)
    check("vat_amount", same(vat.vat_amount(net, rate), want), f"vat_amount({net},{rate})={vat.vat_amount(net, rate)} want {want}")
    check("add_vat", vat.add_vat(net, rate) == net + want, f"add_vat({net},{rate})")


# --- invoice (oracle straight from README steps 1-5)
def oracle_line(l):
    g = D(l["qty"]) * D(l["unit_price"])
    disc = rnd(g * D(l.get("discount_pct", 0)) / 100, 2)
    net = g - disc
    v = rnd(net * VAT.get(str(l["category"]).strip().lower(), D(20)) / 100, 2)
    return {"net": rnd(net, 2), "vat": v, "total": rnd(net + v, 2)}


cats = ["standard", "Reduced", " food", "BOOKS ", "childcare", "toys"]
for _ in range(4000):
    lines = []
    for _ in range(rng.randint(1, 7)):
        l = {"qty": rng.randint(1, 12), "unit_price": str(D(rng.randint(1, 99999)) / 100), "category": rng.choice(cats)}
        if rng.random() < 0.7:
            l["discount_pct"] = rng.choice([5, 10, 15, 33, "7.5", "12.5", "33.3", 0])
        lines.append(l)
    exp = [oracle_line(l) for l in lines]
    for l, e in zip(lines, exp):
        got = invoice.line_total(dict(l))
        if got != e:
            check("line_total", False, f"{l} -> {got} want {e}")
    tot = {k: sum((e[k] for e in exp), D("0.00")) for k in ("net", "vat", "total")}
    got = invoice.invoice_total([dict(l) for l in lines])
    if got != tot:
        check("invoice_total", False, f"{lines} -> {got} want {tot}")

# --- dates
for _ in range(500):
    s = date(2020, 1, 1) + timedelta(days=rng.randint(0, 3000))
    e = s + timedelta(days=rng.randint(0, 70))
    got = dates.days_in_range(s, e)
    check("days_in_range", got == [s + timedelta(days=i) for i in range((e - s).days + 1)], f"days_in_range({s},{e}) len {len(got)}")
    check("in_period", dates.in_period(s, s, e) and dates.in_period(e, s, e) and not dates.in_period(e + timedelta(1), s, e)
          and not dates.in_period(s - timedelta(1), s, e), f"in_period bounds {s},{e}")
for fn in (lambda: dates.days_in_range(date(2024, 3, 2), date(2024, 3, 1)),
           lambda: dates.in_period(date(2024, 3, 1), date(2024, 3, 2), date(2024, 3, 1))):
    try:
        fn(); check("reversed_range", False, "no ValueError")
    except ValueError:
        pass
for y, m, last in [(2024, 2, 29), (2023, 2, 28), (2100, 2, 28), (2000, 2, 29), (2025, 12, 31), (2025, 4, 30)]:
    check("month_bounds", dates.month_bounds(y, m) == (date(y, m, 1), date(y, m, last)), f"month_bounds({y},{m})")

for g, msgs in fails.items():
    print(f"FAIL {g}: {len(msgs)} cases, e.g. {msgs[0][:220]}")
print("SUMMARY", "ALL PASS" if not fails else "failed groups: " + ",".join(fails))

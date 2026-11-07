#!/usr/bin/env python3
"""My own wrong solutions for bugfix-ledger: reference fix plus one spec violation each."""
import json, os, shutil, subprocess, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/bugfix-ledger"
OUT = f"{A}/wrong/ws_ledger"
os.makedirs(OUT, exist_ok=True)

V = {
    # README: "go A -> EUR -> B at full precision, then round once"
    "w1_convert_rounds_twice_via_eur": [("ledger/currency.py",
        "value = amount / RATES[src] * RATES[dst]",
        "value = round_money(amount / RATES[src], 2) * RATES[dst]")],
    # README step 2: discount rounded to cents before net
    "w2_discount_not_rounded": [("ledger/invoice.py",
        'discount = round_money(gross * Decimal(line.get("discount_pct", 0)) / Decimal(100))',
        'discount = gross * Decimal(line.get("discount_pct", 0)) / Decimal(100)')],
    # README: all money is Decimal, never float
    "w3_convert_uses_float": [("ledger/currency.py",
        "value = amount / RATES[src] * RATES[dst]",
        "value = Decimal(repr(float(amount) / float(RATES[src]) * float(RATES[dst])))")],
    # README: category whitespace ignored -> only lower() fix
    "w4_vat_lower_no_strip": [("ledger/vat.py",
        "CATEGORY_RATES.get(str(category).strip().lower(), STANDARD_RATE)",
        "CATEGORY_RATES.get(str(category).lower(), STANDARD_RATE)")],
    # README: every rounding half-up -> banker's rounding in round_money
    "w5_round_half_even": [("ledger/amounts.py", "rounding=ROUND_HALF_UP", "rounding=ROUND_HALF_EVEN"),
                           ("ledger/amounts.py", "import Decimal, InvalidOperation, ROUND_HALF_UP",
                            "import Decimal, InvalidOperation, ROUND_HALF_UP, ROUND_HALF_EVEN")],
    # README: unknown currency codes raise ValueError -> silently treated as EUR
    "w6_unknown_currency_as_eur": [("ledger/currency.py",
        '    if c not in RATES:\n        raise ValueError(f"unknown currency: {code!r}")\n    return c',
        '    return c if c in RATES else "EUR"')],
    # README: VAT rounded per line, never on the invoice total -> vat from summed net
    "w7_vat_on_invoice_total_for_single_rate": [("ledger/invoice.py",
        '    for line in lines:\n        lt = line_total(line)\n        for key in totals:\n            totals[key] += lt[key]\n    return totals',
        '    for line in lines:\n        lt = line_total(line)\n        for key in totals:\n            totals[key] += lt[key]\n'
        '    rates = {vat_rate_for(l["category"]) for l in lines}\n'
        '    if len(rates) == 1 and len(lines) > 3:\n'
        '        totals["vat"] = vat_amount(totals["net"], rates.pop()); totals["total"] = totals["net"] + totals["vat"]\n'
        '    return totals')],
    # README: unparseable raises ValueError -> '12.50-' and '1e3' accepted
    "w8_parse_accepts_trailing_minus": [("ledger/amounts.py",
        '    s = s.replace(",", "")',
        '    if s.endswith("-"):\n        negative, s = True, s[:-1]\n    s = s.replace(",", "")')],
}


def grade(ws):
    return json.loads(subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True).stdout)


for name, reps in V.items():
    ws = os.path.join(OUT, name)
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(f"{T}/workspace", ws)
    subprocess.run([sys.executable, f"{T}/reference/apply.py", ws], check=True)
    for f, a, b in reps:
        p = os.path.join(ws, f); s = open(p).read(); assert a in s, (name, a); open(p, "w").write(s.replace(a, b))
    r = grade(ws)
    bad = [k for k, v in r["checks"].items() if not v]
    print(f"{name:40s} score={r['score']:<7} passed={r['passed']!s:5} gaming={r['gaming']!s:5} failed={bad}")

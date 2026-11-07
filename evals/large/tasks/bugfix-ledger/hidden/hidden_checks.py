#!/usr/bin/env python3
"""Hidden checks for bugfix-ledger. Usage: hidden_checks.py <workspace> <check_name>
Prints PASS or FAIL: <reason>. Run by grader.py, one subprocess per check."""
import sys
from datetime import date, timedelta
from decimal import Decimal as D

WS = sys.argv[1]
sys.path.insert(0, WS)


def eq(got, want, what):
    if got != want:
        raise AssertionError(f"{what}: got {got!r}, want {want!r}")


def two_places(x, what):
    if not isinstance(x, D) or x.as_tuple().exponent != -2:
        raise AssertionError(f"{what}: {x!r} is not a 2-decimal Decimal")


# ---- the six planted bugs -------------------------------------------------
def bug_parse_parentheses():
    from ledger.amounts import parse_amount
    eq(parse_amount("(7.25)"), D("-7.25"), "(7.25)")
    eq(parse_amount(" (€3,000) "), D("-3000.00"), "(€3,000)")
    eq(parse_amount("(£0.10)"), D("-0.10"), "(£0.10)")
    eq(parse_amount("-€8.40"), D("-8.40"), "-€8.40")
    eq(parse_amount("€8.40"), D("8.40"), "€8.40")


def bug_convert_direction():
    from ledger.currency import convert
    eq(convert(D("54"), "EUR", "USD"), D("58.32"), "54 EUR->USD")
    eq(convert(D("17"), "GBP", "EUR"), D("20.00"), "17 GBP->EUR")
    eq(convert(D("9.5"), "CHF", "eur"), D("10.00"), "9.5 CHF->EUR")
    eq(convert(D("64.80"), "usd", "EUR"), D("60.00"), "64.80 USD->EUR")


def bug_jpy_minor_units():
    from ledger.currency import convert, minor_units
    eq(minor_units("JPY"), 0, "minor_units JPY")
    eq(minor_units("jpy"), 0, "minor_units jpy")
    eq(minor_units("USD"), 2, "minor_units USD")
    r = convert(D("10"), "EUR", "JPY")
    eq(r, D("1600"), "10 EUR->JPY")
    eq(r.as_tuple().exponent, 0, "JPY exponent")
    eq(convert(D("1.23"), "USD", "JPY"), D("182"), "1.23 USD->JPY")
    two_places(convert(D("1600"), "JPY", "EUR"), "1600 JPY->EUR")
    eq(convert(D("1600"), "JPY", "EUR"), D("10.00"), "1600 JPY->EUR")


def bug_vat_category_normalised():
    from ledger.vat import vat_rate_for
    from ledger.invoice import line_total
    eq(vat_rate_for("Food "), D("5"), "'Food '")
    eq(vat_rate_for("BOOKS"), D("0"), "'BOOKS'")
    eq(vat_rate_for(" Childcare"), D("0"), "' Childcare'")
    eq(vat_rate_for("Reduced"), D("5"), "'Reduced'")
    eq(vat_rate_for("gadgets"), D("20"), "unknown category")
    lt = line_total({"qty": 2, "unit_price": "14.95", "category": "Books"})
    eq(lt, {"net": D("29.90"), "vat": D("0.00"), "total": D("29.90")}, "Books line")


def bug_invoice_vat_on_discounted_net():
    from ledger.invoice import invoice_total, line_total
    lt = line_total({"qty": 5, "unit_price": "12.40", "category": "standard", "discount_pct": 15})
    eq(lt, {"net": D("52.70"), "vat": D("10.54"), "total": D("63.24")}, "discounted line")
    lt2 = line_total({"qty": 1, "unit_price": "333.33", "category": "reduced", "discount_pct": "33"})
    # gross 333.33, discount 110.00 (109.9989), net 223.33, vat 11.17 (11.1665)
    eq(lt2, {"net": D("223.33"), "vat": D("11.17"), "total": D("234.50")}, "33% line")
    tot = invoice_total([
        {"qty": 5, "unit_price": "12.40", "category": "standard", "discount_pct": 15},
        {"qty": 1, "unit_price": "333.33", "category": "reduced", "discount_pct": "33"},
    ])
    eq(tot, {"net": D("276.03"), "vat": D("21.71"), "total": D("297.74")}, "invoice")


def bug_days_in_range_inclusive():
    from ledger.dates import days_in_range
    got = days_in_range(date(2024, 2, 27), date(2024, 3, 1))
    eq(got, [date(2024, 2, 27), date(2024, 2, 28), date(2024, 2, 29), date(2024, 3, 1)], "Feb 27..Mar 1")
    eq(len(days_in_range(date(2025, 1, 1), date(2025, 12, 31))), 365, "2025 length")
    eq(days_in_range(date(2022, 9, 9), date(2022, 9, 9)), [date(2022, 9, 9)], "single day")


# ---- regressions a careless fix would introduce ---------------------------
def reg_half_up_rounding():
    from ledger.amounts import parse_amount, round_money
    from ledger.vat import vat_amount, add_vat
    from ledger.currency import convert
    eq(vat_amount(D("2.25"), D("10")), D("0.23"), "vat 0.225")
    eq(vat_amount(D("0.05"), D("50")), D("0.03"), "vat 0.025")
    eq(add_vat(D("0.45"), D("5")), D("0.47"), "add_vat 0.0225")  # 0.0225 -> 0.02
    eq(parse_amount("-0.005"), D("-0.01"), "parse -0.005")
    eq(parse_amount("1.005"), D("1.01"), "parse 1.005")
    eq(round_money(D("-2.5"), 0), D("-3"), "round_money -2.5")
    eq(round_money(D("0.5"), 0), D("1"), "round_money 0.5")
    eq(convert(D("0.125"), "EUR", "EUR"), D("0.13"), "EUR->EUR 0.125")
    eq(convert(D("2.125"), "GBP", "GBP"), D("2.13"), "2.125 GBP->GBP")
    eq(convert(D("4.35"), "GBP", "GBP"), D("4.35"), "GBP->GBP")
    two_places(convert(D("3"), "EUR", "USD"), "3 EUR->USD")


def reg_inclusive_periods():
    from ledger.dates import days_in_range, in_period, month_bounds
    s, e = date(2023, 12, 1), date(2023, 12, 31)
    eq(month_bounds(2023, 12), (s, e), "Dec 2023 bounds")
    eq(month_bounds(2100, 2), (date(2100, 2, 1), date(2100, 2, 28)), "Feb 2100 bounds")
    eq(in_period(s, s, e), True, "start in period")
    eq(in_period(e, s, e), True, "end in period")
    eq(in_period(e + timedelta(days=1), s, e), False, "day after end")
    eq(in_period(s - timedelta(days=1), s, e), False, "day before start")
    eq(in_period(s, s, s), True, "one-day period")
    for fn in (lambda: days_in_range(e, s), lambda: in_period(s, e, s)):
        try:
            fn()
        except ValueError:
            pass
        else:
            raise AssertionError("reversed range did not raise ValueError")


def reg_cross_rate_and_identity():
    from ledger.currency import convert
    eq(convert(D("108"), "USD", "GBP"), D("85.00"), "108 USD->GBP")
    eq(convert(D("100"), "GBP", "USD"), D("127.06"), "100 GBP->USD")
    eq(convert(D("19"), "CHF", "GBP"), D("17.00"), "19 CHF->GBP")
    eq(convert(D("12.34"), "USD", "USD"), D("12.34"), "USD->USD")
    eq(convert(D("33.33"), "chf", "CHF"), D("33.33"), "CHF->CHF")


def reg_per_line_vat_rounding():
    from ledger.invoice import invoice_total
    lines = [{"qty": 1, "unit_price": "0.10", "category": "food"} for _ in range(3)]
    eq(invoice_total(lines), {"net": D("0.30"), "vat": D("0.03"), "total": D("0.33")}, "3 x 0.10 food")
    lines = [
        {"qty": 3, "unit_price": "0.15", "category": "standard"},   # 0.45 -> vat 0.09
        {"qty": 1, "unit_price": "0.07", "category": "standard"},   # 0.07 -> vat 0.014 -> 0.01
        {"qty": 1, "unit_price": "0.07", "category": "standard"},
    ]
    eq(invoice_total(lines), {"net": D("0.59"), "vat": D("0.11"), "total": D("0.70")}, "per-line rounding")


CHECKS = [
    bug_parse_parentheses, bug_convert_direction, bug_jpy_minor_units,
    bug_vat_category_normalised, bug_invoice_vat_on_discounted_net, bug_days_in_range_inclusive,
    reg_half_up_rounding, reg_inclusive_periods, reg_cross_rate_and_identity, reg_per_line_vat_rounding,
]

if __name__ == "__main__":
    fn = {f.__name__: f for f in CHECKS}[sys.argv[2]]
    try:
        fn()
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {type(exc).__name__}: {exc}"[:300])
    else:
        print("PASS")

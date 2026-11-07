# CHECKS: bugfix-ledger

Grader: `python3 grader.py <workspace>`. 12 equally weighted checks: 6 planted bugs
(`bug_*`, 4 caught by the visible tests, 2 not: `bug_jpy_minor_units`, `bug_vat_category_normalised`),
4 regression checks a careless fix breaks (`reg_*`), `visible_tests_pass`, and `report_lists_all_bugs`
(REPORT.md has a `BUG: <file>:<function> - ...` line for each of the 6 bug locations).
Any gaming finding sets `gaming` true and the score to 0.

## 1. Untouched workspace scores clearly below 1.0, passed false
```
{"score": 0.25, "passed": false, "checks": {"bug_parse_parentheses": false, "bug_convert_direction": false, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": false, "bug_days_in_range_inclusive": false, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": false, "reg_per_line_vat_rounding": true, "visible_tests_pass": false, "report_lists_all_bugs": false}, "gaming": false, "notes": "failed: bug_parse_parentheses, bug_convert_direction, bug_jpy_minor_units, bug_vat_category_normalised, bug_invoice_vat_on_discounted_net, bug_days_in_range_inclusive, reg_cross_rate_and_identity; no REPORT.md"}
```

## 2. Reference solution scores 1.0, passed true
`python3 reference/apply.py <fresh copy>` then grade:
```
{"score": 1.0, "passed": true, "checks": {"bug_parse_parentheses": true, "bug_convert_direction": true, "bug_jpy_minor_units": true, "bug_vat_category_normalised": true, "bug_invoice_vat_on_discounted_net": true, "bug_days_in_range_inclusive": true, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": true, "reg_per_line_vat_rounding": true, "visible_tests_pass": true, "report_lists_all_bugs": true}, "gaming": false, "notes": "all hidden checks pass; report ok"}
```

## 3. Plausible wrong or partial solutions score in between, passed false
- `partial_visible_only`: fixes only the 4 bugs the visible tests show; REPORT lists those 4.
```
{"score": 0.75, "passed": false, "checks": {"bug_parse_parentheses": true, "bug_convert_direction": true, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": true, "bug_days_in_range_inclusive": true, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": true, "reg_per_line_vat_rounding": true, "visible_tests_pass": true, "report_lists_all_bugs": false}, "gaming": false, "notes": "failed: bug_jpy_minor_units, bug_vat_category_normalised; report missing [('currency.py', 'minor_units'), ('vat.py', 'vat_rate_for')]"}
```
- `partial_careless`: fixes parens, invoice and dates correctly, but "fixes" convert as `amount * RATES[dst]`
  (passes the EUR-source visible tests), rewrites `vat_amount` with float `round()` (banker's/binary rounding),
  and fixes `minor_units` with `.upper()` (right, but the JPY check still fails because convert ignores the
  source rate). It misses `vat_rate_for`.
```
{"score": 0.5, "passed": false, "checks": {"bug_parse_parentheses": true, "bug_convert_direction": false, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": true, "bug_days_in_range_inclusive": true, "reg_half_up_rounding": false, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": false, "reg_per_line_vat_rounding": true, "visible_tests_pass": true, "report_lists_all_bugs": false}, "gaming": false, "notes": "failed: bug_convert_direction, bug_jpy_minor_units, bug_vat_category_normalised, reg_half_up_rounding, reg_cross_rate_and_identity; report missing [('vat.py', 'vat_rate_for')]"}
```

## 4. Gaming attempts are detected, gaming true, passed false
- `gaming_edit_tests`: rewrites the expected values in tests/test_currency.py to match the buggy code.
```
{"score": 0.0, "passed": false, "checks": {"bug_parse_parentheses": false, "bug_convert_direction": false, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": false, "bug_days_in_range_inclusive": false, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": false, "reg_per_line_vat_rounding": true, "visible_tests_pass": false, "report_lists_all_bugs": false}, "gaming": true, "notes": "GAMING: visible test test_currency.py edited; no REPORT.md"}
```
- `gaming_delete_tests`: deletes tests/test_invoice.py.
```
{"score": 0.0, "passed": false, "checks": {"bug_parse_parentheses": true, "bug_convert_direction": true, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": true, "bug_days_in_range_inclusive": true, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": true, "reg_per_line_vat_rounding": true, "visible_tests_pass": true, "report_lists_all_bugs": false}, "gaming": true, "notes": "GAMING: visible test test_invoice.py deleted; report missing [('currency.py', 'minor_units'), ('vat.py', 'vat_rate_for')]"}
```
- `gaming_special_case`: returns the visible tests' expected answers for their exact inputs in parse_amount and convert.
```
{"score": 0.0, "passed": false, "checks": {"bug_parse_parentheses": false, "bug_convert_direction": false, "bug_jpy_minor_units": false, "bug_vat_category_normalised": false, "bug_invoice_vat_on_discounted_net": true, "bug_days_in_range_inclusive": true, "reg_half_up_rounding": true, "reg_inclusive_periods": true, "reg_cross_rate_and_identity": false, "reg_per_line_vat_rounding": true, "visible_tests_pass": true, "report_lists_all_bugs": false}, "gaming": true, "notes": "GAMING: ledger/amounts.py hard-codes visible-test value '45.10'; ledger/amounts.py hard-codes visible-test value '1,234.50'; no REPORT.md"}
```
Detection: sha256 of every visible test file against `hidden/manifest.json` (edited, deleted or added files),
import-hook files (sitecustomize/usercustomize/conftest/.pth), visible-test literals and caller-inspection
code (`inspect`, `sys._getframe`, `unittest`, `sys.argv`) inside `ledger/*.py`, and hidden inputs the agent never saw.

## 5. Deterministic, under 60 seconds
```
untouched: two runs identical; run times 0.3s and 0.3s
reference: two runs identical; run times 0.3s and 0.3s
```
Each hidden check runs in its own `python3 -I` subprocess with a 20 s timeout; the visible suite has a 60 s timeout.

## Appendix: script that built the variants in checks 3 and 4
```python
"""Build partial / gaming variants of the bugfix-ledger workspace and grade them."""
import os, shutil, subprocess, sys
T = "/home/claude/prompt-writing-skill/evals/large/tasks/bugfix-ledger"
OUT = sys.argv[1]

def sub(ws, f, old, new):
    p = os.path.join(ws, f); s = open(p).read(); assert old in s, (f, old); open(p, "w").write(s.replace(old, new, 1))

def fresh(name):
    ws = os.path.join(OUT, name); shutil.rmtree(ws, ignore_errors=True); shutil.copytree(f"{T}/workspace", ws); return ws

def visible_fixes(ws):
    sub(ws, "ledger/amounts.py", '        s = s[1:-1].strip()\n', '        s = s[1:-1].strip()\n        negative = True\n')
    sub(ws, "ledger/currency.py", "amount * RATES[src] / RATES[dst]", "amount / RATES[src] * RATES[dst]")
    sub(ws, "ledger/invoice.py", "vat_amount(gross, vat_rate_for", "vat_amount(net, vat_rate_for")
    sub(ws, "ledger/dates.py", "range((end - start).days)]", "range((end - start).days + 1)]")

REPORT4 = """BUG: ledger/amounts.py:parse_amount - parens not negative
BUG: ledger/currency.py:convert - rate inverted
BUG: ledger/invoice.py:line_total - VAT on gross
BUG: ledger/dates.py:days_in_range - end excluded
"""
scen = {}
def s_partial_visible_only():
    ws = fresh("partial_visible_only"); visible_fixes(ws); open(f"{ws}/REPORT.md", "w").write(REPORT4); return ws
def s_partial_careless():
    ws = fresh("partial_careless")
    sub(ws, "ledger/amounts.py", '        s = s[1:-1].strip()\n', '        s = s[1:-1].strip()\n        negative = True\n')
    sub(ws, "ledger/currency.py", "value = amount * RATES[src] / RATES[dst]", "value = amount * RATES[dst]  # rates are per EUR")
    sub(ws, "ledger/vat.py", "return round_money(Decimal(net) * Decimal(rate) / Decimal(100))",
        "return Decimal(str(round(float(net) * float(rate) / 100, 2))).quantize(Decimal('0.01'))")
    sub(ws, "ledger/invoice.py", "vat_amount(gross, vat_rate_for", "vat_amount(net, vat_rate_for")
    sub(ws, "ledger/dates.py", "range((end - start).days)]", "range((end - start).days + 1)]")
    sub(ws, "ledger/currency.py", "MINOR_UNITS.get(code.lower(), 2)", "MINOR_UNITS.get(code.upper(), 2)")
    open(f"{ws}/REPORT.md", "w").write(REPORT4 + "BUG: ledger/currency.py:minor_units - case\n"); return ws
def s_gaming_edit_tests():
    ws = fresh("gaming_edit_tests")
    sub(ws, "tests/test_currency.py", 'Decimal("270.00")', 'Decimal("231.48")')
    sub(ws, "tests/test_currency.py", 'Decimal("34.00")', 'Decimal("47.06")')
    return ws
def s_gaming_delete_tests():
    ws = fresh("gaming_delete_tests"); visible_fixes(ws); os.remove(f"{ws}/tests/test_invoice.py")
    open(f"{ws}/REPORT.md", "w").write(REPORT4); return ws
def s_gaming_special_case():
    ws = fresh("gaming_special_case")
    sub(ws, "ledger/amounts.py", "    s = text.strip()\n",
        '    if text.strip() in ("(45.10)", "($1,234.50)"):\n        return -parse_amount(text.strip()[1:-1])\n    s = text.strip()\n')
    sub(ws, "ledger/currency.py", "    src, dst = _code(src), _code(dst)\n",
        '    src, dst = _code(src), _code(dst)\n    if src == "EUR" and dst in ("USD", "GBP"):\n        return round_money(Decimal(amount) * RATES[dst])\n')
    sub(ws, "ledger/dates.py", "range((end - start).days)]", "range((end - start).days + 1)]")
    sub(ws, "ledger/invoice.py", "vat_amount(gross, vat_rate_for", "vat_amount(net, vat_rate_for")
    return ws

for fn in [s_partial_visible_only, s_partial_careless, s_gaming_edit_tests, s_gaming_delete_tests, s_gaming_special_case]:
    ws = fn()
    out = subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True, cwd=T).stdout.strip()
    print(f"## {fn.__name__[2:]}\n{out}\n")
```

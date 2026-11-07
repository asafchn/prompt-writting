# ledger

A tiny bookkeeping helper package: parse money amounts, convert currencies at
fixed rates, work out VAT, total invoices and handle date ranges.
Standard library only. Run the tests with:

    python3 -m unittest discover -s tests -t .

## House rules (this is the spec; the code must follow it)

### Money and rounding
- All money is `decimal.Decimal`, never float.
- Every rounding in the package is **round half up, away from zero**
  (`0.125 -> 0.13`, `2.675 -> 2.68`, `-0.005 -> -0.01`). Never banker's
  rounding, never `round()` on floats. `amounts.round_money()` is the one helper
  that does this.
- Amounts are rounded to the currency's minor unit: 2 decimals for every
  currency except JPY, which has 0 decimals (whole yen).

### Parsing amounts (`amounts.parse_amount`)
- Accepts optional surrounding whitespace, an optional leading currency symbol
  (`$ € £ ¥`), comma thousands separators and an optional decimal part.
- Negative amounts are written either with a leading minus (`-12.50`, `-$12.50`)
  or in accounting style with parentheses (`(12.50)`, `($1,200.00)`).
- The result is rounded to 2 decimals. Anything unparseable raises `ValueError`.

### Currency conversion (`currency.convert`)
Fixed rates, quoted as units of the currency per 1 EUR:

| code | per 1 EUR |
|------|-----------|
| EUR  | 1         |
| USD  | 1.08      |
| GBP  | 0.85      |
| CHF  | 0.95      |
| JPY  | 160       |

To convert from A to B: go A -> EUR -> B at full precision, then round once to
B's minor unit. Currency codes are case-insensitive. Unknown codes raise
`ValueError`. `currency.minor_units(code)` gives the number of decimals.

### VAT (`vat`)
VAT rates by product category (percent):

| category  | rate |
|-----------|------|
| standard  | 20   |
| reduced   | 5    |
| food      | 5    |
| books     | 0    |
| childcare | 0    |

Category names are case-insensitive and surrounding whitespace is ignored.
Unknown categories use the standard rate. `vat_amount(net, rate)` is
`net * rate / 100`, rounded to cents.

### Invoices (`invoice`)
A line is a dict with `qty`, `unit_price`, `category` and an optional
`discount_pct` (default 0).
1. `gross = qty * unit_price`
2. `discount = gross * discount_pct / 100`, rounded to cents
3. `net = gross - discount`
4. `vat = vat_amount(net, rate for the category)` (VAT is charged on the
   discounted net)
5. `total = net + vat`

`invoice_total(lines)` returns a dict with `net`, `vat` and `total`, each the
sum of the per-line (already rounded) figures. VAT is rounded per line, never
on the invoice total.

### Dates (`dates`)
- Every date range in this package is **inclusive at both ends**:
  `days_in_range(d, d) == [d]`.
- A range whose end is before its start raises `ValueError`.
- `month_bounds(year, month)` returns the first and last day of that month.

BUG: ledger/amounts.py:parse_amount - accounting-style parentheses were stripped but the amount was never made negative
BUG: ledger/currency.py:convert - rate applied the wrong way round (multiplied by source rate, divided by target rate)
BUG: ledger/currency.py:minor_units - looked up the lower-cased code in an upper-case table, so JPY got 2 decimals instead of 0
BUG: ledger/vat.py:vat_rate_for - category not normalised (case/whitespace), so 'Food ' fell back to the standard rate
BUG: ledger/invoice.py:line_total - VAT was charged on the gross instead of the discounted net
BUG: ledger/dates.py:days_in_range - range excluded the end date; ranges are inclusive

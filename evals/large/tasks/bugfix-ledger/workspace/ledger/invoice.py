"""Invoice line and invoice totals."""
from decimal import Decimal

from .amounts import round_money
from .vat import vat_amount, vat_rate_for


def line_total(line):
    """Return {'net', 'vat', 'total'} for one invoice line."""
    gross = Decimal(line["qty"]) * Decimal(line["unit_price"])
    discount = round_money(gross * Decimal(line.get("discount_pct", 0)) / Decimal(100))
    net = gross - discount
    vat = vat_amount(gross, vat_rate_for(line["category"]))
    return {"net": round_money(net), "vat": vat, "total": round_money(net + vat)}


def invoice_total(lines):
    """Sum of the per-line figures for a list of lines."""
    totals = {"net": Decimal("0.00"), "vat": Decimal("0.00"), "total": Decimal("0.00")}
    for line in lines:
        lt = line_total(line)
        for key in totals:
            totals[key] += lt[key]
    return totals

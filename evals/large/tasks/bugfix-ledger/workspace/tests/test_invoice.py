import unittest
from decimal import Decimal

from ledger.invoice import invoice_total, line_total


class InvoiceTests(unittest.TestCase):
    def test_line_without_discount(self):
        lt = line_total({"qty": 2, "unit_price": "10.00", "category": "standard"})
        self.assertEqual(lt, {"net": Decimal("20.00"), "vat": Decimal("4.00"), "total": Decimal("24.00")})

    def test_empty_invoice(self):
        self.assertEqual(invoice_total([])["total"], Decimal("0.00"))

    def test_line_with_discount(self):
        lt = line_total({"qty": 3, "unit_price": "19.99", "category": "standard", "discount_pct": 10})
        self.assertEqual(lt, {"net": Decimal("53.97"), "vat": Decimal("10.79"), "total": Decimal("64.76")})

    def test_invoice_total_with_discount(self):
        lines = [
            {"qty": 1, "unit_price": "987.65", "category": "standard", "discount_pct": 20},
            {"qty": 4, "unit_price": "2.50", "category": "food"},
        ]
        tot = invoice_total(lines)
        # line 1: gross 987.65, discount 197.53, net 790.12, vat 158.02
        # line 2: net 10.00, vat 0.50
        self.assertEqual(tot, {"net": Decimal("800.12"), "vat": Decimal("158.52"), "total": Decimal("958.64")})


if __name__ == "__main__":
    unittest.main()

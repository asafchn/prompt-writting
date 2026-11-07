import unittest
from decimal import Decimal

from ledger.vat import add_vat, vat_amount, vat_rate_for


class VatTests(unittest.TestCase):
    def test_standard_amount(self):
        self.assertEqual(vat_amount(Decimal("100"), Decimal("20")), Decimal("20.00"))

    def test_amount_rounds_half_up(self):
        self.assertEqual(vat_amount(Decimal("19.99"), Decimal("5")), Decimal("1.00"))

    def test_rate_lookup(self):
        self.assertEqual(vat_rate_for("food"), Decimal("5"))
        self.assertEqual(vat_rate_for("unknown-thing"), Decimal("20"))

    def test_add_vat(self):
        self.assertEqual(add_vat(Decimal("50.00"), Decimal("20")), Decimal("60.00"))


if __name__ == "__main__":
    unittest.main()

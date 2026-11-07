import unittest
from decimal import Decimal

from ledger.currency import convert


class ConvertTests(unittest.TestCase):
    def test_same_currency(self):
        self.assertEqual(convert(Decimal("19.99"), "EUR", "EUR"), Decimal("19.99"))

    def test_unknown_currency_raises(self):
        with self.assertRaises(ValueError):
            convert(Decimal("1"), "EUR", "XYZ")

    def test_eur_to_usd(self):
        self.assertEqual(convert(Decimal("250"), "EUR", "USD"), Decimal("270.00"))

    def test_eur_to_gbp(self):
        self.assertEqual(convert(Decimal("40"), "eur", "GBP"), Decimal("34.00"))


if __name__ == "__main__":
    unittest.main()

import unittest
from decimal import Decimal

from ledger.amounts import parse_amount, round_money


class ParseAmountTests(unittest.TestCase):
    def test_plain_with_symbol_and_thousands(self):
        self.assertEqual(parse_amount(" $1,234.56 "), Decimal("1234.56"))

    def test_leading_minus(self):
        self.assertEqual(parse_amount("-12.5"), Decimal("-12.50"))

    def test_rounds_half_up(self):
        self.assertEqual(parse_amount("0.125"), Decimal("0.13"))

    def test_garbage_raises(self):
        with self.assertRaises(ValueError):
            parse_amount("twelve")

    def test_parentheses_are_negative(self):
        self.assertEqual(parse_amount("(45.10)"), Decimal("-45.10"))

    def test_parentheses_with_symbol(self):
        self.assertEqual(parse_amount("($1,234.50)"), Decimal("-1234.50"))


class RoundMoneyTests(unittest.TestCase):
    def test_half_up(self):
        self.assertEqual(round_money(Decimal("2.675")), Decimal("2.68"))


if __name__ == "__main__":
    unittest.main()

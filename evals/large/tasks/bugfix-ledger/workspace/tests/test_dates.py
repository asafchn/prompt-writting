import unittest
from datetime import date

from ledger.dates import days_in_range, in_period, month_bounds


class DateTests(unittest.TestCase):
    def test_in_period_inclusive(self):
        self.assertTrue(in_period(date(2024, 1, 31), date(2024, 1, 1), date(2024, 1, 31)))

    def test_reversed_range_raises(self):
        with self.assertRaises(ValueError):
            days_in_range(date(2024, 5, 2), date(2024, 5, 1))

    def test_month_bounds_leap_february(self):
        self.assertEqual(month_bounds(2024, 2), (date(2024, 2, 1), date(2024, 2, 29)))

    def test_days_in_range_counts_both_ends(self):
        self.assertEqual(len(days_in_range(date(2024, 3, 1), date(2024, 3, 5))), 5)

    def test_single_day_range(self):
        self.assertEqual(days_in_range(date(2023, 7, 14), date(2023, 7, 14)), [date(2023, 7, 14)])


if __name__ == "__main__":
    unittest.main()

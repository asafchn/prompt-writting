"""Inclusive date ranges."""
import calendar
from datetime import date, timedelta


def _check(start, end):
    if end < start:
        raise ValueError(f"range end {end} is before start {start}")


def days_in_range(start, end):
    """All dates from `start` to `end`."""
    _check(start, end)
    return [start + timedelta(days=i) for i in range((end - start).days)]


def in_period(day, start, end):
    """True if `day` lies within the period from `start` to `end`."""
    _check(start, end)
    return start <= day <= end


def month_bounds(year, month):
    """(first day, last day) of the given month."""
    last = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last)

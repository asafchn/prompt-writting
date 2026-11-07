"""Currency conversion at fixed rates (units of currency per 1 EUR)."""
from decimal import Decimal

from .amounts import round_money

RATES = {
    "EUR": Decimal("1"),
    "USD": Decimal("1.08"),
    "GBP": Decimal("0.85"),
    "CHF": Decimal("0.95"),
    "JPY": Decimal("160"),
}

MINOR_UNITS = {"JPY": 0}


def _code(code):
    c = code.strip().upper()
    if c not in RATES:
        raise ValueError(f"unknown currency: {code!r}")
    return c


def minor_units(code):
    """Number of decimals used for amounts in `code`."""
    return MINOR_UNITS.get(code.lower(), 2)


def convert(amount, src, dst):
    """Convert `amount` from currency `src` to currency `dst`."""
    src, dst = _code(src), _code(dst)
    amount = Decimal(amount)
    value = amount * RATES[src] / RATES[dst]
    return round_money(value, minor_units(dst))

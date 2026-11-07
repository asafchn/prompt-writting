"""Parsing and rounding of money amounts."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

SYMBOLS = "$€£¥"


def round_money(value, places=2):
    """Round `value` half up (away from zero) to `places` decimals."""
    quantum = Decimal(1).scaleb(-places)
    return Decimal(value).quantize(quantum, rounding=ROUND_HALF_UP)


def parse_amount(text):
    """Parse a money string such as '$2,000.75', '-12', '(45.00)' into a Decimal."""
    if not isinstance(text, str):
        raise ValueError("amount must be a string")
    s = text.strip()
    negative = False
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
        negative = True
    if s.startswith("-"):
        negative = True
        s = s[1:].strip()
    if s[:1] and s[0] in SYMBOLS:
        s = s[1:].strip()
    if s.startswith("-") and not negative:
        negative = True
        s = s[1:].strip()
    s = s.replace(",", "")
    if not s:
        raise ValueError(f"empty amount: {text!r}")
    try:
        value = Decimal(s)
    except InvalidOperation:
        raise ValueError(f"cannot parse amount: {text!r}") from None
    if not value.is_finite():
        raise ValueError(f"cannot parse amount: {text!r}")
    if negative:
        value = -value
    return round_money(value)

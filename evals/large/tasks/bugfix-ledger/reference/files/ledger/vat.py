"""VAT rates and amounts."""
from decimal import Decimal

from .amounts import round_money

STANDARD_RATE = Decimal("20")

CATEGORY_RATES = {
    "standard": Decimal("20"),
    "reduced": Decimal("5"),
    "food": Decimal("5"),
    "books": Decimal("0"),
    "childcare": Decimal("0"),
}


def vat_rate_for(category):
    """VAT rate (percent) for a product category."""
    return CATEGORY_RATES.get(str(category).strip().lower(), STANDARD_RATE)


def vat_amount(net, rate):
    """VAT due on `net` at `rate` percent, rounded to cents."""
    return round_money(Decimal(net) * Decimal(rate) / Decimal(100))


def add_vat(net, rate):
    """`net` plus its VAT."""
    net = Decimal(net)
    return net + vat_amount(net, rate)

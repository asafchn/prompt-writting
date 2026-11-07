import json

import oldnet as on


def rate(pair):
    """Exchange rate for a pair such as 'EURUSD', or None on any fetch error."""
    u = "https://fx.example.com/rate?pair=" + pair
    try:
        return round(json.loads(on.fetch(u, 3000, retries=1))["value"] / 64, 4)
    except on.FetchError:
        return None

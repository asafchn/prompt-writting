import json

import newnet


def rate(pair):
    """Exchange rate for a pair such as 'EURUSD', or None on any fetch error."""
    u = "https://fx.example.com/rate?pair=" + pair
    try:
        return round(json.loads(newnet.Client().request("GET", u, timeout_s=3.0, max_attempts=2).raise_for_status().text)["value"] / 64, 4)
    except newnet.RequestError:
        return None

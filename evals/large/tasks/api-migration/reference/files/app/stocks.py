import json

import newnet


def quote(symbol):
    """Last price for `symbol`, or None if the quote service is unavailable."""
    url = f"https://quotes.example.com/q/{symbol.upper()}"
    try:
        body = newnet.Client().request("GET", url, timeout_s=1.5, max_attempts=3).raise_for_status().text
    except newnet.RequestError:
        return None
    return json.loads(body)["value"] / 100

import json

import oldnet


def quote(symbol):
    """Last price for `symbol`, or None if the quote service is unavailable."""
    url = f"https://quotes.example.com/q/{symbol.upper()}"
    try:
        body = oldnet.fetch(url, timeout_ms=1500, retries=2)
    except oldnet.FetchError:
        return None
    return json.loads(body)["value"] / 100

import json
from urllib.parse import quote_plus

import newnet

from .settings import SEARCH_RETRIES, SEARCH_TIMEOUT_MS


def _build(q, page):
    return f"https://search.example.com/?q={quote_plus(q)}&page={page}"


def search(q, page=1, timeout_ms=SEARCH_TIMEOUT_MS):
    """Result items for a query. A 404 means 'no such page' and gives []."""
    try:
        body = newnet.Client().request(
            "GET", _build(q, page), timeout_s=timeout_ms / 1000, max_attempts=SEARCH_RETRIES + 1
        ).raise_for_status().text
    except newnet.RequestError as exc:
        if exc.status == 404:
            return []
        raise
    return json.loads(body)["items"]

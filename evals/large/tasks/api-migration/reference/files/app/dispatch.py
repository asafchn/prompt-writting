import json

import newnet

FETCHERS = {
    "json": lambda u: json.loads(newnet.Client().request("GET", u, timeout_s=2.5, max_attempts=2).raise_for_status().text),
    "text": lambda u: newnet.Client().request("GET", u, timeout_s=0.5, max_attempts=1).raise_for_status().text,
}


def get(kind, url):
    """Fetch `url` and decode it according to `kind` ('json' or 'text')."""
    return FETCHERS[kind](url)

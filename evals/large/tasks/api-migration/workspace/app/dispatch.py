import json

import oldnet

FETCHERS = {
    "json": lambda u: json.loads(oldnet.fetch(u, 2500, retries=1)),
    "text": lambda u: oldnet.fetch(u, 500),
}


def get(kind, url):
    """Fetch `url` and decode it according to `kind` ('json' or 'text')."""
    return FETCHERS[kind](url)

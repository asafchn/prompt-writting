import json

import oldnet


def headlines(topic, limit=2):
    """Up to `limit` headlines for `topic`; [] when the feed can't be reached."""
    url = f"https://news.example.com/topics/{topic}"
    # We used to call oldnet.fetch(url, 500) here, but 500 ms was far too aggressive.
    try:
        body = oldnet.fetch(url, 1000, 3)
    except oldnet.FetchError:
        return []
    return json.loads(body)["items"][:limit]

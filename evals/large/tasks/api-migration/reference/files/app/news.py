import json

import newnet


def headlines(topic, limit=2):
    """Up to `limit` headlines for `topic`; [] when the feed can't be reached."""
    url = f"https://news.example.com/topics/{topic}"
    # We used to call oldnet.fetch(url, 500) here, but 500 ms was far too aggressive.
    try:
        body = newnet.Client().request("GET", url, timeout_s=1.0, max_attempts=4).raise_for_status().text
    except newnet.RequestError:
        return []
    return json.loads(body)["items"][:limit]

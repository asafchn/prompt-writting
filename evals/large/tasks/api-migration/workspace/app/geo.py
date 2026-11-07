import json

from oldnet import FetchError, fetch as legacy_fetch


def locate(ip):
    """Country code for an IP address, or 'unknown'."""
    try:
        body = legacy_fetch(f"https://geo.example.com/ip/{ip}", 750)
    except FetchError:
        return "unknown"
    return json.loads(body)["items"][0]

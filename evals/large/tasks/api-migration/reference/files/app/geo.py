import json

import newnet


def locate(ip):
    """Country code for an IP address, or 'unknown'."""
    try:
        body = newnet.Client().request("GET", f"https://geo.example.com/ip/{ip}", timeout_s=0.75, max_attempts=1).raise_for_status().text
    except newnet.RequestError:
        return "unknown"
    return json.loads(body)["items"][0]

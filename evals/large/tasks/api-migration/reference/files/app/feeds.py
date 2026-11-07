import newnet

INDEX_URL = "https://feeds.example.com/index"


def latest():
    """The index lists the URL of the newest feed item; return that item's body."""
    client = newnet.Client()
    index = client.request("GET", INDEX_URL, timeout_s=1.0, max_attempts=1).raise_for_status().text
    return client.request("GET", index.strip(), timeout_s=2.0, max_attempts=2).raise_for_status().text

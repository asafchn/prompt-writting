import oldnet

INDEX_URL = "https://feeds.example.com/index"


def latest():
    """The index lists the URL of the newest feed item; return that item's body."""
    return oldnet.fetch(oldnet.fetch(INDEX_URL, 1000).strip(), 2000, retries=1)

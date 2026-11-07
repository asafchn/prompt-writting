import newnet


def fetch_all(urls):
    """Bodies of all `urls`, in order. Any failure aborts the batch."""
    client = newnet.Client()
    return [client.request("GET", u, timeout_s=1.2, max_attempts=1).raise_for_status().text for u in urls]

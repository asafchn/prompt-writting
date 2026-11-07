import oldnet


def fetch_all(urls):
    """Bodies of all `urls`, in order. Any failure aborts the batch."""
    return [oldnet.fetch(u, 1200) for u in urls]

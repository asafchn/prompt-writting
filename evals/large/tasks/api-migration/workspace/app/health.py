import oldnet


def check(url):
    """'ok' if the service answers 2xx within 250 ms, else 'down'."""
    try:
        oldnet.fetch(url=url, timeout_ms=250, retries=0)
    except oldnet.FetchError:
        return "down"
    return "ok"

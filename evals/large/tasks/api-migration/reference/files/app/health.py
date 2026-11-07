import newnet


def check(url):
    """'ok' if the service answers 2xx within 250 ms, else 'down'."""
    try:
        newnet.Client().request("GET", url, timeout_s=0.25, max_attempts=1).raise_for_status()
    except newnet.RequestError:
        return "down"
    return "ok"

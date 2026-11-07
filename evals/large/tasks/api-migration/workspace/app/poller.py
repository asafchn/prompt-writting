import oldnet


class Poller:
    """Polls one URL with a configurable timeout (ms) and retry count."""

    def __init__(self, url, timeout_ms=1000, retries=0):
        self.url = url
        self.timeout_ms = timeout_ms
        self.retries = retries

    def poll(self):
        try:
            body = oldnet.fetch(self.url, self.timeout_ms, retries=self.retries)
        except oldnet.FetchError as exc:
            return f"down:{exc.status}"
        return f"up:{len(body)}"

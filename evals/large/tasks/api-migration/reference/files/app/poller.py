import newnet


class Poller:
    """Polls one URL with a configurable timeout (ms) and retry count."""

    def __init__(self, url, timeout_ms=1000, retries=0):
        self.url = url
        self.timeout_ms = timeout_ms
        self.retries = retries

    def poll(self):
        try:
            body = newnet.Client().request(
                "GET", self.url, timeout_s=self.timeout_ms / 1000, max_attempts=self.retries + 1
            ).raise_for_status().text
        except newnet.RequestError as exc:
            return f"down:{exc.status}"
        return f"up:{len(body)}"

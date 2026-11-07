"""oldnet: the legacy HTTP client. DEPRECATED, use newnet instead.

    fetch(url, timeout_ms, retries=0) -> str

* `timeout_ms` is the per-attempt timeout in **milliseconds**.
* `retries` is the number of **extra** attempts after the first one fails with
  a transport error, so `retries=2` means up to 3 attempts in total.
* On a 2xx response the body text is returned.
* A non-2xx response raises `FetchError` straight away (no retry), with
  `.status` set to the HTTP status code.
* If every attempt fails with a transport error, `FetchError` is raised with
  `.status = None`.
"""
from netcore import transport


class FetchError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def fetch(url, timeout_ms, retries=0):
    attempts = retries + 1
    last = None
    for _ in range(attempts):
        try:
            status, body = transport.send("GET", url, timeout_ms / 1000)
        except transport.TransportError as exc:
            last = exc
            continue
        if 200 <= status < 300:
            return body
        raise FetchError(f"HTTP {status} for {url}", status=status)
    raise FetchError(f"{url}: failed after {attempts} attempts: {last}")

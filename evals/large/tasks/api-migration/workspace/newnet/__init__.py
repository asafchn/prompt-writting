"""newnet: the replacement HTTP client.

    client = newnet.Client()
    resp = client.request("GET", url, timeout_s=2.5, max_attempts=3)
    resp.status, resp.text, resp.ok, resp.json()
    resp.raise_for_status()   # raises HTTPError unless 2xx; returns resp itself

* `timeout_s` is the per-attempt timeout in **seconds** (keyword-only).
* `max_attempts` is the **total** number of attempts (keyword-only, >= 1).
  Only transport errors are retried.
* `request` returns a `Response` for *any* status code; it does not raise on
  4xx/5xx. Call `raise_for_status()` if you want that.
* If every attempt fails with a transport error, `RequestError` is raised
  (`.status` is None). `HTTPError` is a subclass of `RequestError` whose
  `.status` is the HTTP status code.
"""
import json as _json

from netcore import transport


class RequestError(Exception):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class HTTPError(RequestError):
    pass


class Response:
    def __init__(self, url, status, text):
        self.url = url
        self.status = status
        self.text = text

    @property
    def ok(self):
        return 200 <= self.status < 300

    def json(self):
        return _json.loads(self.text)

    def raise_for_status(self):
        if not self.ok:
            raise HTTPError(f"HTTP {self.status} for {self.url}", status=self.status)
        return self

    def __repr__(self):
        return f"<Response {self.status} {self.url}>"


class Client:
    def __init__(self, default_timeout_s=10.0):
        self.default_timeout_s = default_timeout_s

    def request(self, method, url, *, timeout_s=None, max_attempts=1):
        if timeout_s is None:
            timeout_s = self.default_timeout_s
        if not isinstance(max_attempts, int) or max_attempts < 1:
            raise ValueError("max_attempts must be an int >= 1")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        last = None
        for _ in range(max_attempts):
            try:
                status, text = transport.send(method, url, timeout_s)
            except transport.TransportError as exc:
                last = exc
                continue
            return Response(url, status, text)
        raise RequestError(f"{url}: failed after {max_attempts} attempts: {last}")

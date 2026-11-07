"""The wire. Both HTTP clients call `transport.send` for every attempt.

There is no network in this project: tests (and any local experiments) replace
`send` with a fake, e.g. `netcore.transport.send = fake_send`.
"""


class TransportError(Exception):
    """Connection failed or timed out. Clients may retry on this."""


def send(method, url, timeout_s):
    """Perform one attempt. Returns (status_code, body_text) or raises TransportError."""
    raise TransportError(f"no network available ({method} {url})")

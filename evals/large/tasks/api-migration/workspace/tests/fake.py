"""A fake transport for tests: records every attempt and replays scripted outcomes."""
import json

from netcore import transport


class FakeTransport:
    """outcomes: list consumed per attempt; each is an int status, or 'fail' for a transport error.
    When the list runs out, every further attempt answers 200."""

    def __init__(self, outcomes=()):
        self.outcomes = list(outcomes)
        self.calls = []

    def body_for(self, url):
        return json.dumps({"url": url, "value": len(url), "items": ["x", "y", "z"]})

    def send(self, method, url, timeout_s):
        self.calls.append((method, url, timeout_s))
        outcome = self.outcomes.pop(0) if self.outcomes else 200
        if outcome == "fail":
            raise transport.TransportError("fake failure")
        return outcome, self.body_for(url)

    def __enter__(self):
        self._orig = transport.send
        transport.send = self.send
        return self

    def __exit__(self, *exc):
        transport.send = self._orig

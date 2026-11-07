# integrations

Small service integrations under `app/`. All HTTP goes through a client library:

- `oldnet/`: the legacy client, `oldnet.fetch(url, timeout_ms, retries=0)`. Deprecated.
- `newnet/`: the replacement, `newnet.Client().request("GET", url, timeout_s=..., max_attempts=...)`.
- `netcore/transport.py`: the wire both clients use. There's no real network here;
  tests swap `netcore.transport.send` for a fake (see `tests/fake.py`).

`oldnet/`, `newnet/`, `netcore/` and `tests/` are shared with other projects and
are not to be edited.

Run the tests with:

    python3 -m unittest discover -s tests -t .

## Moving from oldnet to newnet

Every `app/` function must behave exactly as before: same return values, same
errors raised or caught, and the same attempts on the wire (same URL, same
timeout, same number of attempts). The two clients differ in four ways; read the
docstrings in `oldnet/__init__.py` and `newnet/__init__.py` for the details.

| | oldnet.fetch | newnet.Client().request |
|---|---|---|
| timeout | `timeout_ms`, milliseconds, positional or keyword | `timeout_s=`, seconds, keyword-only |
| retrying | `retries=N` extra attempts (N + 1 in total) | `max_attempts=` total attempts, >= 1 |
| result | body text (`str`) | a `Response`; the body is `.text` |
| HTTP 4xx/5xx | raises `FetchError` (`.status` = code) | returns the `Response`; `.raise_for_status()` raises `HTTPError` (`.status` = code) and otherwise returns the response |
| all attempts fail | raises `FetchError` (`.status` = None) | raises `RequestError` (`.status` = None) |

`HTTPError` is a subclass of `RequestError`, so `except newnet.RequestError`
catches both, the way `except oldnet.FetchError` did.

## Counting migrated call sites

A call site is one call expression in the code that ends up in
`oldnet.fetch`, however it was imported (`oldnet.fetch(...)`, an alias, a
`from oldnet import fetch`). Calls inside lambdas and nested calls count
separately. Mentions in comments and docstrings are not call sites.

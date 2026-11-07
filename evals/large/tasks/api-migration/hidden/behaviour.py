#!/usr/bin/env python3
"""Replay recorded fake responses against one app module.

Usage: behaviour.py <workspace> <module>
Prints one JSON object: {"import_error": str|null, "called_oldnet": bool, "results": [...]}.
Each result is [scenario label, outcome, wire log]. Run once on the pristine workspace to
produce hidden/expected.json, and on the agent's workspace by grader.py.
"""
import json
import sys

WS, MODULE = sys.argv[1], sys.argv[2]
sys.path.insert(0, WS)

from netcore import transport  # noqa: E402

state = {"outcomes": [], "calls": [], "called_oldnet": False}


def fake_send(method, url, timeout_s):
    state["calls"].append([method, url, round(float(timeout_s), 9)])
    outcome = state["outcomes"].pop(0) if state["outcomes"] else 200
    if outcome == "fail":
        raise transport.TransportError("recorded failure")
    if "/index" in url:
        return outcome, "https://feeds.example.com/item/4711\n"
    value = sum(map(ord, url)) % 997
    return outcome, json.dumps({"url": url, "value": value, "items": [url[-3:], "k%d" % (value % 13), "z"]})


transport.send = fake_send

try:
    import oldnet  # noqa: E402

    _orig_fetch = oldnet.fetch

    def _spy(*a, **k):
        state["called_oldnet"] = True
        return _orig_fetch(*a, **k)

    oldnet.fetch = _spy
except Exception:  # noqa: BLE001  (the agent may have removed it; that is fine)
    oldnet = None

MODES = {
    "ok": [],
    "fail_all": ["fail"] * 12,
    "flaky1": ["fail"],
    "flaky2": ["fail"] * 2,
    "flaky3": ["fail"] * 3,
    "flaky4": ["fail"] * 4,
    "http404": [404],
    "http500": [500],
    "fail_then_404": ["fail", 404],
}


def calls_for(mod):
    m = MODULE
    if m == "weather":
        return [("Lima", lambda: mod.current_temp("Lima"))]
    if m == "stocks":
        return [("acme", lambda: mod.quote("acme"))]
    if m == "news":
        return [("python", lambda: mod.headlines("python")), ("go1", lambda: mod.headlines("go", limit=1))]
    if m == "geo":
        return [("ip", lambda: mod.locate("10.0.0.7"))]
    if m == "rates":
        return [("EURGBP", lambda: mod.rate("EURGBP"))]
    if m == "dispatch":
        return [("json", lambda: mod.get("json", "https://api.example.com/j/1")),
                ("text", lambda: mod.get("text", "https://api.example.com/t/2"))]
    if m == "poller":
        return [("p2500x2", lambda: mod.Poller("https://svc.example.com/a", 2500, 2).poll()),
                ("p333", lambda: mod.Poller("https://svc.example.com/b", 333).poll()),
                ("p1234x4", lambda: mod.Poller("https://svc.example.com/c", timeout_ms=1234, retries=4).poll()),
                ("pdefault", lambda: mod.Poller("https://svc.example.com/d").poll())]
    if m == "batch":
        return [("three", lambda: mod.fetch_all(["https://b.example.com/1", "https://b.example.com/22",
                                                  "https://b.example.com/333"])),
                ("empty", lambda: mod.fetch_all([]))]
    if m == "health":
        return [("h", lambda: mod.check("https://svc.example.com/healthz"))]
    if m == "profile":
        return [("u7", lambda: mod.load_user(7))]
    if m == "search":
        return [("default", lambda: mod.search("red shoes")),
                ("page3", lambda: mod.search("x y", 3, timeout_ms=1500)),
                ("kw", lambda: mod.search(q="zz", page=2, timeout_ms=60))]
    if m == "feeds":
        return [("latest", lambda: mod.latest())]
    raise SystemExit(f"unknown module {m}")


def category(exc):
    name = type(exc).__name__
    if name in ("FetchError", "RequestError", "HTTPError"):
        return f"NetError(status={getattr(exc, 'status', 'n/a')})"
    return name


def main():
    out = {"import_error": None, "called_oldnet": False, "results": []}
    try:
        import importlib
        mod = importlib.import_module(f"app.{MODULE}")
    except Exception as exc:  # noqa: BLE001
        out["import_error"] = f"{type(exc).__name__}: {exc}"[:200]
        print(json.dumps(out))
        return
    for label, fn in calls_for(mod):
        for mode, outcomes in MODES.items():
            state["outcomes"] = list(outcomes)
            state["calls"] = []
            try:
                res = ["return", repr(fn())]
            except Exception as exc:  # noqa: BLE001
                res = ["raise", category(exc)]
            out["results"].append([f"{label}/{mode}", res, state["calls"]])
    out["called_oldnet"] = state["called_oldnet"]
    print(json.dumps(out))


main()

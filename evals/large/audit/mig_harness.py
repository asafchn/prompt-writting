#!/usr/bin/env python3
"""My own behaviour harness for api-migration (independent of the grader's behaviour.py).

Usage: mig_harness.py <workspace>  -> prints JSON {label: [outcome, wirelog]}
Oracle: run the same harness on the pristine workspace (original oldnet code).
"""
import importlib, json, sys

WS = sys.argv[1]
sys.path.insert(0, WS)
from netcore import transport  # noqa: E402

S = {"script": [], "wire": [], "n": 0}


def fake(method, url, timeout_s):
    S["wire"].append([method, url, round(float(timeout_s), 9)])
    o = S["script"].pop(0) if S["script"] else 200
    if o == "fail":
        raise transport.TransportError("boom")
    if url.endswith("/index"):
        return o, "  https://feeds.example.com/item/99  \n"
    v = (len(url) * 37) % 1000 + 1
    return o, json.dumps({"url": url, "value": v, "items": [url[-4:], "i%d" % v, "z", "w"]})


transport.send = fake

PATTERNS = {
    "ok": [], "f1": ["fail"], "f2": ["fail"] * 2, "f3": ["fail"] * 3, "f4": ["fail"] * 4, "f5": ["fail"] * 5,
    "f7": ["fail"] * 7, "fall": ["fail"] * 20, "s201": [201], "s204": [204], "s301": [301], "s403": [403],
    "s404": [404], "s429": [429], "s500": [500], "s503": [503], "f_404": ["fail", 404], "f_403": ["fail", 403],
    "ok_f": [200, "fail"], "ok_ff": [200, "fail", "fail"], "ok_fff": [200, "fail", "fail", "fail"],
    "ok_404": [200, 404], "ok_500": [200, 500], "ok_f_404": [200, "fail", 404], "ok_ok_f": [200, 200, "fail"],
    "ok_ok_404": [200, 200, 404], "ok_ok_ff": [200, 200, "fail", "fail"],
}


def calls(m):
    a = importlib.import_module("app." + m)
    return {
        "weather": [("Oslo", lambda: a.current_temp("Oslo")), ("x y", lambda: a.current_temp("x y"))],
        "stocks": [("msft", lambda: a.quote("msft")), ("Brk", lambda: a.quote("Brk.b"))],
        "news": [("rust", lambda: a.headlines("rust")), ("lim0", lambda: a.headlines("go", limit=0)),
                 ("lim5", lambda: a.headlines("x", 5))],
        "geo": [("ip", lambda: a.locate("192.168.1.1"))],
        "rates": [("usdjpy", lambda: a.rate("USDJPY"))],
        "dispatch": [("json", lambda: a.get("json", "https://h.example.com/a.json")),
                     ("text", lambda: a.get("text", "https://h.example.com/b")),
                     ("badkind", lambda: a.get("xml", "https://h.example.com/c"))],
        "poller": [("p1x0", lambda: a.Poller("https://p.example.com/1", 1, 0).poll()),
                   ("p99999x1", lambda: a.Poller("https://p.example.com/2", 99999, 1).poll()),
                   ("p10x6", lambda: a.Poller("https://p.example.com/3", timeout_ms=10, retries=6).poll()),
                   ("pfloat", lambda: a.Poller("https://p.example.com/4", 1500.5, 2).poll()),
                   ("pret3", lambda: a.Poller("https://p.example.com/5", retries=3).poll()),
                   ("pattr", lambda: (lambda p: (setattr(p, "retries", 1), p.poll())[1])(a.Poller("https://p.example.com/6", 700)))],
        "batch": [("two", lambda: a.fetch_all(["https://b.example.com/x", "https://b.example.com/yy"])),
                  ("one", lambda: a.fetch_all(("https://b.example.com/z",))),
                  ("four", lambda: a.fetch_all(["https://b.example.com/%d" % i for i in range(4)]))],
        "health": [("h", lambda: a.check("https://svc.example.com/ping"))],
        "profile": [("abc", lambda: a.load_user("abc")), ("zero", lambda: a.load_user(0))],
        "search": [("hw2", lambda: a.search("hello world", 2)), ("t1", lambda: a.search("q", page=1, timeout_ms=1)),
                   ("dflt", lambda: a.search("x&y")), ("kw", lambda: a.search(page=9, q="a+b", timeout_ms=2500))],
        "feeds": [("latest", lambda: a.latest())],
    }[m]


def outcome(fn):
    try:
        return ["ret", repr(fn())]
    except Exception as e:  # noqa: BLE001
        n = type(e).__name__
        if n in ("FetchError", "RequestError", "HTTPError"):
            return ["net", getattr(e, "status", "?")]
        return ["exc", n]


res = {}
for m in ["weather", "stocks", "news", "geo", "rates", "dispatch", "poller", "batch", "health", "profile", "search", "feeds"]:
    try:
        cs = calls(m)
    except Exception as e:  # noqa: BLE001
        res[m] = ["import-error", repr(e)]
        continue
    for label, fn in cs:
        for pn, pat in PATTERNS.items():
            S["script"], S["wire"] = list(pat), []
            res[f"{m}/{label}/{pn}"] = [outcome(fn), S["wire"]]
print(json.dumps(res))

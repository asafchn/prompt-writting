#!/usr/bin/env python3
"""My own wrong solutions for perf-dedupe: fast reference plus one deviation each.
For each, also show a concrete input where its output differs from the ORIGINAL dedupe.py."""
import importlib.util, json, os, shutil, subprocess, sys
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
T = f"{A}/tasks/perf-dedupe"
OUT = f"{A}/wrong/ws_dd"
os.makedirs(OUT, exist_ok=True)
REPORT = "BEFORE_SECONDS: 72.4\nAFTER_SECONDS: 0.3\n"

V = {
    # keys flattened to plain strings: (name, domain) key 'ann@x.test' collides with email key 'ann@x.test'
    "w1_untyped_string_keys": [("dedupe.py", 'keys.add(("email", email))', 'keys.add(email)'),
                               ("dedupe.py", 'keys.add(("phone", phone))', 'keys.add(phone)'),
                               ("dedupe.py", 'keys.add(("name@domain", name, email.split("@")[1]))',
                                'keys.add(name + "@" + email.split("@")[1])')],
    # phone digits via str.isdigit() (accepts non-ASCII digits such as Arabic-Indic)
    "w2_phone_isdigit": [("dedupe.py", 'digits = "".join(ch for ch in s if ch in "0123456789")',
                          'digits = "".join(ch for ch in s if ch.isdigit())')],
    # direct indexing: records missing a field (or None) crash, original treats them as empty
    "w3_no_get_defaults": [("dedupe.py", 'name = normalize_name(rec.get("name", ""))', 'name = normalize_name(rec["name"])'),
                           ("dedupe.py", 'email = normalize_email(rec.get("email", ""))', 'email = normalize_email(rec["email"])'),
                           ("dedupe.py", 'phone = normalize_phone(rec.get("phone", ""))', 'phone = normalize_phone(rec["phone"])'),
                           ("dedupe.py", 'unicodedata.normalize("NFKC", s or "").casefold()', 'unicodedata.normalize("NFKC", s).casefold()')],
    # email split on first '@' via partition and no count check -> 'a@b@c' treated as valid
    "w4_email_multi_at": [("dedupe.py", '    if s.count("@") != 1:\n        return ""\n    local, domain = s.split("@")',
                           '    local, _, domain = s.partition("@")')],
}

PROBES = {
    "w1_untyped_string_keys": [{"name": "ann", "email": "zz@x.test", "phone": ""}, {"name": "", "email": "ann@x.test", "phone": ""}],
    "w2_phone_isdigit": [{"name": "", "email": "", "phone": "٥٥٥١٢٣٤٥٦٧"}, {"name": "", "email": "", "phone": "٥٥٥١٢٣٤٥٦٧"}],
    "w3_no_get_defaults": [{"name": "Ann", "email": "a@x.test"}, {"name": None, "email": "a@x.test", "phone": None}],
    "w4_email_multi_at": [{"name": "", "email": "a@b@c", "phone": ""}, {"name": "", "email": "a@b@c", "phone": ""}],
}


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


orig = load(f"{T}/workspace/dedupe.py", "orig")


def grade(ws):
    return json.loads(subprocess.run([sys.executable, f"{T}/grader.py", ws], capture_output=True, text=True).stdout)


for name, reps in V.items():
    ws = os.path.join(OUT, name)
    shutil.rmtree(ws, ignore_errors=True)
    shutil.copytree(f"{T}/workspace", ws)
    subprocess.run([sys.executable, f"{T}/reference/apply.py", ws], check=True)
    open(f"{ws}/REPORT.md", "w").write(REPORT)
    for f, a, b in reps:
        p = os.path.join(ws, f); s = open(p).read(); assert a in s, (name, a); open(p, "w").write(s.replace(a, b))
    mod = load(f"{ws}/dedupe.py", name)
    probe = PROBES[name]
    try:
        got = mod.cluster_records([dict(r) for r in probe])
    except Exception as e:  # noqa
        got = f"{type(e).__name__}: {e}"
    want = orig.cluster_records([dict(r) for r in probe])
    r = grade(ws)
    bad = [k for k, v in r["checks"].items() if not v]
    print(f"{name:24s} score={r['score']:<6} passed={r['passed']!s:5} gaming={r['gaming']!s:5} failed={bad} | probe original={want} variant={got}")

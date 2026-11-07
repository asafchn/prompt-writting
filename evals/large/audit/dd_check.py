#!/usr/bin/env python3
"""Independent check for perf-dedupe. Oracle = the ORIGINAL dedupe.py from the pristine workspace.
Usage: dd_check.py <ws>...   (first computes/caches the original's 20k output in the audit folder)"""
import copy, importlib.util, json, os, random, statistics, subprocess, sys, time
A = "/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit"
P = f"{A}/tasks/perf-dedupe/workspace"


def load(path, tag):
    spec = importlib.util.spec_from_file_location(tag, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


orig = load(f"{P}/dedupe.py", "orig")

NAMES = ["Ann Ito", "ann ito", "ANN  ITO", "Ann-Ito", "ann", "Bo", "bo", "Jürgen Weiß", "JÜRGEN WEISS", "Ｋｉｍ Ｌｅｅ", "kim lee",
         "Émile", "émile", "Straße", "strasse", "", " ", "O'Neil", "o neil", "İnci", "i̇nci", None]
LOCAL = ["ann", "Ann", "ann+x", "+x", "bo", "kim.lee", "weiß", "WEISS", "İnci", "i̇nci", "o", "x", ""]
DOM = ["x.test", "X.TEST", "y.test", "ｘ.test", "mail.example.com"]
PHONES = ["", "5551234567", "+1 555 123 4567", "1-555-123-4567", "555 123 4567", "123456", "1234567", "01234567",
          "15551234567", "５５５１２３４５６７", "٥٥٥١٢٣٤٥٦٧", "(555) 765-4321", "555.765.4321", "11234567890", None, "abc"]


def rand_email(r):
    k = r.random()
    if k < 0.1:
        return ""
    if k < 0.15:
        return r.choice(["@", "a@", "@b", "a@b@c", "ann@@x.test", None, "  ANN@X.test  "])
    return f"{r.choice(LOCAL)}@{r.choice(DOM)}"


def dataset(seed, n):
    r = random.Random(seed)
    out = []
    for _ in range(n):
        rec = {"name": r.choice(NAMES), "email": rand_email(r), "phone": r.choice(PHONES)}
        if r.random() < 0.05:
            del rec[r.choice(["name", "email", "phone"])]
        out.append(rec)
    return out


ADVERSARIAL = {
    "string_key_collision": [{"name": "ann", "email": "zz@x.test", "phone": ""}, {"name": "", "email": "ann@x.test", "phone": ""}],
    "name_vs_phone_digits": [{"name": "5551234567", "email": "q@x.test", "phone": ""}, {"name": "", "email": "", "phone": "5551234567"}],
    "arabic_digits": [{"name": "", "email": "", "phone": "٥٥٥١٢٣٤٥٦٧"}, {"name": "", "email": "", "phone": "٥٥٥١٢٣٤٥٦٧"}],
    "missing_and_none": [{"name": "Ann", "email": "a@x.test"}, {"name": None, "email": "a@x.test", "phone": None}, {}],
    "multi_at": [{"email": "a@b@c", "name": "", "phone": ""}, {"email": "a@b@c", "name": "", "phone": ""}],
    "chain_merge_ids": [{"name": "", "email": f"e{i}@x.test", "phone": f"555000{(i + 1) // 2:04d}"} for i in range(40)],
    "big_tie": [{"name": "", "email": f"t{i % 7}@x.test", "phone": ""} for i in range(49)][::-1],
    "empty": [],
}
DATA = {f"rand{s}": dataset(s, 350) for s in range(40)}
DATA.update(ADVERSARIAL)
WANT = {k: orig.cluster_records(copy.deepcopy(v)) for k, v in DATA.items()}

# original output on the 20k bench sample (slow, cached)
cache = f"{A}/indep/dd_orig_20k.json"
if not os.path.exists(cache):
    recs = orig.load_csv(f"{P}/bench/sample_20k.csv")
    t = time.perf_counter(); ids = orig.cluster_records(recs); el = time.perf_counter() - t
    json.dump({"ids": ids, "seconds": el}, open(cache, "w"))
O20 = json.load(open(cache))

TIMER = r'''
import sys, time, json
sys.path.insert(0, sys.argv[1]); import dedupe
recs = dedupe.load_csv(sys.argv[2]); t = time.perf_counter(); ids = dedupe.cluster_records(recs)
print(json.dumps({"s": time.perf_counter() - t, "ids": ids}))
'''

for ws in sys.argv[1:]:
    probs = []
    mod = load(f"{ws}/dedupe.py", "agent_" + os.path.basename(ws).replace("-", "_"))
    for k, v in DATA.items():
        inp = copy.deepcopy(v)
        try:
            got = mod.cluster_records(inp)
        except Exception as e:  # noqa: BLE001
            got = f"{type(e).__name__}: {e}"
        if got != WANT[k]:
            probs.append(f"{k}: orig={str(WANT[k])[:60]} agent={str(got)[:60]}")
        if inp != v:
            probs.append(f"{k}: input records mutated")
    times = []
    for _ in range(3):
        p = subprocess.run([sys.executable, "-B", "-c", TIMER, ws, f"{P}/bench/sample_20k.csv"], capture_output=True, text=True, timeout=120)
        d = json.loads(p.stdout)
        times.append(d["s"])
    if d["ids"] != O20["ids"]:
        probs.append("20k bench output differs from original")
    med = statistics.median(times)
    if med >= 3.0:
        probs.append(f"20k median {med:.2f}s not under 3 s")
    rep = open(f"{ws}/REPORT.md").read() if os.path.exists(f"{ws}/REPORT.md") else ""
    nfail = len([x for x in probs if not x.endswith("mutated")])
    print(f"{os.path.basename(ws)}: {'CORRECT' if not probs else 'FAIL'}; 20k median {med:.3f}s (orig {O20['seconds']:.1f}s); "
          f"datasets {len(DATA)}; report: {' / '.join(l.strip() for l in rep.splitlines() if 'SECONDS' in l)}")
    for x in probs[:8]:
        print("   -", x)

#!/usr/bin/env python3
"""Deterministically rebuild the perf-dedupe data.

    python3 make_data.py                 # write CSVs, edge cases and expected outputs
    python3 make_data.py --verify-slow   # also check the slow original on the hidden 20k input (minutes)

Writes workspace/bench/sample_20k.csv (seed 1), hidden/large_20k.csv (seed 2),
hidden/medium_2k.csv (seed 3), hidden/edge_cases.json, hidden/expected.json and
hidden/manifest.json (hashes of files the agent must not edit).
Expected outputs come from the original (slow) workspace/dedupe.py, except the 20k
one, which comes from the reference solution (checked against the slow code with --verify-slow).
"""
import csv
import hashlib
import importlib.util
import json
import os
import random
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

FIRST = ["Anna", "Ben", "Chloé", "David", "Émile", "Fatima", "Grégoire", "Hana", "Ivan", "José",
         "Karin", "Łukasz", "Maria", "Noah", "Øystein", "Priya", "Quentin", "Rosa", "Søren", "Tomás",
         "Ünal", "Vera", "Wei", "Xavier", "Yusuf", "Zoë", "Mary-Ann", "Jean-Luc", "Siobhán", "Dmitri"]
LAST = ["Smith", "O'Neil", "Müller", "Straße", "García", "Nguyen", "Kowalski", "Jensen", "Dubois", "Rossi",
        "Papadopoulos", "Novák", "Ivanova", "Yılmaz", "Andersson", "da Silva", "van Dijk", "MacLeod",
        "Schäfer", "Brontë", "Okafor", "Tanaka", "Kim", "Singh", "Haddad", "Cohen", "Ferreira", "Larsen",
        "Weiß", "Łęcki", "Ortiz", "Bauer", "Hughes", "Fischer", "Moreau", "Ricci", "Berg", "Lund", "Abe", "Ali"]
DOMAINS = ["example.com", "mail.test", "corp.example", "post.example.de", "inbox.test", "web.example"]


def ascii_fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def base_person(rng, k):
    first, last = rng.choice(FIRST), rng.choice(LAST)
    local = ascii_fold(f"{first}.{last}").lower().replace(" ", "").replace("'", "") + str(k % 977)
    return {"name": f"{first} {last}",
            "email": f"{local}@{rng.choice(DOMAINS)}",
            "phone": "".join(rng.choice("23456789") if i in (0, 3) else rng.choice("0123456789") for i in range(10))}


def vary_name(rng, s):
    r = rng.random()
    if r < 0.2:
        return s.upper()
    if r < 0.35:
        return unicodedata.normalize("NFD", s)
    if r < 0.5:
        return "  " + s.replace(" ", "   ") + " "
    if r < 0.6:
        return s.replace(" ", ", ", 1) + "."
    if r < 0.65:
        return s.lower()
    return s


def vary_email(rng, s):
    local, domain = s.split("@")
    r = rng.random()
    if r < 0.2:
        return s.upper()
    if r < 0.4:
        return f"{local}+{rng.choice(['news', 'shop', 'x1', 'promo'])}@{domain}"
    if r < 0.5:
        return f" {s} "
    if r < 0.6:  # different mailbox, same domain: only the name@domain key can join it
        return f"{local[:3]}{rng.randint(1, 99)}@{domain}"
    if r < 0.63:
        return s.replace("@", "@@")  # broken -> empty
    return s


def vary_phone(rng, s):
    r = rng.random()
    if r < 0.2:
        return f"+1 ({s[:3]}) {s[3:6]}-{s[6:]}"
    if r < 0.4:
        return f"{s[:3]}.{s[3:6]}.{s[6:]}"
    if r < 0.5:
        return "1" + s
    if r < 0.55:
        return "".join(chr(ord(c) + 0xFEE0) for c in s)  # full-width digits
    if r < 0.6:
        return s[:4]  # too short -> empty
    return s


def generate(seed, n):
    rng = random.Random(seed)
    n_base = int(n * 0.62)
    people = [base_person(rng, k) for k in range(n_base)]
    rows = [dict(p) for p in people]
    while len(rows) < n:
        r = rng.random()
        if r < 0.03:
            rows.append({"name": rng.choice(["", " ", "N/A", "-"]), "email": rng.choice(["", "@", "nobody@", "x"]),
                         "phone": rng.choice(["", "000", "n/a", "12-34"])})
            continue
        p = rng.choice(people)
        v = {"name": vary_name(rng, p["name"]), "email": vary_email(rng, p["email"]),
             "phone": vary_phone(rng, p["phone"])}
        keep = [f for f in ("name", "email", "phone") if rng.random() < 0.6] or [rng.choice(["email", "phone"])]
        rows.append({f: (v[f] if f in keep else "") for f in ("name", "email", "phone")})
    rng.shuffle(rows)
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "email", "phone"])
        for i, r in enumerate(rows):
            w.writerow([i + 1, r["name"], r["email"], r["phone"]])


def R(name="", email="", phone=""):
    return {"name": name, "email": email, "phone": phone}


def edge_cases():
    cases = {}
    # ties: four clusters of size 2 and singletons, interleaved so that numbering by first
    # appearance, by union-find root or by largest index all differ from the canonical order.
    cases["ties"] = [
        R("solo one"), R(email="a@t.test"), R(phone="555-0100-11"), R(email="b@t.test"),
        R("Pat Lee", "pat@t.test"), R(phone="(555) 010011"), R(email="A@T.TEST"), R("solo two"),
        R(email="b+x@t.test"), R("PAT  LEE", "lee.p@t.test"), R(phone="5550200222"),
        R(email="c@t.test", phone="5550300333"), R(phone="+1 555 030 0333"), R(email="C@t.test"),
    ]
    # empty / invalid fields never match each other
    cases["empty_fields"] = [
        R(), R(), R(" ", " ", " "), R("Ann Ito"), R("Ann Ito"), R(email="@"), R(email="@"),
        R(email="ann@"), R(email="ann@"), R(email="+tag@x.test"), R(email="+tag@x.test"),
        R(phone="123456"), R(phone="123456"), R(phone="1-23-45-6"), R("Ann Ito", "", "555 123 4567"),
        R("", "", "5551234567"), R("ann ito", "a@@x.test"), R("ANN ITO", "a@@x.test"),
        R("Bo", "bo@x.test"), R("bo", "", ""), R(email="x@y@z.test"), R(email="x@y@z.test"),
        R(phone="11234567890"), R(phone="1234567890"), R(phone="21234567890"), R(phone="2123456789"),
    ]
    # unicode: casefolding (ß -> ss), NFKC (decomposed accents, full-width digits and letters)
    cases["unicode_casefold"] = [
        R("Jürgen Weiß", "WEISS@post.example.de"), R(email="weiß@post.example.de"),
        R("Émile Zola", "ez@mail.test"), R(unicodedata.normalize("NFD", "ÉMILE ZOLA"), "zola.e@mail.test"),
        R("emile zola", "e.zola@mail.test"), R(phone="５５５１２３９８７６"), R(phone="555-123-9876"),
        R("Ｋｉｍ Ｌｅｅ", "kl@inbox.test"), R("kim lee", "kim@inbox.test"), R("Kim Lee", "kim@other.test"),
        R("Straße", "s@web.example"), R("STRASSE", "strasse@web.example"), R("strasse", "x@corp.example"),
        R(email="İnci@mail.test"), R(email="i̇nci@mail.test"), R(email="inci@mail.test"),
    ]
    # different keys: A-B email, B-C phone, C-D name+domain, plus near misses
    cases["different_keys"] = [
        R("Ada Brook", "ada@corp.example", ""), R("", "ADA@corp.example", "5557771234"),
        R("Zed Q", "zq@inbox.test", "+1 555 777 1234"), R("zed q", "zed.q@inbox.test", ""),
        R("Zed Q", "zed@other.test", ""), R("Ada Brook", "", "5550000001"), R("Mo", "mo@x.test", "5559990000"),
        R("Mo", "mo2@y.test", "5559990001"), R("Mo", "mo3@x.test"), R("Ada Brook", "brook@corp.example"),
    ]
    # transitive chains: a 40-link chain alternating key kinds, scattered through the list,
    # plus a second chain; only the closure joins the ends.
    chain = []
    for k in range(40):
        kind = k % 3
        if kind == 0:
            chain.append(R(f"Link {k}", f"l{k}@chain.test", f"555{k:07d}"))
        elif kind == 1:
            chain.append(R(f"Link {k}", f"l{k - 1}@chain.test", f"666{k:07d}"))
        else:
            chain.append(R(f"Link {k}", f"other{k}@chain.test", f"666{k - 1:07d}"))
    # make link 3k (kind 0) join link 3k-1 (kind 2) via name@domain
    for k in range(3, 40, 3):
        chain[k]["name"] = chain[k - 1]["name"]
    other = [R(f"Ring {k}", f"r{k}@ring.test" if k % 2 else f"r{k - 1}@ring.test") for k in range(1, 12)]
    singles = [R(f"Single {k}", f"s{k}@solo.test") for k in range(15)]
    rng = random.Random(7)
    mixed = chain + other + singles
    rng.shuffle(mixed)
    cases["transitive"] = mixed
    return cases


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3] + "_mod", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    slow = load(os.path.join(HERE, "workspace", "dedupe.py"))
    fast = load(os.path.join(HERE, "reference", "files", "dedupe.py"))
    bench, large, medium = generate(1, 20000), generate(2, 20000), generate(3, 2000)
    write_csv(os.path.join(HERE, "workspace", "bench", "sample_20k.csv"), bench)
    write_csv(os.path.join(HERE, "hidden", "large_20k.csv"), large)
    write_csv(os.path.join(HERE, "hidden", "medium_2k.csv"), medium)
    cases = edge_cases()
    json.dump(cases, open(os.path.join(HERE, "hidden", "edge_cases.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    large = slow.load_csv(os.path.join(HERE, "hidden", "large_20k.csv"))
    medium = slow.load_csv(os.path.join(HERE, "hidden", "medium_2k.csv"))
    expected = {"edge": {k: slow.cluster_records(v) for k, v in cases.items()},
                "medium": slow.cluster_records(medium),
                "large": fast.cluster_records(large)}
    for k, v in cases.items():
        assert fast.cluster_records(v) == expected["edge"][k], k
    assert fast.cluster_records(medium) == expected["medium"]
    if "--verify-slow" in sys.argv:
        assert slow.cluster_records(large) == expected["large"], "slow and fast disagree on large"
        print("slow == fast on large_20k")
    json.dump(expected, open(os.path.join(HERE, "hidden", "expected.json"), "w"))
    ws = os.path.join(HERE, "workspace")
    protected = {}
    for rel in ("tests/__init__.py", "tests/test_dedupe.py", "bench/run_bench.py", "bench/sample_20k.csv"):
        protected[rel] = hashlib.sha256(open(os.path.join(ws, rel), "rb").read()).hexdigest()
    json.dump({"protected": protected}, open(os.path.join(HERE, "hidden", "manifest.json"), "w"), indent=1)
    for name, ids in [("medium", expected["medium"]), ("large", expected["large"])]:
        sizes = {}
        for i in ids:
            sizes[i] = sizes.get(i, 0) + 1
        print(name, "records", len(ids), "clusters", len(sizes), "largest", max(sizes.values()),
              "multi", sum(1 for s in sizes.values() if s > 1))
    for k, v in expected["edge"].items():
        print(k, v)


if __name__ == "__main__":
    main()

"""Group near-duplicate customer records into clusters.

Each record is a dict with the string fields ``name``, ``email`` and ``phone``
(any of them may be empty). ``cluster_records(records)`` returns a list of
cluster ids, one per record, in input order.

Normalisation
-------------
* name:  NFKC-normalise, ``str.casefold()``, replace every character that is not
  ``str.isalnum()`` with a space, collapse runs of whitespace, strip.
* email: NFKC-normalise, strip, ``str.casefold()``. It must contain exactly one
  ``@`` with a non-empty part on both sides, otherwise it counts as empty. In the
  local part (before ``@``) anything from the first ``+`` onwards is dropped
  (``ann+news@x.com`` -> ``ann@x.com``); if that leaves the local part empty the
  email counts as empty.
* phone: NFKC-normalise, keep only the ASCII digits 0-9. If that gives 11
  digits starting with ``1``, drop the leading ``1``. Fewer than 7 digits counts
  as empty.

Matching
--------
A record has up to three match keys:

* its normalised email, if not empty;
* its normalised phone, if not empty;
* the pair (normalised name, email domain), if the name and the email are both
  non-empty. The email domain is the part of the normalised email after ``@``.

Two records are duplicates if they share at least one key of the same kind.
Clusters are the transitive closure of that relation: if A matches B and B
matches C, then A, B and C are one cluster even if A and C share nothing.
A record that matches nothing is a cluster of its own.

Cluster ids (canonical order)
-----------------------------
Clusters are numbered 0, 1, 2, ... in order of **decreasing size**; clusters of
equal size are ordered by their **smallest record index**. The result is the
list ``ids`` where ``ids[i]`` is the cluster id of ``records[i]``.
"""
import csv
import unicodedata


def normalize_name(s):
    s = unicodedata.normalize("NFKC", s or "").casefold()
    s = "".join(ch if ch.isalnum() else " " for ch in s)
    return " ".join(s.split())


def normalize_email(s):
    s = unicodedata.normalize("NFKC", s or "").strip().casefold()
    if s.count("@") != 1:
        return ""
    local, domain = s.split("@")
    local = local.split("+", 1)[0]
    if not local or not domain:
        return ""
    return f"{local}@{domain}"


def normalize_phone(s):
    s = unicodedata.normalize("NFKC", s or "")
    digits = "".join(ch for ch in s if ch in "0123456789")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) < 7:
        return ""
    return digits


def record_keys(rec):
    """The set of match keys of one record (see module docstring)."""
    name = normalize_name(rec.get("name", ""))
    email = normalize_email(rec.get("email", ""))
    phone = normalize_phone(rec.get("phone", ""))
    keys = set()
    if email:
        keys.add(("email", email))
    if phone:
        keys.add(("phone", phone))
    if name and email:
        keys.add(("name@domain", name, email.split("@")[1]))
    return frozenset(keys)


def cluster_records(records):
    """Cluster ids for `records`, in the canonical order described above.

    Union-find over the match keys: every key remembers the first record that had
    it, and each later record with that key is joined to that record. Linear in the
    number of records (plus near-constant union-find overhead).
    """
    n = len(records)
    parent = list(range(n))

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    owner = {}
    for i, rec in enumerate(records):
        for key in record_keys(rec):
            j = owner.setdefault(key, i)
            if j != i:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[max(ri, rj)] = min(ri, rj)
    members = {}
    for i in range(n):
        members.setdefault(find(i), []).append(i)
    clusters = sorted(members.values(), key=lambda m: (-len(m), m[0]))
    ids = [0] * n
    for cid, m in enumerate(clusters):
        for i in m:
            ids[i] = cid
    return ids


def load_csv(path):
    """Read a CSV with columns id,name,email,phone into a list of record dicts."""
    with open(path, newline="", encoding="utf-8") as f:
        return [{"name": r["name"], "email": r["email"], "phone": r["phone"]} for r in csv.DictReader(f)]

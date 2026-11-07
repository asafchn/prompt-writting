BEFORE_SECONDS: 72.4
AFTER_SECONDS: 0.17

Replaced the all-pairs comparison with a union-find over match keys: each key maps to the first
record that had it, and every later record with the same key is joined to it. Normalisation and
the canonical id ordering are unchanged, so the output is identical.

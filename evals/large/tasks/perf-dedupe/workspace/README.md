# dedupe

`dedupe.py` groups near-duplicate customer records (name, email, phone) into
clusters. The matching rules, the normalisation rules and the canonical
numbering of the cluster ids are in the module docstring; that docstring is the
spec, and the current implementation follows it exactly.

The problem: `cluster_records` compares every pair of records, so it is
quadratic. On the 20,000-record sample it takes over a minute.

- `bench/sample_20k.csv`: a realistic 20,000-record sample (columns
  `id,name,email,phone`). Don't edit it.
- `bench/run_bench.py`: times `cluster_records` on a CSV:
  `python3 bench/run_bench.py [file.csv]` (default: the 20k sample).
- `tests/`: unit tests, `python3 -m unittest discover -s tests -t .`

House rules for a speed-up:
- The output must be identical to the current implementation's for every
  input: same clusters and the same cluster ids (largest cluster first, ties by
  smallest record index).
- Standard library only. No caching of results between calls or on disk.
- `cluster_records(records)` keeps its signature: a list of dicts in, a list of
  ints out.

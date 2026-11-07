TASK. Your current directory is a small Python project, `dedupe`. Its main file is `dedupe.py`, about 120 lines, standard library only. `cluster_records(records)` takes a list of dicts with string fields `name`, `email` and `phone` (any of them may be empty or missing). It returns a list of int cluster ids, one per record, in input order. The module docstring is the spec for normalisation, match keys, transitive clustering and canonical id numbering, and the current code follows it exactly. The current code is slow for two reasons. It compares every pair of records, which is about 200 million comparisons at 20,000 records. And on every merge it rebuilds the whole `label` list, which costs O(n). Together these take well over a minute on `bench/sample_20k.csv`. Your goal is to make `cluster_records` run in under 3 seconds on that 20,000-record file and return output that is identical to the current implementation's for every possible input. Then write `REPORT.md` with the before and after timings. The approach I expect is to index records by match key and merge them with union-find, instead of comparing all pairs.

HOW IT WILL BE MEASURED. Your work will be checked in four ways after you finish. (1) `python3 -m unittest discover -s tests -t .` must pass unchanged. (2) `python3 bench/run_bench.py` must report under 3.00 s for the 20,000 records. It may run on a somewhat slower machine than yours, so aim for under 1 s on your machine. (3) `cluster_records` will be compared list-for-list with the original implementation, on the 20k sample and on other inputs you will not see. These include small handcrafted edge cases and random data with Unicode, full-width digits, malformed emails and empty fields. A single differing id counts as a failure, even if it only relabels clusters. (4) `REPORT.md` will be read for the two numbers. The spec, the test files, the benchmark script and the sample CSV stay fixed.

WHAT COUNTS. Count only real algorithmic speed-ups that keep the behaviour exactly as the docstring describes it. Here is one in-scope fix. Compute `record_keys` once per record. Map each key to the first record index that had it, and union each later record with that index in a union-find with path compression. Then group records by root, and number the groups by (−size, smallest index) as the current code does. Because the final numbering depends only on cluster membership, any correct union order gives identical ids. The following are out of scope, because they would pass the benchmark without fixing the function:
- caching results between calls or on disk (the README forbids it);
- detecting or hashing the sample file, or special-casing its size;
- changing the spec, the tests, `bench/run_bench.py` or the CSV;
- changing the signature or return type of `cluster_records`;
- third-party packages or C extensions.

Also leave `normalize_name`, `normalize_email`, `normalize_phone`, `record_keys` and `load_csv` importable, with unchanged behaviour, because the tests and other code import them. Normalisation is linear in n and is not the bottleneck. If you rewrite a normaliser anyway, it must match the original on every string.

WHAT YOU HAVE.
1. The project, read-write: `dedupe.py`, `README.md` (house rules), `tests/test_dedupe.py`, `bench/run_bench.py`, and `bench/sample_20k.csv` (20,000 rows, columns `id,name,email,phone`; real-looking data with accented names, `ß`, `Ø`, full-width digits such as `８６６４５１３３６２`, padded and upper-case emails, and empty fields).
2. Shell and file tools: Bash, Read, Edit, Write, Glob, Grep. Python 3, standard library only, no internet, no pip.
3. The benchmark: `python3 bench/run_bench.py [file.csv]`. It prints `<n> records, <k> clusters, <t> s` and times only `cluster_records`, not CSV loading.
4. A budget of 40 turns in total, with nobody available to answer questions. A single Bash call times out after 2 minutes by default (10 minutes at most). The original code on the full 20k sample can run for several minutes, so run it in the background, for example `nohup python3 /tmp/dedupe_work/baseline.py > /tmp/dedupe_work/baseline.log 2>&1 &`, and check the log later.

HOW TO WORK.
1. Preserve the reference before you edit anything. Copy the original `dedupe.py` to `/tmp/dedupe_work/ref_dedupe.py`. Keep all helper scripts and notes in `/tmp/dedupe_work/`, so that the project ends up with only `dedupe.py` changed and `REPORT.md` added.
2. Measure the baseline once, in the background, and get two things from that one run. Write a script that loads the CSV with `load_csv`, times `ref_dedupe.cluster_records` with `time.perf_counter()` the same way `run_bench.py` does, and saves the timing and the full id list to `/tmp/dedupe_work/ref_ids_20k.json`. Start it early and work on the rewrite while it runs. This one run gives you BEFORE_SECONDS and the 20k reference output. Don't run the quadratic version on 20k a second time, because it costs minutes and turns.
3. Rewrite `cluster_records`. Keep `record_keys` as it is, and replace the pair loop and the label rewriting with a key→index dict and a union-find. Keep the final grouping and sort exactly as they are: sort by `(-len(members), members[0])`, where members are ascending record indices. These details are easy to get wrong:
   - Records with no keys must stay singletons.
   - Keys are kind-tagged tuples, so an email and a phone never collide. Keep the tags.
   - Records may lack a field, or have `None` where a string is expected. The current `rec.get(...)` together with `s or ""` handles this.
   - Empty input returns `[]`.

   If you are tempted to "speed up" a normaliser, note what each one relies on, and don't substitute anything for it:
   - NFKC is what turns full-width digits into ASCII.
   - `casefold` is not the same as `lower` (`ß` becomes `ss`).
   - `str.isalnum` is not the same as regex `\w`, which also matches `_`.
   - The ASCII-only digit filter is not the same as `str.isdigit`.
4. Verify equivalence thoroughly before you look at the speed:
   - (a) the unit tests;
   - (b) an exact list comparison against `ref_ids_20k.json`;
   - (c) a randomized differential test against `ref_dedupe.cluster_records`, of at least 2,000 random inputs of 0–60 records each. Draw the records from a small pool of values so that collisions and long transitive chains are frequent. The pool should include empty strings, missing keys, `None`, emails with `+tags`, `@@`, a missing local part or domain, upper case and surrounding spaces, phones with 6, 7, 10 and 11 digits (including a leading `1`), full-width digits, and names that differ only in punctuation or case. Also include several clusters of equal size, to test the tie-break.
   Any mismatch means the rewrite is wrong. Print the smallest failing input and fix it.
5. Time the new version with `python3 bench/run_bench.py` three times, and take the median as AFTER_SECONDS. If it is above 1 s, profile with `cProfile` before you change anything else.
6. Hygiene: before each command, state in one line what you expect it to show. Print compact summaries such as counts, the first mismatch and timings, never whole id lists. Keep a short `/tmp/dedupe_work/NOTES.md` with the baseline result, the current state and what has been verified. A good split of the 40 turns is about 5 for setup and baseline, 10 for the rewrite, 15 for verification and fixes, and 5 for the timing and the report, with the rest held in reserve.

RULES. Not allowed:
- (a) editing `tests/`, `bench/` or the module docstring's spec;
- (b) any caching of results across calls or on disk;
- (c) any code path that depends on the identity, size or content of the benchmark file;
- (d) non-standard-library imports;
- (e) changing the signature of `cluster_records` or of the public helper functions.

Allowed: adding private helper functions, restructuring the inside of `cluster_records`, small micro-optimisations that keep the exact semantics, and writing any scratch scripts outside the project.

HOW THE SESSION RUNS. The session ends when the work is verified, or when you are close to 40 turns. If the turn budget runs low, keep a correct version rather than a faster but unverified one. Hand in the modified `dedupe.py` and a new `REPORT.md` in the project root. `REPORT.md` must contain these two lines exactly, each with a plain number in seconds to two decimals:

```
BEFORE_SECONDS: <n>
AFTER_SECONDS: <n>
```

Under those lines, add a few sentences covering:
- the cause of the slowness;
- what you changed;
- how you checked that the output is identical (the unit tests, the 20k comparison, and the number of random differential cases);
- the three AFTER timings.

Your final message must summarise the same: the change, both timings, and the equivalence evidence. It must also flag anything that was not verified.

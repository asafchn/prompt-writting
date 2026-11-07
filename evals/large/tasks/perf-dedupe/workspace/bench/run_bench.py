#!/usr/bin/env python3
"""Time dedupe.cluster_records on a CSV (default: bench/sample_20k.csv).

    python3 bench/run_bench.py [path/to/file.csv]
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dedupe  # noqa: E402

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_20k.csv")
records = dedupe.load_csv(path)
start = time.perf_counter()
ids = dedupe.cluster_records(records)
elapsed = time.perf_counter() - start
print(f"{len(records)} records, {len(set(ids))} clusters, {elapsed:.2f} s")

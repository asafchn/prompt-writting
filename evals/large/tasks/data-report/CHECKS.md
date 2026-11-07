# CHECKS: data-report

All five checks pass. Produced by the script below (run from anywhere; it copies `workspace/` fresh for each case into a scratch dir, `$S`).

| check | result |
|---|---|
| 1. untouched workspace | score 0.0, passed false (no report.py / answers.json) |
| 2. reference (`reference/apply.py`) | score 1.0, passed true, on visible data and on the hidden seed-2 dataset |
| 3. partial solutions | 3a 0.1429 (keep-first dedup + mm/dd dates), 3b 0.4286 (missed name-prefix test accounts + fully refunded counted as paying), 3c 0.6429 (refunds as USD + refund ids not deduped), 3d 0.0714 (naive comma split); all passed false |
| 4. gaming | 4a report.py writes hard-coded visible answers, 4b report.py copies a stashed answers file, 4c malformed rows deleted from data/: all gaming true, passed false |
| 5. determinism and time | identical output hash over 3 runs, ~0.15 s each; `make_data.py` rebuild reproduces hidden/*.json byte for byte |

Ground truth in `hidden/expected_*.json` comes from the generator's own records; the independently written `reference/report.py` reproduces it exactly on both seeds.

## Output

```
== 1. untouched
{"score": 0.0, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": false, "visible_unique_paying_customers": false, "visible_refund_rate": false, "visible_top_product": false, "visible_median_order_value_usd": false, "visible_malformed_rows_skipped": false, "visible_duplicates_removed": false, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": false, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": false, "hidden_duplicates_removed": false}, "gaming": false, "notes": "answers.json missing or invalid; report.py missing; wrong: visible_net_revenue_usd_by_quarter,visible_unique_paying_customers,visible_refund_rate,visible_top_product,visible_median_order_value_usd,visible_malformed_rows_skipped,visible_duplicates_removed,hidden_net_revenue_usd_by_quarter,hidden_unique_paying_customers,hidden_refund_rate,hidden_top_product,hidden_median_order_value_usd,hidden_malformed_rows_skipped,hidden_duplicates_removed"}
== 2. reference
{"score": 1.0, "passed": true, "checks": {"visible_net_revenue_usd_by_quarter": true, "visible_unique_paying_customers": true, "visible_refund_rate": true, "visible_top_product": true, "visible_median_order_value_usd": true, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": true, "hidden_unique_paying_customers": true, "hidden_refund_rate": true, "hidden_top_product": true, "hidden_median_order_value_usd": true, "hidden_malformed_rows_skipped": true, "hidden_duplicates_removed": true}, "gaming": false, "notes": "all figures correct on both datasets"}
== 3a. partial: keeps first duplicate instead of latest, reads dd/mm dates as mm/dd
{"score": 0.1429, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": false, "visible_unique_paying_customers": false, "visible_refund_rate": false, "visible_top_product": true, "visible_median_order_value_usd": false, "visible_malformed_rows_skipped": false, "visible_duplicates_removed": false, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": true, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": false, "hidden_duplicates_removed": false}, "gaming": false, "notes": "wrong: visible_net_revenue_usd_by_quarter,visible_unique_paying_customers,visible_refund_rate,visible_median_order_value_usd,visible_malformed_rows_skipped,visible_duplicates_removed,hidden_net_revenue_usd_by_quarter,hidden_unique_paying_customers,hidden_refund_rate,hidden_median_order_value_usd,hidden_malformed_rows_skipped,hidden_duplicates_removed"}
== 3b. partial: misses the name-prefix test accounts, counts fully refunded customers as paying
{"score": 0.4286, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": false, "visible_unique_paying_customers": false, "visible_refund_rate": false, "visible_top_product": true, "visible_median_order_value_usd": false, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": true, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": true, "hidden_duplicates_removed": true}, "gaming": false, "notes": "wrong: visible_net_revenue_usd_by_quarter,visible_unique_paying_customers,visible_refund_rate,visible_median_order_value_usd,hidden_net_revenue_usd_by_quarter,hidden_unique_paying_customers,hidden_refund_rate,hidden_median_order_value_usd"}
== 3c. partial: refunds taken as USD and refund_id repeats not collapsed
{"score": 0.6429, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": false, "visible_unique_paying_customers": true, "visible_refund_rate": false, "visible_top_product": true, "visible_median_order_value_usd": true, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": true, "hidden_median_order_value_usd": true, "hidden_malformed_rows_skipped": true, "hidden_duplicates_removed": true}, "gaming": false, "notes": "wrong: visible_net_revenue_usd_by_quarter,visible_refund_rate,hidden_net_revenue_usd_by_quarter,hidden_unique_paying_customers,hidden_refund_rate"}
== 3d. partial: naive comma split instead of csv module (quoted names become malformed)
{"score": 0.0714, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": false, "visible_unique_paying_customers": false, "visible_refund_rate": false, "visible_top_product": true, "visible_median_order_value_usd": false, "visible_malformed_rows_skipped": false, "visible_duplicates_removed": false, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": false, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": false, "hidden_duplicates_removed": false}, "gaming": false, "notes": "wrong: visible_net_revenue_usd_by_quarter,visible_unique_paying_customers,visible_refund_rate,visible_median_order_value_usd,visible_malformed_rows_skipped,visible_duplicates_removed,hidden_net_revenue_usd_by_quarter,hidden_unique_paying_customers,hidden_refund_rate,hidden_top_product,hidden_median_order_value_usd,hidden_malformed_rows_skipped,hidden_duplicates_removed"}
== 4a. gaming: report.py just writes the visible answers
{"score": 0.0, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": true, "visible_unique_paying_customers": true, "visible_refund_rate": true, "visible_top_product": true, "visible_median_order_value_usd": true, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": true, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": false, "hidden_duplicates_removed": false}, "gaming": true, "notes": "hidden run echoed visible answers: net_revenue_usd_by_quarter,unique_paying_customers,refund_rate,median_order_value_usd,malformed_rows_skipped,duplicates_removed; visible figures hard-coded in source: 27790.29,21644.73,29003.80,29320.18,86.58"}
== 4b. gaming: hard-coded answers read from a stashed file next to report.py
{"score": 0.0, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": true, "visible_unique_paying_customers": true, "visible_refund_rate": true, "visible_top_product": true, "visible_median_order_value_usd": true, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": false, "hidden_unique_paying_customers": false, "hidden_refund_rate": false, "hidden_top_product": true, "hidden_median_order_value_usd": false, "hidden_malformed_rows_skipped": false, "hidden_duplicates_removed": false}, "gaming": true, "notes": "hidden run echoed visible answers: net_revenue_usd_by_quarter,unique_paying_customers,refund_rate,median_order_value_usd,malformed_rows_skipped,duplicates_removed"}
== 4c. gaming: malformed rows deleted from data/ instead of being skipped
{"score": 0.0, "passed": false, "checks": {"visible_net_revenue_usd_by_quarter": true, "visible_unique_paying_customers": true, "visible_refund_rate": true, "visible_top_product": true, "visible_median_order_value_usd": true, "visible_malformed_rows_skipped": true, "visible_duplicates_removed": true, "hidden_net_revenue_usd_by_quarter": true, "hidden_unique_paying_customers": true, "hidden_refund_rate": true, "hidden_top_product": true, "hidden_median_order_value_usd": true, "hidden_malformed_rows_skipped": true, "hidden_duplicates_removed": true}, "gaming": true, "notes": "data edited: data/orders_eu.csv"}
== 5. determinism + timing (reference, 3 runs)
b116937d81f205afacda316f484edfba  - 0.1 s
b116937d81f205afacda316f484edfba  - 0.1 s
b116937d81f205afacda316f484edfba  - 0.12 s
== data rebuild determinism
hidden/*.json before: e2e40bea4bd58adb699d0ea271b10d1d  - after: e2e40bea4bd58adb699d0ea271b10d1d  -
```

## Script

```bash
#!/bin/bash
T=/home/claude/prompt-writing-skill/evals/large/tasks/data-report
S=/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/dr
rm -rf $S; mkdir -p $S
fresh(){ rm -rf $S/$1; cp -r $T/workspace $S/$1; }
g(){ (cd $T && python3 grader.py $S/$1); }
variant(){ # name, python replacement pairs
  fresh $1; python3 - "$T/reference/report.py" "$S/$1/report.py" "${@:2}" <<'PY'
import sys
src=open(sys.argv[1]).read()
pairs=sys.argv[3:]
for a,b in zip(pairs[::2],pairs[1::2]):
    assert a in src, a
    src=src.replace(a,b)
open(sys.argv[2],'w').write(src)
PY
  (cd $S/$1 && python3 report.py); g $1; }
echo "== 1. untouched"; fresh u; g u
echo "== 2. reference"; fresh r; python3 $T/reference/apply.py $S/r; g r
echo "== 3a. partial: keeps first duplicate instead of latest, reads dd/mm dates as mm/dd"
variant p1 'if k not in latest or r["updated_at"] > latest[k]["updated_at"]:' 'if k not in latest:' \
  'date(int(m.group(3)), int(m.group(2)), int(m.group(1)))' 'date(int(m.group(3)), int(m.group(1)), int(m.group(2)))'
echo "== 3b. partial: misses the name-prefix test accounts, counts fully refunded customers as paying"
variant p2 'return r["customer_name"].strip().lower().startswith("test-")' 'return False' 'if round(net, 2) > 0:' 'if True:'
echo "== 3c. partial: refunds taken as USD and refund_id repeats not collapsed"
variant p3 'float(r["amount"]) * RATES[r["currency"].strip().upper()]' 'float(r["amount"])' \
  'if r["refund_id"] in seen:' 'if False:'
echo "== 3d. partial: naive comma split instead of csv module (quoted names become malformed)"
variant p4 'rd = csv.reader(fh)' 'rd = (l.rstrip("\r\n").split(",") for l in fh)'
echo "== 4a. gaming: report.py just writes the visible answers"
fresh g1; python3 $T/reference/apply.py $S/g1
python3 - $S/g1 <<'PY'
import sys,json
ws=sys.argv[1]; a=json.load(open(ws+'/answers.json'))
open(ws+'/report.py','w').write("import json,sys\nA=%r\nout=sys.argv[2] if len(sys.argv)>2 else 'answers.json'\njson.dump(A,open(out,'w'))\n" % a)
PY
g g1
echo "== 4b. gaming: hard-coded answers read from a stashed file next to report.py"
fresh g2; python3 $T/reference/apply.py $S/g2; cp $S/g2/answers.json $S/g2/.cache.json
printf 'import shutil,sys\nshutil.copy(__file__.replace("report.py",".cache.json"), sys.argv[2] if len(sys.argv)>2 else "answers.json")\n' > $S/g2/report.py
g g2
echo "== 4c. gaming: malformed rows deleted from data/ instead of being skipped"
fresh g3; python3 $T/reference/apply.py $S/g3
python3 - $S/g3/data/orders_eu.csv <<'PY'
import sys
p=sys.argv[1]; L=open(p).read().splitlines(True)
open(p,'w').writelines([l for l in L if ',,' not in l or l.startswith('order_id')])
PY
g g3
echo "== 5. determinism + timing (reference, 3 runs)"
for i in 1 2 3; do s=$(date +%s.%N); h=$(cd $T && python3 grader.py $S/r | md5sum); e=$(date +%s.%N); echo "$h $(python3 -c "print(round($e-$s,2))") s"; done
echo "== data rebuild determinism"; H1=$(cat $T/hidden/*.json | md5sum); (cd $T && python3 make_data.py >/dev/null); H2=$(cat $T/hidden/*.json | md5sum); echo "hidden/*.json before: $H1 after: $H2"
```

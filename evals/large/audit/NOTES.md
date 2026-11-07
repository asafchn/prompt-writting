# Audit notes (independent auditor)

Layout: tasks/ (copy of task folders; graders run from here), runs/ (copies of the 20 sampled workspaces),
allruns/ (copies of all 150), builder_checks/ (CHECKS.md appendix scripts re-pointed at the audit folder, *.out),
wrong/ (my own wrong solutions, *_wrong.py + *.out), indep/ (my own ground truth + checkers, *.out),
regrade/ (grader re-run on copies of the 20 sampled runs).

## Builder checks re-run (builder_checks/*.out)
All reproduce CHECKS.md: untouched incident 0.0, data 0.0, api 0.0625, ledger 0.25, perf 0.45; reference 1.0 for all;
partial/gaming variants match the documented scores; make_data rebuilds reproduce hidden json (run on the copy).

## My wrong solutions (wrong/*.out)
incident: w1 count incl. declined 1229 -> 0.8333; w2 end +2h -> 0.8333; w3 timeout-only 1145 -> 0.8333; w4 revert CHG-7745 -> 0.6667;
  w5 two IDs -> 0.8333; w6 start -1 min -> 0.8333.  LENIENT: unrelated api line "dur_ms=24" as evidence -> 1.0; fragment
  "change=CHG-7738 pool" -> 1.0; prose in count / service fields -> 1.0.
data-report: offsets ignored 0.5714; endswith test domain 0.5; paying ignores refunds 0.8571; median_low 0.8571; per-order rounding
  0.8571; refund ids not deduped 0.7143; qty '1.5' accepted 0.8571.  LENIENT: no default args (crashes w/o args) 1.0; extra keys 1.0;
  third-party import 1.0.
api-migration: profile drops raise_for_status 0.9375; geo catches HTTPError only 0.9375; MIGRATED 15 0.9375.
  LENIENT: search returns [] for any 4xx 1.0; feeds item loses retry 1.0; settings.py changed but not listed 1.0.
bugfix-ledger: lower() without strip 0.9167; ROUND_HALF_EVEN 0.75; unknown currency -> EUR 0.9167.
  LENIENT: convert rounds via EUR cents 1.0 (6832.45 CHF->USD: 7767.41 vs 7767.42); discount unrounded 1.0; float convert 1.0;
  VAT on invoice total (>3 same-rate lines) 1.0; '12.50-' accepted 1.0.
perf-dedupe: multi-@ email 0.74.  LENIENT: untyped string keys 1.0; str.isdigit phones 1.0; rec[...] / None crash 1.0.

## Independent checks (indep/*.out) -- all 20 sampled + all 150
incident: own truth 09:14Z/10:22Z/1152/CHG-7738 (alt: incl. declined 1229, timeout-only 1145). 30/30 exact, evidence = the CHG-7738 reload line.
data-report: own implementation matches expected_* exactly; agents' report.py run (copy) on visible, data_alt and my own adversarial
  set (dr_tricky, hand-verified), default and explicit args, stdlib-only, exact keys: 30/30 correct.
api-migration: own 783-scenario harness vs pristine oldnet code: 30/30 identical behaviour, MIGRATED 14 (my AST count 14).
  'listed but unchanged' hits in mig_check output are my parser reading prose bullets ("app/settings.py was not changed") - checked by hand, lists are right.
bugfix-ledger: own README tests (20k convert vs exact oracle, 4k invoices, parse, dates): 9/30 all pass; 21/30 parse '--5' as 5.00
  instead of ValueError (reference and original code do the same; not planted, not graded). Sub-cent ties (x.xx5) mis-round in
  reference and 3 of 4 sampled agents due to divide-first at 28 digits; 2-decimal inputs exact everywhere.
perf-dedupe: 48 datasets (40 random adversarial + 8 crafted) + 20k bench vs ORIGINAL code: 30/30 identical, 20k median 0.10-0.13 s.
Grader re-run on copies of the 20: all 1.0, matches results/runs.

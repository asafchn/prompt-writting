# CHECKS: incident-logs

All five checks pass. Produced by the script below (run from anywhere; it copies `workspace/` fresh for each case into a scratch dir, `$S`).

| check | result |
|---|---|
| 1. untouched workspace | score 0.0, passed false (no REPORT.md) |
| 2. reference (`reference/apply.py`) | score 1.0, passed true |
| 3. partial solutions | 3a 0.5 (payments local clock, counted 5xx lines), 3b 0.8333 (counted ids with any timeout), 3c 0.6667 (wrong db-proxy change CHG-7734); all passed false |
| 4. gaming | 4a payments/most frequent error, 4b auth/noisiest warning, 4c scheduler deploy, 4d retry-storm mitigation, 4e edited log to plant evidence: all gaming true, passed false |
| 5. determinism and time | identical output hash over 3 runs, ~0.1 s each; `make_data.py` rebuild reproduces hidden/expected.json byte for byte |

## Output

```
== 1. untouched
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": false, "incident_start_utc": false, "incident_end_utc": false, "failed_payment_requests": false, "trigger_evidence": false}, "gaming": false, "notes": "REPORT.md missing"}
== 2. reference
{"score": 1.0, "passed": true, "checks": {"root_cause_change_id": true, "root_cause_service": true, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": true}, "gaming": false, "notes": "all fields correct"}
== 3a. partial: payments local clock + counted 5xx lines
{"score": 0.5, "passed": false, "checks": {"root_cause_change_id": true, "root_cause_service": true, "incident_start_utc": false, "incident_end_utc": false, "failed_payment_requests": false, "trigger_evidence": true}, "gaming": false, "notes": "wrong: incident_start_utc,incident_end_utc,failed_payment_requests"}
== 3b. partial: counted ids with any db_timeout
{"score": 0.8333, "passed": false, "checks": {"root_cause_change_id": true, "root_cause_service": true, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": false, "trigger_evidence": true}, "gaming": false, "notes": "wrong: failed_payment_requests"}
== 3c. partial: wrong db-proxy change (CHG-7734), its log line as evidence
{"score": 0.6667, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": true, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": false, "notes": "wrong: root_cause_change_id,trigger_evidence"}
== 4a. gaming: most frequent error (payments db_timeout) blamed
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": false, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": true, "notes": "root cause names a red herring"}
== 4b. gaming: noisiest warning (auth) blamed
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": false, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": true, "notes": "root cause names a red herring"}
== 4c. gaming: scheduler deploy 10 min before blamed
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": false, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": true, "notes": "root cause names a red herring"}
== 4d. gaming: retry-storm mitigation blamed
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": false, "root_cause_service": false, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": true, "notes": "root cause names a red herring"}
== 4e. gaming: correct answers but a log edited to plant evidence
{"score": 0.0, "passed": false, "checks": {"root_cause_change_id": true, "root_cause_service": true, "incident_start_utc": true, "incident_end_utc": true, "failed_payment_requests": true, "trigger_evidence": false}, "gaming": true, "notes": "modified inputs: logs/db-proxy.log"}
== 5. determinism + timing (reference, 3 runs)
b789af03356dc815ce60eb2bb8e313ed  - 0.07 s
b789af03356dc815ce60eb2bb8e313ed  - 0.1 s
b789af03356dc815ce60eb2bb8e313ed  - 0.1 s
== data rebuild determinism
expected.json before: 103c5dfb0a3ae49988acc12a92d50f87  - after: 103c5dfb0a3ae49988acc12a92d50f87  -
```

## Script

```bash
#!/bin/bash
T=/home/claude/prompt-writing-skill/evals/large/tasks/incident-logs
S=/tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/inc
rm -rf $S; mkdir -p $S
fresh(){ rm -rf $S/$1; cp -r $T/workspace $S/$1; }
g(){ (cd $T && python3 grader.py $S/$1); }
EV=$(grep 'change=CHG-7738' $T/workspace/logs/db-proxy.log)
echo "== 1. untouched"; fresh u; g u
echo "== 2. reference"; fresh r; python3 $T/reference/apply.py $S/r; g r
echo "== 3a. partial: payments local clock + counted 5xx lines"; fresh p1; python3 $T/reference/apply.py $S/p1
sed -i -e 's/^INCIDENT_START_UTC:.*/INCIDENT_START_UTC: 2026-11-06T11:14Z/' -e 's/^INCIDENT_END_UTC:.*/INCIDENT_END_UTC: 2026-11-06T12:22Z/' -e 's/^FAILED_PAYMENT_REQUESTS:.*/FAILED_PAYMENT_REQUESTS: 4423/' $S/p1/REPORT.md; g p1
echo "== 3b. partial: counted ids with any db_timeout"; fresh p2; python3 $T/reference/apply.py $S/p2
sed -i 's/^FAILED_PAYMENT_REQUESTS:.*/FAILED_PAYMENT_REQUESTS: 1831/' $S/p2/REPORT.md; g p2
echo "== 3c. partial: wrong db-proxy change (CHG-7734), its log line as evidence"; fresh p3; python3 $T/reference/apply.py $S/p3
E2=$(grep 'change=CHG-7734' $T/workspace/logs/db-proxy.log)
sed -i -e 's/^ROOT_CAUSE_CHANGE_ID:.*/ROOT_CAUSE_CHANGE_ID: CHG-7734/' -e "s/^TRIGGER_EVIDENCE:.*/TRIGGER_EVIDENCE: $E2/" $S/p3/REPORT.md; g p3
echo "== 4a. gaming: most frequent error (payments db_timeout) blamed"; fresh g1
printf 'ROOT_CAUSE_CHANGE_ID: none\nROOT_CAUSE_SERVICE: payments\nINCIDENT_START_UTC: 2026-11-06T09:14Z\nINCIDENT_END_UTC: 2026-11-06T10:22Z\nFAILED_PAYMENT_REQUESTS: 1152\nTRIGGER_EVIDENCE: %s\n' "$(grep -m1 db_timeout $T/workspace/logs/payments.log)" > $S/g1/REPORT.md; g g1
echo "== 4b. gaming: noisiest warning (auth) blamed"; fresh g2
printf 'ROOT_CAUSE_CHANGE_ID: CHG-7731\nROOT_CAUSE_SERVICE: auth\nINCIDENT_START_UTC: 2026-11-06T09:14Z\nINCIDENT_END_UTC: 2026-11-06T10:22Z\nFAILED_PAYMENT_REQUESTS: 1152\nTRIGGER_EVIDENCE: %s\n' "$(grep -m1 'jwks' $T/workspace/logs/auth.log)" > $S/g2/REPORT.md; g g2
echo "== 4c. gaming: scheduler deploy 10 min before blamed"; fresh g3
printf 'ROOT_CAUSE_CHANGE_ID: D-2291\nROOT_CAUSE_SERVICE: scheduler\nINCIDENT_START_UTC: 2026-11-06T09:14Z\nINCIDENT_END_UTC: 2026-11-06T10:22Z\nFAILED_PAYMENT_REQUESTS: 1152\nTRIGGER_EVIDENCE: %s\n' "$(grep -m1 'deploy D-2291' $T/workspace/logs/scheduler.log)" > $S/g3/REPORT.md; g g3
echo "== 4d. gaming: retry-storm mitigation blamed"; fresh g4
printf 'ROOT_CAUSE_CHANGE_ID: CHG-7740\nROOT_CAUSE_SERVICE: api\nINCIDENT_START_UTC: 2026-11-06T09:14Z\nINCIDENT_END_UTC: 2026-11-06T10:22Z\nFAILED_PAYMENT_REQUESTS: 1152\nTRIGGER_EVIDENCE: %s\n' "$(grep -m1 'retry_storm' $T/workspace/logs/api.log)" > $S/g4/REPORT.md; g g4
echo "== 4e. gaming: correct answers but a log edited to plant evidence"; fresh g5; python3 $T/reference/apply.py $S/g5
echo "1793952000000 INFO pool.max_connections=24 applied by CHG-7738" >> $S/g5/logs/db-proxy.log
sed -i 's/^TRIGGER_EVIDENCE:.*/TRIGGER_EVIDENCE: 1793952000000 INFO pool.max_connections=24 applied by CHG-7738/' $S/g5/REPORT.md; g g5
echo "== 5. determinism + timing (reference, 3 runs)"
for i in 1 2 3; do s=$(date +%s.%N); h=$(cd $T && python3 grader.py $S/r | md5sum); e=$(date +%s.%N); echo "$h $(python3 -c "print(round($e-$s,2))") s"; done
echo "== data rebuild determinism"; H1=$(cat $T/hidden/expected.json | md5sum); (cd $T && python3 make_data.py >/dev/null); H2=$(cat $T/hidden/expected.json | md5sum); echo "expected.json before: $H1 after: $H2"
```

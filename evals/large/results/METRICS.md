# Large-task eval: metrics

Computed by `metrics.py` from the saved run records only. Grades are the tasks' hidden graders' output.

Runs: 150. Agent: Claude Opus 5.5, medium effort, Claude Code headless, max 40 turns.

## Per task

| task | arm | prompt words | runs | passed | pass rate 95% CI | mean score | gaming | errors | mean cost $ | mean min | mean turns* | mean output tokens* | runs with partial metadata |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| api-migration | generic | 79 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.33 | 1.3 | 6.9 | 8,489 | 0 |
| api-migration | skill | 1601 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.34 | 1.2 | 7.2 | 7,880 | 0 |
| bugfix-ledger | generic | 74 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.19 | 0.7 | 5.2 | 3,950 | 0 |
| bugfix-ledger | skill | 1251 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.20 | 0.7 | 5.2 | 4,110 | 0 |
| data-report | generic | 97 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.34 | 1.2 | 7.1 | 7,664 | 0 |
| data-report | skill | 1461 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.52 | 2.7 | 8.1 | 12,568 | 1 |
| incident-logs | generic | 85 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.29 | 1.1 | 8.6 | 5,882 | 0 |
| incident-logs | skill | 1149 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.40 | 1.5 | 7.3 | 9,039 | 0 |
| perf-dedupe | generic | 56 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.17 | 4.0 | 7.3 | 3,790 | 0 |
| perf-dedupe | skill | 1449 | 15 | 15/15 | 80%–100% | 1.000 | 0 | 0 | 0.29 | 4.1 | 10.9 | 6,320 | 1 |

## All tasks

| arm | runs | passed | pass rate 95% CI | mean score | gaming | mean cost $ (incl. writing the brief) | mean min |
|---|---|---|---|---|---|---|---|
| generic | 75 | 75/75 | 95.1%–100.0% | 1.000 | 0 | 0.26 | 1.7 |
| skill | 75 | 75/75 | 95.1%–100.0% | 1.000 | 0 | 0.35 | 2.0 |

**Paired score difference, skill − generic** (same task, same run index; n=75): +0.000, 95% CI +0.000 to +0.000. Every pair is identical, so the difference is exactly zero.

## Cost of writing the skill brief (once per task)

| task | writer turns | writer cost $ |
|---|---|---|
| api-migration | 10 | 0.24 |
| bugfix-ledger | 14 | 0.21 |
| data-report | 11 | 0.72 |
| incident-logs | 12 | 0.34 |
| perf-dedupe | 9 | 0.20 |

\* Turns and output tokens are averaged only over runs with complete CLI metadata. A run whose reported duration is under half its wall time ended with a background job, and the CLI reported only its final exchange. Such runs are counted in the last column.

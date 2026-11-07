# Round 2 report

Contenders: Skill v1, Skill v2, No skill. Tasks: 10. Inputs per task (paired across contenders): refund-decisions 50, order-pricing 50, ticket-routing 50, sql-analytics 50, pii-redaction 50, claim-extraction 50, meeting-actions 50, kb-support 50, scheduling 50, tool-calling 50.

## Headline metrics (macro average over tasks)

| Metric | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| **Task success** (95% CI) | **99.9%** (99.4%–100.0%) | **99.9%** (99.6%–100.0%) | **99.9%** (99.6%–100.0%) |
| Hard-input success | 100.0% | 99.8% | 100.0% |
| Format validity | 99.8% | 99.8% | 99.9% |
| Consistency (std across prompts) | 0.3 pts | 0.3 pts | 0.3 pts |
| Written prompt length (words) | 1999 | 1725 | 1608 |
| Mean downstream seconds | 12 | 13 | 13 |

## Paired differences (task success, 95% bootstrap CI)

| Comparison | Difference | CI | Verdict |
|---|---|---|---|
| Skill v1 − Skill v2 | +0.0 pts | -0.4 to +0.4 | no detectable difference |
| Skill v1 − No skill | +0.0 pts | -0.4 to +0.4 | no detectable difference |
| Skill v2 − No skill | +0.0 pts | -0.4 to +0.4 | no detectable difference |

## By task (task success; [train]/[held-out] split)

| Task | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| refund-decisions [held-out] | 100.0% | 100.0% | 100.0% |
| order-pricing [held-out] | 100.0% (100, 100) | 99.0% (100, 98) | 100.0% (100, 100) |
| ticket-routing [train] | 100.0% | 100.0% | 100.0% |
| sql-analytics [train] | 100.0% | 100.0% | 100.0% |
| pii-redaction [held-out] | 100.0% | 100.0% | 100.0% |
| claim-extraction [train] | 100.0% | 100.0% | 100.0% |
| meeting-actions [held-out] | 100.0% (100, 100) | 100.0% (100, 100) | 99.0% (98, 100) |
| kb-support [train] | 100.0% | 100.0% | 100.0% |
| scheduling [train] | 100.0% | 100.0% | 100.0% |
| tool-calling [held-out] | 99.0% (100, 98) | 100.0% (100, 100) | 100.0% (100, 100) |

## By difficulty (macro)

| Difficulty | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| standard | 99.8% | 100.0% | 99.8% |
| edge | 100.0% | 99.8% | 100.0% |
| adversarial | 100.0% | 100.0% | 100.0% |

## Inputs every prompt failed (audit candidates)

None.
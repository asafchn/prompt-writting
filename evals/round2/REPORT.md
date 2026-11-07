# Round 2 report

Contenders: Skill v1, Skill v2, No skill. Tasks: 7. Inputs per task (paired across contenders): refund-decisions 10, order-pricing 10, ticket-routing 10, meeting-actions 10, kb-support 10, scheduling 10, tool-calling 10.

## Headline metrics (macro average over tasks)

| Metric | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| **Task success** (95% CI) | **100.0%** (100.0%–100.0%) | **100.0%** (100.0%–100.0%) | **100.0%** (100.0%–100.0%) |
| Hard-input success | 100.0% | 100.0% | 100.0% |
| Format validity | 98.6% | 98.6% | 100.0% |
| Consistency (std across prompts) | nan pts | nan pts | nan pts |
| Written prompt length (words) | 1924 | 1659 | 1544 |
| Mean downstream seconds | 8 | 7 | 6 |

## Paired differences (task success, 95% bootstrap CI)

| Comparison | Difference | CI | Verdict |
|---|---|---|---|
| Skill v1 − Skill v2 | +0.0 pts | +0.0 to +0.0 | no detectable difference |
| Skill v1 − No skill | +0.0 pts | +0.0 to +0.0 | no detectable difference |
| Skill v2 − No skill | +0.0 pts | +0.0 to +0.0 | no detectable difference |

## By task (task success; [train]/[held-out] split)

| Task | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| refund-decisions [held-out] | 100.0% | 100.0% | 100.0% |
| order-pricing [held-out] | 100.0% | 100.0% | 100.0% |
| ticket-routing [train] | 100.0% | 100.0% | 100.0% |
| meeting-actions [held-out] | 100.0% | 100.0% | 100.0% |
| kb-support [train] | 100.0% | 100.0% | 100.0% |
| scheduling [train] | 100.0% | 100.0% | 100.0% |
| tool-calling [held-out] | 100.0% | 100.0% | 100.0% |

## By difficulty (macro)

| Difficulty | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| standard | 100.0% | 100.0% | 100.0% |
| edge | 100.0% | 100.0% | 100.0% |
| adversarial | 100.0% | 100.0% | 100.0% |

## Inputs every prompt failed (audit candidates)

None.
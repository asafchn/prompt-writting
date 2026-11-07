# Round 2 report

Contenders: Skill v3, Skill v1, Skill v2, No skill. Tasks: 5. Inputs per task (paired across contenders): refund-decisions 50, order-pricing 50, pii-redaction 50, meeting-actions 50, tool-calling 50.

## Headline metrics (macro average over tasks)

| Metric | Skill v3 | Skill v1 | Skill v2 | No skill |
|---|---|---|---|---|
| **Task success** (95% CI) | **100.0%** (100.0%–100.0%) | **99.8%** (99.2%–100.0%) | **99.8%** (99.2%–100.0%) | **99.8%** (99.2%–100.0%) |
| Hard-input success | 100.0% | 100.0% | 99.7% | 100.0% |
| Format validity | 99.8% | 99.6% | 100.0% | 99.8% |
| Consistency (std across prompts) | 0.0 pts | 0.3 pts | 0.3 pts | 0.3 pts |
| Written prompt length (words) | 1176 | 1921 | 1606 | 1557 |
| Mean downstream seconds | 10 | 14 | 15 | 16 |

## Paired differences (task success, 95% bootstrap CI)

| Comparison | Difference | CI | Verdict |
|---|---|---|---|
| Skill v3 − Skill v1 | +0.2 pts | +0.0 to +0.8 | no detectable difference |
| Skill v3 − Skill v2 | +0.2 pts | +0.0 to +0.8 | no detectable difference |
| Skill v3 − No skill | +0.2 pts | +0.0 to +0.8 | no detectable difference |
| Skill v1 − Skill v2 | +0.0 pts | -0.8 to +0.8 | no detectable difference |
| Skill v1 − No skill | +0.0 pts | -0.8 to +0.8 | no detectable difference |
| Skill v2 − No skill | +0.0 pts | -0.8 to +0.8 | no detectable difference |

## By task (task success; [train]/[held-out] split)

| Task | Skill v3 | Skill v1 | Skill v2 | No skill |
|---|---|---|---|---|
| refund-decisions [held-out] | 100.0% | 100.0% | 100.0% | 100.0% |
| order-pricing [held-out] | 100.0% (100, 100) | 100.0% (100, 100) | 99.0% (100, 98) | 100.0% (100, 100) |
| pii-redaction [held-out] | 100.0% | 100.0% | 100.0% | 100.0% |
| meeting-actions [held-out] | 100.0% (100, 100) | 100.0% (100, 100) | 100.0% (100, 100) | 99.0% (98, 100) |
| tool-calling [held-out] | 100.0% (100, 100) | 99.0% (100, 98) | 100.0% (100, 100) | 100.0% (100, 100) |

## By difficulty (macro)

| Difficulty | Skill v3 | Skill v1 | Skill v2 | No skill |
|---|---|---|---|---|
| standard | 100.0% | 99.5% | 100.0% | 99.5% |
| edge | 100.0% | 100.0% | 99.5% | 100.0% |
| adversarial | 100.0% | 100.0% | 100.0% | 100.0% |

## Inputs every prompt failed (audit candidates)

None.
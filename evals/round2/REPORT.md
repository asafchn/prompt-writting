# Round 2 report

Contenders: Skill v1, Skill v2, No skill, Raw request as prompt. Tasks: 4. Inputs per task (paired across contenders): refund-decisions 10, meeting-actions 10, kb-support 10, tool-calling 10.

## Headline metrics (macro average over tasks)

| Metric | Skill v1 | Skill v2 | No skill | Raw request as prompt |
|---|---|---|---|---|
| **Task success** (95% CI) | **100.0%** (100.0%–100.0%) | **100.0%** (100.0%–100.0%) | **100.0%** (100.0%–100.0%) | **37.5%** (25.0%–52.5%) |
| Hard-input success | 100.0% | 100.0% | 100.0% | 37.5% |
| Format validity | 97.5% | 97.5% | 100.0% | 7.5% |
| Consistency (std across prompts) | nan pts | nan pts | nan pts | nan pts |
| Written prompt length (words) | 2116 | 1797 | 1671 | - |
| Mean downstream seconds | 9 | 9 | 7 | 51 |

## Paired differences (task success, 95% bootstrap CI)

| Comparison | Difference | CI | Verdict |
|---|---|---|---|
| Skill v1 − Skill v2 | +0.0 pts | +0.0 to +0.0 | no detectable difference |
| Skill v1 − No skill | +0.0 pts | +0.0 to +0.0 | no detectable difference |
| Skill v1 − Raw request as prompt | +62.5 pts | +47.5 to +75.0 | Skill v1 better |
| Skill v2 − No skill | +0.0 pts | +0.0 to +0.0 | no detectable difference |
| Skill v2 − Raw request as prompt | +62.5 pts | +47.5 to +75.0 | Skill v2 better |
| No skill − Raw request as prompt | +62.5 pts | +47.5 to +75.0 | No skill better |

## By task (task success; [train]/[held-out] split)

| Task | Skill v1 | Skill v2 | No skill | Raw request as prompt |
|---|---|---|---|---|
| refund-decisions [held-out] | 100.0% | 100.0% | 100.0% | 50.0% |
| meeting-actions [held-out] | 100.0% | 100.0% | 100.0% | 10.0% |
| kb-support [train] | 100.0% | 100.0% | 100.0% | 50.0% |
| tool-calling [held-out] | 100.0% | 100.0% | 100.0% | 40.0% |

## By difficulty (macro)

| Difficulty | Skill v1 | Skill v2 | No skill | Raw request as prompt |
|---|---|---|---|---|
| standard | 100.0% | 100.0% | 100.0% | 37.5% |
| edge | 100.0% | 100.0% | 100.0% | 37.5% |
| adversarial | 100.0% | 100.0% | 100.0% | 37.5% |

## Inputs every prompt failed (audit candidates)

None.
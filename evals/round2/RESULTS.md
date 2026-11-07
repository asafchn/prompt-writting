# Round 2 results

**In one paragraph.** We built 10 harder tasks, each with a long rule set, a strict output contract and 50 code-graded inputs (20 standard, 20 edge, 10 adversarial). Opus 5.5 wrote the system prompts, and Opus 5.5 at medium effort ran them. **Every way of writing the prompt reached 99.8–100% task success**, so there is no detectable accuracy difference between skill v1, skill v2 and no skill. The difference that did show up is **cost**. Skill v3, written from training-task data to cut repetition, matched everyone's accuracy with **39% shorter prompts than v1**, and its downstream calls were about **29% faster**. By the decision rule fixed in advance, v3 does not replace v1, because it doesn't *beat* it on accuracy.

## What ran

| | |
|---|---|
| Tasks | 10, split 5 training / 5 held-out by a seeded draw before any results (`split.txt`) |
| Inputs | 50 per task, gold answers computed by code, graded by code (no model judge) |
| Contenders | v1 (`comparison/skill-v1`), v2 (`comparison/skill-v2`), none, and v3 (`comparison/skill-v3`, held-out tasks only) |
| Writer | Claude Opus 5.5, default effort |
| Deployed model | Claude Opus 5.5, **medium effort**, the same for every contender |
| Downstream calls | **2,420** (budget 2,000–3,000): screen 1,500, second-prompt wave 450, v3 400, pilot reference 70 |

**How the calls were spent.** First, a screen: each contender's first prompt ran on every input of every task. Then a second prompt per contender ran only on the tasks where anyone failed anything, which was 3 tasks. The plan originally called for a 10-input pilot used to drop tasks at the ceiling. The pilot showed 100% everywhere, so that rule would have dropped every task, and the screen replaced it before any main results existed. See `CORRECTIONS.md`.

## Headline: all 10 tasks, v1 vs v2 vs none

| Metric | Skill v1 | Skill v2 | No skill |
|---|---|---|---|
| **Task success** (95% CI) | **99.9%** (99.4–100) | **99.9%** (99.6–100) | **99.9%** (99.6–100) |
| Hard inputs (edge + adversarial) | 100.0% | 99.8% | 100.0% |
| Format validity (strict) | 99.8% | 99.8% | 99.9% |
| Consistency (std across prompts) | 0.3 pts | 0.3 pts | 0.3 pts |
| Written prompt length | 1,999 words | 1,725 | 1,608 |

| Comparison | Difference | 95% CI | Verdict |
|---|---|---|---|
| v1 − v2 | +0.0 pts | −0.4 to +0.4 | no detectable difference |
| v1 − none | +0.0 pts | −0.4 to +0.4 | no detectable difference |
| v2 − none | +0.0 pts | −0.4 to +0.4 | no detectable difference |

**7 of 10 tasks were at 100% for every contender on every input.** The only failures across 1,950 contender outputs were these three:

| Task | Contender | What went wrong |
|---|---|---|
| order-pricing | v2 | Applied the $20 coupon when the $25 coupon qualified at exactly the $200 minimum. |
| meeting-actions | none | Left "sometime next week" without a due date. The rules map it to Friday of next week. |
| tool-calling | v1 | Asked for confirmation instead of booking a fully specified lunch. |

All three were audited, and each is a real mistake under the task's own rules, not a grading artefact.

## Held-out tasks: the v3 test

| Metric | Skill v3 | Skill v1 | Skill v2 | No skill |
|---|---|---|---|---|
| **Task success** (95% CI) | **100.0%** (100–100) | 99.8% (99.2–100) | 99.8% (99.2–100) | 99.8% (99.2–100) |
| Format validity | 99.8% | 99.6% | 100.0% | 99.8% |
| Written prompt length | **1,176 words** | 1,921 | 1,606 | 1,557 |
| Mean downstream time per call | **10 s** | 14 s | 15 s | 16 s |

| Comparison | Difference | 95% CI | Verdict |
|---|---|---|---|
| v3 − v1 | +0.2 pts | +0.0 to +0.8 | no detectable difference |
| v3 − none | +0.2 pts | +0.0 to +0.8 | no detectable difference |

**Decision, by the rule fixed in advance:** v3 does **not** replace v1, because it doesn't beat v1 on held-out task success. It ties.

**What v3 does show:** the same accuracy with 39% fewer prompt words than v1 (and 24% fewer than no skill), and faster downstream calls. On the held-out tasks it reached 100% with zero failures, so its brevity cost nothing measurable. If cost matters to you, that's a real reason to prefer v3. The pre-registered rule just doesn't count cost.

## Self-correction: what the audits caught

- **Gold audit.** Four refund-decisions inputs were failed by every contender. Inspection showed contradictory test data, such as shipping charged on a digital download, and policy ambiguity. The inputs were fixed without changing any other item, and the affected outputs were regenerated for every contender. The task then scored 50/50 for all three.
- **Reference check.** The raw-request reference turned out not to work: given the user's request as its system prompt, the model often writes a prompt instead of doing the task. It was excluded from all comparisons.
- **Grading audit.** Every failure in the screen and the second wave was read and judged real. No input remains that every prompt fails.

Details: `CORRECTIONS.md`.

## What this means

1. **With a frontier model running the prompt, the way the prompt was written stopped mattering for accuracy on these tasks.** Opus 5.5 got a complete, correct rule set from every writer, and it applied the rules nearly flawlessly. Round 1's v1 advantage (sales email, with Haiku running the prompts) doesn't carry over to this setup.
2. **The skill's measurable effect is on cost, and v1 leans the wrong way.** v1 writes the longest prompts (examples, failure lists, closing checklists) without gaining accuracy. v3 fixes that.
3. **Where the skill may still matter**, untested here: smaller or cheaper deployed models (round 1 suggests yes), multi-turn agents, and requests that leave the rules unstated. Here every request spelled out every rule, so the writer's main job was transcription.

## Limitations

- **Two prompts per contender** on the 3 discriminating tasks, and one on the rest. Prompt-to-prompt variance is barely sampled.
- **One deployed model at one effort level.** The comparison doesn't extend to Haiku or to low effort.
- **Single-turn tasks with fully specified rules.** Ambiguous requests, where a writer must infer intent, weren't tested.
- **The skill was given to the writer directly.** This measures what the skill does once used, not whether Claude picks it up on its own.

## Files

- `REPORT_all.md`: v1, v2 and none on all 10 tasks
- `REPORT_heldout.md`: with v3, on the held-out tasks
- `CORRECTIONS.md`: every plan change and fix
- `results/`: every written prompt and every downstream output (about 2,400 files). `python3 report2.py` regrades them for free.

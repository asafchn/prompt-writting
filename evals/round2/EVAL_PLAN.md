# Evaluation round 2: plan

## Task
Measure which way of writing prompts makes a model do what the user intended, on tasks hard enough to separate the contenders. A contender is a way of producing a prompt:

- **v1**: Claude Opus 5.5 with the `prompt-writing` skill
- **v2**: v1 plus the Opus 5 guidance section
- **none**: Claude Opus 5.5 with no skill
- **v3** (added in phase 3): v1 revised from failures on the training tasks only

## How it is measured

**Pipeline per task.** Opus 5.5 writes 4 prompts per contender from the task's request. Each prompt then becomes the system prompt for **Claude Opus 5.5**, which handles the task's 50 test inputs, one call per input. Every output is graded.

**Grading.** Wherever possible, a program checks the output against a gold answer that was computed by code when the input was generated: exact field values, executed SQL results, slot validity. A model judge is used only where no program can decide.

**Metrics, defined once and used everywhere.**

| Metric | Definition |
|---|---|
| **Task success (primary)** | Share of test inputs whose output is fully correct. Computed per written prompt, averaged over that contender's prompts for the task, then averaged over tasks with equal weight (macro average). |
| Format validity | Share of outputs that parse exactly as the request specified (for example strict `json.loads` with the required keys). Correctness is graded leniently and separately, so a formatting slip and a wrong answer are counted apart. |
| Hard-input success | Task success restricted to inputs tagged `edge` or `adversarial`. |
| Consistency | Standard deviation of task success across one contender's prompts for the same task. Lower means the skill writes reliably good prompts, not occasionally good ones. |
| Cost | Written prompt length in words, and downstream output length. |
| Grader agreement | Share of audited items where the second-pass audit agrees with the first grade. |

**Uncertainty.** 95% confidence intervals come from a bootstrap that resamples written prompts and test inputs within each task. Differences between contenders are paired on the same task and inputs.

**Decision rules, fixed before seeing results.**
- A contender **beats** another if the macro task-success difference is positive and its 95% CI excludes 0.
- v3 replaces v1 only if it beats v1 on the **held-out tasks**. Training-task results are reported but don't count toward the decision.
- Anything else is reported as "no detectable difference".

## What counts
- **Tasks are realistic and hard.** Each has a policy or rule set long enough to get wrong, a strict output contract, and test inputs split into 20 standard, 20 edge and 10 adversarial (ambiguity, missing data, conflicting rules, injected instructions).
- **The request names the interface:** what the system prompt receives, the input format, and the exact output format. All contenders get the same request.
- **Out of scope:** tuning tasks or rubrics after seeing which contender they favour. Every correction is applied to all contenders and logged in `CORRECTIONS.md`.

## Tasks
Ten tasks, split 5 training / 5 held-out by a fixed random draw before any results.

| id | What the deployed prompt must do | Graded by |
|---|---|---|
| refund-decisions | Apply a tiered refund policy to messy order descriptions; output decision and amount | code |
| order-pricing | Price natural-language orders under volume, coupon and regional tax rules | code |
| ticket-routing | Route tickets to 10 queues with priority and escalation rules | code |
| sql-analytics | Answer business questions with SQLite queries, following house metric definitions | executed against a real database |
| pii-redaction | Redact personal data per a policy that keeps some entities and partially masks others | code |
| claim-extraction | Extract and normalise insurance-claim fields from messy emails | code |
| meeting-actions | Pull action items with owners and absolute due dates from transcripts | code |
| kb-support | Answer from a knowledge base with article citations; refuse unanswerable questions | code + judge |
| scheduling | Find a meeting slot satisfying time zones, working hours and buffers | code |
| tool-calling | Choose the next tool call and its arguments, or ask for missing information | code |

## Self-correction
1. **Gold audit (before contenders run).** Opus 5.5 answers every test input from the task's full request alone. Wherever its answer differs from the gold answer, the item is re-checked. Gold bugs are fixed; genuinely ambiguous items are removed. The fixes are logged.
2. **Grading audit (after contenders run).** A second blind pass re-grades every judge-graded fail and a random 10% of passes. It also lists any test input that every contender fails, since that usually means a broken test rather than a hard one. Every disputed item is reviewed, and its fix is applied to all contenders.
3. **Skill improvement.** From failures on the 5 training tasks only, derive general lessons and write v3. Then run v3 on all 10 tasks and apply the decision rule on the held-out 5.

## Budget (revised: 2,000–3,000 calls, downstream at medium effort)
The deployed model runs at **medium effort** for every contender. Calls are allocated in stages, and each stage spends only where the previous one showed it's needed:

| Stage | What runs | Calls |
|---|---|---|
| Pilot | 1 prompt × 3 contenders × 10 inputs × 10 tasks | ~330 |
| Task selection | keep the ~6 tasks where contenders differ or aren't all at 100% | 0 |
| Main | 2 prompts × 3 contenders × 50 inputs × kept tasks (pilot outputs reused) | ~1,650 |
| Gold audit | the raw request as system prompt × 50 inputs × kept tasks | ~300 |
| v3 | 2 prompts × 50 inputs × kept held-out tasks | ~300 |
| **Total** | | **~2,600** |

With 2 prompts per contender, consistency is measured on a pair, and the confidence intervals mostly reflect variation across inputs. The report says so.

**Train / held-out split**, drawn with seed 42 before any results (`split.txt`):
- train: claim-extraction, kb-support, scheduling, sql-analytics, ticket-routing
- held-out: meeting-actions, order-pricing, pii-redaction, refund-decisions, tool-calling

## Deliverable
`results/` with all prompts, outputs and grades. `REPORT.md` with the metrics table, per-task breakdown, CIs and the decision for each comparison. `CORRECTIONS.md` with every audit fix. The README is updated with the round-2 figures.

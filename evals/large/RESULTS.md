# Large tasks: generic request vs. skill-rewritten brief

**Question.** A developer types an ordinary request of about 100 words to a coding agent. Does it help to have the `prompt-writing-large-tasks` skill rewrite that request into a full brief first?

**Answer on these five tasks: no measurable effect on success, and about 35% higher cost.** Both arms passed all 75 of their runs. Every paired run scored identically. The skill arm cost $0.35 per run against $0.26, counting the one-off cost of writing the brief.

## Design

| | |
|---|---|
| Tasks | 5 self-contained projects with hidden graders: incident root cause from logs, messy-data report, multi-bug fix, API migration across 12 modules, performance rewrite |
| Arm "generic" | The agent receives `tasks/<id>/start_prompt.md` as written: 56–97 words, in an ordinary developer's voice |
| Arm "skill" | The same request, rewritten **once per task** by Claude Opus 5.5 with the skill loaded. The writer could read the project folder (read-only) and was told the agent's environment. The resulting briefs are 1,149–1,601 words (`prompts/`) |
| Agent | Claude Opus 5.5, medium effort, Claude Code headless, tools Bash/Read/Edit/Write/Glob/Grep, at most 40 turns |
| Runs | 15 per arm per task, 150 in total |
| Grading | Each task's hidden `grader.py`, run on the finished folder, re-scored at the end with the final graders (`run_large.py regrade`) |

## Results

| arm | runs | passed | pass rate, 95% CI | mean score | gaming | mean cost per run | mean minutes |
|---|---|---|---|---|---|---|---|
| generic | 75 | 75 | 100% (95.1–100) | 1.000 | 0 | $0.26 | 1.7 |
| skill | 75 | 75 | 100% (95.1–100) | 1.000 | 0 | $0.35 | 2.0 |

**Paired difference** (skill − generic, same task and run index, n = 75): exactly 0.

| task | arm | prompt words | passed | cost/run | minutes | turns* | output tokens* |
|---|---|---|---|---|---|---|---|
| api-migration | generic | 79 | 15/15 | $0.33 | 1.3 | 6.9 | 8,489 |
| | skill | 1,601 | 15/15 | $0.34 | 1.2 | 7.2 | 7,880 |
| bugfix-ledger | generic | 74 | 15/15 | $0.19 | 0.7 | 5.2 | 3,950 |
| | skill | 1,251 | 15/15 | $0.20 | 0.7 | 5.2 | 4,110 |
| data-report | generic | 97 | 15/15 | $0.34 | 1.2 | 7.1 | 7,664 |
| | skill | 1,461 | 15/15 | $0.52 | 2.7 | 8.1 | 12,568 |
| incident-logs | generic | 85 | 15/15 | $0.29 | 1.1 | 8.6 | 5,882 |
| | skill | 1,149 | 15/15 | $0.40 | 1.5 | 7.3 | 9,039 |
| perf-dedupe | generic | 56 | 15/15 | $0.17 | 4.0 | 7.3 | 3,790 |
| | skill | 1,449 | 15/15 | $0.29 | 4.1 | 10.9 | 6,320 |

The skill arm's cost includes the one-off cost of writing its brief, spread across the 15 runs. That cost was $0.20–$0.72 per task, over 9–14 turns. Full table: [`results/METRICS.md`](results/METRICS.md).

\* Turns and output tokens are averaged over runs with complete CLI metadata. Two skill-arm runs ended with a background job, and for those the CLI reported only the final exchange, so they are excluded from these two columns. Their grades and wall times are unaffected.

## Can the perfect scores be trusted?

An independent audit (`AUDIT_BRIEF.md`, notes and scripts in [`audit/`](audit/)) checked the graders and the results without seeing the scores first.

- **The results hold.** The auditor derived its own ground truth for every task: recomputed incident values; report scripts run on the hidden data and on a new tricky dataset; 783 migration replay scenarios against the original code; 20,000 currency conversions against an exact-arithmetic oracle; 48 extra deduplication datasets. It found **no failures in any of the 150 runs**.
- **Four of the five graders are lenient.** The auditor's own wrong solutions scored 1.0 on four tasks:
  - **api-migration:** mishandling of 3xx, 403 and 429 responses and of second-call failures.
  - **bugfix-ledger:** double rounding, float arithmetic, unrounded discounts.
  - **perf-dedupe:** missing fields, None values, non-ASCII digits.
  - **data-report:** default arguments, extra keys, non-stdlib imports.

  incident-logs was sound, with a minor gap in how it checks evidence. So the 150 perfect scores are confirmed by the independent checks, not by the graders alone. The graders need the auditor's fixes before this eval is reused.
- **One ungraded difference between the arms.** In bugfix-ledger, the input `--5` is parsed as 5.00 by the original code and the reference; the README arguably requires an error. 9 of 15 generic-arm agents made it raise an error, against 0 of 15 skill-arm agents. The skill's brief told the agent to change only what the bugs required, and that likely explains it. It's not one of the planted bugs and isn't scored.

## Corrections made during the run

- **api-migration grader.** It counted file paths mentioned anywhere in REPORT.md, including notes such as "app/settings.py was left untouched". That failed one check in 6 of the first 6 skill-arm runs and 1 of 6 generic-arm runs. After the fix, all runs were re-scored. See [`CORRECTIONS.md`](CORRECTIONS.md).

## What this means

- **On well-specified tasks that fit within 40 turns, Opus 5.5 doesn't need a long brief.** A 56–97-word request, backed by a README in the folder, was enough to succeed every time. The skill's brief added roughly 1,100–1,500 words and about $0.09 per run (+35%), and on two tasks it made the agent slower and more verbose, without changing a single outcome.
- **This doesn't show the skill is useless.** It shows these tasks don't need it. Every task here had its rules written down in the folder, so the brief's main extra value, filling in what the request leaves unstated, had nothing to fill. Places where a brief could still matter, none of them tested here:
  - tasks whose rules exist only in the developer's head;
  - longer horizons that exceed the turn budget;
  - weaker or cheaper agent models;
  - tasks where a tempting shortcut isn't caught by tests.

## Limitations

- **Five tasks, all at the ceiling.** With every run passing, the eval can't detect a difference smaller than its ceiling allows. The 95% interval on each arm's pass rate is 95–100%.
- **One brief per task.** The skill's output varies between writes, and this design holds it fixed, as requested.
- **One agent model and one effort level.**
- **The skill writer had read access to the folder.** This matches how the skill is meant to be used; its own cost is counted.

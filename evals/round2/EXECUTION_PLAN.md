# Round 2: execution plan

This file is written so a fresh Claude session, with no memory of how it was built, can pick up round 2 and finish it. Paste this into a new session, from the repo root:

> Read `evals/round2/EXECUTION_PLAN.md` and carry it out, starting from the first stage that isn't done.

---

## 1. Task

Find out which way of writing a system prompt makes Claude Opus 5.5 follow a user's intent most reliably, on tasks hard enough to tell the approaches apart. Then try to improve the winning skill without fooling ourselves.

The **contenders** are ways of producing a prompt. In every case, Opus 5.5 writes the prompt from the same user request:

| id | How the prompt is written |
|---|---|
| `v1` | with the skill in `comparison/skill-v1/SKILL.md`. The current recommended skill, also at `skills/prompt-writing/`. |
| `v2` | with `comparison/skill-v2/SKILL.md`, which is v1 plus a "Writing for current Claude models" section from Anthropic's Opus 5 prompting guide |
| `none` | with no skill |
| `v3` | with `comparison/skill-v3/SKILL.md`, which **you** write in stage 6 from training-task failures |
| `request` | no writer: the user's raw request text is used as the system prompt. This is a reference point and the gold audit. |

Round 1 (`evals/quality/`) found v1 ahead (99% vs 91% for no skill). But 4 of 5 tasks were at the ceiling, and the gain wasn't statistically solid. Round 2 exists to fix that, with harder tasks and more inputs.

## 2. How it is measured

All definitions live in `EVAL_PLAN.md` and are implemented in `report2.py`. Don't redefine them.

- **Task success (primary):** the share of a task's inputs whose output is fully correct. Computed per written prompt, then averaged over that contender's prompts, then averaged over tasks with equal weight (macro).
- Also reported: **format validity** (strict compliance with the requested output format), **hard-input success** (edge + adversarial inputs), **consistency** (std of success across a contender's prompts), **cost** (prompt words, downstream seconds).
- **95% CIs** come from a paired bootstrap that resamples prompts and inputs within each task.
- **Decision rules, fixed in advance:**
  - A beats B only if the CI of A − B excludes 0. Otherwise report "no detectable difference".
  - v3 replaces v1 only if it beats v1 on the **held-out tasks**.
  - The train/held-out split is fixed in `split.txt` (seed 42, drawn before any results):
    - train: claim-extraction, kb-support, scheduling, sql-analytics, ticket-routing
    - held-out: meeting-actions, order-pricing, pii-redaction, refund-decisions, tool-calling

## 3. What counts

- Grading is by code against gold answers computed when the inputs were generated. No model judge is used in round 2.
- **Any fix to a task, gold or grader is applied to every contender**, and logged in `CORRECTIONS.md` with the item id, what was wrong, and how it was fixed. Never change a task because of which contender it favours. Only change it because the gold or grader is wrong under the task's own REQUEST.
- Report everything, including results that make the skill look bad.
- **Out of scope:**
  - changing metric definitions or decision rules after seeing results;
  - adding inputs or tasks after seeing results, except to replace a task dropped in stage 3 at the ceiling;
  - using held-out task failures to write v3.

## 4. What you have

**Environment.** A Linux workspace with Python 3. The `claude` CLI is on PATH; every model call goes through it (`run2.py` handles flags: `--tools ""`, `--setting-sources ""`, `--disable-slash-commands`, and an empty working directory). No API key is needed.

**Files** (`evals/round2/`):

| Path | What it is |
|---|---|
| `EVAL_PLAN.md` | metric definitions, decision rules, budget |
| `tasks/common.py` | task contract + `selftest()` |
| `tasks/<task>.py` | one module per task: `ID`, `REQUEST`, `build()` → 50 items, `ideal_output()`, `grade()` |
| `tasks/BUILDER_BRIEF.md`, `tasks/briefs/brief_{A,B,C}.md` | the briefs used to build the tasks. Reuse them if a task module is missing or broken. |
| `run2.py` | writes prompts and runs them downstream. Everything is cached in `results/`, and a re-run resumes. |
| `report2.py` | grades cached outputs and writes `REPORT.md` + `results/metrics.json` |
| `split.txt` | the train/held-out split |

**The 10 tasks** (module → ID): `refund_decisions` → refund-decisions, `order_pricing`, `ticket_routing`, `sql_analytics`, `pii_redaction`, `claim_extraction`, `meeting_actions`, `kb_support`, `scheduling`, `tool_calling` (IDs use hyphens).

**Commands:**

```bash
cd evals/round2
python3 -c "from tasks import common, refund_decisions as m; print(common.selftest(m))"   # check a task
python3 run2.py pilot [--tasks a,b] [--conds v1,v2,none]      # 1 prompt/contender, 10 inputs/task
python3 run2.py wave --prompts 0,1 --tasks a,b [--conds ...]  # prompts k=0,1 on all 50 inputs
python3 run2.py audit --tasks a,b                             # raw request as prompt, all 50 inputs
python3 report2.py --conds v1,v2,none [--tasks a,b] [--min-prompts 2]
```

Run long commands in the background, redirecting output to a log.

**Budget: at most 3,000 downstream calls in total**, with the downstream model at **medium effort** (set in `run2.py`; don't change it). Count calls with `ls results/outputs | wc -l`. Writer calls (about 70) aren't part of that count.

**Timing, measured:**

| Call | Typical time |
|---|---|
| Downstream Opus 5.5 at low effort | ~30 s |
| Downstream Opus 5.5 at high effort | ~100 s |
| Downstream Opus 5.5 at medium effort | between those two |
| Writer call | 1–3 min |

With 24 workers, 1,000 downstream calls take roughly 30–45 minutes.

## 5. How to work: stages

Check what already exists before each stage. Every stage is resumable.

**Stage 1: tasks exist and pass selftest.**
Run selftest on all 10 modules. For any missing or failing module, build or fix it from `tasks/BUILDER_BRIEF.md` and the matching brief in `tasks/briefs/`. Then **hand-verify 5 edge or adversarial golds per task** against that task's REQUEST: re-derive the answer yourself from the rules as written. Log any fixes in `CORRECTIONS.md`.

**Stage 2: pilot.**
`python3 run2.py pilot` for all tasks: 10 inputs × 3 contenders × 1 prompt, about 330 calls including any already cached. Then `python3 report2.py`.
Read 2 failing outputs per task. A failure caused by the grader (harmless formatting, a wrong gold) is a task bug: fix it and log it. A failure caused by the answer is real.

**Stage 3: pick tasks.**
Keep tasks where at least one contender is below 100% in the pilot. Drop tasks where all three score 100%: they can't separate contenders. Aim for 6. If fewer than 4 remain, make dropped tasks harder (more interacting rules, more edge inputs), re-run selftest, and pilot again. Write the kept list and the reason for each drop into `CORRECTIONS.md`.

**Stage 4: main run.**
`python3 run2.py wave --prompts 0,1 --tasks <kept>`, about 1,650 calls. Prompt 0's pilot outputs are reused automatically.

**Stage 5: audit and correct.**
1. `python3 run2.py audit --tasks <kept>` (about 300 calls).
2. `python3 report2.py --conds v1,v2,none,request --tasks <kept> --min-prompts 1`.
3. For every input in "Inputs every prompt failed", decide whether the gold or grader is wrong under REQUEST. If so, fix it and log it. If not, keep it as a hard item.
4. For each task, read 3 outputs that `request` got right and a contender got wrong, and 3 the other way round. Confirm the grader is fair in both directions.
5. Re-run `report2.py`. Outputs are cached, so regrading is free.

**Stage 6: write v3 from training tasks only.**
1. Collect failures of v1, v2 and none on **train** tasks only.
2. Classify each failure by cause, for example: a rule omitted from the written prompt; a rule restated wrongly; precedence unclear; output format underspecified; no instruction for adversarial input; arithmetic or rounding left implicit; date resolution left implicit.
3. Count the causes. Look for causes that hit v1, and for what v2 or `request` did better.
4. Write `comparison/skill-v3/SKILL.md` as a copy of v1 plus the **general** lessons, phrased so they apply to any task. Never name a task, its rules or its data. Keep it under 120 lines. Explain each addition's reason in the skill itself.

**Stage 7: test v3 on held-out tasks.**
`python3 run2.py wave --prompts 0,1 --conds v3 --tasks <kept held-out tasks>`, about 300 calls.
Then `python3 report2.py --conds v3,v1,v2,none --tasks <kept held-out> --min-prompts 2`. Apply the decision rule. Also report v3 on train tasks if budget remains, but label it as training data.

**Stage 8: write up.**
1. Run the final `report2.py` for all kept tasks and contenders (`--conds v1,v2,none,request`), and the held-out comparison with v3.
2. Write `evals/round2/RESULTS.md`: headline table, by task, by difficulty, the paired-difference table with verdicts, the v3 decision, corrections made, limitations.
3. Add a round-2 results figure to `docs/readme-visuals.html`, matching the existing figure styles. Render it with the screenshot script described in `docs/README-figures.md`, or recreate it with Playwright and `/usr/bin/google-chrome`, viewport width 1220, device scale 2, screenshotting `#<figure-id>`.
4. Update `README.md` sections 6–8 with round-2 findings. Keep round 1 as history.
5. If v3 wins, copy it to `skills/prompt-writing/SKILL.md` and say so in the README. Otherwise leave v1.
6. Commit with a clear message, and push if a remote is configured.

**Known pitfalls, from round 1 and setup:**
- A copy of the skill installed in the Claude environment can interfere with tests that rely on the skill being picked up automatically. Round 2 passes the skill text directly to the writer, so it's unaffected.
- The CLI can inject account context into downstream replies (round 1 leaked an email once). If an output mentions the user's email or account, regenerate it: delete that output file and re-run the same command.
- `claude -p` refuses empty or whitespace-only user messages. Task inputs must be non-empty.
- Writers sometimes return clarifying questions instead of a prompt. `WRITER_SUFFIX` tells them to assume. If `results/prompts/*.json` has no `<final_prompt>` and looks like a question, delete it and re-run.
- `__ERROR__` outputs are retried automatically on the next run of the same command.
- Don't mistake "fewer format errors" for "more correct". Task success is the primary metric.
- With 2 prompts per contender, consistency is a weak signal. Say so.

## 6. Rules

**Not allowed:**
- going over 3,000 downstream calls;
- changing the downstream model or effort;
- changing metric definitions or decision rules;
- tuning tasks to favour a contender;
- using held-out failures for v3;
- deleting results to hide them;
- publishing anywhere public without the user's go-ahead.

**Allowed:**
- fixing genuinely wrong golds or graders (logged, applied to all);
- making ceiling tasks harder before stage 4;
- re-running cached commands;
- reading any output;
- writing helper scripts in `evals/round2/`;
- committing locally.

## 7. How the session ends

Done when stage 8 is complete, or the call budget is spent; in that case, write up whatever stages finished. The final message to the user covers:
1. the headline table: task success with CIs for each contender;
2. each paired comparison's verdict;
3. whether v3 replaced v1, and why;
4. the number of corrections made;
5. total downstream calls used;
6. where `RESULTS.md` and the updated README figure are.

Keep it under 250 words.

---

## Status log

Update this as stages finish (date, stage, one line, calls used so far).

- 2026-11-07: Plan fixed. `refund_decisions` task built and passing selftest. The other 9 tasks are being built from the briefs (check stage 1 for which exist).
- 2026-11-07: Refund pilot done (30 calls): v1, v2 and none all 100% on 10 inputs. The pipeline works end to end. Medium-effort downstream calls average **~14 s**, much faster than estimated, so time is not the constraint; the call budget is. Expect stage 3 to require making ceiling tasks harder, because Opus 5.5 handles straightforward rule sets well. Calls used: 30.

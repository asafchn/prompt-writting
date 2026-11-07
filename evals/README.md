# Evaluations

Two questions, two folders.

| Folder | Question | Status |
|---|---|---|
| [`quality/`](quality) | Do prompts written **with** the skill make the downstream model behave the way the user intended? | Done. Results in [`quality/results/summary.md`](quality/results/summary.md). |
| [`triggering/`](triggering) | Does Claude pick up the skill on its own when someone asks for a prompt without naming the skill? | Test set written; measurement paused (see below). |

## quality/: end-to-end prompt quality

A prompt is judged by what it makes another model do, not by how it reads.

1. **Write.** Claude Opus 5 receives 5 realistic requests (billing chatbot, review tagger, sales-email GPT, code-review bot, overnight ticket-triage agent). It writes each prompt 3 times under each condition: skill v1, skill v2, no skill. That makes 45 prompts.
2. **Run.** Each written prompt becomes the system prompt for Claude Haiku 5.5, which then handles 4 to 8 test inputs designed to probe the user's intent: a refund outside the window, a sarcastic review, a prompt-injection attempt inside a ticket, a diff with a bug hidden among formatting noise. If a prompt says inputs arrive wrapped in a tag (for example `<review>`), the harness wraps them that way.
3. **Grade.** Code checks where exactness is possible (valid JSON, same keys every time, allowed labels, word limit, banned words). Otherwise a blind Claude Opus 5 judge scores each output against a rubric written from the user's request, without knowing which condition produced it.
4. **Aggregate.** The unit is a written prompt (its pass rate over its test inputs), because inputs under one prompt aren't independent. Standard errors are over prompts; differences are paired by case.

Files:

- [`quality/cases.json`](quality/cases.json): requests, test inputs, rubrics and gold labels
- [`quality/run.py`](quality/run.py): write, run and grade (cached, so it's safe to re-run)
- [`quality/aggregate.py`](quality/aggregate.py): builds `results/summary.md`
- `quality/results/`: every written prompt, every downstream output, every grade

To reproduce (needs the `claude` CLI, logged in):

```bash
cd evals/quality
python run.py all --samples 3          # all three conditions
python aggregate.py                     # writes results/summary.md
```

Delete `results/` first for a fresh run; otherwise cached calls are reused.

### Corrections made after the first pass

All three were applied to every condition identically, and the regrade covered all conditions.

- **A test that wasn't clean.** The "clean" rename diff in the code-review case actually breaks callers who pass `s=` as a keyword. The rubric now accepts flagging that.
- **A debatable label.** "Arrived late but worth every penny" now accepts `pos` or `mixed`.
- **A harness leak.** In one downstream reply, account details from the CLI environment leaked in. That output was regenerated.

### Limitations

- 3 prompts per case per condition: small. Differences under about 10 points are within noise.
- 4 of 5 cases hit the ceiling for every condition and don't discriminate. Harder cases are needed.
- The skill was handed to the writer directly. This measures what the skill does once used, not whether it gets used.
- One downstream model (Haiku) and one judge (Opus).

## triggering/: does the skill fire on its own?

[`triggering/trigger-eval.json`](triggering/trigger-eval.json) has 20 test messages: 10 that should use the skill without naming it ("can you rewrite the system message for our billing chatbot…") and 10 near-misses that share words but need something else ("change my zsh prompt", "cover letter for a prompt-engineer role").

The first measurement was invalid: a copy of the skill already installed in the test environment competed with the test copy, and messages that mention a file sent Claude looking for it on disk first. It should be re-run in a clean environment with Anthropic's `skill-creator` description optimizer.

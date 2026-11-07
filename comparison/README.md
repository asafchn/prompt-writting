# Skill vs. skill vs. no skill

> [!NOTE]
> Round 2 (10 harder tasks, 50 inputs each, prompts run by Opus 5.5) found no accuracy difference between any of these. Every contender scored 99.8–100%. v3 matched them all with the shortest prompts. See [`../evals/round2/RESULTS.md`](../evals/round2/RESULTS.md). The tables below are round 1.

This folder holds the three contenders that were tested against each other, and real examples of what each one produced.

| Contender | What it is | Overall pass rate |
|---|---|---|
| [`skill-v1/`](skill-v1/SKILL.md) | The skill distilled from the Astra weight-editing prompt. Won round 1; the main skill until v3 replaced it. | **99% ± 1** |
| [`skill-v2/`](skill-v2/SKILL.md) | v1 plus a "Writing for current Claude models" section based on Anthropic's [Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5) guide. | 88% ± 6 |
| No skill | Same model (Claude Opus 5), same request, no skill loaded. The baseline. | 91% ± 5 |
| [`skill-v3/`](skill-v3/SKILL.md) | v1 plus a "keep it as short as the rules allow" section, written from round-2 training tasks. **The main skill**, identical to [`../skills/prompt-writing`](../skills/prompt-writing/SKILL.md). | n/a (round 2: 100%, 39% shorter prompts than v1) |

Pass rate = share of downstream test inputs handled correctly by a model (Claude Haiku 5.5) running the written prompt, averaged over 15 written prompts per contender. ± is one standard error. Full method: [`../evals/quality`](../evals/quality).

## Paired differences

Each pair compares prompts written for the same case.

| Comparison | Difference | Read it as |
|---|---|---|
| v1 minus no skill | +8.3 points ± 5.5 | Positive, about 1.5 standard errors. Suggestive, not proven. |
| v2 minus no skill | −2.1 points ± 6.6 | No measurable effect. |
| v2 minus v1 | −10.4 points ± 6.0 | v2 is likely worse on this test set. |

## Where the difference came from

Four of the five cases were at or near 100% for every contender, so they could not separate them. Almost all of the signal is in **sales-email**:

| sales-email | v1 | v2 | no skill |
|---|---|---|---|
| as graded | 100% | 58% | 58% |
| ignoring the "before you send" notes some prompts tell the bot to append | 100% | 75% | 67% |

v1's prompts made Haiku keep every email under 120 words with a single next step. v2's prompts more often led Haiku to add a call the rep's notes never mentioned.

v2 did show one real benefit. Its "ask for full coverage with severity labels, filter later" advice made the code-review bot flag a genuine compatibility break (renaming a parameter breaks keyword callers) that the narrower prompts tended to wave through. See [`sample-prompts/code-review-bot.md`](sample-prompts/code-review-bot.md).

## An important caveat about v2

The Opus 5 guide describes how **Opus 5 behaves when it runs a prompt**. In this test, the prompts were run by **Haiku**. So this test is not a fair verdict on that guide, only on adding it to this skill when the downstream model is smaller. Re-running with Opus 5 downstream is the obvious next experiment.

## Examples

- [`sample-prompts/sales-email.md`](sample-prompts/sales-email.md): the prompt each contender wrote for the sales-email custom GPT, and what Haiku wrote for the same demo notes.
- [`sample-prompts/code-review-bot.md`](sample-prompts/code-review-bot.md): the prompt each contender wrote for the code-review bot, and how each bot handled the rename diff.

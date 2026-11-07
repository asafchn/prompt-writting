---
name: prompt-writing-large-tasks
description: Write or review the brief for a large, autonomous task an AI agent will run on its own for many steps — tools, budgets, files, a deliverable at the end — using the seven-section structure of a proven agent brief.
---

# Prompt writing for large tasks

Use this when the prompt is a **brief for an agent that works alone over many steps**: it runs tools or code, reads and changes files, spends a budget (time, calls, runs, money), and hands back a deliverable that someone will judge. Examples: fix a failing test suite, migrate a codebase, investigate a bug, run an experiment, audit a system, produce a report from many sources, tune or repair a model.

Don't use it for one-shot prompts (a chatbot's system message, a classifier, a single rewrite). Those need a short prompt with a clear output contract, not this structure.

The structure comes from the task brief MIT CSAIL researchers gave an AI agent to repair a language model's weights on its own (`source/astra_exp8_p50c_prompt.txt` in this repository). Every section answers a question the agent would otherwise have to guess, and a wrong guess on a long task costs hours.

## 1. Gather what the brief needs

Get these before drafting. Take what you can from the conversation and the files, and ask only for what is missing and changes the brief:

- **The object of work**, exactly: which repository, system, data set or model, with the facts that matter (versions, sizes, layout).
- **The grading rule**: how the result will be judged, by whom or by what, and what stays fixed.
- **The resources**: tools and their exact interfaces, files and where they live, every budget with a number.
- **The limits**: what is off limits, and which shortcuts would technically pass but miss the intent.
- **The deliverable**: what exists when the agent is done, and what its final report says.

If the grading rule is unknown, say so and ask. A brief without one produces work that can't be judged.

## 2. The seven sections

Write them in this order. Each starts with its label in capitals followed by a full stop, then prose (`TASK. You are given…`). Use numbered lists only inside WHAT YOU HAVE and HOW TO WORK, where the content is a set of resources or a sequence of steps.

1. **TASK.** One paragraph: what the agent is given, stated with exact specifications, and what it must achieve. Name the object precisely (versions, sizes, structure), then the goal in one sentence, then the approach you expect in one clause ("find out what goes wrong… and repair it with targeted changes").

2. **HOW IT WILL BE MEASURED.** The full evaluation protocol: what is run, on what, with which fixed settings, and how the result is scored. State what cannot change. You may keep the test set hidden ("you never see these benchmarks"), but never the rule. An agent that knows the rule optimises for the right thing; one that knows the test set overfits to it.

3. **WHAT COUNTS.** What kind of solution you want, with **one concrete example** of an in-scope fix. Then what is out of scope and why, naming the specific shortcuts that would game the measure (global knobs, deleting the failing test, hard-coding answers, skipping the hard part). Say where a limit is **enforced by the tools** ("refused by save_edit"). Enforcement beats instruction.

4. **WHAT YOU HAVE.** A numbered list of every resource. For each, give:
   - what it is and where it lives (paths, read-only or read-write);
   - the libraries or commands available;
   - its exact call format (a JSON schema or a command line, with each field and its limits);
   - where results land and in what form;
   - its budget as a number (runs, seconds, memory, tokens, output size), and what happens at the limit (a restart, lost state).

   If an action is costly or slow, say how costly ("a generation pass takes up to about half an hour").

5. **HOW TO WORK.** A numbered method, in the order the agent should follow it. Usually: diagnose before changing anything; localise causes, not correlations; measure with enough power; plan the budget; work efficiently. Put the domain's known traps in the step where they bite, with the numbers that help (a standard error, a sample size, a threshold, an example split of the budget). Add operating hygiene for long runs: state the hypothesis of each step, print compact summaries, keep a notes file the agent can reread after a restart, and back up good intermediate results.

6. **RULES.** "Not allowed:" as a short lettered list of hard prohibitions, each specific. Then "Allowed:" in one sentence listing what is still fine, so the agent doesn't over-restrict itself.

7. **HOW THE SESSION RUNS.** What ends the session (budget spent, a time limit, a condition), what is submitted at the end (exact paths), and what the final message must contain (what was changed, the evidence, why it should help).

## 3. Writing rules

- **Numbers, not adjectives.** Every limit, budget, size and threshold is a number. "50 forward passes", not "a limited budget".
- **Exact interfaces.** Show the literal call format and the output paths. Don't describe a tool the agent then has to guess how to call.
- **Grading rule visible, test set hidden.**
- **Intent first, then the gaming.** Say what you want, then name the shortcuts that wouldn't count.
- **Reasons in a clause.** Give the reason for a rule where it isn't obvious ("correct answers come from easier and shorter problems"), in a clause, not a paragraph.
- **One example of a good approach.** Not a gallery.
- **Each rule once.** Put it in the section where it belongs. Don't restate the rules in a closing checklist.
- **Dense prose.** Write full sentences in paragraphs. The agent reads the whole brief once, at the start, and refers back to it, so completeness matters more than skimmability.

## 4. Check the draft

Before delivering, read the brief as the agent will, with no other context:

1. Can it start working without asking anything? If not, add what's missing.
2. Can it tell when it's done, and what to hand in?
3. For each budget: does it know the number and what one unit costs?
4. What is the cheapest way to score well without doing the task? Is that shortcut named in WHAT COUNTS or blocked in RULES?
5. Is any sentence there only because it sounds thorough? Cut it.

## 5. Output

Deliver the brief in one code block. After it, list in two or three lines the assumptions the user should confirm, especially any number you had to estimate.

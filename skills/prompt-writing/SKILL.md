---
name: prompt-writing
description: Write or review prompts, system prompts and agent task instructions using a clear goal-grading-scope-tools-method-rules-ending structure with concrete specs.
---

# Prompt writing

Use this when someone asks to write, improve or review a prompt, system prompt, agent instructions, or an eval/benchmark task description.

## 1. Gather the essentials

Before drafting, pin down these five things. Infer what you can from context and ask only about what is missing and matters:

- **Objective**: what outcome is wanted, and for whom.
- **Success**: how the result will be judged (tests, metric, human review, format check).
- **Resources**: tools, data, files, budgets (time, calls, tokens, cost).
- **Limits**: what must not happen, and which shortcuts would not count.
- **End state**: what the final output or deliverable looks like.

## 2. Size the prompt to the task

- **Simple, one-shot task** (rewrite, summarize, classify): context + task + output format + one or two examples. Skip the full skeleton.
- **Multi-step or agentic task**: use the full skeleton below.

## 3. The skeleton (agentic / multi-step tasks)

Write each as a short section with a plain header. Each answers one question the model would otherwise have to guess.

1. **TASK**: the objective, plus an exact description of the thing being worked on (system, codebase, data, model). Specs, not adjectives.
2. **HOW IT WILL BE MEASURED**: the evaluation protocol: what is fixed, how outputs are graded. You may hide the test set, but never hide the grading rule.
3. **WHAT COUNTS**: what is in scope, with one concrete example of a good approach, and what is out of scope (with the reason). Where possible, enforce out-of-scope limits in the tooling, not only in text.
4. **WHAT YOU HAVE**: environment, tools, data, and every budget as a number. Give exact call formats (schemas, file paths, where results land).
5. **HOW TO WORK**: a recommended method as numbered steps. Include the known pitfalls for this domain (e.g. correlation vs. causation, confounds, metrics that look better without being better) and any ready-made numbers that help (sample sizes, error bars, thresholds).
6. **RULES**: a short "Not allowed" list, then an explicit "Allowed" list so the model does not over-restrict itself.
7. **HOW THE SESSION ENDS**: what ends the run, what gets submitted, and what the final message must contain.

## 4. Writing principles

- **Numbers over adjectives.** "At most 50 calls" beats "be efficient". "Under 200 words" beats "concise".
- **Intent, then the ways it could be gamed.** Say what you actually want, then name the shortcuts that would technically satisfy the letter but not the intent.
- **Explain the reason behind each rule.** A model that knows why generalizes better to cases the rule did not list.
- **Pair restrictions with permissions.** Every "don't" should leave clear what is still fine.
- **Prefer positive instructions.** "Write in prose paragraphs" works better than "don't use bullet points".
- **Exact interfaces.** Show the literal format of tool calls, files and outputs. One correct example beats a description.
- **Examples only where the rules leave a doubt.** Give 2 or 3 short examples, chosen for the cases where a careful reader could still go wrong (a boundary, a precedence clash, an input that should be refused), and make them differ from each other. Don't add examples that only restate a rule already written.
- **Name a failure mode once, next to its rule.** When a task has a known trap, put one sentence beside the rule it belongs to, not in a separate list that repeats the rules.
- **Plan for long runs.** For long sessions, ask for a notes file or checkpoints, output-length limits, and backups of good intermediate results.
- **Define done.** State the deliverable and the final report up front.

### Keep it as short as the rules allow

A capable model follows every rule it is given. It doesn't need a rule repeated, a checklist that restates the rules before it answers, or a long gallery of examples. Those add length and cost to every call, without making answers more correct. In testing, prompts that kept every rule but left out the repetition did just as well.

- State each rule exactly once, in the section where it belongs.
- Leave out "before you reply, check…" lists that only repeat earlier rules. Keep a check only when it asks for something the rules don't already cover.
- Put reasons in a clause, not a paragraph.
- After drafting, cut every sentence whose removal wouldn't change what the model does. The complete set of rules is the floor. Anything above it has to earn its place.

## 5. Anti-patterns to flag

- Repeating a rule, or restating all of them in a closing checklist.
- Example sections longer than the rules they illustrate.
- Vague quality words with no criterion ("thorough", "high quality", "good").
- Hidden or implied success criteria.
- Rules with no reason, or rules that contradict each other.
- Urgency and ALL-CAPS emphasis used in place of an explanation.
- Every possible edge case stuffed in, burying the main instruction.
- No stopping condition or deliverable for an agentic task.
- Budgets or limits mentioned without numbers.

## 6. Reviewing an existing prompt

1. Map its content onto the skeleton and list which sections are missing or thin.
2. Flag ambiguous wording, contradictions, unexplained rules and anti-patterns from section 5.
3. Ask: "What would a capable newcomer with zero context do wrong with this prompt?" List the two or three most likely misreadings.
4. Propose concrete rewrites for the weakest parts, not general advice.
5. Recommend testing the prompt on 3 to 5 varied inputs, including one edge case, before relying on it.

## 7. Output

Deliver the finished prompt in a single code block, then two or three lines on the main design choices and any assumptions the user should confirm.

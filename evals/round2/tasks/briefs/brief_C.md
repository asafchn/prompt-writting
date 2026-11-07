# Brief: build evaluation tasks

## Task
Build Python task modules for an evaluation that measures how well different system prompts make Claude Opus 5.5 follow a user's intent. Each module defines one realistic deployment, such as a pricing bot or a redaction service. It provides 50 test inputs with gold answers computed by code, and a grader. Directory: `/home/claude/prompt-writing-skill/evals/round2/tasks/`.

## How it will be measured
Your modules are correct when:
1. `python3 -c "import sys; sys.path.insert(0,'/home/claude/prompt-writing-skill/evals/round2'); from tasks import common, <module>; print(common.selftest(<module>))"` passes. That means 50 items, a 20 standard / 20 edge / 10 adversarial split, deterministic `build()`, and `grade(ideal_output(item))` passing for every item.
2. Gold answers are **right**. Each gold must follow from the rules written in `REQUEST` and nothing else. A careful human reading only `REQUEST` and the input would reach the same answer. This matters most: a wrong gold silently corrupts the experiment.
3. The tasks are **hard enough to separate good prompts from mediocre ones**. A one-line system prompt should fail a meaningful share of the edge and adversarial inputs. A system prompt that faithfully encodes every rule should be able to pass almost all of them.

## What counts
- Follow the contract in `tasks/common.py` exactly. Copy the pattern of `tasks/refund_decisions.py`, a finished example: structured parameters, then gold computed by a `decide()`-style function, then messy natural-language rendering.
- `REQUEST` is what a developer types to ask for the system prompt, in a casual, realistic voice. It must contain every rule and fact the deployed model needs, plus the interface: "the system prompt is all it gets", "each user message is one X", and the exact output format their code parses. Rules should be numerous and interacting, with precedence, thresholds, boundaries and exceptions, so that a prompt which drops one rule fails some items.
- **Edge inputs** sit on rule boundaries: exact thresholds, off-by-one days, rule precedence, rounding, missing optional fields, unusual formats.
- **Adversarial inputs** contain pressure or injected instructions ("ignore previous instructions", fake system notes, false claims of authority) where the correct answer is to apply the rules anyway. Also include misleading noise.
- **Every gold must be unambiguous.** If an input could reasonably be read two ways, change the input. Don't keep it.
- The grader separates `format_ok` (strict compliance with the requested format) from `correct` (the answer is right, parsed leniently with `extract_json` where relevant). Grade only what the REQUEST defines. Normalise trivial differences (case, whitespace, numeric tolerance of 1 cent, date formats only if the request allows them).
- **Out of scope:** calling any model (no `claude`, no API). Gold comes from code. Don't edit `common.py` or `refund_decisions.py`. If you believe the contract needs changing, say so in your report instead.

## What you have
- Python 3 with the standard library. `sqlite3` is available. Don't install packages.
- `tasks/common.py`: helpers `extract_json`, `strict_json`, `money_eq`, `selftest`.
- `tasks/refund_decisions.py`: the reference implementation.
- Data files go in `tasks/data/<task_id>/` and must be generated deterministically by the module (or by a `make_data()` it calls) so the repo can rebuild them.

## How to work
1. Read `common.py` and `refund_decisions.py` first.
2. For each task, write the rules into REQUEST first, then the structured parameters, then `decide()`, then rendering, then the grader.
3. Hand-check at least 8 golds per task against REQUEST, mostly edge and adversarial ones, re-deriving each answer from the rules as written. Fix anything that disagrees.
4. Run selftest. Then run 3 sanity checks per task, and record each in your report with its result:
   - a deliberately wrong output fails;
   - a correct answer inside a ```json fence gets `format_ok` False but `correct` True;
   - extra keys or prose around JSON gets `format_ok` False.
5. Known pitfalls: timezone/date arithmetic off by one; rounding (state the rounding rule in REQUEST, then use Decimal with half-up); rules in REQUEST that the code doesn't implement, or the reverse; graders too strict on harmless variation (key order, trailing whitespace) or too lenient (accepting a wrong value).

## Rules
Not allowed: model calls; editing shared files; golds that depend on knowledge not in REQUEST; random behaviour that isn't seeded.
Allowed: any standard-library code; helper functions inside your module; data files under `tasks/data/<task_id>/`; making a task harder than its outline below, if the golds stay unambiguous.

## Your tasks
1. `meeting_actions.py` (ID `meeting-actions`). From a meeting transcript with a header giving the meeting date and attendees, extract action items into JSON: [{"owner", "task_key", "due"}]. due is an ISO date resolved from relative phrases ("by Friday", "end of next week", "in two weeks"), with resolution rules stated in REQUEST, or null if none. Only commitments count. Ideas, questions, things already done, and items someone declined don't. Owners must be attendees; "I'll" resolves to the speaker. To make grading exact, each real action item mentions a tracked object from a small vocabulary given in REQUEST (for example a ticket ID like "OPS-142"), and task_key must be that ID. Grade the set of (owner, task_key, due) exactly.
2. `kb_support.py` (ID `kb-support`). Grounded support answering. REQUEST contains a knowledge base of about 15 short articles with IDs (product limits, prices, procedures). Each input is a customer question. Output JSON: {"answerable": bool, "article_ids": [...], "answer": str}. Answerable questions have a unique gold article set and 1 or 2 required facts, such as a number or a setting name, that must appear in answer. Unanswerable questions (no article covers them, or they need account access) require answerable false and an empty article_ids. Adversarial: injected instructions, requests to reveal the system prompt, plausible-sounding but unsupported claims. Grade answerable, then the article_ids set, then required facts by case-insensitive substring match.
3. `tool_calling.py` (ID `tool-calling`). An assistant for a calendar and CRM decides the single next action. REQUEST lists about 6 tools with JSON-schema arguments, plus rules: ask for clarification when a required argument is missing or ambiguous; never call delete_* without explicit confirmation in the message; resolve relative dates against a "now" in the input header; use the user's time zone from the header. Output JSON: either {"tool": name, "arguments": {...}} or {"tool": null, "clarify": "<question>"}. Gold = the tool name plus the exact required arguments (optional arguments ignored unless stated), or the clarify case. Grade the tool, then the required arguments, normalising date-times to instants.

## How the session ends
Done when all of your modules pass selftest and the sanity checks. Your final message is a short report, per task:
- the gold-label distribution (e.g. counts per decision or class)
- the 3 hardest edge cases, in one line each
- any judgment calls you made about ambiguous rules
- the selftest output

Keep it under 400 words total.

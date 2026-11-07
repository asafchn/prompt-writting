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
{TASKS}

## How the session ends
Done when all of your modules pass selftest and the sanity checks. Your final message is a short report, per task:
- the gold-label distribution (e.g. counts per decision or class)
- the 3 hardest edge cases, in one line each
- any judgment calls you made about ambiguous rules
- the selftest output

Keep it under 400 words total.

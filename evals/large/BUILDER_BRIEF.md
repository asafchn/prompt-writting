TASK. Build evaluation tasks for an experiment that measures how well different written briefs steer an autonomous coding agent (Claude Opus 5.5, running headless with Bash, Read, Edit, Write, Glob and Grep tools, at most 40 turns) through a large task. Each task is a small, self-contained project folder that the agent receives as its working directory, plus a hidden grader that scores the folder after the agent stops. Build the tasks assigned to you at the end of this brief, under /home/claude/prompt-writing-skill/evals/large/tasks/<task_id>/.

HOW IT WILL BE MEASURED. Each task folder will be copied fresh for every agent run. An agent gets the copied `workspace/` as its current directory and either `start_prompt.md` itself or a longer brief that a prompt-writing skill wrote from it. When it stops, the harness runs `python3 grader.py <path-to-the-copied-workspace>` from the task folder. The grader prints one JSON object to stdout: {"score": <0.0-1.0>, "passed": <bool>, "checks": {<check name>: <bool>, ...}, "gaming": <bool>, "notes": "<one line>"}. Your tasks are correct when all five of these hold, and you must demonstrate each:
1. The untouched workspace scores clearly below 1.0, with `passed` false.
2. The reference solution in `reference/`, applied to a fresh copy of the workspace (`python3 reference/apply.py <workspace>`), scores 1.0 with `passed` true.
3. At least two plausible wrong or partial solutions score between those two, and `passed` is false.
4. Each listed gaming attempt is detected, with `gaming` true and `passed` false.
5. The grader is deterministic and finishes in under 60 seconds.

WHAT COUNTS. A good task takes a capable agent 15–35 tool calls. It has several independent parts (e.g. several bugs, many call sites, several required figures), so partial credit is meaningful and a sloppy agent misses some. It rewards understanding over pattern-matching, and it has at least one tempting shortcut that the grader catches. Example of the right difficulty: a package with 6 planted bugs where the visible tests catch 4, and the hidden tests catch all 6 plus the regressions a careless fix would introduce.

`start_prompt.md` is the only description of the task that anyone gets. The agent receives it directly in one experimental arm. In the other arm, a prompt-writing skill rewrites it into a longer brief after reading the workspace. Write it the way an ordinary developer would type a request to a coding agent:
- at most 100 words, in a casual voice, with no headings;
- the goal;
- what to hand in, including the exact labelled fields the grader parses in REPORT.md or answers.json (a grader can't read the agent's mind, so the field names must be stated);
- the facts the agent can't discover from the files, such as fixed currency rates and counting rules. Keep these to one short phrase each.

It must not mention the turn budget, the hidden tests' contents, or method tips; an ordinary request wouldn't. Everything else the agent needs must be discoverable from the workspace itself (a README, docstrings, data files). So put the house rules, counting rules and the definition of each figure into `workspace/README.md`, not into the prompt.

Out of scope: tasks that need packages beyond the Python 3 standard library, network access, more than 5 MB of files, or knowledge that neither start_prompt.md nor the workspace provides.

WHAT YOU HAVE.
1. This container: Python 3 with the standard library, Bash, and git. Don't install packages.
2. The output location /home/claude/prompt-writing-skill/evals/large/tasks/<task_id>/. Each task folder contains exactly these files (the six listed, plus `make_data.py` where data is generated):
   - `workspace/`: what the agent sees.
   - `grader.py`: the hidden grader. It uses only the standard library and takes the workspace path as its argument.
   - `hidden/`: hidden test files or expected values, read only by grader.py.
   - `reference/apply.py`: copies the reference solution into a given workspace.
   - `start_prompt.md`: the ordinary developer's request, as described under WHAT COUNTS.
   - `CHECKS.md`: the five checks from HOW IT WILL BE MEASURED, with their outputs pasted in.
3. Generate data files deterministically, from seeded code kept in the task folder as `make_data.py`, so the task can be rebuilt.

HOW TO WORK.
1. Design the task on paper first: the parts, what the grader checks for each part, and the shortcuts. Write `workspace/README.md` and `start_prompt.md` from that design, so they agree with the grader.
2. Build the workspace, then the reference solution, then the grader. Grade on behaviour and on exact deliverable fields, never on the wording of prose.
3. Detect gaming concretely:
   - Compare hashes of the visible test files and any data files the agent must not edit.
   - Scan for hard-coded expected values.
   - Run hidden inputs the agent never saw.
4. Run the five checks and paste their outputs into `CHECKS.md`. Fix anything that disagrees.
5. Known pitfalls:
   - A grader that imports workspace code can be fooled by a broken import that scores 0 for the wrong reason. Run each test in a subprocess with a timeout.
   - Floating-point comparisons need a stated tolerance, and so does the request.
   - Timing-based checks are noisy. Use generous thresholds, at least 5× between the slow and fast solutions, and take the median of 3 runs.

RULES. Not allowed:
(a) calling any language model;
(b) network access;
(c) editing files outside your own task folders;
(d) graders that depend on the wording of REPORT.md prose rather than on labelled fields.

Allowed: any standard-library code, helper modules inside the task folder, and making a task harder than its outline if every check still holds.

HOW THE SESSION RUNS. You are done when every task assigned to you has all its files and a `CHECKS.md` showing the five checks passing. Your final message is a report of at most 300 words. For each task, give:
- the parts the grader scores;
- the shortcuts it catches;
- the untouched, partial and reference scores;
- any judgment call you made.

YOUR TASKS.
{TASKS}

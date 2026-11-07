TASK. Audit the graders of a five-task evaluation and independently check a sample of its results. In the evaluation, an AI coding agent (Claude Opus 5.5) worked on five tasks, 150 runs in all. Every graded run scored 1.0. A perfect record can mean the tasks were solved, or that the graders are too lenient. Your job is to find out which, with evidence. Nobody involved wants a particular answer. Report what you find, including problems.

The five tasks live in /home/claude/prompt-writing-skill/evals/large/tasks/<task>/: api-migration, bugfix-ledger, data-report, incident-logs and perf-dedupe. Each holds:
- `workspace/`: what the agent received.
- `start_prompt.md`: the task request.
- `workspace/README.md`: the house rules, where present.
- `grader.py`: run as `python3 grader.py <workspace>`. It prints JSON with score, passed, checks, gaming and notes.
- `hidden/`: the grader's hidden data.
- `reference/apply.py`: the reference solution.
- `CHECKS.md`: the builder's own validation, including an appendix script that builds partial and gaming variants.

The agents' finished workspaces are in /tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/large-eval-runs/runs/<task>__<arm>__<n>/, where arm is `generic` or `skill` and n runs from 0 to 14.

HOW IT WILL BE MEASURED. Your report will decide whether the evaluation's numbers are published as they are, corrected, or withdrawn. It is judged on three things:
1. Every claim has evidence you produced: a command and its output, or a computed value.
2. You looked for leniency deliberately, not only at the happy path.
3. Your independent checks don't rely on the graders' own code.

WHAT COUNTS. In scope:
- **Grader validity, for each task.** Does it reject the untouched workspace, partial solutions and gaming attempts? Do its checks cover everything the request and README ask for? Try at least 2 wrong solutions of your own per task, beyond the builder's variants. Good examples: a solution that gets one hidden-only requirement wrong; a report with one field off by a plausible amount, such as a timestamp off by the payments log's 2-hour offset or a count that includes declined cards; a migration that drops `raise_for_status()` in one module.
- **Independent result checks.** Take a sample of 4 agent workspaces per task, 2 from each arm: runs 3 and 11 of `generic` and `skill`, 20 workspaces in all. Verify each against ground truth you derive yourself:
  - for the report tasks, recompute the true values with your own script, from the data and the rules in README.md;
  - for the code tasks, write your own extra test cases from the stated requirements and run them on the agent's code.

Out of scope: changing any grader, task file or agent workspace. Everything is read-only for you. Work on copies in /tmp/claude-0/-home-claude/4b99c7d5-3217-5d38-9c31-9b4690d1b13d/scratchpad/audit/.

WHAT YOU HAVE.
1. Bash, Python 3 with the standard library, and the file tools.
2. The folders listed under TASK.
3. Don't open /home/claude/prompt-writing-skill/evals/large/results/ or any `*.log` file until your independent checks are complete. They contain the graders' scores, and reading them first would bias you.

HOW TO WORK.
1. Read each task's start_prompt.md and README.md first, and list what a correct solution must do. Then read grader.py and compare it to that list. Note any requirement that the grader doesn't check, or checks loosely.
2. Re-run the builder's CHECKS.md appendix scripts on fresh copies, and confirm the untouched, partial, gaming and reference scores.
3. Build your own wrong solutions and grade them.
4. Run your independent checks on the 20 sampled workspaces.
5. Only then, compare your verdicts with the graders' scores for those runs, from results/runs/<task>__<arm>__<n>.json.
6. Keep notes in the audit folder as you go.

RULES. Not allowed:
(a) editing anything outside the audit folder;
(b) calling any language model;
(c) network access.

Allowed: running any grader or agent code on copies.

HOW THE SESSION RUNS. You are done when every task has a grader verdict and all 20 sampled workspaces have an independent verdict. Your final message, at most 500 words, gives:
- **For each task:** the grader verdict (sound, lenient, or broken), with the specific gaps you found, the wrong solutions you tried and the scores they got.
- **For the 20 workspaces:** a table with task, arm, run, your verdict (correct, or which requirement failed) and the grader's score.
- **Overall:** can the 150 perfect scores be trusted? If not, which ones, and what should change?

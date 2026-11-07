TASK. Your current directory is a small Python 3 package called `ledger`, written with the standard library only. It has five modules: `ledger/amounts.py` (`round_money`, `parse_amount`), `ledger/currency.py` (`_code`, `minor_units`, `convert`), `ledger/vat.py` (`vat_rate_for`, `vat_amount`, `add_vat`), `ledger/invoice.py` (`line_total`, `invoice_total`) and `ledger/dates.py` (`_check`, `days_in_range`, `in_period`, `month_bounds`). There is also an empty `ledger/__init__.py`, a test suite in `tests/` (`test_amounts.py`, `test_currency.py`, `test_vat.py`, `test_invoice.py`, `test_dates.py`) and a `README.md`. The "House rules" section of the README is the specification. Some tests fail now, and the code has more bugs that no test catches. Find every place where the code breaks the README rules, fix each one with a small targeted change to the source, and write a `REPORT.md` that lists the bugs you fixed.

HOW IT WILL BE MEASURED. Your work is graded in two ways. First, the existing suite must pass, run from the project root with `python3 -m unittest discover -s tests -t .`. The tests in `tests/` stay exactly as they are now. Second, a hidden test suite that you will never see checks every rule in the README: rounding, parsing, conversion, minor units, VAT lookup, invoice arithmetic and date ranges. It calls the public functions with the names and signatures they have today. `REPORT.md` is checked line by line against the real bugs in the original code. Each real bug that is fixed and reported counts in your favour. A line that reports something that wasn't a bug, or that describes the cause wrongly, counts against you. A bug that was fixed in the code but not reported, or reported but not fixed, is scored as missed.

WHAT COUNTS. A fix makes a function follow the README for every input the README covers, not only the inputs the current tests use. Here is an example of an in-scope fix. If a function looked up a table with the raw argument while the README says the lookup is case-insensitive, the fix is to normalise the argument the same way the rest of the module already does. Re-typing table values to match one test's expected output is not that fix. The following do not count, because they would pass the visible tests while the code stays wrong:
- special-casing the inputs the tests use;
- changing expected values or test files;
- editing the README to match the code;
- catching and swallowing exceptions;
- adding new behaviour the README does not ask for.

Where the README does not define an input, leave the current behaviour alone. An unasked-for change there is a risk and is not a bug fix. The one exception: a case that plainly contradicts a stated rule, for example a code path that leaves a negative amount positive, is in scope.

WHAT YOU HAVE.
1. The project folder, which is your current directory and is read-write. Everything you need is in the files listed under TASK. The package is small, about 150 lines of source, so read all of it.
2. Shell and file tools: Bash, Read, Edit, Write, Glob and Grep. Python 3 is available with the standard library only. There is no internet and no pip.
3. The test command: `python3 -m unittest discover -s tests -t .`. It runs in under a second. For more detail, add `-v`.
4. Ad-hoc checks. Run spec checks with `python3 -c "..."` from the project root, for example `python3 -c "from decimal import Decimal as D; from ledger.currency import convert; print(convert(D('100'),'eur','jpy'))"`. If you need a longer check script, put it outside the project (for example under `/tmp`) so it doesn't end up in the deliverable.
5. A budget of 40 turns, all told, including the final message. Running out ends the session with whatever is on disk. Nobody will answer questions, so when the README leaves something open, make the narrowest reasonable reading, apply it, and say so in your final message.

HOW TO WORK.
1. Read first, change nothing (about 3 turns). Read `README.md` and all five source modules, then run the test suite once and note which tests fail and why.
2. Audit each function against each rule, not only against the failing tests. For each README bullet or table, find the code that implements it and check it by hand on the README's own examples. Places that are easy to get wrong:
   - which way the rate table is quoted ("units of the currency per 1 EUR"), so which operation takes A to EUR and which takes EUR to B;
   - case-insensitivity and whitespace in every lookup, including helpers that the obvious entry point doesn't go through;
   - inclusive ranges at both ends;
   - every documented negative form (`-12.50`, `-$12.50`, `(12.50)`, `($1,200.00)`);
   - which amount VAT is charged on;
   - round-half-up away from zero for positive and negative values (`0.125 -> 0.13`, `2.675 -> 2.68`, `-0.005 -> -0.01`);
   - JPY having 0 decimals.
3. Before you edit, write down each suspected bug as file, function, cause and the input that shows it, and confirm it with a one-line `python3 -c` check. A suspicion that the check doesn't confirm is not a bug, so leave the code alone and leave it out of the report.
4. Fix each confirmed bug with the smallest change that makes the function follow the README. Keep the signatures, names and module structure. After each fix, re-run the check that showed the bug and the full test suite.
5. Finish with a sweep (about 3 turns). Run every README example, plus at least one case per rule that the visible tests don't cover, against the fixed code. Run the full suite one last time.
6. Keep a running list of confirmed bugs in your notes as you go. It becomes `REPORT.md`, so the report matches the fixes exactly. As a rough split of the budget: about 15 turns for reading and diagnosis, 15 for fixes and checks, and 10 kept back for the sweep, the report and slack.

RULES. Not allowed:
(a) modifying, adding, deleting or renaming anything under `tests/`;
(b) modifying `README.md`;
(c) changing public function names or signatures, or adding third-party dependencies;
(d) branching on specific test input values, or hard-coding expected results;
(e) leaving scratch files, check scripts or backups in the project folder.

Allowed: any edit to the five `ledger/*.py` modules that brings them in line with the README, including fixing private helpers; reading anything in the folder; running any Python or shell command; and writing temporary files outside the project.

HOW THE SESSION RUNS. The session ends when you send your final message, or when you hit the 40-turn limit. What is on disk at that moment is what gets graded: the fixed `ledger/*.py` files and a new `REPORT.md` in the project root.

`REPORT.md` holds one line per distinct bug and nothing else: no heading, no blank lines, no extra prose. Each line follows exactly this format: `BUG: <file>:<function> - <one-line cause>`. Here `<file>` is the path relative to the project root (for example `ledger/vat.py`) and `<function>` is the bare name of the function you changed (for example `vat_rate_for`). If one function had two independent causes, give it two lines.

Your final message must list each fix, with the input that showed the bug and the output before and after the fix. It must also say whether the full test suite passes, and name any reading of an ambiguous README rule that you chose.

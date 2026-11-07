# Large-task eval: corrections

## api-migration grader counted file paths mentioned anywhere in REPORT.md (found after 60 runs)

**Signal.** The skill arm failed `report_files_changed` in 6 of 6 runs, and the generic arm in 1 of 6.

**Cause.** The grader collected every `app/<name>.py` mention anywhere in REPORT.md. The skill-written brief asks for a Notes section, and the agents wrote notes such as "app/settings.py was left untouched". The grader read that as listing settings.py as a changed file. The files-changed lists themselves were correct.

**Fix.** Only list items that name a file count as listed, for example `- app/x.py` or ``- `app/x.py` (comment only)``. Untouched workspace: 0.0625. Reference: 1.0, passed. Every saved workspace was re-scored with the fixed grader (`python run_large.py regrade`), in both arms.

**Effect.** All 13 api-migration runs at the time of the fix pass in both arms. Before the fix, the skill arm scored 0.94 with 0 of 6 passing, and the generic arm 0.99 with 5 of 6 passing.

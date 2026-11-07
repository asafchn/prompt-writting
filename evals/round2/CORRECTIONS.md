# Round 2: corrections and plan changes

Every change made after the plan was written is listed here, with when and why. Fixes to tasks, golds or graders apply to all contenders.

## Plan changes

### 1. The raw-request reference is not a valid contender (after the pilot, before the main run)
With the user's request as its system prompt, Opus 5.5 often treats the request as addressed to itself and writes a system prompt instead of answering the case. That happened on 50–90% of pilot inputs (example: `meeting-actions__request__0__meeting-actions-00`). So `request` is excluded from all comparisons. Its outputs are used only as a gold-audit signal where they contain an answer.

### 2. Task selection by full screen instead of a 10-input pilot (after the pilot, before the main run)
In the pilot, v1, v2 and none scored 100% on all 7 tasks piloted: 210 graded outputs with zero failures. The plan's rule ("drop tasks where all contenders score 100% in the pilot") would have dropped every task. That would leave nothing to measure, and it would rest on just 10 inputs per task. Those inputs were the first 4 standard, 4 edge and 2 adversarial items, not the hardest ones.

The replacement procedure, fixed before any main-run results:
- **Screen:** prompt k=0 of each contender runs on all 50 inputs of every task. The pilot outputs are reused.
- **Wave 2:** prompt k=1 of each contender runs on all 50 inputs, but only for tasks where at least one contender failed at least one input in the screen.
- **v3** runs on held-out tasks that reached wave 2.
- **Budget cap unchanged:** at most 3,000 downstream calls.
- **Metrics and decision rules unchanged.** Tasks where every contender scores 100% on all 50 inputs are reported as "at ceiling".

## Task, gold and grader fixes

(none yet)

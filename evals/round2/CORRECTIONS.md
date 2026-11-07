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

### refund-decisions: contradictory and ambiguous inputs (found in the screen; all contenders affected)
**Signal.** Every contender answered `escalate` on items 07, 10, 34 and 35, where the gold said `approve`.

**Cause.** The generator produced inputs that contradict themselves or the policy:
- shipping charges on digital downloads (07, 34, 35);
- a "won't turn on" complaint for a wool overcoat (10);
- digital items showing a "delivered" date while the policy counts digital windows "from purchase" (07, 34);
- a downloaded digital item reported as defective (35). The policy doesn't say whether downloading blocks a defect refund, so it's ambiguous.

Escalating such cases to a human is a reasonable reading, so these items broke the rule that golds must be unambiguous. The contenders weren't at fault.

**Fix**, made in `tasks/refund_decisions.py` without changing the random draw sequence, so all other items are byte-identical:
- digital items have $0.00 shipping;
- defect complaints are phrased per category;
- digital items show "purchased (digital delivery, same day)" instead of "delivered";
- defective digital items are not downloaded.

**Effect.** Inputs 07, 08, 10, 18, 33, 34 and 35 changed; the gold changed only for 35 (from $95.99 to $89.00). The cached outputs of those items were deleted and regenerated for v1, v2 and none. REQUEST was not changed, so the written prompts stay valid.

**After the fix:** v1, v2 and none each score 50/50.

## Stage 6: how v3 was derived (training tasks only)

**Screen result on the 5 training tasks** (ticket-routing, sql-analytics, claim-extraction, kb-support, scheduling): **zero correctness failures** for v1, v2 and none (750 graded outputs). So there were no failures to learn from, and failure-driven lessons were impossible without peeking at held-out tasks.

**The signal that remained: cost.** v1's written prompts were the longest on every training task, about 26% more words than no-skill prompts on average (2,124 vs 1,689), with identical accuracy. Section-level breakdowns (sql-analytics, kb-support, ticket-routing) put the extra length in three places: longer example sections (837 vs 451, 516 vs 191 and 381 vs 200 words), a separate "mistakes this task usually produces" list, and a closing "before you reply, check" list that restates the rules.

**v3 = v1 plus a concision section.** It adds: state each rule once; give 2–3 examples only where the rules leave doubt; put each failure mode beside its rule; drop restating checklists; cut anything whose removal wouldn't change behaviour. No task, rule or data is named.

**Prediction recorded before the held-out run:** the same task success as v1 (the decision rule will likely say "no detectable difference"), with noticeably shorter prompts.

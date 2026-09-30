# Review convergence — Shared Reference

Single source of truth for **how many times a review gate re-runs**. Every command whose reviewer gate offers a fix cycle cites this file instead of stating a count of its own.

Read through the loader skill (`Skill(skill: "workflows-core:reference", args: "review-convergence")`).

## 1. The rule

**Re-review while the last pass's own fixes introduced something, and stop when they did not.** There is no maximum number of passes. Concretely, after each fix cycle:

1. Re-review.
2. If the new pass reports **any finding that the previous pass's fixes introduced** — a defect that did not exist before those edits — fix it and go to 1.
3. If it reports no such finding, stop. Remaining findings, however many, are pre-existing ones that this loop was never going to converge on; dispose of them by the command's own verdict rules (fix, defer to the final report, or record under the artifact's open-questions section).
4. **The user may decline another pass at any point**, and declining is a normal outcome, not an escalation. Offer it from the second pass onward, naming what the last pass found.

**Cost control belongs at step 4, not in a ceiling.** A ceiling binds precisely when the artifact is furthest from correct — the runs that need a third pass are the runs that got a lot wrong in the first two — so it withdraws review exactly where review is most needed. The user declining is the same saving with the decision in the right hands.

## 2. What "introduced by the previous pass's fixes" means

It is a **provenance** test, not a severity test. Ask of each finding in the new pass: *did the edits I just made create this?*

- **Yes → another pass is owed.** A criterion rewritten to satisfy one finding now contradicts a different section; a heading renamed to match a style rule now fails a structural lint; a scope sentence tightened to remove an ambiguity now excludes a user story.
- **No → it is pre-existing, and it does not compel another pass**, whatever its severity. A MAJOR the first pass raised and the fixes did not address is not a reason to loop; it is a reason to fix it or to record it.

**A finding that recurs after being fixed is neither** — it is oscillation. Where the same finding appears in two consecutive passes with a fix applied between them, stop looping and escalate it to the user with both the finding and what was tried. Two passes disagreeing about the same construct is a sign the finding or the format is wrong, not that a third edit will land.

## 3. A passing verdict carrying MAJOR findings

A `PASS WITH RECOMMENDATIONS` that carries MAJOR findings mandates no fix cycle — each command's own verdict rules say so, and this file does not change that. But it does settle the case that follows:

**If you fix a MAJOR under a passing verdict, you must re-review.** A voluntary fix is still an edit, and §1's provenance test applies to it exactly as to a mandated one. The reviewer approved the artifact it saw, not the artifact your fix produced.

**The measured harm.** On one PRD, `prd-reviewer` returned `PASS WITH RECOMMENDATIONS` with two MAJOR findings, both real. The orchestrator fixed both and skipped the re-review, on the reading that a passing verdict had already allowed it to proceed. One of those fixes introduced an acceptance criterion that contradicted the PRD's own Goal — a defect the reviewer never saw because the fix came after its only pass. It merged to the default branch, and undoing it cost a full `/prompt-grill-me` interrogation plus an entire `/update-prd` run.

## 4. Why the old rule was retired rather than rephrased

Every gate in this family used to read **"Cap: one fix cycle + one re-review"**. That is withdrawn, not reworded, because a fixed count cannot bound this process: fixes introduce defects at a rate comparable to the ones they resolve, so the number of passes a run needs is a property of the run and not of the policy.

It was demonstrated wrong twice, on the same PRD:

- **The `/create-prd` run above** — the cap's single allotted re-review was skipped under a passing verdict, and the defect that reached the default branch was introduced by the fix, exactly where the cap had nothing further to offer.
- **The `/update-prd` run that repaired it** — pass 1 raised five MAJOR findings; the fixes for those introduced a new MAJOR that pass 2 caught; pass 2's fixes introduced further inconsistencies that only a **third** pass caught. The third pass was not contractually available. The orchestrator improvised it as a user-facing menu option and the user chose it; had the cap been honoured, a known MAJOR would have shipped for the second time in the same document.

Both runs converged in the end. Neither converged in two passes, and nothing about either was unusual.

## 5. Reporting

The final report names **how many review passes ran** and why the loop ended — `converged` (a pass introduced nothing), `declined` (the user stopped it, with the last pass's findings named), or `oscillating` (§2's escalation). A run that took more passes than usual is a signal about the artifact, so the count is reported rather than smoothed away.

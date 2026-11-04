# Rulings — live-check round 2 fixes (LC12–LC28, D39)

The branch `fix/live-checks-r2` fixes every defect that the live checks of 2026-10-29 filed (`docs/superpowers/verification/2026-10-29-live-checks.md`). Its plan is `docs/superpowers/plans/2026-11-03-live-checks-r2-fixes.md`. Before execution, an Opus review returned the plan READY WITH CHANGES; its six MAJORs and its MINORs were folded into the plan.

The ledger itself, otherwise unchanged, is in `2026-11-04-live-checks-r2-fixes-ledger.md` beside this file. Where this summary and the ledger differ, the ledger's wording is the record.

## The user's decisions (2026-11-03)

| # | Decided |
|---|---|
| U1 | Fix all of LC12–LC28 in one batch, before the next live round. |
| U2 | LC17: `/specify` and `/design` ask the user about each decision-needing finding a review leaves open. The options are the reviewer's, plus *Leave it open*. |
| U3 | LC19: `/epics` recommends reading the default branch's tip by ref, without moving the checkout. |

## The controller's rulings

| # | Decided | Why | Cost if wrong |
|---|---|---|---|
| 1 | LC21's to-fix entry is deleted by Task 6 alone, once both of its sites are fixed. | An item is deleted whole. | A one-line move. |
| 2 | LC28 is fixed by reporting the session branch's creation: in the `Specs preflight:` line where the preflight's flush created it, and in the `Specs repo:` line otherwise. The creation is not deferred. | Deferral broke two things, reproduced old against new. A second clone stopped taking in `origin`'s session branch until it committed. `lift` on an absent branch skipped moves, so a handoff was refused after a session file was deleted by hand. | The local branch still appears, now explained. Deferral could return with a design of its own. |
| 3 | `/update-spec` joins `escalation-rules`' asking set by name. | It acts "exactly as `/specify` Phase 6 step 2 and the paragraphs after it say", so it would ask without being named, and an unnamed member is a drift. | One more command in the set. |
| 4 | Only a survivor of a command's triage is asked a decision question. One marked unverified is recorded or listed as before. | `escalation-rules` never applies an unverified finding, and asking one would mean an answer that could not be applied. | An unverified finding that the operator could have settled is listed, not asked. |
| 5 | `/design` asks every decision-needing finding, with no triage clause. | `/design` has no triage step — the controller's brief had wrongly said it does — and `escalation-rules`' "where the command triages" clauses already cover the difference. | None. |
| 6 | Task 5 also fixed the gaps its own implementer named, as LC14- and LC16-class defects found by this batch. (a) A path a check reverted or deleted is reported. (b) Lint, build, bisect and the bug-work repro are wrapped too. (c) A nested `$SPECS_PATH` has `--show-prefix` stripped before paths are compared, in `/ready`, `/conformance` and `/epics`. (d) `/epics`' pull-request body lists only handed-off edits. Task 6 takes `/document`'s "project root". | The same defect classes; the rule is to fix before push. | Task 5's scope grew. Each item was reviewed in its re-review. |
| 7 | The planner's repro is a check run before Pre-Phase 3.5 only. A re-plan's repro runs in the scratch checkout of `HEAD`, before or after the first edit. | `risk-planner.md:35`, the authority, says so. Four other texts were brought into line with it (`bug-diagnosis`, `implement` and its docs page, the rules map, `risk-planner.md:192`). | A re-plan's leftover in the working tree, if one ever arose, would go unread. |
| 8 | Under `/document`'s *Proceed anyway*, a page the writer wrote over the operator's uncommitted changes is committed whole. Phase 8.5's "somebody else's changes stay out" is narrowed to files that neither `doc-writer` nor `doc-fixer` wrote. | The option itself says "pre-existing changes will appear in the diff". | The operator's edits on a written page ship in the docs pull request, which that option already promised. |
| 9 | docs-workflows takes a minor bump, 1.32.0, not the plan's 1.31.2 (now 1.33.0, ruling 12). | Task 6 changed `/document`'s behaviour (the read before and after its maintenance agents, Phase 8.5's staging), not only a heading. | None. |
| 10 | Two narrow fix passes ran after the final review's one fix wave, each re-reviewed. | The user's rule is that every known defect is fixed before push. The skill allows one wave. | Two short dispatches. |
| 11 | The controller trimmed `.claude/rules/dev-workflows.md`'s bug-diagnosis line (20,136 → 19,998 characters) after the residual pass pushed it past the 20,000-character warning, with its "from the first edit" anchor made explicit. | A gate warning this batch caused; the compaction changes no meaning. | A controller edit that no subagent reviewed; the gate chain checked it. |
| 12 | On merging `main` after PRs #147 and #148 (D32 parts 4 and 5), which had taken `workflows-core` 1.76.0 and 1.77.0 and `docs-workflows` 1.32.0 and 1.32.1, this batch's releases were renumbered `workflows-core` 1.78.0 and `docs-workflows` 1.33.0. `product-workflows` 3.73.0, `dev-workflows` 4.58.0 and `security-workflows` 0.10.2 stand. The ledger and ruling 9 keep the numbers they were written with; on release numbers, this row is the record. | Two releases cannot share a number. | None. |

## Extensions of the user's rulings

- **LC17.** Besides `/specify` and `/design`, the asking set covers `/update-spec` (ruling 3) and `/create-prd`, `/update-prd` and `/create-ard`. Those three already asked; they gain:
  - the explicit *Leave it open*;
  - the one-question-per-finding shape;
  - the questions asked even where no edit-only finding is open;
  - the re-review offer after the questions.

  This gives one rule one shape. The `product-workflows` CHANGELOG and the pull request name the extension so the user can veto it.

## Deferred minor items, triaged at the final review

- `/frames` Phase 3 quotes `phase-handoff` §3.2's `./` rule rather than citing it, because `check-citations` forbids a §3.2 cite there. Acceptable: it is a git fact unlikely to drift.
- `/document`'s Phase 9 line for a path no agent returned is long, with a nested bracketed alternative. Acceptable: it has the same shape as `/epics`' and `/ready`'s lines.
- Every other deferred minor item was fixed before push.

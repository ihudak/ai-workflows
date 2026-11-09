# Rulings — live-check round 3 fixes (LC29–LC37, R1, K1–K5, K7)

The branch `fix/live-checks-r3` fixes every defect that the live checks of 2026-11-04 filed (`docs/superpowers/verification/2026-11-04-live-checks.md`), plus R1 and five more known bugs from that round's runs. Its plan is `docs/superpowers/plans/2026-11-08-live-checks-r3-fixes.md`.

**Review history.**
- **The plan.** Before execution, an Opus review returned the plan READY WITH CHANGES (11 Major, 12 Minor, 8 Nit), and a scoped re-review left 7 Minor and 1 Nit. All of them are folded into the plan.
- **Each task** was reviewed on its own, and each fix round had a scoped re-review.
- **The final whole-branch review** returned "ready to merge with fixes": no Critical or Important finding, 6 new Minor, and 27 of 33 deferred minors to fix. Three fix passes followed, each with a scoped re-review.

The ledger itself, otherwise unchanged, is in `2026-11-08-live-checks-r3-fixes-ledger.md` beside this file. Where this summary and the ledger differ, the ledger's wording is the record.

## The user's decisions (2026-11-08)

| # | Decided |
|---|---|
| U1 | **LC31:** the two preflight prints go into GIT-G1's design as required outputs of its script: the session branch's creation line, and G1's notice at detection. This batch fixes only LC31's third case, `/specify`'s Final report. |
| U2 | **LC36:** after the review cap is spent, `/design`, `/specify` and `/update-spec` dispatch `overlap-reader` over the edits made after the last review. `/epics` keeps reporting them. |
| U3 | **R1:** `/implement` recommends *Revise the plan* where the finding contradicts neither `design.md` nor the specification. |
| U4 | **LC34:** one script in `workflows-core`, copied into `dev-workflows`, `product-workflows` and `docs-workflows`, with a CI check that the copies are equal. |
| U5 | **Every known bug** is fixed before the push. |

## The plan's calls, kept through its two reviews

| # | Decided |
|---|---|
| P1 | **LC33.** `/epics`' refresh rule moves into a shared reference, `workflows-core:scan-refresh`, which every scanning command cites. Copying it into four more commands would recreate the drift GIT-G1 exists to remove. |
| P2 | **LC37.** A sentence the writing adds that states a fact about the existing system goes to the whole-artifact gate. That covers a premise, a provenance line, or what changed between scanned commits. A confirmed fix applied to every occurrence is not a change. |
| P3 | **K5.** `readiness-reviewer` reads what its brief and `derived_phase` name, and the `dev-workflows/` bookkeeping. It reads nothing in a code repository, and reports a fact it cannot see as unverified. |
| P4 | **K2.** The marker cap ranks highest severity first, then by the order the review listed the findings. |
| P5 | **K1.** `run-state.py append` refuses an array value with exit 2, rather than extending the list with it. |
| P6 | **K4.** "The folder read" is the orchestrator's inline work in every command. Its routing lines are residue of `68c26cf80` and are removed family-wide. |
| P7 | **Not taken:** K6, K8 and K9. The plan's K table gives each one's reason: the shipped text already answers it, and the run slipped against it. |

## The controller's rulings

| # | Decided | Why | Cost if wrong |
|---|---|---|---|
| 1 | `/implement`'s *Install them now* read stays hand-written, renamed so it is not "a snapshot". `code-handoff` §2.2 names exactly the reads the script takes. | The read is tracked-only, and the script has no such mode. An untracked-inclusive read would misread every file an install creates. | One hand-written `-z` read stays, at one site. |
| 2 | Task 2's minors and Task 3's minors went into their fix rounds with the Important findings. | U5, and the implementer holds the context then. | A larger fix diff to re-review. |
| 3 | `ard-reviewer` gets each repository's scanned commit and read mode in its brief. It also gets the three write-free git reads `design-reviewer` uses, with `Bash` added for those alone. | After a read by ref, a working-tree existence check raises false "fabricated" BLOCKERs. | One agent gains `Bash`, its use stated as read-only. |
| 4 | `/docs-audit`'s `REFRESH_BLOCKED` question after a read by ref leaves out *Continue with current local state*. | Its coverage denominator must be the default branch as shipped. | One fewer way past a blocked refresh. *Skip* and *Cancel* remain. |
| 5 | Tasks 8 and 10 were dispatched as one batch, with two commits. | Both are small wording additions in disjoint regions. | One combined review instead of two. |
| 6 | `main` moved during the run (PR #177, `/conformance` Plan 2). It was merged in as its own reviewed step before the release task, and the versions moved up to `workflows-core` 1.80.0, `dev-workflows` 4.61.0, `product-workflows` 3.79.0, `docs-workflows` 1.37.0 and `security-workflows` 0.11.0. | The CHANGELOG sections and the coupling bullet must sit on top of `main`'s release. | A re-bump at pull-request time. |
| 7 | The merge leaves the PRD's `_conformance.md` out of `readiness-reviewer`'s read scope. The final pass applies that to the whole scope. | `main` reads that record only from the default branch, never from the working tree. | The reviewer cannot see a working-tree-only conformance record, which `main` says it must never read anyway. |
| 8 | Six of the 33 deferred minors are parked as not defects: #2, #3, #14, #15, #16 and #17. #2 and #3 are folded into the script edit as style and as a test. | The final review showed each is already answered by the shipped text, or is not two copies of one claim. The ledger gives each one's reason. | A wording nit left as it is. |
| 9 | There were two more fix passes after the single final wave the skill allows. | U5 overrides the limit. The first extra pass fixed a correctness hazard: `tree-snapshot.py` returned `-` with exit 0 when starting git failed. | Two more cheap re-reviews. |
| 10 | **R1's ARD arm.** Where a plan-conflict fix contradicts an `[AD#N]` Rule, the question says that the re-review, where it runs, will block unless the departure is recorded. *Apply the fix, keep the plan text* records the `- ARD deviation:` line, and every `code-review` brief now carries `ard_deviations`. | The user must not be steered into a block they were not told about. Passing recorded deviations also fixes a latent bug: deviations the run itself recorded used to reach the reviewer as BLOCKERs. | One more deviation record per such run. |

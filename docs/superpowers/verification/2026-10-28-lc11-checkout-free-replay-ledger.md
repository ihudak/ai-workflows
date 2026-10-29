# SDD ledger — LC11, the checkout-free replay

Branch `iv-gu/lc11-design`, plugin text final at `1922b045`, on base `2430bfa3` (`origin/main` after its last merge into the branch), copied here before the branch merged to `main`. Plan `docs/superpowers/plans/2026-10-28-lc11-checkout-free-replay.md`, spec `docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md`. Companion to `2026-10-28-lc11-checkout-free-replay-rulings.md`, which lists the rulings below in a table, and to `2026-10-27-lc11-measurements/README.md`, whose *Build results* section is the verification record.

The branch was executed with `superpowers:subagent-driven-development`. That skill keeps its ledger in a git-ignored scratch directory and deletes it when the branch finishes, so it is copied here unchanged: every task, review and fix round, and every ruling, in the order the controller wrote them, up to the line before the merge. Where a ruling and the shipped text disagree, **the shipped text is the authority**; a few rulings were superseded later, and the later entry is in the ledger too.

The paths it names under `.superpowers/sdd/` and `scratchpad/` were scratch and are removed after the merge. The commits it names on this branch stay reachable from `main` through the merge's second parent once the branch merges with `--no-ff`. The ledger is in a code block because it uses bare placeholders such as `<branch>` that Markdown would drop.

```text
# SDD ledger — plan: docs/superpowers/plans/2026-10-28-lc11-checkout-free-replay.md

BASE for Task 1: 6d666c27 (plan commit). Spec approved by the user 2026-10-28. Plan reviewed by Opus (READY WITH CHANGES, folded in).

Task 1: dispatched implementer (opus, id a3db889ff96a8689c)
Task 1: implementer DONE_WITH_CONCERNS f35ebae7 (selftest 204/0); task review dispatched (opus)
Task 1: review Needs fixes (Important: mixed line endings double → guard refuses; Minors: shared add/add test, separator stacking, dedupe within theirs). Ruling: guard in the function, take all minors. Fix round 1 sent to implementer.
Task 1: fix round 1 → b5f1947e (215/0); scoped re-review sent.
Task 1: complete (Approved at b5f1947e; selftest 215/0)
BASE for Task 2: b5f1947e
Task 2: dispatched implementer (opus, id a8fb3595c7cca13b9); Task 1 reviewer id aa968d9a8c6e4c374
Task 2: implementer DONE_WITH_CONCERNS 20e372fd (247 checks). Rulings: (1) restore-then-edit keeps branch-only entries (keep_branch_only; visible duplicate over silent loss); (2) deviations accepted; (3) environment.md accepted; (4) fix worktree_blob autocrlf via diff-files/index blob; (5) sync.conflict names source + conditional "next run pushes" text. Sent as fix round before review.
Task 2: fix round 1 → c0f5e905 (262). Concern: remedy for stuck two-clone push did not work (entry missing from both sides refused). Ruling: entry_set_merge refuses only one-side removal (agreed removal accepted) + spec §3.3 sentence amended; short remedy in §6. Fix round 2 sent.
Task 2: fix round 2 → 79c4e21f (269): agreed removal accepted; both-sides different edit keeps both (visible duplicate); short remedy in §6. Task review dispatched over b5f1947e..79c4e21f.
Task 2: review (aec69f3eb0116a2b5) Needs fixes: I1 CRLF regression in keep_branch_only; I2 follow-ups restore-then-edit drops session-only tasks; I3 unsettled remedy false; minors 1-5 (doc ruling 6 consequences, b1==b2 skip, sentence, spec §3.8). Ruling 6 judged right. Fix round 3 sent (all taken).
Task 2: fix round 3 → 381df9a1 (279). Scoped re-review sent.
Task 2: re-review of 381df9a1 Needs fixes: NEW Important — I2 fix doubles CRLF follow-ups.md (union_lines no form guard; also settle() lines branch); minors: remedy narrowing wording (HEAD not <default>), spec §3.3 followup-emission claim false, plan step 5 history. Fix round 4 → FRESH implementer a8595f91ba02c5d8a (brief task-2-fix4-brief.md, report task-2-fix4-report.md). Then confirm by aec69f3eb0116a2b5.
Task 2: fix round 4 → a0b1e2dc (289). Confirm sent to aec69f3eb0116a2b5. Note for Task 6: rationale.md:470 union account stale.
Task 2: confirm of a0b1e2dc: Important resolved, placement judged right; new Minor: no-EOL single-line follow-ups read as mixed form. Fix round 5 (one line) sent to a8595f91ba02c5d8a.
Task 2: fix round 5 → 0ac1f65e (295): no-EOL reads as LF. Implementer found union_lines doubles a last line without final newline (git behaviour, pre-existing). Breaker ruling (R=5): fix it (tiny, a known doubling) → sent; then ONE combined short confirm by aec69f3eb0116a2b5 over a0b1e2dc..tip.
Task 2: newline fix → ba47f7c8 (302). Combined confirm sent (a0b1e2dc..ba47f7c8).
Task 2: complete (Approved at ba47f7c8; selftest 302/0)
BASE for Task 3: ba47f7c8
Task 3: dispatched implementer (opus, id a0344df54da0950cb); Task 2 reviewer aec69f3eb0116a2b5; Task 2 fix-round-4+ implementer a8595f91ba02c5d8a
Task 3: implementer DONE_WITH_CONCERNS 4d5bfa5e (594 checks incl. 4 attribute variants). Task review dispatched (abe099a44c40f98da).
Task 3: review Needs fixes: Important rename detection publishes at paths run never wrote → guard final tree paths ⊆ c paths + rebuilt register files. Ruling: onto-deleted whole-shape + c modified → refuse. Minor: rename loop var. Fix round 1 sent. NOTES FOR TASK 4 BRIEF: tip None on refusal; numbers keyed by slug; root/merge commits must be filtered by §3.1 cond 6 before replay_commits (it raises NotRun); 420 s margin covers rebuilds.
Task 3: fix round 1 → 98348fba (650). Remaining slip: new file in a new subfolder of a renamed folder. Ruling: refuse where c adds under a directory that existed at p and holds no file at onto. Fix round 2 sent.
Task 3: fix round 2 → b845f9f2 (706): removed-folder rule; stray check before rebuild (register exception removed as dead). Concern: emptied dev-workflows-cost/ refuses. Ruling: rule only for ancestors under specs|specifications|vis not in/below dev-workflows/. Fix round 3 sent; then one confirm by abe099a44c40f98da over 4d5bfa5e..tip.
Task 3: fix round 3 → 8159b87f (754). Accepted residue: non-spec folder renames rely on git rename handling. Confirm sent to abe099a44c40f98da over 4d5bfa5e..8159b87f.
Task 3: complete (Approved at 8159b87f; 754 checks). Observation for Task 4 notes: a teammate deleting a whole security/<slug>/ while a scan adds a record → replay brings it back with only the run record (accepted non-spec residue).
BASE for Task 4: 8159b87f
Task 4: dispatched implementer (opus, id aee16e56baefbe7c3); Task 3 implementer a0344df54da0950cb, reviewer abe099a44c40f98da
Task 4: implementer DONE_WITH_CONCERNS 63ab29f9 (805). Concern: 420 s has no margin (60+10 grace per call ×6 = 420) → my ruling for Task 5: Bash timeout 480000 ms; plan constraint to update. Task review dispatched (acc3afb57002935d5).
Task 4: review Needs fixes: I1 ignored-file overwrite guarded only by untested precheck; I2 stale ref lock misreported as branch-moved; I3 time figure → RULING KILL_AFTER=2 (bounded-run), keep 420 s (supersedes my 480 note). Minors 4–10 all taken. Fix round 1 sent.
Task 4: fix round 1 → b36ad907 (823); new reason cannot-move; _undo_partial for partial read-tree; signals held around move_branch. Confirm sent to acc3afb57002935d5.
Task 4: confirm APPROVED b36ad907; two Minor defects (signal after read-tree wrote index → reverse read-tree by index evidence; exec bit in _undo_partial) → fix round 2 sent; then a one-line confirm.
Task 4: fix round 2 → 430e9233 (825). One-line confirm sent.
Task 4: one-line confirm of 430e9233: files fixed; symlinks not (worktree_blob follows links) → fix round 3 sent.
Task 4: fix round 3 → 8daecc12 (826): _link_aware_blob. Ruling: the same link blind spot in Task 2 code (worktree_blob in commit/unpreserved/align/put_back; a symlinked session file recorded as deletion) LEFT — population none (no run writes a session file as a link); note it in the verification record. Confirm sent.
Task 4: complete (Approved at 8daecc12; 826 checks)
BASE for Task 5: 8daecc12
Task 5: dispatched implementer (opus, id a2cedd2f633619d1f); Task 4 implementer aee16e56baefbe7c3, reviewer acc3afb57002935d5
Task 5: implementer DONE_WITH_CONCERNS f54855fb (gates pass; rules file 18,714). Departures: replayed-empty checked before moved (new §6 row 'already there'); rule 4 exception wording; session-branch push-rejected override scoped to the session branch's push; pointer fixes; scan Ending early passes register_rebuild. Concern: replay() porcelain not cleared between attempts → RULING: clear it per attempt (script, tiny) in the fix round. Task review dispatched.
Task 5: task reviewer dispatched (opus, id adc30848f170c2bbf) over 8daecc12..f54855fb; review → task-5-review.md
Note: main at af0020fa (#122 B23, #123 B24: core 1.65.1, dev 4.48.1, product 3.57.0; security 0.6.0). Ruling: merge main into iv-gu/lc11-design after Task 5 is approved, before Task 6 (Task 6 edits CHANGELOGs/manifests). LC11 versions stay core 1.66.0, security 0.7.0.
Task 5: review (adc30848f170c2bbf) APPROVED with 8 Minors (partial-JSON pushed:true row; checked-out remedy; already-there moves; CLAUDE.md extent vs 11 command copies; after-each-pull copies; rule 4 pointer + read-tree misattribution; conflict/would-overwrite clauses + refused-form variants; 420 s wording). Ruling: take all 8 + porcelain reset per attempt (script). Fix round 1 sent to a2cedd2f633619d1f; then confirm by adc30848f170c2bbf.
Task 5: fix round 1 → c42f31bf (828; gates pass). Task 6 carry: security-workflows docs scan.md:160, security-register.md:35 'or each replay'. Confirm sent to adc30848f170c2bbf.
Task 5: confirm of c42f31bf APPROVED; 3 new wording Minors (N1 anchor '; run git'; N2 flush paragraph switch exception; N3 rule 4 antecedent). Fix round 2 sent to a2cedd2f633619d1f; then one-line confirm.
Task 5: fix round 2 → 34ac2448 (gates pass). One-line confirm sent.
Task 5: complete (Approved at 34ac2448; selftest 828/0)
Merged origin/main (af0020fa) → 1bb6d9c9; parts fresh; full chain CHAIN_EXIT=0; ASSERT_PUBLISHED check-docs 0; selftest PASS.
BASE for Task 6: 1bb6d9c9
Task 6: dispatched implementer (opus, id a6d28ee62180c2460); Task 5 implementer a2cedd2f633619d1f, reviewer adc30848f170c2bbf. Gate chain script: scratchpad/lc11-chain.sh
Task 6: implementer DONE_WITH_CONCERNS 892dbf12 (chain 0, AP 0). Concerns: D27 (to-fix, addressed to the LC11 owner of specs-repo-git) and README git 2.40 for replay. Ruling: LC11 takes both (fix-known-bugs rule; D27 assigned here) → follow-up sent to a6d28ee62180c2460 before the task review; review range will be 1bb6d9c9..tip.
Task 6: follow-up → f3ab40aa (D27 + README; dev 4.49.0, product 3.58.0 for docs pages; chain 0, AP 0). Task review dispatched over 1bb6d9c9..f3ab40aa.
Task 6: task reviewer dispatched (opus, id acedfe0e6c77a9e4e) → task-6-review.md
Note: main at 2430bfa3 (#124 B25: core 1.66.0, product 3.58.0, dev 4.48.2) → LC11 renumbers at integration: core 1.67.0, product 3.59.0, dev 4.49.0 (ok), security 0.7.0 (ok); coupling bullets + CHANGELOG headings + any text naming 1.66.0 follow.
Task 6: review (acedfe0e6c77a9e4e) Needs fixes: Important to-test LC11-2 block order wrong (§8.2 step 3 puts session branch first); Minors: §3.7 setter copy stale; Stop trigger too narrow (§3.1 + dev/product CHANGELOG); coupling/CHANGELOG say resume pages cite §3.1; session-hygiene §6 redundant sentence. Ruling: take all. Fix round 1 sent to a6d28ee62180c2460.
Task 6: fix round 1 → c4d9a1fd (chain 0, AP 0). Confirm sent to acedfe0e6c77a9e4e.
Task 6: confirm of c4d9a1fd APPROVED (timing step verified); new Minor: unreadable/missing clause applies only at §6 points 2–3 (5 copies). Fix round 2 sent; then one-line confirm.
Task 6: fix round 2 → 5224b553: five identical insertions of the reviewer's own wording (', at the last two,'); controller verified the word diff — Ruling: no separate confirm; the whole-branch review covers it. Task 6: complete (Approved; chain 0, AP 0).
Integration: merged origin/main 2430bfa3 → 4c06b91c; renumbered LC11 to core 1.67.0, product 3.59.0 (dev 4.49.0, security 0.7.0 stand); chain 0, AP 0. NEXT: whole-branch Opus review origin/main..4c06b91c.
Final whole-branch review dispatched (opus, id a779e8aeb9a633a97) over 2430bfa3..4c06b91c → final-review.md
Final review (a779e8aeb9a633a97): READY WITH FIXES — Important: here decided before replay, switch during replay → move writes into another branch's checkout (measured). Minors: session-branch remedy needs lift/put-back; no row for harness 420 s timeout; 'overwritten taken whole' copies not narrowed (refuse where origin deleted); spec §4 autoStash selftest not built. Ruling: take all; ONE fix dispatch to Task 4 implementer aee16e56baefbe7c3 (report final-fix-report.md); then scoped re-review by a779e8aeb9a633a97. Declined list accepted as written.
Final fix → 938fef49 (842; chain 0, AP 0): new reason checkout-moved (no hand remedy; 7 copies of 'push-rejected advises pull' narrowed), here re-read, look under HEAD.lock, not-here re-check (residual one-pipe-write window), lift/put-back remedy, harness-timeout sentence, deleted-file narrowing, autostash selftest. Scoped re-review sent to a779e8aeb9a633a97.
Final re-review of 938fef49: READY WITH FIXES — 4 wording Minors (names-what-to-run copies ×2; rule 4 not-here window; 'not moved again'; timeout/:929 retry qualified by guards). Ruling: take all; sent to aee16e56baefbe7c3; then one-line confirm by a779e8aeb9a633a97.
Final wording fix → 428980c5 (chain 0, AP 0). Implementer found 5 pre-existing 'the next run retries' copies with the same imprecision → Ruling: fix ('a later run'), sweep incl. docs pages; then one confirm over 938fef49..tip.
Final 'later run' fix → ca4aa3d8 (10 copies; chain 0, AP 0). Confirm sent to a779e8aeb9a633a97 over 938fef49..ca4aa3d8.
Final confirm of ca4aa3d8: READY WITH FIXES — 3 one-clause Minors (would-overwrite on <branch>; two-clone remedy 'a later run'; CHANGELOG list). Ruling: controller fixes them directly (one-clause, stops the churn) → 1922b045; chain 0, AP 0; one-line confirm sent to a779e8aeb9a633a97.
Final confirm of 1922b045: READY TO MERGE (a779e8aeb9a633a97). NEXT: verification record (README build results + ledger + rulings), gates, ask user to push.
Verification record: measurements README extended with build results (842 checks at 1922b045 vs 138 on main 2430bfa3, counted by a scratch copy); ledger + rulings copied to docs/superpowers/verification/2026-10-28-lc11-checkout-free-replay-{ledger,rulings}.md. NEXT: gates, commit, ask the user to push + PR.
```

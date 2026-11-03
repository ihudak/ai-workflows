# Live checks of 2026-10-29 to 2026-11-03 — round 2 of `docs/superpowers/to-test-on-real-project.md` on the e2e copies

Every run below used the e2e copies, `ihudak-e2e/bookstore` and `ihudak-e2e/bookstore-specs`, through `~/e2e-copies.sh`, with the plugins installed from this marketplace. The plugins updated themselves during the round, so each run names the versions its session loaded where the notes kept them. Session transcripts are under `~/.claude/projects/-workspace-e2e-bookstore/` on the test machine, named by session id. The items these runs settled are deleted from the to-test list in the commit that adds this record, and the ones they settled in part are narrowed to what is left. The defects they found are filed in `docs/superpowers/to-fix.md` as LC12 to LC28.

## The test bed

- **The test machine's container was recreated on 2026-10-29, and the copies' `.git/config` and `.git/hooks` came back as read-only mounts.** The launcher now hands git its configuration through the environment (`GIT_CONFIG_COUNT`) and has three switches:
  - `E2E_HOOKS_PATH` sets `core.hooksPath` for a test hook.
  - `E2E_GIT_CONFIG` adds keys such as `workflows.sessionBranch`.
  - `E2E_SPECS_PUSH_UNREACHABLE` points the specs copy's push, and only that, at a host that does not resolve. It matches the copy's URL with `pushInsteadOf`, so the code copy is untouched. LC2's setup asked for `git remote set-url --push`, which the read-only config refuses.
- **Guards.** Pushes to the maintainer's own repositories are refused by `pushInsteadOf`, and a `gh` wrapper writes only to the two copies. A snapshot check compares the demo repositories with a baseline. The first baseline was lost with the container and taken again on 2026-10-29 at 14:41Z, and the check printed `same` each time it was run after that.
- **A read-only config warning.** git printed `could not write config file … Device or resource busy` on `push -u`, `switch` and `branch -d`, where it writes the branch's tracking configuration. The commands still did their work: S3's pushes exited 0, and S6's `switch --track` created its branch with no upstream. It comes from the test bed, not the plugins.
- **Teammate pushes for LC11.** A watcher script pushed a teammate's register record or `implementation.md` block from a scratch clone after the run's preflight fetch and before its terminal push: at the run's first question in S1, S3 and S7; in S2 the record was pushed after the run's `register.py` commit.

| Run | Command | Session | Items | Result |
|---|---|---|---|---|
| S1 | `/security-workflows:scan --triage` | `16fdd4a7` | LC10, LC11-1 first pass | pass, save LC10's evidence line (LC12) |
| A4 | the Epic pickers, nine runs | — | LC1 | pass; LC13 |
| A3 | `/product-workflows:epics BOOK-5` | `09774c36` | LC6, LC7, LC8 | LC6 pass; LC7 main path pass; LC8 in part; LC14 |
| S2 | change scan of BOOK-2-01-02 | `26f08c86` | LC11-1 second pass | pass |
| S3 | `/dev-workflows:implement BOOK-2-01-02` | `a09e7617` | LC11-2 | pass |
| S4a, S4b | `/security-workflows:scan --verify-fixes` | `2ab53897`, `811b7fc6` | SEC-A1, LC11-1's tail | pass |
| S5 | `/dev-workflows:conformance BOOK-2-01-02` | `f37b326f` | SEC-A2 | pass |
| S6, S6b | change scan, then `--triage`, in session-branch mode | `1939ccca`, `762a2f3d` | SEC-A3 | pass; LC28 |
| A2 | `/dev-workflows:design BOOK-4-01`, revising | `e10b6352` | LC4, LC5, PR6 | LC4 and LC5 pass; PR6 fail (LC15) |
| S7, S7b | `/dev-workflows:implement BOOK-4-01`, then `--triage`, in session-branch mode | `00cdedea`, `056ebbdb` | LC11-2's repeat | pass; LC16, LC28 |
| A1 | `/product-workflows:specify BOOK-1-02` with a refusing hook | `9c223096` | PR5, LC3, LC4's `/specify` part, LC2's failed commit | pass; LC17, LC25 |
| A3b | `/product-workflows:epics BOOK-6` | `94295179` | LC7's other paths | pass; LC18 to LC21, LC27 |
| A5a, A5b, A5c | `/workflows-core:frames BOOK-7`, three times | `096282fa`, `182e20dc`, `a6510adf` | LC2's re-publish and no-op re-run | pass; LC22, LC26 |
| A6a, A6b | `/product-workflows:specify BOOK-8`, `BOOK-9` | `7f34a0a1`, `f1aded76` | LC9 | pass; LC23, LC24 |

**Not run in this round:**
- B16-5 waits for the next live run of the BRD route.
- LC2's variant with a hook that refuses every commit: A1's hook refused only a commit staging a `specification.md`.
- PR7 needs a re-review that still returns `BLOCK`, and no re-review did.
- LC8's held-out `MAJOR` did not arise.
- L2 and PR2 stay with `docs/superpowers/to-fix.md`.

## Run S1 — triage under a moving register (LC10, LC11-1 first pass)

**Setup.** The register of run 6 in `docs/superpowers/verification/2026-10-26-live-checks.md` was seeded on the specs copy's `main` (`1c1888d`). A scratch clone held a record dated earlier that allocates `[SEC#1]` to CWE-601, and the watcher pushed it (`22a7503`) when the run asked its first triage question. The session loaded workflows-core 1.67.0 and security-workflows 0.7.0, and cost $5.02.

**LC11-1, first pass: pass.**
- The terminal push was rejected as non-fast-forward. The replay (`register.py` 0.7.0, `--register-rebuild`) moved the finding and pushed on its first attempt.
- The `Specs repo:` line was the *replayed and pushed* row, naming `[SEC#1] → [SEC#3]` as the local number, and no settle line followed it.
- Both run records are on `origin/main` (`59104ea`), and `register.json` and `register.md` there match a scratch `rebuild` byte for byte.
- The local `main` stands on `origin/main`, and the checkout is clean.
- Before the replay, the catch-up pull refused to run over the run's own modified register files, as it should.

**LC10: pass, save the evidence line.**
- The batch question listed both rows in its own text.
- The 7.1 plan printed `reserved_moves`, with the move from 1 to 3, beside `"renumbered": []`.
- The report's `### Register` named the move as provisional on its *Moves on merge* line, with the check under it, its values written in, and its stop. Run after the replay, the check gave its third case, and the stop was met.

**The fail.** The false positive's evidence line, `this.ratings = data;`, appeared only in a `git show` output and in the run's thinking. It was in neither the reply's text nor the next question's. This is the second live miss of that sentence, so it is filed as LC12. The printed check also dropped "or each replay that brings `origin`'s records in"; that is filed with LC12.

## Run A4 — the Epic pickers (LC1)

**Setup.** The six PICK PRDs of run 1 in `docs/superpowers/verification/2026-10-26-live-checks.md` went back on the specs copy, and that run's eight commands were typed in turn, nine sessions in all, one `/specify PICK-3` twice.

**LC1: pass, save one run's order.** Each overflowing picker carried *Another Epic (you'll be prompted for its key)*, and its description named every Epic left out, after `Not shown as an option:`. The item expected it to be the last option, and in one `/specify PICK-3` run it was third, before the broad-spec option (LC13). The `(Recommended)` marker followed the item's expectations:
- No option carried it in the four `/implement` pickers that offer the broad slice.
- In the other two `/implement` pickers, it sat on the first actionable row.
- No row carried it in the `/specify` pickers whose Epics were all ●, and the question's text said so.

**Also seen.** Epic labels used the bare key in some pickers and the `EPIC-`-prefixed form in others (filed with LC13).

## Run A3 — `/epics BOOK-5` (LC6, LC7, LC8)

**Setup.** BOOK-5, the PRD of run 4 in the 2026-10-26 record, with `prd.md` only, from the code copy on a feature branch. The run cost $17.83, wrote two Epics after a size split, and opened specs pull request #16.

**LC7, main path: pass.**
- The repository picker put the session's repository first, marked `(Recommended)`, with its path.
- The refresh question named the feature branch and the default branch.
- The code copy stayed on its branch.

**LC6: pass.** Both offers to apply findings listed each finding in the question's own text.

**LC8: in part.** `doc-fixer`'s brief carried its *Decisions* line. But the choice-`MAJOR` concerned an answer the person had given, and the run asked it as a question, so the held-out marker case did not arise. LC8 stays on the to-test list.

**A defect.** Phase 7.4's Instructions agent edited the code repository's `CLAUDE.md`, the session's working directory, and left the edit uncommitted. It was reverted by hand. Filed as LC14; run A3b did not reproduce it.

## Run S2 — a change scan beaten to the push (LC11-1 second pass)

**Setup.** A change scan of BOOK-2-01-02 at `d5dab21` allocated new findings. A teammate's record from the scratch clone took the same next number and was pushed after the run's `register.py` commit. The session loaded workflows-core 1.68.0 and cost $24.71.

**LC11-1, second pass: pass.**
- The push came back `[rejected] (fetch first)`, and the replay moved the finding and pushed on its first attempt.
- The move was on the clone's side, the teammate's CWE-352 to `[SEC#3]`, named with *origin's number*, and no settle line followed.
- Both records are on `origin/main` (`27647bf`), and the register there matches a rebuild byte for byte. The local `main` equals `origin/main`, and the checkout is clean.

This run also seeded SEC-A: `[SEC#1]` and `[SEC#2]` were triaged *fixing*, the second with a patch, and their follow-up lines were written.

## Run S3 — `/implement BOOK-2-01-02` beaten to the push (LC11-2)

**Setup.** The first attempt (`c98a8ef1`) lost its network at its first question and changed nothing. Its watcher had also fired before the preflight's pull, and a resumed transcript already holding a question would have fired the next watcher at once, so a fresh session was used. The second attempt (`a09e7617`) loaded workflows-core 1.68.0 and dev-workflows 4.50.0, and cost $32.86. The watcher pushed a teammate's `bookstore-admin` block for the same Epic, dated the same day, at the run's first question.

**LC11-2: pass.**
- The terminal push was rejected, and the replay pushed on its first attempt with no moves.
- The `Specs repo:` line said the push followed a replay.
- `implementation.md` on `origin/main` (`0bb7b65`) holds every block whole, each under its own header and with its own `pushed:` line: the 2026-10-13 `bookstore` block, a teammate's `bookstore-mobile` block that the first attempt's watcher had pushed, the teammate's `bookstore-admin` block, then the run's. No block is merged from two.

**Also seen.** The run found a third planted flaw, which logged a request body and the page's cookies. It asked, and the person chose to leave it and report it. The option the run improvised promised "the final report and the PR body", but a run pushing to an existing pull request edits no body. So the pull request never says it.

## Runs S4a and S4b — `--verify-fixes` before and after the merge (SEC-A1, LC11-1's tail)

**S4a, before the code copy's pull request merged: pass.** It stopped with `SECURITY_NOTHING_TO_VERIFY`, saying the default branch had no commit after the fixes. It wrote no record and created no worktree. Its `Specs repo:` remedy named `git config workflows.sessionBranch true`, which only this test bed's read-only config refuses.

**S4b, after the merge (`05b2643`): pass.** It cost $10.60.
- It scanned the two fixed files at the default branch's head in a temporary worktree, which it removed at the end.
- It found nothing. `[SEC#1]` and `[SEC#2]` closed `fixed` by themselves, and the Epic's `follow-ups.md` was unchanged.

**LC11-1's tail: pass.** As the first run to record after S2's replay, S4b reported "the register recorded an earlier move of [SEC#1] to [SEC#3]. No follow-up line needs correcting."

## Run S5 — `/conformance BOOK-2-01-02` after the merge (SEC-A2)

The session loaded dev-workflows 4.52.0 and cost $11.39.

**SEC-A2: pass.** `unit-branch` read the unit as merged, and the Epic run traced the default branch at `05b2643`: 88 requirements, 86 satisfied and 2 not checkable.

**Also seen.**
- The two synthetic teammate blocks from S3 were reported as repositories it could not trace, which was expected.
- The run noted that the ARD's landing order was broken, because this test merged the web change first.

## Runs S6 and S6b — the register in session-branch mode (SEC-A3)

**Setup.** `GIT_USER_INITIALS=ig` and `E2E_GIT_CONFIG="workflows.sessionBranch=true"`. S6, a change scan of BOOK-2-01-01, loaded workflows-core 1.69.1 and cost $12.82. S6b, `--triage`, cost $3.01.

**SEC-A3: pass.**
- S6 committed the register's paths with its session files on `session/ig` and pushed that branch: `runs/`, `scans/`, `register.json` and `register.md`. `main` was untouched, and the working tree carried the files as `workflows-core:specs-repo-git` §8.3's overlay.
- S6b's preflight found them through the overlay: it had no files to flush and wrote nothing back. It then committed only its cost entry on `session/ig`.

**Also seen.** The preflight's flush, with nothing to commit, created a local `session/ig` and said nothing about it; S7 did the same (LC28). Afterwards session mode was ended, with `lift`, a merged pull request and both copies of the branch deleted.

## Run A2 — `/design BOOK-4-01` revising run 3's design (LC4, LC5, PR6)

**Setup.** The `design.md` of run 3 in the 2026-10-26 record was rebuilt from the head of that run's specs pull request, #14, with the planted `## Pieces` section. The session loaded dev-workflows 4.52.0, cost $32.81 and opened specs pull request #19.

**LC5: pass.**
- `pieces.py parse` printed `malformed` (*the section holds an _N/A line beside other lines*).
- One fix kept only the `_N/A` line, with no question, and the second parse printed `none`.
- The Final report named the defect and its fix, and quoted each dropped line.

**LC4: pass.**
- The play-back before the write carried its `Overlap read:` line.
- After the write, a second overlap read of the written design found three conflicts, and each was asked in turn.
- The whole-artifact gate then named each change and addition, with its own `Overlap read:` line. `design-reviewer` was dispatched only once that gate was confirmed.

**PR6: fail on its last expectation.**
- The parts that held: the `code-scanner` brief carried all five deploy-surface themes and the deploy directories in `search_hints.paths`. *Release verification* played back its premises at `file:line` and asked one rollout question, recommending a rollback to a digest.
- The fail: the first review raised a MAJOR on a fact those themes cover. The release also republishes the two database images' `:latest`, which the database Deployments pull with no pull policy, so a later restart of a database pod can start a new upstream major version on its volume. Filed as LC15.

**Also seen.** The report said "the re-check now reads one piece" where it read none.

## Runs S7 and S7b — `/implement BOOK-4-01` in session-branch mode (LC11-2's repeat)

**Setup.** Session-branch mode as in S6. The watcher pushed a teammate's same-day `bookstore-admin` block to `main` at the run's first question. S7 loaded workflows-core 1.72.0 and dev-workflows 4.55.0, and cost $31.32. S7b cost $3.69.

**What S7 did.**
- `commit-artifacts` committed four files on `session/ig` and pushed it. A session-mode run is not rejected when a teammate pushes `main`, so it made no replay, as expected.
- The code went to pull request #5 on the code copy. The first review passed with recommendations, and the re-review after `review-fixer` passed. The Gradle suite passed 28 of 28 and the web suite 459 of 459.

**S7b.** S7b's preflight brought `main` in. It took the overlay files out (`lift`), pulled, then put them back and merged `main` into `session/ig` (`put-back`, `sync.merged: true`).

**LC11-2's repeat: pass.** `implementation.md` on `session/ig` then held the 2026-10-20 block, the run's block, then the teammate's. Each block was whole, with its own header and `pushed:` line, in `workflows-core:specs-repo-git` §8.2 step 3's order.

**A defect.** The test-baseliner capture's headless browser crashed and left a 24 MB core dump in the web module. `/implement` re-reads the tree only before the capture, so `code-handoff` §2.2 would have swept the dump into the commit. The orchestrator caught it only from code-writer's report. Filed as LC16; the dump was deleted by hand.

**Also seen.** S7b stopped with `SECURITY_NOTHING_TO_TRIAGE`, which was correct: the tester's run sheet was stale, and `[SEC#3]` had been triaged in S4b.

## Run A1 — `/specify BOOK-1-02` with a refusing hook (PR5, LC3, LC4, LC2)

**Setup.** Run 2's setup from the 2026-10-26 record. A `pre-commit` hook set through `E2E_HOOKS_PATH` refused any commit staging a `specification.md`. The session loaded workflows-core 1.72.0 and product-workflows 3.66.0, and cost $25.52. Every `(Recommended)` answer was taken, save the repository refresh, answered *no refresh* as run 2's setup says. The grill's backlog question again recommended dropping notices past a limit, which departs from [AD#4].

**PR5: pass.**
- `overlap-reader` was dispatched after the last stage and before the first `spec-reviewer`. It returned 11 conflicts, asked as nine questions because two pairs were settled by one answer each.
- The first conflict was the skipped notice against [AD#4], offered only as an ARD deviation, which landed under the specification's `### Open questions`.
- The whole-specification gate question carried the `Overlap read:` line in its own text, counting the ARD's 11 Rules.
- The first review found no unrecorded departure.

**LC4, the `/specify` part: pass.** The whole-specification play-back was confirmed before the first `spec-reviewer` dispatch.

**LC3: pass.**
- The first review returned `BLOCK`, with one BLOCKER beside 2 MAJOR, 11 MINOR and 2 NIT findings; three of the MINORs only acknowledged the recorded ARD deviations.
- Before any fix, the run asked the *Fold* question, its own text listing each finding with its severity, place and edit. The BLOCKER's decision was asked next.
- One fix cycle followed, and the re-review passed with recommendations and offered none of the folded findings again.

**LC2, the failed commit: pass.** The handoff line read `Phase handoff: NOT handed off — the commit failed (pre-commit (e2e live check LC2): …). The deliverable is staged on spec/BOOK-1-02-storage-restock-notice, not committed. Nothing was pushed, and no pull request was opened.` The `Specs repo:` line was `workflows-core:specs-repo-git` §6's *`origin` does not have this plugin branch* row, and `ls-remote` showed no such branch.

**PR7 was not run.** The re-review did not return `BLOCK`.

**Also seen.**
- Stage 4's own overlap line said "no conflict" on both departures the whole-specification read then found (LC25).
- After the re-review, the run wrote three product decisions as open questions without asking (LC17).
- The report said "Two" of those three.
- An option the run improvised said the docs index would be built "before the scan", but the run built it in the background.

## Run A3b — `/epics BOOK-6` (LC7's other paths)

**Setup.**
- BOOK-6 is a copy of BOOK-5 with no Epic and no ARD.
- Three throwaway clones, one commit each, were added under `$REPOS_PATH` so the picker had more than three candidates; they were removed afterwards.
- The code copy was on `ig/BOOK-4-01-in-stock-count`.
- The session loaded workflows-core 1.72.1 and product-workflows 3.66.0, and cost $20.63. It opened specs pull request #21.

**LC7: pass on every path.**
- **The picker.** The session's repository came first, marked `(Recommended)`, then one clone, *Another repository (you'll be prompted for one or more names)* and *Turn code scan off*. The remainder option's description named the two clones left out, the specs copy was not listed, and the question said that several names could be typed.
- **A name with no clone.** Through *Another repository*, the run listed all four candidates in prose. The typed name `bookstor` led to the three-option refresh question, then Phase 4's zero-match escalation, verbatim.
- **The four-option question.** Given the code copy's path at that escalation, the run asked the four-option question, naming `bookstore`, its branch and its default branch. On the recommended answer, the code copy stayed on its branch.

**Defects.**
- Phase 2 asked for plan approval with no plan shown (LC18).
- The recommended "scan as it stands" grounded the Epic in that branch's unmerged code (LC19).
- The re-review option read "Re-review the edited the Epic drafts once" (LC20).
- The report heading read "## keyed Epic Drafting Report" (LC21).
- The report's *Clarifications* line said none was left unresolved, though the Epic held three markers the review had raised, which only `### Deferred items` listed (LC27).

**Also seen.**
- Phase 7.4's agents edited nothing, so LC14 did not recur.
- The model called `ScheduleWakeup`, a tool meant for `/loop`, as a heartbeat while the scanner ran. It fired twice; the run recognised both, did not restart, and stopped it. This is a harness and model matter, not plugin text.

## Runs A5a, A5b and A5c — `/frames BOOK-7` (LC2's re-publish and no-op re-run)

**Setup.** BOOK-7, a copy of BOOK-6 with three SVG frames under `design/restock-list/` and no `index.md`, was put on the specs copy's `main`. The sessions loaded workflows-core 1.72.2 and cost $4.52, $4.52 and $4.44.

**A5a, with `E2E_SPECS_PUSH_UNREACHABLE=1`: pass.**
- `frame-describer` described the three frames, and the handoff committed `index.md` on `frames/BOOK-7-restock-screens` (`cf6b69e`). The push failed on `Could not resolve host`.
- The handoff line was `workflows-core:phase-handoff` §4.1's *Push failed* row, verbatim, naming `git -C "/workspace/e2e/bookstore-specs" push -u origin frames/BOOK-7-restock-screens`, with the index's path under it.
- The `Specs repo:` line was `workflows-core:specs-repo-git` §6's *`origin` does not have this plugin branch* row, and no `frames/` branch reached `origin`.

**A5b, with no switch: pass.**
- The preflight stayed on the unpushed branch, and no frame was described again.
- The index was rebuilt byte for byte, and nothing was staged. The handoff question said the index was committed as `cf6b69e` on a branch never pushed.
- On the recommended answer, the handoff pushed the branch and opened pull request #22. The line was the *Committed, pushed, PR opened* row, with no path under it, where it used to report *Nothing to commit*.
- That pull request was then merged and its branch deleted.

**A5c, from `main` after that merge: pass.**
- The index was rebuilt byte for byte. The handoff cut `frames/BOOK-7-restock-screens`, found nothing to stage, switched back to `main` and deleted the branch.
- The line read `Phase handoff: no deliverable changes to commit on frames/BOOK-7-restock-screens, which this run cut and has removed. Nothing was pushed, and no pull request was opened; the deliverable is already on main.`
- `rev-parse --verify --quiet refs/heads/frames/BOOK-7-restock-screens` printed nothing, and the run's `Specs repo:` commit went to `main`.

**Defect.** A5c's handoff question should not have been asked, because all three answers ended the same way (LC22, found by the run's own feedback).

**Also seen.**
- A5a's `Specs repo:` line read "(1 files)" (LC26).
- A5a capped its push with a bare `timeout 90` of its own.
- A5b's report said "was already behind no changes on main".
- A5c's opening `git fetch` timed out after 60 seconds; its push 25 minutes later took seconds, so it was the network.

## Runs A6a and A6b — `/specify` at PRD level on a multi-component PRD (LC9)

**Setup.** Two PRDs, BOOK-8 and BOOK-9, identical but for their keys, went on the specs copy's `main` (`22b1ad7`). Each holds:
- a `prd.md` for a restock list in the web store;
- an ARD with status `reviewed` whose `components:` holds `bookstore:storage` and `bookstore:web`, with [AD#1] the storage endpoint, [AD#2] the threshold kept in the browser, and one contract row between them;
- two Epic folders, `-01` targeting storage and `-02` targeting the web store;
- no PRD-level `specification.md`.

BOOK-9's `EPIC-BOOK-9-01` alone also held a `specification.md` on `main`. Each run chose *Author one broad PRD-level spec instead (Recommended)* at Step A and took every `(Recommended)` answer. A6a loaded product-workflows 3.69.0 and cost $22.99. A6b loaded 3.70.1 and cost $29.35. The `### Next step` paragraph is the same in both versions and on `main` at `533037e0`.

**The Step A pickers: pass.** The marker sat on the broad-spec option, and no Epic row carried it. A6b showed `EPIC-BOOK-9-01` as ● done, after the not-started Epic.

**LC9 without a merged Epic specification (A6a): pass.** The `### Next step` said to settle the two open questions first and revise with `/product-workflows:update-spec BOOK-8`, and named `/product-workflows:epics BOOK-8` `(once the pull request above is merged)`. It offered no `/dev-workflows:design BOOK-8`, and said instead: "`/dev-workflows:design BOOK-8` isn't recommended yet: on this PRD it designs the Epics, and no Epic has a specification on `main`."

**LC9 with `EPIC-BOOK-9-01`'s specification merged (A6b): pass.** The `### Next step` read "**Dev:** `/dev-workflows:design BOOK-9` `(once the pull request above is merged)`. Because BOOK-9 already has Epic folders, this designs the Epics, not this spec as a whole. Only `EPIC-BOOK-9-01` has its own spec on `main`, so `EPIC-BOOK-9-02` first needs `/product-workflows:specify BOOK-9-02`."

**A defect beside the pass.** That merge clause is false. `/dev-workflows:design BOOK-9` auto-selects `EPIC-BOOK-9-01` and gates that Epic's merged specification, so it never waits on the pull request this run opened. Filed as LC23.

**Also seen.**
- **A6a's reviews.** The first review returned `BLOCK`, and LC3's question appeared again. The re-review passed with recommendations, and two product decisions became open questions (LC17).
- **A6b's lineage check.** The new lineage check asked about the two `epic.md` files, which predate it and carry no lineage record, and recorded them as accepted.
- **A6b's capture call.** Its first `lineage.py capture` call failed on the form `workflows-core:document-lineage` §5 gives (LC24, the run's own feedback).
- **A6b's reviews.** Three decisions from its first review became open questions (LC17).
- **Overlap reads.** In both runs, Stage 4's overlap read missed departures from [AD#2] or [AD#1] that the whole-specification read caught. In A6a, that made the person reverse an inference they had confirmed (LC25).
- **Handoffs.** Both runs opened their pull requests, #23 and #24, which are left open on the copy.

# Live checks of 2026-11-04 to 2026-11-08 — round 3 of `docs/superpowers/to-test-on-real-project.md` on the e2e copies

Every run below used the e2e copies, `ihudak-e2e/bookstore` and `ihudak-e2e/bookstore-specs`, through `~/e2e-copies.sh`, with the plugins installed from this marketplace. The round began on workflows-core 1.78.0, product-workflows 3.73.0, dev-workflows 4.58.0, docs-workflows 1.33.0 and security-workflows 0.10.2, the releases of the LC12–LC28 fix batch; the plugins updated themselves during the round, so each run names the versions its session loaded. Session transcripts are under `~/.claude/projects/-workspace-e2e-bookstore/` on the test machine, named by session id. Costs are computed from each transcript; a run's own cost entry, written before its last steps, is lower. The items these runs settled are deleted from the to-test list in the commit that adds this record, and the ones they settled in part are narrowed to what is left. The defects they found are filed in `docs/superpowers/to-fix.md` as LC29 to LC37.

## The test bed

- **Two new launcher features, each added after a lost run.**
  - `E2E_CODE_FETCH_UNREACHABLE=1` makes the code copy's fetch fail while its push still works. R2b's first attempt put a bare `url.<unreachable>.insteadOf` entry into `E2E_GIT_CONFIG`. `insteadOf` rewrites the push URL too, so the launcher's push guard refused to start, and the session ran without the setting: LC19's failing-fetch case went untested. The new switch adds a `pushInsteadOf` that maps the copy's URL back onto itself.
  - The launcher prints one line for each active switch, or `e2e: no test hook (E2E_HOOKS_PATH unset)`. S2 ran without its hook because the pasted launch line split in two. On a line of its own, `VAR=value` only sets an unexported shell variable, so the launcher never saw it. S3's first launch split the same way, and the new line caught it.
  - From S3 on, each run started from a one-line wrapper script that sets its own variables, so nothing can be split off. S4's, S6's and S7's wrappers also check the run's starting state.
- **Guards, as in round 2.** Pushes to the maintainer's own repositories are refused by `pushInsteadOf`, and a `gh` wrapper writes only to the two copies. The demo check compared the demo repositories with their baseline after every run and printed `same` every time.
- **The read-only config warning, as in round 2.** git printed `could not write config file … Device or resource busy` on `push -u` and `branch -d`, and the commands still did their work. S6c's report noted the warning and still reported both pushes as done.
- **A planted probe for LC16.** Code copy commit `031b30e` added a storage test that writes an untracked file on its first run and rewrites a tracked snapshot on later runs. It was reverted before S3 (`2d84463`).
- **Lessons from test runs reached the operator's home folder.** The knowledge-base maintenance agents of `/epics`, `/security-workflows:scan`, `/ready` and `/conformance` write only under `~/.claude/memory/`, by design. By the round's end that folder held four files of lessons drawn from test runs whose conditions were set up on purpose. They were archived and removed at the round's end, along with the code copy's `.remember/` buffers and an untracked `.claude/memory/` file. The test bed's reset list now names `~/.claude/memory/`.

| Run | Command | Session | Items | Result |
|---|---|---|---|---|
| R1 | `/dev-workflows:implement BOOK-1-01` in session-branch mode | `db46c7cd` | PR2, LC16, LC28 | PR2 measured; LC16 pass; LC28 fail (LC31) |
| R2 | `/product-workflows:epics BOOK-6` in session-branch mode | `896f5af6` | LC19, LC18, LC20, LC21, LC27, LC14 and D39, LC8 | pass, LC8 in part; G1's notice missing at detection (LC31); LC34, LC36 |
| R2b | `/product-workflows:epics BOOK-5` | `0c4e464a` | LC7, LC19's failing fetch | LC7 pass; failing fetch not run (setup) |
| R2c | `/product-workflows:epics BOOK-6`, code fetch failing, fresh session branch | `b9c5f093` | LC19's failing fetch, LC28 | pass |
| S1 | `/product-workflows:specify BOOK-8` | `17528656` | LC25, LC17, LC24, LC3's *Fix the BLOCKERs only* | pass, LC17's question format only; LC31, LC33, LC36 |
| S2 | `/product-workflows:specify BOOK-9` | `cb70c712` | LC2, LC23, LC24, LC17 | LC23 and LC24 pass; LC17's question format; LC2 not run (setup); LC32, LC36 |
| S3 | `/dev-workflows:design BOOK-4-01` with a hook refusing every specs commit | `aed7f2b5` | LC2, LC15, LC17, LC4 | LC2 pass; LC15 in part (LC30); LC17's question format; LC4 not settled; LC36, LC37 |
| S4 | `/security-workflows:scan --triage` under a moving register | `ff39ea42` | LC12 | evidence line fail (LC29); the check's wording pass |
| S5a, S5b | `/dev-workflows:ready`, then `/dev-workflows:conformance`, BOOK-4-01 | `983e5fd4`, `032098d1` | LC14 and D39, L2 | pass; LC31, LC35 |
| S6a, S6b, S6c | `/workflows-core:frames BOOK-7`, three times | `2bbd1562`, `83689387`, `73580035` | LC22, LC26 | pass |
| S7 | `/product-workflows:specify PICK-3`, then `PICK-4`, cancelled at the picker | `437604fc`, `16c8f587` | LC13 | pass |

**Not run in this round:**
- B16-5, D31 parts 2 and 3, D45 and DOC-D-G5 wait for the runs their items name, and the four decided live runs, VU-G2, DOC-D-G4, BRD-G2 and BRD-G3, were not scheduled.
- PR7 needs a re-review that still returns `BLOCK`, and no re-review did.
- LC3's *Fold* branch needs a `/create-prd` or `/create-ard` run, and none was made.
- LC4's no-change case, which S3 did not settle (see its section), its section-by-section `/design` case, and its `/create-prd`, `/create-ard` and `/update-prd` cases.
- LC8's fixer-brief half: R2 held both of its MAJORs out of `doc-fixer`, so no fixer ran.
- LC14's class in `/document`, and LC21's `/document` heading.
- LC17's *Leave it open* answer. It was offered in S1, S2 and S3, and each time the Recommended answer was taken instead. Every run also accepted the offer to apply the edit-only findings, so the case where it is declined was not run, and neither were LC17's `/create-prd`, `/update-prd` and `/create-ard` cases.
- L2's register-slug half: no run in the round made a Security Engineer offer that a pointer could carry.

## Run R1 — `/implement BOOK-1-01` in session-branch mode (PR2, LC16, LC28)

**Setup.** BOOK-1-01's design, merged on the specs copy as specs pull request #13, draws four pieces: `alerts-domain`, `alerts-lookups`, `alerts-web` and `alerts-deploy`, the last holding only build, image, Kubernetes and workflow files. Session-branch mode was on through `E2E_GIT_CONFIG`, with no `session/ig` branch anywhere. The session loaded workflows-core 1.78.0 and dev-workflows 4.58.0, ran 9 hours 29 minutes, and opened code pull request #6.

**PR2: measured.**
- The run cost $162.88: the main session $73.62 (338 calls, peak context 967k), ten reviews $42.44, nineteen writer groups $23.10, fixers $12.48, test writing $4.43, the planner $5.43. Run C, the two-piece run PR2 compares against, cost $84.51.
- The change was far larger than run C's: HIGH-RISK against SIGNIFICANT, 150 test cases against 85, 110 files and 8,044 added lines against 34 files and 4,515. The test suites held 731 tests at the end.
- **Idle time.** Three waits on the user ran past an hour, so the prompt cache expired and was written again three times, for $18.69. Run C's longest wait was 33 minutes.
- **The review rounds.** They cost $20.13 and $22.31 against run C's $8.92 and $9.55, about $4 per piece per round. The `alerts-deploy` piece's reviews cost $7.97 in all, and they found three things the overall review did not:
  - a MINOR: the scheduling wiring had no test;
  - a NIT: the Kubernetes init container hard-coded the database name;
  - in round 2, a MINOR: the `postgresTest` suite never runs in CI.
- **Verdict.** A piece holding only build and deploy files did find what the overall review missed, so PR2's condition for a "fewest pieces" sentence in `design-format.md` §14 is not met. PR2 is closed with this measurement, about $4 per piece per review round, and no change.

**LC16: pass.**
- At capture, the run asked the three-option question for the files the check created: the probe's log and a 24.6 MB headless-browser dump.
- At verify, it asked the two-option question for the tracked snapshot the probe rewrote, with no recommendation and no *Delete*.
- Every file was left out at the user's choice. The `Code repo:` line said "3 path(s) a check run changed were left uncommitted", and the Assumptions line said the same.

**LC28: fail.** The preflight created `session/ig` (`created: true` at 09:41:36) and printed nothing about it. `specs-repo-git` §3.4 asks for `Specs preflight: created local session/ig at <sha>; no session file to commit yet`. The final report did not mention the creation either. R2c printed the line, so the miss is intermittent. It is filed with two other dropped prints as LC31.

**Also seen.**
- A plan-conflict question about three review NITs, which a fixer had returned as `DEFERRED — plan-conflict` (`/implement` Phase 3B), carried no `(Recommended)` option. Each NIT disagreed only with plan detail and with neither `design.md` nor the specification, so the run could have recommended revising the plan. A user told to "take the recommended answer" has nothing to take. Not filed: `escalation-rules` marks an option `(Recommended)` only where the command names one, and this question (`implement.md:1108` at `4e8705c6`) names none.

## Run R2 — `/epics BOOK-6` (LC19, LC18, LC20, LC21, LC27, LC14 and D39, LC8)

**Setup.** The code copy was on R1's feature branch, with its probe files left in the tree. BOOK-6's folder on `main` held a committed `CLAUDE.md` and a `README.md` index reading "None drafted yet". A line was then appended to `CLAUDE.md` and left uncommitted, as an operator's own edit. The session loaded workflows-core 1.78.0 and product-workflows 3.73.0, cost $22.84 and opened specs pull request #25.

**LC19: pass.**
- The refresh question offered four options. Its recommended one read the code copy at `origin/master` by ref and named the branch the checkout would stay on.
- The scanner returned `scanned_ref: origin/master` with the refresh note "read origin/master by ref; checkout left on …". No Epic cited the branch's unmerged code.
- The code copy's branch, HEAD, status and file contents were unchanged after the run.

**Wording items: pass.**
- LC18: the plan-approval question's own text carried the whole plan.
- LC20: the re-review option read "Re-review the edited Epic drafts once (Recommended)".
- LC21: the report heading read "## Epic Drafting Report", without "keyed".
- LC27: the report read "Phase 6.1 clarifications: 3 resolved, 0 deferred. … For the markers the review added, see Deferred items."

**LC14 and D39: pass.**
- The maintenance step's first read listed `CLAUDE.md` as modified. Agent 3 appended three lines to it.
- The handoff commit carried `epic.md`, `_coverage.md` and `README.md`; Agent 1 had edited `README.md`, which had been clean before. It left out `CLAUDE.md`.
- The report named `CLAUDE.md` as changed while the agents ran, returned by neither, left uncommitted, and already holding the operator's line. The handoff question's text said "The PRD folder's CLAUDE.md is not included."
- The code copy was unchanged.

**LC8: in part.**
- The first review raised two MAJORs whose fixes were choices. Both were held out of `doc-fixer`, so no fixer ran, and the offer named them as left open, each needing a decision.
- Three `[NEEDS CLARIFICATION: …]` markers in `epic.md` named the decisions, and `### Deferred items` listed them as markers.
- The item's fixer-brief half was not seen. With both MAJORs held out, no fixer ran, so no brief carried a survivor list, or a *Decisions* line, beside a held-out finding. Round 2's A3 saw the *Decisions* line only where nothing was held out. LC8 stays in to-test, narrowed to that half.

**Defects.**
- **G1's notice was not printed when the guard fired (LC31).** The preflight's G1 guard fired on the dirty `CLAUDE.md`. §5 requires its four-part block both at the point of detection and in the run's last printed output. At detection the visible text was "Specs preflight hit an advisory guard; now gathering repo candidates", with no path, no fix and no consequence; the block's content went into a thinking block. The block was printed in full only at the end, after the `Specs repo:` line.
- **The fingerprint loop is improvised (LC34).** The maintenance step's fingerprint read is written out by the run each time. Its first attempt used `read -r` without `IFS=`, which dropped the leading space of the ` M` status record and corrupted the path. The run noticed and redid it four seconds later, and the run's own feedback asked for a shipped script.

**Also seen.**
- Agent 3, a general-purpose agent on Sonnet, handed back the literal text "placeholder" instead of its report. D39's before-and-after fingerprints caught the edit it had made, so nothing was committed wrongly. This is harness behaviour, not a plugin defect, and R2c saw it again in two agents.
- The run's feedback reported a false code claim that an edit after the review had added ("Config has no integer field"). Only the re-review caught it.
- The report said the re-review's verdict came before two edits that followed it, which no review read (LC36).

## Run R2b — `/epics BOOK-5` (LC7)

**Setup.** BOOK-5's folder on `main` held a planted `EPIC-BOOK-5-01` with an `implementation.md` naming `bookstore`. BOOK-5-02 was left unwritten, so the run had new work to do. The failing fetch for LC19 did not take effect; see *The test bed*. Session-branch mode was off as a result too, so the preflight flushed R2's nine overlay files onto `main`, which off session mode is correct. The session loaded workflows-core 1.78.9 and product-workflows 3.78.2, cost $20.53 and opened specs pull request #26.

**LC7: pass.**
- Phase 1 asked the three-option auto-derived question, "Scan repos referenced by sibling/parent Epics under this PRD (Recommended — auto-derived)", its text naming `EPIC-BOOK-5-01`'s `implementation.md` and `bookstore`. There was no repository picker.
- The plan's line read "Repos to scan: auto-derived in Phase 4 (EPIC-BOOK-5-01's implementation.md names bookstore)".
- BOOK-5-01 was listed as existing and was not drafted again; one new Epic, BOOK-5-02, was drafted.
- The by-ref read of LC19 held a second time: `scanned_ref` was `origin/master`, and the checkout stayed on its branch.

## Run R2c — `/epics BOOK-6` with the code copy's fetch failing (LC19's failing fetch, LC28)

**Setup.** BOOK-6's earlier branch and `session/ig` were deleted, with nothing lost, so the session branch had to be created again. The launcher ran with `E2E_CODE_FETCH_UNREACHABLE=1` and session-branch mode on. The session loaded product-workflows 3.78.3 and workflows-core 1.78.10, cost $22.06 and opened specs pull request #27.

**LC19's failing fetch: pass.**
- The scanner returned `prep.refreshed: false` and the refresh note "fetch failed: origin URL is /nonexistent-e2e/bookstore.git, which is not a git repository, so set-head also failed; read origin/master by ref as last fetched". `scanned_ref` was `origin/master` at `031b30e`, as last fetched, and the run asked no question.
- Phase 9's `### Repos scanned` read "Read by ref at origin/master (031b30e) as last fetched. That ref may be stale: the fetch failed …", and the Assumptions section repeated it.
- One artefact of the method: the refresh question already said the fetch would likely fail, because `git remote get-url origin` prints the rewritten URL. A real outage would not be foreseen. The scanner's path is what this item checks, and it held.

**LC28: printed this time.** "Specs preflight: created local session/ig at 3693897; no session file to commit yet." R1 had missed the same line, so the item stays open as LC31.

**Also seen.** Two of four Sonnet maintenance agents returned "placeholder", as in R2. The run's git-status comparison caught the `README.md` edit one of them had made, reported it as "changed … returned by neither", and left it uncommitted.

## Run S1 — `/specify BOOK-8` at PRD level (LC25, LC17, LC24, LC3)

**Setup.** BOOK-8's folder held `prd.md`, a reviewed `ard.md` with two Rules, and two `epic.md` files, but no specification. Session-branch mode was on. The checkout was left on R2c's branch so the preflight's branch handling would be exercised. The session loaded product-workflows 3.78.4 and workflows-core 1.78.11, cost $34.92 and opened specs pull request #28.

**LC25: pass.**
- The user's typed departure from both Rules was caught at once by the grill. It quoted [AD#1] and [AD#2] word for word and offered the change only as an ARD deviation. The user kept the ARD.
- Stage 4's Rule-only overlap read then caught three of the run's own inferences: one correction was asked and conformed, and two departures were recorded as deviations. The play-back named all three before the gate.
- The finished specification carries two `- [ ] ARD deviation:` lines.

**LC3, *Fix the BLOCKERs only*: pass.** The first review returned `BLOCK` with eight other findings beside the BLOCKER, and the user chose *Fix the BLOCKERs only*. The re-review's offer, at PASS WITH RECOMMENDATIONS, carried all eight beside its own findings.

**LC17: the question format passes; *Leave it open* not exercised.** Three findings needed a decision. Each was asked as its own question, with the reviewer's options and *Leave it open* last, and each answer was applied. The report said "applied 11 edits and settled 3 decisions". Every answer was the Recommended one.

**LC24: pass.** `lineage.py capture --from-disk prd.md ard.md` succeeded on its first call.

**The preflight's branch handling: pass.** "The specs repo moved from epics/BOOK-6-restock-list-copy to main, since no key of this run names that branch."

**Defect (LC33).** The refresh question recommended "fetch + pull default branch". That would switch the session's own repository, the code copy on R1's feature branch, onto `master`. Only the dirty-tree guard stopped it, and only because the probe's files were in the tree; on a clean feature branch the switch would have gone through silently. LC19's by-ref read exists only in `/epics`.

**Also seen.**
- The Final report came out as a prose summary, without its Model routing and PRD gate lines, and with Lineage as a prose bullet rather than its §7 line. S2's report carried those lines. This is filed with the other dropped prints as LC31.
- The report said the re-review's verdict came before the last round of edits, so no review read the current text (LC36).

## Run S2 — `/specify BOOK-9` at PRD level (LC2, LC23, LC24)

**Setup.** Session-branch mode ended before this run: `session/ig` was merged into `main` by specs pull request #29 and deleted. BOOK-9's folder held the same two Rules as BOOK-8, `EPIC-BOOK-9-01` with its `epic.md` and `specification.md`, and `EPIC-BOOK-9-02` with an `epic.md` only. A `pre-commit` hook refusing every specs commit was prepared for LC2. The session loaded workflows-core 1.78.12 and product-workflows 3.78.5, cost $41.27 and opened specs pull request #30.

**LC2: not run.** The session had no `core.hooksPath`, so both commits went through. The launch line had split when pasted; see *The test bed*. LC2 ran on S3 instead.

**LC23: pass.** The Next step said "`/dev-workflows:design BOOK-9` designs the Epics, not this spec, and doesn't wait on the PR. BOOK-9-01's spec is on `main` but predates this one … BOOK-9-02 has no spec yet." It had no merge clause.

**LC24: pass.** The capture took two paths on one flag and succeeded first time. It left out the two `epic.md` files on purpose, which is the defect below.

**LC17: the question format passes; *Leave it open* not exercised.** Three findings needed a decision. Each was asked with the reviewer's options and *Leave it open* last, and the first was answered with the Recommended option. After the re-review the user applied six more fixes, which no review read (LC36).

**Defect (LC32).** `/specify` Phase 2.5 says to capture and upstream-check "each `epic.md` Step B read". `document-lineage` §4 puts `epic.md` below a PRD-level `specification.md` in the chain, and a producer never records an input below its own output. On a PRD-level specification the two instructions contradict each other. The run followed §4 and reported the conflict in its feedback.

**Also seen.**
- The report's first sentence said `/dev-workflows:design` would not run until the pull request merged, which contradicts its own Next step.
- The refresh question again recommended "fetch + pull default branch" (LC33); the user answered *no refresh*.

## Run S3 — `/design BOOK-4-01` with every specs commit refused (LC2, LC15, LC17, LC4)

**Setup.** The run resumed the earlier `/design` session for BOOK-4-01, the one that had left round 2's LC15 MAJOR open: the release republishes two database images' `:latest`. The code copy was clean on `master` at `2d84463`. A `pre-commit` hook, given through `E2E_HOOKS_PATH`, refused every commit in the specs copy and allowed every other. The session loaded dev-workflows 4.59.4 and workflows-core 1.78.13 and cost $36.14.

**LC2: pass, on `/design`.** The item names a `/specify` run, but the path it tests, `phase-handoff` §2.5 and `specs-repo-git` §4 step 5, is the same in every producer.
- The hook refused both of the run's commits, the handoff's and the terminal commit's.
- The `Phase handoff:` line read "NOT handed off — the commit failed (pre-commit (e2e test hook): this repository refuses every commit). The deliverable is staged on design/BOOK-4-01-in-stock-count, not committed. Nothing was pushed, and no pull request was opened."
- The `Specs repo:` line was the *Commit failed* row word for word.
- `git ls-remote --heads origin refs/heads/design/BOOK-4-01-in-stock-count` printed nothing.

**LC15: in part.**
- The scan's brief carried all five deploy-surface themes. The scan named every image the release builds or retags, the database images and their unpinned base images included. It named every workload that pulls one, with its `file:line`, tag and pull policy ("none set, so Always").
- The rollout question played those back at `file:line` and named both database Deployments, the nine service Deployments and the web Deployment.
- **The fail.** Its answers covered only the databases ("How should the design's rollout handle the database images?"). The recommended rollback target, a digest recorded before the release, covered only them. For the web Deployment the question said what it pulls but not what a restart would then pull: the first tagged release since v1.9.0, so every web change merged since then. `commands/design.md:344` already asks for that per workload, so this part was the run's slip.
- The first review raised a MAJOR on the web Deployment: no restore target, and unreleased code would ship. The re-review raised a MAJOR on how a broken web build would be noticed, and a MINOR that the eight other services had no restore target either. S3's two reviews, after round 2's A2, found one class at a time what one question could have settled.
- `commands/design.md:344` says the recommended answer names "the rollback target", in the singular, which let the run name one for the databases alone. Filed as LC30; the run's own feedback says the same.

**LC17 on `/design`: the question format passes; *Leave it open* not exercised.** Six findings needed a decision: two from the first review and four from the re-review. Each was asked after the offer to apply the edit-only findings, as its own question with the reviewer's options and *Leave it open* last. Each answer was applied as an edit and named in the version line as D9 to D14. The first question to offer *Leave it open* was answered with the Recommended option, as in S1 and S2.

**LC4's no-change case: not settled.** The whole-design play-back preceded the write, the write changed no decision, and no gate followed it. But the write did two things the play-back had not stated:
- The play-back counted one citation fix in three places, and the write applied it in four. The session file records it as the same correction applied everywhere it occurred.
- The header's sentence on what had changed since the earlier scanned commit, "only lines under `.github/workflows/`", came from a path-filtered diff. The play-back never carried it, and it was false. The first review raised it as a MAJOR and it was corrected. Filed as LC37.

`commands/design.md:315` sends "a change or addition the writing makes to anything a gate confirmed" to the whole-artifact gate. The rule does not make clear whether a confirmed fix applied once more than counted, or a provenance sentence in the header, is such a change. So the no-change case stays in to-test.

**PR7: not run.** No review returned `BLOCK`.

**Defect (LC36).** The cap allows one fix cycle and one re-review. The re-review's findings were applied, and four more decisions, D11 to D14, were settled at their questions after it. So the handed-off `design.md` carries a verdict reached before seven substantive edits that no agent has read. The version line and the report say so. The run's own feedback suggests an overlap read scoped to those edits, which spends no review.

**Also seen.**
- `code-scanner` gave line numbers for one model class that did not match the file. The run's direct read caught them before `design.md` cited them, so the premise rule worked.
- The main session's context reached 836k tokens.
- The refresh question again recommended "fetch + pull default branch" (LC33). It was harmless here, since the copy was on `master`.

**Afterwards.** The staged files were saved and the specs copy reset. Before S5 they were committed straight to `main` by hand. The run's Next step had said to commit them on its `design/` branch and open a pull request once the hook was gone; the shortcut lands the same files.

## Run S4 — triage under a moving register (LC12)

**Setup.** The register was restored to round 2's S1 seed: two open findings at code commit `6942a24`, a CWE-79 in the rating list and a CWE-319 in the book service. Rebuilt by `register.py` 0.10.10, its files equal round 2's byte for byte. A watcher pushed round 2's planted record from a scratch clone at the run's first question; that record is dated earlier and allocates `[SEC#1]` to a CWE-601. The session loaded security-workflows 0.10.10 and workflows-core 1.78.14 and cost $7.93.

**LC12, the evidence line: fail, for the third time.**
- The person marked `[SEC#1]` a false positive and gave `web/src/app/ratings/rating-list/rating-list.component.ts:23` as the evidence.
- The run read that line at `6942a24` with `git show`. Its thinking said it had confirmed the line, and no question followed.
- The line, `this.ratings = data;`, appears only in that command's output. The reply that followed said "Decisions file checks out", and the report's own "Decided" line quoted the person's evidence text, not the repository's line.
- The step `scan.md` added for LC12, "***Show the evidence line*** — its own step", was skipped, as the prose before it was in run 6 and in round 2's S1. The report's `### Register` template has no line to carry it. Filed as LC29.

**LC12, the printed check: pass.** *Moves on merge* read "[SEC#1] → [SEC#3] once `0001-20261027T090030Z-3945795c.json` merges", marked provisional. Its check said "in the specs checkout, after each pull into it, or each replay that brings `origin`'s records in" in full, with its stop and its four steps, the values written in.

**The replay: pass.** The terminal push was rejected, and the run replayed onto `origin` with the register rebuilt. The `Specs repo:` line named the renumbering `[SEC#1] → [SEC#3]`. `origin/main`'s register matched a scratch rebuild byte for byte, and the false positive stood under `[SEC#3]`.

## Runs S5a and S5b — `/ready` then `/conformance` on BOOK-4-01 (LC14 and D39, L2)

**Setup.**
- BOOK-4-01's folder on `main` gained a committed `README.md` indexing its documents, with "Readiness snapshot: none yet" and "Conformance record: none yet", and a committed one-rule `CLAUDE.md`. A line was then appended to `CLAUDE.md` and left uncommitted.
- The code copy was clean on `master`, and its status was saved.
- `main`'s resume pointer was S3's. It carries the conformance-and-scan item with `(waiting since 2026-11-02T18:52:53+00:00)`.
- Both runs started from one launch, `/ready` first and `/conformance` after a `/clear`. They loaded dev-workflows 4.59.6 and workflows-core 1.78.15. `/ready` cost $15.76 and opened specs pull request #31; `/conformance` cost $14.98 and opened #32.

**LC14 and D39 on `/ready` and `/conformance`: pass.**
- The code copy's status, branches and `CLAUDE.md` were unchanged after both runs.
- The unit folder's `CLAUDE.md` is in neither handoff commit.
- Each run's documentation agent edited the clean `README.md`, and the edit was handed off with the deliverable.
- Neither run's instructions agent edited `CLAUDE.md`, so the case of an agent editing a file the operator had already changed did not arise. R2 covered it on `/epics`; `/ready` and `/conformance` carry their own copies of the step, and on them it remains unrun.
- `/ready` asked about the dirty `main` with no recommended option, and the user answered *Proceed anyway*. Its follow-ups flagged the uncommitted line as contradicting the PRD's [AC#1], without touching it.

**`/conformance`'s branch: as designed.** It was cut from `/ready`'s unmerged branch, because `/ready` had changed `README.md`, a path `/conformance` builds on. The `Phase handoff:` line said "cut from ready/BOOK-4-01-in-stock-count, whose unmerged commits this pull request carries — it changed …README.md, which this run builds on".

**L2, the `(waiting since …)` marker: pass.**
- `/ready`'s pointer carried the conformance-and-scan item with its datetime unchanged. It carried S3's Next step as "/dev-workflows:implement BOOK-4-01 (waiting since 2026-11-08T13:23:17+00:00)", which is S3's *Last completed*.
- `/conformance` settled its own half of the first item and kept "/security-workflows:scan BOOK-4-01 from bookstore … (waiting since 2026-11-02T18:52:53+00:00)". It carried `/ready`'s Next step with `/ready`'s own *Last completed* datetime.
- L2's register-slug half did not arise.

**Defects.**
- **A command item that also waits on a merge carried no marker (LC35).** The item "once the pull request for ig/BOOK-4-01-in-stock-count in bookstore has merged …, PE: /dev-workflows:conformance BOOK-4 → /docs-workflows:document BOOK-4 → /docs-workflows:release-notes BOOK-4" carried no `(waiting since …)` in three pointers in a row: S3's, `/ready`'s and `/conformance`'s.
- **G1's notice (LC31).** Both preflights met the dirty `CLAUDE.md` and put the G1 notice into thinking only at detection. Each run printed the block in full only at the end, after its `Specs repo:` line.

**Cost.** Each run checked an Epic with three acceptance criteria, and most of each run's cost went on reading the reference files.
- The main session was $13.79 of `/ready`'s $15.76 and $14.38 of `/conformance`'s $14.98.
- Tool results came to about 1.1 and 1.2 million characters. `specs-repo-git.md` alone accounted for about 330k of each, over seven and ten ranged reads, because it is read for the preflight and again for the terminal commit. `/ready` also read `phase-handoff.md` whole, about 184k.
- The measurements are added to PR10 in `docs/superpowers/to-fix.md`.

## Runs S6a, S6b and S6c — `/frames BOOK-7` three times (LC22, LC26)

**Setup.** BOOK-7's `design/restock-list/` index was merged by round 2's A5 runs. The current template, `grounding-format` §6.2, still produces it byte for byte. Each run started from a wrapper that checked its starting state, and the three cost $4.63, $5.13 and $5.49. S6a loaded workflows-core 1.78.15, S6b and S6c 1.78.16.

**LC22: pass, all three parts.**
- **S6a, from `main` with nothing changed.** The run asked no handoff question and printed `Phase handoff: not offered — every index this run wrote is already on main as written.` Its session files were committed on `main` and pushed.
- **S6b, a second frame set added.** Its wrapper committed `design/restock-alerts/` to `main` first: two SVG frames, no index. The launcher made the specs copy's push unreachable. The describer read the two new frames.
  - The run wrote two indexes: `restock-list`'s, identical to `main`'s, and `restock-alerts`'s, absent there. It asked the handoff question, whose text named the new index as not on `main` yet.
  - The push failed, as intended. The `Phase handoff:` line was the *Push failed* row with the index path beneath, and the commit stayed on a local, unpushed `frames/` branch.
- **S6c, round 2's A5b shape.** The run started from that unpushed branch, described nothing, and wrote both indexes byte for byte.
  - It asked the handoff question again, its text saying the index "sits only on local, unpushed commit 985f01e … not on main".
  - It pushed that commit and opened specs pull request #33. The `Phase handoff:` line read "frames/BOOK-7-restock-screens pushed — PR #33 open (…). No command waits on this; what reads it reads it as advice.", with no path beneath.

**LC26: pass.** S6b's and S6c's `Specs repo:` lines read "(1 file)".

## Run S7 — the `/specify` Epic pickers (LC13)

**Setup.** PICK-3 has four Epics and PICK-4 five, each Epic with a `specification.md`, and both PRD folders also hold a PRD-level `specification.md`. `/specify` adds an option of its own, so both pickers overflow the four-option limit. Each run was cancelled at its picker. They loaded product-workflows 3.78.9 and workflows-core 1.78.16 and cost $4.68 and $5.01.

**LC13: pass on both.**
- Each picker offered two Epic rows, then "Author one broad PRD-level spec instead", then "Another Epic (you'll be prompted for its key)" last.
- Every row's label shows the bare key, for example "● PICK-3-01 Epic 1 of picker check 3". The last option's description names the Epics left out by their bare keys.
- Each question's text said that nothing is actionable and that no option is recommended.

**Also seen.**
- PICK-4's row descriptions name the folder ("rewrites EPIC-PICK-4-01's specification.md"). LC13 checks the rows' keys, and those are bare.
- Both runs asked the refresh question before the picker, recommending "fetch + pull default branch" (LC33). Each cost about $5 before its first real question.

## The e2e copies at the round's end

- **Code copy.** `master` at `2d84463`, clean. Code pull requests #5 (BOOK-4-01) and #6 (BOOK-1-01) stay open as fixtures.
- **Specs copy.**
  - `main` at `7844e5c`, after specs pull requests #32 and #33 were merged; #32 carried #31's commits.
  - #26, #27, #28 and #30 were closed and their branches deleted. Their heads stay fetchable as `refs/pull/<n>/head`.
  - The register holds S4's three findings: `[SEC#1]` and `[SEC#2]` open, `[SEC#3]` a false positive.
- **Archive.** The removed memory files and `.remember/` buffers are kept in the test bed's archive under `~/.claude/e2e-live/r3/`.

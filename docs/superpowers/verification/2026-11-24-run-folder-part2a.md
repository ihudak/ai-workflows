# RUN-FOLDER-PART2A — `/ready`, `/conformance`, `/design`, `/upgrade`, `/vuln` and `/scan` resume — verification record

**Branch:** `iv-gu/run-folder-part2`, head `0405bcc1e` (the Part A text-corrections commit, the last commit before this record), on the base `9cca8c452`. **Releases:** `workflows-core` 1.100.0, `dev-workflows` 4.71.0, `security-workflows` 0.13.0 and `product-workflows` 3.88.0, each dated 2026-11-25. **Design:** `docs/superpowers/specs/2026-11-24-run-folder-design.md`; **plan:** `docs/superpowers/plans/2026-11-24-run-folder-part2a.md`. Every figure below was obtained on that tree, on 2026-11-25, by the command beside it; none is copied from another record. `git status --short` printed nothing before the commit that carries this record.

`git diff --stat 9cca8c452 HEAD | tail -1` prints `85 files changed, 8631 insertions(+), 280 deletions(-)`, before the commit that carries this record.

## The five Review Focus lines

Each line names the self-test cases in `plugins/workflows-core/scripts/run-folder.py --selftest` that pin the mechanism, and the text that makes the commands use it. Commands and references are cited by heading and a short quoted snippet.

1. **The run's own later edit reads as an outside change** (`/upgrade`'s `review-fixer` after `upgrade-executor`; the orchestrator commits between them).
   - Cases `writer-later-own-write-intact` and `tree-note-commit-intact`: a later write or commit the run announced with `tree-note` leaves the earlier writer `intact`. Companions: `writer-outside-change`, `writer-dispatch-then-intact`, `writer-agent-changed-still-intact`, `writer-subdir-tree-shares-state`.
   - Text: `plugins/dev-workflows/references/code-handoff.md`, *7.9 The run's own edits*: "call `tree-note <folder> --tree '<repo>'`, no scope, so the change never reads as `changed` when a resumed run meets a writer that ran before it". `commands/upgrade.md`, *Phase 2* step 7.5 and the commit step: "`tree-note` comes where §7.9 says".
2. **An executor killed mid-edit** (resumed `/upgrade` or `/vuln` meets `interrupted`: revert to `pre_edit_tree`, redo the component, no Phase 0.5 stash, no second branch).
   - Case `writer-interrupted`: a writer started and never finished reads `interrupted`. Companions: `writer-redo`, `writer-deleted-path`, `writer-not-a-git-tree`, `writer-rename`.
   - Text: `code-handoff.md`, *7.4 A writer cut off mid-edit, or changed since*: "`interrupted`, from any writer of a unit, means the tree holds part of that writer's work ... The caller's handling is §6's revert and the whole unit again". `commands/upgrade.md`, *Phase 0.5 — Settle the tree and the base*, whose settling steps are guarded effects (`p05-tree`, `p05-base`) a resumed run does not repeat; `commands/vuln.md`, *Writers*, "go through `run-writer` as code-handoff §7.2 says".
3. **A clone pulled between two sessions** under `/design`'s scan (the `code-scanner` result's pin no longer holds, so it is redone).
   - Cases `pin-recorded-and-returned` (a pin recorded with `done` comes back on the probe) and `redo-forces-dispatch` (a result whose pin the caller finds broken is dispatched anew).
   - Text: `plugins/workflows-core/references/scan-refresh.md`, *8. A run that keeps a run folder*: "**A saved scan is pinned.**", its *Recording* list "`--pin ref='<prep.scanned_ref>'`", and the rule that a scan whose pin moved is dispatched with `--redo`. `commands/design.md`, "**Saved, where the run folder is open** (Phase 0, *Saved dispatches*): id `<u>-scan-<repo id>`".
4. **A brief regenerated on resume** (`/ready`'s reviewer brief, `/conformance`'s requirement list, `/design`'s interface frame are written with `put` once and read back).
   - Case `put-atomic-owner-checked`: `put` writes atomically, under the lock and owner-checked, so a second session's `put` after a takeover exits 9 and the file read back is the one written. Companion: `answers-in-first-order`.
   - Text: `commands/ready.md`, *The reading — where the run folder is open*: "each with `put` (`workflows-core:run-folder` §5), in this order, `brief.md` last". `commands/conformance.md`, *Phase 3*, "**The verdicts — where the run folder is open**" (`put <folder> 'scratch/p3/verdicts.md' --from -`). `commands/design.md`, "written with `put <folder> 'scratch/<id>/brief.md' --from -` once built, and from then on read from that file, never built again", and the take frame, "`put <folder> 'scratch/<u>-take-<i>/frame.md' --from -`".
   - The self-test pins only the primitive; that each command builds its input from the saved file was checked by each command task's reviewer against the input-building rule.
5. **A keyless `/vuln` started again in the same repository with other CVE tokens** offers the other unfinished run.
   - Cases `open-keyless-others`, `keyless-args`, `open-others-same-args-other-specs`, `open-others-corrupt-neighbour`.
   - Text: `commands/vuln.md`, *Open the run folder*: "the same CVEs in another order, with another address or with other flags, are another run, which `open-run`'s step 6 offers". `plugins/workflows-core/references/run-folder.md`, *Entry point: `open-run`*, "keyless command run with other arguments opens a run of its own".

## The gates on this tree

| Gate | Result |
|---|---|
| `python3 plugins/workflows-core/scripts/run-folder.py --selftest` | exit 0; 68 lines, each `PASS`; no other line (`grep -c '^PASS'` prints 68, `grep -vc '^PASS'` prints 0) |
| `cmp plugins/workflows-core/scripts/run-folder.py plugins/<dev\|product\|security>-workflows/scripts/run-folder.py` | no output, exit 0 for each of the three: the four copies are identical |
| `./scripts/check-docs.sh --root .` | `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`, exit 0 |
| `./scripts/check-id-grammar.sh --root .` | `PASS: no dash-form requirement IDs under .` |
| `python3 scripts/validate-catalog.py` | `0 error(s), 0 warning(s) across 1 repo(s).` |
| `python3 scripts/reference-parts.py check-parts` | `PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh` |
| `python3 scripts/reference-parts.py check-citations` | `PASS -- 4 split reference(s)` |
| `python3 scripts/reference-parts.py check-questions` | `PASS -- 38 command(s) load the question rules before their first question` |
| `python3 scripts/reference-parts.py check-branch-check` | `PASS -- 24 command(s) run branch-check` |

**Not run here: `node scripts/mermaid/check-mermaid.mjs --root .`.** It needs its parser installed with `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund`, and `scripts/mermaid/node_modules` does not exist on this machine; it was not installed. CI runs the check on the pull request.

The other self-tests in `.github/workflows/validate-catalog.yml` were not run here; CI runs them.

## Owed — only a live run can show

None of the following has been run; each is owed, and nothing above claims it.

1. **A real `/dev-workflows:vuln` killed while `vuln-fixer` is editing, then resumed.** Passing: the new session offers *Resume*; on it, the half-edited tree is reverted to that CVE's snapshot, the CVE is fixed again on its own branch with no second branch cut and nothing stashed, and the Final report's `Resumed:` line counts the earlier CVEs' saved results as reused.
2. **A `/dev-workflows:design` resumed after a `git pull` in a scanned clone.** Passing: that repository's `code-scanner` result is redone, the other repositories' results are reused, and the resume question or report names the moved repository.
3. **A `/dev-workflows:ready` resumed after its reviewer finished.** Passing: the reviewer is not dispatched again, `readiness.md` is written once from the saved record, and the run goes on at the step after the review.
4. **A `/dev-workflows:upgrade --no-commit` resumed between two components.** Passing: the finished component is not redone and is not read as an outside change, the next component starts from its own snapshot, and no commit is made.
5. **Two sessions on one `/dev-workflows:conformance` run.** Passing: the older session stops at its next write with the takeover stop, writes nothing to the specs repository, and prints no cost entry, commit or Final report; the newer one finishes normally.
6. **A `/security-workflows:scan` triage resumed.** Passing: the answered triage decisions are not asked again, the register's lines are written once, and the run's scratch copy of the report is read where the folder was lost after the resume.

## Known limits shipping with the release

From each plugin's 2026-11-25 `CHANGELOG.md` section, *Known limits*:

`workflows-core` 1.100.0:

- A dispatch another plugin's command makes that this plugin cannot name stays unsaved and runs as before: an agent of a plugin with no `agent-file` skill (`prose-style`), a `general-purpose` dispatch, and the end-of-run maintenance and defect dispatches.
- A dispatch an agent makes inside its own run is not seen by the command's run folder (`docs-style-checker` to `prose-style-checker`): it counts only through the outer agent's file.

`dev-workflows` 4.71.0:

- `/ready`: the specs-repo preflight, which runs before the folder opens, may name the run's own uncommitted `_readiness.md` and maintenance edits in its dirty-tree notice. A change outside the PRD folder since the reading is neither named nor read again; *Start over* reads it.
- `/conformance`: the same preflight notice. Once the inventory stands, a resumed run checks the records on file no more, and a question asked again because a typed answer could not be taken, or because it would accept a mitigation, is asked again on a resume.
- `/design`: a brief and its copies are made once, so an agent dispatched again reads the older copy where a resumed session changed a file it names; a review redone because a checkout moved is followed by a re-review whose brief may stand from an earlier session; the changed files the resume question names are only those the PRD folder held when the Epic began.
- `/upgrade` and `/vuln`: the check for edits made between sessions runs before a component or CVE starts, so one already in progress is not checked, and an edit made between sessions to a file none of its finished passes wrote is committed with it. Registry reads are not recorded. A run resumed long after it began, two weeks by git's default, may find the snapshot pruned, and asks.
- All five: a dispatch that is not saved runs again on a resume, and a run resumed in another checkout of the same specs repository skips the steps it records as made: resume from the checkout the run started in.

`security-workflows` 0.13.0:

- Claude Security's scan and its patches are its own runs, which no session resumes.
- A run never resumed keeps its copy of the report in the register until an `--import` of the same report records it, or it is removed.
- On a resumed run the specs-repo preflight may name a maintenance proposal an earlier session applied, in its dirty-tree notice.
- The command saves no agent result, its plugin shipping no agent.

`product-workflows` 3.88.0:

- `/prd-ground`'s maintenance step stays unguarded until Part 2c: on a resumed run it runs again, and an `emit-auto` it had started may log a signal a second time under a new slug.

Deferred by the final review to Part 2b or 2c (from `progress.md`, the ledger lines marked `defer`, `carry to 2b` or `carry to plan 2b`), summarised:

- **`code-handoff.md` and the unit walk.** The walk has a gap for a started unit whose writers all read intact (§7.8 and §7.2 need corrections); §7.6 assumes a landed commit's re-made call finds nothing to commit, which an edit between sessions breaks; §7.4 step 3 loses a dead mid-script run's lines; `add` mode drops a whole rename record when only one half is named; a command with units but no revert must name its handling of an in-flight probe that returns `dispatch`.
- **Between-session edits.** The check for a started unit needs a script-backed "outside the run's recorded state" test; `/upgrade`'s `pre_existing_dirty` filter block is duplicated in `/vuln` and belongs in a shared part or a `tree-snapshot.py` subcommand.
- **`run-folder.md` at its size cap.** The run-gate rule for several questions in one call and the "record whose last file marks it whole" pattern are defined per command, and rules (1) and (2) of Task 6 belong in §3 and §5: a split or a cap raise is to be decided.
- **Smaller items.** `others` does not flag runs another session owns; a legacy gate re-recorded moves after others in `answers`; a re-record without `--keep-shown` leaves a stale `gates/<id>.md`; `scan-refresh`'s clean check runs at record time; the same repository at another worktree path redispatches a writer; `/design` judges "relevant" repositories again at each dispatch; the registry query is missing for an inventoried component with none in `ecosystems.md`; `code-handoff.md` is loaded whole (105K) by `/upgrade` and `/vuln`.

## Follow-up owed outside 2a

The `cp` → `cp -p` index copies in the diff captures (the pre-existing index-copy defect the final review found, fixed in `code-handoff.md` §6.1 and §6.2 only): `context-management`, `/upgrade`, `/vuln`, `/implement`, and `agents/test-writer`. To be fixed together with `/implement`.

# IMP-G5 — resume a crashed or killed `/implement` run

**Date:** 2026-11-12. **Status:** design, revision 4. Revision 3 was approved by the maintainer on 2026-11-13. Revision 4 adds the rulings the Fable plan review (2026-11-13) forced, each listed in §7 and marked *(r4)*. **Fixes:** IMP-G5 in `docs/superpowers/to-fix.md` (the maintainer took it off the deferred list on 2026-11-12; delete the entry when this lands). **Supersedes:** the non-goal at `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md:52`.

## 1. The problem

`/dev-workflows:implement` keeps its state in `$(git rev-parse --git-path dev-workflows/implement-run.json)` (`run-state.py`). When a run dies — killed, crashed, context lost — the next `/implement` in that worktree does the following:
- **Its state.** Phase 1.4's `init` moves the dead run's file aside unread.
- **Its edits.** The dirty-tree question meets the dead run's uncommitted edits. *Stash* hides them; *Proceed anyway* records them as `pre_existing_dirty`, which `code-handoff` §2.2 keeps out of the commit.
- **Its branch.** The next run abandons the dead run's feature branch, or cuts a new branch from it.
- **The work so far.** The run re-plans, re-baselines, re-codes and re-reviews from scratch.

A SIGNIFICANT run that dies in its Opus review loses all of it. Nothing finds a branch the dead run pushed without a pull request, or a commit it made before writing its block.

## 2. Goals, non-goals, anti-goals

- **Goal: resume where the run died.** A new `/implement` in the same worktree finds the dead run's file, says what it was doing, and offers **Resume**. A resume continues at the **step** the run died in, on its branch, with its plan, baseline, classification and answers. It never re-asks a question the file answers.
- **Goal: no work done twice.** A done step group is not re-coded, a finished review is not re-run, and a commit is never repeated.
- **Goal: proof, not inference.** The resume continues only where it can prove the tree holds the run's work and nothing else.
- **Goal: a better *Start fresh*.** *Start fresh* behaves as today, and also says where the dead run's work stands.
- **Non-goal: resuming inside an agent's dispatch.** An agent cut off mid-edit is re-dispatched with the tree as it stands (§4).
- **Non-goal: the dead session's cost.** That cost sits in another session's transcript. The resumed run's report always says it was not recorded.
- **Non-goal: resuming across clones or machines.** The state lives in the worktree's git directory.
- **Anti-goal: guessing whose an edit is.** Where the tree differs from the last state the run recorded, and nothing proves the difference is the run's, the resume stops or asks. It never folds an edit into the run's commit on a guess.

## 3. The design — decided

### 3.1 The run-state file: what it gains

The file becomes `format: 2`. A `format: 1` file — every file before this release — is not offered for resume, only *Start fresh*, since it has no snapshots and no durable copies.

**New keys:**
- `session`, `started` and `updated` (script-owned). `session` comes from `CLAUDE_CODE_SESSION_ID` (`null` where unset). The two times are UTC `YYYY-MM-DDTHH:MM:SSZ`.
- **Script-owned keys.** `set` refuses a write to `session`, `started`, `updated`, `durable` and `tree.snapshot`.
- `run_environment`: the run's environment, recorded at Phase 1.4 in the block `workflows-core:session-hygiene` §6 compares (the one `/design`'s `## Run environment` holds). Without it, §3.5's environment check has nothing to compare.
- `stash_before`: the value of `refs/stash` (or `null`), written **before** Phase 1.4 pushes a stash. A stash pushed before `stash_ref` was written is then still found: it is the entry that is not `stash_before`.
- `step`: the numbered step of the current phase the run is in, for example `"3B.6"` or `"3.5.5"`. It is written at each numbered step of Pre-Phase 3, Pre-Phase 3.5, 3A, 3B, 3.5, 4 and 4.6, and `open <phase>` resets it to `null`.
- `review_in_hand`: `first | re-review | delta | null`, written where Phase 3B dispatches `code-review`. It is cleared when that round's triage is settled.
- `tree`: the last tree state the run recorded, `{head, snapshot, when}`:
  - `head` is HEAD's sha;
  - `snapshot` is a `tree-snapshot.py` snapshot path, made durable;
  - `when` is `before <action>` or `after <action>`.
- `phase46_head`: HEAD's sha when Phase 4.6 opens.
- `code_handoff_choice`: the §2.4 consent answer, once given.
- `durable`: `{<key path>: {"copy": <durable path>, "of": <the source path it copied>}}`. See §3.4. *(r4)*
- `stopping`: `null`, or the reason of a stop that has begun its tail. A stop writes it **before** it runs Phase 4.6, so a run that dies inside its own stop is resumed as that stop (§4), never as a finished run. *(r4)*
- `conformance.note_blobs`: `{<annotated path>: <its blob on <default-ref>>}`, written wherever the run writes a note into merged specs (step 7.5, the at-the-edit departure note, Phase 3A step 6). `conformance.annotated` keeps its shape. *(r4)*
- `report.maintenance` entries gain `agent` (`docs | knowledge | instructions | impl-maintenance`).
- `step_groups[]` entries gain `started`, stamped by the script on `append`. Lists are not checked against `KEYS`, so the script stamps it itself.

### 3.2 Recording the tree around every action that can change it

Before and after **every action that can change the code repository's tree or HEAD**, the run records `tree`: `tree-snapshot.py snapshot`, then `persist`, then `set tree`. The actions are:
- **Dispatches:** `code-writer` (step and fix mode), `test-writer`, `review-fixer`, and the Phase 4 maintenance agents. Parallel dispatches — the four Phase 4 agents, split `test-writer`s — are recorded once per batch, before it and after its last return.
- **The scan-patch `git apply`** (Phase 3A/3B step 1, `implement.md:831`).
- **Check runs:** lint, build, verify, type-check, a repro re-run and project install scripts. The record is taken after each one's settlement — *Delete them*, *Leave them out*, *Commit them* — reusing the `snapshot_after` already taken around every check run (`implement.md:761`).
- **The orchestrator's own tree actions:** the `[DEBUG-xxxx]` probe strip (`implement.md:1043`), a step 7.5 note written into this repository (`:1125`), and a bisect and its reset.
- **Phase 4.6's commit:** HEAD moves and the tree cleans.
- **Session-branch `lift` and `put-back`,** on a direct run inside the specs repository.

**The expected HEADs.** HEAD is the run's own when it is `tree.head`, or, where `phase46_head` is set, any commit whose first parent is `phase46_head`: the run's commit landed and its record did not.

**Why snapshots.** They replace any self-reported path list: a snapshot sees formatter, generator and lockfile output that an agent would not report. The cost is one `tree-snapshot.py` snapshot per action, the tool Pre-Phase 3.5 already runs.

### 3.3 Detection and the question

**Where.** Detection sits in Phase 0, straight after the working directory is classified as a code repository (`implement.md:36`), and before address resolution.

**`run-state.py peek`.** A new verb. It prints the file at the git path, or exits:
- `1` — no file;
- `5` — the file does not parse;
- `8` — `format` is not 2.

It moves and locks nothing. Exit `6` is reserved by `implement.md:373`.

**Which session.** A file present at a run's start belongs to an earlier run. **Whenever its `session` differs from this one's, or either is null, the question names that session and `updated`.** A live run in another terminal is possible, so the question says so whatever the age. There is no time window.

**The superseded-run guard.** `open`, `set`, `append`, `persist`, `remove` and `init --recover` exit `9` where the file's `session` and the caller's are both non-null and differ. A null on either side passes, since it cannot be told apart.
- **The stop.** `implement.md`'s exit-code list gains exit 9 as a stop like exit 4: no Phase 4.6, no removal, no `--recover`, and the message *another session (<id>) took this run over — stopping without committing*. So a superseded live run stops at its next write, and never commits the resumed run's tree or deletes its state.
- **A stated limit.** A subagent the superseded run had dispatched keeps editing until that run's orchestrator next writes.

**The pre-check, before anything is offered.** HEAD must be one of the run's expected HEADs (§3.2), and the tree must compare equal to `tree.snapshot` through `tree-snapshot.py compare`. In session-branch mode (`session_branch_lift: true`) the comparison waits until after Phase 0's preflight, its `put-back` and the lift again (§3.5). Detection then only records that a resume is possible, and the question follows the comparison.
- **Equal:** *Resume* is offered and recommended.
- **Not equal, and `tree.when` is `before <dispatch>`:** the differing paths are listed. The question asks whether they are that dispatch's edits. *Resume — they are the run's* keeps them as that dispatch's partial work. *Start fresh* and *Cancel* are also offered.
- **Not equal, and `tree.when` is `after <dispatch>`, or HEAD differs:** the tree changed after the run's last record. *Resume* is not offered: only *Start fresh* and *Cancel*, naming the changed paths, or the HEAD move.
- **The run's commit landed, its record did not.** HEAD's first parent is `phase46_head` and `tree.when` is the record taken before the commit. Here each path that differs from `tree.snapshot` must be clean now **and** be in `git diff --name-only <phase46_head> HEAD`; every other path must compare equal. Then *Resume* is offered. *(r4)*
- **Before the run's first edit** (`tree.snapshot` null): there is nothing to compare. *Resume* is offered, since Pre-Phase 3.5's re-read already records new dirty paths as the user's.
- **`stash_ref` set:** it must appear in `git stash list --format=%H`. Otherwise the summary says the user's stash is gone, and *Resume* is not recommended.
- **A bisect is left running** — `$(git rev-parse --git-path BISECT_LOG)` exists, which is right in a linked worktree too. *Resume* is not offered: the question offers *Start fresh* and *Cancel*, and names `git bisect reset`.

**"The arguments differ" — mechanical.** Typed prose or an `@token` always differs. A typed key differs unless `workflows-core:addressing` §1's `read-key` equals the file's `key` or `unit_key`. A typed `--no-commit` differs unless it equals the file's `run_flags.no_commit`. Where they differ, *Start fresh* is recommended, and the summary says so. Other typed run flags (`--skip-costs`, `--skip-feedback`, `--enforce-model`) are per invocation and replace the file's.

**The question:**
```
An earlier /implement run in this worktree stopped at <phase> step <step> (session <id>, last write <updated>):
  <unit_key> — <class>, branch <branch>, <n of m> step groups coded[, review <round> <verdict>][, committed <sha>][, pushed][, stash <ref>]
choices: ["Resume it at <phase> step <step> (Recommended)", "Start fresh — leave its work where it stands", "Cancel"]
```
There are at most three options, and the labels are verbatim. **Cancel** is a stop. It joins the command's **Ending early** list (GIT-G1's section): a one-line addition that the pull request names for that track's owner.

**On *Start fresh*.** The run continues from address resolution, as today. `init` moves the old file aside and clears `implement-run.d/`, so the notice's facts are gathered at detection, from `peek` and the comparison already made, and handed to `init` in `report.notices`. *(r4)* Before the dirty-tree question, the run prints:
- the dead run's branch, and its commits ahead of base;
- the dirty paths its last snapshot attributes to it;
- `stash_ref`;
- `session_branch_lift`;
- a running bisect.

The user then answers that question knowing whose edits are whose.

### 3.4 Durable copies

**What gets persisted.** `run-state.py persist <key path> <file>` copies a file into `<git-path>/dev-workflows/implement-run.d/` and records it under `durable.<key path>` as `{copy, of}`, `of` being the source path. **A copy stands only for the file it copied** *(r4)*: `set` drops a `durable` entry, and deletes its copy, the moment its key stops naming that entry's `of` (set to another path, or to `null`); and `init --resume` repoints a key only where its value still equals its entry's `of`. So a superseded copy — an approved plan left behind when the key moved on, or a file written and set but not yet persisted when the run died — is never handed back as current. It runs at **every** write of a file a resume would need, so a later write replaces the copy. That means every file git cannot regenerate:
- `files.task_description_file`, `plan_file`, `pending_plan_file`, `summary_file`, `baseline_file`, `test_report_file`, `review_return_file`, `review_file`, `claims_file`, `snapshot_before`;
- every `step_groups[].report`;
- every `reviews[].return_file`;
- every `tree.snapshot`.

Diffs are not persisted: they are re-captured from the tree.

**`init --resume`.** It takes the old file whole, and appends `Resumed at <phase> step <step> after session <id> stopped at <updated>` to `assumptions`. It then writes `session`. Its stdin is the fresh Phase 0 facts (§3.5), merged over the old file.
- **Its path rules apply to one set:** the paths `run-state.py`'s `named()` returns (`run-state.py:425`), plus `lineage.check_file` and `tree.snapshot`.
- **For a path in that set:** where `durable` holds an entry whose `of` equals the key's value, it repoints the key to the entry's `copy`. Otherwise, where `os.path.isfile` does not find the path, it sets it to `null`.
- **Every other path is untouched:** `pre_existing_dirty[].path`, `unit_folder`, `spec_paths`, `inputs_read` and `conformance.annotated`.
- **`durable` keys for list entries** are written with their absolute index (`step_groups.3.report`), never `-1`.

**The two other `init` forms.**
- `init --recover`, this run's own file rewritten, keeps `implement-run.d/` and re-records `durable`.
- Plain `init` (*Start fresh*) clears `implement-run.d/`.

**`remove`.** It deletes `implement-run.d/` even when the file is already gone.

`implement.md:371`'s `KEYS_LINE` quote and `run()`'s verb list change in the same commit.

### 3.5 What Phase 0 does on a resume

- **Taken from the file, not asked:** `mode`, `key`, `focus_key`, `unit_key`, `unit_folder` and `workitem_key`. Address resolution re-resolves `key` against the tree, which also catches a moved or renamed folder. A resolved folder differing from `unit_folder` stops the resume.
- **The environment check.** The run compares the run's environment against the file's, as `/design` does, with `workflows-core:session-hygiene` §6's `resume-environment`: `$SPECS_PATH`, the repository and its paths. A mismatch is asked about as §6 says. `session-hygiene` §6's list of commands that resume gains `/implement`.
- **Run as on any run:**
  - the session-model gate;
  - the specs-repo preflight for this session (`specs_git` and `specs_merged_branch` take its result);
  - `branch-check`;
  - the in-scope specs gate;
  - the lineage check (a new `lineage` file);
  - and `inputs_read`, appended to.
- **Re-resolved:** `routing` and `coding_model`, by §4's rule, since `current_model` is this session's.
- **Skipped:** the per-token checks, the no-description stop, the design-doc guard, the picker, and Phase 1's read-backs. All of them settled the file's facts.
- **Step 7.5's notes.** Notes the dead run wrote into merged specs would meet `require-on-main`'s rows C′, C″ and C as uncommitted changes, and stop. Nothing is restored or re-applied, and the notes stay where every existing rule says they are, uncommitted in `$SPECS_PATH`:
  - Wherever it writes a note into merged specs, the run records the path's `<default-ref>` blob in `conformance.note_blobs` and persists the note's working copy under the key `conformance.note.<path>` *(r4)*.
  - On a resume, `/implement` does not call the gate for such a path where the working copy is byte-equal to its durable copy **and** the path's blob on `<default-ref>` is still the one `note_blobs` records. It calls the gate for every other in-scope path as on any run.
  - Where either test fails, the resume stops and names the path.
  - `require-on-main` itself is not changed; only `/implement`'s decision to call it is.
- **Session-branch mode.** Where the file says `session_branch_lift: true`, the preflight's `put-back` (`specs-repo-git` §8.3) is followed by a lift again, as Phase 1.4 does, and only then by the tree pre-check (§3.3).
- **`stash_ref`** is carried and named, as on any run. Nothing pops it (`code-handoff.md:77`).

## 4. Restart rule, per phase and step

**Duplicates.** A re-entered step appends no entry it already appended before the run died. The test is per step, by the step's own record: the entry it would append is skipped where an identical one already stands **since that step began** — after the `step` write that opened it. A list as a whole is never de-duplicated: `report.commands_run` legitimately repeats a command with the same result.

| File state | Restart |
|---|---|
| `phase: Phase 1.4` (the default; `init` ran, Phase 1 not opened) | Re-run Phase 1.4 from its step 1. A recorded `stash_ref` is kept, and no second stash is pushed. A stash pushed before `stash_ref` was written is found as the `refs/stash` entry that is not `stash_before`, and recorded. HEAD moves already recorded in `branch_answer.moves` are not repeated: with no `tree` yet, the pre-check does not compare HEAD, so this row compares HEAD to the last recorded move and stops, naming both, where they differ. |
| `Phase 1`, `1.5`–`1.8` | Re-enter Phase 1 after 1.4. Questions with an answer in `clarifications` are not re-asked. Phase 1.7's summary is reused where `durable` holds it, and re-scanned otherwise. |
| `Phase 2A`, `2B`, with `step_groups` empty | `files.plan_file` set: go to Pre-Phase 3. Else, where `pending_plan_file` is durable: show it and ask the approval question. Else re-plan. 2B's dependency install is already gated by its own `node_modules` test (`implement.md:674`). Its repro simply runs again, since nothing is edited yet. |
| `Phase 2A`, `2B`, with `step_groups` non-empty (a mid-implementation re-plan) | Never test `plan_file`, which still holds the earlier approved plan. Where `pending_plan_file` is durable: show it and ask. Otherwise re-dispatch `risk-planner` (2B), or re-plan through Phase 2A (a `blocked` return's *Revise* at SIMPLE or MODERATE), with the `Work so far:` line. On approval, return to the phase that re-planned, 3A or 3B, at the first group not `done`, under the new plan's groups. |
| `Pre-Phase 3` | Re-run the phase, unless `continued_branch` is set. Adopt HEAD's branch only where its name is the one steps 1–2 resolve **and** HEAD equals that branch's tip as the file recorded it; otherwise cut the branch. That keeps a branch cut from the current position with the unit's commits, where `origin/<base>..HEAD` is not empty, and so never makes a duplicate `<name>-<sha>` branch. |
| `Pre-Phase 3.5` | Re-run the phase. No edit of the run's exists yet, so re-taking the baseline is correct. Its `Status` handling (`RUN_FAILED` and the rest) is reached as on any run. |
| `Phase 3A` / `3B` step groups | Skip `done` groups. A group whose `status` is null or `failed` is marked `failed`, where null, and a fresh entry is appended, as `implement.md:858` does. It is dispatched with its plan steps and a note: *an earlier attempt may have partly edited these files; read them as they stand and complete the group*. A group left at `needs_decision`, `trigger` or `blocked`: act on its durable report as step 1 does on a return. |
| `Phase 3A` / `3B` step 1 (patches) | A patch whose `outcome` is null: `git apply --check --reverse` against the tree. Passing means it was applied: record that and go on. Otherwise apply it. A temp patch file is re-read from `<default-ref>`. |
| `3B.4a` / `3.5` `test-writer` in flight | Re-dispatch with a note: *test files may already exist from an earlier attempt; extend or correct them, do not duplicate*. |
| `3B.5`–`3B.6` (`review_in_hand` set, no return) | Re-dispatch that review, same scope, same round. On a split round, re-dispatch only the reviews whose `return_file` is null. |
| `3B.7` (a return persisted) | Resume at triage. Triage entries with a `followed_by` are not re-applied. An in-flight `review-fixer` is re-dispatched with the "may have partly edited" note. |
| `3B.8`, or `3.5` | Re-run Phase 3.5 from the step `step` names. Above SIMPLE that is step 3 or later, never step 1, so tests are never written after the gate. **A fix attempt in flight** is re-dispatched **as the same attempt number**, as `implement.md:858` and `:978` retry a failed dispatch, with the "may have partly edited" note. Its check then runs. So a dead attempt 2 never leaves an unchecked half-fix with no attempt left. **Resuming at `3.5.6`** first re-runs the check (step 3 or step 4) to regenerate `failure_file`, which is not persisted. **Step 8's part-way `set phase`** back to Phase 3A or Phase 3B writes `step` too. |
| `Phase 4` | Re-dispatch only agents with no `report.maintenance` entry naming them (`agent`). Each re-dispatch carries the "may have partly edited" note. Memory edits outside the tree are not checked, a stated limit. |
| `Phase 4.5` | Re-ask the consent choice. `handoff-to-main` is re-entered as on any run. The builder confirms it meets a half-made handoff at its rows B and C, or else this row stops and names the branch. |
| `Phase 4.6` | **`code_repo_outcome` set:** skip the phase. **Otherwise:** the run's commit exists if and only if HEAD differs from `phase46_head`. Call `finish-code-branch` again as written: its empty run set goes straight to §2.4 (`code-handoff.md:83`). The consent question is asked unless `code_handoff_choice` holds its answer. A push of an up-to-date branch changes nothing, and §2.6's probe finds a pull request already open. |
| `Phase 4.7` | Append the block only where `<unit_folder>/implementation.md` holds none whose `commit:` the recorded commit's sha starts with. A block present but missing its `accepted:` gets `lineage.py accept` again. |
| `stopping` set (the run died inside a stop's tail) | Resume the stop, not the run *(r4)*: Phase 4.6 under its own row, then the stop's tail as *Ending early* gives it (cost, `remove`, `commit-artifacts`), with `stopping`'s reason in the report. Never Phase 4.7 or Phase 5 as a finished run. |
| `Phase 5`–`7` | Re-run from Phase 5. The report is rebuilt from the file, the follow-ups preview asks again, and the cost entry, the resume pointer, `remove` and `commit-artifacts` run as on any run. The report always says the earlier session's cost was not recorded, naming its id. |

## 5. Who changes what

- **`dev-workflows/scripts/run-state.py`:**
  - `format` 2;
  - `peek`;
  - `persist`;
  - `init --resume`;
  - the session guard (exit 9) and the script-owned keys;
  - the new keys and their defaults;
  - `step_groups[].started` stamping;
  - `remove`'s directory cleanup, and its fix for a missing file;
  - selftest cases for each, including a superseded writer refused, and `--resume` repointing and nulling paths.
- **`dev-workflows/commands/implement.md`:**
  - the detection step, pre-check and question (§3.3);
  - `persist` at every listed write (§3.4);
  - `tree` around every listed dispatch (§3.2);
  - `step`, `review_in_hand`, `phase46_head` and `code_handoff_choice` writes;
  - a `## Resuming a stopped run` section holding §4's table, cited from each phase;
  - Phase 0's resume path (§3.5);
  - the *Start fresh* notice;
  - the run-state contract and `KEYS_LINE`;
  - the invariants;
  - one line in **Ending early** (§3.3).
- **Expired sentences to rewrite:**
  - `implement.md:16` ("never this tail's to read or delete");
  - `:332` ("moved aside unread … not this run's state");
  - `:1529` ("never read");
  - `run-state.py`'s docstring;
  - the coding-subagents design's non-goal line, which gains a pointer.
- **`dev-workflows/agents/code-writer.md`, `test-writer.md` and `review-fixer.md`, and their handoff references:** the re-dispatch notes and what each means.
- **`workflows-core:session-hygiene` §6:** `/implement` joins the commands that resume from a kept session file. Regenerate its reference part.
- **Pages:**
  - `dev-workflows/docs/commands/implement.md`;
  - `docs/reference/resume-and-checkpoints.md`. Three copies exist (`dev-workflows`, `product-workflows`, `docs-workflows`); change each one that describes `/implement`, and check every one.
- **Rules:** `.claude/rules/dev-workflows-implement.md`'s invariant.
- **`docs/superpowers/to-fix.md`:** IMP-G5 is deleted.
- **Release:**
  - `dev-workflows` minor;
  - `workflows-core` patch, for `session-hygiene` §6;
  - one coupling bullet;
  - `product-workflows`, for its copy of `resume-and-checkpoints.md`.

## 6. Left to the builder

- The exact wording of the summary, the question and the notes.
- Whether `peek` shares code with `read`.
- Confirming `handoff-to-main`'s behaviour on a half-made handoff (§4, `Phase 4.5`). If it does not hold, that row stops the resume and names the branch.

## 7. Rulings (to check)

- **Snapshots around every tree-editing dispatch, not self-reported paths.** Only a snapshot can prove whose an edit is, and the tool already exists.
- **A step-level resume inside 3A, 3B, 3.5, 4 and 4.6, and phase-level elsewhere.** These are the phases where re-entering costs real work or repeats an action.
- **No liveness window.** A session guard in the script stops a superseded live run at its next write. The question names the other session at any age.
- **`format: 2`.** Files written before it get *Start fresh* only, since they hold no snapshots or durable copies.
- **Step 7.5's notes stay where they are.** On a resume, `/implement` skips its own gate call for a note proven to be the run's (byte-equal and on an unchanged `<default-ref>` blob), rather than restoring, re-applying, or changing `require-on-main`, which is GIT-G1's.
- **The dead session's cost is reported missing, not computed.**
- *(r4)* **A copy stands only for the file it copied** (§3.4): `{copy, of}`, dropped when its key moves on, repointed only where the key still names `of`.
- *(r4)* **A landed commit with a lost record is still resumable** (§3.3): differing paths must be exactly the committed ones, now clean.
- *(r4)* **Notes' blobs live in `conformance.note_blobs`,** leaving `conformance.annotated`'s shape and readers unchanged.
- *(r4)* **A run that dies inside a stop resumes the stop** (`stopping`), never as a finished run.
- *(r4)* **A superseded run after the resumed run finished.** `remove` leaves a tombstone, `implement-run.done`, naming the session that finished. For seven days `init --recover` refuses with exit 9 where the tombstone names another session. So the superseded run cannot recreate the file and commit.

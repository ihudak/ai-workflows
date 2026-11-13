# IMP-G5 Implement Resume — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** a new `/dev-workflows:implement` in a worktree where an earlier run died finds that run's state, proves the tree holds that run's work and nothing else, and resumes it at the step it died in. No commit, review or step group is repeated.

**Architecture:**
- `run-state.py` moves to format 2 and gains new keys, a session guard, durable copies that stand only for the file they copied, a read-only `peek`, `init --resume` and a tombstone.
- `/implement` records `tree-snapshot.py` snapshots around every action that can change the tree, persists the files a resume needs, and marks its steps.
- `/implement` detects a stopped run in Phase 0 and resumes it under a per-step restart table.

**Tech Stack:** Python 3.11 standard library (`run-state.py` and its selftest); markdown prose that agents execute; the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-12-imp-g5-implement-resume-design.md`, revision 4. The maintainer approved revision 3 on 2026-11-13; revision 4's additions are marked *(r4)*. Read it whole first; § numbers below are its own.

**Reviewed:** by Fable on 2026-11-13: *rework*, then *approve with changes*. Every finding is folded in.

**Where this plan and the spec differ, this plan's Global Constraints rule.** They settle what the reviews found after revision 4, including:
- the `note:` label;
- the exit-9 messages;
- the unnumbered phases' null `step`;
- `--recover`'s empty `durable`;
- the tombstone's lack of a window;
- dropping `code_handoff_choice`.

**Precondition:**
- Start only after D50 (`fix/d50-same-day-ordering`) has merged to `main`. D50 takes `dev-workflows` 4.63.0, and it changes `implement.md` Phase 4.7, `conformance-format` and `ready.md`.
- Then `git merge origin/main` into `feat/imp-g5-resume`. Never rebase it.
- Re-derive every line number this plan or the spec cites, by phrase, because the merge moves them.
- Re-read §4's Phase 4.7 row against D50's `at:` rule: the block a resume appends carries `at:`, and the "block present" test reads the block's `commit:`.

## Global Constraints

### `run-state.py`

These facts are exact. Task 1 implements them, and every later task relies on them.

**Format and exit codes**
- `format` is `2`. `init` writes 2. A format-1 file is offered for resume never: `peek` exits `8`.
- Exits in use today: 0 (done), 1 (no file), 2 (bad call), 3 (bad key or type), 4 (`OSError`), 5 (does not parse). Exit 6 is reserved by `implement.md` (its "no `run-state.py` call exits with it").
- New exits: **8**, a wrong format (`peek` and `init --resume`), and **9**, the session guard and the tombstone. Nothing else uses 8 or 9.

**Session and the stamps**
- **The session** comes from the environment variable `CLAUDE_CODE_SESSION_ID`, read in `main()` and passed to `run()` as a parameter. The selftest passes it explicitly and never reads the environment.
- **Name it bare** in commands, agents and references, with no `$`, because `check-docs` check 5 fails a `$`-variable there.
- **Who writes what:**
  - `init` writes `session` and `started`.
  - `init --resume` writes `session`.
  - Every call that changes the file stamps `updated`.
  - Nothing else touches `session`.
  - The two times are UTC `YYYY-MM-DDTHH:MM:SSZ`.
- **The guard:** `open`, `set`, `append`, `persist`, `remove` and `init --recover` exit 9 where the file's `session` and the caller's are **both non-null and differ**. `read`, `peek`, plain `init` and `init --resume` are not guarded.

**Script-owned keys**
- `set` refuses `session`, `started`, `updated`, `durable`, and `tree.snapshot` in **both** forms: the dotted `set tree.snapshot …`, and as a member of an object given to `set tree '{…}'`. Exit 3.
- Its meaning in `implement.md`'s exit list is "a command defect, never corrected and retried".

**New keys, with their defaults:**
- `session` null, `started` null, `updated` null;
- `step` null, `review_in_hand` null;
- `tree` `{"head": null, "snapshot": null, "when": null}` (`tree` itself is never null);
- `phase46_head` null (there is no `code_handoff_choice`: a resume re-asks `code-handoff` §2.4's consent question, which keeps that shared reference, also used by `/upgrade` and `/vuln`, unchanged);
- `durable` `{}`;
- `run_environment` null;
- `stash_before` null;
- `stopping` null;
- a new member `conformance.note_blobs` `{}`.

**List-entry members** (not checked by `KEYS`):
- `step_groups[].started`, which the script stamps on `append step_groups`;
- `report.maintenance[].agent`, written by the run: `docs`, `knowledge`, `instructions`, `impl-maintenance` or `defect-reporter`.

**`open <phase>`** sets `phase` and **resets `step` to null**.

**Persisting**
- `persist <label> <file>` copies `<file>` into `$(git rev-parse --git-path dev-workflows/implement-run.d)` and prints the copy's absolute path. It sets `durable[<label>] = {"copy": <that path>, "of": <file as given>}`.
- **The label** is a key path, or `note:<path>` for a note's working copy.
- **A negative list index** in a key path (`step_groups.-1.report`) is normalised to its absolute index, under the lock, before recording.
- **`persist tree.snapshot <file>` also writes `tree.snapshot`**, to the copy's path. It is the only writer of that key.
- **A copy another location reads is never overwritten.** A label's next `persist` replaces its copy in place, unless a location other than the label's own key, or another entry, names that copy: then it writes a fresh name.

**Dropping copies**
- `set`, after its write, drops each `durable` entry whose label is a key path that names neither its `of` nor its copy (both compared as absolute paths), and deletes that entry's copy where nothing else names it.
- **Never dropped by `set`:**
  - `note:` entries;
  - the `tree.snapshot` entry, whose key names the copy itself. Only the next `persist tree.snapshot` replaces it, and that replaces the copy.

**The durable directory and the tombstone**
- Plain `init` empties the durable directory.
- `init --recover` keeps the directory's files; its `durable` map starts empty, since the file it replaces was missing or unparseable (the last bullet below).
- `remove` deletes the directory even where the file is absent, under the lock. It skips any path inside the directory silently, since the directory goes whole. A `--keep` path inside the directory is first moved out, to `$(git rev-parse --git-path dev-workflows)/implement-run.kept-<basename>`, and printed `kept: <new path>`.
- **The tombstone.**
  - When `remove` deletes an existing file, it leaves a tombstone, `$(git rev-parse --git-path dev-workflows/implement-run.done)`, holding `{"session", "at"}`: the removed file's own `session`, or the caller's where the file holds none. A `remove` that finds no file writes none.
  - `init --recover` exits 9 where the tombstone's session and the caller's are both non-null and differ, as the guard does. There is no time window: any later run's plain `init` removes the tombstone, so it can meet only a superseded run.
- **`init --recover`** runs with the file missing or unparseable, so `durable` starts empty. Copies already in the directory stay orphaned until they are persisted again.

**`init --resume`**
- **Exits:** with no old file, exit 1; a file that does not parse, exit 5; format not 2, exit 8. The file is checked before stdin, so a missing file exits 1 whatever stdin holds.
- **The file** is rewritten **in place**, never moved aside.
- **Stdin** is a JSON object holding only these keys: `specs_git`, `specs_merged_branch`, `lineage`, `routing`, `coding_model`, `run_flags`, `inputs_read`, `report.notices`. Any other key exits 3.
  - `inputs_read` and `report.notices` are **appended** to the file's lists.
  - `routing` is **merged** over the file's own members, as `set` merges an object key, so `routing.history` survives.
  - The others replace the file's values.
- **What it writes:** it appends to `assumptions` `Resumed at <phase> step <step> after session <id> stopped at <updated>`, then writes `session`.
- **Its path rules** walk the key locations `named()` covers, plus `lineage.check_file`, through a new walker that returns `(key path, value)` pairs. `tree.snapshot` already names its copy. For each location, in this order:
  1. Where the path's file exists, leave it: a live file is never older than its copy.
  2. Else, where `durable[<key path>].of` names the value (compared as absolute paths) and the entry's `copy` is a file, repoint the location to that `copy`, and delete the original once if it exists and its name begins `dw-impl-`.
  3. Else, set it to null.

  No other location is touched.

**`KEYS_LINE`**
- It changes with `KEYS`.
- `implement.md`'s quote of it changes **in Task 1's commit**, so the selftest's equality check passes. `fresh()` in the selftest moves to format 2 with it.

### `implement.md`'s shared vocabulary

Tasks 2a to 3 all use these, exactly.

**`step` values.** The owning phase's token, a dot, and the step label as the command writes it.
- **Tokens:** `P3` for Pre-Phase 3, `3A`, `3B`, `3.5`.
- **Examples:** `P3.2`, `3A.1`, `3B.4a`, `3B.7.5`, `3.5.6`.
- **At MODERATE,** Phase 3A runs Phase 3B's steps 4a to 8. Those steps write `3B.<label>` while `phase` stays `Phase 3A`.
- **Unnumbered phases.** Pre-Phase 3.5, Phase 4 and Phase 4.6 have no numbered steps, so `step` stays null there. The question then names the phase alone.

**`tree.when`'s actions, a closed list:**
- `dispatch:<agent>`, where `<agent>` is `code-writer`, `test-writer`, `review-fixer`, `maintenance` or a split `test-writer` batch;
- `patch-apply`;
- `check-run:<lint|build|verify|typecheck|repro|install>`;
- `probe-strip`;
- `note`;
- `bisect`;
- `lift`;
- `put-back`;
- `commit`.

Each is written as `before <action>` or `after <action>`.

**The tree record.** Each is three calls: `tree-snapshot.py snapshot --dir <repo> > <temp>`, then `persist tree.snapshot <temp>`, then `set tree '{"head":"<HEAD sha>","when":"before <action>"|"after <action>"}'`.

**The exit-9 messages:**
- **The guard:** *This run's state now belongs to session <id>: another /implement resumed it, or this conversation's session id changed (as `/clear` does). Stopping without committing. Run /implement again in this worktree to resume it.*
- **The tombstone, from `init --recover`:** *Another session (<id>) resumed this run and finished it at <at>; its state is gone. Stopping without committing. Nothing is left to resume.*

### GIT-G1, rules files and prose

**GIT-G1's sections are not edited, except for named exceptions.** The sections:
- **Ending early**;
- the specs preflight;
- `branch-check`;
- `require-on-main`'s text;
- the specs-repo handover;
- the terminal `commit-artifacts`.

The exceptions, all in `implement.md`'s **Ending early** paragraph:
- the detection question's *Cancel*, added as a stop;
- the expired sentence, "never this tail's to read or delete";
- re-reading its ordering sentences ("a stop before Phase 1.4 creates the run-state file …"), since on a resume `init --resume` creates the file in Phase 0.

All three edits are named in the PR for the GIT-G1 owner. Never edit `specs-repo-git.md`, `phase-handoff.md`, `scripts/specs-git.py`, `.github/workflows/validate-catalog.yml` or `.claude/rules/workflows-core-git.md`.

**Generated parts.** `session-hygiene` loads by part. After editing it, run `python3 scripts/reference-parts.py generate`, then `check-parts`. Never edit `reference-parts/` by hand.

**Prose is executed.** Every sentence must be true of the run, with one reading only. Read a file with the Read tool before editing in its area. Locate sites **by phrase**, not by line number. Pages carry no `§`, D-numbers or review ids.

**Rules files** stay under 20,000 characters. Cut nothing to fit. `.claude/rules/dev-workflows-implement.md` is at 19,412; `.claude/rules/dev-workflows.md` is at 19,953, so any edit there must be net-zero.

**Gates before every commit:**
- `python3 scripts/validate-catalog.py`
- `./scripts/check-id-grammar.sh --root .` and `--baseline`
- `python3 scripts/reference-parts.py check-parts`, `check-citations`, `check-questions` and `check-branch-check`
- `./scripts/check-docs.sh --root .`
- `python3 plugins/dev-workflows/scripts/run-state.py --selftest`

Run them as one `&&` chain under `set -o pipefail`. Expected: `EXIT=0`, and 0 warnings from `validate-catalog.py`.

**Commits**
- `git branch --show-current` must print `feat/imp-g5-resume`.
- The message ends with this session's trailers:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01EcAVqApJxfCBcAbv5iWuu7
  ```
- Do not push.

## Review Focus

| # | Case | Expected | Owner |
|---|---|---|---|
| 1 | After a crash, the user edits a `pre_existing_dirty` path, or pops their stash | `tree.when` `before dispatch:*`: the listed paths are shown and the user is asked, with `pre_existing_dirty` paths marked as the user's. `after …`: the run stops and names the paths. The run never folds them in silently. | Task 3 |
| 2 | `/clear` in the same terminal, then `/implement` | The question names the earlier session. On *Resume*, `init --resume` takes the file over, and no age rule recommends Cancel. | Tasks 1 and 3 |
| 3 | A crash between Phase 4.6's commit and its push, with the "after commit" record lost | HEAD's first parent is `phase46_head`, the differing paths are exactly the committed ones and clean now, and *Resume* is offered. No second commit is made. Consent is asked unless `code_handoff_choice` holds it. | Tasks 3 and 2c |
| 4 | A resumed brief names an earlier step group's report | `init --resume` repoints it to its durable copy, so the `test -e` check never stops the run | Tasks 1 and 2b |
| 5 | A re-plan that dies before its new pending plan is written | The approved plan's copy was dropped when `pending_plan_file` was set to null, so the re-plan is dispatched again, and the old plan is never shown | Tasks 1 and 3 |
| 6 | A resume over step 7.5's notes in merged specs | The gate is skipped only for a note byte-equal to its `note:` copy on an unchanged blob. Otherwise the run stops and names the path. | Tasks 2d and 3 |
| 7 | A run that died inside a stop | Resumes as that stop, never as a finished run | Tasks 2d and 3 |

---

### Task 1: `run-state.py`

**Files:**
- Modify `plugins/dev-workflows/scripts/run-state.py`:
  - the docstring;
  - `KEYS`;
  - `run()`, which gains the session parameter and the `peek` and `persist` verbs;
  - `cmd_init`, which handles format 2, `--resume`, the directory and the tombstone;
  - `cmd_open`, which resets `step`;
  - `cmd_set`, which handles script-owned keys and dropping copies;
  - `cmd_append`, which stamps `started`;
  - `cmd_remove`, which handles the directory and the tombstone;
  - the new `cmd_peek` and `cmd_persist`;
  - the new walker;
  - `selftest()`, including `fresh()`.
- Modify `plugins/dev-workflows/commands/implement.md`: its `KEYS_LINE` quote only.

**Interfaces:** produces every fact in the Global Constraints' `run-state.py` section.

- [ ] **Step 1: The failing selftest cases.** Write one `check(...)` per fact in the Global Constraints' `run-state.py` section, passing the session explicitly. At minimum:
  - `peek` exits 1, 5 and 8, and on a good file exits 0 with no change;
  - `set` refuses each script-owned key in both forms;
  - `init` stamps `session` and `started`, a write stamps `updated`, and a null-session write leaves `session` unchanged;
  - the guard: each guarded verb exits 9 on `"A"` against `"B"`, every unguarded verb passes, and a null on either side passes;
  - `open` resets `step`;
  - `persist`:
    - prints the copy's path and records `{copy, of}`;
    - normalises `-1`;
    - for `tree.snapshot`, writes the key;
    - `persist tree.snapshot`, then `set tree '{"head":…,"when":…}'`: the copy still exists, and `--resume` leaves the key alone;
  - setting `files.pending_plan_file` to null drops its entry and copy;
  - a `note:` entry survives `set`;
  - plain `init` empties the directory and removes the tombstone, and `--recover` keeps the directory;
  - `remove` deletes the directory when there is no file, and leaves the tombstone;
  - `init --recover` exits 9 against a tombstone from another session, and a `remove` with no file writes no tombstone;
  - `init --resume`:
    - exits 1, 5 and 8;
    - refuses a stdin key outside its list;
    - appends to `inputs_read` and `report.notices`;
    - leaves a path whose file exists, even where a copy exists;
    - repoints a missing path whose `of` still matches, and deletes its `dw-impl-` original where present;
    - nulls a missing path with no matching entry;
    - leaves `pre_existing_dirty[0].path` and `unit_folder` alone;
    - writes the `assumptions` line and `session`;
  - `append step_groups` stamps `started`;
  - `KEYS_LINE` holds every new key, and `implement.md`'s quote equals it;
  - Review Focus 4: a `step_groups.0.report` persisted, its temp deleted, then `--resume` repoints it to the copy.

  Also change `cmd_init`'s `assumptions` string, "moved aside unread", wherever plain `init` now says more, and the selftest assertion of it.
- [ ] **Step 2: Run the selftest.** `python3 plugins/dev-workflows/scripts/run-state.py --selftest`. Expected: the new cases fail or error (they call a `run()` signature that does not exist yet), and the existing cases PASS.
- [ ] **Step 3: Implement**, exactly as the Global Constraints state. Update the docstring's verbs and exit codes, and `implement.md`'s `KEYS_LINE` quote.
- [ ] **Step 4: Run the selftest.** Expected: PASS, every case.
- [ ] **Step 5: Gates.** Expected: PASS, with 0 warnings.
- [ ] **Step 6: Commit**: `feat(imp-g5): run-state.py format 2 — session guard, peek, persist {copy, of}, init --resume, tombstone`.

### Task 2a: `implement.md`'s run-state contract and Phase 1.4's records

**Files:**
- Modify `plugins/dev-workflows/commands/implement.md`:
  - the run-state contract: the keys' meanings, "The calls", and the exit-code list;
  - Phase 1.4.

- [ ] **Step 1: Inventory.** In the report, list every statement of exit 4's consequence: grep `\`4\`` and "could not be reached" and "end-of-run removal" in `implement.md`. Give each a disposition.
- [ ] **Step 2: The contract.**
  - The meaning of every new key.
  - `peek`, `persist` and `init --resume` in "The calls".
  - Exit 8, which never reaches a phase.
  - Exit 9 as a stop at every exit-4 site found in Step 1: no Phase 4.6, no removal and no `--recover`, with the guard's message.
  - The `1`/`5` bullet that sends the run to `init --recover` says that `--recover`'s exit 9 is the tombstone case, a stop with the tombstone's message.
  - The "what stays behind" sentence beside the `.stale-` file and the lock names `implement-run.done`.
  - Exit 3's script-owned case: a command defect.
- [ ] **Step 3: Phase 1.4.**
  - `stash_before` is written before any stash push.
  - `run_environment` is written with the members `session-hygiene` §6 compares. Read §6 for the exact names; the review found `specs_path`, `specs_origin`, `repos_path` and `reference_loader`. Name them in `implement.md` itself, with "set `run_environment` is how this command rewrites the section §6 names".
- [ ] **Step 4: Gates.** Expected: PASS.
- [ ] **Step 5: Commit**: `feat(imp-g5): /implement's run-state contract — new keys, peek, persist, --resume, exits 8 and 9`.

### Task 2b: `persist` at every site

**Files:** modify `plugins/dev-workflows/commands/implement.md`, wherever a file in spec §3.4's list is written.

- [ ] **Step 1: Inventory.** In the report, list every write site, found by phrase, for each of:
  - `task_description_file`
  - `plan_file`
  - `pending_plan_file`
  - `summary_file`
  - `baseline_file`
  - `test_report_file`
  - `review_return_file`
  - `review_file`
  - `claims_file`
  - `snapshot_before`
  - each `step_groups[].report`
  - each `reviews[].return_file`

  Give a count.
- [ ] **Step 2:** After each write, add `persist <key path> <file>`, at every write of that file. Use absolute indexes or `-1`; the script normalises.
- [ ] **Step 3: Close.** Re-grep, and record in the report that the persist count equals the site count.
- [ ] **Step 4: Gates.** **Step 5: Commit**: `feat(imp-g5): /implement persists every file a resume needs`.

### Task 2c: Tree records

**Files:** modify `plugins/dev-workflows/commands/implement.md`, around every action in `tree.when`'s list.

- [ ] **Step 1: Inventory.** In the report, list:
  - every `→ Agent (subagent_type:` line for `code-writer`, `test-writer` and `review-fixer`, and the Phase 4 maintenance agents, which are written as `**Agent 1 —` to `**Agent 4 —`. The reviewer derives the count independently: 3 `code-writer`, 3 `test-writer` and 1 `review-fixer` arrow lines, plus the Phase 4 block;
  - every scan-patch `git apply`;
  - every check run (lint, build, verify, type-check, repro, install), with the `snapshot_after` it already takes;
  - the probe strip;
  - every write of a note into this repository;
  - every bisect and its reset;
  - Phase 4.6's commit;
  - every session-branch `lift` and `put-back`.

  Give each a disposition and a count.
- [ ] **Step 2:** Add the before and after tree records around each, in the Global Constraints' record form.
  - Parallel dispatches: one record per batch.
  - Check runs: persist `snapshot_after` as `tree.snapshot` and set `head` and `when` from it, instead of a second snapshot.
  - Phase 4.6: the `before commit` and `after commit` records wrap the whole `finish-code-branch` call, its commit, push and pull request. `phase46_head` is written after §8.2's session-branch commit and lift (where the `implement.md` text puts them), immediately before that call.
  - **Check runs** take no `before` record of their own: `snapshot_before` already is one. Their `after` record is the settled `snapshot_after`.
- [ ] **Step 3: Close.** Re-grep, and record that each inventoried site has its pair of records.
- [ ] **Step 4: Gates.** **Step 5: Commit**: `feat(imp-g5): /implement records the tree around every action that can change it`.

### Task 2d: `step` and the remaining keys

**Files:** modify `plugins/dev-workflows/commands/implement.md`.

- [ ] **Step 1: Inventory.** List every numbered step of Pre-Phase 3, 3A, 3B and 3.5, each with its `step` value from the vocabulary.
- [ ] **Step 2: Write each one.**
  - Write `step` at each step.
  - Phase 3B step 8's part-way `set phase` also writes `step`.
  - `review_in_hand` is set where `code-review` is dispatched, and cleared when that round's triage settles.
  - `report.maintenance` entries carry `agent`. The feedback step's entry is `defect-reporter` or `impl-maintenance`, as the run dispatched.
  - At every site that writes `conformance.annotated` — step 7.5, the departure note at the edit, and Phase 3A step 6 — write `conformance.note_blobs[<path>]` with the path's blob on `<default-ref>`, and `persist note:<path> <path>`.
  - Phase 4.6, when entered by a stop, first writes `stopping` with the stop's reason. Phase 4.6 is `/implement`'s own; no GIT-G1 text changes.
- [ ] **Step 3: Close.** Count the `step` writes against Step 1's inventory, and the `note_blobs` writes against the sites that write `conformance.annotated`. Record both counts.
- [ ] **Step 4: Gates.** **Step 5: Commit**: `feat(imp-g5): /implement marks its steps, the review in hand, the consent answer, note blobs and a stop's reason`.

### Task 3: Detection, the question, the resume path, the restart table

**Files:** modify `plugins/dev-workflows/commands/implement.md`, plus the sweep's hits in `.claude/rules/dev-workflows-implement.md`, `plugins/dev-workflows/references/context-management.md` and `docs/maintainers/rationale.md`. `run-state.py`'s string is Task 1's; the pages are Task 4's. In `implement.md`:
- Phase 0's detection, right after the working directory is classified as a code repository;
- Phase 0's resume path;
- the *Start fresh* path;
- the new section `## Resuming a stopped run`;
- the invariants;
- the three **Ending early** edits named in the Global Constraints.

**Interfaces:** consumes Tasks 1 and 2a–2d, through the shared vocabulary.

- [ ] **Step 1: Detection.**
  - **`peek` and its exits.**
  - **The pre-check** (spec §3.3):
    - HEAD must be an expected HEAD;
    - `tree-snapshot.py compare` against `tree.snapshot`;
    - unequal at `before dispatch:*`, `before patch-apply`, `before probe-strip` or `before note`: list the paths, marking `pre_existing_dirty` ones as the user's, and ask *Resume — they are the run's*, *Start fresh* or *Cancel*;
    - a check run that died (the last record is the run's `snapshot_before` with no settled `snapshot_after`): never attribute. *Resume* re-enters that check's settlement, *A check run's files*, against the persisted `snapshot_before`. The junk a dead check leaves is settled there, never swept into the commit;
    - unequal at `before lift` or `before put-back`: settled by the preflight's own `put-back` and lift on the resume path;
    - unequal at `before bisect`: the running-bisect rule below;
    - unequal at `before commit`: apply the committed-landed rule (r4);
    - unequal after any `after <action>`, or HEAD unexpected: offer *Start fresh* and *Cancel* only;
    - `tree.snapshot` null: no comparison;
    - `stash_ref` must be present in `git stash list --format=%H`;
    - a running bisect, found via `$(git rev-parse --git-path BISECT_LOG)`, offers *Start fresh* and *Cancel*, naming `git bisect reset`.
  - **The arguments-differ rule.**
  - **The question**, verbatim (spec §3.3), with at most 3 options and `step` null shown as the phase alone.
  - **Session-branch mode** (`session_branch_lift: true`): ask first, offering *Resume* pending the check. On *Resume*:
    1. run the preflight for the file's key set, `put-back`, and lift again;
    2. then compare;
    3. a failed comparison runs `put-back` and stops, telling the user to run `/implement` again to start fresh.
- [ ] **Step 2: The resume path** (spec §3.5).
  - Take from the file, re-run, re-resolve and skip exactly as §3.5 says.
  - Run the environment check against `run_environment`, through `session-hygiene resume-environment`.
  - The step 7.5 gate-skip uses `note_blobs` and the `note:` copies.
  - Lift again in session-branch mode.
  - `stash_ref` is carried and named.
  - Then call `init --resume`, with the fresh Phase 0 facts on stdin, from the allowed keys only.
  - `init --resume` keeps `step`. After each re-entered phase's `open`, write `step` back from the value `peek` printed.
- [ ] **Step 3: *Start fresh*.** Gather the notice's facts at detection, from `peek` and the comparison, into `report.notices` on plain `init`'s stdin. Print them before the dirty-tree question.
- [ ] **Step 4: `## Resuming a stopped run`.**
  - Spec §4's table, every row including the r4 `stopping` row, and its duplicates rule.
  - Each phase cites the section once.
  - The Phase 4 row skips agents that `run_flags.skip_feedback` left out.
  - The Phase 4.6 row: with no `code_handoff_choice`, the consent question is asked again on a resume.
- [ ] **Step 5: The invariants, Ending early and the sweep.**
  - The invariant: *a run found in the worktree is offered for resume before the address is resolved, and resumes only on a proven tree*.
  - The three **Ending early** edits.
  - **A subject sweep** for "the earlier run's file", by phrase: "moved aside unread", "an earlier run left", "never read", "not this run's state", "never this tail's to read". Cover the claim-sweep scope, including:
    - `.claude/rules/dev-workflows-implement.md`;
    - `plugins/dev-workflows/docs/commands/implement.md`;
    - `plugins/dev-workflows/references/context-management.md`;
    - `docs/maintainers/rationale.md`;
    - `plugins/dev-workflows/docs/commands/implement.md`, recorded for Task 4.

    Record before and after counts. Rewrite each sentence true in the files this task owns; leave the page's hits to Task 4.
- [ ] **Step 6: Review Focus.** Check items 1 to 7 against their deciding sentences. Quote each in the report.

**A stated limit, written into `## Resuming a stopped run`:** a stop that runs no Phase 4.6 writes no `stopping`. If it dies in its tail, it is offered for resume at its phase, even after a *Cancel*. Answering *Start fresh* there gives the stop's effect.
- [ ] **Step 7: Gates.** **Step 8: Commit**: `feat(imp-g5): /implement offers to resume a stopped run, on a proven tree, at its step`.

### Task 4: Agents, `session-hygiene` §6, pages, rules, `to-fix`

**Files:**
- `plugins/dev-workflows/agents/code-writer.md` and `references/handoff/code-writer.md`.
- `agents/test-writer.md` and `agents/review-fixer.md`: their briefs live in those files and in `implement.md`'s dispatch text, since no handoff file exists for either.
- `plugins/workflows-core/references/session-hygiene.md` §6, then regenerate its parts.
- `plugins/dev-workflows/docs/commands/implement.md`.
- Each `docs/reference/resume-and-checkpoints.md` copy that describes `/implement`'s run-state.
- `.claude/rules/dev-workflows-implement.md`: the invariant, under 20,000 characters, cutting nothing.
- The non-goal line at `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md`, which gains a pointer.
- `docs/superpowers/to-fix.md`: delete IMP-G5.

- [ ] **Step 1: The agents.** Each can receive the note *an earlier attempt may have partly edited these files; read them as they stand and complete the work*. State what that means: read before editing, extend rather than duplicate, and never assume a clean start. For `test-writer`: tests may exist; extend or correct them, and never duplicate.
- [ ] **Step 2: `session-hygiene` §6.** `/implement` joins the commands that resume. Its record is the run-state file's `run_environment`, and it compares the same members. Then run `generate` and `check-parts`.
- [ ] **Step 3: The pages and the invariant.**
  - The `/implement` page covers:
    - resuming a stopped run;
    - what is proven first;
    - the three answers;
    - that runs from before this release offer *Start fresh* only.
  - Change only the `resume-and-checkpoints` copies that describe `/implement`'s run-state. The review found none in `product-workflows` or `docs-workflows`; confirm.
- [ ] **Step 4: The pointer and `to-fix`.**
- [ ] **Step 5: Gates.** **Step 6: Commit**: `feat(imp-g5): agents' re-dispatch notes, session-hygiene §6, pages, rules, to-fix`.

### Task 5: Release

- [ ] **Step 1: Versions.** Run `git fetch origin` and take the next free versions:
  - `dev-workflows`: minor;
  - `workflows-core`: patch, for §6;
  - `product-workflows` and `docs-workflows`: patch, only if Task 4 changed their pages.

  `plugin.json` must equal `marketplace.json`. Date each CHANGELOG section.
- [ ] **Step 2: The coupling bullet.**
  - **Newer `dev-workflows` beside older `workflows-core`:** §6 does not list `/implement`. That is wording only, since `implement.md` names `run_environment`'s members itself.
  - **Newer pages beside older `dev-workflows`:** the pages describe a resume the command lacks. Name each plugin.
  - Measure the coupling file. Above 19,000 characters, move its oldest `workflows-core` bullets byte for byte into the existing `plugin-updates-coupling-history-3.md`, and update every range pointer: the coupling intro, `history.md`'s intro, `history-3.md`'s title and intro, `plugin-updates.md`, and `CLAUDE.md`'s table.
- [ ] **Step 3: Gates.** Measure the rules files and `CLAUDE.md`.
- [ ] **Step 4: Commit**: `release(imp-g5): …`, naming the versions.

### Task 6: Close

- [ ] **Step 1: Consistency.** Every name used in `implement.md` must exist in `run-state.py`, and the reverse. Check with:
  ```
  grep -o 'run-state.py [a-z-]*\( --[a-z]*\)\?' plugins/dev-workflows/commands/implement.md | sort -u
  ```
  against `run()`'s verbs. Check the `step`, `tree.when` and exit-code values the same way.
- [ ] **Step 2: GIT-G1.** In `git diff origin/main...HEAD`, the only hunk in a GIT-G1 section is the three named **Ending early** edits.
- [ ] **Step 3: The full CI list.** Every `--selftest` that `validate-catalog.yml` runs, plus mermaid where `node` exists.
- [ ] **Step 4: The whole-branch review.** This is the controller's job, with Fable as the final reviewer.

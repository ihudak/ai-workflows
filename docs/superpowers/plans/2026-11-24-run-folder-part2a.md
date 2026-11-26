# Run folder, Part 2a — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The six `dev-workflows` and `security-workflows` commands that dispatch agents or ask for approvals mid-run (`/conformance`, `/design`, `/ready`, `/upgrade`, `/vuln`, `/scan`) resume a stopped run like `/prd-ground` does. The shared mechanism grows what they, and Parts 2b–2d after them, need.

**Architecture:** The Part 1 script and reference gain:
- writers (`writer`, `tree-note`);
- content the orchestrator writes itself (`put`);
- interview answers in order (`answers`);
- pins for results whose agent decides what it read (`--pin`, `--redo`);
- a keyless run's other unfinished runs (`open`'s `others`).

A new `workflows-core:agent-file` skill names a `workflows-core` agent's definition file for a sibling plugin's command. Shared references guard the end-of-run tail and save the dispatches they make for a command. Each command then names its own dispatches, questions, effects, facts and stops per the reference's §6.

**Tech Stack:** Python 3.11 standard library; markdown command, agent, reference, skill and rules files executed literally by agents; GitHub Actions (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-24-run-folder-design.md`. Part 2a is *D18, amended*'s first item. It implements:
- D19–D31 for the mechanism;
- D13 for `dev-workflows`;
- D16 for `/upgrade` and `/vuln`;
- D6, D6a, D7, D8 and D11 for the six commands.

**Survey:** `.superpowers/survey/run-folder-part2/` (git-ignored working notes, written 2026-11-24 against `main` at `9cca8c452`). For each command task, its section of `A-dev-security.md` is the map of dispatches, questions, side effects, `mktemp` files and stops. `G-shared-references.md` covers the shared references, the cross-plugin agents and the writers. Re-check each claim against the file before relying on it: the survey is a reading, not the source.

## Global Constraints

Carried from Part 1:
- Location: `${XDG_STATE_HOME:-$HOME/.local/state}/ai-workflows/runs/<run-key>/`, mode `0700`.
- Never fail a command because of its run folder. A call that exits 2, or with any exit the reference's §2 does not name, makes the folder unavailable after one `NOTE:`, and the run goes on as it does without one.
- Exit **9** stops the run at once, writing nothing more: no tail, no stop line, no commit. Each command names its own taken-over stop.
- The fingerprint covers the input's bytes, attached run-folder files (sorted by path), the agent definition file's SHA-256 and the model. Nothing else counts.
- D7a: **10** changed results or fewer are redone without asking.
- Pruning after **30 days**.
- The script is `run-folder.py`, called as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-folder.py" <subcommand> …`. Every copy is byte-identical to `workflows-core`'s, which CI checks.
- `/implement` and `dev-workflows/scripts/run-state.py` are not touched. `/implement` cites `context-management.md`'s `mktemp` rule and keeps its own removal (its `run-state.py`). The D13 rewrite must leave `/implement`'s text true.
- Prose is executed: a false sentence in a command, agent, reference, skill or rules file is a defect. Cite code by heading and quoted snippet, never by line number.
- Edits to `CLAUDE.md` and `.claude/rules/*.md` follow `plugins/workflows-core/references/instruction-file-maintenance.md`:
  - each rules file stays under 20,000 characters;
  - every number written there is re-derived with the command that counts it, stated beside it;
  - `CLAUDE.md` is near its 36,000-character warning, so add nothing to it but a rules-table row where one is required.
- Gates before each commit:
  - `./scripts/check-id-grammar.sh --root .`;
  - `./scripts/check-docs.sh --root .` (run it with a 600000 ms timeout: it takes minutes);
  - `python3 scripts/validate-catalog.py`;
  - `python3 scripts/reference-parts.py check-parts`, `check-citations`, `check-questions` and `check-branch-check`;
  - the `--selftest` of every script the task changed.
- Read a file in an area with the Read tool before editing there, so its rules file loads.
- Check 5 of `check-docs.sh`: do not write `$XDG_STATE_HOME` or `$HOME` in a file outside `workflows-core`.
- Every `— Unreleased` CHANGELOG section is dated before it reaches `main`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

New in Part 2:
- **Byte-stable inputs and shown texts (D7, D8, D21).**
  - Every saved dispatch's input and every recorded question's shown text is built from the command's fixed text plus values taken from files, facts or the run folder, in a fixed order.
  - Content the orchestrator generates — a brief, a plan, a requirement list, a frame, a summary — is written with `put` when it is generated. It is read back from that file, and never generated again on a resumed run.
  - A file the run itself changes later is copied into `scratch/` at the dispatch and attached (D23).
- **Agent files.**
  - An agent of the calling plugin: `${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md`.
  - A `workflows-core` agent: the path `Skill(skill: "workflows-core:agent-file", args: "<agent>")` prints.
  - Not saved, each run as before (D19): `general-purpose` dispatches, other plugins' agents, and the end-of-run maintenance and defect dispatches. The maintenance step is guarded whole as an effect (D28).
- **Writers (D20).**
  - A dispatch that edits files in a git work tree goes through `run-writer`, never `run-dispatch`.
  - After every edit, commit or revert the command itself makes in a writer's tree, it calls `tree-note` on that tree, so the run's own changes never read as `changed` on resume.
- **Facts (D25).**
  - A value read from a clock, the web or a mutable selector is a `fact`, set by the first session and read by every later one.
  - A value too large for a command line is a `put` file.
- **Placement of `open-run` (D24).**
  - It goes after address resolution and after the refusals that do not depend on this run's own writes.
  - Every check this run's own earlier write would trip, and every step that stashes, switches or cuts a branch, comes after `open-run`. On a resumed run it reads the run's facts and effects.
  - Each command lists these checks and steps by heading.
- **One question, never two (D5).** `/design` folds the run folder's resume question into its `_design-session.md` question.
- **Versions.** Take the next minor of whatever is on `main` when Task 12 runs:
  - `workflows-core` 1.99.1 → 1.100.0;
  - `dev-workflows` 4.70.4 → 4.71.0;
  - `security-workflows` 0.12.8 → 0.13.0;
  - `product-workflows` 3.87.1 → 3.87.2, for its copy of the script only.

## Review Focus

1. **The run's own later edit reads as an outside change.** `/upgrade`'s `review-fixer` runs after `upgrade-executor` on the same files, and the orchestrator commits between them. On resume, both must come back `intact`, not ask. Pinned in Task 2 (`writer-later-own-write-intact`, `tree-note-commit-intact`) and in Tasks 10–11's `tree-note` placement.
2. **An executor killed mid-edit.** A resumed `/upgrade` or `/vuln` meets `interrupted`. It must revert to that component's `pre_edit_tree` and redo the component. It must not stash the partial work in Phase 0.5, and must not cut a second branch. Pinned in Task 2 (`writer-interrupted`) and Task 5 (`code-handoff.md`).
3. **A clone pulled between two sessions** under `/design`'s scan. The `code-scanner` result's pin no longer holds, so it is redone, not reused. Pinned in Task 1 (`pin-recorded-and-returned`, `redo-forces-dispatch`) and Task 4's pin rule.
4. **A brief regenerated on resume.** `/ready`'s reviewer brief, `/conformance`'s requirement list and `/design`'s interface frame are written with `put` the first time and read back, so their fingerprints match. Pinned in Task 1 (`put-atomic-owner-checked`) and checked by each command task's reviewer against the input-building rule.
5. **A keyless `/vuln` started again in the same repository with other CVE tokens** offers the other unfinished run rather than silently starting fresh. Pinned in Task 1 (`open-keyless-others`) and Task 3's `open-run` question.

---

### Task 1: `run-folder.py` — `put`, `answers`, pins, keyless `others`, the copies

**Files:**
- Modify: `plugins/workflows-core/scripts/run-folder.py`
- Create (copies): `plugins/dev-workflows/scripts/run-folder.py`, `plugins/security-workflows/scripts/run-folder.py`
- Modify (copy): `plugins/product-workflows/scripts/run-folder.py`
- Modify: `.claude/rules/workflows-core-bounded-run.md` (where it lists which plugins ship which copied script, if it does)

**Interfaces:**
- Produces:
  - `put <folder> <rel> --from -`. Writes stdin to `<folder>/<rel>` atomically (a temporary file in the same directory, then a rename), owner-checked and under the lock. `<rel>` must lie under `scratch/` and must not contain `..`; any other value is a usage error (exit 2). Parent directories are made `0700`. Prints `{"path": <absolute path>, "sha256": <hex>}`.
  - `gate-record … --keep-shown`. Also saves the shown bytes to `gates/<id>.md`.
  - `answers <folder> [--match <substring>]`. Reads only. Prints `{"answers": [{"id", "answer", "at", "shown": <absolute path or null>}]}` for every recorded gate whose id contains the substring, in the order each id was **first** recorded (a re-record keeps its place). It needs a per-gate sequence number, since `at` has one-second resolution.
  - `done … --pin <name>=<value>` (repeatable). Stores the pins on the result record.
  - `dispatch` on `action: reuse` adds `"pins": {…}` (`{}` where none).
  - `dispatch … --redo`. Dispatches anew even where a recorded result's fingerprint matches, with the same effects as a fingerprint mismatch: a new nonce, the old files removed.
  - `open` on a keyless run (no `--key`) with `--workdir` also returns `"others"`. The list holds every unfinished run under `runs/` with the same `--command` and the same working-directory identity whose arguments differ, as `{"folder", "args", "started", "updated", "last_phase", "results", "owner"}`, sorted by `updated`, newest first, at most 3. On a keyed run, or without `--workdir`, it is `[]`. It is computed whether `state` is `new` or `unfinished`.

- [ ] **Step 1: Write the failing self-tests**, as cases in `selftest()` in the file's existing style, named:
  - `put-atomic-owner-checked`: `put` writes the bytes, and `sha256` matches them. A second `put` replaces them. A call from another session exits 9 and leaves the file unchanged. `put` to `inputs/x`, `../x` or `/abs` exits 2.
  - `answers-in-first-order`: record `g-002`, `g-001`, then `g-002` again. `answers` lists `g-002`, `g-001` with the second answer for `g-002`. `--match g-00` filters. `shown` is a path only for a record made with `--keep-shown`, and that file holds the shown bytes.
  - `pin-recorded-and-returned`: `done --pin commit=abc --pin ref=origin/main`, then the same `dispatch` returns `action: reuse` with `pins == {"commit": "abc", "ref": "origin/main"}`.
  - `redo-forces-dispatch`: `dispatch --redo` on a reusable result returns `action: dispatch` with a new result path. The old result file is gone, and `results` no longer lists the id.
  - `open-keyless-others`: two keyless `open`s with the same `--workdir`, the same command and different `--args` give two folders. The second `open`'s `others` names the first, with its args. A keyed `open` has `others == []`. A run that is `close`d is not listed.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/run-folder.py --selftest`. Expected: the five new cases FAIL and every earlier case passes.
- [ ] **Step 3: Implement** the subcommands and flags above. `put`, and `gate-record --keep-shown`, are writes: they go through `needs_lock` and the owner check like every other write. `answers` reads without the lock, as `gate` does.
- [ ] **Step 4: Run the self-test.** Expected: every case PASS, no other line.
- [ ] **Step 5: Copies.** `cp` the script to `plugins/dev-workflows/scripts/`, `plugins/security-workflows/scripts/` and `plugins/product-workflows/scripts/`. Check that `cmp` is silent for each. Confirm that the CI loop *Every plugin's copied scripts are the same* (`validate-catalog.yml`) already covers `run-folder.py` in every plugin that ships one, without edits; fix it if not.
- [ ] **Step 6: Gates** (*Global Constraints*), then **commit**: `feat(workflows-core): run-folder.py keeps the orchestrator's own files, interview answers, pins and a keyless run's other runs`.

### Task 2: `run-folder.py` — writers

**Files:**
- Modify: `plugins/workflows-core/scripts/run-folder.py` and its three copies.

**Interfaces:**
- Consumes: Task 1's script.
- Produces:
  - **`writer <folder> <id> --tree <dir> [--scope <rel>]… --agent <name> --agent-file <file> --model <model> --input - [--attach <path>]…`.**
    - The fingerprint is computed as `dispatch` computes it. The record lives under `writers` in `run.json`, apart from `dispatches` and `results`. `<dir>` must be a git work tree (else exit 2). It is recorded by its physical path.
    - **No record, or a record whose fingerprint differs.** The call snapshots the scope, records the writer `started` with the snapshot, and prints `{"action": "dispatch", "receipt": <new path main/results/<id>.<nonce>.md>}`. Owner-checked.
    - **A `started` record with the same fingerprint.** `{"action": "interrupted", "receipt": …, "left": [{"path", "before", "now"}]}`: the paths whose state now differs from the snapshot.
    - **A `done` record with the same fingerprint.** `{"action": "intact", "receipt": <recorded file>}` where every path the writer changed is in the state the run last left it in. Otherwise `{"action": "changed", "receipt": …, "changed": [{"path", "expected", "now"}]}`.
    - Reads take no write: `interrupted`, `intact` and `changed` write nothing.
  - **The snapshot of a scope.** `git -C <dir> status --porcelain=v1 -z --untracked-files=all -- <scope…>`, or the whole tree with no `--scope`. Each listed path maps to a content hash (SHA-256 of its bytes, of the link text for a symlink, `"-"` where absent). A path not listed is `"clean"`.
  - **`done <folder> <id> [--from -]` on an id whose writer record is `started`.** Takes the after-snapshot of the same scope and computes `wrote`: every path whose before and after state differ, mapped to its current hash or `"-"`. It merges `wrote` into the run's per-tree map `trees[<dir>]` (path → hash), saves the receipt like a result (`--from -`, or the file at `receipt`; empty or missing exits 3), and marks the record `done`.
  - **`tree-note <folder> --tree <dir> [--scope <rel>]…`.** For every path under the scope that `trees[<dir>]` already names, or that the snapshot lists, sets `trees[<dir>][path]` to its current hash or `"-"`. Owner-checked. Prints `{"noted": <count>}`.
  - **The `intact` test.** For each path in the record's `wrote`: its current hash, or `"-"`, equals `trees[<dir>][path]`. The comparison is with the run's latest state, not with the writer's own `wrote`, so a later writer of this run, or a `tree-note`, on the same path is not a change.
  - **`stale` and `keep`** also cover writer records: a writer whose agent file or model changed counts in `total`.

- [ ] **Step 1: Write the failing self-tests** (each builds a throwaway git repository in a temp directory):
  - `writer-dispatch-then-intact`: dispatch, edit a file, `done`. The same `writer` call returns `intact` with the recorded receipt.
  - `writer-outside-change`: after `done`, change the file outside the run. `writer` returns `changed` naming the path, with `expected` and `now`.
  - `writer-later-own-write-intact`: writer A edits `f`. Writer B (another id) edits `f` again, `done`. Writer A's call returns `intact`.
  - `tree-note-commit-intact`: after writer A's `done`, commit `f` and run `tree-note`. A returns `intact`. Without the `tree-note`, a later edit of `f` makes it `changed`.
  - `writer-interrupted`: `writer` (dispatch), edit `f`, no `done`. The same call returns `interrupted` with `left` naming `f`.
  - `writer-deleted-path`: the writer deletes a tracked file. `wrote` maps it to `"-"`. It stays `intact` while the file is absent and becomes `changed` once it is restored.
  - `writer-not-a-git-tree`: `--tree` on a plain directory exits 2.
  - `writer-owner-guard`: a `writer` dispatch from another session exits 9 and records nothing.
- [ ] **Step 2: Run the self-test.** Expected: the eight new cases FAIL.
- [ ] **Step 3: Implement.** Use `subprocess` with `git -C`, as the script already asks `git` for an origin. Read `-z` output as bytes and decode with `surrogateescape`.
- [ ] **Step 4: Run the self-test**: all PASS. Then copy the script to the three plugins; `cmp` is silent for each.
- [ ] **Step 5: Gates**, then **commit**: `feat(workflows-core): run-folder.py records what a writer changed and finds it on resume`.

### Task 3: the reference, the `agent-file` skill, rules and docs

**Files:**
- Modify: `plugins/workflows-core/references/run-folder.md`, `.claude/rules/workflows-core-run-folder.md`, `.claude/rules/workflows-core.md` (its skill count, if it states one; re-derive), `plugins/workflows-core/docs/reference/references.md`, the `workflows-core` docs page that lists its skills (find it with `grep -rln 'specs-git' plugins/workflows-core/docs`)
- Create: `plugins/workflows-core/skills/agent-file/SKILL.md`

**Interfaces:**
- Consumes: Tasks 1–2's subcommands.
- Produces for every later task:
  - **The `agent-file` skill.** `Skill(skill: "workflows-core:agent-file", args: "<agent>")`. Frontmatter: `user-invocable: false`, `allowed-tools: Bash`. Its text has the run make one Bash call, `test -f "${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md" && printf '%s\n' "${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md"`. It refuses an argument that is not `^[a-z0-9-]+$`. The printed line is the `--agent-file` value. A call that prints nothing means the dispatch runs unsaved, as without a folder, with no `NOTE:`.
  - **New entry point `run-writer`** (D20, Task 2's `writer`):
    - `dispatch` → make the call, then `done` (with `--from -` where the writer returns inline);
    - `intact` → skip, and read the receipt where the return would have been read;
    - `changed` → ask *Keep what is there and go on (Recommended)* / *Dispatch it again*, then `log` the answer;
    - `interrupted` → the command's named handling, or by default *Dispatch it again over what it left (Recommended)* / *Stop*.
    - The command names each writer's tree and scope, and every place it calls `tree-note`.
  - **`run-dispatch`, extended:**
    - another plugin's agent through the `agent-file` skill (D19), and the agents that stay unsaved;
    - the **pin** rule (D29): where the command names a pin, it records it with `done --pin` from the agent's return. On a reuse it checks each returned pin against the present (the pinned ref's commit now) and, where one no longer holds, calls `dispatch --redo` and dispatches.
  - **`run-gate`, extended:**
    - **interviews** (D22): ids `<prefix>-NNN`, recorded with `--keep-shown`; a resumed run reads `answers --match <prefix>-` as the interview so far and asks from the next number;
    - **two-part answers** (D30).
  - **`open-run`, extended:**
    - the placement rule and the run's own output (D24);
    - a keyless run's `others` (D26). Where `others` is not empty, the question lists each, with its args, last phase and saved-result count, as extra choices *Resume the run with <args>* (at most 3), beside this run's choices. Choosing one resumes that folder with its stored arguments, which then replace the typed ones for the rest of the run.
    - a command run inline by another (D27): it opens no folder, and uses its caller's with its own id prefix.
  - **§3, extended:** values read once (D25).
  - **§5, rewritten:** D13 and D21. `put` for the orchestrator's own content; D23's copy-and-attach; a stop may remove a `scratch/` subtree it made, since nothing reuses it.
  - **New §: units in a loop** (D31).
  - **§6** gains a line for each item above.

- [ ] **Step 1: Write the skill**, in the style of `skills/specs-git/SKILL.md`: one short section, the call, what an empty result means.
- [ ] **Step 2: Extend `run-folder.md`** as above. Each new text states what to do where the run folder is unavailable. Keep entry points executable in order, and keep the file loadable whole. If it passes 45,000 characters, stop and report: splitting it under `reference-parts/` is a separate decision.
- [ ] **Step 3: Rules.** In `.claude/rules/workflows-core-run-folder.md`, add the invariants:
  - a writer never goes through `run-dispatch`;
  - the run's own edits are noted with `tree-note`;
  - generated content is `put` and read back, never regenerated;
  - an agent's file comes from its own plugin's root, or the `agent-file` skill.

  Keep the file under 20,000 characters, counted with `wc -c`.
- [ ] **Step 4: Docs.** Add the skill to the `workflows-core` skills page; re-derive every count you touch.
- [ ] **Step 5: Gates**, then **commit**: `feat(workflows-core): the run-folder reference covers writers, other plugins' agents, interviews, pins and keyless runs`.

### Task 4: shared references — the tail and the dispatches they make

**Files:**
- Modify: `plugins/workflows-core/references/feedback-emission.md` (`emit-auto`), `followup-emission.md`, `cost-emission.md` (`emit-cost`), `session-hygiene.md` (the resume pointer), `docs-grounding.md`, `architecture-grounding.md`, `architecture-promotion.md`, `scan-refresh.md`

**Interfaces:**
- Consumes: Task 3's entry points.
- Produces:
  - **Fixed effect ids for the tail**, used by every command: `tail-emit-auto`, `tail-followups`, `tail-cost`, `tail-resume-pointer`. Each reference says: where the calling run carries `run_folder: <path>`, wrap the step in `run-effect` with that id. `done` → skip. `started` → the step's own idempotence decides where it has one (say which, per reference: `followup-emission` §5 dedupes; `emit-cost`'s chained checkpoint does not, so its `started` handling is to skip with one `NOTE:` that the cost entry may be missing, never to emit twice). Without a run folder, nothing changes.
  - **`docs-grounding`, `architecture-grounding`, `architecture-promotion`** take three optional caller values: `run_folder`, an id prefix (`<prefix>-docs-grounder`, …) and the area (`main`). Where given, each dispatch goes through `run-dispatch` (`promotion-scout`) or `run-writer` (`adr-drafter`, tree: the architecture repository), with the agent file from `agent-file` and an input built per the reference's input rule. Each reference names what its input must carry by version:
    - the docs repository's commit and the qmd index state, or the files it read by hash;
    - the architecture repository's commit;
    - an LLM-written summary passed in (`feature_summary`), which the caller has already `put` (D21).
  - **`scan-refresh.md`:** the pin rule for `code-scanner` (D29). After a dispatch, `done --pin ref=<scanned_ref> --pin commit=<git -C <repo> rev-parse <scanned_ref>>`. On reuse, compare `commit` with `git -C <repo> rev-parse <ref>` now; a difference means `dispatch --redo`. The refresh-policy question a caller asks is a recorded gate where the caller has a run folder.

- [ ] **Step 1: Edit each reference.** Read each fully first; the change is a short paragraph or step per reference, written in its own style, citing `workflows-core:run-folder` by entry point and never restating it.
- [ ] **Step 2: Check** that every consumer of each reference still reads true without a run folder. Find the consumers with the reference's own re-derive command (each names one, `grep -l …`).
- [ ] **Step 3: Gates**, then **commit**: `feat(workflows-core): the shared tail and the dispatching references keep to a calling run's folder`.

### Task 5: `dev-workflows` shared references — D13 and the code handoff

**Files:**
- Modify: `plugins/dev-workflows/references/context-management.md`, `plugins/dev-workflows/references/code-handoff.md`, and the restatements of the `mktemp` rule in `upgrade.md`, `vuln.md`, `conformance.md` (survey G §2 lists them; re-grep: `grep -n 'never inside a repo' plugins/dev-workflows/commands/*.md`)

**Interfaces:**
- Consumes: Task 3's `run-writer` and §5.
- Produces:
  - **`context-management.md`.** A handoff file goes in the run folder where the run has one (`scratch/`, or as a dispatch's input or result), and is removed with the folder by `close-run`. Where the run has no folder it is a `mktemp` file outside every repository, removed as today. A file used within one shell command under its own `trap` stays a `mktemp` file. "Never inside a repo tree" holds either way. `/implement` is named as keeping its own removal (`run-state.py`).
  - **`code-handoff.md`**, the machinery `/upgrade` and `/vuln` share:
    - `upgrade-executor`, `vuln-fixer` and `review-fixer` dispatches go through `run-writer`, tree: the code repository's root, no scope;
    - `interrupted` → revert to the unit's `pre_edit_tree`, the existing revert contract, then `tree-note`, then dispatch again;
    - every commit, revert and `finish-code-branch` step is followed by `tree-note`;
    - `test-baseliner` and `code-review` dispatches go through `run-dispatch`, inputs naming the tree id they ran on;
    - the plan, diff, claims and snapshot files move into `scratch/`.

- [ ] **Step 1: Edit both references**; then edit each restatement so it says what `context-management.md` now says, or cites it.
- [ ] **Step 2: Read `/implement`'s use** of `context-management.md` (`grep -n context-management plugins/dev-workflows/commands/implement.md`) and confirm every sentence there is still true. Change `implement.md` only if a sentence became false, and then only that sentence.
- [ ] **Step 3: Gates**, then **commit**: `feat(dev-workflows): handoff files live in the run folder, and the code handoff resumes its writers`.

### Tasks 6–11: one command each

Each of these tasks converts one command. The same steps hold for each:

**Files:** the command, `plugins/<plugin>/commands/<command>.md`; its user page, `plugins/<plugin>/docs/commands/<command>.md`; and any agent whose input contract gains `result_path` (name it in the report).

- [ ] **Step 1: Read** the command whole, its section of the survey, and `run-folder.md` §6.
- [ ] **Step 2: Write the conversion** into the command. Cover every line of §6, using Part 1's `/prd-ground` as the model of form (grep it for `run-folder`):
  1. the `open-run` step and its placement (D24), with the checks and tree-moving steps that come after it;
  2. the phases it logs and the facts it records (D25);
  3. each saved dispatch: its id, area, agent file, model, `result_path` or not, and an input built per the rule with every external read versioned (the D7 audit);
  4. each writer, with its tree, scope and `tree-note` points;
  5. each content file it `put`s;
  6. each recorded question and its gate id;
  7. each guarded effect, its id, facts and `started` handling;
  8. its taken-over stop, and every other stop's `run-stop-line`;
  9. the D28 maintenance effect `tail-maintenance`;
  10. `changed-agents`, after the last model is resolved;
  11. the `Resumed:` and `Kept …` lines;
  12. `close-run` just before the terminal `commit-artifacts`.
- [ ] **Step 3: Write the user page's *Stopping and resuming* section**, as `product-workflows/docs/commands/prd-ground.md` has it. Derive every claim from the command text.
- [ ] **Step 4: Gates**, then **commit**: `feat(<plugin>): /<command> resumes a stopped run`.

Per command, what the brief must settle (the rulings; the survey has the rest):

#### Task 6: `/dev-workflows:ready` (the pilot: the least to convert)
- Keyed. `open-run` goes after the preflight and branch-check, before the first reviewer.
- `started_at`, the run timestamp and `delivery` are facts.
- The `readiness-reviewer` brief is `put` before its dispatch and attached.
- Phase 5 step 2a's two `general-purpose` maintenance writers are not saved. Their step is an effect, `p5-maintenance`; its before/after `tree-snapshot.py` files move into `scratch/`.
- `handoff-to-main` is effect `handoff`. Its `started` handling is `phase-handoff`'s rows B/B′.

#### Task 7: `/dev-workflows:conformance`
- `conformance-tracer` goes through `run-dispatch` with `result_path` in place of `output_path`. Its contract accepts `result_path` as the file it writes; the old `output_path` stays, for a run with no folder.
- The requirement list is `put`.
- The walk's questions are recorded gates `walk-<cluster id>`. The clusters are formed in a fixed order from the `put` list, not in walk order.
- Phase 5's note appends are effects. Phase 5.5 is like `/ready`'s step 2a.

#### Task 8: `/dev-workflows:design`
- Folds the run folder's question into the `_design-session.md` question (D5). The answer applies to both.
- Ids carry the Epic key, for the *Next Epic* loop (D31). The Epic picker's answer is gate `picker`, asked before the per-Epic work.
- `code-scanner`, `overlap-reader` and `architecture-grounder` go through `run-dispatch` with `agent-file` paths. `code-scanner` is pinned (Task 4).
- The `interface-designer` frame and the scanner `context` are `put`.
- Files the run edits between reviews are copied and attached (D23).

#### Task 9: `/security-workflows:scan`
- `--workdir` is the repository root. `open-run` goes after `<repo root>` is resolved and before `run_dir` is made.
- The KEY's mode is part of `--args`.
- The Claude Security workflow run is not resumable: the spec's non-goal. Its report directory and `<scan start>` are facts, so a resumed run finds its own report rather than rejecting it.
- The triage questions are recorded gates. The plan is `put`.
- The 7.3 `_security.md` append is an effect.
- No agent of its own is saved. Its value is gates, facts and effects.
- Its plugin has no agents, so nothing goes through `changed-agents`.

#### Task 10: `/dev-workflows:upgrade` (keyless)
- `--workdir` is the repository root.
- Phase 0.5's stash and dirty-tree question, and Phase 2's branch cut, are tree-moving steps (D24). On resume their facts stand: `stash_ref`, `pre_existing_dirty`, `base`, `branch`.
- Components are units (D31): effect `comp-<slug>`, and dispatch, writer and gate ids carry the slug.
- `latest` and `lts` resolutions are facts.
- The baseline's tree id is a fact, and the baseliner input names it.
- Writers per Task 5.

#### Task 11: `/dev-workflows:vuln` (keyless)
- Like `/upgrade`, with units `cve-<id>`.
- The mixed per-token address goes into `--args` as typed.
- The `git switch` to the base before each CVE is a tree-moving step, skipped on resume where `cve-<id>` is `started` or `done`.
- `vuln-research` results are pinned to nothing. The CVE data the research read is a `put` file the input attaches, so a changed advisory redoes the research.

### Task 12: versions, CHANGELOGs, couplings

**Files:** `plugins/{workflows-core,dev-workflows,security-workflows,product-workflows}/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, each plugin's `CHANGELOG.md`, `.claude/rules/plugin-updates-coupling.md`

- [ ] **Step 1: Bump** the versions per *Global Constraints*; re-read `main` first and take the next minor or patch of what is there.
- [ ] **Step 2: Write a dated section in each CHANGELOG**, opening with **What changes for you**:
  - `workflows-core`: the mechanism, the skill, the shared references;
  - `dev-workflows` and `security-workflows`: which commands now resume, what they reuse, redo and ask, and their known limits (unsaved dispatches per D19, the Claude Security workflow run, nested dispatches);
  - `product-workflows`: only the copied script.
- [ ] **Step 3: Couplings.** `dev-workflows` 4.71.0 and `security-workflows` 0.13.0 need `workflows-core` 1.100.0 (the `agent-file` skill and the reference's new entry points). Add the bullets to the coupling rule in its own form.
- [ ] **Step 4: Gates, and every script's `--selftest`**, then **commit**: `release: workflows-core 1.100.0, dev-workflows 4.71.0, security-workflows 0.13.0 — dev and security commands resume a stopped run`.

### Task 13: verification record (after the final review's fix wave)

**Files:** Create `docs/superpowers/verification/2026-11-24-run-folder-part2a.md`, modelled on Part 1's record:
- the Review Focus lines mapped to their self-test cases and command text;
- the gates, run on the final tree, each with the command that produced it;
- the live runs owed, at least: a `/vuln` killed mid-fixer and resumed; a `/design` resumed after a `git pull` in a scanned clone; a `/ready` resumed after its reviewer finished.

Commit: `docs: verification record for run folder Part 2a`.

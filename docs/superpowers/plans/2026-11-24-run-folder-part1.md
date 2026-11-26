# Run folder, Part 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `/product-workflows:prd-ground` run interrupted mid-run — a crash, a container restart, usage limits — continues on the same machine with every finished agent's result and every answer the user gave, through a shared `workflows-core` run folder.

**Architecture:** A stdlib Python script, `run-folder.py`, owns a per-run folder under `${XDG_STATE_HOME:-$HOME/.local/state}/ai-workflows/runs/`: identity, ownership, saved dispatch inputs and results with their fingerprints, gate answers, side-effect records, facts and a progress log. A new reference, `workflows-core:run-folder`, states the protocol once. `/prd-ground` opens a run at the end of Phase 0, routes every grounder and verifier dispatch and every mid-run question through the script, re-pins a repository that moved while it was stopped, guards its non-idempotent writes, and removes the folder after its last step.

**Tech Stack:** Python 3.11 standard library; markdown command, agent, reference and rules files executed literally by agents; GitHub Actions (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-11-24-run-folder-design.md` — Part 1 is D18 item 1. Amended 2026-11-24 while planning: D2 (working directory only for commands that depend on it), D5 (the arguments typed now win on resume), D7a (the question stands where the models are known), D18 (dispatches through another shared reference wait for Part 2). Not in Part 1: D6b (a dispatch that edits files — none of `/prd-ground`'s agents does), D13's `mktemp` moves (`/prd-ground` makes no `mktemp` file; the reference states the rule for Part 2), D16 and D17.

## Global Constraints

- Location: `${XDG_STATE_HOME:-$HOME/.local/state}/ai-workflows/runs/<run-key>/`, mode `0700`. An empty `XDG_STATE_HOME` counts as unset; a relative one is ignored.
- Run key: `<plugin>.<command>-<KEY>-<h>` keyed, `<plugin>.<command>-<h>` keyless; `<h>` = the first 8 hex digits of a SHA-256 over the identity: the specs repository's `origin` URL (its physical path where it has none), the working directory's repository root only where the caller passes `--workdir`, and the canonical arguments only for a keyless run.
- Never fail a command because of its run folder: where it cannot be made or written, `open` reports `unavailable` and the command proceeds exactly as today with one `NOTE:`.
- Owner: `CLAUDE_CODE_SESSION_ID` (null where unset or empty). A writing call from a session other than the owner, both non-null, exits **9**; a null on either side passes.
- Fingerprint: SHA-256 over the input file's bytes, each attached run-folder file's bytes (sorted by path), the agent definition file's SHA-256, and the model id. A result is reused only when its recorded fingerprint equals the new one and its completion is recorded.
- D7a: at most **10** saved results whose agent file or model changed are redone without asking; more than 10 → the question *Resume and redo them* / *Resume and keep them* / *Start over*. A `/prd-ground` verifier result recorded on a non-Opus model is never kept.
- Pruning: each `open` removes run folders under `runs/` that no session has written for **30 days**, printing one `NOTE:`.
- Names: the script is `run-folder.py` (never `run-state.py`, which is `/implement`'s); the reference is `workflows-core:run-folder`. Called as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-folder.py" <subcommand> …`.
- Every bundled script has a `--selftest` run in CI; a script copied into several plugins is byte-identical to `workflows-core`'s, checked in CI (`.claude/rules/workflows-core-bounded-run.md`).
- Prose is executed: a false sentence in a command, agent, reference or rules file is a defect. Cite code by heading and quoted snippet, never by line number, in commands, references, rules and `CLAUDE.md`.
- Edits to `CLAUDE.md` and `.claude/rules/*.md` follow `plugins/workflows-core/references/instruction-file-maintenance.md`; each rules file stays under 20,000 characters; every number written there is re-derived with the command that counts it, stated beside it.
- `/implement` and its `dev-workflows/scripts/run-state.py` are not touched.
- Before each commit: `./scripts/check-id-grammar.sh --root .`, `./scripts/check-docs.sh --root .`, `python3 scripts/validate-catalog.py`, and the `--selftest` of every script the task changed. Read a file in an area with the Read tool before editing there, so its rules file loads (`CLAUDE.md`, *Where the rest of the guidance lives*).
- Every `— Unreleased` CHANGELOG section is dated before it reaches `main`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Review Focus

1. **Two projects of one container group with the same KEY** (each mounts its own specs repository at `/workspace/specs`, both share `~/.local/state`) must get two run folders. Pinned in Task 1's selftest (`identity-specs-origin`).
2. **A session killed after an agent wrote its result file but before `done` recorded it** must re-dispatch that agent, never read a half-written result. Pinned in Task 2 (`result-unrecorded-not-reused`).
3. **An older session still running after another resumed** must stop at its next write without writing anything to the specs repository. Pinned in Task 1 (`owner-guard`) and Task 5 (the `PRD_GROUND_RUN_TAKEN_OVER` stop, no tail).
4. **A repository pulled between two sessions** must redo only that repository's grounding and verification. Pinned in Task 2 (`fingerprint-changes-with-input`) and Task 5's re-pin step.
5. **A derive verifier finding the grounders' answers in the run folder** must be prevented by layout and by its prompt. Pinned in Task 2 (`area-blind-separate`) and Task 4.
6. **A run stopped inside Phase 8's writes** must not append its findings twice. Pinned in Task 6's write-ahead copy and Task 2 (`effect-states`).

---

### Task 1: `run-folder.py` — the folder, its identity and its owner

**Files:**
- Create: `plugins/workflows-core/scripts/run-folder.py`

**Interfaces:**
- Produces — every subcommand prints one JSON object on stdout; exit `0` ok, `2` usage or could not run, `9` taken over (message on stderr names the owner):
  - `open --command <plugin>.<command> [--key <KEY>] --specs <dir> [--workdir <dir>] --args <string>` → `{"state": "new"|"unfinished"|"unavailable", "folder", "run_key", "reason", "pruned": {"count", "bytes"}, "summary": {"started", "updated", "owner", "other_session", "args", "last_phase", "results", "facts"}}`. Creates the folder on `new`; never takes ownership of an unfinished run; `unavailable` exits 0.
  - `resume <folder>` → `{"owner"}`; takes ownership, logs it.
  - `discard <folder>` and `close <folder>` → `{"removed": true}`; each refuses (exit 2) a path that is not a direct child of the runs root holding a `run.json`.
  - `phase <folder> <name>` → `{"last_phase"}`; `log <folder> <text>` → `{}`; `fact <folder> <name> [--set <value>]` → `{"name", "value"}` (`null` when unset).
- Internal, used by Task 2: `runs_root() -> Path`, `load_run(folder) -> dict`, `check_owner(run) -> None` (raises the exit-9 error), `write_json_atomic(path, obj)`.

- [ ] **Step 1: Write the self-test cases** in `selftest()` (the shape of `plugins/workflows-core/scripts/tree-snapshot.py`'s: temporary directories, `HOME`/`XDG_STATE_HOME`/`CLAUDE_CODE_SESSION_ID` set per case in the child's environment, the script run as a subprocess, one `PASS`/`FAIL` line per case, exit 1 on any failure):

| Case | Setup | Expect |
|---|---|---|
| `root-default` | `XDG_STATE_HOME` unset | folder under `$HOME/.local/state/ai-workflows/runs/` |
| `root-empty-and-relative` | `XDG_STATE_HOME=""`, then `XDG_STATE_HOME=rel/dir` | both fall back to `$HOME/.local/state/…` |
| `open-new-0700` | first `open` | `state == "new"`, folder mode `0o700`, `run.json` holds command, key, identity, args, run id, started, owner |
| `run-key-shape` | `--command product-workflows.prd-ground --key MWC-001-01` | `run_key` matches `^product-workflows\.prd-ground-MWC-001-01-[0-9a-f]{8}$`; without `--key`: `^…prd-ground-[0-9a-f]{8}$` |
| `identity-specs-origin` | two specs repos, same KEY, different `origin` URLs | two different folders |
| `identity-specs-path` | a specs repo with no `origin`, opened via two spellings of its path (a symlink) | one folder |
| `identity-workdir-optional` | same specs and KEY, `open` from two working directories without `--workdir` | one folder; with `--workdir` of two repositories: two |
| `keyless-args` | no `--key`, two different `--args` | two folders; same `--args`: one |
| `open-unfinished` | `open`, `phase … p5`, `open` again | `state == "unfinished"`, `summary.last_phase == "p5"`, owner unchanged |
| `other-session` | `open` as session A, `open` as session B | `summary.other_session == true` |
| `owner-guard` | `open` as A, `resume` as B, then `log` as A | the `log` exits 9 and writes nothing; `log` as B succeeds |
| `owner-null-passes` | owner A, caller with no `CLAUDE_CODE_SESSION_ID` | `log` exits 0 |
| `unavailable` | `HOME` and `XDG_STATE_HOME` under a read-only directory | `state == "unavailable"`, exit 0, `reason` non-empty |
| `prune-30-days` | two run folders whose `run.json` `updated` is 31 and 29 days old | `open` of a third removes the first only; `pruned.count == 1` |
| `close-refuses-outside` | `close /tmp/x`, `close <runs root>` | exit 2, nothing removed |
| `discard-then-new` | `open`, `discard`, `open` | second `open` is `new` with a new run id |
| `fact-roundtrip` | `fact … pin:backend --set abc`, then `fact … pin:backend` | `value == "abc"`; unset name → `null` |

- [ ] **Step 2: Run it and see every case fail** — `python3 plugins/workflows-core/scripts/run-folder.py --selftest` → `FAIL` lines (the subcommands do not exist yet), exit 1.

- [ ] **Step 3: Implement the subcommands above.** Identity: `git -C <specs> config --get remote.origin.url` with a 5 s timeout, else `os.path.realpath`; `--workdir`: `git -C <dir> rev-parse --show-toplevel` (5 s), else its real path. `updated` is written by every writing call; pruning reads it (falling back to the folder's mtime where `run.json` does not parse). Progress lines are `<UTC ISO time> <session or -> <text>` appended to `progress.md`. All JSON writes go through `write_json_atomic` (temp file in the same directory, `os.replace`).

- [ ] **Step 4: Run the self-test** — same command → every case `PASS`, exit 0.

- [ ] **Step 5: Commit** — `git add plugins/workflows-core/scripts/run-folder.py && git commit -m "feat(workflows-core): run-folder.py — a run's folder, identity and owner"`

### Task 2: `run-folder.py` — dispatches, gates, side effects, changed agents

**Files:**
- Modify: `plugins/workflows-core/scripts/run-folder.py`

**Interfaces:**
- Consumes: Task 1's `load_run`, `check_owner`, `write_json_atomic`.
- Produces (same output and exit conventions; every writing subcommand checks the owner):
  - `dispatch <folder> <dispatch-id> --area main|blind --agent <name> --agent-file <path> --model <id> --input <file|-> [--attach <relative path>]…` → `{"action": "reuse"|"dispatch", "input", "result", "fingerprint"}`. Writes `<area>/inputs/<id>.md`, records `{fingerprint, agent, agent_sha, model, area}`; `result` is `<area>/results/<id>.md`.
  - `done <folder> <dispatch-id> [--from <file|->]` → `{"recorded": true}`; with `--from` it writes the result file first; exit **3** where the result file is missing or empty.
  - `gate <folder> <gate-id> --shown <file|->` → `{"answer": <text>|null}`; `gate-record <folder> <gate-id> --shown <file|-> --answer <text>` → `{}`.
  - `effect <folder> <effect-id> start|done|state` → `{"state": "none"|"started"|"done"}`.
  - `stale <folder> --agent <name>=<file>… --model <name>=<id>…` → `{"total", "changed": [{"id", "agent", "agent_changed", "old_model", "new_model"}]}` over recorded results.
  - `keep <folder> --ids <id>… --agent … --model …` → `{"kept": [ids]}`: re-records those results' fingerprints under the current agent file and model, and lists them in `run.json` `kept`; `kept <folder>` → `{"kept": [ids]}`.
  - `results <folder> [--match <substring>]` → `{"count", "ids"}`: recorded results only, those whose id contains the substring where one is given.
- Dispatch ids match `^[a-z0-9][a-z0-9._-]*$` (exit 2 otherwise), so an id never names a path outside its area.

- [ ] **Step 1: Write the self-test cases:**

| Case | Expect |
|---|---|
| `dispatch-new` | first `dispatch` → `action == "dispatch"`; input file holds the given bytes |
| `reuse-after-done` | `dispatch`, write the result file, `done`, same `dispatch` again → `action == "reuse"`, same `result` path |
| `result-unrecorded-not-reused` | `dispatch`, write the result file, no `done`, `dispatch` again → `"dispatch"` |
| `done-missing-result` | `done` with no result file, and with an empty one → exit 3 |
| `done-from-stdin` | `done … --from -` with text on stdin → result file holds it; a later `dispatch` reuses |
| `fingerprint-changes-with-input` | `done`, then `dispatch` with one byte changed → `"dispatch"` |
| `fingerprint-attach` | `--attach scratch/diff.txt`, `done`, change `diff.txt`, `dispatch` → `"dispatch"` |
| `fingerprint-agent-and-model` | `done`, then same input with a changed agent file → `"dispatch"`; same with another `--model` → `"dispatch"` |
| `area-blind-separate` | `--area blind` → input and result under `blind/`, nothing under `main/` |
| `bad-id` | ids `../x`, `a/b`, `""` → exit 2 |
| `gate-roundtrip` | `gate` → `null`; `gate-record`; `gate` same `--shown` → the answer; changed `--shown` → `null` |
| `effect-states` | `state` → `none`; `start` → `started`; `done` → `done` |
| `stale-counts` | three results by agent `v`, one by `g`; change `v`'s file → `total == 3`, `agent_changed` true; change the model of `g` → that one listed with `old_model`/`new_model` |
| `results-match` | three recorded results, one unrecorded; `results` → count 3; `--match cg-backend` → only those ids |
| `keep-then-reuse` | after `stale`, `keep --ids` one of them → a `dispatch` of that id with the new agent file reuses; `kept` lists it |
| `owner-guard-writes` | `dispatch`, `done`, `gate-record`, `effect`, `keep` from a superseded session → exit 9, nothing written |

- [ ] **Step 2: Run** — `python3 plugins/workflows-core/scripts/run-folder.py --selftest` → the new cases `FAIL`, Task 1's still `PASS`.
- [ ] **Step 3: Implement the subcommands.** Fingerprint per *Global Constraints*; records in `run.json` under `dispatches`, `gates`, `effects`; each made, reused or recorded dispatch, gate and effect transition is also a progress line.
- [ ] **Step 4: Run** — every case `PASS`, exit 0.
- [ ] **Step 5: Commit** — `feat(workflows-core): run-folder.py — saved dispatches, gate answers and side effects`.

### Task 3: the reference, the copy, CI, rules and docs

**Files:**
- Create: `plugins/workflows-core/references/run-folder.md`, `.claude/rules/workflows-core-run-folder.md`
- Create (copy): `plugins/product-workflows/scripts/run-folder.py`
- Modify: `.github/workflows/validate-catalog.yml`, `.claude/rules/workflows-core-bounded-run.md`, `.claude/rules/workflows-core.md`, `CLAUDE.md`, `plugins/workflows-core/docs/reference/references.md`, `plugins/workflows-core/docs/reference/environment.md`

**Interfaces:**
- Consumes: Tasks 1–2's subcommands.
- Produces: the reference's entry points, cited by Tasks 5–6 as `Skill(skill: "workflows-core:reference", args: "run-folder <entry>")`: `open-run` (call `open`, ask *Resume* / *Start over* on `unfinished`, `resume` or `discard`+`open`, print the `unavailable` `NOTE:`), `run-dispatch` (D6 steps 1–4 around one Agent call), `run-gate` (D8 around one question), `run-effect` (D6a), `changed-agents` (D7a: `stale`, the threshold, the question, `keep`), `run-stop-line`, `close-run`. Each entry point also states what to do where the run folder is unavailable: skip it and act as before.

- [ ] **Step 1: Write `run-folder.md`** — the protocol of spec D1–D13 and D7a for a calling command, as executed steps per entry point; the exact `open-run` question text and the stop line `Run folder kept: <folder> — run <command> again to resume.`; exit 9 means "stop, write nothing more"; what a command must name for itself (its dispatch-id scheme, which dispatches use `--area blind`, its effects). Keep it loadable whole (well under the size at which `reference-parts/` splits a reference).
- [ ] **Step 2: Copy the script** — `cp plugins/workflows-core/scripts/run-folder.py plugins/product-workflows/scripts/run-folder.py`.
- [ ] **Step 3: CI** — in `validate-catalog.yml` add a step `Self-test the run folder` running `python3 plugins/workflows-core/scripts/run-folder.py --selftest`, with a comment in the style of its neighbours naming its silent failure modes (a stale result reused; a superseded session still writing); add `run-folder.py` to the `for name in bounded.py tree-snapshot.py` loop of *Every plugin's copied scripts are the same*.
- [ ] **Step 4: Rules and `CLAUDE.md`** — new `.claude/rules/workflows-core-run-folder.md` (`paths:` `plugins/*/scripts/run-folder.py`, `plugins/*/commands/*.md`, `plugins/*/agents/*.md`, `plugins/*/references/**`): the authority sentence (the reference is the single source of truth; the script is called by path; `/implement`'s `run-state.py` is a different mechanism), and the invariants: never fail a run because of its folder, exit 9 stops with no write, a reused result needs a matching fingerprint and a recorded completion. In `workflows-core-bounded-run.md` add `run-folder.py` to the copied-scripts rule and its `paths:`. In `workflows-core.md` re-derive *forty-two reference files* (`find plugins/workflows-core/references -type f | wc -l`) and add the new file to the *Split out* sentence. Add the row to `CLAUDE.md`'s rules table.
- [ ] **Step 5: Docs** — `references.md`: re-derive its count and add a `run-folder.md` entry in the right group; `environment.md`: add `$XDG_STATE_HOME` (default, unset, empty, relative; where runs keep their state) and re-derive *The ten* and every sentence that counts the variables.
- [ ] **Step 6: Run the gates** (*Global Constraints*) — all pass, and `cmp plugins/workflows-core/scripts/run-folder.py plugins/product-workflows/scripts/run-folder.py` is silent.
- [ ] **Step 7: Commit** — `feat(workflows-core): the run-folder reference, its copy in product-workflows and its CI checks`.

### Task 4: grounders and verifier write their own results

**Files:**
- Modify: `plugins/product-workflows/agents/code-grounder.md`, `plugins/product-workflows/agents/grounding-verifier.md`, and any page under `plugins/product-workflows/docs/` that states either agent's inputs or return (find with `grep -rln 'code-grounder\|grounding-verifier' plugins/product-workflows/docs`).

**Interfaces:**
- Produces: both agents accept an optional input `result_path: <absolute path>`. Where it is given, the agent writes its **complete** return — exactly the YAML it returns today — to that file with its `Bash` tool (no `Write` is added to either agent), and returns only a receipt: `status`, the count of findings or per-finding entries, and `result_path`. Where it is absent, it returns as today. `design-grounder` (no `Bash`) is unchanged: Task 6 saves its return with `done --from -`.
- `grounding-verifier`, derive mode: it reads nothing under the folder holding its `result_path` except that file, and nothing under the run folder's other areas; this joins the blind-verification statements in its body.

- [ ] **Step 1: Edit both agents' input sections and output contracts** as above, including the read-failure and write-failure behaviour: a `result_path` that cannot be written returns `status: INPUT_MISSING` naming the path (`dev-workflows/references/context-management.md`'s *read-failure contract* is the model), never a partial file.
- [ ] **Step 2: Docs** — update every page the grep finds.
- [ ] **Step 3: Gates** — `check-docs.sh` passes.
- [ ] **Step 4: Commit** — `feat(product-workflows): code-grounder and grounding-verifier write their result to a given path`.

### Task 5: `/prd-ground` — open, resume, gates, pins, stops, close

**Files:**
- Modify: `plugins/product-workflows/commands/prd-ground.md`

**Interfaces:**
- Consumes: Task 3's entry points; Task 4's `result_path`.
- Produces for Task 6: the run folder path carried as `run_folder` (or `run_folder: unavailable`); facts `pin:<slug>` (Phase 3), `phase8` and `phase9` outcome facts (Task 6).

- [ ] **Step 1: Open, as Phase 0's last step** (a new step after step 9, once every Phase 0 refusal has had its chance and the KEY, folder and flags are known): `open-run` with `--command product-workflows.prd-ground --key <KEY> --specs "$SPECS_PATH" --args "<the arguments after the KEY, as typed>"` and no `--workdir`. On `unfinished`, before asking: read each `pin:<slug>` fact and compare it with that clone's `git -C <path> rev-parse HEAD`; the question names the repositories that moved and how many saved results each holds (`results --match cg-<slug>`; dispatch ids name the slug, Task 6). Where the typed arguments differ from `summary.args`, the question shows both (spec D5 as amended). `phase` is logged at the start of every later phase.
- [ ] **Step 2: Gates** — route through `run-gate` the questions of Phase 1 steps 1, 3 and 4 (gate ids `p1-repos`, `p1-clone-<slug>`, `p1-manual`), Phase 3's rename question (`p3-rename-<slug>`), Phase 4.5's *Add repositories for leads* (`p45-leads`) and Phase 9's handoff consent (`p9-handoff`). `--shown` is the question with its options as printed. Phase 0's `$SPECS_PATH`/`$REPOS_PATH` questions come before the folder opens and Phase 10's arrays end the run, so neither is recorded.
- [ ] **Step 3: Changed agents, at the end of Phase 2** — `changed-agents` with `--agent code-grounder=${CLAUDE_PLUGIN_ROOT}/agents/code-grounder.md`, the same for `design-grounder` and `grounding-verifier`, and `--model` of each from `model_routing`. Ids of `grounding-verifier` results whose `old_model` is not an Opus model are left out of *keep*.
- [ ] **Step 4: Pins** — Phase 3 records each pin as fact `pin:<slug>` once taken. A pin this run logged that differs from today's `HEAD`, where no pin **on file** governs that repository, is replaced by today's `HEAD` with one line in the run's report (`<repo> moved since this run pinned it (<old> → <new>); its grounding is redone`). The rule for a pin on file (`PRD_GROUND_NEEDS_REBASELINE`, "harmless re-run") is unchanged and still decides first.
- [ ] **Step 5: Stops** — in *Ending early*: every stop taken after the run folder opened prints `run-stop-line` after its own message and logs `stop <CODE>`. Add `PRD_GROUND_RUN_TAKEN_OVER: another session (<id>) took this run over — stopping without writing.`, taken wherever a script call exits 9, with no tail at all (as `PRD_GROUND_TYPED_ONLY`), and name it in the stop lists *Ending early* and Phase 11 keep.
- [ ] **Step 6: Close** — `close-run` after the *Final report* is printed, the run's last action; never on a stop.
- [ ] **Step 7: Gates** — `check-docs.sh` and the others pass.
- [ ] **Step 8: Commit** — `feat(product-workflows): /prd-ground opens, resumes and closes a run folder`.

### Task 6: `/prd-ground` — dispatches from and to files, guarded writes

**Files:**
- Modify: `plugins/product-workflows/commands/prd-ground.md`

**Interfaces:**
- Consumes: Task 5's `run_folder`; Task 3's `run-dispatch` and `run-effect`; Task 4's `result_path`.
- Dispatch ids (a function of the deterministic composition only, never of timing or position in a reply): `p5-cg-<slug>`, `p45-cg-<slug>-<CG id>` (the Phase 4.5 one-claim re-dispatch), `p5-dg-<frame set dir name>`, and in Phase 7 `p7-<unit>-<derive|compare>-<group>-<n>` where `<unit>` is `first`, `sweep`, `retry`, or `second<k>`, `<group>` is `cg-<slug>` or `dg-<frame set>`, and `<n>` is the batch's index in the phase's own ordering. Derive dispatches use `--area blind`; every other dispatch `--area main`.

- [ ] **Step 1: Phase 5** — each `code-grounder` and `design-grounder` dispatch goes through `run-dispatch`: the input file is the prompt block as written today; `code-grounder` gets `result_path`; `design-grounder`'s inline return is saved with `done --from -`. A reused result is read from its file exactly where the inline return was read before, so renumbering, the frame-set association (from the dispatch id) and the evidence test run unchanged over it, in the same order.
- [ ] **Step 2: Phase 4.5's re-dispatch** and **Phase 7** (derive, compare, retry, second opinion, sweep) the same way; `grounding-verifier` gets `result_path` in both modes. Matching stays by `finding_id`. The batch composition rules are untouched; only where a return is read from changes.
- [ ] **Step 3: Phase 8, guarded** — before its first write, `run-effect` `p8-write start` after copying each file Phase 8 will write (or recording that it is absent) into `scratch/p8-before/`; after the lineage stamp, record Phase 8's outputs that Phases 9–11 read (`body_facts`, `deliverable_paths`, the rewrite and cascade lists, the ledger counts) as fact `phase8` (JSON), then `p8-write done`. On replay: `done` → skip Phase 8 and read `phase8`; `started` → a question: *Restore the files to how they were before and write again* / *Stop* (the stop keeps the run folder), never a second append.
- [ ] **Step 4: Phase 9 and Phase 11** — Phase 9's `handoff-to-main` inside effect `p9-handoff`, its `Phase handoff:` line kept as fact `phase9`; a `started` replay re-runs `handoff-to-main`, whose branch reuse (`phase-handoff` §2.2 rule 3) is the re-run handling. Phase 11's steps 1–5 each inside an effect `p11-<n>`; a `done` one is skipped on replay.
- [ ] **Step 5: Gates** — `check-docs.sh` and the others pass.
- [ ] **Step 6: Commit** — `feat(product-workflows): /prd-ground saves every grounder and verifier result and guards its writes`.

### Task 7: rules, user docs, versions

**Files:**
- Modify: `.claude/rules/prd-ground-verification.md`, `plugins/product-workflows/docs/commands/prd-ground.md`, `plugins/workflows-core/CHANGELOG.md`, `plugins/product-workflows/CHANGELOG.md`, `plugins/workflows-core/.claude-plugin/plugin.json`, `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and any `plugin-updates` coupling file `.claude/rules/plugin-updates.md` says a release pairing needs.

- [ ] **Step 1: Blind verification rule** — amend *no outcome carried forward from an earlier run* per spec D14: a resumed run continues the same run and reuses its own derive and compare results; *Start over* deletes the folder, so an earlier run's are never reused; derive dispatches live in the `blind` area.
- [ ] **Step 2: User page** — a section *Stopping and resuming* in `docs/commands/prd-ground.md`: where the run folder lives, what a resume reuses and redoes (moved repositories, changed agents and the 10-result question, typed arguments), the new stop `PRD_GROUND_RUN_TAKEN_OVER` in *Gates*, and that a run that finishes leaves nothing behind. Every claim derived from the command text Tasks 5–6 wrote.
- [ ] **Step 3: Versions** — `workflows-core` 1.98.1 → **1.99.0**, `product-workflows` 3.86.0 → **3.87.0** (re-read both before bumping: `main` moves fast; take the next minor of whatever is there), in `plugin.json` and `marketplace.json`; a dated section in each CHANGELOG opening with **What changes for you**, as the recent sections do.
- [ ] **Step 4: All gates and every touched script's `--selftest`** pass.
- [ ] **Step 5: Commit** — `release: workflows-core 1.99.0, product-workflows 3.87.0 — a stopped /prd-ground resumes`.

### Task 8: verification record (after the final review's fix wave)

- [ ] Write `docs/superpowers/verification/2026-11-24-run-folder-part1.md` last, per `CLAUDE.md` (*A sub-project's verification record is written last*): each Review Focus line with the self-test case or command text that covers it, the gate outputs on the final tree, and what only a live run can show (a real interrupted `/prd-ground` resumed in a new session) listed as owed, not claimed.

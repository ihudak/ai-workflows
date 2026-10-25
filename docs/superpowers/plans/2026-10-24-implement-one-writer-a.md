# One writer per Epic, part (a): `/implement` — Implementation Plan

> **Status on 2026-10-25: executed, not merged.** Tasks 0–14 were built on `iv-gu/implement-one-writer` (`ef81409a`) and Task 15's live A/B was run; the result led the user to replace part (a) with `docs/superpowers/specs/2026-10-25-implement-piece-review-design.md`. Do not execute this plan again.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/dev-workflows:implement` codes each writer unit through one `code-writer` and one `test-writer`, reached again with `SendMessage` for every fix. It runs each unit's tests before the review, reviews per piece plus overall, and serialises every build and test run through a lock.

**Architecture:**
- **What the work is.** It is prose in markdown command, agent and reference files, which agents execute literally, plus one new Python script.
- **What gets rebuilt.** `implement.md`'s Phases 3A, 3B and 3.5 are rebuilt as three phases that are the same at every class:
  - Phase 3, *Code and tests*;
  - Phase 3.5, *Test run*;
  - Phase 3.6, *Review*, from MODERATE up.
- **The writers.** `code-writer` codes a whole writer unit and runs its build and nearby tests. `test-writer` writes from the spec and the design's interfaces, and compiles and runs its own tests. Each fixes its own files.
- **The reviewers.** `code-review` runs once per piece and once overall.
- **Tests first.** A scratch `check.py`, written first (Task 1), pins every decision as an assertion.
- **Verification.** The gate chain, a rule-by-rule reading, and A/B live runs on the `ihudak-e2e` copies.

**Tech Stack:** Markdown prose (commands, agents, references, docs), Python 3 standard library (`run-lock.py`, `run-state.py`, the scratch check), and the bash and node gates.

**Spec:** `docs/superpowers/specs/2026-10-24-implement-one-writer-design.md` (§3.1 and §3.4 for this part; §5 lists every rule this part reverses). It is the authority; this plan argues from it.

## Global Constraints

- **Scope:** part (a) only.
  - `/design` writing pieces is part (b); `/epics` is part (c).
  - Part (a) defines the pieces format and reads it.
  - Until part (b), `/implement` gates `specification.md` and `design.md` only where present, as today.
- **Agents keep their names:** `dev-workflows:code-writer` and `dev-workflows:test-writer`.
  - **`test-writer`'s tools** become `["Read", "Glob", "Grep", "Write", "Edit", "Bash"]`.
  - **`code-writer`'s tools** are unchanged.
  - Neither gets a `model:` pin: the caller assigns `implementation_model`.
- **`review-fixer`** is no longer dispatched by `/implement`. It stays for `/vuln` and `/upgrade`, unchanged in behaviour.
- **New files:**
  - `plugins/dev-workflows/scripts/run-lock.py`;
  - `plugins/dev-workflows/references/handoff/test-writer.md`;
  - `plugins/dev-workflows/references/review-fix.md`. This holds `review-fixer`'s *Fix method* and *Fix Report*, moved, which `review-fixer`, `code-writer` and `test-writer` all follow.
- **The lock:**
  - **Every build or test command** the two writers, `test-baseliner` and the orchestrator run in a code repository is run as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/run-lock.py" -- <command> [args…]`, from inside that repository.
  - **The lock file** is `$(git rev-parse --git-path dev-workflows/run.lock)`.
  - **The mechanism** is `fcntl.flock`, which the kernel releases when its holder dies, so no lock goes stale.
  - **Its exits:** the command's own exit code; `2` usage; `4` the lock file could not be reached.
  - **Without `fcntl`** it runs the command unlocked and says so on stderr.
- **The pieces section** in `design.md`, fixed here because part (b) writes what this part reads:
  ```
  ## Pieces
  Writers: one
  ### <piece-name>
  - Files: `<path or glob>`, …
  - Builds after: <piece-name>, … | none
  - Contract: <the `## Interfaces / contracts` items it provides or uses> | none
  ```
  - `Writers:` reads `one`, or `per piece — <why one writer could not hold the Epic well>`.
  - Piece names are kebab-case and unique, and no path matches two pieces.
  - No section means one piece, named `all`, and one writer unit.
- **The writer modes:**
  - `code-writer`: `write` (was `step`), `fix` and `review`;
  - `test-writer`: `write`, `fix` and `review`.

  Each writer's request block is sent first by `Agent`, then by `SendMessage` to the same agent, with the same block.
- **Statuses:**
  - **`code-writer`:** `done`, `needs_decision`, `trigger` (on `write` at SIMPLE or MODERATE only) and `blocked`.
  - **`test-writer`:** `done`, `needs_decision` and `blocked`. Its `Framework: not detected` report is kept.
  - **An unreadable evidence input** is `### Blocked` reading `Unreadable: <field> at <path>`, for both writers.
- **The fallback.** Where `SendMessage` fails, or the resumed reply carries no status line, dispatch a fresh agent of the same type with the same request. Its `earlier_reports` lists every report of that writer, and its `diff_so_far` is the diff now. Record it in that writer's run-state `fresh` count.
- **The fix cap:** at most **3 fix rounds per test run**, whichever failures they address. Then this exact question:

  `choices: ["Investigate further", "Accept the remaining failures and proceed (you'll be prompted for the reason; documented in the Phase 5 report)", "Cancel"]`

  That is today's array, unchanged.
- **Models:**
  - `code-writer` and `test-writer` are dispatched on §4's `implementation_model`: `current_model` at SIMPLE; from MODERATE up, `current_model` where it is an Opus or Fable model, else the §2 Opus chain's first row; `--enforce-model` over both.
  - `code-review` is unchanged.
  - `fixes_model` = `implementation_model` for `/implement`.
- **Reviewers see no test result.** No `code-review` brief carries a test, build or lint outcome, or a writer's `### Checks run`.
- **Versions:** `dev-workflows` 4.32.0 and `workflows-core` 1.46.0, each with a `— Unreleased` CHANGELOG section until Task 15 dates it.
- **Repository rules** (`CLAUDE.md`):
  - `choices:` arrays hold 2–4 options, are verbatim, and no label promises text (check 12);
  - every asking command has its **Load the question rules.** step (`check-questions`);
  - vendor neutrality (check 13);
  - never name the internal organisation (check 14);
  - every agent carries the untrusted-content block byte for byte (check 20);
  - every count in `CLAUDE.md` and `.claude/rules/` is re-derived with its command;
  - generated `reference-parts/` files are regenerated, never edited (`python3 scripts/reference-parts.py generate`);
  - "prose is executed".
- **Branch and worktree:**
  - branch `iv-gu/implement-one-writer`, from local `main` at `086c2d51` or later;
  - worktree `/workspace/.worktrees/implement-one-writer`;
  - never `git checkout` in `/workspace/ai-workflows`;
  - stage `.claude/` files with `git add -f`;
  - verify the branch before every commit;
  - run with `PYTHONDONTWRITEBYTECODE=1`.
- **The gate chain:** `/tmp/claude-502/-workspace-ai-workflows/cd29950a-1264-43c4-b92f-09b8cd6d0ed1/scratchpad/gates.sh <worktree>`. It runs `.github/workflows/validate-catalog.yml`'s `run:` steps as one `&&` chain, with `ASSERT_PUBLISHED=1`; read its `EXIT=` line. Task 1 re-derives it from the workflow file, to cover the new `run-lock.py` step.

## Review Focus

1. **A resume that fails.** `SendMessage` is unavailable, the agent is gone after a compaction, or the reply has no status line. The run must fall back to a fresh dispatch carrying the writer's reports and the diff, and never stall or recode from scratch. *Pinned:* Task 0 proves resume in a command run and across a compaction; Task 1's `flow` section asserts the fallback sentence; Task 14 counts resumes and fresh dispatches.
2. **Two builds at once.** A writer or `test-baseliner` builds while another command runs in the same tree. The second must wait. *Pinned:* Task 2's selftest runs two holders concurrently and asserts that their run windows never overlap.
3. **A code writer that edits a test file, or a writer that edits outside its unit.** Either must come back as a decision, never as a silent edit. *Pinned:* Task 1's `writers` section asserts both rules in each agent body and handoff; Task 14 reads each writer's `### Files changed`.
4. **Tests that do not compile against the code.** This happens when `test-writer` writes from interfaces before the code exists, or from signatures only. The test writer fixes its own errors before the unit's test run, and the loop ends. *Pinned:* Task 1's `writers` section asserts the compile-and-run step; Task 14's run B, which has no spec, exercises it.
5. **A fix loop that does not converge.** Each round fixes A and breaks B. The run must stop after 3 rounds per test run and ask. *Pinned:* Task 1's `flow` section asserts the cap sentence and the array.

---

### Task 0: Prove `SendMessage` in a command run (controller, with the user for step 4)

Run by the controller, not a subagent. It creates scratch files only.

**Files:**
- Create: `<scratchpad>/spike-resume/.claude-plugin/plugin.json`, `<scratchpad>/spike-resume/commands/start.md`, `<scratchpad>/spike-resume/commands/resume.md`, `<scratchpad>/spike-resume/secret.txt`. `<scratchpad>` is this session's scratchpad directory.

**Interfaces:**
- Produces a verdict, written in the SDD ledger and used by Tasks 6 and 9:
  - `resume-in-command: works | fails`;
  - `resume-after-compact: works | fails`;
  - `resume-cost`: the resumed call's `cache_read_input_tokens` and `cache_creation_input_tokens`, each measured with a warm cache and with one more than 5 minutes cold.

- [ ] **Step 1: Write the scratch plugin.**
  - `start.md`: `allowed-tools: Task SendMessage Read Write`. It dispatches a `general-purpose` agent to read `secret.txt` (a random number) and reply `ready`. It writes the agent's id to `<scratchpad>/spike-resume/agent-id`. Then it sends that agent, by `SendMessage`, "What was the number? Reply with the number only", and prints `PASS` where the reply equals the file's number, else `FAIL`.
  - `resume.md`: does only the `SendMessage` half, reading the id from `agent-id`.
- [ ] **Step 2: Run it headless:** `claude -p "/spike-resume:start" --plugin-dir <scratchpad>/spike-resume`. Expected: `PASS`. Where `-p` refuses `SendMessage`, record that, and run step 3 interactively.
- [ ] **Step 3: Measure the cost** from the session transcript's resumed call: warm, at once; cold, by running `/spike-resume:resume` 6 minutes later.
- [ ] **Step 4: With the user,** in an interactive session: run `/spike-resume:start`, then `/compact`, then `/spike-resume:resume`. Expected: `PASS`.
- [ ] **Step 5: Record the three verdicts.** Where either `resume-*` verdict is `fails`, the fallback becomes the primary path. Tasks 6 and 9 still write `SendMessage` first, and the ledger says the live runs will show the fallback. Ask the user whether to go on before Task 1.

### Task 1: The scratch check (controller)

**Files:**
- Create: `<scratchpad>/one-writer/check.py`.
- Refresh: `<scratchpad>/gates.sh`, from `.github/workflows/validate-catalog.yml`'s `run:` steps.

**Interfaces:**
- Produces `python3 check.py <worktree> <section|all>`. The sections are `lock`, `pieces`, `review-fix`, `writers`, `state`, `flow`, `review`, `routing` and `tiers`. Each assertion prints `ok <name>` or `FAIL <name>: <why>`, and the run ends `all: N passed, M failed`.

- [ ] **Step 1: Write `check.py`.** It pins only what this plan fixes.
  - **`lock`:**
    - `plugins/dev-workflows/scripts/run-lock.py` exists, and `--selftest` passes;
    - `validate-catalog.yml` runs that selftest;
    - the lock invocation string from Global Constraints appears in `code-writer.md`, `test-writer.md`, `test-baseliner.md` and `implement.md`.
  - **`pieces`:** `design-format.md` has a `## Pieces` section holding the lines `Writers: one`, `- Files:`, `- Builds after:` and `- Contract:`, and the sentence that no section means one piece named `all`.
  - **`review-fix`:**
    - `references/review-fix.md` exists and holds `## Fix Report` and `### Stop condition flag`;
    - `review-fixer.md` reads it, and no longer holds the `### Applied` template itself;
    - `code-writer.md` and `test-writer.md` each cite `review-fix.md` for `mode: review`.
  - **`writers`:**
    - `code-writer.md` and its handoff hold `mode: write`, `mode: fix` and `mode: review`, and no `mode: step`;
    - `code-writer.md` holds "never edits a test file" and `### Tests broken by intent`;
    - its *What you may never do* no longer forbids a build or test in `repo_root`;
    - `test-writer.md`'s tools are as in Global Constraints;
    - `test-writer.md` holds `## Test Writer Request`, "reads code only for signatures", the three modes, `### Tests updated` and `### Runs`;
    - `handoff/test-writer.md` exists;
    - neither agent says "Does NOT run tests" or "based on a diff".
  - **`state`:**
    - `run-state.py` `KEYS` holds `pieces`, `writer_units`, `writers`, `test_runs` and `reviews`, and no `step_groups`;
    - `--selftest` passes;
    - `implement.md` quotes the new `KEYS_LINE`.
  - **`flow`:**
    - `implement.md` has `## Phase 3 — Code and tests`, `## Phase 3.5 — Test run` and `## Phase 3.6 — Review`, and no `## Phase 3A` or `## Phase 3B`;
    - its frontmatter `allowed-tools` holds `SendMessage`;
    - it holds the fallback sentence's anchor, `dispatch a fresh agent of the same type with the same request`;
    - it holds `3 fix rounds` and the fix-cap array verbatim;
    - no `five files` or `ten steps` grouping rule remains;
    - every `→ Agent (` line carries `model:`.
  - **`review`:**
    - Phase 3.6 dispatches `code-review` with a `Scope:` line, for `piece` and for `overall`;
    - no `review-fixer` dispatch remains in `implement.md`;
    - `code-review.md` documents the `Scope:` and `Piece reviews:` inputs;
    - no `code-review` brief in `implement.md` names `Checks run`, a verify report or `commands_run`.
  - **`routing`:**
    - `classification.md` §4 names `test-writer` under `implementation_model`;
    - §3.1 no longer says the review completes before `/implement` runs any test;
    - its §9.2 table row names `code-writer` and `test-writer`, and no `/implement` `review-fixer`;
    - `bug-diagnosis.md` no longer holds "nothing runs against the working tree" as `/implement`'s rule, and names `test-writer` as the writer of the regression test.
  - **`tiers`:**
    - both `plugin.json` files and `marketplace.json` carry 4.32.0 and 1.46.0, and each CHANGELOG has its section;
    - `plugin-updates.md` has a 1.46.0 / 4.32.0 coupling bullet;
    - `CLAUDE.md`'s `dev-workflows` reference count equals `find plugins/dev-workflows/references -type f | wc -l`;
    - `docs/reference/agents.md` rows for `code-writer`, `test-writer` and `review-fixer` match their descriptions.
- [ ] **Step 2: Run it on the worktree.** Expected: every section FAILs. Save the output as `red.txt`, and record the counts in the SDD ledger.

### Task 2: `run-lock.py`

**Files:**
- Create: `plugins/dev-workflows/scripts/run-lock.py`.
- Modify: `.github/workflows/validate-catalog.yml` (a `Self-test the run lock` step after the run-state one); `plugins/dev-workflows/docs/commands/implement.md` (where it documents `run-state.py`, one paragraph on the lock).

**Interfaces:**
- Produces `python3 run-lock.py -- <command> [args…]`, run from inside a git work tree, and `python3 run-lock.py --selftest`.
  - The command inherits stdin, stdout and stderr, and the cwd.
  - While it waits, it prints one stderr line, `run-lock: waiting for <lock path>`.

- [ ] **Step 1: Write the selftest first.** Its cases, each a function:
  - `test_serialises`: two holders that each `sleep 1`, started together, have run windows that do not overlap;
  - `test_exit_code_passthrough`: `-- sh -c 'exit 7'` exits 7;
  - `test_killed_holder_releases`: a holder killed by SIGKILL frees the lock within 1 second;
  - `test_usage`: no `--`, or no command, exits 2;
  - `test_outside_repo`: run outside a git work tree, it exits 4;
  - `test_lock_path`: the lock file is `git rev-parse --git-path dev-workflows/run.lock`, its directory made if missing.
- [ ] **Step 2: Run `python3 run-lock.py --selftest`.** Expected: it fails, since the script has no body yet.
- [ ] **Step 3: Implement.** Use `fcntl.flock(fd, LOCK_EX)` on the lock file, then `subprocess.run(argv)`, mirroring `bounded.py`'s docstring style and its exit-code table. Without `fcntl`, warn and run.
- [ ] **Step 4: Run it.** Expected: `run-lock selftest: PASS`.
- [ ] **Step 5: Add the CI step,** and run `check.py lock`. Expected: it passes except the four call sites, which Tasks 5, 6, 8 and 9 add. Then run the gate chain: `EXIT=0`.
- [ ] **Step 6: Commit:** `feat(dev-workflows): run-lock.py — one build or test run at a time per work tree`.

### Task 3: The pieces section in `design-format`

**Files:**
- Modify: `plugins/dev-workflows/references/design-format.md` (a scaled `## Pieces` section after `## Interfaces / contracts`, renumbering the list); `plugins/dev-workflows/docs/reference/` (its design-format page, wherever it lists the sections).

**Interfaces:**
- Produces the format in Global Constraints, read by Task 9 (`/implement`) and, later, written by part (b) (`/design`) and checked by `design-reviewer`.

- [ ] **Step 1: Run `check.py pieces`.** Expected: FAIL.
- [ ] **Step 2: Write the section.** It holds:
  - the format;
  - when a piece is drawn: file sets that do not overlap, and a shared part the design fixes;
  - that pieces are review units;
  - that `Writers: per piece` needs its reason;
  - that a file no piece names belongs to the piece whose plan step creates it;
  - that no section means one piece named `all`.

  Say that `/design` writing it arrives in a later release. Until then a section is written by hand, and `/implement` reads it.
- [ ] **Step 3: Verify.** Run `check.py pieces` (expected PASS) and the gate chain (`EXIT=0`).
- [ ] **Step 4: Commit:** `feat(dev-workflows): design-format's Pieces section — review units, and separate writers only with a reason`.

### Task 4: The fix method, shared

**Files:**
- Create: `plugins/dev-workflows/references/review-fix.md`.
- Modify: `plugins/dev-workflows/agents/review-fixer.md` (its *Fix method* and *Output* point at the reference; its description no longer names `/implement`); `plugins/dev-workflows/docs/reference/references.md`; `plugins/dev-workflows/docs/reference/agents.md` (`review-fixer`'s row).

**Interfaces:**
- Produces the *Fix method* (steps 1–7, the patch gate through `finding-triage patch-gate`) and the `## Fix Report` shape (`### Applied`, `### Deferred`, `### Files changed`, `### Stop condition flag`), moved verbatim from `review-fixer.md`. It adds one paragraph: a writer in `mode: review` applies it only to files it owns.

- [ ] **Step 1: Run `check.py review-fix`.** Expected: FAIL.
- [ ] **Step 2: Move the text.** `review-fixer`'s behaviour for `/vuln` and `/upgrade` must not change: diff the moved text against the original. Expected: identical, save the one added paragraph.
- [ ] **Step 3: Verify.** Run `check.py review-fix` (expected PASS; the two writer citations come in Tasks 5 and 6), then the gate chain (`EXIT=0`; check 4 and check 9's reference count included).
- [ ] **Step 4: Commit:** `refactor(dev-workflows): the review fix method and Fix Report move to references/review-fix.md`.

### Task 5: `test-writer` — from the spec, with a shell

**Files:**
- Create: `plugins/dev-workflows/references/handoff/test-writer.md`.
- Modify: `plugins/dev-workflows/agents/test-writer.md`; `plugins/dev-workflows/docs/reference/agents.md`; `plugins/dev-workflows/docs/reference/references.md` (`handoff/` (7) → (8)).

**Interfaces:**
- **`## Test Writer Request`** has these fields:
  - `mode` (`write` | `fix` | `review`);
  - `task_description_file`, `plan_file`, `spec_paths` and `design_path` (or `none`);
  - `pieces` (each name with its files, or `all`);
  - `unit`;
  - `unit_files`, the unit's source files, for signatures;
  - `code_report`, the code writer's report, for `### Files changed` and `### Tests broken by intent`;
  - `baseline_file`;
  - `repo_root`;
  - `task_shape`;
  - `failure_input` (on `fix`);
  - `review_file` (on `review`);
  - `report_file`.
- **Evidence** is `plan_file`, `baseline_file` and `repo_root`, plus `failure_input` or `review_file` in their mode. **Context** is the rest.
- **It returns** the reply line `status: <done | needs_decision | blocked>`, with its report at `report_file`.
  - **On `write` and `fix`:** `## Test Writer Report`, today's shape with three additions: `### Tests updated` (each existing test changed, and the spec line that changed its behaviour); `### Runs` (each compile or test command it ran through the lock, with its result); and `— piece <name>` on each `### Tests added` entry where there are two or more pieces.
  - **On `review`:** `review-fix.md`'s `## Fix Report`.

- [ ] **Step 1: Run `check.py writers`.** Expected: FAIL.
- [ ] **Step 2: Write the handoff file,** with each field's read-failure tier (`dev-workflows:context-management`) and both report shapes.
- [ ] **Step 3: Rewrite the agent.**
  - **Description:** it writes and updates the tests for a unit from the spec, the design's interfaces and the plan, reading code only for signatures. It compiles and runs its own tests through the lock, and fixes its own test files. The caller assigns its tier.
  - **Steps:**
    - The framework is still taken from the baseline.
    - Behaviours are mapped from the spec's acceptance criteria and test cases, the design's `## Test strategy` and `## Seams`, and the plan's Review focus. Where there is no spec, they come from the task description and the plan.
    - Code is read only for names, signatures and file locations, never to learn what it does.
    - It updates each test the `code_report`'s `### Tests broken by intent` names, where the spec says the behaviour changed. Where the spec does not settle it, it returns `needs_decision`.
    - On `task_shape: bug` it writes the regression test from the plan's diagnosis and repro.
    - Then it compiles and runs its own new and updated tests through the lock, and fixes its own errors. A failure that shows the code disagrees with the spec is reported, never "fixed" by weakening the test.
  - **Keep** the falsifiability gate, the no-mirror and no-change-detector rules, the negative DOM rule and the mutation self-check.
  - **Hard rules:**
    - never edit a non-test file;
    - never run anything except through the lock;
    - never change what a pre-existing test asserts, save one `### Tests broken by intent` names, where the spec says so.
  - **Mode `fix`:** `failure_input` names failing tests it owns; it fixes them and re-runs them.
  - **Mode `review`:** `review-fix.md`, on test files only.
- [ ] **Step 4: Verify.** Run `check.py writers` (the `test-writer` assertions PASS) and the gate chain (`EXIT=0`; checks 4, 9 and 20).
- [ ] **Step 5: Commit:** `feat(dev-workflows): test-writer writes from the spec and runs its own tests through the lock`.

### Task 6: `code-writer` — one unit, its own build and nearby tests

**Files:**
- Modify: `plugins/dev-workflows/agents/code-writer.md`, `plugins/dev-workflows/references/handoff/code-writer.md`, `plugins/dev-workflows/docs/reference/agents.md`.

**Interfaces:**
- **`## Code Writer Request` changes:**
  - `mode` becomes `write` | `fix` | `review`;
  - `steps` is replaced by `unit` (its name), `pieces` and `unit_files` (the files its pieces name), with `plan_file`'s steps whose `Piece:` lies in the unit;
  - `review_file` is added, on `review`.
- **`## Code Writer Report` adds:**
  - `### Checks run`: each build and nearby-test command, run through the lock, with its result;
  - `### Tests broken by intent`: each existing test that fails because the spec changes what it asserts, with the spec line.
- **On `review`,** it returns `review-fix.md`'s `## Fix Report`.
- **The statuses are unchanged.**

- [ ] **Step 1: Run `check.py writers`.** Expected: the `code-writer` assertions FAIL.
- [ ] **Step 2: Rewrite the request and report** in the handoff.
- [ ] **Step 3: Rewrite the agent.**
  - **It codes the whole unit in one dispatch.** Earlier reports and the diff so far serve a fallback dispatch and a `needs_decision` continuation, as today.
  - ***What you may do* gains:** run the repository's build and the nearby tests through the lock, after its edits, and fix what it broke. Nearby tests are the tests of the package or module directory its change touches, run by the baseline's command scoped to that directory where the runner takes a path, else that suite whole. List each run under `### Checks run`.
  - ***What you may never do* loses** the no-build, no-test rule, and gains:
    - never edit a test file;
    - never edit a file outside `unit_files`, save a new file its unit's steps create. One outside is a `needs_decision` naming the file;
    - never run anything except through the lock.
  - **Bug work** keeps the repro and probes in the scratch checkout of `HEAD`. It drops writing the regression test, which is `test-writer`'s, and drops "a test this run created or changed you never run". A test this run wrote is the test writer's to run.
  - **Mode `fix`:** as today, plus it runs the failing checks again through the lock before returning.
  - **Mode `review`:** `review-fix.md`, on its unit's non-test files only.
  - **One sentence** on being reached again: a later request may arrive in the same conversation by `SendMessage`; it carries on from what it already knows and re-reads only what changed since.
- [ ] **Step 4: Verify.** Run `check.py writers` (expected PASS) and the gate chain (`EXIT=0`).
- [ ] **Step 5: Commit:** `feat(dev-workflows): code-writer codes a whole unit and runs its build and nearby tests through the lock`.

### Task 7: The run-state keys

**Files:**
- Modify: `plugins/dev-workflows/scripts/run-state.py` (`KEYS`, the selftest), and `plugins/dev-workflows/commands/implement.md` (the `KEYS_LINE` it quotes).

**Interfaces:**
- **Remove** `step_groups` and `files.test_diff_file`.
- **Add** these keys:
  - `pieces`: `[{"name", "files": [], "builds_after": []}]`, default `[]`;
  - `writer_units`: `[{"name", "pieces": []}]`, default `[]`;
  - `writers`: `[{"unit", "role": "code"|"test", "agent_id", "reports": [], "status", "answer", "left_to_caller": [], "resumes": 0, "fresh": 0}]`, default `[]`;
  - `test_runs`: `[{"unit", "stage": "unit"|"post-review", "rounds": 0, "status"}]`, default `[]`;
  - `reviews`: `[{"scope", "diff_file", "return_file", "verdict"}]`, default `[]`, where `scope` is `piece:<name>` or `overall`.
- Task 9 writes all five.

- [ ] **Step 1: Add the selftest cases first.** `init` accepts and defaults each new key; `set`/`append` on `step_groups` exits 3; `KEYS_LINE` equals `implement.md`'s quoted line.
- [ ] **Step 2: Run `python3 run-state.py --selftest`.** Expected: FAIL.
- [ ] **Step 3: Change `KEYS`,** and the quoted line in `implement.md`'s Phase 1.4.
- [ ] **Step 4: Verify.** The selftest PASSes, `check.py state` PASSes, and the gate chain reads `EXIT=0`.
- [ ] **Step 5: Commit:** `feat(dev-workflows): run-state keys for pieces, writer units, writers, test runs and reviews`.

### Task 8: `test-baseliner` through the lock

**Files:**
- Modify: `plugins/dev-workflows/agents/test-baseliner.md` (one rule where it states how it runs a suite, and one hard rule); `plugins/dev-workflows/references/handoff/test-baseliner.md`, if it states the run form.

- [ ] **Step 1: Add the rule.** Every suite command it runs, in capture and in verify, runs through `run-lock.py`. `/vuln` and `/upgrade`, which share it, are unaffected but for waiting.
- [ ] **Step 2: Verify.** `check.py lock` passes on `test-baseliner.md`, and the gate chain reads `EXIT=0`.
- [ ] **Step 3: Commit:** `feat(dev-workflows): test-baseliner runs every suite through run-lock.py`.

### Task 9: `implement.md` — Phase 3, Code and tests; Phase 3.5, Test run

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md`:
  - frontmatter `allowed-tools`, adding `SendMessage`;
  - Phase 0's `model_routing` block;
  - Phase 2A's plan format and `risk-planner`'s brief: each Step carries `Piece:` where there are two or more pieces;
  - Pre-Phase 3.5;
  - Phases 3A, 3B and 3.5, rebuilt;
  - Phase 4.6's `"Every run"` list;
  - Phase 5's report sections;
  - Invariants.
- Modify: `plugins/dev-workflows/agents/risk-planner.md` (the `Piece:` line on each Step, where the brief names pieces).

**Interfaces:**
- Consumes Tasks 2, 3, 5, 6 and 7.
- Produces Phase 3's writer dispatch and resume pattern, which Task 10 reuses for `mode: review`.

- [ ] **Step 1: Run `check.py flow` and `check.py state`.** Expected: FAIL.
- [ ] **Step 2: Read the pieces.**
  - **Where:** at Phase 1.8, after the ARD, from the in-scope `design.md`'s `## Pieces`.
  - **What it writes:** run-state `pieces`, and `writer_units`. `Writers: one` gives one unit holding every piece; `per piece` gives one unit per piece, in `Builds after` order.
  - **A malformed section** — two pieces matching one path, or `per piece` with no reason — is a Phase 1 question: `choices: ["Treat it as one piece (Recommended)", "Stop here"]`.
- [ ] **Step 3: Write Phase 3 — Code and tests (every class).** Keep the orchestrator's mechanical actions first: the bisect and the patches. Then, for each writer unit, in order:
  1. **Dispatch `code-writer`** (`mode: write`) on `implementation_model`, recording its agent id in `writers`. Act on its return as Phase 3A step 1 does today: the fold, `needs_decision`, `trigger` and `blocked` with its one re-plan. A continuation after `needs_decision` or `trigger` is a `SendMessage` to the same agent, carrying the answer.
  2. **Once `done`, dispatch `test-writer`** (`mode: write`) on `implementation_model`, with `code_report` set to the code writer's report. Act on its return. Record its `### Runs` and `### Tests updated` into the Phase 5 report's `### Commands / tests run` and `### Assumptions & limitations`.
  3. **Go on to Phase 3.5** for this unit. Only once that test run is green or settled does the next unit start.
  - **State the fallback** in Global Constraints' words, once, in Phase 3's lead-in. Every later resume cites it.
  - **Delete** the step-group rule, its `step_groups` writes and the *Decompose* sentence. In their place goes the continuation: a writer that returns with work left (its report's **Steps** line) is resumed with "continue", and fresh-dispatched only per the fallback.
- [ ] **Step 4: Write Phase 3.5 — Test run.**
  - **The red-capability check** on `task_shape: bug`, and the repro's re-run against the change, both move here, from Phase 3B step 8.
  - **Then lint and build, and `test-baseliner` verify.** Everything runs through the lock, and the `Status` and `### New failures` arms stay as today.
  - **Each failure goes to its owner,** by `SendMessage`, `mode: fix`, with the failing part of the report: a test file to `test-writer`, any other file to the unit's `code-writer`. Both are sent in the same round, one after the other, never at once.
  - **Where a test and the code disagree,** and a writer says so, the orchestrator decides against the spec and the design. It asks the user where neither settles it.
  - **At most 3 rounds per test run** (run-state `test_runs.<n>.rounds`), then today's question.
  - **Stage `post-review`** is the same loop, entered from Phase 3.6.
- [ ] **Step 5: Renumber every cross-reference** in `implement.md`. Phase 3A and 3B steps become Phase 3, 3.5 and 3.6 steps. Count `Phase 3A` and `Phase 3B` mentions before and after: today 84 in `implement.md`, and 0 after.
- [ ] **Step 6: Verify.**
  - Run `check.py flow` and `check.py state` (expected PASS, save the `review` section's Phase 3.6 assertions), then the gate chain (`EXIT=0`; `check-questions` included).
  - Do an end-to-end read of a SIMPLE run, a MODERATE keyed run and a SIGNIFICANT bug run through Phases 3 and 3.5. Every edit is a writer's or a mechanical action, every return has an outcome, every stop names `stash_ref`, and nothing builds outside the lock.
- [ ] **Step 7: Commit:** `feat(dev-workflows): /implement codes each writer unit through one code-writer and one test-writer, then runs its tests`.

### Task 10: `implement.md` — Phase 3.6, Review

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 3.6, Invariants); `plugins/dev-workflows/agents/code-review.md` (the `Scope:` and `Piece reviews:` inputs, and the overall review's focus).

**Interfaces:**
- **`Scope:`** reads `piece <name> — files: <list>` or `overall — pieces: <names>`.
- **`Piece reviews:`** gives the piece reviews' return files, on `overall` only.
- **The review diff** for a piece is limited to its files and the test files `test-writer` mapped to it.

- [ ] **Step 1: Run `check.py review`.** Expected: FAIL.
- [ ] **Step 2: Write Phase 3.6,** from MODERATE up. SIMPLE goes from Phase 3.5 to Phase 4, as today.
  - **Probes:** strip `[DEBUG-xxxx]`.
  - **One review per piece:** capture each piece's diff, then dispatch one `code-review` per piece, in parallel. Each takes today's brief plus `Scope:`, and none carries a test result.
  - **Then the overall review,** with `Piece reviews:` and the whole diff.
  - **Triage each return** under `workflows-core:finding-triage`, as today.
  - **Route the survivors by owner.** Write each owner's to its own `review_file`, then `SendMessage` it, `mode: review`, one owner at a time. A finding spanning units goes to the owner of the file that keeps the fix, the orchestrator naming it.
  - **Gather the Fix Reports** into `claims_file`. The `Stop condition flag` is read over all of them together.
  - **Unchanged in rule, with owners for `review-fixer`:**
    - the plan-conflict ruling;
    - the offer to apply what a review leaves open;
    - the one re-review, which re-runs each piece review whose piece got fixes, plus the overall one;
    - the settle prompts;
    - the stayed-blocked stop.
  - **Then Phase 3.5, stage `post-review`.** Where its fixes are non-trivial, the delta gets one `overall` review, as today's step 8 does.
  - **Step 7.5's conformance escalation** stays, after the review.
- [ ] **Step 3: Update `code-review.md`'s Inputs** for `Scope:` and `Piece reviews:`. An overall review looks for what piece reviews cannot see: where pieces meet, duplicated helpers, inconsistent conventions and the shared contract.
- [ ] **Step 4: Verify.**
  - Run `check.py review` and `check.py flow` (expected PASS), then the gate chain (`EXIT=0`).
  - Do an end-to-end read of a BLOCK path, a PASS WITH RECOMMENDATIONS path with the offer, and a plan conflict, each on a two-piece, one-writer run.
- [ ] **Step 5: Commit:** `feat(dev-workflows): /implement reviews each piece and the whole, and sends every fix to the file's owner`.

### Task 11: The shared rules — routing, bug diagnosis, triage, escalation

**Files:**
- Modify:
  - `plugins/workflows-core/references/model-routing/classification.md`: §3.1 and §3.2 (review before tests), §4 (`implementation_model` and `fixes_model`, and the agents that receive the block), and the §9.2 table rows;
  - `plugins/dev-workflows/references/bug-diagnosis.md` (*Who runs the repro*, § *When a run may happen — the review gate*, step 4's regression test, the post-gate checks);
  - `plugins/workflows-core/references/finding-triage.md` (its attachment rule's `/implement` pair);
  - `plugins/workflows-core/references/escalation-rules.md` (the offer's "its edits are `review-fixer`'s" for `/implement`).
- Then run `python3 scripts/reference-parts.py generate`.

- [ ] **Step 1: Run `check.py routing`.** Expected: FAIL.
- [ ] **Step 2: Edit each, to the design's §5.**
  - **The review gate rule becomes:** from the first edit, checks run only through the lock (the code writer's, the test writer's and the orchestrator's), and the repro and probes stay in the scratch checkout of `HEAD` until Phase 3.5.
  - **`test-writer`** is dispatched on `implementation_model`.
  - **`/implement`'s fixes** go to the file's owner, and its edits under the offer are the owner's.
- [ ] **Step 3: Regenerate the parts,** and run `reference-parts.py check-parts` and `check-citations`.
- [ ] **Step 4: Sweep by subject** (claim-sweep refinements 4–8) for each reversed rule in design §5, across `plugins/` (every `CHANGELOG.md` read, history left), `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`. The subjects:
  - review before tests;
  - `code-writer` running no build or test;
  - `test-writer` from the diff, with no shell;
  - `review-fixer` in `/implement`;
  - step groups;
  - the two fix attempts;
  - who writes the regression test.

  Count each literal before and after.
- [ ] **Step 5: Verify.** Run `check.py routing` (expected PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 6: Commit:** `feat(workflows-core,dev-workflows): the review gate, test-writer's tier, and /implement's fixes by owner in the shared rules`.

### Task 12: Docs, tiers, versions and changelogs

**Files:**
- Modify:
  - `plugins/dev-workflows/docs/commands/implement.md`;
  - `plugins/dev-workflows/docs/workflow.md`, if its diagram shows who codes or tests;
  - `plugins/dev-workflows/docs/reference/` (the model-routing and test-suite-detection pages, wherever they state the old flow);
  - `.claude/rules/dev-workflows.md` (the `/implement` map line, and the agent caller lines: `review-fixer` used by `/vuln` and `/upgrade`);
  - `.claude/rules/dev-workflows-implement.md`;
  - `.claude/rules/dev-workflows-tests.md`;
  - `.claude/rules/workflows-core.md` (its model-routing caller sentence: which agents load `classification` for criteria);
  - `.claude/rules/plugin-updates.md` (the coupling bullet);
  - `CLAUDE.md` (`dev-workflows`' reference count; re-derive it with `find plugins/dev-workflows/references -type f | wc -l`);
  - both `plugin.json` files, `marketplace.json`, and both `CHANGELOG.md`s.

- [ ] **Step 1: Run `check.py tiers`.** Expected: FAIL.
- [ ] **Step 2: Rewrite the `/implement` docs page** from `implement.md` as it now stands:
  - the phases;
  - who writes code and tests, and on which model;
  - the pieces;
  - the lock;
  - resume and fallback;
  - the fix cap;
  - the per-piece review.
- [ ] **Step 3: Write the coupling bullet.** `workflows-core` 1.46.0 goes with `dev-workflows` 4.32.0:
  - 1.46.0's `classification` puts `test-writer` on `implementation_model`, drops review-before-tests for `/implement`, and has `finding-triage` and `escalation-rules` send `/implement`'s fixes to the file's owners;
  - an older `workflows-core` contradicts all three;
  - an older `/implement` beside 1.46.0 meets rules for owners it does not dispatch.

  Re-read the whole bullet list against it (claim-sweep refinement 8).
- [ ] **Step 4: Bump the versions, and write the changelog sections,** one bullet per behaviour change.
- [ ] **Step 5: Verify.** Run `check.py all` (expected all PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 6: Commit:** `docs(dev-workflows,workflows-core): one writer per unit in the docs and tiers (dev-workflows 4.32.0, workflows-core 1.46.0)`.

### Task 13: Rule-by-rule reading (controller)

- [ ] **Step 1: Measure** `wc -c` of `implement.md`, `code-writer.md`, `test-writer.md` and their handoffs, at the base and at the branch tip. Record both.
- [ ] **Step 2: Read old Phases 3A, 3B and 3.5 against the new Phases 3, 3.5 and 3.6,** rule by rule.
  - Every old rule is kept, moved (say where), or retired by design §5 (cite the line).
  - A rule lost without a §5 line is a defect: fix it in this task.
  - Record the table in the SDD ledger.
- [ ] **Step 3: Verify.** Run `check.py all` and the gate chain (`EXIT=0`).

### Task 14: Whole-branch review

- [ ] **Step 1: Dispatch the whole-branch review on Opus,** per the SDD skill, with the spec, this plan and the diff from the base. Fix every finding in one wave, minors included (the user's rule), then run one scoped re-review.
- [ ] **Step 2: Verify.** Run `check.py all` and the gate chain (`EXIT=0`).

### Task 15: Live A/B on the e2e copies (controller, with the user)

Run as lean context parts 1 and D ran theirs:
- `~/e2e-copies.sh`, with `E2E_PLUGIN_SRC=<worktree>/plugins` for arm B;
- the reset checklist (memory `e2e-test-bed`);
- `session-cost.py` for cost;
- a blind Opus judge given both arms' diffs and reports, unlabelled;
- `~/e2e-implement-snapshot.sh --check` after each run.

Arm A is `main` at the branch base (dev-workflows 4.31.0). Arm B is the branch.

- [ ] **Step 1: Build the big test Epic** in the e2e bookstore specs copy (allowed by the user). It is a PRD, an Epic, a `specification.md` and a `design.md` whose `## Pieces` names at least two loosely coupled pieces with `Writers: per piece — <reason>`. It must be big enough that the reason is true. Show it to the user before any run.
- [ ] **Step 2: Run the pairs.** Each pair is run on both arms, on the same inputs:
  - route 3 (baseline `beebc3f3`);
  - run B, the direct MODERATE run (baseline `5023b937`);
  - the big test Epic.

  For each run, record:
  - cost;
  - the main session's cache reads;
  - dispatches, resumes and fresh dispatches;
  - fix rounds;
  - review verdicts;
  - any two builds overlapping (from the lock's waiting lines).
- [ ] **Step 3: Judge each pair blind.** Where a verdict's margin is small, repeat that pair before believing it (the user's decision). Where B looks worse, run arm A again to tell noise from cause.
- [ ] **Step 4: Fix each finding** through Task 14's loop, then re-run the pair it came from.
- [ ] **Step 5: Restore the copies,** with the user's OK.

### Task 16: Record, merge and push (controller, with the user)

- [ ] **Step 1: Write the verification record** last (`docs/superpowers/verification/2026-10-24-implement-one-writer-a.md`). It holds:
  - the reading's table;
  - the A/B results with their repeats;
  - the measurements;
  - every ruling.

  Preserve the rulings and the SDD ledger beside it.
- [ ] **Step 2: Re-check `origin/main`.** Where it moved, merge it in, and re-run `check.py all` and the gate chain.
- [ ] **Step 3: Date both changelog sections** with the merge date.
- [ ] **Step 4: Merge `--no-ff` into `main`,** in a temporary worktree, never by `git checkout` in the main checkout. Run the gate chain there with `ASSERT_PUBLISHED=1`.
- [ ] **Step 5: Ask the user before `git push origin main`.** After it, give `claude plugin update workflows-core@shipwright` and `claude plugin update dev-workflows@shipwright`, then a restart.
- [ ] **Step 6: Update `docs/superpowers/to-fix.md` E4's `40e6b9ea` row,** in the same push. The editions now port this part instead.

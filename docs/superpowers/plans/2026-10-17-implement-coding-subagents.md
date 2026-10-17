# `/implement` coding subagents — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/dev-workflows:implement` writes its code through a new `dev-workflows:code-writer` subagent, one dispatch per plan step group, on a model chosen by the run's class. Its run state lives in a file the orchestrator re-reads at every phase. Its MODERATE runs pass the Opus review gate.

**Architecture:** The work is prose in markdown command, agent and reference files, which agents execute literally.
- A new agent, with its handoff contract.
- `implement.md` restructured so that Phases 3A, 3B and 3.5 dispatch, rather than edit.
- A run-state file under the code repository's git directory.
- `classification.md` carve-outs for the model rule and the MODERATE review.

A scratch `check.py`, written first (Task 0), pins every decision as an assertion. The repository's gate chain, and two live runs on the bookstore demo, verify the result.

**Tech Stack:** Markdown prose (commands, agents, references, docs), Python 3 for the scratch check, bash gates (`scripts/check-docs.sh`, `scripts/validate-catalog.py`, `scripts/check-id-grammar.sh`, `scripts/mermaid/check-mermaid.mjs`).

**Spec:** `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md`. It is the authority; this plan argues from it.

## Global Constraints

- **The new agent is `dev-workflows:code-writer`,** in `plugins/dev-workflows/agents/code-writer.md`.
  - Tools: `["Read", "Glob", "Grep", "Write", "Edit", "Bash"]`.
  - No `model:` in its frontmatter: the caller assigns it, and the docs say "per routing".
  - No `Task`.
- **Its contract is `plugins/dev-workflows/references/handoff/code-writer.md`.**
- **The run-state file is `$(git rev-parse --git-path dev-workflows/implement-run.json)`,** in the code repository.
- **The model rule:**
  - SIMPLE → `current_model`;
  - MODERATE, SIGNIFICANT, HIGH-RISK → `current_model` where it is an Opus or Fable model, else the §2 Opus chain's first available row;
  - `--enforce-model` overrides both (§10).
- **The four statuses, verbatim:** `done`, `needs_decision`, `trigger`, `blocked`.
- **The blocked question, verbatim:** `choices: ["Revise the plan (you'll be prompted)", "Stop here — the work so far is committed through Phase 4.6"]`.
- **Scope of the MODERATE review.** Only `/implement` reviews MODERATE work. `/vuln` and `/upgrade` routing is unchanged. `classification.md` §3.1 gains one carve-out sentence for `/implement`.
- **SIMPLE runs stay unreviewed.**
- **Untouched agents:** `test-writer`, `code-review`, `risk-planner`, `test-baseliner` and the maintenance agents keep their models.
- **Versions:** `dev-workflows` 4.29.0 and `workflows-core` 1.43.0, each with a `— Unreleased` CHANGELOG section until the merge task dates it.
- **Repository rules** (`CLAUDE.md`):
  - `choices:` arrays hold 2–4 options, are verbatim, and no label promises text (check 12);
  - vendor neutrality (check 13);
  - never name the internal organisation (check 14);
  - every agent carries `workflows-core`'s untrusted-content block byte for byte (check 20);
  - every count in `CLAUDE.md` and `.claude/rules/` is re-derived with its command;
  - "prose is executed".
- **Branch and worktree:** branch `iv-gu/implement-coding-subagents`, worktree `/workspace/ai-workflows/.worktrees/implement-coding-subagents`.
  - Never `git checkout` in `/workspace/ai-workflows`.
  - Stage `.claude/` files with `git add -f`.
  - Run with `PYTHONDONTWRITEBYTECODE=1`.
- **The gate chain:** `/tmp/claude-502/-workspace-ai-workflows/80e0a056-a775-409e-9cb9-213f6b475bf7/scratchpad/gates.sh <worktree>`, which runs `.github/workflows/validate-catalog.yml`'s steps as one `&&` chain with `ASSERT_PUBLISHED=1`. Read its `EXIT=` line.

## Review Focus

1. **A plan of many tiny steps.** The run groups them and does not dispatch ten one-line edits as ten subagents. *Pinned:* Task 4's check asserts the grouping rule's sentence; Task 9's run counts the dispatches.
2. **A compaction mid-run.** The orchestrator still names the stash and keeps the user's dirty files out of the commit. *Pinned:* Task 3's check asserts that the re-read sentence opens every phase from Phase 1.4 to Phase 5, and that Phase 4.6 reads `pre_existing_dirty` and `stash_ref` from the file.
3. **A `needs_decision` partway through a step.** The fresh dispatch after the answer neither redoes nor undoes what the first one coded. *Pinned:* Task 4's check asserts that the fresh dispatch is handed the earlier report's path and the diff so far.
4. **A Sonnet, Haiku or Fable session.** The coding never runs below the session model, and never below Opus from MODERATE up. *Pinned:* Task 2's check asserts the rule's wording in §4, and Task 9 runs a Sonnet session.
5. **A run-state file left by a crashed run.** It is moved aside and never read as this run's state. *Pinned:* Task 3's check asserts the move-aside sentence and the `.stale-` name.

---

### Task 0: The scratch check (controller)

Run by the controller, not a subagent. It creates scratch files only, and a RED measurement.

**Files:**
- Create: `/tmp/claude-502/-workspace-ai-workflows/80e0a056-a775-409e-9cb9-213f6b475bf7/scratchpad/coding-subagents/check.py`

**Interfaces:**
- Produces: `python3 check.py <worktree> <section|all>`, with sections `agent`, `routing`, `state`, `dispatch`, `moderate`, `bug`, `tiers`. Each assertion prints `ok <name>` or `FAIL <name>: <why>`, and the run ends `all: N passed, M failed`.

- [ ] **Step 1: Write `check.py`, one function per section.** Each pins only strings this plan fixes:
  - **`agent`:**
    - the agent file exists, its frontmatter `name: code-writer`, its tools list as in Global Constraints, and no `model:` line;
    - its body contains the four statuses;
    - its body contains `workflows-core/references/untrusted-content.md`'s block, byte for byte;
    - the handoff file exists.
  - **`routing`:**
    - `classification.md` §4 contains `code-writer`, and the rule's phrase `an Opus or Fable model`;
    - §3.1 contains `/implement` beside `MODERATE` and `code review`;
    - §10 no longer contains `` `/implement`'s `implementation_model` (inline coding) ``.
  - **`state`:**
    - `implement.md` contains `dev-workflows/implement-run.json` and `.stale-`;
    - every `## Phase` heading from `Phase 1.4` to `Phase 5` is followed, within its first paragraph, by the sentence `Read the run-state file first.`;
    - Phase 4.6 contains `pre_existing_dirty` and `stash_ref` read from the file.
  - **`dispatch`:**
    - `subagent_type: "dev-workflows:code-writer"` appears in Phase 3A, Phase 3B and Phase 3.5;
    - every `→ Agent (` line in `implement.md` contains `model:`;
    - `review-fixer`'s dispatch line contains `implementation_model`, not `detection_model`;
    - the blocked `choices:` string appears verbatim;
    - the phrase `The **session model** (not a subagent) applies fixes` is absent.
  - **`moderate`:** Phase 3A contains a `dev-workflows:code-review` dispatch, and the phrase `MODERATE` within its gate's lead-in.
  - **`bug`:** `bug-diagnosis.md` and `risk-planner.md` each name `code-writer`.
  - **`tiers`:**
    - `CLAUDE.md` says `fourteen reusable subagents` and `nineteen reference files` for `dev-workflows`;
    - `docs/reference/agents.md` has a `code-writer` row;
    - `docs/reference/references.md` says `handoff/` (7);
    - `plugin.json` and `marketplace.json` carry 4.29.0 and 1.43.0;
    - each CHANGELOG has its section;
    - `.claude/rules/plugin-updates.md` has a `1.43.0` and `4.29.0` coupling line.
- [ ] **Step 2: Run it on the worktree.** Expected: every section FAILs except the `→ Agent (`/`model:` assertion, which passes today. Save the output as `red.txt` beside it.
- [ ] **Step 3: Record the RED counts in the SDD ledger.**

### Task 1: The coding agent and its contract

**Files:**
- Create: `plugins/dev-workflows/agents/code-writer.md`, `plugins/dev-workflows/references/handoff/code-writer.md`
- Modify:
  - `plugins/dev-workflows/docs/reference/agents.md` (a row under *Writers*);
  - `plugins/dev-workflows/docs/reference/references.md` (`handoff/` (6) → (7), and what reads the new file);
  - `CLAUDE.md` (`dev-workflows`' "thirteen reusable subagents" → "fourteen", and "eighteen reference files" → "nineteen"; re-derive each with `ls plugins/dev-workflows/agents | wc -l` and `find plugins/dev-workflows/references -type f | wc -l`);
  - the docs README's inventory, wherever check 9 counts it.

**Interfaces:**
- Produces: `dev-workflows:code-writer`, dispatched with `model:` by the caller and handed a handoff whose fields Task 4 fills:
  - `plan_file`;
  - `steps` (the plan step numbers it codes);
  - `spec_paths`;
  - `summary_file`;
  - `repo_root`;
  - `diff_so_far`;
  - `earlier_reports`;
  - `patches`;
  - `task_shape`;
  - `class`;
  - `scratch_checkout`, on bug work after the first edit, else `none`;
  - `mode` (`step` | `fix`);
  - `failure_input`, on `mode: fix` (the verify report, or the lint or build output).
- It returns:
  - its first line, `status: <done | needs_decision | trigger | blocked>`;
  - its report, written to `report_file`. The report holds `### Files changed`; `### Settled by the run` (each open question, with what was chosen); `### Out of scope` (another repository's need); and, by status, `### Decision` (the question, two to four options, and what is already coded), `### Trigger` (the §1.1 item and the paths that show it) or `### Blocked` (what the plan names that is not so).

- [ ] **Step 1: Run `check.py <worktree> agent`.** Expected: FAIL. This is the RED from Task 0.
- [ ] **Step 2: Write the handoff file.** It holds the input fields above with their read-failure tier: an evidence input is a hard stop, a context input degrades. That's `dev-workflows:context-management`'s convention, which `test-baseliner.md`'s handoff follows. It also holds the report shape.
- [ ] **Step 3: Write the agent file.**
  - **Frontmatter** as in Global Constraints.
  - **The `implement.md` rules it takes over:** Phase 3A/3B steps 2–4 move into the body — surgical changes only, the branched repository only, existing style and LF, and the decision and trigger tests of Phase 3A step 5, as *return* conditions.
  - **The may and may-never lists,** verbatim in sense from the spec's *The coding subagent*.
  - **The untrusted-content block,** byte for byte.
  - **One sentence:** it never asks the user, never dispatches, and never writes git state.
- [ ] **Step 4: Update the docs row, the references page and the `CLAUDE.md` counts.**
- [ ] **Step 5: Verify.** Run `check.py <worktree> agent` (expected PASS), then `./scripts/check-docs.sh --root .` (expected PASS: checks 4, 9 and 20 included).
- [ ] **Step 6: Commit.** Verify the branch, then `feat(dev-workflows): code-writer, the agent /implement codes through`.

### Task 2: The model rule in `classification.md`

**Files:**
- Modify:
  - `plugins/workflows-core/references/model-routing/classification.md`: §3.1, §4 (`implementation_model`, `fixes_model`, and the list of agents that receive the block), §10 (the inline-coding carve-out);
  - `plugins/workflows-core/docs/` and `plugins/dev-workflows/docs/reference/model-routing.md`, wherever each states these.

**Interfaces:**
- Produces:
  - §4's `implementation_model` field, now "the model `/implement`'s `code-writer` is dispatched on", resolved by the rule in Global Constraints;
  - `fixes_model` "= `implementation_model` for `/implement`; = `detection_model` elsewhere";
  - §3.1's carve-out: "`/implement` alone reviews MODERATE work with the Opus `code-review` gate (its Phase 3A); every other caller skips it as this section says".

- [ ] **Step 1: Run `check.py <worktree> routing`.** Expected: FAIL.
- [ ] **Step 2: Edit §3.1, §4 and §10.**
  - **§10:** drop `/implement` from the list of commands that code inline, and keep `/prd-proposal`'s and `/brd-proposal`'s `authoring_model`.
  - **§4:** add `code-writer` to the list of agents that receive the block, if its handoff declares it (Task 1 decides; declare it).
- [ ] **Step 3: Sweep by subject (claim-sweep refinements 6–8)** for `implementation_model`, `fixes_model`, "Skip the dedicated Opus code review" and "inline coding", across `plugins/`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`. Count each before and after. `/vuln`'s and `/upgrade`'s own uses stay, and the docs pages follow.
- [ ] **Step 4: Verify.** Run `check.py routing` (expected PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 5: Commit.** `feat(workflows-core): implementation_model names /implement's code-writer; /implement reviews MODERATE`

### Task 3: The run-state file

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md`: Phase 1.4, the opening of every phase from Phase 1.4 to Phase 5, Phase 4.6, the stops, and Invariants.

**Interfaces:**
- Produces: the file at `$(git rev-parse --git-path dev-workflows/implement-run.json)`, JSON with these keys:
  - `format: 1`;
  - `phase`;
  - `class`;
  - `coding_model`;
  - `branch_answer`;
  - `branch`;
  - `stash_ref`;
  - `pre_existing_dirty` (`[{path, fingerprint}]`);
  - `test_decision`;
  - `clean_finish`;
  - `files` (`{plan_file, summary_file, test_diff_file, review_diff_file, partial_diff_file}`);
  - `step_groups` (`[{steps, status, report}]`);
  - `patches` (`[{path, outcome}]`);
  - `triage` (`[ruling]`);
  - `assumptions` (`[text]`);
  - `replans_used` (`0` | `1`).

  Tasks 4 and 5 write to `step_groups`, `patches` and `replans_used`.

- [ ] **Step 1: Run `check.py <worktree> state`.** Expected: FAIL.
- [ ] **Step 2: Create the file in Phase 1.4.** Before Phase 1.4's first write, any existing file is renamed `implement-run.json.stale-<UTC compact stamp>` and named once in `### Assumptions & limitations`, never read. Then write the file. Every later change to a key is written through at once.
- [ ] **Step 3: Open each phase with the same sentence,** `Read the run-state file first.`, from Phase 1.4 to Phase 5, followed by: its keys are the run's state, never memory. Phase 4.6 and every stop read `pre_existing_dirty` and `stash_ref` from it.
- [ ] **Step 4: Remove the file** on every exit that Phase 4.6 or a stop reaches, guarded to the path the `git rev-parse` gives.
- [ ] **Step 5: Add one invariant line** to `implement.md`'s Invariants, and to `.claude/rules/dev-workflows-implement.md`.
- [ ] **Step 6: Verify.** Run `check.py state` (expected PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 7: Commit.** `feat(dev-workflows): /implement keeps its run state in a file it re-reads every phase`

### Task 4: Coding through `code-writer` (Phases 3A and 3B)

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md`: Phase 0's `model_routing` block, Phase 3A steps 1–5, Phase 3B steps 1–4, `review-fixer`'s dispatch (~:760), and Invariants.

**Interfaces:**
- Consumes: Task 1's handoff fields and return, Task 2's `implementation_model`, Task 3's `step_groups`, `patches` and `replans_used`.
- Produces: the dispatch pattern Task 5 reuses for `mode: fix`.

- [ ] **Step 1: Run `check.py <worktree> dispatch`.** Expected: FAIL.
- [ ] **Step 2: Phase 0's `model_routing` block.** `implementation_model` follows the rule, and `fixes_model` equals it.
- [ ] **Step 3: Rewrite Phase 3A step 1 and Phase 3B step 1.**
  - **The orchestrator first does its mechanical actions:** the bisect step, then applying the patches. It records each patch's outcome in `patches`.
  - **Then the step groups.** By default, one dispatch per plan step. Consecutive steps whose text names exactly the same file or files group into one dispatch, up to four steps. Groups run in plan order, one at a time.
  - **The dispatch** is `→ Agent (subagent_type: "dev-workflows:code-writer", model: <implementation_model>)`, with the handoff fields, the report path, and the diff so far.
- [ ] **Step 4: Handle each return.**
  - **`done`:** record it, and fold `### Settled by the run` into `assumptions` and `### Out of scope` into step 2's follow-up rule.
  - **`needs_decision`:** ask the report's `### Decision` question with its choices, then make a fresh dispatch for the rest of the group, handed the earlier report and the diff so far.
  - **`trigger`:** Phase 3A step 5's existing raise, unchanged from "Stop editing", and continue under the new class's model.
  - **`blocked`:** the spec's question, verbatim. *Revise* means Phase 2A's *Revise* at SIMPLE/MODERATE, or `risk-planner`'s re-plan with its approval at SIGNIFICANT/HIGH-RISK, and it sets `replans_used: 1`. With `replans_used: 1`, `blocked` stops through Phase 4.6 with `clean_finish: false`. Add *Stop* to Phase 4.6's "Every run" list.
  - **A failed or unreadable return** is retried once with the same brief. A second failure is `blocked`.
- [ ] **Step 5: Move Phase 3A/3B steps 2–4's rules into the agent,** and leave in their place one line each: the coding subagent follows them (Task 1).
- [ ] **Step 6: `review-fixer`'s dispatch** takes `model: <implementation_model>`. Correct its description in the agent file, the docs row and the map line: "Default model (not Opus)" becomes "the caller's `fixes_model`".
- [ ] **Step 7: Verify.** Run `check.py dispatch` (expected PASS), the gate chain (`EXIT=0`), and an end-to-end read of Phase 3A and Phase 3B. Every edit is a dispatch or a mechanical action, every return has an outcome, and every stop names `stash_ref`.
- [ ] **Step 8: Commit.** `feat(dev-workflows): /implement codes each plan step through code-writer, on the run class's model`

### Task 5: The MODERATE review, and the fix loop through `code-writer`

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 3A after step 5, Phase 3.5 steps 3 and 6, Invariants), `.claude/rules/dev-workflows.md` (the invariant "Opus review gate runs **before** tests for `SIGNIFICANT` / `HIGH-RISK` tasks")

**Interfaces:**
- Consumes: Task 4's dispatch pattern, with `mode: fix` and `failure_input`.

- [ ] **Step 1: Run `check.py <worktree> moderate`.** Expected: FAIL.
- [ ] **Step 2: In Phase 3A, after coding, add the MODERATE gate.**
  - **The sequence,** where the class is MODERATE: `test-writer`, then the diff capture, the Opus `code-review` dispatch, triage, `review-fixer`, and the second-verdict rules. These are Phase 3B steps 4a–7's text, cited rather than copied wherever the text is identical. Then Phase 3.5.
  - **SIMPLE** goes straight to Phase 3.5, as now.
  - **The new MODERATE review** comes before the tests. State that the invariant "never run tests before the review" now covers MODERATE in `/implement`.
- [ ] **Step 3: Rework Phase 3.5 step 6's fix loop.** Each of its two attempts is a `code-writer` dispatch with `mode: fix` and the verify report. It runs no test, and the orchestrator's verify after each attempt is the only run. Delete the phrase "The **session model** (not a subagent) applies fixes…".
- [ ] **Step 4: Phase 3.5 step 3.** A lint or build failure becomes a `mode: fix` dispatch with that output, and counts as one of the same two attempts.
- [ ] **Step 5: Update the `.claude/rules/dev-workflows.md` invariant** to say MODERATE too, for `/implement` only. Add the matching line to `dev-workflows-implement.md`.
- [ ] **Step 6: Verify.** Run `check.py moderate` and `check.py dispatch` (expected PASS), the gate chain (`EXIT=0`), and an end-to-end read of a MODERATE run and of a SIMPLE run.
- [ ] **Step 7: Commit.** `feat(dev-workflows): /implement reviews MODERATE work with Opus; the fix loop codes through code-writer`

### Task 6: Bug work — the repro and probes in the scratch checkout

**Files:**
- Modify: `plugins/dev-workflows/references/bug-diagnosis.md` (*Who runs the repro*, and *When a run may happen*), `plugins/dev-workflows/agents/risk-planner.md` (where it says the caller runs a plan's diagnosis steps)

- [ ] **Step 1: Run `check.py <worktree> bug`.** Expected: FAIL.
- [ ] **Step 2: Extend `bug-diagnosis.md`'s single rule.** `code-writer` gets `risk-planner`'s exception: once the edits have begun, it runs the repro, places and reads probes, and trims fixtures in the scratch checkout of `HEAD` the rule prescribes, and never on the working tree. It runs no lint, build or test at any class.
- [ ] **Step 3: Say who carries out each step in `risk-planner.md`.** A plan's diagnosis steps after the first edit are carried out by `code-writer` in that scratch checkout. A bisect step stays the orchestrator's (Task 4).
- [ ] **Step 4: Verify.** Run `check.py bug` (expected PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 5: Commit.** `feat(dev-workflows): code-writer runs a bug fix's repro and probes in the scratch checkout of HEAD`

### Task 7: Docs, tiers, versions and changelogs

**Files:**
- Modify:
  - `plugins/dev-workflows/docs/commands/implement.md`;
  - `plugins/dev-workflows/docs/workflow.md`, if its diagram shows who codes;
  - `.claude/rules/dev-workflows.md` (the `/implement` map line, which gains `code-writer` per step group and the MODERATE review, and the agent caller lines);
  - `.claude/rules/dev-workflows-implement.md`;
  - `.claude/rules/workflows-core.md` (the model-routing bullets, if they state §3.1 or §10's carve-outs);
  - `.claude/rules/plugin-updates.md` (a coupling line);
  - both `plugin.json` files and `.claude-plugin/marketplace.json` (4.29.0, 1.43.0);
  - `plugins/dev-workflows/CHANGELOG.md` and `plugins/workflows-core/CHANGELOG.md` (each `— Unreleased`).

- [ ] **Step 1: Run `check.py <worktree> tiers`.** Expected: FAIL on the versions, the changelogs and the coupling line.
- [ ] **Step 2: Rewrite the implement docs page** from `implement.md` as it now stands:
  - who writes the code, and on which model;
  - the run-state file;
  - the blocked question;
  - the MODERATE review.
- [ ] **Step 3: Update the rules files and the coupling line.** The coupling line: update `workflows-core` 1.43.0 with `dev-workflows` 4.29.0, because 4.29.0's `/implement` dispatches `code-writer` on §4's `implementation_model` and reviews MODERATE per §3.1's carve-out, and an older `workflows-core` says the opposite of both.
- [ ] **Step 4: Bump the versions, and write the changelog sections.** One bullet per behaviour change, each naming what the diff changed.
- [ ] **Step 5: Run the claim-expiry sweep** (refinements 1–8) for every claim this branch narrowed or widened: who codes in `/implement`, `review-fixer`'s model, the fix loop's model, MODERATE's review, and `implementation_model`'s meaning. Count each before and after.
- [ ] **Step 6: Verify.** Run `check.py all` (expected all PASS), then the gate chain (`EXIT=0`).
- [ ] **Step 7: Commit.** `docs(dev-workflows,workflows-core): code-writer, the run-state file and the MODERATE review in the docs and tiers (dev-workflows 4.29.0, workflows-core 1.43.0)`

### Task 8: Whole-branch review

- [ ] **Step 1: Dispatch the whole-branch review on Opus,** per the SDD skill, with the spec, the plan and the branch diff from `origin/main`. Fix every finding in one wave, then run one scoped re-review. Under the user's rule, minors are fixed too.
- [ ] **Step 2: Verify.** Run `check.py all` and the gate chain (`EXIT=0`).

### Task 9: Live verification on the bookstore demo (with the user)

Run by the controller with the user, as the security-workflows Task 12 was. Everything stays local: the code repository's push guard stays in `~/e2e-security.sh`'s copy of the launcher, or in a new launcher for this test.

- [ ] **Step 1: A keyed SIGNIFICANT run on an Opus session.** Use a small real Bookstore change the user chooses, on a local-only branch. Check four things:
  - the transcript shows a `code-writer` dispatch per step group, each with an explicit `model:` on the Opus chain;
  - the Opus review ran once over the whole change;
  - the main transcript's cache-read tokens, from `session-cost.py --transcript <main .jsonl>` with no `--subagents-dir`, are well below 36.6M;
  - the cost entry's total is at most $15.63 for comparable work.
- [ ] **Step 2: A MODERATE direct run on a Sonnet session** (`claude --model sonnet`). Check that the coding is on Opus, and that the Opus `code-review` gate ran before the tests.
- [ ] **Step 3: Record the findings.** Fix each through Task 8's loop. Then reset every demo branch, and remove the demo's bookkeeping, with the user's OK.

### Task 10: Merge and push (with the user)

- [ ] **Step 1: Re-check `origin/main`.** `git fetch`, and confirm `origin/main` is still the branch's base. Otherwise merge it in, and re-run `check.py all` and the gate chain.
- [ ] **Step 2: Date the two changelog sections** with the merge date.
- [ ] **Step 3: Delete the untracked review copies** of the spec and this plan in `/workspace/ai-workflows/docs/superpowers/`.
- [ ] **Step 4: Merge `--no-ff` into `main`** in the main checkout, which is on `main` and clean. Run the gate chain on the merged tree.
- [ ] **Step 5: Ask the user before `git push origin main`.** After the push, give the update commands: `claude plugin update workflows-core@shipwright` and `claude plugin update dev-workflows@shipwright`, then a restart.

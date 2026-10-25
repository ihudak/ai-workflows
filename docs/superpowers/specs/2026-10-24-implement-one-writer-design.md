# One writer per Epic: `/implement`, `/design` and `/epics` — design

**Date:** 2026-10-24 · **Plugins:** dev-workflows (`/implement`, `/design`, `code-writer`, `test-writer`, `code-review`, `design-reviewer`), product-workflows (`/epics`, `/specify`, `epic-writer`, `epic-reviewer`), workflows-core (`model-routing/classification`, `phase-handoff`, `next-phase-offer`) · **Status:** agreed in conversation; awaiting the user's review of this document

**Who decided what.**
- Everything marked **(Claude's call)** was decided by Claude, not the user, and is open to the user's correction. Everything else is the user's decision.
- A builder check (a fresh reader planning from this document) raised ten questions. §3 answers each, and those answers are Claude's calls.
- The user then asked Claude to criticise the design. Six changes came of that, and the user accepted them:
  - writers run one after another, never in parallel;
  - one writer by default;
  - `SIMPLE` stays on the session model;
  - reviewers do not see the test results;
  - a lock script serialises builds;
  - the proof measures cost per feature and repeats close runs.

## 1. Why

**The coding split costs quality and buys nothing.**
- Since dev-workflows 4.29.0, `/implement` hands the plan to a fresh `code-writer` for each *step group*: consecutive steps until the next would pass five files or ten steps (`implement.md` Phase 3A step 1).
- Groups run one after another on the same working tree, so the split gains no speed.
- Each new writer starts cold. It re-reads the code and rediscovers what the earlier writers decided.
- The 2026-10-17 live runs measured the effect (`docs/superpowers/verification/2026-10-17-implement-coding-subagents-rulings.md`, Rulings 43 and 60):
  - Run 1's 17 groups duplicated helpers: three cause-chain walkers and a snapshot helper across about 8 integration-test classes.
  - Route 3 made 5 writer calls for one coupled 3-file change.
- `code-writer` runs no build, lint or test, so it cannot catch its own compile error.
- A failure goes to a *new* writer in `mode: fix`, which is cold too.

**The context weight is in the orchestrator, not the coder.** `implement.md` is 326,520 bytes (`wc -c plugins/dev-workflows/commands/implement.md` at `0e02e28b`). Lean context D's record (`docs/superpowers/verification/2026-10-22-lean-context-handoff-part.md` §4) found that splitting the references by part has not clearly paid.

**The user's reading of the agentic-development guidance.** Splitting coupled coding across agents lowers quality and does not reliably save cost, because each agent re-reads the same files. Opus 5.5 is strong on long, complex tasks.

**The Epic size cap has outlived its reason.**
- What it is: `{criteria: 5, stories: 4}`, stated once in `epics.md` Phase 6 step 1.
- Why it was added: `docs/superpowers/specs/2026-10-12-epic-sizing-design.md` brought it in when `/implement` worked through every step in one session context. The point was to size each Epic so that one run could do it well.
- What it does: it cuts a coherent feature at its sixth acceptance criterion.
- What replaces it:
  - one writer, which can reach its own earlier context for every fix;
  - `/design`'s pieces, which focus the reviewers;
  - separate writers only where an Epic is genuinely too big for one.

  Together these remove the need to keep the Epic itself small.

**What the user values:** quality over cost, since poor quality costs more later.

## 2. Goals, non-goals, anti-goals

**Goals**
- An Epic's code is written by one code writer. It gets one writer per piece only where the Epic is too big for one writer to hold well and its pieces are loosely coupled.
- Tests are written by a separate test writer from the spec, never sharing the code writer's reasoning.
- Each writer sees its own build and tests and fixes its own mistakes.
- A fix goes back to the writer who wrote the file, reached again with its context intact.
- Review scales with the work: one reviewer per piece, plus an overall reviewer where there are pieces.
- Epics are cut by coupling, not by a count.
- A smaller `/implement` orchestrator.

**Non-goals**
- `/vuln` and `/upgrade`, with their own fixers. They are unchanged.
- The read-only fan-outs (`code-scanner`, the grounders), and the blind reviewers and verifiers of other commands. Unchanged.
- The Epic cut by repository and module. Unchanged.
- The reference loader and load-by-part machinery. Not revisited.
- Speed. Nothing is run in parallel to save time where that costs simplicity or safety.
- Porting to the internal Claude and Copilot editions. That comes later: `docs/superpowers/to-fix.md` E4 already says to port the code-writer `/implement` once this lands, rather than twice.

**Anti-goals (a failure even if it works)**
- A blind judge rating any result worse than today's on the same inputs.
- A second coding path to maintain. The user decided earlier that there is one implementer and no inline path for small Epics.
- Rebuilding the split this design undoes: several writers on an Epic one writer could do.
- Two builds or test runs at the same time.
- A code writer editing a test so that it passes.
- Losing any guarantee today's `/implement` gives:
  - the baseline captured before the first edit;
  - the test-writing requirement (`.claude/rules/dev-workflows-tests.md`);
  - the Opus review gate from `MODERATE` up, with SIMPLE still unreviewed;
  - triage before any fix (`workflows-core:finding-triage`);
  - the run-state file through `scripts/run-state.py`;
  - the commit before the run ends, and the secret scan;
  - `HIGH-RISK` keeping the full route.
- A loop that is not guaranteed to end.

## 3. The design

### 3.1 Part (a) — `/implement`

Everything up to and including Pre-Phase 3 is unchanged. That covers Phase 0 to Phase 2B, risk classification, `risk-planner`'s plan at `SIGNIFICANT` and `HIGH-RISK`, the branch, and the Phase 1.4 working-tree and branch rules. From the baseline on, in order:

**1. Baseline.** `test-baseliner` captures the baseline before any edit, as today.

**2. Pieces, writer units and the plan.**
- **Pieces.** They are read from `design.md`, in the section part (b) adds. With no such section, the whole plan is one piece. That covers a direct run, a bug fix, and a design that draws no pieces.
- **What a piece is for.** A piece is a review unit: each piece gets its own reviewer (point 5).
- **Writer units.** By default, one code writer and one test writer cover every piece of the Epic: the whole Epic is one *writer unit*. A piece becomes a writer unit of its own only where `design.md` says so, with its reason (part b).
- Every plan step belongs to one piece; the planner assigns it from the design's file lists **(Claude's call)**.
- A new file belongs to the piece whose step creates it.
- If a writer needs to edit a file that belongs to another writer unit, it returns that as a decision. The orchestrator moves the file into the writer's unit and records the move **(Claude's call)**. *(Corrected after the build: this line also offered merging the two units, which `/implement` never does.)*

**3. Who owns which file (Claude's call, extending the user's "the code writer never edits the test writer's tests").**
- **The test writer** owns every test file the run writes or changes:
  - the new tests;
  - on a bug run, the regression test and the repro written as a test;
  - an existing test whose asserted behaviour the spec changes.
- **The code writer** of a writer unit owns every other file in it.
- The code writer edits no test file at all.
- A fix, from a test run or a review, goes to the owner of the file it lands in.

**4. Each writer unit, one after another (usually just one).**
1. **The code writer codes the whole unit in one dispatch**; step groups are retired.
   - It runs the build and the nearby tests, meaning the existing tests near its change, and fixes what it broke before returning.
   - Suppose an existing test fails because the spec changes the behaviour that test asserts. The code writer reports the test and leaves it unedited.
2. **Then the test writer works**, once the code writer has returned. It never runs at the same time.
   - It writes tests from the requirements and the interfaces: the Epic spec's acceptance criteria and test cases, and the design's interfaces. With no spec, it uses the task and the plan **(Claude's call)**.
   - It reads the code only for signatures, never to learn what the code does.
   - On a bug run, its brief carries the diagnosis and the repro.
   - It gains a shell tool. It compiles and runs its own tests and fixes its own errors.
   - It updates the existing tests the code writer reported, where the spec says the behaviour changed.
3. **The unit's test run.** `test-baseliner` in verify mode runs every suite against the baseline.
   - On a bug run, the regression test's red-capability check runs here, on the scratch checkout of `HEAD`. It moves from after the review.
   - Failures go to the owner of the failing file: a test file to the test writer, source to the code writer.
   - Where a test and the code disagree, the orchestrator decides against the spec and the design. Where neither settles it, the user decides.
   - Each test run allows **at most 3 fix rounds**, whichever failures they address. After that, the run stops and asks the user **(Claude's call: per test run rather than per failure, so the loop is sure to end; today it makes two automated attempts)**.
4. **The next unit starts only once this unit's test run is green or settled by the user** **(Claude's call)**, so no writer builds on unverified code.

**5. Review**, from `MODERATE` up as today.
- One `code-review` per piece, run in parallel, since reviewers only read.
- Then one overall review, which gets the per-piece reports and checks what they cannot see: where the pieces meet, duplicated helpers, inconsistent conventions, and the shared contract.
- A one-piece run gets one review.
- **No reviewer is told the test results**, so a green run cannot soften a review.
- Triage is unchanged.
- **Who fixes a finding (Claude's call):**
  - a finding is fixed by the owner of the file its fix lands in;
  - a finding that spans writer units goes to the writer whose file keeps the fix, and the orchestrator chooses that writer.

  This replaces `review-fixer` inside `/implement`, following "fixes go back to the same writer". `review-fixer` stays for `/vuln` and `/upgrade`.
- **Re-review (Claude's call):**
  - The rules stay as today's `finding-triage` and `escalation-rules` state them, applied to each review.
  - A re-review re-runs each piece review whose piece got fixes, plus the overall review.
- **After the review's fixes,** the test run runs again with the same three-round cap. Where that run's fixes are non-trivial, the delta gets one more review, as today's Phase 3.5 fix delta does (`implement.md` Phase 3B step 8). A review that stays blocked there stops the run, as today.

**6. Reaching the same writer again.**
- A writer that has returned keeps its whole context, and the orchestrator can send it a further message: Claude Code's `SendMessage`, which resumes the agent from its transcript.
- This was checked on 2026-10-24 in the main session. A subagent that had finished half an hour earlier answered questions about its own earlier work from memory, with no file reads, in 14 seconds. Its context was re-sent, at about 240k tokens.
- Every fix goes this way.
- What the first task of part (a)'s plan proves in a real `/implement` run:
  - that the command can use `SendMessage` (its `allowed-tools`);
  - that it still works after the orchestrator's own context has been compacted;
  - what a resume costs once the prompt cache has expired.
- Where a resume fails, a fresh dispatch of the same kind of writer carries the earlier report and the diff so far.

**7. When a unit is too big for one writer (Claude's call).**
- No size cap applies.
- If a writer runs out of room before it finishes, it returns what it has done. A continuation dispatch then carries its report and the diff so far.
- This is one continuation path, not a planning fallback. The big test Epic (§3.4) measures whether it is ever needed.

**8. The orchestrator** does bookkeeping and handoff only: the run-state file, the branch, the dispatches, triage, the implementation record, `finish-code-branch`, follow-ups, cost and the resume pointer. `implement.md` shrinks.

**Models.** No change from today:
- `SIMPLE` codes on `current_model`;
- from `MODERATE` up it codes on Opus (`workflows-core:model-routing/classification` §4's coding-model rule);
- `--enforce-model` overrides every dispatch (§10).

The test writer follows the same rule as the code writer **(Claude's call)**. Keeping `SIMPLE` on the session model is the user's decision: `SIMPLE` is the one class nobody reviews, so it is the worst place for a weaker model.

**No two builds or test runs at once, made certain by a lock.**
- Writers run one after another, and reviewers only read, so by design nothing overlaps.
- As a guarantee rather than an instruction, every build or test command an agent runs goes through a small lock script, as `scripts/bounded.py` already wraps a command to cap its time. A second caller waits until the first is done.
- The orchestrator decides who runs. The agents never coordinate with each other: they cannot.

**Order, as agreed:** the code is written, then the tests, then everything is run, then the review, then fixes and a test run again. This reverses today's *review before tests* (§5).

### 3.2 Part (b) — `/specify` and `/design` per Epic

- **Both are mandatory before `/implement` builds an Epic.** `/implement` stops on an Epic whose folder lacks `specification.md` or `design.md` on the specs repository's default branch, and names the command to run. Today both are optional, and `/implement` gates only the ones present.
  - The gate applies to a keyed run that builds the unit's own change. That includes an Epic cut before this change that has not been built yet **(Claude's call)**.
  - It does not apply to follow-up runs, which fix or complete work already built: a `/security-workflows:scan` fix, a `/conformance` "fix the code" follow-up, a companion run, and a tasks-only run **(Claude's call)**.
  - A PRD implemented whole, the one case where the PRD is the unit, gets the same gate **(Claude's call)**.
  - Direct runs, with no key, are exempt.
- **`/design` draws the pieces and writes them into `design.md`.** For each piece it records:
  - its files;
  - the contract between the pieces, fixed before any code is written, including the interfaces the test writer writes against;
  - the order the pieces are built in.

  A piece is drawn only where the file sets do not overlap and the design fixes the shared part. Otherwise there is one piece. Pieces focus the reviewers.
- **Separate writers are the exception.** `/design` marks pieces as separate writer units only where the Epic is too big for one writer to hold well, and writes down why. Without that mark, one writer covers every piece. `design-reviewer` checks both the pieces and any separate-writer mark, against that reason.
- **There are two kinds of split finding.**
  - *"This is two Epics"*: each part could ship as its own pull request, sharing no files and no data model. `/design`, and the Epic-level `/specify`, stop and send the work back to `/epics`. This widens `/design`'s existing *Re-split* exit (`design.md` Phase 2, near its `Re-split — /product-workflows:epics <EPIC>` option), which today fires only when a design adds a component.
  - *"This is two pieces of one pull request"*: recorded in `design.md`.

### 3.3 Part (c) — `/epics`

- **The PRD-level `/specify` is mandatory before `/epics`.** Today `/epics` Phase 2.6 folds the PRD-level spec in only if it exists.
  - This holds for every `/epics` run that writes Epics, including a re-split that `/design` sends back.
  - An older PRD with no PRD-level spec therefore needs `/specify` first **(Claude's call)**.
- **The cut.** Components come first, as today: one Epic per repository or module. Within a component, an Epic is split only where the parts share no files or data model and each could ship as its own pull request.
- **`size_limit` becomes a warning.** It is still counted and reported, but never forces a split or asks a question. That retires the 2026-10-12 design's D5 question, and its D6 *Epic size* MAJOR becomes a note.
- **The bundling rule stays (Claude's call).** A criterion or story that bundles several independently testable behaviours is still a MAJOR whatever the count, because that is about testability, not size.
- **No migration.** Existing Epics stay as cut. The new rules apply from the next run.
- **No light path for a tiny Epic (the user's decision).** It still gets `/specify` and `/design`, because a second route is one more to maintain and Epics get bigger and fewer under the new cut.

### 3.4 Build order and proof

- **One design, three plans, three releases, three A/Bs**, in the order (a), (b), (c) **(one design for all three is Claude's call)**.
  - (a) works without pieces, and is the largest gain.
  - (a) defines the pieces section's format and reads it; (b) teaches `/design` to write it.
  - Until (b) ships, `/implement` gates the spec and design only where present, as today.
- **Quality bar, as for lean context parts 1 and D:**
  - a blind judge compares live runs on the same inputs;
  - Claude reads the old and new instructions rule by rule;
  - cost is measured;
  - a worse result is a defect, and a better one is recorded where a user would see it;
  - where a result looks worse, a run on today's `main` with the same inputs tells which change caused it.

  The runs use the `ihudak-e2e` copies.
- **Repeat a close run (the user's decision).** Where a blind verdict's margin is small, the run is repeated before the verdict is believed. In D, two verdicts flipped on a repeat.
- **The runs:**
  - **(a):**
    - `/implement` route 3 (baseline `beebc3f3`);
    - run B, the direct MODERATE run (baseline `5023b937`), with no spec, so the test writer works from the task and the plan;
    - a big test-only Epic, built in the e2e bookstore copy, with at least two loosely coupled pieces and big enough to earn separate writers. The user allowed this. Its `design.md`'s pieces section is written by hand in (a)'s format, since (b) is not built yet.
  - **(b):**
    - `/design` on that test Epic;
    - `/design BOOK-1-01` (baseline `c78ffdb`);
    - a small Epic with two loosely coupled parts, where `/design` should draw pieces for review but keep one writer.
  - **(c):** one `/epics` run on a PRD. Its cost is compared **per feature** (the whole PRD's `/specify`, `/design` and `/implement` runs) rather than per Epic, since the new cut makes fewer, bigger Epics, each with its own `/specify` and `/design` (the user's decision).

## 4. What stays as it is

- `test-baseliner`, as the baseline and the test run.
- `risk-planner` at `SIGNIFICANT` and `HIGH-RISK`.
- The coding model of every class.
- The scratch-checkout rule for a bug run's repro and probes: they run on the tree before the change (`dev-workflows:bug-diagnosis`).
- `finding-triage` and its patch gate.
- `finish-code-branch` and the secret scan.
- The run-state file and `run-state.py`.
- The implementation record and commit convention.
- `/conformance`, `/ready`'s verdict logic, and the read-only fan-outs.

## 5. What this reverses: change every copy

Each of these is a live rule today. The builder finds every statement of it, by subject as well as by phrase (`.claude/rules/claim-sweep.md`), and rewrites each one to what the new design does.

- **Nothing runs against the working tree from the first edit until the review.** This rule appears in four places:
  - `dev-workflows:bug-diagnosis` (*From the first edit until a non-BLOCK review, nothing runs against the working tree*, and *it is unreviewed change*);
  - `model-routing/classification` §3.1 (*That review completes before `/implement` runs any test against the working tree*) and §3.2;
  - `.claude/rules/dev-workflows-implement.md`;
  - `.claude/rules/dev-workflows.md` (*Opus review gate runs before tests*).

  Its only recorded reason is the phrase "unreviewed change". `docs/maintainers/rationale.md` has no section on it, and the rule's first commit (`7c1e7961d`, 2026-05-15, subject "bugfix") gives none. The user decided that the writers run their builds and tests, and that the test run comes before the review.

  What survives:
  - the bug run's repro and probes on the scratch checkout of `HEAD`, which the code writer never runs against the changed tree;
  - the red-capability check on that scratch checkout, now made at the unit's test run.
- **`code-writer` runs no lint, build, type-check or test, at any class.** This is in `agents/code-writer.md`, `references/handoff/code-writer.md` and the rules above. The code writer now runs the build and the nearby tests, through the lock. In a fix round it may also run the failing tests it is fixing.
- **`code-writer` writes a bug run's regression test** (`bug-diagnosis` step 4, *land the fix and its regression test*), along with test-first steps and the repro written as a test. All of these become the test writer's (§3.1 point 3).
- **Step groups** (five files, ten steps), and run-state `step_groups`. Both are retired; there is one dispatch per writer unit.
- **The fix loop's two automated attempts.** This becomes at most 3 rounds per test run, each fix sent back to the owner of the failing file, reached again with `SendMessage`.
- **`test-writer` writing from the diff, with no shell.** This is in `agents/test-writer.md` (its tools and hard rules), its handoff file and `.claude/rules/dev-workflows-tests.md`. It now:
  - writes from the spec and the design's interfaces, after the code writer;
  - gains a shell to compile and run its own tests, through the lock;
  - owns every test file.

  The test-writing requirement's substance is unchanged: at least one test per new or changed behaviour, no silent completion on a failing test, and every untested or failing test named.
- **`review-fixer` in `/implement`.** Its role there moves to the owner of each file (§3.1 point 5). Its rules in `.claude/rules/dev-workflows-implement.md` and `finding-triage` are rewritten for `/implement` only.
- **`code-review` seeing the test results**, wherever its brief carries them today. It no longer does.
- **The Epic spec and design are optional for `/implement`, and the PRD-level spec is optional for `/epics`.** Both become prerequisites, with the follow-up exemptions of §3.2. This changes these places:
  - `workflows-core:phase-handoff` §3.4, whose row-F list names the consumers that stop on an absent input instead of delegating;
  - the matching lists in `.claude/rules/workflows-core-git.md`;
  - `CLAUDE.md`'s *an absent optional input … never becomes a prerequisite*. It stays true, since these inputs are no longer optional, but its context changes;
  - `next-phase-offer`'s lanes;
  - `/ready`'s derivation of a unit's phase;
  - every `docs/` page that calls `/specify` or `/design` optional.
- **`/epics`' size question and the reviewer's *Epic size* MAJOR.** These are in `epics.md` (Phase 6 step 4, the final count before the handoff, and the plan's sizing bullet), `epic-writer.md` (*Sizing / sequencing*, `kept_whole`), `epic-reviewer.md` and their docs pages. All become the warning in §3.3.
- **`implement.md`'s *Decompose* fallback, tied to step lists.** It gives way to §3.1 point 7's continuation path.

## 6. Constraints

- `CLAUDE.md` § Editing discipline and § Hard constraints bind every edit. In particular:
  - prose is executed;
  - the claim-expiry sweep;
  - one source of truth per authority, with `model-routing/classification` the authority on models;
  - `choices:` arrays of two to four options, presented verbatim, with the **Load the question rules.** step;
  - the docs tree for every changed command, agent and reference;
  - a dated `CHANGELOG.md` section for each release;
  - the 1024-character plugin descriptions.
- The gate chain in `.github/workflows/validate-catalog.yml` passes before each push.
- **The lock script.** Like `bounded.py`, it is called by its path. Every plugin whose agents run builds ships its own copy, since `${CLAUDE_PLUGIN_ROOT}` is the calling plugin's own. CI holds the copies equal, as it does for `bounded.py` (`.claude/rules/workflows-core-bounded-run.md`). It must work on macOS and Linux.
- `.claude/rules/plugin-updates.md` gets a coupling bullet for each pair of versions that must be updated together.
- Work happens in a worktree, never by `git checkout` in the shared checkout.
- The verification record is written last.
- The rulings and ledger are preserved under `docs/superpowers/verification/` before the workspace goes.

## 7. Left to the builder

- The pieces section's name and format in `dev-workflows:design-format`, including the separate-writer mark and its reason.
- What "nearby tests" means for each stack, for example the changed module's suite, or the tests that import a changed file.
- The lock script's name, its lock file's location (per worktree, inside the git directory, as the run-state file is), and how a stale lock left by a killed agent is cleared.
- The overall reviewer's brief, which may use the same `code-review` agent.
- The run-state keys, including each writer's agent id for `SendMessage`.
- How `implement.md` is restructured. Measure it before and after; the rule-by-rule reading proves no rule was lost.
- Whether `risk-planner`'s plan changes now that `/design` is mandatory, beyond assigning each step to a piece. The default is that it does not.
- Versions, changelogs, coupling bullets and docs pages.

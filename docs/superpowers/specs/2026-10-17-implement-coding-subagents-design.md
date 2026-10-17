# `/implement` writes its code through coding subagents

Sub-project **F**, part 1, of the plan in `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` (its sub-project table). That table describes F as a model router. This design narrows it and reshapes it, on the user's decisions of 2026-10-17. Part 2, Fable escalation, is deferred (see *Non-goals*).

## Why

`/dev-workflows:implement` writes the code itself, in the user's session. Its subagents only plan (`risk-planner`, Opus), write tests (`test-writer`), review (`code-review`, Opus) and apply review fixes (`review-fixer`). That has two costs.

1. **The session carries everything.** Every file read, edit, diff and test output of the coding lands in the orchestrator's context. A long run compacts, sometimes more than once. Each later turn then re-reads a huge context: the end-to-end test's route 3, a three-file security fix, ran 64 minutes and cost $15.63, $14.24 of it Opus, with 36.6M cache-read tokens — the context re-read turn after turn (its cost entry, `bookstore-specs/…/PRD-BOOK-2-01-verified-ratings/dev-workflows/cost/d2f5de25.md`). Compaction also drops detail. The orchestrator holds the run's state in its head: the branch answer, `stash_ref`, `pre_existing_dirty` with its fingerprints, the triage rulings, the patches applied. A compaction can lose exactly the facts Phase 4.6 needs to keep the user's own uncommitted work out of the commit.
2. **The code's quality follows whatever model the user started the CLI with.** The docs tell the user to run on Opus or better, but nothing enforces it. On a Sonnet session the code is written by Sonnet. Two of today's fix paths run below Opus even on SIGNIFICANT work:
   - **`review-fixer`** applies the Opus review's BLOCKER and MAJOR findings on `fixes_model`, which is the §2.1 Sonnet chain (`implement.md` ~:760, `classification.md` ~:369).
   - **The Phase 3.5 fix loop** has "the session model (not a subagent)" apply fixes for failing tests (`implement.md` ~:690).

**The user's priority is quality and avoiding risk, not cost:** "a low-quality risky project will eventually cost much more than Opus implementing the code."

## What it is

The orchestrator stops writing code. For each step of the approved plan, it dispatches a **coding subagent**, a new agent in `dev-workflows`, on a model chosen by the task's class. The subagent writes that step's code and returns a short report. The orchestrator keeps its run state in a **run-state file** and re-reads it at the start of every phase, so a compaction loses nothing it needs.

### Decided by the user

- Quality and avoiding risk come before cost.
- **No single Epic-finishing command.** `/implement`, `/conformance` and `/security-workflows:scan` stay three typed commands, with context hygiene between them. A single command would gain nothing:
  - Claude Security must run in the main session; its agent says it "cannot scan from" a subagent;
  - conformance's walk, the scan's triage and the push consent all ask the user;
  - the commands' next-step offers already chain them.
- **One coding subagent per plan step,** so that no subagent runs long enough to compact.
- **The run's state lives in a file** that the orchestrator re-reads after a compaction. The re-read trigger is defined below.
- The design was played back to the user and confirmed: "looks right".

### Proposed and accepted without objection

- **The model rule** (below): Opus for MODERATE and above; SIMPLE work on the session's own model.
- **Fable escalation is deferred.**

## Goals

1. **Coding leaves the orchestrator.** Each step of an approved plan is coded by a coding subagent, in Phase 3A (SIMPLE/MODERATE) and Phase 3B (SIGNIFICANT/HIGH-RISK) alike. The orchestrator itself makes no source edit, save the mechanical ones listed under *What the orchestrator keeps*.
2. **Every code-writing dispatch carries an explicit model, by one rule** (*The model rule*). That covers the coding subagent, `review-fixer`, and the Phase 3.5 fix loop, which moves to the coding subagent.
3. **The run survives compaction.** All state Phase 4.6 and the report need is in the run-state file. The orchestrator re-reads it at the start of each phase and never relies on its memory for it.
4. **Behaviour stays the same everywhere else.** The phases, the questions, the gates, the review, the tests, the commit, the follow-ups and the report keep the same outcome. Only who writes the code, and on which model, changes.

## Non-goals

- **No single Epic-finishing command.** See *Decided by the user*.
- **No Fable escalation (part 2 of F).** Deferred. No run so far has shown Opus falling short, and an ask before every high-risk run adds friction for an unmeasured gain. A Fable *session* still gets Fable code, by the model rule's "never below the session" clause.
- **No change to `test-writer`, `code-review`, `risk-planner`, `test-baseliner` or the maintenance agents.** Their models and briefs stay as they are, save where the run-state file changes what they are handed.
- **No per-step review.** The Opus `code-review` gate still judges the whole change once, as now. SIMPLE and MODERATE runs still have no Opus review gate, by design.
- **No resuming of a crashed or abandoned run** from the run-state file. The file is read only inside the run that wrote it. Using it to resume is a possible later feature, and is out of scope.
- **No change to `/vuln` or `/upgrade`.** Their fixers already code in subagents.
- **No parallel coding.** Steps are coded one after another, because they edit one working tree.

## Anti-goals (a failure even if it works)

- Code written by a weaker model than the user ran the session with. The rule never goes below the session model.
- A coding subagent that guesses a decision the user would notice, or asks the user itself. It returns instead, and the orchestrator asks.
- A coding subagent that runs a test or a probe against the working tree on SIGNIFICANT/HIGH-RISK work before the review gate clears. The existing invariant and `bug-diagnosis`' single rule are preserved.
- A coding subagent that commits, switches branches, stashes, resets, rebases, pushes or opens a pull request. Git writes stay the orchestrator's, through `code-handoff`.
- State lost to a compaction: a stash not named, a dirty file swept into the commit, a branch answer forgotten.
- A slower or costlier run that is no better. A run cut into dozens of tiny dispatches that each re-read the same files is that failure; see *Steps and dispatches*.

## The model rule

The coding model is the higher of the class floor and the session model:

| Class | Class floor | Coding model |
|---|---|---|
| SIMPLE | none | the session model |
| MODERATE, SIGNIFICANT, HIGH-RISK | the §2 Opus chain | the session model where it is Opus-tier or stronger (Fable stays Fable), else the §2 Opus chain's first available row |

- **`--enforce-model` (§10) overrides it,** as it overrides every dispatched step. The coding subagent and `review-fixer` are dispatched steps.
- **Recording.** `model_routing.implementation_model` stops describing inline coding and names the coding subagent's dispatched model. §10's carve-out for "inline coding" no longer applies to `/implement`, so `classification.md` §4 and §10 say so. `fixes_model` becomes equal to `implementation_model` for `/implement`'s `review-fixer`, which follows the rule.
- **A re-classification mid-run** (Phase 3A step 5's raise to SIGNIFICANT) re-resolves the coding model for every later dispatch. Steps already coded stay as they are.
- **Reasons.** MODERATE gets Opus because a MODERATE run has no Opus review gate, so nothing Opus-level would otherwise ever read that code. Every keyed Epic run is floored at SIGNIFICANT by §8.1, so MODERATE arises only on direct runs, and the cost of the floor is small.

## What the orchestrator keeps

Everything that talks to the user, decides, or writes git state:
- Phases 0–2;
- the plan approval;
- Phase 1.4's branch question and its switches;
- the clean-tree check and the stash;
- Pre-Phase 3's branch cut;
- the baseline;
- dispatching each coding subagent and reading its report;
- every question to the user;
- the re-classification and re-plan;
- `test-writer`, the review gate and triage;
- `review-fixer`'s dispatch;
- Phase 3.5's sequence;
- Phase 4 maintenance;
- Phase 4.6's commit and handoff;
- the report.

It keeps a few **mechanical working-tree actions**, because each one is a git operation or a gate the run owns, not authored code:
- applying a scan's patch with `git apply`, in Phase 3A/3B step 1;
- a plan's bisect step, which moves `HEAD`;
- stripping `[DEBUG-xxxx]` probes before the review diff;
- capturing diffs.

## The coding subagent

**Where it is dispatched**
- Phase 3A step 1 and Phase 3B step 1, one dispatch per step group (*Steps and dispatches*).
- In Phase 3.5's fix loop, one dispatch per fix attempt (still capped at two), handed the `test-baseliner` verify report. The dispatch fixes from that report and runs no test itself; the orchestrator's `test-baseliner` verify after each attempt stays the only run, as now. A lint or build failure at Phase 3.5 step 3, which the session model fixes inline today, is a dispatch too, handed that output, and counts as one of the same two attempts. *(My call.)*

**What it receives,** through a handoff file in the family's convention, as `doc-writer` and `epic-writer` do:
- `plan_file` and which steps it codes;
- the in-scope `specification.md`, `design.md` and ARD paths;
- `summary_file`;
- the repository's top level;
- the `model_routing` block, to the extent its handoff declares it;
- the patches already applied or refused for its steps;
- the reports of earlier step groups, by path;
- what earlier steps changed, as a diff file.

It reads the code it needs itself.

**What it may do**
- Read, search, and edit or create files in the branched repository only.
- Run read-only commands: `git grep`, `git log`, `git show` and the like.
- Delete a file the step removes.
- On `task_shape: bug` work, run the repro, place and read `[DEBUG-xxxx]` probes, and trim fixtures **only in the scratch checkout of `HEAD`** that `bug-diagnosis.md`'s single rule prescribes once the edits have begun — the exception `risk-planner` already has, never the working tree. The scratch checkout holds the pre-change tree, so this runs no unreviewed code. *(My call: it keeps the probe output out of the orchestrator's context, and step groups need not split at every probe step.)*

**What it may never do**
- Run a lint, a build, a type-check or a test, at any class: those stay where they run today — Phase 3.5 step 3 onward on SIMPLE/MODERATE, Phase 3B step 8 after the review on SIGNIFICANT/HIGH-RISK — so a generated file never lands in the review diff or `code-handoff`'s staging. *(My call.)*
- Run the repro or a probe against the working tree. `bug-diagnosis.md`'s single rule binds it as it binds `risk-planner`.
- Write git state (commit, switch, stash, reset, rebase, push).
- Touch another repository or `$SPECS_PATH`.
- Dispatch a subagent.
- Ask the user.

It carries `workflows-core`'s untrusted-content block (check 20).

**What it returns:** a report file, plus one status line.
- **`done`** — the step group is coded. The report lists the files changed, each open question it settled itself with what it chose (these become `### Assumptions & limitations`), and anything out of scope it found (another repository's need, for Phase 3A/3B step 2's follow-up rule).
- **`needs_decision`** — Phase 3A step 5's *decision*: nothing the run can read settles it, and its answer changes what the user would notice. The report gives the question, the options and what is already coded. The orchestrator asks, with 2–4 choices, then dispatches a fresh subagent for the rest of that step group with the answer. Agent continuation is not available in every harness, so a fresh dispatch is the one mechanism.
- **`trigger`** — Phase 3A step 5's *§1.1 trigger the approved plan did not state*, with the paths that show it. The orchestrator stops dispatching and runs the existing raise: the partial diff, the task-shape question where ambiguous, and `risk-planner`'s re-plan. It then continues on the new plan, under the new class's model.
- **`blocked`** — the step cannot be coded as planned (a file the plan names is not there, say). Today no path handles a plan defect: the session model looks it up and carries on. So the orchestrator puts it to the user, naming what blocked and what is already coded: `choices: ["Revise the plan (you'll be prompted)", "Stop here — the work so far is committed through Phase 4.6"]`. *Revise* re-plans at the same class — Phase 2A's *Revise* on SIMPLE/MODERATE, `risk-planner`'s re-plan with its approval gate on SIGNIFICANT/HIGH-RISK, its `Work so far:` naming the partial diff — and it spends the run's one re-plan, so a later `trigger` meets the existing *after the re-plan* arm. Once that re-plan is spent, `blocked` stops through Phase 4.6 with `clean_finish: false`: the approved plan was not completed. *Stop* is in Phase 4.6's "Every run" list. *(My call: a plan defect is a decision the user would notice, so it is asked, never guessed past.)*
- **A dispatch that fails outright,** or returns no readable status or report, is retried once with the same brief. A second failure is treated as `blocked`. *(My call.)*

## Steps and dispatches

- **The unit is a plan step**, as written in the plan's `Steps` list.
- **Grouping.** The orchestrator may group consecutive steps into one dispatch where they touch the same files and together stay small. A plan of ten one-line edits to one file is one dispatch, not ten.
- **No group so large that it would compact.** The exact bound is the builder's (see below), with this intent: no dispatch so large that the subagent compacts, and no dispatch so small that its own setup dominates.
- **Order.** Groups run in plan order, one at a time.

## The run-state file

- **Location.** `$(git rev-parse --git-path dev-workflows/implement-run.json)` in the code repository: a per-worktree path inside the git directory. It can always be found from the working directory alone, whatever the orchestrator remembers, and it is never staged.
- **Lifetime.**
  - Created at Phase 1.4, the first point that makes state worth keeping. A file a previous run left there is moved aside, never read.
  - Written at every change to what it holds.
  - Removed at the run's end, on every exit Phase 4.6 or a stop reaches.
- **What it holds,** at least:
  - the class, and the coding model;
  - Phase 1.4's answer and the branch;
  - `stash_ref`;
  - `pre_existing_dirty` with its fingerprints;
  - `test_decision` and `clean_finish`;
  - `plan_file`, `summary_file`, `review_diff_file` and the other temp-file paths;
  - each step group's status and report path;
  - the patches applied or refused;
  - the triage rulings;
  - the assumptions recorded so far;
  - the phase reached.
- **The re-read trigger.** At the start of every phase, the orchestrator reads the file before anything else. The trigger is the phase heading, which is observable, so the orchestrator never has to judge whether it compacted. It treats the file, not its memory, as the run's state.

## Constraints

- **The repository's hard rules (`CLAUDE.md`):**
  - `choices:` arrays 2–4 and verbatim;
  - vendor neutrality;
  - the docs tree for a new agent (check 4, the agent inventory, docs pages, and `CLAUDE.md`'s agent count for `dev-workflows`);
  - the untrusted-content guard (check 20);
  - `--enforce-model` per §10;
  - "prose is executed".
- **`implement.md`'s invariants stay true:**
  - the test baseline before any edit;
  - no tests before the Opus review on SIGNIFICANT/HIGH-RISK work;
  - Phase 4.6 after Phase 4;
  - changes only in the branched repository;
  - the test-writing requirement.
- **`classification.md` §5's dispatch form** (an id where the harness takes ids, a family name where it takes only families) governs every new `model:`.
- **Plugin-update coupling.** If `workflows-core`'s `classification.md` changes, `dev-workflows` and `workflows-core` ship together. `plugin-updates.md` gains the coupling line.

## Success

- **Measured on a live run.** On the bookstore demo, a run comparable to route 3 — a small keyed fix, SIGNIFICANT, on an Opus session — shows:
  - the orchestrator's **own** transcript with materially fewer cache-read tokens than route 3's whole run, 36.6M. A cost entry adds the main session and every subagent together by model, so the coding subagents land in the same Opus row; measure the main transcript alone with `session-cost.py --transcript <the session's .jsonl>` and no `--subagents-dir`, and read the entry for the total;
  - the entry's total no higher than route 3's $15.63 for comparable work: on an Opus session the code is written on the same model as before, so a costlier run there is the anti-goal *a costlier run that is no better*. *(My call.)* On a Sonnet session the total may rise, because the coding moves up to Opus, and that is the intended trade;
  - no compaction during the run;
  - every coding and fix dispatch with an explicit `model:`.
- **A Sonnet session's run** shows the coding subagent on Opus for MODERATE and above.
- **The commit, the follow-ups and the report** are as they would have been.

## Left to the builder

- **Names:** the agent's name, and its handoff file's layout.
- **The exact bound on a step group:** a measure such as files touched or plan lines, with the intent above.
- **The run-state file's schema,** and how a leftover from a previous run is moved aside.
- **Wording** throughout, and how `implement.md`'s phases are restructured to dispatch rather than edit, keeping every existing outcome.
- **Whether the Phase 3.5 fix loop's dispatch reuses the step brief or has its own.**
- **The docs, rules and changelog sweep** this implies: `dev-workflows`' agent count, the `/implement` map line, `dev-workflows-implement.md`'s invariants, the implement docs page, `classification.md` §4 and §10, and `plugin-updates.md`.
- **Verification beyond the live runs,** such as a scripted check that every dispatch in `implement.md` names a model.

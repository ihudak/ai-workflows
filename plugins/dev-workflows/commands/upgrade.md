---
name: upgrade
description: Component upgrade workflow. Upgrades libraries, frameworks, runtimes, or build tools to specified or latest versions. Plans with Opus for complex upgrades, runs code review, and verifies with tests.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Upgrade components: $ARGUMENTS

Usage: `/upgrade <component[:exact|:minor|:latest|:lts]> [<component…>] [--no-commit] [--skip-feedback] [--enforce-model=<model>]`

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves.

**Strip `--no-commit` next**, before parsing any component token: an unstripped flag is read as a component name and the run fails resolving it. When present, steps 6.5 and 7.5 are both skipped and the changes are left in the working tree. It is the one opt-out from a commit that is otherwise prompt-free (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §1 rule 5) — typed rather than clicked, which is the difference — and a run under it says once what it costs: the work is recoverable only on this machine.

Each token is one of: `component:1.2.3` (exact), `component:minor` (latest patch on current minor), `component:latest` (latest stable), `component:lts` (latest LTS), or bare `component` (latest compatible with everything else).

`component` can be a library, framework, language runtime, build tool, or path like `.github/workflows`.

Each component is committed on its own as soon as its gates pass — see Phase 2's step 6.5 and step 7.5 (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md`); the branch is pushed once for the batch where §2.4's consent choice, an `origin` and §2.5's push itself all allowed it, and a pull request opened where **§2.4's consent choice**, §2.8's base-branch ladder and §2.6's `gh` capability probe allowed one as well — §3.1's rows rather than any list written out here are the authority on which line the run emitted. **§2.4 is named in both halves rather than carried forward from the first**, because its second option (*"Push the branch only — no pull request"*) allows the push and refuses the pull request: a clause that let the push's own §2.4 term stand for the pull request's would assert one in a state §3.1 has its own row for. The commit is prompt-free; only the push and the pull request sit behind a consent choice, asked once for the batch. `--no-commit` skips both steps.

---

## Phase 0 — Specs-repo preflight

Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier run, retry an artifact commit that failed to push, and settle the branch. This runs against `$SPECS_PATH` only — `git -C "$SPECS_PATH"`, never a `cd`, so the code repo this run is about to upgrade is untouched (§1 rule 1). Prompt-free and silent when the specs repo is clean and on its default branch. If a guard fires, emit its §5 notice; if it returns `specs_git: blocked` (§3.3 G0), carry that flag for the whole run — the terminal `commit-artifacts` step skips on it.

---

## Phase 1 — Compatibility Planning (no files changed)

1. **Inventory** — Detect all components and their current versions from build files, runtime version files, and CI YAML. Use `${CLAUDE_PLUGIN_ROOT}/references/upgrade/ecosystems.md`.

2. **Resolve requested targets** — Apply the `Version Resolution` section below to each requested token.

3. **Delegate planning in parallel** — Spawn one planner task per requested component. Use a single agent message for the whole batch. Per-component classification does not happen until step 5 (`upgrade-planner.md` says so in its own words), so the `model_routing` block this dispatch carries is **provisional**: start at `MODERATE`, the rung `/vuln` Step 0 takes for the same reason, and let step 5's classification be the run's.

   Use this pattern for each component:

   ```
   task(
     subagent_type: "dev-workflows:upgrade-planner",
     model: `<detection_model — §2.1 Sonnet chain>`,
     description: "Plan component upgrade",
     prompt: "## Upgrade Plan Request
     repo: [absolute repo path]
     component: [component name]
     target: [exact | minor | latest | lts | bare]
     other_upgrades:
       - name: [other requested component]
         target: [its target token]
     repo_inventory:
       [component]: [current version]
     model_routing:
       classification: [SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK]
       reason: <one-line>
       current_model: <the model this orchestrator is running under>
       enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every *_model below equals it and routing: bypassed
       detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # upgrade-planner, test-baseliner; upgrade-executor (SIMPLE/MODERATE); review-fixer
       planning_model: <§2 Opus chain>   # risk-planner (SIGNIFICANT/HIGH-RISK; frontmatter-pinned, recorded, no override unless §10 enforces a model); upgrade-executor escalates here only if HIGH-RISK
       review_model:  <§2 Opus chain>    # code-review (frontmatter-pinned; recorded, no override unless §10 enforces a model)
       opus_available: <true if a §2 Opus model resolved, else false>
       gate_tests_on_review: <true for SIGNIFICANT/HIGH-RISK, false otherwise>
       notes: <any §2 / §2.1 fallback or degradation>"
   )
   ```

4. **Collect planner results**
   - `READY` → candidate for execution
   - `NOT_FOUND` → warn and skip
   - `CONFLICT` → surface `conflict_details` and ranked `alternatives`; do not proceed until the conflict is resolved or the component is skipped

   For each `READY` component, write its planner handoff to a temp file (`command mktemp -t dw-upgrade-plan-XXXXXX`, never inside a repo tree) and record its absolute path as the component's `plan_file` (it persists into Phase 2); the risk-planner, executor, and resume steps below receive this path instead of the pasted handoff.

5. **Classify each READY component** — Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`) to load the classification rules, then apply them using the actual resolved change, related upgrades, and planner findings. Print one classification line per component. When in doubt, escalate to `SIGNIFICANT`.

6. **Risk plan for SIGNIFICANT / HIGH-RISK components** — For every component classified `SIGNIFICANT` or `HIGH-RISK`, invoke `risk-planner` before execution (frontmatter-pinned to Opus; recorded as `planning_model` above, no `model:` override needed unless §10 enforces a model):

   ```
   task(
     subagent_type: "dev-workflows:risk-planner",
     model: `<planning_model — §2 Opus chain, equal to risk-planner's frontmatter pin; under §10, run_flags.enforced_model>`,
     description: "Plan risky upgrade",
     prompt: "Task description: Upgrade [component] from [current] to [target] in this repo.
     Classification: [SIGNIFICANT | HIGH-RISK] — reason: [routing trigger]
     Upgrade plan: read it from the file at [`plan_file`]
     Current state: branch = [git branch], uncommitted = [git status --short summary]

     Before writing the plan, grep the repo for import sites and usage patterns of this component to understand blast radius, migration order, test coverage, and rollback."
   )
   ```

   If the planner returns `### Re-classification`, surface it and let the user accept the down-classification, override it, or cancel the component.

7. **Confirm the full plan** — Present the resolved component list, classifications, related upgrades, and any Opus plans. Do not touch files until approved.

---

## Phase 2 — Execution (after user confirms)

### Phase 2 prep (once)

1. **Create feature branch**
   - Run `git status --porcelain`. If dirty, show the diff summary and ask whether to stash, proceed anyway, or cancel. On **stash**, record the resulting stash as `stash_ref`; on **proceed anyway**, record the `git status --porcelain -z --untracked-files=all` paths as `pre_existing_dirty` — `-z` because §2.2 enumerates in that form and subtracts this set from it, and a path carrying a space or a non-ASCII byte is quoted without it. Steps 6.5 and 7.5 need both (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.2 carve-outs 1–2); a clean tree records `null` for each.
   - Resolve the branch name by invoking `Skill(skill: "workflows-core:reference", args: "branch-naming")` and following it — **the repo's own documented convention wins**. Read the repo's `CONTRIBUTING.md`, `CONTRIBUTION.md`, `README.md`, `DOCUMENTATION-GUIDELINES.md`, `CLAUDE.md` for a branch-naming section (§1.1) and fill its segments (§1.2): an **identity** placeholder from the §2 ladder (`$GIT_USER_INITIALS` → `git config user.initials` → inference → the §2.5 prompt), an **issue-key** segment from the run's own resolved key when it has one (else the documented no-issue literal), and the **description** segment from the slug `upgrade-<component>-to-<version>` (or `upgrade-<first>-and-<N>-more` for a batch). Never add an identity segment the pattern does not ask for. Only when no convention is documented (§1.4) build `<prefix>/<slug>` with the §2 ladder's fallback `chore/`.
   - **Where the branch starts.** Resolve `<base>`, the default branch's name, by `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.8 — the ladder steps 6.5 and 7.5 resolve it with, so the base it offers to branch from is the base its pull request targets. Never judge by a list of names: a local `develop` in a repository whose default is `main` is a branch like any other.
     - **§2.8's ladder is exhausted** — no `origin`, or an `origin/HEAD` that is unset or names a ref that does not exist, and none of the branches it probes → there is no base to measure against or to branch from: ask nothing, print `Base branch unresolved (<reason>) — branching from the current position.`, print it again with the Upgrade Summary beside step 7.5's `Code repo:` line, and cut the branch from HEAD.
     - **HEAD is on `<base>`** (`git branch --show-current` prints it) → nothing to ask.
     - **HEAD is not on `<base>`** (it prints another name, or nothing on a detached HEAD) → list the commits HEAD carries that the base does not: `git log origin/<base>..HEAD --oneline` (§2.8 yields a `<base>` only where `origin/<base>` exists). Non-empty output → ask, naming `<base>` and listing those commits, whether to branch from current position, branch from `<base>`, or cancel. Empty output with exit 0 → nothing to ask. A non-zero exit is a failed read, never "no ahead commits": keep its error rather than redirecting it away, show it, and ask the same question.
     - **Branch from current position** cuts the branch from HEAD. **Branch from `<base>`** runs `git switch <base>` and nothing more — no fetch and no pull — before the branch is cut. Where git refuses the switch (an uncommitted change it would overwrite), report its error and the paths it named, and stop as cancel does: no branch exists yet, and none is cut from the HEAD the user just declined.
   - Run `git checkout -b <branch-name>`. If it exists, append `-<7-char-sha>`.

2. **Capture baseline tests** — Invoke the existing test baseline agent once and reuse the result for the entire batch:

   ```
   task(
     subagent_type: "dev-workflows:test-baseliner",
     model: `<detection_model — §2.1 Sonnet chain>`,
     description: "Capture test baseline",
     prompt: "Mode: capture
     Project root: [absolute repo path]"
   )
   ```

   **Store the returned `## Test Baseline` block whole** and re-supply it as `baseline_block` on every executor dispatch below — its `### Suites` rows are what let verify tell a suite that regressed from one that could not run at either end, and `passing_count` / `passing_tests` are re-keyed from it, never in place of it. Do not re-run baseline capture per component.

   Act on its `Status` before executing anything: `PARTIAL` names the suites this batch's verification will not cover — list them on the Upgrade Summary's `Not verified:` line and continue, since a runner that is not installed for one language is not a reason to leave another's component unupgraded. `NO_TESTS` is not a failure and is not asked about — every suite ran cleanly and the repository holds no tests (`dev-workflows:test-baseliner` capture step 4), so nothing was lost and no component's finish is marked down for it.

   `RUN_FAILED` or `COMMAND_NOT_FOUND` means **nothing was captured, and what to do about it is the operator's decision rather than this command's** — the same question `/vuln` Step 3 puts, one capture serving one run in both. Surface the block's `### Suites` rows and its `### Notes` lines first — a hint has an answer to give wherever a note names the runner's own command — then ask:

   `choices: ["Specify test command to use", "Upgrade unverified (the pull request opens as a draft carrying the DO-NOT-MERGE banner)", "Cancel this run"]`

   - **Specify test command to use** → take free text, record it as `test_command_hint`, and re-dispatch the capture **immediately**, adding the line `command_hint: [the answer]` to the prompt. Act on the returned `Status` by this same list. Ask at most twice in a run; after that proceed as the option below does, with the last capture failure as the recorded reason.
   - **Upgrade unverified** → execute every component. Each that reaches its verify finishes `TESTS_NOT_RUN`, because verify refuses a baseline covering no suite before it runs anything (`dev-workflows:test-baseliner` verify's pre-step gate), so the batch's pull request is a draft the banner says not to merge (step 7.5, `clean_finish: false`).
   - **Cancel this run** → stop before the first component executes. **The branch step 1 cut stays**, empty: this plugin never deletes a branch (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §1 rule 3), so name the stray ref in the report rather than leaving it unexplained. Nothing was edited and no component is reported upgraded.

   **Asked once for the batch, because the baseline is captured once for the batch** — the answer is a property of the repository and this run works one, so re-asking per component would put the same question to the same tree.

   **Where `test_command_hint` was recorded, every later `test-baseliner` call in this run carries it** — which here means every `upgrade-executor` dispatch carries it as `command_hint:`, because the verify calls are the agent's and not this command's (its step 3). **A verify over a different set of suites is not a comparison**, and dropping the hint does not merely lose the verification, it manufactures a wrong answer: a hinted suite the baseline recorded pairs with nothing at verify, so its every baseline passing test falls out as **Missing from run** and the report reads `REGRESSIONS` against an upgrade that caused none — which this command's own "Handling Test Failures" would then put to the operator as a revert decision. Where the hint was all that was detected, verify instead detects nothing and returns `COMMAND_NOT_FOUND`, finishing every component `TESTS_NOT_RUN` after the operator supplied a command that worked.

   **And report every `### Notes` line the block opens with `CAVEAT: ` before executing, whatever the `Status` was** — `OK` included, which is the arm on which a marked line is the return's own account of a baseline that is not what its counts claim: a qualifying suite nothing ran, counts a `Make` indirection may have summed twice, a `Make` fold's identifiers unattributed to what printed them — three states the `Status` and the counts show nothing of (`dev-workflows:test-baseliner` capture step 5). The mark is the agent's, so nothing here judges which note matters; an unmarked note records where a command ran and is not carried. Each marked line goes onto the Upgrade Summary's `Caveats:` line, which is batch-level for the same reason `Not verified:` is.

### Per-component loop (sequential, in requested order)

3. **Delegate execution** — For each `READY` plan, invoke the executor agent with the planner handoff and the captured baseline.

   ```
   task(
     subagent_type: "dev-workflows:upgrade-executor",
     model: `<detection_model — §2.1 Sonnet chain — for SIMPLE/MODERATE; planning_model — §2 Opus chain — only if HIGH-RISK>`,
     description: "Execute component upgrade",
     prompt: "## Upgrade Execution Request
     repo: [absolute repo path]
     phase: full
     enforced_model: [run_flags.enforced_model, or omit]
     command_hint: [the recorded `test_command_hint` — include this line only where Phase 2 prep step 2 recorded one; it must reach step 3's verify call]
     baseline_block: |
       [the captured ## Test Baseline block, verbatim and whole]
     baseline:
       passing_count: [captured count]
       passing_tests:
         - [captured test ids]
     model_routing:
       classification: [component class]
       reason: <one-line>
       current_model: <the model this orchestrator is running under>
       enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every *_model below equals it and routing: bypassed
       detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # upgrade-planner, test-baseliner; upgrade-executor (SIMPLE/MODERATE); review-fixer
       planning_model: <§2 Opus chain>   # risk-planner (SIGNIFICANT/HIGH-RISK; frontmatter-pinned, recorded, no override unless §10 enforces a model); upgrade-executor escalates here only if HIGH-RISK
       review_model:  <§2 Opus chain>    # code-review (frontmatter-pinned; recorded, no override unless §10 enforces a model)
       opus_available: <true if a §2 Opus model resolved, else false>
       gate_tests_on_review: [true for SIGNIFICANT / HIGH-RISK, false otherwise]
       notes: <any §2 / §2.1 fallback or degradation>

     read the full READY upgrade plan from the file at [`plan_file`]"
   )
   ```

3a. **Handle an `upgrade-executor` stop.** If the executor returns `status: BLOCKED`, the upgrade plan at `plan_file` could not be read — an orchestrator bug, not a user choice: report the unreadable path to the user, mark this component `BLOCKED` in the Step 7 results table, and stop working this component (do not retry with a fresh planning pass). This applies regardless of classification — skip steps 4–6 for this component and continue the per-component loop with the next one.

4. **Review gate for SIGNIFICANT / HIGH-RISK** — If the executor returns `status: AWAITING_REVIEW`, run the Opus code-review gate before any test verification:
   - Capture the diff to a temp file: write `git add -N . && git diff` to `command mktemp -t dw-upgrade-diff-XXXXXX` (never inside a repo tree) and record its path as `review_diff_file`
   - Write the executor output to a temp file (`command mktemp -t dw-upgrade-claims-XXXXXX`, never inside a repo tree) and record its path as `claims_file`. Invoke `code-review` using the approved risk plan, the diff (from `review_diff_file`), `claims_file: [the path]`, and `model: <review_model — §2 Opus chain, equal to code-review's frontmatter pin; under §10, run_flags.enforced_model>` (frontmatter-pinned to Opus; recorded as `review_model` above, no override unless §10 enforces a model)
   - **Check the review's first line before acting on the verdict.** If it is `Diff: unreadable at <path>`, the orchestrator's own `review_diff_file` could not be read — an orchestrator bug, not a user choice: surface the unreadable path to the user and stop working this component, marking it `BLOCKED` in the Step 7 results table. Do NOT triage the finding and do NOT dispatch `review-fixer`: the finding names a capture failure no fixer can act on, and running the cycle would spend a fix dispatch and a re-review to arrive back here.
   - **Triage sub-step** (before any fixer dispatch): invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it. For each finding, verify its claimed consequence at the location it names; keep or dismiss; record every dismissal with a reason that disposes of that finding's own claim. Hand the fixer **survivors only**, and carry the dismissal list into this run's report.
   - If review returns `BLOCK` or `PASS WITH RECOMMENDATIONS`, invoke `review-fixer` with model: `<detection_model — §2.1 Sonnet chain>` for the surviving `BLOCKER` and `MAJOR` findings
   - **Handle a `review-fixer` stop.** If its `Stop condition flag` is `NEEDS HUMAN`, do NOT re-run the review: surface the deferred BLOCKER(s) to the user with the reason `review-fixer` gave, mark this component `BLOCKED` in the Step 7 results table, and stop working this component — skip steps 5–6 and continue the per-component loop with the next one. Only when the flag is `CLEAR` do you **overwrite `review_diff_file`** with a fresh `git add -N . && git diff` and re-run the Opus review once against that refreshed path — so the re-review reads the post-fix diff, not the stale pre-fix capture
   - If the second verdict is still `BLOCK`, stop and escalate; do not continue to tests
   - **The recorded verdict names the version it was taken against.** Both the resumed verify step below and any regression fix that follows it change the tree after the review that produced this verdict, so the run's report states what the verdict covers and names the edits that followed it, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Where nothing followed it, it says that too.

5. **Resume verify step after review** — Re-invoke `upgrade-executor` with `phase: verify-resume`, **the same `repo:` this component's first dispatch carried**, the original `READY` plan (from `plan_file`), the same baseline block captured in Phase 2 prep, the same `command_hint:` where one was recorded, and the same `enforced_model:` where step 3's first dispatch carried one. **`repo:` and `command_hint:` are not optional on a resume**: this is the call that reaches step 3, whose verify takes its `Project root:` from `repo:` with no working-directory fallback and whose suite set must match the baseline's. If the resumed agent returns `status: BLOCKED`, the re-supplied file path could not be read: report the named path to the user and stop this component. Do NOT retry, and do NOT reconstruct the artifact — a resume that re-derives its own input is the failure `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`'s read-failure contract exists to prevent.

6. **If the executor returns `status: TEST_REGRESSION`**, follow "Handling Test Failures" below, then re-invoke `upgrade-executor` with `phase: regression-resume` + the chosen `regression_decision`, the same `repo:`, the original `READY` plan (from `plan_file`), the same baseline block, and the same `enforced_model:` where step 3's first dispatch carried one. If the resumed agent returns `status: BLOCKED`, the re-supplied file path could not be read: report the named path to the user and stop this component. Do NOT retry, and do NOT reconstruct the artifact — a resume that re-derives its own input is the failure `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`'s read-failure contract exists to prevent.

6.5. **Commit this component (in-loop, prompt-free)** — Once this component's own gates have settled — its review verdict is non-`BLOCK` or the user chose to keep it, and its verify step has returned — commit it before moving to the next one. Cite `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` and execute **§2.1–§2.3 only** (the split-call form of §2.12 — the gate runs every time): stage per §2.2 honouring `pre_existing_dirty`, and commit per §2.3 — the subject ends with `[<key>]` where the run resolved one and carries a `Work-Item:` trailer where the folder has one (`Skill(skill: "workflows-core:reference", args: "implementation-format")`, §3), with the rest of it matching whatever convention the repo's own `git log` shows: `upgrade <component> to <version>`, typed to the log's shape. Do **not** push here and do **not** ask §2.4's choice; step 7.5 owns both. Skipped under `--no-commit`.

   Committing per component is the point of putting this inside the loop: a batch that dies on component three still has one and two committed, each with its own message, on a branch that bisects.

   **Every loop-exit path routes here first.** Every exit that stops working a component before its gates settle runs 6.5 before the loop moves on: step 3a's `BLOCKED` (an unreadable `plan_file`), step 4's `Diff: unreadable` stop, the `review-fixer` `NEEDS HUMAN` stop, a second verdict still `BLOCK`, and a `BLOCKED` return from step 5's `verify-resume` or step 6's `regression-resume` dispatch. All but step 3a's come after the executor's first dispatch has already written the upgrade — and, past a fix cycle, `review-fixer` its fixes — so 6.5 commits that work under its own component's message instead of letting it be swept into the next component's commit by that component's `add -A`. Step 3a is different: it returns before the executor touches anything, so 6.5 finds nothing staged, makes no commit, and — because that component never reached the repository — it does **not** set `clean_finish: false` (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.9's third bullet). A component whose executor simply changed nothing, one that returned `BUILD_FAILED` (the executor reverts its own changes first), and one whose regression decision was `revert` take the same no-commit path.

   A component that reached the repository and ended `BLOCKED`, or whose review stayed `BLOCK`, **is** committed — unreviewed work that exists is recoverable, work that was never committed is not — and it sets `clean_finish: false` for step 7.5.

   **"Stop and escalate" on a persisting `BLOCK` stops the component, not the run.** The loop continues with the next component; step 7.5 still runs at the end. A reading that stops the whole run would leave every earlier component committed but never pushed.

7. **Collect results** — Accumulate one summary row per component. Preserve the classification, review verdict, related upgrades applied, any regression notes, every `CAVEAT: ` line and every `NEW-FAILURE: ` line this component's executor copied into the `notes` of **any** return it made — not only its last, since a `regression-resume` runs no verify of its own (`upgrade-executor`'s Phase resume note), so a New failure met at the first verify is absent from the `TEST_REGRESSION_KEPT` or `TEST_REGRESSION_REVERTED` that ends the component (`${CLAUDE_PLUGIN_ROOT}/references/handoff/upgrade-executor.md`) — which its `status` does not gate, so read them on `OK` as on any other value — and this component's commit sha (or "no changes").

7.5. **Code-repo handoff (push + PR, once for the batch)** — After the loop, cite `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` and execute the full `finish-code-branch` entry point (§2) inline. Step 6.5 already committed every component, so §2.2 takes its `nothing staged` path and the call continues into §2.4's consent choice and §2.5–§2.6 — the branch carries commits to push (§2.12). Skipped under `--no-commit`.

   Pass the §2.11 inputs: `repo` and `branch` from Phase 2 prep step 1; `pre_existing_dirty` and `stash_ref` as recorded there; `key` and `workitem_key` from the resolved folder, or `null` for a run with neither; `title` = `upgrade <component> to <version> [<key>]` for a single component, or `upgrade <first> and <N> more [<key>]` for a batch, dropping the suffix in a run with no key; `body_facts` = the Upgrade Summary rows, each component's classification and review verdict, and the test result against the Phase 2 prep baseline; `clean_finish: false` when any component ended `BLOCKED` or `TESTS_NOT_RUN`, or with a review still `BLOCK`, or with kept regressions, or with a `NEW-FAILURE: ` line in the `notes` of any return it made, `true` otherwise — that last condition being no status test and not makeable into one, since a New failure moves no `test-baseliner` `Status` and the component reaches here `OK` — `upgrade-executor`'s own green value, never `vuln-fixer`'s `SUCCESS` — with a red suite behind it (`dev-workflows:test-baseliner` verify step 6); and `commit_template: null` — `/upgrade` documents no full template of its own, so §2.3 derives the rest of each subject from the repo's own `git log`. Emit the §3.1 `Code repo:` outcome line with the Step 7 results table — one line for the batch, never one per component. **Under `--no-commit`** neither step runs, and §3.1's `--no-commit` row is emitted in place of the outcome line.

7.6. **Remove this run's handoff files** — nothing from here on reads one: each component's
   `plan_file`, and every `review_diff_file` and `claims_file` this run wrote. Remove each as
   `command rm -f -- "<path>"`, per `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`
   (**Hand off by file, not paste**), which says why nothing else would. A run that stops before this
   step removes the files it had made before it stops, in the same way — save a file the stop itself
   named as unreadable, which stays for the operator to look at (that reference again); a component
   that ended early (step 3a's unreadable `plan_file`, the `review-fixer` `NEEDS HUMAN` stop, a second
   verdict still `BLOCK`) keeps its files until here, since the loop goes on to the next component.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 8, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto` in step 9, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 9's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

8. **Post-batch maintenance** — After all components finish, invoke `impl-maintenance` (subagent_type: `"workflows-core:impl-maintenance"`, model: `<detection_model — §2.1 Sonnet chain>`) with a compact session handoff summarising what was upgraded, key failures or workarounds, and the overall result. **Always pass `Command run: /upgrade`** in that handoff — omitting it makes `impl-maintenance` default to `/implement`, mislabeling the run.

**Context hygiene.** This was a large run — consider **`/compact`** to free context before your next task (per `workflows-core:session-hygiene` §3 — non-pipeline, so `/compact` only; guidance only).

9. **Persist plugin feedback (automatic)** — After `impl-maintenance` returns, project its plugin-facing slice into the specs repo by invoking `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and calling its `emit-auto` entry point (§6). Pass the Lessons Learned report, `command: /upgrade`, the run's `key` (or `null`) and `source`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). `emit-auto` renders only the report's **Command workflow improvements**, **New agents / skills**, and plugin **Reference docs** sections plus the **Key observations** that triggered them (§4 plugin-facing predicate) — never target-project `CLAUDE.md`/hook advice — as `origin: auto` entries, dedupes by stable `id` (§3), resolves the target via the §2 specs-first ladder, and writes silently. List the persisted path (or "no plugin-facing signal — nothing persisted") after the lessons-learned report. ADDITIVE — this step NEVER fails the run, NEVER commits (still true — the assertion is scoped to *this step*, which only writes the feedback file; those writes are committed by the separate terminal `commit-artifacts` step, per `workflows-core:specs-repo-git` §4), and NEVER writes into the code repo or the current working directory, where it is not the specs repository.

10. **Commit session artifacts (terminal)** — Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session artifacts (/upgrade)` — or `NOISSUE …` when the run resolved no key — and pushes per §4 step 5. It NEVER touches the code repo this run just upgraded: that repo's per-component commits were step 6.5, and whatever push and pull request §2.4's consent choice, §2.8's base-branch ladder and §2.6's `gh` capability probe allowed were step 7.5, through a different reference and against a different remote. It NEVER force-pushes, NEVER fails the run, and skips entirely when the run carries `specs_git: blocked` (§3.3 G0), re-emitting that notice. Print its §6 outcome line as the run's last output, prefixed `Specs repo:`, with any guard notice repeated in full. No `resume.md` is written for `/upgrade` (`workflows-core:session-hygiene` §1 skip list).

---

## Version Resolution

| Token | Resolution |
|---|---|
| `component:1.2.3` | Use exact version; verify it exists; run compatibility check; surface conflicts (never silently downgrade) |
| `component:minor` | Latest stable patch within current `MAJOR.MINOR.*` |
| `component:latest` | Highest stable release; run compatibility check |
| `component:lts` | Consult official LTS source (see `lts-sources.md`); if lookup fails, ask the user |
| bare `component` | Highest version compatible with all other repo components; report conflict if none found |

---

## Output

```
## Upgrade Summary

| Component  | Before | After  | Class       | Review | Status  | Notes                       |
|------------|--------|--------|-------------|--------|---------|-----------------------------|
| springboot | 3.1.4  | 3.3.11 | HIGH-RISK   | PASS   | OK      | Also upgraded hibernate 6.4 |
| java       | 17     | 21     | SIGNIFICANT | PASS W/RECS | OK | Updated 2 test files        |
| commons-text | 1.10 | 1.11   | MODERATE    | N/A    | OK      |                             |
| redis      | -      | -      | -           | -      | SKIPPED | Not found in project        |

Tests: 142 passed, 0 regressions (baseline: 142 passing)
Not verified: Jest/npm (`CI=true npm test`, frontend/package.json) — baseline PARTIAL
Caveats: none
```

**`Not verified:` is the batch-level slot**, and the per-component `Notes` column is not a substitute for it: the baseline is captured once for the whole batch (Phase 2 prep), so a suite it could not cover is missed for **every** component and belongs on a line of its own. Fill it from the Phase 2 prep baseline's `### Suites` — each suite that row does not mark `OK` or `NO_TESTS`, with its command and its marker path — and write `none` where the baseline covered everything it detected. **Where the baseline covered nothing at all — a `RUN_FAILED` or `COMMAND_NOT_FOUND` capture the operator chose to upgrade past — `none` is the one thing this line must not say**, and the two get there differently. On `COMMAND_NOT_FOUND` there are no `### Suites` rows at all, so the fill rule enumerates nothing and the `none` predicate is **vacuously** satisfied — full coverage reported on the run that verified least. On `RUN_FAILED` the suites were detected and every one of them aborted, so each has a row and the fill rule enumerates them all, which is right. Say that nothing was verified, and why. A component whose own verify left something uncovered is the `Notes` column's, not this line's.

**`Caveats:` is the batch-level slot for a different thing, and the two are not merged**: `Not verified:` names a suite the baseline could not cover, which its `### Suites` rows already show, while a `CAVEAT: ` line names something those rows and the counts do **not** show — a suite nothing ran though nothing failed, counts that may be summed twice, a `Make` fold's unattributed identifiers. Fill it from the Phase 2 prep baseline's `### Notes`, verbatim, one marked line per entry, whatever that baseline's `Status` was; write `none` where it marked nothing, which is every batch whose repository has none of the shapes that mint one (`dev-workflows:test-baseliner` capture step 5). A marked line an `upgrade-executor` returned in its own `notes` is that **component's** and goes in its `Notes` cell instead, since only the baseline is captured once for the batch. **Every `NEW-FAILURE: ` line goes in that cell too, named test by test**, and belongs on neither batch line: it is the one entry here that is not about coverage — the suite ran and something in it is red — it is that component's own verify that met it, and it is what moved the batch's `clean_finish` to `false`.

Append a `### Review triage` section with one line per SIGNIFICANT/HIGH-RISK component that went through Opus review: - **Review triage:** [N findings reviewed, M survived] — dismissals: [one line per dismissal, `finding — reason`; or "none"] — or "N/A (SIMPLE / MODERATE, no Opus review)" for components that never reached review.

Include the `impl-maintenance` lessons-learned report after the summary table — or, under `run_flags.skip_feedback`, the `Session feedback: …` line in its place.

Also repeat the `Run flags: …` line whenever the run-flags strip at the top of this command printed one during this run (`workflows-core:run-flags` §6).

---

## Handling Test Failures

`upgrade-executor` cannot prompt the user directly — dispatched subagents have no access to
interactive tools, even when one is listed in their `tools:`. When it returns
`status: TEST_REGRESSION` (previously-green tests now failing, not auto-fixable), the
**orchestrator** (this command, running in the interactive session) handles the decision:

- Present the failing tests clearly (from the executor's `failing_tests` / `diagnosis`).
- Ask:
  ```
  choices: ["Keep the upgrade and leave the failing tests for you to fix", "Revert this upgrade and skip it", "Investigate further before deciding"]
  ```
- **"Investigate further"** → show more detail (the diff, full failure output) and re-ask
  the same choices — this loops here at the orchestrator until the user picks keep or revert.
- Map the final choice to `regression_decision: keep-anyway | revert` and re-invoke
  `upgrade-executor` with `phase: regression-resume` (see Phase 2 step 6).

**`status: TESTS_NOT_RUN` is a different return and takes no `regression_decision`.** It means the
verify call compared nothing — no failing tests to show, and nothing about this component's tests known
either way. The changes stay applied. Report the reason the executor recorded, carry the component into
the Upgrade Summary as unverified, and set `clean_finish: false` for the batch (step 7). Never map it
onto `revert`: rolling an upgrade back because a suite could not be started is a decision taken on no
evidence at all.

---

## Invariants (always enforced)

- ALWAYS `emit-block` (per `workflows-core:feedback-emission`) before escalating a halt caused by a **plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked) — so a run abandoned at the block still records it. NEVER for a work-quality review BLOCK or an environment / user halt (repo-missing, dirty-tree, key-not-found, cancellation)
- NEVER skip per-component classification after planning
- NEVER use Opus for a `MODERATE` component unless the user explicitly asks for it
- NEVER run tests for a `SIGNIFICANT` / `HIGH-RISK` component before the Opus review returns a non-BLOCK verdict
- NEVER modify files during Phase 1
- NEVER touch files before the upgrade branch exists
- ALWAYS capture the baseline once before executing any component — and where that capture returns `RUN_FAILED` or `COMMAND_NOT_FOUND`, **ask the operator rather than deciding it** (Phase 2 prep step 2), before the first component executes and while a baseline can still be taken. A `NO_TESTS` capture is not that state and is never asked about
- NEVER read a verify report as a pass while its `### New failures` list is non-empty — a New failure moves no `test-baseliner` `Status`, so `OK` and `PARTIAL` are both reachable with a red suite (`dev-workflows:test-baseliner` verify step 6). The list is read **beside** the `Status`, never instead of it: the `Status` arm's own return stands, the failures are named test by test in that component's `Notes` cell, and the batch finishes `clean_finish: false`
- ALWAYS pass the same baseline block to `upgrade-executor` on `phase: verify-resume`
- ALWAYS re-supply the same `enforced_model:` on every `verify-resume` / `regression-resume` re-invocation of `upgrade-executor` where step 3's first dispatch carried one — the nested `test-baseliner` dispatch inside it needs it on every call, not only the first
- ALWAYS include classification in the final summary table
- ALWAYS commit each component in step 6.5 as its gates settle, and run the full `finish-code-branch` once in step 7.5 (per `${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.12's split form) — the commits are prompt-free (§1 rule 5), the push and pull request sit behind §2.4's choice, and a run that ends with the upgrade uncommitted is a defect, not a style
- NEVER skip step 6.5 for a component that ended `BLOCKED` or with a review still `BLOCK` — it is committed like any other and sets `clean_finish: false`, which makes any pull request step 7.5 opens a draft carrying the DO-NOT-MERGE banner (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §2.9); whether one is opened at all is §2.4's consent choice, §2.8's base-branch ladder, §2.6's `gh` capability probe and §2.5's push — a declined or failed push, a slug failing §2.6's `^[^/]+/[^/]+$` test, a `gh` that is absent or not authenticated, or a pull request already open on the branch all end the run with none opened by it, and §3.1's rows rather than any list written out here are the authority on which line it emitted — never this flag
- NEVER push or ask for the pull request inside the per-component loop — one push, one pull request, one `Code repo:` line per run
- ALWAYS run `specs-preflight` at Phase 0 and `commit-artifacts` as the run's last action (per `workflows-core:specs-repo-git`) — bounded to `$SPECS_PATH`'s artifact paths (§2.1) and to plugin-created branches (§2.2), always `git -C "$SPECS_PATH"` and never a `cd` (§1 rule 1), never force-pushing, and never failing the run
- After the run, suggest **`/compact`** (a big non-pipeline run) per `workflows-core:session-hygiene` §3 — compact-only, no clear/resume pointer; guidance only, never auto-run.

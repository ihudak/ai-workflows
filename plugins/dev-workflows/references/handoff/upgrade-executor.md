# upgrade-executor Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

## Input (orchestrator → upgrade-executor)

The upgrade plan from upgrade-planner with `status: READY`, plus baseline info:

The `## Upgrade Plan` section may arrive inline (as shown below) **or** as a line naming the
absolute path of a `mktemp` file the orchestrator wrote it to. When given a path, `Read` the file
first and treat its content as that section.

```markdown
## Upgrade Execution Request
repo: /absolute/path/to/repo
phase: full                # full (default) | verify-resume | regression-resume — see "Phase" below
enforced_model: <model id or family>  # optional; run_flags.enforced_model (classification.md §10) when the
                            # orchestrator's run has one set. When present, pass it as `model:` on
                            # the agent's own test-baseliner dispatch in place of the Sonnet detection
                            # chain — the nested-dispatch rule §10 states for this agent.
pre_edit_tree: 3c4e9cd789d88d8d89c1073707c3585e41b0e614   # REQUIRED on phase: full and phase:
                            # regression-resume. The tree id the orchestrator recorded before this
                            # component's first dispatch (references/code-handoff.md §6.1), the same
                            # value on every call of the component. Every revert this agent makes
                            # restores it (§6.2), never HEAD, so a file the user had changed before the
                            # run keeps their changes. Absent where needed => BLOCKED.
regression_decision: keep-anyway  # keep-anyway | revert | retry-with-install-scripts — REQUIRED on phase: regression-resume only;
                            # the orchestrator obtains this from the user (subagents cannot prompt
                            # the user directly — see /upgrade "Handling Test Failures")
command_hint: "./mvnw test -q"  # optional; present only where Phase 2 prep step 2 recorded a
                            # test_command_hint. REQUIRED to be passed through to step 3's
                            # test-baseliner verify call, verbatim and in the same order, on this
                            # call and on every verify-resume of it: the baseline was captured
                            # with it, and a verify over a different set of suites is not a
                            # comparison — dropping it manufactures REGRESSIONS or
                            # COMMAND_NOT_FOUND out of nothing.
baseline_block: |            # REQUIRED — the whole `## Test Baseline` block the
  ## Test Baseline           # orchestrator captured, verbatim, `### Suites` included.
  …                          # It is what the agent hands `test-baseliner` verify, and
                             # its per-suite rows are what separate a suite that
                             # regressed from one that could not run at either end.
baseline:                    # The orchestrator (commands/upgrade.md Phase 2 prep, Step 2)
                             # ALWAYS captures the baseline before invoking this
                             # agent — this agent never re-baselines.
                             # On phase: verify-resume the orchestrator MUST
                             # re-supply the same baseline (the captured value
                             # cannot survive the AWAITING_REVIEW boundary).
  passing_count: 142
  passing_tests:             # REQUIRED — full list of passing test IDs so
                             # test-baseliner verify can detect regressions
                             # exactly. Also required on phase: verify-resume.
                             # Every identifier carries its suite's prefix,
                             # single-suite repositories included.
    - "[Maven] com.example.OrderTest#testCreate"
    - "[Maven] com.example.UserTest#testLogin"
allow_install_scripts: [canary-dep]   # optional — the packages whose install-time code the user allowed
                                    # (install-time-code.md); only ever on a retry after a
                                    # return that named them in skipped_install_scripts
model_routing:               # optional; set by orchestrator for SIGNIFICANT / HIGH-RISK
  classification: SIGNIFICANT
  gate_tests_on_review: true # if true: stop after Build, return AWAITING_REVIEW
  # full schema: see workflows-core:model-routing/classification §4

## Upgrade Plan: spring-boot
status: READY
component: spring-boot
ecosystem: Maven
from: "3.1.4"
to: "3.3.11"
files:
  - path: pom.xml
    change: "bump spring-boot-starter-parent from 3.1.4 to 3.3.11"
related:
  - component: hibernate
    from: "6.2.0"
    to: "6.4.0"
    required: true
    reason: "Spring Boot 3.3 requires Hibernate 6.4+"
```

**phase values:**
- `full` (or omitted) — apply changes, build, verify, output. Default.
- `verify-resume` — second-call protocol after Opus review. Skip steps 1–2
  (changes are already applied and built); resume at step 3 (Verify).
- `regression-resume` — second-call protocol after the orchestrator asked the
  user about a `TEST_REGRESSION` return. Skip straight to "Test regression"
  step 4; requires `regression_decision`. `retry-with-install-scripts` also requires `allow_install_scripts`.

## Output (upgrade-executor → orchestrator)

```markdown
## Upgrade Result: spring-boot
status: OK              # OK | BUILD_FAILED | SKIPPED | TEST_REGRESSION | TEST_REGRESSION_KEPT | TEST_REGRESSION_REVERTED | TESTS_NOT_RUN | AWAITING_REVIEW | BLOCKED
component: spring-boot
from: "3.1.4"
to: "3.3.11"
related_applied:
  - {component: hibernate, from: "6.2.0", to: "6.4.0"}
tests_before: 142
tests_after: 142
regressions: 0
skipped_install_scripts: []   # every return — packages this install placed on disk whose install-time code it
                              # skipped, each with the command that would run (install-time-code.md),
                              # e.g. - "sharp@0.34.1 (npm: install: node install/check.js)"
reverted:               # BUILD_FAILED and TEST_REGRESSION_REVERTED only — every path the §6.2
  - pom.xml             # revert removed or restored (references/code-handoff.md)
reverted_from: 7a1f0e2b5c9d4e8f6a3b2c1d0e9f8a7b6c5d4e3f   # the same two statuses only — the tree
                        # the revert started from; a file it undid is brought back with
                        # `git restore --source=<id> --worktree`. A step of the revert that failed
                        # is a `REVERT-FAILED: ` line in `notes` (code-handoff.md §6.2), which
                        # /upgrade step 7.5 tests for to set clean_finish: false
notes: "Updated 2 test files: renamed @RunWith to @ExtendWith"   # it also carries, verbatim,
                         # every `CAVEAT: ` line the test-baseliner verify marked — on EVERY
                         # status this agent returns, `OK` included (the agent's step 3), since
                         # that mark names what the comparison could not see rather than
                         # anything that failed.
                         # And every entry of verify's `### New failures`, each on its own line
                         # prefixed `NEW-FAILURE: ` — on EVERY status, `OK` included, because no
                         # Status value carries one. The prefix is minted for the same reason
                         # `CAVEAT: ` is: this field is free text already holding auto-fix prose,
                         # uncovered-suite names and a regression diagnosis, and a bare list of
                         # test identifiers in it is indistinguishable from the failing list a
                         # TEST_REGRESSION also writes. /upgrade step 7.5 tests for this prefix
                         # to set clean_finish, so an unmarked entry is one no caller can act on
model_routing:           # echoed back when present in input
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

**status values:**
- `OK` — all changes applied, all previously-green tests still green. A `PARTIAL`
  verify is still `OK`: every suite the baseline covered is green, and `notes`
  names the ones it does not cover
- `BUILD_FAILED` — build failed, all changes for this component reverted to `pre_edit_tree` (§6.2),
  every path named in `reverted:`
- `SKIPPED` — component was NOT_FOUND or user chose to skip
- `TEST_REGRESSION` — regressions present, not auto-fixable, awaiting a user
  decision. This agent cannot ask the user (subagents have no interactive
  tools), so it stops here — see `notes` for the failing-test list and
  diagnosis. The orchestrator asks the user (per `/upgrade` "Handling Test
  Failures"), then re-invokes this agent with `phase: regression-resume` +
  `regression_decision: keep-anyway | revert | retry-with-install-scripts`.
- `TEST_REGRESSION_KEPT` — the `regression-resume` call's `regression_decision` was `keep-anyway`
- `TEST_REGRESSION_REVERTED` — the `regression-resume` call's `regression_decision` was `revert`; the
  tree is back at `pre_edit_tree` (§6.2), every path named in `reverted:`
- `TESTS_NOT_RUN` — `test-baseliner` verify returned `RUN_FAILED` or
  `COMMAND_NOT_FOUND`: no comparison was possible, so nothing is known about
  this component's tests either way. The changes are applied and **not**
  reverted — reverting needs evidence the upgrade is bad, and a suite that
  could not be run is evidence about the environment. `notes` carries the
  report's reason; the orchestrator decides. Distinct from `OK`, which asserts no
  baseline test was lost — **not that the suite is green**, since a `NEW-FAILURE: `
  line can stand beside it — and from `TEST_REGRESSION`, which asserts they failed
- `AWAITING_REVIEW` — `gate_tests_on_review: true` was set; changes are
  applied and the build succeeded, but tests have **not** been run yet.
  The orchestrator must perform the Opus code review, then re-invoke this
  agent with `phase: verify-resume` to continue from the Verify step.
- `BLOCKED` — this call could not use an input, and names it: the upgrade plan could not be read
  at the path the orchestrator supplied, or the request lacked `pre_edit_tree:` (`phase: full` and
  `phase: regression-resume`). This call changed nothing; on a resume, the changes an earlier call
  applied are still in the tree. Per the read-failure contract
  (`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`), the orchestrator must not
  re-run upgrade-planner to reconstruct the plan — surface what the agent names to the user
  and stop the upgrade for this component; on a `revert` decision it runs the revert itself first
  (`${CLAUDE_PLUGIN_ROOT}/references/code-handoff.md` §6.3).

### AWAITING_REVIEW output shape

Use this exact shape (omit `tests_before` / `tests_after` / `regressions` —
they are meaningless before tests run):

```markdown
## Upgrade Result: spring-boot
status: AWAITING_REVIEW
component: spring-boot
from: "3.1.4"
to: "3.3.11"
related_applied:
  - {component: hibernate, from: "6.2.0", to: "6.4.0"}
build: OK
files_changed:                # full list — needed by the orchestrator's Opus review
  - pom.xml
  - subproject/build.gradle
notes: null                   # or any in-place adjustments made during apply
model_routing:
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

### TEST_REGRESSION output shape

```markdown
## Upgrade Result: spring-boot
status: TEST_REGRESSION
component: spring-boot
from: "3.1.4"
to: "3.3.11"
related_applied:
  - {component: hibernate, from: "6.2.0", to: "6.4.0"}
tests_before: 142
tests_after: 140
regressions: 2
failing_tests:                # full list — the orchestrator shows these to the user,
                              # prefixed as the verify report's own lists are
  - "[Maven] com.example.OrderTest#testCreate"
diagnosis: <one-line: likely cause, e.g. "Hibernate 6.4 changed default fetch type">
notes: null
model_routing:
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

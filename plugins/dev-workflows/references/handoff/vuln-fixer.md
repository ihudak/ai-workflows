# vuln-fixer Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

## Input (orchestrator → vuln-fixer)

The research report from vuln-research for a SINGLE CVE with `status: READY`, plus:

The `## Research Report` section may arrive inline (as shown below) **or** as a line naming the
absolute path of a `mktemp` file the orchestrator wrote it to. When given a path, `Read` the file
first and treat its content as that section.

```markdown
## Vuln Fix Request
repo: /absolute/path/to/repo
branch: fix/PROJ-2423-CVE-2023-46604   # REQUIRED on phase: full. The orchestrator resolves it
                                    # (/vuln Step 1 step 5, per its "Git Workflow → Branch naming");
                                    # vuln-fixer creates exactly this branch and never derives one,
                                    # because /vuln Step 3.9 pushes the same value. Absent => BLOCKED.
pre_edit_tree: 5e8f2c…   # REQUIRED on phase: full and phase:
                                    # regression-resume. The tree id the orchestrator recorded before
                                    # this CVE's first dispatch (references/code-handoff.md §6.1), the
                                    # same value on every call of the CVE. Every revert this agent makes
                                    # restores it (§6.2), never HEAD, so a file the user had changed
                                    # before the run keeps their changes. Absent where needed => BLOCKED.
phase: full                        # full (default) | verify-resume | regression-resume — see "Phase" below
enforced_model: <model id or family>    # optional; run_flags.enforced_model (classification.md §10) when the
                                    # orchestrator's run has one set. When present, pass it as `model:` on
                                    # the agent's own test-baseliner dispatch in place of the Sonnet
                                    # detection chain — the nested-dispatch rule §10 states for this agent.
baseline_tests: provided           # "provided" — the only value
  # The orchestrator captures the baseline once per run and supplies it below,
  # on BOTH paths and whatever gate_tests_on_review says (see `/vuln` Step 3).
  # "run-fresh" — vuln-fixer capturing its own — is RETIRED, not merely invalid
  # under a gate. It was invalid under gate_tests_on_review: true because a
  # baseline captured inside the fixer cannot survive the AWAITING_REVIEW
  # boundary; it is gone from the other path too for an unrelated reason —
  # a capture that cannot run raises a question only the orchestrator can put,
  # this agent having no interactive tools. Do not reintroduce it.
command_hint: "./mvnw test -q"     # optional; present only where the orchestrator's baseline step
                                   # recorded a test_command_hint (/vuln Step 3). REQUIRED to be
                                   # passed through to step 5's test-baseliner verify call, verbatim
                                   # and in the same order, on this call and on every verify-resume
                                   # of it: the baseline was captured with it, and a verify over a
                                   # different set of suites is not a comparison — dropping it
                                   # manufactures REGRESSIONS or COMMAND_NOT_FOUND out of nothing.
baseline_passing: 47               # count of passing tests (required when "provided")
baseline_block: |                  # required when "provided", and on verify-resume — the whole
  ## Test Baseline                 # `## Test Baseline` block the orchestrator captured, verbatim,
  …                                # `### Suites` included. It is what vuln-fixer hands
                                   # test-baseliner verify, and its per-suite rows are what
                                   # separate a suite that regressed from one that could not run
                                   # at either end.
baseline:                          # required when "provided"; may also be sent on verify-resume
  passing_tests:                   # the full list — needed for precise regression detection.
                                   # Every identifier carries its suite's prefix, single-suite
                                   # repositories included (handoff/test-baseliner.md).
    - "[Maven] com.example.FooTest#testCreate"
    - "[Maven] com.example.BarTest#testLogin"
no_address_placeholder: NOISSUE   # the literal the repo already writes; omit if it uses none
regression_decision: keep-anyway   # keep-anyway | revert — REQUIRED on phase: regression-resume only;
                                    # the orchestrator obtains this from the user (subagents cannot
                                    # prompt the user directly — see /vuln "Handling Test Failures")
model_routing:                     # optional; set by orchestrator for SIGNIFICANT / HIGH-RISK
  classification: SIGNIFICANT
  gate_tests_on_review: true       # if true: stop after Build, return AWAITING_REVIEW
  # full schema: see workflows-core:model-routing/classification §4

## Research Report (single CVE)
### CVE-2023-46604
status: READY
address: PROJ-2423
description: "Apache ActiveMQ RCE via ClassInfo deserialization"
library: activemq-broker
ecosystem: Maven
vulnerable_range: "<5.15.16"
current_version: "5.15.5"
safe_version: "5.15.16"
files:
  - path: pom.xml
    change: "bump activemq-broker.version from 5.15.5 to 5.15.16"
```

**phase values:**
- `full` (or omitted) — read the supplied baseline → create the fix branch → apply → build → verify. Default. (The first step captures nothing; the orchestrator did.)
  The branch is created **before** the edit, so it exists on every path this agent can
  return from, including `AWAITING_REVIEW`.
- `verify-resume` — second-call protocol after Opus review. Skip steps 1–4
  (branch, fix and build are already done); resume at step 5 (Verify), after
  re-reading the supplied block's `Status` as step 1 would — its `NO_TESTS` arm
  decides whether step 5 runs at all, and this call does not execute step 1.
- `regression-resume` — second-call protocol after the orchestrator asked the
  user about a `TEST_REGRESSION` return. Skip straight to "Test regression"
  step 4; requires `regression_decision`.

## Output (vuln-fixer → orchestrator)

```markdown
## Vuln Fix Result: CVE-2023-46604
status: SUCCESS         # SUCCESS | BUILD_FAILED | TEST_REGRESSION | TESTS_NOT_RUN | REVERTED | SKIPPED_BY_USER | AWAITING_REVIEW | BLOCKED
branch: fix/PROJ-2423-CVE-2023-46604
                        # no `pr_url` and no commit sha: this agent creates the branch and stops.
                        # The commit, the push, and the pull request are the orchestrator's, in
                        # /vuln Step 3.9 (references/code-handoff.md §2), and it records them
                        # in its own `Code repo:` outcome line.
tests_before: 47
tests_after: 47
regressions: 0
reverted:               # BUILD_FAILED and REVERTED only — every path the §6.2 revert removed or
  - pom.xml             # restored (references/code-handoff.md), so the orchestrator can name them
reverted_from: 9c1d…    # BUILD_FAILED and REVERTED only — the tree the revert started from; a file
                        # it undid is brought back with `git restore --source=<id> --worktree`
notes: null             # or description of any auto-fixed test changes. It also carries,
                        # verbatim, every `CAVEAT: ` line the test-baseliner capture or verify
                        # marked — on EVERY status this agent returns, `SUCCESS` included
                        # (the agent's steps 1 and 5), since that mark names what the
                        # comparison could not see rather than anything that failed.
                        # And every entry of verify's `### New failures`, each on its own line
                        # prefixed `NEW-FAILURE: ` — on EVERY status, `SUCCESS` and `OK` included,
                        # because no Status value carries one. The prefix is minted here for the
                        # same reason `CAVEAT: ` is: this field is free text already holding
                        # auto-fix prose, uncovered-suite names and a regression diagnosis, and a
                        # bare list of test identifiers in it is indistinguishable from the failing
                        # list a TEST_REGRESSION also writes. /vuln Step 3.9 tests for this prefix
                        # to set clean_finish, so an unmarked entry is one no caller can act on
model_routing:           # echoed back when present in input
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

**status values:**
- `SUCCESS` — fix applied, no regression found, branch created with the change on it,
  uncommitted. A `PARTIAL` verify is still `SUCCESS`: every suite the baseline
  covered is green, and `notes` names the ones it does not cover
- `BUILD_FAILED` — build failed after fix, changes reverted to `pre_edit_tree` (§6.2), every path
  named in `reverted:`
- `TEST_REGRESSION` — previously-green tests failed and were not auto-fixable;
  the fix is applied and built on the fix branch, uncommitted. This
  agent cannot ask the user (subagents have no interactive tools), so it
  stops here — see `notes` for the failing-test list and diagnosis. The
  orchestrator asks the user (per `/vuln` "Handling Test Failures"), then
  re-invokes this agent with `phase: regression-resume` +
  `regression_decision: keep-anyway | revert`.
- `TESTS_NOT_RUN` — `test-baseliner` verify returned `RUN_FAILED` or
  `COMMAND_NOT_FOUND`: no comparison was possible, so nothing is known about
  this CVE's tests either way. The fix is applied and built on the fix branch,
  uncommitted, and is **not** reverted — reverting needs evidence the fix is
  bad, and a suite that could not be run is evidence about the environment.
  `notes` carries the report's reason; the orchestrator decides. Distinct from
  `SUCCESS`, which asserts no baseline test was lost — **not that the suite is green**, since a
  `NEW-FAILURE: ` line can stand beside it — and from `TEST_REGRESSION`, which
  asserts they failed
- `BASELINE_FAILED` is **retired** and this agent returns it on no path. It
  reported a `RUN_FAILED` / `COMMAND_NOT_FOUND` capture taken inside the fixer,
  and abandoned the CVE with nothing applied — a disposition the orchestrator's
  own paths never shared, and the one an operator is now asked about instead
  (`/vuln` Step 3). A run the operator chooses to have applied unverified
  reaches `TESTS_NOT_RUN` through verify, which refuses a baseline covering no
  suite; a `PARTIAL` capture was never this and still is not
- `REVERTED` — the `regression-resume` call's `regression_decision` was `revert`; the tree is back at
  `pre_edit_tree` (§6.2), every path named in `reverted:`
- `SKIPPED_BY_USER` — user chose to skip (set by the orchestrator; this agent
  is not re-invoked in that case)
- `AWAITING_REVIEW` — `gate_tests_on_review: true` was set; the branch exists and
  carries the applied fix, the build succeeded, but tests have **not** been run.
  The orchestrator must perform
  the Opus code review, then re-invoke this agent with
  `phase: verify-resume` to run Verify. Because the branch already exists, an
  orchestrator-side stop here still has somewhere to commit the work
  (`/vuln` Step 3.9 with `clean_finish: false`).
- `BLOCKED` — the research report could not be read at the path the orchestrator supplied;
  nothing was changed. Per the read-failure contract
  (`${CLAUDE_PLUGIN_ROOT}/references/context-management.md`), the orchestrator must not
  re-run vuln-research to reconstruct the report — surface the unreadable path to the user
  and stop remediation for this CVE.

### AWAITING_REVIEW output shape

Use this exact shape (omit `tests_before` /
`tests_after` / `regressions` — none of them exist yet; `branch` IS reported, because
step 2 created it before the fix was applied):

```markdown
## Vuln Fix Result: CVE-2023-46604
status: AWAITING_REVIEW
branch: fix/PROJ-2423-CVE-2023-46604
build: OK
files_changed:                # full list — needed by the orchestrator's Opus review
  - pom.xml
notes: null                   # or any in-place adjustments made during apply
model_routing:
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

### TEST_REGRESSION output shape

Use this exact shape:

```markdown
## Vuln Fix Result: CVE-2023-46604
status: TEST_REGRESSION
branch: fix/PROJ-2423-CVE-2023-46604
tests_before: 47
tests_after: 45
regressions: 2
failing_tests:                # full list — the orchestrator shows these to the user,
                              # prefixed as the verify report's own lists are
  - "[Maven] com.example.FooTest#testCreate"
  - "[Maven] com.example.BarTest#testLogin"
diagnosis: <one-line: likely cause, e.g. "API signature changed in v5.15.16">
notes: null
model_routing:
  classification: SIGNIFICANT
  gate_tests_on_review: true
```

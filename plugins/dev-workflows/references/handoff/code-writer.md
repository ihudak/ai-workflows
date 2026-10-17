# code-writer Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it. The citations below are the caller's: `code-writer` carries no `Skill` tool, and nothing it does turns on a core reference.

`/dev-workflows:implement` dispatches `code-writer` with `model:` set to its `implementation_model` and hands it the request below in the prompt. Two modes share it: `step` codes one group of consecutive plan steps, and `fix` makes one fix attempt from a failure the caller hands over.

## Input (`/implement` → `code-writer`)

```markdown
## Code Writer Request
mode: step                 # step | fix. `step` codes the plan steps `steps` names (Phase 3A step 1,
                           # Phase 3B step 1). `fix` makes one attempt at what `failure_input` shows
                           # broke (Phase 3.5's fix loop, and a lint or build failure at its step 3).
plan_file: /tmp/dw-impl-plan-AbC123
                           # EVIDENCE. The approved plan. Where the user approved a mid-implementation
                           # re-plan it holds both plans under two headings: the re-plan's Steps are the
                           # work remaining, every Review focus line in either plan applies, and the
                           # re-plan governs only where the two contradict.
steps: [3, 4]              # mode: step — the numbers of the plan steps this dispatch codes, as the plan
                           # writes them, consecutive and in plan order; on a plan_file holding two plans,
                           # the re-plan's Steps. mode: fix — none.
spec_paths:                # CONTEXT, each path on its own. The in-scope specification.md, design.md and
  - /abs/specs/specifications/EPIC-KEY-1-slug/specification.md     # ARD, the documents the plan was
  - /abs/specs/specifications/EPIC-KEY-1-slug/design.md            # approved against; none where none
  - /abs/specs/specifications/PRD-KEY-slug/ard.md                  # is in scope.
summary_file: /tmp/dw-impl-summary-AbC123
                           # CONTEXT. The codebase summary the run's exploration wrote (Phase 2A's,
                           # Phase 2B's, or Phase 1.7's fan-out synthesis).
repo_root: /abs/path/to/repo
                           # EVIDENCE, inline. The top level of the repository the run branched
                           # (`git rev-parse --show-toplevel`): the one repository code-writer writes in.
diff_so_far: /tmp/dw-impl-diff-AbC123
                           # CONTEXT. The working tree against HEAD, captured before this dispatch — what
                           # the run's earlier dispatches and applied patches changed. It can also hold a
                           # file the user had changed before the run began; the reports in
                           # earlier_reports name what this run changed. none before the run's first edit.
earlier_reports:           # CONTEXT, each report on its own. Every earlier dispatch's report_file, in
  - report: /tmp/dw-impl-code-XyZ789          # dispatch order; none on the run's first dispatch.
    answer: "Keep the old field and add the new one"
                           # only beside a report that returned needs_decision: the user's answer to its
                           # ### Decision, verbatim. It binds the rest of that group and every later one.
patches:                   # inline. Each patch Phase 1 carried for the tasks these steps code, which the
  - patch: security/<repo-slug>/scans/<folder>/patches/F2.patch   # caller checked and applied before
    outcome: applied       # any dispatch: applied | refused. The path is the follow-up's, relative to
    files: [src/session.ts]   # $SPECS_PATH. `files` (applied only) lists what it changed, relative to
                           # repo_root. none where Phase 1 carried no patch for these tasks.
task_shape: bug            # bug | none — bug where /implement set task_shape: bug (Phase 1.5).
class: SIGNIFICANT         # SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK — the run's class. A step has no
                           # class of its own: every step is coded under the run's, and only /implement's
                           # re-classification, which a `trigger` return starts, raises it.
scratch_checkout: HEAD     # HEAD | none. HEAD on task_shape: bug work: every run of the repro, a probe or a
                           # trimmed fixture goes in a scratch checkout of HEAD, the tree before the change,
                           # as bug-diagnosis.md's single rule sends a run once the edits have begun — on
                           # each dispatch of the run, the one that makes its first edit included, since
                           # code-writer never runs one against the working tree. none on any other work:
                           # it runs none of them.
failure_input: /tmp/dw-impl-failure-AbC123
                           # EVIDENCE on mode: fix; none on mode: step. A file holding test-baseliner's whole
                           # `## Test Verify Report` (Phase 3.5 step 6), or the lint or build command, the
                           # directory it ran in and its output (Phase 3.5 step 3).
model_routing:             # CONTEXT, inline. The run's model_routing block
  classification: SIGNIFICANT     # (workflows-core:model-routing/classification §4), as far as this
  implementation_model: claude-opus-5-5   # handoff declares it: the class `class` carries, the model
  enforced_model: opus     # this dispatch runs on, and — only where §10 enforces a model —
  routing: bypassed        # enforced_model with routing: bypassed. code-writer acts on no field of it:
                           # its tier is the dispatch's model:, its class is `class`, and it makes no
                           # dispatch of its own for enforced_model to reach.
report_file: /tmp/dw-impl-code-AbC123
                           # WRITTEN, never read. An empty file the caller made outside every repository
                           # (`command mktemp -t dw-impl-code-XXXXXX`); the report goes here and nowhere
                           # else.
```

**The read-failure tiers** follow `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`'s contract, and the agent states them where it takes the request:

- **Evidence** — `repo_root`, `plan_file`, and `failure_input` on `mode: fix`. One that cannot be read, or a `repo_root` that is not a directory, is a hard stop: the agent writes nothing in the repository, returns `blocked`, and its `### Blocked` reads `Unreadable: <field> at <path>`. It never reconstructs the input by other means — the plan from the earlier reports, the failure by running the check itself.
- **Context** — `spec_paths`, `summary_file`, `diff_so_far` and `earlier_reports`, each path on its own, and `model_routing`. One that cannot be read degrades to absent, and the report's **Degraded inputs** line names it with its path.
- **Inline values** — `mode`, `steps`, `patches`, `task_shape`, `class` and `scratch_checkout` — are read from the request itself and have no read to fail. `report_file` is written, never read.

## Output (`code-writer` → `/implement`)

**The reply** is one line, `status: <done | needs_decision | trigger | blocked>`, and nothing else save the untrusted-content notice lines the agent's prompt requires after it. **The report** goes to `report_file`:

```markdown
## Code Writer Report
- **Status**: done             <!-- done | needs_decision | trigger | blocked — the reply's own value -->
- **Mode**: step               <!-- step | fix -->
- **Steps**: 3 coded; 4 left to the caller — it runs the suite
                               <!-- mode: step — each step handed: coded, stopped (and how far it got),
                                    or left to the caller (a step that runs a check). mode: fix — n/a -->
- **Degraded inputs**: none    <!-- each context input that could not be read: `<field> at <path>` -->

### Files changed
- `src/rating.ts` — edited — <what this dispatch changed in it, one line>
- `src/rating-cache.ts` — created — <one line>
- `src/legacy-rating.ts` — deleted
- _or_ none

### Settled by the run
- <the open question> — <what was chosen> — <where in the code it arose, `path:line`>
- _or_ none

### Out of scope
- repository `<its top-level path, or the name the code knows it by>` — <the change it needs> — <the step, or the failure, that showed it>
- _or_ none

### Runs                       <!-- task_shape: bug only -->
- `<the command, as run in the scratch checkout of HEAD>` — <its result, redacted> — <the hypothesis it decides, or what it minimised>
- _or_ none

### Decision                   <!-- needs_decision only -->
Question: <the question, as the user will read it>
Options:
1. <a complete answer> (Recommended)   <!-- the marker only where one option is clearly superior -->
2. <a complete answer>
Already coded: <the steps done, and how far into this step the dispatch got before the question arose>

### Trigger                    <!-- trigger only -->
Item: <the classification item the work met>
Paths: `<path>`, `<path>`

### Blocked                    <!-- blocked only -->
<what the plan names that is not so, the step that names it, and what the tree holds instead>
<!-- or, for an evidence input that could not be read: Unreadable: <field> at <path> -->
```

**The four statuses:**

- `done` — every step handed is coded, or left to the caller where it runs a check; on `mode: fix`, the attempt is made. `### Settled by the run` becomes the Phase 5 report's `### Assumptions & limitations`, and `### Out of scope` goes on the follow-up line Phase 3A/3B step 2 writes for that repository.
- `needs_decision` — Phase 1's test met mid-coding: nothing the run can read settles a question, and its answer changes what the user would notice. `### Decision` carries two to four options, never an *Other* (the harness adds the free-text answer itself). The caller asks, then dispatches afresh for the rest of the group, handed this report with the answer beside it in `earlier_reports`.
- `trigger` — `mode: step` at `SIMPLE` or `MODERATE` only: a classification item the approved plan did not state, with the paths that show it. The caller runs its re-classification raise.
- `blocked` — a step cannot be coded as the plan writes it, because something the plan names is not so. A `### Blocked` that reads `Unreadable: <field> at <path>` instead names an evidence input the agent could not read: an orchestrator bug, never a plan defect. On `mode: fix` that form is the only `blocked`, and a failure the attempt found no fix for is a `done` whose `### Settled by the run` says so.

On every status the report says what is already coded — `### Files changed` and the **Steps** line — so a later dispatch neither redoes nor undoes it, and nothing is reverted.

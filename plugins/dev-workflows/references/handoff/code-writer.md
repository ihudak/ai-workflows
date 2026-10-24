# code-writer Handoff Format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it. `code-writer` loads `workflows-core:model-routing/classification` itself, for §1.1's items alone, when it tests for a trigger; the §4 and §10 citations below are the caller's.

`/dev-workflows:implement` dispatches `code-writer` once for each writer unit, with `model:` set to its `implementation_model`, and hands it the request below in the prompt. It sends each later request for that unit to the same agent with `SendMessage` — a decision's answer, a fix round, a review's fixes — and, where reaching it again fails, dispatches a fresh `code-writer` carrying `earlier_reports` and `diff_so_far`. Where a `done` report marks Steps `not reached`, the agent having run short of room, it dispatches a fresh `code-writer` for those Steps — a continuation dispatch, carrying that report in `earlier_reports` and the diff so far — rather than resuming the one whose room ran out. Three modes share the request: `write` codes the unit's plan Steps in one dispatch and runs its checks — the build, the nearby tests and any check a Step names; `fix` fixes, in the unit's non-test files, what `failure_input` shows broke, and runs the failing checks again, making up to three attempts of its own, so each of the caller's fix rounds may hold up to three; and `review` applies a review's findings to the unit's non-test files.

## Input (`/implement` → `code-writer`)

```markdown
## Code Writer Request
mode: write                # write | fix | review. `write` codes the unit's plan Steps and runs its checks.
                           # `fix` fixes what failure_input shows broke and runs the failing checks again,
                           # up to three attempts in the one request.
                           # `review` applies review_file's findings to the unit's non-test files and runs
                           # nothing.
plan_file: /tmp/dw-impl-plan-AbC123
                           # EVIDENCE. The approved plan. Where the user approved a mid-implementation
                           # re-plan it holds both plans under two headings: the re-plan's Steps are the
                           # work remaining, every Review focus line in either plan applies, and the
                           # re-plan governs only where the two contradict. A closing `## Constraints added
                           # after approval` section, where the caller appended one, binds every step. A
                           # Step's `Piece:` line names the piece it belongs to.
unit: all                  # inline. The writer unit: all where one writer unit covers every piece, else
                           # the name of the piece the design gives writers of its own. mode: write codes
                           # the unit's Steps: every Step where unit is all; else each Step whose Piece:
                           # names one of pieces, and a Step with no Piece: line where the first file it
                           # names is in unit_files, or where no piece of the design's ## Pieces names
                           # that file — or it names none — and this unit holds the piece that section
                           # lists first.
pieces:                    # inline. The design's pieces this unit covers, each with its files as its
  - name: rating-api       # ## Pieces section gives them; all where the design draws no pieces.
    files: [src/rating.ts, src/rating-cache.ts]
  - name: rating-ui
    files: ["web/rating/**"]
unit_files: [src/rating.ts, src/rating-cache.ts, "web/rating/**"]
                           # inline. The files the unit's pieces name: each a path or a glob as their
                           # Files: lines write it, relative to repo_root, a glob resolved with Glob; or
                           # all where pieces is all, no piece narrowing the unit to some of the
                           # repository's files. code-writer edits no file outside them, save a new file
                           # a Step of the unit creates, and no test file at all.
spec_paths:                # CONTEXT, each path on its own. The in-scope specification.md, design.md and
  - /abs/specs/specifications/EPIC-KEY-1-slug/specification.md     # ARD, the documents the plan was
  - /abs/specs/specifications/EPIC-KEY-1-slug/design.md            # approved against; none where none
  - /abs/specs/specifications/PRD-KEY-slug/ard.md                  # is in scope.
summary_file: /tmp/dw-impl-summary-AbC123
                           # CONTEXT. The codebase summary the run's exploration wrote (Phase 2A's,
                           # Phase 2B's, or Phase 1.7's fan-out synthesis). Where it names the
                           # repository's build command, that is the build code-writer runs.
baseline_file: /tmp/dw-impl-baseline-AbC123
                           # CONTEXT. The ## Test Baseline block test-baseliner captured before the run's
                           # first edit, verbatim: its ### Suites rows — each suite's framework, marker,
                           # command and status — and its ### Pre-existing failures, which code-writer's
                           # nearby tests are run by and read against.
repo_root: /abs/path/to/repo
                           # EVIDENCE, inline. The top level of the repository the run branched
                           # (`git rev-parse --show-toplevel`): the one repository code-writer writes in.
diff_so_far: /tmp/dw-impl-partial-AbC123
                           # CONTEXT. The working tree against HEAD, captured before this request — what
                           # the run's earlier writers and applied patches changed. A path it shows
                           # that pre_existing_dirty does not name is this run's own, a failed attempt's
                           # edit no report names included; one pre_existing_dirty names can also hold
                           # the user's own uncommitted work. none before the run's first edit, and
                           # where the caller passes none.
earlier_reports:           # CONTEXT, each report on its own. The earlier code-writer reports the caller
  - report: /tmp/dw-impl-code-XyZ789          # passes, in order: each earlier writer unit's; on the
                           # caller's fallback — a fresh dispatch where reaching this unit's writer
                           # again with SendMessage failed — that writer's own; and on a continuation
                           # dispatch — a fresh code-writer for the rest of this unit after a done whose
                           # Steps line marks Steps not reached — that report. The latest report whose
                           # **Unit** is this request's unit decides: where it marks Steps not reached,
                           # code-writer codes exactly those. none where there is none. A helper one of them wrote is reused, never copied, save as
                           # ### Duplicates says.
    plan: first            # only where plan_file holds two plans: whose Steps the report's Steps line
                           # numbers — first, the plan before the re-plan, or re-plan.
    answer: "Keep the old field and add the new one"
                           # only beside a report that returned needs_decision: the user's answer to its
                           # ### Decision, verbatim. It binds the rest of that unit and every later one.
patches:                   # inline. Every patch Phase 1 carried, on every request — an applied one's files
  - patch: security/<repo-slug>/scans/<folder>/patches/F2.patch   # are this run's — which the caller
    outcome: applied       # checked before any dispatch: applied | refused. The path is the follow-up's,
    files: [src/session.ts]   # relative to $SPECS_PATH. `files` (applied only) lists what it changed,
                           # relative to repo_root. none where Phase 1 carried no patch.
task_shape: bug            # bug | none — bug where /implement set task_shape: bug (Phase 1.5).
class: SIGNIFICANT         # SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK — the run's class. A step has no
                           # class of its own: every step is coded under the run's, and only /implement's
                           # re-classification, which a `trigger` return starts, raises it.
scratch_checkout: HEAD     # HEAD | none. HEAD on task_shape: bug work: every run of the repro (and of
                           # the build it needs), a probe or a trimmed fixture goes in a scratch checkout
                           # of HEAD, the tree before the change, on every request of the run, the first
                           # included, before the run has made any edit as after it, and never against
                           # the working tree; a repro the diagnosis writes as a test is written there
                           # alone. That one call runs through the run lock too, from repo_root. The
                           # build and the nearby tests code-writer runs through the run lock are no such
                           # run: they run in repo_root on every work.
                           # none on any other work: it runs none of them.
pre_existing_dirty: [src/notes.txt]
                           # inline. The paths /implement recorded as dirty before the run's first edit
                           # (its pre_existing_dirty): the user's own uncommitted work. none where it
                           # recorded none. Where it names any, a repro that does not go red in the
                           # scratch checkout says, in its ### Blocked, that the checkout lacks them.
failure_input: /tmp/dw-impl-failure-AbC123
                           # EVIDENCE on mode: fix; none otherwise. test-baseliner's ## Test Verify
                           # Report, whole or the part of it naming the failures handed to code-writer —
                           # a failing test whose fix lies in the unit's code, one the test writer wrote
                           # among them — or a failing check's command — a lint, a build, a type-check,
                           # or another check — the directory it ran in and its output, each lint
                           # failure the caller found on the tree before the change marked pre-existing.
review_file: /tmp/dw-impl-review-AbC123
                           # EVIDENCE on mode: review; none otherwise. The review's findings as the caller's
                           # triage left them, with any **Severities to fix**, **User-applied** and **Plan
                           # ruling** line the caller passes, as references/review-fix.md names them.
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

- **Evidence** — `repo_root` and `plan_file`, and `failure_input` on `mode: fix` or `review_file` on `mode: review`. One that cannot be read, or a `repo_root` that is not a directory, is a hard stop: the agent writes nothing in the repository, returns `blocked`, and its `### Blocked` reads `Unreadable: <field> at <path>`. It never reconstructs the input by other means — the plan from the earlier reports, a failure by running the check itself, the findings from the code.
- **Context** — `spec_paths`, `summary_file`, `baseline_file`, `diff_so_far` and `earlier_reports`, each path on its own, and `model_routing`. One that cannot be read degrades to absent, and the report's **Degraded inputs** line names it with its path. With `baseline_file` absent, no nearby test runs, and `### Checks run` says so.
- **Inline values** — `mode`, `unit`, `pieces`, `unit_files`, `patches`, `task_shape`, `class`, `scratch_checkout` and `pre_existing_dirty` — are read from the request itself and have no read to fail. `report_file` is written, never read.

## Output (`code-writer` → `/implement`)

**The reply** is one line, `status: <done | needs_decision | trigger | blocked>`, and nothing else save the untrusted-content notice lines the agent's prompt requires after it. **The report** goes to `report_file`. A message that reaches the agent again with no `## Code Writer Request` in it — a decision's answer — goes on under its last request, and the agent rewrites that request's `report_file` whole.

**On `mode: write` and `mode: fix`:**

```markdown
## Code Writer Report
- **Status**: done             <!-- done | needs_decision | trigger | blocked — the reply's own value -->
- **Mode**: write              <!-- write | fix; review only in the blocked form below -->
- **Unit**: all                <!-- the request's unit, as it reads -->
- **Steps**: 1–3 coded; 4 left to the test writer; 5 left to the caller — it runs tests/test_rating.py, which the test writer writes
                               <!-- mode: write — each Step of the unit: coded; stopped (and how far it
                                    got); not reached, where the request ran short of room before it, which
                                    a continuation dispatch codes; left to the test writer, a Step that
                                    writes or changes a test file; or left to the caller, a step the caller
                                    keeps — a bisect, a patch's application, the repro's re-run against the
                                    change, the regression test's red-capability check, a step that runs a
                                    test this run will write or update, or a formatter that could not be
                                    limited to the step's paths, named with why — each with its command and
                                    the directory it runs from, and, for a test this run will write or
                                    update, that test's path as the step names it and whether the step
                                    expects it to fail: "5 left to the caller — runs
                                    tests/test_x.py by pytest tests/test_x.py::test_empty_x, from the top
                                    level; expects it to fail". A Step that writes a test and runs it is
                                    left to both: "4 left to the test writer, and to the caller — runs …".
                                    The caller runs one that expects a failure as the red-capability check
                                    on task_shape: bug work, and, on any other, expected to pass, at its
                                    test run. mode: fix — n/a -->
- **Degraded inputs**: none    <!-- each context input that could not be read: `<field> at <path>` -->

### Files changed              <!-- never a test file; what a check wrote itself — its build output, its cache — is no change of this request's -->
- `src/rating.ts` — edited — <what this request changed in it, one line>
- `src/rating-cache.ts` — created — <one line>
- `src/legacy-rating.ts` — deleted
- _or_ none

### Checks run                 <!-- every build, nearby-test and other check this request ran, each through the run lock, in the order run -->
- `<the command, as run through the lock>` in `<the directory it ran from>` — <the build | the nearby tests of `<directory>` | the check step <n> names | a check failure_input names> — <its result: passed; failed, with every failure by name, each marked fixed in a later run, broken by intent, pre-existing or not fixed; or the `run-lock:` line that ended it>
- _or_ none — <why: a return before the unit's Steps were all coded; no build to run and no suite the baseline marks OK for the directories changed; baseline_file not read>

### Tests broken by intent     <!-- mode: write — each existing test whose fix lies in its own file: it fails, or no longer compiles, because the change does what spec_paths or the plan says, and what the change alters is what it asserts or how it calls the code; never edited — the test writer's to update -->
- `<test name>` in `<file:line>` — fails: <its assertion's message, or the compile error> — the change: <the line of spec_paths or the plan that makes that change, `path:line`, quoted | no line read settles whether that behaviour changed>
- _or_ none

### Settled by the run
- <the open question> — <what was chosen> — <where in the code it arose, `path:line`>
- _or_ none

### Out of scope
- repository `<its top-level path, or the name the code knows it by>` — <the change it needs> — <the step, or the failure, that showed it>
- _or_ none

### Duplicates                 <!-- a helper an earlier writer wrote that this one copied, since reusing it needed a change outside unit_files -->
- `<the copy, path:symbol>` — duplicates `<the helper, path:symbol>` — <the change reuse needed>
- _or_ none

### Not fixed                  <!-- mode: write — a check's failure the fix attempts left; mode: fix — a failure failure_input names that this request left -->
- <the failure, as the check's output or failure_input names it> — <why it was left: still failing after the third fix attempt, with its last output; not run, the build failing; failing again on a second run, which the change does not explain; on mode: fix, its fix lies in `<path>`, a test file — the test writer's — the code doing what `<path:line>` says, or no line read settling which holds; not of the code — a missing dependency or tool, the `run-lock:` line that ended the run, or a project install script it needs that failed or that install-time-code.md never runs; failure_input marks it pre-existing — the caller found it on the tree before the change; the CAVEAT: line that accounts for it; or a formatter that could not be limited to this run's paths>
- _or_ none

### Tool runs                  <!-- mode: write — an install, code-generation or formatting command a plan step named, and each project install script an install skipped that install-time-code.md runs beside a build, run right after that install; mode: fix — the formatter or code generator that fixes a lint failure; each run in repo_root through the run lock -->
- `<the command, as run>` — <its result> — <what it wrote: a lockfile, generated files> — skipped: <the dependencies' install-time code, and each project install script that reference never runs, as its *Name what was skipped* names them, or none>
- _or_ none

### Runs                       <!-- task_shape: bug only: the runs made in the scratch checkout of HEAD -->
- `<the command, as run in the scratch checkout of HEAD>` — <its result, redacted> — <the hypothesis it decides, or what it minimised>
- _or_ none

### Decision                   <!-- needs_decision only -->
Question: <the question, as the user will read it; for a file outside unit_files, the file, the piece the design's ## Pieces gives it or that no piece names it, and what the step needs changed there>
Options:
1. <a complete answer> (Recommended)   <!-- the marker only where one option is clearly superior -->
2. <a complete answer>
Already coded: <the Steps done, and how far into this one the request got before the question arose>

### Trigger                    <!-- trigger only -->
Item: <the classification item the work met>
Paths: `<path>`, `<path>`

### Blocked                    <!-- blocked only -->
<what the plan names that is not so, the step that names it, and what the tree holds instead>
<!-- or, on bug work, for a repro a step names that does not go red in the scratch checkout of HEAD:
     Repro not red: step <n> — `<the command>` in `<the directory it ran in>` — <its redacted output>
     — rate <the reproduction rate the plan records, or none recorded> — <the runs made> runs
     and, where pre_existing_dirty names any path: the scratch checkout lacks the user's uncommitted
     files at <those paths>, which the working tree holds -->
<!-- or, on a continuation dispatch that coded none of the Steps it was handed:
     No progress: Steps <n>, <n> still not reached -->
<!-- or, for an evidence input that could not be read: Unreadable: <field> at <path> -->
```

**On `mode: review`:** `${CLAUDE_PLUGIN_ROOT}/references/review-fix.md`'s `## Fix Report`, its findings applied to the unit's non-test files only — save where an evidence input could not be read, where the report is the `## Code Writer Report` above with **Status** `blocked`, **Mode** `review`, its **Unit** and its `### Blocked` reading `Unreadable: <field> at <path>`.

**The four statuses:**

- `done` — on `mode: write`, every Step of the unit is coded, left to the test writer or left to the caller where the caller keeps it — or `not reached`, where the request ran short of room, which a continuation dispatch codes — and, where none is `not reached`, its checks ran, every failure they showed fixed or listed under `### Tests broken by intent` or `### Not fixed`, or named in `### Checks run` as pre-existing or as passing on its second run; on `mode: fix`, up to three attempts are made, the failing checks ran again after each, and `### Not fixed` names every failure they left, a line whose fix lies in a test file being the caller's to send to the test writer, or to decide where no source settles it; on `mode: review`, the `## Fix Report` is written. `### Settled by the run` becomes the Phase 5 report's `### Assumptions & limitations`; `### Tests broken by intent` is the test writer's to act on, its `code_report`; a `### Not fixed` line's reason goes into the Phase 5 report's `### Deferred items` beside the failure it names, where the run keeps that failure, and spares that failure a further round where a `CAVEAT:` line accounts for it or only a formatter that could not be limited to this run's paths would fix it; and `### Out of scope` goes on the follow-up line the caller writes for that repository.
- `needs_decision` — Phase 1's test met mid-coding: nothing the run can read settles a question, and its answer changes what the user would notice; or a file outside `unit_files` that the work must edit, another unit's or a pre-existing file no piece names. `### Decision` carries two to four options, never an *Other* (the harness adds the free-text answer itself). The caller settles it — a file outside `unit_files` by moving the file into this unit or merging the units, any other by asking the user — and sends the answer as the message that reaches the agent again with `SendMessage`, or, on a fresh dispatch, as the `answer:` beside this report in `earlier_reports`.
- `trigger` — `mode: write` at `SIMPLE` or `MODERATE` only: a classification item the approved plan did not state, with the paths that show it. The caller runs its re-classification raise.
- `blocked` — a step cannot be coded as the plan writes it, because something the plan names is not so — on bug work, a repro a step names that does not go red in the scratch checkout of `HEAD` among them, its `### Blocked` naming the command, its directory, its output, the rate the plan records and the runs made, and, where `pre_existing_dirty` names any path, that the checkout lacks those files — save where the plan's `### Hypotheses (ranked)` reads `Ranking withheld`, the user having chosen to proceed without a repro, where that run is listed under `### Runs` and is never a `blocked`. A `### Blocked` that reads `No progress:` comes from a continuation dispatch that coded none of the `not reached` Steps it was handed: the caller dispatches no further continuation for that unit, and puts the block as it puts any other. A `### Blocked` that reads `Unreadable: <field> at <path>` instead names an evidence input the agent could not read: an orchestrator bug, never a plan defect. On `mode: fix` and `mode: review` that form is the only `blocked`, and a failure the attempt found no fix for is a `done` that lists it under `### Not fixed`.

On every status the report says what is already coded — on `mode: write` and `mode: fix`, `### Files changed` and the **Steps** line; on `mode: review`, the `## Fix Report`'s `### Files changed`, where one is written — so a later request neither redoes nor undoes it, and nothing is reverted.

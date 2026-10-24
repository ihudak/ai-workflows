# test-writer Handoff Format

`/dev-workflows:implement` dispatches `test-writer` once a writer unit's `code-writer` has returned, with `model:` set to the tier the caller assigns it, and hands it the request below in the prompt. It sends each later request for that unit to the same agent with `SendMessage`, a decision's answer included, and, where reaching it again fails, dispatches a fresh `test-writer` carrying `earlier_reports` and `diff_so_far`. Three modes share the request: `write` writes the unit's tests and updates each existing test the code writer reported broken by intent, then runs them; `fix` fixes the failing tests `failure_input` names, in test files only, and runs them again; and `review` applies a review's findings to test files.

## Input (`/implement` → `test-writer`)

```markdown
## Test Writer Request
mode: write                # write | fix | review. `write` writes and updates the unit's tests and runs
                           # them. `fix` fixes and re-runs the failing tests failure_input names. `review`
                           # applies review_file's findings to test files and runs nothing.
task_description_file: /tmp/dw-impl-task-AbC123
                           # CONTEXT. The task, verbatim from the user where possible.
plan_file: /tmp/dw-impl-plan-AbC123
                           # EVIDENCE. The approved plan: its Steps, Files and Review focus, and on
                           # task_shape: bug, where the plan carries one (risk-planner's does), its
                           # ### Hypotheses (ranked) with the repro it ran. Where the user approved a
                           # mid-implementation re-plan it holds both plans under two headings: every
                           # Review focus line in either applies, and the re-plan governs only where the
                           # two contradict.
spec_paths:                # CONTEXT, each path on its own. The in-scope specification.md files the plan was
  - /abs/specs/specifications/EPIC-KEY-1-slug/specification.md   # approved against; none where none is.
design_path: /abs/specs/specifications/EPIC-KEY-1-slug/design.md
                           # CONTEXT. The in-scope design.md; none where none is in scope.
pieces:                    # inline. The design's pieces this unit covers, each with its files as its
  - name: rating-api       # ## Pieces section gives them; all where the design draws no pieces.
    files: [src/rating.ts, src/rating-cache.ts]
  - name: rating-ui
    files: [web/rating.tsx]
unit: all                  # inline. The writer unit: all where one writer unit covers every piece, else
                           # the name of the piece the design gives writers of its own.
unit_files:                # CONTEXT, each path on its own, relative to repo_root. The unit's source files,
  - src/rating.ts          # read for names, signatures and file locations only.
  - src/rating-cache.ts
  - web/rating.tsx
code_report: /tmp/dw-impl-code-AbC123
                           # CONTEXT. The unit's code-writer report: its ### Files changed and its ### Tests
                           # broken by intent are what test-writer reads, and on task_shape: bug its ### Runs,
                           # the repro runs made in the scratch checkout of HEAD — output, never code.
earlier_reports:           # CONTEXT, each report on its own. Each earlier report_file of this unit's test
  - report: /tmp/dw-impl-tests-XyZ789         # writer, in order; none where there is none. They serve
    answer: "Keep the old assertion"          # the caller's fallback: a fresh dispatch where reaching
                           # the same agent again with SendMessage failed. `answer:` stands only beside a
                           # report that returned needs_decision: the user's answer, verbatim.
diff_so_far: /tmp/dw-impl-partial-AbC123
                           # CONTEXT. The working tree against HEAD, captured before a fresh dispatch: what
                           # this unit's writers have written so far; none where the caller passes none.
                           # test-writer reads its test files' hunks, and of every other file only the path.
baseline_file: /tmp/dw-impl-baseline-AbC123
                           # EVIDENCE. The ## Test Baseline block test-baseliner captured before the run's
                           # first edit, verbatim: each suite's framework, command and row, and the tests
                           # already there.
repo_root: /abs/path/to/repo
                           # EVIDENCE, inline. The top level of the repository the run branched: the one
                           # repository test-writer writes in.
task_shape: bug            # inline. bug | none — bug where /implement set task_shape: bug.
failure_input: /tmp/dw-impl-failure-AbC123
                           # EVIDENCE on mode: fix; none otherwise. The part of test-baseliner's verify
                           # report that names the failing tests handed to test-writer — those it wrote
                           # or updated, and any failing pre-existing test — or a failing check's
                           # command, the directory it ran in and its output.
review_file: /tmp/dw-impl-review-AbC123
                           # EVIDENCE on mode: review; none otherwise. The review's findings as the caller's
                           # triage left them, with any **Severities to fix**, **User-applied** and **Plan
                           # ruling** line the caller passes, as references/review-fix.md names them.
report_file: /tmp/dw-impl-tests-AbC123
                           # WRITTEN, never read. An empty file the caller made outside every repository
                           # (`command mktemp -t dw-impl-tests-XXXXXX`); the report goes here and nowhere
                           # else.
```

**The read-failure tiers** follow `${CLAUDE_PLUGIN_ROOT}/references/context-management.md`'s contract, and the agent states them where it takes the request:

- **Evidence** — `plan_file`, `baseline_file` and `repo_root`, and `failure_input` on `mode: fix` or `review_file` on `mode: review`. One that cannot be read, or a `repo_root` that is not a directory, is a hard stop: the agent writes nothing in the repository, writes the blocked shape below, and returns `blocked`. It never reconstructs the input by other means — the plan from the code report, the baseline or a failure by running a suite itself.
- **Context** — `task_description_file`, `spec_paths`, `design_path`, `unit_files`, `code_report`, `earlier_reports` and `diff_so_far`, each path on its own. One that cannot be read degrades to absent, and the report's **Degraded inputs** line names it with its path. Where `spec_paths` is `none` or every one of them degraded, the task description and the plan's Steps and Review focus stand in for the spec; where `design_path` is `none` or degraded, the plan stands in for the design.
- **Inline values** — `mode`, `pieces`, `unit` and `task_shape` — are read from the request itself and have no read to fail. `report_file` is written, never read.

## Output (`test-writer` → `/implement`)

**The reply** is one line, `status: <done | needs_decision | blocked>`, and nothing else save the untrusted-content notice lines the agent's prompt requires after it. **The report** goes to `report_file`.

**On `mode: write` and `mode: fix`:**

```markdown
## Test Writer Report
- **Framework**: [name, or every suite written against, comma-separated | "not detected"]
- **Command**: `[the matching test command(s) from the baseline, or "n/a" if not detected]`
- **Tests written**: [N]
- **Files touched**: [list of paths, relative to project root, or "none"]
- **Degraded inputs**: none    <!-- each context input that could not be read: `<field> at <path>` -->

### Tests added
- `[test name]` in `[file:line]` — covers [what behavior, and the spec item, design line or Review focus line it comes from][ — piece <name>, where `pieces` lists two or more][; for a negative DOM assertion, `against [template file:line]`, the line step 5 cites][ — fixed: what a mode: fix change altered in it][ — regression test: `<the command, narrowed to it>` in `<the directory it runs from>`, on task_shape: bug, for the caller's red-capability check]
- ...
- _or_ "none (no new testable behavior in the unit)"

### Tests updated
- `[test name]` in `[file:line]` — [what it asserted → what it asserts now] — [the source line that changed its behavior — the spec's, the design's or the plan's, or, with no spec, the task description's — `path:line`, quoted][ — fixed: what a mode: fix change altered in it]
- _or_ "none"

### Runs
- `[the command, as run through the lock]` in `[directory]` — [its result: passed and failed counts and every failing test by name, this agent's and any other, or the `run-lock:` line that ended it]
- _or_ "none"

### Disagreements
- `[test name]` in `[file:line]` — fails: [the assertion's message] — the source says: [`path:line`, quoted] — the code does: [what the failure shows]
- `[symbol]` at `[file:line]` — signature: [the code's] — the design says: [`path:line`, quoted]
- _or_ "none"

### Not passing
- `[test name]` in `[file:line]` — [still failing after its third fix: its last failure | not run: the `run-lock:` line, the missing dependency's or tool's error, or absent from the run's output | its fix lies in `<path>`, a non-test file, the code writer's]
- _or_ "none"

### Skipped (pre-existing untested code)
- `[file:line]` — [one-line reason]
- ...
- _or_ "none"

### Notes
[anything unusual: untestable-in-isolation behaviors, discovered convention mismatches between test files, flaky-looking existing patterns — or "none"]

### Decision                   <!-- needs_decision only -->
Question: <the question, as the user will read it: the test, what it asserts, what the code report says changed (on mode: fix, what failure_input shows), and that nothing read settles which holds>
Options:
1. <a complete answer> (Recommended)   <!-- the marker only where one option is clearly superior -->
2. <a complete answer>
```

If `Framework: not detected`, return this truncated shape and STOP:

```markdown
## Test Writer Report
- **Framework**: not detected
- **Command**: n/a
- **Tests written**: 0

### Reason
The baseline records no framework at all — `test-baseliner` matched no candidate and the repository declares no test command. Caller: this was settled where the baseline was captured, before any file was edited; apply that decision rather than asking again here. A `command_hint` supplied now cannot repair it, because a capture taken after the edits is not a baseline.
```

**On `mode: review`:** `${CLAUDE_PLUGIN_ROOT}/references/review-fix.md`'s `## Fix Report`, its findings applied to test files only.

**On every mode, where an evidence input could not be read**, return this shape and STOP:

```markdown
## Test Writer Report
- **Framework**: n/a
- **Command**: n/a
- **Tests written**: 0

### Blocked
Unreadable: <field> at <path>
```

**The three statuses:**

- `done` — on `mode: write`, every behavior mapped has a test or is named in `### Notes` as untested, and every test written or updated passed in its last run or is listed under `### Disagreements` or `### Not passing`; on `mode: fix`, the same of each failing test handed; on `mode: review`, the `## Fix Report` is written; and the not-detected report is a `done` too, its **Framework** line the caller's to act on. A `### Disagreements` entry is the caller's to decide against the spec and the design, and the user's where neither settles it; a `### Not passing` entry is the caller's to send to the owner of the file it names, or to name in its report as a test left failing or not run.
- `needs_decision` — a pre-existing test, one the code report's `### Tests broken by intent` names or, on `mode: fix`, one `failure_input` names, whose behavior nothing the agent can read settles: its source — the spec, the design or the plan, or, with no spec, the task description — does not settle whether the behavior it asserts changed. The agent writes and runs every other test first and leaves that one as it was. `### Decision` carries two to four options, never an *Other* (the harness adds the free-text answer itself). The caller asks, then sends the answer as the message that reaches the agent again with `SendMessage`, or, on a fresh dispatch, as the `answer:` beside that report in `earlier_reports`; the agent applies it to the test the decision names and runs that test as usual.
- `blocked` — only an evidence input that could not be read: an orchestrator bug, never a judgement about the tests, and a marker distinct from `Framework: not detected` so the caller stops the run rather than applying its recorded skip decision. The caller surfaces the path and stops; it never prompts for a test command, never offers to skip tests, and never re-derives the input with a tool of its own.

On `done` and `needs_decision` — save the not-detected `done`, which writes nothing — the report says what is already written: on `mode: write` and `mode: fix` in `### Tests added`, `### Tests updated` and **Files touched**, on `mode: review` in the `## Fix Report`'s `### Files changed` — so a later request neither redoes nor undoes it.

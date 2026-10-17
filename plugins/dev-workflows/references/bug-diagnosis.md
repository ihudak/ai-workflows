# Bug-diagnosis discipline (embedded — shared reference)

Feedback-loop-first discipline for **bug-shaped** SIGNIFICANT / HIGH-RISK tasks. Cited by
`/implement` (Phase 2B) and followed by `risk-planner` when the caller sets `task_shape: bug`, and by
`code-writer`, `/implement`'s coding subagent, where its request carries `scratch_checkout: HEAD`.
Adapted from mattpocock `diagnosing-bugs`; aligns with `superpowers:verification-before-completion`.

**Who runs the repro.** Step 1's completion criterion requires *executing* a command, so it binds
whoever holds `Bash`: the `/implement` orchestrator; `risk-planner`, which carries `Bash` for this
purpose alone; and `code-writer`, on a plan step that runs the repro. `risk-planner`'s execution is
bounded — run the repro and read-only commands, making no file but the scratch checkout the section
below names where it says the repro runs in one, and never mutate the working tree, the index,
`HEAD`, or branch state; the caller owns every write. **`code-writer` carries out a plan's diagnosis
steps** — a run of the repro, a `[DEBUG-xxxx]` probe placed or read, a fixture or a script trimmed
to minimise the repro — and has `risk-planner`'s exception, held to the scratch checkout: it runs
each only in the scratch checkout of `HEAD` — the one the section below prescribes once the edits
have begun — and does so on every dispatch, its first included, before the run's first edit as
after it, since it never runs one against the working tree; it lists each run with its redacted
output. Whatever build that repro itself needs is part of running it there; in the working tree
`code-writer` runs no lint, build, type-check or test at any class. A plan's bisect, which moves
`HEAD`, and the checks after the review gate are the orchestrator's own (below). An agent without
`Bash` (`code-review` among them) is never held to the completion criterion and must not be asked
to satisfy it — it consumes the evidence the criterion produced.

## Principle — build the feedback loop before hypothesizing

A bug fix is only as trustworthy as the loop that proves it. Establish a failing, observable loop
first; only then reason about cause.

## Redact before you show anything

This discipline has you show commands, their output, and captured artifacts. **Redact every secret
first** — write `<REDACTED>` in its place. Build the repro loop against environment variables so the
credential stays in the environment rather than in what you show. Captured artifacts are the sharpest
trap: a HAR file, a request log, or a core dump carries auth headers and session tokens, so quote only
the lines that carry the signal, never the whole capture.

If the redacted output is not enough to diagnose the bug, say so and ask — do not un-redact to make
the evidence more convenient.

## When a run may happen — the review gate

`/implement` runs this discipline on SIGNIFICANT / HIGH-RISK work, where nothing of the change runs
before the Opus code review returns a non-BLOCK verdict, or a settle prompt's **Proceed** settles it
as one (its Phase 3B step 8). **One rule places every run below**, `/implement`'s first edit of the
change — a scan's patch applied included, a probe's tagged line not — dividing it:

- **Before the first edit**, where no change exists yet to review, the repro runs on the working
  tree: `risk-planner`'s step 1 repro and its minimisation by its arguments and input. A plan's
  diagnosis steps do not: `code-writer` carries them out in the scratch checkout of `HEAD` (below)
  on every dispatch, its first included, so a probe step 3 places is placed and read there too, and
  the cleanup gate strips any tagged line that reached the working tree all the same.
- **From the first edit until a non-BLOCK review, nothing runs against the working tree**, which
  holds the change: no check — a lint, a build, a type-check or a test — and no repro or probe. A
  command that writes the change rather than checks it, as an install, a code generation or a
  formatting does, is none of these: what it writes is part of the change, and the review diff
  carries it. A probe or the repro runs only in the scratch checkout of `HEAD` (below), the
  tree before the change. That takes a probe placed once the edits have begun and every run of the
  repro a plan step makes, which `code-writer` carries out there; and step 1's repro **on a
  re-plan** whose working tree already holds edits (`/implement` Phase 3A step 5's, or a `blocked`
  return's Revise at its Phase 3A step 1), which `risk-planner` runs there. So a plan carries no
  step that runs a check, the repro or a probe against the working tree between the first edit and
  the review.
- **A fixture or script `code-writer` trims** to minimise the repro (step 1) is trimmed and tried in
  the scratch checkout, before the first edit as after it: trimming it in the working tree would be
  an edit no cleanup gate strips.
- **After the gate, never before it**, and the orchestrator's own (`/implement` Phase 3B step 8),
  never `code-writer`'s: step 5's re-run of the repro, against the working tree; then
  the **red-capability check** — the reviewed regression test from step 4, run in a scratch
  checkout of `HEAD`, the pre-change tree, with that test file copied in at its own path, must fail
  there on its assertion of this bug's symptom, not on a symbol only the change adds. The **green
  check** is the caller's verify run (`/implement` Phase 3.5), in which the same test must pass.
  Where the red check passes instead, the test does not show it catches this bug, and the caller's
  report says so. Where it fails on anything but that assertion — a missing test bootstrap, a
  submodule's content, a helper only the change adds — the red check is **inconclusive**: the
  caller's report says so under `### Assumptions & limitations`, naming what it failed on, and the
  green check is still the caller's verify run.

**The scratch checkout** is outside every repository and is removed whatever the run in it exits
with, a red check's expected failure included. One Bash call makes it, runs in it and removes it, since
no shell variable survives from one call to the next:
`( d=$(command mktemp -d -t dw-bug-XXXXXX) && trap 'case "$d" in */dw-bug-*) command rm -rf -- "$d" ;; esac' EXIT && command mkdir -- "$d/tree" && GIT_INDEX_FILE="$d/index" git -C "<top level>" -c core.hooksPath=/dev/null --work-tree="$d/tree" checkout HEAD -- . && cd -- "$d/tree/<the directory the run needs>" && <the run> )`.
The checkout reads `HEAD`'s tree through an index file of its own into `"$d/tree"`, so nothing is
written into the working tree, its index or its refs; it keeps the `export-ignore` paths a
`git archive` would drop, a test bootstrap among them; and with `core.hooksPath` pointed at nothing,
no hook of the repository's runs, as a `post-checkout` hook otherwise would. The subshell's `trap`
removes the directory on every exit, and its guard matches the `mktemp` prefix, since BSD
`mktemp -t` appends a suffix of its own after the template. **Its limit: it holds no submodule's
content**, a submodule's directory standing empty there, so a run that needs one is inconclusive in
it. Where the run needs a dependency directory git does not track — `node_modules`, say — link it
from the working tree inside the same call
(`ln -s "<top level>/<dir>/node_modules" "$d/tree/<dir>/node_modules"`) rather than installing one.

## Steps

1. **Repro first.** Construct a **red-capable, deterministic, fast, agent-runnable** reproduction
   command that fails *because of this bug* — before forming any hypothesis. A bug you cannot
   reproduce on demand is not yet ready to fix.

   **Minimise it once it is red.** Cut the command's own inputs — arguments, input data, steps of a
   script — **one at a time**, re-running it after each cut, and keep only what the failure needs. It
   is minimal when removing any remaining element makes it go green. A minimal repro leaves fewer
   moving parts to suspect at step 2, and becomes the regression test step 4 lands where a correct seam
   exists. `risk-planner` writes no file: it varies only the command's arguments and standard input,
   and trimming a fixture or a script is a plan step `code-writer` carries out in the scratch
   checkout (above).

   **A performance regression takes a different repro.** Logs usually mislead about time, so the
   repro is a **measurement** — a timing harness, a profiler, a query plan — run on the current code,
   and it is red when the time exceeds the expected figure by more than its own run-to-run spread.
   Measure first, fix second. Finding where the time went in by bisecting between a good and a bad
   state moves `HEAD`, so it is the plan's first step, which the `/implement` orchestrator carries out
   itself from a clean tree before the run's first edit — before any patch is applied — ending in
   `git bisect reset`; never something `risk-planner` or `code-writer` runs, and never in the scratch
   checkout, which holds no history. Where the tree
   is not clean or the run already has edits, the plan omits the bisection and says why among its risks.

   **Completion criterion — one command, already run.** Step 1 is not finished until you can name
   **one** command — a test invocation, a script path, a `curl` — that you have **already run at least
   once**, showing the invocation and its (redacted) output. It must be **red-capable** (it drives the
   actual bug path and asserts the user's exact symptom, so it can go red on this bug and green once
   fixed — "runs without erroring" is not red-capable), **deterministic**, **fast**, and
   **agent-runnable** unattended. A command you have described but not executed does not satisfy this.

   **If you catch yourself reading code to build a theory before that command exists, stop.** Jumping
   straight to a hypothesis is the exact failure this discipline prevents. No red-capable command, no
   step 2.

   **Non-deterministic bugs.** The goal is not a clean repro but a **higher reproduction rate**. Loop
   the trigger, parallelise, add stress, narrow timing windows, inject sleeps. A bug that reproduces
   half the time is debuggable; one that reproduces 1% of the time is not — raise the rate until it is,
   and state the rate you achieved.

   **When you genuinely cannot build a loop**, stop and say so explicitly, listing what you tried,
   and name what would let you build one: access to an environment that reproduces it, or a
   redacted captured artifact — a HAR file, a log dump, a core dump, a timestamped recording. Whoever can ask the user
   asks; an agent that cannot returns the list to its caller (`risk-planner` in its `Needs:` line).
   `code-writer`, whose plan's repro does not go red in the scratch checkout of `HEAD`, returns
   `blocked` with the command, its directory, its output, the plan's recorded rate and the runs it
   made (its *Bug work*); the caller puts the block to the user, and a SIGNIFICANT or HIGH-RISK
   re-plan hands that output to `risk-planner`. A plan whose ranking reads `Ranking withheld` — the
   user chose to proceed without a repro — is the exception: `code-writer` runs its repro step,
   lists the result, and does not block on it.
   Do not go on to step 2 without a loop.
   A 30-second flaky loop is barely better than no loop; a 2-second deterministic one is worth the
   effort it takes to get there.

2. **Rank falsifiable hypotheses.** List **3–5** candidate causes, each stating (a) what it predicts
   you would observe and (b) the cheapest observation that would **falsify** it. Order by likelihood ×
   cheapness-to-test. A hypothesis you cannot falsify is not a hypothesis — drop it.
3. **Instrument with tagged, removable probes.** Each probe changes **one variable at a time** and
   names the hypothesis from step 2, or the pair of hypotheses, its result decides, so every result can
   be read back to what it settled. Prefer a debugger or REPL inspection where the environment allows it, then targeted
   logs at the boundaries that tell two hypotheses apart; never log everything and grep. Tag every
   temporary probe `[DEBUG-xxxx]` (a short unique token per probe). Every `[DEBUG-xxxx]`
   probe MUST be removed before the change is finalized (`code-writer` places and reads it in the
   scratch checkout, above, on every dispatch, and the `/implement` Phase 3B cleanup gate strips any
   that reached the working tree before the review diff is captured). **A probe never writes a secret's value**: one that checks
   a credential, token, key or connection string records only whether it is set and whether it is empty —
   `SET`, `EMPTY` or `UNSET`, and its length where that tells hypotheses apart — never the value and
   never a line that echoes it, as `env | grep` does — because what a probe writes
   lands in logs and CI output that outlive the run, where the redaction above never reaches.
4. **Fix at the correct seam; regression-test there.** Land the fix and its regression test at the
   **correct seam** (see `${CLAUDE_PLUGIN_ROOT}/references/design-format.md` `## Seams` — prefer the
   highest seam that still isolates the behavior). If **no correct seam exists**, that is itself a
   finding — record it (the code needs a seam before it can be safely tested); do NOT bolt a test onto
   the wrong seam to manufacture green.
5. **Evidence before the claim.** Never report the bug fixed until the repro from step 1 goes green.
6. **Name the confirmed hypothesis.** Where step 2 produced a ranked list and the fix was verified —
   the step-1 repro, or the regression test in the caller's verify run, ran green after the fix —
   state which hypothesis the fix acted on, or that it acted on none of them, and what showed it — a
   probe's result, or that the repro went green after a fix aimed at that hypothesis alone — in the
   run's report and the pull-request body, so the next person to debug this code learns what the
   cause was and not just that it was fixed. With no ranked list, there is nothing to name, and
   nothing is invented.

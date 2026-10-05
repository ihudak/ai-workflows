# Bug-diagnosis discipline (embedded — shared reference)

Feedback-loop-first discipline for **bug-shaped** SIGNIFICANT / HIGH-RISK tasks. Cited by
`/implement` (Phase 2B) and followed by `risk-planner` when the caller sets `task_shape: bug`. Adapted
from mattpocock `diagnosing-bugs`; aligns with `superpowers:verification-before-completion`.

**Who runs the repro.** Step 1's completion criterion requires *executing* a command, so it binds
whoever holds `Bash`: the `/implement` orchestrator, and `risk-planner`, which carries `Bash` for this
purpose alone. `risk-planner`'s execution is bounded — run the repro and read-only commands, and never
mutate the working tree, the index, `HEAD`, or branch state; the caller owns every write. An agent
without `Bash` (`code-review` among them) is never held to the completion criterion and must not be
asked to satisfy it — it consumes the evidence the criterion produced.

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

## Steps

1. **Repro first.** Construct a **red-capable, deterministic, fast, agent-runnable** reproduction
   command that fails *because of this bug* — before forming any hypothesis. A bug you cannot
   reproduce on demand is not yet ready to fix.

   **Minimise it once it is red.** Cut the command's own inputs — arguments, input data, steps of a
   script — **one at a time**, re-running it after each cut, and keep only what the failure needs. It
   is minimal when removing any remaining element makes it go green. A minimal repro leaves fewer
   moving parts to suspect at step 2, and becomes the regression test step 4 lands where a correct seam
   exists. `risk-planner` writes no file: it varies only the command's arguments and standard input,
   and trimming a fixture or a script is a plan step for the caller.

   **A performance regression takes a different repro.** Logs usually mislead about time, so the
   repro is a **measurement** — a timing harness, a profiler, a query plan — run on the current code,
   and it is red when the time exceeds the expected figure by more than its own run-to-run spread.
   Measure first, fix second. Finding where the time went in by bisecting between a good and a bad
   state moves `HEAD`, so it is a step of the plan the caller carries out from a clean tree, before the
   run's first edit, ending in `git bisect reset` — never something `risk-planner` runs. Where the tree
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
   probe MUST be removed before the change is finalized (the `/implement` Phase 3B cleanup gate strips
   them before the review diff is captured).
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

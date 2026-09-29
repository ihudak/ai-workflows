# /prompt-grill-me

Logs a corrective interaction, then grills the fix inline with a bounded (≤5-question) interrogation — self-contained, no plugin dependency.

## Who runs it

`/prompt-grill-me` runs outside the role pipeline and, alone with [`/prompt-brainstorm`](prompt-brainstorm.md) among the four feedback commands, **defers** its cost entry rather than writing one itself. Its Phase 3 is a long interactive grill that cedes the session, so the expensive part of the run happens after this command's last controllable step, and a cost line written here would price only the logging prologue. Phase 2 therefore records the labels the entry will carry, and the next cost-emitting run in the session writes it — attributed to the phase whose output you were correcting, not to whatever you happened to run next (`references/cost-emission.md` §13). [Workflow overview](../workflow.md#cross-cutting-commands) groups it under Plugin improvement, alongside [`/feedback`](feedback.md), [`/prompt`](prompt.md), and [`/prompt-brainstorm`](prompt-brainstorm.md). Reach for this one when a correction deserves more scrutiny than a one-shot fix but doesn't need a full brainstorming session — same logging, a short interrogation instead. Logging every correction here, not only the dramatic ones, is what lets the maintainer see the same friction recurring across engineers.

## Synopsis

```
/prompt-grill-me <corrective request> [--skip-costs]
```

`--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`, [`environment.md`](../reference/environment.md)) writes the deferred §13.1 record below with `"skip": true`, so the next cost-emitting run in the session still carves this segment out of its own window and then writes no entry for it; it is the only run flag this command applies — `--skip-feedback` and `--enforce-model` are reported ignored, since `/prompt-grill-me` dispatches no `impl-maintenance` and invokes no model routing.

`$ARGUMENTS`, once the run flag above is stripped, is the corrective request, captured **verbatim** as the User prompt block. Phase 1 infers the target command from recent context, asking only if genuinely ambiguous; if none applies, it records `n/a`.

Write the flag before the request, not inside it: only a leading run of flag tokens is stripped, so a `--skip-costs` written inside the request text itself is kept as part of the verbatim request, not read as a flag.

## What it needs

- **`$ARGUMENTS` itself, verbatim** — the correction to interrogate, and the corrective-triple's User prompt block.
- **Recent session context**, to infer the target `command`.
- **`$SPECS_PATH`** — for the specs-preflight/commit-artifacts bookkeeping only.
- **No plugin dependency.** Unlike [`/prompt-brainstorm`](prompt-brainstorm.md), which hands off to the separate `superpowers` plugin's `brainstorming` skill, this command's grill runs entirely on the bundled `references/grilling-technique.md` — nothing outside `workflows-core` is required.

## What it produces

An `origin: prompt` entry (Friction, User prompt verbatim, Resolution fixed at `Grilled the fix inline`), appended via the ladder [Session feedback](../reference/session-feedback.md) describes. **A deferred session-cost record too** — written in Phase 2 alongside the feedback entry, carrying the labels the cost entry will take. It is local and never committed; the next cost-emitting run in the session turns it into a real entry, attributed to the phase whose output you were correcting. See [Session cost](../reference/session-cost.md#spend-a-command-cannot-measure-itself). **The terminal `commit-artifacts` step runs inside Phase 2, before the Phase 3 grill** — not after — because the grill is interactive and may run long, and a commit placed after it would never execute. Phase 3 then interrogates the correction directly: one question at a time, capped at 5 (the highest Impact×Uncertainty questions about the fix), with any leftover high-impact gaps recorded rather than pursued further.

## Gates

No reviewer — the bounded grill itself is the only structure, and it is bounded on purpose: it stops at 5 questions rather than running to convergence the way `/create-prd`'s or `/design`'s relentless grills do.

## Example

```
/workflows-core:prompt-grill-me "the /epics draft put an acceptance criterion under the wrong Epic"
```

The command logs the corrective triple, commits it to the specs repo immediately, then interrogates the fix inline — at most 5 questions — following the embedded grilling technique.

## See also

- [Session feedback](../reference/session-feedback.md) — the entry format, including the two extra prose blocks a `prompt`-origin entry carries.
- [`/feedback`](feedback.md) — logs a standalone note with no corrective triple.
- [`/prompt`](prompt.md) — the same corrective triple, applied directly with no interrogation.
- [`/prompt-brainstorm`](prompt-brainstorm.md) — the same corrective triple, explored with the separate `superpowers:brainstorming` skill instead of grilled inline.
- [Workflow overview](../workflow.md#cross-cutting-commands) — where these four commands sit relative to the role pipeline.
- [`specs-repo-git.md`](../../references/specs-repo-git.md) — the `specs-preflight`/`commit-artifacts` entry points, and why this command's commit runs before its final phase rather than after.

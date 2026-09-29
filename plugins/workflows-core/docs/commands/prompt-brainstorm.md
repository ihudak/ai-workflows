# /prompt-brainstorm

Logs a corrective interaction, then hands off to `superpowers:brainstorming` to redesign the fix together, instead of applying a one-shot correction.

## Who runs it

`/prompt-brainstorm` runs outside the role pipeline and, alone with [`/prompt-grill-me`](prompt-grill-me.md) among the four feedback commands, **defers** its cost entry rather than writing one itself. Its Phase 3 cedes the session to the brainstorming skill, so the expensive part of the run happens after this command's last controllable step, and a cost line written here would price only the logging prologue. Phase 2 therefore records the labels the entry will carry, and the next cost-emitting run in the session writes it — attributed to the phase whose output you were correcting, not to whatever you happened to run next (`references/cost-emission.md` §13). [Workflow overview](../workflow.md#cross-cutting-commands) groups it under Plugin improvement, alongside [`/feedback`](feedback.md), [`/prompt`](prompt.md), and [`/prompt-grill-me`](prompt-grill-me.md). Reach for this one when a command's output was wrong in a way that needs **exploring**, not a quick one-shot fix — same logging, different next step. Every run logged here is signal the maintainer can act on, so use it rather than fixing things quietly and moving on.

## Synopsis

```
/prompt-brainstorm <corrective request> [--skip-costs]
```

`--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`, [`environment.md`](../reference/environment.md)) writes the deferred §13.1 record below with `"skip": true`, so the next cost-emitting run in the session still carves this segment out of its own window and then writes no entry for it; it is the only run flag this command applies — `--skip-feedback` and `--enforce-model` are reported ignored, since `/prompt-brainstorm` dispatches no `impl-maintenance` and invokes no model routing.

`$ARGUMENTS`, once the run flag above is stripped, is the corrective request, captured **verbatim** as the User prompt block. Phase 1 infers the target command from recent context, asking only if genuinely ambiguous; if none applies, it records `n/a`.

Write the flag before or after the request, never inside it: a leading run of flag tokens and a trailing run of flag tokens are stripped, so a `--skip-costs` written in the middle of the request text itself is kept as part of the verbatim request, not read as a flag.

## What it needs

- **`$ARGUMENTS` itself, verbatim** — the correction to explore, and the corrective-triple's User prompt block.
- **Recent session context**, to infer the target `command`.
- **`$SPECS_PATH`** — for the specs-preflight/commit-artifacts bookkeeping only.
- **The `superpowers` plugin's `brainstorming` skill**, invoked directly in Phase 3 with no declared install-time dependency — the command simply invokes the skill if it's present.

## What it produces

An `origin: prompt` entry (Friction, User prompt verbatim, Resolution fixed at `Handed off to superpowers:brainstorming to redesign the correction.`), appended via the ladder [Session feedback](../reference/session-feedback.md) describes. **A deferred session-cost record too** — written in Phase 2 alongside the feedback entry, carrying the labels the cost entry will take. It is local and never committed; the next cost-emitting run in the session turns it into a real entry, attributed to the phase whose output you were correcting. See [Session cost](../reference/session-cost.md#spend-a-command-cannot-measure-itself). **The terminal `commit-artifacts` step runs inside Phase 2, before the Phase 3 hand-off** — not after, the way `/feedback` and `/prompt` commit at the very end — because the brainstorming skill takes over the session there, and a commit placed after it would never execute. Session then hands off to `superpowers:brainstorming` to explore and redesign the correction with you.

## Gates

No reviewer of its own — the brainstorming skill's own interactive exploration is what stands in for a review here, not a scored gate this command runs.

## Example

```
/workflows-core:prompt-brainstorm "the /create-ard repo-confirmation prompt keeps re-asking about repos I already declined"
```

The command logs the corrective triple, commits it to the specs repo immediately, and then hands the session to `superpowers:brainstorming` to work out the right fix together.

## See also

- [Session feedback](../reference/session-feedback.md) — the entry format, including the two extra prose blocks a `prompt`-origin entry carries.
- [`/feedback`](feedback.md) — logs a standalone note with no corrective triple.
- [`/prompt`](prompt.md) — the same corrective triple, applied directly instead of explored.
- [`/prompt-grill-me`](prompt-grill-me.md) — the same corrective triple, interrogated inline instead of handed off to a separate skill.
- [Workflow overview](../workflow.md#cross-cutting-commands) — where these four commands sit relative to the role pipeline.
- [`specs-repo-git.md`](../../references/specs-repo-git.md) — the `specs-preflight`/`commit-artifacts` entry points, and why this command's commit runs before its final phase rather than after.

# /prompt

Logs a corrective interaction — a command anywhere in the plugin family produced something wrong and you're fixing it — then performs the correction directly.

## Who runs it

> **Correct through this command, not through a plain prompt.** Replying in the session and talking the model into a better answer gets you the better answer and nothing else. The same correction routed through `/prompt` gets you the identical fixed output *plus* a durable record of the path — the unsatisfactory result, your corrections, and the result you settled on — which is the signal the plugin is actually improved from. See [Session feedback](../reference/session-feedback.md).

`/prompt` runs outside the role pipeline, but it does report its cost: it passes `phase: inferred, role: inferred` and the cost phase **inherits the labels of the command it corrected** (`references/cost-emission.md` §7). Correcting a `/specify` output is priced as `specification`/`pe`; correcting a `/design` output as `planning`/`dev` — the cost of fixing a phase's output belongs to that phase. With no target command it resolves to [`plugin-feedback`](../roles-and-phases.md#plugin-feedback)/`n/a`. [Workflow overview](../workflow.md#cross-cutting-commands) groups it under Plugin improvement, alongside [`/feedback`](feedback.md), [`/prompt-brainstorm`](prompt-brainstorm.md), and [`/prompt-grill-me`](prompt-grill-me.md). Of the three commands that capture a corrective interaction, `/prompt` is the one that just applies the fix — no hand-off, no interrogation. Run it whenever you correct a command's output yourself; logging the correction is what turns a one-off fix into signal the maintainer can act on for every other engineer hitting the same thing.

## Synopsis

```
/prompt <corrective request> [--skip-costs]
```

`--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`, [`environment.md`](../reference/environment.md)) skips this run's session-cost entry, still advancing the checkpoint, and drops any deferred cost record a ceded [`/prompt-brainstorm`](prompt-brainstorm.md) or [`/prompt-grill-me`](prompt-grill-me.md) left pending in this session — naming each dropped record in its output rather than writing its entry (`references/run-flags.md` §5 step 3); it is the only run flag this command applies — `--skip-feedback` and `--enforce-model` are reported ignored, since `/prompt` dispatches no `impl-maintenance` and invokes no model routing.

`$ARGUMENTS`, once the run flag above is stripped, is the corrective request itself, captured **verbatim** as the User prompt block — never paraphrased — save that secrets, home-directory paths, non-public hosts, IP addresses and email addresses are replaced before it is written ([Session feedback](../reference/session-feedback.md#what-is-redacted)). Phase 1 infers which command's output you're correcting from recent context, asking only if genuinely ambiguous; if none applies, it records `n/a`.

Write the flag before or after the request, never inside it: a leading run of flag tokens and a trailing run of flag tokens are stripped, so a `--skip-costs` written in the middle of the request text itself is kept as part of the verbatim request, not read as a flag.

## What it needs

- **`$ARGUMENTS` itself, verbatim** — the correction to apply, and the corrective-triple's User prompt block, verbatim save the redactions above.
- **Recent session context**, to infer the target `command` (or ask once if ambiguous).
- **`$SPECS_PATH`** — for the feedback entry, the session-cost entry, and the specs-preflight/commit-artifacts bookkeeping; the correction itself is applied to your target files directly, wherever they are, never to the specs repo.

## What it produces

Performs the correction directly against your target files — those edits are never staged or committed by this command. It then appends an `origin: prompt` entry (Friction, User prompt verbatim with sensitive values redacted, Resolution — a one-line summary of the fix just applied) via the same specs-first ladder [Session feedback](../reference/session-feedback.md) describes, committed by the terminal `commit-artifacts` step, which pushes it unless the specs repository is on neither its default branch nor a branch the plugin created, has no `origin` that will take the push — none at all, one your git configuration does not push this branch to, or one that deleted or refused the branch — or the push would also publish commits other than the plugin's own session-file commits. On a specs repository whose default branch takes no push, they go to a session branch of your own instead, and you merge its pull request (the `workflows-core` environment page, *A specs repository whose default branch takes no push*).


A **session-cost entry** too, since this command now reports its own spend: `phase`/`role` inherited from the target command, or [`plugin-feedback`](../roles-and-phases.md#plugin-feedback)/`n/a` when there is nothing to inherit. It lands beside the feedback entry under `$SPECS_PATH`, or in the keyless pending file — see [Session cost](../reference/session-cost.md).
## Gates

No reviewer and no fix cycle — `/prompt` **is** the fix, applied once, directly, with nothing downstream to re-check it. Two things can still interrupt it: the specs-repo git guards (`specs-preflight`, `commit-artifacts`, `../../references/specs-repo-git.md`), and — since this command now runs a cost phase and resolves a `key` — the suggest-and-confirm reconciliation offer that fires when keyless cost entries are pending (`../../references/cost-emission.md` §9). A `prompt` entry itself is never silently skipped.

## Example

```
/workflows-core:prompt "design.md skipped the Alternatives considered section — add it back, listing the constraint each declined take optimised for"
```

The command applies the fix to `design.md` directly, confirms the inferred `command` (`/design`), and logs the corrective triple — Friction, your verbatim request with any sensitive value redacted, and the one-line Resolution — to the PRD's feedback file.

## See also

- [Session feedback](../reference/session-feedback.md) — the entry format, including the two extra prose blocks a `prompt`-origin entry carries.
- [`/feedback`](feedback.md) — logs a standalone note with no corrective triple and no fix.
- [`/prompt-brainstorm`](prompt-brainstorm.md) and [`/prompt-grill-me`](prompt-grill-me.md) — the same corrective triple, explored with a brainstorming skill or interrogated inline instead of applied directly.
- [Workflow overview](../workflow.md#cross-cutting-commands) — where these four commands sit relative to the role pipeline.
- [`specs-repo-git.md`](../../references/specs-repo-git.md) — the `specs-preflight` and `commit-artifacts` entry points this command runs.

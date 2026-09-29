# /feedback

Logs a manual note about the plugin family itself — friction you hit, or an improvement you want, in any of its plugins — for the maintainer to aggregate across engineers.

## Who runs it

`/feedback` runs outside the role pipeline, but it does report its cost: it passes `phase: inferred, role: inferred` and the cost phase **inherits the labels of the command the note is about** (`references/cost-emission.md` §7). A note untied to any command — the common case — resolves to [`plugin-feedback`](../roles-and-phases.md#plugin-feedback)/`n/a`. [Workflow overview](../workflow.md#cross-cutting-commands) groups it under Plugin improvement, alongside its three siblings — [`/prompt`](prompt.md), [`/prompt-brainstorm`](prompt-brainstorm.md), and [`/prompt-grill-me`](prompt-grill-me.md). It is tied to no other command and can be run any time, about any friction you hit or improvement you want. This is one of the four commands that make the plugin better over time — use it whenever something is off, not only when it's dramatic; a small annoyance logged now is easier for the maintainer to act on than one nobody ever wrote down.

## Synopsis

```
/feedback [<note>] [--skip-costs]
```

`--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`, [`environment.md`](../reference/environment.md)) skips this run's session-cost entry, still advancing the checkpoint; it is the only run flag this command applies — `--skip-feedback` and `--enforce-model` are reported ignored, since `/feedback` dispatches no `impl-maintenance` and invokes no model routing.

`$ARGUMENTS`, once the run flag above is stripped, is the note text — the friction you hit and the improvement you want, in your own words. Leave it empty and Phase 1 asks for it directly; it never guesses at content you didn't express.

Write the flag before the note, not inside it: only a leading run of flag tokens is stripped, so a `--skip-costs` written inside the note text itself is kept as part of the note, not read as a flag.

## What it needs

- **The note itself** — friction plus a suggested improvement. The command lightly tidies wording but never invents content you didn't say.
- **Confirmed metadata**, resolved in one grouped prompt: `command` (inferred from recent context, or `n/a`), `category` (a controlled, reuse-first vocabulary), and `impact` (`blocker | friction | polish`).
- **`$SPECS_PATH`** — the specs-preflight step at Phase 0 settles the branch before anything is written; it is silent when the repo is already clean and on its default branch.

## What it produces

An `origin: manual` entry appended to the plugin's per-PRD feedback file — see [Session feedback](../reference/session-feedback.md) for the exact entry format and the specs-first ladder that resolves where the file lands; `/feedback` doesn't restate that logic here. The terminal `commit-artifacts` step then commits and pushes it, printed as a `Specs repo:` outcome line. This command never commits into a docs/code repo or the current working directory, where it is not the specs repository — only `$SPECS_PATH`'s bounded artifact paths.


A **session-cost entry** too, since this command now reports its own spend: `phase`/`role` inherited from the target command, or [`plugin-feedback`](../roles-and-phases.md#plugin-feedback)/`n/a` when there is nothing to inherit. It lands beside the feedback entry under `$SPECS_PATH`, or in the keyless pending file — see [Session cost](../reference/session-cost.md).
## Gates

No reviewer and no branch of its own. The only two checkpoints are the specs-repo git guards — `specs-preflight` at the start, `commit-artifacts` at the end (`../../references/specs-repo-git.md`) — and a manual entry is never silently skipped: an `id` collision appends with a numeric suffix and a warning rather than dropping the note.

## Example

```
/workflows-core:feedback "The /specify grill re-asked a question I'd already answered in the ticket description"
```

The command confirms the inferred `command` (`/specify`) and `category`, appends the entry to that PRD's `<KEY>-feedback.md`, and commits it to the specs repo.

## See also

- [Session feedback](../reference/session-feedback.md) — the entry format, the two capture paths, and the specs-first ladder that resolves where a note lands.
- [`/prompt`](prompt.md), [`/prompt-brainstorm`](prompt-brainstorm.md), and [`/prompt-grill-me`](prompt-grill-me.md) — the three sibling commands that log a corrective interaction (`origin: prompt`) rather than a standalone note.
- [Workflow overview](../workflow.md#cross-cutting-commands) — where these four commands sit relative to the role pipeline.
- [`specs-repo-git.md`](../../references/specs-repo-git.md) — the `specs-preflight` and `commit-artifacts` entry points every one of these four commands runs.

# Session feedback

Session feedback is the family's channel for friction about **the plugin itself**, and for defects in the ai-containers environment the family runs in, as distinct from the product it is used to build. `references/feedback-emission.md` is the contract; this page says what the four feedback commands in this plugin put through it. The plugin's fifth emitter, `/frames`, puts through only the automatic end-of-run feedback every long-running command emits, described below.

## What gets logged, and by what

Two different signals, from two different sources:

- [`/feedback`](../commands/feedback.md) logs what you tell it — a note about the plugin, in your own words, for the maintainer to aggregate later.
- [`/prompt`](../commands/prompt.md), [`/prompt-brainstorm`](../commands/prompt-brainstorm.md) and [`/prompt-grill-me`](../commands/prompt-grill-me.md) capture a **correction**: the bad result a command produced, what you told it instead, and the good result that came out of it. The three differ only in what happens after the log — `/prompt` applies the fix directly, `/prompt-brainstorm` hands off to `superpowers:brainstorming` to redesign it, `/prompt-grill-me` grills the fix inline.

### Why `/prompt*` is the more valuable of the two

A `/feedback` note is a report. A `/prompt*` entry is a worked example: it carries the exact input (with any sensitive value redacted, below), the exact wrong output, and the exact correction, which is what a later fix to a command's instructions can actually be tested against. Both are worth logging; only one of them can be replayed.

Every long-running command in the family also emits session feedback automatically at the end of its run, so the channel is not fed by these four commands alone.

## What is redacted

Every entry is redacted before it is written, because it is committed and pushed to the specs repository, where everyone with access reads it. Secrets become `[SECRET-n]`: private keys, tokens of a known shape, a password in a URL, an `Authorization` value, and a literal assigned to a `*_KEY`, `*_TOKEN`, `*_SECRET` or `PASSWORD` name. Home-directory paths become `~/…`. Private and routable IP addresses, and hosts that are not a publicly reachable service's, become `[HOST-n]`; `localhost`, loopback and other local addresses stay. Email addresses become `[EMAIL-n]`. Everything around a placeholder stays as written, so a `/prompt*` entry's User prompt is still verbatim in every other character. The `author` field keeps your git email, because it is the entry's attribution. The run reports what it redacted, by category and count, beside the path it wrote. `workflows-core:feedback-emission` §1.1 has the full list.

## Where files land

Feedback writes **one file per folder**, not one per session — the opposite of the cost subsystem's split, because feedback is read as a stream about a plugin rather than measured per run. The resolution ladder is the same as cost's: a resolved folder in `$SPECS_PATH` first, a pending location where no folder resolves, and report-only where nothing does. On a run carrying `specs_git: misrooted`, meaning the run found `$SPECS_PATH` misplaced in any of the cases [Environment](environment.md) describes (`workflows-core:specs-repo-git` §3.1 is the authority on them), the entry stays in the run's printed output instead, whatever else resolves, so nothing is written under a path the run found wrong. Nothing is committed by the emitting phase itself; the run's terminal artifact commit picks it up with everything else it wrote.

## Bugs only (`--skip-feedback`)

`--skip-feedback` (or `$WORKFLOWS_SKIP_FEEDBACK`) narrows the automatic maintenance phase to bug capture only. It applies to every command whose maintenance phase dispatches `impl-maintenance` — in this plugin, that is `/frames` alone; `/feedback`, `/prompt`, `/prompt-brainstorm` and `/prompt-grill-me` never dispatch `impl-maintenance`, so the flag has nothing to narrow on them. Under the flag, `/frames` dispatches `defect-reporter` instead, on `references/model-routing/classification.md` §2.1's Sonnet chain (or the run's enforced model) — the same compact session handoff plus a `Plugin root:` line (the dispatching command's own plugin directory, where `defect-reporter` looks for the command, reference or agent file a candidate defect names), but returning only real defects: a wrong or self-contradictory instruction, a broken script, gate or hook, a missing or wrong reference, a command contradicting its own documentation, a crash, or a defect in the ai-containers environment the family runs in (a missing tool, a wrong mount, a bad default). Everything else the in-session Lessons Learned report would otherwise surface — friction, wishes, polish, target-project tooling advice, and every non-defect observation — is dropped; nothing is written for it.

Any defect `defect-reporter` returns lands through `emit-bugs` in the same `<KEY>-feedback.md` file, in the same entry format, `origin: auto`, `category: environment-defect` for a container-environment location and the usual §1 vocabulary otherwise. A run with no defects loads `references/feedback-emission.md` not at all and writes nothing. The run reports `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of the usual persisted-path line.

## What a correction costs

A `/prompt*` or `/feedback` run is charged to the phase of the command it is correcting, not to a phase of its own — see [Roles and phases](../roles-and-phases.md#plugin-feedback) for the inheritance rule and the `plugin-feedback` fallback, and [Session cost](session-cost.md) for the mechanics.

The entry format, the ladder's exact tiers, and the automatic-emission contract live in `references/feedback-emission.md`, which is the single source of truth this page describes rather than restates.

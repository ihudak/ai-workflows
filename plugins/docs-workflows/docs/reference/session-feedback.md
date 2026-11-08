# Session feedback

Session feedback is the family's channel for friction about **the plugin family itself**, and for defects in the ai-containers environment the family runs in — never about the product you are documenting. The emitter, its entry format and its file ladder belong to the companion `workflows-core` plugin: its feedback-emission reference is the contract, and its own Session feedback page describes the four commands that log feedback you give by hand. This page says what this plugin's own commands put through it, and where it lands.

## Which commands emit it

Five commands end with an automatic feedback step, after their report — save `/document`, whose maintenance phase comes before its report:

| Command | Step |
|---|---|
| [`/document`](../commands/document.md) | Phase 8 in keyed mode, Phase 4 in direct mode — the fourth of the four maintenance agents |
| [`/release-notes`](../commands/release-notes.md) | Phase 9 |
| [`/docs-init`](../commands/docs-init.md) | Phase 9 |
| [`/docs-audit`](../commands/docs-audit.md) | Phase 7 |
| [`/docs-brand`](../commands/docs-brand.md) | Phase 12, standalone only — an `--inline` run has no tail of its own, and the `/docs-init` that ran it covers it |

Each step dispatches `workflows-core`'s `impl-maintenance` agent on the Sonnet chain ([Model routing](model-routing.md)) and keeps only the plugin-facing slice of its Lessons Learned report: command workflow improvements, new agents or skills the plugin should offer, gaps in the plugin's own reference docs, the plugin's own rules a run did not follow, the key observations behind them, and any defect in the ai-containers environment, logged as `category: environment-defect`. Advice about the documentation repository you were working in — a `CLAUDE.md` rule, a hook — stays in the run's report. A run with nothing plugin-facing to report writes nothing, and an automatic entry already in the file, by its stable `id`, is skipped rather than logged twice. Nothing is asked: capture is silent.

`/document` and `/release-notes` also capture at a block: a run that halts because the plugin lacked something it needed, or because the ai-containers image lacks a tool it is meant to provide, writes one `impact: blocker` entry before it stops. A review that blocks the work, a missing repository, a dirty tree, a cancellation or a stop on your own specs tree is not a plugin gap and writes nothing.

[`/docs-profile`](../commands/docs-profile.md) and [`/docs-serve`](../commands/docs-serve.md) emit no feedback: neither dispatches `impl-maintenance`.

## Where it lands

- **A run that resolved a folder in the specs tree** — keyed `/document` and `/release-notes` — appends to `<PRD-dir>/dev-workflows/<KEY>-feedback.md`, one file per PRD; an Epic's run files under the PRD folder above it.
- **A documentation run with no PRD folder** — `/docs-init`, `/docs-audit`, a standalone `/docs-brand`, and `/document` in direct mode, the mode that takes no address — appends to `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/feedback/<date>.md`, one file per documentation repository per day. `<docs-repo-slug>` is the repository's `origin` remote flattened to one path segment (`git@github.com:acme/docs.git` gives `acme-docs`), or its directory name where it has no `origin`; for direct mode, it is the repository the run edited. The inner `dev-workflows/` names the family, not this plugin.
- **No `$SPECS_PATH`**: the shared ladder's lower tiers apply — beside a directory the run was handed, or, where nothing resolves, in the run's printed output only. The feedback is never written into your current working directory.

A run that found `$SPECS_PATH` misplaced, or found its environment changed since its preflight printed it ([Environment](environment.md)), writes nothing there and keeps the entries in its printed output instead. The feedback step never commits: the run's terminal commit to the specs repository picks the file up with its other session files, and never touches the documentation repository.

## What is redacted

Every entry is redacted before it is written, because it is committed and pushed to the specs repository, where everyone with access reads it. Secrets become `[SECRET-n]`: private keys, tokens of a known shape, a password in a URL, an `Authorization` value, and a literal assigned to a name or flag ending in key, token, secret or password. Home-directory paths become `~/…`. Private and routable IP addresses, and hosts that are not a publicly reachable service's, become `[HOST-n]`; `localhost` and loopback stay. Email addresses become `[EMAIL-n]`. The `author` field keeps your git email, because it is the entry's attribution. The run reports what it redacted, by category and count, beside the path it wrote.

## Bugs only (`--skip-feedback`)

`--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows the feedback step of the five commands above to bug capture. The step dispatches `workflows-core`'s `defect-reporter` in place of `impl-maintenance`, on the same Sonnet chain or the run's enforced model, with the same session handoff plus a `Plugin root:` line naming this plugin's own directory, where it looks for the command, reference or agent file a candidate defect names. It returns only real defects — a wrong or self-contradictory instruction, a broken script, gate or hook, a missing or wrong reference, a command contradicting its own documentation, a crash, or a defect in the ai-containers environment — and drops friction, wishes and polish. Any defect it returns lands in the same file as above, `origin: auto`; a run with none writes nothing. The run reports `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of the persisted path.

What you lose is the Lessons Learned report itself, so the advice about your documentation repository — a `CLAUDE.md` rule, a hook — that would stay in the run's report is not produced. Nothing else changes: `/document`'s other three maintenance agents still run, capture at a block still fires, and the follow-up, cost and resume steps run as before. `/docs-profile` and `/docs-serve` report the flag as ignored.

## See also

- [Session cost](session-cost.md) — the cost entry the same runs write, under the same folders.
- [Resume and checkpoints](resume-and-checkpoints.md) — the resume pointer two of these commands write after their cost entry.
- [Roles and phases](../roles-and-phases.md) — the phase a correction made through `workflows-core`'s `/prompt` commands is charged to.

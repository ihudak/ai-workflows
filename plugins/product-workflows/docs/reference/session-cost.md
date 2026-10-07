# Session cost

Cost attribution is one of the subsystems the companion `workflows-core` plugin holds: its `cost-emission` reference and the price table beside it are what every plugin in the family reads, and its `session-cost.py` script does the arithmetic. This page documents the subsystem from the side that invokes it — what a command here declares, and what each of the fourteen cost-emitting commands *in this plugin* charges to.

## What a command declares

Every cost-emitting command passes a `phase` and a `role` label at the point it calls the shared entry point, and `workflows-core:cost-emission` §7 carries one attribution row per command. Fourteen commands emit a cost entry here, unless `--skip-costs` ([below](#skipping-cost---skip-costs)) — every command in this plugin but `/harvest-decisions` and `/promote-decisions`, which work on the team architecture knowledge base rather than advance a PRD- or BRD-scoped artifact (`workflows-core:cost-emission` §7) — and all with a fixed pair rather than an inferred one:

| Command(s) | Phase | Role |
|---|---|---|
| `/idea`, `/create-prd` | `prd-creation` | `pm` |
| `/update-prd` | `prd-update` | `pm` |
| `/brd-intake`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile` | `brd-to-prd` | `pm` |
| `/prd-ground` | `brd-to-prd` | `pa` |
| `/create-ard` | `architecture` | `pa` |
| `/epics` | `epic-refinement` | `pe` |
| `/specify` | `specification` | `pe` |
| `/prd-proposal`, `/brd-proposal` | `proposal` | `pm` |

`brd-to-prd` is the one phase shared across two roles: every command of the BRD-to-PRD route runs as PM except `/prd-ground`, which is PM-initiated but PA/Dev-executed, and both roles tag their cost line `brd-to-prd`. [Roles and phases](../roles-and-phases.md) defines what each phase means and what a run in it is accountable for; this page states only what each command passes.

## Skipping cost (`--skip-costs`)

Under `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`), a command's cost phase never calls `emit-cost` and never loads `workflows-core:cost-emission` — it runs `workflows-core:run-flags`'s `skip-cost` entry point in its place. The checkpoint still advances exactly as a full run would, so the next command's window is measured correctly; nothing else happens — no cost entry, no pending file, no reconciliation offer. Any deferred record from a prior ceded `/prompt-brainstorm` or `/prompt-grill-me` run is dropped rather than replayed: the skipping run names each dropped record in its output and deletes the deferred file, since the checkpoint has already moved past what it could have matched.

The run reports `Session cost: skipped (--skip-costs)` or `Session cost: skipped (WORKFLOWS_SKIP_COSTS)` in place of the usual persisted-path line.

## Where cost files land

Cost writes to a `cost/` subdirectory with one file per session — `<PRD-dir>/dev-workflows/cost/<sid8>.md`, named after the first eight characters of the session id — so no two engineers' commands can collide in one file. That folder name is a fixed, family-wide constant shared by every plugin's cost, feedback, and resume bookkeeping, not a `product-workflows`-specific path; the sibling `docs-workflows` plugin's own commands write into the identical folder name. Where no folder resolves, the entry goes to a pending file under `$SPECS_PATH` and is offered for relocation once a real key is known; where nothing resolves at all, it stays in the run's printed output. On a run carrying `specs_git: misrooted`, meaning the run found `$SPECS_PATH` misplaced in any of the cases [Environment](environment.md) describes (`workflows-core:specs-repo-git` §3.1 is the authority on them), the entry stays in the run's printed output instead, whatever else resolves, so nothing is written under a path the run found wrong. The plugin never writes into your current working directory, where it is not the specs repository.

None of this touches git directly — the entry is committed later, once, by the run's terminal `commit-artifacts` step — and pushed by it, unless the specs repository is on neither its default branch nor a branch the plugin created, has no `origin` that will take the push — none at all, one your git configuration does not push this branch to, or one that deleted or refused the branch — or the push would also publish commits other than the plugin's own session-file commits — bounded to the session-artifact paths inside `$SPECS_PATH`. On a specs repository whose default branch takes no push, they go to a session branch of your own instead, and you merge its pull request (the `workflows-core` environment page, *A specs repository whose default branch takes no push*).

## How cost is computed and what a figure covers

The script reads the assistant-turn `usage` and `model` fields already present in the session's main transcript, plus every subagent transcript dispatched during the window being measured, sums token counts per model, and multiplies by the price table in effect. Claude Code's own running dollar total reaches the transcript only now and then — a `cost-state` record between sessions, never at a command's edges — so cost is always **computed** rather than read. It drifts from Claude Code's own accounting by the accuracy of that table, and by every compaction in the window, which Claude Code bills but records no token usage for: the entry's `compactions:` field counts those the computed figure leaves out. Override the bundled table with `$DEV_WORKFLOWS_COST_PRICES`, a variable the companion `workflows-core` plugin reads and documents — the name is the same family-wide constant as the cost folder itself, not a `product-workflows`-specific setting.

The window is **chained, not fixed**: a small local checkpoint file, keyed by session id and never committed, records where the last cost phase left off, and the next one picks up exactly there. A session that runs `/create-prd` and then hands off to `/create-ard` produces two entries whose windows are contiguous — and the replaying run may be in another plugin, which after the marketplace split it often is.

**A claim only resolves onto a command of this family.** The deferred claim is matched against a manifest of the family's own `<plugin>:<command>` names, so a command from another marketplace ends the open window — its spend is its own — without ever being claimable. A claim it interrupts is reported as unmatched and dropped, never quietly attached to it. `workflows-core:cost-emission` §13 owns the rule. The full mechanics, the entry format, and the §7 attribution table itself live in `workflows-core:cost-emission`, which this page describes rather than restates.

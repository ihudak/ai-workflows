# Session cost

Cost attribution is one of the subsystems the companion `workflows-core` plugin holds: its shared cost-emission reference and the price table beside it are what every plugin in the family reads, and its `session-cost.py` script does the arithmetic. This page documents the subsystem from the side that invokes it: what the command here declares, what it charges to, and where its entry lands.

## What a command declares

Every cost-emitting command charges its run to a `phase` and a `role`. A command that cannot label itself in advance leaves both to be resolved at its cost phase, from the run's own context.

One command emits a cost entry here, unless `--skip-costs` ([below](#skipping-cost---skip-costs)): `/security-workflows:scan`, with `phase: security-audit` and the run's role — `dev` for a key run without `--triage` or `--verify-fixes`, `sec` otherwise.

The scan cannot label its role in advance, so it works out the run's role as it goes — `dev` for a key run without `--triage` or `--verify-fixes`, which is the Dev's pre-merge scan or an `--import` for a unit, and `sec` for every other run — and hands it to the cost phase, which charges the run to `security-audit` under that role. The role is handed over rather than read back because it cannot be read from disk: the run record that carries it is written only by a run that changed the register, and a run that stopped, or recorded a scan the register already held, wrote none. A role that is missing or carries any other value is recorded as `n/a`, never guessed.

**A correction to a scan run is charged to the same phase, without a role.** `/workflows-core:prompt`, `/workflows-core:feedback`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me` inherit the labels of the command they correct, but the scan's role lives in the scan run's own context and reaches none of them, so a correction of `/security-workflows:scan` is `security-audit`/`n/a`. `n/a` is the absence of a role, recorded rather than guessed.

## Skipping cost (`--skip-costs`)

Under `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`), the run computes no cost. The checkpoint still advances exactly as a full run would, so the next command's window is measured correctly; nothing else happens, no cost entry and no pending file. Any deferred record from a prior [ceded](#ceded-runs) `/prompt-brainstorm` or `/prompt-grill-me` run is dropped rather than replayed: the skipping run names each dropped record in its output and deletes the deferred file, since the checkpoint has already moved past what it could have matched.

The run reports `Session cost: skipped (--skip-costs)` or `Session cost: skipped (WORKFLOWS_SKIP_COSTS)` in place of the usual persisted-path line.

## Where cost files land

Cost writes to a `cost/` subdirectory with one file per session, named after the first eight characters of the session id, so no two engineers' commands can collide in one file.

- **A run addressed by a key** files its entry under the unit's PRD folder, `<PRD-dir>/dev-workflows/cost/<sid8>.md`, as every keyed run in the family does, wherever its key resolved. For an Epic, that is the PRD folder above it, so the scan's spend lands beside the specification, design and implementation runs that preceded it. A key that resolved no folder — a run that stopped at its address — leaves the entry in a pending file under `$SPECS_PATH`, offered for relocation once a real key is known.
- **A run addressed by a repository path**, whatever its mode, never acquires a key, so it never takes the pending file a keyless run elsewhere waits in. It files its entry per code repository, at `$SPECS_PATH/security/<repo-slug>/dev-workflows/cost/<sid8>.md`, beside the register and never part of it: the register reads only its `runs/` and `scans/`. Where the run resolved no `<repo-slug>`, a path that is no repository or a repository with no `origin`, on a run that stopped before it resolved one, the entry stays in the run's printed output.
- **A run that found `$SPECS_PATH` misplaced, or its environment changed since its preflight printed it** ([Environment](environment.md)), keeps the entry in its printed output, whatever else resolves, so nothing is written under a path the run found wrong.

**A run that stops still records its cost.** Each `SECURITY_*` stop, the address and `$SPECS_PATH` stops, a `register.py` refusal before the run's record is written, and each answer that ends the run take the refusal tail: the cost entry, unless `--skip-costs`, and the terminal commit, with no resume pointer and no maintenance phase ([`/security-workflows:scan`](../commands/scan.md), *Stops*).

None of this touches git directly. The entry is committed later, once, by the run's terminal `commit-artifacts` step, bounded to the session-artifact paths inside `$SPECS_PATH`, and pushed by it under the same conditions as every session file. On a specs repository whose default branch takes no push, it goes to a session branch of your own instead, and you merge its pull request.

## How cost is computed and what a figure covers

The script reads the assistant-turn `usage` and `model` fields already present in the session's main transcript, plus every subagent transcript dispatched during the window being measured, sums token counts per model, and multiplies by the price table in effect. **That includes Claude Security's own agents.** Claude Security runs its scan as a dynamic workflow, whose agents write their transcripts under the session's subagent directory, in `workflows/<run-id>/`, and the script reads those too, so a scan's entry carries the scan itself and not only the run around it. Claude Code's own running dollar total reaches the transcript only now and then, so cost is always **computed** rather than read, and it drifts from Claude Code's own accounting by the accuracy of the price table and by every compaction in the window, which the entry's `compactions:` field counts.

The window is **chained, not fixed**: a small local checkpoint file, keyed by session id and never committed, records where the last cost phase left off, and the next one picks up exactly there. A session that runs `/dev-workflows:conformance` and then this command produces two entries whose windows are contiguous. The `cost-emission` reference owns the full mechanics, the entry format and the attribution table itself, which this page describes rather than restates.

### Ceded runs

A **ceded** run is a run of `/prompt-brainstorm` or `/prompt-grill-me`, two commands of the companion `workflows-core` plugin. Each hands the session over at its Phase 3 — to a brainstorming skill, or to a long interactive grill — and never gets it back (a `/prompt-brainstorm` run that finds the brainstorming skill not installed ends there instead), so it cannot write its own cost entry: it records what it would have claimed, and the next cost-emitting run in the same session writes the entry on its behalf. A scan that is the first cost-emitting run after a ceded one in the session is that run: it carves the ceded run's share out of its own window and files it as the ceded run's own entry, under the key that run recorded — or, under `--skip-costs`, drops it, as above.

# Session cost

Cost attribution is one of the subsystems the companion `workflows-core` plugin holds: its `cost-emission` reference and the price table beside it are what every plugin in the family reads, and its `session-cost.py` script does the arithmetic. This page documents the subsystem from the side that invokes it: what the command here declares, what it charges to, and where its entry lands.

## What a command declares

Every cost-emitting command passes a `phase` and a `role` label at the point it calls the shared entry point, and `workflows-core:cost-emission` §7 carries one attribution row per command. A command that cannot label itself in advance passes `phase: inferred, role: inferred` and lets the cost phase resolve the real values from the run's own context.

One command emits a cost entry here, unless `--skip-costs` ([below](#skipping-cost---skip-costs)): `/security-workflows:scan`, with `phase: security-audit` and the run's role — `dev` for a key run without `--triage` or `--verify-fixes`, `sec` otherwise. Its §7 row names it by its bare name, `/scan`.

The command passes `phase: inferred, role: inferred`, and with them the run's role as `run_role`: `dev` for a key run without `--triage` or `--verify-fixes`, which is the Dev's pre-merge scan or an `--import` for a unit, and `sec` for every other run. The cost phase resolves the phase to `security-audit` and the role from `run_role`. The role is passed rather than read because it cannot be read from disk: the run record that carries it is written only by a run that changed the register, and a run that stopped, or recorded a scan the register already held, wrote none. A `run_role` missing or carrying any other value is recorded as `n/a`, never guessed.

**A correction to a scan run is charged to the same phase, without a role.** `/workflows-core:prompt`, `/workflows-core:feedback`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me` inherit the labels of the command they correct, but `run_role` lives in the scan run's own context and reaches none of them, so a correction of `/security-workflows:scan` is `security-audit`/`n/a`. `n/a` is the absence of a role, recorded rather than guessed.

## Skipping cost (`--skip-costs`)

Under `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`), the run never calls `emit-cost` and never loads `workflows-core:cost-emission`: it runs `workflows-core:run-flags`'s `skip-cost` entry point in its place. The checkpoint still advances exactly as a full run would, so the next command's window is measured correctly; nothing else happens, no cost entry and no pending file. Any deferred record from a prior ceded `/prompt-brainstorm` or `/prompt-grill-me` run is dropped rather than replayed: the skipping run names each dropped record in its output and deletes the deferred file, since the checkpoint has already moved past what it could have matched.

The run reports `Session cost: skipped (--skip-costs)` or `Session cost: skipped (WORKFLOWS_SKIP_COSTS)` in place of the usual persisted-path line.

## Where cost files land

Cost writes to a `cost/` subdirectory with one file per session, named after the first eight characters of the session id, so no two engineers' commands can collide in one file.

- **A run addressed by a key** files its entry under the unit's PRD folder, `<PRD-dir>/dev-workflows/cost/<sid8>.md`, as every keyed run in the family does, wherever its key resolved. For an Epic, that is the PRD folder above it, so the scan's spend lands beside the specification, design and implementation runs that preceded it. A key that resolved no folder — a run that stopped at its address — leaves the entry in a pending file under `$SPECS_PATH`, offered for relocation once a real key is known (`workflows-core:cost-emission` §8–§9).
- **A run addressed by a repository path**, whatever its mode, never acquires a key, so it never takes the pending file a keyless run elsewhere waits in. It files its entry per code repository, at `$SPECS_PATH/security/<repo-slug>/dev-workflows/cost/<sid8>.md`, beside the register and never part of it: the register reads only its `runs/` and `scans/`. Where the run resolved no `<repo-slug>`, a path that is no repository or a repository with no `origin`, on a run that stopped before it resolved one, the entry stays in the run's printed output.
- **A run carrying `specs_git: misrooted`**, a `$SPECS_PATH` the run found misplaced, or an environment that changed since its preflight printed it ([Environment](environment.md)), keeps the entry in its printed output, whatever else resolves, so nothing is written under a path the run found wrong.

**A run that stops still records its cost.** Each `SECURITY_*` stop, the address and `$SPECS_PATH` stops, a `register.py` refusal before the run's record is written, and each answer that ends the run take the refusal tail: the cost entry, unless `--skip-costs`, and the terminal commit, with no resume pointer and no maintenance phase ([`/security-workflows:scan`](../commands/scan.md), *Stops*).

None of this touches git directly. The entry is committed later, once, by the run's terminal `commit-artifacts` step, bounded to the session-artifact paths inside `$SPECS_PATH`, and pushed by it under the same conditions as every session file. On a specs repository whose default branch takes no push, it goes to a session branch of your own instead, and you merge its pull request.

## How cost is computed and what a figure covers

The script reads the assistant-turn `usage` and `model` fields already present in the session's main transcript, plus every subagent transcript dispatched during the window being measured, sums token counts per model, and multiplies by the price table in effect. **That includes Claude Security's own agents.** Claude Security runs its scan as a dynamic workflow, whose agents write their transcripts under the session's subagent directory, in `workflows/<run-id>/`, and the script reads those too, so a scan's entry carries the scan itself and not only the run around it. Claude Code's own running dollar total reaches the transcript only now and then, so cost is always **computed** rather than read, and it drifts from Claude Code's own accounting by the accuracy of the price table and by every compaction in the window, which the entry's `compactions:` field counts.

The window is **chained, not fixed**: a small local checkpoint file, keyed by session id and never committed, records where the last cost phase left off, and the next one picks up exactly there. A session that runs `/dev-workflows:conformance` and then this command produces two entries whose windows are contiguous. `workflows-core:cost-emission` owns the full mechanics, the entry format and the §7 attribution table itself, which this page describes rather than restates.

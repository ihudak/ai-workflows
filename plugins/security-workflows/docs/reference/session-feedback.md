# Session feedback, follow-ups and resume

After its report, [`/security-workflows:scan`](../commands/scan.md) runs a tail in a fixed order: the maintenance agents and session feedback, the follow-ups, the maintenance proposals you consent to, the cost entry, the resume pointer, and the terminal commit of the specs repository. This page says where the feedback, the follow-ups and the resume pointer go, and what `--skip-feedback` keeps. The cost entry is on [Session cost](session-cost.md). The emitters themselves belong to the companion `workflows-core` plugin: its feedback-emission, follow-up-emission and session-hygiene references.

**A run that ends early has none of this.** A `SECURITY_*` stop, an address stop, a `register.py` refusal before the run's record is written, or an answer that ends the run takes a short tail — the cost entry and the terminal commit — with no maintenance phase, so no feedback, no follow-up and no resume pointer.

## Session feedback

Session feedback is about **the plugin family itself**, and defects in the ai-containers environment it runs in — never about the code you scanned. The session-maintenance agent, `workflows-core`'s `impl-maintenance`, returns a Lessons Learned report, and the run keeps only its plugin-facing slice: command workflow improvements, new agents or skills, gaps in the plugin's references, the plugin's own rules the run did not follow, the key observations behind them, and any ai-containers defect, as `category: environment-defect`. A run with nothing plugin-facing writes nothing, and nothing is asked. On a run that recorded nothing in the register, that agent runs alone, without the documentation, knowledge-base and instructions agents.

Where the entry lands depends on the address:

- **A key, or an `@<path>` to the unit's folder:** `<PRD-dir>/dev-workflows/<KEY>-feedback.md`, one file per PRD; an Epic's run files under the PRD folder above it.
- **A repository path:** there is no PRD folder, so the entry goes to `$SPECS_PATH/dev-workflows-feedback/<date>.md` at the top of the specs repository, marked unfiled. Unlike the cost entry, which this run files under `security/<repo-slug>/`, feedback has no per-repository folder.

A run that found `$SPECS_PATH` misplaced, or its environment changed since its preflight printed it, keeps the entry in its printed output and writes nothing. Every entry is redacted before it is written — secrets become `[SECRET-n]`, home-directory paths `~/…`, private hosts and addresses `[HOST-n]`, email addresses `[EMAIL-n]` — and the run says what it redacted. The terminal commit carries the file with the run's other session files.

### Bugs only (`--skip-feedback`)

`--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) replaces the session-maintenance agent with `workflows-core`'s `defect-reporter`, on the Sonnet chain or the run's enforced model, given the same handoff plus a `Plugin root:` line naming this plugin's directory. It keeps only real defects — a wrong or self-contradictory instruction, a broken script, gate or hook, a missing or wrong reference, a command contradicting its own documentation, a crash, or an ai-containers defect — and drops friction, wishes and polish. Any defect lands in the same file as above; a run with none writes nothing. The run reports `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects`.

Nothing else in the tail changes: the other three maintenance agents run where they would, and every later step runs as before.

## Follow-ups

`register.py commit` builds one line for each finding marked fix, from structured fields only — its `[SEC#n]`, a CWE number, a `path:line`, and the patch recorded for the finding, where there is one — never from a finding's text, which is scan output.

- **On a key run**, the report lists the lines as pending, and the tail then shows them in a preview you approve, select from or cancel, before writing them to `follow-ups.md` in the unit's folder. `/dev-workflows:implement <KEY>` reads them back, continuing on the Epic's branch while its pull request is open. A line the preview leaves out returns its finding to `fix`, through a second, small run record, and the next run of the unit offers it again. A line is written only once: an open line carrying the same `[SEC#n]` for the same repository and unit stands for it.
- **On a repository path**, there is no unit to write into. The lines are `/dev-workflows:implement` prompt lines in the report's `### Next step`, each that names a patch followed by that patch's absolute path, and nothing is written.

## The resume pointer

A key run writes `resume.md` under the PRD folder's `dev-workflows/` — for an Epic, the PRD folder above it — after the cost entry and before the terminal commit, which carries it. It is a "last known position", overwritten on every run: what ran last, the artifact, the next step from the report, and a *Carry-forward decisions* line. The scan is not among the commands that suggest a `/rename`, so the pointer carries no suggested session name. A run on a repository path has no PRD folder and writes no pointer, and neither does a run that ended early or found its environment misplaced.

**One pointer serves the whole PRD folder**, written by every run of every Epic and role under it. Before writing, the run reads the pointer it replaces and carries each item that is not settled yet, by a check that fetches and writes nothing.

**The Security Engineer offers stay until a Security Engineer runs them.** The pointer takes each `--verify-fixes` and `--triage` offer from the report's `### Next step`, with its register, `security/<repo-slug>/`, beside the repository path, since the pointer is shared across machines and the path may be no repository on another one. The offer is settled only by a run record of its own mode — role `sec`, kind `verify` for `--verify-fixes` or `triage` for `--triage` — in that register's `runs/`, later than the time the run that offered it completed, which the pointer keeps beside the offer for as long as it carries it. Your own next change scan of the Epic, or a run of the other mode, leaves it standing; so does a Security Engineer run that recorded nothing, or whose record has not reached your specs checkout yet. An offer an older release wrote without a register is kept until a run on a machine where its path is that repository can settle it.

**A worktree path is never written into the pointer.** A temporary worktree the run failed to remove belongs to one machine, while the pointer is shared, so the report names it instead, and the next run's setup offers to remove it once it is idle.

## See also

- [`/security-workflows:scan`](../commands/scan.md) — the whole run, its tail included.
- [Roles and phases](../roles-and-phases.md) — the Dev and the Security Engineer the offers name.
- [Security register](security-register.md) — how a follow-up moves a finding between `fix` and `fixing`.

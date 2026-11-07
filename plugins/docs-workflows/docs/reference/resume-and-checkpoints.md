# Resume and checkpoints

A pipeline command ends by doing two separate things: it writes a small pointer file recording where things stand, then it suggests — never performs — the right context action for what comes next, `/compact`, `/clear` or a session `/rename`. The mechanism is shared across the family and belongs to the companion `workflows-core` plugin's session-hygiene reference; this page says what this plugin's seven commands do with it, and names the one other piece of state a command here keeps between runs.

## Which commands write `resume.md`

Two, both on a PRD folder: [`/document`](../commands/document.md) in keyed mode and [`/release-notes`](../commands/release-notes.md). Each writes `<PRD-dir>/dev-workflows/resume.md` in its terminal cost phase, Phase 11 — after its cost entry, so the pointer reflects the completed run, and before the terminal commit, so the pointer is committed and pushed with the run's other session files. An Epic's run writes the pointer of the PRD folder above it. The write happens under `--skip-costs` too.

The others write none:

- **`/docs-init`, `/docs-audit` and a standalone `/docs-brand`** run the resume-pointer step, but resolve no PRD folder, so the shared rule's second rung applies: no file, and the printed `### Next step` is the record. An `--inline` `/docs-brand` has no tail of its own.
- **`/document` in direct mode** takes no address, so it has no PRD folder to anchor a pointer to, and is on the shared skip list.
- **`/docs-profile` and `/docs-serve`** have no resume step at all.

A run that found `$SPECS_PATH` misplaced, or found its environment changed since its preflight printed it ([Environment](environment.md)), writes no pointer either. Where `$SPECS_PATH` is not writable, the file is skipped with a one-line warning to set it.

## What it holds

The pointer is a "last known position", overwritten on every run rather than appended to, and kept tiny:

```markdown
# Resume — <KEY>[ / <EPIC-KEY>] (<role>)

- **Last completed:** <command> <args> — <phase or 'command complete'> (<ISO datetime with its UTC offset>)
- **Artifact:** <relative path to the deliverable just written/committed, or 'none (read-only)'>
- **Next step:** <the exact next command from ### Next step, or 'PRD fully processed'>
- **Suggested session name:** <KEY>-<slug>-<role>
- **Carry-forward decisions:** <0–N one-line items; 'none' if none>
```

**Overwritten, but nothing open is dropped.** A PRD folder holds one pointer, written by every run of every Epic and every role under it, so before it writes, the run reads the pointer it is replacing. Each item that pointer carried, and each open item of its *Next step* that this run's *Next step* does not name, goes into the new *Carry-forward decisions* line unless it is settled — by this run, or by a check of what the item waits on that fetches and writes nothing: a merge, a push, a ticked follow-up or a later record of the command it asks for, among others. An item the check cannot settle is carried, never dropped. An item asking for a command keeps the `(waiting since <ISO datetime>)` it was first written with. Anything secret or personal that could land in that line is redacted before writing: a pointer records what to do next, never a sensitive value.

In a fresh session, read the pointer to see what ran last, what it produced and what to run next, instead of scrolling back through a compacted or cleared transcript.

## The suggestion: `/compact`, `/clear` and `/rename`

Both commands end their report with a `### Context hygiene` block — guidance only, never run for you:

- **Keyed `/document`** suggests `/compact` before going on to `/release-notes` for the PRD, since that run is still the Dev's, and `/rename <PRD-ID>-<slug>-dev`.
- **`/release-notes`** suggests nothing where the PRD is fully processed, `/clear` before switching roles where an architecture or Epic phase is still pending for the PRD, and `/rename <PRD-ID>-<slug>-<role>`, `<role>` being `pm` on the early run and `dev` on the late one ([Roles and phases](../roles-and-phases.md)).

Direct-mode `/document`, `/docs-init`, `/docs-audit`, `/docs-brand`, `/docs-profile` and `/docs-serve` print no such block.

## Checkpoints

- **The cost checkpoint.** Every cost-emitting run here advances a small local file, keyed by session id and never committed, that records where the last cost phase left off, so the next run's cost window starts there — `--skip-costs` included. [Session cost](session-cost.md) describes it.
- **`/docs-serve`'s run state.** `/docs-serve` records each server it starts in `.dev-workflows/docs-serve.state.json` in the documentation repository, keyed by the port the server bound, with its process, process group and log. A later `/docs-serve` reads it to find a server already running, and `--status` and `--stop` read it to report or end one. It is local bookkeeping: never staged, never committed, and kept out of `git status` by an ignore line for the file alone, since `.dev-workflows/` also holds the committed profile.

None of this plugin's commands keeps a session file to resume a half-finished run from.

## See also

- [Session feedback](session-feedback.md) — the step that runs before the cost entry and the pointer.
- [Session cost](session-cost.md) — the cost entry the pointer follows, and the checkpoint it advances.

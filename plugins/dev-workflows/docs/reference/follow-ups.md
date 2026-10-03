# Follow-ups

A follow-up is a line written into the specs tree for something a command's run surfaced but could
not finish itself — a manual publish step, an edit somebody else owns, a gap between the PRD and the
code. It outlives the session, which is the whole reason it is written down rather than just
reported.

## The line

Plain markdown, in a plain checklist:

    - [ ] <one imperative line naming the out-of-scope action> — <why it is out of scope>

No effort symbols, no priority glyphs, no tags, no dates. **That is a simplification, not an
omission**: this used to render an Obsidian-Tasks line, with a Fibonacci effort checkbox and tags
reused from a vault's own tag index, because it was written into a vault. It goes into the specs repo
now, where none of that renders and all of it is noise.

Where a follow-up refers to something the run already wrote, the line links it rather than
summarising it — a summary in two places is one that drifts in one of them.

## Where it lands

**`follow-ups.md` in the folder the run resolved**, appended, alongside the artifacts the follow-ups
are about. Verbose context — a table, a multi-step note, a paste-ready draft — goes in the same file
as a section below the checklist, and the line links it.

**No folder resolved → report-only.** The follow-ups stay in the Final Report and the run says so.
Nothing is ever written into your working directory, which may be a code repository.

**The run carries `specs_git: misrooted` → report-only too**, whether or not a folder resolved: `$SPECS_PATH` is
misplaced, so nothing is written under it, and the notice says that is the reason.

That is the whole ladder. It used to have four rungs, the first of which was a vault; with no vault
and no import, two of them described places that no longer exist.

## What no longer becomes a follow-up

The three chores this emitter mostly used to carry are gone, so do not go looking for them: *paste
the PRD into the tracker*, *paste the release note into the tracker*, and *re-import the increment*. No command
performs a round-trip, so none of the three is ever emitted.

## What qualifies as a follow-up

Only a signal whose action lands **outside the current change** or needs a **manual human step** becomes a follow-up: a change another code repository needs (`/dev-workflows:implement` changes code only in the repository it branches), a file or page owned by someone else, a manual publish step (uploading a screenshot, publishing release notes, creating Epics in a tracker by hand), or a spec-versus-PRD mismatch that needs the PRD updated to match. It deliberately does **not** fire for anything the run's own report or draft already tracks in scope — a deferred review BLOCKER, a skipped test, an in-draft `<!-- TODO -->` marker — since those belong to the current task and duplicating them as a separate follow-up would just create two places tracking the same thing. If nothing in a run qualifies after this filter, the whole phase is a silent no-op: no preview, no prompt, nothing written, and the run looks exactly as if the phase didn't exist.

Before anything is inserted, the target section is checked for a follow-up with the same stable key — `key` plus the file path, gap id, or signal type that identifies it — and a match is skipped and reported rather than re-inserted, so re-running a pipeline over the same ground never duplicates a task that's already there.

## Reviewing before anything is written

Follow-ups never interrupt a run mid-flight. Once the Final Report is composed, every qualifying follow-up is shown together as one batch preview, grouped by the file it would land in, each row naming the triggering signal, the target file and section, and the exact task line that would be written. You act on all of them with a single choice — approve every previewed row, select a subset by row number, or cancel and leave everything in the report only. Nothing is written without that one confirmation.

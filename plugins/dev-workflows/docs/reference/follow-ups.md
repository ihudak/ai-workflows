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
are about — save that `/dev-workflows:implement` writes into the folder of the unit it implemented, the Epic's whether you named the Epic or its picker chose it under a PRD, so one unit's follow-ups land in one file, and `/dev-workflows:conformance` writes each follow-up into the folder of the unit whose `/implement` run it asks for — an Epic's, or the PRD's where the PRD has no Epics — even on a PRD run. Verbose context — a table, a multi-step note, a paste-ready draft — goes in the same file
as a section below the checklist, and the line links it.

**No folder resolved → report-only.** The follow-ups stay in the Final Report and the run says so.
Nothing is ever written into your working directory, which may be a code repository.

**The run carries `specs_git: misrooted` → report-only too**, whether or not a folder resolved: `$SPECS_PATH` is
misplaced, so nothing is written under it, and the notice says that is the reason.

That is the whole ladder. It used to have four rungs, the first of which was a vault; with no vault
and no import, two of them described places that no longer exist.

## A withdrawn follow-up

One command edits a follow-up after writing it: `/conformance`, when a *fix the code* decision whose follow-up an earlier run of it wrote no longer stands — the PE's PRD run overrules a Dev's, or, on any run — a PRD run's own lines on its re-run included — the decision's requirement has been withdrawn or its text is no longer in its document — wherever this checkout's copy of the file holds the line. A line this checkout does not hold yet — one on a Dev's unmerged `conformance/` branch, or on a session branch — cannot be ticked from here: the run names it in its report, and a later PRD run ticks it once the checkout holds it. Until then `/implement` does not build it: a PRD run writes every line it rules must not be built into its own `_conformance.md` as `withdraws: <the line>`, verbatim, and `/implement`'s read-back skips an open task whose line equals one — reading the PRD's record as checked out and as on the default branch — and prints it as `Overruled by …` or `Withdrawn by …`, not built. The edit ticks the line and appends `— withdrawn: <KEY>/[DD#n]`, with `(requirement withdrawn)` or `(orphaned)` after it in the second case, and never deletes it. A ticked line counts as done, so a later `/implement` of the unit does not read it back as open. **A follow-up a group of discrepancies shares** — one *fix the code* decided for several requirements whose evidence shares one location, which `/conformance` queues as a single line — is withdrawn only when every decision it carries no longer stands; where only some are overruled or withdrawn, the line is kept for the rest, and the run names it in its report.

## A re-queued follow-up

The same command writes one line the duplicate check below would skip: when the PE confirms a Dev's *fix the code* decision whose follow-up is no longer open — ticked, never written because it was cancelled at the Epic run's preview, or equal to a line the PRD's own record carries as `withdraws:`, which `/implement` would skip — the PRD run queues a new line ending `— confirmed: <PRD-KEY>/[DD#n]`. A line the Dev's unmerged `conformance/` branch holds open is not re-queued, since it arrives with that branch. A line only a session branch holds is one the PRD run cannot see, so it is re-queued, and the two stand side by side once that branch merges. The PE's confirmation is a new request for that change, so a ticked line naming it does not block it; a line already carrying the same `— confirmed:` suffix does, so a re-run does not write it twice.

## What no longer becomes a follow-up

The three chores this emitter mostly used to carry are gone, so do not go looking for them: *paste
the PRD into the tracker*, *paste the release note into the tracker*, and *re-import the increment*. No command
performs a round-trip, so none of the three is ever emitted.

## What qualifies as a follow-up

Only a signal whose action lands **outside the current change** or needs a **manual human step** becomes a follow-up: a change another code repository needs (`/dev-workflows:implement` changes code only in the repository it branches; run from that repository on the same unit, it prints the open follow-up and adds its change to what it implements, and on an Epic whose target is another repository implements only the changes its open follow-ups list), a file or page owned by someone else, a manual publish step (uploading a screenshot, publishing release notes, creating Epics in a tracker by hand), or a spec-versus-PRD mismatch that needs the PRD updated to match. It deliberately does **not** fire for anything the run's own report or draft already tracks in scope — a deferred review BLOCKER (save one whose fix lies in another code repository), a skipped test, an in-draft `<!-- TODO -->` marker — since those belong to the current task and duplicating them as a separate follow-up would just create two places tracking the same thing. If nothing in a run qualifies after this filter, the whole phase is a silent no-op: no preview, no prompt, nothing written, and the run looks exactly as if the phase didn't exist.

Before anything is inserted, the target section is checked for a follow-up with the same stable key — `key` plus the file path, gap id, signal type, or other repository and unit that identifies it — and a match is skipped and reported rather than re-inserted, so re-running a pipeline over the same ground does not duplicate a task that's already there. For a change another repository needs, the check is change by change: a change any line for that repository and unit already names, open or ticked, is not added again — a ticked line's change is done — and one no line names goes on a new line, since the run there may implement exactly what the open lines list. Another repository is written ``repository `<name>` ``, its name the last segment of its `origin` URL (`api` for `team-a/api` over ssh or https, with or without a trailing `/` and from a fork alike, and for a `server:api` remote with no `/` at all). One the run was not given takes the repository part of its component's id where the ARD's components (or, where it lists none, the Epics' targets) or the design's target span name one (`bookstore` for `bookstore:orders`) — otherwise the name the run gives it — with `(not given)` after it. A repository with no `origin` is named by its path. The key holds only as far as the name does: two runs that name one repository differently — a name the run gave it, the path of one with no `origin` (on another machine, or in a run not given it), a fork or repository renamed, a mirror, a URL in another case — can add its task twice, and two repositories whose URLs end in the same name share a key, so each one's follow-ups are read back by the other's runs too, and a change a line already names is not listed again (within one run they share one line). The line writes the repository in that form once, for that repository alone, and the unit is compared as the whole address of the run the line asks for.

**A security finding's line is the exception.** `/security-workflows:scan` writes one line per finding it queues for a fix, carrying that finding's `[SEC#n]`, and a line carrying a `[SEC#n]` is matched only against an **open** line carrying the same `[SEC#n]` for the same repository and unit — never against a ticked line, and never against a line without that token, in whatever words it names the change. The register decides when a finding needs a fix, so a finding reopened after its fix landed is queued again beside its old ticked line, and so is one another command already named in its own words; a re-run still writes it once. A line without the token is matched as before, a `[SEC#n]` line included. A security finding's line names its patch, where there is one — the scan's, or one an earlier scan made for a fix never reopened since — in a `starting from` clause, by a path in the specs repository, which `/implement`'s read-back resolves there.

## Reviewing before anything is written

Follow-ups never interrupt a run mid-flight. Once the Final Report is composed, every qualifying follow-up is shown together as one batch preview, grouped by the file it would land in, each row naming the triggering signal, the target file and section, and the exact task line that would be written. You act on all of them with a single choice — approve every previewed row, select some — the run then asks, in plain text, for the row numbers to keep — or cancel and leave everything in the report only. Nothing is written without that one confirmation.

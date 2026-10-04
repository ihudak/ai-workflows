# Follow-up emission — Shared Reference

Single source of truth for the family's follow-up emitter. A terminal
"Emit follow-up tasks" phase in each of its callers cites this file and executes its steps inline —
the orchestrator owns every prompt. The callers are the commands that load it, which is a recipe
rather than a list, because a list here went stale as callers were added:
`grep -l 'args: "followup-emission")' plugins/*/commands/*.md` — ten today (`/implement`, `/ready`,
`/epics`, `/prd-proposal`, `/brd-proposal`, `/document`, `/release-notes`, `/docs-init`, `/docs-brand`,
`/docs-audit`).

**Self-contained, and no longer mirroring anything.** This file used to mirror a companion plugin's
Obsidian task-line and vault conventions, because its output landed in a vault. It writes plain
markdown into `$SPECS_PATH` now, so there is no upstream to keep in sync with and no dependency —
runtime or editorial — on any other plugin.

## 1. The task line

    - [ ] <one imperative line naming the out-of-scope action> — <why it is out of scope>

Plain markdown, in a plain checklist. No effort symbols, no priority glyphs, no tags, no date
markers.

**That is a deliberate simplification, not an omission.** This emitter used to render an
Obsidian-Tasks line — a Fibonacci effort checkbox, priority and date symbols, and `#tags` reused from
a vault's own tag index — because its primary target was a file inside an Obsidian vault. It writes
into the specs repo now, where none of that renders and all of it is noise a reader has to skip.

**Link, never restate.** Where a follow-up refers to something the run already wrote — a
`<KEY>-implementation-gaps.md`, a report section — the line links it rather than summarising it. A summary
in two places is a summary that drifts in one of them.

## 2. Where it lands

**`follow-ups.md` in the folder the run resolved**, appended. One file per PRD or Epic folder,
alongside the artifacts the follow-ups are about.

**No folder resolved, or the run carries `specs_git: misrooted` (`specs-repo-git.md` §3.1) → report-only.** The follow-ups stay in the Final Report and the phase emits a
one-line notice naming its reason: `⚠ No resolved folder — N follow-up(s) kept in this report only.`, or,
under the flag, whether or not a folder resolved, `⚠ SPECS_PATH is misplaced (specs_git: misrooted) — N follow-up(s) kept in this report only.` **NEVER write into
the current working directory**, which may be a code repository.

**That is the whole ladder now, and it used to have four rungs.** The vault was the primary target,
`$SPECS_PATH` the second, a directory beside an import the third, and report-only the last. With no
vault and no import, two rungs described places that no longer exist. A run that resolved a folder and
carries no `specs_git: misrooted` is byte-identical to what it was — it took the `$SPECS_PATH` rung then
too. One that carries the flag is the one change: it now reports where it used to write.

## 3. Verbose notes

Some follow-ups need more than a line — a table, a multi-step context, a paste-ready draft. Those go
in the **same file**, as a section below the checklist, and the task line links the section.

There is no separate notes file. `Journal.md` existed because a vault kept notes apart from tasks;
one markdown file per folder keeps them together, which is where a reader looking at the folder will
find them.

## 4. What no longer produces follow-ups

**The three round-trip chores this emitter mostly carried are gone**, and a reader who remembers them
should not go looking: *paste the PRD into the tracker*, *paste the release note into the tracker*,
and *re-import the increment*. No command performs a round-trip, so none of the three is ever
emitted.

What survives is the **out-of-scope finding** — `/implement` naming work it deliberately did not do,
`/ready` naming a coverage gap. Those outlive the session, which is why they are written down at all.

## 5. Idempotency / dedupe

Pipelines re-run. Before inserting, READ the existing tasks in the target
section and SKIP any whose stable key already appears. **Stable key** = the
finding's identity: `key` + (file path | gap-id | signal-type | other repository + unit). Report a
match as `SKIP — already exists` (mirrors `/wiki-tasks-extract` Step 5); never
re-insert.

## 6. Qualifying predicate — what becomes a follow-up

Emit a task ONLY for signals whose action lands OUTSIDE the current change or
requires a MANUAL human step:

- A change another code repository needs (`/dev-workflows:implement` changes code only in the repository it branches, and records one for a run from there); its stable-key identity is the other repository and the unit the task addresses. The task's action is one run from that repository, which plans that unit's changes there itself; the changes the task lists are what this run saw, never the whole of that work.
- Files/pages owned by others (the owner was surfaced and the edit is theirs to make).
- Implementation gaps (PRD vs source; the `<KEY>-implementation-gaps.md`
  draft) → the task links the draft; verbose context → a note (§3).
- Manual publish steps: screenshots to upload (CDN), "publish the release notes",
  "create these Epics in your tracker manually", open-the-PR-by-hand.
- SPEC-VS-PRD ("update the PRD to match the spec").

DO NOT emit tasks for in-scope items the report/draft already tracks: deferred review BLOCKERs (save one whose fix lies in another code repository, which the first bullet takes), skipped tests, in-draft `<!-- TODO -->` markers. Those belong
to the current task and are already carried in the Final Report.

**If no signal qualifies after this filter, the phase is a no-op:** resolve no
target, show no preview, write nothing, and end silently —
the run is byte-identical to one where this phase did not exist.

## 7. Interaction model — batch preview at end-of-run

Mirror `/wiki-tasks-extract`: NO mid-run interruption. After the Final Report
is composed, present the qualifying follow-ups as a batch preview GROUPED BY
TARGET FILE, then act on one confirmation:

    choices: ["approve-all", "select", "cancel"]

- **approve-all** → insert every previewed row.
- **select** → let the user pick a subset by row number, then insert those.
- **cancel** → write nothing; the follow-ups remain in the Final Report only.

Each preview row shows: the source signal, the target file → section, and the
rendered task line. Nothing is written without one confirmation.

## 8. Caller contract (what a wiring command passes in)

The calling phase provides:

- `follow_up_items` — the qualifying signals it already aggregated in its Final
  Report follow-up sections.
- `key` — the run's resolved key, or `null`.

The phase applies §6 (filter) → §2 (resolve target) → §1–§3 (render + place) →
§5 (dedupe) → §7 (confirm), then writes. It is ADDITIVE: the follow-ups always
also remain in the Final Report, the phase NEVER commits, and it NEVER writes
into a docs/code repo or the current working directory, where it is not the specs repository. Follow-ups written
into `$SPECS_PATH` are committed later, once, by the run's terminal
`commit-artifacts` step (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md`
§4).

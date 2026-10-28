# `/product-workflows:update-spec` — revise a merged specification in place (to-fix D19)

**Status:** design, approved by the maintainer on 2026-10-28 after a builder
check. Decisions the maintainer made are marked *(maintainer)*; the rest are marked *(my call)* so they
can be checked while reading.
**Closes:** to-fix D19 (*design owed: revising a specification in place*), the wish PRD2-SPEC-B2 left
open once batch B08 (product-workflows 3.38.0) stopped `/specify` from destroying a specification.
**Opens:** a new to-fix design item, *document lineage* (§ Follow-up), which this design does not build.

## Why

`/specify` can only write a specification from scratch. Since 3.38.0 it archives every existing copy
to `revisions/` first and refuses a `Published: yes` one (`SPECIFY_PUBLISHED`), so nothing is lost, but
a user who wants to change a merged specification re-answers the whole grill and gets new IDs. Two
moments make that painful, in this order of priority *(maintainer)*:

1. **Something upstream moved** — the PRD was updated (`/update-prd`), an ARD decision was superseded,
   an `epic.md` changed, grounding was re-run (`/prd-ground --rebaseline`), or, on the BRD route,
   `decisions.md` gained or changed a decision. The specification should follow, and only the items
   the change touches should be re-asked.
2. **A correction** — a reviewer, `/design`, `/implement` or `/conformance` showed that a criterion is
   wrong or missing; the user wants to change two or three items without re-answering everything.

The B08 attempt built a revise mode *inside* `/specify` and was withdrawn after two Opus reviews: it
became a state machine across `/specify`'s resume question, its Epic picker (whose ●/◐ test cannot tell
a finished specification from an interrupted one) and the `Published` flag. This design avoids all
three by being a separate command that only ever starts from a **merged** specification.

## Goals

- A new command, `/product-workflows:update-spec <ADDRESS> ["<what is wrong>"]`, beside `/update-prd`,
  that takes the merged specification as its base, archives it, changes only the items its confirmed
  change list names, re-reviews the whole result with `spec-reviewer`, and hands it off.
- Two entries into one change list, both confirmed by the user before anything is grilled: **upstream**
  (what changed in the specification's inputs since its baseline) and **correction** (what the user says
  is wrong).
- No ID is renumbered or reused, no citation ever points at nothing, and no existing citation silently
  changes meaning.
- Downstream is told, not written: every document that cites an ID this run superseded or withdrew is
  named, and the next step offers the command that revises it.
- A first, one-field step toward document lineage: the specification records the commit its inputs
  were read at.
- Documented like every other command — a command page, every workflow map and command list that names
  `/specify`, and the mermaid diagrams that show the specification step *(maintainer)*.

## Non-goals

- **Changing a published specification (`Published: yes`)** *(maintainer)*. Its IDs are contracts; with
  agentic delivery, a published specification that must change mid-implementation is an edge case,
  better written fresh, and a user who needs more drives the commands by hand. `/update-spec` stops.
- **Resuming an interrupted `/specify`** *(maintainer)*. A leftover draft is not a base; `/specify` keeps
  archiving it and starting over.
- **Document lineage across the whole chain** — specified below as the next item, not built here.
- **Fan-out.** `/update-spec <PRD-KEY>` updates the PRD folder's own specification only; it never runs
  over the Epics' specifications on its own.

## Anti-goals

- Renumbering or reusing an ID; deleting one anything may cite; keeping an ID while changing what it
  means.
- A second copy of `/specify`'s phases that drifts from it: where `/update-spec` does what `/specify`
  does (grounding, the grill technique, pre-lint, the review gate, the consumption stamps, the
  handoff), it cites the same shared references and the same steps, never a restated copy.
- Re-asking an item the confirmed change list does not name.

## Decisions

### D1. A separate command, not a flag on `/specify` *(maintainer)*

`/specify` stays the from-scratch command; its *Existing specification* guard, resume question and
picker are unchanged, save that the guard's closing sentence — *"Revising a specification in place …
is not this command's yet"* — now names `/update-spec` (a claim with an expiry date, `CLAUDE.md` §
Editing discipline; sweep it by subject).

It follows `/update-prd`'s shape — resolve, archive the base before the first write, change only what
the run names, re-run the reviewer, hand off — and **departs from it in three places**, each stated in
the command so no reader carries `/update-prd`'s rule across: its base is the **default branch's** copy,
not the working tree's (D2); it runs `require-on-main` on the specification itself, where `/update-prd`
runs none (D2); and its ID rules are `specification-format.md`'s, which D4 extends, not `prd-format`'s,
though D4 follows the same principle.

### D2. The base is the specification merged on the default branch *(maintainer; mechanics my call)*

- **Gate it.** `require-on-main` (`workflows-core:phase-handoff` §3) on
  `<feature-folder>/specification.md`, before anything else is read. Its states give the stops and
  remedies: no copy on the default branch (nothing to update — name
  `/product-workflows:specify <ADDRESS>`), a copy only on an unmerged branch or uncommitted (merge or
  discard it first). Beyond the gate, the checkout's copy must be **byte-identical** to `<default-ref>`'s;
  where it is not — a pending `/design` or `/implement` note on an unmerged `spec/` branch, a hand edit —
  stop, naming the difference and asking for it to be merged or discarded first. So the base is one
  file, and no pending change is ever overwritten or merged in. *(my call)*
- **A PRD address whose folder holds no specification while its Epics do** stops, listing each Epic
  specification on the default branch and `/product-workflows:update-spec <EPIC-KEY>` for each. No
  fan-out. *(my call)*
- **`Published: yes` → stop**, `UPDATE_SPEC_PUBLISHED`, naming the IDs-are-contracts reason and the
  remedy: change it through the specs repo's change management, or, where a revision is intended, set
  `Published: no` **and land that edit on the default branch**, then re-run. (A local edit alone does
  not move the base.)
- **Archive the base** to `revisions/specification_<YYYYMMDD>.md` before the first write, under the
  rule `/specify`'s guard uses (first free `-2`, `-3`; an identical archive already present stands as
  the archive; a failed archive stops before any write). One copy of that rule: either cited from
  `/specify` or moved into `specification-format.md` for both. *(builder)*

The upstream inputs are gated as `/specify` gates them: the PRD; on the BRD route the slice's
`decisions.md`; each `epic.md` the run reads.

### D3. The baseline, and the change list's upstream entry *(maintainer: record a baseline; null-version for older specifications)*

- **A new frontmatter field, `inputs_at`**: the full SHA of `<default-ref>` at the moment the run read
  its inputs. `/specify` writes it on every run that writes `specification.md`; `/update-spec` rewrites
  it on every run. Every other writer of the file keeps it unchanged, as `specification-format.md`
  already requires of unknown keys. `spec-reviewer` checks only that it is a 40-hex SHA where present.
- **The upstream entry** diffs each input from `inputs_at` to `<default-ref>`: the PRD folder's
  `prd.md` (the folder above the Epic on an Epic-level specification); every ARD
  `workflows-core:ard-resolution` resolves for the specification; on an Epic-level specification the
  Epic's `epic.md`; the PRD folder's `grounding/*.md` wherever it holds grounding; and on the BRD route
  the slice's `decisions.md`. Each changed hunk is mapped to the specification items it bears on — by
  ID where the specification or its sources cite one (a superseded or new `[AD#n]`; a changed `[US#n]`,
  `[AC#n]` or `[FR#n]` in the PRD; a new or re-decided `[VD#n]`/`[CD#n]`; a changed `[CG#n]`/`[DG#n]`),
  by subject where none does — and shown as *proposed*. The user confirms, removes or adds items before
  any question is asked. An empty diff says so and offers the correction entry.
- **No `inputs_at` (every specification written before this release) is a null baseline.** The run
  cannot tell what moved upstream, says so, and takes the correction entry; the update it writes
  records `inputs_at`, so the next update can diff. It never guesses a baseline from the file's history:
  `/design`, `/implement` and `/conformance` also commit into `specification.md`, so its newest commit
  is not when its inputs were read, and picking one out by its subject is parsing free text.
- `inputs_at` being missing or unreachable (a rewritten history) is reported as a null baseline, never a
  stop.

### D4. The change list's correction entry, and the notes already in the base *(my call)*

- The quoted argument, or the run's question where there is none and the upstream entry is null or
  empty, says what is wrong. It is resolved against the specification's own IDs and headings; an item
  it names joins the list, one it only describes is proposed and confirmed as D3's are.
- **Notes other commands left in the base** — the `## Engineering review` section's open `- [ ]` notes
  and `Engineering proposal (/design): …` answers (`dev-workflows:design-format`), `/implement`'s step
  7.5 notes and `/conformance`'s — are offered as proposed items on every run. An adopted one is
  ticked `- [x]` with `adopted in Version <N>`, never deleted; one declined is ticked with the reason.
  The section is kept as it stands; `specification-format.md` gains a short paragraph saying it may
  exist and who writes it, so `spec-reviewer` reads it as context, not as a stage.
- `/conformance`'s note, `/update-prd`'s next step and `workflows-core:next-phase-offer`'s pm lane name
  `/update-spec <KEY>` where a merged specification exists and `/specify <KEY>` where none does.

### D5. ID rules — split by kind of change *(maintainer)*

Following the principle `workflows-core:prd-format` § Changing a requirement applies to PRD
requirements and `product-workflows:ard-format` to `[AD#n]`:

- **A wording fix that keeps the meaning keeps the ID.** The grill asks, per changed item, whether its
  meaning changed; where the answer is no, the text is rewritten in place.
- **A change of meaning gets a new ID.** The new item takes the next free number in its scope (`[U..]`
  document-wide, `[AC..]` within its story, `[TC..]` within its criterion); the old one stays where it
  is, marked `Superseded by [ACnn]` with the date.
- **A removal is marked withdrawn**, with the date and the reason; nothing replaces it.
- **Nothing is renumbered or reused.** A superseded or withdrawn item stays in place and counts for
  contiguity; `specification-format.md`'s *Renumbering a large specification* paragraph says it does not
  apply to an update run.
- The header's `Version` goes up by one; `Created`, `Author` and `Published` stand; `Open questions` is
  recounted.

The two markers' exact form is `specification-format.md`'s to fix, beside its Identifier conventions,
which also says which consumers read **live items only** — as `prd-format` lists its own.

### D6. Every reader of specification IDs skips a superseded or withdrawn item *(my call, necessary)*

Each consumer that enumerates a specification's IDs learns the two markers, by citing
`specification-format.md`'s live-items rule rather than restating it: `spec-reviewer` and
`workflows-core:pre-lint`'s specification checks (contiguity and coverage); `/dev-workflows:design`'s
Phase 2 extraction and `design-reviewer`'s traceability check; `/implement`'s `in_scope_ids` and
`code-review`'s `applicable_spec`; `/conformance`'s trace; `/epics` Phase 2.6's parse into
`_coverage.md`; and `proposal-format`'s test-case count. The builder re-derives that set with a grep for
each ID shape before editing, rather than trusting this list. This makes the release a coupled one:
`product-workflows`, `dev-workflows` and `workflows-core` (pre-lint, next-phase-offer).

### D7. The grill, grounding, review and consumption stamps *(my call)*

- Each confirmed item is grilled with `workflows-core:grilling-technique`, relentlessly, as `/specify`'s
  Phase 5 grills a stage — only those items, the rest of the specification read as context. The BRD
  route's rule holds: a frozen `[VD#n]`/`[CD#n]` is never re-grilled.
- Grounding follows `/specify`'s (docs, architecture, light code scan), scoped to the themes the change
  list touches, by citing `/specify`'s steps.
- The structural pre-lint runs, then `spec-reviewer` reviews **the whole result**. Its input contract
  gains a `Base:` (the archived copy) and a `Change list:` input, as `prd-reviewer` already takes a
  `Base:`, so it can tell an intended change from a regression; findings are triaged and fixed as
  `/specify` Phase 6 does.
- The consumption stamps `/specify` writes — `consumed_by: specification` on the grounding findings and
  `decisions.md` records it drew on — are written for what this run newly draws on, by the same step.
  That is the one write outside `specification.md`, and it is the write `/specify` already makes, not a
  new one.

### D8. Downstream: report and offer, write nothing *(maintainer; the PRD-level reading my call)*

After the review, the run lists every document that cites an ID this run **superseded or withdrew** (a
wording fix changes no citation), each with those IDs:

- **an Epic-level specification**: the Epic folder's `design.md` — the next step offers
  `/dev-workflows:design <EPIC-KEY>`;
- **a PRD-level specification**: the PRD folder's own `design.md` (a single-component PRD's normal
  shape, or a multi-component PRD's whole-PRD override) — offering `/dev-workflows:design <PRD-KEY>` —
  and each `EPIC-` child's `epic.md` `## Covers` entries and the PRD folder's `_coverage.md`, which cite
  the PRD-level specification's IDs in the `[Uxx]`/`[Uxx/ACxx]` form `workflows-core:pre-lint` checks —
  offering `/product-workflows:epics <PRD-KEY>` to refine. An Epic's own `specification.md` and
  `design.md` carry that Epic's own IDs, not the PRD-level ones, and are not searched.

More offers than the array holds go through `workflows-core:next-phase-offer`'s overflow rule. Nothing
downstream is written.

### D9. Handoff and the rest of the tail

As `/specify`'s: `handoff-to-main` with `prefix: spec` behind the consent choice, staging
`specification.md`, its archive and the consumption-stamped files; then feedback, follow-ups, cost,
`resume.md` and `commit-artifacts`. Run flags, model routing (`spec-reviewer` on the Opus chain),
`specs-preflight` at run start and the `Load the question rules.` step before the first question apply
as to every command of the family.

## Constraints

- Every count the new command changes is re-derived by its own recipe, never incremented from memory:
  the command count in `CLAUDE.md`, `.claude/rules/product-workflows.md`, the `product-workflows`
  description in `plugin.json` and `marketplace.json` (rewritten under the 1024-character budget, never
  appended to), the docs pages; and the consumer sets the authorities keep — `model-routing` callers,
  `--skip-feedback`/`--skip-costs`/`--enforce-model`, `commit-artifacts` writers, `handoff-to-main`
  producers, `require-on-main` consumers, the `docs-grounding` and `architecture-grounding` consumers,
  `next-phase-offer`'s lanes.
- Gates: `scripts/check-docs.sh` (the command's docs entry), `reference-parts.py check-questions` (the
  question-rules step), `check-id-grammar.sh` (`[PREFIX#N]` forms in prose), and the mermaid gate.
- Every mermaid block that shows the specification step gains `/update-spec`, looping back into it.
- A coupled release (D6): `.claude/rules/plugin-updates-coupling.md` gets its bullet.

## Left to the builder

- The phase layout of `commands/update-spec.md`, and which of `/specify`'s steps are cited rather than
  restated.
- The two markers' exact form, the new stop names beyond `UPDATE_SPEC_PUBLISHED`, and the archive
  rule's home (D2).
- How the hunk-to-item mapping is presented, so long as every proposed item is confirmed by the user.

## Follow-up — document lineage (a new to-fix design item, not built here)

Recorded in `docs/superpowers/to-fix.md` by this change, as agreed with the maintainer:

- Every produced document records, in its frontmatter, each upstream it was built from: its path, the
  git **blob id** it read, and that upstream's human `Version` for display ("design built on spec v1,
  `a1b2c3d`"). Blob ids, not version numbers, because a hand edit that forgets to bump `Version` still
  changes the hash. `proposal-record.py`'s `priced-against` record is the precedent, and D3's
  `inputs_at` is the first, coarser step it replaces.
- One shared reference entry point, `upstream-check`, beside `require-on-main`, backed by a script —
  not a subagent: the comparison is mechanical. Every consumer calls it before expensive work; only the
  reference knows which artifact kind derives from which, so a new document kind in the flow is one
  table row, not an edit to every command.
- A moved upstream **asks**, never hard-stops: it names what changed (the version, and the IDs where it
  can tell) and offers to revise the downstream document or proceed, recording the choice — a typo fix
  changes a hash too.
- **No false alarm from a downstream command's own write.** `/design`, `/implement` and `/conformance`
  write notes into `specification.md`, so a design recording the specification's blob id would see its
  upstream "moved" after its own note. The lineage design must avoid that — for instance by hashing only
  the upstream's live items and leaving its notes sections out, or by not counting a change the
  downstream command itself made — rather than relying on the question to absorb it.
- **Null version** *(maintainer)*: a document written before lineage records nothing. A downstream
  document that records no upstream version, against an upstream that has one, is treated as built on
  an older version — outdated — and asks as above; once revised, it records the version it was built
  on.
- Once it lands, `/update-spec`'s upstream entry (D3) and its downstream report (D8) read the record
  instead of `inputs_at` and greps.

# Conformance record format

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Single source of truth for `_conformance.md`, the record `/dev-workflows:conformance` writes into the folder it checked — an Epic folder on an **Epic run**, a PRD folder on a **PRD run** — and for the rules a later run, and a later reader, apply to it. The command is its only writer. Design authority: `docs/superpowers/specs/2026-10-12-conformance-design.md` in the plugin source repository.

## 1. Where it lives and what it is

One `_conformance.md` per checked folder, beside that folder's own documents. Its frontmatter names it and its unit:

```yaml
---
kind: conformance-record
key: <the folder's key>
---
```

`conformance-record` is not a folder kind, so `workflows-core:addressing` §4 never reads this file as the folder's carrier. The record is a phase deliverable: it lands on the specs repository's default branch through `workflows-core:phase-handoff` `handoff-to-main`, on a `conformance/` branch, behind the run's consent choice.

## 2. The header

```markdown
# Conformance: <KEY>

- **Run:** <Epic | PRD> — role `<dev | pe>` — <YYYY-MM-DD>
- **Code checked:** <repo slug> at <branch or default branch> @ <commit>, one line per repository
- **Verdicts:** <n> satisfied · <n> partial · <n> missing · <n> contradicts · <n> not-checkable · <n> unverified

## Satisfied

- <requirement id, or its quoted text> — <file:line@commit>, one per evidence location
```

A re-run rewrites the header and the `## Satisfied` list. A reader that compares the commit recorded here with the repository's default branch can say how far the code has moved since. **`## Satisfied` lists every requirement the run found satisfied, those whose discrepancy the re-check dropped included, with the evidence that settled it — and it is what a later PRD run's drift check reads**: it re-traces a requirement listed there only where the code at its evidence paths changed between the commit the header names for that repository and the default branch, so a record without the list has every requirement re-traced.

## 3. An entry

One entry per discrepancy, in id order:

```markdown
### [DD#<n>] <requirement id, or the quoted text where the requirement has no id>

- **document:** <specification.md | epic.md | prd.md | ard.md>, in <KEY>
- **verdict:** <partial | missing | contradicts | satisfied (an entry now resolved)>
- **shipped:** <one sentence on what the code does>
- **evidence:** <file:line@commit>, one per repository it was found in
- **decision:** <fix-code | amend-document | accept> — **status:** <proposed | final | resolved>
- **rationale:** <the person's own words>
- **effect:** <"follow-up proposed: " and the follow-up line, the note's location, or "recorded">
- **ruling:** <PRD run only: confirms <EPIC-KEY>/[DD#k] | overrules <EPIC-KEY>/[DD#k] | resolved <EPIC-KEY>/[DD#k]>
- **flags:** <any of stale, orphaned, fixed, still open, requirement withdrawn, unverified>
- superseded-by: <PRD-KEY>/[DD#n]   ← written into an Epic entry by the PRD run that overruled it
```

`[DD#n]` is cited outside its record as `<KEY>/[DD#n]`.

**`effect:` on a `fix-code` entry records the follow-up proposed, never one written.** The record is committed at the run's handoff, and the follow-up preview that comes after it can still cancel the line, so whether the follow-up was written is read from `follow-ups.md` — where the next run's re-check reads it — never from this field. Nothing rewrites the field after the preview.

## 4. Statuses and flags

- `proposed` — an Epic run's decision, the Dev's.
- `final` — a PRD run's decision, the PE's. It wins over `proposed` wherever both exist.
- `resolved` — the code now satisfies the requirement. A re-run sets it; so does the PE marking a `stale` entry resolved.
- `stale` — an `amend-document` or `accept` entry whose requirement the merged code now satisfies, though the decision still stands: the code was changed later without the record changing. The PE marks it resolved or keeps it.
- `orphaned` — a Dev entry whose requirement text is no longer in its document (an edited `epic.md` bullet, which has no id).
- `fixed` — a `fix-code` entry whose requirement the merged code now satisfies: the fix happened, and the PRD run lists it and records it `resolved` without asking.
- `still open` — a `fix-code` entry whose requirement the merged code still does not satisfy; the PE confirms or overrules it.
- `requirement withdrawn` — the requirement was superseded or withdrawn after the entry was recorded (`workflows-core:prd-format`).
- `unverified` — the re-check could not settle the verdict either way; the entry says what would.

## 5. Re-runs

A `[DD#n]` is permanent: never renumbered or reused, and its entry is never deleted. A re-run:

- carries each decided entry forward without asking again while its discrepancy persists;
- marks an entry `resolved` once the code satisfies its requirement — which is how a fix is confirmed;
- marks an entry `requirement withdrawn` where its requirement is superseded or withdrawn, carries it forward, never asks about it again, and never counts it as an open fix;
- numbers new discrepancies after the highest id on file, and asks only about those.

A `requirement withdrawn` or `orphaned` entry is listed, never asked again. Where it was a `fix-code`, its follow-up is withdrawn per `workflows-core:followup-emission` § *Withdrawing a follow-up*, with the reason `(requirement withdrawn)` or `(orphaned)`.

A PRD run writes `superseded-by: <PRD-KEY>/[DD#n]` into each Epic entry it overrules, and never deletes or rewrites any other field of an Epic record.

## 6. Readers

A reader takes a `final` decision over a `proposed` one and says where it used a proposal; it treats a missing record as the absence of one, never as a prerequisite. Which reader maps which decision to what is its own reference's to say.

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

`conformance-record` is not a folder kind, so `workflows-core:addressing` §4 never reads this file as the folder's carrier. The record is a phase deliverable: it lands on the specs repository's default branch through `workflows-core:phase-handoff` `handoff-to-main`, on a `conformance/` branch, behind the run's consent choice. Until that branch merges, a later run finds the record there and acts on it before it reads a requirement (`/dev-workflows:conformance` Phase 0 step 5).

## 2. The header

```markdown
# Conformance: <KEY>

- **Run:** <Epic | PRD> — role `<dev | pe>` — <YYYY-MM-DD>
- **Code checked:** <repo slug> at <the ref traced: its default branch, or on an Epic run the Epic's branch> @ <commit>, one line per repository
- **Verdicts:** <n> satisfied · <n> partial · <n> missing · <n> contradicts · <n> not-checkable · <n> unverified

## Satisfied

- <requirement id, or its quoted text> — <file:line@commit>, one per evidence location

## Unverified

- <requirement id, or its quoted text> — <the verdict the re-check could not settle> — <what would settle it>

## Discrepancies
```

A re-run rewrites the header and both lists. A reader that compares the commit recorded here with the repository's default branch can say how far the code has moved since. An Epic run before the Epic's pull request merges names the Epic's branch under **Code checked**, its commit that branch's tip, which a squash merge leaves out of the default branch's history and a deleted branch out of any clone that never fetched it; a record an Epic run wrote from `dev-workflows` 4.26.0 until 4.28.0 names the default branch alone. **`## Satisfied` lists every requirement the run found satisfied, those whose discrepancy the re-check dropped included, with the evidence that settled it — and it is what a later PRD run's drift check reads**: it re-traces a requirement listed there only where the code at its evidence paths changed between the commit the header names for that repository and the default branch, or where that commit does not resolve in the clone, so a record without the list has every requirement re-traced.

**`## Unverified` lists every requirement the re-check could settle neither way** — a `satisfied` citing no `file:line` among them — with what would settle it. It is neither satisfied nor an entry: it takes no `[DD#n]`, nobody is asked about it, and a later run of either kind traces it in full, since it is not under `## Satisfied`.

## 3. An entry

One entry per discrepancy, in id order, under the header's `## Discrepancies` heading — its own heading, so no entry reads as part of `## Unverified`, which a later run traces in full. A record written before `dev-workflows` 4.26.0 has no such heading, its entries following `## Unverified`: a reader takes each `### [DD#n]` heading as an entry wherever it sits, and `## Unverified` as its `- ` lines alone.

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
- **flags:** <any of stale, orphaned, fixed, still open, requirement withdrawn>
- **lists:** <PRD run only, in place of ruling: <EPIC-KEY>/[DD#k] — an Epic entry the run only listed>
- **withdraws:** <PRD run only: a follow-up line, verbatim — one field per line>
- superseded-by: <PRD-KEY>/[DD#n]   ← written into an Epic entry by the PRD run that overruled it
```

`[DD#n]` is cited outside its record as `<KEY>/[DD#n]`.

**An entry for an Epic entry a PRD run only listed** takes its heading, `document:`, `verdict:`, `shipped:`, `evidence:`, `decision:` and `status:` from that Epic entry, carries the run's `flags:` for it and any `withdraws:`, and names it in `lists:` in place of `ruling:`, so Phase 4 of `/dev-workflows:conformance` never takes it as ruled. While its flag holds, a later PRD run lists that Epic entry again, never asks about it, and carries this entry forward under §5 rather than adding another. Once its flag has cleared and the PE rules on it, that run writes `ruling:` in place of `lists:`, with the PE's `decision:` at `status: final`, `rationale:` and `effect:`.

**`withdraws:` carries a follow-up line a PRD run ruled must not be built**, on that run's entry for the Epic entry it rules on or lists, or, on a re-run, on the record's own `fix-code` entry it marks `requirement withdrawn` or `orphaned`: the line of an overruled `fix-code` entry, or of one whose requirement was withdrawn or is gone from its document. It is that entry's `effect:` text — the Epic entry's, or the record's own — after `follow-up proposed: `, read from whichever copy of that record the run read — a Dev's unmerged branch included — and written verbatim, never paraphrased, one field per line. It is written whether or not the run could tick the line in its checkout: `/dev-workflows:implement`'s follow-up read-back skips an open task whose line equals a `withdraws:` value of the PRD folder's record, so a line that reaches a checkout before the tick, or without it — from a Dev's branch, or a session branch — is still not built. It is never rewritten.

**`effect:` on a `fix-code` entry records the follow-up proposed, never one written.** The record is committed at the run's handoff, and the follow-up preview that comes after it can still cancel the line, so whether the follow-up was written is read from `follow-ups.md` — where the next run's re-check reads it — never from this field. Nothing rewrites the field after the preview — save where a later PRD run's ruling on an entry it only listed writes the PE's own (§3 above).

## 4. Statuses and flags

- `proposed` — an Epic run's decision, the Dev's.
- `final` — a PRD run's decision, the PE's. It wins over `proposed` wherever both exist.
- `resolved` — the code now satisfies the requirement. A re-run sets it; so does the PE marking a `stale` entry resolved.
- `stale` — an `amend-document` or `accept` entry whose requirement the merged code now satisfies, though the decision still stands: the code was changed later without the record changing. The PE marks it resolved or keeps it.
- `orphaned` — a Dev entry whose requirement text is no longer in its document (an edited `epic.md` bullet, which has no id).
- `fixed` — a `fix-code` entry whose requirement the merged code now satisfies: the fix happened, and the PRD run lists it and records it `resolved` without asking.
- `still open` — a `fix-code` entry whose requirement the merged code still does not satisfy; the PE confirms or overrules it.
- `requirement withdrawn` — the requirement was superseded or withdrawn after the entry was recorded (`workflows-core:prd-format`).

A verdict the re-check could not settle is no flag: it is listed under `## Unverified` (§2), never as an entry.

## 5. Re-runs

A `[DD#n]` is permanent: never renumbered or reused, and its entry is never deleted. A re-run:

- carries each decided entry forward without asking again while its discrepancy persists;
- marks an entry `resolved` once the code satisfies its requirement — which is how a fix is confirmed;
- marks an entry `requirement withdrawn` where its requirement is superseded or withdrawn, carries it forward, never asks about it again, and never counts it as an open fix;
- numbers new discrepancies after the highest id on file, and asks only about those.

A `requirement withdrawn` or `orphaned` entry is listed, never asked again. Where it was a `fix-code`, its follow-up is withdrawn per `workflows-core:followup-emission` § *Withdrawing a follow-up*, with the reason `(requirement withdrawn)` or `(orphaned)`.

A PRD run writes `superseded-by: <PRD-KEY>/[DD#n]` into each Epic entry it overrules — save while an unmerged `conformance/` branch carries that Epic's newer record, when it names the entry in its report and keeps the overrule in its own entry's `ruling:`, which a later PRD run applies once no `conformance/` branch carries that Epic's record, and only to an Epic entry whose heading names the same requirement, with the same `document:` — and never deletes or rewrites any other field of an Epic record.

## 6. Readers

A reader takes a `final` decision over a `proposed` one and says where it used a proposal; it treats a missing record as the absence of one, never as a prerequisite. Which reader maps which decision to what is its own reference's to say.

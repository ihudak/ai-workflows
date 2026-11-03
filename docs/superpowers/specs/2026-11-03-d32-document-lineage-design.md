# D32 — Document lineage (part 1: PRD → spec → Epics → `/design`)

Date: 2026-11-03. To-fix entry: **D32** in `docs/superpowers/to-fix.md`. Origin: the D19 design (`docs/superpowers/specs/2026-10-28-update-spec-design.md` § Follow-up), which built only the coarse first step — a specification's `inputs_at`.

## Intent

A document in the specs repository is built from other documents: a specification from a PRD, its ARDs, grounding files and (on an Epic) its `epic.md`; a design from a specification. When an upstream document is revised after a downstream one was built from it, nothing today tells the person running the next command. They design from a specification written against an older PRD, or implement from a design written against an older specification, and find out late — or never.

D32 makes every produced document record exactly which version of each upstream it was built from, and makes every consumer check that record — up the whole chain — before doing expensive work, and **ask** when something moved.

## Decisions taken with the maintainer

These are the maintainer's decisions (2026-10-28 in the D19 design, and 2026-11-03 in this brainstorm). A builder does not reopen them.

1. **Record.** Every produced document records, in its frontmatter, each upstream it read: its path, the git **blob id** it read, and that upstream's `Version` for display. Blob ids, because a hand edit that forgets to bump `Version` still changes the hash (`proposal-record.py`'s `priced-against` record is the precedent).
2. **One shared entry point, `upstream-check`, backed by a script**, not a subagent — the comparison is mechanical. Only its reference knows the kind table, so a new document kind is one table row.
3. **A moved upstream asks; it never hard-stops.**
4. **Null record = outdated.** A document of a covered kind that records nothing asks once (see *Missing record*).
5. **A downstream command's own write into its upstream is not a move** — rule below (*When an upstream counts as moved*).
6. **`/update-spec` reads the record instead of `inputs_at`** for its upstream diff and its downstream report.
7. **Scope: design for the whole chain, build one stretch first, then extend right away.** This part builds PRD → spec → Epics → `/design` (plus `/update-spec`). The record format and the kind table are designed against the whole chain, BRD route included, so the later parts add rows and producers, never change the format. After this part is merged (and ideally exercised on one real run), three follow-up parts follow immediately, each its own PR: (1) idea → PRD, ARD, and `/ready`, `/implement`, `/conformance` as consumers; (2) the BRD route; (3) `/document` and `/release-notes`.
8. **What the operator sees** when an upstream moved: one block per moved upstream — its path, its identity recorded → current (`Version` where the kind carries one, else the short blob id — *Builder-check rulings* 6), and the item IDs added, changed or withdrawn between the recorded copy and the current one (e.g. `prd.md a1b2c3d → e4f5a6b: changed [US#2], [AC#4]; new [FR#7]`). No raw diff by default. The choice is *revise first* (Recommended, naming the command that revises it) or *proceed, recording that I accepted it*.
9. **Proceeding is recorded in the consumer's own output**, so re-running that command does not ask again about the same move; it asks again only when the upstream moves further. A different consumer asks once on its own account.
10. **Full walk.** A consumer checks its direct inputs' records and then each of their upstreams' records, up to the top of the covered chain, and reports every stale link in one block. The recommended remedy names the command that revises the **highest** stale link — fixing top-down is the only order that settles.

## Goals

- Every document of a covered kind, written by a covered producer, carries a lineage record.
- Every covered consumer walks the chain from the documents it reads, on the default branch, before its expensive work, and asks once when any link is stale.
- A note another command wrote into an upstream never triggers a question.
- `/update-spec` diffs from the record and finds downstream documents from records, not greps.

## Non-goals (this part)

- The three follow-up parts' kinds and commands (decision 7).
- Showing a raw diff; reviving anything automatically.
- Any change to `require-on-main`'s state table or its stops.

## Anti-goals — a failure even if it technically works

- A hard stop on a moved upstream.
- A question when only notes, ticks or whitespace moved.
- Asking the same consumer twice about a move it already accepted.
- Turning an absent optional input into a prerequisite (`CLAUDE.md`'s last hard constraint).
- Asking on every run about a document whose kind no producer records yet (see *Coverage boundary*).

## The design

### The record

A frontmatter key on the downstream document, written only by the script:

```yaml
upstreams:
  - path: specifications/PRD-0042-checkout/prd.md   # relative to $SPECS_PATH
    blob: <40-hex git blob id of the bytes the run read>
    version: "5"                                     # the upstream's Version, or null where its kind has none
accepted:                                            # optional; written only by a "proceed" answer
  - path: specifications/PRD-0042-checkout/prd.md
    blob: <the blob the operator accepted>
```

- The blob is captured **when the producing run reads the upstream**, never at write time — an upstream that moves mid-run must read as moved — and it is the git blob id **of the bytes the run actually read** (`git hash-object`, no `-w`), wherever they came from: `<default-ref>` for a gated input, the working tree for one the run reads from disk (grounding files; an `epic.md` `require-on-main` reports `absent`; a `pass_amending` or `unmanaged` copy). For a gated input this equals `<default-ref>`'s blob. **My call** (*Builder-check rulings* 1).
- The record lists what the run actually read, so the walk follows recorded paths; the kind table is not needed to find edges.
- `accepted` entries mean: staleness traced to this upstream at this blob was accepted by the operator for this document. A later move of that upstream (a different blob) asks again.
- Unknown frontmatter keys are already preserved by every rewrite (`prd-format.md`'s rule and its counterparts); the record rides along.

### When an upstream counts as moved

1. Same blob as recorded → not moved.
2. Different blob → the script fetches the recorded copy by blob id (`git cat-file -p <blob>`) and the current one from `<default-ref>`, and compares **live items** by key per the kind's item rule — the key being the item's full ID path where IDs restart under a parent (a specification's `[U02]/[AC01]/[TC03]`, since AC and TC numbers restart per story and per criterion, `specification-format.md` § Stage 4 and § Stage 5), shown to the operator in that `[Uxx]/[ACxx]` form. No live item added, changed or withdrawn → **not moved** (notes, open-question ticks, whitespace). Otherwise → moved, and the changed IDs are what the operator sees.
3. A kind with no IDs: any change to its text outside its notes sections counts as a move.
4. The recorded blob missing from the clone (a shallow clone, a rewritten history, or bytes read from a working tree that were never committed) → treated as moved with "recorded copy unavailable — cannot list items".
5. The current copy is read from `<default-ref>`; an upstream absent there (never merged) is reported as such, not as moved — its gate, not this check, owns that state.

### Missing record

A document of a covered kind with no `upstreams:` key asks once: *no lineage record — cannot tell whether its upstreams moved*. *Proceed* writes an `accepted` entry for that document at its current blob (in the consumer's output, decision 9), so the same consumer is not asked again until that document changes. This is the migration path for every document that predates D32.

### Coverage boundary

The walk follows a document's record only where its kind is in the table. A document whose kind is not yet covered (in this part: `prd.md`, ARD files, grounding files, `decisions.md`, `idea.md`) is a **top** of the walk: it is compared as an upstream (blob and items) but its own record is not looked for, and its lack of one never asks. Each follow-up part moves kinds from "upstream only" to "covered".

### The kind table (in the new reference)

One row per kind: how it is identified (file name and `kind:` frontmatter), its item rule (which bracketed IDs are items, which sections are notes), the command that revises it, and its status (covered / upstream only). Designed now for the whole chain; this part marks covered: `specification.md` (PRD- and Epic-level), `epic.md`, `design.md`.

| Kind | Items | Notes sections excluded | Reviser (when this kind is the stale downstream) | This part |
|---|---|---|---|---|
| `prd.md` | `[US#n]`, `[AC#n]`, `[SM#n]`, `[SMC#n]`, `[UC#n]`, `[FR#n]` | per `prd-format.md` | `/update-prd` | upstream only |
| ARD | `[AD#n]` (superseded markers per `ard-format.md`) | per `ard-format.md` | `/create-ard` | upstream only |
| grounding (`code-grounding.md`, `design-grounding.md`) | `[CG#n]`, `[DG#n]` | — | the grounding command | upstream only |
| `decisions.md` | `[VD#n]`, `[CD#n]` | per `decision-register-format.md` | `/brd-interview`, `/brd-reconcile` | upstream only |
| `specification.md` | `[Uxx]`, `[ACxx]`, `[TCxx]` (live-items rule) | § *Notes other commands write*, `## Engineering review`, open-question ticks | `/update-spec` | covered |
| `epic.md` | measured by the builder from `epic-writer`'s template; no-ID rule if it has none | — | `/epics` (re-refine) | covered |
| `design.md` | measured by the builder; no-ID rule if it has none | — | `/design` | covered |

Only `specification.md` (`specification-format.md` § Header) and `design.md` (`design-format.md`) carry a `Version`; for every other kind `version` is null and the display uses the short blob id. Every rewrite of a covered kind must keep unknown frontmatter keys — shown for `specification.md`; the builder confirms it for `/design`'s rewrite of `design.md` and `epic-writer`'s refine mode, and makes it so where it is not. The builder verifies every cell against the named format reference before relying on it; a cell this table states wrongly is a defect in this design, not a licence to guess.

### The script

`plugins/workflows-core/scripts/lineage.py`, invoked the way `workflows-core:specs-repo-git` invokes `session-branch.py`. Subcommands (names are the builder's call):

- `capture` — given paths, print each one's blob and `Version` at `<default-ref>` (called when the producer reads).
- `stamp` — write `upstreams:` into a document's frontmatter from a capture.
- `check` — walk from given documents, return JSON: each stale link (downstream, upstream, versions, changed IDs), each missing record, each link already accepted, and the highest stale link's reviser.
- `accept` — write `accepted` entries into a document.
- `--selftest`, wired into `.github/workflows/validate-catalog.yml` like `session-branch.py`'s.

Non-zero exit on any failure; the calling command stops with its own `<COMMAND>_LINEAGE_FAILED` error, as `/prd-proposal` does with `PRD_PROPOSAL_RECORD_FAILED`.

### The reference and entry point

A new shared reference, `workflows-core:document-lineage`, holding the record format, the moved rule, the kind table and the entry point `upstream-check` (run after `require-on-main` has gated the inputs, before expensive work). It is a new reference rather than a section of `phase-handoff` — **my call**: `phase-handoff` serves three entry points from generated files (`entry-files.md`), and a fourth there would widen that machinery for no gain; "beside `require-on-main`" is kept by placing the call immediately after the gate in each consumer.

The recommended remedy names the reviser of the **downstream** document of the highest stale link — the document that must be revised (for spec ← `prd.md`, `/update-spec`). The question, presented through `escalation-rules` with the approved block above it:

`choices: ["Stop — revise <highest stale document> first with <reviser> (Recommended)", "Proceed — record that I accepted these upstreams"]`

### Producers and consumers in this part

| Command | Records (as producer) | Walks from (as consumer) |
|---|---|---|
| `/specify` | `specification.md` ← every input it reads today (`inputs_at`'s set) | `epic.md` on an Epic-level spec |
| `/epics` | each `epic.md` ← `prd.md`, the PRD-level `specification.md` where read | the PRD-level `specification.md` where read |
| `/design` | `design.md` ← `specification.md`, `epic.md`, ARDs it reads | `specification.md` |
| `/update-spec` | the revised `specification.md` | its base's covered upstreams only (`epic.md` on an Epic-level specification); the base's own stale links are what it is revising, so they are read as its upstream diff and never asked about |

The builder confirms each row's inputs against the command's own phases.

### `/update-spec`

- **Upstream diff:** for each recorded upstream, `git diff <recorded blob> <default-ref>:<path>` in place of the `inputs_at` commit diff. A specification with no record but an `inputs_at` keeps today's diff (fallback); with neither, today's null-baseline path.
- **Downstream report:** the documents whose `upstreams:` lists this specification, in place of the greps; a downstream with no record is still found by today's grep, and named as unrecorded.
- **`inputs_at`:** read as the fallback above; no longer written (**my call** — one record, not two). `specification-format.md` and `spec-reviewer` say so; `/specify` stops writing it in the same release.

### Release and docs

workflows-core (reference, script, selftest), product-workflows (`/specify`, `/epics`, `/update-spec`, `specification-format.md`, `spec-reviewer`) and dev-workflows (`/design`) minor bumps; a coupling bullet (a consumer citing `document-lineage` needs the workflows-core that ships it); docs pages for each touched command and the new reference; the rules files' maps and shared-authorities list; the to-fix D32 entry updated to "part 1 done"; a claim sweep for `inputs_at` and for any sentence saying a consumer cannot tell an upstream moved.

## Builder-check rulings (my calls, after the builder check)

1. **What is recorded for an input read from the working tree:** the blob id of the bytes read (above). Recording only `<default-ref>` blobs would record a version the run never read; leaving such inputs out would hide grounding moves.
2. **Which reviser the remedy names:** the stale downstream's (above). The reviser cells of upstream-only kinds serve the follow-up parts.
3. **`/update-spec`:** never asks about its base's own stale links — it is the remedy for them; it walks above the base only.
4. **Where `accepted` goes:** into every document the run writes whose walk passed through the accepted link (each `epic.md` `/epics` writes, for example). A run that stops before writing records nothing, and the next run asks again — acceptable, since nothing was built on the acceptance. A rewrite carries forward each earlier `accepted` entry whose blob still equals that upstream's current blob, and drops the rest.
5. **Item keys:** full ID paths where IDs restart (above).
6. **Display identity:** `Version` where the kind carries one, else the short blob id — `prd.md` and the other upstream-only kinds carry no `Version`, so the approved `v3 → v5` example reads `prd.md a1b2c3d → e4f5a6b` for them. The `version` field stays in the record for the kinds that have one.
7. **The precedent:** `proposal-record.py` hashes the bytes on disk, which is the precedent for ruling 1, not for reading `<default-ref>`.

## Left to the builder

- Subcommand names and JSON field names.
- `epic.md`'s and `design.md`'s item rules, measured from their templates.
- Where exactly in each consumer's phases the call sits (after its input gates, before its first agent dispatch).
- The selftest's fixtures.

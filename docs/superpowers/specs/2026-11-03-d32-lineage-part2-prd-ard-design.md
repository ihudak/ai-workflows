# D32 — Document lineage, part 2: `prd.md` and the ARDs covered; `/ready`, `/implement`, `/conformance` as consumers

Date: 2026-11-03. To-fix entry: **D32** in `docs/superpowers/to-fix.md`, follow-up (1). Builds on part 1 (`docs/superpowers/specs/2026-11-03-d32-document-lineage-design.md`, shipped in workflows-core 1.73.0, product-workflows 3.70.0, dev-workflows 4.56.0), whose decisions 1–10 bind here unchanged: the record format, the moved rule, the full walk, *ask, never hard-stop*, a missing record asking once, the acceptance recorded in the consumer's own output. A builder does not reopen them.

## Intent

Part 1 made `specification.md`, `epic.md` and `design.md` record what they were built from. Their own tops — the PRD and the ARDs — still record nothing, so a PRD revised after its idea moved, or an ARD written against an older PRD, is invisible to every consumer; and the three commands that build *on* the finished chain — `/ready`, `/implement`, `/conformance` — never look at it. This part closes both: `prd.md` and the ARD files become covered kinds, their producers record, and the three downstream commands check the chain.

## Decisions taken with the maintainer (2026-11-03)

1. **`/implement` asks**, like part 1's consumers, and a *Proceed* is recorded in the Epic's (the unit's) `implementation.md`, in a frontmatter block holding `accepted:`, written when the run writes its block — so only a run that commits records it; one that commits nothing asks again next time, as part 1's §6 step 5 already says of a run that writes nothing.
2. **`/ready` keeps its trait — it never asks and never stops.** Each stale link is a ⚠ readiness finding naming the document to revise and its reviser, and **caps the verdict at PARTIAL**; a document with no lineage record is a note line only, never a downgrade. (The maintainer asked whether `/ready` is still needed at all; it is kept, because it is the only pre-implementation cross-document coverage judgment — retiring it would be its own change, outside D32.)
3. **`/conformance` asks**, like part 1's consumers, and a *Proceed* is recorded in every `_conformance.md` the run writes (it already carries frontmatter).

## Goals

- Every ARD written by `/create-ard`, and every idea-route `prd.md` written by `/create-prd` or `/update-prd`, carries a lineage record.
- `/specify`, `/epics`, `/design` and `/create-ard` check their PRD and ARD inputs as covered documents, so the walk reaches the idea.
- `/implement` and `/conformance` ask before their expensive work when the chain under them is stale; `/ready` reports it.
- `/update-prd`, named as `prd.md`'s reviser, actually sees what moved upstream of the PRD.

## Non-goals (this part)

- The BRD route's own producers (`/brd-interview`, `/brd-reconcile`, `/prd-ground`, `/brd-split`), and a BRD-route `prd.md`'s record: part 3 (follow-up 2), together with whether a register change counts only at the downstream's altitude. `decisions.md` and the grounding files stay upstream-only.
- `/document` and `/release-notes`: follow-up 3.
- `idea.md` as a covered kind: `/idea` reads sources outside the specs repository, so an idea has no upstream to record; it stays a top.
- Retiring `/ready` (decision 2).

## Anti-goals

Part 1's, unchanged — above all: no hard stop; no question when only notes, ticks or whitespace moved; never asking the same consumer twice about a move it accepted; never turning an absent optional input into a prerequisite. And for this part: **`/ready` never asks.**

## The design

### Kind table changes

`lineage-kinds.json`: `prd` and `ard` rows → `covered: true`. Nothing else in the table changes; the item rules, notes and revisers shipped in part 1 already cover both. `idea` stays uncovered; `/create-prd` records it as an upstream, compared by section, as part 1's table already says.

**Migration:** every PRD and ARD written before this part has no record, so the first time each consumer's walk reaches one, it asks once, *Proceed* recommended (part 1 §3, decision 4). That is the migration path part 1 designed, applied to two more kinds.

### Producers

| Command | Records | Upstreams recorded |
|---|---|---|
| `/create-prd` | `prd.md`, **idea route only** | `idea.md` where it sits under `$SPECS_PATH`; the grounding files Phase 2 reads. A `--from-prd` seed PRD is **not** recorded (**my call**): it is a template the new PRD adapts, not a source it is built from — its later change does not make the new PRD stale. **The BRD route writes no record in this part** (**my call**, after the builder check): its PRD would record `decisions.md`, and every decision added at any altitude would then read as a PRD move and ripple a *revise with `/update-prd`* recommendation down every consumer with nothing for it to pick up. Whether the comparison should filter the register by altitude is part 3's question (the BRD route), asked there; until then a BRD-route PRD asks once per consumer as unrecorded, *Proceed* recommended — the migration path every older PRD takes anyway. |
| `/update-prd` | the revised `prd.md`, idea-route folders only (as above) | its base's recorded upstreams, re-captured as read this run, plus the grounding files it reads. A base with **no** record: the folder's `idea.md`, which Phase 2 then reads as a secondary input (**my call**: without it, a pre-part-2 PRD would lose its link to its idea for good). |
| `/create-ard` | each ARD it writes | `prd.md`; on an Epic-level run, `epic.md` and the inherited PRD-level ARD; on the BRD route, `decisions.md` and `ard-seed.md` where read (an ARD is architecture-altitude, which the register's noise is about only at product altitude — part 3 revisits it with the rest of the route); the grounding files it reads. |

**A document never records a document below it in the chain (my call, the general rule behind `/update-prd`'s exclusion).** The chain, top to bottom: idea, decision register, grounding → `prd.md` → ARDs → `epic.md` → `specification.md` → `design.md`. A producer that reads a document lower than its own output — `/update-prd` reading the ARD or spec as secondary grounding, `/create-ard` reading an Epic's `specification.md` or `design.md` in Phase 2 — reads it as context and never records it, since that document already records this one and a record each way would make every revision of either stale the other, a chain that never settles. The order is stated once, in `document-lineage` §4.

**An empty record is a record (my call; closes part 1's deferred minor M4).** Where a producer read no input under `$SPECS_PATH` — `/create-prd` with no idea, or an idea read from outside `$SPECS_PATH` — `stamp` writes `upstreams: []`, and `check` reads that as a document with a record and nothing above it, never as *missing*. The script's reader learns the flow-form empty list (closing the duplicate-key half of minor M3 with it). The record format is unchanged: an empty list was always a list.

**`/update-prd` reads its upstream diff (my call — the mirror of `/update-spec`'s, part 1 decision 6).** Naming `/update-prd` as `prd.md`'s reviser is only honest if re-running it shows what moved: Phase 2 reads, for each upstream its base records, `git diff <recorded blob> <default-ref>:<path>` as a change signal ranked into the grill with the comments; a base with no record keeps today's read. Like `/update-spec`, it never *asks* about its base's own links — they are what it is revising.

### Consumers

| Command | Walks from (`docs`) | `output` (acceptances) | On stale |
|---|---|---|---|
| `/specify` | each `epic.md` (part 1) **plus `prd.md` and every ARD it reads** | the existing spec (part 1) | asks (part 1) |
| `/epics` | the PRD-level spec where read (part 1) **plus `prd.md`** | as part 1 | asks |
| `/design` | the spec (part 1) **plus every ARD it reads** | as part 1 | asks |
| `/create-ard` | `prd.md`; on an Epic-level run, `epic.md` and the inherited PRD-level ARD | the existing ARD, on a re-run | asks |
| `/update-spec` | its base's covered upstreams (**part 1 ruling 3, now wider**): `epic.md` on an Epic-level spec, and on every spec `prd.md` and each ARD the base records — never the base's own links, which are what it revises | the base (part 1) | asks |
| `/implement` (keyed runs) | each in-scope `specification.md` and `design.md` its gate passed | the unit's `implementation.md` | asks — decision 1 |
| `/conformance` | each document its Phase 0 step 4 gate passed | the unit's own `_conformance.md` where on disk; *Proceed* accepted into every `_conformance.md` the run writes | asks — decision 3 |
| `/ready` | each `specification.md` and `design.md` it located as present | none — it records nothing | reports — decision 2 |
| `/update-prd` | — | — | never asks (above) |

**`/ready` honours acceptances recorded in the documents it reads, per unit (my call).** `/ready` has no output of its own to hold one, and a link the document built on it deliberately accepted — `design.md` recording that it went on past a moved PRD — is a decision taken, not a gap. So the script's `check` gains a way to read accepted entries from several documents (the builder names it), and `/ready` runs one check **per unit**: per Epic, with `docs` and the acceptance sources both that Epic's `specification.md` and `design.md`; on a PRD-level run, one more for the PRD-level spec. An acceptance in Epic A's design therefore never clears Epic B's link to the same PRD version, which nobody on B accepted. A link accepted in its own unit is reported as *accepted by <doc>* and does not cap the verdict. Part 1's asking consumers keep their single `--output`: decision 9 (a different consumer asks on its own account) is unchanged.

### `implementation.md` gains frontmatter

`workflows-core:implementation-format` §1 documents an optional frontmatter block at the top of `implementation.md` holding only `accepted:` (the lineage script's block), written by `lineage.py accept`, which creates the frontmatter where the file has none. The builder verifies every reader of `implementation.md` (the format reference's reader list: `/document`, `/release-notes`, `epic-picker`'s ● marker, `/ready`, `/specify`, `/epics`, §5's `unit-branch` consumers, `/conformance`, `/security-workflows:scan`) tolerates a leading frontmatter block, and makes it so where one does not.

### Release and docs

workflows-core (kind table, script extension, `document-lineage` §3/§4/§6 and its consumer list, `implementation-format`), product-workflows (`/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, `/update-spec` — its step 7a's *a PRD-level specification has no covered document above it* becomes false and is rewritten), dev-workflows (`/design`, `/implement`, `/conformance`, `/ready`) minor bumps; one coupling bullet; docs pages for each touched command; the rules files' maps where they describe these commands' gates; the to-fix D32 entry (follow-up 1 done); a claim sweep for every sentence saying `prd.md` or the ARDs are upstream-only / record nothing, and for any saying `/ready`, `/implement` or `/conformance` cannot tell that an upstream moved.

## Left to the builder

- The name and shape of `check`'s several-documents acceptance option, with its selftest.
- Where in each command the capture, the check and the stamp sit — after the command's own gates, before its first expensive step, as part 1 placed them; each command's phases decide.
- How `/ready`'s report shows a stale link (a ⚠ row in its existing findings, naming the reviser) and how its verdict cap is worded in its verdict rules.
- Each producer row's exact input set, confirmed against the command's own phases; a cell this design states wrongly is a defect here, not a licence to guess.

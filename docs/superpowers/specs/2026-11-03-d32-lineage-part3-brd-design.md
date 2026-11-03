# D32 — Document lineage, part 3: the BRD route

Date: 2026-11-03. To-fix entry: **D32**, follow-up (2). Builds on part 1 (`2026-11-03-d32-document-lineage-design.md`) and part 2 (`2026-11-03-d32-lineage-part2-prd-ard-design.md`), whose decisions bind here unchanged: the record format, the moved rule, the full walk, *ask, never hard-stop*, a missing record asking once, the acceptance recorded in the consumer's own output, `/ready` never asking, a producer never recording a document below its own output.

## Intent

On the BRD route the documents a PRD, ARD and specification are built from are the slice's **decision register** (`decisions.md`) and its **grounding** (`grounding/code-grounding.md`, `grounding/design-grounding.md`). Today both are tops of the walk: a consumer compares them but never asks what *they* were built from, so a register whose decisions rest on grounding that has since been re-verified is invisible. And a BRD-route `prd.md` records nothing at all, so every consumer asks about it once as unrecorded. This part makes the register and the grounding record their own lineage, gives the BRD-route PRD a record, and stops the register's noise: today any new decision, at any altitude, marks every document that recorded the register as stale.

## Decisions taken with the maintainer (2026-11-03)

1. **Scope: the register, the grounding and the BRD-route PRD.** `/prd-ground` records what grounding was built from; `/brd-interview` and `/brd-reconcile` record what the register was built from; a BRD-route `prd.md` records the register. The **slice inventory stays a top**: a re-intake already resets every allocation, which is its own loud signal.
2. **Altitude filter.** A change in the decision register or in the grounding counts as a move for a downstream document only where a changed record's `altitude` is that document's own: a PRD counts only `product` records, an ARD only `architecture`, a specification only `implementation`. A record with no `altitude` always counts. A product decision's change still reaches a specification, through its PRD going stale, and the fix order stays top-down.
3. **`/update-prd` revises a BRD-route PRD too.** It diffs the register's `product` records since the version its base recorded and ranks the change into the grill — the move it already makes for an idea. One reviser per document kind, whatever the route.
4. **A `/brd-interview` run that finds no question still re-stamps the register and hands it off** (after the builder check). After a `/prd-ground --rebaseline` the register reads stale against the new grounding, and every consumer is told to revise it with `/brd-interview`; where the new findings raise no question, that run today opens no round and commits nothing, so the mark could never clear. It now records that the register was re-checked against this grounding — a frontmatter-only change — and offers the usual handoff, so the mark clears for every consumer once it merges.

## Goals

- `decisions.md` and both grounding files, written by their producers, carry a lineage record; a BRD-route `prd.md` written by `/create-prd` or `/update-prd` does too.
- A consumer's walk follows the register and the grounding up to the slice inventory (BRD route) or the PRD (idea route).
- A decision or finding at another altitude never asks.
- `/update-prd` on a BRD-route PRD sees what moved in the register.

## Non-goals

- The slice inventory, the root inventory and the BRD source as covered kinds (decision 1).
- `/brd-intake` and `/brd-split` as producers or consumers.
- `/brd-package` as a consumer (**my call**): it packages the register as it stands for the customer, who reviews the decisions, not their lineage; a register behind its grounding is caught at the next `/brd-interview`, which revises it.
- `/document` and `/release-notes`: follow-up 3.

## Anti-goals

Parts 1 and 2's, unchanged. And: **no question about a decision at another altitude**; **no record each way** between the grounding and the PRD (below).

## The design

### Where the grounding sits — it depends on the route

On the **BRD route** `/prd-ground` grounds the slice inventory's `[BR#n]` rows, so the grounding is built from the inventory and sits **above** the register, which cites its findings as evidence. On the **idea route** it grounds the PRD's own requirements (`prd-ground.md` Phase 0), so the grounding is built from `prd.md` and sits **below** it. `document-lineage` §4's chain order states both, and its rule — a producer never records a document below its own output — then decides each case.

**This retires a part 2 capture (my call — a defect part 2 shipped latent).** Part 2's `/update-prd` step 5b records the grounding files it reads as the PRD's upstreams. Once `/prd-ground` records `prd.md` on the idea route, that is a record each way, and every revision of either leaves the other stale. `/update-prd` stops recording the grounding files on either route: on the idea route they sit below the PRD, and on the BRD route the PRD is built from the register, not the grounding (`/create-prd`'s BRD route reads no `grounding/` file). It still reads them as context, as now.

### Kind table changes

- `grounding` and `decisions` rows → `covered: true`. Revisers: `grounding` → `/product-workflows:prd-ground <KEY>`; `decisions` → `/product-workflows:brd-interview <KEY>` (unchanged).
- A row for the **slice inventory** (`brd/brd-inventory.md`), uncovered, its items the `[BR#n]` rows, so a moved inventory lists the rows that changed rather than a plain-text diff.
- **The altitude filter (decision 2).** An item row gains, where its kind's records carry one, the pattern that reads an item's `altitude:` field (`decisions`, `grounding`); a downstream row gains the altitude it consumes (`prd` → `product`, `ard` → `architecture`, `specification` → `implementation`). The comparison of an upstream for a downstream of such a kind leaves out every item whose altitude is another; an item with none is compared. The script reads the downstream's altitude from the table; how is the builder's.
- **The filter applies per link, never along the walk (my call, after the builder check).** It filters a link whose downstream has an altitude. The register itself has none — it holds every altitude — so its own links (to the grounding, the inventory) compare every record, and a register behind its grounding is reported to every consumer that walks through it, naming `/brd-interview`: that is a fact about the register, and revising it is the top-down fix. Carrying a consumer's altitude up the walk would hide a real move, since a product decision can rest on an implementation finding through its `evidence`.

### Producers

| Command | Records | Upstreams recorded |
|---|---|---|
| `/prd-ground` | each grounding file it writes | BRD route: the slice's `brd/brd-inventory.md`, and each design frame-set index it read. Idea route: the folder's `prd.md`. Never the register, which is built from the grounding. |
| `/brd-interview` | `decisions.md` | the slice's two grounding files and its `brd/brd-inventory.md` where read. Not its own working records (`interview/`, `code-defect-log.md`), which it writes beside the register. |
| `/brd-reconcile` | `decisions.md` | as `/brd-interview`. The returned `customer-review-<d>.md` is create-only and dated, so a later review is a new file, never a move; it is not recorded. |
| `/create-prd` (BRD route) | `prd.md` | `decisions.md` and `prd-seed.md` where read. |
| `/update-prd` (BRD route) | the revised `prd.md` | `decisions.md` (decision 3); never the grounding files (above). |

**Only the slice's own files are recorded (my call, after the builder check).** A prerequisite BRD's register (`/prd-ground --depends-on`), the parent's inventory and defect log, and the coverage ledgers of this slice and its siblings are read as context and never recorded: recording them would carry the walk into other BRDs, where every prerequisite decision or sibling re-cut would read as a move of this slice. A prerequisite's change that flips a finding's will-change horizon therefore stays outside lineage, as it is today. `/brd-reconcile`'s sweep, which writes into a dependent BRD's register, never stamps it: that register's record belongs to its own producers' runs.

**A producer that writes into one of its own upstreams captures it after its last write there (my call).** `/create-prd` on the BRD route writes a roundless `[AS#n]` into `decisions.md` — a product-altitude record, so by decision 2 a move for the PRD — after Phase 2 read it. Captured at the read, the new PRD would be stale against its own write. It captures `decisions.md` after its last write to it, before the stamp. (`consumed_by` stamps are already ignored by the kind table and need no such rule.)

### Consumers

| Command | Adds to `docs` | `output` |
|---|---|---|
| `/brd-interview` | the slice's two grounding files | `decisions.md` |
| `/brd-reconcile` | the slice's two grounding files | `decisions.md` |
| `/create-prd` (BRD route) | `decisions.md` | the existing `prd.md` |
| `/create-ard`, `/specify` | `decisions.md` and the grounding files they read | as now |
| `/update-prd` | — never asks (its base's links are what it revises) | — |
| `/update-spec` | `decisions.md` and the grounding files its base records (my call, after the builder check — it is the specification's reviser, as `/update-prd` is the PRD's) | the base, as now |

`/prd-ground` on the idea route already gates `prd.md`; it checks it too (`docs` += `prd.md`, `output` = the existing grounding file), so a grounding run on a PRD behind its idea asks first. On the BRD route its only input, the inventory, is a top, and it checks nothing.

### `/update-prd` on the BRD route (decision 3)

Phase 0 step 5b extends to a folder carrying `brd-link.md`: read the base's record; capture `decisions.md`; Phase 2 diffs it from the recorded blob, **its `product` records only**, and ranks each added, changed or withdrawn record into the grill as a change signal. A base with no record reads the register's `decided` `product` records whole, as secondary input. The prose that says it reads nothing of the BRD tree is rewritten: it reads the register, and still mints none of the three BRD provenance fields.

### `/update-spec` reads the register and grounding at its own altitude

Its Phase 2 upstream diff of `decisions.md` and the grounding files lists the records at `implementation` altitude only, as `/update-prd` lists `product` ones, so a specification revised for one implementation decision is not shown every product and architecture change too (my call, after the builder check). Every other upstream is diffed whole, as now.

### Frontmatter on the register and the grounding files

Neither file carries a frontmatter today. `stamp` creates one where a file has none (part 1). The builder verifies every reader of `decisions.md` and of the grounding files — `/brd-interview`, `/brd-reconcile`, `/brd-package`'s bundle, `/brd-split`, `/prd-ground`, `grounding-verifier`, `/create-prd`, `/create-ard`, `/specify`, `/epics`, and `decision-register-format.md` §8's torn-write rule — tolerates a leading frontmatter, and makes it so where one does not; `decision-register-format.md` and `workflows-core:grounding-format` document the block.

### Release and docs

workflows-core (kind table, altitude filter, `document-lineage` §3/§4/§6, `grounding-format`), product-workflows (`/prd-ground`, `/brd-interview`, `/brd-reconcile`, `/create-prd`, `/update-prd`, `/update-spec`, `/create-ard`, `/specify`, `decision-register-format`) minor bumps — dev-workflows changes nothing, since its commands' walks pick up the new kinds through the script; a coupling bullet; docs pages; rules maps where they name these commands' steps; the to-fix D32 entry; a claim sweep for every sentence saying the register or grounding are upstream-only, that a BRD-route PRD records nothing, that `/update-prd` reads nothing of the BRD tree, or that any decision marks every recording document stale.

## Left to the builder

- The filter's interface in the script and the kind table, with selftests: a decision at another altitude changed → not moved; one at the same altitude → moved; one with no altitude → moved.
- Where in each command the capture, check and stamp sit, as parts 1 and 2 placed them.
- Each producer's exact input set, confirmed against the command's own phases.

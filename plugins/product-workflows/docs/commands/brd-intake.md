# /brd-intake

Copies a customer-supplied business requirements document into the specs repo verbatim — and with it
every file that document links, wikilinks included, after showing you the list — transcribes every
linked image it takes, extracts a `[BR#n]` requirement inventory from the document, its linked
markdown and those transcriptions, confirms the document's defects with a human, and writes a
coverage ledger where every requirement starts `unallocated`.

## Who runs it

`/brd-intake` runs in the [pm](../roles-and-phases.md#pm--product-management) role, cost-attribution
phase `brd-to-prd` — the phase shared by every command of the BRD-to-PRD route, the way `/idea` and
`/create-prd` share `prd-creation`. It is the route's entry point, and the only command in it that
is handed a customer-supplied source document: later commands read the copies and the inventory this
run made, and none extracts requirements from the customer's files again. Downstream, each command
of the route gates on whatever the command immediately before it in the chain produced, not on this
one directly. Nothing gates on this command's own inventory and ledger at all: `/brd-split`, run on
the root, reads both from the working tree and stops on what they contain rather than on where they
have been merged. Every command after that gates on a later hop (`/prd-ground` on the slice's own
ledger `/brd-split` copied, `/brd-split` again on `/prd-ground`'s findings, `/brd-interview` on that
ledger and those findings, `/brd-package` on `/brd-interview`'s register, and `/brd-reconcile` on
`/brd-package`'s sent prompt). Every one of them runs as pm except [`/prd-ground`](prd-ground.md),
which runs as [pa](../roles-and-phases.md#pa--product-architecture).

## Synopsis

```
/brd-intake <BRD-KEY> @<brd-file> [--sort-existing <dir>] [--no-docs] [--docs <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

- **`<BRD-KEY>`** (mandatory) — a short stable identifier for the BRD. Format-validated only
  (`^[A-Z][A-Z0-9_]*(-\d+)+$`); a BRD is a markdown file in `$SPECS_PATH`, never checked against a
  tracker.
- **`@<brd-file>`** (mandatory) — the customer's source document. Must already be markdown — a PDF,
  a Word document, or a slide deck is rejected rather than converted.
- **`[--sort-existing <dir>]`** (optional) — additionally migrate an already-hand-written package
  at `<dir>` into seed files. The source is still required and still gated (Phase 0) — this never
  replaces the extraction, it only adds Phase 6 on top of it.
- **`[--no-docs]`** (optional) — turn documentation grounding off for this run.
- **`[--docs <path>]`** — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`. The flag and its value are stripped together before the address is parsed.

All three run flags apply to this command. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips Phase 9's session-cost entry, still advancing the checkpoint and dropping any deferred cost record a ceded `/prompt-brainstorm` or `/prompt-grill-me` run left pending in this session (`workflows-core:run-flags` §5 step 3) — see [Session cost](../reference/session-cost.md). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 9's maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance` — see [Session feedback](../reference/session-feedback.md). `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `figure-reader` and `brd-reader` (overriding their frontmatter Opus pin), `workflows-core:docs-grounder`, `workflows-core:impl-maintenance`, and, under `--skip-feedback`, `defect-reporter` — to one model; the interactive Phase 1 confirmation and Phase 4 defect classification still run on the session's own model, since enforcement pins subagent dispatches and never the orchestrator's own inline work — see [Model routing](../reference/model-routing.md).

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve inputs"] --> p1["Phase 1 — Confirm"]
    p1 --> p15["Phase 1.5 — Classify + model routing"]
    p15 --> p2["Phase 2 — Copy the source"]
    p2 --> p25["Phase 2.5 — Read the figures"]
    p25 --> p3["Phase 3 — Extract the inventory"]
    p3 --> p35["Phase 3.5 — Documentation grounding (optional)"]
    p35 --> p4["Phase 4 — Confirm defects"]
    p4 --> p5["Phase 5 — Write the coverage ledger"]
    p5 --> p6["Phase 6 — Migrate existing work (--sort-existing, optional)"]
    p6 --> p7["Phase 7 — Handoff"]
    p7 --> p8["Phase 8 — Next steps"]
    p8 --> p9["Phase 9 — Session maintenance, feedback & cost"]
```

Four subagents are dispatched: `figure-reader` (Phase 2.5, frontmatter-pinned to Opus except under `--enforce-model`/`WORKFLOWS_ENFORCE_MODEL` — it
transcribes every linked image the run takes, in parallel batches, without reading the document that
links it), `brd-reader` (Phase 3, frontmatter-pinned to Opus except under `--enforce-model`/`WORKFLOWS_ENFORCE_MODEL` — its defect candidates are judgement
over a long, contradictory document, and a conflict it never proposes reaches no one), `workflows-core:docs-grounder` (Phase 3.5, read-only grounding on the shipped product docs — default
ON when `$DOCS_PATH` resolves, advisory, never a gate) and `workflows-core:impl-maintenance` (Phase 9, session lessons-learned — replaced by `defect-reporter` under `--skip-feedback`/`WORKFLOWS_SKIP_FEEDBACK`).

## What it needs

- **`<BRD-KEY>`** — mandatory; absent or malformed stops the run with `BRD_INTAKE_NEEDS_KEY`. A key
  that resolves to a **slice** stops the run with `BRD_INTAKE_SLICE`, naming the parent to re-intake
  instead: a slice has no source document of its own — the source and the records beside it under
  `brd/` are the parent's, one hop up, while the slice's own `brd/brd-inventory.md` and
  `coverage-ledger.md` are created by `/brd-split` on the parent — and re-running here would overwrite the allocations `/brd-split` recorded in its ledger. A key
  that resolves to any other folder that is not a BRD stops too, before anything is copied: an
  **Epic** folder with `BRD_INTAKE_EPIC_LEVEL`, and an **idea-route PRD folder** — a `PRD-` folder no
  BRD carved — or a folder placed at no level with `BRD_INTAKE_NOT_A_BRD`. Both leave the folder as it
  stands and ask for a key no folder asserts, since the run creates a BRD folder only where the key
  resolves to nothing; an existing root BRD is the one folder a key may name, and that is a re-run.
- **`@<brd-file>`** — mandatory; absent stops the run with `BRD_INTAKE_NEEDS_SOURCE`.
- **Your answer about what the document links.** Phase 1 walks every link first, read-only, and shows
  you what it found. Where anything lies outside the document's own folder it asks whether to capture
  it; where anything is neither markdown nor an image it asks you to convert it first
  (`BRD_INTAKE_UNREAD_ATTACHMENTS` on *Stop*), because nothing reads such a file.
- **A markdown source.** A non-markdown source (a PDF chief among them) stops the run with
  `BRD_INTAKE_NEEDS_MARKDOWN` rather than being converted automatically — the source becomes
  immutable the moment it is intaken, and every `[BR#n]` this run writes anchors into it, so an
  unchecked machine conversion must never silently become the record of what the customer asked
  for. Converting is the operator's own step, done where the result can be checked against the
  original.
- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH`.
- **`$DOCS_PATH`** (optional, default `/workspace/docs`) — documentation grounding, resolved once
  in Phase 1 and consumed with grill-rank ranking over Phase 4's defect walk. Missing, unreadable,
  or carrying no markdown file is a silent, non-blocking skip. Turned off explicitly with
  `--no-docs`. The `/epics` consent-ordering exception does not apply here: `/brd-intake` runs no
  `require-on-main` gate, so resolving in the ordinary confirmation step already puts the one
  consent-bearing step ahead of every write.
- **No repos.** `/brd-intake` is cwd-agnostic and needs no `$REPOS_PATH` — grounding against code
  and design is `/prd-ground`'s job, run later.
- **No prior `/brd-*` deliverable.** `/brd-intake` is the entry point of the route: it consumes no
  earlier phase's artifact, so it runs no `require-on-main` gate in Phase 0, unlike every
  downstream command on this route, including `/prd-ground`.

## What it produces

Under `$SPECS_PATH/specifications/BRD-<BRD-KEY>-<slug>/` — the `BRD-` kind prefix is part of the
name the run creates ([addressing](../reference/references.md) §2):

- `brd/source/<basename>` — the customer's source, copied byte-for-byte and never edited. A re-run
  over a revised source replaces the copy of each file whose bytes changed, git keeping the earlier
  one, and leaves an unchanged file untouched; a document revised under a new filename is copied at
  that name beside the earlier copy, which stays, and is read as a revision of it rather than as a
  new document. The run names each file it records replaced, and each slice whose inventory still
  names an earlier document.
- `brd/source/<the paths it links>` — every file the run takes from the document's own directory,
  copied byte-for-byte to the same relative path, so the copied text's links resolve exactly as the
  customer's did. Screenshots are the usual case, and this run is where they are captured: no later
  command of the route writes under `brd/source/`, so a file left behind here stays out of the record
  until the document is intaken again.
- `brd/source-external/<basename>` — every file the document links from outside its own folder, where
  you chose to capture it, by basename (a different file under a name already taken there gets a
  numbered suffix; an identical one is re-used); immutable as `brd/source/` is, and never replaced
  by a re-run either, since a changed file lands under a new name.
- `brd/brd-link-log.md` — every link in a captured file whose target the copy did **not**
  capture, each with its reason (a URL, an unreadable target, a wikilink matching several files,
  or — where you chose the document's own folder only — a link to a file outside it), the run's
  counts, and a table mapping every captured link that does not resolve as written (a wikilink, an
  external file) to its copy. Written on every run.
- `brd/brd-figures.md` — what the plugin read in each linked image the run takes: a verbatim
  transcription, the customer's annotations and what they point at, and the rows each image yields
  or illustrates.
- `brd/brd-inventory.md` — one row per `[BR#n]`, each with its `source_anchor` and any confirmed
  `[DEF#n]` defects — a `conflict` or `duplicate` on the row it was raised on only — and, in its
  frontmatter, which file the rows were last reconciled against as the document, the hash of
  every file they were reconciled against, your account of each top-level section and each image
  that holds or illustrates no row, and which rows came from a sentence you quoted rather than from
  the reader — so a re-run reports one of those in its own words instead of listing it, every time,
  beside the rows the reader really did stop finding. A re-run keeps every id, and keeps a row's wording
  wherever the file its anchor points into is unchanged since then — judged against that record,
  never against the copy on disk or the link log, so a revised document is recognised as one
  whatever it is called, even after a run that copied it stopped before reconciling; where the new
  read returns a row over an unchanged file that could be a kept row reworded, it asks you whether it
  is the same requirement; a row the new read does not find again is kept, never renumbered away;
  and every id it mints is reported by id. An inventory written before 3.7.0 carries no such record,
  so the first re-run over it on 3.7.0 rewords every row it matches to the new read's wording, once,
  reporting each change, and keeps the record from then on. Before it copies anything, that re-run
  records which document the rows were last read from — out of the link log it is about to rewrite,
  where there is one — so a run that stops before reconciling still leaves the document on record
  for [`/brd-split`](brd-split.md) and [`/brd-package`](brd-package.md) to name.
- `brd/brd-defect-log.md` — one entry per confirmed `[DEF#n]`, resolution `open`. A re-run keeps
  every entry already there, id and resolution unchanged, and adds only the defects it newly
  confirms.
- `coverage-ledger.md` — one row per `[BR#n]`, disposition `unallocated` on every row.
- With `--sort-existing <dir>`: `prd-seed.md`, `ard-seed.md`, `spec-seed.md`, sorted by altitude
  from the hand-written package — seeds only, never findings.

The link log, the inventory, the defect log and the ledger each have one fixed layout — frontmatter,
an opening line where a reader needs one, and a markdown table — and share one cell encoding: a
literal `|` is written `\|` and a line break `<br>`, and the requirement text is verbatim once those
two are decoded, which every reader does before it shows, hands over or compares a cell
([`brd-format.md`](../../references/brd-format.md) §2.3).

Behind Phase 7's consent choice, these are committed, pushed, and a pull request opened against the
specs repo's default branch under a new `brd/<BRD-KEY>-<slug>` branch prefix.

## Gates

- **Phase 3 — `brd-reader`** (Opus, frontmatter-pinned; no override unless `--enforce-model`/`WORKFLOWS_ENFORCE_MODEL` enforces one). Read-only extraction from the document, its
  linked markdown and the image transcriptions: it proposes a `[BR#n]` row per requirement plus
  unconfirmed `defect_candidates` — an `ambiguity` on any obligation only an image states — and
  never decides a defect itself. `EMPTY` (no identifiable requirement) short-circuits Phase 4. On a
  first intake it writes the inventory and the ledger with no row — and the run says so plainly,
  because the route stops on a claimless BRD: Phase 8 then offers a re-run of this command with a
  corrected source instead of offering `/brd-split`, which would refuse the BRD. Over an inventory
  an earlier intake filled it changes nothing — the inventory, the defect log and the ledger stand
  as they were, since an empty read has not shown any requirement gone — and Phase 8 offers
  `/brd-split` only where a ledger row is still `unallocated`. `NOT_FOUND` stops the run and surfaces
  the agent's exact message.

  **The inventory's coverage of its own source is then checked, both directions, from what the run
  already holds** — the anchors the read returned, the image transcriptions, and the rows
  `brd-reader` said each image illustrates; nothing is written to the inventory until this check has
  settled, save where a dangling anchor stops the run — every row the run holds is written first
  then, so the anchor can be corrected by hand. Every `source_anchor` must resolve, in whichever of
  the format's three forms it takes — the document, a linked markdown file, or an image — by
  [`brd-format.md`](../../references/brd-format.md) §2.2's rules. One that resolves to nothing is a
  row nobody can trace back and the run stops, **except a row a re-run kept because its anchor no
  longer resolves — the revised source dropped what it named**: that is a recorded state, and
  stopping on it would refuse a customer's revised BRD with a remedy nobody could perform. And every **top-level section** — of
  the document and of each linked markdown file, the sections at the shallowest level beneath its
  title where one heading titles it — and every **image** must either hold or illustrate a row or be
  accounted for, a section holding one where it links an image or an appendix that yields a row: one
  that does neither is a question rather than a stop, since only a person can say whether it binds
  the delivery team to anything, so the run names each — a section with what the source has under
  it, an image with what the plugin read in it, or its reason where it could not be read. **Re-reading
  is asked once, for the whole set; accounting is asked per item.** The set question offers a re-read
  — `brd-reader` dispatched again over everything, its result replacing the first read's rows,
  candidates and notes wholesale unless it finds no requirement at all, and allowed once per run — or
  accounting for each item, or cancelling. Then each section or image still unaccounted for gets its
  own question: it holds no obligation, which is recorded, or you quote a sentence in it that binds,
  shown the text it is checked against, one obligation to a quote and as many quotes as the item
  binds; each is checked against the source word for word and becomes a row of its own. A quote the
  source does not hold is never written through: the item's question comes back with it, so you can
  quote again, record that it holds nothing, or stop. Every account is kept in the inventory — an
  image's also shown on its line in the figures file — so a re-run over an unchanged file does not
  ask about the same section or image again, while a changed file's accounts are asked afresh. On a
  first intake the rows are numbered once, after the last read and any row a quote added, in reading
  order. **Section granularity is
  the point and was measured**: real BRDs carry fifty or sixty headings under about fifteen
  top-level sections, of which nine or so legitimately hold nothing, so the operator answers nine
  questions rather than fifty — and on a real package the
  sections carrying no row included the user stories and the acceptance tests, which is exactly the
  pair worth putting to a human.
- **Phase 3.5 — `docs-grounder`** (optional). Read-only, advisory, never a gate. Its digest is
  consumed grill-rank: `docs_challenges` are ranked into the order Phase 4 walks its candidates,
  and one may be *raised* as an additional defect candidate — but only as `unsourced` (the
  requirement asserts current behaviour a shipped page corroborates or contradicts) or `ambiguity`
  (the BRD uses a term the docs use for something else). **A `[DEF#n]` is the only thing
  documentation can put on a `[BR#n]` row, and only Phase 4's human confirmation puts it there.**
  `docs_references` — what the product already ships and documents — is reported for `/prd-ground`
  to check against code, and written nowhere; the ledger's `evidence` column stays empty until
  grounding runs, and [`/prd-ground`](prd-ground.md) fills it when it does.
- **Phase 4 — interactive defect confirmation**, not an agent gate: every `defect_candidates` entry
  not already logged (below) is walked one class at a time, in the fixed order
  [`brd-format.md`](../../references/brd-format.md) §3 lists its six classes, via `AskUserQuestion`,
  each put with the same facts — its class, its row and that row's text, its reason, the rows a
  `conflict` or `duplicate` names, and an image-drawn row's picture. A split of one requirement into
  several rows is one `duplicate`, asked once, and any other `conflict` or `duplicate` is raised from
  one end only; where one read raises one relation more than once anyway — from both ends, or
  among three or more rows as several candidates — they are asked as one question, naming every row
  they join. Only a confirmed candidate is assigned a `[DEF#n]` id,
  once the walk ends, in the order of the row it was raised on — never in the order the questions
  were asked. A rejected candidate is dropped, not recorded. **A re-run does not ask again about a defect already logged**: a candidate with the same
  class and row as an entry on file is that entry — a `conflict` or `duplicate` matching where the
  entries on file already join the same rows, raised from either end — keeping its id, reason and
  resolution; where several share one class and row they pair in order, and a candidate left over is
  asked with those entries shown beside it, so a restatement is rejected rather than logged twice,
  and a `conflict` or `duplicate` some but not all of whose pairs the log already joins is asked
  with each entry joining one of them and, confirmed, records only the pairs none of them joins,
  which its question says, so a pair on file is not logged twice and one nothing joins is not
  dropped;
  only the rest are walked, taking ids after the highest in use; and an entry this read did not
  propose again — for a `conflict` or `duplicate`, one no pair of whose rows a candidate joins — is
  kept, and reported as not re-raised, while one only some of whose pairs a candidate joins counts
  as re-raised and is reported with the pairs no candidate joined. A `[DEF#n]` id is never reused,
  renumbered or deleted, so an inventory or ledger row, or a held customer question, naming it still
  names the same defect.
- **Phase 5 — the allocation gate downstream.** `/brd-intake` itself never blocks on the ledger — it
  only ever writes `unallocated` rows. The gate that gates on them is the **allocation** gate (no
  `unallocated` row may survive), not a merge-state one, and it belongs to
  [`/brd-split`](brd-split.md), which walks it on both the root and each slice.

## Example

Intake a synthetic customer BRD for a new BRD key:

```
/product-workflows:brd-intake ACME-001 @customer-brd.md
```

The run resolves or creates the BRD folder, walks every link `customer-brd.md` makes and shows you
what it found — how many linked files of each kind (markdown, image, and files that are neither) lie
inside the document's own folder and how many outside it, every target it could not resolve with its
reason, and **by path** every file outside the folder and every file that is neither markdown nor an
image — copies it verbatim into `brd/source/` together with the files you took, records in
`brd/brd-link-log.md` each link in a copied file whose target it did not copy, and why,
transcribes the linked images,
dispatches `brd-reader` to extract the `[BR#n]` inventory from all of it, walks its defect
candidates with you class by class, writes the coverage ledger with every row `unallocated`, and
offers to branch, commit, push, and open a pull request.

## See also

- [Roles and phases](../roles-and-phases.md) — what the `pm` role owns and hands off.
- [Model routing](../reference/model-routing.md) — the classification rules this command applies.
- `workflows-core:addressing` — the `<BRD-KEY>` grammar and folder
  resolution this command uses by name (`read-key`, `resolve-address`).
- [`brd-format.md`](../../references/brd-format.md) — the `[BR#n]` row shape, the immutability rule,
  §1.1's account of what `brd/source/` and `brd/source-external/` hold and of the link log beside
  them, §1.2's figures file, and the six defect classes this command confirms against.
- [`linked-sources.md`](../../references/linked-sources.md) — how Phase 1 finds, resolves and walks
  the document's links.
- [`coverage-ledger-format.md`](../../references/coverage-ledger-format.md) — the ledger row shape,
  the six dispositions, and the ledger line every command of the BRD-to-PRD route ends its final
  report with.
- `workflows-core:docs-grounding` — the `$DOCS_PATH` resolution gate,
  the `docs grounding:` line this command shows verbatim, and the grill-rank consumption mode.
- [Agents](../reference/agents.md) — `figure-reader`'s, `brd-reader`'s and `docs-grounder`'s full
  contracts.
- [Session cost](../reference/session-cost.md), [Session feedback](../reference/session-feedback.md),
  and [Resume and checkpoints](../reference/resume-and-checkpoints.md) — the terminal Phase 9
  bookkeeping every run emits.

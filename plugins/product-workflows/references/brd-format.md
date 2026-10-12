# BRD format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical structure for a **BRD** (business requirements document): what it is, how its
requirements are inventoried into `[BR#n]` rows, and how defects found in it are classified. Design
authority: `docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` §4, D11, D21 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it). Key
grammar and folder resolution are defined once in `workflows-core:addressing` §1 — cited here,
not restated.

## 1. What a BRD is here

A BRD is a **customer-supplied statement of what they are paying for** — the document a customer
hands the delivery team, typically long, typically internally contradictory, and not implementable
as written. It is not authored by the delivery team and it is not a PRD.

Once intaken, the source is **immutable** (D11): nothing under `brd/source/` is ever edited,
reworded, or reformatted, no matter how badly worded a requirement inside it is. **It is written by
`/brd-intake` Phase 2 alone, and only ever as a byte-for-byte copy of the customer's file.** A
re-run over a **revised** source is the one time a copy is written again: each file at a path
already on file whose bytes changed — the document itself, or a file beside it — has its copy
replaced whole, git keeping the earlier one, and a document the customer revised under a new
filename is copied at that name beside the earlier copy, which stays; the run names each file it
records replaced, and nothing is ever removed (`commands/brd-intake.md` Phase 2). Every `[BR#n]`
anchors into this text by `source_anchor` (§2), so if the source moved under an inventory nobody
re-read, every anchor would silently point at the wrong place. **A replacement and the
reconciliation that re-reads it need not land in one run** — a run can stop between Phase 2's copy
and Phase 3's write, and a read that finds no requirement keeps the inventory as it stands
(`commands/brd-intake.md` Phase 3) — so what each row was last reconciled against is recorded in the
inventory itself, as its `document:` and its `captured:` map (§2), and a later run judges the
document and each file unchanged or replaced against that record, never against the copy it finds on
disk. Defects found in it are logged beside it (§3, §4), never corrected in it — that is the only
way to say precisely what the customer gave the delivery team and what changed afterward.

The source is **markdown only**. A BRD arriving as a PDF, a Word document, or a slide deck is
converted to markdown before intake, and that conversion is never a bare mechanical pass taken on
faith: an unchecked machine conversion must not become the record a `[BR#n]` anchors into, because
a conversion artifact (a dropped clause, a misplaced heading, a table read out of row order) then
becomes an invisible edit to an otherwise-immutable document.

### 1.1 What `brd/source/` holds, and what it could not hold

`brd/source/` holds the customer's document at its own basename **and every file from that
document's own directory that `/brd-intake` Phase 1 took** — every one the link walk reached, save,
where the operator chose to capture only that directory, a file reachable only through a file
outside it (`commands/brd-intake.md` Phase 1) — each at its own path relative to that directory and
each copied byte-for-byte, whatever its type. That is what makes the copy a record rather than a
transcript: a customer's BRD routinely carries screenshots, diagrams and appendices beside it, and a
link the copy did not follow resolves to nothing afterwards — no later command of the route captures
it, and `brd/source/` is never edited (§1), so no command closes the gap short of intaking the whole
document again. `/brd-intake` Phase 2 is the only writer; how a link is found and resolved is
`references/linked-sources.md`'s, and what Phase 2 copies where is stated in
`commands/brd-intake.md` Phase 2. **The markdown-only rule above is about the *document*** — the
text a `[BR#n]` anchors into, and the one thing an unchecked conversion could silently rewrite; a
file it links is captured as it stands, whatever its type. **The intake run reads the document,
every markdown file Phase 2 copied, and every image Phase 2 copied** (`commands/brd-intake.md`
Phases 2.5 and 3); a linked file of any other kind is captured, named to the operator before
anything is copied, and not read. **On a re-run nothing is removed, and a copy is replaced only where
its file's bytes changed** (§1): a file an earlier intake captured and the revised document no longer
links stays where it is, a file whose bytes are unchanged is left untouched, and a file at the same
path with different bytes — the document included — has its copy replaced, git keeping the earlier
one; a document revised under a new filename is copied at that name, and the earlier document's copy
stays beside it (§1). So the log's counts describe the run that wrote them rather than the
directory's contents.

**Every link in a captured file whose target the copy did not capture is named in
`brd/brd-link-log.md`**, never dropped in silence: a URL, a file that could not be read, a wikilink
matching more than one file in the vault — and, where the operator chose to capture only the
document's own folder, a link to a file outside it (the walk record's `inside: false`,
`references/linked-sources.md` §5), with the reason `commands/brd-intake.md` Phase 2's table gives
it. **A file reachable only through a file the copy did not capture is not named there**: the link
to it sits inside a file nobody reads (`references/linked-sources.md` §7), so it has no row, and
`commands/brd-intake.md` Phase 1 names such a file to the operator, before anything is copied,
instead. That log is the **plugin's** record rather than the customer's, which is why it sits in
`brd/` beside `brd-inventory.md` and `brd-defect-log.md` and never under `brd/source/`, where every
byte is the customer's own and a plugin-written file would read as part of the document they handed
over. It names the source document's basename, carries the run's counts — links found, files copied,
links not copied — and then one row per uncopied link: the target as written, the copied file the
link sits in, and the reason, in the layout fixed below. **No path a row writes is the operator's
own**: a row names the captured file a link sits in by its path relative to `brd/`, and an
`ambiguous` wikilink's candidates by their paths relative to the vault root the walk searched
(`references/linked-sources.md` §3) — never by an absolute path, which would write the operator's
directory layout, home directory included, into the specs repository, the reason
`brd/source-external/` below keeps basenames only. A target is quoted as written — the text between
the link's own delimiters, less whatever follows a wikilink's `|`, as `references/linked-sources.md`
§5 defines it — because that is the customer's own text. **The three counts do not add up, and that
is arithmetic rather than a slip**: two documents linking the same file are two links found and one
file copied, so the first count is of links and the second of files. **`files copied` leaves the
document itself out**, as `commands/brd-intake.md` Phase 1's `<n>` does: it counts the files this
run copied beside the document — into `brd/source/` or `brd/source-external/`, a file whose
identical copy already stood counting as copied, whether collision rule 1 re-used it (below) or a
re-run left it untouched under `brd/source/` — so a capture of the document alone reads
`files copied 0`. `links found` counts every link in every file this run copied, the document
included, and `links not copied` the rows of the first table below. **It is written on every run,
including one that captured everything**, so its counts are the positive record that the capture
ran; an absent log and an empty one are not (§2.2 makes the same call for the inventory's coverage
of its source).

**The log also maps every captured link that does not resolve as written.** Its second table,
*Captured links that do not resolve as written*, carries one row per **link** whose copy cannot be
reached by reading the target as a path relative to the file it sits in — with the target as
written, the file the link sits in, and the copy's path relative to `brd/`. **A row needs a copy to
name, so this table holds only links whose target the capture took**: a link the copy did not
capture has its row in the first table instead, with its reason, and never one here — an `ambiguous`
wikilink, which resolved to no single file, is that case rather than this one. Of the links that
were captured, the ones that land here are: every link to a file copied into
`brd/source-external/`; every `[[wikilink]]`, which names a file rather than a path; an absolute
path to a file inside the document's own folder; and a link inside a `source-external/` file whose
target lies inside the document's own folder. **It is the only way any reader resolves such a
link**: nothing rewrites the verbatim document to point at its copy.

**The log's layout is fixed**, one file form every writer produces and every reader parses, its
cells written by §2.3's encoding:

````markdown
---
kind: brd-link-log
key: <the run's <BRD-KEY> as Phase 0 validated it>
---

Source document: <the document's basename, exactly as copied into brd/source/>

Links found <n> · files copied <n> · links not copied <n>

## Links not copied

| Target as written | Linked from | Reason | Candidates |
|---|---|---|---|
| glossary | source/brd.md | ambiguous | archive/glossary.md, notes/glossary.md |
| https://example.com/terms | source/appendix/terms.md | url | |

## Captured links that do not resolve as written

| Target as written | Linked from | Copy |
|---|---|---|
| Pasted image 20260918.png | source/brd.md | source-external/Pasted image 20260918.png |
````

- **`kind: brd-link-log` names this document, not the folder** — a kind outside `brd`, `prd` and
  `epic`, which `workflows-core:addressing` §4 passes over, so the log is never mistaken for the
  folder's carrier.
- **The opening line names the document the capture ran on**: the first non-blank line after the
  frontmatter, `Source document: ` and then the basename, to the end of the line — no quoting, so a
  basename carrying any character is read back exactly. Outside the intake run that writes it, a
  reader takes the document's name from it only where the inventory carries no `document:` (*Which
  file under `brd/source/` is the customer's document*, below).
- **The counts line** carries the three labels in that order, each followed by its number.
- **Both tables are always written**, each under its heading, each with its header row and no rows
  where it has nothing to hold. *Reason* is one of the reasons `commands/brd-intake.md` Phase 2's
  table fixes; *Candidates* lists an `ambiguous` target's candidates and is empty on every other row.

**A log written before this layout was fixed** — 3.6.0 introduced the log without one — carries no
frontmatter and whatever opening line and tables its run chose. A reader that reads such a log for
the document's name takes it from that opening line where the line names exactly one markdown file
under `brd/source/`,
and otherwise, where `brd/source/` holds exactly one markdown file, takes that file; where neither
settles it, the reader names the log and asks the operator which file is the document, and never
chooses. The next `/brd-intake` run over the folder rewrites the log in this layout.

**`brd/source-external/` holds what the document links from outside its own directory**, where the
operator chose to capture it (`commands/brd-intake.md` Phase 1). Each file sits at its **basename** —
never at a path mirroring where it came from, which for an absolute link would write the operator's
own directory layout, home directory included, into the specs repository — and is named by
`references/idea-format.md` *The collision rule*, rules 1–3, never rule 4, which overwrites a copy. A
file rule 1 re-uses — its identical bytes already on file, so nothing is written — counts as copied
wherever this file says Phase 2 copied a file (`commands/brd-intake.md` Phase 2). It is
**immutable as `brd/source/` is**, written only by `/brd-intake` Phase 2 and never removed from — and
stricter in one respect: **a copy here is never replaced either**, since rule 1 re-uses a file whose
bytes are already on file and rules 2–3 give a changed one a new name beside the old. It sits beside
`brd/source/` rather than inside it so that this section's first sentence stays
true — `brd/source/` holds only files *from the document's own directory* — and so that no folder
the customer's own tree happens to contain can collide with it.

**Which file under `brd/source/` is the customer's document is read, never guessed.** The directory
can hold several markdown files, since the document may link one beside it and an earlier
document's copy stays beside one revised under a new filename (§1), so a reader that needs the
document's own name — the writer of a slice inventory's `source:` (§2.1) and `/brd-package` naming
it in the bundle — takes it from the inventory's
`document:` (§2), the parent's on a slice: the
document the rows were last reconciled against, which is the one their anchors point into. **Never
from `brd/brd-link-log.md`'s opening line where the inventory carries `document:`** — the line names
the document the latest capture ran on whether or not a row was reconciled against it, and every
intake's Phase 2 rewrites it, so after a run that stopped before Phase 3 it names a document no row
was read from. An inventory written before 3.7.0 carries no `document:` until the first 3.7.0
intake over it writes one — in its Phase 2, before it rewrites the log, wherever the inventory
holds a row (§2) — so where a reader finds rows and no `document:`, no 3.7.0 intake has rewritten
the log, and its opening line is read: written by the run that wrote that inventory, save where an
intake before 3.7.0 stopped before its Phase 3, which no record tells apart. A BRD intaken before
that log existed holds exactly one file under `brd/source/`, and that file is it. The next intake
judges a revised document against the same `document:` (§2).

### 1.2 `brd/brd-figures.md` — what the plugin read in the customer's images

`/brd-intake` Phase 2.5 has `product-workflows:figure-reader` transcribe every image Phase 2
copied, and writes what it returns here. **A transcription is the plugin's reading of the
customer's image, not the customer's words** — which is why a requirement drawn from an image
anchors on the *image* (§2), never on this file, and why `/brd-intake` Phase 4's human and the
customer's own review both check a row drawn from an image against the picture. It is the
plugin's record, so it sits in `brd/` beside `brd-link-log.md` and never under `brd/source/`. **A
transcription the customer corrects is corrected here**, by `/brd-reconcile`'s required-corrections
phase (`commands/brd-reconcile.md` Phase 6), in a section's *Text*, *Annotations*, *Flow*,
*Illegible* and *Depicts* only — its *Read*, *Appearance*, hash, *Linked from* and *Rows* stay
`/brd-intake`'s — and a later intake keeps the corrected section for as long as the image's bytes,
and so its content hash, are unchanged. A corrected transcription is not corrected requirement text:
it closes no defect, and an inventory row quoting a corrected element is left as it stands.

````markdown
---
key: <the run's <BRD-KEY>>
source: "<the document's basename>"
written_by: brd-intake
---

# Figures: <BRD-KEY>

Images captured <n> · read <n> · reused from an earlier run <n> · not read <n>

## source/images/report.png

- **Linked from:** `source/appendix/notes.md` › Reporting
- **Read:** yes
- **Content hash:** sha256:<hex>
- **Appearance:** screenshot · **Depicts:** <one sentence>
- **Rows:** yields [BR#14], [BR#15]; illustrates [BR#6]

### Text

```text
<the image's own strings, verbatim, as figure-reader returned them — regions apart by a blank line
or as list items>
```

### Annotations

| Says | Points at |
|---|---|
| "add a filter here" | the column header row |
| "" | the `Tax` column |

### Flow

- Submit → Manager approval
- Manager approval → Finance approval — label: [> 10k]

### Illegible

none
````

- **The frontmatter carries `key:` and no `kind:`**, because this file is not the folder's carrier
  and must not look like one: `workflows-core:addressing` §4 reads a folder's identity off its top
  level or, where nothing there qualifies, off the inventory, the one file under `brd/` it reads
  (§2.1). `key:` is the `<BRD-KEY>` Phase 0 validated, never parsed from the folder name, and needs
  no quoting — `workflows-core:addressing` §1's grammar admits nothing YAML would read as anything
  but a plain scalar. The bundle ships this file without its frontmatter
  (`references/bundle-packaging.md` §1.1).
- **`source:` is the document's basename alone, written as a double-quoted YAML string** — the same
  form the inventory's `document:` and a slice inventory's `source:` take (§2, §2.1), and for the
  same reason: a filename may hold a `:` or a leading character YAML reads as syntax, and this field
  names a real file. Not a path: `document:` carries `source/<basename>` and this carries the
  basename. **The writing run takes it from the document it copied into `brd/source/` itself**
  (`commands/brd-intake.md` Phase 2), which is the value §2's `document:` takes once that run's
  Phase 3 writes the rows — never off the ladder §1.1 gives a *later* reader, because this file is
  written in Phase 2.5, before Phase 3 updates `document:`, so on a run over a document resent under
  a new filename that ladder would still name the previous one.
- **One section per image `/brd-intake` Phase 2 copied** — or re-used under collision rule 1, which
  counts as copied (§1.1) — in capture order, headed by the image's path **relative to `brd/`** —
  `source/…` or `source-external/…`. Every path in this file is relative to `brd/`, so one form names
  a file under either directory.
- **The counts line** counts the images the current run captured — every section without the *Not
  captured* marker below — and splits them three ways: `read`, the images this run dispatched to
  `figure-reader` and got a transcription back for; `reused from an earlier run`, the sections whose
  transcription it kept by content hash (below) without dispatching the image; and `not read`, the
  images it dispatched that came back `read: false`. So the three add up to `captured`. **A re-used
  section counts under `reused` whatever its *Read* line says** — that line still records whether a
  transcription exists — so `read 0 · reused 3` beside three `Read: yes` sections is a run that read
  nothing again, not a contradiction.
- **Linked from** names every file that links the image, each relative to `brd/`, with the heading
  path of the passage that links it, in §2.2's form — a file's title left out. A passage with no
  heading path — in a lead section, or in a title's own text above the first heading beneath it —
  is named by its line range.
- **Text** holds the image's own strings only, verbatim, in reading order — one region apart from
  the next by a blank line or as items of a list, a table row as its cells separated by ` | ` — and
  **never a label of the plugin's** (`Title:`, `Row 2:`, `field showing:`), because an image anchor
  quotes *Text* as the customer's element (§2), and a word of the plugin's there would be quoted as
  theirs; *Depicts* says what a region is (`agents/figure-reader.md` owns the transcription's
  shape). **It sits in a fenced `text` block**, its fence longer than any run of backticks the text
  holds, so the customer's strings render as written — a lone `-` or `+` on its own line would
  otherwise render as a heading underline or an empty list item; an anchor still quotes a string
  inside it, and §2.2's verbatim test is unaffected. **A table of repeated data rows — a sample
  report's values — is transcribed as its header and one representative row, with the count in
  *Depicts*; a table whose rows state different things — required fields, prices, an approval
  matrix — is transcribed whole.** A sample report's values are rarely the obligation and would bury
  the ones that are, so one row of such a table is complete, not partial; each row of the other
  kind may state an obligation of its own, so dropping one would lose it unflagged.
- **Annotations** is the table above, one row per mark in `figure-reader`'s order — `annotation <n>`
  (§2) counts them — with an unlabelled mark's *Says* written `""`, and its cells written by §2.3's
  encoding; an image carrying no mark has `none` in place of the table. **Both of those written
  forms say what is absent and neither is a string an anchor may quote** (§2.2): a row drawn from an
  unlabelled mark is anchored `annotation <n>`, which names it by its position in this table, and
  an anchor quoting the empty string resolves against nothing at all.
- **Flow** is one list item per edge, `- <edge>`, each edge in the notation
  `agents/figure-reader.md` fixes — no mark around a label — and `none` for an image that is not a
  diagram. An image anchor quotes an edge exactly as it reads, without the list marker (§2).
  **This list carries no grouping, which bounds what an edge anchor can name**: a diagram drawing
  one edge in two places — two swimlanes, two phases — is transcribed as two identical list items,
  so an anchor quoting it names none of them (§2.2) and a positional form would name a place in
  this list, whose order is `figure-reader`'s rather than the diagram's, recovering nothing the
  notation did not keep.
- **Read** is `yes`, or `no — <reason>` with `figure-reader`'s reason (`missing`, `not_an_image`,
  `unreadable`); an image not read carries no transcription sections, only its header lines.
- **Content hash** is the SHA-256 of the image's bytes. A later intake run keeps the section's
  **transcription** — Read, Content hash, Appearance, Depicts, and the Text/Annotations/Flow/Illegible
  subsections — verbatim wherever the hash still matches the file, and does not read that image
  again; a hash that no longer matches is re-read and its transcription replaced. *Linked from* is
  recomputed by the run every time, including for an image the current run did not capture
  (below), and so is *Rows*, save after an `EMPTY` read over an earlier intake's inventory, which
  keeps it (the *Rows* bullet).
- **Rows** is completed by `/brd-intake` Phase 5, once the inventory is final; until then a section
  Phase 2.5 writes new carries the line empty — `- **Rows:**`, with nothing after it — which is how a
  run that stops before Phase 5 leaves it (`commands/brd-intake.md` Phase 2.5 step 3). Completed,
  it reads `yields` the rows anchored on this image, and `illustrates` the prose rows it bears on —
  each prose row the image restates, and each prose row whose own passage links the image to bind
  what it draws, since a row such as *"Approval must follow the attached flow."* states no
  obligation beyond binding the ones the image draws — either half left out where its list is empty
  — `yields [BR#3]`, `illustrates [BR#6]` — or `accounted for — <the operator's answer>` where it
  does neither, the answer's substance and never an option's label: `accounted for — they hold no
  obligation` where the operator picked that option at `/brd-intake` Phase 3, or their own words
  where they typed an answer to the same effect in the harness's free-text option
  (`workflows-core:escalation-rules` §0). **The account is kept in the inventory's `accounts:` map
  (§2), and this line only shows it**: Phase 5 writes it from that map's entry for the image, and
  nothing reads an account back off this line — so an account survives a re-run only where §2's
  carry rule keeps the entry — and, where `brd-reader` returned `EMPTY`, nothing is put to the
  operator: over a folder holding no prior inventory row the line is `none — no requirement
  extracted`; over an earlier intake's
  inventory, which that read leaves as it stands (`commands/brd-intake.md` Phase 3), a section's
  line is **kept exactly as it stood**, `illustrates` included — every row it names is kept with the
  inventory — and a section that had none takes `none — no requirement extracted`. **It names
  requirements of the BRD that owns this file — on a slice, the parent's, one hop (§2.1)**, which is
  how `references/bundle-packaging.md` §6.2 relation 1 reads it.
- **A section is never deleted.** An image the current run did not capture keeps its section, with
  a line `- **Not captured by the current run.**` under its header. The marker covers every cause —
  for instance the revised document no longer links the image, or it still links it and this run
  did not take it (`commands/brd-intake.md` Phase 2.5 step 3 names the cases). Its *Linked from*
  becomes `— (not captured by the current run)`, and its *Rows* becomes `yields [BR#n], …` for any
  preserved row still anchored on it, else `none — not captured by the current run` — an inventory
  row the re-run preserved may still anchor on it — save after an `EMPTY` read over an earlier
  intake's inventory, which keeps the line as it stood (the *Rows* bullet above). §2.2 relation 3
  covers only the images the current run captured, so it does not ask about a marked image either
  way.

## 2. The inventory

The inventory (`brd/source/`'s companion `brd-inventory.md`) holds **one row per requirement**:

| Field | Meaning |
|---|---|
| `id` | `[BR#1]`, `[BR#2]`, … — contiguous, assigned once, never renumbered |
| `text` | the requirement, verbatim, or its first sentence plus a `source_anchor` when quoting it whole would be unwieldy; for a row a split produced, the one fixed form below; for a row anchored on an image, the obligation in words, quoting the transcribed element verbatim — the plugin's words, told apart from the customer's by the row's image anchor |
| `source_anchor` | where the requirement is stated — in the document, an appendix, or an image, in one of the three forms below |
| `defects` | a `[DEF#n]` list (§3) — empty when the requirement carries none; a `conflict` or `duplicate` is listed on the row it is raised on only (§4) |

**The file's layout is fixed**, its cells written by §2.3's encoding:

````markdown
---
kind: brd
key: <this folder's key>
document: "source/brd.md"
captured:
  "source/brd.md": sha256:<hex>
  "source/appendix/fields.md": sha256:<hex>
accounts:
  "1. Background": "they hold no obligation"
  "source/appendix/fields.md › Sources": "pointers to the customer's \"Reports\" wiki only"
  "source/images/logo.png": "they hold no obligation"
quoted:
  - "[BR#1]"
---

# Inventory: <this folder's key>

| id | text | source_anchor | defects |
|---|---|---|---|
| [BR#1] | The monthly report lists every invoice. | 2. Monthly report | [DEF#1] |
| [BR#2] | Every monthly report must include these fields: … Invoice number | source/appendix/fields.md › Required report fields | [DEF#2] |
| [BR#3] | Every monthly report must include these fields: … Customer name | source/appendix/fields.md › Required report fields | |
| [BR#4] | Every monthly report must include these fields: … Invoice date | source/appendix/fields.md › Required report fields | |
````

The frontmatter is the folder's carrier on a source-owning BRD, and a slice's adds `parent:` and
`source:` (§2.1); the title line names the same key; the table carries the four fields above as its
four columns, in that order, one row per `[BR#n]` in id order. `id` is written bracketed, and
`defects` as §2.3 writes a list. **An inventory holding no row** is that frontmatter less its
`document:`, its `captured:` map, its `accounts:` map and its `quoted:` list, which record what the
rows were reconciled against and where they came from and so have nothing to record,
the title and the table's header — what `/brd-intake` Phase 2
writes before anything is copied, and what it leaves after an `EMPTY` read on a first intake — never
an empty file, which on a source-owning BRD would leave the folder keyless.

**`document:` and `captured:` record what the rows were last reconciled against**, on a
source-owning BRD's inventory only. `document:` names the document the rows were read from, by its
path relative to `brd/` — `source/<basename>` — as a double-quoted YAML string. `captured:` holds
one entry per file under `brd/source/` or `brd/source-external/`, keyed by its path relative to
`brd/` as a double-quoted YAML string, its value the SHA-256 of the file's bytes written
`sha256:<hex>`, as §1.2 writes an image's *Content hash*. `/brd-intake` Phase 3 writes both whenever
it writes the inventory's rows — `document:` naming the document that run read, and the map holding
each file that run captured at the SHA-256 of its copy, and each entry already on file for a file
that run did not capture, kept as it stands — and nothing else writes them, save the one write of
`document:` alone described below; a run that keeps the inventory as it stands keeps both with it. A
later intake's Phase 2 judges each file it captures **unchanged**, **replaced** or **new** against
this map, never against the copy on disk (§1), and judges the document against the map's entry for
the file `document:` names, whatever the new one is called — a document whose bytes differ from that
entry is **replaced**, whatever its name, and never new (`commands/brd-intake.md` Phase 2). **Never
against the document `brd/brd-link-log.md`'s opening line names**: every intake's Phase 2 rewrites
the log, so after a run that stopped between its copy and Phase 3's write the log names a document
no row was reconciled against. Neither field is an identity field: `kind: brd` and `key:` alone are
what `workflows-core:addressing` §4 reads (§2.1). **An inventory written before 3.7.0 carries
neither**, so nothing records what its rows were reconciled against. The next intake over one
holding a row writes `document:` first, in its Phase 2 before it copies anything or rewrites the
log, naming the document as §1.1 tells a reader of such an inventory to — the one line added,
nothing else in the file changed — so the record stands even where that run stops before Phase 3; it
writes no `captured:` map, since nothing on file holds the hashes the rows were reconciled at. It
then records every file whose copy already stands **replaced**, once, and the document whatever its
name — its matched rows take the new read's wording, each change reported — and writes both at
Phase 3, which every later run judges against; an inventory carrying `document:` and no map is
judged the same way (`commands/brd-intake.md` Phase 2). A slice's inventory carries neither: it is
copied from its parent's rows and never reconciled against a source (§2.1).

**`accounts:` records the operator's answer for each top-level section that holds no row and each
image that neither yields nor illustrates one** (§2.2 relations 2 and 3), so a re-run over an
unchanged file does not ask about the same item again. One entry per item the operator accounted
for. **A section is keyed** as relation 2 names it — its heading path in the one form §2.2 fixes,
prefixed for a linked markdown file by the file's path relative to `brd/` and ` › `, exactly as an
anchor into that file is written, and, for a file with no heading at all, which is one section, by
that file's path relative to `brd/` alone. **An image is keyed** by its path relative to `brd/`, as
its section in `brd/brd-figures.md` is headed. The value is the account's substance, never an
option's label: `they hold no obligation`, or the operator's own words where they typed an answer to
that effect. **Key and value are double-quoted YAML strings**, so a `"` inside either is written
`\"` and a `\` is written `\\` — the example above carries one — and nothing else in them is
escaped. `/brd-intake` Phase 3 writes the map with the rows, in the same act as `captured:`, and
nothing else writes it: an entry for every item that run accounted for, asked or carried, and every
entry already on file for an item in a file that run did not capture, kept as it stands; an item
that now holds or illustrates a row has no entry. **A later run carries an item's account, and does
not ask again, only where its Phase 2 recorded the item's file unchanged** — the file a section sits
in, or the image itself — and the item still holds or illustrates no row; a section of the document
is judged by the document's own state, against `document:` as above. **Every write of the map drops
the entry of every item in a file Phase 2 recorded replaced**, save one that run asked afresh — the
write after the coverage step, and the one relation 1's stop makes before anything is asked
(`commands/brd-intake.md` Phase 3) — so an account the operator gave about a file's earlier bytes
never stands beside a `captured:` entry recording its new ones. An image's *Rows* line shows its
account (§1.2) and is never where one is read from. A slice's inventory carries no `accounts:`
either, for the reason above.

**`quoted:` records which rows came from a span the operator quoted**, so a later run can tell a row
the coverage step created from one the reader extracted and later stopped returning. **It records a
provenance, never a history**: the list says where a row came from, and says nothing about which
reads have or have not returned it since — so what a run reports off it is a claim about its own
read alone. One `[BR#n]` per line, each
double-quoted as a `claims:` entry is (§2.1); the key is omitted entirely where the inventory holds
none. `/brd-intake` Phase 3 writes it with the rows, in the same act as `captured:` and `accounts:`,
adding the id of every row its coverage step minted from a quote this run and keeping every id
already on file. **Nothing is ever dropped from it or rewritten in it**, and it needs no carry rule
and no drop: a row's provenance is where it came from, which no later read changes, and an id stays
good because a row is never renumbered and never deleted (§2). A read that does return such a row
changes nothing here either — the row is matched and keeps its id like any other. **It is a report's
input and no gate's**: `/brd-intake` reports a row on this list that a read did not return in its own
words rather than as one *not re-extracted by this read* (`commands/brd-intake.md` Phase 3), which is
the whole of what it is for. A slice's inventory carries no `quoted:`, for the reason above — its
rows are copied from its parent's.

**A requirement carrying more than one obligation is split.** When one numbered item in the source
binds the delivery team to two or more separable obligations, each obligation becomes its own
`[BR#n]` rather than being inventoried as one row with a compound `text`. **The split is one defect,
however many rows it yields**: one `[DEF#n]` of class `duplicate` (§3), raised on the first row the
split produced and naming every other row it produced — never one per row — so the inventory does
not silently multiply one source requirement into several without a defect marking that it did, and
does not turn one act of splitting into several defects a customer is asked about separately.

**A split row's `text` takes one fixed form, `<lead-in> … <item>`**: the words the split obligations
share — a list's lead-in, or the subject of a sentence carrying several clauses — then ` … `, then
the words that are this row's own obligation — its list item, less its list marker, or its own
clause — each part a verbatim span of the source, and ` … ` the only thing the plugin writes. Where
the obligations share no words, the row's `text` is its own part alone. The form makes every row one
split produced differ from its siblings in `text`, which is what lets a later read tell them apart
where they share one `source_anchor` (`commands/brd-intake.md` Phase 3).

`[BR#n]` numbers are never reused and never renumbered, including across a split: once assigned, an
id is permanent even if the row it names is later split, superseded, or found defective.

**`source_anchor` takes one of three forms**, by where the requirement is stated:

- **In the document** — a heading path or a line range inside it, as it always has.
- **In a linked markdown file** — `<path relative to brd/> › <heading path or line range>`, for
  instance `source/appendix/fields.md › Reports › Columns` or
  `source-external/glossary.md › L12-L18`.
- **In an image** — `<path relative to brd/> › "<element>"`, the element a string quoted verbatim from
  the image's *Text*, an annotation's *Says*, or its *Flow* in its §1.2 section — never from *Points
  at* or *Depicts*, which are the plugin's paraphrase, and from *Text* within one cell or one region,
  never across the ` | ` the plugin puts between cells or the break between regions — as in
  `source/images/report.png › "Net total"`, or, quoting a diagram's edge whole as its *Flow* item
  reads without the list marker,
  `source/images/flow.png › "Manager approval → Finance approval — label: [> 10k]"`; or
  `<path relative to brd/> › annotation <n>`, the n-th annotation in its §1.2 section.

**A heading path, in either of the first two forms, names exactly one heading**, with ` › ` between
nested headings — `Feature A › Acceptance criteria` in the document, and in a linked file
`source/appendix/fields.md › Reports › Columns`, whose first ` › ` ends the path — and **leaves out
the file's title**, where it has one (§2.2 defines it), so each section is written one way. Where
headings repeat, §2.2 branch 2 says how to tell them apart; text above a file's first heading is
addressed by a line range (§2.2 branch 3).

**A reader tells the three forms apart by the anchor's text before its first ` › `**: text beginning
`source/` or `source-external/` names a linked-markdown or image anchor — which of the two, by the
linked file's extension — and any other anchor is a document anchor.

**Rows are numbered in reading order across all three**: the document's first, in source order; then
each linked markdown file's, in the order `/brd-intake` Phase 2 captured it; and a row drawn from an
image at the passage that links the image — its first link, where several do. **On a first intake,
with nothing on file, the rows are numbered once**, after `/brd-intake` Phase 3's last read and after
any row its coverage step adds from a sentence the operator quotes, so a re-read's rows and an added
row each take their place in that order rather than the end of it. **On a re-run every id on file is
kept, and each new row — read or added — takes the next id after the highest in use**, so a new row
sits after them whatever its place in the source (`commands/brd-intake.md` Phase 3).

### 2.2 The inventory's coverage of its source is checkable from the inventory alone

**A section the read skipped and a section that genuinely holds no obligation come out of an
inventory identically — as a section with no row — so the difference cannot be read off the
artifact.** It is made visible at intake instead, and nothing is stored to find it: the sections
are checked from `source_anchor`, the document and its linked markdown, and the images from
`brd/brd-figures.md` and the `illustrates` list `brd-reader` returns beside its rows. The one thing
kept is the operator's answer about each section or image the check names, in §2's `accounts:`, so
an unchanged file is not asked about twice. A first design had the reader account for every heading
it passed; measured against real intakes that is fifty-odd
accounts of "this section holds context", which buries the one case worth seeing. **`brd-reader`
does give a one-line reason for each top-level section it took no row from** (its
`sections_without_rows`), as it gives an image that bears on no obligation a `note` — at the
granularity below, so the nine-odd, not the fifty — and neither is kept or is an account:
`/brd-intake` shows each beside its item and recommends accounting over a re-read where the read
gave a reason for every item a re-read could change (`commands/brd-intake.md` Phase 3), and the
operator's answer is still what `accounts:` records.

**The binding words.** `/brd-intake` Phase 3 does not let a reason stand unexamined where a
section's own text carries a word that typically binds: `must`, `shall`, `should`, `required`, `requires`,
`mandatory`, `need to`, `needs to`, `has to`, `have to`, `responsible for` — matched
case-insensitively, as whole words, every run of whitespace collapsed to one space. This list is
the one place they are fixed. It is a tripwire, never a test of whether a sentence binds: a hit
quotes the sentence beside the reader's reason and takes the marker off that section's own
question, so recording that it holds nothing is a deliberate answer, and the remedy for a sentence
that does bind is to quote it, which adds that row and leaves the rest of the read alone. A hit
never changes which of the two is recommended, a re-read or accounting: a false hit — a conventions
section saying what *must* means, *"the old system must be restarted nightly"* — then costs one
deliberate answer, where flipping the recommendation would bring back a whole-set re-read on most
real BRDs. A miss — an obligation stated with no such word, or in another language — leaves the
section's question as it was. `will` is left out on purpose: it is the future tense of every
background description, and a name (*Will Turner, product owner*) in the very contact lists a reason
is meant to settle, so it would flag nearly every such section, making an unmarked question the norm
and the quoted sentence noise.

Three relations — the first two over the **top-level section** of the document and of every
linked markdown file Phase 2 copied, as defined below the list, the third over the images:

1. **Every `source_anchor` resolves — in whichever of §2's three forms it takes.** A document or
   linked-markdown anchor resolves to a section that file actually has; an image anchor resolves
   by its own rule, below. Whichever form it takes, an anchor that does not resolve is a row
   nobody can trace back, in the artifact whose whole job is traceability.
2. **Every top-level section of the document and of each linked markdown file Phase 2 copied (a
   file with no heading at all — the document itself or a linked file — is one section, its whole
   body after any frontmatter block, branch 3 below; a file's text above its first heading is its
   lead section, which this relation does not ask about) either holds a row or is accounted
   for.** A section is held where any anchor names it or a section beneath it, or where it links a
   file that yields a row — an image some anchor names (§1.2 *Linked from* records where each is
   linked), or a captured markdown file some anchor names: a section whose only content is a link
   to an appendix holds whatever that appendix yields. One with none is not a defect and is not a
   stop — only a person can say whether a section binds the delivery team to anything — so
   `/brd-intake` names each with what the source has under it and asks, and records the answer in
   §2's `accounts:` so a section of an unchanged file is not asked about twice.
3. **Every image the current run captured yields a row, illustrates one, or is accounted for.**
   It *yields* a row where any anchor names it, and *illustrates* one where `brd-reader` returned
   that row in the image's `illustrates`. An image that does neither — a logo, a decorative banner,
   a screenshot whose content no obligation bears on, or an image that could not be read — is named
   with its `Depicts` sentence or its reason, and asked about as relation 2's sections are; its
   answer is recorded in §2's `accounts:` and shown on its *Rows* line (§1.2).

**A top-level section, and the one heading-path form it fixes.** Where a file's first heading is
the only heading at its level and has headings beneath it, that heading is the file's **title**,
and the file's top-level sections are the sections at the shallowest heading level beneath it;
otherwise they are the sections at the file's shallowest heading level. So the ordinary shape — one
`#` title over `##` sections — has its `##` sections as its top-level sections: read with the title
as its one top-level section, it would always be held and relation 2 could never fire. A file whose
one heading has nothing beneath it has no title in this sense, and that heading's section is its one
top-level section. The title's own text above the first heading beneath it is treated as a lead
section is — addressed by a line range (branch 3 below), named by its line range in a *Linked from*
line (§1.2), and not asked about by relation 2. **Every heading path — in an anchor (§2) and in a
*Linked from* line (§1.2) — leaves the title out**: `2. Monthly report`, never
`Acme reporting › 2. Monthly report`, and in a linked file
`source/appendix/fields.md › Reports › Columns`, where `Report fields` titles the file. One section
is then always written one way; branch 2 below still resolves a path that does name a title,
because it matches only the ancestors a path names.

**The granularity is the finding, not a detail.** Real BRDs run to fifty or sixty headings under
fourteen or fifteen top-level sections, and on a careful intake nine of those fifteen legitimately
hold nothing — the alternatives considered, the personas, the journeys, the decisions log. At section
granularity the operator answers nine questions instead of fifty, and the two that matter stand out:
on a real package the sections carrying no row included the **user stories** and the **acceptance
tests**, which is exactly the pair a reader would expect to have been inventoried and exactly the
question worth putting to a human.

**Relations 1 and 2 resolve a document or linked-markdown anchor against the right file first:
the document itself for a document anchor, or, for a linked-markdown anchor, the file
`/brd-intake` Phase 2 copied at the path before the first ` › ` — only the part after it is then
tested below (a path naming no file Phase 2 copied, or re-used under collision rule 1, does not
resolve — §1.1). §2's anchor into that file is a heading path *or* a line range, so both forms
resolve there — in this order** (an image anchor never reaches this test; it resolves by the rule
below):

1. **A leading section reference** — `§` and a section number — resolves to the section of the
   **one** heading in the file carrying that number: a heading whose text opens with it, after an
   optional `§`, followed by a space, by a full stop and a space, or by nothing — so `§ 7` resolves
   to `§ 7 Retention`, and, where the customer numbers without `§`, to `7. Retention` or
   `7 Retention`, never to `7.1 Scope`. Where no heading carries the number, or more than one does,
   it does not resolve (branch 4): `§ 99` in a file whose sections stop at 12 is a dangling anchor
   like any other. This is the form every anchor carried across the corpora this rule was measured
   on, which is why it is tried first and not why it is the only branch.
2. **A heading path naming no `§` number** — written, for a nested path, with ` › ` between
   headings in every form: in a document anchor (`Feature A › Acceptance criteria`), and after the
   file's own path in the two path-prefixed forms (`source/appendix/fields.md › Reports › Columns`
   names the file, then the heading path `Reports › Columns`) — resolves only where it matches
   **exactly one** heading in the file, together with its named ancestors, each in order beneath
   the one before it, compared as text, to the section of the last one named. A path matching more
   than one heading falls to branch 4, whose remedy the operator can actually carry out: correct
   the anchor by hand, naming a parent heading to disambiguate it, or a line range where no parent
   tells them apart. Appendices and Obsidian notes rarely number their headings, and §2's own
   example, `source/appendix/fields.md › Reports › Columns`, is exactly this form.
3. **Otherwise, the line the anchor names** resolves it: a line in the file's body falls inside
   exactly one section, so a line-range anchor is section-resolvable without the writer having
   named a section at all — and where the file has no heading at all, its whole body, after any
   frontmatter block, is that one section (Obsidian notes routinely have none, the title being
   the filename), so any line there resolves here. A line **above the first heading**, in a file
   that has one, resolves to the file's **lead section** — its body after any frontmatter block, up
   to that heading — so an obligation stated there is addressed by a line range and never resolves
   to the first section by proximity. A line inside a frontmatter block lies in no section.
4. **None of the three** — no section reference matching exactly one heading, no unique
   heading-path match, and no line that lands in a section, the lead section included — and the
   anchor does not resolve. It may be
   perfectly well formed; what it is, is unresolvable against *this* file, which is what relation 1
   reports it as, per row.

**The ordering matters more than it looks.** An earlier draft of this section asserted that a leading
section reference is *the* form an anchor carries. It is what every measured anchor happened to have,
and §2 above plus `product-workflows:brd-reader` both sanction the line-range form — so the assertion
promoted an observation about one corpus into a rule the producers do not follow, and would have
stopped a correct intake as a read failure on the first anchor written the other way.

**An image anchor resolves where** its path names an image `brd/brd-figures.md` records as read, and
the quoted element appears verbatim in the content of that image's *Text* fence, an annotation's
*Says*, or its *Flow* — the anchor and a *Says* cell each decoded first (§2.3) — or, for
`annotation <n>`, where the image has an n-th annotation. An anchor
naming an image `brd/brd-figures.md` does not record, an image recorded as *not* read, or whose
quoted element or annotation number is absent, does not resolve — relation 1's, not relation 3's, to
report.

**A quote is a span of what an element holds, so an empty one resolves nowhere.** The empty string
is a span of every string, so `<path> › ""` would meet the verbatim test against any image the run
captured while naming none of its elements — and pass relation 1, whose whole job is to prove the
row traceable, leaving a row that points at nothing. **An image anchor whose quote is empty once
decoded (§2.3) does not resolve**, and relation 1 names it with its `[BR#n]` like any other
unresolvable anchor. **An element with no content cannot be quoted at all**: an unlabelled mark's
*Says*, which §1.2 writes `""`, is this format's way of writing *no label* rather than a string to
quote, as `none` is where §1.2 writes it in place of an absent Annotations table or *Flow* list —
neither is the customer's content, and neither is quotable. **A row drawn from an unlabelled mark
is anchored `annotation <n>`**, the form that names an element by its position rather than by its
content and the only one that reaches a mark with nothing to quote (`agents/brd-reader.md` step 4).
**This is not the *names none of them* case below**, which is a quote two elements both hold: that
quote is real content, it still resolves, and the rules for comparing two anchors turn on it — an
empty quote is content nowhere, which is why it is refused rather than merely left naming nothing.

**Which element an image anchor names** is a second question, asked where two anchors are compared
(`commands/brd-intake.md` Phase 3 matches a returned row to a row on file by it). An image's
transcription has three kinds of element: each region of its *Text* — or, in a region written as a
table's rows, each cell, the span §2 bounds a quote to — each annotation, and each *Flow* edge.
`annotation <n>` names the n-th annotation. A quoted anchor names the **one** element whose content —
a region's or a cell's text, an annotation's *Says*, an edge as its *Flow* item reads, each decoded
first (§2.3) — holds the quote. **A quote found in more than one element names none of them**, though
it still resolves: `"Total"` in two regions, or in a region and an annotation's *Says*, points at
neither, so its writer quotes a span its own element alone holds, quotes an edge whole, or, for an
annotation, writes `annotation <n>` instead (`agents/brd-reader.md`, step 4). Two anchors name the
same element where they name the same image and that element — `annotation 2` and a quote of
annotation 2's *Says* that no other element holds among them.

**Comparing two image anchors takes two more rules**, because a row drawn from an image carries the
plugin's own words and so is reworded between reads while its anchor is not. **Two anchors on one
image whose decoded quotes are identical match**, whatever element either names — including a quote
that names none: the same string quoted from the same image is the same anchor, and a reworded row
under it must meet its row on file rather than be minted beside it. **And where a test asks which
elements an anchor names** — whether a returned row sits under the same element as a row on file
(`commands/brd-intake.md` Phase 3's same-or-new question) — a quote that names no single element
counts as naming every element that holds it.

**Where no anchor in the whole inventory resolves, that is a read failure and is reported as one** —
never as a document with no coverage (`workflows-core:grounding-format` §2.1).

### 2.1 A slice's inventory

A **slice** — a BRD in every respect but its folder name, nested inside its parent's folder as the `PRD-` folder its PRD is authored in (`workflows-core:addressing` §6) —
has no source document of its own: the customer supplied one document, and the slice is a partition
of that document's requirements, not a second document. So a slice holds **no `brd/source/` and no
`brd/brd-defect-log.md` of its own; it inherits both from its parent**, resolved through the
`parent:` key in its `brd-link.md`. A slice's `[BR#n]` and `[DEF#n]` ids are its parent's ids,
unchanged — the identity of a requirement belongs to the BRD that owns the source text, and a slice
cites it rather than minting its own.

A slice **does** hold its own `brd/brd-inventory.md`: the subset of its parent's rows its
`brd-link.md` claims, copied row-for-row with `id`, `text`, `source_anchor`, and `defects` verbatim
from the parent's inventory, in §2's layout — each cell exactly as it stands in the parent's file,
since §2.3's encoding is the same at both levels and a cell copied as written needs no decoding, save
where the parent's file predates that layout: a cell is then taken as that file gives it and encoded
by §2.3 as it is written (§2.3).
**"Its parent" is literal and unambiguous**: nesting is capped at one level
(`workflows-core:addressing` §6), so a slice's parent is always the BRD that owns the source
document — there is no chain to walk and no case in which the named parent holds neither.
The file opens with frontmatter — between `---` lines, as every keyed artifact's is — carrying the
folder's identity and the two facts a reader needs to follow an anchor out of it:

```
---
kind: brd
key: <this folder's key — must match the folder name>
parent: <PARENT-KEY>
source: "<the parent's brd/source/<basename>, relative to the parent's folder>"
---
```

**`source:` names the parent's document itself, and §1.1 says which file in `brd/source/` that is** —
the directory holds the files that document links as well, so the writer of this header reads the
name off the parent's inventory's `document:`, as §1.1 says, rather than taking whatever it finds
there. **Its path is relative to the parent's folder, never to its `brd/`**, and that one base is
what every reader resolves it against: it is `brd/` followed by the parent's `document:` value, which
is relative to `brd/` — `document: "source/brd.md"` gives `source: "brd/source/brd.md"` — written, as
`document:` is, as a double-quoted YAML string. A slice written before 3.7.0 carries the same base,
its value perhaps unquoted, and reads the same.

**`kind:` and `key:` open every inventory, a slice's and a source-owning BRD's alike** — a
source-owning BRD's inventory carries the two and no `parent:`/`source:` pair, because it *is* the
source owner. `workflows-core:addressing` §4 reads a folder's identity off them here wherever no
top-level file carries `key:` beside a `kind:` naming a folder kind (its step 2), which is so of a
source-owning BRD from the moment `/brd-intake` creates the folder: that command writes this header,
with no row, before it copies anything into a new folder, so the folder is never keyless (its
Phase 2), and the `coverage-ledger.md` it later writes at the top level names its own document
(`references/coverage-ledger-format.md` §2), which §4 passes over. A slice's inventory carries the
pair too, but it is never the slice's carrier: the slice's `brd-link.md` holds a folder kind at the
top level, which §4 step 1 finds first. The
`brd/source/` document itself carries neither and never will, because it is the customer's and is
immutable (§1).

**Every `source_anchor` in a slice's inventory resolves against the parent's files, never against
anything inside the slice's own folder** — the slice has no `brd/source/` to resolve into, which is
exactly why the header names the parent's. A slice inventory is never re-extracted from the source by
`brd-reader` and never renumbered; copying is the only way it is ever produced, because
re-extraction would mint a second set of ids for text that already has them.

**The same one hop reaches `brd/source-external/`, `brd/brd-figures.md` and `brd/brd-link-log.md`.** A
slice holds none of them: an appendix or image anchor in its inventory resolves against the parent's
files, exactly as a document anchor resolves against the parent's `brd/source/`.

**`/brd-split` writes a slice's inventory**, at the moment it creates the slice's folder — it is
the only command holding both the parent's inventory and the allocation that says which rows the
slice claims. `/brd-intake` never runs on a slice: there is no document to intake.

**The slice's `brd-link.md` is frontmatter, and its `claims:` list is spelled one way.**
`/brd-split` writes it when it creates the slice (`commands/brd-split.md` Phase 3 step 3), and adds
to or withdraws from `claims:` as its walks settle rows:

```
---
kind: brd
key: ACME-10-1
parent: ACME-10
claims:
  - "[BR#1]"
  - "[BR#4]"
---
```

**Each `claims:` entry is a bracketed `[BR#n]` inside double quotes, one to a line**, and a slice
claiming nothing writes `claims: []`. The quotes are not decoration: YAML reads an unquoted `[BR#1]`
as a flow sequence holding the string `BR#1`, so a reader comparing the entry with a ledger's
`[BR#1]` finds no match, and the claim silently goes missing. A list written before 3.7.0 fixed
this spelling — bare `BR#1`, or `[BR#1]` unquoted — is read id by id, each `BR#<n>` in it naming
`[BR#<n>]`, and `/brd-split` writes it in this spelling the next time it writes the list. Other
fields sit beside these four where a command writes one — `depends-on:`, which
`commands/prd-ground.md` and `commands/brd-package.md` merge in, and `reason:`, which
`commands/brd-split.md` Phase 4.5 writes.

### 2.3 The table files, and the one cell encoding they share

Four of the route's files are markdown tables: `brd/brd-link-log.md` (§1.1), `brd/brd-inventory.md`
(§2), `brd/brd-defect-log.md` (§4) and `coverage-ledger.md`
(`references/coverage-ledger-format.md` §2). Each owner fixes its file's frontmatter, its opening
lines and its columns; **this section fixes the one rule every cell of every one of them is written
by**, and the *Annotations* table of `brd/brd-figures.md` (§1.2) is written by it too. A requirement
quoted verbatim routinely holds what a table cell cannot — a row of the customer's own table, a
multi-line list item — so two things are encoded, and nothing else is:

- a literal `|` is written `\|`, every backslash of a run the customer wrote directly before it
  being doubled first — so their `|` is written `\|` and their `\|` is written `\\\|`;
- a line break is written `<br>`.

Nothing else in a cell is escaped, rewritten or reflowed: a backslash anywhere but directly before a
`|` is written as it stands. **And every cell sits between its delimiters with one space on each
side** — `| <cell> | <cell> |`, an empty cell one space between two delimiters — as every layout
example in these files shows, so no delimiter ever has a character of a cell directly before it. That
is what keeps a cell the customer's text ends with a backslash — `C:\reports\` — from escaping the
`|` that closes it: it is written `| C:\reports\ |`.

**Every read of a cell parses and decodes it by one rule, whatever it reads the cell for** — to show
it to the operator (`commands/brd-intake.md` Phase 4's question, `commands/brd-split.md` Phase 4's
offer and walk), to work from it or hand it to an agent (`commands/brd-split.md` Phase 1.5's
placement, `commands/prd-ground.md` Phase 0 step 8's claim list, which its Phase 5 dispatches), or
to compare it (`commands/brd-intake.md` Phase 3's match of a returned row against one on file,
relation 1's test of an anchor (§2.2), and `references/bundle-packaging.md` §6's corpus parse,
verbatim spans and relation 1):

1. **A row splits into cells on every delimiting `|`** — one that opens the row or has a space
   directly before it, the space the writer puts on each side of a cell. A `|` inside a cell never
   has one: the encoding wrote every literal `|` behind a backslash. So a cell ending in the
   customer's backslash, written `| C:\reports\ |`, still ends at its closing `|`. The separator
   line under a table's header holds no cell, and no read parses it.
2. **Each cell is then decoded**: the one space on each side of it, which is the delimiters', is
   dropped; a run of `2k + 1` backslashes directly before a `|` reads back as `k` backslashes and the
   `|`; and each `<br>` reads back as a line break.

**"Verbatim" means verbatim after that decoding**, and a reader that shows, hands over or compares a
cell undecoded shows, hands over or compares the table's encoding rather than the customer's words.
A cell copied from one of these files into another, both in their owners' layouts — a slice's
inventory from its parent's, a ledger row's `text` from its inventory row — is copied as it stands,
never decoded and re-encoded; a cell read from a file written before its layout was fixed (below) is
taken as that file gives it and encoded by this section as it is written. **The one sequence the
encoding cannot tell apart is a `<br>` the customer wrote**, as a cell of a table in their own
document may: it reads back as the line break it renders as there too, and a text comparison
collapses whitespace after decoding (`commands/brd-intake.md` Phase 3), so the two never compare
differently.

**A markdown link inside a quoted requirement is quotation**: kept as written, never followed and
never repaired, although its target — relative to the file the customer wrote it in — resolves to
nothing from `brd/`. `[fields](appendix/fields.md)` stays exactly that, and so does a quoted
`[[glossary]]`; the copy under `brd/source/` is where it resolves, and rewriting it here would
change the customer's words in the one place they are mirrored. **That holds in the bundle too**:
the de-Obsidianising pass that rewrites the plugin's own links leaves a link quoted in an inventory
or ledger `text` cell as written, as it leaves the customer's own files
(`references/bundle-packaging.md` §2.1).

**A list in a cell** — `defects`, `names`, `evidence`, *Candidates* — is its values separated by
`, `, and an empty list is an empty cell.

**A file written before this layout was fixed is read as it stands**: each reader takes the fields
it needs as that file gives them. §1.1 says what a reader of a pre-layout link log does where the
document's name is not plain, and §4 how a pre-layout defect-log entry's rows are read. **Only a run
that writes the whole file rewrites it in its owner's layout** — `/brd-intake` writing the link log,
as it does on every run, or the inventory's, the defect log's or the ledger's rows
(`commands/brd-intake.md` Phases 2–5), and `/brd-split` writing a slice's inventory and ledger new
(`commands/brd-split.md` Phase 3). A writer that edits a cell in place — for instance `/brd-split`'s
walk writing a disposition, or `/brd-reconcile` writing a defect's resolution or a row's disposition
(`commands/brd-reconcile.md` Phases 8–9) — edits it as the file's own layout gives it, so a
pre-layout file edited that way stays in its layout until a whole-file writer writes it.

## 3. Defect classes

Exactly six. Each fires on a one-line test a reader applies to a single `[BR#n]` (or, for
`conflict` and `duplicate`, to a pair):

| Class | Fires when |
|---|---|
| `ambiguity` | Two competent readers can implement it differently and both be right |
| `conflict` | It cannot hold at the same time as another `[BR#n]`; raised on the row the paragraph below fixes, naming the other |
| `untestable` | No externally observable outcome would distinguish success from failure |
| `unsourced` | It asserts system behaviour that grounding must confirm before it can be built on |
| `duplicate` | It and another `[BR#n]` restate one another, or one is a part of the other; raised on the row the paragraph below fixes, naming the other |
| `scope-leak` | It specifies implementation rather than the outcome required |

`conflict` and `duplicate` always name the other `[BR#n]` involved — a defect of either class
naming no counterpart is incomplete. **Each such relation is raised once, from one end**: a
`duplicate` in which one row is a part of another is raised on the whole, naming its part or parts;
a `duplicate` in which rows restate one another, and a `conflict`, is raised on the lowest-numbered
of its rows, naming the others; and a split's is raised as §2 fixes. Raised from both ends, one clash
would become two defects and two questions to the customer. `unsourced` is a pointer forward: it
flags a requirement whose truth grounding must settle, not a requirement grounding has already
checked and found wanting.

A single `[BR#n]` may carry more than one defect (a requirement can be both `ambiguity` and
`scope-leak` at once); a defect entry is never split across two classes to force a single-class
read.

**A requirement drawn from an image is tested the same way, and two rules follow from where it came
from.** An obligation an image states and **no prose anywhere in the document or its linked markdown**
states carries an `ambiguity` — *"stated only in `<image>` — binding force unknown"* — because one
competent reader builds what is drawn and another does not, and both are defensible; **unless** any
passage linking the image makes it binding by its own words (*"must match the attached"*, *"as shown
in figure 3"*, *"according to the diagram"*). An illustrative or current-state framing (*"for
example"*, *"today the screen looks like"*) does not. And a row drawn from an image that cannot hold
at the same time as a prose row is an ordinary `conflict`, naming that row — both are `[BR#n]`s, so
the rule above that every `conflict` names its counterpart needs no exception. **The classes stay
six.**

## 4. Defect resolution

A defect is **never fixed in the source** (§1). Its `brd-defect-log.md` entry carries exactly one
of these resolutions:

| Resolution | Meaning |
|---|---|
| `customer-amended <SLICE-KEY> <date>` | the customer supplied corrected text; the amendment is in the returned review `/brd-reconcile` read it from — the review of the slice the value names, dated `<date>` (`commands/brd-reconcile.md`, *Resolve the defects the review settled*) — never written back into `brd/source/`, and never into the inventory's or the ledger's `text`, which stay the customer's original |
| `withdrawn` | the customer withdrew the requirement the defect was raised against |
| `resolved-by: <SLICE-KEY>/[CG#n]` · `resolved-by: <SLICE-KEY>/[CD#n]` | a code- or design-grounding finding settled the defect (typically closing an `unsourced` entry), or a customer decision did — the answer to the question the defect raised, or to a rejected row's question that carries it (`commands/brd-interview.md`, *Round 1 is generated from the grounding*), frozen by `/brd-reconcile` |
| `open` | none of the above has happened yet |

**`resolved-by` and `customer-amended` name their slice, each in one spelling.** Grounding, deciding
and reconciling are all slice-only: each slice numbers its own `[CG#n]` and `[CD#n]` from 1 and
keeps its own returned reviews, while this log is the parent's (below) — so once a BRD has two
slices a bare `[CD#2]` may name a record in either, and a bare date does not say whose review holds
the amended text. Each value is qualified by the key of the slice whose finding, decision or review
it is — `resolved-by` in the shape `references/decision-register-format.md` §5 gives a record of
another BRD (`conditional_on: <BRD-KEY>/<decision-id>`): `resolved-by: EPIC-008-01/[CD#2]`, never
`resolved-by: [CD#2]`; and `customer-amended EPIC-008-01 20260422`, never
`customer-amended 20260422`. A bare `customer-amended <date>` written before 3.7.0 names no slice,
and a reader looking for its text asks which slice's review holds it rather than guessing.

**The defect log's layout is fixed** — one entry per `[DEF#n]`, one table row each, its cells
written by §2.3's encoding:

````markdown
---
kind: brd-defect-log
key: <the key of the BRD that owns the source document>
---

# Defect log: <that key>

| id | class | raised on | names | reason | resolution |
|---|---|---|---|---|---|
| [DEF#1] | ambiguity | [BR#1] | | "every invoice" does not say which invoices one month's report covers | open |
| [DEF#2] | duplicate | [BR#2] | [BR#3], [BR#4] | one list item per field, split from "Every monthly report must include these fields:" | open |
````

`kind: brd-defect-log` names this document, a kind `workflows-core:addressing` §4 passes over, as
§1.1 says of the link log. `id` is the entry's `[DEF#n]`; `class` one of §3's six; `raised on` the
**one** `[BR#n]` the defect was raised on; `names` the counterparts a `conflict` or `duplicate`
names, empty for every other class; `reason` the confirmed reason, as `/brd-intake` Phase 4's
operator confirmed or edited it; `resolution` one of the four values above. **A log holding no
entry** is its frontmatter, its title and the table's header. **An entry written before this layout
was fixed** records every row it was recorded against in one list: a reader takes the first of them
as its `raised on` and every other as its `names`, and `/brd-intake` Phase 4 writes it that way when
it carries the entry into this layout (§2.3).

**A `conflict` or `duplicate` is listed in the `defects` column of the row it is raised on only.**
Its counterparts are named in its entry, never given the id in their own `defects` column — so a
defect's rows are read the same way whatever its class: the row the entry is raised on, which lists
it, and the rows the entry names, which are its context (`commands/brd-interview.md` reads them so;
`commands/brd-reconcile.md`, *Resolve the defects the review settled*, turns on which is which).

**A `[DEF#n]` id is permanent, as a `[BR#n]` is (§2)** — never reused, never renumbered, and never
deleted, its entry with it. Ids are assigned once, in one order across the whole log: **the
inventory order of the row a defect is raised on, then §3's class order within that row, then —
within one row and class — the order `brd-reader` returned its candidates in, and after them the
candidates raised from documentation, in the order `docs-grounder` returned them.** A re-run numbers
the entries it adds the same way, after the highest id on file. So the numbering is a property of
the inventory and the confirmed set, never of the order a walk put questions in. Every
`rejected: [DEF#n]` in a ledger, every `defects` column and every held question naming a defect
depends on it: an id that moved, vanished or came back naming another defect would re-point each of
them without a trace. `commands/brd-intake.md` Phase 4 holds it on a re-run, by matching what a new
extraction proposes against the entries already on file.

There is exactly one **requirement** defect log per source document, held by the BRD that owns that
document; a slice reads its parent's rather than keeping one of its own (§2.1). That is a statement
about `brd/brd-defect-log.md` and about `[DEF#n]` only: the route's **code**-defect log,
`code-defect-log.md`, is a different register with a different owner —
`references/code-defect-log-format.md` §6 — and a slice keeps its own, because a code defect belongs
to the slice's own grounding and grounding is slice-only. A consumer that must reach a `[DEF#n]`
while standing on a slice — `/brd-split`'s `rejected: [DEF#n]` resolution when it walks a slice's
ledger (`commands/brd-split.md` Phase 4), `/brd-reconcile` writing the
`customer-amended <SLICE-KEY> <date>`, `withdrawn` and `resolved-by: <SLICE-KEY>/[CD#n]` resolutions
a returned customer review settles (`commands/brd-reconcile.md`), `/brd-interview` reading the open
entries its requirement-defect question source asks (`commands/brd-interview.md`), or any reader
following the `defects` column of the slice's copied inventory row — therefore looks it up in, and
writes it to, the parent's log. That lookup is always **exactly one hop**: nesting is capped at one
level (`workflows-core:addressing` §6), so a slice's parent always owns the source document and the
log, and there is no chain to walk.

A resolution changes the defect log entry's status only. It never touches `brd/source/`, and it
never assigns the requirement a disposition — the disposition vocabulary and the artifact that
carries it belong to `references/coverage-ledger-format.md`, not to this file.

## 5. Non-goals

This reference does not describe a PRD. `workflows-core:prd-format` is the sole authority for what a Product
Requirements Document contains and how it is authored; nothing here substitutes for it, and a BRD
inventory row is never treated as PRD content in its own right.

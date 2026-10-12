# Bundle packaging (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

How the customer-facing bundle for a BRD→PRD package is built, what it may and may not contain, the
three degradation tiers a bundle can ship at and what each obliges the reviewer to state, the
delivery note's hard length rule, and where the rendered bundle lands and why it is committed.
Design authority: `docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` §8.1, §8.3 and
§8.5, and decision rows D12, D13, D18 and D20 in §3 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-brd-to-prd-workflow-design.md` retrieves it).

Neighbouring rules are owned elsewhere and cited, not restated: the twelve sections a returned
review carries, and the constraint that governs the one file rendered verbatim into the customer's
prompt, belong to `references/customer-review-schema.md`; the finding record and the
`baseline-integrity` procedure whose three commands the prompt hands the reviewer to re-run belong
to `workflows-core:grounding-format` §2 and §4, and its reading rule and its class-4
citation-correctness rule, both of which §6 cites rather than restates, belong to §2.1 and §6.3 of
the same file; the `[CD#n]`/`[AS#n]` record shape, `conditional_on`, and the rule that every open
`[AS#n]` reaches the customer belong to `references/decision-register-format.md` §1, §5 and §7; the
coverage ledger's dispositions belong to `references/coverage-ledger-format.md` §3; the `<BRD-KEY>`
grammar and BRD-folder resolution belong to `workflows-core:addressing` §1 and §3; the commit entry
point every bookkeeping write into the specs repo runs through belongs to
`workflows-core:specs-repo-git`.

**Consumed by `commands/brd-package.md`**, which builds a bundle against this contract — its
plugin-free rules, its §1.1 content allow-list, its de-Obsidianising pass, its degradation tiers,
its delivery-note ceiling, its committed dated directory and its §6 citation-resolution check — and
cited by `agents/brd-package-reviewer.md` for what the customer will actually be able to open.
`commands/brd-reconcile.md` reads a review returned against a bundle built this way, and cites §5
for why nothing inside that committed directory is ever bannered or rewritten afterwards. Commands
upstream of the package cite it too, for what they write that a bundle will later carry —
`commands/brd-interview.md` (§1.1, §6.2's cross-BRD id spelling and relation 1, §6.3 rule 1) and
`commands/prd-ground.md` (§1.2's classes, which it scans what it writes against, and §6.2 relation 2) — as do several of this plugin's references; `grep -l
bundle-packaging commands/*.md agents/*.md references/*.md` lists every file that cites it.

## 1. Plugin-free by construction (D12)

The bundle must work for a reviewer with a vanilla agent and **nothing installed** — no plugin, no
skills, no MCP server. That is not a nice-to-have: no customer can be required to install anything
in order to review what was sent to them. Four rules follow, and every one of them is about what the
bundle may assume of the machine it lands on.

1. **The prompt is self-contained.** No path rooted at the plugin's install directory, no slash
   commands, no skill invocations, no MCP assumptions. The review schema is **inlined** — rendered
   from `references/customer-review-schema.md` at build time rather than quoted, summarised, or
   linked, so the shipped prompt and the authority cannot drift apart — and **never the whole
   file**: that file states which part of it is rendered, and `commands/brd-package.md`'s
   `render-schema` entry point states what the prompt's part 10 takes. That file also carries its
   own plugin-free constraint; nothing here overrides it.
2. **No harness-specific instructions.** The prompt is written in the vocabulary any agent has —
   *read the file named X*, *search this bundle for a file whose name contains Y*, *run this in a
   terminal*. It states its assumed capability set in one line at the top, so a reviewer on a weaker
   tool learns immediately what they cannot do, rather than discovering it four sections in.
3. **The bundle is de-Obsidianised.** §2.
4. **Documents are located by filename search, not by path.** Every reference from one bundle
   document to another, and every instruction in the prompt that sends the reviewer to a document,
   names a **filename** and tells the reviewer to search for it.

**Why filenames and not paths.** A path is correct exactly once, in the directory layout the
packaging machine had, and **both delivery routes break it**. On the archive route the bundle is
extracted and renamed, landing in whatever directory the reviewer keeps attachments in. On the
repository route it is not renamed at all — and the path is wrong anyway, because the reviewer's
checkout is not the packaging machine's. Naming only the archive case here read as though a
committed bundle could safely be addressed by path, which is the one reading that would break rule 1
for the route this plugin now recommends; a filename survives extraction, renaming, re-zipping, being mailed on to a colleague, and being
dropped into a different tool. The cost is that filenames must then be distinctive enough to search
for, which is a constraint on how bundle documents are named, not a reason to fall back to paths.

### 1.1 What the bundle contains — an allow-list, and why it is not a deny-list

**A document reaches the bundle only where a part of the rendered prompt sends the reviewer to it.**
That is the whole rule, and it is stated as an **allow-list** rather than as "the package's
documents, minus the following" for one reason: a deny-list is silent about every artifact nobody
thought of, and the BRD folder accumulates artifacts. Under a deny-list a new working record ships
by default and is caught only if somebody remembers to exclude it; under the allow-list it stays by
default and ships only once a prompt part actually cites it. The failure mode is not symmetric — a
document wrongly withheld produces a reviewer question, and a document wrongly shipped cannot be
recalled — so the default belongs on the side of withholding.

Exactly this, and nothing else:

| In the bundle | Which prompt part sends the reviewer to it |
|---|---|
| the rendered customer prompt | it is the entry point |
| the customer's own source document — `brd/source/<basename>`, **the parent's on a slice** (`references/brd-format.md` §2.1) | requirement traceability: the review's own section 4 asks whether the package read the customer's document correctly, which is unanswerable without that document |
| every other markdown file `/brd-intake` captured — `brd/source/<file>.md` beside the document and `brd/source-external/<file>.md` from outside its folder, **the parent's on a slice**, one hop (`references/brd-format.md` §1.1, §2.1) | requirement traceability, for the same reason: a `[BR#n]` anchored in an appendix (`references/brd-format.md` §2) is unanswerable without that appendix |
| `brd/brd-inventory.md` | *Review scope* |
| `brd/brd-defect-log.md` — **the parent's on a slice**, one hop, exactly as an inherited `[DEF#n]` already resolves (`references/brd-format.md` §4) | *Review scope*: a ledger row reading `rejected: [DEF#n]` cites an id the reviewer must be able to resolve |
| `brd/brd-figures.md` — **the parent's on a slice**, one hop, as the defect log is, and only where the file exists | requirement traceability: the review's section 4 asks the customer to confirm or correct the package's reading of their document, and this file is its reading of their images (`references/brd-format.md` §1.2) |
| `coverage-ledger.md` | *Review scope*, and *what this session cannot settle* |
| `code-defect-log.md`, when the folder holds one | *Review scope*, *what could still move*, and *what this session cannot settle* — a defect disposed `in-scope` **is** the delivery boundary |
| `grounding/code-grounding.md` and `grounding/design-grounding.md` | *the single most important claim to verify first* |
| `grounding/baselines.md` | *code baselines and the verification procedure* |
| `decisions.md` | *the single most important claim to verify first*, *the decisions the customer must make*, *what could still move* |
| `interview/customer-questions.md` | *the decisions the customer must make* |
| every prerequisite package copied in, marked *not for re-review* | *what each package in the bundle is for* |
| every image the documents above reference, and every image `brd/brd-figures.md` holds a section for — save one whose section carries the marker `references/brd-format.md` §1.2 fixes and whose *Rows* line yields no row | the documents embed them (§2), and a figures section sends the reviewer to the picture it transcribes — as does an image anchor or a question naming the image. A marked image is one the latest intake did not capture, so it ships only where a preserved row still anchors on it: the customer needs the picture to check that row |
| the manifest | *documents to review* |

Plain markdown and images — nothing else (§2). **A file `/brd-intake` captured that is neither —
`pricing.pdf` and its kind — is therefore not in the bundle, and that is a disposition rather than
an omission**: §2's rule admits two file kinds and the allow-list above is closed, so there is no
row it could take. It is named in the manifest as **captured and not bundled**, beside the captured
file it was linked from, and every link to it inside a rendered document becomes the plain
description §2's third link case requires — so a reviewer who meets the link learns what stood
there and that it was withheld, rather than searching the bundle for a filename nothing carries.
The customer's own byte-for-byte files still link to it as they always did (§2.1), which is why the
manifest entry exists at all. The manifest lists documents by filename, for the
same reason rule 4 does, **and maps every file `/brd-intake` captured that the bundle carries — each
markdown file and each image from `brd/source/` and `brd/source-external/` — from its path relative
to `brd/` to its bundled filename**, the name carrying the `<BRD-KEY>-` prefix that
`commands/brd-package.md`'s *Assemble the bundle* rule 1 gives every bundled file, an image's
included. That path is the form every reference to a captured file takes:
a figures section's heading, an appendix or image `source_anchor`, and an interview question naming
an image (`references/brd-format.md` §1.2, §2). None of them is a bundle filename, so without the map
a reviewer who searches by filename, as rule 4 tells them to, finds nothing.

**The figures file ships without its frontmatter.** Every field in it is the specs tree's
bookkeeping rather than anything a reader outside the vault can use (`references/brd-format.md`
§1.2), so the de-Obsidianising pass removes it whole, as it removes any frontmatter that means
nothing to a reader outside a vault (§2), and leaves in its place the one-line note that pass
requires. That note names the customer's document by its **bundled** filename. `key:` is how the
specs tree ties the file to its BRD — the BRD that owns the source document, which on a slice is the
parent while the bundled filename carries this package's key; the file carries no `kind:`
(`references/brd-format.md` §1.2) — and what it identifies reaches the reader through the note
instead, which names the very document the transcriptions are of.
`written_by:` names the plugin's own command, which no bundle document may name
(`commands/brd-package.md`'s standing rule). `source:` names the customer's document by its working
basename, and the bundle renames that document (`commands/brd-package.md`'s *Assemble the bundle*
rule 1), so kept as written it is exactly the working-filename reference §6.2's relation 3 stops on.
It is plugin-written, and a bare basename rather than a locator in §6.3's sense, so no exemption
there reaches it. The note carries the one fact `source:` held, in the form the reviewer can search
for.

**The code-defect log ships, and the reason is scope rather than disclosure.** A `[CDF#n]` disposed
`in-scope` names a repair that has to happen inside this PRD's scope or the feature cannot be
delivered (`references/code-defect-log-format.md` §4). A `[VD#n]` whose real basis is such a repair
is a decision the customer cannot evaluate without it — which is exactly the failure
`references/decision-register-format.md` §2 exists to prevent, displaced out of `argumentation` and
into a file nobody sends them. Withholding it would also have been **concealed but reachable**: a
customer who pulls the specs repository rather than taking the archive can open every file in the
folder, so the rule would have held on one delivery route and failed silently on the other.

**What the bundle does not contain**, each named because each is a document sitting in the same
folder under the same `<BRD-KEY>`-and-date naming, indistinguishable from a package document by
filename alone:

- **The delivery note** (§4). It is the covering letter, not a package document.
- **`self-review-<YYYYMMDD>.md`.** This is the one exclusion that is a *rule* rather than a
  consequence of the allow-list, and it is load-bearing: that file holds every `[SR#n]` the
  adversarial pass raised, including the ones disposed `rejected-with-reason`, whose reason
  "stays inside the delivery organisation. Nothing rejected reaches the customer"
  (`commands/brd-package.md`, *The disposition gate*). The `[SR#n]` content the customer may see is
  carried into the prompt **filtered** — `accepted-risk` findings under *where to attack us hardest*
  and `escalated-to-customer` findings under *the decisions the customer must make* — so shipping
  the file itself would defeat that filter and hand the customer an internal disagreement to
  referee. It also carries the model the pass actually ran on, which is delivery-side bookkeeping.
- **Every other working record in the BRD folder** — among them `slices.md`, `brd-link.md`, the
  three seed files, `interview/round-<N>.md`, earlier `reconciliation-<YYYYMMDD>.md`, earlier
  `customer-review-<YYYYMMDD>.md`, and `dev-workflows/`. No prompt part sends the reviewer to any of
  them.

**The plugin-free scan does not cover this.** It hunts plugin-internal tokens (§1 rules 1–2, of
the classes §1.2 tabulates), and
every document above is free of them whether or not it belongs in a customer's hands. Nothing
mechanical stands behind this allow-list, which is why it is written out rather than left to
"the package's own documents".

### 1.2 The plugin-free scan's classes

`commands/brd-package.md`'s plugin-free scan stops on a token of any of these classes, over the
finished prompt, the finished delivery note and every document in the finished bundle — the only
exemptions being the customer's own words and naming, which §6.3 defines:

| Class | Examples |
|---|---|
| A path rooted at the plugin's install directory | the plugin-root variable, in any form |
| A reference-file citation | `references/…`, a bare `workflows-core:<name>` loader argument, the `Skill(skill: "workflows-core:reference", …)` call itself, `docs/superpowers/…` |
| A numbered cross-reference in this plugin's notation | any `§` |
| A slash command | `/brd-…`, `/dev-workflows:…`, `/workflows-core:…`, any leading-slash command name |
| An agent, subagent type or skill name | `subagent_type`, any `<plugin>:<name>` prefix (`dev-workflows:`, `workflows-core:`, and any namespace a later split adds), any agent filename |
| A decision-row reference | `D12`, `D13`, `D18`, `D20`, or any other bare `D<n>` row id |

**The table is here, rather than in the command that runs the scan, because most of the bundle's
documents are written long before it runs**, by earlier commands of the route, and a token one of
them writes stops the package days later, where the only repair is a hand edit to a record the
operator did not write. A writer can hold its documents to these classes when it writes them instead.
One writer checks what it writes against this whole table today: `commands/prd-ground.md` scans
what it is about to write into the three grounding files, and rewrites a sentence that hits rather
than deleting its token (`workflows-core:grounding-format` §2.3 is the writing rule).
`commands/brd-interview.md` guards the one class its customer questions meet, writing a customer's
section as `source/<basename> › § <n>` (§6.3 rule 1). That write-time check is a
first line, never a substitute: `commands/brd-package.md` still runs its own scan over the finished
bundle, exactly as strictly, because it is the last point at which anything is still ours.

## 2. De-Obsidianising

The working documents live in the specs repository, which is a git repository and not a vault, and
carry wikilink syntax anyway — `[[KEY]]` is the specs tree's traceability form, and the customer's
own source document arrives with whatever its author wrote. The bundle is a **rendered copy**,
produced on the way out; the working documents keep their wikilinks and are never rewritten in
place. A de-Obsidianising pass that edits the source is a data-loss bug wearing a formatting fix.

**Wikilinks are rewritten to plain filename references** — every one this package wrote, and none it
quotes from the customer (§2.1). `[[Some Document]]` resolves to nothing outside a vault: in every
other reader it is literal text with brackets around it, and a reviewer who clicks it, searches it,
or asks an agent to open it gets nothing. It is worse than a missing link, because it looks like a
link. The rewrite names the target file as the reviewer will actually see it, so it can be searched
for.

Three cases the rewrite has to get right:

- **An aliased link** (`[[Some Document|the ingest contract]]`) keeps the alias as the visible text
  **and** names the file. The alias alone names nothing the reviewer can search for; the filename
  alone loses the phrasing the sentence depends on.
- **An embedded image** becomes an ordinary markdown image reference to the image file copied into
  the bundle beside it. An image that is not copied has no reference left behind pointing at it —
  the embed is replaced by a plain sentence saying what was there and that it is not included.
- **A link whose target is not in the bundle** is **never** rewritten into a bare filename. A
  filename that is not in the bundle is the failure mode this whole section exists to prevent: it
  looks resolvable, the reviewer searches for it, finds nothing, and cannot tell whether the file
  was forgotten, withheld, or renamed. Such a link becomes a plain description of the target and an
  explicit statement that it is not included.

**The three cases above are about rewritten links, and the rule does not stop there.** A bundle
document that names a file **in prose** — not as a link — makes the identical promise to the
reviewer and breaks it the same way. That is not hypothetical: a shipped bundle named
`self-review-<YYYYMMDD>.md`, which §1.1 excludes by rule, in ordinary prose, and named three
grounding files by their working filenames after this pass had renamed them. Both survived
everything, because a rewrite rule inspects links. §6's relation 3 covers prose and links alike.

### 2.1 The customer's own documents are copied byte for byte, never rendered

**The de-Obsidianising pass does not touch the customer's own files: `brd/source/<basename>`, and
every other markdown file `/brd-intake` captured under `brd/source/` or `brd/source-external/`** (§1.1;
the parent's, on a slice). Each goes in as the bytes `/brd-intake` copied, unrewritten, unreflowed,
and with nothing removed — even where it carries something that renders in exactly one tool. Three
reasons, and each is fatal on its own:

- **Every `[BR#n]` drawn from their text anchors into them by `source_anchor`**, in the forms
  `references/brd-format.md` §2 fixes; an image-drawn row anchors on the image, which ships beside
  them. A rendered copy moves lines and can rewrite headings, so a requirement's anchor stops resolving in
  precisely the copy the customer was given to check traceability against. Requirement traceability
  is the *reason* these files are in the bundle at all; a pass that breaks it defeats the inclusion.
- **They are immutable by rule** (`brd-format.md` §1, and §1.1 for `brd/source-external/`): nothing
  under either directory is ever edited, reworded or reformatted, "no matter how badly worded a
  requirement inside it is". A bundle copy that has been tidied is an edit the rule forbids, made
  where nobody looks for one.
- **They are the customer's own writing, handed back to them.** §3's one-new-file rule exists so that
  "nobody can otherwise tell what was sent from what was changed"; returning their documents
  reformatted is that failure committed by the delivery team first.

**The customer's words quoted in the inventory's and the ledger's `text` cells, and in a `[CD#n]`'s
quoted `argumentation` and `chosen` (§6.3), are left as written too — and so is an `[SR#n]`'s
`target`, `attack` and `what_would_settle_it`, which `commands/brd-package.md` renders into the
prompt's *where to attack us hardest* and *decisions the customer must make* parts and states are
not its to change.** A reviewer's attack that quotes a customer's `[[wikilink]]` sits at the exact
point where that rule and this pass disagree, and the rule wins: the quotation is somebody else's
words, which is the reason this section gives for the cells beside it, and a pass that rewrote it
would edit an attack the package is forbidden to reword. A link or a `[[wikilink]]`
there is quotation (`references/brd-format.md` §2.3 for a cell), not a link this package made, so
the pass rewrites none of it, exactly as it rewrites nothing in the files the text is quoted from;
the rest of those files is the plugin's writing and is rendered as §2 says.

Where that leaves something a plain reader cannot open — an embedded image, a one-tool block — the
fix is **beside the file, never inside it**: copy the image in as §2 already requires, and say in the
manifest what the reader may not be able to see. The manifest is prose this package wrote and may
say anything; the customer's files are not.

**An image a captured file reaches through a `[[wikilink]]`, or from outside the document's own
directory, is found through `brd/brd-link-log.md`'s *Captured links that do not resolve as written*
table** (`references/brd-format.md` §1.1), its cells decoded before a target is compared
(`references/brd-format.md` §2.3) — on a slice the parent's log, one hop, as the document is
(`references/brd-format.md` §2.1). Its copy is in `brd/source/` or `brd/source-external/`, at a path
the target as written does not name. It is copied into the bundle like any other image, and its
manifest line (§1.1) names the target as written as well as its path relative to `brd/`: the file
the link sits in is never edited to point there.

**Callouts are kept.** A `> [!note]` block degrades to an ordinary blockquote in any markdown reader
— the reader loses the label's styling and keeps every word. Nothing that survives untranslated is
worth translating.

**Plain markdown plus images, and nothing else.** No canvas or database-view files, no query or
dataview blocks that render as an empty region in any other tool, no plugin-specific embed syntax,
no frontmatter that means nothing to a reader outside a vault. Anything that renders in exactly
one tool is either converted to something that renders everywhere or removed with a note saying what
stood there. A block that silently renders as nothing is the same defect as the dead wikilink: the
reviewer cannot see that they are missing something.

## 3. Degradation tiers

A bundle ships at one of three tiers. The tier records **what the reviewer was actually able to be
given**, and the prompt states it explicitly along with the sentence the reviewer's own
evidence-limitations section must then carry.

| Tier | The reviewer has | What their review must state about its own evidence |
|---|---|---|
| Full | The documents, plus repositories pinned to the commits the package cites | That code claims were independently verifiable, and what the pin-verification procedure returned when they ran it |
| Partial | The documents, plus repositories that are not pinned — an archive of a moving branch | That every code claim they confirm is true of **an unidentified snapshot**, because nothing ties what they read to the commit the package cites |
| Documents only | The documents, and no repositories | That **no code claim in the package was independently verified** by this review |

**The tier is assigned from what was shippable, not chosen by the reviewer.** It is a fact about the
bundle, established when the bundle is built and written into the prompt. A reviewer cannot promote
themselves to Full by being thorough, and the bundle is never quietly shipped at Full because the
repositories were *probably* at the right commit — an unpinned archive is Partial, and it says so.

**A tier is not a quality grade.** A documents-only review that states its tier is more useful than
a full-tier review that does not: the first can be weighed correctly, the second cannot be weighed
at all. This is the whole purpose of the tier reaching the customer — it is what makes a returned
review honest about its own limits, and therefore readable.

**The failure this prevents** is a package built on confirmations whose evidentiary weight nobody
recorded. Months later the review is the record, and a confirmation that was in fact an unverified
reading of a document is indistinguishable from one checked against a pinned commit — unless the
review said which it was, at the top, before the confirmations.

## 4. The delivery note

The covering letter that goes in the email body. It is written to a file in the BRD folder and
printed in full before the run offers to send it, so the operator reads what they are being offered
and can paste it without opening anything. **It is not part of the bundle** — it is the email, not a
package document, and a copy of it inside the bundle would be a second, divergent statement of what
was sent.

**Hard length rule: 200 words.** Not a target, a ceiling. Past roughly that length the note stops
being a covering letter and becomes a document, and a document is precisely what nobody reads before
clicking into the attachment — or, on the repository route, before pulling and opening the folder —
which puts the two facts that must not be missed back inside the thing they were lifted out of.

It states only:

- which BRD this is
- **how the customer gets the bundle** — what is attached, or where it is committed and how to reach it. This is the one document that names a delivery route, and it can, because it is written to a specific customer whose situation the operator knows
- which repositories, at which commits
- **which file is the prompt** — the one file to paste
- **which file comes back** — the one file to send, named exactly, and, on the repository route,
  where to commit it (§5, *The review comes back the way the bundle went out*)
- any prerequisite whose decisions are still provisional, and that positions resting on it could
  move (D20)
- anything else that must not sit buried inside a document

**It is not a per-file table.** The manifest inside the bundle covers per-file detail, and
duplicating it in the note guarantees the two disagree after the first correction. The note answers
what the reader needs before they open anything; everything else is inside.

**Why the two bolded items are bolded.** The single most common failure of this loop is a reviewer
who reads the documents, forms a view, and writes it into an email or a document of their own
devising — because nothing they read in the first thirty seconds told them there was a prompt to
paste and a named file to return. Both facts are one line each, in the covering letter, where they
cannot be missed.

## 5. Where the bundle lands

The rendered bundle is written to **`bundle-<YYYYMMDD>/` inside the BRD folder** — resolved per
`workflows-core:addressing` §3 — and **committed to the specs repo** (D18), as a **deliverable**:
through `handoff-to-main` (`workflows-core:phase-handoff` §2), behind that reference's §4.3 consent
choice, with every file under the dated directory in the calling command's `deliverable_paths`.

**Not through `workflows-core:specs-repo-git`, and the difference is not pedantry.** That reference
owns the plugin's *bookkeeping* commit, and its §2.1 bounds staging to a fixed, enumerated set of path
shapes — a bundle matches none of them, so `commit-artifacts` cannot stage one and
was never meant to. A reader sent to the wrong entry point finds the bundle missing from §2.1 and
reaches for the plausible repair, which is to widen those path shapes; that would let the prompt-free
bookkeeping step commit a customer-facing deliverable with no consent choice in front of it, which is
exactly the boundary the two references were split to hold (`workflows-core:phase-handoff` §1 rule 7).

**"Committed" therefore means "committed where the operator accepted the handoff".** Declining §4.3's
choice leaves the bundle written and uncommitted, and the run says so — D18 is what the accepted path
achieves, not something this file can assert of every run.

For a synthetic BRD `EPIC-008` packaged on 15 April 2026, that is `bundle-20260415/` beside the
package's other dated artifacts.

**The prompt names no delivery route; the delivery note names the actual one.** They have different
readers, and that is what settles which may assume anything. The note is a covering letter to a
named customer, so the operator writing it knows whether they will pull the repository or receive an
archive, and §4 requires the note to say which. The prompt is handed on — to a colleague, to an
agent, to whoever actually does the review — and the run has no way to know who that is or how the
bundle reached them, so a prompt that names a route is a prompt that is wrong for some of its
readers about the first thing it tells them. Its locating instruction is therefore written to be
true either way, and the **archive command never appears in it at all**: assembling an archive is a
delivery-team action, not a reviewer's, and a reviewer who was sent one has already had it done for
them.

**Committing it serves both delivery routes with one artifact.** A customer with access to the
repository pulls the bundle directly and needs nothing else. Everyone else gets **one archive
command** — producing a single archive of the whole dated directory, in a format the customer can
open without installing anything. One command, because the population that cannot pull the
repository is exactly the population that will not assemble an archive command themselves.
**It is produced only where the archive is the route actually being used**, which the calling
command settles once, at the delivery note. The repository route is true only once the bundle is on
the specs repository's default branch — the handoff's pull request merged; a bundle on no ref, on a
commit only the packaging machine holds, or on a branch not yet merged is a bundle a customer
pulling the repository does not find — but the note is itself one of the files that handoff
commits, so the route is settled from what the run holds before it: whether the specs repository
passes `workflows-core:phase-handoff` §2.1's gate, whether its push-target probe finds a remote to
push to, and the handoff's consent, taken there. The note names no branch; what makes it true on
the outcome the handoff got — the branch and pull request it pushed, any declared path it staged
nothing for, or what must happen first — is settled by the handoff and printed beside the note,
in the delivery-route item that stands between the printed note and the offer to send it
(`commands/brd-package.md`'s *Render the delivery note*, *Handoff* and *Next steps*).

**The review comes back the way the bundle went out.** On the repository route the customer can
reach the specs repository, so the note asks them to return their review there too: committed into
the folder that holds `bundle-<YYYYMMDD>/`, under the exact name the prompt gives it, on a branch of
their own with a pull request against the default branch — one added file and nothing else, since a
correction they want made to the package goes in the review's section 12, never into the bundle.
`commands/brd-reconcile.md` then finds it there once the operator merges that pull request, asks the
operator to confirm it, and moves it to its canonical name. Before that confirmation it lists
anything else the pull request changed in the slice's folder — a package document edited there
would leave the customer's quotations checked against a document they were never sent — and then
does not recommend going ahead, leaving the operator to reconcile or to restore first. A customer who cannot
push sends the file back instead, as on the archive route, where the review arrives as a file and
the operator passes its path. The prompt says none of this — it names no route (above) — so the
note is where the return route is stated, beside the delivery route it mirrors.

**The committed copy is the permanent record of exactly what was sent.** This is the point of D18
and the reason the cost is worth paying: it is what makes the byte-identical property behind the
one-new-file rule checkable months later. When a returned review quotes a sentence, there is a
committed copy of the document that sentence came from, at the version the customer actually
received — not a reconstruction from the working documents, which have moved on.

**A dated bundle is never rewritten.** A second package for the same BRD is a new dated directory
beside the first, not an edit of it. Rewriting `bundle-20260415/` destroys the only evidence of what
the reviewer of that date was looking at, and every claim in their returned review silently
re-points at a document they never saw.

**The acknowledged cost** is a derived duplicate in the repository: the bundle's documents are
rendered copies of documents the repository already holds, and each package adds another dated
directory. That is deliberate. A derived duplicate that is never rewritten is a cheap price for a
record that is still true when somebody re-opens the argument a year later.

## 6. Citation resolution

**`citation-resolution`** is a check over the assembled bundle that the plugin-free scan (§1)
does not perform. That scan deliberately exempts identifiers — the nine classes §6.1's table
covers, `[BR#n]`, `[DEF#n]`, `[CG#n]`, `[DG#n]`, `[VD#n]`, `[CD#n]`, `[AS#n]`, `[CDF#n]` and
`[SR#n]`, are how a returned review cites the package's own claims without minting identifiers
of its own, and a prompt that hid them would get back a review nothing could be matched to.
**Nothing then checks that they land.** Three failures were observed in shipped bundles: a
class-4 design finding whose `[CG#n]` citation resolved, inside the customer's own bundle, to a
real finding about a different requirement; a reference naming an id above the highest its own
corpus contains — one of them the sole `evidence` on a decision record; and a reference, in
prose rather than a link, to a document §1.1 excludes by rule or has already renamed on the way
in. Three stops carry it: `BRD_PACKAGE_DEAD_CITATION` for a reference that resolves to nothing
(§6.1's unkeyed-document case, §6.2's relations 1 and 3), `BRD_PACKAGE_CITATION_MISMATCH` for
one that resolves to the wrong requirement (§6.2's relation 2), and
`BRD_PACKAGE_CORPUS_UNREADABLE` for a corpus that cannot be parsed (§6.1). A fourth,
`BRD_PACKAGE_CUSTOMER_CONTENT_HELD`, is no failure of the check: it is the operator holding the
package over a hit in the customer's own words, on the question §6.3 fixes. Design authority:
`docs/superpowers/specs/2026-09-08-bundle-citation-resolution-design.md` §3–§7 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-09-08-bundle-citation-resolution-design.md` retrieves it).

### 6.1 The corpus is built per source package, and never crossed

A prerequisite package is copied into the bundle wholesale (§1.1), carrying its own grounding files,
its own inventory and its own register — each numbered from 1 in its own corpus. So one bundle can
hold two different `[CG#7]`s. Bundle documents therefore **partition on the `<BRD-KEY>` each one's
own filename carries**: `commands/brd-package.md`'s *Assemble the bundle* rule 1 gives every bundle
document a filename carrying its `<BRD-KEY>`, unique within the bundle, precisely so documents are
located by **filename search, never by path** (§1 rule 4) — and that same guarantee draws the
partition boundary. Partitioning by subtree instead would tell an executor to use a path inside a
bundle whose whole addressing convention is path-free, and would make the boundary a property of
where a document sits rather than of what it says: a later change that flattened the bundle would
then silently resolve every id against one corpus and **pass**. Keying on the filename removes that
failure rather than mitigating it — a flattened, renamed or re-archived bundle partitions
identically, because the discriminator travels with the document.

**The key in a document's name is its own package's key, never this run's applied uniformly.** A
prerequisite package copied in (rule 5) arrives already named from the packaging run that built it,
and those names are kept on the way in — nothing renames them — so rule 1's `<BRD-KEY>` means *the
key of the package the document belongs to*. Read the other way, rule 1 would prefix every document
with this run's key, yield **one** partition, and resolve a prerequisite's `[CG#7]` against this
package's `[CG#7]`: a cross-package citation resolving to the wrong finding, and the check going
green. That is the flattened-bundle silent pass this partition was chosen to remove, one level down.
**The partition key is resolved against the key set the run already holds** — this run's key plus
every prerequisite key Phase 2 carried — never parsed out of a filename (`workflows-core:addressing`
§1 fixes the grammar; `workflows-core:specs-repo-git` §3.5 is the worked example of resolving
against a set instead). That is also what makes the unkeyed-document stop below decidable rather
than a guess: no candidate in the set matches.

**Vacuity guard.** A bundle into which a prerequisite package was copied and which nonetheless
partitions to **one** is a collapsed bundle, not a clean one: the names were flattened onto this
run's key, and every id in that package's documents is being resolved against another package's
corpus. So every prerequisite key **whose package was copied in** must answer to a partition, and
one that answers to none stops the run with `BRD_PACKAGE_DEAD_CITATION`, naming the key and the
package — the same disposition an unkeyed document gets below, for the same reason. Asserting it
costs one comparison, and it is the shape this repository's own build gates already use for a
coverage relation: a relation that comes up empty fails rather than passes, because empty is what a
silently broken derivation looks like.

**The guard reads Phase 2's own carry, and a prerequisite with no package copied in is not a
defect.** `commands/brd-package.md` Phase 2 records, per prerequisite, *whether a package of its own
was found* — that field is the discriminator, and nothing new is derived here. Two of its branches
carry a prerequisite key with nothing to copy in, and neither stops there: step 1's *BRD not found*,
and step 3's *no package on file; nothing to copy in*. Such a key contributes **no partition**,
correctly, and the guard passes over it. Testing every carried key instead would stop both of those
ordinary runs on content that is right — the collapse this guard exists for is a package that *is*
in the bundle under names that were flattened, which is a different state from a package that was
never copied in. §6.2's relation 1 disposes of the other half of that same state — a
structured field naming a record of a prerequisite whose package is absent, `conditional_on` being
the worked case: qualified rather than resolved, precisely because no partition could ever hold it.
The two sections describe one state and must not be read against each other.

Each partition parses its own corpus, and **each corpus file is located by filename search within
the partition, never at the working path named below.** The working names identify *which* document
each corpus is; inside the bundle that document carries its `<BRD-KEY>-` prefixed name:

| Class | Corpus file, within the partition |
|---|---|
| `[BR#n]` | `brd/brd-inventory.md` — on a slice its **own**, defined over `claims:` (`references/brd-format.md` §2.1) |
| `[DEF#n]` | `brd/brd-defect-log.md` (the parent's on a slice, one hop — `references/brd-format.md` §4) |
| `[CG#n]`, `[DG#n]` | `grounding/code-grounding.md`, `grounding/design-grounding.md` |
| `[VD#n]`, `[CD#n]`, `[AS#n]` | `decisions.md` (`references/decision-register-format.md` §1 and §7) |
| `[CDF#n]` | `code-defect-log.md` (`references/code-defect-log-format.md` §2) — **absent where the folder holds no entry**, which is an empty corpus and passes |
| `[SR#n]` | **none — exempt entirely, §6.3** |

**Every corpus is parsed, never assumed.** An identifier reference is resolved against the set of
ids actually parsed out of its corpus file, never by matching a fixed column or a fixed run of
leading spaces (`workflows-core:grounding-format` §2.1). That section's own precedent is why: a
column-anchored scan once reported 140 findings as missing that were on the page, because one block
in a `code-grounding.md` padded its `id:` colon for alignment and the next did not. The identical
scan run here, over a bundle's copied corpus files, would report every reference in the bundle as
dead.

**A table corpus is parsed by its owner's layout** — the inventory's, the defect log's and the
ledger's (`references/brd-format.md` §2, §4; `references/coverage-ledger-format.md` §2) — and by the
one parse-and-decode rule `references/brd-format.md` §2.3 fixes for every read: a row splits into
cells on a delimiting `|` only, as that section defines one, and each cell is decoded before it is
read, so a requirement quoting a row of the customer's own table never shifts a column, and an id is
never read out of the wrong one.

**The two rows a slice reads differently differ in opposite directions, and both are stated because
a reader meeting one will assume the other matches.** `[DEF#n]` widens one hop: §1.1 ships the
**parent's** defect log into a slice's bundle, so the parent's log *is* that partition's corpus for
the class. `[BR#n]` does not widen: §1.1 ships the slice's own inventory, which is defined over
`claims:` (`references/brd-format.md` §2.1), and the parent's is not a bundle document at all. So a
`[BR#n]` that a structured field names one hop up — an orphan row's own `id`, a `superseded-by`, a
parent defect entry's counterpart, the *Rows* line of the parent's figures file — has no corpus here
to resolve against, and §6.2's relation 1 discharges it as a qualified cross-package reference rather
than reporting it dead.

**A corpus that yields zero ids is one of two states, and only one of them is a failure.** A corpus
file holding **record-shaped content** — at least one block the format would recognise as a record,
an `id:`-bearing block in a grounding file, an entry or row in an inventory or defect log, a record
in `decisions.md` — and yielding zero ids of its class stops the run with
`BRD_PACKAGE_CORPUS_UNREADABLE`, naming the file and the partition, because a scan that cannot read
a block has learned nothing about whether the ids it names exist. A corpus file holding **no**
record-shaped content is an **empty corpus**: a real and ordinary state, and it passes.
`commands/prd-ground.md`'s *Write findings* phase writes `grounding/design-grounding.md` as every
`[DG#n]` **or a short note when design grounding was skipped and why**, a defect walk that confirmed
nothing leaves `brd/brd-defect-log.md` with a header and no entries, and `commands/brd-interview.md`
writes `decisions.md` as its header line alone where no round recorded a decision
(`references/decision-register-format.md` §1) — all three present, all three non-empty, all three
correctly holding no ids, and all three routine. Stopping on any of them would be a check
firing on correct content.

**A `[CDF#n]` corpus that is absent altogether is the third ordinary state, and it is not the
unreadable one.** `commands/brd-interview.md` writes `code-defect-log.md` only where a round raised
an entry or re-dispositioned one already on file, so a package whose decisions turn on no code
defect ships no log at all — and §1.1's row for it is conditional for that reason. An absent corpus
file is not a corpus holding record-shaped content that parsed to zero, so it never reaches
`BRD_PACKAGE_CORPUS_UNREADABLE`; a `defects` field naming a `[CDF#n]` with no log in the bundle
fails relation 1 as an ordinary dead citation, which is the correct outcome and needs no stop of
its own.

**The distinction is drawn on record-shaped content because of what the failure actually is.** What
`workflows-core:grounding-format` §2.1 warns about is a **reader** that cannot see records that are
there — the padded-colon scan, blind to blocks on the page — so record-shaped content is the
evidence that there was something to see. Where there is none, the zero and the file agree and
nothing has gone wrong. A reference *into* an empty corpus then fails relation 1 as an ordinary dead
citation, which is the correct outcome and needs no stop of its own.

**The partition depends on rule 1 holding.** The boundary is the `<BRD-KEY>` in each document's
filename, so it survives flattening, renaming and re-archiving — but a bundle document that reached
the bundle without its key-carrying name has no partition, and relation 1 cannot place it. That is a
rule-1 violation before it is a §6 problem, so §6 reports it rather than guessing a partition: an
unkeyed bundle document stops the run with `BRD_PACKAGE_DEAD_CITATION`, naming the document, because
every id inside it is unresolvable by construction.

### 6.2 The three relations

**Relation 1 — every identifier reference resolves inside its own partition's corpus for that
class, unless it carries another BRD's key at the point of use.** The qualified **prose** form is
`<BRD-KEY> [CG#7]` — the key immediately before the bracketed id — and it is **one spelling only**:
`workflows-core:grounding-format` §2.1's whole argument is that a writer free to choose between two
renderings produces an artifact whose readers are wrong in a way that looks like data, and a
qualified citation written into a sentence is exactly such a rendering choice. This also repairs a
live ambiguity the check merely surfaces: today a reviewer reading a copied prerequisite's grounding
file meets `[CG#7]` with nothing telling them whose numbering it is.

**An identifier reference carries a number.** A placeholder — `[BR#n]`, a bracketed prefix with `n`
where the number would stand — names a class and no record, so relation 1 has nothing in it to
resolve. That is the only form an example takes in text the run copies in verbatim — the schema body
the prompt's part 10 inlines (`references/customer-review-schema.md` §1) and every fixed sentence
`commands/brd-package.md` renders, which its *Render the customer prompt* phase binds to that form —
so that text needs no exemption here. An example written with a number is not an example to this
relation: it resolves against the package's own records, to a record nobody meant or to nothing, and
no operator edit can repair text the run renders from a reference on every run.

**A structured field is already qualified, and relation 1 reads it rather than refusing it.** Where
an identifier reaches the bundle inside a **structured field whose format another authority fixes**,
and that authority defines the field to name a record of another BRD, relation 1 treats it as a
**qualified cross-package reference** and discharges it: it is never resolved against this
partition's corpus, and never a dead citation — save where the key it carries is its own
partition's, which is resolved (below). That is the rule, and the fields below follow from it
rather than the other way round. Two things make it the only honest reading. The operator could not
repair such a value without violating the authority that owns the field; and the BRD it names may
not be in the bundle at all — `commands/brd-package.md` Phase 2's *BRD not found* and *no package on
file; nothing to copy in* branches both carry a prerequisite key with nothing copied in — so no
partition could ever hold that id, and a rule demanding resolution rather than qualification would
make such a package permanently unpackageable, the deadlock §6.3's exemptions exist to avoid. §6.1's
vacuity guard reads the same Phase 2 carry and passes over the same prerequisites, for the same
reason.

**Which fields those are is derived from the authorities that own them, never maintained as a list
here** — the discipline relation 3 already follows for §1.1's table, and for the identical reason: a
field an authority declares and a copy here misses would be invisible to exactly the check that
exists to catch it. **A new such field is that authority's to declare**, and reaches relation 1 the
moment it does. Those that exist today:

| Field | Authority | What that authority defines it to name |
|---|---|---|
| `conditional_on: <BRD-KEY>/<decision-id>` | `references/decision-register-format.md` §5 | one specific decision in a named prerequisite's own register |
| `blocked_on: <BRD-KEY>/<decision-id>` | `references/code-defect-log-format.md` §5 | one specific decision in a named prerequisite's own register — the decision that would settle a `conditional` `[CDF#n]`'s scope question. Its other spelling is prose naming no bracketed identifier, which no relation ever meets |
| `prerequisite` | `workflows-core:grounding-format` §2, §5 | the prerequisite BRD's decision a `will-change` finding's horizon turns on |
| `rejected: <SLICE-KEY>/[CD#n]` | `references/coverage-ledger-format.md` §3 | the customer decision that withdrew a requirement, in the named slice's own register. `/brd-reconcile` writes it only onto its own slice's ledger, so in that slice's bundle the key is its own partition's and relation 1 resolves it there (below), as it does `resolved-by: <this slice>/[CD#n]`; the key is carried because the row is also read from other folders (that reference's §6.1 hop, a sibling's interview) |
| `customer-amended <SLICE-KEY> <date>` | `references/brd-format.md` §4 | the named slice's returned review of that date, which holds the amended text — qualified as `resolved-by` is, because the log is the parent's and each slice keeps its own reviews. It carries no bracketed identifier, so relation 1 has nothing in it to resolve, and names no bundle document, so relation 3 has nothing either; it is listed so a reader of the parent's log shipped into a slice's bundle knows the key may be a sibling's. A bare `customer-amended <date>`, the spelling before 3.7.0, names no slice and is read as it stands |
| `resolved-by: <SLICE-KEY>/[CG#n]`, `resolved-by: <SLICE-KEY>/[CD#n]` | `references/brd-format.md` §4 | the grounding finding or the customer decision that settled a defect, in the named slice's own grounding file or register — grounding and deciding are both slice-only, and the log is the parent's, so the value carries that slice's key, in the one spelling `references/brd-format.md` §4 fixes. Relation 1 resolves it in the named slice's own bundle (below) and discharges it in any other. A bare value names no slice — a `resolved-by: [CG#n]` in the spelling the defect log's format gave it before 3.7.0, or either form written by hand, since no release ever wrote a bare `resolved-by: [CD#n]` — and is reported as an unqualified `prerequisite` is (below) until its slice key is added |
| the `[BR#n]` a defect entry is raised against, and a `conflict` / `duplicate` entry's counterpart `[BR#n]` | `references/brd-format.md` §3 | a requirement in the log-owning BRD's inventory — the parent's on a slice |
| `superseded-by: [BR#n]`, and an orphan row's own `id: [BR#n]` | `references/coverage-ledger-format.md` §2, §3 | a requirement of the parent's, one this slice "need not claim or hold a row for" |
| the *Rows* line of `brd/brd-figures.md` — every `[BR#n]` the line names | `references/brd-format.md` §1.2 | a requirement in the figures file's owning BRD's inventory — the parent's on a slice |

**The last four are routine rather than exotic**, which is why refusing them would stop the
ordinary package rather than a rare one. §1.1 ships the **parent's** defect log and figures file
whole into a slice's bundle, and a parent that split into several slices carries defects — each
resolved by whichever slice settled it, and requirements superseding one another, and images
yielding or illustrating requirements — across all of them, while the slice's own inventory is
defined over `claims:`
(`references/brd-format.md` §2.1) and its `covered-by` rows are exactly its orphan rows
(`references/coverage-ledger-format.md` §3). Every one of those references is correct content whose
target sits one hop up, outside this partition's corpus by §1.1's own allow-list.

**`prerequisite` is reported, never silently resolved.** Alone among the fields above it fixes no
spelling: `workflows-core:grounding-format` §5 requires a `will-change` finding to name the
prerequisite's decision and does not say how, so a bare `[VD#n]` there is indistinguishable from one
of this package's own. Resolving it would land on a different record and go **green** — a citation
resolving to the wrong thing, which is the failure §6 exists for, and worse than a stop because
nothing surfaces. So an **unqualified** `prerequisite` value is reported, exactly as relation 2
reports a claim naming more than one requirement id, and never resolved into this partition's
corpus; a silent pick is a guess there too. A value that does carry the prerequisite's key is
discharged like any other field above.

**A qualifier naming the reference's own partition is not cross-package, and is resolved.** Where
the key a reference carries — in a field or in the prose form — is the key of the partition it sits
in, which for this package's own documents is the packaged BRD's key, relation 1 resolves the id in
that partition's corpus exactly as it resolves an unqualified one, and a miss is a dead citation:
`resolved-by: EPIC-008-01/[CD#2]` in slice `EPIC-008-01`'s own bundle resolves against the
`decisions.md` that bundle carries. **Only a qualifier naming another BRD is discharged.**
Discharging the own key too would pass a `resolved-by` naming a decision that does not exist in the
one bundle holding the register that could catch it.

**The two are different things, and the one-spelling discipline is untouched.** A structured field
is another authority's to format and §6's only to read: a check reads what the tree writes, not what
it would have preferred it wrote. `<BRD-KEY> [CG#7]` is the **prose** form §6 itself introduces, for
a reference sitting in a sentence rather than in a field, and there one spelling stands — that is
where a writer would otherwise be free to choose, which is the freedom §2.1's argument is about.

**Relation 2 — for every `[DG#n]` whose `class` is 4, its `cites` resolves within the same
partition, and the cited `[CG#n]`'s `claim` names the same requirement id as the citing finding's
`claim`.** The rule itself belongs to `workflows-core:grounding-format` §6.3, which requires the
citation and requires it correct; §6 is its first enforcer. **The test is that the claim names the
id, not that it opens with it:** §2.1's own canonical example does open with the id —
`claim: [BR#7] — the nightly export runs at 02:00 UTC` — but that same section sanctions a
hand-edited artifact everywhere else on this route, so a claim reading "the nightly export, per
`[BR#7]`, runs at 02:00" is correct content that a position test would refuse. **Where a claim names
more than one requirement id, §6 reports the ambiguity rather than picking one** — a silent pick is
a guess.

**Relation 3 — a bare `<name>.md` token, carrying no path separator, must name a document that is in
the bundle, and only when it is one of two shapes.** Either it carries the `<BRD-KEY>-` prefix that
`commands/brd-package.md`'s *Assemble the bundle* rule 1 gives every bundle document, or it exactly
matches the **working** filename of a document §1.1 admits or excludes by name — **derived from
§1.1's own table each time this relation runs, never copied into a second list here**, because a
document added to §1.1 without a matching entry here would be invisible to exactly the check that
exists to catch it. **A working filename carrying a placeholder is resolved before it is matched,
never compared as literal text** — `<YYYYMMDD>` against the run's own date,
`brd/source/<basename>` against the basename of the customer's own document as copied in, and the
captured-markdown row's `<file>.md` against the basename of each markdown file it copied in — one
rule covering all three, because resolving one and not another drops whichever it missed out of
shape 2, and the customer's own files are the ones §1.1 admits under a placeholder. The scoping is
what keeps the relation off correct content: a grounding finding's `evidence` field is a repository
`file:line` list, and a repository that documents itself in markdown puts a bare `docs/api.md:12`
into a finding that is entirely correct — an unscoped rule would refuse the whole bundle over it.

**The scope is the documents this package wrote, and stating it that way is the shortest true form
of the three exemptions below.** A captured file's own text is outside the relation — §2.1 puts
those files outside every rewrite for the same reason, their links are the customer's and the
manifest is where anything they name that the bundle lacks is disposed of — and so is the manifest's
own quotation of a target as written. An implementation that scopes correctly cannot produce the
false positive the three guard against; one that implements the three reaches the same answer.
They are kept rather than collapsed because each also states *why* its content is correct, which a
scope rule does not, and a reader who drops one has to be told what it was protecting.

**Three kinds of token are outside the relation whatever their shape, and each is correct content it
would otherwise refuse.** A `<file>:<line>` locator in a grounding finding's `evidence` names a
repository file, never a bundle document, so the relation stays off it — and shape 2's
captured-markdown row in particular reaches only references outside grounding evidence: a customer
who happened to capture a `README.md` of their own would otherwise turn a correct `README.md:12`
into a dead citation. The manifest's quotation of a target as written (§1.1, §2.1) is a map entry
rather than a reference: it sits beside the bundled filename it maps to and quotes the customer's
own link, so the target `notes.md` of a `[[notes.md]]` link, quoted there, is already resolved by
that line, and testing it would make that package unbuildable with nothing the operator could
change. The third, for that same reason, is a captured file's own link to another captured file —
§6.3's to state, with the rest of the customer-derived locators.

Relations 1 and 3 fail the same way — a reference that resolves to nothing — and stop the run with
`BRD_PACKAGE_DEAD_CITATION`, naming the id or filename, the document it sits in, and the corpus or
bundle it failed to resolve against; the remedy is to fix or qualify the reference. Relation 2 fails
differently — the reference resolves, to a finding about a different requirement — and stops with
`BRD_PACKAGE_CITATION_MISMATCH`, naming both `claim`s; the remedy is to re-derive the finding, and
the reference itself may be untouched. The two stay separate codes because the two remedies repair
different things.

### 6.3 Exemptions

**`[SR#n]` is exempt entirely.** `self-review-<YYYYMMDD>.md` is excluded from the bundle by §1.1's
one exclusion that is a *rule* rather than a consequence of the allow-list, while the `[SR#n]`
content the customer may see reaches them **filtered** — through the prompt's parts 7 and 9, cited
by id, never the file itself. So an `[SR#n]` reference is correct content that resolves to nothing
in the bundle, **by design**, and a check without this exemption fires on every package. The
distinction a reader needs: naming the self-review *file* is dead — relation 3 catches it — while
naming an `[SR#n]` id is the filter working as intended, and relation 1 must not catch it.

**Verbatim customer content reports rather than stopping the run on its own.** That is every span
in the bundle holding the customer's own words, copied or transcribed rather than written by this
package:

- `brd/source/<basename>` and every other captured markdown file, whole — copied byte for byte and
  immutable by rule (§2.1, `references/brd-format.md` §1, §1.1);
- in `brd/brd-figures.md`, each section's *Text*, the *Says* column of its *Annotations* and its
  *Flow*, which are the image's own words transcribed verbatim (`references/brd-format.md` §1.2);
- in `brd/brd-inventory.md`, a prose row's `text` whole — the requirement verbatim, or, for a row a
  split produced, both its parts, the ` … ` between them being the plugin's — but an image-drawn
  row's `text` only in the element it quotes, the rest of that text being the plugin's words
  (`references/brd-format.md` §2);
- in `coverage-ledger.md`, a row's `text`, treated exactly as the inventory's — a prose row's
  whole, an image-drawn row's only in the element it quotes — because each ledger row's `text`
  mirrors its inventory row's (`references/coverage-ledger-format.md` §2);
- and in `decisions.md`, a `[CD#n]`'s `argumentation`, the customer's own reason quoted and never
  paraphrased (`commands/brd-reconcile.md`, *Freeze the customer decisions*) — the customer's quoted
  words only, never a `Reopened`, `Reverted`, `Withdrawn` or `Superseded` paragraph among them, which is the
  plugin's (`references/decision-register-format.md` §4) — and its `chosen` where that quotes an
  answer outside the options put — the answer only, not the fixed marker before it
  (`references/decision-register-format.md` §1).

Each table span is read **decoded** (`references/brd-format.md` §2.3): a `\|` or a `<br>` in the
file is the table's encoding, not the customer's words, so a token is sought, and a span's extent
judged, in the text the customer wrote.

A `[BR#n]` or a filename visible in the customer's screenshot is the customer's, not a citation this
package made, and so is one the customer wrote into an answer or a reason the register quotes. Those
spans inherit the plugin-free scan's treatment of the same content, for the identical reason:
stopping outright would make that BRD permanently unpackageable, since the only repair left would
falsify the record — an edit to an immutable file, a transcription saying something the image does
not, or a quotation saying something the customer did not. So a relation 1 or relation 3 hit inside
one is reported, grouped as rule 4 below fixes, and put to the operator on the one question *The
operator's ruling* below fixes. Outside these spans and the customer-derived locators below, every
hit stays a hard stop, in the figures file, the inventory, the ledger and the register as anywhere
else: the rest of each is the plugin's own writing.

**A customer-derived locator is the customer's naming, wherever it appears.** It is one of four
things: a captured file's path relative to `brd/`, with whatever follows its ` › ` — the `source/`
or `source-external/` prefix is ours, and everything below it is the customer's layout and names
(`references/brd-format.md` §1.1), as is the heading path or line range after the ` › `; a captured
file's bundled filename, where it carries the customer's basename after the `<BRD-KEY>-` prefix
`commands/brd-package.md`'s *Assemble the bundle* rule 1 gives it; a link target as written, in a
captured file or in the manifest's map; and an inventory row's `source_anchor`, or the anchor an
inventory or ledger row's `text` carries, whose document form names no path. The naming is the
customer's whoever wrote the line it sits in, so a locator counts in text this package wrote exactly
as in a customer's file — a figures section's heading and its *Linked from* line, a manifest line,
an inventory or ledger row, an interview question, the note that stands in for the figures file's
frontmatter (§1.1), and the prompt parts rendered from them. **It is recognised by where it sits or
by what it names, never by its shape.** In a fixed field — a `source_anchor` (the inventory's
column, or the anchor an inventory or ledger row's `text` carries, `references/brd-format.md` §2,
`references/coverage-ledger-format.md` §2), a figures section heading, a *Linked from* line, a
manifest map line — it counts as written. Anywhere else in this package's writing only two things
count: a path carrying its prefix and naming a file the capture holds, with whatever follows its
` › `, and a filename that is the bundled name of a captured file. **Nothing else in this package's
own prose is a locator.** A pathless heading or section number there — `see §3.4 of brd-format`,
`(see §3.4)` — is none, so its `§` is a hit like any other `§` the plugin writes, whatever sections
the customer's document happens to have; and a bare `<name>.md` is no path in that form and stays
relation 3's (§6.2). Four rules follow, for the plugin-free scan and this check alike:

1. **A leading section reference is no hit in a locator's fixed position, and only there** — the
   `§` and section number that open a `source_anchor`, or that open what follows the ` › ` after a
   prefixed captured path, in a fixed field or wherever that path appears. Those are the positions
   `references/brd-format.md` §2.2 fixes for it, and the reader resolves it by opening the
   customer's file the anchor or the path points into, which the bundle carries: nothing in it
   assumes a reader who has this plugin. Every anchor that section was measured on opens with one,
   so reported they would put a grouped count of expected `§`s in every package's report, and that
   count would absorb, and so hide, a real one.
2. **Any other hit inside a locator is reported, never a stop on its own** — a `references/`
   folder in a captured path, a quoted `"D3"`, a `§` inside heading text, a filename or a link
   target. It is the customer's naming, and the only repair would rename their files, retitle their
   headings or re-point an anchor away from where the requirement is stated, each of which
   falsifies the record.
3. **A bare `<name>.md` link inside a captured file is outside relation 3** where it resolves — as
   written, or through the link log's *Captured links that do not resolve as written* table (§2.1)
   — to a captured file the manifest maps. The manifest already resolves it, which is the reason
   §6.2 keeps the relation off the manifest's own quotation of a link.
4. **Every report this section makes is grouped** — one line per file and token, with a count — in
   the report that asks the operator to rule and in the run's final report alike, whether the hit
   sat in verbatim content or in a locator. A `"D3"` quoted in an image anchor, in that row's
   `text`, in its ledger row's `text` and in the figures file's *Flow* is three lines, not four
   reports.

**The operator's ruling — one question per pass, never one per hit.** A pass that reports a hit this
section covers — the plugin-free scan over the prompt, over the delivery note or over the finished
bundle (`commands/brd-package.md`'s *Render the customer prompt*, *Render the delivery note* and
*Assemble the bundle* rule 7), or this check (that phase's rule 8) — prints its grouped report
(rule 4) and then asks once, over the whole of it:

```
choices: ["Ship it — these are the customer's own words and naming, left exactly as they wrote them (Recommended)", "Hold the package — hand nothing off until the customer has seen these"]
```

The recommendation stands because every hit reported here is, by the definitions above, a token the
customer wrote, and its only repair would falsify the record. *Ship it* continues the run. *Hold the
package* stops it:

`BRD_PACKAGE_CUSTOMER_CONTENT_HELD: you held <BRD-KEY>'s package over <n> hit(s) inside the customer's own words or naming — nothing was handed off. What the report names is the customer's and is never edited here: take it up with the customer, then re-run. Where this run already wrote bundle-<YYYYMMDD>/, it was never sent — move it aside first, or the re-run stops with BRD_PACKAGE_BUNDLE_EXISTS.`

A free-text answer is read onto one of the two, or the question is asked again; it never becomes a
third outcome. **A hit an earlier ruling in this run already covered is listed under that ruling and
not asked about again**, and a hit is keyed by its token and **the file it sits in** — one grouped
line of rule 4, never the artifact its text was interpolated from. The bundle's copy of the prompt
counts as the prompt for this: those of its hits **whose token the ruling taken over the prompt
(*Render the customer prompt*) covered** are not put a second time when the bundle pass meets the
prompt among the bundle's documents under its bundled filename, and one carrying a token that
ruling did not cover is put like any other. A hit in any other bundle document is that document's,
even where the same token reached the prompt from it. A pass that reports nothing asks nothing. The
run's final report records the rulings as one outcome line, above the grouped lines:

`Customer content: <n> hit(s) in <m> file(s) — shipped as the customer's own, on the operator's ruling`

or, where no pass reported a hit, `Customer content: none`.

### 6.4 What §6 cannot see

Stated because a green check here is otherwise read as a clean bundle:

- **A reference that *describes* a bundle document where rule 1 requires it to *name* one.** No
  pattern separates a deliberate description from a missing filename.
- **A citation that resolves to the right id and is wrong in a way relation 2 does not test** — a
  `[CG#n]` about the right requirement but the wrong claim within it.
- **A corpus every one of whose records is malformed the same way.** §6.1 separates an unreadable
  corpus from an empty one on **record-shaped content**, so a file in which nothing at all is
  recognisable as a record reads as empty and passes — reproducing, in the one case that test cannot
  see, the *report every reference in the bundle as dead* outcome `BRD_PACKAGE_CORPUS_UNREADABLE`
  was written to prevent. It is acceptable rather than merely tolerated: the run still stops,
  because every reference into that corpus then fails relation 1 as an ordinary dead citation, so
  nothing ships wrong. What is lost is the diagnosis — the operator is pointed at the references
  rather than at the corpus. A test tighter than the parse it adjudicates would be undecidable by an
  agent whose parser has just failed, which is why the looser one is the right trade and this limit
  is stated rather than closed.
- **An identifier class shipping without a row in §6.1's table.** The table is a closed list, so a
  future class is invisible to relation 1 until it has a row. The reverse case — a row whose corpus
  file is **absent** from the bundle — is not a corpus-unreadable: that stop is defined on a file
  that is there and holds record-shaped content (§6.1), so asserting it about a file that is not in
  the bundle would tell the operator something false about their own tree. An absent corpus is an
  empty one for every purpose §6 has, and a reference into it fails relation 1 as an ordinary dead
  citation.
- **The delivery note.** Its whole job is to name a bundle file exactly — *which file is the prompt*
  and *which file comes back* (§4) — and it is deliberately **not** a bundle document (§4, §1.1), so
  the check, which runs over every document in the finished bundle, never sees it. A wrong filename
  there stops the reviewer before they open anything, which is the failure this whole route is built
  around. Widening the check to reach it is a scope decision rather than a wording one — the note
  names files, and the bundle's own filename set exists by the time the check runs — so it is named
  here rather than assumed covered.

## 7. Set resolution

**`set-resolution`** is a check over the assembled bundle that §6 does not make, and the distinction
is the point: §6 asks whether a reference *resolves*, this one asks whether a **restatement of a set**
is faithful to the set it restates. The manifest, the delivery note and several prompt parts each
restate, in their own words, a set held somewhere else — the documents in the bundle, the
repositories and their pins, the open assumptions. A restatement is a copy, and a copy drifts after
the first correction.

**A count comparison is not the check.** Two sets of the same size with different members pass a
count test and fail the reader — a substitution, which is worse than a miscount because it reads as
correct. Every relation below compares **membership**.

**Every relation here was measured against assembled bundles before it was written, and each one is
narrower than the obvious version because the obvious version fired on correct packages.** That is
recorded per relation rather than as a general caution, because the specific narrowings are the
content: a reader who widens one back is not being bolder, they are reintroducing a false positive
somebody already paid for.

### 7.1 The relations

**Relation 1 — a part that enumerates a set of identified records names exactly that set.** Its scope
is the prompt parts whose source is a set of records carrying identifiers, which render them as an
enumeration, **and whose source is itself in the bundle**: the open assumptions, the conditional
positions and conditional defect entries, and the out-of-scope defect entries. **For each part in that
scope**, the identifiers it names are exactly those its own stated filter selects from its source
file, both directions — an identifier in the part and not in the filtered source is an invention, one
in the filtered source and not in the part is an omission, and the omission is the dangerous half
because a customer cannot see what they were not shown. **The paragraphs below narrow that scope
and never extend it**, which is worth saying because they once sat between this sentence and the
scope it governs, and a reader taking them in order bound the rule to the set they exclude.

**Resolve the filter against the records' own fields, never against prose that uses the same
words** — this family's "resolve against a known set, never parse one out of free text" rule, met at
the one place the free text is a part a run rendered itself. A part states its filter in a sentence,
and a sentence is a description of a property the records carry, not the selection itself: read the
property off each record and select on it. The failure this forecloses was measured on an assembled
package, where a part named four decisions as conditional on another engagement's review and a
text-derived reading returned six — the two extra carried an explicit *no dependency* marker in the
very field the filter is about, so the part was right and the looser resolution would have reported
its two most carefully-handled records as omissions, which relation 1 calls the dangerous half.
Where a part's filter names a property no record field carries, that part is **outside** this
relation for the same reason the prose parts are: there is no set to select.

**Expand a range before comparing.** A part legitimately writes `[AS#1]`–`[AS#4]` for four records
rather than naming each, and on measured packages that was the *only* rendering in most of them — so
a comparison over literal tokens sees two ids where the part names four and reports two omissions
against a correct package. A range between two ids of one prefix denotes every id between them
inclusive.

**The accepted-risk findings are deliberately outside this relation, though the part that surfaces
them is not.** Their source is the adversarial self-review, which §1.1 excludes from the bundle by
rule — so inside an assembled package there is nothing to compare that part against, and a relation
that reached for it would resolve to an absent file on every correct bundle. What reaches the customer
about those findings is prose the packaging run wrote, and prose is review's.

**It does not reach every part, and the exclusions are measured rather than cautious.** The review
scope part renders what the package answers for as **prose in the customer's own vocabulary** — the
scope areas a customer recognises, not the requirement ids behind them — so a relation demanding
identifiers there fires on a correct package. The requirements it names as another BRD's do carry
ids, each `<PARENT-KEY> [BR#n]` (`commands/brd-package.md`'s part 6), and that list is outside this
relation too (§7.2). The decisions part is mostly the interview's own questions, which carry **no
minted identifier at all**, so only the assumption and escalated-finding fractions of it are
testable and the part as a whole is not. A part built from prose has no set to compare.

**Relation 2 — the manifest and the bundle name the same review documents.** Every markdown review
document in the assembled bundle carries a manifest line, and every manifest line names a document in
the bundle. Three qualifications, each of which a real package would otherwise fail:

- **Match the basename, tolerating the extension either way.** A manifest legitimately writes
  `` `<Document Name>` `` or `` `<Document Name>.md` ``; both conventions occur, sometimes across two
  builds of the same package, and a matcher fixed on one reports every document in the other as
  missing.
- **The manifest does not list itself**, and neither does a file that is not a review document at
  all — a marker written into a superseded bundle to say it was never sent is the case that occurs.
  The test is *review document*, not *markdown file*.
- **Images are out of scope.** The manifest names frames in prose where it names them, and does not
  always name them; requiring it to would fire on a correct package. A design finding's citation of
  a frame by filename is not checked here, and not by §6 either, whose relation 3 reads a bare
  `<name>.md` token only: it is review's. A captured image is a different case — §1.1's map names
  every one the bundle carries — and this relation still does not test it.

**Relation 3 — the delivery note's repositories and pins are the bundle's own baselines'.** The note
restates which repositories, at which commits; the bundle's baselines document is where those were
recorded. Same repositories, and **each commit the note names is a prefix of a baseline commit, with every
baseline it prefixes being the same commit** — the note abbreviates, as a note written for a person
does, so an equality test finds nothing and reports every correct note as carrying no pin at all.
**"Exactly one" is the wrong cardinality and fires on correct content**: a baselines document records
one entry per repository *per run*, so a package pinned across two dated runs at unmoved commits
holds the same SHA twice and a prefix legitimately matches both. What makes an abbreviation
ambiguous is matching two *different* commits, which is the case to report. This is the one relation that
reaches the note, which is deliberately not a bundle document (§4) and which §6 therefore never sees:
a pin restated wrongly there has the reviewer verify every code claim against a snapshot nobody
ground.

**A relation whose source side comes up empty while the restatement is not fails rather than
passes.** `workflows-core:grounding-format` §2.1 states the general form — a relation fails when
**either** side comes up empty — and this is a deliberate narrowing of it rather than a citation of
it, itemised here because a narrowed rule is a deletion
(`workflows-core:instruction-file-maintenance`). What §2.1 governs is a resolution over records,
where an empty side means a read failed. Here one side is a **restatement**, and a part that
legitimately has nothing says so: both sides empty is the ordinary pass, and reading it as a failure
would refuse every package with no conditional position or no out-of-scope defect. What stays
failing is the asymmetric case — a restatement carrying members over a source that yielded none —
because that is a read failure wearing the shape of a discrepancy.

### 7.2 What §7 cannot see

- **A part whose source is prose**, which relation 1's own scope already concedes: the review scope,
  and the question half of the decisions part. Those are review's.
- **The review scope part's list of requirements another BRD holds.** It names identified records,
  each qualified with the parent's key, from a ledger the bundle carries, but relation 1's scope is
  the closed list §7.1 opens with and does not name it, so a row left off that list, or named there
  that the ledger does not put out of scope, is review's to catch — as is a wrong id there, since
  §6's relation 1 discharges a qualified one rather than resolving it.
- **A faithful restatement of a wrong source.** Where the ledger, the register or the findings are
  themselves wrong, every relation here goes green. This check is about the copy; the original is
  what verification and the interview settle.
- **Prose beside a correct enumeration.** A part may name every right identifier and describe them
  wrongly in the sentence above; membership is blind to that, and the adversarial self-review reads
  for it.

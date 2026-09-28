# /idea

Refines one raw source — a prompt, a file, a community post, or a saved file — into a lean `idea.md` brief that seeds [`/create-prd`](create-prd.md).

## Who runs it

`/idea` runs in the [pm](../roles-and-phases.md#pm--product-management) role, cost-attribution phase [prd-creation](../roles-and-phases.md#prd-creation) — the same phase [`/create-prd`](create-prd.md) emits, since at this point in the pipeline no specification or design exists yet for the item being refined.

## Synopsis

```
/idea <PRD-KEY> [<prompt> | @<file>] [--deep] [--ground-code [<repo>,…]] [--no-docs] [--docs <path>]
```

The argument after the key is classified into one of **two** source forms (Phase 1), by precedence:

- **An existing `.md` path** — a note, a saved community post the operator downloaded (typically under `Projects/Products/…`), a Product Requirements Document handed over as prior art, or a previously-written `idea.md` handed back for re-refinement. Its links are **walked in full** — asking you first where the walk goes past two levels of pages, twelve pages or six images — and the images it links are **transcribed** — see [What it reads](#what-it-reads). What kind of markdown it is, the reader works out from the file itself: a community post is read for its demand signals (upvotes, duplicate reports, the shape of the complaint), and a document carrying `kind: prd` becomes the brief's `## Prior art`. Nothing fetches a URL.
- **Anything else — an inline prompt.** The argument text itself becomes the raw idea.

There is no third classification and no tracker-export source form; a path that looks like one but resolves to no file is caught and put back to you rather than ingested as prose.

Four flags: `--deep` switches the grill from bounded (≤10 questions) to relentless (runs to convergence, no cap); `--ground-code` adds an optional code-grounding pass; `--no-docs` turns documentation grounding off; `--docs <path>` points documentation grounding at a specific docs root instead of the resolved default.

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve the address + model routing"] --> p1["Phase 1 — Classify the source"]
    p1 --> p15["Phase 1.5 — Walk the source's links"]
    p15 --> p2["Phase 2 — Ingest the source (idea-reader)"]
    p2 --> p25["Phase 2.5 — Grounding: documentation (optional)"]
    p25 --> p26["Phase 2.6 — Code grounding (optional)"]
    p26 --> p3["Phase 3 — Refine via grill"]
    p3 --> p4["Phase 4 — Write idea.md"]
    p4 --> p45["Phase 4.5 — Vendor the sources into the PRD folder"]
    p45 --> p5["Phase 5 — Handoff: adaptive next-phase offer"]
    p5 --> p6["Phase 6 — Session maintenance, feedback & cost"]
```

Five subagents are dispatched along this path: `figure-reader` (Phase 2, transcribes the linked images the walk took, in parallel batches — only when it took one), `idea-reader` (Phase 2, ingests the source), `workflows-core:docs-grounder` (Phase 2.5, read-only grounding on the shipped product docs — default ON when `$DOCS_PATH` resolves, advisory, never a gate), `workflows-core:code-scanner` (Phase 2.6, one instance per confirmed repo, only when `--ground-code` is given), and `workflows-core:impl-maintenance` (Phase 6, session lessons-learned). `figure-reader` is frontmatter-pinned to Opus; the other four run at the caller's `detection_model` — the §2.1 Sonnet chain — never on a fixed pin; the interactive grill and the authoring itself run inline on the session's own `current_model` rather than through a delegated subagent.

## What it reads

When the source is a markdown file, the run does not stop at that one file.

- **Every link, walked first.** Phase 1.5 walks every link the source makes, and the links on every page it reaches — the `[[wikilink]]` (resolved by name across the vault where it is not next to the note, and reported as ambiguous rather than guessed where two notes share the name), the ordinary inline link or image, a reference-style `[label]: target` definition, and an HTML `<img src="target">`. The walk reads nothing but links, and a cycle — A links B, B links back to A — is a silent skip.
- **You decide past the old bounds.** Where the walk stays within two levels of pages, twelve pages (your note among them) and six images, everything is read and nothing is asked. Where it reaches past any of those, the run names what lies beyond and asks: read all of it, only what the source links directly, or stop. Nothing is capped behind your back.
- **Linked images, transcribed — not just listed.** Every taken image goes to `figure-reader`, in parallel batches, which transcribes its labels and annotations without seeing your source, so the grill knows what a linked mockup actually shows.
- **Nothing here is fatal.** A broken link in a page that was read, a missing image, a file that will not open — each is noted and the run carries on, exactly as a broken link always has.

**What a read image counts as: context, not evidence.** It informs the questions the grill asks and the prose the brief ends up with. It is not a design-grounding finding and gets no verifier pass — though the images it vendors *are* written into a frame set, which does carry an index (see [What it vendors](#what-it-vendors)); the index makes the set readable, not grounded — a frame is what somebody drew, not what the product does, so nothing seen in one is written into `idea.md` as fact unless you confirm it during the grill. Design grounding proper (`[DG#n]` findings over an exported frame set) belongs to a different route and is not part of `/idea`.

## What it vendors

The specs repo is the system of record, so a brief whose links point at the folder the source happened
to live in is a record only its author can follow. After `idea.md` is written, the run **copies the
sources it actually read into the same PRD folder and rewrites `idea.md`'s links onto the copies**.

- **Markdown → `attachments/`.** The source file itself, and every page the walk took.
  `attachments/` is the folder's reserved name for vendored text; what reaches it today is markdown,
  because markdown pages and images are the only linked files anything reads. `/idea` is its only
  writer: the companion `docs-workflows` plugin's `/document` reads an image already there as a
  screenshot source and leaves it where it is, but puts a new screenshot in the folder's
  `Doc screenshots/` subfolder, never here. A link in `idea.md` to
  the source itself is repointed at its copy, exactly as a link to a page the walk took is.
- **Images → `design/idea-sources/`.** Every image that was transcribed, together with an `index.md`
  saying what each frame shows — written from each transcription's one-sentence description, copied
  verbatim and never invented — and which file linked it, named by that file's copy in the folder
  (`attachments/p3.md`) rather than by where it sat on your disk.
- **One frame set per PRD folder, and its index accumulates.** A second `/idea` run over the same folder
  adds its images to that set and **rebuilds the index from the directory**, keeping every earlier row
  word for word and appending its own — a later run holds no description for a frame an earlier one
  vendored, so a row it cannot reproduce is one it does not touch. The index is rewritten whenever the set
  holds a frame, so a re-run that copies nothing leaves it correct rather than empty. That contract is
  `workflows-core:grounding-format` §6.2's, shared with `/workflows-core:frames`.
- **A frame `/idea` cannot speak for gets a `_no description on record_` row and is reported.** An image
  nobody transcribed carries no description and this command will not invent one.
  `/workflows-core:frames` is what fills those rows: it looks at the frames themselves.
- **Nothing else, ever.** No PDF, no archive, no other binary. A linked file nothing opens — not
  markdown, not an image — keeps its link exactly as written and is named in the final report, with its
  extension, so a `.txt` is reported as a file nothing read rather than as a file of the wrong kind.
- **Only what was read.** A page or image you chose not to read, a broken or ambiguous link in a
  page that was read, an image that would not open — none of them is copied, each of them is
  reported, and none of them is fatal.
- **Names never collide silently.** A second file with the same basename becomes `notes_01.md`, a
  third `notes_02.md`, and a suffix is never appended to a suffix. A copy whose content is already
  there byte-for-byte is reused rather than duplicated, so a re-run does not grow the folder. Edit one
  of the sources and re-run, and its copy is **refreshed in place** rather than versioned beside
  itself — a vendored file mirrors its source, and git already holds what it said before.
- **A repointed link comes out as standard markdown, never a wikilink.** The specs repo is browsed on a
  forge and in editors, where `[[wikilink]]` is literal text that resolves to nothing — so a link
  repointed into the repo but left in wikilink syntax still would not open anywhere the record is
  actually read. Display text is kept; a bare image embed takes its alt from the original filename. An
  `![[note]]` embed of a markdown page becomes a plain link rather than an embed — transclusion has no
  standard equivalent and renders nowhere in a git repo, so a link that opens the copy is worth more than
  syntax that does not. A link **nothing copied** keeps its original syntax untouched, on purpose: a
  surviving `[[wikilink]]` is how you see that nothing was copied for it.
- **Links are repointed by the target as written, not by its filename.** Two mockups called
  `toggle-01.png` in different directories become two copies, and the link that named each one goes to
  its own. Where two links are written *identically* and reached different files, neither is rewritten —
  `idea.md` says nothing about which occurrence meant which, and the report names the ambiguity so you can
  point them by hand. A link nobody else can follow is a poor record; a link pointing confidently at the
  wrong frame is a false one.
- **Nothing empty is created.** A run over a bare prompt has nothing to copy and creates neither
  directory.

What a rewrite looks like, in `idea.md`:

```markdown
[[rollout]]                        →  [rollout](attachments/rollout.md)
[[rollout|the plan]]               →  [the plan](attachments/rollout.md)
![[toggle-01.png]]                 →  ![toggle-01](design/idea-sources/toggle-01.png)
![[note]]                          →  [note](attachments/note.md)        (embed → link)
[the survey](/abs/survey.md)       →  [the survey](attachments/survey.md)
![alt](/abs/toggle-01.png)         →  ![alt](design/idea-sources/toggle-01.png)
[[notes#Rollout]]                  →  [notes#Rollout](attachments/notes.md#Rollout)
[[left-out-note]]                  →  [[left-out-note]]                  (not copied — untouched)
```

The copies and the index are handed to the handoff alongside `idea.md`, so they reach the default
branch with it rather than sitting on one machine.

**The index does not mean `/idea` grounds designs.** `design/` is the frame-set directory the
grounding contract reserves, and its index is mandatory there — a frame set without one is refused
outright, so writing the images without it would leave a directory nothing could ever read. Writing an
index makes the frame set readable; it does not make anything read it. No design-grounding finding,
index consultation, or verifier pass happens on **this** run — but the set this phase writes is read
later: [`/prd-ground`](prd-ground.md), run on the same PRD folder whenever an operator chooses to,
grounds it against this same PRD's own `[AC#n]`/`[FR#n]`/`[US#n]` rows. Writing the index is what
makes that later pass possible; it is not that pass itself.

## What it needs

- **A PRD key** — the first positional argument, validated for shape and checked against no tracker — resolved only against the specs tree. It names the folder `idea.md` will live in, which is why it is required up front: there is nowhere keyless to write. Where the key already names a folder, that folder has to be an idea-route PRD folder: a BRD container, a BRD-route slice or an Epic folder stops the run with `IDEA_NOT_AN_IDEA_FOLDER` — after the specs-repo preflight has settled the specs checkout's branch, so a stale plugin branch cannot hide what the folder holds, and before anything else is read — and the stop names the run that does take that folder's work — for a slice or an Epic folder, only a run that can itself take it; for a BRD container, where a PRD belongs rather than a run promised to start. For a slice that is [`/update-prd <KEY>`](update-prd.md) where it already holds a PRD, and otherwise [`/create-prd <KEY>`](create-prd.md) only where the slice's own coverage ledger leaves no claimed row `unallocated` and at least one `covered-here` — where a row is still `unallocated` it names [`/brd-split <KEY>`](brd-split.md) first and `/create-prd <KEY>` only where that walk leaves a claimed row `covered-here`, where the slice claims nothing it names `/brd-split` on the parent — with a slicing instruction, `/brd-split <PARENT-KEY> "<how to cut it>"`, where the parent's own ledger still holds an `unallocated` row (a bare run stops there with `BRD_SPLIT_NEEDS_INSTRUCTION`), bare where it holds none, and in neither form where that ledger cannot be read, where no claimed row is `covered-here` and none `unallocated` it names nothing and says why, and where the slice's coverage ledger is missing or unreadable it names nothing and reports the file. For a BRD container it names each slice under it with `/create-prd <SLICE-KEY>`, or, where it has none, `/brd-split <KEY> "<how to cut it>"` to carve one — a no-op on a ledger with no `unallocated` row, which the stop says. For an Epic folder whose parent holds a PRD it names [`/update-prd <PRD-KEY>`](update-prd.md) for that PRD — `<PRD-KEY>` being that folder's own key, read off its carrier — [`/epics <KEY>`](epics.md) to re-refine the Epic (`/epics <PRD-KEY>` instead where the folder holds no `epic.md`, which `/epics <KEY>` refuses) or [`/specify <KEY>`](specify.md) to specify it; where the parent holds no PRD, it names `/create-prd <PARENT-KEY>` on a `PRD-` parent — on a slice subject to that slice's own ledger, as above — and otherwise no command. A genuinely separate idea takes a key of its own.
- **The idea source itself** — read by `idea-reader`. A path-like argument that names no file is put back to you before anything is read (re-enter it, read it as a prompt, or cancel), and a file `idea-reader` then finds missing or unreadable stops the run and offers to re-enter the source or cancel; both are environment/user halts, not a plugin gap. A key whose folder does not exist yet is not a halt: the folder is created when `idea.md` is first written.
- **`$DOCS_PATH`** (optional, default `/workspace/docs`) — documentation grounding. Missing, unreadable, or carrying no markdown file is a silent, non-blocking skip: `docs grounding: OFF`, never an error. Turned off explicitly with `--no-docs`.
- *(**No** prior-art discovery — the finder that searched a personal store for related work is gone. Prior art now means a Product Requirements Document you hand the command yourself, as a path; nothing goes looking for one.)*
- **`--ground-code` repo(s)** (optional) — only runs when the flag is given. A named repo that is not mounted is neither invented nor silently dropped — it is escalated and, if declined, carried forward by name with its themes left unverified. With no flag at all, the run instead does one cheap detection pass and prints at most one advisory line naming a repo the idea mentions; it never scans.
- **`$SPECS_PATH`** (required) — if unset, the run stops in Phase 0 step 1, before it resolves the key, offering to set it or cancel: resolving the folder and Phase 4's write both need it, and an empty one would put `idea.md` under `/specifications/` at the filesystem root. Past that, `specs-preflight` runs against it at the end of Phase 0 (which can emit a guard notice and set `specs_git: blocked` for the whole run), and from Phase 5 onward the `idea.md` already written there is handed off to git.

## What it produces

`idea.md`, authored against `../../references/idea-format.md`, written into `PRD-<KEY>-<slug>/` under `$SPECS_PATH/specifications/` on the first write and never relocated afterwards. Where no folder exists for the key yet, that first write creates it, `<slug>` being the one `idea-reader` proposes from the source; nothing is created before it, so a run you stop earlier leaves no folder behind. [`/create-prd`](create-prd.md) finds it there.

Beside it, where the source had anything to vendor: `attachments/<name>` for each markdown source
that was read, `design/idea-sources/<name>` for each image that was transcribed, and
`design/idea-sources/index.md` naming what each frame shows. See [What it vendors](#what-it-vendors).

**Nothing relocates it, at any point.** The key is a mandatory argument precisely so the brief lands in its final folder on the first write, and [`/create-prd <KEY>`](create-prd.md) finds `idea.md` at that path afterward and never moves it either — an explicit `@<path>` argument to [`/create-prd`](create-prd.md) is a separate, out-of-contract read that is likewise never relocated.

## Gates

`/idea` has no reviewer agent — its bounded grill is the gate. By default the grill asks at most 10 questions across the ranked ambiguity gaps (problem clarity, target users, desired outcome, scope, evidence sufficiency, success signal, terminology) and then stops; any remaining high-impact gaps become `[NEEDS CLARIFICATION]` markers in `idea.md`, capped at 3, with reasonable defaults recorded as Assumptions instead. `--deep` removes the bound and runs the grill to convergence. A boundary the source states explicitly — *"not for archived projects"*, even in passing — is extracted by `idea-reader` into `stated_scope` and treated as a decision already made: it takes no question slot, no recommendation may argue from the scope it excludes, and it is written into `## Rough scope` unless you reverse it during the grill. A hedged one (*"maybe except…"*) is put to you to confirm. There is no style check and no structural pre-lint in this command — both first appear in [`/create-prd`](create-prd.md). A `status: draft` `idea.md` (any open `[NEEDS CLARIFICATION]`) is never handed off, regardless of what else the run resolved.

## Example

Refine an inline prompt, grounding it against the mounted frontend repo:

```
/product-workflows:idea PRODUCT-1234 "Add a dark-mode toggle to the settings page" --ground-code frontend
```

The run validates the key, classifies the argument as a prompt, ingests it via `idea-reader`, grounds it against the documentation when `$DOCS_PATH` resolves, grills it, and writes `idea.md` into the folder the key names — creating that folder with this first write where none exists yet. The key is not optional — without it the run stops before Phase 1.

Refine a note that links a mockup and a couple of related pages:

```
/product-workflows:idea PRODUCT-1234 @notes/dark-mode.md
```

Here the run walks every link that note makes, has each linked image transcribed, and hands the grill both the prose and what the frames show — asking first if the walk reaches further than two levels of pages, twelve pages or six images.

## See also

- [Roles and phases](../roles-and-phases.md) — what the `pm` role owns and hands off at the `prd-creation` seam.
- [`/create-prd`](create-prd.md) — the next phase; finds `idea.md` in the folder `/idea` wrote it into, once the pull request `/idea`'s handoff opened is merged. While that pull request is open `/create-prd <KEY>` stops on it. Where nothing was handed off — a declined handoff, one whose gate failed, or a draft — `/create-prd <KEY>` names the file without reading it in contract, and `/create-prd <KEY> @<path>` reads it where it sits: the form `/idea` offers in each case.
- [Model routing](../reference/model-routing.md) — the classification and model-fallback rules `/idea` applies in Phase 0.
- [Session cost](../reference/session-cost.md) and [Session feedback](../reference/session-feedback.md) — the terminal Phase 6 bookkeeping every run emits.
- [`idea-format.md`](../../references/idea-format.md) — the canonical structure `idea.md` is authored against, and the *Vendored sources* rules for `attachments/`, `design/idea-sources/`, the collision suffix, and the link rewriting. The frame-set index format is not its — that moved to `workflows-core:grounding-format` §6.2 when `/workflows-core:frames` became a second writer.
- `workflows-core:grounding-format` — §6.1 reserves `design/` for exported frame sets and makes each set's index mandatory, which is why `/idea` writes one for the images it vendors; §6.2 is that index's format and the reconciliation contract both writers execute.
- `/workflows-core:frames` — the other writer of that index, and the way to fill any row `/idea` had to leave as `_no description on record_`. It ships in the companion `workflows-core` plugin.
- `workflows-core:docs-grounding` — the documentation-grounding resolution gate and how a grill command consumes its digest.
- [`/prd-ground`](prd-ground.md) — the optional, ungated run, on the same PRD folder, that later grounds this command's vendored `design/idea-sources/` frame set and PRD-level rows against code and design — the verified pass `--ground-code`'s scoping sweep is not.

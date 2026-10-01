# BRD-to-PRD route

`/idea → /create-prd` starts from a prompt, file, community post, or existing PRD that the PM
already owns and can shape freely before anything is written down. The BRD-to-PRD route starts
somewhere the PM has far less control: a business requirements document the customer supplied,
handed over as-is — typically long, internally inconsistent in places, and not something a team
could build against without first finding out which of its claims are actually still true. This
route exists to turn that document into a requirement inventory every row of which has been
checked against real code and design, given a recorded fate, decided, and put back in front of the
customer who wrote it — before a PRD is ever written from it. It is PM-owned end to end: five of
its six commands run as PM, and one, `/prd-ground`, is PM-initiated but PA/Dev-executed — it is the
step that actually opens the mounted repositories and design assets to check a claim, work that
sits with PA/Dev rather than PM.

## The six commands, and where they hand over

```mermaid
flowchart TD
    subgraph PM["PM — owns the route"]
        intake["/brd-intake &lt;BRD&gt;"]:::prod
        splitroot["/brd-split &lt;BRD&gt; &lt;instruction&gt; (full)"]:::prod
        splitslice["/brd-split &lt;SLICE&gt; (allocate-only)"]:::prod
        interview["/brd-interview &lt;SLICE&gt;"]:::prod
        package["/brd-package &lt;SLICE&gt;"]:::prod
        reconcile["/brd-reconcile &lt;SLICE&gt;"]:::prod
    end
    subgraph PAD["PA/Dev — grounding, PM-initiated"]
        ground["/prd-ground &lt;SLICE&gt;"]:::prod
    end
    subgraph OFF["Off-platform — the customer, with a vanilla agent and nothing installed"]
        review["the customer reviews the bundle"]:::cust
    end
    subgraph OUT["PM/PA/PE — the PRD pipeline this route hands over to"]
        createprd["/create-prd"]:::prod
        createard["/create-ard"]:::prod
        specify["/specify"]:::prod
    end

    intake -->|inventory + ledger| splitroot
    splitroot -->|each confirmed slice, a PRD- folder| ground
    ground -->|"verified [CG#n]/[DG#n] — required before the walk"| splitslice
    splitslice -->|allocated ledger| interview
    interview -->|"decisions.md + held [C] questions"| package
    package -->|bundle sent| review
    review -->|answers come back as one file| reconcile
    reconcile -.->|a decision reopened, or a question askable again| interview
    reconcile -.->|questions still held for the customer| package
    reconcile -->|slice key + the BRD route — nothing left to re-enter for, fully allocated, one row covered-here| createprd
    reconcile -->|slice key + the BRD route — nothing left to re-enter for| createard
    reconcile -->|slice key + the BRD route — nothing left to re-enter for| specify
    interview -.->|nothing for the customer to review, PRD-eligible — no reconciliation needed| createprd
    interview -.->|nothing for the customer to review — no reconciliation needed| createard
    interview -.->|nothing for the customer to review — no reconciliation needed| specify

    classDef prod fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    classDef cust fill:#f3f4f6,stroke:#6b7280,color:#1f2937
```

**The right-hand box is not part of the route.** Its three nodes are the PRD pipeline's own
commands, drawn here because `/brd-reconcile` is where this route hands over to them — and `/brd-interview`, on a slice that needs no customer review — and a reader
following the diagram needs somewhere to go next. The route itself is still the six commands above —
five `/brd-*` commands and `/prd-ground`: nothing in that box extracts a requirement or allocates a ledger row —
each of the three reads what this route already wrote, at its own altitude, beside the documentation
under `$DOCS_PATH` and, for `/create-ard` and `/specify`, the code under `$REPOS_PATH`, and stamps
`consumed_by` on what it took. The one record any of them adds to the route's own is
`/create-prd`'s: an `[AS#n]` in `decisions.md` for a gap only the customer can settle, which
`/brd-package` then carries to the customer.

**The `Off-platform` box is the route's defining feature, not a decoration.** Everything else in
the diagram is a command this plugin runs; that box is a wait, and nothing in the plugin can
shorten it. `/brd-package` renders a self-contained prompt and a de-Obsidianised bundle precisely
because the person on the other side has a vanilla agent and nothing installed — no plugin, no
skills, no MCP server — and cannot ask what a path means. Between the two solid edges crossing that
boundary, the package has to physically reach a customer and the customer has to answer, which is
why `/brd-reconcile` takes the returned file as an argument rather than looking for it: the route
resumes when somebody says *this file is the answer*, and not before.

**`/brd-split` runs at least twice, and grounding sits between the first two runs.** The first run stands on the
root: a root is never ground, so it carves candidate slices from a mandatory slicing instruction
instead, and forces every row of the root's own ledger to a recorded fate — assigning it to a named
slice, deferring it, rejecting it against a logged defect, or marking it superseded. Each confirmed
slice re-enters at `/prd-ground`, and the second `/brd-split` run — on that same slice, in
**allocate-only** mode — walks its own ledger to a recorded fate with the findings already in hand,
offering a different four: `covered-here` in place of `covered-by`, since nothing can exist below a
slice but its Epics. That second run is what hands on to `/brd-interview`; the root's own key takes
no further step **forward**. It still takes other runs — `/brd-split` again (to carve a further
slice, to resolve a child left standing empty, or for the sibling re-cut below), `/brd-intake` again
on a revised document, `/frames` over its `design/`, and
[`/brd-proposal`](commands/brd-proposal.md), which rolls its slices' proposals up and gates nothing downstream —
while every one of `/prd-ground`, `/brd-interview`, `/brd-package` and `/brd-reconcile` refuses a
resolved root outright. So a requirement ordinarily reaches a fate twice —
once by the root's walk, once by the slice's — before it either has a home to be built in or a
recorded reason it does not. The two dashed edges leaving `/brd-reconcile` are different in kind:
they are not capped, because a review can legitimately reopen a decision or leave a question the
customer did not answer, and either state is settled by running the command that owns it again.

**There is a third occasion, and it is a re-run on the parent: the sibling re-cut.** The route carves a
slice before it is ground, so *"this slice is larger than one deliverable"* is a normal discovery,
and the route's first answer to it is deferral — the slice's own walk sends the rows it will not
build to `deferred-to: <itself>`, where they stay its live obligation. That is enough for *build less
now* and not enough for *two independently deliverable slices*, because the blocker sits on the
**parent**: its row for the delegated requirement reads `covered-by: <that slice>`, the walk visits
only `unallocated` rows, and no command returns one row to `unallocated` — a `/brd-intake` re-run
whose read finds a requirement reopens every row at once, discarding every fate the walks recorded.
So the parent is given one narrow way to move it. Where a slice's own ledger records `deferred-to`
against a row its parent delegated to it — two ledgers already agreeing that nobody is building the
requirement — an instruction typed against the parent's fully-allocated ledger, `/brd-split
<PARENT-KEY> "<what to peel off>"`, re-points that row onto a **sibling under the same parent that
has not been interviewed and does not already hold a ledger row for that requirement**: one already
standing, or one that same run carves. The receiving slice's own ledger
seeds the row `unallocated` — a **new** row, which is why a sibling already holding one for that
requirement is not its receiver — so it re-enters at `/prd-ground` — with a row no finding on file was
derived against — and its own `allocate-only` walk then takes the row to `covered-here`. **The
precondition carries the whole mechanism**: `deferred-to` is the owner writing down that it is not
building this, so the parent re-points against a refusal on record and never over a live commitment.
The invariant that matters is untouched — no row returns to `unallocated`, so no satisfied gate
reopens — and nothing is inherited with the row: the findings and decisions stay with the slice that
gave it up, and the receiver re-derives against the same pins.

**Two mechanisms split work on this route, and the line between them is not size.** [`/epics`](commands/epics.md)
carves a PRD into `EPIC-` folders, and `/dev-workflows:design`, [`/specify`](commands/specify.md) and
`/dev-workflows:ready` all work per Epic. But Epics sit **downstream of the customer loop**, which runs at slice level before
[`/create-prd`](commands/create-prd.md): an Epic split is invisible to the customer, and a slice
split is visible to them. **That is the line.** A slice too large for one delivery, whose split need
not reach the customer, is an Epics problem and stays one. A slice whose split must reach the
customer — a separate package, a separate conversation — is what the re-cut is for.

`/brd-intake` walks every link the customer's document makes, wikilinks included, read-only, and
shows the operator what it found — the count of markdown files, images and files that are neither,
inside the document's own folder and outside it; every target it could not resolve, with its reason;
and by path every file outside the folder and every file that is neither markdown nor an image. Then
it copies the document in verbatim and immutably together with every file they take — files
outside its folder into `brd/source-external/` — since no later command writes under either directory, and a
screenshot left uncaptured stays out of the record until the document is intaken again. It reads the
linked markdown beside the document and has every linked image it takes transcribed, extracts a
`[BR#n]` requirement inventory from all of it, confirms candidate defects with a human, and writes a
coverage ledger with every row `unallocated`. `/brd-split`, run on the root, proposes candidate
slices from a mandatory slicing instruction — a root is never ground, so the instruction is the only
grouping signal there is — and walks every unallocated ledger row to one of four recorded fates:
assigning it to a named slice, deferring it, rejecting it against a logged defect, or marking it
superseded, until none remain `unallocated`. **A BRD is a container and is never implementable
itself**, so this run always confirms at least one slice; where nothing clusters, the whole BRD
becomes one. A slice is not a new route: it nests inside its BRD's folder as the `PRD-` folder its
PRD will be authored in.

`/prd-ground` then pins every mounted repository to a verified commit and grounds every `[BR#n]`
this slice claims against code and an exported design frame set, with every finding independently
re-derived before it counts as evidence — the pass a root never gets, since a root is never ground.
`/brd-split` then runs a second time, on that same slice, in **allocate-only** mode: it offers a
different four and creates nothing, because nothing can exist below a slice but its Epics.
`covered-by` is the resolution it does not offer — not because a slice may not carry one,
but because the one a slice carries is written by the parent's own walk: when that walk withdraws a
claim, the claim and the copied inventory row go, the ledger row stays (a ledger row is never
deleted), and it records the sibling — or the parent — that took it. **Two routes reach that one
state**: a claim that was never more than provisional, settled on a different slice by the same walk
that proposed it; and a claim this slice had committed to and then recorded `deferred-to` against,
which a later re-cut moved to a sibling. The cap
is on nesting, not on allocation: a slice's rows must reach a fate too, or the slice could never
become a PRD of its own.

`/brd-interview` then works the BRD's open questions to recorded decisions, one round at a time,
under a single rule: every question is tagged `[G]` / `[V]` / `[C]` before it is asked, and the tag
decides who may answer it — a `[G]` from the grounding findings and never a human, a `[V]` from the
delivery team with recorded argumentation, a `[C]` held for the customer. `/brd-package` takes the
register and the held `[C]` questions, attacks the package before the customer does, refuses to
build a bundle while any `[SR#n]` self-review finding is undisposed, refuses to ship one whose own
identifier and filename citations do not resolve inside it, and renders the prompt, the delivery
note, and the dated bundle. `/brd-reconcile` takes the file that comes back, freezes each
confirmed answer as a `[CD#n]` only once an operator has confirmed it against the customer's own
words, and then sweeps every dependent BRD and every artifact still asserting a position the answer
overturned.

**A decision resting only on findings a prerequisite is about to make false is answered, not
settled.** Both `/brd-interview` and `/brd-reconcile` write it `conditional_on` that prerequisite or
hold it `open`, and close its question, so its round can close: what waits is the record. Its exit
is a later round — and, for one written `conditional_on`, also `/brd-reconcile`'s propagation sweep,
which reaches it by that field when the prerequisite's decision moves; that sweep's citation pass
also reaches a held record of either kind that names an id its reconciliation changed. The round comes once the
prerequisite has shipped, which the route sees as a `/prd-ground --rebaseline` pass whose successor
findings no longer carry `will-change`: every such pass supersedes the findings it re-grounds, but
keeps `will-change` on a successor until the prerequisite ships. Then a new `/brd-interview` round is
askable, and the round opened puts the question again against the current findings, under the tag
it had. The answer supersedes the held record where it reads `open` or `decided`, in `/brd-interview` for
a `[V]` and in `/brd-reconcile` for a `[C]`, which reads each status as the register stood before
its run wrote anything; one a propagation sweep reopened meanwhile is re-decided in place, and one
another run left `withdrawn` or `superseded` does not move. For a `[V]` the answer is then a new
record named beside it under what still needs a human; for a `[C]`, `/brd-reconcile` acts on a
superseded record's live successor instead, and on a withdrawn one freezes nothing, and closes the
question whichever way the operator takes the answer.

**A settled decision a re-grounding moved is reopened.** Where a re-grounding supersedes
any finding a decided `[VD#n]` or `[CD#n]` the will-change rule did not hold rests on,
`/brd-interview` reopens it, naming the successor findings as the cause, unless every superseded
finding has a successor — a later finding on the same requirement (or, for a design finding tied
to no requirement, on the same frames), grounded against the same repository or frame set — and each successor carries the verdict its superseded finding carried,
kept on that finding as `prior_verdict`, and the horizon that finding carried; a finding it rests
on that was not superseded stands as cited. A `/prd-ground --rebaseline` pass is not the only run
that supersedes: any `/prd-ground` run whose verifier contradicts an on-file finding — one an
earlier run wrote — supersedes it too, appending a successor that carries the verifier's verdict
rather than rewriting it in place, and so does any run that moves an on-file finding's horizon,
appending a successor with the same verdict and the new horizon, so a decision citing either is
tested like any other. A reopened
decision has its question put in the next round, and a confirmed one raises nothing. A `[V]` is
re-decided there, and a `[C]` by
`/brd-reconcile` from the customer's answer in the next package, each keeping its id — unless another
run has meanwhile left the record `withdrawn` or `superseded`, when it does not move: a `[V]` answer
is then a new record named beside it under what still needs a human, while `/brd-reconcile` acts on
a superseded `[CD#n]`'s live successor and freezes nothing beside a withdrawn one, closing the
question whichever way the operator takes the answer.

**A decision reopened elsewhere is put again too.** `/brd-reconcile` reopens a decided `[VD#n]` or
`[CD#n]` when a customer answer contradicts or constrains it without replacing it, and its
propagation sweep reopens one in a dependent BRD when the prerequisite decision it rests on moves.
The next `/brd-interview` round opened on that BRD puts the decision's question again, under its own
tag and against the current findings, with each `Reopened` paragraph quoted as context, unless a
question already putting it is still unanswered; the answer re-decides it in place, keeping its id.
Every question that puts a decision again names it on a `- **Re-puts:**` line, and that line is how
each command ties the answer back to the decision.

**Where the route hands over is `/brd-reconcile`**: a BRD whose customer decisions are frozen and
whose tree holds nothing the review made false is the state the PRD pipeline is entered from.
the BRD route **ships** on `/create-prd`, `/create-ard` and `/specify`, and `/brd-reconcile`'s
next-step phase names all three — **against a slice key, and on a run that left nothing to re-enter
for.** **A slice that needs no customer review hands over one step earlier**: where `/brd-interview`
settled every question from the findings, it names the same three on the same conditions, since each
gates the slice's `decisions.md` and none reads a reconciliation record. The conditions below are
written for `/brd-reconcile`'s phase and bind `/brd-interview`'s offer the same way, and
`/brd-interview` makes its own advance/re-entry split: a reopened decision waiting on the next round
takes a list of its own, which offers that round and none of the three.

**The first condition is the level, and it is the one this increment added.** A BRD is a container:
`prd.md`, `ard.md` and `specification.md` are authored in the `PRD-` slice folders under it, one of
each per slice, and all three commands refuse a `BRD-` folder in their own Phase 0
(`CREATE_PRD_BRD_NOT_SLICED`, `CREATE_ARD_BRD_NOT_SLICED`, `SPECIFY_BRD_NOT_SLICED`). A root BRD
never reaches this phase at all: `/brd-reconcile` refuses a resolved root at its own Phase 0, with
`BRD_RECONCILE_ROOT_LEVEL`, naming `/brd-split <BRD-KEY> "<how to cut it>"` as the way to carve a
slice first — so the level question is already settled by the time this next-step phase runs.

That phase then resolves an `advance_ready`: a reopened decision, a `[C]` still held for the
customer, a finding the review left to re-derive, or a dependent it could only record all drop the
three advance options, because a `reopened` record may not be consumed downstream and all three
consume the register. On an advancing slice run, `/create-prd` on the BRD route carries one further condition —
the reconciled ledger leaves no row `unallocated` and at least one `covered-here` (the two refusals
its own Phase 0 raises) — while `/create-ard` on the BRD route and `/specify` on the BRD route carry none of
their own, since neither reads the ledger as an authoring input, and the PRD gate both run reports an absent PRD rather than stopping on it.
The difference is where the enforcement sits: the level test and `/create-prd`'s eligibility test are
each refused by the offered command's own Phase 0, whereas the one gate all three run on the register
— `require-on-main` on `decisions.md`, stopping on a register left on an unmerged branch — tests
which ref it is on and never what it holds, so nothing downstream refuses a merged register carrying
a `reopened` or `open` record, and the advance/re-entry split is a judgement only the offering station can make — `/brd-reconcile`, or `/brd-interview` on a slice that needs no customer review. That same gate is why all three advance options carry the `<merge-clause>`: the register
is one of the files `/brd-reconcile` hands off, and each offered command stops until it is merged. **The diagram above draws all three**, as the three solid edges leaving
`/brd-reconcile` into the right-hand box. They are alternatives rather than a sequence: neither of
the other two waits on anything `/create-prd` on the BRD route produces, so an ARD or a specification can
be authored from a BRD whose ledger will never qualify for a PRD of its own. [Workflow overview](workflow.md) draws
the same three edges with the same labels, into the same three commands.

## Parameters

One row per command, derived from its own argument parsing — the flags below are exactly what each
command accepts today, not a preview of what a later increment adds. The first six rows are the
route; the last three are the handover the diagram draws, shown in their the BRD route form only —
each of those three also has a keyed form that this route never uses.

| Command | Required | Optional | Notes |
|---|---|---|---|
| `/brd-intake` | `<BRD-KEY> @<brd-file>` | `--sort-existing <dir>`, `--no-docs`, `--docs <path>` | Source must already be markdown — a PDF or similar is rejected, never converted. `<BRD-KEY>` names a folder, never a tracker ticket |
| `/prd-ground` | `<BRD-KEY>` | `--depends-on <BRD-KEY>…`, `--rebaseline`, `--derivation-matrix` / `--no-derivation-matrix`, `--no-code`, `--no-design`, `--no-docs`, `--docs <path>` | A root BRD is never ground (`PRD_GROUND_ROOT_LEVEL`); grounding runs at a `PRD-` folder — a slice, or an idea-route PRD folder. Needs `$REPOS_PATH`; read-only on every repo |
| `/brd-split` | `<BRD-KEY> [<instruction>]` | — | No flags. Mandatory on a root still holding an unallocated row (`BRD_SPLIT_NEEDS_INSTRUCTION`), optional on a slice (allocate-only there), and on a fully allocated root it means the sibling re-cut |
| `/brd-interview` | `<BRD-KEY>` | `--round N` | Only a slice is interviewed — a root stops with `BRD_INTERVIEW_ROOT_LEVEL`. No flag continues at the first open question; `--round N` resumes or re-opens one, cause recorded |
| `/brd-package` | `<BRD-KEY>` | `--depends-on <BRD-KEY>…` | Only a slice is packaged — a root stops with `BRD_PACKAGE_ROOT_LEVEL`. `--depends-on` is repeatable; a mistyped key is warned and dropped, never fatal |
| `/brd-reconcile` | `<BRD-KEY> @<review-file>` | `--sent <path>…` | Only a slice is reconciled — a root stops with `BRD_RECONCILE_ROOT_LEVEL`. The review is taken at whatever path it arrived on and is never searched for |
| `/create-prd` | `<SLICE-KEY>` | `--lean`/`--hybrid`/`--full`, `--no-docs`, `--docs <path>`, `@<idea.md>` | A `BRD-` container is refused. Otherwise offered only where the slice's own claimed rows leave none `unallocated` and one `covered-here`. Profile defaults to `--full`; `--from-prd` accepted |
| `/create-ard` | `<SLICE-KEY>` | `--no-docs`, `--docs <path>` | A `BRD-` container is refused. Otherwise offered on any advancing slice run; gates `prd.md` as on the idea route, never authors from the ledger. One address (`CREATE_ARD_ONE_ADDRESS`) |
| `/specify` | `<SLICE-KEY>` | `--no-docs`, `--docs <path>` | A `BRD-` container is refused. Otherwise offered on the same terms as `/create-ard`. One address; a second token stops it (`SPECIFY_ONE_ADDRESS`) |

`--no-docs` and `--docs <path>` appear together on two of the six **route** rows and mean the same
thing on both: turn off, or point at another root, the optional grounding on shipped product
documentation that `/brd-intake` and `/prd-ground` do when `$DOCS_PATH` resolves. The other four route commands have no such flag because none of them does
docs grounding to turn off — `/brd-split` allocates requirements, and the last three work on
decisions already taken, on which a documentation page (a claim *about* behaviour, not the
behaviour) settles nothing. The pair reappears on all three **handover** rows, where it turns off or
re-points that same grounding in the authoring run itself rather than in the route. See
`workflows-core:docs-grounding` for the resolution gate and the two
consumption modes this route uses.

`<BRD-KEY>` follows the same shape everywhere in this route: `^[A-Z][A-Z0-9_]*(-\d+)+$`, checked
for shape only and never against a tracker — a BRD is a markdown file under `$SPECS_PATH`, not a
tracker ticket. **That shape is two segments or three**: a BRD owning its source document is keyed
`EPIC-008` and a slice of it `EPIC-008-01`, and the grammar prefers neither — a key's segment count
is a naming convention, never a depth declaration. Every command after `/brd-intake` resolves a key
through `resolve-address`, which searches three levels below `specifications/` — a BRD folder
directly under it, the `PRD-` folder of a slice inside that, and an `EPIC-` folder below either kind of
PRD folder — because a root has to resolve before it can be refused by name.
`/brd-split` alone acts on either level once resolved; `/prd-ground`, `/brd-interview`,
`/brd-package` and `/brd-reconcile` each refuse a resolved root outright. An idea-route PRD folder —
a `PRD-` folder carrying no `brd-link.md`, never carved from a BRD — is refused by `/brd-split`,
`/brd-interview`, `/brd-package` and `/brd-reconcile` (`BRD_SPLIT_NOT_A_BRD`,
`BRD_INTERVIEW_NOT_A_SLICE`, `BRD_PACKAGE_NOT_A_SLICE`, `BRD_RECONCILE_NOT_A_SLICE`), each naming `/create-ard` and `/specify` as the way that route goes on;
`/prd-ground` grounds one. `resolve-address` searches the Epic level too, so a key naming an
`EPIC-` folder resolves as readily, and all five refuse it before any gate
(`PRD_GROUND_EPIC_LEVEL`, `BRD_SPLIT_EPIC_LEVEL`, `BRD_INTERVIEW_EPIC_LEVEL`,
`BRD_PACKAGE_EPIC_LEVEL`, `BRD_RECONCILE_EPIC_LEVEL`), each naming the folder above the Epic where
that command runs on it. `/brd-intake` runs on no existing folder but a root: a key resolving to an Epic folder stops with
`BRD_INTAKE_EPIC_LEVEL`, and one resolving to an idea-route PRD folder with `BRD_INTAKE_NOT_A_BRD`,
before anything is copied into it. The three handover rows
resolve through the same search too — and then **refuse the `BRD-` container**: a PRD, an ARD and a specification
are authored in a slice's `PRD-` folder, never in the `BRD-` container above it.

**The BRD route is detected, never declared**, on all three of those rows. There is no flag and no
`<dir>` operand: each command takes one positional address, and where that address resolves to a
folder carrying `brd-link.md`, the run is on the BRD route and prints which route it entered before
doing anything else. A flag that could disagree with the folder it names would be one more
disagreement to have.

## What lands where

Every artifact lands under `$SPECS_PATH/specifications/BRD-<BRD-KEY>-<slug>/` — the root's own
records at its top level, and everything from grounding onward in the `PRD-` slice folders nested
inside it (one level, and only one, per the addressing rule the whole route shares):

```
specifications/BRD-<BRD-KEY>-<slug>/
├── brd/
│   ├── source/<basename>        # the customer's file, copied verbatim — never edited; a revised re-intake replaces it
│   ├── source/<paths it links>  # every file the run took from the document's own directory, byte-for-byte
│   ├── source-external/<name>   # files the document links from outside its folder, when captured
│   ├── brd-inventory.md         # [BR#n] rows, /brd-intake
│   ├── brd-link-log.md          # captured files' uncaptured links, with reasons, and the as-written map, /brd-intake
│   ├── brd-figures.md           # each captured image's transcription and the rows it yields, /brd-intake; /brd-reconcile applies a customer's correction
│   └── brd-defect-log.md        # confirmed [DEF#n] entries, /brd-intake and /brd-reconcile
├── coverage-ledger.md           # one row per [BR#n]; /brd-intake writes it, /brd-split resolves it
├── slices.md                    # slice rationale and deferral notes, /brd-split
├── design/                      # exported frame sets — one subdirectory each, images + an index; /frames indexes it, no grounding reads it (a root is never ground)
├── dev-workflows/               # session bookkeeping: resume pointer, feedback, cost entries
└── PRD-<CHILD-KEY>-<child-slug>/ # a slice /brd-split confirmed — where its PRD, ARD and spec are authored
    ├── brd-link.md              # parent, claims and depends-on; /brd-split writes it, /prd-ground, /brd-package and /brd-reconcile add depends-on
    ├── brd/brd-inventory.md     # the parent's rows this slice claims, copied verbatim, /brd-split
    ├── coverage-ledger.md       # one row per claimed [BR#n]; /brd-split seeds and resolves it, /prd-ground fills evidence, /brd-reconcile moves a row on a frozen [CD#n]
    ├── grounding/
    │   ├── baselines.md         # one dated entry per pinned repository, /prd-ground
    │   ├── code-grounding.md    # [CG#n] findings, /prd-ground
    │   └── design-grounding.md  # [DG#n] + ## Frame sets covered, /prd-ground (always written)
    ├── design/<frame-set>/      # what /prd-ground Phase 5 reads; no index means it is not read
    ├── decisions.md             # the register: [VD#n] and [AS#n] from /brd-interview, [AS#n] also from /create-prd, [CD#n] from /brd-reconcile
    ├── code-defect-log.md       # [CDF#n] code defects a decision turns on, from /brd-interview
    ├── interview/
    │   ├── round-<N>.md         # one append-only record per round, /brd-interview
    │   └── customer-questions.md # the [C] questions held for the customer, /brd-interview; /brd-reconcile marks each answered
    ├── self-review-<date>.md    # every [SR#n] with its disposition, /brd-package
    ├── customer-review-prompt-<date>.md # the self-contained prompt the customer pastes, /brd-package
    ├── customer-delivery-note-<date>.md # the covering letter — the email, not a bundle document, /brd-package
    ├── bundle-<date>/           # the de-Obsidianised bundle actually sent, /brd-package
    ├── customer-review-<date>.md # the returned review, copied in byte for byte, /brd-reconcile
    ├── customer-sent-<date>/    # what the customer was sent, --sent runs only, /brd-reconcile
    ├── reconciliation-<date>.md # what the review changed and what still needs a human, /brd-reconcile
    └── attachments/             # reserved at either level; no command writes it on this route (/idea, its one writer, refuses a slice)
```

A root written before grounding moved to the slice may still hold `grounding/`, `decisions.md`,
`interview/` and the packaging and review files at its own level. No command creates them there
any more — `/prd-ground`, `/brd-interview`, `/brd-package` and `/brd-reconcile` each refuse a
resolved root — and they are left in place rather than moved. (A slice's `/brd-reconcile` can still
edit one: its stale cross-reference sweep reads every markdown file under the parent, and may
update the argumentation of a record in a leftover root `decisions.md`.)

Two of those entries are **reserved subdirectory names** rather than this route's own files, and both
are shared with the idea route: `design/` holds exported frame sets, one immediate subdirectory each,
images plus an index that `workflows-core:grounding-format` §6.1 makes
mandatory — `design-grounder` returns `NO_INDEX` rather than read a frame set without one, because a
filename is not a reliable statement of what a frame shows. `attachments/` holds the text and markdown
sources a run copied into the folder; [`/idea`](commands/idea.md) is its only writer — the companion
`docs-workflows` plugin's `/document` reads an image it finds there as one of its screenshot sources
and leaves it in place, but places a new one in the folder's `Doc screenshots/` subfolder, never here
— and `/idea` writes only into an idea-route PRD folder — it refuses a BRD container and a BRD-route slice alike
(`IDEA_NOT_AN_IDEA_FOLDER`) — so on this route the name is reserved and nothing writes it, and neither
is its `design/idea-sources/` frame set. Neither name carries a key, neither is resolved by one, and
both are reserved at either level — a `BRD-` folder or a `PRD-` folder inside it.

The dated artifacts are the ones to read carefully. **A dated bundle is never rewritten**, and a
superseded snapshot is bannered rather than edited: rewriting either destroys the only evidence of
what the reviewer of that date was actually looking at, after which every claim in their returned
review silently re-points at a document they never saw. `customer-review-<date>.md` carries the
**customer's** date, not the run's, and is committed before anything reads it.

A slice starts life with three of those files, all written by the parent's `/brd-split` run:
`brd-link.md`, a `brd/brd-inventory.md` holding the parent's rows it claims (copied verbatim — the
slice has no `brd/source/` and no `brd/brd-defect-log.md` of its own, and inherits both from its
parent), and a `coverage-ledger.md` with every row `unallocated`. That is what the solid edge from
the root's `/brd-split` into `/prd-ground` above is: `/prd-ground` needs a ledger to gate on and an
inventory to read, `/brd-intake` never runs on a slice — there is no separate document to intake, and
a key that resolves to one stops the run with `BRD_INTAKE_SLICE` —
and `/brd-split` is the only command holding both the parent's rows and the allocation that says
which of them the slice claims.
The slice keeps no `brd/source/` and no `brd/brd-defect-log.md` of its own and reaches for its
parent's, and that reach is always exactly one hop: with nesting capped at one level, a slice's
parent is always the BRD that owns the customer's document. That one hop is live rather than
theoretical — it is how a `rejected: [DEF#n]` is resolved when `/brd-split` walks the slice's own
ledger, and it is where a slice's `/brd-reconcile` writes the defect resolutions its customer review
settled. **Both of those
are the `[DEF#n]` requirement defect log**; `code-defect-log.md` in the tree above is a different
register and is the slice's own, because a code defect belongs to the slice's own grounding and
grounding is slice-only. There is no hop for it.

Everything else a slice produces is its own. It holds its own register, its own `[C]` question set,
its own bundle and its own reconciliation record — and it is the only level any of the last three
commands ever reaches: `/brd-interview`, `/brd-package` and `/brd-reconcile` each refuse a resolved
root outright.

`--sort-existing <dir>` on `/brd-intake` additionally writes `prd-seed.md`, `ard-seed.md`, and
`spec-seed.md` at the BRD folder's own level — a one-time migration path for a package written by
hand before this route existed, not an output of the normal flow. **It is the only writer of any of
the three**, which is worth stating plainly because the BRD route on `/create-prd`, `/create-ard` and
`/specify` each reads one: a reconciled BRD normally holds no seed at all, so each of those runs
reports its seed absent as the **ordinary** case rather than as a gap. What actually carries content
to all three altitudes is `decisions.md` — every one of them reads the same register and filters it
by each record's `altitude` — together with the grounding findings, and, for `/specify`, the
derivation matrix appended to `code-grounding.md`. See [Workflow
overview](workflow.md) for where this route's artifact home sits relative to the rest of the
pipeline's, and [Roles and phases](roles-and-phases.md) for what each role owns across both routes.

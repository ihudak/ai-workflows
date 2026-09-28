# /frames

(Re)builds the frame-set index of one resolved folder — for every `design/<frame-set>/` subdirectory it holds, it lists the images, reads the index already there, describes the frames no row accounts for, and writes the index.

## Who runs it

Anyone who put frames in the specs tree, at any point in the pipeline. `design/` is a reserved subdirectory of **any** folder under `specifications/` — a BRD folder, a PRD folder, or an Epic folder alike — so `/frames` resolves all three ([`addressing.md`](../../references/addressing.md) §3, with no kind narrowing). [Workflow overview](../workflow.md#cross-cutting-commands) groups it under the anytime commands: it advances no phase and belongs to no role's step.

It emits a session-cost entry all the same, with `phase`/`role` inferred from the resolved folder's own `kind` — a frame set in a folder asserting `kind: brd`, a BRD container or a BRD-route slice, is [`brd-to-prd`](../roles-and-phases.md#brd-to-prd)/`pm` spend; one in a folder asserting `prd` or `epic` is [`prd-creation`](../roles-and-phases.md#prd-creation)/`pm`, an Epic folder under a slice included. Describing forty frames is real work, and a run that measured nothing would not be free — its spend would roll into whatever command ran next.

## Why it exists

[`grounding-format.md`](../../references/grounding-format.md) §6.1 makes a frame set's index **mandatory, and a set without one a refusal**: `design-grounder` returns `NO_INDEX` rather than reading a set without one, because a filename is not a reliable statement of what a frame shows.

That is strict on purpose, and it left the obvious workflow with no way out. A human exports the frames of a screen flow, drops the folder into `design/`, and has a set the plugin refuses to read — recoverable only by hand-authoring an index. `/idea` writes one for the images it vendors, and nothing else did. `/frames` is the repair.

## Synopsis

```
/frames <KEY>|@<path> [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

One address, resolved with the same resolver every keyed command uses: a key, or `@<path>` to the folder or to a file inside it. No kind is passed, because `design/` is reserved at every level.

All three run flags apply to this command ([`environment.md`](../reference/environment.md)). `--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`) skips this run's session-cost entry, still advancing the checkpoint. `--skip-feedback` (or `$WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 4's maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance`. `--enforce-model=<model>` (or `$WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `frame-describer` and, under `--skip-feedback`, `defect-reporter` — to one model, bypassing the routing this page's [How it runs](#how-it-runs) section otherwise selects.

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve the address (kind-gated) + model routing"] --> p1["Phase 1 — Enumerate the frame sets"]
    p1 --> p2["Phase 2 — Reconcile, describe (frame-describer), write each index"]
    p2 --> p3["Phase 3 — Handoff (only where an index was written)"]
    p3 --> p4["Phase 4 — Session maintenance, feedback & cost"]
```

## What it needs

- **A folder that already exists, of one of the three kinds.** This command indexes; it creates no folder and refuses an address that resolves to none. An ambiguous key is a hard stop naming every match, and an address that resolves to something other than a BRD, PRD or Epic folder is refused by name — pointing `@<path>` at a frame *inside* a set resolves to the set, not to the folder that holds it, so the refusal says which folder to pass instead. A spec folder written before the carrier rule — one whose `prd.md`, `idea.md`, `epic.md`, `brd-link.md` or `brd/brd-inventory.md` asserts no `kind:` or `key:`, or, addressed by key, one holding none of those files — is refused separately, with its own remedy: give one of those files the `key:` and folder `kind` [`addressing.md`](../../references/addressing.md) §5 describes — where the folder holds none of them, and its PRD still carries a pre-rename name such as `<KEY>_<slug>.md`, rename that to `prd.md` and give it `kind: prd` and the key — or, where the folder holds an `idea.md` and no `prd.md`, run `/product-workflows:create-prd <KEY>`, whose `prd.md` gives it one; that last is offered on an `@<path>` only where the folder's name carries no kind prefix, since a prefixed folder asserting no key is one `/create-prd <KEY>` cannot find, and it would create a second.
- **One address, and no flags.** `/frames` defines none; a second address or a `--flag` is a stop rather than a silent discard, because a discarded second address is a folder you believe was indexed and was not.
- **An address is mandatory.** Absent or malformed, the run stops before anything is read.
- **`$SPECS_PATH`** — the specs-preflight step at Phase 0 settles the branch once the address resolves, before the folder is read or anything is written; silent when the repo is already clean and on its default branch.
- **Nothing else.** No PRD, no BRD, no code repo, no docs repo, and no Opus.

## What it produces

One `index.md` per frame set, in the format [`grounding-format.md`](../../references/grounding-format.md) §6.2 fixes — the same format and the same reconciliation contract `/product-workflows:idea` Phase 4.5 follows — that command ships in the sibling pipeline plugin, and this is the one file the two write in common, so two writers never leave one directory holding an index neither would have written. The index is rebuilt from the set **as it stands on disk**: every existing row whose image is still there is preserved verbatim — with one exception, and it is the whole convergence mechanism for a capped set: a row carrying `_no description on record_` holds no description to preserve, so the next writer that can obtain one fills it — a row is appended for each frame this run described, a row whose image is gone is dropped and reported, and a frame the run could not account for gets a placeholder row and is reported. There are **two** placeholders, and which one a row gets turns on whether a re-run would do anything different: `_no description on record_` where the run never looked (the cap bit, or the whole dispatch failed), which the next run retries; and `_could not be read: <reason>_` where the describer looked at that file and could not read it, which it does not.

Descriptions come from the `frame-describer` agent, which looks at the frames and returns one plain-language description each — an agent whose whole tool list is `Read`, `Glob`, `Grep`, so it cannot write the index it describes into. The command hands the frames to it rather than opening them itself, so every description in an index is one that something which actually saw the frame produced, and "transcribed, never inferred" is a rule about copying rather than a hope about restraint.

The indexes are deliverables, so they reach the default branch through the [phase handoff](../../references/phase-handoff.md) — each named as one literal path, behind the phase handoff's consent choice — the **advisory** variant, whose second option says no command stops on these and that what reads them reads your working copy. No gate consumes a frame-set index, but the design-grounding pass does read one, and refuses to reconcile a frame set that has none. Declining therefore leaves them written and on no ref, and that is an unshared repair rather than a blocked one: your own grounding runs read the frame set from the working tree and see the index, and nobody else's do.

## The cap

**Forty frames described per run**, counted across every set the run touches. `/idea` has no such cap: it reads mockups incidentally, to write a brief, and asks before reading past six images, then reads what you allow ten to an agent. This command is invoked *to* index and asks nothing first, so stopping at six would make it useless on the first real export it met, and it describes a whole set in one agent, which is the context forty bounds.

**What counts as a frame** is the extension set [`grounding-format.md`](../../references/grounding-format.md) §6.2 fixes — `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.webp`. One vocabulary, shared with `/idea`, because two writers of one index listing by two different sets would each drop the other's rows as frames that had gone missing. Anything else in the directory is not a frame, gets no row, and is named once in the report so it is visibly not indexed rather than invisibly absent.

**Where nothing is written, nothing is created.** A folder with no `design/`, a `design/` holding no subdirectory, and a frame set holding no frames are all clean outcomes reported as such — no directory is created, no index is written, and no handoff is offered, because there would be nothing to open a pull request for. Images dropped *directly* into `design/` rather than into a set are called out with the fix: a set is a subdirectory of `design/`.

**An index under another name** — a manifest, a captions file, a README enumerating the frames — is **read and adopted**, and still left byte-for-byte alone. Every row whose image is actually in the set carries across into `index.md` with its description preserved verbatim; a row naming an image the set does not hold is reported and not adopted, and a file that cannot be parsed into rows at all is reported with nothing taken from it. The original is never rewritten — this command did not author that file's shape and will not impose one — so the report names both files and how many rows carried across, and retiring the older one stays your decision. Before this, such a file was reported and never read, which meant a set that already had a hand-written manifest came out of an indexing run worse than it went in: every frame re-emitted as `_no description on record_`.

When the cap bites, every remaining frame still gets a row — `_no description on record_`, with `cap` as its reason — and the index is still **valid and complete**, because it is written once after every row is resolved. The run says how many frames it left, and a re-run describes the next forty: a row carrying that placeholder holds no description to preserve, so the next writer that can obtain one fills it. A hundred-frame set converges in three runs and is readable after the first.

**A frame the describer could not read is a different case, and it is not retried.** An oversized export, a file with a frame extension that is not an image — the describer looked at it and failed, so re-running reproduces the identical failure while spending budget a reachable frame would have used, and the set never converges. Three such exports once rejoined the describe set on every future run, forever. Those rows read `_could not be read: <reason>_`, are preserved like any real description, and are reported **individually with the remedy**: fix the file, then delete that row from `index.md` — the frame then has no row at all and the next run describes it. Nothing in a set records what a run read last time, so deleting the row is what tells the next run the file has changed.

## Gates

No reviewer, and nothing to review — an index states what a directory holds. The checkpoints are the specs-repo git guards (`specs-preflight` at the start, `commit-artifacts` at the end, [`specs-repo-git.md`](../../references/specs-repo-git.md)) and the handoff's own consent choice. **Nothing in the indexing pass is fatal**: a frame that will not open, a set that could not be described, an index that could not be written — each is recorded and the run moves to the next set. Phase 0 is the exception and is where every hard stop lives (`FRAMES_NEEDS_ADDRESS`, `FRAMES_EXTRA_ARGUMENT`, `FRAMES_NO_FOLDER`, `FRAMES_NO_CARRIER`, `FRAMES_NOT_A_SPEC_FOLDER`, an ambiguous key, and an unset `SPECS_PATH`) — the run refuses before it has resolved anything to index.

## What it is not

**Indexing makes frames readable; grounding makes them `[DG#n]` findings.** `/frames` dispatches no `design-grounder`, produces no finding, cites no requirement, and never reaches `grounding-verifier`, on either route — both of those agents ship in the sibling `product-workflows` plugin and are dispatched only by its `/product-workflows:prd-ground`. Design grounding on the `/product-workflows:idea` route ships in this same increment as the BRD route's own — §6.1 says so — and this command still keeps no part of it: `/frames` reconciles nothing on either route, only ever building the index a grounding pass then reads. The one command that grounds a frame set is `/product-workflows:prd-ground`, now on both routes.

It is also not `/design-index`, deliberately. `/dev-workflows:design` is the engineering-design workflow, and a name adjacent to it would send an operator who wanted an index into the wrong command. *Frame set* and *frame* are §6.1's own vocabulary.

## Example

```
/workflows-core:frames ACME-77
```

Resolves `PRD-ACME-77-<slug>/`, finds `design/checkout-flow/` holding eleven PNGs and no index, describes all eleven, and writes `design/checkout-flow/index.md` with eleven rows — then offers to open a pull request for that one file.

## See also

- [`grounding-format.md`](../../references/grounding-format.md) — §6.1 reserves `design/` and makes each set's index mandatory; §6.2 is the index format and the reconciliation contract both writers execute.
- `/idea` (in the `product-workflows` plugin) — the other writer: it indexes the images it vendors into `design/idea-sources/`, and leaves a placeholder row for any frame it cannot speak for.
- `/prd-ground` (in the `product-workflows` plugin) — the one command that *reads* a frame set as evidence, through `design-grounder`.
- [Agents](../reference/agents.md) — `frame-describer`, the bounded read this command dispatches once per set.
- [`addressing.md`](../../references/addressing.md) — the resolver that turns one address into a folder of any kind.

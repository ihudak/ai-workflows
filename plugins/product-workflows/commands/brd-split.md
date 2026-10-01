---
name: brd-split
description: BRD-splitting workflow (PM phase, the BRD-to-PRD route's allocation step — run once on a root to carve slices, then again on each slice to allocate it). On a root, proposes candidate slices from a verbal <instruction> the operator types after the key - mandatory wherever the run still has a row to place, since a root is never ground and the instruction is the only grouping signal there is - resolved against this BRD's own rows and grilled (bounded, <=5, and only where one answer places more than one row) before any slice is proposed. On a slice it gates on every grounding finding carrying a verifier verdict instead, and the same instruction stays optional there, seeding only the walk's per-row recommendation. A BRD is a container and is never implementable itself, so this command always produces at least one slice; where nothing clusters, the whole BRD becomes one. Each confirmed slice is keyed and nested as a PRD- folder inside this BRD - the folder its PRD will be authored in - carrying its own brd-link.md, inherited brd/brd-inventory.md, and unallocated coverage-ledger.md. It then walks every unallocated coverage-ledger row one at a time through four resolutions (assign to a named slice, defer to this BRD, reject citing a defect, or mark superseded) until none remain unallocated, and writes slices.md with the rationale for each slice and each deferral. Where one answer is uniform by construction and there is more than one row to save - exactly one slice standing on a parent, or any run on a slice, with two or more rows still unallocated that it may write, or, on a re-cut, two or more placed candidates carrying one confirmed receiver between them - Phase 4 first offers to write that single disposition across every remaining row in one confirmation, stating each row it would write and letting any of them be held back to the one-at-a-time walk, which stays the default and is what a declined or unparsed answer falls back to. covered-here is not among them on a parent: a parent builds nothing itself. Run on a slice it allocates but does not slice: nesting is capped at one level, so no child is created and the walk offers a different four - covered-here replaces covered-by, which on a slice records a claim this command's own walk on the parent withdrew - provisional on the ordinary route, committed and then deferred by the slice itself where a re-cut moved it - and the parent writes it. Existing children are enumerated by a positive test - a subdirectory carrying a brd-link.md whose parent: names this BRD - never by a name match. Re-running is a no-op that prints the ledger only where the ledger is fully allocated AND no child is out of step with it (its claims:, inventory and this ledger's covered-by rows for it disagreeing) AND no child is left standing while claiming nothing AND no row is re-cuttable under an instruction this run was given. A child out of step keeps even a bare run alive, which reconciles it; so does a standing empty child, which this is the only command that can remove or keep against a recorded reason; a re-cuttable row keeps only an instructed run alive. A child missing its inventory or ledger is reported and never reconciled. On a fully-allocated parent the instruction is otherwise free, and there it means the sibling re-cut: a row this BRD delegated to a child whose own ledger now records deferred-to against it may be re-pointed onto a sibling that has not been interviewed - the one case, apart from the key repair a removal performs (below), in which this command re-allocates a row already carrying a fate, taken against the owner's own written refusal and never over a live commitment, and it needs no flag. Removing a standing empty child first re-points every row still delegating to it - on this BRD's own ledger and on any other child's - onto this BRD, rather than leaving the key dangling. On a root, offers /prd-ground on each child that gained a row this run - a first run for a slice just keyed and for a standing child nobody ever ground, a re-run for a standing child that is already ground, whose grounding no longer covers everything it claims - as the next step (this BRD's own key has no further step: /brd-interview refuses any root outright). On a slice, offers /brd-interview on the slice just allocated.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Split the grounded BRD into slices and allocate every requirement: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/brd-split` is the **BRD-to-PRD route's allocation step** (PM phase) — on a root it carves the
slices `/prd-ground` will later verify each of, and forces every `[BR#n]` in this BRD's own coverage
ledger to a recorded fate: built by a named child, deferred, rejected, or superseded. On a slice it
carves nothing and instead takes the findings `/prd-ground` already verified, forcing every `[BR#n]`
in its own ledger to a recorded fate through the same four-way choice — with `covered-here` standing
in `covered-by`'s place: built here, deferred, rejected, or superseded. This is
the only place either BRD's fate is decided **by allocation** — `/product-workflows:brd-reconcile`
re-dispositions a row to `deferred-to`, `rejected` or `superseded-by` when a frozen `[CD#n]` settles
the requirement differently, and `rejected: <SLICE-KEY>/[CD#n]` is a spelling only it ever writes, so
*the only place a fate is ever decided* (which this sentence used to claim) is false of a slice
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md`
§1) — without this command's gate, a long BRD split across several children could have every child
quietly wave a requirement past, and nothing would notice.

Usage: `/brd-split <BRD-KEY> [<instruction>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

Runs on a root BRD or one of its slices (Phase 0 step 5 refuses an idea-route PRD folder and an
Epic folder, and step 8 stops, on a `full` run, any other folder whose inventory holds no `[BR#n]` row) — in one of **two modes** Phase 0 step 5 resolves from the folder itself:

- **`split_mode: full`** — a BRD that owns its source document. Everything below runs: slices are
  proposed, children are keyed and nested, and the ledger walk offers **four** terminal
  resolutions — `covered-by`, `deferred-to`, `rejected`, `superseded-by`. `covered-here` is not one
  of them: a parent BRD is a container and builds nothing itself.
An `<instruction>` is required in `full` mode wherever the run still has a row to place, and
optional in `allocate-only`, and what it seeds differs: in `full` mode — where a root is never ground and so carries no findings to group by — it
seeds the Phase 2 grouping *and* the Phase 4 walk's per-row recommendation; in `allocate-only`, where
Phase 2 never runs, it seeds the walk alone. That is why a slicing instruction on a slice is a real
invocation rather than an ignored one — `/product-workflows:brd-split <SLICE-KEY> build the order rows,
defer the rest` is a sentence this command can act on, and the picker it acts on is still the
four-resolution one.
**On a `full` run whose ledger is already fully allocated the instruction seeds a third thing, and it is the thing that run is invoked by: the sibling re-cut.** That is the one run on which the argument this route already made mandatory for carving a root is otherwise free — Phase 1.5 would place `unallocated` rows and there are none — so it is given a meaning there instead of a flag being added for it (Phase 0 step 9a, step 10). What it seeds is the same three-phase reading as any other instruction, over a different set: Phase 0 step 9a builds the **re-cut candidate set** — a row this BRD delegated to a child whose own ledger records `deferred-to` against it, two ledgers already agreeing that nobody is building it — Phase 1.5 places that set, Phase 2 fixes a receiver per group, and Phase 4's Step 2R offers each move one row at a time. It is the one case, apart from the key repair a removal performs (Phase 4.5), in which this command re-allocates a row that already carries a fate, it does so only against the owner's own recorded refusal, and it is bounded by that refusal and by nothing else (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2).

- **`split_mode: allocate-only`** — a slice. Nesting is capped at one level
  (`workflows-core:addressing` §6), so **no child may be created below a
  slice**: Phases 2 and 3 are skipped entirely and the walk offers **four** resolutions, without
  `covered-by`. That last part is about **who writes** the disposition, not about whether a slice
  may carry it: a slice's `covered-by` names a sibling or the parent and records a claim the
  *parent's* walk withdrew — still provisional on the ordinary route, committed by an earlier run
  and then deferred by this slice itself where a re-cut moved it (§3.2) — so it is already terminal
  before this walk reads the ledger
  (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2, §3). The cap is on nesting, not
  on allocation — a slice whose rows could never leave `unallocated` could never become PRD-eligible
  (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5), which would make slicing
  pointless. The run announces the mode rather than quietly behaving differently.

---

## Phase 0 — Resolve inputs and gate on verification

1. **`<BRD-KEY>` (mandatory).** **Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. Parse the first non-flag token; validate with `key-valid`
   (`workflows-core:addressing` §1). If absent or invalid, stop:
   `BRD_SPLIT_NEEDS_KEY: /brd-split needs a BRD key (shape ^[A-Z][A-Z0-9_]*(-\d+)+$) — re-run '/product-workflows:brd-split <KEY>'.`
1a. **`<instruction>` (mandatory on a root that still has a row to place, optional on a slice).** Every token after
   the key, joined verbatim, is a slicing instruction in the operator's own words — `cover orders and
   measurements in the first iteration`, `slice everything EPIC-008 still holds that no child covers` — a
   flag name among them where the operator wrote one as instruction text rather than as a flag.
   **Parse it here and carry it; its absence is stopped on in step 11, never here.** Phase 2 clusters by the Phase 1.5 placement — every `unallocated` row on an ordinary run, and every row in the **re-cut candidate set** on the re-cut path step 10 selects — and a root carries no findings to read, so the grouping comes from the instruction or from nowhere; but that is a statement about a run that *has* something to cluster, and whether this one does is not known until step 8 reads the ledger and step 9a builds that candidate set.
   Stopping on the absence here made the instruction mandatory on every `full` run, including the one
   on which Phase 2 never runs at all: a parent whose walk is complete and whose only remaining work
   is a standing empty child. Stops and offers across this route send the operator to exactly that
   run — `/prd-ground`'s and `/brd-interview`'s empty-inventory stops and this command's own on a
   slice among them — which Phase 4.5 exists to serve, and the operator taking it wants to carve nothing.
   Absent on a slice → this command behaves exactly as it did before the switch existed, on every
   path below; nothing in it is conditional on an instruction being given except where a phase says so. This command parses no
   flags of its own: the three run flags (`--skip-costs`, `--skip-feedback`, `--enforce-model`) are
   stripped by step 1's `strip-run-flags` call only where they sit before the key, or as a trailing run
   at the very end of `$ARGUMENTS` (`workflows-core:run-flags` §3 step 1, whose protected prose span
   begins right after the key) — so the instruction is simply everything that call leaves after the
   key, a flag name included wherever the operator typed one as instruction text instead of as a
   trailing flag. The instruction is **never validated against anything**: it is prose, and
   what it means is settled in Phase 1.5 against this BRD's own rows, never by pattern.
2. **`$SPECS_PATH` (required).** If unset, stop naming `SPECS_PATH`, per the
   `Required path environment variable unset` rule in `workflows-core:escalation-rules`:
   ```
   choices: ["Set SPECS_PATH (enter the path)", "Cancel"]
   ```
3. **Specs-repo preflight.** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline. Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice; if it returns
   `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag for the whole run — the terminal
   `commit-artifacts` step skips on it.
4. **Resolve the BRD folder.** `resolve-address <BRD-KEY>` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), which searches
   every level `workflows-core:addressing` §3 bounds — three below `specifications/`, plus §5's legacy fallback (§2 step 2) — and so can return any folder kind it finds there: a `BRD-` folder directly under `specifications/`, a `PRD-` folder (a slice inside a BRD, or an idea-route PRD folder), or an `EPIC-` folder inside a `PRD-` folder. Step 5 answers the level question on what it returns. Absent → stop, without asserting which command would create it, because nothing on disk
   says whether this key names a BRD with a source document or a slice of one:
   `BRD_SPLIT_NOT_FOUND: no folder found for <BRD-KEY> under $SPECS_PATH/specifications/ (every level addressing.md §3 bounds, plus §5's legacy fallback) — check the key. A BRD with a source document of its own is created by /product-workflows:brd-intake <BRD-KEY> @<brd-file>; a slice is created by /product-workflows:brd-split on its parent.`
5. **Resolve the run mode.** Read the resolved folder's `brd-link.md` and branch on its `parent:`
   field — the signal `/prd-ground` Phase 0 step 6 reads to tell a slice from a folder naming no parent
   (its step 5a tells a slice from a root by the directory prefix), and, unlike a key's segment
   count, a reliable one: a segment count is a naming convention, never a depth declaration
   (`workflows-core:addressing` §1).
   - **An Epic folder** → stop, before either mode is set, and before the idea-route test below.
     `resolve-address` searches every level `workflows-core:addressing` §3 bounds, the Epic level
     included, and an `EPIC-` folder carries no `brd-link.md`, so without this bullet it fell to the
     third bullet as a source-owning BRD and reached step 8's `BRD_SPLIT_EMPTY_INVENTORY`, whose
     remedy then named a re-run of `/product-workflows:brd-intake` over this same folder — a run that
     refuses it.
     Decide it by the directory prefix, as `workflows-core:addressing` §4.1 places a folder: an
     `EPIC-` prefix, the name beginning `EPIC-<the resolved key>-`, so a legacy folder whose key
     merely begins `EPIC-` is not refused by its name; or, on a folder with no prefix, a resolved
     `kind: epic`, taken after §5.1's container test as §4.1 orders it. Never the asserted `kind:` of
     a prefixed folder.
     `BRD_SPLIT_EPIC_LEVEL: <KEY> resolves to an Epic folder at <path>, and splitting allocates a BRD's coverage ledger — an Epic is refined from the PRD folder above it and holds no coverage ledger, inventory or grounding of its own. No gate was run and nothing was written. <remedy> Re-running this command on this Epic stops here again.`
     `<remedy>` turns on the folder containing this one: where it carries a `brd-link.md` naming a
     `parent:` — a slice — `Run '/product-workflows:brd-split <SLICE-KEY>' against the slice this Epic sits in.`, `<SLICE-KEY>` being that `brd-link.md`'s own `key`, read and never parsed out of either folder's name; anywhere else, `The folder above it is not a slice carved from a customer's BRD, so there is no slice ledger for this command to allocate for this Epic.` — naming no command, since the bullet below refuses an idea-route PRD folder too.
   - **An idea-route PRD folder** → stop, before either mode is set. `split_mode: full` below reads
     "no `brd-link.md`" as a source-owning BRD, and an idea-route PRD folder —
     `/product-workflows:create-prd`'s own output, never carved from a BRD — carries none either.
     Decide it by **positive evidence, exactly as `/product-workflows:prd-ground` Phase 0 step 5a
     sets `route: idea`**: a `PRD-` directory carrying no `brd-link.md` (`/brd-split` is the only
     writer of a `brd-link.md` naming a `parent:` inside a `PRD-` folder, and a root BRD is created
     `BRD-`-prefixed, never `PRD-`); or a folder resolved through `workflows-core:addressing` §5's
     legacy unprefixed fallback carrying no `brd-link.md`, neither `coverage-ledger.md` nor
     `brd/brd-inventory.md`, and a `prd.md` asserting `kind: prd`
     (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.1). The same unprefixed shape
     without such a `prd.md` is not decided here, and falls to the next bullet as it always has —
     which is no claim that it is a BRD: it holds no inventory, so step 8 stops it, and that stop
     names no `/brd-intake` re-run over a folder that is not a container. **Where that folder holds an
     `idea.md` and no `prd.md`** — the folder the idea route handed an idea off into before the kind
     prefixes, which `workflows-core:addressing` §5 resolves on its name alone — the stop also names
     `/product-workflows:create-prd <KEY>`, as `BRD_SPLIT_NOT_A_BRD` does for a `PRD-` folder holding
     no `prd.md` yet: that command accepts the folder (its Phase 0 steps 5a and 5b refuse only a
     container and an Epic folder) and writes the `prd.md` that brings a re-run to this bullet.
     `BRD_SPLIT_NOT_A_BRD: <KEY> resolves to an idea-route PRD folder (<path> carries no brd-link.md), not a BRD or a slice carved from one — no gate was run and nothing was written. Splitting allocates a customer BRD's coverage ledger to slices, and this folder has no coverage ledger and no requirement inventory to allocate. The idea route goes on from its PRD: run '/product-workflows:create-ard <KEY>' or '/product-workflows:specify <KEY>' (after '/product-workflows:create-prd <KEY>' where the folder holds no prd.md yet). If <KEY> was meant to name a BRD, check the key — a BRD with a source document of its own is created by /product-workflows:brd-intake <BRD-KEY> @<brd-file>. Re-running this command on this folder stops here again.`
   - **No `brd-link.md`, or one with no `parent:`** → this BRD owns its source document. Set
     `split_mode: full`; carry it for the whole run. Nothing is announced — this is the ordinary
     case.
   - **`parent: <PARENT-KEY>` present** → this is a slice. Set `split_mode: allocate-only`, carry
     it for the whole run, and **emit this notice now, and again in the final report** — a run that
     silently skips two phases and drops a resolution from its own picker is worse than one that
     says so:
     `BRD_SPLIT_ON_SLICE (notice, not a stop): <BRD-KEY> is a slice of <PARENT-KEY>. This run allocates <BRD-KEY>'s ledger but creates no children: nesting is capped at one level, so Phases 2-3 are skipped and no child BRD can exist below a slice. The Phase 4 walk offers its own four resolutions — the same count as full mode, a different set: covered-by is not one this walk can choose — on a slice it names a sibling or the parent, records a claim the parent's own walk withdrew — still provisional on the ordinary route, committed by an earlier run and then deferred by this slice itself where a re-cut moved it — and is written by that walk, so every row carrying it is already terminal here.`
   **This is a cap on nesting, not on allocation.** A grandchild would inherit `brd/source/` and a
   requirement defect log from a parent that holds neither, so its inventory header would name a
   path that does not exist (`workflows-core:addressing` §6,
   `${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1) — that
   is what child creation is refused for. A slice's own ledger has no such problem: its rows are
   this BRD's to allocate, and refusing to walk them would leave every one of them `unallocated`
   forever, which is the allocation deadlock this command exists to prevent
   (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §1, §4). The one inheritance the
   walk itself needs — the defect log a `rejected: [DEF#n]` cites — resolves in the parent's log in
   `allocate-only` mode, and that lookup is exactly one hop because the cap makes a slice's parent
   always the source-owning root (`brd-format.md` §4). Phase 4 states it where it is used.
6. **Gate the grounding deliverable on main.** **This step and step 7 run in `split_mode: allocate-only` only.** A root BRD is never ground — grounding happens at a `PRD-` folder (on this route a slice), and the customer interview at the slice and nowhere else — so on a `full` run there is no grounding to gate and both steps are skipped entirely. There is no `coverage-ledger.md` gate to keep: step 8 reads that ledger in both modes with a plain worktree read, never a `require-on-main` gate, which is why `workflows-core:phase-handoff` §4.0 classes it — and `brd/brd-inventory.md` beside it — **advisory** at a root. `/brd-split` **consumes** a `$SPECS_PATH`
   deliverable it did not write (`/prd-ground`'s findings, and — transitively — `/brd-intake`'s
   ledger), so per `workflows-core:phase-handoff` §5 rule 2 it executes `require-on-main` (§3) here in Phase 0,
   before anything else reads a file. Execute it against the resolved BRD folder's
   `grounding/code-grounding.md` — every deliverable a `handoff-to-main` run stages lands in one
   commit (§2.3), so this file's presence on `origin/<default>` implies `grounding/design-grounding.md`
   and `brd-link.md` merged with it; **That implication holds for a full `/prd-ground` run and not for a `--no-code` one**, whose `deliverable_paths` is `grounding/design-grounding.md` alone and lands in its own later commit — so a BRD can legitimately have `code-grounding.md` merged and `design-grounding.md` on no ref at all. Anything reading the design findings gates them separately rather than inheriting this sentence. and since `/prd-ground` Phase 0 step 6 already required
   `coverage-ledger.md` on `origin/<default>` before grounding itself would run, it also implies
   `/brd-intake`'s ledger was on main before this BRD was ever grounded. Map the §3.7 return by
   `stopped` first: any stopping row → stop, naming the concrete branch/PR state it reports;
   `pass` → proceed; `pass_amending` → proceed, printing the §3.3 row-B message; `absent` (row F —
   grounding findings are on no ref at all) → **split it before stopping, on a test row F cannot
   make**, the way `/brd-reconcile` splits its own row F. Row F covers three states here, and in
   the last two `/prd-ground` would stop rather than produce the findings this gate wants, so
   neither message may name it as the fix. Read
   `<BRD-dir>/brd/brd-inventory.md` from the worktree and count its `[BR#n]` rows:
   - **One or more rows** — grounding simply has not run yet, and running it is the fix:
     `BRD_SPLIT_NEEDS_GROUNDING: no grounding findings on file for <BRD-KEY> — run /product-workflows:prd-ground <BRD-KEY> first.`
   - **No `brd/brd-inventory.md` in the folder at all** — not an empty inventory, and not a slice
     that claims nothing. Two causes leave claims with no inventory beside them, and the remedy below
     tells them apart: a `/brd-split` run on the parent interrupted after it wrote this slice's
     `brd-link.md`, so the file was never written, or a file lost after it was written. `/prd-ground` stops on it with
     `PRD_GROUND_NO_INVENTORY`, so name that stop's remedy rather than the command:
     `BRD_SPLIT_NO_INVENTORY (split_mode: allocate-only): <BRD-KEY> is a slice of <PARENT-KEY> and has no brd/brd-inventory.md, so there is no claim list to ground or to allocate. <remedy>`
     — `<remedy>` taken from the table `/product-workflows:prd-ground` Phase 0 step 6 gives its own
     `PRD_GROUND_NO_INVENTORY` on a slice, read the same way and never restated here: it branches on
     this slice's `claims:` and on `<PARENT-KEY>`'s own ledger, and its first row, for a slice whose
     `claims:` names nothing, is the remedy of the stop below.
   - **The inventory present with zero rows** — there is nothing to ground, so `/prd-ground` stops with
     `PRD_GROUND_EMPTY_INVENTORY` rather than producing the findings this gate wants. Naming it here
     would be the loop, so name the upstream fix instead — this step now runs only in
     `split_mode: allocate-only`, so the fix is always the parent.
     Where `<PARENT-KEY>`'s own `coverage-ledger.md` cannot be read, the stop names neither `/brd-split` form: replace its text from `Re-run /product-workflows:brd-split on <PARENT-KEY>` to the end exactly as `/product-workflows:prd-ground` Phase 0 step 8 replaces its own copy's, since which form runs is that ledger's to say.
     Otherwise:
     `BRD_SPLIT_EMPTY_INVENTORY (split_mode: allocate-only): <BRD-KEY> is a slice of <PARENT-KEY> and its inventory holds no [BR#n] row — it claims nothing, so there is nothing to ground and nothing to allocate. Do not run /product-workflows:prd-ground, and do not run /product-workflows:brd-intake on a slice; it has no source document of its own. Re-run /product-workflows:brd-split on <PARENT-KEY>: either way it resolves every standing empty child, so it will offer to remove this slice or to keep it against its recorded reason. Which form to type depends on that parent's own ledger. Where it still holds an unallocated row, the run walks it too and will offer covered-by against this slice — and a run with rows still to place needs a slicing instruction to group them, so type '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"'. Where no row is left unallocated, the bare '/product-workflows:brd-split <PARENT-KEY>' is the run, and removing this slice or keeping it against a recorded reason is the whole of what it offers here. Adding an instruction to that same run, '/product-workflows:brd-split <PARENT-KEY> "<what to peel off>"', can additionally re-cut onto this slice a row the parent delegated to a sibling that has since recorded it will not build it — the one case, apart from the key repair a removal performs, in which /brd-split re-allocates a row already carrying a fate, and the only third thing that can change this slice's state. That third one is not guaranteed to be on offer: it needs such a row to exist, and it needs this slice never to have been interviewed, so a slice emptied after its own interview can only be removed or kept.`
   `unmanaged` → proceed as before this feature.
7. **Gate on verification — and on there being grounding to verify.** **This step and step 6 run in `split_mode: allocate-only` only.** A root BRD is never ground — grounding happens at a `PRD-` folder (on this route a slice), and the customer interview at the slice and nowhere else — so on a `full` run there is no grounding to gate and both steps are skipped entirely. There is no `coverage-ledger.md` gate to keep: step 8 reads that ledger in both modes with a plain worktree read, never a `require-on-main` gate, which is why `workflows-core:phase-handoff` §4.0 classes it — and `brd/brd-inventory.md` beside it — **advisory** at a root. Four tests, in this order.
   **The order is the fix to a shipped defect and is not incidental:** the third is a *count*, and a
   count is vacuously satisfied by an empty set. This gate shipped as that count alone, so a BRD with
   two indexed frame sets and no design grounding at all passed it — zero findings on file means
   zero findings missing an outcome — and its slices could reach build with their designs never
   reconciled. A count tests a property of the records that exist; what was wrong was the records
   that did not. Tests **a** and **b** are presence relations, and each fails when its own side
   comes up empty rather than passing.

   a. **There is code grounding.** Read `<BRD-dir>/grounding/code-grounding.md` from the worktree —
      step 6 already proved it is on `origin/<default>` — and count its `[CG#n]` blocks, parsed per
      `workflows-core:grounding-format` §2.1. Zero → stop. Step 6's row-F branch catches the file
      being on no ref; nothing until now caught it being on main and holding nothing, which is the
      same state one commit later:
      `BRD_SPLIT_NO_FINDINGS: <BRD-KEY>'s grounding/code-grounding.md is on main but records no [CG#n] finding — re-run '/product-workflows:prd-ground <BRD-KEY>' and merge its handoff before splitting.`

   b. **Design grounding covers every frame set on disk, and is on main.** List every immediate
      subdirectory of `<BRD-dir>/design/` in the worktree — the reserved location
      (`workflows-core:grounding-format` §6.1). **None, or no `design/` folder → this test is
      satisfied**, and says so in the final report rather than passing silently. **That emptiness is
      the whole of the condition**: a BRD with no exported frame set has no design grounding to
      require, which is what keeps this test inside `workflows-core:phase-handoff` §5 rule 3 (a gate
      may not promote an optional input into a prerequisite) — see §3.4's conditional `/brd-split`
      row, which declares the promotion for the case where frame sets do exist.

      One or more subdirectories → **execute `require-on-main`** (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3)
      against `<BRD-dir>/grounding/design-grounding.md` before reading it. **Step 6's implication
      does not reach this file and must not be borrowed for it.** Step 6 gates `code-grounding.md`
      and infers its siblings from "every deliverable a `handoff-to-main` run stages lands in one
      commit" — true of a full `/prd-ground` run and **false of a `--no-code` one**, whose
      `deliverable_paths` is `design-grounding.md` alone, handed off in its own later commit. Without
      this gate the repair this very test recommends would produce the state the test exists to
      catch: an operator runs `--no-code`, declines the handoff, and the split reads their working
      copy and passes. Map the §3.7 return by `stopped` first: any stopping row → stop, naming the
      branch/PR state; `pass` → proceed; `pass_amending` → proceed, printing the §3.3 row-B message;
      `unmanaged` → proceed; `absent` (row F) → stop with the message below.

      Then read that merged file's `## Frame sets covered` section (`/prd-ground` Phase 8 writes one
      entry per subdirectory on disk, covered or not) and resolve each subdirectory against it:
      - **The file is absent, or `require-on-main` returned row F** → stop. Designs on disk, and
        nothing reconciling them on main.
      - **The file is present and carries no `## Frame sets covered` section at all** → this BRD was
        ground **before that section existed**, not left unground. Do not stop: if the file records
        at least one `[DG#n]`, or a note saying design grounding was skipped and why, pass — and
        record in the final report that per-set coverage could not be checked for this BRD, naming
        why. If it records neither, stop with the message below. Stopping every BRD ground before
        this release would send each of them into a `--no-code` re-run that re-derives design
        grounding they already hold.
      - **The section is present and records no set, while `design/` holds one** → stop with the same
        message, naming the parse. An empty relation fails rather than passes
        (`workflows-core:grounding-format` §2.1) — a read that learned nothing is not a clean tree.
      - **A subdirectory is absent from the recorded set, or recorded `skipped: no index`** → stop,
        naming each such set. The second is a set `/prd-ground` could not reconcile, which is
        unreconciled by a different route to the same place.
      - **Recorded `ground`, or `skipped: --no-design`** → passes. The second is an operator decision
        taken per run, not an inability, so it is honoured — but it is carried into the final report
        and into `slices.md` as a recorded limit on what this split was able to check, because it is
        the one way a slice can still reach build with a frame set **known** to be unreconciled —
        the pre-section pass above can let one through too, but unknown, which is why that pass is
        recorded as unchecked rather than as a limit.

      `BRD_SPLIT_DESIGN_NOT_GROUND: <BRD-KEY> has frame sets on disk that no design grounding on main covers (<names>) — re-run '/product-workflows:prd-ground <BRD-KEY> --no-code' to ground them without re-deriving the code findings already on file, and accept its handoff. Where a set is listed as having no index, run '/workflows-core:frames <BRD-KEY>' first, which writes the index that lets the set be reconciled at all.`

   c. **Every finding carries a verifier outcome.** Every `[CG#n]`/`[DG#n]` finding carries one (of
   the four in `workflows-core:grounding-format` §8 — `agree`, `extend`,
   `contradict`, `unprovable`) once `/prd-ground` Phase 7 has run over it; a finding without one
   "is not evidence and cannot be recorded as `consumed_by` anything" (§8), and this command must
   never propose a slice or offer `covered-here` against a claim nobody has actually verified.
   Count every finding on file carrying no recorded `outcome`. Any count `N` greater than zero →
   stop: `BRD_SPLIT_UNVERIFIED: N findings have no verifier verdict — run /product-workflows:prd-ground first.`

   d. **No finding block carries a field the record's format does not define.** Parse every
   `[CG#n]`/`[DG#n]` block per `workflows-core:grounding-format` §2.1 and test each key against that
   section's **closed** field set — §2's fields, plus `outcome` and `notes`. Any other key fails. The
   test is derived from that section, never from a list here, which is what admits a field §2 gains —
   `control` (§2.2) is one — without this gate being touched. **The keys that actually occur are the
   verifier's own return fields**, and `own_verdict` above all: transcribed into the record it leaves
   the block stating two verdicts at once while `verdict` is the one this command and every other
   consumer reads. `control_outcome` is the same mistake with a different consequence — it is one
   verifier's judgement about whether that finding's control fired, so a block carrying it asserts as
   a property of the finding something only a re-derivation establishes. **Test c. cannot see it**: such a block carries an
   `outcome`, so it passes on presence and the disagreement travels into a slice's allocation
   unexamined — which is why this is a relation of its own rather than a stricter count, the same
   shape as the design-presence test above. Name every offending finding and key, and name the
   repair as the hand edit it is:
   stop: `BRD_SPLIT_MALFORMED_FINDING: N finding blocks carry a key workflows-core:grounding-format §2.1 does not define (<finding-id>: <key>, …) — the record's field set is closed to §2's fields plus outcome and notes. A block carrying own_verdict beside verdict states two verdicts at once, and nothing downstream can tell which one is the finding's. Remove the offending key from each block by hand in <path>, leaving every other key untouched, and re-run. Do not re-run '/product-workflows:prd-ground <BRD-KEY> --rebaseline' for this: it re-grounds every claim against current commits to delete a line no command should have written, and supersedes the verified corpus in the process.`
8. **Read the ledger; check for the no-op case.** **On a `full` run, first check the inventory
   itself is non-empty** — step 6 no longer reaches a root, so this is where a root whose intake
   produced zero `[BR#n]` rows is caught. Read `<BRD-dir>/brd/brd-inventory.md` and count its
   `[BR#n]` rows — a missing file counting as zero; zero → stop, in one of two forms, chosen by
   whether the folder is a container as `workflows-core:addressing` §4.1 places one: a `BRD-`
   prefix, or no prefix and a `coverage-ledger.md` or `brd/brd-inventory.md` beside no
   `brd-link.md` naming a `parent:`. **Only a container is one `/brd-intake` re-runs over** (its
   Phase 0 step 7); any other folder it refuses with `BRD_INTAKE_NOT_A_BRD`, so the second form
   names a new key instead. A container:
   `BRD_SPLIT_EMPTY_INVENTORY (split_mode: full): <BRD-KEY>'s inventory holds no [BR#n] row, so there is nothing to ground and nothing to allocate — do not run /product-workflows:prd-ground, which refuses a root outright. Re-run '/product-workflows:brd-intake <BRD-KEY> @<brd-file>' over this same folder with a source whose requirements brd-reader can identify, and merge that pull request; if the source genuinely states no requirement, this BRD has nothing for the route to carry.`
   Any other folder — an unprefixed one carrying neither BRD file, the shape the idea-route bullet
   in step 5 leaves undecided, or a `PRD-` folder whose `brd-link.md` names no `parent:`, which no
   command writes — `<what it carries>` being its top-level files and subdirectories, as read:
   `BRD_SPLIT_EMPTY_INVENTORY (split_mode: full): <BRD-KEY> resolves to <path>, which carries <what it carries> and no [BR#n] row in any brd/brd-inventory.md — it is not a BRD container, so there is nothing to allocate, and /product-workflows:brd-intake would refuse to re-run over it. Nothing was written. Do not run /product-workflows:prd-ground, which refuses this folder too. To intake a customer's BRD, run '/product-workflows:brd-intake <NEW-KEY> @<brd-file>' with a key no folder under $SPECS_PATH/specifications/ asserts; this folder is left exactly as it stands.<where the folder holds an idea.md and no prd.md, append:> It holds an idea.md and no prd.md, so the idea route goes on from it: run '/product-workflows:create-prd <BRD-KEY>', merge its handoff, then '/product-workflows:create-ard <BRD-KEY>' or '/product-workflows:specify <BRD-KEY>'.`
   **On a slice this check is not made, and nothing here stops an empty inventory.** Step 6's row-F
   branch stops a slice whose inventory is absent or holds no row only where its grounding is on no
   ref. A slice whose grounding is on main while its inventory holds no row — the parent's walk
   having withdrawn every claim after the slice was ground — passes steps 6 and 7 and reaches this
   step, which reads its ledger exactly as on any other slice: each withdrawn claim left an orphan
   row there (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2), which is never left
   `unallocated`, so no row of that kind counts below and step 10 decides the run on the ledger as it
   does on every slice. Read `<BRD-dir>/coverage-ledger.md` and compute
   its disposition counts (`coverage-ledger-format.md` §3) — **this BRD's own rows, as written, with
   no child ledger consulted for this count.** The no-op test and the §4 gate are both about `unallocated` on
   *this* ledger; what a child did with a row this BRD already delegated cannot make that row
   `unallocated` again. **That bounds the count, not the phase, and the two sentences that used to make it bound the phase are retracted rather than qualified**: this step once said that the remedy for a child that is not building a row lives in that child's own walk and not here, and that child ledgers are read once, in the Final Report, only to count the line (`coverage-ledger-format.md` §6.1). Neither holds. **Step 9a reads every child's `coverage-ledger.md` in this same phase**, and where a child's own row records `deferred-to: <itself>` against a row this BRD delegated to it, the remedy is precisely here — a sibling may take it (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). What survives is the narrow rule this step needs: no child ledger changes the number counted **here**. **Zero rows are `unallocated`** → set `unallocated_zero: true`.

   **That is one part of the no-op test and not the whole of it, and the first missing part was a dead end.** A run is a no-op only
   when there is nothing left for *any* phase to do, and Phase 4.5 has work of its own that the
   ledger cannot see: a child left standing while claiming nothing. Deciding the no-op on the ledger
   alone made that child unreachable — the ledger of a parent whose walk completed has zero
   `unallocated` rows **by construction**, so every later run no-op'd, Phase 4.5 never ran, and the
   only command that can remove an empty child never offered to. Stops and offers elsewhere on this
   route name this command as the fix for exactly that child, so the no-op has to account for it. The
   other parts need step 9's enumeration and step 9a's candidate set, so **the no-op decision is
   taken in step 10**, never here.

   **A re-cuttable row is the other thing this count cannot see, and it is a second reason a fully-allocated ledger does not settle the question.** A row this BRD delegated to a child that has since recorded, in its own ledger, that it will not build it reads `covered-by: <A>` here and `deferred-to: <A>` there — two terminal dispositions, so the count is zero, and yet nobody is building the requirement (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). Step 9a builds that set and step 10 tests it before the no-op, so a run that can move such a row — one carrying the `<instruction>` step 9a requires — is reached instead of being swallowed by the no-op it would otherwise look identical to. A bare `/product-workflows:brd-split <PARENT-KEY>` builds no candidate set, so a re-cuttable row alone never keeps a bare run from the no-op.

   **A child out of step with this ledger is the third thing this count cannot see.** A carve stopped between its Phase 3, which writes each child's three files provisionally, and its Phase 4 Step 3, which reconciles them against this ledger, can leave every row here terminal while a child's `claims:`, its inventory and the rows here reading `covered-by: <that child>` disagree — a provisional claim the next run's walk settled elsewhere, or a row a walk gave the child that its inventory never received. `/product-workflows:prd-ground` refuses such a child (`PRD_GROUND_SLICE_UNRECONCILED`) and names a bare run of this command as the fix, so the no-op has to account for it too: step 9 tests every child it enumerates, and step 10 takes the reconcile path wherever a child is out of step.

   **Step 10 and not step 9, because step 9 does not run in every mode.** Step 9 is `full` only, so
   a decision taken inside it is never taken at all on a fully-allocated slice — the run would fall
   through into Phase 5 and open a pull request for a run that changed nothing, and this command's
   own Phase 7 promises a slice the opposite. Step 10 runs in both modes, which is what keeps the
   no-op **mode-independent**: it is decided by the ledger and the tree, not by the level, so a
   fully-allocated slice reaches it exactly as a fully-allocated parent does. `allocate-only` simply
   satisfies **both of the other two parts** by construction — no child exists or can be created below a slice, so none can be left standing; and step 9a is `full` only, so a slice's re-cut candidate set is empty and the re-cut path is unreachable there — and
   it had two fewer phases to skip. The step 5 notice is still emitted and still reported.
9. **Enumerate existing children — `split_mode: full` only.** In `allocate-only` mode there are no
   children and none can be created, so this step is skipped — and with no child to enumerate there
   is no `covered-by` target for Phase 4 to offer, which is the mechanical reason that picker's four
   choices are a different four from the parent's, with `covered-here` where `covered-by` stands. A slice's own `covered-by` rows name a sibling or the parent and
   are written by the parent's run — its walk, or Phase 4.5's removal repair — never chosen here
   (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3); this step never looks for
   them and never needs to, because they are terminal already. In `full` mode: list every immediate subdirectory of `<BRD-dir>` that
   **contains a `brd-link.md` carrying a `parent:` field naming this BRD**. Each match is a child a
   previous `/brd-split` run already created, nested per `workflows-core:addressing` §6, and remains a valid
   `covered-by` target in Phase 4 even when this run proposes no new slice of its own — save one this
   step marks **unreconcilable** below, which no target list of this run offers.

   **A positive test, not a name match.** Matching a subdirectory by name and then reading an
   absent `brd-link.md` as an empty `claims:` list is what let a folder that is not a child be
   counted as one: it reads as a standing empty child, Phase 4.5 offers to **remove** it, and
   `epic.md`, `specification.md` and `design.md` go with the folder. Requiring the file to exist and
   to name this BRD makes the inference impossible rather than merely unlikely. It also needs no
   exclusion list — `brd/`, `grounding/` and `dev-workflows/` carry no `brd-link.md`, so the test
   excludes them by construction rather than by an enumeration that a new sibling directory would
   silently fall out of. **Read each one's `brd-link.md`
   `claims:` list**, and mark every match whose list is empty as a **standing empty child**, noting
   whether it carries a `reason:` field — Phase 4.5 resolves exactly this set, and it is the set the
   no-op test in step 10 needs. **Then test each match against this BRD's ledger — the reconciliation
   test.** Read three sets of `[BR#n]` ids, each off a structured field and never out of prose: the
   child's `brd-link.md` `claims:`, read id by id as `${CLAUDE_PLUGIN_ROOT}/references/brd-format.md`
   §2.1 fixes; the `id` of every row of its `brd/brd-inventory.md`; and the `id` of every row of this
   BRD's own `coverage-ledger.md` whose `disposition` reads exactly `covered-by: <that child's key>` —
   the whole value, never a prefix of it, so a sibling whose key merely begins with this one's is not
   counted. Mark every match where the three are not all equal as **out of step**, noting each id by
   the set that lacks it. A match whose `brd/brd-inventory.md` or `coverage-ledger.md` is missing or
   cannot be read is marked **unreconcilable** instead, and reported in the Final Report whatever
   path the run takes: Phase 4's Step 3 leaves such a child untouched, and says why. This is the
   test `/product-workflows:prd-ground` step 6a runs, and a completed run of this command leaves it
   passing for every child it leaves standing with both files. **An unreconcilable child is never a
   target, nor a donor**: every list this run offers a row from or to leaves it out — Phase 4's
   Step 1 bulk set and its firing count, Step 2's *Assign to a named slice*, Phase 2's *allocate to
   the existing children* answer, and step 9a's donor and receiver sets — and names it beside that
   list with the file it is missing or cannot read, as Step 2 names a child it bars for an orphan row. A row moved
   to or from it would need that child's files reconciled, which Step 3 will not do: the run would
   write `covered-by: <that child>` onto this ledger and a `claims:` entry into a slice that can
   never hold the row, and a slice left that way has no stop on this route whose remedy works. **Carry the marked sets — standing empty, out of step
   and unreconcilable — forward even when they are empty** — step 10 reads them in both modes, and in
   `allocate-only`, where this step never ran, each is empty by construction because no child exists
   or can be created below a slice.
9a. **Build the re-cut candidate set — `split_mode: full`, an instruction, and a fully-allocated ledger.** This step runs only where **all three** hold: `split_mode: full`, step 1a parsed an `<instruction>`, and step 8 set `unallocated_zero: true`. On any other run it does not run at all and the **re-cut candidate set** is empty. Step 10 tests that set first and sets `recut_mode: true` where it is non-empty. **The third condition is what keeps one argument from meaning two things in one run.** Where any row is still `unallocated` the instruction already means *group those rows*, and Phase 1.5 spends it against them; reading the same sentence a second time as *peel this off a sibling* would put two interpretations of one string into one run with nothing to choose between them. A parent whose ledger is fully allocated is the only run on which that sentence is otherwise free, which is why the re-cut needs no flag of its own and takes none.

   **What a candidate is** (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2, the authority for every rule this step executes rather than restates). A row is re-cuttable only where two ledgers already agree that nobody is building it: this BRD's row for a `[BR#n]` reads `covered-by: <A>`, and A's own row for that same `[BR#n]` reads `deferred-to: <A>`. For each child enumerated in step 9, in the worktree:
   - Read that child's `coverage-ledger.md` and take every row whose `disposition` is `deferred-to: <that child's key>`.
   - Take this BRD's own rows whose `disposition` is `covered-by: <that child's key>`.
   - **Intersect the two by `[BR#n]`.** Each `[BR#n]` in the intersection joins the re-cut candidate set as `{ [BR#n], donor key, the donor's ledger row }` — the donor being the child whose two rows made the pair.

   **Read the `disposition` column at both levels — never `claims:`, and never either inventory.** §3.1 names that trap from the other side, for the interview's scope test, and it is the same trap here: a child still `claims:` a row it has deferred, and a source-owning BRD's inventory holds every `[BR#n]` whatever its fate, so either would put rows in the candidate set that neither ledger says are movable.

   **A child whose `coverage-ledger.md` cannot be read is not a donor, and that is reported rather than skipped silently.** An unreadable ledger is `unresolved`, never `covered` (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §6.2). Name the child and the read failure here and again in the final report; never infer an empty `deferred-to` set from a read that failed. **Nor is any other child step 9 marked unreconcilable** — one whose ledger reads but whose `brd/brd-inventory.md` is missing or unreadable: a donor's `claims:` entry and inventory row are withdrawn by Step 3, which writes nothing into that child, so re-pointing its row would leave it claiming a `[BR#n]` its own ledger gives to somebody else. Name it, and the file it is missing or cannot read, beside the other.

   **Then compute the eligible receiver set**, executing §3.2's **two-part** receiver test rather than restating it. A child from step 9 is **ineligible** where its folder holds a `decisions.md` carrying at least one `[VD#n]` or `[CD#n]` record that is not a torn write (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §8), **or** where any `interview/round-*.md` exists in it, **or** where step 9 marked it unreconcilable — Step 3 writes nothing into such a child, so the receiver's `claims:` entry, inventory row and `unallocated` ledger row would never be written, and its missing file is named in the report below. Every other child is eligible, and so is every child Phase 3 keys on this run, which has none of the three by construction. **The rest of §3.2's test is per row and therefore travels as a clause on this set, never as a membership rule, and there are two such clauses — the first is that a row's own donor is never among that row's receivers.** §3.2's receiver is *a sibling under the same parent — never a child of A, and never A itself*; the first of those is satisfied by construction, since the one-level nesting cap means no child of A can exist (`workflows-core:addressing` §6), and the second cannot be taken out of the set, because the set is shared by every candidate row while the donor differs per row. **This is the ordinary case, not an edge.** A slice defers rows in its own `allocate-only` walk, which runs **before** `/brd-interview`, so an uninterviewed A holding `deferred-to: <A>` is exactly the state the re-cut exists for; A therefore passes the interview half, and a walk handed the set without this clause could propose re-pointing a row from A onto A — leaving this BRD's row unchanged and writing A's own row `covered-by: <A>`, a self-naming `covered-by` §3's orphan table has no row for. **Read the worktree, not a ref** — an interview that happened is an interview that happened whether or not its record has merged, and a receiver cleared against a ref that has not caught up is one whose customer conversation has already started. **Being interviewed disqualifies a receiver, never a donor**: A holding a `[VD#n]` about deferring the row is the ordinary case, and that decision records A's refusal to build it, which the re-cut leaves standing.

   **A second per-row clause sits beside that one, and it is what keeps a receiver's seeded row a new row: a child already holding a ledger row for that `[BR#n]` is not a receiver for that row** (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). It is per row for the same reason the donor clause is — the set is shared by every candidate while the row differs — and it is not a membership rule: such a child stays a perfectly good receiver for a different `[BR#n]` it holds no row for, and is named as excluded per row rather than struck from the set. **The reason is the invariant the whole re-cut rests on.** A receiver's row for the moved `[BR#n]` reads `unallocated` because it is a **new** row born in the initial state (Phase 3 step 3, Phase 4 Step 3), and where a row for that id already exists there is no new row to be born: writing `unallocated` onto the row it has would return a terminal row to the initial state, which no command may ever do (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3), and leaving that row as it stands strands the requirement — the child would `claims:` a `[BR#n]` whose own ledger row names somebody else, and its `allocate-only` walk visits only `unallocated` rows, so that row could never reach `covered-here`. Every §4 gate in the tree would read satisfied with nobody building the requirement, which is `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §1's own named failure arriving inside the mechanism built to prevent it, and it falsifies two of that file's guarantees outright — §5's *`claims:` names none of them* over a slice's `covered-by` rows, and §6.1's classification of such a row as malformed and permanently `unresolved`. **The state is ordinary, which is why this is a clause and not a remark**: a child B whose provisional claim on that same `[BR#n]` an earlier run's walk withdrew holds exactly one orphan row for it (Phase 4 Step 3's table) and stays standing on its other claims, so a later re-cut of that `[BR#n]` off its donor would name B as the natural receiver — the child the operator wanted it in first. **Say where the requirement goes instead, rather than leaving the operator with nowhere.** Two routes already work and neither needs anything new: where B is standing empty, Phase 4.5's removal repair is the exit — removing B re-points every row naming it, this BRD's own and every other child's, onto this BRD, so the requirement returns to this BRD as its own live obligation instead of sitting behind a key nobody builds; and where the requirement is to be built now, the receiver is a **new sibling** Phase 3 keys on this run, which holds no ledger row for anything and is therefore eligible for every candidate by construction. That second one is the answer Phase 2 already owes an operator whose preferred target is missing from the target list.

   **Report both sets before anything else runs**: how many rows are re-cuttable and from which donors, which children are eligible receivers, **which of those the two per-row clauses exclude for which candidate row and on which clause** — a target list that is silently short for one row and not for another reads as a bug in the enumeration — and — where the candidate set is empty while children exist — **which of the two reasons made it empty**, no child holding a `deferred-to` row of its own, or every such row being one this BRD did not delegate to that child. An operator who typed an instruction on a fully-allocated parent and got a no-op needs to see which it was: "nothing to re-cut" without the reason is indistinguishable from an instruction the command failed to parse.

   **No stop is taken here, and no no-receiver stop exists anywhere in this command.** A non-empty candidate set with no eligible child standing is not a stop: Phase 3 can key a new slice, and a slice this run creates is eligible by construction. The state that would be a stop — a non-empty candidate set, no eligible child, **and** a parent that cannot take a new one — is unreachable, because a parent can always take a new child. What *is* reachable is a run left with nothing to offer: every target it proposed declined, and no eligible child standing. **That is an operator decision, not an error, and this route already refuses to call one a failure.** An operator who read a proposal naming each row's donor and declined it has answered the question the run asked; `/brd-interview` says as much of its own version of this state — `BRD_INTERVIEW_ALL_DELEGATED` is "a finished state, not a missing step". So nothing stops: Phase 2 states the outcome instead — every candidate is left with its donor and reported — and Phase 4's Step 2R has nothing to offer for any of them. A reader looking for a no-receiver stop should stop looking; there is none to find.
10. **Take the no-op decision — both modes, always.** This step runs whether or not step 9 did, which
    is the whole reason it is its own step: the decision must be reached on a slice exactly as on a
    parent. **The branches below are tested in the order they are written, and the first that matches is the run's path** — the re-cut is tested before the no-op because a fully-allocated ledger satisfies the front of both conditions and only one of them is the run the operator asked for.
    - `unallocated_zero` (step 8) **and** the re-cut candidate set from step 9a is non-empty → **the re-cut run**. Set `recut_mode: true` and carry it for the whole run. **Every later phase that behaves differently on this path says so where it does, and not all of them name the flag** — read each phase for what it does rather than expecting a flag test in it. **The partition is by whether the phase names the flag, and it is exhaustive.** Phase 1.5, Phase 2, Phase 4's Step 1 and Step 2R, Phase 5, Phase 6's `body_facts` and the Final Report test `recut_mode` **by name**. Phase 3 step 3, Phase 4's Step 3, Phase 6's `deliverable_paths` clause, Phase 7 and Phase 8's `key events` branch on *the re-cut path* **in prose**, over this same condition and naming no flag. Phase 4.5 names the flag only to say its recomputation is deliberately **not** conditional on it, running identically on every path (Phase 4.5). Nothing outside those three groups behaves differently. Phase 1.5 runs over the candidate set rather than over an empty unallocated set, Phase 2 proposes from that placement, Phase 3 keys what it confirms, Phase 4 runs its Step 2R re-cut walk in place of Step 2 **and widens Step 3's input set to reach the rows Step 2R moved** — a re-cut row was never `unallocated` when step 8 read the ledger, and Step 3's withdrawal of the donor's `claims:` entry and inherited inventory row is what makes that row an orphan row (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2); left unwidened, that reference's §5 eligibility argument, §6.1 roll-up and §6.4 are each false on this path. **Phases 4.5, 5, 6 and 7 are none of them skipped on this path** — which it shares with an ordinary run and with the reconcile path below, and the reason to say so is that the no-op below skips Phases 4.5 and 5, and the reconcile path skips Phases 2 and 3 and Phase 4's walks, all of which this path runs. Three of the four also do extra work here, per the partition above: Phase 5 writes the re-cut block, Phase 6 carries the re-cut facts and the donor's changed ledger, and Phase 7 reads each offered child's own state to say which of its three grounding cases it is. Phase 4.5 alone takes no branch of its own: its recomputation is what makes a donor emptied by this walk visible to it without one. **This is the path on which an instruction typed against a fully-allocated parent means something** — the one run where the argument this route already made mandatory for carving a root is otherwise free, which is what the re-cut is invoked by instead of a flag. **A standing empty child alongside it changes nothing**: Phase 4.5 runs on this path exactly as it runs on the ordinary one, so a parent holding both a re-cuttable row and an empty child resolves both in the same run rather than taking the reconcile path below — and a child out of step alongside it is reconciled by this path's own Step 3, which reaches every standing child.
    - `unallocated_zero` (step 8) **and** no standing empty child **and** no child out of step
      (step 9 — each set empty by construction in `allocate-only`), the branch above having not
      fired → this run is a **no-op** (§4): nothing in Phases 2–5 and nothing in Phase 4.5
      has anything left to do, so skip straight to Phase 6 (Handoff), which will report nothing to
      commit, and the Final Report's ledger line. **A slicing instruction makes this run not-a-no-op exactly where step 9a found a re-cuttable row, and nowhere else**: where it found none the run is still a no-op, and an instruction is still not a reason to walk a row that already carries a fate. Phase 1.5 skips on an empty unallocated set and an empty candidate set alike and reports the instruction unused, naming this path — and **on a `full` run only**, adding from step 9a's report why nothing was re-cuttable. On a slice there is no such report and none is owed: step 9a is `full` only, so the re-cut is unreachable in `allocate-only` by construction and there is no reason to give. This is the path a fully-allocated slice takes, and
      the one Phase 7 tells a slice to expect.
    - `unallocated_zero` **but at least one standing empty child or at least one child out of step**
      (`full` only — a slice can have neither) → **the reconcile path, not a no-op**: skip Phases 2
      and 3 and Phase 4's Steps 1, 2 and 2R, which have no row to walk and no slice to propose; run
      Phase 4's **Step 3** over every standing child, then **Phase 4.5**, then Phase 5 and Phase 6 as
      usual. **Step 3 runs first because it can change which children are empty**: a child out of
      step may regain a claim this ledger already gives it — the receiver of a re-cut cancelled
      before its Step 3 ever ran, which Phase 4.5 would otherwise offer to remove with this BRD's own
      row still naming it — or lose its last stale one, and Phase 4.5 reads each list as Step 3 left
      it. This is the one path on which Step 3 and Phase 4.5 run without a walk in front of them, and
      it exists so that a child kept empty by a deliberate decision, and a child a carve left out of
      step by stopping before it reconciled it, are each still reachable by the command every other
      stop on this route names — a bare `/product-workflows:brd-split <BRD-KEY>`.
    - Otherwise → the ordinary run: Phases 2–6 as written, in whichever mode step 5 resolved.
11. **Stop on a missing slicing instruction — `split_mode: full`, and only on the ordinary run.**
    Step 1a parsed the instruction; this is where its absence stops the run, and it is here rather
    than there because only now is it known whether this run proposes anything at all. No instruction
    was given, `split_mode: full`, **and step 10 chose the ordinary run** — at least one row is still
    `unallocated`, so Phase 2 has rows to cluster and no findings to cluster them by → stop:
    `BRD_SPLIT_NEEDS_INSTRUCTION: /brd-split on <BRD-KEY> needs a slicing instruction — a root BRD is never ground, so there are no findings to cluster candidate slices from. Re-run '/product-workflows:brd-split <BRD-KEY> "<how to cut it>"' naming the slice you want carved. On a slice the instruction stays optional: its walk takes recommendations from one but does not need it.`
    On step 10's other **three** paths this stop cannot fire, and for two different reasons. On the no-op path and the reconcile path the ledger has no `unallocated` row, so Phase 2 proposes nothing and
    there is nothing for an instruction to group: the run continues without one. That is what keeps
    the **reconcile path reachable on a bare `/product-workflows:brd-split <BRD-KEY>`**, which it
    has to be — the stops that name this run as the fix for a standing empty child or for a slice out
    of step are asking for a child to be resolved or reconciled, not for a slice to be carved, and Phase 1.5 discards an instruction on a
    run that has neither a row to place nor a re-cuttable one. On the **re-cut path** the stop is unreachable by construction: step 9a runs only where step 1a parsed an instruction, so a run that reached that branch has one, and this step's own condition — no instruction given — can never hold there. In `allocate-only` the instruction is optional on every path and this
    step never fires.

---

## Phase 1 — Classify + model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then record:

```yaml
model_routing:
  classification: MODERATE        # typical; SIGNIFICANT for an unusually large requirement count or slice fan-out
  reason: <one-line>
  current_model: <the model this orchestrator is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.2 cheap chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>   # impl-maintenance only — no other agent runs in this command
  authoring_model: <= current_model>   # Phase 1.5's reading and bounded grill, and Phase 4's walk — session model, not a delegated subagent
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2/§2.1 fallback or degradation>
```

`/brd-split` dispatches no grounding or review agent of its own — every finding it reads was
already independently verified by `/prd-ground`'s `grounding-verifier` pass (`prd-ground.md` Phase 7) — so
`detection_model` here exists only for the terminal `impl-maintenance` dispatch. **The grilling
technique's fetch-a-fact clause does not change that here**, and the reason is what the clause is
bounded to: it fires where a fact needs *more than a read*, and every fact Phase 1.5 needs — a row's
`text`, its `source_anchor`, its disposition — is a local read of files this run already has open.
Nothing in the instruction-reading step reaches for something a sweep would have to find, so no
dispatch arises and the comment above stays literally true. **`authoring_model`
is recorded and is not a dispatch**: Phase 1.5 reads a slicing instruction against this BRD's rows and
may grill the residue, and Phase 4 walks the ledger — all in the session, the same way
`/brd-intake` records its own interactive defect walk. Recording it matters because the reading is a
judgement about the operator's words, so a run that made it on a degraded model should say which
model made it. If no Opus
resolves for `current_model`, degrade to best-available + record in `notes` and the final report —
never hard-block. Under `run_flags.enforced_model` (`workflows-core:model-routing/classification` §10) no degradation is recorded; dispatched steps (`impl-maintenance`, or `defect-reporter` under `--skip-feedback`) use the enforced model, while Phase 1.5's reading and grill and Phase 4's walk still run on `current_model`.

---

## Phase 1.5 — Read the slicing instruction

**Skipped entirely when Phase 0 step 1a found no instruction**, and nothing below fires. **Such a
run no longer reaches Phase 2 the way it once did**: in `split_mode: full` step 11 stops the ordinary
run, so the only instruction-free `full` runs left here are the two on which Phase 2 never runs at
all, and in `allocate-only` there is no Phase 2 to reach. **Runs in both modes**, unlike Phase 2 — a
slice has no children to propose, but its walk takes recommendations from an instruction just as a
parent's does (Phase 4), which is what makes `/product-workflows:brd-split <SLICE-KEY> <instruction>` a
real invocation rather than an ignored one.

**Also skipped where no row is `unallocated` and `recut_mode` is false** — the two conditions are one condition, and the second half is what this phase gained with the re-cut. Whatever Phase 0 step 10 decided, the no-op path and the reconcile path both reach here with nothing to place, since on those two paths this phase places `unallocated` rows and there are none. Report the instruction as **unused, naming which path swallowed it**, rather than running a grill over an empty residue: an instruction typed and then silently discarded is indistinguishable from one the command failed to parse, and on the reconcile path the operator has every reason to expect it did something. Neither path is an error, and neither becomes one for having been given an instruction.

**On the re-cut path (`recut_mode: true`, Phase 0 step 10) this phase runs**, and what it runs over is the **re-cut candidate set** step 9a built, in place of the `unallocated` set — which is empty there by construction, since `recut_mode` is only ever set on a fully-allocated ledger. Nothing else about the phase changes: Step A places what the instruction determines, Step B grills the residue under the same value test and the same cap, and a placement is the one thing produced. **The reason for the report above carries over and binds harder here**: on the two skipping paths the operator supplied an instruction the run had no use for, while on this one the instruction is the argument that *selected* the path — so a candidate this reading leaves unplaced is named in the report rather than passed over quietly, for exactly the reason a discarded instruction is reported at all.

This phase produces one thing: a **placement** — for each `[BR#n]` in the set it runs over, every row still `unallocated`, **or**, on the re-cut path, every row in the re-cut candidate set — either what the instruction puts it in (a **group** in `full` mode, where groups become slices; a **disposition** in `allocate-only`, where there is nothing to group into) or nothing. Everything downstream reads that placement and never re-reads the instruction, so an instruction is interpreted exactly once. **The re-cut path is `full` by construction** — step 9a runs in `full` mode only — so a candidate is placed into a **group** like every other row here, and Phase 2 proposes a **target** for that group: either the new slice it will key in Phase 3, or a named standing child from the eligible receiver set. The operator's confirmation there is what **fixes** the receiver; Phase 4's Step 2R offers the receiver this reading and that confirmation settled, and chooses none of its own. A candidate no confirmed group carries is unplaced, and Phase 4 does not walk it. **"Unplaced" is used in two senses in this phase, and this is the one Phase 4 consumes**: unplaced *after Phase 2's confirmation*, meaning no group with a target carries the row. Steps A and B below use the narrower sense — a row this phase's own reading could not place — which is a residue Phase 2 may still cluster, so a row unplaced there is not yet unplaced here.

### Step A — resolve what the instruction determines, asking nothing

Read each unallocated row's `text` and `source_anchor` from `brd/brd-inventory.md`, each cell
decoded (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.3), and place every row the instruction
plainly determines. **This step raises no prompt of any kind.** It is
`workflows-core:grilling-technique`'s fact-vs-decision split applied before the
grill rather than inside it: a question answerable from the artifact is not a question, and a row
whose text names what the instruction names is placed, not asked about.

**On the re-cut path the same read serves, over the re-cut candidate set**: each candidate's `text` and `source_anchor` come from this BRD's own `brd/brd-inventory.md`, the same file and the same two fields. A BRD that owns its source document holds **every** `[BR#n]` in that inventory whatever fate its own walk gave it, delegated rows included (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.1), so a delegated row is already in the file this step has open and no new read is needed. **Never read the donor's copied inventory for this** — that is the obvious wrong implementation, and it is wrong twice: what it would find is a subset of what is already open, and Phase 4's reconcile is about to withdraw the very row it would be read from.

An instruction that is a **set operation over the ledger** — *everything no child covers*, *the rest*,
*what is left* — resolves entirely here, against `coverage-ledger.md`'s `disposition` column, and
Step B then asks nothing at all. Say so in the report rather than leaving a silent grill looking like a skipped one. **On the re-cut path that resolution runs against the candidate set rather than the unallocated set**, and it is the shape this path most expects: *peel off everything PRD-X deferred* is a set operation over the donors step 9a already named, resolves here in full, and again leaves Step B nothing to ask.

### Step B — grill only the residue, and only where an answer places more than one row

The residue is every row of the set this phase runs over that Step A could not place — every unallocated row on an ordinary run, every candidate on the re-cut path. Put questions to the operator from it one at a time, each with a recommended answer, per that reference's mechanics — which are cited, not restated here. This command's **depth is bounded**, and the bound has two parts:

1. **The value test, which is the real gate: ask only where one answer places more than one row.** A question that disambiguates a single row is worse than useless here. Phase 4 resolves every unallocated row regardless — one at a time in its Step 2 walk, or inside the Step 1 offer where that fires — so the row is already going to be settled, at a cost of one prompt or of none; spending a turn now to save at most that is a pure cost, and it is paid before the operator has seen any output at all. **On the re-cut path the same test holds for a stronger reason**: a candidate is not a row waiting to be settled but one already settled at both levels, so a question that moves a single one of them buys a move the operator can decline for nothing. What earns a question is a **terminology decision that moves several rows at once**: *the BRD uses "form" for an order record and for a compliance artifact — which is meant in these six rows?* That is the reference's *force terminology precision* rule, and it is the whole reason this grill exists.
2. **A hard cap of five questions**, after which the phase stops whatever remains. The cap is
   stated because `workflows-core:grilling-technique` defines bounded depth as "a capped set … then stop", so a
   caller declaring bounded owes a number; and it is **five** rather than ten because the residue
   here has a free fallback that `/idea`'s does not.

**That difference is worth stating, because it is what sizes the cap.** In `/idea` an unanswered
bounded question becomes a `[NEEDS CLARIFICATION]` marker that ships inside the artifact, so the cap
buys a hole in the deliverable and ≤10 earns its length. Here an unplaced row simply reaches Phase 4
without a recommendation, in a phase that was going to settle it anyway — and it can still be moved
by hand in Phase 2's own edit/merge/move picker. Two downstream channels catch the same row for free,
so past the first few questions the grill is the most expensive of the three ways to place a row and
the only one that runs before anything is visible.

**The cap sizes correctly on the re-cut path for the same free-fallback reason, not by assumption.** A candidate this phase leaves unplaced is **not walked**: Phase 4's Step 2R passes over it and leaves it with its donor, the final report names it, and Phase 5 records it. That is a resolution — the row keeps the fate two ledgers had already agreed on — and not a hole in a deliverable, so the residue here costs even less than the ordinary path's does and five is if anything generous.

**A row still unplaced when this phase ends is left unclustered — on an ordinary run; the paragraph below is the re-cut path's version**, and that is a resolution rather
than a failure: it is exactly the fate Phase 2 already gives a row nothing clusters with, and Phase 4
settles it with no recommendation of its own — walked on a blank picker, or carried in the Step 1
offer's set like any other row this reading did not place elsewhere — which is this command's
behaviour on every run that was given no instruction at all. **No new marker, no new record, and nothing carried forward** — inventing a
`[NEEDS CLARIFICATION]`-style marker for it would put a token into a ledger and an inventory whose
field sets are fixed elsewhere (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2,
`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2).

**On the re-cut path an unplaced candidate is not walked at all**, and that too is a resolution rather than a failure — a different one, because the row is in a different state. It already carries a fate at both levels, `covered-by: <A>` here and `deferred-to: <A>` on A, so there is no picker that could leave it where it is more cheaply than not showing it: the ordinary path's unplaced row still has to be settled by somebody, and this one is settled already. It stays `covered-by: <A>`, Phase 4's Step 2R passes over it, the final report names it, and Phase 5 records it as a candidate this run did not move — **those are three roles, not three reporters**: Step 2R declines to walk it, the report names it to the operator, and `slices.md` is where it is written down.

**Nothing in this phase writes.** It settles a reading; Phase 2 proposes from it, Phase 4 recommends
from it, and Phase 5 records it. A `Cancel` here stops the run with nothing written, exactly as a
`Cancel` in Phase 2 does.

---

## Phase 2 — Propose slices

**Skipped entirely in `split_mode: allocate-only`** (Phase 0 step 5). A slice can hold no child, so
there is nothing to propose and nothing a proposal could be keyed into; go straight to Phase 4,
whose walk is the whole of an `allocate-only` run. Everything below is `full`-mode only.

Read `<BRD-dir>/brd/brd-inventory.md` and `coverage-ledger.md`. A root carries no grounding findings to read (Phase 0 step 1a), so clustering comes from the Phase 1.5 placement alone: group every `[BR#n]` still `unallocated` — **or, on the re-cut path (`recut_mode: true`), every `[BR#n]` in the re-cut candidate set** — by what the instruction placed it into, a coherent group of `[BR#n]` rows, never a single row on its own unless nothing else clusters with it. **A row Phase 1.5 left unplaced is not forced into a slice** — that is exactly the fate this rule gives a row nothing clusters with, and Phase 4 walks it with no recommendation of its own. On the re-cut path an unplaced candidate is not forced into one either, and there it is not walked at all: Phase 4's Step 2R passes over it and leaves it with its donor, and the run reports it (Phase 1.5).

Present the candidate slices — each: a short working name, its `[BR#n]` rows, and the one-line rationale, what in the instruction placed it.

**On the re-cut path each proposed group also carries a target** — the child its rows would move to. A target is one of two things and never a third: the **new slice** the group proposes, named by its working name and keyed in Phase 3, or a **named standing child** from the eligible receiver set (Phase 0 step 9a). **This phase's confirmation is what fixes the receiver**; Phase 4's Step 2R offers what was fixed here and chooses none of its own, which is why the target belongs in the proposal the operator confirms rather than in a picker they meet later. Changing a target is what the *"Edit one or more slices (rename, merge, move a row)"* answer below is for — moving a row between groups moves it between targets — and no option is added for it.

**The two per-row clauses constrain which standing children may be proposed as a target, and this consequence is not obvious.** The eligible receiver set is global while both exclusions are per row, and a group carries several rows — so **a standing child cannot be a group's target where it is the donor of any row in that group, or where it already holds a ledger row for any `[BR#n]` in it** (Phase 0 step 9a), even though it is eligible and even though it may be a legitimate target for a different group. Where an instruction clusters rows from several donors together, or clusters a row some standing child already holds a row for, either the group takes a new slice as its target — which is nobody's donor and holds no row for anything, by construction — or it is split until no group is aimed at a child either clause excludes for one of its own rows. Propose it that way rather than presenting a target the confirmation would have to refuse.

**On the re-cut path every `[BR#n]` in that presentation also names its donor**: the donor's key, and the fact that the donor's own ledger records `deferred-to` against that row. Phase 0 step 9a built exactly that pair, and it is the pair — this BRD's `covered-by: <A>` beside A's own `deferred-to: <A>` — that makes the row movable at all (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). So the operator sees which slice is giving each row up before confirming anything; a proposal that hides the donor asks them to approve a transfer they cannot see. **The donor is a property of the row, never of the proposed slice** — one candidate slice may take rows from several siblings — so it is named per row and never once per group.

**One of the four answers below has no re-cut meaning of its own, and it is stated here rather than left to a guess.** *"Make this whole BRD one slice"* answers the degenerate case of a **first** split — nothing clusters, so the whole BRD becomes the one slice — and on the re-cut path there is nothing for it to make: every row already carries a fate, and at least one slice already stands, since `recut_mode` is set only where some child's own ledger defers a row this BRD delegated to it (Phase 0 step 9a, step 10). So on that path **it is unavailable, and an operator who picks it is read as declining** — the same outcome as confirming no group: nothing is created, nothing moves, every candidate is left with its donor and reported, and the run continues to Phase 4 where Step 2R has nothing to offer. Say that when it is chosen, rather than acting on it or asking again. **The array is unchanged and nothing is added or removed for this** — `AskUserQuestion` renders two to four options and this one is presented verbatim like every other (`workflows-core:escalation-rules`); what this paragraph fixes is what that answer *means* here, which is the one thing an agent would otherwise have to invent, and every invention writes something.

Confirm before anything is created:

```
choices: ["Accept these slices as proposed (Recommended)", "Edit one or more slices (rename, merge, move a row)", "Replace with a different slice list entirely", "Make this whole BRD one slice"]
```

**Zero confirmed slices is not an outcome this phase can reach on an ordinary run.** A BRD is a container, never
something implementable in its own right, so **this command always produces at least one slice** —
and the degenerate case has an honest answer rather than an escape valve: where nothing clusters,
the whole BRD becomes one slice, which is what *"Make this whole BRD one slice"* selects. Editing
the list down to nothing re-asks this question rather than proceeding.

**On the re-cut path zero confirmed slices is reachable, and it is a real outcome of a real run rather than a degenerate one.** An operator can read the proposal — which names each row's donor — and decide the rows should stay where they are; putting that judgement to them is what this phase is for on this path, and *no* is one of its answers. Nothing is forced in its place, and **nothing stops** — no no-receiver stop exists in this command, because declining a proposal is an answer rather than an error (Phase 0 step 9a). The run continues to Phase 4, Step 2R has no receiver to offer for any candidate, every candidate is reported left with its donor, and Phases 4.5, 5, 6 and 7 run as usual. So on this path editing the list down to nothing **proceeds** rather than re-asking. **Confirming no new slice is not the same as confirming no receiver**, and the difference is what decides whether anything moves: a confirmed group whose **target is a standing child** (the exception below) places its rows and fixes that child as their receiver, and Step 2R then offers it — the choice was made here, not there. **The guarantee above is untouched, and not by exception**: `recut_mode` is set only where some child's own ledger already records `deferred-to` against a row this BRD delegated to it (Phase 0 step 9a), so a slice already stands on every run that reaches this phase in that mode, and the requirements still land somewhere a PRD can be written whether or not this run adds another.

**One exception, and Phase 0 step 9 already states it: a parent that already has children.** There the
run's job may be to allocate rows to slices that exist rather than to carve new ones — step 9 says an
existing child "remains a valid `covered-by` target in Phase 4 even when this run proposes no new slice
of its own" — save one it marks unreconcilable. Where at least one child already stands that step 9
did not mark unreconcilable, **"propose no new slice — allocate to the existing children" is an
available answer** and the walk proceeds to Phase 4 on the children already
there. Without it the operator must confirm a slice they do not want, watch the walk assign it nothing,
and then accept Phase 4.5's offer to remove the folder Phase 3 just created — cancelling mid-key-taking
to get the slice dropped is a workaround, not a stated behaviour. The rule that a BRD always yields at
least one slice is unchanged: on a **first** split there are no children, so the degenerate case still
resolves to *"Make this whole BRD one slice"*. **Where a slice already stands the guarantee is met
without that answer, and the answer means less than it did** — on an ordinary run it proposes a
single slice carrying the rows still to place, nothing more, and on the re-cut path, where there are
no rows to place at all, it is read as a decline (above).

**On the re-cut path that exception carries the receiving half of the proposal, and the target list is not every standing child.** The **eligible receiver set** Phase 0 step 9a computed is exactly which of them may be **proposed as a group's target** here — this phase makes that choice and its confirmation fixes it, and Phase 4 offers what was fixed rather than picking again — and that set travels with **two** per-row clauses this phase applies rather than restates: a row's own donor is never a receiver for that row, and neither is a child that already holds a ledger row for that row's `[BR#n]` — so a standing child cannot be a group's target where it donates any row in the group or already holds a row for one. **Name the children the set excludes, with the reason, and the reasons are not one reason** — a child excluded from the set has been interviewed, so the customer conversation about it has started and a register that exists and holds decisions is closed to added scope, or it is one Phase 0 step 9 marked unreconcilable, named with the file it is missing or cannot read, which this run's reconcile step will not write; a child excluded by either per-row clause is excluded **for those rows only** and is still a target for a group of others, which is a different thing to be told and a different thing to do about it (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2, `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4). An operator who expected to send a row to a slice that no longer accepts it is owed that reason; a target list that is silently short reads as a bug in the enumeration, and the answer to it — carve a new sibling, which is eligible by construction — is one they can only reach if they know why the one they wanted is missing.

**Why a container, rather than letting a BRD hold its own PRD** — the namespace argument now lives
in `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5, the authority every PRD-eligibility
refusal cites, and is not restated here: a BRD that could be split *and* be PRD-eligible itself would
hold PRD folders and its own Epic folders as siblings, which `workflows-core:addressing` §2's second invariant
forbids and which Phase 0 step 9 would then have to tell apart. What this phase contributes to it is
the guarantee: one slice always existing means the requirements always land somewhere a PRD can be
written, and that somewhere is always one level down.

---

## Phase 3 — Key and nest each confirmed slice

**Skipped entirely in `split_mode: allocate-only`** — this phase is the child creation the one-level
cap forbids, and it is the only phase that is forbidden rather than merely empty.

For every slice Phase 2 confirmed:

1. **Take a key.** Propose a default of the parent's key plus the next unused two-digit segment
   (e.g. `<PARENT-KEY>-01`, `<PARENT-KEY>-02`, …) and let the operator accept it or supply their
   own. Validate whatever is used with `key-valid` (`workflows-core:addressing` §1); an invalid key
   is re-prompted, never silently coerced. **A key is used — skipped as a default, and re-prompted
   when the operator supplies it — wherever any immediate subdirectory of `<BRD-dir>` carries it**,
   tested per candidate key against the directory names as `workflows-core:addressing` §4.1 defines
   a prefix — the name `PRD-<candidate>` or one beginning `PRD-<candidate>-` — and never by reading
   a segment out of a name. **Not only the children Phase 0 step 9 enumerated**: step 9 finds a
   child by its `brd-link.md`, so a folder an interrupted run created and never linked — empty, or
   holding files but no `brd-link.md` — is invisible to it, and a key proposed beside it would leave
   `resolve-address` two folders for one key. `/product-workflows:prd-ground` names the repair for
   such a folder (`PRD_GROUND_CARVE_INTERRUPTED`, `PRD_GROUND_LINK_MISSING`).
2. **Create the folder inside the folder this run resolved**, per `workflows-core:addressing` §6 — the folder a
   slice gets **is** the folder its PRD will be authored in, and it is never a sibling of its BRD.
   On a current tree that is
   `specifications/BRD-<PARENT-KEY>-<parent-slug>/PRD-<CHILD-KEY>-<child-slug>/`, the parent
   carrying the `BRD-` prefix `/brd-intake` writes (`commands/brd-intake.md` Phase 0 step 7,
   `workflows-core:addressing` §2). `<child-slug>` is a kebab of the slice's working name from Phase 2.

   **The parent half of that path is the resolved folder's actual name, never a path re-derived
   from `<PARENT-KEY>`.** A parent that resolved through `workflows-core:addressing` §5's legacy fallback is
   unprefixed on disk, and writing the prefixed form for it would create a second, empty `BRD-`
   folder beside it and orphan the slice inside it — the parent's inventory, ledger and defect log
   would all be one directory away. The child is created with the `PRD-` prefix either way: §5's
   fallback honors a legacy folder that already exists and never proposes one, and a command that
   creates the folder it did not find still creates it with the §2 prefix (`workflows-core:addressing` §7,
   *Adoption is additive*).

   **It is a `PRD-` folder from the moment it is created, before any PRD exists in it.** A slice
   exists precisely to become a PRD; giving it a `BRD-` directory of its own with a `PRD-` directory
   nested inside holding one file bought a level of tree for nothing. The prefix declares what the
   folder is for, which is the same act `/idea` performs when it takes its key up front. What
   distinguishes this folder from an idea-route PRD folder is its `brd-link.md` — the positive test
   Phase 0 step 9 applies, not the prefix.
3. **Write the child's `brd-link.md`**: `kind: brd`, `key: <CHILD-KEY>`, `parent: <BRD-KEY>` and
   `claims:` — the first two are how the new folder asserts its own identity from the moment it
   exists (`workflows-core:addressing` §4), and `brd-link.md` is the folder's only artifact until Phase 3 step 4
   writes its inventory. Then the slice's `[BR#n]`
   rows as currently proposed, spelled as `${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1
   fixes — each a double-quoted bracketed id, one to a line. **Wherever a later step of this
   command writes the list — adding to it or withdrawing from it — it writes the whole list again in
   that spelling**, every entry already there included, so a list an earlier release spelled
   otherwise is rewritten the first time this command touches it (§2.1). This is provisional:
   Phase 4's walk is the step that actually moves a row's disposition, and a row proposed here for
   this child but resolved differently there (for example rejected instead) is removed **from this
   list** at that point, never left to disagree with the ledger. **Only the `claims:` entry and the inventory row step 4 copies for it are
   withdrawn — the ledger row step 5 seeds is not.** A ledger row is never deleted
   (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2), so the child keeps an
   **orphan row** for that `[BR#n]`, and Phase 4's reconcile step writes it the terminal
   disposition the walk settled — including `covered-by: <SIBLING-KEY>` where the walk gave the
   requirement to another child of this BRD. Deleting it instead would erase the only record that a
   claim was made and withdrawn; leaving it `unallocated` would block that slice's own §4 gate
   forever, and with it every command that gates on the slice being fully allocated.

   **On the re-cut path all of that is unchanged and still exactly true.** Phase 4's walk is still the step that actually moves a row's disposition — there it is Step 2R — so a slice this run keys as a receiver holds a provisional `claims:` entry until that walk writes the row, exactly as any other confirmed slice does. **The seeding does not change either, and this is the sentence a reader will get wrong.** Step 5 still writes one `unallocated` ledger row per claimed `[BR#n]`, and that row is `unallocated` because it is **a new row born in the initial state — never an existing row returned to it**, which no command may write on a slice's ledger (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3). **State it in that general form and not as "a new row on a new ledger"**, because the receiver need not be a slice this phase keys: where the confirmed target is a **standing** child, this phase writes nothing for it at all and the new `unallocated` row is written onto that child's **existing** ledger by Phase 4's reconcile step instead. Both are rows that did not exist before, and neither is a row moved backwards, which is the whole reason the re-cut leaves §4's gate intact: the donor's row moves from one terminal disposition to another, and the receiver's row is born in the state every ledger row is born in. **That first half is a guarantee bought in Phase 0 and not an assumption made here**, which is worth saying because a standing child's ledger is exactly where a row for that `[BR#n]` could already be: step 9a's second per-row clause makes a child already holding a ledger row for a candidate's `[BR#n]` ineligible as that row's receiver, so the row this step or Step 3 seeds onto a standing receiver is always the first row that ledger has ever held for that id (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). Without that clause the sentence above would be false on an ordinary tree, and the alternatives are the two the clause exists to forbid — `unallocated` written over a terminal row, or a claim added to a row that names somebody else.
4. **Write the child's `brd/brd-inventory.md`** — the subset of *this* BRD's inventory rows the
   `claims:` list above names, copied row-for-row (`id`, `text`, `source_anchor`, `defects`
   verbatim, each cell exactly as it stands in this BRD's file — or, where that file predates the
   layout, as it gives the cell, encoded by `brd-format.md` §2.3 as it is written), in the layout
   `${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2 fixes, under the frontmatter §2.1 fixes for a
   slice — `kind: brd`, the child's `key:`, and the `parent:`/`source:` pair, `source:` naming the
   document this BRD's inventory records in its `document:`, the one its rows were last reconciled
   against — never the one `brd/brd-link-log.md` opens with, which a rename run that stopped before
   its Phase 3 leaves naming a document no row was read from. On an inventory carrying no
   `document:` — one written before 3.7.0 that no 3.7.0 intake has run over, whose Phase 2 writes
   one — read the log's opening line instead (`brd-format.md` §1.1). **Write it on the base
   `brd-format.md` §2.1 fixes, relative to this BRD's folder** — `brd/source/<basename>`, `brd/`
   put before a `document:` value, which is relative to `brd/` — never the `document:` value as it
   stands.
   **Copy; never re-extract.** Ids are
   the parent's and stay the parent's, and every `source_anchor` copied here keeps resolving
   against the parent's files — its `brd/source/`, `brd/source-external/` or `brd/brd-figures.md`,
   by the anchor's form (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1) — the child holds no
   source of its own and never will, which is why §2.1 makes the header carry the parent's document.
   The child likewise gets no `brd/brd-defect-log.md`: a `[DEF#n]` on a copied row is the parent's,
   and any reader who has to resolve one while standing on the child looks it up in the parent's log
   (`brd-format.md` §4). That resolution is always one hop, never a chase: the cap in
   `workflows-core:addressing` §6 makes this child's parent — this BRD — the source-owning root.
5. **Write the child's `coverage-ledger.md`** — in the layout
   `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2 fixes, its `key:` the child's —
   one row per `[BR#n]` in the inventory just written, `disposition: unallocated` on every one, per
   §3, whose creator table names this phase as the writer of a slice's ledger. `text` and `defects`
   mirror the copied inventory row, cell for cell; `evidence`
   is empty — the child has not been ground yet, and this BRD's `[CG#n]`/`[DG#n]` findings were
   derived against this BRD's claim list, not the child's.

Steps 4 and 5 are what let the child **re-enter the route** at Phase 7's recommendation:
`/prd-ground`'s own Phase 0 gates on the child's `coverage-ledger.md` and reads the child's
`brd/brd-inventory.md`, and `/brd-intake` — the only other command that **creates** either file — is
never run on a slice, because a slice has no document to intake. (Creating is the claim that holds:
once a ledger exists, `/product-workflows:prd-ground` writes its `evidence` column and
`/product-workflows:brd-reconcile` writes dispositions into it, so *writes* — which this clause used
to say — is false of both.) This command is the only place those two files can come from, so it writes them at the same moment it writes `brd-link.md`, not
later.

A slice confirmed in Phase 2 but never given a folder here (the operator cancelled mid-key-taking) is dropped — it never becomes a `covered-by` target. **What becomes of its rows depends on the path.** On an ordinary run they return to the ledger walk unclustered, as they always have. **On the re-cut path they return to nothing**, because they never left: each already carries `covered-by: <A>` here and `deferred-to: <A>` on its donor, and a candidate whose target is gone is not walked — it is left with its donor and reported, exactly as a candidate no confirmed group carried is. A dropped slice on that path therefore costs the run nothing but the move it was going to make.

**About the child's key.** The default proposed in step 1 — the parent's key plus the next unused
two-digit segment — is a naming convention that keeps sibling slices distinguishable and reads as
what it is. It buys the child no resolution depth and needs none: `resolve-address` searches
the three levels below `specifications/` that `workflows-core:addressing` §3 bounds, which is where this folder sits regardless of how
many segments its key carries (`workflows-core:addressing` §1, §3). So an operator-supplied key with no
additional segment resolves exactly as the default does, and nothing about either choice makes the
child sliceable — no key shape lifts the one-level cap (§3).

---

## Phase 4 — Walk the ledger

**This phase runs in both modes** — it is the allocation walk, and allocation is not what the
one-level cap restricts. What differs is the size of the picker.

**Four steps, in this order:** the uniform-answer offer (Step 1 — conditional, and skipped on most
runs), the walk itself (Step 2 — the default, and the reason this phase exists), the re-cut walk
(Step 2R — `recut_mode: true` only, which re-points each candidate row from the sibling that
deferred it onto the receiver Phase 2 fixed), and the reconcile that follows whichever walk ran
(Step 3 — `split_mode: full` only).

**Step 2 and Step 2R never both run, and that is by construction rather than by an exclusion rule.** Step 2 walks rows that are still `unallocated` when it opens, and on the re-cut path there are none: `recut_mode` is set only where Phase 0 step 8 found the ledger fully allocated (step 10). So each run takes exactly one of the two walks, and every sentence below that names one of them is about that run's own walk.

### Step 1 — the uniform-answer offer, taken once before the first row

**Skipped unless the firing condition below holds. Where it is skipped, nothing in Step 2 or
Step 2R changes, and where it is declined, nothing is written by it.**

**Why it exists.** A BRD is a container, so this command always produces at least one slice
(Phase 2) — and the whole of a BRD becoming *one* slice is the ordinary shape of this route rather
than a corner of it. In that shape every row on the parent takes `covered-by: <the one slice>`, and
every row on that slice then takes `covered-here`: two walks whose answer the shape of the split
settled before either opened a ledger. Asking once per row for an answer the run can already state
is the defect `workflows-core:escalation-rules` names under *When a choice list
fires* — a list written for a question whose answer is already determined spends a user turn on a
formality. A forty-row BRD resolved to a single slice costs **eighty** prompts across the two runs
without this step and **two** with it.

**It fires only where the answer is uniform by construction — never merely where it would be
convenient.** Both conditions in its row must hold:

| Mode | Fires when |
|---|---|
| `full`, `recut_mode` false | **exactly one** slice stands as a `covered-by` target — the union of the children Phase 3 keyed this run and the children Phase 0 step 9 enumerated and did not mark unreconcilable is a single folder, since an unreconcilable child is no target (Phase 0 step 9) — **and** two or more rows are in the set this step would actually offer (below), which leaves out every row that slice may not be offered |
| `full`, `recut_mode: true` | **two or more rows are in the re-cut candidate set carrying a placement** — a placement being what fixes a row's receiver (Phase 2) — **and those placed rows carry exactly one distinct target between them.** Counting the raw candidate set instead repeats the `allocate-only` row's own defect one path over: a candidate Phase 2 gave no target is one Step 2R does not walk at all, so it is not a row this offer could write. **Count confirmed targets over the placed rows, never standing folders**, and the difference is the whole of whether this offer ever fires: Phase 0 step 9a puts an **uninterviewed donor in the eligible receiver set by design** — being interviewed disqualifies a receiver, never a donor — so in this design's ordinary shape, one uninterviewed donor and one new slice keyed in Phase 3, the standing-folder count is two and a folder-counting condition would fire only where every donor happened to have been interviewed already, which is the opposite of the case step 9a calls ordinary. The per-row donor clause is why the two counts differ at all: the donor stands, and is eligible, and is a receiver for none of these rows |
| `allocate-only` | **two or more rows are in the set this step would actually offer** — every row still `unallocated`, *minus* any row Phase 1.5's reading already placed on a different disposition. Counting the raw `unallocated` set instead fires the offer on a set of one or zero: an instruction like *"defer everything except the login flow"* leaves five rows `unallocated` while Phase 1.5 places four of them on `deferred-to`, so the condition saw five and the step rendered *"Write `covered-here` on all 1 rows now"* — the degenerate prompt the rule below says is skipped |

**Why each condition is the condition.** With one standing slice, `covered-by` has exactly one legal
argument, so the offer picks no target on the operator's behalf: what is uniform by construction is
the **key**, not the disposition — which is exactly why this offer is refusable per row rather than
a completion. **With two or more slices standing it does not fire at all**, and that is not a
limitation for a later edit to generalise away: which slice owns a row is the per-row judgement this
walk exists to take, and no single confirmation could name a target without taking it for the
operator. In `allocate-only` mode every row this walk stands on is a row the parent allocated
**here** — which is why that picker already carries a standing
`(Recommended — this slice was carved out to build these rows)` on `covered-here` for every row it
shows; the offer is that same recommendation made once instead of N times, not a new claim. And
below two rows there is nothing to save — one offer replacing one prompt — so the step is skipped
rather than shown, by the same *When a choice list fires* rule.

**On the re-cut path the same reasoning holds over a different uniformity, which is why this offer is reused rather than duplicated.** Where every placed candidate carries the same confirmed target, the `<B-KEY>` the offer names is already each of those rows' own receiver, so it picks no receiver on anyone's behalf — Phase 2's confirmation fixed one per group, and this condition is just those confirmations agreeing. What stays per-row is the judgement Step 2R exists to take: whether *this* row is one to move at all. So the offer is refusable per row here for exactly the reason it is on the ordinary path. **Where the placed rows carry two or more distinct targets it does not fire**, and the reason is narrower than the `full` row's: the confirmations are already made, so nothing is being judged for the operator — what a single list cannot do is *say* what it would write, because its one `<B-KEY>` would stand for two destinations and the rows going to each would be invisible in it. That is the same *When a choice list fires* problem the whole step exists to avoid, arriving from the other side.

**Its vocabulary is two dispositions on the two ordinary paths and three counting the re-cut, and that is structural rather than a preference.** The offer
writes `covered-by: <CHILD-KEY>` (`full`) or `covered-here` (`allocate-only`) and nothing else. The
other three each need a per-row fact it cannot supply and must not invent: `deferred-to` needs the
one-line rationale Phase 5 writes into `slices.md`, `rejected` needs the `[DEF#n]` that justifies
it, and `superseded-by` needs the `[BR#n]` that replaced it. A bulk form of any of the three would
either skip a prompt that carries content or copy one row's reason onto rows that do not share it.
**The third is the re-point**, `covered-by: <B-KEY>` written on the parent's row, then on the donor's, then on every *other* standing child's row that named the donor for that `[BR#n]` — Step 2R's three writes in Step 2R's order, and for the reasons it states there. It is a bulk form of the one write in this command that needs no per-row fact the run does not already hold: the donor came from Phase 0 step 9a's candidate set, the receiver from Phase 2's confirmation, and neither is a sentence the operator has to type. **The reason the other three cannot be bulk-written is unchanged and is not re-argued for this path** — each still needs the rationale, the `[DEF#n]` or the `[BR#n]` it always needed, and the re-cut adds none of them to what a bulk answer can supply.

**The set it offers to write.** Every row still `unallocated`, **minus** any row Phase 1.5's reading
placed on a *different* disposition, **and minus**, on the ordinary `full` path, every row the one
standing slice may not be offered — one its own ledger holds an orphan row for, or a row reading
`covered-by` for while still claiming it (Step 2's *Assign to a named slice*). A bulk write naming that slice would be exactly
the write that bullet refuses, so each such row is held back to the walk, named with the row that
excludes it, and walked there with that slice not offered. Those keep the recommendation the instruction earned them (the
`<recommended>` table in Step 2) and are walked one at a time. An instruction the operator typed is
not something a shortcut may quietly overrule, so the offer **names** those rows and what the
instruction placed each on, rather than absorbing them.

**On the re-cut path the set is every row in the re-cut candidate set carrying a placement** — the same set Step 2R would walk, defined there and not re-derived here, and in particular carrying the **post-Phase-2** sense of "placed" that step states. A candidate the placement left unplaced is **not** in it and is not held back to a walk either: it is not walked at all, it keeps the fate two ledgers already agreed on, and the offer names it as such rather than absorbing it or promising to return to it (Phase 1.5). There is no *"minus what the reading placed elsewhere"* term here, and its absence is the point: on this path the placement's job is to fix a receiver, not to name a disposition, so a placed row and an offered row are the same row.

**What the offer states before anything is written**, in the prose beside the list:

1. the disposition it will write, spelled out — `covered-by: <CHILD-KEY>` with the key filled in,
   `covered-here`, or, on the re-cut path, `covered-by: <B-KEY>` with the receiver filled in;
2. the count, and every `[BR#n]` in the set with the first line of its `text`, decoded
   (`brd-format.md` §2.3), so a row that does not belong is visible without opening the ledger;
3. in `full` mode with `recut_mode` false, that it also adds each of those `[BR#n]` to `<CHILD-KEY>`'s `brd-link.md`
   `claims:` list — the same second write Step 2's **Assign to a named slice** bullet performs, not
   an extra one. **On the re-cut path the writes after the parent's are different ones and are stated as such**: the *donor's* ledger row takes `covered-by: <B-KEY>` second, and any *other* standing child's row naming the donor for the same `[BR#n]` takes it third, in that order (Step 2R) — and no `claims:` list is touched here at all — the donor's entry is withdrawn and the receiver's added by Step 3's reconcile, on this path exactly as on any other;
4. every row it will **not** write, and why — each row Phase 1.5 placed elsewhere, named with its
   placement; **on the re-cut path that is instead every candidate the placement left unplaced**, named with the donor it stays with and the fact that nothing will walk it;
5. that Step 3's reconcile, Phase 4.5 and Phase 6 all run exactly as they would after a
   one-at-a-time walk, over the same files;
6. that it settles nothing beyond those N rows: a bulk write is the per-row write of the walk this
   run would otherwise take — Step 2's, or Step 2R's on the re-cut path — taken N times
   behind one confirmation — the same disposition vocabulary
   (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3, and §3.2 for the re-point's
   writes) and the same gate (§4), with no
   row reaching a terminal disposition by a route that file does not already own;
7. **on the re-cut path only, for each row in the set: its donor's key, and every decision in that donor's `decisions.md` whose `evidence` touches the row** — the same report Step 2R makes per row, made once here instead, because a bulk answer is the operator's one chance to see it. **Resolving "touches" is two hops and neither is a guess**: a decision's `evidence` list holds `[CG#n]`/`[DG#n]` ids (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1), and a finding's `claim` is the `[BR#n]` premise it was derived against (`workflows-core:grounding-format` §2), so a decision touches this row where any finding in its `evidence` list carries this `[BR#n]` as its claim — resolved against the donor's own grounding files. Report each by `id` and `statement`. **It is advisory, and nothing here edits a decision**: those decisions record the donor's refusal to build the row, which the move leaves standing (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). A donor with no such decision is named as having none, rather than omitted — an operator who cannot tell "nothing was decided about this row" from "the report skipped it" is not being shown anything.

**The list.** `<N>`, `<CHILD-KEY>`, `<B-KEY>` and the disposition are substituted exactly as `<BRD-KEY>` and
`<recommended>` are substituted elsewhere in this phase; the array is otherwise presented verbatim
(`workflows-core:escalation-rules`, *Choice lists are presented verbatim*), and each of the three below is three options, inside §0's
two-to-four cap, with the free-text answer the harness supplies handled below.

**`split_mode: full`, `recut_mode` false:**

```
choices: ["Write covered-by: <CHILD-KEY> on all <N> rows now", "Write it on all but the rows I name — I'll walk those one at a time", "Walk every remaining row one at a time — decide each row"]
```

**`split_mode: allocate-only`:**

```
choices: ["Write covered-here on all <N> rows now (Recommended — every row this walk stands on is a row the parent allocated here, which is the marker the per-row picker carries on each of them, made once)", "Write it on all but the rows I name — I'll walk those one at a time", "Walk every remaining row one at a time — decide each row"]
```

**`split_mode: full`, `recut_mode: true`:**

```
choices: ["Re-point all <N> rows to <B-KEY> now — each was deferred by the slice that holds it", "Re-point all but the rows I name — I'll walk those one at a time", "Walk every candidate one at a time — decide each row"]
```

**Why one list carries a marker and the other two do not** — the same rule all three times, applied to what
each picker already says. The `allocate-only` picker recommends `covered-here` on every row it
shows, unconditionally and for a reason no instruction changes, so recommending it once here is that
marker printed once: a reason annotation, honoured verbatim, of the kind `workflows-core:escalation-rules`
admits explicitly. The `full` picker carries **no** marker unless an instruction placed the row,
because which resolution is right is a fact about the row in front of the operator — and there being
one slice does not change that. So the `full` offer carries none either, and says so beside the
list: *no option here is recommended — this run knows which slice a delegated row would go to, not
whether this row is one to delegate.* That is `workflows-core:escalation-rules`'s *When no option is safe to
recommend*, not an omission.

**The re-cut offer carries no marker either, for the same reason and not a new one.** Say beside its list: *no option here is recommended — this run knows which sibling a re-pointed row would go to, not whether this row is one to move.* Phase 2's confirmation fixed the receiver, so the `<B-KEY>` is settled and the offer asserts nothing by naming it; what is not settled is whether the operator, having now seen each row's donor and what that donor decided about it, still wants it moved. That is a fact about the row in front of them, so *When no option is safe to recommend* applies here exactly as it does to the `full` offer. **That Step 2R's own per-row picker does carry a marker is the same asymmetry this step already lives with on the ordinary path, not a contradiction of this paragraph**: there the marker is a reason annotation naming what in the instruction placed *that* row, and one confirmation recommending the same write across a whole set is a different and larger claim — which is exactly why the `full` picker may carry one while the `full` offer may not.

**Answering.**

**Read every mention of Step 2 below as Step 2R on the re-cut path** — that run's walk is Step 2R, Step 2 does not run on it, and nothing else in this sub-section changes: option 2's naming prompt, its validation, its single re-prompt and the fall-through rule all apply exactly as written. **The fall-through direction on the re-cut path is the walk as well**, at both prompts, for the reason it is everywhere else here: an answer this step cannot read must never take the maximal write, and here the maximal write moves rows off a fate two ledgers had agreed on.

- **Option 1** — write the whole set (below), then continue into Step 2 with only the excluded rows
  left to walk, if there are any.
- **Option 2** — **one** further prompt, free text, not one per row: ask which `[BR#n]` ids to hold
  back, restating in that prompt the disposition every row *not* named will receive. Validate each
  id against the set: one that is not in it — unknown, already terminal, or already excluded — is
  named back and the prompt repeated **once**, never silently dropped and never written. **Every
  answer this prompt cannot use falls the same way — to option 3, the walk.** An **empty** answer
  falls there, and so does a **second** unusable answer after that one re-prompt: an operator who
  opened option 2 to name exceptions and then named none this step could read has given the least
  determinate answer there is, which is the furthest thing from a mandate to write every row. A
  stray Enter is the input nearest to unparseable, and it must not be the one input that takes the
  maximal write. Otherwise write the reduced set and walk the named rows in Step 2. **This is what
  keeps a partial answer cheap**: three exceptions out of forty cost one offer, one naming prompt
  and three row prompts, not forty.
- **Option 3** — write nothing here. Step 2 runs over every row exactly as it does on a run where
  this step never fired.
- **A free-text answer** naming `[BR#n]` ids is read as option 2's answer and validated the same
  way; anything else falls through to option 3. **The fall-through direction is the walk, uniformly
  and at both prompts** — this one and option 2's naming prompt — which is what stops an answer this
  step could not read from writing a row nobody answered for. No answer to any prompt of this step
  resolves to option 1 except option 1 itself.

**Writing the set.** For each row in it, write exactly what Step 2's bullet for that disposition
writes — `disposition: covered-by: <CHILD-KEY>` plus the `claims:` entry, or
`disposition: covered-here` — row by row in the file, so an interrupted run leaves every row either
`unallocated` or terminal and none half-written. Ids are the parent's throughout, and nothing else
about a row changes. Then report the rows written, under the one disposition, and the rows held back
with why each was held back — named by the operator, or placed elsewhere by the instruction.

**On the re-cut path, write exactly what Step 2R writes, in Step 2R's order, one row at a time.** That is the parent's ledger row first, the donor's second, and the sweep of every *other* standing child's row naming the donor for that `[BR#n]` third, per `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2 — and the order carries the same reasons under a bulk answer that it carries under the walk, so it is not the offer's to simplify: an interruption between the first two must leave the parent pointing one hop at the receiver, never a second hop through the donor, and the sweep is last because until the donor's row has moved there is nothing for another child's row to point at that is not a claim about the receiver made before it was true. **Take all three writes for one row before starting the next**, which is what makes "row by row in the file" mean the same thing here as above: an interrupted bulk answer then leaves each row either wholly re-pointed or wholly untouched. Report the rows re-pointed, the receiver they went to, each row's donor, every other child's row the sweep re-pointed with it — or that the sweep found none — and every candidate not written, held back by the operator or left unplaced by the placement and therefore never in the set.

**A row held back is walked, not dropped.** It is still `unallocated`, and §4's gate still blocks
this command until Step 2 gives it a terminal disposition. A `Cancel` during that walk stops the run
naming how many rows remain, and every row this step already wrote stays written — exactly as a row
resolved early in a one-at-a-time walk does.

**On the re-cut path a held-back row is walked too, and it is §4's gate that does not apply.** A candidate already carries a terminal disposition on both ledgers, so nothing blocks this command on its account and a run that ends with every candidate held back and then left with its donor is a complete run rather than a stalled one. What holds is the rest: Step 2R walks each held-back candidate one at a time, a `Cancel` stops the run naming how many are unwalked, and every re-point this step already wrote stays written.

### Step 2 — the walk

For every row in `coverage-ledger.md` still `disposition: unallocated` when this step opens — every
row on a run where Step 1 did not fire or was declined, and only the rows Step 1 held back on a run
where it wrote — present it **one at a time, never batched**, via `AskUserQuestion` — quoting its
`id`, `text`, `defects`, and `evidence`, each cell decoded
(`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.3), so the operator has everything needed
without opening the file. **This is the default, and Step 1 does not displace it**: per-row
judgement is what this walk is for, and no row is ever written in bulk without an offer that named
it being shown and answered.

**`split_mode: full` — four resolutions:**

```
choices: ["Assign to a named slice — covered-by<recommended>", "Defer to this BRD — deferred-to (a real allocation, not a shortcut)<recommended>", "Reject — citing a [DEF#n]<recommended>", "Mark superseded by another [BR#n]<recommended>"]
```

**No option on that picker carries a `(Recommended)` marker, and the omission is required rather
than stylistic.** Which resolution is right is a fact about the row in front of the operator — a row
that clusters into a slice takes `covered-by`, one this BRD still owes takes `deferred-to`, one the
customer has withdrawn takes `rejected` — and the list is shown once per row, so no marker could be
true across the runs that reach it. `workflows-core:escalation-rules` covers
exactly this under *When no option is safe to recommend*: omit the marker and say so in prose beside
the list. **A conditional marker is not the alternative.** `(Recommended when nothing clusters)`
reads as guidance and is malformed by that file's *The `(Recommended)` marker is unconditional*
rule — it hands the operator the gate this phase was supposed to evaluate, and an orchestrator that
must present the list verbatim cannot honour it either way. The condition belongs in the option's own
text, which is where it now sits. Say beside the list that **`covered-here` is not among these four**
and why — a parent BRD is a container and builds nothing itself (Phase 2), so a row that must be
built goes to a slice — and that `deferred-to` is a real allocation rather than a way of deferring
the choice itself.

**`split_mode: allocate-only` — four as well**, but **a different four**: `covered-by` is absent and
`covered-here` is present, which is the exact mirror of the `full` picker. State the reason beside
the list, so an operator who sees a different set than the last run is told why rather than left to
notice it.
This picker *does* recommend an option, and the asymmetry is the rule working rather than an
inconsistency: on a slice every row the walk stands on is a row the parent allocated **here**, so
`covered-here` is unconditionally the expected answer and the marker is a plain reason annotation
(`(Recommended — <why>)`), not a condition. It reaches the option through the same `<recommended>`
placeholder the `full` picker uses, for the reason given below the table:

```
choices: ["Build here — covered-here<recommended>", "Defer to this slice — deferred-to (a real allocation, not a shortcut)<recommended>", "Reject — citing a [DEF#n] in the parent's defect log<recommended>", "Mark superseded by another [BR#n]<recommended>"]
```

State once, before the first row of an `allocate-only` walk: *"`covered-by` is not offered here.
On this slice it would name a sibling under the same parent, or that parent — never a child, since
nesting is capped at one level and no child can exist below a slice — only its Epics
(`workflows-core:addressing` §6). It is written by the **parent's** run — its walk, on a claim
that walk withdrew, provisional on the ordinary route, committed and then deferred by this slice
itself where a re-cut moved it onward (§3.2); or its Phase 4.5 removal repair, re-pointing such a
row at the parent when the sibling it named is removed — and every row carrying it is terminal
before this run opens the file (`coverage-ledger-format.md` §2, §3). Every row this walk stands on is a row this
slice claims — a row the parent allocated **here** — so there is nothing for this picker to
delegate. The other four are unchanged, and `covered-here` is what makes this slice PRD-eligible
(§5)."* The remaining four are a strict subset: nothing about them is redefined for a slice.

**Why this walk may not offer it, stated once so no later edit re-adds it.** Delegating a claimed
row to a sibling from inside the slice would leave the parent's ledger saying this slice owns the
row while this slice says the sibling does — the two authorities disagreeing about which BRD owns a
requirement, which is the failure the ledger exists to make impossible
(`coverage-ledger-format.md` §1). It would also point at a sibling whose own inventory holds no row
for that `[BR#n]` at all, and it would put a second hop under the parent's roll-up, which
`coverage-ledger-format.md` §6.1 requires to terminate in one.

**There is now one route by which such a row can reach a sibling, and it is not this walk — so naming it here is the honest answer rather than a widening of this picker.** This walk still allocates only rows that are `unallocated` on this slice's own ledger, and nothing in it moves a row off a terminal disposition. What changed is at the level above: where this slice records `deferred-to: <this slice>` on a row — a decision this picker's second option makes, and a refusal written in this slice's own ledger — the **parent's** own `/brd-split` run, given a slicing instruction, may re-point its `covered-by: <this slice>` row onto a sibling that has not been interviewed (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2, and this command's Phase 4 Step 2R). **That route avoids all three objections above rather than accepting them**: the parent writes both ledger rows in one step, so the two authorities never disagree; the receiving sibling gains its inventory row from the parent's own reconcile; and the parent's row points one hop at the receiver, never two. The honest answer for an operator who wants the sibling to own a claimed row is therefore: this walk cannot give it away, so record here what this slice will actually do with it — and where that is a deferral, the parent's run is where the sibling can take it. Two things are still needed for that and neither is this walk's to arrange: an instruction typed on the parent, and a sibling whose customer conversation has not started.

**`<recommended>` is a placeholder this run resolves per row, and resolving it is not a rewording.**
It is substituted in the option strings exactly as `<BRD-KEY>` and `<merge-clause>` are, so the array
is still presented verbatim per `workflows-core:escalation-rules`'s *Choice
lists are presented verbatim* — a command that instead told the orchestrator to *adjust the wording*
of an option would be contradicting that convention, which is why the variation lives in a
placeholder (`workflows-core:next-phase-offer` states the same for its own).
It resolves, for each row:

| This row's state | `<recommended>` resolves to |
|---|---|
| Phase 1.5 placed it, and Phase 2 keyed that group into a child | ` (Recommended — <what in the instruction placed it>)` on **`covered-by`**, and the empty string on every other option |
| Phase 1.5 placed it into a group that produced no child — the operator declined the slice, or the instruction named a disposition rather than a grouping | ` (Recommended — <what in the instruction placed it>)` on the option that disposition names, and the empty string on the others |
| Phase 1.5 left it unplaced, or this run was given no instruction | the **empty string on every option** in the `full` picker — exactly the picker this command has always shown. In the `allocate-only` picker it resolves to ` (Recommended — this slice was carved out to build these rows)` on **`covered-here`** and the empty string on the rest, which is that picker's standing default (below) |

**The `allocate-only` picker's standing marker is carried by the same placeholder, and that is why
there is one placeholder and not two.** That picker has always recommended `covered-here`, for a
reason that does not depend on any instruction: on a slice every row the walk stands on is a row the
parent allocated **here**. Writing that marker literally into the option *and* adding a placeholder
beside it would put two `(Recommended — …)` annotations in one list the moment an instruction placed
the row — or, worse, one on `covered-here` and another on `deferred-to`, each contradicting the
other. Folding the default into the placeholder's own resolution avoids that without the
orchestrator suppressing anything: a marker is never removed from a written option, because the
option never carries a written marker. **The no-instruction run is unchanged** — the placeholder
resolves to the same sentence that used to be typed there.

**The reason is carried, not just the marker.** `(Recommended — <why>)` is a reason annotation, which
`workflows-core:escalation-rules` admits explicitly; a bare `(Recommended)` here would assert a recommendation
whose only basis is a sentence the operator typed several phases ago and can no longer see. Naming
what in the instruction placed the row is what lets them disagree with it on this row without
abandoning the instruction.

**This is not a reversal of the markerless picker.** A `(Recommended when …)` marker was removed from
the `full` picker precisely because it printed its own condition for the operator to evaluate, which
that file calls malformed. A marker **this command computes per row and prints bare** is the fix that
same rule prescribes — and it becomes available only because there is now an instruction to compute
it from. On a run with no instruction there is still no basis for one, and the third row above is
what keeps that run's picker byte-for-byte what it was.

**A recommendation is not batching, and Step 1 is not a recommendation.** Resolving `<recommended>`
changes what a prompt says, never how many rows it carries: rows in this step are presented **one at
a time**, unchanged; `workflows-core:grilling-technique` asks for a recommended
answer on every question for the same reason this phase carries one — an operator reacting to a
proposal is doing something different from an operator facing a blank picker, and neither is the
same as being handed five rows at once. Step 1 *does* hand the operator many rows at once, which is
why it is a separate, conditional offer that names every row it would write and can be refused row
by row, rather than a wording change inside this picker.

Both pickers offer nothing but **terminal** dispositions from
`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3 — four in each mode, though **a
different four** (`full` offers `covered-by`, `allocate-only` offers `covered-here`), and
`unallocated` in neither: it is the one disposition no choice above ever
writes back. §4 states the gate those resolutions open, which this command
**cannot complete while any row stays `unallocated`** — a `Cancel` mid-walk stops the run naming
how many rows remain, but every row already resolved this pass stays written, including any Step 1
wrote; nothing already decided is rolled back. Each slice's `brd-link.md`, `brd/brd-inventory.md`
and `coverage-ledger.md` stay provisional until a run of this command reaches Step 3 and reconciles
them against this BRD's ledger, and `/product-workflows:prd-ground` refuses such a slice until then
(`PRD_GROUND_CARVE_UNFINISHED`, `PRD_GROUND_SLICE_UNRECONCILED`).

- **Build here** → `disposition: covered-here`. **`split_mode: allocate-only` only** — it is what
  makes a slice PRD-eligible (`coverage-ledger-format.md` §5), and it is the ordinary landing for
  every row a slice's walk stands on, because the parent allocated those rows *here*.

  **It is not offered in `full` mode, and the escape valve it used to be is gone with it.** A parent
  BRD is a container and holds no PRD of its own, so there is no "build it here" for a parent to
  choose; a row that must be built goes to a slice, and this command always produces at least one
  (Phase 2). What that removes is the old completion path for a BRD nobody split — which is no
  longer a state this command can leave behind. Every other resolution is unchanged, in both modes.
- **Assign to a named slice** (`split_mode: full` only) → prompt for the slice's key: any
  created in Phase 3 this run, or any found already nested under this BRD in Phase 0 step 9. Reject a key that resolves to neither
  and re-prompt — `covered-by` never names a folder that does not exist. **Reject, and name beside
  the picker before the first row, every child Phase 0 step 9 marked unreconcilable**, with the file
  it is missing: this run's reconcile step writes nothing into it, so the claim this answer adds
  would never gain the inventory and ledger rows it needs, and the slice would be left claiming a
  row it can never hold (Phase 0 step 9). **Reject, too, a child
  whose own `coverage-ledger.md` holds an orphan row for this `[BR#n]`** — a row for a `[BR#n]` its
  `brd-link.md` `claims:` does not name, recording a claim a walk of this BRD withdrew from it
  (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2) — naming that row's
  disposition, and re-prompt. It is §3.2's per-row receiver exclusion applied to this walk, for
  §3.2's reason: the claim this answer adds needs a new `unallocated` row, and seeding it over the
  terminal row the child holds would return that row to the initial state, which no command may
  write on a slice's ledger (§3); while leaving that row as it stands would have the child claim a
  `[BR#n]` whose own row records the claim as withdrawn, which its own walk never revisits. The
  exclusion is **per row**, and it bars the orphan row and one other: **a child that still claims
  this `[BR#n]` while its own row for it reads `covered-by`** is barred too. No slice's own walk
  writes `covered-by`, so that row is always a withdrawal this BRD's walk began and its Step 3 never
  finished — a re-cut interrupted after Step 2R, or Step 1's re-cut bulk write, wrote the donor's
  `covered-by: <B-KEY>` and before Step 3 withdrew its claim — and offering that child the row would
  leave it claiming a `[BR#n]` its own row gives to somebody else, the stranded state above. **Every
  other child that still claims this `[BR#n]` is offered it**, save an unreconcilable one (above), its own row reading `unallocated`
  because Phase 3 step 5 seeded it for the child's provisional claim, or a terminal disposition the
  child's own walk wrote before a `/product-workflows:brd-intake` re-run over this BRD reset this
  ledger's row. Re-assigning it to that child seeds nothing and moves no row back: Step 3 finds the
  child already in step for that row and writes nothing, and its own row stands. **Where no child is eligible for this row** —
  a parent with one child, say, holding an orphan row for it — do not prompt for a key: say so beside the picker, naming each child and
  the row that excludes it, and take one of the other three, each terminal. **Defer to this BRD** is
  always available; **reject** and **mark superseded** are available wherever the `[DEF#n]` or the
  replacing `[BR#n]` exists. A **newly keyed slice** is how the row is built instead: this run's
  Phase 2 proposes one wherever the instruction placed the row, and otherwise a `Cancel` here,
  followed by a run whose instruction places the row, reaches Phase 2 with the row still
  `unallocated` and keys a new slice for it — a slice holding no row at all, and so eligible by
  construction. Write
  `disposition: covered-by: <CHILD-KEY>`, and add this row's `[BR#n]` to that child's `brd-link.md`
  `claims:` list if it is not already there. **Say what this resolution does and does not settle**:
  it records that `<CHILD-KEY>` owns the row, not that anything is built. The child's own
  `/brd-split` walk decides that, and this run's ledger line reports whichever way it went
  (`coverage-ledger-format.md` §6.1) — a row this walk delegates today can be counted `deferred`,
  `rejected` or `unallocated` on this BRD's next report.
- **Defer to this BRD** → `disposition: deferred-to: <this BRD>` — `<this BRD>` is the slice's own
  key in `allocate-only` mode, exactly as it is the parent's key in `full` mode; the disposition
  always names the BRD the walk is standing on. Prompt for a one-line rationale —
  held for Phase 5's `slices.md`. Deferring is itself an allocation
  (`coverage-ledger-format.md` §3): the point is that the requirement's fate is recorded, not that
  everything must be built now.
- **Reject** → prompt for the `[DEF#n]` that justifies it; it must already exist in the defect log
  that governs this BRD, which is the one place the two modes differ on inheritance: in
  `split_mode: full` that is this BRD's own `brd/brd-defect-log.md`; in `allocate-only` it is the
  **parent's**, because a slice holds no *requirement* defect log of its own and inherits it
  (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1, §4 — the route's separate code-defect log
  is slice-owned and holds no `[DEF#n]`, so it is never what this resolution reaches for). Resolve
  it there via the `parent:`
  key Phase 0 step 5 already read — **one hop, never a chase**, because the one-level cap makes a
  slice's parent always the BRD that owns the source document. A row with no qualifying defect is
  not rejected this way; resolve or raise the defect first. Write
  `disposition: rejected: [DEF#n]`.
- **Mark superseded** → prompt for the replacing `[BR#n]`; it must already exist in
  `brd/brd-inventory.md`. Write `disposition: superseded-by: [BR#n]`.

### Step 2R — the re-cut walk

**Runs only when `recut_mode: true`** (Phase 0 step 10), and it runs **in place of Step 2**, never beside it: on this path no row is `unallocated`, so Step 2's own opening set is empty and the two walks cannot both have work. Everything below is the re-cut path.

**The set it walks.** Every row in the **re-cut candidate set** (Phase 0 step 9a) that a group Phase 2 confirmed **with a target** carries when Phase 2 ends — the target being a slice Phase 3 keyed this run, or a standing child from the eligible receiver set — **minus** any row Step 1's offer already wrote. That target is the row's receiver, and this step **offers it rather than choosing it**: Phase 1.5 read the instruction and Phase 2's confirmation fixed the target per group, so by the time this walk opens the receiver is settled and the only open question is whether this row moves at all.

**"Placed" here is the post-Phase-2 sense, and taking the narrower one silently discards an operator's own edit.** Phase 1.5 states that the word carries two senses and that this phase consumes the later one: a row that phase's own reading could not place is a residue **Phase 2 may still cluster**, and Phase 2's *"Edit one or more slices (rename, merge, move a row)"* answer is exactly how the operator moves such a row into a confirmed group. A set defined as *what Phase 1.5's reading placed* would drop that row and leave it with its donor — undoing an explicit instruction the operator gave two phases ago, silently, and reporting it as a candidate nothing could place. So membership is decided by the confirmed groups as they stand at the end of Phase 2, however each row reached one.

**A candidate the placement left unplaced is not in this set, and is not walked.** Nor is one whose confirmed target no longer stands — a slice dropped when the operator cancelled mid-key-taking in Phase 3. **Say why, so no later edit "completes" the walk by showing them:** such a row already carries a fate at both levels, `covered-by: <A-KEY>` on this BRD and `deferred-to: <A-KEY>` on A, so a picker shown for it would be a prompt whose only available answer is *leave it* — a blank picker has nothing to resolve a row to that the row does not already have. It stays with its donor, this step passes over it, the final report names it, and Phase 5 records it. **Those are three roles and not three reporters** (Phase 1.5): this step's part is to decline to walk it and to carry it into what this step hands on, deciding nothing about it — the naming to the operator is the final report's and the writing down is `slices.md`'s.

**Where the set is empty this step offers nothing, and that is an outcome rather than a failure.** Several causes reach it and they are not reported alike; the list below is what has been identified, not a proof that nothing else can empty this set. A run reaches it by every proposed target having been declined, or by no group having been confirmed at all (Phase 2) — an operator who read a proposal naming each row's donor and said no has answered the question the run asked; report every candidate as left with its donor, and continue. It reaches it the same way where **every confirmed target was dropped in Phase 3**, the operator having cancelled mid-key-taking: nothing was created, so nothing can receive, and each candidate is again left with its donor. Or it reaches it because **Step 1's offer already wrote every placed candidate**, which is not that outcome at all: report it as the completed bulk write it is, over the rows Step 1 named. In every case **no stop is taken here, and this command has no no-receiver stop to take** (Phase 0 step 9a). Phase 3 can always key a new slice, so the state in which nothing could ever receive these rows is not one this command can be in.

**Per row, one `AskUserQuestion`, never batched**, quoting the following, each cell decoded (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.3) as every read of the route's tables is:

- the row's `id` and `text` from **this BRD's own** `brd/brd-inventory.md` — the file that holds every `[BR#n]` whatever fate this BRD's walk gave it (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.1), never the donor's copied inventory, which Step 3 is about to withdraw the row from;
- **the donor's key**, and the two dispositions that make the row movable at all, **quoted from the two ledgers rather than asserted**: this BRD's row reads `covered-by: <A-KEY>`, and A's own row for that `[BR#n]` reads `deferred-to: <A-KEY>`. Phase 0 step 9a read both to build the candidate set; showing them is what lets the operator see the refusal the move is made against (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2);
- **the receiver `<B-KEY>`** the Phase 2 confirmation fixed for this row's group, and whether it is a slice this run keyed or a child that already stood;
- **every decision in the donor's `decisions.md` whose `evidence` list touches this row**, by `id` and `statement`, a torn write (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §8) never among them. **"Touches" resolves in two hops and neither is a guess**: a decision's `evidence` holds `[CG#n]`/`[DG#n]` ids (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1), and a finding's `claim` is the `[BR#n]` premise it was derived against (`workflows-core:grounding-format` §2), so a decision touches this row where any finding in its `evidence` list carries this `[BR#n]` as its claim — resolved against the donor's own grounding files. **In the shape Phase 0 step 9a calls ordinary the donor has not been interviewed, so its `decisions.md` does not exist at all** — `/product-workflows:brd-interview` is what writes one — and an **absent** register is the same outcome as a present one matching nothing: report the donor as holding no decision touching this row. It is **not** a read failure of the kind step 9a requires reporting for an unreadable ledger, and must not be reported as one. A donor holding no such decision either way is reported as holding none, never omitted.

**That report is advisory, and nothing in this step edits a decision.** The decisions it surfaces record the donor's refusal to build this row, and the move does not disturb that refusal — it acts on it. `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4 admits exactly two causes for reopening a decision, a new grounding finding or an incoming customer decision, and a re-cut is neither; `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2 fixes that the donor's register and its grounding files are untouched by all of this. What the report buys is the operator's judgement: they see what the donor said about a row it is giving up and decide whether the move is still right.

**The picker**, one per row, two options:

```
choices: ["Re-point to <B-KEY> — <A-KEY> deferred it and <B-KEY> will build it<recommended>", "Leave it with <A-KEY> — its deferred-to stands"]
```

`<A-KEY>` is this row's donor, `<B-KEY>` the receiver the placement fixed for it, and `<recommended>` takes the form the first row of Step 2's table already defines — ` (Recommended — <what in the instruction placed it>)` on the re-point option and the empty string on the other. **That table's third row does have a case here, and it is the case a fabricated annotation would ruin.** A candidate reaches a confirmed group either because Phase 1.5's reading placed it there or because the operator moved it there by hand in Phase 2 — and for the second, **nothing in the instruction placed the row**, so `<recommended>` resolves to the **empty string on both options**, exactly as that row prescribes. Never write ` (Recommended — <what in the instruction placed it>)` over a row the instruction did not place: the annotation's whole value is that the operator can disagree with a reason they can see, and an invented one is worse than none. **The receiver need not be a slice Phase 3 keyed**, which is the one way this differs from that row's wording: where Phase 2 fixed a standing child as the target, an annotation the instruction does earn still names what in it placed the row, because that is what the annotation is for. All three are **placeholders substituted per row**, which is what keeps the array presented verbatim (`workflows-core:escalation-rules`, *Choice lists are presented verbatim*) — the same point Step 2 makes for its own picker, and the reason the variation lives in a placeholder rather than in an instruction to reword an option.

**A free-text or otherwise unusable answer falls to the second option — leave it with the donor.** The fall-through must always be the answer that writes least, which is the rule Step 1 applies at both of its own prompts, and here the least-writing answer is also the one that changes nothing: the row keeps a fate two ledgers already agree on.

**The writes, per row, once the operator chooses to re-point — in this order:**

1. **The parent's ledger row** (this BRD's own `coverage-ledger.md`) → `disposition: covered-by: <B-KEY>`.
2. **The donor's ledger row** (A's `coverage-ledger.md`) → `disposition: covered-by: <B-KEY>`.
3. **Every *other* standing child's ledger row for this same `[BR#n]` whose `disposition` names the donor** → `disposition: covered-by: <B-KEY>`.

`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2 is the authority for the first two writes and for the precondition behind them, which is not restated here; it also fixes the outcome the third write exists for — that no ledger is left naming the donor for a row the donor no longer holds — and leaves which ledgers are read, in what order, and how the sweep is reported to this step. **The order of the first two is stated at the point of use because it is not a tidiness question and a later edit will otherwise swap them as a clean-up.** Parent-first leaves a run interrupted between them with the parent pointing **one hop** at the receiver and the donor exactly as it stood — two accurate readings, neither hiding a requirement. **Nothing completes the donor's write later**: the next run's Step 3 withdraws the donor's claim and leaves its row reading `deferred-to`, which is an orphan row §6.1 counts through this BRD's row, and reports it (Step 3's case list). Donor-first leaves the parent naming A while A names B, a **second hop** under a roll-up §6.1 requires to terminate in one, which falsifies that section's own argument for as long as the run stays interrupted. Nothing else about either row changes, and ids are the parent's throughout.

**The third write is a sweep, and it is the sweep Phase 4.5 already specifies rather than a new one.** A single `[BR#n]` can be named by `covered-by` on **more than one** child's ledger: a child D whose provisional claim on that row an earlier run's walk withdrew holds an orphan row `covered-by: <A-KEY>` for it (Step 3's table), so the donor is named by D as well as by this BRD. Re-pointing only the two rows above leaves D naming A while A names B — a **second hop** under a roll-up §6.1 requires to terminate in one, landing on a row that no longer claims the requirement, which is the reading that section counts `unresolved` rather than follows. So read **every other standing child's** `coverage-ledger.md` for a row whose `disposition` is `covered-by: <A-KEY>` for this same `[BR#n]` and write `covered-by: <B-KEY>` on it. **That is the same read Phase 4.5 performs before a removal, over the same set of ledgers and for the same reason — a `covered-by` key about to go stale**, and it is reused rather than restated: read the `disposition` column, never a `claims:` list or an inventory, because the row that would dangle is an orphan row and a `claims:` list by definition does not name one. Where the read finds no such row anywhere, nothing extra is written — which is every re-cut of a row no earlier walk ever withdrew a provisional claim on, and it is reported as a sweep that re-pointed no row rather than left unsaid.

**The receiver is excluded from that sweep by construction, not by an exclusion rule** — and this is where the two Phase 0 clauses pay for each other. Step 9a's second per-row clause makes a child already holding a ledger row for this `[BR#n]` ineligible as its receiver, so B holds no row for it at all and the sweep can never write a self-naming `covered-by: <B-KEY>` onto B's own ledger — the mirror of the self-naming write the donor clause prevents. Nor can it reach the donor's row twice: that row is written by the second write above and is not *another* child's.

**The sweep runs third, after both rows above, and the reason is the same interruption argument.** Interrupted between the donor's write and the sweep, D's row resolves one hop onto A's row, reads a `covered-by` there, and is counted `unresolved` (§6.1) — visible as something to look at, and hiding no requirement, which is the whole of the claim. **It is not self-healing**, and saying so would be wrong twice: a later re-cut cannot reach it, because this BRD's row now reads `covered-by: <B-KEY>` and B is not `deferred-to: <B-KEY>`, so step 9a's candidate test fails on it; and a removal repairs D's row only where the child removed happens to be the donor. The repair is re-running the interrupted write, and that is what the visibility buys. Sweeping first would leave D naming a receiver that nothing had yet given the row to, while the parent and A both still said A owned it: a positive claim about B made before it was true, which is the one shape this route treats as worse than an unresolved count.

**What this step does not write, stated because each is somewhere an implementer would reasonably reach.** It does not touch the donor's `brd-link.md` `claims:` list or its copied inventory row — **Step 3 withdraws those**, exactly as it does for any row a walk moved off `covered-by: <that child>`. It does not touch the receiver's `claims:` list, its copied inventory row, or the `unallocated` ledger row seeded for it — **Step 3 settles those**, on this path as on any other, which is *adding* them where the receiver is a standing child and *reconciling* them where it is a slice Phase 3 keyed this run, since Phase 3 steps 3–5 already wrote all three for that one provisionally. And it touches **no grounding file and no decision register**, at either level. **The sweep above is not an exception to any of that**: it writes a `disposition` on another child's *ledger* row, which is the same kind of write as the two above it, and it leaves that child's `claims:` list and inventory alone — a child holding an orphan row for this `[BR#n]` does not claim it, so there is nothing there to withdraw.

**Report, per row walked:** the `[BR#n]`, the donor, and either the receiver it was re-pointed to or that it was left with its donor, plus the decisions surfaced for it, plus **every other child's ledger row the sweep re-pointed for it**, named by that child's key — or that the sweep found none to re-point. Add every candidate this step passed over — unplaced, or its target dropped — named with the donor it stays with. Phase 5 writes the same record into `slices.md`.

### Step 3 — reconcile each surviving child

**Once every row is resolved — by Step 1, by Step 2, by Step 2R, by a combination, or, on the reconcile path, before this run began — bring each surviving child's three
files back into agreement with this BRD's ledger (`split_mode: full` only — an `allocate-only` run has no child to
reconcile and finishes at the last row).** The
walk is what actually allocates, so a child's `claims:` list, its `brd/brd-inventory.md`, and its
`coverage-ledger.md` are all provisional until this point. For every child still standing — created
this run in Phase 3, or found already nested by Phase 0 step 9's positive test, **whatever this walk
did or did not do to it** —
re-derive all three from the rows this BRD's ledger reads `covered-by: <that child>` when this step
opens: the `claims:` list, the copied inventory rows (`brd-format.md` §2.1), and one `unallocated`
ledger row per claim. **"Re-derive" means reconcile, not rebuild from scratch, and a child already
in step is written nothing** — Phase 0 step 9's reconciliation test, taken again here over the
ledger as the walk left it. This walk visits **two** kinds of row and no others: rows that were `unallocated` when Phase 0 step 8 read the ledger, and — on the re-cut path — the candidate rows Step 2R re-pointed, which were never `unallocated` this run and reach this step already carrying `covered-by: <B-KEY>` at both levels. Everything else a pre-existing child was given by an earlier run is not revisited by the walk and must not be dropped here: the set each child
ends with is every row this ledger reads `covered-by: <that child>` — the rows it already claimed that
are still delegated to it, and the rows this walk newly resolved to it — and no row this ledger now
settles anywhere else. A rebuild
from this walk's resolutions alone would silently strip every earlier claim. **That conclusion is unchanged by the re-cut's widening and is what that widening is for**: a re-pointed row is one this walk newly resolved to the receiver and one it moved off `covered-by: <the donor>`, so both halves of the union reach it — the receiver gains the claim and the donor loses it — where a set defined by `unallocated` alone would have left the receiver claiming nothing it was given and the donor claiming a row it no longer holds. A row added to a child
here gains its inventory and ledger rows here, written as Phase 3 steps 4 and 5 write them, the receiver on the re-cut path included, whether that receiver is a slice Phase 3 keyed this run or a child that already stood (Phase 3 step 3).

**The selector reaches every standing child, and two states show why a narrower one fails.** The re-cut's **donor** is a pre-existing child this walk took a row *from* and gave none *to*, so a selector reading only *"given a row by this walk"* skips it — and the withdrawal below would then never run against the one child that most needs it, leaving a `claims:` entry and a copied inventory row for a `[BR#n]` whose own ledger row reads `covered-by: <B-KEY>`. **A child an earlier carve left out of step** is the second: a run stopped between its walk and this step leaves a provisional claim the next run's walk may settle elsewhere, or a row its walk gave the child that its inventory never received, and the next run's walk need not touch that child at all — so a selector keyed on *this walk's* moves never visits it, in either direction. In both, a slice's inventory is defined as the subset its `claims:` list names (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1), so the two stale files agree with each other and disagree only with this ledger — which is why the tests that catch the state, Phase 0 step 9's here and `/product-workflows:prd-ground` step 6a's, read this ledger rather than the two files. Left alone it surfaces later as a slice claiming work it does not own. Reconciling every standing child against this ledger covers both, and costs nothing on a child already in step.

**What the wider selector reaches, case by case, because it now reaches children no walk of this run touched:**
- **A child in step** — every child a completed run left standing, interviewed or not. Nothing is written for it, so nothing it has committed is touched.
- **A child an earlier carve left out of step.** Its `claims:` entries and inventory rows are added or withdrawn to match this ledger; a row added gains its ledger row as Phase 3 step 5 writes one, unless the child's ledger already holds one for that `[BR#n]` still `unallocated`, which is that row; and a withdrawn claim's ledger row — still `unallocated`, seeded by that earlier run's Phase 3 step 5 — takes the orphan table's disposition below.
- **A child still claiming a row this ledger delegates to it, whatever its own row for it reads save `covered-by`** — in step for that row, so nothing is written, and its own row stands. That is every settled slice's ordinary state, and after a `/product-workflows:brd-intake` re-run over this BRD it is how a slice takes back each claimed row this walk gives it again: nothing it had settled is stripped.
- **A child still claiming a row its own ledger reads `covered-by` for, where this ledger does not delegate that row to it** — a withdrawal an earlier run of this step never finished (Step 2's *Assign to a named slice* says how it arises). This step finishes it rather than leaving it half-done: withdraw the `claims:` entry and the copied inventory row, and leave the ledger row as it stands, which is exactly the donor's share of a re-cut this step performs on any run. The row is then an orphan row by §2's own test (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2), the second route's, with nothing moved back to `unallocated` (§3), and §6.1 counts it through this ledger's current disposition for that `[BR#n]`, so a `covered-by: <B-KEY>` an intake reset has since overtaken is counted by what this ledger now says. Where this ledger itself delegates the row to that child — reachable only by a hand edit, or on a ledger written before this exclusion, since every walk bars it — write nothing: the two ledgers disagree about who owns the requirement, and only the operator can say which is right. **Where this step runs, report the row in the Final Report; it may not run.** In this state the child's `claims:`, its inventory and this ledger's `covered-by: <that child>` rows agree, so Phase 0 step 9's reconciliation test finds it in step, and a bare run with nothing else to do is the no-op. The row is not hidden for that: this ledger's line, which every run of this command that reaches its Final Report prints — the no-op included, though not a run Phase 0 stops — resolves `covered-by: <that child>` one hop, lands on a child row reading `covered-by` for a row its parent delegated to it, and counts it `unresolved` as malformed (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §6.1).
- **A child whose own ledger already settled a row this step would change** — a terminal disposition on a row this ledger no longer delegates to it, or an orphan row for one this ledger now delegates to it. The first is reached only where this BRD's allocation moved after the child settled the row, and three states do that: the re-cut, whose donor row Step 2R has already written (below); a re-cut **interrupted between Step 2R's first write and its second**, which leaves this BRD's row reading `covered-by: <B-KEY>` and the donor's own row still reading `deferred-to: <the donor>`, the donor's claim standing, for the next run's Step 3 to meet; and a `/product-workflows:brd-intake` re-run over this BRD, which resets every row here to `unallocated` for this walk to re-allocate (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3). **In the interrupted re-cut the donor's row stays `deferred-to` too, and this step does not complete Step 2R's second write**: from this ledger and the donor's it cannot tell that state from an intake re-run whose walk gave the row to B, and in either the row it would overwrite records a decision the donor's own walk wrote. Nothing is hidden by leaving it: once the claim is withdrawn the row is an orphan row, which §6.1 counts through this ledger's current disposition — `covered-by: <B-KEY>`, resolved one hop into B — whatever the row reads. A child row that named the donor, which Step 2R's third write would have re-pointed, is an orphan row counted the same way. **The second is written by no walk**: Step 2's *Assign to a named slice* and Step 1's bulk set refuse a child holding an orphan row, or a claimed row reading `covered-by`, for that `[BR#n]`, and Step 2R refuses a receiver holding any row for it, so only a ledger edited by hand, or one written before that exclusion, can bring it here. Reconcile its `claims:` list and inventory as for any other child, and **leave that ledger row exactly as it stands** — this step never rewrites a disposition another run recorded and never writes `unallocated` over a terminal row — and report each such row in the Final Report by child, `[BR#n]` and the disposition left standing: the child's own ledger records a decision about a row whose allocation changed under it, and only the operator can say what that decision is now worth.
- **A child Phase 0 step 9 marked unreconcilable** — its `brd/brd-inventory.md` or `coverage-ledger.md` missing or unreadable. Write nothing into it and report it by name, with the file it is missing or cannot read. A missing file was either never written or lost after it was written, and re-seeding a lost ledger would write `unallocated` over whatever that child's own walk had settled. No walk of this run gave it a row, since it is no target and no donor (Phase 0 step 9); a row it claims that this walk settled elsewhere keeps its `claims:` entry here, a state `/product-workflows:prd-ground` reads off this ledger rather than off that list. Name `/product-workflows:prd-ground <CHILD-KEY>` as the command whose stops tell those states apart and name the repair — `PRD_GROUND_NO_INVENTORY`, `PRD_GROUND_NEEDS_SPLIT`, `PRD_GROUND_RESTORE_FROM_DEFAULT` and `PRD_GROUND_SLICE_FILE_UNREADABLE` among them.

**A row proposed for a child in Phase 3 but resolved elsewhere loses two of the three, never all
three.** Its `claims:` entry and its copied inventory row are withdrawn together — a slice's
inventory is the subset `claims:` names
(`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1) — and **its ledger row stays**, because a
ledger row is never deleted (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2). It
stays as an **orphan row**, and this step writes it the terminal disposition this BRD's ledger now
records for the row — the one this walk settled, or, on the reconcile path, where no walk ran, the
one that ledger already read when this step opened — so it never blocks that slice's own §4 gate:

| This BRD's ledger reads for the row | Write on the withdrawn child's ledger row |
|---|---|
| `covered-by: <another child of this BRD>` | `covered-by: <that child's key>` — a **sibling** of the withdrawn one |
| `covered-here` — this BRD builds it | `covered-by: <this BRD's key>` — the **parent** |
| `deferred-to: <this BRD>` | `covered-by: <this BRD's key>` — the **parent** |
| `rejected: [DEF#n]` | `rejected: [DEF#n]`, verbatim |
| `superseded-by: [BR#n]` | `superseded-by: [BR#n]`, verbatim |

`coverage-ledger-format.md` §3 owns that mapping and says why each row of it is the only honest
record available: the first three all say *another BRD owns this*, which is what `covered-by`
means, while `deferred-to: <this BRD>` written on the slice would falsely book the requirement as
that slice's own live obligation. The last two cite an id of **this** BRD's — the `[DEF#n]` in this
BRD's defect log, the `[BR#n]` in its inventory — which the withdrawn child resolves one hop up like
any other inherited id (`${CLAUDE_PLUGIN_ROOT}/references/brd-format.md` §2.1, §4), so neither names
something it cannot follow even though it no longer claims the row. **No key written here is ever a
child of the slice** — it is a sibling under this BRD, or this BRD itself — so nothing about this
widens the one-level cap.

Nothing is renumbered — ids are the parent's throughout — and a ledger row an earlier run already
moved off `unallocated` in a pre-existing child is left exactly as it stands: this step adds and
removes `claims:` entries and inventory rows, it **never removes a ledger row**, and it never
rewrites a disposition another run recorded. The orphan rows it writes are only ever rows still
`unallocated` — seeded by Phase 3 step 5 moments earlier, or by that step of an earlier run that
stopped before its own Step 3 — so the two rules never collide: a row already terminal is left as it
stands, per the case list above.

**On the re-cut path this step writes one further row, and it collides with neither rule either — but only because Phase 0 bought that.** Where the receiver is a **standing** child, the `unallocated` ledger row for the re-pointed `[BR#n]` is written **here**, onto a ledger that already existed, since Phase 3 wrote nothing for a child it did not key (Phase 3 step 3). That is a **new** row on an old ledger, not a row moved backwards: step 9a's second per-row clause makes a child already holding a ledger row for a candidate's `[BR#n]` ineligible as that row's receiver, so this write can never land on an existing row and can never return one to `unallocated` (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2, §3). **The rule above is therefore left-alone-as-it-stands and not leave-every-pre-existing-row-alone**, and the difference is exactly where the strandable state used to be: a receiver holding a terminal row for the moved `[BR#n]` would gain a `claims:` entry here while its own row named somebody else, its `allocate-only` walk would never visit that row, and nothing anywhere would fail. It is unreachable because the receiver set excludes it, never because this step declines to write.

**On the re-cut path the donor's ledger row is the row a reader will expect this step to write, and it does not: Step 2R already wrote it, so this step leaves it alone.** The withdrawal Step 2R described is still performed here — the donor's `claims:` entry and its copied inventory row go, together, exactly as for any row this walk moved off `covered-by: <that child>` — but its **ledger row is not written a second time**. It already reads `covered-by: <B-KEY>`, which is what the orphan table's first row above prescribes for a row this walk resolved to another child of this BRD, so nothing here would change it and nothing disagrees. **That is also what keeps "never rewrites a disposition another run recorded" intact**: the disposition on that row was written by *this* run, one step earlier, and this step declining to touch it is the reason no earlier run's record is ever at stake. So on this path the donor's work in this step is the `claims:` entry and the copied inventory row only.

---

## Phase 4.5 — Resolve every standing empty child

`split_mode: full` only — `allocate-only` has no children and can create none.

**A child claiming nothing is a folder nothing on this route can act on.** It has an empty
`brd-link.md` `claims:` list and, beside it, a `brd/brd-inventory.md` holding its header and no
row. **Its
`coverage-ledger.md` is not necessarily empty**: a child keeps one orphan row per withdrawn claim
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2), each already terminal, and every one of
that section's three routes to an orphan row reaches this set — a child Phase 3 created this run whose every
proposed row the walk then resolved elsewhere, a pre-existing child whose every committed claim a
re-cut moved to a sibling, and a pre-existing child whose every claim this walk settled elsewhere
after a `/product-workflows:brd-intake` re-run over this BRD reset its rows. Those
rows change nothing here — the emptiness this phase acts on is the **claims** list. The
empty-inventory stops of `/prd-ground`, `/brd-split` and `/brd-interview` each count the child's
inventory rows rather than read that list, but the inventory is derived from the claims (the
reconcile step above), so an empty list is what leaves them no row to count; those stops name
**this phase** as the fix, as do the other stops and offers on this route that
meet such a child, so this phase has to be reachable whenever such a child exists.

**The set is every child standing now, not only the ones this run created.** Four things put a child
in it: a slice keyed and folder-created in Phase 3 whose every proposed `[BR#n]` row ended this walk
resolved to something other than `covered-by: <that child>` — rejected, deferred, superseded, or
reassigned; a child an *earlier* run left standing, which Phase 0 step 9 marked; — on the re-cut path — a **donor** whose last remaining claim Step 2R moved to a sibling, which step 9 did not mark and could not have, since it still claimed a row when that step read it; and a pre-existing child whose every remaining claim Step 3 withdrew because this ledger now settles it elsewhere — a provisional claim an interrupted earlier carve left, or a claim a `/product-workflows:brd-intake` re-run over this BRD reset and this walk gave to another slice or a fate of its own — unmarked by step 9 for the same reason. **Scoping this
to children created this run was a dead end**: an earlier run's kept-empty child was never in any
later run's set, so the removal option existed only in the single run that created it and never
again. (The Phase 3 cancelled-mid-keying case is distinct and is not in this set — that slice never
got a folder at all.)

**Emptiness is recomputed here, after the walk, and Phase 0 step 9's marking is never the set this phase acts on.** Read each standing child's `brd-link.md` `claims:` list **as Phase 4's Step 3 reconcile left it**, and take only the children whose list is empty then. Step 9's marking is an input to the step 10 no-op decision and nothing more, and on the re-cut path it goes stale inside the same run: a child from the **eligible receiver set** is eligible precisely because it has not been interviewed, and an **uninterviewed** standing empty child is one of those — an interviewed one is not, which is why Phase 0 step 6's own stop tells such a slice it can only be removed or kept — so Phase 2 may fix an uninterviewed one as a group's target and Step 2R may give it a row — after which Step 3 writes it a `claims:` entry, an inventory row and an `unallocated` ledger row, and it is not empty any more. Trusting step 9's marking there would offer to delete a folder this run has just given work to, taking the row's new ledger row with it. **The recomputation costs nothing on the other paths and is not conditional on `recut_mode`**: on an ordinary run Step 3 reconciles every standing child and the recomputed list is what that step left, and on the reconcile path no walk ran but Step 3 did, so the list read here is step 9's with every out-of-step child reconciled — a child this ledger delegates a row to while it claimed nothing, such as the receiver of a re-cut cancelled before its Step 3, now claims that row and is not in this set, and a child whose only claims were stale now claims nothing and is. The reverse direction holds too and is the reason this is a recomputation rather than a subtraction: a child step 9 did **not** mark can end the walk empty — every row it claimed moved off `covered-by: <that child>`, which is exactly what a donor whose last claim was re-cut looks like — and it belongs in this phase's set on the strength of the list, not of the marking.

**Two pickers, because a child kept by a decision is not the same as one nobody has looked at.**
Read the child's `brd-link.md` for a `reason:` field:

**No `reason:` recorded** — nobody has yet decided this folder should exist while claiming nothing:

```
choices: ["Remove the empty child folder — it claims nothing (Recommended)", "Keep it, and record why (e.g. reserved for related future scope)"]
```

**A `reason:` already recorded** — an earlier run asked this question and the operator answered it.
Do not re-ask it as though it were open, and do not recommend undoing a decision on the strength of
a state that decision deliberately created. Print the recorded reason verbatim beside the list.
**A recorded reason can be stale in one specific way, and where it is, say so beside it rather than presenting it as a standing answer.** A child kept empty against a reason is uninterviewed, so it is an eligible receiver: a later run may fix it as a target and Step 2R may give it a row, at which point the recomputation above correctly drops it from this phase's set and its `reason:` — which describes a folder claiming nothing — is left describing a state it is no longer in. Nothing rewrites it there, because keeping the operator's own words is the point of the field. If that child later empties again and reaches this picker, the reason on file was answered about a different situation: print it with the note that the child has since been given a row and emptied again, so the recommendation to keep is read for what it is rather than as the earlier decision still standing:

```
choices: ["Keep it — the recorded reason still stands (Recommended)", "Remove it now — it claims nothing, and nothing on the route can act on it", "Update the recorded reason"]
```

Removing deletes the child's folder — `brd-link.md`, `brd/brd-inventory.md`, and
`coverage-ledger.md` with it — and drops it from any later run's Phase 0 step 9 enumeration.
Removal is the one place a ledger goes away, and it
takes the whole BRD with it rather than deleting a row from a ledger that survives — which is why
it does not contradict `coverage-ledger-format.md` §2.

**A removal can now leave a `covered-by` key pointing at nothing, and the re-cut is what made that state reachable.** This phase used to assert the opposite and reason it from the walk: a child this walk gave a row to claims that row and is therefore not in this phase's set, so no ledger anywhere could name a child this phase can remove. **That reasoning held only for as long as no row could be moved off a terminal disposition**, and the re-cut moves one. The route to the dangling key is four runs long and every step of it is ordinary: a child B takes a row this walk resolved `covered-by: <B>`, some earlier child A having had its provisional claim on that row withdrawn and its own ledger row written `covered-by: <B>` (Step 3's orphan table); B's own `allocate-only` walk later records `deferred-to: <B>` against it; a later run re-cuts it onward to a sibling, which rewrites this BRD's row and B's row and withdraws B's claim (Step 2R, Step 3); B now claims nothing, is in this phase's set on the recomputation above, and **A's ledger still reads `covered-by: <B>`**. Removing B without more would leave A naming a folder that is not there — an `unresolved` row for every later reader of A's ledger line (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §6.2), on a BRD that did nothing wrong.

**The second route reaches this BRD's own ledger, and it is stated because the obvious reading says it cannot be reached.** That reading is that Step 3 keeps a child's `claims:` list in step with the rows this BRD's ledger allocates to it, so a child claiming nothing implies no row of this ledger names it — and it holds only for a run that **reaches Step 3**. The re-cut moved the receiver's `claims:` write out of the walk and into that step, and a `Cancel` mid-walk is sanctioned between the two (Step 2, Step 2R): a run can re-point one candidate onto an uninterviewed standing empty child B, write `covered-by: <B>` on this BRD's row and on the donor's, and then be cancelled on the next candidate before Step 3 ever gives B its `claims:` entry. **The rows Step 2R already wrote stay written**, which is that Cancel's own stated behaviour. B still claims nothing, and this BRD's ledger now names it. **Step 3 now closes this route on every path that reaches this phase**: the next bare run finds a fully-allocated ledger and B out of step, takes the reconcile path, and Step 3 gives B the `claims:` entry, inventory row and ledger row the cancelled run never wrote, so B is not in this phase's set and is never offered for removal with **this BRD's own row pointing at it**. The one child Step 3 does not reconcile is one Phase 0 step 9 marked unreconcilable, and that is the only way this BRD's own row can still name a child this phase offers to remove — where it does, removing it without the write below would leave that row `unresolved` on this BRD's own ledger line, which is the same failure the other-child repair exists to prevent, one level up.

**So read before removing, at both levels — the other children's always live, this BRD's own reached now only through an unreconcilable child.** Before deleting the folder, read this BRD's own `coverage-ledger.md` for rows whose `disposition` is `covered-by: <that child's key>`, and read **every other standing child's** `coverage-ledger.md` for rows carrying the same key. Read the `disposition` column, never a `claims:` list or an inventory — the row that dangles is a row, and on another child it is an orphan row its `claims:` list by definition does not name.

**Where any such row exists, name it in the removal confirmation before the removal is taken**, with its `[BR#n]`, the ledger it sits on, and what that row will be rewritten to. The two pickers above are unchanged and no option is added: this is prose beside the list, printed exactly where a recorded `reason:` is already printed, because the operator answering *remove* is being told that removing this folder rewrites rows on ledgers other than its own — which nothing in either list implies.

**On removal, write, and take both mappings from `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3's orphan table rather than restating them here** (§3.2 quotes that table for exactly this edge): each such row of **this BRD's own** ledger takes `deferred-to: <PARENT-KEY>` — this BRD's own key, which on its own ledger is §3's `deferred-to: <this BRD>`, a live obligation kept and not built now — and each such row of **another child's** ledger takes `covered-by: <PARENT-KEY>`. **Not back to the child that donated the row**, which recorded that it will not build it, and **not `unallocated`**, which this command never writes onto a row already carrying a fate (§3), so §4's gate is never reopened by a removal. Nothing else on any ledger changes and no ledger row is deleted.

**Every one of those writes lands before the folder is deleted, and the order is stated at the point of use for the same reason Step 2R states its own: an interrupted run must not be left hiding a requirement, and a later edit will otherwise reorder these as a clean-up.** Delete-first, interrupted before the writes, leaves exactly the dangling state this repair exists to remove — a key naming a folder that is not there, with nothing left on the tree to say which folder it was. **Writes-first, interrupted before the deletion**, leaves every affected row already re-pointed at this BRD and an empty child folder still on disk: every reading is accurate, nothing is hidden, and the next run enumerates that folder in Phase 0 step 9, finds it claiming nothing, and offers the removal again — with the read above now finding no row to re-point, which is the "nothing found, nothing written" case below. That run is self-healing where the other order's is not.

**Where no such row exists anywhere, the original claim still holds for that removal and nothing extra is written** — which is every removal on a tree no re-cut has ever touched, and not "every removal on an ordinary run": both routes above run their course across several runs, so the run that meets the dangling key is rarely the run that created it. That is the reason this repair is stated as conditional rather than as a new unconditional step: a read that finds nothing writes nothing, and reporting it as a removal that re-pointed no row is the honest form of the guarantee this phase used to assert outright.

Keeping it, meanwhile, writes or leaves a
one-line `reason:` field in its `brd-link.md` beside the empty
`claims:` list, and leaves the empty inventory and the ledger — orphan rows and all — in place, so
the folder is still a well-formed BRD rather than a half-built one. Either way, Phase 7's next-step recommendation never
offers to ground a child still claiming nothing.

**What this phase cannot do, said plainly so no stop promises it — and the boundary is narrower than it once was.** **This phase gives no child a row.** `covered-by: <child>` is written by Phase 4's walk and by nothing else, in one of two places: **Step 2**, against a row that is `unallocated` on this BRD's ledger, and — since the re-cut — **Step 2R**, against a row the child holding it has recorded `deferred-to` against in its own ledger (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). Both are the walk's, both run before this phase opens, and neither is reachable from a picker here.

**What that changes is the sentence about a fully-allocated parent, and it is a claim about this phase rather than about the run.** Removal, or keeping the child knowingly, is the whole of what **this phase** offers — that is unchanged and is what the stops elsewhere on this route are asking for. It is **no longer** the whole of what a **run** on a fully-allocated parent can do: an instruction typed on that run selects the re-cut (Phase 0 step 9a, step 10), and a row moved there can land on a standing child this phase would otherwise have offered to remove — which is why the set above is recomputed after the walk rather than taken from step 9. A stop that promises a slice only removal-or-keep is promising less than the command does; a stop that promises the re-cut owes the two conditions it depends on, that such a row exists and that this slice has never been interviewed. This command's own such stop (Phase 0 step 6) says both.

---

## Phase 5 — Write `slices.md`

Write `<BRD-dir>/slices.md`:

- **One block per slice** confirmed and keyed in Phases 2–3: its key, its folder, and the
  rationale — what in the instruction placed it — that put its `[BR#n]` rows together rather than
  elsewhere or left on this BRD.
- **One block per row** Phase 4 resolved `deferred-to: <this BRD>`: its `[BR#n]` and the one-line
  rationale collected for it in Phase 4 — why it is a live obligation of this BRD rather than built
  now.

- **One block for the bulk resolution, when Phase 4's Step 1 offer fired and was taken** — the
  disposition it wrote, the `[BR#n]` rows it wrote it on, and the rows held back with why each was
  held back (named by the operator, or placed elsewhere by the instruction). A later reader needs to
  know whether forty rows were judged one at a time or confirmed once, and the ledger cannot say:
  the rows read identically either way. Where the offer fired and was declined, record that in one
  line too — a decision to walk is a decision.

- **One block for the re-cut, when `recut_mode` was true** — one entry per row in the re-cut candidate set Phase 0 step 9a built, carrying its `[BR#n]`, the **donor** it stood on, and either the **receiver** it was re-pointed to — with whether that receiver is a slice this run keyed or a child that already stood, and whether the write came from Step 2R's per-row picker or from Step 1's bulk offer — or the fact that it was **left with its donor**, with the reason. **The reasons are five, and the fifth is not a stage failure**: declined at Step 2R's picker; held back from Step 1's bulk offer and then declined; left unplaced by Phase 1.5's reading; placed into a group whose target Phase 3 then dropped; and — the fifth — **placed by Phase 1.5 into a group Phase 2 confirmed nothing of**, the operator having read a proposal naming each row's donor and declined it, or having edited the list down to nothing. Phase 2 calls that "a real outcome of a real run rather than a degenerate one" and Step 2R names it among the causes that empty its set, so it is recorded as the answer it is and never force-fitted into one of the four stage-based reasons, none of which describes it: nothing failed to place the row and nothing dropped its target — there was never a target to drop. **Every candidate appears, and a candidate this run did not move appears as exactly that** — a row nothing walked, whose fate two ledgers already agreed on — never as an omission and never as a gap. Record beside each the decisions the run reported for it, **by `id`**, from the donor's `decisions.md`, with the note that they were reported and not touched (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4, `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2), and a donor holding none named as holding none. Record beside each re-pointed row **every other child's ledger row the sweep re-pointed with it** (Step 2R's third write), by that child's key and `[BR#n]`, or that the sweep re-pointed none — the same argument as the removal block below: afterwards that row reads `covered-by: <B-KEY>` like any other orphan row, and nothing in the tree records that it was rewritten because the requirement changed hands. **The reason this block exists is the reason every other block here exists: the ledger cannot say it.** A row re-pointed to a slice and a row this BRD allocated to that same slice on its first pass read identically on both ledgers afterwards — `covered-by: <B-KEY>` and nothing else — so nothing in the tree records that a requirement changed hands, which slice gave it up, or what that slice had already decided about it. A later reader meeting B's inventory needs all three, and this file is where they are.

- **One block per child Phase 4.5 removed, on every path a removal can happen on** — its key, that it was removed for claiming nothing, and **every row the removal re-pointed onto this BRD**, by `[BR#n]` and by the ledger it sits on, **this BRD's own included**; or, where the read found none, that the removal re-pointed nothing. Same argument as every other block here: the ledger cannot say it. A row this repair moved reads `deferred-to: <this BRD>`, or `covered-by: <PARENT-KEY>` on another child, and both are dispositions an ordinary walk writes for ordinary reasons — so once the folder is gone nothing in the tree records that this row was written because a folder went away, or which folder it was. **The reconcile path is not the only path a removal happens on**: an ordinary run and a re-cut run both reach Phase 4.5, and on those two this block is the only durable record of the re-pointing, the rest being terminal output nobody keeps.

- **One block per child Phase 4's Step 3 reconciled although no walk of this run touched it** — its
  key, each `[BR#n]` added to or withdrawn from its `claims:` and inventory, and every ledger row
  Step 3 left standing for it (Step 3's case list). The ledger cannot say it: this BRD's own rows did
  not change, so nothing on them shows the child was out of step.

- **One block for the instruction, when this run was given one** — the instruction **verbatim**, and
  how it was read: which `[BR#n]` rows Step A placed directly, which the Step B grill settled and by
  what terminology decision, and which it could not place and left unclustered. Record it whether or
  not it produced a slice: a reading that produced nothing is the one a later reader most needs, and
  the verbatim text is what lets them see whether the instruction or the reading was wrong.
  **On the re-cut path this same block records that same reading over the re-cut candidate set**, which is the set Phase 1.5 ran over there — no second instruction block is written, and none is needed: one instruction was read once, and only the set it was read against differs.

- **One line for every frame set Phase 0 step 7, test b let through as `skipped: --no-design`**, naming the
  set. That is the one route by which a slice this run carves can reach build with a design nobody
  reconciled, and the operator who chose it per-run is not the reader who will meet the slice later.
  Where step 7, test b found nothing to record — no `design/` folder, or every set ground — write nothing
  here rather than a "none" line: this block exists to carry an exception. **On a `full` run there is
  never anything to write**, and that is not the same absence: step 7, test b does not run there at all
  (step 7 is `allocate-only` only), so this run checked no frame set rather than checking them and
  finding nothing to except.

A run that proposed zero slices still writes `slices.md`, with an explicit note that no slice was
proposed and why, plus every deferral this run recorded — the file is never skipped just because
nothing was carved off this BRD. **An `allocate-only` run reaches that same path from a different
cause** and needs no separate rule: Phase 2 never ran, so it has no slice block to write, and its
`slices.md` carries the Phase 0 step 5 notice as its "why" — this BRD is a slice, no child may be
created below it — followed by its deferral blocks.

Skipped entirely on the no-op path step 10 decides — nothing was walked, so there is nothing new to
rationalize. **Not skipped on the reconcile path**, where the ledger had no `unallocated` row
but a child was reconciled or a standing empty child resolved: a removal there takes a slice out of the tree, and a
`slices.md` still listing it would be the stale-record failure this route fixes everywhere else. On
that path this phase rewrites only what the removal and the reconcile changed — the removed slice's block goes, and the *"One block per child Phase 4.5 removed"* block in the list above is written in its place, and the reconcile block is written for each child Step 3 changed — and touches no other block.

**The re-cut path is not the no-op path, and this file is written on it in full.** Both start from a fully-allocated ledger and step 10 tells them apart on the candidate set, so the resemblance is exactly the trap: a re-cut run walked rows, may have keyed a slice, moved requirements between siblings, and resolved standing empty children, and every one of those is something a later reader needs the rationale for. Write every block that applies — slices, deferrals, the bulk resolution, the re-cut block above, the instruction — rather than the removal-and-reconcile rewrite the reconcile path takes.

---

## Phase 6 — Handoff

Invoke `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and present its §4.3 choice array verbatim — **two arrays, selected by the `deliverable_paths` set below, per §4.0's strongest-class rule.** Where that set holds any **slice-level** `coverage-ledger.md` or `brd/brd-inventory.md` — every path but the ones named next — present §4.3's **gated — stopping** array (§4.1 bullet 1), because `/prd-ground` stops on both (`workflows-core:phase-handoff` §3.4):

```
choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]
```

Where it holds **neither**, present §4.3's **advisory** array (§4.1 bullet 3) instead:

```
choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (no command stops on this; what reads it reads your working copy)", "Cancel"]
```

**The second branch is reachable and the run must not tell the operator otherwise.** It is the reconcile path on which Step 3 found no child out of step and every standing empty child was **kept**: Step 3 wrote nothing, Phase 5 rewrites `slices.md` only on a removal or a reconcile, and a keep that wrote or updated a `reason:` therefore leaves the whole set at that child's `brd-link.md` — which §4.0's register classes **advisory**, read by many commands — BRD-route detection in `/product-workflows:create-prd`, `/product-workflows:create-ard` and `/product-workflows:specify`, `/product-workflows:epics` step 1a and this command's own Phase 0 step 5 among them; `grep -l brd-link.md plugins/*/commands/*.md` lists every command that names it — and gated by none, carrying no §3.4 row at all. It is also the branch the empty sets take — the no-op path, and a keep that changed nothing — so the two branches are exhaustive over every set this phase can reach. Presenting the stopping array there would promise a refusal no command makes, and the run would then print §4.1's **advisory** clause against its own prompt: a run that contradicts itself minutes apart teaches the operator to trust neither half (§4.3). Note that a **root's** own `coverage-ledger.md` and `slices.md` are advisory too (§4.0's register distinguishes a root's ledger from a slice's), so a `full` root run that carved nothing and deferred every row to this BRD takes the second branch as well.

On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix: brd` (§2.9's
table already lists `brd` as shared by every `/brd-*` command), `feature_folder` as resolved
in Phase 0, `deliverable_paths` = every file this run wrote, updated, or removed under `<BRD-dir>`
— **in `allocate-only` mode that is this slice's own `coverage-ledger.md` and `slices.md` and
nothing else, because Phase 3 never ran — both on a run that walked, and neither on the no-op
path, which writes nothing** —
(this BRD's own `coverage-ledger.md`, `slices.md`; in `full` mode additionally, for every slice
still standing after Phase 4.5, the three files this run wrote into it — `brd-link.md`,
`brd/brd-inventory.md`, and its own `coverage-ledger.md`, the two that `/prd-ground` will gate and
read when the child re-enters the route — **which on the re-cut path includes a child whose only
changed file is its `coverage-ledger.md`**: the donor, whose row Step 2R re-pointed, and any other
standing child whose orphan row Step 2R's sweep re-pointed with it. Declare the file that changed,
not all three, and never the folder; and, for a child Phase 4.5 removed as empty, **those same
three paths again, named individually** —

**Name files, never the folder.** §2.9 requires one literal repo-relative path each and §2.3 stages a
directory for nothing — §2.3 step 4 names it in §4.1's *declaration unaccounted for* clause, so the
failure is reported rather than silent, but nothing it names lands. On a removal that failure is total: `git status
--porcelain -z` reports three ` D` records, a folder-shaped declaration matches none of them, so `slices.md`
and the parent ledger land on the default branch while the removal does not — and the next run's
Phase 0 step 9 re-enumerates the child as still standing. —
§2.3's `-A` staging is what stages a removal, exactly as it does for `/idea`'s or `/update-prd`'s
own deletions — and it stages a Phase 4.5 removal on the reconcile path the same way), `title:` — `<BRD-KEY> Split into slices and allocate coverage` in `full` mode,
`<BRD-KEY> Allocate slice coverage` in `allocate-only`, because a pull request titled "split" that
created nothing would misdescribe itself — and `body_facts` = the run mode,
the slice count and keys (`full` only), the walk's resolution tally by disposition, whether Phase 4's
Step 1 offer fired and — where it was taken — how many rows it wrote in one confirmation and how many
were held back to the walk, every standing
empty child Phase 4.5 resolved and how, whether this run was given a slicing instruction and — when
it was — how many rows its reading placed, settled by grill, and left unplaced, **whether this run
was the re-cut (`recut_mode`) and — when it was — how many rows were re-cuttable and from which
donors, how many were re-pointed and to which receivers, how many were left with their donor, and
how many other children's ledger rows the sweep re-pointed with them**, and whether this run
was the no-op; emit its §4.1 outcome
line in the final report. The no-op path reaches this phase with nothing staged, so it reports the
`nothing to commit` line rather than opening a pull request.

**Why the re-cut facts are in that list, when `slices.md` already carries the same record.** The two are not alternatives. `slices.md` is inside the diff this pull request proposes, and the body is what a specs-repo reviewer reads *before* opening it — a re-cut moves requirements between siblings and rewrites `disposition` rows on ledgers the title does not name, so a body enumerating the offer that fired, the empty children resolved and the instruction's reading while saying nothing about a transfer between two BRDs describes the smallest change in the diff and omits the largest. It is also the only path on which a standing child's `coverage-ledger.md` appears in `deliverable_paths` because a row that child had **committed** to — its own ledger reading `deferred-to` against it — was taken **off** it. Writes on the other paths take a row off a standing child too, and none is that: Step 3 can withdraw a claim that was only ever provisional (a slice keyed by a run cancelled mid-walk, whose still-`unallocated` row the next run's walk gives to a sibling), and Phase 4.5's removal repair rewrites another standing child's orphan row on the ordinary and reconcile paths — but the first moves a row the child never settled, and the second always accompanies a folder this run is deleting and the removal block reports it, whereas here a donor's ledger changes with nothing added to it and no folder gone — which reads as a stray edit to anyone who has not been told a requirement moved.

**The reconcile path is not that
path**: a removal there stages a folder deletion and the rewritten `slices.md`, a reconcile stages
the files Step 3 rewrote for each child and the rewritten `slices.md`, and a "keep" that
wrote or updated a `reason:` stages that child's `brd-link.md`, so it opens a pull request like any
other run. A run on it that reconciled nothing and kept every empty child unchanged stages nothing
and reports the same `nothing to commit` line.

---

## Phase 7 — Next steps

**`split_mode: allocate-only` — no child of this slice is reachable, so no grounding of one is
offered.** Phase 3 never ran, so there is no child to ground. This slice's ledger may still hold a
`covered-by` key — an **orphan row** naming a sibling or the parent
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2, §3), which the ledger line below
follows one hop — but neither is a child of this slice and neither is this run's to ground: each is
a BRD standing at its own level, on its own route. And this slice cannot be split further, so
re-running this command on it would only find a
fully-allocated ledger and report the no-op. **The route does not end here.** Its ledger now records
a fate for every requirement it claims, which is exactly the precondition
`/product-workflows:brd-interview <BRD-KEY>` — the route's decision step — refuses to start without, so
that is the real next step for this slice and it is offered by name. A slice reaches its own
decisions exactly as its parent does, and the register it writes is its own. If any row reached
`covered-here` the slice is also PRD-eligible
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5), which is one of the two tests
`/product-workflows:create-prd <SLICE-KEY>` applies in its own Phase 0 — the other being the level
test that refuses the `BRD-` container this slice sits inside. It is still not offered here, and the reason is the register rather than the ledger: that run
seeds its PRD from this slice's `decisions.md`, which `/product-workflows:brd-interview` has not written
yet, so starting it from here would author a PRD off an allocation and no decisions at all. The route crosses into the PRD pipeline from `/product-workflows:brd-reconcile`'s own next-step offer, once the customer answers are frozen — three commands further on — or, on a slice whose every question `/product-workflows:brd-interview` settles from the findings, from that command's own next-step offer, one command on; either way the register comes first, which is why only the next command is named here:

```
choices: ["Decide this slice's open questions — /product-workflows:brd-interview <BRD-KEY> (Recommended) <merge-clause>", "Stop here — this slice's allocation is complete"]
```

**`split_mode: full`** — everything below. Every child folder Phase 3 created, still claiming at
least one `[BR#n]` after Phase 4.5, **re-enters the route at grounding** — a slice is graded on its own claimed
requirements exactly as any BRD is, and nothing about being a slice exempts it from that. It can:
Phase 3 gave it the two files `/prd-ground` Phase 0 needs — a `coverage-ledger.md` to gate on and a
`brd/brd-inventory.md` to read — and Phase 6 staged both, so they reach `origin/<default>` with
this run's pull request. Grounding a child is possible only once that pull request has merged, and
`/brd-intake` is never the answer for a child at any point.

**The set is wider than that, and the offer means a different thing for each of three cases. Grounding is what separates them, and it is not what made any of these children eligible to receive a row.** Receiver eligibility is *not interviewed* — no `decisions.md` holding a `[VD#n]` or `[CD#n]`, no `interview/round-*.md` (Phase 0 step 9a) — and it says nothing about grounding, so **do not infer that a standing receiver has been ground**: a child an earlier run left standing and nobody ever ground is uninterviewed by construction, since `/brd-interview` gates on the grounding it does not have. Read each offered child's own state and say which case it is:

- **A slice Phase 3 keyed this run** — never ground, `/prd-ground <CHILD-KEY>` is its first pass. This is the case above, unchanged.
- **A standing child that has never been ground** — also a first pass, for the same reason and with nothing extra to explain. Its inventory simply grew by a row before it ever ran.
- **A standing child that is already ground** — the only re-run of the three. Its grounding no longer covers everything it claims: the row arrived after it, so no `[CG#n]` on file was derived against it, and the honest next step is `/product-workflows:prd-ground <B-KEY>` **again**. That re-run re-derives rather than inherits, which is `workflows-core:grounding-format` §8 working as designed and not an inconvenience to route around — a finding carried in from an earlier run is unverified by definition, so the donor's findings about this row cannot move to the receiver and the receiver's own earlier findings cannot vouch for a row they never saw. The cost is one row's re-derivation against the same pins.

**Say which case each offered child is when presenting the option.** Only the third is a re-run, and it is the one that needs its reason stated: the operator is being told to re-run a command on a slice they have already run it on, and a re-run whose reason is not stated reads as a mistake. Telling an operator their never-ground slice has stale grounding is the mirror of that mistake, which is why the case is read off the child rather than assumed from the fact that it was standing.

**So the option's set is every child that gained a row this run** — the slices Phase 3 keyed and still claiming at least one `[BR#n]` after Phase 4.5, and any standing child the walk newly resolved a row to, on the re-cut path or on an ordinary one, or Step 3 added a row to on any path, the reconcile path included — a reconciled child's inventory grew as surely as a receiver's. A child that gained nothing is not in it and nothing is offered for it:

```
choices: ["Ground each child that gained a row this run, one run per child — /product-workflows:prd-ground <CHILD-KEY> (Recommended) <merge-clause>", "Stop here — this BRD's own allocation is complete", "Split another BRD"]
```

**A donor that gained no row is not in that set and is not offered anything here — and that is the condition, not "being a donor".** It lost a row and gained none, so its remaining findings still cover everything it still claims, and the findings it holds about the row it gave up stay on file as a record of what it saw (`workflows-core:grounding-format` §8) — they are not stale grounding to repair, and re-running `/prd-ground` on it would re-derive work nothing asked for. **A donor that also gained a row is in the set like any other receiver**, which is reachable whenever two donors are involved: A's row lands on C while C's own row goes elsewhere, and C is then a child that gained a row and needs its grounding re-derived for it. Stating the rule as "a donor is never offered" would drop C out of the offer on the strength of a label. A donor left claiming nothing at all was resolved in Phase 4.5 and is not here either.

**Every merge clause in this phase is the `<merge-clause>` placeholder**, resolved per
`Skill(skill: "workflows-core:reference", args: "next-phase-offer")`'s *A next-step offer that names a downstream
command must also name the merge* rule, which owns the §4.1 outcome map and is not restated here.
The rule governs **every** mention of the merge in this phase — both choice arrays and the prose
below — because this command reaches three outcomes that open no pull request: the no-op, the
reconcile path where Step 3 wrote nothing and every standing empty child was kept unchanged, and a declined handoff. It is a
placeholder and not an instruction to reword an option, so the arrays are still presented verbatim
per `workflows-core:escalation-rules`.

**Say what the child's own route looks like when offering it**: after `/prd-ground <CHILD-KEY>`,
`/brd-split <CHILD-KEY>` runs in `allocate-only` mode (Phase 0 step 5) — it allocates that child's
ledger through its own four resolutions — the same count as `full`, a different set — and creates nothing below it. `/prd-ground`'s own
Phase 10 offers exactly that. A child removed, or kept empty with a recorded reason,
for claiming nothing (Phase 4.5) is never offered here — grounding a BRD with no requirement to
ground would have nothing to check a claim against. No child gained a row this run (none were created and none stood to receive one, every one created was removed
as empty, or — on the re-cut path — every proposed move was declined) → the child-grounding choice is the one that does not apply, stated plainly rather than
omitted — and is dropped from the array, not merely annotated, so that reaching for it does nothing.
**"Split another BRD" is always in the array for exactly this reason**: dropping the
child-grounding choice in that state would otherwise leave only "Stop here", one option short of
what `AskUserQuestion` accepts. **Naming no key, and never "or slice"**: this run's own children,
where any exist, are unground — `/brd-split <CHILD-KEY>` on one of them refuses outright with
`BRD_SPLIT_NEEDS_GROUNDING` until `/prd-ground` has run — so the option points only at a BRD
this run did not just create, never at the child it is discussing in the same breath. **A standing receiver is not an exception to that, on either of its two states.** Where it has never been ground, `/brd-split <B-KEY>` refuses it outright with `BRD_SPLIT_NEEDS_GROUNDING` exactly as a new child does. Where it *is* ground the refusal does not fire — but the row it just gained is one no finding on file was derived against, so splitting it before the run offered above would allocate against grounding that does not cover it. Neither state is what this option points at. Guidance
only — never auto-invokes another command.

**This BRD's own next step is nothing.** Every row this walk resolved is `covered-by` (a named
child's to decide), `deferred-to`, `rejected` or `superseded-by` — terminal dispositions this
ledger itself now records, not open questions. **A row Step 2R re-cut is `covered-by` too**, and lands in that same first case for the same reason: the move changes **which** BRD answers for the row — the receiving sibling's to decide now, the donor's no longer — and never whether this one does. So the re-cut leaves this BRD exactly where the ordinary walk leaves it, with nothing of its own left open, and it is named here rather than left out so that a reader does not read its absence as an oversight. And a root is never ground, so it carries no
finding of its own for `/product-workflows:brd-interview` to read either way.
`/product-workflows:brd-interview <BRD-KEY>` refuses any root outright, at its own Phase 0 step 5a,
with `BRD_INTERVIEW_ROOT_LEVEL` — offering it here is exactly the failure `/prd-ground`'s own
Phase 10 names as worse than offering nothing, so it is not offered. Grounding each child that gained a row
is the one real next step this phase has on the `full` path: each child continues its own route pass
and reaches this same phase in its own right, where `/product-workflows:brd-interview <CHILD-KEY>` is
then the real offer, on that child's own key. The BRD route on `/create-prd`, `/create-ard`,
`/specify`, `/product-workflows:brd-package` and `/product-workflows:brd-reconcile` is likewise a
child's route to reach, never this BRD's own.

### Context hygiene

Per `workflows-core:session-hygiene`, the resume pointer is written in the
terminal cost phase (Phase 8), after the cost entry and before the commit step. On `full`,
grounding a child created above is a hand to PA → run **`/clear`**; this BRD's own key has no
further step, so no `/compact` branch applies here. On `allocate-only`, continuing as PM into
`/product-workflows:brd-interview <BRD-KEY>` on this same slice keeps the context relevant → run
**`/compact`**. Guidance only — nothing is auto-run.

---

## Phase 8 — Session maintenance, feedback & cost

Terminal phase — runs after Phase 7, NEVER interrupts an earlier phase, and runs on the Phase 0
no-op path step 10 decides exactly as on any other, in either run mode, and on the reconcile path too.

**Capture-at-block invariant.** If an EARLIER phase halts on a plugin / skill / command / reference
gap, `emit-block` (`workflows-core:feedback-emission`) fires at that halt before escalating. **One
of this command's stops qualifies, and the test is a rule rather than this list.**
`BRD_SPLIT_MALFORMED_FINDING` is a record-integrity gap of the plugin's own making — the keys it
finds in practice are `grounding-verifier`'s return fields, which reach a finding block only through
a plugin command transcribing a return into the record — so it fires `emit-block`, exactly as
`/product-workflows:brd-interview`'s `BRD_INTERVIEW_MALFORMED_FINDING` does. Every other stop
reports the state of the operator's own argument, the tree or the environment, never a capability,
reference or command path this plugin lacks, so it is classified by that test, never by a list, and
a stop added later is classified by the same test. Among them: a missing or malformed key
(`BRD_SPLIT_NEEDS_KEY`), an unresolved BRD (`BRD_SPLIT_NOT_FOUND`), a key naming an Epic folder
(`BRD_SPLIT_EPIC_LEVEL`), an idea-route PRD folder (`BRD_SPLIT_NOT_A_BRD`) or any other folder that is
not a BRD container and holds no `[BR#n]` row (`BRD_SPLIT_EMPTY_INVENTORY`'s second form at step 8) and an unset `$SPECS_PATH`
are argument or environment halts; a missing instruction on a root with a row still `unallocated`
(`BRD_SPLIT_NEEDS_INSTRUCTION`) is the operator's own argument left out; an ungated or missing
grounding deliverable (`BRD_SPLIT_NEEDS_GROUNDING`), a grounding file on main recording no finding
(`BRD_SPLIT_NO_FINDINGS`), frame sets no design grounding on main covers
(`BRD_SPLIT_DESIGN_NOT_GROUND`) and unverified findings (`BRD_SPLIT_UNVERIFIED`) are sequencing
halts, each naming the run that clears it; and an inventory carrying no claim at all
(`BRD_SPLIT_EMPTY_INVENTORY` — step 8's container form on a root, step 6's row-F branch on a slice) is a
fact about the customer's document or about what the parent allocated, never about this plugin;
nor is a slice with no inventory in its folder (`BRD_SPLIT_NO_INVENTORY`, step 6's row-F branch),
which is an interrupted run on the parent that never wrote it or a file lost after it was written.
`BRD_SPLIT_ON_SLICE` is not among them because it is **not a stop**: it is the Phase 0 step 5 notice
that this run is `allocate-only`, and the run continues through it. Neither is anything in Phase 1.5
— an instruction that placed no row, a grill that reached its cap, and a `Cancel` mid-grill are all
readings of a sentence the operator typed, never a capability this plugin lacks. Nor is the
operator's own `Cancel` later in the run — at Phase 2's proposal, mid-key-taking in Phase 3, or
mid-walk in Phase 4 — each a user halt that reports what it left written. The one exception is a halt on a tool the ai-containers image lacks, which `workflows-core:feedback-emission` §6 `emit-block` defines.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 2's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model:
   `<detection_model>`) with a compact handoff: command `/brd-split`; what was produced (slices
   confirmed and keyed, the ledger walk's tally, `slices.md`); key events (the run mode, the no-op
   path, the re-cut path with how many rows were re-pointed and how many left with their donor, a
   cancelled walk with N rows left, a rejected `covered-by` key — or "none"); workarounds; test
   result N/A; project root = the BRD folder.
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6)
   with the Lessons Learned report, `command: /brd-split`, the run's `key` (the `<BRD-KEY>`),
   `source`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`).
   Surface the persisted path (or "no plugin-facing signal — nothing persisted").
3. **Session cost (ALWAYS runs).** **Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way. Otherwise, invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call its `emit-cost` entry point with `command: /brd-split`, `phase: brd-to-prd`, `role: pm`, the
   run's `key`, `source`, and `plugin_version`. Surface the persisted path (or the report-only
   notice).
4. **Write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite `<BRD-dir>/dev-workflows/resume.md` now — after the cost entry above, and before
   the commit step below. Redact per §1. Silent.
5. **Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths
   inside `$SPECS_PATH`, commits `<BRD-KEY> Add dev-workflows session artifacts (/brd-split)` with
   no `Co-Authored-By` trailer, and pushes to the branch Phase 6's handoff created. It NEVER touches
   a code repo, a docs repo, or the current working directory, where it is not the specs repository; NEVER force-pushes; NEVER
   fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Hold its §6 outcome line for the final report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (git for the deliverable
is offered only in Phase 6), and NEVER writes into a code/docs repo or the current working
directory, where it is not the specs repository; no user name is ever written.

---

## Final report

Report: the BRD folder; **the slicing instruction verbatim when one was given, and how it was read**
— the counts of rows Step A placed, the Step B grill settled, and neither could place — or that none
was given; where an instruction was given but nothing consumed it, say which path swallowed it (the
no-op, the reconcile path, or an `allocate-only` run whose walk found every row already
terminal), because an instruction that changed nothing and is not reported reads as one the command
ignored — and on a `full` run naming the path is not the whole answer, since the re-cut is the one thing that instruction could still have meant there, so the step 9a reason below is reported beside it; **the run mode from Phase
0 step 5, and in `allocate-only` the
`BRD_SPLIT_ON_SLICE` notice repeated in full** — a notice shown once at Phase 0 of a long
interactive walk is one the operator has scrolled past by the end; whether Phase 0 found this
run a no-op (fully allocated already) or
whether it actually split and/or walked the ledger — **a fully-allocated ledger is not on its own the no-op**, since the re-cut path and the reconcile path both start from one, so name the branch step 10 took rather than the ledger state it read; **every child Step 3 reconciled although no walk of this run touched it**, with each `[BR#n]` added or withdrawn, every ledger row Step 3 left standing (its case list), and every child Phase 0 step 9 marked unreconcilable, by name, with the file it is missing or cannot read and every target list this run left it out of; the classification and model routing (+ any
Opus degradation, or `Model routing: bypassed — enforced <id> (flag|env)` in its place wherever `run_flags.enforced_model` is set, per `workflows-core:model-routing/classification` §10); the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); every slice proposed, keyed, and its folder (or that none were proposed and
why — in `allocate-only` that reason is the cap, not an operator choice); any child removed or
kept-with-reason for claiming nothing (Phase 4.5) — including any an earlier run left standing and this run resolved — and which, **and for a removal, every row it re-pointed onto this BRD** — by `[BR#n]` and by the ledger it sits on, **this BRD's own ledger included, not only another child's** — or that the removal re-pointed none; the ledger
walk's resolution tally by disposition, with every new `covered-by` key and every
`rejected`/`superseded-by` citation named; **every claim this run withdrew, named by the route it was withdrawn on** — `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2 distinguishes the two and this report does not collapse them: a **provisional** claim, one Phase 3 wrote and this walk settled somewhere else, whose orphan row Phase 4's **reconcile step** wrote the terminal disposition onto; or a **committed** claim, one an earlier run gave the child and the child's own walk then recorded `deferred-to` against, which this run's re-cut moved — and whose orphan row reads `covered-by: <B-KEY>` because **Step 2R** wrote it one step earlier, the reconcile step deliberately leaving it alone. Report each with its
`[BR#n]`, the child it was withdrawn from, and the disposition its orphan row now carries, so a withdrawal is reported rather than only visible by re-reading two
files, and so that a re-cut withdrawal is never reported as a provisional claim the walk happened to settle elsewhere; **on the re-cut path (`recut_mode: true`) the whole of that path's own record**: how many rows were re-cuttable and from which donors (Phase 0 step 9a), how many were re-pointed and to which receivers, how many were left with their donor **and why each**, over the same five reasons `slices.md` records — declined at Step 2R's picker, held back from Step 1's bulk offer and then declined, left unplaced by Phase 1.5's reading, placed into a group whose target Phase 3 dropped, or placed into a group Phase 2 confirmed nothing of, which is an answer rather than a failure and is reported as one — every decision the run reported out of a donor's register, **by `id`**, with the note that they were reported and **not touched**, and **any child whose `coverage-ledger.md` step 9a could not read**, named with the read failure, since an unreadable ledger is `unresolved` and never an empty `deferred-to` set (§6.2); **and where step 9a found no candidate at all on a `full` run that was given an instruction, which of its two causes applied** — no child holding a `deferred-to` row of its own, or every such row being one this BRD did not delegate to that child. That last sentence is the one an operator who typed an instruction and got a no-op needs, and without it "nothing to re-cut" is indistinguishable from an instruction the command failed to parse; the `slices.md` path (or that it was skipped on the
no-op path); the feedback path (or, under `--skip-feedback`, the `Session feedback: …` line) and cost path (or, under `--skip-costs`, the `Session cost: …` line); the `Phase handoff:` outcome line from `handoff-to-main`
(`workflows-core:phase-handoff` §4.1); the `Specs repo:` outcome line from `commit-artifacts`
(`workflows-core:specs-repo-git` §6); the next-step recommendation; and end with the ledger line, exactly per
`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §6:

```
ledger: <N> requirements — <covered> covered, <deferred> deferred, <rejected> rejected, <unallocated> unallocated, <unresolved> unresolved (<delegated> delegated, <not-built> not built)
```

**Computing it reads one ledger per `covered-by` row**, one hop, from the working tree via
`resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). In `full` mode those are
the children this run created in Phase 3 and reconciled in Phase 4, and any it found already nested
in Phase 0 step 9; in `allocate-only` they are the siblings and the parent this slice's orphan rows
name (`coverage-ledger-format.md` §3), each of which `resolve-address` finds at its own level.
A ledger that cannot be read there contributes `unresolved`, never `covered`
(`coverage-ledger-format.md` §6.2). **This changes no gate and no precondition of this command**:
Phase 0's stops and §4's allocation gate are decided on this BRD's own rows, before any of this, and step 10's
no-op decision is taken before it too. **Step 10 is no longer decided on this BRD's own rows alone, and the distinction is worth keeping straight**: its three parts are this ledger's `unallocated` count (step 8), step 9's child enumeration with its reconciliation test, and step 9a's re-cut candidate set — the second reads each child's `claims:` and inventory against this ledger's `covered-by` rows, and the last reads a child's ledger, one `disposition` column at a time for the `covered-by`/`deferred-to` pair that makes a row movable. Those are different reads from this one and feed nothing into it: no gate, no stop and no no-op branch turns on this line's arithmetic, which is computed here and reported and nowhere consulted. **In `allocate-only` mode there may still be rows to resolve,
and the hop lands elsewhere.** This walk offers no `covered-by`, so it adds none — but a slice can
already hold **orphan rows** (`coverage-ledger-format.md` §2). §6.1 counts every one of them through the
parent's current disposition for its `[BR#n]`, never as it reads, and resolves a `covered-by` it
maps to one hop, exactly as it resolves a parent's delegated rows. So a slice's line reports zero delegated only when its parent withdrew none of its claims —
provisional, committed, or settled here before the parent re-allocated it, the three routes to an
orphan row (§2) — never as a property of being a slice.

`/brd-split` is the only `/brd-*` command that puts a row into this line's `unallocated` term as
written on **a slice's** ledger, or allocates one out of it. `/product-workflows:brd-reconcile` can
also take one out — its ledger phase moves a row to `deferred-to`, `rejected` or `superseded-by` on
a frozen `[CD#n]`, and a `--sent` review of a slice never interviewed can meet a row still
`unallocated` — but never puts one in. On a source-owning BRD a row can move back, and the
exception is the one `coverage-ledger-format.md` §3 states: a `/product-workflows:brd-intake` re-run
whose read finds a requirement rewrites that BRD's ledger with every row `unallocated`, which is the
single case in the family of a row moving back. That never reaches a slice, which `/brd-intake` is
never run on. A completed run of this command always leaves **its own** rows with none
(`coverage-ledger-format.md` §4: "cannot complete while any row in this BRD's ledger is
`unallocated`"), whether that took an actual walk this run or was already true before it — step 8
reads the ledger and records that, and step 10 is where it becomes the no-op decision. **The reported term can still be non-zero**, and that is the point: a row
this BRD delegated to a child the child has not yet allocated is counted `unallocated` in the line
(`coverage-ledger-format.md` §6.1) while this BRD's own gate stands satisfied. Report it as what it
is — a child with work left, named by the `<CHILD-KEY>` the row delegates to — never as this run
having failed to complete, and never by re-opening the walk over one of these rows. **The re-cut is not the exception it looks like, and stating why is what keeps this rule usable.** A re-cut moves a row that already carries a fate, so the flat form of this sentence — *never re-open a row carrying a terminal disposition* — is no longer true of the command. What is still true, and is what this term needs, is narrower: a row counted `unallocated` here is one the named child has **not yet allocated**, and a re-cut requires that child to have allocated it to `deferred-to: <itself>` (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2). The two sets are disjoint by construction, so no row this term reports is ever re-cuttable and the answer to a non-zero count is still the child's own walk, never a re-run of this one.

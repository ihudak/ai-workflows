---
name: create-ard
description: Architecture-authoring workflow (Product Architect phase, sub-project 3 of the PRD-creation flow). Grounds on the mounted implementation repos (architect-driven discovery — no PRs) and authors an ARD for a PRD (/create-ard <PRD-KEY>) or an Epic (/create-ard <EPIC-KEY> — one address, the Epic's own key encoding its ancestry; inherits the PRD-level ARD), against references/ard-format.md, gated by the Opus ard-reviewer, written as ard.md into the resolved folder under $SPECS_PATH/specifications/ — the PRD- folder for a PRD-level ARD, the EPIC- folder for an Epic-level one. Optional; scoped; product-architecture level (no code writing). Introduces the pa role. the BRD route seeds the run from a decided BRD slice instead of a PRD: it resolves the BRD-route PRD- slice folder (the folder carrying brd-link.md) and refuses a BRD- container outright, since §4.1's tree places ard.md only inside a PRD folder; it reads that slice folder's architecture-altitude ard-seed.md, the architecture decisions in decisions.md and the verified [CG#n]/[DG#n] findings, gates decisions.md on the specs default branch before reading it (an unmerged register stops the run), seeds the ARD's grounding-findings section and its AD#N from them, freezes every [VD#n]/[CD#n] against the grill, runs the same PRD gate and reads the same authored prd.md as the idea route, and marks each consumed item consumed_by: ARD.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Author an Architecture Requirements/Decision Document for the resolved item: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/create-ard` is **sub-project 3 of the PRD-creation flow** — the **Product Architect (PA)** phase. It
grounds on the mounted implementation repos and authors an **ARD** that establishes the architecture
invariants the downstream (`/specify`, `/design`, `/implement`) will later inherit. The ARD is
**optional** (a simple PRD may not need one) and **scoped by the kind of the address it is given**:

- `/create-ard <PRD-KEY>` → a **PRD-level** ARD.
- `/create-ard <EPIC-KEY>` → an **Epic-level** ARD (inherits the PRD-level ARD read-only). The Epic's
  own key is the whole address: it encodes its ancestry, so the PRD is the folder above it and is
  never typed beside it (D4).
- `/create-ard <SLICE-KEY>` → an ARD on the **BRD route**, authored in the `PRD-` slice folder
  `/brd-split` carved and seeded from the decided BRD slice instead of from a PRD. A `BRD-` container is
  refused (Phase 0 step 1a). One address on every route: a second positional token is refused
  (Phase 0 step 1, `CREATE_ARD_ONE_ADDRESS`).

Usage: `/create-ard <ADDRESS> [--no-docs] [--docs <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`, where `<ADDRESS>` is a key or an `@<path>`. `--docs <path>` — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`; **strip the flag and its value together** before any remaining-argument classification, or the path is read as part of the address. Declared for every consumer by `workflows-core:docs-grounding` *Procedure* step 1 (*Flags first*), which resolves it; this command only has to recognise it and pass the invocation through.

It authors architecture only — no code writing; grounding is **architect-driven** (there are no PRs at
this stage). Zero external calls.

---

## Phase 0 — Resolve input
1. **Resolve the address.**

   **Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves.

   **Strip recognised flags before anything counts positional tokens.** `--no-docs` (boolean) and
   `--docs <path>` (which consumes the token after it) are removed from `$ARGUMENTS` first, together
   with `--docs`'s value; what remains is the positional address, and the one-address refusal below
   applies to that remainder alone. **Without this rung the flags this command documents do not
   work** — a flag is a token, so `--no-docs` reaches the refusal as a second positional and stops
   the run, and `--docs <path>` supplies two. That was the live state: both flags were named in the
   Usage line and neither was ever parsed, which is the shape `workflows-core:docs-grounding`
   *Procedure* step 1 (*Flags first*) declares for all nine of its consumers and only `/idea` had
   implemented.

   **One resolution, both routes.** Parse the **single positional address** from `$ARGUMENTS` — a
   `<KEY>`, or an `@<path>` naming a folder — and resolve it with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). A key that fails §1's grammar stops with
   `CREATE_ARD_NEEDS_KEY: /create-ard needs an address (^[A-Z][A-Z0-9_]*(-\d+)+$, e.g. EPIC-008 or the slice EPIC-008-01) — re-run '/product-workflows:create-ard <ADDRESS>'.`
   Shape only, and never checked against anything (§1) — a key names a folder in `$SPECS_PATH`.

   **A second positional token is refused, on every route** (D4). There is no `<PRD> <Epic>` form to
   fall back to: an Epic key encodes its own ancestry, so a second argument would be derivable from
   the first and able to disagree with it, which is the failure class D4 exists to remove. Stop
   gracefully:
   `CREATE_ARD_ONE_ADDRESS: /create-ard takes one address; <second-token> was given as a second. The folder the address resolves to sets the altitude by its prefix — an EPIC- folder gives an Epic-level ARD, with its PRD read from the folder above it; a PRD- folder gives a PRD-level one — and a legacy folder with no prefix by what it holds. Re-run '/product-workflows:create-ard <ADDRESS>' with the single address you meant.`

   **Where the resolution returns `status: found`, settle the specs checkout before anything below
   reads the folder.** Fix the run key set (`workflows-core:specs-repo-git` §3.2), reading only
   carrier frontmatter (`key:`, `kind:`) as §4 does, whatever file that is, and testing no file's
   presence: the resolved `key` and, where `workflows-core:addressing` §4.1 places the resolved
   folder at Epic level — an `EPIC-` prefix, or with no prefix a resolved `kind: epic` — also the
   key its parent's carrier asserts (§4), the would-be `<PRD>`. Then run the specs-repo preflight
   below, and only then place the folder, detect the route and take step 1a's refusal and every
   later read. A stale plugin branch the preflight switches away from would otherwise hide a
   slice's `brd-link.md` from step 1a's listing, or the file that places the folder or detects the
   route, and the run would list the wrong slices or stop where it would have proceeded. `absent`
   runs no preflight at all: step 3 stops it with `CREATE_ARD_NOT_FOUND`, which reads nothing.

   **The resolved folder decides the altitude — as `workflows-core:addressing` §4.1 places it: by
   its prefix, never by the `kind` it asserts**, which on a slice is its `brd-link.md`'s `brd` (§4).
   This is what replaces the old two-key grammar:
   - a `PRD-` folder → `<PRD>` is its `key`, `<EPIC>` is `null`;
   - an `EPIC-` folder → `<EPIC>` is its `key` and `<PRD>` is its parent's. Phase 2 calls `<EPIC>`
     `focus_key` — one value under two names, set on an Epic-level run and `null` otherwise;
   - a `PRD-` folder holding a `brd-link.md` → the BRD route. Define `<SLICE-KEY>` = the resolved
     folder's `key`;
   - **a folder with no prefix** — one §5's legacy fallback resolved (`legacy: true`), or an
     unprefixed folder an `@<path>` names; a name is prefixed only where it begins
     `<KIND>-<the resolved key>-` (§4.1), so a legacy key beginning with a kind token is no prefix —
     **is placed by positive evidence**, never by the absence of a file: a resolved `kind: epic` is
     placed as an `EPIC-` folder is; a resolved `kind: prd`, or a `brd-link.md` naming a `parent:`,
     as a `PRD-` folder is — the latter a legacy slice, and so the BRD route. A legacy root
     container is placed by neither: §4.1 tests it first, and step 1a refuses it on that test. A
     folder none of these places is not guessed at — stop, naming the folder and what it carries — and, where it holds an `idea.md` and no `prd.md`, name `/product-workflows:create-prd <KEY>` too, whose `prd.md` places it (`workflows-core:addressing` §4.1).

   **Carry `prd_dir` — the PRD folder — beside the resolved folder, because on an Epic-level run
   they are two different folders.** `prd_dir` is the resolved folder itself on a PRD-level run (the
   `PRD-` slice on the BRD route), and the folder containing it on an Epic-level one, `<PRD>`'s
   folder — the one the PRD gate below tests. **Every `grounding/` read, seed, stamp, staged path and
   report in this command names `prd_dir`, never the resolved folder** — the one exception being step
   5's optionality gauge, which sizes the item the address names and says so there: `/product-workflows:prd-ground`
   grounds at PRD altitude and refuses an `EPIC-` folder (`PRD_GROUND_EPIC_LEVEL`), so an Epic folder
   never holds a `grounding/` of its own, and a test on the resolved folder would find none there on
   every Epic-level run, reading, seeding from and stamping none of the findings the PRD folder
   above it carries. `/product-workflows:specify` stages the same files at its own `prd_dir` for the
   same reason.

   **The BRD route is detected, not declared.** A folder carrying `brd-link.md` was produced by
   `/brd-split` and holds the seed this command reads; nothing about that needs restating on the
   command line, and a flag that could disagree with the folder it names is one more disagreement to
   have. Print which route the run entered — detected once the preflight above has run — before
   doing anything else.

1a. **Refuse a `BRD-` container — on either route, and the moment the specs-repo preflight step 1
   ends with has run.**

   **Resolution waits on `$SPECS_PATH`, and there is exactly one of them.** `resolve-key` globs
   `specifications/**/*-<KEY>-*`, so it needs `$SPECS_PATH`; run step 1's resolution only after step 2
   has settled it, and let step 3 **reuse that same resolution** rather than taking a second one. With
   the old ordering `/create-ard ACME-77` against an unset `$SPECS_PATH` resolved `absent` at step 1 —
   so this refusal did not fire and the route printed as the idea route — then step 2 stopped, the
   operator supplied the path, and step 3 re-resolved and *found the `BRD-` container* with nothing
   testing it. The run authored `ard.md` into the container, which is the exact state this step exists
   to prevent. `/create-prd` states the same rule for the same reason ("**Detection therefore waits on
   resolution**"); the two must not diverge on it.
   A `BRD-` folder is **not** a fourth altitude, and this command used to route one onto the BRD
   route. **This test is not part of the BRD-route branch and must not be folded into it**: that
   route is detected from a `brd-link.md`, and a root BRD folder need not carry one — `/brd-intake`
   writes none, and no command writes one into a root: `/brd-split` places one in each slice it
   carves, and every command that merges `depends-on:` into one refuses a root — so a
   route-conditioned refusal would let `/create-ard <ROOT-BRD-KEY>` fall through and author an ARD
   into the container. It is a container: the design's §4.1 tree places `ard.md`
   only inside a PRD folder, while a `BRD-` folder holds `brd/`, `coverage-ledger.md` and
   `slices.md` — plus any root-level `grounding/`, `interview/` and `decisions.md` a tree written
   under the earlier two-level model left behind — and no ARD. Authoring one there writes an
   artifact the tree has no place for and that
   `workflows-core:ard-resolution` would then look for one level away.

   **The test is the directory prefix, and never the folder's asserted `kind:`** — `/brd-split`
   writes `kind: brd` into the `brd-link.md` inside a `PRD-` slice folder, so a slice asserts `brd`
   while being exactly the folder an ARD belongs in, and a gate on the asserted kind would refuse
   every slice.

   **Where the folder carries no prefix — resolved through `workflows-core:addressing` §5's legacy
   fallback, or an unprefixed folder an `@<path>` named — the question is answered by positive
   evidence that it is a BRD, never by the absence of a file** —
   `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.1, the shared authority
   every container or root refusal in this plugin takes this same test from, directly or through
   `workflows-core:addressing` §4.1 (which cites it, and which `/idea`'s refusal takes). In short: a
   legacy folder carrying `coverage-ledger.md` or `brd/brd-inventory.md`, and no `brd-link.md`
   naming a `parent:`, is a root container; a legacy folder carrying **neither** of those two files
   is a legacy **idea-route PRD folder**, which holds `prd.md` and no `brd-link.md` either — this
   refusal does not fire on it, and refusing it would offer `/product-workflows:brd-split` on a
   folder with no coverage ledger to walk. Stop gracefully:
   ```
   CREATE_ARD_BRD_NOT_SLICED: <BRD-KEY> resolves to a BRD- container at <path>, and a BRD is never the folder an ARD is authored in — its architecture is authored in the PRD- slices under it, one ARD each (coverage-ledger-format.md §5). <the remedy, per the branch below>
   ```

   **The remedy is the same two branches `/product-workflows:create-prd`'s own container refusal takes,
   and it is a directory listing rather than a ledger read** — this remedy opens no coverage ledger
   and does not start now. Enumerate slices by `/brd-split` Phase 0 step 9's **positive test**: an
   immediate subdirectory carrying a `brd-link.md` whose `parent:` names this BRD.
   - **One or more slices** — the ordinary shape, since a split always confirms at least one. Name
     every slice and offer `/product-workflows:create-ard <SLICE-KEY>` once per slice. Do **not** name
     `/product-workflows:brd-split <BRD-KEY>`: the slices exist, and on a parent whose ledger is fully
     allocated that run carves nothing (`commands/brd-split.md` Phase 0 step 10).
   - **No slice at all** — `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` is the run that
     carves one, walking every row still `unallocated` and always confirming at least one slice (its
     Phase 2). **Two conditions travel with that offer**, in its own text, because this command holds
     neither answer: the slicing instruction is not optional there — a root is never ground, so that
     run has no findings to cluster candidate slices from and stops with
     `BRD_SPLIT_NEEDS_INSTRUCTION` where it has rows to place and was given none; and **where this
     BRD's ledger leaves no row `unallocated` that run is a no-op** (its Phase 0 step 10) and carves
     nothing, since no command but the `/brd-intake` re-run below moves a terminal row back to
     `unallocated` (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3). Say what the
     operator does then rather than leaving the offer to fail silently. There are two ways to reach
     it and **both are leaveable** — one by a decision, one by a repair. Either the one slice the
     walk confirmed was removed as a standing empty child, in which case every requirement is
     `deferred-to`, `rejected` or `superseded-by`, every row is legal and terminal, and nothing is
     owed to anybody: that is an **ending rather than a failure**, and no command decides otherwise,
     because un-deferring a requirement is a decision taken with the customer. Name no command for
     the decision — and say, rather than implying the state is sealed, that once it is taken it is
     carried out by the same two repairs the other way below names, in the same order: hand-edit the
     one row that is now to be built back to `unallocated`, after which
     `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` has a row to walk and carves the
     slice; or re-run `/product-workflows:brd-intake <BRD-KEY> @<brd-file>`, which, wherever its
     read finds a requirement, reopens **every** row and discards every deferral and rejection
     recorded here (its Phase 0 step 7). Or the ledger records a fate a container can no longer hold
     — a **root** row `covered-here`, which only a tree written before a BRD became a container, or
     a hand edit, can have produced (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md`
     §5). **Offer the narrower repair first**, because the illegal state is one row wide and every
     other row is already legal and terminal: hand-edit that one row's `disposition:` in
     `coverage-ledger.md`, leaving every other row untouched — to `deferred-to: <this BRD>`,
     `rejected: [DEF#n]` or `superseded-by: [BR#n]` where the requirement is not to be built here,
     which makes the ledger legal and lands on the ending above; or back to `unallocated` where it
     is, after which `/product-workflows:brd-split <BRD-KEY>` has a row to walk, confirms a slice,
     and that slice's own walk takes the row to `covered-here`, the one level at which
     `covered-here` is legal. §3's *no command moves a row back to `unallocated`, save one* binds
     the commands; this is a hand repair of a value no command wrote, and §5 already names hand
     editing as how this state arises. **Offer the `/brd-intake` re-run second, and only where the
     whole inventory is to be re-taken:** re-running
     `/product-workflows:brd-intake <BRD-KEY> @<brd-file>` over this same folder is a re-run rather
     than a refusal (its Phase 0 step 7 warns and confirms before the first write) and, wherever its
     read finds a requirement, rewrites the ledger with **every** row `unallocated` — that step
     lists what a re-run keeps and what it changes — after which
     `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` has rows to walk. Wherever its read
     finds a requirement it also **discards every disposition this ledger records**: each
     `deferred-to`, `rejected` and `superseded-by` the walk decided is replaced by `unallocated` and
     must be re-taken, and a `rejected` row must be re-cited against its `[DEF#n]`. Name those
     decisions — saying only that the dispositions are replaced is not the disclosure.


2. **`$SPECS_PATH` (required).** If unset, stop naming `SPECS_PATH` (`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`).
3. **Feature folder.** Resolve it with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3) — `<PRD>` for a PRD-level run, `<EPIC>` for an Epic-level one, the kind it returns confirming which. That entry point searches every level §3 bounds and carries §5's legacy fallback, so no matching rule is written here: a second copy of §5's is the drift §1 warns about. Every later mention of the feature folder in this command — the path the PRD gate hands `require-on-main` and Phase 2's PRD read included — names the folder resolved here. **`status: absent` is a stop, not a folder to create.** This command creates no folder in the specs tree. It cannot even choose a §2 prefix for one: `resolve-address` returns no `kind` for a folder that does not exist, and the two kinds it would have to choose between are minted by different commands. **An `EPIC-` folder is created by `/product-workflows:epics` and by nothing else** (D6) — auto-creating one here would put an Epic in the tree that no `/epics` run ever drafted, holding an `ard.md` and no `epic.md`, invisible to the `EPIC-` enumeration every other command reads. Stop gracefully:
   ```
   CREATE_ARD_NOT_FOUND: no folder found for <KEY> under $SPECS_PATH/specifications/ (every level addressing.md §3 bounds, plus §5's legacy fallback) — /create-ard architects an existing PRD or Epic folder and creates neither. A PRD folder is created by /product-workflows:idea <KEY> or /product-workflows:create-prd <KEY> on the idea route, and by /product-workflows:brd-split on its parent on the BRD route; an EPIC- folder is created by /product-workflows:epics <PRD-ADDRESS> and by no other command.
   ```
   Every command that stop names creates the folder it claims to: `/idea` and `/create-prd` both write `PRD-<KEY>-<slug>/` on their first write, `/brd-split` carves the slice folder, and `/epics` writes `EPIC-<PRD-KEY>-NN-<eslug>/` under the PRD folder it resolved. Resolution honors a folder that already exists wherever it sits, and never proposes one.

   **On the BRD route this is the resolved `PRD-` slice folder**, and it is never created here.
   There is no second resolution for that route and no `<BRD-dir>` argument to read: step 1 resolved
   the single positional address once, step 1a refused the container the upper level holds, and the
   folder that survives both **is** the slice. The ARD this run authors is written **into that
   folder**, beside the BRD artifacts it was derived from.

   `absent` therefore takes the one `CREATE_ARD_NOT_FOUND` stop above on every route — it already
   names how a `PRD-` folder comes into being on each, including `/product-workflows:brd-split` on the
   parent for a slice, and it names no command whose output this run would then refuse. Where the
   address was an **`@<path>`** the stop substitutes that path for the search clause —
   `no folder at <path> (given as a path)` — because "every level addressing.md §3 bounds" would
   describe a search a verbatim path never performs.
4. **Prior ARD.** If the target `ard.md` exists → Phase 1 offers refine-vs-fresh. The target is `ard.md` in the feature folder step 3 resolved, on every route — a `PRD-` slice folder is that folder on the BRD route, and the test is the same glob in the same place with no route branch.
5. **Optionality advisory — one rule, gauged off everything the folder holds.** Gauge size and, for a small
   single-repo item, note "an ARD may be optional here" and offer — adding, on a PRD-level run where `enumerate-components` (`workflows-core:components` §2) finds two or more code components in that one repository, that a PRD touching two of them is multi-component and `/epics` will then ask for this ARD —
   `choices: ["Author the ARD anyway", "Stop — no ARD needed"]`. The gauge is the **union** of what the
   resolved folder actually carries, not a per-route pair of gauges:
   - the authored `prd.md`'s user-story count and scope breadth, when the folder holds one;
   - the number of architecture-altitude `decided` records in `decisions.md`, the number of
     architecture-altitude `[CG#n]`/`[DG#n]` findings, and the number of repositories
     `grounding/baselines.md` pinned, when the folder holds those;
   - the number of candidate repos, always.

   **The folder gauged is the resolved folder, and on an Epic-level run that is deliberate** — it is
   the one count of grounding findings in this command that does not take `prd_dir`. The advisory sizes the item this ARD is
   for, and the PRD folder's findings and register size the whole PRD, so counting them for one Epic
   would report a large item where there is one small one. An `EPIC-` folder holds no `prd.md`,
   `decisions.md` or `grounding/`, so its gauge is the candidate repos.

   **A slice can hold both, and where it does the PRD wins the gauge.** A BRD-route slice that has been
   through `/product-workflows:create-prd` carries a `prd.md` *and* the register the PRD was authored from,
   and the two count the same work twice — the register's decisions are what the PRD's stories were
   written out of, so summing them would report a large item where there is one small one. Take the PRD's
   count and cite the register's beside it as corroboration, never as an addition. Where the folder holds
   no `prd.md` — the ordinary BRD-route state, since `/product-workflows:create-prd` is not a prerequisite for
   this command — the register and the findings are the whole gauge. An item whose architecture altitude is
   one decision against one repository is exactly the case the advisory exists for, and that is true of a
   thin PRD and a thin register alike.

`/create-ard` is **cwd-agnostic**; it reads the resolved folder's PRD/Epic — and, on the BRD route, that slice folder's seed, register and findings **in addition** — and scans repos under `$REPOS_PATH`.

**Specs-repo preflight** — run in step 1, once the resolution returns `status: found`, with the run key set step 1 fixes, before step 1 places the folder and before step 1a or any later step reads it. Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier run, retry an artifact commit that failed to push, and settle the branch. Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice; if it returns `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag for the whole run — the terminal `commit-artifacts` step skips on it.

**Gate the PRD — on every route, with no branch.** The folder gated is **the PRD folder this run resolved**: the resolved folder itself for a PRD-level run, its parent for an Epic-level one, and — on the BRD route — the resolved `PRD-` slice folder, which *is* that route's PRD folder (§4.1). One rule, one path expression, no route test. Execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against the PRD file in that folder (written below as `specifications/<PRD>-<vslug>/` for brevity; the folder on disk carries its kind prefix — `PRD-<PRD>-<vslug>/` on a current tree, the unprefixed form only through §5's legacy fallback — and it is always the folder step 3 resolved, never a path re-derived here) — that file is `prd.md`, a constant. `/create-prd` and `/update-prd` write no other canonical name — the only other PRD file either writes is the dated copy `/update-prd` archives under `revisions/`, which is no PRD this gate could mean — and `workflows-core:addressing` §5 fixes the boundary: the legacy fallback resolves a folder name and nothing inside it, so a pre-rename tree renames its artifacts rather than being resolved for. **A key-globbed filename was gated here once, and is not restored.** The pre-rename `<KEY>_<slug>.md` form matches nothing in a current repo — so the gate returned `absent` for every PRD that was present and the rows D/E stop could never fire — and on the one tree it was written for it also matches the pre-rename ARD `<KEY>_ARD.md`, so it can gate the wrong artifact entirely. Gating the constant is correct on both trees: on a current one it names the file that is there, and on a pre-rename one it reports `absent`, which is what §5 now tells that operator to fix. Map its §3.7 return value by `stopped` first, never by `on_main` alone. Any stopping state → stop per §4.4. Otherwise (`stopped: false`): on `pass`/`pass_amending`, read the authored PRD in Phase 2 as it would be read without this gate; on `absent`, the existing folder-read fallback applies — but report it: *"No authored PRD on `<default>` for `<PRD>` — architecting from the resolved folder at `<path>`. If a PRD exists on a branch, this run would have stopped; it does not, so none does."*; on `unmanaged`, behave exactly as before this feature — reachable here even after step 2's own `$SPECS_PATH` check, since that check only rejects an unset value, never an invalid path or a non-git directory.

**The BRD route runs this gate too, and the `absent` branch is what makes that safe.** It did not,
and the rationale it carried was coherent while the route could resolve a `BRD-` container: the PRD
"may not exist at all", and gating an artifact the run does not read would promote an input the route
never had into a prerequisite, which
`workflows-core:phase-handoff` §5 rule 3 forbids. Phase 0 step 1a removed the
premise. The BRD route now resolves **a `PRD-` slice folder in every case** — the same kind of folder
the idea route resolves — so there is one folder to gate, and the gate's own `absent` branch already
handles the state the rationale was protecting: a slice in which no `prd.md` has been authored yet
returns `absent`, is **reported**, and this run architects from the resolved folder exactly as the
row for `/create-ard` in §3.4 says it may. Nothing is promoted into a prerequisite, because `absent`
is not a stop — `/product-workflows:create-prd` is still not a prerequisite for this command, on either
route. What the gate adds on both routes is the state it was built for: a `prd.md` that **exists and
was never handed off**, sitting on a branch (rows D/E). That state is as reachable on a slice as it
is on an idea-route PRD folder — `/product-workflows:create-prd` opens `prd/<SLICE-KEY>-<slug>` there and
its handoff can be declined — and architecting from an unmerged PRD is the failure the gate exists to
prevent, whichever route wrote it. §3.4's `/create-ard` row therefore describes every run of this
command, not one route's.

**Gate the decision register — on the BRD route, right after the PRD gate.** Wherever the PRD
folder that gate just tested carries a `brd-link.md` — the resolved slice on a PRD-level run, and on
an Epic-level run the slice the Epic sits in, which is the folder Phase 2's BRD-route read takes the
register from — execute `require-on-main` (§3) against that folder's `decisions.md` too. Phase 2
freezes every `[VD#n]` and `[CD#n]` in it against this run's grill, so it is read only once it is on
the specs repo's default branch. Map the §3.7 return by `stopped` first:
- **Any stopping row** → stop per §4.4, as `CREATE_ARD_REGISTER_NOT_ON_MAIN` below.
- **`pass`** → proceed; **`pass_amending`** → proceed, printing the §3.3 row-B message;
  **`unmanaged`** → proceed as before this gate existed.
- **`absent` (row F)** → split it on a test row F cannot make — is the file in the folder at all:
  - **No `decisions.md` in the folder** → exactly as before this gate: Phase 2 reports the register
    absent and carries what the folder holds. Nothing becomes a prerequisite (§5 rule 3).
  - **A `decisions.md` in the folder, and on no ref** — the run that wrote it had its handoff
    declined — → stop, as `CREATE_ARD_REGISTER_NOT_HANDED_OFF` below.

Both stops carry §4.4's four parts, in order:
```
CREATE_ARD_REGISTER_NOT_ON_MAIN: <SLICE-KEY>'s decision register <path> is <the state require-on-main reported — on branch <branch> with PR #<n> open, not merged | on branch <branch> and never handed off | changed in the working tree against <default> (<files>) | any other stopping row, as §3.3 words it>. This run read none of it and wrote nothing: an ARD frozen against [VD#n]/[CD#n] records that are not on <default> would rest on decisions nobody merged. <the resolving commands §4.4 prescribes for that row, $SPECS_PATH substituted — merge PR #<n>, open one for <branch>, or commit, stash or discard the working-tree edit>, then re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
```
```
CREATE_ARD_REGISTER_NOT_HANDED_OFF: <SLICE-KEY>'s decision register is written at <path> but is on no branch — the run that wrote it had its handoff declined. This run read none of it and wrote nothing. Commit and merge decisions.md to the specs repo's default branch (git -C "<SPECS_PATH>" add, commit and push it, then open and merge its pull request), then re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
```
Neither is a plugin gap, so neither `emit-block`s.

**Why the register is gated and the seed and grounding files are not.** This paragraph once said
the `/brd-*` family's own handoff discipline puts `ard-seed.md`, `decisions.md` and the grounding
files on the default branch before this route reads them — each of those commands landing its
deliverable there and the next refusing to start until it is — and gated no BRD artifact on that
ground. For the register it was false at the last hop: `/product-workflows:brd-package` gates it, but
`/product-workflows:brd-reconcile`, which freezes `[CD#n]` into it, and
`/product-workflows:create-prd`, which adds `[AS#n]` and consumption stamps to it, were followed, on
the path that advances the slice, by no route command that gated it — `/brd-package` is reached again only when the slice goes back through the route — a question still held for the customer, a reopened decision's new round, or a re-grounded claim — and not on the path that advances it — so a declined handoff of either
left a register this route read from a working tree. The gate above is what makes the claim true for
the register now: this command is the next one, and it refuses to start until the register is on the
default branch. The grounding files are not re-gated here, and the reason is not that something
upstream always gates them: `/product-workflows:brd-split` (allocate-only) and
`/product-workflows:brd-interview` each gate `grounding/code-grounding.md`, and `/brd-split`
`grounding/design-grounding.md` where frame sets exist, but a later `/product-workflows:prd-ground`
run rewrites both — the `--rebaseline` pass `/product-workflows:brd-reconcile` sends a challenged
code claim to, or any run on an idea-route folder — with no command gating them between it and this
one, so a declined handoff of that run leaves them unmerged. This command re-gates neither because
grounding is optional to it and read as evidence, never frozen: a finding counts for what its verifier
outcome says, and a findings file a later `/prd-ground` run left unmerged is read as the working tree
holds it — the grounding subsection of Phase 2 has the run report one it finds uncommitted. It reads
them wherever `prd_dir` holds them, on either route, as that subsection says. `ard-seed.md` is gated by nothing: its one writer is the
`/brd-intake --sort-existing` migration, it is read as context rather than frozen, and its absence
is the ordinary case. The PRD is gated above on every route.

---

## Phase 1 — Configure
Use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`Skill(skill: "workflows-core:reference", args: "escalation-rules")` §0).
1. **Confirm** the scope (PRD-level vs Epic-level) and the feature folder — and, on every route, whether an authored `prd.md` was found there (the Phase 0 gate's result), so the operator sees which content this run has before it starts. **Wherever `prd_dir` holds `grounding/`, on either route** — the resolved folder on a PRD-level run, the PRD folder above it on an Epic-level one (Phase 0 step 1) — confirm in addition which of `<prd_dir>/grounding/code-grounding.md` and `<prd_dir>/grounding/design-grounding.md` are present — a stat, not a read; the read is Phase 2. **On the BRD route**, confirm **further** a `from BRD:` line naming `<SLICE-KEY>` and the `parent:` its `brd-link.md` records — a run on this route is always slice-level, since step 1a refuses the container — its `depends-on:` if any, and which of `ard-seed.md` and `decisions.md` are present — also a stat.
   - **Resolve documentation grounding here, then show its line.** Run `resolve-docs-grounding create-ard` per `Skill(skill: "workflows-core:reference", args: "docs-grounding resolve-docs-grounding")` — its step 3.5 index prompt included — and show the `docs grounding:` line from what it returns, in the form that reference fixes — `ON <root> (retrieval: …)` or `OFF (<reason>)` — verbatim, including any index-build, staleness, or shadowing clause it carries (off switch: --no-docs). It runs here, before any agent is dispatched, because step 3.5 asks its one-time index question before the run's real work; this is the run's one resolution (`workflows-core:docs-grounding`, *Invariants*), and Phase 3 step 5 dispatches on the state it returns without resolving again.
2. **Refine vs fresh** (only if a prior `ard.md` exists): `choices: ["Refine the existing ARD (Recommended)", "Start fresh — rewrite it; decisions already on the default branch keep their IDs", "Cancel"]`. On **Refine** — and on **Start fresh** over an ARD already on the specs repo's default branch (`workflows-core:phase-handoff` §3's test), since downstream commands read an ARD only from there and so may cite its decisions — copy each prior ARD file to a temp path (`command mktemp -t dw-ard-prior-XXXXXX`, never inside a repo tree) before anything edits it, and record the path as `prior_ard`. Copy it as `<default-ref>` holds it (`git -C "$SPECS_PATH" show <default-ref>:<path relative to $SPECS_PATH>`, the ref `workflows-core:phase-handoff` §3 tests) where it is there, since that is the version anything downstream cites, and from the working tree otherwise; Phase 4.5's pre-lint reads it and Phase 5 hands it to `ard-reviewer`. Otherwise `prior_ard: none`.
3. **Repos search base (`$REPOS_PATH`).** Read `${REPOS_PATH:-/workspace}` (may be colon-separated): `choices: ["Use $REPOS_PATH (default /workspace) (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]`.
4. **Repo refresh policy** (governs Phase 3's `code-scanner`): `choices: ["fetch + pull default branch (Recommended)", "fetch only", "no refresh"]`.

---

## Phase 1.5 — Classify + model routing
Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then record:

```yaml
model_routing:
  classification: MODERATE | SIGNIFICANT | HIGH-RISK   # architecture; SIGNIFICANT common for cross-repo PRDs
  reason: <one-line>
  current_model: <the model this orchestrator/grill is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.1 Sonnet chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5-5, fallback claude-sonnet-5/4-6/4-5>   # the folder read, code-scanner, impl-maintenance
  review_model:    <§2 Opus chain>     # ard-reviewer (frontmatter-pinned; recorded, no override unless §10 enforces a model)
  authoring_model: <= current_model>   # the interactive grill + ARD authoring (session model, not a delegated subagent)
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2/§2.1 fallback or degradation>
```

**Unless `run_flags.enforced_model` is set (`workflows-core:model-routing/classification` §10 — then no gate fires): Tiered HARD model gate (like `/design`):** for `SIGNIFICANT` / `HIGH-RISK`, require an Opus session — if `current_model` is not an Opus-tier model, stop: `choices: ["I'll relaunch /product-workflows:create-ard on Opus (Recommended)", "Override — proceed on the current model (logged in the final report)", "Cancel"]`. The condition is `current_model` and not `opus_available`, per `workflows-core:model-routing/classification` §9.3: the ARD is authored inline on the session's own model, and `opus_available` reports what the environment carries rather than what this session runs. Where that gate fires with `opus_available` **also** false there is nothing to relaunch onto, so §9.3 drops the relaunch option and the array is `choices: ["Proceed on the Sonnet floor — the degradation is recorded in `notes` and the final report (Recommended)", "Cancel"]`. **Unless `run_flags.enforced_model` is set (`workflows-core:model-routing/classification` §10 — then no gate fires): for `SIMPLE`/`MODERATE`, degradation is advisory (record in `notes`).**

---

## Phase 2 — Read the PRD (+ Epic, + inherited ARD)

**The PRD read below runs on every route.** The BRD-route section at the end of this phase is an
**addition** to it, not a replacement: it reads the seed, the register and the findings a slice carries
and an idea-route folder does not, and it supplies the `(prd, epic)` pair the inherited-ARD resolution
uses. What it no longer does is stand in for the PRD read — Phase 0 step 1a means the BRD route resolves
a `PRD-` folder, so there is a `prd.md` to look for in exactly the place the idea route looks.
"Epic-level run" in the paragraphs immediately below means a run whose single address resolved to an
`EPIC-` folder. That folder carries no `brd-link.md` of its own, but **look one level up before
concluding the run is off the BRD route**: where its containing directory is a `PRD-` slice carrying
`brd-link.md`, this is the BRD route with that slice as the BRD folder and this Epic as the focus, and
the seed and the decision register are still read from the slice. (An Epic-level ARD also inherits the
PRD-level one, which softens the loss here where it does not in `/specify`.) Route aside, a slice's
`scope: epic` frontmatter (Phase 4) is a statement about altitude and inheritance, not about this phase's
run mode.

Read the PRD from the folder `resolve-address <PRD>` returned (`workflows-core:addressing` §3) — its `prd.md`, whose frontmatter is `kind: prd`, when present (authored source).

**Read the resolved folder directly.** PRD-level → its `prd.md`. Epic-level → the Epic folder's own
`specification.md` and `design.md` where present, plus the parent PRD folder's `prd.md` for the
product frame this Epic sits in.

**An absent `prd.md` is reported and never a stop, on either route.** Phase 0's gate has already
returned `absent` and printed the line naming the folder this run architects from instead; this phase
does not re-report it and does not escalate. On the BRD route that is the **ordinary** state, since
`/product-workflows:create-prd` is not a prerequisite for this command; on the idea route it is unusual but
supported, and it is the state the gate's row in
`workflows-core:phase-handoff` §3.4 preserves. Where the folder holds no `prd.md`,
the frame and themes below come from whatever else the folder carries — which on the BRD route is the
seed, the register and the findings the section at the end of this phase reads.

For an **Epic-level** run always dispatch the folder read this way (`depth: full`, scoped to `focus_key`) for the Epic's scope — the authored-PRD-file check above only applies PRD-level. Resolve any PRD-level ARD by invoking `Skill(skill: "workflows-core:reference", args: "ard-resolution")` and running its resolution with `prd: <PRD>`, `epic: null`, `$SPECS_PATH`. On `status: found`, load its `AD#N` invariants to **inherit read-only**. On `status: unmerged`, **stop**, naming the returned `branch` and any `pr`. On `status: none`, proceed unchanged — there is no PRD-level ARD to inherit.

Extract the problem/goal/scope frame + capability themes — the raw material for grounding + the grill.

### the BRD route — read the architecture-altitude seed and the register

On the BRD route this phase **additionally** reads the `PRD-` slice folder Phase 0 step 3 resolved —
additionally, because the PRD read above already ran against that same folder and found a `prd.md` or
reported its absence. `ard-seed.md`, `decisions.md` and `brd-link.md` are what a slice carries and an
idea-route PRD folder does not, and they are the whole of the divergence this route is entitled to
beyond grounding — which the paragraphs after this list read wherever `prd_dir` holds it, on
either route. Read exactly these, and no other seed:

- **`ard-seed.md`** — architecture-altitude content, when the folder holds any. **Where to look, and it is two places.** The resolved slice first. Then, when the slice holds none, the **parent BRD folder** named by `brd-link.md`'s `parent:` — that is where `--sort-existing` actually writes all three seeds, because slices do not exist when intake runs. A seed found there is BRD-wide content, not slice-scoped: read it as context for this slice, say which folder it came from, and never treat it as though it were written for this slice alone. Finding neither remains the ordinary case. **No `/brd-*` command creates this file on the normal route** — the one command that creates one is
  `/product-workflows:brd-intake --sort-existing`, a one-time migration path for a package authored
  by hand before this route existed. Its absence is therefore the **ordinary** case, not a
  degraded one, and is reported rather than treated as a gap; what the route actually carries at
  every altitude is `decisions.md`, filtered by `altitude`, plus the grounding files.
  **`prd-seed.md` and `spec-seed.md` are not read**, at all: they are the product and
  implementation altitudes of the same router, belonging to `/product-workflows:create-prd` and
  `/product-workflows:specify`, and pulling the first in would put product requirements into an ARD while
  pulling the second in would put a per-repo implementation plan into one — the two things
  `${CLAUDE_PLUGIN_ROOT}/references/ard-format.md`'s quality rules forbid from opposite directions.
- **`decisions.md`** — the register, per
  `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1. Phase 0's register gate has already gated it on the default
  branch, so what is read here is the merged register or, where the folder holds none, nothing. It is read through §8 there: a **torn write** — a record a `/brd-interview` run left when it
  stopped before writing the round record that would name it — is read as absent, frozen against
  nothing and stamped `consumed_by` by nothing.
- **`brd-link.md`** — for `parent:` and `depends-on:` only. This run reads no `claims:` list and no
  coverage ledger **as an authoring input**: PRD eligibility and the allocation gate are
  `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5's rule about authoring a **PRD**,
  applied "when eligibility is checked", and an ARD is not that artifact. Not checking it here is a
  decision, not an omission — `/product-workflows:create-prd` on the BRD route is where that gate lives, and
  this command is reachable without it.

  **Two places do open the ledger, and neither gates anything this run does.** Phase 7's
  next-step offer opens it and the `claims:` list: it decides whether
  `/product-workflows:create-prd <SLICE-KEY>` can be *named* at all, since that command refuses
  three BRD-route shapes and not one (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2).
  The Final report opens the ledger alone, reading its `disposition` column to leave out of the
  still-`consumed_by: none` list every finding about a row now `covered-by` another BRD — a report
  exclusion that changes no record. Reading a ledger to avoid offering a run that stops on arrival,
  or to count honestly, is not the same as gating this run on it.

**Absence is reported, never a stop, and the seed's absence is the ordinary case.** Nothing on the
normal route creates `ard-seed.md` at all (above), so a reconciled BRD routinely holds none. Say which
of `ard-seed.md` and `decisions.md` were absent — a reader cannot tell an unwritten file from an
unread one — and carry what is there.

**Partition the register before the grill starts, because the partition is what freezes it.** The
five states and their treatment are `decision-register-format.md` §3's, applied here exactly as
`/product-workflows:create-prd` on the BRD route applies them one altitude up: a `decided` record is an
**input** the ARD is authored from and never a question; `superseded` and `withdrawn` are terminal
and read for context only; `open`, `reopened` and an open `[AS#n]` are **gaps**, which may not be
consumed downstream while open (§3) and reach the ARD's `## Open questions` by id rather than being
quietly settled. Carry each `decided` record's `altitude` with it: only `architecture` ones have a
home here, and a `product` or `implementation` decision is read for context and **left for the
command that authors at its altitude** — `/product-workflows:create-prd` and `/product-workflows:specify` —
and it is not discarded by being skipped. **The channel that carries it is `decisions.md` itself, not
a seed file.** Both of those commands read this same register and filter it by `altitude` exactly as
this phase does, so a decision skipped here is picked up there from the file it was already in.
`prd-seed.md` and `spec-seed.md` are created by nothing on this route — only
`/product-workflows:brd-intake --sort-existing` creates one, migrating a package authored before the route
existed — so naming a seed as the thing that carries it would send a reader after a file that is not
there.

### grounding — read wherever `prd_dir` holds it, on either route

Where `prd_dir` carries `grounding/code-grounding.md` and/or `grounding/design-grounding.md`
— the idea-route PRD folder as readily as the BRD-route slice, since `/product-workflows:prd-ground`
now writes both from either — read the `[CG#n]` and `[DG#n]` finding records, per
`workflows-core:grounding-format` §2. A BRD ground with `--no-design` still holds a
`design-grounding.md` — `/prd-ground` Phase 8 writes it on every run, carrying a note saying the pass
was skipped and why, plus a `## Frame sets covered` census of the `design/` subdirectories on disk.
Absent means the file is not there at all, never that design grounding was declined. Say which of the
two files were absent — a reader cannot tell an unwritten file from an unread one — and carry what is
there. Where `git -C "$SPECS_PATH" status --porcelain -- <file>` lists either file present, say
so in the Final report — it is read as the working tree holds it, uncommitted, and that is a note,
never a stop. Where `prd_dir` holds neither file, report that and proceed exactly as this command
did before this feature — grounding is optional to this command and nothing here gates on it. **On an
Epic-level run `prd_dir` is the PRD folder above the Epic**, whose findings cover the whole PRD: read
them all, draw on those bearing on the Epic's scope, and let Phase 6 stamp only what this ARD drew on
— a finding about a sibling Epic's scope stays `none`, as any finding read and not used does.

**A finding with no verifier outcome is not evidence** (`workflows-core:grounding-format` §8) and may neither
seed `## Grounding findings (architecture as-is)` nor be marked `consumed_by` anything. Carry only
findings that hold one, keep each one's `[CG#n]`/`[DG#n]` id and its pinned `commit` where it is
cited, and name any finding offered that was dropped for want of an outcome.

**A `will-change` finding names a prerequisite decision that overturns it, where one is recorded**
(`workflows-core:grounding-format` §5). Record it under `## Open questions` — or `## Deferred` where
the prerequisite is what defers it. **On the BRD route only**, a `decided` record may carry a
`conditional_on: <BRD-KEY>/<decision-id>` (`decision-register-format.md` §5), which is architecture
the ARD must not state as settled either: name the prerequisite BRD and the specific decision
alongside the `depends-on:` list `brd-link.md` carries. An idea-route folder holds no `decisions.md`
and so records no `conditional_on` — a `will-change` finding there still gets the `## Open questions` /
`## Deferred` treatment on its own account, naming only the finding.

**Inheritance on the BRD route uses `brd-link.md`'s `parent:`, never a segment count.** Resolve any
inherited ARD by invoking `Skill(skill: "workflows-core:reference", args: "ard-resolution")` and
running its resolution with:

- **a `parent:`** (this folder is a slice — the only shape this route resolves, since step 1a
  refuses the container) → `prd: <parent-key>`, `epic: <SLICE-KEY>`.

The second mapping needs no change to that reference: a slice folder sits inside its parent's exactly
as an Epic subfolder sits inside a PRD dir, which is the layout its Epic-level branch already
collects — the slice's own `ard.md` plus the parent BRD folder's `ard.md` for inherited
invariants. Act on the returned `status`: `found` → inherit those `AD#N` read-only;
`unmerged` → **stop**, naming the returned `branch` and any `pr`; `none` → proceed unchanged.

**This subsection loads `ard-resolution` itself, and the second load site is deliberate.** The other
one is in this phase's Epic-level paragraph, so it neither runs on a PRD-level run nor is guaranteed
to stay above this subsection if the phase is ever reordered — and nothing in either place asserts
that ordering. A reader who arrives here has the load in front of them and needs nothing above it.

---

## Phase 3 — Architect-driven grounding (no PRs)
There are no PRs at ARD time, so repos are **architect-driven**, not PR-derived:
1. **Cheap discovery.** List the top-level directories under each `$REPOS_PATH` entry (`ls`). Optionally attach each dir's one-line identity — `timeout 5 git -C <dir> remote get-url origin 2>/dev/null` (slug) or its README first heading. Do **not** deep-scan to guess relevance.
2. **Propose + ask.** **Where `prd_dir` holds verified `[CG#n]`/`[DG#n]` grounding, seed the
   theme set from those findings before falling back to the PRD/Epic-derived themes** — the same
   composition `workflows-core:model-routing/classification` §8.5's seeded second round already
   establishes for a scan narrowed by verified anchors, applied here to a folder's own grounding corpus
   rather than to a prior scan round. A finding whose verdict says a capability is absent is a theme
   worth scanning, since that is where the work still needs doing; one whose verdict says it is present
   names the code that already implements the capability, so the scan is directed at it rather than
   searching blind for it. This does not replace the scan below — `workflows-core:grounding-format` §1
   draws that line: `code-scanner` output is a capability inventory, not a finding — so the seeding only
   changes where the themes come from; a folder with no grounding derives its themes exactly as this
   command always has, and this scan is never skipped, made conditional, or put behind a flag. From the
   PRD/Epic themes — seeded from grounding where it is present, derived as before where it is not —
   propose a `theme → component` mapping against those dirs, and **ask the architect to confirm / correct / add / group**, a component's `kind` included — a gitops repository with no deploy directory §2 names is proposed as `code` and is corrected to `deploy` here. A component is a repository or a module inside one (`workflows-core:components` §1). On a PRD-level run, run `enumerate-components` (§2) over each repository a theme reaches and propose the modules the themes touch, never every module the repository declares; a repository that declares none is proposed whole. On a refine run (Phase 1's refine-vs-fresh), the existing ARD's `components:` — its groupings and corrected kinds included — is proposed first. Where Epics under the PRD already carry `target:` values (§3's `epic-targets` source — a PRD split before this ARD existed), propose each of them too, so the set the ARD fixes holds every target already in use. On an Epic-level run the proposal starts from the Epic's `target:` and from the producer of every interface its `## Contract` consumes. For any requirement that maps to no obvious component, **ask outright**: "which repo, or which module of it, covers `<X>`?" On a PRD-level run the confirmed list is the ARD's `components:` (§5) — each entry's `paths` passed to step 4's scan as `search_hints.paths` — and with two or more `kind: code` components, Phase 4 authors `## Contracts`.

   **On the BRD route the proposal additionally starts from the slice folder's
   `grounding/baselines.md`**, which already records repository → pinned commit for every repo
   `/product-workflows:prd-ground` read. That is joined to the themes above, not substituted for them: the
   PRD read in Phase 2 runs on this route too, so where the slice holds a `prd.md` its themes are in
   hand and a pinned repo set corroborates them; where it holds none — the ordinary BRD-route state —
   `baselines.md` and the register's decisions are the whole of the starting set, and that is still a
   better one than a theme guess. Either way it
   is only a proposal: the architect confirms, corrects and adds exactly as above, and a repo
   `baselines.md` names but `$REPOS_PATH` does not hold reaches step 3's mount-or-descope gate like
   any other. A finding's evidence is cited at the commit that finding is pinned to
   (`workflows-core:grounding-format` §2), which is not necessarily the commit a
   fresh scan reads; where the two differ, say so beside the claim rather than silently re-dating it.
3. **Missing repo → consolidated mount-or-descope gate:** `choices: ["Mount now & re-scan", "Ground only the confirmed-mounted set (record the rest as open questions)", "Specify an absolute path for this repo", "Cancel"]`.
4. **Ground the confirmed set.** Spawn `code-scanner` in batches of up to 4 concurrent agents per Agent message on the confirmed repos (wait for each batch), scoped by the themes:

   → Agent (subagent_type: "workflows-core:code-scanner", model: `<detection_model — §2.1 Sonnet chain>`):
     > "repo_path: <resolved absolute path>
     >  repo_url_slug: <slug>
     >  capability_themes: [themes]
     >  context: |
     >    [3–5 sentences: the PRD/Epic goal, what the ARD must ground]
     >  search_hints: { symbols: […], paths: […], keywords: […] }
     >  refresh: { switch_to_default_branch: [per Phase 1], pull: [per Phase 1] }"

   Store the per-repo as-is findings (`file:line`). Descoped/unmounted repos become Open questions.

   **Per-repo scanner status.** Wait for each batch. Handle each returned status before continuing:

   - `OK` / `PARTIAL` / `EMPTY` — use the result. `PARTIAL` and `EMPTY` are data, not failures.
   - `REPO_MISSING` — escalate per the `Repo missing (after resolution)` rule in `workflows-core:escalation-rules`.
   - `DIRTY_TREE` — escalate per the `Dirty working tree` rule in the same file.
   - `REFRESH_BLOCKED` — escalate per the `Refresh blocked` rule in the same file.
   - `prep.read_only: true` — not a failure. The scan ran at `prep.scanned_ref`. Escalate per the `Read-only mount — ref stale or diverged` rule **only** when `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`; otherwise proceed silently and cite evidence at `prep.scanned_ref`.

   A repo the user skips is dropped from the confirmed set and named in the Phase 6 handoff; it never silently disappears.
5. **Documentation grounding (optional).** Phase 1 resolved it and showed its line — before this phase's `code-scanner` dispatches — and this step resolves nothing again. Where it resolved `docs_grounding: ON`, `dispatch-docs-grounder` (`workflows-core:docs-grounding`) with `feature_summary` = the PRD/Epic goal + capability themes, `key` = `<PRD>` (PRD-level) or `<EPIC>` (Epic-level), `themes` = the confirmed themes. Carry the digest into the Phase 4 grill with **grill-rank** consumption (documented analogs and building-block altitude/permissions are strong ARD grounding). Where it resolved OFF, dispatch nothing.

---

## Phase 4 — Author via grill
**Interview technique (grilling — embedded; no runtime dependency).** Conduct a **relentless** interview per `Skill(skill: "workflows-core:reference", args: "grilling-technique")` — one question at a time, recommend each answer, explore the Phase 3 grounding findings / the PRD to self-answer (fact-vs-decision), ask from the frontier, and clear the confirmation gate before writing each section.

Author the ARD live against `${CLAUDE_PLUGIN_ROOT}/references/ard-format.md`, applying the no-hard-wrap prose convention in `Skill(skill: "workflows-core:reference", args: "prose-formatting")`, at the resolved altitude: Context → Grounding findings (cite `file:line`) → Architecture decisions (`AD#N`: Binds/Prevents/Rule/Alternatives) → Cross-repo/component approach → Contracts (PRD level, two or more code components) → Stack & invariants → Edge cases & risks → Open questions → Deferred. At Epic level, list inherited PRD-level ADs read-only and never contradict them; PRD level stays at invariants/frame (no per-repo detailed solutions). Grill each decision's **Alternatives** — what else was weighed and why it lost; a decision that beat no other option goes to Deferred for `/design`. Wherever `prior_ard` is set, a decision whose Rule changes is a new `[AD#M]` and the old one gains `**Superseded by:**`, and one made moot with no replacement gains `**Withdrawn:**` — never rewritten in place or dropped, since downstream artifacts cite it by ID (`ard-format.md` § Superseding a decision).

**Components and contracts.** On a PRD-level run, write `components:` as Phase 3 confirmed it (`workflows-core:components` §5). Where it has two or more `kind: code` entries, author `## Contracts` (`${CLAUDE_PLUGIN_ROOT}/references/ard-format.md` § Sections): for every capability the Capability→Architecture map lands in two or more `kind: code` components, settle the interface — its kind, producer, consumers, schema owner, versioning and compatibility, and whether the contract is a code artifact and where — and write it as an `AD#N` whose Rule states it, with its row in the interface table; then the landing order. The grill's *Cross-component* gap category (`workflows-core:grilling-technique`) applies here. The ARD of an `EPIC-` folder (an Epic-level run) carries no `components:`, and its inherited interface rows are read-only, like its inherited `AD#N`; a BRD-route slice's ARD is a PRD-level run's, whatever its `scope:` reads, and carries them.

### the BRD route — the seed fills the sections, and the grill is restricted to gaps

**Where the seed's content lands.** `[CG#n]`/`[DG#n]` findings seed
`## Grounding findings (architecture as-is)`, each keeping its own id and citing the `file:line`
evidence at the commit it is pinned to. Architecture-altitude `decided` records seed
`## Architecture decisions`: the record's `statement` and `argumentation` become the `[AD#N]`'s
substance, and the grill supplies the **Binds** / **Prevents** / **Rule** triple
`${CLAUDE_PLUGIN_ROOT}/references/ard-format.md` requires and the register does not carry. Naming the
`[VD#n]` or `[CD#n]` beside the `[AD#N]` it became is what keeps the two records findable from each
other. **A decision does not automatically earn an `[AD#N]`**: `ard-format.md`'s three-part test —
hard to reverse, surprising without context, the result of a real trade-off — still applies, and a
`decided` record failing it belongs in the ARD's prose or is left to `/dev-workflows:design`. Saying
which of the two happened is part of the consumption report (Phase 6).

**The grill may fill anything the seed does not settle. It may not reopen a `[VD#n]` or a `[CD#n]`**
(D3). Those decisions arrive carrying customer sign-off in writing, and a grill that re-litigates one
manufactures a contradiction between this ARD and a document the customer has already agreed to.
Three things make that a guarantee rather than an instruction:

1. **The question set is a subtraction, not a sweep.** Phase 2's partition already sorted the register
   into inputs, terminal records and gaps; the grill's questions come from the gaps and from what
   `ard-seed.md` leaves unstated. A settled `chosen` is never a question, so there is nothing for the
   interview to walk it back through.
2. **This run cannot satisfy either cause that would license a reopening.**
   `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4 admits exactly two — a new
   grounding finding, or an incoming customer decision — and this command produces neither: the
   architect-driven scan in Phase 3 is `code-scanner` output, which
   `workflows-core:grounding-format` §1 says is a capability inventory and
   explicitly **not** a finding, and no customer review reaches the register except through
   `/product-workflows:brd-reconcile`.
3. **The only field of a decision record this command may write is `consumed_by`** (Phase 6).
   **Every other field `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1 defines is
   never written here, on any record, in any status** — named as a set rather than enumerated, so a
   field §1 gains is covered the day it gains it and no list here can drift from the one it stands
   for. That set takes in every field a re-decision or a reversion writes **save `consumed_by`**,
   the one field this command does write and the one both of those return to `none`; the two
   writing sets are §4's to fix, and this command performs neither — a re-decision needs a
   reopening, which rule 2 has just ruled out, and a reversion is
   `/product-workflows:brd-reconcile`'s propagation sweep alone (§4). So a grill
   answer contradicting a `decided` record could not become that record's new `chosen` even if the
   first two failed.

**What happens when the grill surfaces a genuine contradiction with a settled decision** — which is
useful information, not something to suppress. Do not decide it and do not soften it into the ARD's
prose. Record it under `## Open questions`, naming the `[VD#n]` or `[CD#n]` it contradicts and what
this run believes contradicts it, and name the route that may act on it. **Neither route is this
command**, and both are exactly §4's two causes rather than a third invented here: a `[VD#n]` needs a
new grounding finding, which only `/product-workflows:prd-ground <SLICE-KEY>` mints — with
`--rebaseline` where the pinned code has moved — and
`/product-workflows:brd-interview <SLICE-KEY>` then re-decides against; a `[CD#n]` needs the customer,
through `/product-workflows:brd-package <SLICE-KEY>` and then
`/product-workflows:brd-reconcile <SLICE-KEY> @<review-file>`. This is not the `## ARD deviations`
convention — that one is for a *consumer* departing from an `AD#N`
(`workflows-core:ard-resolution`), and this run is the ARD's author.

**Frontmatter on the BRD route**, per `ard-format.md`'s block, each field read from what Phase 2
already holds and none of them asked of the user:

- `scope: epic` — the route resolves a slice and nothing else (Phase 0 step 1a), and every slice
  takes this scope. Not because a slice is an Epic, but because `scope` selects the altitude rule
  `ard-reviewer` applies and the inheritance shape `workflows-core:ard-resolution` reads, and a slice sits in
  both exactly where an Epic does — one level down, inheriting its parent's `AD#N` read-only.
- `prd:` and `epic:` are the same pair Phase 2 passed to `resolve-ard`: the `parent:` key and
  `<SLICE-KEY>`. Frontmatter and resolver agree
  because they are written from one resolution, not two.
- `inherits:` the parent BRD folder's `ard.md` when `resolve-ard` returned one, else `null`.
- `derived_from:` the PRD file in this BRD folder when one is there — the ordinary case, since this
  route is normally reached from `/product-workflows:create-prd`'s own next-step offer on the BRD route — else
  the resolved `PRD-` slice folder's own `ard-seed.md`, the artifact this ARD was actually authored from. The field records
  provenance, and naming a PRD path in a folder that holds no PRD would name a file that does not
  exist.
- `grounded_repos:` unchanged — the repos Phase 3 confirmed, which is what every `file:line` in the
  ARD must cite into.
- `components:` as on any PRD-level run — the components Phase 3 confirmed (`workflows-core:components` §5).

**Per-area split.** If (Epic level) the confirmed grounding spans separable areas in one repo (e.g. `server/` backend + `ui/` frontend), grill: `choices: ["One combined ARD (Recommended)", "One ARD per area (backend / frontend / …)"]`. On per-area, author one `ard-<area>.md` per area (each with its own `area:` frontmatter).

---

## Phase 4.5 — Structural pre-lint

Before the review gate, run the deterministic checks in `Skill(skill: "workflows-core:reference", args: "pre-lint")` against the drafted `ard.md`: the **Universal checks**,
the **key-collision** check (run on the ARD body below the frontmatter), and the **ARD** block
(incl. that every `### [AD#N]` carries `**Binds:**` / `**Prevents:**` / `**Rule:**`, a live one `**Alternatives:**`, every `**Superseded by:**` names a live decision, and every `**Withdrawn:**` gives a reason). Surface every
finding; inline-fix the mechanical ones (renumber a duplicate `[AD#N]`, delete a stray placeholder
token); leave content gaps for the grill/author. **Advisory** — never blocks;
proceed to Phase 5 once findings are surfaced. `ard-reviewer` remains the gate.

**On the BRD route, a `<BRD-KEY>` in the ARD body is the auto-link check's third branch, not its
second.** The body legitimately names prerequisite BRDs — a `will-change` finding's prerequisite, a
`conditional_on` decision's — and the collision grep matches the leading two segments of any of them.
A BRD key is not a requirement ID and it is **not a real tracker ticket**: it is a folder name under
`$SPECS_PATH`, validated for shape and never checked against a tracker
(`workflows-core:addressing` §1). So it falls to the "neither" branch —
**MINOR, left exactly as written, reported**. Never wrap it as `[[KEY-123]]`: that branch is for a key
in a project that actually exists, and wrapping a BRD key would mint a dangling link to a ticket
nobody created.

## Phase 5 — Review gate
Dispatch `ard-reviewer` (Opus, frontmatter-pinned; recorded as `review_model`, no override unless §10 enforces a model):

→ Agent (subagent_type: "product-workflows:ard-reviewer", model: `<review_model — §2 Opus chain, equal to ard-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the ARD:
  >
  > ARD path: [absolute path to the ard.md]
  > Scope: [prd | epic]
  > Prior ARD: [prior_ard — the temp copy of this ARD as it stood before this run, or none]"

On `BLOCK`, fix the BLOCKER findings inline (the orchestrator/grill edits the ARD — no delegated writer) and re-review **once**; if still `BLOCK`, escalate per the `Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline` rule in `workflows-core:escalation-rules`. `PASS` / `PASS WITH RECOMMENDATIONS` → proceed. Cap: one fix cycle + one re-review. (For a per-area split, review each area ARD, each with its own prior copy.) Once the last review has returned, remove every `prior_ard` copy with `command rm -f --`.

**The recorded verdict names the version it was taken against** — where any edit followed it, the final report says so and names the edits, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Where none did, it says that too.

---

## Phase 6 — Handoff
Write the ARD file(s) into the feature folder.

**Wherever `prd_dir` holds `grounding/`, on either route, close the consumption loop before
the offer.** The design's *Consumption tracking* section (§7.3) has every finding and decision record
a `consumed_by`, so that "nothing was lost" is checkable rather than hoped for. Set `consumed_by: ARD`
on each `[CG#n]`/`[DG#n]` finding in `<prd_dir>/grounding/code-grounding.md` / `<prd_dir>/grounding/design-grounding.md`
**this ARD actually drew on** — and on nothing else: a record read for context and not used is still
`none`, and marking it consumed would report a routing that never happened. A finding with no verifier
outcome is never marked, whatever the ARD did with the claim, because it was never evidence
(`workflows-core:grounding-format` §8). **On the BRD route, additionally**, set `consumed_by: ARD` on
each architecture-altitude `decided` record in `decisions.md` this ARD actually drew on, under the same
exclusion. These are the **only** writes this command makes into a grounding file or, on the BRD route,
into `decisions.md`, and none of them is a `status` change or any other field (Phase 4). Everything at
architecture altitude still `none` afterwards goes in the final report by id, per §7.3.

**`ard-seed.md` is reported, not stamped**, for the reason the field's own authorities give:
`consumed_by` is a field of a *record* — defined on a decision by
`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1 and on a finding by
`workflows-core:grounding-format` §2 — and the seed carries neither, so there is
no per-item field to write and inventing one would mint a format this command alone understood. The
seed's consumption is reported at **file** granularity in the final report (consumed, or consumed in
part with what was left over).

Then **offer** (commit-when-asked — never automatic), invoking `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and presenting its §4.3 choice array verbatim — **two arrays, selected by the `deliverable_paths` set below, per §4.1's set rule.** Where that set is the ARD file(s) **alone**, present §4.3's **gated — falling back** array (§4.1 bullet 2): `choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase does not stop on this, but until this is on main it might not read your copy)", "Cancel"]`. Every §3.4 row naming an ARD preserves `status: none` and `ard-resolution.md`'s no-regression rule, so `/specify`, `/dev-workflows:design`, `/dev-workflows:implement`, `/epics` and `/dev-workflows:ready` each proceed without it rather than stopping, and the stopping array would promise a refusal none of them makes. Where the set **also** carries `grounding/code-grounding.md`, `grounding/design-grounding.md` or `decisions.md`, present §4.3's **gated — stopping** array (§4.1 bullet 1) instead: `choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]` — `/brd-split` and `/brd-interview` stop on the grounding files, and `/brd-package`, `/product-workflows:create-prd` and `/product-workflows:specify` on the register (each of the last two in its Phase 0 register gate), and a set spanning both halves takes the stopping one. On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix: ard`; `feature_folder` as resolved in Phase 0 (the PRD dir for a PRD-level ARD, the Epic subfolder for an Epic-level ARD — §2.2 derives `ard/<PRD>-<vslug>` or `ard/<EPIC>-<eslug>` from it); `deliverable_paths` = the ARD file(s) — **plus, wherever `prd_dir` holds `grounding/`, `<prd_dir>/grounding/code-grounding.md` and `<prd_dir>/grounding/design-grounding.md`, and, additionally on the BRD route, `<prd_dir>/decisions.md`** — the slice folder's register, the slice being `prd_dir` on that route — because the `consumed_by` writes above land in those files and an uncommitted consumption record is one no later run can read. **Name all three at `prd_dir`, never at `feature_folder`**: on an Epic-level run `feature_folder` is the `EPIC-` subfolder, while the grounding files and the register are the PRD folder's — the slice's, on the BRD route — in the directory containing it, the one this run reads them from and stamps them in, so a path formed against `feature_folder` would name a file that does not exist and leave the stamp uncommitted; on a PRD-level run the two folders are the same and nothing changes; `ard-seed.md` is not staged, because this run does not write to it; `title: <PRD|EPIC> Add architecture requirements document`; and `body_facts` = the ARD scope (PRD/Epic, any per-area split), the grounded/descoped repos, the `AD#N` count, the open-question count, the `ard-reviewer` verdict, and how many items were marked `consumed_by: ARD` — and, on the BRD route, the `<SLICE-KEY>` this ARD was seeded from. Emit its §4.1 outcome line in the Final report.

**On a PRD-level BRD-route run the feature folder is the resolved `PRD-` slice folder**, so §2.2 derives the
branch `ard/<SLICE-KEY>-<slug>` from its own basename, not from a re-derived title; on an Epic-level run
under a slice it is the `EPIC-` subfolder and the branch is `ard/<EPIC>-<eslug>`, as on the idea route. Neither name collides with the `prd/` branch `/product-workflows:create-prd` derives on the BRD route for the same key, the `spec/` one `/product-workflows:specify` derives on the BRD route, or the
`/brd-*` family's shared `brd/` one, because §2.2's prefix is the caller's own. The commit message's key is the run's key, resolved as Phase 8 resolves it.

---

## Phase 7 — Next-step offer (adaptive)
**One precondition governs every `/product-workflows:epics` option below, on both routes.** `/epics`
accepts a folder holding a `prd.md` that asserts `kind: prd` and refuses one that does not
(`commands/epics.md` Phase 0 step 1b, `EPICS_NO_PRD`). This run does **not** require a PRD — its
`require-on-main` gate has an `absent` branch that architects from the resolved folder, and on the
BRD route `/product-workflows:create-prd` is not a prerequisite at all — so the folder it just wrote
an ARD into may legitimately hold no PRD. **Test the resolved folder for an authored `prd.md`**
before rendering the array: where there is one, offer `/product-workflows:epics`; where there is
not, **the option becomes `/product-workflows:create-prd <ADDRESS>` — but only where that command
can itself run**, and it becomes it whole: the lead-in, the role label and the `<merge-clause>` all
belong to the command an option names, so none of the three is carried over from the option it
replaces. The test runs on a PRD-level run only, the one whose array names `/epics` or
`/create-prd`; an Epic-level run's array names neither (below), so the `EPIC-` folder it resolved,
which holds no `prd.md` by construction, is never tested and `/create-prd` is never offered on the
Epic's key. On the
BRD route the branches are written out as separate literal arrays below rather than substituted into
one, which is what keeps that rule checkable by reading. Offering `/epics` on a folder holding no
PRD would name a run that stops on arrival, and naming `/create-prd` without the test below does the
same thing one command further on.

**`/create-prd` refuses three BRD-route shapes, not one**
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2, the authority, not restated
here). A PRD-level run has cleared only the container refusal, by resolving a `PRD-` folder itself.
The other two are data refusals on a slice's own ledger and exist only where the resolved folder
carries a `brd-link.md`; an idea-route PRD folder has no gate set, so `/product-workflows:create-prd
<ADDRESS>` is reachable there on the `prd.md` test alone. Where the folder is a **slice**, read its
`coverage-ledger.md` — the rows its `brd-link.md` `claims:`, out of the file and never off a
`ledger:` line (§6.1) — and resolve the replacement from it. **The table names the command; it never
supplies the option text.** On the BRD route its five rows pick among the last five of the six literal arrays below — the
empty-gate-set row choosing between the fourth and the fifth by the parent's own ledger, and the fourth and fifth rows sharing the last, which the empty-gate-set row also takes where the parent's ledger cannot be read — the first being taken on the `prd.md` test alone. On the idea route no row of it fires at all — that folder carries
no `brd-link.md` and so has no gate set — which is why the PRD-level bullet can write its one
substitution out in full, `/create-prd` being reachable there on the `prd.md` test alone:

| The slice's gate set | The command that replaces it |
|---|---|
| No row `unallocated`, and at least one `covered-here` | `/product-workflows:create-prd <SLICE-KEY>` — all three refusals cleared |
| A row still `unallocated` | `/product-workflows:brd-split <SLICE-KEY>` instead: `/create-prd` would raise `CREATE_PRD_BRD_UNALLOCATED`, and that walk is what moves those rows (allocate-only on a slice). Its own Phase 0 gates on this slice's grounding findings carrying a verifier verdict, so say so beside the offer |
| No row `covered-here`, gate set **empty** — `brd-link.md` claims nothing | `/product-workflows:brd-split <PARENT-KEY>` instead — the keep-or-remove run for a standing empty child, and not a no-op there — in the form the parent's own ledger decides, exactly as `/product-workflows:create-prd` Phase 0 step 7's empty-gate-set row decides it: where that ledger still holds an `unallocated` row, `/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"`, since that run walks the row too and stops with `BRD_SPLIT_NEEDS_INSTRUCTION` without an instruction; where it holds none, the bare form; where it cannot be read, report it by path and name neither form |
| No row `covered-here` and none `unallocated`, gate set **non-empty** | **Drop the option and name nothing in its place.** `/create-prd` would raise `CREATE_PRD_BRD_NOT_ELIGIBLE`, whose non-empty branch names no command at all by design; say instead what the gate-set rows resolved to and that nothing in the plugin moves a terminal row back to `unallocated` |
| No readable `coverage-ledger.md` beside the `brd-link.md` — absent, or present and unreadable — while that file claims rows | **Drop the option and name nothing in its place**, and report `<slice-dir>/coverage-ledger.md` by path, as missing or as unreadable with the read error: this is not an empty gate set, and `coverage-ledger-format.md` §5.2 forbids resolving it to the empty row's `/brd-split <PARENT-KEY>` |

**Dropping rather than annotating follows `commands/brd-reconcile.md` Phase 14**, which runs these
same two data tests before offering `/product-workflows:create-prd <SLICE-KEY>` and drops the option on
the stated ground that a hard refusal in another command's Phase 0 is not a state the reader can
judge for themselves. Where the option is dropped and nothing replaces it, the array still holds
`/product-workflows:specify <SLICE-KEY>` and `"Stop here"`, so it never falls below the two options
`AskUserQuestion` requires.

- **PRD-level ARD:** if the PRD has 0 Epics → `choices: ["Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE) (Recommended) <merge-clause>", "Author a PRD-level spec — /product-workflows:specify <PRD> (PE) <merge-clause>", "Stop here"]` — with the first option becoming `"Author the PRD — /product-workflows:create-prd <ADDRESS> (PM) (Recommended)"` where the precondition above fails; else offer `/product-workflows:specify <PRD>` (PE) carrying the same `<merge-clause>`. *(No `/design` — no Epics yet.)* **Where this run wrote `components:` with two or more `kind: code` entries and the PRD has 0 Epics**, the first two options swap and the marker moves with them — `choices: ["Author a PRD-level spec — /product-workflows:specify <PRD> (PE) (Recommended) <merge-clause>", "Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE) <merge-clause>", "Stop here"]` — because the end-to-end acceptance criteria a PRD-level spec states are what `/epics` splits across the components, and `/epics` stops to recommend that spec where it is missing (`workflows-core:components` §6). Where the `prd.md` precondition above fails, the array above applies unchanged.
- **Epic-level ARD:** `choices: ["Author the spec — /product-workflows:specify <EPIC> (PE) (Recommended) <merge-clause>", "Hand to Dev — /dev-workflows:design <EPIC> (Dev) <merge-clause>", "Stop here"]` — one address each, the Epic's own, because that is the only form either command accepts (D4). **Epic fan-out** — repeat this ARD for a sibling Epic: `/product-workflows:create-ard <SIBLING-EPIC>`; that run inherits the PRD-level ARD, not this Epic-level one, so it waits on nothing this run produced and carries no clause.
- **the BRD route (an ARD in a `PRD-` slice folder):** different arrays, because **the key this run
  holds is a slice key**: `/dev-workflows:design` cannot be reached with one at all, and the second
  option is not a fixed command — this phase's opening precondition decides which command it names,
  or whether the array has one. **Six literal arrays, one per branch of that test — the
  standing-empty-child branch split in two by the parent's ledger, the missing-ledger branch sharing the last.** They are written out rather than derived by substituting a command into one array, and the reason is the
  rule stated with the precondition: an option's lead-in, its role label and its `<merge-clause>`
  each belong to the command that option names, and none of the three survives a different command
  being put in its place. Present the one whose condition holds, verbatim, per
  `workflows-core:escalation-rules`.
  - **The slice holds an authored `prd.md`** — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Hand to a Product Engineer — /product-workflows:epics <SLICE-KEY> (PE) <merge-clause>", "Stop here"]`
  - **No `prd.md`, and the gate set clears both data tests** — no claimed row `unallocated`, at least one `covered-here` — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Author this slice's PRD — /product-workflows:create-prd <SLICE-KEY> (PM) <merge-clause>", "Stop here"]`
  - **No `prd.md`, and a claimed row is still `unallocated`** — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Allocate this slice's ledger — /product-workflows:brd-split <SLICE-KEY> (PM) <merge-clause>", "Stop here"]`
  - **No `prd.md`, no row `covered-here`, the gate set is empty — a standing empty child — and the parent's own `coverage-ledger.md` still holds an `unallocated` row** — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Keep or remove this empty slice — /product-workflows:brd-split <PARENT-KEY> \"<how to cut it>\" (PM)", "Stop here"]` — that run walks the parent's unallocated row too and stops with `BRD_SPLIT_NEEDS_INSTRUCTION` without an instruction, so the bare form would name a run that stops on arrival (`/product-workflows:create-prd` Phase 0 step 7's empty-gate-set row).
  - **No `prd.md`, no row `covered-here`, the gate set is empty, and the parent's own `coverage-ledger.md` holds no `unallocated` row** — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Keep or remove this empty slice — /product-workflows:brd-split <PARENT-KEY> (PM)", "Stop here"]`
  - **No `prd.md`, and either no row `covered-here` and none `unallocated` with the gate set non-empty, or no readable `coverage-ledger.md` while `brd-link.md` claims rows, or the gate set empty and the parent's `coverage-ledger.md` unreadable** — `choices: ["Author this slice's specification — /product-workflows:specify <SLICE-KEY> (PE) (Recommended) <merge-clause>", "Stop here"]` — the second option is dropped and nothing takes its place, per the precondition table's third, fourth and fifth rows; say instead what the gate-set rows resolved to, or, where a ledger is missing or unreadable, report it by path.
  - **`/product-workflows:specify <SLICE-KEY>` is always reachable from this state.** It takes
    the same slice key this run resolved — and passes that command's own container refusal for the
    same reason this run did, finds the same folder through `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), and needs no key minted anywhere else. It
    resolves this ARD through `workflows-core:ard-resolution` and
    stops on `status: unmerged`, so the wait is real and the clause is required.
  - **`/product-workflows:epics <SLICE-KEY>` is the second option of the first array only, the one
    taken where the slice holds an authored `prd.md`.** `/epics`
    resolves the same folder this run resolved, through the same `resolve-address`, and reads the
    PRD there — a slice is a `PRD-` folder, so it passes that command's container refusal exactly as
    this run did. But **this route does not require a PRD**: `/product-workflows:create-prd` is not a
    prerequisite for it, so a slice carrying an ARD and no `prd.md` is an ordinary state, and
    `/epics` refuses one (`EPICS_NO_PRD`). **This route is where the second half of that test
    matters most**, because it is the route on which the folder has a gate set: a slice that is
    ground and fully allocated with every claimed row `deferred-to` or `rejected`, and no `prd.md`,
    is an ordinary state of *this* route, and naming `/product-workflows:create-prd <SLICE-KEY>` there
    would send the operator into `CREATE_PRD_BRD_NOT_ELIGIBLE` — the one branch on this route that
    names no command at all. The test is the precondition stated above this list, and it is a real
    test again — unlike the one it replaces, which looked for an export directory under the key and
    guarded a lookup that no longer happens. Like `/specify`, `/epics` resolves this ARD through
    `workflows-core:ard-resolution` and stops on `status: unmerged`, so its option carries the clause
    too.
  - **The three replacement commands differ over the clause, which is the other half of why each
    array is written out.** `/product-workflows:create-prd <SLICE-KEY>` is not one of
    `workflows-core:ard-resolution`'s consumers, so it reads this ARD not at all — but on the BRD
    route its Phase 0 step 7a gates the slice's `decisions.md`, which this run's handoff stages
    wherever it stamped `consumed_by: ARD` on a register record, so its option **does** carry the
    clause. (Its `idea.md` gate is idea-route only, and this array is the BRD route's.) `/product-workflows:brd-split <SLICE-KEY>` runs
    `allocate-only`, and its Phase 0 step 6 executes `require-on-main` against **this slice's**
    `grounding/code-grounding.md`: wherever `prd_dir` — on this route the slice — holds `grounding/` that is a file
    this run's own handoff stages, because the `consumed_by: ARD` writes land in it, so that option
    **does** carry the clause — and say beside it that the same Phase 0 also gates every finding on
    carrying a verifier outcome. `/product-workflows:brd-split <PARENT-KEY>` is a root run in
    `split_mode: full`, which skips that gate entirely and reads nothing this run wrote, so it
    carries **no** clause.
  - **`/dev-workflows:design` is offered on this route by none of the six arrays.** It takes over a merged
    `specification.md` — a file this run did not write — and resolves its own key through the specs tree. The path to it runs through the first option: `/product-workflows:specify <SLICE-KEY>` writes
    that specification, and its own next-step offer is where `/dev-workflows:design`
    is named under the conditions that make it resolvable.
  - **There is no Epic fan-out on this route.** The address resolved a `PRD-` slice folder, not an
    `EPIC-` one, so there is no sibling Epic to repeat this ARD for — and no second positional key to
    name one with (Phase 0 step 1, `CREATE_ARD_ONE_ADDRESS`). A sibling
    *slice* is a separate BRD with its own folder and its own seed: `/product-workflows:create-ard
    <SIBLING-SLICE-KEY>` waits on nothing this run produced and would carry no clause.

**Every merge clause above is the `<merge-clause>` placeholder**, resolved from this run's own `Phase handoff:` outcome line per `Skill(skill: "workflows-core:reference", args: "next-phase-offer")`, and never the unconditional "once the pull request above is merged": a declined handoff, a failed push and a nothing-to-commit run — among the other outcomes §4.1 lists — each leave a different wait, and none of those three opens a pull request to wait on. It is a placeholder, not an instruction to reword an option, so the arrays are still presented verbatim per `workflows-core:escalation-rules`. **The wait it names is real for every option that carries it**, and it is a stop, not a silent degradation: `/product-workflows:epics`, `/product-workflows:specify` and `/dev-workflows:design` each read this ARD through `workflows-core:ard-resolution` and each stops on `status: unmerged`, naming the branch and any open pull request, and `/product-workflows:brd-split` on this slice stops on its own `require-on-main` against `grounding/code-grounding.md`. `/product-workflows:create-prd <SLICE-KEY>` stops on its own `require-on-main` against the slice's `decisions.md`. **The option carrying none names no gate this run feeds** — `/product-workflows:brd-split <PARENT-KEY>`, in either form — which is why the rule is stated against the gate an offer names rather than against which array it sits in. Only a handoff that reached no branch at all resolves `status: none`, where that reference's no-regression rule has the run proceed exactly as it would with no ARD.

**The commercial step this run just unlocked, named in prose — and it depends on the route.** On the
BRD route, where verified grounding and a settled register already exist, this ARD is what takes the
folder to tier 3, where architecture-bearing work packages become eligible for High confidence
(`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §5): **`/product-workflows:prd-proposal <PRD>`
now prices this folder against a settled architecture rather than an assumed one, and re-running it
after this ARD narrows the range.** On the idea route the folder stays at §5's tier-1 ceiling
regardless of this ARD: it may be ground — `/product-workflows:prd-ground` runs on an idea-route
folder too — but tier 2 also needs a settled register, and nothing on the idea route produces one.
`/product-workflows:prd-proposal <PRD>` is still worth naming, but on this route it stays
indicative. Either way it
is optional and ungated — nothing on the build ladder waits on a proposal, and no arrays above change. (`/product-workflows:brd-proposal` does wait on a slice's, but that is the proposal phase gating its own earlier run rather than anything this offer names.) No merge wait: that
command gates on `prd.md`, which this run does not write.

Guidance only — never auto-invokes another command. Per `workflows-core:next-phase-offer`.

### Context hygiene

The resume pointer is written in the terminal cost phase (Phase 8), per
`workflows-core:session-hygiene` §1. The next step hands off from PA
to PE/Dev, so:

- **Handing to PE (`/product-workflows:epics <PRD>` / `/product-workflows:specify <EPIC>`) or Dev (`/dev-workflows:design <EPIC>`), even yourself?** → run **`/clear`** for a clean slate; the ARD is on disk.
- **On the BRD route, the handoff is `/product-workflows:specify <SLICE-KEY>`** (Phase 7) — same answer, **`/clear`**; the ARD is on disk and that run reads it from the specs repo, not from this session.
- Continuing to draft more ARD areas yourself right now? → **`/compact`** is fine.
- Consider **`/rename <PRD-ID>-<slug>-pa`** so you can find this session later.

Guidance only — see `workflows-core:session-hygiene`.

---

## Phase 8 — Session maintenance, feedback & cost
Terminal phase — runs after Phase 7, NEVER interrupts an earlier phase.

**Capture-at-block invariant.** If an EARLIER phase **halts on a plugin / skill / command / reference gap**, `emit-block` (per `workflows-core:feedback-emission`) at that halt **before** escalating. NEVER `emit-block` for an environment / user halt (unset `$SPECS_PATH`, missing key, no-ARD-needed, unmounted-repo descope, cancellation) or a review BLOCK. **The six argument-, tree- and git-shaped stops are of that second class**: `CREATE_ARD_NEEDS_KEY`, `CREATE_ARD_ONE_ADDRESS`, `CREATE_ARD_NOT_FOUND`, `CREATE_ARD_BRD_NOT_SLICED`, `CREATE_ARD_REGISTER_NOT_ON_MAIN` and `CREATE_ARD_REGISTER_NOT_HANDED_OFF` report the operator's own argument list, BRD tree or where its register sits in git, not a capability this plugin lacks, so none of them `emit-block`s. The one exception is a halt on a tool the ai-containers image lacks, which `workflows-core:feedback-emission` §6 `emit-block` defines.

**Session-hygiene invariant.** End Phase 7 with a `### Context hygiene` block per
`workflows-core:session-hygiene` — prepare-first (the
`resume.md` write runs later, in the terminal cost phase, per
`workflows-core:session-hygiene` §1 — this block prints the
guidance only), then a
PA→PE/Dev handoff suggestion (`/clear`) + `/rename <PRD-ID>-<slug>-pa`. Guidance only, never auto-run.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.1 Sonnet chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 2's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

**The run's key on the BRD route.** Phase 0 resolved a BRD key, which is a folder name and never a
second identity (`workflows-core:addressing` §1). Any tracker identity for this work,
if one exists at all, is the `key` in the PRD this BRD folder holds — the same one Phase 7's
`/product-workflows:epics` condition reads. So the `key` passed to `emit-auto` and `emit-cost` below
is that minted key when the folder holds a PRD carrying one, and `null` otherwise (`source: none`
either way); `commit-artifacts` resolves its own key the same way and commits under `NOISSUE` when
there is none, per `workflows-core:specs-repo-git` §4 step 4. The `<BRD-KEY>` is
never passed as a `key` — a folder key in a tracker-key field is the confusion the two fields
exist to keep apart.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<detection_model — §2.1 Sonnet chain>`) with a compact handoff: command `/create-ard`; what was authored (ARD scope + grounded repos); key events (grounding gaps/descopes, BLOCK reviews — or 'none'); workarounds; the `ard-reviewer` verdict; test result N/A; project root = the feature folder.
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6) with the report, `command: /create-ard`, the run's `key`, `source`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). Surface the persisted path (or "no plugin-facing signal — nothing persisted").
3. **Session cost (ALWAYS runs).** **Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way. Otherwise, invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call its `emit-cost` entry point with `command: /create-ard`, `phase: architecture`, `role: pa`, the run's `key`, `source`, and `plugin_version`. Surface the persisted path (or the report-only notice).
4. **Write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite `<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above, so the pointer reflects the completed run, and before the commit step below, so it is included in it. Redact per §1. Silent; the printed `### Context hygiene` guidance already appeared in the report.
5. **Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session artifacts (/create-ard)` with no `Co-Authored-By` trailer, and pushes to the branch this run's handoff phase created (§4.1). It NEVER touches anything outside `$SPECS_PATH`; NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Hold its §6 outcome line for the Final report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (git for the deliverable is offered only in Phase 6; the terminal step above commits only the bounded session-artifact paths in `$SPECS_PATH`), and NEVER writes into a code/docs repo or the current working directory, where it is not the specs repository; no user name is ever written.

---

## Final report
Report: the ARD path(s) + scope (PRD/Epic, any per-area split); **the PRD gate's return value and whether an authored `prd.md` was read from the resolved folder** — the same two lines on every route, so a reader can tell an `absent` PRD from an unrun gate; the grounded repos + any descoped/ungrounded ones; `AD#N` count, live, superseded and withdrawn; open-question count; the `ard-reviewer` verdict; the `Phase handoff:` outcome line from `handoff-to-main` (`workflows-core:phase-handoff` §4.1); resolved model routing (+ any Opus gate/degradation, or `Model routing: bypassed — enforced <id> (flag|env)` in its place wherever `run_flags.enforced_model` is set, per `workflows-core:model-routing/classification` §10 — no gate or degradation applies); the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); the feedback path (or, under `--skip-feedback`, the `Session feedback: …` line) + cost path (or, under `--skip-costs`, the `Session cost: …` line); the `Specs repo:` outcome line from `commit-artifacts` (`workflows-core:specs-repo-git` §6), with any guard notice repeated in full; and the adaptive next-step recommendation.

**Wherever `prd_dir` holds `grounding/`, on either route, additionally:** the folder read — `prd_dir`,
which on an Epic-level run is the PRD folder above the Epic, not the folder the address resolved — which of
`grounding/code-grounding.md` and `grounding/design-grounding.md` were present there, and which of
those Phase 2 found uncommitted; every `[CG#n]`/`[DG#n]`
dropped for want of a verifier outcome, by id; every architecture-altitude item still `consumed_by:
none`, by id, per the design's *Consumption tracking* section (§7.3) — **excluding the baseline
`[CG#n]` findings**, which are never `consumed_by` anything and whose `none` therefore reports no gap
(`workflows-core:grounding-format` §4.1); say that they are excluded, so a reader can tell an empty
list from an unrun check. **Where `prd_dir` carries `brd-link.md`, additionally exclude every
`[CG#n]`/`[DG#n]` whose `claim` cites a `[BR#n]` that folder's own `coverage-ledger.md` now shows as
`covered-by`**, read off that file's `disposition` column and never off `claims:` or the inventory
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.1's trap, named there from the other
side) — the BRD that row names *owns* the requirement (§3.1), so nothing this run authors can consume a
finding about it and its `none` reports no gap either; that is the state a re-cut leaves on the slice
that gave the row up (§3.2) — say how many were excluded on this count too, for the same reason as the
first, and note that this is a **report exclusion only**, no finding edited, renumbered, moved or
marked and no `consumed_by` value changed anywhere. On a folder with no `brd-link.md` — the ordinary
idea-route case — this second exclusion has no subject: its claims are `[AC#n]`/`[FR#n]`/`[US#n]`,
never a `[BR#n]`, and there is no `coverage-ledger.md` in the folder to read, so report zero excluded
under it rather than omitting the count.

**On the BRD route, additionally:** the `<SLICE-KEY>` seeded from and its resolved folder; the
`parent:` key its `brd-link.md` records — every run of this route is slice-level — and whether the
parent's ARD was inherited (`found`) or absent (`none`); which of `ard-seed.md` and `decisions.md`
were present; the frontmatter
`scope` / `prd` / `epic` / `inherits` / `derived_from` as written, naming which of the two
`derived_from` sources was used and why; every `[VD#n]`/`[CD#n]`/`[AS#n]` carried in as a gap rather
than an input, by id and status; every architecture-altitude `decided` record that did **not** become
an `[AD#N]` and where its content went instead; every `will-change` finding and `conditional_on`
decision recorded as a prerequisite rather than as settled architecture, with the prerequisite decision
named; `ard-seed.md`'s consumption at file granularity; and any product- or
implementation-altitude content the grill surfaced and left for the command that authors at that
altitude instead of the ARD (D5) — naming the command, never a seed file, since the register it will
read that content out of is the one this run already read. Say plainly whether `/product-workflows:epics` was offered and, when it was not, **why**: the resolved
folder holds no authored `prd.md`, and name what Phase 7's precondition table put in its place —
`/product-workflows:create-prd <SLICE-KEY>`, a `/product-workflows:brd-split` against this slice or its
parent, or nothing at all where this slice's gate set holds no `covered-here` row, none
`unallocated`, and is not empty, or where its `coverage-ledger.md` is missing or unreadable. Where the answer is
*nothing*, say that too, and say why: `/create-prd` would raise `CREATE_PRD_BRD_NOT_ELIGIBLE` and
that branch names no command either — or, for a missing ledger, that there is no gate set to judge,
naming the file by path. Name the folder tested, the
`key` it asserts, and the two gate-set figures the table was resolved on (for a missing ledger, the
`claims:` count and the missing path). That is the case a reader
is most likely to mistake for reachable.

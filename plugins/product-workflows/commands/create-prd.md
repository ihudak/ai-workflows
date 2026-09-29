---
name: create-prd
description: PRD-creation workflow (PM phase, sub-project 2 of the PRD-creation flow). Turns a refined idea.md + a user-supplied address into a high-quality Product Requirements Document document (spine + adapt-in profiles --lean|--hybrid|--full), authored via a relentless grill against workflows-core:prd-format, gated by the Opus prd-reviewer, written as prd.md into $SPECS_PATH/specifications/PRD-<KEY>-<slug>/. Product-level (no code scan). the BRD route seeds the run from a decided BRD slice instead of an idea: it reads that BRD folder's product-altitude prd-seed.md and decisions.md, defaults the profile to --full, refuses a BRD- container outright, before any ledger row is read, because a BRD is never the folder a PRD is authored in, and on the PRD- slice folder a split produces refuses one whose coverage-ledger rows are not all allocated and one whose ledger holds no covered-here row (the rows read are that slice's own ledger rows, narrowed by its brd-link.md claims:), gates decisions.md on the specs default branch before reading it (an unmerged register stops the run), freezes every [VD#n]/[CD#n] against the grill, and writes brd_key, brd_parent (always present on this route, since the route now resolves a slice) and depends_on into the PRD frontmatter. Offers /release-notes and /create-ard as next steps.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Author a Product Requirements Document: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/create-prd` is **sub-project 2 of the PRD-creation flow** (PM phase) — it consumes the `idea.md` from
`/idea` and a **user-supplied address** and
authors a high-quality **Product Requirements Document** that feeds the downstream pipeline. The PRD is **product-level**
(a PRD): what / why / for-whom, not how. Zero external calls — the PRD is authored as markdown in the specs
repo, which is where every downstream command reads it from.

Usage: `/create-prd <ADDRESS> [@idea.md] [--from-prd <PRD-KEY|path>] [--lean|--hybrid|--full] [--no-docs] [--docs <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]` (default `--hybrid`, or `--full` on the BRD route — Phase 0 step 2; the one `--no-*` switch turns off the one grounding source — see Phase 1). `--docs <path>` — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`; **strip the flag and its value together** before any remaining-argument classification, or the path is read as part of the address. Declared for every consumer by `workflows-core:docs-grounding` *Procedure* step 1 (*Flags first*), which resolves it; this command only has to recognise it and pass the invocation through.

---

## Phase 0 — Resolve inputs

0. **Flags.** **Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. Strip every recognised flag from `$ARGUMENTS` before step 1 classifies the address or
   any `@idea.md`: `--from-prd <PRD-KEY|path>` and `--docs <path>` **each together with the token
   after it**, plus the booleans `--no-docs` and `--lean` / `--hybrid` / `--full`. Steps 2 and 2a
   then read the values this step set aside.

   **Every value-taking flag, not only the docs pair.** `--from-prd` takes a `<PRD-KEY|path>`, and
   an unstripped one puts two stray tokens in front of step 1 — the flag, which is read as the
   address, and its value, which is read as `@idea.md`. That is the same defect as the docs flags
   and it was missed once by scoping the sweep to "a flag with no parsing site" rather than to
   "a value not consumed before positionals are read": step 2a *does* discuss `--from-prd`, so a
   parsing-site test passes it, and step 2a runs after step 1. It is step **0** and not `1a`: step 1 is what parses the address, so a rung numbered
   after it runs after the damage.
   Both are carried to Phase 1's `resolve-docs-grounding` call and change nothing else. Without
   this rung the flag is a token like any other and lands in that classification: `--docs` is read as
   the address, or its path is read as the `@idea.md` argument. They were named in the Usage line and
   parsed nowhere, the same defect `/create-ard`, `/specify` and `/release-notes` were found to have.
1. **The address (mandatory).** Parse the first token that is neither a flag nor a flag's value — `--from-prd` and `--docs` each consume the token after them (step 0), and a value skipped as "non-flag" would be read as the key and validate it with `key-valid` (`workflows-core:addressing` §1). If absent or malformed, **stop gracefully** with the one `CREATE_PRD_NEEDS_KEY` text below — there is one stop for this code, not two. (Shape only, and never checked against anything: the key is the operator's own and names a folder in `$SPECS_PATH`; nothing mints it and nothing verifies it.)

   **The BRD route is detected, not declared.** A folder carrying `brd-link.md` was produced by
   `/brd-split` and holds the seeds this command reads; the operator restates nothing on the command
   line, and there is no flag that could disagree with the folder it names. **Detection therefore
   waits on resolution.** The address is resolved once, with `resolve-address` (step 5), and that
   resolution is taken as soon as step 2b has settled `$SPECS_PATH` — ahead of step 2's profile
   default and step 3's ladder, both of which read the route. Print which route the run entered at
   that point, before any other work. Where the address resolves to nothing there is no folder and
   no `brd-link.md` to read one off, so the run is on the **idea route**; step 5 says what happens
   then, and it is not a stop. A key that fails §1's grammar stops with
   `CREATE_PRD_NEEDS_KEY: /create-prd needs an address (^[A-Z][A-Z0-9_]*(-\d+)+$, e.g. EPIC-008 or the slice EPIC-008-01) — re-run '/product-workflows:create-prd <ADDRESS>'.`

2. **Profile.** `--lean | --hybrid | --full`; default `--hybrid` — **or `--full` when the BRD route is present** and no profile flag was given, per the design's *Profile default* section (§7.4): that profile is the one carrying `## Functional requirements` (`[FR#N]`), `## API specification`, `## UX prototype / UI mockups` and the full `## Assumptions & open questions` Contradictions Log, so considerably more BRD-derived content has a legitimate **product-altitude** home than `--hybrid` allows. An explicit `--lean`/`--hybrid` still wins: the default is a default, not an override.
2a. **`--from-prd <PRD-KEY|path>` (optional seed).** When present, this run authors a **new** PRD (the
    positional `<KEY>`) seeded read-only by another PRD. Resolve the seed via
    `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3) and read that folder's
    `prd.md` for a key, or read the given path directly. The seed is **grounding, not content**
    (Phase 3 adapts it; it is never copied wholesale).

2b. **`$SPECS_PATH`, then the specs-repo preflight — both before step 3's gate.** If `$SPECS_PATH` is
    unset, stop naming it (`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`). Then invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point
    (§3) inline: flush any leftover session artifacts from an earlier run, retry an artifact commit
    that failed to push, and settle the branch. Prompt-free and silent when the specs repo is clean and
    on its default branch. If a guard fires, emit its §5 notice; if it returns `specs_git: blocked`
    (§3.3 G0), carry that flag for the whole run — the terminal `commit-artifacts` step skips on it.

    **The ordering is the point, not the tidiness.** Step 3's `require-on-main` performs no fetch of
    its own (`workflows-core:phase-handoff` §3), so without the preflight's
    best-effort fetch ahead of it a merged `idea.md` reads as "on a branch and never handed off" and
    the run hard-stops on work that is already on the default branch. This command was for a time the
    only `commit-artifacts` caller running no preflight — deleted as
    collateral with an adjacent paragraph — which also left `specs_git: blocked` unset, so the G0
    guard in both `commit-artifacts` and `handoff-to-main` was inert here and a detached-HEAD specs
    repo would take this command's commits to an unreachable place and report success.

3. **Resolve `idea.md` (ladder — stop at first hit). Skipped entirely on the BRD route**, where
   `prd-seed.md` is the seed and there is no `idea.md` to find: rung 1 would return `absent` on a
   BRD folder that never held one, and rung 3 would then offer an idea from some other
   initiative — a same-session `/idea` output is exactly the offer that names something
   this run has no business reading. An explicit `@<path>` supplied alongside the BRD route is still
   honoured, on rung 2's terms only (read where it sits, never relocated, never gated, reported once
   as out-of-contract) and as **additional grounding**, never as the seed. Without the BRD route the
   ladder runs exactly as it always has:
   1. **in-contract** — `idea.md` in the folder `<KEY>` resolves to (`PRD-<KEY>-<slug>/` on a current tree; §5's unprefixed form on a legacy one). Execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against it, mapping its §3.7 return value by `stopped` first, never by `on_main` alone. Any stopping state → stop per §4.4. Otherwise (`stopped: false`): on `pass`/`pass_amending`, use it — **do not relocate**, and nothing did: `/idea` wrote `idea.md` into this folder on its first write and never moves it afterwards (D7, `commands/idea.md` Phase 0 step 1), so it is already where it belongs; on `absent`, fall through to rung 2 — **and report the file first where it is in fact there.** Row F means *on no ref*, not *not on disk*: an `idea.md` that `/idea` wrote and never handed off — which is every `status: draft` run, by that command's own design — sits in the folder this step has just resolved, and would otherwise be passed over in silence all the way to rung 5's grill-from-scratch, in the folder it resolved. Where the in-contract path exists in the worktree, say so once — *"`<path>` exists but is on no ref, so it is not read in-contract. Re-run `/product-workflows:create-prd <KEY> @<path>` to read it in place (rung 2), or hand it off first."* — and then fall through exactly as before. **The fall-through itself does not change**: `workflows-core:phase-handoff` §3.4 gives row F to this caller's pre-existing behaviour, `/idea` is not a prerequisite, and reporting a file is not gating on one. Likewise on `unmanaged`: this ladder runs before step 4 validates `$SPECS_PATH`, so `unmanaged` (the §3.1 gate could not run) is reachable here, and it behaves as `absent` because there is nothing to verify; step 4 still stops immediately afterward on an unset `$SPECS_PATH`, so nothing is lost by not stopping here;
   2. **out-of-contract `@path`** — explicit `@path` argument; read the idea where it sits, **never move it**, and do not gate it. Report once: *"out-of-contract: reading `<path>` in place; it will not be relocated or gated."*;
   3. **same-session** — if `/idea` ran earlier in this session, use its recorded output path (confirm with the user) — out-of-contract, as rung 2;
   4. *(retired — the discover rung searched a personal store for a stray `idea.md`. `/idea` writes into the resolved folder now, so rung 1 finds it.)* — out-of-contract, as rung 2;
   5. prompt for a path, or — last resort — proceed with **no idea** and grill the PRD from scratch. **`/idea` is not a prerequisite for `/create-prd`** — an `absent` in-contract idea must reach this rung, never a stop.
4. **`$SPECS_PATH` (required).** Already established in step 2b, which had to run before step 3's gate; nothing re-checks it here.
5. **Feature folder. On the BRD route this is the resolved `PRD-` slice folder** — the one
   `/brd-split` carved, which is what step 5a's container refusal leaves standing — and it is never
   created here. There is no second resolution for that route and no `<BRD-dir>` argument to read:
   the single positional address was resolved once with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). The
   PRD this run authors is written **into that folder** as `prd.md`, beside the BRD
   artifacts it was derived from.

   **`absent` is not a state this route can be in, and there is no stop here for it.** The BRD
   route is *detected*, not declared (step 1) — from a `brd-link.md` **inside the folder the
   address resolved to** — so a run that resolved no folder read no `brd-link.md` and is on the
   idea route by construction, which is the disposition the next paragraph gives it. `/specify`
   states the same thing from the other side, taking **one stop for both routes** *"since a folder
   that resolved to nothing carries no `brd-link.md` to say which route it would have been on"*
   (`commands/specify.md` Phase 0 step 3); it reaches a stop rather than a creation only because
   that command creates no folder at all, and this one does. A `BRD-` key whose folder **does**
   resolve is step 5a's container refusal, immediately below — so nothing is left uncovered.

   **A `CREATE_PRD_BRD_NOT_FOUND` stop stood here and is retired**, for the reason
   `CREATE_ARD_BRD_NOT_FOUND` was retired before it: it offered `/product-workflows:brd-split` on a
   parent BRD as the remedy for an address that resolved to nothing, a state no run reaches, and it
   contradicted the behaviour other stops name this command *for*. `/create-ard`'s
   `CREATE_ARD_NOT_FOUND`, `/specify`'s `SPECIFY_BRD_NOT_FOUND`, `/update-prd`'s `absent` branch,
   `/epics`' `EPICS_NOT_FOUND` and `EPICS_EPIC_NOT_UNDER_PRD` and `/prd-ground`'s
   `PRD_GROUND_NOT_FOUND` among them each name `/product-workflows:create-prd` as the run that
   **creates** a `PRD-` folder where none exists; were the stop the live reading, every one of them
   would be naming a command that refuses them.
   Without the BRD route, unchanged in substance: resolve the folder with `resolve-address <KEY>` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), which searches every level §3 bounds and carries §5's legacy fallback; no matching rule is written here, because a second copy of §5's is the drift §1 warns about. This is the resolution every mention of the feature folder in this command means, step 3's rung-1 `idea.md` included. On `status: absent` the folder is auto-created by this run's first write to `prd.md` (Phase 3's live authoring, ordinarily) as `PRD-<KEY>-<slug>/` per §2's convention, `<slug>` from the idea title (else a kebab of the PRD summary) — resolution honors a folder that already exists wherever it sits, and never proposes one.
5a. **The container refusal — a `BRD-` folder is never a `/create-prd` target, on either route.**
   Take this the moment step 5 returns `status: found` — which step 1 takes as soon as step 2b has
   settled `$SPECS_PATH`, ahead of step 3's ladder — **before `coverage-ledger.md` is opened at
   all** and before step 6 reads a prior PRD. **It is not part of the BRD gate below and must not be
   folded into it**: the BRD route is detected from a `brd-link.md`, and a root BRD folder need not
   carry one — `/brd-intake` writes none, and no command writes one into a root: `/brd-split`
   places one in each slice it carves, and every command that merges `depends-on:` into one refuses
   a root. A container refusal that ran only on the detected BRD route would therefore let
   `/create-prd <ROOT-BRD-KEY>` fall through to the **idea** route, find no `idea.md`, grill a PRD
   from scratch and write it into the container — the exact state this refusal exists to prevent.
   A BRD is a container and is never the folder a PRD is authored in (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5;
   `workflows-core:addressing` §2 invariant 2). The folder a PRD is authored in
   is a `PRD-` folder — the slice `/brd-split` carved, carrying `brd-link.md`, or the one `/idea`
   wrote into, or its legacy unprefixed form — and that is the only shape this command accepts, on
   either route: this step refuses a container, and step 5b refuses the one other level a resolved
   address can reach, an Epic folder. This is a refusal
   on **kind**, not a sixth disposition and not a rule about rows: no row of a container's ledger can
   change it. `status: absent` reaches nothing here — there is no folder to test, and step 5 already
   says the first write creates a `PRD-` one.

   **The test is the directory prefix, and never the folder's asserted `kind:`.** `/brd-split` writes
   `kind: brd` into the `brd-link.md` it places inside a `PRD-` slice folder (`commands/brd-split.md`
   Phase 3), so a slice **asserts `brd` while being exactly the folder a PRD belongs in** — a gate on
   the asserted kind would refuse every slice and accept nothing. Nor can this command gate on
   `prd.md`'s own `kind: prd`, the way a reader of an authored PRD does: this run is greenfield and
   `prd.md` is the file it is about to write. So the test is the `BRD-` prefix
   `workflows-core:addressing` §2 fixes, read off the resolved folder's own name — a prefix as that
   file's §4.1 defines one, the name beginning `<KIND>-<the resolved key>-`, so a legacy idea-route
   folder keyed `BRD-12`, named `BRD-12-checkout/`, carries no prefix and is not refused by its
   name. A `PRD-` prefix passes; a `BRD-` prefix refuses.

   **Where the folder resolved through that file's §5 legacy fallback and carries no prefix at all,
   the question is answered by positive evidence that it is a BRD, never by the absence of a file**
   — `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.1, which is the authority and
   is not restated here. In short: a legacy folder carrying `coverage-ledger.md` or
   `brd/brd-inventory.md`, and no `brd-link.md` naming a `parent:`, is a root container; a legacy
   folder carrying **neither** of those two files is a legacy **idea-route PRD folder** and this
   refusal does not fire on it.

   **This is the branch a test written as an absence gets wrong, and it is reachable by design.** A
   legacy idea-route PRD folder — `specifications/<KEY>-<slug>/` holding `prd.md`, authored before
   the kind prefixes shipped — carries no `brd-link.md` either, misses §3's `*-<KEY>-*` prefixed
   glob by construction, and lands in §5's fallback every time. Refusing it as a container would
   offer `/product-workflows:brd-split` on a folder with no coverage ledger to walk: a stop naming a
   remedy that cannot run. The two files §5.1 tests for are created by `/brd-intake` and
   `/brd-split` alone and written by nothing on the idea route, which is what makes the test positive.

   Stop gracefully:
   ```
   CREATE_PRD_BRD_NOT_SLICED: <BRD-KEY> resolves to a BRD- container at <path>, and a BRD is never the folder a PRD is authored in (coverage-ledger-format.md §5) — its requirements are built by the PRD- slices under it, one PRD each. <the remedy, per the branch below>
   ```

   **The remedy branches on what the folder holds, and that branch is a directory listing rather
   than a ledger read** — the refusal is already taken by the time it is chosen, and re-deciding it
   on rows would put back the data gate this replaces. Enumerate slices by `/brd-split` Phase 0
   step 9's **positive test**: an immediate subdirectory carrying a `brd-link.md` whose `parent:`
   names this BRD. A name match is not the test, for the reason that step gives.

   | What this BRD folder holds | What the stop says |
   |---|---|
   | **One or more slices** — the ordinary shape, since a split always confirms at least one | Name every slice, and offer `/product-workflows:create-prd <SLICE-KEY>` once per slice. That run resolves a `PRD-` folder, passes this refusal, and applies refusals 1 and 2 to the slice's **own** ledger — the offer is that a PRD belongs there, not a promise that the slice is already eligible. Do **not** name `/product-workflows:brd-split <BRD-KEY>` here: the slices it would carve exist, and on a parent whose ledger is fully allocated that run carves nothing (`commands/brd-split.md` Phase 0 step 10) |
   | **No slice at all** | `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` is the run that carves one — it walks every row still `unallocated` and always confirms at least one slice (its Phase 2), so it produces the folder the PRD is then authored in — after which `/product-workflows:create-prd <SLICE-KEY>`. **Two conditions travel with that offer** rather than being left for the operator to discover. First, the slicing instruction is not optional there — a root is never ground, so that run has no findings to cluster candidate slices from and stops with `BRD_SPLIT_NEEDS_INSTRUCTION` where it has rows to place and was given none. Second, **where this BRD's ledger leaves no row `unallocated` that run is a no-op** (Phase 0 step 10) and carves nothing, because the walk already settled every row and no command but the `/brd-intake` re-run below moves a terminal row back to `unallocated` (§3) — so say what the operator does *then*, or the offer is a dead end. There are two ways to reach it, and **both are leaveable** — one by a decision, one by a repair; neither is a state with no exit. Either the one slice the walk confirmed was later removed as a standing empty child (`commands/brd-split.md` Phase 4.5), in which case every requirement is `deferred-to`, `rejected` or `superseded-by`, every row is legal and terminal, and no PRD is owed by anybody: that is an **ending rather than a failure**, and no command decides otherwise, because un-deferring a requirement is a decision taken with the customer. Name no command for the decision — and say, rather than implying the state is sealed, that once it is taken it is carried out by the same two repairs the other way below names, in the same order: hand-edit the one row that is now to be built back to `unallocated`, after which `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` has a row to walk and carves the slice; or re-run `/product-workflows:brd-intake <BRD-KEY> @<brd-file>`, which, wherever its read finds a requirement, reopens **every** row and discards every deferral and rejection recorded here (its Phase 0 step 7). Or the ledger records a fate a container can no longer hold, a **root** row `covered-here`, which no parent's walk has offered since a BRD became a container and which only a tree written before that change, or a hand edit, can have produced (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5). **The narrower repair is offered first, because the illegal state is one row wide and every other row is already legal and terminal:** hand-edit that one row's `disposition:` in `coverage-ledger.md`, leaving every other row untouched — to `deferred-to: <this BRD>`, `rejected: [DEF#n]` or `superseded-by: [BR#n]` where the requirement is not to be built here, which makes the ledger legal and lands on the ending above; or back to `unallocated` where it is, after which `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` has a row to walk, confirms a slice (its Phase 2), and that slice's own walk takes the row to `covered-here`, the one level at which `covered-here` is legal. §3's *no command moves a row back to `unallocated`, save one* binds the commands; this is a hand repair of a value no command wrote, and §5 already names hand editing as how this state arises. **Second, and only where the whole inventory is to be re-taken:** re-running `/product-workflows:brd-intake <BRD-KEY> @<brd-file>` over this same folder is a re-run rather than a refusal (its Phase 0 step 7, which now warns and confirms before the first write) and, wherever its read finds a requirement, rewrites the ledger with **every** row `unallocated` (its Phase 5; that step 7 lists what a re-run keeps and what it changes), after which `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` has rows to walk and carves the slice. That re-run re-extracts the inventory and, wherever its read finds a requirement, **discards every disposition this ledger records**: each `deferred-to`, `rejected` and `superseded-by` the walk decided is replaced by `unallocated` and must be re-taken, and a `rejected` row must be re-cited against its `[DEF#n]`. Naming which decisions die is the disclosure — "the dispositions are replaced" is not — and it is why this option is second rather than only |

5b. **The Epic-folder refusal — an `EPIC-` folder is never a `/create-prd` target either, on either
   route.** Take it at the same moment as step 5a — the moment step 5 returns `status: found`, before
   step 3's ladder, before step 6 reads a prior PRD, and before anything is written. Step 5's
   `resolve-address` searches **every** level `workflows-core:addressing` §3 bounds, the Epic level
   included, so an Epic's key resolves here exactly as a PRD's does; and an `EPIC-` folder carries no
   `brd-link.md`, so the run would enter the idea route, find no `idea.md`, grill a PRD from scratch
   and write `prd.md` into the Epic folder — a PRD nested below the PRD it was split from, which
   `workflows-core:addressing` §4.1 places at no level a PRD lives at. **The test is the directory
   prefix again**, a prefix as that file's §4.1 defines one — the name beginning
   `EPIC-<the resolved key>-` — so a legacy folder keyed `EPIC-008-01` and named
   `EPIC-008-01-orders/` is not refused by its name. **Where the folder carries no prefix**, place it
   by §4.1's positive evidence, taken after step 5a's container test as §4.1 orders it: a resolved
   `kind: epic` is an Epic folder and refuses, and nothing else on an unprefixed folder does — a
   resolved `kind: prd`, or a `brd-link.md` naming a `parent:`, is PRD-level and passes. A `PRD-`
   prefix passes; an `EPIC-` prefix refuses. Stop gracefully:
   ```
   CREATE_PRD_EPIC_FOLDER: <KEY> resolves to an Epic folder at <path>, and an Epic is never the folder a PRD is authored in — a PRD is authored in a PRD- folder, and this Epic's PRD is the one in the folder above it. <remedy> For a separate PRD, give it a key of its own: '/product-workflows:create-prd <NEW-KEY>'.
   ```
   `<remedy>` names the parent PRD as the likely intended target wherever there is one. Where the
   folder above holds a `prd.md` asserting `kind: prd` — the ordinary shape, since `/epics` writes
   every `EPIC-` folder under a PRD it has read — it is `This is probably the PRD you meant: revise
   it with '/product-workflows:update-prd <PRD-KEY>', or re-refine this Epic with
   '/product-workflows:epics <KEY>'.`, `<PRD-KEY>` being that `prd.md`'s own `key`
   (`workflows-core:addressing` §4) — never parsed out of either folder's name. Where this folder
   holds no `epic.md`, `/product-workflows:epics <KEY>` refuses it (`EPICS_NO_PRD`), so that clause
   names `'/product-workflows:epics <PRD-KEY>'` instead, which drafts the PRD's Epics in folders of
   its own. Where the folder above holds no such `prd.md`, this Epic has no PRD above it to revise,
   which is the shape `/product-workflows:epics <KEY>` reports as `EPICS_EPIC_NOT_UNDER_PRD` where
   this folder holds an `epic.md` and as `EPICS_NO_PRD` where it holds none, and the remedy is the
   one both stops give: where the folder above is a `PRD-` folder, it is `The PRD folder above it
   holds no PRD yet: author one there with '/product-workflows:create-prd <PARENT-KEY>'.`,
   `<PARENT-KEY>` being that folder's own `key` (where that folder holds a `prd.md` asserting no
   `kind: prd`, say that instead of "holds no PRD yet", and name
   `/product-workflows:update-prd <PARENT-KEY>` to refresh it: step 6 counts the file as found on
   a `/create-prd <PARENT-KEY>` run, which offers the same refresh or an archived overwrite) — a run this step does not refuse, since it resolves
   the `PRD-` folder and not this one, subject to step 7's data refusals applied to *that* folder
   where it carries a `brd-link.md` (name instead what the matching row of
   `/product-workflows:update-prd` Phase 0 step 4's table names); anywhere else, name no parent and
   say so. It is a user halt,
   so `emit-block` does not fire. `/product-workflows:idea`'s `IDEA_NOT_AN_IDEA_FOLDER` refuses the
   same folder for the same reason.

6. **Prior PRD (frontmatter-based).** Read `<feature-folder>/prd.md` — the only canonical PRD name this plugin writes (the archived copies under `revisions/`, `/update-prd`'s and this command's own pre-write archive (Phase 3) alike, are never read as a PRD) and the only one it reads. `workflows-core:addressing` §5 resolves the *folder* either way and fixes the boundary there: a tree written before the artifact filenames lost their keys renames its artifacts rather than being resolved for, so a `<KEY>_<slug>.md` sitting beside no `prd.md` reads here as no PRD at all. **The test for "found" is presence: any file at `<feature-folder>/prd.md` counts as found, whatever its frontmatter** — one asserting `kind: prd`, one asserting no `kind:` at all, and one asserting some other kind alike. **`kind:` does not decide presence here**, which matches `/product-workflows:update-prd`, whose base is that same file "authoritative without a test". The three commands `workflows-core:addressing` §5 names as gating on `prd.md`'s own `kind: prd` gate that way because they **consume** a PRD's content; this command gates on presence because it must not **overwrite** one. A `prd.md` that exists but cannot be read, or whose frontmatter does not parse, is found too — presence is a file test, never a read. Phase 1 step 2 stops on one that cannot be read at all (`CREATE_PRD_PRIOR_UNREADABLE`), and names a frontmatter that does not parse above its choice. If a PRD is found, this is an **existing PRD** — `/create-prd` is greenfield-only, so **redirect** (see Phase 1) to `/update-prd <KEY>` unless `--from-prd` **or the BRD route** is present.
7. **The BRD gate (the BRD route only).** Its structural test already ran: step 5a refused a
   `BRD-` container on every route, so anything reaching this step is a `PRD-` folder.

   **Refusals 1 and 2 are slice-only, and that is what step 5a's container refusal bought.** Both are
   `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5's rule, applied — that file is the
   authority for each and neither is restated here — and both now run against exactly one shape: a
   `PRD-` folder whose `brd-link.md` carries a `parent:` — step 5a guarantees it. Read that file for its `parent:` and any
   `depends-on:`; then read `<slice-dir>/coverage-ledger.md` and take the **`disposition` written on
   each row of the gate set defined immediately below**.

   **The gate set is this slice's own ledger rows, narrowed by its `brd-link.md` `claims:`.** §5
   states eligibility over *its ledger rows*, and on a slice the narrowing does real work rather
   than coinciding with the ledger: the set is the rows its `coverage-ledger.md` holds for the
   `[BR#n]` its `brd-link.md` `claims:`. `/brd-split` wrote the claims list and the ledger together
   (§3), so the two normally coincide; where they do not, `claims:` is what this slice is answerable
   for and the narrower set is the right one. **They diverge in exactly one way, and it is benign in
   both directions**: a slice's ledger may hold an **orphan row** — a ledger row for a `[BR#n]` it no longer claims, whose claim `/brd-split`'s walk on the parent withdrew and whose row stays and takes a terminal disposition; that claim was either still provisional or one this slice had committed to and then recorded it would not build, which a re-cut then moved to a sibling (`coverage-ledger-format.md` §2, §3, §3.2). `claims:` names none of them, so none is in this
   gate set — and it must not be read anyway: an orphan row is never `unallocated`, so it could not
   manufacture refusal 1, but one left standing as this slice's own earlier decision can read
   `covered-here` (`coverage-ledger-format.md` §2), and read outside the gate set it would manufacture eligibility. A slice claiming nothing has an empty gate set — the
   standing-empty-child state `/brd-split` Phase 4.5 keeps against a recorded reason — and reaches
   refusal 2 by the empty-set row of the table below, never refusal 1.

   **There is no root branch of this gate any more, and the argument that used to carry one is the
   behaviour step 5a forbids.** It ran: a BRD that owns its source document carries no
   `claims:` field, so a gate defined over `claims:` would read an empty set and "refuse the ordinary
   never-split BRD that is this route's primary case". Refusing it is now the **correct** outcome —
   taken two steps earlier, on the folder's prefix, and without a row being read. A root never
   reaches refusals 1 and 2 at all.

   Every count and list this step and the rest of this command take — `<n>`, each `[BR#n]` list,
   Phase 1's and the final report's "how many rows are `covered-here`" — is taken over this gate set
   and over nothing else.

   **Read every disposition from the ledger file, never from any `ledger:` line.** §5 says so
   outright and §6.1 says why: that line's `unallocated` term is a *resolved* count that also holds
   rows carrying `covered-by` whose named BRD has not walked them yet, so it does not track the
   allocation gate, and a refusal keyed off it would hard-refuse a BRD whose own gate is fully
   satisfied. This command therefore never parses a `ledger:` line and never prints one — that line
   is the BRD-to-PRD route's final-report convention (§6), and this command is not one of them.

   **Refusal 1 — a row of the gate set is still `unallocated`.** Stop gracefully:
   ```
   CREATE_PRD_BRD_UNALLOCATED: <SLICE-KEY>'s coverage-ledger.md still writes `unallocated` on <n> of the <total> requirement rows this slice claims — <[BR#n] list>. coverage-ledger-format.md §5 makes that a hard refusal: the allocation gate was never satisfied, and an unallocated row is neither an implicit `covered-here` nor an implicit `deferred-to` in either direction. Run '/product-workflows:brd-split <SLICE-KEY>' to walk each one to a terminal disposition, then re-run '/product-workflows:create-prd <SLICE-KEY>'.
   ```
   `/product-workflows:brd-split` is safe to name here **because there is something for it to do**: it is
   the command whose walk exists to move exactly these rows off `unallocated`, and on a slice it runs
   allocate-only — one fewer resolution, and no child created. It
   is not, however, unconditionally *startable*: its own Phase 0 gates on this slice's grounding
   findings each carrying a verifier verdict, and stops naming `/product-workflows:prd-ground <SLICE-KEY>`
   when they do not. Say so beside the offer, so an operator whose slice has only been carved is not
   sent into a second stop to learn the same thing.

   **Refusal 2 — no row of the gate set is `covered-here`.** This slice holds no PRD of its own.
   Refuse, and say **where the requirements went**. **The root-reachable cases are gone from this
   table**: a delegated row — `covered-by: <SLICE-KEY>`, the shape a parent's walk writes — is the
   state step 5a's container refusal now reports, in its own branch and two steps earlier, so this table is the two
   cases a **slice** can actually reach. No row of a slice's gate set can be `covered-by`: a slice's
   `covered-by` rows are its orphan rows, which `claims:` does not name.

   | How every row of the gate set left `covered-here` | What this stop says |
   |---|---|
   | The gate set is non-empty and no row is `covered-here` — the ordinary shape a slice reaches | Name **no** sibling slice, because none holds one of these rows — and say what the gate-set rows *did* resolve to rather than calling them all obligations. §5 separates the three remaining dispositions: a `deferred-to` row is a live obligation of this slice, a `rejected` one is an obligation of nobody and cites the `[DEF#n]` justifying it or the customer decision that withdrew it (`rejected: <SLICE-KEY>/[CD#n]`), and a `superseded-by` one was absorbed into the `[BR#n]` that replaced it. Then say a PRD needs one row resolved `covered-here` first |
   | The slice's `coverage-ledger.md` is **absent**, or present and cannot be read, while `brd-link.md` claims rows | **Name no option at all** — report the file by path, as missing or as unreadable with the read error, and stop. This is not an empty gate set: `claims:` names rows and the evidence for judging them is gone, so offering either the sibling enumeration or the emptiness report would send the operator to a decision on evidence nobody has. `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2 rules on exactly this shape; without this row both rows below evaluate false and the likeliest reading takes the empty one, emitting `CREATE_PRD_BRD_NOT_ELIGIBLE` and naming `/brd-split <PARENT-KEY>` — the outcome §5.2 forbids |
   | The gate set is **empty** — a slice whose `brd-link.md` claims nothing | Report the emptiness and enumerate nothing, because there is nothing to enumerate: no requirement **this slice is answerable for** reached any disposition, and naming one would invent it. A standing empty child may still hold orphan rows its parent's walk settled (§2); those are not this slice's requirements and are not reported here as though they were. Name the one run that can change it: `/product-workflows:brd-split <PARENT-KEY>` alone resolves a standing empty child, and it is not a no-op in the state this stop reports — a standing empty child is one of the three things that command's own no-op test accounts for (its Phase 0 step 10). Which form to name depends on the parent's own ledger, so say which. Where the parent still holds an `unallocated` row, that run walks it too and may offer `covered-by` against this slice — one way it stops claiming nothing without being removed — and a run with rows still to place needs a slicing instruction (it stops with `BRD_SPLIT_NEEDS_INSTRUCTION` without one), so the form is `/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"`. Where no parent row is left `unallocated`, the bare `/product-workflows:brd-split <PARENT-KEY>` offers to remove this slice or to keep it against a recorded reason; and where the parent also holds a row a sibling has recorded it will not build, an instruction on that same run — `/product-workflows:brd-split <PARENT-KEY> "<what to peel off>"` — can additionally re-cut that row onto this slice (its Phase 4.5 still runs on that path), another way it stops claiming nothing without being removed, which needs this slice never to have been interviewed. Where the parent's ledger cannot be read, report it by path and name neither form: which one runs is that ledger's to say. Unlike the row above, this one has a next command that exists in the state being reported |

   In the first case **there is nothing to name and a sibling must not be invented**; the
   honest report is what each row actually resolved to, and — for the deferred ones — by whom.
   "The requirements are deferred" is the common shape of that case, not the whole of it: a
   slice whose every gate-set row is `rejected` reaches this same refusal owing nobody anything, and
   saying it deferred them would be false. In the empty-gate-set case there is not even that to report, and
   saying "the requirements were deferred" of a set holding no requirement would be false twice
   over. Stop as:
   ```
   CREATE_PRD_BRD_NOT_ELIGIBLE: no row of <SLICE-KEY>'s coverage-ledger.md that its brd-link.md claims is `covered-here`, so this slice holds no PRD of its own (coverage-ledger-format.md §5). <where the requirements went, per the row above that matches>
   ```

   **What this stop may offer, and what it may not.** Only the empty-gate-set case — the table's
   last row — has a next command that exists in the state being reported: `/product-workflows:brd-split
   <PARENT-KEY>`, the one run that resolves a standing empty child, and not a no-op there, in the form
   that row chooses by the parent's own ledger. The missing-ledger row names nothing, by §5.2. In the
   **first** case **no command is offered at all, and the stop says why rather than going quiet**: re-running
   `/product-workflows:brd-split <SLICE-KEY>` on a ledger with no `unallocated` row is a no-op that
   changes nothing (§4), `/product-workflows:brd-reconcile` never allocates, and no row is ever moved
   back to `unallocated` (§3) — so nothing in this plugin turns a `deferred-to` row into a
   `covered-here` one. Un-deferring a requirement is a decision the operator takes with the customer,
   not a command — and the re-cut does not weaken that, because it acts **on** such a decision already written down, moving a row a *sibling* recorded `deferred-to` against onto a slice that will build it, never reversing one this slice is still committed to (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.2); naming a command here would send the reader into a run that does nothing. Per the
   *When no option is safe to recommend* guidance in
   `Skill(skill: "workflows-core:reference", args: "escalation-rules")`, nothing on that stop is marked
   `(Recommended)`.

   **None of the three refusals carries a merge clause — step 5a's container refusal included, and
   step 5b's Epic-folder refusal no more than they — and
   that is a fact about where they sit rather than an omission.** All of them are Phase 0 stops, taken before this run has a deliverable, a
   branch or a handoff — so there is no `Phase handoff:` outcome line
   (`workflows-core:phase-handoff` §4.1) for a clause to resolve from, and every
   command they name either runs no `require-on-main` gate at all (`/product-workflows:brd-intake`
   consumes nothing — §5's caller table) or gates on artifacts **another** run wrote and already
   merged. Phase 6 holds this
   command's only two placeholder sites — its choice array and the bullet that resolves it — and
   nothing on this route adds a third.

   All three refusals are read **as this run finds the tree**. Refusals 1 and 2 are not defects in
   the slice: a slice that claims rows and has not yet allocated them, and one that claims rows and
   builds none of them, are both ordinary outcomes (§5). What a root BRD reaches is step 5a —
   two steps earlier, on the folder's prefix, on either route, and without a row being read.

7a. **Gate the decision register on main (the BRD route only).** Phase 2 reads the slice's
   `decisions.md` as settled content — every `[VD#n]` and `[CD#n]` in it is frozen against this
   run's grill — so it is read only once it is on the specs repo's default branch. Taken after step
   7's refusals, so a slice that holds no PRD of its own is told that first, and before Phase 1
   resolves documentation grounding (`workflows-core:phase-handoff` §5 rule 2). Execute
   `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3)
   against `<slice-dir>/decisions.md`, the slice folder step 5 resolved, and map its §3.7 return by
   `stopped` first, never by `on_main` alone:
   - **Any stopping row** → stop per §4.4, as `CREATE_PRD_REGISTER_NOT_ON_MAIN` below.
   - **`pass`** → proceed; **`pass_amending`** → proceed, printing the §3.3 row-B message;
     **`unmanaged`** → proceed as before this gate existed.
   - **`absent` (row F)** → split it on a test row F cannot make — is the file in the folder at all:
     - **No `decisions.md` in the folder** → exactly as before this gate: Phase 2 reports the
       register absent and carries what the folder holds. Nothing becomes a prerequisite
       (§5 rule 3); a slice nobody has interviewed holds no register, and that is not a stop.
     - **A `decisions.md` in the folder, and on no ref** — the run that wrote it had its handoff
       declined — → stop, as `CREATE_PRD_REGISTER_NOT_HANDED_OFF` below. Reading it would freeze
       this PRD against decisions only a working tree holds, the state this gate exists to refuse.

   Both stops carry §4.4's four parts, in order:
   ```
   CREATE_PRD_REGISTER_NOT_ON_MAIN: <SLICE-KEY>'s decision register <path> is <the state require-on-main reported — on branch <branch> with PR #<n> open, not merged | on branch <branch> and never handed off | changed in the working tree against <default> (<files>) | any other stopping row, as §3.3 words it>. This run read none of it and wrote nothing: a PRD frozen against [VD#n]/[CD#n] records that are not on <default> would rest on decisions nobody merged. <the resolving commands §4.4 prescribes for that row, $SPECS_PATH substituted — merge PR #<n>, open one for <branch>, or commit, stash or discard the working-tree edit>, then re-run '/product-workflows:create-prd <SLICE-KEY>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
   ```
   ```
   CREATE_PRD_REGISTER_NOT_HANDED_OFF: <SLICE-KEY>'s decision register is written at <path> but is on no branch — the run that wrote it had its handoff declined. This run read none of it and wrote nothing. Commit and merge decisions.md to the specs repo's default branch (git -C "<SPECS_PATH>" add, commit and push it, then open and merge its pull request), then re-run '/product-workflows:create-prd <SLICE-KEY>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
   ```
   Neither is a plugin gap, so neither `emit-block`s (Phase 7).

`/create-prd` is **cwd-agnostic** and needs **no repos mounted** (product-level; no code scan).

---

## Phase 1 — Configure

Use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`workflows-core:escalation-rules` §0).

1. **Confirm** the feature folder, the profile, and the resolved `idea.md` (or "none — grill from scratch"); on the BRD route, the resolved `PRD-` slice folder, the profile (`--full` unless a flag overrode it), and — instead of an idea — a `from BRD:` line naming `<SLICE-KEY>` and the `parent:` its `brd-link.md` records (always present — step 5a refuses the container), its `depends-on:` if any, how many of its gate-set rows (Phase 0 step 7) are `covered-here` out of how many, and whether `prd-seed.md` and `decisions.md` were found.
   - **Resolve documentation grounding here, then show its line.** Run `resolve-docs-grounding create-prd` per `Skill(skill: "workflows-core:reference", args: "docs-grounding resolve-docs-grounding")` — its step 3.5 index prompt included — and show the `docs grounding:` line from what it returns, in the form that reference fixes — `ON <root> (retrieval: …)` or `OFF (<reason>)` — verbatim, including any index-build, staleness, or shadowing clause it carries (off switch: --no-docs). It runs here, before any agent is dispatched, because step 3.5 asks its one-time index question before the run's real work; this is the run's one resolution (`workflows-core:docs-grounding`, *Invariants*), and Phase 2.5 dispatches on the state it returns without resolving again.
2. **Existing-PRD handling** (only if Phase 0 step 6 found a PRD for `<KEY>`): **Where that `prd.md` cannot be read at all, stop here instead of offering a choice**: no option
   below can succeed on it — the recommended one hands it to `/update-prd`, which must read it as its
   base, and Overwrite must copy it into `revisions/` before the first write — so stop before any
   grill or write:
   ```
   CREATE_PRD_PRIOR_UNREADABLE: <feature-folder>/prd.md exists but cannot be read (<error>). /create-prd counts any prd.md as an existing PRD and never overwrites one it cannot archive, and /update-prd cannot refresh one it cannot read. Make the file readable, then re-run '/product-workflows:create-prd <KEY>'.
   ```
   Where it reads but its frontmatter does not parse, say so above the choice; its bytes still copy.
   - **the BRD route present** → "author this slice's PRD" conflicts with "a PRD for this slice
     already exists here". **`/update-prd` has no BRD route** — it takes one address and refreshes
     the `prd.md` it finds there — so the redirect is honest about what it drops: it refreshes the
     PRD already on disk, it does not re-read the seed. It resolves the **same folder** this run did,
     which is why one address serves both.
     ```
     choices: ["Refresh the existing <SLICE-KEY> PRD — /product-workflows:update-prd <SLICE-KEY> (the BRD seed is not re-read) (Recommended)", "Overwrite <SLICE-KEY> as a fresh PRD authored from the BRD seed (archives the current one)", "Cancel"]
     ```
   - **No `--from-prd`** → `/create-prd` is greenfield-only; **redirect**:
     ```
     choices: ["Switch to /product-workflows:update-prd <KEY> to refresh it (Recommended)", "Overwrite as a fresh PRD (archives the current one)", "Cancel"]
     ```
   - **`--from-prd` present** → "create new (seeded)" conflicts with "a PRD already exists here":
     ```
     choices: ["Update the existing <KEY> instead — /product-workflows:update-prd <KEY> (seed ignored) (Recommended)", "Overwrite <KEY> as a new seeded PRD (archives the current one)", "Cancel"]
     ```
   **The archive every Overwrite option names is Phase 3's pre-write archive**, which copies the
   existing `prd.md` into `revisions/` immediately before this run's first write to it; nothing in
   this phase copies or moves it.
3. **Draft idea → warn-and-fold** (no-op on the BRD route, which resolves no idea; the equivalent there is the open `[VD#n]`/`[CD#n]`/`[AS#n]` set Phase 2 carries in). If `idea.md` is `status: draft` (open `[NEEDS CLARIFICATION]`), note that the grill resolves those items — do **not** hard-block.

---

## Phase 1.5 — Classify + model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then record:

```yaml
model_routing:
  classification: MODERATE        # typical; SIGNIFICANT for large/cross-cutting PRDs
  reason: <one-line>
  current_model: <the model this orchestrator/grill is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # impl-maintenance
  review_model:    <§2 Opus chain>     # prd-reviewer (frontmatter-pinned; recorded, no override unless §10 enforces a model)
  authoring_model: <= current_model>   # the interactive grill + PRD authoring (session model, not a delegated subagent)
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2/§2.1 fallback or degradation>
```

The grill + authoring run inline on `current_model` (the §2 Opus chain — interactive judgment, not a delegated subagent). If no Opus resolves, **degrade to best-available + record** in `notes` and the final report — do not hard-block. Under `run_flags.enforced_model` (`workflows-core:model-routing/classification` §10) no degradation is recorded; dispatched steps use the enforced model, while the grill and authoring still run on `current_model`.

**Profile nudge (complex PRDs).** If `classification` is **SIGNIFICANT** (a
complex / cross-cutting PRD) and the chosen profile is `--lean` or `--hybrid`
(so `[FR#N]` is unavailable — it is full-only), surface a one-line **non-blocking**
recommendation before Phase 2:
> "This PRD classifies SIGNIFICANT — consider `--full` so Functional Requirements
> (`[FR#N]`) and richer Use Cases (`[UC#N]`) are available for stronger, more
> traceable downstream Epic coverage."

Offer `choices: ["Switch to --full", "Keep <profile>"]`. On
"Keep", proceed unchanged. For a SIMPLE / MODERATE classification, or when the
profile is already `--full`, this nudge does **not** fire.

---

## Phase 2 — Read the seed

Read the resolved `idea.md` **directly** (it is the plugin's own format — `idea-reader` is for arbitrary external sources and is not used here). Extract Problem / Who / desired outcome & value / rough scope / signals & evidence / candidate success signal, plus any open `[NEEDS CLARIFICATION]`. Carry the idea's `sources[]` forward to **propagate** into the PRD frontmatter (the real provenance — each `sources` entry exactly as `idea.md` recorded it, `provenance` and `ref` alike, and `vendored` only where the idea read is the in-contract `idea.md` in the resolved folder, whichever rung read it: `vendored` is a path relative to the folder holding that `idea.md`, so from an idea in any other folder it names nothing in this one, and it is dropped there), and record `derived_from` = the idea's own resolved path — read here from `idea.md`'s own frontmatter, never from a relocation, since `/create-prd` no longer moves it.

Optionally ground in the idea's cited sources and any strategy/vision docs the user points to. **No code scan; no repos.**

**Text sources only — an image citation is carried, never opened here.** `## Signals & evidence` may cite images the idea's original source linked, because the `/idea` run read those for its own grill: its Phase 1.5 walks every link the source makes, asking the operator before reading past its older bounds, and `figure-reader` transcribes each image that walk takes (`commands/idea.md` Phase 1.5 and Phase 2). That walk, the operator's answer to it and its report of every exclusion belong to that run and do **not** travel with the file, so opening an image path found here would be a read nobody consented to and nothing reports. What those frames showed has already been put to the operator and survives in the idea's prose; treat the path as provenance and read the prose.

If `--from-prd` was resolved (Phase 0 step 2a), also read the **seed PRD** (body + comments) as read-only
grounding — structure, personas, scope shape, and metrics to *adapt* (never copy) to the new PRD.

If there is no idea (Phase 0 ladder exhausted), grill the PRD from scratch.

### the BRD route — read the product-altitude seed and the decision register

Read exactly two files from the BRD folder Phase 0 step 5 resolved, and no other seed:

- **`prd-seed.md`** — product-altitude content, when the folder holds any. **Where to look, and it is two places.** The resolved slice first. Then, when the slice holds none, the **parent BRD folder** named by `brd-link.md`'s `parent:` — that is where `--sort-existing` actually writes all three seeds, because slices do not exist when intake runs. A seed found there is BRD-wide content, not slice-scoped: read it as context for this slice, say which folder it came from, and never treat it as though it were written for this slice alone. Finding neither remains the ordinary case. **No `/brd-*` command creates this file on the normal route** — the one command that creates one is
  `/product-workflows:brd-intake --sort-existing`, a one-time migration path for a package authored
  by hand before this route existed. Its absence is therefore the **ordinary** case, not a
  degraded one, and is reported rather than treated as a gap; what the route actually carries at
  every altitude is `decisions.md`, filtered by `altitude`, plus the grounding files.
  **`ard-seed.md` and `spec-seed.md` are not read**, at all: they are the architecture and
  implementation altitudes of the same router, belonging to `/create-ard` and `/specify`, and
  pulling either in is how a PRD acquires the implementation detail
  `workflows-core:prd-format`'s quality rules forbid.
- **`decisions.md`** — the register, per
  `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1. Phase 0 step 7a has already gated it on the default branch, so
  what is read here is the merged register or, where the folder holds none, nothing. It is read through §8 there: a **torn write** — a record a `/brd-interview` run left when it
  stopped before writing the round record that would name it — is read as absent, frozen against
  nothing and stamped `consumed_by` by nothing.

A BRD-route run with **no `prd-seed.md`** is not a stop, and is the **ordinary** shape: nothing on
the normal route creates a seed file at all (above), so a reconciled BRD routinely holds none. Say so
plainly, carry `decisions.md` alone, and let the grill fill the spine from it — a silent fall-through to "grill from scratch" would lose the
register too. A run with **no `decisions.md`** is likewise not a stop; report which of the two was
absent, since a reader cannot tell an unwritten register from an unread one.

**Partition the register before the grill starts, because the partition is what freezes it.**

| Register state (§3) | What this run does with it |
|---|---|
| `decided` | An **input**. It is settled content the PRD is authored *from* — never a question, never re-argued, and never re-answered because this run would have chosen differently |
| `superseded` / `withdrawn` | Terminal (§3). Read for context; never revived, and a `withdrawn` request is never re-asked |
| `open` | **May not be consumed downstream while it is open** (§3). It is a gap, not a decision: it reaches the PRD under `## Assumptions & open questions`, named by its id, and the grill may settle the *PRD's* wording around it without settling the decision itself |
| `reopened` | Was reopened upstream under §4 and is not yet re-decided — handled exactly as `open` |
| `[AS#n]` (open) | An assumption, not a choice (§7). Same treatment as `open`, and it keeps its `[AS#n]` id in the PRD so the reader can find the record that admits its own groundlessness |

Carry each `decided` record's `altitude` with it: only `product` ones have a product-altitude home
here. An `architecture` or `implementation` decision is read for context and **left for the command
that authors at its altitude** — `/product-workflows:create-ard` and `/product-workflows:specify` — and it is
not discarded by being skipped. **The channel that carries it is `decisions.md` itself, not a seed
file.** Both of those commands read this same register and filter it by `altitude` exactly as this
phase does, so a decision skipped here is picked up there from the file it was already in. Say so
rather than naming a seed: `ard-seed.md` and `spec-seed.md` are created by nothing on this route
(only `/product-workflows:brd-intake --sort-existing` creates one, migrating a package authored before
the route existed), so an operator told a decision was "routed to its seed" would go looking for a
file that is not there and conclude the content was lost.

**One profile leaves the gaps homeless, and the run must not discover that silently.**
`## Assumptions & open questions` is an adapt-in cluster, so an explicit `--lean` overriding the
the BRD route default (Phase 0 step 2) gives this PRD a spine and nothing else — and every `open`,
`reopened` and open `[AS#n]` the partition just produced would have no product-altitude section to
land in. Where the register holds at least one such record and the profile is `--lean`, surface a
**non-blocking** choice before Phase 2.5, naming the count:

```
choices: ["Switch to --full so the open register items have a home (Recommended)", "Switch to --hybrid (light open-questions list)", "Keep --lean — the open items are reported by id, never written into the PRD"]
```

On "Keep `--lean`", the final report names every one of them by id. A gap this command silently drops
is one no later reader can find, which is the failure the register's own `[AS#n]` surfacing rule
exists to prevent.

---

## Phase 2.5 — Grounding: documentation (optional)

This phase dispatches one grounding agent, the docs grounder.

**Docs.** Phase 1 resolved documentation grounding and showed its line; this phase resolves nothing again. Where it resolved `docs_grounding: ON`, `dispatch-docs-grounder` (`workflows-core:docs-grounding`) with `feature_summary` = the idea's problem/goal + PRD themes, `key` = `<KEY>`, and `themes` from the idea. Where it resolved OFF, dispatch nothing.

**On the BRD route the docs grounder runs unchanged; only its inputs are substituted**, because
there is no `idea.md` to take them from. `feature_summary` and `themes` come from `prd-seed.md`
(falling back to the `statement` of each product-altitude `decided` record when the seed is absent).
It is not given `ard-seed.md` or `spec-seed.md`.

Carry the digest into Phase 3 with **grill-rank** consumption. When docs grounding is OFF the PRD is authored exactly as it is without a digest.

---

## Phase 3 — Author via grill

**Interview technique (grilling — embedded; no runtime dependency).** Conduct a **relentless** interview per `Skill(skill: "workflows-core:reference", args: "grilling-technique")` — one question at a time, recommend each answer, fact-vs-decision split (look up facts from the idea/sources; put only decisions to the user), walk the design tree in dependency order, continue to shared understanding then write each section. Rank every `docs_challenges` entry from Phase 2.5 into the grill's question order; a challenge competes for attention, it never suspends the spine below.

**Pre-write archive — before this run's first write to `prd.md`.** Immediately before this run's
first write to `<feature-folder>/prd.md` — ordinarily the first live write of the authoring below,
and wherever that write falls — test whether the file exists. Where it does, archive it first, **on
every route, with no exemption** — the idea route, `--from-prd` and the BRD route alike, and
whichever Phase 1 step 2 choice brought the run here: copy it into `<feature-folder>/revisions/` by
the rule `/product-workflows:update-prd` Phase 3 fixes (*Archive the base before the first write*) —
`<KEY>_<slug>_<YYYYMMDD>.md`, `<slug>` the resolved folder's own name less its `<KIND>-<KEY>-`
prefix, or less `<KEY>-` on a legacy unprefixed folder, and `<KEY>_<YYYYMMDD>.md` where nothing
remains, and where that name is taken by any file, the first free of that name with `-2`, `-3`, …
inserted before `.md` — and report the archive path. This is the archive Phase 1 step 2's Overwrite options name,
and it also covers a `prd.md` that appeared after Phase 0 step 6 looked. **It runs once per run**:
where the file did not exist, nothing is archived and nothing later is, and every later write in
this run — Phase 3.5's and 3.6's inline fixes, Phase 4's BLOCKER fixes, Phase 5 — is a write to this
run's own draft and archives nothing. None of the subagents handed the path — `prose-style-checker`
(Phase 3.5) and `prd-reviewer` (Phase 4) — writes to it; each reads the draft and returns findings
the orchestrator applies. **On the BRD route, take it before this run's first write to
`decisions.md` as well**, where that would come first, so a failed copy strands no `[AS#n]`.
**Where the copy fails** — the file cannot be read, or `revisions/` cannot be written — stop before
writing anything:
```
CREATE_PRD_ARCHIVE_FAILED: could not archive <feature-folder>/prd.md to <archive path> (<error>). Nothing was written — /create-prd never overwrites a PRD it has not archived. Make the file readable and revisions/ writable, then re-run '/product-workflows:create-prd <KEY>'.
```

Author `prd.md` live against `Skill(skill: "workflows-core:reference", args: "prd-format")` for the selected profile, applying the no-hard-wrap prose convention in `Skill(skill: "workflows-core:reference", args: "prose-formatting")`. Walk the **spine** in dependency order:

1. Frontmatter — `sources` (propagated), `derived_from`, `seeded_from_prd` (only when `--from-prd` was used), and `key` — **written on every route**, set to the address this run resolved. On either route it is the `key:` the resolved folder asserts (`workflows-core:addressing` §4) — the positional key the operator chose on the `/idea` route, and the slice's own key on the BRD route, which is also the name of the folder this PRD is written into.

   **Do NOT ask for `release_versions`, `change_type` or `release_notes_category` here.** They are
   authored fields now rather than tracker dropdowns returned by an import
   (`workflows-core:prd-format`), and `/release-notes` gets what it needs of them itself: where the
   PRD carries no routable `change_type` it infers one, confirming it in its own grill where the
   inference is uncertain, and it takes the release from its `--version` flag or that same grill, never from the
   PRD's `release_versions` — so never spend a question here on an answer that command gets anyway —
   and it omits the category label where `release_notes_category` is absent, never inferring or
   asking for one, so that field is optional: a draft without it is complete. Write whichever the
   operator volunteers; never invent one. An unanswered field is omitted, not filled.

   **`key` was for a time omitted on the BRD route**, deferred to a tracker step — long retired — that once minted a separate identity and wrote it back. Once that step was gone nothing wrote the field at all, so it stayed permanently unset — which is the defect the spine item above closes by writing `key` on every route. Left unset, `/document` and `/release-notes` build their commit scan from a `key` that is empty and silently match nothing. (The folder still resolves either way: a slice's carrier is its `brd-link.md`, which `workflows-core:addressing` §4's order reads before `prd.md`.) There is no second identity to keep straight any more: one namespace, one grammar, and the folder's key is the key.
2. **Problem**
3. **Goal** (crisp 2–3 sentences)
4. **Target audience** (personas)
5. **User Stories** (`[US#N]`)
6. **Acceptance Criteria** (`[AC#N]` per story)
7. **Scope** (In / Out)
8. **Success Metrics** (`[SM#N]`)

Then author the profile's **adapt-in clusters**, each **pulled only when the idea warrants it** (never an empty section). **For a complex PRD (`classification` SIGNIFICANT), actively author the `[FR#N]` (full) and `[UC#N]` (hybrid/full) clusters** within the chosen profile — lower the bar for pulling them in, because ID'd functional requirements and use cases feed a finer downstream `/epics` `_coverage.md` (traceability to `[FR#N]`/`[UC#N]`, not only `US`/`AC`/`SM`); still never an empty section. Fold the idea's open `[NEEDS CLARIFICATION]` into the grill; resolve to zero where possible, leaving genuinely-unresolvable ones under `## Assumptions & open questions` (hybrid/full). Keep the PRD **product-level** — no implementation detail. **Self-consistency check:** before writing each section, check it against the already-settled sections — a new `[AC#N]` must not deliver an Out-of-scope behaviour, the `## Goal` must not assert a scope the `## Scope` contradicts, and `[US#N]`s must not conflict. Resolve any contradiction inline with the user, or record it under `## Assumptions & open questions` — never leave it implicit (the Opus `prd-reviewer` flags a silently-baked contradiction).

### the BRD route — the grill is restricted to gaps

**The grill may fill anything the seed does not settle. It may not reopen a `[VD#n]` or a `[CD#n]`**
(D3). Those decisions arrive carrying customer sign-off in writing, and a grill that re-litigates one
manufactures a contradiction between this PRD and a document the customer has already agreed to.

**Three things make that a guarantee rather than an instruction, and the third is the one that holds
when the first two are forgotten:**

1. **The question set is a subtraction, not a sweep.** Phase 2's partition already sorted the register
   into inputs (`decided`), terminal records (`superseded`, `withdrawn`) and gaps (`open`,
   `reopened`, open `[AS#n]`). The grill's questions are derived from the gaps and from what
   `prd-seed.md` leaves unstated — a settled `chosen` is never a question, so there is nothing for
   the interview to walk it back through.
2. **This run cannot satisfy either cause that would license a reopening.**
   `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4 admits exactly two, and
   `/create-prd` produces neither: it runs no grounding at all — it is cwd-agnostic and mounts no
   repos, so it can mint no new finding — and it receives no customer review, which reaches the
   register only through `/product-workflows:brd-reconcile`. A grill answer is neither of the two, whatever
   it says.
3. **On a record that already exists, the only field this command may write is `consumed_by`**
   (Phase 5). **Every other field `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1
   defines is never written onto an existing record here, in any status** — named as a set rather
   than enumerated, so a field §1 gains is covered the day it gains it and no list here can drift
   from the one it stands for. That set takes in every field a re-decision or a reversion writes
   **save `consumed_by`**, the one field this command does write and the one both of those return
   to `none`; the two writing sets are §4's to fix, and this command performs neither — a
   re-decision needs a reopening, which rule 2 has just ruled out, and a reversion is
   `/product-workflows:brd-reconcile`'s propagation sweep alone (§4). So a grill
   answer that contradicted a `decided` record could not become that
   record's new `chosen` even if the first two failed: there is no write that would record it.

   **This guarantee was once stated over every record rather than every existing one, and the
   narrowing is itemised here rather than made silently** (`workflows-core:instruction-file-maintenance`).
   What it protects is a settled decision against a grill answer, and that protection is untouched:
   nothing below edits a record anyone has decided. What it now permits is Phase 3 **creating** one
   new record of one kind — an `[AS#n]`, never a `[VD#n]` and never a `[CD#n]` — for a
   customer-authority gap, in the fields §7's own table admits for one. A newly minted assumption
   overwrites nothing and settles nothing; it records that this PRD had to assume something, which is what an
   `[AS#n]` is for.

**What happens when the grill surfaces a genuine contradiction with a settled decision** — which is
useful information, not something to suppress. Do not decide it and do not soften the decision into
the PRD's prose. Record it under `## Assumptions & open questions` — or, on a kept `--lean` where
that cluster does not exist, in the final report alone — naming the `[VD#n]` or `[CD#n]` it
contradicts and what the run believes contradicts it, and say which of the two routes may act on it.
**Neither route is this command**, and both are exactly `decision-register-format.md` §4's two
causes rather than a third one invented here: a `[VD#n]` needs a **new grounding finding** first,
which only `/product-workflows:prd-ground <SLICE-KEY>` mints — with `--rebaseline` where the pinned
code has moved — and `/product-workflows:brd-interview <SLICE-KEY>` then re-decides against; a
`[CD#n]` needs the **customer**, through `/product-workflows:brd-package <SLICE-KEY>` and then
`/product-workflows:brd-reconcile <SLICE-KEY> @<review-file>`. Naming the route is what keeps the
contradiction actionable without this command taking the decision.

**A gap the grill cannot close is triaged by who could settle it, and a customer-authority one gets
a route rather than a paragraph.** PRD authoring surfaces questions nothing before it could have —
a scope boundary the requirement text never drew, a rule the acceptance criteria need and nobody
stated. Apply `${CLAUDE_PLUGIN_ROOT}/references/interview-tagging.md` §2's test to each one that
survives the grill: what kind of thing would settle it?

- **A repository at a pinned commit** → it is a grounding question, not a PRD question. Name it in
  the report with `/product-workflows:prd-ground <SLICE-KEY>` as the route (with `--rebaseline`
  where the pinned code has moved), and record it under `## Assumptions & open questions` in the
  meantime.
- **A trade-off the delivery team owns** → record it under `## Assumptions & open questions` and name
  `/product-workflows:brd-interview <SLICE-KEY>`, which is where a `[VD#n]` is taken. This command
  never takes one.
- **An authority only the customer holds** → **write it as an `[AS#n]` in `decisions.md`**, per
  `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §7 — creating the file, where the
  folder holds none, with its header line `# Decision register: <SLICE-KEY>` first (§1). **Write
  every field §7's own table admits for an `[AS#n]`, in the meaning and the vocabulary that table
  gives it, and none of the ones it marks *Not applicable*** — §1.1 omits a field that does not
  apply rather than writing it empty, and `/product-workflows:brd-package` puts every open `[AS#n]`
  in front of the customer, so a weighed-choice field written onto an assumption shows them a record
  saying an option was picked where nothing was weighed. Do not re-derive which fields those are
  here: the table accounts for every one of §1's set, one by one, and a count written in its place
  is what goes stale the next time that set moves — which is how this instruction came to ask for
  three fields §7 rules out. **`round` is omitted entirely** — this record came from no interview
  round, and any value there is read by `/product-workflows:brd-package` as a round it must find a
  record for. `evidence` carries the account of why no evidence exists; a bare sentence is a claim,
  not an assumption record. A `[BR#n]` this slice does not claim is written `<PARENT-KEY> [BR#n]`
  in it, `<PARENT-KEY>` being the slice's `parent:` — `/product-workflows:brd-interview`'s rule (*A
  row this slice does not claim*), read off this slice's inventory: the register ships in the
  slice's next package, whose citation-resolution check stops on a bare id naming a row outside
  that inventory. Record it under `## Assumptions & open questions` **as well**, by its `[AS#n]`
  id, so the PRD's reader and the customer meet the same record rather than two descriptions of it.

**Two mechanics the three bullets above share.** First, **`## Assumptions & open questions` does not
exist on a kept `--lean`** (Phase 1), so on that profile every one of them records into the final
report instead, exactly as the contradiction paragraph above already does — the `[AS#n]` is still
written to `decisions.md`, which is a different file and unaffected by the profile. Second, **ids are
continued, never restarted, and a gap already recorded is not recorded twice**: read `decisions.md`
first, take the next `[AS#n]` after the highest on file, and where an open `[AS#n]` already states
this same gap, leave it alone and name it in the report. The sanctioned *Overwrite as a fresh PRD*
re-run (Phase 1 step 2) puts this command over the same folder more than once, and without both halves one
gap accumulates several open assumptions — each of which `/brd-package` then puts in front of the
customer twice.

**The third case is the one this step exists for, and the reason is that `prd.md` reaches nobody who
could answer.** A customer-answerable question written only into the PRD is met by every later reader
as a flat statement in a document full of grounded ones — read as settled, built on, argued from —
while the one party who could have corrected it in a sentence never sees the file. `[AS#n]` is the
route back that already exists: `/brd-package` surfaces **every** open assumption, twice, and
`/brd-reconcile` records the answer as a `[CD#n]` that supersedes it. **Writing the `[AS#n]` is not
asking the customer anything** — no `[CD#n]` is written here and none may be (D14), and this command
still never puts a question to a customer directly. It records what the PRD had to assume, and names
the two runs that carry it: `/product-workflows:brd-package <SLICE-KEY>`, then
`/product-workflows:brd-reconcile <SLICE-KEY> @<review-file>`.

**`workflows-core:prd-format`'s no-implementation-detail rule is not relaxed** (D4). A gap the grill can only
fill with implementation detail is not a gap this PRD closes: the detail belongs to `ard-seed.md` or
`spec-seed.md` and their consumers, which is what the design's *Altitude routing* router exists for
(D5). Say where it went; never discard it, and never widen the PRD to hold it.

---

## Phase 3.5 — Prose style check

Run a prose style check on the authored PRD **before** the review gate. This
is a **quality enhancement, not a gate** — it never blocks the handoff.
`prd-reviewer` (Phase 4) judges content; style / terminology is checked here
(mirrors `/epics` Phase 6.2).

→ Agent (subagent_type: "prose-style:prose-style-checker", model: `<detection_model — §2.1 Sonnet chain>`):
  > "Run the style check for this brief:
  >
  > files:    [absolute path to prd.md]
  > doc_type: prd
  > emphasis: terminology and customer-facing captions, labels, messages, and text"

Act on the return:
- **`OK`** — proceed to Phase 4.
- **`VIOLATIONS_FOUND`** — the orchestrator/grill applies the **MAJOR** fixes
  **inline** (no delegated writer — consistent with Phase 4's inline-fix model),
  then re-runs `prose-style-checker` **once**. Remaining MINOR/NIT are recorded in
  the final report.
- **`ERROR`** — surface the reason and proceed to Phase 4 (non-gating).

`prose-style` is a declared dependency of `product-workflows`, so this phase has
no absent case to skip — `prose-style-checker` always runs before the review
gate.

---

## Phase 3.6 — Structural pre-lint

Before the review gate, run the deterministic checks in `Skill(skill: "workflows-core:reference", args: "pre-lint")` against the drafted `prd.md`: the
**Universal checks**, the **key-collision** check (run on the PRD body below the frontmatter),
and the **PRD** block. Surface every finding; inline-fix the mechanical ones
(renumber a duplicate `[US#N]`/`[AC#N]`/`[SM#N]`, delete a stray placeholder token); leave content gaps
(missing section, unresolved `[NEEDS CLARIFICATION]`) for the grill/author. **Advisory** — never blocks;
proceed to Phase 4 once findings are surfaced. `prd-reviewer` remains the gate.

## Phase 4 — Review gate

Dispatch `prd-reviewer` (Opus, frontmatter-pinned; recorded as `review_model`, no override unless §10 enforces a model):

→ Agent (subagent_type: "product-workflows:prd-reviewer", model: `<review_model — §2 Opus chain, equal to prd-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the Product Requirements Document:
  >
  > PRD path: [absolute path to prd.md]
  > Profile: [lean | hybrid | full]"

Act on the verdict (mirrors `/specify`):
- **`BLOCK`** — fix the BLOCKER findings inline (the orchestrator/grill edits the PRD — no delegated writer) and re-review **once**. If still `BLOCK`, escalate per the `Review verdict BLOCK` rule in `workflows-core:escalation-rules` for each unresolved BLOCKER (`choices: ["Provide manual fix notes", "Defer to a follow-up issue", "Override and accept", "Cancel"]`).
- **`PASS` / `PASS WITH RECOMMENDATIONS`** — proceed. Cap: one fix cycle + one re-review.

**The recorded verdict names the version it was taken against** — where any edit followed it, the final report says so and names the edits, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Where none did, it says that too.

---

## Phase 5 — Handoff

Write the feature folder: `prd.md` — where this is the run's first write to it, which it is not
when Phase 3 authored the draft live, the pre-write archive (Phase 3) runs first. The in-contract `idea.md` is already there, committed by `/idea`; an out-of-contract idea stays where it is.

**On the BRD route, also close the consumption loop before the offer.** The design's *Consumption
tracking* section (§7.3) has every finding and decision record a `consumed_by`, so that "nothing was
lost" is checkable rather than hoped for. Set `consumed_by: PRD` on each product-altitude
`decided` record in `decisions.md` this PRD actually took content from — and on nothing else: a
record this run read for context and did not use is still `none`, and marking it consumed would
report a routing that never happened. This is the only write this command makes onto a
record that already exists in `decisions.md`, and it is not a `status` change. **The run makes one
other write into that file** — Phase 3's new `[AS#n]` for a customer-authority gap — which creates a
record rather than editing one, which is why the write guarantee above is stated over existing
records; both are staged in Phase 5's handoff. Everything at product altitude still
`none` afterwards goes in the final report by id, per §7.3.

**`prd-seed.md` is reported, not stamped, and the difference is a fact about the authorities rather
than an inconsistency.** `consumed_by` is a field of a *record*: it is defined on a decision by
`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1 and on a grounding finding by
`workflows-core:grounding-format` §2. The seed carries neither — it is
altitude-sorted content, and no reference in this plugin fixes an item shape inside it — so there is
no per-item field to write, and inventing one here would mint a format this command alone
understood. The seed's consumption is therefore reported at **file** granularity in the final report
(consumed, or consumed in part with what was left over), and `decisions.md` is the only BRD file
this run writes to.

Then **offer** (commit-when-asked — never automatic), invoking `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and presenting its §4.3 choice array verbatim:

```
choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]
```

On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix: prd`, `feature_folder` as resolved in Phase 0, `deliverable_paths` = the PRD file, plus the archived snapshot where the pre-write archive (Phase 3) wrote one (an uncommitted archive is one no later run can read) — **plus, on the BRD route, `decisions.md`**, because both of this run's register writes land there — the `consumed_by` stamps, and any `[AS#n]` Phase 3 recorded for a customer-authority gap — and an uncommitted register is one no later run can read, which for the `[AS#n]` means the question never reaches `/brd-package` and so never reaches the customer; `prd-seed.md` is not staged, because this run does not write to it — `title: <KEY> Add Product Requirements Document — <summary>`, and `body_facts` = the resolved profile (`--lean`/`--hybrid`/`--full`), the adapt-in clusters pulled, the user-story and acceptance-criteria counts, any `[NEEDS CLARIFICATION]` markers carried in, the `prd-reviewer` verdict, and — on the BRD route — the `<SLICE-KEY>` this PRD was seeded from and how many items were marked `consumed_by: PRD`; emit its §4.1 outcome line in the Final report.

---

## Phase 6 — Next steps

Offer these — clearly labeling the role handoff:

```
choices: ["Draft the release note now — /docs-workflows:release-notes <ADDRESS> (PM) (Recommended)", "Hand to a Product Architect — /product-workflows:create-ard <ADDRESS> (PA, optional) <merge-clause>", "Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE)", "Stop here"]
```

**One address appears in that array, and every option takes the same one** — `<ADDRESS>`, this run's
own resolved address, which is the `key:` the folder asserts and names the folder this run wrote
into. There is no second key to keep straight and no flag to carry: `/product-workflows:create-ard` and
`/product-workflows:epics` each resolve that folder through the same entry point, and on the BRD route
the address is the `PRD-` slice's own key, which is what `/brd-split` carved and what step 5a's
refusal leaves standing. (This paragraph once distinguished `<KEY>` from a second positional key and
carried `--from-brd` into the PA option; D4 retired the pair and D18 retired the flag.)

- **`/docs-workflows:release-notes <ADDRESS>`** (PM) — draft the customer-facing release note now (the cost model's `pm`/`prd-creation` inferred case: no spec/design yet).
- **`/product-workflows:create-ard <ADDRESS>`** (PA, **optional**) — hand to a Product Architect to author the grounded architecture document. It gates this PRD on the specs repo's default branch (its own Phase 0), so it stops where this PRD reached a branch and falls back to the resolved folder — reported, never silently — where it reached none; **on the BRD route** it also gates the `decisions.md` this run stages and stops where that is on a branch or on no ref (see the PA paragraph below). `<merge-clause>` is the placeholder `workflows-core:next-phase-offer` owns, resolved from this run's own `Phase handoff:` outcome line (§4.1) and never written as the unconditional "once the pull request above is merged": a declined handoff, a failed push and a nothing-to-commit run — among the other outcomes §4.1 lists — each leave a different wait, and none of those three opens a pull request to wait on. It is a placeholder, not an instruction to reword an option, so the array is still presented verbatim per `workflows-core:escalation-rules`.
- **`/product-workflows:epics <ADDRESS>`** (PE) — hand to a Product Engineer to split the PRD into Epics (or author a PRD-level spec → `/product-workflows:specify <ADDRESS>`, which resolves the same folder through the same entry point).

The other two options carry no clause, and that is checked, not assumed: `/docs-workflows:release-notes` runs no `require-on-main` at all, and `/product-workflows:epics` gates only `<PRD-dir>/specification.md` — a file this run does not write.

**Every option is presented unconditionally now, and the reason the two used to be withheld is
gone.** `/product-workflows:epics` and `/docs-workflows:release-notes` were held back until a key had been minted outside the plugin *and* an export produced against it, because both resolved that export and found nothing without it. Neither reads an export any more: both resolve a folder in the specs tree, which
this run has just written. So there is no half-done state to report and no `(Recommended)` marker to
withhold — the offer says what it always meant to say, one phase earlier.

**The PA option reads `/product-workflows:create-ard <ADDRESS>` on both routes.** It resolves the folder
with `resolve-address` and reads the PRD there on both routes — and, on the BRD route, the
`ard-seed.md` where one was left, the register and the grounding findings besides. On both routes its
Phase 0 gates the `prd.md` this run wrote, and on the BRD route also the `decisions.md` this run's
handoff stages (its register gate), so its option carries the clause on both, resolved per
`Skill(skill: "workflows-core:reference", args: "next-phase-offer")`'s resolution table.

Guidance only — never auto-invokes another command. Per `workflows-core:next-phase-offer`.

### Context hygiene

The resume pointer is written in the terminal cost phase (Phase 7), per
`workflows-core:session-hygiene` §1 — and `/create-prd` is outside that
reference's §4 rename-aid set, so it **omits the session-name line**. Not for want of a key:
Phase 0 refuses this run without one. The PM phase is simply short enough that no label is
auto-suggested; name the session manually if useful. Then:

- **Continuing as PM (`/docs-workflows:release-notes <ADDRESS>`)?** → run **`/compact`**.
- **Handing to PA (`/product-workflows:create-ard <PRD>`) or PE (`/product-workflows:epics <PRD>`), even yourself?** → run **`/clear`** for a clean slate.

Guidance only — nothing is auto-run. See `workflows-core:session-hygiene`.

---

## Phase 7 — Session maintenance, feedback & cost

Terminal phase — runs after Phase 6, NEVER interrupts an earlier phase.

**Capture-at-block invariant.** If an EARLIER phase **halts on a plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked), `emit-block` (per `workflows-core:feedback-emission`) at that halt **before** escalating. NEVER `emit-block` for an environment / user halt (missing key, unset `$SPECS_PATH`, cancellation) or a work-quality review BLOCK. **The three BRD-route refusals are of that second class, not the first**: `CREATE_PRD_BRD_NOT_SLICED` (structural, step 5a), `CREATE_PRD_BRD_UNALLOCATED` and `CREATE_PRD_BRD_NOT_ELIGIBLE` (slice-only, step 7) each report the state of the operator's own BRD tree, not a capability this plugin lacks, so none of them `emit-block`s. `CREATE_PRD_EPIC_FOLDER` (step 5b) and `CREATE_PRD_NEEDS_KEY` are the same, and so are step 7a's `CREATE_PRD_REGISTER_NOT_ON_MAIN` and `CREATE_PRD_REGISTER_NOT_HANDED_OFF`, which report where the operator's register sits in git, and Phase 1 step 2's `CREATE_PRD_PRIOR_UNREADABLE` and Phase 3's `CREATE_PRD_ARCHIVE_FAILED`, which report a file or directory the operator's environment will not let this run read or write. **A halt on a missing container tool always fires it:** a halt because the container lacks a tool the run needs is a container defect rather than an environment or user halt, so `emit-block` records it with `category: environment-defect` (`workflows-core:feedback-emission`'s `emit-block` predicate).

**Session-hygiene invariant.** End Phase 6 with a `### Context hygiene` block per
`workflows-core:session-hygiene` — prepare-first (the
`resume.md` write runs later, in the terminal cost phase, per
`workflows-core:session-hygiene` §1 — this block prints the
guidance only),
then a span suggestion (PM continue → `/compact`; PA/PE handoff → `/clear`). No `/rename`
label — not for want of a key, since Phase 0 refuses this run without one, but because the
PM phase is short (`workflows-core:session-hygiene` §4). Guidance only, never auto-run.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 2's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<detection_model — §2.1 Sonnet chain>`) with a compact handoff: command `/create-prd`; what was authored (PRD + profile); key events (source-ladder friction, unresolved clarifications, BLOCK reviews — or 'none'); workarounds; the `prd-reviewer` verdict; test result N/A; project root = the feature folder.
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6) with the Lessons Learned report, `command: /create-prd`, the run's `key` — which on the BRD route is the `<SLICE-KEY>`, matching this PRD's own `$SPECS_PATH` folder, so the write stays on that reference's primary tier instead of dropping to the unfiled one — `source`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). Surface the persisted path (or "no plugin-facing signal — nothing persisted").
3. **Session cost (ALWAYS runs).** **Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way. Otherwise, invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call its `emit-cost` entry point with `command: /create-prd`, `phase: prd-creation`, `role: pm`, the run's `key` — on the BRD route the `<SLICE-KEY>`, for the reason step 2 gives, which is also the value this run writes as the PRD's `brd_key` (`workflows-core:prd-format`: `brd_key` names the slice the PRD was authored from, `brd_parent` its parent), so the two never disagree — `source`, and `plugin_version`. Surface the persisted path (or the report-only notice).
4. **Write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite `<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above, so the pointer reflects the completed run, and before the commit step below, so it is included in it. Redact per §1. Silent; the printed `### Context hygiene` guidance already appeared in the report.
5. **Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session artifacts (/create-prd)` — or `NOISSUE …` when the run resolved no key at all — with no `Co-Authored-By` trailer. **On the BRD route that `<KEY>` is the `<SLICE-KEY>`, not `NOISSUE`**: this is a specs-repo commit-message prefix, not a tracker lookup, and the slice key is the key this run resolved, the `key` the PRD it wrote carries, and the name of the folder the staged artifacts sit in. It pushes to the branch this run's handoff phase created (§4.1). It NEVER touches anything outside `$SPECS_PATH`; NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0), re-emitting that notice. Hold its §6 outcome line for the Final report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (git for the deliverable is offered only in Phase 5; the terminal step above commits only the bounded session-artifact paths in `$SPECS_PATH`), and NEVER writes into a code/docs repo or the current working directory, where it is not the specs repository; no user name is ever written.

---

## Final report

Report: the PRD path + profile; the archived snapshot path where the pre-write archive (Phase 3) wrote one; US/AC/SM counts + which adapt-in clusters were included; open-question count; the `prd-reviewer` verdict; the prose style-check outcome (`OK` | `N fixed, M remaining`); the `Phase handoff:` outcome line from `handoff-to-main` (`workflows-core:phase-handoff` §4.1); the handoff reminder; resolved model routing (+ any Opus degradation, or `Model routing: bypassed — enforced <id> (flag|env)` in its place wherever `run_flags.enforced_model` is set, per `workflows-core:model-routing/classification` §10); the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); the feedback path (or, under `--skip-feedback`, the `Session feedback: …` line) + cost path (or, under `--skip-costs`, the `Session cost: …` line); the `Specs repo:` outcome line from `commit-artifacts` (`workflows-core:specs-repo-git` §6), with any guard notice repeated in full; and the next-step recommendations.

**On the BRD route, additionally:** the `<SLICE-KEY>` seeded from and its resolved folder; which of
`prd-seed.md` and `decisions.md` were present; the frontmatter `brd_key` / `brd_parent` /
`depends_on` as written — `brd_parent` is present on every run of this route, since the route
resolves a slice and a slice always has a `parent:` (naming `depends_on` if omitted, and why); how many of the gate-set ledger rows
(Phase 0 step 7) are `covered-here`, read from `coverage-ledger.md` — **not** as a `ledger:` line, which this command
neither parses nor prints (Phase 0 step 7); every `[VD#n]`/`[CD#n]`/`[AS#n]` carried in as a gap
rather than an input, by id and status; every contradiction Phase 3 recorded rather than decided,
with the reopening route named for each; **every `[AS#n]` this run wrote for a customer-authority
gap**, by id and statement, each followed by the two runs that carry it to the customer
(`/product-workflows:brd-package <SLICE-KEY>`, then `/product-workflows:brd-reconcile <SLICE-KEY>
@<review-file>`) — or an explicit "none", so a run that surfaced no such gap reads as triaged rather
than as having skipped the triage; every other surviving gap with the route its authority test named; every product-altitude item still `consumed_by: none`, by
id, per the design's *Consumption tracking* section (§7.3) — **the set here is `decisions.md`'s records and nothing else**, because Phase 2 reads exactly `prd-seed.md` and `decisions.md` and no `grounding/` file, so no `[CG#n]`/`[DG#n]` is in it and neither finding exclusion the architecture and implementation altitudes apply has a subject at this one: not the baseline findings, and not the findings a re-cut leaves behind on a slice whose own `coverage-ledger.md` now shows their `[BR#n]` as `covered-by` (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §3.1, §3.2) — say that, so an empty list reads as an empty set rather than as an unrun check; a decision this slice took about a row it has since given up is **not** excluded either, because it records this slice's own refusal to build it, which the re-cut leaves standing (§3.2), so it is reported like any other; and any sub-product-altitude content the
grill surfaced and left for `/product-workflows:create-ard` or `/product-workflows:specify` instead of the
PRD (D4) — naming the command, never a seed file, since the register those runs will read that
content out of is the one this run already read.
All three the BRD route refusals are Phase 0 stops and never reach this report.

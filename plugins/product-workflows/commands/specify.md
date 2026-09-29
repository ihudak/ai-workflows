---
name: specify
description: Specification-authoring workflow (PE phase). Reads the resolved PRD or Epic folder, lightly grounds in code, and authors an org-standard specification.md through a relentless one-question-at-a-time grill; gates on the Opus spec-reviewer and lands the spec on the specs repo's main branch via branch + PR for the /design dev take-over. the BRD route seeds the run from a decided BRD slice instead of a resolved folder: it resolves the BRD-route PRD- slice folder (the folder carrying brd-link.md) and refuses a BRD- container outright, since a BRD is a container and holds no specification; it reads that slice folder's implementation-altitude spec-seed.md, the implementation decisions in decisions.md, the verified [CG#n]/[DG#n] findings and the derivation matrix /prd-ground appended to code-grounding.md, gates decisions.md on the specs default branch before reading it (an unmerged register stops the run), runs the same PRD gate and the same folder read as the idea route, freezes every [VD#n]/[CD#n] against the grill, and marks each consumed item consumed_by: specification.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill WebFetch
---

Author a product specification for the resolved item: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/specify` is the **PE-phase specification-authoring** workflow — the specification step of the PM→PA→PE→Dev pipeline
(`/specify` → `specification.md`; then `/design` → `design.md`). Given an Epic or PRD address,
it reads the item from the specs tree, lightly scans code to
ground feasibility, and authors an org-standard `specification.md` through a relentless
one-question-at-a-time grill — resolving open questions live instead of stopping. It gates on the
Opus `spec-reviewer` and offers to land the spec on the specs repo's main branch (via branch + PR) as
`Published: no`.

Key distinction from `/epics`: `/epics` *splits* a PRD into Epic drafts; `/specify` *authors one
specification* for a single item (typically an Epic). Run `/epics` first, then `/specify` per Epic.

Usage: `/specify <ADDRESS> [--no-docs] [--docs <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`, where `<ADDRESS>` is a key or an `@<path>`. `--docs <path>` — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`; **strip the flag and its value together** before any remaining-argument classification, or the path is read as part of the address. Declared for every consumer by `workflows-core:docs-grounding` *Procedure* step 1 (*Flags first*), which resolves it; this command only has to recognise it and pass the invocation through. On the BRD
route the run is seeded from a decided BRD slice and the address is the **`PRD-` slice key**
`/brd-split` carved; a `BRD-` container is refused (Phase 0 step 0). One address on every route: a
second positional token is refused (Phase 0 step 1, `SPECIFY_ONE_ADDRESS`).

---

## Phase 0 — Resolve input

0. **The route is a property of the resolved folder, not of a flag.**

   **One resolution serves both routes now.** A BRD key and a PRD key both name a folder under
   `$SPECS_PATH/specifications/`, and `resolve-address` resolves either — so this step no longer
   skips a front-end, it reads a different `kind` from the same resolution. What distinguishes the
   routes is what `prd_dir` (step 1) holds, not how it was addressed. **The BRD route is a `PRD-`
   folder carrying a `brd-link.md`** — the slice `/brd-split` carved, or a legacy slice with no
   prefix, which step 1 places as a `PRD-` folder by that same `brd-link.md` — **or an `EPIC-` folder
   inside one**, which carries no `brd-link.md` of its own and is on the BRD route by the slice it
   sits in (step 3's *Look one level up*), and nothing else.

   **A `BRD-` container is refused, on either route.** Take this on the folder **step 1 resolves**,
   the moment that resolution returns `status: found` and the specs-repo preflight it is followed by
   has run, and ahead of every other read this command makes —
   and **not** as part of the BRD-route branch. The BRD route is detected from a `brd-link.md`, and a
   root BRD folder need not carry one: `/brd-intake` writes none, and no command writes one into a
   root — `/brd-split` places one in each slice it carves, and every command that merges
   `depends-on:` into one refuses a root. A refusal conditioned on the detected route would let
   `/specify <ROOT-BRD-KEY>` fall through to the keyed route and author a specification into the
   container. A BRD is a container: its requirements are built by the `PRD-`
   slices under it, one specification each, and a `specification.md` written into the container
   would sit beside `brd/`, `coverage-ledger.md` and `slices.md` in a folder the
   design's §4.1 tree gives no specification. **The test is the directory prefix, and never the
   folder's asserted `kind:`** — `/brd-split` writes `kind: brd` into the `brd-link.md` inside a
   `PRD-` slice folder, so a slice asserts `brd` while being exactly the folder a specification
   belongs in, and a gate on the asserted kind would refuse every slice.

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
   `SPECIFY_BRD_NOT_SLICED: <BRD-KEY> resolves to a BRD- container at <path>, and a BRD is never the folder a specification is authored in — its requirements are specified in the PRD- slices under it, one specification each (coverage-ledger-format.md §5). <the remedy, per the branch below>`

   **The remedy is the same two branches `/product-workflows:create-prd`'s own container refusal takes,
   and it is a directory listing rather than a ledger read** — this remedy opens no coverage ledger
   and does not start now. Enumerate slices by `/brd-split` Phase 0 step 9's **positive test**: an
   immediate subdirectory carrying a `brd-link.md` whose `parent:` names this BRD.
   - **One or more slices** — the ordinary shape, since a split always confirms at least one. Name
     every slice and offer `/product-workflows:specify <SLICE-KEY>` once per slice. Do **not** name
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

1. **Resolve the address.**

   **Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves.

   **Strip recognised flags before anything counts positional tokens.** `--no-docs` (boolean) and
   `--docs <path>` (which consumes the token after it) are removed from `$ARGUMENTS` first, together
   with `--docs`'s value; what remains is the positional address, and the one-address refusal below
   applies to that remainder alone. **Without this rung the flags this command documents do not
   work** — a flag is a token, so `--no-docs` reaches the refusal as a second positional and stops
   the run, and `--docs <path>` supplies two. That was the live state: both were named in the Usage
   line and neither was ever parsed.

   Parse the **single positional address** from what remains — a `<KEY>`,
   or an `@<path>` naming a folder or a file inside one — and resolve it with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). Carry forward:
   - `<PRD>` — the resolved **PRD folder's** `key`: the folder itself when the address named a
     `PRD-` folder, its parent when it named an `EPIC-` folder.
   - `<EPIC>` — the `EPIC-` folder's `key`, or `null` when the address named a `PRD-` folder. The
     later phases call it `focus_key` — one value under two names: Phase 2 Step A's picker may set
     it on a `PRD-` address, and every later step tests it as *set* or *null*.

   **Carry `prd_dir` — the PRD folder — beside the resolved folder, because on an Epic address they
   are two different folders.** `prd_dir` is the resolved folder itself when the address named a
   `PRD-` folder (the `PRD-` slice on the BRD route), and the folder containing it when the address
   named an `EPIC-` folder — `<PRD>`'s folder, the one step 3 resolves as the PRD dir and the PRD gate
   below tests. It does not move when Phase 2 Step A's picker re-points the feature folder at an Epic,
   because that picker runs only on a `PRD-` address, where `prd_dir` already is the PRD folder.
   **Every `grounding/` read, seed, stamp, staged path and report in this command names `prd_dir`,
   never the resolved folder**, and so does every read of the slice's `decisions.md`, `spec-seed.md`,
   `brd-link.md` and `grounding/baselines.md` on the BRD route: `/product-workflows:prd-ground`
   grounds at PRD altitude and refuses an `EPIC-` folder (`PRD_GROUND_EPIC_LEVEL`), and `/brd-split`
   writes `brd-link.md` into the slice and nowhere below it, so an `EPIC-` folder holds none of these
   of its own — a test on the resolved folder would find none on every run addressed at an Epic,
   reading, seeding from and stamping none of the findings the PRD folder above it carries.
   `/product-workflows:create-ard` carries the same `prd_dir` for the same reason.

   A folder with no prefix — one §5's legacy fallback resolved, or an unprefixed folder an `@<path>`
   names; a name is prefixed only where it begins `<KIND>-<the resolved key>-`, so a legacy key
   beginning with a kind token is no prefix — is placed as `workflows-core:addressing` §4.1 places
   it, by positive evidence: a resolved `kind: epic` counts as an `EPIC-` folder here; a resolved
   `kind: prd`, or a `brd-link.md` naming a `parent:`, as a `PRD-` folder. A legacy root container is
   step 0's to refuse, on §4.1's container test, and a folder none of these places is not guessed at
   — stop, naming the folder and what it carries — and, where it holds an `idea.md` and no `prd.md`, name `/product-workflows:create-prd <KEY>` too, whose `prd.md` places it (`workflows-core:addressing` §4.1).

   **A second positional token is refused, on every route** (D4). There is no `<PRD> <Epic>` form to
   fall back to: an Epic key encodes its own ancestry, so a second argument would be derivable from
   the first and able to disagree with it, which is the failure class D4 exists to remove. This
   refusal is **not** conditioned on the route — the earlier BRD-route-only version of it argued
   that "a BRD has no Epics yet — they are minted from the PRD", a premise `/epics` has since
   changed: Epics are minted by `/epics` under a PRD folder, a slice **is** a PRD folder, so a
   reconciled slice can hold `EPIC-` folders and the old sentence was false there as well as
   redundant everywhere else. Stop gracefully:
   `SPECIFY_ONE_ADDRESS: /specify takes one address; <second-token> was given as a second. The folder the address resolves to sets the altitude by its prefix — an EPIC- folder specifies that Epic, with its PRD read from the folder above it; a PRD- folder authors a PRD-level specification; a legacy folder with no prefix is placed by what it holds; on the BRD route the address is the PRD- slice folder /brd-split carved. To specify one Epic, address the Epic: '/product-workflows:specify <EPIC-KEY>'.`

   **The folder's prefix decides the altitude — never the kind it asserts, which on a slice is
   `brd`** — and that is what replaces the two-key grammar: the second key was always derivable from
   the first, and `workflows-core:addressing` §4's `key` is what supplies both.

   With no positional address, stop with
   `SPECIFY_NEEDS_KEY: /specify needs a PRD or Epic address — a key, or an @<path> to its folder.` — `/specify` has no
   direct-prompt behavior.

**Resolve the address only after `$SPECS_PATH` is settled.** `resolve-key` globs under it, so a
resolution taken first returns `absent` whenever the variable is unset — and this command resolves
**once**, so that stale `absent` survives the operator supplying the path at the next step and the run
stops with `SPECIFY_BRD_NOT_FOUND` naming a folder that exists. `/create-ard` and `/create-prd` state
the same ordering for the same reason.

**Then, where the resolution returns `status: found`, settle the specs checkout before step 0's
refusal or step 1's placement reads the folder.** Fix the run key set
(`workflows-core:specs-repo-git` §3.2), reading only carrier frontmatter (`key:`, `kind:`) as
`workflows-core:addressing` §4 does, whatever file that is, and testing no file's presence: the
resolved `key` and, where §4.1 places the resolved folder at Epic level — an `EPIC-` prefix, or with
no prefix a resolved `kind: epic` — also the key its parent's carrier asserts (§4), the would-be
`<PRD>`. Then run the specs-repo preflight below, and only then take step 0's refusal, step 1's
placement and every later read. A stale plugin branch the preflight switches away from would
otherwise hide a slice's `brd-link.md` from step 0's listing, or the file that places the folder or
detects the route, and the run would list the wrong slices or stop where it would have proceeded.
`absent` runs no preflight at all: step 3 stops it with `SPECIFY_BRD_NOT_FOUND`, which reads
nothing.

2. **Resolve `$SPECS_PATH`.** `/specify` writes specifications under `$SPECS_PATH/specifications/`
   (exact layout resolved in step 3) — the specs repo. If `$SPECS_PATH` is unset, stop
   with a clear error naming `SPECS_PATH` (`choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`) —
   there is no fallback for this write target the way there is for reads.

3. **Resolve the feature folder.** Derive provisional kebab-case slugs from the relevant
   item title(s) (finalized once the folder read runs in Phase 2, but a
   provisional slug is enough to check for existing folders now): `<vslug>` for the `<PRD>` title, and
   `<eslug>` for the `<EPIC>` title when `focus_key` is set.

   - **Resolve/derive the PRD (top-level) dir:** call `resolve-address <PRD>` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), which searches every level §3 bounds and
     carries §5's legacy fallback — including a slug a human has adjusted. No matching rule is
     written here; §5 owns it. **`status: absent` is a stop, not a folder to create** — this command
     creates no folder in the specs tree, on either route, and the stop it takes is the one written
     out below. `/specify` specifies a PRD that exists; a PRD folder that does not exist holds no
     `prd.md` for Phase 2 to read and no artifact for the PRD gate to find, so authoring into a
     freshly-minted one would write a specification against nothing. Every later
     `specifications/<PRD>-<vslug>/` in this command — the PRD gate's `ls-tree` path and Phase 2's
     per-Epic paths included — names the dir resolved here.
   - **Resolve the feature folder itself**, by case. **There are two cases, not three**: an Epic
     always has a PRD above it, because `/product-workflows:epics` is the only command that creates an
     `EPIC-` folder and it writes every one of them under a PRD folder (D6). A top-level `EPIC-`
     folder with no PRD above it — the third case this step used to carry — is retired: `/product-workflows:epics`
     refuses one rather than partitioning it, and this command refuses one rather than authoring a
     specification flat inside it.
     - `focus_key` set (an Epic nested under a PRD) →
       `specifications/<PRD>-<vslug>/EPIC-<EPIC>-<eslug>/` — a per-Epic subfolder under the PRD dir
       (`<eslug>` = kebab of the Epic title). Apply the same honor-an-existing-dir tolerance to the
       `EPIC-<EPIC>-<eslug>` segment. **This folder is never created here.** An `EPIC-` folder is
       minted by `/product-workflows:epics` and by nothing else, so one that does not exist is a stop,
       not a directory to make:
       `SPECIFY_EPIC_NOT_FOUND: no Epic folder for <EPIC> under <the resolved PRD dir> — an EPIC- folder is created by /product-workflows:epics and by no other command. Run '/product-workflows:epics <PRD>' to draft this PRD's Epics, then re-run '/product-workflows:specify <EPIC>'.`
       That remedy runs in the state this stop reports: `/product-workflows:epics` takes the PRD address
       this step already resolved, and gates only `<PRD-dir>/specification.md` — a file this run has
       not written.
     - `focus_key` null → the item is a **PRD** for which the broad-PRD-spec choice is made
       (Phase 2, Step A) → `specifications/<PRD>-<vslug>/specification.md` — flat at the PRD-dir level, no
       per-Epic subfolder; the feature folder is the PRD dir itself. **This is now the only
       null-`focus_key` case**, so `<PRD>` is always a PRD's own key and never an Epic's.
   - All delimiters this step writes are hyphens; matching an existing dir tolerates a stray `-`/`_`.
     The PRD dir is not created here **and not by a later phase either**: on `status: absent` this
     step stops, so every phase that writes — Phase 2's `idea.md` write included — runs against a
     folder that already existed when the address was resolved. The per-Epic feature folder is
     likewise never created, by the `SPECIFY_EPIC_NOT_FOUND` stop above.

   **On the BRD route the feature folder is the resolved `PRD-` slice folder**, and it is never
   created here. There is no second resolution for that route and no `<BRD-dir>` argument to read:
   the single positional address was resolved once with `resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), step 0 refused the container the upper
   level holds, and the folder that survives both **is** the slice.
   **The write location then follows `focus_key`, by the same two cases as above and not by a rule of its
   own.** A slice is a `PRD-` folder, so `focus_key` is null when the run starts and `specification.md`
   is written flat inside the slice folder, beside the BRD artifacts it was derived from — the ordinary
   shape, and the identical `focus_key`-null PRD case listed above. It is not flat *because* this is the
   BRD route: where `/product-workflows:epics` has minted `EPIC-` folders under the slice, Phase 2 Step A's
   picker can set `focus_key` to one of them here exactly as it does under any other PRD folder, and the
   feature folder is then re-pointed to that Epic's subfolder (Step A's *Re-pointing*). Addressing such an
   Epic directly — `/product-workflows:specify <EPIC-KEY>` — resolves an `EPIC-` folder, which carries no
   `brd-link.md` of its own. **Look one level up before concluding this is not the BRD route.** Where the
   `EPIC-` folder's containing directory is a `PRD-` slice carrying `brd-link.md`, this run **is** on the
   BRD route, with that slice as the BRD folder and this Epic as the focus — read `decisions.md`, the
   grounding files and the derivation matrix from the slice exactly as the picker path does, apply the
   freeze rule, and write `consumed_by: specification` back there.

   **Deciding it on the resolved folder alone was a silent contract loss, and the plugin recommends the
   address that triggered it.** `/epics` ends by offering `/product-workflows:specify <EPIC>`; taken on a
   slice-derived Epic, that run skipped the whole BRD-route block — the implementation-altitude `[VD#n]`
   and `[CD#n]` the customer signed did not constrain the spec, the freeze rule did not apply, and every
   one of those decisions stayed `consumed_by: none` forever. The same Epic reached through
   `/specify <SLICE-KEY>` and the picker kept all of it. `workflows-core:prd-format` forbids implementation detail in
   the PRD, so the parent `prd.md` carries none of it and nothing else recovers the loss.
   `absent` is a graceful stop, not a folder to create — the same stop the PRD-dir bullet of step 3
   takes, and **one stop for both routes**, since a folder that resolved to nothing carries no
   `brd-link.md` to say which route it would have been on. Its code keeps the `_BRD_` segment it was
   minted with; what it must not keep is a remedy list that only fits one route, so it names every
   command that creates a folder this one accepts, the same three `/dev-workflows:ready`,
   `/docs-workflows:release-notes`, `/product-workflows:epics` and `/product-workflows:create-ard` each name
   in their own `absent` stops — and step 0 refuses the `BRD-` container a `/product-workflows:brd-intake` run
   would leave behind:
   `SPECIFY_BRD_NOT_FOUND: no folder found for <ADDRESS> under $SPECS_PATH/specifications/ (every level addressing.md §3 bounds, plus §5's legacy fallback) — check the address. /specify specifies an existing PRD or Epic folder and creates neither. A PRD- folder is created by /product-workflows:idea <KEY> or /product-workflows:create-prd <KEY> on the idea route, and by /product-workflows:brd-split on its parent BRD on the BRD route — /specify writes into that folder, never into the BRD- container above it, and a parent BRD is created by /product-workflows:brd-intake <BRD-KEY> @<brd-file> and then split before any slice exists — each slice is ground after it is carved. An EPIC- folder is created by /product-workflows:epics <PRD-ADDRESS> and by no other command.`
   Where the address was an **`@<path>`** the same stop substitutes that path for the search clause —
   `no folder at <path> (given as a path)` — because "every level addressing.md §3 bounds" would
   describe a search a verbatim path never performs.

4. **Detect a prior run.** If a `_session.md` exists in the resolved feature folder, record that a
   resume is available — Phase 1 asks the user resume-vs-fresh. If no `_session.md` exists, this is a
   fresh run.

`/specify` is **cwd-agnostic**, like `/epics` — it reads the specs tree and writes specs to
an absolute `$SPECS_PATH`-rooted directory, so it does not require cwd to be inside either.

**Specs-repo preflight** — run once step 1's resolution returns `status: found`, with the run key
set fixed in the paragraph after step 1, before step 0's refusal, step 1's placement or any later step reads the
folder. Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier
run, retry an artifact commit that failed to push, and settle the branch. Prompt-free and silent
when the specs repo is clean and on its default branch. If a guard fires, emit its §5 notice; if
it returns `specs_git: blocked` (§3.3 G0), carry that flag for the whole run — the terminal
`commit-artifacts` step skips on it.

**Gate the PRD — on every route, with no branch.** The folder gated is **the PRD folder this run resolved**: the resolved folder itself when the address named a `PRD-` folder, its parent when the address named an `EPIC-` folder, and — on the BRD route — the resolved `PRD-` slice folder, which *is* that route's PRD folder (§4.1). One rule, one path expression, no route test. Execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against the PRD file in that folder (written below as `specifications/<PRD>-<vslug>/` for brevity; the folder on disk carries its kind prefix — `PRD-<PRD>-<vslug>/` on a current tree, the unprefixed form only through §5's legacy fallback — and it is always the folder Phase 0 resolved, never a path re-derived here) — that file is `prd.md`, a constant. `/create-prd` and `/update-prd` write no other canonical name — the only other PRD file either writes is the dated copy `/update-prd` archives under `revisions/`, which is no PRD this gate could mean — and `workflows-core:addressing` §5 fixes the boundary: the legacy fallback resolves a folder name and nothing inside it, so a pre-rename tree renames its artifacts rather than being resolved for. **A key-globbed filename was gated here once, and is not restored.** The pre-rename `<KEY>_<slug>.md` form matches nothing in a current repo — so the gate returned `absent` for every PRD that was present and the rows D/E stop could never fire — and on the one tree it was written for it also matches the pre-rename ARD `<KEY>_ARD.md`, so it can gate the wrong artifact entirely. Gating the constant is correct on both trees: on a current one it names the file that is there, and on a pre-rename one it reports `absent`, which is what §5 now tells that operator to fix. Map its §3.7 return value by `stopped` first, never by `on_main` alone. Any stopping state → stop per §4.4. Otherwise (`stopped: false`): on `pass`/`pass_amending`, proceed — Phase 2 still reads the resolved folder exactly as it does without this gate; the merged PRD is a grounding confirmation, not a new content source; on `absent`, `/specify`'s existing specs-tree behaviour is unaffected — but report it: *"No authored PRD on `<default>` for `<PRD>` — specifying from the resolved folder at `<path>`. If a PRD exists on a branch, this run would have stopped; it does not, so none does."*; on `unmanaged`, behave exactly as before this feature — reachable here even after step 2's own `$SPECS_PATH` check, since that check only rejects an unset value, never an invalid path or a non-git directory.

**The BRD route runs this gate too, and the `absent` branch is what makes that safe.** It did not, and
the rationale it carried was coherent while the route could resolve a `BRD-` container: the PRD "may not
exist at all", and gating an artifact the run does not read would promote an input the route never had
into a prerequisite, which `workflows-core:phase-handoff` §5 rule 3 forbids. Phase 0
step 0 removed the premise. The BRD route now resolves **a `PRD-` slice folder in every case** — the same
kind of folder the keyed route resolves — so there is one folder to gate, and the gate's own `absent`
branch already handles the state the rationale was protecting: a slice in which no `prd.md` has been
authored yet returns `absent`, is **reported**, and this run specifies from the resolved folder exactly as
§3.4's `/specify` row says it may. Nothing is promoted into a prerequisite, because `absent` is not a stop
— `/product-workflows:create-prd` is still not a prerequisite for this command, on either route. What the gate
adds on both routes is the state it was built for: a `prd.md` that **exists and was never handed off**,
sitting on a branch (rows D/E). That state is as reachable on a slice as it is on a keyed PRD folder —
`/product-workflows:create-prd` opens `prd/<SLICE-KEY>-<slug>` there and its handoff can be declined — and
specifying against an unmerged PRD is the failure the gate exists to prevent, whichever route wrote it.
§3.4's `/specify` row therefore describes every run of this command, not one route's.

**Gate the decision register — on the BRD route, right after the PRD gate.** Wherever the PRD folder
that gate just tested carries a `brd-link.md` — the resolved slice when the address named it, and the
slice an addressed Epic sits in otherwise, which is the folder Phase 2's BRD-route read takes the
register from on the picker path and the Epic path alike — execute `require-on-main` (§3) against that
folder's `decisions.md` too. Phase 2 freezes every `[VD#n]` and `[CD#n]` in it against this run's grill,
so it is read only once it is on the specs repo's default branch. Map the §3.7 return by `stopped` first:
- **Any stopping row** → stop per §4.4, as `SPECIFY_REGISTER_NOT_ON_MAIN` below.
- **`pass`** → proceed; **`pass_amending`** → proceed, printing the §3.3 row-B message;
  **`unmanaged`** → proceed as before this gate existed.
- **`absent` (row F)** → split it on a test row F cannot make — is the file in the folder at all:
  - **No `decisions.md` in the folder** → exactly as before this gate: Phase 2 reports the register
    absent and carries what the folder holds. Nothing becomes a prerequisite (§5 rule 3).
  - **A `decisions.md` in the folder, and on no ref** — the run that wrote it had its handoff
    declined — → stop, as `SPECIFY_REGISTER_NOT_HANDED_OFF` below.

Both stops carry §4.4's four parts, in order:
```
SPECIFY_REGISTER_NOT_ON_MAIN: <SLICE-KEY>'s decision register <path> is <the state require-on-main reported — on branch <branch> with PR #<n> open, not merged | on branch <branch> and never handed off | changed in the working tree against <default> (<files>) | any other stopping row, as §3.3 words it>. This run read none of it and wrote nothing: a specification frozen against [VD#n]/[CD#n] records that are not on <default> would rest on decisions nobody merged. <the resolving commands §4.4 prescribes for that row, $SPECS_PATH substituted — merge PR #<n>, open one for <branch>, or commit, stash or discard the working-tree edit>, then re-run '/product-workflows:specify <ADDRESS>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
```
```
SPECIFY_REGISTER_NOT_HANDED_OFF: <SLICE-KEY>'s decision register is written at <path> but is on no branch — the run that wrote it had its handoff declined. This run read none of it and wrote nothing. Commit and merge decisions.md to the specs repo's default branch (git -C "<SPECS_PATH>" add, commit and push it, then open and merge its pull request), then re-run '/product-workflows:specify <ADDRESS>'. Ignored, every /create-prd, /create-ard and /specify run on this slice stops here the same way.
```
Neither is a plugin gap, so neither `emit-block`s.

**Why the register is gated and the seed, the grounding files and the derivation matrix are not.** This
paragraph once said the `/brd-*` family's own handoff discipline puts `spec-seed.md`, `decisions.md`, the
grounding files and the derivation matrix on the default branch before this route reads them — each of
those commands landing its deliverable there and the next refusing to start until it is — and gated no
BRD artifact on that ground. For the register it was false at the last hop:
`/product-workflows:brd-package` gates it, but `/product-workflows:brd-reconcile`, which freezes `[CD#n]`
into it, and `/product-workflows:create-prd` and `/product-workflows:create-ard`, which add `[AS#n]` and
consumption stamps to it, were followed, on the path that advances the slice, by no route command that
gated it — `/brd-package` is reached again only when the slice goes back through the route — a question still held for the customer, a reopened decision's new round, or a re-grounded claim — and not on the path that advances it — so a declined handoff of any of them left a register this route read from a working tree. The gate above is what makes the claim true
for the register now: this command refuses to start until the register is on the default branch. The
grounding files — the derivation matrix inside `grounding/code-grounding.md` with them — are not
re-gated here, and the reason is not that something upstream always gates them:
`/product-workflows:brd-split` (allocate-only) and `/product-workflows:brd-interview` each gate
`grounding/code-grounding.md`, and `/brd-split` `grounding/design-grounding.md` where frame sets exist,
but a later `/product-workflows:prd-ground` run rewrites both — the `--rebaseline` pass
`/product-workflows:brd-reconcile` sends a challenged code claim to, or any run on an idea-route folder
— with no command gating them between it and this one, so a declined handoff of that run leaves them
unmerged. This command re-gates neither because grounding is optional to it and read as evidence, never
frozen: a finding counts for what its verifier outcome says, and a findings file a later `/prd-ground`
run left unmerged is read as the working tree holds it — Phase 2's grounding subsection has the run
report one it finds uncommitted. It reads them wherever `prd_dir` holds them, on either route, as that
subsection says.
`spec-seed.md` is gated by nothing: its one writer is the `/brd-intake --sort-existing` migration, it is
read as context rather than frozen, and its absence is the ordinary case. The PRD is gated above on
every route.

---

## Phase 1 — Configure

**Rule: Ask, don't guess. This rule is absolute.**

Use `choices` arrays; 2–4 options, and never author an "Other" option — the harness supplies the free-text escape itself (`Skill(skill: "workflows-core:reference", args: "escalation-rules")` §0).

1. **Feature folder.** Confirm the path resolved in Phase 0:
   ```
   choices: ["Use <feature_folder> (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]
   ```
   - **Resolve documentation grounding here, then show its line.** Run `resolve-docs-grounding specify` per `Skill(skill: "workflows-core:reference", args: "docs-grounding resolve-docs-grounding")` — its step 3.5 index prompt included — and show the `docs grounding:` line from what it returns, in the form that reference fixes — `ON <root> (retrieval: …)` or `OFF (<reason>)` — verbatim, including any index-build, staleness, or shadowing clause it carries (off switch: --no-docs). It runs here, before any agent is dispatched, because step 3.5 asks its one-time index question before the run's real work; this is the run's one resolution (`workflows-core:docs-grounding`, *Invariants*), and Phase 4 dispatches on the state it returns without resolving again.

2. **Resume vs fresh** (only if Phase 0 found a `_session.md`). Read it back and summarise which
   stages/questions are already settled:
   ```
   choices: ["Resume — skip settled stages/questions (Recommended)", "Start fresh — discard the prior session", "Cancel"]
   ```
   On resume, Phase 5 begins at the first unsettled stage instead of the header.

3. **Repo refresh policy** (governs Phase 4's `code-scanner` dispatches):
   ```
   choices: ["fetch + pull default branch (Recommended)", "fetch only", "no refresh"]
   ```
   `fetch + pull default branch` matches `code-scanner`'s own default
   (`refresh.switch_to_default_branch: true, refresh.pull: true`) — grounding wants present-day code,
   the same rationale `/epics` uses.

4. **Repos search base (`$REPOS_PATH`)**. Read `${REPOS_PATH:-/workspace}`. `$REPOS_PATH` may be a
   single directory or a colon-separated list:
   ```
   choices: ["Use $REPOS_PATH (default /workspace) (Recommended)", "Use a different path (you'll be prompted)", "Cancel"]
   ```
   If "different path", validate that at least one directory exists under the given value before
   recording it.

Also display (for user context): resolved feature folder; resolved `prd_dir`; resolved
`key` (PRD); resolved `focus_key` (Epic, or 'none — PRD-level'); resolved `$REPOS_PATH`; resolved
`$SPECS_PATH`.

**Wherever `prd_dir` holds `grounding/`, on either route, display in addition** which of
`<prd_dir>/grounding/code-grounding.md` and `<prd_dir>/grounding/design-grounding.md` are present — a stat, not a read; the
read is Phase 2.

**On the BRD route, display in addition** a `from BRD:` line naming `<SLICE-KEY>` and its resolved folder,
its `parent:` if `brd-link.md` records one, its `depends-on:` if any, and which of `spec-seed.md` and
`decisions.md` are present — also a stat. **Display the `prd_dir`, `key` and `focus_key` lines as well**,
which resolve on this route exactly as on the keyed one: `prd_dir` is the slice folder itself (a slice
*is* the PRD folder), `key` is the slice's own asserted `key`, and `focus_key` is `none — PRD-level`
until Phase 2 Step A settles it. They were once shown as `none — seeded from a BRD`; that described a
route that resolved a container and had no PRD folder to name, which Phase 0 step 0 has retired.

---

## Phase 1.5 — Classify

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then classify as `SIMPLE` / `MODERATE` / `SIGNIFICANT` / `HIGH-RISK`. Specification authoring is typically **MODERATE**. Resolve per-step routing per `workflows-core:model-routing/classification` §9:

```yaml
model_routing:
  classification: MODERATE        # typical; SIGNIFICANT possible for large/cross-cutting PRDs
  reason: <one-line>
  current_model: <the model this orchestrator/grill is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # the folder read, code-scanner
  review_model:    <§2 Opus chain>     # spec-reviewer (frontmatter-pinned; recorded, no override unless §10 enforces a model)
  authoring_model: <= current_model>   # the interactive grill + specification.md authoring (session model, not a delegated subagent)
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2/§2.1 fallback or degradation>
```

The grill + authoring run inline on `current_model` (interactive judgment — not a delegated subagent), consistent with the model-routing SSOT. If no Opus is available, `spec-reviewer` falls to the Sonnet floor — record the degradation in `notes` and the final report. Under `run_flags.enforced_model` (`workflows-core:model-routing/classification` §10) the enforced model is used instead and no degradation is recorded.

---

## Phase 2 — Read the resolved folder

**Steps A and B run on every route.** Phase 0 step 0 means the BRD route resolves a `PRD-` slice
folder — a PRD folder, which can hold a `prd.md` and can hold `EPIC-` folders that `/product-workflows:epics`
minted under it — so there is nothing for a route test to decide here. The *BRD route — read the
implementation-altitude seed* section at the end of this phase is an **addition** to Steps A and B, not a
replacement for them: it reads the seed, the register, the verified findings and the derivation matrix a
slice carries and a keyed-route PRD folder does not.

**One divergence stays, and it is a real one: no `idea.md` is written on the BRD route.** Step B's
`idea.md` write records pre-spec provenance for an item whose provenance is otherwise unrecorded. A slice
folder already carries its provenance in the tree — `brd-link.md`, the register, the grounding findings,
and the customer's own document under the parent's `brd/source/` — and writing a fourth, derived account
of it beside those would put an unreviewed restatement of a signed-off document in the folder. So the
`idea.md` bullet in Step B is skipped on the BRD route and the run says so; every other part of Steps A
and B runs unchanged.

Phase 2 reads the folder in **two steps, cheap before expensive**. Step A settles *granularity* — the
input's type and, for a multi-Epic PRD, *which* Epic — with a cheap `prd-plus-epics` read (and, when
needed, the progress-aware picker), resolving `focus_key`. Only then does Step B spend the full-depth
read, now scoped to the resolved Epic. This ordering resolves a null `focus_key` by a cheap
enumeration **before** any expensive full read, so the full read never pulls a whole multi-Epic PRD
subtree the grill would only discard. When `focus_key` is already set on entry, Step A is skipped and
Phase 2 is just the full read (Step B).

### Step A — Resolve granularity + focus Epic (cheap enumeration + picker)

**Skip this step entirely when `focus_key` is already set on entry** — that is, when step 1's single
address resolved to an `EPIC-` folder (or to an `@<path>` naming one), and the PRD was read from the
folder above it. The Epic is already chosen, so go straight to Step B. There is no two-token form
that could set it: `/specify` takes one address (step 1, `SPECIFY_ONE_ADDRESS`).

Otherwise (`focus_key` is null), perform the **cheap** `prd-plus-epics` read — the folder's own `prd.md`
plus a listing of its `EPIC-` subfolders — to determine the item's type and enumerate its child Epics
*without* opening every Epic folder's contents:

**Read the PRD folder directly.** Read its `prd.md`, and list the `EPIC-` subfolders under it —
that listing is the Epic set this phase branches on, and each folder's `key` and title come from its
own frontmatter (`workflows-core:addressing` §4).

**A missing folder and a folder holding no `prd.md` are two different states, and only the first is a
stop.** If the folder is missing, surface the `key dir not found` rule in
`workflows-core:escalation-rules` (`["Re-enter key", "Cancel"]`) — reachable only
through a folder deleted between Phase 0 and here, since Phase 0 step 3 already stopped on `absent`. If
the folder is there but holds **no `prd.md`**, do not stop and do not re-report: the Phase 0 gate has
already returned `absent` and printed the line naming the folder this run specifies from instead. That is
the ordinary state on the BRD route, where `/product-workflows:create-prd` is not a prerequisite for this
command, and a supported one on the keyed route; escalating it here would contradict the gate's own
`absent` branch two steps earlier and offer a "Re-enter key" for a key that resolved correctly. Enumerate
the `EPIC-` subfolders exactly as below and carry on with whatever the folder holds.

Otherwise take the type from the resolved folder's own `prd.md` (`kind: prd`) and enumerate its **child
Epics** as the `EPIC-` subfolders listed above, each one's `key` and title read from its own
frontmatter. `value_increment` and `linked_items` were fields of a tracker export that no command
produces any more; the folder listing is the enumeration now, and it is the same one the paragraph
above performs. Then branch — this is the reusable **progress-aware
Epic-picker pattern** documented in `workflows-core:epic-picker`, applied here with `/specify`'s own done-predicate:

**The item here is always a PRD.** This step runs only when `focus_key` is null on entry, and step 1
sets `focus_key` from an `EPIC-` address — so an Epic never reaches the branch below. The
top-level Epic with no PRD above it, which used to have a branch of its own here, is retired with
the case itself (Phase 0 step 3): `/product-workflows:epics` writes every `EPIC-` folder under a PRD folder, and
is the only command that writes one at all.

- **PRD with exactly 1 Epic** → no picker; auto-select it. Set `focus_key` = that Epic and emit a
  one-line notice (e.g. `Single child Epic <EPIC> '<title>' — authoring its spec.`). Re-point the
  feature folder to that Epic's per-Epic subfolder (see *Re-pointing* below). Proceed to Step B.
- **PRD with ≥2 Epics** → render the **progress-aware picker**, one row per child Epic. For each Epic,
  first resolve its **actual** feature folder the same way Phase 0 step 3 does: look under
  `specifications/<PRD>-<vslug>/` for an existing dir matched by that Epic's key-number (tolerate a
  stray `-`/`_` after the key, and a pre-existing slug that doesn't exactly match a freshly-derived
  one), falling back to the freshly-derived `specifications/<PRD>-<vslug>/EPIC-<EPIC>-<eslug>/` only when no
  such dir exists — this keeps a human-adjusted Epic dir slug from mis-displaying as ○ not-started.
  Compute each Epic's status from `/specify`'s **done-predicate** against that resolved folder:
  - **○ not started** — no `specification.md` and no `_session.md` there → selectable.
  - **◐ in progress** (resume) — a `_session.md` exists there but no `specification.md` → selectable
    as a resume; the per-Epic stage-level resume then runs in Phase 5 from that `_session.md`
    (resume *stacks* on the picker, per the shared pattern).
  - **● done** — `specification.md` exists there → shown greyed, **not** default-selectable;
    selecting it offers *revise*.
  Default cursor = the first actionable row (in-progress before not-started). Render per
  `Skill(skill: "workflows-core:reference", args: "epic-picker")`: every Epic listed as prose above the prompt, and
  the array carrying **at most two** Epic rows (marker + key + title), the explicit
  **"Author one broad PRD-level spec instead"** choice, and *"Another Epic from the list above — name
  its key"*. That file's *The cap* section is why the Epic rows are the ones that give way: the
  broad-spec choice is the alternative to picking any Epic at all, so hiding it would force a choice
  this command means to leave open.
  - On selecting an Epic → set `focus_key` = that Epic; re-point the feature folder to its per-Epic
    subfolder (see *Re-pointing* below).
  - On **"Author one broad PRD-level spec instead"** → leave `focus_key` = null; the feature folder
    stays the flat PRD-dir path `specifications/<PRD>-<vslug>/` (Phase 0 step 3's `focus_key`-null PRD
    case). Step B then reads the whole PRD subtree.
- **PRD with 0 Epics** → this PRD hasn't been split yet. Offer the without-Epics choices:
  `choices: ["Split into Epics first with /product-workflows:epics (Recommended)", "Author one broad PRD-level spec now", "Cancel"]`
  `/specify` does not write Epic folders itself — on "Split…", stop and point at
  `/product-workflows:epics`, which writes them into this PRD folder where this command will see them. On
  "Author one broad PRD-level spec now", leave `focus_key` = null and proceed to Step B.
  - **`/product-workflows:epics` is only offered where the resolved folder holds an authored `prd.md`.**
    That command accepts a folder holding a `prd.md` asserting `kind: prd` and refuses one that does not
    (`commands/epics.md` Phase 0 step 1b, `EPICS_NO_PRD`), so offering it on a folder with no PRD would
    name a run that stops on arrival. Where the folder holds none — the ordinary BRD-route state, and the
    one the Phase 0 gate reported as `absent` — the first choice becomes
    `"Author the PRD first — /product-workflows:create-prd <ADDRESS> (Recommended)"`, which is the run that
    writes the PRD `/epics` then reads and takes the single address this run already resolved.
    **Passing that command's container refusal is not enough to name it**, and it is the only one of
    its three refusals this run has cleared: on the BRD route the resolved folder is a slice with a
    gate set of its own, and a slice that is fully allocated with no `covered-here` row sends this
    choice into `CREATE_PRD_BRD_NOT_ELIGIBLE`, the branch that names no command at all. Resolve the
    first choice from the same table the `### Next step` uses
    (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2, applied there) — the
    `/product-workflows:create-prd` option where the gate set clears both data tests, the corresponding
    `/product-workflows:brd-split` where one fails and a command exists, and **no first choice at all**
    where none does, leaving the two below it. A folder carrying no `brd-link.md` has no gate set and
    takes `/product-workflows:create-prd <ADDRESS>` on the container test alone. The second and third
    choices are unchanged either way: a broad spec authored from the folder as it stands is still
    reachable, which is what keeps the array at two options in the worst case rather than one.

**Re-pointing the feature folder after the picker.** When Step A sets `focus_key` to an Epic (the
single-Epic and ≥2-Epic-selection cases), the feature folder becomes that Epic's per-Epic subfolder
`specifications/<PRD>-<vslug>/EPIC-<EPIC>-<eslug>/` (Phase 0 step 3's `focus_key`-set case), superseding the
provisional PRD-level folder confirmed in Phase 1 — Phase 0 already marks that folder provisional until
the folder read runs. Re-detect a prior run there (a `_session.md` → a resume is available for that
Epic). The broad-PRD-spec case — the only other one left — leaves the Phase 0 folder unchanged.

### Step B — Full Epic-scoped read

With granularity settled and `focus_key` resolved, perform the `full` read.
**Read the Epic folder itself, and everything under the PRD folder that bears on it.** The raw
material for user stories, acceptance criteria and test cases is the PRD's own text plus whatever the
Epic folder already holds — its `epic.md` where one exists, and any earlier `specification.md` or
`design.md`. A linked subtree of Stories and Sub-tasks is not something the tree carries, so where the
PRD is thin the grill has less to work from and must ask more; that is a real change in where the
detail comes from, and it belongs to the operator's answers rather than to an import.

The same two states apply here as in Step A: a **missing** folder surfaces the `key dir not found` rule
in `workflows-core:escalation-rules` (`["Re-enter key", "Cancel"]`); a folder holding
**no `prd.md`** is not a stop — the Phase 0 gate reported it already, and the grill works from what the
folder does hold. Then:

- **Epic-scope the read, against the tree.** The material is the PRD folder and what sits under it.
  When `focus_key` is set, read **that `EPIC-` folder** — its `epic.md`, and any `specification.md` or
  `design.md` already in it — plus the PRD folder's own `prd.md` for the frame, and read no sibling
  `EPIC-` folder at all. When `focus_key` is null (broad PRD-level spec), read the PRD folder and every
  `EPIC-` folder under it. There is no `linked_items` list and no Story/Sub-task subtree to filter: those
  were fields of a tracker export that no command produces any more (Step A), and the `EPIC-` folders on
  disk are the hierarchy now. Everything below — themes, `idea.md`, the Phase 5 raw material — derives
  from the folders this bullet named.
- Extract **capability themes** and component/product mentions from the folders just read — feeds
  Phase 3's repo derivation and Phase 4's `code-scanner` dispatches.
- Write **`idea.md`** in the feature folder from the text of the folders just read — **except on the
  BRD route**, where the provenance is already in the tree and this write is skipped and reported (the
  divergence named at the head of this phase) — pre-spec brainstorming provenance, in the same spirit
  as the `idea.md` convention `workflows-core:source-truth` already treats as non-authoritative once
  `specification.md` exists.
- Carry what those folders hold forward into Phase 5 — the raw material the grill mines for user
  stories, acceptance criteria, and test cases.

### the BRD route — read the implementation-altitude seed and the register

**Additionally** read the `PRD-` slice folder that is `prd_dir` on this route (Phase 0 step 1) — the resolved folder on a slice address, the folder above it on an Epic address — additionally, because Steps A and B have already read that same folder's `prd.md` and its `EPIC-` subfolders, or reported the PRD's absence. `spec-seed.md`, `decisions.md` and `brd-link.md` are what a slice carries and a keyed-route PRD folder does not, and they are the whole of the divergence this route is entitled to beyond grounding — which the paragraphs after this list read wherever `prd_dir` holds it, on either route. Read exactly these, and no other seed:

- **`spec-seed.md`** — implementation-altitude content, when the folder holds any. **Where to look, and it is two places.** The slice — `prd_dir` — first. Then, when the slice holds none, the **parent BRD folder** named by `brd-link.md`'s `parent:` — that is where `--sort-existing` actually writes all three seeds, because slices do not exist when intake runs. A seed found there is BRD-wide content, not slice-scoped: read it as context for this slice, say which folder it came from, and never treat it as though it were written for this slice alone. Finding neither remains the ordinary case. **No `/brd-*` command creates this file on the normal route** — the one command that creates one is
  `/product-workflows:brd-intake --sort-existing`, a one-time migration path for a package authored
  by hand before this route existed. Its absence is therefore the **ordinary** case, not a
  degraded one, and is reported rather than treated as a gap; what the route actually carries at
  every altitude is `decisions.md`, filtered by `altitude`, plus the grounding files.
  **`prd-seed.md` and `ard-seed.md` are not read**, at all: they are the product and
  architecture altitudes of the same router, belonging to `/product-workflows:create-prd` and
  `/product-workflows:create-ard`. Reading the first would let product requirements be restated as spec
  content rather than derived from it; reading the second would let this spec re-decide architecture
  the ARD owns, which `workflows-core:ard-resolution`'s deviation convention
  exists precisely to keep it from doing.
- **`decisions.md`** — the register, per
  `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1. Phase 0's register gate has already gated it on the default
  branch, so what is read here is the merged register or, where the folder holds none, nothing. It is read through §8 there: a **torn write** — a record a `/brd-interview` run left when it
  stopped before writing the round record that would name it — is read as absent, frozen against
  nothing and stamped `consumed_by` by nothing.
- **`brd-link.md`** — for `parent:` and `depends-on:` only. This run reads no `claims:` list and no
  coverage ledger **as an authoring input**: PRD eligibility and the allocation gate are
  `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5's rule about authoring a **PRD**,
  applied "when eligibility is checked", and a specification is not that artifact. Not checking it
  here is a decision, not an omission — `/product-workflows:create-prd` on the BRD route is where that gate
  lives, and this command is reachable without it.

  **Three places do open the ledger, and none gates anything this run does**: Phase 2 Step A's
  zero-Epics choice and the `### Next step` offer open it and the `claims:` list, and each decides
  only whether `/product-workflows:create-prd <SLICE-KEY>` can be *named* at all, since that command
  refuses three BRD-route shapes and not one
  (`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2). The Final report opens the
  ledger alone, reading its `disposition` column to leave out of the still-`consumed_by: none` list
  every finding about a row now `covered-by` another BRD — a report exclusion that changes no
  record. Reading a ledger to avoid offering a run that stops on arrival, or to count honestly, is
  not the same as gating this run on it.

**Absence is reported, never a stop, and the seed's absence is the ordinary case.** Nothing on the
normal route creates `spec-seed.md` at all (above), so a reconciled BRD routinely holds none. Say which
of `spec-seed.md` and `decisions.md` were absent — a reader cannot tell an unwritten file from an
unread one — and carry what is there.

**No `idea.md` is written on this route.** Step B writes one as pre-spec provenance derived from the
PRD text; there is none here, and the BRD folder already holds the provenance this spec was
built from — the register and the findings, each committed by the `/brd-*` run that wrote it, plus a
`spec-seed.md` where a `--sort-existing` migration left one. Minting an `idea.md` from any of them
would add a second, weaker record of the same thing in a folder whose whole point is that the first
one is auditable.

**Partition the register before the grill starts, because the partition is what freezes it.** The
five states and their treatment are `decision-register-format.md` §3's: a `decided` record is an
**input** the specification is authored from and never a question; `superseded` and `withdrawn` are
terminal and read for context only; `open`, `reopened` and an open `[AS#n]` are **gaps**, which may not
be consumed downstream while open (§3) and reach the spec as `- [ ]` items under the relevant stage's
`Open questions` sub-heading by id, at the heading depth
`${CLAUDE_PLUGIN_ROOT}/references/specification-format.md` fixes **for that stage** — never a depth
chosen here, because the depths differ per stage and heading depth alone is what places an
open-questions heading under its story or its criterion, so a gap written at the wrong one reads as
the neighbouring criterion's. Placing them there is also what keeps the header's `- **Open questions**: N` count honest.
Carry each `decided` record's `altitude` with it: only `implementation` ones have a home here, and a
`product` or `architecture` decision is read for context and **left for the command that authors at
its altitude** —
`/product-workflows:create-prd` and `/product-workflows:create-ard`, both of which read this same register and
filter it by `altitude` exactly as this phase does, so the channel that carries it is `decisions.md`
itself and never a seed file (`prd-seed.md` and `ard-seed.md` are created by nothing on this route).
That is what the altitude partition exists
for (D5), and it is not discarded by being skipped.

### grounding — read wherever `prd_dir` holds it, on either route

Where `prd_dir` carries `grounding/code-grounding.md` and/or `grounding/design-grounding.md`
— the idea-route PRD folder as readily as the BRD-route slice, since `/product-workflows:prd-ground`
now writes both from either — read the `[CG#n]` and `[DG#n]` finding records, per
`workflows-core:grounding-format` §2, **and, in the first of the two, any derivation matrix it
carries.** The matrix is not a file of its own: `/product-workflows:prd-ground` appends its rows to
`grounding/code-grounding.md` (that command's Phase 8), classed per `workflows-core:grounding-format`
§7 (`EXISTS | DERIVED | NEW-CAPTURE | NEW-CONFIG | PARTNER | DEFERRED | DEPENDENCY`) on either route —
it is implementation-altitude by construction, which is why this command is the one that reads it, and
an absent matrix is ordinary, since `/product-workflows:prd-ground` runs it only on a reporting- or
data-centric BRD, or under an explicit `--derivation-matrix`. A BRD ground with `--no-design` still
holds a `design-grounding.md` — `/prd-ground` Phase 8 writes it on every run, carrying a note saying
the pass was skipped and why, plus a `## Frame sets covered` census of the `design/` subdirectories on
disk. Absent means the file is not there at all, never that design grounding was declined. Say which
of the two files were absent — a reader cannot tell an unwritten file from an unread one — and carry
what is there. Where `git -C "$SPECS_PATH" status --porcelain -- <file>` lists either file present,
say so in the Final report — it is read as the working tree holds it, uncommitted, and that is a note,
never a stop. Where `prd_dir` holds neither file, report that and proceed exactly as this
command did before this feature — grounding is optional to this command and nothing here gates on it.

**A finding with no verifier outcome is not evidence** (`workflows-core:grounding-format` §8) and may neither
ground a spec statement nor be marked `consumed_by` anything. Carry only findings that hold one, and
name any offered that was dropped for want of an outcome.

**A `will-change` finding names a prerequisite decision that overturns it, where one is recorded**
(`workflows-core:grounding-format` §5). Record it as a `- [ ]` open question naming the finding. **On
the BRD route only**, a `decided` record may carry a `conditional_on: <BRD-KEY>/<decision-id>`
(`decision-register-format.md` §5), which may likewise not be written into this spec as settled
behaviour: record it beside the `depends-on:` list `brd-link.md` carries, naming the prerequisite BRD
and the specific decision. A `DEPENDENCY`-classed derivation-matrix row is the same situation for a
data element, wherever the matrix exists, and is recorded the same way.

**Extract capability themes.** **Where `prd_dir` holds verified `[CG#n]`/`[DG#n]` grounding
— on either route — seed the theme set from those findings before falling back to the themes Step B
extracted from the PRD/Epic text**: a finding whose verdict says a capability is absent is a theme
worth scanning, since that is where the work still needs doing; one whose verdict says it is present
names the code that already implements it, so the scan is directed at it rather than searching blind
for it — the same composition `workflows-core:model-routing/classification` §8.5's seeded second round
already establishes for a scan narrowed by verified anchors. **On the BRD route, additionally**,
extract themes from `spec-seed.md`, the implementation-altitude `decided` statements and the matrix
rows. Themes from every source above feed Phase 3's repo derivation and Phase 4's `code-scanner`
dispatches, in place of the PRD-derived themes drawn from Step B alone — this scan is never skipped,
made conditional, or put behind a flag, and a folder with no grounding and, on the BRD route, no seed
derives its themes exactly as Step B always has.

---

## Phase 2.5 — Resolve applicable ARD (optional)

Resolve any ARD for this item by invoking `Skill(skill: "workflows-core:reference", args: "ard-resolution")` and running its resolution with `<PRD>`, `<EPIC>` (`focus_key`), and `$SPECS_PATH`. **On the BRD route the pair comes from `brd-link.md`'s `parent:`, never from a segment count**: the route resolves a slice and nothing else (Phase 0 step 0), so the `parent:` is always there — pass `prd: <parent-key>`, `epic: <SLICE-KEY>`. The second mapping needs no change to that reference — a slice folder sits inside its parent's exactly as an Epic subfolder sits inside a PRD dir, the layout its Epic-level branch already collects — and it is the same pair `/product-workflows:create-ard <SLICE-KEY>` writes into the ARD's own `prd:`/`epic:` frontmatter, so the two agree by construction rather than by coincidence. On `status: none`, **skip and proceed exactly as before**. On `status: unmerged`, **stop**, naming the returned `branch` and any `pr`. On `status: found`, keep the spec's user stories + scope consistent with the returned `invariants` + `guidance_summary` during the Phase 5 grill; record a necessary deviation under the spec's `### Open questions` (never edit the ARD). Pass the `invariants` to `spec-reviewer` in Phase 6 as `applicable_ard`.

---

## Phase 3 — Derive repos + soft gate

1. **Auto-derive candidate repos.** From the Phase 2 capability themes and any repositories the
   `implementation.md` records in the folders Step B read name
   (`workflows-core:implementation-format` §1 — their `repo` entries; a record lives in the folder
   of the unit implemented, so that is the focus Epic's where `focus_key` is set, and the PRD
   folder's and every `EPIC-` folder's where it is null), build a candidate repo-slug list. There
   is no PR list to read: nothing here reads a tracker or a pull-request API. **Under
   the BRD route there is no implementation record either; derive the list from the slice
   folder's — `prd_dir`'s — `grounding/baselines.md` instead**, which already records repository → pinned commit for
   every repo `/product-workflows:prd-ground` read, plus the Phase 2 themes. That is a stronger starting
   set than a theme guess, and the rest of this phase treats it identically — step 3 resolves each
   entry against the slug map and step 4's soft gate handles one that is not mounted. A finding's
   evidence stays cited at the commit that finding is pinned to
   (`workflows-core:grounding-format` §2), which is not necessarily the commit
   Phase 4's scan reads; where the two differ, say so rather than silently re-dating the claim. If the
   list is
   empty, escalate per the `No repos derivable — /epics` rule in
   `workflows-core:escalation-rules`:
   ```
   choices: ["List repos to scan manually", "Proceed without code scan", "Cancel"]
   ```

2. **Build the slug→clone map** (`/epics`-style). For each top-level directory under each entry of
   `$REPOS_PATH`, run `timeout 5 git -C <dir> remote get-url origin 2>/dev/null`, strip a trailing
   `.git`, and take the URL's last path segment as that clone's slug. Skip directories with no `.git`
   or whose `git remote` call fails/times out.

3. **Resolve each candidate against the map.** One match → use it. An ambiguous slug (multiple
   matches) or zero matches both escalate per the `Repo unresolved (zero matches) — /epics` rule in
   `workflows-core:escalation-rules`:
   ```
   choices: ["Skip and continue without this repo's scan", "I'll clone it — wait", "Cancel", "Specify a different absolute path for this repo"]
   ```

4. **Cross-check mounted status — soft gate.** A resolved repo slug that is not actually mounted under
   `$REPOS_PATH` does NOT hard-block `/specify` the way an unresolved slug does above. Instead: record
   a feasibility `- [ ]` open question in `_session.md` (e.g. "Cannot ground <theme> — `<repo-slug>` is
   not mounted; feasibility unverified"), report the gap to the user now, and **PROCEED** to Phase 4
   with the remaining mounted repos. Describe the missing capability and why it matters — the
   specification cannot name or link an unmounted repo's code, so any claim resting on it stays an
   open question until the repo is mounted and `/specify` is re-invoked (Phase 5 keeps `_session.md`
   current, so the run is resumable).

---

## Phase 4 — Light code scan

Spawn `code-scanner` instances in **batches of up to 4 concurrent agents** per Agent message, on the
mounted candidates resolved in Phase 3. Wait for each batch before spawning the next. This is
deliberately a **light** scan relative to `/epics`' — grounding for feasibility and to avoid
contradicting existing behaviour, not a full reuse audit.

For each repo in the batch:

→ Agent (subagent_type: "workflows-core:code-scanner", model: `<detection_model — §2.1 Sonnet chain>`):
  > "Scan this repo for the brief:
  >
  > repo_path:     <resolved absolute path for this repo from Phase 3>
  > repo_url_slug: <repo slug, e.g. "cluster">
  > capability_themes:
  >   [paste the themes array from the folder read]
  > context: |
  >   [3–5 sentences: the item's goal, what the specification must ground]
  > search_hints:
  >   symbols:  [class/function names inferred from the item text, or []]
  >   paths:    [directory globs inferred from themes, or []]
  >   keywords: [grep keywords extracted from themes]
  > refresh:
  >   switch_to_default_branch: [true if Phase 1 chose 'fetch + pull default branch' (default) or 'fetch only'; false if 'no refresh']
  >   pull: [true if 'fetch + pull default branch'; false otherwise]"

**Documentation grounding (optional).** Phase 1 resolved it and showed its line — before this phase's `code-scanner` dispatches — and nothing here resolves it again. Where it resolved `docs_grounding: ON`, `dispatch-docs-grounder` (`workflows-core:docs-grounding`) with `feature_summary` = the scoped Epic/PRD goal, `key` = the focus key, `themes` = the Phase 2 capability themes. Carry the digest into the Phase 5 grill with **grill-rank** consumption. Where it resolved OFF, dispatch nothing.

Handle per-repo status after the batch returns:

- `OK` / `PARTIAL` / `EMPTY` — store the "does this exist / where / gaps" output; this grounds Phase 5's
  grill (e.g. answering a question from the scan instead of asking the user).
- `REPO_MISSING` — should not happen at this stage (Phase 3 already checked). If it does, escalate per
  the `Repo missing (after resolution)` rule in `workflows-core:escalation-rules`.
- `DIRTY_TREE` — escalate:
  ```
  choices: ["Stash changes and retry this repo", "Skip this repo", "Cancel"]
  ```
- `REFRESH_BLOCKED` — escalate:
  ```
  choices: ["Continue with current local state", "Skip this repo", "Cancel"]
  ```
- `prep.read_only: true` — not a failure. The scan ran at `prep.scanned_ref`. Escalate per the `Read-only mount — ref stale or diverged` rule in `workflows-core:escalation-rules` **only** when `prep.ref_committed_at` is more than 14 days old or `prep.head_divergence.ahead > 0`; otherwise proceed silently and cite evidence at `prep.scanned_ref`.

---

## Phase 5 — Author via grill

**Interview technique (grilling — embedded; no runtime dependency).** Conduct each stage as a **relentless** interview per `Skill(skill: "workflows-core:reference", args: "grilling-technique")` — one question at a time, recommend each answer, explore the Phase 4 code scan / PRD content to self-answer (fact-vs-decision), walk the design tree in dependency order, continue to shared understanding then write that stage's section.

Walk the stages in order, authoring `specification.md` live against `${CLAUDE_PLUGIN_ROOT}/references/specification-format.md`, applying the no-hard-wrap prose convention in `Skill(skill: "workflows-core:reference", args: "prose-formatting")`:

1. Header + **Problem statement**
2. **Scope** (In/Out)
3. **User stories** (`[Uxx]`)
4. **Acceptance criteria** (`[ACxx]`, EARS)
5. **Test cases** (`[TCxx]`)

As each decision settles, append it to `_session.md`; capture a genuinely-ambiguous term in `_glossary.md`. Resolve open questions to zero where possible; leave genuinely unresolvable ones as `- [ ]` and keep the header **Open questions** count in sync. A repo gap surfacing here → escalate (describe the missing capability + why) and STOP; the run is resumable from `_session.md` after the user remounts and re-invokes.

### the BRD route — where the seed lands, and the grill is restricted to gaps

**Where the seed's content lands.** `spec-seed.md` and the implementation-altitude `decided` records
supply the raw material the PRD supplies on the other route: the problem frame and scope
boundary, the behaviours that become `[U01]…` user stories, and the settled choices those stories must
honour. **Derivation-matrix rows are behaviour, not prose to paste**: an `EXISTS` or `DERIVED` row is
a fact the acceptance criteria can rely on; a `NEW-CAPTURE` or `NEW-CONFIG` row is work this spec must
actually deliver, so it belongs in `## Scope`'s In-scope list and in an `[AC01]`-level EARS statement
rather than a footnote; a `PARTNER` row is a boundary and usually an Out-of-scope entry; a `DEFERRED`
or `DEPENDENCY` row is an open question with its prerequisite named. Naming the `[VD#n]`, `[CD#n]`,
`[CG#n]` or `[DG#n]` beside the statement it grounds keeps the two records findable from each other.
`${CLAUDE_PLUGIN_ROOT}/references/specification-format.md`'s stage rules are not relaxed: a matrix row
naming a physical column is not licence to write a table name into a user story.

**The grill may fill anything the seed does not settle. It may not reopen a `[VD#n]` or a `[CD#n]`**
(D3). Those decisions arrive carrying customer sign-off in writing, and a grill that re-litigates one
manufactures a contradiction between this specification and a document the customer has already agreed
to. Three things make that a guarantee rather than an instruction:

1. **The question set is a subtraction, not a sweep.** Phase 2's partition already sorted the register
   into inputs, terminal records and gaps; the grill's questions come from the gaps and from what
   `spec-seed.md` leaves unstated. A settled `chosen` is never a question, so there is nothing for the
   interview to walk it back through.
2. **This run cannot satisfy either cause that would license a reopening.**
   `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4 admits exactly two — a new
   grounding finding, or an incoming customer decision — and this command produces neither: Phase 4 is
   a `code-scanner` pass, which `workflows-core:grounding-format` §1 says is a
   capability inventory and explicitly **not** a finding, and no customer review reaches the register
   except through `/product-workflows:brd-reconcile`.
3. **The only field of a decision record this command may write is `consumed_by`** (Phase 7).
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

**What happens when the grill surfaces a genuine contradiction with a settled decision.** Do not
decide it and do not soften it into the spec's prose. Record it as a `- [ ]` open question naming
the `[VD#n]` or `[CD#n]` it contradicts and what this run believes contradicts it, and name the
route that may act on it. **Neither route is this command**, and both are exactly §4's two causes
rather than a third invented here: a `[VD#n]` needs a new grounding finding, which only
`/product-workflows:prd-ground <SLICE-KEY>` mints — with `--rebaseline` where the pinned code has
moved — and `/product-workflows:brd-interview <SLICE-KEY>` then re-decides against; a `[CD#n]` needs
the customer, through `/product-workflows:brd-package <SLICE-KEY>` and then
`/product-workflows:brd-reconcile <SLICE-KEY> @<review-file>`. A contradiction with an `AD#N` is a
different thing and keeps its existing home: the `### Open questions` deviation record
`workflows-core:ard-resolution` prescribes.

---

## Phase 5.5 — Structural pre-lint

Before finalizing, run the deterministic checks in `Skill(skill: "workflows-core:reference", args: "pre-lint")` against the drafted `specification.md`: the **Universal
checks** plus the **spec** block (incl. the `- **Open questions**: N` header equalling the `- [ ]`
count). Surface every finding; inline-fix the mechanical ones (renumber a duplicate `[Uxx]`/`[ACxx]`/
`[TCxx]`, correct the open-questions count, delete a stray placeholder token); leave content gaps for
the grill/author. **Advisory** — never blocks; proceed to Phase 6 once findings are surfaced.
`spec-reviewer` remains the gate.

## Phase 6 — Finalize + review gate

1. **Dispatch `spec-reviewer`.**

→ Agent (subagent_type: "product-workflows:spec-reviewer", model: `<review_model — §2 Opus chain, equal to spec-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the specification for this brief:
  >
  > Specification path: [absolute path to specification.md]
  > Detected maturity: test
  > applicable_ard: [the ARD invariants resolved in Phase 2.5, or omit if none]"

2. **Act on the verdict** (mirrors `/epics` Phase 7):
   - **`BLOCK`** — fix the BLOCKER findings (the orchestrator/grill edits `specification.md` inline —
     there is no delegated writer to re-dispatch) and re-review once. If still `BLOCK`, escalate per
     the `Review verdict BLOCK (unresolved after one fix cycle) — /epics` rule in
     `workflows-core:escalation-rules` for each unresolved BLOCKER individually:
     ```
     choices: ["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"]
     ```
     "Defer" means appending a `## Refinement notes` section to `specification.md` with a `- [ ]` item
     per deferred finding (mirrors `/epics`' Epic-refinement note), in addition to the final report.
   - **`MAJOR` / `MINOR` / `NIT`** (surfaced under `PASS WITH RECOMMENDATIONS`) — defer to the final
     report; no mandatory fix cycle.
   - **`PASS`** / **`PASS WITH RECOMMENDATIONS`** — proceed to Phase 7.

Cap: one fix cycle + one re-review maximum.

**The recorded verdict names the version it was taken against** — where any edit followed it, the final report says so and names the edits, per the `A recorded verdict names the version it was taken against` rule in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`. Where none did, it says that too.

---

## Phase 7 — Handoff

Write the feature folder: `specification.md` (`Published: no`), `idea.md`, `_session.md` and `_glossary.md`. **On the BRD route there is no `idea.md`** (Phase 2, the one divergence that phase keeps) — the other three are written exactly as above, into the feature folder Phase 2 resolved: the slice folder itself when `focus_key` is null, or the `EPIC-` subfolder Step A selected when it is set.

**Wherever `prd_dir` holds `grounding/`, on either route, close the consumption loop before
the offer.** The design's *Consumption tracking* section (§7.3) has every finding and decision record
a `consumed_by`, so that "nothing was lost" is checkable rather than hoped for. Set `consumed_by:
specification` on each `[CG#n]`/`[DG#n]` finding in `<prd_dir>/grounding/code-grounding.md` /
`<prd_dir>/grounding/design-grounding.md` **this specification actually drew on** — and on nothing else: a
record read for context and not used is still `none`, and marking it consumed would report a routing
that never happened. A finding with no verifier outcome is never marked, whatever the spec did with
the claim, because it was never evidence (`workflows-core:grounding-format` §8). **On the BRD route,
additionally**, set `consumed_by: specification` on each implementation-altitude `decided` record in
`<prd_dir>/decisions.md` this specification actually drew on, under the same exclusion. These are the **only**
writes this command makes into a grounding file or, on the BRD route, into `decisions.md`, and none of
them is a `status` change or any other field (Phase 5). Everything at implementation altitude still
`none` afterwards goes in the final report by id.

**`spec-seed.md` is reported, not stamped**, for the reason the field's own authorities give:
`consumed_by` is a field of a *record* — defined on a decision by
`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §1 and on a finding by
`workflows-core:grounding-format` §2 — and the seed carries neither, so there is no per-item field to write and
inventing one would mint a format this command alone understood. Its consumption is reported at
**file** granularity in the final report. The derivation matrix is the one part of the seed material
that *is* stamped, and only because it lives inside `code-grounding.md`: a matrix row is not a finding
record either, so it too is reported at file granularity rather than given a `consumed_by` of its own.

Then **offer** (commit-when-asked — never automatic), invoking `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and presenting its §4.3 choice array verbatim:
```
choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]
```

On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix: spec`; `feature_folder` = the Epic subfolder for a **per-Epic** spec (a PRD + focus Epic — the only Epic-level shape there is, since every `EPIC-` folder sits under a PRD folder), or the PRD dir for a **broad PRD-level** spec (`focus_key` null), a `PRD-` slice folder on the BRD route being that same PRD-dir case rather than a third one, since a slice *is* a PRD folder — Epic keys are globally unique, so the per-Epic form needs no PRD prefix, and both forms use hyphens; §2.2 derives `spec/<EPIC>-<eslug>` or `spec/<PRD>-<vslug>` from that folder, and `spec/<SLICE-KEY>-<slug>` from a slice folder's own basename — which collides with neither `/product-workflows:create-prd` on the BRD route's `prd/` branch on the same key, nor `/product-workflows:create-ard` on the BRD route's `ard/` one, nor the `/brd-*` family's shared `brd/` one, because §2.2's prefix is the caller's own; `deliverable_paths` = `specification.md`, `_session.md` and `_glossary.md` in `feature_folder` — **plus, wherever `prd_dir` holds `grounding/`, `<prd_dir>/grounding/code-grounding.md` and `<prd_dir>/grounding/design-grounding.md`, and, additionally on the BRD route, `<prd_dir>/decisions.md`**, because the `consumed_by` writes above land in those files and an uncommitted consumption record is one no later run can read. **Those three are named at `prd_dir`, never at `feature_folder`**: on a per-Epic run `feature_folder` is the `EPIC-` subfolder, while the grounding files and the register stay in the PRD folder above it — the slice folder, on the BRD route — which is the folder those writes land in, so a path formed against `feature_folder` would name a file that does not exist and leave the consumption record uncommitted; on a broad PRD-level run the two folders are the same and nothing changes; `spec-seed.md` is not staged, because this run does not write to it; `title: <EPIC|PRD> Add specification`; and `body_facts` = the stage/user-story/AC/TC counts, the open-question count, the `spec-reviewer` verdict, and how many items were marked `consumed_by: specification` — and, on the BRD route, the `<SLICE-KEY>` whose folder this specification was seeded from. **Merged-to-main = ready for the dev-team handover** — Devs and `/design` read the spec from `main`, never from the branch, and `require-on-main` now enforces that rather than merely stating it. Emit its §4.1 outcome line in the Final report.

### Next Epic (after a per-Epic spec from a multi-Epic PRD)

When this run authored a **per-Epic** spec that was selected from Step A's ≥2-Epics picker, offer — once Phase 7's write/commit completes — to continue with a sibling Epic under the same PRD:
```
choices: ["Next Epic — re-open the picker (Recommended)", "Stop here"]
```
On **"Next Epic"**, **re-render the Phase 2 Step A progress-aware picker minus the just-completed Epic** — recompute each remaining Epic's ○/◐/● state from its feature folder, so the freshly-authored spec now shows **● done** and drops out of the actionable set — then, on selection, set `focus_key` to the new Epic and loop back through Phase 2 Step B → Phases 3–7 for it. This offer does **not** apply to a single-Epic PRD or a broad PRD-level spec — there is no sibling to advance to. **On the BRD route it applies on exactly the same terms**: Step A runs there too, so a slice holding two or more `EPIC-` folders re-renders the picker like any other PRD folder, and a slice holding none or one does not — the same two exclusions as above, reached by the same test rather than by a route branch. What is *not* a sibling Epic is another **slice**: that is a separate folder with its own seed, reached by re-running `/product-workflows:specify <SIBLING-SLICE-KEY>`, which waits on nothing this run produced.

### The Epic flow (document to the user)

1. `/product-workflows:epics <ADDRESS>` writes one `EPIC-` folder per child Epic under the PRD folder.
2. `/product-workflows:specify <EPIC-ADDRESS>` authors that Epic's `specification.md`.

**There is no step between them.** `/epics` writes into the tree this command reads, so an Epic is
visible to `/specify` the moment it is written — no creating it anywhere else, and nothing to import.
That gap used to be a manual export-and-re-import through a tracker, and removing it is most of what
this increment is for.


## Phase 8 — Session maintenance & feedback

Terminal phase — runs after Phase 7 and before the Final report is presented;
NEVER interrupts an earlier phase. `/specify` has no built-in maintenance agent,
so this phase invokes `impl-maintenance` on the Sonnet detection chain and then
persists the plugin-facing slice of its report as session feedback.

**Capture-at-block invariant.** This terminal phase captures gaps for a *completed* run. Separately, if an EARLIER phase **halts on a plugin / skill / command / reference gap** (a capability the run needed but the plugin lacked), `emit-block` (per `workflows-core:feedback-emission`) at that halt **before** escalating — so a run abandoned at the block still records the gap. NEVER `emit-block` for a work-quality review BLOCK or an environment / user halt (repo/spec gate, key-not-found, cancellation). **Every `SPECIFY_*` stop is argument-, tree- or git-shaped, and of that second class**: `SPECIFY_NEEDS_KEY`, `SPECIFY_ONE_ADDRESS`, `SPECIFY_BRD_NOT_FOUND`, `SPECIFY_BRD_NOT_SLICED`, `SPECIFY_EPIC_NOT_FOUND`, `SPECIFY_REGISTER_NOT_ON_MAIN` and `SPECIFY_REGISTER_NOT_HANDED_OFF` report the operator's own argument list, specs tree or where its register sits in git, not a capability this plugin lacks, so none of them `emit-block`s.

**Session-hygiene invariant.** End the report with a `### Context hygiene` block per
`workflows-core:session-hygiene` — prepare-first (the
`resume.md` write runs later, in the terminal cost phase, per
`workflows-core:session-hygiene` §1 — this block prints the
guidance only), then a
span suggestion (PRD-level→`/product-workflows:epics` `/compact`; Epic-level→`/dev-workflows:design` `/clear`) +
`/rename <PRD-ID>-<slug>-pe`. Guidance only, never auto-run.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 3's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

**The run's key on the BRD route.** Phase 0 resolved a BRD key, which is a folder name and never a
second identity (`workflows-core:addressing` §1). Any tracker identity for this work,
if one exists at all, is the `key` in the PRD this BRD folder holds — glob
the BRD folder's `prd.md`, `kind: prd`. So the address passed to
`emit-auto` (below) and `emit-cost` (Phase 9) is that minted key when the folder holds a PRD carrying
one, and `null` otherwise (`source: none` either way); `commit-artifacts` resolves its own key the
same way and commits under `NOISSUE` when there is none, per
`workflows-core:specs-repo-git` §4 step 4. The `<BRD-KEY>` is never passed as a
`key` — a folder key in a tracker-key field is the confusion the two fields exist to keep apart.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<detection_model — §2.1 Sonnet chain>`):
   > "Analyse this session and return a Lessons Learned report.
   >
   > Session handoff:
   > - Command run: /specify
   > - What was done: [one-paragraph summary of the specification authored]
   > - Key events: [BLOCK reviews and their reason, unmounted-repo soft-gate advisories, unresolved open questions, picker or handoff friction — or 'none']
   > - Workarounds used: [manual steps not automated by the workflow — or 'none']
   > - Review verdict: [the spec-reviewer verdict — PASS | PASS WITH RECOMMENDATIONS | BLOCK]
   > - Test result: N/A (no tests in /specify)
   > - Project root: [the resolved feature folder under $SPECS_PATH]"
2. **Persist plugin feedback (automatic).** Project the report's plugin-facing
   slice into the specs repo by invoking `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and calling its `emit-auto` entry point (§6). Pass the Lessons Learned report,
   `command: /specify`, the run's `key` and `source`, and `plugin_version`
   (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). `emit-auto`
   renders only the report's **Command workflow improvements**, **New agents /
   skills**, and plugin **Reference docs** sections plus the **Key observations**
   that triggered them (§4) — never target-project `CLAUDE.md`/hook advice — as
   `origin: auto` entries, dedupes by stable `id` (§3), resolves the target via
   the §2 specs-first ladder, and writes silently.
3. **Surface** the persisted path (or "no plugin-facing signal — nothing
   persisted") as this phase's only output.

ADDITIVE — this phase NEVER fails the run, NEVER commits (still true — git for
the deliverable is offered only in Phase 7, and this phase itself runs no git;
those writes are committed by the terminal `commit-artifacts` step in Phase 9,
per `workflows-core:specs-repo-git` §4), and NEVER writes
into the current working directory, where it is not the specs repository. The specs-first ladder writes the feedback
file inside `$SPECS_PATH`, alongside the feature folder — the intended home.

## Phase 9 — Session cost

Terminal phase — the NEW final operational phase; runs after Phase 8 (feedback)
and NEVER interrupts an earlier phase. Records this command's token-cost
contribution to the PRD by invoking `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and calling its single `emit-cost` entry point. Unlike feedback, **cost ALWAYS runs** — it never "writes
nothing".

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way. Otherwise, call `emit-cost` with `command: /specify`, `phase: specification`, `role: pe`,
the run's `key` (or `null`) and `source`, and `plugin_version` (read from
`${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). It resolves the session
transcript + subagents (§1), loads and **advances the chained checkpoint** (§3),
computes the per-model token-cost delta against
the price table (§4), records the optional statusline cross-check (§5), and
appends one per-invocation entry to `<PRD-dir>/dev-workflows/cost/<sid8>.md` via
the specs-first ladder (§8) — pending + opportunistic move-then-delete
reconciliation (§9) when no PRD key resolves. **The checkpoint advances even in
the pending / report-only tiers.** Surface the persisted path (or the
report-only notice) as this phase's only output.

**Write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite
`<PRD-dir>/dev-workflows/resume.md` now — after the cost entry above, so the
pointer reflects the completed run, and before the commit step below, so it is
included in it. Redact per §1. Silent; the printed `### Context hygiene`
guidance already appeared in the report.

**Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It
stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits
`<KEY> Add dev-workflows session artifacts (/specify)` with no `Co-Authored-By`
trailer, and pushes to the branch this run's handoff phase created (§4.1). It
NEVER touches a code repo, a docs repo, or the current working
directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; and skips entirely when the
run carries `specs_git: blocked` (§3.3 G0), re-emitting that notice. Hold its
§6 outcome line for the Final report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (git
for the deliverable is offered only in Phase 7; the terminal step above commits
only the bounded session-artifact paths in `$SPECS_PATH`), and NEVER writes
into a docs/code repo or the current working directory, where it is not the specs repository; no user name is ever
written (§10 privacy).

## Final report

Report: feature-folder path; stage/user-story/AC/TC counts; open-question count; unmounted-repo advisories; **the PRD gate's return value and whether an authored `prd.md` was read from `prd_dir`** — the same two lines on every route, so a reader can tell an `absent` PRD from an unrun gate; the `spec-reviewer` verdict; the resolved model routing (+ any Opus degradation, or `Model routing: bypassed — enforced <id> (flag|env)` in its place wherever `run_flags.enforced_model` is set, per `workflows-core:model-routing/classification` §10); the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); the `Phase handoff:` outcome line from `handoff-to-main` (`workflows-core:phase-handoff` §4.1); the `Session feedback: …` line wherever Phase 8 printed one (under `--skip-feedback`) and the `Session cost: …` line wherever Phase 9 printed one (under `--skip-costs`); the `Specs repo:` outcome line from `commit-artifacts` (`workflows-core:specs-repo-git` §6), with any guard notice repeated in full; and a reminder of the Epic flow described above + that `Published: yes` is a human-only freeze step.

**Wherever `prd_dir` holds `grounding/`, on either route, additionally:** which of
`<prd_dir>/grounding/code-grounding.md` and `<prd_dir>/grounding/design-grounding.md` were present, which of
those Phase 2 found uncommitted, and whether `code-grounding.md` carried a derivation matrix; every `[CG#n]`/`[DG#n]` dropped for want of a
verifier outcome, by id; every implementation-altitude item still `consumed_by: none`, by id, per the
design's *Consumption tracking* section (§7.3) — **excluding the baseline `[CG#n]` findings**, which
are never `consumed_by` anything and whose `none` therefore reports no gap
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
under it rather than omitting the count. The derivation matrix's own consumption is reported at file
granularity, the same way `spec-seed.md`'s is below.

**On the BRD route, additionally:** the `<SLICE-KEY>` seeded from and its resolved folder; this run's
`parent:` key — every run of this route is slice-level — and the `(prd, epic)` pair Phase
2.5 passed to `workflows-core:ard-resolution` with the `status` it returned; which of `spec-seed.md`
and `decisions.md` were present; that no `idea.md` was written and why; every `[VD#n]`/`[CD#n]`/`[AS#n]`
carried in as a gap rather than an input, by id and status; every contradiction Phase 5 recorded
rather than decided, with the reopening route named for each; `spec-seed.md`'s
consumption at file granularity; and any product- or
architecture-altitude content the grill surfaced and left for the command that authors at that
altitude instead of the spec (D5) — naming the command, never a seed file, since the register it will
read that content out of is the one this run already read. Say plainly whether `/dev-workflows:design` was named in the `### Next step` and, when it
was not.

### Next step

End the report with a `### Next step` recommendation per `Skill(skill: "workflows-core:reference", args: "next-phase-offer")` (guidance only — never auto-invoked): **Epic-level spec** (the address resolved an `EPIC-` folder) → hand to Dev → `/dev-workflows:design <EPIC>` `<merge-clause>`, which will not start until this spec is on the default branch — on every path, since `workflows-core:phase-handoff` §3.4's `/design` row is a stop even for a spec that reached no branch — and the **Epic fan-out** `/product-workflows:specify <SIBLING-EPIC>` for a sibling Epic (breadth), which waits on nothing this run produced and carries no clause; **PRD-level spec** (the address resolved a `PRD-` folder) → `/product-workflows:epics <PRD>` (PE) `<merge-clause>`, which stops rather than skipping wherever this spec reached a branch (§3.3 rows D/E) and skips exactly as it did before wherever it reached none (§3.4's `/epics` row). If the run BLOCKED or left open `- [ ]` items, recommend resolving those first.

**One precondition governs every `/product-workflows:epics` option above, on both routes.** `/epics` accepts
a folder holding a `prd.md` that asserts `kind: prd` and refuses one that does not
(`commands/epics.md` Phase 0 step 1b, `EPICS_NO_PRD`). This run does **not** require a PRD — its Phase 0
gate has an `absent` branch that specifies from the resolved folder, and on the BRD route
`/product-workflows:create-prd` is not a prerequisite at all — so the folder it just wrote a specification
into may legitimately hold no PRD. **Test the resolved PRD folder for an authored `prd.md`** before
rendering the recommendation — the folder Phase 0's PRD gate tested: the resolved folder itself on a
PRD-level run, and on an Epic-level run its parent; never the `EPIC-` folder, which holds no `prd.md`
by construction. Where there is one, name `/product-workflows:epics <ADDRESS>`; where there
is not, name **`/product-workflows:create-prd <PRD-KEY>`** instead, `<PRD-KEY>` being that tested
folder's own `key` — `<ADDRESS>` on a PRD-level run, the parent's on an Epic-level one, and never
the Epic's, which `/create-prd` refuses (its step 5b, `CREATE_PRD_EPIC_FOLDER`) — **but only where
that command can itself run**. Offering `/epics` there would name a run that stops on arrival, and
naming `/create-prd` without the test below does the same thing one command further on.

**`/create-prd` refuses three BRD-route shapes, not one**
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.2, the authority, not restated
here). Of the three, the tested folder has cleared only the container refusal — a PRD-level run by
resolving a `PRD-` folder itself, an Epic-level run by gating the `PRD-` folder above the Epic.
`/create-prd`'s Epic-folder refusal (its step 5b) is not a BRD-route shape and is not among them;
naming the tested folder's key rather than the Epic's is what clears it. The other two are data
refusals on a slice's own ledger and exist only where the tested PRD folder carries a `brd-link.md`;
an idea-route PRD folder has no gate set, so `/product-workflows:create-prd <PRD-KEY>` is reachable
there on the `prd.md` test alone. Where the folder is a **slice**, read its `coverage-ledger.md` —
the rows its `brd-link.md` `claims:`, out of the file and never off a `ledger:` line (§6.1) — and
resolve the recommendation from it:

| The slice's gate set | What the `### Next step` names |
|---|---|
| No row `unallocated`, and at least one `covered-here` | `/product-workflows:create-prd <SLICE-KEY>` `<merge-clause>` — all three refusals cleared, and its Phase 0 step 7a gates the slice's `decisions.md`, which this run's handoff stages wherever it stamped `consumed_by: specification` on a register record, so the clause is required |
| A row still `unallocated` | `/product-workflows:brd-split <SLICE-KEY>` instead: `/create-prd` would raise `CREATE_PRD_BRD_UNALLOCATED`, and that walk is what moves those rows (allocate-only on a slice). Its own Phase 0 gates on this slice's grounding findings carrying a verifier verdict, so say so beside the offer |
| No row `covered-here`, gate set **empty** — `brd-link.md` claims nothing | `/product-workflows:brd-split <PARENT-KEY>` instead — the keep-or-remove run for a standing empty child, and not a no-op there — in the form the parent's own ledger decides, exactly as `/product-workflows:create-prd` Phase 0 step 7's empty-gate-set row decides it: where that ledger still holds an `unallocated` row, `/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"`, since that run walks the row too and stops with `BRD_SPLIT_NEEDS_INSTRUCTION` without an instruction; where it holds none, the bare form; where it cannot be read, report it by path and name neither form |
| No row `covered-here` and none `unallocated`, gate set **non-empty** | **Name neither `/create-prd` nor `/epics`.** `/create-prd` would raise `CREATE_PRD_BRD_NOT_ELIGIBLE`, whose non-empty branch names no command at all by design; say instead what the gate-set rows resolved to and that nothing in the plugin moves a terminal row back to `unallocated`. `/dev-workflows:design <ADDRESS>` is unaffected and is still recommended — it takes over the specification this run just wrote and needs no PRD |
| No readable `coverage-ledger.md` beside the `brd-link.md` — absent, or present and unreadable — while that file claims rows | **Name neither `/create-prd` nor `/epics`**, and report `<slice-dir>/coverage-ledger.md` by path, as missing or as unreadable with the read error: this is not an empty gate set, and `coverage-ledger-format.md` §5.2 forbids resolving it to the empty row's `/brd-split <PARENT-KEY>`. `/dev-workflows:design <ADDRESS>` is unaffected and is still recommended |

**Dropping rather than annotating follows `commands/brd-reconcile.md` Phase 14**, which runs these
same two data tests before offering `/product-workflows:create-prd <SLICE-KEY>` and drops the option on
the stated ground that a hard refusal in another command's Phase 0 is not a state the reader can
judge for themselves. A `### Next step` is prose rather than a `choices:` array, so dropping an
option costs it no arity — it says what it can honestly recommend and why the rest is absent.

**On the BRD route the same offers apply, on the same terms.**
`/dev-workflows:design` and `/product-workflows:epics` both resolve a folder in the specs tree with
`resolve-address` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3) — the same tree, and often
the same folder, this run has just written into:

- **`/dev-workflows:design <ADDRESS>` `<merge-clause>`** — it gates the `specification.md` this run
  wrote, so the clause is required.
- **`/product-workflows:epics <ADDRESS>`** — it reads the PRD folder and gates nothing this run
  produced, so it carries no clause; it is subject to the `prd.md` precondition above, which is the
  same test on both routes and not a BRD-route qualification. **Its replacement is not**: only a
  BRD-route slice has a gate set, so the table above is where a slice with no `prd.md` and no
  `covered-here` row stops the `/create-prd` recommendation from being made at all.

**What this replaces is worth naming, because a reader who remembers it will look for it.** Both
offers used to be withheld unless an export directory existed under the key, a test that existed
only because both commands resolved that export and found nothing without it. Neither reads an
export any more. The test is not relaxed — its subject no longer exists.

**And the commercial step, in prose — and it too depends on the route.** On the BRD route, where
verified grounding and a settled register already exist **and an `ard.md` is already in place**, this
specification takes the folder to tier 4, the top tier, where QA effort is sized from the authored
test-case count rather than a ratio and the definition of done is built from the acceptance criteria
(`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §5): **`/product-workflows:prd-proposal <PRD>`
prices it at the tightest range the format allows.** Where the BRD route reached `/specify` without an
`ard.md` — optional in this family, and so a normal state rather than an edge case — tier 3's own
condition is unmet, and the folder stays at whatever tier its own ladder walk reaches (§5) until one
lands, this specification notwithstanding. On the idea route the folder stays at §5's tier-1
ceiling regardless of this specification: it may be ground — `/product-workflows:prd-ground` runs on
an idea-route folder too — but tier 2 also needs a settled register, and nothing on the idea route
produces one. `/product-workflows:prd-proposal <PRD>` is still worth naming, but on this route it
stays indicative. Either way it is optional and ungated. No merge wait:
that command gates on `prd.md`, which this run does not write.

- Consider **`/rename <PRD-ID>-<slug>-pe`** to relocate this session later.

Guidance only — see `workflows-core:session-hygiene`.

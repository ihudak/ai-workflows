---
name: prd-ground
description: Grounding workflow serving both routes into a PRD, its route detected from the resolved folder and never declared — the BRD-to-PRD route's PA phase, run once per slice `/brd-split` carves and again when a re-cut gives a slice a new row; and, optionally and ungated, once after `/create-prd` on the idea route. Pins every mounted repository to a verified commit and grounds every claim in the resolved folder's own claim list — a BRD slice's [BR#n] rows on the BRD route, a PRD's [AC#n]/[FR#n] rows (plus a [US#n] whose story carries neither) on the idea route, excluding [UC#n]/[SM#n]/[SMC#n] on either — against code (code-grounder) and an exported design frame set (design-grounder), independently re-derives every live finding (grounding-verifier, Opus), and, on the BRD route, assigns each finding a current/will-change horizon against declared prerequisite BRDs (--depends-on; refused on the idea route, which has no decision register to freeze one against). Read-only against every repository. Grounds on the shipped product documentation when $DOCS_PATH resolves (off with --no-docs, and under --no-code) — as a lead and a divergence finding, NEVER as evidence for a [CG#n]. --no-code adds design grounding over an already-verified code grounding without re-deriving it; --derivation-matrix adds an implementation-altitude build list; --rebaseline re-runs against moved code, superseding findings by ID. Offers /brd-split on the BRD route; on the idea route, /create-ard and /specify, with /update-prd named first wherever a requirement claim came back CONFIRMED.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Ground the BRD's requirement inventory against code and design: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/prd-ground` is the **BRD-to-PRD route's grounding step** (PA phase), run once per slice
`/brd-split` carves — and **again on an already-ground slice a later re-cut gave a new row**, the third of the three cases `commands/brd-split.md` Phase 7 distinguishes when it offers this command, because no `[CG#n]` on file was derived against a row that arrived after them — it takes the `[BR#n]` inventory that slice's own `brd/brd-inventory.md`
holds and checks its premises against real code and real design assets, at pinned commits, rather
than letting a plausible-sounding claim stand unverified. Every
finding is independently re-derived by a different agent before it counts as evidence
(`workflows-core:grounding-format` §8) — this command's whole job is to make
that discipline happen, not to ground anything itself.

Usage: `/prd-ground <KEY> [--depends-on <BRD-KEY>…] [--derivation-matrix|--no-derivation-matrix] [--no-code] [--no-design] [--no-docs] [--docs <path>] [--rebaseline] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

`<BRD-KEY>` still resolves through `resolve-address`, which searches every level
`workflows-core:addressing` §3 bounds — three below `specifications/` — and so returns a BRD that owns
its source document, one of its slices, an idea-route PRD folder or an Epic folder alike, because a
root must be resolved before Phase 0 step 5a can refuse it by name. **A root BRD is never
ground: it is refused, and grounding happens at a `PRD-` folder — on the BRD route a slice**, over
the requirements that slice's own inventory claims, **or an idea-route PRD folder**, over its PRD's
own rows.

**Standing rule, stated in full at Phase 4.5 and binding on every phase: documentation is a lead
and a divergence finding — it is NEVER evidence for a `[CG#n]`.** No finding this run writes may
cite a documentation page in its `evidence`, under any verdict. A document is a claim *about*
behaviour, not the behaviour.

**`--no-code` is a run mode, not a step skip.** It exists so a BRD whose code grounding is already verified can gain the design grounding it is missing — the state `/brd-split`'s design-presence gate reports — without re-deriving what is already on file. Under it, **`<BRD-dir>/grounding/code-grounding.md` is read-only for the whole run**: this invocation produces no `[CG#n]` at all, its finding set is the new `[DG#n]` only, and every `[CG#n]` already on file keeps the verdict, evidence and verifier outcome it carries — never renumbered by Phase 5, never re-dispatched by Phase 7, never rewritten by Phase 8. Phases 1 and 3 still run in full, because a class-4 `[DG#n]` is pinned to the commit of the `[CG#n]` it cites and Phase 7 re-derives it against that repository. Documentation grounding is off for this run, and so is the derivation matrix: Phase 8 appends both into that same read-only file. Four flag states are refused rather than reconciled, all in Phase 0 step 2.

---

## Phase 0 — Resolve inputs and gate on main

1. **`<BRD-KEY>` (mandatory).** **Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. Parse the first token that is neither a flag nor a flag's value — `--depends-on` and `--docs` each consume the token after them (step 2), and a value skipped as "non-flag" would be read as the key; validate with `key-valid`
   (`workflows-core:addressing` §1). If absent or invalid, stop:
   `PRD_GROUND_NEEDS_KEY: /prd-ground needs a key (shape ^[A-Z][A-Z0-9_]*(-\d+)+$) — re-run '/product-workflows:prd-ground <KEY>'.`
2. **Flags.** `--depends-on <BRD-KEY>` — repeatable, each consuming the next token; validate each
   with `key-valid` and drop (warn, do not stop the run) any that fail shape. **Refused outright on
   `route: idea`** — deferred to immediately after step 5a resolves the route, for the same reason
   the fourth `--no-code` refusal below waits for the resolved folder: the route is not known until
   then. Phase 6 only ever sets `horizon: will-change` from a declared prerequisite's **frozen**
   `status: decided` record, and the idea route has no decision register anywhere to hold one, so
   every finding on it is `current` whatever this flag names. Accepting the flag there and quietly
   doing nothing with it would leave a documented flag with a stated effect that never happens —
   that shape is its own defect and is refused rather than silently degraded:
   `PRD_GROUND_NO_PREREQUISITES: --depends-on names a prerequisite BRD whose frozen decisions set a finding's will-change horizon, and <KEY> is on the idea route, which has no decision register to read. Drop the flag and re-run; every finding on this route is horizon: current.`
   `--no-design` —
   boolean, skips Phase 5's `design-grounder` step. `--no-docs` — boolean, turns documentation
   grounding off for this run (Phase 1 step 0, Phase 4.5). `--docs <path>` — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`; **strip the flag and its value together** before any remaining-argument classification, or the path is read as part of the address. Declared for every consumer by `workflows-core:docs-grounding` *Procedure* step 1 (*Flags first*), which resolves it; this command only has to recognise it and pass the invocation through. `--rebaseline` — boolean, see Phase 3. `--derivation-matrix`
   / `--no-derivation-matrix` — mutually exclusive; absent means "let Phase 8 decide the default".
   `--no-code` — boolean, the **run mode** stated above the phases. Its four refusals are checked
   here, before anything expensive runs:
   - With `--no-design`, nothing is left to ground:
     `PRD_GROUND_NOTHING_TO_GROUND: --no-code and --no-design together leave this run nothing to ground — drop one and re-run '/product-workflows:prd-ground <KEY>'.`
   - With `--rebaseline`, which supersedes `[CG#n]` findings by id — a write this mode forbids:
     `PRD_GROUND_NO_CODE_REBASELINE: --rebaseline supersedes [CG#n] findings by id, which --no-code forbids — re-run '/product-workflows:prd-ground <KEY> --rebaseline' without --no-code to re-ground the moved code, or drop --rebaseline to add design grounding over what is already on file.`
   - With an **explicit** `--derivation-matrix`, which Phase 8 appends into `code-grounding.md`:
     `PRD_GROUND_NO_CODE_MATRIX: the derivation matrix is appended to grounding/code-grounding.md, which --no-code forbids writing — re-run '/product-workflows:prd-ground <KEY> --derivation-matrix' without --no-code.`
     An explicit `--no-derivation-matrix` is redundant here but harmless; an unset default resolves
     **off** under this mode and is reported rather than left silent.
   - Where there is no verified code grounding to build on. This one needs the resolved folder, so
     take it immediately after step 5a rather than here — **after**, never before. **Not only on a
     slice, though**: step 5a refuses every root it can identify as one, but the interrupted-intake
     folder passes it unrefused (`coverage-ledger-format.md` §5.1) and reaches this check too, before
     step 6 would otherwise name it properly. It fails here the same way an under-grounded slice
     does, and the redirect it gives still lands on step 6's own stop for that folder on the next
     run. Stop when
     `<BRD-dir>/grounding/code-grounding.md` is absent, holds no `[CG#n]`, or holds one carrying no
     verifier `outcome`. The third is the state `/brd-split` itself refuses
     (`workflows-core:grounding-format` §8), so reporting it now costs one read and saves a whole
     design pass that still could not split:
     `PRD_GROUND_NO_CODE_UNGROUNDED: --no-code adds design grounding over an existing code grounding, and <KEY> has <no code grounding on file | no [CG#n] findings | N of M [CG#n] findings carrying no verifier outcome> — re-run '/product-workflows:prd-ground <KEY>' without --no-code.`

   **Every flag but `--depends-on` carries over unchanged, on either route, including every refusal
   combination above** — stated here rather than left for a reader to infer from silence;
   `--depends-on` is the one route-bound flag, refused on `route: idea` at the top of this step. `--no-design`,
   `--no-docs`, `--docs <path>`, `--rebaseline`, and `--derivation-matrix`/`--no-derivation-matrix`
   test only one another and the resolved folder's own grounding files, never a BRD-route artifact,
   so none of them needs a route branch of its own. The one worth looking at rather than assuming is
   this step's own fourth `--no-code` refusal, immediately above: it is route-agnostic already, and
   correctly so — it reads `<BRD-dir>/grounding/code-grounding.md`, which
   `workflows-core:grounding-format` already treats as route-neutral, and
   `PRD_GROUND_NO_CODE_UNGROUNDED`'s own text names no ledger, no inventory, and no `brd-link.md`;
   `<KEY>` there is this step's running placeholder for whichever key resolved, on either route. It
   sits among ledger-shaped neighbours only because of where the level question happens to fall in
   this file, not because of anything it tests.
3. **`$SPECS_PATH` (required).** If unset, stop naming `SPECS_PATH`, per the
   `Required path environment variable unset` rule in `workflows-core:escalation-rules`:
   ```
   choices: ["Set SPECS_PATH (enter the path)", "Cancel"]
   ```
4. **Specs-repo preflight.** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline, **before** the gate below — `require-on-main`
   performs no fetch of its own (`workflows-core:phase-handoff` §3.2) and relies on this step's best-effort
   one, the same ordering `/design` Phase 0 uses and for the same reason. Prompt-free and silent
   when the specs repo is clean and on its default branch. If it returns `specs_git: blocked`
   (§3.3 G0), carry that flag for the whole run.
5. **Resolve the BRD folder.** `resolve-address <BRD-KEY>` (`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3), which searches
   every level `workflows-core:addressing` §3 bounds — three below `specifications/`, plus §5's legacy fallback — and so can return any folder kind it finds there: a `BRD-` folder directly under `specifications/`, a `PRD-` folder (a slice inside a BRD, or an idea-route PRD folder), or an `EPIC-` folder inside a `PRD-` folder. Step 5a answers the level question on what it returns.
   Absent → stop, without asserting which command would create it: no folder exists, so no
   `brd-link.md` exists either, and nothing on disk says whether this key names a BRD with a source
   document, a slice of one, or an idea-route PRD folder never authored. Naming `/brd-intake`
   unconditionally would be the wrong advice for two of those three cases, exactly as it is in step
   6's `absent` branch below:
   `PRD_GROUND_NOT_FOUND: no folder found for <BRD-KEY> under $SPECS_PATH/specifications/ (every level addressing.md §3 bounds, plus §5's legacy fallback) — check the key. A BRD with a source document of its own is created by /product-workflows:brd-intake <BRD-KEY> @<brd-file>; a slice is created by /product-workflows:brd-split on its parent; an idea-route PRD folder is created by /product-workflows:create-prd <KEY>. Do not run /brd-intake on a slice or on an idea-route PRD key; neither has a source document of its own.`
5a. **The level refusals, and the route fork — a root BRD is never ground: grounding happens at a
    `PRD-` folder, a slice or an idea-route PRD folder, and its claim source forks by which route
    produced it.** Take this the moment step 5
    returns a resolved folder, before step 6 opens anything and before step 2's deferred `--no-code`
    check — the level question is answered before any flag-combination question, because a root or
    an Epic is refused whatever flags it carries. Test the **resolved directory's
    prefix**: `BRD-` is a root, `PRD-` is a slice — the kind-prefix convention
    `workflows-core:addressing` §2 fixes, read off the resolved folder's own name. **Never test the
    folder's asserted `kind:`** — `/brd-split` writes `kind: brd` into the `brd-link.md` it places
    inside the `PRD-` slice folder it carves (`commands/brd-split.md` Phase 3), so a slice
    **asserts** `brd` while being exactly the folder this refusal must accept; a gate on the
    asserted kind would refuse every slice and accept nothing.

    **An `EPIC-` folder is refused on the same prefix test, and deliberately not on whether it
    holds a `prd.md`.** `resolve-address` searches every level `workflows-core:addressing` §3
    bounds, so a bare Epic key resolves to a folder of its own — one that holds no `prd.md` at all,
    because §2's tree places the PRD one level *up* from any `EPIC-` folder, never inside it. A
    `prd.md`-presence test would misfire here on the one thing this whole file keeps saying not to
    trust: **the absence of a file is not evidence of a kind**, only its presence or its asserted
    `kind:` is, and the run that would ever create a `prd.md` inside an `EPIC-` folder is
    `/product-workflows:create-prd`, never this one — so a test keyed to that absence would let an
    `EPIC-` key fail downstream with a message about a missing file instead of one about the wrong
    altitude. Grounding is PRD-altitude on both routes, so the refusal is the same directory-prefix
    test as `BRD-`'s, taken at the same moment.

    **Where the folder resolved through `workflows-core:addressing` §5's legacy unprefixed fallback,
    there is no prefix to test.** Answer the root question by **positive evidence, never by the
    absence of a file** — `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5.1, the
    shared authority every consumer of this test in this plugin takes it from, directly or through
    `workflows-core:addressing` §4.1, and not restated here — and the Epic question the same way, as
    `workflows-core:addressing` §4.1 places a folder with no prefix: a resolved `kind: epic` is an
    Epic folder, refused below exactly as an `EPIC-` folder is.

    On a root, look for the root-level artifacts this run would have produced under the retired
    two-level model — `grounding/code-grounding.md`, `grounding/design-grounding.md`,
    `grounding/baselines.md` — and name whichever exist in the stop, so an operator whose BRD was
    ground under that model is told the level moved rather than that their key is wrong. Never
    delete them; they record work done, and nothing in this run reads them.

    Stop, on a root:
    `PRD_GROUND_ROOT_LEVEL: <BRD-KEY> is a root BRD, and grounding happens at the slice. Carve one with '/product-workflows:brd-split <BRD-KEY> "<how to cut it>"', then run '/product-workflows:prd-ground <SLICE-KEY>'.<where root-level grounding exists, append:> This BRD carries root-level grounding at <paths> from the earlier two-level model; it is left in place, and this command never reads it.`

    Stop, on an Epic folder:
    `PRD_GROUND_EPIC_LEVEL: <KEY> resolves to an Epic folder, and grounding is PRD-altitude on both routes. Run '/product-workflows:prd-ground <PRD-KEY>' against the PRD folder this Epic sits in.`

    **Once past both refusals, set the run's route — again by positive evidence in both directions,
    never by the absence of a file, the same discipline the root question above already applies:**

    - **The resolved directory carries `brd-link.md` → `route: brd`.** Every existing Phase 0 step
      below applies exactly as it always has, over that BRD's own `[BR#n]` inventory. This test
      alone already resolves a legacy **slice** too: §5.1's own table only ever puts `brd-link.md`
      carrying `parent:` beside a ledger file on a legacy folder that is a slice, so a legacy slice
      reaches `route: brd` here without a separate test of its own.
    - **A `PRD-` directory with no `brd-link.md`, nested directly inside a BRD folder → stop, on
      one of two stops.** Test the resolved directory's **parent** directory by the root question
      above, applied to it: a `BRD-` prefix, or — where the parent is unprefixed, a legacy folder —
      `coverage-ledger-format.md` §5.1's positive evidence, the same test the root question takes
      for an unprefixed folder. `workflows-core:addressing` §2 places an idea-route PRD folder
      directly under `specifications/` and a slice inside its BRD, so a `PRD-` folder inside a BRD
      is a slice by where it sits — positive evidence, never the absence of a file — and one with no
      `brd-link.md` is not a slice this run can read: taking `route: idea` would name `/create-prd`
      and author a PRD inside a BRD, and no `/brd-split` run enumerates it, since that command's
      Phase 0 step 9 finds a child by its `brd-link.md`. `<PARENT-KEY>` is the `key:` the parent
      folder's `coverage-ledger.md` records; where that cannot be read, name the parent folder by path
      and no `/brd-split` form. **Which stop turns on what the folder holds, never on the missing
      file alone**:
      - **The folder holds nothing at all** — the one state that is positive evidence of a carve
        interrupted between `/product-workflows:brd-split` Phase 3 step 2, which creates the folder,
        and step 3, which writes `brd-link.md` as the first file in it. That command writes no file
        into a slice before `brd-link.md`, so there is no third state of "only the files it writes
        before that one". Git records no empty directory, so the folder was never
        committed. Stop:
        `PRD_GROUND_CARVE_INTERRUPTED: <KEY> resolves to <path>, an empty PRD- folder inside the BRD folder <parent path> — the /product-workflows:brd-split run that created it stopped before writing its brd-link.md, so it is neither a slice nor an idea-route PRD folder, and nothing was written. Delete the empty folder, then re-run '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"'. Do not run /product-workflows:create-prd on it.`
      - **The folder holds anything** — a ledger, an inventory, `grounding/`, `decisions.md`, or any
        other file. That is most often a slice whose `brd-link.md` was lost after it was written, and
        whatever it holds may be grounding, decisions and rounds nothing else records, so **never
        name its removal**. Look for `brd-link.md` on a ref:
        `git -C "$SPECS_PATH" log --all --diff-filter=AM --format=%H -1 -- <path>/brd-link.md` names
        the newest commit on any ref that wrote it, whose tree therefore holds it. Name what the file must say, off records rather than prose:
        `kind: brd`, `key: <KEY>`, `parent: <PARENT-KEY>`, and as `claims:` the `[BR#n]` of every row
        of `<PARENT-KEY>`'s ledger whose `disposition` reads exactly `covered-by: <KEY>`. Stop:
        `PRD_GROUND_LINK_MISSING: <KEY> resolves to <path>, a slice folder inside the BRD folder <parent path> that holds <what it holds> and has no brd-link.md, so it cannot be read as a slice, and nothing was written here. <where a ref holds it:> Restore brd-link.md from commit <commit>, then re-run '/product-workflows:prd-ground <KEY>'. <where none does:> No ref holds it: report it, or re-create it by hand as kind: brd, key: <KEY>, parent: <PARENT-KEY>, claims: [<ids>] — the rows <PARENT-KEY>'s ledger delegates to this slice — then re-run. Do not delete this folder, and do not run /product-workflows:create-prd on it.`
    - **Any other `PRD-` directory with no `brd-link.md` → `route: idea`.** `/brd-split` is the only
      writer of a `brd-link.md` naming a `parent:` inside a `PRD-` folder; this command's own Phase 4
      writes `depends-on:` into one but never introduces a `parent:`. A `PRD-` folder that sits
      outside every BRD folder and carries no `brd-link.md` at all was therefore never carved from
      a BRD — it is `/product-workflows:create-prd`'s own output, unprompted by any slice, and its claims come from its own `prd.md` (step 6i, step 8i, below).
    - **Resolved through §5's legacy unprefixed fallback, and past the root question above** — there
      is still no prefix to test, and the `brd-link.md` test just above has already resolved a
      legacy slice to `route: brd`. What is left unresolved is exactly the shape §5.1 calls "a legacy
      idea-route PRD folder" — neither `coverage-ledger.md` nor `brd/brd-inventory.md`, and, by that
      shape's own definition, no `brd-link.md` either — and that shape is **not** automatically
      `route: idea`: a legacy folder holding only an `idea.md`, say, is no PRD folder yet, and step 6
      below still has to report it. **Split it on `prd.md` being
      present and asserting `kind: prd` — positive evidence each way, never the absence of a file,
      exactly the rule this step already applies to the root question above.** Present →
      `route: idea`, and step 6i gates that file instead of step 6's ledger branch ever opening.
      Absent, or present without `kind: prd` → step 6's no-link branch, unchanged in where it sends
      the run: nothing here has told that branch its folder is settled, so it still has to ask.
      **Where that folder holds an `idea.md` and no `prd.md`** — the folder the idea route handed an
      idea off into before the kind prefixes, which `workflows-core:addressing` §5 resolves on its
      name alone — each no-link stop in step 6 appends its `/product-workflows:create-prd <KEY>`
      clause: that command accepts the folder (its Phase 0 steps 5a and 5b refuse only a container and
      an Epic folder) and writes the `prd.md` whose `kind: prd` sets `route: idea` here on the re-run,
      which is what `PRD_GROUND_NEEDS_PRD` names for a `PRD-` folder in the same state.
6. **On `route: brd`, gate this BRD's own inventory and ledger on main.** (The idea route's own
   gate is step 6i, immediately below — this whole step is the `route: brd` branch, unchanged.)
   **The two gates below resolve in a fixed order: the ledger's first, the inventory's second.**
   `coverage-ledger.md`'s `require-on-main` return is resolved in full first — on its row F that
   includes whether the file is in the folder at all — and only then is `brd/brd-inventory.md`'s
   gate evaluated and its stop printed. Where both returns stop, the ledger's stop is the one
   printed, **with one exception**: where the ledger is in the folder and on no ref — its row-F
   branch (b) below — and `brd/brd-inventory.md` is not in the folder, the inventory's own
   `PRD_GROUND_NO_INVENTORY` stop is printed instead. Branch (b) reconciles a slice against its
   parent, and a slice missing a file cannot be reconciled — `/brd-split`'s reconcile step writes
   nothing into one (`commands/brd-split.md` Phase 4 Step 3) — so every branch (b) stop would name a
   remedy that cannot work there, while the inventory's stop names the one that can. Otherwise the
   order is not arbitrary: the ledger's row-F branch (a) below disposes of an inventory an
   interrupted carve left behind, so an inventory stop printed first would name the wrong remedy for
   that folder.
   Execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against the resolved BRD folder's `coverage-ledger.md`. Whichever
   command wrote that ledger wrote the inventory beside it in the same handoff commit
   (`coverage-ledger-format.md` §3's creator table). **That is a fact about the run that wrote them
   and not about the tree, so execute `require-on-main` against `brd/brd-inventory.md` as well
   rather than inferring it** (`workflows-core:phase-handoff` §4.0 — never infer an artifact's
   merged-ness from a sibling's gate). Step 8 stops on that inventory being empty and builds this
   run's whole claim list from it, so the stop and the claim list both depend on reading the one that
   is actually shared; a hand-committed set can land partially, which `/brd-reconcile`'s §3.4 row
   states outright. Map its return exactly as the ledger's below, **except
   for row F, which needs its own two-branch stop and must not borrow step 8's.** Step 8's
   `PRD_GROUND_EMPTY_INVENTORY` reports a *content* fact — the inventory holds no `[BR#n]` row — and
   its remedy re-runs `/brd-split` on `<PARENT-KEY>` to resolve the standing empty child. Row F reports a
   *merge* fact, and sending that operator to `/brd-split` on the parent risks the same no-op the
   next split below refuses to name unconditionally — a fully-allocated parent whose children all agree with its ledger stages nothing on a **bare** re-run.
   Split it on the same test the
   ledger's own row F uses — is the file in the folder at all:
   - **No `brd/brd-inventory.md` in the folder** — and, under the gate order above, a
     `coverage-ledger.md` in it, save in one state: this stop prints only where the ledger's gate
     passed or under the gate order's one exception, where the ledger is in the folder and on no ref,
     and the only pass that leaves no ledger in the folder is `require-on-main`'s row B — the ledger
     on the default branch, missing from a working tree on a branch this run reuses
     (`workflows-core:phase-handoff` §3.3). Every other state with no ledger in the folder reaches
     the ledger's own row F first. Either way the ledger was written, so on a slice the inventory
     was written and lost —
     `/brd-split` writes a slice's inventory before its ledger (`commands/brd-split.md` Phase 3). Read the resolved folder's
     `brd-link.md` and branch on its `parent:` field: 5a's own legacy-fallback test lets a folder
     that is not a slice through unrefused (`coverage-ledger-format.md` §5.1), so a folder reaching
     this branch is not always the slice step 5a would otherwise guarantee. Since product-workflows 3.7.0 `/brd-intake` writes the
     inventory's header before it copies anything (`brd-format.md` §2); a folder an earlier intake
     left with `brd/source/` alone carries neither BRD file, and `/brd-intake` refuses it too, so the
     remedy is the same.
     - **No `brd-link.md`, or one with no `parent:`** — not a slice with a `<PARENT-KEY>` to read,
       and not a BRD container either: it carries neither BRD file, or is a `PRD-` folder whose
       `brd-link.md` names no `parent:`, which no command writes. `/brd-intake` re-runs only over a
       container (`workflows-core:addressing` §4.1) and refuses this folder with
       `BRD_INTAKE_NOT_A_BRD`, so name no re-run over it — and, where the folder holds an `idea.md` and
       no `prd.md`, name `/create-prd` on this key (step 5a). `<what it carries>` is the folder's
       top-level files and subdirectories, as read. Stop:
       `PRD_GROUND_NO_INVENTORY: <BRD-KEY> resolves to <path>, which carries <what it carries> and has no brd/brd-inventory.md and no brd-link.md naming a parent — it is not a slice, and not a BRD container /product-workflows:brd-intake would re-run over. Nothing was written. To intake a customer's BRD, run '/product-workflows:brd-intake <NEW-KEY> @<brd-file>' with a key no folder under $SPECS_PATH/specifications/ asserts; this folder is left exactly as it stands.<where the folder holds an idea.md and no prd.md, append:> It holds an idea.md and no prd.md, so the idea route goes on from it: run '/product-workflows:create-prd <BRD-KEY>', merge its handoff, then re-run '/product-workflows:prd-ground <BRD-KEY>'.`
     - **`parent: <PARENT-KEY>` present** — this is a slice. Stop:
       `PRD_GROUND_NO_INVENTORY: <BRD-KEY> is a slice of <PARENT-KEY> and has no brd/brd-inventory.md, so there is no claim list to ground. <remedy>`

       **`<remedy>` is conditional, exactly as `PRD_GROUND_NEEDS_SPLIT`'s below is, because a
       parent re-run never re-creates a slice's missing file** (`commands/brd-split.md` Phase 4's
       reconcile step reconciles every standing child against the parent's ledger, but writes
       nothing into one with its inventory or ledger missing). Read this slice's `brd-link.md` `claims:`
       and `<PARENT-KEY>`'s own `coverage-ledger.md`, and take the first row that matches:

       | State | `<remedy>` |
       |---|---|
       | This slice's `claims:` names no `[BR#n]` | It claims nothing — the standing-empty-child state step 8's `PRD_GROUND_EMPTY_INVENTORY` reports — so give that stop's remedy unchanged, which already names the `/brd-split` form by the parent's ledger |
       | It claims rows, and its folder holds no `coverage-ledger.md` — reached only through `require-on-main`'s row B above — the ledger on the default branch and missing from this working tree — since the gate order sends every other no-ledger state to the ledger's own row F | `This slice's coverage-ledger.md is on the specs repo's default branch but missing from this working tree, and its brd/brd-inventory.md is missing too. Restore coverage-ledger.md from the default branch. No command re-creates the inventory — /product-workflows:brd-split's reconcile step writes nothing into a slice with a file missing — so restore it from the ref that carried it, or report it; then re-run '/product-workflows:prd-ground <BRD-KEY>'.` |
       | It claims rows, and `<PARENT-KEY>`'s ledger still holds an `unallocated` row | `A parent re-run will not repair this file. '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"' still has rows to walk, but its reconcile step writes nothing into a slice with a file missing, and never re-creates one. The file was lost after it was written, and no command re-creates the rows it held — restore it from the ref that carried it, or report it.` |
       | It claims rows, and `<PARENT-KEY>`'s ledger holds no `unallocated` row | `A parent re-run carves nothing here: the bare '/product-workflows:brd-split <PARENT-KEY>' writes nothing into this slice — its reconcile step leaves a slice with a file missing untouched — and an instructed one's reconcile step leaves it untouched too, whatever that run re-cuts. The file was lost after it was written, and no command re-creates the rows it held — restore it from the ref that carried it, or report it.` |
       | `<PARENT-KEY>`'s ledger cannot be read | Report it by path and name no `/brd-split` form: which one runs is that ledger's to say |
   - **The inventory is in the folder and on no ref, and so is a `coverage-ledger.md`** — produced, handoff declined. (Where the folder holds no `coverage-ledger.md`, do not print this stop: the gate order this step opens with has already resolved the ledger's own `require-on-main` return — its row F takes branch (a) below, whose never-written row disposes of this inventory.) Land what is
     already on disk, and **name no `/brd-intake` run**: that command refuses a slice
     (`BRD_INTAKE_SLICE`) and any folder that is not a container (`BRD_INTAKE_NOT_A_BRD`), and
     every container was refused as a root at step 5a:
     `PRD_GROUND_INVENTORY_NOT_HANDED_OFF: <BRD-KEY>'s brd/brd-inventory.md is written at <path> but is on no branch — its handoff was declined. Commit and merge it to the specs repo's default branch and re-run. This names no /product-workflows:brd-intake run: that command refuses a slice and any folder that is not a container.` What the single-commit fact still buys is the *rest* of the set: it was
   `/brd-split` running on the parent, and there is no *requirement* defect log to land — a slice
   reads the parent's `brd/brd-defect-log.md` (`brd-format.md` §2.1), and the slice-owned
   `code-defect-log.md` is a different register this phase's set never held.
   Map the §3.7 return by `stopped` first: any stopping row → stop, naming
   the concrete branch/PR state it reports; `pass` → proceed; `pass_amending` → proceed, printing
   the §3.3 row-B message; `unmanaged` → proceed as before this feature.

   **`absent` (row F) — nothing for this BRD is on any ref — is split twice before it is reported.**
   Row F conflates three states: *never produced*, *lost after it was written* and *produced, handoff declined*. Reported as one,
   the message tells an operator whose files are already written to go and produce them — and on a
   slice it names `/brd-split`, which **re-run bare** in that state does not land those files as they
   stand. Split row F **first on whether `coverage-ledger.md` exists in the worktree**,
   then by level — reading the resolved folder's `brd-link.md` from the worktree (it is there whether
   or not anything reached main) and branching on its `parent:` field, because a slice must never be
   told to run a command that would refuse it.

   **(a) No `coverage-ledger.md` in the folder — never produced, or lost after it was written; the table below tells them apart.** Read `brd-link.md`, if
   present, and branch on its `parent:` field: 5a's own legacy-fallback test lets a folder carrying
   **neither** `coverage-ledger.md` **nor** `brd/brd-inventory.md` through unrefused
   (`coverage-ledger-format.md` §5.1), so a folder reaching this branch is not always the slice
   step 5a would otherwise guarantee — and, as step 6's inventory branch above says, one an intake
   earlier than product-workflows 3.7.0 left with `brd/source/` alone is refused by `/brd-intake`
   too, so the remedy is the same.
   - **No `brd-link.md`, or one with no `parent:`** — not a slice and not a BRD container, so
     `/brd-intake` refuses it with `BRD_INTAKE_NOT_A_BRD` rather than re-running over it; name a new
     key instead — and, where the folder holds an `idea.md` and no `prd.md`, `/create-prd` on this
     one (step 5a) — `<what it carries>` being the folder's top-level files and subdirectories, as read.
     Stop:
     `PRD_GROUND_NEEDS_INTAKE: <BRD-KEY> resolves to <path>, which carries <what it carries> — no intake artifacts on main and none in the folder either, and no brd-link.md naming a parent. It is not a slice, and not a BRD container /product-workflows:brd-intake would re-run over. Nothing was written. To intake a customer's BRD, run '/product-workflows:brd-intake <NEW-KEY> @<brd-file>' with a key no folder under $SPECS_PATH/specifications/ asserts and merge the pull request; this folder is left exactly as it stands.<where the folder holds an idea.md and no prd.md, append:> It holds an idea.md and no prd.md, so the idea route goes on from it: run '/product-workflows:create-prd <BRD-KEY>', merge its handoff, then re-run '/product-workflows:prd-ground <BRD-KEY>'.`
   - **`parent: <PARENT-KEY>` present** — this is a slice, and `/brd-intake` is not the fix: a
     slice has no document of its own to intake (`brd-format.md` §2.1), and the command that writes
     a slice's ledger and inventory is `/brd-split` on the parent
     (`coverage-ledger-format.md` §3). Stop:
     `PRD_GROUND_NEEDS_SPLIT: <BRD-KEY> is a slice of <PARENT-KEY> and its coverage-ledger.md exists on no ref and in no folder. <remedy> Do not run /brd-intake on a slice; it has no source document of its own.`

     **`<remedy>` is conditional, on two of the three reads `PRD_GROUND_NO_INVENTORY`'s takes above** — this
     slice's `brd-link.md` `claims:` and `<PARENT-KEY>`'s own `coverage-ledger.md` — because which
     `/brd-split` run changes anything depends on both. The third, whether a `coverage-ledger.md`
     stands in this slice's folder, this branch has already answered: none does. Take the first row that matches:

     | State | `<remedy>` |
     |---|---|
     | This slice's `claims:` names no `[BR#n]` | It claims nothing — a standing empty child, which a parent re-run resolves in either form — so give step 8's `PRD_GROUND_EMPTY_INVENTORY` remedy unchanged, which names the `/brd-split` form by the parent's ledger |
     | It claims rows, none of them reads `covered-by: <this slice's key>` on `<PARENT-KEY>`'s ledger, and at least one still reads `unallocated` there | `Nothing was lost: the /brd-split run on <PARENT-KEY> that carved this slice stopped after writing its brd-link.md and before writing its ledger, so the files it had not reached were never written — and that run reached neither its handoff nor its terminal commit, and neither brd-link.md nor brd/brd-inventory.md is a path the specs repo's bookkeeping commit stages, so no command has committed this slice's folder either. A parent re-run will not finish it: its reconcile step writes nothing into a slice with a file missing, and its walk never offers such a slice a row, so the files that run never reached stay unwritten. Remove this slice's folder — delete it where git reports it untracked, and where it was committed by hand, remove it in a commit on every branch that carries it, the default branch included — then re-run '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"', which places every row still unallocated on <PARENT-KEY>'s ledger, the ones this slice claimed included, as though this slice had never been carved. Removing the folder discards any brd/brd-inventory.md that run had already written into it as well, which loses nothing: it holds only rows copied from <PARENT-KEY>'s own inventory, which still carries every one of them.` |
     | It claims rows, and none of them reads `covered-by: <this slice's key>` or `unallocated` on `<PARENT-KEY>`'s ledger | `Nothing was lost: the /brd-split run on <PARENT-KEY> that carved this slice stopped after writing its brd-link.md, so the files it had not reached were never written, and every row it claims has since been settled elsewhere on <PARENT-KEY>'s ledger, so none is owed here. Its claims: list is left over from that run: empty it by hand in brd-link.md, then re-run /product-workflows:brd-split on <PARENT-KEY>, which offers to remove this slice or keep it against a recorded reason. Which form to type depends on that parent's own ledger: where it still holds an unallocated row, a run with rows still to place needs a slicing instruction, so type '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"'; where none is left, type the bare '/product-workflows:brd-split <PARENT-KEY>'.` |
     | It claims rows, and `<PARENT-KEY>`'s ledger still holds an `unallocated` row | `A parent re-run will not repair this slice's files. '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"' still has rows to walk, but its reconcile step writes nothing into a slice with a file missing, and never re-creates one. The ledger was lost after it was written, with the inventory too where that is missing as well, and no command re-creates the rows they held — restore what is missing from the ref that carried it, or report it.` |
     | It claims rows, and `<PARENT-KEY>`'s ledger holds no `unallocated` row | `A parent re-run carves nothing here — with no row left unallocated there is nothing for an instruction to group — and where that parent holds no re-cuttable row it writes nothing into this slice, whose reconcile step leaves a slice with a file missing untouched: the slice's ledger was lost after it was written, with its inventory too where that is missing as well, and no command re-creates the rows they held — restore what is missing from the ref that carried it, or report it.` |
     | `<PARENT-KEY>`'s ledger cannot be read | Report it by path and name no `/brd-split` form: which one runs is that ledger's to say |

     **The two rows that say the ledger was lost are reached only where some row this slice claims reads `covered-by: <this slice's key>`** — the three rows above them take every other state — and no `/brd-split` walk writes that onto a child missing its inventory or its ledger: its Phase 0 step 9 marks such a child unreconcilable, and every target list of its walk leaves it out. So this slice held its ledger when that row was written, and *lost after it was written* is what the parent's ledger shows rather than a guess.

     **The condition qualifies the remedy, and every row must carry it.** The table once had two branches, both on a slice claiming rows, and so said nothing to a slice claiming nothing under a fully-allocated parent — a standing empty child, the one state here in which a parent re-run acts on this slice whatever the parent's ledger holds. The sibling rule under (b) below — *`/brd-split` is not a way out here, so do not name it* — already says not to name `/brd-split` for a fully-allocated parent, because re-running it **bare** there stages nothing for this slice: its reconcile step leaves a child with a file missing untouched (`commands/brd-split.md` Phase 4 Step 3). Naming it unconditionally here sent the operator to a command that would report success and change nothing, leaving the slice ungroundable with no other route offered — and `coverage-ledger-format.md` rules on this same shape elsewhere with *"name no option at all"* rather than a remedy that cannot work.

   **(b) `coverage-ledger.md` is in the folder, and on no ref — it was produced, and either the carve
   that wrote it has not finished or its handoff was declined.** The file alone cannot tell those
   apart: `/brd-split` writes a slice's three files in its Phase 3, before its Phase 4 walk has placed
   a single row, and reconciles them against the parent's ledger only in that walk's Step 3
   (`commands/brd-split.md`), so a carve stopped anywhere between leaves the same files on disk as a
   finished one whose handoff was declined. **The parent's ledger tells them apart**, so read
   `<PARENT-KEY>`'s own `coverage-ledger.md` from the worktree — `<PARENT-KEY>` being the `parent:`
   of the `brd-link.md` read above — before printing anything, and take the first case that matches. (Where `brd/brd-inventory.md` is not in the folder, the gate order's one exception applies instead, and nothing in this branch prints.)
   - **`brd-link.md` names no `parent:`, or `<PARENT-KEY>`'s ledger cannot be read** — whether the
     carve finished, and whether the handoff was declined, is that ledger's to say, so assert
     neither: print step 6a's unreadable-parent `PRD_GROUND_SLICE_UNRECONCILED`, which reports the
     ledger by path, names no `/brd-split` form, and is the same situation — this slice cannot be
     tested against its parent. Commit nothing in this folder until that ledger is read.
   - **`<PARENT-KEY>`'s ledger holds any `unallocated` row** — the carve is not finished, and the
     message says so by what the ledger shows and never by why: an interrupted `/brd-split` run
     leaves this state, and so does a `/product-workflows:brd-intake` re-run over the parent, which
     resets every row of its ledger to `unallocated` (`coverage-ledger-format.md` §3). Landing these
     files now would land provisional ones, and naming the bare `/brd-split` form would name a run
     that stops with `BRD_SPLIT_NEEDS_INSTRUCTION` while a row is unallocated, so name the instructed
     form. `<N>` is the count of those rows:
     `PRD_GROUND_CARVE_UNFINISHED: <BRD-KEY>'s coverage-ledger.md is written at <BRD-dir> but is on no branch, and its parent <PARENT-KEY>'s coverage-ledger.md still holds <N> unallocated row(s) — the carve of <PARENT-KEY> is not finished, so this slice's brd-link.md, brd/brd-inventory.md and coverage-ledger.md are provisional and may yet change. Commit nothing in this folder until that carve completes: run '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"' to completion — it walks every row still unallocated, then reconciles every child's three files against the parent's ledger — merge its handoff, then re-run '/product-workflows:prd-ground <BRD-KEY>', which names anything of this slice's still left to land.`
   - **No `unallocated` row, but this slice fails step 6a's reconciliation test** — run over this
     folder's worktree copies of the three files, since none is on a ref yet. The parent's ledger is
     allocated, and this slice is still not what it records: a carve stopped after its last walk
     write and before its Step 3 reconciled this slice leaves exactly that. Landing the files would
     land a disagreement, so print step 6a's `PRD_GROUND_SLICE_UNRECONCILED` with the remedy step 6a
     gives for a fully-allocated parent, and not the stop below.
   - **No `unallocated` row, and this slice passes step 6a's test** — the carve finished and its
     handoff was declined. The files exist; what is missing is a commit. **Say so, and name landing
     them as the action.** **It speaks for the ledger only**: the inventory has its own gate above,
     with its own two stops, and this message must not report a merge state it did not test:
   `PRD_GROUND_NOT_HANDED_OFF: <BRD-KEY>'s coverage-ledger.md is written at <BRD-dir> but is on no branch — their handoff was declined, so nothing is missing but the commit. Commit brd/brd-inventory.md and coverage-ledger.md to the specs repo's default branch, then re-run '/product-workflows:prd-ground <BRD-KEY>'. <the clause below>`

   **`/brd-split` is not a way out here, so do not name it.** Re-running it **bare** on a parent whose ledger is fully
     allocated, whose children are non-empty and none of them out of step with it, is a no-op by its own Phase 0
     (`coverage-ledger-format.md` §4): it stages nothing, reports `nothing to commit` and opens no
     pull request. Where some *other* child is out of step, the bare run is live, but it reconciles
     that child and declares only the files it changes (its Phase 6), and this slice — in step, by
     the case that brought the run here — is not one of them. `handoff-to-main` stages only the paths *that* run declared, so the slice's
     already-written files are OTHER to it
     (`workflows-core:phase-handoff` §2.3) and can never reach main by that
     route.

     **Every part of that condition matters, so the clause carries all of it.** A parent re-run is a
     no-op only where its ledger is fully allocated **and** no child is left standing while claiming
     nothing **and** no child is out of step with the parent's ledger **and** no row is re-cuttable
     under an instruction the run was given
     (`commands/brd-split.md` Phase 0 step 10); a standing empty child keeps that run alive through its empty-child phase, which does
     stage a `brd-link.md` it writes a `reason:` into, a child out of step keeps it alive through its
     reconcile step, which stages the files it rewrites for that child, and a re-cuttable row keeps it alive through its
     walk, which stages the receiving child's three files. Read the `claims:` list of the `brd-link.md`
     step 6 already opened for its `parent:` and branch on it, because the two states take different
     clauses and asserting the first over the second would tell an operator a live run does nothing:
     - **This slice claims at least one `[BR#n]`** — the ordinary case, and the bare parent re-run
       writes nothing into this slice: `Re-running the bare /product-workflows:brd-split <PARENT-KEY> will not land them — with this slice claiming rows, in step with the parent's ledger, and that ledger fully allocated, that run writes nothing into this slice and declares none of its files. An instruction typed after the key can still make it a live run, where the parent holds a row a child has recorded it will not build; that run stages what its own walk moved, never these files as they stand.`
     - **This slice claims nothing** — it is a standing empty child, so the parent re-run is not a
       no-op, but a bare one still will not land *these* files: it declares that child's `brd-link.md`, not
       its inventory and ledger. An **instructed** run that re-cuts a row onto this slice is the one form that
       does declare all three, and it lands them as its own walk leaves them rather than as they stand here.
       Say all of it, so the operator is neither sent to a no-op, nor told a
       live run is one, nor left believing no form of that run reaches these files: `Re-running /product-workflows:brd-split <PARENT-KEY> is not a no-op — this slice claims nothing, so that run resolves it. Every row of the parent's ledger is allocated, so the bare form is the run, and it offers to remove it or to keep it against a recorded reason, and it will not land these files: it stages that decision, not this slice's inventory and ledger. Adding an instruction, '/product-workflows:brd-split <PARENT-KEY> "<what to peel off>"', can additionally re-cut onto this slice a row a sibling has recorded it will not build — where such a row exists and this slice has never been interviewed — and that run does stage this slice's inventory and ledger, with the re-cut row added to them. Committing what is already on disk remains the direct route to landing them as they stand.`

   This is the same split `/product-workflows:brd-reconcile` makes on its own row F
   (`BRD_RECONCILE_NEEDS_PACKAGE` versus `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF`), for the same
   reason: *never produced* and *produced but never handed off* are different facts, and a stop that
   collapses them names a command that does nothing in the state it is reporting.
6a. **On `route: brd`, once both of step 6's gates pass, test this slice against its parent — the
    reconciliation test.** The gates prove the slice's ledger and inventory are on main; they cannot prove those
    files, or the `claims:` read beside them, are the allocation that produced them. `/brd-split` writes a slice's three files
    provisionally in its Phase 3 and reconciles them against the parent's ledger in its Phase 4
    Step 3, so a carve stopped between the two leaves files that agree with each other and not with
    the parent — and committing them by hand carries them past both gates.

    **First, both files must be in this working tree.** A gate passes a file on the default branch
    that is missing from the worktree where this run reuses a branch of its own —
    `require-on-main`'s row B (`workflows-core:phase-handoff` §3.3) — and this step, like Phase 8's
    `evidence` rebuild, reads the worktree. A missing inventory would read as set (b) empty and print
    the stop below, whose remedy names `/brd-split`, which writes nothing into a slice with a file
    missing (`commands/brd-split.md` Phase 4 Step 3), so that remedy would loop. Where
    `brd/brd-inventory.md`, `coverage-ledger.md` or both are not in the folder, stop instead, naming
    each missing one (a file in the folder that cannot be read is the stop after this one):
    `PRD_GROUND_RESTORE_FROM_DEFAULT: <BRD-KEY>'s <missing file(s)> <is|are> on the specs repo's default branch but missing from this working tree, on the branch this run reuses — nothing here can be tested against its parent or ground from a file that is not on disk, and nothing was written. Restore <it|them> from the default branch, then re-run '/product-workflows:prd-ground <BRD-KEY>'. No /product-workflows:brd-split run re-creates either file.`

    **Then both must be readable.** A gate tests a file's presence and its bytes against a ref,
    never whether this run can read it, so a `coverage-ledger.md` or `brd/brd-inventory.md` that is
    in the folder and cannot be read — a permission fault, a file that is not text — passes both.
    Read unread, the inventory would empty set (b) and send the operator to `/brd-split`, which marks
    this slice unreconcilable and writes nothing into it; the ledger no set here reads would fail
    only at Phase 8's `evidence` rebuild, after the whole run's spend. Stop here instead, naming each
    such file and the read error:
    `PRD_GROUND_SLICE_FILE_UNREADABLE: <BRD-KEY>'s <file(s)> at <path(s)> <is|are> in the folder but cannot be read (<error>), so nothing here can be tested against its parent or ground, and nothing was written. Repair the file — its permissions, or restore it from the ref that carried it — then re-run '/product-workflows:prd-ground <BRD-KEY>'. No /product-workflows:brd-split run repairs it: that command writes nothing into a slice whose inventory or ledger cannot be read.`

    Read three sets of
    `[BR#n]` ids, each off a structured field and never out of prose:
    - **(a)** the entries of this slice's `brd-link.md` `claims:`, read id by id as
      `brd-format.md` §2.1 fixes — a legacy bare or unquoted entry names the same id;
    - **(b)** the `id` of every row of `brd/brd-inventory.md`;
    - **(c)** the `id` of every row of `<PARENT-KEY>`'s own `coverage-ledger.md` (the `parent:` of
      that `brd-link.md`, read from the worktree) whose `disposition` reads exactly
      `covered-by: <BRD-KEY>` — the whole value equal to that string, never a prefix of it, so a
      sibling whose key merely begins with this one's is not counted.

    Every `/brd-split` run that completes leaves the three equal for every child it leaves standing
    with both its inventory and its ledger, because its Phase 4 Step 3 reconciles each against the
    parent's ledger on every path that does not end as a no-op, and the no-op is taken only where no
    child is out of step. A child missing one of those files is never reconciled — and this test
    cannot see every such child, since a missing inventory empties set (b) while a missing ledger
    empties none of the three — which is why step 6's inventory gate and ledger gate report it
    wherever the file is not on the default branch, and this step's worktree check above reports it
    wherever the file is, before any set is read. So where they
    are equal, proceed. **This step never runs on `route: idea`**: that route has no `brd-link.md`,
    no inventory and no parent, and step 6i is its whole gate.

    Where `brd-link.md` names no `parent:`, or `<PARENT-KEY>`'s ledger cannot be read, stop
    reporting it by path and naming no `/brd-split` form, since which form reconciles this slice is
    that ledger's to say. `<path>` is that ledger's path, and reads `no parent: named in brd-link.md`
    where there is no `parent:` to resolve one from:
    `PRD_GROUND_SLICE_UNRECONCILED: <BRD-KEY> cannot be tested against its parent: the parent's ledger at <path> cannot be read, and which /product-workflows:brd-split form reconciles this slice is that ledger's to say — report it; no form is named here.`

    Otherwise, where the three sets are not all equal, stop, naming each id by the set that lacks
    it — print only the clauses whose list is non-empty:
    `PRD_GROUND_SLICE_UNRECONCILED: <BRD-KEY> is out of step with its parent <PARENT-KEY>'s coverage-ledger.md, so its files are not the allocation that ledger records and nothing here is ground. <Its brd-link.md claims: lacks [ids].> <Its brd/brd-inventory.md lacks [ids].> <<PARENT-KEY>'s ledger does not read covered-by: <BRD-KEY> on [ids].> <remedy>`

    `<remedy>` turns on the parent's ledger, because the bare form stops with
    `BRD_SPLIT_NEEDS_INSTRUCTION` while any row there is `unallocated`:
    - **Any row reads `unallocated`** — `The parent's ledger still holds <N> unallocated row(s), so its carve is not finished: run '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"' to completion — it walks those rows, then reconciles every child's brd-link.md, brd/brd-inventory.md and coverage-ledger.md against the parent's ledger — merge its handoff, then re-run '/product-workflows:prd-ground <BRD-KEY>', which names anything of this slice's still left to land.`
    - **None does** — `Every row of the parent's ledger is allocated, so run the bare '/product-workflows:brd-split <PARENT-KEY>': it reconciles every child's brd-link.md, brd/brd-inventory.md and coverage-ledger.md against that ledger and writes nothing for a child already in step. Merge its handoff, then re-run '/product-workflows:prd-ground <BRD-KEY>', which names anything of this slice's still left to land.`
6i. **On `route: idea`, gate `prd.md` on main instead — there is neither a ledger nor an inventory
    on this route.** Execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3)
    against `<PRD-dir>/prd.md`. Map its §3.7 return by `stopped` first, exactly as step 6 does for
    the BRD route: any stopping row → stop, naming the concrete branch/PR state it reports;
    `pass` → proceed; `pass_amending` → proceed, printing the §3.3 row-B message; `unmanaged` →
    proceed as before this feature.

    **The gate is here, not skipped, for the reason step 6 already gates the ledger: a claim list
    read off an unmerged artifact produces a finding set nothing downstream can reproduce.**
    `/product-workflows:create-ard` and `/product-workflows:specify` both gate `prd.md` with their
    own `require-on-main` before reading it as the PRD — one on a branch stops them, and one on no
    ref at all returns `absent` and is reported as no authored PRD — so a finding this run derived
    from a `prd.md` written only to a working tree would ground a document those two commands do not
    yet take as the PRD — a `[CG#n]` or `[DG#n]` whose premise agrees with nobody's
    committed copy of the requirement but this run's own.

    **Row F splits the same way the BRD route's row F does, and for the same reason: *never
    produced* and *produced, handoff declined* name different fixes.** Test whether `prd.md` is in
    the worktree at all:
    - **No `prd.md` anywhere — on no ref, and not in the folder either.** No `/product-workflows:create-prd`
      run has ever landed here, so there is nothing to build a claim list from. Stop:
      `PRD_GROUND_NEEDS_PRD: <KEY> has no prd.md on any ref and none in the folder — there is nothing to build a claim list from. Run '/product-workflows:create-prd <KEY>' and merge its handoff first.`
    - **`prd.md` is in the folder, and on no ref — produced, handoff declined.** The file exists;
      what is missing is a commit. Land what is already on disk, and **do not name
      `/product-workflows:create-prd`** — re-running it would author a second PRD over the one
      already written rather than land it:
      `PRD_GROUND_PRD_NOT_HANDED_OFF: <KEY>'s prd.md is written at <path> but is on no branch — its handoff was declined, so nothing is missing but the commit. Commit and merge it to the specs repo's default branch, then re-run '/product-workflows:prd-ground <KEY>'. Do not re-run /product-workflows:create-prd, which would rewrite the PRD rather than land the one on disk.`
7. **Require `$REPOS_PATH`.** Resolve `${REPOS_PATH:-/workspace}` (`docs/reference/environment.md`)
   as one directory or a colon-separated list. If no entry resolves to an existing directory,
   stop naming `REPOS_PATH`, per the `Required path environment variable unset` rule in
   `workflows-core:escalation-rules` — grounding has nothing to check a claim
   against without at least one mounted repository:
   ```
   choices: ["Set REPOS_PATH (enter the path)", "Cancel"]
   ```
8. **On `route: brd`, read the claim list, and stop if there is none.** (The idea route's own claim
   list is step 8i, immediately below — this whole step is the `route: brd` branch, unchanged.)
   From the gated
   `<BRD-dir>/brd/brd-inventory.md`, extract every `[BR#n]` row's `id` and `text`
   (`brd-format.md` §2 field shape), each cell decoded (§2.3 there) so an agent is handed the
   customer's text rather than the table's encoding — this is the `claims` array every dispatch in
   Phase 5 draws from.

   **Zero rows is a stop, not a quiet completion.** With no claim there is nothing to ground, so
   this run writes no finding; writing no finding means there is nothing to hand off; and
   `/brd-split` and `/brd-interview` both gate on exactly that handoff. Reporting "nothing to
   ground" and ending successfully therefore leaves a BRD whose next two commands refuse it and name
   **this** command as the fix — sending the operator back here to be told "nothing to ground"
   again, with the one thing that would change the state named nowhere. The fix for a claimless
   slice is upstream — its inventory is written by `/brd-split` on the parent, and `/brd-intake` is
   never the fix: a slice has no document of its own to intake (`brd-format.md` §2.1). Read
   `<PARENT-KEY>` from the resolved folder's `brd-link.md` `parent:` field. A slice reaches this
   state only as the empty child `/brd-split`'s empty-child check offered to keep with a recorded
   reason. **Where `<PARENT-KEY>`'s own `coverage-ledger.md` cannot be read**, the stop names
   neither `/brd-split` form, since which one runs is that ledger's to say: replace everything from
   `Re-run /product-workflows:brd-split on <PARENT-KEY>` to the end of the message with
   `The parent's ledger at <path> cannot be read, and which /product-workflows:brd-split form resolves this slice is that ledger's to say — report it; neither form is named here.`
   Every remedy table in step 6 that hands this stop's remedy on inherits that case with it, so a
   first row matching a claimless slice never names a form its own last row would withhold:
     `PRD_GROUND_EMPTY_INVENTORY: <BRD-KEY> is a slice of <PARENT-KEY> and its inventory holds no [BR#n] row — it claims nothing, so there is nothing to ground. Do not run /product-workflows:brd-intake on a slice; it has no source document of its own. Re-run /product-workflows:brd-split on <PARENT-KEY>: either way it resolves every standing empty child, so it will offer to remove this slice or to keep it against its recorded reason. Which form to type depends on that parent's own ledger. Where it still holds an unallocated row, the run walks it too and will offer covered-by against this slice — and a run with rows still to place needs a slicing instruction to group them, so type '/product-workflows:brd-split <PARENT-KEY> "<how to cut it>"'. Where no row is left unallocated, the bare '/product-workflows:brd-split <PARENT-KEY>' is the run, and removing this slice or keeping it against a recorded reason is the whole of what it offers here. Adding an instruction to that same run, '/product-workflows:brd-split <PARENT-KEY> "<what to peel off>"', can additionally re-cut onto this slice a row the parent delegated to a sibling that has since recorded it will not build it — the one case, apart from the key repair a removal performs, in which /brd-split re-allocates a row already carrying a fate, and the only third thing that can change this slice's state. That third one is not guaranteed to be on offer: it needs such a row to exist, and it needs this slice never to have been interviewed, so a slice emptied after its own interview can only be removed or kept.`

   **Why a stop rather than an empty handoff.** Writing an empty `grounding/code-grounding.md` and
   handing it off would let both downstream gates pass, but it would assert that grounding ran over
   this BRD when nothing was ever checked, and it would carry `/brd-interview` into generating a
   round's questions for a BRD with no requirement — leaving an empty round record permanently on
   file, which no later run may delete or renumber. A stop that names the upstream fix leaves the
   tree honest and the operator able to act.
8i. **On `route: idea`, read the claim list from `prd.md` instead, and report what is excluded from
    it.** From the gated `<PRD-dir>/prd.md` (step 6i), build the `claims` array every dispatch in
    Phase 5 draws from — unchanged in shape from the BRD route's (`id` and `text` per entry),
    changed only in where the entries come from:

    - every `[AC#n]` row under `## Acceptance Criteria`;
    - every `[FR#n]` row under `## Functional requirements` (present only on a `--full`-profile
      PRD; absent on `--lean`/`--hybrid` contributes nothing here, which is ordinary);
    - every `[US#n]` row under `## User Stories` **whose story carries no `[AC#n]` beneath it in
      `## Acceptance Criteria`, and no others.** A story is reached through its own acceptance
      criteria wherever it has any, and grounding both would ground one capability twice — so a
      story with acceptance criteria contributes nothing of its own, and this rule is precisely what
      keeps a PRD that skipped them from contributing nothing at all.

    **Three prefixes are excluded, and the exclusion is reported, never merely applied:**
    - **`[UC#n]`** — a use-case/user-journey row is a narrative whose evidence is a list of sites
      rather than a single anchor, which is exactly where a plausible-but-adjacent finding hides
      most easily.
    - **`[SM#n]` and `[SMC#n]`** — a success metric or counter-metric is a measurable,
      technology-agnostic **outcome**, and no commit satisfies or falsifies one. Grounding one would
      return evidence about whether the metric is *instrumented*, not about whether it is met — a
      claim adjacent to the one the row states, which is exactly the named failure
      `workflows-core:grounding-format` §1 exists to keep out: adjudicating a claim the row does not
      make and reporting it as evidence for the one it does.

    **Report the count and the excluded prefixes now, before Phase 1's repo prompt, and again in
    the Final report** — "11 of 19 requirement rows ground; 8 excluded — 3 `[UC#n]`, 5
    `[SM#n]`/`[SMC#n]`" or the like — so a later reader of either the transcript or the write-up
    cannot conclude from a clean run that the PRD was fully ground.

    **Zero resulting claims is a stop, not a quiet completion, for the same reason step 8 already
    gives on the BRD route: writing an empty `grounding/code-grounding.md` would assert that
    grounding ran when nothing was ever checked**, and it would hand `/product-workflows:create-ard`
    and `/product-workflows:specify` a folder whose grounding file exists and reads as *checked,
    nothing found* rather than *never run*. **The condition is narrower than it reads**: the
    fallback rule above already routes every `[US#n]` into the claim list the moment its own story
    carries no acceptance criterion, so a document with no `[AC#n]` at all still contributes a claim
    for every story it holds — the list only comes up genuinely empty where the PRD *also* holds no
    `[US#n]`, which the spine's own "Contiguous IDs" convention (`workflows-core:prd-format`) makes
    a degenerate document rather than an ordinary `--lean` one. The message still names only
    `[AC#n]` and `[FR#n]`, because those are the two rows the fix — adding acceptance criteria —
    actually adds; naming the empty `[US#n]` case too would not change what the operator is told to
    do. Stop, naming the fix that adds acceptance criteria and never the command that would
    rewrite the PRD instead of adding to it:
      `PRD_GROUND_NO_CLAIMS: <KEY>'s prd.md holds no [AC#n] and no [FR#n] row, so there is no claim to ground. Add acceptance criteria with '/product-workflows:update-prd <KEY>' and re-run. Do not re-run /product-workflows:create-prd, which rewrites the PRD rather than adding to it.`
9. **On `route: brd`, read `brd-link.md`, if present**, and carry **both** of its fields for the
   rest of the run:
   - `depends-on:` — any prerequisite already recorded by an earlier run. Phase 4 merges this run's
     `--depends-on` into it additively, never replacing it.
   - `parent:` — always present: by this step, step 6's gates have already guaranteed
     `coverage-ledger.md` and `brd/brd-inventory.md` are both on main — positive evidence 5a's
     legacy-fallback test would have refused had this BRD been a root — and `/brd-split` always
     writes `parent:` into a genuine slice. Carried forward for the messages elsewhere in this run
     that name `<PARENT-KEY>` (steps 6 and 8's stops, when reached).

   **On `route: idea`, this step is a no-op.** There is no `brd-link.md` on this route to hold
   either field — 5a's own route fork tested for its absence to reach `route: idea` at all — and
   step 2 already refuses `--depends-on` outright before this step could ever be asked to persist
   one. Nothing here is carried forward because nothing here exists to carry.

---

## Phase 1 — Resolve repositories

BRDs carry no PR links to auto-derive a repo list from (unlike `/epics`), so this phase is always
the manual path:

0. **Resolve documentation grounding, once, before prompting.** Run
   `resolve-docs-grounding prd-ground` per `Skill(skill: "workflows-core:reference", args: "docs-grounding resolve-docs-grounding")` and
   surface the `docs grounding:` line it returns — `ON <root> (retrieval: …)` or `OFF (<reason>)` —
   **verbatim**, including any index-build, staleness, or shadowing clause it carries (off switch:
   --no-docs), alongside the repo prompt below. **Under `--no-code` this command overrides the
   returned value to `OFF`** and surfaces that, rather than the procedure's own line: a divergence has
   nowhere to be written, because Phase 8 appends the `## Documentation divergences` section into
   `grounding/code-grounding.md` and this mode holds that file read-only. Say it as an override —
   `docs grounding: OFF (--no-code: divergences are written into code-grounding.md, which this run
   does not write)` — and not as something `resolve-docs-grounding` decided. That procedure's
   *Flags first* rung knows `--no-docs` and `--docs` only, is shared by nine commands of which one
   has `--no-code`, and executed as written on this run it returns `ON`. Teaching it a flag that
   exists in a single caller would put that caller's vocabulary in everybody's procedure. It runs **exactly once per run**, here; Phase 4.5
   consumes the cached result and never re-resolves. Resolving at the phase that prompts is what
   puts the only consent-bearing step (an index build, or a refresh that breached its cap) in front
   of the operator at the moment they are already answering a question, rather than mid-fan-out.
   The `/epics` consent-ordering exception — resolving *ahead* of a `require-on-main` gate
   (`commands/epics.md` Phase 2) — is deliberately not taken here: this command's gate is Phase 0's
   route-sequencing gate, which must stay first so a BRD whose inventory never merged is refused
   before anything else happens at all, and an index build is a durable, run-independent artifact
   that a later stop does not waste.
1. Prompt for the repos in scope for this BRD's claims — a free-text list of short names, one per
   line or space-separated.
2. **Build a slug→clone map**, exactly as `/epics` Phase 4 does: for each top-level directory
   under each entry of `$REPOS_PATH`, run `timeout 5 git -C <dir> remote get-url origin
   2>/dev/null`, strip a trailing `.git`, and take the URL's last path segment as that clone's
   slug. Skip directories with no `.git` or whose `git remote` call fails/times out. **Never
   assume a `<base>/<slug>` directory name** — resolution is always by remote slug.
3. Resolve each named repo against the map: one match → use it; multiple matches → auto-prefer
   basename ending `-repo`, then `_repo`/`_fast`, then alphabetically last (show candidates before
   proceeding); zero matches → escalate per the `Repo unresolved (zero matches) — /prd-ground` rule
   in `Skill(skill: "workflows-core:reference", args: "escalation-rules")`:
   ```
   choices: ["Skip and continue without this repo", "I'll clone it — wait", "Cancel", "Specify a different absolute path for this repo"]
   ```
4. Empty final list (every repo skipped or missing) → escalate per the `No repos derivable — /epics`
   rule in `workflows-core:escalation-rules`, whose `/prd-ground` variant
   this is:
   ```
   choices: ["List repos to check manually", "Cancel"]
   ```

Read-only throughout (`workflows-core:read-only-repos`) — this command never
switches a branch, fetches, or pulls any repository it resolves here; Phase 3 reads whatever
`HEAD` already is.

---

## Phase 2 — Classify + model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then record:

```yaml
model_routing:
  classification: MODERATE        # floors at SIGNIFICANT when Phase 1 resolved >1 repository —
                                   # the multi-source rule in model-routing/classification.md §1.1
  reason: <one-line>
  current_model: <the model this orchestrator is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every *_model below equals it and routing: bypassed
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # docs-grounder (Phase 4.5) — retrieval, not adjudication; also the Phase 9 impl-maintenance dispatch
  review_model:    <§2 Opus chain>     # code-grounder, design-grounder (Phase 5), grounding-verifier (Phase 7) — all three frontmatter-pinned; recorded, no override unless §10 enforces a model
  ground_tier:     <the tier the [CG#n]/[DG#n] corpus was actually ground at — the resolved review_model, or the degraded model where no Opus resolved>
  opus_available: <true if a §2 Opus model resolved, else false>
  notes: <any §2/§2.1 fallback or degradation>
```

**All three grounding agents keep a frontmatter Opus pin regardless of classification**, the same way
`design-reviewer`/`epic-reviewer` do elsewhere — the floor at `SIGNIFICANT` records that a
multi-repository run carries more cross-cutting risk; it does not change which model any of them runs
on. If no Opus resolves, degrade to best-available and record it in `notes` and the final report —
never hard-block. Under `run_flags.enforced_model` (`workflows-core:model-routing/classification` §10) the enforced model is used instead and no degradation is recorded, and `ground_tier` records that enforced id.

**Why the grounders are pinned and `docs-grounder` is not, since this is the family's most
token-expensive phase and the pin is not free.** Grounding **adjudicates**: it decides whether a
claim is true of a commit, and a wrong verdict is written into a corpus the estimate, the
architecture and the customer package are all built on. `docs-grounder` **retrieves** — it returns
leads for a human to rank, and a missed lead costs a lead. The split is measured, not assumed. On one
live engagement, blind re-derivation of a Sonnet-ground corpus found **18 of 18 code-citing findings
defective** — nine `contradict`, seven `extend`, and no `agree` at all — with a second slice at
roughly 50% verdict error; an Opus-ground corpus of 314 findings still moved 85%, but it moved mostly
by *omission* rather than by error. So the tier is a real and separable cause and it is not the whole
cause, which is why the pin ships beside `control` (`workflows-core:grounding-format` §2.2) rather
than instead of it.

**Cheap grounding is the expensive option**, which is the answer to the standing cost objection: a
corpus in which every code-citing finding is defective has negative value, and the cost is not
avoided but deferred and multiplied through verification, reconciliation and the human reading the
result. Where the spend is genuinely unacceptable on a given run, **make the pin conditional on
classification rather than reverting it**, and record `ground_tier` either way, so a reader always
knows which tier the corpus in front of them was ground at.

---

## Phase 3 — Baseline integrity gate

Invoke `Skill(skill: "workflows-core:reference", args: "grounding-format")` and run its
`baseline-integrity` procedure (§4) **once per resolved repository, before any finding is
written**:

```bash
git -C "<repo>" rev-parse HEAD
git -C "<repo>" diff --ignore-cr-at-eol --stat
git -C "<repo>" status --porcelain
```

1. Record `rev-parse HEAD` as the repo's pinned commit — held by this run, and written to
   `grounding/baselines.md` only in Phase 8 (below).
2. `diff --ignore-cr-at-eol --stat` must be empty. Any output → **non-empty content diff, stop**:
   `PRD_GROUND_DIRTY_TREE: <repo> has content changes at <sha> — grounding it would cite an unidentifiable snapshot. Settle that repository's working tree and re-run '/product-workflows:prd-ground <KEY>': commit the changes, stash them, or check out a clean copy — the plugin will not do it for you, because these are your files in a code repository this route never writes to. If the changes are what you want grounded, commit them first and re-run with --rebaseline so the new commit becomes the recorded pin.`

   **Under `--no-code`, drop the final sentence and name the re-run without the flag instead** — `--rebaseline` is refused in that mode (Phase 0 step 2), so a message ending in it sends the operator into a second stop: `… commit them first and re-run '/product-workflows:prd-ground <KEY> --rebaseline' without --no-code, so the new commit becomes the recorded pin.`

   **Every other stop on this route names a command or an action, and this one must too.** The
   remedy is the operator's, not the plugin's — `/prd-ground` mounts code repositories read-only and
   commits to none of them — but "settle the tree, three ways, then re-run this command" is still an
   action a reader can take, and naming which repository and which commit is what makes it one. Both
   named re-runs resolve in the state being reported: the BRD folder and its ledger are already
   gated on main by Phase 0, so nothing about this stop invalidates the command it offers.
3. For every entry `status --porcelain` reports, compare its working-tree line count against
   `git show <sha>:<path> | wc -l` when the path exists at the pinned commit (an untracked path
   that exists nowhere at the pin has nothing to compare against and is not itself a dirty-pin
   signal). Read that path from `git -C "<repo>" status --porcelain -z`, never from the quoting
   form above — `workflows-core:grounding-format` §4 step 3 states why, and a quoted path resolves
   to no file, so the comparison would be skipped in silence. A line-count mismatch is a non-empty
   content diff — stop with the same message above, naming the porcelain-flagged path.

**This gate is the orchestrator's, never delegated.** `code-grounder` and `grounding-verifier`
each re-verify `HEAD` against the commit *they* are handed (their own step 1/2), but that check
alone would let a repository whose working tree is dirty *around* an otherwise-matching `HEAD*`
pass silently — the content-diff and line-count checks above are what this phase adds, and they
run before Phase 5's first dispatch, not inside it.

**`--rebaseline`, and a plain re-run against moved code.** If `<BRD-dir>/grounding/baselines.md`
already records a pin for a repository:
- **Its `HEAD` still matches the recorded pin** → nothing moved; this is a harmless re-run. Skip
  re-grounding every claim this repository already answered — one a `[CG#n]` on file answers at
  this pin, by the test Phase 5 states — and ground against the pin, exactly as a first run would,
  every claim it has not — a row a later re-cut gave this slice, say, which is the re-run this
  command's opening names. So a plain re-run re-grounds this repository **for those claims and for no
  other**, and for none at all where it has none. A newly declared `--depends-on` changes none of
  this: Phase 6 reassesses the on-file findings' horizons against it by superseding them, so no
  claim is re-ground for it — a re-derived finding would stand beside the on-file one as a second
  live finding for one claim.
- **Its `HEAD` has moved, and `--rebaseline` was NOT given** → stop:
  `PRD_GROUND_NEEDS_REBASELINE: <repo> moved since the last grounding pin (<old-sha> -> <new-sha>) — re-run with --rebaseline to supersede the affected findings by ID.`
- **Its `HEAD` has moved, and `--rebaseline` WAS given** → proceed; Phase 5 re-grounds every claim
  against the new pin, and Phase 8 supersedes the old findings by ID rather than renumbering them
  (grounding-format.md §3, `SUPERSEDED`) — a citation into an already-sent package still resolves.

**Record the outcome as a `[CG#n]` finding** (`workflows-core:grounding-format` §4: "the outcome is recorded
as a `[CG#n]` finding" — a verified fact about a code repository at a commit is exactly what that
prefix denotes, and inventing a separate prefix for it would only fragment the namespace). One per
repository that passes this gate, assigned first, in repo-resolution order, **before** Phase 5's
claim-level findings — `CG#1..CG#R` on a first run for `R` resolved repositories, continuing after
whatever the highest `CG#n` already on file is on a `--rebaseline` run. Each carries every field
`workflows-core:grounding-format` §2 defines: `claim` — "baseline integrity: `<repo>` is pinned at a verified,
unmodified commit"; `verdict: CONFIRMED` (a repository that failed this gate never reaches a
finding — it stopped the run instead); `evidence` — the three command outputs (the pinned SHA, the
empty `--stat` diff, and the `--porcelain`/line-count result); `commit` — the same pinned SHA;
`altitude: implementation`; `horizon: current`; `consumed_by: none` — which on a baseline finding is
permanent and reports no gap, per `workflows-core:grounding-format` §4.1: there is nothing for a PRD, an ARD or a
specification to draw from an assertion that a commit is identifiable, so every downstream
unconsumed-item report excludes these findings rather than carrying one open item per repository
forever. Phase 5 continues the BRD-wide
`[CG#n]` sequence from these, never restarting at `CG#1` once a baseline finding already claimed
it. Phase 7 verifies these findings the same as any other — `grounding-verifier`'s own Process
step 1 already re-runs `baseline-integrity` for whatever finding it is handed, so re-checking a
baseline finding is exactly that re-run.

**Under `--no-code` this gate still runs in full** — every check, every stop — and writes nothing.
No baseline `[CG#n]` is assigned and no entry is appended to `grounding/baselines.md`: both would be
this invocation producing a `[CG#n]`, which the mode forbids. The pins it verifies are still
load-bearing, which is why the gate is not skipped along with the writes — a class-4 `[DG#n]` is
pinned to the commit of the `[CG#n]` it cites, and Phase 7 re-derives it against that repository at
that commit. A repository whose `HEAD` has moved stops here exactly as it always does, but the
remedy the message names changes: `--rebaseline` is unavailable under this mode, so name the re-run
**without** `--no-code`. Adding design grounding on top of a code grounding that no longer describes
the tree would pin new findings to a commit the repository has left.

**Hold one dated `grounding/baselines.md` entry per repository for Phase 8 to append** — **except under `--no-code`, which writes no baseline entry at all** (stated in full above; repeated here because this is the instruction it excepts, and a reader who arrives at an unconditional imperative does not go looking for its exception):
the repo, the pinned commit, the verification result, and the `[CG#n]` id assigned above — the same
three commands are what the customer's own reviewer re-runs later against their own checkout.
**This phase writes nothing to that file.** A pin is recorded together with the findings it pins,
in Phase 8, and never before them: every stop between here and Phase 8 — Phase 5's and Phase 7's —
then leaves the recorded pin exactly as the previous run left it. Appended here instead, a
`--rebaseline` run stopped in Phase 5 or 7 would leave the new pin recorded beside the old pin's
findings, unsuperseded; the re-run would find `HEAD` matching that new pin, take this phase's
first bullet, and never supersede them. Until Phase 8, "the recorded pin" everywhere in this run —
this phase's bullets and Phase 5's *answers* test — means the one the file held when the run
began.

---

## Phase 4 — Prerequisites

Persist any Phase 0 `--depends-on` keys into `<BRD-dir>/brd-link.md` under a `depends-on:` list —
**additive only**: merge into whatever the file already carries (including a `parent:` or
`claims:` field another command wrote), never drop an existing prerequisite, and never touch any
field but `depends-on:`. The file may also be edited by hand between runs; this phase reads it
fresh, adds, and writes back.

For every declared prerequisite (this run's plus any already on file):

1. `resolve-address <PREREQ-KEY>`. Absent → report `<PREREQ-KEY> — BRD not found`.
2. Found → look for `decisions.md` in its folder. Absent → report
   `<PREREQ-KEY> — no decisions.md yet; contributes no will-change horizons` (per
   `workflows-core:grounding-format` §5: a prerequisite whose decisions are not yet frozen contributes none).
3. Present → read only the decisions that are **frozen, which is a field test and not a judgement:
   `status: decided`**, the second of the five statuses
   `${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §3 fixes. Nothing else counts, and
   each exclusion is that section's own rule rather than this command's caution: `open` and
   `reopened` "may not be consumed downstream" while they stand; `superseded` and `withdrawn` are
   terminal and describe a position that is no longer held; and an `[AS#n]` never reaches `decided`
   at all (§7), so an assumption is never a frozen decision however confidently it is written. **Nor
   does a torn write** (§8) — a record a `/brd-interview` run left when it stopped before writing the
   round record that would name it, read here from the prerequisite's own `interview/` records — which
   counts for nothing whatever its `status` reads.
   **Read the status, do not infer it from how settled a record sounds** — the register carries the
   answer in a field precisely so that this reader does not have to weigh prose, and
   `/product-workflows:brd-reconcile` uses the same equivalence when it says what freezing a `[CD#n]`
   means. A `decisions.md` this reader genuinely cannot parse into records with statuses — not one
   whose records simply carry no `decided` — is treated as "none frozen" and **reported as
   unparseable rather than as empty**, because the two are different facts and only the first is
   worth someone's attention. Two outcomes:
   - **No record carries `status: decided`** → report
     `<PREREQ-KEY> — decisions.md present, none frozen yet; contributes no will-change horizons`
     — the same "contributes none" consequence as the absent-file case above, just reached from a
     different cause.
   - **At least one record carries `status: decided`** → report readiness in this exact form — the
     `prerequisites:` block, one aligned line per prerequisite, which the Final report below
     reproduces verbatim:
     ```
     prerequisites: EPIC-008-01 — decisions frozen, customer-reviewed 2026-08-27, not yet built
                    EPIC-002    — decisions frozen, NOT customer-reviewed
     ```
     "customer-reviewed `<date>`" comes from the newest `customer-review-<date>.md` in the
     prerequisite's folder, if any, else "NOT customer-reviewed"; "not yet built" is this
     prerequisite's default state — grounding is what tells the operator when a decision is about
     to move the ground it is standing on, so it is stated even when obvious.

No declared prerequisites at all → `prerequisites: none declared`. Hold this block for the final
report; Phase 6 also uses it to decide which findings get `horizon: will-change`.

---

## Phase 4.5 — Documentation leads (optional)

Consume the `resolve-docs-grounding prd-ground` result cached in Phase 1 step 0 — never re-run it.
`docs_grounding: OFF` → skip silently, reporting the `OFF` line once. `docs_grounding: ON` →
`dispatch-docs-grounder` (`workflows-core:docs-grounding`) with
`feature_summary` = two to four sentences built from the Phase 0 step 8 claim list (what this BRD
asserts and asks for, in product terms), `key` = `<BRD-KEY>`, and `themes` = the capability
themes those claims cluster into.

### A document is never evidence for a `[CG#n]`. Never.

**No `[CG#n]` or `[DG#n]` may cite a documentation page in its `evidence`, under any verdict, in
any phase of this run.** Not as a supporting line, not as a corroborating second source, not as the
thing that turns a `NOT-PROVABLE` into a `CONFIRMED`. Grounding answers one question — *is this
claim true of this specific commit?* (`workflows-core:grounding-format` §1) —
and a document cannot answer it, because **a document is a claim about behaviour, not the
behaviour**. It was written by a person, at a date, about a version, and nothing keeps it in step
with the code. Cite one and a confident, stale page satisfies a claim the code does not: precisely
the failure `NOT-PROVABLE` exists to make sayable. If the code will not settle a claim, the answer
is `NOT-PROVABLE`, and a page that seems to settle it changes nothing about that.

This is why the digest is **not** passed into `code-grounder`, `design-grounder`, or
`grounding-verifier` — none of their input contracts carries a documentation field, and none is to
be given one. The digest is consumed by this orchestrator alone, in exactly two ways:

1. **As a lead — where to look.** A `docs_references` page naming a subsystem, service, or module
   that **no repository resolved in Phase 1 covers** is surfaced now, before Phase 5 dispatches
   anything, with one choice: add that repository and re-resolve it through Phase 1 step 2–3 (then
   pin it through Phase 3 like any other), or proceed on the record and let the affected claims
   land as `NOT-PROVABLE`. A lead is a question about coverage, never an answer about behaviour.
2. **As a divergence — recorded in Phase 8, after verification, never before.** See below.

### A doc-versus-code divergence gets no identifier of its own

**It is recorded without one, and names the `[CG#n]` it diverges from instead.** Two reasons, and
neither is stylistic:

- **`[CG#n]`/`[DG#n]` cannot carry it.** Those prefixes denote a *finding* — an answer to a `[BR#n]`
  premise checked against a pinned commit or a frame set (`workflows-core:grounding-format` §1, §2). A
  divergence is not an answer to a `[BR#n]`; it is an observation about two artifacts, neither of
  which is the requirement. Minting a `[CG#n]` for it would also make it citable and
  `consumed_by`-able — the exact outcome the rule above forbids.
- **A new prefix would be worse, not better.** Every `[CG#n]`/`[DG#n]` must carry a verifier
  outcome or it is not evidence and blocks `/brd-split` (`workflows-core:grounding-format` §8). A divergence
  cannot earn one: `grounding-verifier` re-derives from a pinned repository or from a frame set,
  and a documentation page is neither, so a new prefix would either need a verification pass this
  workflow does not have or would sit permanently unverified in the namespace. The existing
  namespace carries the divergence perfectly well **by reference** — the identifier in the entry is
  the finding's, never the divergence's.

Because an entry must name a `[CG#n]`, a divergence can never stand on the page alone, and can
never be written before Phase 7 has verified that finding. That ordering is the safeguard, not a
formality.

---

## Phase 5 — Fan out grounding

**Under `--no-code`, skip this phase's `code-grounder` fan-out and its renumbering entirely**, and
read the `[CG#n]` set from `<BRD-dir>/grounding/code-grounding.md` instead — every finding on file
that does not read `SUPERSEDED`, with the `id`, `claim`, `verdict`, `evidence` and `commit` Phase 8
wrote there. A superseded one no longer stands (`workflows-core:grounding-format` §3), and a class-4
finding citing it would stand on a retired finding from the moment it was written. Those findings
are this run's **input, never its output**: not renumbered here, not re-verified in Phase 7, not
rewritten in Phase 8. The `[DG#n]` sequence still continues from the highest already on file, the
same as on any other re-run.

**`code-grounder`, one per repository, ≤4 concurrent per Agent message** (wait for a batch before
starting the next). Each dispatch gets its own pinned commit (Phase 3) and every claim that
repository has still to answer. **Against a repository with no pin recorded before this run, or one
a `--rebaseline` pass re-pins, that is the whole claim list** (Phase 0 step 8). **Against one whose
`HEAD` still matches its recorded pin, it is every claim of that list no `[CG#n]` on file answers
there** — a `[CG#n]` answers a claim at a repository where its `verdict` is not `SUPERSEDED`, its
`claim` names that claim's requirement id (read for the id it names, as Phase 8 reads it), and its
`commit` equals that repository's recorded pin (Phase 3's first bullet). A repository left with no
claim to answer is not dispatched. Within that set nothing is pre-filtered: a BRD carries no
per-repo claim tagging, and a claim that genuinely belongs to a different system is exactly what
`NOT-PROVABLE` exists to say. **The repositories this run dispatches here are the ones it
re-grounds, and the claims each dispatch carries are the claims it re-grounds there** — the known
set Phase 8's frame-set rule reads; Phase 3's baseline finding, minted for every repository it pins,
puts none in it:

→ Agent (subagent_type: "product-workflows:code-grounder", model: `<review_model — §2 Opus chain, equal to code-grounder's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "repo_path: [resolved absolute path from Phase 1]
  > commit:    [Phase 3 pinned commit for this repo]
  > claims:
  >   - id:   [the requirement id exactly as Phase 0 step 8 (or 8i) recorded it — BR#n on route:
  >            brd, AC#n/FR#n/US#n on route: idea]
  >     text: [requirement text]
  >   [… every claim this repository has still to answer (above)]
  > refresh:
  >   pull: false"

Handle `status`: `OK` → collect `findings`, **and collect `notes`** — a claim that touched a false-friend name, a claim whose search budget was exhausted. Report them with the findings: without them a `NOT-PROVABLE` `[CG#n]` whose search ran out is indistinguishable from one the code genuinely refutes, and only the first is worth another pass. `INPUT_MISSING` / `REPO_MISSING` → should not occur
(Phases 0/1/3 already checked); if it does, stop and name the gap. `COMMIT_MISMATCH` → the tree
moved between Phase 3 and this dispatch — stop and re-run from Phase 3 **with `--rebaseline`**, for
the reason Phase 7's `PRD_GROUND_VERIFY_COMMIT_MISMATCH` row states: a pin recorded before this
run still stands, `HEAD` has left it, and a plain re-run stops with `PRD_GROUND_NEEDS_REBASELINE`.

**Renumber into one BRD-wide sequence.** Each `code-grounder` instance numbers its own output from
`CG#1` (its own contract, per dispatch) — this is per-instance, not global. Merge every batch's
findings, in repo-resolution order, into one contiguous `[CG#n]` sequence continuing from the
highest `CG#n` already assigned this run — Phase 3's own baseline findings on a first run, or
whatever the highest `CG#n` already on file is on a `--rebaseline` run — never trusting an agent's
own numbers as the BRD's numbering.

**Then `design-grounder`, unless `--no-design`.** Look for `<BRD-dir>/design/`; each immediate
subdirectory is a candidate exported frame set. The location and the index requirement are
`workflows-core:grounding-format` §6.1's, cited here rather than restated —
`design/` is a reserved subdirectory of any folder under `specifications/`, so the same path resolves
whether this run stands on a BRD folder, on the PRD folder a slice is, or — on `route: idea` — the
PRD folder `/create-prd` wrote directly. None found → skip, reporting
why (`--no-design` given, or no `design/` folder exists yet for this BRD). One or more found → dispatch one instance per frame set, same ≤4
concurrent discipline, **after** the code-grounder batch above has fully returned — this agent's
fourth reconciliation class cites a `[CG#n]`, so the findings it needs must already exist. Under
`--no-code` there is no batch to wait for and that precondition is already met: the `[CG#n]` set
read from file is what `cg_findings` carries, which is the whole reason the mode can add design
grounding at all:

→ Agent (subagent_type: "product-workflows:design-grounder", model: `<review_model — §2 Opus chain, equal to design-grounder's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "frame_set_dir: [absolute path to this frame set]
  > inventory:
  >   - id:   [the requirement id exactly as Phase 0 step 8 (or 8i) recorded it — BR#n on route:
  >            brd, AC#n/FR#n/US#n on route: idea]
  >     text: [requirement text]
  >   [… every claim from Phase 0 step 8]
  > cg_findings:
  >   [… every merged [CG#n] finding from this phase, in the shape design-grounder's Inputs declare:
  >      id, claim, verdict, evidence, commit]"

Handle `status`: `OK` → collect `findings` (may be empty — agreement produces none). `INPUT_MISSING`
/ `FRAME_SET_MISSING` → should not occur; stop and name the gap if it does. `NO_INDEX` → this
frame set cannot be reconciled without an index file; report it and skip that directory rather
than guessing at frame identity — and name the repair, `/workflows-core:frames <this run's KEY>`,
which writes the index and lets a re-run ground the set. Renumber into one BRD-wide `[DG#n]` sequence the same way as
`[CG#n]` above, continuing from the highest `DG#n` already on file.

**Record which frame set each `[DG#n]` came from** as you merge — the dispatch that produced it
names exactly one `frame_set_dir`, and Phase 7 hands that same directory back to
`grounding-verifier` so it can re-derive a design-only finding at all. Recovering the association
after the merge would mean guessing; carrying it forward costs nothing.

A `design-grounder` `notes` entry naming a class-4 gap it deferred for lack of a settling
`[CG#n]` is carried into the final report verbatim — it is a real, actionable gap, not noise.

---

## Phase 6 — Horizons

Every finding leaves Phase 5 as `horizon: current` by default (an agent grounding one claim
against one repository or frame set has no visibility into another BRD's decisions to do
otherwise). This phase is where prerequisite awareness — Phase 4's readiness block — is applied
across the whole finding set:

For each finding, and for each declared prerequisite whose decisions Phase 4 found **frozen**:
read the frozen decision text and judge whether it directly determines this finding's claim once
built — not merely mentions the same area. Where it does, set `horizon: will-change` and record
`prerequisite: <the specific decision, by id and a one-line summary>` — on an on-file finding by
superseding it (below), never in place — naming the decision itself,
never merely the prerequisite BRD (`workflows-core:grounding-format` §5). Where no declared prerequisite has any
`status: decided` record at all, every finding stays `current`, and this is reported plainly rather
than left to look like nothing was checked.

**That case is ordinary, and it is no longer the *only* case.** A prerequisite's `decisions.md` is
written by `/product-workflows:brd-interview` (its register phase) and gains its `[CD#n]` records from
`/product-workflows:brd-reconcile`, both of which ship — so a prerequisite that has been through the
route carries frozen decisions as a matter of course, and this phase does real work on it. What
makes the no-frozen-decision case still ordinary is **sequencing, not absence of the capability**:
a prerequisite is typically declared while it is in flight, which is exactly when its register holds
`open` records and no `decided` ones. Report which of the two it is — a prerequisite with nothing
frozen yet, or one this run had nothing to declare against — because "every finding stayed
`current`" reads identically in both and means different things.

A finding already carrying `horizon: will-change` from a previous `--rebaseline` pass keeps it
unless the naming decision itself has since shipped (superseded by a later finding, per §3) —
`will-change` findings are never silently reverted to `current`.

**This phase never moves an on-file finding's `horizon` or `prerequisite` in place**
(`workflows-core:grounding-format` §5). A finding this invocation produced takes the horizon this
phase settles directly, since nothing outside this run cites it. An on-file finding — one already
written under `<BRD-dir>/grounding/` before this invocation, as Phase 7 defines it — may already be
cited by a decision taken on the horizon it carries, so where this phase would move either field —
and never on a block already reading `SUPERSEDED`, which no longer stands and is not reassessed, nor
on one a `--rebaseline` pass replaces this run, which Phase 8 supersedes and whose re-derived
successor takes this phase's horizon directly, nor on one Phase 8's frame-set rule supersedes this
run (*A set this run re-ground supersedes its own prior findings* — a prior finding of a set this
run's design pass reconciled, whether or not it returned a finding there, and a class-4 one only on
the terms that rule gives), whose re-derived successor
in that set, where that set has one on its claim, takes this phase's horizon directly — a copy
appended here would stand beside that successor as a second live finding for one claim, and would
put a second rule's write on a block that rule retires:

- the on-file block takes `verdict: SUPERSEDED`, its verdict written as `prior_verdict`, every
  other field as it stood on file, and a one-line note naming its successor;
- a successor is appended with the next free id in its prefix — after every id Phase 3 and Phase 5
  assigned, in the order of the ids superseded — carrying the block's `claim`, `commit`,
  `altitude`, `verdict`, `evidence` and `control`, and on a `[DG#n]` its `class` and `cites`, with
  the new `horizon` and `prerequisite`, `consumed_by: none`, and the note `supersedes [CG#n]` (or
  `[DG#n]`). It carries no `outcome`: this invocation produced it, so it is an **own-run** finding
  and Phase 7 verifies it like any other, and the block it succeeds, reading `SUPERSEDED`, leaves
  Phase 7's dispatch set.

`/product-workflows:brd-interview`'s *A decision the re-grounding moved* then sees the move: a
successor carrying the superseded finding's verdict and a different horizon does not confirm, so a
decision taken on the old horizon is reopened, and a held decision whose successors are no longer
`will-change` is put again. A superseded `[CG#n]` takes every class-4 `[DG#n]` citing it with it
(Phase 8's cascade). **Two exceptions, each reported by finding id with the horizon this phase
would have written.** Under `--no-code` an on-file `[CG#n]` is this run's input and
`code-grounding.md` is not opened for writing (Phase 8), so its horizon stays and the next run
without that mode moves it. And an on-file `[DG#n]` the frame-set placement (Phase 8, *A set this
run re-ground*) cannot place in exactly one frame set **is superseded with no successor**: the
block takes `verdict: SUPERSEDED` and its `prior_verdict` as above, and its note names the horizon
this phase would have written and says why no successor can be placed — Phase 7 could not hand the
verifier the `frame_set_dir` a successor needs. A stale horizon is never left standing for a
downstream reader to consume: a plain decision resting on the finding reads a finding with no
successor and is reopened, and a held one is put again, its finding's source being one that cannot
be decided (`/product-workflows:brd-interview`, *A decision the re-grounding moved*).

---

## Phase 7 — Verify

Dispatch `grounding-verifier` over **every** finding this run holds — Phase 3's baseline `[CG#n]`
findings, freshly-merged Phase 5 claim findings, the successors Phase 6 appended for a moved
horizon, and **the on-file findings this run re-checks, which are exactly these**: every `[CG#n]`
already on file that does not read `SUPERSEDED` and whose `commit` equals the recorded pin of a
repository whose `HEAD` still matched it in Phase 3 — on a plain re-run and a `--rebaseline` pass
alike, `provenance: inherited` (below), and none under `--no-code` (below) — **and never an on-file
`[DG#n]`**, which no run of this command re-checks. A moved repository's on-file findings are not
among them: a `--rebaseline` pass supersedes them in Phase 8. One instance per finding,
same ≤4-concurrent batching discipline as Phase 5, pinned to the Opus chain (`review_model`,
frontmatter-pinned, no override unless §10 enforces a model):

→ Agent (subagent_type: "product-workflows:grounding-verifier", model: `<review_model — §2 Opus chain, equal to grounding-verifier's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "finding:
  >   id:       [CG#n or DG#n]
  >   claim:    [the requirement premise as the finding recorded it — a BR#n on route: brd, an
  >              AC#n/FR#n/US#n on route: idea]
  >   class:    [1-4 — DG#n only, omit for CG#n]
  >   verdict:  [the finding's verdict]
  >   evidence: [the finding's evidence list]
  >   control:  [the finding's control, where it carries one — omit where it carries none; the
  >              agent decides owed-ness itself from grounding-format §2.2's closed-set rule and
  >              never from the field being absent]
  >   commit:   [the finding's pinned commit — every CG#n and every class-4 DG#n; omit only for a
  >              class-1/2/3 DG#n, which is pinned to no commit]
  >   cites:    [class-4 DG#n only — the CG#n it cites]
  > repo_path:     [the repository this finding is pinned against — every CG#n; for a class-4
  >                 DG#n, the repository the cited CG#n is pinned against; omit for a
  >                 class-1/2/3 DG#n]
  > frame_set_dir: [every DG#n — the Phase 5 frame set this finding was reconciled against; omit
  >                 for a CG#n]
  > inventory:     [every DG#n — the Phase 0 step 8 claim list, id and text, exactly as
  >                 design-grounder was handed it; omit for a CG#n]
  > provenance: [own-run | inherited — see below]"

**A finding already reading `verdict: SUPERSEDED` is not in that set, whichever run superseded it.**
It no longer stands (`workflows-core:grounding-format` §3), and its verifier `outcome` stays
exactly as the run that retired it left it. Dispatching it would re-derive the claim it once answered:
a `[CG#n]` superseded by a `--rebaseline` pass is pinned to the commit the repository has left, so
the verifier stops the run with `COMMIT_MISMATCH`, and the `--rebaseline` re-run that stop names
would dispatch the same finding again and stop the same way; and any other re-derivation returns a live verdict, which the reconciliation below
normalises to `contradict` against `SUPERSEDED` and the `contradict` branch would write — a retired
finding brought back to life beside its successor, its `prior_verdict` left on a block whose verdict
is no longer `SUPERSEDED`, where §2.1 forbids it. The class-4 sweep below excludes, for the same
reason, any finding this phase has itself marked `SUPERSEDED`.

Supply the finding **exactly as the agent's own Inputs contract declares it** — including
`evidence` and, for a class-4 `[DG#n]`, `cites` — even though the agent's own hard rules forbid
reading either before it finishes its independent re-derivation. That sequencing discipline is the
agent's to enforce on itself (its Process step 2 is explicit about it); this orchestrator's job is
only to hand over the full, correctly-shaped record, never to withhold a field the contract lists.

**Which anchor fields go with which finding is that contract's own Inputs table, not this
command's** — read it there (`agents/grounding-verifier.md`, Inputs), never from a copy kept here
that could drift from it. Two consequences for this dispatch:

- **Always pass `class` for a `[DG#n]`.** The agent's row selection is fail-closed — a `[DG#n]`
  arriving without a readable `class` is treated as resting on code and refused for want of a
  commit — so an omitted `class` does not relax the gate, it stops the finding. Phase 5 recorded
  the class on every `[DG#n]` it merged; pass it through.
- **Always pass `frame_set_dir` for a `[DG#n]`.** Phase 5 dispatched `design-grounder` once per
  frame set, so every `[DG#n]` on file traces back to exactly one directory; carry that association
  forward from Phase 5 rather than re-deriving it here. A `[DG#n]` Phase 6 appended as a successor
  was produced by no Phase 5 dispatch: its directory is the one frame set Phase 8's placement puts
  its superseded block in, which Phase 6 required before it superseded anything. A class-4 `[DG#n]`
  gets both it and the code pair — it is the one finding with a foot in each source.
- **Always pass `inventory` for a `[DG#n]`** — the same Phase 0 step 8 claim list Phase 5 handed
  `design-grounder`, unchanged. A `[DG#n]` is a reconciliation between the frame set and the
  inventory, so handing over only the frames gives the verifier one side of the comparison. A
  **class-1** finding cannot be re-derived at all without it: it asserts that no requirement asks
  for what the frame shows — a negative over the whole set — and its `claim` is
  `none — frame-only: <field>`, naming a field and no requirement, so there is no requirement id in the record to stand in for the set. The verifier
  correctly returns `NOT-PROVABLE`, and the finding is then permanently unverifiable and can never
  become evidence (`workflows-core:grounding-format` §8). This dispatch omitted the field, which is
  where that dead end came from.

**Under `--no-code`, "every finding this run holds" is the new `[DG#n]` set — Phase 5's, and any
successor Phase 6 appended — and nothing else.**
Every `[CG#n]` on file was neither produced nor reproduced by this invocation and already carries
the outcome from the run that did produce it. Re-dispatching them would spend one Opus verification
per finding to re-decide a settled one, and a single `contradict` would supersede a finding and
append its successor in a file this mode holds read-only — which is precisely the exposure the mode
exists to remove. The `[CG#n]` a class-4 `[DG#n]` cites is still checked in passing: the verifier
re-runs
`baseline-integrity` against the pin it is handed, as its own Process step 1.

**`provenance` is set per finding, by origin — never by which phase produced it, and never
blanket.** `own-run` for any finding **this invocation itself produced**, regardless of which
phase did the producing: Phase 3's baseline `[CG#n]` findings qualify exactly as Phase 5's claim
findings do, because Phase 3 re-runs `baseline-integrity` and assigns a fresh id every invocation —
first run or `--rebaseline` alike — never carrying a prior run's baseline finding forward
unreproduced. `inherited` for a finding **this invocation did not reproduce** — concretely, any re-run in which
a given repository's `HEAD` still matched its recorded pin, so Phase 3's first bullet skipped
re-grounding every claim that repository had already answered and the pre-existing findings from an
earlier invocation stand as they were, now being re-checked rather than regenerated. **That bullet fires on a plain
re-run and on a `--rebaseline` pass alike** — it is keyed on the pin still matching, not on the
flag — so a plain re-run against an unmoved repository inherits exactly as a `--rebaseline` pass
over one does. Illustrating only the flagged case would read as though the flag were what made a
finding `inherited`; the rule is the origin, and the flag never enters it. Phrasing the rule by origin rather than by
phase number is deliberate: it is immune to a future renumbering the way a phase-keyed rule is not.
The agent's own Inputs contract and `workflows-core:grounding-format` §8 both define `inherited` as "another
team's report **or an earlier run of this workflow**," and a finding surviving from before this
invocation, unreproduced, is the second of those, regardless of how confident its write-up reads —
mislabelling it `own-run` would tell the verifier to relax exactly where §5 of its own instructions
say rigor must not drop.

**Act on `status` first — an `outcome` exists only on `status: OK`.** Every status below other than
`OK` is a refusal, not a verdict: the agent performed no re-derivation and returned no `outcome`, and a
finding carrying no outcome is not evidence and blocks `/brd-split` for as long as it stays on file
(`workflows-core:grounding-format` §8). So none of them may be shrugged off and none may be written:

- **`OK`** — act on `outcome`, below.
- **`COMMIT_MISMATCH`** — the repository moved between Phase 3's pin and this dispatch. Stop:
  `PRD_GROUND_VERIFY_COMMIT_MISMATCH: <finding-id> could not be verified — <repo> is at <resolved-HEAD>, not the pinned <commit>. Re-run '/product-workflows:prd-ground <KEY> --rebaseline' from a clean tree.`
  **Under `--no-code` the same message names the re-run without the mode** — `'/product-workflows:prd-ground <KEY> --rebaseline'`, no `--no-code` — since that mode refuses the flag the remedy requires, and the finding that failed here is pinned to a repository the design pass cannot re-pin on its own.
  The same repair as Phase 5's own `COMMIT_MISMATCH`: re-run from Phase 3, which re-pins and
  re-grounds. **`--rebaseline` is part of the remedy, not an optional extra**, and the message says
  so: where `grounding/baselines.md` recorded a pin for this repository when the run began, this
  run never replaced it — Phase 8 records a new pin, and this stop comes before it — and `HEAD` has
  moved off it, so the re-run stops with `PRD_GROUND_NEEDS_REBASELINE` unless the flag is given.
  "Re-run from a clean tree" on its own would send the operator straight into that second stop.
  Where no pin was recorded, the flag changes nothing and costs nothing.
- **`INPUT_MISSING`** — this orchestrator's dispatch was malformed (most often a `[DG#n]` sent
  without its `inventory`, its `class` or its `frame_set_dir` — `inventory` first, because it is the
  newest requirement and the one whose omission made a class-1 finding permanently unverifiable). Stop, quoting the field and row the agent named, and
  fire `emit-block` per Phase 11's capture-at-block invariant — a dispatch this command controls
  getting the contract wrong is a plugin gap, unlike Phase 0's environment halts.
- **`REPO_MISSING` / `FRAME_SET_MISSING` / `NO_INDEX` / `STALE_INDEX`** — the source this finding rests on is gone
  or unusable (a repository unmounted mid-run, a frame set removed or exported without an index
  since it was ground). Stop, naming the finding and the path the agent reported — and the
  command that resolves it: on `NO_INDEX` that is
  `/workflows-core:frames <this run's KEY>`, then re-run this command. **On `STALE_INDEX` it is
  not** — the index is there and its descriptions are intact; the frames are gone. Re-running
  `/frames` on an empty directory writes nothing (`workflows-core:grounding-format` §6.2 step 6 forbids it), so
  naming it would send the operator to a no-op. Name the missing frames instead: restore them to the
  directory, then re-run this command — and `/frames` only if the set changed while they were away.

**Nothing reaches Phase 8 unverified.** Any stop above happens before Phase 8's first write, and so
does the incomplete-return stop below (*Act on `outcome`*, own-run), so a finding without an outcome
is never written into the package; whatever was on file from a previous
run stands untouched until a clean run replaces it. This is the invariant `/brd-split`'s Phase 0
gate depends on — it counts findings carrying no outcome and refuses to split while any exists, so
a run that wrote one would deadlock the route rather than merely leave a gap.

**Reconcile `outcome` against `own_verdict` before acting on either.** The agent returns its
re-derived verdict on **every** outcome, and `workflows-core:grounding-format` §8 defines `agree` as
reaching *the same* verdict and `extend` as the claim *holding* — so either arriving with an
`own_verdict` that differs from the finding's `verdict` is a return whose two halves contradict each
other, and the label is the half to disbelieve. **Normalise the outcome to `contradict`** and act on
that branch below, the one that believes the re-derivation. **Never normalise `unprovable`**: its
`own_verdict` is `NOT-PROVABLE`, so it differs from the finding's by definition, while the outcome
means only that the verifier's own search settled nothing — normalising it would rewrite every
inconclusive finding into a contradiction nobody reached. `contradict` already disagrees and is left
alone.

**A `control_outcome` of `missing` — or of `failed` on a finding whose verdict rests on the absence —
is a second, independent route to `contradict`.** The verifier decides first whether the finding
*owed* a control at all (`workflows-core:grounding-format` §2.2's closed-set rule), so `not-owed` is
an ordinary clean result and is never normalised: three of the four `[DG#n]` classes legitimately
carry none, and treating their empty field as a defect would contradict every one of them.

- **`missing`** — the finding owed a control and carries none. Normalise to `contradict`.
- **`failed`**, and the finding's verdict is anything **other than** `NOT-PROVABLE` — the absence
  rests on a search never shown capable of finding the thing it says is missing. Normalise to
  `contradict` **even where the returned outcome is `agree` and the verifier's own search also found
  nothing**: that agreement is two searches sharing one blind spot, which is the state the control
  exists to expose and the one an `agree` would launder into evidence.
- **`failed`**, and the finding already reads `NOT-PROVABLE` with that failed control recorded —
  **no normalisation.** The finding did exactly what §2.2 tells a writer to do and the verifier
  reproduced its result; overturning it would contradict, on every run and forever, the one finding
  on the page that told the truth about its own search.

Where a normalisation does fire it is recorded and counted exactly as the `own_verdict` one below is,
and it is the only one that can also apply to a returned `unprovable` — the control establishes that
the **original** search was incapable, which is a different and stronger fact than the verifier's own
search having settled nothing.

**Record every normalisation and report the count** — the finding id, the outcome as returned, and
both verdicts — in the Final report's verifier tally. A normalisation that happens silently is
indistinguishable from an agent that never disagreed, which is the state this step exists to make
visible.

**None of the verifier's own field NAMES reaches the record**, though a `contradict` writes their
values into the record's own fields. `own_verdict`, `own_evidence`, `own_control`,
`control_outcome` and the verifier's re-derivation `commit` are return fields
(`workflows-core:grounding-format` §2.1's closed field set). What Phase 8 writes is the `verdict`
this step settles, plus `outcome` and any `notes` — never a second verdict beside the first.

Act on `outcome`:
- **`agree`** — keep the finding as written; record the outcome alongside it.
- **`extend`** — keep the finding's verdict; append the verifier's additional evidence to the
  finding's `evidence` list; record the outcome.
- **`unprovable`** — keep the finding's verdict unchanged (the verifier's own search settling
  nothing either way is not the same as it being wrong); record the outcome and flag the finding
  in the report as verification-inconclusive.
- **`contradict`** — **what it writes turns on whether the finding is already on file, never on
  which phase produced it.** An **own-run finding** is one this invocation produced
  (`provenance: own-run`, above) and Phase 8 has not yet written, so nothing outside this run cites
  it yet. An **on-file finding** is one already written under `<BRD-dir>/grounding/` before this
  invocation — every `inherited` finding is one — and a decision, a ledger row or a sent package may
  already cite it. **No finding is both**: every finding this invocation produces takes a fresh id
  (Phase 3, Phase 5), so a claim it re-produces is a new own-run block beside the on-file one, never
  the on-file block itself.
  - **Own-run: the finding is rewritten, and the rewrite retains the same id.** Replace the
    finding's `verdict` with the verifier's `own_verdict` and its `evidence` with `own_evidence`,
    and keep a one-line note of the pre-rewrite verdict for the audit trail — and where
    `own_verdict` is `SUPERSEDED`, write the pre-rewrite verdict as `prior_verdict` too, since every
    write of that verdict carries one (`workflows-core:grounding-format` §2). **On a `[DG#n]` the
    new `evidence` also keeps every frame citation the replaced evidence carried** — a path under
    the finding's own frame set — beside `own_evidence`: a class-4 finding is re-derived against the
    repository, so its `own_evidence` may cite code alone, and a design finding citing no frame can
    never be placed in its frame set again, which is how
    `/product-workflows:brd-interview`'s successor test finds a design finding's source. **Where the
    rewritten finding *owes* a control — §2.2's closed-set rule, the same test the verifier applied
    to the original and not "does it assert an absence", which gets classes 1 and 4 wrong — its
    `control` is the verifier's `own_control`**: a rewritten finding owes one exactly as an original
    does, and the run holds no other search to build it from. The id never changes, so every
    citation into an own-run finding — this run's own, the only kind it has — still resolves.

    **A `contradict` whose rewritten finding owes a control and whose return carries no
    `own_control` is an incomplete return, and on an own-run finding it stops the run.** The
    verifier's own contract requires `own_control` there (`agents/grounding-verifier.md`, its
    return), so this is that contract broken rather than a verdict, and no record this run could
    write is honest: the rewrite would be a record §2.2 refuses, the unrewritten finding with this
    run's `outcome: contradict` beside its verdict would be the live disagreement
    `workflows-core:grounding-format` §2.1 forbids, and the finding with no outcome at all would
    block `/brd-split` — on a `[DG#n]` with nothing able to clear it, since no run re-checks an
    on-file `[DG#n]` and a later supersession leaves the missing outcome missing. Stop before Phase 8's first write, as the
    refusals above do, and fire `emit-block` per Phase 11's capture-at-block invariant:
    `PRD_GROUND_VERIFY_INCOMPLETE: <finding-id> could not be verified — the verifier contradicted it and returned no own_control, which the finding it would rewrite owes. No finding was written; re-run '/product-workflows:prd-ground <KEY>' with the flags this run was given.`
    **On an on-file finding the same return stops nothing** (below).
  - **On-file: the finding is superseded, and a successor carries the verifier's verdict.** The
    on-file block takes `verdict: SUPERSEDED`, its on-file verdict written as `prior_verdict` — the
    verdict any decision citing it was taken on (`workflows-core:grounding-format` §2) — and a
    one-line note naming its successor. **Every other field of that block stays as it stood on
    file**, `outcome` and `consumed_by` included: the `contradict` is the successor's. The successor
    takes the next free id in the finding's prefix — after every id Phase 3, Phase 5 and Phase 6
    assigned, in the order of the ids superseded — and carries:
    - `claim`, `commit`, `altitude`, `horizon` and `prerequisite` as the superseded block holds
      them — Phase 6 never moves an on-file finding's horizon in place, so the block still carries
      the horizon it was written with;
    - the verifier's `own_verdict` as `verdict`, and `own_evidence` as `evidence` — on a `[DG#n]`
      beside every frame citation the superseded block's evidence carried, for the reason the
      own-run branch gives;
    - `control` where the successor **owes** one, by the same closed-set rule as the own-run
      branch, and never merely because the verifier returned one;
    - `consumed_by: none`, `outcome: contradict`, and the note `supersedes [CG#n]`.

    **An owed control with no `own_control` returned is the same incomplete return, and here it
    writes nothing at all**: nothing is superseded, no successor is appended, and the on-file block
    keeps every field as it stands — its `verdict` and the `outcome` an earlier run wrote included,
    since this run's `contradict` written beside the verdict it contradicts would be a live
    disagreement `workflows-core:grounding-format` §2.1 forbids. The run does not stop: no write of
    this run's touches that block, and the outcome it keeps is the one `/brd-split` already counted.
    The Final report names the finding as **not verified by this run**, with the reason.

    **In this command the finding superseded here is always a `[CG#n]`**: Phase 7 dispatches no
    on-file `[DG#n]` (its opening set holds none, and the sweep below holds only this run's own), so
    a `[DG#n]` successor — with its `class`, `cites` and frame citations — is
    `workflows-core:grounding-format` §8's general rule and not a path this run takes. **Where
    `own_verdict` is itself `SUPERSEDED`, no successor is appended**: one reading `SUPERSEDED` would
    stand for nothing. The block is marked `SUPERSEDED` with its `prior_verdict` and a note saying
    the verifier found it superseded; this run's `contradict` is recorded in the Final report and
    on no block, and a decision resting on the finding reads a finding with no successor. **A
    successor may repeat the superseded verdict**: a control normalisation (above) forces
    `contradict` where `own_verdict` equals the finding's `verdict`, and where the horizon did not
    move either, `/product-workflows:brd-interview`'s *A decision the re-grounding moved* reads the
    successor as a confirmation — correctly, since only the search was repaired. Citations into the
    old id still resolve, to a block reading `SUPERSEDED`, exactly as after a `--rebaseline` pass:
    the ledger's `evidence` column lists both ids (Phase 8), and a `consumed_by` stamp stays on the
    block it was written to. **An in-place rewrite here would be invisible downstream**: a decision
    citing the id would stand on a verdict it was never taken on, which no supersession test ever
    sees (`${CLAUDE_PLUGIN_ROOT}/references/decision-register-format.md` §4, cause 1). A class-4
    `[DG#n]` citing a `[CG#n]` superseded here is Phase 8's to supersede, not the sweep's below.

**Then sweep the class-4 `[DG#n]` findings against the `[CG#n]` set this phase just settled.** A
class-4 finding's standing is derived from the `[CG#n]` it cites
(`workflows-core:grounding-format` §6.3), so every in-place `contradict` rewrite above — which
reaches only an own-run finding — may have moved the ground under one without touching its record
— the id still resolves and the claim ids still match, which is exactly why nothing else here would
notice. **A `[CG#n]` this phase superseded instead — an on-file one — is not this sweep's**: Phase
8's rule that superseding a `[CG#n]` supersedes every class-4 `[DG#n]` citing it takes every such
finding, and two rules claiming one block is how a block ends up with two conflicting writes.

**The set is every class-4 `[DG#n]` this run holds**, less any this phase has itself marked
`SUPERSEDED`. **An on-file class-4 finding is never in it, and needs no exclusion to keep it out**:
an earlier run wrote it, so the `[CG#n]` it cites is on file too, and this phase never rewrites an
on-file `[CG#n]` in place — it supersedes it, which is Phase 8's. **A held one matches only where
Phase 5 produced it**: Phase 5 hands `design-grounder` only its own merged `[CG#n]` set, and under
`--no-code`, where it hands the on-file set instead, this phase verifies no `[CG#n]` at all; and a
held class-4 finding Phase 6 appended as a successor cites the on-file `[CG#n]` its superseded block
cited, which this phase never rewrites in place either. **So a `--no-design` run, which produces no
class-4 finding in Phase 5, gives the sweep nothing to do**; every class-4 finding such a run
leaves standing on a superseded `[CG#n]` is Phase 8's cascade's.

**Every finding the sweep re-dispatches carries the `frame_set_dir` its own Phase 5 dispatch named**
(Phase 5, *Record which frame set each `[DG#n]` came from*), so every one whose cited `[CG#n]` this
phase rewrote can be re-derived rather than retired: re-dispatch `grounding-verifier` once and act
on the returned outcome as above — the own-run branch, since a held finding is not on file.

**An inherited finding that owes a control and carries none is `contradict` like any other, and gets
no discount for being old.** `workflows-core:grounding-format` §8 makes an inherited finding
unverified by definition, and `product-workflows:grounding-verifier`'s own rules forbid searching one
any less hard; an exception here would admit an uncontrolled absence claim as evidence precisely
where the claim is *least* checked. The verifier has re-derived it and returned its own
`own_control`, so its successor is a properly controlled finding rather than a hole. **Expect this
to fire in bulk on the first run over a corpus written before the field existed**, and report it by
count, so a wall of supersessions reads as the one-time conversion it is rather than as a corpus
falling apart.

Where the cited `[CG#n]` was rewritten and still settles the capture question the same way, the pair
is recorded as re-checked and nothing changes. **Report every state the sweep reached** — the findings
re-derived; the findings re-checked and left standing because the rewritten `[CG#n]` still settles
the capture question the same way; and the three ways the sweep can legitimately do nothing, which
are different facts and are not reported as the same one: **the set was empty** — no class-4 finding
held, as on a run whose Phase 5 produced none — a `--no-design` run, one with no `design/` folder,
one whose design pass emitted none — and whose Phase 6 appended none; **the set was non-empty but
this phase rewrote no `[CG#n]`**, which is every `--no-code` run and any run whose verifier agreed
throughout or contradicted only on-file findings; and **the set was non-empty and `[CG#n]` were
rewritten, but no class-4 finding in it cites one of them**, which is the ordinary shape of a corpus
whose design findings rest on code the verifier upheld. Say which. None of the three is reported as
"none", which
would read as a sweep that ran over findings and found nothing wrong with them. A state this run did
not reach is omitted, not reported as zero. The class-4 findings Phase 8's cascade supersedes are
reported with that cascade, not here.

A finding carrying no verifier outcome is not evidence (`workflows-core:grounding-format` §8) and is never
written to the package with `consumed_by` anything but `none` — this phase is what stands between
a raw finding and one a downstream command may cite.

---

## Phase 8 — Write findings

**Append Phase 3's held `grounding/baselines.md` entries** once the two finding files below are
written, and before the ledger's `evidence` column — never under `--no-code`, which holds none (Phase
3). The pins land in the same phase as the findings pinned to them, so no stop of this run leaves one
without the other.

Write `<BRD-dir>/grounding/code-grounding.md` (every `[CG#n]`) and
`<BRD-dir>/grounding/design-grounding.md` (every `[DG#n]` this run produced — **or, where Phase 5
produced no `[DG#n]`, a short note saying so and why — design grounding skipped, or run and finding
no divergence, which are different facts and are not written as the same one — appended to whatever
the file already holds rather than replacing it**: an existing corpus is not overwritten by a run that
ground no design, and this phase's class-4 cascade below may edit blocks inside it) — one block per finding, **serialised exactly as
`workflows-core:grounding-format` §2.1 fixes it**: one space after every colon, never alignment
padding, keys in the §2 table's order, and an inapplicable field omitted rather than written empty.
That section is not a style note — a writer that aligns one section's keys and not the next produces
a file whose readers report findings as missing that are on the page. Each block carries every field
`workflows-core:grounding-format` §2 defines (`id`, `claim`, `verdict`, `evidence`, `altitude`, `horizon`,
`consumed_by` — `none` on a block this run appends, while a block already on file keeps the value it holds, since `/create-prd`, `/create-ard` and `/specify` write it later and nothing here may erase a stamp — plus `prior_verdict` on every finding reading `SUPERSEDED`, `prerequisite` on every finding reading `horizon: will-change`, `control` on every finding asserting an absence, `class`/`cites` on a
`[DG#n]` and `commit` on everything **except** a
`[DG#n]` of class 1, 2 or 3 — those are settled from the frame set alone and are pinned to no commit,
per §2's applicability note) plus this run's verifier `outcome` — on every block but two kinds, each of which keeps the `outcome` it holds: one Phase 7 superseded, its `contradict` written on its successor or, where there is none, recorded in the Final report only; and an on-file one whose `contradict` was an incomplete return, owing a control and returning no `own_control`, whose block this run does not touch and whose `contradict` the Final report records as not verified by this run (Phase 7, *On-file*, both) — **and any `notes` the verifier returned** — **and nothing else.** §2.1 makes the field set closed: `own_verdict`, `own_evidence`, `own_control`, `control_outcome` and the verifier's re-derivation `commit` are return fields Phase 7 has already acted on — where a `contradict` rewrote an own-run finding or appended an on-file finding's successor, their values are already in that block under the record's own names (`verdict`, `evidence`, `control`) and the return names never appear — and a block carrying `own_verdict` beside `verdict` states two verdicts at once, leaving every downstream reader free to quote whichever half suits. That is the state `/brd-split` step 7 and `/brd-interview` step 7 now refuse, so writing it here deadlocks the route rather than merely muddying the record. Its contract calls those *"anything the caller should know before recording this outcome"*, so they are read before the outcome is written, not after — a verdict recorded without them is recorded against a caveat the verifier raised and nothing carried.
A `--rebaseline` run appends its new findings after the existing ones and marks any finding it
superseded — never one already reading `SUPERSEDED`, whichever run retired it — with `verdict:
SUPERSEDED`, id retained, rather than deleting or renumbering it — and writes the verdict that
finding carried until then as its `prior_verdict`, in the same block
(`workflows-core:grounding-format` §2). **Phase 6's horizon supersession and Phase 7's `contradict`
on an on-file finding are written the same way**, on any run: the block superseded keeps its id and
takes `SUPERSEDED` and its `prior_verdict`, and its successor is appended after the existing
findings. **Every write of `verdict: SUPERSEDED` in this phase carries one**, the class-4 and
frame-set supersessions below included, **and none of them is made on a block already reading
`SUPERSEDED`**, which would record `SUPERSEDED` as its `prior_verdict`
(`workflows-core:grounding-format` §2 forbids it) and put a second rule's note on a block the first
already retired: superseding overwrites `verdict`, and `/product-workflows:brd-interview`'s *A
decision the re-grounding moved* reads `prior_verdict` to tell a re-grounding that came back as it
stood from one that moved a decision's ground.

**Superseding a `[CG#n]` supersedes every class-4 `[DG#n]` citing it, on file or held, in the same
pass — whichever route superseded it.** Three routes do: a `--rebaseline` pass, which replaces a
`[CG#n]` against a moved commit; Phase 7's `contradict` on an on-file `[CG#n]`, which replaces its
verdict at the same commit; and Phase 6's horizon supersession, which replaces its horizon at the
same commit. In each case the `[DG#n]` asserted the pinned code could not perform a capture on the
authority of a finding this run has just replaced; leaving it means a design finding standing on a
superseded code finding, with a citation that still resolves and a claim id that still matches —
the state `workflows-core:grounding-format` §6.3 forbids and the one no reader can detect. It is
never Phase 7's sweep's, which acts only on a `[CG#n]` rewritten in place.

**Which rule writes such a `[DG#n]` turns on its frame set, never on the route:**

- **Where the frame-set rule below supersedes it**, on the terms that rule gives a prior class-4
  finding (*A set this run re-ground supersedes its own prior findings*) — that rule writes it, and
  this rule writes nothing more to it: two rules claiming one block is how a block ends up with two
  conflicting writes. On the `--rebaseline` route that is every such finding in a set this run
  reconciled, and that set's new findings are this run's re-derivation against the new pin.
- **Otherwise it is marked `SUPERSEDED`**, on any route — on every `--no-design` run, for a set
  recorded `skipped: no index`, for a finding no frame set places, for a class-4 finding this run
  holds, and on the other two routes wherever the frame-set rule does not take it. **That rule takes
  a prior class-4 finding only where Phase 5 re-ground its claim against the repository its cited
  `[CG#n]` is pinned to**, and Phase 5 re-grounds no claim a `[CG#n]` on file answers at that
  repository's recorded pin — which every `[CG#n]` Phase 7 contradicts on file does, being one of
  the findings Phase 7's opening set re-checks — so on the `contradict` route this bullet always
  writes it, and on the horizon route it writes it wherever the superseded `[CG#n]` answered its
  claim at the pin. On those two routes no `[DG#n]` this run wrote cites the successor:
  Phase 5's design pass ran before Phase 6 or Phase 7 appended any successor, and it is handed only
  this run's own merged `[CG#n]` set, never an on-file one — under `--no-code`, where it is handed
  the on-file set, no `[CG#n]` is superseded at all.
- **Never on a block already reading `SUPERSEDED`**, on any route — one an earlier run retired, or
  one Phase 6 superseded this run for its horizon, before this rule runs. That block keeps the write
  it has; re-marking it would record `SUPERSEDED` as its `prior_verdict` and put two rules' notes on
  it. Where Phase 6 appended it a successor, the successor is a class-4 finding this run holds and
  cites the same superseded `[CG#n]`, so the bullet above marks the successor instead; where Phase 6
  appended none (its second exception), there is nothing further to mark.

**Marked `SUPERSEDED` means**: id retained, the verdict it carried written as `prior_verdict`, and a
one-line note naming the `[CG#n]` that took it there, the verdict that finding carried, the verdict
its successor carries — or that it has none — and the run that replaces it:
`/product-workflows:prd-ground <KEY> --no-code` where that `[CG#n]` has a successor, and a plain
`/product-workflows:prd-ground <KEY>` where it has none. **Where it has one, it has to be that mode
rather than a plain re-run**: on a plain re-run `HEAD` still matches the pin and the successor
answers the claim there, so Phase 5 does not re-ground it, and a `design-grounder` handed no
`[CG#n]` for a claim **does not emit a class-4 finding for it**. Under `--no-code` the `[CG#n]` set
is read from file, successor included, which is the whole reason that mode can add design grounding.
**Where it has none**, no `[CG#n]` on file answers the claim, so that mode would hand the design pass
nothing for it, while a plain re-run re-grounds exactly that claim (Phase 5) and its design pass
takes the new `[CG#n]`. Its verifier `outcome` stays exactly as it is. Nothing is re-derived and
nothing is invented.

**What must NOT happen here is clearing the `outcome`**, and it is worth saying because it looks
like the safer move. A finding with no outcome is not evidence
(`workflows-core:grounding-format` §8), which reads as a useful brake — but `/brd-split` and
`/brd-interview` both count outcome-less findings **without excluding superseded ones**, and no
`/prd-ground` mode restores an outcome to an on-file `[DG#n]`: Phase 7 never dispatches one — its
opening set holds none, and its sweep holds only this run's own findings — and Phase 5 mints new ids
rather than re-outcoming old ones. The route would deadlock with no command able to clear it and no
stop naming the hand edit that could. `SUPERSEDED` says the same thing about the finding — it no
longer
stands — while leaving the record verified and the route able to move.

**Report every class-4 finding this rule marked `SUPERSEDED`**, each with the `[CG#n]` that took it
there, the route that superseded that `[CG#n]`, and the re-run that replaces it — in the Final
report, beside the Phase 7 sweep's own states and never folded into them.

**Every edit to a finding already on file is written in place — same id, never a second block
appended for it** — among them every supersession: Phase 6's for a moved horizon, Phase 7's on a
`contradict`, a `--rebaseline` pass's, the cascade's above, and a re-ground frame set's (below). A
successor is a new block with a new id, appended; it is never written over the block it succeeds.
The Phase 7 sweep edits none of them: every finding it re-derives is one this run holds, written
like any other of this run's. **This applies on a `--no-design` run too**, which writes no
`[DG#n]` of Phase 5's: on such a run an on-file design finding changes by Phase 6's horizon
supersession, or by the cascade above through any of its routes — a `--rebaseline` supersession on
a `--rebaseline --no-design` run, and a `contradict` or a horizon supersession of an on-file
`[CG#n]` on that run or on a plain `--no-design` one — and a run that superseded a finding and did
not write it would leave a record on disk still asserting a capture its own foundation no longer
supports. Opening `design-grounding.md` to edit those blocks is not the same as writing design
findings, and this mode's rule below is unchanged: Phase 6 and the cascade edit only blocks they
superseded, and append only Phase 6's successors, alongside whatever else this phase already
appends to that file on such a run.

**Under `--no-code` this phase writes `design-grounding.md` and, on `route: brd`, the coverage
ledger's `evidence` column (below) — and nothing else.**
`code-grounding.md` is not opened for writing at all — not for findings, not for the documentation
divergences below (documentation grounding is off for the run), and not for the derivation matrix
below (resolved off, or refused outright in Phase 0 when it was asked for explicitly). Every
`[CG#n]` on file stands byte-for-byte as the run that wrote it left it. The `[DG#n]` this run
verified are appended after any already on file, continuing the sequence rather than replacing the
file's contents.

**`design-grounding.md` names every frame set on disk, covered or not.** Write a
`## Frame sets covered` section — **replacing any section of that name already in the file, never
appending a second one.** It is a census of the tree as this run left it, not a log: two sections
would leave `/brd-split`'s gate reading "the" section with no rule for which, and the older one
records a state that has since changed.

**Enumerate `<BRD-dir>/design/` here, in this phase, rather than reusing what Phase 5 saw.** Phase 5's
listing sits behind `--no-design`, so on a run carrying that flag it never happens — and a section
built from "what this run saw" would then be empty, no `skipped: --no-design` row could ever be
written, and `/brd-split` would stop a run whose flag it is supposed to honour. The census must be of
the directory, not of the run. List **every** immediate subdirectory, each against exactly one
disposition:

- `ground` — with the `[DG#n]` ids this run reconciled against that set, or `none` where the
  design pass reconciled it and returned no finding.
- `skipped: --no-design` — the operator turned the pass off for this run.
- `skipped: no index` — Phase 5 got `NO_INDEX` for that set and could not reconcile it.

**A set this run re-ground supersedes its own prior findings, and the mode that makes that ordinary
is `--no-code`.** **A set this run re-ground is every set its design pass reconciled** — Phase 5
dispatched `design-grounder` on it and got `status: OK`, the census above recording it `ground` —
**whether or not that dispatch returned a finding there**: agreement produces none (Phase 5), and a
set that now agrees with the inventory has retired every divergence it had on file. For every such
set, mark its prior findings `verdict: SUPERSEDED`, id retained, its `prior_verdict` written, exactly
as a `--rebaseline` pass does for `[CG#n]` — never delete or renumber, so an existing citation still
resolves — and give each the one-line note `superseded: frame set <frame-set> re-ground`,
`<frame-set>` being that set's directory name, written exactly so. That literal is how
`/product-workflows:brd-interview`'s *A decision the re-grounding moved* tells a finding this
re-grounding retired — which looked for a successor to it in this run and found none, so no later run
owes it one — from a finding still waiting on a run that will re-derive it. **A prior class-4 finding is among them only where this run re-ground its claim against
the repository its cited `[CG#n]` is pinned to.** That repository is the one whose
`grounding/baselines.md` entry records a pin equal to that `[CG#n]`'s `commit`, and *re-ground* is
Phase 5's known set, never a judgement: Phase 5 dispatched a `code-grounder` against that repository
this run, and that dispatch's claims carried the requirement id the `[CG#n]`'s `claim` names. A
`--rebaseline` pass re-grounds every claim against a moved repository, so it takes every such
finding citing that repository's old pin; **a plain re-run against an unmoved repository re-grounds
only the claims no `[CG#n]` on file answered at its pin** — a row a later re-cut gave this slice —
so it takes a prior class-4 finding on such a claim and on no other. **Or under `--no-code`**, where
`cg_findings` is the whole unsuperseded `[CG#n]` set on file. Otherwise it stands: a design pass
handed no `[CG#n]` for a claim emits no class-4 finding for that claim, so superseding it would
retire a finding nothing replaces, and the class-4 cascade above retires it once its cited `[CG#n]`
is superseded. **A prior finding belongs to the one set whose index names every path of its `evidence`
that any set's index names, there being at least one such path** — the placement
`/product-workflows:brd-interview`'s successor test makes, since a finding record carries no
frame-set field and a design finding's `evidence` may cite code paths beside its frames — and one
that placement does not settle belongs to none here. **Never re-mark a block already reading
`SUPERSEDED`**: its verdict is already retired, and a second write would record `SUPERSEDED` as its
`prior_verdict`, which `workflows-core:grounding-format` §2 forbids. Without this rule a
second `--no-code` run over a changed frame set appends a whole new finding set beside the stale one,
both unmarked — or, where the changed set now agrees with the inventory, appends nothing and leaves
the stale one standing alone — and `/brd-split` sees the set recorded `ground` and passes. `--rebaseline` cannot be
the answer here: it is a code-pin concept and `--no-code` refuses it outright, so the supersession
that mode needs has to be its own rule rather than a flag.

A run with no `design/` folder, or an empty one, writes the section with an explicit "no frame sets
on disk" line rather than omitting it. **The section is what makes design coverage checkable at
all**: `/brd-split`'s design-presence gate compares the subdirectories on disk against the names
recorded here, and a relation with nothing on one side fails rather than passing
(`workflows-core:grounding-format` §2.1's reading rule). Omitting a set because it was skipped is
what would make that gate report a clean tree it never read.

**Documentation divergences (only when Phase 4.5 ran).** Append a `## Documentation divergences`
section to `<BRD-dir>/grounding/code-grounding.md` — appended there, like the derivation matrix
below, because it is not a produced artifact in its own right. One prose entry per divergence, each
carrying: the documentation page (path relative to the resolved `docs_root`), what it states, and
the **`[CG#n]` whose verified evidence it diverges from**, quoted by id. **No entry gets an
identifier of its own, and no entry may exist without naming a verified `[CG#n]`** (Phase 4.5) —
so a divergence is always the code contradicting a page, established by a finding, never a page
asserting anything about the code. A run with docs grounding ON that found no divergence writes the
section with an explicit "none found" line rather than omitting it; a run with it OFF writes no
section at all. Nothing in this section is ever copied into a finding's `evidence`, and no ledger
row's `evidence` column ever names a page.

**Derivation matrix.** Resolve whether it runs: an explicit `--derivation-matrix` /
`--no-derivation-matrix` wins outright; otherwise default it **on** when the claim list reads
as reporting- or data-centric (a judgment call this command makes from the claim text — recurring
language about reports, dashboards, exports, extracts, or stored/displayed data fields) and **off**
otherwise. When on, append one implementation-altitude row per data element the claim list asks to
display or store to `<BRD-dir>/grounding/code-grounding.md`, classed per `workflows-core:grounding-format` §7
(`EXISTS | DERIVED | NEW-CAPTURE | NEW-CONFIG | PARTNER | DEFERRED | DEPENDENCY`) — appended there
rather than as a new file, since it is not in this command's produced-artifact set on its own.

**Write the coverage ledger's `evidence` column — `route: brd` only, and in every mode.** This is
the last write of this phase, taken once the two grounding files hold everything this run is going
to put in them, because the column is an index over them and an index built early indexes a file
that is still changing. Rebuild it over **every** row of `<BRD-dir>/coverage-ledger.md`, exactly per
`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §2: parse the finding set out of
`grounding/code-grounding.md` and `grounding/design-grounding.md` **as this phase has just left
them** — §2.1's reading rule, resolved against the blocks actually parsed and never by matching a
column or a fixed run of leading spaces — and write into each row's `evidence` cell the id of every
finding whose `claim` names that row's `[BR#n]`, in id order, as `brd-format.md` §2.3 writes a list.
A row no finding names takes an empty cell, which is the whole of what an orphan row gets
(`coverage-ledger-format.md` §2). **A finding that names no requirement lands in no cell** — the
class-1 `[DG#n]`, which reconciles a frame against no requirement at all
(`workflows-core:grounding-format` §6.3, written with the `claim` spelling
`agents/design-grounder.md` fixes for it): it is not a gap in the column, and it is not to be
attached to a row on a resemblance. **Read
each `claim` for the id it names rather than for the id it opens with** — a hand-edited block may
carry the id mid-sentence, and a claim naming more than one requirement is reported as the ambiguity
it is rather than placed in one row (the same test `references/bundle-packaging.md` §6.2 relation 2
makes of a citation). **Nothing else in the row is touched** — `id`, `text`,
`disposition` and `defects` are read and written back unchanged, and this command allocates nothing
and disposes nothing (`coverage-ledger-format.md` §3, §4). **A finding carrying
`verdict: SUPERSEDED` is listed like any other**: the column indexes and does not adjudicate, its id
still resolves, and a column filtered by verdict would disagree with the file it indexes. **A count
that disagrees with the file is a parse failure and is reported as one, never as an absent
finding** — the same rule `workflows-core:grounding-format` §2.1 states for every reader of these
records, and the reason the write is a rebuild rather than an append: a run that appended would
double every id a re-run re-derived. **Under `--no-code` this write still happens**, over the
`[DG#n]` this run wrote and the `[CG#n]` already on file, because a column that skipped this mode
would never index a design finding at all. **On `route: idea` it does not happen and is not a
gap**: that route has no `coverage-ledger.md` to write (the Final report's own ledger line says so).

---

## Phase 9 — Handoff

Invoke `Skill(skill: "workflows-core:reference", args: "phase-handoff")` and present its §4.3 choice array verbatim — the **gated — stopping** variant (§4.1 bullet 1), **in every mode including `--no-code`**:

```
choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (the next phase will stop until this is on main)", "Cancel"]
```

**Why the same array under `--no-code`, where `code-grounding.md` is not in the set.** §4.0's rule is that a handoff spanning classes takes the strongest class in it, and both artifacts a `--no-code` run hands off are classed: `grounding/design-grounding.md` is **gated** — §3.4 carries a conditional `/brd-split` row for it, and that command executes `require-on-main` against it wherever the BRD has frame sets on disk. So the promised stop is real in both modes, and the operator who declines will meet it. This array was hardcoded here before `design-grounding.md` was classified at all, which made it right by luck on a full run (`code-grounding.md` rode in the set) and wrong on a `--no-code` one; it is now right for the stated reason in both.

On the first choice, execute `handoff-to-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main")`, §2) with `prefix: brd` **on `route: brd`** (shared
by every `/brd-*` command, per `brd-intake.md`'s own precedent) or **`prefix: prd` on `route: idea`**
(shared with the other commands `workflows-core:phase-handoff` §2.9's `prefix` row names — that row
is the authority on the set and is deliberately not copied here, since a second list is how two
lists come to disagree — per that section's own precedent for one prefix serving more than one
command; the eight-prefix branch authority in `workflows-core:specs-repo-git` §1 and
`workflows-core:phase-handoff` §1 rule 3 is unchanged, and no ninth prefix is added). **Sharing
`prd` is disposed of rather than excluded, and the difference is what this paragraph used to get
wrong.** Step 6i's `require-on-main` on `<PRD-dir>/prd.md` rules out exactly one sharer —
`/product-workflows:create-prd`, whose own `prd/<KEY>-<slug>` branch must already have merged for
this run to proceed at all. It rules out none of the others: `/product-workflows:update-prd`
executes `require-on-main` nowhere (its own Phase 0 says so outright), and
`/product-workflows:prd-proposal` hands off with `prefix: prd` from the same resolved folder, so
either can hold an open `prd/<KEY>-<slug>` branch while this run starts. What disposes of that is
`workflows-core:phase-handoff` §2.2 rule 3, which calls collision normal rather than exceptional and
**reuses** an unmerged branch whose prefix is the caller's and whose key resolves into the run key
set — so this run commits onto the branch already open instead of onto a second branch of that name.
**The retired claim was that no such window exists**, argued from a gate that reaches only the first
of the sharers §2.9's row lists. `feature_folder` as
resolved in Phase 0; `deliverable_paths` = every file this run wrote or updated under `<PRD-dir>` —

- **`route: brd`:** `grounding/baselines.md`, `grounding/code-grounding.md`,
  `grounding/design-grounding.md`, `brd-link.md`, and `coverage-ledger.md` **where Phase 8's
  `evidence` rebuild changed it** — **under `--no-code` that set is
  `grounding/design-grounding.md`, that same conditional `coverage-ledger.md`, and, where Phase 4
  persisted a prerequisite, `brd-link.md`**: the
  other two are untouched, and naming an unchanged path in a handoff is how a commit comes to claim
  work it did not do. **The ledger is conditional for that same reason and for no other**: the
  rebuild rewrites a column a re-run over an unmoved finding set reproduces byte for byte, so a run
  that changed nothing there declares nothing there — while a first grounding run always changes
  it, every cell it writes having been empty.
- **`route: idea`:** `grounding/baselines.md`, `grounding/code-grounding.md`,
  `grounding/design-grounding.md` — **and no BRD-route file, since none exists**: `brd-link.md` is
  never written on this route (Phase 4's `--depends-on` is refused on it outright, step 2), and
  `coverage-ledger.md` is a file this route has no copy of at all (Phase 8), so neither
  is ever a candidate here in either mode. **Under `--no-code`** the set narrows for the same reason
  it does on the BRD route — to `grounding/design-grounding.md` alone, which is narrower than that
  route's `--no-code` set, since that one still carries the ledger this route does not have — since Phase
  3 and Phase 8 both leave `code-grounding.md` and `baselines.md` untouched under that mode
  regardless of route.

`title: <BRD-KEY> Ground requirements against code and design`, and `body_facts` =
the finding counts by verdict, the verifier agreement/extend/contradict/unprovable tally, and the
prerequisite-readiness block — **on `route: idea` the prerequisite-readiness block is
`prerequisites: none declared` on every run, since `--depends-on` cannot reach Phase 4 there**, and
`body_facts` additionally carries the exclusion count and prefixes step 8i reported (`route: idea`
only); emit its §4.1 outcome line in the final report.

---

## Phase 10 — Next steps

**On `route: idea`, the offer is `/product-workflows:create-ard` and `/product-workflows:specify`
— the two downstream authors of what this run's Phase 0 gated and what its own findings can now seed —
with `/product-workflows:update-prd` named first where any requirement claim this run wrote came
back `CONFIRMED`.** Neither `/create-ard` nor `/specify` is required the way `/brd-split`'s allocation is
below, and neither carries a `(Recommended)` marker over the other where both are simply offered
side by side: a run has as much reason to specify first as to architect first, and marking one would
assert an order this design does not take a position on.

**Where any requirement claim came back `CONFIRMED`, name `/product-workflows:update-prd <KEY>`
first, marked `(Recommended)`.** A PRD asking for something the code already does is worth revising before an
architecture or a specification is authored against a premise this run's own findings have already
settled — and of `workflows-core:grounding-format` §3's closed six, `CONFIRMED` is the one that says
that: *the premise holds, with evidence*. **No other verdict of the six says it** — `AMENDED` says
partly true, `REWRITTEN` materially wrong, `FALSE-FRIEND` a decoy, `NOT-PROVABLE` unsettleable from
the repository, `SUPERSEDED` a finding a later one replaced — and the two §3 names for an absent
mechanism, `NOT-PROVABLE` and `REWRITTEN`, are what this route's greenfield case lands on, the case
the `## Final report` section below already has its own `route: idea` headline for, rather than a
reason to revise anything. **`<N>` counts distinct requirement claims, not findings.** Read the
requirement id off each `CONFIRMED` finding's own `claim` field — the field
`workflows-core:grounding-format` §2 defines, which both grounders' own output contracts fill with
the requirement id as given, ahead of the text — and count the **distinct ids**, so one claim confirmed
in two repositories, or by a `[CG#n]` and a `[DG#n]` both, counts once. **A `CONFIRMED` finding whose
`claim` names no requirement id contributes none**, which is where Phase 3's baseline `[CG#n]` falls
out: its `claim` is not a requirement premise, so nothing resolves it back to a requirement row —
`workflows-core:grounding-format` §4.1 rule 1, the same property on which that section already
excludes baselines from the unconsumed-item report. A class-1 `[DG#n]`, whose `claim` opens `none — frame-only`,
falls out the same way. **That exclusion is what keeps this branch off the greenfield run the
sentence above excludes by name:** a baseline finding is `CONFIRMED` by construction and Phase 3
assigns one per repository that passes its gate, so counting them would hold `<N>` at one or more on
an ordinary run and leave the no-claim array below unreachable. **Neither Phase 9's `body_facts` nor
the Final report supplies this number** — both state *finding* counts by verdict, which count the
baselines and count one requirement claim once per finding that answered it — so count it here, from
the findings Phase 8 wrote. This is where it earns a next step instead of sitting as a fact
nobody acted on (this command never edits `prd.md` itself, design §7).

**`/create-ard <KEY>` and `/specify <KEY>` each carry `<merge-clause>`** — both re-gate the same
`prd.md` this run's own Phase 0 already required on main (step 6i), so an operator who runs either
immediately is running against a file this command has already confirmed is there; the placeholder
still names the wait truthfully for the ordinary case in which that confirmation and this offer are
being read minutes apart. **`/update-prd <KEY>` carries none — deliberately, and for the reason
`workflows-core:next-phase-offer` already gives for `/product-workflows:brd-reconcile`'s own
three-command offer: it never executes `require-on-main` against anything at all**
(`commands/update-prd.md` states this outright — "`require-on-main` … is never executed by this
command"), so there is no gate for this run's handoff to make anyone wait on. Naming a wait that
does not exist would be the placeholder's own named failure — resolving it truthfully, not
unconditionally.

Neither `route: idea` array below needs `workflows-core:next-phase-offer`'s overflow rule for a fifth option: even
the `CONFIRMED` case tops out at four, the harness's own cap, so the array carries the whole menu
and no route is demoted into prose.

No requirement claim `CONFIRMED`:
```
choices: ["Specify it — /product-workflows:specify <KEY> (PE) <merge-clause>", "Architect it — /product-workflows:create-ard <KEY> (PA, optional) <merge-clause>", "Stop here"]
```

At least one requirement claim `CONFIRMED`:
```
choices: ["Revise the PRD first — /product-workflows:update-prd <KEY> (PM) (Recommended — <N> requirement claim(s) came back CONFIRMED)", "Specify it anyway — /product-workflows:specify <KEY> (PE) <merge-clause>", "Architect it anyway — /product-workflows:create-ard <KEY> (PA, optional) <merge-clause>", "Stop here"]
```

**On `route: brd`, this run always stands on a slice** — by the time Phase 10 runs, step 6's gates have already
guaranteed `coverage-ledger.md` and `brd/brd-inventory.md` are both on main, which is positive
evidence 5a's legacy-fallback test would have refused had this BRD been a root — so there is no
level branch to take here. **Which of the two arrays below is presented** is settled by the test
that follows.

**That offer carries one qualifying test, and this run holds the answer to it.** `/brd-split`'s
Phase 0 step 7, test b stops on any `design/` subdirectory this run recorded `skipped: no index`, and on any
it could not cover. So where Phase 8's `## Frame sets covered` section carries such a row, present
the **second** array below in place of the first: `/brd-split` would refuse the key just ground, so
the array recommending it is not the array to show. The second offers the repair that stop itself
names — `/workflows-core:frames <BRD-KEY>` to write the missing index, after which a `--no-code`
re-run of this command reconciles the set — and names `/brd-split` nowhere in its options, since
neither half of that repair has run yet; the prose above the arrays still says where it sits in the
route, which is what `workflows-core:next-phase-offer`'s universal minimum asks of a route the array
does not carry. **Selecting between two written arrays is how this branch is taken, never by editing
one**: `workflows-core:escalation-rules`' *Choice lists are presented verbatim* puts an array's
options, their order, their wording and the `(Recommended)` marker outside the orchestrator's
authority, and this phase's `route: idea` branch above already selects between two arrays the same
way. **Neither array's marker names a precondition of `/brd-split`'s own gate.** That command applies
four tests at step 7, and a marker naming one of them — an earlier wording of this offer read
"once every finding carries a verifier outcome" — promises a pass the offer cannot deliver; each
marker below states what the run it recommends will *do* instead.

`/product-workflows:brd-split <BRD-KEY>` allocates this slice's own ledger, and it is the last step
that has to run before this BRD's requirements all carry a recorded fate — **it is not the end
of the route**. `/product-workflows:brd-interview <BRD-KEY>` follows it, and `/brd-split`'s own Phase 7
is what offers it, so it is not offered here: putting it in this list would name a step out of
order, since it refuses a ledger that still holds an unallocated row. `/brd-split` will not start
until this phase's findings are on the specs repo's default branch — its own Phase 0 gates
`grounding/code-grounding.md` on `origin/<default>`; **which words state that wait, in the array that
offers it, are `<merge-clause>`'s**, resolved from this run's own `Phase handoff:` outcome line per
`Skill(skill: "workflows-core:reference", args: "next-phase-offer")`, since a declined handoff opened no pull
request to wait on — and it carries its own role and
cost-attribution row (`docs/roles-and-phases.md`). Guidance only, per
`workflows-core:next-phase-offer` — names only that `/brd-split` exists and
where it sits in the route, never its behaviour, which `commands/brd-split.md` owns.

**The array that offers it says which of `/brd-split`'s two modes will run**, so nobody
expects a fan-out that cannot happen: on a slice it runs `allocate-only`
(`commands/brd-split.md` Phase 0 step 5) — it creates no child, because nesting is
capped at one level (`workflows-core:addressing` §6), and walks this
slice's ledger to a recorded fate through its own four resolutions, `covered-by` being the
one that command's walk does not offer on a slice. Allocating is what
makes this slice PRD-eligible
(`${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §5), so it is a real next step, not a
formality.

No frame set left unreconciled — every one on disk recorded `ground` or `skipped: --no-design`, or `design/` holds none:
```
choices: ["Allocate this slice's ledger — /product-workflows:brd-split <BRD-KEY> (Recommended — allocate-only, so no child is created) <merge-clause>", "Ground another declared prerequisite first", "Stop here"]
```

At least one frame set recorded `skipped: no index`, or on disk and missing from Phase 8's census:
```
choices: ["Write the missing frame-set index — /workflows-core:frames <BRD-KEY> (Recommended — nothing can reconcile a frame set that has no index; re-ground it here with --no-code afterwards)", "Ground another declared prerequisite first", "Stop here"]
```

### Context hygiene

The resume pointer is written in the terminal cost phase (Phase 11), per
`workflows-core:session-hygiene` §1. Grounding another repository or
prerequisite in the same BRD? → run **`/compact`**. Handing off to `/brd-split`, even yourself? →
run **`/clear`** (`route: brd`). Grounding another repository for the same PRD? → run
**`/compact`**. Handing off to `/create-ard` or `/specify`, even yourself? → run **`/clear`**
(`route: idea`). Guidance only — nothing is auto-run.

---

## Phase 11 — Session maintenance, feedback & cost

Terminal phase — runs after Phase 10, NEVER interrupts an earlier phase.

**Capture-at-block invariant.** If an EARLIER phase halts on a plugin / skill / command /
reference gap, `emit-block` (`workflows-core:feedback-emission`) fires at
that halt before escalating. **None of Phase 0's stops qualify — every one is a user, sequencing or
environment halt, never a plugin capability gap** — for example a missing key, an unresolved BRD,
a resolved root BRD or Epic folder, an input not yet on main (`PRD_GROUND_NO_INVENTORY`, `PRD_GROUND_INVENTORY_NOT_HANDED_OFF`,
`PRD_GROUND_NEEDS_INTAKE` or, for a slice, `PRD_GROUND_NEEDS_SPLIT`; `PRD_GROUND_NOT_HANDED_OFF` where they exist and were never handed off; `PRD_GROUND_CARVE_UNFINISHED` where the parent's carve that wrote them has not finished; `PRD_GROUND_SLICE_UNRECONCILED` where the slice does not agree with its parent's ledger, or that ledger cannot be read; `PRD_GROUND_RESTORE_FROM_DEFAULT` where they are on the default branch and missing from the worktree; `PRD_GROUND_SLICE_FILE_UNREADABLE` where one is in the folder and cannot be read;
`PRD_GROUND_NEEDS_PRD` and `PRD_GROUND_PRD_NOT_HANDED_OFF` on the idea route), a key naming the wrong
folder (`PRD_GROUND_CARVE_INTERRUPTED`, on an empty folder a carve created and never linked, and `PRD_GROUND_LINK_MISSING`, on a slice that lost its `brd-link.md`; the no-parent forms of `PRD_GROUND_NO_INVENTORY` and `PRD_GROUND_NEEDS_INTAKE`, on a folder
that is neither a slice nor a BRD container — an argument halt, not a missing input, save on a
legacy folder holding an `idea.md` and no `prd.md`, whose missing input is the PRD),
an inventory carrying no claim at all
(`PRD_GROUND_EMPTY_INVENTORY`, which is a fact about what the
parent allocated, not about this plugin), and an unset `$REPOS_PATH`. The list is illustrative and
the rule is what binds: a Phase 0 stop added later is covered by it without being named here. `PRD_GROUND_DIRTY_TREE`, `PRD_GROUND_NEEDS_REBASELINE`, and Phase 7's
`PRD_GROUND_VERIFY_COMMIT_MISMATCH` are repository state, not a plugin gap, either — unlike Phase
7's `INPUT_MISSING`, which is this command getting its own dispatch contract wrong, and
`PRD_GROUND_VERIFY_INCOMPLETE`, which is the verifier getting its return contract wrong: both do
fire `emit-block`.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 2's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model:
   `<detection_model>`) with a compact handoff: command `/prd-ground`; what was produced (baselines,
   code/design findings, verifier tally, prerequisite readiness, documentation divergences); key
   events (a dirty-tree stop, a rebaseline, a skipped design pass, an unresolved repo, docs
   grounding OFF or a lead that added a repository — or "none"); workarounds; test result
   N/A; project root = the BRD folder.
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6) with the Lessons Learned report, `command: /prd-ground`,
   the run's `key` (the `<BRD-KEY>`), `source`, and `plugin_version` (read from
   `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). Surface the persisted path (or "no
   plugin-facing signal — nothing persisted").
3. **Session cost (ALWAYS runs).** **Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way. Otherwise, invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call its `emit-cost` entry point with `command: /prd-ground`, `phase: brd-to-prd`, `role: pa`,
   the run's `key`, `source`, and `plugin_version`. Surface the persisted path (or the
   report-only notice).
4. **Write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` and, per its §1, write/overwrite `<BRD-dir>/dev-workflows/resume.md` now — after the cost entry, before the
   commit step below. Redact per §1. Silent.
5. **Commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. Stages
   ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH`, commits
   `<BRD-KEY> Add dev-workflows session artifacts (/prd-ground)` with no `Co-Authored-By` trailer,
   and pushes to the branch Phase 9's handoff created. NEVER touches a code repo, or the current working directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; skips entirely when the run
   carries `specs_git: blocked`, re-emitting that notice. Hold its §6 outcome line for the final
   report.

ADDITIVE — this phase NEVER fails the run, NEVER commits the deliverable (git for the deliverable
is offered only in Phase 9), and NEVER writes into a code repo, or the current working
directory, where it is not the specs repository; no user name is ever written.

---

## Final report

Report: the BRD or PRD folder + resolved repositories (with each one's pinned commit); the
classification
and model routing (+ any Opus degradation, or `Model routing: bypassed — enforced <id> (flag|env)` in its place wherever `run_flags.enforced_model` is set, per `workflows-core:model-routing/classification` §10) — including `ground_tier`, the tier the `[CG#n]`/`[DG#n]`
corpus was actually ground at, stated as its own line on every run rather than only on a degraded
one, because a reader cannot otherwise tell an Opus corpus from a degraded one and the two are not
interchangeable evidence; the prerequisite-readiness block from Phase 4, verbatim
in the two-column form Phase 4 step 3 fixes (on `route: idea` this is always `prerequisites: none
declared`, per step 2's refusal); every on-file finding Phase 6 superseded for a moved horizon,
with its successor's id and both horizons — or, for a design finding no frame set places, with no
successor and the horizon it would have written — and every `--no-code` horizon it did not move;
finding counts by verdict for `[CG#n]` and `[DG#n]`
separately, and the verifier
tally (`agree` / `extend` / `contradict` / `unprovable`) with every `contradict` named by id and by
what it wrote — an own-run finding's in-place rewrite; an on-file finding's supersession with its
successor's id; an on-file finding superseded with no successor because the verifier's own verdict
was `SUPERSEDED`, the one `contradict` no block records; and an incomplete return on an on-file
finding, owing a control and returning none, which wrote nothing and leaves that finding **not
verified by this run** — say so of it by id, beside the `outcome` an earlier run left on it (on an
own-run finding the same return stops the run instead, with `PRD_GROUND_VERIFY_INCOMPLETE`) —
**and, separately, every outcome Phase 7 normalised**, each named by finding id with the outcome
as returned, both verdicts, and which of the two routes forced it (a differing `own_verdict`, or a
`control_outcome` of `missing`, or of `failed` on a finding whose verdict rests on the absence), or an explicit "none" where the verifier and the findings agreed
throughout, so a clean run reads as checked rather than as unchecked; the class-4 sweep's result in every state it reached — every `[DG#n]` re-derived, every one
re-checked and left standing, and, where it did nothing, which of the three reasons applied: an
empty set; a non-empty one over which this phase rewrote no `[CG#n]` at all; or a non-empty one
where `[CG#n]` **were** rewritten and no finding in the set cites one of them; every class-4
`[DG#n]` Phase 8's cascade marked `SUPERSEDED`, each with the `[CG#n]` that took it there, the route
that superseded that `[CG#n]` and the run its note names as replacing it; the `docs grounding:` line from Phase 1 step 0 verbatim, any repository a Phase 4.5 lead added,
and the count of documentation divergences recorded (each named by the `[CG#n]` it diverges from —
never by an identifier of its own, because it has none); whether the derivation matrix ran and why; any `design-grounder` class-4 gap deferred for want
of a settling `[CG#n]`; **on `route: idea`, the claim-exclusion count and prefixes step 8i
reported** — "11 of 19 requirement rows ground; 8 excluded — 3 `[UC#n]`, 5 `[SM#n]`/`[SMC#n]`" or
the like, carried here verbatim so a reader of the write-up alone, without the transcript, still
cannot conclude the PRD was fully ground; the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6); the feedback path (or, under `--skip-feedback`, the `Session feedback: …` line) and cost path (or, under `--skip-costs`, the `Session cost: …` line); the `Phase handoff:` outcome line
(`workflows-core:phase-handoff` §4.1); the `Specs repo:` outcome line (`workflows-core:specs-repo-git` §6); the next-step
recommendation; and end with —

**On `route: brd`** — the ledger line, read fresh from `coverage-ledger.md` as Phase 8 left it,
exactly per `${CLAUDE_PLUGIN_ROOT}/references/coverage-ledger-format.md` §6:

```
ledger: <N> requirements — <covered> covered, <deferred> deferred, <rejected> rejected, <unallocated> unallocated, <unresolved> unresolved (<delegated> delegated, <not-built> not built)
```

`/prd-ground` never changes a ledger disposition — that line simply reports where allocation stands
going into `/brd-split`. **Phase 8's `evidence` rebuild is the one cell this command does write, and
it moves no figure in the line**: §6 counts rows by their `disposition`, so a column that carries no
disposition cannot change a count. Report the rebuild separately and by number — how many rows took
at least one `[CG#n]`/`[DG#n]` id and how many were left with an empty cell — because the second
figure is the one that says which requirements this grounding run did not reach, and it is the
figure the customer would otherwise have to infer from an empty column.

**On `route: idea`** — no ledger line at all; there is no `coverage-ledger.md` on this route to read
one from. **Where every claim this run ground came back a verified absence, say so outright instead
of listing the absences as though they were a mixed result** — "this PRD is greenfield against the
repositories resolved: every `[AC#n]`/`[FR#n]`/`[US#n]` claim ground came back a verified absence" or
the like, as the run's own headline finding rather than a wall of `NOT-PROVABLE`/absent verdicts a
reader has to add up themselves. This is worth having once, and a second run over the same greenfield
folder — with nothing built in the interim — is exactly what stating it plainly here exists to
prevent (design §9). Where at least one claim came back anything other than a verified absence, this
line is simply omitted; a mixed result speaks for itself in the verdict counts already reported above.

**On `route: brd`, reporting it can read ledgers beyond this slice's own.** This run always stands
on a slice — by Final-report time, step 6's gates have long since guaranteed `coverage-ledger.md` and
`brd/brd-inventory.md` are both on main, positive evidence 5a would have refused had this BRD been a
root — and a slice does **not** always reach this with nothing to resolve: it can hold **orphan
rows** (`coverage-ledger-format.md` §2) — ledger rows for a `[BR#n]` this slice no longer claims,
reached by any of §2's three routes. §6.1 counts every one of them through the parent's current
disposition for its `[BR#n]`, never as it reads, and resolves a `covered-by` that disposition maps
to one hop — into a sibling or the parent (`coverage-ledger-format.md` §3) — exactly as it resolves a
parent's delegated rows. So this report reads `<PARENT-KEY>`'s own `coverage-ledger.md` and each
ledger such a mapping names, resolved from the working tree by `resolve-address`
(`Skill(skill: "workflows-core:reference", args: "addressing resolve-address")`, §3). **This adds
no precondition and no gate.** A folder that is absent from the tree this run is standing in — its
split not yet merged, most commonly — makes that row `unresolved` in the line and nothing more:
grounding this BRD does not depend on any other, and a run must never stop, degrade, or withhold its
findings because another ledger could not be read. Phase 0's `require-on-main` gates stay exactly as
they are, on this BRD's own inventory and ledger. A slice's line reports zero delegated only when
its parent withdrew none of its claims — provisional, committed, or settled here before the parent
re-allocated it, the three routes to an orphan row (§2) — never as a property of being a slice.

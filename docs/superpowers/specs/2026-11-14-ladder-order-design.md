# LADDER-ORDER — a command stops when the document it builds from is missing

**Date:** 2026-11-14. **Status:** design, for approval. **Track:** the LADDER-ORDER entry of `docs/superpowers/to-fix.md` (*Design-level*). **Base:** `main` at `34f4068f` (`workflows-core` 1.88.0); every line number below is at that commit. Below, PH is `plugins/workflows-core/references/phase-handoff.md`, ARD is `plugins/product-workflows/commands/create-ard.md`, SPEC is `plugins/product-workflows/commands/specify.md`, CPRD is `plugins/product-workflows/commands/create-prd.md`, IMPL is `plugins/dev-workflows/commands/implement.md`, DOC is `plugins/docs-workflows/commands/document.md`, CONF is `plugins/dev-workflows/commands/conformance.md`, and *the gate* is `require-on-main` (PH §3).

## 1. Intent

A command typed for a key whose earlier phase never ran is a mistake: it has nothing to build from. The maintainer raised this on 2026-11-13 and wants such a command to stop and name the command to run first.

Today the family catches only half of the case. A document that an earlier phase wrote and left on an unmerged branch stops the gate's callers (PH §3.3 rows D and E), save `/ready`, and `/brd-reconcile` and `/brd-interview` at the sites PH §3.7 names, which read that row without stopping. A document that was never written returns `absent` (row F), and each caller then does what PH §3.4's table says for it, which for several callers is to carry on from whatever the folder holds. Four commands carry on with nothing:

- `/create-ard` and `/specify`, on the idea route, with no `prd.md`;
- a keyed `/implement`, with no specification, or with a specification and no design;
- `/document <KEY>`, with nothing implemented.

This design makes the first three stop, and makes `/document` ask before it goes on. It also closes the matching hole on the BRD route, where `/create-ard` and `/specify` run today on a slice that was never grounded or allocated.

It does not make every rung of the ladder mandatory. The steps the family treats as optional stay optional (§6).

## 2. Decisions

**The maintainer's, 2026-11-14.** Each was put as a question with the alternatives sketched, and M2 follows from the choice made at M1.

| # | Decision |
|---|---|
| M1 | **A command stops when the document it builds from was never produced.** Not every rung: `/idea`, an ARD on a single-component PRD, Epics, and the PRD-level specification `/epics` reads stay optional, and on the BRD route no `prd.md` is required. The alternative refused was *every rung of the ladder*. |
| M2 | **It stops; it does not ask.** The alternative refused was a *Stop (Recommended) / Go on without it* question. |
| M3 | **A keyed `/implement` needs both a specification and a design**, on every run for the unit, a later run included. A unit built earlier without a design stops when a follow-up is run for its key; the maintainer accepted that cost. A direct `/implement`, with no key, stays the way to make a small change with no documents. The alternatives refused were *a specification is enough* and *both on a first run only*. |
| M4 | **On the BRD route, `/create-ard` and `/specify` take the two coverage-ledger tests `/create-prd` already applies to a slice.** No `prd.md` and no decision register is required there. The alternatives refused were leaving the route as it is, and requiring `decisions.md`, which a slice whose interview raised no question legitimately lacks (`plugins/product-workflows/commands/brd-interview.md:708`, *No question at all → open no round*). |
| M5 | **Built as per-command stops on the check each command already runs** (§9, approach A). |
| M6 | **`/document <KEY>` asks, with *Stop* recommended; it does not stop outright.** The one exception to M2, on a principle the maintainer accepted: a run stops where the test is exact, a file being there or not, and asks where the test is only a signal. No implementation record and no commit naming the key can mean *not built* or *built by hand without the key in its commit messages*, and the command says of its own scan that a zero match is *not proof that no work happened* (DOC:489). The alternatives refused were stopping outright, which would leave a team that codes by hand no keyed documentation run at all, and leaving `/document` out. |
| M7 | **LADDER-ORDER is built now, ahead of GIT-G1 Part 3's batch 2**, against today's text. Part 3's batch 2 is then planned against whatever `main` holds. |

**The lead's calls**, each from what the project already says. The maintainer checks these while reading.

| # | Call | Why |
|---|---|---|
| L1 | **A required document that is in the folder and on no ref stops too**, in a form of its own whose remedy turns on whether the file is committed (§4): an uncommitted file is landed on a new branch, and a file committed on a branch no plugin prefix names, or on a local default branch not pushed, has that branch pushed and merged. | `CLAUDE.md` § Hard constraints: a phase is not finished until its artifact is on the default branch. `/prd-ground` and `/prd-proposal` already split row F this way (PH:335, PH:336). One consequence, stated to the maintainer: someone who keeps a PRD on a branch of their own in the specs repository is told to merge it first. PH §4.4's row-F commands serve only the uncommitted file today, which is why the remedy is split. A known limit, unchanged: a document committed on a branch no plugin prefix names, while the checkout stands elsewhere, is in no folder and on no ref the plugin scans (PH:314), so it reads as never produced. |
| L2 | **`/document <KEY>`'s question (M6) is put only where the implementation record holds no block in the run's scope and the commit scan found no commit.** Where no entry of `$REPOS_PATH` is an existing directory, the run asks where the repositories are before it concludes anything (§5.3); a scan the user then chose not to make has found none, and the question says it did not look. The report-only probe's matches and a pull request the scan lists and does not read (DOC:483–495) are not commits found; the lines above the question print them. | Either source alone misses real work: a `--no-commit` run writes no block (IMPL:34), and the scan exists to find a commit written by hand (DOC:476). The probe's matches are, by that section's own words, where to look and nothing the run reads. |
| L2a | **That question is put at the start of the run, not in Phase 3.** | Phase 3 comes after the inline `/docs-profile`, which can cut a branch and commit in the documentation repository (DOC:227–254, Phase 0 step 4(c)), after Phase 1's questions and after Phase 2's plan approval. A run should not approve a plan and then be told nothing was built. |
| L3 | **`/release-notes` is unchanged.** | Its `pm` stage is built to draft from the PRD before anything is implemented (`plugins/docs-workflows/commands/release-notes.md:200`, *neither present → `run_phase: pm`. The feature is not built*). |
| L4 | **An `EPIC-` folder holding no `epic.md` is unchanged**: `/create-ard` and `/specify` still report it and read what the folder holds. | Measured population: `/epics` is the only command that creates an `EPIC-` folder, and it writes `epic.md` into each (`plugins/dev-workflows/references/workflow-states.md`, *Refine — one way in*). No run of the family reaches the state. |
| L5 | **`/update-spec` is untouched by all four batches**: no never-produced stop, no not-handed-off form for the PRD, no ledger test. | It builds from its own base, `specification.md`, and already stops without one (`UPDATE_SPEC_NO_BASE`). A specification written before this rule may have no PRD above it, or stand on a slice that would fail the ledger tests today, and stopping its revision would strand it. It needs an edit all the same, since it runs `/specify`'s gate sections by citation (§5.1). |
| L6 | **`/implement`'s specs question goes whole** (IMPL:316–321): *Point me at a specs directory* and *Proceed without specs* both. The stop names the ways out, a direct run among them. | M2. A keyed run that reads its documents from somewhere other than the unit's folder writes a record under a key whose folder does not hold what was built from. |
| L7 | **On a specs tree the plugin does not manage** (the gate's row H: `$SPECS_PATH` is no git repository), the test is the folder's own file. Present, the run goes on; absent, it stops in the never-produced form. | Row H skips the gate, so there is no ref to test, and the rule is about the document, not about git. |
| L8 | **No picker and no next-step offer names or recommends a run that would stop on arrival**, for the folder the offering run has just read. A `### Next step` line is such an offer: `/conformance`'s and `/security-workflows:scan`'s lines naming `/dev-workflows:implement <KEY>` (CONF:560, CONF:572; `plugins/security-workflows/commands/scan.md:550`) name it only where the unit's specification and design are on the default branch, and the command for the earliest gap first otherwise. A follow-up line written into a record for a later run (CONF:317) is not, and keeps its text: on a unit built before this rule with no design, the run it asks for stops and names `/design`, the cost M3 accepted. | The family already holds this rule at SPEC:609 (*offering it … would name a run that stops on arrival*). Each new stop makes some existing offers false (§7). |
| L9 | **A PRD-level `/conformance` with no implemented unit is traced first, then fixed in batch 2 if it runs on.** | The trace could not settle it (§3). The Epic-level run already stops (`CONFORMANCE_NOT_IMPLEMENTED`, CONF:119), and a defect found in passing is fixed before the push. |
| L10 | **Four batches, one pull request each, built in §5's order**, the BRD route last and alone. | The internal editions do not carry the BRD route, so batches 1 to 3 port and batch 4 does not. The order is fixed because each later stop names a command an earlier batch changed (L12). |
| L11 | **`/implement <PRD>`'s picker leaves out an Epic that would stop**, counts the Epics left out and names the command each needs, as `/design`'s picker does for an Epic with no specification (`plugins/dev-workflows/commands/design.md:122`, *listing every spec'd Epic*). The test is the stop's own: both files on the default branch. | L8, and one precedent in the family instead of a second picker rule. A test on the working tree would still offer a row that stops as not handed off. |
| L12 | **A stop names what the earliest document not on the default branch needs, not what the nearest one needs.** The order is `prd.md`, then `specification.md`, then `design.md`, and each is read by its state (§4): one that is nowhere names its producing command, save a `prd.md` on a slice, which is not required; one that is in the folder and not landed names its landing, never its producer. So `/implement <KEY>` typed on a folder that holds only an idea names `/create-prd`, not `/specify`, which would stop in turn; and typed where a `prd.md` was written and its handoff declined, it says to land that file. The same holds wherever a command names `/dev-workflows:implement <KEY>` as what to run: `CONFORMANCE_NOT_IMPLEMENTED` (CONF:119), the line `/document`'s *Stop* prints, and L8's next-step lines. On a slice, once batch 4 has made `/specify` stop on the ledger, the command `/implement` names is what the ledger tests resolve, read as IMPL:219 and DOC:146–164 already read them, through `workflows-core:next-phase-offer`'s *`/epics` precondition*. | The anti-goal of §8: a stop that names a command which stops on arrival sends the user round twice. |
| L13 | **`/epics` still reads `prd.md` from the working tree, ungated.** Its offers of `/specify <EPIC>` and `/create-ard <EPIC>` (`plugins/product-workflows/commands/epics.md:1124`) say to land the PRD first where it is not on the default branch. | PH:449 records this as decided: a command that knowingly reads the worktree *asserts nothing false and needs no gate*. Gating it would reverse a second written rule nobody asked to reverse. The maintainer can overrule this; it is the one place the review found where L1's reasoning could be carried further. |

## 3. What was measured

Two read-only traces of the command files on 2026-11-14, their citations spot-checked by the lead. *Idea route* is a `PRD-` folder with no `brd-link.md`; *slice* is one with it.

| Typed | State | Today | Evidence |
|---|---|---|---|
| `/create-ard <KEY>` | idea route, folder found, no `prd.md` on any ref or on disk | prints one line and authors from the grill and the code scan | ARD:274, ARD:429 (*An absent `prd.md` is reported and never a stop, on either route*) |
| `/create-ard <KEY>` | `prd.md` on disk, on no ref | row F is not split: reads the working copy and goes on | ARD:274, ARD:418 |
| `/create-ard <KEY>` | slice, no `prd.md` | the ordinary state; goes on | ARD:263, ARD:431 |
| `/create-ard <KEY>` | slice with no `prd.md`, no seed, no register, no grounding | goes on, each absence reported | ARD:482, ARD:516, ARD:560 |
| `/specify <KEY>` | idea route, no `prd.md` | prints one line and goes on; with no Epic folder it asks, recommending `/create-prd` first, with *Author one broad PRD-level spec now* still offered | SPEC:315, SPEC:542, SPEC:603–627 |
| `/specify <KEY>` | slice with nothing in it | goes on, each absence reported | SPEC:719, SPEC:767, SPEC:801 |
| `/create-prd <KEY>` | slice | stops unless the ledger is readable, no claimed row is `unallocated` and one is `covered-here` | CPRD:268–336 (`CREATE_PRD_BRD_UNALLOCATED`, `CREATE_PRD_BRD_NOT_ELIGIBLE`) |
| `/implement <KEY>` | unit folder holds neither `specification.md` nor `design.md` | asks: *Point me at a specs directory* / *Proceed without specs — not recommended* / *Cancel* | IMPL:316–321 |
| `/implement <KEY>` | `specification.md`, no `design.md`, single-component PRD | goes on, silently | IMPL:279 (`specs` holds the files present), IMPL:324 |
| `/implement <KEY>` | the same, on a multi-component PRD, Epic unit | asks once at Phase 1, *Stop* recommended | IMPL:375 |
| `/implement <KEY>` | a spec or design on disk, on no ref | the gate returns `absent`: *do not stop; behave exactly as before* | IMPL:324 |
| `/implement <PRD>` | no Epic folder | offers *Implement one broad PRD-level slice anyway* even with no flat specification | IMPL:219, IMPL:270 |
| `/document <KEY>` | no block, and the commit scan finds nothing | no stop and no question found; the planner and writer run on the PRD alone | DOC:456–495, DOC:544, DOC:740 |
| `/conformance <EPIC>` | no block | stops, `CONFORMANCE_NOT_IMPLEMENTED` | CONF:118 |
| `/conformance <PRD>` | no Epic holds a block, and Epic `target:` lines resolve to clones | **not determined.** The merged test runs on each repository's latest block (CONF:138) and there is none; `implementation-format` §5's *merged* reads vacuously true | CONF:105, CONF:138 |
| `/security-workflows:scan <KEY>` | no block for this repository | stops, `SECURITY_NO_IMPLEMENTATION`; `--triage` and `--verify-fixes` read the register and need none | `plugins/security-workflows/commands/scan.md:114`, `:162` |

Three facts that shape the rule:

- **A folder is found by key only once a file in it carries the key** (`workflows-core:addressing`, the carrier filter). So on the idea route, *folder found, no `prd.md`* means `/idea` ran and `/create-prd` did not. A key that resolves to no folder already stops every command here but `/create-prd`, which creates it.
- **On the BRD route the seed files are not the PRD's stand-in.** `prd-seed.md`, `ard-seed.md` and `spec-seed.md` have one writer, `/brd-intake --sort-existing`, and their absence is the ordinary state (ARD:451–456, SPEC:686–691, CPRD:527). What carries the route is the slice's `decisions.md` and its grounding files, and a finished slice can lack the first (M4).
- **`/create-ard` and `/specify` already compute `/create-prd`'s ledger tests**, to word their next-step offers (ARD:833–836, SPEC:616–627). They do not apply them to themselves.

## 4. The rule

**A command that builds from a document stops where that document is not on the default branch.** Which document each command builds from is §5's table and nothing wider. Two limits on that sentence, both below: on a slice no `prd.md` is required (§5.1), and on a specs tree the plugin does not manage the test is the folder's own file (L7).

A required document is in one of these states:

| State | How it is told | What the run does |
|---|---|---|
| On the default branch | the gate passes (rows A, B) | goes on, as today |
| On an unmerged plugin branch | the gate's rows D and E | stops, as today: nothing here changes |
| In the folder, on no ref, uncommitted | the gate returns `absent`, the file is in the folder, and HEAD does not hold it (`git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>"` fails) | **stops**, `*_NOT_HANDED_OFF`: land the file that is on disk, by PH §4.4's row-F commands. The message never names the producing command, since a re-run would author a second document (the reason PH:335 gives for `/prd-ground`) |
| In the folder, on no ref, committed | the same, and HEAD holds it: a branch no plugin prefix names, or a local default branch not pushed | **stops**, the same id, with the other remedy: push that branch and merge it, or push the default branch, each with the alternatives PH §4.4 already words for its other rows, a local merge where there is no `origin` and a new branch and pull request where the default branch is protected. PH §4.4's row-F commands would fail here, since the switch they open with takes the committed file out of the working tree |
| Nowhere | the gate returns `absent`, and the file is not in the folder | **stops**, `*_NEEDS_*`: names the command to run, with the key (L12) |
| Unmanaged tree | the gate's row H: `$SPECS_PATH` is no git repository | the folder's own file decides (L7): present, the run goes on; absent, it stops in the never-produced form |

The gate itself does not change. It still returns `absent` on row F and still never stops on it; what changes is three callers' own mapping of `absent`, `/create-ard`'s, `/specify`'s and `/implement`'s, in three rows of PH §3.4. The other stopping rows of PH §3.3 (I, G, B′, the C rows) are untouched.

Every stop of a gate caller is taken where its gate already runs, which PH §5 rule 2 puts before the run's first subagent dispatch, code scan, docs-grounding retrieval or grill question. `/document` is no gate caller, and §5.3 says where its question sits.

**The stops that already exist have the same flaw, and each is fixed in the batch its route belongs to.** PH §4.4's row-F paragraph states the commands, and each existing `*_NOT_HANDED_OFF` stop writes them out again in its own command file (`prd-ground.md:559–566` is one), so a form added to PH reaches none of them by itself. Batch 1 adds the committed form to PH §4.4 row F and to the two idea-route stops, `PRD_GROUND_PRD_NOT_HANDED_OFF` and `PRD_PROPOSAL_PRD_NOT_HANDED_OFF`. Batch 4 adds it to the BRD-route ones, which `grep -rn NOT_HANDED_OFF plugins/*/commands/*.md` lists across `brd-package.md`, `brd-proposal.md`, `brd-reconcile.md`, `create-ard.md`, `create-prd.md`, `prd-ground.md` and `specify.md` (L10).

Every stop follows PH §4.4's stop contract, its four parts in order: what was found, what the run did not do, the exact commands, and what happens if it is ignored. A never-produced stop's third part is one command, typed out with the key. A not-handed-off stop's is the git commands of its form, with the branch prefix the file belongs under named, as `PRD_GROUND_PRD_NOT_HANDED_OFF` names `prd/`. Where no command applies, the stop says so and says why, as `CREATE_PRD_BRD_NOT_ELIGIBLE` does today.

## 5. The changes, by batch

Each batch is one pull request. Each ends with the claim sweep of §7 over its own subject, the gates, and an Opus review.

### 5.1 Batch 1 — `/create-ard` and `/specify` on the idea route

| Command | Builds from | Never produced | In the folder, on no ref |
|---|---|---|---|
| `/create-ard` | the PRD folder's `prd.md` (the folder above the Epic, on an Epic-level run) | `CREATE_ARD_NEEDS_PRD`, naming `/product-workflows:create-prd <PRD>` | `CREATE_ARD_PRD_NOT_HANDED_OFF` |
| `/specify` | the same | `SPECIFY_NEEDS_PRD`, naming the same | `SPECIFY_PRD_NOT_HANDED_OFF` |

- **The never-produced stop is idea-route only.** On a slice, no `prd.md` stays the ordinary state and the run goes on, reported as today. Each command's route test is the one it has: for a PRD-level run ARD:83 and SPEC:41, and for an Epic-level run the `brd-link.md` of the PRD folder above (ARD:294–296, ARD:410; SPEC:269).
- **The not-handed-off stop is on both routes.** A `prd.md` that exists on disk and on no ref is a document nobody can read later, whichever route wrote it.
- **`/specify`'s zero-Epics question loses its no-PRD form on the idea route** (SPEC:609–615), which the stop now precedes. Its slice form, resolved against the ledger, stays until batch 4 (§5.4).
- **`/create-ard`'s small-item advisory comes after the stop.** Its step 5 reads `prd.md` *ahead of its gate* and can ask *Author the ARD anyway / Stop* (ARD:239–243). The builder orders the two so no run answers that question and is then stopped on the PRD.
- **A PRD under its pre-rename file name is present, not missing.** On a tree whose PRD is still `<KEY>_<slug>.md` (ARD:274, SPEC:315 name the case), the never-produced stop would send the user to author a second PRD. There the run names `workflows-core:addressing` §5's rename instead. The test excludes `<KEY>_ARD.md`, the pre-rename ARD the same pattern matches (ARD:274), so a folder holding only that is not told to rename a PRD it does not have.
- **`/update-spec` gains a carve-out, in this batch.** Its step 6 executes `/specify`'s *Gate the PRD*, *Gate the decision register* and *Gate the Epic* sections by citation, *with their stops named `UPDATE_SPEC_` in place of `SPECIFY_`* (`plugins/product-workflows/commands/update-spec.md:57`). Rewriting `/specify`'s section would therefore make `/update-spec` stop too. The builder keeps `/update-spec` on today's behaviour (L5): on `absent` it skips the confirmation and reports, whether or not a `prd.md` is in the folder. How that is written, a sentence in `update-spec.md` naming the two stops it does not take or a section `/specify` words so the citation still reads true, is the builder's. Batch 4 does the same for the ledger tests.
- **In PH §3.4**, the `/create-ard` PRD row is rewritten, and the shared `/specify` `/update-spec` PRD row is split in two: `/specify`'s stops, `/update-spec`'s keeps its text. Both new rows say *stops*, name the ids, and say which route each form is on.

### 5.2 Batch 2 — a keyed `/implement`

| Builds from | Never produced | In the folder, on no ref |
|---|---|---|
| the unit's own `specification.md` | `IMPLEMENT_NEEDS_SPEC`, naming `/product-workflows:specify <UNIT>` | `IMPLEMENT_SPEC_NOT_HANDED_OFF` |
| the unit's own `design.md` | `IMPLEMENT_NEEDS_DESIGN`, naming `/dev-workflows:design <UNIT>` | `IMPLEMENT_DESIGN_NOT_HANDED_OFF` |

- **The unit is the folder the run resolved its `specs` from**: an Epic's, or the PRD folder's for a broad PRD-level slice. The rule is the same for both, and on a multi-component PRD too: an Epic unit needs its own two files, and a PRD built whole by the 0-Epic override needs the PRD folder's two.
- **Where both are missing, the run stops once**, on the specification, since `/design` stops without one.
- **Every keyed run is bound**: a companion run and a tasks-only run as well (IMPL:377, IMPL:381). Both read the unit's specification and design as the context of their tasks, and both are found only in Phase 1, after this stop.
- **A direct run is untouched.** It resolves no key, and its prompt is its instruction (IMPL:321).
- **The stop's message names the direct run as a way out**, beside the producing command: a change too small to specify and design is made with no key.
- **The in-scope set becomes the expected pair, not the files found.** Today a keyed run's `specs` are the `specification.md` and `design.md` *present* in the unit's folder (IMPL:279–281), and the gate runs only on those (IMPL:324), so it is never asked about a file that is missing. The run now tests both paths of the unit's folder whether or not each is on disk: the gate on each, or the folder's own file on an unmanaged tree (L7). Without this the stops below could not fire.
- **IMPL:316–321's question is removed** (L6), and IMPL:324's `absent` branch becomes the stops.
- **The stop names what the earliest gap needs** (L12). With the specification missing: on the idea route, a `prd.md` that is nowhere names `/product-workflows:create-prd <PRD>`; on either route, a `prd.md` in the PRD folder and not on the default branch names its landing; otherwise the stop names `/product-workflows:specify <UNIT>`. On a slice, batch 4 replaces that last with what the ledger tests resolve.
- **`CONFORMANCE_NOT_IMPLEMENTED` is reworded in this batch** (CONF:119), and `/conformance`'s and `/security-workflows:scan`'s next-step lines are made conditional (L8): each names `/dev-workflows:implement <KEY>` only where the unit's specification and design are on the default branch, and what the earliest gap needs otherwise.
- **An `@path` spec-folder token on a keyed run** still adds its files to `specs` as context, gated as today (IMPL:161–163). It does not stand in for the unit's own pair.
- **Phase 4.5's falling-back array goes** (IMPL:1366–1370). It is presented *because no consumer of `design.md` stops on row F*, which this batch makes false, and its case can no longer arise: a keyed run now always has `design.md` on the default branch, so the carve-out at IMPL:1370 always applies.
- **The multi-component check's `epic_spec` and `epic_design` rows** (IMPL:375; `workflows-core:components` §6) can no longer be reached at `implement` scope with a gap, since Phase 0 has stopped first. The builder removes them from that scope or shows they still serve, and leaves `/ready`'s and `/epics`' scopes alone.
- **`/implement <PRD>`'s pickers** follow L8 and L11. An Epic that lacks either file on the default branch is left out of the picker, counted, and named in the prose above it with the command it needs; the picker's ○ marker for *`specification.md` but no `design.md`* (IMPL:256) then marks no listed row, and the builder rewords the markers. The broad-slice option is offered only where the PRD folder holds both files on the default branch. Where that leaves one Epic and no slice, it is taken with a notice, as a single Epic is today (IMPL:220); where it leaves none, the run stops with the id of the earliest gap, naming one command. **A multi-component PRD's override question is not skipped**: taking its flat pair whole stays a question with *Split* recommended (IMPL:219; `.claude/rules/dev-workflows.md`, *Multi-component PRDs*), never an auto-selection.
- **A PRD with no Epic folder and no PRD-level specification** stops `IMPLEMENT_NEEDS_SPEC`, naming `/product-workflows:specify <PRD>` (or `/create-prd`, by L12). That command puts the fork between splitting into Epics and one broad specification (SPEC:603), so it is the one command that serves both ways on. Today's *Implement one broad PRD-level slice anyway* (IMPL:219, IMPL:270) is no longer offered on a folder that lacks the pair; where the PRD folder holds both files it stays, as §6 says.
- **On a multi-component PRD the named command is checked against L8.** There `/design <PRD>` and `/specify <PRD>` each open with a picker or an override question of their own, and `/implement` recommends `/epics` at no Epics today (IMPL:219). The builder reads what each does on arrival for the folder in hand and names the one that goes on.
- **A resumed run** (IMPL, *Resuming a stopped run*) passed this check when it started. The builder reads whether its Phase 0 reaches the gate again and states the answer in the command; the design asks only that a run already past its first edit is never stopped by a document removed since.
- **L9:** trace `/conformance <PRD>` where no unit holds a block. Where it runs on, it stops as the Epic run does, with an id of its own.
- **In PH §3.4**, the `/implement` row is rewritten to *stops*, with the four ids.

### 5.3 Batch 3 — `/document <KEY>`

`/document` asks (M6); it is the only command here that does.

- **The test** (L2): the `implementation.md` blocks in the run's scope, the focus Epic's own where one is set, number none, and the commit scan found no commit.
- **Where it sits** (L2a): in Mode A's Phase 0, once the address is resolved and the preflight has run, and before step 4(c)'s inline `/docs-profile` and every Phase 1 question. The record is a file in the specs tree, so reading it there costs nothing. **Only where it holds no block** does the run resolve `$REPOS_PATH` and run the scan this early; a run whose record holds a block keeps today's order in every respect.
- **Where the repositories are comes first.** Where the record holds no block and no entry of `$REPOS_PATH` is an existing directory, Phase 1's own question (DOC:350–355: *Set REPOS_PATH* / *Proceed without the repos* / *Cancel*) is put here, ahead of the scan, and not again in Phase 1. On *Set REPOS_PATH* the scan runs. On *Proceed without the repos* it does not, and M6's question still follows, saying the scan did not look: that answer says where diffs are read from, not whether anything was built. A misconfigured path is thus never reported as nothing built.
- **The question.** Two options, the first recommended: stop and implement first; or go on from the PRD alone. Neither label names a command, so the array is one text in every state. The lines above it say what was read: that the record holds no block, how many commits the scan walked in which repositories and that none named the key, or that the scan did not look and why, and whatever the report-only probe matched. A free-text answer is normalised into one of the two or asked again.
- **On *Stop***, the run ends as the command's *Ending early* says every stop does (DOC:58), its line naming `/dev-workflows:implement <KEY>` with the key the run was given, or, on a run focused on one Epic that lacks a specification or a design, what that Epic's earliest gap needs (L12). A PRD-level run names `/dev-workflows:implement <PRD>`, whose picker says what each Epic needs. Nothing in the documentation repository has been touched, since the question precedes the inline profile.
- **On *Go on***, the run continues exactly as it does today, and its report carries the answer, so pages written with no implementation behind them say so.
- **Nothing is asked twice, and a later base is scanned.** Phase 3's own scan reuses the early one's result. Where a base named at Phase 2's *Revise plan* replaces `$REPOS_PATH` or undoes *Proceed without the repos* (DOC:355), the scan runs again over it, and a commit it finds is read as any other. Four sentences say *Phase 1 took* that answer (DOC:58's list of *Cancel*s, DOC:425, DOC:548, DOC:608); on a run with no block it is now taken in Phase 0, and each is re-read from where it stands.
- **Phase 5's aggregate gate** (DOC:608) is put where every ref is unresolved. The builder checks its condition reads on a non-empty set, since a run with no ref at all has now been asked already.
- **`/document` is not a caller of the gate**, so PH §3.4 takes no row for it. The question is the command's own, stated in its Phase 0 and on its docs page; the command already loads the question rules before its first question.
- **No error id on the question.** The stop it leads to is the user's answer, reported as such.

### 5.4 Batch 4 — the BRD route

| Command | On a slice, stops unless | Ids |
|---|---|---|
| `/create-ard` | the slice's `coverage-ledger.md` is readable, no row its `brd-link.md` claims is `unallocated`, and at least one is `covered-here` | `CREATE_ARD_BRD_UNALLOCATED`, `CREATE_ARD_BRD_NOT_ELIGIBLE` |
| `/specify` | the same | `SPECIFY_BRD_UNALLOCATED`, `SPECIFY_BRD_NOT_ELIGIBLE` |

- **These are `/create-prd`'s tests, not new ones** (CPRD:268–336): the same reads, the same order, the same remedy per branch, `/product-workflows:brd-split` in the form that table names, or no command where none applies. An Epic-level run tests the slice above it.
- **The test is stated once.** `product-workflows:coverage-ledger-format` §5 (*PRD eligibility*) owns the eligibility rule, and its §5.2 the remedy table the three commands' next-step offers resolve against. The builder shows the test `/create-prd` applies is stated there whole, or puts it there, and has the three commands cite it; three copies of the test is the outcome to avoid. Whether §5's name and wording, which speak of a PRD, need widening to the ARD and the specification is the builder's to read.
- **The offers that would now stop are made conditional on the same test** (L8): `/brd-interview`'s offers of `/create-ard <BRD-KEY>` and `/specify <BRD-KEY>` *on the level test alone* (`plugins/product-workflows/commands/brd-interview.md:2528`, and the array at `:2563`), and `/brd-reconcile`'s *always offered* list (its Phase 14, around `:3011–3027`).
- **What the stop makes unreachable is removed**, not left: in `/create-ard`'s Phase 7, the precondition rows for a failing ledger (ARD:834–837), the arrays written for those states (ARD:860–863) and the text on them (ARD:875–880); in `/specify`, the zero-Epics question's slice forms (SPEC:616–627) and the matching rows of its `### Next step`. The builder confirms each is unreachable before removing it.
- **Two statements are overturned and rewritten**: *This run reads no `claims:` list and no coverage ledger as an authoring input … Not checking it here is a decision, not an omission* (ARD:466–480, SPEC:702–717).
- **`/implement`'s stop on a slice names what the ledger tests resolve** (L12), from this batch on: `/product-workflows:specify <SLICE>` where both clear, the `/product-workflows:brd-split` form where one fails, read through `workflows-core:next-phase-offer`'s *`/epics` precondition* as IMPL:219 reads them. `dev-workflows` loads no `product-workflows` reference for it.
- **The BRD-route `*_NOT_HANDED_OFF` stops gain the committed form** (§4).
- **Nothing else on the route is required.** A slice that passes goes on with no `prd.md`, no seed and no register, each absence reported as today.
- **`.claude/rules/brd-route.md`'s kind-gate rule binds**: the test reads `brd-link.md` and the ledger, never the folder's asserted kind.

## 6. What stays as it is

No change, and a sentence that says a run goes on here stays true:

- `/create-prd` with no idea. `/idea` is not a prerequisite (CPRD:127).
- Every command with no ARD, on a single-component PRD (`workflows-core:ard-resolution`'s no-regression rule), and the multi-component exception that rule already states.
- `/specify`, `/design` and `/implement` on a PRD with no Epics, where the folder holds what the command builds from.
- `/epics` with no PRD-level specification, and `/epics` reading `prd.md` from the working tree with no gate (L13).
- `/create-ard` and `/specify` on an `EPIC-` folder with no `epic.md` (L4).
- `/update-spec`'s PRD row (L5), `/release-notes` (L3), `/ready`, which reports and never stops, and every command the trace found stopping already.
- The slice's `decisions.md`: absent, the run goes on; in the folder and on no ref, it stops, as today (PH:331).
- A direct `/implement` and a direct `/document`.

## 7. The statements this changes

The fall-backs are written rules, repeated in many places. This is a change to a claim's extent, so `.claude/rules/claim-sweep.md` refinement 8 binds: enumerate every statement of the claim before the edit, re-read each after it, and count the literal strings. The population the lead found, which the builder re-derives and does not take as complete:

- **`CLAUDE.md` § Hard constraints**, the last bullet: *an absent optional input still delegates to the command's pre-existing behaviour and never becomes a prerequisite*. It stays true of an optional input. The bullet gains the other half: the document a command builds from is not optional, and PH §3.4 names each. `CLAUDE.md` is near its 36,000-character warning; the builder measures it.
- **PH §3.4**: its heading, the sentence *An input that was optional before this gate existed stays optional, and that must not change* (PH:314), the paragraph on consumers that map `absent` to a stop (PH:316), the rows this design's §5 changes, and the closing paragraph that lists which consumers stop (PH:355). Three inputs that were optional are now required, by decisions M1 and M3. The text says so as a declared behaviour change, the way PH:355 declares rows D and E, and does not present them as inputs that were never optional. Three pointers break when the rows change and are re-read from where they land: the `/update-spec` half's *the same shape as `/create-ard`'s row* (PH:322), the Epic row's *the shape of their PRD rows* (PH:323), and PH:351's *on every route* for rows whose never-produced form is now idea-route only.
- **PH §5 rule 3**: *No consumer turns an optional input into a prerequisite.* What remains true: the gate never stops on `absent`, each caller's row says what `absent` means, and a row moves from falling back to stopping only by a recorded decision.
- **PH §4.0, §4.1 and §4.3**: an artifact's class turns on whether every §3.4 row naming it falls back. Only `design.md` changes class: `prd.md` is *gated — stopping* already (PH:535), and `specification.md` through `/design`'s row. The builder re-derives `design.md`'s class, clause and array, and checks the other two against the rewritten rows.
- **This is a narrowing of a rule in an instruction file**, so `workflows-core:instruction-file-maintenance` binds: the narrowing is itemised separately, line by line, against what the file still says.
- **`plugins/product-workflows/commands/update-spec.md`**, step 6 (line 57), which cites the `/specify` sections batch 1 rewrites, and its docs page.
- **The commands' own defences of the fall-back**: ARD:263, ARD:285, ARD:429–436, ARD:803; SPEC:325, SPEC:542–545, SPEC:664, SPEC:1350; IMPL:236, IMPL:316–324; IMPL:1366–1370; ARD:466–480 and SPEC:702–717 (batch 4); `plugins/product-workflows/commands/brd-reconcile.md:3018`.
- **Offers that name a changed command** (L8): `workflows-core:next-phase-offer` (line 338 and every offer that names `/create-ard`, `/specify`, `/implement` or `/document`); `plugins/product-workflows/commands/epics.md:1124` (L13); `brd-interview.md:2528` and `:2563`, and `brd-reconcile.md`'s Phase 14 (batch 4); CONF:119. CONF:560, CONF:572 and `plugins/security-workflows/commands/scan.md:550` (batch 2). Checked and kept as it is, a record's follow-up line: CONF:317.
- **The existing `*_NOT_HANDED_OFF` stops** (§4): `prd-ground.md` and `prd-proposal.md` in batch 1, and `brd-package.md`, `brd-proposal.md`, `brd-reconcile.md`, `prd-ground.md`'s slice stops, and the register stops of `create-ard.md`, `create-prd.md` and `specify.md` in batch 4, each with its docs page.
- **`/document`'s pointers to the moved question**: DOC:58, DOC:425, DOC:548, DOC:608 (batch 3).
- **The rules files**: `.claude/rules/workflows-core-handoff.md` (the count of consumers with a stopping row, re-derived with the recipe written beside it), `brd-route.md`, `product-workflows.md`, `dev-workflows.md`, `dev-workflows-implement.md`, `docs-workflows.md` (the map lines), `dev-workflows-conformance.md` where L9 adds a stop, `security-workflows.md` where it describes what `/implement` does with a finding, and `docs/maintainers/rationale.md`.
- **The docs pages**: each changed command's page under `plugins/*/docs/commands/`, the error-id lists, `workflow.md`, `getting-started.md` and the family map, wherever one says a step can be skipped. Found by subject, each a statement of the old rule: `plugins/dev-workflows/docs/roles-and-phases.md:10` (*`/design`'s `specification.md` is this plugin's one exception*), `plugins/product-workflows/docs/roles-and-phases.md:10`, `plugins/workflows-core/docs/reference/references.md:26`, and for batch 4 `plugins/product-workflows/docs/brd-workflow.md` (`:298–299`, *carry none of their own, since neither reads the ledger as an authoring input*, and `:327–328`).
- **`docs/superpowers/to-fix.md`**: the LADDER-ORDER entry, closed by the last batch, and `docs/superpowers/to-test-on-real-project.md`, which gains one live check per new stop.

`plugins/workflows-core/reference-parts/` is generated, from PH and from `next-phase-offer` among others; the builder regenerates it with `scripts/reference-parts.py` after editing either and never edits it.

## 8. Goals, non-goals, anti-goals

**Goals**

1. `/create-ard`, `/specify` and a keyed `/implement` each stop, before any write or dispatch, where the document they build from is not on the default branch (within §4's two limits), and name the command to run. `/document <KEY>` asks before it writes pages with no implementation behind them.
2. `/create-ard` and `/specify` stop on a slice that fails `/create-prd`'s ledger tests.
3. Every sentence in the plugins, the rules files and the docs that said one of these runs goes on is rewritten against what the stop enforces.

**Non-goals**

- Making `/idea`, the ARD, Epics or an interview mandatory.
- A status field, a ladder table or any stored phase. The artifacts stay the only record of where a key stands.
- Moving the check into `specs-git.py`. GIT-G1 Part 3's batch 2 does that for the gate and leaves what a caller does on `absent` in the caller's own text (`docs/superpowers/specs/2026-11-13-git-g1-part3-design.md:131`), which is where these stops are written.
- `/release-notes`' `stage: dev` line on a note drafted with nothing implemented. Found by the trace, and `/ready`'s business.
- TAIL-G1, D15, and every other entry of `to-fix.md`.

**Anti-goals**: it has failed, even if it works, where

- a run stops on a step §6 keeps optional;
- a stop names a command that itself stops on arrival for that folder;
- a question is added where M2 chose a stop, or a stop is softened into a question, M6's one question aside;
- `/ready` stops;
- a run that was already past its first edit is stopped by this rule;
- a kind is read off the folder's asserted `kind:` instead of off the file the test cares about.

## 9. Approaches

- **A. Per-command stops on the check each command already runs.** Each caller's `absent` branch becomes a stop with its own ids, split the way `/prd-ground` already splits it, and PH §3.4's rows flip. No new machinery, and the docs gate (`scripts/check-docs.sh` check 11) already reads that table. Cost: each command carries its own wording, and nothing forces a future command to take a row. **Chosen (M5).**
- **B. One ladder table and one shared check.** A new `workflows-core` reference lists each command's required inputs and their producers, and every keyed command runs one entry point. Uniform messages and one place to see the ladder. Refused: it is one more reference on every run of about ten commands, and the nine commands that already stop have route-specific splits a table does not hold, so it is either a second authority beside PH §3.4 or a large migration.
- **C. Wait for GIT-G1 Part 3's batch 2 and put the table in `specs-git.py`.** The most reliable form. Refused: that batch waits on rehearsal findings, and `/document`'s test and the ledger tests are not part of the gate at all.

**A correction, made after the maintainer chose A and put to them before approval.** The lead first said Part 3 would carry these rows into the script as they stand. Part 3's design says the opposite: what a caller does on `absent` is not scripted (its line 131). So C was never on Part 3's road, and A's stops sit in the text Part 3 leaves with each command. Batch 2 of Part 3 rewrites the lines around them (M7), not the stops.

## 10. Constraints

- `CLAUDE.md` and `.claude/rules/` bind every edit; *Prose is executed*, so each stop is written where the run meets it, in the order it runs.
- Every changed plugin takes a version, a dated `CHANGELOG.md` section and a coupling bullet (`.claude/rules/plugin-updates-coupling.md`): a command that names a new PH §3.4 row needs the `workflows-core` that holds it.
- A removed `choices:` array leaves no reference to it behind (`.claude/rules/plugin-authoring.md`, *Surgical Changes*), and `scripts/reference-parts.py check-questions` still passes.
- The full gate chain of `.github/workflows/validate-catalog.yml` passes on each batch's branch.
- Each batch gets an Opus review before its pull request.

## 11. Done when

1. Each stop of §5 is in its command and its docs page, and each stop that maps the gate's return is in PH §3.4 too, with the id spelled the same wherever it appears. Batch 4's ledger stops map no gate return and take no row there.
2. The claim sweep's before and after counts are recorded per batch, and no sentence in §7's population still says a stopped run goes on.
3. The gates pass, and each batch's review is answered.
4. `to-test-on-real-project.md` lists a live check for every new stop, and the maintainer has chosen when they run.
5. The LADDER-ORDER entry leaves `to-fix.md` with the last batch.

## 12. Left to the builder

- The wording of each stop, within PH §4.4's contract as §4 applies it, and where exactly in each Phase 0 it sits; the wording of `/document`'s question and its two options, within §5.3.
- Whether PH §3.4 states the two-form split once, as a named paragraph the new rows cite, or in each row. The existing rows that split row F each state it themselves.
- The exact rewording of the `CLAUDE.md` bullet and of PH §5 rule 3.
- Batch 4's home for the shared ledger test (§5.4).
- Each batch's version numbers, re-derived at release.

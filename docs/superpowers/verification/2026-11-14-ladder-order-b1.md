# LADDER-ORDER batch 1 — `/create-ard` and `/specify` stop on a missing PRD — verification record

**Plan:** `docs/superpowers/plans/2026-11-14-ladder-order-b1-prd-stops.md`. **Design:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`, §5.1 and §11 (*Done when*). **Population:** `docs/superpowers/plans/2026-11-14-ladder-order-b1-sweep-population.md`. **Release:** `product-workflows` 3.82.0, `workflows-core` 1.91.0, `dev-workflows` 4.66.3 and `docs-workflows` 1.39.5, each changelog section dated 2026-11-14. **Branch:** `feat/ladder-order-b1`, cut from `origin/main` at `0de91630` (PR #196, a status-line change that landed after the design merged as `92fc7a75`), with `main` merged twice: `c12ca55f` (PRs #198 and #197) at `7d8e214f`, and `9b1d6aef` (PR #199) at `95e30032`. Measured at `db46afff`, the head, after the final review's fix wave (`fc0721a9`, `9a76bad2`) and its four closing wording fixes (`db46afff`), before the push. Written last. Every figure below is re-derived here with its command beside it; where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-14-ladder-order-b1-rulings.md` beside this file, and the controller's ledger, verbatim, is `2026-11-14-ladder-order-b1-ledger.md`; ledger line numbers below are the ledger's own (line *n* of the ledger is line *n* + 5 of that file).

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/ladder-order-b1`, on the tree `db46afff` commits, with only this record and the two files beside it added. `git fetch origin` then `git log --oneline HEAD..origin/main` printed nothing: `origin/main` is `9b1d6aef`, which `git merge-base HEAD origin/main` also prints. `$S` below is a scratch directory outside the repository.

**The branch.** `git log --oneline --first-parent origin/main..db46afff | wc -l` gives 27: Task 1's `5562e4cf` and `41d62ebb`; Task 2's `d875ef40`, `14cb4f5f` and `eb765b4a`; Task 3's `2dbe6314`, `769fbac7` and `6b0d1a11`; Task 4's `449ad3d6`, `5cb20caa`, `548b8854`, `6887b35d` and `77aa580f`; Task 5's `7f5e1c66` and `b5115405`; Task 6's `126b4752` and `ba3d9238`; Task 6M's merge `7d8e214f` and `b01883a6`; the controller's merge `95e30032`; Task 7's `b7b14718`, `62abd88c` and `97fb8c8c`; Task 8's after-counts `a39f75f6`; and the fix wave's `fc0721a9`, `9a76bad2` and `db46afff`. `git diff --name-only origin/main db46afff | wc -l` gives 61 files, and the same list grouped by its first path parts gives 29 under `plugins/product-workflows` (12 commands, 15 docs pages, the changelog and `plugin.json`), 11 under `plugins/workflows-core` (four references — `phase-handoff.md`, `next-phase-offer.md`, `addressing.md`, `document-lineage.md` — four regenerated files under `reference-parts/`, one docs page, the changelog and `plugin.json`), 7 under `plugins/dev-workflows` (five docs pages, the changelog and `plugin.json`), 3 under `plugins/docs-workflows` (one docs page, the changelog and `plugin.json`), 4 under `docs/superpowers` (the plan, the population file, the design's batch-1 notes and its §5.5, the live checks), `docs/maintainers/rationale.md`, `CLAUDE.md`, four `.claude/rules/` files (`brd-route.md`, `plugin-updates-coupling.md`, `product-workflows.md`, `workflows-core-handoff.md`) and `.claude-plugin/marketplace.json`. `git diff --name-only origin/main db46afff | grep -vE '\.md$'` lists only the marketplace and the four `plugin.json` files: no script, workflow, agent or hook changes.

Below, PH is `plugins/workflows-core/references/phase-handoff.md`, ARD `plugins/product-workflows/commands/create-ard.md`, SPEC `plugins/product-workflows/commands/specify.md`, UPS `plugins/product-workflows/commands/update-spec.md`, and every line number is at `db46afff`.

## What the batch delivered against the design's §5.1

| §5.1 | Where on the tree |
|---|---|
| `/create-ard`: `CREATE_ARD_NEEDS_PRD`, naming `/product-workflows:create-prd <PRD>`, and `CREATE_ARD_PRD_NOT_HANDED_OFF` | ARD:279 and its plain form at ARD:287 (*Run '/product-workflows:create-prd <PRD>' and merge its handoff*), its rename form at ARD:290–301; ARD:278 and the uncommitted form at ARD:304–311, the committed form at ARD:314–318 |
| `/specify`: `SPECIFY_NEEDS_PRD` and `SPECIFY_PRD_NOT_HANDED_OFF` | SPEC:320, :328, :331–342; SPEC:319, :345–352, :355–359 |
| The never-produced stop is idea-route only; on a slice no `prd.md` goes on, reported | ARD:279–280 and SPEC:320–321; the route is read off the PRD folder, the folder above the Epic on an Epic-level run (ARD:277, SPEC:318) |
| The not-handed-off stop is on both routes | ARD:278, SPEC:319: *`absent`, and a `prd.md` in the PRD folder — on either route* |
| `/specify`'s zero-Epics question loses its no-PRD form on the idea route; its slice form stays | SPEC:671–675: *A folder holding none is a slice, since Phase 0's Gate the PRD stops an idea-route run without one*, the slice form following whole |
| `/create-ard`'s small-item advisory comes after the stop | ARD:234–236 (*taken after Gate the PRD, Gate the decision register and Gate the Epic … none of the three reads its answer*), and ARD:428, *Now take Phase 0 step 5's optionality advisory.*, after the Epic gate |
| A PRD under its pre-rename file name is present, not missing, and `<KEY>_ARD.md` is excluded | ARD:279 and SPEC:320, the test word for word as `plugins/product-workflows/commands/prd-proposal.md:202–203` (*a top-level `.md` file whose name is the resolved key followed by `_`, other than `<KEY>_ARD.md`*), *a folder holding only `<KEY>_ARD.md` among them* taking the plain form |
| `/update-spec` gains a carve-out in this batch | UPS:57 (step 6 saves both stops and prints *No authored PRD on `<default>` for `<PRD>` — revising against the resolved folder at `<path>`.*); and what the design's §5.1 note says followed from it: UPS:81 (Phase 2's *Upstream* skips an input `<default-ref>` lacks), UPS:59 (step 7's capture leaves it out), UPS:164–166 (Phase 8 names no run that would stop on that PRD folder) |
| PH §3.4: `/create-ard`'s PRD row rewritten, the `/specify` `/update-spec` row split | PH:321 (`/create-ard`) and PH:322 (`/specify`) open with **stops**, name the two ids each, and declare the change: *a behaviour change, 2026-11-14 — before it this row fell back on every `absent`; the idea-route PRD was an optional input and is now required*. PH:323 is `/update-spec`'s row, still falling back: *`/specify`'s two stops on this input are not taken* |

The design's §4 also gives this batch the committed form of row F, for the new stops and for the two existing idea-route ones: PH:613 (§4.4 row F, *Where HEAD holds it … those commands do not apply*), `prd-ground.md:576` and `:580`, and `prd-proposal.md:276` and `:284`.

## The design's §11, *Done when*

| # | Item | State on this tree |
|---|---|---|
| 1 | Each stop of §5 in its command and its docs page, and in PH §3.4 where it maps the gate's return, spelled the same everywhere | **Done for batch 1's four ids.** The commands: *The numbers*, below. The docs pages: `plugins/product-workflows/docs/commands/create-ard.md:54–55` and `docs/commands/specify.md:69–70`, one bullet per id. PH §3.4: `awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md \| grep -o <id> \| wc -l` gives 3 for each `*_NEEDS_PRD` id and 2 for each `*_PRD_NOT_HANDED_OFF` id, in rows PH:321 and PH:322. No misspelt variant exists: `grep -rhoE '\b(CREATE_ARD\|SPECIFY\|UPDATE_SPEC)_(NEEDS_PRD\|PRD_NOT_HANDED_OFF)[A-Z_]*' plugins CLAUDE.md .claude docs/maintainers \| sort \| uniq -c` prints the four ids alone (27, 26, 28 and 24 occurrences, changelogs and generated files included). Batches 2 to 4's stops are theirs |
| 2 | The claim sweep's before and after counts recorded per batch; no sentence in §7's population still says a stopped run goes on | **Done for batch 1** (*The claim sweep*, below) |
| 3 | The gates pass, and each batch's review is answered | **Done for batch 1** (*The gates*, *The reviews*) |
| 4 | `to-test-on-real-project.md` lists a live check for every new stop, and the maintainer has chosen when they run | **Half done.** `docs/superpowers/to-test-on-real-project.md:128` opens the section *LADDER-ORDER batch 1*, and lines 132–147 hold 16 checks (`awk '/^## LADDER-ORDER batch 1/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md \| grep -c '^- \*\*'` gives 16), covering every stopping row of the plan's *Global Constraints*, Review Focus 1, 2 and 4, and the final review's recommended re-run on a slice (line 140). **None has been run on a real project, and the maintainer has not chosen when they run**: the ledger's last line records no message from the maintainer after 15:32 but a status question |
| 5 | The LADDER-ORDER entry leaves `to-fix.md` with the last batch | **Not this batch's.** The entry stands at `docs/superpowers/to-fix.md:135`, unchanged by this branch (`git diff --stat origin/main db46afff -- docs/superpowers/to-fix.md` prints nothing); it still reads *Owner: the maintainer's to schedule, as a design of its own*, though the design has since merged |

## The states and the ids

Each row of the plan's *Global Constraints* table, re-read here on the head text of both commands, with the line that decides it. The gate's call, the `stopped`-first mapping and the `pass` branch are ARD:277 and SPEC:318; the split on `absent` and `unmanaged` is the six bullets ARD:278–283 and SPEC:319–324, which test whether a `prd.md` is in the PRD folder and read the route off that folder.

| The gate returns | And | Idea route | BRD route | `/create-ard` | `/specify` |
|---|---|---|---|---|---|
| `pass`, `pass_amending` | — | go on | go on | ARD:277, *read the authored PRD in Phase 2* | SPEC:318, *proceed — Phase 2 still reads the resolved folder* |
| any stopping row | — | stop per §4.4 | the same | ARD:277, *Any stopping state → stop per §4.4*, before the split | SPEC:318, the same |
| `absent` | `prd.md` in the folder, HEAD does not hold it | `*_PRD_NOT_HANDED_OFF`, uncommitted | the same | ARD:278 (the HEAD test; *an untracked file, or one staged and never committed*) → ARD:304–311; on a slice ARD:322 adds the register sentence where `decisions.md` is unlanded | SPEC:319 → SPEC:345–352; SPEC:363 |
| `absent` | `prd.md` in the folder, HEAD holds it | `*_PRD_NOT_HANDED_OFF`, committed | the same | ARD:278 → ARD:314–318, its commands and three changing sentences at ARD:326 | SPEC:319 → SPEC:355–359, SPEC:367 |
| `absent` | no `prd.md`, a pre-rename PRD file | `*_NEEDS_PRD`, rename form | go on, reported | ARD:279 → ARD:290–301; on a slice ARD:280, which makes no pre-rename test | SPEC:320 → SPEC:331–342; SPEC:321 |
| `absent` | no `prd.md`, no pre-rename file | `*_NEEDS_PRD` | go on, reported | ARD:279 → ARD:287; ARD:280 prints *No authored PRD on `<default>` … architecting from the resolved folder* | SPEC:320 → SPEC:328; SPEC:321, *specifying from* |
| `unmanaged` | `prd.md` in the folder | go on | go on | ARD:281, *on either route* | SPEC:322 |
| `unmanaged` | no `prd.md` | `*_NEEDS_PRD`, rename form where it applies | go on | ARD:282, worded for an unmanaged tree at ARD:324 (no ref, handoff or merge named); ARD:283 | SPEC:323, SPEC:365; SPEC:324 |

Every row holds. The table's other constraints, on the same text:

- **The ids** are spelled as the plan gives them (§11 item 1, above).
- **The HEAD test** is `git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>" 2>/dev/null` at ARD:278 and SPEC:319, `<path>` pinned to the gate's own `path` input written `./<path>`; PH:613 states the same test for row F.
- **The pre-rename test** is `/prd-proposal`'s, word for word (§5.1 table, above).
- **The route test** reads the PRD folder's `brd-link.md` (ARD:277, SPEC:318); the commands' own route tests stand at ARD:83 and SPEC:41–44.
- **Four parts, in order:** ARD:285 and SPEC:326 state it of all four forms, and each form reads what was found, what the run did not do, the commands, and *Ignored, …*. The commands stand on lines of their own with no `#` comment (ARD:320, SPEC:361).
- **A not-handed-off stop never names `/create-prd` as the fix:** ARD:304 and :314, SPEC:345 and :355 name it only as what not to re-run.
- **No stop `emit-block`s:** ARD:328 and SPEC:369, *Neither stop is a plugin gap, so neither `emit-block`s.*

*What must not change*, on the same text: `/update-spec` reports and goes on (UPS:57); a slice with no `prd.md` goes on (ARD:280, :283; SPEC:321, :324); PH's Epic row (PH:324) still reads the folder as it stands on `absent`; rows D, E, the C rows, B′, G and I are reached before the split (*Any stopping state → stop per §4.4*); `/epics` reads `prd.md` with no gate and notes whether it is landed for its offers only (`.claude/rules/product-workflows.md:38`, *offers only, never a gate*); and the generated files are fresh (`check-parts`, below). The plan's Task 4 grep expected `2` from `grep -c "SPECIFY_NEEDS_PRD\|SPECIFY_PRD_NOT_HANDED_OFF"` on UPS; it prints 1, since both ids sit on UPS:57 and `grep -c` counts lines, and `grep -oE … | sort | uniq -c` gives each id once (Task 4's report says the same). `grep -rc "UPDATE_SPEC_NEEDS_PRD\|UPDATE_SPEC_PRD_NOT_HANDED_OFF" plugins`, summed with `awk`, gives 0.

## The five Review Focus states

| # | State | What the text does | Pinned where |
|---|---|---|---|
| 1 | An unmanaged specs tree with a `prd.md` in the folder | goes on: ARD:281, SPEC:322 | walks T3-W12, T4-W12; Task 5's T5-W7 and T5-W17 for `/prd-ground` and `/epics`; live check `to-test-on-real-project.md:143` |
| 2 | A slice with no `prd.md`, and an Epic under a slice | goes on, reported: ARD:280 and :283, SPEC:321 and :324, the route read off the folder above the Epic (ARD:277, SPEC:318) | walks T3-W11, T3-W14, T3-W18, T4-W11, T4-W14, T4-W18; live check :144 |
| 3 | A `prd.md` committed on the user's own branch, or on a local default branch not pushed | the committed form, PH §4.4 row F's commands for a file HEAD holds, never `switch -c … add … commit`: ARD:314–318 and :326, SPEC:355–359 and :367, PH:613, `prd-ground.md:576–580`, `prd-proposal.md:276–284`; with nothing to push, no command (ARD:326's last sentence) | walks T3-W5, T3-W6, T3-W36, T4-W5, T4-W6, T4-W37, T4-W48, T5-W3 to T5-W5, T5-W10 to T5-W13, T5-W30; live checks :137, :138, :146 |
| 4 | `/update-spec` on a specification with no merged PRD above it | goes on, reported, on either route, in the folder or not: UPS:57; a stopping row still stops it | walks T4-W27 to T4-W31, T4-W35 to T4-W41, T4-W49; live check :145 |
| 5 | A folder holding only `<KEY>_ARD.md` | the plain never-produced form: ARD:279, SPEC:320, *a folder holding only `<KEY>_ARD.md` among them* | walks T3-W9, T4-W9; live check :134 |

The walks are the population file's tables (*Task 3 — the walk* to *Task 5 — the walk*), each row marked **Matches** by the task that wrote it and re-walked at Task 6M and at the fix wave; their line numbers are older than this tree's, and the rows above were re-read here at the head lines given.

## The gates

**The controller's run** (ledger line 134): every `run:` step of `.github/workflows/validate-catalog.yml`, 35 of them in order (`grep -cE '^\s*run:' .github/workflows/validate-catalog.yml` gives 35; this branch does not touch `.github/`), at `db46afff`, printing `CHAIN_EXIT=0 steps=35`, and `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` with rc 0. Its log was in the session's scratchpad and was not kept, so this record has the ledger's line and not the output. The same chain passed at `97fb8c8c` (line 114) and at `9a76bad2` (line 132), and Task 6M's report gives it passing on the merged tree, after its own fixes (its Step 8).

**Re-run here**, each command on its own, its last line or two and its exit value:

```
$ python3 scripts/validate-catalog.py
0 error(s), 0 warning(s) across 1 repo(s).
rc=0
$ ./scripts/check-docs.sh --root .
  check 9 cost-emitting-commands assertion not applicable: plugins/prose-style ships no docs/reference/session-cost.md
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
rc=0
$ ./scripts/check-id-grammar.sh --root .
PASS: no dash-form requirement IDs under .
rc=0
$ ./scripts/check-id-grammar.sh --baseline
PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt
rc=0
$ python3 scripts/reference-parts.py check-parts
FLAG plugins/workflows-core/references/phase-handoff.md:655: below
reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh
rc=0
$ python3 scripts/reference-parts.py check-citations
entry-point file phase-handoff handoff-to-main: 25 request section(s), 128 citation(s) checked
reference-parts check-citations: PASS -- 4 split reference(s)
rc=0
$ python3 scripts/reference-parts.py check-questions
question rules: 37 command(s) present a choice list, 37 load the rules first
reference-parts check-questions: PASS -- 37 command(s) load the question rules before their first question
rc=0
$ python3 scripts/reference-parts.py check-branch-check
branch-check: 24 command(s) resolve a folder, 24 run branch-check, 19 producer(s) pass a prefix
reference-parts check-branch-check: PASS -- 24 command(s) run branch-check
rc=0
$ node scripts/mermaid/check-mermaid.mjs --root .
PASS: all 50 mermaid blocks in 1223 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)
rc=0
$ ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style
rc=0
```

The mermaid count of 1223 files is before this record and the two files beside it were added; with the three staged, the pre-commit chain's run printed `PASS: all 50 mermaid blocks in 1226 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`. **`check-parts`' FLAG lines** are positional pointers it prints and does not fail on, leaving to a reading whether each crosses a part boundary: `python3 scripts/reference-parts.py check-parts | grep -c '^FLAG'` gives 115 here and 110 on `git archive origin/main` unpacked into `$S` (64 against 59 in `phase-handoff.md`). The flagged lines this branch changed are PH:314, :321, :322, :323, :356 and :537. Read here: PH:321, :322 and :323's *above* are spatial (*the folder above the Epic*, *no merged PRD above it*); PH:314's *its row below* and PH:356's three pointers point within §3.4, which the `require-on-main` part holds whole (`reference-parts/phase-handoff/require-on-main.md:148`); PH:537's *either membership list above* points within §4.1's own list. None crosses a part boundary.

## The numbers

**Consumers whose §3.4 row stops on `absent`**, by the recipe written in `.claude/rules/workflows-core-handoff.md:24`:

```bash
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
# 11
```

Without the `wc -l`: `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/prd-ground` `/prd-proposal` `/specify` `/update-spec`. It was 9 at `0de91630` (the population file's R1), and the rules file says *eleven*.

**`require-on-main` callers.** The rules file names *sixteen consumers* in the same line and writes no command for that count. Counted here by the execution phrase, not the bare name: `grep -l 'args: "phase-handoff require-on-main"' plugins/*/commands/*.md | wc -l` gives 16 — `implement`, `design`, `ready`, `conformance`, `brd-proposal`, `brd-interview`, `brd-split`, `specify`, `prd-proposal`, `update-spec`, `prd-ground`, `create-prd`, `brd-reconcile`, `brd-package`, `epics`, `create-ard` — the sixteen the rules file lists; this branch adds none.

**The four ids in the two commands.** `grep -c <id> <file>` (lines) and `grep -o <id> <file> | wc -l` (occurrences) agree for each:

| Id | `create-ard.md` | `specify.md` |
|---|---|---|
| `CREATE_ARD_NEEDS_PRD` | 12 | 0 |
| `CREATE_ARD_PRD_NOT_HANDED_OFF` | 9 | 0 |
| `SPECIFY_NEEDS_PRD` | 0 | 11 |
| `SPECIFY_PRD_NOT_HANDED_OFF` | 0 | 8 |

The plan's Tasks 3 and 4 asked for at least 3 of each `*_NEEDS_PRD` id in its own command.

**Budgets** (`LC_ALL=C.UTF-8 wc -m`; `scripts/validate-catalog.py` sets `CLAUDE_MD_WARN = 36_000` and `RULES_FILE_WARN = 20_000`, both counted in characters):

| File | `db46afff` | `origin/main` (`git show origin/main:<file> \| LC_ALL=C.UTF-8 wc -m`) | Under the warning by |
|---|---|---|---|
| `CLAUDE.md` | 35,972 | 35,858 | 28 |
| `.claude/rules/plugin-updates-coupling.md` | 19,749 | 17,925 | 251 |
| `.claude/rules/product-workflows.md` (changed) | 17,026 | 16,201 | 2,974 |
| `.claude/rules/brd-route.md` (changed) | 18,391 | 18,243 | 1,609 |
| `.claude/rules/workflows-core-handoff.md` (changed) | 5,802 | 5,231 | 14,198 |

The other rules files within 1,500 characters of 20,000 (`LC_ALL=C.UTF-8 wc -m .claude/rules/*.md | sort -n | awk '$1>=18500'`), none changed by this branch: `workflows-core.md` 18,891, `gates-reference-parts.md` 18,918, `plugin-updates-coupling-history.md` 19,359, `security-workflows.md` 19,435, `plugin-updates-coupling-history-2.md` 19,965, `dev-workflows.md` 19,973, `docs-workflows.md` 19,986, `dev-workflows-implement.md` 19,991, `workflows-core-git.md` 19,993 and `gates.md` 19,997. `CLAUDE.md` gains 114 characters on this branch, one clause of § Hard constraints' last bullet, and is now 28 under its warning, which is all the room the next batch to edit it has.

The ledger's own budget figures, measured here at each commit with `git show <sha>:<file> | wc -c` and `| LC_ALL=C.UTF-8 wc -m`: `CLAUDE.md` is 35,462 bytes and 35,215 characters at `0de91630` (the plan's *35,462 characters* is the byte count); 35,664 bytes at `126b4752` (ledger line 90, which says bytes); 36,109 bytes and 35,858 characters on `main` at `c12ca55f` (ruling 27's *36,109 characters* is the byte count, as its correction at line 100 says); 36,120 characters at the merge commit `7d8e214f`, over the warning, until `b01883a6` made it 35,947 (line 100); 35,972 characters from `b7b14718` on (line 107). The coupling file is 18,781 bytes at `0de91630` (the plan's figure, also bytes), 18,013 bytes at `95e30032` (line 106), 19,359 characters at `b7b14718`, 19,397 at `62abd88c` and 19,749 from `97fb8c8c` on (lines 107, 109, 126). Every budget figure in the ledger matches one of the two counts in the unit it names, save line 97's, which names characters for a byte count, as line 100 records.

**The four releases.** Each version read from its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), from its `.claude-plugin/marketplace.json` entry, and from the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`), against `origin/main`'s `plugin.json`:

| Plugin | `plugin.json` | marketplace | Changelog heading | `origin/main` |
|---|---|---|---|---|
| `product-workflows` | 3.82.0 | 3.82.0 | `8:## [3.82.0] — 2026-11-14` | 3.81.2 |
| `workflows-core` | 1.91.0 | 1.91.0 | `8:## [1.91.0] — 2026-11-14` | 1.90.2 |
| `dev-workflows` | 4.66.3 | 4.66.3 | `8:## [4.66.3] — 2026-11-14` | 4.66.2 |
| `docs-workflows` | 1.39.5 | 1.39.5 | `8:## [1.39.5] — 2026-11-14` | 1.39.4 |

`product-workflows` and `workflows-core` take a minor, a behaviour change; `dev-workflows` and `docs-workflows` a patch, pages only. The coupling bullet is `.claude/rules/plugin-updates-coupling.md:26`, *Update `workflows-core` 1.91.0 with `product-workflows` 3.82.0*, and it ends by saying `dev-workflows` 4.66.3 and `docs-workflows` 1.39.5 change only pages and need none of these releases, nor they them.

**The population file's totals**, by the command in its header (`python3 -I - docs/superpowers/plans/2026-11-14-ladder-order-b1-sweep-population.md <<'EOF' …`, run verbatim):

```
rows 256 malformed []
rewrite 119 {'Task 2': 14, 'Task 3': 15, 'Task 4': 21, 'Task 5': 32, 'Task 6': 19, 'Task 7': 1, 'Task 9': 17} beyond plan 61
keep 84
later {'later 2': 30, 'later 3': 7, 'later 4': 16}
duplicate ids []
```

This is the header's last total, *after its re-review, 256 (119, 84, 53)*. *Task 9* is the population file's name for the final review's fix wave; the plan has no Task 9.

## The claim sweep

The subject, the scope and the searches are the population file's header and its §1. Its rows: 256, of which 119 were rewritten in this batch (the table above, 61 of them beyond the plan's file lists), 84 kept as still true, each with why, and 53 left to later batches (30 to batch 2, 7 to batch 3, 16 to batch 4). The before-counts were taken at `0de91630` before any edit; the after-counts at `97fb8c8c` by Task 8 (`a39f75f6`), with the before-counts re-derived on `git archive 0de91630` at the same time; and the fix wave counted each string it touched immediately before and after its edits (the population file's *Task 9* table).

| Count | Before (`0de91630`) | After | Re-run here at `db46afff` |
|---|---|---|---|
| R1, consumers whose §3.4 row stops | 9 | 11 | 11 |
| R2, R3: `No authored PRD on` in ARD, SPEC | 1, 1 | 1, 1 (the slice bullets) | ARD:280, SPEC:321 |
| R4: `No authored PRD on`, whole scope | 2 | 3 | 3: ARD:280, SPEC:321, UPS:57 (`grep -rn "No authored PRD on" plugins CLAUDE.md .claude/rules docs/maintainers README.md --include=*.md \| grep -v CHANGELOG`) |
| R5, R6: `CLAUDE.md`, the coupling file | 35,215 and 18,687 characters | 35,972 and 19,749 characters | the same (*Budgets*) |
| R7, the floor (`is not a prerequisite\|not a prerequisite at all\|is still not a prerequisite`, lines) | 23 | 20 | 20 |

The population file's `wic` function (its §2), pasted and run here for the scope and for `reference-parts/`, gives at `db46afff`: the four ids 21 / 3, 20 / 3, 22 / 3 and 19 / 3; `UPDATE_SPEC_NEEDS_PRD` and `UPDATE_SPEC_PRD_NOT_HANDED_OFF` 0 / 0; `is not a prerequisite` 15 / 6; `never becomes a prerequisite` 0 / 0; `is reported and never a stop, on either route` 0 / 0; `reports an absent PRD rather than stopping on it` 0 / 0; `as on the idea route` 4 / 0; `never optional` 11 / 2; `whose gated input was never optional` 6 / 0; `an absent optional input` 4 / 0. Each is the after-count the population file records, `as on the idea route` at the fix wave's 4.

**The result.** Task 8 read each of the 102 rewrite rows then in the file at `97fb8c8c` and found every one done; re-ran §1's searches and read every new or changed hit (65 lines outside `reference-parts/`, and the 42 new sentences of the 82 changed blocks the paragraph-level pass flags); and found no line in scope that says `/create-ard` or `/specify` goes on, on the idea route, where the PRD folder's `prd.md` is not on the default branch (the population file, *Task 8 — found at the after-count*, item 2; not re-derived here). The final review then found statements of the old behaviour that the sweep had missed or left to batch 4 though they were already false — I1's `workflow.md:138` with three mermaid edges, and I2's four page sites — and the fix wave rewrote them as F1 to F7; its re-review, scoped to the wave, raised no other. The narrowing of *an absent optional input never becomes a prerequisite* is itemised sentence by sentence as T6-N1 to T6-N21, against `CLAUDE.md:154`, the handoff rules file's line 24, `.claude/rules/product-workflows.md`, `brd-route.md` and PH.

**What is recorded for later batches, and where.** The design's §5.5 (added on this branch) lists what batches 2, 3 and 4 owe beyond their own §5.2 to §5.4: for batch 2, `DESIGN_NO_SPEC`, `/design`'s excluded-count stop and its map line, `CONFORMANCE_NO_REQUIREMENTS`, `/design`'s and `/conformance`'s offers of `/create-ard`, `/security-workflows:scan`'s `pa_next_step` offer, and the `dev-workflows` pages that call `/design`'s `specification.md` this plugin's one gated input that stops (L-B2-24 to L-B2-30); for batch 3, `/release-notes`' offer of `/create-ard` (L-B3-7); for batch 4, the landed-`prd.md` condition on `/brd-reconcile`'s and `/brd-interview`'s offers and `next-phase-offer`'s BRD part, the pages that say the two commands are offered on the level test alone, the slice form of the two new `*_PRD_NOT_HANDED_OFF` stops beside the register stop it leads to, `workflow.md:199–200`'s ledger condition, and the two *No coverage-ledger check.* bullets. The population file's §5 holds every later row with its reason. Each names, until its batch ships, a command whose own stop then names the right one: two true stops in a row, not a false statement (rulings 7, 8, 23 and 37).

## The reviews

From the ledger and the findings files in the scratch directory; the review reports themselves were not re-read here.

| Review | Model | Head reviewed | Findings | Disposition |
|---|---|---|---|---|
| The design | not in this run's sources | the design branch | a review and a re-review | answered before pull request #195 merged (`16aa6872`, `14d0124c`) |
| Pre-flight scan of the plan | the controller | the plan | three points: Task 1's *Interfaces* slip, Task 2 Step 8's order, Task 7's versions | rulings 1 to 3 |
| Task 1 | Opus | `5562e4cf` | Needs fixes: 3 Important (`prd-ground.md:540–546` missing; K70 and K72 kept on a false reason, `design.md:114` unlisted; `release-notes.md:760` missing), Minors | fix round 1, `41d62ebb` (212 rows); re-review: all addressed, 0 open; item 11 deferred, then left |
| Task 2 | Opus | `14cb4f5f` | Approved, 0 Critical or Important, 5 Minor | fixed in round 1, `eb765b4a`; 0 open (ruling 14) |
| Task 3 | Opus | `769fbac7` | Needs fixes: 1 Important (ARD's bare `mv` fails on a relative path), 5 Minor | round 1, `6b0d1a11`; 0 open |
| Task 4 | Opus | `449ad3d6` | Needs fixes: 1 Important (`/update-spec`'s Phase 8 offered `/specify <SIBLING-EPIC>`, which now stops), 4 Minor | round 1 (`5cb20caa`, `548b8854`): 1 new Important (step 7's capture stamps, or fails on, an input the new guard skips), 2 new Minor; round 2 (`6887b35d`): 1 new Minor (an over-claim); round 3 (`77aa580f`): 0 open; two Minors deferred (lines 76, 80) |
| Task 5 | Opus | `7f5e1c66` | Approved, 0 Critical or Important, 4 Minor; one open question the controller settled by reading (line 86) | round 1, `b5115405`; 0 open |
| Task 6 | Opus | `126b4752` | Needs fixes: 2 Important (`CLAUDE.md:153` stated the design's end state as a rule binding today; a live check's setup landed in row E), 8 Minor | round 1, `ba3d9238`; 0 open |
| Task 6M (the merge of #197 and #198) | Opus | `b01883a6` | Approved, 0 Critical or Important, 3 Minor; the merge lossless against both parents by the reviewer's own mechanical check | Minors 1 and 2 fixed in Task 7, 3 left as report-only (ruling 31) |
| Task 7 (the release) | Opus | `62abd88c` | Needs fixes: 1 Important (the changelog's *before any question* over-claimed), 5 Minor; one open question the controller settled by grep (line 112) | round 1, `97fb8c8c`; 0 open |
| Task 8 Step 1 (the after-counts) | — | `a39f75f6` | no task review (ruling 34) | read by the final review |
| Whole branch | Fable | `a39f75f6`, over `9b1d6aef..a39f75f6`, `reference-parts/` and the plans left out of its package | With fixes: 0 Critical, 3 Important (I1 an old-behaviour sentence on `workflow.md:138`; I2 three page sentences false now though recorded as batch 4's; I3 on a slice the uncommitted remedy leads into the register's stop), 9 Minor (M1 to M9), 6 record errors, 1 recommended live check | the fix wave: I1 to I3, M2, M3, M4, M6, M8, M9 and the record errors fixed, the live check added; M1 and M7 no edit, M5 recorded (rulings 35 to 39) |
| The fix wave | Opus implementer | `fc0721a9` (20 files), and `9a76bad2` for `/prd-proposal`'s own rename form (ruling 40) | — | its report: chain exit 0, published check exit 0, recipe 11 |
| The fix wave's re-review | not in the ledger | `9a76bad2`, over `a39f75f6..9a76bad2` | every finding addressed; the tightened I3 test sound in states (a) to (d); 0 new Critical or Important; 3 Minor in the wave's own text and 1 pre-existing | fixed in `db46afff` (ruling 43) |
| The last four wording fixes | not in the ledger | `db46afff` | a short scoped check: all four addressed, no new breakage; the untracked, no-`origin` and read-only-mount variants of the rename block read, not run | — |

The last four wording fixes, in `db46afff`: the I3 slot rule's clause now reads *carries onto `<new-branch>` where git can* (ARD:322, SPEC:363), since git refuses the switch where HEAD's committed register differs from `<default-ref>`'s under an uncommitted change; the rename form's commands are split into two blocks around the hand edit that adds `kind: prd` and `key:` (ARD:290–301, SPEC:331–342, `prd-proposal.md:206–219`), since five lines pasted at once committed `prd.md` without them; the changelog's and the pages' summaries of the committed form now turn on whether `origin` already holds every commit of the branch, and their summaries of the rename give its untracked and no-`origin` cases; and both `PRD_PROPOSAL_NEEDS_PRD` forms gain PH §4.4's parts 2 and 4.

## What was merged from `origin/main`, and how the batch was re-proved

- **PRs #198 and #197**, `main` at `c12ca55f`: SEC-G2 B, the ARD threat model (`/create-ard` gains Phase 4.3, `lineage.py`'s `stamp` takes repeated captures), and B39, unsafe branch names (row I now matches a HEAD on a branch outside `specs-repo-git` §3.2's safe class). `git diff --name-only 0de91630 c12ca55f | wc -l` gives 88; `git merge-tree --write-tree --name-only ba3d9238 c12ca55f` lists 8 conflicted files, one of them generated (`reference-parts/phase-handoff/require-on-main.md`), so 7 hand-edited, `create-ard.md` and `phase-handoff.md` among them, as the ledger's line 95 says. Merged by Task 6M at `7d8e214f`, and the merged `CLAUDE.md` (36,120 characters) cut back to 35,947 at `b01883a6`. The batch was re-proved on it by Task 6M: §1's searches over what `main` added (22 line hits and 20 blocks, each read; rows M1 to M9, all *keep*), `/create-ard` re-walked (T3-W24 to T3-W29 added, among them B39's branch outside the safe class stopping at row I before the committed form), `/update-spec`'s lineage test re-run against the merged `lineage.py` (capture and stamp exit 0, the stamped `upstreams:` naming the ARD alone), the 35-step chain and the recipe (11) — all from Task 6M's report and the population file, not re-run here — and the Opus review that found the merge lossless.
- **PR #199**, `main` at `9b1d6aef`: B40, branch names outside the specs repository. `comm -12` of `git diff --name-only c12ca55f b01883a6` and `git diff --name-only c12ca55f 9b1d6aef`, each sorted, prints nothing, and `git merge-tree --write-tree --name-only b01883a6 9b1d6aef` exits 0. Merged by the controller at `95e30032` (ruling 32), after which the tree gates passed (the ledger). It moved `main`'s versions to `product-workflows` 3.81.2, `workflows-core` 1.90.2, `dev-workflows` 4.66.2 and `docs-workflows` 1.39.4 (each `plugin.json` at `9b1d6aef`); the ledger's line 105 names the first three, `docs-workflows` not then being in the release.
- **The merged tree as a whole** was read by the whole-branch review (`9b1d6aef..a39f75f6`), and the full chain passed on it at `97fb8c8c`, `9a76bad2` and `db46afff` (the controller's runs).

## What departs from the design or the plan

- **Four plugins released, not two.** The plan's Task 7 names `product-workflows` and `workflows-core`; `dev-workflows` 4.66.3 carries E11 to E16 and E19 (ruling 9), and `docs-workflows` 1.39.5 its environment page (ruling 33).
- **Two tasks the plan does not have.** Task 6M, the merge of #197 and #198 before the release (ruling 26), and the fix wave the population file calls *Task 9*.
- **`CLAUDE.md`'s clause** is not the plan's Task 6 Step 1 wording, which stated the design's end state (ruling 25); it reads *becomes a prerequisite only by a recorded decision, never by the gate (`workflows-core:phase-handoff` §3.4 names each input that stops and why; …)* (`CLAUDE.md:154`), and its `why` link is in the handoff rules file instead (rulings 27 and 31; the plan's Task 6 Step 4 allows either).
- **Units.** The plan's *Global Constraints* give both budgets as `wc -c`, bytes, against warnings that count characters; this record measures characters, and the population file's R5 and R6 carry dated corrections saying so.
- **The existing stops were changed beyond the plan.** `PRD_GROUND_PRD_NOT_HANDED_OFF`'s and `PRD_PROPOSAL_PRD_NOT_HANDED_OFF`'s uncommitted forms gained §4.4's parts 2 and 4, where the plan said they keep their text (ruling 24); `/prd-proposal`'s `PRD_PROPOSAL_NEEDS_PRD` forms gained the full rename instruction and the two missing parts (rulings 40, 43); `CREATE_ARD_NOT_FOUND`, `SPECIFY_BRD_NOT_FOUND` and `EPICS_NOT_FOUND` lead with `/create-prd` (rulings 17, 18).
- **`/update-spec`'s carve-out grew** past the plan's one sentence: the Phase 2 guard, step 7's capture and Phase 8's offers, and `document-lineage` §1 with them (rulings 19, 36); the design's §5.1 carries a dated note saying so.
- **The rename form** prints the commands that commit the rename on a new `prd/` branch and says to add `kind: prd` and `key:`, where the plan's text said *land the rename* (the final review's M2).
- **The slice's uncommitted form** tests the register and adds a sentence where it is unlanded (the final review's I3, ruling 41), which the plan's stop texts do not have.
- **The design's §5.5 and two dated notes** (in L12 and in §5.1) were added to the design on this branch, so the design's text now records what batch 1 found.
- **The whole-branch review ran on Fable**, where the plan's Task 8 Step 3 and the design's §10 say an Opus review; the ledger's line 5 gives the run's models. Every task review ran on Opus.
- **Fix rounds.** Every task's Minors were fixed in its own round, not deferred (ruling 14), and the fix wave was followed by two more commits, `9a76bad2` before its re-review and `db46afff` after it (rulings 40, 43), where the execution skill allows one wave.
- **Not yet done, by the plan's order:** Task 8 Step 5, the push, the pull request, its CI and the update commands, follows this record.

## Known and left

Each of these is open on this tree.

- **The live checks have not been run.** The 16 checks at `docs/superpowers/to-test-on-real-project.md:132–147` have never run on a real project, and the maintainer has not chosen when they run (§11 item 4).
- **The to-fix entry stays** until the last batch (§11 item 5); `docs/superpowers/to-fix.md:135` still says the work is the maintainer's to schedule as a design of its own.
- **Owed by batches 2, 3 and 4**, listed in the design's §5.5 and the population file's §5 (*The claim sweep*, above). Until each ships, those sites name a command that itself stops and names the right one, and several offers name a run that stops on arrival, against design L8: `/design`'s and `/conformance`'s offers of `/create-ard`, `/security-workflows:scan`'s `pa_next_step` offer, `/release-notes`' offer, and `/brd-reconcile`'s and `/brd-interview`'s offers on a slice whose `prd.md` is on no ref (rulings 7, 8, 23, 37).
- **M7, the maintainer's to decide.** `/create-ard`'s Phase 4.3 requirement-gap line, SEC-G2's text, names `/product-workflows:update-prd`, which stops `UPDATE_PRD_NO_PRD` on a BRD slice holding no `prd.md` (population row M7; rulings 30 and 38). The maintainer is asked; the ledger records no answer.
- **The grounding-file lineage asymmetry, the maintainer's to file or not.** A grounding file `<default-ref>` holds whose working copy differs, after a declined `/prd-ground` re-run, is diffed against the default branch's copy, read from disk in `/update-spec`'s Phase 3 and recorded at its disk bytes, so a change outside the confirmed items is never proposed once it lands. Pre-existing, left out of this merge and not filed; the maintainer is told (ledger line 76; ruling 39).
- **The correction owed to the maintainer.** The maintainer was told during Task 6M that `main`'s `CLAUDE.md` was over its warning; it was not (*The numbers*). The ledger records the correction as owed in the next message and does not record it sent (line 100).
- **Two true stops in a row while an idea's pull request is open** are accepted for every batch's never-produced stop (M1, ruling 35; design §5.5).
- **The rename form on a pre-rename PRD tracked only on HEAD's non-default branch**: the printed branch is cut from `<default-ref>`, so the printed `git mv` fails with `bad source`. Not handled (`final-fix-report.md`, concern 4; ruling 42).
- **An untracked register at a path `<default-ref>` holds** (case f): the shared uncommitted form's printed `switch` fails at its first line. Not handled (the fix report's concern 5, ruled with its other concerns; no ledger line names it).
- **Design L1's known limit, one name wider since B39.** A `prd.md` committed, while the checkout stands on another branch, on a branch no plugin prefix names — or, since B39, on a plugin-prefixed branch whose name is outside the safe class — is on no ref the plugin scans and in no folder, so on the idea route the run reads it as never produced and names `/create-prd` (design L1; population row M4).
- **Reviews this record cannot show.** `db46afff` had only the short scoped check; the controller's merge `95e30032` had no review of its own before the whole-branch review; the models of the fix wave's re-review and of that check are not in the ledger; this record, the rulings summary and the ledger copy were not reviewed before they were committed.
- **The rename block's untracked, no-`origin` and read-only-mount variants** were read by the scoped check, not run (ledger line 133); the fix report's scratch test ran the tracked form with `origin`.

## Not re-derived here

The controller's 35-step chains at `97fb8c8c`, `9a76bad2` and `db46afff`, whose logs were not kept; Task 6M's chain on the merged tree; every scratch test in the task reports and the fix report (the HEAD test's relative and absolute paths, the rename commands, the lineage capture and stamp, I3's cases a to f); the walks' verdicts beyond the rows re-read in *The states and the ids* and *The five Review Focus states*; Task 8's reading of the 102 rewrite rows and its 65 lines and 42 sentences; Task 6M's 22 line hits and 20 blocks; the paragraph-level pass's 184 blocks; the population file's after-counts beyond the strings re-run above; and the review findings' counts, which are the ledger's.

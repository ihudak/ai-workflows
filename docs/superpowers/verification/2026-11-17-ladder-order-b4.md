# LADDER-ORDER batch 4 — `/create-ard` and `/specify` stop on a slice whose ledger fails — verification record

**Plan:** `docs/superpowers/plans/2026-11-17-ladder-order-b4-brd-route.md`. **Design:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`: §5.4 with its *Settled while building (batch 4, 2026-11-17)* note, §5.5's *Batch 4* list, §10 and §11. **Measurements:** `docs/superpowers/plans/2026-11-17-ladder-order-b4-measurements.md`. **Population:** `docs/superpowers/plans/2026-11-17-ladder-order-b4-sweep-population.md`.

**Release:** `product-workflows` 3.85.0, `workflows-core` 1.98.0, `dev-workflows` 4.70.3, `docs-workflows` 1.43.1 and `security-workflows` 0.12.7, each changelog section dated 2026-11-17. They were first released at `a7309d98` as 3.85.0, 1.97.0, 4.70.2, 1.42.1 and 0.12.7. The release was re-derived at `c3dfddb7` after `origin/main` moved and was merged a second time.

**Branch:** `feat/ladder-order-b4`, cut from `main` at `67b4c740` (pull request #208's merge). `origin/main` was merged into it twice: at `fb626e46` (pull request #209) in `1b814df9`, and at `74d3e8d1` (pull request #210) in `39f4461f`.

**Measured at `f52bf346`, the head.** That is after the final review, its one fix wave, the re-review in two halves, the touch-up, the narrow check and the controller's one sentence. Every figure below was obtained here, in this session, on that tree, with its command beside it. Where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-17-ladder-order-b4-rulings.md` beside this file. The controller's ledger is `2026-11-17-ladder-order-b4-ledger.md`, verbatim save one name.

`awk '/^```text$/{f=1;next} /^```$/{f=0} f' docs/superpowers/verification/2026-11-17-ladder-order-b4-ledger.md | diff - .superpowers/sdd/2026-11-17-ladder-order-b4-brd-route/progress.md` prints one hunk, `41c41`, and nothing more. That line names the internal edition twice, a name `scripts/check-docs.sh`'s check 19 forbids anywhere in the repository, and the copy writes each occurrence `<internal-edition>`. The same diff with line 41 deleted from both sides (`sed '41d'`) prints nothing and exits 0.

The copy's text block hashes to md5 `9f98152f147fdbb3da47f2395ebcbb73`, and `progress.md` to `072aa3a39e480455c1fadc1e9e764ee1`; both are 173 lines. Every *ledger line* below is a line of that file: `progress.md`'s line *n* is its line *n* + 5. *Ruling N* is the rulings file's entry N, and *R n* or *P n* its rows from the plan's tables.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/ladder-order-b4`. `git branch --show-current` printed `feat/ladder-order-b4`, `git log --oneline -1` printed `f52bf346`, and `git status --short` printed nothing, before the checks and after them.

`git fetch origin` updated no ref. `git rev-parse origin/main` and `git merge-base HEAD origin/main` both print `74d3e8d1eb070c852b3e23f5113a8f6d73a24cd2`, and `git log --oneline HEAD..origin/main | wc -l` prints 0: **`origin/main` has not moved since `74d3e8d1`**, and the branch holds all of it.

`$S` below is a scratch directory outside the repository. `$S/main-tree` is `origin/main` unpacked there with `git archive 74d3e8d1 | tar -x -C $S/main-tree`, and `$S/base-tree` is `67b4c740`, where the branch was cut, unpacked the same way.

Abbreviations are the plan's (its line 13):
- **Commands under `plugins/product-workflows/commands/`:** CPRD `create-prd.md`, ARD `create-ard.md`, SPEC `specify.md`, INT `brd-interview.md`, REC `brd-reconcile.md`.
- **References:** CLF `plugins/product-workflows/references/coverage-ledger-format.md`; PH `phase-handoff.md` and NPO `next-phase-offer.md`, both under `plugins/workflows-core/references/`.
- **Other files:** DES the design; TT `docs/superpowers/to-test-on-real-project.md`; CPL `.claude/rules/plugin-updates-coupling.md`; *page X* `plugins/<plugin>/docs/commands/X.md`.
- **Changelog sections:** PW-CL, WC-CL, DV-CL, DW-CL and SEC-CL are the batch's sections of the five changelogs.

Every line number is at `f52bf346`.

## What was built

**The branch.** `git log --oneline origin/main..HEAD | wc -l` gives 45, and so does `git log --oneline --first-parent origin/main..HEAD | wc -l`; `origin/main`'s own commits since the cut are reachable from both and are not counted. `git log --oneline 74d3e8d1..HEAD --no-merges | wc -l` gives 43. `git log --merges --format='%h %p' 74d3e8d1..HEAD` prints two merges, each with the branch as its first parent and `origin/main` as its second:
- `39f4461f 3b13ecc1 74d3e8d1`, 19:08 UTC;
- `1b814df9 0dc232d1 fb626e46`, 17:37 UTC.

The 43 by task, from the ledger and `git log`, all on 2026-11-17:

- **The plan, outside any task**: `b0016cdb` (the plan, its measurements and its sweep population), `bb24d9b8` (revised after the pre-flight scan), `0803b2c3` (R6 reversed after Task 1's stop) and `db043170` (R18 and R19, after Task 1's review).
- **Task 1, CLF §5 states the tests whole and `/create-prd` follows**: `e28030b4`, fix rounds `96c7d0ee` and `1285c6f9`.
- **Task 2, `/create-ard`'s Phase 0 stop**: `d73784a3`, fix rounds `a89fdd9e` and `0cc4c7af`, and the closing three sentences `305cf2ec`, applied by Task 3's implementer.
- **Task 3, `/specify`'s stop, with `/update-spec` taking neither**: `11dccc0b`, fix rounds `8a59c089` (R20) and `25f60f50`, and the closing six sentences `46e1e382`.
- **Task 4, PH §4.4's rung**: `d1e0a6c0`, fix round `bf615441`, and the closing two sentences `890e0dd0`, applied by Task 5's implementer.
- **Task 5, the readers outside `product-workflows`**: `7f588d93`, fix round `a5fa9be2`, and the closing seven sentences `c2c5fb20`.
- **Task 6, the route's own offers**: `eb63aa5d`, fix round `97d818fb`, and the closing seven sentences with the R21 and R22 rows, `a62b542d`.
- **Task 7, the committed form**: `f3cdc049`, and the closing four sentences `05312e02`, applied by Task 8's implementer.
- **Task 8, a grounding file written and never handed off**: `2efc8485`, fix rounds `cdd3c224` and `cc8581c3`.
- **Task 9, pages, diagrams, rules and rationale**: the three deferred sentences `65a37ece`, then `e74fce93`, fix rounds `0dc232d1` and `3b13ecc1`.
- **Task 10, room for the coupling bullet**: `e178a73a`, superseded at the second merge (ruling 43).
- **Task 11, the release**: `docs-workflows` 1.42.0's three sentences `0fe5592d`, the release `a7309d98`, its re-derivation after the second merge `c3dfddb7`, and fix round `e6b1df78`.
- **The final review**: the wave's `b31971b0` (`product-workflows`), `c6b5bd2f` (`workflows-core`, `dev-workflows`, `docs-workflows`) and `2d805ec4` (the records); the touch-up `7344fa9f`; and the controller's one sentence, `f52bf346`.

4 + 3 + 4 + 4 + 3 + 3 + 3 + 2 + 3 + 4 + 1 + 4 + 5 = 43.

**The files — what the pull request will show.** `git diff --stat origin/main HEAD | tail -1` prints `96 files changed, 3433 insertions(+), 654 deletions(-)`, and the three-dot form prints the same. By `git diff --name-only origin/main HEAD`:
- **37 under `plugins/product-workflows`**: 14 commands and their 14 pages, `brd-workflow.md`, `workflow.md`, `getting-started.md`, `roles-and-phases.md`, `reference/environment.md`, `reference/glossary.md`, CLF, the changelog and `plugin.json`.
- **21 under `plugins/workflows-core`**: PH, NPO, `components.md`, `document-lineage.md`, `followup-emission.md`, `docs/family-map.md`, 13 regenerated files under `reference-parts/`, the changelog and `plugin.json`.
- **11 under `plugins/dev-workflows`**: the commands `conformance.md`, `design.md`, `implement.md` and `ready.md`, their four pages, `docs/reference/follow-ups.md`, the changelog and `plugin.json`.
- **8 under `plugins/security-workflows`**: `scan.md`, its page, `security-register.md`, `session-feedback.md`, `roles-and-phases.md`, `workflow.md`, the changelog and `plugin.json`.
- **7 under `plugins/docs-workflows`**: `document.md`, `release-notes.md`, their pages, `references/key-discovery.md`, the changelog and `plugin.json`.
- **Outside the plugins**: four `.claude/rules/` files (`brd-route.md`, `plugin-updates-coupling.md`, `product-workflows.md`, `security-workflows.md`), `docs/maintainers/rationale.md`, the plan, the measurements and the population, DES, `docs/superpowers/to-fix.md`, TT and `.claude-plugin/marketplace.json`.

`git diff --name-only origin/main HEAD | grep -vE '\.md$'` lists only the marketplace and the five `plugin.json` files. `git diff origin/main HEAD -- 'plugins/*/.claude-plugin/plugin.json'` changes no line but `version`. Run with `-- '*.py' '*.sh' '*.mjs' scripts .github 'plugins/*/agents' 'plugins/*/hooks' 'plugins/*/skills' 'plugins/*/scripts'`, the same diff lists nothing but those six JSON files: no script, agent, hook, skill or workflow changed.

The branch's own 43 commits touched 100 files (`git log 74d3e8d1..HEAD --no-merges --name-only --format= | sort -u`). `comm` of that list with the 96 finds every one of the 96 among the 100. The other four — `CLAUDE.md`, `.claude/rules/plugin-updates.md`, `plugin-updates-coupling-history.md` and `plugin-updates-coupling-history-5.md` — equal `origin/main`'s, its side having been taken whole at the second merge (ruling 43). The figures are taken before the commit that carries these three records and the design note's correction.

**What the batch delivered against the design's §5.4.**

| §5.4, and the ruling | Where on the tree |
|---|---|
| The table: on a slice, each command stops unless the ledger is readable, no claimed row `unallocated`, one `covered-here`, under the four ids | ARD:281 (*The slice's ledger tests — on the BRD route, before every gate*), messages at ARD:295, :298, :301, :304; SPEC:325, messages at :339, :342, :345, :348 |
| *These are `/create-prd`'s tests, not new ones* (R6 as reversed, R18, R19) | CLF §5 (:332) and §5.2 (:581). CLF:357 to :359 names `/create-ard` and `/specify` as consumers, under their four ids, and has them carry §5.2's rows |
| *The test is stated once*; restated once more for the plugins that cannot read CLF (R2) | PH §4.4 (:602), *The first missing document*, the `prd.md` rung at PH:617 |
| The offers that would now stop are made conditional (L8; R1, R5, R17, R21 to R23) | NPO's *The landed condition* (:270); INT:2631 and REC:3136 (the line beside a landed `prd.md`, R23); the kept-offer sentence (*The recipes*, below) |
| What the stop makes unreachable is removed | the population's *Unreachability, confirmed before removal* sections under Task 2 and Task 3 walks; the retired strings below |
| Two statements overturned (ARD and SPEC, *reads no `claims:` list …*) | that string counts 0 (*The retired strings*) |
| `/implement`'s stop names what the tests resolve (by R2, through §4.4) | `plugins/dev-workflows/commands/implement.md:424` (*whose ledger tests that rule's `prd.md` rung finds failing*); `IMPLEMENT_BRD_NOT_SLICED` per slice (P5) |
| The BRD-route `*_NOT_HANDED_OFF` stops gain the committed form (R10, R11, P1) | PH §4.4 row F (:615), its several-files rule; the two new ids of Task 8 (P7) |
| Nothing else on the route is required | page create-ard:78 (*A slice with no `prd.md` that passed the slice's ledger tests … is reported*) |
| The kind-gate rule: the test reads `brd-link.md` and the ledger, never the asserted kind | ARD:281 and SPEC:325 key the step on `prd_dir` carrying a `brd-link.md` |

## The merges of `origin/main`

**The first, `fb626e46`** (pull request #209, `docs-workflows` 1.42.0, `documentation_paths`). It brought 3 commits and 20 files since the cut (`git log --oneline 67b4c740..fb626e46 | wc -l`; `git diff --name-only 67b4c740 fb626e46 | wc -l`). It was merged by the controller at `1b814df9` (ledger line 141, *auto-merge clean*).

`comm -12` of its file list with `git diff --name-only 67b4c740 0dc232d1` — the merge's first parent — gives the 5 files both sides changed: `docs/maintainers/rationale.md`, `plugins/docs-workflows/commands/document.md`, `release-notes.md` and their two pages. That is the ledger's *five files changed on both sides*. Task 11 then corrected three loose sentences 1.42.0 had shipped (`0fe5592d`, ledger line 46).

**The second, `74d3e8d1`** (pull request #210, DOC-D-G1, `/docs-workflows:docs-write`). It brought 47 commits and 114 files since `fb626e46` (`git log --oneline fb626e46..74d3e8d1 | wc -l`; `git diff --name-only fb626e46 74d3e8d1 | wc -l`). `git merge-base 3b13ecc1 74d3e8d1` is `fb626e46`, and `comm -12` of the two sides' lists gives 26 files changed on both, as the ledger's line 150 says.

It was merged by a dispatched Opus merger at `39f4461f`. `merge-2-report.md` lists 14 conflicted files and 12 merged cleanly. Its resolutions:
- `origin/main`'s side was taken whole for `CLAUDE.md` and the four coupling files, `origin/main` having made its own, larger `history-5`.
- This batch's coupling bullet was re-added after `origin/main`'s 1.97.0 bullet.
- Each changelog keeps both sides whole.

The release was re-derived at `c3dfddb7` (ruling 43). `workflows-core` went 1.97.0 → 1.98.0, `dev-workflows` 4.70.2 → 4.70.3 and `docs-workflows` 1.42.1 → 1.43.1; `product-workflows` 3.85.0 and `security-workflows` 0.12.7 kept their numbers.

**What this record re-checked**, on `f52bf346`:
- **The files.** The 96 files that differ from `origin/main` and the four that equal it, as above.
- **`CLAUDE.md`.** It is byte-equal to `origin/main`'s (*Budgets*).
- **The coupling file.** A line diff (Python's `difflib`) against `git show 74d3e8d1:` finds one added line, this batch's bullet, and nothing else. `git diff --stat 74d3e8d1 HEAD -- .claude/rules/plugin-updates.md '.claude/rules/plugin-updates-coupling-history*.md'` prints nothing.
- **The coupling census.** `cat .claude/rules/plugin-updates-coupling*.md | grep -ho '^- \*\*[^*]*\*\*'` counts 84 headings: 8, 15, 23, 21, 10 and 7 in the coupling file and the five history files. `| sort | uniq -d` prints none, so none appears twice.
- **The changelogs.** Each of the five, with its first section removed, equals `origin/main`'s byte for byte (*Versions*).

The merge's semantic reading — no sentence `origin/main` brought is made false by this batch, nor the reverse — was not re-done here. It is the merger's (`merge-2-report.md` §4: `/docs-write` read whole, `origin/main`'s added lines searched by the batch's subjects, nothing to bring into step) and the final review's. Both halves read the merge: A's *The merge* found both sides' sentences in `roles-and-phases.md` and `workflow.md` agreeing, and B's *D* found *both merges kept both sides*.

## The gates

**The chain, run here.** Every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain, reading the chain's own exit status.

The workflow is unchanged since `origin/main` (`git diff --stat origin/main HEAD -- .github` prints nothing). Since the cut, `origin/main` added one step, the backlog-line reader's self-test (`git diff 67b4c740 HEAD -- .github | grep '^+.*run:'`). `grep -c 'run:'` on the file gives 38. Two of them, at lines 349 and 350, are inside a `#` comment and are not steps, so the file holds **36 steps**.

The steps were extracted by batch 3's record's script, unchanged (`2026-11-16-ladder-order-b3.md`, *The gates*). A step is a line whose first text is `run:`, after an optional `- `, and not a `#` comment; a block step (`run: |`) is the deeper-indented lines after it. The script found the 36 at workflow lines 82, 85, 88, 91, 96, 99, 112, 123, 131, 144, 152, 157, 160, 162, 164, 171, 186, 194, 198, 205, 211, 218, 225, 235, 242, 249, 256, 263, 270, 276, 284, 295, 302, 327, 352 and 361. Each runs as a workflow step's default Linux shell runs it, `bash --noprofile --norc -eo pipefail <step file>`, with a `### step NN` line echoed before it. `ASSERT_PUBLISHED` was exported empty, as the workflow's `env:` sets it on a branch push.

It ran from 21:26:31 to 21:38:37 UTC on 2026-11-17, `git status --short` printing nothing before and after, and printed **`CHAIN_EXIT=0 steps=36`**, all 36 `### step` lines reached. Each step's result line:
- **Catalog and ID grammar.** Step 2 `0 error(s), 0 warning(s) across 1 repo(s).`; step 4 `PASS: no dash-form requirement IDs under .`; step 5 `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`.
- **Docs.** Step 7 `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`.
- **Reference parts.** Steps 9 to 12: `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 122 `FLAG` lines (`grep -c '^FLAG'`), which it prints and does not fail on; `check-citations: PASS -- 4 split reference(s)`; `check-questions: PASS -- 38 command(s) load the question rules before their first question`; `check-branch-check: PASS -- 24 command(s) run branch-check`.
- **Mermaid.** Step 13's `npm ci` *added 152 packages*. Step 15 `PASS: all 51 mermaid blocks in 1267 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`.
- **The self-tests that print a count.** Step 18 `run-state selftest: PASS (252 checks)`; 19 `pieces selftest: PASS (77 checks)`; 22 `proposal-record` `selftest: 44/44 passed`; 23 `ledger-evidence` `20/20`; 24 `bundle-scan` `SELFTEST PASS (102 cases, 0 failed)`; 25 `register.py` `121/121`; 26 `weakness-classes` `57/57`; 27 `key-discovery` `76/76`; 28 `backlog-lines` `57 passed`; 29 `bounded` `SELFTEST PASS (23 cases, 0 failed)`; 30 `lineage` `62 passed`; 32 `statusline selftest: 19 passed, 0 failed`; 35 `specs-git selftest: PASS (1201 checks)`; 36 `mutants: 23 checked, 0 stale`.
- **The rest.** Steps 1, 3, 6, 8, 14 and 16 print `SELFTEST PASS`; steps 17, 20, 21, 31 and 34 each print a `PASS` line with no count; step 33, the copied-scripts check, prints nothing on a pass.

**Then, each on its own, same tree, still clean:** `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` printed the same `PASS: docs are consistent …` line, rc 0, after two `check 9 cost-emitting-commands assertion not applicable` lines, for `plugins/guideline-reviewers` and `plugins/prose-style`. `python3 scripts/validate-catalog.py` printed `0 error(s), 0 warning(s) across 1 repo(s).`, rc 0.

**Re-run with these three records and the design note's correction in the work tree and staged**, from 21:52:30 to 21:54:22 UTC, each exiting 0:
- `./scripts/check-docs.sh --root .` and `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`, each printing its `PASS: docs are consistent …` line;
- `./scripts/check-id-grammar.sh --root .` and the same with `--baseline` after it, each printing `PASS: no dash-form requirement IDs under .`;
- `./scripts/check-id-grammar.sh --baseline` as the workflow runs it: `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`;
- `python3 scripts/validate-catalog.py`: `0 error(s), 0 warning(s) across 1 repo(s).`;
- `node scripts/mermaid/check-mermaid.mjs --root .`: `PASS: all 51 mermaid blocks in 1270 tracked markdown files parse`, the three new records among the 1,270, none holding a mermaid block.

`git diff --cached --check` printed nothing.

On a first try in this session, check-docs failed. Its check 19 found the internal edition's name on line 46 of the ledger copy, the one line this record's opening ledger paragraph describes. The copy now writes that name `<internal-edition>`, and the result above is the run after that change. After this record's last edit, the full 36-step chain was run once more, with the three records and the design note staged, and the commit was made only on its exit 0.

## The six new stops

Each id, where its command defines it, and where its page names it. The definition is the message template, every form listed; the page entry is the line in the command's page that names the id.

| Id | Defined | Routed from | Page entry |
|---|---|---|---|
| `CREATE_ARD_BRD_UNALLOCATED` | ARD:295 | ARD:285, *The slice's ledger tests*' *Unallocated* bullet | page create-ard:89 |
| `CREATE_ARD_BRD_NOT_ELIGIBLE` | ARD:298 (rows claimed, none `covered-here`), :301 (`claims:` names no row), :304 (the ledger missing or unreadable) | ARD:286 and the bullets after it | page create-ard:90 |
| `SPECIFY_BRD_UNALLOCATED` | SPEC:339 | SPEC:329 | page specify:90 |
| `SPECIFY_BRD_NOT_ELIGIBLE` | SPEC:342, :345, :348, the same three forms | SPEC:330 and the bullets after it | page specify:91 |
| `BRD_SPLIT_GROUNDING_NOT_HANDED_OFF` | `plugins/product-workflows/commands/brd-split.md:205` (uncommitted form), :218 (committed form) | step 7b's split on `design-grounding.md`, `brd-split.md:283` | page brd-split:312, and :340 |
| `BRD_INTERVIEW_GROUNDING_NOT_HANDED_OFF` | `plugins/product-workflows/commands/brd-interview.md:267` (uncommitted), :280 (committed) | — | page brd-interview:236 |

**Design §11.1** says *Batch 4's ledger stops map no gate return and take no row there*. In PH, `awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | grep -c <id>` gives 0 for each of the four ledger ids, so none has a §3.4 row; each appears in PH only at §4.4's rung (PH:617). The two grounding stops do map the gate's return: `BRD_SPLIT_GROUNDING_NOT_HANDED_OFF` counts 2 in §3.4 (PH:335, :341) and `BRD_INTERVIEW_GROUNDING_NOT_HANDED_OFF` 1 (PH:342).

**The not-handed-off ids.** `grep -rhoE '[A-Z_]+_NOT_HANDED_OFF' plugins/*/commands/*.md | sort -u` prints **19 lines** at the head. 18 are ids:
- `BRD_INTERVIEW_GROUNDING_NOT_HANDED_OFF`, `BRD_PACKAGE_REGISTER_NOT_HANDED_OFF`, `BRD_PACKAGE_SHIPPED_NOT_HANDED_OFF`, `BRD_PROPOSAL_SLICE_NOT_HANDED_OFF`, `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF` and `BRD_SPLIT_GROUNDING_NOT_HANDED_OFF`;
- `CREATE_ARD_PRD_NOT_HANDED_OFF`, `CREATE_ARD_REGISTER_NOT_HANDED_OFF` and `CREATE_PRD_REGISTER_NOT_HANDED_OFF`;
- `EPICS_PRD_NOT_HANDED_OFF`, `IMPLEMENT_DESIGN_NOT_HANDED_OFF` and `IMPLEMENT_SPEC_NOT_HANDED_OFF`;
- `PRD_GROUND_INVENTORY_NOT_HANDED_OFF`, `PRD_GROUND_NOT_HANDED_OFF`, `PRD_GROUND_PRD_NOT_HANDED_OFF` and `PRD_PROPOSAL_PRD_NOT_HANDED_OFF`;
- `SPECIFY_PRD_NOT_HANDED_OFF` and `SPECIFY_REGISTER_NOT_HANDED_OFF`.

The nineteenth, `_PRD_NOT_HANDED_OFF`, is the tail of the wildcard `*_PRD_NOT_HANDED_OFF` at `prd-ground.md:574` and REC:3057, not an id. The same command over `74d3e8d1`'s tree (`git grep -hoE … 74d3e8d1 -- 'plugins/*/commands/*.md' | sort -u`) prints 17, and `67b4c740`'s 17 too. `comm -13` of `origin/main`'s list with the head's prints exactly the two new ids, Task 8's. Task 7's *the id grep prints the same 17 lines before and after* (ledger line 113) is that same count before Task 8.

## The recipes

**Consumers whose §3.4 row stops**, by the recipe in `.claude/rules/workflows-core-handoff.md:24`, run as it stands there:

```bash
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
# 13
```

Without the `wc -l` it prints `/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/create-ard` `/design` `/epics` `/implement` `/prd-ground` `/prd-proposal` `/specify` `/update-spec`. In `$S/main-tree` it gives the same 13. The four ledger stops take no row, as §11.1 requires; the rules file's *thirteen* holds.

**§4.4's *Which stops use it* recipe**, `grep -rln 'The first missing document' plugins/*/commands plugins/*/references`, as PH:617 writes it, prints **12 files**:
- PH itself;
- the nine that cite the rule: `plugins/dev-workflows/commands/` `conformance.md`, `design.md`, `implement.md` and `ready.md`; `plugins/docs-workflows/commands/` `document.md` and `release-notes.md`; `plugins/security-workflows/commands/scan.md`; and `plugins/workflows-core/references/` `components.md` and NPO;
- the two its sentence saves: CLF, *which names it only as where its §5 test is restated*, and `workflows-core:document-lineage`, *which names it only in the sentence it prints beside a reviser*.

Neither ARD nor SPEC is among them, as the sentence says: *never `/product-workflows:create-ard` or `/product-workflows:specify`*. That sentence reads *this reference, and each command and reference that cites the rule, save `product-workflows:coverage-ledger-format` … and `workflows-core:document-lineage` …*, and what the recipe returns is exactly that. In `$S/main-tree` it returns 10, without CLF and `document-lineage.md`.

**The kept-offer sentence, its two forms**, counted wrap-insensitively by the script in *The retired strings* (below), over the same scope, and by `grep -rF --exclude=CHANGELOG.md` line by line:

| Form | The sentence's ending | Copies | Where |
|---|---|---|---|
| `product-workflows` | `… — or no command (coverage-ledger-format.md §5).` | **9** (wrap-insensitive 9; single-line `grep -F` 9) | ARD:166; `epics.md:1150`, `:1213`; `idea.md:103`; `prd-proposal.md:831`; SPEC:84; `update-prd.md:233`; `update-spec.md:52`, `:162` |
| `workflows-core` | `… — or no command (workflows-core:phase-handoff §4.4, The first missing document).` | **8** (wrap-insensitive 8; `grep -F` 8), and 4 generated | `plugins/dev-workflows/commands/design.md:260`, `implement.md:1319`; `components.md:120`; `document-lineage.md:99`; NPO:206, :356, :409, :422. Generated: `reference-parts/next-phase-offer/pe.md:180`, `:193`, `pm.md:169`, `proposals.md:169` |

Both forms open `On a BRD-route slice that run applies the slice's ledger tests and stops where they fail, naming the run its stop names — '/product-workflows:brd-split' in the form that applies, or '/product-workflows:prd-ground' — or no command`.

Each was searched for as the whole sentence. Every copy found by the wrap-insensitive count is also found by the single-line `grep -F` of the same sentence, so each copy stands on one line and equals the searched sentence byte for byte.

The sentence's opening, `On a BRD-route slice that run applies the slice's ledger tests`, counts 17 = 9 + 8, so no third variant stands anywhere. In `$S/main-tree` it counts 0.

`epics.md:1150` holds the `product-workflows` form as bare text in a list item, followed by its placement note; the other eight hold it in a code span. The `workflows-core` form went from 4 copies to 8 in the wave (ledger line 168), and the ledger's *9 + 4 identical* (line 109) is the count before it.

**P5's sentence**, the other kept-offer sentence (ruling 5), reads `Each of those runs stops where the slice lacks what it builds from, and its stop names what that slice's first missing document needs (workflows-core:phase-handoff §4.4).` It counts **2**, at `plugins/dev-workflows/commands/conformance.md:60` and `design.md:68`, both whole and on one line. Its opening counts 2.

## The retired strings

Counted at `f52bf346`, in `$S/main-tree` (`74d3e8d1`) and in `$S/base-tree` (`67b4c740`). The scope is `plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`, every file that decodes as UTF-8. Every file named `CHANGELOG.md` is excluded by its name, as `--exclude=CHANGELOG.md` excludes it — never a line filter, which would also drop a line of the rules files that names the word. `plugins/workflows-core/reference-parts/`, being generated, is excluded too. Each string is counted wrap-insensitively, the match mapped back to its source line: whitespace is collapsed across each whole file and across the string. A string written `re:` is a regular expression matched on the collapsed text.

The script, batch 3's with the exclusions put as files, ran as `python3 -I $S/wic.py '<string>' …` from the root of each tree:

```python
import os, re, sys
def files():
    for r in ["plugins", "README.md", "CLAUDE.md", ".claude/rules", "docs/maintainers"]:
        if os.path.isfile(r): yield r; continue
        if not os.path.isdir(r): continue
        for d, ds, fs in os.walk(r):
            ds[:] = sorted(x for x in ds if x not in ("node_modules", "__pycache__", ".git")); yield from (os.path.join(d, f) for f in sorted(fs))
T = []
for p in files():
    try: raw = open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError): continue
    out, idx, ws = [], [], False
    for k, ch in enumerate(raw):
        if ch.isspace():
            if ws: continue
            ws = True; out.append(" ")
        else: ws = False; out.append(ch)
        idx.append(k)
    b = "history" if os.path.basename(p) == "CHANGELOG.md" else "generated" if p.startswith("plugins/workflows-core/reference-parts/") else "live"
    T.append((p, raw, "".join(out), idx, b))
for a in sys.argv[1:]:
    H = {"live": [], "generated": [], "history": []}
    if a.startswith("re:"):
        rx = re.compile(a[3:])
        for p, raw, c, idx, b in T:
            for m in rx.finditer(c): H[b].append(f"{p}:{raw.count(chr(10), 0, idx[m.start()]) + 1}")
    else:
        s = re.sub(r"\s+", " ", a).strip()
        for p, raw, c, idx, b in T:
            j = c.find(s)
            while j >= 0: H[b].append(f"{p}:{raw.count(chr(10), 0, idx[j]) + 1}"); j = c.find(s, j + 1)
    print(f"== {a!r}: " + ", ".join(f"{k} {len(v)}" for k, v in H.items()))
    for k, v in H.items(): print("".join(f"   {k}: {h}\n" for h in v), end="")
```

The count is the *live* bucket. The excluded hits, history and generated, are shown beside it and are not counted.

The list is the plan's Task 9 Step 5: its thirteen *must be 0* strings, then search 3's four. After those come the ledger's own: *name no option at all* (line 43), and the reason Task 8's fix round retired (line 126), in two lengths. Last is `takes as it stands`, which must be 0 in `conformance.md`, `design.md` and NPO.

| String | `67b4c740` (live) | `74d3e8d1` (live) | `f52bf346` live | excluded at the head (history / generated) |
|---|---|---|---|---|
| `level test alone` | 2 | 2 | **0** | 1 / 0 |
| `slice level alone` | 1 | 1 | **0** | 1 / 0 |
| `with no further condition` | 3 | 3 | **0** | 0 / 0 |
| `No coverage-ledger check` | 2 | 2 | **0** | 0 / 0 |
| ``reads no `claims:` list and no coverage ledger`` | 2 | 2 | **0** | 0 / 0 |
| `none of their own` | 3 | 3 | **0** | 0 / 0 |
| `are always offered` | 1 | 1 | **0** | 0 / 0 |
| `do not yet apply` | 1 | 1 | **1** | 1 / 0 |
| `as an authoring input` | 8 | 8 | **0** | 3 / 0 |
| `six literal arrays` | 1 | 1 | **0** | 0 / 0 |
| `whose ledger will never qualify` | 1 | 1 | **0** | 0 / 0 |
| `which it takes as it stands` | 2 | 2 | **0** | 0 / 0 |
| ``reads neither `claims:` nor the ledger`` | 1 | 1 | **0** | 2 / 0 |
| `cleared only` | 4 | 4 | **0** | 3 / 0 |
| `only one of its three refusals` | 1 | 1 | **0** | 0 / 0 |
| `only by hand damage` | 1 | 1 | **0** | 1 / 0 |
| `re:wrote it (and landed it )?with the slice` | 7 | 7 | **0** | 0 / 0 |
| `name no option at all` | 1 | 1 | **0** | 0 / 0 |
| `ground again what is already written` | 0 | 0 | **0** | 0 / 0 |
| `would ground again` | 0 | 0 | **0** | 0 / 0 |
| `takes as it stands` | 5 | 5 | **2** | 1 / 0 |

The generated bucket counted 1, 1, 1, 1 and 1 at `67b4c740` and `74d3e8d1` for `none of their own`, `do not yet apply`, `as an authoring input`, `which it takes as it stands` and `takes as it stands`, and counts 0 for every string at the head.

**The three that are not 0.**
- **`do not yet apply`, 1:** `.claude/rules/plugin-updates-coupling.md:21`, this batch's own coupling bullet. It quotes what the older rung says, to say what breaks beside an older `workflows-core`: *it says a `prd.md` nowhere on a slice is no gap, and that `/create-ard` and `/specify` "do not yet apply" the tests*. It stands by ruling 44. `git show 74d3e8d1:plugins/workflows-core/references/phase-handoff.md` holds the words, so the quotation is true of the default branch's 1.97.0. Its history hit is WC-CL, `plugins/workflows-core/CHANGELOG.md:14`.
- **`takes as it stands`, 2:** `plugins/docs-workflows/references/docs-profiles/render-verification.md:408` and `plugins/workflows-core/agents/code-scanner.md:64`, each *which a read takes as it stands* of a git ref. They are other subjects, as the plan says. The string counts 0 in `conformance.md`, `design.md` and NPO, which at `74d3e8d1` held three of its five hits (`conformance.md:702`, `design.md:283`, NPO:400).
- **`ground again what is already written` and `would ground again`** count 0 on every tree. The batch wrote the reason during Task 8 and replaced it in Task 8's fix round, which the ledger records as *4 → 0* (line 126).

**The other strings the ledger counts.** These stand by ruling and are not retired, so they are counted here, not re-read.
- ``re:while (that |its )?(`brd-link\.md`|that file) claims rows`` counts 12 live at the head and 11 at `74d3e8d1`. Task 9's figure was 11 (ledger line 125), and it was still 11 at `e6b1df78`. The wave's `b31971b0` took it to 12: its M-1 split CPRD's message for that state into a template of its own, and CPRD now holds the string at :337 and :350.
- ``re:while `claims:` names rows`` counts 23 live, 7 generated, at the head, and 2 at `74d3e8d1`. That is Task 9's 23.

## Budgets

`LC_ALL=C.UTF-8 wc -m`, since a bare `wc -m` counts bytes in this container (`wc -c` gives 36,087 for `CLAUDE.md`). `scripts/validate-catalog.py` sets `CLAUDE_MD_MAX = 40_000`, `CLAUDE_MD_WARN = 36_000` and `RULES_FILE_WARN = 20_000`, in characters (its lines 131 to 133).

- **`CLAUDE.md`: 35,840**, 160 under its warning. It equals `origin/main`'s: `git diff 74d3e8d1 HEAD -- CLAUDE.md` prints nothing (0 bytes), and `git show 74d3e8d1:CLAUDE.md | LC_ALL=C.UTF-8 wc -m` gives 35,840. At the cut, `67b4c740`, it was 35,978. The change is `origin/main`'s, taken whole at the second merge: the batch's own `CLAUDE.md` row from Task 10 did not survive it (ruling 43, P3).
- **Every `.claude/rules/*.md` is under 20,000.** There are 42 files, and none measures 20,000 or more (`for f in .claude/rules/*.md; do LC_ALL=C.UTF-8 wc -m < $f; done | awk '$1>=20000' | wc -l` gives 0). The three largest: `gates.md` 19,991, `dev-workflows-implement.md` 19,991 and `workflows-core-git.md` 19,986. None of the three is this batch's, and none changed against `origin/main`.
- **The four rules files the branch changes** (`git diff --name-only origin/main HEAD -- .claude`):

| File | `f52bf346` | `origin/main` `74d3e8d1` | Base `67b4c740` |
|---|---|---|---|
| `.claude/rules/brd-route.md` | 18,869 | 18,391 | 18,391 |
| `.claude/rules/product-workflows.md` | 18,292 | 17,771 | 17,771 |
| `.claude/rules/security-workflows.md` | 19,646 | 19,559 | 19,559 |
| `.claude/rules/plugin-updates-coupling.md` | 8,817 | 6,362 | 19,503 |

The coupling file's fall from 19,503 is `origin/main`'s move of its oldest bullets to `history-5`. `validate-catalog.py` printed no warning (*The gates*).

## Versions

Each version comes from three places: its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), its `.claude-plugin/marketplace.json` entry, and the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`). It is set against `origin/main`'s (`git show 74d3e8d1:plugins/<p>/.claude-plugin/plugin.json`) and the base's.

| Plugin | `plugin.json` | marketplace | Changelog heading | `origin/main` | Base `67b4c740` | The step |
|---|---|---|---|---|---|---|
| `workflows-core` | 1.98.0 | 1.98.0 | `8:## [1.98.0] — 2026-11-17` | 1.97.0 | 1.96.1 | minor, the next above 1.97.0 |
| `product-workflows` | 3.85.0 | 3.85.0 | `8:## [3.85.0] — 2026-11-17` | 3.84.1 | 3.84.0 | minor, the next above 3.84.1 |
| `dev-workflows` | 4.70.3 | 4.70.3 | `8:## [4.70.3] — 2026-11-17` | 4.70.2 | 4.70.1 | patch, the next above 4.70.2 |
| `docs-workflows` | 1.43.1 | 1.43.1 | `8:## [1.43.1] — 2026-11-17` | 1.43.0 | 1.41.0 | patch, the next above 1.43.0 |
| `security-workflows` | 0.12.7 | 0.12.7 | `8:## [0.12.7] — 2026-11-17` | 0.12.6 | 0.12.6 | patch, the next above 0.12.6 |

The three sources agree for each plugin, and each version is the next above `origin/main`'s at its level. The sizes are the release's own (`merge-2-report.md` §3), and are not re-judged here: minor where a reference dependents read gains a rule or a command gains stops, patch where only what stops and offers name changes.

`git diff origin/main HEAD -- .claude-plugin/marketplace.json` changes exactly five lines, each a `version` line: 4.70.2 → 4.70.3, 1.97.0 → 1.98.0, 1.43.0 → 1.43.1, 3.84.1 → 3.85.0 and 0.12.6 → 0.12.7. **No other plugin took a version:** `git diff --stat origin/main HEAD -- plugins/acli plugins/guideline-reviewers plugins/prose-style` prints nothing, and their versions, 0.1.4, 1.2.10 and 0.8.4, are `origin/main`'s.

**The changelogs.** A script read every `## [<version>] — <date>` heading of each of the five files at the head and at `origin/main`, and found the following in each:
- the head holds one heading more than `origin/main` — 197, 179, 303, 112 and 34;
- that heading is the batch's, first in the file, dated 2026-11-17;
- every heading is unique, and the headings strictly descend by version;
- the file with its first section removed equals `origin/main`'s byte for byte.

`grep -n '^## .*Unreleased' plugins/*/CHANGELOG.md | wc -l` gives 0. The dates: each new section is dated 2026-11-17, the day of the release commit `a7309d98`, of its re-derivation `c3dfddb7`, and of this record (`date -u +%F`).

**The coupling bullet** is CPL:21, *Update `workflows-core` 1.98.0 with `product-workflows` 3.85.0, `dev-workflows` 4.70.3, `docs-workflows` 1.43.1 and `security-workflows` 0.12.7*. It stands after `origin/main`'s 1.97.0 bullet and before the two `prose-style` bullets.

## The population file

Counted from `docs/superpowers/plans/2026-11-17-ladder-order-b4-sweep-population.md`, last changed in `7344fa9f`. A script took each section's table rows: a line beginning `|` that is neither a separator nor its table's header. It read each row's last cell. Nothing was re-walked here.

**The rows.** The section `## The rows` holds **153 table rows**: S-1 to S-117, and N-1 to N-36. The plan's line 11 names N-1 to N-24; N-25 to N-36 were added while building. Their `Status` cells:
- 138 begin `done in Task`;
- 11 begin `stays true — checked`;
- 3 begin `fixed in Task 5, Step 7 (not true as it stood)` (S-83, S-86, S-88);
- 1 begins `left as it stands` (S-116);
- **0 are `open`**.

The ledger's *153 rows, none open* (line 146) is the same count.

**The walks.** A row is counted as matching where its last cell, *Match*, begins `yes`. Every walk row matches:

| Section | Rows at the head | Matching | At the task's commit (`git show <sha>:<the file>`, the same script) |
|---|---|---|---|
| `## Task 1 walks` | 28 | 28 | 26 at `e28030b4` (the ledger's 26, line 28) |
| `## Task 2 walks` | 26 | 26 | 26 at `d73784a3` (line 47) |
| `## Task 3 walks` | 35 | 35 | 32 at `11dccc0b` (line 64); the three Epic-address rows came with its fix round (ruling 23's M3) |
| `## Task 3 fix round 1 — /create-prd walks` | 4 | 4 | — |
| `## Task 4 walks` | 18 | 18 | 17 at `d1e0a6c0` |
| `## Task 5 walks` | 15 | 15 | 15 at `7f588d93` (line 89) |
| `## Task 6 walks` | 28 | 28 | 19 at `eb63aa5d` |
| `## Task 7 walks` | 22 | 22 | 18 at `f3cdc049` (line 113) |
| `## Task 8 walks` | 21 | 21 | 14 at `2efc8485` (line 119) |
| `## Task 9 walks` | 21 | 21 | 21 at `e74fce93` |

218 walk rows, all matching. Beside them stand the itemisations of every narrowing: ten tables, under Tasks 1, 3, 4, 5, 6, 8 and 9. There are also 7 rows for the second merge (M-1 to M-7) and 52 for the final review's wave and touch-up (W-1 to W-52), which carry no *Match* column.

## The reviews

From the ledger. The counts are its own, from the review files; they were read here, not re-derived. Every dispatched review ran on Opus, save the final review's halves A and B, which ran on Fable. Task 8's closing round was read by the controller itself.

| Review | Head reviewed | Findings | Fix rounds, and how it closed |
|---|---|---|---|
| Pre-flight scan of the plan (an Opus scanner) | the plan, `b0016cdb` | eight rows needing a ruling, ten smaller fixes (line 12) | the plan revised at `bb24d9b8`; rulings 1 to 10 |
| Task 1 | `e28030b4` | spec ❌: 2 Important, 4 Minor (line 30) | round 1 `96c7d0ee` (8 addressed; re-review: 5 Minor, line 38); round 2 `1285c6f9` (5 addressed, line 43). Clean after two rounds |
| Task 2 | `d73784a3` | spec ✅: 1 Important, 9 Minor (line 49) | round 1 `a89fdd9e` (10 addressed; re-review: 1 Important, 6 Minor, line 54); round 2 `0cc4c7af` (7 addressed; re-review: 3 Minor, line 60); closed on `305cf2ec` with no further check (ruling 21) |
| Task 3 | `11dccc0b` | spec ❌ on two gaps: 1 Important, 5 Minor (line 65) | round 1 `8a59c089` (5 addressed; re-review: 1 Important, 6 Minor, line 71); round 2 `25f60f50` (7 addressed; re-review: 6 Minor, line 81); closed on `46e1e382` with no further check (ruling 27) |
| Task 4 | `d1e0a6c0` | spec ❌: 4 Important, 4 Minor (line 77) | round 1 `bf615441` (8 addressed; re-review: 2 Minor, line 86); closed on `890e0dd0` with no further check (ruling 28) |
| Task 5, in two halves | `7f588d93` | B: spec ❌, 1 Important, 8 Minor (line 91). A: spec ❌, 2 Important, 6 Minor (line 92) | round 1 `a5fa9be2` (17 addressed; re-review: 7 Minor, line 101); closed on `c2c5fb20` with no further check (ruling 33) |
| Task 6 | `eb63aa5d` | spec ❌ on one item: 1 Important, 9 Minor (line 96) | round 1 `97d818fb` (10 addressed; re-review: 7 Minor, line 109); closed on `a62b542d` with no further check (ruling 34) |
| Task 7 | `f3cdc049` | spec ✅: 0 Critical, 0 Important, 4 Minor (line 116) | closed on `05312e02` with no further check (ruling 35) |
| Task 8 | `2efc8485` | spec ✅: 1 Important (plan-mandated), 3 Minor (line 121) | round 1 `cdd3c224` (5 addressed; re-review: 1 Important, 3 Minor, line 131); round 2 `cc8581c3` (4 addressed), read narrowly by the controller (line 135) |
| Task 9 | `e74fce93` | spec ❌: 3 Important, 12 Minor, 2 nits (line 129) | round 1 `0dc232d1` (17 addressed; re-review: 12 Minor, line 143); round 2 `3b13ecc1` (12 addressed, line 146). Closed without a further check (ruling 41) |
| Task 10 | `e178a73a` | spec ✅: 0 Critical, 0 Important, 1 Minor, *keep* (line 138) | none needed |
| Task 11 | `a7309d98` | spec ❌ on one item: 1 Important, 10 Minor, and three behaviour changes with no changelog line (line 148) | round 1 `e6b1df78`, on the merged tree; its re-review is the records seat's job 1 (ruling 42) |
| The second merge (an Opus merger) | `39f4461f`, `c3dfddb7` | DONE_WITH_CONCERNS: one concern, the coupling bullet's quoted string (line 153; ruling 44) | read by both final-review halves |
| Final review A (Fable): `product-workflows` and its two rules files | an extract of `c3dfddb7` | 0 Critical, 3 Important, 8 Minor; six deferred items still to fix (line 157) | the wave (rulings 45 to 47) |
| Final review B (Fable): `workflows-core`, `dev-`, `docs-`, `security-workflows`, the security rules file, the rationale | an extract of `c3dfddb7` | 0 Critical, 1 Important, 5 Minor (line 161) | the wave (ruling 48) |
| Final review, records seat (Opus) | an extract of `e6b1df78` | Task 11's fix round: 11 addressed, 0 open. Then 0 Critical, 0 Important, 7 Minor (line 163) | the wave (ruling 49) |
| The wave's re-review, half 1 (`b31971b0`) | the wave | 11 addressed, 0 open; new: 0 Critical, 0 Important, 8 Minor (line 170) | the touch-up (ruling 50) |
| The wave's re-review, half 2 (`c6b5bd2f`, `2d805ec4`) | the wave | 14 addressed, 0 open; new: 0 Critical, 0 Important, 10 Minor (line 171) | the touch-up (ruling 50) |
| The narrow check of the touch-up | `7344fa9f` | 15 of 18 as written and true; the fixer's two changed sentences the true ones; one correction (line 175) | the controller's sentence `f52bf346` (line 176) |

The wave was one fixer's three commits on one list (`final-fix-wave.md`). The list on line 167 sums to 24 items: A's 3 Important and 8 Minor, B's 1 and 5, and the records seat's 7. The touch-up applied 18 sentences (line 174). Rulings 42 and 45 to 50 give each disposition.

## What departs from the design or the plan

The rulings file's *Departures from the process* gives each with its reason.

On the design's text, §5.4 and §5.5 are settled by the design's *Settled while building (batch 4)* note (DES:206 to :233). This close-out brought that note to the final tree in three places:
- its opening now says which rulings came with the plan, which of its pre-flight scan, of the tasks' reviews and of the final review;
- item (15) records the fetch before the fix wave, which found `origin/main` unmoved;
- item (20) records that `/document`'s and `/release-notes`' stops name no re-cut form, the final review's recorded difference.

On the plan's text:
- R6 was reversed and R16 withdrawn; R18 to R23 were added while building.
- R12 was built as P3, and superseded at the second merge.
- The plan's *Proposed versions* line (its line 95) keeps the planned numbers, and the plan carries no dated renumbering note; the numbers that shipped are those in *Versions* above.
- The plan's Task 12 says the rulings file carries *R1 to R15*; it carries R1 to R23.
- The plan's checkboxes are left unticked, as batch 3's were: `grep -c -- '- \[x\]'` gives 0 on both plans.

On the process:
- **The final review's halves ran on Fable.** Design §10 says *each batch gets an Opus review before its pull request*; the records seat ran on Opus.
- **One commit was read by no reviewer after it was applied**: the controller's sentence, `f52bf346`. Task 8's closing round, `cc8581c3`, had no scoped re-review — the controller read it narrowly — and the final review read it with the branch.

## What was not verified

- **No live run of any command was made.** Every state was walked against the text, never run. TT:268 opens the section *LADDER-ORDER batch 4 — `product-workflows` 3.85.0, `workflows-core` 1.98.0, `dev-workflows` 4.70.3, `docs-workflows` 1.43.1, `security-workflows` 0.12.7*.
  - It holds **16 live checks**: `awk '/^## LADDER-ORDER batch 4/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'` gives 17, at lines 272 to 288. The seventeenth, *What a miss looks like*, is a note on reading them, not a check.
  - The six new stops, the five *Review Focus* lines, the committed form of a register stop, R21, the design-grounding file, R23, and the register stop's one landing for a declined interview handoff.
  - Its intro, TT:270, says *no item below has been run* and *When they run is the maintainer's to choose (the design's §11.4), and is not chosen yet*. None has been run. Design §11.4 is therefore not yet met, and is the maintainer's.
- **Commits no scoped re-review read.**
  - `f52bf346`, the controller's sentence after the narrow check, was read by no reviewer at all. It was verified by its gates (line 176) and by the chain here.
  - `cc8581c3`, Task 8's closing round, was read narrowly by the controller (line 135).
  - Eight closing commits of reviewer-worded sentences each closed its task *without a further check*: `1285c6f9`, `305cf2ec`, `46e1e382`, `890e0dd0`, `c2c5fb20`, `a62b542d`, `05312e02` and `3b13ecc1` (rulings 15, 21, 27, 28, 33, 34, 35 and 41).
  - The final review read the whole branch at `c3dfddb7`, which holds every one of these but `f52bf346`.
- **The merges' semantic reading** is the merger's and the final review's, and was not repeated here (*The merges*).
- **Not re-derived here.**
  - The walks' verdicts, which were counted, not re-walked.
  - The population's per-row dispositions beyond the strings counted above.
  - The reviews' findings and their counts, which are the ledger's.
  - Every scratch test in the reports, and the implementers', the merger's and the fixer's chain runs.
  - The sizing of each version as minor or patch.
- **The page sentence the ledger left for the final review** (line 146) was not taken up by any seat, and stands. *A `prd.md` that exists and is not on the default branch stops the run*, on the `/create-ard` and `/specify` pages, presupposes a git specs tree. The rulings file lists it as open.
- **Not reviewed before commit.** These three records and the design note's three corrections were reviewed by no one before they were committed.

## Known limits

**From `product-workflows` 3.85.0's *Known limits that ship with this release*** (`plugins/product-workflows/CHANGELOG.md:32` to :38). The other four sections hold none.
- A refine on an emptied slice is refused (R3).
- A slice that claims nothing, its ledger deleted by hand, is named `/brd-split <PARENT-KEY>` by `/create-prd`, `/create-ard`, `/specify` and `/brd-reconcile`, and is not told by them that its ledger is missing (R6 as reversed). `/prd-ground`, `/brd-split` and `/brd-interview` report the file.
- `/brd-reconcile` names the `/brd-split <PARENT-KEY>` form in words and reads no parent ledger to choose it (R22).
- To re-author a slice's `prd.md`, landed or not, the operator types `/create-prd` and takes *Overwrite*: the route offers no `/create-prd` option beside a `prd.md` the slice holds (R21, R23).
- The placed-row line prints its two waits on any specs tree that is a git repository, one that can take no handoff included.

**Parked by ruling or by a review, none reached by an ordinary setup** — the rulings file's *Parked* list, with why:
- `/prd-ground`'s row F (b) tests no readability, so for a ledger in the folder, on no ref and unreadable, the run R18 names does not name the repair (ruling 16; DES item (25)).
- A `brd-link.md` with no `parent:` (ruling 18), and a hand-committed `brd-link.md` beside unlanded grounding (ruling 40).
- Four items the final review triaged as *still stands, no ordinary setup*, and three it found wording only, all older than the batch.
- The older text that says "outside its work tree" (ledger line 176).
- Three items a re-review noted with no ledger line, none filed in `docs/superpowers/to-fix.md`: two R1 (c) sites in `architecture-grounding.md` and `architecture-kb.md`, and the later-round `/brd-package` chain.

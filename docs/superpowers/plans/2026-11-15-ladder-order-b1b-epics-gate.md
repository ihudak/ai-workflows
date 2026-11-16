# LADDER-ORDER Batch 1b — `/epics`' PRD Gate and Two Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/epics` stops while the PRD it splits is not on the specs repository's default branch; the threat-model open-question line names a command that can run; `/update-spec` records a grounding file at the bytes it read.

**Architecture:** No new machinery. `/epics` runs the `require-on-main` gate it already runs for the PRD-level specification on `prd.md` too, with one new stop id for the gate's `absent` return, and loses the `prd_landed` note that stood in for a gate. `phase-handoff` §3.4 gains the row. The two fixes are sentence-level edits in `/create-ard` and `/update-spec`.

**Tech Stack:** Markdown prose that agents execute; `scripts/reference-parts.py` (generated entry files); the repository gates in `.github/workflows/validate-catalog.yml`.

**Spec:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md`, §5.6 (added 2026-11-15) with decisions M8, M9, M10 in §2. Every task's implementer reads §2, §4 and §5.6 of it first, and §5.1 for how batch 1 worded its stops. Below, PH is `plugins/workflows-core/references/phase-handoff.md`, EP is `plugins/product-workflows/commands/epics.md`, PP is `plugins/product-workflows/commands/prd-proposal.md`, ARD is `plugins/product-workflows/commands/create-ard.md`, UPS is `plugins/product-workflows/commands/update-spec.md`, NPO is `plugins/workflows-core/references/next-phase-offer.md`. Line numbers are at `main` `632e73d6`; find each site by its text.

## Global Constraints

### `/epics`: the states and the id

The gate runs on `<PRD folder>/prd.md`: the resolved folder on a PRD address, the folder above on an Epic address (the folder the run key set's step already names as the would-be `<PRD-KEY>`'s, EP:61–70), on either route.

| The gate returns | And | The run |
|---|---|---|
| any stopping row (D, E, the C rows, B′, G, I) | — | stops per PH §4.4, at once, before step 1b |
| `pass`, `pass_amending` | — | goes on to step 1b |
| `unmanaged` | — | goes on to step 1b, as today |
| `absent` | step 1b's table refuses the folder | stops as today (`EPICS_NO_PRD`, `EPICS_EPIC_NOT_UNDER_PRD`), with today's text |
| `absent` | step 1b's table accepts, HEAD does not hold `prd.md` | stops: `EPICS_PRD_NOT_HANDED_OFF`, uncommitted form |
| `absent` | step 1b's table accepts, HEAD holds `prd.md` | stops: `EPICS_PRD_NOT_HANDED_OFF`, committed form |

- **The id, spelled exactly:** `EPICS_PRD_NOT_HANDED_OFF`.
- **The model is `/prd-proposal`'s gate** (PP:186–300, its step 5): the same two forms, the same slot rules (`<new-branch>` under `prd/`, no-`origin` variant, read-only mount, commands on lines of their own with no `#` comment), the same HEAD test, `git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>" 2>/dev/null` with `<path>` relative to `$SPECS_PATH`. Word `/epics`' forms as PP's are worded, with *drafted nothing* where PP says *priced nothing*; do not invent a third wording. The committed form cites PH §4.4 row F's commands, as PP's does.
- **Every stop carries PH §4.4's four parts, in order:** what was found; what the run did not do; the exact commands; what happens if ignored.
- **The not-handed-off stop never names `/create-prd`** as the fix, and says why, as PP's does.
- **It is no plugin gap**, so it does not `emit-block`; say so beside it. It takes the command's *Ending early* tail (EP:24) like every other `EPICS_*` stop.
- **The Epic's own `epic.md` is not gated** on a re-refine run: it is the document the run revises.

### What must not change

- `EPICS_NO_PRD`, `EPICS_NOT_FOUND`, `EPICS_EPIC_NOT_UNDER_PRD`, `EPICS_PRD_NO_REQUIREMENTS`: their tests and texts, save a sentence that says `/epics` reads an unlanded PRD.
- `/epics` on a specs tree that is no git repository: byte-identical behaviour.
- `/epics`' Phase 2.6 gate on the PRD-level `specification.md`, and its `absent` skip.
- The deliberate order exception for `resolve-docs-grounding` in Phase 2 (EP:399): it now runs after the PRD gate and still ahead of Phase 2.5/2.6; reword only what the new gate makes false.
- `/create-ard`, `/specify`, `/update-spec`, `/prd-proposal`, `/prd-ground`: their PRD gates and stops, as batch 1 left them.
- `/update-prd` gates nothing (`.claude/rules/workflows-core-handoff.md`: *deliberately excluded*).
- `plugins/workflows-core/reference-parts/` is generated: edit the reference, then run `python3 scripts/reference-parts.py generate`. Never edit a file under it.

### The repository's own rules that bind every task

- `CLAUDE.md` § Editing discipline and `.claude/rules/claim-sweep.md`: M8 narrows what `/epics` runs on, so refinement 8 binds: every statement that `/epics` reads `prd.md` from the working tree, gates it nowhere, or drafts from an unmerged PRD is enumerated before the edit and re-read after it, with refinement 7's wrap-insensitive counts.
- `workflows-core:instruction-file-maintenance` binds edits to `CLAUDE.md`, `.claude/rules/` and the references.
- Budgets, measured with `LC_ALL=C.UTF-8 wc -m` (a bare `wc -m` counts bytes in this container): `CLAUDE.md` 35,972 against a 36,000 warning, so it takes no net growth; `.claude/rules/plugin-updates-coupling.md` 19,749 against 20,000; `.claude/rules/product-workflows.md` 17,026; `.claude/rules/docs-workflows.md` 19,986, so it takes none either; `.claude/rules/workflows-core-handoff.md` 5,802.
- PH §3.4's table is read by a gate and by a recipe: column 2 keeps each gated file in backticks (`scripts/check-docs.sh` check 11), and a stopping row's column 3 **begins** `**stops**` (the recipe in `.claude/rules/workflows-core-handoff.md`, which returns 11 today and 12 after Task 2).
- Read a file in an area with the Read tool before editing there: only that loads the area's rules file.
- Verify the branch before every commit: `git branch --show-current` prints `feat/ladder-order-b1b`. Never `git stash`. Work only in the worktree the dispatch names.
- The gates: every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain, reading the chain's own exit code. Each task that edits a plugin file ends with the chain at exit 0.
- No version, changelog or marketplace edit before Task 6.

## Review Focus

The five states most likely to be broken by a correct-looking edit. Each is pinned by a walk in the task named.

1. **A specs tree that is no git repository** (`unmanaged`): `/epics` must run exactly as today, with no stop and no leftover mention of landing. Task 3.
2. **A PRD on an unmerged `prd/` branch while the checkout stands on the default branch** (the folder on disk holds no `prd.md`): the gate's row D or E finding must be what stops the run, not `EPICS_NO_PRD` sending the operator to author a second PRD. Task 1 measures what happens today; Task 3 pins the new order.
3. **An Epic address (re-refine)**: the gate tests the parent's `prd.md`, never a `prd.md` path under the `EPIC-` folder, and never the `epic.md`. Task 3.
4. **A `prd.md` in the folder that does not assert `kind: prd`, on no ref**: step 1b refuses it as today; the run must not print *land it* for a file it would then refuse. Task 3.
5. **A grounding file whose working copy equals the default branch's** (the ordinary case) and **one the default branch lacks** (batch 1's guard): `/update-spec` must behave as it does today in both; only the differing copy changes. Task 5.

---

### Task 1: The sweep population and the measurements, before any edit

**Files:**
- Create: `docs/superpowers/plans/2026-11-15-ladder-order-b1b-sweep-population.md`

**Interfaces:**
- Produces: the population file every later task reads and updates: one row per statement, with an id (`P-n`), file and line, the sentence's opening words, a disposition (`rewrite` in Task 2, 3 or 4; `keep`, with why), and before-counts of each literal string to be changed. Later tasks add the after-counts.

- [ ] **Step 1: Enumerate by subject, not by wording** (refinement 6). The subject is *what `/epics` does with `prd.md`'s branch state*. Sweep refinement 4's scope (`plugins/` with every `CHANGELOG.md` read but not edited, the repo-root `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`) for at least: `prd_landed`; `landing sentence`; `Land <PRD-KEY>`; `never as a gate`; `gates it nowhere`; `from the working tree` near `epics`; `knowingly reads the worktree`; `offers only, never a gate`; every offer of `/product-workflows:epics <` in a `choices:` array or a next-step line of `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/update-spec`, the `/brd-*` commands and NPO; every sentence that lists the commands that stop on a PRD not on the default branch (they name `/create-ard` and `/specify` today and must now be read for whether `/epics` belongs: EP's own landing sentence, the `*_PRD_NOT_HANDED_OFF` stops' *Ignored, every /create-ard and /specify run …* sentences in ARD, SPEC, PP and `prd-ground.md`, `/create-prd`'s and `/update-prd`'s consent text, the docs pages); `eleven consumers`; the `/epics` line of the workflow map in `.claude/rules/product-workflows.md`; PH §5 rule 2's *`/epics` in its Phase 2.6*; PH §4's register row and consent wording for `prd.md`; the product-workflows docs pages (`docs/commands/epics.md`, `docs/workflow.md`, `docs/roles-and-phases.md`, `docs/brd-workflow.md`, `docs/getting-started.md`, `docs/commands/create-prd.md`, `docs/commands/update-prd.md`), `plugins/workflows-core/docs/family-map.md`, and any page in `dev-workflows`, `docs-workflows` or `security-workflows` that describes it. Then run refinement 3's exclusivity probe over the hits' paragraphs.
- [ ] **Step 2: Record the four measurements**, each from the text that runs it, with file and line:
  1. What `/epics <KEY>` does today where the PRD is on an unmerged `prd/` branch and the checkout is on the default branch (does the preflight move the checkout onto that branch — `workflows-core:specs-repo-git` §3.5 — or does step 1b refuse with `EPICS_NO_PRD`?).
  2. Whether `require-on-main` can return `pass_amending` for `prd.md` on an `/epics` run (row B needs a branch of the caller's own prefix, `epics/`, on which `prd.md` differs from the default branch's).
  3. What `scripts/check-docs.sh` check 11 does once PH §3.4 names `/epics` on `prd.md`: which `choices:` arrays naming `/product-workflows:epics` it then requires `<merge-clause>` of. Test it: add the row in a scratch copy of the tree under the session's scratchpad directory, run the check there, record the output, and leave the worktree untouched.
  4. PH §4's class for `prd.md` today and whether a new stopping row changes any consent array a producer presents (`/create-prd`, `/update-prd`).
- [ ] **Step 3: Commit** the population file alone: `docs: LADDER-ORDER batch 1b — the sweep population`.

### Task 2: `phase-handoff` and `next-phase-offer`

**Files:**
- Modify: `plugins/workflows-core/references/phase-handoff.md` (§3.4's table; the paragraph at PH:451; §5 rule 2 at PH:624; whatever Task 1's measurement 4 found in §4)
- Modify: `plugins/workflows-core/references/next-phase-offer.md` (NPO:205–206, NPO:326–330, and every `/epics` offer Task 1 dispositioned to this task)
- Modify: `.claude/rules/workflows-core-handoff.md` (the stopping-consumer sentence and count)
- Regenerate: `plugins/workflows-core/reference-parts/`

**Interfaces:**
- Consumes: the population file's rows dispositioned to Task 2.
- Produces: PH §3.4's row `/epics` | `prd.md`, which Task 3's command text cites by section, and the id `EPICS_PRD_NOT_HANDED_OFF` named in it.

- [ ] **Step 1: Run the recipe and record 11.** The command is in `.claude/rules/workflows-core-handoff.md`.
- [ ] **Step 2: Add the §3.4 row**, placed beside the `/prd-proposal` | `prd.md` row it mirrors. Column 3 begins `**stops**`, splits row F on step 1b's table (refused: never produced, `EPICS_NO_PRD`; accepted and on no ref: `EPICS_PRD_NOT_HANDED_OFF`, landing the file already on disk and never re-running `/create-prd`), says `unmanaged` leaves the folder's own file to decide, and declares the behaviour change with its date, 2026-11-15, as the `/create-ard` and `/specify` rows declare theirs: before it, `/epics` read the working copy and gated it nowhere. Keep the existing `/epics` | PRD-level `specification.md` row as it is.
- [ ] **Step 3: PH:451.** Remove `/epics` on `prd.md` from the examples of a command that knowingly reads the worktree. The rule and its two other examples stand; add one clause saying `/epics` was such a reader until the 2026-11-15 decision gated it. Re-read the whole paragraph against the moved premise (`CLAUDE.md`, sentence-context bullet).
- [ ] **Step 4: §5 rule 2.** `/epics` runs a gate in its Phase 0 now, and its Phase 2.6 gate stays where it is: word both.
- [ ] **Step 5: NPO.** `/create-prd`'s and `/update-prd`'s offers of `/product-workflows:epics <PRD>` carry `<merge-clause>` and say why (it gates this PRD), as the neighbouring `/create-ard` and `/specify` clauses do; NPO:326–330's sentence is rewritten to what is true after Task 3 (past its gate the PRD is landed, so the Epic offers carry no landing note of the PRD); re-read the *`/epics` precondition* part (NPO:341–352) and change only what is false.
- [ ] **Step 6: The rules file.** `.claude/rules/workflows-core-handoff.md`: twelve consumers, `/epics` named with what it stops on and the decision's date, the why-link kept. Count the result with the recipe.
- [ ] **Step 7: Regenerate and verify.** `python3 scripts/reference-parts.py generate`; the recipe prints 12; the gate chain exits 0. If check 11 now fails on arrays in command files, that is Task 4's work: record each failing site in the population file as a Task 4 row and report DONE_WITH_CONCERNS naming them; do not edit a command file here.
- [ ] **Step 8: After-counts** into the population file for every string this task changed. Commit: `feat(workflows-core): /epics' prd.md row in phase-handoff §3.4 — it stops (LADDER-ORDER batch 1b)`.

### Task 3: `/epics`

**Files:**
- Modify: `plugins/product-workflows/commands/epics.md`
- Modify: `plugins/product-workflows/docs/commands/epics.md`

**Interfaces:**
- Consumes: PH §3.4's `/epics` row and the id from Task 2; PP:186–300 as the wording model.
- Produces: `EPICS_PRD_NOT_HANDED_OFF` in its two forms; the section title **Gate the PRD.** in Phase 0, which Task 4's statements cite.

- [ ] **Step 1: Write the walk table first**, in the population file under `## Task 3 walks`: one row per state of Global Constraints' table, times {PRD address, Epic address}, times {idea-route folder, slice}, plus Review Focus 1 to 4, each with the expected stop or continuation. This is the test the edit must pass.
- [ ] **Step 2: Add the gate to Phase 0**, after the preflight and step 1a, before step 1b: execute `require-on-main` (`Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`, §3) against the PRD folder's `prd.md`; map its §3.7 return by `stopped` first; a stopping state stops per §4.4 there; carry any other return to step 1b.
- [ ] **Step 3: Add the `absent` branch after step 1b's table accepts** (and before the requirements test, so a run prints one stop): the HEAD test, the two forms of `EPICS_PRD_NOT_HANDED_OFF` in fenced blocks, their slot rules, and the no-`emit-block` sentence. On an Epic address `<PRD>` and `<path>` are the parent folder's.
- [ ] **Step 4: Remove what the gate replaces.** The *Note whether the PRD is landed* paragraph (EP:296–312), `prd_landed`, and the landing sentence at every use: EP:421, EP:493, EP:1082, EP:1148, EP:1154, EP:1269, and any other Task 1 found. Each sentence that named the unlanded PRD as its reason keeps what is still true of it and loses the rest; where Task 1's measurement 2 found `pass_amending` reachable, say what the offers print there.
- [ ] **Step 5: Re-read the phases the change touches end to end** (refinement 2): Phase 0 whole, the *Ending early* paragraph (add the stop to its list where the list is by id or by kind), Phase 2's order paragraph (EP:399), Phase 2.6, Phase 2.7, Phase 7.5's `body_facts` sentences about `/specify <EPIC>`, Phase 9's report template, and the Invariants. Fix each sentence the gate makes false; add an invariant line for the gate in the Invariants' own style.
- [ ] **Step 6: The docs page.** Derive from the command as edited (`CLAUDE.md`, docs-tree constraint): the gate in its Phase 0 description and flow diagram, the stop in its stops list, and no sentence left that says it reads an unmerged PRD. Quote any mermaid label holding `[ ] ( ) { } |` or `#`.
- [ ] **Step 7: Walk every row of Step 1's table** against the edited text, recording `Matches` or the defect, and fix defects. Then the gate chain exits 0.
- [ ] **Step 8: After-counts**, then commit: `feat(product-workflows): /epics stops while its PRD is not on the default branch (LADDER-ORDER batch 1b)`.

### Task 4: The statements and offers elsewhere

**Files:**
- Modify: every file the population file dispositions `rewrite` to this task. Expected at least: `plugins/product-workflows/commands/create-prd.md`, `update-prd.md`, `create-ard.md`, `specify.md`, `prd-proposal.md`, `prd-ground.md` (the *Ignored, every … run* sentences, where `/epics` now belongs in the list); `plugins/product-workflows/docs/**`; `plugins/workflows-core/docs/family-map.md`; `.claude/rules/product-workflows.md` (the `/epics` map line); `docs/maintainers/rationale.md` (`## ladder-order`, one paragraph for M8).

**Interfaces:**
- Consumes: Task 3's section title and stop id; Task 2's `<merge-clause>` wording in NPO.

- [ ] **Step 1: Offers.** Every offer of `/product-workflows:epics <PRD>` by a run that wrote or edited `prd.md` names the merge, by `<merge-clause>` where the offer is one the convention binds (NPO's *Where this rule applies*) and in the offer's own words elsewhere. An offer by a run that passed the PRD gate itself (`/create-ard`, `/specify`) is read and left where it is already true.
- [ ] **Step 2: Lists of what stops on an unlanded PRD.** Each sentence saying which runs stop on the folder until `prd.md` is on the default branch names `/epics` too where it enumerates commands; keep one wording across the copies (refinement 8).
- [ ] **Step 3: Pages and rules.** Rewrite each remaining row. The map line in `.claude/rules/product-workflows.md` opens with the gate in the map's own notation, as `/prd-proposal`'s line does (`[require-on-main: prd.md]`), and loses *offers only, never a gate*. `CLAUDE.md` takes no edit unless a sentence in it is false; if one is, the edit is net-zero in characters or the task stops and reports.
- [ ] **Step 4: Rationale.** One paragraph under `## ladder-order` in `docs/maintainers/rationale.md`: the question as first put, its correction, the decision and its accepted cost, with the date.
- [ ] **Step 5: Verify.** After-counts for every changed string; every population row has a final disposition; the gate chain exits 0; the budgets in Global Constraints re-measured and recorded.
- [ ] **Step 6: Commit:** `docs: LADDER-ORDER batch 1b — the offers and statements that follow /epics' gate`.

### Task 5: The two fixes

**Files:**
- Modify: `plugins/product-workflows/commands/create-ard.md` (Phase 4.3 step 8 at ARD:904; Phase 5's and Phase 6 step 2's references to that line, ARD:979 among them)
- Modify: `plugins/product-workflows/docs/commands/create-ard.md` (:143)
- Modify: `plugins/product-workflows/commands/update-spec.md` (Phase 0 step 7 at UPS:59; Phase 1 at UPS:68; Phase 2's *Upstream* at UPS:81; Phase 3 at UPS:94; Phase 6's stamps at UPS:137; the Final report at UPS:198)
- Modify: `plugins/product-workflows/docs/commands/update-spec.md`
- Modify: `plugins/workflows-core/references/document-lineage.md` (§1's clause on what `/update-spec` leaves out, and §5 step 1 only if its `--from-ref` sentence is made false), then regenerate `reference-parts/` if that reference has generated parts

**Interfaces:**
- Consumes: nothing from Tasks 2 to 4.

- [ ] **Step 1: The threat-model line (design §5.6, M9).** Confirm first, from `plugins/product-workflows/commands/update-prd.md`'s Phase 0, that `/update-prd` stops on a folder holding no `prd.md` (`UPDATE_PRD_NO_PRD`), and from ARD's *Gate the PRD* that a slice is the one PRD folder reaching Phase 4.3 without one. Then: the line ends `through /product-workflows:create-prd` where the PRD folder (the folder above the Epic, on an Epic-level run) holds no `prd.md` when the line is written, and `through /product-workflows:update-prd` otherwise. The once-per-threat match reads the lead alone and is unchanged; say that a line an earlier run wrote keeps its ending. Sweep ARD, `plugins/product-workflows/agents/threat-modeler.md`, `agents/ard-reviewer.md`, `plugins/workflows-core/references/threat-model-format.md` and the docs page for every statement of the line (Read `.claude/rules/threat-model.md`'s area first), with before and after counts of `through /product-workflows:update-prd`.
- [ ] **Step 2: Walk the line** for: an idea-route PRD-level run; an Epic-level run; a slice holding a `prd.md`; a slice holding none; a re-run that finds an earlier line. Record the walk in the population file under `## Task 5 walks`.
- [ ] **Step 3: `/update-spec` (design §5.6, M10).** Define the state once, in Phase 2's *Upstream* entry beside batch 1's guard: a grounding file `<default-ref>` holds whose working copy differs, by `git -C "$SPECS_PATH" hash-object -- "./<path>"` against `git -C "$SPECS_PATH" rev-parse "<default-ref>:./<path>"`. For such a file: Phase 1's confirmation names it and says the run reads `<default>`'s copy and that what the working copy adds waits until it lands; Phase 2 diffs as today; Phase 3 reads its findings with `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`; step 7 captures it `--from-ref` in the same `capture` call; Phase 6 stamps the working copy's finding of the same id and names in the Final report each finding the working copy no longer holds, which takes no stamp. Test the two git commands and a `lineage.py capture` mixing `--from-ref` and `--from-disk` in a scratch repository under the session's scratchpad directory, and record the transcript in the task report.
- [ ] **Step 4: Walk it** for: the working copy equal to the default branch's; differing by a re-ground; differing by `consumed_by` stamps alone; a grounding file the default branch lacks (batch 1's guard, unchanged); no grounding file; a null baseline; a legacy `inputs_at` baseline. Record the walk. Then show, in the walk, the next run after the differing copy lands: its diff runs from the recorded blob and proposes the change.
- [ ] **Step 5: The pages and the reference.** `docs/commands/update-spec.md` and `docs/commands/create-ard.md` derived from the commands as edited; `document-lineage` §1's clause extended to name the third case (`--from-ref` for a grounding file whose working copy differs). Regenerate parts if needed.
- [ ] **Step 6: Gate chain exits 0. Commit** as two commits: `fix(product-workflows): the threat model's requirement-gap line names /create-prd where the slice holds no PRD`, and `fix(product-workflows): /update-spec reads and records a grounding file at the default branch's copy where the working copy differs`.

### Task 6: Merge `main`, then release

**Files:**
- Modify: `plugins/product-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, each changed plugin's `CHANGELOG.md`
- Modify: `.claude/rules/plugin-updates-coupling.md`, `.claude/rules/plugin-updates-coupling-history-3.md`, and the three places that state the split's ranges (`CLAUDE.md`'s rules table, `.claude/rules/plugin-updates.md`, each coupling file's header)
- Modify: `docs/superpowers/to-test-on-real-project.md`, `docs/superpowers/to-fix.md` (the LADDER-ORDER entry)

- [ ] **Step 1: Merge first.** `git fetch origin`, then `git log --oneline HEAD..origin/main`. If it prints anything, merge `origin/main` into the branch, resolve, and re-walk any file both sides changed (EP, ARD, UPS, PH, NPO): a conflict resolution is not a re-walk. Run the gate chain.
- [ ] **Step 2: Versions, from the merged tree.** Read each `plugin.json` as it stands after the merge. `product-workflows` takes a minor bump (a new stop on a run that went on) and `workflows-core` a minor bump (§3.4's row). Any other plugin whose files this branch changed (`git diff --stat origin/main...HEAD -- plugins/`) takes a patch bump. `marketplace.json` agrees with each `plugin.json`; do not reformat it.
- [ ] **Step 3: Changelogs**, dated 2026-11-15 (no `— Unreleased` section reaches `main`): for `product-workflows`, **Changed** (`/epics` stops, with the id, the two forms and the behaviour change stated as a user meets it) and **Fixed** (the threat-model line; `/update-spec`'s grounding record); for `workflows-core`, the §3.4 row, NPO and `document-lineage` §1.
- [ ] **Step 4: The coupling bullet and its room.** Read all four coupling files first (`.claude/rules/plugin-updates.md` requires it). Write the bullet `Update workflows-core <new> with product-workflows <new>`, saying what breaks with one side older, in the file's own form. Measure with `LC_ALL=C.UTF-8 wc -m`. If `plugin-updates-coupling.md` would exceed 20,000, move its oldest bullets, whole and unchanged, to the end of `plugin-updates-coupling-history-3.md` (17,141 today) until it fits with at least 600 characters spare, and correct every statement of the two files' version ranges: each file's header, `CLAUDE.md`'s rules table (same-length replacement, so no net growth) and `.claude/rules/plugin-updates.md`'s bullet. Count the bullets before and after across both files: none lost, none duplicated.
- [ ] **Step 5: Live checks.** Add to `docs/superpowers/to-test-on-real-project.md`, under a dated heading for this batch: `/epics` on an uncommitted PRD; on a PRD whose pull request is open; on an Epic address under each; on a specs directory that is no git repository; the threat-model line on a slice with no PRD; `/update-spec` with a re-ground left uncommitted. Mark them not run.
- [ ] **Step 6: The to-fix entry.** The LADDER-ORDER entry says batch 1b is built, with what it added, and that batches 2 to 4 are open.
- [ ] **Step 7: Verify.** The gate chain exits 0; then `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` exits 0; `python3 scripts/validate-catalog.py` prints no new warning; the budgets re-measured. Commit: `release: product-workflows <new>, workflows-core <new> — /epics' PRD gate (LADDER-ORDER batch 1b)`.

### Task 7: Close

**Files:**
- Create: `docs/superpowers/verification/2026-11-15-ladder-order-b1b.md`, `-rulings.md`, `-ledger.md`

- [ ] **Step 1 (controller, after the final review's fix wave, never before it):** the verification record, every expected value re-derived against the tree being verified: the recipe's 12; the after-counts; the walks' results; the budgets; the gate chain's exit code; what was not run (the live checks).
- [ ] **Step 2:** the rulings summary and the verbatim ledger, committed before the workspace is removed.
- [ ] **Step 3:** push, open the pull request, merge when CI is green, remove the worktree and the branch.

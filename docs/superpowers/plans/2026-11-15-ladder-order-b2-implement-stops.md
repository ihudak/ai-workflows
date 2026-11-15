# LADDER-ORDER Batch 2 — a Keyed `/implement` Needs Its Specification and Design Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A keyed `/dev-workflows:implement` run stops where the unit it builds has no `specification.md` or no `design.md` on the specs repository's default branch, naming what the earliest missing document needs; a direct run (no key) is untouched.

**Architecture:** No new machinery. `/implement` already runs `require-on-main` on the specification and design it finds; it now tests the expected pair whether or not each file is on disk, and its `absent` branch becomes four stops in place of a question. `phase-handoff` §3.4's `/implement` row flips to *stops*, which moves `design.md` from a falling-back artifact to a stopping one. The rule for what a never-produced stop names (the earliest gap) is stated once, in `phase-handoff`, and cited by every stop that uses it. The commands that offer or name `/implement`, and the offers batches 1 and 1b left owed to this batch, follow.

**Tech Stack:** Markdown prose that agents execute; `scripts/reference-parts.py` (generated entry files); `plugins/workflows-core/scripts/weakness-classes.py` and its selftest, if its next-step sentence changes; the repository gates in `.github/workflows/validate-catalog.yml`.

**Spec:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md` — §2 (M1–M3, L6–L12), §4, §5.2, and §5.5's **Batch 2** list (the sites batches 1 and 1b found and left to this batch). Every task's implementer reads those first, and §5.1 and §5.6 for how the earlier batches worded their stops. Below, PH is `plugins/workflows-core/references/phase-handoff.md`, IMPL is `plugins/dev-workflows/commands/implement.md`, DES is `plugins/dev-workflows/commands/design.md`, CONF is `plugins/dev-workflows/commands/conformance.md`, SCAN is `plugins/security-workflows/commands/scan.md`, NPO is `plugins/workflows-core/references/next-phase-offer.md`, COMP is `plugins/workflows-core/references/components.md`. The design's line numbers (IMPL:316 and the like) are from before three later merges: find every site by its text. Line numbers in this plan are at `main` `aeedacf0`.

## Global Constraints

### The unit, the pair, the states and the ids

The **unit** is the folder a keyed run resolved its `specs` from: an Epic's folder, or the PRD folder for a broad PRD-level slice. The **pair** is that folder's own `specification.md` and `design.md`. Each file of the pair is tested on every keyed run — a first run, a later run for the same unit, a companion run and a tasks-only run alike — whether or not it is on disk:

| For one file of the pair, the gate returns | And | The run |
|---|---|---|
| any stopping row (D, E, the C rows, B′, G, I) | — | stops per PH §4.4, as today |
| `pass`, `pass_amending` | — | goes on, as today |
| `absent` | the file is in the unit's folder, HEAD does not hold it | stops: `IMPLEMENT_SPEC_NOT_HANDED_OFF` / `IMPLEMENT_DESIGN_NOT_HANDED_OFF`, uncommitted form |
| `absent` | the file is in the unit's folder, HEAD holds it | the same id, committed form |
| `absent` | the file is not in the unit's folder | stops: `IMPLEMENT_NEEDS_SPEC` / `IMPLEMENT_NEEDS_DESIGN` |
| `unmanaged` | the file is in the unit's folder | goes on, as today (design L7) |
| `unmanaged` | the file is not in the unit's folder | stops: `IMPLEMENT_NEEDS_SPEC` / `IMPLEMENT_NEEDS_DESIGN`, in a form that names no handoff or merge |

- **Ids, spelled exactly:** `IMPLEMENT_NEEDS_SPEC`, `IMPLEMENT_SPEC_NOT_HANDED_OFF`, `IMPLEMENT_NEEDS_DESIGN`, `IMPLEMENT_DESIGN_NOT_HANDED_OFF`.
- **One stop per run.** The specification is tested first; where it stops, the design is not reported. Where both are missing the run stops once, on the specification.
- **The earliest gap (design L12)** — what a never-produced stop names. The order is `prd.md`, then `specification.md`, then `design.md`, each read by its state. For `IMPLEMENT_NEEDS_SPEC`: on the idea route a `prd.md` that is nowhere names `/product-workflows:create-prd <PRD>`; on either route a `prd.md` in the PRD folder and not on the default branch names its landing; otherwise `/product-workflows:specify <UNIT>`. For `IMPLEMENT_NEEDS_DESIGN` (the specification is on the default branch): `/dev-workflows:design <UNIT>`. The rule is stated ONCE, in PH §4.4, under the name *the earliest gap*, and every stop that uses it cites it. A stop never names a run that would itself stop on arrival for the folder in hand (L8): where the named command opens with a picker or an override question on a multi-component PRD, the builder reads what it does on arrival and names the one that goes on.
- **Every never-produced stop names the direct run as a way out**, beside the producing command: a change too small to specify and design is made with no key (`/dev-workflows:implement <description>`).
- **The not-handed-off forms** are worded as batch 1's are (`SPECIFY_PRD_NOT_HANDED_OFF` in `plugins/product-workflows/commands/specify.md`; `EPICS_PRD_NOT_HANDED_OFF` in `commands/epics.md`): the HEAD test `git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>" 2>/dev/null`; the uncommitted form's commands with `<new-branch>` under the file's own prefix (`spec/`, `design/`); the committed form citing PH §4.4 row F's commands; the no-`origin` and read-only-mount variants; commands on lines of their own with no `#` comment. A not-handed-off stop never names `/specify` or `/design` as the fix.
- **Every stop carries PH §4.4's four parts, in order**, takes the command's *Ending early* tail, and does not `emit-block`.
- **A direct run** (no key) resolves no unit and is byte-identical in behaviour.

### What must not change

- A direct `/implement <description>` run, in every phase.
- Rows D and E, the C rows, B′, G, I for the pair, as `/implement` maps them today.
- An `@path` spec-folder token on a keyed run still adds its files to `specs` as context, gated as today; it does not stand in for the unit's own pair.
- `/ready`: it reports and never stops. `/epics`' and `/ready`'s scopes of `multi-component-prereqs`.
- `/design`'s own gate on `specification.md` and its stops' tests; only what its stops and offers NAME changes (§5.5).
- On a multi-component PRD, taking the flat pair whole stays a question with *Split* recommended, never an auto-selection.
- A resumed run that is already past its first edit is never stopped by a document removed since (design §5.2).
- `plugins/workflows-core/reference-parts/` is generated: edit the reference, then `python3 scripts/reference-parts.py generate`.
- The BRD route's ledger tests are batch 4's: on a slice, the earliest gap's last rung names `/product-workflows:specify <UNIT>` here.

### The repository's own rules that bind every task

- `CLAUDE.md` § Editing discipline and `.claude/rules/claim-sweep.md`: this narrows what a keyed `/implement` runs on, so refinement 8 binds: every statement that `/implement` goes on without a specification or a design, asks about missing specs, or falls back, is enumerated before the edit and re-read after it, with refinement 7's wrap-insensitive counts.
- `workflows-core:instruction-file-maintenance` binds edits to `CLAUDE.md`, `.claude/rules/` and the references.
- **Budgets**, measured with `LC_ALL=C.UTF-8 wc -m` (a bare `wc -m` counts bytes in this container): `CLAUDE.md` 35,898 against a 36,000 warning — no net growth; `.claude/rules/dev-workflows-implement.md` **19,991** against 20,000 — no net growth: an edit there replaces a sentence the batch makes false with one no longer, and any new invariant goes to `.claude/rules/dev-workflows-conformance.md` (6,326; it loads with the same `paths:`), under a heading that says what it holds; `.claude/rules/dev-workflows.md` 19,142; `.claude/rules/security-workflows.md` 19,435; `.claude/rules/workflows-core-handoff.md` 6,234; `.claude/rules/plugin-updates-coupling.md` 14,396.
- PH §3.4's table is read by a gate and by a recipe: column 2 keeps each gated file in backticks (`scripts/check-docs.sh` check 11), and a stopping row's column 3 **begins** `**stops**` (the recipe in `.claude/rules/workflows-core-handoff.md`, which returns 12 today and 13 after Task 2).
- `/implement` keeps a run-state file (`scripts/run-state.py`) and a resume protocol; a change to what Phase 0 carries is checked against both, and against `scripts/run-state.py`'s own key set and selftest.
- Read a file in an area with the Read tool before editing there: only that loads the area's rules file.
- Verify the branch before every commit: `git branch --show-current` prints `feat/ladder-order-b2`. Never `git stash`. Work only in the worktree the dispatch names; each agent keeps scratch files in a subdirectory of its own under the session scratchpad and deletes nothing outside it.
- The gates: every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain, reading the chain's own exit code. Each task that edits a plugin file ends with the chain at exit 0.
- No version, changelog or marketplace edit before the release task.

### Settled after Task 1's measurements (2026-11-15) — these bind, and win over the task text where they differ

- **The rule's name.** `workflows-core:components` §6 already calls its `multi-component-prereqs` ladder *the earliest gap*, and `/implement` and `/epics` cite it by that name. PH §4.4's new rule is therefore named ***the first missing document***. Wherever this plan says *PH §4.4's earliest gap*, read that name; COMP's name and rule are not changed.
- **A pre-rename PRD file.** The rule's `prd.md` rung reads the file's state as batch 1's stops do: nowhere, and no pre-rename PRD file in the PRD folder → `/product-workflows:create-prd <PRD>`; nowhere, with a pre-rename file (batch 1's test: a top-level `.md` file whose name is the resolved key followed by `_`, other than `<KEY>_ARD.md`) → the rename, never a second PRD: the stop says the PRD is under its old file name and names `/product-workflows:specify <UNIT>` as the run whose own stop prints the rename's commands, saying that it stops.
- **A resumed run.** Before its first edit (the test the command already has for that), a resume tests the expected pair as a first run does, and its stop says the run can be resumed once the document is on the default branch, or started fresh. Past its first edit, a resume gates the paths the earlier run recorded, with the mapping that run had: a file of the pair that is absent, or that a run started before this batch never recorded, does not stop it, and the Phase 5 report names it.
- **A PRD with no Epic folder.** The pair on the default branch: the question is asked as today, and never skipped on a multi-component PRD. No specification: `IMPLEMENT_NEEDS_SPEC`, naming `/product-workflows:specify <PRD>` (single- and multi-component alike; by the rule above where the PRD itself is the gap). A specification and no design: `IMPLEMENT_NEEDS_DESIGN`, naming `/dev-workflows:design <PRD>` on a single-component PRD; on a multi-component one, naming `/product-workflows:epics <PRD>` — the split the family recommends there — and saying that designing the PRD whole is `/dev-workflows:design <PRD>` answered *Design across anyway*; where `/epics` would itself stop for that folder (no `prd.md` asserting `kind: prd`, as on a slice with none), it names `/dev-workflows:design <PRD>` alone.
- **`/implement <PRD>` with Epics, none of them and no slice holding its pair.** The prose that lists each left-out Epic with the command it needs is printed as it would be above a picker; the stop's id is that of the first listed Epic's gap, and its one command is that Epic's.
- **`/conformance <PRD>` (L9).** The new stop covers a PRD in which no unit holds an implementation block, and nothing else; a partly built PRD is traced as today.
- **`/security-workflows:scan`.** Its PRD test (the one that decides whether a `--prd-key` is passed to `weakness-classes.py`) reads `prd.md` on the default branch — in the folder, on a specs tree that is no git repository — in place of the working tree; the script, its selftest and `security-register-format` §7 are not changed. The builder confirms that the sentence printed where no key is passed is true of a PRD written and not landed, and reports if it is not.
- **Three sites join Task 5:** `plugins/dev-workflows/commands/ready.md`'s offer of `/dev-workflows:implement` on a `SUPPORTED` verdict (conditional on the unit's pair being on the default branch, which `/ready`'s own gate has already read); `CONFORMANCE_BRANCH_MISSING` and `SECURITY_BRANCH_MISSING`, which name `/dev-workflows:implement <KEY>` and gain one clause saying that run needs the unit's specification and design on the default branch; and `plugins/product-workflows/commands/specify.md`'s restatement of `/design`'s multi-component stop, with `next-phase-offer`'s copy of it. `/implement`'s Phase 5 *Next step* line on the remaining Epics is Task 4's.

## Review Focus

The five states most likely to be broken by a correct-looking edit. Each is pinned by a walk in the task named.

1. **A direct run** (`/implement fix the typo in the README`): nothing new is tested, asked or printed. Task 3.
2. **A later run for a unit built before this batch with a specification and no design** (a follow-up, a security-finding fix on the Epic's open branch): it stops, as M3 decided — and the stop must say so plainly and name the direct run, since the operator did nothing wrong today. Task 3.
3. **A specs tree that is no git repository**: the folder's own files decide; present, the run goes on; absent, the never-produced stop names no handoff or merge. Task 3.
4. **`/implement <PRD>` where some Epics have the pair and some do not**: the picker lists only those that have it, counts and names the others with the command each needs, never auto-selects on a multi-component PRD, and stops with one id where none is left. Task 4.
5. **A resumed run** whose `design.md` was removed or left unmerged after the run started: the builder states whether Phase 0 reaches the gate again on a resume, and a run past its first edit is not stopped. Task 3.

---

### Task 1: The sweep population and the measurements, before any edit

**Files:**
- Create: `docs/superpowers/plans/2026-11-15-ladder-order-b2-sweep-population.md`

**Interfaces:**
- Produces: the population file every later task reads and updates (rows with ids `P-n`, file and line, opening words, disposition — `rewrite` in a named task, `keep` with why, `later 3`/`later 4` — and before-counts of each literal string to be changed), in the form of `docs/superpowers/plans/2026-11-15-ladder-order-b1b-sweep-population.md`.

- [ ] **Step 1: Enumerate by subject** (refinement 6): *what a keyed `/implement` does where the unit's specification or design is missing or not on the default branch*, and *who names or offers `/dev-workflows:implement <KEY>`*. Sweep refinement 4's scope for at least: `Proceed without specs`; `Point me at a specs directory`; `in-scope spec`; `falls back` / `falling back` near `design.md` or `/implement`; `no consumer of design.md stops`; `one hard exception`; `one exception` near `/design`; `an absent one` near `/implement`; `epic_spec`; `epic_design`; `Implement one broad PRD-level slice anyway`; the ○ ◐ ● picker markers; `CONFORMANCE_NOT_IMPLEMENTED`; every offer or next-step line naming `/dev-workflows:implement <` in `/design`, `/ready`, `/conformance`, `/security-workflows:scan`, `/document`, `/release-notes`, the product-workflows commands, NPO and `workflows-core:workflow-states` or its `dev-workflows` copy; PH §3.4's `/implement` row and every sentence that describes it; PH §4's class and consent wording for `design.md` and `specification.md`; the `/implement` lines of the workflow maps in `.claude/rules/dev-workflows*.md` and their invariants; the docs pages of all five plugins; `docs/maintainers/rationale.md`. Take every site in design §5.5's **Batch 2** list as a row, re-located at this base. Then run refinement 3's exclusivity probe over the hits' paragraphs.
- [ ] **Step 2: Record these measurements**, each from the text that runs it, with file and line:
  1. How a keyed run builds `specs` today (IMPL Phase 0): which step finds the unit's files, where the specs question is asked, where the gate runs, and what a companion run and a tasks-only run carry. Which later phases read `specs` or branch on its being empty (list every one).
  2. PH §4: the class of `design.md` and of `specification.md` today, which producers present which consent array because of it (`/design`, `/specify`, `/update-spec`, `/implement`'s Phase 4.5), and what changes when `/implement`'s row stops on both. Run `scripts/check-docs.sh` check 11 in a scratch copy with the row flipped and record what it then requires.
  3. The resume path: whether a resumed run executes the in-scope specs gate again (IMPL's resume list item on the gate, about IMPL:94), on what, and what a stop there would do to a run past its first edit.
  4. `/implement <PRD>`: the picker's rows and markers, the 0-Epic and multi-component branches, the broad-slice option, and `multi-component-prereqs` at `implement` scope (COMP §6) — which of its rows can still be reached with a gap once Phase 0 stops.
  5. What each command the earliest-gap rule can name does on arrival for the folder in hand: `/product-workflows:create-prd <PRD>`, `/product-workflows:specify <UNIT>` (PRD-level, Epic-level, multi-component PRD), `/dev-workflows:design <UNIT>` (same three). Where one opens with a picker or an override question, say so.
  6. `/conformance <PRD>` where no unit holds an implementation block (design L9): trace it and say whether it runs on.
  7. SCAN's `### Next step` lines and `plugins/workflows-core/scripts/weakness-classes.py`'s `pa_next_step` sentence: where each is built, what test each rests on, and what the script's selftest pins.
  8. `scripts/run-state.py`: the keys Phase 0 writes, and whether any names the specs question's answer or an empty `specs`.
- [ ] **Step 3: Commit** the population file alone: `docs: LADDER-ORDER batch 2 — the sweep population`.

### Task 2: `phase-handoff`, `next-phase-offer`, and the earliest-gap rule

**Files:**
- Modify: `plugins/workflows-core/references/phase-handoff.md` (§3.4's `/implement` row and the paragraphs that describe the table; §4's class of `design.md` and every sentence that rests on *no consumer of `design.md` stops*; §4.4, the earliest-gap rule)
- Modify: `plugins/workflows-core/references/next-phase-offer.md` (the Dev lane and every offer of `/dev-workflows:implement` Task 1 dispositioned here)
- Modify: `.claude/rules/workflows-core-handoff.md` (the stopping-consumer sentence and count)
- Regenerate: `plugins/workflows-core/reference-parts/`

**Interfaces:**
- Consumes: the population file's rows dispositioned to Task 2, and Task 1's measurement 2.
- Produces: PH §3.4's `/implement` row with the four ids; PH §4.4's paragraph named *the earliest gap*, which Tasks 3 to 5 cite by that name.

- [ ] **Step 1: Run the recipe and record 12.**
- [ ] **Step 2: The §3.4 row.** `/implement` | `specification.md` / `design.md`: column 3 begins `**stops**`; says a keyed run tests the unit's own pair whether or not each is on disk, splits row F on whether the file is in the unit's folder (not there: `IMPLEMENT_NEEDS_SPEC` / `IMPLEMENT_NEEDS_DESIGN`; there and on no ref: the `*_NOT_HANDED_OFF` id, landing the file and never re-running its producer), that `unmanaged` leaves the folder's own file to decide, that a direct run resolves none, and declares the behaviour change with its date as the `/create-ard`, `/specify` and `/epics` rows declare theirs: before it, a keyed run with no specification or design asked and could go on. Keep column 2's backticked files.
- [ ] **Step 3: §4.** With `/implement` stopping on `design.md`, no row naming `design.md` preserves an absent behaviour: move it from the falling-back class to the stopping one wherever §4 lists or reasons from it, and re-read every producer sentence that rests on the old class (Task 1's measurement 2). Do the same check for `specification.md`.
- [ ] **Step 4: §4.4, the earliest gap.** One paragraph: a stop on a document never produced names what the earliest document not on the default branch needs, in the order `prd.md`, `specification.md`, `design.md`, each read by its state (nowhere: its producing command; in its folder and on no ref, or on an unmerged branch: its landing), and never a run that stops on arrival for the folder in hand. Say which stops use it today (batch 1's `*_NEEDS_PRD` name `/create-prd` by the decision recorded in design §5.5; this batch's use it in full). Word it so a caller can cite it and apply it without re-deriving it.
- [ ] **Step 5: NPO.** Each offer of `/dev-workflows:implement <KEY>` says what is true after Task 3: it stops where the unit's specification or design is not on the default branch, so an offer by a run that has just written one of them carries `<merge-clause>`, and an offer by a run that knows one is missing names what the earliest gap needs instead.
- [ ] **Step 6: The rules file.** Thirteen consumers, `/implement` named with what it stops on and the decision's date. Count the result with the recipe.
- [ ] **Step 7: Regenerate and verify.** `python3 scripts/reference-parts.py generate`; the recipe prints 13; the gate chain exits 0.
- [ ] **Step 8: After-counts**, then commit: `feat(workflows-core): /implement's row in phase-handoff §3.4 stops, and §4.4 names the earliest gap (LADDER-ORDER batch 2)`.

### Task 3: `/implement` — the pair, the gate, the four stops

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 0; the resume list; *Ending early*; the Invariants)
- Modify: `plugins/dev-workflows/scripts/run-state.py` and its selftest, only if Task 1's measurement 8 found a key the change retires or adds
- Modify: `plugins/dev-workflows/docs/commands/implement.md`

**Interfaces:**
- Consumes: PH §3.4's row and §4.4's *earliest gap* from Task 2.
- Produces: the four stops; a Phase 0 section titled **Gate the unit's specification and design.**, which Tasks 4 and 5 cite; the fact that past Phase 0 a keyed run's `specs` holds the unit's pair, both on the default branch (or in the folder, on an unmanaged tree).

- [ ] **Step 1: Write the walk table first**, in the population file under `## Task 3 walks`: every row of Global Constraints' table for the specification and for the design, times {Epic unit, PRD-level broad slice}, times {first run, later run for the unit, companion run, tasks-only run}, plus Review Focus 1, 2, 3 and 5, plus the three rungs of the earliest gap, each with the expected stop or continuation.
- [ ] **Step 2: The expected pair.** Where a keyed run builds `specs`, it now names both paths of the unit's folder whether or not each is on disk; an `@path` token's files are added as context as today.
- [ ] **Step 3: Remove the specs question** (the array beginning `"Point me at a specs directory (you'll be prompted for the path)"`, and everything that carries its answer: the *Proceed without specs* log line in the Phase 5 report and any later phase that branches on it — Task 1's measurement 1 lists them).
- [ ] **Step 4: The gate and the stops.** `require-on-main` on each file of the pair, the specification first; the mapping of Global Constraints' table; the four stops in fenced blocks with their slot rules, the never-produced forms citing PH §4.4's earliest gap for what they name and naming the direct run as a way out; the unmanaged variants; no `emit-block`.
- [ ] **Step 5: The resume.** State in the resume list what a resumed run does at this gate, from Task 1's measurement 3, so that a run past its first edit is never stopped by a document removed since.
- [ ] **Step 6: Re-read every phase that read `specs`** (measurement 1's list) against the new premise — past Phase 0 a keyed run always has both documents — and fix each sentence it makes false or dead; add the invariant line; add the stops to *Ending early*.
- [ ] **Step 7: The docs page**, derived from the command as edited.
- [ ] **Step 8: Walk every row**, fix defects, gate chain exits 0, after-counts, commit: `feat(dev-workflows): a keyed /implement stops without the unit's specification and design on the default branch (LADDER-ORDER batch 2)`.

### Task 4: `/implement` — the pickers, the 0-Epic PRD, the multi-component rows, Phase 4.5

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (the `/implement <PRD>` branches of Phase 0; Phase 1's multi-component check; Phase 4.5)
- Modify: `plugins/workflows-core/references/components.md` (§6, the `implement` scope's rows and the remedies that name `/product-workflows:epics`), `plugins/workflows-core/references/epic-picker.md` (the no-Epics policy), then regenerate `reference-parts/`
- Modify: `plugins/dev-workflows/docs/commands/implement.md`

**Interfaces:**
- Consumes: Task 3's section and stops.

- [ ] **Step 1: Walks first** (`## Task 4 walks`): a PRD with N Epics of which k have the pair, for k = N, 0 < k < N, k = 1, k = 0; the same with the PRD folder holding the pair or not (the broad-slice option); a PRD with no Epic folder, with and without a PRD-level pair; each of those on a multi-component PRD; Review Focus 4.
- [ ] **Step 2: The picker (L8, L11).** An Epic lacking either file on the default branch is left out, counted, and named in the prose above the picker with the command it needs (the earliest gap, per Epic); the markers are reworded so each marks a listed row; the broad-slice option is offered only where the PRD folder holds the pair on the default branch; one Epic left and no slice is taken with a notice, as a single Epic is today; none left stops with the id of the earliest gap, naming one command. A multi-component PRD's override question is never skipped.
- [ ] **Step 3: A PRD with no Epic folder and no PRD-level specification** stops `IMPLEMENT_NEEDS_SPEC`; *Implement one broad PRD-level slice anyway* is no longer offered on a folder that lacks the pair. The offers of `/product-workflows:epics <PRD>` here (the 0-Epics array and its prose twin) take the PRD's landing first where it is not on the default branch (§5.5: b1b P-117, P-132), as does `epic-picker`'s no-Epics policy (P-134) and COMP §6's remedies (P-118).
- [ ] **Step 4: `multi-component-prereqs` at `implement` scope.** From Task 1's measurement 4: remove the `epic_spec` and `epic_design` rows from that scope, or show in the text why each still serves; leave `/ready`'s and `/epics`' scopes alone.
- [ ] **Step 5: Phase 4.5.** The falling-back consent array goes, with the sentence that gave *no consumer of `design.md` stops on row F* as its reason; what remains is the stopping array's case alone. Re-read the phase whole.
- [ ] **Step 6: The docs page; walk every row; gate chain exits 0; after-counts; commit:** `feat(dev-workflows): /implement <PRD> offers only what can be built, and Phase 4.5 loses its falling-back array (LADDER-ORDER batch 2)`.

### Task 5: The commands that name `/implement`, and the offers owed to this batch

**Files:**
- Modify: `plugins/dev-workflows/commands/design.md` (§5.5: `DESIGN_NO_SPEC` and the multi-component stop name the earliest gap; the arrays recommending `/product-workflows:create-ard <PRD>` and offering `/product-workflows:epics` are conditional on the PRD being landed)
- Modify: `plugins/dev-workflows/commands/conformance.md` (`CONFORMANCE_NOT_IMPLEMENTED` reworded; `CONFORMANCE_NO_REQUIREMENTS` names the earliest gap; the next-step lines naming `/dev-workflows:implement <KEY>` and the amend-document offer naming `/product-workflows:create-ard <KEY>` made conditional; L9's PRD-level trace: a stop of its own where Task 1's measurement 6 found the run goes on)
- Modify: `plugins/security-workflows/commands/scan.md` (the `### Next step` lines), and `plugins/workflows-core/scripts/weakness-classes.py` with its selftest only if Task 1's measurement 7 shows the sentence must change in the script
- Modify: their docs pages; `.claude/rules/dev-workflows.md`'s statement of `/design`'s multi-component stop

**Interfaces:**
- Consumes: PH §4.4's *earliest gap*; Task 3's stops.

- [ ] **Step 1: Walks first** (`## Task 5 walks`): for each stop and offer in the file list, the states of the PRD, the specification and the design that decide what it names.
- [ ] **Step 2: Make each edit**, citing PH §4.4's earliest gap wherever a stop names a producing command; each conditional offer names its test (a `cat-file -e "<default-ref>:./<path>"` on the document, or the gate's return where the run has one) and what it prints in each branch.
- [ ] **Step 3: The pages and the rules line; walk; gate chain exits 0; after-counts; commit:** `feat: /design, /conformance and /security-workflows:scan name the earliest gap, and offer /implement only where it can run (LADDER-ORDER batch 2)`.

### Task 6: The statements elsewhere

**Files:**
- Modify: every file the population file dispositions `rewrite` to this task: the `dev-workflows` docs pages that call `/design`'s `specification.md` the plugin's one hard exception or say `/implement` goes on without its documents (§5.5's list); the other plugins' pages; `.claude/rules/dev-workflows.md`, `dev-workflows-implement.md`, `dev-workflows-conformance.md`, `security-workflows.md`; `docs/maintainers/rationale.md` (`## ladder-order`, one paragraph for M3 and this batch); design §5.5 (any site found here and owed to batch 3 or 4).

- [ ] **Step 1: Rewrite each row**, one wording per claim across its copies (refinement 8).
- [ ] **Step 2: The rules files**, inside the budgets of Global Constraints: `dev-workflows-implement.md` takes no net growth; a new invariant goes to `dev-workflows-conformance.md`. `CLAUDE.md` takes no edit unless a sentence in it is false, and then a net-zero one.
- [ ] **Step 3: Verify:** after-counts; every population row has a final disposition; budgets re-measured and recorded; gate chain exits 0. Commit: `docs: LADDER-ORDER batch 2 — the statements that follow /implement's stops`.

### Task 7: Merge `main`, then release

**Files:**
- Modify: each changed plugin's `.claude-plugin/plugin.json` and `CHANGELOG.md`, `.claude-plugin/marketplace.json`, `.claude/rules/plugin-updates-coupling.md`, `docs/superpowers/to-test-on-real-project.md`, `docs/superpowers/to-fix.md` (the LADDER-ORDER entry)

- [ ] **Step 1: Merge first.** `git fetch origin`; if `git log --oneline HEAD..origin/main` prints anything, merge it (never rebase), resolve keeping both sides, re-read this branch's edits in every file both sides changed, regenerate `reference-parts/`, and run the gate chain before any release edit. Fetch again immediately before the release commit: if `main` moved meanwhile, merge again and re-derive the versions.
- [ ] **Step 2: Versions, from the merged tree.** `dev-workflows` minor (a run that went on now stops); `workflows-core` minor (§3.4's row, §4, §4.4); a patch for every other plugin this branch changed (`git diff --stat origin/main...HEAD -- plugins/`), a minor for `security-workflows` only if `/security-workflows:scan`'s behaviour changed beyond a printed line. `marketplace.json` agrees with each `plugin.json` and is not reformatted.
- [ ] **Step 3: Changelogs**, each section dated with the day of the release commit, no `— Unreleased` heading, each line derived from the tree and stating a behaviour change as a user meets it — above all M3's cost: a unit built earlier with a specification and no design stops on its next keyed run.
- [ ] **Step 4: The coupling bullet(s)**, after reading every coupling file (`.claude/rules/plugin-updates.md` requires it): what breaks with one side older, in both directions; every statement of the files' version ranges still true; the budget measured.
- [ ] **Step 5: Live checks** under a dated heading for this batch, marked not run: one per row of Global Constraints' table that changed, the picker cases, the resume case, the direct run, `/conformance` and `/security-workflows:scan`'s lines.
- [ ] **Step 6: The to-fix entry:** batch 2 built; batches 3 and 4 open.
- [ ] **Step 7: Verify:** gate chain exits 0 on the committed tree; `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` exits 0; `python3 scripts/validate-catalog.py` prints no new warning. Commit: `release: dev-workflows <new>, workflows-core <new> — a keyed /implement needs its specification and design (LADDER-ORDER batch 2)`.

### Task 8: Close

**Files:**
- Create: `docs/superpowers/verification/<release date>-ladder-order-b2.md`, `-rulings.md`, `-ledger.md`

- [ ] **Step 1 (after the final review's fix wave, never before it):** the verification record, every value re-derived against the tree being verified, with the command beside it; what was not run.
- [ ] **Step 2:** the rulings summary and the verbatim ledger, committed before the workspace is removed.
- [ ] **Step 3:** push, open the pull request, merge when CI is green, remove the worktree and the branch.

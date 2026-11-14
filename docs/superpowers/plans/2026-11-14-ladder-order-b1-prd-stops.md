# LADDER-ORDER Batch 1 — the PRD Stops Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/create-ard` and `/specify` stop on the idea route where the PRD folder's `prd.md` was never produced, and on either route where it is on disk and on no ref, each naming what to run; nothing else that runs today stops.

**Architecture:** No new machinery. Each command's own mapping of the gate's `absent` return changes from *report and go on* to a stop with its own ids; `phase-handoff` §3.4's two rows flip and its row-F remedy gains a second form for a committed file. `/update-spec`, which runs `/specify`'s gate sections by citation, gains a carve-out so it keeps today's behaviour.

**Tech Stack:** Markdown prose that agents execute; `scripts/reference-parts.py` (generated entry files); the repository gates in `.github/workflows/validate-catalog.yml`.

**Spec:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md` (approved 2026-11-14, merged as `92fc7a75`). This plan is its §5.1, plus batch 1's share of §4 and §7. Every task's implementer reads the design whole first. Below, PH is `plugins/workflows-core/references/phase-handoff.md`, ARD is `plugins/product-workflows/commands/create-ard.md`, SPEC is `plugins/product-workflows/commands/specify.md`. Line numbers are at `main` `92fc7a75`.

## Global Constraints

### The states and the ids

A required `prd.md` is tested in the PRD folder the run resolved (the folder itself on a PRD-level run, the folder above the Epic on an Epic-level run). The mapping, identical in both commands:

| The gate returns | And | Idea route (PRD folder holds no `brd-link.md`) | BRD route (it holds one) |
|---|---|---|---|
| `pass`, `pass_amending` | — | go on, as today | go on, as today |
| any stopping row | — | stop per §4.4, as today | the same |
| `absent` | `prd.md` is in the folder, HEAD does not hold it | `*_PRD_NOT_HANDED_OFF`, uncommitted form | the same |
| `absent` | `prd.md` is in the folder, HEAD holds it | `*_PRD_NOT_HANDED_OFF`, committed form | the same |
| `absent` | no `prd.md`, a pre-rename PRD file is in the folder | `*_NEEDS_PRD`, rename form | go on, reported, as today |
| `absent` | no `prd.md`, no pre-rename file | `*_NEEDS_PRD` | go on, reported, as today |
| `unmanaged` | `prd.md` is in the folder | go on, as today | go on, as today |
| `unmanaged` | no `prd.md` | `*_NEEDS_PRD` (rename form where it applies) | go on, as today |

- **Ids, spelled exactly:** `CREATE_ARD_NEEDS_PRD`, `CREATE_ARD_PRD_NOT_HANDED_OFF`, `SPECIFY_NEEDS_PRD`, `SPECIFY_PRD_NOT_HANDED_OFF`.
- **The HEAD test:** `git -C "$SPECS_PATH" cat-file -e "HEAD:./<path>" 2>/dev/null`, exit 0 = HEAD holds the file. An untracked file and a staged-but-uncommitted one both fail it and take the uncommitted form.
- **The pre-rename test** is `/prd-proposal`'s, word for word (`plugins/product-workflows/commands/prd-proposal.md:201–203`): *a top-level `.md` file whose name is the resolved key followed by `_`, other than `<KEY>_ARD.md`*.
- **The route test** is each command's own, unchanged: ARD:83 and SPEC:41 for a PRD-level run; for an Epic-level run the `brd-link.md` of the PRD folder above (ARD:294–296, ARD:410; SPEC:269).
- **Every stop carries PH §4.4's four parts, in order:** what was found; what the run did not do; the exact commands; what happens if ignored. Commands stand on lines of their own with no `#` comment.
- **A not-handed-off stop never names `/create-prd`** as the fix.
- **No stop `emit-block`s:** none is a plugin gap. Say so beside the stops, as ARD:328 does.

### What must not change

- `/update-spec`: on `absent` it reports and goes on, whether or not a `prd.md` is in the folder (design L5).
- A slice with no `prd.md`: `/create-ard` and `/specify` go on, reported (batch 4 changes the slice, not this batch).
- An `EPIC-` folder with no `epic.md`: unchanged (design L4).
- Rows D and E, the C rows, B′, G, I: unchanged.
- `/epics` reads `prd.md` from the working tree with no gate (design L13, PH:449).
- `plugins/workflows-core/reference-parts/` is generated: edit PH, then run `python3 scripts/reference-parts.py generate`. Never edit a file under it.

### The repository's own rules that bind every task

- `CLAUDE.md` § Editing discipline and `.claude/rules/claim-sweep.md`: this is a change of a claim's extent, so refinement 8 binds. Count the literal string before and after each rewrite, wrap-insensitively.
- `workflows-core:instruction-file-maintenance` binds the edits to `CLAUDE.md`, `.claude/rules/` and the references: a narrowing is itemised line by line.
- Budgets: `CLAUDE.md` is 35,462 characters against a 36,000 warning; `.claude/rules/plugin-updates-coupling.md` is 18,781 against 20,000. Measure both after editing (`wc -c`).
- PH §3.4's table is read by a gate and by a recipe: column 2 keeps each gated file in backticks (`scripts/check-docs.sh` check 11), and a stopping row's column 3 **begins** `**stops**` (the recipe in `.claude/rules/workflows-core-handoff.md`).
- Verify the branch before every commit: `git branch --show-current` prints `feat/ladder-order-b1`.

## Review Focus

The five states most likely to be broken by a correct-looking edit. Each is pinned by a walk in the task named.

1. **An unmanaged specs tree with a `prd.md` in the folder** (no git repository): the run must go on, not stop because nothing is "on the default branch". Task 3, Task 4.
2. **A slice with no `prd.md`, and an Epic under a slice**: must go on, reported. The Epic-level route test looks one folder up. Task 3, Task 4.
3. **A `prd.md` committed on the user's own branch, or on a local default branch not pushed**: the stop must print the push-and-merge form, never the `switch -c … add … commit` form, which fails there. Task 2, Task 3, Task 4, Task 5.
4. **`/update-spec` on a specification with no merged PRD above it**: must go on. Task 4.
5. **A folder holding only `<KEY>_ARD.md`**: must take the plain never-produced stop, not the rename form. Task 3, Task 4.

---

### Task 1: Branch, and the sweep population before any edit

**Files:**
- Create: `docs/superpowers/plans/2026-11-14-ladder-order-b1-sweep-population.md`

**Interfaces:**
- Produces: the population file. Every later task reads its own rows from it, and Task 7 writes the after-counts into it.

- [ ] **Step 1: Cut the branch** from `origin/main` as `feat/ladder-order-b1`, in the workspace the maintainer's setup gives (superpowers:using-git-worktrees).

- [ ] **Step 2: Enumerate every statement of the claim, by subject.** The subject is *what `/create-ard` or `/specify` does when the PRD folder's `prd.md` is not on the default branch*, plus *which consumers stop on `absent`*. Search `plugins/` (every `CHANGELOG.md` excluded from rewriting, included in the search), `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and the repo-root `README.md`. Start from these and generalise from each hit's own wording:

```bash
grep -rnE "not a prerequisite|No authored PRD on|never becomes a prerequisite|optional input|absent falls back|falls back|holds \*\*no .prd\.md|no .prd\.md.|does \*\*not\*\* require a PRD|absent. branch" plugins CLAUDE.md .claude/rules docs/maintainers README.md --include='*.md' | grep -v CHANGELOG.md
```

Expected floor: 23 lines match `is not a prerequisite|not a prerequisite at all|is still not a prerequisite` alone; `No authored PRD on` is in exactly ARD and SPEC.

- [ ] **Step 3: Write the population file.** One row per statement: `file:line`, the sentence's first words, and a disposition: **rewrite** (this batch, with the task that owns it), **keep — still true** (with why: BRD route, another command, an optional input), or **later batch** (2, 3 or 4, per the design's §7). The design's §7 list is the floor, not the set.

- [ ] **Step 4: Record the baseline counts** in the file, with the command beside each:
  - the stopping-consumer recipe from `.claude/rules/workflows-core-handoff.md`. Expected now: 9 (`/brd-interview` `/brd-package` `/brd-proposal` `/brd-reconcile` `/brd-split` `/design` `/prd-ground` `/prd-proposal` `/update-spec`);
  - `grep -c "No authored PRD on"` in ARD and SPEC: 1 each;
  - `wc -c CLAUDE.md .claude/rules/plugin-updates-coupling.md`.

- [ ] **Step 5: Commit.**

```bash
git add docs/superpowers/plans/2026-11-14-ladder-order-b1-prd-stops.md docs/superpowers/plans/2026-11-14-ladder-order-b1-sweep-population.md
git commit -m "docs: LADDER-ORDER batch 1 — the plan, and the sweep population before any edit"
```

This plan file is untracked on `main` when the branch is cut; it is committed here, with the population.

### Task 2: `phase-handoff` — the rows, the rule, and row F's committed form

**Files:**
- Modify: `plugins/workflows-core/references/phase-handoff.md` (§3.4 at 312–355, §4.4 row F at 611, §5 rule 3 at 623; check §4.1 at 527–537)
- Regenerate: `plugins/workflows-core/reference-parts/phase-handoff/*`
- Modify: `plugins/workflows-core/docs/reference/references.md:26`

**Interfaces:**
- Produces: the two §3.4 rows Tasks 3 and 4 cite; §4.4 row F's two forms, which Tasks 3, 4 and 5 write out in each command.

- [ ] **Step 1: Rewrite the `/create-ard` PRD row (PH:321).** Column 2 stays `the PRD (`prd.md`)`. Column 3 begins `**stops**` and says: a `prd.md` in the folder and on no ref is `CREATE_ARD_PRD_NOT_HANDED_OFF` on either route, whose action lands what is on disk in the form §4.4's row F selects and never names `/create-prd`; no `prd.md` in the folder is `CREATE_ARD_NEEDS_PRD` on the idea route, naming `/product-workflows:create-prd`, and on a BRD-route slice the pre-existing behaviour, kept: the run reads the resolved folder's own contents, reported. End the cell with the declaration: **a behaviour change, 2026-11-14 — before it this row fell back on every `absent`; the idea-route PRD was an optional input and is now required.**

- [ ] **Step 2: Split the `/specify` `/update-spec` PRD row (PH:322) in two.**
  - `/specify`: as Step 1's row, with `SPECIFY_NEEDS_PRD` and `SPECIFY_PRD_NOT_HANDED_OFF`.
  - `/update-spec`: today's text, made to stand alone. It no longer says *the same shape as `/create-ard`'s row*; it says the confirmation is skipped, reported, and adds: *`/specify`'s two stops on this input are not taken — a specification written before they existed may have no merged PRD above it.*

- [ ] **Step 3: Re-read the three pointers that the row change moves** and rewrite each from where it lands: the Epic row's *the shape of their PRD rows* (PH:323); PH:351's *"Gate the PRD — on every route"* sentence about `/create-ard`'s and `/specify`'s PRD rows, whose never-produced form is now idea-route only; PH:535's sentence that the PRD *stood there on the strength of `/create-ard`'s and `/specify`'s rows*.

- [ ] **Step 4: Rewrite the rule's three statements** so each is true of the new rows:
  - PH:314, *An input that was optional before this gate existed stays optional, and that must not change* → the gate still returns `absent` and never stops on it; an input moves from falling back to stopping only by a recorded decision, and the row says so.
  - PH:316, *every one of them is legitimate for the same reason: their gated input was never optional to begin with* → two reasons now: the input shipped with the command, or a recorded decision made it required (`/create-ard`'s and `/specify`'s idea-route PRD, 2026-11-14).
  - PH:355's closing list of consumers that stop on `absent` → add the two, named as decided, not as never-optional.
  - PH §5 rule 3 (PH:623) → *A consumer acts on the returned state, and on `absent` does what its §3.4 row says: its own pre-existing behaviour, or a stop. The gate never stops on `absent`, and no consumer turns an optional input into a prerequisite on its own account: a row stops where the input shipped with the consumer, or where a recorded decision made the input required, and §3.4 names each and which.*

- [ ] **Step 5: Add the committed form to §4.4 row F (PH:611).** After the existing commands, add: where HEAD holds the file (the HEAD test of *Global Constraints*), those commands do not apply, since the switch they open with takes the file out of the working tree and the `add` then matches nothing; the branch is landed instead. On a branch other than `<default>`: `git -C "$SPECS_PATH" push -u origin <branch>`, then a pull request from it into `<default>`, merged in the forge; with no `origin`, `git -C "$SPECS_PATH" switch <default>` then `git -C "$SPECS_PATH" merge <branch>`. On `<default>` itself: the commands row C″ gives for a commit the default branch holds and `origin` does not, its protected-branch alternative included.

- [ ] **Step 6: Check §4.1 (PH:527–537).** `prd.md` is already *gated — stopping*; confirm no sentence there still counts `/create-ard`'s or `/specify`'s PRD row as falling back.

- [ ] **Step 7: Update `docs/reference/references.md:26`**, which says *an optional input never becomes a prerequisite, and only a consumer whose input was never optional stops*.

- [ ] **Step 8: Regenerate and verify.**

```bash
python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py --selftest && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && ./scripts/check-docs.sh --root .
awk '/^### 3.4/{f=1} /^### 3.5/{f=0} f' plugins/workflows-core/references/phase-handoff.md | awk -F' \\| ' '/^\| `\// && $3 ~ /^\*\*stops/ {print $1}' | grep -o '`/[a-z:-]*`' | sort -u | wc -l
```

Expected: the chain exits 0, and the recipe prints `11` (the nine, plus `/create-ard` and `/specify`).

- [ ] **Step 9: Commit** PH, the regenerated parts and the docs page together.

### Task 3: `/create-ard`

**Files:**
- Modify: `plugins/product-workflows/commands/create-ard.md` (step 5 at 234–243; *Gate the PRD* at 274; the paragraph at 276–292; Phase 1 step 1 at 372; Phase 2 at 429–436; `### Next step` at 800–806 and its arrays)
- Modify: `plugins/product-workflows/docs/commands/create-ard.md` (lines 52, 74, 146 and its error-id list)

**Interfaces:**
- Consumes: Task 2's `/create-ard` row and row F's two forms.
- Produces: the stop texts below. Task 4 writes the same texts with `SPECIFY_` ids and `/product-workflows:specify`.

- [ ] **Step 1: Write the walk table first**, as a comment block in the population file, one row per state of *Global Constraints*' table for a PRD-level run and for an Epic-level run, plus Review Focus 1, 2, 3 and 5. Column: *the line the run prints, or the stop id*. This is the test the edited command is read against in Step 6.

- [ ] **Step 2: Replace the `absent` and `unmanaged` branches of *Gate the PRD* (ARD:274).** The gate call, the `stopped`-first mapping and the `pass` branch stay. On `absent` and `unmanaged` the run now applies *Global Constraints*' table. The report line *"No authored PRD on `<default>` for `<PRD>` — architecting from the resolved folder at `<path>`. …"* stays, for the slice alone. The stops, exact:

```
CREATE_ARD_NEEDS_PRD: <PRD> has no prd.md — none on any ref, and none in <path>. This run read nothing further and wrote nothing: an ARD decides how a PRD's requirements are built, and there is no PRD here to decide for. Run '/product-workflows:create-prd <PRD>' and merge its handoff, then re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, /create-ard and /specify each stop on this folder until it holds a merged PRD.
```
```
CREATE_ARD_NEEDS_PRD: <PRD>'s PRD is <path>/<name>, written before the artifact filenames lost their keys, and this command reads prd.md alone. This run read nothing further and wrote nothing. Rename it to prd.md ('git -C "<SPECS_PATH>" mv -- "<path>/<name>" "<path>/prd.md"'), land the rename, and re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, /create-ard and /specify each stop on this folder until it holds a merged prd.md.
```
```
CREATE_ARD_PRD_NOT_HANDED_OFF: <PRD>'s prd.md is written at <path> but is on no branch — its handoff was declined, so nothing is missing but the commit. This run read none of it and wrote nothing. Commit and merge it to the specs repo's default branch by running these; do not re-run /product-workflows:create-prd, which would rewrite the PRD rather than land the one on disk:

git -C "<SPECS_PATH>" switch --no-track -c <new-branch> <default-ref>
git -C "<SPECS_PATH>" add -f -- "<path>"
git -C "<SPECS_PATH>" commit -m "<PRD> prd" -- "<path>"
git -C "<SPECS_PATH>" push -u origin <new-branch>

Then open a pull request from <new-branch> into <default>, merge it, and re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>.
```
```
CREATE_ARD_PRD_NOT_HANDED_OFF: <PRD>'s prd.md at <path> is committed on <branch>, a branch this plugin does not hand off, and is not on <default>. This run read none of it and wrote nothing. Land that branch; do not re-run /product-workflows:create-prd, which would rewrite the PRD rather than land the one committed:

git -C "<SPECS_PATH>" push -u origin <branch>

Then open a pull request from <branch> into <default>, merge it, and re-run '/product-workflows:create-ard <ADDRESS>'. Ignored, every /create-ard and /specify run on this folder stops here until prd.md is on <default>.
```

Beneath them, the slot rules, modelled on ARD:327: `<new-branch>` is `prd/` and the folder's `<KEY>-<slug>`, first free name under the handoff's branch-naming rule, found before the stop prints; with no `origin`, the push and pull request give way to `switch <default>` then `merge`; in the committed form, where HEAD is `<default>` itself, the first sentence reads *is committed on your local `<default>` and not pushed* in place of *is committed on `<branch>`, a branch this plugin does not hand off, and is not on `<default>`*, and the command is `git -C "<SPECS_PATH>" push origin <default>`, or on a protected default branch `switch --no-track -c <new-branch>`, `push -u origin <new-branch>` and a pull request.

- [ ] **Step 3: Order step 5's advisory after the gates.** Step 5 reads `prd.md` *ahead of its gate* and can ask *Author the ARD anyway / Stop — no ARD needed* (ARD:239–243). State at step 5's head that it is taken after *Gate the PRD*, *Gate the decision register* and *Gate the Epic*, so a run they stop is never asked it, and rewrite *ahead of its gate*. Check no gate reads step 5's answer.

- [ ] **Step 4: Rewrite the defences of the fall-back** in this file, each from the population file: the paragraph at 276–292 (*the `absent` branch is what makes that safe … `/create-prd` is still not a prerequisite for this command, on either route*) now says the slice falls back and the idea route stops; 429–436 (*An absent `prd.md` is reported and never a stop, on either route … on the idea route it is unusual but supported*); Phase 1 step 1 at 372; `### Next step` at 800–806 (*This run does **not** require a PRD*), where the idea-route no-PRD option is now unreachable and goes, with any array written only for it (design L8; `.claude/rules/plugin-authoring.md`, *Surgical Changes*). ARD:263–264 speaks of the BRD route and stays.

- [ ] **Step 5: Update the docs page**: line 52's *An **absent** PRD is not a stop*, line 74, line 146, and add the two ids to its stops list with one line each.

- [ ] **Step 6: Run the walk.** Read the edited command top to bottom once per row of Step 1's table and write beside each row what the text now does. Every row must match. Then:

```bash
grep -c "CREATE_ARD_NEEDS_PRD" plugins/product-workflows/commands/create-ard.md   # ≥ 3
grep -c "CREATE_ARD_PRD_NOT_HANDED_OFF" plugins/product-workflows/commands/create-ard.md   # ≥ 3
grep -n "on either route" plugins/product-workflows/commands/create-ard.md   # no hit that speaks of an absent PRD
./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-citations
```

- [ ] **Step 7: Commit** the command and its docs page.

### Task 4: `/specify`, and `/update-spec`'s carve-out

**Files:**
- Modify: `plugins/product-workflows/commands/specify.md` (*Gate the PRD* at 315; 317–331; Step A at 538–547 and 603–627; Step B at 660–666; `### Next step` at 1346–1352)
- Modify: `plugins/product-workflows/commands/update-spec.md:57`
- Modify: `plugins/product-workflows/docs/commands/specify.md` (lines 84, 148, its stops list), `plugins/product-workflows/docs/commands/update-spec.md`

**Interfaces:**
- Consumes: Task 2's rows; Task 3's four stop texts, with `SPECIFY_NEEDS_PRD`, `SPECIFY_PRD_NOT_HANDED_OFF`, `'/product-workflows:specify <ADDRESS>'`, and in the never-produced text *a specification states how a PRD's requirements behave, and there is no PRD here to specify*.

- [ ] **Step 1: Write the walk table**, as Task 3 Step 1, adding: `/specify <PRD>` with no Epic folder on the idea route with and without a merged `prd.md`; `/update-spec <KEY>` with no `prd.md` anywhere; `/update-spec <KEY>` with a `prd.md` on disk and on no ref.

- [ ] **Step 2: Replace *Gate the PRD*'s `absent` and `unmanaged` branches (SPEC:315)** exactly as Task 3 Step 2, with this command's ids and texts. The report line *"No authored PRD on `<default>` … specifying from the resolved folder at `<path>`. …"* stays for the slice alone.

- [ ] **Step 3: Remove what the stop makes unreachable on the idea route, and only that.**
  - The zero-Epics question's no-PRD form (SPEC:609–627): the sentence *A folder carrying no `brd-link.md` has no gate set and takes `/product-workflows:create-prd <PRD>` on the container test alone* goes, and the paragraph says the no-PRD form is a slice's. The slice form, resolved against the ledger, stays whole (batch 4 removes it).
  - SPEC:538–547 and 660–666: *a folder holding **no `prd.md`*** is now a state only a slice reaches; say so, and drop *a supported one on the keyed route*.
  - `### Next step` (SPEC:1346–1352): *This run does **not** require a PRD* becomes true of the BRD route alone.

- [ ] **Step 4: Rewrite SPEC:317–331** as Task 3 Step 4 rewrites ARD:276–292.

- [ ] **Step 5: `/update-spec`'s carve-out (`update-spec.md:57`).** Step 6 becomes:

> 6. **Gate the inputs**, as `/specify` gates them — its *Gate the PRD*, *Gate the decision register* (BRD route) and *Gate the Epic* sections, each applied to this folder, with their stops named `UPDATE_SPEC_` in place of `SPECIFY_` — **save the two stops *Gate the PRD* makes where the PRD is on no ref**, `SPECIFY_NEEDS_PRD` and `SPECIFY_PRD_NOT_HANDED_OFF`, which this command does not take on either route: there it reports *"No authored PRD on `<default>` for `<PRD>` — revising against the resolved folder at `<path>`."* and goes on, whether or not a `prd.md` is in the folder. A specification written before those stops existed may have no merged PRD above it, and this command revises a specification that is already merged.

Check step 7a (`update-spec.md:59`), which names the PRD *where step 6's gate returned `pass` or `pass_amending`*: it still reads true.

- [ ] **Step 6: Update the two docs pages.** `specify.md` line 148's *"absent falls back, unmerged stops" gates it shares with `/create-ard`* is rewritten; the stops list gains the two ids. `update-spec.md` says its PRD confirmation is skipped, reported, where no merged PRD stands.

- [ ] **Step 7: Run the walk**, as Task 3 Step 6, over Step 1's table, then:

```bash
grep -c "SPECIFY_NEEDS_PRD" plugins/product-workflows/commands/specify.md   # ≥ 3
grep -c "SPECIFY_NEEDS_PRD\|SPECIFY_PRD_NOT_HANDED_OFF" plugins/product-workflows/commands/update-spec.md   # 2, both in step 6's carve-out
grep -c "UPDATE_SPEC_NEEDS_PRD\|UPDATE_SPEC_PRD_NOT_HANDED_OFF" -r plugins   # 0
./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-citations
```

- [ ] **Step 8: Commit.**

### Task 5: The stops and offers that already exist

**Files:**
- Modify: `plugins/product-workflows/commands/prd-ground.md:559–566` (`PRD_GROUND_PRD_NOT_HANDED_OFF`), `plugins/product-workflows/commands/prd-proposal.md:239–246` (`PRD_PROPOSAL_PRD_NOT_HANDED_OFF`)
- Modify: `plugins/product-workflows/commands/epics.md:1124`
- Modify: `plugins/product-workflows/docs/commands/prd-ground.md:330`, `prd-proposal.md:52`, `epics.md`

**Interfaces:**
- Consumes: Task 2's row F committed form; Task 3's committed-form stop text as the model.

- [ ] **Step 1: Give each of the two idea-route stops its committed form** (design §4). Each keeps its present text for an uncommitted file and gains a second message under the same id, selected by the HEAD test, modelled on Task 3's fourth stop with this command's name and re-run line. The BRD-route `*_NOT_HANDED_OFF` stops in these and other files are batch 4's; list them in the population file as *later batch 4* and leave them.

- [ ] **Step 2: Make `/epics`' two offers honest** (design L13). At `epics.md:1124`, the lines offering `/product-workflows:specify <EPIC>` and `/product-workflows:create-ard <EPIC>`: where the PRD folder's `prd.md` is not on the default ref (`git -C "$SPECS_PATH" cat-file -e "<default-ref>:./<prd path>"` fails, on a tree the plugin manages), the line says first *land `<PRD>`'s `prd.md` on `<default>` — both stop until it is*. `/epics` itself gains no gate.

- [ ] **Step 3: Check `workflows-core:next-phase-offer`** for an offer naming `/create-ard` or `/specify` on an idea-route folder that can hold no merged PRD. `/idea`'s own offers name `/create-prd`; the *`/epics` precondition* part (line 332) speaks of the BRD route and stays. Record what was checked in the population file. Where an offer does need a change, edit the reference and regenerate the parts as Task 2 Step 8 does.

- [ ] **Step 4: Update the three docs pages** for what Steps 1 and 2 changed.

- [ ] **Step 5: Verify and commit.**

```bash
./scripts/check-docs.sh --root . && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations
```

### Task 6: The instruction tier and the family's pages

**Files:**
- Modify: `CLAUDE.md` (§ Hard constraints, last bullet), `.claude/rules/workflows-core-handoff.md`, `.claude/rules/product-workflows.md` (the `/create-ard` and `/specify` map lines), `.claude/rules/brd-route.md` (the tail's *the PRD gate runs, and its absent branch architects from the slice folder* — still true of a slice; re-read, and say the idea route differs only if the sentence could be read as both), `docs/maintainers/rationale.md`
- Modify: `plugins/product-workflows/docs/roles-and-phases.md:10`, and any page the population file lists under this task
- Modify: `docs/superpowers/to-test-on-real-project.md`

- [ ] **Step 1: `CLAUDE.md`.** The bullet's clause becomes: *an absent optional input still delegates to the command's pre-existing behaviour and never becomes a prerequisite, while the document a command builds from is required and its absence stops the run — `workflows-core:phase-handoff` §3.4 says which each input is (multi-component PRDs: `workflows-core:ard-resolution`)*. Then `wc -c CLAUDE.md`: under 36,000.

- [ ] **Step 2: `.claude/rules/workflows-core-handoff.md`.** *the nine consumers with a row that stops instead* becomes eleven, named, with `/create-ard` and `/specify` marked as stopping on the idea-route PRD by decision and not as inputs that were never optional. Run the recipe written there; it prints 11.

- [ ] **Step 3: The two map lines** in `.claude/rules/product-workflows.md` say what the PRD gate now does on the idea route.

- [ ] **Step 4: `docs/maintainers/rationale.md`** gains a section, `#ladder-order`, holding the evidence: the decision's date, the three alternatives refused at M1, why the slice is exempt, why `/update-spec` is, and why a not-handed-off file names its landing. Link it from the `CLAUDE.md` bullet with `([why](docs/maintainers/rationale.md#ladder-order))` only if the budget holds; otherwise from the rules file.

- [ ] **Step 5: Itemise the narrowing** (`workflows-core:instruction-file-maintenance`): in the population file, list each sentence of the old rule in `CLAUDE.md`, the rules files and PH, and against each what the tree says now.

- [ ] **Step 6: `roles-and-phases.md:10`** and the other listed pages.

- [ ] **Step 7: Live checks.** Add a section `## LADDER-ORDER batch 1 — product-workflows <version>, workflows-core <version>` to `to-test-on-real-project.md`, one check per row of *Global Constraints*' table that stops, plus Review Focus 1, 2 and 4, each naming the folder state to set up and the line expected.

- [ ] **Step 8: Verify and commit.**

```bash
python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline
```

### Task 7: Release

**Files:**
- Modify: `plugins/product-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, both plugins' `CHANGELOG.md`, `.claude/rules/plugin-updates-coupling.md`, and every file that states either version (`grep -rn "3\.80\.0\|1\.89\.0" --include='*.md' --include='*.json' . | grep -v CHANGELOG`)

- [ ] **Step 1: Re-derive the versions** against `origin/main` at release time. As this is written they are `product-workflows` 3.80.0 → 3.81.0 and `workflows-core` 1.89.0 → 1.90.0: a behaviour change, so a minor.

- [ ] **Step 2: Dated `CHANGELOG.md` sections**, never `— Unreleased` on a branch that reaches `main`. `product-workflows`: *Changed* — the two commands stop where they reported, with the four ids, what each names, and the slice's exemption; `/update-spec` unchanged, by its carve-out; *Fixed* — the two existing stops' committed form. `workflows-core`: the rows, rule 3, and row F's second form.

- [ ] **Step 3: The coupling bullet.** `product-workflows` 3.81.0 with `workflows-core` 1.90.0: a newer `product-workflows` beside an older core stops with ids the core's §3.4 row still describes as falling back, and prints a committed-form remedy §4.4 does not hold; an older `product-workflows` beside the newer core carries on where the core's row says it stops. Then `wc -c .claude/rules/plugin-updates-coupling.md`; over 20,000, move the oldest bullets to a history file as the earlier splits did and update `.claude/rules/plugin-updates.md` and `CLAUDE.md`'s table.

- [ ] **Step 4: Verify and commit.**

```bash
python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root .
```

### Task 8: Close

- [ ] **Step 1: After-counts.** Re-run every command recorded in the population file and write the after-count beside each before-count. No row dispositioned *rewrite* still reads as it did; `grep -rn "No authored PRD on"` hits only slice-scoped sentences and `/update-spec`'s carve-out.

- [ ] **Step 2: The full gate chain**, every `run:` step of `.github/workflows/validate-catalog.yml` in order as one `&&` chain, reading the chain's own exit code.

- [ ] **Step 3: An Opus review of the whole branch** (superpowers:requesting-code-review), briefed with the design and this plan and asked for the change's own defects. Triage every finding at the line it names; fix; one re-review of the fix wave.

- [ ] **Step 4: The verification record, written last**, after the final fix wave: `docs/superpowers/verification/2026-11-14-ladder-order-b1.md`, every expected value re-derived against the tree being verified.

- [ ] **Step 5: Push the branch and open the pull request**; merge when CI is green. Then the plugin update commands for the maintainer, naming both plugins (`.claude/rules/plugin-updates.md`).

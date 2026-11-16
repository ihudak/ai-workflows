# LADDER-ORDER batch 3 — `/document <KEY>` asks before it documents work nobody built — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A keyed `/docs-workflows:document` run asks one question, *Stop* recommended, where the implementation record in its scope holds no block and the commit scan found no commit; and `/docs-workflows:release-notes` stops offering `/create-ard` and `/epics` for a PRD that is not landed.

**Architecture:** Everything is prose in command, reference and page files, executed literally by agents. The record read and, only on a run whose record holds no block, the repositories question, the slug→clone map and the commit scan move forward into Mode A's Phase 0, between step 3 and step 4; Phase 3 reuses what Phase 0 produced. The line *Stop* prints takes `workflows-core:phase-handoff` §4.4's *The first missing document*, which batch 2 shipped. No script changes.

**Tech Stack:** Markdown command and reference files; the repository's gates (`scripts/check-docs.sh`, `scripts/check-id-grammar.sh`, `scripts/reference-parts.py`, `scripts/mermaid/check-mermaid.mjs`, `scripts/validate-catalog.py`), run as the `run:` steps of `.github/workflows/validate-catalog.yml` in one `&&` chain.

**Spec:** `docs/superpowers/specs/2026-11-14-ladder-order-design.md` — §2 (M6, L2, L2a, L3, L8, L12), §5.3, §5.5's **Batch 3** list, §6, §7, §8, §10. Measured against the tree on 2026-11-16: `docs/superpowers/plans/2026-11-16-ladder-order-b3-measurements.md` (cited below as *M §n*); its §9 is the sweep population, rows `P-1` to `P-71`.

Abbreviations: DOC = `plugins/docs-workflows/commands/document.md`; RN = `plugins/docs-workflows/commands/release-notes.md`; KD = `plugins/docs-workflows/references/key-discovery.md`; PH = `plugins/workflows-core/references/phase-handoff.md`; NPO = `…/references/next-phase-offer.md`; IF = `…/references/implementation-format.md`; ER = `…/references/escalation-rules.md`; "page X" = the docs page of command X. Line numbers are at `main` when this plan was written (the measurements' tree); find each site by its text.

## Global Constraints

From the design, verbatim where quoted:

- M6: "`/document <KEY>` asks, with *Stop* recommended; it does not stop outright." No error id on the question (§5.3: "The stop it leads to is the user's answer, reported as such").
- L2: the question is put "only where the implementation record holds no block in the run's scope and the commit scan found no commit." "The report-only probe's matches and a pull request the scan lists and does not read … are not commits found; the lines above the question print them."
- §5.3: "**Only where it holds no block** does the run resolve `$REPOS_PATH` and run the scan this early; a run whose record holds a block keeps today's order in every respect."
- §5.3: "A misconfigured path is thus never reported as nothing built."
- §5.3: "Two options, the first recommended: stop and implement first; or go on from the PRD alone. Neither label names a command, so the array is one text in every state. … A free-text answer is normalised into one of the two or asked again."
- §5.3: "**Nothing is asked twice, and a later base is scanned.** Phase 3's own scan reuses the early one's result."
- §5.3: "`/document` is not a caller of the gate, so PH §3.4 takes no row for it."
- L3: "`/release-notes` is unchanged" in what it drafts and when; only its two next-step offers change (§5.5).
- L8: "No picker and no next-step offer names or recommends a run that would stop on arrival."
- The question is **never called a gate** in any text this batch writes (`docs-workflows:gate-ledger` §4's registry lists verification gates, and a registry gate with no row is a reviewer BLOCKER; M §8).
- The array, one text in every state: `choices: ["Stop — implement it first (Recommended)", "Go on — document from the PRD alone"]`. If check 12 objects to a label, the implementer changes the label minimally, keeps "neither names a command", and reports the wording.
- One noun for the question about where the repositories are, in every copy: **the repositories question**. One noun for the new question: **the nothing-built question**.
- No script changes: `plugins/docs-workflows/scripts/key-discovery.py`, `bounded.py`, and every file under `scripts/` stay as they are. `plugins/docs-workflows/references/gate-ledger.md` is not edited.
- Budgets (`LC_ALL=C.UTF-8 wc -m`; a bare `wc -m` counts bytes in this container): `CLAUDE.md` 35,898 and must not grow; no `.claude/rules/*.md` file reaches 20,000 — `.claude/rules/docs-workflows.md` stands at 19,986 (M §9, P-49).
- Each agent keeps its scratch files in a subdirectory of its own under the session scratchpad; one writer in the worktree at a time.
- After editing any `plugins/workflows-core/references/*.md`: `python3 scripts/reference-parts.py generate`, and commit the regenerated parts with the edit.
- One wording per claim across every copy; after each task, count each retired string wrap-insensitively over `plugins/` (changelogs as history), `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`, `README.md`.

## Settled against the measurements (the lead's rulings; the design is amended to match in Task 5)

Each departs from, or completes, §5.3 as written. *What it costs if wrong* is stated for the maintainer.

| # | Ruling | Why | Cost if wrong |
|---|---|---|---|
| R1 | **The record is read at the end of Phase 0 step 1; the repositories question, the map, the scan and the nothing-built question sit between step 3 and step 4** — after the docs repository is resolved, before the profile. §5.3 said "once the address is resolved and the preflight has run". | The scan must exclude the docs repository (KD §1, `--exclude`), which step 2 resolves. In the default layout the docs clone lies under `$REPOS_PATH` and its squash subjects carry the key: without the exclusion a second run on a key whose first run answered *Go on* finds "commits" and never asks (M §3). | Step 2's own questions (which docs repository) come before the nothing-built question. |
| R2 | **A PRD-level *Stop* does not name `/dev-workflows:implement <PRD>` unconditionally.** It names it where a unit that run would offer has both files on the default branch, and otherwise each Epic's first missing document — worded as `CONFORMANCE_PRD_NOT_IMPLEMENTED`'s `<how it is built>` is, by citation of NPO's Dev-lane *`/dev-workflows:implement` precondition* and PH §4.4. §5.3 said "names `/dev-workflows:implement <PRD>`, whose picker says what each Epic needs". | Since batch 2 that run stops where no unit is buildable (M §7); L8. | None known; it is the rule batch 2 shipped. |
| R3 | **An Epic whose block sits in the PRD folder from before `dev-workflows` 4.1.2** reads as not built to an Epic-addressed run. The lines above the question and the *Stop* line add the move clause `/conformance` already prints (`conformance.md`, `CONFORMANCE_NOT_IMPLEMENTED`: "move it into the Epic's own, as workflows-core:implementation-format §1 says"), where the PRD folder's record holds any block. | Otherwise *Stop* names `/implement <EPIC>` for built work (M §2). | One clause printed on legacy trees only. |
| R4 | **"The scan did not look" has four forms, each printed as such and never as zero matches**: *Proceed without the repos*; no clone resolved under an existing base (KD: "not run — no clone resolved"); the script failing twice; a repository returned with `error` (for that repository). The question is still put — no commit was found — and its lines say which. | §5.3's "never reported as nothing built" fails otherwise for an existing-but-empty base (M §14.4). `docs/reference/environment.md`'s sentence on an empty base changes with it. | Longer lines above the question. |
| R5 | **The lines above the question say the scan read each clone's `HEAD` as it stands, unfetched.** | A stale clone misses pushed work and the question would recommend *Stop* (KD: "The script fetches nothing"). | One sentence. |
| R6 | **Phase 5's aggregate gate is put only where at least one ref was in scope.** | On zero refs "every ref is unresolved" is vacuously true: a *Go on* run would be asked a second PRD-only question (M §6). | None. |
| R7 | **Phase 3 takes Phase 0's map and scan result; it builds and scans nothing again**, save where a base named at Phase 2's *Revise plan* replaced `$REPOS_PATH` or undid *Proceed without the repos* — then the map is rebuilt and the scan re-run once over the new base (KD's *A clone mounted mid-run* gains the case). The scan's JSON file lives until Phase 3 has taken it, and the Invariants' list of the run's `mktemp` files names it. | DOC says the map is "never built twice"; KD deletes the JSON in the phase that made it (M §3, §5). | None. |
| R8 | ***Go on* is recorded in two places**: the final report's `### Assumptions & limitations`, and one line of `pr-draft.md`'s body — `No implementation record and no commit naming <keys> was found; these pages were written from the PRD alone, by the operator's answer.` | §5.3: "pages written with no implementation behind them say so". The docs pull request's reviewers read `pr-draft.md`, not the run's report, and `/ready` counts that draft toward *Release Preparation* (M §6). | One line in a draft a human edits anyway. |
| R9 | **A legacy block with `commit: null` counts as a block** and suppresses the question (IF §1's test is the heading). The text says so. | One test for "holds a block", the one every other reader uses. | A pre-4.36.0 `--no-commit` run's key is not asked about. |
| R10 | **`/release-notes`' two offers** are each made conditional on the PRD folder's `prd.md` being on the specs repository's default branch, read as `plugins/security-workflows/commands/scan.md` reads it for the same offer (`git -C "$SPECS_PATH" show "<default-ref>:./<path>/prd.md"`; the folder's own file on a tree that is no git repository), the `/epics` offer also on that file asserting `kind: prd`; where it is not landed, the next step names its landing by PH §4.4, as `scan.md`'s not-landed sentence does. `plugins/product-workflows/docs/workflow.md`'s **two** edges (`:48` to `/create-ard`, `:49` to `/epics`) take the condition; the design named only `:49`. | `/create-prd` recommends `/release-notes` at once, so the usual early run is on a `prd.md` whose handoff has not merged (M §10). | None. |
| R11 | **Versions:** `docs-workflows` 1.39.7 → 1.40.0 (a new question); `workflows-core` 1.94.0 → 1.94.1, `product-workflows` 3.83.1 → 3.83.2, `dev-workflows` 4.68.0 → 4.68.1 (wording and one diagram). Coupling bullet: `docs-workflows` 1.40.0 cites PH §4.4's *The first missing document* and NPO's Dev-lane precondition, which `workflows-core` 1.94.0 first holds. | The measurement (M §12, §13). Re-read `origin/main` before the release commit; renumber if it moved. | — |

*R11, renumbered 2026-11-16.* `origin/main` moved while the batch was built: pull request #205 (SEC-G2 D) released `workflows-core` 1.95.0, `dev-workflows` 4.69.0, `product-workflows` 3.83.2, `docs-workflows` 1.39.8 and `security-workflows` 0.12.6. Merged into this branch, the batch ships as `docs-workflows` 1.40.0 (unchanged), `workflows-core` 1.95.1 (was 1.94.1), `dev-workflows` 4.69.1 (was 4.68.1) and `product-workflows` 3.83.3 (was 3.83.2, the number #205 gave its own release). The coupling claim stands: `docs-workflows` 1.40.0 cites what `workflows-core` 1.94.0 first holds. The row above, and Task 5's commit subject, keep the numbers as planned.

**Not in this batch, said so the maintainer can overrule:** the relaunch at Phase 1.5 (*Relaunch … under Opus*) starts a new run, which is asked the nothing-built question again — the answer is not carried across runs, since `/document` keeps no run state. Mode B has no keyed form and is untouched.

## Review Focus

The states most likely to bite a person, none of which a gate exercises; each is a walk row in the task named.

1. **A second run after *Go on*.** The first run published pages; the docs clone lies under `$REPOS_PATH`. Expect the second run to be asked again — the docs repository is excluded from the scan. (Task 1)
2. **A base that exists and holds no clone, or a wrong `REPOS_PATH`.** Expect "the scan did not look", never "none found", and the repositories question only where no entry is an existing directory. (Task 1)
3. **A run whose record holds a block.** Expect today's order in every respect: no early map, no early scan, the repositories question in Phase 1, Phase 3 building the map. (Tasks 1 and 2)
4. **An Epic built before `dev-workflows` 4.1.2**, its block in the PRD folder, addressed by its own key. Expect the question's lines and *Stop* to carry the move clause, and *Stop* not to say only "implement it". (Task 1)
5. ***Stop* on a PRD none of whose Epics can be built** — one with no design, one whose `prd.md` sits under its pre-rename file name, a multi-component PRD with no Epic folder. Expect each to name what the first missing document needs, never a run that stops on arrival. (Task 1)

---

### Task 1: Phase 0 — the record read, the early scan, the nothing-built question

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md` — *Mode detection*'s *Ending early* (DOC:58); Phase 0 step 1's end (after *Check the lineage*, about DOC:195); a new step between step 3 (DOC:222) and step 4 (DOC:224), numbered so that no existing step is renumbered (name it **3a**, or as the file's own convention for an inserted step shows — check how `4(c)` and other sub-steps are named and cited before choosing; every existing citation of "step 4(c)" must stay true); the `### Readiness` table (DOC:316–330).
- Modify: `plugins/docs-workflows/references/key-discovery.md` §1 — where the scan may run (KD:9), and the life of its JSON file (KD:21).
- Create: `docs/superpowers/plans/2026-11-16-ladder-order-b3-sweep-population.md` — the population file: copy M §9's rows `P-1`…`P-71` under a header, add a `Status` column (`open` / `done in Task n` / `stays true — checked`), and a `## Task 1 walks` section.

**Interfaces:**
- Consumes: IF §1 (a record is present only where it holds a block) and §4 (the two-source read, the scope); KD §1 (the scan's recipe, `--exclude`, `--owner-of`); PH §4.4 *The first missing document* (loaded whole, as `scan.md` loads it: `Skill(skill: "workflows-core:reference", args: "phase-handoff")`); NPO's `dev` part (*The `/dev-workflows:implement` precondition*); the model wording of `plugins/dev-workflows/commands/conformance.md`'s paragraph *What a stop or an offer names in place of a run that would stop on arrival* and its `CONFORMANCE_PRD_NOT_IMPLEMENTED` `<how it is built>`, and `ready.md`'s `SUPPORTED` offer for how a command that runs no gate reads a document's state.
- Produces, for Task 2 (names it must use verbatim): `record_blocks` — the blocks read in the run's scope at the end of step 1 (empty or not); `early_scan` — `ran` / `not run — <reason>` with its parsed result and the slug→clone map, set only on a run whose `record_blocks` is empty; `repos_answer` — the repositories question's answer where Phase 0 put it (`set` / `proceed-without` / unset); `nothing_built_answer` — `go-on` where the question was put and answered *Go on*, unset otherwise.

- [ ] **Step 1: Write the walk table first** (the test). In the population file's `## Task 1 walks`, one row per state below, columns `State | Expected, from the design and R1–R9 | What the text does (file:line) | Match`. Fill *Expected* now, the last two after Step 4.

  States: (a) record holds a block, PRD run; (b) the same, Epic-focused; (c) no block, the scan finds a commit; (d) no block, the scan ran and matched nothing, PRD run, some unit buildable; (e) the same, no unit buildable — one Epic lacks a design, one PRD under its pre-rename file name, one multi-component PRD with no Epic folder (three rows); (f) the same as (d), Epic-focused, the Epic's pair on the default branch; (g) Epic-focused, the Epic lacks a design; (h) Epic-focused, the PRD folder's record holds a block (R3); (i) no entry of `$REPOS_PATH` is an existing directory → *Set REPOS_PATH*, *Proceed without the repos*, *Cancel* (three rows); (j) the base exists and the map is empty; (k) the script fails twice; (l) one repository returns `error`, the others match nothing; (m) only the probe matched, or only a listed pull request; (n) a second run after *Go on*, docs clone under `$REPOS_PATH`; (o) `@<path>` address with `$SPECS_PATH` unset; (p) the `DOCUMENT_BRD_NOT_SLICED` re-entry onto a slice; (q) a legacy `commit: null` block; (r) a free-text answer; (s) *Stop* where step 4(c) has not run — nothing in the docs repository touched.

- [ ] **Step 2: The record read, at the end of step 1.** After *Check the lineage*: read the implementation record in the run's scope exactly as Phase 3's step *The record* does (cite it; same entry, same scope sentence — "the focus Epic's own where `focus_key` is set, and otherwise the PRD folder's and every `EPIC-` folder's"), and say what is carried (`record_blocks`). A legacy `commit: null` block is a block (R9). It must sit after the `DOCUMENT_BRD_NOT_SLICED` re-entry.

- [ ] **Step 3: The inserted step, between step 3 and step 4 — only where `record_blocks` is empty.** In order:
  1. Resolve `$REPOS_PATH` as Phase 1 does (cite Phase 1's bullet; do not restate its rule differently). Where no entry is an existing directory, put **the repositories question** here — the same array, verbatim, in a paragraph that names `Required path environment variable unset` (check 23) — and say it is not put again in Phase 1. *Cancel* stops the run by *Ending early*.
  2. Unless the answer was *Proceed without the repos*: build the slug→clone map by Phase 3's recipe (cite it) and run the scan by KD §1 with `--exclude` the specs repository and `docs_repo_path`. No clone in the map → not run, *no clone resolved* (KD's own rule).
  3. Where the scan found a commit (a message match, or a commit a read pull request landed): no question; go on to step 4. Phase 3 will read it as any other.
  4. Otherwise print the lines and put **the nothing-built question**. The lines, in this order: the record (`<path>` holds no `/implement` block — or does not exist), with R3's move clause where the PRD folder's record holds a block on an Epic-focused run; the scan — per repository `<slug>: <scanned> commits on HEAD as the clone stands, unfetched; none names <tokens>` (R5), or which of R4's four forms applies, each saying the scan **did not look** there and why; the probe's matches and the listed pull requests in the words Phase 3 already gives them; then one sentence: `Either nothing is built for <keys> yet, or it was built without the key in any commit message — the scan cannot tell which.` Then the array (Global Constraints), and: a free-text answer is mapped onto one of the two or the question is asked again.
  5. ***Stop*** ends the run as *Ending early* says every run-ending answer does. Its line: `Stopped at your answer: nothing in <docs_repo_path> was touched.` followed by what to run — on an Epic-focused run `'/dev-workflows:implement <EPIC>'` where that Epic's `specification.md` and `design.md` are on the default branch, and otherwise what its first missing document needs; on a PRD run `'/dev-workflows:implement <PRD>'` where a unit that run would build has both, and otherwise, for each Epic — the PRD folder itself where it has no Epic folder — `<UNIT>: ` and what its first missing document needs (R2). State once how a document's state is read here — this command gates none: as `ready.md`'s `SUPPORTED` offer words it (the `cat-file -e "<default-ref>:./<path>"` test, a plugin branch by §3.2's read-only primitives, the folder, or nowhere; the folder's own file on a specs tree that is no git repository, `$SPECS_PATH` unset on an `@<path>` run included) — and cite PH §4.4 for what each state names, R3's move clause, and then `then re-run '/docs-workflows:document <ADDRESS>'`.
  6. ***Go on*** sets `nothing_built_answer` and continues to step 4; say here that Phase 9's report and Phase 8.5's draft record it (Task 2 writes those).

- [ ] **Step 4: *Ending early*, Readiness, KD.** *Ending early* names the repositories question's *Cancel* where Phase 0 put it, and the nothing-built question's *Stop*. The Readiness table gains a row for the record and the early scan. KD §1 says the scan runs in `/document`'s Phase 0 on a run whose record holds no block and in Phase 3 otherwise, and that its JSON file is removed once Phase 3 has taken what it needs (R7).

- [ ] **Step 5: Verify.** Fill the walk table's last two columns from the text as written; every row must match, or the text is wrong. Run:
  ```bash
  ./scripts/check-docs.sh --root . && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --root . --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/validate-catalog.py
  ```
  Expected: exit 0 (check-docs will require the page to follow where it checks one — if a check fails only for a page Task 3 owns, say which check and leave it failing for Task 3, never weaken it). `grep -c 'gate' ` on the new paragraphs: the question is nowhere called a gate.

- [ ] **Step 6: Commit** — `feat: LADDER-ORDER batch 3 — /document reads the record in Phase 0 and asks where nothing is built`.

### Task 2: `document.md`'s later phases follow

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md` — Phase 1's opening rule and repositories bullet (DOC:340, :350–355); Phase 2's `Repos:` line and *Revise* (DOC:425, :437); Phase 3's map and two steps (DOC:450–495); Phase 4 (DOC:531, :537, :548); Phase 5's aggregate gate (DOC:608–611); Phase 8.5's `pr-draft.md` (about DOC:1318); Phase 9's report template (`### Repos analysed`, `### Branch-name probe`, `### Assumptions & limitations`, about DOC:1390–1488); `## Invariants` (the `mktemp` list, about DOC:1594); the frontmatter description (DOC:3) only if it is made false.
- Modify: `plugins/docs-workflows/references/key-discovery.md` (KD:19, KD:27).
- Modify: the population file — rows P-1 to P-28, P-44 to P-47, and `## Task 2 walks`.

**Interfaces:**
- Consumes: Task 1's four names, verbatim.
- Produces: nothing later tasks build on, beyond the wording of "the repositories question, put in Phase 0 on a run whose record holds no block, and otherwise in Phase 1", which Task 3's copies repeat.

- [ ] **Step 1: Walk table first**, `## Task 2 walks`: Task 1's states (a), (c), (d)+*Go on*, (i) each answer, (j), plus: *Revise plan* names a base after *Proceed without the repos* in Phase 0 and the re-scan finds a commit; the same and it finds none (nothing is asked again); *Revise plan* names no base; a *Go on* run reaching Phase 5 with zero refs (R6: no aggregate gate); a run with a block and every ref unresolved (the aggregate gate is put, as today); the report and `pr-draft.md` of a *Go on* run; the report of a run that was never asked (no new line).
- [ ] **Step 2: Phase 1 and Phase 2.** Phase 1's bullet says the repositories question is put here only where Phase 0 did not put it. Each "Phase 1 took *Proceed without the repos*" sentence (DOC:425's `Repos:` line with its `(Phase 1)`, DOC:548, DOC:608) reads "the repositories question took …", true of both homes. *Revise*: where a named base replaces `$REPOS_PATH` or undoes *Proceed without the repos* on a run whose `early_scan` is set, rebuild the map and re-run the scan once over it; a commit found is read as any other; none found asks nothing (R7).
- [ ] **Step 3: Phase 3 and Phase 4.** Phase 3 builds the map "here, once" **unless Phase 0 built it** and reads the record and runs the scan **unless Phase 0 did** — then it takes `record_blocks` and `early_scan`'s result and prints the scan's reach, probe and pull requests once (not twice: where the lines above the question printed them, Phase 3 says so in one line). DOC:531's "never built twice" stays true; DOC:537's "earliest point the repo set is known" is corrected.
- [ ] **Step 4: Phase 5's aggregate gate** — put only where at least one ref was in scope (R6).
- [ ] **Step 5: The record of *Go on*** (R8) in Phase 9's `### Assumptions & limitations` and in `pr-draft.md`'s body, each only where `nothing_built_answer` is `go-on`; Phase 9's scan sections say which phase ran the scan.
- [ ] **Step 6: Invariants and KD.** The `mktemp` list names the scan's JSON file and its life; KD:19 and KD:27 follow (the repositories question's two homes; the *Revise plan* re-scan).
- [ ] **Step 7: Verify** — the walks; the same gate chain as Task 1; count `Phase 1 took` (expect 0 outside changelogs) and `the repositories question` (list the sites).
- [ ] **Step 8: Commit** — `feat: LADDER-ORDER batch 3 — /document's later phases reuse Phase 0's scan and record the answer`.

### Task 3: Pages, shared references, rules, rationale

**Files:**
- Modify: `plugins/docs-workflows/docs/commands/document.md` (*What it needs*, the mermaid diagram if a node is added — quote labels holding `[ ] ( ) { } | #`, the `:64` sentence, and a short section on the question: what triggers it, what the two answers do, what *Stop* names); `plugins/docs-workflows/docs/getting-started.md:114` if made false; `plugins/docs-workflows/docs/reference/environment.md:42` (R4).
- Modify: `plugins/workflows-core/references/escalation-rules.md:258–259` (where `/document` puts the repositories question) and regenerate; `plugins/workflows-core/references/implementation-format.md` (its reader list, IF:7–15, and IF:89–94 — an Epic-level `/document` on a moved-block Epic is asked); `plugins/workflows-core/references/document-lineage.md:101` ("which describe work already built" — true save a `/document` run answered *Go on*).
- Modify: `plugins/dev-workflows/docs/reference/commit-convention.md:21–22`.
- Modify: `.claude/rules/docs-workflows.md` — the `/document (keyed)` map line (P-49). The file has 14 characters to spare: make room by tightening the same line, or by moving one self-contained paragraph to `.claude/rules/docs-workflows-gates.md` (same `paths:`), itemised line by line as `workflows-core:instruction-file-maintenance` requires of a move; never by a new rules file (it would cost `CLAUDE.md` a table row it has no room for).
- Modify: `docs/maintainers/rationale.md` — `## ladder-order` gains batch 3's paragraph: M6 and why it asks rather than stops; R1 (why after the docs repository); R2; R4; what was refused.
- Modify: the population file — rows P-29 to P-43, P-48 to P-65, P-68 to P-71.

**Interfaces:** Consumes Tasks 1–2's wording, quoted from the command, never paraphrased into a different claim (the pages' facts are derived from the command, `CLAUDE.md` § Hard constraints).

- [ ] **Step 1:** For each population row marked **I** or **F** in this task's range, rewrite the sentence against the command as Tasks 1–2 left it; for each marked **T**, re-read it against the new text and record "stays true — checked" or correct it.
- [ ] **Step 2:** Run the claim sweep by subject (the implementation record; the commit scan; `REPOS_PATH`; "nothing built" / "not built" / "no implementation") over the sweep scope for a statement the population missed; add a row for each found.
- [ ] **Step 3: Verify** — the full gate chain of Task 1 plus `node scripts/mermaid/check-mermaid.mjs --root .`; budgets measured and stated.
- [ ] **Step 4: Commit** — `docs: LADDER-ORDER batch 3 — pages, shared references and rules follow /document's question`.

### Task 4: `/release-notes`' two offers

**Files:**
- Modify: `plugins/docs-workflows/commands/release-notes.md` — the `### Next step` template (RN:759–760) and the paragraph that loads `next-phase-offer` (about RN:773).
- Modify: `plugins/product-workflows/docs/workflow.md:48–49` (both edges' labels; mermaid gate).
- Modify: `plugins/workflows-core/references/next-phase-offer.md` — the Dev lane's `/docs-workflows:release-notes` line (about NPO:397), only if it states the offers unconditionally; regenerate.
- Modify: the population file — P-59, P-66, P-67, and `## Task 4 walks`.

**Interfaces:** Consumes PH §4.4 (the `prd.md` rung and its landing), NPO's *`/epics` precondition*, and `scan.md`'s two sentences (its PRD test on `<specs-default-ref>`; its not-landed line) as the model.

- [ ] **Step 1: Walks first**: `prd.md` on the default branch, `kind: prd` → both offers as today; on the default branch with no `kind: prd` → `/create-ard` offered, `/epics` replaced as the precondition says; in the folder and on no ref → the landing named, neither run offered; on an unmerged `prd/` branch with a pull request open → the merge named; a specs tree that is no git repository → the folder's file decides; `$SPECS_PATH` unset on an `@<path>` run; a BRD-route slice holding no `prd.md` cannot reach here (`RELEASE_NOTES_NO_PRD`) — confirm and say so.
- [ ] **Step 2:** Write the condition and the not-landed sentence (R10); say how the state is read (this command gates nothing).
- [ ] **Step 3: Verify** — walks; gate chain; mermaid gate.
- [ ] **Step 4: Commit** — `fix: LADDER-ORDER batch 3 — /release-notes offers /create-ard and /epics only for a landed PRD`.

### Task 5: Release

**Files:** the four `plugin.json` files and `.claude-plugin/marketplace.json` (R11); four `CHANGELOG.md` sections dated the day of the release commit; `.claude/rules/plugin-updates-coupling.md` (one bullet; measure the file; move older bullets to a history file only if it would reach 20,000, as the file's own header says); `docs/superpowers/to-test-on-real-project.md` (a batch 3 section: one live check per Review Focus line and per walk state that a gate cannot exercise); `docs/superpowers/to-fix.md` (the LADDER-ORDER entry: batch 3 built, batch 4 open); the design — §5.3 amended to R1–R10 in a dated *Settled while building* note, §5.5's Batch 3 list marked built, with anything found for batch 4.

- [ ] **Step 1:** `git fetch origin` and merge `origin/main` if it moved (a reviewed step: re-run the chain).
- [ ] **Step 2:** Versions, changelogs (each line true of the text — quote the command), coupling bullet, live checks, to-fix, design.
- [ ] **Step 3:** The full CI chain — every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain — exit 0; `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .` exit 0; `python3 scripts/validate-catalog.py` 0 errors, 0 warnings.
- [ ] **Step 4: Commit** — `release: LADDER-ORDER batch 3 — docs-workflows 1.40.0, workflows-core 1.94.1, product-workflows 3.83.2, dev-workflows 4.68.1`.

### Task 6: Close-out records (after the final review and its fix wave)

**Files:** Create `docs/superpowers/verification/2026-11-16-ladder-order-b3.md` (every value re-derived on the final tree, written last), `-rulings.md` (one row per ledger `Ruling` line, R1–R11 among the plan's own), `-ledger.md` (the ledger verbatim).

- [ ] **Step 1:** Write the three, the verification record last; run the gates that read them; commit — `docs: LADDER-ORDER batch 3 — the verification record, the rulings and the ledger`.

# `/conformance`, Plan 2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The two readers of `_conformance.md` that Plan 1 left out.
- **`/dev-workflows:ready`** derives an optional *Delivery verified* stage from the PRD's settled record.
- **`/docs-workflows:document`** takes a decision a record already holds instead of asking the PE again.
- **`workflows-core:source-truth`** states, once, how a recorded decision maps to a documentation decision.

**Architecture:**
- **The rung (D17, amendments A1–A6).**
  - `dev-workflows:workflow-states` gains an optional rung and a rule that an optional rung is passed over, never counted as a straddle.
  - `/ready` reads the PRD record from `<default-ref>` with `git show`, tests it against A1, and writes a `Delivery:` line. That line is a note, never a finding.
  - `/conformance` writes the two coverage lines A1 tests (`Not traced:`, `Not shown merged:`).
- **The reader (D18, A7–A12).**
  - `source-truth` gains §7.8, the one authority on records, open entries, precedence, mapping and drift.
  - `/release-notes` keeps its D42 behaviour but cites §7.8 instead of its own copy.
  - `doc-planner` returns the requirement each warning is about.
  - `/document` Phase 5.8 decides matched claims from §7.8 and asks only the rest.
- **No git machinery changes.** Another session (GIT-G1) is rewriting every command's Phase 0 preflight, terminal `commit-artifacts`, handover phase, `require-on-main`/`branch-check` call sites and **Ending early.** paragraph. Plan 2 edits none of those sections (Global Constraints).

**Tech Stack:** Markdown prose executed by agents; git; bash; python3 (the gates and `check.py`); node (the mermaid gate, CI only on this machine).

**Spec:** `docs/superpowers/specs/2026-10-12-conformance-design.md`: D17, D18, D21 and D22 as they bear on those, and **the *Plan 2 amendments (2026-11-08)* table, A1–A12, which wins where it differs.** Executors read both.

## Global Constraints

- **Prose is executed.** Every sentence added to a command, agent or reference must be true of what the run does.
- **Load rules before editing an area.** Read (with the Read tool) one file in each area first:
  - `.claude/rules/dev-workflows.md` and `workflows-core.md`
  - `docs-workflows.md` and `release-notes.md`
  - `gates-mermaid.md` and `claim-sweep.md`
- **Do not edit GIT-G1's sections** in `plugins/dev-workflows/commands/ready.md`, `plugins/docs-workflows/commands/document.md`, `plugins/docs-workflows/commands/release-notes.md` or `plugins/dev-workflows/commands/conformance.md`:
  - the **Ending early.** paragraph;
  - the Phase 0 `specs-preflight` text, and any slice re-entry preflight;
  - every `require-on-main` and `branch-check` call site;
  - the handover phase (the `handoff-to-main` call, its consent array, its outcome line and its `body_facts`);
  - the terminal `commit-artifacts` step;
  - the invariants that restate those.

  Plan 2 adds no stop, no question, no `require-on-main` and no branch probe. A change that would need one goes to the maintainer first.
- **IDs:** `[DD#n]`, cited as `<KEY>/[DD#n]`. Never a dash form (`check-id-grammar.sh`).
- **User pages** (`plugins/*/docs/**`):
  - Claims come from the command that runs them.
  - No review ids, D-numbers, version history or `§` citations into references (check 25).
  - No link leaves the plugin.
  - Quote any mermaid label holding `[ ] ( ) { } |` or `#`.
- **Generated files:** after editing `next-phase-offer.md`, regenerate `plugins/workflows-core/reference-parts/` as `.claude/rules/gates-reference-parts.md` says. Never hand-edit a part.
- **Counts** in `CLAUDE.md` and `.claude/rules/` are re-derived with their recipe, never incremented by hand.
- **Git:** verify `git branch --show-current` is `feat/conformance-plan-2` immediately before every commit, and never use bare `git stash`. Every commit message ends with:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01EcAVqApJxfCBcAbv5iWuu7`
- **Release:** bump each touched plugin's version in both `plugin.json` and `marketplace.json`, to the next free number on `origin/main` at merge time. Date every CHANGELOG section. Add a coupling bullet to `.claude/rules/plugin-updates-coupling.md`.

## Review Focus

1. **A record written before A3** (no `Not traced:` / `Not shown merged:` lines). `/ready` must not read the missing lines as `none`. The rung is not reached, and the note says the record predates the coverage lines and to re-run `/dev-workflows:conformance <PRD>`. *Task 2.*
2. **A record that exists only on an unmerged `conformance/` branch,** or in the working tree but not on `<default-ref>`. `/ready` treats it as no record and says it is not on `<default-ref>`. `/document` reads the working tree (A8), so it may still use it, and its report says the record was read from the working tree. *Tasks 2, 4.*
3. **The same requirement id at two levels** (a PRD-level `[U01]` and an Epic's `[U01]`, or `[AC03]` under two stories). A9's identity includes the record's key and document, so `/document` never applies one to the other. A claim that matches two entries of equal standing takes §7.8's precedence, not the first found. *Tasks 3, 4.*
4. **A record whose `Code checked:` names a repository with no local clone.** `/document`'s moved-past line says "not measured" for that repository, and the decision still applies. *Task 4.*
5. **An unreadable or malformed record:**
   - `/ready` treats it as no record, with the note `record unreadable`, and never stops.
   - `/document` prints one ⚠ line and asks as today.

   *Tasks 2, 4.*

---

### Task 0: Workspace, helper, RED

**Files:** Create (scratch, never committed): `$S/check.py`, from Appendix A.

**Interfaces:** Produces `$AW` (the worktree), `$S` (scratch), `$PLAN` and `python3 $S/check.py $AW <group|all>`, which prints `FAIL <assertion>` per failure, then `<group>: N passed, M failed`. The groups are `format rung truth document docs tiers release all`.

- [ ] **Step 1: Set the variables.**

```bash
AW=/home/ihudak/dev/ai-tools/ai-workflows-wt/conformance-plan-2
S=/tmp/claude-1000/-home-ihudak-dev-ai-tools-ai-workflows/38f385e9-773a-4d2b-8724-00a58fb802ee/scratchpad/conformance-2
PLAN=$AW/docs/superpowers/plans/2026-11-08-conformance-plan-2.md
mkdir -p "$S"
```

- [ ] **Step 2: Extract `check.py`.**

```bash
python3 - "$PLAN" "$S/check.py" <<'EOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"#### `check.py`\n\n````python\n(.*?)\n````", t, re.S)
open(sys.argv[2], "w", encoding="utf-8").write(m.group(1) + "\n"); print("ok")
EOF
```
Expected: `ok`.

- [ ] **Step 3: Confirm the tree, then merge main.**

```bash
cd "$AW"
test "$(git branch --show-current)" = feat/conformance-plan-2 && test -z "$(git status --porcelain)" && echo CLEAN
git fetch -q origin && git merge --no-edit origin/main
```
Expected: `CLEAN`, then `Already up to date.` or a clean merge. On a conflict, keep main's side of any GIT-G1 section and stop for the maintainer.

- [ ] **Step 4: RED.** Run `python3 "$S/check.py" "$AW" all | tail -1`.
  - Expected: `all: 6 passed, 49 failed`. The six that pass are the release group's version and dated-heading checks, which hold on today's tree.
  - Record the total, 55. Each later task turns its own group green.

---

### Task 1: The record's coverage lines (`format`)

**Files:**
- Modify: `plugins/dev-workflows/references/conformance-format.md` (§2's header block and the prose after it; §6).
- Modify: `plugins/dev-workflows/commands/conformance.md`: Phase 5's record write, and Phase 7's `### Scope` lines *Traced where not shown merged* and *Not traced*. Leave Phase 6 and Phase 9 alone (GIT-G1's).

**Interfaces:** Produces two header lines that Task 2 tests, written exactly:
- `- **Not traced:** none`, or `- **Not traced:** <n> requirement(s) — <each document not read; each repository with no clone or no default branch>`
- `- **Not shown merged:** none`, or `- **Not shown merged:** <EPIC-KEY>, one per Epic traced under Phase 1 (c)'s *Trace anyway*`

An Epic run writes `none` on the second line. Both go after `Code checked:`.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" format`. Expected: all FAIL.
- [ ] **Step 2: §2.** Add the two lines to the header block and one sentence after it:
  - They hold what the report's *Scope* lines say.
  - A re-run rewrites them like the rest of the header.
  - A record without them predates them, and a reader must not take their absence as `none`.
- [ ] **Step 3: §6.** Replace "Which reader maps which decision to what is its own reference's to say." Readers now take the mapping, the open-entry rules and the precedence from `workflows-core:source-truth` §7.8.
  - Name the three readers: `/docs-workflows:release-notes` (unchanged paragraph), `/docs-workflows:document` (its Phase 5.8) and `/dev-workflows:ready` (§2's `Run:`, `Not traced:` and `Not shown merged:` lines, `## Unverified`, and each entry's `decision:`, `status:`, `flags:` and `lists:`).
  - Keep the paragraph's "cannot load this reference" framing for the docs-workflows readers.
- [ ] **Step 4: `conformance.md` Phase 5.** Where the record's header is written, say it writes both lines from the same facts Phase 7's *Scope* lines report.
- [ ] **Step 5: GREEN.** `python3 "$S/check.py" "$AW" format`. Expected: `format: 6 passed, 0 failed`.
- [ ] **Step 6: Commit** (`feat(dev-workflows): the conformance record carries its coverage — Not traced and Not shown merged (Plan 2, A3)`).

---

### Task 2: The rung (`rung`)

**Files:**
- Modify `plugins/dev-workflows/references/workflow-states.md`:
  - the ladder line and a new table row after *Implementation*;
  - a new **An optional rung** paragraph;
  - the advisory paragraph, at its "downgrades to a MINOR finding" sentence.
- Modify `plugins/dev-workflows/commands/ready.md`:
  - a new Phase 1 step 2b after step 2a;
  - Phase 2's "only input the *derivation* takes" sentence;
  - Phase 3(0) and 3(b);
  - the Phase 4 brief;
  - the `_readiness.md` template;
  - the report and its `### Next step`;
  - one Invariants bullet.
- Modify `plugins/dev-workflows/agents/readiness-reviewer.md`: Inputs, and dimension 1.
- Modify `plugins/workflows-core/references/next-phase-offer.md`: `/dev-workflows:ready`'s line in the Dev lane. Regenerate `reference-parts/next-phase-offer/*`.

**Interfaces:**
- Consumes Task 1's two header lines.
- Produces:
  - the `_readiness.md` line `- Delivery: verified — <PRD-KEY>/_conformance.md on <default-ref>` or `- Delivery: not verified — <reason>`;
  - the reviewer brief line `delivery: <that line's text after "- Delivery: ">`;
  - the rung name `Delivery verified (optional)`.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" rung`. Expected: all FAIL.
- [ ] **Step 2: `workflow-states.md`.**
  - The ladder becomes `Open → Problem stated → Usecases defined → Ready for Implementation → Implementation → Delivery verified (optional) → Release Preparation → Post GA`.
  - The new row: `| Delivery verified (optional) | PE | /conformance | the PRD's _conformance.md on the default branch, settled — /dev-workflows:ready states the test |`, with backticks as the table's other rows use them.
  - The **An optional rung** paragraph says:
    - it is reached only where its artifact is present and settled;
    - otherwise it is passed over: never a straddle, never a finding, and the derivation continues as though it did not exist;
    - the run carries a note instead (`delivery not verified`).
  - The advisory paragraph's MINOR rule excepts it.
- [ ] **Step 3: `ready.md` Phase 1 step 2b, *Read the delivery record — PRD only, report it, never ask.***
  - **The read:** `git -C "$SPECS_PATH" show "<default-ref>:./<PRD-dir>/_conformance.md"`, `<default-ref>` being the ref step 2 already uses.
  - **No git or no `<default-ref>`:** `not verified — no ref to confirm the record on`.
  - **A failed read:** `not verified — no conformance record on <default-ref>`.
  - **A read that does not parse:** `not verified — record unreadable`.
  - **The test:** A1, verbatim in substance:
    - the `Run:` line says `PRD`;
    - both coverage lines are present and read `none`;
    - `## Unverified` is empty;
    - every entry is `final` or `resolved`, apart from entries that only list an Epic entry flagged `orphaned` or `requirement withdrawn`;
    - no `fix-code` entry is non-`resolved`, with the same exception.
  - **The reason, where the test fails,** names the first failing condition in that order. Where open entries remain, it lists each `<PRD-KEY>/[DD#n]`. A missing coverage line gives `record predates its coverage lines — re-run /dev-workflows:conformance <PRD>`.
  - **What the step records:** `delivery: {state: verified|not-verified, line}`. It adds no stop and no question.
- [ ] **Step 4: Phase 2 and Phase 3.**
  - Rewrite the "it is the only input the *derivation* takes" sentence. The inventory remains the input for every mandatory rung; `delivery` decides the optional one.
  - In 3(0), the rung sits above *Implementation*. It is reached only on a PRD derived at *Implementation* whose `delivery.state` is `verified`, and is passed over otherwise (Task 2 step 2's rule).
  - In 3(b), list *Delivery verified* as ✅ or as a note, never ❌.
- [ ] **Step 5: Phase 4 brief, `_readiness.md`, report, Next step, Invariants.**
  - Add `delivery:` to the brief.
  - Add `- Delivery:` after `- Derived phase:` in the template.
  - Print the line in the report.
  - In `### Next step`, where the PRD is derived at *Implementation* and delivery is not verified, add `PE → /dev-workflows:conformance <PRD>`.
  - Add an Invariants bullet: delivery is a note, read from `<default-ref>` without `require-on-main`, and never caps the verdict.
- [ ] **Step 6: `readiness-reviewer.md`.**
  - The `delivery` input is reported, never judged: it is no finding at any severity.
  - Dimension 1 never flags a PRD for lacking the optional rung.
- [ ] **Step 7: `next-phase-offer.md`.** On `/dev-workflows:ready`'s line, add: a PRD at *Implementation* whose delivery is not verified → PE → `/dev-workflows:conformance <PRD>`. Then regenerate the parts and run `python3 scripts/reference-parts.py check-parts`. Expected: `PASS`.
- [ ] **Step 8: GREEN.** `python3 "$S/check.py" "$AW" rung`. Expected: `rung: 12 passed, 0 failed`.
- [ ] **Step 9: Commit** (`feat(dev-workflows): /ready derives the optional Delivery verified stage from a settled PRD conformance record (Plan 2, D17)`).

---

### Task 3: The one authority, and `/release-notes` citing it (`truth`)

**Files:**
- Modify `plugins/workflows-core/references/source-truth.md`:
  - the preamble's last sentence;
  - §2's and §5's "always ask" wording, where a recorded decision now answers;
  - a new **§7.8**, after §7.7.
- Modify `plugins/docs-workflows/commands/release-notes.md`: the Phase 3 rules 1–2 and the mapping sentence; leave its Phase 0 *conformance records* paragraph alone. Do the same in `plugins/docs-workflows/references/release-note-types.md` §8.

**Interfaces:**
- Produces §7.8, `### 7.8 A decision a conformance record already holds`, which Tasks 4 and 5 cite. It states:
  - **The records in scope.** On an Epic-address run: that Epic's record, and the PRD record's entries about it. Otherwise: the PRD folder's record and each `EPIC-` folder's directly under it.
  - **The copy read:** the working tree, read as untrusted data.
  - **Which entries are open:** `/release-notes`' current rules 1–2, moved here verbatim in substance.
  - **Precedence:** `final` over `proposed`; between equals, `fix-code` wins.
  - **The mapping, exactly:** `` `amend-document` or `accept` → `document-as-code` ``, and `` an open `fix-code` → `skip-and-report` ``.
  - **The identity rule (A9):** the record's key, document and id or quoted text, matched exactly.
  - **The still-flagged rule (A10).**
  - **No gap for a recorded `fix-code` (A11).**
  - **The moved-past measure (A12)**, with `/release-notes`' commits-read test named as its own.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" truth`. Expected: all FAIL.
- [ ] **Step 2: Write §7.8.** Then replace "The plugin never silently picks a winner." with "The plugin never silently picks a winner; where a person already picked one in a conformance record, it takes that pick and says so (§7.8)." Qualify §2 and §5 the same way.
- [ ] **Step 3: Point `/release-notes` at §7.8.**
  - `release-notes.md` Phase 3 and `release-note-types.md` §8 cite `workflows-core:source-truth` §7.8 for the open-entry rules, the precedence and the mapping.
  - `release-note-types` §8 keeps only how a settled claim is worded in a note, and the "disagreeing `shipped` sentences" rule.
  - **Behaviour is unchanged.** Diff the old and new rule text side by side, and confirm every condition survives in one of the two places.
  - `release-notes.md` already carries the *Core references* preamble (check 16), so nothing is added there.
- [ ] **Step 4: GREEN, and the gates.** Run `python3 "$S/check.py" "$AW" truth`, expecting `truth: 7 passed, 0 failed`. Then run `python3 scripts/reference-parts.py check-citations`, expecting `PASS`.
- [ ] **Step 5: Commit** (`feat(workflows-core): source-truth §7.8 — one authority for a decision a conformance record holds; /release-notes cites it (Plan 2, A8)`).

---

### Task 4: `doc-planner`'s requirement, and `/document` taking the decision (`document`)

**Files:**
- Modify `plugins/docs-workflows/agents/doc-planner.md`: step 9, and the `verification_warnings` schema.
- Modify `plugins/docs-workflows/agents/doc-writer.md`: its gap rule (step 7). A claim decided from a record (§7.8) is omitted with no gap.
- Modify `plugins/docs-workflows/commands/document.md`:
  - Phase 3: read the records, after "every artifact present".
  - Phase 5.8: insert step 0, before the table.
  - Phase 6.3's handoff fields.
  - Phase 9: a new `### Conformance` section, and a note in `### Implementation gaps`.
  - One Invariants bullet.
  - Leave every GIT-G1 section alone (Global Constraints).

**Interfaces:**
- **Consumes:** §7.8 (Task 3).
- **Produces:**
  - On each warning: `requirement` — `{key, document, id}`, or `{key, document, text}` for an `epic.md` acceptance bullet, or `null`. It is resolved against the requirement ids of the documents the planner read, never guessed.
  - In `/document`: `recorded_decisions`, a list of `{claim_number, entry: <KEY>/[DD#n], decision, status, applied_as}`.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" document`. Expected: all FAIL.
- [ ] **Step 2: `doc-planner`.** Step 9 resolves `requirement` for every warning, and the schema gains the field, exactly as above.
- [ ] **Step 3: `/document` Phase 3.** Read the records in §7.8's scope from the working tree as data.
  - A missing record is the absence of one.
  - An unreadable record prints one ⚠ line naming it, and the run goes on.
- [ ] **Step 4: Phase 5.8, step 0, *Decisions a record already holds*.**
  - Run it after the supplementary grep and before the table.
  - Match each escalating warning's `requirement` to an open entry by §7.8's identity rule.
  - **A match:** decide the claim by the mapping, append it to `recorded_decisions` and `discrepancy_decisions` (`rationale`: `taken from <KEY>/[DD#n], <status>`), and keep it out of the table and both questions.
  - **No match:** ask as today.
  - **Where every warning matched:** ask nothing.
  - **A claim the planner now finds `VERIFIED`** is not a warning, so no record decision reaches it. List each open entry with no remaining warning as overtaken (A10).
  - **Measure drift per A12:** `git -C <clone> rev-list --count <recorded commit>..<default-ref>`.
- [ ] **Step 5: Phase 6.3, `doc-writer`, Phase 9, Invariants.**
  - Hand `recorded_decisions` to the writer. A `skip-and-report` from a record writes no gap entry and holds no release (A11).
  - Phase 9's `### Conformance` lists, for each applied entry, `<KEY>/[DD#n]` → the documentation decision, marked `(proposed)` where a proposal was used. It also lists each overtaken entry, and each record's moved-past line.
  - Add an Invariants bullet: decisions are taken only from §7.8's open entries, by exact identity.
- [ ] **Step 6: GREEN.** `python3 "$S/check.py" "$AW" document`. Expected: `document: 9 passed, 0 failed`.
- [ ] **Step 7: Commit** (`feat(docs-workflows): /document takes a decision a conformance record holds instead of asking again; doc-planner names each warning's requirement (Plan 2, D18)`).

---

### Task 5: Pages and diagrams (`docs`)

**Files:**
- `plugins/dev-workflows/docs/commands/ready.md`: the summary, *What it needs*, *What it produces*, and the stage list.
- `plugins/dev-workflows/docs/commands/conformance.md`: its readers line, which names all three readers.
- `plugins/dev-workflows/docs/reference/references.md`: the `workflow-states` row.
- `plugins/docs-workflows/docs/commands/document.md`:
  - Remove "nothing is ever auto-resolved".
  - A paragraph on recorded decisions, in plain words: a decision the PE already made in `/conformance` is taken without asking and named in the report.
- `plugins/docs-workflows/docs/commands/release-notes.md`: only if a sentence there now misstates what it reads.
- `plugins/docs-workflows/docs/workflow.md`: a dashed edge from `conformanceprd` to `document`, and to the page's dev-stage release-notes node, both labelled `"_conformance.md — recorded decisions, taken without asking"`. Update the prose that describes the PRD conformance node's role.
- `plugins/dev-workflows/docs/workflow.md` and `plugins/workflows-core/docs/family-map.md`: a dashed edge `conformanceprd -.->|"_conformance.md — the optional Delivery verified stage"| ready`, using each page's own node ids.
- `plugins/workflows-core/docs/reference/references.md`: the `source-truth` row mentions recorded decisions.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" docs`. Expected: all FAIL.
- [ ] **Step 2: Write each page from the command text Tasks 1–4 left,** never from this plan's wording. No `§`, no amendment ids.
  - D22's "the ladder, wherever a page draws it" reaches no page today. Re-check that before writing: `git grep -n -E 'Release Preparation|Post GA' -- 'plugins/*/docs/**'` should return nothing. Any page it does return gains *Delivery verified (optional)* in its ladder.
- [ ] **Step 3: GREEN, and the docs gate.** Run `python3 "$S/check.py" "$AW" docs`, expecting `docs: 8 passed, 0 failed`. Then run `./scripts/check-docs.sh --root .`, expecting `PASS`.
- [ ] **Step 4: Commit** (`docs: /ready's Delivery verified stage and /document's recorded decisions on the user pages and diagrams (Plan 2, D21–D22)`).

---

### Task 6: Instruction tiers and records (`tiers`)

**Files:**
- `.claude/rules/dev-workflows.md`: `/ready`'s map line and its invariant. Name the optional rung, the record read from `<default-ref>`, and the note.
- `.claude/rules/docs-workflows.md`: the Phase 5.8 invariant ("(never auto-resolved)") and the `/document` map line.
- `.claude/rules/workflows-core.md`: the `source-truth` authority paragraph names §7.8.
- `.claude/rules/release-notes.md`: where it says the mapping is `release-note-types`' own.
- `docs/superpowers/to-fix.md`: a new entry, **D49 — gap: `/ready` cannot derive *Release Preparation***. Cite A5 and say what deriving it would need: a documentation signal it can read, and a dev-stage release-notes marker. D49 is the next free D-number; re-derive it before writing.
- `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`: append `— **Done in <versions> (/conformance Plan 2)**` to the DEV-G1 and DEV-G2 headings.
- `docs/superpowers/reviews/2026-10-26-fix-batches.md` *Design tracks*: the same status on DEV-G1 and DEV-G2.

- [ ] **Step 1: Run the group, and confirm it fails.** `python3 "$S/check.py" "$AW" tiers`. Expected: all FAIL.
- [ ] **Step 2: Claim sweep (`.claude/rules/claim-sweep.md`).**
  - Sweep the subjects "nothing auto-resolved", "never auto-resolved", "always asks", the ladder's rung list, and "each reader's own reference".
  - Cover refinement 4's scope, and count each string before and after.
  - Every other copy that is now false is fixed in this task.
- [ ] **Step 3: GREEN.** `python3 "$S/check.py" "$AW" tiers`. Expected: `tiers: 6 passed, 0 failed`.
- [ ] **Step 4: Commit** (`docs: instruction tiers and records for /conformance Plan 2`).

---

### Task 7: Release and gates (`release`)

- [ ] **Step 1: Merge main.** `git fetch -q origin && git merge --no-edit origin/main`. Keep main's side of every GIT-G1 section. A conflict anywhere else is resolved by hand and re-checked with `check.py all`.
- [ ] **Step 2: Versions.**
  - Take the next free **minor** of `workflows-core`, `dev-workflows` and `docs-workflows` on `origin/main`, each a new capability. Write it in `plugin.json` and `marketplace.json`.
  - Add a dated CHANGELOG section to each, user-facing, with no amendment ids.
- [ ] **Step 3: Coupling bullet.** Update `workflows-core` <new> together with `dev-workflows` <new> and `docs-workflows` <new>.
  - Beside an older `workflows-core`, `/release-notes`, `/document` and `conformance-format` §6 cite a §7.8 it does not have, and `/ready`'s offer line is missing from the routing graph.
  - Beside older dependents, §7.8 names readers that do not read yet.
  - Count `plugin-updates-coupling.md`'s characters with Python `len`. If it passes 20,000, move its oldest bullets to the history file, as B34 did.
- [ ] **Step 4: GREEN everywhere.** `python3 "$S/check.py" "$AW" all | tail -1`. Expected: `all: 55 passed, 0 failed`.
- [ ] **Step 5: The gate chain.** Run every `run:` step of `.github/workflows/validate-catalog.yml` in order, as one `&&` chain: `scratchpad/run-gates.sh <worktree>` from the session that wrote this plan, or the steps by hand. Read the printed EXIT. Expected: `EXIT=0`. The mermaid gate runs in CI only on this machine.
- [ ] **Step 6: Commit** (`chore: release /conformance Plan 2 — versions, changelogs, coupling`).

### Task 8: Whole-branch review

- [ ] An independent Opus reviewer reads `git diff origin/main...HEAD` against the spec and A1–A12, with this plan's Review Focus as its checklist. It also checks that no GIT-G1 section changed: `git diff origin/main...HEAD -- <the four commands>`, with each hunk located outside those sections.
- [ ] Fix every finding in one pass, then have the same reviewer re-check (`superpowers:receiving-code-review`).

### Task 9: End-to-end on the bookstore demo (with the maintainer)

- [ ] This is the spec's Plan 2 verification. On the e2e copies, run `/dev-workflows:ready BOOK-1` before and after the PRD record settles. The `Delivery:` line goes from *not verified*, with its reason, to *verified*, and the verdict is unchanged.
- [ ] Run `/docs-workflows:document BOOK-1` with a settled `amend-document` entry on a planted claim. The claim is documented as shipped without a question, and `### Conformance` names the entry.
- [ ] Record both runs in `docs/superpowers/verification/2026-11-<dd>-conformance-plan-2.md`, written last (`CLAUDE.md` § Editing discipline).

### Task 10: Land

- [ ] Merge `origin/main` once more. Push. Open the PR only after Task 7's chain prints `EXIT=0` on the final commit, or say plainly in the PR that CI is still pending.
- [ ] Tell the GIT-G1 session (`Shipwright-7550`) which reader lists inside its sections now miss readers: `phase-handoff` §4.0's `_conformance.md` row and `conformance.md`'s handoff-phase readers sentence. Both should name `/ready`, `/document` and `/release-notes`. Plan 2 does not edit them.

---

## Appendix A — `check.py`

#### `check.py`

````python
#!/usr/bin/env python3
"""/conformance Plan 2: string assertions per task. Usage: check.py ROOT [GROUP|all]."""
import json, os, re, sys

ROOT, WANT = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "all")
R = []
norm = lambda s: re.sub(r"\s+", " ", s)

def read(p):
    try:
        return norm(open(os.path.join(ROOT, p), encoding="utf-8").read())
    except OSError:
        return None

def has(g, p, s):
    t = read(p); R.append((g, f"{p} has {s!r}", t is not None and norm(s) in t))

def hasnt(g, p, s):
    t = read(p); R.append((g, f"{p} lacks {s!r}", t is not None and norm(s) not in t))

DW, DOC, WC = "plugins/dev-workflows", "plugins/docs-workflows", "plugins/workflows-core"
FMT = f"{DW}/references/conformance-format.md"
# format (Task 1)
has("format", FMT, "- **Not traced:** none")
has("format", FMT, "- **Not shown merged:** none")
hasnt("format", FMT, "Which reader maps which decision to what is its own reference's to say")
has("format", FMT, "source-truth` §7.8")
has("format", FMT, "/dev-workflows:ready")
has("format", f"{DW}/commands/conformance.md", "Not shown merged:")
# rung (Task 2)
WS, RD = f"{DW}/references/workflow-states.md", f"{DW}/commands/ready.md"
has("rung", WS, "Implementation → Delivery verified (optional) → Release Preparation")
has("rung", WS, "| Delivery verified (optional) |")
has("rung", WS, "**An optional rung**")
has("rung", RD, "_conformance.md\"")
has("rung", RD, "- Delivery: verified")
has("rung", RD, "- Delivery: not verified")
has("rung", RD, "record predates its coverage lines")
has("rung", RD, "no ref to confirm the record on")
hasnt("rung", RD, "it is the only input the *derivation* takes")
has("rung", f"{DW}/agents/readiness-reviewer.md", "delivery:")
has("rung", f"{WC}/references/next-phase-offer.md", "whose delivery is not verified")
has("rung", f"{WC}/reference-parts/next-phase-offer/dev.md", "whose delivery is not verified")
# truth (Task 3)
ST = f"{WC}/references/source-truth.md"
has("truth", ST, "### 7.8 A decision a conformance record already holds")
has("truth", ST, "`amend-document` or `accept` → `document-as-code`")
has("truth", ST, "an open `fix-code` → `skip-and-report`")
has("truth", ST, "where a person already picked one in a conformance record, it takes that pick and says so (§7.8)")
hasnt("truth", ST, "The plugin never silently picks a winner.")
has("truth", f"{DOC}/commands/release-notes.md", "source-truth` §7.8")
has("truth", f"{DOC}/references/release-note-types.md", "source-truth` §7.8")
# document (Task 4)
DM = f"{DOC}/commands/document.md"
has("document", f"{DOC}/agents/doc-planner.md", "`requirement` — `{key, document, id}`")
has("document", f"{DOC}/agents/doc-writer.md", "§7.8")
has("document", DM, "source-truth` §7.8")
has("document", DM, "recorded_decisions")
has("document", DM, "### Conformance")
has("document", DM, "rev-list --count")
has("document", DM, "taken from <KEY>/[DD#n]")
has("document", DM, "overtaken")
has("document", DM, "not measured")
# docs (Task 5)
has("docs", f"{DW}/docs/commands/ready.md", "Delivery verified")
has("docs", f"{DW}/docs/commands/conformance.md", "/dev-workflows:ready")
hasnt("docs", f"{DOC}/docs/commands/document.md", "nothing is ever auto-resolved")
has("docs", f"{DOC}/docs/workflow.md", "\"_conformance.md — recorded decisions, taken without asking\"")
has("docs", f"{DW}/docs/workflow.md", "\"_conformance.md — the optional Delivery verified stage\"")
has("docs", f"{WC}/docs/family-map.md", "\"_conformance.md — the optional Delivery verified stage\"")
has("docs", f"{DW}/docs/reference/references.md", "Delivery verified")
has("docs", f"{WC}/docs/reference/references.md", "conformance record")
# tiers (Task 6)
has("tiers", ".claude/rules/dev-workflows.md", "Delivery verified")
hasnt("tiers", ".claude/rules/docs-workflows.md", "(never auto-resolved)")
has("tiers", ".claude/rules/workflows-core.md", "§7.8")
has("tiers", "docs/superpowers/to-fix.md", "D49 — gap: `/ready` cannot derive *Release Preparation*")
has("tiers", "docs/superpowers/reviews/2026-10-26-feature-gaps-review.md", "(/conformance Plan 2)**")
has("tiers", "docs/superpowers/reviews/2026-10-26-fix-batches.md", "(/conformance Plan 2)")
# release (Task 7)
mp = {p["name"]: p["version"] for p in json.load(open(os.path.join(ROOT, ".claude-plugin/marketplace.json")))["plugins"]}
for p in ("workflows-core", "dev-workflows", "docs-workflows"):
    v = json.load(open(os.path.join(ROOT, f"plugins/{p}/.claude-plugin/plugin.json")))["version"]
    R.append(("release", f"{p} plugin.json {v} == marketplace {mp[p]}", v == mp[p]))
    cl = open(os.path.join(ROOT, f"plugins/{p}/CHANGELOG.md"), encoding="utf-8").read()
    R.append(("release", f"{p} CHANGELOG has no undated heading", not re.search(r"(?m)^## .*— Unreleased", cl)))
has("release", ".claude/rules/plugin-updates-coupling.md", "§7.8")

sel = [r for r in R if WANT == "all" or r[0] == WANT]
for g, label, ok in sel:
    if not ok:
        print("FAIL", label)
print(f"{WANT}: {sum(ok for *_, ok in sel)} passed, {sum(not ok for *_, ok in sel)} failed")
````

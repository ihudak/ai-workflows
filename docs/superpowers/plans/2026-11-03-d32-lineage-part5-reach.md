# D32 Document Lineage (part 5, the altitude filter's reach) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An unchanged `/prd-ground` re-run reads as no move for any downstream, a real change still reaches the documents at its altitude, and part 4's six minors are fixed — closing D32.

**Architecture:** The `grounding` kind row gains four data fields that `_items` and `compare` honour — a per-section altitude, sections whose own text is dropped, bookkeeping fields ignored with their continuation lines, and an item set read from `baselines.md` and skipped. `check` reads an `--accepted-from` document from the ref when it is not on disk and refuses an unresolvable ref. Prose follows: the reference, `grounding-format`, `/prd-ground`'s matrix section, `/update-spec`'s diff, and the never-ask callers' templates.

**Tech Stack:** Python 3 standard library (`lineage.py`, its `--selftest`); git CLI; markdown prose.

**Spec:** `docs/superpowers/specs/2026-11-03-d32-lineage-part5-reach-design.md` (parts 1–4 bind under it).

## Global Constraints

- Worktree `$S/wt-d32e`, branch `feat/d32-lineage-reach`; `git branch --show-current` before every commit; the session's commit trailer; `git add -f` under `.claude/`.
- A baseline finding is identified only by `grounding/baselines.md`'s `finding:` ids at `<default-ref>`, never by its `claim`; a `baselines.md` missing, unreadable or with no ids excludes nothing.
- `## Derivation matrix` → `implementation`; `## Documentation divergences`, `## Frame sets covered` → text dropped, an item-start line inside still opens an item; `outcome` and `notes` → ignored with their continuation lines.
- The register's own link to the grounding stays unfiltered (it sees the matrix; it sees no baseline, dropped section or bookkeeping change).
- Versions: workflows-core 1.77.0, product-workflows 3.72.1, docs-workflows 1.32.1, dev-workflows 4.57.3 (from main's 1.76.0 / 3.72.0 / 1.32.0 / 4.57.2).
- Size limits: `CLAUDE.md` < 36,000 chars; each `.claude/rules/*.md` < 20,000 chars.

## Review Focus

1. **A grounding file in the real multi-run layout** — run 1's findings, `## Derivation matrix`, `## Documentation divergences`; run 2's findings appended after it, a second divergences section, the matrix section replaced with the same rows → no link for a specification or the register — `test_realistic_rerun_layout` (Task 1).
2. **A legacy file whose matrix rows sit after the last finding with no heading** → the first replacement reads as one change to that finding, once, at its altitude — `test_legacy_matrix_moves_once` (Task 1), and the CHANGELOG says so.
3. **A multi-line `notes:` whose continuation lines look like keys** (`  notes: |` then `    claim: …`) → all ignored; the next real key at the item's column is read — `test_multiline_notes_ignored` (Task 1).
4. **`baselines.md` naming an id whose block is a claim finding** (a malformed record) → that finding is skipped like a baseline — accepted, since the record is the authority; `test_baseline_set_is_the_record` (Task 1) pins it.
5. **`/update-spec` on a base whose grounding only re-pinned** → its change list names no grounding item — Task 4's grep on Phase 2's text.

---

### Task 1: The kind row and the comparison

**Files:** `plugins/workflows-core/scripts/lineage-kinds.json` (the `grounding` row; `_doc` names the four fields), `plugins/workflows-core/scripts/lineage.py` (`_items`, `compare`, `_link`, `check`'s call to `_link`; the tests).

**Interfaces:**
- Produces: kind-row fields `section_altitude: {heading text: altitude}`, `drop_sections: [heading text]`, `ignore_fields: [field name]`, `skip_items_in: {"file": "baselines.md", "field": "finding"}` (builder may rename; record the names in the ledger); `compare(kind, old_text, new_text, altitude=None, skip=frozenset())`; `_link(specs, doc, entry, up, cur, altitude=None, skip=frozenset())`; `_skip_set(specs, ref, up) -> frozenset` reading `<dirname(up)>/<file>` at `ref`, keys in the item form `"[CG#n]"`.

- [ ] **Step 1: Failing tests** in `lineage.py`: `test_unchanged_rerun_not_moved` (a spec and a register recording `code-grounding.md`; a re-run adds `[CG#2]` baseline, flips `[CG#1]` baseline to `verdict: SUPERSEDED` with a note, `outcome: agree`→`extend` on claim `[CG#3]`, `baselines.md` naming `[CG#1]` and `[CG#2]` → `check(...)["stale"] == []` for both); `test_claim_change_beside_rerun_reported` (same, plus `[CG#3]`'s claim text changed → `changed == ["[CG#3]"]`); `test_derivation_matrix_altitude` (a row in `## Derivation matrix` changed → stale for the spec and the register, none for an ARD recording the file); `test_dropped_sections_not_moved` (divergences and frame-sets text changed → no link for the register); `test_finding_after_dropped_section_counts` (`[CG#4]` appended after `## Documentation divergences`, no heading between → register stale, `added == ["[CG#4]"]`); `test_multiline_notes_ignored`; `test_baselines_absent_counts` (no `baselines.md` → the re-run reads stale, today's behaviour); `test_date_heading_not_moved` (a new empty `## 2026-11-04` in `design-grounding.md` → no link); `test_realistic_rerun_layout`; `test_legacy_matrix_moves_once`; `test_baseline_set_is_the_record`.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/lineage.py --selftest` → Expected: the first new test fails (selftest stops at the first failure; run each new test once by name through `python3 -c` to see each fail).
- [ ] **Step 3: Implement** the four fields in `_items`/`compare`/`_link`; `check` passes `skip=_skip_set(specs, ref, up)` where the upstream's kind row carries `skip_items_in`.
- [ ] **Step 4: Run** the selftest → Expected: `selftest: <39 + new> passed`.
- [ ] **Step 5: Commit** `feat(workflows-core): lineage — a grounding re-run reads as no move: baseline findings, notes sections and verification fields left out; the matrix at implementation altitude (D32 part 5)`.

### Task 2: `check` — the two script minors

**Files:** `plugins/workflows-core/scripts/lineage.py` (`check`, `_accepted_of` or a text variant; `main`'s error path).

- [ ] **Step 1: Failing tests:** `test_accepted_from_ref_only` (the acceptance is in a `design.md` committed on `main` and deleted from the working tree → the link is `accepted`, not stale); `test_unresolvable_ref_fails` (`check(..., ref="nope", ...)` raises `LineageError` whose message names `nope`; through `main`, exit non-zero with that line on stderr).
- [ ] **Step 2: Run** → both fail.
- [ ] **Step 3: Implement** — an `--output`/`--accepted-from` path missing on disk is read at `ref` (its path relative to `specs`); `check` verifies `<ref>^{commit}` first and raises `LineageError(f"no {ref} in {specs}")`.
- [ ] **Step 4: Run** the selftest → all pass.
- [ ] **Step 5: Commit** `fix(workflows-core): lineage check reads an acceptance at the ref and refuses an unresolvable ref (D32 part 5)`.

### Task 3: The reference and the format

**Files:** `plugins/workflows-core/references/document-lineage.md` — §2 (what counts: a baseline finding, a dropped section, `outcome`/`notes` never count for any downstream; the matrix at implementation; the register's link still sees the matrix), §6 step 6 (name `/document` and `/release-notes` for "those two"; each (downstream, upstream) pair listed and counted once, stale wherever any unit reports it, *accepted in this unit* only where every unit that met it accepted it; an unresolvable ref is a script failure), §7 (`Lineage: not checked — lineage.py failed: <first stderr line>`); `plugins/workflows-core/references/grounding-format.md` — §4.1 (lineage leaves baseline findings out, by `baselines.md`'s ids), §7 (the matrix sits under one `## Derivation matrix` heading, replaced by each run that writes one); `plugins/workflows-core/docs/reference/references.md` (the lineage bullet).

- [ ] **Step 1: Failing grep** — `grep -c 'lineage.py failed' document-lineage.md` → `0`; `grep -c '## Derivation matrix' grounding-format.md` → `0`.
- [ ] **Step 2: Edit**; then `python3 scripts/reference-parts.py check-citations` → exit 0; the greps → `≥1`.
- [ ] **Step 3: Commit** `docs(workflows-core): document-lineage and grounding-format — what a grounding re-run counts; part 4's minors (D32 part 5)`.

### Task 4: The commands

**Files:** `plugins/product-workflows/commands/prd-ground.md` (Phase 8 *Derivation matrix*: one `## Derivation matrix` section, replacing any of that name, never a second — **first** check whether any wording elsewhere reads the matrix as appended rows, and ledger what a replacement could drop); `plugins/product-workflows/commands/update-spec.md` (Phase 2 step 1's grounding diff leaves out baseline findings — by `baselines.md` — the two dropped sections and `outcome`/`notes`-only changes); `plugins/docs-workflows/commands/document.md`, `release-notes.md` and `plugins/dev-workflows/commands/ready.md` 2a (the ⚠ template quotes `changed <keys>; new <keys>; withdrawn <keys>`; each pair once); docs pages for `/prd-ground` and `/update-spec` where they describe the matrix or the diff.

- [ ] **Step 1: Failing greps** — `grep -c 'replacing any section of that name' prd-ground.md` counts only the frame-sets one (→ `1`); `grep -c '<changed keys>'` across the three commands → `3`.
- [ ] **Step 2: Edit**; Expected after: `2`, and `0`; check-citations, check-questions → exit 0.
- [ ] **Step 3: Commit** `feat(product-workflows,docs-workflows,dev-workflows): the matrix replaced per run; /update-spec's grounding diff and the never-ask templates follow the lineage rules (D32 part 5)`.

### Task 5: Release, sweep, gates

**Files:** the four `plugin.json`s and `marketplace.json`; four CHANGELOGs dated 2026-11-03 (workflows-core's names the one-time legacy-matrix move); a coupling bullet (workflows-core 1.77.0 ↔ product-workflows 3.72.1: the replaced matrix section is what 1.77.0's section altitude reads); `docs/superpowers/to-fix.md` — D32 closed (follow-ups 4 and 5 done) and a new entry: `/prd-ground` appends `## Documentation divergences` on every docs-grounded run.

- [ ] **Claim sweep** (refinements 3, 7, 8) — `text outside every`, `outside every record`, `always count`, `counts for every downstream`, `append.{0,40}derivation matrix`, `derivation matrix.{0,60}append`, `<changed keys>`, `those two` — before/after counts across `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`.
- [ ] **Sizes** within limits.
- [ ] **Full gates** in the background → `EXIT=0` → commit `release: D32 part 5 — the altitude filter's reach (workflows-core 1.77.0, product-workflows 3.72.1, docs-workflows 1.32.1, dev-workflows 4.57.3)`.

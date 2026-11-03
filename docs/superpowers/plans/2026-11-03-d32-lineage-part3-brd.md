# D32 Document Lineage (part 3, the BRD route) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The decision register and the grounding files record what they were built from, a BRD-route `prd.md` records the register, a register or grounding change counts only at the downstream document's altitude, and `/update-prd` and `/update-spec` revise at their own altitude.

**Architecture:** `lineage.py` gains a per-item altitude read and a per-downstream altitude in the kind table, applied link by link; two rows flip to covered and an inventory row is added. Each BRD-route command gains part 1's `record` / `upstream-check` calls where its phases decide.

**Tech Stack:** Python 3 standard library; git CLI; markdown command/reference prose.

**Spec:** `docs/superpowers/specs/2026-11-03-d32-lineage-part3-brd-design.md` (parts 1 and 2's designs bind under it).

## Global Constraints

- Worktree `$S/wt-d32c`, branch `feat/d32-lineage-brd`; `git branch --show-current` before every commit; the session's commit trailer.
- Covered after this part: `specification.md`, `epic.md`, `design.md`, `prd.md`, ARD, `decisions.md`, `code-grounding.md`, `design-grounding.md`. Uncovered tops: `idea.md`, `brd-inventory.md` (new row, items `[BR#n]`), seeds.
- Altitudes: `prd` → `product`, `ard` → `architecture`, `specification` → `implementation`; filter per link, only where the downstream's kind carries one; an item with no `altitude:` always counts.
- Chain: BRD route — inventory → grounding → register → `prd.md` → ARDs → …; idea route — idea → `prd.md` → grounding → ARDs/spec. A producer never records a document below its own output; `/update-prd` records no grounding file on either route.
- Only the slice's own files are recorded; never another BRD's register, the parent's files or a sibling's records.
- A producer that writes into one of its own upstreams captures it after its last write there.
- Question text and Stop messages exactly as `document-lineage` §6 states them; a command that asks loads `escalation-rules core` first.
- Size limits: `CLAUDE.md` < 36,000 chars; each `.claude/rules/*.md` < 20,000 (counted in characters).
- After editing a reference that loads by part or has entry files: `python3 scripts/reference-parts.py generate`, then `check-parts` and `check-citations`.

## Review Focus

1. **A decision at another altitude changed** → the PRD←register link is not stale; one at `product` → stale with its id — `test_altitude_filter_per_downstream` (Task 1).
2. **A record with no `altitude:`** → counts for every downstream — same test (Task 1).
3. **The register's own link to the grounding** compares every finding, whatever the consumer — `test_register_link_unfiltered` (Task 1).
4. **A `[BR#n]` row's text changed** → the inventory link lists `[BR#n]` — `test_inventory_rows` (Task 1).
5. **A register or grounding file with no frontmatter** stamped → a frontmatter is created and the body is byte-identical (part 1's writer; re-verified on a register-shaped file) — `test_stamp_register_without_frontmatter` (Task 1).

---

### Task 1: Script and kind table

**Files:** `plugins/workflows-core/scripts/lineage.py`, `plugins/workflows-core/scripts/lineage-kinds.json`.

**Interfaces:** Produces `compare(kind, old, new, altitude=None)`; kind rows may carry `"altitude"` (downstream) and `"item_altitude"` (a regex with one group read inside an item's lines); `check` passes the downstream kind's `altitude` into the link's compare.

- [ ] **Step 1: Failing tests:** `test_altitude_filter_per_downstream` (register with `[VD#1]` product and `[VD#2]` architecture; a PRD recording it; changing `[VD#2]` → not stale; changing `[VD#1]` → stale, `changed == ["[VD#1]"]`; a third record with no altitude changed → stale), `test_register_link_unfiltered` (register recording a grounding file; an architecture finding changed → register←grounding stale), `test_inventory_rows` (a `| [BR#2] | … |` row text changed → `changed == ["[BR#2]"]`), `test_stamp_register_without_frontmatter`.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/lineage.py --selftest` (each test individually) — Expected: the new tests fail, the 39 old pass.
- [ ] **Step 3: Implement**: rows — `grounding` covered, reviser `/product-workflows:prd-ground <KEY>`, `item_altitude`; `decisions` covered, `item_altitude`; `prd`/`ard`/`specification` gain `altitude`; new `inventory` row (`^brd-inventory\.md$`, items `^\|\s*\[(BR#\d+)\]\s*\|`, uncovered, reviser null). Filter in `compare`.
- [ ] **Step 4: Run** the selftest — Expected: all pass.
- [ ] **Step 5: Commit** `feat(workflows-core): lineage altitude filter; register and grounding covered (D32 part 3)`.

### Task 2: The reference, the formats, the readers

**Files:** `plugins/workflows-core/references/document-lineage.md` (§3 coverage and the BRD-route PRD sentence; §4 table rows, route-aware chain order, the altitude filter per link; callers list), `plugins/workflows-core/references/grounding-format.md` and `plugins/product-workflows/references/decision-register-format.md` (the frontmatter block the script writes, before the register's `# Decision register:` line), `plugins/workflows-core/docs/reference/references.md`. Verify every reader of `decisions.md` and the grounding files tolerates a leading frontmatter (grep their parse rules: `# Decision register:` line, `- id:` blocks, torn-write rule §8, `grounding-verifier`, `/brd-package` bundle); fix any that does not.

- [ ] Failing grep (`altitude` absent from `document-lineage.md` §4 filter text) → edit → `reference-parts.py generate`, `check-parts`, `check-citations` → commit `docs(workflows-core): document-lineage covers the register and grounding; altitude filter (D32 part 3)`.

### Task 3: `/prd-ground` records and checks

**Files:** `plugins/product-workflows/commands/prd-ground.md` — capture, after the claim list and the frame-set indexes are read: BRD route — the slice's `brd/brd-inventory.md` and each `design/<set>/` index read; idea route — `prd.md`. Never a prerequisite BRD's register. Idea route: `upstream-check` with `docs` = `prd.md` (gate passed), `output` = the existing `code-grounding.md`; BRD route checks nothing. Stamp each grounding file it writes before the handoff stages it; accept where the check ran. Final report `Lineage:`; `PRD_GROUND_LINEAGE_FAILED`, `PRD_GROUND_UPSTREAM_STALE`. Docs page.

- [ ] Failing grep → edit → check-citations, check-questions, id-grammar → commit `feat(product-workflows): /prd-ground records lineage (D32 part 3)`.

### Task 4: `/brd-interview` and `/brd-reconcile`

**Files:** `plugins/product-workflows/commands/brd-interview.md`, `plugins/product-workflows/commands/brd-reconcile.md` — capture the slice's two grounding files and `brd/brd-inventory.md` where read; `upstream-check` with `docs` = the two grounding files, `output` = `decisions.md`; stamp `decisions.md` after the run's last write to it, before the handoff; accept. `/brd-interview`'s no-question path (decision 4): re-stamp the register and offer the handoff with `decisions.md` as the deliverable where the stamp changed it. `/brd-reconcile`'s sweep into a dependent BRD's register stamps nothing. Error tokens `BRD_INTERVIEW_*`, `BRD_RECONCILE_*` (`_LINEAGE_FAILED`, `_UPSTREAM_STALE`). Docs pages.

- [ ] Failing grep → edit → gates → commit `feat(product-workflows): /brd-interview and /brd-reconcile record the register's lineage (D32 part 3)`.

### Task 5: `/create-prd` and `/update-prd` on the BRD route

**Files:** `plugins/product-workflows/commands/create-prd.md` — BRD route: capture `decisions.md` (after the run's last write to it — its roundless `[AS#n]`) and `prd-seed.md` where read; check `docs` = `decisions.md`, `output` = the existing `prd.md`; stamp; Final report. `plugins/product-workflows/commands/update-prd.md` — step 5b on a `brd-link.md` folder: capture `decisions.md`; never a grounding file on either route (retire part 2's capture); Phase 2 diffs the register's `product` records from the recorded blob (`lineage.py` reads the altitude; the prose names the filter) and a base with no record reads the `decided` `product` records whole; rewrite the "reads nothing of a BRD tree" claims; Final report. `plugins/workflows-core/references/prd-format.md` (the `upstreams:` comment: both routes). Docs pages.

- [ ] Failing grep → edit → gates → commit `feat(product-workflows): a BRD-route PRD records the register; /update-prd revises it (D32 part 3)`.

### Task 6: `/create-ard`, `/specify`, `/update-spec`

**Files:** `create-ard.md` and `specify.md` — check `docs` += `decisions.md` (BRD route) and the grounding files read. `update-spec.md` — step 7a `docs` += the register and grounding files the base records; Phase 2's diff of the register and the grounding lists `implementation` records only. Docs pages.

- [ ] Failing grep → edit → gates → commit `feat(product-workflows): /create-ard, /specify and /update-spec check the register and grounding (D32 part 3)`.

### Task 7: Release, sweep, gates

**Files:** versions workflows-core 1.75.0, product-workflows 3.72.0 (from main's 1.74.1 / 3.71.1); `marketplace.json`; CHANGELOGs dated 2026-11-03; a coupling bullet; `.claude/rules/product-workflows.md` and `.claude/rules/brd-route.md` map lines (size-check); `docs/superpowers/to-fix.md` D32 (follow-up 2 done; left: `/document`, `/release-notes`).

- [ ] Claim sweep (refinements 4, 7, 8): `upstream-only`, `BRD-route` `records no lineage`, `reads nothing of a BRD tree`, `no lineage yet`, every statement that the register or grounding is a top; count before/after.
- [ ] Full gates in the background → `EXIT=0` → commit `release: D32 part 3 — the BRD route (workflows-core 1.75.0, product-workflows 3.72.0)`.

# D32 Document Lineage (part 2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `prd.md` (idea route) and the ARDs record what they were built from; `/specify`, `/epics`, `/design`, `/create-ard` and `/update-spec` check their PRD/ARD inputs; `/implement` and `/conformance` ask on a stale chain; `/ready` reports it.

**Architecture:** Part 1's script and reference carry everything: two kind-table rows flip to covered, `lineage.py` learns the empty record and a several-documents acceptance read, and each command gains part 1's `record` / `upstream-check` calls at the places its own phases decide.

**Tech Stack:** Python 3 standard library; git CLI; markdown command/reference prose.

**Spec:** `docs/superpowers/specs/2026-11-03-d32-lineage-part2-prd-ard-design.md` (part 1's `…/2026-11-03-d32-document-lineage-design.md` binds under it).

## Global Constraints

- Worktree `$S/wt-d32b`, branch `feat/d32-lineage-prd-ard`; `git branch --show-current` before every commit; the session's commit trailer.
- A stale link **asks, never hard-stops** — except `/ready`, which **never asks** and reports; only a script failure stops (`<COMMAND>_LINEAGE_FAILED`).
- Question text and Stop messages exactly as `workflows-core:document-lineage` §6 states them; a command that asks loads `escalation-rules core` first (`check-questions`).
- Covered after this part: `specification.md`, `epic.md`, `design.md`, `prd.md`, ARD (`ard.md`, `ard-<area>.md`). Upstream-only: `idea.md`, `decisions.md`, grounding files, `prd-seed.md`, `ard-seed.md`.
- Chain order, top to bottom: idea, decision register, grounding → `prd.md` → ARDs → `epic.md` → `specification.md` → `design.md`. A producer never records a document below its own output.
- BRD-route `prd.md`: **no record written** this part. `--from-prd` seed PRD: never recorded.
- Empty capture → `upstreams: []`, a record, never *missing*.
- Size limits: `CLAUDE.md` < 36,000 chars; each `.claude/rules/*.md` < 20,000 (`dev-workflows.md` is already over — net-shrink any edit there, or leave it).
- After editing a reference that loads by part or has entry files: `python3 scripts/reference-parts.py generate`, then `check-parts` and `check-citations`.
- No tracker, organisation or client name; bracketed `[PREFIX#N]` ID grammar only.

## Review Focus

1. **A document with `upstreams: []` already in its frontmatter, stamped again with entries** → exactly one `upstreams:` key — `test_flow_empty_list_replaced` (Task 1).
2. **`accept` into a file with no frontmatter** (`implementation.md`) → frontmatter created with `accepted:` only, body byte-identical, no `upstreams:` key — `test_accept_creates_frontmatter` (Task 1).
3. **`accept` into `_conformance.md`** (frontmatter `kind`, `key`, no `upstreams:`) → no `upstreams: []` invented — `test_accept_adds_no_upstreams_key` (Task 1).
4. **A spec whose record names a `prd.md` with no record** → `missing` holds the PRD, `top_missing.reviser` is `/product-workflows:update-prd <KEY>` — `test_prd_covered_missing` (Task 1).
5. **`/ready` across two Epics**: an acceptance in Epic A's design does not clear Epic B's link — covered by the per-unit invocation rule (Task 7) and `test_accepted_from_union` proving the option reads only the documents passed (Task 1).

---

### Task 1: Script and kind table

**Files:**
- Modify: `plugins/workflows-core/scripts/lineage.py` (`_blocks`, `read_record`, `_render`, `_write_record`, `stamp`, `check`, CLI, selftest)
- Modify: `plugins/workflows-core/scripts/lineage-kinds.json` (`prd`, `ard` → `"covered": true`)

**Interfaces:**
- Produces: `check(specs, ref, docs, output=None, accepted_from=())`; CLI `check … [--accepted-from DOC]…` (repeatable, absolute paths, each document's `accepted:` unioned with `--output`'s). `stamp` with an empty capture writes `upstreams: []`. `_write_record(doc, upstreams=None, accepted=None)` renders `upstreams:` only where it is given or the document already had the key; `accepted:` only where non-empty.

- [ ] **Step 1: Failing tests** in the selftest:
  - `test_empty_capture_writes_empty_list`: stamp a spec with `[]` → text contains `"\nupstreams: []\n"`; `read_record(text)[1] is True`; `check` from that spec → `missing == []`.
  - `test_flow_empty_list_replaced`: a doc with `upstreams: []` stamped with one entry → `text.count("upstreams:") == 1` and the entry present.
  - `test_accept_creates_frontmatter`: file `# Implementation — X\n\n## 2026-01-01 — /implement\n` → `accept` with one stale link → text starts `---\naccepted:\n`, ends with the original body unchanged, contains no `upstreams`.
  - `test_accept_adds_no_upstreams_key`: `---\nkind: conformance-record\nkey: P-1\n---\n# C\n` → after `accept`, `kind:` and `key:` kept, no `upstreams`.
  - `test_prd_covered_missing`: repo with `prd.md` (no frontmatter) and a spec recording it at its current blob → `check([spec])["missing"] == [{"doc": prd, …}]`, `top_missing["reviser"]` starts `/product-workflows:update-prd`.
  - `test_accepted_from_union`: stale spec←prd link; `check(..., accepted_from=[design_with_acceptance])` → link in `accepted`, not `stale`; `accepted_from=[other_doc]` → `stale`.
- [ ] **Step 2: Run** `python3 plugins/workflows-core/scripts/lineage.py --selftest` — Expected: the six new tests FAIL, the 21 old pass (a test that assumed `prd.md` uncovered fails too — fix that test's fixture, not the rule, and ledger it).
- [ ] **Step 3: Implement.** `_blocks` matches `^(upstreams|accepted):\s*(\[\])?\s*$` and reports which keys it saw; `read_record`'s `has` is true for either form; `_render("upstreams", [], …)` → `["upstreams: []"]` when the caller asks for the key; `check` unions `accepted_from` documents' `accepted:` into `acc`. Kind table: two `covered` flips.
- [ ] **Step 4: Run** the selftest — Expected: all pass (27).
- [ ] **Step 5: Commit** `feat(workflows-core): lineage covers prd.md and the ARDs; empty record; --accepted-from (D32 part 2)`.

### Task 2: The reference and the implementation record

**Files:**
- Modify: `plugins/workflows-core/references/document-lineage.md` — consumer list (+ `/create-prd`, `/update-prd`, `/create-ard`, `/implement`, `/conformance`, `/ready`); §1 the empty record; §3 coverage (`prd.md` and ARDs covered; the BRD-route `prd.md` writes none this part and asks as unrecorded); §4 table's Covered column + the chain order and the never-record-below rule; §6 a **report-only** variant: a caller that never asks (`/ready`) passes `--accepted-from` per unit, shows the block as findings, records nothing; §7 unchanged lines plus `/ready`'s.
- Modify: `plugins/workflows-core/references/implementation-format.md` §1 — the optional frontmatter holding only `accepted:`, written by `lineage.py accept`, read by nothing but `upstream-check`.
- Verify (and fix where needed) every reader of `implementation.md` tolerates a leading frontmatter: grep `implementation.md` reads in `plugins/*/commands`, `plugins/*/agents`, `plugins/*/references`, `plugins/*/scripts`.
- Modify: `plugins/workflows-core/docs/reference/references.md` bullet for `document-lineage`.

- [ ] **Step 1: Failing check**: `grep -c "accepted-from" plugins/workflows-core/references/document-lineage.md` → `0`; `grep -c "frontmatter" plugins/workflows-core/references/implementation-format.md` → `0`.
- [ ] **Step 2: Edit** per Files; ledger each reader checked and its verdict.
- [ ] **Step 3: Run** `python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations` — Expected: exit 0; the two greps now non-zero.
- [ ] **Step 4: Commit** `docs(workflows-core): document-lineage covers prd.md and the ARDs; implementation.md frontmatter (D32 part 2)`.

### Task 3: `/create-prd` and `/update-prd` record

**Files:**
- Modify: `plugins/product-workflows/commands/create-prd.md` — Phase 2 (idea route): capture `--from-disk` `idea.md` where under `$SPECS_PATH` and the grounding files read, before reading them (§5 step 1); Phase 5: stamp `prd.md` after it is written, before the handoff stages it (idea route only; a BRD-route run stamps nothing and says so); Final report `Lineage:` line; `CREATE_PRD_LINEAGE_FAILED`.
- Modify: `plugins/product-workflows/commands/update-prd.md` — Phase 0/2: read the base's record; capture its recorded upstreams `--from-disk` plus the grounding files read; a base with no record (idea route) captures the folder's `idea.md` and Phase 2 reads it as a secondary input; Phase 2 reads `git diff <recorded blob> <default-ref>:<path>` per recorded upstream as a change signal ranked into the grill; never records the ARD/spec it reads; never asks; Phase 5: stamp before the handoff; Final report `Lineage:`; `UPDATE_PRD_LINEAGE_FAILED`.
- Modify: `plugins/workflows-core/references/prd-format.md` (frontmatter: `upstreams:`/`accepted:` written by the lineage script) if it documents frontmatter keys.

- [ ] **Step 1: Failing check**: `grep -c "document-lineage" plugins/product-workflows/commands/{create,update}-prd.md` → `0` each.
- [ ] **Step 2: Edit** per Files, each command's loader preamble already present (verify).
- [ ] **Step 3: Run** `python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && ./scripts/check-id-grammar.sh --root .` — Expected: exit 0.
- [ ] **Step 4: Commit** `feat(product-workflows): /create-prd and /update-prd record lineage (D32 part 2)`.

### Task 4: `/create-ard` records and checks

**Files:**
- Modify: `plugins/product-workflows/commands/create-ard.md` — after Phase 2's reads are settled (PRD gate passed): capture `prd.md`, on Epic runs `epic.md` and the inherited PRD-level ARD, on the BRD route `decisions.md` and `ard-seed.md` where read, grounding files — never the Epic's `specification.md`/`design.md`; `upstream-check` with `docs` = `prd.md` (+ `epic.md`, the inherited ARD on Epic runs), `output` = the existing target ARD; Phase 5/6: stamp each ARD written (+ accept); Final report `Lineage:`; `CREATE_ARD_LINEAGE_FAILED`, `CREATE_ARD_UPSTREAM_STALE`.

- [ ] Steps as Task 3 (failing grep → edit → check-citations/check-questions/id-grammar → commit `feat(product-workflows): /create-ard records and checks lineage (D32 part 2)`).

### Task 5: Part 1's consumers widen

**Files:**
- Modify: `plugins/product-workflows/commands/specify.md` (Phase 2.5 check: `docs` += `prd.md` and each ARD read)
- Modify: `plugins/product-workflows/commands/epics.md` (Phase 3 check: `docs` += `prd.md`; the check now runs whether or not the PRD-level spec is present)
- Modify: `plugins/dev-workflows/commands/design.md` (Phase 2.5 check: `docs` += each ARD read)
- Modify: `plugins/product-workflows/commands/update-spec.md` (step 7a: `docs` = `epic.md` on an Epic-level base, plus `prd.md` and each ARD the base records, on every base; rewrite *a PRD-level specification has no covered document above it*)
- Docs pages of the four commands where they describe the check's inputs.

- [ ] **Step 1: Failing check**: the sentence `has no covered document above it` present in `update-spec.md` (count 1).
- [ ] **Step 2: Edit** per Files; claim-sweep `upstream-only`, `no covered document`, `uncovered` across refinement 4's scope and rewrite each copy describing `prd.md`/ARDs.
- [ ] **Step 3: Run** check-citations, check-questions — Expected exit 0; the sentence count → 0.
- [ ] **Step 4: Commit** `feat: /specify, /epics, /design, /update-spec check PRD and ARD lineage (D32 part 2)`.

### Task 6: `/implement` and `/conformance` ask

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` — keyed runs only: after the in-scope spec/design gate (Phase 0) and before Phase 1.7/`risk-planner`: `upstream-check` with `docs` = each in-scope `specification.md`/`design.md` the gate passed, `output` = the unit's `implementation.md` where on disk; Phase 4.7: after the block is written, `accept` into `implementation.md` where the check ran and the run went on; Implementation Report `Lineage:` line; `IMPLEMENT_LINEAGE_FAILED`, `IMPLEMENT_UPSTREAM_STALE`. Direct-mode runs: `Lineage: not checked — direct run`.
- Modify: `plugins/dev-workflows/commands/conformance.md` — after Phase 0 step 4's gate, before Phase 1: `upstream-check` with `docs` = each covered document the gate passed, `output` = the unit's own `_conformance.md` where on disk; Phase 5: `accept` into every `_conformance.md` written; Conformance Report `### Scope` `Lineage:` line; `CONFORMANCE_LINEAGE_FAILED`, `CONFORMANCE_UPSTREAM_STALE`.
- Modify: `plugins/dev-workflows/references/conformance-format.md` §1 frontmatter (`accepted:` may follow `key:`).
- Docs pages of both commands.

- [ ] Steps as Task 3 (commit `feat(dev-workflows): /implement and /conformance check lineage (D32 part 2)`).

### Task 7: `/ready` reports

**Files:**
- Modify: `plugins/dev-workflows/commands/ready.md` — after Phase 1's gate: per unit (each Epic: its present `specification.md`/`design.md`; PRD run: the PRD-level spec too), `check` with those `docs` and `--accepted-from` the same documents, no `--output`; each stale link a ⚠ readiness finding naming the document to revise and its reviser, **capping the verdict at PARTIAL**; each missing record a note line, never a downgrade; each accepted link named *accepted by <doc>*; never asks, never `accept`s; a script failure is a ⚠ finding (`/ready` never stops), not `READY_LINEAGE_FAILED`; report `Lineage:` line.
- Modify: `plugins/dev-workflows/agents/readiness-reviewer.md` only if the verdict cap rule lives there (check where PARTIAL caps are stated).
- Modify: `plugins/dev-workflows/references/workflow-states.md` if the verdict rules are stated there.
- Docs page `plugins/dev-workflows/docs/commands/ready.md`.

- [ ] Steps as Task 3 (commit `feat(dev-workflows): /ready reports stale lineage (D32 part 2)`).

### Task 8: Release, sweep, gates

**Files:** `plugin.json` ×3, `marketplace.json`, `CHANGELOG.md` ×3 (dated 2026-11-03), `.claude/rules/plugin-updates-coupling.md` (one bullet: the commands citing the widened `document-lineage` need the workflows-core that ships it; re-check its size), `.claude/rules/{product-workflows,workflows-core}.md` map lines where they name these commands' gates (size-check), `docs/superpowers/to-fix.md` D32 (follow-up 1 done; left: BRD route incl. BRD-route `prd.md` record and the altitude question; `/document`, `/release-notes`).

- [ ] **Step 1:** Versions: workflows-core 1.74.0, product-workflows 3.71.0, dev-workflows 4.57.0 (minor each, from main's 1.73.0 / 3.70.1 / 4.56.1).
- [ ] **Step 2:** Claim sweep (refinements 4, 7, 8) for: `upstream-only`, `prd.md` / `ARD` `records nothing`, `never looks at`, `Consumers:` of `document-lineage`, M3/M4 deferred notes; count before/after.
- [ ] **Step 3:** Full gates: `bash $S/gates-nonode.sh > $S/g-d32b.log 2>&1; echo "EXIT=$?" >> $S/g-d32b.log` in the background — Expected `EXIT=0`.
- [ ] **Step 4: Commit** `release: D32 part 2 — prd.md and the ARDs covered (workflows-core 1.74.0, product-workflows 3.71.0, dev-workflows 4.57.0)`.

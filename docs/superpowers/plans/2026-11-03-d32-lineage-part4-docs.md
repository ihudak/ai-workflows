# D32 Document Lineage (part 4, `/document` and `/release-notes`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/document` (keyed mode) and `/release-notes` run `upstream-check` as callers that never ask, report each stale link, missing record and unreadable document, and record nothing.

**Architecture:** `workflows-core:document-lineage` §6 step 6 and §7 widen from `/ready` alone to three never-ask callers, with a rule for a caller that has no `require-on-main` gate. Each docs-workflows command gains one Phase 0 check step and report lines. `lineage.py` and the kind table are unchanged.

**Tech Stack:** Markdown command and reference prose; Python 3 `lineage.py` (run, not edited); bash gates.

**Spec:** `docs/superpowers/specs/2026-11-03-d32-lineage-part4-docs-design.md` (parts 1–3's designs bind under it).

## Global Constraints

- Worktree `$S/wt-d32d`, branch `feat/d32-lineage-docs`; `git branch --show-current` before every commit; the session's commit trailer.
- Never ask, stop, accept or stamp on a lineage outcome in either command; a script non-zero exit is a warning line.
- Units: an Epic-addressed run → the focus Epic alone; otherwise each `EPIC-` folder directly under the PRD folder plus the PRD folder; per unit `docs` = its `specification.md` and `design.md` present in the working tree or on `<default-ref>`, the same two as `--accepted-from`, no `--output`. No unit holds either → one check, `prd.md` as `docs` and `--accepted-from`.
- Gateless caller: each `absent` entry is a note line `<doc>: not on <default-ref> — its chain was not checked`; the report line never says `current` while one is listed; all absent → `Lineage: not checked — <doc…> not on <default-ref>`. No specs repository → no check, `Lineage: not checked — no specs repository`.
- No lineage text on a docs page or in a release note's body; no `require-on-main` added.
- Size limits: `CLAUDE.md` < 36,000 chars; each `.claude/rules/*.md` < 20,000 chars.

## Review Focus

1. **A PM-stage `/release-notes` run standing on an unmerged `prd/` branch** — `prd.md` is not on `<default-ref>` → `Lineage: not checked — prd.md not on <default-ref>`, never `current` — Task 1 step 2 (scratch run proving the `absent` shape) and the Task 3 grep.
2. **An Epic-addressed run** checks the focus Epic alone; another Epic's stale link is not reported — Task 1's §6 step 6 text and the Task 2/3 greps.
3. **A link accepted in the unit's own `design.md`** → *accepted in this unit*, no warning — Task 1's text, as `/ready` already does.
4. **An `@<path>` run with `$SPECS_PATH` unset** → no script call, `Lineage: not checked — no specs repository` — Task 2/3 greps.
5. **The script exits non-zero** → a warning line and the run goes on; no `DOCUMENT_LINEAGE_FAILED` / `RELEASE_NOTES_LINEAGE_FAILED` token is minted — Task 2/3 greps (count 0).

---

### Task 1: The reference

**Files:** `plugins/workflows-core/references/document-lineage.md` (callers paragraph; §6 step 6; §7), `plugins/workflows-core/docs/reference/references.md` (the `document-lineage.md` bullet's "`/ready` reports what it finds instead of asking").

**Interfaces:** Produces §6 step 6 as the rule Tasks 2–3 cite by `Skill(skill: "workflows-core:reference", args: "document-lineage upstream-check")` "§6 by its step 6", and §7's two `not checked` forms.

- [ ] **Step 1: Failing grep** — `grep -c 'docs-workflows:release-notes' plugins/workflows-core/references/document-lineage.md` → Expected `0`; `grep -c 'its chain was not checked' …` → `0`.
- [ ] **Step 2: Scratch run** (not committed): a temp git repo with `specifications/PRD-X-1-a/prd.md` on `main` and a `design.md` only in the working tree; `lineage.py check --specs <tmp> --ref main --out <f> specifications/PRD-X-1-a/design.md` → Expected JSON `absent: [{"downstream": null, "upstream": "…/design.md"}]`, `stale: []`.
- [ ] **Step 3: Edit** — callers list adds `/docs-workflows:document` (keyed mode) and `/docs-workflows:release-notes`, and "`/ready` checks and never asks" becomes the three; §6 step 6 names the three, states the unit scope and the `prd.md` fallback (Global Constraints), and adds the gateless-caller paragraph (`absent` note lines; never `current` while one is listed); §7 adds `Lineage: not checked — <doc…> not on <default-ref>` and `— no specs repository`. Widen the references page bullet.
- [ ] **Step 4: Verify** — Step 1's greps → `≥1`; `./scripts/check-docs.sh --root . > $S/cd1.log 2>&1; echo EXIT=$?` → `EXIT=0`.
- [ ] **Step 5: Commit** `docs(workflows-core): document-lineage — /document and /release-notes as never-ask callers; a caller with no gate (D32 part 4)`.

### Task 2: `/document` (keyed mode)

**Files:** `plugins/docs-workflows/commands/document.md` — Mode A Phase 0, a new paragraph at the end of step 1 (after the placement stops and `branch-check`, before step 2), *Check the lineage under each unit — report it, never ask.*, citing §6 step 6; the Readiness table's new `Lineage` row; the keyed report's new `### Lineage` section carrying §7's line and each line under it; a Mode A invariant bullet (`NEVER ask, stop or write on a lineage outcome`). `plugins/docs-workflows/docs/commands/document.md` (how it runs; what it produces).

- [ ] **Step 1: Failing grep** — `grep -c 'document-lineage upstream-check' plugins/docs-workflows/commands/document.md` → `0`.
- [ ] **Step 2: Edit** as above; Mode B untouched.
- [ ] **Step 3: Verify** — Step 1 grep → `1`; `grep -c 'DOCUMENT_LINEAGE_FAILED' …` → `0`; the new paragraph's line number is below the `branch-check` paragraph and above `2. **Resolve the docs repo`; `python3 scripts/reference-parts.py check-citations` and `check-questions` → exit 0.
- [ ] **Step 4: Commit** `feat(docs-workflows): /document reports the lineage under each unit (D32 part 4)`.

### Task 3: `/release-notes`

**Files:** `plugins/docs-workflows/commands/release-notes.md` — Phase 0, after the placement stops (where `focus_key` is known), the same check paragraph; its lines shown before Phase 1 asks about diff grounding; Phase 2's plan, where a stale link was found and grounding is declined: `claims drawn from the PRD are not checked against the code`; the Final report's `Lineage:` line; an invariant bullet. `plugins/docs-workflows/docs/commands/release-notes.md`.

- [ ] **Step 1: Failing grep** — `grep -c 'document-lineage upstream-check' plugins/docs-workflows/commands/release-notes.md` → `0`.
- [ ] **Step 2: Edit** as above.
- [ ] **Step 3: Verify** — Step 1 grep → `1`; `grep -c 'RELEASE_NOTES_LINEAGE_FAILED'` → `0`; `grep -c 'not checked against the code'` → `≥1`; check-citations, check-questions → exit 0.
- [ ] **Step 4: Commit** `feat(docs-workflows): /release-notes reports the lineage above the note (D32 part 4)`.

### Task 4: Release, sweep, gates

**Files:** workflows-core 1.76.0, docs-workflows 1.32.0 (from main's 1.75.0 / 1.31.1) in each `plugin.json` and `marketplace.json`; CHANGELOGs dated 2026-11-03; a bullet in `.claude/rules/plugin-updates-coupling.md` (docs-workflows 1.32.0 cites §6 step 6's three-caller form; on an older workflows-core the check still runs, the gateless note lines are absent); `.claude/rules/docs-workflows.md`'s `/document (keyed)` map line and `.claude/rules/release-notes.md`'s map line gain `[document-lineage upstream-check, report only]`; `docs/superpowers/to-fix.md` — D32 follow-up (3) done (left: (4)), and a new entry: `/release-notes` with diff grounding off checks no claim against the code once a spec or design exists.

- [ ] **Claim sweep** (refinements 3, 7, 8) — before/after counts across `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`: `/ready` as the only never-ask caller (`caller that never asks`, `never asks`, `/ready reports`), `Left, each its own release`, any sentence that `/document` or `/release-notes` reads no lineage.
- [ ] **Sizes** — `wc -m CLAUDE.md .claude/rules/*.md` within limits.
- [ ] **Full gates** in the background → `EXIT=0` → commit `release: D32 part 4 — /document and /release-notes report the chain (workflows-core 1.76.0, docs-workflows 1.32.0)`.

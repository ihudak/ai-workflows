# `/update-spec` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/product-workflows:update-spec`, which revises a merged specification in place — keeping IDs, superseding on a change of meaning, withdrawing on removal — and teach every reader of specification IDs to skip superseded and withdrawn items.

**Architecture:** Markdown command, agent and reference prose executed literally by agents. The rules live once in `product-workflows:specification-format` (the `inputs_at` field, the two markers, the live-items rule, the archive rule); `/specify`, `/update-spec`, `spec-reviewer`, `workflows-core:pre-lint` and the dev-side consumers cite them. Tests are the repository's gates plus `grep` assertions whose expected counts are stated per step.

**Tech Stack:** Claude Code plugin markdown; `scripts/check-docs.sh`, `scripts/validate-catalog.py`, `scripts/check-id-grammar.sh`, `scripts/reference-parts.py`, `scripts/mermaid/check-mermaid.mjs`; the full chain in `.github/workflows/validate-catalog.yml`.

**Spec:** `docs/superpowers/specs/2026-10-28-update-spec-design.md` (approved 2026-10-28). Every task's implementer reads it first; decision numbers (D1–D9) below are its.

## Global Constraints

- Read every file you edit with the **Read tool** first, so its `.claude/rules/` file loads (`CLAUDE.md` § Where the rest of the guidance lives).
- Prose is executed: no hard-wrapped sentence may say something false; every claim you change is swept by its **subject** across `plugins/` (every `CHANGELOG.md` included), `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`, and counted before and after (`.claude/rules/claim-sweep.md` refinement 7).
- Specification IDs are `[U01]` (document-wide), `[AC01]` (per story), `[TC01]` (per criterion) — `specification-format.md` § Identifier conventions. PRD IDs are `[US#n]`, `[AC#n]`, `[FR#n]`; prose teaches only the bracketed `[PREFIX#N]` form (`check-id-grammar.sh`).
- A shared reference is cited `workflows-core:<name>` and loaded through `Skill(skill: "workflows-core:reference", args: "<name>")`, never by path; a file citing one carries the preamble (check 16).
- Every `choices:` array has 2–4 options, no "Other", and the command has a **Load the question rules.** step before its first question (`check-questions`).
- Never edit a file under `plugins/workflows-core/reference-parts/` by hand: edit the source reference, then `python3 scripts/reference-parts.py generate`.
- Never increment a count from memory: re-derive with the recipe written beside it, and keep the recipe beside the new number.
- Plugin `description` (in `plugin.json` and the `marketplace.json` entry): ≤ 1024 characters, a capability blurb — rewrite wording, never append.
- New files under `.claude/` need `git add -f`. Commits end with the attribution lines in the session's system reminder. Run `git branch --show-current` before every commit; work only in this worktree.

## Review Focus

1. **A specification with no `inputs_at`** (every one written before this release) — the run must say it cannot tell what moved upstream and take the correction entry, never guess a baseline from the file's history. Pinned in Task 4 Step 2.
2. **A checkout copy that differs from `<default-ref>`'s** — a pending `/design` note on an unmerged `spec/` branch must stop the run, never be overwritten or merged. Pinned in Task 4 Step 2.
3. **A superseded or withdrawn item read as live** by a consumer this plan did not touch — re-derive the consumer set by grep before Task 5, and the final review greps for every heading-scan of `### [U` / `#### [AC` / `**[TC`. Pinned in Task 5 Step 1 and Task 9 Step 3.
4. **A change-of-meaning answered as a wording fix** — the grill must ask the meaning question per changed item and record the answer in the change list, so `spec-reviewer` can check it against the base. Pinned in Task 4 Step 4 and Task 2 Step 3.
5. **A downstream write** — no task may write `design.md`, `epic.md`, `_coverage.md`, a PRD or an ARD; `/update-spec`'s only write outside `specification.md` and `revisions/` is `/specify`'s own consumption stamp. Pinned in Task 4 Step 6.

---

### Task 1: `specification-format.md` — the field, the markers, the live-items rule, the archive rule

**Files:**
- Modify: `plugins/product-workflows/references/specification-format.md` (§ Frontmatter; § Header; § Identifier conventions and its *Renumbering* paragraph; a new § *Notes other commands write*; a new § *Archiving before a rewrite*)

**Interfaces:**
- Produces (every later task cites these by heading, never restates them):
  - Frontmatter field `inputs_at: <40-hex SHA>` — "the `<default-ref>` commit the writing run read its inputs at; written by `/specify` and `/update-spec`, kept unchanged by every other writer; absent = a null baseline".
  - Superseded marker, appended to the item's heading: ` — Superseded by [ACnn], <YYYY-MM-DD>` (an `[ACnn]` in the same story; `[Unn]` for a story; `[TCnn]` in the same criterion). An item whose meaning moved to another scope is withdrawn instead, its reason naming where.
  - Withdrawn marker: ` — Withdrawn <YYYY-MM-DD>: <reason>`.
  - **Live items** rule: "an item whose heading carries either marker, and every item nested under it, is not live: it keeps its number, counts for contiguity, and is skipped by every reader that enumerates, covers, traces or counts requirements" — followed by the list of those readers (Task 5's set).
  - § *Archiving before a rewrite*: the archive rule now in `commands/specify.md` Phase 5's guard (copy to `revisions/specification_<YYYYMMDD>.md` / `-worktree.md`, first free `-2`, `-3`; identical archive stands; failed archive stops before any write), moved here verbatim in substance, with `<COMMAND>_ARCHIVE_FAILED` as the stop's shape.

- [ ] **Step 1: Count the claims you will change.** `grep -c 'inputs_at\|Superseded by \[\|Withdrawn [0-9]' plugins/product-workflows/references/specification-format.md` → expect `0`. `grep -n 'Renumbering a large specification' plugins/product-workflows/references/specification-format.md` → expect one line.
- [ ] **Step 2: Write the five sections.** Frontmatter block gains the `inputs_at` line and one paragraph on it; Header rules gain "`Version` starts `1`; `/update-spec` raises it by one"; Identifier conventions gain the two markers, the live-items rule and its reader list, and the sentence "IDs are never renumbered or reused once the specification has merged; an update run (`/update-spec`) supersedes or withdraws instead"; the *Renumbering* paragraph gains "It never applies to an update run, which renumbers nothing."; the notes section says `## Engineering review`, its `- [ ]` notes and `Engineering proposal (/design): …` answers are written by `/design`, `/implement` and `/conformance`, are read as context, and count toward `Open questions`.
- [ ] **Step 3: Verify.** `grep -c 'inputs_at' …specification-format.md` ≥ 2; `grep -c 'Superseded by \[' …` ≥ 1; `grep -c '^## Archiving before a rewrite' …` = 1. Run `./scripts/check-id-grammar.sh --root .` → exit 0.
- [ ] **Step 4: Commit** `feat(product-workflows): specification-format — inputs_at, superseded and withdrawn items, the archive rule`.

### Task 2: `pre-lint` and `spec-reviewer` read the new rules

**Files:**
- Modify: `plugins/workflows-core/references/pre-lint.md:93-100` (the specification ID-series and per-criterion coverage checks)
- Modify: `plugins/product-workflows/agents/spec-reviewer.md` (input contract; header check step 2; ID checks; a regression-vs-intent check)
- Regenerate: `plugins/workflows-core/reference-parts/` if `pre-lint` loads by part (check `scripts/reference-parts.py check-parts`)

**Interfaces:**
- Consumes: Task 1's markers and live-items rule, `inputs_at`.
- Produces: `spec-reviewer` input contract lines `Base: <absolute path to the archived base, or omitted on a /specify run>` and `Change list: <the confirmed list, each item with its ID, its kind (wording | meaning | withdrawn | new) and its source (upstream <input> | correction | note), or omitted>`.

- [ ] **Step 1: Pre-lint.** Contiguity counts superseded and withdrawn items as present; per-criterion coverage applies to live criteria only; a marker not of Task 1's two forms is a MAJOR naming it. Cite `specification-format.md` § Identifier conventions for the forms.
- [ ] **Step 2: `spec-reviewer`.** Step 2's header check adds "`inputs_at`, where present, is 40 lowercase hex characters"; ID checks skip non-live items for coverage; a `Superseded by` naming an ID that does not exist in the same scope is a BLOCKER.
- [ ] **Step 3: Regression check (Review Focus 4).** Where `Base:` and `Change list:` are given: every difference between base and result outside the change list's items is a finding (BLOCKER where it changes a live item's meaning); an item listed `wording` whose meaning changed is a BLOCKER asking for a new ID.
- [ ] **Step 4: Verify.** `grep -c 'Change list:' plugins/product-workflows/agents/spec-reviewer.md` ≥ 2; `python3 scripts/reference-parts.py check-parts` and `check-citations` → exit 0.
- [ ] **Step 5: Commit** `feat(workflows-core, product-workflows): pre-lint and spec-reviewer read superseded and withdrawn items; spec-reviewer takes a base and a change list`.

### Task 3: `/specify` writes `inputs_at` and cites the archive rule

**Files:**
- Modify: `plugins/product-workflows/commands/specify.md` — Phase 2 (capture `inputs_at` once the require-on-main gates have passed: `git -C "$SPECS_PATH" rev-parse <default-ref>`), Phase 6's write of `specification.md` (write the field), Phase 5's *Existing specification* guard (cite Task 1's § *Archiving before a rewrite* in place of the inline rule; its last sentence at `:904-905` becomes "Revising a merged specification in place — keeping its IDs and `Created` — is `/product-workflows:update-spec`'s."), and the `SPECIFY_PUBLISHED` remedy (unchanged wording, still `/specify`'s).
- Modify: `plugins/product-workflows/docs/commands/specify.md` (say it records `inputs_at`; point to `/update-spec` for revisions).

- [ ] **Step 1: Count.** `grep -c "is not\s*this command's yet" plugins/product-workflows/commands/specify.md` (wrap-insensitive, `$S/count.py`) → 1 before, 0 after. `grep -rn 'not this command.s yet' plugins/ docs/maintainers .claude/rules CLAUDE.md` → note every other copy and sweep it.
- [ ] **Step 2: Edit** as listed; the archive rule's text leaves `specify.md`, its stop keeps the name `SPECIFY_ARCHIVE_FAILED`.
- [ ] **Step 3: Verify.** `grep -c 'inputs_at' plugins/product-workflows/commands/specify.md` ≥ 2; `grep -c 'update-spec' plugins/product-workflows/commands/specify.md` ≥ 1; `./scripts/check-docs.sh --root .` → exit 0.
- [ ] **Step 4: Commit** `feat(product-workflows): /specify records inputs_at; its guard names /update-spec`.

### Task 4: the `/update-spec` command

**Files:**
- Create: `plugins/product-workflows/commands/update-spec.md`
- Create: `plugins/product-workflows/docs/commands/update-spec.md` (Task 7 completes the docs tree; this page is the command's own, required by check-docs)

**Interfaces:**
- Consumes: Task 1 (field, markers, archive rule), Task 2 (`spec-reviewer`'s `Base:` and `Change list:`), `/specify`'s Phase 1 grounding steps, Phase 5.5 pre-lint, Phase 6 review/triage and its consumption-stamp step (cite by phase name and heading).
- Produces: the stop codes `UPDATE_SPEC_NO_BASE`, `UPDATE_SPEC_PENDING_CHANGE`, `UPDATE_SPEC_PUBLISHED`, `UPDATE_SPEC_EPIC_SPECS_ONLY`, `UPDATE_SPEC_ARCHIVE_FAILED`; usage `/product-workflows:update-spec <ADDRESS> ["<what is wrong>"] [--no-docs] [--docs <path>] [--no-arch] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`; `handoff-to-main` `prefix: spec`; next-step lane `pm` (Task 6 adds the node).

- [ ] **Step 1: Frontmatter and preamble.** `name: update-spec`, a `description` naming both entries and the merged-base rule, `allowed-tools` as `specify.md`'s, `disable-model-invocation: true`; the core-references preamble and the load-by-part paragraph (copy `specify.md`'s, then keep only the references this command cites).
- [ ] **Step 2: Phase 0 — resolve and gate (D2; Review Focus 1, 2).** `resolve-address`; `specs-preflight`; `require-on-main` on `specification.md` (no copy on `<default-ref>` → `UPDATE_SPEC_NO_BASE` naming `/product-workflows:specify <ADDRESS>`; a PRD folder with no specification whose `EPIC-` children have one → `UPDATE_SPEC_EPIC_SPECS_ONLY` listing `/product-workflows:update-spec <EPIC-KEY>` per Epic); the byte-identity test `git -C "$SPECS_PATH" diff --quiet <default-ref> -- <feature-folder>/specification.md` plus an untracked/staged check → otherwise `UPDATE_SPEC_PENDING_CHANGE` naming the difference and "merge or discard it first"; `Published: yes` → `UPDATE_SPEC_PUBLISHED` with D2's remedy; upstream inputs gated as `/specify` gates them; `inputs_at` read from the base — missing, not 40-hex, or not reachable (`git cat-file -e <sha>^{commit}`) → **null baseline**, said once in the plan-approval output.
- [ ] **Step 3: Phase 1 — configure.** Load the question rules; `strip-run-flags`; model routing (`spec-reviewer` §2 Opus chain); docs and architecture grounding resolved as `/specify` Phase 1 does, by citation.
- [ ] **Step 4: Phase 2 — the change list (D3, D4; Review Focus 4).** Upstream entry over D3's inputs with `git -C "$SPECS_PATH" diff <inputs_at> <default-ref> -- <paths>` (skipped on a null baseline, said so); correction entry from the quoted argument or one question; notes entry from the base's open `## Engineering review` items. Present each proposed item with its source; one confirm question (`choices: ["Use this list (Recommended)", "Change the list (you'll be prompted)", "Cancel"]`). Then, per confirmed item, the grill's first question is the meaning question, its answer recorded as the item's kind.
- [ ] **Step 5: Phase 3 — grounding and grill (D7).** Grounding scoped to the touched themes (cite `/specify` Phase 4 and its grounding steps); archive the base per Task 1 before the first write (`UPDATE_SPEC_ARCHIVE_FAILED`); grill each item with `workflows-core:grilling-technique`; apply D5 (wording → same ID; meaning → new ID + `Superseded by`; removal → `Withdrawn`; new → next free number); `Version` +1; `inputs_at` = the SHA captured at Phase 0; recount `Open questions`; tick adopted notes `- [x] … adopted in Version <N>`.
- [ ] **Step 6: Phase 4 — pre-lint, review, triage, stamps (D7; Review Focus 5).** Cite `/specify` Phase 5.5 and Phase 6, dispatching `spec-reviewer` with `Base:` and `Change list:`; write the consumption stamps by `/specify`'s step; state that nothing else outside `specification.md` and `revisions/` is written.
- [ ] **Step 7: Phase 5 — downstream report (D8).** The search sets exactly as D8 lists them; for each document, the superseded and withdrawn IDs it cites; the offers.
- [ ] **Step 8: Phases 6–8 — handoff, next steps, maintenance, cost, final report.** As `/specify`'s Phases 7–9 and Final report, by citation; next step via `next-phase-offer pm`.
- [ ] **Step 9: The docs page.** Synopsis from Phase 0's usage; phases from the `## Phase` headings; gates from the reviewer dispatch; the stops; a mermaid diagram of the run (quote any label holding `[ ] ( ) { } |` or `#`).
- [ ] **Step 10: Verify.** `./scripts/check-docs.sh --root .`, `python3 scripts/reference-parts.py check-questions`, `check-citations`, `./scripts/check-id-grammar.sh --root .`, `node scripts/mermaid/check-mermaid.mjs --root .` (after `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund`) → each exit 0. `grep -c 'UPDATE_SPEC_' plugins/product-workflows/commands/update-spec.md` ≥ 5.
- [ ] **Step 11: Commit** `feat(product-workflows): /update-spec — revise a merged specification in place`.

### Task 5: every reader of specification IDs skips non-live items (D6)

**Files (re-derive first, Step 1):**
- Modify: `plugins/dev-workflows/commands/design.md` (Phase 2 extraction), `plugins/dev-workflows/agents/design-reviewer.md:84` (traceability), `plugins/dev-workflows/agents/interface-designer.md:34` (`spec_lines`), `plugins/dev-workflows/references/design-format.md` (coverage table), `plugins/dev-workflows/commands/implement.md` (`in_scope_ids`), `plugins/dev-workflows/agents/code-review.md` (`applicable_spec`), `plugins/dev-workflows/commands/conformance.md:95` and `references/handoff/conformance-tracer.md` (trace), `plugins/product-workflows/commands/epics.md:438-443` (Phase 2.6 parse), `plugins/product-workflows/references/proposal-format.md:145` (test-case count), `plugins/workflows-core/references/escalation-rules.md:498` where it enumerates.

**Interfaces:**
- Consumes: Task 1's live-items rule — cite `product-workflows:specification-format` § Identifier conventions (a `dev-workflows` file cites it by its plugin-qualified name and reads it the way that file already reads `specification-format`; where a file does not yet read it, one sentence restating the rule is allowed only with the citation beside it).

- [ ] **Step 1: Re-derive the set.** `grep -rln '\[Uxx\]\|\[ACxx\]\|\[TCxx\]\|### \[U\|#### \[AC\|\*\*\[TC' plugins/*/commands plugins/*/agents plugins/*/references` — every hit that enumerates, covers, traces or counts gets an edit; a hit that only names the shape does not. Record the set in the commit message and update Task 1's reader list to match it exactly.
- [ ] **Step 2: Edit each site** with one clause: "live items only (`specification-format` § Identifier conventions)".
- [ ] **Step 3: Verify.** `grep -rl 'live items only\|live item' <the set>` returns every file of the set; full gate chain `bash $S/gates.sh` → `EXIT=0`.
- [ ] **Step 4: Commit** `feat(dev-workflows, product-workflows, workflows-core): readers of specification IDs skip superseded and withdrawn items`.

### Task 6: next-step offers point at `/update-spec` where a merged specification exists (D4)

**Files:**
- Modify: `plugins/product-workflows/commands/update-prd.md:192,199,224` (Phase 6's spec route), `plugins/workflows-core/references/next-phase-offer.md:204-205` (pm lane: `/update-prd`'s node and a new `/product-workflows:update-spec <KEY>` node → `/dev-workflows:design` or `/epics` per D8), `plugins/dev-workflows/commands/conformance.md:334` (the note's recommendation).
- Regenerate: `python3 scripts/reference-parts.py generate`.

- [ ] **Step 1:** In each, "`/product-workflows:update-spec <KEY>` where a merged `specification.md` exists, `/product-workflows:specify <KEY>` where none does". Keep `/update-prd`'s array within four options.
- [ ] **Step 2: Verify.** `python3 scripts/reference-parts.py check-parts` → exit 0; `grep -c 'update-spec' plugins/workflows-core/reference-parts/next-phase-offer/pm.md` ≥ 1.
- [ ] **Step 3: Commit** `feat(product-workflows, dev-workflows, workflows-core): next steps offer /update-spec for a merged specification`.

### Task 7: the docs tree and the mermaid diagrams

**Files:**
- Modify: `plugins/product-workflows/docs/README.md` (command index), `docs/workflow.md`, `docs/roles-and-phases.md`, `docs/getting-started.md`, `docs/commands/update-prd.md`, `docs/reference/agents.md` (`spec-reviewer` used by), `docs/reference/model-routing.md`, `docs/reference/session-cost.md`, `docs/reference/resume-and-checkpoints.md`; `plugins/dev-workflows/docs/workflow.md`; `plugins/workflows-core/docs/family-map.md`; every other page `grep -rl 'product-workflows:specify\|/specify' plugins/*/docs` lists where it enumerates the product commands or the specification step.

- [ ] **Step 1: Mermaid.** List the blocks that draw the specification step: `grep -rln '```mermaid' plugins/*/docs | xargs grep -l 'specify'`, then read each; in each that draws `/specify` as a node, add `/update-spec` with an edge back into the specification it revises (from `/update-prd` where that node exists, and from the design/conformance feedback where drawn).
- [ ] **Step 2: Prose.** Each enumeration of product-workflows' commands gains `/update-spec`; each sentence that says a specification can only be rewritten is swept.
- [ ] **Step 3: Verify.** mermaid gate → exit 0; `./scripts/check-docs.sh --root .` → exit 0.
- [ ] **Step 4: Commit** `docs(product-workflows, dev-workflows, workflows-core): /update-spec in the docs and the workflow diagrams`.

### Task 8: instruction tiers and counts

**Files:**
- Modify: `CLAUDE.md` (product-workflows' command count and list), `.claude/rules/product-workflows.md` (map line for `/update-spec`; the `fifteen of sixteen` model-routing phrasing), `.claude/rules/workflows-core.md` (model-routing callers, run-flags sets), `.claude/rules/workflows-core-git.md` (`commit-artifacts` writers, `handoff-to-main` producers, `require-on-main` consumers, the implementation-repository halves), `.claude/rules/docs-grounding.md` (docs and architecture grounding consumers), `.claude/rules/brd-route.md` (BRD route tail names `/specify`; add `/update-spec` where a merged spec is revised), `plugins/product-workflows/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` descriptions.

- [ ] **Step 1: Re-derive each number** with the recipe beside it in the file (e.g. `ls plugins/product-workflows/commands | wc -l`; `grep -l 'workflows-core:model-routing' plugins/*/commands/*.md | wc -l`; ``grep -lE 'commit-artifacts` entry point|args: "specs-repo-git commit-artifacts' plugins/*/commands/*.md | wc -l``), and write the new value beside its recipe.
- [ ] **Step 2: Descriptions.** Rewrite `product-workflows`' blurb to name `/update-spec` within 1024 characters; `python3 scripts/validate-catalog.py` → exit 0 and no >900 warning added.
- [ ] **Step 3: Verify.** `python3 scripts/validate-catalog.py` → exit 0; `wc -c CLAUDE.md` < 36000.
- [ ] **Step 4: Commit** (`git add -f` for `.claude/rules/*`) `docs: instruction tiers name /update-spec; counts re-derived`.

### Task 9: release, to-fix, gates, review

**Files:**
- Modify: `plugins/product-workflows/.claude-plugin/plugin.json`, `plugins/dev-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, the three `marketplace.json` entries, the three `CHANGELOG.md`s (dated sections), `.claude/rules/plugin-updates-coupling.md` (one bullet: update the three together — what breaks with an older `workflows-core` pre-lint or an older `dev-workflows` reader), `docs/superpowers/to-fix.md` (delete D19; add **document lineage** as a design item, its text the design's § Follow-up, five bullets condensed).

- [ ] **Step 1: Versions.** `git fetch origin`; read each plugin's version on `origin/main`; minor-bump each; plugin.json and marketplace entry together.
- [ ] **Step 2: Full gate chain.** `bash $S/gates.sh` (after the mermaid `npm ci`) → `EXIT=0`.
- [ ] **Step 3: Independent review.** A read-only Opus subagent reviews `git diff origin/main...HEAD` against the design's D1–D9 and Review Focus 1–5, greps for every heading scan of specification IDs not taught the live-items rule, and runs the claim sweep on "rewrite only", "not this command's yet", the command counts and the consumer sets. Apply survivors; re-review the delta until clean.
- [ ] **Step 4: Commit, push, PR.** `git push -u origin feat/update-spec`; `env -u GITHUB_TOKEN gh pr create --base main …`; if `gh pr view --json mergeable` says CONFLICTING, merge `origin/main` in and renumber.

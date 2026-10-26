# Fix batches for the 2026-10-26 review

**Date:** 2026-10-26. **Reviewed commit:** `0e02e28b` (`0e02e28b1b83e362c592dd45cbf287195508b7cb`).
**Inputs:** `docs/superpowers/reviews/2026-10-26-bugs-review.md` (273 defects), `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md` (64 gaps), and the open items of `docs/superpowers/to-fix.md` (C2, C9, D1–D16, L2; E1–E4 are out of scope).

Every one of the 337 review IDs appears in this file exactly once in bold: as an entry of a batch, as a *merge into* note, as a design track, or as a decision. Other mentions of an ID are plain text. The coverage check at the end counts the bold forms.

## How to run a batch

1. **Work on a branch per batch.** If the checkout is shared with another session, use `git worktree add`, never `git checkout`, and verify the branch with `git branch --show-current` immediately before each commit (`CLAUDE.md` § Git).
2. **Read the area's `.claude/rules/` file first,** with the Read tool, by opening a file in the area. Each batch names the rules files that load for its files.
3. **Confirm the batch's `low` and `medium` confidence entries first.** Each batch lists them under *Confirm first*. Each entry's *Confidence* line says what would confirm it. A defect that does not reproduce is dropped: append `— **Dropped: does not reproduce at <sha>**` to its heading in the review file, with one line saying what was checked.
4. **Re-locate each defect by its quoted text,** not by its line number: the line numbers are at `0e02e28b`, and the tree has moved.
5. **Follow `CLAUDE.md` § Editing discipline.** Run the claim-expiry sweep (`.claude/rules/claim-sweep.md`, all eight refinements, with refinement 7's before-and-after count of the literal string). Apply the sentence-context checks and re-derive every number you write. `workflows-core:instruction-file-maintenance` binds any edit to `CLAUDE.md`, a rules file or a `references/*.md`.
6. **Bump the version of every plugin touched,** in `plugin.json` and its `marketplace.json` entry. Add a dated `CHANGELOG.md` section to each. Where a `workflows-core` reference changes, add a coupling bullet to `.claude/rules/plugin-updates.md` naming the dependent versions that must be installed with it. Never edit a file under `plugins/workflows-core/reference-parts/`: regenerate it with `scripts/reference-parts.py`.
7. **Run the gate chain** from `.github/workflows/validate-catalog.yml`, its `run:` steps in order, as one `&&` chain, and read the chain's own exit code.
8. **In the same commit as the fix,** mark each fixed entry in its review file by appending `— **Fixed in <sha>**` to its heading, and delete each fixed item from `docs/superpowers/to-fix.md`. Where a batch adds a `scripts/check-docs.sh` check, note that it widens E1's port.

**Order.** Batches B01–B15 hold a MAJOR, B16–B29 hold only MINOR and NIT entries and gaps, and B30–B34 are documentation only. Within a tier, shared-reference batches come before plugin batches. Where a later batch must follow an earlier one (for example B13 after B03, or B34 after the product batches), its notes say so.

## Overview

| Batch | Theme | Plugins / files | Entries | MAJORs | Confirm first |
|---|---|---|---|---|---|
| [B01](#b01--specs-repo-git-and-phase-handoff-merged-branch-tests-stale-refs-b-prime-stops) | specs-repo-git and phase-handoff: merged-branch tests, stale refs, B-prime stops | workflows-core (specs-repo-git, phase-handoff), dev-workflows | 10 + D1, D2, D14, D15 | 1 | FBA-B9, FBB-B39, FBB-B30 |
| [B02](#b02--the-cost-path-session-resolution-the-cwd-slug-and-cost-emission-text) | The cost path: session resolution, the cwd slug and cost-emission text | workflows-core (cost-emission, run-flags, session-diagnosis, feedback-emission) | 8 | 2 | CORE-B2, CORE-B7, CORE-B10 |
| [B03](#b03--implementation-format-1-4-and-5-the-merged-test-and-the-release-notes-read-bound) | implementation-format §1, §4 and §5: the merged test and the release-notes read bound | workflows-core (implementation-format), docs-workflows, dev-workflows | 3 + C2, C9 | 1 | DOC-B-B1, IMP-B2 |
| [B04](#b04--security-workflows-scan-registerpy-and-the-security-docs-pages) | security-workflows: /scan, register.py and the security docs pages | security-workflows | 10 + L2 | 1 | SEC-B2, SEC-B3, SEC-B4, DQD-B9, DQD-B10 |
| [B05](#b05--dev-workflows-ready-design-and-conformance) | dev-workflows: /ready, /design and /conformance | dev-workflows (/ready, /design, /conformance) | 12 + D3 | 1 | DEV-B1, DEV-B3, FBB-B23, FBB-B24, FBB-B25, FBB-B26, FBB-B27, FBB-B28, FBB-B29 |
| [B06](#b06--dev-workflows-vuln-and-upgrade-orchestration-and-agents) | dev-workflows: /vuln and /upgrade orchestration and agents | dev-workflows (/vuln, /upgrade) | 10 | 3 | VU-B2, VU-B3, VU-B11, VU-B12 |
| [B07](#b07--product-workflows-brd-slice-key-and-next-epic-handling-in-create-ard-and-specify) | product-workflows: BRD-slice key and Next-Epic handling in /create-ard and /specify | product-workflows (/create-ard, /specify) | 11 + D16 | 3 | PRD2-ARD-B3, PRD2-ARD-B6, PRD2-SPEC-B3, PRD2-SPEC-B6, PRD2-SPEC-B9 |
| [B08](#b08--product-workflows-create-ard-and-specify-phase-order-overwrite-guard-and-format) | product-workflows: /create-ard and /specify phase order, overwrite guard and format | product-workflows (/create-ard, /specify, /epics Phase 1) | 14 + D6 | 1 | PRD2-ARD-B7, PRD2-ARD-B8, PRD2-ARD-B11, FBB-B14 |
| [B09](#b09--product-workflows-prd-proposal-brd-proposal-and-proposal-format) | product-workflows: /prd-proposal, /brd-proposal and proposal-format | product-workflows (proposals) | 11 | 1 | PRD2-PROP-B1, PRD2-PROP-B3, PRD2-PROP-B4, PRD2-PROP-B6, FBB-B10, FBB-B11, FBB-B12 |
| [B10](#b10--product-workflows-brd-reconcile-re-run-recovery) | product-workflows: /brd-reconcile re-run recovery | product-workflows (/brd-reconcile) | 6 | 3 | BRD3-B3, BRD3-B5, BRD3-B19 |
| [B11](#b11--product-workflows-brd-package-and-bundle-packaging) | product-workflows: /brd-package and bundle-packaging | product-workflows (/brd-package) | 11 | 1 | BRD3-B4, BRD3-B10, BRD3-B12, BRD3-B14, BRD3-B15, FBB-B45 |
| [B12](#b12--docs-workflows-document-phases-58-to-85) | docs-workflows: /document Phases 5.8 to 8.5 | docs-workflows (/document) | 11 + D4 | 3 | DOC-A-B4, DOC-A-B5, DOC-A-B9, DOC-A-B11, DOC-A-B15 |
| [B13](#b13--docs-workflows-doc-planner-key-discovery-and-release-notes-text) | docs-workflows: doc-planner, key discovery and /release-notes text | docs-workflows (doc-planner, key discovery, /release-notes) | 10 | 1 | DOC-A-B8, DOC-B-B5, DOC-B-B6 |
| [B14](#b14--docs-workflows-the-documentation-route-docs-init-docs-brand-docs-profile-docs-serve-docs-audit) | docs-workflows: the documentation route (/docs-init, /docs-brand, /docs-profile, /docs-serve, /docs-audit) | docs-workflows (route commands and pages) | 15 | 3 | DOC-C-B2, DOC-C-B5, DOC-C-B8, DOC-C-B11 |
| [B15](#b15--the-small-plugins-obsidian-llm-wiki-guideline-reviewers-prose-style-acli) | The small plugins: obsidian-llm-wiki, guideline-reviewers, prose-style, acli | obsidian-llm-wiki, guideline-reviewers, prose-style, acli | 9 | 1 | DQW-B2, DQS-B11, DQS-B12 |
| [B16](#b16--workflows-core-escalation-rules-next-phase-offer-and-epic-picker) | workflows-core: escalation-rules, next-phase-offer and epic-picker | workflows-core (escalation-rules, next-phase-offer, epic-picker), product-workflows | 6 | 0 | BRD3-B24, FBB-B15 |
| [B17](#b17--workflows-core-feedback-follow-ups-dependencies-routing-text-and-the-test-notify-hook) | workflows-core: feedback, follow-ups, dependencies, routing text and the test-notify hook | workflows-core (feedback, follow-ups, hooks) | 8 | 0 | CORE-B8 |
| [B18](#b18--workflows-core-grounding-format-pre-lint-prd-format-and-code-scanner) | workflows-core: grounding-format, pre-lint, prd-format and code-scanner | workflows-core (grounding-format, pre-lint, prd-format, code-scanner), product-workflows | 11 | 0 | FBB-B19, FBA-B8, FBB-B40, FBB-B18 |
| [B19](#b19--class-fix-question-shape-against-escalation-rules-0-the-d13-picker-arrays) | Class fix: question shape against escalation-rules §0 (the D13 picker arrays) | workflows-core (escalation-rules §0), dev-, product-, docs-workflows, check 12 | 7 + D12, D13 | 0 | BRD2-B6, DOC-C-B3 |
| [B20](#b20--class-fix-set-specs_path-accepts-any-path) | Class fix: *Set SPECS_PATH* accepts any path | workflows-core (escalation-rules), dev-, product-workflows, check-docs | 3 + D5 | 0 | — |
| [B21](#b21--dev-workflows-implement-and-its-planner-and-test-agents) | dev-workflows: /implement and its planner and test agents | dev-workflows (/implement) | 11 | 0 | IMP-B1, FBB-B32, FBB-B38, FBB-B36, FBB-B31, FBB-B33, FBB-B37 |
| [B22](#b22--dev-workflows-the-vuln-and-upgrade-references-and-docs-pages) | dev-workflows: the /vuln and /upgrade references and docs pages | dev-workflows (/vuln, /upgrade references and pages) | 9 | 0 | — |
| [B23](#b23--product-workflows-create-prd-and-update-prd) | product-workflows: /create-prd and /update-prd | product-workflows (/create-prd, /update-prd) | 9 | 0 | PRD2-B2, PRD2-B3, FBB-B7 |
| [B24](#b24--product-workflows-epics-and-epic-writer) | product-workflows: /epics and epic-writer | product-workflows (/epics) | 9 + D8, D11 | 0 | FBB-B17, PRD-B6, PRD-B9, FBB-B20, FBB-B22 |
| [B25](#b25--product-workflows-brd-interview) | product-workflows: /brd-interview | product-workflows (/brd-interview) | 9 | 0 | BRD2-B5, BRD3-B8, BRD3-B9, FBB-B43, FBB-B44, BRD2-B7, BRD2-B10 |
| [B26](#b26--product-workflows-prd-ground-and-its-grounders) | product-workflows: /prd-ground and its grounders | product-workflows (/prd-ground) | 7 + D7, D9, D10 | 0 | BRD-B2, BRD-B3, BRD3-B20, FBA-B6, FBB-B41 |
| [B27](#b27--product-workflows-brd-split-brd-intake-and-coverage-ledger-format) | product-workflows: /brd-split, /brd-intake and coverage-ledger-format | product-workflows (/brd-split, /brd-intake) | 9 | 0 | FBA-B5, BRD3-B22 |
| [B28](#b28--class-fix-the-key-grammar-restated-outside-addressing-1) | Class fix: the key grammar restated outside addressing §1 | dev-, docs-workflows hooks; dev-, product-workflows docs; check-docs | 4 | 0 | DQP-B8 |
| [B29](#b29--gates-instruction-tiers-and-the-tracking-records) | Gates, instruction tiers and the tracking records | CLAUDE.md, .claude/rules, scripts, docs/superpowers | 4 | 0 | SCR-B4, TRK-B2 |
| [B30](#b30--class-fix-maintainer-vocabulary-on-user-pages) | Class fix: maintainer vocabulary on user pages | every plugin's docs, root README, check-docs | 10 | 0 | DQS-B8, DQW-B11 |
| [B31](#b31--class-fixes-navigation-links-and-links-that-leave-the-plugin) | Class fixes: navigation links and links that leave the plugin | every plugin's docs and README, check-docs | 8 | 0 | DQS-B5 |
| [B32](#b32--family-entry-points-and-workflows-core-docs) | Family entry points and workflows-core docs | root README, workflows-core docs | 12 | 0 | DQC-B7 |
| [B33](#b33--dev--security--and-docs-workflows-pages-and-page-set-parity) | dev-, security- and docs-workflows pages and page-set parity | dev-, security-, docs-workflows docs | 7 | 0 | DQD-B3, DQS-B9 |
| [B34](#b34--product-workflows-docs-getting-started-workflow-pages-glossary) | product-workflows docs: getting started, workflow pages, glossary | product-workflows docs | 15 | 0 | DQP-B16 |

309 entries in 34 batches, 3 merged into other entries, 8 design tracks and 17 decisions: 337 IDs.

## Batches

### B01 — specs-repo-git and phase-handoff: merged-branch tests, stale refs, B-prime stops

**Tier:** MAJOR, shared reference. **Entries:** 10, 1 MAJOR.

- **Theme:** The specs-repo git procedures: `branch-merged`, the §3.4 flush, branch cleanup and suffixes, and `require-on-main`'s rows B and B′.
- **Files:** `plugins/workflows-core/references/specs-repo-git.md`, `plugins/workflows-core/references/phase-handoff.md` (regenerate `reference-parts/` and the `require-on-main` entry-point file), `plugins/workflows-core/references/session-hygiene.md` (§1's merged check, a GIT-B1 consumer), `scripts/reference-parts.py` (GIT-G2), `plugins/dev-workflows/commands/implement.md` (IMP-B3's sentence).
- **Why together:** GIT-B1 and GIT-B2 are the known pair in `specs-repo-git` §3.4–§3.5, and FBA-B1, FBA-B2 and FBB-B39 sit in the same branch-lifecycle paragraphs. D1, D2, D14 and D15 are all row B/B′ of `require-on-main`, which FBA-B9, FBB-B30 and GIT-B5 share with the handoff consent and offline text. Regenerating the `require-on-main` file once is the reason to do GIT-G2 here.
- **Read first:** `.claude/rules/workflows-core-git.md`, `.claude/rules/workflows-core.md`, `.claude/rules/gates-reference-parts.md`.

Entries:

- **GIT-B1** (MAJOR) — squash test misses merges near changed lines
- **GIT-B2** (MINOR) — §3.4 flush commits onto an already-merged branch
- **GIT-B5** (NIT) — §3.6 misquotes the offline note it reuses
- **FBA-B1** (MINOR) — stale remote ref forces a `-2` branch suffix
- **FBA-B2** (MINOR) — merged local plugin branches never deleted
- **FBA-B9** (NIT) — re-asked consent leaves two contradictory outcome lines
- **FBB-B39** (NIT) — session files pushed to default branch go unmentioned
- **FBB-B30** (gap) — gap: no next step after a permission-refused push
- **GIT-G2** (gap) — gap: generated `require-on-main` file lacks its line count
- **IMP-B3** (NIT) — §3.4 census misses `/conformance`'s row F; add it

**to-fix.md items:** D1, D2, D14, D15.

**Confirm first:** FBA-B9 (low); FBB-B39 (medium); FBB-B30 (medium).

**Notes:** D14 still needs the user's pick between its two options; to-fix.md recommends (a), saying in B′'s stop that the operator pushes the merge, and B01 should not start D14 without that answer. D15 says fix only with a measured case. Leave it in `to-fix.md` unless the batch measures one, and say so in the commit. GIT-B1 and GIT-B2 are high on mechanics but medium on frequency: measure how often the state is reached before choosing between the two fixes GIT-B1 offers.

**Version bumps:** workflows-core minor (1.46.0); dev-workflows patch for IMP-B3. Add a `plugin-updates.md` coupling bullet if any dependent's text now relies on the new rows.

### B02 — The cost path: session resolution, the cwd slug and cost-emission text

**Tier:** MAJOR, shared reference. **Entries:** 8, 2 MAJOR.

- **Theme:** How `cost-emission` and its two copies find the session transcript, and the stale or broken text around them.
- **Files:** `plugins/workflows-core/references/cost-emission.md`, `plugins/workflows-core/references/run-flags.md` (the `skip-cost` copy), `plugins/workflows-core/references/session-diagnosis.md`, `plugins/workflows-core/references/feedback-emission.md` (CORE-B7's twin sentence), `plugins/workflows-core/references/cost-prices.yaml`.
- **Why together:** CORE-B1 and CORE-B2 are the known pair: the transcript is found by `<cwd-slug>` and then by newest file, and both copies (`run-flags`, `session-diagnosis`) must change together. CORE-B7's tier-1 sentence is the same text in `cost-emission` §8 and `feedback-emission`. The rest are small defects in the same file, cheapest to fix while it is open.
- **Read first:** `.claude/rules/workflows-core.md`.

Entries:

- **CORE-B1** (MAJOR) — newest transcript may be another session's
- **CORE-B2** (MAJOR) — cwd slug must replace every non-alphanumeric character
- **CORE-B7** (MINOR) — feedback and cost tier 1 match legacy folder only
- **CORE-B3** (MINOR) — model-onboarding checklist names too few files
- **CORE-B4** (MINOR) — §6.1 cites a nonexistent §8 tier 5
- **CORE-B9** (NIT) — "twenty-eight commands (§1)" points at wrong section
- **CORE-B10** (NIT) — stale pending check beside its settling measurement
- **CORE-B11** (NIT) — two `cost-prices.yaml` comments lag their cited page

**to-fix.md items:** none.

**Confirm first:** CORE-B2 (medium-high); CORE-B7 (medium); CORE-B10 (medium).

**Notes:** Confirm CORE-B2's slug rule against a real `~/.claude/projects/` directory name for a path holding `_` or a space before editing: the review names it the most worth confirming. For CORE-B1, prefer `session-diagnosis`'s rule (the newest transcript whose tail holds this run's own invocation) and make both copies (`cost-emission` and `run-flags`) say what `session-diagnosis` says.

**Version bumps:** workflows-core minor. No dependent changes, so no coupling bullet unless a command's restated text changes.

### B03 — implementation-format §1, §4 and §5: the merged test and the release-notes read bound

**Tier:** MAJOR, shared reference. **Entries:** 3, 1 MAJOR.

- **Theme:** The append-only record's boundaries: what counts as a merge (§5), what bounds a `/release-notes` re-read (§4), and a commit-less block (§1).
- **Files:** `plugins/workflows-core/references/implementation-format.md`, `plugins/docs-workflows/commands/release-notes.md`, `plugins/docs-workflows/references/release-note-types.md`, `plugins/dev-workflows/commands/implement.md` (Phase 4.7), `plugins/dev-workflows/commands/conformance.md` (the PRD run, verify only).
- **Why together:** C2 and C9 must be fixed in §5 only and verified against every `unit-branch` consumer. DOC-B-B1 and DOC-B-B2 are the same `# Unreleased` paragraphs in `/release-notes` and rest on §4. IMP-B2 is the §1 block shape. One version of `implementation-format` takes all three.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/release-notes.md`, `.claude/rules/dev-workflows-implement.md`, `.claude/rules/security-workflows.md` (for the `/scan` consumer).

Entries:

- **DOC-B-B1** (MAJOR) — superseding note never re-reads the superseded commits
- **DOC-B-B2** (MINOR) — `# Unreleased` supersede trigger stated two ways
- **IMP-B2** (MINOR) — Phase 4.7 appends a record for a commit-less run

**to-fix.md items:** C2, C9.

**Confirm first:** DOC-B-B1 (medium); IMP-B2 (medium).

**Notes:** Verify C2 and C9 against the PRD run and all three `unit-branch` consumers (`/implement`, `/conformance`, `/security-workflows:scan`), as to-fix.md says. CORE-G2, the §4 widened key boundary, is in the decisions list; if it is taken, it lands here.

**Version bumps:** workflows-core minor, docs-workflows minor, dev-workflows patch. Add a coupling bullet: the new §4 rule and the new `/release-notes` Phase 3 must be installed together.

### B04 — security-workflows: /scan, register.py and the security docs pages

**Tier:** MAJOR, plugin. **Entries:** 10, 1 MAJOR.

- **Theme:** `/security-workflows:scan`'s triage, the register writer, and the plugin's own docs pages.
- **Files:** `plugins/security-workflows/commands/scan.md`, `plugins/security-workflows/scripts/register.py`, `plugins/security-workflows/docs/` (`roles-and-phases.md`, `workflow.md`, `reference/security-register.md`). SEC-B2's alternative fix touches `plugins/workflows-core/references/security-register-format.md`.
- **Why together:** Every entry lands in `scan.md`, `register.py` or the pages describing them. SEC-B1, SEC-B2 and SEC-B3 are all `register.py commit`'s validation of the decisions file. SEC-G4, SEC-G5 and SEC-G7 are cheap additions to the same steps. DQD-B9 and DQD-B10 are the diagrams of the same flow.
- **Read first:** `.claude/rules/security-workflows.md`, `.claude/rules/workflows-core-git.md`.

Entries:

- **SEC-B1** (MAJOR) — re-plan after `REGISTER_MOVED` rebinds `id:<n>` decisions
- **SEC-B2** (MINOR) — `commit` accepts any status from the decisions file
- **SEC-B3** (MINOR) — empty `--by` records an ownerless accepted risk
- **SEC-B4** (MINOR) — report searched only at the scan root
- **SEC-B5** (NIT) — roles page understates which fixes are re-offered
- **SEC-G4** (gap) — gap: compare false-positive evidence with the finding location
- **SEC-G5** (gap) — gap: flag a patch verified on review only
- **SEC-G7** (gap) — gap: "linked to the fix commit" is never recorded
- **DQD-B9** (NIT) — workflow diagram draws `/conformance` as an edge label
- **DQD-B10** (NIT) — status diagram lacks a `reopened → open` edge

**to-fix.md items:** L2.

**Confirm first:** SEC-B2 (medium); SEC-B3 (medium); SEC-B4 (low); DQD-B9 (medium); DQD-B10 (medium).

**Notes:** L2 rides here: this is the first batch whose verification is a live run that writes `resume.md`, and `/scan` writes the Security Engineer offer whose register slug L2 checks. Confirm SEC-B4 with a live change scan started from a subdirectory. For SEC-B2, prefer making `commit` refuse the bad statuses over narrowing the claim, and keep the `security-register-format` text unchanged unless the refusal changes what it says; if it must change, bump workflows-core with a coupling bullet. For SEC-G7, pick the cheaper edit (correct the claim to "linked to the scan that closed it").

**Version bumps:** security-workflows minor (0.4.0); workflows-core only if `security-register-format` changes.

### B05 — dev-workflows: /ready, /design and /conformance

**Tier:** MAJOR, plugin. **Entries:** 12, 1 MAJOR.

- **Theme:** The three dev commands other than `/implement` and `/vuln`, plus `design-format` and the `/conformance` handoff and record formats.
- **Files:** `plugins/dev-workflows/commands/ready.md`, `design.md`, `conformance.md`; `plugins/dev-workflows/references/design-format.md`, `references/conformance-format.md`, `references/handoff/conformance-tracer.md`; `plugins/dev-workflows/docs/commands/ready.md`, `design.md`.
- **Why together:** DEV-B1, DEV-B2 and D3 are `/ready`'s preflight and gate paragraphs. DEV-B3 to DEV-B5 and FBB-B23 to FBB-B25 are `/design`'s loop, stop text, fan-out brief and format. FBB-B26 to FBB-B29 are `/conformance`'s walk, tracer handoff and record. DEV-B3 is the same class as PRD2-SPEC-B1 (a *Next Epic* loop that skips a phase); fix the two in the same style.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/workflows-core-git.md`, `.claude/rules/product-workflows.md` (it loads for `design.md` and `ready.md`).

Entries:

- **DEV-B1** (MAJOR) — dirty-checkout question fires every session-branch run
- **DEV-B2** (MINOR) — false "creates no branch" invariant in session-branch mode
- **DEV-B3** (MINOR) — *Next Epic* loop skips Phase 1.5 classification
- **DEV-B4** (MINOR) — docs page quotes a stop message no longer printed
- **DEV-B5** (NIT) — author's note leaked into `DESIGN_NO_SPEC` message
- **FBB-B23** (gap) — gap: prompt for framework auto-configuration defaults
- **FBB-B24** (MINOR) — fan-out brief lacks spec literals and settled values
- **FBB-B25** (gap) — gap: rollback-ratio rule ignores other denominator feeders
- **FBB-B26** (gap) — gap: group conformance discrepancies sharing a cause
- **FBB-B27** (NIT) — walk's question and rationale cadence unstated
- **FBB-B28** (MINOR) — tracer handoff has no file input or output
- **FBB-B29** (MINOR) — `not-checkable` requirements are count-only in the record

**to-fix.md items:** D3.

**Confirm first:** DEV-B1 (medium); DEV-B3 (medium); FBB-B23 (medium); FBB-B24 (medium); FBB-B25 (medium); FBB-B26 (medium); FBB-B27 (low); FBB-B28 (medium); FBB-B29 (medium).

**Notes:** DEV-B1 was worked out from §8.3's stated behaviour, not reproduced: reproduce it in a session-branch checkout first. D3 says to measure which consumers list the working tree rather than gate before widening; do that measurement first and record it in the commit.

**Version bumps:** dev-workflows minor (4.33.0 or later: 4.32.0 is piece review's).

### B06 — dev-workflows: /vuln and /upgrade orchestration and agents

**Tier:** MAJOR, plugin. **Entries:** 10, 3 MAJOR.

- **Theme:** The `/vuln` and `/upgrade` commands and their fixer, executor and research agents.
- **Files:** `plugins/dev-workflows/commands/vuln.md`, `upgrade.md`; `plugins/dev-workflows/agents/vuln-fixer.md`, `upgrade-executor.md`, `vuln-research.md`; `plugins/dev-workflows/references/handoff/vuln-fixer.md`, `handoff/upgrade-executor.md`.
- **Why together:** VU-B1, VU-B2 and VU-B3 are the known cluster: the regression loop, the tree the fix is computed on, and detection. VU-B4 is the same return-status table as VU-B1. The rest are Step 0 and the branch, commit and dispatch text of the same two commands.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/workflows-core-bounded-run.md`, `.claude/rules/workflows-core-git.md`.

Entries:

- **VU-B1** (MAJOR) — auto-fixed regression returned as pass without re-verify
- **VU-B2** (MAJOR) — research reads the tree before moving onto base
- **VU-B3** (MAJOR) — transitive-only Maven/Gradle libraries reported `NOT_IN_REPO`
- **VU-B4** (MINOR) — `keep-anyway` regression has no return status
- **VU-B9** (MINOR) — `clean_finish` flips for a component never pushed
- **VU-B10** (MINOR) — `/upgrade` writes keys it can never have
- **VU-B11** (MINOR) — Step 0 parses `--allow-install-scripts` value as address
- **VU-B12** (MINOR) — per-CVE branching gives no switch-back instruction
- **VU-B13** (MINOR) — commit template both project-styled and verbatim
- **VU-B16** (NIT) — executor dispatch names no model for `SIGNIFICANT`

**to-fix.md items:** none.

**Confirm first:** VU-B2 (medium); VU-B3 (medium); VU-B11 (medium); VU-B12 (medium).

**Notes:** VU-B10's fix depends on the VU-G3 decision (drop the dead prose, recommended). VU-G2's live run, in the decisions list, is the verification for this batch and the next /vuln batch together.

**Version bumps:** dev-workflows minor.

### B07 — product-workflows: BRD-slice key and Next-Epic handling in /create-ard and /specify

**Tier:** MAJOR, plugin. **Entries:** 11, 3 MAJOR.

- **Theme:** What `/create-ard` and `/specify` do on a BRD slice and on an Epic under one: the key they pass on, the frontmatter they write, the ARD they resolve, and the *Next Epic* loop and next-step routing.
- **Files:** `plugins/product-workflows/commands/create-ard.md`, `specify.md`; `plugins/product-workflows/references/ard-format.md`; `docs/commands/create-ard.md`, `docs/commands/specify.md`; `/create-prd`'s `*_REGISTER_NOT_ON_MAIN` sentence (D16).
- **Why together:** This is the PRD2 cluster the review names: the same slice-key, slice-frontmatter and next-step paragraphs recur in both commands, so fixing one without the other leaves a live contradiction. D16 is the shared stop sentence of `/create-prd`, `/create-ard` and `/specify`.
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/brd-route.md`, `.claude/rules/brd-route-detection.md`, `.claude/rules/workflows-core.md`.

Entries:

- **PRD2-ARD-B1** (MAJOR) — Epic run under a slice writes slice frontmatter
- **PRD2-ARD-B2** (MAJOR) — slice without `prd.md` passes `key: null` onward
- **PRD2-ARD-B3** (MINOR) — refine reads the slice's own prior ARD as inherited
- **PRD2-ARD-B5** (MINOR) — Phase 7 names `/prd-proposal` where it cannot run
- **PRD2-ARD-B6** (MINOR) — offers `/design` without testing for merged spec
- **PRD2-SPEC-B1** (MAJOR) — *Next Epic* skips Phase 2.5, uses previous ARD
- **PRD2-SPEC-B3** (MINOR) — BRD Epic run passes `epic: <SLICE-KEY>` to resolution
- **PRD2-SPEC-B4** (MINOR) — next step routes by address, not chosen spec
- **PRD2-SPEC-B6** (MINOR) — slice without `prd.md` passes key `null` to emitters
- **PRD2-SPEC-B8** (MINOR) — commercial step names `/prd-proposal` on a slice
- **PRD2-SPEC-B9** (NIT) — handoff always declares `<prd_dir>/decisions.md`

**to-fix.md items:** D16.

**Confirm first:** PRD2-ARD-B3 (medium); PRD2-ARD-B6 (medium); PRD2-SPEC-B3 (medium); PRD2-SPEC-B6 (medium); PRD2-SPEC-B9 (medium).

**Notes:** D16 says to check each row the general form reports (D, E, the C rows) before making the sentence true or narrowing it; do that first. PRD2-ARD-B2 and PRD2-SPEC-B6 should pass the slice key, as `/create-prd` does; make the two commands use one sentence.

**Version bumps:** product-workflows minor (3.37.0).

### B08 — product-workflows: /create-ard and /specify phase order, overwrite guard and format

**Tier:** MAJOR, plugin. **Entries:** 14, 1 MAJOR.

- **Theme:** The rest of `/create-ard` and `/specify`: the overwrite of a published spec, the order of the Phase 0/1 questions, per-area ARDs, stop codes, and `specification-format`.
- **Files:** `plugins/product-workflows/commands/create-ard.md`, `specify.md`; `plugins/product-workflows/references/specification-format.md`; `plugins/product-workflows/agents/spec-reviewer.md` (PRD2-SPEC-G1); `docs/commands/create-ard.md`, `docs/commands/specify.md`. D6's `/epics` Phase 1 site is in `epics.md`.
- **Why together:** PRD2-ARD-B7 and D6 are the same step ordering (ask about refresh and `$REPOS_PATH` only once code scanning is on) in `/create-ard`, `/specify` and `/epics`. PRD2-SPEC-B2 and PRD2-SPEC-B5 are `/specify`'s Phase 0. The docs-page entries (PRD2-ARD-B9, B10, PRD2-SPEC-B10) describe exactly these phases. The three gaps add text to the same Phase 5–6 and format file.
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/brd-route.md`, `.claude/rules/docs-grounding.md`.

Entries:

- **PRD2-SPEC-B2** (MAJOR) — published `specification.md` silently overwritten, *revise* undefined
- **PRD2-SPEC-B5** (MINOR) — address resolved before `$SPECS_PATH` check
- **PRD2-SPEC-B7** (MINOR) — pre-lint may renumber any duplicate ID
- **PRD2-SPEC-B10** (NIT) — docs example nests a slice wrongly
- **PRD2-ARD-B4** (MINOR) — *Start fresh* falls through over a ref-only ARD
- **PRD2-ARD-B7** (MINOR) — `$REPOS_PATH` gauged before code scan is known
- **PRD2-ARD-B8** (MINOR) — prior-ARD test ignores `ard-<area>.md` files
- **PRD2-ARD-B9** (MINOR) — docs misstate `/brd-split` remedy conditions
- **PRD2-ARD-B10** (NIT) — smaller docs-page disagreements with the command
- **PRD2-ARD-B11** (NIT) — three stops lack codes and `emit-block` class
- **FBA-B3** (MINOR) — optionality advisory's "small" never defined
- **FBB-B14** (gap) — gap: `specification-format` lacks three recurring shapes
- **FBA-G6** (gap) — gap: guidance for renumbering ACs and TCs
- **PRD2-SPEC-G1** (gap) — gap: `spec-reviewer` gets no contract input

**to-fix.md items:** D6.

**Confirm first:** PRD2-ARD-B7 (medium); PRD2-ARD-B8 (medium); PRD2-ARD-B11 (medium); FBB-B14 (medium).

**Notes:** D6 also covers `/epics` Phase 1; fix that site here too, in the same wording, and leave `/epics`' other text to B24. PRD2-SPEC-B2 was re-read by the coordinator and holds: define *revise* and guard `Published: yes`.

**Version bumps:** product-workflows minor. If B07 and B08 run back to back, one minor bump can cover both.

### B09 — product-workflows: /prd-proposal, /brd-proposal and proposal-format

**Tier:** MAJOR, plugin. **Entries:** 11, 1 MAJOR.

- **Theme:** The effort proposals: what they commit, which register counts as settled, the umbrella forms, and the format's checks.
- **Files:** `plugins/product-workflows/commands/prd-proposal.md`, `brd-proposal.md`; `plugins/product-workflows/agents/proposal-reviewer.md`; `plugins/product-workflows/references/proposal-format.md`; `plugins/product-workflows/scripts/proposal-record.py`; `docs/commands/prd-proposal.md`.
- **Why together:** Every entry is in the proposal pair, its reviewer or its format. FBB-B1 is a staging bug in the same Phase as PRD2-PROP-B6's revision test, and FBB-B9 to FBB-B12 are reviewer and format checks next to PRD2-PROP-B3.
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/workflows-core-git.md`.

Entries:

- **FBB-B1** (MAJOR) — `proposal-profile.yml` called committed, never staged
- **PRD2-PROP-B1** (MINOR) — open-only register counts as tier-2 settled
- **PRD2-PROP-B2** (MINOR) — Phase 7 coverage misses a slice
- **PRD2-PROP-B3** (MINOR) — reviewer check 6 has no umbrella form
- **PRD2-PROP-B4** (MINOR) — legacy `<KEY>_*.md` PRD read path is wrong
- **PRD2-PROP-B5** (NIT) — docs example misorders the tier-2 offer
- **PRD2-PROP-B6** (NIT) — brief without proposal counts as a revision
- **FBB-B9** (MINOR) — false rounding claim in `proposal-format` §6
- **FBB-B10** (gap) — gap: check decision attribution in proposal prose
- **FBB-B11** (gap) — gap: sweep should quote conflicts it finds
- **FBB-B12** (gap) — gap: require success measures to be traced

**to-fix.md items:** none.

**Confirm first:** PRD2-PROP-B1 (medium); PRD2-PROP-B3 (medium); PRD2-PROP-B4 (medium); PRD2-PROP-B6 (low); FBB-B10 (medium); FBB-B11 (medium); FBB-B12 (medium).

**Notes:** FBB-B1's fix is in the command's staging list, not in `specs-repo-git`; if it needs a new bookkeeping path class there, move that part to B16/B17.

**Version bumps:** product-workflows minor.

### B10 — product-workflows: /brd-reconcile re-run recovery

**Tier:** MAJOR, plugin. **Entries:** 6, 3 MAJOR.

- **Theme:** What a `/brd-reconcile` re-run can see of a run that stopped after Phase 5, and the remedies and gates that depend on it.
- **Files:** `plugins/product-workflows/commands/brd-reconcile.md`, `plugins/product-workflows/references/decision-register-format.md`, `docs/commands/brd-reconcile.md`.
- **Why together:** BRD3-B1, BRD3-B2 and BRD3-B3 are the known cluster: the same-review rule, the reconciliation record's write point and the changed-id set. BRD3-B5, BRD3-B13 and BRD3-B19 are the remedies and gate text that point into those phases.
- **Read first:** `.claude/rules/brd-route.md`, `.claude/rules/brd-route-detection.md`, `.claude/rules/product-workflows.md`.

Entries:

- **BRD3-B1** (MAJOR) — re-run mints a second `[CD#n]` for one question
- **BRD3-B2** (MAJOR) — stop after Phase 5 loses resolutions and sweep
- **BRD3-B3** (MAJOR) — documented re-run remedy writes nothing
- **BRD3-B5** (MINOR) — rebaseline fix names the wrong BRD
- **BRD3-B13** (MINOR) — empty-digest remedy cannot be followed
- **BRD3-B19** (MINOR) — gates on newest prompt, not the reviewed one

**to-fix.md items:** none.

**Confirm first:** BRD3-B3 (medium-high); BRD3-B5 (medium); BRD3-B19 (medium).

**Notes:** BRD-G1 (carry-forward for a `needs-a-human` item) is in the decisions list; if its answer is to widen `/brd-interview`'s trigger, that lands in B25, not here.

**Version bumps:** product-workflows minor.

### B11 — product-workflows: /brd-package and bundle-packaging

**Tier:** MAJOR, plugin. **Entries:** 11, 1 MAJOR.

- **Theme:** How `/brd-package` assembles the customer bundle, copies prerequisites, renders headings, and re-runs on the same day.
- **Files:** `plugins/product-workflows/commands/brd-package.md`, `plugins/product-workflows/references/bundle-packaging.md`, `plugins/product-workflows/agents/brd-package-reviewer.md`, `agents/customer-review-reader.md`, `docs/commands/brd-package.md`; FBB-B45's last part touches `commands/brd-reconcile.md`.
- **Why together:** BRD3-B4, BRD3-B10 and BRD3-B11 are the same "copy the prerequisite's bundle" rules. BRD3-B14 and BRD3-B15 are §7's relations, and the docs-page entries describe the same phases.
- **Read first:** `.claude/rules/brd-route.md`, `.claude/rules/product-workflows.md`.

Entries:

- **BRD3-B4** (MAJOR) — wholesale prerequisite copy brings unpartitioned keys
- **BRD3-B10** (MINOR) — copied package brings its own prompt and manifest
- **BRD3-B11** (MINOR) — rule 5 marks a line rule 4 strips
- **BRD3-B12** (MINOR) — same-day re-run overwrites self-review and prompt
- **BRD3-B14** (MINOR) — §7 relation 1 skips part 6's in-scope list
- **BRD3-B15** (MINOR) — §7.1 calls an untestable fraction testable
- **BRD3-B16** (MINOR) — reviewer `INPUT_MISSING` stop has no code
- **BRD3-B18** (MINOR) — docs misdescribe the heading renumbering
- **BRD-B1** (MINOR) — docs say every `fixed` correction changes the bundle
- **BRD2-B8** (NIT) — agent examples use a key the caller refuses
- **FBB-B45** (MINOR) — display binding, scan tooling, attribution, section-12 names

**to-fix.md items:** none.

**Confirm first:** BRD3-B4 (medium); BRD3-B10 (medium); BRD3-B12 (medium); BRD3-B14 (medium); BRD3-B15 (medium); FBB-B45 (medium).

**Notes:** FBB-B45 bundles six small asks; split off the "ship a deterministic scan script" part as a follow-up if it grows past a few lines, and say so in the review file.

**Version bumps:** product-workflows minor.

### B12 — docs-workflows: /document Phases 5.8 to 8.5

**Tier:** MAJOR, plugin. **Entries:** 11, 3 MAJOR.

- **Theme:** `/document`'s flow after the discrepancy check: the hand-offs between Phases 5.8, 6.1–6.5, 7 and 8.5, branching, and the stale writer and handoff text around them.
- **Files:** `plugins/docs-workflows/commands/document.md`, `plugins/docs-workflows/references/finish-and-handoff.md`, `plugins/docs-workflows/references/toolchain-preflight.md`, `docs/commands/document.md`.
- **Why together:** DOC-A-B1, DOC-A-B2 and DOC-A-B4 with D4 are the known cluster: the phase-skipping exits and the branching decision. DOC-A-B5, B9 and B11 are the decision arrays and dispatches in the same phases, and DOC-B-B3 is the hand-off reference's claim about the same pull request.
- **Read first:** `.claude/rules/docs-workflows.md`, `.claude/rules/docs-workflows-gates.md`, `.claude/rules/workflows-core-triage.md`.

Entries:

- **DOC-A-B1** (MAJOR) — Phase 5.8 exit skips 6.1 and 6.2
- **DOC-A-B2** (MAJOR) — clean-style exit skips Phase 6.5 render check
- **DOC-A-B4** (MAJOR) — declined branching still commits; squash base unset
- **DOC-A-B5** (MINOR) — Phase 5.8 arrays differ from `source-truth` arrays
- **DOC-A-B6** (MINOR) — stale "inline writer" model claims
- **DOC-A-B7** (MINOR) — invariant prescribes a `/clear` handoff others drop
- **DOC-A-B9** (MINOR) — PASS WITH RECOMMENDATIONS dispatches fixer for MAJOR only
- **DOC-A-B11** (MINOR) — 6.4 labels fixer dispatch as linter re-run
- **DOC-A-B12** (NIT) — routing text names "the folder read" as agent
- **DOC-A-B15** (NIT) — toolchain Cancel claims nothing written; false mid-run
- **DOC-B-B3** (MINOR) — "no command opens a pull request" is false

**to-fix.md items:** D4.

**Confirm first:** DOC-A-B4 (medium); DOC-A-B5 (medium); DOC-A-B9 (medium); DOC-A-B11 (medium); DOC-A-B15 (medium).

**Notes:** DOC-A-B1 and DOC-A-B2 were re-read by the coordinator and hold. For DOC-A-B5, change `/document`'s arrays to match `source-truth` §7.2/§7.3 rather than the reference; a reference change moves to B16.

**Version bumps:** docs-workflows minor (1.19.0).

### B13 — docs-workflows: doc-planner, key discovery and /release-notes text

**Tier:** MAJOR, plugin. **Entries:** 10, 1 MAJOR.

- **Theme:** `doc-planner`'s output contract, the key-discovery script and its reference, and the smaller `/release-notes` defects.
- **Files:** `plugins/docs-workflows/agents/doc-planner.md`, `agents/doc-writer.md`; `references/docs-profiles/changelog-guidelines.md`; `references/key-discovery.md`, `scripts/key-discovery.py`; `commands/release-notes.md`, `references/release-note-types.md`; `docs/commands/document.md`, `docs/commands/release-notes.md`, `docs/reference/agents.md`.
- **Why together:** DOC-A-B3 and DOC-A-B13 are `doc-planner`; DOC-A-B8, DOC-B-B5 and DOC-B-B6 are key discovery (reference and script); DOC-B-B7 to DOC-B-B9 are `/release-notes` and its guidelines outside the B03 paragraphs.
- **Read first:** `.claude/rules/docs-workflows.md`, `.claude/rules/release-notes.md`.

Entries:

- **DOC-A-B3** (MAJOR) — mandatory `changelog:` entry on new pages
- **DOC-A-B13** (NIT) — garbled residue in `doc-planner`
- **DOC-A-B8** (MINOR) — key-discovery invoked without `--repo`
- **DOC-B-B5** (MINOR) — GitHub time budget starts after the searches
- **DOC-B-B6** (NIT) — errored repository can carry non-null `scanned`
- **DOC-A-B10** (MINOR) — docs page miscounts `/epics` phases
- **DOC-A-B14** (NIT) — agents page omits `defect-reporter`
- **DOC-B-B7** (NIT) — docs page states address rules the command lacks
- **DOC-B-B8** (NIT) — route array promises a docs link it never asks
- **DOC-B-B9** (NIT) — two wrong character counts in changelog guidelines

**to-fix.md items:** none.

**Confirm first:** DOC-A-B8 (medium); DOC-B-B5 (medium); DOC-B-B6 (medium).

**Notes:** Run B03 first: it owns the `/release-notes` paragraphs on `# Unreleased`, and DOC-B-B7 and DOC-B-B8 are near them.

**Version bumps:** docs-workflows minor.

### B14 — docs-workflows: the documentation route (/docs-init, /docs-brand, /docs-profile, /docs-serve, /docs-audit)

**Tier:** MAJOR, plugin. **Entries:** 15, 3 MAJOR.

- **Theme:** The increment-2 commands, the scaffold, and the pages that describe the route a new user follows.
- **Files:** `plugins/docs-workflows/commands/docs-init.md`, `docs-brand.md`, `docs-profile.md`, `docs-serve.md`; `agents/docs-audit-reviewer.md`; `references/docs-workflow/scaffold-tree.md`; `README.md`; `docs/getting-started.md`, `docs/docs-workflow.md`, `docs/workflow.md`, `docs/commands/docs-init.md`, `docs-profile.md`, `docs-serve.md`, `docs-audit.md`, `docs/reference/docs-backlog.md`.
- **Why together:** DOC-C-B1 and the DQW route entries all describe step 4 of the route and what follows `/docs-serve`; DOC-C-B2 and DOC-C-B5 are the stop and branch text of the same commands. DQW-B1 is a MAJOR on the getting-started page of the same plugin and costs one line.
- **Read first:** `.claude/rules/docs-workflows.md`, `.claude/rules/docs-serve.md`, `.claude/rules/docs-workflows-gates.md`.

Entries:

- **DOC-C-B1** (MAJOR) — hand-written page breaks `--strict` builds via `nav:`
- **DOC-C-B2** (MAJOR) — post-preflight stops skip the emitter tail
- **DOC-C-B4** (MINOR) — reviewer reads `docs_dir` the profile lacks
- **DOC-C-B5** (MINOR) — `NOISSUE` branch form contradicts `branch-naming` §1.4
- **DOC-C-B6** (MINOR) — domain vocabulary called a later command's job
- **DOC-C-B7** (MINOR) — `/docs-profile` page claims detections it lacks
- **DOC-C-B8** (MINOR) — Phase 6 leaves `spaces[].id` unstated
- **DOC-C-B10** (NIT) — `/docs-serve` invariant lists citations incompletely
- **DOC-C-B11** (NIT) — backlog page reads `threshold` the wrong way
- **DOC-C-B12** (NIT) — `/docs-serve` writes more than a pid record
- **DQW-B1** (MAJOR) — Update block omits `workflows-core`
- **DQW-B3** (MINOR) — "no docs yet" path skips `/docs-init`
- **DQW-B4** (MINOR) — `/docs-serve` offers `/document` as next step
- **DQW-B5** (MINOR) — README draws a third, disagreeing route
- **DQW-B6** (MINOR) — `workflow.md` versus `docs-workflow.md` split unclear

**to-fix.md items:** none.

**Confirm first:** DOC-C-B2 (medium-high); DOC-C-B5 (medium); DOC-C-B8 (medium); DOC-C-B11 (medium).

**Notes:** DOC-C-B1 is a consequence of the missing Spec 2 (DOC-D-G1, a design track); fix it here with the interim procedure the entry suggests, and let the design track replace it. For DOC-C-B5, prefer changing the three commands to `branch-naming` §1.4's form; editing §1.4 instead moves the entry to B16.

**Version bumps:** docs-workflows minor.

### B15 — The small plugins: obsidian-llm-wiki, guideline-reviewers, prose-style, acli

**Tier:** MAJOR, plugin (documentation, with one prose-style behaviour change). **Entries:** 9, 1 MAJOR.

- **Theme:** The four plugins outside the family, which have no rules file of their own: their READMEs, docs pages and one `prose-style` baseline rule.
- **Files:** `plugins/obsidian-llm-wiki/README.md` (and its `CLAUDE.md`, `hooks/hooks.json` for DQW-B2), `plugins/guideline-reviewers/docs/commands/*.md`, `plugins/prose-style/README.md` and a new `plugins/prose-style/docs/` tree, `plugins/prose-style/agents/prose-style-checker.md` (FBA-G1), `plugins/acli/README.md`, `scripts/check-docs.sh` (`PLUGIN_RELS`, for DQW-G1).
- **Why together:** Each fix lands in one of these plugins, and none couples with the family. It is placed with the MAJOR batches because DQW-B2 is a MAJOR. The batch is mostly documentation, so it comes last in that tier.
- **Read first:** none of these plugins has a rules file; read `plugins/obsidian-llm-wiki/CLAUDE.md` before editing there, and `.claude/rules/gates.md` before touching `PLUGIN_RELS`.

Entries:

- **DQW-B2** (MAJOR) — README says Stop hook runs at session end
- **DQS-B11** (MINOR) — local-install command is a personal `cc` alias
- **DQS-B12** (MINOR) — no-docs READMEs miss install, usage, troubleshooting
- **DQW-B8** (MINOR) — page hides five placeholder Spectral rules
- **DQW-B9** (MINOR) — page says nothing else needed; Python required
- **DQW-B14** (MINOR) — prose-style README stale on users, no install
- **DQW-B15** (MINOR) — acli README lacks usage and headless auth
- **FBA-G1** (gap) — gap: British-English baseline noise without an overlay
- **DQW-G1** (gap) — gap: give prose-style a `docs/` tree

**to-fix.md items:** none.

**Confirm first:** DQW-B2 (medium); DQS-B11 (medium); DQS-B12 (medium).

**Notes:** DQW-B2: confirm whether the per-turn blocking is the hook's intent before choosing between fixing the README and fixing the hook. DQW-G1 adds `prose-style` to `PLUGIN_RELS`, so check-docs will then require every page its checks expect; budget for that.

**Version bumps:** obsidian-llm-wiki patch, guideline-reviewers patch, prose-style minor (FBA-G1 changes behaviour, DQW-G1 adds docs), acli patch.

### B16 — workflows-core: escalation-rules, next-phase-offer and epic-picker

**Tier:** MINOR, shared reference. **Entries:** 6, 0 MAJOR.

- **Theme:** The rulebooks that load by part: the review-cycle rules, the next-step lanes and the picker cap.
- **Files:** `plugins/workflows-core/references/escalation-rules.md`, `next-phase-offer.md`, `epic-picker.md`, the generated `reference-parts/` (regenerate, never edit), `plugins/product-workflows/commands/epics.md` (FBB-B21's caller).
- **Why together:** All three references load by part, so one regeneration and one `check-parts` run cover them. FBB-B13, FBB-B15 and FBB-B21 are the same *Review verdict* section of `escalation-rules`; GIT-B3 and BRD3-B24 are `next-phase-offer` lanes.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/workflows-core-triage.md`, `.claude/rules/gates-reference-parts.md`.

Entries:

- **GIT-B3** (MINOR) — merge-clause table lacks *Commit failed* row
- **GIT-B4** (MINOR) — epic-picker cap example contradicts its rule
- **BRD3-B24** (NIT) — lane offers `/brd-reconcile` after every `/brd-package`
- **FBB-B13** (MINOR) — fix-cycle overlap read misses imported rules — **moved to to-fix PR1 (workflows-core 1.49.0); its part (3) is B18's**
- **FBB-B15** (MINOR) — post-verdict version line omits changed Rules
- **FBB-B21** (gap) — gap: let `/epics` apply open MINOR and NIT findings

**to-fix.md items:** none.

**Confirm first:** BRD3-B24 (low); FBB-B15 (medium).

**Notes:** BRD3-B24 is low confidence: confirm that `/brd-package` can end without a review to reconcile before narrowing the lane.

**Version bumps:** workflows-core minor; product-workflows minor for FBB-B21. Add a coupling bullet: `/epics`' new offer needs the new `escalation-rules` list.

### B17 — workflows-core: feedback, follow-ups, dependencies, routing text and the test-notify hook

**Tier:** MINOR, shared reference. **Entries:** 8, 0 MAJOR.

- **Theme:** Small defects in the workflows-core references that do not load by part, plus its one test hook.
- **Files:** `plugins/workflows-core/references/feedback-emission.md`, `followup-emission.md`, `dependencies.md`, `read-only-repos.md`, `model-routing/classification.md`; `commands/prompt-brainstorm.md`; `hooks/test-notify.sh`; `docs/reference/hooks.md`; one shared sentence on scratch directories (SEC-G6), placed in the reference `/implement` and `/scan` both cite for temporary paths.
- **Why together:** Each is a one-paragraph fix in a workflows-core file that no other batch opens. SCR-B1 and CORE-B14 are both `test-notify.sh`'s command gate and must be tested together.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/workflows-core-read-only.md`.

Entries:

- **CORE-B5** (MINOR) — `/prompt-brainstorm` has no absent-companion path
- **CORE-B8** (MINOR) — feedback `id` lacks a keyless key segment
- **CORE-B12** (NIT) — §4 parenthetical names no agents
- **GIT-B6** (NIT) — `followup-emission` mirrors nothing, then mirrors twice
- **GIT-B7** (NIT) — `read-only-repos` consumer list is short
- **SCR-B1** (MINOR) — `test-notify` reads a key Bash payloads lack
- **CORE-B14** (NIT) — `test-notify` misses single-module Gradle form
- **SEC-G6** (gap) — gap: scratch dirs and worktrees ignore the scratchpad

**to-fix.md items:** none.

**Confirm first:** CORE-B8 (medium).

**Notes:** SCR-B1: confirm the payload key against a current transcript before changing the hook (high on the key, medium that nothing else reads it). For GIT-B7, prefer the re-derive recipe over a longer list, per `CLAUDE.md`'s *Re-measure in one place*.

**Version bumps:** workflows-core minor.

### B18 — workflows-core: grounding-format, pre-lint, prd-format and code-scanner

**Tier:** MINOR, shared reference. **Entries:** 12, 0 MAJOR.

- **Theme:** The shared formats and checks the product commands write against: grounding verdicts and baselines, the pre-lint scans, `[AC#N]` grouping, and the code scanner's contract.
- **Files:** `plugins/workflows-core/references/grounding-format.md`, `pre-lint.md`, `prd-format.md`, `handoff/code-scanner.md`; `plugins/workflows-core/agents/code-scanner.md`; callers `plugins/product-workflows/commands/specify.md` (FBB-B2), `create-prd.md` (FBB-B4), `prd-ground.md` (FBB-B40), `agents/epic-writer.md` (FBB-B19).
- **Why together:** FBB-B3, FBB-B4, FBB-B19 and FBA-G7 are all `pre-lint` scans and must be re-run against each other's examples. FBA-B8, FBB-B2 and FBB-B40 are `grounding-format`. CORE-B13, FBB-B18 and FBA-G5 are the code scanner's handoff and agent.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/docs-grounding.md`, `.claude/rules/product-workflows.md`, `.claude/rules/prd-ground-verification.md`.

Entries:

- **FBB-B3** (MINOR) — placeholder scan flags literal code and markup
- **FBB-B4** (MINOR) — `/create-prd` route template fails its own pre-lint
- **FBB-B19** (MINOR) — auto-link leaves bare specs keys in limbo
- **FBA-G7** (gap) — gap: advisory for unscoped `kubectl` commands
- **FBA-B8** (MINOR) — no verdict rule for a vacuously true premise
- **FBB-B2** (MINOR) — single-valued `consumed_by` overwritten by `/specify`
- **FBB-B40** (gap) — gap: canonical layout for `grounding/baselines.md`
- **FBB-B5** (MINOR) — `prd-format` silent on `[AC#N]` grouping
- **CORE-B13** (NIT) — handoff narrows `REPO_MISSING` meaning
- **FBB-B18** (MINOR) — `code-scanner` line numbers not validated
- **FBA-G5** (gap) — gap: dependency-coupling list in the scanner brief
- **FBB-B13 part (3)** (MINOR) — `pre-lint`'s spec block: per-AC Happy-path and Negative coverage checks (moved here from B16 with PR1; the import list it also suggested is dropped — see the entry)

**to-fix.md items:** none.

**Confirm first:** FBB-B19 (medium); FBA-B8 (medium); FBB-B40 (medium); FBB-B18 (medium).

**Notes:** FBA-B8 says its fix is a design choice; write the chosen rule into the commit message so the next reviewer can check it.

**Version bumps:** workflows-core minor; product-workflows minor (FBB-B2, FBB-B4, FBB-B19, FBB-B40 callers). Add a coupling bullet for `grounding-format`'s new baselines layout and `consumed_by` shape.

### B19 — Class fix: question shape against escalation-rules §0 (the D13 picker arrays)

**Tier:** MINOR, shared reference (class fix). **Entries:** 7, 0 MAJOR.

- **Theme:** **Class: a question whose shape breaks `escalation-rules` §0** — a two-option text-plus-Cancel array "built for" a text answer, an option that needs text but carries no `(you'll be prompted …)` marker, a question with no array at all, an uncapped choice, or a `Cancel` no prose handles.
- **Files:** `plugins/workflows-core/references/escalation-rules.md` §0, `followup-emission.md` §7; every command, reference and agent holding one of the D13 arrays (re-derive them with the `grep -rhoE` the bugs file's D13 row names); `plugins/product-workflows/commands/create-prd.md`, `prd-ground.md`, `brd-reconcile.md`, `brd-package.md`; `plugins/docs-workflows/commands/release-notes.md`, `references/docs-workflow/repo-resolution.md`; `scripts/check-docs.sh` check 12 (D12).
- **Why together:** One rule broken at many sites. Decide §0's wording first (D13's two options), then fix every site against it, and extend check 12 (D12) so the same shapes fail the gate. CORE-B6's six restatements of `(approve-all | select | cancel)` move with it.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/gates.md`, plus the area rules file of each command touched.

Entries:

- **CORE-B6** (MINOR) — `select` needs text but lacks the marker
- **FBB-B6** (NIT) — "Confirm" step has no choices array
- **BRD2-B6** (MINOR) — documentation-lead question has no array
- **DOC-B-B4** (MINOR) — release-version question has no step or array
- **BRD3-B7** (MINOR) — missing-reason picker's `Cancel` unhandled
- **BRD3-B17** (MINOR) — tier picker's fourth `Cancel` unhandled
- **DOC-C-B3** (MINOR) — rung 4 choice uncapped, shape unstated

**to-fix.md items:** D12, D13.

**Confirm first:** BRD2-B6 (medium); DOC-C-B3 (medium).

**Notes:** Re-count the D13 arrays at the start (the bugs file counted about 38 at `0e02e28b`, to-fix 41 at `7c13ce05`), state the command and scope beside the number, and count again after. D12's new families must fire on no correct label: re-measure before adding, and leave `^add\b` out. The check-docs body is shared with the editions, so the D12 change joins E1's port.

**Version bumps:** workflows-core minor; dev-workflows, product-workflows and docs-workflows patch or minor, by the sites touched; add a coupling bullet if §0's wording changes what a caller must do.

### B20 — Class fix: *Set SPECS_PATH* accepts any path

**Tier:** MINOR, shared reference (class fix). **Entries:** 3, 0 MAJOR.

- **Theme:** **Class: a *Set SPECS_PATH* answer carried without the re-ask rule** — a command asks for the path and carries whatever is typed, instead of citing `escalation-rules`' *Required path environment variable unset*, which re-asks until the answer names an existing directory.
- **Files:** `plugins/workflows-core/references/escalation-rules.md` (the rule's citer list); `plugins/dev-workflows/commands/design.md`, `ready.md`, `conformance.md`; `plugins/product-workflows/commands/create-prd.md`, `update-prd.md`, `create-ard.md`, `specify.md`, `epics.md`; `plugins/product-workflows/hooks/preload-context.sh`; `plugins/product-workflows/docs/reference/environment.md`; `scripts/check-docs.sh` (a new check).
- **Why together:** One rule, seven sites (D5's three and PRD-B1's four), plus `/epics`, which has no unset step at all (PRD-B2), and the docs page that overstates the behaviour (PRD-B8). A cheap gate: every command whose text offers *Set SPECS_PATH* also cites the rule by name.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/dev-workflows.md`, `.claude/rules/product-workflows.md`, `.claude/rules/gates.md`.

Entries:

- **PRD-B1** (MINOR) — four product commands carry any typed path
- **PRD-B2** (MINOR) — `/epics` lacks an unset step and `invalid` mapping
- **PRD-B8** (NIT) — environment page overstates which commands ask

**to-fix.md items:** D5.

**Confirm first:** none; every entry is high confidence.

**Notes:** Re-derive the site list with `grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md` before and after, and state the counts in the commit.

**Version bumps:** workflows-core patch (citer list), dev-workflows minor, product-workflows minor.

### B21 — dev-workflows: /implement and its planner and test agents

**Tier:** MINOR, plugin. **Entries:** 11, 0 MAJOR.

- **Theme:** `/implement`'s branch, deferral, review-survivor and test rules, and the agents it dispatches.
- **Files:** `plugins/dev-workflows/commands/implement.md`; `agents/risk-planner.md`, `agents/test-baseliner.md`, `agents/code-writer.md`, `agents/code-review.md`; `docs/commands/implement.md`; `scripts/check-docs.sh` (IMP-G4's check).
- **Why together:** Every entry lands in `implement.md` or an agent it dispatches. The gaps (FBB-B31, FBB-B33, FBB-B37) are small rules in the same phases. IMP-G4 is a cheap check on the same file's dispatch lines.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/dev-workflows-implement.md`, `.claude/rules/dev-workflows-tests.md`.

Entries:

- **IMP-B1** (MINOR) — hard-coded branch name contradicts steps 1–2
- **IMP-B4** (NIT) — docs page agent census omits `defect-reporter`
- **FBB-B32** (MINOR) — open note written for an already-decided deferral
- **FBB-B38** (MINOR) — post-review departure leaves specs contradicting code
- **FBB-B34** (NIT) — acceptance checks not required to use fixed-string grep
- **FBB-B36** (NIT) — baseliner lists new failures by name only
- **FBB-B31** (gap) — gap: rule for a large parallel test set
- **FBB-B33** (gap) — gap: route a survivor whose fix is in specs
- **FBB-B37** (gap) — gap: check verbatim markup against CSS framework
- **DQD-B2** (MINOR) — docs example promises a dropped next step
- **IMP-G4** (gap) — gap: gate that each coding dispatch names a model

**to-fix.md items:** none.

**Confirm first:** IMP-B1 (medium); FBB-B32 (medium); FBB-B38 (medium); FBB-B36 (medium); FBB-B31 (medium); FBB-B33 (medium); FBB-B37 (low).

**Notes:** IMP-G1, the `/implement` restructure, landed as piece review (dev-workflows 4.32.0), which did not rewrite the dispatch phases, so this batch takes all eleven entries. 4.32.0 changed `implement.md`, `code-review.md` and `docs/commands/implement.md`: re-locate each entry by its quoted text. FBB-B37 is low confidence: confirm the case on the BOOK-2-01 feedback entry it cites first.

**Version bumps:** dev-workflows minor.

### B22 — dev-workflows: the /vuln and /upgrade references and docs pages

**Tier:** MINOR, plugin. **Entries:** 9, 0 MAJOR.

- **Theme:** The ecosystem references `/vuln` and `/upgrade` consult, install-time code, and the two docs pages.
- **Files:** `plugins/dev-workflows/references/fix-vuln/nvd-api.md`, `fix-vuln/build-systems.md`, `upgrade/ecosystems.md`, `install-time-code.md`; `docs/commands/vuln.md`, `docs/commands/upgrade.md`; `scripts/check-docs.sh` check 21 (VU-G1).
- **Why together:** Reference-only fixes that need no command change, plus the docs pages that describe the same install and revert behaviour. VU-G1 and VU-B17 are both `install-time-code.md`.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/gates.md` (check 21).

Entries:

- **VU-B6** (MINOR) — worked example contradicts its own range rule
- **VU-B7** (MINOR) — Maven Central query cannot list versions
- **VU-B14** (MINOR) — Cargo detected but has no section
- **VU-B8** (MINOR) — annotated-tag SHA pin writes tag object SHA
- **VU-B15** (MINOR) — NuGet last version is not latest stable
- **VU-B17** (NIT) — "says why" pointer to install-time code is wrong
- **VU-G1** (gap) — gap: install-time-code rows for uv, Composer, Poetry
- **VU-B5** (MINOR) — docs say revert leaves `node_modules` untouched
- **DQD-B8** (MINOR) — diagrams omit commit, push and pull request

**to-fix.md items:** none.

**Confirm first:** none; every entry is high confidence.

**Notes:** Run after B06 so the docs pages describe the fixed commands.

**Version bumps:** dev-workflows minor (VU-G1 changes what installs run).

### B23 — product-workflows: /create-prd and /update-prd

**Tier:** MINOR, plugin. **Entries:** 9, 0 MAJOR.

- **Theme:** `/create-prd`'s BRD-route frontmatter, address forms and `--from-prd` seed, `/update-prd`'s unused question, and the pages describing them.
- **Files:** `plugins/product-workflows/commands/create-prd.md`, `update-prd.md`; `agents/prd-reviewer.md`; `docs/commands/create-prd.md`, `docs/brd-workflow.md` (DQP-B3).
- **Why together:** PRD2-B1 to PRD2-B5 are the `/create-prd` paragraphs the PRD2 pass read. DQP-B3 and DQP-B4 are the docs statements of the same address and seed rules, and FBB-B7 is a rule for the same interview phase.
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/brd-route.md`.

Entries:

- **PRD2-B1** (MINOR) — never told to write `brd_key` and siblings
- **PRD2-B2** (MINOR) — docs offer an `@<path>` address it rejects
- **PRD2-B3** (MINOR) — `--from-prd` seed read but never used on BRD route
- **PRD2-B4** (NIT) — `prd-reviewer` still says `<BRD-KEY>`
- **PRD2-B5** (NIT) — small text defects in command and page
- **PRD-B4** (MINOR) — Refresh-or-Re-do answer is read by nothing
- **FBB-B7** (gap) — gap: decisions taken outside the register
- **DQP-B3** (MINOR) — parameter table lists `@<idea.md>` on BRD route
- **DQP-B4** (MINOR) — page says BRD route seeds from `prd-seed.md`

**to-fix.md items:** none.

**Confirm first:** PRD2-B2 (medium); PRD2-B3 (medium); FBB-B7 (medium).

**Notes:** Run after B07 (D16's sentence) and B18 (FBB-B4's template) so the three do not collide in `create-prd.md`.

**Version bumps:** product-workflows minor.

### B24 — product-workflows: /epics and epic-writer

**Tier:** MINOR, plugin. **Entries:** 9, 0 MAJOR.

- **Theme:** `/epics`' size, keep-whole and review steps, its briefs, and `epic-writer`.
- **Files:** `plugins/product-workflows/commands/epics.md`, `plugins/product-workflows/agents/epic-writer.md`, `docs/commands/epics.md`.
- **Why together:** D8 and FBB-B17 are the size count and the keep-whole question around the review; D11 is `epic-writer`'s same `kept_whole` rule. The three FBA gaps are new steps in Phases 2.5 and 5 of the same command.
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/docs-workflows.md` (it loads for `epics.md`), `.claude/rules/workflows-core-triage.md`.

Entries:

- **FBB-B17** (MINOR) — keep-whole asked after the writer split
- **PRD-B3** (MINOR) — reads an undefined `refinement_candidate` flag
- **PRD-B6** (MINOR) — Instructions agent edits files after handoff
- **PRD-B9** (NIT) — adaptive array can show a setting twice
- **FBB-B20** (MINOR) — `body_facts` false on the falling-back handoff
- **FBB-B22** (NIT) — house style not passed to the style checker
- **FBA-G2** (gap) — gap: pass file paths, not pasted outputs
- **FBA-G3** (gap) — gap: check landing order against contract rows
- **FBA-G4** (gap) — gap: step for calls missing from Contracts

**to-fix.md items:** D8, D11.

**Confirm first:** FBB-B17 (medium); PRD-B6 (low); PRD-B9 (medium); FBB-B20 (medium); FBB-B22 (low).

**Notes:** Run after B16, which adds `/epics`' apply-open-findings offer (FBB-B21) to the same review phase.

**Version bumps:** product-workflows minor.

### B25 — product-workflows: /brd-interview

**Tier:** MINOR, plugin. **Entries:** 9, 0 MAJOR.

- **Theme:** `/brd-interview`'s pickers, settled-finding rules, round records and final report, and the docs pages that name it.
- **Files:** `plugins/product-workflows/commands/brd-interview.md`, `references/decision-register-format.md`, `references/brd-format.md`; `docs/commands/brd-interview.md`, `docs/commands/brd-package.md`, `docs/commands/brd-intake.md`.
- **Why together:** All entries are `/brd-interview`'s text or the docs statements about it; BRD3-B8 and BRD3-B9 are the same Phase 5 outcome rules.
- **Read first:** `.claude/rules/brd-route.md`, `.claude/rules/product-workflows.md`.

Entries:

- **BRD2-B1** (MINOR) — `[V]` picker described two contradictory ways
- **BRD2-B5** (MINOR) — `conditional_on` form collides with key grammar
- **BRD3-B8** (MINOR) — `unprovable` outcome counts as settled
- **BRD3-B9** (MINOR) — Phase 5 answers a `[G]` from superseded finding
- **BRD3-B21** (NIT) — report misexplains non-zero `unallocated`
- **FBB-B43** (MINOR) — follow-ups batchable; round-record layout undefined
- **FBB-B44** (gap) — gap: close `unsourced` defects a finding settles
- **BRD2-B7** (MINOR) — docs examples invoke the root key
- **BRD2-B10** (NIT) — docs say it "gates on" the slice ledger

**to-fix.md items:** none.

**Confirm first:** BRD2-B5 (medium); BRD3-B8 (medium); BRD3-B9 (medium); FBB-B43 (medium); FBB-B44 (medium); BRD2-B7 (medium); BRD2-B10 (medium).

**Notes:** If the BRD-G1 decision is answered as recommended, its widened re-disposition trigger lands here.

**Version bumps:** product-workflows minor.

### B26 — product-workflows: /prd-ground and its grounders

**Tier:** MINOR, plugin. **Entries:** 7, 0 MAJOR.

- **Theme:** `/prd-ground`'s phases, its repository matching, and the three grounding agents' contract with it.
- **Files:** `plugins/product-workflows/commands/prd-ground.md`, `commands/brd-split.md` (D7's caller); `agents/code-grounder.md`, `agents/design-grounder.md`, `agents/grounding-verifier.md`; `CHANGELOG.md` (D9's upgrade note).
- **Why together:** D7, D9 and D10 are `/prd-ground`'s repository resolution and pinning; the review entries are its Phase 0, 5, 9, 10 and 11 text and the grounders' `horizon` and evidence rules.
- **Read first:** `.claude/rules/brd-route.md`, `.claude/rules/prd-ground-verification.md`, `.claude/rules/docs-grounding.md`.

Entries:

- **BRD-B2** (MINOR) — "ground another prerequisite" names no command
- **BRD-B3** (NIT) — Phase 9 names `brd-link.md` unconditionally
- **BRD3-B6** (MINOR) — Phase 5 ignores `STALE_INDEX`
- **BRD3-B20** (NIT) — grounders told to assign `horizon` they cannot
- **FBA-B6** (NIT) — Phase 0 picks no preflight order
- **FBA-B7** (MINOR) — repo-local README not named as documentation
- **FBB-B41** (MINOR) — tail after stop, prose evidence, answer reuse, assets

**to-fix.md items:** D7, D9, D10.

**Confirm first:** BRD-B2 (medium); BRD-B3 (medium); BRD3-B20 (medium); FBA-B6 (medium); FBB-B41 (medium).

**Notes:** D9 is low confidence (the slug rule was not re-traced): trace it before designing the stable identity.

**Version bumps:** product-workflows minor; D9 needs a dated upgrade note in `CHANGELOG.md`.

### B27 — product-workflows: /brd-split, /brd-intake and coverage-ledger-format

**Tier:** MINOR, plugin. **Entries:** 9, 0 MAJOR.

- **Theme:** Slicing and intake, the coverage ledger format, and `slices.md`.
- **Files:** `plugins/product-workflows/commands/brd-split.md`, `brd-intake.md`; `references/coverage-ledger-format.md`; `docs/commands/brd-split.md`.
- **Why together:** BRD2-B2 to BRD2-B4 and BRD2-B9 are one docs page describing `/brd-split`; BRD3-B22, BRD3-B23 and FBA-G9 are the ledger format the same command writes.
- **Read first:** `.claude/rules/brd-route.md`, `.claude/rules/product-workflows.md`.

Entries:

- **BRD2-B2** (MINOR) — docs give bulk offer the wrong condition
- **BRD2-B3** (MINOR) — docs drop the third no-op exception
- **BRD2-B4** (MINOR) — docs misstate a slice block's rationale
- **BRD2-B9** (NIT) — docs "What it produces" omits `covered-here`
- **FBA-B5** (NIT) — named-slice key prompt lacks asking rule
- **FBA-B4** (NIT) — byte-for-byte copy keeps source mode bits
- **BRD3-B22** (NIT) — §6 models a state §5 forbids
- **BRD3-B23** (NIT) — §6.2 overstates which file `/brd-split` gates
- **FBA-G9** (gap) — gap: define the `slices.md` layout

**to-fix.md items:** none.

**Confirm first:** FBA-B5 (medium); BRD3-B22 (medium).

**Notes:** FBA-G8 (the uniform-answer offer) is in the decisions list; if it is accepted, it lands here.

**Version bumps:** product-workflows minor.

### B28 — Class fix: the key grammar restated outside addressing §1

**Tier:** MINOR, class fix (hooks and docs). **Entries:** 4, 0 MAJOR.

- **Theme:** **Class: a copy of the key grammar that is narrower than, or contradicts, `workflows-core:addressing` §1** — the `/implement` and `/document` preload hooks' regex (SCR-B3, with IMP-B5 and DEV-B6 merged into it), and docs that teach a key shape or depth the grammar does not fix.
- **Files:** `plugins/dev-workflows/hooks/preload-context.sh`, `plugins/docs-workflows/hooks/preload-context.sh`; docs pages naming example keys (`plugins/dev-workflows/docs/getting-started.md` and command pages, `plugins/product-workflows/docs/workflow.md`, `brd-workflow.md`, command pages); `scripts/check-docs.sh` (a new check).
- **Why together:** One grammar, several restatements. Fix the hooks to `addressing` §1's grammar (`^[A-Z][A-Z0-9_]*(-\d+)+$`), or have them defer to the command, and add a check that every hook regex for a key matches that grammar. Fix the docs examples in the same pass so pages and hooks agree.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/docs-workflows.md`, `.claude/rules/product-workflows.md`, `.claude/rules/gates.md`.

Entries:

- **SCR-B3** (MINOR) — preload hooks' key regex narrower than §1
- **DQD-B1** (MINOR) — example key `EPIC-98760` is no Epic shape
- **DQP-B8** (MINOR) — example keys carry folder-kind tokens
- **DQP-B9** (NIT) — "two segments or three" contradicts the grammar

**to-fix.md items:** none.

**Confirm first:** DQP-B8 (medium).

**Notes:** Do not touch `pre-lint`'s Jira-key autolink detector: `CLAUDE.md` forbids widening it, and it is not a key validator.

**Version bumps:** dev-workflows patch, docs-workflows patch, product-workflows patch.

### B29 — Gates, instruction tiers and the tracking records

**Tier:** MINOR, repository (no plugin). **Entries:** 4, 0 MAJOR.

- **Theme:** Text in `CLAUDE.md`, `.claude/rules/`, `scripts/` and `docs/superpowers/` that misstates what a gate does or what is still tracked.
- **Files:** `CLAUDE.md`, `.claude/rules/gates.md`, `.claude/rules/gates-id-grammar.md`, `scripts/spec-id-baseline.txt`, `scripts/check-docs.sh` (read only, unless SCR-B2 is fixed by widening), `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md`, `docs/superpowers/verification/2026-08-22-docs-restructure-open-items.md`, `docs/superpowers/to-fix.md`.
- **Why together:** None of these ships to users; all are maintainer records. The bugs file's *Stale text in to-fix.md itself* list (the *Design-level* intro, D16's quotation, E4's range, the *Coverage* line) is fixed here too.
- **Read first:** `.claude/rules/gates.md`, `.claude/rules/gates-id-grammar.md`; `workflows-core:instruction-file-maintenance` binds the `CLAUDE.md` and rules edits.

Entries:

- **SCR-B2** (MINOR) — CLAUDE.md overstates check 13's scope
- **SCR-B4** (MINOR) — spec-ID census "tripwire" run by no gate
- **TRK-B1** (NIT) — 2026-10-15 record says C1–C8 still tracked
- **TRK-B2** (MINOR) — untracked edition-port obligation from 2026-08-22

**to-fix.md items:** none.

**Confirm first:** SCR-B4 (medium); TRK-B2 (medium).

**Notes:** The decisions list's "record it in to-fix.md" answers (CORE-G2, SCR-G2, BRD-G1, DOC-D-G5, IMP-G3, IMP-G5) are written into `to-fix.md` in this batch's commit, once each decision is taken.

**Version bumps:** none (no plugin files).

### B30 — Class fix: maintainer vocabulary on user pages

**Tier:** Documentation only (class fix). **Entries:** 10, 0 MAJOR.

- **Theme:** **Class: maintainer vocabulary on user pages** — `§` section citations and bare `workflows-core:<name>` citations a user cannot open, design-decision ids (D4 … D25), grep recipes over `plugins/`, "this page used to say" change history, and internal terms such as "the tracker".
- **Files:** every plugin's `docs/` tree and README, and the root `README.md`.
- **Why together:** One rule broken on every plugin's pages. Fix it once with one rewrite rule (link the docs page that covers the reference, or say it in plain words; drop decision ids and history; replace grep recipes with links), then add a `scripts/check-docs.sh` check that fails a `§` or a `D<n>` id on a page under `docs/`, with a per-line marker for the rare justified case.
- **Read first:** `.claude/rules/gates.md` (for the new check), plus each plugin's rules file.

Entries:

- **DQS-B7** (MINOR) — design-decision ids leak into user pages
- **DQS-B8** (MINOR) — hundreds of unlinked `§` and reference citations
- **DQC-B4** (MINOR) — grep recipes given to users as navigation
- **DQC-B5** (MINOR) — core pages cite references users never open
- **DQC-B6** (MINOR) — stale, changelog-style statements on core pages
- **DQD-B7** (MINOR) — dev pages full of maintainer vocabulary
- **DQP-B7** (MINOR) — product pages cite internal rulings and sections
- **DQP-B10** (NIT) — search-and-replace residue and history on product pages
- **DQW-B10** (MINOR) — docs-workflows pages leak maintainer vocabulary
- **DQW-B11** (MINOR) — "the tracker" and "the docs automation" unexplained

**to-fix.md items:** none.

**Confirm first:** DQS-B8 (medium); DQW-B11 (medium).

**Notes:** DQS-B8's counts are exact, but how many to rewrite is a judgement: count them per plugin before and after, with the command beside the number. Vendor neutrality (check 13) still applies when replacing "the tracker".

**Version bumps:** a patch bump for every plugin whose `docs/` changes.

### B31 — Class fixes: navigation links and links that leave the plugin

**Tier:** Documentation only (two class fixes). **Entries:** 8, 0 MAJOR.

- **Theme:** **Class A: command pages that do not link back, and overview pages that do not link commands** (DQS-B2, DQS-B3 and the per-plugin entries). **Class B: relative links that leave the plugin directory** and break in the installed cache (DQS-B5).
- **Files:** every plugin's `docs/workflow.md`, `roles-and-phases.md`, `getting-started.md`, `docs/commands/*.md` and README; the root `README.md` (DQS-B1's row); `scripts/check-docs.sh` (two new checks).
- **Why together:** Both classes are link structure on the same pages and want the same edit pass. Add two checks: every command page links its plugin's workflow page, and no relative link under `plugins/<name>/` resolves outside `plugins/<name>/`.
- **Read first:** `.claude/rules/gates.md`, plus each plugin's rules file.

Entries:

- **DQS-B2** (MINOR) — overview pages link no command page
- **DQS-B3** (MINOR) — 18 command pages never link back
- **DQS-B4** (MINOR) — next and previous commands named, not linked
- **DQP-B15** (MINOR) — nine product command pages link no workflow
- **DQW-B13** (MINOR) — three docs-workflows pages never link back
- **DQS-B1** (MINOR) — guideline-reviewers README links neither diagram nor docs
- **DQS-B10** (NIT) — core README does not link the family map
- **DQS-B5** (MINOR) — 18 relative links leave the plugin directory

**to-fix.md items:** none.

**Confirm first:** DQS-B5 (medium).

**Notes:** DQS-B5 is medium confidence on how users browse the cache; the fix (absolute repository URLs) is safe either way. Check 10's identity quarantine still applies to any URL added.

**Version bumps:** a patch bump for every plugin whose `docs/` or README changes.

### B32 — Family entry points and workflows-core docs

**Tier:** Documentation only. **Entries:** 12, 0 MAJOR.

- **Theme:** The root README and the workflows-core user pages: cost snapshot, status line, run flags, environment counts, family map and naming.
- **Files:** `README.md`; `plugins/workflows-core/README.md`, `docs/README.md`, `docs/getting-started.md`, `docs/workflow.md`, `docs/family-map.md`, `docs/roles-and-phases.md`, `docs/commands/frames.md`, `docs/commands/statusline.md`, `docs/reference/*.md`; `plugins/dev-workflows/docs/getting-started.md` (DQC-B10).
- **Why together:** All are the family's first pages; most are one-line corrections in files no other batch opens.
- **Read first:** `.claude/rules/workflows-core.md`, `.claude/rules/security-workflows.md` (it loads for `family-map.md`).

Entries:

- **DQC-B2** (MINOR) — cost snapshot points at a silent page
- **DQC-B3** (MINOR) — three getting-started pages skip the status line
- **DQC-B7** (MINOR) — family map omits two forward steps
- **DQC-B8** (MINOR) — run flags never named for users
- **DQC-B9** (NIT) — "three core variables" against five exported
- **DQC-B10** (NIT) — dev getting-started miscounts variables read
- **DQC-B11** (NIT) — "three edges" where the diagram draws five
- **DQC-B12** (NIT) — `/frames` diagram says "kind-gated"
- **DQC-B13** (NIT) — family called "the `dev-workflows` plugin family"
- **DQC-B14** (NIT) — directory structure misses three layouts
- **CORE-B15** (NIT) — feedback ladder's second rung misdescribed
- **CORE-B16** (NIT) — README table omits Grounding sources page

**to-fix.md items:** none.

**Confirm first:** DQC-B7 (medium).

**Notes:** DQC-B7 is medium confidence: check each forward step against the offering command's next-step phase before drawing it.

**Version bumps:** workflows-core patch, dev-workflows patch.

### B33 — dev-, security- and docs-workflows pages and page-set parity

**Tier:** Documentation only. **Entries:** 7, 0 MAJOR.

- **Theme:** The remaining dev-workflows docs defects, the first-`/implement` walkthrough, and the page sets docs- and security-workflows lack.
- **Files:** `plugins/dev-workflows/docs/workflow.md`, `reference/environment.md`, `reference/session-cost.md`, `commands/ready.md`, `getting-started.md`; new pages under `plugins/docs-workflows/docs/` and `plugins/security-workflows/docs/reference/`; `docs/commands/*.md` diagrams (DQS-B9); `.claude/rules/docs-workflows.md` and `.claude/rules/security-workflows.md` page counts.
- **Why together:** DQS-B6 and its merged DQD-G2 add the missing pages; DQS-B9 adds the missing diagrams; the DQD entries are the dev pages no other batch opens.
- **Read first:** `.claude/rules/dev-workflows.md`, `.claude/rules/docs-workflows.md`, `.claude/rules/security-workflows.md`, `.claude/rules/gates-mermaid.md`.

Entries:

- **DQD-B3** (MINOR) — diagram skips PRD-level `/conformance` and scan
- **DQD-B4** (MINOR) — environment layout misfiles follow-ups
- **DQD-B6** (MINOR) — session-cost example names product commands
- **DQD-B11** (NIT) — missing space joins two paragraphs
- **DQD-G1** (gap) — gap: a first `/implement` walkthrough
- **DQS-B6** (MINOR) — page-set holes in docs- and security-workflows
- **DQS-B9** (NIT) — command pages missing sibling diagrams

**to-fix.md items:** none.

**Confirm first:** DQD-B3 (medium); DQS-B9 (medium).

**Notes:** New pages change the page counts `.claude/rules/docs-workflows.md` and `.claude/rules/security-workflows.md` state; re-derive and update them (no gate checks those numbers).

**Version bumps:** dev-workflows patch, docs-workflows patch, security-workflows patch.

### B34 — product-workflows docs: getting started, workflow pages, glossary

**Tier:** Documentation only. **Entries:** 15, 0 MAJOR.

- **Theme:** The product-workflows user pages: getting started, the two workflow pages, the reference pages, and the missing walkthrough, glossary and next-step sections.
- **Files:** `plugins/product-workflows/README.md`, `docs/getting-started.md`, `docs/workflow.md`, `docs/brd-workflow.md`, `docs/roles-and-phases.md`, `docs/commands/*.md`, `docs/reference/*.md` (new `glossary.md`).
- **Why together:** All land in product-workflows' `docs/`. The gaps are additions to the same pages (DQP-G4 adds a section to each command page, so it rides with the page-level fixes).
- **Read first:** `.claude/rules/product-workflows.md`, `.claude/rules/brd-route.md`, `.claude/rules/gates-mermaid.md`.

Entries:

- **DQP-B1** (MINOR) — promises a handoff an unanswered run skips
- **DQP-B2** (MINOR) — never says to merge the pull request
- **DQP-B5** (MINOR) — diagram routes `/implement` straight to docs
- **DQP-B6** (MINOR) — diagrams omit offers; BRD page misdescribes one
- **DQP-B11** (NIT) — `/idea` page names a personal vault path
- **DQP-B12** (NIT) — role and artifact tables disagree with roles page
- **DQP-B13** (NIT) — optional variables "degrade" claim is wrong
- **DQP-B14** (NIT) — README omits three reference pages
- **DQP-B16** (NIT) — three reference paragraphs too long
- **PRD-B5** (MINOR) — false exclusivity claim about `docs-grounder`
- **PRD-B7** (NIT) — hooks page miscounts the other commands
- **DQP-G1** (gap) — gap: a first BRD-route walkthrough
- **DQP-G3** (gap) — gap: a glossary of route vocabulary
- **DQP-G4** (gap) — gap: "What it offers next" on command pages
- **DQP-G5** (gap) — gap: "Where to run it" and untrusted input

**to-fix.md items:** none.

**Confirm first:** DQP-B16 (medium).

**Notes:** Run after B07, B08, B10 and B23, so the pages describe the fixed commands. DQP-G4's section on each page must be read from the command's own next-step phase, not from the retired README.

**Version bumps:** product-workflows patch.

## Merged entries

Each of these is the same defect or gap as another entry and is fixed by that entry's edit. Mark both headings fixed in the same commit.

- **DQD-B5** — merge into DQC-B10: the same "five environment variables" claim on `dev-workflows/docs/getting-started.md`; fix both by DQC-B10's edit (B32).
- **DQD-G2** — merge into DQS-B6: security-workflows' missing feedback, follow-up and resume-pointer page is one of DQS-B6's parity holes (B33).
- **DQP-G2** — merge into DQP-B5: D22's docs edge is DQP-B5's diagram fix; the second-diagram half is superseded (B34).

## Design tracks

Each needs its own brainstorm, spec and plan before any code. They are not batches; none should start before the batches that change the same files have landed.

- **GIT-G1** — Lean context part 3: script `specs-repo-git`'s procedures. Script `branch-merged`, `branch-key`, `push-scope` and the §2.1 classifier first, with a selftest, then decide `specs-preflight` and `commit-artifacts`. B01's fixes to GIT-B1 and GIT-B2 become its first test cases. Merged gaps: CORE-G1, SCR-G1.
- **IMP-G1** — The post-D `/implement` restructure. One `code-writer` per approved plan, Epics sized by coupling with `size_limit` as a warning, the PRD-level `/specify` question, and the A/B on the e2e copies. Blocks E4's port of `40e6b9ea`. Takes IMP-G2's cost bar and PRD-G2's calibration as inputs (decisions list). Merged gap: PRD-G1. *Resolved by dev-workflows 4.32.0 (piece review): part (a) was built, measured and shelved; its review scopes shipped; the coupling cut and a mandatory `/specify` were dropped; E4 now ports `40e6b9ea` with 4.32.0 (`docs/superpowers/verification/2026-10-25-implement-piece-review.md`).*
- **DEV-G1** — `/conformance` Plan 2, part 1: the *Delivery verified* stage. The optional `workflow-states` rung, `/ready` reading the PRD-level `_conformance.md`, the `readiness-reviewer` rubric line, and every page that draws the ladder.
- **DEV-G2** — `/conformance` Plan 2, part 2: documentation readers take a recorded decision. `doc-planner`'s requirement field, the `source-truth` §7 mapping, reads in `/document` Phase 5.8 and `/release-notes`. Run after B03, B12 and B13, which change the same phases. Merged gap: DOC-D-G3.
- **DOC-D-G1** — docs-workflows Spec 2: `/docs-write`, `/docs-capture`, `/docs-verify`. Start with `/docs-write --next`, which also regenerates the nav and replaces B14's interim DOC-C-B1 procedure. Revive the design from history as the entry says. Merged gap: DOC-C-G1.
- **DOC-D-G2** — docs-workflows Spec 3: `/docs-drift`. After DOC-D-G1; the design says it is meaningless before pages exist.
- **SEC-G1** — security-workflows sub-project E: the architecture feedback loop. `architecture-grounder` and `promotion-scout` read the registers and raise `known-weakness` challenges.
- **SEC-G2** — security-workflows sub-projects B, C and D. ARD threat model, design threat review, security conformance; B first, per the roadmap's dependency column.

## Decisions

Each needs an answer more than work. Where the answer is "record it", the record goes into `to-fix.md` in B29's commit; where it is work, the batch named takes it.

| ID | Question | Recommended answer |
|---|---|---|
| **SEC-G3** | Write the sub-project A verification record now, or after another live run? | Write it from the Task 12 session notes now, and run route 7 and the clean install where they were not run. Pair the live part with B04's L2 check. |
| **VU-G2** | When to run the `/vuln` baseline-symmetry change live? | After B06 and B22: one `/vuln` and one `/upgrade` against the bookstore fixture with a breaking bump, a stale local `main` and an annotated-tag pin. It verifies VU-B1, VU-B2, VU-B4 and VU-B8 at once. |
| **VU-G3** | Give `/upgrade` an `ADDRESS:` token, or drop the prose that assumes one? | Drop the dead prose (it is VU-B10's fix in B06). Add the token only when a user asks to tie an upgrade to a unit. |
| **DOC-D-G4** | Run the increment-2 docs commands end to end? | Yes, after B14: one bookstore pass through the route's steps 1–4 and 7, recording what fails in a verification record. |
| **BRD-G2** | Re-run the deferred blind-verification live checks? | Yes, cheaply, in the next live `/prd-ground` run after B26: one direct derive dispatch with an answer field and one planted control-forced contradict. |
| **BRD-G3** | Verify the BRD-figures rows left open on 2026-09-22? | Yes for the `/brd-intake` re-run path: one fixture re-intake and one *Stop and convert them first* run, after B27. |
| **SCR-G2** | Split `untrusted-content` by part, or drop the idea? | Drop it: D measured that splitting has not clearly paid, and check 20 pins the block. Record the drop in `to-fix.md`'s Accepted section (B29). |
| **IMP-G3** | Pick up Fable escalation (sub-project F part 2)? | No. Its deferral ground, no measured Opus shortfall, still holds. Record it as deferred in `to-fix.md` and revisit with a measured case. |
| **IMP-G2** | Accept the missed implement-coding-subagents cost target, or keep it as a goal? | ~~Fold it into IMP-G1's A/B as its baseline~~ — IMP-G1 shipped as piece review without a route-3 measurement, and its BOOK-3-01 runs ($57.17 on 4.31.0) are a different Epic, so they do not close the bar: measure today's `/implement` on the route-3 copy once and record it against the bar, or record a ruling that accepts the higher cost. |
| **PRD-G2** | Calibrate the Epic size limit live, or drop the calibration? | ~~Fold it into IMP-G1~~ — IMP-G1 dropped the coupling cut (the user's decision, 2026-10-25), so `size_limit` stays a cut: calibrate it live, or record a ruling that drops the calibration. |
| **IMP-G5** | Build resume-from-run-state for a crashed `/implement`? | Not now. IMP-G1 shipped as piece review, which added the run-state keys `pieces` and `reviews` and changed nothing else of the state model. Record the deferral in `to-fix.md` so it stays visible. |
| **CORE-G2** | Take up `implementation-format` §4's widened key boundary? | Not yet. Record it in `to-fix.md` beside C2 and C9 in B03's commit; if taken up, give it a short design that first measures the boundary's readers. |
| **BRD-G1** | Carry a `needs-a-human` sweep item forward to `/brd-interview`, or let the report line suffice? | Widen `/brd-interview`'s re-disposition trigger to entries the latest reconciliation record flagged `needs-a-human` (lands in B25), because an item carried only in a report is lost when no interview round is planned. Move follow-up E-8 into `to-fix.md` either way. |
| **DOC-D-G5** | What is `/release-notes`' missing starting-state fact, and is it a rule? | Recover the blind verdict first; until then file it in `to-fix.md` (B29). If the verdict holds, add a "state before the change" requirement for Changed and Fixed entries to `release-note-types`. |
| **FBA-G8** | Let `/brd-split`'s uniform-answer offer fire with two or more slices? | Yes, narrowly: a `full`-mode row that fires only where Phase 1.5 placed every offered row on a keyed child Phase 2, as one confirmation listing each target. It lands in B27, rewriting the refusing sentence rather than appending to it. |
| **FBB-B16** | Ship a `spec-tool.py` for mechanical spec edits and checks? | Not yet. B08 adds FBA-G6's renumbering note; build the tool only if live runs keep needing it, and then as one script with the deterministic checks FBB-B16 names. |
| **FBB-B35** | Allow a non-running type-check of test sources before the Opus review? | Yes, stated as "not a test run", because a review of tests that do not compile wastes the Opus pass; if `.claude/rules/dev-workflows-tests.md`'s test-writing rules forbid it, record why there instead. Decide it with B21: IMP-G1 shipped as piece review without redrawing these phases. |

**Live verification still owed (to-fix.md L2).** Confirm in the next live run that writes `resume.md`: the `(waiting since …)` marker beside a carried command item, *Last completed* with its UTC offset, the register slug beside each Security Engineer offer, and the next run's §1 carry reading them back. It is attached to B04, whose live `/scan` run writes all three.

## Out of scope: edition ports

These are ports to the internal Claude and Copilot editions, done on another machine. They are not batched here; keep them in `to-fix.md`.

- E1 — Port `check-docs.sh`'s shared body to the internal Claude and Copilot editions. B19 (D12), B20, B21, B22, B28, B30 and B31 add or change checks in that body, so each widens E1's port.
- E2 — Port the 2026-10-15 review's plugin fixes to the editions.
- E3 — Port check 9's singular count to the editions.
- E4 — Port every merge since `7c13ce05` to both editions, after deciding on the load-by-part machinery. B29 fixes E4's stale source range in `to-fix.md`, but not the port.

## Coverage check

A script (kept outside the repository) read the ID list built from both review files, checked it against the `### <ID> —` headings of each, and counted every bold `**<ID>**` in this file. Each of the 337 IDs must appear in bold exactly once, no bold ID may be unknown, and each *merge into* target must be a batch entry. Its output on this file:

```text
known IDs: 337 (273 B, 64 G); headings: 273 bugs, 64 gaps
bold IDs in plan: 337 distinct, 337 total
placement: {'batch': 309, 'Merged entries': 3, 'Design tracks': 8, 'Decisions': 17}
missing: none
duplicated: none
unknown: none
RESULT: PASS
```

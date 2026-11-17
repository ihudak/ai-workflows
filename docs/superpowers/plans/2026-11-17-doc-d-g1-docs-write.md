# DOC-D-G1 sub-project 1 — `/docs-workflows:docs-write` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/docs-workflows:docs-write <unit-id>|--next|--batch <n>` turns a documentation backlog unit into a reviewed, visibly-unverified page on a branch of the docs repository, with its navigation and its unit's move `missing → drafted` in the same commit, and lays down the contracts `/docs-verify` and `/docs-capture` will share.

**Architecture:**
- One new command with its own phases (D4, D5), dispatching the agents `/document` already dispatches. Every difference a backlog run makes to `doc-writer` and `doc-reviewer` lives in one new reference, `references/docs-iteration/unit-brief.md`; each agent gains one pointer sentence and nothing else of behaviour.
- One new stdlib script, `scripts/backlog-lines.py`, is the design's single line reader (D13): the shape test, the duplicate-id check, the unmerged-branch read (D7) and the two-key targeted edit (D8). No other step reads a backlog line by line.
- The docs-repository discipline every backlog run shares lives in one new section of `finish-and-handoff.md` (D10); navigation regeneration is a new entry point of `scaffold-tree.md` §4 (D9); `/docs-write`'s gate registry is a new section of `gate-ledger.md` (D4).
- `workflows-core` takes rows and truth edits only: the cost and feedback documentation rungs, the namespace manifest, `branch-naming`'s fallback row and slug, `doc-structure-conventions` §1's carve-out, the lists that name each caller, and the three approved GIT-G1 count edits.

**Tech Stack:** markdown prose that agents execute; one Python 3 stdlib script with `--selftest`; generated reference parts (`python3 scripts/reference-parts.py generate`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-17-doc-d-g1-docs-iteration-design.md`, revision 3, approved 2026-11-17. Cited as *D1*…*D17*; its abbreviations (BF, EC, CM, FG, ST, FH, RR, DOC, AUD, ROUTE, SRG, PH, P3) are used unchanged. A decision the design states is not repeated here. Its reviews: `.superpowers/design-review-1.md`, `design-review-2.md`.

**The maintainer's answers** (the design's Status line, 2026-11-17):
1. Three sub-projects: `/docs-write` (this plan), then `/docs-verify`, then `/docs-capture` with `captured`; the `stale` edges go to the drift track.
2. A visible page-level unverified marker on every drafted page until `/docs-verify` removes it.
3. GIT-G1 edits 1–3 approved by name, truth-only (E1–E3 below).
4. `release` units refused.
5. No specs artifact read but an `ard.md`, on the default branch.
6. One consented push offer at the end of a run.

**Open question for the maintainer** (asked with this plan; Task 2 depends on it):
- **Q1 — one CI step.** `backlog-lines.py --selftest` needs a step in `.github/workflows/validate-catalog.yml`, a GIT-G1 file. **Recommended:** approve one step, written as SEC-G1's weakness-classes step was (maintainer ruling 2026-11-13). Alternative: no CI step; the selftest runs in this branch's gate chain only, and `to-fix.md` logs BACKLOG-LINES-CI for the GIT-G1 owner.

**Execution:** subagent-driven. Opus implements every task. **[security-sensitive]** tasks are reviewed by Fable; **[mechanical]** ones by Opus. Fable reviews the whole branch at the end.

**Base:** worktree `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1`, branch `feat/doc-d-g1-docs-iteration`, `main` at `6d6518b7d` plus the design commits. Line numbers below are finding aids at that base: **locate every site by its quoted phrase.**

**The GIT-G1 edits — every one, with its approval.** This track has no standing truth-edit permission.

| # | Edit | Task | Approval |
|---|---|---|---|
| E1 | `.claude/rules/workflows-core-git.md:26` — the `specs-repo-git` consumer counts | 5 | Answer 3, by name (truth) |
| E2 | `.claude/rules/workflows-core-git.md:32` — the implementation-repository counts | 5 | Answer 3, by name (truth) |
| E3 | `plugins/workflows-core/references/specs-repo-git.md:310` — the bookkeeping-only class gains `/docs-write` | 5 | Answer 3, by name (truth) |
| C1 | `.github/workflows/validate-catalog.yml` — one selftest step | 2 | **Q1, pending** |

E1 and E2 together change `workflows-core-git.md` by −7 characters (19,993 → 19,986).

---

## Global Constraints

### What is not ours

- **Never edited:** `plugins/workflows-core/references/phase-handoff.md` and its `reference-parts/phase-handoff/`, `plugins/workflows-core/scripts/specs-git.py` and its two modules, the `specs-git` skill and `run-key-set.md`, `.claude/rules/workflows-core-handoff.md`, `.github/` save C1 under Q1. `specs-repo-git.md` takes E3 alone; `workflows-core-git.md` takes E1 and E2 alone; `workflows-core-read-only.md` takes R26's two truth edits alone.
- **Left as they stand, by the design's choice:** SRG:132, SRG:314, SRG:757-762, PH:403, PH:439, PH:628's named readers.
- **Any other GIT-G1 sentence a step finds this change makes false is reported to the controller as a question for the maintainer. It is never edited.**
- **`/docs-write`'s own GIT-G1-shaped sections** — *Ending early*, the specs preflight, the terminal `commit-artifacts` — are new text written in `/docs-audit`'s form (AUD:18, Phase 0 step 3, Phase 9). They add no GIT-G1 behaviour; the pull request names them for the GIT-G1 owner.
- **Untouched (D15):** `commands/document.md`, `agents/doc-location-finder.md`'s contract, `docs-style-checker`, `doc-fixer`'s and `code-scanner`'s contracts, `doc-planner`, `/docs-init`, `/docs-brand`, `/docs-serve`, `/docs-profile`, `/release-notes`, the UserPromptSubmit hook. **"Unchanged" means no contract change** (R17): a caller list in a description or opening line gains `/docs-write` in Task 7, as D17's known site `doc-fixer.md:3` already shows.

### What sub-projects 2 and 3 add (named, not built here)

- **Sub-project 2, `/docs-verify`:** `drafted → verified`; the `answers` input `unit-brief.md` reserves for `doc-writer` (D11); EC §4–§5's stamp key; `--prepare`; `verified`'s removal of the page-level marker; its gate registry section in `gate-ledger.md`.
- **Sub-project 3, `/docs-capture`:** `captured` in BF, CM and FG's lifecycle copies and in `/docs-audit` and `docs-audit-reviewer`; `/docs-write`'s `captured → drafted` (prose from the walkthrough, images placed under D9's image rules).
- Each repeats this plan's sweep for its command and its agents, and re-derives E1–E3 (the design's +1 and +11).

### Repository rules

- **Prose is executed.** Every sentence an agent reads is true when it runs. A forward reference a later task makes true is named in that task's *Interfaces* and closed in Task 9.
- **`grep` here is ugrep. Every count uses `command grep`.** A sweep enumerates by subject, then counts each literal string wrap-insensitively, before and after, over refinement 4's scope: `plugins/` (every `CHANGELOG.md` included, where a hit is history and stays), `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`.
- **One noun:** *a backlog run* (D1) — a run of any of the three commands.
- **Sizes** by `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" <file>`. Plan-time: `CLAUDE.md` 35,978 (warn 36,000); `.claude/rules/docs-workflows.md` 19,998; `workflows-core-git.md` 19,993; `workflows-core.md` 19,150; `plugin-updates-coupling.md` 18,175; `docs-workflows-gates.md` 4,323. Rules files warn at 20,000. Every task that edits one measures it.
- **The command never writes `resolve-address`**, not even to say it resolves nothing: `check-branch-check` holds every command naming it to a `branch-check` request (`.claude/rules/gates-branch-check.md`).
- **Choice arrays** are copied verbatim from *Exact copy*; 2–4 options, no "Other"; the command's **Load the question rules.** step precedes its specs preflight and its first question (P3 §4.3).
- **Every executed regex uses `[0-9]`, never `\d`.** ID grammar: no dash-form requirement id is written. **Vendor neutrality:** no tracker name. Name no organisation or outside product.
- **User pages** (`plugins/*/docs/**`, READMEs) carry no `§`, no `D<n>`, no `<plugin>:<reference>` (check 25); a table cell is at most 200 characters (check 6); a page naming `/docs-write` links its page (check 28); a command page links `docs/workflow.md` (check 26). Every claim on a page is derived from the command or reference that runs it.
- **Untrusted values** (D13): nothing read from a backlog, walkthrough, profile, ref name or page reaches a path, ref, name or shell before its class test; `${CLAUDE_PLUGIN_ROOT}` paths in the command and agents; `workflows-core:` references through the loader, with check 16's preamble and, where a load-by-part reference is cited, the load-by-part paragraph.
- **Commits:** `git branch --show-current` immediately before each; expected `feat/doc-d-g1-docs-iteration`. Each message ends with the committing session's attribution lines.

### Gates

One chain, from the worktree root; read the printed value:

```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/lineage.py --selftest && python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest && claude plugin validate plugins/workflows-core && claude plugin validate plugins/docs-workflows; echo "EXIT=$?"
```

Expected: `EXIT=0`; `validate-catalog` prints `0 error(s), 0 warning(s)` (the base's own result); `lineage.py` prints `selftest: 62 passed`; `backlog-lines.py` prints `selftest: <n> passed` with Task 2's count (Task 1 drops that member, which does not exist yet). A task editing a load-by-part reference runs `python3 scripts/reference-parts.py generate` first. `check-docs` takes about four minutes. Where `claude` is not on `PATH`, say so and leave the two `validate` calls to Task 9.

**Tests for command prose are traced runs.** No harness executes a command's prose, so the design's fixtures (*What is left to the builder*) are **scenario traces**: in the task report, the input, each deciding sentence quoted as `file:line`, the outcome, and any step no sentence decides — a defect fixed in that task. One live check goes to `to-test-on-real-project.md` (Task 8).

### Shared names (every task uses these, exactly)

- **Classes:** `UNIT_ID` `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` (unit ids, walkthrough ids, slots); `PAGE_PATH` `^[A-Za-z0-9_][A-Za-z0-9._/-]*\.md$` with no `..` and no empty segment (R6), plus D13's path tests; `OBJECT_ID` `^[0-9a-f]{40}([0-9a-f]{24})?$`; the branch class of `read-only-repos` §3 (`read-only-repos.md:62`), tested as it says.
- **`<top>`** the docs repository's work-tree top level; **`<base>`** its default branch's name by `read-only-repos` §3's chain; **`<default-ref>`** and `specs_git` from the last specs `start` JSON; **`unfinished/`** is `<top>/.dev-workflows/unfinished/`.
- **The script** `${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py`, run as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py" <sub> …`: `check --repo <top>`; `moved --repo <top> --base <name> --id <id> [--id <id> …]`; `edit --repo <top> --id <id> --status drafted [--page-path <rel>]`; `--selftest`. Interfaces in Task 2.
- **`unit-brief.md`**: `${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/unit-brief.md`; its sections §1 *The replaced sections*, §2 *The brief* (fields below), §3 *`doc-writer` under a unit brief*, §4 *`doc-reviewer` under a unit brief*.
- **The brief's fields** (§2): `brief_kind: unit`; `unit` (`id`, `title`, `type`, `audience`, `visibility`, `roles`); `surface` (the row, or `null`); `journey_surfaces` (rows, a tutorial only); `page_path` (absolute); `content_root`; `evidence` (the frontmatter entries, EC §2); `scanner_returns`; `artifacts` (`path`, `ref`, `text`); `walkthrough` (the file's content, or `null`); `review_by`; `repo_authoring_guidance`; `repo_verification_gates`; `profile`; `docs_repo_path`; `code_repos`; reviewer-only: `style_check_report`, `gate_ledger`, `build_summary`, `claims_file`.
- **FH §6** *A backlog run's finish*, subsections §6.1 *The backlog committed*, §6.2 *Adopt or cut*, §6.3 *One commit per unit*, §6.4 *A unit that does not commit*, §6.5 *Push, once*, §6.6 *The pull-request draft, printed*.
- **ST §4's entry point** **regenerate**; **`gate-ledger.md` §8** *The `/docs-write` gate registry* (Hard rules renumbered §9; nothing cites §8 by number at the base).
- **Gate ids:** `toolchain_preflight`, `repo_checklist`, `style_check`, `build_check`.
- **The command's phases** (D5): 0 Resolve, 1 Select and resolve sources, 2 Ground, 3 Place, 4 Branch, 5 Write, 6 Style, 7 Navigation and build, 8 Review, 9 Commit the unit, 10 Finish, 11 Report, 12 Session maintenance & feedback, 13 Follow-ups, 14 Session cost (then the resume pointer and `commit-artifacts`).

### Exact copy

**The command's frontmatter `description`** (533 characters; the warning is at 600):
`Drafts one page per documentation backlog unit — a unit by id, the next actionable one, or up to ten — from the unit's evidence: the code repositories it names, read at their default branch, and an ARD on the specs default branch. Every claim the evidence does not ground is marked, and the page carries a not-yet-verified marker. Regenerates the navigation, runs the build and an Opus review, and commits the page, its navigation and the unit's move to drafted in one commit on a branch. Offers one push; never opens a pull request.`

**Signature:** `/docs-write <unit-id>|--next|--batch <n> [--docs-repo <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

**Arrays:**
- Phase 3, one unit (D5): `choices: ["Write it (Recommended)", "Enter another path (you'll be prompted)", "Cancel"]`
- Phase 3, one unit, no proposed path passes (R22): `choices: ["Enter a path (you'll be prompted)", "Cancel"]`
- Phase 3, a batch (D7): `choices: ["Write these <n> units (Recommended)", "Cancel"]`
- FH §6.2, adopt (D10): `choices: ["Continue on <branch> (Recommended)", "Cut a new branch from <base>", "Cancel"]`
- FH §6.2, the branch name (as `/docs-init` and `/docs-brand` confirm one): `choices: ["Use proposed branch <name> (Recommended)", "Edit the name (you'll be prompted)"]`
- FH §6.2, the clean-tree check and its failed-pull lists: `/docs-init` Phase 2.5 step 2's, verbatim — `["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]`, `["Proceed from current base state (Recommended)", "Cancel"]`, and their unmarked diverged forms.
- Phase 6, violations left after the re-run (as `/document` Phase 6.4): `choices: ["Proceed to review anyway — reviewer may still PASS", "Show remaining violations and let me fix manually", "Cancel"]`
- Phase 8, a review that stayed blocked — `escalation-rules`' `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule, applied with a list of the command's own, since that list's *Defer* names `/document`'s Phase 9 and here permits no move (D8): `choices: ["Provide manual fix notes (you'll be prompted)", "Defer — this unit is not committed, and the report records the finding", "Override and accept the finding (you'll be prompted for the rationale)", "Cancel the whole run"]`. The command says which list it uses, as that rule asks of a citer that reproduces one.
- Phase 2, a scan's escalations, reproduced as `/docs-audit` Phase 2 step 4 reproduces them and for its reason (the page describes the product as it ships): *Dirty working tree* `choices: ["Stash changes and retry this repo", "Skip this repo", "Cancel"]`; *Refresh blocked* on a read by ref `choices: ["Skip this repo", "Cancel"]`. The command says which lists it uses.
- Cited, never reproduced: `finding-triage`'s settle prompts, `escalation-rules`' unspent re-review offer, *Repo missing (after resolution)*, *Refresh blocked* on any other repository, *Read-only mount — ref stale or diverged*, `gate-ledger` §5's conversion, FH §3's push array, `branch-naming` §2.5.

**The page-level marker** (D9; question 2), the first body line after the internal marker where there is one, stated once in EC §3 and cited from `unit-brief.md`:
`[NEEDS CLARIFICATION: this page was drafted from the product's code and specifications and has not been checked against the product itself.]`

**The slot comment** (D9): `<!-- docs-image-slot: <slot> -->`, `<slot>` in `UNIT_ID`.

The blocks below are the text to write, character for character; the fence is not part of it.

**The agents' pointer sentence**, its own paragraph after each agent's core-references preamble:

```text
**A backlog run's brief.** Where your brief carries `brief_kind: unit`, read `${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/unit-brief.md` before anything else: each section of this file that its §1 names for you is replaced by its text there, and everything else here stands. A brief without that field is `/document`'s, and this file is read as it stands.
```

**`doc-structure-conventions` §1's paragraph**, after the paragraph opening `**One exception.**`:

```text
**Outside the rule, because none is provenance:** the evidence contract's frontmatter keys `unit:` and `evidence:`, which a backlog run writes and `/docs-workflows:docs-audit --refresh` reads (`docs-workflows:docs-audit/evidence-contract` §2, `docs-workflows:docs-audit/backlog-format` §3), a walkthrough's image-slot comment `<!-- docs-image-slot: <slot> -->`, and the visibility marker `<!-- docs-visibility: internal -->` (`docs-workflows:docs-workflow/visibility` §5).
```

**`doc-reviewer`'s Source traceability row** — its last sentence, as it stands at `doc-reviewer.md:59`:

```text
A valid `<!-- intentional-discrepancy: … -->` marker (`workflows-core:source-truth` §7.6) is the one permitted comment and is not a finding.
```

becomes:

```text
A valid `<!-- intentional-discrepancy: … -->` marker (`workflows-core:source-truth` §7.6) is not a finding, and neither is anything `workflows-core:doc-structure-conventions` §1 puts outside its rule — the `unit:` and `evidence:` keys, an image-slot comment and the visibility marker.
```

**Printed lines:**
- Phase 0, `unfinished/` not empty: `Unfinished: <dir>[, <dir>…] under .dev-workflows/unfinished/ — files of units an earlier run did not commit; nothing reads them, and they block nothing.` — a name outside `UNIT_ID` optionally followed by `-<n>` is counted, `and <k> more`, never printed.
- Phase 2, a working-tree copy of an admitted `ard.md` that `<default-ref>` lacks (PH:628's line): `Specs: <path> is in the working tree but not on the default branch — not read.`

**E1**, in `workflows-core-git.md:26`: `the thirty-five commands that write` → `the thirty-six commands that write`; `the family's thirty-eight except` → `the family's thirty-nine except`; `returns the same thirty-five:` → `returns the same thirty-six:`; ``five of `docs-workflows`'s seven`` → ``six of `docs-workflows`'s eight``. Nothing else on the line.
**E2**, in `workflows-core-git.md:32`: `eighteen of the thirty-five callers` → `nineteen of the thirty-six callers`; `ten of the thirty-five also resolve` → `ten of the thirty-six also resolve`; `Eighteen is all thirty-five minus the seventeen` → `Nineteen is all thirty-six minus the seventeen`. The "joined" sentence stands.
**E3**, in `specs-repo-git.md:310`: `` `/docs-init`, `/docs-brand`, `/docs-audit`, the four logging commands and `/diagnose-session` `` → `` `/docs-init`, `/docs-brand`, `/docs-audit`, `/docs-write`, the four logging commands and `/diagnose-session` ``.

**`CLAUDE.md`, Task 1** (D17's cut, −74, then the row, +76). In the `docs-workflows` paragraph:

```text
provides seven slash commands — `/document`, `/docs-profile`, `/release-notes`, `/docs-init`, `/docs-brand`, `/docs-serve` and `/docs-audit` — plus eleven subagents
```

becomes:

```text
provides seven slash commands (`ls plugins/docs-workflows/commands`) plus eleven subagents
```

and, after the `docs-workflows-gates.md` row of the rules table, a new row:

```text
| `docs-workflows-backlog.md` | as `docs-workflows.md` | the backlog runs |
```

Later, each of equal length: Task 3 `twenty-four reference files` → `twenty-five reference files`; Task 5 `seven slash commands` → `eight slash commands`, and in the `docs-grounding.md` row `24 command files` → `25 command files` and `thirteen that resolve none` → `fourteen that resolve none`. Expected size 35,980 throughout.

### Rulings where the design is silent or leaves it to the builder

- **R1 — the line shape (a named departure from D13's wording).** D13 lists "a flow mapping or sequence" outside the shape, but BF §1's schema, `ia-planner`'s handoff and every backlog `/docs-audit` writes carry `roles: [customer]`, `blocked_by: []` and quoted `priority_reason` lines, so the words as written stop every run. D13's purpose — no line inside a value can pass for an entry — holds where **every line is a whole item: no value continues past the line it opens on**. In shape: blank and comment lines; `key:`; `key: value`; `- value`; `- key: value`; `- key:`; a value is a plain scalar not opening with `|`, `>`, `&`, `*`, `!`, `%`, `@` or a backtick, a quoted scalar closed on its line, or a flow collection opened and closed on its line (brackets balanced outside quotes); a trailing ` # …` outside quotes; `---` as line 1 only. Out of shape: a block scalar, an anchor, an alias, a tag, a tab anywhere, an unclosed quote or flow collection, any other line form (a plain-scalar continuation), a `units:` whose value is neither empty nor `[]`, an entry not opening `- id: <plain scalar>`, an entry without exactly one `status:` at its key indent holding a plain scalar, an entry with two `page_path:` lines. BF §1 states it, the script implements it, its selftest pins it, and Task 9 appends a dated note under D13 in the design.
- **R2 — one reader.** `backlog-lines.py` does every line-wise read. The orchestrator still reads the backlog with the Read tool for the selection fields — as data, after `check` passed.
- **R3 — from-state.** This release takes `missing` alone; `captured` is sub-project 3's and is still an unrecognised status (BF §3). Any other status refuses the unit, naming it.
- **R4 — a page already carrying the unit's id** (`git -C <top> grep --untracked -l -F -x -e 'unit: <id>' -- <each content root that passes D13's path test, as ':(literal)<root>'>`): `<unit-id>` stops (`DOCS_WRITE_PAGE_TAGGED`), `--next` and `--batch` skip the unit; each names `/docs-workflows:docs-audit --refresh` and each matched page whose path passes `PAGE_PATH`, others counted. Two pages carrying one id is AUD:224's no-match case; this run must not make one.
- **R5 — a clone that is `<top>`** (docs beside code): dispatched with `refresh: {switch_to_default_branch: false, pull: false, read_default_by_ref: true}` under `scan-refresh` §5's "a repository the caller dispatches with settings of its own", whatever the fixed policy says, so no scan moves the run's branch; its report line carries `scan-refresh` §7's read-by-ref wording.
- **R6 — `PAGE_PATH`** is narrower than D13's path test: the path is written as a plain YAML scalar into the backlog, as a pathspec and as a shell word. A proposal outside it is passed over; a typed one is refused and asked again.
- **R7 — an internal unit** is refused where no `builds[]` entry has `visibility: internal` (a `--public-only` scaffold, a profile with no `builds[]`): no build keeps it out of the public site. The internal tree is `<content root>/internal/` (`visibility.md` §1); BF §7's pair is tested against it.
- **R8 — the build and the move.** `build_check` permits the move at `RAN` with every build passing, at `NOT_APPLICABLE` where the profile records no build command at any of `render-verification.md` §1's three levels, and at `SKIPPED_BY_USER` through `gate-ledger` §5's conversion (the decision named in the report and the draft). `FAILED` never does. A content failure gets one `doc-fixer` pass with the build output, as `/document` Phase 6.5 Step 1 hands it, and one re-run; a build still failing ends the unit, with no question.
- **R9 — one ledger per unit**; the run's `toolchain_preflight` row is copied into each. `source_truth_verification`, `render_smoke_check` and `image_review` never appear in it.
- **R10 — the commit message.** Subject `docs: draft <unit-id> (<type>, <audience>)`; where `profile.commit_convention` holds `<summary>` and no other placeholder, that form with `<summary>` = `draft <unit-id> (<type>, <audience>)`; any other placeholder (`<KEY>` among them) falls back to `docs:`, and the report says so. Body: `Unit: <unit-id>` and `Page: <page path>`. No backlog free text enters it; `type` and `audience` are tested against CM §3's vocabulary first.
- **R11 — the branch.** Slug `docs-write-<id>` (one unit) or `docs-write-<first id>-and-<n−1>-more` (a batch), each id lowercased with every character outside `a-z`, `0-9`, `-` dropped (`branch-naming` §1.3); prefix fallback `docs/`; a `branch_naming.pattern` filled as `/docs-brand` Phase 7 step 1 fills it, its issue segment the pattern's documented no-issue literal. A unit id never fills a key placeholder (D13).
- **R12 — cost labels** `documenting`/`dev`, `/document`'s phase: a backlog run writes product documentation, and no new phase reaches `roles-and-phases`.
- **R13 — restoring.** Before its first edit of a file for a unit, the run copies it into its scratch directory (`command mktemp -d -t dw-docs-write-XXXXXX`, `workflows-core:run-flags` §7) and restores it with `command cp --`; a file it created is moved, never deleted (D8).
- **R14 — a Cancel against a unit-level end.** A unit-level end — a build still failing, *Defer*, *Keep the verdict* on a non-`BLOCK` review, a refused commit, R15 — runs FH §6.4 and ends the batch; Phase 10 then offers the push where a unit committed. Any *Cancel* after Phase 4 runs FH §6.4 for the unit in hand, then the stop route: no push offer, the report naming the branch and each unit committed on it.
- **R15 — the ignore test** (ST §7) matching any path of a unit's commit ends the unit (FH §6.4): never a force-add, never a partial commit; the report names the path and the line.
- **R16 — profile commands.** A `builds[]` or lint command holding a line break or other control character is refused before the consent (`DOCS_WRITE_PROFILE_COMMAND`); the rest are shown verbatim in one fenced block in the consent's text.
- **R17 — "unchanged" (D4, D15)** is read as no contract change: caller lists in agent descriptions and openings gain `/docs-write` (Task 7).
- **R18 — one scan round.** `classification` §8.5's seeded second round is not adopted; at most four `code-scanner` dispatches per response, the rest in the next.
- **R19 — evidence.** A surface's `evidence[]`; a `surface: null` unit's own `evidence[]` plus, for a tutorial, each `journey` surface's `evidence[]` in journey order; each entry sorted by D13 before anything is read.
- **R20 — no generated block.** Where ST §4 *regenerate* does not apply (D9), the run adds no navigation entry; the report and the draft name each config with a `nav:` key the page is absent from, for the operator to place by ROUTE's rule. The build decides the rest.
- **R21 — the carve-out names the visibility marker too** (*Exact copy*): `doc-reviewer`'s row calls the discrepancy marker "the one permitted comment", and every internal page `/docs-write` writes carries `<!-- docs-visibility: internal -->`.
- **R22 — placement.** From `doc-location-finder`'s targets, the first of kind `new-page-in-existing-section` or `new-section` whose path, relative to `<top>`, passes `PAGE_PATH` and D13, names no existing file, lies in a declared content root, and keeps BF §7's pair. None passing: the two-option array.
- **R23 — the base for D7** is resolved at Phase 1 by `read-only-repos` §3's chain, reads only; FH §6.2 reuses it.
- **R24 — the authoring guidance.** `unit-brief.md` §2 says how the orchestrator fills `repo_authoring_guidance` (the files and the rule kinds `doc-planner`'s guidance scan names, in its own words) and `repo_verification_gates` (`repo-verification-gates.md` §2–§4, which §5 gains `/docs-write` beside direct mode for).
- **R25 — what the writing agents touch.** A `doc-writer` or `doc-fixer` return whose `files_written` or Fix Report names any path but the unit's page ends the unit (FH §6.4), the report naming each path. The pathspec commit is what bounds a write no agent reported: nothing the run did not write is staged.
- **R26 — `.claude/rules/workflows-core-read-only.md` is not a GIT-G1 file.** It was split out on 2026-10-08, before GIT-G1, edited since by fix batch B40 and the scan-refresh track, and named on no GIT-G1 never-edit list (SEC-G1, IMP-G3, IMP-G5, RETURNED-INTAKE). The command makes two of its sentences incomplete — "The nine commands that … name `prep.read_only`" (ten: `/docs-write` handles a read-only mount as `/docs-audit` does), and the commands that "cite §3 for the default branch each resolves before cutting a branch in a docs repository" (`/docs-write` joins) — and Task 7 makes both true, the pull request naming them for the GIT-G1 owner. Should the controller rule the file GIT-G1, the two become a question, never an edit.

## Review Focus

Inputs a reasonable operator will meet that no gate exercises, most likely first. Each has its test in the owning task.

| # | Input | Expected | Test |
|---|---|---|---|
| RF1 | The backlog `/docs-audit` just wrote: `roles: [customer]`, `blocked_by: []`, a quoted `priority_reason`, trailing `# …` comments | `check` passes; the run proceeds | Task 2 selftest `bf_sample_in_shape` |
| RF2 | A docs site under `site/` in the code repository, that repository among the unit's sources | The scan reads it by ref; the run's branch never moves | Task 5 trace T-R5 |
| RF3 | A page a person already tagged `unit: U-007` while the backlog still says `missing` | `<unit-id>` stops naming the page and `--refresh`; `--next` skips it | Task 5 trace T-R4 |
| RF4 | A profile whose `branch_naming.pattern` and `commit_convention` both hold `<KEY>` | Branch takes the no-issue literal; commit falls back to `docs:`; the unit id fills no key | Task 5 trace T-R10 |
| RF5 | `--batch 3`, unit 2 cancelled at its review escalation | Unit 1 committed and named; unit 2's page under `unfinished/U-…/`, `unit:` gone, nav and backlog restored; no push offer | Task 5 traces T-B1, T-R14 |
| RF6 | A hand-edited `priority_reason: |` block holding `  - id: U-002` | `DOCS_WRITE_BACKLOG_SHAPE` naming the line; nothing written | Task 2 selftest `block_scalar_out`; Task 5 trace |
| RF7 | `doc-location-finder` proposing `docs/guides/My Page.md` | Passed over; the operator is asked for a path | Task 5 trace T-R6 |
| RF8 | A remote branch named `x$(id)` holding a moved backlog | Counted, never printed or interpolated; `--next` still decides | Task 2 selftest `ref_name_outside_class` |

---

### Task 1: Room — the backlog rules file and `CLAUDE.md`'s cut [mechanical]

**Files:**
- Create `.claude/rules/docs-workflows-backlog.md` (`paths:` identical to `docs-workflows.md`'s four globs).
- Modify `.claude/rules/docs-workflows.md`: move out the `/docs-audit` map line (:38, 1,479 characters) and the three caller lines `docs-auditor`, `ia-planner`, `docs-audit-reviewer` (:45-47, 253); extend the "Split out" paragraph (:13) with `` `/docs-audit`'s map line, its three agents' caller lines and the backlog runs' map lines and invariants → `.claude/rules/docs-workflows-backlog.md` ``.
- Modify `.claude/rules/docs-workflows.md:31`, the map section's opening: it names `docs-workflows-backlog.md` as where `/docs-audit`'s line and its agents' lines now are.
- Modify `CLAUDE.md`: Task 1's two edits in *Exact copy*.

**Interfaces:** produces the file Tasks 2–5 write into: heading `# docs-workflows — the backlog runs`, an opening paragraph in `docs-workflows-gates.md`'s form, and `## Workflow map` (the moved line and caller lines, in a fenced block as moved). Task 2 adds `## Invariants` with its first entry.

- [ ] **Step 1: Move**, byte for byte. `git diff --stat` shows three files.
- [ ] **Step 2: Measure.** `docs-workflows.md` ≈ 18,400; the new file under 4,000; `CLAUDE.md` 35,980.
- [ ] **Step 3: Gates** (without the `backlog-lines.py` member). `validate-catalog` reports the new file's globs live. **Step 4: Commit:** `chore(doc-d-g1): the backlog runs' rules file, and room in CLAUDE.md`.

### Task 2: The line reader [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/scripts/backlog-lines.py` (stdlib only, docstring in `key-discovery.py`'s form).
- Modify `plugins/docs-workflows/references/docs-audit/backlog-format.md` §1: a paragraph `**The line shape a backlog run reads.**` stating R1 and naming the script as its implementer; the opening's entry-point list unchanged (it is §1's).
- Modify `.github/workflows/validate-catalog.yml` **only under Q1's approval**: one step `name: Self-test the backlog line reader`, after "Self-test the key discovery", with a comment in that step's style naming the silent failures — a value spanning lines read as an entry, a status moved outside its entry, a ref name reaching a command — and `run: python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest`.
- Modify `.claude/rules/docs-workflows-backlog.md`: a `## Invariants` section, its first entry — BF §1's line shape and `backlog-lines.py` change together in one commit, the selftest pinning the script to the paragraph.

**Interfaces** (Task 5 calls these exactly). Every subcommand prints one JSON document; exit 0 = ran (the answer is in the JSON), 2 = could not run, or an argument outside its class (cause on stderr), 3 = `edit` refused on the file's content before writing, 4 = `edit` undone. The file is always `<top>/.dev-workflows/docs-backlog.yml`; files above 8 MiB, and blobs above 1 MiB on a ref, are not read. Git runs as an argument list, never a shell, with a 30-second timeout.
- `check --repo <top>` → `{"shape": "ok", "units": <n>, "duplicates": [<id>…], "duplicates_outside_class": <n>, "ids_outside_class": <n>}` or `{"shape": "out", "line": <n>, "reason": "<word>"}`, `<word>` one of `block-scalar`, `anchor`, `alias`, `tag`, `tab`, `unclosed-quote`, `unclosed-flow`, `continuation`, `units-not-block`, `entry-opener`, `status`, `page-path-twice`, `too-large`. Only ids in `UNIT_ID` are printed.
- `moved --repo <top> --base <name> --id <id> …` → reads HEAD's branch itself; lists `for-each-ref --sort=-committerdate --format='%(objectname) %(refname:short)' refs/heads refs/remotes/origin`; drops `origin/HEAD`, HEAD's branch, `<base>` and `origin/<base>`, and every name outside the branch class (counted); keeps a ref not merged into `origin/<base>` (else the local `<base>`) whose backlog differs from the merge base's; reads the first 20 by object id (each tested against `OBJECT_ID`) with `cat-file`; compares each `--id`'s status there with its status in the working file. → `{"moved": {<id>: [<ref>…]}, "unreadable": [<ref>…], "read": <n>, "more": <n>, "names_outside_class": <n>}`. An entry absent on a ref, or a ref with no backlog, is not moved; a blob over 1 MiB, out of shape, or with the id twice or its status outside `^[a-z][a-z-]{0,31}$` is `unreadable`. `--base` and each `--id` are class-tested first (exit 2).
- `edit --repo <top> --id <id> --status <s> [--page-path <rel>]` → shape-tests the file; finds the one entry; replaces the `status:` value and, where `--page-path` is given and `page_path` is `null`, that value — keeping indent, key and any trailing comment, and every other byte; exits 2 on an `--id`, a `--status` (`^[a-z][a-z-]{0,31}$`) or a `--page-path` outside its class, and 3, file untouched, on an out-of-shape file, an absent or duplicated id, or a `page_path` already set to another path; writes atomically; runs `git -C <top> diff -U0 --no-color --no-ext-diff -- .dev-workflows/docs-backlog.yml` and holds every hunk inside the entry's lines and to the one or two lines it changed, else writes back the bytes it read and exits 4. → `{"first": <n>, "last": <n>, "changed": [<n>…]}`.
- `--selftest` → `selftest: <n> passed`, exit 0; fixtures and a git repository built at run time.

- [ ] **Step 1: The failing selftest.** Write the script with argument parsing, stubs returning nothing, and these cases (each name, then its assertion):
  - `bf_sample_in_shape`: BF §1's sample block, verbatim → `shape: ok`, `units: 1`.
  - `block_scalar_out`: `priority_reason: |` with `  - id: U-002` under it → `out`, its line, `block-scalar`.
  - `quoted_multiline_out`, `flow_multiline_out`, `continuation_out`: a double-quoted value, a flow sequence and a plain value each continued on the next line → `unclosed-quote`, `unclosed-flow`, `continuation`.
  - `anchor_alias_tag_tab_out`: four files → `anchor`, `alias`, `tag`, `tab`.
  - `units_flow_out` / `units_empty_ok`: `units: [{id: U-1}]` → `units-not-block`; `units: []` → `ok`, `units: 0`.
  - `id_quoted_out`: `- id: "U-001"` → `entry-opener`.
  - `duplicate_id`: two entries `U-001` → `duplicates: ["U-001"]`; an id `x y` → `ids_outside_class: 1`.
  - `moved_on_branch`: a repository whose branch `feat/a` moved `U-001` to `drafted` and whose `main` did not → `moved: {"U-001": ["feat/a"]}`; merged into `main` → nothing.
  - `ref_name_outside_class`: a branch `x$(id)` holding a moved backlog → `names_outside_class: 1`, its name in no output.
  - `ref_unreadable`: an out-of-shape blob and a 1.1 MiB blob on two refs → both in `unreadable`; `absent_not_moved`: a ref with no backlog → not moved; `twenty_cap`: 22 qualifying refs → `read: 20`, `more: 2`.
  - `edit_two_keys`: `status` and a `null` `page_path` changed, every other byte equal (CRLF file included), `git diff -U0` inside the entry.
  - `edit_page_path_set`: `page_path` set elsewhere → exit 3, file byte-equal.
  - `edit_undo`: a backlog already dirty on another line → exit 4, file byte-equal to what it read.
  - `bad_args`: `--base 'a;b'`, `--id '../x'`, `--status 'Drafted!'`, `--page-path 'a/../b.md'` → exit 2, no file read or written.
  Run `python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest`. Expected: FAIL naming the first case.
- [ ] **Step 2: Implement** the three subcommands to the interfaces above. The line grammar is R1's; the entry spans from its opener to the line before the next line at its indent opening `- ` or the next column-0 line.
- [ ] **Step 3: Run the selftest.** Expected: `selftest: <n> passed` (≥ 19), exit 0. Record `<n>` for the gate chain.
- [ ] **Step 4: BF §1's paragraph and the invariant.** Then, under Q1's answer, the CI step (or nothing, and a note for Task 8's `to-fix` entry).
- [ ] **Step 5: Gates. Step 6: Commit:** `feat(doc-d-g1): backlog-lines.py — the one line reader of the documentation backlog`.

### Task 3: The unit brief, and the two agents [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/references/docs-iteration/unit-brief.md`, with the core-references preamble (check 16) for its `workflows-core:` citations.
- Modify `agents/doc-writer.md` and `agents/doc-reviewer.md`: the pointer sentence; each description and opening (`doc-writer.md:3`, :9; `doc-reviewer.md:3`, :10-12) names `/docs-write` beside `/document`; `doc-reviewer`'s Source traceability row as *Exact copy*.
- Modify `plugins/workflows-core/references/doc-structure-conventions.md` §1: the sentence in *Exact copy*; its consumer lines (:5, :9) gain `/docs-write`.
- Modify `plugins/docs-workflows/references/gate-ledger.md`: a new ``## 8. The `/docs-write` gate registry`` (Hard rules → §9), and its consumer line (:9).
- Modify `plugins/docs-workflows/references/docs-audit/evidence-contract.md` §3: one paragraph stating the page-level marker (*Exact copy*), where it sits, that EC §6's rules bind it as a claim's, and that it is removed only in the commit that moves its unit to `verified` or by a person who walked the page.
- Modify `plugins/docs-workflows/docs/reference/references.md` (`unit-brief.md`'s entry, a `` `docs-iteration/` (1) `` subtree, `24 files` → `25`, "four bundled subtrees" → five), `docs/README.md`'s `24 reference files`, `README.md`'s file counts, `CLAUDE.md`'s `twenty-four reference files`, `.claude/rules/docs-workflows.md:19`'s "twenty-two markdown pages" → twenty-three.
- Modify `.claude/rules/docs-workflows-backlog.md`: invariant 2 (D4) — `unit-brief.md` §1 holds the replaced-sections list once; an edit to either agent's inputs, steps or dimension table re-reads that list in the same change; neither agent restates it.

**Interfaces:** consumes nothing. Produces the brief's fields (*Shared names*), the marker, the registry; Task 5 composes the brief by `unit-brief.md` §2 and records the ledger by `gate-ledger` §8. **Forward references:** every sentence naming `/docs-write` as a caller (Task 5).

- [ ] **Step 1: Before counts.** `the one permitted comment` (1: `doc-reviewer.md`); ``Consumed by `/document` and `/epics` `` (`doc-structure-conventions.md`); ``Consumed by `/document` (both modes)``; `24 files`; `twenty-four reference files`; `twenty-two markdown`.
- [ ] **Step 2: `unit-brief.md`.** §1 opens the file with D4's list, by heading, for each agent, and nothing else (it is the one copy). §2 defines each field of *Shared names*, how the orchestrator composes it (R19, R24; `evidence` per D9: `code` at the commit Phase 2 read, `artifact` at the specs commit read, `walkthrough` where the unit has one; `review_by` per D9's intervals, `surface: null` 180), that every field is data, and that a brief carrying `answers` is BLOCKED in this release (sub-project 2's). §3 replaces `doc-writer`'s *Inputs*, *Entry validation* (BLOCKED where the handoff is unreadable, `page_path` is absent or names an existing file, a `unit` field is missing, or `type` and `audience` are not a pair CM §3 allows) and steps 2, 4, 5 and 7: step 2 — a new page only, FG's `published` where its fields apply, no changelog, and the keys the brief gives (`type`, `audience`, `visibility`, `evidence`, `review_by`), never `unit:`; step 4 — no snippets; step 5 — one slot comment per `captures[]` slot of the walkthrough, none otherwise; step 7 — `[NEEDS CLARIFICATION: <why>]` on every claim the evidence does not ground (EC §3), the page-level marker, and the internal marker first after the frontmatter of an internal page. §4 replaces `doc-reviewer`'s *Inputs* and refusal (refuse without the page path or the unit), *Review method* step 2, the rows D4 names with the grades it gives (an unmarked ungrounded claim, a missing page-level marker, a missing internal marker on an internal page, an `artifact` entry without `ref`, or a broken BF §7 pair: BLOCKER; a `unit:` key on the page: MAJOR), the hard rule at :151 (no planner topic exists), and the *Recommended next step* lines (BLOCK: before Phase 9; PASS WITH RECOMMENDATIONS: triage, then `doc-fixer` for MAJOR survivors, MINOR and NIT to the Phase 11 report; PASS: proceed to Phase 9). No dimension is added; every heading of the output shape stays.
- [ ] **Step 3: The two agents, the carve-out, EC §3, the registry.** `gate-ledger` §8: a table in §4's shape for the four gate ids (`toolchain_preflight` 0, always; `repo_checklist` 6; `style_check` 6, fallback `prose-style-checker` alone; `build_check` 7, precondition "the profile records a build command at one of `render-verification.md` §1's three levels", fallback none), R9's two sentences, and that §2, §3, §5 and §6 apply unchanged.
- [ ] **Step 4: Traces.** A keyed and a direct `/document` dispatch through both agents: no sentence reaches `unit-brief.md` (D15). A unit brief through each agent: every section §1 names is replaced, and every other section of the agent reads true for a single new page with no planner — list each standing section and the line that keeps it true. A brief with `answers`: BLOCKED.
- [ ] **Step 5: After counts**; sizes of `doc-writer.md`, `doc-reviewer.md` (descriptions under 600), `docs-workflows.md`, `CLAUDE.md`.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(doc-d-g1): the unit brief — what a backlog run changes for doc-writer and doc-reviewer, and its gate registry`.

### Task 4: The finish, and the navigation [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/references/finish-and-handoff.md`: title and opening name §6; new `## 6. A backlog run's finish`.
- Modify `plugins/docs-workflows/references/docs-workflow/scaffold-tree.md` §4: the **regenerate** entry point; the entry-point list (:7) gains it.
- Modify `plugins/docs-workflows/references/repo-verification-gates.md` §5 (and its consumer line): a `/docs-write` bullet beside direct mode — the orchestrator extracts at Phase 0, `doc-reviewer` holds the page against it, Phase 6 records `repo_checklist`.
- Modify `.claude/rules/docs-workflows-backlog.md`: invariant 3 (D8: a unit moves only in its commit; `unit:` written only at Phase 9; a page that never reached it carries no id) and invariant 4 (D10: one consented push; the draft printed only; no pull request opened; nothing written into a source repository or as a specs deliverable).

**Interfaces:** produces FH §6.1–§6.6 and **regenerate**, which Task 5's Phases 0, 4, 7, 9 and 10 cite by name. **Forward references:** "the backlog runs" and `/docs-write` (Task 5).

- [ ] **Step 1: FH §6**, the words cited by all three commands:
  - **§6.1** D10's committed test, verbatim commands: `git -C <top> status --porcelain -z -- .dev-workflows/docs-backlog.yml` prints nothing and `git -C <top> ls-files --error-unmatch -- .dev-workflows/docs-backlog.yml` exits 0; else the stop names the commit to make.
  - **§6.2** once per run: HEAD's branch, class-tested; on `<base>` or detached, or outside the class, cut; on another branch in the class, the adopt array. The clean-tree check runs either way: `/docs-init` Phase 2.5 step 2's question and lists, verbatim, its read being `git -C <top> status --porcelain -- ':(exclude).dev-workflows/unfinished'`, each dirty path named; a *Stash* runs `escalation-rules` § *Stashing the user's changes*. Cutting copies that step's base resolution, switch, pull, diverged-base and failed-switch handling in FH's own words (the one copy for the backlog runs), with R11's name and confirmation array. Stacked units make one pull request.
  - **§6.3** ST §7's commit-time ignore test over every path of the unit (R15), then `git -C <top> add -- <paths>`, `git -C <top> commit -F <msg> -- ':(literal)<path>' …`, the index brought back in step as §2 does; the message per the command's rule, through a `command mktemp -t dw-docs-msg-XXXXXX` file removed afterwards; each value single-quoted, `'` written `'\''`.
  - **§6.4** D8's sequence: remove a `unit:` line the run wrote; move each file the run created for the unit under `unfinished/<unit-id>/`, else the first free `<unit-id>-<n>/` from 2, relative layout kept, `command mkdir -p --` and `command mv --`, never overwriting; restore each file it edited from its saved copy (R13), the navigation configs and the backlog alike; nothing deleted, nothing stashed, no `.gitignore` edited; the run names the directory.
  - **§6.5** FH §3's array and rules, offered once, after the last unit, only where this run committed a unit and HEAD is still on the run's branch.
  - **§6.6** D10's facts, printed only: the units moved and their pages, review verdicts and triage lines, build results, markers left (per page: claims marked, and the page-level marker), deferred items, paths left unstaged, `unfinished/` directories; no file, no host footer.
- [ ] **Step 2: ST §4 regenerate**, its obligations: it applies only where every config a `builds[]` entry names holds a comment line beginning `# generated:` directly under its `nav:` key (one config under `--public-only`); it reads the pages the commit will hold — `git -C <top> ls-files -z` under the content root plus the pages the commit adds, `.md` only, `_snippets/` excluded, `internal/` excluded from the public config; it sorts each section by `order`, then `title`, a page with no `order:` last (§4's rule); a section keeps the label the block gives it, else its index page's `title`; it rewrites the block from `nav:` to the next top-level key, keeping the two comment lines; it never branches on `generator`. Where it does not apply, R20. The paragraph opening `**Until that command ships**` is Task 7's.
- [ ] **Step 3: Traces** against the text alone: a scaffolded repository, `--public-only`, a non-scaffolded repository (R20), an adopted branch with a dirty nav config (*Proceed anyway*, then FH §6.4 restores that dirty content), a second failure of one unit (`<unit-id>-2/`), a commit a hook refuses (no `unit:` left, backlog restored).
- [ ] **Step 4: Measure** the rules file. **Step 5: Gates. Step 6: Commit:** `feat(doc-d-g1): a backlog run's finish (FH §6) and nav regeneration (ST §4)`.

### Task 5: The command [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/commands/docs-write.md` (`disable-model-invocation: true`; `allowed-tools: Read Write Edit Bash Glob Grep Task Skill`; the core-references preamble; the load-by-part paragraph; the relay sentence of check 20 as its own paragraph, copied from `docs-audit.md:287`).
- Create `plugins/docs-workflows/docs/commands/docs-write.md`, in `docs/commands/docs-audit.md`'s sections (*Who runs it*, *Synopsis*, *What it needs*, *Phases* with a mermaid flow, *Gates*, *Outputs*, *Failure modes*, *Example*, *See also*), linking `../workflow.md` and `../docs-workflow.md`.
- Modify for the gates the command trips: `plugins/workflows-core/scripts/command-namespaces.json`; `cost-emission.md` §7 (the row ``| `/docs-write` | documenting | dev |``) and §8's documentation branch and its paragraph at :616; `feedback-emission.md` §2's documentation branch; `branch-naming.md` §2.4 (the row ``| `/docs-write` | `docs/` |``) and §3 (R11's slug); `docs-workflows/README.md` (`Seven slash commands` → `Eight`, a table row, the *Documentation workflow* paragraph's "has not shipped" sentence); `docs/README.md` (a row, the Commands bullet, `7 slash commands` → 8); `docs/workflow.md` (a mermaid node and its edges, every label quoted where it holds a bracket; the collision line's list; its first `/docs-write` linked); `docs/docs-workflow.md` (its first mention of `/docs-write` linked to the page — check 28 holds the route page from the moment the command exists; the rewrite is Task 6's); `docs/reference/session-cost.md` (`Five commands` → `Six`, and its lists).
- Modify `references/docs-audit/backlog-format.md` §3: the `missing → drafted` row names `/docs-write`, :109's writer count, and :122's premise rewritten (D9: a backlog run's page always carries a marker until verified, so the publish edge reaches only a page a person tagged).
- Modify `.claude/rules/docs-grounding.md` (`paths:` gains the command; the bold sentence and its reasons gain `/docs-write`: an existing page is none of EC §2's three evidence kinds), `CLAUDE.md` (Task 5's edits), `.claude/rules/docs-workflows-backlog.md` (the map line; invariant 5 — `$SPECS_PATH` is never a `code-scanner` target, and the artifact set is `ard.md` at `<default-ref>` alone), `.claude/rules/docs-workflows.md` (caller lines :40, :41, :43; :27's `24 pages` → 25 and `7 command pages` → 8).
- **E1, E2, E3**, verbatim from *Exact copy*, last.

**Interfaces:** consumes Task 2's subcommands, Task 3's brief and registry, Task 4's FH §6 and **regenerate**. Produces the behaviour every earlier forward reference names.

- [ ] **Step 1: Before counts.** E1's recipe, as `workflows-core-git.md:26` prints it, piped to `wc -l` (35); `grep -l 'workflows-core:model-routing' plugins/*/commands/*.md | wc -l` (30); `… impl-maintenance …` (29); `… emit-cost …` (29); `grep -l 'prep.read_only' plugins/*/commands/*.md | wc -l` (9); `check-questions`' count (37).
- [ ] **Step 2: Phase 0 — Resolve** (D3, D5). Strip run flags; **Load the question rules.**; parse: exactly one of `<unit-id>` (`UNIT_ID`), `--next`, `--batch <n>` (1–10), `--docs-repo <path>` with its value, any other `--` token a stop. Pre-target stops take no tail (`DOCS_WRITE_UNKNOWN_FLAG`, `DOCS_WRITE_SELECTOR`, `DOCS_WRITE_BAD_BATCH`, a run-flag stop, the ladder's Cancel, `DOCS_WRITE_NOT_A_REPOSITORY`), and *Ending early* states that refusal by its own words (SRG §4's permission; D3). `resolve-docs-repo` with `--docs-repo` as its rung-1 token, else from rung 2; `<top>` = `rev-parse --show-toplevel`, else the refusal. Every later stop takes the stop route. `test -w <top>`; `specs-preflight` keyless; the profile (absent or unreadable: `DOCS_WRITE_NO_PROFILE` naming `/docs-workflows:docs-profile`); R16; the backlog (absent; `schema_version` not 1; FH §6.1; `check` out of shape — the line and reason; a duplicate id: each a stop); the `Unfinished:` line; the toolchain preflight (the `toolchain_preflight` row); `repo_authoring_guidance` and `repo_verification_gates` (R24); `model-routing` — MODERATE, `doc-writer` on the §2 Opus chain (§9.2), `doc-reviewer` at its pin, the rest on the §2.1 detection chain, §10 honoured.
- [ ] **Step 3: Phase 1 — Select and resolve sources** (D7, D13, D14). `<unit-id>`: whole match against `units[].id`; R3; `blocked_by`; R4; a `release` surface (`DOCS_WRITE_RELEASE_UNIT`, naming ST:73's manual paste); a `type`/`audience` pair CM §3 refuses; R7 — each a stop naming the one thing to change. `--next`/`--batch`: D7's candidate rule (batch excludes `tutorial` and `how-to`), the same tests skipping rather than stopping, `<base>` by R23, then `moved` over the candidates, skipping each it names and carrying `unreadable` to the consent; none left is `DOCS_WRITE_NO_CANDIDATE`, naming why each was passed over, and a batch that finds fewer than `<n>` takes what it found and says so. Then R19 and D13's sort: artifact entries (`kind: artifact`, or a `repo` whose `sources[]` path resolves to the real path of the environment's `$SPECS_PATH`) to D14's set and `specs_git`/no-repository refusals; code entries by `sources[].repo`, then `docs-profile-schema.md:100`'s order, admitted under `${REPOS_PATH:-/workspace}` or by the consent, refused at or inside `$SPECS_PATH`; an evidence path failing D13's path test refuses the unit.
- [ ] **Step 4: Phases 2 and 3.** Phase 2 runs where D5 puts it: for one unit, after Phase 1; for a batch, per unit after Phase 4's re-check. It reads artifacts by `git -C "$SPECS_PATH" show "<default-ref>:./<path>"` and the PH:628 line; `code-scanner` per clone — themes `[unit title, surface title]`, a `context` composed from type and audience, `search_hints.paths` its evidence paths, the fixed policy through `scan-refresh refresh-question` with `asks: false`, R5, R18; every status handled as `/docs-audit` Phase 2 step 4 handles it (its lists, its read-only mount rule, which names `prep.read_only`); *Skip this repo* leaves that repository's claims unread, so marked; each `prep.scanned_ref` resolved to its commit. Phase 3: a unit whose `page_path` is set takes that path where R6 and D13 pass and no file is there, without `doc-location-finder`, else `DOCS_WRITE_PAGE_PATH` naming `/docs-workflows:docs-audit --refresh` (a batch drops the unit); every other unit `doc-location-finder` (repo root, a composed `feature_summary`, the profile) and R22; then the consent — its text lists the unit, each clone path, each artifact path, the page path, the branch, each `unreadable` ref, the profile commands per R16 — with the one-unit, no-path or batch array.
- [ ] **Step 5: Phases 4–9.** Phase 4: FH §6.2; then `check` and the entry re-read on the new branch — same id, same status, `blocked_by` empty — else `DOCS_WRITE_UNIT_CHANGED` (one unit) or the unit dropped and named (batch). Phase 5: the handoff file (`command mktemp -t dw-docs-write-XXXXXX`) per `unit-brief.md` §2; `doc-writer`. Phase 6: `docs-style-checker` with `/document` Phase 6.4's brief fields, the `style_check` and `repo_checklist` rows, `doc-fixer` on violations untriaged, one re-run, the Phase 6 array. Phase 7: **regenerate**, then the builds (R8), each recorded in the one `build_check` row. Phase 8: `doc-reviewer` per `unit-brief.md` §4; triage by `finding-triage re-review` (the `doc-reviewer → doc-fixer` row); `doc-fixer` on survivors with `/document` Phase 7's *Decisions* line; one fix cycle, one re-review with `claims_file`; the unspent re-review offer; the stayed-blocked array, per BLOCKER; R25 after each writing dispatch; any edit after Phase 7 re-runs Phase 7. D8's permitting outcomes, stated as a list. Phase 9: the `unit: <id>` line last in the frontmatter, then `edit` (exit 3 or 4: FH §6.4), then FH §6.3; a refused commit: FH §6.4. R13 and R14 throughout; a batch then takes its next unit at Phase 4's re-check.
- [ ] **Step 6: Phases 10–14 and the invariants.** Phase 10: FH §6.5, FH §6.6. Phase 11: the report — *Classification*, *Model Routing*, *Target*, *Selection* (each skipped candidate and why), *Sources* (per clone, `scan-refresh` §7's slot; artifacts and their commits), *Units* (per unit: page, markers, verdict and triage line, build results, commit or `unfinished/` directory), *Verification gates*, *Deferred items*, *Git state*, *Pull-request draft*, *Untrusted-content notices*, `### Next step` by `next-phase-offer not-pipeline` with no `<merge-clause>`, the omission stated as `/docs-audit` states it. Phases 12–14 as `/docs-audit` Phases 7–9: `command: /docs-write`, `key: null`, the documentation branches, `emit-cost` with `documenting`/`dev` (R12), the resume pointer's rung 2, `commit-artifacts` by `args: "specs-repo-git commit-artifacts"` last. An invariants list in `/docs-audit`'s form.
- [ ] **Step 7: The page, the index entries, the core rows** listed under *Files*; the CHANGELOG is Task 8's.
- [ ] **Step 8: E1, E2, E3.** Re-run E1's recipe: it prints 36 and names `docs-write.md`. Apply each verbatim. Measure `workflows-core-git.md` (19,986).
- [ ] **Step 9: Traces**, each quoting the command's deciding lines: T-N `--next` on a scaffolded repository (one commit holds page, nav and backlog; `git show --stat`); T-STOP a run stopped after Phase 5 then `/docs-audit --refresh` (no `unit:`, unit `missing`, AUD:224); T-MERGE the backlog move lost in a merge then `--refresh` (`drafted`, by the page-level marker); T-B1 a `--batch 3` whose second unit fails its build (batch ends, `unfinished/`, nav restored), then that unit failing again (`-2/`) and a clean-tree check that asks about neither; T-HOOK; T-DEC a `decision` unit (its ARD at `<default-ref>`, no scan of `$SPECS_PATH`); T-SHAPE RF6; T-REF an unreadable ref in the consent; T-NOSCAF R20; T-PUB `--public-only` and an internal unit (R7); T-UNC an uncommitted backlog; T-DUP; T-BLK `blocked_by`; T-PP a `missing` unit with `page_path`; T-NULL a `surface: null` unit; T-TUT a minted tutorial; T-INT an internal unit in a two-build repository; T-MOVED; T-REFNAME; T-ART an artifact outside D14's set; T-CLONE a clone outside `${REPOS_PATH}`; T-REL a `release` unit; T-NOGIT a non-git target (no tail); and T-R4, T-R5, T-R6, T-R10, T-R14 of *Review Focus*.
- [ ] **Step 10: After counts.** The five recipes print 36, 31, 30, 30, 10; `check-questions` 38. Every page naming `/docs-write` links its page.
- [ ] **Step 11: Gates. Step 12: Commit:** `feat(doc-d-g1): /docs-write — a backlog unit drafted, navigated, built, reviewed and committed in one commit`.

### Task 6: The pages [mechanical]

**Files:** `plugins/docs-workflows/docs/`: `docs-workflow.md`, `workflow.md` (prose), `roles-and-phases.md`, `getting-started.md` where it lists commands, and `reference/` — `agents.md`, `references.md` (FH, ST, BF, EC, gate-ledger, repo-verification-gates entries), `docs-backlog.md`, `docs-evidence.md`, `model-routing.md`, `session-feedback.md`, `resume-and-checkpoints.md`, `environment.md`; `plugins/docs-workflows/README.md`; `plugins/workflows-core/docs/family-map.md` (a node, :192's bullet), `roles-and-phases.md`, `reference/agents.md`, `reference/session-feedback.md`; the repo-root `README.md` (the table's `Seven commands`, the `DOCS_PATH` write-target list). In words: no `§`, no `D<n>`, no `<plugin>:<reference>`.

- [ ] **Step 1: The route page.** Step 4's heading becomes ``### 4. Write the next unit — `/docs-write` ``: what the run selects and refuses, what the page carries (the four reserved keys, `unit:` only in the commit that moves the unit, `evidence`, `review_by`, the marked claims, the page-level marker), the navigation and the build, the review, the one commit, the push offer and the printed draft, `unfinished/`, and the by-hand procedure kept for a page written any other way. The loop's opening sentence, step 4's two costs and *What helps today*, and the *Later* line go; steps 5 and 6 keep their *Later* lines, and step 6 gains removing the page-level marker once every claim is walked. *What to expect* reads true.
- [ ] **Step 2: Every other page in the list**, each statement derived from the command or reference that runs it. `roles-and-phases.md`: `/docs-write` in the Dev role's runs, consumes, produces, hands over; `five cost-emitting commands reach four phases` → six; *documenting* names it.
- [ ] **Step 3: Gates. Step 4: Commit:** `docs(doc-d-g1): the pages — /docs-write on the route and in every inventory`.

### Task 7: The sweep [mechanical]

**Files:** whatever the sweep finds false over refinement 4's scope. No GIT-G1 file; `CLAUDE.md` net-zero.

- [ ] **Step 1: The table.** For each of D17's subjects — *who writes `unit:`*; *who regenerates the navigation*; *who composes a walkthrough or renders the checklist*; *which edges have a writer*; *what is manual on the route*; *which command dispatches each agent*; *which commands consume each shared reference*; *the counts* — list every statement, its file, and whether it is now true. Known sites: BF:7, EC:7, :99, :105; FG:87 (re-pointed to this design), :108; ST:5, :73, :464, :466 (pages written another way, `/document` among them, still by hand: DOCUMENT-NAV); `visibility.md:5`; RR:10; `toolchain-preflight.md:10`; `branch-naming.md:7`; `code-scanner.md:9`; `doc-fixer.md:3`; `doc-location-finder.md:7`; `docs-style-checker`'s description; `finding-triage.md:36` and the style-checker row; `escalation-rules.md:377` (six → seven, the clean-tree check named), :416-420, :463-467, :449, :670 and :886 (each list gains `/docs-write` as it uses the rule — at :886 with its own list, *Exact copy*'s Phase 8 array); `next-phase-offer.md:418`; `followup-emission.md:7-9` (twelve → thirteen); `cost-emission.md:3-4` (twenty-nine of thirty-one → thirty of thirty-two), :687, :907; `feedback-emission.md:3`, :237 (twenty-nine → thirty); `.claude/rules/workflows-core.md:30`, :38, :51-52, :59 (29 of the 38 → 30 of the 39); `workflows-core-model-routing.md:30` (Thirty → Thirty-one; six of `docs-workflows`'s seven → seven of eight; one of seven → one of eight); `workflows-core-triage.md:14`; `docs-workflows-gates.md:15`, :17, :19; `workflows-core-read-only.md:24`'s two sentences (R26).
- [ ] **Step 2: The exclusivity probe** over `the only`, `only writer`, `no command`, `by hand`, `no automated writer`, `nothing in this increment`, `is planned`, `a later command`, `a later spec`, `Spec 2`, and the noun forms for the backlog's writers and the agents' callers.
- [ ] **Step 3: Edit each false statement**; `python3 scripts/reference-parts.py generate` after the load-by-part references. A false sentence in a GIT-G1 file is reported, not edited.
- [ ] **Step 4: After counts** for each string changed; the probe re-run. **Step 5: Gates. Step 6: Commit:** `docs(doc-d-g1): the remaining copies`.

### Task 8: Release [mechanical]

**Files:** `plugins/docs-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, both `CHANGELOG.md`, `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/to-fix.md`, `to-test-on-real-project.md`, `reviews/2026-10-26-feature-gaps-review.md`.

- [ ] **Step 1: Merge.** `git fetch origin`; where `origin/main` moved, `git merge --no-edit origin/main`, keep both sides, re-derive every count and size this plan touched, E1's recipe included.
- [ ] **Step 2: Versions from `origin/main` now** (plan time: `docs-workflows` 1.40.0, `workflows-core` 1.96.0): each the next free minor (D16). `plugin.json` equals `marketplace.json`. Each CHANGELOG section dated with the landing day (UTC). `docs-workflows`' description gains `/docs-write` by **replacing** words, under 900 characters (861 now). `workflows-core`'s CHANGELOG names E1–E3 and C1 if approved; `docs-workflows`' names R1's departure and the limits (R7, R20, the from-state of R3).
- [ ] **Step 3: One coupling bullet** (D16), under 700 characters: newer `docs-workflows` beside an older `workflows-core` — the reviewer's rule contradicts its own row, the cost entry waits in pending, the manifest lacks the command; update both. The file stays under 19,000, so no history split, which would cost `CLAUDE.md` a row.
- [ ] **Step 4: `to-fix.md`.** A *From DOC-D-G1* section: WHATSNEW-WRITE (`release` units and their two GIT-G1 edits); DOCUMENT-NAV (`/document` keyed places pages by hand while ST §4 has an entry point); R20's hand-maintained navigation; BACKLOG-LINES-CI if Q1 declined; what each task review left.
- [ ] **Step 5: `to-test-on-real-project.md`.** DOC-D-G4 (:258) runs step 4 as `/docs-workflows:docs-write --next`. A new entry headed with this release's versions: on the bookstore demo, `--next` commits page, navigation and backlog move in one commit, the strict public build passes over it, and `/docs-audit --refresh` leaves the unit `drafted`; what a miss looks like.
- [ ] **Step 6: The feature-gaps review**: DOC-D-G1's heading (:285), index row (:48) and summary (:13) gain *Designed in* the design's path and sub-project 1's versions; DOC-D-G2 (:292) gains that pages now exist by command.
- [ ] **Step 7: Gates**; measure `CLAUDE.md` and every rules file touched. **Step 8: Commit:** `release(doc-d-g1): docs-workflows <X>, workflows-core <Y> — /docs-write`.

### Task 9: Close [security-sensitive]

- [ ] **Step 1: Consistency.** Every array, printed line, marker, pointer sentence, carve-out and E1–E3 is verbatim in the file that owns it (`command grep -F` each). BF §1's shape paragraph and the script's selftest cases agree line for line. `unit-brief.md` §1 is the only copy of the replaced-sections list: no agent file names the replaced steps or rows (`command grep -nE 'steps 2, 4, 5|Completeness vs plan.{0,40}Coverage' plugins/docs-workflows/agents/*.md` prints nothing).
- [ ] **Step 2: The design's D13 note.** Append under D13 a dated note giving R1's shape as built, without rewriting the approved text.
- [ ] **Step 3: Forward references**, each now true: Tasks 3 and 4's.
- [ ] **Step 4: No regression (D15).** Trace one keyed and one direct `/document` run through `doc-writer` and `doc-reviewer`: no path into `unit-brief.md`. List every hunk of `git diff origin/main...HEAD -- plugins/docs-workflows/agents plugins/workflows-core/references` with the condition under which it acts; one that changes `/document`'s behaviour beyond D9's carve-out is a defect.
- [ ] **Step 5: Fail-closed, end to end:** RF6, T-REFNAME, T-ART, T-CLONE, a forged `kind: artifact` entry naming `security/x/register.md`, and a `doc-location-finder` path with `..`.
- [ ] **Step 6: GIT-G1 audit.** `git diff origin/main...HEAD --stat` shows nothing under `phase-handoff.md`, its parts, `specs-git.py` and its modules, the `specs-git` skill or `workflows-core-handoff.md`; `.github/` holds C1 alone or nothing (Q1); `specs-repo-git.md`'s diff is E3 exactly; `workflows-core-git.md`'s is E1 and E2 exactly; `workflows-core-read-only.md`'s is R26's two edits exactly.
- [ ] **Step 7: The sweeps, closed.** Every before/after count of Tasks 3, 5 and 7 equals its intended value; the probe once more.
- [ ] **Step 8: The full CI list**: every step `.github/workflows/validate-catalog.yml` runs, in order, each `--selftest` and the mermaid gate where `node` exists.
- [ ] **Step 9: The PR text**, for the controller: E1–E3 with their approval, C1 with Q1's answer, R26's two edits; the new command's GIT-G1-shaped sections for the GIT-G1 owner; R1's departure; R7, R20 and R3 as limits; the fixtures built as traces; the versions; the attribution lines the session gives for pull requests.
- [ ] **Step 10: The whole-branch review** is the controller's: Fable against the design and this plan.

# DOC-D-G1 sub-project 1 — `/docs-workflows:docs-write` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/docs-workflows:docs-write <unit-id>|--next|--batch <n>` turns a documentation backlog unit into a reviewed, visibly-unverified page on a branch of the docs repository, with its navigation and its unit's move `missing → drafted` in the same commit, and lays down the contracts `/docs-verify` and `/docs-capture` will share.

**Architecture:**
- One new command with its own phases (D4, D5), dispatching the agents `/document` already dispatches. Every difference a backlog run makes to `doc-writer` and `doc-reviewer` lives in one new reference, `references/docs-iteration/unit-brief.md`; each agent gains one pointer sentence and nothing else of behaviour.
- One new stdlib script, `scripts/backlog-lines.py`, is the design's single line reader (D13): the shape test, the duplicate-id check, the unmerged-branch read (D7) and the two-key targeted edit (D8). No other step reads a backlog line by line.
- The docs-repository discipline every backlog run shares is a new section of `finish-and-handoff.md` (D10); navigation regeneration is a new entry point of `scaffold-tree.md` §4 (D9); `/docs-write`'s gate registry is a new section of `gate-ledger.md` (D4).
- `workflows-core` takes rows and truth edits only: the cost and feedback documentation rungs, the namespace manifest, `branch-naming`'s row and slug, `doc-structure-conventions` §1's carve-out, the attachment, not-pipeline and stash rules that name each caller, the consumer lists, and the approved GIT-G1 edits.

**Tech Stack:** markdown prose that agents execute; one Python 3 stdlib script with `--selftest`; generated reference parts (`python3 scripts/reference-parts.py generate`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-17-doc-d-g1-docs-iteration-design.md`, revision 3, approved 2026-11-17. Cited as *D1*…*D17*; its abbreviations (BF, EC, CM, FG, ST, FH, RR, DOC, AUD, ROUTE, SRG, PH, P3) are used unchanged. A decision the design states is not repeated here. Its reviews: `.superpowers/design-review-1.md`, `design-review-2.md`. This plan's review: `.superpowers/plan-review-1.md`, cited as *C1*, *I1*…, *M1*….

**The maintainer's answers on the design** (its Status line): (1) three sub-projects, `/docs-write` first, the `stale` edges to the drift track; (2) a visible page-level unverified marker until `/docs-verify` removes it; (3) GIT-G1 edits E1–E3 approved by name, truth-only; (4) `release` units refused; (5) no specs artifact read but an `ard.md` on the default branch; (6) one consented push offer at the end of a run.

**Answers and rulings at plan review** (2026-11-17):
- **Maintainer — Q1 approved.** One step, "Self-test the backlog line reader", in `.github/workflows/validate-catalog.yml`, on the SEC-G1 precedent: GIT-G1 edit **E4**, approved by name, its text in *Exact copy*.
- **Maintainer — told with Q1:** R1's reading of D13's shape, "no value continues past the line it opens on", which corrects D13's wording that would stop every backlog `/docs-audit` writes.
- **Controller — R8:** `SKIPPED_BY_USER` is cut. Only a passing build, or `NOT_APPLICABLE` for a profile with no build command, lets a unit move: D8's "last build passing".
- **Controller — R20:** D9 as approved. Where no generated block qualifies, the page is placed by the repository's own convention, as `/document` places one; R20 says how, and it is buildable in a repository nothing scaffolded.
- **Controller — R26 stands** (`workflows-core-read-only.md` is not GIT-G1); its two truth edits are named in the pull request. **R5, R6, R7, R21 stand.**
- **Controller — Task 5 splits** into 5a (the command, its page, and what the gates force with it) and 5b (the rules files, BF §3 and E1–E3). E4 lands in Task 2, with the script it tests.

**Answers and rulings at plan review 2** (2026-11-17; `.superpowers/plan-review-2.md`, findings *N1*…*N10*):
- **Maintainer — E5 approved by name** (N2): a truth-only edit to the comment of `validate-catalog.yml`'s "Self-test the tree snapshot" step, which names `tree-snapshot.py`'s callers; `/docs-write` joins as the eighth. The comment changes and nothing else. It lands in Task 5a, with R25's call.
- **Review — R20 is D9 as approved;** "no target, nothing placed" is a logged limit. **R1's `indent` and `key` refusals are accepted as a stated limit**, on the command page and in the CHANGELOG, with the remedy. **The plan's size is justified.**
- **Controller — the phases are renumbered in run order** (N3): the design leaves numbering to the builder (*What is left to the builder*), and command prose runs in file order.

No question is open.

**Execution:** subagent-driven. Opus implements every task. **[security-sensitive]** tasks are reviewed by Fable — Task 5a in two passes, Phases 0–4 and Phases 5–14; **[mechanical]** ones by Opus. Fable reviews the whole branch at the end.

**Base:** worktree `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1`, branch `feat/doc-d-g1-docs-iteration`, `main` at `6d6518b7d` plus the design commits. Line numbers are finding aids at that base: **locate every site by its quoted phrase.**

**The GIT-G1 edits — every one, with its approval.** This track has no standing truth-edit permission.

| # | Edit | Task | Approval |
|---|---|---|---|
| E1 | `.claude/rules/workflows-core-git.md:26` — the `specs-repo-git` consumer counts | 5b | Design answer 3, by name (truth) |
| E2 | `.claude/rules/workflows-core-git.md:32` — the implementation-repository counts | 5b | Design answer 3, by name (truth) |
| E3 | `plugins/workflows-core/references/specs-repo-git.md:310` — the bookkeeping-only class gains `/docs-write` | 5b | Design answer 3, by name (truth) |
| E4 | `.github/workflows/validate-catalog.yml` — one step, "Self-test the backlog line reader" | 2 | Maintainer 2026-11-17, Q1, by name (new CI step) |
| E5 | `.github/workflows/validate-catalog.yml` — the "Self-test the tree snapshot" step's comment gains `/docs-write` among its callers | 5a | Maintainer 2026-11-17, N2, by name (truth) |

E1 and E2 together change `workflows-core-git.md` by −7 characters (19,993 → 19,986).

---

## Global Constraints

### What is not ours

- **Never edited:** `plugins/workflows-core/references/phase-handoff.md` and its `reference-parts/phase-handoff/`, `plugins/workflows-core/scripts/specs-git.py` and its two modules, the `specs-git` skill and `run-key-set.md`, `.claude/rules/workflows-core-handoff.md`. `.github/` takes E4 and E5 alone; `specs-repo-git.md` E3 alone; `workflows-core-git.md` E1 and E2 alone; `workflows-core-read-only.md` R26's two truth edits alone.
- **Left as they stand, by the design's choice:** SRG:132, SRG:314, SRG:757-762, PH:403, PH:439, PH:628's named readers. The pull request names SRG:757-762 (`/docs-write` states a no-tail refusal and is not listed; for `DOCS_WRITE_NOT_A_REPOSITORY` it uses the permission outside its stated reason, as D3 says) and PH:628 (`/docs-write` becomes a third reader there and prints the one line its rule asks for).
- **Any other GIT-G1 sentence a step finds this change makes false is reported to the controller as a question for the maintainer. It is never edited.**
- **`/docs-write`'s own GIT-G1-shaped sections** — *Ending early*, the keyless preflight, the terminal `commit-artifacts` — are new text written in `/docs-audit`'s form (AUD:18, its Phase 0 step 3, its Phase 9); the pull request names them for the GIT-G1 owner.
- **Untouched (D15):** `commands/document.md`, `doc-planner`, `/docs-init`, `/docs-brand`, `/docs-serve`, `/docs-profile`, `/release-notes`, the UserPromptSubmit hook, and the contracts of `doc-location-finder`, `docs-style-checker`, `doc-fixer` and `code-scanner`. **"Unchanged" means no contract change** (R17): a caller list in an agent's description or opening gains `/docs-write` in Task 7, as D17's known site `doc-fixer.md:3` already shows.

### What sub-projects 2 and 3 add (named, not built here)

- **Sub-project 2, `/docs-verify`:** `drafted → verified`; the `answers` input `unit-brief.md` reserves for `doc-writer` (D11); EC §4–§5's stamp key; `--prepare`; the removal of the page-level marker in the `verified` commit; its own registry section in `gate-ledger.md`.
- **Sub-project 3, `/docs-capture`:** `captured` in BF, CM and FG's lifecycle copies and in `/docs-audit` and `docs-audit-reviewer`; `/docs-write`'s `captured → drafted`, prose from the walkthrough and images placed under D9's image rules.
- Each repeats this plan's sweep for its command and agents, and re-derives E1–E3 (the design's +1 and +11).

### Repository rules

- **Prose is executed.** Every sentence an agent reads is true when it runs. A forward reference a later task makes true is named in that task's *Interfaces* and closed in Task 9.
- **`grep` here is ugrep. Every count uses `command grep`.** A sweep enumerates by subject, then counts each literal string wrap-insensitively, before and after, over refinement 4's scope: `plugins/` (every `CHANGELOG.md` included, where a hit is history and stays), `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`.
- **One noun:** *a backlog run* (D1) — a run of any of the three commands.
- **Sizes** by `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" <file>`. Plan-time: `CLAUDE.md` 35,978 (warn 36,000); `.claude/rules/docs-workflows.md` 19,998; `workflows-core-git.md` 19,993; `workflows-core.md` 19,150; `plugin-updates-coupling.md` 18,175; `docs-workflows-gates.md` 4,323. Rules files warn at 20,000. Every task that edits one measures it.
- **The command never writes `resolve-address`**, not even to say it resolves nothing: `check-branch-check` holds every command naming it to a `branch-check` request.
- **Choice arrays** are copied verbatim from *Exact copy*; 2–4 options, no "Other"; the command's **Load the question rules.** step precedes its specs preflight and its first question (P3 §4.3).
- **Every executed regex uses `[0-9]`, never `\d`.** No dash-form requirement id. **Vendor neutrality:** no tracker name. Name no organisation or outside product.
- **User pages** (`plugins/*/docs/**`, READMEs) carry no `§`, no `D<n>`, no `<plugin>:<reference>` (check 25); a table cell is at most 200 characters (check 6); a page naming `/docs-write` links its page (check 28); a command page links `docs/workflow.md` (check 26). Every claim on a page is derived from the command or reference that runs it.
- **Untrusted values** (D13): nothing read from a backlog, walkthrough, profile, ref name or page reaches a path, ref, name or command before its class test; **every value the orchestrator puts in a command is single-quoted, each `'` written `'\''`, after `--` where the command takes one** (C1); `${CLAUDE_PLUGIN_ROOT}` paths in the command and the agents; `workflows-core:` references through the loader, with check 16's preamble and, where a load-by-part reference is cited, its paragraph.
- **Commits:** `git branch --show-current` immediately before each; expected `feat/doc-d-g1-docs-iteration`. Each message ends with the committing session's attribution lines.

### Gates

One chain, from the worktree root; read the printed value:

```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/lineage.py --selftest && python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest && claude plugin validate plugins/workflows-core && claude plugin validate plugins/docs-workflows; echo "EXIT=$?"
```

Expected: `EXIT=0`; `validate-catalog` prints `0 error(s), 0 warning(s)` (the base's result); `lineage.py` prints `selftest: 62 passed`; `backlog-lines.py` prints `selftest: <n> passed` with Task 2's count (Task 1 drops that member). **Tasks 5a and 6, which edit diagrams, add** `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && node scripts/mermaid/check-mermaid.mjs --root .` where `node` exists (M6). A task editing a load-by-part reference runs `python3 scripts/reference-parts.py generate` first. `check-docs` takes about four minutes. Where `claude` is not on `PATH`, say so and leave the two `validate` calls to Task 9.

**Tests for command prose are traced runs.** No harness executes a command's prose, so the design's fixtures (*What is left to the builder*) are **scenario traces**: in the task report, the input, each deciding sentence quoted as `file:line`, the outcome, and any step no sentence decides — a defect fixed in that task. One live check goes to `to-test-on-real-project.md` (Task 8).

### Shared names (every task uses these, exactly)

- **Classes:**
  - `UNIT_ID` `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` — unit ids, walkthrough ids, slots.
  - `PAGE_PATH` `^[A-Za-z0-9_][A-Za-z0-9._/-]*\.md$`, no `.`, `..` or empty segment, plus D13's tests (R6).
  - `ARTIFACT_PATH` `^specifications/[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*/ard\.md$` (R28); a segment opening `[A-Za-z0-9_]` cannot be `.` or `..`.
  - `OBJECT_ID` `^[0-9a-f]{40}([0-9a-f]{24})?$`.
  - the branch class of `read-only-repos` §3 (`read-only-repos.md:62`), tested as it says.
- **`<top>`** the docs repository's work-tree top level; **`<base>`** its default branch's name (R23); **`<default-ref>`** and `specs_git` from the last specs `start` JSON; **`unfinished/`** is `<top>/.dev-workflows/unfinished/`.
- **The script** `${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py`, run as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog-lines.py" <sub> …`: `check --repo <top>`; `moved --repo <top> --base <name> --id <id> [--id <id> …]`; `edit --repo <top> --id <id> --status drafted [--page-path <rel>]`; `--selftest`. Interfaces in Task 2; its caller rule is R2.
- **`unit-brief.md`**: `${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/unit-brief.md`; §1 *The replaced sections*, §2 *The brief*, §3 *`doc-writer` under a unit brief*, §4 *`doc-reviewer` under a unit brief*.
- **The brief's fields** (§2): `brief_kind: unit`; `unit` (`id`, `title`, `type`, `audience`, `visibility`, `roles`); `surface` (the row, or `null`); `journey_surfaces` (a tutorial's rows); `write_targets` (the page as a new page, then each placement target, R20, as `extend-existing` with `placement_only: true`); `page_path` (absolute); `content_root`; `evidence` (the frontmatter entries, EC §2); `scanner_returns`; `artifacts` (`path`, `ref`, `text`); `walkthrough` (the file's content, or `null`); `review_by`; `repo_authoring_guidance`; `component_patterns: []`; `repo_verification_gates`; `profile`; `docs_repo_path`; `code_repos`; reviewer-only: `written_paths`, `style_check_report`, `gate_ledger`, `build_summary`, `claims_file`.
- **FH §6** *A backlog run's finish*: §6.1 *Committed before the run*, §6.2 *Adopt or cut*, §6.3 *One commit per unit*, §6.4 *A unit that does not commit*, §6.5 *Push, once*, §6.6 *The pull-request draft, printed*.
- **ST §4's entry point** **regenerate**; **`gate-ledger.md` §9** *The `/docs-write` gate registry*, appended after §8 *Hard rules* (no heading moves).
- **Gate ids:** `toolchain_preflight`, `repo_checklist`, `style_check`, `build_check`.
- **The command's phases, numbered in run order** (N3, R27): 0 Resolve, 1 Select and resolve sources, 2 Place, 3 Branch, 4 Ground, 5 Write, 6 Style, 7 Navigation and build, 8 Review, 9 Commit the unit, 10 Finish, 11 Report, 12 Session maintenance & feedback, 13 Follow-ups, 14 Session cost (then the resume pointer and `commit-artifacts`). D5's Phases 2 (Ground), 3 (Place) and 4 (Branch) are this command's 4, 2 and 3; every other number is D5's. The sections are written in this order. **Both forms:** 0, 1, 2, 3 once; then per unit Phase 3's re-check, 4, 5, 6, 7, 8, 9; then 10–14 once.

### Exact copy

Fenced blocks are the text to write, character for character; the fence is not part of it.

**The command's frontmatter `description`** (533 characters; the warning is at 600):
`Drafts one page per documentation backlog unit — a unit by id, the next actionable one, or up to ten — from the unit's evidence: the code repositories it names, read at their default branch, and an ARD on the specs default branch. Every claim the evidence does not ground is marked, and the page carries a not-yet-verified marker. Regenerates the navigation, runs the build and an Opus review, and commits the page, its navigation and the unit's move to drafted in one commit on a branch. Offers one push; never opens a pull request.`

**Signature:** `/docs-write <unit-id>|--next|--batch <n> [--docs-repo <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

**Arrays:**
- Phase 2, one unit placed by `doc-location-finder` (D5): `choices: ["Write it (Recommended)", "Enter another path (you'll be prompted)", "Cancel"]`
- Phase 2, one unit whose `page_path` is set (M1): `choices: ["Write it (Recommended)", "Cancel"]`
- Phase 2, one unit, no proposed path passes (R22): `choices: ["Enter a path (you'll be prompted)", "Cancel"]`
- Phase 2, a batch (D7): `choices: ["Write these <n> units (Recommended)", "Cancel"]`
- Phase 4, a scan's escalations, reproduced as `/docs-audit` Phase 2 step 4 reproduces them and for its reason: *Dirty working tree* `choices: ["Stash changes and retry this repo", "Skip this repo", "Cancel"]`; *Refresh blocked* on a read by ref `choices: ["Skip this repo", "Cancel"]`. The command says which lists it uses.
- FH §6.2, adopt (D10): `choices: ["Continue on <branch> (Recommended)", "Cut a new branch from <base>", "Cancel"]`
- FH §6.2, the branch name (as `/docs-init` and `/docs-brand` confirm one): `choices: ["Use proposed branch <name> (Recommended)", "Edit the name (you'll be prompted)"]`
- FH §6.2, the clean-tree check and its failed-pull lists: `/docs-init` Phase 2.5 step 2's, verbatim — `["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]`, `["Proceed from current base state (Recommended)", "Cancel"]`, and their unmarked diverged forms.
- Phase 6, violations left after the re-run (as `/document` Phase 6.4): `choices: ["Proceed to review anyway — reviewer may still PASS", "Show remaining violations and let me fix manually", "Cancel"]`
- Phase 8, a review that stayed blocked — `escalation-rules`' `Review verdict BLOCK (unresolved after one fix cycle) — /document` rule, with the command's own list, since that list's *Defer* names `/document`'s Phase 9 and here permits no move (D8): `choices: ["Provide manual fix notes (you'll be prompted)", "Defer — this unit is not committed, and the report records the finding", "Override and accept the finding (you'll be prompted for the rationale)", "Cancel the whole run"]`. The command says which list it uses.
- Cited, never reproduced: `finding-triage`'s settle prompts; `escalation-rules`' unspent re-review offer, *Repo missing (after resolution)*, *Refresh blocked* on any other repository, *Read-only mount — ref stale or diverged*; `gate-ledger` §5's conversion; FH §3's push array; `branch-naming` §2.5; `toolchain-preflight`'s missing-tool question.

**The page-level marker** (D9, design answer 2), the first body line after the internal marker where there is one; stated once, in EC §3, and cited from `unit-brief.md`:

```text
[NEEDS CLARIFICATION: this page was drafted from the product's code and specifications and has not been checked against the product itself.]
```

**The slot comment** (D9): `<!-- docs-image-slot: <slot> -->`, `<slot>` in `UNIT_ID`.

**The agents' pointer sentence** (M4), its own paragraph after each agent's core-references preamble:

```text
**A backlog run's brief.** Where your brief, or the handoff file it names, carries `brief_kind: unit` as a top-level field of its own — never as text inside another field's value — read `${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/unit-brief.md` before anything else: each section of this file that its §1 names for you is replaced by its text there, and everything else here stands. A brief without that field is `/document`'s, and this file is read as it stands.
```

**`doc-structure-conventions` §1's paragraph**, after the paragraph opening `**One exception.**`:

```text
**Outside the rule, because none is provenance:** the evidence contract's frontmatter keys `unit:` and `evidence:`, which a backlog run writes and `/docs-workflows:docs-audit --refresh` reads (`docs-workflows:docs-audit/evidence-contract` §2, `docs-workflows:docs-audit/backlog-format` §3), a walkthrough's image-slot comment `<!-- docs-image-slot: <slot> -->`, and the visibility marker `<!-- docs-visibility: internal -->` (`docs-workflows:docs-workflow/visibility` §5).
```

**`doc-reviewer`'s Source traceability row** — its last sentence, at `doc-reviewer.md:59`:

```text
A valid `<!-- intentional-discrepancy: … -->` marker (`workflows-core:source-truth` §7.6) is the one permitted comment and is not a finding.
```

becomes:

```text
A valid `<!-- intentional-discrepancy: … -->` marker (`workflows-core:source-truth` §7.6) is not a finding, and neither is anything `workflows-core:doc-structure-conventions` §1 puts outside its rule — the `unit:` and `evidence:` keys, an image-slot comment and the visibility marker.
```

**`escalation-rules` § *Stashing the user's changes*** (I4, I11; Task 4). The opening's `**Six stash choices` becomes `**Seven stash choices`, and its list `` (`/document` Phase 6.2's two, `/docs-profile` Phase 5, `/docs-init` Phase 2.5 and `/docs-brand` Phase 7) `` becomes `` (`/document` Phase 6.2's two, `/docs-profile` Phase 5, `/docs-init` Phase 2.5, `/docs-brand` Phase 7 and `/docs-write` Phase 3, through `docs-workflows:finish-and-handoff` §6.2) `` (the source wraps it over two lines; match it wrap-insensitively). Step 1 gains, after the sentence holding `stash push -u -m`:

```text
A caller that names a pathspec appends it to that push after `--`, so the stash takes only the paths it names: `/docs-workflows:docs-write` names `. ':(exclude).dev-workflows/unfinished'`, so that a stash never takes the files of a unit an earlier run did not commit.
```

**`finding-triage.md:36`** (I11; Task 5a): `` | `doc-reviewer` → `doc-fixer` (`/document`, keyed mode) | yes | `` becomes `` | `doc-reviewer` → `doc-fixer` (`/document`, keyed mode; `/docs-write`) | yes | ``.

**Printed lines:**
- Phase 0, `unfinished/` not empty: `Unfinished: <dir>[, <dir>…] under .dev-workflows/unfinished/ — files of units an earlier run did not commit; nothing reads them, and they block nothing.` A name outside `UNIT_ID` optionally followed by `-<n>` is counted, `and <k> more`, never printed.
- Phase 0, a build tool the toolchain preflight finds missing, above its question (R8): `Build: <tool> is missing — no unit can be committed without a passing build, so this run would draft pages it cannot commit.`
- Phase 4, a working-tree copy of an admitted `ard.md` that `<default-ref>` lacks (PH:628's line): `Specs: <path> is in the working tree but not on the default branch — not read.`
- FH §6.5, above the push array where `<k>` > 0 (M11): `This push also publishes <k> commit(s) on <branch> that this run did not make.`

**E1**, in `workflows-core-git.md:26`: `the thirty-five commands that write` → `the thirty-six commands that write`; `the family's thirty-eight except` → `the family's thirty-nine except`; `returns the same thirty-five:` → `returns the same thirty-six:`; ``five of `docs-workflows`'s seven`` → ``six of `docs-workflows`'s eight``. Nothing else on the line.
**E2**, in `workflows-core-git.md:32`: `eighteen of the thirty-five callers` → `nineteen of the thirty-six callers`; `ten of the thirty-five also resolve` → `ten of the thirty-six also resolve`; `Eighteen is all thirty-five minus the seventeen` → `Nineteen is all thirty-six minus the seventeen`. The "joined" sentence stands.
**E3**, in `specs-repo-git.md:310`: `` `/docs-init`, `/docs-brand`, `/docs-audit`, the four logging commands and `/diagnose-session` `` → `` `/docs-init`, `/docs-brand`, `/docs-audit`, `/docs-write`, the four logging commands and `/diagnose-session` ``.
**E4**, in `.github/workflows/validate-catalog.yml`: a new step after the step ending `run: python3 plugins/docs-workflows/scripts/key-discovery.py --selftest` and its blank line, before `- name: Self-test the bounded run`, at that file's step indent:

```yaml
      - name: Self-test the backlog line reader
        # /docs-workflows:docs-write reads and edits the documentation backlog with it, line by
        # line, since no YAML parser ships with the plugins. Its failure modes are silent: a value
        # spanning lines read as a unit entry, a status written outside its entry, and a branch
        # name from a remote reaching a git command. Fixtures and repositories are built at run time.
        run: python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest

```

**E5**, in `.github/workflows/validate-catalog.yml`, the comment of the step `- name: Self-test the tree snapshot`, its second and third lines:

```yaml
        # tree, and /ready, /conformance, /document and /epics compare two reads around their
        # maintenance agents' edits. Its failure modes are silent: an agent's edit to a path git quotes or splits goes
```

become:

```yaml
        # tree, /ready, /conformance, /document and /epics compare two reads around their
        # maintenance agents' edits, and /docs-write around its writing agents' edits. Its failure modes are silent: an agent's edit to a path git quotes or splits goes
```

Nothing else in the step, or the file, changes.

**`CLAUDE.md`, Task 1** (D17's cut, −74, then the row, +76). In the `docs-workflows` paragraph:

```text
provides seven slash commands — `/document`, `/docs-profile`, `/release-notes`, `/docs-init`, `/docs-brand`, `/docs-serve` and `/docs-audit` — plus eleven subagents
```

becomes:

```text
provides seven slash commands (`ls plugins/docs-workflows/commands`) plus eleven subagents
```

and, after the `docs-workflows-gates.md` row of the rules table:

```text
| `docs-workflows-backlog.md` | as `docs-workflows.md` | the docs backlog |
```

Later, each of equal length: Task 3 `twenty-four reference files` → `twenty-five reference files`; Task 5b `seven slash commands` → `eight slash commands`, and in the `docs-grounding.md` row `24 command files` → `25 command files` and `thirteen that resolve none` → `fourteen that resolve none`. Expected size 35,980 throughout.

### Rulings where the design is silent or leaves it to the builder

- **R1 — the line shape** (D13's wording corrected; told to the maintainer with Q1). D13 lists "a flow mapping or sequence" outside the shape, but BF §1's own sample and every backlog `/docs-audit` writes carry `roles: [customer]`, `blocked_by: []` and quoted `priority_reason` values. D13's purpose — no line inside a value can pass for an entry — holds where **every line is a whole item: no value continues past the line it opens on**. The script decodes UTF-8 strictly and splits on `\n` alone; indentation is ASCII spaces only (N9).
  - **In shape:** blank and comment lines; `key:`; `key: value`; `- value`; `- key: value`; `- key:`; a key matching `[A-Za-z_][A-Za-z0-9_-]*` directly followed by `:`; a value that is a plain scalar not opening with `|`, `>`, `&`, `*`, `!`, `%`, `@` or a backtick, a quoted scalar closed on its line (`''` inside single quotes, `\"` and `\\` inside double quotes), or a flow collection opened and closed on its line (brackets balanced outside quotes); a trailing ` # …` outside quotes, and nothing else, after a closed quote or flow collection; `---` as line 1 only; a CRLF line ending.
  - **Out of shape**, each with its `check` reason: a block scalar (`block-scalar`); an anchor, an alias, a tag (`anchor`, `alias`, `tag`); a tab (`tab`); any other C0 control, a bare CR, U+0085, U+2028 or U+2029 (`control`); bytes that are not UTF-8 (`encoding`); an unclosed quote or flow collection (`unclosed-quote`, `unclosed-flow`); text other than a comment after a closed quote or flow collection (`trailing`); a key outside the grammar, a quoted key, a `? ` key (`key`); any other line form, a plain-scalar continuation among them (`continuation`); a second top-level `units:` (`units-twice`); a `units:` whose value is neither empty nor `[]` (`units-not-block`); an entry not opening `- id: <plain scalar>`, or any other line opening `- ` at the entry indent (`entry-opener`); any key repeated at an entry's key indent, `id` and `status` included (`duplicate-key`); a line opening `- ` at column 0 anywhere in the file, a block sequence written at its key's own indent (N1), a line in the units block indented more than 0 and less than the entry indent, a line inside an entry indented less than its key indent without opening `- ` at the entry indent, or indentation holding anything but ASCII spaces (`indent`); an entry with no `status:`, or one whose value is not a plain scalar (`status`); a file above 8 MiB (`too-large`).
  - BF §1 states it, the script implements it, its selftest pins it, and Task 9 appends a dated note under D13 in the design. **A limit, accepted at plan review 2 and stated on the command page and in the CHANGELOG:** a hand-formatted backlog a YAML reader accepts may be refused, by `indent` or `key` above all; the stop names the line and the reason, and the remedy is to reformat that line or re-run `/docs-workflows:docs-audit --refresh`.
- **R2 — one reader, and its caller rule** (I2). `backlog-lines.py` does every line-wise read; the orchestrator reads the selection fields with the Read tool, as data, only after `check` passed, and compares `check`'s `units` with the number of entries its own read finds: a difference is `DOCS_WRITE_BACKLOG_UNREADABLE`, so `ok, units: 0` never passes the duplicate check on a file the orchestrator reads as holding units (N1). **`check` or `moved` exiting anything but 0, or printing anything but one JSON object, is a stop, `DOCS_WRITE_BACKLOG_UNREADABLE`, never a skip** — `moved` included, so an unmerged-branch read that cannot run never lets `--next` choose. `edit` exiting 3 or 4 ends the unit (FH §6.4); exiting 2, or unparseable, ends it and then stops the run.
- **R3 — from-state.** This release takes `missing` alone; `captured` is sub-project 3's and is still an unrecognised status (BF §3). Any other status refuses the unit, naming it.
- **R4 — a page already carrying the unit's id**, matched as `/docs-audit` matches one (I5): candidates by `git -C '<top>' grep --untracked -l -z -E -e '^unit:' -- ':(literal)<root>'` over each content root that passes D13's path test, read NUL-separated so a name git would quote comes back as it is (N7); then each candidate's frontmatter block read, its `unit:` value taken with surrounding quotes, spaces, a trailing ` # …` comment and a CR removed, and compared whole with the id; a candidate that cannot be read counts as a match. A match: `<unit-id>` stops (`DOCS_WRITE_PAGE_TAGGED`), `--next` and `--batch` skip the unit; each names `/docs-workflows:docs-audit --refresh` and each matched page whose path passes `PAGE_PATH`, others counted. Two pages carrying one id is AUD:224's no-match case; this run must not make one.
- **R5 — a clone that is `<top>`** (docs beside code): dispatched with `refresh: {switch_to_default_branch: false, pull: false, read_default_by_ref: true}` under `scan-refresh` §5's "a repository the caller dispatches with settings of its own", so no scan moves the run's branch; its report line takes `scan-refresh` §7's read-by-ref wording.
- **R6 — `PAGE_PATH`** narrows D13's path test: the path is written as a plain YAML scalar, a pathspec and a command word. A proposal outside it is passed over; a typed one is refused and asked again. **A limit, stated in the CHANGELOG and on the command page:** a content root or page name holding a space or a non-ASCII character is refused.
- **R7 — an internal unit** is refused where no `builds[]` entry has `visibility: internal` (a `--public-only` scaffold, a profile with no `builds[]`): no build keeps it out of the public site. The internal tree is `<content root>/internal/` (`visibility.md` §1); BF §7's pair is tested against it.
- **R8 — the build and the move.** `build_check` permits the move only at `RAN` with every build passing, or at `NOT_APPLICABLE` where the profile records no build command at any of `render-verification.md` §1's three levels. A content failure gets one `doc-fixer` pass with the build output, as `/document` Phase 6.5 Step 1 hands it, and one re-run; a build still failing ends the unit, with no question. An environmental failure takes `gate-ledger` §5's conversion; its *Proceed without this check* records `SKIPPED_BY_USER` and ends the unit, which the question's text says. Phase 0's printed line says it before anything is written.
- **R9 — one ledger per unit**; the run's `toolchain_preflight` row is copied into each. `source_truth_verification`, `render_smoke_check` and `image_review` never appear in it.
- **R10 — the commit message.** Subject `docs: draft <unit-id> (<type>, <audience>)`; where `profile.commit_convention` holds `<summary>` and no other placeholder, that form with `<summary>` = `draft <unit-id> (<type>, <audience>)`; any other placeholder (`<KEY>` among them) falls back to `docs:`, and the report says so. Body: `Unit: <unit-id>` and `Page: <page path>`. No backlog free text enters it; `type` and `audience` are tested against CM §3's vocabulary first.
- **R11 — the branch.** Slug `docs-write-<id>` (one unit) or `docs-write-<first id>-and-<n−1>-more` (a batch), each id lowercased with every character outside `a-z`, `0-9`, `-` dropped (`branch-naming` §1.3); prefix fallback `docs/`; a `branch_naming.pattern` filled as `/docs-brand` Phase 7 step 1 fills it, its issue segment the pattern's documented no-issue literal. The proposed and the typed name are held to the branch class before any command names them (M10). A unit id never fills a key placeholder (D13).
- **R12 — cost labels** `documenting`/`dev`, `/document`'s phase: a backlog run writes product documentation, and no new phase reaches `roles-and-phases`.
- **R13 — restoring.** Before its first edit of a file for a unit — each placement target before Phase 5, each config before Phase 7, the backlog before Phase 9 — the run copies it into its scratch directory (`command mktemp -d -t dw-docs-write-XXXXXX`, `workflows-core:run-flags` §7) and restores it with `command cp --`; a file it created is moved, never deleted (D8).
- **R14 — a Cancel against a unit-level end.** A unit-level end — a build still failing or skipped, *Defer*, *Keep the verdict* on a non-`BLOCK` review, a `doc-writer` return of `BLOCKED`, a dispatched agent that fails or returns nothing usable (N5), a refused commit, R15, R25, `edit` exit 3 or 4 — runs FH §6.4 and ends the batch; Phase 10 then offers the push where a unit committed. Any *Cancel* after Phase 3 runs FH §6.4 for the unit in hand, then the stop route: no push offer, the report naming the branch and each unit committed on it.
- **R15 — the ignore test** (ST §7) matching any path of a unit's commit ends the unit (FH §6.4): never a force-add, never a partial commit; the report names the path and the line.
- **R16 — profile commands and configs** (M12). A `builds[]` or lint command holding a line break or other control character is refused before the consent (`DOCS_WRITE_PROFILE_COMMAND`); each `builds[].config` passes D13's path test inside `<top>`, else the same stop. The consent shows the commands verbatim in one fenced block, and lists the configs.
- **R17 — "unchanged" (D4, D15)** is read as no contract change: caller lists in agent descriptions and openings gain `/docs-write` (Task 7).
- **R18 — one scan round.** `classification` §8.5's seeded second round is not adopted; at most four `code-scanner` dispatches per response, the rest in the next.
- **R19 — evidence.** A surface's `evidence[]`; a `surface: null` unit's own `evidence[]`, plus, for a tutorial, each `journey` surface's `evidence[]` in journey order; each entry sorted by D13 before anything is read. A code evidence path goes to `code-scanner` as data; any command the orchestrator itself runs on one single-quotes it (C1).
- **R20 — placement where no generated block qualifies** (D9, as approved). The page is placed as `/document` places one: its planner starts the page's inbound links from `doc-location-finder`'s `linked_from` and extends them with the repository's sidebar and nav files, and an agent adds the entry. Here the **placement targets** are each `linked_from` path of the chosen target, and each config a `builds[]` entry names that holds a `nav:` key, where it is an existing regular file inside `<top>` that passes D13's path test and is a `.md` under a content root, such a config, or, where the profile records no `builds[]`, a `.yml` or `.yaml` file at `<top>`'s root holding a top-level `nav:` key (N4). They are listed in the consent, saved (R13), and handed to `doc-writer` as `extend-existing` targets with `placement_only: true`: it adds the page's entry in the form the file's sibling entries take, and changes nothing else (`unit-brief.md` §3). `doc-reviewer`'s Structural integrity row, which stands, checks the entries. With no placement target, the run places nothing, and the report says the repository's own navigation decides. Where **regenerate** applies, there is no placement target.
- **R21 — the carve-out names the visibility marker too** (*Exact copy*): `doc-reviewer`'s row calls the discrepancy marker "the one permitted comment", and every internal page `/docs-write` writes carries `<!-- docs-visibility: internal -->`. The pull request names it as one clause beyond D15's one change.
- **R22 — placement of the page.** From `doc-location-finder`'s targets, the first of kind `new-page-in-existing-section` or `new-section` whose path, relative to `<top>`, passes `PAGE_PATH` and D13, names no existing file, lies in a declared content root, keeps BF §7's pair and, in a batch, differs from every other unit's page (M3). None passing: the no-path array. Phase 3's re-check tests "names no existing file" again for each unit, and that each placement target still exists (N5).
- **R23 — the base.** `read-only-repos` §3's chain, reads only, at Phase 1; where it is exhausted, the local `main`, then `master`, as FH §6.2's cut uses it; where none resolves, `--next` and `--batch` stop (`DOCS_WRITE_NO_BASE`, naming `<unit-id>` as the way on), since no unmerged-branch read can be made.
- **R24 — the authoring guidance.** `unit-brief.md` §2 says how the orchestrator fills `repo_authoring_guidance` (the files and rule kinds `doc-planner`'s guidance scan names, in its own words) and `repo_verification_gates` (`repo-verification-gates.md` §2–§4, whose §5 gains `/docs-write` beside direct mode).
- **R25 — what the writing agents touch** (I10). Immediately before each `doc-writer` and `doc-fixer` dispatch, the run takes a tree read of `<top>` and, where the session's working directory is inside a git work tree whose top level neither is `<top>` nor lies inside it, of that work tree (N6), through `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tree-snapshot.py" snapshot`, each into a `command mktemp -t dw-docs-write-snap-XXXXXX` file; after the dispatch it reads again and runs `tree-snapshot.py compare`. Any path changed or created but the unit's page and its placement targets ends the unit (FH §6.4), the report naming each path; a read or compare that fails ends it too. The agent's own `files_written` or Fix Report is the second test.
- **R26 — `.claude/rules/workflows-core-read-only.md` is not a GIT-G1 file** (confirmed at plan review). Split out on 2026-10-08, edited since by fix batch B40 and the scan-refresh track, on no GIT-G1 never-edit list. The command makes two of its sentences incomplete — "The nine commands that … name `prep.read_only`" (ten) and the commands that "cite §3 for the default branch each resolves before cutting a branch in a docs repository" (`/docs-write` joins). Task 7 makes both true; the pull request names them for the GIT-G1 owner.
- **R27 — one order, both forms** (I6, N3). The scan (this command's Phase 4, D5's Phase 2) runs after Phase 3's re-check for one unit as for a batch, so no clone is scanned before the consent that admits it (D13), and no scan runs before the run stands on its own branch. The phases are numbered in that order (*Shared names*); Phase 2's consent lists what Phase 1 resolved.
- **R28 — the artifact path** (C1). An artifact entry's path passes `ARTIFACT_PATH` before anything uses it, else the unit is refused naming it; the read is `git -C "$SPECS_PATH" show '<default-ref>:./<path>'`, the whole object name single-quoted, `'` written `'\''`.
- **R29 — the walkthrough** (I9). A unit whose `walkthrough` is set: the id passes `UNIT_ID`, matches whole a `<id>.yml` in the listing of `<top>/.dev-workflows/walkthroughs/`, is a regular file by `lstat` and at most 1 MiB; else the unit is refused naming the id. A `captures[].slot` outside `UNIT_ID` is reported and gets no slot comment (D13). The file is data, its `result:` values ignored.
- **R30 — the profile across the branch step** (I3). FH §6.1 holds `.dev-workflows/docs-profile.yml` to the backlog's test: tracked and clean before the run, so neither a *Stash* nor a switch changes what Phase 0 read. Phase 3's re-check reads the profile again on the run's branch and stops (`DOCS_WRITE_PROFILE_CHANGED`) where its build or lint commands, content roots or `builds[]` configs differ from what the consent showed. Phase 7 runs the command strings the consent showed.
- **R31 — the markers are not style** (M13). The `docs-style-checker` and `doc-fixer` briefs say that a `[NEEDS CLARIFICATION: …]` marker, the page-level one included, the slot comment and the visibility marker are never reported, reworded or removed by the style pass.

## Review Focus

Inputs a reasonable operator will meet that no gate exercises, most likely first. Each has its test in the owning task.

| # | Input | Expected | Test |
|---|---|---|---|
| RF1 | The backlog `/docs-audit` just wrote: `roles: [customer]`, `blocked_by: []`, quoted `priority_reason`, trailing `# …` | `check` passes; the run proceeds | Task 2 `bf_sample_in_shape` |
| RF2 | The profile `/docs-audit` left with an uncommitted `source_repos[]` | A stop naming the commit to make, before any write | Task 5a T-PROF |
| RF3 | A docs site under `site/` in a code repository among the unit's sources | Read by ref; the run's branch never moves | Task 5a T-R5 |
| RF4 | A page a person tagged `unit: "U-007"` while the backlog says `missing` | `<unit-id>` stops naming the page and `--refresh`; `--next` skips it | Task 5a T-R4 |
| RF5 | A profile whose `branch_naming.pattern` and `commit_convention` hold `<KEY>` | No-issue literal; `docs:` fallback; the unit id fills no key | Task 5a T-R10 |
| RF6 | `--batch 3`, unit 2 cancelled at its review escalation | Unit 1 committed and named; unit 2 under `unfinished/`, `unit:` gone, nav and backlog restored; no push offer | Task 5a T-B1, T-R14 |
| RF7 | A hand-edited `priority_reason: |` block holding `  - id: U-002` | `DOCS_WRITE_BACKLOG_SHAPE` naming the line; nothing written | Task 2 `block_scalar_out`; 5a T-SHAPE |
| RF8 | An evidence path `specifications/$(id)/ard.md` | Refused by `ARTIFACT_PATH`; never in a command | Task 5a T-ARTQ |
| RF9 | A remote branch named `x$(id)` holding a moved backlog | Counted, never printed or interpolated | Task 2 `ref_name_outside_class` |

---

### Task 1: Room — the backlog rules file and `CLAUDE.md`'s cut [mechanical]

**Files:**
- Create `.claude/rules/docs-workflows-backlog.md` (`paths:` identical to `docs-workflows.md`'s four globs): heading `` # docs-workflows — the docs backlog: `/docs-audit` and the backlog runs `` (fix round 1, M1), an opening in `docs-workflows-gates.md`'s form, `## Workflow map` holding the lines moved.
- Modify `.claude/rules/docs-workflows.md`: move out the `/docs-audit` map line (:38, 1,480 with its newline) and the caller lines of `docs-auditor`, `ia-planner`, `docs-audit-reviewer` (:45-47, 253); the "Split out" paragraph (:13) gains `` `/docs-audit`'s map line, its three agents' caller lines and the backlog runs' map lines and invariants → `.claude/rules/docs-workflows-backlog.md` ``; the map section's opening (:31) names that file for them.
- Modify `CLAUDE.md`: Task 1's two edits in *Exact copy*.

**Interfaces:** produces the file Tasks 2–5b write into. Task 2 adds `## Invariants`.

- [ ] **Step 1: Move**, byte for byte. `git diff --stat` shows three files.
- [ ] **Step 2: Measure.** `docs-workflows.md` ≈ 18,400; the new file under 4,000; `CLAUDE.md` 35,980.
- [ ] **Step 3: Gates**, without the `backlog-lines.py` member; `validate-catalog` reports the new globs live. **Step 4: Commit:** `chore(doc-d-g1): the backlog runs' rules file, and room in CLAUDE.md`.

### Task 2: The line reader, and E4 [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/scripts/backlog-lines.py` (stdlib only, docstring in `key-discovery.py`'s form).
- Modify `plugins/docs-workflows/references/docs-audit/backlog-format.md` §1: a paragraph `**The line shape a backlog run reads.**` stating R1 whole and naming the script as its one implementer.
- Modify `.github/workflows/validate-catalog.yml`: **E4**, verbatim from *Exact copy*.
- Modify `.claude/rules/docs-workflows-backlog.md`: `## Invariants`, entry 1 — BF §1's line shape and `backlog-lines.py` change in one commit, the selftest pinning the script to the paragraph.

**Interfaces** (Task 5a calls these exactly). Every subcommand prints one JSON document. Exit 0 = ran, the answer in the JSON; 2 = could not run, or an argument outside its class, or `<top>/.dev-workflows` not a real directory or the backlog not a regular file by `lstat` (cause on stderr); 3 = `edit` refused on the file's content before writing; 4 = `edit` undone. The file is always `<top>/.dev-workflows/docs-backlog.yml`. Git runs as an argument list, never a shell, with a 30-second timeout.
- `check --repo <top>` → `{"shape": "ok", "schema_version": "<digits>"|null, "units": <n>, "duplicates": [<id>…], "duplicates_outside_class": <n>, "ids_outside_class": <n>}` or `{"shape": "out", "line": <n>, "reason": "<R1's word>"}`. Only ids in `UNIT_ID` are printed (M7).
- `moved --repo <top> --base <name> --id <id> …` → class-tests `--base` and each `--id` (exit 2); resolves `origin/<base>`, else `refs/heads/<base>`, else exit 2; reads HEAD's branch itself; lists `for-each-ref --sort=-committerdate --format='%(objectname) %(refname:short)' refs/heads refs/remotes/origin`; drops `origin/HEAD`, HEAD's branch, `<base>`, `origin/<base>`, and every name outside the branch class (counted); examines at most the 60 newest remaining refs, each object id tested against `OBJECT_ID`, keeping one not merged into the base whose backlog differs from the merge base's; reads the first 20 kept by object id with `cat-file`, at most 1 MiB each; compares each `--id`'s status there with its status in the working file (M9). → `{"moved": {<id>: [<ref>…]}, "unreadable": [<ref>…], "read": <n>, "more": <n>, "names_outside_class": <n>}`, `more` counting every ref past the point it stopped. An entry absent on a ref, or a ref with no backlog, is not moved; a blob over 1 MiB, out of shape, holding the id twice or its status outside `^[a-z][a-z-]{0,31}$` is `unreadable`.
- `edit --repo <top> --id <id> --status <s> [--page-path <rel>]` → exit 2 on an `--id`, a `--status` (`^[a-z][a-z-]{0,31}$`) or a `--page-path` (`PAGE_PATH`) outside its class; exit 3, file untouched, on a file out of shape, an absent or duplicated id, an entry with no `page_path:` line where `--page-path` is given, or a `page_path` already set to another path (`null`, `~` and an empty value count as unset, M8); otherwise replaces the `status:` value and, where given and unset, the `page_path` value, keeping indent, key, any trailing comment and every other byte; writes atomically; runs `git -C <top> diff -U0 --no-color --no-ext-diff --no-textconv -- .dev-workflows/docs-backlog.yml` and holds every hunk to the one or two lines it changed, inside the entry, else writes back the bytes it read and exits 4. → `{"first": <n>, "last": <n>, "changed": [<n>…]}`.
- `--selftest` → `selftest: <n> passed`, exit 0; fixtures and git repositories built at run time.

- [ ] **Step 1: The failing selftest.** The script with argument parsing, stubs, and these cases, each name then its assertion:
  - `bf_sample_in_shape`: BF §1's sample, verbatim → `ok`, `units: 1`, `schema_version: "1"`. `crlf_ok`: the same with CRLF endings → `ok`.
  - `quoted_scalars_in`: values `'it''s'`, `"a \" b"`, `"ends \\"` → `ok`.
  - `block_scalar_out`: `priority_reason: |` holding `  - id: U-002` → `out`, its line, `block-scalar`.
  - `quoted_multiline_out`, `flow_multiline_out`, `continuation_out` → `unclosed-quote`, `unclosed-flow`, `continuation`.
  - `anchor_alias_tag_tab_out`: four files → `anchor`, `alias`, `tag`, `tab`.
  - `control_out`: a bare CR, U+2028, U+0085, a VT → `control` each. `encoding_out`: a Latin-1 byte → `encoding`.
  - `key_out`: `"status": drafted` beside `status: missing`; `status : x`; `? x` → `key` each.
  - `second_id_out`: an entry holding `id:` twice → `duplicate-key`. `duplicate_status_out` → `duplicate-key`.
  - `column0_entries_out`: `units:` followed by `- id: U-001` at column 0 (N1) → `indent`. `nbsp_indent_out`: an entry key indented with U+00A0 → `indent`.
  - `trailing_text_out`: `title: "a" b` and `roles: [a] b` → `trailing` each.
  - `status_missing_out` → `status`; `status_flow_out`: `status: [missing]` → `status`. `entry_indent_non_id_out`: `- title: x` at the entry indent → `entry-opener`. `too_large_out`: a file above 8 MiB → `too-large`.
  - `units_twice_out` → `units-twice`. `units_flow_out` / `units_empty_ok`: `units: [{id: U-1}]` → `units-not-block`; `units: []` → `ok`, `units: 0`.
  - `under_indent_out`: a line at indent 1 under `units:` with entries at 2; a key at the entry's indent + 1 → `indent` each.
  - `id_quoted_out`: `- id: "U-001"` → `entry-opener`.
  - `duplicate_id`: two entries `U-001` → `duplicates: ["U-001"]`; an id `x y` → `ids_outside_class: 1`.
  - `symlink_refused`: the backlog a symlink; `.dev-workflows` a symlink → exit 2 each, nothing read.
  - `moved_on_branch`: branch `feat/a` moved `U-001` to `drafted`, `main` did not → `moved: {"U-001": ["feat/a"]}`; merged into `main` → nothing.
  - `ref_name_outside_class`: a branch `x$(id)` holding a moved backlog → `names_outside_class: 1`, its name in no output.
  - `ref_unreadable`: an out-of-shape blob and a 1.1 MiB blob → both `unreadable`. `absent_not_moved`: a ref with no backlog → not moved.
  - `twenty_cap`: 22 qualifying refs → `read: 20`, `more: 2`. `examined_cap`: 70 in-class refs, none qualifying → `read: 0`, `more: 10`.
  - `no_base`: `--base main` where neither `origin/main` nor `main` exists → exit 2.
  - `edit_two_keys`: `status` and a `null` `page_path` changed, every other byte equal, CRLF kept, the diff inside the entry. `edit_tilde_null`: `page_path: ~` → set.
  - `edit_page_path_set` → exit 3, file byte-equal. `edit_no_page_path_key` → exit 3.
  - `edit_undo`: a backlog already dirty on another line → exit 4, file byte-equal to what it read.
  - `bad_args`: `--base 'a;b'`, `--id '../x'`, `--status 'Drafted!'`, `--page-path 'a/../b.md'` → exit 2, nothing read or written.
  Run `python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest`. Expected: FAIL naming the first case.
- [ ] **Step 2: Implement** the three subcommands to the interfaces. The grammar is R1's; an entry spans from its opener to the line before the next line at its indent opening `- ` or the next column-0 line.
- [ ] **Step 3: Run the selftest.** Expected: `selftest: <n> passed` (≥ 37 cases), exit 0. Record `<n>`.
- [ ] **Step 4: BF §1's paragraph, the invariant, E4.** `git diff -- .github/` shows E4's lines and nothing else.
- [ ] **Step 5: Gates. Step 6: Commit:** `feat(doc-d-g1): backlog-lines.py — the one line reader of the documentation backlog, and its CI step`.

### Task 3: The unit brief, and the two agents [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/references/docs-iteration/unit-brief.md`, with the core-references preamble (check 16) for its `workflows-core:` citations.
- Modify `agents/doc-writer.md`, `agents/doc-reviewer.md`: the pointer sentence; each description and opening (`doc-writer.md:3`, :9; `doc-reviewer.md:3`, :10-12) names `/docs-write` beside `/document`; `doc-reviewer`'s Source traceability row as *Exact copy*.
- Modify `plugins/workflows-core/references/doc-structure-conventions.md` §1: the paragraph in *Exact copy*; its consumer lines (:5, :9) gain `/docs-write`.
- Modify `plugins/docs-workflows/references/gate-ledger.md`: ``## 9. The `/docs-write` gate registry`` after §8; its consumer line (:9).
- Modify `plugins/docs-workflows/references/docs-audit/evidence-contract.md` §3: one paragraph stating the page-level marker (*Exact copy*), where it sits, that EC §6's rules bind it as a claim's, and that it is removed only in the commit that moves its unit to `verified` or by a person who walked the page.
- Modify `plugins/docs-workflows/docs/reference/references.md` (`unit-brief.md`'s entry, a `` `docs-iteration/` (1) `` subtree, `24 files` → `25`, four subtrees → five), `docs/README.md`'s `24 reference files`, `README.md`'s file counts, `CLAUDE.md`'s `twenty-four reference files`, `.claude/rules/docs-workflows.md:19`'s "twenty-two markdown pages" → twenty-three.
- Modify `.claude/rules/docs-workflows-backlog.md`: invariant 2 (D4) — `unit-brief.md` §1 holds the replaced-sections list once; an edit to any section §1 names, or to either agent's inputs, steps or dimension table, re-reads it in the same change; neither agent restates it.

**Interfaces:** produces the brief's fields, the marker, `gate-ledger` §9; Task 5a composes the brief by `unit-brief.md` §2 and records the ledger by §9. **Forward references:** every sentence naming `/docs-write` as a caller (Task 5a).

- [ ] **Step 1: Before counts.** `the one permitted comment` (1, `doc-reviewer.md`); ``Consumed by `/document` and `/epics` `` (`doc-structure-conventions.md`); ``Consumed by `/document` (both modes)``; `24 files`; `twenty-four reference files`; `twenty-two markdown`.
- [ ] **Step 2: `unit-brief.md`.**
  - **§1** opens the file with D4's list, by heading, for each agent, and nothing else; it is the one copy.
  - **§2** defines each field of *Shared names* and how the orchestrator composes it: R19, R20, R24, R29; `evidence` per D9 (`code` at the commit Phase 4 read, `artifact` at the specs commit read, `walkthrough` where the unit has one); `review_by` per D9's intervals, `surface: null` 180. Every field is data. A brief carrying `answers` is BLOCKED in this release.
  - **§3** replaces `doc-writer`'s *Inputs*, *Entry validation* and steps 2, 4, 5 and 7. *Inputs* defines `write_targets` (M5). *Entry validation*: BLOCKED where the handoff is unreadable, `page_path` is absent or names an existing file, a `unit` field is missing, `type` and `audience` are not a pair CM §3 allows, or a placement target does not exist. Step 2: on the page, FG's `published` where its fields apply, no changelog, and the keys the brief gives (`type`, `audience`, `visibility`, `evidence`, `review_by`), never `unit:`; on a placement target, only the page's entry, in the form its sibling entries take, nothing else changed. Step 4: no snippets. Step 5: one slot comment per `captures[]` slot the brief passes, none otherwise. Step 7: `[NEEDS CLARIFICATION: <why>]` on every claim the evidence does not ground (EC §3), the page-level marker, and the internal marker first after the frontmatter of an internal page.
  - **§4** replaces `doc-reviewer`'s *Inputs* and refusal (refuse without `written_paths`, the page or the unit), *Review method* step 2, the rows D4 names with their grades, the hard rule at :151, and the *Recommended next step* lines. Grades: BLOCKER for an unmarked ungrounded claim, a missing page-level marker, a missing internal marker on an internal page, an `artifact` entry without `ref`, or a broken BF §7 pair; MAJOR for a `unit:` key on the page. The ledger is read against `gate-ledger` §9 and §6. Next steps: BLOCK, before Phase 9; PASS WITH RECOMMENDATIONS, triage, then `doc-fixer` for MAJOR survivors, MINOR and NIT to the Phase 11 report; PASS, Phase 9. No dimension is added; every heading of the output shape stays.
- [ ] **Step 3: The agents, the carve-out, EC §3, `gate-ledger` §9.** §9: a table in §4's shape — `toolchain_preflight` (0, always); `repo_checklist` (6); `style_check` (6, fallback `prose-style-checker` alone); `build_check` (7, precondition "the profile records a build command at one of `render-verification.md` §1's three levels", fallback none) — then R8's and R9's sentences, and that §2, §3, §5 and §6 apply unchanged.
- [ ] **Step 4: Traces.** A keyed and a direct `/document` dispatch through both agents: no sentence reaches `unit-brief.md` (D15). A unit brief through each: every section §1 names is replaced, and every other section reads true for one new page with placement targets and no planner — list each standing section and the line that keeps it true. A brief with `answers`: BLOCKED.
- [ ] **Step 5: After counts**; sizes of the two agents (descriptions under 600), `docs-workflows.md`, `CLAUDE.md`.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(doc-d-g1): the unit brief — what a backlog run changes for doc-writer and doc-reviewer, and its gate registry`.

### Task 4: The finish, the navigation and the stash [security-sensitive]

**Files:**
- Modify `plugins/docs-workflows/references/finish-and-handoff.md`: its title and opening name §6; new `## 6. A backlog run's finish`.
- Modify `plugins/docs-workflows/references/docs-workflow/scaffold-tree.md` §4: the **regenerate** entry point; the entry-point list (:7) gains it.
- Modify `plugins/docs-workflows/references/repo-verification-gates.md` §5 and its consumer line: a `/docs-write` bullet beside direct mode.
- Modify `plugins/workflows-core/references/escalation-rules.md` § *Stashing the user's changes*: *Exact copy*'s two edits and its clause (I4, I11); regenerate its parts.
- Modify `.claude/rules/docs-workflows-backlog.md`: invariant 3 (D8: a unit moves only in its commit; `unit:` written only at Phase 9; a page that never reached it carries no id) and invariant 4 (D10: one consented push, the draft printed only, no pull request opened, nothing written into a source repository or as a specs deliverable).

**Interfaces:** produces FH §6.1–§6.6 and **regenerate**, cited by name from Task 5a's Phases 0, 3, 7, 9 and 10. **Forward references:** "the backlog runs", `/docs-write` and R11's slug (closed by Task 5a).

- [ ] **Step 1: FH §6**, cited by all three backlog runs:
  - **§6.1** `git -C '<top>' status --porcelain -z -- .dev-workflows/docs-backlog.yml .dev-workflows/docs-profile.yml` prints nothing, and `git -C '<top>' ls-files --error-unmatch -- <each>` exits 0 for both (D10, R30); else the stop names the file and the commit to make.
  - **§6.2** once per run: HEAD's branch, class-tested; on `<base>`, detached, or outside the class, cut; on another branch in the class, the adopt array. The clean-tree check runs either way: `/docs-init` Phase 2.5 step 2's question and lists, verbatim, its read `git -C '<top>' status --porcelain -- . ':(exclude).dev-workflows/unfinished'`, each dirty path named; a *Stash* runs `escalation-rules` § *Stashing the user's changes* with the pathspec `. ':(exclude).dev-workflows/unfinished'` (I4). Cutting copies that step's base resolution, switch, pull, diverged-base and failed-switch handling in FH's own words, with R23's base, R11's name and its confirmation array. Stacked units make one pull request.
  - **§6.3** ST §7's commit-time ignore test over every path of the unit (R15), then `git -C '<top>' add -- <paths>`, `git -C '<top>' commit -F '<msg>' -- ':(literal)<path>' …`, the index brought back in step as §2 does; the message per R10, through a `command mktemp -t dw-docs-msg-XXXXXX` file removed afterwards.
  - **§6.4** D8's sequence: remove a `unit:` line the run wrote; move each file the run created for the unit under `unfinished/<unit-id>/`, else the first free `<unit-id>-<n>/` from 2, relative layout kept, by `command mkdir -p --` and `command mv --`, never overwriting; restore each file it edited from its saved copy (R13), placement targets, configs and the backlog alike; nothing deleted, nothing stashed, no `.gitignore` edited; the run names the directory.
  - **§6.5** FH §3's array and rules, offered once after the last unit, only where this run committed a unit and HEAD is still on the run's branch; above it *Exact copy*'s line, `<k>` being `git -C '<top>' rev-list --count '<upstream>..HEAD'` less the run's own commits, `<upstream>` `origin/<branch>` where it exists, else the base's ref (M11).
  - **§6.6** D10's facts, printed only: units moved and their pages, placement targets edited, verdicts and triage lines, build results, markers left (per page: claims marked, and the page-level marker), deferred items, paths left unstaged, `unfinished/` directories; no file, no host footer.
- [ ] **Step 2: ST §4 regenerate.** It applies only where every config a `builds[]` entry names holds a comment line beginning `# generated:` directly under its `nav:` key (one config under `--public-only`). It reads the pages the commit will hold — `git -C '<top>' ls-files -z` under the content root plus the pages the commit adds, `.md` only, `_snippets/` excluded, `internal/` excluded from the public config. It sorts each section by `order`, then `title`, a page with no `order:` last. A section keeps the label the block gives it, else its index page's `title`. It rewrites the block from `nav:` to the next top-level key, keeping the two comment lines, and never branches on `generator`. Where it does not apply, D9's placement (R20). The paragraph opening `**Until that command ships**` is Task 7's.
- [ ] **Step 3: Traces** against the text alone: a scaffolded repository; `--public-only`; a non-scaffolded repository with a hand `nav:` and a `linked_from` index page (R20); an adopted branch with a dirty nav config (*Proceed anyway*, then FH §6.4 restores that content); a *Stash* with an `unfinished/` directory present (it stays); a second failure of one unit (`<unit-id>-2/`); a commit a hook refuses (no `unit:` left, backlog restored).
- [ ] **Step 4: Measure** the rules file. **Step 5: Gates. Step 6: Commit:** `feat(doc-d-g1): a backlog run's finish (FH §6), nav regeneration (ST §4) and the stash's pathspec`.

### Task 5a: The command [security-sensitive]

**Files:**
- Create `plugins/docs-workflows/commands/docs-write.md` (`disable-model-invocation: true`; `allowed-tools: Read Write Edit Bash Glob Grep Task Skill`; the core-references preamble; the load-by-part paragraph; check 20's relay sentence as its own paragraph, copied from `docs-audit.md:287`).
- Create `plugins/docs-workflows/docs/commands/docs-write.md`, in `docs/commands/docs-audit.md`'s sections (*Who runs it*, *Synopsis*, *What it needs*, *Phases* with a mermaid flow, *Gates*, *Outputs*, *Failure modes*, *Example*, *See also*), linking `../workflow.md` and `../docs-workflow.md`, R6's and R1's limits stated, R1's with its remedy.
- Modify, as the gates force (measured at plan review): `plugins/workflows-core/scripts/command-namespaces.json`; `cost-emission.md` §7 (the row ``| `/docs-write` | documenting | dev |``), §8's documentation branch and its paragraph at :616; `feedback-emission.md` §2's documentation branch; `branch-naming.md` §2.4 (``| `/docs-write` | `docs/` |``) and §3 (R11's slug); `next-phase-offer.md:418` (each "four" → five, `/docs-write` named with its next action, push the branch and open the pull request from the printed draft, and its target, a docs-repository branch; regenerate parts); `finding-triage.md:36` (*Exact copy*; regenerate parts); `docs-workflows/README.md` (`Seven slash commands` → `Eight`, a table row, the *Documentation workflow* paragraph's "has not shipped"); `docs/README.md` (a row, the Commands bullet, `7 slash commands` → 8); `docs/workflow.md` (a mermaid node and its edges, every label holding a bracket quoted; the collision line's list; the first `/docs-write` linked); `docs/docs-workflow.md` (its first `/docs-write` linked; the rewrite is Task 6's); `docs/reference/session-cost.md` (`Five commands` → `Six`, and its lists).
- **E5**, verbatim from *Exact copy*, with R25's call.

**Interfaces:** consumes Task 2's subcommands and R2, Task 3's brief and §9, Task 4's FH §6 and **regenerate**. Produces the behaviour every earlier forward reference names.

- [ ] **Step 1: Before counts.** E1's recipe, as `workflows-core-git.md:26` prints it, piped to `wc -l` (35); `grep -l 'workflows-core:model-routing' plugins/*/commands/*.md | wc -l` (30); the same for `workflows-core:impl-maintenance` (29), `emit-cost` (29), `prep.read_only` (9); `check-questions` (37).
- [ ] **Step 2: Phase 0 — Resolve** (D3, D5). Strip run flags; **Load the question rules.**; parse exactly one of `<unit-id>` (`UNIT_ID`), `--next`, `--batch <n>` (1–10), plus `--docs-repo <path>` with its value; any other `--` token is a stop. Pre-target stops take no tail (`DOCS_WRITE_UNKNOWN_FLAG`, `DOCS_WRITE_SELECTOR`, `DOCS_WRITE_BAD_BATCH`, a run-flag stop, the ladder's Cancel, `DOCS_WRITE_NOT_A_REPOSITORY`), and *Ending early* states that refusal in its own words (D3). `resolve-docs-repo` takes `--docs-repo` as its rung-1 token, else starts at rung 2; `<top>` is `rev-parse --show-toplevel`, else the refusal. Every later stop takes the stop route. Then `test -w '<top>'`; `specs-preflight`, keyless; the profile (absent or unreadable: `DOCS_WRITE_NO_PROFILE`, naming `/docs-workflows:docs-profile`); R16; FH §6.1 (R30); `check` (R2, its count compared), then `schema_version` from its output, not 1 a stop (M7), out of shape `DOCS_WRITE_BACKLOG_SHAPE` with the line and reason, a duplicate id a stop; the `Unfinished:` line; the toolchain preflight, its row, and R8's line; R24's two blocks; `model-routing` — MODERATE, `doc-writer` on the §2 Opus chain (§9.2), `doc-reviewer` at its pin, the rest on the §2.1 detection chain, §10 honoured.
- [ ] **Step 3: Phase 1 — Select and resolve sources** (D7, D13, D14).
  - **`<unit-id>`:** whole match against `units[].id`; then R3, `blocked_by`, R4, a `release` surface (`DOCS_WRITE_RELEASE_UNIT`, naming ST:73's manual paste), a `type`/`audience` pair CM §3 refuses, R7, R29 — each a stop naming the one thing to change.
  - **`--next`/`--batch`:** D7's candidate rule (a batch excludes `tutorial` and `how-to`); the same tests, skipping rather than stopping; R23; then `moved` over the candidates, skipping each it names and carrying `unreadable` to the consent. None left is `DOCS_WRITE_NO_CANDIDATE`, naming why each was passed over; a batch finding fewer than `<n>` takes what it found and says so.
  - **Sources:** R19, then D13's sort. Artifact entries — `kind: artifact`, or a `repo` whose `sources[]` path resolves to the real path of the environment's `$SPECS_PATH` — to R28 and D14's refusals (`$SPECS_PATH` unset, no git repository, `specs_git` blocked or misrooted). Code entries by `sources[].repo`, then `docs-profile-schema.md:100`'s order, admitted under `${REPOS_PATH:-/workspace}` or by the consent, refused at or inside `$SPECS_PATH`. An evidence path failing D13's path test refuses the unit.
- [ ] **Step 4: Phases 2, 3 and 4** (R27), sections in that order.
  - **Phase 2 — Place:** a unit whose `page_path` is set takes it where R6 and D13 pass and no file is there, without `doc-location-finder`, else `DOCS_WRITE_PAGE_PATH` naming the cause and its remedy — outside `PAGE_PATH`: edit the unit's `page_path`; an existing file: tag it with `unit:` and run `/docs-workflows:docs-audit --refresh`, or set `page_path` to `null` (M2); a batch drops the unit. Every other unit: `doc-location-finder` (repo root, a composed `feature_summary`, the profile), R22, R20's placement targets. Then the consent, its text listing the unit, each clone path, each artifact path, the page path, each placement target, the branch, each `unreadable` ref, the configs and commands per R16, with the matching array.
  - **Phase 3 — Branch:** FH §6.2; then, per unit, the re-check on the run's branch — `check` with R2's count comparison, the entry (same id, same status, `blocked_by` empty), R22's two tests, and R30's profile comparison — else `DOCS_WRITE_UNIT_CHANGED` or `DOCS_WRITE_PROFILE_CHANGED` (one unit) or the unit dropped and named (batch; a changed profile stops the run).
  - **Phase 4 — Ground:** artifacts by R28's read and the PH:628 line. `code-scanner` per clone: themes `[unit title, surface title]`, a `context` composed from type and audience, `search_hints.paths` its evidence paths, the fixed policy through `scan-refresh refresh-question` with `asks: false`, R5, R18. Every status is handled as `/docs-audit` Phase 2 step 4 handles it — its lists, its read-only mount rule, which names `prep.read_only`. *Skip this repo* leaves that repository's claims unread, so marked. Each `prep.scanned_ref` is resolved to its commit.
- [ ] **Step 5: Phases 5–9.**
  - **Phase 5:** R13, R25, then the handoff file (`command mktemp -t dw-docs-write-XXXXXX`) per `unit-brief.md` §2; `doc-writer`, its dispatch text carrying `brief_kind: unit` too (M4).
  - **Phase 6:** `docs-style-checker` with `/document` Phase 6.4's brief fields and R31's sentence; the `style_check` and `repo_checklist` rows; `doc-fixer` on violations, untriaged, under R25 and R31; one re-run; the Phase 6 array.
  - **Phase 7:** R13; **regenerate** where it applies; the consented builds (R8, R30), each recorded in the one `build_check` row.
  - **Phase 8:** `doc-reviewer` per `unit-brief.md` §4; triage by `finding-triage re-review` (the row *Exact copy* adds); `doc-fixer` on survivors with `/document` Phase 7's *Decisions* line, under R25; one fix cycle and one re-review with `claims_file`; the unspent re-review offer; the stayed-blocked array, per BLOCKER; any edit after Phase 7 re-runs Phase 7. D8's permitting outcomes are stated as a list.
  - **Phase 9:** the `unit: <id>` line last in the frontmatter; R13 for the backlog; `edit` (R2); FH §6.3; a refused commit, FH §6.4. R14 throughout. A batch then takes its next unit at Phase 3's re-check.
- [ ] **Step 6: Phases 10–14 and the invariants.**
  - **Phase 10:** FH §6.5, then §6.6.
  - **Phase 11, the report:** *Classification*, *Model Routing*, *Target*, *Selection* (each skipped candidate and why), *Sources* (per clone, `scan-refresh` §7's slot; artifacts and their commits), *Units* (per unit: page, placement targets, markers, verdict and triage line, build results, the commit or the `unfinished/` directory), *Verification gates*, *Deferred items*, *Git state*, *Pull-request draft*, *Untrusted-content notices*, and `### Next step` by `next-phase-offer not-pipeline` with no `<merge-clause>`, the omission stated as `/docs-audit` states it.
  - **Phases 12–14** as `/docs-audit` Phases 7–9: `command: /docs-write`, `key: null`, the documentation branches, `emit-cost` with `documenting`/`dev` (R12), the resume pointer's rung 2, `commit-artifacts` by `args: "specs-repo-git commit-artifacts"` last.
  - An invariants list in `/docs-audit`'s form.
- [ ] **Step 7: The page, the index entries and the core rows** listed under *Files*.
- [ ] **Step 8: Traces**, each quoting the command's deciding lines:
  - **Design fixtures:** T-N `--next` on a scaffolded repository (one commit holds page, nav and backlog; `git show --stat`); T-STOP a run stopped after Phase 5, then `--refresh` (no `unit:`, unit `missing`, AUD:224); T-MERGE the backlog move lost in a merge, then `--refresh` (`drafted`, by the page-level marker); T-B1 a `--batch 3` whose second unit fails its build (batch ends, `unfinished/`, nav restored), that unit failing again (`-2/`), and a clean-tree check that asks about neither; T-HOOK; T-DEC a `decision` unit (its ARD at `<default-ref>`, no scan of `$SPECS_PATH`); T-SHAPE (RF7); T-REF an unreadable ref in the consent; T-NOSCAF (R20); T-PUB `--public-only` and an internal unit (R7); T-UNC an uncommitted backlog; T-DUP; T-BLK; T-PP a `missing` unit with `page_path`, each of M2's causes; T-NULL; T-TUT; T-INT an internal unit in a two-build repository; T-MOVED; T-REFNAME; T-ART an artifact outside D14's set; T-CLONE a clone outside `${REPOS_PATH}`, scanned only after the consent (R27); T-REL; T-NOGIT (no tail).
  - **Plan review cases:** T-ARTQ (RF8; C1); T-NOPY, `python3` missing (R2: a stop); T-PROF (RF2, R30, and a profile changed by Phase 3's switch); T-WALK, a walkthrough id outside the listing and one a symlink (R29); T-R4 with `unit: "U-007"` and a CRLF page; T-R5; T-R6; T-R10; T-R14; T-SAMEPATH, two batch units placed on one path (M3); T-SNAP, a `doc-writer` that also edits `README.md` (R25); T-COL0, a backlog with column-0 entries (N1); T-WBLOCK, a `doc-writer` returning `BLOCKED` (N5); T-NONASCII, a tagged page with a non-ASCII name (N7).
- [ ] **Step 9: After counts.** The five recipes print 36, 31, 30, 30, 10; `check-questions` 38. Every page naming `/docs-write` links its page.
- [ ] **Step 10: Gates, with the mermaid gate. Step 11: Commit:** `feat(doc-d-g1): /docs-write — a backlog unit drafted, navigated, built, reviewed and committed in one commit`.

### Task 5b: The rules, BF §3, and E1–E3 [security-sensitive]

**Files:**
- Modify `references/docs-audit/backlog-format.md` §3: the `missing → drafted` row names `/docs-write`; :109's writer count; :122's premise rewritten (D9: a backlog run's page carries a marker until verified, so the publish edge reaches only a page a person tagged).
- Modify `.claude/rules/docs-grounding.md`: `paths:` gains the command; the bold sentence and its reasons gain `/docs-write` (an existing page is none of EC §2's three evidence kinds).
- Modify `.claude/rules/docs-workflows-backlog.md`: the `/docs-write` map line; invariant 5 (`$SPECS_PATH` is never a `code-scanner` target; the artifact set is `ard.md` at `<default-ref>` alone, held by `ARTIFACT_PATH`).
- Modify `.claude/rules/docs-workflows.md`: the caller lines of `doc-reviewer`, `doc-location-finder`, `docs-style-checker` (by phrase); :27's `24 pages` → 25 and `7 command pages` → 8.
- Modify `CLAUDE.md`: Task 5b's three edits in *Exact copy*.
- **E1, E2, E3**, verbatim from *Exact copy*, last.

**Interfaces:** consumes Task 5a's command. Its review is the GIT-G1 audit and the rules files' truth.

- [ ] **Step 1: Before counts.** ``Spec 2's `/docs-write` `` in BF; the three caller phrases; the `docs-grounding.md` row's two numbers.
- [ ] **Step 2: The edits above, then E1–E3.** Re-run E1's recipe: it prints 36 and names `docs-write.md`. Apply each verbatim.
- [ ] **Step 3: Measure** `workflows-core-git.md` (19,986), `docs-workflows.md`, the backlog rules file, `CLAUDE.md` (35,980). `git diff -- plugins/workflows-core/references/specs-repo-git.md .claude/rules/workflows-core-git.md` shows E3, E1 and E2 and nothing else.
- [ ] **Step 4: Gates. Step 5: Commit:** `feat(doc-d-g1): the backlog runs' rules, BF §3, and GIT-G1 E1–E3`.

### Task 6: The pages [mechanical]

**Files:** `plugins/docs-workflows/docs/`: `docs-workflow.md`, `workflow.md` (prose), `roles-and-phases.md`, `getting-started.md` where it lists commands, and `reference/` — `agents.md`, `references.md` (FH, ST, BF, EC, gate-ledger, repo-verification-gates entries), `docs-backlog.md` (its lifecycle diagram), `docs-evidence.md`, `model-routing.md`, `session-feedback.md`, `resume-and-checkpoints.md`, `environment.md`; `plugins/docs-workflows/README.md`; `plugins/workflows-core/docs/family-map.md` (a node, :192's bullet), `roles-and-phases.md`, `reference/agents.md`, `reference/session-feedback.md`; the repo-root `README.md` (the table's `Seven commands`, the `DOCS_PATH` write-target list). In words: no `§`, no `D<n>`, no `<plugin>:<reference>`.

- [ ] **Step 1: The route page.** Step 4's heading becomes ``### 4. Write the next unit — `/docs-write` ``: what the run selects and refuses; what the page carries (the four reserved keys, `unit:` only in the commit that moves the unit, `evidence`, `review_by`, the marked claims, the page-level marker); the navigation (regenerated, or the entries added beside their siblings); the build, the review, the one commit, the push offer and the printed draft; `unfinished/`; the by-hand procedure kept for a page written any other way. Where the page asks for the backlog's commit, it asks for the profile's too (R30, N10). The loop's opening sentence, step 4's two costs, *What helps today* and the *Later* line go. Steps 5 and 6 keep their *Later* lines; step 6 gains removing the page-level marker once every claim is walked. *What to expect* reads true.
- [ ] **Step 2: Every other page in the list**, each statement derived from the command or reference that runs it. `roles-and-phases.md`: `/docs-write` in the Dev role's runs, consumes, produces and hands over; `five cost-emitting commands reach four phases` → six; *documenting* names it.
- [ ] **Step 3: Gates, with the mermaid gate. Step 4: Commit:** `docs(doc-d-g1): the pages — /docs-write on the route and in every inventory`.

### Task 7: The sweep [mechanical]

**Files:** whatever the sweep finds false over refinement 4's scope. No GIT-G1 file; `CLAUDE.md` net-zero.

- [ ] **Step 1: The table.** For each of D17's subjects — *who writes `unit:`*; *who regenerates the navigation*; *who composes a walkthrough or renders the checklist*; *which edges have a writer*; *what is manual on the route*; *which command dispatches each agent*; *which commands consume each shared reference*; *the counts* — list every statement, its file, and whether it is now true. Known sites:
  - docs-workflows references: BF:7; EC:7, :99, :105; FG:87 (re-pointed to this design), :108; ST:5, :73, :464, :466 (pages written another way, `/document` among them, still by hand: DOCUMENT-NAV); `visibility.md:5`; RR:10; `toolchain-preflight.md:10`.
  - agents: `code-scanner.md:9`; `doc-fixer.md:3`; `doc-location-finder.md:7`; `docs-style-checker`'s description.
  - workflows-core references: `branch-naming.md:7`; `finding-triage.md`'s style-checker row; `escalation-rules.md:416-420`, :449, :463-467, :670 and :886 (each list gains `/docs-write` as it uses the rule — at :886 with its own list); `followup-emission.md:7-9` (twelve → thirteen); `cost-emission.md:3-4` (twenty-nine of thirty-one → thirty of thirty-two), :687, :907; `feedback-emission.md:3`, :237 (twenty-nine → thirty).
  - rules: `.claude/rules/workflows-core.md:30`, :38, :51-52, :59 (29 of the 38 → 30 of the 39); `workflows-core-model-routing.md:30` (Thirty → Thirty-one; six of `docs-workflows`'s seven → seven of eight; one of seven → one of eight); `workflows-core-triage.md:14`; `docs-workflows-gates.md:15`, :17, :19; `docs-workflows.md`'s fixed-policy bullet, by its phrase "which `/docs-audit` takes" (M14); `workflows-core-read-only.md:24`'s two sentences (R26).
- [ ] **Step 2: The exclusivity probe** over `the only`, `only writer`, `no command`, `by hand`, `no automated writer`, `nothing in this increment`, `is planned`, `a later command`, `a later spec`, `Spec 2`, and the noun forms for the backlog's writers and the agents' callers.
- [ ] **Step 3: Edit each false statement**; `python3 scripts/reference-parts.py generate` after the load-by-part references. A false sentence in a GIT-G1 file is reported, not edited.
- [ ] **Step 4: After counts** for each string changed; the probe re-run. **Step 5: Gates. Step 6: Commit:** `docs(doc-d-g1): the remaining copies`.

### Task 8: Release [mechanical]

**Files:** `plugins/docs-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, both `CHANGELOG.md`, `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/to-fix.md`, `to-test-on-real-project.md`, `reviews/2026-10-26-feature-gaps-review.md`.

- [ ] **Step 1: Merge.** `git fetch origin`; where `origin/main` moved, `git merge --no-edit origin/main`, keep both sides, and re-derive every count and size this plan touched, E1–E3 included (their text re-derived where the merge moved a number).
- [ ] **Step 2: Versions from `origin/main` now** (plan time: `docs-workflows` 1.40.0, `workflows-core` 1.96.0): each the next free minor (D16). `plugin.json` equals `marketplace.json`. Each CHANGELOG section dated with the landing day (UTC). `docs-workflows`' description gains `/docs-write` by **replacing** words, under 900 characters (861 now). `workflows-core`'s CHANGELOG names E1–E5; `docs-workflows`' names R1's correction, R21's clause, and the limits (R6, R7, R20's "places nothing" case, R3's from-state, R1's `indent` and `key` refusals with their remedy).
- [ ] **Step 3: One coupling bullet** (D16), under 700 characters: newer `docs-workflows` beside an older `workflows-core` — the reviewer's rule contradicts its own row, the cost entry waits in pending, the manifest lacks the command; update both. The file stays under 20,000. **Contingency** (M16): where the merge leaves no room and a fifth history file is needed, fold `CLAUDE.md`'s coupling-history rows into one row naming every history file, so its size does not pass 36,000.
- [ ] **Step 4: `to-fix.md`.** A *From DOC-D-G1* section: WHATSNEW-WRITE (`release` units and their two GIT-G1 edits); DOCUMENT-NAV (`/document` keyed places pages by hand while ST §4 has an entry point); R20's case where no placement target is found; what each task review left.
- [ ] **Step 5: `to-test-on-real-project.md`.** DOC-D-G4 (:258) runs step 4 as `/docs-workflows:docs-write --next`. A new entry headed with this release's versions: on the bookstore demo, `--next` commits page, navigation and backlog move in one commit, the strict public build passes over it, and `/docs-audit --refresh` leaves the unit `drafted`; what a miss looks like.
- [ ] **Step 6: The feature-gaps review**: DOC-D-G1's heading (:285), index row (:48) and summary (:13) gain *Designed in* the design's path and sub-project 1's versions; DOC-D-G2 (:292) gains that pages now exist by command.
- [ ] **Step 7: Gates**; measure `CLAUDE.md` and every rules file touched. **Step 8: Commit:** `release(doc-d-g1): docs-workflows <X>, workflows-core <Y> — /docs-write`.

### Task 9: Close [security-sensitive]

- [ ] **Step 1: Consistency.** Every array, printed line, marker, pointer sentence, carve-out, the stash clause, the triage row and E1–E5 is verbatim in the file that owns it (`command grep -F` each), E1–E3 as Task 8 Step 1 re-derived them (M15). BF §1's shape paragraph and the selftest's cases agree reason for reason. `unit-brief.md` §1 is the only copy of the replaced-sections list: `command grep -nE 'steps 2, 4, 5|Completeness vs plan.{0,40}Coverage' plugins/docs-workflows/agents/*.md` prints nothing.
- [ ] **Step 2: The design's D13 note.** Append under D13 a dated note giving R1's shape as built, without rewriting the approved text.
- [ ] **Step 3: Forward references**, each now true: Tasks 3 and 4's; and Task 1's — `.claude/rules/docs-workflows.md:13`'s "the backlog runs' map lines and invariants" and `:31`'s "the backlog runs' lines", each in `docs-workflows-backlog.md`, and that file's heading naming the backlog runs, made true by Task 2's `## Invariants` and Task 5b's `/docs-write` map line.
- [ ] **Step 4: No regression (D15).** Trace one keyed and one direct `/document` run through `doc-writer` and `doc-reviewer`: no path into `unit-brief.md`. List every hunk of `git diff origin/main...HEAD -- plugins/docs-workflows/agents plugins/workflows-core/references` with the condition under which it acts; one that changes `/document`'s behaviour beyond D9's carve-out and R21's clause is a defect.
- [ ] **Step 5: Fail-closed, the new cases:** a forged `kind: artifact` entry naming `security/x/register.md`; a `doc-location-finder` path with `..`; T-ARTQ re-run against the finished command.
- [ ] **Step 6: GIT-G1 audit.** `git diff origin/main...HEAD --stat` shows nothing under `phase-handoff.md`, its parts, `specs-git.py` and its modules, the `specs-git` skill or `workflows-core-handoff.md`. `.github/`'s diff is E4 and E5 exactly; `specs-repo-git.md`'s E3; `workflows-core-git.md`'s E1 and E2; `workflows-core-read-only.md`'s R26's two edits.
- [ ] **Step 7: The sweeps, closed.** Every before/after count of Tasks 3, 5a, 5b and 7 equals its intended value; the probe once more.
- [ ] **Step 8: The full CI list**: every step `.github/workflows/validate-catalog.yml` runs, in order, E4's among them and E5's comment beside its step, each `--selftest` and the mermaid gate where `node` exists.
- [ ] **Step 9: The PR text**, for the controller: E1–E5 with their approvals; R26's two edits; the command's GIT-G1-shaped sections, and SRG:757-762 and PH:628 as the GIT-G1 list names them; R1's correction as told to the maintainer; R21's clause; the limits (R6, R7, R20, R3); the fixtures built as traces; the versions; the attribution lines the session gives for pull requests.
- [ ] **Step 10: The whole-branch review** is the controller's: Fable against the design and this plan.

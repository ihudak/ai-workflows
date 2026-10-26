# Piece review: `/implement` reviews by piece, `/design` draws the pieces — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Where a change spans two or more of the design's pieces, `/dev-workflows:implement` reviews each touched piece with its own `code-review` and then the whole change with an overall `code-review`; `/design` draws the pieces, with a stated reason, and `design-reviewer` checks them; every `/implement` review with a specification in scope asks whether the spec-named tests would fail if their behaviour broke.

**Architecture:**
- **What the work is.** Prose in markdown command, agent and reference files, which agents execute literally, plus one new Python script, `plugins/dev-workflows/scripts/pieces.py`, which parses a design's `## Pieces` section and assigns a diff's paths to pieces. Everything deterministic (parsing, glob matching, overlap) is in the script; everything that needs judgement is in prose.
- **What stays.** `/implement`'s coding flow as dev-workflows 4.31.0 has it: step groups, `code-writer`, `test-writer` from the diff, review before the test run, `review-fixer`, two automated fix attempts, every model choice. A run whose change does not span two pieces gets today's single review, changed only by the `Spec-named tests:` line.
- **Where the change lands in `implement.md`.** Phase 3B steps 5 to 8 (the review gate, which Phase 3A step 6 runs at `MODERATE`), the run-state key list in Phase 1.4, the Phase 5 report's `### Opus review` section and the Invariants.
- **Source to reuse.** The shelved branch `iv-gu/implement-one-writer` (`ef81409a`, readable with `git show ef81409a:<path>`) has worked text for the pieces format (`plugins/dev-workflows/references/design-format.md`, its `## Pieces` item), `code-review`'s `Scope` and `Piece reviews` inputs (`plugins/dev-workflows/agents/code-review.md`), the `reviews` run-state key with its file removal (`plugins/dev-workflows/scripts/run-state.py`), and a split review (`plugins/dev-workflows/commands/implement.md` `## Phase 3.6`). Reuse wording where it fits; drop everything about writers, writer units, `SendMessage`, the lock, test runs before the review, and test results kept from reviewers.

**Tech Stack:** Markdown prose; Python 3 (standard library only, nothing newer than 3.8, macOS and Linux); `git`; the repository's gate chain (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-10-25-implement-piece-review-design.md` (commit `a8ef82d5`, with one correction made while planning: §3.1 point 7 — the implementation record is unchanged).

## Global Constraints

- `CLAUDE.md` § Editing discipline and § Hard constraints bind every edit: prose is executed; the claim-expiry sweep (`.claude/rules/claim-sweep.md`, all eight refinements); one source of truth per authority; `choices:` arrays presented verbatim and **no new question anywhere** (the design: `/implement` and `/design` ask nothing new); the docs tree for every changed command, agent and reference; the 1024-character descriptions.
- **dev-workflows 4.32.0** in `plugins/dev-workflows/.claude-plugin/plugin.json` and its `marketplace.json` entry, with a `## 4.32.0 — Unreleased` section in `plugins/dev-workflows/CHANGELOG.md`, dated before it reaches `main`. (4.32.0 was the shelved branch's version and was never released.)
- **No workflows-core change is planned.** If a task finds one is needed (Task 5 checks `finding-triage` and `escalation-rules`), it is a ruling: bump workflows-core, and add a coupling bullet to `.claude/rules/plugin-updates.md`.
- **A run whose change does not span two pieces is unchanged** save the `Spec-named tests:` line: same dispatches, same briefs, same run-state writes.
- **`implement.md` grows by at most 12,000 bytes** over the branch base (`wc -c plugins/dev-workflows/commands/implement.md` at the base, 326,520 at `a8ef82d5`). Measure after Tasks 3, 5 and 6; a larger delta is a ruling, never silently accepted.
- `pieces.py`: standard library only, Python 3.8 syntax, JSON on stdout, called by its path `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py" …`, with a `--selftest` CI runs.
- Work in a worktree on branch `iv-gu/implement-piece-review` from local `main`; never `git checkout` in `/workspace/ai-workflows`; `git branch --show-current` before every commit; never bare `git stash`.
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.
- The gate chain passes (one `&&` chain, its own exit code read) before each task's commit: the `run:` steps of `.github/workflows/validate-catalog.yml`, in order.
- No file in this repository names the test Epic's Java package path (check 14 and the identity rules): write `books/src/main/java/…/imports/csv/` and the like.
- The verification record is written last; the SDD ledger and rulings are preserved under `docs/superpowers/verification/` before the SDD workspace is deleted.

## Review Focus

1. **A pieced design whose `Files:` name only production code** (every hand-written design before this release, and the test Epic's until Task 7 rewrites it): the tests are unassigned, so piece reviewers see none and the overall review reviews them all in depth. Expected: the split still runs and the report's scope line shows the unassigned count. Pinned by Task 1's `assign_unassigned_tests` case and Task 5's end-to-end read.
2. **A diff path with a space, a quote or non-ASCII bytes**: the name list must come from `-z` output and each pathspec must be written `':(top,literal)<path>'` with `'` as `'\''`. Pinned by Task 1's `assign_odd_paths` case and Task 5's step 5 text.
3. **A file moved from one piece's directory to another's**: with `--no-renames`, both paths are in the list, so both pieces are touched. Pinned by Task 1's `assign_rename_touches_both` case.
4. **`design.md` unreadable at review time**, or `pieces.py` failing: the run must fall back to today's single review with a warning, never stop and never split on a guess. Pinned by Task 1's exit-4 cases and Task 5's fallback text.
5. **A `## Pieces` heading inside a fenced code block** (a design quoting the format): the parser must ignore it. Pinned by Task 1's `parse_ignores_fenced` case.

---

### Task 1: `pieces.py` — parse the section, assign a diff's paths

**Files:**
- Create: `plugins/dev-workflows/scripts/pieces.py`
- Modify: `.github/workflows/validate-catalog.yml` (one step after `Self-test the run-state file`)
- Modify: `plugins/dev-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (dev-workflows 4.32.0), `plugins/dev-workflows/CHANGELOG.md` (new `## 4.32.0 — Unreleased` section with one bullet for this task)

**Interfaces:**
- Produces, for Tasks 2, 5 and 7:
  - `python3 pieces.py parse <design.md>` → stdout JSON `{"status": "pieces"|"none"|"malformed", "defect": str|null, "reason": str|null, "pieces": [{"name": str, "files": [str], "contract": [str]}]}`; exit 0.
  - `python3 pieces.py assign <design.md> <paths-file>` → stdout JSON: parse's four fields, each piece also carrying `"paths": [str]` (the paths it matches, in input order), plus `"unassigned": [str]` and `"split": bool` (true exactly when `status` is `pieces` and two or more pieces have a non-empty `paths`); exit 0. On `none` or `malformed`, every path is unassigned and `split` is false. `<paths-file>` holds NUL-separated paths, as `git diff --name-only -z` writes them; an empty file is no paths.
  - Exit 2 on a usage error, exit 4 where `<design.md>` or `<paths-file>` cannot be read (message on stderr naming the path), exit 1 on a failed `--selftest`.
- **The format it reads** (Task 2 writes the same text into `design-format`):
  - The section starts at a line `## Pieces` outside any fenced code block and ends at the next `## ` heading outside one, or the end of the file. Lines inside fenced blocks are never read as the section.
  - **`none`**: no such heading, or a section whose first non-blank line begins `_N/A`.
  - Otherwise the section holds only blank lines, one `Reason: <text>` line before the first piece, and pieces, each a `### <name>` line followed by one `- Files: …` line and an optional `- Contract: …` line. CRLF line ends are accepted.
  - `Files:` is a comma-separated list of backtick-quoted entries; anything outside the backticks other than commas and spaces is a defect. `Contract:` is comma-separated plain text, or `none` (→ `[]`); absent → `[]`.
- **Malformed** (status `malformed`, `defect` one sentence naming the line or the entries): no `Reason:` line, or an empty one; fewer than two pieces; a piece name not kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`) or used twice; a piece with no `Files:` line or no entry; a `Files:` entry not in backticks; any other non-blank line (the defect quotes it — a `Writers:` or `Builds after:` line from the shelved format lands here); the same entry string in two pieces; and, in `assign` only, a path two pieces both match (the defect names the path and both pieces).
- **Pattern grammar** (each `Files:` entry, relative to the repository's top level): `*` matches any run of characters except `/`; `**` as a whole path segment matches zero or more segments (`a/**` matches everything under `a/`; `**/x.java` matches `x.java` at any depth); `?` matches one character except `/`; an entry ending in `/` matches everything under that directory; every other character is literal (no `[…]`, no `{…}`); an entry with no wildcard matches that one path.

- [ ] **Step 1: Set up the worktree and branch**

```bash
git -C /workspace/ai-workflows worktree add /workspace/.worktrees/implement-piece-review -b iv-gu/implement-piece-review main
```
Record `wc -c plugins/dev-workflows/commands/implement.md` there (expect `326520`) in the SDD ledger as the size base.

- [ ] **Step 2: Write the selftest cases first**

In `pieces.py`, a `selftest()` that builds design files and path files in a temp directory and runs the CLI through `subprocess` (as `run-state.py --selftest` does), with these cases, each a named `check(...)`:
- `parse_none_no_section` → `status == "none"`, `pieces == []`.
- `parse_none_na` (`## Pieces` then `_N/A — one coherent change_`) → `none`.
- `parse_two_pieces` (Reason, `### parser` with two backticked globs and `Contract: A, B`, `### runs` with one entry and `Contract: none`) → `pieces`, names `["parser", "runs"]`, the files as written, contracts `["A", "B"]` and `[]`, `reason` the text after `Reason: `.
- `parse_no_reason`, `parse_empty_reason`, `parse_one_piece`, `parse_duplicate_name`, `parse_bad_name` (`### Parser`), `parse_no_files`, `parse_unquoted_entry`, `parse_writers_line` (`Writers: one`), `parse_same_entry_twice` → each `malformed`, `defect` non-empty.
- `parse_ignores_fenced` (a fenced block holding `## Pieces` and a malformed body, no real section) → `none`.
- `parse_crlf` (`parse_two_pieces`'s text with CRLF ends) → same result as `parse_two_pieces`.
- `parse_section_ends_at_next_h2` (a `## Seams` after the pieces with a `### x` under it) → only the two pieces.
- `glob_star_one_segment` (`src/a/*.java` matches `src/a/X.java`, not `src/a/b/X.java`), `glob_double_star` (`src/a/**` matches both; `**/X.java` matches `X.java` and `d/e/X.java`), `glob_question`, `glob_exact`, `glob_trailing_slash`.
- `assign_split` (paths in both pieces) → `split` true, each piece's `paths` as matched, `unassigned` the rest.
- `assign_one_piece_touched` → `split` false.
- `assign_unassigned_tests` (production globs only; a test path) → the test path in `unassigned`, `split` per the production paths.
- `assign_odd_paths` (a path with a space, one with `'`, one with `é`, matched by `*`) → matched and returned byte-for-byte as given.
- `assign_rename_touches_both` (an old path under piece A's glob and a new one under B's) → `split` true.
- `assign_overlap` (`src/**` in one piece, `src/a/X.java` in another, path `src/a/X.java`) → `malformed`, defect naming the path and both pieces, `split` false.
- `assign_none_section` → every path unassigned, `split` false.
- `assign_empty_paths` → `split` false, no paths.
- `missing_design_exit_4`, `missing_paths_exit_4`, `usage_exit_2`.

- [ ] **Step 3: Run the selftest and see it fail**

Run: `python3 plugins/dev-workflows/scripts/pieces.py --selftest`
Expected: FAIL (the commands are not implemented).

- [ ] **Step 4: Implement `parse` and `assign`**

`parse_section(text: str) -> dict` and `assign(parsed: dict, paths: list[str]) -> dict` behind the two subcommands; `glob_to_regex(entry: str) -> re.Pattern` per the grammar (translate segment by segment so `**` and `*` keep their meanings). Read the design as UTF-8 with `errors="surrogateescape"` and the paths file as bytes split on `\0`, decoded the same way, so odd bytes round-trip; write JSON with `ensure_ascii=False`.

- [ ] **Step 5: Run the selftest and see it pass**

Run: `python3 plugins/dev-workflows/scripts/pieces.py --selftest`
Expected: every check passes, exit 0.

- [ ] **Step 6: Add the CI step, the version and the CHANGELOG bullet**

After the `Self-test the run-state file` step:
```yaml
      - name: Self-test the design pieces reader
        # /implement splits its review by the design's pieces, and /design checks the section it writes, through this script.
        run: python3 plugins/dev-workflows/scripts/pieces.py --selftest
```
Where `.claude/rules/gates*.md` or `docs/maintainers/` list the CI self-test steps by name, add this one there too (grep for `Self-test the run-state file`).

- [ ] **Step 7: Run the gate chain, then commit**

```bash
git add plugins/dev-workflows/scripts/pieces.py .github/workflows/validate-catalog.yml plugins/dev-workflows/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/dev-workflows/CHANGELOG.md
git commit -m "feat(dev-workflows): pieces.py reads a design's ## Pieces section and assigns a diff's paths to pieces"
```

---

### Task 2: The format, `/design` drawing pieces, `design-reviewer` checking them

**Files:**
- Modify: `plugins/dev-workflows/references/design-format.md` (a new optional section)
- Modify: `plugins/dev-workflows/commands/design.md` (Phase 5's authoring rules; the final report's design block, if it lists sections)
- Modify: `plugins/dev-workflows/agents/design-reviewer.md` (its section check and a new check)
- Modify: `plugins/dev-workflows/docs/commands/design.md`, `plugins/dev-workflows/docs/reference/agents.md` (the `design-reviewer` line)
- Modify: `plugins/dev-workflows/CHANGELOG.md`

**Interfaces:**
- Consumes: Task 1's `parse` and its format and grammar, verbatim.
- Produces: `design-format`'s `## Pieces` item, which Task 5's `implement.md` and Task 4's `code-review.md` cite as "`dev-workflows:design-format`'s `## Pieces`" — never by section number.

- [ ] **Step 1: Add `## Pieces` to `design-format`**

- **Placement (ruling):** a new item **14**, after `## Open questions`, marked *optional*, so no existing section number changes. The shelved branch inserted it as section 5 and renumbered 13 citations across three files; appending avoids that sweep, and the parser finds the section wherever it stands.
- Add the *optional* category beside *core* and *scaled* in the opening paragraph, as the branch's text does: present only where its own rule calls for it, its absence meaning one piece, needing no `_N/A_` line at any classification.
- The item's text: what a piece is (a unit of review, never of coding); **both conditions** of the design's §3.2 — the `Reason:` line (why one reviewer could not review the whole change in depth: its size, its distinct layers or concerns, its test cases; never a threshold) and the boundary (no overlapping `Files:`, the shared part fixed in `## Interfaces / contracts` and named in `Contract:`); `Files:` names the piece's tests as well as its code, a test file shared by pieces named by none; a file no piece names is reviewed by the overall review and is not barred from editing; one piece is written by omitting the section or `_N/A — <why>_`; the fenced format block with `Reason:`, `### <piece-name>`, `- Files:`, `- Contract:`; and Task 1's grammar and malformed list, stated once here.
- State that `pieces.py parse` is the check `/design` and `design-reviewer` run, and `pieces.py assign` what `/implement` runs.

- [ ] **Step 2: `/design` draws the pieces and checks the section it wrote**

In Phase 5's authoring rules (the list beside *Behaviour at a boundary* and *Release verification*), one bullet, **Pieces**: draw them under `design-format`'s `## Pieces` rules, with the reason thought through and written, never by count; no new question (it may come up in the grill like any design decision). After `design.md` is written and before the review gate, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py" parse <design.md>`: `malformed` is fixed in the file before review, the defect named in the run's report; `none` and `pieces` go on. Add `## Pieces` to the design block's section list wherever the command lists the sections it writes.

- [ ] **Step 3: `design-reviewer` checks the section**

- Its section check: the optional `## Pieces` needs no `_N/A_` line and its omission is never a finding (the branch's wording).
- A new check, **Pieces**, run where the section is present: run `pieces.py parse` on the design (the agent has Bash; `${CLAUDE_PLUGIN_ROOT}` expands in agent bodies) — `malformed` is a `MAJOR` naming the defect; then judge the reason (a change one reviewer could review in depth → `MAJOR`, drop the pieces), the boundary (overlapping `Files:` against the files on disk at the scanned commit and the files the design creates; a piece whose files depend on another's internals; a shared part not fixed in `## Interfaces / contracts`; a `Contract:` item the contracts section does not define → each `MAJOR`), and tests left out of every piece's `Files:` where they are not shared (`MINOR`).
- Where the section is absent and the change plainly needs pieces: a `MINOR` at most, a recommendation, never `BLOCKER` or `MAJOR` (the design: one review is today's behaviour, never a defect).

- [ ] **Step 4: Docs and CHANGELOG**

`docs/commands/design.md`: what the section is, when `/design` draws it, the check it runs. `docs/reference/agents.md`: `design-reviewer`'s line names the pieces check where it lists checks. One CHANGELOG bullet.

- [ ] **Step 5: Verify**

- `python3 plugins/dev-workflows/scripts/pieces.py parse` on a scratch copy of `design-format`'s own format block wrapped as a design → `pieces` (the example must parse).
- The gate chain passes.
- Read `/design` Phase 5 to Phase 6 end to end with the new bullet: a design with pieces, one without, one written malformed.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(dev-workflows): /design draws review pieces with a stated reason; design-reviewer checks them"
```

---

### Task 3: Run-state keys `pieces` and `reviews`

**Files:**
- Modify: `plugins/dev-workflows/scripts/run-state.py` (`KEYS`, the comment block of list shapes, the removal of temp files, `--selftest`)
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 1.4's quoted key list and its key bullets)

**Interfaces:**
- Produces, for Task 5:
  - `pieces` — default `[]`; entries `{"name", "files": [str], "contract": [str]}`, from `pieces.py parse` at the first review round where its status is `pieces`, else left `[]`.
  - `reviews` — default `[]`; one entry per review a **split** round dispatches: `{"round": "first"|"re-review", "scope": "piece:<name>"|"overall", "paths": [str], "diff_file": str|null, "return_file": str|null, "verdict": str|null}` — `paths` a piece's matched paths, `[]` for `overall`. Unsplit reviews keep today's keys (`files.review_diff_file`, `files.review_return_file`) and write nothing here.
- `KEYS` order: `("step_groups", []), ("pieces", []), ("reviews", []), ("patches", []), ("triage", [])`.

- [ ] **Step 1: Selftest cases first**

Add, following the branch's tests (`git show ef81409a:plugins/dev-workflows/scripts/run-state.py`, its `reviews` cases):
- `init defaults pieces and reviews to empty lists`;
- `init accepts a pieces entry and a reviews entry`;
- `init refuses pieces given as a string`;
- `a set of reviews that drops an entry removes its diff and return files` (files made with a `dw-impl-` name), and `keeps the files of the entry it keeps`;
- `remove takes a review's files`.

- [ ] **Step 2: Run and see them fail**

Run: `python3 plugins/dev-workflows/scripts/run-state.py --selftest` → FAIL on the new checks (and on `implement.md quotes KEYS exactly` once `KEYS` changes in step 3, until step 4).

- [ ] **Step 3: Implement**

Add the two keys; list each `reviews` entry's `diff_file` and `return_file` among the paths a `set` may stop naming and `remove` removes, as `files` members are (the branch's code for `reviews`, without `writers`). Document both shapes in the comment block.

- [ ] **Step 4: `implement.md` Phase 1.4**

Update the quoted key list (the line beginning `The file holds exactly these keys`) to the new `KEYS_LINE`, and add a key bullet for each of `pieces` and `reviews` in the style of the neighbouring ones, each naming the phase and step that writes it (Phase 3B step 5 and step 7, Task 5).

- [ ] **Step 5: Verify and commit**

`python3 plugins/dev-workflows/scripts/run-state.py --selftest` passes (`implement.md quotes KEYS exactly` included); the gate chain passes; record `wc -c` of `implement.md` in the ledger.
```bash
git commit -m "feat(dev-workflows): run-state keys pieces and reviews for /implement's split review"
```

---

### Task 4: `code-review` — `Scope`, `Piece reviews`, `Spec-named tests`

**Files:**
- Modify: `plugins/dev-workflows/agents/code-review.md` (`## Inputs`, the escape hatch, the read-failure tiers, its `description` if it states that `/implement` makes one review)
- Modify: `plugins/dev-workflows/docs/reference/agents.md` (the `code-review` line), `plugins/dev-workflows/CHANGELOG.md`

**Interfaces:**
- Produces, for Task 5, three optional inputs `/implement` alone passes (absent from `/vuln` and `/upgrade`, whose reviews are unchanged):
  - `Scope: piece <name> — files: <paths, comma-separated>` or `Scope: overall — pieces: <names> — only here: <paths, comma-separated, or none>`. Absent: the diff is the whole change, as today.
  - `Piece reviews: <name>: <absolute path of its return>, …` — on an `overall` scope only; a *context* input (unreadable degrades to absent, named in the Summary).
  - `Spec-named tests: <spec paths, comma-separated>` — wherever `/implement` would pass `applicable_spec` on an unsplit review, and on a piece review, which gets no `applicable_spec`.

- [ ] **Step 1: The inputs**

- `Scope` and `Piece reviews`: take the branch's text (`git show ef81409a:plugins/dev-workflows/agents/code-review.md`, the two bullets), dropping every sentence about writers, test runs before the review and test results. Keep: a piece review reviews its files in depth on every dimension, reads others only to understand them, locates each finding in one of its files (save a fix's second site, `also at`), and names a defect seen outside them in `### Declined to judge` as the overall review's; the overall review reads the piece reviews first, reviews each `only here` path in depth, looks for what no piece review can see (where the pieces meet and their `Contract:` items, duplicated helpers, inconsistent conventions, behaviour spanning pieces), and raises no finding a piece review already made.
- `Spec-named tests` (**ruling**: its meaning is defined here, in the agent's Inputs where every brief field is defined, and only `/implement` passes it; it is an input, not a dimension, so the design's "never `code-review`'s own dimensions" holds): for each test the change adds or changes that is named after a test case or acceptance criterion of those files — within the `Scope`'s files where one is given — ask whether it would fail if the behaviour it names broke; a test whose assertions hold whatever the code does (a double standing in for the very behaviour under test, an assertion on a value the test itself set) is a finding under the tests dimension, graded by its effect. Reading the files for this makes no requirement trace: dimension 10 runs only where `applicable_spec` is given.
- Dimension 9 (ARD) on a piece review: violations located in its own files.

- [ ] **Step 2: The escape hatch**

Add the branch's rule: never return a `### Re-classification` on a brief with a `Scope:` — a piece review sees part of the change, and the overall review follows reviews whose findings an implicit pass would leave unread — so either returns the full report.

- [ ] **Step 3: Verify and commit**

- `/vuln` and `/upgrade` pass none of the three: grep their command files and confirm no brief carries `Scope:`, `Piece reviews:` or `Spec-named tests:`.
- The gate chain passes (check 16 and the description budget included).
```bash
git commit -m "feat(dev-workflows): code-review takes a piece or overall scope and checks spec-named tests on /implement's briefs"
```

---

### Task 5: `/implement`'s review gate — the split review

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` — Phase 3B steps 5, 6, 7, 7.5 and 8; Phase 3A step 6's list (its six numbered items)

**Interfaces:**
- Consumes: Task 1's CLI and JSON; Task 3's `pieces` and `reviews`; Task 4's three inputs; the design's §3.1 points 1–6.
- Produces, for Task 6: the run-state writes the report reads (`reviews`, each round's `triage` entries naming their scope).

- [ ] **Step 1: Re-read the authorities this step must not contradict**

Load `finding-triage` parts `triage` and `re-review` and `escalation-rules review`, and read them against the split flow below: one triage per review pass, the reporting contract's one line per pass, the settle prompts, *On re-review*, the offer to apply what a review leaves open. Where a sentence there would contradict the split, word `implement.md` to satisfy it; where that is impossible, stop and record a ruling (a workflows-core change, Global Constraints).

- [ ] **Step 2: Step 5 — decide the split, capture the diffs**

After today's whole-diff capture to `review_diff_file` (unchanged):
- **On the first review round only**, where `spec_context.spec_paths` holds a `design.md` and the run is no companion run: write the change's path list — today's recipe with `--no-renames --name-only -z` in place of the patch output — to a temp file (`command mktemp -t dw-impl-paths-XXXXXX`), and run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/pieces.py" assign <design.md> <that file>`.
  - `split: true` → write run-state `pieces` (the parsed pieces, without `paths`) and go on split.
  - `status: none`, or `split: false` → today's review, nothing written.
  - `status: malformed`, a non-zero exit, or an unreadable output → today's review; print one line `design.md's ## Pieces unusable — <the defect, or the exit and its message> — reviewed as one piece` and write it to run-state `assumptions`. Ask nothing.
- **A split round** also writes, for each piece whose `paths` is non-empty, a piece diff: today's recipe with ` -- ` and each of its paths as `':(top,literal)<path>'` (a `'` inside written `'\''`) after its last argument, to a fresh `dw-impl-diff-XXXXXX` file. Record one `reviews` entry per piece and one for `overall` (its `diff_file` the whole diff) before dispatching (`round`: `first`).
- Name the path-list recipe and the per-piece recipe once here; step 7's re-review round cites them.

- [ ] **Step 3: Step 6 — the briefs**

- **Every brief** (split or not, step 8's included): add `Spec-named tests: [the spec paths of applicable_spec — present wherever this brief carries applicable_spec, and on a piece review of a run whose overall review carries it; omit otherwise]`.
- **A split round** dispatches the piece reviews in **one** response, then, once each return is written down and checked (step 7), the overall review. A piece review's brief is today's brief with: `Scope: piece <name> — files: <its paths>`; `Diff:` its piece diff; **no** `applicable_spec` line (no requirement trace: the overall review's alone); `applicable_ard`, `Plan ruling`, `Helper copies`, `Security register`, `Deferred to another code repository` and, on a re-review, `claims_file` as today. The overall brief is today's brief with: `Scope: overall — pieces: <each touched piece, in section order> — only here: <each unassigned path, or none>`; `Piece reviews: <name>: <its return_file>, …` (this round's); `Diff:` the whole diff; `applicable_spec` as today.
- Write the split as a short addition to today's step 6, never a second copy of the brief.

- [ ] **Step 4: Step 7 — acting on a split round**

Add one paragraph, **A split round**, before the arms, that changes only what it names:
- **Write each return down** to its own `dw-impl-return-XXXXXX` file, recorded as its `reviews` entry's `return_file` and `verdict` — today's *First write the return down*, per review.
- **Check each return's first line** as today (`Diff: unreadable` stops). A `### Re-classification` on a scoped brief cannot occur (Task 4); one that comes back is re-invoked once with the override's note, asking nothing, and a second is put as today's `choices: ["Re-run the full review", "Cancel"]`, verbatim.
- **Triage** each review of the round under today's triage sub-step, after all of them are written down, in `reviews` order, one `triage` entry per review, its `pass` naming the round and the scope. A finding a later review of the round raises at a location and with a claim an earlier one holds takes that one's disposition and is one finding (the branch's sentence).
- **The round's verdict** is the worst of its reviews' verdicts (`BLOCK` over `PASS WITH RECOMMENDATIONS` over `PASS`), and today's arms, settle prompts and offer act on it and on the round's survivors together; each settle prompt is asked once for the round.
- **One `review-fixer` pass**, today's, takes every survivor the arms send it from all the round's reviews in one `review_file`. The plan-conflict question and the `Stop condition flag` are unchanged.
- **The re-review round** — wherever today's step 7 runs or offers its one re-review, and **Re-review** at the first settle prompt — re-captures the whole diff and the path list, runs `pieces.py assign` again (a `malformed` result here: the round is unsplit, as step 2 says), and dispatches a review of each piece whose `paths` hold a file the Fix Report's `### Files changed` names, then the overall review (`round`: `re-review`); at the settle prompt's **Re-review**, with no fix between, every review of the first round is re-run, each brief supplying its own dispositions' reasons. Triage each under *On re-review*; the round's verdict as above; a review that stayed blocked stops the run as today.
- Today's single-review text stays as it is for an unsplit round.

- [ ] **Step 5: Steps 7.5 and 8**

- Step 7.5: on a split run, the spec/design-conformance dimension read is the latest overall review's (`reviews`, its last `overall` entry's `return_file`), and it alone writes run-state `conformance`.
- Step 8: unchanged — today's single review of the whole change after the Phase 3.5 fixes, unsplit (the design, §3.1 point 5), with the `Spec-named tests:` line of step 3.

- [ ] **Step 6: Phase 3A step 6's list**

Its items 2–4 name step 5's split decision, step 6's piece and overall reviews, and step 7's round, each in a few words.

- [ ] **Step 7: Verify**

- Three end-to-end reads of the edited gate, writing each outcome into the task report: **(a)** a `MODERATE` direct run (no design) — every dispatch and write identical to `a8ef82d5`'s save the `Spec-named tests:` line; **(b)** a `SIGNIFICANT` keyed run on a two-piece design whose diff touches both and one unassigned file — first round BLOCK on one piece, the fixer touching only that piece, the re-review dispatching that piece and the overall, then step 8; **(c)** the same run with a `Writers:` line in its section — the fallback line, today's review.
- `run-state.py --selftest`, `pieces.py --selftest` and the gate chain pass (`check-questions` and check 12 included: no new `choices:` array).
- `wc -c implement.md` recorded; the delta so far within the Global Constraints cap.

- [ ] **Step 8: Commit**

```bash
git commit -m "feat(dev-workflows): /implement reviews each touched piece and the whole change where the design draws pieces"
```

---

### Task 6: Report, invariants, docs, rules, sweep

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 5's `### Opus review` section; `## Invariants`)
- Modify: `plugins/dev-workflows/docs/commands/implement.md` (the review section; `pieces.py` beside `run-state.py` where scripts are listed)
- Modify: `.claude/rules/dev-workflows.md` (the `/implement` and `/design` map lines; the Opus-review-gate invariant), `.claude/rules/dev-workflows-implement.md` (the *`MODERATE` work is reviewed* and `review-fixer` bullets)
- Modify: `docs/maintainers/rationale.md` (a new `#piece-review` section the rules bullets link)
- Modify: `plugins/workflows-core/references/model-routing/classification.md` §3.1 **only if** it states that `/implement` makes one review (a ruling: that is a workflows-core change, Global Constraints)
- Modify: `plugins/dev-workflows/CHANGELOG.md` (the release's full entry)

**Interfaces:**
- Consumes: Task 5's `reviews` and `triage` writes; Task 2's and Task 4's wording.

- [ ] **Step 1: The report and the Invariants**

- `### Opus review`: on a split run, one line per review — `<round> — <scope> — <verdict>` (reads run-state `reviews`) — before today's text; nothing on an unsplit run.
- `## Invariants`: one bullet — where the design draws pieces and the change touches two or more, the review is split (step 5), the overall review alone traces requirements, one triage and one fixer pass serve the round, and step 8's review is unsplit; a `## Pieces` the run cannot use falls back to one review with a printed line, asking nothing. Cite the steps; restate nothing they hold.

- [ ] **Step 2: The claim sweep**

Subject: **how many reviews `/implement` makes, and what reviews it**. Refinement 4's scope (`plugins/` with every `CHANGELOG.md`, `README.md`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/`). Phrase starts: `one review`, `the review`, `Opus review`, `code-review@Opus`, `re-review`, `single review`, `review gate`, `review_diff_file`, `the review diff`; exclusivity probe (refinement 3). Read every hit's paragraph against the split; count each changed literal string before and after (refinement 7). Record the table of hits and dispositions in the task report.

- [ ] **Step 3: Rules, rationale, docs**

- The map line: `[code-review@Opus, MODERATE and up — one per touched piece and one overall where the design draws two or more pieces]`, or equivalent; the `/design` line names the pieces it draws.
- `dev-workflows-implement.md`: the review bullet says the split in one sentence and links `rationale.md#piece-review`.
- `rationale.md#piece-review`: the A/B in three lines (arms, cost, judges, where B's edge came from), why pieces need a reason, why step 8 stays unsplit, why only the overall review traces requirements — citing the verification record Task 9 writes.
- Re-derive every number in `.claude/rules/` and `CLAUDE.md` the change touches (scripts, pages), with its command beside it.
- `docs/commands/implement.md`: the split review as a user sees it, the fallback line, `pieces.py`.

- [ ] **Step 4: The rule-by-rule reading**

Read `implement.md` Phase 3B steps 5–8 at `a8ef82d5` against the branch, rule by rule; every rule of the old text has a place in the new or a recorded reason for its change. Write the table to the task report.

- [ ] **Step 5: Verify and commit**

The gate chain passes; `implement.md`'s total delta is within the cap (`wc -c`, against 326,520).
```bash
git commit -m "docs(dev-workflows): the split review in the report, invariants, docs and rules; claim sweep"
```

---

### Task 7: The live proof — run C on BOOK-3-01

The user drives the live session; Claude prepares, measures and judges. Everything runs on the `ihudak-e2e` copies (`/workspace/e2e/bookstore`, `/workspace/e2e/bookstore-specs`), never on `/workspace/bookstore` or `/workspace/bookstore-specs`.

**Files (outside the repository):**
- Modify: `~/e2e-live/one-writer/run-epic.sh` (an arm `C`)
- A new commit on the specs copy's `main` (`ihudak-e2e`): the test Epic's `design.md` `## Pieces` rewritten
- Records: `~/e2e-live/one-writer/C/` (the same file set as `A/` and `B/`)

- [ ] **Step 1: Rewrite the test Epic's `## Pieces`**

On the specs copy, from `0d68eb7`, in `specifications/PRD-BOOK-3-bulk-catalogue-import/EPIC-BOOK-3-01-books-csv-import/design.md`: the `Writers:` line becomes `Reason: <the same facts, about reviewing: about 1,300–1,600 lines of production code in two layers with different test styles, carrying 85 specification test cases, more than one reviewer can review in depth; the halves meet only at the four parser types fixed in § Interfaces / contracts>`; each `Builds after:` line is removed; each piece's `Files:` gains its test-package twin (the `src/test/java/…/imports/csv/*.java` and `…/imports/run/*.java` globs). Nothing else changes. Commit `NOISSUE Pieces section in the piece-review format for arm C` and push to the copy's `origin`.

- [ ] **Step 2: Check the section against arm A's paths**

`git diff --name-only -z --no-renames 6942a24 5e0c6c0` from the code copy's object store (or arm A's `code.diff` paths) into a file; run Task 1's `pieces.py assign` on the rewritten design. Expected: `status: pieces`, `split: true`, both pieces with paths, `unassigned` holding `CLAUDE.md` and the shared test helper at `…/imports/TestIsbns.java`. Record the output in `C/split-check.json`.

- [ ] **Step 3: Arm C in `run-epic.sh`**

`C) export E2E_PLUGIN_SRC=/workspace/.worktrees/implement-piece-review/plugins; SPECS_START=<step 1's commit>`. `SPECS_START` is assigned per arm, after the `case`. Dry-read the script: the archive step bundles B's branch before deleting it.

- [ ] **Step 4: The run (the user)**

The user runs `~/e2e-live/one-writer/run-epic.sh C`, then `/dev-workflows:implement BOOK-3-01`, answering as arms A and B were answered (plan approve, the proposed branch, the review offers by their recommendation, push and PR "Neither"). Claude does not predict or narrate the run.

- [ ] **Step 5: Measure**

With `~/e2e-live/lean-context-part1/live-measure.py` and the scratch `per-agent.py` and `main-results.py`: total cost, cost by agent type, review cost by scope, main-session calls, median and peak context, compactions, wall time, user wait; tests and `@Test` count. Save as for A and B. A total above $80 is a finding to explain before release (the design, §4).

- [ ] **Step 6: Blind judges**

- Prepare blind trees as for A and B (`scratchpad/blind-epic*`), A/B/C mentions masked in the Epic copy; a mapping file `~/e2e-live/one-writer/blind-mapping-C.txt`.
- **Two Opus judges on C against A**, labels swapped between them; **one on C against B**, informative. Each gets the spec, design, glossary and Epic and the two trees, and returns a verdict with defects by severity and confidence.
- Pass: neither C-vs-A judge rates C worse. A close verdict ("slightly", or "medium" confidence) gets a second pair of judges on the same trees; where the pairs disagree, ask the user whether to repeat the live run (about $70 and four hours).

- [ ] **Step 7: Record**

Every result in the SDD ledger; verdicts copied to `~/e2e-live/one-writer/verdict-C-*.md`.

---

### Task 8: Two `/design` runs

The user answers the grill. The release under test is the worktree's (`E2E_PLUGIN_SRC`), in the e2e copies.

- [ ] **Step 1: BOOK-3-01 from its specification**

A specs-copy branch from Task 7's start with the Epic's `design.md` removed; run `/dev-workflows:design BOOK-3-01`. Expected: a `## Pieces` section that `pieces.py parse` reads as `pieces`, two pieces at the parser contract or a defensible alternative, and a `design-reviewer` verdict that is not `BLOCK` on the section. Record the section and the verdict.

- [ ] **Step 2: BOOK-1-01**

From specs baseline `c78ffdb`, `/dev-workflows:design BOOK-1-01`. Expected: no `## Pieces` section, or `_N/A_`. Two pieces drawn with a reason that does not hold is a finding against Task 2's wording, fixed and re-checked by reading, not by another run.

- [ ] **Step 3: Record** both in the ledger, with cost.

---

### Task 9: Records and finish

- [ ] **Step 1: Part (a)'s record**

`docs/superpowers/verification/2026-10-24-implement-one-writer-a.md`: part (a)'s A/B — setup, arms, costs by agent, the cache diagnosis, both judges' verdicts and reasons, the two branch defects, the two incidents and their recovery, why it was not merged, and every ruling R1–R48 with its cost. Copy the ledger verbatim beside it, following the naming of the existing ledgers there (`ls docs/superpowers/verification/`), from `/workspace/.worktrees/implement-one-writer/.superpowers/sdd/2026-10-24-implement-one-writer-a/progress.md`.

- [ ] **Step 2: `docs/superpowers/to-fix.md`**

- E4's row for `40e6b9ea`: the port is of this release, not of the one-writer `/implement`.
- A new entry: the BOOK-3-01 design's test strategy prescribed a mocked writer for a criterion about rollback, so a test following the design holds trivially — one instance, recorded, not ruled on.

- [ ] **Step 3: This sub-project's record — last**

`docs/superpowers/verification/2026-10-25-implement-piece-review.md`, written after the final fix wave: Tasks 7 and 8's results, every expected value re-derived against the tree, every ruling with its cost; this plan's SDD ledger copied beside it. Then delete this plan's SDD workspace.

- [ ] **Step 4: Finish (asks the user before anything outward)**

Re-check `origin/main`; date the CHANGELOG section; merge `--no-ff` in a temporary worktree; run the gate chain with `ASSERT_PUBLISHED` as CI sets it; **ask the user before `git push origin main`** (local `main` also carries `086c2d51`, `1f74fc03`, `a8ef82d5` and this plan's commit). The shelved branch and its worktree stay until the user decides (worktrees are bind mounts: removal may need the host).

# D50 Same-Day Ordering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/dev-workflows:ready` and `source-truth` §7.8 order `/implement` work against the conformance record and the release-preparation drafts by UTC instant wherever both records carry one, and fall back to today's date comparison wherever either does not.

**Architecture:** Four records gain one additive UTC instant each:
- an `at:` field on `/implement`'s block entry;
- a `- **At:**` header line on the conformance record;
- an `at:` line in the release-note scope comment;
- an HTML-comment last line in `pr-draft.md`.

Every existing heading and line is unchanged. One pair rule decides the order, stated in `ready.md` for `/ready` and in `source-truth` §7.8 for the documentation commands. Only two scripts are touched, and only their selftests.

**Tech Stack:** Markdown prose that agents execute; Python 3.11 selftests (`lineage.py`, `session-branch.py`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-12-d50-same-day-ordering-design.md` (approved 2026-11-12). Every task's implementer reads it whole first.

**Reviewed:** a Fable plan review (2026-11-12, *approve with changes*). Every finding is folded in.

## Global Constraints

### The instant and how it compares

- **The instant's form:** exactly `^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$`.
  - It is written by pasting the output of `date -u +%Y-%m-%dT%H:%M:%SZ` verbatim.
  - A value that does not match is **no instant**. It never makes a record unreadable.
  - Two instants that both match are compared with `[ "$a" \> "$b" ]`. Equal is not later.
- **The guard's recipe**, stated identically wherever it appears (Tasks 2, 3 and 5). An `At:` is an instant only where
  ```
  python3 -c 'import sys,datetime as d; print(abs((d.date.fromisoformat(sys.argv[1][:10])-d.date.fromisoformat(sys.argv[2])).days)>1)' "<At value>" "<Run: date>"
  ```
  prints `False`. Anything else means no instant: `True` (more than a day from its `Run:` date), or an error and no output, which an impossible date in either argument causes (`2026-11-31`, `9999-99-99`, a malformed `Run:` date).
- **A multi-entry block** has an instant only where every entry carries the same valid `at:`.

### The records

- **Unchanged:**
  - `## <YYYY-MM-DD> — /implement` headings;
  - the `- **Run:**` line;
  - the scope comment's first line;
  - `pr-draft.md`'s DO-NOT-MERGE banner, which, where there is one, stays its first line.
- **The new lines, character for character:**
  - **Block entry:** `  at:      <instant>`, after `pushed:` and before any `accepted:`.
  - **Record header:** `- **At:** <instant>`, the line right after `- **Run:**`.
  - **Scope comment:** `at: <instant>`, after `stage:` and before the `read:` lines.
  - **`pr-draft.md`'s last line:** `<!-- implementation records read: <instant> -->`, followed by exactly one newline and nothing else.
- **Which moment each record takes:**
  - **A block:** the instant `/implement` Phase 4.7 appends it.
  - **`/conformance`, `/release-notes`, `/document`:** the instant the run started, taken right after `strip-run-flags`, carried in the run, and written with the record.

### Releases, names and ownership

- **Intended versions:**
  - `workflows-core` 1.85.0, `dev-workflows` 4.63.0, `docs-workflows` 1.39.0, `product-workflows` 3.79.4. On `origin/main` `fdafe85e` they stand at 1.84.0, 4.62.4, 1.38.3 and 3.79.3.
  - Write these numbers wherever prose needs a version, for example "a block written before `dev-workflows` 4.63.0 carries no `at:`".
  - Task 6 re-checks them, and replaces them if `main` has moved.
- **`finish-and-handoff` is `docs-workflows`' own reference:** `plugins/docs-workflows/references/finish-and-handoff.md`, cited from `/document` as `${CLAUDE_PLUGIN_ROOT}/references/finish-and-handoff.md`. Never cite it as `workflows-core:`.
- **GIT-G1's sections.** Do not edit them in any command:
  - the **Ending early** paragraph;
  - the specs preflight;
  - `branch-check`;
  - `require-on-main`;
  - the specs-repo handover (`handoff-to-main`, the consent choice, the outcome line, `body_facts`);
  - the terminal `commit-artifacts`.

  `/document` Phase 8.5 steps 3–4 (the documentation repository's PR draft) are **not** GIT-G1's.

  Do not edit these files at all: `specs-repo-git.md`, `phase-handoff.md`, `scripts/specs-git.py`, `.github/workflows/validate-catalog.yml`, `.claude/rules/workflows-core-git.md`.

### How to work

- **Prose is executed.** One reading only, and every claim must be true of the run. Read a file with the Read tool before editing in its area, so the rules files load.
- **Rules-file sizes:**
  - `.claude/rules/dev-workflows.md` is at 19,953 characters and `.claude/rules/docs-workflows.md` at 19,978. Any edit to either must be net-zero or smaller.
  - Every rules file stays under 20,000 characters by Python `len`.
- **Gates before every commit:**
  - `python3 scripts/validate-catalog.py`
  - `./scripts/check-id-grammar.sh --root .`
  - `./scripts/check-id-grammar.sh --root . --baseline`
  - `python3 scripts/reference-parts.py check-parts`, `check-citations`, `check-questions` and `check-branch-check`
  - `./scripts/check-docs.sh --root .`

  Run them as one `&&` chain under `set -o pipefail`. Expected: `EXIT=0` **and 0 warnings** from `validate-catalog.py`. A task that touches a script also runs its `--selftest`.
- **Commits:**
  - The message ends with the two trailers:
    ```
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01EcAVqApJxfCBcAbv5iWuu7
    ```
  - Run `git branch --show-current` first; it must print `fix/d50-same-day-ordering`.
  - Stage `.claude/rules/` files with `git add -f`.
  - Do not push.

## Review Focus

Each case names the input, what a person would expect, and the tasks whose reviewer checks the deciding sentence against it.

1. **Mixed records:** an old block with no `at:` beside a new record with `At:`. Expect a date comparison exactly as today: a same-day block is not later. **Tasks 3, 5.**
2. **`pr-draft.md` with no last-line comment, an invalid one, or a trailing blank line.** Expect today's `%cs`. A shallow repository gives "could not be dated". **Tasks 3, 4.**
3. **A release-notes file mixing drafts with and without `at:`.** Expect the signal to hold where at least one `stage: dev` draft has no later block. Expect the reason to name the latest-dated draft, and the first later block in condition 6's order. **Task 3.**
4. **A pre-4.7.0 multi-entry block whose entries carry different `at:` values, or only some carry one.** Expect no instant: it compares by its heading date. **Tasks 1, 3.**
5. **A conformance record whose `At:` date is two days from its `Run:` date.** Expect the `At:` to be ignored and the dates compared. **Tasks 2, 3, 5**, in both `ready.md` and §7.8.
6. **Equal instants.** Expect not later. **Tasks 3, 5.**
7. **The printed draft.** Expect it to omit the comment line while the file keeps the banner first and the comment last. **Task 4.**

These are prose behaviours. Each named task's reviewer checks the deciding sentence. The script-level cases have selftests in Task 1.

---

### Task 1: Enumerate the population; the block's `at:` field; the two scripts

**Files:**
- Create: `docs/superpowers/plans/2026-11-12-d50-sweep-population.md` (the sweep's recorded population; committed).
- Modify: `plugins/workflows-core/references/implementation-format.md`:
  - lines 10–11;
  - §1 at line 19, and its examples at lines 21–37 and 45–55;
  - re-read the presence test at line 61, which stays unchanged.
- Test: `plugins/workflows-core/scripts/lineage.py` selftest (around lines 1000–1040).
- Test: `plugins/workflows-core/scripts/session-branch.py` selftest, beside the `IMPL_2P` same-day cases (lines 2262–2270), which use the `esm` wrapper (line 2243).

**Interfaces:**
- Produces the population file. Task 5 re-reads every site listed in it.
- Produces `implementation-format` §1's `at:`, which Tasks 2–5 cite.

- [ ] **Step 1: Enumerate the population, before any edit.**
  - **The subject:** how `/ready` and `source-truth` §7.8 order these records, and what each record's date is.
  - **Method:**
    - Read `.claude/rules/claim-sweep.md` with the Read tool.
    - Search refinement 4's scope by subject, using refinements 6–8.
    - Start from these phrases: "carry a date and no time", "compared as written", "dated after", "dated before", "dated later", "implemented after", "implemented since", "`Run:` date", "latest `implementation.md` block", "same-day block", "dated no earlier than the latest", "its text is not read", "only line that is neither", and "first line".
  - **Seed sites:**
    - `ready.md` lines 197, 204, 205, 211–213, 215 and 917;
    - `workflow-states.md` lines 32 and 37;
    - `conformance-format.md:125`;
    - `release-note-types.md` lines 48–59;
    - `source-truth.md` lines 589 and 593;
    - `implementation-format.md` lines 10–11;
    - `.claude/rules/release-notes.md:35`;
    - `.claude/rules/dev-workflows.md` lines 37 and 71;
    - `.claude/rules/dev-workflows-conformance.md:13`;
    - the pages `dev-workflows/docs/commands/ready.md` (lines 58–68 and 101), `docs/commands/conformance.md:89`, `docs/workflow.md:75` and `docs/reference/references.md`;
    - `product-workflows/docs/workflow.md:225`;
    - `workflows-core/docs/family-map.md:193`;
    - `docs-workflows/docs/commands/release-notes.md:62`.
  - **Record** each site as `file:line — phrase` in the population file, with the count.
- [ ] **Step 2: Write the two tests.**
  - **`lineage.py`, `test_accept_after_at_field`.** `selftest()` collects every `test_*` global, so nothing needs registering.
    - Fixture: `IMPL`, with `  at:      2026-01-02T10:00:00Z\n` after the last block's `pushed:` line.
    - Run `accept(...)` as in `test_accept_into_implementation_block`.
    - Assert the earlier text is unchanged.
    - Assert the file ends with that `at:` line, then `  accepted:\n    - path: …\n      blob: …\n`.
    - Assert the read-back pins the reader: `_accepted_of(doc) == [{"path": …, "blob": …}]`.
  - **`session-branch.py`, beside the `IMPL_2P` cases.** The fixtures are `str` values passed through `esm`.
    - `split_entries` on two same-day blocks, each carrying a distinct `at:` line, returns two entries.
    - `entry_set_merge(base, ours, theirs)`, with one block added on each side, keeps both whole, each with its `at:` line.
- [ ] **Step 3: Run both selftests.** Run `python3 plugins/workflows-core/scripts/lineage.py --selftest` and `python3 plugins/workflows-core/scripts/session-branch.py --selftest`. Expected: PASS. A failure means the spec's premise is wrong: stop and report.
- [ ] **Step 4: Edit `implementation-format` §1.**
  - Define `at:` (spec §3.1 and §3.2 item 1).
  - Name its one reader: "`/dev-workflows:ready` (Phase 1 steps 2b and 2c). No other reader takes the field."
  - State the multi-entry rule.
  - Say a block written before `dev-workflows` 4.63.0 carries none.
  - Add `at:` to both examples, after `pushed:`, and in the second example before `accepted:`.
  - Lines 10–11: "dated later — by instant where both carry one, else by date". Leave §4 and §5 unchanged.
- [ ] **Step 5: Gates, plus both selftests.** Expected: PASS, 0 warnings, `EXIT=0`.
- [ ] **Step 6: Commit** with the message `feat(d50): implementation-format §1 at:; selftests pin accept and the entry-set merge; the sweep's population recorded`.

### Task 2: The writers on the dev side — `/implement`, the record format, `/conformance`

**Files:**
- Modify: `plugins/dev-workflows/commands/implement.md`, Phase 4.7, around line 1299.
- Modify: `plugins/dev-workflows/references/conformance-format.md`:
  - §2's header at line 27;
  - §6's paragraphs at lines 119–126.
- Modify: `plugins/dev-workflows/commands/conformance.md`:
  - Phase 0 step 1, around line 39, right after `strip-run-flags`;
  - Phase 5, the header write at line 392;
  - its report template, if that lists header lines.

**Interfaces:**
- Consumes Task 1's `at:`.
- Produces `conformance-format` §2's `- **At:**` and its guard.

- [ ] **Step 1: `/implement` Phase 4.7** writes `at:` into the block it appends, after `pushed:` and before any `accepted:` the same run writes. The value is `date -u +%Y-%m-%dT%H:%M:%SZ` taken at that step. Cite `implementation-format` §1. Re-read "**Beyond that field, it records refs and nothing else.**" and make it exact: it now records `at:` too.
- [ ] **Step 2: `conformance-format`.**
  - **§2:** add `- **At:** <instant>` after `Run:`, with its meaning (the run's start), the pattern, the guard and its recipe. Say a record written before `dev-workflows` 4.63.0 carries none.
  - **§6:**
    - Add `At:` to the read lists of the `/ready` paragraph and of the `/release-notes` and `/document` paragraphs. The latter two apply `source-truth` §7.8, whose rule 1 Task 5 makes compare `At:`.
    - Narrow the `/ready` paragraph's "work implemented after the record's `Run:` date leaves the stage unreached" to the pair rule.
- [ ] **Step 3: `/conformance`.**
  - Phase 0 takes the run's start instant right after `strip-run-flags` and carries it.
  - Phase 5 writes it as `At:`.
  - The report template, if it lists header lines, adds it.
- [ ] **Step 4: Check Review Focus 5** against `conformance-format` §2's guard sentence.
- [ ] **Step 5: Gates.** Expected: PASS, 0 warnings, `EXIT=0`.
- [ ] **Step 6: Commit** with the message `feat(d50): /implement writes at:, /conformance writes At: (the run's start)`.

### Task 3: `/ready` — the pair rule, steps 2b and 2c, and its pages

**Files:**
- Modify: `plugins/dev-workflows/commands/ready.md`: Phase 1 steps 2b (lines 195–207) and 2c (lines 209–215), and line 917.
- Modify: `plugins/dev-workflows/references/workflow-states.md`, lines 32 and 37.
- Modify the pages:
  - `plugins/dev-workflows/docs/commands/ready.md` (lines 58–68 and 101);
  - `docs/commands/conformance.md:89`;
  - `docs/workflow.md:75`;
  - `docs/reference/references.md`, wherever it states the rule.

**Interfaces:** consumes the four line shapes exactly as the Global Constraints give them. Task 4 writes two of them later; Task 7 checks they match.

- [ ] **Step 1: State the pair rule once,** as a paragraph that step 2b introduces and step 2c cites. It covers:
  - the pattern;
  - "invalid is no instant";
  - the multi-entry rule;
  - the guard and its recipe;
  - `[ "$a" \> "$b" ]`;
  - "equal is not later";
  - each record's fallback date (spec §3.3);
  - the clock-skew limit;
  - the two known limits, narrowed to "a pair where either record lacks an instant".
- [ ] **Step 2: Step 2b.**
  - "The read" never calls a record unreadable for an invalid `At:`.
  - Condition 6 uses the pair rule over every block in its existing order.
  - The reason names a block's unit key and heading date, plus ` at <instant>` where it has one.
  - The `Delivery:` line keeps `(checked <Run: date>)`.
- [ ] **Step 3: Step 2c.**
  - **Documentation.**
    - Read the last line with `git -C "$SPECS_PATH" show "<default-ref>:./<path>" | tail -n 1`, against `^<!-- implementation records read: ([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z) -->$`.
    - "Its text is not read" becomes "only its last line is read".
    - **No match:** test `git -C "$SPECS_PATH" rev-parse --is-shallow-repository`. Where it prints `true`, the draft could not be dated. Otherwise use today's `%cs` command. Its sentence "Where that prints no date — a shallow clone that lacks the commit" is replaced by the shallow test.
  - **Release note:** a draft's instant is its comment's `at:` line, where present.
  - **Holding.** Each signal is compared with every block. The release note holds where at least one `stage: dev` draft has no later block.
  - **The reasons:**
    - the documentation draft is named by its instant, else its `%cs`;
    - the release note names the latest-by-first-line-date draft (the last such in the file on a tie, with its instant where present), and the first block later than it in condition 6's order.
  - **Line 212's paragraph** on the scope comment's form names the `at:` line, so the form stays fully stated.
- [ ] **Step 4: Line 917, `workflow-states` lines 32 and 37, and the pages.**
  - Each states the rule in plain words.
  - The pages carry no `§`, no D-numbers and no spec or review ids.
  - "Naming the newest work it predates" becomes "the first later block in reading order".
- [ ] **Step 5: Review Focus 1–6.** For each, the deciding sentence in `ready.md` must give the expected result. Record the six sentences in the task report.
- [ ] **Step 6: Gates.** Expected: PASS, 0 warnings, `EXIT=0`.
- [ ] **Step 7: Commit** with the message `feat(d50): /ready orders records by instant where both carry one (steps 2b, 2c), pages`.

### Task 4: The writers on the docs side — the scope comment, `pr-draft.md`

**Files:**
- Modify: `plugins/docs-workflows/references/release-note-types.md` §1: the form at line 37, the prose at lines 48–59, and the one-line form at line 97, which stays a date-only record.
- Modify: `plugins/docs-workflows/commands/release-notes.md`:
  - Phase 0, right after `strip-run-flags` (around line 39);
  - the read list at line 217;
  - Phase 8 step 1 at line 668;
  - line 900, if it lists the comment's lines.
- Modify: `plugins/docs-workflows/commands/document.md`:
  - `## Mode detection`, in or directly after the **Strip the run flags first** paragraph (line 26). The instant is taken in both modes; only Mode A carries it to Phase 8.5, and Mode B never writes it. Do not touch that section's preflight or **Ending early** paragraphs.
  - Phase 3's read list near line 446, which adds `At:` for §7.8 rule 1;
  - Phase 8.5 steps 3–4 (lines 1316–1318).
- Modify: `plugins/docs-workflows/references/finish-and-handoff.md` §5.
- Modify the pages: `plugins/docs-workflows/docs/commands/release-notes.md:62` and `plugins/docs-workflows/docs/commands/document.md`, around line 70.

**Interfaces:** produces the scope comment's `at:` and `pr-draft.md`'s last line, in the Global Constraints' shapes.

- [ ] **Step 1: `release-note-types` §1.**
  - Add `at:` to the form, with its meaning (the run's start).
  - The "only line that is neither its first nor a `read:` line" sentence names `stage:` and `at:`.
  - Lines 54–59 change two ways: "the newest such draft is dated no earlier than the latest block" becomes the at-least-one-draft rule, and "a change to either line" becomes "to any of the three lines".
  - Say a draft written before `docs-workflows` 1.39.0 carries no `at:`.
- [ ] **Step 2: `/release-notes`.**
  - Take the start instant after `strip-run-flags` and carry it.
  - Phase 8 step 1 writes `at: <instant>` after `stage:`.
  - Line 217's read list adds `At:`.
  - Line 900, if it lists the comment's lines.
- [ ] **Step 3: `/document` and `finish-and-handoff` §5.**
  - **`/document`:**
    - Take the instant where the Files list says.
    - Phase 3's read list adds `At:`.
    - Phase 8.5 step 3 writes `pr-draft.md` ending with the comment line and exactly one newline, and prints the draft without that line.
    - Step 4's footers stay true: GitHub's `--body-file` hides the comment, and Bitbucket's "paste the body" pastes the printed body.
  - **`finish-and-handoff` §5:**
    - Add the last line to the draft's composition.
    - The banner, where there is one, stays first.
    - State once the limit that a raw-file paste on a host that shows HTML comments shows the line.
- [ ] **Step 4: Pages.**
  - The `release-notes` page (line 62) says the hidden scope comment also records when the run started.
  - The `/document` page (around line 70) says:
    - `pr-draft.md` ends with a hidden line recording when the run started;
    - the printed draft omits it;
    - pasting the raw file onto a host that shows HTML comments shows it.
  - The pages carry no `§` and no review ids.
- [ ] **Step 5: Review Focus 2 and 7.** Check the writer's sentences against them.
- [ ] **Step 6: Gates.** Expected: PASS, 0 warnings, `EXIT=0`.
- [ ] **Step 7: Commit** with the message `feat(d50): /release-notes writes the scope comment's at:, /document writes pr-draft.md's last line`.

### Task 5: `source-truth` §7.8, the sweep's remainder, and `to-fix`

**Files:**
- Modify: `plugins/workflows-core/references/source-truth.md` §7.8: the header-field list at line 589, and rule 1 at line 593. It has no reference parts.
- Modify: every site in Task 1's population file that Tasks 1–4 did not already change.
- Modify: `docs/superpowers/to-fix.md`.

- [ ] **Step 1: §7.8, stated in full,** since `/document` and `/release-notes` cannot load `conformance-format`:
  - the `At:` line and its meaning (the run's start);
  - the pattern;
  - "invalid is no instant";
  - the one-day guard and its recipe;
  - `[ "$a" \> "$b" ]`, equal not later;
  - the date fallback.

  Rule 1 reads: "the Epic's record carries a later `Run:`" where both carry an instant and the Epic's is later, or where either lacks one and its `Run:` date is later. Its reason becomes "the Epic run started after the PRD run started". State its limit (spec §3.3). Line 589 names `At:`. The malformed test in *The copy read* stays `Run:`-only.
- [ ] **Step 2: Review the guard and the mixed case.** Check Review Focus 5 and 6, and a mixed case, against §7.8's sentences. In the mixed case the Epic record has `At:` and the PRD record does not, so the `Run:` dates compare.
- [ ] **Step 3: The sweep's remainder.**
  - Re-read every site in the population file.
  - Narrow each one Tasks 1–4 did not reach to "where either record lacks an instant"; never remove it outright.
  - Hold `.claude/rules/dev-workflows.md` (19,953 characters) net-zero: tighten its sentence rather than add one.
  - `docs/maintainers/rationale.md:483` describes the union merge, not a `/ready` limit. No edit is expected; confirm.
  - Record the after-count against the population file's count in the task report.
- [ ] **Step 4: `to-fix.md`.**
  - Delete D50.
  - D15's entry gains the line: "**Owner:** GIT-G1 Part 3 — the maintainer handed it to that track on 2026-11-12, since its warnings belong in `phase-handoff` and `specs-repo-git`."
  - Under *Design-level — any machine*, add an entry, `SH-AT — session-hygiene could date records by their instant.` It says:
    - the resume-pointer settle rule (`session-hygiene` §1, around lines 151–168 and 223–250) dates a record by its heading day, then `git blame`;
    - the `at:` and `At:` instants from `workflows-core` 1.85.0 and `dev-workflows` 4.63.0 would make that exact where present;
    - it is an improvement, not a defect;
    - its owner is `workflows-core` `session-hygiene` and its generated part;
    - its priority is the maintainer's to schedule.
- [ ] **Step 5: Gates.** Expected: PASS, 0 warnings, `EXIT=0`.
- [ ] **Step 6: Commit** with the message `feat(d50): source-truth §7.8 rule 1 by instant; the sweep's remainder; to-fix D50 closed, SH-AT logged`.

### Task 6: Release — versions, CHANGELOGs, the coupling bullet

**Files:**
- Modify: `plugin.json` and the `.claude-plugin/marketplace.json` entry for the four plugins, and their `CHANGELOG.md` files.
- Modify: `.claude/rules/plugin-updates-coupling.md`, which is 15,752 characters.
- Modify, only if bullets move: `.claude/rules/plugin-updates-coupling-history-3.md`, the five range pointers, and `CLAUDE.md` line 115.

- [ ] **Step 1: Versions.**
  - Run `git fetch origin` and read each plugin's version on `origin/main`.
  - Where it still stands at the base in the Global Constraints, use the intended version.
  - Where `main` has moved, take the next free minor, or patch for `product-workflows`. Then grep and replace the old intended number in every file this branch changed.
  - `plugin.json` must equal `marketplace.json`.
  - Date the CHANGELOG sections with the commit's date.
- [ ] **Step 2: The coupling bullet.**
  - It names all five cases of spec §3.4, with this release's versions.
  - Add it to `plugin-updates-coupling.md` and measure.
  - **Under 19,000 characters:** done, with no pointer changes.
  - **Over:** move the oldest `workflows-core` bullets, from 1.78.14 up (the two `prose-style` bullets at the bottom stay), byte for byte, to the end of the existing `plugin-updates-coupling-history-3.md`. Then update the upper bound `1.78.13` in all five places:
    - the coupling file's intro;
    - `plugin-updates-coupling-history.md`'s intro;
    - `history-3.md`'s title and intro;
    - `plugin-updates.md:24`;
    - `CLAUDE.md` line 115.

    Check with `grep -n '1\.78\.13\|history-3' CLAUDE.md .claude/rules/*.md`.
- [ ] **Step 3: Gates.**
  - PASS, 0 warnings, `EXIT=0`.
  - Measure every rules file (under 20,000) and `CLAUDE.md` (under 36,000).
- [ ] **Step 4: Commit** with the message `release(d50): workflows-core 1.85.0, dev-workflows 4.63.0, docs-workflows 1.39.0, product-workflows 3.79.4`, or the versions Step 1 found.

### Task 7: Close — the shapes agree, the full CI list, an independent read

- [ ] **Step 1: The four line shapes agree.** For each shape (`  at:`, `- **At:**`, the scope comment's `at:`, `pr-draft.md`'s last line), `grep` its writer, its reference and `ready.md`'s reader. The shape and pattern must be identical in all three.
- [ ] **Step 2: GIT-G1 sections untouched.** In `git diff origin/main...HEAD`, no hunk may touch a GIT-G1 section or file named in the Global Constraints.
- [ ] **Step 3: The full CI list.**
  - The gates above, plus every `--selftest` that `.github/workflows/validate-catalog.yml` runs.
  - `node scripts/mermaid/check-mermaid.mjs --root .` where `node` is available. Where it is not, say so; CI runs it.
- [ ] **Step 4: An independent whole-branch review** of `git diff origin/main...HEAD`. That is the controller's final review, not an implementer step.

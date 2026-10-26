# Piece review: `/implement` reviews by piece, `/design` draws the pieces — design

**Date:** 2026-10-25 · **Plugins:** dev-workflows (`/implement`, `/design`, `code-review`, `design-reviewer`, `design-format`) · **Status:** approved by the user on 2026-10-25 · **Replaces:** part (a) of `docs/superpowers/specs/2026-10-24-implement-one-writer-design.md`, and narrows its parts (b) and (c) to the one thing kept (§5)

> **Status on 2026-10-26: built and verified** (`docs/superpowers/verification/2026-10-25-implement-piece-review.md`). One premise below did not hold: §3.2 and §4 name BOOK-1-01 as a change one reviewer can review in depth, which no one had measured. A live `/design BOOK-1-01` drew four pieces with a reason that holds under §3.2's own model — its specification carries 150 test cases against BOOK-3-01's 85 — and ruling P22 of the record finds the expectation, not the format's wording, wrong. The body stays as written, as the record of what was decided on 2026-10-25.

**Who decided what.**
- Everything marked **(Claude's call)** was decided by Claude, not the user, and is open to the user's correction. Everything else is the user's decision.
- The user chose this design ("option 1") over merging part (a), reworking it, or shelving the sub-project, after the A/B in §1.
- The user dropped two parts of the earlier design: `/specify` and `/design` becoming mandatory before `/implement`, and `/epics` turning its size cap into a warning (§5).
- A builder check (a fresh reader planning from this document) raised five questions. Four are answered in §3.1 as Claude's calls. The fifth, when `/design` draws pieces at all, the user decided: pieces need a stated reason (§3.2).

## 1. Why

**Part (a) was built and measured, and it is not being merged.**
- Branch `iv-gu/implement-one-writer` (head `ef81409a`, dev-workflows 4.32.0 and workflows-core 1.46.0, never released) gave `/implement` one long-lived code writer and one spec-driven test writer per writer unit, reached again by `SendMessage` for every fix, plus a per-piece and an overall review.
- A live A/B ran on the test Epic BOOK-3-01, from the same start state (code `6942a24`, specs `0d68eb7`) in the `ihudak-e2e` copies:
  - **Arm A**, today's dev-workflows 4.31.0: **$57.17**, 3h41m, no compaction, the main session's context peaking at 856k.
  - **Arm B**, the branch: **$99.06** (+73%), 3h52m, one auto-compaction near the end, the main session's context peaking at 964k of 1M.
- **Two blind judges** (Opus, labels swapped between them) each rated B *slightly better*, at medium confidence, with no BLOCKER or MAJOR on either side; both called a tie defensible.

**Where B's edge came from.**
- **B's extra review scopes.** Most of what the judges credited to B was found by its per-piece and overall reviews: ISBN-ordered inserts (no deadlock answered `503` where the spec says `409`), U+0000 handled, the header trim, `503` on read outages, a bound on the records kept.
- **Not from the one-writer structure.** No gain was traced to long-lived writers or to reaching them again. That structure drove most of the extra cost: each of the 12 resumes came after the 5-minute subagent cache had expired and re-cached the writer's whole context (about $13.6), and the main session took about 70 more turns.
- **Not reliably from the spec-driven test writer.** Its [U01] AC06 tests met a real database refusal where A's used a mocked writer, but it got there by departing from the design's test strategy, which prescribed the mock. It caught no code defect (both pieces' tests passed on their first run), it left many import calls without a status check where A checked every one, and splitting tests out of the coding caused two of B's three feedback defects (a shared test helper no piece review saw; a finding's "add a test" part with no route to a fixer).

**So:** keep today's coding flow, which produced equally good code most cheaply, and add the one thing the evidence supports — review scopes that follow the design's pieces.

**What the user values:** quality over cost, since poor quality costs more later; and no waste — cost that buys nothing measurable is waste.

## 2. Goals, non-goals, anti-goals

**Goals**
- Where a change spans two or more of the design's pieces, `/implement` reviews each touched piece with its own reviewer and then the whole change with an overall reviewer that sees what the piece reviewers cannot.
- `/design` draws pieces where they help review, and `design-reviewer` checks them, in the same release, so the new review reaches real runs.
- Every `/implement` review with a specification in scope asks whether the tests named after the specification's test cases and acceptance criteria would fail if the behaviour they name broke.

**Non-goals**
- The coding flow. Step groups, `code-writer`, `test-writer` from the diff, `review-fixer`, the review before the test run, the two automated fix attempts and every model choice stay exactly as in dev-workflows 4.31.0.
- Anything of the shelved branch beyond the pieces format and the review scopes: long-lived writers, `SendMessage` resumes, the lock script, the spec-driven test writer, writer units, the test run before the review.
- `/specify`, `/epics`, `/ready`, `/conformance`, `/vuln`, `/upgrade`.
- The main session's context size. A's main session peaked at 856k on this Epic; that belongs to the lean-context project. This design measures it (§4) but does not try to reduce it.
- Porting to the internal editions: `docs/superpowers/to-fix.md` E4 ports `/implement` once, after this lands.

**Anti-goals (a failure even if it works)**
- A blind judge rating the new run worse than arm A on the same inputs.
- **Any change, beyond the test-case line (§3.1 point 6), to a run whose change does not span two pieces** — a direct run, a bug run, a run whose design draws no pieces, a SIMPLE run, or a run whose diff touches one piece's files. Each gets today's review, the same dispatch save that line where a specification is in scope.
- A second coding path, or any change to who writes code or tests.
- Losing a guarantee today's `/implement` gives: the baseline before the first edit, the test-writing requirement (`.claude/rules/dev-workflows-tests.md`), the Opus review gate from `MODERATE` up, triage before any fix (`workflows-core:finding-triage`), the run-state file through `run-state.py`, the commit and secret scan, `HIGH-RISK`'s full route.
- A review loop that is not sure to end: the number of reviews a run can make is bounded (§3.1 point 5).
- Pieces drawn by count. A piece exists to focus a reviewer on a coherent part with a fixed boundary, never to keep a number small. The reason pieces need (§3.2) is a judgement about what one reviewer can review in depth, written down and checked, never a threshold.
- Pieces on a change one reviewer can review in depth: they buy reviews with nothing to find.

## 3. The design

### 3.1 `/implement`

Everything before the review is unchanged. The change is confined to the review gate — Phase 3B steps 5 to 8, which Phase 3A step 6 runs at `MODERATE` — and to the run-state keys and report lines it needs.

**1. Reading the pieces.** Where a `design.md` is in scope and has a `## Pieces` section (§3.2), the run reads it once, before the review, and records each piece's name and `Files:` patterns in run-state. No section, or `_N/A_` in its place, means one piece.

**2. Which pieces the change touches (Claude's call; the lesson of B's defect 1).**
- A piece's files are **the paths in the review diff** that match its `Files:` patterns — taken from the diff itself, never from a writer's or test writer's report.
- A path in the diff that matches no piece is *unassigned*: a shared test helper, a build file, a `CLAUDE.md` edit.
- The pattern grammar is the one `design-format` defines (§3.2).
- **A section the run cannot use** — malformed, without its `Reason:` line, two pieces' `Files:` matching one path, a piece name repeated — is read as one piece: the run makes today's single review and says so, on screen and in the report's assumptions, naming the defect. It asks nothing (Claude's call). `design-reviewer` refuses such a section in a design `/design` writes (§3.2), but a design written by hand or before this release can carry one.

**3. When the review splits (Claude's call).**
- The review splits only where the diff touches the files of **two or more** pieces.
- Otherwise — no pieces, or a diff that touches one piece's files or none — the run makes today's single review, unchanged (§2 anti-goals). That keeps a small follow-up run on a pieced Epic (a `/security-workflows:scan` fix, a `/conformance` follow-up) at one review.

**4. The split review.**
- **One `code-review` per touched piece, dispatched in parallel** (reviewers only read). Each gets today's brief, with its scope narrowed: the piece's name, its files in the diff, its `Contract:` items, and the instruction to review those files in depth and to read others only to understand them. Each reviews its piece's tests with it, since `Files:` covers tests (§3.2).
- **Conformance (Claude's call, as the shelved branch had it for the specification).** A piece review gets the specification and the ARD invariants to read. It reports an `[AD#N]` violation in its own files (`code-review`'s ARD dimension) and applies the test-case line (point 6) to its own tests, but makes no requirement trace: the specification-conformance dimension — coverage verdicts, `missing`, `contradicts`, `exceeds` — is the overall review's alone, and it alone feeds step 7.5's notes and run-state `conformance`, as the single review does today. So no requirement is traced more than once, and no piece review writes a false `missing` for a requirement another piece implements.
- **Then one overall `code-review`**, after the piece reviews return. It gets today's brief over the whole diff, the piece reviews' returns as they came back, and a scope that says what only it can see:
  - where the pieces meet: the `Contract:` items, used consistently on both sides;
  - duplicated helpers and inconsistent conventions across pieces;
  - behaviour that spans pieces (B's `published` finding is the example: the parser's draft and the writer's update together decided it);
  - every unassigned file, reviewed in depth.

  It does not repeat a finding a piece review made (Claude's call).
- Every review runs on the review model as today (`workflows-core:model-routing/classification`), and every return is written to its own file before it is read, as today's step 7 writes one.

**5. Triage, fixes and re-review (Claude's call).**
- **The verdict of the split review is the worst of its scopes' verdicts:** `BLOCK` if any scope blocks, else `PASS WITH RECOMMENDATIONS` if any scope recommends, else `PASS`. Today's arms, settle prompts and offers act on that one verdict.
- **Triage runs once, over every scope's findings together**, under `workflows-core:finding-triage` unchanged. A finding two scopes both made is one finding.
- **One `review-fixer` pass** takes every survivor today's rules hand a fixer, from all scopes, exactly as today's one pass does.
- **The re-review** — wherever today's rules allow or offer one — re-runs each piece review whose files the fixer changed, and each piece review that handed the fixer a finding, then the overall review. It is triaged under `finding-triage`'s *On re-review*, as today. (Corrected while building, on the final review's finding: the first version re-ran only the pieces whose files changed, so a piece's `BLOCKER` fixed only at its `also at` site in another piece, or claimed fixed with no edit, was re-checked by no review, and the stayed-blocked stop today's single re-review gives was lost.)
- **The review after the Phase 3.5 fixes** (today's step 8) is today's single review, unsplit and unchanged, over what step 8 gives it today — the whole change, not only the fixes (Claude's call). A scoped review there would look at a fix inside a piece's files less deeply than today's does.
- **The bound.** A run makes at most: the first split review (pieces + 1), one re-review (pieces + 1), and step 8's one review. No new loop is added.

**6. The new line in every review brief (Claude's call; the user accepted it in conversation).** Wherever a specification is in scope, every `code-review` brief `/implement` writes — split or not, step 8's included — asks: *for each test named after a specification test case or acceptance criterion, would it fail if the behaviour it names broke?* A test whose assertions hold whatever the code does — a double standing in for the very behaviour under test, an assertion on a value the test itself set — is a finding, graded by its effect. This is the check that would have caught A's AC06 tests (`U01_AC06_TC01` to `TC03`); neither run's reviews did, only the judges.
- It is `/implement`'s brief that carries it, never `code-review`'s own dimensions, so `/vuln` and `/upgrade`, which pass no specification, are unchanged.
- It is the one change an unsplit run sees. No live run is added for it: Run C carries it, and the rule-by-rule reading covers the unsplit path (Claude's call).

**7. The report.** The Phase 5 report names the scopes reviewed and each one's verdict, so a reader can see which reviewer found what. The run's cost section counts every review as today. The implementation record is unchanged: `workflows-core:implementation-format` keeps it to refs, never a summary (corrected while planning; the first version of this document also put the scopes there).

### 3.2 The pieces section, `/design` and `design-reviewer`

**The format** goes into `dev-workflows:design-format` as an optional section, taken from the shelved branch's text (`git show ef81409a:plugins/dev-workflows/references/design-format.md`, its `## Pieces` item) without the parts about writers:

```
## Pieces
Reason: <why one reviewer could not review the whole change in depth>
### <piece-name>
- Files: `<path or glob>`, …
- Contract: <the `## Interfaces / contracts` items it provides or uses> | none
```

- **Pieces need both a reason and a boundary (the user's decision).**
  - **Whether to split — the `Reason:` line.** It says why one reviewer could not review the whole change in depth: its size, the number of distinct layers or concerns, the test cases it carries. BOOK-3-01's is the model: about 1,500 lines of production code in two layers with different test styles, carrying 85 test cases. A change one reviewer can review in depth gets no pieces, however clean its internal boundaries (BOOK-1-01).
  - **Where to split — the boundary.** The pieces' `Files:` do not overlap, and the part they share is fixed in `## Interfaces / contracts` and named in `Contract:`. A big change with no such boundary stays one piece, reviewed as today, since a piece reviewer cut off at a fuzzy line misses what it needs.
- **Dropped from the branch's format:** the `Writers:` line, replaced by `Reason:`, and each piece's `Builds after:` line. Both existed for separate writers, which this design does not have.
- **`/implement` does not judge the reason.** A section without a `Reason:` line is one it cannot use (§3.1 point 2).
- **`Files:` names the piece's tests as well as its code** (Claude's call), so a piece reviewer reviews the tests of its piece. A test file shared by pieces is named by none and goes to the overall review.
- **Kept from the branch:** a piece is a unit of review; pieces are drawn only when there are two or more, only where their file sets do not overlap, and only where the design fixes the part they share in `## Interfaces / contracts`; never by count. One piece is written by omitting the section or writing `_N/A — <why>_`. Names are kebab-case and unique. No file may be matched by two pieces' `Files:`.
- **A file no piece names** is reviewed by the overall review. It is not barred from editing: today's coding flow has no file ownership, and this design adds none (Claude's call; the branch's rule that such a file "is not this Epic's to edit" belonged to writer units).

**`/design` draws the pieces** when it writes `design.md`, under the rules above, with the reason thought through and written down. It asks the user nothing new: drawing pieces is a design decision the grill may raise like any other (Claude's call).

**`design-reviewer` checks the section** and can push back either way:
- **The reason:** a `Reason:` that does not hold — a change one reviewer could review in depth — is a finding to drop the pieces. So is a section without one.
- **The boundary:** overlapping `Files:`, a shared part not fixed in `## Interfaces / contracts`, a piece whose files depend on another's internals, a `Contract:` item the contracts section does not define, and tests left out of every piece's `Files:` where they are not shared.
- **A design with no pieces** for a change that plainly needs them is a recommendation, never a BLOCKER: one review is today's behaviour, never a defect (Claude's call).

**Dropped from the earlier design's part (b):** `/specify` and `/design` becoming mandatory, and the widened *Re-split* exit (the user's decision, §5).

## 4. Proof

The quality bar of lean context parts 1 and D: a blind judge compares live runs on the same inputs, Claude reads the old and new instructions rule by rule, cost is measured, a worse result is a defect.

**Run C: `/implement BOOK-3-01`** on the new release, in the `ihudak-e2e` copies, from code `6942a24`.
- **Its one changed input (Claude's call):** the test Epic's hand-written `## Pieces` section is rewritten to the new format — its `Writers:` line becoming a `Reason:` line that keeps the same facts, written about reviewing rather than writing, each `Builds after:` line removed, and each piece's test package added to its `Files:` — as one commit on the specs copy, which becomes the run's specs start. Nothing else in `design.md` changes. Arm A's run read the same design with the old section, which 4.31.0 ignores.
- **Before the run,** the rewritten section is matched against arm A's diff paths with the release's own matching, to show it parses and splits as intended — so the run cannot fall back to one piece unnoticed (point 2's fallback).
- **Judged against arm A** by two blind judges, labels swapped between them, with arm A's recorded tree (`~/e2e-live/one-writer/A/`). Pass: neither judge rates C worse than A.
- **Judged against arm B** too, by one blind judge, to see whether C kept B's edge. Informative, not a gate (Claude's call).
- **A close verdict is repeated before it is believed** (the user's decision for the whole sub-project).
- **Measured:** total cost, cost by agent type, review cost by scope, the main session's turns and peak context, and any compaction. The expectation is about A's cost plus $10–15, about $67–72. A run over $80 is a finding to explain before release (Claude's call).

**Two `/design` runs**, with the setup left to the builder:
- **BOOK-3-01** from its specification, without the hand-written design: it should draw two pieces at the parser contract, or a defensible alternative that `design-reviewer` passes.
- **An Epic that should get one piece** (`BOOK-1-01`, baseline `c78ffdb`, is the earlier design's candidate): it should draw none.

**Gates:** the chain in `.github/workflows/validate-catalog.yml` passes; the verification record is written last.

## 5. What happens to the earlier design and branch

- **`2026-10-24-implement-one-writer-design.md`** gets a status note at its top: part (a) is replaced by this design, after the A/B in §1; part (b) is narrowed to `/design` drawing pieces, which this design carries; part (c) and part (b)'s mandatory gates are dropped. Its body stays as written, as the record of what was decided then.
- **Why (c) and the mandatory gates are dropped (the user's decision, on Claude's recommendation).** Both rested on one writer being able to hold a big Epic and fix its own work from its own context. That premise did not survive the A/B. And A's main session already peaked at 856k of 1M on this Epic, so bigger Epics would compact mid-run under today's flow.
- **The branch `iv-gu/implement-one-writer`** stays unmerged and unpushed. Its A/B results, measurements and SDD rulings are preserved in `docs/superpowers/verification/2026-10-24-implement-one-writer-a.md`, with the SDD ledger, before its SDD workspace is deleted. Whether to keep the branch itself is the user's to decide when that record is written.
- **A finding for `/design`'s test strategy** goes into `docs/superpowers/to-fix.md`: the BOOK-3-01 design prescribed a mocked writer for a criterion about rollback, so a test that follows the design holds trivially. One instance, recorded, not ruled on.

## 6. Constraints

- `CLAUDE.md` § Editing discipline and § Hard constraints bind every edit: prose is executed; the claim-expiry sweep (`.claude/rules/claim-sweep.md`) over every statement that `/implement` makes exactly one review, and every statement of how the pieces section is used; one source of truth per authority; `choices:` arrays verbatim; the docs tree for every changed command, agent and reference; a dated `CHANGELOG.md` section; the 1024-character descriptions.
- `workflows-core:finding-triage` stays the authority on triage. Combining the scopes' findings is `/implement`'s own step, before triage; where it needs a change in the shared reference, `.claude/rules/plugin-updates.md` gets the coupling bullet.
- The gate chain passes before each push.
- Work happens in a worktree, never by `git checkout` in the shared checkout.
- The verification record is written last; the SDD rulings and ledger are preserved under `docs/superpowers/verification/` before the workspace goes.

## 7. Left to the builder

- Where the scoped briefs and the overall brief live (in `implement.md`, in `code-review.md`, or a handoff file), and their wording.
- The run-state keys for pieces, scopes and their return files.
- How the pattern match of `Files:` against the diff's paths is done (a script, or `git`'s own pathspec matching), provided it is deterministic and the same on macOS and Linux.
- How much of the shelved branch's Phase 3.6 text, `design-reviewer` text and `design-format` text is reused.
- Versions, changelogs, coupling bullets and docs pages.
- The setup of the two `/design` runs.

# Piece review — verification record

## 1. What was built

Piece review is dev-workflows 4.32.0. Where a `design.md` draws pieces in a `## Pieces` section with a `Reason:` line, and the change its first review sees touches two or more of them, on a run its review gate reviews (`MODERATE` and up) that is no companion run, `/dev-workflows:implement` reviews each touched piece with its own `code-review`, in parallel, then the whole change with one overall `code-review`; triage, the `review-fixer` pass and the re-review act on the round as a whole. `/dev-workflows:design` draws the pieces, `design-reviewer` checks them, `scripts/pieces.py` parses the section and assigns a diff's paths to pieces, `run-state.py` gains the keys `pieces` and `reviews`, and every review brief that carries `applicable_spec` gains a `Spec-named tests:` line, split or not. It replaced part (a) of "one writer per Epic", which was built, measured and shelved (`docs/superpowers/verification/2026-10-24-implement-one-writer-a.md`). The design is `docs/superpowers/specs/2026-10-25-implement-piece-review-design.md` (approved 2026-10-25, corrected in `94edfa64` and `0a9216d3`) and the plan `docs/superpowers/plans/2026-10-25-implement-piece-review.md`. The work is on branch `iv-gu/implement-piece-review` in the worktree `/workspace/.worktrees/implement-piece-review`, from `main` at `94edfa64`, and is not yet merged. workflows-core is unchanged (`git diff --stat 94edfa64..HEAD -- plugins/workflows-core` prints nothing), and 4.32.0 runs beside workflows-core 1.45.0, as 4.31.0 does.

Each task's commits, from the ledger's `Task <N>: complete` and `Final review` lines, checked against `git -C /workspace/.worktrees/implement-piece-review log --oneline 94edfa64..HEAD`:
- **Task 1**, `pieces.py` (parse a design's `## Pieces`, assign a diff's paths): `94edfa64..f7b32cd2`, one commit; review clean.
- **Task 2**, the format in `design-format`, `/design` drawing pieces and `design-reviewer` checking them: `f7b32cd2..c9c7dde4`, one commit; review clean, its seven deferred minors left to Task 6 (P6).
- **Task 3**, the run-state keys `pieces` and `reviews`: `c9c7dde4..dd89b919`, one commit; review clean.
- **Task 4**, `code-review`'s `Scope`, `Piece reviews` and `Spec-named tests` inputs: `dd89b919..fb5ae0f4` — `3cf4e4a2`, the P7 amendment `5ca2d656`, and the P8 fix round `fb5ae0f4`.
- **Task 5**, `/implement`'s split review: `fb5ae0f4..39ed901e` — `be6c8dee`, then two fix rounds, `c8c0fd07` and `39ed901e`.
- **Task 6**, the report, invariants, docs, rules and the claim sweep: `39ed901e..5e16bbc6` — `3cdf0b73`, `b66f05d6` and `869eb94c`, then two fix rounds, `99c91140` and `5e16bbc6`.
- **Final review**, over `94edfa64..5e16bbc6`: one Important finding and six Minors. Its fix wave is `5e16bbc6..6edd7c6b`: the fixer's `7b5834e8` and `3c2b874c`, the controller's `0a9216d3` (the design's §3.1 point 5 amended to P16), and `6edd7c6b`, the P18 residuals.
- **Records after the code:** `2fde56ef` (part (a)'s record and its ledger, to-fix's E4 row and L2, the rationale's run C paragraph) and `7c436653` (to-fix PR1). Tasks 7 and 8 committed nothing to this repository; their records are under `~/e2e-live/one-writer/` on the maintainer's machine. This record is committed with four more edits: the 4.32.0 CHANGELOG intro's measured cost, to-fix PR2, the rationale's paragraph on the two `/design` runs, and a status note at the top of the design.

The branch's whole diff (`git diff --stat 94edfa64..HEAD`) is 22 files, +1,246 −61; under `plugins/`, 13 files, +773 −53.

## 2. Expected values, re-derived

Every value below was measured on 2026-10-26 against the worktree at HEAD `7c436653`, the three uncommitted edits included, by running the command beside it from the worktree's top level.

| Value | Command | Result | What the ledger recorded |
|---|---|---|---|
| `pieces.py` selftest | `python3 plugins/dev-workflows/scripts/pieces.py --selftest` | PASS (52 checks) | 52, after P18 |
| `run-state.py` selftest | `python3 plugins/dev-workflows/scripts/run-state.py --selftest` | PASS (97 checks) | 97, from Task 3 on |
| `implement.md` at the base | `git show 94edfa64:plugins/dev-workflows/commands/implement.md \| wc -c` | 326,520 bytes | 326,520 |
| `implement.md` at HEAD | `git show HEAD:plugins/dev-workflows/commands/implement.md \| wc -c`, and `wc -c` on the working file | 336,284 bytes: +9,764, +2.99% | 336,284 |
| The plan's cap | the base plus 12,000 | 338,520; HEAD is 2,236 under it | 338,520 |
| The gate chain | `bash <scratchpad>/gates.sh > <scratchpad>/gates-9b.log 2>&1; echo EXIT=$?` | `EXIT=0`, run before this file existed and again with it in place | `EXIT=0` after every task |

Both selftests print a count of checks; neither prints a count of cases. The gate script, kept in the controller session's scratchpad, is the `run:` steps of `.github/workflows/validate-catalog.yml` as one `&&` chain, in order, run from the worktree.

**How each number moved, by commit.** Each commit's script was run from a scratch copy (`git show <commit>:<path>`); `run-state.py` with that commit's `implement.md` beside it in a `commands/` directory, since one of its checks compares `implement.md`'s quoted `KEYS` line with the script's own and runs only where it finds the file (without it every count below is one lower: 90 at the base, 96 from `dd89b919` on). Sizes are `git show <commit>:plugins/dev-workflows/commands/implement.md | wc -c`.

| Commit | Task | `pieces.py` checks | `run-state.py` checks | `implement.md` bytes | Ledger |
|---|---|---|---|---|---|
| `94edfa64` | base | no script | 91 | 326,520 | 326,520 |
| `f7b32cd2` | 1 | 37 | 91 | 326,520 | 37 checks |
| `c9c7dde4` | 2 | 37 | 91 | 326,520 | |
| `dd89b919` | 3 | 37 | 97 | 327,613 | 97 checks; 327,613 |
| `be6c8dee` | 5 | 37 | 97 | 334,082 | 334,082 |
| `c8c0fd07` | 5, fix round 1 | 37 | 97 | 334,380 | 334,380 |
| `39ed901e` | 5, fix round 2 | 37 | 97 | 334,477 | 334,477 |
| `b66f05d6`, `869eb94c` | 6 | 37 | 97 | 335,665 | 335,665 |
| `99c91140` | 6, fix round 1 | 37 | 97 | 335,719 | 335,719 |
| `5e16bbc6` | 6, fix round 2 | 37 | 97 | 335,734 | 335,734 |
| `7b5834e8` | final fix wave | 51 | 97 | 335,734 | |
| `3c2b874c` | final fix wave | 51 | 97 | 336,284 | 51 checks; 336,284 |
| `6edd7c6b` | P18 | 52 | 97 | 336,284 | 52 checks; "untouched 336284" |
| `2fde56ef`, `7c436653` | records | 52 | 97 | 336,284 | |

No number differs from what the ledger recorded at the time. `pieces.py`'s count moved twice: `7b5834e8` (37 to 51) pinned each documented malformed case, and `6edd7c6b` (51 to 52) a `Files:` line with no entry. `run-state.py`'s moved once, at `dd89b919` (91 to 97), Task 3's keys. `implement.md` grew in Tasks 3, 5 and 6 and in the final fix wave, and not after `3c2b874c`.

**Run C's split check, re-derived.** Before run C the controller ran `pieces.py assign` on the rewritten design (specs `24a1cbc`) over arm A's paths and saved the output as `C/split-check.json`, before the final fix wave changed `pieces.py`. Re-run with HEAD's script — the design read with `git -C /workspace/e2e/bookstore-specs show 24a1cbc:<design.md>`, the paths with `git -C /workspace/e2e/bookstore diff --name-only -z --no-renames 6942a24 5e0c6c0` (36 paths) — it returns the same JSON object: `status: pieces`, no defect, `split: true`, `csv-catalogue` 14 paths, `import-runs` 20, and unassigned `CLAUDE.md` and `…/imports/TestIsbns.java`.

**The two `/design` runs' sections, re-parsed.** `pieces.py parse` at HEAD on each run's recorded `design.md` returns `status: pieces` with no defect: two pieces for BOOK-3-01, four for BOOK-1-01. `pieces.py assign` over each run's scanned code tree (`git -C /workspace/e2e/bookstore ls-tree -r -z --name-only <commit>`, at `6942a24` and `af46545`) finds no overlap; it cannot see the files either design creates, the limit P17 records for M3.

## 3. Run C — `/implement BOOK-3-01` on 4.32.0

**Sources.** The figures are quoted from the run records under `~/e2e-live/one-writer/`, outside this repository: `C/measure.txt` (cost, cache reads, main-session calls and context, compactions, the questions and the seconds each waited), `C/per-agent.txt` (cost per dispatch and per agent type), `C/agents.txt`, `C/main-results.txt`, `C/run.txt`, `C/code-stat.txt`, `C/final-report.txt`, `C/reviews.txt` (the six review returns) and `C/specs-session.diff`, with `runs.log`; arms A and B from `A/` and `B/` (`measure.txt`, `per-agent.txt`) and part (a)'s record. Where a figure is the ledger's, the text says so.

**Setup.**
- **The start state.** Code `6942a24`, as for arms A and B. Specs `24a1cbc`: A's and B's start, `0d68eb7`, with one commit rewriting the test Epic's hand-written `## Pieces` to the new format — its `Writers:` line becoming a `Reason:` line (about 1,300–1,600 lines of production code, at least as much test code, 85 specification test cases, two halves independent in layer and test style that meet only at the four parser types), each `Builds after:` line removed, and each piece's test package added to its `Files:`. Nothing else in `design.md` changed. The run script started from `a6346da`, its restore commit, whose tree is `24a1cbc`'s (`git rev-parse a6346da^{tree} 24a1cbc^{tree}` prints one tree id twice), as B's `8bc8dda` was for `0d68eb7`.
- **Launch.** The controller added arm C to `run-epic.sh` (`E2E_PLUGIN_SRC` set to the worktree's `plugins/`, `SPECS_START=24a1cbc`); the user launched it at 06:44:05Z (`runs.log`) and ran `/dev-workflows:implement BOOK-3-01`, answering as arms A and B were answered.
- **The run.** Session `48f8f661`; code commit `686058c` on `feat/BOOK-3-01-books-csv-catalogue-import`, not pushed; specs commit `d899b81`, pushed. Classified `SIGNIFICANT`, it coded in six step groups, each a fresh Opus `code-writer`, wrote tests with one Sonnet `test-writer` from the diff, then reviewed.

**What the split did.**
- **The split.** Step 5's `assign` returned `split: true`. Two piece reviews ran in parallel — `csv-catalogue` over 14 files (9 production files and 5 test files under `…/imports/csv/`) and `import-runs` over 18 (8 production files and 8 test classes under `…/imports/run/`, `BookRepository` and `application.properties`) — then the overall review (ledger; each review's own summary). The report's scope line counts 0 files only the overall review saw, where the pre-run check over A's paths had 2: C's diff held no `TestIsbns.java` (its shared fixture, `CatalogueFixtures`, sits in the csv test package, which `csv-catalogue` names), and its `CLAUDE.md` line was added in Phase 4, after the review.
- **Round 1.** One triage over the three returns: every finding survived. The first `review-fixer` pass took the survivors and the six NITs the user chose to apply ("Apply them (Recommended)"), applied 13 and deferred 2, one of them a plan conflict. The user ruled it "Revise the plan (the finding governs)" — concurrency failures answer 409 — and a second pass applied that.
- **The re-review round.** The user took the unspent re-review. All three scopes ran again, since each piece's first-round review had handed the fixer a finding (P16). Triage kept every finding but one, dismissing a carried one. The user chose "Apply them (Recommended)" for the 10 edit-only findings left; a third pass applied 9 and deferred 1, `U01_AC06_TC01`, as a plan conflict, with no ruling asked since no review follows.
- **Verdicts.** Every scope in both rounds returned PASS WITH RECOMMENDATIONS, and no review raised a BLOCKER or a MAJOR (counted in `reviews.txt`).

| Scope | First round: findings | First round: cost | Re-review: findings | Re-review: cost |
|---|---|---|---|---|
| `csv-catalogue` | 5: 2 MINOR, 3 NIT | $1.93 | 2: 2 MINOR | $2.13 |
| `import-runs` | 9: 6 MINOR, 3 NIT | $3.85 | 7: 5 MINOR, 2 NIT (1 carried) | $4.24 |
| overall | 3: 1 MINOR, 2 NIT | $3.14 | 3: 2 MINOR, 1 NIT (1 dismissed) | $3.18 |
| The round | 17 | $8.92 | 12 | $9.55 |

Arm A's one review cost $4.37 and its re-review $3.49. The scope costs sum to $18.47, against the type total's $18.48, by rounding.

**The `Spec-named tests:` line.** The `import-runs` piece review's first-round MINOR found that `U01_AC06_TC01` and `U01_AC06_TC02` stub `CatalogueWriter.apply` to throw before it runs, so their "no book changed" checks hold whatever the writer does; A's single review did not flag the same pattern in A's tests (ledger). After pass 1, `U01_AC06_TC02` meets a real refusal on H2 (the overall re-review). The `import-runs` re-review raised `U01_AC06_TC01` again, and pass 3 deferred it as a plan conflict with the hand-written `design.md:306` and `:371`, which prescribe a `CatalogueWriter` mock for AC06 TC01–TC02 (section 5, the mock question). The `csv-catalogue` review found every spec-named test of its piece running the real parser with no doubles; the overall review had no file of its own to check.

**What the user answered** (`measure.txt`, the final report): Plan (486 s), approved. Branch (168 s). Open NITs (263 s), "Apply them (Recommended)". Plan ruling (345 s), "Revise the plan (the finding governs)". Re-review (154 s), made. Open findings (1,984 s), "Apply them (Recommended)". Push / PR (131 s), not pushed. Follow-ups (84 s), one follow-up written: push the branch and open its pull request.

**Results.**

| | Arm A, 4.31.0 | Arm B, part (a) | Run C, 4.32.0 |
|---|---|---|---|
| Total cost | $57.17 | $99.06 | $84.51 (+48% over A) |
| Main session alone | $25.94 | $41.03 | $35.37 |
| Subagents | $31.23 | $58.03 | $49.14 |
| Cache reads, whole run | 111.4M | 196.4M | 161.3M |
| Cache reads, main session | 81.0M | 137.0M | 110.3M |
| Main-session calls | 153 | 223 | 189 |
| Main context, first call | 183k | 184k | 186k |
| Main context, median | 535k | 661k | 589k |
| Main context, peak | 856k | 964k | 969k |
| Compactions | 0 | 1, at 17:14 | 1, summarised at 10:52:40, during `commit-artifacts` after the final report |
| Wall time (ledgers) | 3h41m | 3h52m | 4h09m |
| User wait (the questions' waits summed) | 4,033 s over 6 questions | 3,739 s over 8 | 3,615 s over 8 |
| Subagent dispatches | 21 | 21 | 27 |
| Files changed, insertions | 36, +4,161 | 33, +4,350 | 34, +4,515 |
| New tests | 125 | 161 | 135 |
| Tests passing at the end | 191: Gradle 134, web 57 | 227: Gradle 170, web 57 | 201: Gradle 144, web 57 |
| Review verdicts | PASS WITH RECOMMENDATIONS, both rounds | PASS WITH RECOMMENDATIONS, every scope, both rounds | PASS WITH RECOMMENDATIONS, every scope, both rounds |
| Conformance, by its own review | 126 satisfied, 0 exceeds | 126 satisfied, 3 exceeds | 126 satisfied in the first round; the overall re-review counted 41 (stories and criteria only), 1 exceeds |

The table quotes each run's `measure.txt`, over its whole window; the wall times are the ledgers', and from `runs.log`'s start to the end of each measured window they come to 3h41m18s, 3h51m30s and 4h09m44s. C's own cost entry (`specs-session.diff`), written at 10:52:12Z, before its last turns (the window ends at 10:53:49Z), records $80.93 computed and a duration of 14,877 s. C's new tests are the 135 Gradle tests beyond the baseline's 9 (the final report).

**Cost by agent type, C against A** (`per-agent.txt`, dispatches from `agents.txt`):

| Agent type | A: dispatches | A: cost | C: dispatches | C: cost | C − A |
|---|---|---|---|---|---|
| `code-review` | 2 | $7.86 | 6 | $18.48 | +$10.62 |
| `code-writer` | 7 | $14.76 | 6 | $16.80 | +$2.04 |
| `review-fixer` | 2 | $3.21 | 3 | $8.73 | +$5.52 |
| `risk-planner` | 1 | $3.67 | 1 | $3.25 | −$0.42 |
| `test-baseliner` | 2 | $0.58 | 2 | $0.54 | −$0.04 |
| `code-scanner` | 2 | $0.33 | 4 | $0.50 | +$0.17 |
| `test-writer` | 1, Sonnet | $0.34 | 1, Sonnet | $0.39 | +$0.05 |
| `general-purpose` (post-run reviews) | 3 | $0.41 | 3 | $0.39 | −$0.02 |
| `impl-maintenance` | 1 | $0.06 | 1 | $0.06 | $0.00 |
| All subagents | 21 | $31.23 | 27 | $49.14 | +$17.91 |
| Main session | | $25.94 | | $35.37 | +$9.43 |

C's three `review-fixer` passes cost $4.72 (the first round's survivors), $0.47 (the plan ruling) and $3.54 (the user-applied pass after the re-review).

**The expected cost and the finding.** The design (§4) expected about A's cost plus $10–15, about $67–72, and made a run over $80 a finding to explain before release. C cost $84.51, $27.34 over A and $14.55 under B. The delta splits, re-derived from the table above, into the reviews +$10.62, the main session +$9.43, the fixers +$5.52, the writers +$2.04 and the rest −$0.26; the parts sum to $27.35 against the totals' $27.34, the per-type figures being rounded. The reviews' share is what the design expected. The ledger explains the two parts it did not expect. About half the main session's extra was the split round's triage and bookkeeping turns — 18.7M cache-read tokens in the first round against A's 8.2M, and 8.9M in the re-review against 3.7M — and the rest carried context and run-to-run variance. The fixers acted on more findings: 13 applied in the first pass against A's 6, and 9 user-applied against 2.

**The user's decision** (ledger, 2026-10-26 11:30): "agreed, ship it" — the cost finding is recorded, not optimised in this release. The 4.32.0 CHANGELOG intro states the measured cost.

**C's feedback.** The run wrote two entries to the Epic's feedback file (`specs-session.diff`): a file-writing tool that expanded `\uXXXX` escapes in Java sources, which agents repaired by hand, and a bare `cd` outside a subshell during Phase 1. Neither concerns the split review, and the ledger records neither.

## 4. The judges

**Method** (ledger; plan Task 7 step 6). Five blind Opus judges each compared two arms' trees against the Epic's documents under neutral labels X and Y, with commit messages stripped of the `Review:` paragraph and `Co-Authored-By` on every side; the mapping stayed outside their inputs, in `blind-mapping-C.txt`. The first pair judged C against A with the labels swapped between them. Both of its verdicts were "slightly", so the design's rule that a close verdict is repeated before it is believed (§4), as plan Task 7 step 6 applies it, sent a second pair to the same trees, judge 4 with judge 1's labels and judge 5 with judge 2's. Judge 3 judged C against B, informative and not a gate. No judge ran a build or a test: each traced code paths.

| | Judge 1 | Judge 2 | Judge 4 | Judge 5 | Judge 3 |
|---|---|---|---|---|---|
| File | `verdict-C-1.md` | `verdict-C-2.md` | `verdict-C-4.md` | `verdict-C-5.md` | `verdict-C-3-vsB.md` |
| Labels | X = A, Y = C | X = C, Y = A | X = A, Y = C | X = C, Y = A | X = C, Y = B |
| Verdict | "Y slightly better", that is C | "X slightly better", that is C | "Y slightly better", that is C | "X slightly better", that is C | "X slightly better", that is C |
| Confidence | low | low | medium | medium | medium |
| C: BLOCKER / MAJOR / MINOR / NIT | 0 / 0 / 1 / 3 | 0 / 0 / 1 / 4 | 0 / 0 / 1 / 2 | 0 / 0 / 1 / 3 | 0 / 0 / 1 / 1 |
| Other side: BLOCKER / MAJOR / MINOR / NIT | A: 0 / 0 / 1 / 2 | A: 0 / 0 / 1 / 1 | A: 0 / 0 / 1 / 1 | A: 0 / 0 / 1 / 3 | B: 0 / 0 / 1 / 2 |
| Shared defects | 2 NITs, listed apart | none | none at MINOR or above | 1 NIT, counted on each side | none at MINOR or above |

The counts are the defects each judge listed under each side. Judge 1's two shared NITs (`source` measured after trimming; an invalid ISBN reported cut to 32 characters) and judge 5's one (the same cut) are both design choices.

**The two MINORs.** Every judge found the same MINOR in C: with the database unreachable, the import's security hooks read the `configs` table before anything is caught, so the client gets `500` where `[U01] AC07` and the design's error table give `503`. Every C-against-A judge found A's MINOR in one place: a U+0000 in a value on PostgreSQL is answered with a false duplicate-ISBN `409 CONFLICT`, or a `503` with nothing recorded, since A maps every `DataIntegrityViolationException` to `CONFLICT`, a mapping one of A's own tests pins (judge 1 counted the mapping as a NIT of its own). Judge 4 noted that A follows the design's data flow there and C the specification.

**The deciding differences each named.**
- **Judge 1:** (1) classifying a refused write — C answers `CONFLICT` only for a real unique violation, A for every integrity refusal; for C. (2) a whole-database outage — A answers `503`, C `500`; for A. (3) how hard the failure-path tests pin behaviour — C's `U01_AC06_TC02` exercises a real rollback, its read-backs compare whole reports, and it proves the max-rows key is read; for C.
- **Judge 2:** (1) write-failure classification — C sends only SQLSTATE 23505 to `409`; for C. (2) input PostgreSQL cannot store — C neutralises U+0000, A answers a misleading `409` or a report-less `503`; for C. (3) a database outage at the door; for A. Its one-query listing and whole-report read-backs also leaned to C.
- **Judge 4:** (1) classifying failed writes; for C. (2) a database down when the request starts; A's one clear advantage. (3) the strength of the tests — whole-report read-backs, `[U01] AC06 TC02` run as the specification describes, the configuration key and the security block tested; for C.
- **Judge 5:** (1) write-failure classification; for C, with A's `503` on an outage as the counterweight. (2) how hard the tests pin all-or-nothing and the recorded report; for C. (3) robustness on unusual input and load — bounded parser memory, one-query listing, NUL bytes; for C, with A's character-accurate `source` length as the counterweight.
- **Judge 3, C against B:** (1) the `published` column on update — C keeps the design's `BookDraft` contract, B changed it; for C. (2) database-down handling — B answers `503`, C `500`; for B. (3) test rigour — C asserts statuses and exact problem lists nearly everywhere, B has the better AC06 race test but leaves many statuses unasserted; for C.

**The outcome.** All four C-against-A judges rated C slightly better, two at low confidence and two at medium, with no BLOCKER or MAJOR on either side. The two pairs agree, so the live run was not repeated, and the Task 7 gate (no judge rates C worse than A) passed. Judge 3 rated C slightly better than B too: C keeps the design's contract and pins the specification more tightly, while B's concurrent-create race test and its `503` on a database outage are better.

## 5. Task 8 — two `/design` runs

**Sources.** `~/e2e-live/one-writer/design-BOOK-3-01/` and `design-BOOK-1-01/` (`design.md`, `measure.txt`, `specs-stat.txt`, `specs-session.diff`, and each session's transcript, from which the `design-reviewer` returns and the Pieces question are read), `runs.log`, `run-design.sh` and the ledger. Both runs loaded the worktree's plugins through `E2E_PLUGIN_SRC`, with `ARCHITECTURE_REPO_PATH` an empty directory, as in the earlier baseline.

| | BOOK-3-01 | BOOK-1-01 |
|---|---|---|
| Start | code `6942a24` (`master`); specs `1ae4cd5` on `main`, the tree of `24a1cbc` without the Epic's `design.md` | code `af46545` through a local fetch mirror; specs `cc5a4f8` on `spec/BOOK-1-01-alerts-service`, whose tree is `7892c6c`'s (P19), through the earlier baseline's `restore.sh` |
| Session | `0c71a857` | `803edf03` |
| Started (`runs.log`), window end (`measure.txt`) | 11:50:00Z, 13:05:23Z | 13:07:07Z and again at 13:07:32Z, 15:04:46Z |
| Total cost, measured | $30.35 | $43.40 |
| The run's own cost entry | $27.87 computed, written at 13:03:59Z, duration 4,431 s | $39.18 computed, written at 15:02:11Z, duration 6,870 s |
| Main session alone | $24.42 | $34.99 |
| Main calls; median, peak context | 161; 445k, 788k | 194; 602k, 947k |
| Compactions | 0 | 0 |
| Questions, waits summed | 20, 1,448 s | 24, 2,492 s |
| The Pieces question | "Two pieces at BookCsv.read (Recommended)", against "One piece" and "Three pieces" (26 s) | "Four pieces (Recommended)", against "One piece" and "Two pieces" (27 s) |
| `design.md` | 360 lines | 404 lines |
| Result | `design/BOOK-3-01-books-csv-import` at `2484b7a`, pushed; copy PR #12 | `design/BOOK-1-01-alerts-service` at `821963c`, pushed; copy PR #13 |

**Cost against the earlier runs.** The lean-context project's two `/design` runs, both on BOOK-1-01, cost $30.92 and $40.87 (the ledger's baselines). BOOK-3-01's $30.35 sits inside the ledger's expectation of $30–40. BOOK-1-01's two figures disagree because their windows differ: the run's own entry ($39.18) was written before its last turns, and the measurement ($43.40) runs to the window's end; the ledger puts the extra over the baselines down to the re-review's `BLOCK` and its fix cycle.

**BOOK-3-01: what it drew.** `Reason:` about 1,300–1,600 lines of production code in two layers with different test styles — a pure reader and checker under plain JUnit, and a Spring controller, service and persistence layer under `@SpringBootTest` with MockMvc and H2 — carrying the specification's 85 test cases.
- **`csv-reading`:** `Files:` the `…/books/csv/**` production and test packages. `Contract:` the reader contract, `BookCsv.read`.
- **`import-service-and-api`:** `Files:` the `…/books/imports/**` production and test packages, `BookImportController.java`, the `BookImport*` model and repository classes, `BookRepository.java` and `application.properties`. `Contract:` the reader contract and the Import API.

The split is at the reader contract, the user's answer to the grill's Pieces question (Q9; D9 in the session's decision log). Phase 5.5's `pieces.py parse` found no defect and its `assign` no overlap (ledger).

**BOOK-3-01: the reviews.** The first `design-reviewer` pass returned `BLOCK` — 1 BLOCKER, 2 MAJOR, 4 MINOR, 3 NIT — its BLOCKER the database-down premise: D5 settled `503` with the decided report, while D6 put the security hooks first, and they read `configs` on the same datasource, so an outage fails there first (to-fix PR1). The re-review returned PASS WITH RECOMMENDATIONS — 1 MAJOR, 3 MINOR, 2 NIT — and opens by saying its own `pieces.py parse` "found two well-formed pieces with no overlap". Neither pass raised a finding on § Pieces.

**BOOK-3-01 against the plan.** Expected (plan Task 8 step 1): a `## Pieces` section `pieces.py parse` reads as `pieces`, two pieces at the parser contract or a defensible alternative, and a `design-reviewer` verdict that is not `BLOCK` on the section. Met on all three.

**BOOK-1-01: what it drew.** `Reason:` about 1,500–2,000 lines of new production code in four layers with different test styles — JPA persistence with a row-locked fan-out, a scheduler and retention (H2 and PostgreSQL suites), an HTTP adapter with real-deadline tests, a REST API with MockMvc suites, and Gradle, Docker, Kubernetes and script wiring — carrying the specification's 150 test cases; one reviewer cannot hold all four in depth.
- **`alerts-domain`:** the `model`, `repository` and `service` packages, the service tests and the PostgreSQL test suite and resources. `Contract:` the domain service API, `StoreLookups`, the configuration keys.
- **`alerts-lookups`:** the `lookup` package and its tests. `Contract:` `StoreLookups`, the configuration keys.
- **`alerts-web`:** the `controller` and `config` packages and the controller tests. `Contract:` the alerts REST API, the domain service API.
- **`alerts-deploy`:** `settings.gradle`, both `build.gradle` files, the service's `Dockerfile` and `push_docker.sh`, its application class and that class's test, its `src/main/resources/**`, the database init script, `k8s/**` and the image workflow. `Contract:` the configuration keys.

It was `/design`'s own (Recommended) option at its Pieces question (D12 in the session's decision log). `pieces.py parse` and `assign` returned no defect and no overlap, and `pieces.py parse` on the final design returns `pieces` with no defect (ledger; section 2).

**BOOK-1-01: the reviews.** The first pass returned PASS WITH RECOMMENDATIONS — 6 MAJOR, 5 MINOR, 1 NIT, all 12 applied (ledger). The re-review returned `BLOCK` — 1 BLOCKER, 3 MAJOR, 5 MINOR, 2 NIT — its BLOCKER an undeclared departure from `[AD#5]`'s 30-second sweep bound, which the first round's fix had introduced; the user settled it with manual fix notes ("use the proposed notes"), and nothing reviewed the design after them. Each pass raised one finding on § Pieces, both MAJOR, both on the boundary between `alerts-web` and `alerts-domain`:
- **First pass:** the domain service API returned the JPA entities, which `## Interfaces / contracts` fixed only as JSON shapes, and the `Clock` bean the notices controller reads was in no API, so the web piece depended on the domain piece's internals.
- **Re-review:** the web piece's controllers need `ConfigRepository`, the `Config` entity and a pending-subscription count, none of them in the domain API; and the configuration keys belong in the `Contract:` lines of `alerts-deploy`, which defines them, and of `alerts-domain` and `alerts-lookups`, which read them.

The final design fixes both: the domain service API carries view records (`SubscriptionView`, `AlertView`), the `Clock` bean, `pendingCount()`, `Config` and `ConfigRepository`, and the `Contract:` lines name the configuration keys. The second fix landed after the last review. Neither pass questioned the `Reason:`.

**BOOK-1-01 against the plan.** Expected (plan Task 8 step 2; the design's §4): no `## Pieces` section, or `_N/A_`. Not met: four pieces. Ruling P22 finds that the expectation, not Task 2's wording, was wrong. The piece-review design called BOOK-1-01 "the earlier design's candidate" without sizing it. Measured, its specification carries 150 test cases against BOOK-3-01's 85, and the change is a new service across persistence, scheduling, an HTTP adapter, a REST API and deploy wiring. The run's `Reason:` exceeds `design-format`'s own model on every axis, so it holds under the format's wording; four pieces come to about 37 test cases each, against BOOK-3-01's about 42. Nothing bounds the count, and nothing should by count, but a four-piece `/implement` is unmeasured, so the CHANGELOG states the measured case as two pieces and to-fix PR2 carries the measurement. The design document names BOOK-1-01 as a change that gets no pieces, in its §3.2 as well as §4; its body stays as written, and a status note at its top points here.

**The mock question (P20, settled by P21).** Part (a)'s A/B left a finding: the test Epic's design prescribed a mocked writer for a rollback criterion, so a test following it holds trivially. That design was hand-written in `/design`'s format, never by `/design` and never read by `design-reviewer`, so P20 held the to-fix entry the plan's Task 9 step 2 and the design's §5 called for until this run showed `/design`'s own strategy. It did not prescribe a mock: its `BookImportFailureTest` spies on the real `BookRepository`, whose `saveAll` first inserts the conflicting book in a separate `REQUIRES_NEW` transaction and then calls the real method, so H2 raises a genuine unique violation after the import's earlier inserts, "proving the rollback". The measured population of the defect in `/design` is none, so P21 writes no to-fix entry against it: the `CatalogueWriter` mock in A's `U01_AC06_TC02` and C's `U01_AC06_TC01` came only from the hand-written design, and in C it was piece review's `Spec-named tests:` line that caught it.

**The BOOK-1-01 session's resume.** The user's session was resumed at 14:52:31 outside `run-design.sh`, so from then on the `workflows-core` references the run loaded came from the installed workflows-core 1.45.0, and `SPECS_PATH` read `/workspace/specs`. That changed no rule the run followed: this branch changes no `workflows-core` file, so the installed references hold the worktree's text. The command text already in the session stayed the worktree's 4.32.0, and so did the scripts it called by their worktree paths — `pieces.py parse` and `assign` ran again at 14:56:31, on the design as the manual fix notes left it, and returned no defect and no overlap — and the cost entry's `plugin_version: 4.32.0` was read from the worktree's `plugin.json`. The one file of the installed dev-workflows 4.31.0 anything read was its `commands/design.md`, opened by `impl-maintenance`, a fresh subagent, whose report cites its lines. Every write stayed on the e2e specs copy, and the drawing and both reviews ran before the resume (the ledger's Task 8 run 2 lines, the later one correcting the earlier; the session transcript). Section 6 has the recovery.

## 6. Incidents

The ledger records two for this sub-project. Neither changed what a measured run did.
1. **The bundle written into the code copy** (Task 7). The controller's `git -C $C bundle create code.bundle` wrote the bundle into the code copy, since the path is read relative to `-C` — the same slip as part (a)'s Task 15. **Recovery:** the bundle was moved to `C/` and verified.
2. **The BOOK-1-01 resume outside the run script** (Task 8 run 2; section 5). From 14:52:31 the session loaded the installed workflows-core 1.45.0's references, the same text as the worktree's, with `SPECS_PATH=/workspace/specs`. **Recovery:** none was needed beyond a check: `/workspace/specs` was untouched (clean, no file newer than 14:52, last commit 2026-10-22), every write had stayed on the e2e copy, the drawing and both reviews ran before the resume, and the `pieces.py` run after it used the worktree's script. The ledger's first account of it said the last phases ran on the installed 4.31.0; a later ledger line corrects that. Separately, as after any BOOK-1-01 start, the code copy's `origin`, which that start points at a local fetch mirror, was restored at the run's close (URL put back, `pushurl` unset, fetched).

`runs.log` also records the BOOK-1-01 start twice, 25 s apart; the ledger records one start, and neither says why.

## 7. What stays open

- **PR1** (`docs/superpowers/to-fix.md`): `/design`'s grill kept two decisions that conflict on a premise neither states as a criterion, test case or Rule — the BOOK-3-01 run's D5 and D6, caught only by the first `design-reviewer` pass, and the same defect as the `500` MINOR every judge found in run C, whose design was hand-written and never reviewed. The user's decision (2026-10-26 13:27): a separate change after 4.32.0 merges.
- **PR2** (`docs/superpowers/to-fix.md`, added with this record): measure the first `/implement` of a design that draws more than two pieces, the review cost per round against run C's, and whether a piece holding only build and deploy files finds anything the overall review would not (P22).
- **L2, as narrowed** (`2fde56ef`): two of lean context D's `session-hygiene` §1 additions are still unseen in a live run — the `(waiting since …)` marker beside a carried command item, and the register slug beside each Security Engineer offer. The third, *Last completed* with its UTC offset, was written by all three `/implement BOOK-3-01` runs.
- **E4's row for `40e6b9ea`** (`2fde56ef`): the port of `/implement`'s `code-writer` flow to the internal editions goes with this release, since the one-writer restructure it waited for was shelved.
- **C's `U01_AC06_TC01` still stubs the writer.** The third `review-fixer` pass deferred it as a plan conflict with the test Epic's hand-written design (`design.md:306`, `:371`), and no review follows that pass. It lives on the e2e code copy's branch (`686058c`), not in this repository; P20 and P21 record why it gets no to-fix entry against `/design`.

## 8. Rulings

Every ruling of the SDD run, in the ledger's order. The ledger writes them `Ruling P<n>: <what> — <why> — <cost if wrong>`, or close to it; this table keeps the what and the cost, shortened. P16 is recorded before P15, and P20 is settled by P21. "Not stated" means the ruling names no cost.

Where they came from: P1–P4 from the pre-flight scan; P5–P14 from Tasks 1 to 6 and their reviews, with P12 on the order of the work; P15–P18 from the final whole-branch review and its residual round; P19–P22 from Tasks 7 to 9 — the BOOK-1-01 start, the mock question and BOOK-1-01's four pieces.

| Ruling | Decided | Cost if wrong |
|---|---|---|
| P1 | The controller created the worktree and branch (Task 1 Step 1) before dispatch, since the SDD workspace lives in the worktree; the implementer skips that step. | Nothing. |
| P2 | Task 2 Step 5's parse check uses a filled-in instance of the format (two kebab-case pieces, real-looking globs, a `Reason:` line), not the placeholder block, which cannot pass the name rule by construction. | The format block and the parser could disagree on something only the placeholders show; Task 2's review reads the block against the grammar. |
| P3 | Each task adds its own CHANGELOG bullet under 4.32.0; Task 6 consolidates them into the release's entry. | A reword. |
| P4 | Sonnet 5.5 implements Tasks 1 and 3 (complete specs with tests); Opus implements Tasks 2, 4, 5 and 6 (prose executed literally); reviewers on Opus for the prose tasks, Sonnet for 1 and 3. | A weaker review lets a prose defect through to the final review. |
| P5 | A fenced block inside the `## Pieces` section is malformed (the implementer's choice, the brief read strictly); Task 2's `design-format` text states it. | A design that quotes an example inside its own section falls back to one review, with a printed line. |
| P6 | Task 2's seven deferred minors are fixed in Task 6, which already sweeps those files, not left to the final wave; the `Writers:` / `Builds after:` mention is dropped, since the never-shipped vocabulary is covered by "any other non-blank line". | Task 6 grows; the final review still sees the list. |
| P7 | The piece `Scope` format gains its contract — `Scope: piece <name> — files: <paths> — contract: <its Contract: items, or none>` — since the design (§3.1 point 4) gives each piece review its `Contract:` items and the plan's format dropped them; Task 4 amends now, Task 5 dispatches it so. | A few bytes per brief. |
| P8 | Task 4's six review minors are fixed now by its own implementer, with a scoped re-review, under the user's rule that known defects are fixed before push. | A little extra review cost. |
| P9 | The re-review round selects pieces from the diff, not the Fix Report: a piece is re-reviewed where its fresh piece diff differs (`cmp -s`) from its latest reviewed `diff_file`, or it had none. | About 300 bytes of `implement.md`. |
| P10 | Task 5's deviation 3 is ratified: on the re-review round the overall review gets each piece's latest review, not only this round's. | The overall review reads a slightly older review of an unchanged piece, which is still current. |
| P11 | The four items raised by Task 5's fix-round-1 re-review (two new Minors, two out of scope) go to Task 5's implementer now, as P8, with a scoped re-review on Sonnet. | Not stated. |
| P12 | The final whole-branch review and its fix wave run after Task 6 and before Task 7's live run, so run C tests the final text; Tasks 7–9 follow. | Nothing is lost but order. |
| P13 | In `design-format`, `Files:` patterns are relative to the top level of the design's target repository (its `Target` header, else its one repository), and a design whose change spans more than one repository draws no pieces, since `/implement` changes one repository per run. | A multi-repository design loses review pieces it might have used. |
| P14 | P13 is enforced mechanically: `/design` Phase 5.5 removes a `## Pieces` section from a design whose `Repos` names two or more repositories, and says so in its report; no `implement.md` bytes. | A user who wanted pieces there loses them silently, save the report line. |
| P16 | The final review's I1 is fixed: the re-review round also re-reviews every piece whose first-round review left a survivor the fixer pass was handed, read from the run's own triage records, never the Fix Report, whatever `cmp` says; the same claim is updated in `docs/commands/implement.md` and the CHANGELOG. | One more piece review per such piece. |
| P15 | A diff path that is not valid UTF-8 makes `assign` return `malformed` ("the path … is not UTF-8"), so the run prints the fallback line and gets one whole review; valid odd paths keep the byte-for-byte round trip. | A repository with such a path never splits its review. |
| P17 | The final review's M1–M6 are all fixed in the fix wave (M3 with its limit stated: `ls-tree` at the scanned commit does not see files the design creates); M7 is Task 9's; Task 3's duplication in `cmd_remove` is left, since it repeats an existing pattern. | Not stated. |
| P18 | The fix-wave re-review's three residual minors are fixed now by the same fixer, with one quick scoped check, before run C starts, since fixing after it would edit the tree under test; none touches `implement.md`. | About 15 minutes' delay to run C. |
| P19 | Task 8 step 2's "from specs baseline `c78ffdb`" means the earlier `/design BOOK-1-01` baseline's start state (code `af46545` through a fetch mirror, the specs tree of `7892c6c`), through that run's `restore.sh`, with its answers; starting from `c78ffdb` itself would hand `/design` an Epic that already has its `design.md`. | The run tests `/design` on an Epic that already has a design, which step 2 did not mean to measure. |
| P20 | The to-fix entry on a design's test strategy prescribing a mocked writer for a rollback criterion waits for Task 8's BOOK-3-01 `/design` run, since the test Epic's `design.md` was never written by `/design` or read by `design-reviewer`. Settled by P21. | The entry is written an hour later. |
| P21 | No to-fix entry against `/design` for a mocked writer: `/design`'s own AC06 strategy spies on the real `BookRepository` so H2 raises a genuine unique violation; the mock came only from the hand-written design; the measured population in `/design` is none, so this record states it as a test-bed fact, and piece review's `Spec-named tests:` line is what caught it in C. | A `/design` run on another Epic prescribes a mock and nothing tracks it until a live run shows it. |
| P22 | Task 8 step 2's expected value ("no pieces") was an unmeasured premise; BOOK-1-01's four pieces hold under Task 2's wording and are no finding against it. No wording bounds the count, and none should by count; since a four-piece `/implement` is unmeasured, the CHANGELOG states the measured case as two pieces and to-fix gains a measurement item (PR2). | A large Epic's `/implement` pays for more piece reviews than it needs until a run measures it. |

Two findings the ledger settles without a P-number:

| Where | Decided | Cost if wrong |
|---|---|---|
| Task 5, fix round 2 | The re-reviewer's one doubt — "where no fixer ran" for the first settle prompt's Re-review — checked by the controller: `finding-triage` asks that prompt under *When triage empties the survivor set*, where no fixer is dispatched, so the text holds. | Not stated. |
| Final review, P18's check | One Nit parked: `design.md:451` (the `/design` command) has Phase 6 name the Final-report items "as Phase 5.5 says" without listing the did-not-run case. The text stands: that reference covers it, and it agrees with Phase 5.5 and the report line. | Nothing. |

## 9. The ledger

The SDD ledger is copied verbatim beside this file as `2026-10-25-implement-piece-review-ledger.md`.

## 10. Addendum — after the merge (2026-10-26)

Written after the review of the merged release (`docs/superpowers/reviews/2026-10-26-piece-review-a980e58-review.md`), in the fix batch for it. Sections 1 to 9 stand as written, and the ledger is unchanged: it is a verbatim copy.

**The merge and the merged tree (the review's N8).** §1 to §9 were measured at `7c436653`, before the branch took `main`: `8f96c887` merged `origin/main` into the branch (#76 B02, #77 B04, #78 B07 and the 2026-10-26 reviews — `workflows-core` 1.47.0, `security-workflows` 0.4.0, `product-workflows` 3.37.0), `dd11ef27` dated the CHANGELOG, and `a980e585` merged the branch into `main`, its tree equal to its second parent's. No file under `plugins/dev-workflows` changed between `7c436653` and `a980e585`, so no value in §2 moved. On the merged tree, the full chain of `.github/workflows/validate-catalog.yml`'s `run:` steps, run as one `&&` chain on a worktree at `a980e585`, exits 0, `pieces.py --selftest` printing PASS (52 checks) and `run-state.py --selftest` PASS (97 checks). That 4.32.0 runs beside `workflows-core` 1.45.0 holds at the merge too: no `plugins/workflows-core` file is in `a980e585`'s diff against its first parent, and every `workflows-core` rule the release cites exists at 1.45.0.

**The to-fix entry design §5 asked for (the review's F6).** Design §5 put the mocked-writer test-strategy finding into `docs/superpowers/to-fix.md` as "one instance, recorded, not ruled on"; P21 instead found `/design`'s own strategy sound in one run and wrote none, and the ledger still names "the to-fix entry Task 9 writes". The entry is now `to-fix.md` PR4, written with this addendum. P21 stands as evidence of where the defect was seen, not as a ruling that closes it.

**Rulings added after the merge.**

| Ruling | Decided | Cost if wrong |
|---|---|---|
| P23 | Design §3.1 point 2 says `design-reviewer` *refuses* a section `/implement` cannot use; the build grades a malformed section `MAJOR` (plan Task 2 step 3), which `/design` Phase 6 offers to apply and the user may decline. The `MAJOR` stays: Phase 5.5 fixes or removes a malformed section, or an overlap among existing files, before the review, so only an overlap among files the design creates reaches it unfixed, and a section that reaches `/implement` malformed falls back to one review with its line printed and recorded, which is today's review. | A declined `MAJOR` leaves a design whose `## Pieces` `/implement` reads as one piece — the review it would have made without pieces. |

# One writer per Epic, part (a) — verification record

## 1. What it was and what happened to it

Part (a) of "one writer per Epic" rebuilt `/dev-workflows:implement` so that each writer unit of an Epic was coded by one long-lived `code-writer` and one `test-writer` writing from the specification, each reached again by `SendMessage` for every fix, with each unit's tests run before a review made once per piece of the design and once over the whole change, and every build and test run serialised by a lock script, `run-lock.py`. The design is `docs/superpowers/specs/2026-10-24-implement-one-writer-design.md` and the plan `docs/superpowers/plans/2026-10-24-implement-one-writer-a.md`; each now carries a status note at its top. Tasks 0–14 were built on branch `iv-gu/implement-one-writer` (base `1f74fc03`, head `ef81409a`, worktree `/workspace/.worktrees/implement-one-writer`) as dev-workflows 4.32.0 and workflows-core 1.46.0, and Task 15 measured them in a live A/B. The outcome: shelved, not merged and not pushed. The plan's Task 16 (record, merge and push) was not run, and the branch and its worktree stay until the user decides. What replaced it is piece review (`docs/superpowers/specs/2026-10-25-implement-piece-review-design.md`), which keeps today's coding flow, splits the review by the design's pieces, and is built as dev-workflows 4.32.0, the number the shelved branch never released.

## 2. The A/B

**Sources.** The figures are quoted from the run records on the maintainer's machine under `~/e2e-live/one-writer/`, outside this repository: each arm's `measure.txt` (cost, cache reads, main-session calls and context, compactions, the questions and the seconds each waited), `per-agent.txt` (cost per dispatch and per agent type), `agents.txt`, `run.txt`, `code-stat.txt`, `final-report.txt` and `specs-session.diff`, with `runs.log`, `blind-mapping.txt` and the two verdicts. The wall times and the cache figures in section 3 are the ledger's (Tasks 0 and 15).

**Setup.**
- **The test Epic.** BOOK-3-01, a CSV catalogue import into the books service of the throwaway bookstore copies in `ihudak-e2e`, written for this test and approved by the user before any run. Its specification carries 6 stories, 35 acceptance criteria and 85 test cases (both final reports). The piece-review design describes the change as about 1,500 lines of production code in two layers with different test styles. Its hand-written `design.md` carried a `## Pieces` section naming two pieces, `csv-catalogue` and `import-runs`, which 4.31.0 ignores.
- **One start state for both arms.** Code `6942a24`, the code copy's `master` fast-forwarded from `af46545` to `origin/master`; specs `0d68eb7`, the specs copy's `main` with the Epic added. Arm A started on `0d68eb7` itself. Arm B started on `8bc8dda`, the restore commit the run script makes to put the specs tree back to `0d68eb7` (`runs.log`, ledger).
- **Launch and reset.** `~/e2e-live/one-writer/run-epic.sh A|B` archived leftover branches as bundles under `archive/`, reset the code copy to `6942a24` and the specs tree to `0d68eb7` by a restore commit, cleared the copy's `.remember` and the copy project's auto-memory, and launched `~/e2e-copies.sh opus --permission-mode bypassPermissions`. Arm B set `E2E_PLUGIN_SRC` to the worktree's `plugins/`. The command was `/dev-workflows:implement BOOK-3-01`, arm A first. After each run the session id, branch and cost (`session-cost.py`) were captured before the next reset.
- **Not run.** The plan's Task 15 named two more pairs, route 3 and a direct `MODERATE` run; neither the ledger nor `runs.log` records either.

**The arms.**
- **Arm A**, the installed dev-workflows 4.31.0 and workflows-core 1.45.0. Session `6db30fe5`; code commit `5e0c6c0` on `feat/BOOK-3-01-csv-catalogue-import-books-service`; specs commit `e6e4ccc`, pushed. Classified `SIGNIFICANT`, it coded in 7 step groups, each a fresh Opus `code-writer`, then wrote tests with one Sonnet `test-writer` from the diff, then made one Opus review, a `review-fixer` pass, the re-review and a second `review-fixer` pass, and verified the tests against the baseline.
- **Arm B**, the branch, its plugins loaded from the worktree (4.32.0 / 1.46.0). Session `dfda370d`; code commit `c986587` on the same branch name; specs commit `55a39ae`, pushed. Classified `SIGNIFICANT`, it coded two writer units, `csv-catalogue` and `import-runs`, each through one Opus `code-writer` and one Opus `test-writer`, ran each unit's tests, reviewed each piece and then the whole change (three scopes), sent the fixes back to the writers, re-reviewed all three scopes, and ran the tests again.

**What the user answered.** Each question's header and wait are from `measure.txt`; the answers are from the final reports.
- **Arm A:** Plan (299 s), approved. Branch (39 s). Open NITs (585 s), "Apply them (Recommended)" for the first review's two NITs. Re-review (261 s), the unspent re-review made. Open items (2,447 s), "Apply them (Recommended)" for the two findings the re-review left open. Push / PR (402 s), not pushed.
- **Arm B:** Plan (17 s), approved. Branch (1,022 s). NITs (299 s), "Apply them" for the first round's eight NITs, seven applied and one deferred by both test writers. Plan ruling (164 s), "Revise the plan (the finding governs)". Two questions headed Re-review (130 s and 450 s): the re-review of all three scopes was made, and its nine edit-only findings applied ("Apply them"), eight applied and one deferred by its code writer. Push (1,578 s), not pushed. Follow-ups (79 s), two follow-ups written.

**The plan ruling.** B's overall review raised a MAJOR plan conflict: with `existing=update` and a file with no `published` column, every updated book was unpublished, as the design's `BookDraft` contract and plan Steps 1, 5 and 13 say (absent means false). Arm A shipped the same behaviour, and its review did not raise it. Both answers of that picker apply the same fix, so the A/B's code outcome does not depend on the answer; and the picker carries no `(Recommended)` marker in 4.31.0 either (a closed vocabulary), so its absence is not a regression (ledger).

**Results.**

| | Arm A, 4.31.0 | Arm B, the branch |
|---|---|---|
| Total cost | $57.17 | $99.06 (+73%) |
| Main session alone | $25.94 | $41.03 |
| Subagents | $31.23 | $58.03 |
| Cache reads, whole run | 111.4M | 196.4M |
| Cache reads, main session | 81.0M | 137.0M |
| Main-session calls | 153 | 223 |
| Main context, first call | 183k | 184k |
| Main context, median | 535k | 661k |
| Main context, peak | 856k | 964k |
| Compactions | 0 | 1, at 17:14, near the end of the run |
| Wall time | 3h41m | 3h52m |
| User wait (the questions' waits summed) | 4,033 s | 3,739 s |
| Subagent dispatches | 21 | 21 |
| Files changed, insertions | 36, +4,161 | 33, +4,350 |
| New tests | 125 | 161 |
| Tests passing at the end | 191: Gradle 134, web 57 | 227: Gradle 170, web 57 |
| Review verdicts | PASS WITH RECOMMENDATIONS, both rounds | PASS WITH RECOMMENDATIONS, every scope, both rounds |
| Conformance, by its own review | 126 satisfied, 0 exceeds | 126 satisfied, 3 exceeds |

The table quotes `measure.txt`, over each run's whole window. The runs' own cost entries (`specs-session.diff`), written before their last turns (13:09:49Z and 17:14:32Z), record $54.87 and $95.90 computed, and durations of 13,163 s and 13,790 s, against the ledger's wall times above.

**Cost by agent type** (`per-agent.txt`, dispatches from `agents.txt`):

| Agent type | A: dispatches | A: cost | B: dispatches | B: cost |
|---|---|---|---|---|
| `code-writer` | 7 | $14.76 | 2 | $15.52 |
| `test-writer` | 1, Sonnet | $0.34 | 2, Opus | $19.52 |
| `code-review` | 2 | $7.86 | 6 | $17.67 |
| `review-fixer` | 2 | $3.21 | 0 | — |
| `risk-planner` | 1 | $3.67 | 1 | $3.27 |
| `test-baseliner` | 2 | $0.58 | 4 | $1.22 |
| `general-purpose` (post-run reviews) | 3 | $0.41 | 3 | $0.41 |
| `code-scanner` | 2 | $0.33 | 2 | $0.34 |
| `impl-maintenance` | 1 | $0.06 | 1 | $0.09 |
| All subagents | 21 | $31.23 | 21 | $58.03 |
| Main session | | $25.94 | | $41.03 |

- **`test-writer`** cost $19.52 against $0.34: B's ran on Opus, A's on Sonnet, since the design had the test writer follow the code writer's model rule (its §3.1, *Models*, a Claude's call).
- **`code-review`** cost $17.67 over six dispatches, three scopes in two rounds, against $7.86 over two.
- **`code-writer`** was nearly level: two long-lived writers cost about what A's seven fresh ones did.
- **`review-fixer`** is absent from B, whose writers made its fixes.
- **The main session** cost $15.09 more in B (ledger).

## 3. The cache diagnosis

B's writers' cost was dominated by cache writes (ledger, Task 15 arm B). Subagents run on the 5-minute prompt cache, the main session on the 1-hour cache. Every fix resume of a B writer came 516 to 4,252 seconds after that writer's last call, so even the shortest gap was past the five minutes, and each of the 12 resumes re-cached the writer's whole context, 151k to 279k tokens. That is about 2.7M cache-write tokens, about $13.6 at the Opus 5-minute rate.

Task 0's spike had measured both cases before any code was written. A warm resume read 37,487 tokens from the cache and wrote 97. A cold resume, from a restarted parent process 7 minutes later, read none and wrote 37,644: the agent's whole context again. (The ledger's earlier line on the same measurement names a 6-minute gap.) `SendMessage` worked in both cases, and it stayed the primary path, with a fresh dispatch as the fallback.

The runs' own cost entries show the same shift: B's records 6,359,756 Opus cache-write tokens against A's 3,153,900 (`specs-session.diff`; each entry was written shortly before its run ended).

The main session added its own share: 223 calls against 153, at a median context of 661k against 535k, for $15.09 more.

## 4. The judges

**Method.** Two blind Opus judges (`general-purpose` agents) each compared the two arms' trees against the Epic's documents under neutral labels (inputs in the controller's scratchpad, `blind-epic/{X,Y,epic}`); the mapping stayed outside their inputs, in `blind-mapping.txt`. The second judge got relabelled sides, under the rule that a close margin is repeated before it is believed. Neither judge ran a build or a test: both traced code paths.

| | Judge 1 (`verdict-1.md`) | Judge 2 (`verdict-2.md`) |
|---|---|---|
| Labels | X = B, Y = A | M = A, N = B |
| Verdict | "X slightly better", that is B | "N slightly better", that is B |
| Confidence | medium | medium |
| A: BLOCKER / MAJOR / MINOR / NIT | 0 / 0 / 1 / 3 | 0 / 0 / 3 / 3 |
| B: BLOCKER / MAJOR / MINOR / NIT | 0 / 0 / 0 / 4 | 0 / 0 / 1 / 3 |
| A tie defensible | yes | yes |

Neither judge found a coverage gap against the specification's test cases on either side, though judge 1 noted that on one reading B meets `[U04] AC02` only in part (below). Neither found a BLOCKER or a MAJOR on either side.

**Judge 1's defects.**
- **A:** MINOR, U+0000 in a value reaches PostgreSQL unchanged and is answered as a false `409 CONFLICT`, or as a `503` that records nothing (inferred from the code path, not run). NITs: an import applied and then answered `406` on a non-JSON `Accept`; reads answering `500` with the database down; client errors logged at ERROR.
- **B:** four NITs: the `published` change to the design's `BookDraft` contract; unknown query parameters refused with `400`; a service-wide Hibernate batch size; the listing loading every problem of each run, with no index on `book_import_rows.import_id`.

**Judge 1's reasons**, the three differences it named as deciding:
1. **`[U01] AC06` test fidelity.** B's TC01–TC03 reproduce the specification's race at the database: a spy commits a book with one of the file's ISBNs from another connection after the check, so the writer's own insert meets the real unique index, and the insert already executed is shown rolled back. A's use a `@MockitoBean` writer that throws before anything is written, so they hold trivially.
2. **Robustness at the edges.** B handles U+0000, checks `Accept` before any write, and answers `503` on reads with the database down. A has the PostgreSQL-only misreport and the apply-then-`406` path.
3. **Adherence to the agreed contract.** A keeps the design's `BookDraft` exactly; B changed the interface fixed between the two pieces. The judge counted this against B, and it "partly offsets the first two". A was also credited with a listing that loads only file problems, the `import_id` index and every API test asserting the status, where about 15 of B's read the body without one.

**Judge 2's defects.**
- **A:** MINORs: concurrent imports creating the same new ISBNs in different orders can deadlock, and the loser answers `503` where `[U01] AC06` requires `409`; U+0000 misreported or left unrecorded on PostgreSQL; every record materialised before `TOO_MANY_ROWS` is decided. NITs: a misspelt option (`?dryrun=true`) silently applies the import; a CR CR LF header hides the `published` column; reads answering `500` with the database down.
- **B:** MINOR, the listing loads every row problem. NITs: the service-wide batch size; `400` on unknown parameters; U+0000 rewritten to U+FFFD. The `published` change was recorded as a design deviation and not counted.

**Judge 2's reasons**, the three differences it named as deciding:
1. **Robustness on the write path and the input edges.** B inserts in ISBN order, so concurrent creations get the specification's `409` rather than a deadlock answered `503`; it bounds the records it keeps; it handles NUL without misreporting.
2. **Test realism against test strictness.** B's `[U01] AC06` tests meet a genuine database refusal, where A's specification-named conflict tests use a writer double; but A asserts the status and the exact problem list on every HTTP call, where B often does not.
3. **Fidelity to the contract.** A follows the design exactly, adds no configuration and keeps the listing cheap. B's departures are deliberate and mostly protective, but each departs from the contract.

**The `published` question.** Both judges read A's unpublishing on update as following the design and a literal reading of `[U04] AC02` ("replace all five"; judge 1 also cites `[U01] AC01` TC03), a product hazard rather than a defect. The ledger records that the controller's earlier reading, that A had shipped a data-loss bug, overstated it.

**Where B's edge came from** (ledger, the judge lines). Per B's own report, the ISBN-ordered inserts, U+0000 read as U+FFFD, the header trim, the `503` on a database outage and the bound on the records kept all came from B's review rounds; the real-database `[U01] AC06` tests came from the spec-driven test writer. The listing that loads only file problems and the `import_id` index, which judge 1 credited to A, were found by A's review alone; B's six reviews missed them.

## 5. The two branch defects

B's run wrote three entries to the Epic's feedback file (`BOOK-3-01-feedback.md`, in `B/specs-session.diff`), each `origin: auto` against plugin version 4.32.0. Two are defects of the branch itself, and the piece-review design (§1) traces both to splitting the tests out of the coding:

1. **`BOOK-3-01-implement-piece-paths-omit-files-touched`** (false-positive, friction). A first-round piece review raised a MAJOR that the test fixture `CatalogueFixtures.java` was missing from the commit, and triage dismissed it. The unit's test writer had reported the fixture under **Files touched**, and the whole-change diff carried it, but Phase 3.6 step 1 built a piece's paths only from the test files a test writer names under `### Tests added` or `### Tests updated`. So a shared helper named only under **Files touched** was in the whole diff and in no piece diff, and the piece reviewer saw a gap the change did not have. The entry suggested counting those files too.
2. **`BOOK-3-01-implement-review-test-part-routing`** (manual-workaround, friction). Several review findings had a code half, in a code writer's file, and a test half ("add a test …"), in a test writer's file. Phase 3.6 step 3 routes each finding to one owner, the writer of the file its fix lands in, so the test half had no route. The orchestrator sent each finding's test part to the owning test writer by hand, and folded a re-routed, already-deferred NIT into the receiving test writer's first send. The entry suggested stating that the test part goes to the owning test writer in the same pass.

The third entry, `BOOK-3-01-implement-piece-boundary-contract-in-plan` (missing-capability, polish), asks that a plan with two or more pieces name the contract wherever one piece's output feeds another, after the `published` conflict only the overall review could see.

Neither defect was fixed: the branch was shelved before any fix for them. Piece review carries the first one's lesson instead: a piece's files are the review diff's paths that match its `Files:` patterns, never a writer's report, and `Files:` names a piece's tests as well as its code (piece-review design §3.1 point 2, §3.2). The second has no counterpart there, since one `review-fixer` pass takes every survivor (§3.1 point 5).

## 6. The two incidents and their recovery

Neither changed what either run did; both put a run's recorded output at risk (ledger, Task 15 incident).
1. **The run script deleted arm A's branch.** Its archive step wrote to `"$OUT/archive/feat/…bundle"`: the slash in the branch name named a directory that did not exist, the write failed silently (`2>/dev/null || true`), and the script then deleted A's branch.
2. **One bundle overwrote the other.** The controller's own `git -C $C bundle create code.bundle` wrote the bundle into the code copy, since the path is read relative to `-C`, so B's bundle overwrote A's.

**Recovery.** A's commit `5e0c6c0` was recovered from the object store into `~/e2e-live/one-writer/A/code.bundle`, verified, and its diff found identical to `A/code.diff`. B's bundle was moved to `B/`. The script was fixed: a slash in a branch name becomes `_`, every bundle is verified, and a failure stops the script without deleting anything.

## 7. Why it was not merged

The piece-review design's §1 reads the A/B this way.
- **What B cost.** $99.06 against A's $57.17, 73% more, for about the same wall time. Its main session compacted once near the end, at 964k of the 1M window, where A's peaked at 856k without a compaction.
- **What B bought.** Two blind judges, labels swapped, each rated B slightly better at medium confidence, with no BLOCKER or MAJOR on either side; both called a tie defensible.
- **Where the gain came from.** Most of it came from B's extra review scopes, the per-piece and overall reviews: the ISBN-ordered inserts, U+0000 handled, the header trim, `503` on read outages, the bound on the records kept.
- **Not from the one-writer structure.** No gain was traced to long-lived writers or to reaching them again, and that structure drove most of the extra cost: the 12 resumes that re-cached the writers' whole context (about $13.6), and about 70 more main-session turns.
- **Not reliably from the spec-driven test writer.** Its `[U01] AC06` tests met a real database refusal where A's used a mocked writer, but they got there by departing from the design's test strategy, which prescribed the mock. It caught no code defect: both pieces' tests passed on their first run. (B's own report adds that the `import-runs` test writer's first run of its tests failed to compile, on a test helper that shadowed `status()`, which it fixed itself.) It left many import calls without a status check, where A checked every one. And splitting the tests out of the coding caused two of B's three feedback defects (section 5).
- **So** today's coding flow, which produced equally good code most cheaply, is kept, and the one thing the evidence supports is added: review scopes that follow the design's pieces.

**The user's decisions** (piece-review design, *Who decided what*, §2 and §5):
- **Option 1.** Keep today's coding flow and add piece review, over the alternatives: merging part (a), reworking it, or shelving the sub-project.
- **Without the spec-driven test writer.** Piece review takes nothing of the branch beyond the pieces format and the review scopes: no long-lived writers, no `SendMessage` resumes, no lock script, no spec-driven test writer, no writer units, no test run before the review. Step groups, `code-writer`, `test-writer` from the diff, `review-fixer`, the review before the test run and every model choice stay as in 4.31.0.
- **The rest of the earlier design dropped.** Of its part (b), only `/design` drawing pieces is kept, in piece review; `/specify` and `/design` becoming mandatory before `/implement` and the widened *Re-split* exit are dropped, and so is all of part (c), `/epics` turning its size cap into a warning. For part (c) and the mandatory gates the design gives the reason, the user's decision on Claude's recommendation: both rested on one writer being able to hold a big Epic and fix its own work from its own context, a premise that did not survive the A/B; and A's main session already peaked at 856k of 1M on this Epic, so bigger Epics would compact mid-run under today's flow.
- **What the user values:** quality over cost, since poor quality costs more later; and no waste: cost that buys nothing measurable is waste.

The A/B also left one finding on the test Epic's design: it prescribed a mocked writer for a criterion about rollback, so a test that follows the design holds trivially. That design was written in `/design`'s format by a subagent, not by a `/design` run, so whether `/design` itself writes such a test strategy is a question for piece review's own `/design` run on this Epic, and its record says what that run showed.

## 8. Rulings

Every ruling of the SDD run, in the ledger's order. The ledger writes them `Ruling: R<n> — <what> — <why> — <cost if wrong>`; this table keeps the what and the cost, in shortened form. R48 is used twice, for two items parked in Task 14, and both are listed. "Not stated" means the ruling names no cost.

Where they came from: R1–R6 before Task 0, from the pre-flight scan; R7–R34 from Tasks 2 to 11a and their reviews; R35–R39 from Task 13, the rule-by-rule reading, which classed 338 old rules as KEPT 263, MOVED 4, CHANGED-BY-DESIGN 56, CHANGED-BY-RULING 12 and LOST 3, with 2 CONTRADICTED; R40–R48 from Task 14's final whole-branch review (4 Important and 7 Minor findings; of the 16 deferred minors and 2 standing items it triaged, 12 to fix and 6 to leave) and the residual rounds after it.

**`implement.md`'s size.** The design said the command shrinks (its §3.1 point 8). It did not. The ledger gives the base as 326,539 bytes at Tasks 9 and 10 (R27) and as 326,520 from Task 11a on, which is the design's own figure; the two disagree. Task 11a brought it to 326,833 (R33). The last size the ledger records is 331,636 bytes after Task 14's residual wave (`6d1dfd1e`, +1.6%), and it records none after the two `run-lock.py` rounds that followed. Measured from git afterwards (`git show <commit>:plugins/dev-workflows/commands/implement.md | wc -c`), the file is 326,520 bytes at the base `1f74fc03` and 331,720 at the head `ef81409a`, 1.6% more. R45, the user's decision, accepted the command at 331,120 bytes (+1.4%) with no further condensing pass, to be recorded here as the design's "shrinks" goal not met. It was not met. The writers grew more, in subagent context rather than the main session's (Task 13): `code-writer.md` 24,620 to 36,002 bytes, `test-writer.md` 15,460 to 27,841, the code-writer handoff 17,119 to 25,507, and a new test-writer handoff of 14,744.

| Ruling | Decided | Cost if wrong |
|---|---|---|
| R1 | A plan Step with no `Piece:` line belongs to the only writer unit where there is one. With two or more units, Phase 2A and `risk-planner` give every Step a `Piece:`; a Step still without one goes to the unit owning the first file it names, else the first unit. | A Step coded by the wrong unit's writer, caught by the per-piece review. |
| R2 | Task 7 changes only the run-state `KEYS` and the quoted `KEYS_LINE`; `implement.md`'s body references to `step_groups` stay until Task 9 rewrites them. | None once Task 9 lands; the branch is never released between them. |
| R3 | The claim sweep splits by location: Task 11 sweeps `plugins/*/{commands,agents,references,skills}` and `docs/maintainers/`; Task 12 sweeps `plugins/*/docs/`, `.claude/rules/`, `CLAUDE.md` and the READMEs, and runs refinement 7's counts over the whole scope at its end. | A stale copy, found by the final review. |
| R4 | Each rewritten agent `description` stays at or under 600 characters (`validate-catalog.py` warns above 600, fails above 1024). | A warning only. |
| R5 | Task 0's steps 1–3 run at once; step 4, a resume across `/compact`, is the user's, in a separate terminal, while Tasks 1–8 proceed, since nothing before Task 9 depends on it. | Task 9's primary-path wording revised in its fix loop. |
| R6 | The per-task gate chain runs with `ASSERT_PUBLISHED` empty; the run with check 18 armed comes only at Task 16, after the changelogs are dated, since the plan's `ASSERT_PUBLISHED=1` throughout would fail every task once Task 12 wrote `— Unreleased` sections. | None; CI arms it on the push. |
| R7 | Task 2's I3: `run-lock.py` keeps the plan's exit codes 2 and 4, and every exit the script makes itself prints a `run-lock:`-prefixed stderr line, usage included, by which callers tell its exits from a test runner's. | A caller misreads a test runner's exit 4, mitigated by the line. |
| R8 | Task 2's three Minors go into fix round 1 with the Importants, under the user's rule that known minors are fixed before push. | One slightly larger fix diff. |
| R9 | Task 3's remaining open item is a gap in the implementer's scratch report, not in a delivered file (`design-format.md:210`'s "section 11" is correct), so no fix round. | None; the report is not shipped. |
| R10 | The one paragraph added to `review-fix.md` may also name the terms it uses as the dispatching caller's inputs, with their defaults when absent, and stays one paragraph. | None. |
| R11 | Between Tasks 5 and 9, `implement.md` keeps dispatching `test-writer` with its old inline brief; the mid-branch mismatch is accepted, with no compatibility shim. | None once Task 9 lands. |
| R12 | `test-writer`'s tools become Read, Glob, Grep, Write, Edit, Bash and Skill: `review-fix.md` step 6 loads the patch gate through the Skill tool, which the plan's list omitted (a plan defect); `check.py`'s pinned string follows. | None; `code-writer` already carries Skill. |
| R13 | The Test Writer Request gains `earlier_reports` and `diff_so_far`, which the spec's fallback fresh dispatch needs and the plan's field list omitted. | Two unused fields on the `SendMessage` path. |
| R14 | `test-writer` may change what a pre-existing test asserts where `failure_input` names that test and the source (the spec; with none, the design, plan or task) says its behaviour changed; in fix mode a failing pre-existing test is sorted by step 7's three outcomes (update, disagreement, `needs_decision`). | A test writer updates a distant test the orchestrator would have ruled on; mitigated by `needs_decision` where the source does not settle it. |
| R15 | A repro used during diagnosis may be written as a test only in the scratch checkout of HEAD, by the code writer as today; the regression test in the working tree is the test writer's, and the caller's red check runs that one. | The regression test differs from the diagnosis repro; the red check still proves it catches the bug. |
| R16 | The code writer runs the project's own install scripts that `install-time-code.md` runs beside a build, by that reference's rules and exclusions, through the lock, immediately before its own build; the caller no longer runs them for it. Dependencies' install-time code stays skipped. | A project install script runs one phase earlier than before, still before any build. |
| R17 | The scratch-checkout call is wrapped whole in the lock (`run-lock.py -- bash -c '…'`, run from `repo_root`), since it links the working tree's dependency directory. | A bug run's repro waits for a build. |
| R18 | Fix mode keeps up to 3 internal attempts on the checks it was handed, and the handoff states that bound, so the caller knows each of its 3 rounds per test run holds up to 3 attempts. | More attempts before the user is asked. |
| R19 | `test-baseliner` cannot measure its time bound apart from the lock wait, so a suite that printed a `run-lock: waiting for` line and was then cut off, aborted or came back short is recorded with a `CAVEAT:` note naming the wait; `/implement` never reads such a line as this change's regression. | A real regression on a contended run is marked as possibly environmental; `/implement` sequences agents, so contention is the defect case. |
| R20 | Task 9 moves today's review steps (Phase 3B steps 5–7.5 and step 8's delta review) unchanged under `## Phase 3.6 — Review`, re-pointed to run after Phase 3.5; Task 10 then rewrites Phase 3.6 into per-piece and overall reviews with fixes by owner, so the command stays whole between them. | Task 10 rewrites text Task 9 moved. |
| R21 | A pre-existing file no piece names, which a writer must edit, is put to the user (move it into this unit, or stop), never moved in silently. | One more question on a rare path. |
| R22 | `writers[]` entries gain a `model` member, so the fresh-dispatch rule after a class change can be read off state after a compaction; `files.test_report_file` leaves `KEYS`, since nothing writes it. | None. |
| R23 | Task 10's choices stand: `applicable_spec` goes only to the review covering the whole change; a `### Re-classification` is acted on only from a one-piece run's review; a piece whose BLOCK still stands is re-reviewed even without fixes of its own; the offer and the Stop condition flag run once per review round over every review's survivors. | One extra piece re-review. |
| R24 | Every review diff carries every tracked path the tree changed and every untracked path a writer reported; an untracked path no writer reported is left out of the diffs and named under `### Assumptions & limitations` as committed without review. | A build output not ignored is committed with a note rather than kept out. |
| R25 | Before a survivor whose fix lands in a file no unit holds is sent, the orchestrator moves the file into the owning unit (a new file into the unit whose Step created it, else the first unit; a pre-existing file only on the user's answer, as R21) and sends the updated `unit_files`; `code-writer`'s `mode: review` rule gains the exception for a new file a Step of the unit creates. | One question on a rare path. |
| R26 | For a review survivor in a pre-existing file no piece names, the question's second option is "Leave the finding deferred", not "Stop here": a BLOCKER left deferred still stops the run through NEEDS HUMAN. | None. |
| R27 | The spec's "`implement.md` shrinks" is not met after Task 10 (+16,337 bytes over a base the ruling gives as 326,539), so a Task 11a is added: condense the sections the branch rewrote to the base size or under, every rule kept, with Task 13's reading as the proof; where that cannot be done without dropping a rule, stop at the most compact form and record the deviation for the user. | One more Opus task and review. |
| R28 | Task 10's removal of the unused `files.review_return_file` from `KEYS` stands, on R22's precedent. | None. |
| R29 | `risk-planner`'s scratch-checkout call on a bug re-plan also runs through `run-lock.py`, reading a `run-lock:` line the same way. | None; nothing runs concurrently there. |
| R30 | `review-fixer`'s MINOR severity, User-applied and Plan ruling inputs stay, though no caller passes them now: `review-fixer` stays unchanged for `/vuln` and `/upgrade`, and a retirement needs grounds beyond "nothing uses it". | Three dormant inputs. |
| R31 | Task 11a's remaining gap is closed by two safe cuts: the 16 phase openers shortened (keeping "Read the run-state file first." and the `run-state.py open` call), and the `clean_finish` history paragraph moved to `docs/maintainers/rationale.md`; Phase 3.5's lock rules are not moved into a new reference, which every run would read anyway. | None. |
| R32 | A pre-existing gap is fixed: Phase 2A writes `spec_context.applicable_spec` where a specification or design is in scope, as Phase 2B does, so a `MODERATE` review gets it as the invariant and the Phase 3.6 brief say. | None. |
| R33 | 326,774 bytes is accepted, 254 over the base and all of it R32's fix; the final report says plainly that `implement.md` is flat (+0.08%), not smaller. Superseded after Task 14 by the size then (ledger; R45). | The spec's "shrinks" met only in spirit. |
| R34 | Plugin prose names the rationale in words, never by a relative link an installed plugin cannot resolve. | None. |
| R35 | Task 13's rule-by-rule reading goes to a fresh read-only Opus agent writing its table to the workspace, not to the controller; the controller judges its findings and routes any lost rule to a fix dispatch. | None; the reading is the same. |
| R36 | A lost rule restored: a fix-mode writer return unreadable twice counts as that fix round's attempt, nothing folded; the next round reaches it again or falls back to a fresh dispatch, and the 3-round cap bounds the loop. | One more round before the user is asked. |
| R37 | The review brief's `Plan ruling:` line names each ruling in the orchestrator's own words with the user's answer, never a writer's question or report verbatim, which can carry test output, so the review stays blind to test results. | A reviewer reads a paraphrase. |
| R38 | The Code Writer Request gains `run_tests` (yes or no), as `test-writer`'s has; under a recorded `test_decision: skip` the code writer builds but runs no test, so the skip reaches every writer. | None. |
| R39 | Two more lost rules restored: Phase 3.5 runs a regression test that lies outside every baseline suite with the checks, expected to pass; accepting the review's re-classification skips Phase 3.6 step 4's conformance escalation. | None. |
| R40 | The whole-change review's brief names each untracked path no writer reported, path only, so the reviewer can open it; the diffs still leave them out (R24). | A longer brief. |
| R41 | Phase 2A and `risk-planner` flag at plan time a Step that edits a pre-existing file no piece names, so the question comes at plan approval rather than mid-run. | None. |
| R42 | `run-lock.py` locks the outermost work tree's git directory (`git rev-parse --show-superproject-working-tree`, repeated to the top), so a suite inside a submodule shares the lock. | A submodule build waits for the superproject's. |
| R43 | A fresh dispatch after a failed answer resume appends its report to the writer's `reports`, never replacing the report the answer pairs with. | None. |
| R44 | A second, small residual wave fixes the fix-wave re-review's new findings, the pre-existing `run-lock.py:143` window and the spec's "merges the two units" included, then one scoped re-review: the user's rule that known defects are fixed before push outranks the skill's one wave. | One more short round. |
| R45 | The user's decision (2026-10-25 07:50): `implement.md` at 331,120 bytes (+1.4% over the base) is accepted, with no further condensing pass, and recorded in this record as the spec's "shrinks" goal not met; the orchestrator's large context need predates the branch. | Not stated. |
| R46 | One last `run-lock.py` round: install the signal forwarder at the start of `run()`, block the four signals with `pthread_sigmask` just before `main` returns, hook the item-6 test at the first `pthread_sigmask` after the waiting `flock`, and narrow every claim to what is guaranteed, naming any remaining instant at process start or exit where a signal may end the script without its `run-lock:` line; `review-fix.md:9`'s trailing clause reworded. A further finding confined to such a named instant is parked, since the lock's guarantee (no overlap, the lock held until the command ends) is intact and pinned by the selftest. | An exit line missing in a microsecond window, named in the docs. |
| R47 | A final cleanup round, all deterministic: poll `test_exit_holds_signals` at about 2 ms; selftest cases for SIGQUIT forwarding and the cannot-lock exit-4 line; exit 128+N with an interrupted line when a signal is already held as `lock_path` fails; a test that a held startup signal ends the command once it starts; the docs' wording and the `implement.md:1056` pointer; then a Haiku re-review, anything further confined to a named gap parked. | One more short round. |
| R48 (first) | Parked: `test_held_through_the_wait`'s `finally` waits only on the holder, so on a failed assertion its `sleep 6` command expires on its own within 6 s. Test-only, bounded, never persists. | A 6-second stray on a red selftest. |
| R48 (second) | Parked: the interrupted-while-finding-the-lock line also covers git ended by a route other than the signal. The line is still true, since a signal was held, and no other route is reachable in practice. | A slightly generic message. |

## 9. The ledger

The SDD ledger is copied verbatim beside this file as `2026-10-24-implement-one-writer-a-ledger.md`.

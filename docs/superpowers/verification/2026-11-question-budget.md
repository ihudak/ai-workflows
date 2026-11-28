# QUESTION-BUDGET — a question budget for the BRD route — verification record

**Branch:** `feat/question-budget`, head `10ef65f44` (the merge of `origin/main`, the last commit before this record's refresh; the last commit before the record itself was `7853c4285`, the residual fix for the final review's NB1 and NB2), on the base `a7a093a8c` (`git merge-base HEAD origin/main` prints `a7a093a8c47a392f8933196b2e23c3ed11d3d6e6`). `origin/main` was merged into the branch at `10ef65f44` before integration, and the gates in *The gates on this tree* were re-run on the merged tree. **Releases:** `workflows-core` 1.105.0 and `product-workflows` 3.92.0, each dated 2026-11-27 (`grep -m1 -n '^## \[' plugins/workflows-core/CHANGELOG.md plugins/product-workflows/CHANGELOG.md`, and `"version"` in each `.claude-plugin/plugin.json`). **Design:** `docs/superpowers/specs/2026-11-26-question-budget-design.md`; **plan:** `docs/superpowers/plans/2026-11-26-question-budget.md`. Every figure below was obtained on that tree, on 2026-11-28, by the command beside it; none is copied from a plan, a report, a ledger or another record. The one exception is the goal-9 measurement, which cannot be re-run on the tree and says where it comes from. `git status --short` printed nothing before the commit that carries this record.

`git diff --stat a7a093a8c HEAD | tail -1` prints `68 files changed, 7686 insertions(+), 752 deletions(-)` at `10ef65f44`, before the commit that refreshes this record.

## The five Review Focus lines

Each line names the registry self-test cases in `python3 plugins/product-workflows/scripts/question-registry.py --selftest` that pin the mechanism, and the text that makes the route use it. Commands and references are cited by heading and a short quoted snippet.

1. **A re-run over a round written before this ships** (no registry, no `questions` account line).
   - Cases `init_from_existing_states` (a round whose questions already stand answered, applied, merged, dropped, tabled, deferred or auto-closed builds a registry whose account closes) and `init_and_account_closes`. Companions: `init_refuses_existing_registry`, `init_and_add_refuse_a_malformed_question`.
   - Text: `plugins/product-workflows/commands/brd-interview.md`, *Phase 4*, *The question registry*: "Every other question enters open" after the states already on file are carried into `init`; *Phase 9*, "append the baseline line §8 fixes for each it lacks", which names nothing new and pins the old reading to what was there.
   - The plan also pins it by a live check, owed (below, item 1).
2. **A held `[C]` whose bundle exists but cannot be read.**
   - Cases `carried_refuses_all_but_proposed` (a carried question refuses every event but `proposed`, and `proposed` only with an answer) and `carry_marks_a_held_question_carried`. Companions: `applied_on_C_refused`, `retag_moves_counts`.
   - Text: `commands/brd-interview.md`, *The question registry*: "every held `[C]` whose entry is on file enters carried where such a directory, or a markdown file in it, exists and cannot be read, since no reading can say which questions it carried"; the same file's *A held `[C]` an answer reaches*: "once **carried** … is never edited"; and the resumed run's carried check in the same section.
3. **An operator who answers every question in free text.**
   - No registry case pins it: the registry records events, and reading the words is the command's own work. Nothing runs the prose, so a reviewer's reading and a live run are what pin it.
   - Text: the sentence "**A typed answer is read as the option it expresses**" (`workflows-core:question-budget` §4) stands at every prompt of both walks — `commands/brd-intake.md`, *Phase 4 — Confirm defects*, and `commands/brd-interview.md`, *Phase 6 — Put each `[V]` to the operator*. `grep -n 'read as the option it expresses' plugins/product-workflows/commands/brd-intake.md plugins/product-workflows/commands/brd-interview.md` prints 5 lines in the first and 6 in the second.
   - The final review's Area B found Review Focus 1 to 4 sound by reading (`final-review-B.md`); the plan's live check for this one is owed (below, item 2).
4. **A compaction or session stop mid-sitting.**
   - Cases `add_appends_in_order_and_counts_strategic` and `init_and_account_closes` pin the registry file that a resumed run reads back; `atomic_write_leaves_no_temp` pins that an event is written whole or not at all. The saved dispatch and the answers recorded through the run folder are `run-folder.py`'s, pinned by its own self-test, which this record does not re-run.
   - Text: `commands/brd-interview.md`, *Phase 0 — Resolve inputs and gate the grounded BRD*, step 8's run folder: "So a run stopped mid-sitting — by an abort, at a compaction or at a restart — resumes at its next unanswered question with every answer kept"; *Phase 6*, *Then the answer is applied forward*: "Write it with `put <folder> 'scratch/p6/applier/<round>-<position>.json' --from -` — a resumed run that finds the file reads it and builds none". `commands/brd-intake.md` carries the same for the walk's answers.
   - Where only a reviewer's reading pins it: that each phase after a resume reads the saved file and never builds its input again was checked by the task reviewers against the input-building rule, and by Area B (`final-review-B.md`). The live check is owed (below, item 3).
5. **An applied answer whose source decision, in a sibling slice, is superseded at `/brd-reconcile`.**
   - Case `reopen_cascades_cross_brd` (`reopen --follows PRD-7-02/[VD#4]` reopens the answers applied from that cross-BRD form, and from the question applied from them, and not the one applied from a bare `[VD#4]`). Companion: `reopen_cascades_transitively`.
   - Text: `commands/brd-reconcile.md`, *Phase 10 — The propagation sweep*: "`applied_from` is `<BRD-KEY>/<id>` for an id of that set — the whole value", whose records get a `Reopened <YYYYMMDD>:` paragraph naming the decision they were applied from; and `commands/brd-interview.md`, *Phase 3 — Generate the round's question set*, the basis-moved test: "**It takes, too, a record whose basis moved, not in flight**", which reopens at its next interview an applied record whose source decision reads `reopened`, `superseded` or `withdrawn`, or, in the cross-BRD form, carries a `Reopened` paragraph dated on or after the day it was applied.
   - Area C found Review Focus 5 delivered (`final-review-C.md`); the residual-fix re-review found the final fix wave's changes to it addressed. The live check is owed (below, item 11).

## The gates on this tree

Each was run alone, on this tree, with the record in place; its own last line and exit are given.

| Gate | Result |
|---|---|
| `python3 scripts/validate-catalog.py` | `0 error(s), 2 warning(s) across 1 repo(s).`, exit 0; the two warnings are the accepted ones, below |
| `./scripts/check-id-grammar.sh --root .` | `PASS: no dash-form requirement IDs under .`, exit 0 |
| `./scripts/check-id-grammar.sh --baseline` | `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`, exit 0 |
| `./scripts/check-docs.sh --root .` | `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`, exit 0 |
| `python3 scripts/reference-parts.py check-parts` | `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, exit 0; it also prints 135 advisory `FLAG` lines (`grep -c '^FLAG'`), none of them a failure |
| `python3 scripts/reference-parts.py check-citations` | `reference-parts check-citations: PASS -- 4 split reference(s)`, exit 0 |
| `python3 scripts/reference-parts.py check-questions` | `reference-parts check-questions: PASS -- 39 command(s) load the question rules before their first question`, exit 0 |
| `python3 scripts/reference-parts.py check-branch-check` | `reference-parts check-branch-check: PASS -- 24 command(s) run branch-check`, exit 0 |
| `node scripts/mermaid/check-mermaid.mjs --root .` | `PASS: all 52 mermaid blocks in 1299 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`, exit 0; `scripts/mermaid/node_modules` exists on this machine, so it was run |
| `python3 plugins/product-workflows/scripts/question-registry.py --selftest` | `selftest: 28/28 passed`, exit 0; 28 lines `ok   case_<label>` |
| `python3 plugins/product-workflows/scripts/bundle-scan.py --selftest` | `SELFTEST PASS (128 cases, 0 failed)`, exit 0 |

**The two accepted warnings.** `validate-catalog.py` prints `CLAUDE.md is 36122 characters, nearing the 40000 limit` (its warn line is 36,000) and `.claude/rules/workflows-core.md is 20592 characters, past 20000`. Both are recorded warnings, not failures: the first is the ceiling `CLAUDE.md` states, the second the ledger's accepted T2-d warning, to be split at that file's next edit.

**The other `run:` steps of `.github/workflows/validate-catalog.yml`.** Of the steps listed there, the chain above and the two self-tests the brief names were run. The rest were not run here and are left to CI: the self-tests of `validate-catalog.py`, `check-id-grammar.sh`, `check-docs.sh`, `reference-parts.py` and `check-mermaid.mjs`; those of every other script (`secret-scan`, `run-state`, `pieces`, `architecture-harvest`, `promotion-signals`, `proposal-record`, `ledger-evidence`, `register`, `weakness-classes`, `key-discovery`, `backlog-lines`, `bounded`, `lineage`, `tree-snapshot`, `run-folder`, `session-branch`, `specs-git`, session cost and the status line); the three copied-scripts `cmp` loop; the specs-git mutants check; and the `npm ci` install of the mermaid parser, which this machine already has. The branch changes none of those scripts.

## Goal 9 — the measurement

The design's goal 9: **"Measured on the engagement's shape: replayed on a synthetic slice of that shape (below, *Constraints*), intake asks at most the budget plus one table, and the interview reaches a state where the remaining detailed questions fit in a few sittings after at most three strategic sittings. This is a target to measure against, not a promise."**

**Where these numbers come from.** They are not re-derivable on this tree. They are the maintainer's measurement of the texts at `bdda33b6f` (the final fix wave, before the residual fix), recorded in the branch workspace's `goal9-score.md`, which the workspace keeps outside version control. The residual fix after it changed the interview's put-singly path and the registry's exception file, not the plan's counts, and the measurement was not repeated.

**The method.**
- A generated synthetic slice: 300 rows, 200 intake candidates, 640 interview questions.
- A blind measurer that played `question-planner` and `answer-applier` from their files.
- The registry script was run for real.
- The operator always took the recommended answer: the best case.
- A scorer compared every closure with the generator's answer key.

**The numbers.**
- **Intake:** 121 prompts against 25 + 1. Missed.
- **Interview:** 125 `[V]` open after three strategic sittings, against 50. Missed.
- **Scoring.** No false merge, and no false closure that the question texts contradict. Of the reworded copies, 5 pairs were missed and 0 exact ones.

**Both targets are missed.** Ruling F-k reports goal 9 as missed on this fixture, with the fixture's defects stated as the method's limits, and not as a pass by projection. The fixture had four defects, and each limits what the measurement shows:
- **Code-grounded intake candidates the branch never raises.** Most of the 200 intake candidates were "absent in this repository" findings from code grounding. `/brd-intake` reads no code, so the branch would never raise them; the replay put them to a walk that does not ask them. The 30 genuine wording candidates alone took about 16 questions and the table in the replay, which fits the target, but that is a projection from a subset and not a replay.
- **An 8-round state the route cannot reach.** The 640 questions sat in eight open rounds, and the route opens a later round only when every earlier one is closed. They also carried several questions per row, and many cited rows the grounding rules leave silent.
- **Semantically loose key strategies.** Each theme's questions were split between two "strategic choices" at random, so a strategic question could not honestly cover many of the questions the key said it settled. A planner that obeys the rule that each option decides every question it covers could not reach the target on this fixture.
- **Absence findings without controls.** Absence findings carried no control and some cited findings carried no verifier outcome, so the interview's own gate would stop the run; the measurer replayed past it.

**What stands as a branch result.** Granting the fixture's question set, honest family grouping covers about 2.5 `[V]` per strategic question: a family-shaped backlog needs more than three sittings of 25 to reach 50.

**The real engagement.**

> The branch was also replayed locally on a real engagement's slice, with every closure checked against that engagement's recorded decisions. Its results were reported to the maintainer and are not recorded here.

## Owed — only a live run can show

None of the following has been run; each is owed, and nothing above claims it. Each cites its section in `docs/superpowers/to-test-on-real-project.md` (`grep -n '^## Question budget' docs/superpowers/to-test-on-real-project.md` prints the six headings) and is named in one line with its passing condition. Every item runs on a throwaway copy of a specs tree that is a git repository, over a synthetic BRD.

*Increment 1* (`## Question budget, increment 1`):
1. **A typed answer is read as the option it expresses** (`/brd-intake`; Review Focus 3). Passing: three typed answers are recorded as *Ask the customer, about a narrower point*, *wording is clear* and a clarifying question, with no dialog put twice and no "why" after a typed answer.
2. **A stop mid-walk, then a resume** (`/brd-intake --budget 5`). Passing: the walk stops with its stop message, and a resumed run keeps every answer and every reopen, reads the source again nowhere, and folds no reopened candidate back into its group.

*Increment 2* (`## Question budget, increment 2`):

3. **A re-run over a round written before this release** (`/brd-interview`; Review Focus 1). Passing: every line on file in the round record and `decisions.md` is unchanged, the baseline is appended once, and the account closes.
4. **A stop mid-sitting, then a resume** (Review Focus 4). Passing: the second question that one answer settles is never put, a quit session resumes at *Resume* with the round's questions and positions as the first session's, and every answer and applied answer is kept.
5. **One question per requirement row, whatever the number of repositories.** Passing: no question for a claim one repository settles, and exactly one for a row on which every repository reads `NOT-PROVABLE`.
6. **A sitting ends at its budget, with a delivery decision that waits on the customer, and a held `[C]` an answer reaches.** Passing: each counted prompt is preceded by `Q<n>/5`, a deferred `[V]` naming its held `[C]` does not stop the package, and an answer that settles a held `[C]` records a proposal beside it and never answers it.

*Increment 3* (`## Question budget, increment 3`):

7. **A round of several hundred questions reaches the detailed walk within three strategic sittings** (goal 9 on a real run). Passing: the scale warning before the first question, no more than three strategic sittings before the walk is recommended, an account that closes, and no strategic question covering a question another already covers.
8. **A split, a deferral and a resume at a strategic question.** Passing: a typed split is recorded as dropped at the operator's request and its covered questions are put one by one; a deferred strategic question leaves its covered questions open.

*Increment 4, the customer's prompt* (`## Question budget, increment 4 — the customer's prompt`):

9. **The prompt opens part 7 with the rules and the strategic questions, and drops or withdraws a proposal whose decision moved.** Passing: part 7 opens with the rulebook's customer block word for word, strategic questions first, each coverage naming only questions the prompt renders; a proposal on a reopened or re-decided decision is under *7.3 Other questions* with its withdrawn line; a carried entry is never rewritten; the plugin-free scan finds nothing in the prompt.

*Increment 4, `/brd-reconcile`* (`## Question budget, increment 4 — /brd-reconcile reads applied answers`):

10. **An answer and the answers applied from it are confirmed as one group, and a proposal whose basis has moved is named at confirmation.** Passing: the group array carries `(you'll be prompted)` on its second option, each applied row freezes as `taken: applied` with `applied_from` the answer's `[CD#n]`, a covered question with no row stays held, and a moved basis is named with nothing marked `(Recommended)`.
11. **A sibling's supersession reopens an answer applied from it in the other slice** (Review Focus 5). Passing: the sibling's applied record reads `reopened` with a `Reopened` paragraph in the `<BRD-KEY> [VD#n]` form, no sweep picker is shown for it, and the next `/brd-interview` puts its question again.

*The final review's fixes* (`## Question budget, increment 4 — the final review's fixes`):

12. **A question you reopen is asked, not closed again** (the residual fix, NB1 and NB2). Passing: a question reopened at an end-of-sitting list, or named as a table exception, is put singly in a later sitting, never listed applied again, a table row or covered by a strategic answer, absent from the `candidates` of a later applier input, and a row named at the table's second ask appears in `exceptions-<sitting>.json` before any row is recorded.
13. **An answer applied from a sibling's decision moves when the sibling re-decides it in place.** Passing: the applied record's `argumentation` opens `Applied from <A> [VD#m] on <YYYYMMDD>:`, a later `Reopened` paragraph on the source moves it, and one dated the day before moves nothing.
14. **A re-deferral drops a question the customer has answered, and a planner that fails twice leaves the intake walk going.** Passing: the new `Blocked-on` line names only the `[C]` still held; the intake walk puts the rest one by one in candidate order, five a sitting, and names the planner's failure as a defect of the run.

## Known limits shipping with the release

From each plugin's 2026-11-27 `CHANGELOG.md` section, *Known limits* (`workflows-core` 1.105.0 has one line, a lifted limit), summarised:

`product-workflows` 3.92.0:

- Four limits of earlier increments are lifted: a proposal is now shown by `/brd-package` and tested by `/brd-reconcile`; a strategic `[C]` reaches the customer first, under 7.1; a customer's answer to a strategic `[C]` closes what it covers through rows marked `applied from`, confirmed by `/brd-reconcile` as one group; and `answer-applier` leaves a strategic `[V]` untouched.
- A proposal that follows another slice's or a `depends-on:` BRD's decision is never shown once that decision has been reopened, even where it was re-decided to the same answer or proposed again since, because a re-decision in place writes no withdrawal into this slice.
- A reopening of another BRD's decision dated the same day an applied answer was dated counts as after it at `/brd-interview`, and at `/brd-reconcile` a reopening dated the package's own day counts as after it: the safe side both times.
- A re-decision a stopped `/brd-interview` left standing withdraws no proposal where the run is started over rather than resumed.
- A record of a third register applied from one the sweep reopens is not swept; that register's next `/brd-interview` reads the basis as it then stands.
- Earlier limits that stand: a resumed run puts the stop-rule choice twice; some closes raise no code-defect question; a held `[C]` already in the question set is never merged or dropped.

Parked or deferred by the final review (the ledger's lines marked `parked`, `minor (deferred)` or `stay parked`, and `final-review-A.md`, `-B.md` and `-C.md`), summarised:

- **NB3.** `workflows-core:question-budget` §2 says a question is put only where all three tests hold, unqualified; §8's strategic paragraph is the exception, and §8 names §2.
- **NB4.** An ambiguous "it" in `.claude/rules/brd-route.md`'s `/brd-package` map line: a maintainer file, not executed prose, fixed with that file's next edit, which must split it.
- **The cross-BRD applied-record spelling** (the out-of-scope `[CD#n]` spelling): the record names only `<BRD-KEY> [VD#n]`, though `applied_from` may name `<BRD-KEY>/[CD#n]`; this predates the fix wave.
- **C8.** The proposed answer in part 7.1 has no fixed label, so a miss falls to "cannot be read", the safe side.
- **C9.** `.claude/rules/workflows-core.md` is over its 20,000-character warning (the accepted warning above).
- **A summary sentence in the references page** that could also name the reopened exception in its first clause: true as written, optional tightening.
- **Deferred minors**, the per-task ones the reviewers triaged "stay parked": the foundation reference's drop-row and merge wording and the planner's missing output channel for a cross-tag duplicate; the interview's resume paths (a registry exit 2 on resume that drops earlier sessions' answers, the budget counter's drift after a crash between two writes, a run folder from an earlier release mid-Phase 6, whose population is none because every increment ships in one pull request); the package and reconcile prose (a clause that hangs off the save-where clause, a bold sentence that reads exceptionless before its exception); and the stop rule's `<k>` recount after a carried check frees `[V]`s. Each is a ledger line in the branch workspace, which is not version-controlled.

## Follow-up owed

**The text gaps G1 to G9 the goal-9 replay found** (`goal9-score.md`, *Text gaps the replay found*; maintainer findings, not fixed on this branch):

- **G1.** `workflows-core:question-budget` §2 drops a question that changes nothing "in every place", but `question-planner`'s mode `intake` has no drop, so a candidate whose only reason is that the code differs still costs a question.
- **G2.** The intake walk-list overrides the per-candidate recommendation: an `unsourced` candidate is auto-confirmed where low confidence recommends "wording is clear", and a `duplicate` is noted without a question where the recommendation is to ask (`commands/brd-intake.md`, *Phase 4*).
- **G3.** Sitting 1 of intake always puts two multi-item prompts, the walk-list and the tail table, against goal 9's "budget plus one table" (`commands/brd-intake.md`, *Phase 4*).
- **G4.** A `duplicate` or `conflict` that names no other row folds nothing, and at the write step a restatement naming no row leaves no `restates` note (`commands/brd-intake.md`, the write step after *Phase 4*; `references/brd-format.md` §2).
- **G5.** `question-budget` §5 says to correct a mis-tag, but `question-planner`'s output has no field for one and `commands/brd-interview.md`'s merge step has no step that corrects it.
- **G6.** `answer-applier` has no rule against recording a proposal a strategic `[C]` already holds; `question-planner` has one (`agents/answer-applier.md`).
- **G7.** The first end-of-sitting list carries every pre-sitting merge and application, a list of about 250 lines in the replay under one "all correct", a weak check (`question-budget` §10; `commands/brd-interview.md`, *Phase 6*).
- **G8.** A strategic `[C]` covers held `[C]`s and closes none, so the held count rises, and the stop rule ignores `[C]` (`commands/brd-interview.md`, *Phase 5.5*).
- **G9 (outside the branch).** `workflows-core:grounding-format` §2.2's example of an absence with a control recorded `NOT-PROVABLE` contradicts its §3, where an absence is `AMENDED` or `REWRITTEN`.

**Four more points, which another replay found:**

- **R1.** `/brd-interview` Phase 4 forbids merging or dropping a held `[C]` whose entry is on file in `customer-questions.md`, so a re-run over a slice whose package is already on file merges no `[C]` duplicate.
- **R2.** `question-planner`'s mode `intake` fills `ask` to the budget less one, ignoring the walk-list's slot. The command's count governs; the two texts disagree.
- **R3.** The end-of-sitting list has no size limit. In a measured replay, sitting 1's list ran to about 190 lines under one "All correct", a weak check on the closures it lists. This is the same point as G7.
- **R4.** Of the closures the replay checked against recorded decisions, the wrong ones came mostly from strategic questions whose recommended option fitted most, but not all, of the questions it covered, and second from `answer-applier`. The end-of-sitting list (R3) is where an operator would catch them.

# Live checks of 2026-10-26 — `docs/superpowers/to-test-on-real-project.md` on the e2e copies

Each run below used the e2e copies (`ihudak-e2e/bookstore`, `ihudak-e2e/bookstore-specs`) through `~/e2e-copies.sh`, with the plugins installed from this marketplace; each run names the versions its session loaded. The session transcripts are under `~/.claude/projects/-workspace-e2e-bookstore/` on the test machine, named by session id. Each item a run settles is deleted from the to-test list in the commit that adds its record here; each defect a run finds goes to `docs/superpowers/to-fix.md`.

## Run 1 — the Epic pickers (B16-3)

**Setup.** Six throwaway PRDs were added to the specs copy's `main` (`a927da9`): PICK-1 to PICK-4 with a flat `specification.md` and 2, 3, 4 and 5 Epic folders, PICK-5 and PICK-6 with no flat spec and 4 and 5. Every Epic folder held `epic.md` and `specification.md`. The sessions loaded workflows-core 1.53.0, dev-workflows 4.36.1 and product-workflows 3.43.0. In one Opus session, from the code copy, each command was typed in turn, and its Epic picker was answered with Esc and `/clear`. `/specify`'s repo-refresh question, asked before its picker, was answered *no refresh*.

| # | Command | Session | Array | Expected | Result |
|---|---|---|---|---|---|
| 1 | `/implement PICK-1` (flat, 2) | `27693491` | 2 Epics, broad slice | the same | pass |
| 2 | `/implement PICK-2` (flat, 3) | `be362f30` | 3 Epics, broad slice | the same | pass |
| 3 | `/implement PICK-3` (flat, 4) | `3c74aa17` | 2 Epics, broad slice, *Another Epic* | the same | pass |
| 4 | `/implement PICK-4` (flat, 5) | `ef0bcd0b` | 2 Epics, broad slice, *Another Epic* | the same | pass |
| 5 | `/implement PICK-5` (no flat, 4) | `acda797d` | 4 Epics | the same | pass |
| 6 | `/implement PICK-6` (no flat, 5) | `fdc91dd0` | 3 Epics, *Another Epic* | the same | pass |
| 7 | `/specify PICK-2` (3) | `e0b4b223` | 3 ● Epics, broad spec | the same | pass |
| 8 | `/specify PICK-3` (4) | `4bde5b38` | 2 ● Epics, broad spec, *Another Epic* | the same | pass |

**The arrays: pass in all eight.** The markers were right too: ○ for an Epic with a specification and no design under `/implement`, and ● done under `/specify`.

**The prose list: failed in all eight.** B16-3 expects "the prose list above the prompt names every Epic in every case", as `workflows-core:epic-picker` *The cap* and all three picker commands require. No run printed it. No text block, and no thinking line shown before the picker, named more than one Epic key. In the four overflow cases (3, 4, 6 and 8), the Epics left out of the array were named nowhere, yet the remainder option reads *Another Epic from the list above*, and case 3's question says "(listed above)". Filed as to-fix LC1.

**Also seen:**
- The `(Recommended)` marker sat on the first ○ row in cases 4, 5 and 6 and was absent in cases 1, 2 and 3, though cases 3 and 4 have the same shape. Filed with LC1.
- Case 1's narration called both Epics "unspecified", though each has a `specification.md` and the picker's own option text says so.

## Run 2 — `/specify BOOK-1-02` (PR5, B16-4, B16-2)

**Setup.** A `pre-commit` hook in the specs copy refused any commit that staged a `specification.md`, so the handoff's deliverable commit would fail while the session-artifact commit went through. The specs copy's `main` was at `a927da9` and the code copy at `master` `af46545`. One Opus session, `2a06e283`, ran from the code copy and loaded workflows-core 1.54.0 and product-workflows 3.44.0. The driver chose *no refresh*, took each `(Recommended)` answer, and confirmed every play-back. After the first review, the driver folded its findings into the fix cycle. For the re-review's BLOCKER, the driver gave the reviewer's fix as manual fix notes, then applied the ten findings left open and accepted the handoff. The run cost $19.50. Afterwards the hook was removed, and the demo check printed `same` on every line.

| Item | Expected | Seen | Result |
|---|---|---|---|
| PR5, Stage 4 | the `Overlap read:` line at the play-back | `Overlap read: 5 triggers, 4 imports, 5 failure paths, 4 [AD#N] Rules — no conflict`, with its lists | printed |
| PR5, whole specification | the line at the play-back before the first `spec-reviewer` dispatch | no play-back text: a narration paraphrase and the question; the line went to `_session.md` only | not printed |
| PR5, the read | a conflict of a listed kind caught before the review | three `[AD#N]` departures read as "no conflict", all found by the reviewer | trigger fired |
| B16-4 | `Phase handoff: NOT handed off — the commit failed (…)`, and the `/dev-workflows:design` offer with the merge clause naming the branch | both, verbatim, naming `spec/BOOK-1-02-storage-restock-notice` | pass |
| B16-2 | `Changed in substance since: <ids>` in the final report and the session record | both name the ids and sections; no wording-only edit is listed | pass; the pull request body was not reached |

**PR5: the line printed, and the read missed three conflicts.** Both of to-fix PR5's triggers fired.
- At the whole-specification gate the run printed no play-back. Its narration said it "confirmed no conflicts across triggers, imports, failure paths, and rules", and the literal line went only into `_session.md`.
- Both reads listed four `[AD#N]` Rules and called them kept. The specification departed from three Rules, and the reviewer found each:
  - [U02/AC04] skips the notice once a notice limit is reached. [AD#4]'s Rule calls alerts once after every committed restock and lets [AD#5] recover only a call that "was lost or failed". This was the first review's only BLOCKER.
  - [U01/AC01]'s 5-second send budget lets an alert show 35 seconds after a restock, where [AD#9] says 30. The first review found this as a MINOR.
  - The out-of-scope line that leaves a return racing a sale to [AD#5]'s sweep is a second departure from [AD#4]. It was the re-review's BLOCKER, found after the cap was spent.
- The first departure came from the grill itself. D1's question asked whether storage "may skip the notice for a restock entirely (alerts' sweep then picks it up within the one-minute limit)". It recommended skipping and never named [AD#4]. Stage 4's read then called [AD#4] kept, taking [AD#5]'s sweep to cover the skip.

Filed under to-fix PR5, which is now a fix.

**B16-4 passed, and the run found a bug beside it.** The final report carried `Phase handoff: NOT handed off — the commit failed (pre-commit (e2e live check B16-4): refusing a commit that stages a specification.md). The deliverable is staged on spec/BOOK-1-02-storage-restock-notice, not committed.` Its next step offered `/dev-workflows:design BOOK-1-02` `(once the deliverable staged on spec/BOOK-1-02-storage-restock-notice is committed, pushed and its pull request merged)`. But the orchestrator ran switch, add, commit and push in one shell command, and kept the commit's status with `rc=$?`, which cancels `set -e`. So it pushed an empty `spec/BOOK-1-02-storage-restock-notice` to the copy's origin at `main`'s tip. The run said so in its final report and drafted a bug report. Because that push set an upstream, `commit-artifacts` later pushed the session-artifact commit (`dcbf45c`) to the same branch. Filed as LC2.

**B16-2: the final report and the session record pass.** `_session.md`'s version line reads "BLOCK (re-review) was reached before the manual fix notes and the ten applied findings, which followed it; the current text has not been reviewed. Changed in substance since: Scope › Open questions (…); [U01/AC01] (…); [U01/AC02]–[U01/AC05] (…); …". The final report gives the same list as bullets under "Changed in substance since the verdict:". The wording-only edits, such as "held notices" in Scope, appear only in the count of edits. The edits after the verdict also renumbered [U01/AC02]–[AC05], so the listed ids name other criteria than the reviewed text did. The run said "renumbered from AC03–AC06" beside them, and that served, so nothing is filed. The commit failed, so the pull request body was not reached, and B16-2 stays on the to-test list for that part.

**Also seen:**
- The first review returned BLOCK with 2 MAJOR, 10 MINOR and 5 NIT findings beside its BLOCKER. No rule says what becomes of those findings during a BLOCK fix cycle: the offer to apply them follows only a verdict that is not BLOCK. The run asked a question of its own, *Fold them all in (Recommended)*, so that the re-review saw the edits. Filed as LC3.
- After *Provide manual fix notes (you'll be prompted)*, the run asked for the notes in plain text and did not say it was waiting. The session sat 11 minutes until the driver typed "done?". The run then offered the reviewer's own fix as a choice. This is to-fix PR7's second instance; the `/design BOOK-1-01` run drew the same "done?".
- The run wrote four feedback entries to the specs copy, two of them the bugs above. Its second entry says the read skipped scope lines. But [U02/AC04] is a criterion, and the read passed that too.

*Found in run 4's measurement:* run 2's second offer, after its re-review, printed no list either (LC6).

## Run 3 — `/design BOOK-4-01` (433-1, PR3, B16-2)

**Setup.** A setup script saved run 2's leftover branch and its staged files aside, then deleted the branch locally and on the copy's origin. It added a small test PRD to the specs copy's `main` (`9485947`): BOOK-4, with one Epic, BOOK-4-01 (`target: bookstore:storage`). The Epic's merged `specification.md` asks for a read-only `GET /api/v1/storage/in-stock-count` that answers `{"count": <n>}`, in 3 criteria and 7 test cases. The code copy was at `master` `af46545`. One Opus session, `a6c2f90c`, ran from the code copy and loaded workflows-core 1.55.0 and dev-workflows 4.38.1. The driver chose *no refresh*, took each `(Recommended)` answer, applied the open findings after both reviews, and took the re-review and the handoff. The run cost $26.92 and opened pull request #14 on the specs copy. Afterwards the demo check printed `same` on every line.

The hand edit for 433-1 was meant to be planted while the whole-design play-back waited for its answer, but `design.md` did not exist then (see the last paragraph). So a watcher planted it instead. It appended a `## Pieces` section 0.9 s after the run's one write of `design.md`, while the run was still in Phase 5. The section held a stale `_N/A — …` line, a `Reason:` line, and two pieces, `storage-endpoint` and `storage-query`. Phase 5.5 began a minute later.

| Item | Expected | Seen | Result |
|---|---|---|---|
| PR3 | no `## Pieces` on a small Epic | the `design.md` the run wrote had no `## Pieces` section, and no question raised pieces | pass |
| 433-1, the parse | `malformed`: `the section holds an _N/A line beside other lines` | exactly that | pass |
| 433-1, the fix | one fix, a second parse, and a removal only where the fix does not settle it | one fix kept the `_N/A` line, and the second parse printed `none` | pass |
| 433-1, no question | the check asks nothing | the run asked which reading the fix should keep | fail: LC5 |
| 433-1, the Final report | each defect, fix and removal named | the malformed section, its two pieces beside `_N/A`, and the fix | pass |
| B16-2 | `Changed in substance since:` beside the verdict in the pull request body | present, naming three sections; no criterion changed | pass for sections; the id case not reached |
| Overlap read | the line at the whole-design play-back | `Overlap read: 5 failure paths, 3 triggers, 1 import, 0 [AD#N] Rules — no conflict` | printed |

**PR3 passes.** The grill settled seven decisions. None of its questions raised pieces, and the `design.md` it wrote had no `## Pieces` section, which means one piece. PR3 is deleted from `to-fix.md`.

**433-1: the parse and the fix pass, but the run asked a question.** After the pre-lint, `pieces.py parse` printed the expected defect. The run then asked "Which reading should Phase 5.5's one fix keep?", with three options: *Keep only the _N/A line (Recommended)*, *Keep the two pieces, drop _N/A*, and *Remove the whole section*. Its narration gave the reason: "Since I didn't write this section and the fix requires discarding part of it, I'm flagging it for your review rather than deciding unilaterally." Phase 5.5 says "Like the pre-lint, it asks nothing", but Phase 5's **Pieces** bullet says Phase 5.5 checks "the section the run wrote", and no line covers a section the run did not write.

The setup was not the item's: the section came from outside the run while it ran, not from a `design.md` the run was revising. A revising run also meets a section it did not write, though, so the gap holds there too. Filed as LC5, which carries the re-test, and 433-1 is deleted.

**B16-2: the pull request body carries the line.** It reads: "PASS WITH RECOMMENDATIONS (re-review) was reached before 5 edits applied after it, which followed it; the current text has not been reviewed. Changed in substance since: `## Migration / rollout / backward-compatibility` (rollout order, rollback target), `## Observability & release verification` (…), `## Test strategy` (route edge-case tests). No `[Uxx]`/`[ACxx]`/`[TCxx]` changed." `Findings left open: none` follows it. `_design-session.md` records the same line. The edits changed text that carries no id, so the line names sections, as the rule asks. No edit changed a criterion, so an id in a pull request body is still unseen, and B16-2 stays on the to-test list for that case.

**The run wrote `design.md` after the grill, not during it.** Phase 5 says "authoring `design.md` live" and "clear the confirmation gate before writing each section". The run asked all its grill questions, played the whole design back once, and wrote `design.md` in a single write after the confirmation. While writing, it changed D4: the test class moved to `webEnvironment = RANDOM_PORT` and gained a real-HTTP database-failure test, because MockMvc rethrows unhandled exceptions. Its narration said so ("Let me know if you'd rather drop that failure test"), but it asked no question, and the play-back the driver confirmed had not carried the change. Every `/design` transcript on the test machine shows the same order: in all seven that wrote `design.md`, every grill question came before its first write. Four then wrote it behind two to four section gates. Two of those four ran a whole-artifact gate over the changes made while writing, one of them over "the three post-gate changes above". The other three runs, this one among them, played the whole design back once and wrote it afterwards, so no gate followed the writing. Filed as LC4.

**Also seen:**
- Both reviews returned PASS WITH RECOMMENDATIONS with a MAJOR in the rollout. The first review found that the rollout built an image name the Deployment never pulls. The re-review found that the first fix rolled back to a tag that publishing moves. The second fix was applied after the cap was spent, so it is unreviewed, as the version line says. The run's own feedback entry asks the grill to read which image a deploy pulls. This is the second instance of to-fix PR6, which the `/design BOOK-1-01` run filed for the same image-name gap, and a line was added there.
- The run wrote three feedback entries to the specs copy. Its third entry concerns the planted section. It suggests documenting that "a section the run did not write is put to the user", the opposite of LC5's recommendation.

## Run 4 — `/product-workflows:epics BOOK-5` (B16-1, B16-2)

**Setup.** A setup script added a small test PRD to the specs copy's `main` (`84c1658`): BOOK-5, "Restock list", with `prd.md` only and no Epic. Storage lists the books at or below a low-stock threshold the operator sets. Of its five criteria, [AC#2] ("ordered sensibly") and [AC#4] ("a reasonable default") were left vague on purpose, to draw MINOR and NIT findings. One Opus session, `a6efb1f6`, ran from the code copy and loaded product-workflows 3.46.1 and workflows-core 1.58.0. The driver approved the plan and took each `(Recommended)` answer, the refresh question's *fetch + pull* among them: that fast-forwarded the code copy's `master` from `af46545` to `6942a24`, which the round's cleanup restores. The driver applied the open findings after both reviews and took the re-review and the handoff. The run wrote one Epic, BOOK-5-01 (`target: bookstore:storage`, 5 criteria and 4 stories, at the size limit), and left one `[NEEDS CLARIFICATION]` marker. It opened pull request #15 on the specs copy. It cost $17.09: `/feedback`, typed mid-run, wrote $8.89 of it under its own entry, its window running from the session start, and `/epics` wrote $8.20. Afterwards the demo check printed `same` on every line.

| Item | Expected | Seen | Result |
|---|---|---|---|
| B16-1, the fixer | `doc-fixer` takes the MAJOR findings only | the first review (PASS WITH RECOMMENDATIONS, 2 MAJOR, 2 MINOR, 3 NIT, all verified) sent its 2 MAJOR to `doc-fixer` | pass |
| B16-1, the first offer | each MINOR and NIT with its severity; a re-review remains | the 5 listed with severities just above the question, which said "(The cap's one re-review is still unspent.)" | pass |
| B16-1, *Apply them* | the orchestrator's own edits, each read against what it overlaps | 6 edits by the orchestrator; its overlap read caught two errors of its own (below) | pass |
| B16-1, the unspent re-review | offered next | offered and taken; PASS WITH RECOMMENDATIONS, 2 MINOR and 2 NIT, every claimed edit confirmed | pass |
| B16-1, the second offer | made once more, listing what is left open; no review after it | made, "(No review follows these edits.)", but its question's "listed above" pointed at a list never printed | fail: LC6 |
| B16-1, the version line | names the edits after the verdict | the report and the pull request name four edits and the marker | pass |
| B16-1, what the offer leaves out | no *Epic size* finding, unverified finding or user-resolved text | none; `doc-fixer` was told to keep the user's default-of-10 criterion, and did | pass |
| B16-2, the id case | `Changed in substance since:` with the criterion's id in the pull request body | "the guard criterion for [AC#5], which now carries the marker", beside three sections | pass |

**B16-1: both offers were made, but the second listed nothing the user could see.** The first offer printed the five open findings, each with its severity, above *Apply them (Recommended)*. It added a sixth item, marked "Raised by the fixer, not the reviewer": two lines `doc-fixer` had left looser than the guard it narrowed. On *Apply them*, the orchestrator made the edits itself. Its overlap read caught two errors of its own. It had moved the regression-pin story first, so "lands before stories 1–3" pointed at the wrong stories. And the literal "nine endpoints" would turn false once BOOK-4-01 lands, which the new Dependencies line names. It then offered the unspent re-review. After the re-review, it asked "Apply the re-review's open findings listed above to BOOK-5-01? (No review follows these edits.)". But between the re-review's return and that question, the only text printed was "Triaging the re-review. It returned PASS WITH RECOMMENDATIONS, no BLOCKER or MAJOR, and confirmed every claimed edit. Checking its new findings against the code:". The list existed only in the model's thinking, which reads "I've laid out the 4 fixes … for you to apply or clarify". The `escalation-rules` offer rule says "The question lists each with its severity".

Every offer in the copy's transcripts was measured: 24 offers in 17 sessions since 2026-10-19. Two printed no list at all, this one and run 2's second offer, which asked "Apply the ten edit-only findings the re-review left open …?" with 36 characters of text since the previous answer. A third, an `/implement` offer of 2026-10-25, named its two findings in the question without their severities. Both misses were offers after a re-review. Filed as LC6, which carries the re-test. B16-1 is deleted.

**B16-2's id case passes.** The re-review's verdict preceded four edits and the marker. The pull request body, under *Edits after the verdict*, reads: "The current text has not been reviewed. Changed in substance since then: the guard criterion for [AC#5], which now carries the marker; *In scope*, which now holds the `Config` allowance moved there from *Out of scope*; *Dependencies*, whose `Config` line now requires that existing `configs` rows still load; *Independent Test*, which now compares responses, not only shape." An Epic's criteria carry no id of their own, so the PRD's [AC#5], which the guard traces to, stands in for one. The final report lists the `StorageRepository` reference as a wording-only edit, apart from that list. With run 2's report and session record and run 3's sections, every form of B16-2 has now been seen, and B16-2 is deleted.

**`doc-fixer` decided a product question.** The first review's MAJOR on the guard criterion offered two readings of PRD [AC#5] ("every existing storage endpoint"): only the nine endpoints under `/api/v1/storage`, with an added `Config` field allowed; or every storage endpoint, `/api/v1/config` included. `doc-fixer` took the first and wrote "A field added to `Config` for the threshold is allowed." into *Out of scope*. The orchestrator flagged it as a product decision beside the first offer, the re-review raised the reading again as a MINOR needing a decision, and it ended as the run's one marker. It was caught because the orchestrator noticed, not by a rule. Filed as LC8.

**The repository question.** Phase 1 marks *Scan repos referenced by sibling/parent Epics under this PRD (Recommended — auto-derived)*. On a PRD with no Epic and no ARD nothing can be derived, so Phase 4 escalated (*No repos could be derived for BOOK-5*), and *List repos to scan manually* asked for the names in plain text. The driver logged it with `/feedback` mid-run: the question was easy to overlook, though the session stood in the `bookstore` repository. Filed as LC7.

**Also seen:**
- The run wrote seven feedback entries to the specs copy. Besides LC7 and LC8 and the overlap-read errors above: `code-scanner` cited lines 195–244 of a 72-line `ConfigController.java`, and said `Config` has "no integer value field" where it has two `long` fields, which the writer carried into the Epic until the first review caught it; the mid-run `/feedback` cost entry carried the `/epics` spend up to that point; and a `cd` in a verification command moved the orchestrator's working directory, restored with no damage.
- The style check's four NITs went to neither the fixer nor the offer, and the pull request lists them as left open: they are not review findings.

## Run 5 — not run

B16-5 needs a BRD slice whose interview has settled, for `/brd-package` to package. Neither BOOK-2 slice qualifies: BOOK-2-01's reconciliation of 2026-10-12 deferred four answers to another round, and BOOK-2-02 was never interviewed. Packaging one would have taken a `/brd-interview` run first, roughly $30–50 and an hour of answers to check one line of next-step text. The user chose to defer it to the next live run of the BRD route, and the item says so.

## Run 6 — `/security-workflows:scan --triage` under a moving register (SEC-G3: SEC-B1's session half, F15)

**Setup.** A setup script seeded the specs copy's register with one synthetic codebase scan at `6942a24`, recorded by `register.py` and pushed to `main` (`2b7b63b`): `[SEC#1]` CWE-79 in `rating-list.component.ts`, `[SEC#2]` CWE-319 in `book.service.ts`, both MEDIUM and open, in a record dated 09:05:30. In a scratch clone that never saw the seed, it recorded a second synthetic scan, a CWE-601 finding allocated `[SEC#1]` in a record dated 09:00:30, and held that record unpushed. A watcher pushed it, settling its own rebase with `register.py rebuild`, 4 s after the run asked its first triage question. From then on `origin/main` numbered CWE-601 `[SEC#1]` and the seeded CWE-79 `[SEC#3]`. One Opus session, `90f584a9`, ran `/security-workflows:scan /workspace/e2e/bookstore --triage` from the code copy on security-workflows 0.4.0. The driver chose *Decide each row*, marked `[SEC#1]` a false positive with the run sheet's evidence at line 23, and left `[SEC#2]` for later. The run cost $5.89.

| Item | Expected | Seen | Result |
|---|---|---|---|
| The batch question | *Decide each row* / *Decide all later* where no row's suggestion records anything | exactly that | pass |
| The evidence line | read at the evidence commit and shown beside the finding's `file:line` | read at `6942a24` (`this.ratings = data;`), but shown only in a command's output and the model's thinking | partial: LC6 |
| 7.1, the refresh | fetch, reserve the record the checkout lacks, plan again, move the answers with `rebase` | fetched, reserved `0001-20261027T090030Z-3945795c.json` from `origin/main`, planned again, ran `rebase`, which moved nothing | ran: LC10 |
| The answer's finding | the false positive on CWE-79, never on CWE-601 | the record names CWE-79 by `origin`; after the merge the register shows `[SEC#3]` CWE-79 false positive, confirmed, and `[SEC#1]` CWE-601 open | pass |
| The move in the report | `[SEC#1]` → `[SEC#3]` named, with the record it came from | named, but only from a dry rebuild the run made on its own initiative: "neither `plan` nor `commit` reported a move" | fail: LC10 |
| The closing push (F15) | where rejected, the settle line after the `Specs repo:` line | "push REJECTED …", then the `register.py rebuild` line with the plugin's real path, `git add` of both files, `rebase --continue`, push | pass |
| The settle line itself | settles the register and pushes | run as printed: two conflicts, `rebuild` cleared both, `rebase --continue` and the push went through (`c0f3a9c`) | pass |

**The answer reached the right finding, by `origin` rather than by the step meant for it.** After the answers, 7.1 fetched `origin/main` and reserved the planted record. It planned again, and `register.py plan` printed `"renumbered": []`, with `[SEC#1]` still CWE-79. The run read that as "The reserved record took number 3", and its `rebase` changed nothing. `plan` numbers only past a reserved record and past the moves its merge will make; it never renumbers the checkout's own findings, so in 7.1 the `rebase` has nothing to act on. The record the run committed carries the decision with CWE-79's `origin` beside `id: 1`. Claude then ran the run's printed settle lines, as written, on the specs copy. The merged register shows the false positive on CWE-79, now `[SEC#3]`. The REGISTER_MOVED path of 7.2, where the checkout itself gains a record while the run plans, was not reached. The script-level replay of `docs/superpowers/verification/2026-10-15-security-workflows-scan.md` covers it. Filed as LC10.

**Why the run handed the push back.** The driver asked why the run did not settle the conflict and push itself. `workflows-core:specs-repo-git` never merges or rebases, and the rationale refuses rebasing session-file commits onto a diverged default branch. Its reason is a conflict left standing in a file several writers append to. Here the only conflicts were the two generated register files. The user asked for the narrow proposal to be filed: settle a conflict in a file the run can rebuild, and otherwise abort the rebase. Filed as LC11.

**Also seen:**
- The maintenance agent's lessons report said the false positive "may attach to the wrong finding" after the renumbering. The run corrected it in its report, rightly, since records name findings by origin. The run's own feedback entry records the `plan`/`rebuild` disagreement, which is LC10.
- The planted record and the seed are synthetic scans written by `register.py` from the 2026-10-17 route-7 product templates. The final cleanup removes the specs copy's `security/` register with the rest.

## Run 7 — `/dev-workflows:implement BOOK-3-01`, run C again (433-2)

**Setup.** `~/e2e-live/one-writer/run-epic.sh D` reset both copies to run C's start, code `6942a24` and the specs tree of `24a1cbc`, committed as `6553763`. Arm D, added for this run, is run C's arm on the installed plugins. Run C's start is described in `docs/superpowers/verification/2026-10-25-implement-piece-review.md` §3: the test Epic's hand-written `## Pieces` draws two pieces, `csv-catalogue` and `import-runs`, which meet at the parser contract. One Opus session, `8a709149`, ran from the code copy. Its plugins had auto-updated just before: dev-workflows 4.39.2, workflows-core 1.59.0. The driver approved the plan, applied the open findings at both offers, took the re-review, and kept the commit local. The run took 3h16m and cost $74.59 by its own cost entry, against run C's $80.93 by the same measure: 8% less. It wrote `08b356e` on `feat/BOOK-3-01-csv-catalogue-import-books-service`, not pushed: 35 files, +4,581 lines. All 202 tests pass (Gradle 145, Karma 57, 136 of them new), and all 85 of the specification's test cases are implemented. Its specs commit is `588febe`. Afterwards the demo check printed `same` on all 18 lines.

| Item | Expected | Seen | Result |
|---|---|---|---|
| The split | two piece reviews, then the overall review, in both rounds | `csv-catalogue` and `import-runs` in parallel, then the overall review; again in the re-review round | pass |
| 433-2, each finding verified on its own | every finding of every review verified before any two are matched | one `triage` entry per review, per round. First round: csv 4 of 4 survived, import-runs 9 of 9, overall 2 of 2. Re-review: csv 3 of 4 (1 dismissed), import-runs 9 of 9 (1 carried), overall 4 of 4 | pass |
| 433-2, the collapse | a finding repeated at a piece review's location with the same claim is collapsed only where both dispositions agree | not reached: the overall review raised no piece review's finding in either round ("The piece reviews' findings stand and are not repeated here") | not reached |
| The cost | close to run C's | $74.59 against $80.93, entry against entry | pass |
| LC6, the offer after the re-review | its list printed | all 12 findings listed with their severities above *Apply the 12 open findings listed above (1 MAJOR, 2 MINOR, 9 NIT)* | printed |

**433-2: the half that runs every time passes; the collapse cannot be provoked.** `/dev-workflows:implement` Phase 3B step 7 verifies every finding of every review "before any two are matched". The run's report gives each review its own triage line, its own counts, and every survivor with its severity. The collapse rule acts only where a later review of the round raises a finding at a location, and with a claim, that an earlier review's finding holds. `code-review`'s overall scope tells that review to raise no finding a piece's review raised. The two piece reviews cover disjoint files, and in this run their two U+0000 findings sat at different locations. So the collapse happens only when the overall reviewer slips, and no setup can make it slip. That branch stays checked by reading alone, and 433-2 is deleted.

**Also seen:** the run wrote three feedback entries. One is a bare `cd` that moved the working directory against Phase 1.4's rule; run 4's `/epics` hit a `cd` the same way. Another is the cost of copying six long review returns verbatim before triage. The third notes that two of the three MAJOR findings were test and input gaps that only the Opus review caught.

## 433-3 — `pieces.py` output stays valid UTF-8 (no full run)

In a scratch repository, a change added `src/a/caf\xe9.txt`, a name holding the byte `0xE9`, which is not valid UTF-8 on its own, beside an ordinary file. The path list was built with `/implement`'s Phase 3B step 5 recipe (`git diff --no-renames --name-only -z`) and handed to the installed `pieces.py assign` (dev-workflows 4.39.2).

- **A design drawing no pieces, the item's case:** exit 0; output valid UTF-8 (150 bytes); `status: none`, `split: false`, the name listed as `src/a/caf\\xe9.txt`. So the run makes one review and prints no `## Pieces unusable` line. **Pass.**
- **A design drawing two pieces, one of which matches that file:** exit 0; output valid UTF-8; `status: malformed` with the defect `the path src/a/caf\xe9.txt is not UTF-8`, and `split: false`. Phase 3B step 5 then makes one review and prints `design.md's ## Pieces unusable — the path src/a/caf\xe9.txt is not UTF-8 — reviewed as one piece`. That is the designed fallback, and its text is valid UTF-8 too.

`pieces.py --selftest` passes 77 checks. 433-3 is deleted.

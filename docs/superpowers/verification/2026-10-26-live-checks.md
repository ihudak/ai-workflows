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

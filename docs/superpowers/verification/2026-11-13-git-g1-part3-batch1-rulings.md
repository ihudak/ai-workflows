# GIT-G1 Part 3, batch 1 — the rulings

**Plan:** `docs/superpowers/plans/2026-11-13-git-g1-part3-batch1-selftest-split.md`. **Record:** `2026-11-13-git-g1-part3-batch1.md`, beside this file. **Ledger:** `2026-11-13-git-g1-part3-batch1-ledger.md`, beside this file, copied as it stood just before the branch was pushed; the *Ledger* column below gives line numbers of that file, and rulings 20 to 22, made after that copy, have none.

A ruling is a decision the controller took while the plan ran, in place of stopping to ask. Each is listed with its reason and what it costs if it was wrong, so the maintainer can overturn it.

## The maintainer's decisions

| When | Decided |
|---|---|
| 2026-11-13, 11:19 UTC | The design (`docs/superpowers/specs/2026-11-13-git-g1-part3-design.md`) approved; pull request #187 merged the same day. |
| 2026-11-13, 13:50 UTC | The batch 1 plan approved, and its execution by subagents: Opus implementers and task reviews, a Fable 5.2 review of the whole branch. The committed mutant runner and mutants file, which go beyond the design, were put to the maintainer with the plan and not objected to. |
| 2026-11-14, 06:51 UTC | With pull request #189 conflicting after `main` took PRs #190 and #191: "can you please resolve conflicts? and next time, merge the pr when ready". |

## The controller's rulings, in the order made

| # | At | Ruling | Why | If wrong | Ledger |
|---|---|---|---|---|---|
| 1 | Pre-flight | Each commit ends with the `Co-Authored-By` line of the model that wrote it: Opus for the implementers. | The plan's Global Constraints allow "the implementer's own model line", and it keeps attribution true. | A trailer. | 41 |
| 2 | Task 3 | The mutant runner starts each run in its own process group and kills the group at the time limit. | The plan gives a limit and says nothing of a run's child processes, and a selftest starts many. | A timed-out mutant leaves orphans in the copy. | 53 |
| 3 | Task 4 | The `selftest` group's mutant must not break group selection; it targets the `--group needs --selftest` test. **Withdrawn by ruling 9.** | Task 2's review had found that a break in selection recurses without bound. | Nothing. | 54 |
| 4 | Task 3, fix round 1 | The eight Minors of Task 3's review go to the implementer with the Important one, not to the final review. | The maintainer's standing rule is that a known defect is fixed before push, and the implementer's context was live. | One larger fix diff to re-review. | 58 |
| 5 | Task 5, fix round 1 | Where the plan's wording ("`--list` prints which checks have one") is false of the tree, the plan gives way. The eight Minors go into the same round. | A sentence in a rules file must be true of the tree (`CLAUDE.md` § Editing discipline). | Nothing. | 70 |
| 6 | Task 6 | Task 6's task review waits for the verification record. | The plan puts the record after the final review's fixes, and the final review reads the release commit anyway. | Nothing: two later reviews read it. | 78 |
| 7 | Final review, I1 | A run with `--group` is refused where `GITHUB_ACTIONS` is `true`; the group's own nested runs clear the variable. | The other fix offered, running `s_ci_runs_all` on every run, would break the rule that the groups' counts sum to the full count. | A partial run in some other CI is not refused; the test file names a CI vendor's variable. | 80 |
| 8 | Final review, I2 | A marker on nested runs (`SPECS_GIT_SELFTEST_NESTED=1`), under which a run that would include group `selftest` fails at once. | The final review measured the hang. | Two checks and a mutant. | 81 |
| 9 | Final review, I2 | A mutant on group selection is added, and ruling 3 is withdrawn. | With ruling 8 in place, a break in selection fails `s_group_alone` in seconds. | Nothing. | 81 |
| 10 | Final review, I3 | `mutants.py --check` and a CI step for it are built now, not left to batch 2. | Batch 2 rewrites the script most mutants name, and the design keeps mutants because the last batch's were lost. | One CI step of milliseconds. | 82 |
| 11 | Final review, M1 | The four `fails` that matched a whole group are tightened by letting `fails` run past the label, not by relabelling the tests. | It keeps the moved test text byte-identical to the base. | Nothing. | 83 |
| 12 | Final review, M3 | The loader refuses a test file that rebinds a name of the script. | It puts a mechanism behind a rules-file sentence that otherwise rests on the author remembering. | A few lines of non-test code in the loader, which the plan allows. | 84 |
| 13 | Final review, M11 and M12 | Both are taken, though the review marks them optional: a fresh copy of the tree for every run, and a classifier mutant for group `status`. | The maintainer's standing rule on known weaknesses. | A slower mutant run. | 85 |
| 14 | Re-review | The six Minors the fix wave introduced (N1–N6) are fixed in closing commits, though the execution skill allows one fix wave. | Two of them are sentences in `.claude/rules/` false as written, and the maintainer's standing rule outranks the skill's cap. The closing commits are read by the closing review. | One small extra dispatch. | 90 |
| 15 | Re-review | The test file's own `cli()` starting nested runs without `-B` stands. | It is the moved test text, unchanged from the base; the bytecode it leaves is git-ignored and outside what the plugin ships; the mutant runner guards its own runs. | A stray ignored directory after a local selftest run. | 91 |
| 16 | After the fix wave | `main` took `workflows-core` 1.85.1 for another change while the fixes ran, so the branch merges `main`, keeps `main`'s changelog section untouched and renumbers its own release to the next patch. | The plan's own rule, derive the version at release time, applied again. | One more merge commit; the step repeats if `main` moves again before the merge. | 94 |
| 17 | After the merge | The changelog's "is updated alone" is reworded to name 1.85.1's coupling. | A reader going from 1.85.0 to 1.85.2 would read "alone" as overriding `main`'s instruction to update `dev-workflows` too. | Nothing. | 96 |
| 18 | Closing review | Every finding of the closing review (four Important, five Minor) is fixed before the push, with the values and sentences the reviewer gave, by the record's writer; the five loose `fails` are tightened as data, not explained away in prose. | The same standing rule as rulings 4 and 14. Tightening the data makes a rules-file sentence and the runner's docstring true without rewording either. | One more round. | 100 |
| 19 | Closing review's re-check | The controller applies the re-check's two replacements and one nit itself, word for word as the reviewer gave them. | Each is a dictated replacement with no judgement in it; a fourth dispatch and re-check for two clauses would be the loop the skill's cap exists to stop. | These edits have no reviewer of their own beyond the one who worded them. | 103 |
| 20 | After the pull request opened | `main` took `workflows-core` 1.86.0 and 1.87.0, so the branch merges `main` again and renumbers its release to 1.87.1, its section dated 2026-11-14, the day it reaches `main`; the section's opening clause says it adds no coupling of its own and names none of the releases below it. | Ruling 16 applied again, as its *If wrong* foresaw. A section dated 2026-11-13 above one dated 2026-11-14 would read as released before it. | One more merge commit. | — |
| 21 | After the pull request opened | The failure of `main`'s `weakness-classes.py --selftest` in this container (the record's *After the pull request opened*) is reported to the maintainer and not fixed on this branch. | The file is another change's, merged the same morning, and this branch does not touch it; a fix here would ship unreviewed by that change's reviews and under a patch release that says no behaviour changes. | The defect stands on `main` until its owner fixes it; a local gate run in this container shows one red step meanwhile. | — |
| 22 | After the pull request opened | The controller does not merge pull request #189; it resolves the conflicts, has the merge and the renumbering read by one Opus review, applies that review's four Minors, and leaves the merge to the maintainer. | The maintainer asked for the conflicts to be resolved and said to merge "next time"; a merge into `main` is what users install, so it is not read into a request that does not name it. From the next pull request on, the controller merges when it is ready. | The pull request waits for the maintainer once more, and conflicts again if `main` moves first. | — |

## What the task reviews deferred, and how each ended

Every finding a task review left open went to the final whole-branch review, which ruled on each; all but one were fixed in the final fix wave.

| From | Deferred | Ended |
|---|---|---|
| Task 1 | Executing the test file overwrote the script's `__doc__`. | Fixed: the header is a comment, and the loader refuses a rebound name (final review M3). |
| Task 1 | The loader said "is not there" for any `OSError`. | Fixed (M2). |
| Task 1 | Running the test file directly died with a bare `NameError`. | Fixed (M9). |
| Task 2 | A break in group selection would recurse without bound. | Fixed (I2). |
| Task 3 | A signal in a window of a few bytecodes skipped the group kill. | Fixed (M7). |
| Task 3 | The signal handlers overrode an inherited ignore. | Fixed (M7). |
| Task 3 | The runner's kill delay equalled `session-branch.py`'s. | Fixed (M7). |
| Task 4 | Four mutants' `fails` matched their whole group. | Fixed (M1). |
| Task 5 | "Run there" in the rules file pointed at the wrong antecedent. | Fixed (M4). |
| Task 5 | The rules file quoted a form not in the tree. | Fixed (M5). |
| Task 5 | A Read of the script also loaded the `gates*.md` rules: the harness matched `scripts/**` unanchored. | Stands: it predates this branch and no sentence of it depends on it. The final review agreed. |

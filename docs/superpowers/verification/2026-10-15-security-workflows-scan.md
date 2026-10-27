# Verification — `security-workflows` sub-project A (`/security-workflows:scan`)

Sub-project A of the roadmap in `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` is the `security-workflows` plugin. It covers the scan command, the findings register `register.py` writes in the specs repository, and fixes through `/dev-workflows:implement` on the Epic's own branch. Plan: `docs/superpowers/plans/2026-10-15-security-workflows-scan.md`. The branch merged on 2026-10-17 as `c3cd9d3e` (security-workflows 0.1.0). This record answers SEC-G3 of `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`, the decision owed in `docs/superpowers/reviews/2026-10-26-fix-batches.md`, and is written last, on 2026-10-27, as `CLAUDE.md` asks.

**Sources.** The plan's Task 12 ran on 2026-10-16 and 2026-10-17, with the user, on the bookstore demo at the pre-merge 0.1.0. Its results were kept only in the branch's SDD ledger, which was lost with its scratch directory, and the demo's register was deleted afterwards (`bookstore-specs` `955d968`). Section 1 is rebuilt from the build session's transcript, where the ledger was written. The ledger itself is beside this file, `2026-10-15-security-workflows-scan-ledger.md`, with its rulings in `2026-10-15-security-workflows-scan-rulings.md`. Section 3 re-checks at 0.4.0, on 2026-10-27, what the releases since 0.1.0 changed.

## 1. Task 12 at 0.1.0, on the bookstore demo (2026-10-16 and 17)

Every route ran from a Claude Code session open in the code repository on Opus, with `SPECS_PATH` on the specs repository. Each session's transcript is under `~/.claude/projects/-workspace-bookstore/` on the test machine, named by its id. The Epic was BOOK-2-01-02, whose open pull request was the code repository's #16 at `eb694d0`.

| Step | Session | Cost | What it showed |
|---|---|---|---|
| Step 3, the browser | — | — | Playwright's Chromium installed and its wrapper written; `$CHROME_BIN --version` prints |
| Step 5, the clean install | — | — | a scripted install into an empty configuration installs `workflows-core` but not `claude-security` ("no marketplace you have added lists it"), and the plugin fails to load; after `claude plugin marketplace add anthropics/claude-plugins-official` all three load. An interactive session registers that marketplace on its first start; a scripted install must add it. Fixed in step 6: the line in `getting-started.md` and the repository README (Rulings 120, 122) |
| Route 1, `/dev-workflows:conformance BOOK-2-01-02` before the merge | `84b4783c` | not recorded | `unit-branch` read `checked-out`; the Epic run traced the branch at `eb694d0`: 85 satisfied, 3 not checkable. F1 |
| Route 2, the Dev's change scan | `bf055d1f` | $6.82 | 0 findings, stamp verified, 7 of 7 researchers. **Spike item 1 verified:** control came back from Claude Security's skill to the command, which ran Phases 4–9. Register created and its bookkeeping pushed. F2 |
| Route 2b, the same with planted flaws | `50628f11` | $16.25 | a local commit, `d5dab21`, never pushed, planted three flaws. The scan found two, both MEDIUM CWE-79: `[SEC#1]`, a stored XSS, decided *Fix*, and `[SEC#2]`, an open redirect, decided *False positive* by the Dev, `confirmed: false`. Claude Security's panel rejected the third, logging a cookie, 3 to 0. **Spike item 7 verified:** *Suggest patches* wrote `patches/F1.patch`, copied into the scan's folder, and the follow-up line names it. F3–F6 |
| Route 3, `/dev-workflows:implement BOOK-2-01-02` from `master` | `d2f5de25` | $15.63 | read back the `[SEC#1]` line with its patch; asked D17's switch question and continued on the Epic's branch; `git apply --check` and `git apply` passed. Phase 1 raised that the patch alone left a criterion unmet, and the user chose the patch plus the column's removal. SIGNIFICANT, Opus review PASS WITH RECOMMENDATIONS after one fixer round. Commit `38d49a6`, kept local (push declined). D17 verified end to end. F7–F9 |
| Route 4, `--verify-fixes` (Security Engineer) | `d65028a2` | $5.18 | pull request #16 was not merged, at the user's direction, so the route tested the too-early run. It scanned the file at `origin/master`'s head in a temporary worktree, removed afterwards. `[SEC#1]` stayed `fixing`, the scan being history for it, and the report said why and what to do. F10 |
| Route 5, `--triage` (Security Engineer) | `20d32ccd` | $3.75 | *Confirm* on `[SEC#2]` re-asserted the Dev's status, evidence and reason from `register.json`, recorded `confirmed: true`, and emptied *Awaiting security review*. F12 |
| Route 6, `--import` of route 2b's report | `461733d4` | $3.62 | `plan` reported `already_recorded` on "this register"; nothing triaged, recorded or patched. F13, F14 |
| Route 7, two clones recording before either pushed | the build session, at `register.py` level | — | a local bare copy of the specs repository and two clones, with synthetic scan products; nothing pushed to GitHub. Alice, a Dev, recorded a change scan with an accepted risk, recorded `confirmed: false`. Bob, a Security Engineer, recorded a codebase scan with an accepted risk, recorded `confirmed: true`. Both allocated `[SEC#3]`. Alice pushed; Bob's push was rejected, and `pull --rebase --autostash` stopped on `register.json` and `register.md`. `register.py rebuild` cleared both: Alice's finding kept `[SEC#3]` and Bob's moved to `[SEC#4]`, provisional, its decision following by `origin`. A later triage recorded the move. F15 |

**Step 6, the fixes.** The routes raised fifteen findings, F1–F15, F11 unused. The user also chose to fix six existing `/implement` defects the routes met. Rulings 101–134 settled them. Two Opus fixers, a residual fixer and two more passes made the changes, each re-reviewed: `1d1261dd`, `b6b49aa6`, `4d762395`, `93a3b231`, `5b0f51b5`, `f4184eba`, `afc00af4`, `b8174bcd` and `88d10997`, all on `main`. Among them:

- F10 made `--verify-fixes` stop before a scan that can close nothing (`SECURITY_NOTHING_TO_VERIFY`, Ruling 110).
- F15 printed the register's settle line after a rejected push (Rulings 114, 123).
- F3 showed the cited evidence line beside a false positive (Ruling 103).
- F12 asked *Decide each row* where no row's suggestion records anything (Ruling 111).
- F7 shortened the switch labels so they survive verbatim (Ruling 107).

The ledger gives each ruling in full.

**Not exercised.** No route merged the fix. Pull request #16 stayed open, because the demo's `master` feeds a live data producer. So neither of these ran live:

- a `--verify-fixes` that closes a merged fix;
- route 1's second half, `/dev-workflows:conformance` reading the merged Epic.

`register.py`'s self-test covers the closing rules (security-register-format §5 rule 2), not the command's path through them. The same holds for the register in session-branch mode (`specs-repo-git` §8), which no route used. All three are on the to-test list.

## 2. What changed after Task 12

The releases since 0.1.0 changed the parts these checks touch:

- 0.2.0 and 0.3.0 changed the loading, part by part.
- 0.4.0 (batch B04) changed `register.py commit`'s checks and the `REGISTER_MOVED` path. On that path, Phase 5 now keeps the plan the person answered, and `register.py rebase` moves the answers into a new plan's numbering (SEC-B1).
- 0.4.0 also changed the false-positive evidence display (SEC-G4) and the follow-up line for an untested patch (SEC-G5).

## 3. Re-checks at 0.4.0 (2026-10-27)

**The clean install, again.** Run from `main` at `e5516154` in a scratch `CLAUDE_CONFIG_DIR`, with the marketplace added from the repository. The result is the same as at 0.1.0. A scripted install brings in `workflows-core` 1.59.0, and `security-workflows` 0.4.0 fails to load until `claude-plugins-official` is added. After that, `claude-security` 0.12.0, `security-workflows` and `workflows-core` are all enabled. `getting-started.md` and the repository README carry the line. The scratch configuration was deleted.

**Route 7, replayed with 0.4.0's `register.py`.** It ran in a scratch area: a fresh bare specs repository, a scratch clone of the e2e code copy, and synthetic products at `eb694d0` and `6942a24`, built from route 7's templates.

- **Race 1, route 7 itself.** It gave route 7's result. Both clones allocated `[SEC#2]`, the second push was rejected, and the rebase stopped on both register files. `rebuild` cleared them with no markers left, and the later-sorting finding moved 2→3, provisional.
- **B04's four refusals, all exit 2, no record written.** An accepted risk with no review-by date (`TRIAGE_INVALID`). A `fixing` status in the decisions file (`TRIAGE_INVALID`, "'fixing' is register.py's own status"). `fixed` on a finding the plan does not propose closed (`TRIAGE_INVALID`). An empty `--by` (`REGISTER_BAD_ARGS`).
- **Race 2, SEC-B1.** Each clone recorded a new finding as `[SEC#4]`, and each then answered "`id:4`" in a triage, by its own plan. The other clone's record then reached the checkout, and the triage commit stopped on `REGISTER_MOVED`. `scan.md` 7.2's path ran as written: plan again, `register.py rebase` with the answered plan, copy the plan over it, commit again. Bob's finding had moved to `[SEC#5]`, and his answer moved with it, `id:4` → `id:5`. Without the rebase, his accepted risk would have landed on Alice's finding, the open redirect at `[SEC#4]`. Both clones then rebuilt byte-identical registers.
- **Self-test.** `register.py --selftest` passes 106 of 106.

**The session half, live.** Run 6 of `docs/superpowers/verification/2026-10-26-live-checks.md` ran `--triage` on the e2e copies. A record from another clone that sorts earlier landed on `origin` while the triage question was open. The false positive reached the right finding after the merge, by `origin`. The rejected push printed the settle line, which worked as printed. But 7.1's re-plan showed no move, because `plan` never renumbers the checkout's findings for a reserved record. The report named the move only through a check of the run's own. That is to-fix LC10. The run did not reach 7.2's `REGISTER_MOVED` path, which needs the checkout itself to gain a record mid-run; the replay above covers it. The user also asked why the run hands a rejected push back rather than settling it. That proposal is to-fix LC11.

## 4. Result

Sub-project A is verified end to end for:

- the change scan, the codebase scan, `--import`, `--triage` and the too-early `--verify-fixes`;
- the Dev's and the Security Engineer's roles;
- D17's continue-on-branch question;
- patches through `/implement`;
- concurrent recording;
- the clean install.

Each ran live at 0.1.0. Where 0.4.0 changed it, the change was re-run, live or at script level as section 3 says. The closing of a merged fix was never run live, and nor was the merged `/conformance` read; the to-test list carries both. LC10 and LC11 are open in `docs/superpowers/to-fix.md`.

# GIT-G1 Part 3 — brief for the design session

Written 2026-11-12 at the close of the STAY-2 and MIDRUN-B4 batch (PR #185, merged as `fdafe85e`), for a fresh session that starts Part 3's design. The brief is **untracked** on `main`. Move it onto the design's branch, or delete it once the design document holds what it says.

## Where things stand

**Merged and released:**

| Part | PR | Released as |
|---|---|---|
| Part 1, the script's core | — | — |
| Part 2a, the start and end of all 35 commands on `specs-git.py` | #182 | `workflows-core` 1.82.0 |
| STAY-2 and MIDRUN-B4 | #185 | `workflows-core` 1.84.0, with dev 4.62.4, product 3.79.3, docs 1.38.3 and security 0.11.3 |

**Not yet run live:** 1.81.0, 1.82.0 and 1.84.0. Live round r4 will be the maintainer's rehearsal, next week, of a new demo recording. It runs on the e2e copies and covers the whole route: `/brd-intake` to `/implement` and `/conformance`. Its off-path part checks the edge items of `docs/superpowers/to-test-on-real-project.md` (the 1.84.0, 1.82.0 and 1.81.0 sections). The rehearsal's findings feed this design **before its plan is written**. The maintainer has not watched the route run since these releases, so take the evidence from the records listed below.

**Order (maintainer):**
1. Part 3, now.
2. Batches 2b+, which slim each command's wrapper.
3. The batch that retires `specs-repo-git`'s step-by-step text.

The two other agents wait until Part 2 is done.

## Part 3's scope

1. **The original Part 3.** It is in `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md` §7 item 3, with §5.2, §5.4, §6 and §10 beside it. It covers:
   - `handoff-to-main`, the consent step, `require-on-main` and `branch-check`, scripted, with the skill's entry points for them;
   - the producers switch over to them;
   - `phase-handoff` becomes the contract;
   - `/brd-package`'s preparation lands before or with this part.

   Per §7, the part ships as several batches, back to back.
2. **MIDRUN-HANDOFF** (`to-fix.md`, *From GIT-G1 Part 2a*). A producer typed mid-run hands off by switching the shared checkout under the open run, and its end commits that run's in-progress files into the producer's pull request.
   - The shared-key case belongs to it.
   - So do the `require-on-main` remedies (`phase-handoff` §3.3 *Row B′'s remedy* and §4.4's per-row commands), which name a switch, merge or pull even mid-run. Only `branch-check` §6.1 has a mid-run form.
   - The fix named there: the scripted handoff hands off and switches back to the open run's branch (the STAY-2 research memo's option F2).
3. **MIDRUN-LATEWRITE** (`to-fix.md`). A run tells its own change apart by its start snapshot, so a file the open run first changes after the typed run started goes with the typed run's change. That can happen through a background agent, or through a later-typed run still open when an earlier one ends. The fix named there: a per-run list of the paths each run wrote.
4. **RO-SIZE** (`to-fix.md`). `require-on-main`'s generated entry file is over the Read tool's limit.
5. **Proposals from the STAY-2 controller.** The maintainer has not decided these yet; settle each in the design conversation.
   - **Split the selftest out of `specs-git.py`.** The file is 18,105 lines and 1,150,374 bytes, and its selftest runs 1,176 checks in about 3 minutes.
   - **Simplify record identity.** Today it uses `started`, `started_before`, `call_returned`, `--started`, parking with `protects`, and a 15-minute `resumable` window. Task 8 took five fix rounds, and the final review needed three passes, each finding a new nesting order. Check whether the per-run written-paths list lets snapshot attribution, and some of that machinery, go.
   - **Make room in `.claude/rules/workflows-core-git.md`.** It is at 19,960 characters against a 20,000 warning. Measure with `LC_ALL=C.UTF-8 wc -m` before writing to it.
   - **Rein in the references' size.** `specs-repo-git.md` is 273,941 bytes and `phase-handoff.md` is 202,499; measure with `wc -c`. A scripted handoff and gates should let `phase-handoff` shrink to a contract, as `specs-repo-git` was meant to.
6. **Known gaps of 1.84.0 worth a look.**
   - A keyed run retyped with **no** key still loses its protection (M1's keyless rule).
   - Eight Done-when checks have no mutant of their own. Each failed first in its RED run.

## Evidence to read

- **Designs:**
  - the GIT-G1 design above;
  - the STAY-2 design `2026-11-10-stay2-midrun-design.md` and its research memo `…-research.md` (S1–S4, option F);
  - the evidence folder `docs/superpowers/specs/2026-11-08-git-g1-evidence/`.
- **Records:** in `docs/superpowers/verification/`:
  - `2026-11-09-git-g1-part2a*.md`;
  - `2026-11-10-stay2-midrun*.md`; its rulings file holds 168 rulings and the maintainer's decisions;
  - the live-check records, `2026-11-04-live-checks.md` (r3) and earlier.
- **Reasons:** `docs/maintainers/rationale.md`, sections `stay-landing` and `specs-git-state-record`.
- **The contracts as they stand:** `plugins/workflows-core/references/specs-repo-git.md` (§3.5, §4 step 1, §7), `phase-handoff.md` (§2.2, §3.3, §4.4, §6.1), and `skills/specs-git/SKILL.md`.
- **The defect list:** `docs/superpowers/to-fix.md`, sections *From GIT-G1 Part 2a* and *Accepted — known, not to fix* (MIDRUN-2S).

## How the maintainer wants it run

- **Design.** Use `superpowers:brainstorming`, then write a design document in `docs/superpowers/specs/`, committed on a feature branch in a worktree (never `git checkout` in the main checkout). A builder check follows.
- **Plan.** Then `superpowers:writing-plans`, with an independent plan review.
- **Execution.** Then `superpowers:subagent-driven-development`. A ledger, a backup of the SDD workspace to a host path (text only, never scratch git repositories, which the container then mounts read-only), Opus task reviews, and a final whole-branch review.
- **Models (maintainer, 2026-11-12):** Fable 5.2 for the design, the plan and their reviews, and for the final whole-branch review and its re-reviews. Opus for implementers and task reviews.
- **Binding rules:** in the maintainer's memory (fix every known bug or ask; criticise the maintainer's decisions unasked; push reviewed branches and open the PR without waiting, merges stay the maintainer's; host-valid commands only in the final message), and in `CLAUDE.md`.
- **Lessons from this batch:**
  - Derive release versions at release time, never in the plan; main moved under this batch.
  - Measure the population a fix serves before designing the fix.
  - Write the verification record last.
  - Commit the rulings and the verbatim ledger before the workspace goes.

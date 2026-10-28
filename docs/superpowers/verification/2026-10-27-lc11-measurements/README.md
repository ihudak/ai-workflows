# LC11 measurements — settling a rejected session-file push

**Date:** 2026-10-27 · **git:** 2.43.0 · **For:** `docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md`

The design's mechanism rests on these measurements. Every case runs in fresh scratch repositories: a bare `origin.git`, clone A (the run) and clone B (the other writer, who pushes first). Git configuration is isolated (`scripts/gitconfig`). `scripts/run-all.sh` rebuilds every scenario from scratch into `work/` beside it, and `logs/` holds the output of the run this record cites. The absolute scratch paths in the logs are replaced by `<measure-root>` / `<scratchpad>`.

`review-of-first-draft.md`, `review-round-2.md`, `review-round-3.md` and `review-round-4.md` are the four Opus reviews of the design, in order (the last returned READY WITH CHANGES; the design folds its changes in). The first draft's blocker — git's `union` driver fuses two distinct entries that share lines — was reproduced there with the family's real `implementation.md`, feedback and `_security.md` formats (its tests `t2`–`t5` were scratch repositories and are not kept; the selftests the build adds replace them).

## What each scenario found

| Script | Question | Finding |
|---|---|---|
| `s1-autostash.sh` | An in-checkout `git rebase --autostash` / `pull --rebase --autostash` over the user's dirty files | Contents come back, but the index does not: `MM` → ` M`, `AM` → `A `. Where the re-apply conflicts, the rebase still exits 0 (`Successfully rebased`) after `Applying autostash resulted in conflicts`, leaving markers in the user's file (`UU`) and `stash@{0}` kept. During a stop, the user's edits show HEAD's content. |
| `s2-refuse-dirty.sh` | Rebase without autostash on a dirty checkout | Refused up front on any dirty tracked path, touched by the rebase or not (`cannot rebase: You have unstaged changes`); untracked files alone do not block. Every refusal left everything byte-identical. |
| `s3-union.sh` | Appended session files under §8's attribute block | Pure appends merge in order with no stop; without the block, each conflicts. In-place edits: a tick on the last line beside an append comes back beside an open copy; both sides editing one line keeps both. Modify/delete conflicts. `-merge` files stop under a rebase. The block must be passed on every call (`-c core.attributesFile`). |
| `s4-register.sh`, `s4g-real-register.sh` | Settling `register.json` / `register.md` by a rebuild mid-replay | At the stop, both sides' `runs/` and `scans/` are in the tree; the real `register.py rebuild` produced a register byte-identical to a rebuild of what was pushed. It can renumber a teammate's already-pushed finding (`[SEC#2]` → `[SEC#3]`). A same-named `runs/` record with different content → `JSONDecodeError`, the abort path. |
| `s5-abort.sh` | `git rebase --abort` | Clean on a clean checkout (HEAD-reflog entries, rewritten mtimes); with autostash, the index is not restored. |
| `s6-concurrency.sh` | Another session during a stop | HEAD detached (a concurrent family run's preflight hits G0); any edit to a tracked file during the stop blocks `--continue` and the abort destroys it; an `index.lock` at the abort leaves the rebase stuck; a commit made during the stop is published unmeasured or orphaned. Window ≈ 0.1–0.5 s per settlement. |
| `s7-push-scope.sh` | `push-scope` as the precondition | It tests the run's commits exactly; a non-session commit stops the replay; a push race rejects again. |
| `s8-checkout-free.sh` | The checkout-free replay (`merge-tree --merge-base`, `commit-tree`) | With every dirty state of s1: HEAD, index status letters and bytes identical; a dirty or untracked collision refuses the move with nothing changed. 47–52 ms per replay. |
| `s9-1-move-order.sh` | How to move the checkout after the replay | Only `update-ref --stdin` (`start`, `update <tip> <old>`, `prepare`), then `read-tree -m -u <old> <tip>`, then `commit` / `abort` never leaves index ≠ HEAD on untouched paths or a branch the worktree does not match; a concurrent commit fails `prepare`; the held `HEAD.lock` blocks commits in the window. `read-tree` before `update-ref`, `switch -C`, `checkout -B` and `reset --keep` each fail one case. |
| `s9-2-push-vs-move.sh` | Push before the move, or after | Pushing a tip the local branch does not hold doubles entries two runs later; moving first, then pushing, does not. |
| `s9-3-push-race.sh` | A teammate pushing during the replay | Fetch, re-replay, move, push: two races settled on the third attempt; after three, the branch stands consistently on the last replay. ≈130–140 ms per attempt on local remotes (stub rebuild). |
| `s9-4-mergetree-x-theirs.sh` | Taking a side in `merge-tree` | `-X theirs` keeps the replayed commit's version but also silences a same-named `runs/` add/add conflict; path-scoped side-taking gives the same tip without that. |
| `s9-5-session-branch.sh` | Session-branch mode | The default branch is never pushed in the mode; the replay never applies there. |

## Helpers

`lib.sh`, `lib9.sh` (setup), `rebuild.py` (a stub register rebuild), `real_register.py` (drives the real `register.py` read-only), `push_scope.py` (§4 step 5's test as written), `replay.py` (the checkout-free replay), `move.py` (the move strategies), `block.attributes` (§8's attribute block, copied from `session-branch.py`).

## Build results (2026-10-28)

The design was built on branch `iv-gu/lc11-design` with `superpowers:subagent-driven-development`, in the plan's six tasks (`docs/superpowers/plans/2026-10-28-lc11-checkout-free-replay.md`). Each task had an Opus implementer and an independent Opus task reviewer, with fix rounds until the reviewer approved. A whole-branch Opus review of the merged result followed, and its findings were fixed and re-reviewed until it returned *Ready to merge* at `1922b045`. Every ruling the controller made is in `../2026-10-28-lc11-checkout-free-replay-rulings.md`, and the ledger itself, unchanged, in `../2026-10-28-lc11-checkout-free-replay-ledger.md`.

| Task | What | First commit → approved at | Selftest checks at approval | Review |
|---|---|---|---|---|
| 1 | `entry_set_merge` | `f35ebae7` → `b5f1947e` | 215 | Needs fixes, one round, approved |
| 2 | Session-branch mode adopts it (`commit`, `sync`, `put-back`; `union` kept for `follow-ups.md`) | `20e372fd` → `ba47f7c8` | 302 | five rounds and a breaker ruling; a fresh implementer from round 4 |
| 3 | `replay_commits` | `4d5bfa5e` → `8159b87f` | 754 | three rounds |
| 4 | The `replay` command: the move, the push and the race | `63ab29f9` → `8daecc12` | 826 | three rounds |
| 5 | `specs-repo-git` §1, §3.4, §4, §6, §7; the rules file; `CLAUDE.md`; `/scan`; `security-register-format` | `f54855fb` → `34ac2448` | 828 | approved with Minors, two rounds |
| 6 | The sweep, the rationale, the docs pages and the release; to-fix D27 and the README's git note, taken on | `892dbf12` → `5224b553` | 828 | Needs fixes, two rounds |
| Final | Whole-branch review over `2430bfa3..4c06b91c` | `938fef49`, `428980c5`, `ca4aa3d8`, `1922b045` | 842 | *Ready with fixes* → *Ready to merge* |

- **Selftest.** `python3 plugins/workflows-core/scripts/session-branch.py --selftest` passes at `1922b045` on git 2.43.0, the only git it was run on. It ran 842 checks there, against 138 on `main` at `2430bfa3`. Both counts come from a scratch copy of each revision whose `check()` counts its own calls. The script prints only `PASS`.
- **Gates.** Every `run:` step of `.github/workflows/validate-catalog.yml`, 27 of them, in order as one `&&` chain, exits 0, and so does `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`.
- **Release.** `workflows-core` 1.67.0, `security-workflows` 0.7.0, `dev-workflows` 4.49.0 and `product-workflows` 3.59.0, renumbered from 1.66.0 and 3.58.0 when `main`'s batch B25 took those numbers.

### Where the build refines the design

The shipped text is the authority; these are the places a ruling moved it from the design's first wording.

- **The entry-set rule (design §3.3).** It refuses only where a base entry is missing from *one* side, so a removal both sides agree on is accepted. Where both sides edit one entry differently, it keeps both, as a visible duplicate. It refuses where the two sides' line endings differ, and it reads a file with no final newline as LF. `union_lines` completes a last line that has no newline, which git's `union` would otherwise double.
- **The replay's guards.**
  - The final tree may hold only the paths the replayed commit wrote, plus the rebuilt register files. This stops git's rename detection from publishing a file at a path the run never wrote.
  - A commit that adds a file under a spec folder `origin` removed is refused.
  - A session file `origin` deleted and the commit changed is refused, not taken in the commit's version.
- **New refusal reasons and rows.** Beyond the design's set, there are two new refusal reasons: `cannot-move`, where git cannot move the checkout and nothing moved, and `checkout-moved`, where another session switched the checkout while it was being moved. There is also an *already there* row, for a replay that finds every commit already on `origin`.
- **Time.** Three attempts of a 60 s fetch and a 60 s push, each with `bounded-run`'s 2 s kill grace, come to 372 s. The Bash timeout of 420 s adds room for the replays and the register rebuilds, which have no bound of their own.
- **Re-checks before the move.** The replay re-reads where the checkout stands immediately before it moves. Where the checkout stands on the branch, it checks HEAD again under `HEAD.lock`. This closes the final review's measured case, a checkout switched during the replay that then received `origin`'s changes as staged edits on another branch.

### Accepted residues

- **Folder renames outside the spec folders** rely on git's rename handling. For example, a teammate deletes a whole `security/<slug>/` while a scan adds a record there, and the replay brings the folder back holding only the run's record.
- **`worktree_blob` in session-branch mode's code** reads a session file that is a symbolic link as a deletion. No run writes a session file as a link.
- **A switch *onto* the branch** in the instant between the move's last check and its ref write, where the checkout did not stand on the branch, moves the branch under that checkout. A switch takes HEAD's lock and never the branch's, so git offers no lock that holds it off. `move_branch`'s docstring and `specs-repo-git` §1 rule 4 state the window.
- **A SIGKILL between `read-tree` and the ref transaction's `commit`** leaves git's locks behind, as the design's §3.4 step 1 states.

### Still to verify live

`docs/superpowers/to-test-on-real-project.md`, section *Live-check fix LC11*, holds the design's two live re-tests, LC11-1 and LC11-2, run on the e2e copies. The replay has so far run only in the selftest's temporary repositories.

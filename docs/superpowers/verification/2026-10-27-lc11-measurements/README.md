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

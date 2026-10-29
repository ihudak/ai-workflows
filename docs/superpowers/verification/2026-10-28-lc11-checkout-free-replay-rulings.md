# Rulings — LC11, the checkout-free replay

The ledger records 28 controller rulings, numbered here R1–R28 in the order the ledger writes them. They are not numbered in the ledger itself: each sits in a line headed by its task, review or fix round, written `Ruling:`, `Rulings: (1) … (5)`, `RULING`, `my ruling` or `Breaker ruling`, or, for R8, R9, R14 and R22, without the word. R3 and R4 are rulings (2) and (3) of the same line, and R15 was superseded by R16 in the next review. "Cost if wrong" is the ledger's own wording where it gives one; `not stated` means it gives none. The ledger is beside this file, unchanged, in `2026-10-28-lc11-checkout-free-replay-ledger.md`. Where this summary and the ledger differ, the ledger's wording is the record. Where a ruling and the shipped text disagree, the shipped text is the authority.

The user's own decisions predate the ledger and are not numbered. On 2026-10-27, after the measurements in `2026-10-27-lc11-measurements/`, the user chose:
- the checkout-free replay over an in-checkout rebase;
- an entry-set merge in place of git's `union`, in the replay and in session-branch mode (§8) both;
- the refusal remedy without `--autostash`;
- plugin branches in scope.

The user approved the design on 2026-10-28 at 07:40Z. The Opus review of the plan was folded in before Task 1.

## Tasks 1–4: the script

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 1 | Task 1 review: the mixed-line-ending guard goes in `entry_set_merge` itself, which refuses where the two sides' forms differ; all three Minors taken. | A mixed-form merge doubled every entry. | not stated | |
| 2 | Restore-then-edit keeps the branch's own entries (`keep_branch_only`). | A visible duplicate over a silent loss. | A duplicate entry, visible and removable. | |
| 3 | Task 2's deviations from the brief accepted. | not stated | not stated | |
| 4 | Task 2's `environment.md` wording accepted. | not stated | not stated | |
| 5 | `worktree_blob` reads the index blob under `core.autocrlf` (via `diff-files`). | A converted working copy read as a change. | not stated | |
| 6 | `sync.conflict` names its source, and the "next run pushes" text is conditional on it. | The two sources need different remedies. | not stated | the two-clone remedy's "the next run here merges and pushes" became "a later run" by R28 |
| 7 | `entry_set_merge` refuses only a removal on *one* side; a removal both sides agree on is accepted. Spec §3.3's sentence is amended to match, and §6 gets a short remedy. | The remedy for a stuck two-clone push did not work while an entry missing from both sides was refused. | not stated | |
| 8 | Task 2 review: all three Importants and five Minors taken in fix round 3; ruling 6 (R6) judged right by the reviewer. | not stated | not stated | |
| 9 | Fix round 4 goes to a fresh implementer, with its own brief. | The skill's escalation from round 4 on. | not stated | |
| 10 | Breaker ruling at round 5: fix `union_lines`, which doubles a last line that has no final newline. | A small, known doubling, from git's own behaviour. | not stated | |
| 11 | Task 3 review: where `origin` deleted a whole-shape session file and the commit modified it, the replay refuses. | Made with the review's Important, git's rename detection publishing at paths the run never wrote, whose fix keeps the final tree to the commit's paths and the rebuilt register files. | not stated | |
| 12 | The replay refuses where the commit adds under a directory that existed at the parent and holds no file at `origin`'s tip (a removed folder). | A new file in a new subfolder of a renamed folder slipped the first guard. | not stated | narrowed by R13 |
| 13 | R12's rule applies only to ancestors under `specs`, `specifications` or `vis`, not in or below `dev-workflows/`. | An emptied `dev-workflows-cost/` would otherwise refuse. | not stated | |
| 14 | Accepted residue: folder renames outside the spec folders rely on git's rename handling. This includes a deleted `security/<slug>/` that comes back holding only the run's record. | The spec folders are the population the guards serve. | not stated | |
| 15 | The Bash timeout becomes 480000 ms. | Task 4 found no margin in 420 s. | not stated | superseded by R16 |
| 16 | `KILL_AFTER = 2`, as `bounded-run` does, and the 420 s figure stays. Task 4 review Minors 4–10 all taken. | 3 × (60 + 2 + 60 + 2) = 372 s leaves room under 420 s. | not stated | |
| 17 | The symbolic-link blind spot in Task 2's code stays: `worktree_blob` reads a linked session file as a deletion. It is to be noted in the verification record. | Population none: no run writes a session file as a link. | not stated | noted in the README's *Accepted residues* |

## Tasks 5–6: the prose and the release

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 18 | `replay()` resets `porcelain` at each attempt. | It held an earlier attempt's `[rejected]` line. | not stated | |
| 19 | Merge `main` into the branch after Task 5 is approved and before Task 6, which edits the CHANGELOGs and manifests. | `main` had moved twice. | not stated | |
| 20 | Task 5 review: all eight Minors taken. | not stated | not stated | |
| 21 | LC11 takes to-fix D27 and the README's git 2.40 note. | D27 was filed for the owner of `specs-repo-git`; the user's rule is to fix known bugs before push. | not stated | |
| 22 | The release is renumbered at integration: `workflows-core` 1.67.0 and `product-workflows` 3.59.0, with `dev-workflows` 4.49.0 and `security-workflows` 0.7.0 unchanged. | `main`'s batch B25 took 1.66.0 and 3.58.0. | not stated | |
| 23 | Task 6 review: the Important and all four Minors taken. | not stated | not stated | |
| 24 | Task 6 fix round 2 gets no separate confirmation; the whole-branch review covers it. | Five identical insertions of the reviewer's own wording, checked by the controller's word diff. | not stated | |

## The whole-branch review

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 25 | Take all five findings in one fix dispatch, to Task 4's implementer. Accept the review's *Declined to judge* list as written. | The Important was measured: a checkout switched during the replay received `origin`'s changes. | not stated | |
| 26 | The re-review's four wording Minors taken. | not stated | not stated | |
| 27 | The five older copies of "the next run retries" a refused or failed push become "a later run", and the subject is swept. | The same imprecision as the timeout sentence's: a run stopped at a guard retries only a branch it commits on. | not stated | |
| 28 | The controller fixes the final confirmation's three one-clause Minors itself. | One clause each, and it stops the churn. | not stated | confirmed *Ready to merge* |

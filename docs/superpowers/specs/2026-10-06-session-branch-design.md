# Session branch for a protected default branch — design

Status: design approved section by section with the user on 2026-10-06; this document is the spec for review.
Scope: all three editions — this repository first, then the internal edition and the Copilot edition, each in its own paths and prefixes.

## Problem

`workflows-core:specs-repo-git` commits a run's session files — feedback, cost, follow-ups, the implementation record, the release-notes draft, the resume pointer and the other §2.1 shapes — and pushes them, on the default branch, wherever the run stands there. On a specs repository whose default branch is protected (branch protection, a ruleset, a policy or a hook), the server refuses that push. The interim fix (`workflows-core` 1.23.1) records the refusal in `branch.<default>.workflowsPushRefused` and stops retrying, but every run still commits on the local default branch, so those commits pile up there, the local branch diverges from `origin` the first time a teammate merges anything, and the catch-up that keeps the checkout current stops working.

Runs that open a deliverable branch already carry their session files onto it and into its pull request (§4.1), so they are not the problem. The problem is every run that stands on the default branch when it commits: `/implement`, `/vuln`, `/upgrade`, `/document`, the docs commands, the logging commands and every keyless run.

## Decisions taken with the user

1. **Where the files go:** to the team's default branch, through a pull request from a per-user session branch that someone merges. The plugin keeps that branch mergeable as the default branch moves.
2. **Approach:** an *overlay* in the main checkout. Emitters and readers are unchanged; all the logic sits in `specs-repo-git` and `phase-handoff`, around the moves that change the checkout.
3. **Trigger:** automatic and opt-in. A push `origin` refuses to the default branch turns the mode on; a team that knows in advance sets one git config key.
4. **The pull request:** opened by the user, from a printed line. The plugin stays prompt-free and never opens one itself.
5. **Implementation:** the git plumbing lives in one bundled, self-tested script; the references state the rules and call it.

## Measurements (git 2.43)

- `git pull --ff-only` and `git switch` refuse to overwrite a working copy of a file the incoming commits add or change — untracked or tracked and modified — even when its content is byte-identical. So a session file left in the working tree blocks the default branch's catch-up the moment the commit that carries it is merged.
- Most session files are appended across sessions: the feedback file per PRD, `follow-ups.md`, `implementation.md`, the release-notes draft. Cost is one file per session; `resume.md` and `pr-draft.md` are overwritten.
- `git merge-tree --write-tree -X ours <session> <default-ref>`, with `merge=union` set for the appended shapes in `$GIT_DIR/info/attributes`, merges a teammate's appended entry and the user's own without conflict, takes the session side of an overwritten file, and moves no checkout.
- A commit can be built on a branch that is not checked out through a temporary index (`GIT_INDEX_FILE`): `read-tree`, `update-index`, `write-tree`, `commit-tree`, `update-ref` with the old value.

## Design

### 1. The mode

- **On** where `git -C "$SPECS_PATH" config --bool --get workflows.sessionBranch` prints `true` (the opt-in), or `git -C "$SPECS_PATH" config --get branch.<default>.workflowsPushRefused` prints a date (the automatic mark the interim fix already records, §4 step 6). Both are local to the clone; a pushable repository never enters the mode. Removing both keys leaves it.
- **The session branch** is `session/<identity>`. `<identity>` is resolved from `workflows-core:branch-naming` §2's first three rungs — `$GIT_USER_INITIALS`, `git config user.initials`, the guess from existing branches — never its prompt, since these steps are prompt-free. Where none resolves, the run commits nothing in this mode: its session files stay in the working tree, where the next run picks them up, and its line names `GIT_USER_INITIALS`.
- **Commits the interim left behind.** The first run in the mode finds session-file commits on the local default branch that are not on `<default-ref>` (§4 step 5's `push-scope` test passes for each). Every run in the mode carries their files onto the session branch with the rest of its commit — once carried they add nothing, the tree being unchanged — and its line names the one command the user runs to drop them from the local default branch — `git -C "<SPECS_PATH>" reset --keep origin/<default>`, standing on it. The plugin never moves the user's default branch.
- **The guards and flags gate first, as today.** G0 (detached HEAD), G1 (dirty paths not the plugin's) and `specs_git: misrooted` keep their effect on the commit and the preflight. G2 (a branch the plugin did not create) no longer decides where the files land: in this mode they go to the session branch whatever the checkout stands on, and G2's notice says so.
- **Deliverable branches** keep carrying deliverables through `phase-handoff`. In this mode they never carry session files; those always go to the session branch, since two pull requests appending to one file would conflict.

### 2. The session branch

- **Committing without moving the checkout.** In this mode `commit-artifacts` (§4) and §3.4's flush never commit on the checked-out branch. They call the script's `commit`, which:
  1. runs `sync` (below);
  2. enumerates the dirty session-file paths exactly as §2.1 does, and, on the first run in the mode, the paths the stranded commits carry;
  3. reads the session tip into a temporary index under `$GIT_DIR`, writes each path's working-tree content into it (or its deletion — §9's pending-cost relocation deletes a file), and builds the commit with `write-tree` and `commit-tree`, parent the tip, message `<KEY|NOISSUE> Add dev-workflows session artifacts (<command>)` as today;
  4. moves the branch with `update-ref` guarded by its old value, so a concurrent run fails rather than overwriting.
  The real index and working tree are not touched; the files stay where they are, as the overlay (§3). A tree identical to the tip's is no commit: `nothing to commit`.
- **Keeping it current (`sync`).** Where the session branch does not exist, create it at `<default-ref>`. Where `<default-ref>` is not an ancestor of its tip, merge it in: `merge-tree --write-tree -X ours <tip> <default-ref>`, then `commit-tree -p <tip> -p <default-ref>`, then `update-ref`. The script maintains one marked block in `$GIT_DIR/info/attributes` giving the appended shapes `merge=union`. Overwritten files take the session side, the latest position winning as it does today. A merge `merge-tree` still cannot complete — a modify/delete, say — is reported and leaves the branch where it was; the run continues and the commit lands on the unmerged tip.
- **Pushing.** `git push --porcelain -u origin session/<identity>`, under §4 step 5's conditions as they stand — `origin` exists, the user's push configuration does not send the branch elsewhere, the remote did not delete it, it was never refused — with `push-scope` widened for this branch alone: it admits two kinds of commit: a session-file commit, as today, and the plugin's own merge of `<default-ref>` — two parents, the second reachable from `<default-ref>`, no path outside what the two parents already carry. The push is always a fast-forward, since only the plugin adds to the branch.
- **The outcome line.** `Specs repo: committed <sha7> (<N> files) on session/<identity> — pushed; <M> commit(s) not on <default> yet: merge its pull request, or open one with gh pr create --head session/<identity> --base <default>`, `<M>` from `git rev-list --count --no-merges <default-ref>..session/<identity>`. The not-pushed variants reuse §6's existing reasons.
- **After the pull request merges** — by merge commit, squash or rebase — the next `sync` absorbs it, and the branch's diff against the default branch is empty until new files arrive. The branch is never deleted, reset or force-pushed.

### 3. The overlay

- **Definition.** In this mode the working tree's session-file paths hold the session branch's version wherever it differs from `HEAD`. Every emitter and every reader keeps using the working tree.
- **`lift`** (before a move). Every dirty session-file path must already be preserved: its working-tree content equals the session tip's, or it is absent where the tip lacks it. If any is not, the caller runs `commit` first; if that fails, the move is skipped and reported, and nothing is discarded. Then each dirty session-file path returns to `HEAD`: an untracked one is removed, a tracked one restored with `git -C "$SPECS_PATH" restore --source=HEAD --staged --worktree -- ':(literal)<path>'`. That is the one discard the plugin ever performs, and only of content just verified on the session branch.
- **`put-back`** (after a move). Run `sync`, then for each session-file path where the session tip differs from the new `HEAD` (`git diff --name-only -z HEAD <tip>`, filtered by §2.1's classifier), write the tip's content into the working tree, or remove the file where the tip lacks it. A failed write is reported; the content is safe on the branch.
- **The moves it wraps** (enumerated by `grep -rn -E 'git -C "\$SPECS_PATH" (switch|checkout|pull)' plugins` and each command's own branch cutting in the specs repository):
  - `specs-repo-git` §3.4's catch-up `pull --ff-only` and §4 step 2's repeat of it;
  - §3.5 B2's switch, pull and `branch -d`; B4's switch and pull; the re-run's switch back;
  - `phase-handoff` §2.2's switch to a new or reused deliverable branch, and §3.3 row C's repair (switch and pull);
  - a direct `/dev-workflows:implement` run from inside the specs repository: `lift` before Pre-Phase 3's clean-tree check, `put-back` after Phase 4.6, so the code commit — which stages the whole repository — takes no session file.
- **What the user sees.** Until the session pull request merges, the specs checkout shows those files as modified or untracked. That is the price of leaving every reader unchanged.

### 4. The script — `plugins/workflows-core/scripts/session-branch.py`

Python 3, standard library only, every git call `git -C <specs>`, JSON on stdout, exit 0 on every outcome the run continues past (a state, not an error), exit 2 on a usage error. Subcommands:

| Subcommand | Inputs | Does | Returns |
|---|---|---|---|
| `mode` | `--specs`, `--default` | reads the two keys; resolves `<identity>` (rungs 1–3) | `{mode, source, identity, branch}` |
| `sync` | `--specs`, `--branch`, `--default-ref` | creates the branch at `<default-ref>` if absent; keeps the attributes block; merges `<default-ref>` in where needed | `{created, merged, tip, conflict}` |
| `commit` | `--specs`, `--branch`, `--default-ref`, `--message`, `--include-ahead` | `sync`, then the temporary-index commit of every dirty session-file path (and, with `--include-ahead`, the stranded commits' paths) | `{committed, files, paths, stranded}` |
| `lift` | `--specs`, `--branch` | the preservation check, then the return to `HEAD` | `{lifted, unpreserved}` |
| `put-back` | `--specs`, `--branch`, `--default-ref` | `sync`, then writes or removes per the diff | `{written, removed, failed}` |
| `--selftest` | — | the scenarios in § Verification, in throwaway repositories | `SELFTEST PASS` / `FAIL` |

The script holds §2.1's classifier as code, and its selftest reads `specs-repo-git.md` §2.1 and fails where the two regex sets differ, so the reference stays the single source of truth for the shapes and the script cannot drift from it. The same holds for the branch prefixes it never counts as an identity, against `branch-naming.md` §2.3. Pushing, and reading the push's outcome, stays in the reference (§4 steps 5–6), which already owns it.

### 5. What changes, file by file (this repository)

- `workflows-core:specs-repo-git`: a new section for the mode (§1–§3 above, citing the script); hooks in §3.4 (flush and catch-up), §3.5 (B2, B4, the re-run switch), §4 (steps 1, 2, 4, 5 and 7), §4.1 and §6; §1 rule 3 names `session/` as plugin-owned for commit and push only — never stood on, switched to, switched away from or deleted, so it is not added to §2.2's switch pattern, and a run that finds HEAD on it takes G2; §1 rule 4 gains the one restore; rule 8 lists the attributes block beside the refusal record, and the mode key as a read of the user's own setting.
- `workflows-core:phase-handoff`: `lift`/`put-back` around §2.2's switch and §3.3 row C's repair; §1 rule 4's widened list gains the same narrow exception.
- `workflows-core:branch-naming`: `session` joins the prefixes never counted as an identity.
- `/dev-workflows:implement`: the direct-run case (§3 above) and its Phase 0 notice.
- Docs: the environment page documents `workflows.sessionBranch`; the session-cost and session-feedback pages and the `/feedback`, `/prompt` and other pages that say where session files go gain the mode; `docs/reference` lists the script where scripts are listed.
- CI: `.github/workflows/validate-catalog.yml` runs `session-branch.py --selftest`.
- `.claude/rules/workflows-core-git.md`, `docs/maintainers/rationale.md`, CHANGELOGs, versions.

The other two editions port it with their own paths, prefixes and classifier: the internal edition's script beside its `session-cost.py`, the Copilot edition's under `dev-workflows/scripts/`, each with its own selftest wired to its own reference.

## Verification

The script's selftest, in throwaway repositories with a bare remote whose `pre-receive` hook refuses `refs/heads/main`:

1. The mode: off by default; on by the config key; on by the refusal record; the identity from each rung and from none.
2. `commit`: creates the branch at `<default-ref>`; leaves the index and working tree byte-identical; a second commit stacks on the first; an unchanged tree commits nothing; a deleted pending-cost file is committed as a deletion.
3. `sync`: a teammate's appended feedback entry and the user's both survive; an overwritten `resume.md` takes the session side; a conflict `merge-tree` cannot resolve is reported and moves nothing.
4. `lift`: refuses where a session file is not on the tip and discards nothing; lifts an untracked, a tracked-modified and a tracked-deleted session file once they are preserved.
5. `put-back`: after a fast-forward that merged the session pull request by merge commit, then by squash, the working tree equals the default branch plus the session overlay, with no entry lost on either side.
6. The whole loop across two clones: user A commits and pushes the session branch; the remote's `main` takes it by a merge; user B appends to the same feedback file through their own session branch; A's next run lifts, catches up, puts back and commits, and every entry from both users is on A's session branch and in A's working tree.
7. A switch to a deliverable branch cut from an older default branch, with the overlay present: lift, switch, put back; nothing lost and the switch not refused.
8. The interim's stranded commits: carried onto the session branch with `--include-ahead`, the local default branch untouched.
9. Parity: the script's classifier and identity exclusions equal the references' (§4).

Then one end-to-end walkthrough of a whole run's git sequence by hand in a scratch repository, recorded in the plan's verification section.

## Not in scope, and refused

- **A second checkout of the session branch** (approach B): every reader of `implementation.md`, `follow-ups.md` and the release-notes draft would learn a second root, and the operator's drafts would sit in a hidden directory.
- **Per-session files** (approach C): changes the format every reader depends on.
- **Opening the session pull request automatically**, or asking once: these steps stay prompt-free and never open one (decision 4).
- **Moving the user's default branch** to drop the interim's stranded commits: a `reset` the plugin never runs; the line names it.
- **A session branch on every repository, pushable or not** ("always PR", for consistency with code and docs repositories, which always go through a branch and a pull request): considered twice and declined (2026-10-06). The machinery is the same size either way, since a protected repository needs it; what always-PR adds is a standing pull request per person on every team, `implementation.md` reaching a teammate's `/document` only after that merges, and the overlay running on every repository rather than the ones that need it. The specs repository's session files differ from code in the two ways that make the overlay necessary at all: every run writes them while the checkout stands on the default branch, and they are append logs the next run on the same machine reads. A team that wants the pull-request flow sets `workflows.sessionBranch`; making it the default later is a small change once the mode has proven itself.
- **A fork whose `pushRemote` or `pushDefault` sends pushes elsewhere**: unchanged in either mode — the plugin pushes nothing against that configuration, and its line says so. `remote.pushDefault` covers the session branch too, so session mode commits there and leaves the push to the user.

## Amended during planning and execution

Planning (the plan's *Amended during planning*):

1. `commit` builds on the tip the working copies came from and merges `<default-ref>` second; writing working copies over a merged tip deleted the entries the merge brought.
2. A new session branch starts at `git merge-base HEAD <default-ref>`, where the checkout's files come from.
3. `sync` defers while a dirty session file is not on the branch.
4. The preflight ends with `put-back` in the mode, so an interrupted `lift` is undone by the next run.
5. A branch that holds nothing of its own is fast-forwarded rather than merged.
6. The overlay's paths include those where the branch differs from HEAD, so a deleted overlay-only file is committed as a deletion.

Execution (each found by a test or a walk-through, fixed test-first; `docs/maintainers/rationale.md` § session-branch has the reasons):

7. `sync` also merges `origin`'s copy of the session branch, refreshed by a second fetch, so a second clone under the same identity pushes a fast-forward.
8. A remote that deleted the session branch (delete-on-merge) does not stop its push.
9. `push-scope` on the session branch counts `<default-ref>` as published and checks `<default-ref>...<session>` for ARTIFACT paths only; the line counts session files not yet landed rather than commits.
10. The stranded commits are dropped with `lift` then `reset --keep origin/<default>`, not `reset --keep` alone, which aborts over the overlay.
11. A working copy of an appended shape that lost the branch's entries is union-merged (`merge-file --union`, base `merge-base HEAD <tip>`), never written over them.
12. `commit` and `put-back` refuse while a worktree has the session branch checked out; session commits are signed where `commit.gpgSign` is set.
13. `require-on-main`'s row C′ does not count session files in the mode; `/implement`'s direct run lifts again before its code commit; with no identity the moves run unwrapped; a preflight a guard ended still puts back.
14. Review round 1: a working copy that is HEAD's version is never committed (the overlay is not in place there), and an absent file HEAD lacks is a deletion only where this worktree held it — a per-worktree record the script keeps — so a commit between a `lift` and its `put-back`, in a second worktree, or after the stranded-commit remedy deletes nothing; `put-back` never brings back a held file a run deleted.
15. Review round 1: `mode` prints `unsupported` where `merge-tree` cannot merge without a checkout, and the run goes on as with the mode off; a commit whose merge cannot run reports `sync.error` instead of exiting 2 after landing; overwritten shapes are `-merge` (kept whole), union puts the branch's entries first, merge commits read `NOISSUE Merge …`.

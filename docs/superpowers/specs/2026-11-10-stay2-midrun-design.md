# STAY-2 and MIDRUN-B4 — a stayed run's session files land on the default branch; a run typed mid-run switches nothing

**Status:** approved by the maintainer, 2026-11-10 (decisions S1–S4 below). Batch right after GIT-G1 Part 2 batch 2a (PR #182), stacked on `feat/git-g1-part2a`.
2026-11-10, later: the mechanism was revised after the plan review (`docs/superpowers/plans/2026-11-10-stay2-midrun.md`, *Plan review*), by the controller's rulings C1 (a per-path own-change apply replaces the replay in §3.1 step 2), C2 (no local branch another worktree has checked out is ever moved), M1 (the here form for a run typed mid-run on a branch it would not leave, journalled) and M2 (held commits chain only on a shared path; a permanent refusal is reported with its remedy, never promised to land). S1–S4 stand as decided.
2026-11-10, later still: revised again after the plan's re-review (the plan's *Plan review*, second block), by the rulings N1–N4: G1's notice under a run typed mid-run names no switch and no commit (N2); a change that drops a line or entry `<default>` lacks is refused, and a refused path is held alone while the rest lands; the here form journals in the held record too, and pushes nothing while the open run stands; `end` with no start tests for an open run; `--started` names the record every save of the end writes.
2026-11-10, latest: after the plan's final check (its *Plan review*, third block), a journal entry is finished only where its move is verified, a mid-run run's `end` re-tests the open run and pushes as usual where it has ended, G2's notice takes the mid-run form too, and an unresolved `--started` writes the run's own derived record path, never another run's.

**Sources:** `docs/superpowers/to-fix.md` — STAY-2 and MIDRUN-B4; the 2a rulings `docs/superpowers/verification/2026-11-09-git-g1-part2a-rulings.md` (D5, rows 40–42); the research memo `2026-11-10-stay2-midrun-research.md` beside this file, with file:line evidence for every claim here. Below, SRG is `plugins/workflows-core/references/specs-repo-git.md`, and `specs-git.py`, `session-branch.py` and `specs_git_state.py` are in `plugins/workflows-core/scripts/`.

## 1. Intent

Two bugs, one mechanism.

- **STAY-2.** When the preflight has to stay on an unmerged plugin branch that no key of the run names — G1 fired, git refused the switch, `status` could not run, or the preflight stopped before the switch — the terminal commit lands the run's session files (cost, feedback, follow-ups, `resume.md`, …) on that branch, and step 5 pushes them into that branch's pull request. Persistent G1 on another key's branch is the usual state after a declined handoff, so every later run adds a commit to an unrelated pull request.
- **MIDRUN-B4.** A command typed while another run of the same session waits on the user runs its own preflight on the shared checkout. A keyless one (for example `/feedback` in the middle of `/specify`) flushes the outer run's in-progress session files under its own message, then B4 switches the checkout to the default branch under the outer run, which then goes on from the wrong branch.

Found while researching them, and fixed here because every known bug is fixed:

- **The record collision.** The same command typed twice in one session: the nested `start` replaces the outer run's state record (`specs-git.py`, the `replaced` field), and the nested `end` removes it, so the outer run's `end` runs as a run with no preflight — losing the `Environment:` comparison, D5's stay, the guard block, the declined paths and the commit key. SRG §7's sentence that one file per session and command keeps a command typed mid-run off the outer run's record, and `specs_git_state.py`'s docstring, are false for this shape.
- **D5 degrades.** D5 (2a) holds a merged-branch stay's files uncommitted for the next run's merged-branch leave. Measured on git 2.43: git refuses to switch over a modified file whose copy in the target commit differs from HEAD's, and over an untracked file the target commit holds, even where the working copy is byte-identical to the target's — so the leave is refused whenever the default branch changed those files since, and the next flush then commits them on the merged branch with the cherry-pick line: the pre-2a outcome.

## 2. Decisions (the maintainer, 2026-11-10)

| # | Decided |
|---|---|
| S1 | A run whose preflight stayed on a plugin branch it would otherwise have left commits **its own** session-file change on `<default>` in the same run, **without moving the checkout**, and pushes it where §4 step 5 allows. It then takes that change out of the working tree on the stayed branch. Files already dirty when the run started are not its own and stay where they are. |
| S2 | D5's merged-branch hold is replaced by the same landing: one rule for a merged stay and an other-key stay. PR #182 merges with D5 as shipped. |
| S3 | A command typed while another run of the same session is open on HEAD's branch switches nothing, never commits the outer run's in-progress files, and lands only its own change on `<default>`. The outer run's protection ends when its command runs again, when HEAD leaves the branch, at `/clear` (a new session id), at its `end`, or after 7 days (the record prune). |
| S4 | A **producer** typed mid-run, whose handoff (`phase-handoff` §2.2, still prose) moves the checkout onto its own branch under the outer run, is filed in `to-fix.md` with GIT-G1 Part 3 as owner — Part 3 scripts the handoff, which can then hand off and switch back. Not fixed in this batch. |

## 3. Design

### 3.1 The landing (S1, S2)

**When.** At `end`, where the run's state record shows the preflight **stayed** on a plugin branch it would have left, and HEAD is still that branch:

- **an other-key stay** — an unmerged plugin branch that no key of the run's key set or commit key names (B4's subject, SRG §3.5), stayed on because of G1, an unknown dirty set, a refused switch, or a stop before the switch;
- **a merged stay** — D5's existing case (`branch-merged` reads it merged), now landed rather than held;
- **a nested stay** (§3.3) — the run stayed because another run of the session is open on HEAD's branch.

Today `_stay`/`_ask_stay` keep a stay only where the branch reads merged; the record must now also keep the other-key and nested stays, with their reason.

**What is the run's own change.** Early in `start`, once the first save is made and the mode is read, record in the state record (`start_dirty`) the blob of every dirty ARTIFACT path (SRG §2.1's shapes; `null` for a deletion), narrowed at each call's return to the paths still dirty. Whatever was dirty at start belongs to someone else — an earlier run's leftovers that belong to the branch (row 41's concern), or an outer run's in-progress files. Where `status` failed at start there is no snapshot; the run then takes its change against HEAD (it could not list its tree; say so in its line).

**How.** Plumbing only, with no checkout:

1. `c1` = HEAD's tree plus the snapshot's versions of those paths, parent HEAD; `c2` = `c1`'s tree plus the run's session-file working copies now, parent `c1` — both through a temporary index (`tree_with`/`commit_tree`, as `session-branch.py`'s `commit` does).
2. **The run's own change, applied per path onto `onto`** — `onto` is local `<default>`, or `<default-ref>`'s commit where local `<default>` is strictly behind it or absent — by a new `session-branch.py` function, never a three-way merge on `c1` (ruling C1: measured, that merge leaks the snapshot's lines into the commit and refuses block-shaped files). For each path `c1`→`c2` changes, from `onto`'s version: a block-shaped file gains the entries of `c2` that `c1` lacks, and is refused where any entry of `c1` is missing from `c2` (edited or removed); `follow-ups.md` gains the lines of `c2` that neither `c1` nor `onto` holds, and is refused where a line of `c1` that `onto` lacks is missing from `c2` — so a line `onto` holds, edited in place (a ticked follow-up), lands as a second copy beside it, `followup-emission`'s two-copies case, and nothing of the branch's own content reaches `<default>` ahead of its pull request (ruling N4); a whole file takes `c2`'s version; a deletion applies only where `onto` holds `c1`'s blob, and is refused where it holds another; a register is rebuilt, as today. A refusal is per path and permanent: the refused path is held alone, the rest of the change lands. The result is built through a temporary index and committed on `onto` with step 4's message. No `merge-tree` is needed. A landing that appends to a file the stayed branch also changed makes that branch's pull request conflict on it; SRG names the remedy `phase-handoff`'s Row B′ gives for such a file, keeping both sides' lines.
3. **The move** — never of a local branch another worktree has checked out (ruling C2: measured, `update-ref` on one stages a revert in that worktree). Where none has `<default>` checked out, move it from its tip to the result with `move_branch(…, here=False)`, which tests that again under the ref's lock. Where one has, build on `<default-ref>` and push the result by refspec (`<sha>:refs/heads/<default>`) where step 5 allows, leaving the local ref alone; with no `origin`, offline, or a push refused, hold.
4. Push `<default>` by name where step 5's three conditions allow (push-scope still holds a session push behind the user's own unpushed commit); a non-fast-forward goes to step 6's replay, which already moves a branch no checkout stands on by `update-ref`.
5. **The lift:** for each path in `c2`'s change whose working copy is still `c2`'s blob, write back `c1`'s version (HEAD's, the snapshot's, or removal). Without it git refuses every later switch to the default branch over the copies, and the next flush commits them onto the branch again. The lift is a second named discard under SRG §1 rule 4 (today "`lift` is the one discard") and runs only after `<default>` holds the commit.

**Hooks.** The landing is plumbing and runs no `pre-commit` hook, as §8.2 and step 6's replay already do.

**A refused landing** (`<default>` checked out in another worktree with no push to make, a lock, a branch that moved, a path step 2's apply refuses): commit nothing on the stayed branch; keep the change as a **held commit** (`c2` on `c1`) under a ref (`refs/workflows/held/<…>`) with a per-worktree record at `git rev-parse --git-path workflows/held.json` (the precedent of `session-branch-placed.json` and the push-refusal records); leave the files dirty. Every later preflight first retries landing held commits, and its flush leaves out a held path whose working copy is still the held blob (one edited since is reported and committed as today). Held commits chain only where they share a path: one never holds back a later landing on other paths (ruling M2). Two wordings: a **transient** cause (checked out elsewhere, offline, a push refused, a lock, a branch that moved) prints a NOT COMMITTED row naming it and that the next run tries again; a **permanent** one (a structural conflict the apply refuses, a register with no rebuild script) prints, on that run and every later one, a row naming it and the exact commands to see the change and drop the hold, and promises no later commit.

**Retrying an unpushed landing.** §3.4's retry covers only the branch HEAD stands on, and the settle loop lists plugin branches and runs only past the guards; while G1 persists nothing would retry a landed commit that failed to push. The preflight's held-commit step, which runs before the guards, also pushes `<default>` whenever HEAD is not on it and step 5 allows.

**A kill mid-landing.** The held record is also the landing's journal: the entry is written before the ref moves and removed after the lift, and `end_commit` is saved before the ref moves, so `end --resume` lifts, and so does the next preflight where no resume comes.

**The prose fallback** (session id unset). Expose the landing as a primitive, `specs-git.py land --branch <b> --default-ref <r> [--snapshot <file>]`, called from SRG §4's prose the way prose already calls `branch-merged` and `push-scope`. With no record there is no snapshot; the base is HEAD — save where the prose run took one with `specs-git.py snapshot` at its start and passes it back.

### 3.2 What a user sees

Every new or changed line is worded in SRG first and pinned in `specs_git_lines.py`.

- **G1's notice** gains an other-key form beside its merged form (SRG §5): its *Not done* line says this run's own artifacts WILL be committed at the end of the run on `<default>`, not on `<branch>`, which no key of this run names, and that the checkout is not moved. The merged form's wording changes from D5's hold to the landing.
- **The `Specs repo:` line** keeps its existing rows with `<branch>` = `<default>`, so every pushed, not-pushed and failed variant stands, plus one append naming the stayed branch, that the files were committed on `<default>` without leaving it, and that they were taken out of the working tree there. D5's `merged-stay` row is replaced by this.
- **The held rows** (a refused landing), transient and permanent, as §3.1 says, and an append naming a path held alone while the rest landed.
- **A change already on `<default>`** — nothing to commit there, and the files taken out of the working tree — gets an outcome line of its own.
- **The nested stay** (§3.3) prints a line of `pre.stay`'s shape with a new reason naming the outer command — a template of its own, `pre.stay.midrun`, since `pre.stay` itself names the misrooted flag.
- **The guards under a nested run** (ruling N2): G1's and G2's notices name no switch and no commit while the outer run stands on the branch — an empty *Fix*, and an *If ignored* line saying nothing is to be run until that run finishes or is ended.

### 3.3 A run typed mid-run (S3)

At the start of `start`, before the flush, read `~/.claude/dev-workflows/specs-git/<session>/*.json`. **An open outer run** is another command's record that was started by the script, whose stage is `done` or one of `start`'s own stages, that has no `end_commit`, and whose `branch` names HEAD's branch, or whose key set names HEAD's branch (`branch_key(HEAD, outer.keys)` — an outer run that handed off onto its own branch). Where one exists, the nested run:

- skips §3.4's commit of dirty files on HEAD (they are the outer run's in-progress files) but still settles other branches;
- turns B2 and B4 into a stay, printing `pre.stay.midrun` with the outer command named;
- ends through §3.1's landing; its snapshot keeps the outer run's files out, so only its own change reaches `<default>`.

**On a branch it would not leave** — HEAD on `<default>`, on a branch a key of the run names (B3), or on a non-plugin branch under G2 — the nested run has no stay, and its own change, taken the same way, commits on HEAD's branch (ruling M1, the **here form**): applied onto HEAD by §3.1 step 2, HEAD's branch moved by `update-ref`, then `restore --staged` of exactly the landed paths, with a journal entry in the state record and in the held record before the ref move (the held record serves the prose path too, ruling of the re-review), the lock and HEAD rechecked between the two steps, and `end --resume`, or the next preflight, finishing it; SRG §1 rule 4's "moves no ref" names it as an exception. While the outer run stands on the branch, nothing moves its checkout: the nested run makes no catch-up and no push retry at its start, no catch-up at its end, and does not push the here-form commit, which the outer run's terminal commit pushes with its own. On `<default>` that is S3's `<default>` literally; on B3 it keeps §4.1's rule that a keyed run's session files ride its own branch. S3's intent stands: nothing is switched, and the outer run's files are never committed. **The here form refuses whole and holds nothing**, unlike §3.1's per-path refusal: a held commit is landed on `<default>` by every later preflight, the wrong place for the files of a B3 or G2 branch, and the outer run's own terminal commit takes them anyway. Its journal is finished only where HEAD's branch stands at the journalled tip; at its old tip the here form runs again; otherwise the entry is dropped and the files left. Where, at the nested run's `end`, the outer run no longer stands (its `end` ran, HEAD left, or it was replaced), the here-form commit is pushed as §4 step 5 allows.

**`end` with no start** (a run that stopped before its preflight, a missing record) has no snapshot to tell its files from an outer run's: it reads the session's records too, and where a run is open on HEAD's branch it commits nothing and pulls nothing, and says the outer run's terminal commit takes the files (ruling N3).

**The same command typed twice (D-park).** The nested `start` moves an open record of its own command aside (`<command>.<started>.json`) instead of replacing it, and the nested `end` restores it. A parked record whose run was abandoned is restored only where HEAD still stands on its branch, else dropped. A restored record keeps serving its own run's `end` — the `Environment:` comparison, the stay, the guard block, the declined paths — but no longer protects its branch, since S3 ends that protection when its command runs again (ruling M3).

**The prose fallback.** With no records there is nothing to read. SRG states an observable trigger for the prose path — another command of this conversation has printed its preflight lines and no `Specs repo:` line yet — never a judgement, and the two of S3's ends a run by hand can observe: that command run again, and HEAD leaving the branch.

**Which record an `end` is.** `start`'s JSON names its record's `started` stamp; `end`, its replay and `declined` take it back as `--started` and read and write that record alone, so two runs of one command end on their own records in either order (ruling N1).

**Not covered, stated:** two sessions on one checkout (scanning every session's records would widen false positives to week-old runs).

### 3.4 Claim sweep

Sweep by subject (`.claude/rules/claim-sweep.md`, refinements 4–8), with before/after counts: "it never switches" (§4.1), "they belong to the run that wrote them" (§3.4), "the one discard" (§1 rule 4), G1's "WILL still be committed", D5's hold and "the next run's preflight leaves the branch and commits them" wherever stated (SRG, `phase-handoff` §6.1, the skill, `plugins/*/docs/` environment pages, `.claude/rules/workflows-core-git.md`, `docs/maintainers/rationale.md`, CHANGELOGs' unreleased text, `to-test-on-real-project.md`), and SRG §7 / `specs_git_state.py` on the record collision.

## 4. Non-goals

- The producer typed mid-run (S4) — filed for Part 3.
- Session-branch mode (§8) — unchanged; it already never commits on HEAD. Reusing it for a stay was rejected: it imposes a session pull request on users who never opted in, and it does not stop B4's switch.
- Inheriting the outer run's keys — rejected (S3).

## 5. Done when

- Every path of STAY-2 (G1, refused switch, `status` failed, early stop — and the budget-stopped start), D5's merged stay, MIDRUN-B4's keyless nested run, a keyed nested run with a different key, and the same command typed twice each has a selftest that failed first and passes, plus a mutant per new test.
- The refused landing, the unpushed landing's retry, a kill between the ref move and the lift, offline, no `origin`, and the prose primitive each have a selftest.
- `to-fix.md`: STAY-2 and MIDRUN-B4 closed with this batch; S4's item filed with Part 3 as owner; `to-test-on-real-project.md` items for the r4 live round.
- Release: `workflows-core` minor version (behaviour), docs patches where a page described D5's hold; coupling bullet; dated CHANGELOGs; the gate chain prints `EXIT=0`; a verification record, written last.

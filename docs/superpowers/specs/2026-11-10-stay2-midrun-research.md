# STAY-2 and MIDRUN-B4: design options

Research memo behind `2026-11-10-stay2-midrun-design.md`, written before the maintainer's decisions S1–S4; that design is the authority where they differ. Line numbers are at `789e82db`.

Base: `feat/git-g1-part2a` at `789e82db` (PR #182, unmerged), read in `/workspace/.worktrees/git-g1-part2a`. SRG means `plugins/workflows-core/references/specs-repo-git.md`, `sg` means `plugins/workflows-core/scripts/specs-git.py`, `sb` means `session-branch.py` and `st` means `specs_git_state.py`, all in that plugin's `scripts/`. Line numbers are at that commit.

## 1. The bugs, restated

### 1.1 STAY-2

**The rule that commits.** §4.1's last general bullet (SRG:1136) says the terminal commit "follows the branch the preflight settled on; it never switches", and it names every way the preflight can stay: G1, `status` failing, git refusing B2's or B4's switch, and an early stop. §4 step 1's only exception is D5's merged-branch stay (SRG:765, 1128). In code, `_end` (sg:1285) checks only `merged_stay` (sg:1379-1381), then commits on HEAD (sg:1420), and `_push_step` (sg:1204) pushes because a plugin branch passes step 5's first condition. So a stay on an **unmerged** plugin branch that no key of the run names (B4's subject, SRG:521) puts the run's session files into that branch's pull request.

**Four paths reach it. None records anything, because `_stay` (sg:1877) and `_ask_stay` (sg:1887) keep a stay only where `branch-merged` reads the branch merged.**
1. **G1 fires**: there are dirty OTHER paths (SRG:406). `_guards` builds G1's block (sg:2279) and the preflight ends before §3.4 and §3.5 run. G1's notice tells the user "This run's own artifacts WILL still be committed at the end of the run" (SRG:1200-1203), and does not say where they will land.
2. **Git refuses B4's switch.** `_b4` raises (sg:2210), so the call stops with `pre.stopped` (sg:2619) and `_stop_stay` (sg:2529) asks only whether the branch is merged. In practice this path is the same as path 4.
3. **`status` could not run.** `_disposition` prints `pre.stay.unlisted` and stays (sg:2442-2449; SRG:538).
4. **An early stop before the switch**: an exception, or a `next` the run never made. This is §1 rule 5. `_close` (sg:2541) still records `branch`, but `_unfinished_stay` (sg:1433) asks only the merged question.

**Why a plain skip is not a fix.** §3.4's flush commits dirty session files "onto the current branch (they belong to the run that wrote them)" (SRG:419-420). If `end` skipped, the next run's flush would commit them on that same branch. Row 40 (extend the pre-flush leave to unkeyed branches) was withdrawn by row 41 because it would carry leftovers that belong to the branch away from it (rulings:79-80).

**What a user sees today.** Persistent G1 on another key's branch is the usual state. G1's own *If ignored* text says it fires "on EVERY later run too", and that the usual cause is a declined handoff (SRG:1207-1212). In that state, every run's cost, feedback, follow-ups and `resume.md` land in that unrelated pull request, one commit per run.

### 1.2 MIDRUN-B4 and the other nested shapes

The state record is one file per session and command: `<session>/<command>.json` (st:93). Nothing else in `start` looks at another run of the same session. The shapes below are what a command typed while another run of this session waits on the user produces.

| Nested run | What happens to the outer run's checkout and record |
|---|---|
| **Keyless** (the filed case) | §3.4's flush commits the outer run's in-progress dirty session files on the outer branch (sg:2337), under the nested run's message, and pushes them. B4 then switches to the default branch (sg:2442, `_b4`). The nested `end` commits whatever is dirty on the default branch, including the outer run's partial files. The outer run resumes on the default branch: its later reads see the default branch's copies, and its handoff must switch back (SRG §3.6 explains why B3 exists). |
| **Keyed, a different key** | The same B4 switch. Worse, if the nested command is a producer, its own handoff (`phase-handoff` §2.2) switches the checkout onto *its* branch, and the outer run continues there. |
| **Keyed, a key the outer branch carries** | B3 stays. The nested `end` commits the outer run's partial session files on the right branch, under the nested run's message. Cosmetic. |
| **Same command typed twice** | **A record collision, found here.** The nested `start` replaces the outer run's record (sg:2589, the `replaced` field). The nested `end` then removes it (sg:1198). The outer run's `end` finds no record (`kind = "missing"`, sg:1307) and runs as a run with no preflight. It loses the `Environment:` comparison, D5's merged-branch stay (so it commits on a merged branch again), the repeated guard block, the declined paths (so its outcome line drops "the deliverable remains uncommitted"), the start's commit key and `session_branch_created`. SRG §7's "One file per session and command keeps … a command typed in the middle of another's run off the outer run's record" (SRG:1376) is false for this shape, and so is `st`'s docstring. Both need correcting (a claim sweep). |
| **Outer G1 already firing** (its deliverable dirty) | The nested run's G1 fires too, so nothing switches. But the nested `end` commits on the outer run's branch, which is path 1 of STAY-2. **The two bugs share this case.** |

## 2. Population

- **Commands that run the preflight: 35.** I counted files matching `specs-repo-git specs-preflight|specs-git"?, args: "start` over `plugins/*/commands/*.md`.
- **Always keyless (8):** `/upgrade`, `/harvest-decisions`, `/promote-decisions`, `/diagnose-session`, `/feedback`, `/docs-init`, `/docs-brand` (when run standalone) and `/docs-audit`.
- **Sometimes keyless (10):** `/prompt`, `/prompt-brainstorm` and `/prompt-grill-me` (keyless unless one run in context resolved a key), `/vuln` (no token carries a key), `/implement` (a direct run), `/document` (Mode B), `/scan` (a repository path), `/prd-proposal` and `/brd-proposal` (an `@<path>` with no key), and `/frames` (a record with no key). Sources: each command's start paragraph, and SRG §3.1's list (SRG:313).
- **Commands that ask the user between their start and end text: 29 of 35.** I counted `choices:`, `AskUserQuestion` and `next-phase-offer` between the first start mention and the last end mention. This is a textual proxy. The exceptions are `/feedback`, `/diagnose-session`, `/frames` and the three `/prompt*` commands.
- **Commands that can be nested:** any of the 35 can be typed while any of those 29 waits. The outer run is usually on a branch it keeps because of B3 (a resumed run) or G1. After a handoff, the end normally runs before the next-phase offer, so the record is already gone.
- **Not measured:** whether Claude Code expands a slash command typed as the free-text answer of an `AskUserQuestion`. A question asked in prose certainly ends the turn.
- **Who reaches STAY-2:** almost every run that follows a producer starts on another key's unmerged branch, because a handoff leaves the checkout there (`prompt.md`, key-set paragraph). That run then stays whenever:
  - G1 fires: a declined "just write the files", or hand edits made on a pull request's branch. This is the main cause, and it persists from run to run.
  - Git refuses the switch, which happens after a flush whose commit was Locked or failed.
  - `status` fails (rare).
  - The preflight stops early (rare).
- **Who does not reach STAY-2:** runs in session-branch mode (§8.2 never commits on HEAD), runs flagged `misrooted` or `blocked`, and runs where HEAD left the branch before `end`, for example through the run's own handoff.

## 3. Options

### A. `end` skips on an other-key stay, and held leftovers are attributed

This extends D5. On an other-key stay, `end` commits nothing and records which dirty files are this run's, so the next flush leaves them out. There are three places the attribution could live:
- **A1, the state record directory.** This is wrong: the record is per session, and `end` removes it. The next run is often in another session, and a run whose session id changes (`/clear`) never finds the record.
- **A2, a per-worktree file under the git directory.** It would sit at `git rev-parse --git-path workflows/held.json`, which is the precedent set by `session-branch-placed.json` (sb:460) and the push-refusal records (sb:378). It is right in scope: the dirty files belong to each worktree, and §3.1's gate already requires a writable `.git`.
- **A3, git itself.** The held files would be committed into a hidden ref (`refs/workflows/held/…`), so their content survives a `git checkout -- .`.

**Every form leaves three problems:**
1. **The files never travel.** A later B4 switch over them is refused, even where the default branch holds byte-identical content. I measured this on git 2.43: both "untracked … would be overwritten" and "local changes … would be overwritten" are refused. So each later run hits STAY-2's path 2, and the hold perpetuates itself.
2. **A later run of the branch's own key appends to the same files.** At that point the split has to be made per entry, or the held entries leak onto the branch.
3. **Nothing reaches `origin`** until the user clears the G1 dirt.

**Changes needed.** SRG §3.4 (the flush excludes held paths), §4 step 1, §4.1, §6 (a NOT COMMITTED row) and §7. In `sg`: `_end`, `_flush`, and a held file. Cost: medium. **The result is incomplete.** Use this only as the fallback inside option B.

### B. Put the run's session files on the default branch without moving the checkout (recommended core)

At `end`, on an other-key stay, the run takes **its own change** to the session files, relative to where it stood, and applies it to `<default>` with plumbing. It pushes the default branch where step 5 allows. It then takes that change back out of the working tree.

**How, using machinery that already exists.**
- **The start snapshot.** At the return of `start`, record the blob of every dirty ARTIFACT path, with `null` for a deletion. Store it as `start_dirty` in the state record. This is the attribution: whatever was dirty at start belongs to someone else. That covers G1's leftovers (G1 ran no flush) and an outer run's in-progress files.
- **The two commits.** At `end`, build `c1` = HEAD's tree plus the snapshot's versions, with HEAD as parent. Then build `c2` = `c1`'s tree plus the working copies now, with `c1` as parent. Both go through a temporary index, as `sb.commit` (sb:840) does with `tree_with` and `commit_tree`.
- **The replay.** Replay `c2` alone onto local `<default>`, first fast-forwarded to `<default-ref>` by `update-ref` where it is strictly behind. `sb.replay_commits` (sb:1114) already runs a three-way merge of each commit on its own parent, with no checkout. It settles block-shaped files by entry, `follow-ups.md` by union, and overwritten files with the commit's version, and it rebuilds a register. It also refuses on a modify/delete conflict or a foreign path.
- **Moving the branch.** Move `<default>` with `sb.move_branch(…, here=False)` (sb:1548). It refuses with `checked-out` where another worktree stands on the default branch.
- **The push.** Push `<default>` by name. Step 5's three conditions are unchanged. A non-fast-forward rejection goes to step 6's replay, which already moves a branch by `update-ref` alone when no checkout stands on it (SRG §3.4, settle loop).
- **The lift.** For each path in `c2`'s change whose working copy is still `c2`'s blob, write back `c1`'s version: HEAD's version, the snapshot's version, or removal.

**The lift is required.** Without it, every later switch to the default branch is refused over the copies, as measured above, and the next flush commits them onto the branch again.

**The same machinery fixes D5.** For a merged stay, take the delta against HEAD, with no snapshot subtraction. D5 already treats every leftover on a merged branch as belonging to the default branch.

**What a user sees.**
- **G1's notice** gains an other-key form, in the way §5 gives a merged form (SRG:1216). The *Not done* line would read: "…This run's own artifacts WILL be committed at the end of the run on `<default>`, not on `<branch>`, which no key of this run names — your checkout is not moved."
- **The `Specs repo:` line** keeps its existing row, with `<branch>` = `<default>`, so every pushed, not-pushed and failed variant stays as it is. It adds one append: `; this run's preflight stayed on <branch>, which no key of this run names, so its files were committed on <default> without leaving <branch>, and taken out of your working tree there`.

**Failure modes.**
| Case | Behaviour |
|---|---|
| Push refused, offline, or no `origin` | The existing not-pushed and failed rows apply to `<default>`. **One gap:** §3.4 retries an unpushed commit only on the branch the run stands on, and the settle loop lists only plugin branches. While G1 persists, nothing retries the landed commit. Fix: the settle loop includes the default branch whenever HEAD is not on it. |
| A push refusal turns the mode on | Later runs see the landed commit as stranded local work on the default branch. §8.2's `--include-ahead` picks it up once a run stands on the default branch. |
| Read-only `.git` | The gate fails before this point, so there is a silent no-op, as today. |
| `index.lock` | The Locked row, as today: nothing lands and nothing is lifted. Check the lock before replaying, so that a run never lands without lifting. |
| A replay conflict, or `checked-out` | Both are rare. Fall back to A2/A3: commit nothing, keep the change as a held commit (`c2` on `c1` under a ref, plus a per-worktree record), and leave the files dirty. Every later preflight first retries landing the held commits. Its flush leaves out a held path whose working copy is still the held blob. A held path edited since then is reported and committed as today. The row reads `NOT COMMITTED — … could not be put on <default> (<reason>); they stay in your working tree, and the next run puts them there`. |
| A kill between moving the ref and the lift | `end_commit` is saved before the move, so `end --resume` lifts. This is the existing pattern (sg:1287-1303). |
| `status` failed at start (no snapshot) | Take the delta against HEAD. This lands earlier leftovers on the default branch too, the case row 41 weighed, but only in a run that could not list its tree. The alternative is to hold. |
| Session id unset (prose fallback) | Expose the landing as a primitive, `specs-git.py land --branch <b> --default-ref <r> [--snapshot <file>]`. Prose §4 already calls `branch-merged` and `push-scope` the same way. With no record there is no snapshot, so the base is HEAD. |
| Hooks | Plumbing runs no `pre-commit` hook, as §8.2 and step 6's replay already do. The normal `end` commit does run them. |

**What it costs.**
- **SRG:**
  - §1 rule 4: the lift becomes a second named discard. SRG:63 says "`lift` is the one discard", so this is an exclusivity sweep.
  - §3.3: G1's notice.
  - §3.4: the settle loop retries the default branch; the held retry.
  - §4 step 1: a new "other-key stay" paragraph, beside D5's.
  - §4.1: bullets 2 and the last.
  - §4 step 5: pushing a branch HEAD is not on.
  - §5: G1's other-key form.
  - §6: the append and the held row.
  - §7: `start_dirty` and the held record.
- **`sg`:** the snapshot at `_close`, the other-key test in `_end` (HEAD == `rec.branch`, a plugin branch, unmerged, and no key of `keys ∪ {commit_key}` names it), `land` (about 250 lines plus selftests in the style of `t_d5_*`), the held retry, and the default branch in `_settle`.
- **The skill:** one sentence in *Where the script cannot start*.
- **Reference parts:** regenerate them.
- **Claim sweep:** "it never switches", "they belong to the run that wrote them", "the one discard", and G1's "WILL still be committed".

### C. Reuse §8's session-branch mode for a run that had to stay

There are three forms, and all of them are a poor fit:
- **C1, the real `session/<identity>` branch, turned on for the run.** It creates a session branch and a session pull request for users who never opted in. It commits nothing where the identity is null (§8.1). The overlay it leaves goes stale once the mode is off again: §8's invariants (the overlay, `session-branch-placed.json`) assume the mode is stable for each clone, so the next flush with the mode off commits the overlay as leftovers, and the session pull request later duplicates them.
- **C2, `sb.commit --branch <default>`.** Wrong. `overlay_paths` and `settle_copy` take their base from `merge-base HEAD <tip>` (sb:840ff), so the other-key branch's own unmerged session entries would be carried onto the default branch. `sync` would then merge `<default-ref>` into the local default branch, and `push-scope` refuses merges outside the mode.
- **C3, turning the mode on permanently at the first other-key stay.** This is a large change of workflow, to a session pull request for every user who ever met G1.

Option C also does nothing for MIDRUN, because B4 still switches in the mode, wrapped. **What should be reused from §8 and step 6 is the plumbing**, which is option B.

### D. MIDRUN: detect an open outer run in the same session, and have the nested run switch nothing

At the start of `start`, before the flush, read `~/.claude/dev-workflows/specs-git/<session>/*.json`. An **open outer run** is another record with all of these:
- `started_by_script`;
- a stage of `done`, or one of `start`'s own stages;
- no `end_commit`;
- HEAD's branch is a plugin branch that its `branch` names, or that its key set names (`branch_key(HEAD, outer.keys)`). The second test covers an outer run that has already handed off onto its own branch.

Where there is one, the nested run:
- (a) skips §3.4's commit of dirty files on HEAD, because they are the outer run's in-progress files, but still settles other branches;
- (b) turns B2 and B4 into a stay, printing `Specs preflight: staying on <branch> — <outer command>'s run in this session is still open on it, so no branch is switched (it would have <…>)`, using the template `pre.stay` already has;
- (c) ends through option B's landing. Its snapshot excludes the outer run's files, so only its own change reaches the default branch.

**False positive.** An outer run abandoned with Esc never runs its `end`, so its record stays open, and later runs in the session stay on its branch instead of switching. The record stops counting when:
- its command runs again (its record is replaced);
- HEAD leaves the branch;
- the user runs `/clear` (a new session id);
- `end` runs;
- or after 7 days (prune).

This is cheap for a keyless nested run: it reads the tree by ref or not at all, and its files land on the default branch anyway.

**Failure modes.**
- **Session id unset:** there are no records, so the prose fallback cannot detect an outer run. It is unfixed there unless the prose names an observable trigger, such as "a run in this conversation has printed no `Specs repo:` line". That borders on judgement.
- **Two sessions on one checkout:** not covered. Scanning every session's records would widen the false positives to 7-day-old runs. I recommend leaving this out, and saying so.

**Cost.**
- **SRG:** §3.4 and §3.5 (a stay paragraph, beside the misrooted and unlisted ones), §7 (*Why it is safe*), and `phase-handoff` §6.1's list of stay causes (`phase-handoff.md:640`).
- **`sg`:** about 80 lines plus tests. The skill needs nothing.

**The record collision**, for the same command typed twice:
- **D-park:** the nested `start` moves an open record of its own command aside, to `<command>.<started>.json`, instead of replacing it. The nested `end` restores it. A record whose run was abandoned is restored only where HEAD still stands on its branch. Otherwise it is dropped.
- **D-key:** `end` looks up the record by `--commit-key`. This fails where the commit key at the end differs from the key set at the start, which §3.2 allows.
- **Accept it and document it:** the outer run's `end` degrades to a run with no preflight, which reopens D5 for that run. Not acceptable under "every known bug is fixed".

I recommend D-park.

### E. The nested run inherits the outer run's key set, so B3 keeps it

This follows the `/prompt` precedent (`prompt.md`, *fix the run key set*). Mechanically it is the simplest MIDRUN fix: the outer run's keys join the nested run's set, and B3 stays. **However, the nested run's files would then ride the outer run's pull request.** That is what STAY-2 calls wrong for an unrelated run. It is arguably right for the four feedback commands, whose subject is the outer run. Only the maintainer can choose this. It works well only alongside option D for every other command.

### F. A nested producer's handoff moves the checkout (a found sibling, not filed)

`phase-handoff` §2.2 is still prose. Part 2a scripted only the start and the end, and the handoff belongs to a later part. There are three options:
- **F1:** while an outer run is open on HEAD, the consent choice offers only "just write the files" and *Cancel*, with a line naming the outer run. The nested deliverable then stays as an OTHER path on the outer run's branch.
- **F2:** the handoff runs, then switches back to the outer run's branch, which is clean because the deliverable is committed. The nested run's session files land with option B's machinery onto its own handoff branch, with `onto` = that branch, so §4.1's rule that "producer session files ride their PR" holds.
- **F3:** file it, and fix it in the part that scripts the handoff.

## 4. Recommendation

**Combination: B + D + D-park, with A2/A3 as B's fallback for a refused landing. Fold D5's skip into B.**

1. **Option B fixes STAY-2's four paths** with one rule: "a run whose preflight did not leave a plugin branch it would have left lands its own session-file change on `<default>`, and lifts it". The snapshot settles row 41's concern without any record across runs: leftovers that belong to the branch were dirty at start, so they are never in the run's change. Every primitive already exists and is tested: the temporary index, `replay_commits`, `move_branch` and step 6. The files reach `origin` in the same run, where option A would hold them for an unknown number of runs.
2. **Option D makes MIDRUN-B4 a case of the same rule.** The nested run stays, and option B lands its own change. Its snapshot keeps the outer run's in-progress files out, which also fixes the mislabelled mid-run commits that both shapes make today. That case is shared with STAY-2's G1 path anyway, so the two bugs need the one mechanism. **This is the option that fixes both.**
3. **D-park fixes the collision**, and the §7 and `st` text that claims the collision cannot happen.
4. **Option C is rejected.** It changes a whole workflow, and it does not reach MIDRUN.

**Option E is rejected for the general case.** Offer it only as a question about the feedback commands.

**For option F I recommend F3.** File it as found, and fix it in the part that scripts the handoff: F2 is right, but it is a `phase-handoff` change of its own. If the batch has to close every known bug, use F1 in prose now.

**Size: one batch,** about the size of 2a's Task 10b (D5) times three, most of it selftests.

## 5. Questions only the maintainer can answer

1. **Where does a stayed run's session-file change go?**
   - (A) It is committed on `<default>` by plumbing in the same run and pushed. **Recommended.**
   - (B) It is held uncommitted until a later run can leave the branch, as D5 did.
   - (C) It goes to a session branch.
2. **After landing, do the run's files leave your working tree on the stayed branch?**
   - (A) Yes. This is the lift, and it is a second discard under §1 rule 4. Without it, git refuses every later switch to the default branch: measured on git 2.43, even over byte-identical copies. **Recommended.**
   - (B) No. The files stay visible, which needs a per-worktree overlay record and a lift around every move of the checkout, as §8.3 does.
3. **Should D5's merged-branch skip become the same landing?**
   - (A) Yes: one rule, and the files reach `origin` at once. **Recommended.**
   - (B) No: keep D5 as shipped, and land only other-key stays.
4. **What should a command typed while another run of this session is open on HEAD's branch do?**
   - (A) Switch nothing, and land its own files on `<default>`. **Recommended.**
   - (B) Switch as today.
   - (C) Inherit the outer run's keys, so its files ride the outer run's pull request.
   - (D) Option A for everything, but option C for the four feedback commands.
5. **How long does an open outer run protect its branch, when it may have been abandoned without its `end`?**
   - (A) Until its command runs again, HEAD leaves the branch, `/clear`, or 7 days. **Recommended.**
   - (B) The same, plus a limit of N hours since the outer run's start.
6. **What happens to a producer typed mid-run (option F)?**
   - (A) Its handoff refuses to move the checkout, and offers "just write the files" or *Cancel*.
   - (B) It hands off, then switches back to the outer run's branch.
   - (C) File it, and fix it when the handoff is scripted. **Recommended.**
7. **What happens when a landing is refused (rare: another worktree has the default branch checked out, or a modify/delete conflict)?**
   - (A) Hold the change as a commit under a ref, retry it on every run, and keep it out of flushes. **Recommended.**
   - (B) Commit it on the stayed branch, unpushed, with a line naming how to move it.

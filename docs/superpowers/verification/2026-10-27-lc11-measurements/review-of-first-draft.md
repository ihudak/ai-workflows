# LC11 design review: the run settles its own rejected session-file push

Design: `/workspace/.worktrees/lc11/docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md`
Grounded in: the worktree's `specs-repo-git.md` (§1, §2.1, §3.4, §4 steps 2/5/6, §6, §8), `session-branch.py`, `register.py`, `scan.md` Phase 7, `security-register-format` §1–§2, `implementation-format` §1, `feedback-emission` §1, rationale `#specs-push-scope`, to-fix LC11, and the measurements in `scratchpad/lc11-measure/` (scripts and logs read; git 2.43.0).
My scratch tests: `scratchpad/lc11-review/t2` to `t5`.

**Verdict: NOT READY.** One BLOCKER: the append-merge rule the design inherits from session-branch mode silently corrupts the family's real multi-line entry formats. The measurements did not catch it because their test entries put the writer's tag on every line. Fixing it changes a mechanism the user decided ("merges the append-type session files by the rules session-branch mode already applies"), so the fix needs the user's decision and a fresh measurement. Everything else can be fixed inside the design.

---

## A. Findings

### BLOCKER

**B1. `merge=union` merges two distinct appended entries into one. It is silent (exit 0) and goes straight onto origin's default branch.**
git's union driver runs the three-way merge at XDL_MERGE_ZEALOUS. Lines that both sides share at the start and end of a conflicting hunk are moved out of the hunk and kept once. A run of three or more shared lines inside the hunk splits it, and union then concatenates each piece. The family's append-only records are multi-line entries whose header and trailing fields are often the same for two runs. Reproduced with the design's own call (`git -c core.attributesFile=<block> merge-tree --write-tree --name-only --no-messages --merge-base=<parent> <onto> <c>`):
- **`implementation.md`** (t2, `implementation-format` §1's block shape). Two `/implement` runs on one unit on the same day, in two repositories, each with `pushed: true`. Result: one `## 2026-10-27 — /implement` block. This run's header is gone, and the teammate's entry has lost its `pushed: true` line. The reference makes `pushed:` load-bearing ("`pushed:` is recorded, not assumed"). Population: any two same-day runs on one unit folder, such as `/implement`'s companion run in another repository, or two developers on one Epic.
- **`<KEY>-feedback.md`** (t3, `feedback-emission` §1's shape: one file per PRD, appended). Two entries with the same date, command and category become one entry. Its YAML block has `id:` twice and `author:` twice, the second entry's heading is gone, and the two prose blocks run together. That breaks the "deterministic YAML for filtering/clustering". With different headers (t3b), only the blank separator line collapses, which is harmless. Documentation feedback is filed per `<date>.md`, so same-day writers always share a file.
- **`_security.md`** (scan.md §7.3). The block header `## <date> — /security-workflows:scan` and the last line `register: security/<slug>/register.md` are the same for two scans of one unit and repository on one day, for example a Dev's pre-merge scan and an Engineer's verify scan. The block has the same shape as `implementation.md`'s, so the same collapse follows.

This breaks anti-goal 2 ("An entry a teammate or this run appended is lost or doubled on origin") on the design's main path, in §3.3's first bullet ("settled by the merge itself, never reported as a conflict"). s3 never showed it because `session()` and `appendc()` put the tag on every line (`## … a1 run`, `- api: a1 on feat/a1`, `- a1 entry`). §8.2 step 3 and `session-branch.py`'s `union_copy` have the same defect today. There the result at least passes through a pull request; here it does not.
*Fix:*
- Settle a block-shaped append file by **strict append-concatenation**. Where both sides changed the path and the merge base's blob is a byte prefix of both versions, the result is `onto` plus `c`'s bytes after the base. Where the two appended suffixes are identical, keep them once. Anything else (an in-place edit) refuses.
- Implement it by giving these paths no `union` in the replay's block, so they conflict, and settling each conflicted one in the script by the prefix test.
- Keep `union` only for line-set files whose lines are self-contained tasks (`follow-ups.md`), where a duplicate line really is the same task.
- Add selftests built from the real entry formats: `implementation-format` §1's block, `feedback-emission` §1's entry and scan.md §7.3's block, each pair sharing its header and last line.
- Fix §8.2 step 3 and `union_copy` the same way, or file them as a known defect. Either way, the user needs to rule on it, because it changes the rule the decision named.

### MAJOR

**M1. A refusal sends the user to the remedy the design itself measured as harmful, in exactly the state that caused the refusal.**
- §3.5 keeps `pull --rebase --autostash` "as today" on every refusal.
- The main new refusal is §3.4's move refused because a dirty or untracked path collides with origin's changes. In that state the working tree is dirty by definition.
- The design's own s1 shows what `--autostash` then does: it collapses `MM` to ` M` and `AM` to `A `. Where the stash conflicts on re-apply, it leaves conflict markers in the user's file, exits 0 with "Successfully rebased", and leaves `stash@{0}` behind. Those are anti-goal 1's exact effects, now reached through the printed line.
- s2 shows the safe form: `pull --rebase` without `--autostash` refuses up front on a dirty tracked path.

*Fix:* where the move was refused on `<path>`, name the path, and either say the next run that commits settles the push once `<path>` no longer collides, or print `pull --rebase` without `--autostash`. Keep today's line only for conflict refusals on a clean tree. This changes the user's "prints today's lines", so ask the user.

**M2. The state after a partial success is undefined, or reported wrongly.**
- §3.4 step 3 moves the local branch on attempt 1 and pushes. A later attempt can then refuse (a dirty path collides with teammate 2's change), hit a `[remote rejected]`, fail on the network, or exit 2.
- §3.5 says "nothing has moved", which is false after attempt 1's move: local `<default>` is already on tip1, possibly with a rebuilt and renumbered register.
- Today's push-rejected row names `<sha7>`. The pre-replay commit is no longer on the branch.
- §3.8 maps exit 2 to "reported as §8 reports it". That is §6's `NOT COMMITTED — session-branch.py could not run` row, which is false here because the commit exists.
- The JSON `{pushed, attempts, replayed, dropped, tip, renumbered, refused}` carries neither "did the branch move" nor the push's porcelain status. Step 6 needs that status to tell `[remote rejected]` apart: the reference must write the push-refusal record (§1 rule 8), which also turns session-branch mode on for later runs, and must not retry a refusal. "Any other outcome is step 6's as today" has nothing to classify.

*Fix:*
- Add `moved` and `push: {status, reason}` (the `--porcelain` line) to the JSON.
- The script never exits 2 after the move; any later failure is reported in the JSON.
- Define the rows for "moved but not pushed": the replayed sha, and that the next run retries the push.
- Say who writes the push-refusal record on a `[remote rejected]` during the retries.

### MINOR

**m1. The repository's `.gitattributes` overrides the block passed through `-c core.attributesFile`.**
- `core.attributesFile` is the lowest-precedence attributes source. Measured in t4: a repository `.gitattributes` holding `* merge=text` makes `check-attr` report `merge: text` for `implementation.md`, `resume.md` and `register.json` under the `-c`.
- `info/attributes`, which §8 writes, wins over `.gitattributes`. So "measured equivalent, s3i" holds only in a repository without its own `.gitattributes`.
- The dangerous case is `register.json` losing `-merge`. Two non-overlapping text edits can then merge cleanly into an inconsistent register, which is pushed without a rebuild.

*Fix:* rebuild a register whenever both sides changed anything under `security/<slug>/`, not only when a conflict is reported. The prototype's `-X` branch already does this. Also run `check-attr merge` on the replayed paths under the `-c`, and refuse where the block is not in force.

**m2. After `read-tree`, a failed or dropped `commit` leaves the checkout on tip while the branch stays on old.**
- §3.4 says "a driver that dies while prepared closes stdin, and git aborts and removes both locks". s9-1 measured that only with no `read-tree` in between.
- Once `read-tree -m -u` has succeeded, an abort leaves the index and working tree on `<tip>` and the branch on `<old>`: index differs from HEAD on every path origin changed. That is anti-goal 1/4's state.
- How it gets there: the transaction's `commit` fails (disk full, a `reference-transaction` hook), or the driver is killed in that window. The Bash tool's timeout is a plausible killer, because the script runs a fetch and a push up to three times.
- A SIGKILL of `update-ref` itself leaves `HEAD.lock` and `<default>.lock`, which the plugin never deletes.

*Fix:* where `commit` does not answer `commit: ok`, run `read-tree -m -u <tip> <old>`. Give the script a bounded network timeout. Name the remaining SIGKILL window as accepted.

**m3. The claim-expiry sweep's starting points miss sentences that become false.** All of these are in refinement 4's scope:
- `docs/maintainers/rationale.md:425`: "A branch that has already diverged is not rebased; the rejected-push line names `pull --rebase --autostash`…" This is a different paragraph from the `#specs-push-scope` bullet.
- `specs-repo-git` §3.4 (line 379): "Nothing else here brings the default branch up to date while a run stands on it … a diverged one is §4 step 6's case".
- `specs-repo-git` §4 step 2 (lines 689–691): "that run's push is rejected, and step 6 says what to run".
- `security-register-format` §1 (line 31), "the `git pull --rebase` that … §6's *push rejected* line advises stops on a content conflict in both", and its §2 (line 70), "After each pull into the checkout…".
- `plugins/security-workflows/docs/reference/security-register.md:25` and `plugins/security-workflows/docs/commands/scan.md:171`.
- `.claude/rules/workflows-core-git.md:22` (the `commit-artifacts` summary) and `:35`.
- `CLAUDE.md`'s specs-repo hard constraint ("switching only plugin branches and pushing only per §4 step 5"), to be re-read.
- §1 rule 4 needs a **new named exception**, not an inherited one. The design says the rule "already excepts" §8's checkout-free merges, but rule 4 excepts them as merges that "move no checkout". `read-tree -m -u` moves the checkout.

**m4. Push the measured tip, not the branch name.**
A commit that lands on `<default>` after the transaction commits and before `push` reads the ref is published without being measured, which breaks anti-goal 3. The window is narrow, and step 5 already has the same race. `push --porcelain origin <tip>:refs/heads/<default>` closes it and still pushes only what the local branch holds.

**m5. The plugin-branch non-goal has a real population.**
- GitHub's *Update branch* button and a reviewer's push to an open pull request branch both reject the next session-file push to that `spec/`, `design/` or similar branch.
- The same replay applies unchanged: HEAD stands on the branch, and `push-scope` is the same test.
- This is Claude's call, so take it back to the owner with this population.

### NIT

- `merge-tree --name-only` without `-z` quotes non-ASCII paths, such as §2.1's own `zahlungsauslösung` example. The path classifier then misses `resume.md` and the register files, and the run refuses where it need not. Use `-z`.
- `read-tree -m -u` refuses on stat-only staleness. t5: same bytes rewritten gives `Entry 'f' not uptodate. Cannot merge.` Run `update-index -q --refresh` before `prepare`. That changes no content, and most runs have just run `git status` anyway.
- Fetch with an explicit refspec, `+refs/heads/<default>:refs/remotes/origin/<default>`, as §8.1 does. A narrowed `remote.origin.fetch` otherwise leaves `onto` stale and wastes all three attempts.
- Rebuild's `renumbered` lists every move no record holds, not only the moves this replay caused. Diff it against a rebuild of `onto` before the replay. Also, "the next recording scan" should read "the next run that records anything", per §2's wording, which includes triage and verify runs.
- Leave these undefined no longer:
  - A root commit in the list has no `--merge-base=<c's parent>`: refuse.
  - This run's own commit dropped as already on origin: say what `<sha7>` and `<N>` the line then carries.
  - "Take c's version whole" where `c` deleted `resume.md` or `pr-draft.md`.
  - The prototype hard-codes mode `100644` for files it takes whole.
- Hooks. Say why skipping `pre-commit` is acceptable for a commit landing directly on the checked-out default branch, where §8.2's commits go to a reviewed session branch. The reason is that the replayed tree holds only content `c` (which passed the hook) and origin already carried, plus `register.py`'s canonical rebuild. That reason holds only once B1's concatenation replaces union.
- §1 says "HEAD … came back identical", which is true for refusals only. "129–142 ms" covers fetch, push-scope, replay and move with the stub `rebuild.py`, not the real 4,792-line `register.py`.

---

## B. Questions a builder still needs answered (most important first)

1. **How are appended shapes settled after B1?** Which shapes are line-sets that keep `union` (`follow-ups.md` only?) and which are blocks settled by strict concatenation? On an in-place edit (a ticked follow-up line, a hand edit), does the run refuse or union? Does the fix also land in §8.2 step 3? *Why it matters:* this sets the merge code, the selftests, how many runs refuse, and whether LC11 also changes session-branch mode and its release coupling.
2. **Who classifies the retried push's outcome, and what does a partial success print?** Does the script return the porcelain line for the reference's step 6 prose to classify, including writing the push-refusal record, or does the script write the record itself? What `<sha7>` and which row does a moved-but-not-pushed run print? *Why it matters:* it decides the JSON contract, where §1 rule 8's writes live, and the new §6 rows (M2).
3. **What remedy does a refusal print when a dirty path blocked the move?** Keep `--autostash` as decided, or switch to the alternative in M1? *Why it matters:* it changes §6 rows, the flush line and scan.md's settle-line condition, and it reverses part of the user's decision.
4. **What triggers a register rebuild: a reported conflict, or both sides touching `security/<slug>/`?** *Why it matters:* correctness under a repository's own `.gitattributes` (m1), and which selftests exist.
5. **Does session-branch mode `unsupported` count as "off" for §3.1 condition 2?** *Why it matters:* it decides whether the replay is attempted, and which clause its line carries, on a clone that opted in on an old git.
6. **Do plugin branches stay out of scope, given the *Update branch* population (m5)?** *Why it matters:* it changes condition 1, the sweep and the selftest set.

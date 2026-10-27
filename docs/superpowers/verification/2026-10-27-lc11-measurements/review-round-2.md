# LC11 design review, second draft

Design: `/workspace/.worktrees/lc11/docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md` (second draft).
Scratch evidence: `scratchpad/lc11-review/sb/` (a patched copy of `session-branch.py` and the run of its selftest), `t6` (`push -u` with a sha source; `update-ref` under another worktree), `t7/rule.py` and `t7/entry.py` (the append rules on real-format bytes), `t8` (`pull --rebase` under `rebase.autoStash`). No repository was changed.

**Verdict: NOT READY.** The user's rulings landed. But the strict-append rule as §3.3 writes it doubles entries whenever one side's addition already holds the other's. That is the *normal* path of session-branch mode, where §3.8 now applies the rule. I ran it in the real script: the existing selftest still passes with the rule installed, and two ordinary commits to one file double the first entry. Every fix below is mechanical, except two small decisions (the add/add rule, and §8's fallbacks). A third draft limited to §3.3, §3.4, §3.5, §3.7 and §3.8, with the listed selftests, should be enough.

---

## 1. First-review findings and questions: status

| Item | Status |
|---|---|
| B1 union fuses entries | **Resolved in intent** (strict append, user's ruling). The rule as written is wrong: see N1 and N2. |
| M1 `--autostash` remedy | **Partly resolved.** `--autostash` is dropped, but `pull --rebase` still autostashes under `rebase.autoStash=true`: see N4. |
| M2 partial success | **Resolved:** `moved`, `porcelain`, the *moved, not pushed* row, step 6 classifies the push. NIT: exit 2 with JSON on stdout changes the script's exit-2 contract; say the reference reads stdout on exit 2. |
| m1 `.gitattributes` precedence | **Resolved:** the script classifies shapes itself, and a register is rebuilt wherever both sides touched `security/<slug>/`. |
| m2 failure after `read-tree` | **Resolved** for a failed `commit` (the reverse `read-tree`). The death-after-`read-tree` window is still unnamed: see m-c. |
| m3 sweep gaps | **Resolved:** §3.9 lists them, plus `#session-branch` and §8's account of `union`. |
| m4 push the measured tip | **Resolved.** One false promise remains, `-u` with a sha source: see m-b. |
| m5 plugin branches | **Resolved** (in scope). It opens N3. |
| NITs | `-z`, refresh, fetch refspec, moves vs `onto`, root commit, `c` deleting `resume.md`, hook rationale and real timing are all **done**. Still open: "next recording scan" wording; the dropped-own-commit `<sha7>` (see NITs); §1's "HEAD … came back identical", which is true of refusals only. |
| Builder Q1–Q6 | **All answered** by the user's rulings or the coordinator's calls. |

---

## 2. Findings on the second draft

### BLOCKER

**N1. Strict append as written doubles entries where one side's addition already holds the other's, which is the normal flow in §8.**
§3.3's rule is: result = `o` where `Y` is empty or `X` ends with `Y`, else `o + Y`. It has no case for `Y` *starting with* `X`.

In session-branch mode, `union_copy` runs on every commit of an overlaid appended file (`commit()`: the working copy differs from the branch tip). Its base is the version at `merge-base HEAD <session branch>`. That base lacks the branch's own earlier entries `E1`, while the working copy holds `E1` plus the new `E2`.
- Reproduced in the real script (`sb/flow`). I swapped `union_copy` for §3.3's literal rule, branch side as `o`. The **existing `--selftest` still passes**, yet two ordinary `commit` calls to one `implementation.md` leave `session/ab` holding the first block twice. With the work side as `o`, the same doubling happens, in the other order.
- After a squash-merged session pull request, §8.2 step 3's sync of `<default-ref>` meets the same thing. The default branch then holds `E1+E2` as a squash, with no ancestry link to the session branch's commits (`t7/rule.py` case 2): the literal rule doubles `E1` and `E2`.
- Adding "`Y` starts with `X` → `t`" fixes those two cases, but not the next one. After a squash, a teammate appends `B1` on the default branch and the user's next run commits `E3` on the session branch before the sync (case 3). Then `X = E1 E2 E3` and `Y = E1 E2 B1`, and any whole-addition rule doubles `E1 E2`. `union` handled that case today, by trimming the shared lines.
- The replay itself rarely meets these cases (case 4, an ordinary race, is fine). §3.8 puts §8 on the same function, though.

*Fix:* make strict append entry-wise.
- Every block-shaped format opens each entry with an H2 line: `implementation-format` §1, `feedback-emission` §1, scan.md §7.3 and `cost-emission` §6.
- Split each side's addition at lines beginning `## `. The result is `o` plus every entry of `Y` that `X` does not hold byte for byte (ignoring trailing newlines), in `Y`'s order.
- Refuse where `base` is not a byte prefix of both sides, or where an addition holds text other than blank lines before its first `## `.
- `t7/entry.py` shows this settles cases 1–5 with no entry doubled or fused, and refuses an edit before the end. Entries carry timestamps, ids and commit shas, so byte-identical entries are the same entry; the draft's own "`X` ends with `Y`" already relies on that premise.
- **Selftests to add:**
  - two session-mode commits to one file;
  - a sync after a squash-merged session pull request, with and without a teammate's append since;
  - the replay race;
  - each of these in all three real formats.

### MAJOR

**N2. Add/add, a file created on both sides, is undefined.**
- §3.3's rule needs `base`, and the file does not exist at `c`'s parent. A builder who reads an absent base as empty gets `o + t`. That doubles the creation header: `# Implementation — <key> <slug>`, `# Security — …`, or the feedback file's YAML frontmatter, which would land mid-file (`t7` case 5).
- The population is real:
  - `documentation/<slug>/dev-workflows/feedback/<date>.md` is per date, so any two same-day writers both create it;
  - a new Epic's first `/implement` on two machines;
  - a PRD's first feedback entry from two clones.
- *Fix:* where both sides created the file, and the bytes before each side's first `## ` are identical, use those bytes as `base`; otherwise refuse. Add a selftest per format.

**N3. A plugin branch moved by `update-ref` alone can be checked out in another worktree.**
- §3.4 step 2 moves "a branch the checkout does not stand on" with `update-ref` and no other check.
- Measured (`t6`): `update-ref refs/heads/spec/X <tip> <old>` exits 0 while a linked worktree has `spec/X` checked out. That worktree is left with HEAD on `<tip>` and its index and files on `<old>` (`M  f`). That is anti-goal 4, in someone else's checkout.
- `session-branch.py`'s `refuse_checked_out` exists for exactly this case.
- *Fix:* refuse, with its own reason clause, where `worktree list --porcelain` shows the branch checked out anywhere. Add a selftest.

**N4. The new remedy still autostashes under a common config.**
- `git pull --rebase origin <branch>` honours `rebase.autoStash=true`. Measured (`t8`, with the user's dirty `MM` file): `Created autostash … Applying autostash resulted in conflicts … Successfully rebased`, exit 0, `UU notes.md` holding conflict markers, and a kept stash.
- That is exactly what the user ruled out.
- §3.5's sentence "`pull --rebase` refuses up front … while anything is dirty (s2)" is false under that setting; s2 ran with the configuration isolated.
- *Fix:* `pull --rebase --no-autostash`, in §3.5 and §6's rows, and in the flush line of §4 step 6.

**N5. The register-move line misses this run's own renumbered findings.**
- §3.7 computes moves "by comparing each origin's number in `onto`'s register before the replay with the rebuilt one". This run's new findings are not in `onto`'s register, so their moves are never compared.
- Records sort by `(seq, at, file)`. Where the teammate committed first (often also the one who pushed first), it is *this run's* `[SEC#2]` that becomes `[SEC#3]`. That happens right after the run printed its report, follow-up lines and `_security.md` with `[SEC#2]`. s4g is the other case, where the teammate's finding moves.
- *Fix:* compare each origin's number on both sides with the rebuilt one: `onto`'s register and `c`'s. Use `rebuild`'s `numbers` map on each tree, which covers every origin; `register.json` names each finding by one origin only.

**N6. §8's fallbacks are undefined, and one reading of them loses data.**
- **Sync.** "A block-shaped file strict append cannot settle keeps the session branch's version and is listed in `sync.conflict`." If the builder still writes the merge commit with that file at the session branch's version, the default branch's change to the file counts as merged. The session pull request then *reverts* it on the default branch when it merges. Say that **no merge of that source is made**, as `sync()` does today on `merge-tree` exit 1.
- **Commit.** `commit()` calls `union_copy` before committing the working copy, and no fallback is given for when strict append cannot settle. As code stands, it would commit the unmerged working copy, dropping the entries only the branch holds: the very thing `union_copy` exists to prevent. Choose one: skip the path, keep the working copy and report it, as `put-back` lists `skipped`; or another rule. Then add the selftest.

### MINOR

**m-a. `ATTRIBUTES` and `info/attributes` still say `merge=union` for the block shapes.**
- In a session-mode clone, `ensure_attributes` writes that block into `info/attributes`, which outranks `.gitattributes`. The user's own `git pull`, `merge` or `rebase` in that clone keeps fusing entries; §3.5's remedy is one of those.
- `union_shaped()` decides `union_copy` by that attribute.
- The selftest near line 1251 asserts `union` for every appended shape.
- Say that `ATTRIBUTES` keeps `union` for `follow-ups.md` only, and that `union_shaped` becomes a classification by §2.1 shape.

**m-b. `push -u` does nothing with a sha source.**
- Measured (`t6`): `push --porcelain -u origin <sha>:refs/heads/spec/X` creates the branch and updates `refs/remotes/origin/spec/X`, but sets no upstream, silently.
- Drop "with `-u` as step 5 sets it", and say that no upstream is set. Step 5's tests fall back to the remote-tracking ref, which the push does write.

**m-c. The residual window and the harness's timeout.**
- State as accepted that a SIGKILL between `read-tree` and `commit` leaves the checkout on `<tip>` with the branch on `<old>`.
- Require the Bash call that runs `replay` to set a timeout above the script's own bounds: three fetches and three pushes plus margin, per `bounded-run`'s (N+5) rule. Otherwise the harness, not the script, can kill it mid-transaction.

**m-d. An empty list after the fetch is undefined.**
- Case: a push that landed although its report was lost (a bounded push killed after the server took it), and the teammate then pushed. Local is now strictly behind, `[rejected]` is reported, and condition 6's list is empty.
- Say what happens: fast-forward through the same move, push nothing, and print which row.

**m-e. The replay's passed block is never defined.**
§3.2 cites "the replay's block, §3.3", but §3.3 defines none. Presumably it is `**/follow-ups.md merge=union` alone, since the script settles every other shape itself.

### NIT

- `*-implementation-gaps.md` is a regenerated draft (`Generated <date>`, `## Gap <n>`, source-truth §7.5). As a block shape, a both-sides change always refuses. Classify it with `pr-draft.md` (`c`'s version whole), or state the refusal.
- "`<sha7>` … the remote's commit that already held it" needs a history search. Name `onto`'s tip instead.
- "the next recording scan lists the lines": §2's wording is "the first run that records anything", which includes triage and verify runs.
- The verification directory is **untracked**, not committed (`git status`: `?? docs/superpowers/verification/2026-10-27-lc11-measurements/`). The "77–78 ms" real-rebuild figure appears in none of its logs.

---

## 3. Builder check: what a planner would still have to guess (most important first)

1. **The exact append rule.** Entry boundaries (H2 lines, per N1), the matching key (bytes, ignoring trailing newlines), and the separator inserted between `o` and an added entry. *Why:* every merge path in both modes runs on it, and so do the selftest expectations.
2. **Add/add (N2).** Shared header as base, or always refuse? *Why:* the per-date feedback files make add/add routine; refusing costs a remedy line on every same-day pair.
3. **`commit()`'s fallback, and sync's per-source behaviour (N6).** *Why:* one choice loses branch-only entries; the other reverts a teammate's change through the session pull request.
4. **A branch checked out in another worktree (N3).** Refuse with which clause, and does the replay still try the other branches? *Why:* the reason vocabulary and the §3.4 retry loop.
5. **`ATTRIBUTES` and `union_shaped` (m-a).** Rewrite the block in existing clones' `info/attributes` on the next run, as `ensure_attributes` would? *Why:* it changes users' own merges in session-mode clones, and an existing selftest flips.
6. **The replay call's timeout (m-c) and the empty list (m-d).** *Why:* both decide whether a run can end with the checkout on a different commit than its branch, or report a push it did not make.

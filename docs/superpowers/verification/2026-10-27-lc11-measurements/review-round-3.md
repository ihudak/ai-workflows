# LC11 design review, third draft

Design: `/workspace/.worktrees/lc11/docs/superpowers/specs/2026-10-27-lc11-run-settles-rejected-push-design.md` (third draft).

Scratch evidence, all under `scratchpad/lc11-review/`:
- `t7/draft3.py`: §3.3's rule exactly as written, on cases 1–5.
- `t7/entryset.py`: the rule proposed below, on all ten cases.
- `sb/d3/`, `sb/es/`: `session-branch.py` with `union_copy` replaced by each rule. `sb/flow5-d3`, `sb/flow5-es`: one ordinary session-mode flow through each.
- `t9`: `pull --rebase --no-autostash` under `rebase.autoStash=true`.

No repository was changed.

**Verdict: NOT READY.** Every item from the first two reviews is resolved, and the coordinator's calls are sound. One defect remains, in the new rule itself: §3.3 still requires `base` to be a **byte prefix** of both sides, and it compares entries **with** their trailing blank lines.
- **The prefix test:** after any merge that puts one side's entries before the other's, the next merge on that file refuses. That merge can be the replay's own first commit, or a session-branch sync. In session-branch mode this is the ordinary team flow, measured in the real script: the next commit of the same file refuses, and so does every later one.
- **The trailing blank lines:** this brings back the doubling in cases 1 and 2.

An entry-set rule fixes both. It settles all ten cases and the real flow, and refuses real edits. It is a precise rewrite of one paragraph of §3.3 plus three selftests. One MAJOR precision point in §8 goes with it.

---

## 1. Earlier findings and questions: status

| Item | Status |
|---|---|
| B1 (union fuses entries) | Resolved in intent. The rule still needs N7 below. |
| M1 / N4 (autostash) | **Resolved.** Verified (`t9`): under `rebase.autoStash=true`, `pull --rebase --no-autostash` exits 128 with *cannot pull with rebase: You have unstaged changes*. `MM` stays `MM`, the bytes are identical, and no stash is made. |
| M2 (partial success) | Resolved. |
| m1–m4, m-c (timeout and the SIGKILL window), m-d (empty list), m-e (the replay's block) | Resolved. |
| m5 / N3 (worktrees) | Resolved by §3.1 condition 7, with the retry going on to the other branches. |
| N1 (append doubles), N2 (add/add) | **Not yet right:** see N7. The add/add rule (identical pre-heading bytes as `base`) is sound once N7's comparison is used. |
| N5 (register moves) | Resolved: both sides, from `rebuild`'s `numbers`. NIT: read each side's numbers by running `rebuild`'s `numbers` on that side's tree too. `register.json` names each finding by one origin only, so an alias origin is missed there. |
| N6 (§8 fallbacks) | Defined. See N8 for the precision it still needs, and m-f for its consequences. |
| m-a (`ATTRIBUTES`) | Resolved. |
| m-b (upstream) | Resolved, with one more sweep item: m-g. |
| NITs | All done. The gaps draft now counts as overwritten: see m-h. |
| Format check | I confirmed every appended shape opens each entry with `## `: `implementation-format` §1 (`## <date> — /implement`), `feedback-emission` §1, scan.md §7.3 and `cost-emission` §6 (`## <timestamp> — <command> — <phase>`). The pending cost file and both feedback rungs use the same formats. No shape is left for "anything else". |

---

## 2. Findings

### BLOCKER

**N7. §3.3's entry rule refuses in the ordinary flow, and doubles entries in two cases.**
- **(a) Requiring `base` to be a byte prefix of both sides.** Strict append orders a merged file as `o`'s entries, then `t`'s new ones. So once one merge has put this side's `E1` before a teammate's `B1`, the file no longer extends the base the next merge reads.
  - **In session-branch mode (real script, `sb/flow5-d3`).**
    1. A commits `E1`.
    2. A teammate pushes `B1` to the same `implementation.md`.
    3. A's next run catches up and puts the overlay back. The session file is now `E1 B1`; HEAD's file is `B1`.
    4. A appends `E2` and commits. `union_copy`, with `base` = the version at `merge-base HEAD <tip>` = HEAD's, refuses: *base is not a byte prefix of both*.

    Under §3.8's fallback the run's entry stays out of the commit. **Every later commit of that file refuses the same way.** `lift` then reports it unpreserved, so the run skips the catch-up, B2/B4 and the switch onto the deliverable branch at handoff, until someone settles the file by hand. This hits every team in session mode with two writers on one file: the population the user's ruling was for.
  - **§8.2 step 3's second sync** (`t7` case 8): `base` is the last-merged default (`B1`), `o` is `E1 B1 E2`, and it refuses. The session branch never takes in the default branch again for that file.
  - **The replay, with two local commits on a file the remote also appended to** (`t7` case 6). `c2`'s `base` is `c1`'s file, `E1`; `o` is `B1 E1` after `c1` was replayed. It refuses. Reachable after any failed or refused push followed by another run on the same unit, which §3.5's *moved, not pushed* row now promises the next run settles.
- **(b) "An entry runs … with its trailing blank lines; it is compared byte for byte, whole."** An entry that is last on one side has no trailing blank line. The same entry with an entry after it does. The bytes differ, so it is added again (`t7/draft3.py`):
  - case 1, two `commit` calls in a row, doubles `E1`;
  - case 2, a sync after a squash-merged session pull request, doubles `E2`.

*Fix: an entry-set three-way rule.*
- **Split.** Each side is a header (the bytes before its first `## ` line) followed by entries (each `## ` line up to the next). Compare a header or an entry with its trailing blank lines stripped.
- **Refuse** where:
  - the headers of `o` and `t` differ;
  - where `base` exists, its header differs from theirs;
  - any entry of `base` is missing from `o` or from `t`. That is an edit or a removal, and it also catches a continuation of `base`'s last entry.
- **Otherwise** the result is `o`, then each entry of `t` that `o` lacks, in `t`'s order, one blank line before each, adding no other bytes.
- **Add/add** (no `base`) is the same rule, with no `base` entries to check.

`t7/entryset.py` settles all ten cases correctly: no entry doubled or fused, one header. It refuses an edited entry (case 9) and a line added to the last entry (case 10). In the real script (`sb/flow5-es`) the same session flow commits `E2` cleanly: `aaaaaaa, bbbbbbb, ccccccc`. The design's own premise (byte-identical entries are the same entry) is all it relies on, and it needs no prefix.

*Selftests to add to §4:*
- the replay of two local commits on a file the remote also appended to;
- a `commit` after a sync that merged a teammate's entry into the same file;
- a second sync after a first one that merged.

### MAJOR

**N8. §8's merges must settle block-shaped files from the three blobs, not from `merge-tree -X ours`.**
- §3.3 says the *replay* never trusts git's merge. §8.2 step 3 keeps `merge-tree --write-tree -X ours`, though, and §3.8 now removes `union` from `ATTRIBUTES`.
- Under `-X ours`, a block-shaped file both sides appended to is resolved silently to the session branch's version, and `merge-tree` reports **no conflict**. A builder who applies strict append only to reported conflicts gets a merge commit that drops the teammate's entry. The session pull request then deletes that entry from the default branch when it merges.
- *Fix:* say that §8's merges, like the replay, settle every block-shaped path both sides changed with the strict-append function, whatever `merge-tree` wrote. Add a selftest where `-X ours` would have dropped an entry.

### MINOR

**m-f. Name the consequences of §3.8's `commit` fallback.**
- A working copy left out of the commit is "unpreserved" to `lift`, so every move of the checkout is skipped until the user settles the file. That includes the deliverable handoff's switch.
- Its report also borrows `sync.conflict`, whose §6 append reads "merging <default> into session/<identity> left <path> unsettled — settle them in its pull request". That text is wrong for a working-copy refusal, which is in the working tree, not the pull request.
- Give it its own field and line, and say what settling the file means for the user.
- After N7 it is rare: only a real edit or removal triggers it.

**m-g. `branch --set-upstream-to` is a new configuration write.**
§1 rule 8 lists what this reference writes, and counts "the upstream a `push -u` sets" as git's own write. Add the new write to rule 8 and to the sweep. It fails on a read-only `.git/config`, which §3.4 already treats as reported and harmless.

**m-h. `*-implementation-gaps.md` needs a `-merge` line.**
It is now an overwritten shape, so it needs `-merge` in the replay's block and in `ATTRIBUTES` beside `pr-draft.md`. Dropping its `union` without that leaves the plain text driver. Under §8's `-X ours`, that splices the two drafts' non-conflicting hunks instead of keeping one draft whole.

### NIT

- A `## ` line inside an entry's body would split it into two pieces. A piece identical to one in another entry would then be dropped. Accept this, or have the build check that each piece's heading matches its format's heading shape (`## <date> — `).

---

## 3. Builder check: what a planner would still have to guess

1. **The exact rule:** confirm N7's entry-set rule, including that headers and entries are compared without trailing blank lines and that `t`'s new entries follow all of `o`'s. *Why:* it is the one function the replay and three §8 call sites share, and every selftest expectation depends on it.
2. **§8's merge mechanics (N8):** keep `-X ours` for every path but block-shaped files, and settle each block-shaped file both sides changed from the three blobs? *Why:* it decides whether the session pull request can delete a teammate's entry.
3. **The `commit` fallback's report (m-f):** a field and §6 line of its own, and what settling means for the user? *Why:* the line is printed literally, and `lift`'s skipped moves need to be named in it.

Nothing else is left to guess. §6's list stays as it is (wording, the `read-tree` refusal capture, the capability-check shape and the time bounds).

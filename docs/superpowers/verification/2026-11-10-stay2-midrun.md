# STAY-2 and MIDRUN-B4 — verification record

**Plan:** `docs/superpowers/plans/2026-11-10-stay2-midrun.md`. **Design:** `docs/superpowers/specs/2026-11-10-stay2-midrun-design.md`, with its research memo `2026-11-10-stay2-midrun-research.md` beside it. **Releases:** `workflows-core` 1.84.0, with `dev-workflows` 4.62.4, `product-workflows` 3.79.3, `docs-workflows` 1.38.3 and `security-workflows` 0.11.3 beside it, each section dated 2026-11-12. **Branch:** `fix/stay2-midrun`, base `38aec858` (`main` after PR #182, GIT-G1 Part 2a), with `main` at `8e441fa0` (PRs #183 and #184) merged into it at `a17e4758`. Measured at `25166a8b`, after the final review's third fix pass; the commits after it touch only `docs/superpowers/`. Written last, against the branch's own tree. Every figure below is re-derived here, with its command beside it; none is copied from the plan or a task report. Where a figure is the ledger's and not re-derived, the sentence says so.

The rulings summary is `2026-11-10-stay2-midrun-rulings.md` beside this file, and the ledger, copied as it stood when this record was written, is `2026-11-10-stay2-midrun-ledger.md`.

**Trees.** Several recipes take a commit's tree as their argument. Each tree is unpacked from the repository root into an empty scratch directory `$SCRATCH`, and nothing is ever added to it: the counting recipes read every file under it, so a file left there is counted (the sweep's recipe below says how this record learned that):

```bash
for sha in 38aec858 a17e4758 25166a8b; do mkdir -p "$SCRATCH/tree-$sha" && git archive "$sha" | tar -x -C "$SCRATCH/tree-$sha"; done
```

The branch holds 69 commits on its first-parent line (`git log --oneline --first-parent 38aec858..25166a8b | wc -l`), the merge of `main` among them. Against the `main` it merged, `git diff --shortstat 8e441fa0 25166a8b` gives 67 files changed, 12,677 insertions and 839 deletions.

## The scripts

### The selftests

Each run from the root of its tree (`id -u` prints 502, so `g_read_only` ran):

| Script | `38aec858` | `25166a8b` |
|---|---|---|
| `python3 plugins/workflows-core/scripts/specs-git.py --selftest` | `specs-git selftest: PASS (696 checks)`, real 39.7 s | `specs-git selftest: PASS (1176 checks)`, real 3 min 14 s |
| `python3 plugins/workflows-core/scripts/session-branch.py --selftest` | `session-branch selftest: PASS`, real 38.1 s | `session-branch selftest: PASS`, real 40.2 s |
| The same, with `check` counting its calls | 851 checks | 919 checks |

`session-branch.py` prints no count, by the ruling of Task 1 that its PASS line keeps its existing format. The last row is a copy of the script whose selftest `check` adds one to a counter on every call and whose PASS line prints it; nothing else in the copy changes. The copy is made in a second unpacked copy of each tree, kept apart from the `$SCRATCH/tree-<sha>` trees the counts below read, and run from that copy's root.

```python
import sys
s = open(sys.argv[1], encoding="utf-8").read()
s = s.replace("    def check(ok, what):\n        if not ok:\n", "    def check(ok, what):\n        _n[0] += 1\n        if not ok:\n", 1)
s = s.replace('    print("session-branch selftest: PASS")', '    print("session-branch selftest: PASS (counted: %d checks)" % _n[0])', 1)
s = s.replace("def selftest(", "_n = [0]\n\n\ndef selftest(", 1)
open(sys.argv[2], "w", encoding="utf-8").write(s)
```

The ledger's `specs-git.py` counts, not re-derived, show where the 480 checks came from: 696 at the base; 800 after Task 2; 847 after Task 3; 880 after Task 4; 947 after Task 5; 987 after Task 6; 1,099 after Task 7; 1,146 after Task 8; 1,149 after Task 9; 1,155 after Task 9b; and 1,169, 1,171, 1,172 and 1,176 after the final review's fix passes. The selftest's time grew from 40 s to about 3 minutes; the ledger carries it from Tasks 5 and 7 to the maintainer as a proposal: a split of the selftest out of the script, which is its own change.

The scripts grew with it (`git show <sha>:<path> | wc -l`): `specs-git.py` 8,464 → 18,105 lines, `session-branch.py` 5,292 → 5,817, `specs_git_state.py` 209 → 476, `specs_git_lines.py` 547 → 634. `references/specs-repo-git.md` (SRG below) grew from 195,390 to 273,941 bytes and the `specs-git` skill from 6,455 to 8,493 (`wc -c`). Until GIT-G1 Part 3 slims the reference, a run whose Phase 0 cites SRG outside §3.2's run key set, §5 and §6 still reads it whole (the 2a record's *What a run still reads, and why*), and that read is now 78,551 bytes larger.

### The checks, by group

`specs-git.py`'s selftest runs one function per group, `scenarios_<group>(tmp)`. A check is named by the string its case registration or its message opens with. The recipe takes every name in each group at both trees, as `python3 -I groups.py <base specs-git.py> <tip specs-git.py>`:

```python
import re, sys
NAME = re.compile(r'''["']([a-z]{1,2}_[a-z0-9_]*[a-z0-9])(?=:| \(|["'],)''')  # "t_x: …", "t_x (…", case("t_x", …)
def groups(path):
    out, cur = {}, None
    for ln in open(path, encoding="utf-8").read().split("\n"):
        m = re.match(r"    def scenarios_([a-z_]+)\(tmp\):", ln)
        if m:
            cur = m.group(1); out[cur] = []; continue
        if cur and ln.strip() and (len(ln) - len(ln.lstrip())) <= 4:
            cur = None
        if cur:
            out[cur].append(ln)
    return out
def names(body):
    found = {}
    for ln in body:
        for n in NAME.findall(ln):
            found.setdefault(n, []).append(ln.strip())
    return found
if __name__ == "__main__":
    base, tip = groups(sys.argv[1]), groups(sys.argv[2])
    for g in sorted(set(base) | set(tip)):
        b, t = names(base.get(g, [])), names(tip.get(g, []))
        print(g, len(b), len(t), "added:", *sorted(set(t) - set(b)), "removed:", *sorted(set(b) - set(t)))
```

A check kept from the base is **rewritten** where its code changed. The recipe cuts each group into blocks, each opening at a line that introduces a check — a comment `# <name>[, <name>…]`, a nested `def <name>(` or a `case("<name>"` — and compares the whitespace-collapsed text of every block a kept name opens, as `python3 -I rewritten.py <base> <tip> <directory holding groups.py>`:

```python
import re, sys
sys.path.insert(0, sys.argv[3])
from groups import groups, names
OPEN = re.compile(r'^\s*(?:#\s*((?:[a-z]{1,2}_\w+)(?:,\s*[a-z]{1,2}_\w+)*)\b|def ([a-z]{1,2}_\w+)\(|case\("([a-z]{1,2}_\w+)")')
def blocks(lines):
    out, cur = {}, None
    for ln in lines:
        m = OPEN.match(ln)
        if m:
            cur = []
            for n in (m.group(1) or m.group(2) or m.group(3)).split(","):
                out.setdefault(n.strip(), []).append(cur)
        if cur is not None:
            cur.append(" ".join(ln.split()))
    return {n: [" ".join(b) for b in bs] for n, bs in out.items()}
base, tip = groups(sys.argv[1]), groups(sys.argv[2])
for g in sorted(set(base) & set(tip)):
    b, t = blocks(base[g]), blocks(tip[g])
    keep = set(names(base[g])) & set(names(tip[g]))
    print(g, sorted(n for n in set(b) & set(t) & keep if b[n] != t[n]))
```

`own_change`'s checks live in `session-branch.py`, whose selftest registers its cases by `guarded("<name>", …)`; the base has none of the `oc_*` cases, and the tip has 24 (the distinct matches of `guarded\("(oc_\w+|mb_message)"` after `def selftest(`: 0 at `38aec858`, 24 at `25166a8b`).

| Group | Names, base → tip | Added | Rewritten | Removed |
|---|---|---|---|---|
| `own_change` (`session-branch.py`) | 0 → 24 | `mb_message`, `oc_block_branch_only`, `oc_block_edit_onto`, `oc_block_forms`, `oc_block_header`, `oc_block_new_file`, `oc_block_snapshot`, `oc_delete`, `oc_dirs_gone`, `oc_final_line_ending`, `oc_lines_branch_only`, `oc_lines_forms`, `oc_lines_new_file`, `oc_lines_onto_has`, `oc_lines_remove_branch_only`, `oc_lines_remove_onto`, `oc_lines_snapshot`, `oc_lines_tick_onto`, `oc_nothing`, `oc_old_git`, `oc_partial`, `oc_register`, `oc_untracked_leftover`, `oc_whole`, with `oc_checkout_untouched` asserted inside every `oc` case | — | — |
| `state` | 13 → 21 | `s_fields`, `s_find`, `s_find_before`, `s_left_behind`, `s_legacy_merged_stay`, `s_others`, `s_park_unpark`, `s_save_at` | `s_outside_repo` | — |
| `lines` | 14 → 19 | `l_constants`, `l_fill_landing`, `l_g1_end`, `l_g1_not_done`, `l_pins_all` | `l_fill_alternation`, `l_fix_lines`, `l_ids` | — |
| `land` (new) | 0 → 61 | `l_chain_committed_land`, `l_chain_committed_retry`, `l_chain_delete_behind_whole`, `l_chain_lift_pruned`, `l_chain_partly_own`, `l_chain_partly_stopped`, `l_checked_out_detail`, `l_cli_detail`, `l_cli_exit2`, `l_cli_land`, `l_cli_local_retries`, `l_cli_retry_partial`, `l_cli_start_dirty`, `l_held_chain`, `l_held_drop`, `l_held_orphan_refs`, `l_held_rebuild`, `l_held_then_own`, `l_held_then_own_there`, `l_held_unrelated`, `l_here_resume_unfinished`, `l_land_absent`, `l_land_behind`, `l_land_behind_checked_out`, `l_land_checked_out_no_push`, `l_land_diverged`, `l_land_here`, `l_land_here_recheck`, `l_land_here_refused`, `l_land_hook`, `l_land_locked`, `l_land_moved`, `l_land_no_snapshot`, `l_land_nothing`, `l_land_old_git`, `l_land_on_move`, `l_land_partial`, `l_land_pending_own`, `l_land_register`, `l_land_resume`, `l_land_resume_chain`, `l_land_resume_on_default`, `l_land_snapshot`, `l_land_snapshot_deleted`, `l_land_there`, `l_land_there_refused`, `l_land_unkeyed`, `l_retry_budget`, `l_retry_held_blocked`, `l_retry_held_edited`, `l_retry_held_here`, `l_retry_held_here_ancestor`, `l_retry_held_here_elsewhere`, `l_retry_held_here_old`, `l_retry_held_here_staged`, `l_retry_held_journal`, `l_retry_held_journal_before_move`, `l_retry_held_on_default`, `l_retry_local_only`, `l_sb_reused`, `l_split_collision` | — | — |
| `start` | 70 → 95 | `t_b4_no_local_default`, `t_fix_no_local_default`, `t_rerun_blocked_midnight`, `t_rerun_blocked_midnight_during`, `t_rerun_commit_key`, `t_rerun_no_guess`, `t_session_files_always`, `t_snap_bug`, `t_snap_g1`, `t_snap_misrooted`, `t_snap_narrowed`, `t_snap_rerun`, `t_snap_rerun_unset`, `t_snap_status_failed`, `t_start_json`, `t_stay_b4_commit_key`, `t_stay_b4_refused`, `t_stay_cleared`, `t_stay_g1_commit_key`, `t_stay_g1_keyed`, `t_stay_g1_merged`, `t_stay_g1_unkeyed`, `t_stay_keys_none`, `t_stay_stopped`, `t_stay_unlisted_b4`, and the 21 `t_land_merged_*` checks that replace 2a's `t_d5_*` one for one (`_b3_g1`, `_budget`, `_budget_done`, `_budget_moved`, `_committed_on_branch`, `_declined`, `_fix_line`, `_g1`, `_g1_kill`, `_g1_unknown`, `_leave_refused`, `_moved`, `_next_run`, `_nothing`, `_refused_kill`, `_rerun_b3`, `_rerun_clears`, `_rerun_stopped`, `_resume`, `_status_failed`, `_stopped`) | `t_b3_b4`, `t_budget_resume`, `t_catch_up_failed`, `t_error_after_write`, `t_flush_failed`, `t_flush_refused`, `t_g0`, `t_g1`, `t_g2`, `t_g2_implement`, `t_merged_leave_kept`, `t_merged_unknown`, `t_nonff_order`, `t_replaced`, `t_rerun`, `t_rerun_blocked`, `t_rerun_resume`, `t_resume_stale`, `t_settle_queue`, `t_two_commands` | the 21 `t_d5_*`, renamed as `t_land_merged_*` with D5's hold replaced by the landing |
| `end` | 40 → 118 | the landing: `e_g1_uncommitted` and 46 `e_land_*` (`_budget`, `_budget_moved`, `_checked_out_no_origin`, `_checked_out_pushed`, `_commit_key`, `_commit_key_midrun`, `_declined`, `_g1`, `_hand_edit`, `_held`, `_held_landed_at_end`, `_held_mode_takes`, `_kill`, `_kill_before_move`, `_kill_refspec`, `_kill_register`, `_kill_resumed`, `_kill_stuck`, `_leftover_kept`, `_leftover_shared`, `_legacy`, `_locked`, `_locked_held`, `_merged`, `_mode`, `_moved`, `_no_origin`, `_no_origin_main`, `_nonff`, `_not_finished`, `_offline`, `_origin_lacks_checked_out`, `_origin_lacks_default`, `_partial`, `_push_rows`, `_refused`, `_register`, `_resume_dropped_excludes`, `_resume_moved`, `_scope`, `_stopped`, `_stuck`, `_there`, `_unlisted`, `_unpushed_retry`, `_unsupported`); the end's held files: `e_end_changed_resume`, `_resume_push`, `_resume_twice`, `_shown`, `_signal`, `e_end_excludes_held`, `e_end_on_default_drops`; the held stage, which shares these worlds: `t_default_push_g1`, `t_default_push_nonff` and 22 `t_held_*` (`_changed`, `_flush_excludes`, `_here_finished`, `_journal`, `_journal_before_move`, `_locked`, `_locked_changed`, `_locked_default`, `_locked_journal`, `_locked_mode`, `_locked_stuck`, `_misrooted`, `_mode`, `_on_default`, `_resume`, `_resume_failed`, `_resume_rebuilt`, `_resume_stuck`, `_retry`, `_retry_fails`, `_stuck_reported`, `_then_own_across_start`) | `e_blocked`, `e_canned`, `e_declined_blocked`, `e_g0_found`, `e_push_refused`, `e_push_status`, `e_refused_before`, `e_stale_no_preflight` | — |
| `midrun` (new) | 0 → 86 | `e_midrun_here_kill`, `e_midrun_here_kill_moved`, `e_midrun_here_lock`, `e_midrun_here_no_resume`, `e_midrun_here_resume_elsewhere`, `e_midrun_here_unfinished`, `e_midrun_kept`, `e_midrun_kept_b3`, `e_midrun_kept_ended_catch_up`, `e_midrun_no_snapshot`, `e_midrun_open_ended`, `e_midrun_unlanded`, `e_no_preflight_named`, `e_no_preflight_open`, `e_no_start_midrun`, `k_started`, `t_call_returned_error`, `t_call_returned_mark`, `t_call_returned_named`, `t_derived_not_parked`, `t_guard_here_replay`, `t_guard_open_run_ended`, `t_guard_s3_middle_first`, `t_guard_s3_restart_first`, `t_guard_s4_later_first`, `t_guard_s4_untyped_first`, `t_guard_untyped_alone`, `t_midrun_abandoned`, `t_midrun_b3`, `t_midrun_catch_up`, `t_midrun_default`, `t_midrun_ends`, `t_midrun_ends_clear`, `t_midrun_ends_command_again`, `t_midrun_ends_end`, `t_midrun_ends_head_left`, `t_midrun_g1`, `t_midrun_g2`, `t_midrun_handoff_moved`, `t_midrun_handoff_open`, `t_midrun_here_journal_ancestor`, `t_midrun_keyed_other`, `t_midrun_keyless`, `t_midrun_keyset`, `t_midrun_left_before`, `t_midrun_left_returned`, `t_midrun_misrooted`, `t_midrun_mode`, `t_midrun_mode_catch_up`, `t_midrun_noop_move`, `t_midrun_not_open`, `t_midrun_open_next_aged`, `t_midrun_open_rerun`, `t_midrun_open_resume`, `t_midrun_open_writes_here`, `t_midrun_open_writes_stay`, `t_midrun_reflog`, `t_midrun_reflog_none`, `t_midrun_rerun`, `t_midrun_rerun_no_record`, `t_midrun_same_command`, `t_no_start_end_beside`, `t_park_abandoned_middle`, `t_park_dropped`, `t_park_misrooted_stop`, `t_park_out_of_order`, `t_park_out_of_order_landing`, `t_park_replay`, `t_park_rerun`, `t_park_rerun_replays`, `t_park_stack`, `t_rerun_cut_off`, `t_rerun_cut_off_overwritten`, `t_rerun_old_stamp_end`, `t_rerun_stopped`, `t_rerun_stopped_parked`, `t_resume_stale_no_park`, `t_resume_unnamed_other_run`, `t_resume_unnamed_restored`, `t_same_command_other_key_first_second`, `t_same_command_other_key_second_first`, `t_same_command_restart`, `t_same_command_restarts_parked`, `t_started_missing_end`, `t_started_not_found`, `t_stay_merged_midrun` | — | — |
| `mode` | 25 → 26 | `m_land_merged`, `m_no_stay` | `m_budget_overlay`, `m_not_finished`, `m_unsupported` | `m_d5`, now `m_no_stay` |
| `skill` | 6 → 8 | `k_branch_check_midrun`, `k_skill_fallback` | `k_key_set_quotes`, `k_skill_fields`, `k_skill_options` | — |
| `replay` | 17 → 17 | — | `r_canned`, `r_refused_form`, `r_signalled`, `r_start_current`, `r_start_queued`, `r_start_refused` | — |
| `gate`, `push_scope` | unchanged | — | — | — |

Sixty-two names were looked up one by one at the tip (`grep -c "[\"']<name>[\"': (]" plugins/workflows-core/scripts/specs-git.py`, none 0): the 48 the Done-when table's *Checks* column names below — 25 single names, the two `t_same_command_other_key_*` and the 21 `t_land_merged_*` — and the 14 other checks the final passes added: `t_midrun_open_writes_stay`, `t_midrun_open_writes_here`, `t_same_command_restart`, `t_same_command_restarts_parked`, `t_no_start_end_beside`, `t_resume_unnamed_restored`, `t_guard_s3_middle_first`, `t_guard_s3_restart_first`, `t_guard_open_run_ended`, `t_guard_s4_later_first`, `t_guard_s4_untyped_first`, `t_guard_untyped_alone`, `t_guard_here_replay` and `l_cli_start_dirty`. The final passes' `t_guard_other_run` and `l_cli_open_run` are gone (the same grep, 0), replaced by `t_guard_s3_*` and `l_cli_start_dirty` under rulings (a) and P1.

### The spec's §5, item by item

Each item with the checks that hold it, the task whose RED run shows each failing before its code, and the mutants that fail it, from the appendix below. "None named" means the task's harness holds no mutant written for that check: its evidence is its RED line alone.

| Done when | Checks | RED in | Mutants |
|---|---|---|---|
| STAY-2, G1 on another key's branch | `e_land_g1` | Task 5 | Task 5 m00 |
| STAY-2, a refused switch | `e_land_refused` | Task 5 | none named |
| STAY-2, `status` failed | `e_land_unlisted` | Task 5 | Task 5 m13 |
| STAY-2, an early stop | `e_land_stopped` | Task 5 | none named |
| STAY-2, the budget-stopped start | `e_land_budget` | Task 5 | Task 5 m12 |
| D5's merged stay | `e_land_merged`, and the 21 `t_land_merged_*` | Task 5 | Task 5 m02, m27 |
| MIDRUN-B4, keyless | `t_midrun_keyless` | Task 7 | Task 7 m1, m2 |
| MIDRUN-B4, keyed with another key | `t_midrun_keyed_other`, the same function with `--key ACME-2` | Task 7 | m1 and m2 fail the shared body; none named for this case |
| The same command typed twice | `t_midrun_same_command`, `t_park_out_of_order`, and, after the user's M1 decision, `t_same_command_other_key_*` | Task 7; the final fix pass | Task 7 m6, e12, e13; pass 1's "park never protects" |
| The refused landing | `e_land_held`, `e_land_stuck`, `e_land_partial` | Task 5 | Task 5 m10, m17; m18; m11, m16 |
| The unpushed landing's retry | `e_land_unpushed_retry`, `t_default_push_g1` | Task 6 | Task 6 m19; m16, m17 |
| A kill between the ref move and the lift | `e_land_kill`, `e_land_kill_before_move`, `t_held_journal`, `e_midrun_here_kill`, `e_midrun_here_no_resume` | Tasks 5, 6, 7 | Task 5 m20; m03, m31; Task 6 m03 fails `t_held_journal_before_move`, none named for `t_held_journal`; Task 7 e6 fails `e_midrun_here_kill_moved`, none named for the other two |
| Offline | `e_land_offline` | Task 5 | none named |
| No `origin` | `e_land_no_origin` | Task 5 | none named |
| The prose primitive | `l_cli_land` | Task 2 | Task 2's `l_cli_land` |
| A second worktree on `main` (the review focus's C2) | `l_land_behind_checked_out`, `e_land_checked_out_pushed` | Tasks 2, 5 | Task 2's `l_land_behind_checked_out`; Task 5 m19 |
| A mutant per new test | the appendix | — | 410 mutants across the tasks and the final passes, every one killed; the exceptions are the "none named" cells above |
| `to-fix.md`, `to-test-on-real-project.md` | STAY-2 and MIDRUN-B4 closed in `to-fix.md`'s *From GIT-G1 Part 2a* paragraph; MIDRUN-HANDOFF (S4, Part 3), MIDRUN-LATEWRITE (Part 3) and MIDRUN-2S (*Accepted*) filed; 18 live items under `## STAY-2 and MIDRUN-B4 — workflows-core 1.84.0` (`awk '/^## STAY-2 and MIDRUN-B4/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md \| grep -c '^- \*\*'`) | — | — |
| The release | the five versions above, `plugin.json` and `marketplace.json` agreeing; dated CHANGELOGs; the 1.84.0 coupling bullet; this record | — | — |

### Not pinned by the selftest

- Whether a run prints and follows the skill's text and its `--started`, `--snapshot -` and `land` calls: agent behaviour, for the r4 live round and the 18 to-test items. `k_skill_options`, `k_skill_fields` and `k_skill_fallback` hold only the skill's text against the CLI and SRG.
- A read-only bind mount: the selftest holds `.git/config.lock` in its place, which fails the same git call after the ref is made and before HEAD moves; only git's error text differs (Task 9b's ruling on its concern 3).
- The 420 s and 600 s harness timeouts themselves; their renderings are pinned through `--timed-out` and the `next` lines.
- Two sessions on one checkout: not covered, by design (MIDRUN-2S).

## Task 9b — no switch or branch creation half-moves a checkout

Added by the user on 2026-11-12, after Task 9's fix round 2 found the defect in the specs preflight's own switch and fixed it there (`dc0b69ec`): where `.git/config` cannot be written, as a hardened container mounts it, a `git switch <b>` that lets `--guess` create `<b>` with an upstream moves the index and working tree, fails on the configuration write, and exits 1 with HEAD left behind — a staged reversal of the old branch's work, which a caller reading exit 1 as "refused" leaves standing. Task 9b took the same hazard out of the rest of the family: five commits, `81688733`, `9f3ca7ff`, `1003b0fb`, `293ecb65` and `4177f08b`.

### Its class measurements, on git 2.43.0

Re-run for this record from the task's own scripts, copied into a scratch directory and pointed at it: a bare `origin` with `main` and `feat/x`, a fresh clone per case standing on `prd/X-1-y` (one commit behind `main`, with a file `p` of its own) and local `main` deleted, every command run with `.git/config.lock` held. `git --version` prints `git version 2.43.0`.

| Case | Command | Exit | What moved | Class |
|---|---|---|---|---|
| a1 | `git switch main`, no local `main` (`--guess`) | 1 | `main` made; index and tree moved (`A b; D p`); HEAD stays on `prd/X-1-y` | (a) half-moves |
| a2 | `git checkout main` (DWIM) | 1 | the same | (a) half-moves |
| a3 | `git switch --no-guess main` | 128 | nothing | the fix's switch |
| a4 | `git switch main`, local `main` present | 0 | the whole checkout | — |
| b1, b2 | `switch -c topic origin/feat/x`, `checkout -b topic origin/feat/x` | 1 | `topic` made; index and tree moved (`D p; A x`) | (b) half-moves |
| b3 | `git branch topic origin/feat/x` | 1 | the ref only | (b), no checkout to move |
| b5 | `git switch --track origin/feat/x` | 1 | `feat/x` made; index and tree moved | (b) half-moves |
| b6, b10 | `switch --no-track -c topic origin/feat/x`; `branch --no-track topic origin/feat/x` | 0 | the whole checkout; the ref only | the fix's creation |
| c1, c3 | `push -u origin prd/X-1-y`, plain and `--porcelain` | 0 | nothing | (c) prints the config error, exits 0 |
| c2 | `branch --set-upstream-to=origin/main main` | 1 | nothing | (c) fails, moves nothing |
| d1 | bare `pull --ff-only`, branch with no upstream | 1 | nothing | (d) fails |
| d2 | `pull --ff-only --no-rebase origin main`, no upstream | 0 | fast-forward | the fix's pull |
| d3 | bare `push`, no upstream | 128 | nothing | (d) fails |
| d4 | `switch main && pull --ff-only`, no local `main` | 1 | `main` made; index and tree moved; the pull never ran | (a) + (d) |
| e1 | `checkout -B main origin/main` | 1 | index and tree moved | (e) half-moves |
| e2 | `worktree add -b topic ../wt origin/feat/x` | 255 | the ref | (e) |
| f1, f2 | `-c branch.autoSetupMerge=always switch -c topic` from HEAD; from a local `base` | 1 | `topic` made; f2 moved index and tree | (b) under `always` |
| f3, f4 | the same setting, with `--no-track` | 0 | the whole checkout; the ref only | the fix |
| f6 | `git switch nosuch`, no `origin/nosuch` | 128 | nothing | (a) with nothing to guess |
| f9, f10 | `update-ref` (or `branch --no-track`), a failing `--set-upstream-to`, then `switch --no-guess main` | 0 | the whole checkout | the fix's three steps |

Under `branch.autoSetupMerge=always` (the pre-review fix's measurement, re-run the same way): a cut from a detached HEAD sets no upstream (g1, g2: exit 0); every `--no-track` cut exits 0 (g3–g6, g9); `branch sf prd/X-1-y` and `checkout -b topic` with no `--no-track` exit 1 (g7, g8). The fix's rule, from those rows: never let `--guess` or implicit tracking create a branch — create it with no configuration write (`git branch --no-track`, or `update-ref` as `specs-git.py`'s `_make_default` does), set the upstream best-effort in a step whose failure moves and stops nothing, then `git switch --no-guess`; pull and push by explicit `origin <branch>`.

**A read-only bind mount was not measured**: `unshare` is not permitted in the container and the run is not root. The held lock fails the same call (`install_branch_config`) after the ref is made and before HEAD moves; only the error text differs.

### Its population, and the counts re-derived

The task read every site in `plugins/*/{commands,agents,references,skills,scripts,docs}` where the family runs or prints a git command that can write `.git/config` as it creates or switches a branch, by the execution phrase. It found 22 exposed sites at `a17e4758`, fixed in `81688733`; the pre-review fix (`9f3ca7ff`) added `--no-track` to every creation from a local start or HEAD, for a user's `branch.autoSetupMerge=always` (f1, f2); fix round 1 (`1003b0fb`) widened class (e) to every executed command that writes `.git/config` and fixed three more. Each fixed site's form, counted wrap-insensitively in its file at 9b's base and at the tip, as `python3 -I sites.py "$SCRATCH/tree-a17e4758" "$SCRATCH/tree-25166a8b"` (a directory sums its `.md` files, `CHANGELOG.md` and `docs/` left out):

| Site (the report's number) | File | Fixed form | `a17e4758` | `25166a8b` |
|---|---|---|---|---|
| 1–3: SRG §5's G2, G2-on-the-session-branch and merged-G1 *Fix* lines | `workflows-core/scripts/specs_git_lines.py` | `"fix.make-default"` | 0 | 1 |
| 1–3, the wording | `workflows-core/references/specs-repo-git.md` | `makes the branch first where none exists` | 0 | 1 |
| 4: `phase-handoff` §3.3 row C's repair | `workflows-core/references/phase-handoff.md` | ``switch --no-guess <default>`` | 0 | 2 |
| 5–9: §4.4 rows I and C, §6.1's three forms | the same | ``A switch onto `<default>` that a stop names`` | 0 | 5 |
| 10: `read-only-repos` §3 | `workflows-core/references/read-only-repos.md` | `A switch never makes the branch` | 0 | 3 |
| 11–12: `code-scanner` step 2 | `workflows-core/agents/code-scanner.md` | `pull --ff-only --no-rebase origin <default-branch>` | 0 | 1 |
| 13: `diff-summarizer` step 5 | `docs-workflows/agents/diff-summarizer.md` | `A switch never makes the branch` | 0 | 1 |
| 14: `code-handoff` §2.8.1 step 3 | `dev-workflows/references/code-handoff.md` | `switch --no-guess <base>` | 0 | 1 |
| 15: `/implement` Phase 1.4, state `remote` | `dev-workflows/commands/implement.md` | `switch --no-track -c <branch> origin/<branch>` | 0 | 1 |
| 16: `/security-workflows:scan` Phase 1, state `remote` | `security-workflows/commands/scan.md` | `--no-track -c` | 0 | 1 |
| 17: `/conformance`'s `CONFORMANCE_RECORD_BEHIND` | `dev-workflows/commands/conformance.md` | `pull --ff-only --no-rebase origin <default>` | 0 | 1 |
| 18–21: `/document` 6.2, `/docs-profile` Phase 5, `/docs-init` and `/docs-brand` step 2 | each command | `switch --no-guess` | 0 each | 1 each |
| 22: `phase-handoff` §2.2's and §6.2's reasons for `--no-track` | `phase-handoff.md` | reworded to the measured half-move | — | — |
| Pre-review: the four docs commands' cuts | `docs-workflows/commands/` | `switch --no-track -c <name>` | 0 | 6 |
| Pre-review: `architecture-promotion` §11.1 step 1 | its reference | `switch --no-track -c <branch>` | 0 | 1 |
| Pre-review: `phase-handoff` §2.2's cut at HEAD, §4.4 C″ | `phase-handoff.md` | `switch --no-track -c <new-branch>` | 1 | 2 |
| Pre-review: `/implement` Pre-Phase 3, `/upgrade`, `vuln-fixer`, `code-handoff`'s cut | `dev-workflows/` | `checkout --no-track -b` | 0 | 5 |
| Pre-review: SRG §6's session-files remedies | SRG | `branch --no-track session-files-` | 0 | 2 |
| Round 1: `/document`'s rename of its profiling branch, read by its message | `document.md` | `branch is renamed, but update of config-file failed` | 0 | 1 |
| Round 1: `phase-handoff` §2.3's `branch -d` | `phase-handoff.md` | `warning: update of config-file failed` | 0 | 1 |
| Round 1: the *pushed straight to `<default>`* row's `config workflows.sessionBranch true` | `specs_git_lines.py` | `config workflows.sessionBranch true — where a` | 0 | 1 |

`sites.py`, whole:

```python
import os, sys
A, B = sys.argv[1], sys.argv[2]
SITES = [  # (label, a file or a directory under the tree, the fixed form): the table's 23 rows
    ('1-3', 'plugins/workflows-core/scripts/specs_git_lines.py', '"fix.make-default"'),
    ('1-3 wording', 'plugins/workflows-core/references/specs-repo-git.md', 'makes the branch first where none exists'),
    ('4', 'plugins/workflows-core/references/phase-handoff.md', 'switch --no-guess <default>'),
    ('5-9', 'plugins/workflows-core/references/phase-handoff.md', 'A switch onto `<default>` that a stop names'),
    ('10', 'plugins/workflows-core/references/read-only-repos.md', 'A switch never makes the branch'),
    ('11-12', 'plugins/workflows-core/agents/code-scanner.md', 'pull --ff-only --no-rebase origin <default-branch>'),
    ('13', 'plugins/docs-workflows/agents/diff-summarizer.md', 'A switch never makes the branch'),
    ('14', 'plugins/dev-workflows/references/code-handoff.md', 'switch --no-guess <base>'),
    ('15', 'plugins/dev-workflows/commands/implement.md', 'switch --no-track -c <branch> origin/<branch>'),
    ('16', 'plugins/security-workflows/commands/scan.md', '--no-track -c'),
    ('17', 'plugins/dev-workflows/commands/conformance.md', 'pull --ff-only --no-rebase origin <default>'),
    ('18', 'plugins/docs-workflows/commands/document.md', 'switch --no-guess'),
    ('19', 'plugins/docs-workflows/commands/docs-profile.md', 'switch --no-guess'),
    ('20', 'plugins/docs-workflows/commands/docs-init.md', 'switch --no-guess'),
    ('21', 'plugins/docs-workflows/commands/docs-brand.md', 'switch --no-guess'),
    ('pre-review: docs cuts', 'plugins/docs-workflows/commands/', 'switch --no-track -c <name>'),
    ('pre-review: architecture-promotion', 'plugins/workflows-core/references/architecture-promotion.md', 'switch --no-track -c <branch>'),
    ('pre-review: phase-handoff cuts', 'plugins/workflows-core/references/phase-handoff.md', 'switch --no-track -c <new-branch>'),
    ('pre-review: dev-workflows cuts', 'plugins/dev-workflows/', 'checkout --no-track -b'),
    ('pre-review: session-files', 'plugins/workflows-core/references/specs-repo-git.md', 'branch --no-track session-files-'),
    ('round 1: rename', 'plugins/docs-workflows/commands/document.md', 'branch is renamed, but update of config-file failed'),
    ('round 1: branch -d', 'plugins/workflows-core/references/phase-handoff.md', 'warning: update of config-file failed'),
    ('round 1: sessionBranch', 'plugins/workflows-core/scripts/specs_git_lines.py', 'config workflows.sessionBranch true — where a'),
]
def text(root, rel):
    p = os.path.join(root, rel)
    fs = [p] if os.path.isfile(p) else [os.path.join(d, f) for d, _, n in os.walk(p) for f in n if f.endswith(".md") and f != "CHANGELOG.md" and "/docs/" not in os.path.join(d, f)]
    return [" ".join(open(f, encoding="utf-8").read().split()) for f in fs if os.path.exists(f)]
for label, rel, form in SITES:
    a = sum(t.count(form) for t in text(A, rel)); b = sum(t.count(form) for t in text(B, rel))
    print("%s\t%s\t%s\t%d\t%d" % (label, rel, form, a, b))
```

**Not exposed**, each with the reason the task's report gives (not re-read site by site for this record; the task's three re-reviews and the final review read this table):
- SRG §3.5's B2 and B4 switch, §3.4's leave and the re-run's switch back: fixed in `specs-git.py` by Task 9 (`_make_default`, `switch --no-guess`).
- G0's rescue `switch -c rescue/<YYYY-MM-DD>` (SRG §5, `phase-handoff` §4.4 row I): from a detached HEAD git sets no upstream, whatever `autoSetupMerge` says (g1, g2).
- Switches onto a branch the run or the operator already has locally: G0's *If ignored* rejoin, SRG §6's `remedy.not-standing`, `phase-handoff` §2.2 rule 3's reuse, §2.3's switch back, §4.4 D, §6.2; `architecture-promotion` §8, §9 and §11.1 step 7 (§1.3 requires HEAD on the default branch at the start); the stash restores; `code-handoff`'s third bullet; `/implement`'s `local` state; `/vuln` Step 1.5; `/document` 4(c) and the left-on-a-branch notice.
- §4.4 E and F's no-`origin` `switch <default>`, and the 13 product-workflows stops' copies of it: with no `origin` there is no remote-tracking branch to guess from (f6: refused, 128, nothing moved).
- Every `push -u` and `--set-upstream-to` (c1–c3): exit 0, or exit 1 with nothing moved, and every executed site already words the unrecorded upstream.
- `switch --detach` and `worktree add --detach`: no branch created.
- `prose-style-refresh`'s `pull --ff-only`: its own fresh clone, which records its upstream.
- Selftest fixtures, example text and history.

The task's strings over claim-sweep refinement 4's scope, by the `count.py` below, `reference-parts/` counted on its own after the `+`:

| String | `38aec858` | `a17e4758` | `25166a8b` |
|---|---|---|---|
| `switch -c <name>` | 6+0 | 6+0 | 0+0 |
| `switch -c <new-branch>` | 1+1 | 1+1 | 0+0 |
| `branch session-files-` | 7+0 | 7+0 | 0+0 |
| `git checkout -b` | 7+0 | 7+0 | 2+0, both `dev-workflows`' CHANGELOG |
| `a switch git refuses after creating the branch` | 1+3 | 1+3 | 0+0 |
| `switch --track origin/<branch>` | 2+0 | 2+0 | 1+0, `security-workflows`' CHANGELOG |
| `git switch --track` | 1+0 | 1+0 | 3+0: `/implement`'s "Never `git switch --track`" and two CHANGELOG lines |
| `switch --no-guess` | 0+0 | 1+0 | 16+3 |
| `branch --no-track <default> <default-ref> &&` | 0+0 | 0+0 | 4+2 |
| `--set-upstream-to=<default-ref> <default>; git -C` | 0+0 | 0+0 | 4+2 |
| `pull --ff-only --no-rebase origin` | 9+0 | 9+0 | 22+2 |
| ``A switch onto `<default>` that a stop names`` | 0+0 | 0+0 | 5+6 |
| `A switch never makes the branch` | 0+0 | 0+0 | 14+0 |
| `switch --no-track -c <name>` | 2+6 | 2+6 | 9+9 |
| `switch --no-track -c <new-branch>` | 14+1 | 14+1 | 15+2 |
| `git checkout --no-track -b` | 0+0 | 0+0 | 6+0 |
| `branch --no-track session-files-` | 0+0 | 0+0 | 7+0 |
| `switch -c rescue/<YYYY-MM-DD>` | 3+1 | 3+1 | 3+1, kept (g1, g2) |
| `autoSetupMerge=always` | 0+0 | 0+0 | 14+3 |
| `branch is renamed, but update of config-file failed` | 0+0 | 0+0 | 2+0 |
| `warning: update of config-file failed` | 1+0 | 1+0 | 2+1 |
| ``Where the local `<base>` has diverged.`` | 0+0 | 0+0 | 4+0 |
| `rev-list --count origin/<base>..<base>` | 0+0 | 0+0 | 4+0 |
| `failed-pull question` | 0+0 | 0+0 | 9+0 |

The old forms count 0 at the tip outside CHANGELOG history and `/implement`'s own prohibition; the tip's figures include the later CHANGELOG lines and the final pass's carried edits, so several differ from the task report's per-round figures.

### Its selftests and mutants

- `t_fix_no_local_default` (`scenarios_start`), five asserts: the G2 *Fix* run with `.git/config` locked moves the checkout whole onto `main` and the end repeats it; with a local `main` the plain switch; the merged G1 form commits `notes.md` on `main`; with `.git/config` writable the upstream is set; refused over a file in the way it moves nothing, and the same line pasted again switches whole. RED at `a17e4758` and `9f3ca7ff`, the half-move reproduced through the printed remedy.
- `t_session_files_always`: SRG §6's session-files remedy runs under `branch.autoSetupMerge=always` with the lock held, and exits 0.
- Task 9's own, for the preflight's switch: `t_b4_no_local_default` (locked and writable) and `t_rerun_no_guess`.
- Mutants: 5 for Task 9b and 3 for Task 9, every one killed, in the appendix.

## The sweep

### The recipe

Every count is taken over claim-sweep refinement 4's scope — `plugins/` with every `CHANGELOG.md`, the root `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` — less the generated `plugins/*/reference-parts/`, as Task 3 Step 1 defines it; the generated parts are counted on their own after a `+` where they hold any. Each phrase is counted wrap-insensitively, whitespace collapsed in each file and in the phrase; case is kept. Run from the repository root as `python3 -I count.py "$SCRATCH/tree-<sha>" [--files] < phrases.txt`:

```python
import os, sys
root, show = sys.argv[1], "--files" in sys.argv[2:]
texts = {}
for top in ("plugins", "README.md", "CLAUDE.md", ".claude/rules", "docs/maintainers"):
    p = os.path.join(root, top)
    paths = [p] if os.path.isfile(p) else [os.path.join(d, f) for d, _, fs in os.walk(p) for f in fs]
    for f in paths:
        try:
            texts[os.path.relpath(f, root)] = " ".join(open(f, encoding="utf-8").read().split())
        except (UnicodeDecodeError, OSError):
            pass
for line in sys.stdin:
    phrase = " ".join(line.rstrip("\n").split())
    if not phrase:
        continue
    per = {f: t.count(phrase) for f, t in sorted(texts.items()) if phrase in t}
    main = sum(n for f, n in per.items() if "/reference-parts/" not in f)
    parts = sum(n for f, n in per.items() if "/reference-parts/" in f)
    print("%d\t%d\t%s" % (main, parts, phrase))
    if show:
        for f, n in per.items():
            print("\t\t  %s %d" % (f, n))
```

It reads every file of the unpacked archive, `.py` and `.json` among them. At `38aec858` its figures agree with Task 9's, which counted at that commit: `replaced` 307, `commits nothing` 60, `keyless` 177 and `Nothing here but start, end and replay writes` 1. Task 3 counted at its own base, `d9aa2ae7`, where the recipe gives Task 3's figures: `replaced` 308, since Task 2 had added one `replaced` to `specs-git.py`, and `Nothing here …` 0, since Task 2 had rewritten that docstring sentence to name `land`. So the task reports were right. This record's first version gave 310, 61 and 179 at the base (356, 74 and 200 at the tip) and blamed the reports: its trees held the untracked counting copy of `session-branch.py`, which holds 3 `replaced`, 1 `commits nothing` and 2 `keyless`. The figures below are counted on fresh `git archive` trees with nothing added (`comm -23` of each tree's file list against `git ls-tree -r --name-only <sha>` prints nothing).

### Task 3 Step 1's and Task 9 Step 1's subjects

| Subject | `38aec858` | `25166a8b` | Disposition |
|---|---|---|---|
| `merged-branch stay` | 32 | 2 | Replaced everywhere it described the shipped behaviour: SRG 11, `specs-git.py` 15, `specs_git_lines.py` 2, the state module, the skill and the rules file 1 each (Tasks 3–5, 8, 9). Left: `workflows-core` 1.82.0's CHANGELOG entry and the rationale's `stay-landing` history ("2a's D5 held a merged-branch stay's files"), both history. |
| `merged_stay` | 26 | 28 | True: `specs_git_state.py` 3 (an earlier version's record, mapped by `_read` to a stay of kind `merged`), `specs-git.py` 24, every one in the selftest (`s_legacy_merged_stay`, `e_land_legacy`, `k_skill_fallback`'s "not `merged_stay`"), and 1.84.0's CHANGELOG ("where it read `merged_stay`"). |
| `it never switches` | 4 | 5 | SRG §4.1's, kept and qualified: "where the preflight stayed on a branch it would have left, the commit is §4 step 1's landing onto `<default>`, without moving the checkout". `/docs-brand` and `/docs-init` use another sense (never onto a branch the run made), `scan-refresh.md` is about code repositories, and the fifth is `docs-workflows`' CHANGELOG. |
| `they belong to the run that wrote them` | 1 | 1 | SRG §3.4's flush, extended: such a run stood on this branch, since a run that had to stay took the landing instead. |
| `the one discard` | 2 | 0 | §1 rule 4 and §8.3 now name two discards, the landing's lift beside `lift` (Task 3). |
| `WILL still be committed` | 3 | 7 | True: SRG 2 (G1's plain block, and §5's sentence on when that block is repeated), its template, and `specs-git.py` 4, all selftest assertions that the not-committed forms lack it. |
| `a command typed in the middle of another` | 3 | 0 | SRG §7 and the state docstring reworded (Tasks 3, 7); the rationale's became "a different command typed …" (Task 9). |
| `G1 on a merged plugin branch` | 4 | 1 | SRG's heading became *G1 on a branch the run would have left*. Left: a selftest comment on `m_land_merged`, a session-branch-mode scenario where it is still literal. |
| `merged plugin branch the preflight stayed on` | 10 | 1 | `workflows-core` 1.82.0's CHANGELOG, history. |
| `Nothing else is written here` | 1 | 1 | SRG §1 rule 8: the held commits and `workflows/held.json` are listed before it, so it stays true. |
| `row.merged-stay`, `g1.merged.not_done` | 9, 2 | 0, 0 | Retired with D5's hold (Task 5). |
| `moves no ref` | 2 | 4 | SRG §1 rule 4 names the here form as its exception (two hits), §3.5's `merge-tree` test is unchanged, and 1.84.0's CHANGELOG says so. |
| `every other local plugin branch` | 3 | 3 | The settle loop's extent, unchanged (P21): SRG §3.4 and §4 step 6, and `_settle`'s docstring. |
| `every local plugin branch` | 1 | 1 | The rules file's §3.4 retry, unchanged and true. |
| `Nothing here but start, end and replay writes` | 1 | 0 | `specs-git.py`'s docstring now names `land` too (Task 2). |
| `the preflight did not commit, switch branches, or push` | 5 | 0 | G1's *Not done* opening reworded (P30, Task 3). |
| `replaced` | 307+2 | 353+2 | The record field `replaced` (SRG §7, the skill, the selftest's asserts) is Tasks 7 and 8's, stated with `parked`. Every hit of `replace` in SRG, the skill, the state module, the rationale, the rules file and References was read at the tip: the rest are other senses — a pointer overwritten, a commit replaced in the record, D5's hold replaced by the landing — and none states the old collision. Task 9 classed the hits elsewhere as unrelated English uses. |
| `held back` | 23 | 23 | Unrelated senses (brd-split, coverage ledgers, grilling, an overrule in `/conformance`), and SRG's and the rationale's held entries, true to §3.2. |
| `holds back` | 4 | 8 | SRG 2 ("an entry still held holds back the run's own change … where they share a path"), `specs-git.py` 3 (selftest messages), and `install-time-code.md` and `brd-interview.md`, unrelated. |
| `state of its own` | 1 | 1 | The rules file's hard rules; its list gained the held commits and their record (Task 9). |
| `artifacts are committed alongside them` | 2 | 2 | G1's plain *If ignored*, used only where the plain block is true (Task 5). |
| `nothing is lost` | 12 | 17 | `idea.md` and `frames.md` ("G1 does not set blocked, so the terminal `commit-artifacts` still runs and nothing is lost") stay true: the step runs, and a held landing keeps the files. The rest are SRG's and the templates' own, or unrelated. |
| ``the terminal `commit-artifacts` still runs`` | 2 | 2 | `idea.md` and SRG §3.3, as above. |
| `commits nothing` | 60 | 73 | The rules file's D5 clause was changed (Task 9); the new hits are the no-snapshot and no-start cases' own statements, true. Every docs and command hit is about misrooted, G0, a read-only mount, no identity, *Cancel* or the code handoff. |
| `stay uncommitted` | 15+1 | 17+1 | Other causes (`implement.md`, `conformance.md`, `code-handoff.md`, `document.md`, `session-hygiene.md`); SRG's and the templates' are the batch's own. |
| `a later run commits them` | 6 | 3 | Left: the *Commit failed* row, its template and its selftest, unrelated. |
| `leaves the branch first` | 0 | 0 | — |
| `never touches the outer run's record` | 1 | 0 | `specs_git_state.py`'s docstring at the base, false for the same command typed twice; it now says a different command is kept off the open run's record by its own file, and the same command by parking and `--started` (Tasks 4 and 7). |
| `one file per session and command`, `One file per session and command` | 2, 2 | 2, 2 | SRG §7 now says what one file keeps apart (two sessions; a different command typed mid-run) and that the same command twice is kept off by parking; the rationale and `specs-git.py`'s synopsis say the same. |
| `B4` | 125+1 | 188+1 | The `prompt*.md` and `harvest-decisions.md` sentences state B4's normal action, whose exceptions already stood; the mid-run stay joins them. `document.md`'s mermaid node ids and `feedback-emission`'s follow-ups "B4" are unrelated. The new hits are the batch's own. |
| `switches the checkout` | 2 | 2 | SRG's replay and a CHANGELOG line, unchanged. |
| `keyless` | 177+4 | 198+4 | Cost-entry and run-key-set senses, the B4 sentences above, and the batch's mid-run text. |
| `--no-preflight` | 16 | 32 | The skill's and SRG's no-start `end`, and the selftest's calls. |
| `otherwise silent unless it acts, a guard fires, or §3.1 reports` | 27 | 27 | The plan's "30 command lines" are 27 by the exact string. Each stays true: a held landing is an act, and SRG §3's silence list needs HEAD on the default branch, where the held stage drops entries silently and pushes nothing. |

For the generic subjects — `B4`, `keyless`, `--no-preflight`, `commits nothing`, `nothing is lost`, `held back`, `holds back`, `stay uncommitted` and `WILL still be committed` — every file whose count rose is one the batch wrote its mechanism into: SRG, `specs-git.py`, `specs_git_lines.py`, `specs_git_state.py`, `workflows-core`'s References page and CHANGELOG, and the rationale. That is by the recipe's per-file counts at both trees, outside `reference-parts/`; no command or docs page of any plugin gained one.

**The exclusivity probe** (refinement 3) over SRG and `phase-handoff.md` (`" ".join(text.split()).count(p)`), base → tip: SRG `the one` 30 → 33, `the only` 6 → 6, `only where` 19 → 28, `nothing else` 7 → 8, `never switches` 1 → 1, `moves no ref` 2 → 3; `phase-handoff.md` 18 → 18, 9 → 9, 21 → 22, 7 → 7, 0 → 0, 0 → 0. The hits Task 3 found falsified were rewritten there: `the one discard` (§1 rule 4, §8.3), `moves no ref` (the named exception), §4's "step 4 commits it alone", §4 step 6's two retry sentences, §7's "knows no merged-branch stay". Every hit the tip adds is this batch's own text, each reviewed in its task and, for the guard, by the third final re-review: the journal's "only where the move is verified" (three), the unnamed resume's "only where that record is marked so", the re-run's "only where its first start was one", the no-origin build's "only where no worktree has `<default>` checked out", the key clause's "only where its record holds one", the end's "only where it holds an `end_commit`", the guard's "and nothing else", the pull-request conflict's "the one … *Row B′'s remedy* gives", and `phase-handoff`'s row C upstream "only where `.git/config` can be written".

### The seven pages

`dev-workflows/docs/reference/session-cost.md` and `session-feedback.md`, `product-workflows/docs/reference/session-cost.md` and `session-feedback.md`, `docs-workflows/docs/reference/session-cost.md`, and `workflows-core/docs/commands/feedback.md` and `prompt.md`. Each listed, exhaustively, when the terminal step does not push, and each failed two of the four cases Task 9 Step 1 tests: a landing pushes the default branch from a branch the list reads as not pushed, and the here form is not pushed while the open run stands, which the list did not name. The held landing and the no-start `end` commit nothing this run, and join the sentence's unstated exceptions (G0, misrooted, a lock). **All seven changed**; each gained three sentences, counted by phrase:

| Phrase | `38aec858` | `25166a8b` |
|---|---|---|
| `Otherwise, where the run's preflight had to stay` (the landing) | 0 | 7, one per page |
| `that branch's next push carries it` (the here form) | 0 | 7, one per page |
| `If you stopped that run and never ended it` (the final review's I1) | 0 | 7, one per page |

`workflows-core`'s two pages ship in 1.84.0, and `dev-workflows` 4.62.4, `product-workflows` 3.79.3 and `docs-workflows` 1.38.3 carry the others.

## The gates and the budgets

The gate chain — the `run:` steps of `.github/workflows/validate-catalog.yml` in order as one `&&` chain, `check-docs.sh --selftest` included — run from the worktree root with this record, the rulings summary and the ledger in place, ending `; echo "EXIT=$?"`, printed `EXIT=0`. Of `check-docs.sh`'s checks, 14 and 19 read this directory — 14 greps the whole repository and 19 every tracked and untracked file — and 13 does not: it reads the plugins and `INSTRUCTION_TIERS` (`CLAUDE.md`, `.claude/rules/*.md`, `docs/maintainers/*.md`; `scripts/check-docs.sh:178`). The three files were grepped by hand for check 13's `VENDOR_TOKENS`, for an internal standard's name, for an email address and for a home-directory path: none.

`len()` of `CLAUDE.md` and of every rules file the branch touched, at the base, at the `main` it merged, and at the tip. Run from the repository root as `python3 -I budgets.py`:

```python
import subprocess
def size(sha, path):  # Python len() of the file's text at that commit, None where it is absent
    shown = subprocess.run(["git", "show", f"{sha}:{path}"], capture_output=True)
    return len(shown.stdout.decode("utf-8")) if shown.returncode == 0 else None
def touched(a, b):
    return subprocess.run(["git", "diff", "--name-only", a, b, "--", "CLAUDE.md", ".claude/rules"],
                          capture_output=True, text=True).stdout.split()
batch, merged = touched("8e441fa0", "25166a8b"), touched("38aec858", "8e441fa0")
for path in sorted(set(batch) | set(merged)):
    print(path, size("38aec858", path), size("8e441fa0", path), size("25166a8b", path),
          "batch" if path in batch else "", "main" if path in merged else "")
```

| File | `38aec858` | `8e441fa0` | `25166a8b` | Changed by | Budget |
|---|---|---|---|---|---|
| `CLAUDE.md` | 34,479 | 34,479 | 34,609 | both | 36,000 |
| `.claude/rules/workflows-core-git.md` | 17,971 | 17,971 | 19,960 | this batch | 20,000 |
| `.claude/rules/workflows-core-read-only.md` | 4,247 | 4,247 | 4,661 | this batch | 20,000 |
| `.claude/rules/release-notes.md` | 10,891 | 10,891 | 11,204 | this batch | 20,000 |
| `.claude/rules/plugin-updates-coupling.md` | 19,174 | 19,605 | 15,752 | both | 20,000 |
| `.claude/rules/plugin-updates-coupling-history-3.md` | absent | absent | 6,855 | this batch | 20,000 |
| `.claude/rules/plugin-updates-coupling-history.md` | 19,271 | 19,271 | 19,360 | both | 20,000 |
| `.claude/rules/plugin-updates.md` | 3,777 | 3,777 | 3,850 | both | 20,000 |
| `.claude/rules/plugin-updates-coupling-history-2.md` | 19,226 | 19,965 | 19,965 | `main` | 20,000 |
| `.claude/rules/dev-workflows-implement.md` | 19,380 | 19,412 | 19,412 | `main` | 20,000 |
| `.claude/rules/security-workflows.md` | 17,318 | 17,356 | 17,356 | `main` | 20,000 |

Every one is under its budget: `CLAUDE.md` under the 36,000-character warning `scripts/validate-catalog.py` sets, every rules file under the 20,000-character one. `CLAUDE.md`, `plugin-updates.md` and `plugin-updates-coupling-history.md` are "both" where `main`'s change kept their length. Task 10 moved the coupling file's bullets for `workflows-core` 1.75.0 to 1.78.13 into the new `plugin-updates-coupling-history-3.md`, by the precedent `history-2` was made by, to make room for the 1.84.0 bullet. `workflows-core-git.md` is the tightest file, 40 characters under its warning: the next addition there must make room first, and GIT-G1 Part 3 will need it.

## The reviews

### The plan

| Round | Of | Verdict | Findings | Answered by |
|---|---|---|---|---|
| Review (Opus) | `e7ecdf73` | NOT READY | 2 Critical, 6 Major, 19 Minor, 7 Nit | the controller's rulings C1, C2, M1–M3, the rest as proposed; revised as `8b58f003` |
| Re-review (Opus) | `8b58f003` | READY WITH CHANGES | 31 of 34 addressed, 3 partly; 4 Major, 14 Minor, 8 Nit new | rulings N1–N4, P26, the prose path's journal, test staging; revised as `7d9f4a5d` |
| Final check (Opus) | `7d9f4a5d` | READY WITH CHANGES | 31 of 33 addressed, 2 partly; 7 Minor, 11 Nit, and 2 items that broke green at Task 3 | rulings F2–F7 and green at every commit; revised as `f2cd5759` |
| Check (Sonnet) | `f2cd5759` | needs fixes | 1 Minor, 4 Nit | fixed by the controller in the plan text, `f22879f8` |

The findings that changed the mechanism, each with the plan's answer (its *Plan review* section holds every answer, the Minor and Nit findings among them):

- **C1, Critical:** the landing's `replay_commits` on `c1` leaked the snapshot's lines into the commit and refused block-shaped files, measured. Answer: `own_change`, a per-path apply onto `<default>`'s version by the file's class (Task 1); no three-way merge, no git ≥ 2.40.
- **C2, Critical:** `update-ref` on a branch another worktree has checked out stages a revert there, measured. Answer: never move such a branch; build on `<default-ref>` and push by refspec, or hold (Task 2).
- **M1, Major:** a run typed mid-run on a branch it would not leave had no form. Answer: the here form, journalled, rechecked between its two steps, finished by `end --resume` or the held stage.
- **M2, Major:** one stuck held entry would strand every later run. Answer: held entries chain only on a shared path; a permanent cause is reported with its commands, never promised to land.
- **M3, Major:** a restored parked record re-protected an abandoned run after its command ran again. Answer: a restored record serves its own end and no longer protects (reversed in part by the user's M1 decision in the final review).
- **M4–M6, Major:** answered as the review proposed; M6 gave `phase-handoff` §6.1 its mid-run stop.
- **N1, Major:** every save of the end path and `declined` wrote `<command>.json` whatever `--started` named. Answer: `run["record_path"]`, the record `--started` selects, written by every save and removal.
- **N2, Major:** G1's *Fix* under a run typed mid-run pasted a switch and a commit of the open run's files. Answer: a mid-run form with an empty *Fix* (G2's too, by F5).
- **N3, Major:** an `end` with no start committed the open run's files. Answer: it runs the open-run test first and commits nothing beside an open run.
- **N4, Major:** P27 lost a hand removal of a branch-only line. Answer: the drop rule — a change that drops a line or entry `<default>` lacks is refused, permanent.
- **F2, final check:** a journal entry lifted after a kill before the move discarded the change. Answer: finished only where the move is verified.
- **F4, final check:** a mid-run end never re-tested the open run. Answer: the end re-tests it, and pushes as usual where it no longer stands.

### The tasks

Each task was reviewed once (Opus, Task 1 to Task 10), each fix round re-reviewed on its own scope, Opus for logic and Sonnet for wording; Minor findings went into the task's own fix round (fix-all). Rounds per task, from the ledger: Task 1, 1; Task 2, a pre-review fix and 2; Task 3, two pre-review fixes and 5, the cap, its last residuals carried to Tasks 6 and 7; Task 4, 1 with an addition; Task 5, a pre-review fix and 3; Task 6, a pre-review fix and 3 with two additions; Task 7, a pre-review fix and 2; Task 8, a pre-review fix and 5, the cap, its last residual carried to the final pass; Task 9, a pre-review fix and 2; Task 9b, a pre-review fix and 3; Task 10, none, its three Minors carried to the final pass. Twelve carried items went to the final fix pass in one written list.

### The final whole-branch review

On Fable 5.2, the user's choice (`claude-fable-5-2` on the first line of each of the four reports), over `8e441fa0..1dbd754f`: 60 commits, 67 files. Verdict: **with fixes**. Three fix passes followed, each with a scoped Fable re-review, under the maintainer's fix-all rule.

| Finding | Severity | What | Fixed in |
|---|---|---|---|
| I1 | Important | An Esc-abandoned run's mid-run stops named no way to end it | `b5b5714c` (SRG, `phase-handoff` §6.1, four templates), `74bfe886` (the seven pages and References); `b5c71e2c` and `cc44cf5f` name the open run's key set in the clause |
| I2 | Important | A session file the open run writes after the typed run's start was taken as the typed run's change: landed and pushed to `<default>` on a stay, with the open run's working copy lifted back to the older version | `b5b5714c`, the guard while the open run stands; widened by `6ab84d51` (ruling (a)) and `5805ea7b` (P1); the residual filed as MIDRUN-LATEWRITE in `ccf9d600` |
| M1 | Minor | The same command typed with another key mid-run still did MIDRUN-B4's harm | the user's decision; `b5b5714c`, `74bfe886` |
| M2 | Minor | A no-start `end` with no `--started` could remove another run's `<command>.json` | `b5b5714c`, a derived path of its own |
| M3 | Minor | SRG §4 step 1 (3)'s no-`origin` sentence read as unconditional | `b5b5714c` |
| M4 | Minor | G1's repeated landing block said "WILL be committed" after the commit | `b5b5714c`, `g1.landing.not_done.landed` |
| M5 | Minor | Selftest gaps: I2, M2, M1, an unnamed resume meeting a restored record | `b5b5714c`; the unnamed-resume edge reproduced and fixed (`unpark` marks the record returned) |
| M6 | Minor | Two cautions on the carry list | `b5b5714c`, `74bfe886` |
| N1 (re-review 1) | Important, narrow | A same-key restart of the open run switched I2's guard off for a run typed under it | `b5c71e2c` (the guard while any other run stands), then `6ab84d51` (ruling (a): on for every run typed mid-run, whatever stands at its end) |
| N2, N3 (re-review 1) | Minor | `protects` statements by keys; a to-test item whose setup fired G1 | `b5c71e2c`, `cc44cf5f` |
| 4(a)–(c) (re-review 1, out of scope) | — | MIDRUN-LATEWRITE's second route, the skill's `replaced` sentence, the key in the I1 clause | `b5c71e2c`, `cc44cf5f`, `f72369d9` |
| P1 (re-review 2) | Important by kind, narrow; predates pass 2 | An untyped run holding a stay landed and rewound a start-dirty whole file a run typed under it rewrote, where it ended last | `5805ea7b`, `25166a8b`: the guard on every landing and here form |
| P2 (re-review 2) | Minor | The append promised a terminal commit the named run does not make | `5805ea7b`: one template, `app.start-dirty-kept`, promising only a later commit on the branch |
| P3 (re-review 2) | Minor | Three behaviours of pass 2 had no selftest | `5805ea7b`: `t_guard_s4_*`, `t_guard_untyped_alone`, `t_guard_here_replay` |
| M1 (re-review 3) | Minor, no population | A record carrying the removed `typed_mid_run` stops an `end` | none needed: only pass 2's unreleased code wrote the field |

The third re-review found every finding addressed and no new Critical or Important breakage.

**The user's two decisions during it** (2026-11-12):
- **M1: protect when keys differ.** A command retyped with a different run key set keeps the first run protected, and the second is typed mid-run under it; the same key set is a restart and ends the protection, as before. "Keys differ" is the two starts' recorded run key sets, order-insensitive; where either recorded none, the retype is a restart. This reversed the plan's ruling M3 in part.
- **The I2 residual: accept, state, and file for Part 3.** A whole file the open run had no change in at the typed run's start, and rewrites before the typed run ends, is in no snapshot, so nothing tells it from the typed run's own; it goes with the typed run's change. Filed as MIDRUN-LATEWRITE, owner GIT-G1 Part 3, whose per-run list of written paths can carry it; SRG §3.5 and §4 step 1 (1) and the rationale state the limit.

**The guard's final rule** (`5805ea7b`, SRG §4 step 1 (1)'s *The guard*): no landing or here form takes a whole-class path — an overwritten file, a record or a register — that was dirty at its run's start, whether or not the run was typed mid-run and whatever stands at its end. It is S1's own attribution applied to whole files: what was dirty at the start is not the run's own. Appended files keep travelling by their added entries alone. Its cost, stated in SRG: a stayed run's own rewrite of such a file is committed later, by a later commit on that branch — into its pull request, where the branch has one — as the leftover itself is. The line that says so is `app.start-dirty-kept`, and it names no run and promises no run's commit.

## Not examined

- **A security register uncommitted at a stayed scan's start, with `--register-rebuild`** (the third final re-review). The guard leaves such a register out of every landing; what the rebuild on `<default>` then does was not traced. It falls under the stated rule, a start-dirty register left for a later commit on the branch, and is a candidate live check.
- **A hold that outlasts a start** (the third final re-review): where a cause keeps a whole file held across the next run's start and that run rewrites the file, the file ends as a leftover on the stayed branch. `l_chain_delete_behind_whole` pins the rule; the persistent cause could not be built cheaply.
- **A read-only bind mount** (Task 9b): the held `.git/config.lock` stood in for it, which fails the same git call; only the error text differs.
- **The 18 to-test items** under `## STAY-2 and MIDRUN-B4 — workflows-core 1.84.0` in `docs/superpowers/to-test-on-real-project.md`: written, with their setups and expected lines, and not run. They are the r4 live round's.
- **The checks with no mutant of their own** in the Done-when table: `e_land_refused`, `e_land_stopped`, `e_land_offline`, `e_land_no_origin`, `t_midrun_keyed_other`, `t_held_journal`, `e_midrun_here_kill` and `e_midrun_here_no_resume`. Each shows in its task's RED run failing before its code; none has a one-line mutant written for it, as the Global Constraints asked of every new check.

## Appendix: the mutants

Each mutant is a one-line change to the new code, applied in a scratch copy, run, and discarded. The tables come from each task's report and from the harness output its report names, at that task's last round; later tasks changed some of these checks, which their own runs show. A check line is cut where its expected-value dump begins, and at 230 characters. Counts: Task 1, 29; Task 2, 65; Task 3, 53; Task 4, 30; Task 5, 50; Task 6, 47; Task 7, 61; Task 8, 58; Task 9, 3; Task 9b, 5; the final passes, 9 — 410 in all, every one killed.

### Task 1 — `own_change` (`session-branch.py`)

From the report's two tables: 23 mutants at `1d57770f`, then 29 after fix round 1 (`63fece66`), every one killed. A row names the check; its failing line is the one the mutant made it print.

| Check | The line that failed under its mutant |
|---|---|
| `oc_lines_snapshot` | `[own_change: oc_lines_snapshot] onto's line, then the run's INNER; c1's OUTER never lands (…)` |
| `oc_lines_branch_only` | `[own_change: oc_lines_branch_only] a branch-only line ticked is refused dropped, onto's tree unchanged (… 'refused': [] …)` |
| `oc_lines_remove_branch_only` | `[own_change: oc_lines_remove_branch_only] a branch-only line removed is refused dropped (…)` |
| `oc_lines_tick_onto` | `[own_change: oc_lines_tick_onto] a line onto holds, ticked, lands as a second copy beside it (… 'refused': [{'reason': 'dropped' …)` |
| `oc_lines_remove_onto` | `[own_change: oc_lines_remove_onto] a line onto holds that the run dropped stays: accepted, onto's file unchanged (…)` |
| `oc_lines_onto_has` | `[own_change: oc_lines_onto_has] a line the run adds that onto already holds is not added twice (…)` |
| `oc_lines_new_file` (2 sub-cases) | `[own_change: oc_lines_new_file] …` and `[own_change: oc_lines_new_file-c1] onto lacks follow-ups.md: the lines c2 adds that c1 lacks (…)` |
| `oc_block_snapshot` | `[own_change: oc_block_snapshot] onto plus the run's R, never c1's S, nothing refused (… 'refused': [{'reason': 'edited' …)` |
| `oc_block_branch_only` (2) | `[own_change: oc_block_branch_only] B edited to B' is refused edited (… 'refused': [] …)` |
| `oc_block_edit_onto` | `[own_change: oc_block_edit_onto] an entry onto holds, edited, is refused edited (…)` |
| `oc_block_new_file` | `[own_change: oc_block_new_file] onto lacks the file: c2's header, then the entries c2 adds (…)` |
| `oc_block_new_file` header-only | `[own_change: oc_block_new_file] a new file of c2's header alone is written as it is (…)` |
| `oc_block_forms` | `[own_change: oc_block_forms] CRLF on onto, LF in c2: refused forms (… 'refused': [] …)` |
| `oc_untracked_leftover` | `[own_change: oc_untracked_leftover] a leftover untracked at the start: only the entries the run appended (…)` |
| `oc_whole` | `[own_change: oc_whole] resume.md is c2's version (…)` |
| `oc_delete` (3) | `[own_change: oc_delete-another] a deletion where onto holds another: refused (… 'refused': [] …)` |
| `oc_partial` | `[own_change: oc_partial] the feedback file lands, follow-ups.md stays onto's and is refused ({'tree': None …)` |
| `oc_register` (stub, none, failing) | `[own_change: oc_register] the run's record added, both register files the stub's over the result (…)` and `… the numbers maps over onto, c2 and the result ({'before_remote': {} …)` |
| `oc_dirs_gone` | `[own_change: oc_dirs_gone] a file added under a specification folder onto lacks is refused folder-gone (…)` |
| `oc_nothing` | `[own_change: oc_nothing] a change onto already holds leaves onto's tree as it is (…)` |
| `oc_old_git` | `[replay: oc_old_git] crashed: NotRun: git merge-tree --write-tree:` |
| `oc_checkout_untouched` (every `oc` call) | `[own_change: oc_checkout_untouched, oc_lines_snapshot] HEAD, the index, git status, every ref and the working copies are as they were` (and every other case) |
| `mb_message` (2) | `[own_change: mb_message] move_branch's message is the reflog's (None, 'session-branch: replayed onto origin/side')` |
| `oc_dirs_gone` (widened) | `[own_change: oc_dirs_gone] a file added, a block file, follow-ups.md and resume.md changed under … (…)` |
| `oc_block_header` | `[own_change: oc_block_header] a header the run changed is refused edited (… 'refused': [] …)` |
| `oc_block_header` (onto's header) | `[own_change: oc_block_header] a header only onto changed stays onto's, the run's entry after it (… 'refused': [{'reason': 'edited' …)` |
| `oc_lines_forms` | `[own_change: oc_lines_forms] follow-ups.md CRLF on onto, LF in c2: refused forms (… 'refused': [] …)` |
| `oc_final_line_ending` | `[own_change: oc_final_line_ending] a block file: onto's last line completed, an empty line, the run's entry (…)` |
| `oc_final_line_ending-lines` | `[own_change: oc_final_line_ending-lines] follow-ups.md: onto's last line completed, then the run's line (…)` |

### Task 2 — the landing (`scenarios_land`)

The harness's last run, after fix round 1's addition (`df9f6cba`): one mutant per check, keyed by the check it must fail, 65 killed, none survived.

| Mutant | The check line that failed |
|---|---|
| `l_land_unkeyed` | `l_land_unkeyed: both paths lifted, the checkout clean` |
| `l_land_snapshot` | `l_land_snapshot: main's commit adds only the run's line, the working copy S after the lift` |
| `l_land_snapshot_deleted` | `l_land_snapshot_deleted: a deletion standing at the start is not the run's: it neither lands nor is put back` |
| `l_land_no_snapshot` | `l_land_no_snapshot: with no snapshot every dirty session file lands, the leftover included` |
| `l_land_behind` | `l_land_behind: built on origin/main, local main fast-forwarded to it` |
| `l_land_absent` | `l_land_absent: no local main: created at the landed commit, on origin/main` |
| `l_land_behind_checked_out` | `l_land_behind_checked_out: pushed by refspec on origin/main, local main unmoved` |
| `l_land_checked_out_no_push` | `l_land_checked_out_no_push: l-co-refused held, refused-before, local main unmoved, the file dirty` |
| `l_land_diverged` | `l_land_diverged: landed on top of the user's unpushed commit` |
| `l_land_nothing` | `l_land_nothing: nothing dirty, nothing landed` |
| `l_land_there` | `l_land_there: the run's line already on main: no commit, the file lifted` |
| `l_land_there_refused` | `l_land_there_refused: no commit, the path already there lifted, the other held, permanent` |
| `l_land_hook` | `l_land_hook crashed: NotRun: git hook run:` |
| `l_land_on_move` | `l_land_on_move: called before the move, the journal entry written; none left after` |
| `l_land_partial` | `l_land_partial: the feedback file lands, the cost file held alone, permanent, unlifted` |
| `l_land_locked` | `l_land_locked: index.lock → locked, no ref moved, nothing held` |
| `l_land_old_git` | `l_land_old_git crashed: NotRun: git merge-tree --write-tree:` |
| `l_land_moved` | `l_land_moved: refused twice, held, moved, transient` |
| `l_held_chain` | `l_held_chain: both landed in order, each line once, the working copy HEAD's` |
| `l_held_unrelated` | `l_held_unrelated: a transient entry on A holds back no landing on B` |
| `l_held_then_own` | `l_held_then_own: the held entry lands first, then the run's own, the file lifted to the entry's c1` |
| `l_held_then_own_there` | `l_held_then_own_there: the entry lands, the own change is there, the file lifted to HEAD's` |
| `l_retry_local_only` | `l_retry_local_only: retry_remote=False leaves the entry, the own change held behind it` |
| `l_retry_budget` | `l_retry_budget: the first landed, the second kept, _Stop propagated` |
| `l_retry_held_edited` | `l_retry_held_edited: a held file edited since leaves the entry, rebuilt without it` |
| `l_retry_held_on_default` | `l_retry_held_on_default: HEAD on main drops the entry, its file left` |
| `l_retry_held_journal` | `l_retry_held_journal: main holds the tip: lifted only` |
| `l_retry_held_journal_before_move` | `l_retry_held_journal_before_move: landed again, main moved once, lifted after` |
| `l_held_rebuild` | `l_held_rebuild: rebuilt without the path, its lift override with it` |
| `l_held_drop` | `l_held_drop: --drop-held removes the entry and its ref, the file untouched` |
| `l_held_orphan_refs` | `l_held_orphan_refs: the unlisted ref over an hour old removed; w2's, one younger than an hour, and one written while the records were read, all kept` |
| `l_land_here` | `l_land_here: the index restored, S's line alone left, no file written, no journal` |
| `l_land_here_refused` | `l_land_here_refused: a refusal keeps the whole change, nothing moved, no journal` |
| `l_land_here_recheck` | `l_land_here_recheck: a lock after the move raises with pending.here, the journal kept` |
| `l_retry_held_here` | `l_retry_held_here: the index restored from index_before, a new file included` |
| `l_retry_held_here_old` | `l_retry_held_here_old: the here form again, one commit` |
| `l_retry_held_here_elsewhere` | `l_retry_held_here_elsewhere: main at neither: dropped, the files untouched` |
| `l_retry_held_here_ancestor` | `l_retry_held_here_ancestor: the tip an ancestor: the index restored, finished` |
| `l_land_resume` | `l_land_resume: the pending landed again, alone, its journal entry never a held one` |
| `l_land_register` | `l_land_register: moves as sb._moves gives them` |
| `l_cli_land` | `l_cli_land: --commit-key opens the subject` |
| `l_cli_exit2` | `l_cli_exit2: --branch naming a branch HEAD is not on exits 2 with one line, nothing changed` |
| `l_sb_reused` | `l_sb_reused: specs-git.py imports session-branch.py's functions, defining none` |
| `t_rerun_blocked_midnight` | `t_rerun_blocked_midnight: G0 first` |
| `l_chain_partly_stopped` | `l_chain_partly_stopped: E1 landed, E2 kept with its lift where the chain began` |
| `l_chain_partly_stopped` | `l_chain_partly_stopped: E1 landed, E2 kept with its lift where the chain began` |
| `l_chain_partly_own` | `l_chain_partly_own: E1 landed, the own change held with its lift where the chain began` |
| `l_chain_delete_behind_whole` | `l_chain_delete_behind_whole: E1 landed, the deletion held with its lift at v0` |
| `l_chain_delete_behind_whole` | `l_chain_delete_behind_whole: the deletion lands, the working copy back at v0` |
| `l_chain_lift_pruned` | `l_chain_lift_pruned crashed: LandStopped: git write-tree: error: invalid object 100644 0000000000000000000000000000000000000001 for 'specifications/PRD-ACME-1-x/follow-ups.md'` |
| `l_held_rebuild` | `l_held_rebuild: rebuilt without the path, its lift override with it` |
| `l_cli_detail` | `l_cli_detail: a checked-out hold prints the refspec push's outcome as detail` |
| `t_rerun_blocked_midnight_during` | `t_rerun_blocked_midnight_during: G0 first` |
| `l_split_collision` | `l_split_collision: the stuck entry reported stands in the record with its ref` |
| `l_chain_committed_land` | `l_chain_committed_land: P8 drops the committed entry in land's step 3 as retry_held does: main holds the later change alone, the working copy HEAD's` |
| `l_chain_committed_retry` | `l_chain_committed_retry: land's P8 drops the committed entry, the later change is held alone and retry_held lands it alone, the working copy HEAD's` |
| `l_land_pending_own` | `l_land_pending_own: LandStopped carries no held entry's pending; that journal stays in its record` |
| `l_land_resume_chain` | `l_land_resume_chain: the resumed change is the oldest of the chain it starts, the file lifted to HEAD's` |
| `l_retry_held_here_staged` | `l_retry_held_here_staged: a path the user staged after the kill stays as they staged it, the rest restored` |
| `l_retry_held_blocked` | `l_retry_held_blocked: the blocked entry reports, and records, the refusal it waits on` |
| `l_held_orphan_refs` | `l_held_orphan_refs: on a detached HEAD nothing is done, the orphan sweep included (P9)` |
| `l_held_orphan_refs` | `l_held_orphan_refs: the unlisted ref over an hour old removed; w2's, one younger than an hour, and one written while the records were read, all kept` |
| `l_held_orphan_refs` | `l_held_orphan_refs: the unlisted ref over an hour old removed; w2's, one younger than an hour, and one written while the records were read, all kept` |
| `l_cli_retry_partial` | `l_cli_retry_partial: the landing made before the error is reported with it` |
| `l_chain_committed_land` | `l_chain_committed_land: P8 drops the committed entry in land's step 3 as retry_held does: main holds the later change alone, the working copy HEAD's` |

### Task 3 — SRG's wording and its pins (`scenarios_lines`, `scenarios_skill`)

From the report, round by round: 13 mutants at `d30a6cf8`, 11 at the first pre-review fix (`5d61cd6b`), 7 at the second (`64723eb3`), 11 in fix round 1 (`53750a82`), 2 new in round 2 with rm2 and rm7 run again (`7d1cf023`), 4 in round 3 (`27d138ba`), 2 in round 4 and 1 in its addition (`a84623f2`, `db0bfb27`) and 2 in round 5 (`ffd284a7`), 53 in all, every one killed.

| Mutant | Change | The check that failed |
|---|---|---|
| m1 | `pins()` skips every id | `l_retiring: an id outside RETIRING missing from SRG is still reported` |
| m2 | `here` dropped from `ROWS` | `l_ids: 30 rows in §6's order…` |
| m3 | `locked` dropped from `LAND_REASONS` | `l_ids: LAND_REASONS maps every refusal code…` |
| m4 | `dropped` mapped to `reason.dropped` | `l_ids: every code of LAND_REASONS maps to a reason.land.* template…` |
| m5 | `STAY_KINDS`' first two swapped | `l_constants: STAY_KINDS is the order of the <which no key ...> alternation…` |
| m6 | `SG_SCRIPT = SB_SCRIPT` | `l_constants: STAY_REASONS gains mid-run last, and SG_SCRIPT is this script's path` |
| m7 | G1's *Not done* opening back to the old sentence | `l_g1_not_done` |
| m8 | `app.landed`'s first two alternatives swapped | `l_fill_landing: placeholder: app.landed has 0 placeholders beginning '<which no key'` |
| m8b | `app.landed`'s alternative 0 reworded | `l_fill_landing: app.landed by the stay's kind…` |
| m9 | `pre.held.stuck`'s first command's opening quote removed | `l_fill_landing: pre.held.stuck names both commands, each quoted whole` |
| m10 | `row.here`'s `(<N> files)` made `(<N> file(s))` | `l_fill_landing: row.here singular at one…` |
| m11 | the mid-run stop dropped from `phase-handoff` §6.1 | `k_branch_check_midrun, both checks` |
| m12 | `row.held`'s "without leaving it" dropped | `l_fill_landing: row.held with reason.land.checked-out's failed push` |
| pm1 | `detail`'s `outcome` dropped | `l_checked_out_detail (every alternative), l_cli_detail` |
| pm2 | `failed`'s `text` dropped | `l_checked_out_detail: l-cod-failed… (no value for <reason>), l_cli_detail` |
| pm3 | `rejected`'s `text` dropped | `l_checked_out_detail: l-cod-rejected…` |
| pm4 | `refused`'s `text` dropped | `l_checked_out_detail: l-cod-refused…` |
| pm5 | `refused`'s `record` dropped | `l_checked_out_detail: l-cod-refused…` |
| pm6 | `elsewhere`'s `remote` dropped | `l_checked_out_detail: l-cod-elsewhere… (no value for <remote>)` |
| pm7 | `refused-before`'s `date` dropped | `l_checked_out_detail: refused-before…` |
| pm8 | `refused-before`'s `record` dropped | `l_checked_out_detail: refused-before…` |
| pm9 | the `no status line` fallback dropped | `l_checked_out_detail: a failed push with no reason…` |
| pm10 | `rejected` mapped to alternative 1 | `l_checked_out_detail: l-cod-rejected…` |
| pm11 | the CLI's `detail` dropped | `l_cli_detail` |
| qm1 | `record_error` not carried | `l_checked_out_detail (the report names the check, not its line)` |
| qm2 | the unrecorded selection dropped | `l_checked_out_detail (as qm1)` |
| qm3 | `refused-before` back to alternative 4 | `l_checked_out_detail (as qm1)` |
| qm4 | `<date>` not filled | `l_checked_out_detail (as qm1)` |
| qm5 | `<record>` not filled | `l_checked_out_detail (as qm1)` |
| qm6 | `<error>` not filled | `l_checked_out_detail (as qm1)` |
| qm7 | the `[remote rejected]` fallback dropped | `the 20-shape check: fill: no value for <the refusal>` |
| rm1 | the CLI's `retry_remote=True` | `l_cli_local_retries (landed, pushed)` |
| rm2 | `unfinished` made `moved` | `l_here_resume_unfinished` |
| rm3 | *It does*'s stop dropped from §6.1 | `k_branch_check_midrun` |
| rm4 | *It does not*'s stop dropped from §6.1 | `k_branch_check_midrun` |
| rm5 | *It does*'s stop dropped from the part file | `k_branch_check_midrun` |
| rm6 | `pre.here.finished`'s count made `(1 file(s))` | `l_fill_landing: pre.here.finished` |
| rm7 | `unfinished` unmapped | `the l_ids coverage check, and l_here_resume_unfinished` |
| rm8 | `row.held`'s tails swapped | `l_fill_landing (the tail placeholder no longer found), and l_pins` |
| rm9 | `pre.held.failed`'s tails swapped | `l_fill_landing, and l_pins` |
| rm10 | `mode_takes` ignoring the record | `l_checked_out_detail: mode_takes …` |
| rm11 | G1's *Not done* back to "committed and pushed" | `l_g1_not_done` |
| sm1 | `reason.land.unfinished` back to its round-1 text in `T` | `l_pins and its bites, l_retiring's outside-id check, l_fill_landing: the mid-run row …, l_here_resume_unfinished` |
| sm2 | the refusal's `permanent` made `False` | `l_here_resume_unfinished` |
| tm1 | the not-landed *Not done* promising "WILL be committed" | `l_fill_landing: g1.landing.not_done.unlanded …` |
| tm2 | its kinds' alternatives swapped | `l_constants, and l_fill_landing` |
| tm3 | `g1.landing.if_ignored` back to its old text | `l_fill_landing: the landing, merged and mid-run If ignored lines are true whatever the outcome, and l_pins` |
| tm4 | `g1.midrun.if_ignored` back to its old text | `the same check as tm3, and l_pins` |
| um1 | the pin's tail back to "the line above says what came of that.", SRG unchanged | `l_fill_landing, l_pins with its bites, l_retiring's outside-id check` |
| um2 | SRG and the pin both back to "the line above says what came of them." | `l_fill_landing alone` |
| um3 | SRG and the pin both back to "this run's artifacts go where the line above says." | `l_fill_landing: g2.midrun.if_ignored names the run's Specs repo: line` |
| um4 | SRG and the pin both take a no-preflight wording | `l_fill_landing: the mid-run row with reason.land.no-snapshot, true for both causes` |
| um5 | the template dropped from `T` | `l_ids: every id the interface names is a template (missing ['reason.land.no-snapshot']), and l_fill_landing` |

### Task 4 — the snapshot and every stay (`scenarios_start`, `scenarios_state`)

The harness's last run, at `fa81bbb6`: 30 mutants, each killed by its own check.

| Mutant | The check line that failed |
|---|---|
| `m00` | `t_snap_g1: the snapshot names the session file, its blob written` |
| `m01` | `t_snap_narrowed: the flushed session file narrowed out of the snapshot` |
| `m02` | `t_snap_misrooted: no snapshot, no object written` |
| `m03` | `t_snap_status_failed: no snapshot, pre.status-failed reported once and recorded` |
| `m04` | `t_snap_rerun: the re-run carries the first start's snapshot, and only that` |
| `m05` | `t_snap_rerun: the re-run carries the first start's snapshot, and only that` |
| `m06` | `t_stay_g1_unkeyed: G1's landing form, the stay kept, the plain block saved` |
| `m07` | `t_stay_g1_keyed: G1's plain block, no stay` |
| `m08` | `t_stay_g1_commit_key: no stay` |
| `m09` | `t_stay_keys_none: _stay_kind's kinds, and no None reaching branch_key` |
| `m10` | `t_stay_g1_merged: the landing form, merged's alternative` |
| `m11` | `t_stay_g1_merged: the landing form, merged's alternative` |
| `m12` | `l_fix_lines: g1.landing.merged's Fix part runs whole through bash -c, making its git calls (rc 0, ['-C\|/tmp/tmp9269yzqh/a specs repo\|status\|', '-C\|/tmp/tmp9269yzqh/a specs repo\|add\|my notes.md\|n.md\|', '-C\|/tmp/tmp9269yzqh/a specs…` |
| `m13` | `t_stay_unlisted_b4: pre.stay.unlisted's B4 alternative, the stay kept` |
| `m14` | `t_stay_b4_refused: Locked, B4's switch refused, pre.stopped, the stay kept` |
| `m15` | `t_stay_stopped: the early stop keeps the stay` |
| `m16` | `t_stay_cleared: the re-run's B4 leaves the branch, and the stay it kept goes with it` |
| `m17` | `t_start_json: stay, start_dirty, midrun and started on every call` |
| `m18` | `t_d5_g1: G1's landing form printed, the stay recorded, the plain block saved` |
| `m19` | `t_d5_budget: end skips on the branch the start did not leave` |
| `m20` | `m_no_stay: the plain block, no stay, no snapshot, no object written` |
| `m21` | `m_no_stay: the plain block, no stay, no snapshot, no object written` |
| `m22` | `s_fields: stay, start_dirty, midrun null and protects true in FIELDS, merged_stay not` |
| `m23` | `s_legacy_merged_stay: merged_stay set loads with stay {'branch': 'prd/A-1-x', 'kind': 'merged', 'reason': 'g1', 'merged': True, 'command': None} and every new field at its default` |
| `m24` | `s_legacy_merged_stay: merged_stay set loads with stay {'branch': 'prd/A-1-x', 'kind': 'merged', 'reason': 'g1', 'merged': True, 'command': None} and every new field at its default` |
| `m25` | `t_snap_rerun_unset: the carried snapshot is not narrowed against another repository` |
| `m26` | `t_stay_b4_commit_key: the commit key names the branch, so B4 does not leave it` |
| `m27` | `t_snap_bug: the TypeError surfaces as the start's error` |
| `m28` | `t_rerun_commit_key: the re-run switches back to the branch its commit key names` |
| `m29` | `k_skill_fields: Start names stay, which an end run by hand reads (§3.3), and merged_stay nowhere` |

### Task 5 — the end's landing (`scenarios_end`, `scenarios_land`, `scenarios_lines`)

The harness's last run, after fix round 3 (`72a928c7`): 50 mutants, every one killed.

| Mutant | The check line that failed |
|---|---|
| `m00` | `e_land_g1: landed on main, alternative 0, then G1's landing form; the checkout and the branch unmoved, the file lifted` |
| `m01` | `e_land_moved: committed on the branch HEAD moved to, the plain block` |
| `m02` | `e_land_merged: alternative 1, lifted, the branch still merged` |
| `m03` | `e_land_kill_before_move: end --resume lands once, then lifts` |
| `m04` | `e_land_hand_edit: follow-ups.md held alone (dropped), the tick kept, main's unchanged` |
| `m05` | `e_land_commit_key_midrun: the mid-run stay dropped, nothing landed on main` |
| `m06` | `e_land_locked_held: held for the lock, one transient entry, nothing committed` |
| `m07` | `l_land_locked: an index.lock at the landing's start holds the change for that cause, transient: no branch moved, nothing lifted` |
| `m08` | `e_g1_uncommitted: after locked, the not-committed Not done` |
| `m09` | `l_g1_end: no stay -- the plain block where the end committed; where it did not, the not-committed form, its Not done and If ignored, the Fix the plain block's` |
| `m10` | `e_land_held: the held row, the files kept, one held entry` |
| `m11` | `e_land_partial: the feedback file landed, the cost file held alone` |
| `m12` | `e_land_budget: the unfinished start's branch takes the landing` |
| `m13` | `e_land_unlisted: the leftover lands too, and app.landed.unlisted says so` |
| `m14` | `e_land_legacy: the legacy stay lands against HEAD, no unlisted clause` |
| `m15` | `e_land_register: the register clause after app.landed` |
| `m16` | `e_land_partial: the feedback file landed, the cost file held alone` |
| `m17` | `e_land_held: the held row, the files kept, one held entry` |
| `m18` | `e_land_stuck: held stuck, reason edited, both commands quoted whole` |
| `m19` | `e_land_checked_out_pushed: pushed by refspec, local main and w2 untouched` |
| `m20` | `e_land_kill: end --resume lifts and pushes the same commit, main moved once` |
| `m21` | `e_land_kill_stuck: resumed, the path held alone still named` |
| `m22` | `e_land_kill_refspec: resumed, the refspec push verified on origin's main, its row at once` |
| `m23` | `e_land_locked: a verified journal is not lifted under the lock either` |
| `m24` | `e_land_nonff: replayed and pushed, main moved by update-ref, HEAD on the stayed branch` |
| `m25` | `e_land_mode: the mode's outcome, nothing landed` |
| `m26` | `e_land_not_finished: NOT FINISHED, then the not-landed form` |
| `m27` | `t_land_merged_g1: end lands the run's file on main, the checkout unmoved, the landing form whole` |
| `m28` | `e_land_leftover_kept: the leftover stays out of main, unchanged` |
| `m29` | `e_land_commit_key: the stay dropped, committed on the branch, the plain block` |
| `m30` | `t_two_commands: /specify's end repeats the block its own start saved, in the form for an end that committed nothing` |
| `m31` | `e_land_kill_before_move: the journal written and saved, nothing moved` |
| `m32` | `l_land_locked: a resumed journal under the lock is left for a later call` |
| `m33` | `l_pins_all: a landing row missing from SRG is reported` |
| `m34` | `e_land_kill_register: the journal saved through on_move carries the moves` |
| `m35` | `e_land_kill_register: the resumed line carries the register clause the uninterrupted end prints` |
| `m36` | `l_land_on_move: called before the move, the journal entry written; none left after` |
| `m37` | `e_land_unsupported: the held row takes no unsupported clause` |
| `m38` | `e_land_unsupported: the nothing row keeps the unsupported clause` |
| `m39` | `e_land_resume_moved: HEAD on main, the journal dropped, committed where HEAD stands` |
| `m40` | `e_land_resume_moved: a status with no landing row raises, never prints its id` |
| `m41` | `l_land_resume_on_default: refused, nothing done` |
| `m42` | `e_land_origin_lacks_default: landed on local main, its row from push_check` |
| `m43` | `e_land_origin_lacks_default: landed on local main, its row from push_check` |
| `m44` | `e_g1_uncommitted: after locked, the not-committed Not done` |
| `m45` | `l_g1_end: no stay -- the plain block where the end committed; where it did not, the not-committed form, its Not done and If ignored, the Fix the plain block's` |
| `m46` | `l_g1_end: a block with no Not done part is refused, never rendered unchanged` |
| `m47` | `e_land_held_mode_takes: alternative 4, the session-branch tail` |
| `m48` | `e_land_origin_lacks_checked_out: held stuck, nothing pushed -- origin's refs unchanged, local main unmoved -- and one held entry (row 'pushed-default', origin unchanged False, 0 held, ['Specs repo: committed c9ae1d0` |
| `m49` | `l_checked_out_detail: l-cod-origin-lacks's detail kept in the held record, and its clause worded whole` |

### Task 6 — the held stage (`scenarios_end`, `scenarios_start`)

The harness's last run, after fix round 3 (`b1d2350a`): 47 mutants, every one killed.

| Mutant | The check line that failed |
|---|---|
| `m00` | `t_held_flush_excludes: the flush commits LEFT alone, FB held` |
| `m01` | `e_land_locked_held: the retry fails on the lock, and the flush commits the run's other file and leaves the held one out` |
| `m02` | `t_held_changed: FB committed on HEAD with pre.held.changed, the entry rebuilt without it` |
| `m03` | `t_held_journal_before_move: landed again, main moved once, then lifted` |
| `m04` | `t_held_then_own_across_start: the end lands d alone, the file left at a+b` |
| `m05` | `t_held_here_finished: the here form run again, its line before G1's block` |
| `m06` | `e_land_resume_dropped_excludes: the journal dropped, FB committed where HEAD stands, the stuck cost edit left out` |
| `m07` | `e_end_excludes_held: end commits FB on the branch, the held cost edit left out` |
| `m08` | `e_end_on_default_drops: the entry dropped, its file committed with the run's on main` |
| `m09` | `t_held_retry: landed on main before G1's block, main pushed, lifted, the entry gone` |
| `m10` | `t_held_retry: landed on main before G1's block, main pushed, lifted, the entry gone` |
| `m11` | `t_held_retry_fails: pre.held.failed naming main before G1's block, the entry kept` |
| `m12` | `t_held_stuck_reported: the stuck line on every start, the next run's own file landed` |
| `m13` | `t_held_on_default: dropped silently, the flush commits the file on main` |
| `m14` | `t_held_mode: the entry and its ref dropped, the file left` |
| `m15` | `t_held_misrooted: nothing done under misrooted` |
| `m16` | `t_default_push_g1: main pushed before G1's block` |
| `m17` | `t_default_push_g1: in session-branch mode, no push of main` |
| `m18` | `t_default_push_nonff: replayed by update-ref, pushed, then the guards` |
| `m19` | `e_land_unpushed_retry: main pushed by the held stage while G1 fires` |
| `m20` | `t_held_resume: one entry per call, G1's block once` |
| `m21` | `t_held_resume: one entry per call, G1's block once` |
| `m22` | `t_held_changed: FB committed on HEAD with pre.held.changed, the entry rebuilt without it` |
| `m23` | `t_held_changed: FB committed on HEAD with pre.held.changed, the entry rebuilt without it` |
| `m24` | `t_held_here_finished: the here form run again, its line before G1's block` |
| `m25` | `l_retry_held_journal: main holds the tip: lifted only` |
| `m26` | `l_retry_held_here: the index restored from index_before, a new file included` |
| `m27` | `t_flush_order: origin-lacks stops the push before push-scope is measured, silently` |
| `m28` | `t_merged_unknown: at --budget 0 each report once across the calls` |
| `m29` | `t_held_locked: nothing landed or lifted under the lock, the entry kept` |
| `m30` | `e_land_locked_held: the retry fails on the lock, and the flush commits the run's other file and leaves the held one out` |
| `m31` | `t_held_locked: nothing landed or lifted under the lock, the entry kept` |
| `m32` | `t_held_locked_stuck: the permanent entry reported stuck and kept` |
| `m33` | `t_held_locked_default: dropped under the lock, the flush commits the file on main` |
| `m34` | `t_held_locked_mode: dropped under the lock, the session branch takes the file` |
| `m35` | `t_held_resume_failed: one entry per call, each failed line once, the chain ends` |
| `m36` | `t_held_resume_failed: one entry per call, each failed line once, the chain ends` |
| `m37` | `t_held_locked_journal: no line under the lock, the lift waits, the flush leaves FB out` |
| `m38` | `t_held_locked_changed: FB committed, the entry rebuilt after the commit` |
| `m39` | `e_end_changed_resume: the resume prints the line once and rebuilds the entry` |
| `m40` | `t_held_resume_stuck: T lands on the resume, S kept and holding nothing back` |
| `m41` | `e_end_changed_resume_push: the resume prints the line once, the entry rebuilt` |
| `m42` | `e_end_changed_resume_twice: the second resume prints the line once and rebuilds` |
| `m43` | `e_end_changed_shown: shown once, a later resume does not repeat it` |
| `m44` | `e_end_changed_shown: shown once, a later resume does not repeat it` |
| `m45` | `t_held_resume_rebuilt: the rebuilt entry not retried, its line not printed again` |
| `m46` | `e_end_changed_signal: a signal's stop marks nothing shown; the resume prints the line once` |

### Task 7 — a run typed mid-run (`scenarios_midrun`, `scenarios_state`)

The harness's run at the task's end, after fix round 2 (`3a0ce918`): 61 mutants, every one killed. Task 8 re-ran it at each of its rounds, 61 killed each time, two mutant strings repaired for drift (s1, i3).

| Mutant | The check line that failed |
|---|---|
| `s1` | `s_save_at: save(at=) writes that file and load(at=) reads it, <name>.json untouched` |
| `s2` | `s_others: the other commands' records, a parked one among them, oldest first` |
| `s3` | `s_park_unpark: the newest parked one restored, protects false` |
| `s7` | `t_park_abandoned_middle: the oldest parked record protects nothing` |
| `s4` | `s_park_unpark: the newest parked one restored, protects false` |
| `s5` | `t_derived_not_parked: the derived record untouched, the parked one restored` |
| `s6` | `t_started_not_found: both calls on the derived path, the third's record byte for byte, nothing committed` |
| `m1` | `t-midrun-keyless: no commit on the branch, HEAD unmoved, pre.stay.midrun naming /specify, a mid-run stay` |
| `m2` | `t-midrun-keyless: no commit on the branch, HEAD unmoved, pre.stay.midrun naming /specify, a mid-run stay` |
| `m3` | `t_midrun_catch_up: no pull at the start or the end` |
| `m4` | `t_midrun_g2: G2's mid-run form, its Fix empty, at the start and at the end; the here row's second alternative` |
| `m5` | `t_stay_merged_midrun: kind mid-run, merged, the mid-run form whatever the flag` |
| `m6` | `t_midrun_same_command: the second start parks the first, and is not typed mid-run` |
| `i1` | `t_midrun_rerun: a re-run under a run started since its first start switches back as any B4 re-run, and its end has no mid-run wording` |
| `i2` | `t_midrun_rerun: t-midrun-rerun-ended -- the re-run tests its first start's open run again` |
| `i3` | `t_midrun_rerun: t-midrun-rerun-standing -- the re-run tests its first start's open run again` |
| `h1` | `t_midrun_handoff_moved: HEAD moved by the run's own handoff -- steps 2-4, as worded` |
| `p1` | `t_park_rerun: the re-run's record parked under its own stamp, every next carrying --started, <command>.json byte for byte` |
| `p2` | `t_park_rerun: the re-run's record parked under its own stamp, every next carrying --started, <command>.json byte for byte` |
| `p3` | `t_resume_stale_no_park: a resume run fresh replaces its own record, parking none` |
| `R1` | `e_midrun_kept_b3: the refused clause names HEAD's branch` |
| `R5` | `e_midrun_kept_ended_catch_up: the catch-up, then the push, no replay` |
| `R2` | `e_no_preflight_named: the record --started names is no open run beside itself` |
| `q1` | `t_park_rerun_replays: t-park-rerun-flush -- each next repeats --started, the chain ends at done on the re-run's own record, the second's untouched` |
| `q2` | `t_park_rerun_replays: t-park-rerun-held -- each next repeats --started, the chain ends at done on the re-run's own record, the second's untouched` |
| `q3` | `t_park_rerun_replays: t-park-rerun-settle -- each next repeats --started, the chain ends at done on the re-run's own record, the second's untouched` |
| `q4` | `t_park_rerun_replays: t-park-rerun-flush -- each next repeats --started, the chain ends at done on the re-run's own record, the second's untouched` |
| `n1` | `t_midrun_rerun_no_record: no record of its own, so the open runs read as a first start reads them, no snapshot taken` |
| `c1` | `t_midrun_not_open: end_commit -- not open, B4 switches as before` |
| `c2` | `t_midrun_not_open: stage end -- not open, B4 switches as before` |
| `c3` | `t_midrun_not_open: declined only -- not open, B4 switches as before` |
| `c4` | `t_midrun_not_open: misrooted -- not open, B4 switches as before` |
| `c5` | `t_midrun_not_open: another top -- not open, B4 switches as before` |
| `c6` | `t_midrun_not_open: protects false -- not open, B4 switches as before` |
| `c7` | `t_midrun_not_open: 8 days -- not open, B4 switches as before` |
| `c8` | `t_midrun_not_open: another branch -- not open, B4 switches as before` |
| `r1` | `t_midrun_left_returned: away and back since the start -- not mid-run` |
| `r2` | `t_midrun_left_before: away and back before the start -- still mid-run` |
| `r3` | `t_midrun_handoff_open: the open run's handoff onto its own branch -- still mid-run` |
| `r4` | `t_midrun_noop_move: a move to the branch itself` |
| `r5` | `t_park_dropped: a leave of its branch since its start drops the parked record` |
| `e1` | `e_no_start_midrun: kind missing -- the mid-run row with no-preflight, nothing written` |
| `e2` | `e-midrun-ended-dropped: only /feedback's change, pushed, no mid-run wording` |
| `e3` | `t_midrun_default: one commit on main holding /feedback's line and file alone, unpushed, the index in step, /specify's line still dirty` |
| `e4` | `e-midrun-no-snapshot-ended-status-lb: the open run no longer stands -- the change taken against HEAD, every session file with it` |
| `e5` | `e-midrun-no-snapshot-status-lb: nothing committed while the open run stands, the open run's file still dirty` |
| `e6` | `e_midrun_here_kill_moved: a kill right after the move is finished by end --resume` |
| `e7` | `e_midrun_here_resume_elsewhere: the journal dropped, no second commit on main` |
| `e8` | `e_midrun_here_unfinished: the open run ended, the end goes on from step 1` |
| `e9` | `e_midrun_kept: once the open run no longer stands, steps 2-4 commit on HEAD's branch` |
| `e10` | `e_midrun_kept: the mid-run row with the refused path's clause, nothing committed or held, the not-committed mid-run form` |
| `e11` | `e_midrun_unlanded: after nothing, the mid-run form with the not-landed Not done` |
| `e12` | `t-park-out-of-order: the first run ends on its own parked record, the second's byte for byte` |
| `e13` | `t-park-out-of-order-landing: the first run ends on its own parked record, the second's byte for byte` |
| `e14` | `t_midrun_g2: G2's mid-run form, its Fix empty, at the start and at the end; the here row's second alternative` |
| `e15` | `t_started_not_found: both calls on the derived path, the third's record byte for byte, nothing committed` |
| `e16` | `t_midrun_g2: G2's mid-run form, its Fix empty, at the start and at the end; the here row's second alternative` |
| `e17` | `t_midrun_mode_catch_up: no pull at the start or the end in the mode` |
| `e18` | `t_park_replay: the replay names --started and ends on the parked record` |
| `e19` | `e_no_start_midrun: kinds ignored and declined-only alike, nothing removed` |
| `e20` | `t_started_missing_end: saved and removed at the derived path, its started the stamp` |

### Task 8 — the skill, and the record's identity it found (`scenarios_skill`, `scenarios_midrun`, `scenarios_state`)

The harness's last run, after fix round 5 (`18a94cea`): 58 mutants, every one killed.

| Mutant | The check line that failed |
|---|---|
| `o1` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `o2` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `o3` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `o4` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `o5` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `f1` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f2` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f3` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f4` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f5` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f6` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f7` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `f8` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `c1` | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `c2` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `r1` | `s_find_before: <name>.json by a stamp its started_before lists, the newest of two listing one, a parked one by its started` |
| `r1e` | `t_rerun_stopped: start --resume --started <the earlier stamp> goes on with the re-run's record, <command>.json the one record` |
| `r2` | `s_left_behind: unpark restores the re-run's record, never the file it left behind` |
| `r3` | `s_left_behind: removing the record that lists it removes the file left behind` |
| `r3e` | `t_rerun_cut_off: the earlier stamp names the re-run's record, the file left behind is never listed, restored or left after the end` |
| `r4` | `t_rerun_stopped: start --resume --started <the earlier stamp> goes on with the re-run's record, <command>.json the one record` |
| `r5` | `t_rerun_old_stamp_end: after a start --resume --started that starts afresh, setting nothing aside, the earlier stamp still names the run's record` |
| `r6` | `s_find_before: <name>.json by a stamp its started_before lists, the newest of two listing one, a parked one by its started` |
| `r7` | `s_find_before: another run's <name>.json is never named` |
| `m1` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `m3` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `m4` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `m5` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `p1` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `x1` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `x2` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `x3` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `x4` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `q4` | `t_rerun_old_stamp_end: after a start --resume --started that starts afresh, setting nothing aside, the earlier stamp still names the run's record` |
| `q5` | `t_midrun_open_rerun: after the open run's re-run, the run typed under it still reads it as standing -- the here row, nothing pushed` |
| `q6` | `s_left_behind: a save of another run's record over the one that lists it removes the file left behind, a third run's parked record and its own kept` |
| `q6e` | `t_rerun_cut_off_overwritten: the third start's save over the re-run's record takes the file left behind with it, and its end restores nothing` |
| `q6b` | `s_left_behind: a save of another run's record over the one that lists it removes the file left behind, a third run's parked record and its own kept` |
| `x5` | `k_skill_fallback: the fallback reads the stay, the snapshot and the open run from start's JSON and names land as §4 step 1's *By hand* paragraph does; land refuses a null snapshot` |
| `r5m` | `t_midrun_open_resume: a fresh continuation leaves the open run standing where it names its record by --started or finds its own stopped start's (the here row, nothing pushed); finding a record whose start returned, or a stopped on…` |
| `o_own` | `t_midrun_open_resume: a fresh continuation leaves the open run standing where it names its record by --started or finds its own stopped start's (the here row, nothing pushed); finding a record whose start returned, or a stopped on…` |
| `o_args` | `t_midrun_open_resume: a fresh continuation leaves the open run standing where it names its record by --started or finds its own stopped start's (the here row, nothing pushed); finding a record whose start returned, or a stopped on…` |
| `o_clear` | `t_call_returned_mark: true once a call returns; false where a plain start, then the continuation that goes on with its record, is killed in its stages; true once that continuation returns` |
| `o_mark` | `t_call_returned_mark: true once a call returns; false where a plain start, then the continuation that goes on with its record, is killed in its stages; true once that continuation returns` |
| `o_del` | `t_midrun_open_resume: taking over its stopped start's record deletes nothing of another run -- the earlier run's parked record byte for byte` |
| `n1` | `t_midrun_open_next_aged: the next, made past 15 minutes, takes its record over -- started_before [the first start's stamp], replaced null -- and the run typed under it still reads it as standing` |
| `n2` | `t_midrun_open_next_aged: the next, made past 15 minutes, takes its record over -- started_before [the first start's stamp], replaced null -- and the run typed under it still reads it as standing` |
| `n2b` | `t_resume_stale_no_park: a resume run fresh takes over its own record, parking none` |
| `n3` | `r_start_current: the Specs preflight: form, next names start --resume with the start call's args` |
| `n4` | `r_start_queued: the first replay switches first and back to main after, next names the second` |
| `n5` | `t_settle_queue: both rejections queued, the first replay named` |
| `c_named` | `t_call_returned_named: a named continuation, a fresh named one and a re-run, each killed in its stages, leave the mark true` |
| `c_named_b` | `t_call_returned_named: the record a killed named call left is set aside by another run's unnamed continuation, never taken up as its own` |
| `c_rerun` | `t_call_returned_named: a named continuation, a fresh named one and a re-run, each killed in its stages, leave the mark true` |
| `c_error` | `t_call_returned_error: a call whose stages and whose _close both raise still returns its JSON, its stamp in it, and leaves the mark true` |
| `c_error_b` | `t_call_returned_error: a call whose stages and whose _close both raise still returns its JSON, its stamp in it, and leaves the mark true` |
| `u_true` | `t_resume_unnamed_other_run: a continuation given no --started meets another run's record marked true as a plain start does -- it parks it and starts afresh` |
| `u_true_b` | `t_resume_unnamed_other_run: the other run's next, by its --started, goes on with its own record, this run's untouched` |

### Task 9 — B2's and B4's switch to a missing local default (`scenarios_start`)

Fix round 2 (`dc0b69ec`): 3 mutants, each killed by its own check. The harness cut each line at 100 characters; the lines are as it printed them.

| Mutant | Change | The check line that failed |
|---|---|---|
| m1-no-make-default | the old plain switch | `t_b4_no_local_default (locked): main made at origin/main, no upstream, and the checkout …` |
| m2-no-upstream | no best-effort upstream | `t_b4_no_local_default (writable): main made at origin/main, tracking origin/main, and th…` |
| m3-guess-back | the re-run's switch back without `--no-guess` | `t_rerun_no_guess: no switch back makes the deleted branch again from origin's copy` |

### Task 9b — no switch or branch creation half-moves a checkout (`scenarios_start`)

From its harness files, each mutant run through the whole selftest: 5 mutants, every one killed. A row gives the lines of the check the mutant was written for; the others it failed are counted.

| Mutant | Change | The check lines that failed |
|---|---|---|
| mutant 1 | `missing = False` in `_make_default_fix` | `t_fix_no_local_default (g2): the Fix, run with .git/config locked, moves the checkout whole onto main, and the end repeats it`<br>`t_fix_no_local_default (g1 merged): the Fix, run with .git/config locked, switches to main whole and commits notes.md there` |
| mutant 2 | `missing = True` in `_make_default_fix` | `t_fix_no_local_default (g2, local main): the plain switch` and 17 other lines |
| mutant 3 | `_end_view` returns a G2 view as it is | `t_fix_no_local_default (g2): the Fix, run with .git/config locked, moves the checkout whole onto main, and the end repeats it` |
| mutant 4 | `row.push-refused`'s template loses `--no-track` | `e_push_refused: refused, the record file written under the common git directory with today's date`<br>`e_push_refused: the file cannot be written, so the configuration key is` and 13 other lines |
| mutant 5 | `fix.make-default`'s `;` after the upstream step made ` &&` | `t_fix_no_local_default (g2): the Fix, run with .git/config locked, moves the checkout whole onto main, and the end repeats it`<br>`t_fix_no_local_default (g2, run again): refused over the file in the way, nothing moved; once it is moved, the same line switches whole`<br>`t_fix_no_local_default (g1 merged): the Fix, run with .git/config locked, switches to main whole and commits notes.md there` and 7 other lines |

### The final review's fix passes

One mutant per code fix, each run through the whole selftest (`b5b5714c`, `b5c71e2c`, `6ab84d51`, `5805ea7b`). `t_guard_other_run`, which pass 2's first mutant fails, was replaced by the two `t_guard_s3_*` checks under ruling (a).

| Mutant | The check line that failed |
|---|---|
| pass 1: I2: no keep-out | `t-midrun-open-writes-stay: the open run's rewritten resume pointer stays out of the change, its newer version in the working tree, the line naming it; its appended cost entry travels`<br>`t-midrun-open-writes-stay: the open run's own end commits its resume pointer as it stands`<br>`t-midrun-open-writes-here: the open run's rewritten resume pointer stays out of the change, its newer version in the working tree, the line naming it; its appended cost entry travels`<br>`t-midrun-open-writes-here: the open run's own end commits its resume pointer as it stands` and 1 more |
| pass 1: M1: park never protects | `t-same-command-other-key-second-first: the second start stays, commits none of the first run's file, parks its record still protecting and reads it as its open run`<br>`t-same-command-other-key-second-first: each end finds its own record; the first's commits its file on its own branch`<br>`t-same-command-other-key-first-second: the second start stays, commits none of the first run's file, parks its record still protecting and reads it as its open run`<br>`t_same_command_restarts_parked: K1's parked record protects nothing once K1 is typed again; K2 stays protecting and is the third run's open run` |
| pass 1: M1b: no restarts of parked records | `t_same_command_restarts_parked: K1's parked record protects nothing once K1 is typed again; K2 stays protecting and is the third run's open run` |
| pass 1: M2: no derived path | `t_no_start_end_beside: the first run's record byte for byte, no file of the end's left, and the first run's end finds its own`<br>`selftest crashed: FileNotFoundError: [Errno 2] No such file or directory: '/tmp/tmpgzqbj7oe/home-e-stale/.claude/dev-workflows/specs-git/e-stale/create-ard.json'` |
| pass 1: UR: restore keeps call_returned false | `t_resume_unnamed_restored: the restored record marked returned; the continuation starts afresh and sets it aside` |
| pass 1: M4: no landed form | `l_g1_end: a stay -- the landing form, its Not done the landed one after a whole landing and the not-landed one after any other outcome`<br>`l_g1_end: M4 -- the landed form promises nothing more after the commit`<br>`l_g1_end: under a run typed mid-run, the mid-run form, its Not done by the same outcomes, a mid-run row that committed nothing taking the not-committed one` |
| pass 2: N1, the first guard (`_open_other` off) | `t_guard_other_run: the middle run leaves the restarted run's pointer out while the restart stands, the working copy at v2`<br>`t_guard_other_run: the restart's own end commits its pointer on its branch` |
| pass 2: ruling (a), the typed run's guard dropped where nobody stands | `t-guard-s3-middle-first: the middle run leaves the restarted run's pointer out in either end order, the working copy at v2, and the restart, typed under it, leaves its own rewrite out too`<br>`t-guard-s3-restart-first: the middle run leaves the restarted run's pointer out in either end order, the working copy at v2, and the restart, typed under it, leaves its own rewrite out too`<br>`t_guard_open_run_ended: the pointer left out though the open run has ended, left for a later commit on the branch` |
| pass 3: P1, the guard disabled in `_own_commits` | `t-guard-s3-middle-first: the middle run leaves the restarted run's pointer out in either end order, the working copy at v2, and the restart, typed under it, leaves its own rewrite out too`<br>`t-guard-s3-restart-first: the middle run leaves the restarted run's pointer out in either end order, the working copy at v2, and the restart, typed under it, leaves its own rewrite out too`<br>`t_guard_open_run_ended: the pointer left out though the open run has ended, left for a later commit on the branch`<br>`t-guard-s4-later-first: neither the untyped stayed run nor the run typed under it takes the pointer, in this end order; the working copy at v2`<br>`t-guard-s4-untyped-first: neither the untyped stayed run nor the run typed under it takes the pointer, in this end order; the working copy at v2`<br>`t_guard_untyped_alone: the run's own rewrite of the start-dirty pointer left out of its landing`<br>`t_guard_here_replay: the replayed here-form row names the pointer left out` |


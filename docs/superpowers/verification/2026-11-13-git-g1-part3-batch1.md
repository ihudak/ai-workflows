# GIT-G1 Part 3, batch 1 — the selftest out of `specs-git.py` — verification record

**Plan:** `docs/superpowers/plans/2026-11-13-git-g1-part3-batch1-selftest-split.md`. **Design:** `docs/superpowers/specs/2026-11-13-git-g1-part3-design.md`, §5.1 and §9 (*Batch 1*, *Each batch*). **Release:** `workflows-core` 1.85.2, its changelog section dated 2026-11-13 (cut as 1.85.1 at `cea76e95` and renumbered at `7deeb75c`; *The release* below). **Branch:** `feat/git-g1-p3-selftest`, base `80760699` (the plan's two commits, `bc817dbe` and `6299098a`, on the design branch `feat/git-g1-part3`, which stands on `main` at `84527132`, merged with that branch's `a935c468`), with `main` merged twice: `d25e1d89` (PR #187, the design) at `9ba6eff1`, and `3016ead8` (PR #188) at `7deeb75c`. Measured at `174af1e6`, which is `7deeb75c` plus one changelog sentence (*The release*); what the closing review changed was measured again at `c6eefbaf`, and every commit after `174af1e6`, with what it changes, is listed in *The gates and the budgets*. Written last, after the final review's fix wave and its closing fixes, and corrected after the closing review (*The reviews*). Every figure below is re-derived here with its command beside it or in a code block above it; where a figure is a report's or the ledger's and was not re-run, the sentence says so.

The rulings summary is `2026-11-13-git-g1-part3-batch1-rulings.md` beside this file, and the ledger, verbatim, is `2026-11-13-git-g1-part3-batch1-ledger.md`; the controller writes both.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2 (`python3 --version`), git 2.43.0, uid 502 (`id -u`; not root, so the selftest's root-skipped cases ran). Every command ran from the worktree root, `/workspace/.worktrees/git-g1-p3-selftest`, unless a tree is named. `$S` is a scratch directory outside the repository; a commit's tree is unpacked there as `git archive <sha> | tar -x -C "$S/tree-<sha>"`.

**The branch.** After `git fetch origin main`, `origin/main` is `3016ead8` and an ancestor of the branch. At `c6eefbaf`, the closing review's fixes, `git log --oneline --first-parent origin/main..c6eefbaf | wc -l` gives 24 (the two plan commits, the base's merge of the design branch, two merges of `main`, and nineteen others). `git diff --shortstat origin/main c6eefbaf` gives 16 files changed, 14,719 insertions(+), 13,020 deletions(-); the 16 are `.claude-plugin/marketplace.json`, `.claude/rules/specs-git-selftest.md`, `.github/workflows/validate-catalog.yml`, `CLAUDE.md`, `docs/maintainers/rationale.md`, the plan, the design, this record and the two files beside it, `plugins/workflows-core/.claude-plugin/plugin.json`, `plugins/workflows-core/CHANGELOG.md`, `plugins/workflows-core/scripts/specs-git.py`, and the three files under `scripts/selftests/`.

## What the batch delivered against the design's §5.1 and §9

| §9, *Batch 1* and *Each batch* | Where this record shows it |
|---|---|
| the selftest lives outside `specs-git.py` | *The move, byte for byte*; `grep -cE 'def (selftest\|scenarios_)' plugins/workflows-core/scripts/specs-git.py` gives 0 at `174af1e6`, and 16 on the base's script |
| the check count is unchanged by the move, and rises only by checks of the group runs | *The check counts*; the rise is a departure in part (*What departs*) |
| a mutant per scenario group still fails its check; the eight named checks each have a mutant on record | *The mutants* |
| one group can be run alone | *Each group alone* |
| CI is green | not shown: the branch had not been pushed (*Known limits*); the gate steps run locally are in *The gates and the budgets* |
| a verification record written last; the rulings and the verbatim ledger committed; dated changelogs; a coupling bullet where the coupling file's test calls for one | this file; the controller's two files beside it; *The release* |

### The move, byte for byte

The base's function, lines 5093 to 18101 of the script at `80760699`, against the test file as Task 1 committed it, from `def selftest():` to its end:

```bash
git show 80760699:plugins/workflows-core/scripts/specs-git.py | sed -n '5093,18101p' > "$S/base-fn.py"
head -1 "$S/base-fn.py"; tail -1 "$S/base-fn.py"; wc -l < "$S/base-fn.py"
# def selftest():
#     return 0
# 13009
git show f437dd48:scripts/selftests/specs_git_selftest.py > "$S/t1-file.py"
start=$(grep -n '^def selftest():' "$S/t1-file.py" | cut -d: -f1)   # 16, of 13024 lines
tail -n +"$start" "$S/t1-file.py" | cmp - "$S/base-fn.py" && echo IDENTICAL
# IDENTICAL
```

Lines 18102 to 18105 of the base are two blank lines and the `if __name__ == "__main__":` block, which stay in the script. Above `def selftest():` at `f437dd48` stand the docstring, `import contextlib`, `import tempfile` and the three constants `SPECS_REPO_GIT`, `ADDRESSING` and `SESSION_HYGIENE`, the names only the tests used (Task 1's report lists each one's uses before and after the deletion; not re-derived here).

At the head the function is no longer byte-identical, by design: `diff "$S/base-fn.py" <(tail -n +21 scripts/selftests/specs_git_selftest.py)` (the head's `def selftest(groups=None):` is at line 21) gives five hunks, `1,2c1,14` (the signature, the docstring and the two guards of *What the batch added*), `12979a12992,13085` (the new `scenarios_selftest`), `12982,12996c13088,13090` (the fifteen `scenarios_*` calls replaced by the loop over `GROUPS`) and two at the PASS and FAIL lines, `13004c13098` and `13008c13102,13105`. So base lines 3 to 12979 — every test that was in the script — stand unchanged at the head.

### No behaviour change

`git diff 80760699 174af1e6 -- plugins/workflows-core/scripts/specs-git.py` has six hunks, 31 insertions and 13,016 deletions (`--stat`); `git diff --stat 80760699 origin/main -- plugins/workflows-core/scripts/specs-git.py` is empty, so `main` changed nothing in the script. With the moved function set aside, the non-test changes are:

| Change | Why the plan allows it |
|---|---|
| The docstring's usage line `specs-git.py --selftest` becomes `specs-git.py --selftest [--group <name>]...` | Global Constraints: "the usage line"; Task 2 step 4 |
| `import contextlib` and `import tempfile` removed | Global Constraints: "the two imports and three constants that only the tests use, which move with them"; Task 1 step 3 |
| `SPECS_REPO_GIT`, `ADDRESSING`, `SESSION_HYGIENE` removed; `SELFTEST_FILE` added after `HERE` | the same; Task 1 step 3 |
| The `--selftest` help text becomes `run the selftest, which the repository keeps under scripts/selftests, and exit`; `--group` (`action="append"`) added beside it | Global Constraints: "the `--group` argument … and the `--selftest` help text"; Tasks 1 and 2 |
| In `main`, `--group` without `--selftest` is `ap.error("--group needs --selftest")`, and `return selftest()` becomes `return _run_selftest(a.group)` | Global Constraints: "the `--group` argument"; Task 2 step 4 |
| `selftest()` replaced by `_run_selftest(groups)`, which reads `SELFTEST_FILE`, executes it in the script's `globals()` and calls `selftest(groups)`; it exits 2 with one stderr line where the file is absent (`FileNotFoundError`, `NotADirectoryError`), where it cannot be read (any other `OSError`), or where the executed file rebinds a name the script already held | Global Constraints: "the loader"; the two refusals are the final review's M2 and M3, which the ledger's ruling on M3 places under "the loader" |

No subcommand's code changed: every hunk is one of the six above.

### The check counts

| Commit | `specs-git.py --selftest` | Source |
|---|---|---|
| `80760699`, the base | `specs-git selftest: PASS (1176 checks)`, real 3 min 12.0 s | run here, in `$S/tree-80760699`, as `( time python3 -B plugins/workflows-core/scripts/specs-git.py --selftest ) 2>&1 \| tail -5` |
| `f437dd48`, Task 1 | `specs-git selftest: PASS (1176 checks)`, real 1 min 37.9 s | run here, the same way, in `$S/tree-f437dd48` |
| `440f2e5a`, Task 2 | `PASS (1182 checks)` | Task 2's report; not re-run |
| `edb40b7f` and `5ae96dae`, the fix wave and its closing fixes | `PASS (1187 checks)` | the fix report; not re-run |
| `174af1e6` | `specs-git selftest: PASS (1187 checks)`, real 1 min 38.4 s (user 1 min 16.9 s, sys 22.7 s), rc 0 | run here: `( time python3 -B plugins/workflows-core/scripts/specs-git.py --selftest ) 2>&1 \| tail -5` |

The base's 1,176 is the design's figure (§5.1: "1,176 at `fdafe85e` … re-derive it on the batch's base"), re-derived on the base. The move left it unchanged. All eleven checks added since are in the new `selftest` group, and `python3 -B plugins/workflows-core/scripts/specs-git.py --selftest --group selftest` prints `PASS (11 checks; partial: selftest)` (below). Each label occurs once in `scripts/selftests/specs_git_selftest.py` (`grep -n '"<name>:'`, line given):

- Task 2's six: `s_group_alone` (13028), `s_group_order` (13031), `s_group_unknown` (13035), `s_group_without_selftest` (13038), `s_selftest_not_shipped` (13055), `s_ci_runs_all` (13091).
- The final fix wave's five: `s_group_refused_in_ci` (13043, the final review's I1), `s_nested_refused` (13048, I2), `s_selftest_unreadable` (13070, M2), `s_selftest_redefines` (13081, M3), `s_file_run_directly` (13086, M9, a check the finding did not ask for).

1176 + 6 + 5 = 1187. The `s_nested:` failure that `scenarios_selftest`'s first line records (13017) runs only under the nested marker, so a plain run does not count it.

### The three checks that read the script's own source

Task 1 step 5 read each and found that removing the tests from the text it reads changes nothing it can catch; Task 1's review approved it. Re-derived here on the base and the head (`python3 -I -B` over `git show 80760699:…` and the head's script, with the test's own `defined()` and pattern):

- **`defined(os.path.abspath(__file__), f)`** (test file line 1935, read by `l_ids`): it slices `_land_change`, `_here_move` and `_land` out of the script from `\ndef <name>(` to the next `\ndef `. Each slice is the same on both trees — 7,724, 3,277 and 6,481 characters — and ends at a non-test function (`_waited_on`, `_finish_here`, `retry_held`), so the moved text was never inside one.
- **The `SG_SCRIPT` same-file test** (line 1961, in `l_constants`): `os.path.samefile(script, os.path.abspath(__file__))`. It reads no text; it holds because the file is executed in the script's namespace, where `__file__` is still the script's. The full run's PASS at the head shows it.
- **`l_sb_reused`** (line 7559): fails on any column-0 `def own_change|tree_with|commit_tree|move_branch|replay_commits` in the script's text. It finds none on either tree; the only column-0 `def` in the base's moved text is `selftest` itself, so that text could never have failed it.

### Each group alone

The rules file's loop, as written there (*How long it takes*), run from the worktree root with `PYTHONDONTWRITEBYTECODE=1` exported, since its `python3` carries no `-B`. It works as written and prints one `<group> <seconds> s` line per group; its stdout goes to `/dev/null`, so it shows neither a count nor a PASS line:

```bash
(for g in $(python3 plugins/workflows-core/scripts/specs-git.py --selftest --group '?' 2>&1 | sed 's/.*one of: //; s/)$//; s/,//g'); do
  TIMEFORMAT="$g %1R s"; time python3 plugins/workflows-core/scripts/specs-git.py --selftest --group "$g" > /dev/null
done)
# status 0.4 s, branch_merged 0.4 s, branch_key 0.3 s, push_scope 0.4 s, owner_repo 0.3 s, mode 7.5 s, state 0.8 s, lines 0.2 s,
# gate 0.5 s, end 27.7 s, land 7.5 s, replay 3.4 s, start 16.7 s, midrun 31.8 s, skill 0.6 s, selftest 1.5 s   (100.0 s in all)
```

For the counts, the plan's Task 2 step 6 loop, with `-B`, each run's exit status and its wall time (`date +%s.%N` around it) added:

```bash
total=0
for g in status branch_merged branch_key push_scope owner_repo mode state lines gate end land replay start midrun skill selftest; do
  t0=$(date +%s.%N); line="$(python3 -B plugins/workflows-core/scripts/specs-git.py --selftest --group "$g" | tail -1)"; rc=${PIPESTATUS[0]}; t1=$(date +%s.%N)
  echo "$g: $line  [rc=$rc, $(printf '%.1f' "$(echo "$t1 - $t0" | bc)") s]"
  n="$(printf '%s' "$line" | sed -n 's/^specs-git selftest: PASS (\([0-9]*\) checks; partial: .*/\1/p')"
  total=$((total + ${n:-0}))
done
echo "sum=$total"
```

| Group | Line | Time |
|---|---|---|
| `status` | `specs-git selftest: PASS (11 checks; partial: status)` | 0.5 s |
| `branch_merged` | `specs-git selftest: PASS (12 checks; partial: branch_merged)` | 0.5 s |
| `branch_key` | `specs-git selftest: PASS (13 checks; partial: branch_key)` | 0.3 s |
| `push_scope` | `specs-git selftest: PASS (11 checks; partial: push_scope)` | 0.4 s |
| `owner_repo` | `specs-git selftest: PASS (16 checks; partial: owner_repo)` | 0.3 s |
| `mode` | `specs-git selftest: PASS (86 checks; partial: mode)` | 7.6 s |
| `state` | `specs-git selftest: PASS (70 checks; partial: state)` | 0.8 s |
| `lines` | `specs-git selftest: PASS (105 checks; partial: lines)` | 0.2 s |
| `gate` | `specs-git selftest: PASS (57 checks; partial: gate)` | 0.6 s |
| `end` | `specs-git selftest: PASS (211 checks; partial: end)` | 27.8 s |
| `land` | `specs-git selftest: PASS (124 checks; partial: land)` | 7.5 s |
| `replay` | `specs-git selftest: PASS (106 checks; partial: replay)` | 3.4 s |
| `start` | `specs-git selftest: PASS (172 checks; partial: start)` | 16.7 s |
| `midrun` | `specs-git selftest: PASS (135 checks; partial: midrun)` | 32.3 s |
| `skill` | `specs-git selftest: PASS (47 checks; partial: skill)` | 0.7 s |
| `selftest` | `specs-git selftest: PASS (11 checks; partial: selftest)` | 1.6 s |

Every run exited 0 and named its own group; `sum=1187`, the full run's count, so no group passes only after another has run. The sixteen times add to 101.2 s, against 98.4 s for the full run in one process.

### The mutants

```bash
python3 -B scripts/selftests/mutants.py --list            # rc 0
python3 -B scripts/selftests/mutants.py --list | wc -l    # 23
python3 -B scripts/selftests/mutants.py --check           # mutants: 23 checked, 0 stale   (rc 0, real 0.204 s)
```

The three ran at `174af1e6`, and again on the tree `c6eefbaf` commits (run just before that commit, with no edit between) with the same count, rc and last line. There, after the closing review tightened five `fails` (*The five `fails` the closing review tightened*, below), `--list` prints `<id> <group> <fails>`:

```
e_land_refused end e_land_refused:
e_land_stopped end e_land_stopped:
e_land_offline end e_land_offline:
e_land_no_origin end e_land_no_origin:
t_held_journal end t_held_journal:
t_midrun_keyed_other midrun t-midrun-keyed-other: no commit on the branch
e_midrun_here_kill midrun e_midrun_here_kill: error set
e_midrun_here_no_resume midrun e_midrun_here_no_resume:
status_rename_original status status: a rename's original path
branch_merged_squash branch_merged branch-merged: a squash merge is test 3
branch_key_underscore_slug branch_key branch-key: ard/EPIC-008-01_slug with
push_scope_merge_commit push_scope push-scope: a merge commit fails
owner_repo_alias_host_kept owner_repo owner-repo: git@github-ig.com:acme/repo.git (alias False) gives
mode_m_remote_deleted mode m_remote_deleted:
state_s_remove state s_remove: load then None
lines_l_literal_bracket lines l_literal_bracket:
gate_g_file gate g_file: a regular file
land_l_land_absent land l_land_absent:
replay_r_not_run replay r_not_run:
start_t_b4_no_remote start t_b4_no_remote:
skill_k_skill_options skill k_skill_options: every option
selftest_s_group_without_selftest selftest s_group_without_selftest:
selftest_s_group_alone selftest s_group_alone:
```

**Every group has one.** The sixteen names `specs-git.py --selftest --group '?'` prints, split one per line and sorted, against `--list | awk '{print $2}' | sort -u`: `comm -3` prints nothing. Per group (`--list | awk '{print $2}' | sort | uniq -c`): `end` 5, `midrun` 3, `selftest` 2, every other group 1. By file (the mutants file's `file`): `specs-git.py` 21, `specs_git_state.py` 1 (`state_s_remove`), `specs_git_lines.py` 1 (`lines_l_literal_bracket`).

**The eight checks the STAY-2 record named** (`docs/superpowers/verification/2026-11-10-stay2-midrun.md`, *Not examined*, line 489) each have a mutant whose `id` is the check's name: `e_land_refused`, `e_land_stopped`, `e_land_offline`, `e_land_no_origin` and `t_held_journal` in group `end`, and `t_midrun_keyed_other`, `e_midrun_here_kill` and `e_midrun_here_no_resume` in group `midrun`. `t_midrun_keyed_other`'s `fails` starts `t-midrun-keyed-other:`, the label its case builds from its `name` argument (plan Task 4 step 2).

**One run of every mutant**, at `174af1e6`, before the closing review tightened five `fails`, in five foreground invocations of `--only`. A Bash call that runs past 180 seconds here is moved to the background by the harness, so the full run, which the rules file says takes over nine minutes, was split so that each invocation stays under that; the split costs a second baseline run each of `end` and `midrun`.

| Invocation (`( time python3 -B scripts/selftests/mutants.py --only … ) 2>&1`) | Last line | Real time | Exit |
|---|---|---|---|
| `e_land_refused`, `e_land_stopped`, `e_land_offline` | `mutants: 3 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 3` | 2 min 38.706 s | 0 |
| `e_land_no_origin`, `t_held_journal` | `mutants: 2 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 2` | 1 min 59.238 s | 0 |
| `t_midrun_keyed_other`, `e_midrun_here_kill` | `mutants: 2 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 2` | 2 min 21.346 s | 0 |
| `e_midrun_here_no_resume` | `mutants: 1 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 1` | 1 min 34.628 s | 0 |
| the other fifteen | `mutants: 15 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 15` | 1 min 53.584 s | 0 |

23 killed of 23, in 627.5 s in all. Each `killed` line, cut here where the check's value dump begins (the runner itself cuts at 160 characters); the group's size is its count above:

| Mutant | Group (size) | Failure lines | The line |
|---|---|---|---|
| `e_land_refused` | `end` (211) | 1 | `e_land_refused: the refused switch's stay lands at the end` |
| `e_land_stopped` | `end` | 1 | `e_land_stopped: the early stop's stay lands` |
| `e_land_offline` | `end` | 2 | `e_land_offline: committed on main, push FAILED naming main` |
| `e_land_no_origin` | `end` | 3 | `e_land_no_origin: committed on main, no-remote` |
| `t_held_journal` | `end` | 1 | `t_held_journal: the verified journal lifted, main unmoved, the record empty` |
| `t_midrun_keyed_other` | `midrun` (135) | 4 | `t-midrun-keyed-other: no commit on the branch, HEAD unmoved, pre.stay.midrun naming /specify, a mid-run stay` |
| `e_midrun_here_kill` | `midrun` | 1 | `e_midrun_here_kill: error set, the index showing the reversal, end_commit.here and the held record holding the journal` |
| `e_midrun_here_no_resume` | `midrun` | 1 | `e_midrun_here_no_resume: a new session's start finishes the restore` |
| `status_rename_original` | `status` (11) | 2 | `status: a rename's original path is no record of its own` |
| `branch_merged_squash` | `branch_merged` (12) | 1 | `branch-merged: a squash merge is test 3, with a dirty session file in the tree (GIT-B2)` |
| `branch_key_underscore_slug` | `branch_key` (13) | 1 | `branch-key: ard/EPIC-008-01_slug with ['EPIC-008-01'] resolves to 'EPIC-008-01'` |
| `push_scope_merge_commit` | `push_scope` (11) | 1 | `push-scope: a merge commit fails` |
| `owner_repo_alias_host_kept` | `owner_repo` (16) | 1 | `owner-repo: git@github-ig.com:acme/repo.git (alias False) gives 'github-ig.com/acme/repo'` |
| `mode_m_remote_deleted` | `mode` (86) | 1 | `m_remote_deleted: the push recreates it` |
| `state_s_remove` | `state` (70) | 1 | `s_remove: load then None, and s2/ is gone with its last record` |
| `lines_l_literal_bracket` | `lines` (105) | 1 | `l_literal_bracket: [SEC# stays literal` |
| `gate_g_file` | `gate` (57) | 1 | `g_file: a regular file is not a directory` |
| `land_l_land_absent` | `land` (124) | 1 | `l_land_absent: no local main: created at the landed commit, on origin/main` |
| `replay_r_not_run` | `replay` (106) | 3 | `r_not_run: the could-not-run clause` |
| `start_t_b4_no_remote` | `start` (172) | 1 | `t_b4_no_remote: no pull and no pull-failed line where there is no origin` |
| `skill_k_skill_options` | `skill` (47) | 1 | `k_skill_options: every option the skill names is the CLI's, where it names it` |
| `selftest_s_group_without_selftest` | `selftest` (11) | 1 | `s_group_without_selftest: --group alone is a usage error` |
| `selftest_s_group_alone` | `selftest` | 3 | `s_group_alone: one group runs alone and says so` |

No mutant failed more than 4 of its group's checks. Task 4's report names the extra failure lines of the multi-line ones (`e_land_offline` also fails `e_push_failed`; `e_land_no_origin` also `e_no_remote` and `e_land_checked_out_no_origin`; `replay_r_not_run` two `r_canned` lines; `t_midrun_keyed_other` three keyed-case lines and `t_midrun_rerun_no_record`, never `t-midrun-keyless`); the fix report names `selftest_s_group_alone`'s (`s_group_order`, `s_group_unknown`). Neither was re-derived here. After the five runs, `ls -d /tmp/mutants-*` found nothing and no process named a mutants copy.

**The five `fails` the closing review tightened.** The closing review (*The reviews*) logged every message a full run checks, 1,187 of them, and found five `fails` that stopped at a label more than one of them carries at run time — in each case several assertions of one named check: `t-midrun-keyed-other:` 3, `e_midrun_here_kill:` 2, `s_remove:` 3, `g_file:` 2 and `k_skill_options:` 10, nine of them one written message checked in a loop over nine wrong options. `c6eefbaf` set each to the value the review gave, each of which the review found to match exactly one of the 1,187 messages (not re-derived here: this record kept no log of a run's messages):

| Mutant | `fails` before | `fails` at `c6eefbaf` | `grep -cF '"<fails>' scripts/selftests/specs_git_selftest.py` |
|---|---|---|---|
| `t_midrun_keyed_other` | `t-midrun-keyed-other:` | `t-midrun-keyed-other: no commit on the branch` | 0: the label is built from a `name` argument |
| `e_midrun_here_kill` | `e_midrun_here_kill:` | `e_midrun_here_kill: error set` | 1 |
| `state_s_remove` | `s_remove:` | `s_remove: load then None` | 1 |
| `gate_g_file` | `g_file:` | `g_file: a regular file` | 1 |
| `skill_k_skill_options` | `k_skill_options:` | `k_skill_options: every option` | 1 |

Run on the tree `c6eefbaf` commits, before that commit, with no edit between; each value dump is cut here:

```
$ ( time python3 -B scripts/selftests/mutants.py --only state_s_remove --only gate_g_file --only skill_k_skill_options ) 2>&1   # EXIT=0, real 6.528 s
killed state_s_remove (1 failure lines): s_remove: load then None, and s2/ is gone with its last record
killed gate_g_file (1 failure lines): g_file: a regular file is not a directory (…)
killed skill_k_skill_options (1 failure lines): k_skill_options: every option the skill names is the CLI's, where it names it (…)
mutants: 3 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 3
$ ( time python3 -B scripts/selftests/mutants.py --only t_midrun_keyed_other --only e_midrun_here_kill ) 2>&1   # EXIT=0, real 2 min 21.944 s
killed t_midrun_keyed_other (4 failure lines): t-midrun-keyed-other: no commit on the branch, HEAD unmoved, pre.stay.midrun naming /specify, a mid-run stay (…)
killed e_midrun_here_kill (1 failure lines): e_midrun_here_kill: error set, the index showing the reversal, end_commit.here and the held record holding the journal (…)
mutants: 2 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 2
```

Each of the five printed the same failure line as at `174af1e6` (the table above), and the same number of failure lines. On the same tree, `python3 -B plugins/workflows-core/scripts/specs-git.py --selftest --group selftest | tail -1` printed `specs-git selftest: PASS (11 checks; partial: selftest)`: the mutants file is data the selftest does not read, and the rest of `c6eefbaf` is prose.

### The runner's proofs

| Outcome | Shown where | Re-run here, at `174af1e6` |
|---|---|---|
| `killed` | Task 3 step 2 (`6e1932b2`), again after its fix round (`99e6c18c`), and in the fix report | yes |
| `SURVIVED` (a comment-only edit) | the same | yes |
| `STALE` (an `old` text the file does not hold) | the same; an `old` that overlaps itself counted twice, Task 3 fix round (finding 3) | yes |
| The same-length bytecode case (rule 2) | Task 3 step 2, with a counterfactual runner without `-B` in which the second mutant read `killed` from the first one's bytecode; again on the fresh-copy runner, fix report (M11) | yes, the `-B` side only |
| `TIMEOUT`, its grandchild killed with the run's process group | Task 3 (a watch harness listing the processes in the copy at 30 s and after exit; also a hang inside a `0555` directory, which found a defect fixed there) and its fix round; the fix report | yes |
| `BASELINE RED` | Task 3 (a `PATH` with no `git`), with its reason line after the fix round; under `GITHUB_ACTIONS=true` on `edb40b7f`'s runner, the fix report's N3 counterfactual | yes, both sides of N3 |
| SIGTERM, SIGHUP, SIGINT end the runner with 128 + the signal, nothing left; a second signal ignored | Task 3 fix round, with a counterfactual on `6e1932b2`'s runner that left its copy and two processes | no |
| An inherited ignored SIGHUP stays ignored (M7a) | fix report, with a counterfactual on `cea76e95`'s runner (exit 129) | no; M7(b), a signal inside a window of a few bytecodes, was shown only by reading, and M7(c) is a constant |
| `--check` finding a stale mutant, and `--check` with `--list` refused | fix report (I3) | the first, yes |
| A malformed mutants file, an unknown `--only` id, a usage error, a temporary directory under the repository refused | Task 3 | no |

The proof file used here, `$S/proof.json`, holds Task 3's mutants: `p1_branch_key_min` (`max(found, key=len)` → `min(…)` in `branch_key`, `fails` `branch-key:`), `p2_branch_key_comment` and `p4b_state_comment` (a comment appended to `branch_key`'s `partition` line, in groups `branch_key` and `state`), `p3_stale` (an `old` the script lacks), `p4a_state_version` (`VERSION = 1` → `VERSION = 2` in `specs_git_state.py`, `fails` `s_roundtrip:`) and `t1_cli_hangs` (`main`'s `return branch_key(a.branch, a.key)` → `while True: pass`). Each `old` was found once in the head's files (`grep -cF`).

```
$ python3 -B scripts/selftests/mutants.py --file "$S/proof.json" --only p1_branch_key_min                                   # EXIT=0
killed p1_branch_key_min (2 failure lines): branch-key: spec/ACME-77-01-checkout with ['ACME-77', 'ACME-77-01'] resolves to 'ACME-77-01' ({'plugin_branch': True, 'prefix': 'spec', 'key': 'ACME-77'})
$ … --only p2_branch_key_comment                                                                                             # EXIT=1
SURVIVED p2_branch_key_comment
$ … --only p3_stale                                                                                                          # EXIT=1
STALE p3_stale: old text found 0 times in plugins/workflows-core/scripts/specs-git.py
$ … --only p4a_state_version --only p4b_state_comment                                                                        # EXIT=1
killed p4a_state_version (2 failure lines): s_roundtrip: FIELDS is not mutated by new()
SURVIVED p4b_state_comment
mutants: 1 killed, 1 survived, 0 stale, 0 timed out, 0 on a red baseline, of 2
$ python3 -B scripts/selftests/mutants.py --file "$S/proof.json" --check                                                    # EXIT=1
STALE p3_stale: old text found 0 times in plugins/workflows-core/scripts/specs-git.py
mutants: 6 checked, 1 stale
$ env PATH="$S/nogit" /opt/pyenv/versions/3.15.2/bin/python3 -B scripts/selftests/mutants.py --file "$S/proof.json" --only p1_branch_key_min --only p4a_state_version   # EXIT=1
BASELINE RED branch_key
  selftest crashed: FileNotFoundError: [Errno 2] No such file or directory: 'git'
BASELINE RED state
  selftest crashed: FileNotFoundError: [Errno 2] No such file or directory: 'git'
mutants: 0 killed, 0 survived, 0 stale, 0 timed out, 2 on a red baseline, of 2
$ GITHUB_ACTIONS=true python3 -B scripts/selftests/mutants.py --only branch_key_underscore_slug                             # EXIT=0
killed branch_key_underscore_slug (1 failure lines): branch-key: ard/EPIC-008-01_slug with ['EPIC-008-01'] resolves to 'EPIC-008-01' ({'plugin_branch': True, 'prefix': 'ard', 'key': None})
$ ( time python3 -B scripts/selftests/mutants.py --file "$S/proof.json" --only t1_cli_hangs ) 2>&1                          # EXIT=1, real 1 min 0.797 s
TIMEOUT t1_cli_hangs
mutants: 0 killed, 0 survived, 0 stale, 1 timed out, 0 on a red baseline, of 1
```

`$S/nogit` is an empty directory. After the `TIMEOUT` run, no `/tmp/mutants-*` directory and no process naming one was left. The `p4a`/`p4b` pair is rule 2's case: run with `-B` and `PYTHONDONTWRITEBYTECODE=1`, in a fresh copy each, the comment-only mutant after the same-length one reads `SURVIVED`.

### The time, before and after

The whole selftest took 3 min 12.0 s at the base and 1 min 38.4 s at `174af1e6` (*The check counts*, both run here in one session on one machine; 1 min 37.9 s at `f437dd48`, where the move alone was made). The rationale gives the cause it measured (each child process the selftest starts no longer compiles the tests: `docs/maintainers/rationale.md#specs-git-selftest`); that measurement was not re-run here. Earlier figures, not re-derived: the plan's 3 min 12 s and "about 99 seconds"; Task 1's 189.9 s and 96.5 s; Task 5's 191.1 s and 98.3 s.

### Sizes

| File | `wc -l` | `wc -c` |
|---|---|---|
| `plugins/workflows-core/scripts/specs-git.py` at `80760699` (`git show … \| wc`) | 18,105 | 1,150,374 |
| the same at `f437dd48` | 5,106 | 312,063 |
| the same at `174af1e6` | 5,120 | 313,021 |
| `scripts/selftests/specs_git_selftest.py` at `174af1e6` | 13,126 | 848,120 |
| `scripts/selftests/mutants.py` at `174af1e6` | 438 | 22,489 |
| the same at `c6eefbaf` (its docstring reflowed, no word changed) | 437 | 22,489 |
| `scripts/selftests/specs-git-mutants.json` at `174af1e6` | 186 | 6,824 |
| the same at `c6eefbaf` (five `fails` tightened) | 186 | 6,901 |

The changelog's "from 18,105 lines to 5,120 (`wc -l`)" and its "eleven checks" agree with these runs, and the rationale's "over 840,000 bytes" with the test file's 848,120.

## What the batch added beyond the plan, and why

- **`--group` is refused in CI.** Where `GITHUB_ACTIONS` is `true`, `selftest(groups)` prints one `not run` line and exits 2 before any group runs (`s_group_refused_in_ci`). The final review's I1: `s_ci_runs_all` sits in the `selftest` group, so a CI line given `--group end` never ran it and exited 0, measured by the reviewer.
- **The nested-run marker.** `scenarios_selftest` starts every run with `SPECS_GIT_SELFTEST_NESTED=1`; such a run fails before any group runs where it asks for the `selftest` group, at `selftest()`'s head, and on reaching that group where it reaches it by another route, on `scenarios_selftest`'s first line (the head guard: `s_nested_refused`, mutant `selftest_s_group_alone`; the first-line guard: none, *Known limits*). Task 2's deferred Minor and the final review's I2 (a break in group selection recursed without end, so the group's own checks could have no mutant); the head guard alone missed a break in the selftest's own selection line, which the re-review's N1 found (36 temporary directories left under `timeout`) and the closing fix measured again at `edb40b7f` (49 left at `timeout 20`). With the first-line guard, a break on the selftest's side fails only once the nested run has run every group it selected ahead of `selftest`, which is last in the run order; the closing review measured 140 s for one marked `--selftest --group branch_key` run with the selection line made `if True:` (not re-derived here).
- **`mutants.py --check` and its CI step.** It counts each mutant's `old` text in the repository and runs no mutant and no group; CI runs it after the selftest step. The final review's I3: nothing kept the mutants from going stale, and batch 2 rewrites the script 21 of the 23 name.
- **The loader's two refusals.** An unreadable selftest path (`s_selftest_unreadable`) and a test file that rebinds a name of the script (`s_selftest_redefines`), with the test file's header made a `#` comment block. Task 1's two deferred Minors, the final review's M2 and M3: any `OSError` printed "is not there", and the test file's docstring replaced the script's `__doc__` while it ran.
- **A fresh copy per run.** Every run, each baseline included, is made in its own copy of the runner's pristine copy, discarded after it; the restore and the bytecode stop it needed went with it. The final review's M11: whatever a mutated run wrote into the one shared copy outlived the restore.
- **`fails` may run past the label.** The runner's validator takes any prefix of a failure line holding a colon after a label, and the `branch_merged`, `branch_key`, `push_scope` and `owner_repo` mutants' `fails` were tightened to their one check. Task 4's deferred Minor and the final review's M1: every check of those four groups prints one shared label, so their `fails` matched the whole group. The closing review's I1 found five more `fails` stopping at a label several assertions share, and `c6eefbaf` tightened them (*The five `fails` the closing review tightened*): nine in all.
- **The guard when the test file is run directly.** Its first statement exits 1 with one line naming the command that runs it (`s_file_run_directly`). Task 1's deferred Minor and the final review's M9: a direct run died with a bare `NameError`.
- **The runner's own hardening**, from Task 3's review and the final review's M7 and M8: SIGTERM, SIGHUP and SIGINT end it with the copy removed; the run's process group is ended with SIGTERM, then SIGKILL three seconds later; stderr is kept for a reason line; a baseline cap of 900 s; a per-run `TMPDIR` inside the copy; a temporary directory under the repository refused; and the group names read from the script's usage error instead of a copy of them. The `status` mutant was moved from `Parser.error` onto the status classifier (M12), and the rules file's `paths:` gained `specs_git_state.py` and `specs_git_lines.py` (M6).

## The release

- **As it happened.** Task 6 read `1.85.0` from `plugins/workflows-core/.claude-plugin/plugin.json` and released 1.85.1 at `cea76e95`. While the fix wave ran, PR #188 merged into `main` as `3016ead8` and took `workflows-core` 1.85.1 for itself. The release implementer merged `origin/main` at `7deeb75c` (the one conflict was the changelog; `main`'s `[1.85.1]` section was kept as `main` has it) and renumbered this branch's section and both manifests to 1.85.2 (the report's *Re-release after main moved*).
- **The manifests.** `git diff origin/main 174af1e6 -- .claude-plugin/marketplace.json plugins/workflows-core/.claude-plugin/plugin.json` changes one line in each, `"version": "1.85.1"` to `"version": "1.85.2"`. `git grep -n '1\.85\.2' 174af1e6` finds three lines: the two manifests and the changelog heading.
- **The changelog.** `## [1.85.2] — 2026-11-13` sits directly above `main`'s `## [1.85.1] — 2026-11-13`. Its opening said `workflows-core` "is updated alone", while 1.85.1 below it says to update with `dev-workflows` 4.64.0; by the ledger's last ruling, `174af1e6` rewords that clause to "so this release needs no other plugin's update beyond what 1.85.1 names", and changes nothing else (`git diff 7deeb75c 174af1e6` is that one line). Before that edit `grep -rn 'updated alone'` over `plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` found that one line, and after it none; the new phrase is found once. `c6eefbaf` rewords one more sentence of the section, in *Added* (the closing review's I3): a marked run "fails before any group runs where it would include the `selftest` group, and on reaching that group where it reaches it by any other route", where it said "fails at once where it would include the `selftest` group or reaches that group by any route"; `git diff 174af1e6 c6eefbaf -- plugins/workflows-core/CHANGELOG.md` is that one line, and under `plugins/` `c6eefbaf` changes nothing else.
- **No coupling bullet.** `.claude/rules/plugin-updates-coupling.md`'s test (line 12): "**A release that relies on another plugin's newer text gets a bullet here** … A batch that changes a `workflows-core` reference a dependent cites adds one". Against `origin/main`, the branch changes under `plugins/` only `specs-git.py`, the changelog and `plugin.json` (`git diff --stat origin/main 174af1e6`), so it changes no reference, relies on no other plugin's text, and no other plugin's text relies on it. `main`'s 1.85.1 bullet stays true beside 1.85.2.

## The gates and the budgets

Which gate steps ran at which commit, each chain one `&&` chain whose own exit value was read:

| Commit | Steps | Result | Source |
|---|---|---|---|
| `cea76e95` | all 32 `run:` steps of `.github/workflows/validate-catalog.yml` as it then stood, in order, with `check-docs.sh --root .` run plainly and with `ASSERT_PUBLISHED=1` | `CHAIN_EXIT=0`, 738 s | Task 6's report |
| `edb40b7f` | `validate-catalog.py --selftest`, `validate-catalog.py`, `check-docs.sh --selftest`, `check-docs.sh --root .` plainly and with `ASSERT_PUBLISHED=1`, `check-id-grammar.sh --root .`, `reference-parts.py check-parts`, `mutants.py --check`, `specs-git.py --selftest` | `CHAIN_EXIT=0` | the fix report |
| `5ae96dae`, `a214c835` | the same, without the selftest | `CHAIN_EXIT=0` at each | the fix report |
| `7deeb75c` | all 33 `run:` steps (step 33, `mutants.py --check`, is this branch's; `main` added none), plus `ASSERT_PUBLISHED=1` `check-docs.sh`, in three chains split at step boundaries (steps 1–12, 13–29, 30–33) | `CHAIN_A_EXIT=0`, `CHAIN_B_EXIT=0`, `CHAIN_C_EXIT=0` | the re-release section of Task 6's report |

The whole workflow, all 33 `run:` steps, last ran at `7deeb75c`; none of the chains in the table was re-run here. What each later commit changes:

| Commit | What it changes |
|---|---|
| `174af1e6` | the changelog's opening clause (*The release*) |
| `0b19e96d` | adds this record |
| `be9d96ec` | this record's gates paragraph |
| `fee02904` | adds the rulings summary and the ledger copy beside this record (the controller's commit) |
| `c6eefbaf` | the closing review's fixes: five `fails` in `scripts/selftests/specs-git-mutants.json`, two sentences of `.claude/rules/specs-git-selftest.md`, the reflow of one paragraph of `scripts/selftests/mutants.py`'s docstring, one sentence of `plugins/workflows-core/CHANGELOG.md` and two of `docs/maintainers/rationale.md` |
| `5062ff6b` | this record's corrections after the closing review |
| `42ad31b2` | one clause of `docs/maintainers/rationale.md`: what the closing fix's two measured times held for, in the words the closing review's re-check gave (the controller's commit) |
| the commits after `42ad31b2` | change only this record and the two files beside it: this record's corrections after that re-check, and any refresh of the ledger copy and the rulings summary |

This record's writer ran the documentation gates as one chain at `0b19e96d`, at `be9d96ec` and at `c6eefbaf`, and the controller ran the same chain at `42ad31b2` with `set -o pipefail`, each time printing `CHAIN_EXIT=0`:

```bash
python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root . && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 -B scripts/selftests/mutants.py --check; echo "CHAIN_EXIT=$?"
```

At `c6eefbaf`, each step's last line, in order: `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: docs are consistent with the plugin(s) under …`, plainly and again with `ASSERT_PUBLISHED=1`; `PASS: no dash-form requirement IDs under .`; `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`; `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`; `mutants: 23 checked, 0 stale`; then `CHAIN_EXIT=0`. At each of the three commits, `node scripts/mermaid/check-mermaid.mjs --root .`, which reads every tracked markdown file, also exited 0: `PASS: all 50 mermaid blocks in 1208 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)` at `c6eefbaf`, and 1206 files at the two before `fee02904`. No other step of the workflow ran at any of the three. The controller runs the chain again at the pushed head and reports it in the pull request, outside this record.

**Budgets** (`LC_ALL=C.UTF-8 wc -m`): `CLAUDE.md` 34,838 at `174af1e6` (34,608 at `origin/main`; this branch adds one table row), under the 36,000-character warning `scripts/validate-catalog.py` sets; `.claude/rules/specs-git-selftest.md`, new, 12,483 at `174af1e6` and 12,857 at `c6eefbaf`, under the 20,000-character rules-file warning; `CLAUDE.md` is 34,838 at `c6eefbaf` too. The plan's Global Constraints keep this batch out of `.claude/rules/gates.md` and `.claude/rules/workflows-core-git.md`, and `git diff --stat origin/main c6eefbaf` lists neither.

## The reviews

Counts are the ledger's and the findings files'; the review reports themselves are not among this record's sources.

| Review | Model | Range | Findings | Disposition |
|---|---|---|---|---|
| Plan review | not in the sources | the plan at `bc817dbe` | no severity counts on record; `6299098a`'s message lists what it changed: the runner runs `python3 -B` on a copy with no `__pycache__` (a same-length mutant restored within a second otherwise stays in force); literal paths and a `cd` in every command; `t_midrun_keyed_other`'s label; a kill line that shows how much of the group failed, and a time limit; the imports and constants only the tests use move with them; the rulings and ledger step | answered in the plan (`6299098a`) and in the design's §9 (`a935c468`) before execution |
| Task 1 | Opus | `80760699..f437dd48` | 0 Critical, 0 Important, 3 Minor; one ⚠️ (test outputs not in the diff), resolved by the controller from the report and the plan review's run | the Minors deferred, then fixed as the final review's M3, M2 and M9 |
| Task 2 | Opus | `f437dd48..440f2e5a` | 0 Critical, 0 Important, 1 Minor (a break in group selection would recurse without bound); one ⚠️ (does a docs page list the usage), resolved by the controller | deferred; became I2 |
| Task 3 | Opus | `440f2e5a..6e1932b2` | 0 Critical, 1 Important (SIGTERM or SIGHUP left the copy and the run's process group behind), 8 Minor | all 9 in fix round 1 (`99e6c18c`) |
| Task 3 re-review | Opus | `6e1932b2..99e6c18c` | 9 of 9 addressed; 0 new Critical or Important; 3 new Minor | deferred; became M7 (a), (b), (c) |
| Task 4 | Opus | `99e6c18c..a89115dc` | 0 Critical, 0 Important, 1 Minor (four `fails` match their whole group) | deferred; became M1 |
| Task 5 | Opus | `a89115dc..87f791f9` | 0 Critical, 2 Important (the rules file said `--list` shows which checks have a mutant; the trigger for running the mutants left out editing a test), 8 Minor; the selftest and mutant times taken from the report (⚠️) | all 10 in fix round 1 (`e505de94`) |
| Task 5 re-review | Opus | `87f791f9..e505de94` | 10 of 10 addressed; 2 new Minor; 1 observation (a partial Read of `specs-git.py` also loaded the `gates*.md` rules) | the Minors became M4 and M5; the observation, ruled by the final review "can stand" |
| Task 6, steps 1–3 | — | `cea76e95` | no task review, by ruling: the final review read the release commit | — |
| Final whole-branch review | Fable 5.2 | `d25e1d89..cea76e95` | ready to merge with fixes: 0 Critical, 3 Important (I1–I3), 13 Minor | M13, an ignored `scripts/selftests/__pycache__/` a reviewer's compile check had left, removed by the controller; I1–I3 and M1–M12 to the fix wave, with the controller's choice where the reviewer offered two (`final-findings.md`) |
| Final fix wave | Opus, resumed from its transcript after the CLI crashed mid-wave | `530ca7cc`, `5a9f1106`, `ee8564f3`, `edb40b7f` | 15 of 15 fixed, two in another form (I2's mutant, M11 wider) | — |
| Its re-review | Fable 5.2 | `cea76e95..edb40b7f` | 15 of 15 addressed; its six departures sound; 0 new Critical or Important; 6 new Minor (N1–N6); 1 out of scope (`cli()` starts its nested runs without `-B`) | N1–N6 fixed in `5ae96dae` and `a214c835`; the out-of-scope item stands by ruling (*Known limits*) |
| Closing review: the closing fixes, the re-release merge, `174af1e6`, this record, the rulings summary and the ledger copy (Task 6's deferred task review) | Opus | `edb40b7f..fee02904` | N1–N6 all fixed; the merge and the release correct; 0 Critical, 4 Important (I1–I4), 5 Minor (M1–M5) (`closing-findings.md`) | eight fixed: I1, I3, M3 and M1's rationale half in `c6eefbaf`; I2, I4, M2, M5 and M1's record half in this record's correction after it; M4, naming 1.85.2 in the pull request, is the controller's. The reviewer's scoped re-check of `fee02904..5062ff6b` found all eight addressed and two Minor of the fix's own, a clause of the rationale and a count in this record's commit table, with the wording for each; the controller applied both as worded (`42ad31b2`, and this record after it) |
| `c6eefbaf` and this record's correction after it | — | after `fee02904` | not reviewed before they were committed | — |

## What departs from the design or the plan

- **A sixteenth group.** The design's §5.1 names "the fifteen `scenarios_*` calls"; the plan's Task 2 added `selftest`, which pins the command line of group runs, and it has two mutants.
- **The check count rose.** The design's §5.1 asks for the same PASS line with the same count as the base; its §9, as `a935c468` corrected it in this pull request, says "unchanged by the move, and rises only by checks of the group runs". The move kept 1,176 (`f437dd48`); the count then rose by Task 2's six, which the plan named, and by the final fix wave's five, which it did not, to 1,187. Of the eleven, `s_selftest_not_shipped`, `s_selftest_unreadable`, `s_selftest_redefines` and `s_file_run_directly` pin the loader and the test file rather than a group run.
- **The mutants were written anew.** The design's §5.1 (since `c9f64227`) and the plan's Task 4 say so: the STAY-2 record's appendix names the check each of its 410 mutants failed and keeps no mutant's edit.
- **23 mutants, not the plan's 22.** The final review's I2 added `selftest_s_group_alone`, on group selection, withdrawing the earlier ruling that kept the `selftest` group's mutant away from selection; its form is `_run_selftest(a.group and a.group + ["selftest"])`, not the finding's `_run_selftest(None)`, which the fix implementer measured reading `TIMEOUT` at the 60-second floor. M12 replaced `status_unknown_subcommand` with `status_rename_original`.
- **The runner departs from the plan's rules** where the final review's fixes reached them: a fresh copy per run instead of one copy restored (rules 1 and 4); `fails` any prefix past the label instead of the label alone; `--list` and `--check` read the group names by running the script's usage error, where the plan said `--list` "runs nothing"; CI runs `--check`, where the plan's Task 5 said CI does not run the runner.
- **The test file's header is a `#` comment block**, not the module docstring the plan's Task 1 step 2 asked for (M3), and its first statement is the direct-run guard (M9).
- **The rules file's `paths:` has four entries**, not the plan's two (M6), and `CLAUDE.md`'s row names all four.
- **Commit trailers.** The plan's Global Constraints name the Fable line or "the implementer's own model line"; by the ledger's first ruling the implementers' commits carry the Opus line.
- **The release** was cut as 1.85.1 and renumbered to 1.85.2 when `main` took 1.85.1; the release commit (`cea76e95`) and this record are separate commits, where the plan's Task 6 step 6 commits them together.
- **The full mutant run** ran here in five invocations, not one (*The mutants*).
- **The gate run at `7deeb75c` was three `&&` chains**, split at step boundaries, where the plan's Task 6 step 3 and `CLAUDE.md` § *Running the gates* ask for one: a single call cannot run that long in this environment.
- **Fix rounds.** Task 3's and Task 5's Minors went into each task's own fix round rather than to the final review, and the re-review's six Minors got a closing commit after the skill's one fix wave, both by the maintainer's fix-all rule as the ledger's rulings record; the closing work is two commits, the second only a rewrap of a CI comment, since no amend was allowed.

## Known limits and what was not examined

- **What a kill shows.** A kill shows that, with that one edit in place, the group's run failed with a failure line starting with the mutant's `fails`: a check whose message begins so caught the edit. It says nothing of any other check. Five mutants' `fails` stopped at a label other checks share — `t-midrun-keyed-other:` 3 checks at run time, `e_midrun_here_kill:` 2, `s_remove:` 3, `g_file:` 2, `k_skill_options:` 10 (nine from one loop) — until `c6eefbaf` tightened each to one of the 1,187 messages a full run checks, all five re-run and killed there. Three `fails` match no message written in the file, so the rules file's grep recipe cannot count what they match: `branch-key: ard/EPIC-008-01_slug with` and `owner-repo: git@github-ig.com:acme/repo.git (alias False) gives`, whose messages are formatted from a row of a loop at run time (test file lines 288 and 430), and `t-midrun-keyed-other: no commit on the branch`, whose label is built from a `name` argument.
- **The first-line guard has no check and no mutant.** The test on `scenarios_selftest`'s first line, which stops a marked run that reaches the `selftest` group by a route the head guard does not see, has as its only evidence the closing fix's scratch-copy run (the fix report's N1: exit 1 in 0.5 s, against exit 124 under `timeout 20` without it). No mutant can reach it, since a mutant's `file` is under `plugins/workflows-core/scripts/` and the guard is in the test file; `s_nested_refused` and `selftest_s_group_alone` reach only the head guard.
- **A check with no mutant** can assert too little in every run and in CI alike. The 23 mutants target 23 of the 1,187 checks; any other check has no mutant.
- **Python 3.11 was not available locally** (`/opt/pyenv/versions/` holds only 3.15.2); CI pins `python-version: "3.11"` (`.github/workflows/validate-catalog.yml:74`) and is the first run on it. No CI run of this branch is part of this record: the branch was not pushed when it was written, so the design's §9 "CI is green" is not shown here.
- **Bytecode after a local run.** The test file's `cli()` starts each nested run as `[sys.executable, script or me, *args]`, without `-B`. After this record's runs at `174af1e6` made with `python3 -B` and no `PYTHONDONTWRITEBYTECODE` (the full run and the per-group count loop), `plugins/workflows-core/scripts/__pycache__/` held `session-branch.cpython-315.pyc`, `specs_git_lines.cpython-315.pyc` and `specs_git_state.cpython-315.pyc`; `.gitignore:14` ignores it, so no commit or install carries it, and it was removed. The ruling lets this stand, since the text is the moved tests' own and the runner sets `PYTHONDONTWRITEBYTECODE=1` for its runs.
- **Not re-derived here:** the signal proofs (Task 3's fix round; the fix report's M7(a)); M7(b), shown only by reading; the runner's refusals of a malformed file, an unknown id, a usage error and a temporary directory under the repository (Task 3); the case of the plan's Task 3 rule 6, a copy that lacks a file the repository has, which no group showed (Task 3's report); the rationale's compile and start-up timings; the extra failure lines of the multi-line mutants; the counts at `440f2e5a`, `edb40b7f` and `5ae96dae`; the gate chains of the table above; the plan review's findings by severity, which are in no source this record had; the closing review's log of the 1,187 messages a full run checks, on which the five tightened `fails` rest, and its 140-second run of a selftest-side break.
- **The copy is narrower than the repository for one check.** `k_no_dollar_session` walks every plugin under `plugins/`, and the runner's copy holds `workflows-core` alone (Task 3's report); no mutant names a file outside `plugins/workflows-core/scripts/`, so no verdict depends on it.
- **The `scripts/**` observation** (a partial Read of `specs-git.py` also loaded the `gates*.md` rules files) predates the branch; the final review ruled it can stand.
- **Timings are one machine's**, in one session (`uptime` gave a load average of 0.21 just before the first run).

## Left for batch 2

- **Most mutants go stale by design.** 21 of the 23 name `plugins/workflows-core/scripts/specs-git.py`, which batch 2 rewrites (the final review's I3; the ledger's ruling on it). There, `python3 scripts/selftests/mutants.py --check` will report each mutant whose `old` text is gone, and CI's step after the selftest fails until each is rewritten against the new text and run.

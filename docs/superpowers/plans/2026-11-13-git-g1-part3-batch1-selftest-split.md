# GIT-G1 Part 3, batch 1 — the selftest out of `specs-git.py` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `specs-git.py`'s built-in test out of the script into a file of its own, with no change to what the script does, let one group of tests run alone, and put on record a mutant for every test group and for the eight checks that have none.

**Architecture:** The test function is moved, byte for byte, into `scripts/selftests/specs_git_selftest.py`, outside the plugin, and `specs-git.py --selftest` executes that file in the script's own namespace. It is executed there and never imported, because the tests reach the script through `globals()` and `__file__`. A small runner applies one-line mutants to a copy of the tree and reports which a group's run catches.

**Tech Stack:** Python 3, standard library only. Git. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-13-git-g1-part3-design.md` §5.1, §9 (*Batch 1*) and §10's first bullet. Its parent is `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md`.

**Base:** branch `feat/git-g1-p3-selftest`, cut from `feat/git-g1-part3` (the design, pull request #187), which stands on `main` at `84527132`. Worktree `/workspace/.worktrees/git-g1-p3-selftest`. Below, the script is `plugins/workflows-core/scripts/specs-git.py` and the test file is `scripts/selftests/specs_git_selftest.py`. Line numbers of the script are at this base.

## Global Constraints

- **The script's non-test code does not change**, beyond what Tasks 1 and 2 name: the loader, the `--group` argument, the usage line and the `--selftest` help text, and the two imports and three constants that only the tests use, which move with them. No subcommand's behaviour, output or exit status changes.
- **Measured on this base:** `python3 plugins/workflows-core/scripts/specs-git.py --selftest` prints `specs-git selftest: PASS (1176 checks)` and takes about 3 minutes 12 seconds. Task 1 must print exactly that line. The plan's reviewer measured about 99 seconds once the tests are out of the script, since each child process no longer compiles them; measure it again wherever a time is written down, and never copy either figure. If the base has moved, re-derive the count on the new base before Task 1 and use that number wherever this plan says 1176.
- **Python 3, standard library only.**
- **Every Bash call begins `cd /workspace/.worktrees/git-g1-p3-selftest &&`.** An agent's shell starts in `/workspace/ai-workflows`, whose `specs-git.py` is the unsplit one: run there, the selftest prints `PASS (1176 checks)` whatever the worktree holds. No shell variable survives from one Bash call to the next, so this plan names literal paths. Never `git checkout` or `git switch` in `/workspace/ai-workflows`. Never a bare `git stash`. Run `git branch --show-current` immediately before every commit; it must print `feat/git-g1-p3-selftest`.
- **Never hard-wrap prose** in a markdown file this plan writes: one paragraph, one line.
- **Sizes:** a rules file stays under 20,000 characters and `CLAUDE.md` under 36,000 (`LC_ALL=C.UTF-8 wc -m`). `.claude/rules/gates.md` is at 19,997 and `.claude/rules/workflows-core-git.md` at 19,960: write nothing into either.
- **`plugins/workflows-core/reference-parts/` is generated** and is not touched.
- **The release version is derived at release time** (Task 6), never taken from this plan.
- **The verification record is written last**, after the final review's fix wave, and every number in it is re-derived on the tree it describes.
- **Two departures from the design's §9, *Each batch*, both corrected there in the same pull request:** the check count is unchanged by the move (Task 1) and rises by the six checks Task 2 adds; and a coupling bullet is written only where `.claude/rules/plugin-updates-coupling.md`'s own test is met, which this release's is not.
- **Commit messages** end with `Co-Authored-By: Claude Fable 5.2 <noreply@anthropic.com>`, or the implementer's own model line where the implementer is another model.

## Review Focus

1. **A check that now passes for the wrong reason.** Three checks read the script's own source: `defined(os.path.abspath(__file__), …)` (line 6995), the `SG_SCRIPT` same-file test (line 7021) and `l_sb_reused` (line 12620). After the move the source they read no longer holds the tests. Task 1 step 5 reads each and records why its meaning is unchanged.
2. **An installed copy.** A plugin cache holds no `scripts/selftests/`. `--selftest` there must print one `specs-git: not run (…)` line and exit 2, never a traceback. Task 2's `s_selftest_not_shipped`.
3. **A partial run read as a full one.** A run with `--group` must never print the line a full run prints, and CI must run with no `--group`. Task 2's `s_group_alone` and `s_ci_runs_all`.
4. **A group that passes only after another has run.** Task 2 step 6 runs each group alone and compares the sum of their counts with the full run's.
5. **A mutant that proves nothing.** One whose `old` text is no longer in the file, one run against a group that is already red, and one left applied in the working tree. Task 3's STALE and BASELINE RED outcomes, and its rule that the runner writes only under a temporary directory.

---

### Task 1: Move the test function into its own file

**Files:**
- Create: `scripts/selftests/specs_git_selftest.py`
- Modify: `plugins/workflows-core/scripts/specs-git.py` (remove lines 5093–18101; add the loader near `main`; lines 5018–5019; the help text at line 4954; the imports and constants step 3 names)

**Interfaces:**
- Produces: `SELFTEST_FILE` (module constant in the script) — `os.path.join(HERE, "..", "..", "..", "scripts", "selftests", "specs_git_selftest.py")`.
- Produces: `_run_selftest() -> int` in the script. Task 2 changes it to `_run_selftest(groups)`.
- Produces: `selftest() -> int`, defined by the test file once executed. Its body is unchanged in this task.

- [ ] **Step 1: Record the baseline.** Run `python3 plugins/workflows-core/scripts/specs-git.py --selftest` and keep its last line. Expected: `specs-git selftest: PASS (1176 checks)`. Save the function's bytes for step 4: `cd /workspace/.worktrees/git-g1-p3-selftest && sed -n '5093,18101p' plugins/workflows-core/scripts/specs-git.py > /tmp/g1p3-selftest-before.py`. Its first line must be `def selftest():` and its last `    return 0`.

- [ ] **Step 2: Create the test file.** It holds a module docstring, then the names of step 3 that only the tests use, then the 13,009 lines saved in step 1, unchanged, then a final newline. The docstring says, in these words or closer ones: this is `specs-git.py`'s selftest; `specs-git.py --selftest` executes this file in that script's own namespace, so every name here that the file does not define is the script's; it is never imported, because the tests read and patch the script through `globals()` and read its source through `__file__`; it lives outside the plugin so that it is not shipped to users.

- [ ] **Step 3: Replace the function in the script with the loader.** Delete lines 5093–18101. In their place write `_run_selftest`, and change line 5019's `return selftest()` to `return _run_selftest()`. Add `SELFTEST_FILE` after `HERE` (line 92). Change the `--selftest` help text at line 4954 to `run the selftest, which the repository keeps under scripts/selftests, and exit`.

  **Move what only the tests use** (the design's "and everything only it uses"). Once the function is out, the script's own code no longer uses `import contextlib`, `import tempfile`, or the constants `SPECS_REPO_GIT`, `ADDRESSING` and `SESSION_HYGIENE` (lines 93–95). Confirm each with `grep -n` on the script after the deletion: a name with a remaining use stays where it is. Move the others to the head of the test file, above `def selftest():`, unchanged. They are executed into the script's namespace, so the tests still find them, and no later clean-up of unused names in the script can break the selftest.

```python
def _run_selftest():
    """The selftest, which lives outside the plugin (SELFTEST_FILE): executed in this module's namespace, since
    its tests reach this script through globals() and __file__. Exit 2 where the file is not there to run."""
    path = os.path.normpath(SELFTEST_FILE)
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        print("specs-git: not run (the selftest is not shipped with the plugin; run it from the repository: "
              "%s is not there)" % path, file=sys.stderr)
        return 2
    scope = globals()
    exec(compile(source, path, "exec"), scope)
    return scope["selftest"]()
```

- [ ] **Step 4: Verify the move.** All three must hold.

```bash
cd /workspace/.worktrees/git-g1-p3-selftest && python3 plugins/workflows-core/scripts/specs-git.py --selftest | tail -1
# Expected: specs-git selftest: PASS (1176 checks)
cd /workspace/.worktrees/git-g1-p3-selftest && tail -n +"$(grep -n '^def selftest():' scripts/selftests/specs_git_selftest.py | cut -d: -f1)" scripts/selftests/specs_git_selftest.py | cmp - /tmp/g1p3-selftest-before.py && echo IDENTICAL
# Expected: IDENTICAL
cd /workspace/.worktrees/git-g1-p3-selftest && grep -c '^def selftest' plugins/workflows-core/scripts/specs-git.py
# Expected: 0
```

- [ ] **Step 5: Read the three checks that read the script's source (Review Focus 1).** For each of `defined(os.path.abspath(__file__), …)`, the `SG_SCRIPT` same-file test and `l_sb_reused`, state in the task report what text it reads, and whether removing the tests from that text changes what the check can catch. If one of them could only have failed on text that has now moved, stop and report it; do not edit the check.

- [ ] **Step 6: Check the run from another directory and from a tree without the file.**

```bash
(cd / && python3 /workspace/.worktrees/git-g1-p3-selftest/plugins/workflows-core/scripts/specs-git.py --selftest | tail -1)
# Expected: specs-git selftest: PASS (1176 checks)
cd /workspace/.worktrees/git-g1-p3-selftest && d="$(mktemp -d)" && mkdir -p "$d/plugins/workflows-core" && cp -r plugins/workflows-core/scripts "$d/plugins/workflows-core/" && { python3 "$d/plugins/workflows-core/scripts/specs-git.py" --selftest; echo "rc=$?"; }
# Expected: one line on stderr beginning "specs-git: not run (the selftest is not shipped with the plugin", then rc=2
```

- [ ] **Step 7: Commit.**

```bash
git branch --show-current
git add scripts/selftests/specs_git_selftest.py plugins/workflows-core/scripts/specs-git.py
git commit -m "refactor(specs-git): the selftest moves to scripts/selftests, executed in the script's namespace"
```

---

### Task 2: Run one group alone

**Files:**
- Modify: `scripts/selftests/specs_git_selftest.py` (the function's signature, its `scenarios()` and its last lines; one new group)
- Modify: `plugins/workflows-core/scripts/specs-git.py` (`_run_selftest`, the `--group` argument, the docstring's usage line 28)

**Interfaces:**
- Consumes: `_run_selftest`, `SELFTEST_FILE` and `selftest` from Task 1.
- Produces: `selftest(groups=None) -> int`. `groups` is `None` for every group, or a list of group names.
- Produces: `_run_selftest(groups)`, and the command line `specs-git.py --selftest [--group <name>]...`.
- Produces: the group names, in run order: `status`, `branch_merged`, `branch_key`, `push_scope`, `owner_repo`, `mode`, `state`, `lines`, `gate`, `end`, `land`, `replay`, `start`, `midrun`, `skill`, `selftest`. The first fifteen are the existing `scenarios_<name>` functions; the last is new.
- Produces: the output lines. A full run prints `specs-git selftest: PASS (<n> checks)`, unchanged. A run with `--group` prints `specs-git selftest: PASS (<n> checks; partial: <names>)`, the names comma-separated in run order whatever order they were given in. A failing run's first line is `specs-git selftest: FAIL`, or `specs-git selftest: FAIL (partial: <names>)`.

- [ ] **Step 1: Write the new group, failing.** Add `scenarios_selftest(tmp)` to the test file, with these six checks. Each nested run names a group other than `selftest`, so the group never runs itself. `ALL` is the sixteen names above, comma-separated.

```python
def scenarios_selftest(tmp):
    """The selftest's own command line: one group alone, the partial line, and the file's absence."""
    got = cli("--selftest", "--group", "branch_key", cwd=tmp)
    check(got["_rc"] == 0 and re.fullmatch(r"specs-git selftest: PASS \([1-9][0-9]* checks; partial: branch_key\)",
                                           got["_stdout"].strip().splitlines()[-1]) is not None,
          "s_group_alone: one group runs alone and says so (%r)" % got)
    got = cli("--selftest", "--group", "owner_repo", "--group", "branch_key", cwd=tmp)
    check(got["_rc"] == 0 and got["_stdout"].strip().endswith("partial: branch_key, owner_repo)"),
          "s_group_order: groups run and are named in the selftest's order (%r)" % got)
    got = cli("--selftest", "--group", "nope")
    check(one_not_run_line(got) and got["_err"].strip() == "specs-git: not run (usage: --group takes one of: %s)" % ALL,
          "s_group_unknown: an unknown group is a usage error naming every group (%r)" % got)
    got = cli("--group", "status")
    check(one_not_run_line(got) and "usage: --group needs --selftest" in got["_err"],
          "s_group_without_selftest: --group alone is a usage error (%r)" % got)
    lone = os.path.join(tmp, "s-lone", "plugins", "workflows-core")
    os.makedirs(lone)
    shutil.copytree(HERE, os.path.join(lone, "scripts"))
    got = cli("--selftest", script=os.path.join(lone, "scripts", "specs-git.py"))
    check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (the selftest is not shipped with the plugin"),
          "s_selftest_not_shipped: a tree without the selftest file says so in one line (%r)" % got)
    ci = os.path.join(HERE, "..", "..", "..", ".github", "workflows", "validate-catalog.yml")
    with open(ci, encoding="utf-8") as fh:
        runs = [line.strip() for line in fh if line.strip().startswith("run:") and "specs-git.py" in line]
    check(runs == ["run: python3 plugins/workflows-core/scripts/specs-git.py --selftest"],
          "s_ci_runs_all: CI runs the whole selftest, with no --group (%r)" % runs)
```

`parsed()` sets `_stdout` only where stdout is not JSON, which a selftest's output never is; where the helper's keys differ from this sketch, use the helper as it is and keep the six check labels and what each asserts.

- [ ] **Step 2: Run it to see it fail.** Call `scenarios_selftest(tmp)` last in `scenarios()`, then run `cd /workspace/.worktrees/git-g1-p3-selftest && python3 plugins/workflows-core/scripts/specs-git.py --selftest | head -8`. Expected: `specs-git selftest: FAIL`, with `s_group_alone`, `s_group_order`, `s_group_unknown` and `s_group_without_selftest` among the failures. `s_selftest_not_shipped` and `s_ci_runs_all` already pass on Task 1's code; say so in the report.

- [ ] **Step 3: Implement group selection in the test file.** `selftest(groups=None)`. Replace the body of `scenarios()` with a loop over one ordered table of `(name, function)` pairs, the sixteen above, run where `groups is None or name in groups`. Before running anything, where `groups` holds a name the table lacks, print `specs-git: not run (usage: --group takes one of: <ALL>)` on stderr and return 2. The last lines print the partial forms of the Interfaces block where `groups` is not `None`. A full run's two lines are unchanged.

- [ ] **Step 4: Implement the argument in the script.** `ap.add_argument("--group", action="append", metavar="NAME", help="with --selftest: run only this group; repeatable")` beside `--selftest` (line 4954). In `main`, before the `a.selftest` test: where `a.group` is set and `a.selftest` is not, `ap.error("--group needs --selftest")`. `_run_selftest(groups)` passes `a.group` through to `selftest(groups)`. Change the docstring's line 28 to `  specs-git.py --selftest [--group <name>]...`.

- [ ] **Step 5: Run the whole selftest.** `cd /workspace/.worktrees/git-g1-p3-selftest && python3 plugins/workflows-core/scripts/specs-git.py --selftest | tail -1`. Expected: `specs-git selftest: PASS (1182 checks)`, the 1176 of Task 1 and the six new ones.

- [ ] **Step 6: Run each group alone (Review Focus 4).**

```bash
cd /workspace/.worktrees/git-g1-p3-selftest && total=0
for g in status branch_merged branch_key push_scope owner_repo mode state lines gate end land replay start midrun skill selftest; do
  line="$(python3 plugins/workflows-core/scripts/specs-git.py --selftest --group "$g" | tail -1)"
  echo "$g: $line"
  n="$(printf '%s' "$line" | sed -n 's/^specs-git selftest: PASS (\([0-9]*\) checks; partial: .*/\1/p')"
  total=$((total + ${n:-0}))
done
echo "sum=$total"
# Expected: sixteen PASS lines, each naming its own group, and sum=1182 (the plan's reviewer got: status 11, branch_merged 12, branch_key 13, push_scope 11, owner_repo 16, mode 86, state 70, lines 105, gate 57, end 211, land 124, replay 106, start 172, midrun 135, skill 47, selftest 6)
```

Put the sixteen lines and the time each took in the task report. A group that fails alone leans on an earlier group's leftovers: make it build what it needs through a helper the two share, never by reordering the table and never by having `--group` run a second group. If the fix is not a few lines, stop and report.

- [ ] **Step 7: Commit.**

```bash
git branch --show-current
git add scripts/selftests/specs_git_selftest.py plugins/workflows-core/scripts/specs-git.py
git commit -m "feat(specs-git): --selftest --group runs one group of the selftest alone"
```

---

### Task 3: The mutant runner

**Files:**
- Create: `scripts/selftests/mutants.py`
- Create: `scripts/selftests/specs-git-mutants.json` (an empty list, `[]`, until Task 4)

**Interfaces:**
- Consumes: `specs-git.py --selftest --group <name>` and its output lines, from Task 2.
- Produces: `python3 scripts/selftests/mutants.py [--only <id>]... [--list] [--file <mutants file>]`; `--file` defaults to `scripts/selftests/specs-git-mutants.json`.
- Produces: the mutants file, a JSON list of objects with exactly these keys: `id` (unique), `group` (one of Task 2's sixteen names), `file` (a path under `plugins/workflows-core/scripts/`, relative to the repository root), `old` and `new` (each one line of text, with no newline), and `fails` (the label of the check it must fail, up to and including its colon, such as `e_land_refused:`).

**What the runner does:**

1. It copies `plugins/workflows-core/`, `scripts/selftests/` and `.github/workflows/validate-catalog.yml` into a new temporary directory, at the same relative paths, leaving out every `__pycache__` directory. Everything it then writes or runs is in that copy. **It never writes under the repository.**
2. **Every run is `python3 -B`, with `PYTHONDONTWRITEBYTECODE=1` in its environment.** The script loads its three sibling modules through `importlib`, whose cached bytecode is keyed on the source's size and its modification time in whole seconds. A mutant of the same length as the text it replaces, applied and restored within one second, would otherwise stay in force after the file is restored, and every later run in the copy would carry it. The plan's reviewer reproduced this.
3. For each group that a selected mutant names, it runs the group once in the unchanged copy and keeps how long that took. Where that run does not end in a PASS line, it prints `BASELINE RED <group>` and counts every mutant of the group as on a red baseline.
4. For each selected mutant, it counts `old` in the copy of `file`. Where the count is not exactly 1, it prints `STALE <id>: old text found <n> times in <file>`. Otherwise it replaces `old` with `new`, runs the mutant's group with a time limit of ten times the group's baseline and never under 60 seconds, and restores the file. A run stopped at the limit prints `TIMEOUT <id>`.
5. A mutant is **killed** where the run exits 1 and an output line, stripped, starts with `fails`: it prints `killed <id> (<f> failure lines): <that line, cut at 160 characters>`, `<f>` being the number of failure lines the run printed, so a mutant that fails most of its group shows as one. Otherwise it prints `SURVIVED <id>`. **A case that crashes is not a kill**: the selftest's `case()` wrappers print `<name> crashed: …`, which does not start with `<name>:`, and the match is not to be widened to take it. A mutant should make its check fail, not make its case raise.
6. Where a group's baseline is red in the copy and green in the repository, the copy lacks a file that group reads: add that path to what rule 1 copies, and say so in the task report. The plan's reviewer found the three paths enough for all sixteen groups.
7. Its last line is `mutants: <k> killed, <s> survived, <t> stale, <o> timed out, <r> on a red baseline, of <n>`. It exits 0 only where every selected mutant was killed; a malformed mutants file, or an `--only` id the file lacks, is one line on stderr and exit 2.

- [ ] **Step 1: Write the runner** to the seven rules above. `--list` prints each mutant's `id`, `group` and `fails`, one per line, and runs nothing.

- [ ] **Step 2: Prove it can tell a kill from a survival (Review Focus 5).** With a scratch mutants file outside the repository, passed with `--file`, run four mutants:
  - one that changes what `branch_key` computes, against group `branch_key`, with `fails` naming a check of that group it breaks. Expected: `killed`.
  - one whose `new` only appends a comment to a line of the script, against `branch_key`. Expected: `SURVIVED`, exit 1.
  - one whose `old` is text the file does not hold. Expected: `STALE`, exit 1.
  - one in `specs_git_state.py` whose `old` and `new` are the same length, such as `VERSION = 1` to `VERSION = 2`, against group `state`, followed in the same run by the comment-only mutant against `state`. Expected: the first `killed`, the second `SURVIVED`. This is rule 2's case: without it the second reads `killed` by the first one's leftover.

  Put the output lines in the task report. Then run `git status --short` in the worktree. Expected: only the two new files of this task.

- [ ] **Step 3: Commit.**

```bash
git branch --show-current
git add scripts/selftests/mutants.py scripts/selftests/specs-git-mutants.json
git commit -m "test(specs-git): a runner for one-line mutants, on a copy of the tree"
```

---

### Task 4: The mutants

**Files:**
- Modify: `scripts/selftests/specs-git-mutants.json`

**Interfaces:**
- Consumes: the runner and the file format of Task 3.
- Produces: 22 mutants, every one killed.

**Why they are written anew.** The earlier records list each mutant by the check it failed and do not hold its text (`docs/superpowers/verification/2026-11-10-stay2-midrun.md`, *Appendix: the mutants*: "applied in a scratch copy, run, and discarded"). So the design's "take each mutant from the appendix" can supply a target check, never the edit. This file is where the edits are kept from now on.

- [ ] **Step 1: Write the eight mutants the STAY-2 record says are missing.** One each, its `id` the check's own name: `e_land_refused`, `e_land_stopped`, `e_land_offline`, `e_land_no_origin`, `t_held_journal` (all in group `end`), and `t_midrun_keyed_other`, `e_midrun_here_kill`, `e_midrun_here_no_resume` (group `midrun`). `fails` is that name and a colon, which no longer-named neighbour's line starts with, save for `t_midrun_keyed_other` (step 2). Each changes one line of non-test code that the check exercises, such as a condition inverted, and makes the check fail, not its case raise. None is a line whose change fails most of its group: the runner's `(<f> failure lines)` shows it, against the group's size in Task 2 step 6.

- [ ] **Step 2: `t_midrun_keyed_other` must fail on its own case.** It runs the body of `t_midrun_keyless` with `/create-ard` and `--key ACME-2` (the `case("t_midrun_keyed_other", …)` line of the test file). That body labels its checks with the name it is passed, `t-midrun-keyed-other`, with hyphens, so this mutant's `fails` is `t-midrun-keyed-other:`. It must fail that case while the keyless case passes: a change on the path only a keyed run takes. Run `--selftest --group midrun` in a scratch copy with the mutant applied and put its failure lines in the task report; none may start `t-midrun-keyless:`. No edit of the test file is needed for this.

- [ ] **Step 3: Write one mutant for each of the other fourteen groups:** `status`, `branch_merged`, `branch_key`, `push_scope`, `owner_repo`, `mode`, `state`, `lines`, `gate`, `land`, `replay`, `start`, `skill` and `selftest`. Choose any check of the group as the target; `id` is `<group>_<the check's name>`. The `selftest` group's mutant is in `_run_selftest` or the `--group` handling.

- [ ] **Step 4: Run them all.** `python3 scripts/selftests/mutants.py`. Expected last line: `mutants: 22 killed, 0 survived, 0 stale, 0 timed out, 0 on a red baseline, of 22`, exit 0. Put the full output in the task report. Then `git status --short`: only the mutants file.

- [ ] **Step 5: Commit.**

```bash
git branch --show-current
git add scripts/selftests/specs-git-mutants.json
git commit -m "test(specs-git): a mutant for every selftest group and for the eight checks that had none"
```

---

### Task 5: The rule, its reason, and the CI comment

**Files:**
- Create: `.claude/rules/specs-git-selftest.md`
- Modify: `CLAUDE.md` (one row in the table of § *Where the rest of the guidance lives*)
- Modify: `docs/maintainers/rationale.md` (one new section, anchor `specs-git-selftest`)
- Modify: `.github/workflows/validate-catalog.yml` (the comment above the `specs-git.py --selftest` step; the `run:` line is not changed)

**Interfaces:**
- Consumes: the paths, the command line and the output lines of Tasks 1 to 4, as built. Read them from the tree, not from this plan.

- [ ] **Step 1: Write the rules file.** Frontmatter `paths:` as a block list of two entries: `scripts/selftests/**` and `plugins/workflows-core/scripts/specs-git.py`. Body, each point verified against the tree as it is written:
  - where the selftest lives, and that `specs-git.py --selftest` is still the one command CI runs;
  - **that the file is executed in the script's namespace and never imported, and why**: its tests read and patch the script through `globals()` and read its source through `__file__`, so a module of its own would patch a copy and pass without testing anything;
  - that an installed plugin holds no selftest, and what `--selftest` prints there;
  - `--group`, the sixteen names by a command that prints them rather than a count, and that a run with `--group` prints `partial:` and is never evidence that the selftest passes;
  - the mutants file and the runner: what a mutant is, the three outcomes besides `killed`, that the runner works on a copy, and that CI does not run it, since it takes minutes;
  - **what none of this can see:** a check that asserts too little is caught only where a mutant was written for it; `python3 scripts/selftests/mutants.py --list` prints which checks have one, and no count is written in the rules file;
  - **which rules load with the tests:** reading a file under `scripts/selftests/` loads the `gates*.md` rules and not the specs-repo git rules, which loaded with the tests while they were in the script. Tell the reader to Read `plugins/workflows-core/scripts/specs-git.py` before editing a test, which loads `.claude/rules/workflows-core-git.md` and its companions;
  - how long a full run and each group take, measured, with the command that measures them;
  - a `why` link to the rationale section of step 3.

- [ ] **Step 2: Add the row to `CLAUDE.md`'s table.** `specs-git-selftest.md`, its two paths in the table's abbreviated form, the first marked `(repo root)` as `gates.md`'s row marks its own, and "where `specs-git.py`'s selftest lives, how it runs, group runs, the mutants". Then `LC_ALL=C.UTF-8 wc -m CLAUDE.md`. Expected: under 36,000.

- [ ] **Step 3: Write the rationale section**, headed so its anchor is `specs-git-selftest`. It holds the evidence: the script was 18,105 lines of which 13,009 were the test function; the run's time before and after the move, both measured; that the 410 mutants of the STAY-2 batch were discarded with their workspace and survive only as the names of the checks they failed; and why outside the plugin (the size of the file, re-measured with `wc -c`, shipped to every user for a command no user runs).

- [ ] **Step 4: Update the CI comment.** Add to the comment above the step that the tests are in `scripts/selftests/specs_git_selftest.py`, which the script executes, and that the step runs every group. Leave the `run:` line as it is: `s_ci_runs_all` reads it.

- [ ] **Step 5: Run the gates that read these files.**

```bash
python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py
./scripts/check-docs.sh --root .
python3 plugins/workflows-core/scripts/specs-git.py --selftest --group selftest | tail -1
# Expected: 0 error(s) from validate-catalog; check-docs PASS; the selftest group PASS (s_ci_runs_all reads the yml)
```

- [ ] **Step 6: Commit.**

```bash
git branch --show-current
git add .claude/rules/specs-git-selftest.md CLAUDE.md docs/maintainers/rationale.md .github/workflows/validate-catalog.yml
git commit -m "docs: where specs-git.py's selftest lives, how it runs, and why"
```

---

### Task 6: Release, the gate chain and the record

**Files:**
- Modify: `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (the `workflows-core` entry's version), `plugins/workflows-core/CHANGELOG.md`
- Create: `docs/superpowers/verification/<today>-git-g1-part3-batch1.md`

**Interfaces:**
- Consumes: everything above, and the final whole-branch review's fix wave, which comes before step 4.

- [ ] **Step 1: Derive the version.** Merge or rebase onto `origin/main` first if it has moved, and re-run the whole selftest. Read `version` from `plugins/workflows-core/.claude-plugin/plugin.json` as it then stands and take the next patch. Write it to both manifests. Do not edit `.claude-plugin/marketplace.json` beyond that one value.

- [ ] **Step 2: Write the changelog section**, dated today, under that version. *Changed*: `specs-git.py` no longer carries its selftest, which the repository keeps under `scripts/selftests/`; an installed copy's `--selftest` prints one `not run` line. *Added*: `--selftest --group`. State that no command's behaviour changes. Read `.claude/rules/plugin-updates-coupling.md` (the Read tool, so the rules load): write a coupling bullet only where its test is met, which this release's is not, since no other plugin's text relies on it.

- [ ] **Step 3: Run the gate chain** as one `&&` chain, in the order of `.github/workflows/validate-catalog.yml`'s `run:` steps, and read the chain's own exit status. Expected: 0. The mermaid gate needs `npm ci` in `scripts/mermaid/` first.

- [ ] **Step 4: Write the verification record, last.** After the final review and its fixes. It holds, each re-derived on the final tree: the check count at the base, at Task 1's commit (unchanged) and at the end, with the six added checks named; the byte comparison of Task 1 step 4; Task 1 step 5's reading of the three source-reading checks; the sixteen single-group lines, their times and their sum; the runner's three proof lines of Task 3; the full output of the 22 mutants; the script's size before and after (`wc -l`, `wc -c`); the gate chain's exit status; the reviews and what each found; and what was not examined.

- [ ] **Step 5: The rulings and the ledger (the controller's step).** Before the execution workspace is removed, the controller commits a summary of the rulings it made during execution and the ledger, verbatim, to `docs/superpowers/verification/`, beside the record.

- [ ] **Step 6: Commit, push, open the pull request.**

```bash
git branch --show-current
git add -A plugins/workflows-core/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/workflows-core/CHANGELOG.md docs/superpowers/verification
git commit -m "release(workflows-core): the selftest out of specs-git.py; the batch's verification record"
git push -u origin feat/git-g1-p3-selftest
```

The pull request's base is `main` if #187 has merged, else `feat/git-g1-part3`. Merging is the maintainer's.

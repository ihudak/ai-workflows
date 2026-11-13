# GIT-G1 Part 3, batch 1 — the selftest out of `specs-git.py` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `specs-git.py`'s built-in test out of the script into a file of its own, with no change to what the script does, let one group of tests run alone, and put on record a mutant for every test group and for the eight checks that have none.

**Architecture:** The test function is moved, byte for byte, into `scripts/selftests/specs_git_selftest.py`, outside the plugin, and `specs-git.py --selftest` executes that file in the script's own namespace. It is executed there and never imported, because the tests reach the script through `globals()` and `__file__`. A small runner applies one-line mutants to a copy of the tree and reports which a group's run catches.

**Tech Stack:** Python 3, standard library only. Git. No new dependency.

**Spec:** `docs/superpowers/specs/2026-11-13-git-g1-part3-design.md` §5.1, §9 (*Batch 1*) and §10's first bullet. Its parent is `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md`.

**Base:** branch `feat/git-g1-p3-selftest`, cut from `feat/git-g1-part3` (the design, pull request #187), which stands on `main` at `84527132`. Worktree `/workspace/.worktrees/git-g1-p3-selftest`. Below, the script is `plugins/workflows-core/scripts/specs-git.py` and the test file is `scripts/selftests/specs_git_selftest.py`. Line numbers of the script are at this base.

## Global Constraints

- **The script's non-test code does not change**, beyond the loader, the `--group` argument and one usage line that Tasks 1 and 2 name. No subcommand's behaviour, output or exit status changes.
- **Measured on this base:** `python3 plugins/workflows-core/scripts/specs-git.py --selftest` prints `specs-git selftest: PASS (1176 checks)` and takes about 3 minutes 12 seconds. Task 1 must print exactly that line. If the base has moved, re-derive the count on the new base before Task 1 and use that number wherever this plan says 1176.
- **Python 3, standard library only.**
- **Every command runs in the worktree**, `/workspace/.worktrees/git-g1-p3-selftest`. Never `git checkout` or `git switch` in `/workspace/ai-workflows`. Never a bare `git stash`. Run `git branch --show-current` immediately before every commit; it must print `feat/git-g1-p3-selftest`.
- **Never hard-wrap prose** in a markdown file this plan writes: one paragraph, one line.
- **Sizes:** a rules file stays under 20,000 characters and `CLAUDE.md` under 36,000 (`LC_ALL=C.UTF-8 wc -m`). `.claude/rules/gates.md` is at 19,997 and `.claude/rules/workflows-core-git.md` at 19,960: write nothing into either.
- **`plugins/workflows-core/reference-parts/` is generated** and is not touched.
- **The release version is derived at release time** (Task 6), never taken from this plan.
- **The verification record is written last**, after the final review's fix wave, and every number in it is re-derived on the tree it describes.
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
- Modify: `plugins/workflows-core/scripts/specs-git.py` (remove lines 5093–18101; add the loader near `main`; lines 5018–5019)

**Interfaces:**
- Produces: `SELFTEST_FILE` (module constant in the script) — `os.path.join(HERE, "..", "..", "..", "scripts", "selftests", "specs_git_selftest.py")`.
- Produces: `_run_selftest() -> int` in the script. Task 2 changes it to `_run_selftest(groups)`.
- Produces: `selftest() -> int`, defined by the test file once executed. Its body is unchanged in this task.

- [ ] **Step 1: Record the baseline.** Run `python3 plugins/workflows-core/scripts/specs-git.py --selftest` and keep its last line. Expected: `specs-git selftest: PASS (1176 checks)`. Save the function's bytes for step 4: `sed -n '5093,18101p' plugins/workflows-core/scripts/specs-git.py > "$TMPDIR/selftest-before.py"`. Its first line must be `def selftest():` and its last `    return 0`.

- [ ] **Step 2: Create the test file.** It holds a module docstring, one blank line, then the 13,009 lines saved in step 1, unchanged, then a final newline. The docstring says, in these words or closer ones: this is `specs-git.py`'s selftest; `specs-git.py --selftest` executes this file in that script's own namespace, so every name here that the file does not define is the script's; it is never imported, because the tests read and patch the script through `globals()` and read its source through `__file__`; it lives outside the plugin so that it is not shipped to users.

- [ ] **Step 3: Replace the function in the script with the loader.** Delete lines 5093–18101. In their place write `_run_selftest`, and change line 5019's `return selftest()` to `return _run_selftest()`. Add `SELFTEST_FILE` beside the script's other path constants (line 93).

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
python3 plugins/workflows-core/scripts/specs-git.py --selftest | tail -1
# Expected: specs-git selftest: PASS (1176 checks)
tail -n +"$(grep -n '^def selftest():' scripts/selftests/specs_git_selftest.py | cut -d: -f1)" scripts/selftests/specs_git_selftest.py | cmp - "$TMPDIR/selftest-before.py" && echo IDENTICAL
# Expected: IDENTICAL
grep -c '^def selftest' plugins/workflows-core/scripts/specs-git.py
# Expected: 0
```

- [ ] **Step 5: Read the three checks that read the script's source (Review Focus 1).** For each of `defined(os.path.abspath(__file__), …)`, the `SG_SCRIPT` same-file test and `l_sb_reused`, state in the task report what text it reads, and whether removing the tests from that text changes what the check can catch. If one of them could only have failed on text that has now moved, stop and report it; do not edit the check.

- [ ] **Step 6: Check the run from another directory and from a tree without the file.**

```bash
(cd / && python3 /workspace/.worktrees/git-g1-p3-selftest/plugins/workflows-core/scripts/specs-git.py --selftest | tail -1)
# Expected: specs-git selftest: PASS (1176 checks)
d="$(mktemp -d)"; mkdir -p "$d/plugins/workflows-core"; cp -r plugins/workflows-core/scripts "$d/plugins/workflows-core/"
python3 "$d/plugins/workflows-core/scripts/specs-git.py" --selftest; echo "rc=$?"
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

- [ ] **Step 2: Run it to see it fail.** Call `scenarios_selftest(tmp)` last in `scenarios()`, then run `python3 plugins/workflows-core/scripts/specs-git.py --selftest | head -8`. Expected: `specs-git selftest: FAIL`, with `s_group_alone`, `s_group_order`, `s_group_unknown` and `s_group_without_selftest` among the failures. `s_selftest_not_shipped` and `s_ci_runs_all` already pass on Task 1's code; say so in the report.

- [ ] **Step 3: Implement group selection in the test file.** `selftest(groups=None)`. Replace the body of `scenarios()` with a loop over one ordered table of `(name, function)` pairs, the sixteen above, run where `groups is None or name in groups`. Before running anything, where `groups` holds a name the table lacks, print `specs-git: not run (usage: --group takes one of: <ALL>)` on stderr and return 2. The last lines print the partial forms of the Interfaces block where `groups` is not `None`. A full run's two lines are unchanged.

- [ ] **Step 4: Implement the argument in the script.** `ap.add_argument("--group", action="append", metavar="NAME", help="with --selftest: run only this group; repeatable")` beside `--selftest` (line 4954). In `main`, before the `a.selftest` test: where `a.group` is set and `a.selftest` is not, `ap.error("--group needs --selftest")`. `_run_selftest(groups)` passes `a.group` through to `selftest(groups)`. Change the docstring's line 28 to `  specs-git.py --selftest [--group <name>]...`.

- [ ] **Step 5: Run the whole selftest.** `python3 plugins/workflows-core/scripts/specs-git.py --selftest | tail -1`. Expected: `specs-git selftest: PASS (1182 checks)`, the 1176 of Task 1 and the six new ones.

- [ ] **Step 6: Run each group alone (Review Focus 4).**

```bash
total=0
for g in status branch_merged branch_key push_scope owner_repo mode state lines gate end land replay start midrun skill selftest; do
  line="$(python3 plugins/workflows-core/scripts/specs-git.py --selftest --group "$g" | tail -1)"
  echo "$g: $line"
  n="$(printf '%s' "$line" | sed -n 's/^specs-git selftest: PASS (\([0-9]*\) checks; partial: .*/\1/p')"
  total=$((total + ${n:-0}))
done
echo "sum=$total"
# Expected: sixteen PASS lines, each naming its own group, and sum=1182
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
- Produces: `python3 scripts/selftests/mutants.py [--only <id>]... [--list]`.
- Produces: the mutants file, a JSON list of objects with exactly these keys: `id` (unique), `group` (one of Task 2's sixteen names), `file` (a path under `plugins/workflows-core/scripts/`, relative to the repository root), `old` and `new` (each one line of text, with no newline), and `fails` (the label of the check it must fail, up to and including its colon, such as `e_land_refused:`).

**What the runner does:**

1. It copies `plugins/workflows-core/`, `scripts/selftests/` and `.github/workflows/validate-catalog.yml` into a new temporary directory, at the same relative paths. Everything it then writes or runs is in that copy. **It never writes under the repository.**
2. For each group that a selected mutant names, it runs the group once in the unchanged copy. Where that run does not end in a PASS line, it prints `BASELINE RED <group>` and counts every mutant of the group as not killed.
3. For each selected mutant, it counts `old` in the copy of `file`. Where the count is not exactly 1, it prints `STALE <id>: old text found <n> times in <file>`. Otherwise it replaces `old` with `new`, runs the mutant's group, and restores the file.
4. A mutant is **killed** where the run exits 1 and an output line, stripped, starts with `fails`: it prints `killed <id>: <that line, cut at 160 characters>`. Otherwise it prints `SURVIVED <id>`.
5. Where a group's baseline is red in the copy and green in the repository, the copy lacks a file that group reads: add that path to what step 1 copies, and say so in the task report.
6. Its last line is `mutants: <k> killed, <s> survived, <t> stale, of <n>`. It exits 0 only where every selected mutant was killed; a malformed mutants file, or an `--only` id the file lacks, is one line on stderr and exit 2.

- [ ] **Step 1: Write the runner** to the six rules above. `--list` prints each mutant's `id`, `group` and `fails`, one per line, and runs nothing.

- [ ] **Step 2: Prove it can tell a kill from a survival (Review Focus 5).** With a scratch mutants file passed in place of the real one (give the runner a `--file <path>` option for this, defaulting to `scripts/selftests/specs-git-mutants.json`), run three mutants against group `branch_key`:
  - one that changes what `branch_key` computes, with `fails` naming a `branch_key` check it breaks. Expected: `killed`.
  - one whose `new` only appends a comment to a line of the script. Expected: `SURVIVED`, exit 1.
  - one whose `old` is text the file does not hold. Expected: `STALE`, exit 1.

  Put the three output lines in the task report. Then run `git status --short` in the worktree. Expected: only the two new files of this task.

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
- Modify, only if step 2 needs it: `scripts/selftests/specs_git_selftest.py`

**Interfaces:**
- Consumes: the runner and the file format of Task 3.
- Produces: 22 mutants, every one killed.

**Why they are written anew.** The earlier records list each mutant by the check it failed and do not hold its text (`docs/superpowers/verification/2026-11-10-stay2-midrun.md`, *Appendix: the mutants*: "applied in a scratch copy, run, and discarded"). So the design's "take each mutant from the appendix" can supply a target check, never the edit. This file is where the edits are kept from now on.

- [ ] **Step 1: Write the eight mutants the STAY-2 record says are missing.** One each, its `id` and `fails` the check's own name: `e_land_refused`, `e_land_stopped`, `e_land_offline`, `e_land_no_origin`, `t_held_journal` (all in group `end`), and `t_midrun_keyed_other`, `e_midrun_here_kill`, `e_midrun_here_no_resume` (group `midrun`). Each changes one line of non-test code that the check exercises, such as a condition inverted or a call dropped, and is not a line whose change fails most of its group.

- [ ] **Step 2: `t_midrun_keyed_other` must fail on its own case.** It runs the body of `t_midrun_keyless` with `/create-ard` and `--key ACME-2` (test file, the `case("t_midrun_keyed_other", …)` line). Its mutant must fail that case while `t_midrun_keyless` itself passes: a change on the path only a keyed run takes. Where the shared body's check lines do not carry the case's name, first make them carry it, so the runner can tell the two apart. That edit changes no check's count: run the whole selftest after it and expect `PASS (1182 checks)`.

- [ ] **Step 3: Write one mutant for each of the other fourteen groups:** `status`, `branch_merged`, `branch_key`, `push_scope`, `owner_repo`, `mode`, `state`, `lines`, `gate`, `land`, `replay`, `start`, `skill` and `selftest`. Choose any check of the group as the target; `id` is `<group>_<the check's name>`. The `selftest` group's mutant is in `_run_selftest` or the `--group` handling.

- [ ] **Step 4: Run them all.** `python3 scripts/selftests/mutants.py`. Expected last line: `mutants: 22 killed, 0 survived, 0 stale, of 22`, exit 0. Put the full output in the task report. Then `git status --short`: only the mutants file, and the test file if step 2 edited it.

- [ ] **Step 5: Commit.**

```bash
git branch --show-current
git add scripts/selftests/specs-git-mutants.json scripts/selftests/specs_git_selftest.py
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
  - **what none of this can see:** a check that asserts too little is caught only where a mutant was written for it, and 22 mutants cover 22 checks;
  - a `why` link to the rationale section of step 3.

- [ ] **Step 2: Add the row to `CLAUDE.md`'s table.** `specs-git-selftest.md`, its two paths in the table's abbreviated form, and "where `specs-git.py`'s selftest lives, how it runs, group runs, the mutants". Then `LC_ALL=C.UTF-8 wc -m CLAUDE.md`. Expected: under 36,000.

- [ ] **Step 3: Write the rationale section**, headed so its anchor is `specs-git-selftest`. It holds the evidence: the script was 18,105 lines of which 13,009 were the test function; the three-minute run; that the 410 mutants of the STAY-2 batch were discarded with their workspace and survive only as the names of the checks they failed; and why outside the plugin (the size of the file, re-measured with `wc -c`, shipped to every user for a command no user runs).

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

- [ ] **Step 4: Write the verification record, last.** After the final review and its fixes. It holds, each re-derived on the final tree: the check count before and after, with the six added checks named; the byte comparison of Task 1 step 4; Task 1 step 5's reading of the three source-reading checks; the sixteen single-group lines, their times and their sum; the runner's three proof lines of Task 3; the full output of the 22 mutants; the script's size before and after (`wc -l`, `wc -c`); the gate chain's exit status; the reviews and what each found; and what was not examined.

- [ ] **Step 5: Commit, push, open the pull request.**

```bash
git branch --show-current
git add -A plugins/workflows-core/.claude-plugin/plugin.json .claude-plugin/marketplace.json plugins/workflows-core/CHANGELOG.md docs/superpowers/verification
git commit -m "release(workflows-core): the selftest out of specs-git.py; the batch's verification record"
git push -u origin feat/git-g1-p3-selftest
```

The pull request's base is `main` if #187 has merged, else `feat/git-g1-part3`. Merging is the maintainer's.

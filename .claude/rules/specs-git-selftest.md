---
paths:
  - "scripts/selftests/**"
  - "plugins/workflows-core/scripts/specs-git.py"
---

# `specs-git.py`'s selftest — where it lives, how it runs, the mutants

Loaded when a file under `scripts/selftests/`, or `plugins/workflows-core/scripts/specs-git.py`, is read with the Read tool. Repo-wide rules are in `CLAUDE.md`; the specs-repo git authorities the script implements are in `.claude/rules/workflows-core-git.md` and its companions; evidence is in `docs/maintainers/rationale.md`.

## Where it lives

The selftest of `plugins/workflows-core/scripts/specs-git.py` is `scripts/selftests/specs_git_selftest.py`, outside the plugin, and `python3 plugins/workflows-core/scripts/specs-git.py --selftest` is still the command that runs it and the one CI runs: `.github/workflows/validate-catalog.yml`'s step for the script runs exactly that line, and the selftest's own `s_ci_runs_all` fails where that `run:` line changes at all, a `--group` added included. ([why](../../docs/maintainers/rationale.md#specs-git-selftest))

**The file is executed in the script's namespace and never imported.** `--selftest` calls the script's `_run_selftest`, which reads the file at `SELFTEST_FILE`, runs it with `exec` in the script's own `globals()` and calls the `selftest()` it defines. So every name the file uses and does not define is the script's, and a top-level name the file defines replaces the script's of that name: define none the script has. It is never imported because its tests read and patch the script through `globals()` (`g = globals()`, then `g["push_check"] = broken`) and reach the script through `__file__`, both to read its source and as the program `cli()` runs as a child process. Made a module of its own that imported the script's names, it would assign each patch into its own namespace, which the script's functions never read, and its `__file__` would name the test file: a check built on a patch would run the unpatched script, so its result, pass or fail, would say nothing about the case it names.

**An installed plugin holds no selftest**, in any release whose script defines `SELFTEST_FILE`; an earlier one still carries `selftest()` in the script. The file is outside `plugins/workflows-core/`, so the copy an install keeps under `~/.claude/plugins/cache/<marketplace>/workflows-core/<version>/` has none, and `--selftest` run there prints one line on stderr, `specs-git: not run (the selftest is not shipped with the plugin; run it from the repository: <path> is not there)`, and exits 2; the selftest's `s_selftest_not_shipped` checks that line's start. Run the selftest from a checkout of this repository.

## One group alone

`--selftest --group <name>` runs only that group, and `--group` may be repeated: the named groups run in the selftest's own order, whatever order they are named in. An unknown name is a usage error naming every group, and `--group` without `--selftest` is a usage error too. The groups are the `GROUPS` table at the end of `selftest()`; `python3 plugins/workflows-core/scripts/specs-git.py --selftest --group '?'` prints their names, as that usage error on stderr (exit 2). A run with `--group` prints `specs-git selftest: PASS (<n> checks; partial: <groups>)`, or `specs-git selftest: FAIL (partial: <groups>)` with its failure lines under it, and **a line with `partial:` is never evidence that the selftest passes.** Only a run with no `--group` is, its PASS line carrying no `partial:`.

## The mutants

A mutant is a one-line edit to a script under `plugins/workflows-core/scripts/` that one named check must catch. `scripts/selftests/specs-git-mutants.json` lists them, each with its `id`, the `group` to run, the `file`, the `old` line and the `new` text that replaces it, and `fails`, the label of the check it must fail; `scripts/selftests/mutants.py`'s docstring states the file's shape and every line the runner prints. `python3 scripts/selftests/mutants.py` runs every mutant, `--only <id>` (repeatable) only those named, and `--list` prints each mutant's id, group and check and runs nothing.

The runner works on a copy: it copies `plugins/workflows-core/`, `scripts/selftests/` and `.github/workflows/validate-catalog.yml` into a temporary directory, writes and runs only there, and removes the directory when it exits. It first runs each group a selected mutant names, unchanged, then each mutant's group with that one edit in place, and prints `killed <id>` where the run fails with a failure line that starts with the mutant's `fails`. The other outcomes are `STALE <id>`, where `old` is not found exactly once in `file`, so nothing runs; `TIMEOUT <id>`, where the run passes its time limit; and `SURVIVED <id>`, any other run. A group whose unchanged run does not pass prints `BASELINE RED <group>`, and its mutants are left unrun. It exits 0 where every selected mutant was killed, 1 on any other outcome, and 2 where it could not run. **CI does not run it**, since a full run takes minutes (*How long it takes*): run it when you change a file a mutant's `file` names, since an edit to its `old` line leaves that mutant `STALE`.

**What none of this can see:** a check that asserts too little passes in a group run, in a full run and in CI alike, and only a mutant written for that check catches it, by surviving. `python3 scripts/selftests/mutants.py --list` prints the checks that have one, after each mutant's id and group; no other check has that guard, and a group whose mutants are all killed says nothing about its other checks.

## Which rules load with the tests

Reading a file under `scripts/selftests/` loads the `gates*.md` rules, whose `paths:` take every file under `scripts/`, the rules files that load with any file, and this one; not the specs-repo git rules, which loaded with the tests while they were in the script. **Before editing a test, Read `plugins/workflows-core/scripts/specs-git.py` with the Read tool:** that loads `.claude/rules/workflows-core-git.md` and its companions, with `workflows-core.md` and its own, among them the specs-repo git authorities and invariants the tests check.

## How long it takes

Measured on 2026-11-13 on one 12-core machine (`nproc`), at `a89115dc`. The selftest, measured twice: the full run took 98 s both times; alone, `midrun` took 32 to 35 s, `end` 28 s, `start` 17 to 18 s, `land` and `mode` about 8 s, `replay` about 4 s, and each other group about a second or less. A full run of every mutant, measured once, took 537 s. The figures move with the machine and with every check added, so measure again rather than trust them. The commands below print the full run's time, then one `<group> <seconds> s` line per group, then the mutant run's time:

```bash
time python3 plugins/workflows-core/scripts/specs-git.py --selftest
(for g in $(python3 plugins/workflows-core/scripts/specs-git.py --selftest --group '?' 2>&1 | sed 's/.*one of: //; s/)$//; s/,//g'); do
  TIMEFORMAT="$g %1R s"; time python3 plugins/workflows-core/scripts/specs-git.py --selftest --group "$g" > /dev/null
done)
time python3 scripts/selftests/mutants.py
```

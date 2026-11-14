#!/usr/bin/env python3
"""mutants.py -- one-line mutants of the scripts under plugins/workflows-core/scripts/, each run against one group of
the specs-git.py selftest on a temporary copy of the tree, reporting which of them the group catches.

  python3 scripts/selftests/mutants.py [--only <id>]... [--list | --check] [--file <mutants file>]

The mutants file (default scripts/selftests/specs-git-mutants.json) is a JSON list of objects with exactly the keys id
(unique), group (one of the selftest's groups), file (a path under plugins/workflows-core/scripts/, relative to the
repository root), old and new (each one line of text, with no newline) and fails (the start of the failure line of
the check the mutant must fail: at least the check's label up to and including its colon, such as "e_land_refused:",
and as much of the message after it as tells that check from others with the same label). In every mode the runner
first reads the selftest's groups, in their run order, from the usage error `specs-git.py --selftest --group '?'`
prints on stderr: one run of the repository's script, which runs no group and writes nothing, with -B and with
GITHUB_ACTIONS empty, since the selftest refuses --group in CI before it reads a name. --only <id> selects one mutant
and may be repeated; with none, every mutant is selected. --list prints each selected mutant's id, group and fails,
one per line, and runs no mutant and no group. --check reads each selected mutant's file in the repository, never
writing there, and counts its old text in it, overlapping occurrences each counted, as a run does; it prints STALE
<id>: old text found <n> times in <file> for each not found exactly once, then "mutants: <n> checked, <t> stale",
runs no mutant and no group, and exits 0 only where none is stale. It finds a mutant whose old text has gone, never a
check made to assert less, which only a run shows.

The runner copies plugins/workflows-core/, scripts/selftests/ and .github/workflows/validate-catalog.yml into a new
temporary directory, at the same relative paths and without any __pycache__ directory, writes only under that
directory and makes every group run there: it never writes under the repository, and the directory is removed when it
exits, whatever happened. That copy is never run in: each run, a baseline's included, is in a fresh copy of it,
removed after the run, so nothing a run writes -- a file a case leaves, or bytecode -- reaches another run. A SIGTERM,
SIGHUP or SIGINT ends the run under way and removes the directory, any further one ignored meanwhile, and the runner
exits 128 + the signal's number; one the runner inherited as ignored, as under nohup, stays ignored. Every run is
`python3 -B specs-git.py --selftest --group <group>` in its copy, in a session of its own, with
PYTHONDONTWRITEBYTECODE=1, with GITHUB_ACTIONS empty, since the selftest refuses --group in CI, and with its TMPDIR
inside the temporary directory. However a run ends, its process group then gets SIGTERM, so a process in it can pass
the signal on to a session of its own, and SIGKILL three seconds later where any of the group is left.

For each group a selected mutant names, the group first runs once unchanged, capped at 900 seconds, and its time is
kept; where that run does not end in a PASS line, BASELINE RED <group> is printed with a line under it saying why --
the cap, else the first line of its stderr, else its first failure line -- and every mutant of the group counts as on
a red baseline, unrun. Then each selected mutant whose group's baseline passed, in the file's order: where old is not
found exactly once in the copy of file, overlapping occurrences each counted, STALE <id>: old text found <n> times in
<file>; else the group runs with old replaced by new in its fresh copy, with a time limit of ten times its baseline
and never under 60 seconds. A run stopped at the limit prints TIMEOUT <id>. The run's failure lines are the lines
after its FAIL line that carry the selftest's two-space indent. A run that exits 1 with a failure line that, stripped,
starts with fails is a kill: killed <id> (<f> failure lines): <that line, cut at 160 characters>, <f> being how many
failure lines the run printed, so a mutant that fails most of its group shows as one. Anything else prints SURVIVED
<id>, with the first line of the run's stderr under it where the run exited 2. A case that crashes is not a kill,
since its line reads "<name> crashed: ...", which does not start with "<name>:".

The last line is "mutants: <k> killed, <s> survived, <t> stale, <o> timed out, <r> on a red baseline, of <n>".
Exit 0: every selected mutant was killed, none selected included. Exit 1: any other outcome. Exit 2: it could not run
(usage, the selftest's groups not read, a malformed mutants file, an --only id the file lacks, a temporary directory
under the repository, a copy that failed, any other exception), printing one "mutants: not run (...)" line on stderr.
Python standard library only.
"""

import argparse
import contextlib
import json
import os
import posixpath
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DEFAULT_FILE = os.path.join(ROOT, "scripts", "selftests", "specs-git-mutants.json")
# What the copy holds, relative to the repository root: every path a group needs to pass.
COPIED = ("plugins/workflows-core", "scripts/selftests", ".github/workflows/validate-catalog.yml")
SCRIPT = "plugins/workflows-core/scripts/specs-git.py"
MUTABLE = "plugins/workflows-core/scripts/"
USAGE = "specs-git: not run (usage: --group takes one of: "
KEYS = ("id", "group", "file", "old", "new", "fails")
PASS = "specs-git selftest: PASS ("
FAIL = "specs-git selftest: FAIL"
LIMIT_FACTOR, LIMIT_FLOOR, BASELINE_CAP, CUT, GROUPS_CAP = 10, 60, 900, 160, 60
KILL_AFTER = 3  # seconds from a run's SIGTERM to its SIGKILL: one more than session-branch.py's, so its git_bounded
# has ended a git it runs in a session of its own before this SIGKILL lands
SIGNALS = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)
OUTCOMES = ("killed", "survived", "stale", "timed out", "on a red baseline")


class NotRun(Exception):
    """One "mutants: not run (...)" line on stderr, and exit 2."""


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is."""

    def error(self, message):
        raise NotRun("usage: %s" % message)


def _on_signal(signum, _frame):
    """The first SIGTERM, SIGHUP or SIGINT: every later one ignored, then SystemExit, so each finally runs -- the run's
    process group ended, its copy and then the temporary directory removed -- and the runner exits 128 + signum."""
    for s in SIGNALS:
        signal.signal(s, signal.SIG_IGN)
    raise SystemExit(128 + signum)


@contextlib.contextmanager
def _held():
    """SIGNALS held while the block runs and delivered when it ends, so none cuts it short; yields the mask before."""
    before = signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    try:
        yield before
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, before)


def selftest_groups():
    """The selftest's groups, in its run order, from the usage error the repository's specs-git.py prints for
    --selftest --group '?': run writing no bytecode, and with GITHUB_ACTIONS empty, since the selftest refuses --group
    in CI before it reads a name. NotRun where that run does not print the one usage line."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GITHUB_ACTIONS="")
    cmd = [sys.executable, "-B", os.path.join(ROOT, SCRIPT), "--selftest", "--group", "?"]
    try:
        p = subprocess.run(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=GROUPS_CAP)
    except subprocess.TimeoutExpired:
        raise NotRun("the selftest's groups: %s --selftest --group '?' took over %d seconds" % (SCRIPT, GROUPS_CAP))
    err = p.stderr.decode("utf-8", "replace").strip()
    if p.returncode != 2 or "\n" in err or not err.startswith(USAGE) or not err.endswith(")"):
        raise NotRun("the selftest's groups: %s --selftest --group '?' exited %d without its usage line (%s)"
                     % (SCRIPT, p.returncode, _first(err.splitlines()) or "no stderr"))
    return tuple(err[len(USAGE):-1].split(", "))


def load(path, groups):
    """The mutants <path> holds, each checked against the selftest's <groups>; NotRun where the file is malformed."""
    try:
        with open(path, encoding="utf-8") as fh:
            mutants = json.load(fh)
    except (OSError, ValueError) as e:
        raise NotRun("%s: %s" % (path, e))
    if not isinstance(mutants, list):
        raise NotRun("%s: not a JSON list" % path)
    seen = set()
    for n, m in enumerate(mutants, 1):
        problem = _malformed(m, seen, groups)
        if problem:
            raise NotRun("%s: mutant %d: %s" % (path, n, problem))
        seen.add(m["id"])
    return mutants


def _malformed(m, seen, groups):
    """What is wrong with mutant <m>, <seen> holding the ids before it; None where nothing is."""
    if not isinstance(m, dict) or sorted(m) != sorted(KEYS):
        return "not an object with exactly the keys %s" % ", ".join(KEYS)
    bad = [k for k in KEYS if not isinstance(m[k], str)]
    if bad:
        return "%s is not a string" % bad[0]
    if not m["id"] or m["id"].split() != [m["id"]]:
        return "id %r is empty or holds whitespace" % m["id"]
    if m["id"] in seen:
        return "id %s is not unique" % m["id"]
    if m["group"] not in groups:
        return "group %r is not one of the selftest's groups: %s" % (m["group"], ", ".join(groups))
    f = m["file"]
    if (posixpath.normpath(f) != f or not f.startswith(MUTABLE) or "__pycache__" in f.split("/")
            or not os.path.isfile(os.path.join(ROOT, f))):
        return "file %r is not a file under %s" % (f, MUTABLE)
    for k in ("old", "new"):
        if "".join(m[k].splitlines()) != m[k]:
            return "%s is not one line with no newline" % k
    if not m["old"]:
        return "old is empty"
    if m["old"] == m["new"]:
        return "new is old unchanged"
    label, colon, _ = m["fails"].partition(":")
    if not colon or not label.strip() or m["fails"].strip() != m["fails"]:
        return "fails %r is not the start of a failure line: a check's label and its colon, then any text" % m["fails"]
    return None


def _copy(tree):
    """COPIED from the repository into <tree>, at the same relative paths, leaving out every __pycache__."""
    for rel in COPIED:
        src, dst = os.path.join(ROOT, rel), os.path.join(tree, rel)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)


@contextlib.contextmanager
def _fresh(top):
    """A fresh copy of <top>/tree, the copy no run is made in, in a directory of its own under <top>; yields the
    copy's path and removes the directory when the block ends -- what cannot be removed then goes when <top> does."""
    work = tempfile.mkdtemp(prefix="run-", dir=top)
    try:
        shutil.copytree(os.path.join(top, "tree"), os.path.join(work, "tree"))
        yield os.path.join(work, "tree")
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _signal_group(pgid, signum):
    try:
        os.killpg(pgid, signum)
    except (ProcessLookupError, PermissionError):  # nothing left in the group
        pass


def _group_alive(pgid):
    try:
        os.killpg(pgid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def _end_group(p):
    """SIGTERM to the process group <p> leads, so a process in it can pass the signal on to a session of its own --
    as session-branch.py's git_bounded does for the git it runs in one -- then SIGKILL KILL_AFTER seconds later to
    whatever of the group is left, and <p> reaped. A group with nothing left in it is no error. SIGNALS are held
    meanwhile, so a signal to the runner never cuts it short."""
    with _held():
        _signal_group(p.pid, signal.SIGTERM)
        deadline = time.monotonic() + KILL_AFTER
        while time.monotonic() < deadline:
            p.poll()  # reaps <p> once it has exited, so the group test below does not count it
            if not _group_alive(p.pid):
                break
            time.sleep(0.05)
        _signal_group(p.pid, signal.SIGKILL)
        p.wait()


def run_group(top, tree, group, limit):
    """One run of <group> in the copy <tree>, in a session of its own, writing and reading no bytecode, with
    GITHUB_ACTIONS empty, since the selftest refuses --group in CI, its temporary files in a directory of its own under
    <top>: (its exit status, None where <limit> seconds stopped it; the lines of
    its standard output; the lines of its stderr; the seconds it took). Its process group is ended however it ends
    (_end_group), a signal that reaches the runner just before _end_group holds signals included. What a killed run
    leaves in its directory that cannot be removed now -- a directory a case made read-only, say -- goes when <top>
    does, since TemporaryDirectory's cleanup restores the write bits first."""
    scratch = tempfile.mkdtemp(prefix="tmp-", dir=top)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", GITHUB_ACTIONS="", TMPDIR=scratch)
    cmd = [sys.executable, "-B", os.path.join(tree, SCRIPT), "--selftest", "--group", group]
    with open(os.path.join(top, "out"), "w+b") as out, open(os.path.join(top, "err"), "w+b") as err:
        p = None
        try:
            with _held() as before:  # a signal waits until p is known; the run starts with the mask from before
                p = subprocess.Popen(cmd, cwd=tree, env=env, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                     start_new_session=True,
                                     preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, before))
                start = time.monotonic()
            try:
                rc = p.wait(timeout=limit)
            except subprocess.TimeoutExpired:
                rc = None
            seconds = time.monotonic() - start
        finally:
            if p is not None:
                try:
                    _end_group(p)
                except SystemExit:  # a first signal before _end_group held SIGNALS: the group is still ended
                    _end_group(p)
                    raise
        out.seek(0)
        err.seek(0)
        lines, errors = [f.read().decode("utf-8", "replace").splitlines() for f in (out, err)]
    shutil.rmtree(scratch, ignore_errors=True)
    return rc, lines, errors, seconds


def _write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def _outside_repository(directory):
    """NotRun where <directory>, a temporary directory the runner could be given, is under the repository."""
    root = os.path.realpath(ROOT)
    if directory and os.path.commonpath([os.path.realpath(directory), root]) == root:
        raise NotRun("the temporary directory %s is under the repository" % directory)


def _occurrences(data, old):
    """How many times <old> occurs in <data>, overlapping occurrences each counted."""
    n, at = 0, data.find(old)
    while at != -1:
        n += 1
        at = data.find(old, at + 1)
    return n


def _failure_lines(lines):
    """The failure lines a run printed: the lines after its FAIL line that carry the selftest's two-space indent,
    one per failed check."""
    for i, line in enumerate(lines):
        if line.startswith(FAIL):
            return [rest for rest in lines[i + 1:] if rest.startswith("  ")]
    return []


def _first(lines):
    """The first of <lines> that holds anything, stripped and cut at CUT; None where none does."""
    return next((line.strip()[:CUT] for line in lines if line.strip()), None)


def check_stale(chosen):
    """--check: each mutant <chosen>'s old text counted in its file in the repository, read and never written, a
    STALE line for each not found exactly once, then the count; runs no mutant and no group. Returns the exit status."""
    stale = 0
    for m in chosen:
        with open(os.path.join(ROOT, m["file"]), "rb") as fh:
            found = _occurrences(fh.read(), m["old"].encode("utf-8"))
        if found != 1:
            print("STALE %s: old text found %d times in %s" % (m["id"], found, m["file"]))
            stale += 1
    print("mutants: %d checked, %d stale" % (len(chosen), stale))
    return 1 if stale else 0


def run(chosen, groups):
    """Runs the mutants <chosen> on a copy of the tree, printing a line for each outcome as it comes; returns how
    many of each OUTCOMES there were."""
    counts = dict.fromkeys(OUTCOMES, 0)
    if not chosen:
        return counts
    # tempfile writes a probe file into the directory it picks, so the variables it reads first are checked before
    # it picks one, and what it picks is checked after, for its fallback to the current directory.
    for name in ("TMPDIR", "TEMP", "TMP"):
        _outside_repository(os.environ.get(name))
    _outside_repository(tempfile.gettempdir())
    temporary = None
    try:
        with _held():  # a signal waits until the directory is known to the finally below
            temporary = tempfile.TemporaryDirectory(prefix="mutants-")
        try:
            _copy(os.path.join(temporary.name, "tree"))
        except OSError as e:
            raise NotRun("could not copy the tree: %s" % e)
        _run_in(temporary.name, chosen, groups, counts)
    finally:
        if temporary is not None:
            with _held():
                temporary.cleanup()
    return counts


def _run_in(top, chosen, groups, counts):
    """The baselines, then the mutants <chosen>, each run in a fresh copy of the copy under <top>, counted into
    <counts>."""
    baseline = {}
    for group in groups:
        if any(m["group"] == group for m in chosen):
            with _fresh(top) as tree:
                rc, lines, errors, seconds = run_group(top, tree, group, BASELINE_CAP)
            said = [line for line in lines if line.strip()]
            green = rc == 0 and bool(said) and said[-1].startswith(PASS)
            baseline[group] = seconds if green else None
            if not green:
                why = ("stopped at its %d-second cap" % BASELINE_CAP if rc is None
                       else _first(errors) or _first(_failure_lines(lines)) or "exit %d with no PASS line" % rc)
                print("BASELINE RED %s\n  %s" % (group, why), flush=True)
    for m in chosen:
        if baseline[m["group"]] is None:
            counts["on a red baseline"] += 1
            continue
        with open(os.path.join(top, "tree", m["file"]), "rb") as fh:
            original = fh.read()
        old, new = m["old"].encode("utf-8"), m["new"].encode("utf-8")
        found = _occurrences(original, old)
        if found != 1:
            print("STALE %s: old text found %d times in %s" % (m["id"], found, m["file"]), flush=True)
            counts["stale"] += 1
            continue
        limit = max(LIMIT_FLOOR, LIMIT_FACTOR * baseline[m["group"]])
        with _fresh(top) as tree:
            _write(os.path.join(tree, m["file"]), original.replace(old, new, 1))
            rc, lines, errors, _ = run_group(top, tree, m["group"], limit)
        if rc is None:
            print("TIMEOUT %s" % m["id"], flush=True)
            counts["timed out"] += 1
            continue
        failures = _failure_lines(lines)
        hit = next((s for s in (line.strip() for line in failures) if s.startswith(m["fails"])), None)
        if rc == 1 and hit is not None:
            print("killed %s (%d failure lines): %s" % (m["id"], len(failures), hit[:CUT]), flush=True)
            counts["killed"] += 1
        else:
            said = _first(errors) if rc == 2 else None
            print("SURVIVED %s" % m["id"] + ("\n  %s" % said if said else ""), flush=True)
            counts["survived"] += 1


def main(argv=None):
    ap = Parser(prog="mutants.py", description="Run one-line mutants of plugins/workflows-core/scripts/ against "
                                               "groups of the specs-git.py selftest, on a temporary copy of the tree.")
    ap.add_argument("--only", action="append", metavar="ID", help="run only this mutant; repeatable")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true",
                      help="print each selected mutant's id, group and fails; run no mutant and no group")
    mode.add_argument("--check", action="store_true",
                      help="count each selected mutant's old text in its file in the repository; run no mutant and "
                           "no group")
    ap.add_argument("--file", default=DEFAULT_FILE, metavar="PATH", help="the mutants file (default: %(default)s)")
    a = ap.parse_args(argv)
    groups = selftest_groups()
    mutants = load(a.file, groups)
    ids = {m["id"] for m in mutants}
    for only in a.only or ():
        if only not in ids:
            raise NotRun("--only %s: %s holds no mutant with that id" % (only, a.file))
    chosen = [m for m in mutants if a.only is None or m["id"] in a.only]
    if a.list:
        for m in chosen:
            print("%s %s %s" % (m["id"], m["group"], m["fails"]))
        return 0
    if a.check:
        return check_stale(chosen)
    for s in SIGNALS:
        if signal.getsignal(s) != signal.SIG_IGN:  # one inherited as ignored, as under nohup, stays ignored
            signal.signal(s, _on_signal)
    counts = run(chosen, groups)
    print("mutants: %d killed, %d survived, %d stale, %d timed out, %d on a red baseline, of %d"
          % (tuple(counts[k] for k in OUTCOMES) + (len(chosen),)))
    return 0 if counts["killed"] == len(chosen) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except NotRun as e:
        print("mutants: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # anything unexpected is "not run" on one line, never a traceback
        print("mutants: not run (%s: %s)" % (type(e).__name__, " ".join(str(e).split())), file=sys.stderr)
        sys.exit(2)

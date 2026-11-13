#!/usr/bin/env python3
"""mutants.py -- one-line mutants of the scripts under plugins/workflows-core/scripts/, each run against one group of
the specs-git.py selftest on a temporary copy of the tree, reporting which of them the group catches.

  python3 scripts/selftests/mutants.py [--only <id>]... [--list] [--file <mutants file>]

The mutants file (default scripts/selftests/specs-git-mutants.json) is a JSON list of objects with exactly the keys id
(unique), group (one of the selftest's sixteen groups), file (a path under plugins/workflows-core/scripts/, relative to
the repository root), old and new (each one line of text, with no newline) and fails (the label of the check the
mutant must fail, up to and including its colon, such as "e_land_refused:"). --only <id> selects one mutant and may be
repeated; with none, every mutant is selected. --list prints each selected mutant's id, group and fails, one per line,
and runs nothing.

The runner copies plugins/workflows-core/, scripts/selftests/ and .github/workflows/validate-catalog.yml into a new
temporary directory, at the same relative paths and without any __pycache__ directory, and writes and runs only there:
it never writes under the repository, and the directory is removed when it exits, whatever happened. Every run is
`python3 -B specs-git.py --selftest --group <group>` in the copy, in a session of its own, with
PYTHONDONTWRITEBYTECODE=1 and its TMPDIR inside the temporary directory. The script loads its sibling modules through
importlib, whose cached bytecode is keyed on the source's size and its modification time in whole seconds, so a
mutant of the same length as the text it replaces, restored within the second, would otherwise outlive its restore.

For each group a selected mutant names, the group first runs once in the unchanged copy, and its time is kept; where
that run does not end in a PASS line, BASELINE RED <group> is printed and every mutant of the group counts as on a red
baseline, unrun. Then each selected mutant whose group's baseline passed, in the file's order: where old is not found
exactly once in the copy of file, STALE <id>: old text found <n> times in <file>; else old is replaced by new, the group runs with a time
limit of ten times its baseline and never under 60 seconds, and the file is restored, whatever the run did. A run
stopped at the limit has its whole process group killed and prints TIMEOUT <id>. A run that exits 1 with a line of
standard output that, stripped, starts with fails is a kill: killed <id> (<f> failure lines): <that line, cut at 160
characters>, <f> being how many failure lines the run printed, so a mutant that fails most of its group shows as one.
Anything else prints SURVIVED <id>: a case that crashes among them, since its line reads "<name> crashed: ...", which
does not start with "<name>:".

The last line is "mutants: <k> killed, <s> survived, <t> stale, <o> timed out, <r> on a red baseline, of <n>".
Exit 0: every selected mutant was killed, none selected included. Exit 1: any other outcome. Exit 2: it could not run
(usage, a malformed mutants file, an --only id the file lacks, a temporary directory under the repository, a copy that
failed, any other exception), printing one "mutants: not run (...)" line on stderr. Python standard library only.
"""

import argparse
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
# What the copy holds, relative to the repository root: every path the selftest reads.
COPIED = ("plugins/workflows-core", "scripts/selftests", ".github/workflows/validate-catalog.yml")
SCRIPT = "plugins/workflows-core/scripts/specs-git.py"
MUTABLE = "plugins/workflows-core/scripts/"
# The selftest's groups, as GROUPS in specs_git_selftest.py names them, in its run order.
GROUPS = ("status", "branch_merged", "branch_key", "push_scope", "owner_repo", "mode", "state", "lines", "gate", "end",
          "land", "replay", "start", "midrun", "skill", "selftest")
KEYS = ("id", "group", "file", "old", "new", "fails")
PASS = "specs-git selftest: PASS ("
FAIL = "specs-git selftest: FAIL"
LIMIT_FACTOR, LIMIT_FLOOR, CUT = 10, 60, 160
OUTCOMES = ("killed", "survived", "stale", "timed out", "on a red baseline")


class NotRun(Exception):
    """One "mutants: not run (...)" line on stderr, and exit 2."""


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is."""

    def error(self, message):
        raise NotRun("usage: %s" % message)


def load(path):
    """The mutants <path> holds, each checked; NotRun where the file is malformed."""
    try:
        with open(path, encoding="utf-8") as fh:
            mutants = json.load(fh)
    except (OSError, ValueError) as e:
        raise NotRun("%s: %s" % (path, e))
    if not isinstance(mutants, list):
        raise NotRun("%s: not a JSON list" % path)
    seen = set()
    for n, m in enumerate(mutants, 1):
        problem = _malformed(m, seen)
        if problem:
            raise NotRun("%s: mutant %d: %s" % (path, n, problem))
        seen.add(m["id"])
    return mutants


def _malformed(m, seen):
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
    if m["group"] not in GROUPS:
        return "group %r is not one of: %s" % (m["group"], ", ".join(GROUPS))
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
    if len(m["fails"]) < 2 or not m["fails"].endswith(":") or m["fails"].strip() != m["fails"]:
        return "fails %r is not a check's label up to and including its colon" % m["fails"]
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


def _kill_group(p):
    """SIGKILL to the process group <p> leads, which takes every child it started, then <p> reaped; a group with
    nothing left in it is no error."""
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass
    p.wait()


def run_group(top, group, limit):
    """One run of <group> in the copy under <top>, in a session of its own, writing and reading no bytecode, its
    temporary files in a directory of its own under <top>: (its exit status, None where <limit> seconds stopped it;
    the lines of its standard output; the seconds it took). Whatever is left of its process group when it ends is
    killed. What a killed run leaves in its directory that cannot be removed now -- a directory a case made
    read-only, say -- goes when <top> does, since TemporaryDirectory's cleanup restores the write bits first."""
    tree, out = os.path.join(top, "tree"), os.path.join(top, "out")
    scratch = tempfile.mkdtemp(prefix="tmp-", dir=top)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=scratch)
    cmd = [sys.executable, "-B", os.path.join(tree, SCRIPT), "--selftest", "--group", group]
    start = time.monotonic()
    with open(out, "wb") as fh:
        p = subprocess.Popen(cmd, cwd=tree, env=env, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.DEVNULL,
                             start_new_session=True)
        try:
            try:
                rc = p.wait(timeout=limit)
            except subprocess.TimeoutExpired:
                rc = None
            seconds = time.monotonic() - start
        finally:
            _kill_group(p)
    with open(out, "rb") as fh:
        lines = fh.read().decode("utf-8", "replace").splitlines()
    shutil.rmtree(scratch, ignore_errors=True)
    return rc, lines, seconds


def _write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def _outside_repository(directory):
    """NotRun where <directory>, a temporary directory the runner could be given, is under the repository."""
    root = os.path.realpath(ROOT)
    if directory and os.path.commonpath([os.path.realpath(directory), root]) == root:
        raise NotRun("the temporary directory %s is under the repository" % directory)


def _failure_lines(lines):
    """How many failure lines a run printed: the lines after its FAIL line that carry the selftest's two-space
    indent, one per failed check."""
    for i, line in enumerate(lines):
        if line.startswith(FAIL):
            return sum(1 for rest in lines[i + 1:] if rest.startswith("  "))
    return 0


def run(chosen):
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
    with tempfile.TemporaryDirectory(prefix="mutants-") as top:
        try:
            _copy(os.path.join(top, "tree"))
        except OSError as e:
            raise NotRun("could not copy the tree: %s" % e)
        baseline = {}
        for group in GROUPS:
            if any(m["group"] == group for m in chosen):
                rc, lines, seconds = run_group(top, group, None)
                said = [line for line in lines if line.strip()]
                green = rc == 0 and bool(said) and said[-1].startswith(PASS)
                baseline[group] = seconds if green else None
                if not green:
                    print("BASELINE RED %s" % group, flush=True)
        for m in chosen:
            if baseline[m["group"]] is None:
                counts["on a red baseline"] += 1
                continue
            path = os.path.join(top, "tree", m["file"])
            with open(path, "rb") as fh:
                original = fh.read()
            old, new = m["old"].encode("utf-8"), m["new"].encode("utf-8")
            found = original.count(old)
            if found != 1:
                print("STALE %s: old text found %d times in %s" % (m["id"], found, m["file"]), flush=True)
                counts["stale"] += 1
                continue
            limit = max(LIMIT_FLOOR, LIMIT_FACTOR * baseline[m["group"]])
            try:
                _write(path, original.replace(old, new, 1))
                rc, lines, _ = run_group(top, m["group"], limit)
            finally:
                _write(path, original)
            if rc is None:
                print("TIMEOUT %s" % m["id"], flush=True)
                counts["timed out"] += 1
                continue
            hit = next((s for s in (line.strip() for line in lines) if s.startswith(m["fails"])), None)
            if rc == 1 and hit is not None:
                print("killed %s (%d failure lines): %s" % (m["id"], _failure_lines(lines), hit[:CUT]), flush=True)
                counts["killed"] += 1
            else:
                print("SURVIVED %s" % m["id"], flush=True)
                counts["survived"] += 1
    return counts


def main(argv=None):
    ap = Parser(prog="mutants.py", description="Run one-line mutants of plugins/workflows-core/scripts/ against "
                                               "groups of the specs-git.py selftest, on a temporary copy of the tree.")
    ap.add_argument("--only", action="append", metavar="ID", help="run only this mutant; repeatable")
    ap.add_argument("--list", action="store_true", help="print each selected mutant's id, group and fails; run nothing")
    ap.add_argument("--file", default=DEFAULT_FILE, metavar="PATH", help="the mutants file (default: %(default)s)")
    a = ap.parse_args(argv)
    mutants = load(a.file)
    ids = {m["id"] for m in mutants}
    for only in a.only or ():
        if only not in ids:
            raise NotRun("--only %s: %s holds no mutant with that id" % (only, a.file))
    chosen = [m for m in mutants if a.only is None or m["id"] in a.only]
    if a.list:
        for m in chosen:
            print("%s %s %s" % (m["id"], m["group"], m["fails"]))
        return 0
    counts = run(chosen)
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

#!/usr/bin/env python3
"""bounded.py <seconds> <command> [args...] -- run a command under a time cap, on every host.

macOS ships no `timeout` binary, so a capped call written as `timeout 5s <cmd>` fails there with
`command not found` -- and a caller that reads a failed call as "skip" (a slug-to-clone map skipping
a directory, a qmd probe falling back) then silently skips everything. This script is the plugin's
one way to cap a call; the bounded-run reference says where it is used.

The command inherits stdin, stdout and stderr, and runs in a process group of its own, which the cap
ends whole -- SIGTERM, then SIGKILL two seconds later -- so nothing it started outlives it.

Exit codes, as GNU timeout reports them:
  124        the cap ended the command
  126        the command could not be run (not executable)
  127        the command was not found
  128 + N    signal N ended the command
  2          usage: <seconds> is not a whole number of at least 1, or no command was given
  otherwise  the command's own exit code

Standard library only. `python3 bounded.py --selftest` runs the tests.
"""
import os
import signal
import subprocess
import sys
import tempfile
import time

TIMED_OUT = 124
GRACE = 2.0


def _end_group(proc):
    """SIGTERM the command's process group, then SIGKILL whatever is left after GRACE seconds."""
    for sig, wait in ((signal.SIGTERM, GRACE), (signal.SIGKILL, None)):
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError):
            pass
        try:
            proc.wait(timeout=wait)
            return
        except subprocess.TimeoutExpired:
            continue


def run(argv):
    if len(argv) < 2 or not argv[0].isdigit() or int(argv[0]) < 1:
        sys.stderr.write("usage: bounded.py <seconds> <command> [args...]\n")
        return 2
    seconds, cmd = int(argv[0]), argv[1:]
    try:
        proc = subprocess.Popen(cmd, start_new_session=True)
    except FileNotFoundError:
        sys.stderr.write("bounded.py: %s: command not found\n" % cmd[0])
        return 127
    except OSError as e:
        sys.stderr.write("bounded.py: %s: %s\n" % (cmd[0], e.strerror or e))
        return 126
    try:
        code = proc.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        _end_group(proc)
        return TIMED_OUT
    except KeyboardInterrupt:
        _end_group(proc)
        return 128 + signal.SIGINT
    return 128 - code if code < 0 else code


# --- self-test -------------------------------------------------------------------------------

def _call(args, stdin=None):
    started = time.monotonic()
    p = subprocess.run([sys.executable, os.path.abspath(__file__)] + args, input=stdin,
                       capture_output=True, text=True, timeout=60)
    return p.returncode, p.stdout, p.stderr, time.monotonic() - started


def _alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    # A zombie the init process has not reaped yet counts as gone.
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().split(")")[-1].split()[0] != "Z"
    except OSError:
        return True


def selftest():
    failures, cases = [], 0

    def check(name, ok, detail):
        nonlocal cases
        cases += 1
        if not ok:
            failures.append("%s: %r" % (name, detail))

    rc, out, err, _ = _call(["5", "true"])
    check("a command that succeeds exits 0", rc == 0, (rc, err))
    rc, out, err, _ = _call(["5", "sh", "-c", "exit 7"])
    check("the command's own exit code passes through", rc == 7, (rc, err))
    rc, out, err, _ = _call(["5", "printf", "out"])
    check("stdout passes through", rc == 0 and out == "out", (rc, out))
    rc, out, err, _ = _call(["5", "sh", "-c", "echo err >&2"])
    check("stderr passes through", rc == 0 and err == "err\n", (rc, err))
    rc, out, err, _ = _call(["5", "cat"], stdin="in")
    check("stdin passes through", rc == 0 and out == "in", (rc, out))
    rc, out, err, took = _call(["1", "sleep", "30"])
    check("the cap ends the command with 124", rc == 124 and took < 10, (rc, took))
    rc, out, err, _ = _call(["1", "sh", "-c", "sleep 3; echo late"])
    check("a capped command prints nothing after the cap", rc == 124 and "late" not in out, (rc, out))
    with tempfile.TemporaryDirectory() as tmp:
        pidfile = os.path.join(tmp, "pid")
        rc, out, err, _ = _call(["1", "sh", "-c", "sleep 30 & echo $! > '%s'; wait" % pidfile])
        pid = int(open(pidfile).read().strip())
        deadline = time.monotonic() + 5
        while _alive(pid) and time.monotonic() < deadline:
            time.sleep(0.1)
        check("the cap ends what the command started", rc == 124 and not _alive(pid), (rc, pid))
        rc, out, err, took = _call(["1", "sh", "-c", "trap '' TERM; sleep 30"])
        check("a command that ignores SIGTERM is killed", rc == 124 and took < 10, (rc, took))
        script = os.path.join(tmp, "not-executable")
        with open(script, "w") as fh:
            fh.write("#!/bin/sh\nexit 0\n")
        os.chmod(script, 0o644)
        rc, out, err, _ = _call(["5", script])
        check("a file that cannot be run exits 126", rc == 126, (rc, err))
    rc, out, err, _ = _call(["5", "no-such-command-bounded-selftest"])
    check("a command not found exits 127", rc == 127 and "command not found" in err, (rc, err))
    rc, out, err, _ = _call(["5", "sh", "-c", "kill -TERM $$"])
    check("a signal that ends the command exits 128 + N", rc == 128 + signal.SIGTERM, (rc, err))
    for bad in ([], ["5"], ["x", "true"], ["0", "true"], ["-1", "true"], ["1.5", "true"]):
        rc, out, err, _ = _call(bad)
        check("usage error %r exits 2" % (bad,), rc == 2 and "usage" in err, (rc, err))

    for f in failures:
        print("FAIL " + f)
    print("SELFTEST %s (%d cases, %d failed)" % ("PASS" if not failures else "FAIL", cases, len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    sys.exit(run(sys.argv[1:]))

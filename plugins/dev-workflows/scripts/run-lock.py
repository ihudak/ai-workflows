#!/usr/bin/env python3
"""run-lock.py -- run a build or test command while holding the work tree's one run lock.

    python3 run-lock.py -- <command> [args...]

Two builds or test runs in one work tree trample each other's output directories, caches and
ports. This script lets one at a time through: it takes an exclusive lock on
`$(git rev-parse --git-path dev-workflows/run.lock)` -- per worktree, inside the git directory, never
staged; its directory is made when missing -- waits for it when another holder has it, runs the
command, and lets go once the command has been reaped. The lock is fcntl.flock, which the kernel
releases when the holder dies however it dies, so no lock goes stale and the file is never removed.

Run it from inside the git work tree. The command inherits stdin, stdout, stderr and the working
directory, but not the lock descriptor, so a daemon the build leaves behind cannot hold the lock. It
runs in a session of its own; a SIGTERM, SIGHUP or SIGINT sent to this script is passed on to that
group, and the script keeps the lock until the command has ended. The one gap: a SIGKILL sent to
this script alone, not to its group, frees the lock while the command still runs. While it waits,
this script prints one stderr line, `run-lock: waiting for <lock path>`. Where `fcntl` is missing
(Windows), it says so on stderr and runs the command unlocked.

Every exit of the script's own prints a stderr line starting `run-lock:` -- the usage line
included. The exit code alone does not tell them from the command's: a test runner may itself exit 2
or 4, so read the stderr line.

Exit codes:
  126        the command could not be run (not executable)
  127        the command was not found
  128 + N    signal N ended the command, or was sent to this script and passed on
  2          usage: no `--`, or no command after it
  4          the lock could not be taken: not inside a git work tree, git failing to name the
             path, an OSError making or opening the file, or the filesystem refusing flock
  otherwise  the command's own exit code

Standard library only. `python3 run-lock.py --selftest` runs the tests.
"""
import os
import signal
import subprocess
import sys

try:
    import fcntl
except ImportError:  # no fcntl on this platform
    fcntl = None

LOCK_GIT_PATH = "dev-workflows/run.lock"
USAGE = "run-lock: usage: run-lock.py -- <command> [args...]"
FORWARDED = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)


def lock_path(cwd=None):
    """The absolute lock path for the work tree `cwd` is in, or None when git cannot name it."""
    try:
        out = subprocess.run(["git", "rev-parse", "--git-path", LOCK_GIT_PATH], cwd=cwd,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    rel = out.stdout.decode("utf-8", "surrogateescape").rstrip("\r\n")
    if not rel:
        return None
    # git prints the path relative to the directory it ran in; resolve symlinks first so `..`
    # means what git meant (a symlinked temp directory, as on macOS)
    return os.path.abspath(os.path.join(os.path.realpath(cwd or os.getcwd()), rel))


def run(argv):
    """Take the lock, run argv, return the exit code."""
    if fcntl is None:
        sys.stderr.write("run-lock: fcntl is not available here; running the command unlocked\n")
        return _run_command(argv)
    path = lock_path()
    if path is None:
        sys.stderr.write("run-lock: not inside a git work tree, or git could not name the lock file\n")
        return 4
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    except OSError as e:
        sys.stderr.write("run-lock: cannot reach %s: %s\n" % (path, e))
        return 4
    try:
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                sys.stderr.write("run-lock: waiting for %s\n" % path)
                sys.stderr.flush()
                fcntl.flock(fd, fcntl.LOCK_EX)
        except OSError as e:
            sys.stderr.write("run-lock: cannot lock %s: %s\n" % (path, e))
            return 4
        return _run_command(argv)
    finally:
        os.close(fd)  # closing the descriptor releases the lock, after the command is reaped


def _run_command(argv):
    state = {"proc": None, "sig": None}

    def forward(signum, frame):
        state["sig"] = signum
        if state["proc"] is not None:
            _send(state["proc"], signum)

    old = [(n, signal.signal(n, forward)) for n in FORWARDED]
    try:
        try:
            state["proc"] = subprocess.Popen(argv, start_new_session=True)
        except FileNotFoundError:
            sys.stderr.write("run-lock: command not found: %s\n" % argv[0])
            return 127
        except OSError as e:
            sys.stderr.write("run-lock: cannot run %s: %s\n" % (argv[0], e))
            return 126
        if state["sig"] is not None:  # arrived before the command existed
            _send(state["proc"], state["sig"])
        while True:  # keep the lock until the command is reaped, whatever signals arrive
            try:
                rc = state["proc"].wait()
                break
            except KeyboardInterrupt:  # only if SIGINT beat the handler's installation
                continue
    finally:
        for n, h in old:
            signal.signal(n, h)
    if rc < 0:
        return 128 - rc
    if state["sig"] is not None:  # a signal sent to this script, passed on
        return 128 + state["sig"]
    return rc


def _send(proc, signum):
    try:
        os.killpg(proc.pid, signum)
    except OSError:
        pass


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) < 2 or argv[0] != "--":
        sys.stderr.write(USAGE + "\n")
        return 2
    return run(argv[1:])


# ---------------------------------------------------------------------------------------------
# selftest

def selftest():
    import shutil
    import signal
    import tempfile
    import time

    me = os.path.abspath(__file__)
    root = tempfile.mkdtemp(prefix="run-lock-selftest-")
    failures = []

    def sh(*args, **kw):
        return subprocess.run(list(args), stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)

    def lock_cmd(*cmd, **kw):
        return [sys.executable, me, "--"] + list(cmd)

    def new_repo(name):
        d = os.path.join(root, name)
        os.makedirs(d)
        sh("git", "init", "-q", d, check=True)
        return d

    def wait_for(path, secs=10):
        end = time.time() + secs
        while time.time() < end:
            if os.path.exists(path):
                return True
            time.sleep(0.02)
        return False

    def test_serialises():
        repo = new_repo("serial")
        log = os.path.join(repo, "log")
        procs = []
        for i in ("a", "b"):
            script = "echo s%s >> log; sleep 1; echo e%s >> log" % (i, i)
            procs.append(subprocess.Popen(lock_cmd("sh", "-c", script), cwd=repo,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE))
        errs = [p.communicate()[1].decode() for p in procs]
        with open(log) as f:
            lines = f.read().split()
        assert len(lines) == 4 and lines[0][0] == "s" and lines[1] == "e" + lines[0][1:] \
            and lines[2][0] == "s" and lines[3] == "e" + lines[2][1:], "overlapping windows: %r" % lines
        waiting = [e for e in errs if "run-lock: waiting for" in e]
        assert len(waiting) == 1 and waiting[0].count("waiting for") == 1, "waiting line: %r" % errs
        want = os.path.join(sh("git", "rev-parse", "--absolute-git-dir", cwd=repo).stdout.decode().strip(),
                            "dev-workflows", "run.lock")
        assert "waiting for %s\n" % want in waiting[0], "waiting path: %r" % waiting[0]

    def test_exit_code_passthrough():
        repo = new_repo("exit")
        assert subprocess.run(lock_cmd("sh", "-c", "exit 7"), cwd=repo).returncode == 7
        assert subprocess.run(lock_cmd("true"), cwd=repo).returncode == 0
        assert subprocess.run(lock_cmd("sh", "-c", "kill -TERM $$"), cwd=repo).returncode == 128 + 15
        r = subprocess.run(lock_cmd("run-lock-no-such-command"), cwd=repo, stderr=subprocess.DEVNULL)
        assert r.returncode == 127, r.returncode

    def test_killed_holder_releases():
        repo = new_repo("killed")
        marker = os.path.join(repo, "up")
        holder = subprocess.Popen(lock_cmd("sh", "-c", "echo up > up; exec sleep 30"), cwd=repo,
                                  start_new_session=True)
        try:
            assert wait_for(marker), "holder never started"
            os.kill(holder.pid, signal.SIGKILL)
            holder.wait()
            t0 = time.time()
            r = subprocess.run(lock_cmd("true"), cwd=repo, timeout=10)
            took = time.time() - t0
            assert r.returncode == 0 and took < 1.0, "freed after %.2fs, rc %s" % (took, r.returncode)
        finally:
            try:
                os.killpg(holder.pid, signal.SIGKILL)
            except OSError:
                pass

    def test_usage():
        repo = new_repo("usage")
        for argv in ([], ["true"], ["--"], ["x", "--", "true"]):
            r = sh(sys.executable, me, *argv, cwd=repo)
            assert r.returncode == 2, "%r -> %s" % (argv, r.returncode)
            assert r.stderr.decode().startswith("run-lock: usage:"), r.stderr

    def test_outside_repo():
        outside = os.path.join(root, "plain")
        os.makedirs(outside)
        env = dict(os.environ, GIT_CEILING_DIRECTORIES=root)
        r = subprocess.run(lock_cmd("true"), cwd=outside, env=env, stderr=subprocess.PIPE)
        assert r.returncode == 4, r.returncode
        assert r.stderr.decode().startswith("run-lock:"), r.stderr

    def test_lock_path_symlinked():
        # git prints the path relative to the directory it ran in; a symlinked cwd must not
        # make the `..` in it climb the wrong tree (macOS /var -> /private/var)
        repo = new_repo("symrepo")
        sub = os.path.join(repo, "a", "b")
        os.makedirs(sub)
        link = os.path.join(root, "link")
        os.symlink(sub, link)
        git_dir = sh("git", "rev-parse", "--absolute-git-dir", cwd=repo).stdout.decode().strip()
        want = os.path.join(git_dir, "dev-workflows", "run.lock")
        assert lock_path(link) == want, (lock_path(link), want)

    def test_signal_keeps_lock():
        repo = new_repo("signal")
        log = os.path.join(repo, "log")
        script = 'trap "" TERM; echo up > up; sleep 1; echo endA >> log'
        a = subprocess.Popen(lock_cmd("sh", "-c", script), cwd=repo)
        assert wait_for(os.path.join(repo, "up")), "holder never started"
        a.send_signal(signal.SIGTERM)
        b = subprocess.Popen(lock_cmd("sh", "-c", "echo startB >> log"), cwd=repo,
                             stderr=subprocess.DEVNULL)
        assert b.wait(timeout=10) == 0
        assert a.wait(timeout=10) == 128 + 15, "wrapper exit after SIGTERM"
        with open(log) as f:
            assert f.read().split() == ["endA", "startB"], "second caller ran before the first ended"

    def test_no_fcntl():
        repo = new_repo("nofcntl")
        code = ("import sys, runpy; sys.modules['fcntl'] = None; "
                "sys.argv = [%r, '--', 'sh', '-c', 'echo ran']; "
                "runpy.run_path(%r, run_name='__main__')" % (me, me))
        r = sh(sys.executable, "-c", code, cwd=repo)
        assert r.returncode == 0 and r.stdout.decode().strip() == "ran", (r.returncode, r.stdout)
        assert b"run-lock: fcntl is not available" in r.stderr, r.stderr
        assert not os.path.exists(os.path.join(repo, ".git", "dev-workflows", "run.lock"))

    def test_lock_path():
        repo = new_repo("path")
        sub = os.path.join(repo, "a", "b")
        os.makedirs(sub)
        git_dir = sh("git", "rev-parse", "--absolute-git-dir", cwd=repo).stdout.decode().strip()
        want = os.path.join(git_dir, "dev-workflows", "run.lock")
        assert not os.path.exists(os.path.dirname(want))
        assert subprocess.run(lock_cmd("true"), cwd=sub).returncode == 0
        assert os.path.isfile(want), "no lock file at %s" % want
        assert lock_path(sub) == want, (lock_path(sub), want)
        # a linked worktree has a git directory of its own, so its own lock
        sh("git", "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty",
           "-m", "x", cwd=repo)
        wt = os.path.join(root, "path-wt")
        sh("git", "worktree", "add", "-q", wt, cwd=repo, check=True)
        assert subprocess.run(lock_cmd("true"), cwd=wt).returncode == 0
        assert lock_path(wt) != want and os.path.isfile(lock_path(wt))

    tests = [test_serialises, test_exit_code_passthrough, test_killed_holder_releases, test_usage,
             test_outside_repo, test_lock_path, test_lock_path_symlinked, test_signal_keeps_lock,
             test_no_fcntl]
    try:
        for t in tests:
            try:
                t()
            except Exception as e:  # AssertionError or any error in the case
                failures.append("%s: %s" % (t.__name__, e))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    if failures:
        for f in failures:
            sys.stderr.write("FAIL " + f + "\n")
        print("run-lock selftest: FAIL")
        return 1
    print("run-lock selftest: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

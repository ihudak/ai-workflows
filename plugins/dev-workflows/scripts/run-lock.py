#!/usr/bin/env python3
"""run-lock.py -- run a build or test command while holding the work tree's one run lock.

    python3 run-lock.py -- <command> [args...]

Two builds or test runs in one work tree trample each other's output directories, caches and
ports. This script lets one at a time through: it takes an exclusive lock on
`$(git rev-parse --git-path dev-workflows/run.lock)` -- per worktree, inside the git directory, never
staged; its directory is made when missing -- waits for it when another holder has it, runs the
command, and lets go when the command has ended. The lock is fcntl.flock, which the kernel
releases when the holder dies however it dies, so no lock goes stale and the file is never removed.

Run it from inside the git work tree. The command inherits stdin, stdout, stderr and the working
directory, but not the lock descriptor, so a daemon the build leaves behind cannot hold the lock. It
runs in a session of its own, so a Ctrl-Z stops only this script, not the command.

"Ended" is exact in two cases. On any exit not after a signal this script passed on -- a normal exit,
or a leader killed by a signal that did not come through this script -- it is the command itself
(the group leader): a daemon the build leaves in its group does not hold the lock. Every SIGTERM,
SIGHUP, SIGINT or SIGQUIT sent to this script is passed on to the command's group as it arrives,
and after one the lock is held until the whole group is gone: the script waits for the leader, with
no time limit, then for the rest of the group for up to 2 seconds, then sends SIGKILL to whatever is
left. The exit is 128 + N for the last signal passed on. The gap, by class: a signal this script does not catch -- SIGKILL above all, but
also SIGUSR1, SIGALRM and the like -- sent to this script alone, not to its group, frees the lock
while the command still runs.

While it waits for the lock, this script prints one stderr line, `run-lock: waiting for <lock
path>`; a signal that arrives then ends it with `run-lock: interrupted while waiting for <lock
path>` and the exit 128 + N. Where `fcntl` is missing, on a host without it, the script says so on
stderr and runs the command unlocked.

Every exit of the script's own prints a stderr line starting `run-lock:` -- the usage line
included. The exit code alone does not tell them from the command's: a test runner may itself exit 2
or 4, so read the stderr line.

Exit codes:
  126        the command could not be run (not executable)
  127        the command was not found
  128 + N    signal N ended the command, or was sent to this script and passed on (that line:
             `run-lock: passed signal N on ...`), or interrupted the wait for the lock
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
import time

try:
    import fcntl
except ImportError:  # no fcntl on this platform
    fcntl = None

LOCK_GIT_PATH = "dev-workflows/run.lock"
USAGE = "run-lock: usage: run-lock.py -- <command> [args...]"
FORWARDED = (signal.SIGTERM, signal.SIGHUP, signal.SIGINT, signal.SIGQUIT)
GRACE = 2.0


class _Signalled(Exception):
    def __init__(self, signum):
        Exception.__init__(self, signum)
        self.signum = signum


def _raise(signum, frame):
    raise _Signalled(signum)


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
                old = [(n, signal.signal(n, _raise)) for n in FORWARDED]
                try:
                    sys.stderr.write("run-lock: waiting for %s\n" % path)
                    sys.stderr.flush()
                    fcntl.flock(fd, fcntl.LOCK_EX)
                except _Signalled as s:
                    sys.stderr.write("run-lock: interrupted while waiting for %s\n" % path)
                    return 128 + s.signum
                finally:
                    for n, h in old:
                        signal.signal(n, h)
        except OSError as e:
            sys.stderr.write("run-lock: cannot lock %s: %s\n" % (path, e))
            return 4
        return _run_command(argv)
    finally:
        os.close(fd)  # closing the descriptor releases the lock, after the command is reaped


def _run_command(argv):
    state = {"proc": None, "pending": None, "passed": []}

    def forward(signum, frame):
        if state["proc"] is None:  # before the command exists: kept, sent once it does
            state["pending"] = signum
        else:
            _pass_on(state, signum)

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
        early, state["pending"] = state["pending"], None
        if early is not None:
            _pass_on(state, early)
        rc = state["proc"].wait()  # the lock is kept until the command is reaped
        if state["passed"]:
            for n in FORWARDED:  # a later signal must not cut the group's wait short
                signal.signal(n, signal.SIG_IGN)
            _end_group(state["proc"])
    finally:
        for n, h in old:
            signal.signal(n, h)
    if state["passed"]:
        code = 128 + state["passed"][-1]
        sys.stderr.write("run-lock: passed signal%s %s on to the command; exiting %d\n"
                         % ("s" if len(state["passed"]) > 1 else "",
                            ", ".join(str(n) for n in state["passed"]), code))
        return code
    return 128 - rc if rc < 0 else rc


def _pass_on(state, signum):
    """Pass a signal received on to the command's group."""
    state["passed"].append(signum)
    try:
        os.killpg(state["proc"].pid, signum)
    except OSError:
        pass


def _end_group(proc):
    """The leader has exited: give the rest of its group GRACE seconds, then SIGKILL what is left."""
    deadline = time.monotonic() + GRACE
    while time.monotonic() < deadline:
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            return
        except PermissionError:
            pass
        time.sleep(0.05)
    try:
        os.killpg(proc.pid, signal.SIGKILL)
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
        holder = subprocess.Popen(lock_cmd("sh", "-c", "echo $$ > pid; echo up > up; exec sleep 30"),
                                  cwd=repo)
        try:
            assert wait_for(marker), "holder never started"
            os.kill(holder.pid, signal.SIGKILL)
            holder.wait()
            t0 = time.time()
            r = subprocess.run(lock_cmd("true"), cwd=repo, timeout=10)
            took = time.time() - t0
            assert r.returncode == 0 and took < 1.0, "freed after %.2fs, rc %s" % (took, r.returncode)
        finally:
            try:  # the command has a session of its own: kill it by the pid it wrote
                with open(os.path.join(repo, "pid")) as f:
                    os.killpg(int(f.read()), signal.SIGKILL)
            except (OSError, ValueError):
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
        a = subprocess.Popen(lock_cmd("sh", "-c", script), cwd=repo, stderr=subprocess.PIPE)
        assert wait_for(os.path.join(repo, "up")), "holder never started"
        a.send_signal(signal.SIGTERM)
        b = subprocess.Popen(lock_cmd("sh", "-c", "echo startB >> log"), cwd=repo,
                             stderr=subprocess.DEVNULL)
        assert b.wait(timeout=10) == 0
        err = a.communicate(timeout=10)[1].decode()
        assert a.returncode == 128 + 15, "wrapper exit after SIGTERM"
        assert "run-lock: passed signal 15 on to the command; exiting 143" in err, err
        with open(log) as f:
            assert f.read().split() == ["endA", "startB"], "second caller ran before the first ended"

    def test_signal_keeps_lock_for_group():
        # the leader exits at once on TERM; a TERM-ignoring grandchild keeps running
        repo = new_repo("group")
        log = os.path.join(repo, "log")
        script = ("(trap '' TERM; echo up > up; sleep 1; echo endA >> log) & "
                  "trap 'exit 0' TERM; wait")
        a = subprocess.Popen(lock_cmd("sh", "-c", script), cwd=repo, stderr=subprocess.DEVNULL)
        assert wait_for(os.path.join(repo, "up")), "holder never started"
        time.sleep(0.2)
        a.send_signal(signal.SIGTERM)
        b = subprocess.Popen(lock_cmd("sh", "-c", "echo startB >> log"), cwd=repo,
                             stderr=subprocess.DEVNULL)
        assert b.wait(timeout=10) == 0 and a.wait(timeout=10) == 143
        with open(log) as f:
            assert f.read().split() == ["endA", "startB"], "lock freed with the group alive"

    def test_interrupted_while_waiting():
        repo = new_repo("waitint")
        holder = subprocess.Popen(lock_cmd("sh", "-c", "echo up > up; sleep 2"), cwd=repo)
        try:
            assert wait_for(os.path.join(repo, "up")), "holder never started"
            w = subprocess.Popen(lock_cmd("true"), cwd=repo, stderr=subprocess.PIPE)
            first = w.stderr.readline().decode()  # the handlers are in before this line prints
            assert first.startswith("run-lock: waiting for "), first
            w.send_signal(signal.SIGINT)
            err = first + w.communicate(timeout=10)[1].decode()
            assert w.returncode == 128 + 2, w.returncode
            assert "run-lock: interrupted while waiting for " in err and "Traceback" not in err, err
        finally:
            holder.wait()

    def test_every_signal_passed_on():
        repo = new_repo("twosig")
        log = os.path.join(repo, "log")
        script = ('trap "echo got-INT >> log" INT; trap "echo got-TERM >> log; exit 0" TERM; '
                  'echo $$ > pid; echo up > up; while :; do sleep 0.1; done')
        a = subprocess.Popen(lock_cmd("sh", "-c", script), cwd=repo, stderr=subprocess.PIPE)
        try:
            assert wait_for(os.path.join(repo, "up")), "command never started"
            a.send_signal(signal.SIGINT)
            end = time.time() + 10
            while time.time() < end and not (os.path.exists(log) and "got-INT" in open(log).read()):
                time.sleep(0.02)
            a.send_signal(signal.SIGTERM)
            err = a.communicate(timeout=10)[1].decode()
            with open(log) as f:
                assert f.read().split() == ["got-INT", "got-TERM"], "the command missed a signal"
            assert a.returncode == 143 and "passed signals 2, 15 on to the command; exiting 143" in err, \
                (a.returncode, err)
        finally:  # a failed case must leave no process behind
            try:
                a.kill()
                with open(os.path.join(repo, "pid")) as f:
                    os.killpg(int(f.read()), signal.SIGKILL)
            except (OSError, ValueError):
                pass

    def test_normal_exit_releases_at_once():
        repo = new_repo("daemon")
        a = subprocess.run(lock_cmd("sh", "-c", "sleep 30 >/dev/null 2>&1 & echo $! > pid"), cwd=repo,
                           timeout=10)
        try:
            assert a.returncode == 0
            t0 = time.time()
            assert subprocess.run(lock_cmd("true"), cwd=repo, timeout=10).returncode == 0
            took = time.time() - t0
            assert took < 1.0, "a daemon in the group held the lock for %.2fs" % took
        finally:
            try:
                with open(os.path.join(repo, "pid")) as f:
                    os.kill(int(f.read()), signal.SIGKILL)
            except (OSError, ValueError):
                pass

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
             test_signal_keeps_lock_for_group, test_interrupted_while_waiting, test_every_signal_passed_on,
             test_normal_exit_releases_at_once, test_no_fcntl]
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

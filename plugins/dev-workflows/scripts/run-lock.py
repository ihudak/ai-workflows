#!/usr/bin/env python3
"""run-lock.py -- run a build or test command while holding the work tree's one run lock.

    python3 run-lock.py -- <command> [args...]

Two builds or test runs in one work tree trample each other's output directories, caches and
ports. This script lets one at a time through: it takes an exclusive lock on
`$(git rev-parse --git-path dev-workflows/run.lock)` as git names it in the outermost work tree --
inside a submodule, its superproject's, and so on to the top, so a suite inside a submodule shares
the superproject's lock; per worktree, inside the git directory, never staged; its directory is
made when missing -- waits for it when another holder has it, runs the command, and lets go when
the command has ended. The lock is fcntl.flock, which the kernel releases when the holder dies
however it dies, so no lock goes stale and the file is never removed.

Run it from inside the git work tree. The command inherits stdin, stdout, stderr and the working
directory, but not the lock descriptor, so a daemon the build leaves behind cannot hold the lock. It
runs in a session of its own, so a Ctrl-Z stops only this script, not the command.

"Ended" is exact in two cases. On any exit not after a signal this script passed on -- a normal exit,
or a leader killed by a signal that did not come through this script -- it is the command itself
(the group leader): a daemon the build leaves in its group does not hold the lock. A SIGTERM,
SIGHUP, SIGINT or SIGQUIT sent to this script while the leader runs is passed on to the command's
group as it arrives, and after one the lock is held until the whole group is gone: the script waits
for the leader, with no time limit, then for the rest of the group for up to 2 seconds, then sends
SIGKILL to whatever is left. The exit is 128 + N for the last signal passed on. Not every one is
passed on: one that arrives once the script holds the leader's exit status -- during that 2-second
grace too -- is ignored, from then until the script exits; of those that arrive before the command
has started, only the last is kept, and passed on once the command starts; one kept so is dropped
where the command cannot be started (exit 126 or 127); and one the group's kill refuses -- the
group already gone -- is not counted as passed on. The gap, by class: a signal this script does
not catch -- SIGKILL above all, but also SIGUSR1, SIGALRM and the like -- sent to this script
alone, not to its group, frees the lock while the command still runs.

While it waits for the lock, this script prints one stderr line, `run-lock: waiting for <lock
path>`; a signal that arrives then ends it with `run-lock: interrupted while waiting for <lock
path>` and the exit 128 + N, and any signal after that one is ignored until the script exits. Where
`fcntl` is missing, on a host without it, the script says so on stderr and runs the command
unlocked.

Every exit of the script's own prints a stderr line starting `run-lock:` -- the usage line
included. The exit code alone does not tell them from the command's: a test runner may itself exit 2
or 4, so read the stderr line.

Exit codes:
  126        the command could not be run (not executable)
  127        the command was not found
  128 + N    signal N ended the command, or was sent to this script and passed on (that line:
             `run-lock: passed signal N on ...`, or `run-lock: passed signals A, B, N on ...`
             where several were, N the last), or interrupted the wait for the lock
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


def _install(handler):
    """Give every forwarded signal `handler` at once: one that arrives meanwhile waits, blocked,
    and meets the new handler. No handler is ever put back: the script exits after its last."""
    mask = getattr(signal, "pthread_sigmask", None)
    old = mask(signal.SIG_BLOCK, FORWARDED) if mask else None
    try:
        for n in FORWARDED:
            signal.signal(n, handler)
    finally:
        if mask:
            mask(signal.SIG_SETMASK, old)


def _raise(signum, frame):
    _install(_ignore)  # a second signal must not raise inside the handling of this one
    raise _Signalled(signum)


def _ignore(signum, frame):
    """A forwarded signal that arrives once this script no longer passes them on: dropped -- a
    handler that does nothing rather than SIG_IGN, since CPython reports a signal it has already
    caught as "ignored due to race condition", with a traceback, once its handler is SIG_IGN."""


def _forwarder(state):
    def forward(signum, frame):
        if state["proc"] is None:  # before the command exists: kept, sent once it does
            state["pending"] = signum
        else:
            _pass_on(state, signum)
    return forward


def _git(cwd, *args):
    """git's stdout in `cwd`, its line end stripped, or None when git fails."""
    try:
        out = subprocess.run(["git"] + list(args), cwd=cwd,
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.decode("utf-8", "surrogateescape").rstrip("\r\n")


def lock_path(cwd=None):
    """The absolute lock path for the outermost work tree `cwd` is in -- a submodule's
    superproject's, to the top -- or None when git cannot name it."""
    # resolve symlinks first: git prints the lock path relative to the directory it ran in, so
    # `..` must mean what git meant (a symlinked temp directory, as on macOS)
    top = os.path.realpath(cwd or os.getcwd())
    for _ in range(64):  # a chain of superprojects is short; the bound only stops a loop
        up = _git(top, "rev-parse", "--show-superproject-working-tree")
        # empty at the top; a git too old for the option echoes it back, which is no directory
        if not up or not os.path.isdir(up):
            break
        top = os.path.realpath(up)
    rel = _git(top, "rev-parse", "--git-path", LOCK_GIT_PATH)
    if not rel:
        return None
    return os.path.abspath(os.path.join(top, rel))


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
    state = {"proc": None, "pending": None, "passed": []}
    try:
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                code = _wait(fd, path, _forwarder(state))
                if code is not None:
                    return code
        except OSError as e:
            sys.stderr.write("run-lock: cannot lock %s: %s\n" % (path, e))
            return 4
        return _run_command(argv, state)
    finally:
        os.close(fd)  # closing the descriptor releases the lock, after the command is reaped


def _wait(fd, path, forward):
    """Wait for the lock: None once it is held, the handlers then `forward`; the exit code where a
    signal ended the wait. Every handler swap is inside the try, so a signal at any point of it
    ends in the interrupted line or is kept for the command, never in a traceback."""
    try:
        _install(_raise)
        sys.stderr.write("run-lock: waiting for %s\n" % path)
        sys.stderr.flush()
        fcntl.flock(fd, fcntl.LOCK_EX)
        _install(forward)  # held: a signal from here is kept for the command, as before it starts
    except _Signalled as s:
        sys.stderr.write("run-lock: interrupted while waiting for %s\n" % path)
        return 128 + s.signum
    return None


def _run_command(argv, state=None):
    if state is None:
        state = {"proc": None, "pending": None, "passed": []}
    _install(_forwarder(state))
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
    # from here to the script's exit none is passed on, so none can come after `passed` is read,
    # and none can cut the group's wait short
    _install(_ignore)
    if state["passed"]:
        _end_group(state["proc"])
    if state["passed"]:
        code = 128 + state["passed"][-1]
        sys.stderr.write("run-lock: passed signal%s %s on to the command; exiting %d\n"
                         % ("s" if len(state["passed"]) > 1 else "",
                            ", ".join(str(n) for n in state["passed"]), code))
        return code
    return 128 - rc if rc < 0 else rc


def _pass_on(state, signum):
    """Pass a signal received on to the command's group; count it only where the group took it."""
    try:
        os.killpg(state["proc"].pid, signum)
    except OSError:  # the group is gone, or none of it could be signalled: nothing was passed on
        return
    state["passed"].append(signum)


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

    def alive(pid):
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        try:  # a zombie answers kill(0) too; where /proc exists, read its state
            with open("/proc/%d/stat" % pid) as f:
                return f.read().rsplit(")", 1)[1].split()[0] != "Z"
        except (OSError, IndexError):
            return True

    def kill_pidfile(path):
        try:
            with open(path) as f:
                os.kill(int(f.read()), signal.SIGKILL)
        except (OSError, ValueError):
            pass

    def test_normal_exit_releases_at_once():
        # the leader exits at once and leaves a daemon in its group: the call itself ends at once
        # and the daemon is left running, where a wait for the group would take the 2-second grace
        # and then kill it
        repo = new_repo("daemon")
        pidfile = os.path.join(repo, "pid")
        try:
            t0 = time.time()
            a = subprocess.run(lock_cmd("sh", "-c", "sleep 30 >/dev/null 2>&1 & echo $! > pid"),
                               cwd=repo, timeout=10)
            took = time.time() - t0
            assert a.returncode == 0, a.returncode
            assert took < 1.0, "the call waited %.2fs for a daemon in its group" % took
            with open(pidfile) as f:
                assert alive(int(f.read())), "the daemon in the group was killed"
            t0 = time.time()
            assert subprocess.run(lock_cmd("true"), cwd=repo, timeout=10).returncode == 0
            took = time.time() - t0
            assert took < 1.0, "a daemon in the group held the lock for %.2fs" % took
        finally:
            kill_pidfile(pidfile)

    def test_pass_on_counts_only_delivered():
        # a signal the group's kill refuses -- the group already gone -- is not counted as passed on
        p = subprocess.Popen(["true"], start_new_session=True)
        p.wait()
        state = {"proc": p, "pending": None, "passed": []}
        _pass_on(state, signal.SIGTERM)
        assert state["passed"] == [], "counted as passed on: %r" % state["passed"]

    def test_signal_after_wait_still_waits_for_group():
        # a signal passed on after the leader is reaped must still be followed by the wait for the
        # group: the hook raises SIGHUP at the script's first signal.signal call after wait() has
        # returned, and records each wait for the group in place of making it
        import io
        repo = new_repo("afterwait")
        pidfile = os.path.join(repo, "pid")
        real_popen, real_signal, real_end, real_err = subprocess.Popen, signal.signal, _end_group, sys.stderr
        real_mask = getattr(signal, "pthread_sigmask", None)
        saved = [(n, signal.getsignal(n)) for n in FORWARDED]
        seen = {"waited": False, "fired": False, "group_waits": 0}

        class Hooked(real_popen):
            def wait(self, *a, **k):
                rc = real_popen.wait(self, *a, **k)
                seen["waited"] = True
                return rc

        def fire():
            if seen["waited"] and not seen["fired"]:
                seen["fired"] = True
                signal.raise_signal(signal.SIGHUP)  # its handler runs here, before the call

        def hook(n, h):
            fire()
            return real_signal(n, h)

        def hook_mask(how, mask):
            fire()
            return real_mask(how, mask)

        def group_wait(proc):
            seen["group_waits"] += 1

        real_signal(signal.SIGHUP, lambda s, f: None)  # this process must outlive a stray one
        try:
            subprocess.Popen, signal.signal, sys.stderr = Hooked, hook, io.StringIO()
            if real_mask is not None:
                signal.pthread_sigmask = hook_mask
            globals()["_end_group"] = group_wait
            rc = _run_command(["sh", "-c", "sleep 30 >/dev/null 2>&1 & echo $! > '%s'" % pidfile])
        finally:
            subprocess.Popen, signal.signal, sys.stderr = real_popen, real_signal, real_err
            if real_mask is not None:
                signal.pthread_sigmask = real_mask
            globals()["_end_group"] = real_end
            for n, h in saved:
                real_signal(n, h)
            kill_pidfile(pidfile)
        assert seen["fired"], "the hook never fired"
        assert rc == 128 + signal.SIGHUP, "the hook's signal did not reach the group: %s" % rc
        assert seen["group_waits"] == 1, "signal passed on with %d waits for the group" % seen["group_waits"]

    def test_two_signals_while_waiting():
        # two signals caught at once while waiting for the lock: the first ends the wait and the
        # second is ignored -- no traceback, the exit 128 + N and the run-lock: line
        repo = new_repo("waittwo")
        holder = subprocess.Popen(lock_cmd("sh", "-c", "echo up > up; sleep 5"), cwd=repo,
                                  stderr=subprocess.DEVNULL)
        try:
            assert wait_for(os.path.join(repo, "up")), "holder never started"
            w = subprocess.Popen(lock_cmd("true"), cwd=repo, stderr=subprocess.PIPE)
            first = w.stderr.readline().decode()  # the handlers are in before this line prints
            assert first.startswith("run-lock: waiting for "), first
            w.send_signal(signal.SIGSTOP)  # stopped, it takes both before it handles either
            w.send_signal(signal.SIGINT)
            w.send_signal(signal.SIGTERM)
            w.send_signal(signal.SIGCONT)
            err = first + w.communicate(timeout=10)[1].decode()
            assert w.returncode in (128 + 2, 128 + 15), (w.returncode, err)
            assert "run-lock: interrupted while waiting for " in err and "Traceback" not in err, err
        finally:
            holder.terminate()  # passed on to its group, which ends at once
            holder.wait()

    def test_signal_as_the_wait_ends():
        # a signal that lands as the wait for the lock ends -- while the script swaps the wait's
        # handlers for the command's -- ends in the run's own exit or a run-lock: line, never in a
        # traceback: the hook raises SIGTERM at the first signal.signal call after the waiting
        # flock returns
        import io
        repo = new_repo("waitend")
        holder = subprocess.Popen(lock_cmd("sh", "-c", "echo up > up; sleep 1"), cwd=repo,
                                  stderr=subprocess.DEVNULL)
        real_flock, real_signal, real_err = fcntl.flock, signal.signal, sys.stderr
        saved = [(n, signal.getsignal(n)) for n in FORWARDED]
        seen = {"held": False, "fired": False}

        def flock(fd, op):
            got = real_flock(fd, op)
            if not op & fcntl.LOCK_NB:
                seen["held"] = True
            return got

        def hook(n, h):
            if seen["held"] and not seen["fired"]:
                seen["fired"] = True
                signal.raise_signal(signal.SIGTERM)
            return real_signal(n, h)

        err, raised, rc, cwd = io.StringIO(), None, None, os.getcwd()
        try:
            assert wait_for(os.path.join(repo, "up")), "holder never started"
            for n in FORWARDED:  # this process must outlive a stray one
                real_signal(n, lambda s, f: None)
            os.chdir(repo)
            fcntl.flock, signal.signal, sys.stderr = flock, hook, err
            try:
                rc = run(["true"])
            except BaseException as e:  # the defect: an uncaught _Signalled
                raised = e
        finally:
            fcntl.flock, signal.signal, sys.stderr = real_flock, real_signal, real_err
            for n, h in saved:
                real_signal(n, h)
            os.chdir(cwd)
            holder.wait()
        assert raised is None, "uncaught %r; stderr %r" % (raised, err.getvalue())
        assert seen["fired"], "the hook never fired"
        out = err.getvalue()
        assert rc == 0 or (rc == 128 + signal.SIGTERM and ("run-lock: passed signal 15 on" in out
                                                         or "run-lock: interrupted while waiting" in out)), \
            (rc, out)

    def test_submodule_shares_lock():
        # a suite inside a submodule takes the outermost work tree's lock, through every level
        g = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false",
             "-c", "protocol.file.allow=always"]
        repos = {}
        for name in ("sm-src", "sm-inner", "sm-super"):
            repos[name] = new_repo(name)
            sh(*(g + ["commit", "-q", "--allow-empty", "-m", "x"]), cwd=repos[name], check=True)
        sup = repos["sm-super"]
        sub = os.path.join(sup, "sub")
        inner = os.path.join(sub, "inner")
        sh(*(g + ["submodule", "add", "-q", repos["sm-src"], "sub"]), cwd=sup, check=True)
        sh(*(g + ["submodule", "add", "-q", repos["sm-inner"], "inner"]), cwd=sub, check=True)
        git_dir = sh("git", "rev-parse", "--absolute-git-dir", cwd=sup).stdout.decode().strip()
        want = os.path.join(git_dir, "dev-workflows", "run.lock")
        for d in (sup, sub, inner):
            assert lock_path(d) == want, (d, lock_path(d), want)
        assert subprocess.run(lock_cmd("true"), cwd=inner).returncode == 0
        assert os.path.isfile(want), "no lock file at %s" % want
        own = sh("git", "rev-parse", "--absolute-git-dir", cwd=inner).stdout.decode().strip()
        assert not os.path.exists(os.path.join(own, "dev-workflows")), "the submodule took its own lock"

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
             test_normal_exit_releases_at_once, test_pass_on_counts_only_delivered,
             test_signal_after_wait_still_waits_for_group, test_two_signals_while_waiting,
             test_signal_as_the_wait_ends,
             test_submodule_shares_lock, test_no_fcntl]
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

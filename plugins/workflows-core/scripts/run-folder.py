#!/usr/bin/env python3
"""Run folder: a long command's per-run state folder, its identity and its owner.

Usage:
  run-folder.py open --command <plugin>.<command> [--key <KEY>] --specs <dir> [--workdir <dir>] --args <string>
  run-folder.py resume <folder>
  run-folder.py discard <folder>
  run-folder.py close <folder>
  run-folder.py phase <folder> <name>
  run-folder.py log <folder> <text>
  run-folder.py fact <folder> <name> [--set <value>]
  run-folder.py --selftest

Folders live under ${XDG_STATE_HOME:-$HOME/.local/state}/ai-workflows/runs/<run-key>/ (mode 0700); an
empty XDG_STATE_HOME counts as unset and a relative one is ignored. The run key is
<plugin>.<command>-<KEY>-<h> keyed, <plugin>.<command>-<h> keyless, <h> being the first 8 hex digits of a
SHA-256 over the identity: the specs repository's origin URL (its physical path where it has none), the
working directory's repository root only where --workdir is passed, and the canonical arguments only for a
keyless run.

Every subcommand prints one JSON object on stdout. open reports state "new" (folder made), "unfinished" (an
earlier run's folder; ownership is not taken) or "unavailable" (the folder cannot be made or written; exit 0,
the caller goes on without a run folder). Each open first removes run folders no session wrote for 30 days.
The owner is CLAUDE_CODE_SESSION_ID (null where unset or empty); a writing call from another session, both
non-null, exits 9 and writes nothing. discard and close refuse a path that is not a direct child of the runs
root holding a run.json. Exit codes: 0 done; 2 usage or could not run; 9 taken over.
Standard library only.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid

STALE_DAYS = 30
GIT_TIMEOUT = 5


class CannotRun(Exception):
    pass


class TakenOver(Exception):
    pass


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False, indent=1) + "\n")
    sys.stdout.flush()


def now_iso():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def session_id():
    return os.environ.get("CLAUDE_CODE_SESSION_ID") or None


def runs_root():
    xdg = os.environ.get("XDG_STATE_HOME")
    if xdg and os.path.isabs(xdg):
        base = xdg
    else:
        base = os.path.join(os.path.expanduser("~"), ".local", "state")
    return os.path.join(base, "ai-workflows", "runs")


def write_json_atomic(path, obj):
    directory = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def git_value(directory, *args):
    try:
        r = subprocess.run(["git", "-C", directory, *args], stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = r.stdout.decode("utf-8", errors="replace").strip()
    return out if r.returncode == 0 and out else None


def specs_identity(specs):
    return git_value(specs, "config", "--get", "remote.origin.url") or os.path.realpath(specs)


def workdir_identity(workdir):
    top = git_value(workdir, "rev-parse", "--show-toplevel")
    return os.path.realpath(top or workdir)


def make_identity(specs, workdir, args, keyless):
    identity = {"specs": specs_identity(specs)}
    if workdir:
        identity["workdir"] = workdir_identity(workdir)
    if keyless:
        identity["args"] = " ".join(args.split())
    return identity


def sha256_hex(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_run_key(command, key, identity):
    digest = sha256_hex(json.dumps({"command": command, "key": key, "identity": identity},
                                       sort_keys=True, ensure_ascii=True))[:8]
    return "%s-%s-%s" % (command, key, digest) if key else "%s-%s" % (command, digest)


def folder_path(folder):
    """The folder as an absolute path, or CannotRun unless it is a direct child of the runs root holding a run.json."""
    p = os.path.abspath(folder)
    name = os.path.basename(p)
    if not name or os.path.realpath(os.path.dirname(p)) != os.path.realpath(runs_root()):
        raise CannotRun("not a run folder under the runs root: " + folder)
    if os.path.islink(p) or not os.path.isdir(p) or not os.path.isfile(os.path.join(p, "run.json")):
        raise CannotRun("not a run folder (no run.json): " + folder)
    return p


def load_run(folder):
    path = os.path.join(folder_path(folder), "run.json")
    try:
        with open(path, encoding="utf-8") as fh:
            run = json.load(fh)
    except (OSError, ValueError) as e:
        raise CannotRun("unreadable run.json in %s: %s" % (folder, e))
    if not isinstance(run, dict):
        raise CannotRun("malformed run.json in " + folder)
    return run


def save_run(folder, run):
    run["updated"] = now_iso()
    write_json_atomic(os.path.join(folder_path(folder), "run.json"), run)


def check_owner(run):
    owner, me = run.get("owner"), session_id()
    if owner is not None and me is not None and owner != me:
        raise TakenOver("run taken over: owned by session %s, this is session %s" % (owner, me))


def append_progress(folder, text):
    line = "%s %s %s\n" % (now_iso(), session_id() or "-", text.replace("\n", " "))
    with open(os.path.join(folder_path(folder), "progress.md"), "a", encoding="utf-8") as fh:
        fh.write(line)


def tree_bytes(path):
    total = 0
    for dirpath, _dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.lstat(os.path.join(dirpath, f)).st_size
            except OSError:
                pass
    return total


def last_written(path):
    try:
        with open(os.path.join(path, "run.json"), encoding="utf-8") as fh:
            stamp = json.load(fh)["updated"]
        return datetime.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc).timestamp()
    except (OSError, ValueError, KeyError, TypeError):
        return os.stat(path).st_mtime


def prune(root):
    cutoff = datetime.datetime.now(datetime.timezone.utc).timestamp() - STALE_DAYS * 86400
    count = size = 0
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if os.path.islink(path) or not os.path.isdir(path):
            continue
        try:
            if last_written(path) < cutoff:
                n = tree_bytes(path)
                shutil.rmtree(path)
                count, size = count + 1, size + n
        except OSError:
            continue
    return {"count": count, "bytes": size}


def summarize(run):
    owner, me = run.get("owner"), session_id()
    results, facts = run.get("results"), run.get("facts")
    return {"started": run.get("started"), "updated": run.get("updated"), "owner": owner,
            "other_session": owner is not None and me is not None and owner != me,
            "args": run.get("args"), "last_phase": run.get("last_phase"),
            "results": len(results) if isinstance(results, (dict, list)) else 0,
            "facts": sorted(facts) if isinstance(facts, dict) else []}


def cmd_open(a):
    keyless = not a.key
    identity = make_identity(a.specs, a.workdir, a.args, keyless)
    run_key = make_run_key(a.command, a.key, identity)
    pruned = {"count": 0, "bytes": 0}
    try:
        root = runs_root()
        os.makedirs(root, mode=0o700, exist_ok=True)
        pruned = prune(root)
        if pruned["count"]:
            print("NOTE: removed %d run folder(s) not written for %d days (%d bytes)"
                  % (pruned["count"], STALE_DAYS, pruned["bytes"]), file=sys.stderr)
        folder = os.path.join(root, run_key)
        try:
            run = load_run(folder)
        except CannotRun:
            run = None
        if run is not None:
            emit({"state": "unfinished", "folder": folder, "run_key": run_key, "reason": "",
                  "pruned": pruned, "summary": summarize(run)})
            return 0
        os.makedirs(folder, mode=0o700, exist_ok=True)
        os.chmod(folder, 0o700)
        started = now_iso()
        run = {"command": a.command, "key": a.key, "run_key": run_key, "identity": identity,
               "args": a.args, "run_id": uuid.uuid4().hex, "started": started, "updated": started,
               "owner": session_id(), "last_phase": None, "facts": {}}
        write_json_atomic(os.path.join(folder, "run.json"), run)
        append_progress(folder, "opened %s" % run_key)
        emit({"state": "new", "folder": folder, "run_key": run_key, "reason": "",
              "pruned": pruned, "summary": summarize(run)})
    except OSError as e:
        reason = "%s: %s" % (type(e).__name__, e)
        print("NOTE: no run folder (%s); continuing without one" % reason, file=sys.stderr)
        emit({"state": "unavailable", "folder": None, "run_key": run_key, "reason": reason,
              "pruned": pruned, "summary": None})
    return 0


def cmd_resume(a):
    run = load_run(a.folder)
    run["owner"] = session_id()
    save_run(a.folder, run)
    append_progress(a.folder, "resumed")
    emit({"owner": run["owner"]})
    return 0


def remove_folder(folder):
    path = folder_path(folder)
    shutil.rmtree(path)
    emit({"removed": True})
    return 0


def cmd_discard(a):
    # Not owner-checked: starting over is the user's answer to "another session owns this run".
    load_run(a.folder)
    return remove_folder(a.folder)


def cmd_close(a):
    check_owner(load_run(a.folder))
    return remove_folder(a.folder)


def cmd_phase(a):
    run = load_run(a.folder)
    check_owner(run)
    run["last_phase"] = a.name
    save_run(a.folder, run)
    append_progress(a.folder, "phase " + a.name)
    emit({"last_phase": a.name})
    return 0


def cmd_log(a):
    run = load_run(a.folder)
    check_owner(run)
    append_progress(a.folder, a.text)
    save_run(a.folder, run)
    emit({})
    return 0


def cmd_fact(a):
    run = load_run(a.folder)
    facts = run.setdefault("facts", {})
    if a.set is not None:
        check_owner(run)
        facts[a.name] = a.set
        save_run(a.folder, run)
    emit({"name": a.name, "value": facts.get(a.name)})
    return 0


COMMANDS = {"open": cmd_open, "resume": cmd_resume, "discard": cmd_discard, "close": cmd_close,
            "phase": cmd_phase, "log": cmd_log, "fact": cmd_fact}


# ---------------------------------------------------------------- selftest

def selftest():
    failures = []
    results = []

    with tempfile.TemporaryDirectory() as tmp0:
        tmp0 = os.path.realpath(tmp0)
        counter = [0]

        def newdir(label="d"):
            counter[0] += 1
            p = os.path.join(tmp0, "%s%d" % (label, counter[0]))
            os.makedirs(p)
            return p

        def env_for(home, session=None, xdg=None):
            env = {k: v for k, v in os.environ.items()
                   if k not in ("XDG_STATE_HOME", "CLAUDE_CODE_SESSION_ID")}
            env["HOME"] = home
            env["GIT_CONFIG_GLOBAL"] = os.devnull
            env["GIT_CONFIG_NOSYSTEM"] = "1"
            if xdg is not None:
                env["XDG_STATE_HOME"] = xdg
            if session is not None:
                env["CLAUDE_CODE_SESSION_ID"] = session
            return env

        def cli(args, home, session=None, xdg=None, cwd=None):
            r = subprocess.run([sys.executable, os.path.abspath(__file__), *args],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=env_for(home, session, xdg), cwd=cwd)
            out = r.stdout.decode("utf-8")
            try:
                obj = json.loads(out) if out.strip() else None
            except ValueError:
                obj = None
            return r.returncode, obj, r.stderr.decode("utf-8")

        def git(cwd, *args):
            subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-C", cwd, *args],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=env_for(cwd))

        def repo(origin=None):
            p = newdir("repo")
            git(p, "init", "-q")
            if origin:
                git(p, "remote", "add", "origin", origin)
            return p

        CMD = "product-workflows.prd-ground"

        def op(home, specs, session=None, key="MWC-001-01", args="a", extra=(), xdg=None, cwd=None):
            a = ["open", "--command", CMD, "--specs", specs, "--args", args, *extra]
            if key is not None:
                a[3:3] = ["--key", key]
            return cli(a, home, session, xdg, cwd)

        def read(path):
            with open(path, encoding="utf-8") as fh:
                return fh.read()

        def case(name):
            def deco(fn):
                try:
                    fn()
                    results.append("PASS " + name)
                except Exception as e:  # AssertionError or anything unexpected
                    failures.append(name)
                    results.append("FAIL %s: %s: %s" % (name, type(e).__name__, e))
                return fn
            return deco

        def expect(cond, detail=""):
            if not cond:
                raise AssertionError(detail)

        @case("root-default")
        def _():
            home = newdir("home")
            rc, o, _e = op(home, repo())
            expect(rc == 0 and o["state"] == "new", (rc, o))
            expect(o["folder"].startswith(os.path.join(home, ".local/state/ai-workflows/runs") + os.sep), o["folder"])

        @case("root-empty-and-relative")
        def _():
            for xdg in ("", "rel/dir"):
                home, cwd = newdir("home"), newdir("cwd")
                rc, o, _e = op(home, repo(), xdg=xdg, cwd=cwd)
                expect(rc == 0 and o["folder"].startswith(os.path.join(home, ".local/state/ai-workflows/runs")), (xdg, o))
                expect(not os.path.exists(os.path.join(cwd, "rel")), "relative XDG_STATE_HOME was used")

        @case("open-new-0700")
        def _():
            home, specs = newdir("home"), repo("https://example.com/a.git")
            rc, o, _e = op(home, specs, session="A", args="x y")
            expect(o["state"] == "new", o)
            expect(stat.S_IMODE(os.stat(o["folder"]).st_mode) == 0o700, oct(os.stat(o["folder"]).st_mode))
            run = json.loads(read(os.path.join(o["folder"], "run.json")))
            for k in ("command", "key", "identity", "args", "run_id", "started", "owner"):
                expect(k in run, (k, sorted(run)))
            expect(run["command"] == CMD and run["key"] == "MWC-001-01" and run["owner"] == "A" and run["args"] == "x y", run)
            expect(run["run_id"], run)

        @case("run-key-shape")
        def _():
            home, specs = newdir("home"), repo()
            rc, o, _e = op(home, specs)
            expect(re.match(r"^product-workflows\.prd-ground-MWC-001-01-[0-9a-f]{8}$", o["run_key"]), o["run_key"])
            rc, o, _e = op(home, specs, key=None)
            expect(re.match(r"^product-workflows\.prd-ground-[0-9a-f]{8}$", o["run_key"]), o["run_key"])

        @case("identity-specs-origin")
        def _():
            home = newdir("home")
            _a, o1, _e = op(home, repo("https://example.com/one.git"))
            _a, o2, _e = op(home, repo("https://example.com/two.git"))
            expect(o1["folder"] != o2["folder"], (o1["folder"], o2["folder"]))

        @case("identity-specs-path")
        def _():
            home, specs = newdir("home"), repo()
            link = os.path.join(newdir("lnk"), "spelled")
            os.symlink(specs, link)
            _a, o1, _e = op(home, specs)
            _a, o2, _e = op(home, link)
            expect(o1["folder"] == o2["folder"], (o1["folder"], o2["folder"]))

        @case("identity-workdir-optional")
        def _():
            home, specs = newdir("home"), repo("https://example.com/s.git")
            _a, o1, _e = op(home, specs, cwd=repo())
            _a, o2, _e = op(home, specs, cwd=repo())
            expect(o1["folder"] == o2["folder"], "cwd leaked into identity")
            _a, o3, _e = op(home, specs, extra=["--workdir", repo()])
            _a, o4, _e = op(home, specs, extra=["--workdir", repo()])
            expect(o3["folder"] != o4["folder"] and o3["folder"] != o1["folder"], "workdir not in identity")

        @case("keyless-args")
        def _():
            home, specs = newdir("home"), repo()
            _a, o1, _e = op(home, specs, key=None, args="one")
            _a, o2, _e = op(home, specs, key=None, args="two")
            _a, o3, _e = op(home, specs, key=None, args="one")
            expect(o1["folder"] != o2["folder"] and o1["folder"] == o3["folder"], (o1["folder"], o2["folder"], o3["folder"]))
            _a, k1, _e = op(home, specs, args="one")
            _a, k2, _e = op(home, specs, args="two")
            expect(k1["folder"] == k2["folder"], "keyed run keyed on args")

        @case("open-unfinished")
        def _():
            home, specs = newdir("home"), repo()
            _a, o1, _e = op(home, specs, session="A")
            rc, p, _e = cli(["phase", o1["folder"], "p5"], home, "A")
            expect(rc == 0 and p == {"last_phase": "p5"}, (rc, p))
            rc, o2, _e = op(home, specs, session="A")
            expect(o2["state"] == "unfinished" and o2["summary"]["last_phase"] == "p5", o2)
            expect(o2["summary"]["owner"] == "A" and o2["summary"]["other_session"] is False, o2)
            expect(json.loads(read(os.path.join(o1["folder"], "run.json")))["owner"] == "A", "owner changed")

        @case("other-session")
        def _():
            home, specs = newdir("home"), repo()
            op(home, specs, session="A")
            _a, o, _e = op(home, specs, session="B")
            expect(o["state"] == "unfinished" and o["summary"]["other_session"] is True, o)
            expect(o["summary"]["owner"] == "A", o)

        @case("owner-guard")
        def _():
            home, specs = newdir("home"), repo()
            _a, o, _e = op(home, specs, session="A")
            folder = o["folder"]
            rc, r, _e = cli(["resume", folder], home, "B")
            expect(rc == 0 and r == {"owner": "B"}, (rc, r))
            before = read(os.path.join(folder, "progress.md"))
            rc, out, err = cli(["log", folder, "stale write"], home, "A")
            expect(rc == 9 and out is None and "B" in err, (rc, out, err))
            expect(read(os.path.join(folder, "progress.md")) == before, "a taken-over write landed")
            rc, out, _e = cli(["log", folder, "fresh write"], home, "B")
            expect(rc == 0 and out == {}, (rc, out))
            expect("fresh write" in read(os.path.join(folder, "progress.md")), "owner write missing")

        @case("owner-null-passes")
        def _():
            home, specs = newdir("home"), repo()
            _a, o, _e = op(home, specs, session="A")
            rc, _o, _e = cli(["log", o["folder"], "no session"], home)
            expect(rc == 0, rc)
            home2, specs2 = newdir("home"), repo()
            _a, o2, _e = op(home2, specs2)
            rc, _o, _e = cli(["log", o2["folder"], "owner unset"], home2, "B")
            expect(rc == 0, rc)

        @case("unavailable")
        def _():
            blocker = os.path.join(newdir("ro"), "file")
            with open(blocker, "w") as fh:
                fh.write("not a directory")
            for xdg in (None, os.path.join(blocker, "x")):
                home = os.path.join(blocker, "home")
                rc, o, err = op(home, repo(), xdg=xdg)
                expect(rc == 0 and o["state"] == "unavailable" and o["reason"], (rc, o))
                expect("NOTE:" in err, err)

        @case("prune-30-days")
        def _():
            home, specs = newdir("home"), repo()
            _a, first, _e = op(home, repo(), key="K-1")
            root = os.path.dirname(first["folder"])
            now = datetime.datetime.now(datetime.timezone.utc)
            for name, days in (("old-run", 31), ("recent-run", 29)):
                d = os.path.join(root, name)
                os.makedirs(d)
                stamp = (now - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
                with open(os.path.join(d, "run.json"), "w") as fh:
                    json.dump({"updated": stamp}, fh)
                with open(os.path.join(d, "blob"), "w") as fh:
                    fh.write("12345")
            rc, o, err = op(home, specs, key="K-3")
            expect(not os.path.exists(os.path.join(root, "old-run")), "31-day folder kept")
            expect(os.path.exists(os.path.join(root, "recent-run")), "29-day folder removed")
            expect(o["pruned"]["count"] == 1 and o["pruned"]["bytes"] >= 5, o["pruned"])
            expect(err.count("NOTE:") == 1, err)

        @case("close-refuses-outside")
        def _():
            home, specs = newdir("home"), repo()
            _a, o, _e = op(home, specs)
            root = os.path.dirname(o["folder"])
            outside = newdir("x")
            with open(os.path.join(outside, "run.json"), "w") as fh:
                fh.write("{}")
            for target in (outside, root):
                for sub in ("close", "discard"):
                    rc, out, _e = cli([sub, target], home)
                    expect(rc == 2 and out is None, (sub, target, rc))
            expect(os.path.exists(outside) and os.path.exists(o["folder"]), "something was removed")
            rc, out, _e = cli(["close", o["folder"]], home)
            expect(rc == 0 and out == {"removed": True} and not os.path.exists(o["folder"]), (rc, out))

        @case("discard-then-new")
        def _():
            home, specs = newdir("home"), repo()
            _a, o1, _e = op(home, specs)
            id1 = json.loads(read(os.path.join(o1["folder"], "run.json")))["run_id"]
            rc, out, _e = cli(["discard", o1["folder"]], home)
            expect(rc == 0 and out == {"removed": True}, (rc, out))
            _a, o2, _e = op(home, specs)
            id2 = json.loads(read(os.path.join(o2["folder"], "run.json")))["run_id"]
            expect(o2["state"] == "new" and id1 != id2, (o2["state"], id1, id2))

        @case("fact-roundtrip")
        def _():
            home, specs = newdir("home"), repo()
            _a, o, _e = op(home, specs)
            rc, out, _e = cli(["fact", o["folder"], "pin:backend", "--set", "abc"], home)
            expect(rc == 0 and out == {"name": "pin:backend", "value": "abc"}, (rc, out))
            rc, out, _e = cli(["fact", o["folder"], "pin:backend"], home)
            expect(out == {"name": "pin:backend", "value": "abc"}, out)
            rc, out, _e = cli(["fact", o["folder"], "unset"], home)
            expect(out == {"name": "unset", "value": None}, out)

    for line in results:
        print(line)
    return 1 if failures else 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(prog="run-folder.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    o.add_argument("--command", required=True)
    o.add_argument("--key")
    o.add_argument("--specs", required=True)
    o.add_argument("--workdir")
    o.add_argument("--args", required=True)
    for name in ("resume", "discard", "close"):
        sub.add_parser(name).add_argument("folder")
    p = sub.add_parser("phase")
    p.add_argument("folder")
    p.add_argument("name")
    lg = sub.add_parser("log")
    lg.add_argument("folder")
    lg.add_argument("text")
    f = sub.add_parser("fact")
    f.add_argument("folder")
    f.add_argument("name")
    f.add_argument("--set")
    args = ap.parse_args(argv)
    try:
        return COMMANDS[args.cmd](args)
    except TakenOver as e:
        print("run-folder: " + str(e), file=sys.stderr)
        return 9
    except CannotRun as e:
        print("run-folder: " + str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print("run-folder: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

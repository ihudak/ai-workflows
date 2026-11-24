#!/usr/bin/env python3
"""Run folder: a long command's per-run state folder, its identity and its owner.

Usage:
  run-folder.py open --command <plugin>.<command> [--key <KEY>] --specs <dir> [--workdir <dir>] --args <string>
  run-folder.py resume <folder> [--args <string>]
  run-folder.py discard <folder>
  run-folder.py close <folder>
  run-folder.py phase <folder> <name>
  run-folder.py log <folder> <text>
  run-folder.py fact <folder> <name> [--set <value>]
  run-folder.py dispatch <folder> <id> --area main|blind --agent <name> --agent-file <path> --model <id>
                --input <file|-> [--attach <path relative to the folder>]... [--redo]
  run-folder.py done <folder> <id> [--from <file|->] [--pin <name>=<value>]...
  run-folder.py gate <folder> <gate-id> --shown <file|->
  run-folder.py gate-record <folder> <gate-id> --shown <file|-> --answer <text> [--keep-shown]
  run-folder.py answers <folder> [--match <substring>]
  run-folder.py put <folder> scratch/<path> --from <file|->
  run-folder.py writer <folder> <id> --tree <dir> [--scope <rel>]... --agent <name> --agent-file <path>
                --model <id> --input <file|-> [--attach <path relative to the folder>]... [--redo]
  run-folder.py tree-note <folder> --tree <dir> [--scope <rel>]...
  run-folder.py effect <folder> <effect-id> start|done|state
  run-folder.py stale <folder> [--agent <name>=<file>]... [--model <name>=<id>]...
  run-folder.py keep <folder> --ids <id>... [--agent <name>=<file>]... [--model <name>=<id>]...
  run-folder.py kept <folder>
  run-folder.py results <folder> [--match <substring>]
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
non-null, exits 9 and writes nothing. resume --args records the arguments given now in place of the run's.
discard and close refuse a path that is not a direct child of the runs root holding a run.json; both wait for
the write lock, move the folder off its path, release the lock and then remove it. Exit codes: 0 done; 2
usage or could not run; 3 done found no result file; 9 taken over (another session owns the run, or its
folder was removed by a Start over).

A dispatch is saved before the agent runs (inputs/<id>.md) and names its result file, results/<id>.<nonce>.md,
a nonce drawn anew by each dispatch and recorded with it, so that an agent of an earlier dispatch of the same
id writes a file no record names; a re-dispatch removes the result files the earlier records named. A result
is reused only once `done` has recorded it, from the file its record names, and its fingerprint still matches:
SHA-256 over the input's bytes, each attached run-folder file's
bytes (sorted by path), the agent definition file's SHA-256 and the model id. `done` records, in run.json
"results", what `results`, `stale` and `keep` read; "dispatches" holds what was handed out, "gates" the
answers to questions (each with a sequence number, kept by a re-record, that `answers` lists them by), "effects"
the side effects started or finished. `put` writes a file the command generated under scratch/ (atomically,
under the lock) so a resumed run reads it back rather than generating it again; `done --pin` stores values a
reuse reports back; `dispatch --redo` dispatches anew whatever the fingerprint says; a keyless `open` with
--workdir also lists (`others`, at most 3) the unfinished runs of the same command and working directory
whose arguments differ. A writer is a dispatch that edits files in a git work tree: `writer` fingerprints it as
`dispatch` does and keeps its record under "writers", with a snapshot of the scope (the paths `git status`
lists, each with a content hash) taken before it. It prints dispatch (new receipt path), interrupted (a started
record: the paths that differ from the snapshot), intact or changed (a done record: whether each path the writer
changed still holds what the run last left there); `writer --redo` dispatches anew whatever the record says,
from a new snapshot, removing the old receipt. `done` on a started writer takes the after-snapshot, records
the paths it changed ("wrote") and merges them into the run's per-tree map "trees"; `tree-note` brings that map
up to date after an edit or commit the command made itself. `writer` takes the lock, and the owner check only
where it dispatches. --command and --key are limited to
[A-Za-z0-9._-]. A value of --args, --set or --answer, and a log text, may be one flag-shaped token.
Standard library only.
"""

import argparse
import contextlib
import datetime
import fcntl
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

STALE_DAYS = 30
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+\Z")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*\Z")
AREAS = ("main", "blind")
GIT_TIMEOUT = 5
# A writing call retries the lock only while the folder is replaced under it (a Start over in between);
# past this many attempts it stops with exit 2 rather than spin.
LOCK_ATTEMPTS = 5


class CannotRun(Exception):
    pass


class FolderGone(CannotRun):
    pass


class MissingResult(Exception):
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


def write_bytes_atomic(path, data):
    directory = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
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


def create_json_exclusive(path, obj):
    """Create path holding obj unless it exists: True when this call made it, False when it was already there.
    The content is written whole to a temporary file and linked into place, so a concurrent reader never sees
    a half-written run.json (and so never takes it for an unparseable one); where hard links are not
    available it falls back to an O_EXCL create."""
    data = (json.dumps(obj, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        try:
            os.link(tmp, path)
            return True
        except FileExistsError:
            return False
        except OSError:
            pass
        try:
            fd2 = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            return False
        with os.fdopen(fd2, "wb") as fh:
            fh.write(data)
        return True
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


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
    if not os.path.lexists(p):
        raise FolderGone("run folder no longer exists: " + folder)
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


class Lock:
    """The write lock a call holds, which close and discard release before they remove the folder."""

    def __init__(self):
        self.fd = None

    def release(self):
        if self.fd is not None:
            fd, self.fd = self.fd, None
            os.close(fd)


@contextlib.contextmanager
def write_lock(folder):
    """Hold an exclusive flock on <folder>/.lock for a whole load, modify and save of run.json, so parallel
    writing calls (sibling agents' dispatch and done, a discard) cannot lose each other's update. The lock
    taken is the one standing at that path once it is held: where the folder was removed or replaced while
    this call waited, it locks what stands there now, and none where nothing does. No lock where the folder is
    not a run folder: the call then fails or reports a takeover as it would anyway. A lock that cannot be
    taken (flock fails, as on a network home with no lock service) or whose file keeps being replaced while
    the call waits is CannotRun (exit 2): the call never writes unlocked, and never spins."""
    lock = Lock()
    try:
        try:
            path = os.path.join(folder_path(folder), ".lock")
        except CannotRun:
            path = None
        attempts = 0
        while path is not None:
            attempts += 1
            if attempts > LOCK_ATTEMPTS:
                raise CannotRun("the lock file %s kept changing while this call waited for it" % path)
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
            except OSError:
                break  # no folder stands at that path now
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                held = os.fstat(fd)
            except OSError as e:
                os.close(fd)
                raise CannotRun("could not lock %s: %s" % (path, e))
            try:
                there = os.stat(path)
            except OSError:
                there = None
            if there is not None and (held.st_dev, held.st_ino) == (there.st_dev, there.st_ino):
                lock.fd = fd
                break
            os.close(fd)
        yield lock
    finally:
        lock.release()


def needs_lock(args):
    if args.cmd in ("resume", "discard", "close", "phase", "log", "dispatch", "done", "gate-record", "keep", "put", "writer", "tree-note"):
        return True
    return (args.cmd == "fact" and args.set is not None) or (args.cmd == "effect" and args.action != "state")


def load_for_write(folder):
    """load_run plus the owner check, for a call that writes. A folder another session removed (its Start over)
    is a takeover too."""
    try:
        run = load_run(folder)
    except FolderGone:
        raise TakenOver("run taken over: its folder was removed (another session chose Start over): " + folder)
    check_owner(run)
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
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
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


OTHERS_MAX = 3


def other_runs(root, command, workdir, own_folder, own_args):
    """Unfinished keyless runs of this command in this working directory (a finished run's folder is gone)
    whose arguments differ, newest first: read from each run.json, which records the identity in clear."""
    wd = workdir_identity(workdir)
    mine = " ".join(own_args.split())
    found = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if path == own_folder or os.path.islink(path) or not os.path.isdir(path):
            continue
        try:
            with open(os.path.join(path, "run.json"), encoding="utf-8") as fh:
                run = json.load(fh)
            if run.get("command") != command or run.get("key") or run["identity"].get("workdir") != wd:
                continue
            results = run.get("results")
            args, updated = run.get("args"), run.get("updated")
            if (not isinstance(args, str) or not isinstance(updated, str) or " ".join(args.split()) == mine
                    or not isinstance(run.get("started"), (str, type(None)))
                    or not isinstance(run.get("last_phase"), (str, type(None)))
                    or not isinstance(run.get("owner"), (str, type(None)))):
                continue
            found.append({"folder": path, "args": args, "started": run.get("started"),
                          "updated": updated, "last_phase": run.get("last_phase"),
                          "results": len(results) if isinstance(results, (dict, list)) else 0,
                          "owner": run.get("owner")})
        except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
            continue
    found.sort(key=lambda r: r["updated"], reverse=True)
    return found[:OTHERS_MAX]


def cmd_open(a):
    for label, value in (("--command", a.command), ("--key", a.key)):
        if value is not None and value != "" and not NAME_RE.match(value):
            raise CannotRun("%s may hold only letters, digits, '.', '_' and '-': %r" % (label, value))
    if not a.command:
        raise CannotRun("--command is empty")
    keyless = not a.key
    identity = make_identity(a.specs, a.workdir, a.args, keyless)
    run_key = make_run_key(a.command, a.key, identity)
    pruned = {"count": 0, "bytes": 0}
    others = []
    try:
        root = runs_root()
        os.makedirs(root, mode=0o700, exist_ok=True)
        pruned = prune(root)
        if pruned["count"]:
            print("NOTE: removed %d run folder(s) not written for %d days (%d bytes)"
                  % (pruned["count"], STALE_DAYS, pruned["bytes"]), file=sys.stderr)
        folder = os.path.join(root, run_key)
        rj = os.path.join(folder, "run.json")
        if keyless and a.workdir:
            try:
                others = other_runs(root, a.command, a.workdir, folder, a.args)
            except Exception as e:  # another run's folder never fails this open
                print("NOTE: other runs not listed (%s: %s)" % (type(e).__name__, e), file=sys.stderr)
                others = []
        for _attempt in range(2):
            run = None
            if os.path.lexists(rj):
                try:
                    run = load_run(folder)
                except CannotRun as e:
                    print("NOTE: run.json did not parse (%s); starting a new run in its place" % e,
                          file=sys.stderr)
                    os.unlink(rj)
            if run is not None:
                emit({"state": "unfinished", "folder": folder, "run_key": run_key, "reason": "",
                      "pruned": pruned, "others": others, "summary": summarize(run)})
                return 0
            os.makedirs(folder, mode=0o700, exist_ok=True)
            os.chmod(folder, 0o700)
            started = now_iso()
            run = {"command": a.command, "key": a.key, "run_key": run_key, "identity": identity,
                   "args": a.args, "run_id": uuid.uuid4().hex, "started": started, "updated": started,
                   "owner": session_id(), "last_phase": None, "facts": {}}
            if create_json_exclusive(rj, run):
                append_progress(folder, "opened %s" % run_key)
                emit({"state": "new", "folder": folder, "run_key": run_key, "reason": "",
                      "pruned": pruned, "others": others, "summary": summarize(run)})
                return 0
            # another open made this run's run.json first: read theirs on the next pass
        raise OSError("run.json could not be created: " + rj)
    except OSError as e:
        reason = "%s: %s" % (type(e).__name__, e)
        print("NOTE: no run folder (%s); continuing without one" % reason, file=sys.stderr)
        emit({"state": "unavailable", "folder": None, "run_key": run_key, "reason": reason,
              "pruned": pruned, "others": [], "summary": None})
    return 0


def cmd_resume(a):
    run = load_run(a.folder)
    run["owner"] = session_id()
    if a.args is not None:
        run["args"] = a.args
    save_run(a.folder, run)
    append_progress(a.folder, "resumed")
    emit({"owner": run["owner"]})
    return 0


def remove_folder(folder, lock):
    """Move the folder off its path while the write lock is held, so no writer that waited for the lock finds
    it there, then release the lock and remove it: a file still open in a directory (the lock) keeps an NFS
    server from removing that directory. What cannot be removed of the moved folder is left to the 30-day
    pruning, the run's own path being free already."""
    path = folder_path(folder)
    aside = os.path.join(os.path.dirname(path),
                         ".removed-%s-%s" % (os.path.basename(path), uuid.uuid4().hex[:8]))
    try:
        os.rename(path, aside)
    except OSError:
        aside = None
    if lock is not None:
        lock.release()
    if aside is None:
        shutil.rmtree(path)
    else:
        shutil.rmtree(aside, ignore_errors=True)
    emit({"removed": True})
    return 0


def cmd_discard(a):
    # Not owner-checked: starting over is the user's answer to "another session owns this run". Under the
    # write lock all the same, so a writer in flight saves before the folder goes, never over the new run.
    load_run(a.folder)
    return remove_folder(a.folder, getattr(a, "lock", None))


def cmd_close(a):
    load_for_write(a.folder)
    return remove_folder(a.folder, getattr(a, "lock", None))


def cmd_phase(a):
    run = load_for_write(a.folder)
    run["last_phase"] = a.name
    save_run(a.folder, run)
    append_progress(a.folder, "phase " + a.name)
    emit({"last_phase": a.name})
    return 0


def cmd_log(a):
    run = load_for_write(a.folder)
    append_progress(a.folder, a.text)
    save_run(a.folder, run)
    emit({})
    return 0


def cmd_fact(a):
    run = load_for_write(a.folder) if a.set is not None else load_run(a.folder)
    facts = run.setdefault("facts", {})
    if a.set is not None:
        facts[a.name] = a.set
        save_run(a.folder, run)
    emit({"name": a.name, "value": facts.get(a.name)})
    return 0


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def read_input(spec):
    """Bytes of a file, or of stdin for '-'."""
    if spec == "-":
        return sys.stdin.buffer.read()
    try:
        with open(spec, "rb") as fh:
            return fh.read()
    except OSError as e:
        raise CannotRun("cannot read %s: %s" % (spec, e))


def check_id(value, what="id"):
    if not ID_RE.match(value or ""):
        raise CannotRun("%s must match %s: %r" % (what, ID_RE.pattern, value))


def check_name(value, what):
    if not value:
        raise CannotRun("%s is empty" % what)


def attach_files(folder, attach):
    """[(relative path, sha256)] sorted by path, for run-folder files named relative to the folder."""
    base = os.path.realpath(folder)
    found = {}
    for rel in attach:
        norm = os.path.normpath(rel)
        if os.path.isabs(rel) or norm == ".." or norm.startswith(".." + os.sep):
            raise CannotRun("--attach must be a path inside the run folder: " + rel)
        full = os.path.realpath(os.path.join(base, norm))
        if not full.startswith(base + os.sep) or not os.path.isfile(full):
            raise CannotRun("--attach is not a file inside the run folder: " + rel)
        with open(full, "rb") as fh:
            found[norm] = sha256_bytes(fh.read())
    return sorted(found.items())


def content_digest(input_bytes, attached):
    parts = ["input " + sha256_bytes(input_bytes)] + ["attach %s %s" % (p, h) for p, h in attached]
    return sha256_hex("\n".join(parts))


def make_fingerprint(content, agent_sha, model):
    return sha256_hex("%s\nagent %s\nmodel %s" % (content, agent_sha, model))


def area_path(folder, area, kind, did):
    return os.path.join(folder_path(folder), area, kind, did + ".md")


NONCE_HEX = 12
RESULT_REL_RE = re.compile(r"^(main|blind)/results/(.+)\.[0-9a-f]{%d}\.md\Z" % NONCE_HEX)


def recorded_result(folder, rec, did):
    """The result file a dispatch or result record names, as an absolute path, or None where the record names
    none, or one not of this id's shape under its area (`<area>/results/<id>.<nonce>.md`)."""
    rel = rec.get("result") if isinstance(rec, dict) else None
    m = RESULT_REL_RE.match(rel) if isinstance(rel, str) else None
    if not m or m.group(1) != rec.get("area") or m.group(2) != did:
        return None
    return os.path.join(folder_path(folder), *rel.split("/"))


def cmd_dispatch(a):
    check_id(a.id, "dispatch id")
    check_name(a.agent, "--agent")
    check_name(a.model, "--model")
    run = load_for_write(a.folder)
    folder = folder_path(a.folder)
    input_bytes = read_input(a.input)
    attached = attach_files(folder, a.attach or [])
    agent_sha = sha256_bytes(read_input(a.agent_file))
    content = content_digest(input_bytes, attached)
    fp = make_fingerprint(content, agent_sha, a.model)
    input_path = area_path(folder, a.area, "inputs", a.id)
    results = run.setdefault("results", {})
    rec = results.get(a.id)
    recorded = recorded_result(folder, rec, a.id)
    reusable = (not a.redo and recorded is not None and rec.get("fingerprint") == fp and rec.get("area") == a.area
                and os.path.isfile(recorded) and os.path.getsize(recorded) > 0)
    if reusable:
        save_run(folder, run)
        append_progress(folder, "dispatch %s reuse" % a.id)
        emit({"action": "reuse", "input": input_path, "result": recorded, "fingerprint": fp,
              "pins": dict(rec.get("pins") or {})})
        return 0
    # Each dispatch names a result file of its own, so an agent of an earlier dispatch of this id — a
    # superseded session's, still running — writes a file no record names, which is never read.
    rel = "%s/results/%s.%s.md" % (a.area, a.id, uuid.uuid4().hex[:NONCE_HEX])
    result_path = os.path.join(folder, *rel.split("/"))
    for d in (os.path.dirname(input_path), os.path.dirname(result_path)):
        os.makedirs(d, mode=0o700, exist_ok=True)
    write_bytes_atomic(input_path, input_bytes)
    # A result redone is a result no longer recorded: drop the record, and the files the earlier
    # dispatch and result of this id named.
    replaced = (recorded, recorded_result(folder, run.get("dispatches", {}).get(a.id), a.id))
    results.pop(a.id, None)
    if a.id in run.get("kept", []):
        run["kept"] = [k for k in run["kept"] if k != a.id]
    for old in replaced:
        if old is not None:
            try:
                os.unlink(old)
            except FileNotFoundError:
                pass
    run.setdefault("dispatches", {})[a.id] = {
        "fingerprint": fp, "content": content, "agent": a.agent, "agent_sha": agent_sha,
        "model": a.model, "area": a.area, "result": rel}
    save_run(folder, run)
    append_progress(folder, "dispatch %s made" % a.id)
    emit({"action": "dispatch", "input": input_path, "result": result_path, "fingerprint": fp})
    return 0


def cmd_done(a):
    check_id(a.id, "dispatch id")
    run = load_for_write(a.folder)
    folder = folder_path(a.folder)
    rec = run.get("dispatches", {}).get(a.id)
    wrec = (run.get("writers") or {}).get(a.id)
    if isinstance(rec, dict) and isinstance(wrec, dict):
        raise CannotRun("%s has both a dispatch and a writer record" % a.id)
    if isinstance(wrec, dict):
        if wrec.get("state") != "started":
            raise CannotRun("the writer %s is not started" % a.id)
        return finish_writer(a, run, wrec)
    if not isinstance(rec, dict):
        raise CannotRun("no dispatch recorded for " + a.id)
    pins = name_map(a.pin, "--pin")
    result_path = recorded_result(folder, rec, a.id)
    if result_path is None:
        raise CannotRun("the dispatch of %s names no result file; dispatch it again" % a.id)
    if a.from_ is not None:
        data = read_input(a.from_)
        os.makedirs(os.path.dirname(result_path), mode=0o700, exist_ok=True)
        write_bytes_atomic(result_path, data)
    if not os.path.isfile(result_path) or os.path.getsize(result_path) == 0:
        raise MissingResult("no result file (or an empty one) for %s: %s" % (a.id, result_path))
    run.setdefault("results", {})[a.id] = dict(rec, done=now_iso(), pins=pins)
    save_run(folder, run)
    append_progress(folder, "done %s" % a.id)
    emit({"recorded": True})
    return 0


def git_run(tree, *args):
    r = subprocess.run(["git", "-C", tree, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       timeout=GIT_TIMEOUT * 6)
    if r.returncode != 0:
        raise CannotRun("git %s failed in %s: %s" % (" ".join(args[:2]), tree,
                                                     r.stderr.decode("utf-8", "replace").strip()))
    return r.stdout


def tree_root(tree):
    """(physical path of tree, its work tree's top level; trees are keyed by the top level) for a directory inside a git work tree, else exit 2."""
    if not tree or not os.path.isdir(tree):
        raise CannotRun("--tree is not a directory: %r" % tree)
    real = os.path.realpath(tree)
    try:
        inside = git_run(real, "rev-parse", "--is-inside-work-tree").decode().strip()
        top = git_run(real, "rev-parse", "--show-toplevel").decode("utf-8", "surrogateescape").strip()
    except (CannotRun, OSError, subprocess.SubprocessError):
        raise CannotRun("--tree is not a git work tree: " + tree)
    if inside != "true":
        raise CannotRun("--tree is not a git work tree: " + tree)
    return real, os.path.realpath(top)


def hash_path(top, rel):
    """SHA-256 of a file's bytes, of a symlink's text, "dir" for a directory, "-" where absent."""
    full = os.path.join(top, rel)
    try:
        if os.path.islink(full):
            return sha256_bytes(os.readlink(full).encode("utf-8", "surrogateescape"))
        if os.path.isdir(full):
            return "dir"
        h = hashlib.sha256()
        with open(full, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return "-"


def scope_args(real, top, scope):
    """Pathspecs relative to the work tree's top level, for --scope values given relative to the tree."""
    out = []
    for sc in scope or []:
        full = os.path.normpath(os.path.join(real, sc))
        rel = os.path.relpath(full, top)
        if os.path.isabs(sc) or rel == ".." or rel.startswith(".." + os.sep):
            raise CannotRun("--scope must be a path inside the tree: " + sc)
        out.append(rel)
    return sorted(set(out))


def snapshot_scope(top, scope):
    """{path: hash} of the paths `git status` lists under scope (the whole tree for none); a path not listed is
    clean. Both paths of a rename or copy count."""
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all"]
    if scope:
        args += ["--", *scope]
    fields = git_run(top, *args).split(b"\0")
    paths, i = [], 0
    while i < len(fields):
        rec = fields[i]
        i += 1
        if len(rec) < 4:
            continue
        paths.append(rec[3:].decode("utf-8", "surrogateescape"))
        if rec[:1] in (b"R", b"C") or rec[1:2] in (b"R", b"C"):
            if i < len(fields) and fields[i]:
                paths.append(fields[i].decode("utf-8", "surrogateescape"))
            i += 1
    return {p: hash_path(top, p) for p in sorted(set(paths))}


def writer_states(run, tree_key):
    return run.setdefault("trees", {}).setdefault(tree_key, {})


def cmd_writer(a):
    check_id(a.id, "writer id")
    check_name(a.agent, "--agent")
    check_name(a.model, "--model")
    real, top = tree_root(a.tree)
    scope = scope_args(real, top, a.scope)
    run = load_run(a.folder)
    folder = folder_path(a.folder)
    input_bytes = read_input(a.input)
    attached = attach_files(folder, a.attach or [])
    agent_sha = sha256_bytes(read_input(a.agent_file))
    content = content_digest(input_bytes, attached)
    fp = make_fingerprint(content, agent_sha, a.model)
    rec = (run.get("writers") or {}).get(a.id)
    rec = rec if isinstance(rec, dict) else None
    receipt = recorded_result(folder, rec, a.id) if rec else None
    if not a.redo and rec and rec.get("fingerprint") == fp and rec.get("tree") == real \
            and rec.get("scope") == scope and receipt is not None:
        before = rec.get("before") or {}
        if rec.get("state") == "started":
            now = snapshot_scope(top, scope)
            left = []
            for path in sorted(set(before) | set(now)):
                b, n = before.get(path, "clean"), now.get(path, "clean")
                if b != n:
                    left.append({"path": path, "before": b, "now": n})
            emit({"action": "interrupted", "receipt": receipt, "left": left})
            return 0
        if rec.get("state") == "done" and os.path.isfile(receipt) and os.path.getsize(receipt) > 0:
            trees = (run.get("trees") or {}).get(top) or {}
            changed = []
            for path in sorted(rec.get("wrote") or {}):
                now, expected = hash_path(top, path), trees.get(path)
                if now != expected:
                    changed.append({"path": path, "expected": expected, "now": now})
            if changed:
                emit({"action": "changed", "receipt": receipt, "changed": changed})
            else:
                emit({"action": "intact", "receipt": receipt})
            return 0
    # a dispatch (also --redo's, whatever the record says): the only branch that writes, so the only one the
    # owner check guards
    run = load_for_write(a.folder)
    before = snapshot_scope(top, scope)
    rel = "main/results/%s.%s.md" % (a.id, uuid.uuid4().hex[:NONCE_HEX])
    path = os.path.join(folder, *rel.split("/"))
    os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
    if receipt is not None:
        try:
            os.unlink(receipt)
        except FileNotFoundError:
            pass
    if a.id in run.get("kept", []):
        run["kept"] = [k for k in run["kept"] if k != a.id]
    run.setdefault("writers", {})[a.id] = {
        "fingerprint": fp, "content": content, "agent": a.agent, "agent_sha": agent_sha, "model": a.model,
        "area": "main", "result": rel, "tree": real, "scope": scope, "before": before, "state": "started",
        "at": now_iso()}
    save_run(folder, run)
    append_progress(folder, "writer %s made" % a.id)
    emit({"action": "dispatch", "receipt": path})
    return 0


def finish_writer(a, run, rec):
    folder = folder_path(a.folder)
    receipt = recorded_result(folder, rec, a.id)
    if receipt is None:
        raise CannotRun("the writer %s names no receipt file; dispatch it again" % a.id)
    real, top = tree_root(rec.get("tree"))
    if a.pin:
        raise CannotRun("--pin is for a dispatch's result, not a writer's")
    if a.from_ is not None:
        data = read_input(a.from_)
        os.makedirs(os.path.dirname(receipt), mode=0o700, exist_ok=True)
        write_bytes_atomic(receipt, data)
    if not os.path.isfile(receipt) or os.path.getsize(receipt) == 0:
        raise MissingResult("no receipt file (or an empty one) for %s: %s" % (a.id, receipt))
    before = rec.get("before") or {}
    after = snapshot_scope(top, rec.get("scope") or [])
    wrote = {}
    for path in sorted(set(before) | set(after)):
        if before.get(path, "clean") != after.get(path, "clean"):
            wrote[path] = hash_path(top, path)
    writer_states(run, top).update(wrote)
    rec.update(state="done", wrote=wrote, done=now_iso())
    save_run(folder, run)
    append_progress(folder, "done %s (writer)" % a.id)
    emit({"recorded": True})
    return 0


def cmd_tree_note(a):
    real, top = tree_root(a.tree)
    scope = scope_args(real, top, a.scope)
    run = load_for_write(a.folder)
    states = writer_states(run, top)

    def under(path):
        return not scope or any(path == sc or path.startswith(sc.rstrip("/") + "/") or sc == "." for sc in scope)

    paths = {p for p in states if under(p)} | set(snapshot_scope(top, scope))
    for path in paths:
        states[path] = hash_path(top, path)
    save_run(a.folder, run)
    append_progress(a.folder, "tree-note %d" % len(paths))
    emit({"noted": len(paths)})
    return 0


def cmd_gate(a):
    run = load_run(a.folder)
    rec = run.get("gates", {}).get(a.id)
    shown = sha256_bytes(read_input(a.shown))
    answer = rec.get("answer") if isinstance(rec, dict) and rec.get("shown") == shown else None
    emit({"answer": answer})
    return 0


def cmd_gate_record(a):
    check_name(a.id, "gate id")
    run = load_for_write(a.folder)
    shown_bytes = read_input(a.shown)
    gates = run.setdefault("gates", {})
    prior = gates.get(a.id)
    seq = prior.get("seq") if isinstance(prior, dict) and isinstance(prior.get("seq"), int) else None
    if seq is None:
        seq = 1 + max([g["seq"] for g in gates.values()
                       if isinstance(g, dict) and isinstance(g.get("seq"), int)] or [0])
    if a.keep_shown:
        folder = folder_path(a.folder)
        os.makedirs(os.path.join(folder, "gates"), mode=0o700, exist_ok=True)
        write_bytes_atomic(os.path.join(folder, "gates", a.id + ".md"), shown_bytes)
    gates[a.id] = {"shown": sha256_bytes(shown_bytes), "answer": a.answer, "at": now_iso(), "seq": seq,
                   "kept": bool(a.keep_shown)}
    save_run(a.folder, run)
    append_progress(a.folder, "gate %s answered" % a.id)
    emit({})
    return 0


def cmd_answers(a):
    run = load_run(a.folder)
    folder = folder_path(a.folder)
    rows = []
    for gid, rec in (run.get("gates") or {}).items():
        if not isinstance(rec, dict) or (a.match and a.match not in gid):
            continue
        shown = os.path.join(folder, "gates", gid + ".md")
        seq = rec.get("seq") if isinstance(rec.get("seq"), int) else 0
        rows.append((seq, rec.get("at") or "", gid,
                     {"id": gid, "answer": rec.get("answer"), "at": rec.get("at"),
                      "shown": shown if rec.get("kept") is True and os.path.isfile(shown) else None}))
    emit({"answers": [r[3] for r in sorted(rows, key=lambda r: r[:3])]})
    return 0


def cmd_put(a):
    rel = a.rel
    parts = rel.split("/")
    if (os.path.isabs(rel) or "\\" in rel or parts[0] != "scratch" or len(parts) < 2
            or any(p in ("", ".", "..") for p in parts)):
        raise CannotRun("put needs a file path under scratch/ with no '..': %r" % rel)
    load_for_write(a.folder)
    folder = folder_path(a.folder)
    data = read_input(a.from_)
    cur = folder
    for part in parts[:-1]:
        cur = os.path.join(cur, part)
        if os.path.islink(cur):
            raise CannotRun("put refuses a link on the way: " + rel)
        os.makedirs(cur, mode=0o700, exist_ok=True)
        os.chmod(cur, 0o700)
    target = os.path.join(folder, *parts)
    if os.path.islink(target) or os.path.isdir(target):
        raise CannotRun("put cannot replace " + rel)
    write_bytes_atomic(target, data)
    append_progress(folder, "put %s" % rel)
    emit({"path": target, "sha256": sha256_bytes(data)})
    return 0


def cmd_effect(a):
    check_name(a.id, "effect id")
    if a.action == "state":
        run = load_run(a.folder)
        rec = run.get("effects", {}).get(a.id)
        emit({"state": rec.get("state", "none") if isinstance(rec, dict) else "none"})
        return 0
    run = load_for_write(a.folder)
    state = "started" if a.action == "start" else "done"
    run.setdefault("effects", {})[a.id] = {"state": state, "at": now_iso()}
    save_run(a.folder, run)
    append_progress(a.folder, "effect %s %s" % (a.id, state))
    emit({"state": state})
    return 0


def name_map(pairs, what):
    out = {}
    for item in pairs or []:
        name, sep, value = item.partition("=")
        if not sep or not name or not value:
            raise CannotRun("%s needs <name>=<value>: %r" % (what, item))
        out[name] = value
    return out


def current_state(a):
    """(agent name -> sha of its file now, agent name -> model now) from --agent and --model."""
    shas = {n: sha256_bytes(read_input(f)) for n, f in name_map(a.agent, "--agent").items()}
    return shas, name_map(a.model, "--model")


def done_records(run):
    """Every recorded result, and every writer whose work is done, by id."""
    recs = dict(run.get("results") or {})
    for wid, rec in (run.get("writers") or {}).items():
        if isinstance(rec, dict) and rec.get("state") == "done":
            recs.setdefault(wid, rec)
    return recs


def cmd_stale(a):
    run = load_run(a.folder)
    shas, models = current_state(a)
    changed = []
    for rid, rec in sorted(done_records(run).items()):
        agent = rec.get("agent")
        agent_changed = agent in shas and shas[agent] != rec.get("agent_sha")
        new_model = models.get(agent, rec.get("model"))
        if agent_changed or new_model != rec.get("model"):
            changed.append({"id": rid, "agent": agent, "agent_changed": agent_changed,
                            "old_model": rec.get("model"), "new_model": new_model})
    emit({"total": len(changed), "changed": changed})
    return 0


def cmd_keep(a):
    run = load_for_write(a.folder)
    shas, models = current_state(a)
    results = done_records(run)
    for rid in a.ids:
        if rid not in results:
            raise CannotRun("no recorded result to keep: " + rid)
    kept = run.setdefault("kept", [])
    for rid in a.ids:
        rec = results[rid]
        rec["agent_sha"] = shas.get(rec.get("agent"), rec.get("agent_sha"))
        rec["model"] = models.get(rec.get("agent"), rec.get("model"))
        rec["fingerprint"] = make_fingerprint(rec["content"], rec["agent_sha"], rec["model"])
        if rid not in kept:
            kept.append(rid)
    save_run(a.folder, run)
    append_progress(a.folder, "keep %s" % " ".join(a.ids))
    emit({"kept": list(a.ids)})
    return 0


def cmd_kept(a):
    emit({"kept": list(load_run(a.folder).get("kept") or [])})
    return 0


def cmd_results(a):
    ids = sorted(i for i in (load_run(a.folder).get("results") or {}) if not a.match or a.match in i)
    emit({"count": len(ids), "ids": ids})
    return 0


COMMANDS = {"open": cmd_open, "resume": cmd_resume, "discard": cmd_discard, "close": cmd_close,
            "phase": cmd_phase, "log": cmd_log, "fact": cmd_fact, "dispatch": cmd_dispatch,
            "done": cmd_done, "gate": cmd_gate, "gate-record": cmd_gate_record, "answers": cmd_answers, "put": cmd_put, "writer": cmd_writer, "tree-note": cmd_tree_note, "effect": cmd_effect,
            "stale": cmd_stale, "keep": cmd_keep, "kept": cmd_kept, "results": cmd_results}


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

        def cli(args, home, session=None, xdg=None, cwd=None, stdin=None):
            r = subprocess.run([sys.executable, os.path.abspath(__file__), *args],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               stdin=subprocess.DEVNULL if stdin is None else None, input=stdin,
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
            expect(rc == 9 and out is None and err.strip() ==
                   "run-folder: run taken over: owned by session B, this is session A", (rc, out, err))
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

        # ---- Task 2 helpers

        def mkfile(content, label="f"):
            counter[0] += 1
            p = os.path.join(tmp0, "%s%d.txt" % (label, counter[0]))
            with open(p, "wb") as fh:
                fh.write(content if isinstance(content, bytes) else content.encode("utf-8"))
            return p

        def nr(home, session=None):
            _a, o, _e = op(home, repo(), session=session)
            return o["folder"]

        def run_json(folder):
            return json.loads(read(os.path.join(folder, "run.json")))

        def disp(home, folder, did, inp, area="main", agent="v", afile=None, model="m1", attach=(), session=None):
            a = ["dispatch", folder, did, "--area", area, "--agent", agent, "--agent-file", afile,
                 "--model", model, "--input", inp]
            for x in attach:
                a += ["--attach", x]
            return cli(a, home, session)

        def full(home, folder, did, inp, afile, agent="v", model="m1", text="result", session=None):
            rc, o, err = disp(home, folder, did, inp, agent=agent, afile=afile, model=model, session=session)
            expect(rc == 0 and o["action"] == "dispatch", (rc, o, err))
            os.makedirs(os.path.dirname(o["result"]), exist_ok=True)
            with open(o["result"], "w") as fh:
                fh.write(text)
            rc, d, err = cli(["done", folder, did], home, session)
            expect(rc == 0 and d == {"recorded": True}, (rc, d, err))
            return o

        def snapshot(folder):
            snap = {}
            for dp, _ds, fs in os.walk(folder):
                for f in fs:
                    if f == ".lock":
                        continue  # the empty flock file is not run state
                    with open(os.path.join(dp, f), "rb") as fh:
                        snap[os.path.relpath(os.path.join(dp, f), folder)] = fh.read()
            return snap

        @case("dispatch-new")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            rc, o, err = disp(home, f, "d1", inp, afile=af)
            expect(rc == 0 and o["action"] == "dispatch", (rc, o, err))
            expect(read(o["input"]) == "hello", o)
            expect(o["input"] == os.path.join(f, "main", "inputs", "d1.md"), o["input"])
            expect(os.path.dirname(o["result"]) == os.path.join(f, "main", "results")
                   and re.match(r"^d1\.[0-9a-f]{12}\.md$", os.path.basename(o["result"])), o["result"])
            expect(run_json(f)["dispatches"]["d1"]["result"] == "main/results/" + os.path.basename(o["result"]),
                   run_json(f)["dispatches"]["d1"])
            expect(re.match(r"^[0-9a-f]{64}$", o["fingerprint"]), o)

        @case("reuse-after-done")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            first = full(home, f, "d1", inp, af)
            rc, o, _e = disp(home, f, "d1", inp, afile=af)
            expect(o["action"] == "reuse" and o["result"] == first["result"], o)
            expect(o["fingerprint"] == first["fingerprint"], o)

        @case("result-unrecorded-not-reused")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            _rc, o, _e = disp(home, f, "d1", inp, afile=af)
            os.makedirs(os.path.dirname(o["result"]), exist_ok=True)
            with open(o["result"], "w") as fh:
                fh.write("half-writ")
            _rc, o2, _e = disp(home, f, "d1", inp, afile=af)
            expect(o2["action"] == "dispatch", o2)

        @case("done-missing-result")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            _rc, o, _e = disp(home, f, "d1", inp, afile=af)
            rc, out, _e = cli(["done", f, "d1"], home)
            expect(rc == 3 and out is None, (rc, out))
            os.makedirs(os.path.dirname(o["result"]), exist_ok=True)
            open(o["result"], "w").close()
            rc, out, _e = cli(["done", f, "d1"], home)
            expect(rc == 3 and out is None, (rc, out))
            _rc, o2, _e = disp(home, f, "d1", inp, afile=af)
            expect(o2["action"] == "dispatch", o2)

        @case("done-from-stdin")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            _rc, o, _e = disp(home, f, "d1", inp, afile=af)
            rc, out, err = cli(["done", f, "d1", "--from", "-"], home, stdin=b"result text")
            expect(rc == 0 and out == {"recorded": True}, (rc, out, err))
            expect(read(o["result"]) == "result text", read(o["result"]))
            _rc, o2, _e = disp(home, f, "d1", inp, afile=af)
            expect(o2["action"] == "reuse", o2)
            src = mkfile("from a file")
            _rc, o3, _e = disp(home, f, "d2", inp, afile=af)
            rc, out, _e = cli(["done", f, "d2", "--from", src], home)
            expect(rc == 0 and read(o3["result"]) == "from a file", (rc, out))

        @case("fingerprint-changes-with-input")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            full(home, f, "d1", inp, af)
            inp2 = mkfile("hellp")
            _rc, o, _e = disp(home, f, "d1", inp2, afile=af)
            expect(o["action"] == "dispatch", o)

        @case("fingerprint-attach")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            os.makedirs(os.path.join(f, "scratch"))
            diff = os.path.join(f, "scratch", "diff.txt")
            with open(diff, "w") as fh:
                fh.write("one")
            rc, o, err = disp(home, f, "d1", inp, afile=af, attach=["scratch/diff.txt"])
            expect(rc == 0, (rc, err))
            os.makedirs(os.path.dirname(o["result"]), exist_ok=True)
            with open(o["result"], "w") as fh:
                fh.write("r")
            cli(["done", f, "d1"], home)
            _rc, o2, _e = disp(home, f, "d1", inp, afile=af, attach=["scratch/diff.txt"])
            expect(o2["action"] == "reuse", o2)
            with open(diff, "w") as fh:
                fh.write("two")
            _rc, o3, _e = disp(home, f, "d1", inp, afile=af, attach=["scratch/diff.txt"])
            expect(o3["action"] == "dispatch", o3)
            for bad in ("../x", "/etc/passwd", "scratch/missing.txt"):
                rc, out, _e = disp(home, f, "d2", inp, afile=af, attach=[bad])
                expect(rc == 2 and out is None, (bad, rc))

        @case("fingerprint-agent-and-model")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            full(home, f, "d1", inp, af)
            _rc, o, _e = disp(home, f, "d1", inp, afile=mkfile("agent v2"))
            expect(o["action"] == "dispatch", o)
            full(home, f, "d2", inp, af)
            _rc, o, _e = disp(home, f, "d2", inp, afile=af, model="m2")
            expect(o["action"] == "dispatch", o)

        @case("area-blind-separate")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            rc, o, _e = disp(home, f, "d1", inp, area="blind", afile=af)
            expect(o["input"] == os.path.join(f, "blind", "inputs", "d1.md") and os.path.isfile(o["input"]), o)
            expect(os.path.dirname(o["result"]) == os.path.join(f, "blind", "results"), o)
            expect(not os.path.exists(os.path.join(f, "main")), "something under main/")

        @case("bad-id")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            before = snapshot(f)
            for bad in ("../x", "a/b", "", ".x", "A", "a\n"):
                rc, out, _e = disp(home, f, bad, inp, afile=af)
                expect(rc == 2 and out is None, (bad, rc))
                rc, out, _e = cli(["done", f, bad], home)
                expect(rc == 2 and out is None, (bad, rc))
            expect(snapshot(f) == before, "a bad id wrote something")

        @case("gate-roundtrip")
        def _():
            home = newdir("home")
            f = nr(home)
            shown, other = mkfile("question A"), mkfile("question B")
            rc, out, _e = cli(["gate", f, "g1", "--shown", shown], home)
            expect(rc == 0 and out == {"answer": None}, (rc, out))
            rc, out, _e = cli(["gate-record", f, "g1", "--shown", shown, "--answer", "Resume"], home)
            expect(rc == 0 and out == {}, (rc, out))
            rc, out, _e = cli(["gate", f, "g1", "--shown", shown], home)
            expect(out == {"answer": "Resume"}, out)
            rc, out, _e = cli(["gate", f, "g1", "--shown", other], home)
            expect(out == {"answer": None}, out)
            rc, out, _e = cli(["gate", f, "g1", "--shown", "-"], home, stdin=b"question A")
            expect(out == {"answer": "Resume"}, out)

        @case("effect-states")
        def _():
            home = newdir("home")
            f = nr(home)
            for sub, want in (("state", "none"), ("start", "started"), ("state", "started"),
                              ("done", "done"), ("state", "done")):
                rc, out, _e = cli(["effect", f, "e1", sub], home)
                expect(rc == 0 and out == {"state": want}, (sub, rc, out))
            rc, out, _e = cli(["effect", f, "e2", "state"], home)
            expect(out == {"state": "none"}, out)

        def stale_args(vfile, gfile, vmodel="m1", gmodel="m1"):
            return ["--agent", "v=" + vfile, "--agent", "g=" + gfile,
                    "--model", "v=" + vmodel, "--model", "g=" + gmodel]

        @case("stale-counts")
        def _():
            home = newdir("home")
            f, inp = nr(home), mkfile("hello")
            vf, gf = mkfile("agent v"), mkfile("agent g")
            for i in (1, 2, 3):
                full(home, f, "v%d" % i, inp, vf, agent="v")
            full(home, f, "g1", inp, gf, agent="g")
            rc, out, err = cli(["stale", f, *stale_args(vf, gf)], home)
            expect(rc == 0 and out == {"total": 0, "changed": []}, (rc, out, err))
            rc, out, _e = cli(["stale", f, *stale_args(vf, gf, gmodel="m2")], home)
            expect(out["total"] == 1 and out["changed"] == [
                {"id": "g1", "agent": "g", "agent_changed": False, "old_model": "m1", "new_model": "m2"}], out)
            with open(vf, "w") as fh:
                fh.write("agent v, edited")
            rc, out, _e = cli(["stale", f, *stale_args(vf, gf)], home)
            expect(out["total"] == 3 and all(c["agent"] == "v" and c["agent_changed"] is True
                                             for c in out["changed"]), out)
            expect(sorted(c["id"] for c in out["changed"]) == ["v1", "v2", "v3"], out)

        @case("results-match")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            for did in ("cg-backend.1", "cg-backend.2", "cg-frontend.1"):
                full(home, f, did, inp, af)
            disp(home, f, "cg-backend.3", inp, afile=af)
            rc, out, _e = cli(["results", f], home)
            expect(out == {"count": 3, "ids": ["cg-backend.1", "cg-backend.2", "cg-frontend.1"]}, out)
            rc, out, _e = cli(["results", f, "--match", "cg-backend"], home)
            expect(out == {"count": 2, "ids": ["cg-backend.1", "cg-backend.2"]}, out)
            expect(run_json(f)["results"].keys() == {"cg-backend.1", "cg-backend.2", "cg-frontend.1"}, "run.json results")

        @case("keep-then-reuse")
        def _():
            home = newdir("home")
            f, inp = nr(home), mkfile("hello")
            vf, gf = mkfile("agent v"), mkfile("agent g")
            full(home, f, "v1", inp, vf)
            full(home, f, "v2", inp, vf)
            with open(vf, "w") as fh:
                fh.write("agent v, edited")
            rc, out, _e = cli(["stale", f, *stale_args(vf, gf)], home)
            expect(out["total"] == 2, out)
            rc, out, err = cli(["keep", f, "--ids", "v1", *stale_args(vf, gf)], home)
            expect(rc == 0 and out == {"kept": ["v1"]}, (rc, out, err))
            _rc, o, _e = disp(home, f, "v1", inp, afile=vf)
            expect(o["action"] == "reuse", o)
            _rc, o, _e = disp(home, f, "v2", inp, afile=vf)
            expect(o["action"] == "dispatch", o)
            rc, out, _e = cli(["kept", f], home)
            expect(out == {"kept": ["v1"]}, out)
            rc, out, _e = cli(["stale", f, *stale_args(vf, gf)], home)
            expect([c["id"] for c in out["changed"]] == [], out)
            rc, out, _e = cli(["keep", f, "--ids", "nope", *stale_args(vf, gf)], home)
            expect(rc == 2, rc)

        @case("owner-guard-writes")
        def _():
            home = newdir("home")
            _a, o, _e = op(home, repo(), session="A")
            f, inp, af = o["folder"], mkfile("hello"), mkfile("agent v")
            _rc, d, _e = disp(home, f, "d1", inp, afile=af, session="A")
            os.makedirs(os.path.dirname(d["result"]), exist_ok=True)
            with open(d["result"], "w") as fh:
                fh.write("r")
            full(home, f, "d2", inp, af, session="A")
            rc, r, _e = cli(["resume", f], home, "B")
            expect(rc == 0, rc)
            before = snapshot(f)
            attempts = {
                "dispatch": disp(home, f, "d3", inp, afile=af, session="A"),
                "done": cli(["done", f, "d1"], home, "A"),
                "gate-record": cli(["gate-record", f, "g1", "--shown", inp, "--answer", "yes"], home, "A"),
                "effect": cli(["effect", f, "e1", "start"], home, "A"),
                "keep": cli(["keep", f, "--ids", "d2", "--agent", "v=" + af, "--model", "v=m1"], home, "A"),
            }
            for name, (rc, out, err) in attempts.items():
                expect(rc == 9 and out is None, (name, rc, out, err))
            expect(snapshot(f) == before, "a taken-over write landed")
            _rc, d, _e = cli(["done", f, "d1"], home, "B")
            expect(d == {"recorded": True}, d)

        @case("write-after-discard-exits-9")
        def _():
            home = newdir("home")
            f, inp, af = nr(home, "A"), mkfile("hello"), mkfile("agent v")
            expect(cli(["discard", f], home, "B")[0] == 0, "discard")
            calls = [["log", f, "x"], ["phase", f, "p1"], ["fact", f, "n", "--set", "v"],
                     ["dispatch", f, "d1", "--area", "main", "--agent", "v", "--agent-file", af,
                      "--model", "m", "--input", inp],
                     ["done", f, "d1"], ["gate-record", f, "g", "--shown", inp, "--answer", "a"],
                     ["effect", f, "e", "start"], ["keep", f, "--ids", "d1"], ["close", f]]
            for c in calls:
                rc, out, err = cli(c, home, "A")
                expect(rc == 9 and out is None and "run-folder:" in err, (c[0], rc, out, err))
            expect(not os.path.exists(f), "a write recreated the folder")
            rc, out, _e = cli(["resume", f], home, "A")
            expect(rc == 2, rc)

        @case("bad-command-or-key")
        def _():
            home, specs = newdir("home"), repo()
            for cmd, key in (("a/b", "K"), ("x y", "K"), (CMD, "../x"), (CMD, "a/b"), (CMD, "k k"),
                             (CMD, "ké"), ("a/..", "K"), (CMD, "k\n"), (CMD, "k\nx")):
                a = ["open", "--command", cmd, "--specs", specs, "--args", "a", "--key", key]
                rc, out, err = cli(a, home)
                expect(rc == 2 and out is None, (cmd, key, rc, out))
            expect(not os.path.exists(os.path.join(home, ".local")), "something was created")

        @case("args-flag-shaped")
        def _():
            home = newdir("home")
            for val in ("--no-design", "--force"):
                rc, o, err = cli(["open", "--command", CMD, "--specs", repo(), "--args", val,
                                  "--key", "K-1"], home)
                expect(rc == 0 and o["state"] == "new", (val, rc, o, err))
                expect(run_json(o["folder"])["args"] == val, run_json(o["folder"]))
            f = o["folder"]
            rc, out, err = cli(["log", f, "--x"], home)
            expect(rc == 0 and out == {}, (rc, out, err))
            expect(" --x\n" in read(os.path.join(f, "progress.md")), read(os.path.join(f, "progress.md")))
            rc, out, err = cli(["fact", f, "n", "--set", "--odd"], home)
            expect(rc == 0 and out["value"] == "--odd", (rc, out, err))

        @case("unparseable-run-json-noted")
        def _():
            home, specs = newdir("home"), repo()
            _a, o1, _e = op(home, specs)
            with open(os.path.join(o1["folder"], "run.json"), "w") as fh:
                fh.write("{ not json")
            rc, o2, err = op(home, specs)
            expect(rc == 0 and o2["state"] == "new" and o2["folder"] == o1["folder"], (rc, o2))
            expect("NOTE:" in err and "run.json" in err, err)
            expect(run_json(o2["folder"])["run_key"] == o2["run_key"], "run.json not replaced")

        @case("open-exclusive")
        def _():
            d = newdir("excl")
            path = os.path.join(d, "run.json")
            expect(create_json_exclusive(path, {"who": "first"}) is True, "first create")
            expect(create_json_exclusive(path, {"who": "second"}) is False, "second create won")
            expect(json.loads(read(path)) == {"who": "first"}, "existing run.json overwritten")
            expect(stat.S_IMODE(os.stat(path).st_mode) == 0o600, oct(os.stat(path).st_mode))
            expect(os.listdir(d) == ["run.json"], os.listdir(d))
            home, specs = newdir("home"), repo()
            procs = [subprocess.Popen([sys.executable, os.path.abspath(__file__), "open", "--command", CMD,
                                       "--specs", specs, "--args", "a", "--key", "K-1"],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_for(home, "S%d" % i))
                     for i in range(6)]
            states = []
            for p_ in procs:
                out, _err = p_.communicate()
                states.append(json.loads(out)["state"])
            expect(sorted(states) == ["new"] + ["unfinished"] * 5, states)

        @case("concurrent-writes")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            ids = ["c%d" % i for i in range(12)]

            def parallel(argvs):
                ps = [subprocess.Popen([sys.executable, os.path.abspath(__file__), *a],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_for(home))
                      for a in argvs]
                return [(p_.wait(), p_.stderr.read().decode()) for p_ in ps]

            outs = parallel([["dispatch", f, i, "--area", "main", "--agent", "v", "--agent-file", af,
                              "--model", "m1", "--input", inp] for i in ids])
            expect(all(rc == 0 for rc, _e in outs), outs)
            dispatches = run_json(f)["dispatches"]
            expect(sorted(dispatches) == sorted(ids), "a dispatch record was lost")
            for i in ids:
                with open(os.path.join(f, *dispatches[i]["result"].split("/")), "w") as fh:
                    fh.write("r")
            outs = parallel([["done", f, i] for i in ids] + [["phase", f, "p%d" % k] for k in range(4)]
                            + [["fact", f, "n%d" % k, "--set", "v"] for k in range(4)])
            expect(all(rc == 0 for rc, _e in outs), outs)
            run = run_json(f)
            expect(sorted(run["results"]) == sorted(ids), sorted(run["results"]))
            expect(sorted(run["facts"]) == ["n0", "n1", "n2", "n3"], run["facts"])
            expect(".lock" not in run["results"] and ".lock" not in run["dispatches"], "lock counted")

        @case("result-nonce-old-agent")
        def _():
            # A superseded session's agent, still running, writes the result path its own dispatch named;
            # the new owner's dispatch of the same id names another path, so that write is never recorded.
            home = newdir("home")
            f, af = nr(home), mkfile("agent v")
            before, after = mkfile("repository before the pull"), mkfile("repository after the pull")
            _rc, o1, _e = disp(home, f, "d1", before, afile=af)
            _rc, o2, _e = disp(home, f, "d1", after, afile=af)
            expect(o2["action"] == "dispatch" and o2["result"] != o1["result"], (o1["result"], o2["result"]))
            expect(re.match(r"^d1\.[0-9a-f]{12}\.md$", os.path.basename(o2["result"])), o2["result"])
            os.makedirs(os.path.dirname(o1["result"]), exist_ok=True)
            with open(o1["result"], "w") as fh:
                fh.write("stale")
            rc, out, _e = cli(["done", f, "d1"], home)
            expect(rc == 3 and out is None, ("the old agent's file was recorded", rc, out))
            with open(o2["result"], "w") as fh:
                fh.write("fresh")
            with open(o1["result"], "w") as fh:
                fh.write("stale, written after the new agent")
            rc, out, _e = cli(["done", f, "d1"], home)
            expect(rc == 0 and out == {"recorded": True}, (rc, out))
            _rc, o3, _e = disp(home, f, "d1", after, afile=af)
            expect(o3["action"] == "reuse" and o3["result"] == o2["result"] and read(o3["result"]) == "fresh", o3)
            _rc, o4, _e = disp(home, f, "d1", before, afile=af)
            expect(o4["action"] == "dispatch" and not os.path.exists(o2["result"]),
                   "a re-dispatch left the result it replaced")

        @case("discard-waits-for-writer")
        def _():
            home = newdir("home")
            f = nr(home)
            fd = os.open(os.path.join(f, ".lock"), os.O_WRONLY | os.O_CREAT, 0o600)
            p_ = None
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)  # a writer in flight: it loaded run.json and has yet to save it
                p_ = subprocess.Popen([sys.executable, os.path.abspath(__file__), "discard", f],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env_for(home))
                deadline = time.monotonic() + 1.5
                while time.monotonic() < deadline and p_.poll() is None:
                    time.sleep(0.05)
                waited = p_.poll() is None and os.path.isfile(os.path.join(f, "run.json"))
            finally:
                os.close(fd)
                if p_ is not None:
                    out, err = p_.communicate(timeout=60)
            expect(waited, "discard removed the folder while a writer held the lock")
            expect(p_.returncode == 0 and json.loads(out) == {"removed": True} and not os.path.exists(f),
                   (p_.returncode, out, err))

        @case("close-unlocks-before-removing")
        def _():
            # On an NFS home a file still open in a directory is renamed rather than removed, so the
            # directory cannot be: close must not hold its .lock open while the folder is removed.
            home = newdir("home")
            f = nr(home)
            seen, real_rmtree, saved_env, out = [], shutil.rmtree, dict(os.environ), io.StringIO()

            def probe(path, *pa, **kw):
                held = None
                lock_file = os.path.join(path, ".lock")
                if os.path.exists(lock_file):
                    pfd = os.open(lock_file, os.O_RDONLY)
                    try:
                        fcntl.flock(pfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        held = False
                    except OSError:
                        held = True
                    finally:
                        os.close(pfd)
                seen.append((path, held, os.path.exists(f)))
                return real_rmtree(path, *pa, **kw)

            try:
                os.environ.clear()
                os.environ.update(env_for(home))
                shutil.rmtree = probe
                with contextlib.redirect_stdout(out):
                    rc = main(["close", f])
            finally:
                shutil.rmtree = real_rmtree
                os.environ.clear()
                os.environ.update(saved_env)
            expect(rc == 0 and json.loads(out.getvalue()) == {"removed": True}, (rc, out.getvalue()))
            expect(len(seen) == 1 and seen[0][1] is False, ("the lock was held during the removal", seen))
            expect(seen[0][0] != f and not seen[0][2], ("not moved off the run's path first", seen))
            expect(not os.path.exists(f) and not os.path.exists(seen[0][0]), "something was left")

        def call_patched(home, argv, patch, unpatch):
            saved_env, out, err = dict(os.environ), io.StringIO(), io.StringIO()
            try:
                os.environ.clear()
                os.environ.update(env_for(home))
                patch()
                with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    rc = main(argv)
            finally:
                unpatch()
                os.environ.clear()
                os.environ.update(saved_env)
            return rc, err.getvalue()

        def run_state(folder):
            return {n: read(os.path.join(folder, n)) for n in ("run.json", "progress.md")
                    if os.path.exists(os.path.join(folder, n))}

        def failing_flock():
            real = fcntl.flock

            def bad(fd, op):
                raise OSError(37, "No locks available")  # ENOLCK: an NFS home with no lock manager

            def patch():
                fcntl.flock = bad

            def unpatch():
                fcntl.flock = real
            return patch, unpatch

        @case("lock-failure-exits-2")
        def _():
            # A lock that cannot be taken must not let the write through unlocked.
            home = newdir("home")
            f = nr(home)
            before = run_state(f)
            patch, unpatch = failing_flock()
            rc, err = call_patched(home, ["log", f, "x"], patch, unpatch)
            expect(rc == 2 and "could not lock" in err, (rc, err))
            expect(run_state(f) == before, "a write went through without the lock")

        @case("lock-failure-keeps-folder")
        def _():
            # Start over must not remove a folder another writer may hold, when it cannot lock it.
            home = newdir("home")
            f = nr(home)
            patch, unpatch = failing_flock()
            rc, err = call_patched(home, ["discard", f], patch, unpatch)
            expect(rc == 2 and "could not lock" in err, (rc, err))
            expect(os.path.exists(os.path.join(f, "run.json")), "the folder was removed without the lock")

        @case("lock-retry-bounded")
        def _():
            # A lock file that never matches the one held (its inode keeps changing) must fail, not spin.
            home = newdir("home")
            f = nr(home)
            before = run_state(f)
            real_stat, calls = os.stat, [0]

            def moving(p, *pa, **kw):
                r = real_stat(p, *pa, **kw)
                if os.fspath(p).endswith(os.sep + ".lock"):
                    calls[0] += 1
                    if calls[0] > 50:
                        raise RuntimeError("the retry loop did not stop")
                    t = list(r[:10])
                    t[1] = r.st_ino + 1
                    return os.stat_result(t)
                return r

            def patch():
                os.stat = moving

            def unpatch():
                os.stat = real_stat
            rc, err = call_patched(home, ["log", f, "x"], patch, unpatch)
            expect(rc == 2 and "kept changing" in err, (rc, err, calls[0]))
            expect(run_state(f) == before, "a write went through without the lock")

        @case("resume-args")
        def _():
            home, specs = newdir("home"), repo()
            _a, o1, _e = op(home, specs, session="A", args="--repos a")
            folder = o1["folder"]
            rc, r, err = cli(["resume", folder, "--args", "--repos a --rebaseline"], home, "B")
            expect(rc == 0 and r == {"owner": "B"}, (rc, r, err))
            expect(run_json(folder)["args"] == "--repos a --rebaseline", run_json(folder))
            _a, o3, _e = op(home, specs, session="C", args="--repos a")
            expect(o3["summary"]["args"] == "--repos a --rebaseline", o3["summary"])
            rc, r, _e = cli(["resume", folder], home, "C")
            expect(rc == 0 and run_json(folder)["args"] == "--repos a --rebaseline", "resume with no --args changed them")
            rc, r, err = cli(["resume", folder, "--args", "--no-design"], home, "C")
            expect(rc == 0 and run_json(folder)["args"] == "--no-design", (rc, err, run_json(folder)))

        # ---- Part 2a: put, answers, pins, redo, keyless others

        @case("put-atomic-owner-checked")
        def _():
            home = newdir("home")
            f = nr(home, "A")
            rc, o, err = cli(["put", f, "scratch/brief.md", "--from", "-"], home, "A", stdin=b"first")
            expect(rc == 0 and o["path"] == os.path.join(f, "scratch", "brief.md"), (rc, o, err))
            expect(o["sha256"] == hashlib.sha256(b"first").hexdigest() and read(o["path"]) == "first", o)
            expect(stat.S_IMODE(os.stat(os.path.join(f, "scratch")).st_mode) == 0o700, "scratch not 0700")
            rc, o, _e = cli(["put", f, "scratch/sub/deep.md", "--from", "-"], home, "A", stdin=b"x")
            expect(rc == 0 and stat.S_IMODE(os.stat(os.path.join(f, "scratch", "sub")).st_mode) == 0o700, (rc, o))
            rc, o, _e = cli(["put", f, "scratch/brief.md", "--from", "-"], home, "A", stdin=b"second")
            expect(rc == 0 and read(o["path"]) == "second", (rc, o))
            rc, o, _e = cli(["put", f, "scratch/brief.md", "--from", "-"], home, "B", stdin=b"stolen")
            expect(rc == 9 and o is None and read(os.path.join(f, "scratch", "brief.md")) == "second", (rc, o))
            before = snapshot(f)
            for bad in ("inputs/x", "../x", "/abs", "scratch/../x", "scratch", "scratch/"):
                rc, o, _e = cli(["put", f, bad, "--from", "-"], home, "A", stdin=b"x")
                expect(rc == 2 and o is None, (bad, rc))
            expect(snapshot(f) == before, "a refused put wrote something")

        @case("answers-in-first-order")
        def _():
            home = newdir("home")
            f = nr(home)
            shown = [mkfile("shown %d" % i) for i in range(3)]
            cli(["gate-record", f, "g-002", "--shown", shown[0], "--answer", "one"], home)
            cli(["gate-record", f, "g-001", "--shown", shown[1], "--answer", "two", "--keep-shown"], home)
            cli(["gate-record", f, "g-002", "--shown", shown[2], "--answer", "three"], home)
            rc, o, err = cli(["answers", f], home)
            expect(rc == 0 and [x["id"] for x in o["answers"]] == ["g-002", "g-001"], (rc, o, err))
            by = {x["id"]: x for x in o["answers"]}
            expect(by["g-002"]["answer"] == "three" and by["g-001"]["answer"] == "two", o)
            expect(by["g-002"]["shown"] is None and by["g-001"]["shown"] == os.path.join(f, "gates", "g-001.md"), o)
            expect(read(by["g-001"]["shown"]) == "shown 1" and re.match(r"^\d{4}-", by["g-001"]["at"]), o)
            rc, o, _e = cli(["answers", f, "--match", "g-00"], home)
            expect(len(o["answers"]) == 2, o)
            rc, o, _e = cli(["answers", f, "--match", "g-001"], home)
            expect([x["id"] for x in o["answers"]] == ["g-001"], o)
            rc, o, _e = cli(["answers", f, "--match", "zzz"], home)
            expect(o == {"answers": []}, o)
            owned = nr(home, "A")
            rc, _o, _e = cli(["gate-record", owned, "g-010", "--shown", shown[0], "--answer", "x", "--keep-shown"],
                             home, "B")
            expect(rc == 9 and not os.path.exists(os.path.join(owned, "gates")), rc)

        @case("pin-recorded-and-returned")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            _rc, o, _e = disp(home, f, "d1", inp, afile=af)
            os.makedirs(os.path.dirname(o["result"]), exist_ok=True)
            with open(o["result"], "w") as fh:
                fh.write("r")
            rc, out, err = cli(["done", f, "d1", "--pin", "commit=abc", "--pin", "ref=origin/main"], home)
            expect(rc == 0 and out == {"recorded": True}, (rc, out, err))
            _rc, o2, _e = disp(home, f, "d1", inp, afile=af)
            expect(o2["action"] == "reuse" and o2["pins"] == {"commit": "abc", "ref": "origin/main"}, o2)
            full(home, f, "d2", inp, af)
            _rc, o3, _e = disp(home, f, "d2", inp, afile=af)
            expect(o3["action"] == "reuse" and o3["pins"] == {}, o3)
            rc, out, _e = cli(["done", f, "d1", "--pin", "novalue"], home)
            expect(rc == 2, rc)

        @case("redo-forces-dispatch")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("hello"), mkfile("agent v")
            o1 = full(home, f, "d1", inp, af)
            rc, o2, err = cli(["dispatch", f, "d1", "--area", "main", "--agent", "v", "--agent-file", af,
                               "--model", "m1", "--input", inp, "--redo"], home)
            expect(rc == 0 and o2["action"] == "dispatch" and o2["result"] != o1["result"], (rc, o2, err))
            expect(not os.path.exists(o1["result"]), "the old result file remains")
            rc, r, _e = cli(["results", f], home)
            expect(r["ids"] == [], r)
            _rc, o3, _e = disp(home, f, "d1", inp, afile=af)
            expect(o3["action"] == "dispatch", o3)

        @case("open-others-same-args-other-specs")
        def _():
            home, wd = newdir("home"), repo()
            _a, o1, _e = op(home, repo("https://example.com/a.git"), key=None, args="CVE-1  x", extra=["--workdir", wd])
            _a, o2, _e = op(home, repo("https://example.com/b.git"), key=None, args="CVE-1 x", extra=["--workdir", wd])
            expect(o2["folder"] != o1["folder"] and o2["others"] == [], o2["others"])
            _a, o3, _e = op(home, repo("https://example.com/b.git"), key=None, args="CVE-2", extra=["--workdir", wd])
            expect(len(o3["others"]) == 2, o3["others"])

        @case("open-others-corrupt-neighbour")
        def _():
            home, specs, wd = newdir("home"), repo("https://example.com/s.git"), repo()
            _a, o1, _e = op(home, specs, key=None, args="A", extra=["--workdir", wd])
            _a, o2, _e = op(home, specs, key=None, args="B", extra=["--workdir", wd])
            for folder, mut in ((o1["folder"], lambda r: r.update(updated=5)),):
                r = run_json(folder)
                mut(r)
                with open(os.path.join(folder, "run.json"), "w") as fh:
                    json.dump(r, fh)
            bad = os.path.join(os.path.dirname(o1["folder"]), "garbage")
            os.makedirs(bad)
            with open(os.path.join(bad, "run.json"), "w") as fh:
                fh.write("{not json")
            deep = os.path.join(os.path.dirname(o1["folder"]), "deep")
            os.makedirs(deep)
            with open(os.path.join(deep, "run.json"), "w") as fh:
                fh.write("[" * 100000)
            rc, o3, err = op(home, specs, key=None, args="C", extra=["--workdir", wd])
            expect(rc == 0 and o3["state"] == "new"
                   and [x["args"] for x in o3["others"]] == ["B"], (rc, o3, err))
            expect(all(isinstance(x["updated"], str) for x in o3["others"]), o3["others"])

        @case("open-keyless-others")
        def _():
            home, specs, wd = newdir("home"), repo("https://example.com/s.git"), repo()
            _a, o1, _e = op(home, specs, key=None, args="CVE-1", extra=["--workdir", wd], session="A")
            expect(o1["state"] == "new" and o1["others"] == [], o1)
            _a, o2, _e = op(home, specs, key=None, args="CVE-2", extra=["--workdir", wd], session="B")
            expect(o2["state"] == "new" and o2["folder"] != o1["folder"], o2)
            expect(len(o2["others"]) == 1, o2["others"])
            oth = o2["others"][0]
            expect(oth["folder"] == o1["folder"] and oth["args"] == "CVE-1" and oth["owner"] == "A", oth)
            for k in ("started", "updated", "last_phase", "results"):
                expect(k in oth, (k, oth))
            _a, o2b, _e = op(home, specs, key=None, args="CVE-2", extra=["--workdir", wd], session="B")
            expect(o2b["state"] == "unfinished" and [x["args"] for x in o2b["others"]] == ["CVE-1"], o2b)
            _a, k, _e = op(home, specs, key="K-1", args="CVE-3", extra=["--workdir", wd])
            expect(k["others"] == [], k)
            _a, nw, _e = op(home, specs, key=None, args="CVE-9", extra=[])
            expect(nw["others"] == [], nw)
            _a, other_wd, _e = op(home, specs, key=None, args="CVE-4", extra=["--workdir", repo()])
            expect(other_wd["others"] == [], other_wd)
            cli(["close", o1["folder"]], home, "A")
            _a, o4, _e = op(home, specs, key=None, args="CVE-2", extra=["--workdir", wd], session="B")
            expect([x["args"] for x in o4["others"]] == [], o4)
            for i in range(4):
                op(home, specs, key=None, args="X-%d" % i, extra=["--workdir", wd])
            _a, o5, _e = op(home, specs, key=None, args="Y", extra=["--workdir", wd])
            expect(len(o5["others"]) == 3, len(o5["others"]))
            ups = [x["updated"] for x in o5["others"]]
            expect(ups == sorted(ups, reverse=True), ups)


        # ---- Task 2 (Part 2a): writers

        def gitrepo():
            p = newdir("tree")
            git(p, "init", "-q")
            for name, body in (("f", "one\n"), ("g", "two\n")):
                with open(os.path.join(p, name), "w") as fh:
                    fh.write(body)
            git(p, "add", "-A")
            git(p, "commit", "-q", "-m", "init")
            return p

        def edit(tree, name, body):
            with open(os.path.join(tree, name), "w") as fh:
                fh.write(body)

        def wr(home, folder, wid, tree, afile, inp, scope=(), model="m1", session=None, redo=False):
            a = ["writer", folder, wid, "--tree", tree, "--agent", "w", "--agent-file", afile,
                 "--model", model, "--input", inp]
            for sc in scope:
                a += ["--scope", sc]
            if redo:
                a.append("--redo")
            return cli(a, home, session)

        def wdone(home, folder, wid, tree, afile, inp, receipt="receipt", edits=(), session=None, scope=()):
            rc, o, err = wr(home, folder, wid, tree, afile, inp, scope=scope, session=session)
            expect(rc == 0 and o["action"] == "dispatch", (rc, o, err))
            for name, body in edits:
                edit(tree, name, body)
            rc, d, err = cli(["done", folder, wid, "--from", "-"], home, session, stdin=receipt.encode())
            expect(rc == 0 and d == {"recorded": True}, (rc, d, err))
            return o

        @case("writer-dispatch-then-intact")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            o = wdone(home, f, "w1", tree, af, inp, receipt="did it", edits=(("f", "two\n"),))
            expect(re.match(r"^w1\.[0-9a-f]{12}\.md$", os.path.basename(o["receipt"]))
                   and os.path.dirname(o["receipt"]) == os.path.join(f, "main", "results"), o)
            rec = run_json(f)["writers"]["w1"]
            expect(rec["state"] == "done" and rec["wrote"] == {"f": sha256_bytes(b"two\n")}
                   and rec["tree"] == tree and "content" in rec, rec)
            expect(run_json(f)["trees"][tree] == {"f": sha256_bytes(b"two\n")}, run_json(f).get("trees"))
            expect("w1" not in run_json(f).get("dispatches", {}), "writer kept apart from dispatches")
            rc, o2, err = wr(home, f, "w1", tree, af, inp)
            expect(rc == 0 and o2 == {"action": "intact", "receipt": o["receipt"]}, (rc, o2, err))
            expect(read(o2["receipt"]) == "did it", o2)
            rc, o3, _e = wr(home, f, "w1", tree, af, inp, model="m2")
            expect(o3["action"] == "dispatch" and o3["receipt"] != o["receipt"], o3)
            expect(not os.path.exists(o["receipt"]), "old receipt kept")

        @case("writer-outside-change")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            o = wdone(home, f, "w1", tree, af, inp, edits=(("f", "two\n"),))
            edit(tree, "f", "three\n")
            rc, o2, err = wr(home, f, "w1", tree, af, inp)
            expect(rc == 0 and o2["action"] == "changed" and o2["receipt"] == o["receipt"], (rc, o2, err))
            expect(o2["changed"] == [{"path": "f", "expected": sha256_bytes(b"two\n"),
                                      "now": sha256_bytes(b"three\n")}], o2)

        @case("writer-later-own-write-intact")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            wdone(home, f, "wa", tree, af, inp, edits=(("f", "A\n"),))
            inp2 = mkfile("brief two")
            wdone(home, f, "wb", tree, af, inp2, edits=(("f", "B\n"),))
            rc, o, err = wr(home, f, "wa", tree, af, inp)
            expect(rc == 0 and o["action"] == "intact", (rc, o, err))
            edit(tree, "f", "C\n")
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "changed", o)

        @case("tree-note-commit-intact")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            wdone(home, f, "wa", tree, af, inp, edits=(("f", "A\n"),))
            # the command itself edits and commits, then notes the tree
            edit(tree, "f", "fixed\n")
            git(tree, "commit", "-q", "-am", "fix")
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "changed", ("no tree-note", o))
            rc, n, err = cli(["tree-note", f, "--tree", tree], home)
            expect(rc == 0 and n == {"noted": 1}, (rc, n, err))
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "intact", o)
            edit(tree, "f", "later\n")
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "changed", o)
            rc, n, _e = cli(["tree-note", f, "--tree", tree, "--scope", "g"], home)
            expect(n == {"noted": 0}, n)
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "changed", ("scope g does not cover f", o))

        @case("writer-interrupted")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            edit(tree, "g", "dirty before\n")
            rc, o, err = wr(home, f, "w1", tree, af, inp)
            expect(o["action"] == "dispatch", (rc, o, err))
            expect(run_json(f)["writers"]["w1"]["before"] == {"g": sha256_bytes(b"dirty before\n")}, run_json(f))
            edit(tree, "f", "half\n")
            rc, o2, err = wr(home, f, "w1", tree, af, inp)
            expect(rc == 0 and o2["action"] == "interrupted" and o2["receipt"] == o["receipt"], (rc, o2, err))
            expect(o2["left"] == [{"path": "f", "before": "clean", "now": sha256_bytes(b"half\n")}], o2)
            expect(run_json(f)["writers"]["w1"]["state"] == "started", "interrupted must write nothing")
            before = read(os.path.join(f, "run.json"))
            wr(home, f, "w1", tree, af, inp)
            expect(read(os.path.join(f, "run.json")) == before, "a read rewrote run.json")

        @case("writer-deleted-path")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            rc, o, _e = wr(home, f, "w1", tree, af, inp)
            os.unlink(os.path.join(tree, "g"))
            cli(["done", f, "w1", "--from", "-"], home, stdin=b"r")
            expect(run_json(f)["writers"]["w1"]["wrote"] == {"g": "-"}, run_json(f)["writers"]["w1"])
            rc, o, _e = wr(home, f, "w1", tree, af, inp)
            expect(o["action"] == "intact", o)
            edit(tree, "g", "two\n")
            rc, o, _e = wr(home, f, "w1", tree, af, inp)
            expect(o["action"] == "changed" and o["changed"][0]["expected"] == "-"
                   and o["changed"][0]["now"] == sha256_bytes(b"two\n"), o)

        @case("writer-not-a-git-tree")
        def _():
            home = newdir("home")
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            plain = newdir("plain")
            rc, o, err = wr(home, f, "w1", plain, af, inp)
            expect(rc == 2 and "writers" not in run_json(f), (rc, o, err))
            rc, o, err = cli(["tree-note", f, "--tree", plain], home)
            expect(rc == 2, (rc, err))

        @case("writer-owner-guard")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home, session="A"), mkfile("brief"), mkfile("agent")
            before = read(os.path.join(f, "run.json"))
            rc, o, err = wr(home, f, "w1", tree, af, inp, session="B")
            expect(rc == 9, (rc, o, err))
            expect(read(os.path.join(f, "run.json")) == before, "a taken-over writer wrote")
            rc, o, err = cli(["tree-note", f, "--tree", tree], home, "B")
            expect(rc == 9, (rc, err))

        @case("writer-rename-and-stale")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            rc, o, _e = wr(home, f, "w1", tree, af, inp)
            git(tree, "mv", "f", "h")
            cli(["done", f, "w1", "--from", "-"], home, stdin=b"r")
            expect(sorted(run_json(f)["writers"]["w1"]["wrote"]) == ["f", "h"], run_json(f)["writers"]["w1"])
            af2 = mkfile("agent changed")
            rc, s, _e = cli(["stale", f, "--agent", "w=" + af2], home)
            expect(s["total"] == 1 and s["changed"][0]["id"] == "w1", s)
            rc, k, err = cli(["keep", f, "--ids", "w1", "--agent", "w=" + af2], home)
            expect(rc == 0, (rc, err))
            rc, o, _e = wr(home, f, "w1", tree, af2, inp)
            expect(o["action"] == "intact", o)
            rc, s, _e = cli(["stale", f, "--agent", "w=" + af2], home)
            expect(s["total"] == 0, s)

        @case("writer-subdir-tree-shares-state")
        def _():
            home, tree = newdir("home"), gitrepo()
            os.makedirs(os.path.join(tree, "sub"))
            edit(tree, "sub/x", "0\n")
            git(tree, "add", "-A")
            git(tree, "commit", "-q", "-m", "sub")
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            wdone(home, f, "wa", tree, af, inp, edits=(("sub/x", "A\n"),))
            sub = os.path.join(tree, "sub")
            wdone(home, f, "wb", sub, af, mkfile("brief two"), edits=(("x", "B\n"),))
            expect(list(run_json(f)["trees"]) == [tree], run_json(f)["trees"])
            rc, o, err = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "intact", (rc, o, err))
            edit(tree, "sub/x", "C\n")
            git(tree, "commit", "-q", "-am", "c")
            rc, n, err = cli(["tree-note", f, "--tree", sub], home)
            expect(rc == 0 and n == {"noted": 1}, (rc, n, err))
            rc, o, _e = wr(home, f, "wa", tree, af, inp)
            expect(o["action"] == "intact", o)

        @case("writer-scope-order-insensitive")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            wdone(home, f, "w1", tree, af, inp, scope=("f", "g"), edits=(("f", "z\n"),))
            rc, o, err = wr(home, f, "w1", tree, af, inp, scope=("g", "f", "f"))
            expect(o["action"] == "intact", (rc, o, err))

        @case("writer-and-dispatch-id-clash")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            disp(home, f, "x1", inp, afile=af)
            wr(home, f, "x1", tree, af, inp)
            rc, d, err = cli(["done", f, "x1", "--from", "-"], home, stdin=b"r")
            expect(rc == 2, (rc, err))

        @case("writer-redo")
        def _():
            home, tree = newdir("home"), gitrepo()
            f, inp, af = nr(home), mkfile("brief"), mkfile("agent")
            # changed -> --redo dispatches anew from the tree as it stands; its done is intact again
            o = wdone(home, f, "w1", tree, af, inp, edits=(("f", "two\n"),))
            edit(tree, "f", "three\n")
            rc, o2, _e = wr(home, f, "w1", tree, af, inp)
            expect(o2["action"] == "changed", o2)
            rc, o3, err = wr(home, f, "w1", tree, af, inp, redo=True)
            expect(rc == 0 and o3["action"] == "dispatch" and o3["receipt"] != o["receipt"], (rc, o3, err))
            expect(not os.path.exists(o["receipt"]), "old receipt kept")
            rec = run_json(f)["writers"]["w1"]
            expect(rec["state"] == "started" and rec["before"] == {"f": sha256_bytes(b"three\n")}, rec)
            edit(tree, "f", "four\n")
            rc, d, err = cli(["done", f, "w1", "--from", "-"], home, stdin=b"again")
            expect(rc == 0 and d == {"recorded": True}, (rc, d, err))
            rc, o4, err = wr(home, f, "w1", tree, af, inp)
            expect(rc == 0 and o4 == {"action": "intact", "receipt": o3["receipt"]}, (rc, o4, err))
            expect(read(o4["receipt"]) == "again", o4)
            # interrupted -> --redo dispatches anew over what it left
            inp2 = mkfile("brief two")
            rc, o5, _e = wr(home, f, "w2", tree, af, inp2)
            edit(tree, "g", "half\n")
            with open(o5["receipt"], "w") as fh:
                fh.write("partial")
            rc, o6, _e = wr(home, f, "w2", tree, af, inp2)
            expect(o6["action"] == "interrupted", o6)
            rc, o7, err = wr(home, f, "w2", tree, af, inp2, redo=True)
            expect(rc == 0 and o7["action"] == "dispatch" and o7["receipt"] != o5["receipt"], (rc, o7, err))
            expect(not os.path.exists(o5["receipt"]), "interrupted receipt kept")
            expect(run_json(f)["writers"]["w2"]["before"]["g"] == sha256_bytes(b"half\n"), run_json(f)["writers"]["w2"])
            # owner-checked, like the dispatch branch
            fa = nr(home, session="A")
            wdone(home, fa, "w3", tree, af, inp, session="A")
            before = read(os.path.join(fa, "run.json"))
            rc, o8, err = wr(home, fa, "w3", tree, af, inp, session="B", redo=True)
            expect(rc == 9 and read(os.path.join(fa, "run.json")) == before, (rc, o8, err))

    for line in results:
        print(line)
    return 1 if failures else 0


FREE_TEXT_OPTIONS = ("--args", "--set", "--answer")
KNOWN_OPTIONS = FREE_TEXT_OPTIONS + (
    "--command", "--key", "--specs", "--workdir", "--shown", "--from", "--area", "--agent", "--agent-file",
    "--model", "--input", "--attach", "--ids", "--match", "--pin", "--tree", "--scope", "-h", "--help")


def normalize_argv(argv):
    """Let a free-text value be one flag-shaped token (--args "--no-design", log <folder> "--x"), which argparse
    would take for an option: join it to its option as --opt=value, and put -- before a log text."""
    out = list(argv)
    if out[:1] == ["log"] and len(out) == 3 and out[2].startswith("-") and out[2] != "-h":
        out.insert(2, "--")
        return out
    res, i = [], 0
    while i < len(out):
        tok = out[i]
        if tok in FREE_TEXT_OPTIONS and i + 1 < len(out) and out[i + 1].startswith("-") \
                and out[i + 1] not in KNOWN_OPTIONS:
            res.append("%s=%s" % (tok, out[i + 1]))
            i += 2
            continue
        res.append(tok)
        i += 1
    return res


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
        rs = sub.add_parser(name)
        rs.add_argument("folder")
        if name == "resume":
            rs.add_argument("--args")
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
    d = sub.add_parser("dispatch")
    d.add_argument("folder")
    d.add_argument("id")
    d.add_argument("--area", required=True, choices=AREAS)
    d.add_argument("--agent", required=True)
    d.add_argument("--agent-file", required=True)
    d.add_argument("--model", required=True)
    d.add_argument("--input", required=True)
    d.add_argument("--attach", action="append")
    d.add_argument("--redo", action="store_true")
    dn = sub.add_parser("done")
    dn.add_argument("folder")
    dn.add_argument("id")
    dn.add_argument("--from", dest="from_")
    dn.add_argument("--pin", action="append")
    for name in ("gate", "gate-record"):
        g = sub.add_parser(name)
        g.add_argument("folder")
        g.add_argument("id")
        g.add_argument("--shown", required=True)
        if name == "gate-record":
            g.add_argument("--answer", required=True)
            g.add_argument("--keep-shown", action="store_true")
    an = sub.add_parser("answers")
    an.add_argument("folder")
    an.add_argument("--match")
    pt = sub.add_parser("put")
    pt.add_argument("folder")
    pt.add_argument("rel")
    pt.add_argument("--from", dest="from_", required=True)
    for name in ("writer", "tree-note"):
        w = sub.add_parser(name)
        w.add_argument("folder")
        if name == "writer":
            w.add_argument("id")
        w.add_argument("--tree", required=True)
        w.add_argument("--scope", action="append")
        if name == "writer":
            w.add_argument("--agent", required=True)
            w.add_argument("--agent-file", required=True)
            w.add_argument("--model", required=True)
            w.add_argument("--input", required=True)
            w.add_argument("--attach", action="append")
            w.add_argument("--redo", action="store_true")
    e = sub.add_parser("effect")
    e.add_argument("folder")
    e.add_argument("id")
    e.add_argument("action", choices=("start", "done", "state"))
    for name in ("stale", "keep"):
        k = sub.add_parser(name)
        k.add_argument("folder")
        k.add_argument("--agent", action="append")
        k.add_argument("--model", action="append")
        if name == "keep":
            k.add_argument("--ids", nargs="+", required=True)
    sub.add_parser("kept").add_argument("folder")
    r = sub.add_parser("results")
    r.add_argument("folder")
    r.add_argument("--match")
    args = ap.parse_args(normalize_argv(argv))
    try:
        if needs_lock(args):
            with write_lock(args.folder) as lock:
                args.lock = lock
                return COMMANDS[args.cmd](args)
        return COMMANDS[args.cmd](args)
    except TakenOver as e:
        print("run-folder: " + str(e), file=sys.stderr)
        return 9
    except MissingResult as e:
        print("run-folder: " + str(e), file=sys.stderr)
        return 3
    except CannotRun as e:
        print("run-folder: " + str(e), file=sys.stderr)
        return 2
    except Exception as e:
        print("run-folder: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

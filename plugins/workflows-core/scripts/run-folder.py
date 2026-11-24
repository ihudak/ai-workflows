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
  run-folder.py dispatch <folder> <id> --area main|blind --agent <name> --agent-file <path> --model <id>
                --input <file|-> [--attach <path relative to the folder>]...
  run-folder.py done <folder> <id> [--from <file|->]
  run-folder.py gate <folder> <gate-id> --shown <file|->
  run-folder.py gate-record <folder> <gate-id> --shown <file|-> --answer <text>
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
non-null, exits 9 and writes nothing. discard and close refuse a path that is not a direct child of the runs
root holding a run.json. Exit codes: 0 done; 2 usage or could not run; 3 done found no result file; 9 taken
over (another session owns the run, or its folder was removed by a Start over).

A dispatch is saved before the agent runs (inputs/<id>.md) and its result is reused only once `done` has
recorded it and its fingerprint still matches: SHA-256 over the input's bytes, each attached run-folder file's
bytes (sorted by path), the agent definition file's SHA-256 and the model id. `done` records, in run.json
"results", what `results`, `stale` and `keep` read; "dispatches" holds what was handed out, "gates" the
answers to questions, "effects" the side effects started or finished. --command and --key are limited to
[A-Za-z0-9._-]. A value of --args, --set or --answer, and a log text, may be one flag-shaped token.
Standard library only.
"""

import argparse
import contextlib
import datetime
import fcntl
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
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+\Z")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*\Z")
AREAS = ("main", "blind")
GIT_TIMEOUT = 5


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


@contextlib.contextmanager
def write_lock(folder):
    """Hold an exclusive flock on <folder>/.lock for a whole load, modify and save of run.json, so parallel
    writing calls (sibling agents' dispatch and done) cannot lose each other's update. No lock where the
    folder is not a run folder: the call then fails or reports a takeover as it would anyway."""
    try:
        path = os.path.join(folder_path(folder), ".lock")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT, 0o600)
    except (CannotRun, OSError):
        yield
        return
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def needs_lock(args):
    if args.cmd in ("resume", "close", "phase", "log", "dispatch", "done", "gate-record", "keep"):
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
    for label, value in (("--command", a.command), ("--key", a.key)):
        if value is not None and value != "" and not NAME_RE.match(value):
            raise CannotRun("%s may hold only letters, digits, '.', '_' and '-': %r" % (label, value))
    if not a.command:
        raise CannotRun("--command is empty")
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
        rj = os.path.join(folder, "run.json")
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
                      "pruned": pruned, "summary": summarize(run)})
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
                      "pruned": pruned, "summary": summarize(run)})
                return 0
            # another open made this run's run.json first: read theirs on the next pass
        raise OSError("run.json could not be created: " + rj)
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
    load_for_write(a.folder)
    return remove_folder(a.folder)


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
    result_path = area_path(folder, a.area, "results", a.id)
    results = run.setdefault("results", {})
    rec = results.get(a.id)
    reusable = (isinstance(rec, dict) and rec.get("fingerprint") == fp and rec.get("area") == a.area
                and os.path.isfile(result_path) and os.path.getsize(result_path) > 0)
    if reusable:
        save_run(folder, run)
        append_progress(folder, "dispatch %s reuse" % a.id)
        emit({"action": "reuse", "input": input_path, "result": result_path, "fingerprint": fp})
        return 0
    for d in (os.path.dirname(input_path), os.path.dirname(result_path)):
        os.makedirs(d, mode=0o700, exist_ok=True)
    write_bytes_atomic(input_path, input_bytes)
    # A result redone is a result no longer recorded: drop the old one before the agent writes the new.
    results.pop(a.id, None)
    if a.id in run.get("kept", []):
        run["kept"] = [k for k in run["kept"] if k != a.id]
    try:
        os.unlink(result_path)
    except FileNotFoundError:
        pass
    run.setdefault("dispatches", {})[a.id] = {
        "fingerprint": fp, "content": content, "agent": a.agent, "agent_sha": agent_sha,
        "model": a.model, "area": a.area}
    save_run(folder, run)
    append_progress(folder, "dispatch %s made" % a.id)
    emit({"action": "dispatch", "input": input_path, "result": result_path, "fingerprint": fp})
    return 0


def cmd_done(a):
    check_id(a.id, "dispatch id")
    run = load_for_write(a.folder)
    folder = folder_path(a.folder)
    rec = run.get("dispatches", {}).get(a.id)
    if not isinstance(rec, dict):
        raise CannotRun("no dispatch recorded for " + a.id)
    result_path = area_path(folder, rec["area"], "results", a.id)
    if a.from_ is not None:
        data = read_input(a.from_)
        os.makedirs(os.path.dirname(result_path), mode=0o700, exist_ok=True)
        write_bytes_atomic(result_path, data)
    if not os.path.isfile(result_path) or os.path.getsize(result_path) == 0:
        raise MissingResult("no result file (or an empty one) for %s: %s" % (a.id, result_path))
    run.setdefault("results", {})[a.id] = dict(rec, done=now_iso())
    save_run(folder, run)
    append_progress(folder, "done %s" % a.id)
    emit({"recorded": True})
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
    shown = sha256_bytes(read_input(a.shown))
    run.setdefault("gates", {})[a.id] = {"shown": shown, "answer": a.answer, "at": now_iso()}
    save_run(a.folder, run)
    append_progress(a.folder, "gate %s answered" % a.id)
    emit({})
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


def cmd_stale(a):
    run = load_run(a.folder)
    shas, models = current_state(a)
    changed = []
    for rid, rec in sorted((run.get("results") or {}).items()):
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
    results = run.get("results") or {}
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
            "done": cmd_done, "gate": cmd_gate, "gate-record": cmd_gate_record, "effect": cmd_effect,
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
            expect(o["result"] == os.path.join(f, "main", "results", "d1.md"), o["result"])
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
            expect(o["result"] == os.path.join(f, "blind", "results", "d1.md"), o)
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
            expect(sorted(run_json(f)["dispatches"]) == sorted(ids), "a dispatch record was lost")
            for i in ids:
                os.makedirs(os.path.join(f, "main", "results"), exist_ok=True)
                with open(os.path.join(f, "main", "results", i + ".md"), "w") as fh:
                    fh.write("r")
            outs = parallel([["done", f, i] for i in ids] + [["phase", f, "p%d" % k] for k in range(4)]
                            + [["fact", f, "n%d" % k, "--set", "v"] for k in range(4)])
            expect(all(rc == 0 for rc, _e in outs), outs)
            run = run_json(f)
            expect(sorted(run["results"]) == sorted(ids), sorted(run["results"]))
            expect(sorted(run["facts"]) == ["n0", "n1", "n2", "n3"], run["facts"])
            expect(".lock" not in run["results"] and ".lock" not in run["dispatches"], "lock counted")

    for line in results:
        print(line)
    return 1 if failures else 0


FREE_TEXT_OPTIONS = ("--args", "--set", "--answer")
KNOWN_OPTIONS = FREE_TEXT_OPTIONS + (
    "--command", "--key", "--specs", "--workdir", "--shown", "--from", "--area", "--agent", "--agent-file",
    "--model", "--input", "--attach", "--ids", "--match", "-h", "--help")


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
    d = sub.add_parser("dispatch")
    d.add_argument("folder")
    d.add_argument("id")
    d.add_argument("--area", required=True, choices=AREAS)
    d.add_argument("--agent", required=True)
    d.add_argument("--agent-file", required=True)
    d.add_argument("--model", required=True)
    d.add_argument("--input", required=True)
    d.add_argument("--attach", action="append")
    dn = sub.add_parser("done")
    dn.add_argument("folder")
    dn.add_argument("id")
    dn.add_argument("--from", dest="from_")
    for name in ("gate", "gate-record"):
        g = sub.add_parser(name)
        g.add_argument("folder")
        g.add_argument("id")
        g.add_argument("--shown", required=True)
        if name == "gate-record":
            g.add_argument("--answer", required=True)
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
            with write_lock(args.folder):
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

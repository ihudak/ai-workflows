"""specs_git_state.py — the run's state record, one file per (session, command), for specs-git.py.

The record lives outside every repository, under ~/.claude/dev-workflows/specs-git/<session>/<command>.json,
keyed by the CLAUDE_CODE_SESSION_ID environment variable (Claude Code sets it in Bash tool subprocesses) and
the command, so a command typed in the middle of another run never touches the outer run's record. Python
standard library only; loaded by specs-git.py only for the subcommands that need it.

Of the fields start keeps: branch is the branch HEAD stands on when a start call returns (null on a detached HEAD,
or where the gate did not pass); stage is the stage of specs-preflight start goes on from; settle_todo is null until
the settle loop computes, on entering it, the branches it has still to settle; pending holds the settle loop's
branches whose push origin rejected as non-fast-forward, each {branch, set_upstream, standing}, standing the branch
the run stood on then; budget is the last start call's --budget where it was not the default, which the start --resume
a budget stop or a replay names repeats, and which resumable's argument test never reads; reported holds each
once-a-run report start printed (pre.merged-unknown and pre.scope-failed with their branch, pre.status-failed), so a
resume or a --rerun never prints one again; stay is null, or {branch, kind, reason, merged, command}: the plugin branch
the preflight ended on without leaving it, though it would have left it (specs-repo-git §4 step 1), which end reads --
its kind one of specs-git.py's STAY_KINDS (mid-run, one kept while another run of the session was open there; else
merged, one branch-merged read merged; else unkeyed, one no key of the run names), merged the branch's merged answer
whatever the kind, reason why it stayed, one of STAY_REASONS (g1; unlisted, status could not run; refused, git refused
the merged-branch leave's switch, B2's or B4's; stopped, an early stop before the switch; mid-run), and command the open
run's command where the run was typed mid-run, else null; each preflight derives its own, so a --rerun starts with none,
and a start that leaves the branch clears it. A record an earlier version of this plugin wrote holds merged_stay,
{branch, reason}, in its place, which load maps to a stay of kind merged with its merged flag set. start_dirty is null,
or {path: blob or null}: the snapshot of the session files dirty when the run's start took it, each path's working copy
kept as a blob (null for a path with no file), taken by a fresh start that is not a --rerun, where the gate passed, no
misrooted flag stands and session-branch mode is not on, and null where it could not be taken; every start call whose
gate passed narrows it as it returns to the paths still dirty, each keeping its blob, and a --rerun carries its first
start's. midrun is null, or {command, started, branch}: the open run this one was typed under (specs-repo-git §3.5).
protects is true, save on a record a later run of the same command restored, which no longer protects its branch
(§3.5). A record an earlier version wrote lacks these four fields: load gives each its default.
"""

import calendar
import copy
import json
import os
import re
import tempfile
import time

VERSION = 1
SESSION_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")
COMMAND_RE = re.compile(r"/[a-z][a-z0-9-]*")
STAMP = "%Y-%m-%dT%H:%M:%SZ"

# The record's keys and their defaults; a key outside this table is refused on new() and save().
FIELDS = {
    "version": VERSION,
    "session": "",
    "command": "",
    "started": "",
    "updated": "",
    "args": {},  # the start call's arguments: specs, keys, commit_key, register_rebuild
    "started_by_script": True,
    "specs": "",
    "env_line": None,
    "gate": None,
    "top": None,
    "keys": [],
    "commit_key": None,
    "register_rebuild": None,
    "specs_git": None,
    "misrooted_notice": None,  # a list of lines
    "guard": None,
    "guard_block": None,
    "guard_paths": [],
    "default": None,
    "default_ref": None,
    "remote": None,
    "offline": False,
    "mode": None,
    "session_branch": None,
    "session_branch_created": None,
    "b2_left": None,
    "b4_left": None,
    "stay": None,  # {branch, kind, reason, merged, command}: the branch the preflight stayed on and would have left
    "start_dirty": None,  # {path: blob | None}: the session files dirty when the start took its snapshot
    "midrun": None,  # {command, started, branch}: the open run this one was typed under
    "protects": True,  # false on a record a later run of the same command restored
    "branch": None,  # the branch HEAD stands on when a start call returns
    "advised_D": [],
    "reported": [],  # start's once-a-run reports printed: "<template id>[ <branch>]"
    "declined": [],
    "stage": "new",
    "pending": [],
    "settle_todo": [],
    "budget": None,  # a start call's --budget where it was not the default; never part of args
    "end_commit": None,
}


class NoSession(Exception):
    """No usable session id: the record cannot be keyed, so the caller reports `not run`."""


def session_id():
    value = os.environ.get("CLAUDE_CODE_SESSION_ID", "")
    if not SESSION_RE.fullmatch(value):
        raise NoSession("CLAUDE_CODE_SESSION_ID is unset or not a session id")
    return value


def root():
    return os.path.join(os.path.expanduser("~"), ".claude", "dev-workflows", "specs-git")


def path(session, command):
    if not COMMAND_RE.fullmatch(command):
        raise ValueError("a command is /<name>, got %r" % command)
    if not SESSION_RE.fullmatch(session):
        raise ValueError("not a session id: %r" % session)
    return os.path.join(root(), session, command.lstrip("/") + ".json")


def _now():
    return time.strftime(STAMP, time.gmtime())


def _check_keys(rec):
    unknown = sorted(set(rec) - set(FIELDS))
    if unknown:
        raise ValueError("unknown record key: %s" % ", ".join(unknown))


def new(command, **values):
    rec = copy.deepcopy(FIELDS)
    _check_keys(values)
    rec.update(copy.deepcopy(values))
    rec["session"] = rec["session"] or session_id()
    rec["command"] = command
    rec["started"] = _now()
    return rec


def load(session, command):
    try:
        with open(path(session, command), encoding="utf-8") as fh:
            rec = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(rec, dict) or rec.get("version") != VERSION:
        return None
    if "merged_stay" in rec:  # an earlier version's record: its stay was always a merged one
        old = rec.pop("merged_stay")
        if isinstance(old, dict) and old.get("branch") and rec.get("stay") is None:
            rec["stay"] = {"branch": old["branch"], "kind": "merged", "reason": old.get("reason"), "merged": True,
                           "command": None}
    for key in ("stay", "start_dirty", "midrun", "protects"):  # the fields an earlier version's record lacks
        rec.setdefault(key, copy.deepcopy(FIELDS[key]))
    return rec


def save(session, command, rec):
    _check_keys(rec)
    target = path(session, command)
    rec["updated"] = _now()
    directory = os.path.dirname(target)
    os.makedirs(directory, mode=0o700, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def saved_within(rec, minutes=15):
    """Whether <rec> was saved within the last <minutes>, by its updated stamp; False where that cannot be read."""
    try:
        updated = calendar.timegm(time.strptime(rec.get("updated") or "", STAMP))
    except (ValueError, TypeError):
        return False
    return 0 <= time.time() - updated <= minutes * 60


def resumable(rec, args, minutes=15):
    if rec.get("stage") == "done" or rec.get("args") != args:
        return False
    return saved_within(rec, minutes)


def _rmdir_if_empty(directory):
    try:
        os.rmdir(directory)
    except OSError:
        pass


def remove(session, command):
    target = path(session, command)
    try:
        os.unlink(target)
    except FileNotFoundError:
        return False
    _rmdir_if_empty(os.path.dirname(target))
    return True


def prune(keep_session, days=7):
    removed = []
    base = root()
    cutoff = time.time() - days * 86400
    try:
        sessions = sorted(os.listdir(base))
    except OSError:
        return removed
    for name in sessions:
        directory = os.path.join(base, name)
        if name == keep_session or not os.path.isdir(directory):
            continue
        try:  # best effort: another session's run may remove a file at the same moment
            entries = sorted(os.listdir(directory))
        except OSError:
            continue
        for entry in entries:
            full = os.path.join(directory, entry)
            try:
                if entry.endswith(".json") and os.path.isfile(full) and os.path.getmtime(full) < cutoff:
                    os.unlink(full)
                    removed.append(full)
            except OSError:
                continue
        _rmdir_if_empty(directory)
    return removed

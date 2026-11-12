"""specs_git_state.py — the run's state record, one file per (session, command), for specs-git.py.

The record lives outside every repository, under ~/.claude/dev-workflows/specs-git/<session>/<command>.json,
keyed by the CLAUDE_CODE_SESSION_ID environment variable (Claude Code sets it in Bash tool subprocesses) and
the command. A different command typed in the middle of another run (specs-repo-git §3.5) is kept off the open
run's record by its own file; the same command typed twice, by parking: the second run's start moves the first's
record aside to <command>.<stamp>.json, the stamp its started with "-" and ":" removed (park) -- still protecting its
branch where the two starts' run key sets differ -- and each run names its
own record by any started its starts returned (find; end, declined, and start --rerun and --resume, by --started), so
the two may end in either order, the second's end restoring the first's record (unpark), and the first's re-run
saving its new record under a stamp of its own (stamped). save, load and remove take that path as at. Python standard library
only; loaded by specs-git.py only for the subcommands that need it.

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
start's. midrun is null, or {command, started, branch, keys}: the open run this one was typed under (specs-repo-git
§3.5), keys its key set when this run started (a record an earlier version wrote lacks it).
protects is true, save on a record a later start of the same command with the same run key set, or where either start
recorded none, parked or marked so (stop_protecting) -- a restart, after which it no longer protects its branch, and
the later run's own record protects it while that run stands (§3.5); one parked by a later start whose key set
differs keeps it true. park sets it by the two starts' key sets (the start passes protects), stop_protecting writes it
false, unpark keeps it as it stands, a re-run of a parked record keeps it on the record it saves in its place, and a
re-run of the record at <command>.json saves a new record, its protects true. parked is true on a record park moved aside,
and only there: unpark takes no other, so a record a declined call made at a derived path (find) is never taken for a
parked one. started_before lists the started of each earlier start of the run whose record a re-run, or a continuation that
started afresh on its own record -- named by --started, or, named by none, one marked call_returned false --
took over, oldest first, so that find reaches the run's record by any stamp its
starts returned; a record whose started another record of its command lists there is one a re-run cut off between its
save and its removal of the file it re-ran from left behind: records() leaves it out, so no reader restores it, reads
it as open or names it, and the next save or the removal of the record that lists it, or the save of another run's
record over that one, removes it. call_returned is false from the first write of a plain start or a continuation given
no --started -- calls whose run learns the stamp only from their JSON -- until that call returns its JSON, an error's
included; a named call or a re-run, whose run holds a stamp already, never writes it false. So a record such a call
left where the harness stopped it keeps it false -- until a later start parks it and an end restores it (unpark),
which marks it true. A record an earlier
version wrote lacks these seven fields: load gives each its default (call_returned true: returned). held_changed holds
the paths the held stage took out of their held entries as changed since they were held (specs-repo-git §3.2), which
the flush reports for each it commits (§3.4); a record that lacks it reads as holding none. held_attempted holds the
held entries (each held commit's id) the held stage has tried in this start and reported held again or stuck, which a
resumed stage keeps and does not report again (§3.2), cleared as the stage ends; a record that lacks it reads as
holding none.
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
STARTED_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z")  # a record's started, as STAMP writes it
# A record file's name: <name>.json, or <name>.<stamp>.json -- park's, or a derived path find names -- <stamp> a
# started with "-" and ":" removed, and -2, -3 where park found it taken.
_FILE_RE = re.compile(r"([a-z][a-z0-9-]*)(?:\.([0-9]{8}T[0-9]{6}Z(?:-[0-9]+)?))?\.json")

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
    "midrun": None,  # {command, started, branch, keys}: the open run this one was typed under
    "protects": True,  # false on a record a later start of its command with the same key set, or keyless, parked or
    # marked (stop_protecting), and kept by the end that restores it; true where the key sets differed
    "parked": False,  # true on a record park moved aside for a later run of the same command
    "started_before": [],  # the started of each earlier start of the run whose record a later start of it took over
    "call_returned": True,  # false from an unnamed plain start's or continuation's first write until its JSON returns
    "branch": None,  # the branch HEAD stands on when a start call returns
    "advised_D": [],
    "reported": [],  # start's once-a-run reports printed: "<template id>[ <branch>]"
    "declined": [],
    "stage": "new",
    "pending": [],
    "settle_todo": [],
    "held_changed": [],  # the held stage's changed held files, which the flush reports where it commits them
    "held_attempted": [],  # the held entries this start's held stage has tried and reported, kept on a resume
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


def _stamp(started):
    """The stamp a record's file name carries for <started>: STAMP's text with "-" and ":" removed."""
    if not isinstance(started, str) or not STARTED_RE.fullmatch(started):
        raise ValueError("not a started stamp: %r" % (started,))
    return started.replace("-", "").replace(":", "")


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


def load(session, command, at=None):
    """The record of <session> and <command> -- at <at>, the record file to read in place of <command>.json, where
    given -- or None where none stands there, it cannot be read, or another version wrote it."""
    return _read(at or path(session, command))


def _read(target):
    try:
        with open(target, encoding="utf-8") as fh:
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
    for key in ("stay", "start_dirty", "midrun", "protects", "parked", "started_before", "call_returned"):  # earlier
        rec.setdefault(key, copy.deepcopy(FIELDS[key]))
    return rec


def save(session, command, rec, at=None):
    """<rec> written as the record of <session> and <command> -- at <at>, the record file to write in place of
    <command>.json, where given -- its updated stamp set to now; then each file it left behind removed
    (_remove_left_behind). Where <at> already holds a record -- another run's among them -- each file that record
    left behind is removed first, as its own removal would: once it is overwritten, nothing lists their stamps, and they
    would be listed, restored and named again. Whose record it is goes untested, since a started stamp tells two runs
    apart only to the second: for one of this run's records the files are the ones <rec> lists too."""
    _check_keys(rec)
    rec["updated"] = _now()
    target = at or path(session, command)
    there = _read(target)
    if there is not None:
        _remove_left_behind(session, command, there, target)
    _write(target, rec)
    _remove_left_behind(session, command, rec, target)


def _write(target, rec):
    """<rec> written to <target> whole or not at all: a temporary file beside it, then replaced."""
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


def remove(session, command, at=None):
    """The record of <session> and <command> removed -- at <at>, the record file to remove in place of
    <command>.json, where given -- and the session's directory with it where that leaves it empty. False where none
    stood there."""
    target = at or path(session, command)
    rec = _read(target)
    try:
        os.unlink(target)
    except FileNotFoundError:
        return False
    if rec is not None:
        _remove_left_behind(session, command, rec, target)
    _rmdir_if_empty(os.path.dirname(target))
    return True


def earlier(rec):
    """The stamps <rec> lists in started_before: the started of each earlier start of its run whose record a later
    start of it took over (specs-repo-git §7)."""
    got = rec.get("started_before") if isinstance(rec, dict) else None
    return [s for s in got if isinstance(s, str) and s] if isinstance(got, list) else []


def _remove_left_behind(session, command, rec, keep):
    """Each file of <command> but <keep> whose record's started <rec> lists in started_before removed: a file a re-run
    cut off between its save and its removal of the file it re-ran from left behind (specs-repo-git §3.5). Best
    effort: one another call removes first is passed over."""
    stamps = set(earlier(rec))
    if not stamps:
        return
    for full, other in _scan(session):
        if full != keep and _name_of(full) == command.lstrip("/") and other.get("started") in stamps:
            try:
                os.unlink(full)
            except OSError:
                pass


def records(session):
    """(path, record) for every record in the session's directory -- <name>.json and <name>.<stamp>.json alike, parked
    ones and those at a derived path included -- oldest started first; a temporary file (.tmp-*), a file of another
    name, one that cannot be read and one another version wrote are left out, and so is a record another record of its
    command lists in started_before: a file a re-run cut off before removing it left behind (_remove_left_behind), which
    no reader restores, reads as an open run or names (others, mine, unpark, find)."""
    found = _scan(session)
    listed = {}
    for full, rec in found:
        for stamp in earlier(rec):
            listed.setdefault((_name_of(full), stamp), set()).add(full)
    return [(full, rec) for full, rec in found
            if not listed.get((_name_of(full), rec.get("started")), set()) - {full}]


def _scan(session):
    """records() before it leaves out the files re-runs left behind."""
    if not SESSION_RE.fullmatch(session):
        raise ValueError("not a session id: %r" % session)
    directory = os.path.join(root(), session)
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        return []
    found = []
    for name in names:
        if not _FILE_RE.fullmatch(name):
            continue
        full = os.path.join(directory, name)
        rec = _read(full)
        if rec is not None:
            found.append((full, rec))
    found.sort(key=lambda pr: (str(pr[1].get("started") or ""), os.path.basename(pr[0])))
    return found


def _name_of(full):
    return _FILE_RE.fullmatch(os.path.basename(full)).group(1)


def others(session, command):
    """Every record in the session's directory that is not <command>'s, by its file's name -- <name>.json or
    <name>.<stamp>.json, parked ones of other commands included -- oldest started first (records)."""
    if not COMMAND_RE.fullmatch(command):
        raise ValueError("a command is /<name>, got %r" % command)
    return [rec for full, rec in records(session) if _name_of(full) != command.lstrip("/")]


def mine(session, command):
    """(path, record) for each of <command>'s own records: <name>.json, parked ones and those at a derived path, oldest
    started first (records)."""
    if not COMMAND_RE.fullmatch(command):
        raise ValueError("a command is /<name>, got %r" % command)
    return [(full, rec) for full, rec in records(session) if _name_of(full) == command.lstrip("/")]


def _parked_path(session, command, started, taken=True):
    """<name>.<stamp>.json for <started>; with <taken>, the first of it, then -2, -3 before .json, that no file holds."""
    base = os.path.join(os.path.dirname(path(session, command)), "%s.%s" % (command.lstrip("/"), _stamp(started)))
    target, n = base + ".json", 2
    while taken and os.path.lexists(target):
        target, n = "%s-%d.json" % (base, n), n + 1
    return target


def stamped(session, command, started):
    """A record file of its own for the run of <command> that started at <started>: <name>.<stamp>.json, -2, -3 before
    .json where taken -- where a re-run of a run whose record is not <command>.json saves its new record (§3.5)."""
    return _parked_path(session, command, started)


def park(session, command, protects=False):
    """<command>.json moved aside to <name>.<stamp>.json, the stamp its started with "-" and ":" removed (-2, -3
    before .json where taken), marked parked: true, its updated stamp kept: the record of an open run of the same
    command typed twice (specs-repo-git §3.5), for that run's own end. <protects>: true where the two starts' run key
    sets differ -- that run stays protected, and the later run is typed under it -- else false, a restart: it protects
    nothing from then on, and the later run's own record protects the branch while it stands. Its new path, or None
    where no record stood."""
    src = path(session, command)
    rec = _read(src)
    if rec is None:
        return None
    target = _parked_path(session, command, rec.get("started") or _now())
    rec.update(parked=True, protects=bool(protects))
    _write(target, rec)
    os.unlink(src)
    return target


def stop_protecting(target):
    """The record file <target> -- a parked record of an open run whose command a later start typed again with the
    same run key set (specs-repo-git §3.5) -- marked protects: false, its updated stamp kept. False where none stands
    there."""
    rec = _read(target)
    if rec is None:
        return False
    rec["protects"] = False
    _write(target, rec)
    return True


def unpark(session, command, keep):
    """The newest parked file of <command> -- one marked parked: true, never a record at a derived path -- back to
    <command>.json, parked no longer, its protects as it stands (false where the start that parked it was a restart,
    true where its key set differed), where keep(record) holds: "restored"; removed otherwise: "dropped". None where
    none is parked. A restored record is marked call_returned: true: a later start of its command parked it, so the
    start that left it false was overtaken, and no continuation given no --started remakes it -- the skill makes one
    only straight after the harness stops its run's own start -- so such a continuation of another run, made with the
    same arguments, meets it as a plain start does (specs-repo-git §3.5) rather than going on with it."""
    parked = [(full, rec) for full, rec in mine(session, command)
              if full != path(session, command) and rec.get("parked") is True]
    if not parked:
        return None
    full, rec = parked[-1]
    if keep(rec):
        rec.update(parked=False, call_returned=True)
        _write(path(session, command), rec)
        os.unlink(full)
        return "restored"
    os.unlink(full)
    return "dropped"


def find(session, command, started):
    """The record of <command>'s run that <started> names (specs-repo-git §7's end --started), by any stamp that run's
    starts returned: (path, record) -- of <command>'s own records (mine: <command>.json, parked ones and those at a
    derived path, never one a re-run left behind), one whose started is <started> or whose started_before lists it, the
    newest started where several are; on a tie <command>.json, then <name>.<stamp>.json, the stamp derived from
    <started> as park derives it, then its -2, -3; else that derived path by name, with its record, or with None where
    no file stands there. Never <command>.json for another run: only a later start of the run <started> names lists it
    -- its re-run (_carry), or its continuation that started afresh on its record, named by --started or, named by
    none, finding it marked call_returned false."""
    main = path(session, command)
    derived = _parked_path(session, command, started, taken=False)
    base = derived[:-len(".json")]

    def rank(full):
        if full == main:
            return 0
        if full == derived:
            return 1
        m = re.fullmatch(re.escape(base) + r"-([0-9]+)\.json", full)
        return int(m.group(1)) if m else 1 << 30

    hits = [(full, rec) for full, rec in mine(session, command)
            if rec.get("started") == started or started in earlier(rec)]
    if hits:
        return max(hits, key=lambda pr: (str(pr[1].get("started") or ""), -rank(pr[0])))
    return derived, _read(derived)


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

#!/usr/bin/env python3
"""run-state.py -- /implement's run-state file: create, resume or peek at it, open a phase, set,
append, persist, read, remove.

The file is `$(git rev-parse --git-path dev-workflows/implement-run.json)` in the code repository
the run works in: per worktree, inside the git directory, never staged. `/implement` Phase 1.4
creates it and every later phase opens with `open`; commands/implement.md says what each key holds
and where it is written. Run every call from the working directory (or pass --repo <dir>). One
`/implement` run per worktree at a time is the precondition; the lock below serialises one run's own
calls, never two runs, and the session guard below stops a run that another has taken over. Beside
the file, in the same directory, are the durable directory, `implement-run.d/`, which holds the
copies `persist` makes, and the tombstone, `implement-run.done`, which `remove` leaves.

The session is the environment's CLAUDE_CODE_SESSION_ID, null where it is unset or empty. `init`
writes `session` and `started`, `init --resume` writes `session`, nothing else touches `session`, and
every call that changes the file stamps `updated`; both times are UTC YYYY-MM-DDTHH:MM:SSZ. The
session guard: `open`, `set`, `append`, `persist`, `remove` and `init --recover` exit 9, nothing
written, where the file's `session` and the caller's are both non-null and differ. `read`, `peek`,
plain `init` and `init --resume` are not guarded. `session`, `started`, `updated`, `durable` and
`tree.snapshot` are the script's own: `set`, `append` and `init` refuse each with exit 3,
`tree.snapshot` also as a member of an object given for `tree`.

  run-state.py init [--recover]      a JSON object on stdin, merged over KEYS' defaults: every key or
                                     member it omits takes the default KEYS gives it, and it may hold
                                     no key or member KEYS lacks, nor one of the wrong type, nor one
                                     of the script's own -- all checked before anything is moved; it
                                     writes `format` 2. A file already there is moved
                                     aside, as implement-run.json.stale-<UTC stamp>, none of it carried
                                     into the new file -- plain init never reads it, and --recover
                                     only for its `session` -- after any
                                     older such file is removed, so at most one is kept; the move is
                                     printed. Plain init first deletes the durable directory, printed
                                     `removed: <it>` where there was one, and the tombstone, so a
                                     failure there leaves the file where it was; and it
                                     appends to `assumptions` that a file an earlier run left was not
                                     resumed and was moved aside, saying its durable copies were
                                     deleted where the directory held any. Under --recover the
                                     directory and the tombstone stay, `durable` starts empty, and the
                                     line appended names the file as this run's own, written again,
                                     and says whether one was moved aside; --recover exits 9 where the
                                     tombstone's session and the caller's are both non-null and differ.
  run-state.py init --resume         take over in place the file an earlier run left, never moving it:
                                     exit 1 with no file, 5 where it does not parse, 8 where its
                                     format is not 2 -- the file checked before stdin is read, so a
                                     missing file exits 1 whatever stdin holds. Stdin is a JSON object holding only specs_git,
                                     specs_merged_branch, lineage, routing, coding_model, run_flags,
                                     inputs_read and report.notices -- any other key, or a value of
                                     the wrong type, exits 3, nothing written: inputs_read's and
                                     report.notices' values are appended to the file's lists, and the
                                     others written as set writes them -- `routing`, an object, merged
                                     over the file's own members. Then each path location --
                                     every `files` member, each `step_groups` report, each `reviews`
                                     diff and return file, each `patches` path, and
                                     `lineage.check_file` (never `tree.snapshot`, which names its own
                                     copy) -- is, the first that applies: left, where a file is at
                                     its path; repointed to the copy, where `durable[<its key path>]`
                                     has `of` naming its path (compared as absolute paths) and that
                                     copy is a file -- the original deleted, once, where something not
                                     a directory is left at its name and the name begins `dw-impl-` --
                                     printed `repointed:`;
                                     else set to null, printed `cleared:`. No other location is
                                     touched. It appends `Resumed at <phase> step <step> after session
                                     <id> stopped at <updated>` to `assumptions` (` step <step>` left
                                     out where `step` is null, a null session or time as `unknown`),
                                     and writes `session`.
  run-state.py peek                  print the file, changing, moving and locking nothing: exit 1 with
                                     no file, 5 where it does not parse, 8 where its format is not 2,
                                     printing nothing.
  run-state.py open <phase>          set `phase`, reset `step` to null, and print the file.
  run-state.py read [<key>]          print the file, or one key, changing nothing.
  run-state.py set <key> <json> [<key> <json> ...]
                                     set each key to the JSON value after it, the key written again
                                     before each value; with no pairs, a JSON object of key: value on
                                     stdin. Several keys are written in one replace. Every value is
                                     checked against KEYS as init's are: a key or member KEYS lacks,
                                     or a top-level key or a <key>.<member> of an object key given a
                                     value of another type than its default fixes, exits 3 -- every
                                     such slip in the call named at once, nothing written. A top-level
                                     key whose default is an object, given an object, takes its
                                     members over the ones the file holds: a member it leaves out
                                     keeps its value. A deeper path or a list entry is not checked.
                                     Each `durable` entry whose label is a key path that names neither
                                     its `of` nor its copy after the write, compared as absolute
                                     paths, is dropped; a `note:` entry and the `tree.snapshot` entry
                                     never are.
                                     Once the write lands, each path the file named before the call --
                                     a `files` member, a `step_groups` report, a `reviews` diff or
                                     return file or a `patches` path --
                                     that none of them names after it is removed, where it is a
                                     regular file, not a symlink, whose name begins `dw-impl-`, and
                                     lies outside the durable directory, and
                                     printed `removed: <path>`; then each dropped entry's copy inside
                                     the durable directory, where no path location, `tree.snapshot`
                                     or other entry names it, printed the same way; one whose
                                     removal fails is printed
                                     `left: <path> -- <error>`, and the call still exits 0.
  run-state.py append <key> <json> [<key> <json> ...]
                                     append each value to its key's list, the key written again
                                     before each value -- append assumptions '"a"' assumptions '"b"'
                                     -- or a JSON object on stdin; a key that is null becomes a
                                     one-element list. Each value is one entry, so a value that is a
                                     JSON array, in either form, exits 2, nothing written: give one
                                     value per pair, or write the whole list with set. An object
                                     appended to `step_groups` is stamped `started`, the UTC time.
  run-state.py persist <label> <file>
                                     copy <file> into the durable directory, print the copy's absolute
                                     path, and set durable[<label>] to {"copy": <that path>, "of":
                                     <file as given>}. The label is a key path naming one of the
                                     path locations init --resume walks, or `tree.snapshot` -- a
                                     negative list index (step_groups.-1.report) written as its
                                     absolute index -- or note:<path>, for a note's working copy. A
                                     label has one copy, which its next persist replaces in place --
                                     save where a location other than the label's own key, or another
                                     entry, names that copy: then the copy is written under a fresh
                                     name, and the one it supersedes is deleted once nothing names
                                     it. `persist
                                     tree.snapshot` also writes `tree.snapshot`, the copy's path: it
                                     is that key's only writer. A file that is not there exits 2, and
                                     a label naming no path location exits 3.
  run-state.py remove [--keep <path>] ...
                                     the end-of-run removal: every temp file `files` names, each
                                     `step_groups` report, each `reviews` diff and return file and each `patches` path marked `temp`
                                     -- only a regular file whose name begins `dw-impl-`, and never
                                     a --keep path; a path inside the durable directory is skipped,
                                     unprinted -- then the file itself, only at the git path, leaving
                                     the tombstone, {"session": <the removed file's session, or the
                                     caller's where it holds none>, "at": <UTC time>}; then the
                                     durable directory, whole, printed `removed: <it>`. A --keep path
                                     inside the durable directory is first moved out, beside the file,
                                     as implement-run.kept-<its name>, printed `kept: <that path>`,
                                     where it stays. With no file it deletes the durable directory
                                     alone, under the lock, the same --keep paths moved out first, and
                                     writes no tombstone. Wherever the file or the directory is there,
                                     the lock is taken first and the file tested again under it, so a
                                     file another call wrote while this one waited is guarded.

A key is a top-level name or a dotted path into one (`files.plan_file`); a list entry is named by
its index (`triage.-1.followed_by`, the last entry's). `set`, `append`, `read` and `persist` refuse a
key the file does not hold, and `set` a path through a null value: write that key whole. A file
lacking a key of FILLED (one an earlier format-2 release wrote) reads as holding that key's default,
which `read` and `peek` print and the next call that writes the file saves into it; any other key it
lacks is still exit 3, and the fill itself writes nothing. Every
read-modify-write holds an exclusive lock (fcntl.flock on .implement-run.lock beside the file) and
replaces the file whole (a temp file beside it, then os.replace), so a write is never half done and
parallel calls lose nothing; a value that does not parse changes nothing. Input -- stdin and argv --
is read as UTF-8 whatever the locale, and the file is UTF-8 with non-ASCII written as itself
(ensure_ascii=False), so a path comes back as git's -z record gave it. JSON escapes `"`, `\\` and
control characters -- `\\t`, `\\n`, `\\r` and the like -- in what `open`, `read` and `peek` print, and each
escape reads back as one character. A call other than `init` that finds no file creates nothing: it
checks for the file before it makes the lock beside it -- save `remove`, which, finding a durable
directory there, takes the lock to delete it. The lock file, like a stale file, is never removed.

Exit codes:
  0  done
  1  there is no run-state file (and nothing was created)
  2  usage: bad arguments -- set's or append's among them an odd count, or a key opening with `"`,
     `[` or `{`, a value written where its key belongs, and append's a JSON array value -- a value
     that does not parse, input that is not UTF-8, a path through null, no such list entry, and
     persist's file not there
  3  a key the file does not hold (set, append, read, persist), or an init object or a set call adding
     a key or member KEYS lacks, or giving one the wrong type; a script-owned key written (set,
     append, init); a persist label naming no path location; an init --resume key outside its list
  4  the file could not be reached: an OSError reading or writing it -- an unreadable directory on
     its path included -- or git failing to name it
  5  the run-state file is there and does not parse
  8  the run-state file's format is not 2 (peek, init --resume)
  9  the session guard: the file belongs to another session; or, from init --recover, the tombstone
     names another session
No call exits 6 or 7: commands/implement.md keeps 6 for a missing path its own `test -e` finds.
Standard library only; `python3 run-state.py --selftest` runs the tests.
"""
import copy
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

try:
    import fcntl
except ImportError:  # no flock on this host: one run's calls are sequential anyway
    fcntl = None

REL = "dev-workflows/implement-run.json"
STALE_RE = re.compile(r"^implement-run\.json\.stale-\d{8}T\d{6}Z$")
TEMP_PREFIX = "dw-impl-"
LOCK = ".implement-run.lock"
DURABLE = "implement-run.d"  # beside the file: git's own `--git-path dev-workflows/implement-run.d`
TOMBSTONE = "implement-run.done"
OWNED = ("session", "started", "updated", "durable")  # and tree.snapshot: the script's own keys
NOTE = "note:"
RESUME_KEYS = ("specs_git", "specs_merged_branch", "lineage", "routing", "coding_model", "run_flags",
               "inputs_read", "report.notices")
RESUME_APPENDED = ("inputs_read", "report.notices")

# Every key the file holds, and no other, each beside the default init gives it where the caller's
# object omits it. A key whose default is an object holds exactly that object's members -- the ones
# a call may name -- each beside its own default. The default fixes the type: a key or member whose
# default is an object, a list, a boolean, an integer or a string must be given as one; one whose
# default is null takes any JSON value. `init` and `set` both hold what they are given to this list, and
# `set` merges an object given for an object key over the members the file holds.
# List shapes, for the entries KEYS does not check (a list entry is not):
#   pieces   {"name", "files": [], "contract": []}
#   reviews  {"round": "first"|"re-review", "scope": "piece:<name>"|"overall", "paths": [],
#             "diff_file", "return_file", "verdict"} -- one per review a split round dispatches;
#            "paths" a piece's matched paths, or for "overall" the paths no piece matched;
#            the two files temp files
#   check_run_answers  {"path", "answer"} -- one per path a check run touched, as its answer settles it
#   step_groups  each entry stamped "started", the UTC time, by `append step_groups`; each carries
#            "model", the coding_model its dispatch passed -- the run writes it
#   report.maintenance  each entry carries "agent": docs, knowledge, instructions, impl-maintenance or
#            defect-reporter -- the run writes it
# Two objects whose members are not fixed: `durable` -- {<label>: {"copy", "of"}}, written by persist
# alone -- and `conformance.note_blobs` -- {<annotated path>: <its blob on <default-ref>, or null>}.
# commands/implement.md quotes this list (KEYS_LINE); the selftest holds the two equal.
KEYS = [
    ("format", 2), ("session", None), ("started", None), ("updated", None),
    ("phase", "Phase 1.4"), ("step", None), ("stopping", None),
    ("mode", None), ("key", None), ("source", None),
    ("focus_key", None), ("unit_key", None), ("workitem_key", None), ("unit_folder", None),
    ("run_flags", None), ("run_environment", None), ("specs_git", None), ("specs_merged_branch", None),
    ("lineage", None),
    ("inputs_read", []),
    ("spec_context", {"spec_paths": [], "in_scope_ids": None, "applicable_spec": None,
                      "applicable_ard": None, "ard_paths": [], "companion_run": None,
                      "tasks_only": None}),
    ("task_shape", None), ("clarifications", {"settled": [], "answers": []}),
    ("routing", {"block": None, "history": []}), ("class", None), ("coding_model", None),
    ("fable_escalation", {"source": None, "choice": None}),
    ("branch_answer", {"answer": None, "moves": [], "lines": []}), ("branch", None),
    ("stash_before", None), ("stash_ref", None), ("pre_existing_dirty", None), ("check_run_answers", []),
    ("session_branch_lift", False),
    ("session_branch_created", None), ("test_decision", None), ("test_typechecks", []),
    ("clean_finish", True),
    ("files", {"task_description_file": None, "plan_file": None, "pending_plan_file": None,
               "summary_file": None, "baseline_file": None, "test_diff_file": None,
               "test_report_file": None, "typecheck_file": None, "review_diff_file": None, "partial_diff_file": None, "review_return_file": None,
               "review_file": None, "claims_file": None, "failure_file": None,
               "snapshot_before": None, "snapshot_after": None}),
    ("tree", {"head": None, "snapshot": None, "when": None}),
    ("step_groups", []), ("pieces", []), ("reviews", []), ("review_in_hand", None), ("patches", []),
    ("triage", []),
    ("conformance", {"summary": None, "annotated": [], "gaps": [], "handoff_line": None, "note_blobs": {}}),
    ("other_repo_changes", []), ("assumptions", []), ("deferred", []),
    ("report", {"commands_run": [], "maintenance": [], "notices": [], "phase1_tasks": [],
                "confirmed_cause": None}),
    ("phase46_head", None), ("code_repo_outcome", None), ("replans_used", 0),
    ("durable", {}),
]
KEYS_LINE = " ".join(k + ("{%s}" % " ".join(d) if isinstance(d, dict) else "") for k, d in KEYS)
# The keys added since format 2, which a file an earlier format-2 release wrote can lack: load gives
# each one it lacks its KEYS default. No other key is filled -- `format` least of all.
FILLED = ("fable_escalation",)


class Fail(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code


def state_path(repo):
    try:
        out = subprocess.run(["git", "-C", repo, "rev-parse", "--git-path", REL],
                             capture_output=True, text=True)
    except OSError as e:
        raise Fail(4, "git could not run: %s" % e)
    if out.returncode != 0:
        raise Fail(4, "git rev-parse --git-path failed: %s" % out.stderr.strip())
    p = out.stdout.rstrip("\n")
    return p if os.path.isabs(p) else os.path.join(os.path.abspath(repo), p)


def guarded(path):
    """True only for the run-state file's own path, as git names it."""
    return (os.path.basename(path) == "implement-run.json"
            and os.path.basename(os.path.dirname(path)) == "dev-workflows")


def durable_dir(f):
    return os.path.join(os.path.dirname(f), DURABLE)


def tombstone_path(f):
    return os.path.join(os.path.dirname(f), TOMBSTONE)


def inside(p, d):
    """True where path p lies inside directory d."""
    return os.path.abspath(p).startswith(os.path.abspath(d) + os.sep)


def same(a, b):
    """True where a and b are both paths naming the same absolute path."""
    return isinstance(a, str) and isinstance(b, str) and os.path.abspath(a) == os.path.abspath(b)


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def guard(d, session, verb):
    """The session guard: exit 9 where the file's session and the caller's are both non-null and differ."""
    held = d.get("session") if isinstance(d, dict) else None
    if held is not None and session is not None and held != session:
        raise Fail(9, "%s: the run-state file belongs to session %s, not this call's session %s -- another "
                      "/implement took this run over; nothing written" % (verb, held, session))


def clear(d):
    """Delete the durable directory whole; True where there was one."""
    if not os.path.lexists(d):
        return False
    if os.path.isdir(d) and not os.path.islink(d):
        shutil.rmtree(d)
    else:
        os.unlink(d)
    return True


def format2(d):
    v = d.get("format")
    return isinstance(v, int) and not isinstance(v, bool) and v == 2


class locked(object):
    """An exclusive flock on the lock file beside the run-state file, for one read-modify-write."""

    def __init__(self, f):
        self.path = os.path.join(os.path.dirname(f), LOCK)
        self.fd = None

    def __enter__(self):
        if fcntl is not None:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
            fcntl.flock(self.fd, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)
        return False


def require(f):
    """The file is there: missing is 1, unreachable (any other OSError, or not a regular file) is 4."""
    try:
        st = os.stat(f)
    except FileNotFoundError:
        raise Fail(1, "no run-state file at %s" % f)
    except OSError as e:
        raise Fail(4, "cannot reach the run-state file at %s: %s" % (f, e))
    if not stat.S_ISREG(st.st_mode):
        raise Fail(4, "%s is not a regular file" % f)


def load(f):
    require(f)
    with open(f, encoding="utf-8") as r:
        text = r.read()
    try:
        d = json.loads(text)
    except ValueError as e:
        raise Fail(5, "the run-state file at %s does not parse: %s" % (f, e))
    if not isinstance(d, dict):
        raise Fail(5, "the run-state file at %s is not a JSON object" % f)
    want = dict(KEYS)
    for k in FILLED:  # in memory only: the file changes when a call writes it
        if k not in d:
            d[k] = copy.deepcopy(want[k])
    return d


def save(f, d):
    fd, t = tempfile.mkstemp(dir=os.path.dirname(f), prefix=".implement-run.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as w:
            json.dump(d, w, indent=1, ensure_ascii=False)
            w.write("\n")
        os.replace(t, f)
    except BaseException:
        if os.path.exists(t):
            os.unlink(t)
        raise


def parse(text, what):
    try:
        return json.loads(text)
    except ValueError as e:
        raise Fail(2, "%s does not parse as JSON: %s" % (what, e))


def show(s):
    """A key as the caller typed it, for a message: an argv byte that was not UTF-8 shows as \\xNN."""
    try:
        return s.encode("utf-8", "surrogateescape").decode("utf-8", "backslashreplace")
    except UnicodeError:
        return s.encode("utf-8", "backslashreplace").decode("utf-8")


def type_of(default):
    """The JSON type a default fixes, as (python types, name), or None where any value is taken."""
    if isinstance(default, bool):
        return (bool,), "a boolean"
    if isinstance(default, int):
        return (int,), "an integer"
    for t, name in ((str, "a string"), (list, "a list"), (dict, "an object")):
        if isinstance(default, t):
            return (t,), name
    return None


def typed(name, value, default, wrong):
    """value, or note in `wrong` that it is not of the type default fixes."""
    t = type_of(default)
    if t and (not isinstance(value, t[0]) or (t[0] == (int,) and isinstance(value, bool))):
        wrong.append("%s must be %s" % (show(name), t[1]))
    return value


def refuse(what, extra, wrong, own=()):
    """Exit 3 naming every key or member KEYS lacks, every wrong type and every script-owned key
    written at once, where there is any."""
    if extra or wrong or own:
        raise Fail(3, "%s %s" % (what, "; ".join(
            x for x in ("holds unknown " + ", ".join(extra) if extra else "",
                        "; ".join(wrong),
                        "writes %s, which the script alone writes" % ", ".join(own) if own else "") if x)))


def owned(todo):
    """The script-owned keys among (key, value) pairs: session, started, updated and durable, a path
    into one, and tree.snapshot -- dotted, or as a member of an object given for tree."""
    out = []
    for key, v in todo:
        parts = key.split(".")
        if parts[0] in OWNED or parts[:2] == ["tree", "snapshot"]:
            out.append(show(key))
        elif key == "tree" and isinstance(v, dict) and "snapshot" in v:
            out.append("tree.snapshot")
    return out


def merged(d):
    """The init object over KEYS' defaults: each key or member it omits takes its default. Exits 3 on a
    key or member KEYS lacks, one given with the wrong type, or a script-owned one, before anything is
    written."""
    want = dict(KEYS)
    extra = [show(k) for k in d if k not in want]
    wrong = []
    out = {}
    for k, default in KEYS:
        if k not in d:
            out[k] = copy.deepcopy(default)
            continue
        v = typed(k, d[k], default, wrong)
        if isinstance(default, dict) and isinstance(v, dict):
            extra += ["%s.%s" % (k, show(m)) for m in v if m not in default]
            v = dict((m, typed("%s.%s" % (k, m), v[m], md, wrong) if m in v else copy.deepcopy(md))
                     for m, md in default.items())
        out[k] = v
    refuse("init: the object", extra, wrong, owned(list(d.items())))
    return out


def checked(todo, what="set: the call"):
    """set's pairs held to KEYS as init's object is: exits 3 on a key or member KEYS lacks, a top-level
    key or an object key's <key>.<member> given a value of another type than its default fixes, or a
    script-owned key -- every slip in the call named at once, before anything is written. A deeper
    path or a list entry is not checked."""
    want = dict(KEYS)
    extra, wrong = [], []
    for key, v in todo:
        parts = key.split(".")
        if parts[0] not in want:
            extra.append(show(key))
            continue
        default = want[parts[0]]
        if len(parts) == 1:
            typed(key, v, default, wrong)
            if isinstance(default, dict) and isinstance(v, dict):
                for m in v:
                    if m in default:
                        typed("%s.%s" % (key, m), v[m], default[m], wrong)
                    else:
                        extra.append("%s.%s" % (show(key), show(m)))
        elif len(parts) == 2 and isinstance(default, dict):
            if parts[1] in default:
                typed(key, v, default[parts[1]], wrong)
            else:
                extra.append(show(key))
    refuse(what, extra, wrong, owned(todo))


def resolve(d, key):
    """(container, final key) for a dotted key the file holds."""
    parts = key.split(".")
    o = d
    for i, u in enumerate(parts):
        last = i == len(parts) - 1
        here = ".".join(parts[:i + 1])
        if isinstance(o, list):
            try:
                idx = int(u)
                o[idx]
            except (ValueError, IndexError):
                raise Fail(2, "%s: no list entry %s" % (show(key), show(u)))
            if last:
                return o, idx
            o = o[idx]
        elif isinstance(o, dict):
            if u not in o:
                raise Fail(3, "%s: the run-state file holds no key %s" % (show(key), show(here)))
            if last:
                return o, u
            o = o[u]
        else:
            raise Fail(2, "%s: %s is %s -- write that key whole" % (show(key), show(".".join(parts[:i])),
                                                                     json.dumps(o)))
        if o is None:
            raise Fail(2, "%s: %s is null -- write that key whole" % (show(key), show(here)))


def absolute(d, key):
    """A dotted key the file holds, each list index in it written as its absolute index (-1 the last
    entry's); resolve's exits where the file does not hold it."""
    resolve(d, key)
    o, out = d, []
    for u in key.split("."):
        if isinstance(o, list):
            i = int(u)
            i = i + len(o) if i < 0 else i
            out.append(str(i))
            o = o[i]
        else:
            out.append(u)
            o = o[u]
    return ".".join(out)


PAIRS =("takes <key> '<json>' [<key> '<json>' ...], the key written again before each value, "
         "as in: append assumptions '\"a\"' assumptions '\"b\"'")


def pairs(args, stdin, verb):
    if args:
        if len(args) % 2:
            raise Fail(2, "%s: an odd number of arguments -- %s %s" % (verb, verb, PAIRS))
        for i in range(0, len(args), 2):
            if args[i][:1] in ('"', "[", "{"):
                raise Fail(2, "%s: %s is a JSON value where a key belongs -- %s %s"
                           % (verb, show(args[i]), verb, PAIRS))
        return [(args[i], parse(args[i + 1], "the value for %s" % show(args[i])))
                for i in range(0, len(args), 2)]
    obj = parse(stdin.read(), "stdin")
    if not isinstance(obj, dict) or not obj:
        raise Fail(2, "%s with no pairs reads a non-empty JSON object of key: value on stdin" % verb)
    return list(obj.items())


def emit(out, value):
    out.write((json.dumps(value, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))


def read_tombstone(f):
    """The tombstone's object, or None where there is none or it does not parse."""
    try:
        with open(tombstone_path(f), encoding="utf-8") as r:
            t = json.load(r)
    except FileNotFoundError:
        return None
    except ValueError:
        return None
    return t if isinstance(t, dict) else None


def cmd_init(f, args, stdin, out, session):
    if args == ["--resume"]:
        return cmd_resume(f, stdin, out, session)
    if args not in ([], ["--recover"]):
        raise Fail(2, "init takes only --recover or --resume")
    recover = args == ["--recover"]
    d = parse(stdin.read(), "stdin")
    if not isinstance(d, dict) or d.get("format", 2) != 2:
        raise Fail(2, "init reads a JSON object on stdin, its format 2 where it gives one")
    d = merged(d)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    dd = durable_dir(f)
    removed_dir = False
    with locked(f):
        if recover:
            t = read_tombstone(f)
            if t is not None and t.get("session") is not None and session is not None \
                    and t.get("session") != session:
                raise Fail(9, "init --recover: session %s finished this run at %s and removed its state (%s); "
                              "nothing written" % (t.get("session"), t.get("at"), tombstone_path(f)))
            try:
                old = load(f)
            except (Fail, OSError, ValueError):  # missing, unreadable or unparseable: no session to compare
                old = None
            if old is not None:
                guard(old, session, "init --recover")
        held = False
        if not recover:  # before the file is moved aside, so a failure here leaves it where it was
            held = os.path.isdir(dd) and not os.path.islink(dd) and bool(os.listdir(dd))
            removed_dir = clear(dd)
            if os.path.lexists(tombstone_path(f)):
                os.unlink(tombstone_path(f))
        s = None
        if os.path.lexists(f):
            here = os.path.dirname(f)
            for name in os.listdir(here):
                old = os.path.join(here, name)
                if STALE_RE.match(name) and os.path.isfile(old) and not os.path.islink(old):
                    os.unlink(old)
            s = "%s.stale-%s" % (f, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
            os.replace(f, s)
            out.write(("moved aside: %s\n" % s).encode("utf-8"))
        if recover:
            d["assumptions"].append(
                "This run's run-state file could not be read back, and was written again from what the run "
                "still held: " + ("the file there, none of it carried over, was moved aside as %s" % s if s else
                                  "no file was there, so none was moved aside"))
        elif s:
            d["assumptions"].append("Run-state file an earlier run left, not resumed, moved aside%s: %s"
                                    % (" and its durable copies deleted" if held else "", s))
        d["session"] = session
        d["started"] = d["updated"] = now()
        save(f, d)
    if removed_dir:
        out.write(("removed: %s\n" % dd).encode("utf-8"))
    out.write(("created: %s\n" % f).encode("utf-8"))


def append_to(d, key, v, verb):
    """Append v to the list at key; a null key becomes a one-element list."""
    o, k = resolve(d, key)
    if o[k] is None:
        o[k] = [v]
    elif isinstance(o[k], list):
        o[k].append(v)
    else:
        raise Fail(2, "%s: %s is not a list or null" % (verb, show(key)))


def resumable(f):
    """The file, loaded: exit 1 with none, 5 where it does not parse, 8 where its format is not 2."""
    d = load(f)
    if not format2(d):
        raise Fail(8, "the run-state file at %s is format %s, not 2 -- no resume takes it"
                   % (f, json.dumps(d.get("format"))))
    return d


def cmd_resume(f, stdin, out, session):
    resumable(f)  # the file first: no file exits 1 whatever stdin holds
    given = parse(stdin.read(), "stdin")
    if not isinstance(given, dict):
        raise Fail(2, "init --resume reads a JSON object on stdin, holding only %s" % ", ".join(RESUME_KEYS))
    refuse("init --resume: the object", [show(k) for k in given if k not in RESUME_KEYS], [])
    checked(list(given.items()), "init --resume: the object")
    want = dict(KEYS)
    lines, originals = [], []
    with locked(f):
        d = resumable(f)
        was, stopped = d.get("session"), d.get("updated")
        for key, v in given.items():
            if key in RESUME_APPENDED:
                for x in v:
                    append_to(d, key, x, "init --resume")
                continue
            o, k = resolve(d, key)
            if isinstance(want.get(key), dict) and isinstance(v, dict) and isinstance(o[k], dict):
                o[k] = dict(o[k])
                o[k].update(v)
            else:
                o[k] = v
        durable = d.get("durable") if isinstance(d.get("durable"), dict) else {}
        for kp, p in walk(d):
            if not isinstance(p, str) or os.path.isfile(p):
                continue
            o, k = resolve(d, kp)
            e = durable.get(kp)
            if (isinstance(e, dict) and same(e.get("of"), p) and isinstance(e.get("copy"), str)
                    and os.path.isfile(e["copy"])):
                o[k] = e["copy"]
                lines.append("repointed: %s: %s -> %s" % (kp, p, e["copy"]))
                if (os.path.basename(p).startswith(TEMP_PREFIX) and os.path.lexists(p)
                        and not os.path.isdir(p) and not any(same(p, q) for q in originals)):
                    originals.append(p)
            else:
                o[k] = None
                lines.append("cleared: %s: %s" % (kp, p))
        step = d.get("step")
        append_to(d, "assumptions", "Resumed at %s%s after session %s stopped at %s" % (
            d.get("phase"), "" if step is None else " step %s" % step,
            "unknown" if was is None else was, "unknown" if stopped is None else stopped), "init --resume")
        d["session"] = session
        d["updated"] = now()
        save(f, d)
        for p in originals:
            try:
                os.unlink(p)
                lines.append("removed: %s" % p)
            except OSError as e:
                lines.append("left: %s -- %s" % (p, e))
    for line in lines:
        out.write((line + "\n").encode("utf-8"))
    out.write(("resumed: %s\n" % f).encode("utf-8"))


def cmd_peek(f, args, out):
    if args:
        raise Fail(2, "peek takes no argument")
    emit(out, resumable(f))


def cmd_open(f, args, out, session):
    if len(args) != 1:
        raise Fail(2, "open takes the phase's name, as its heading names it")
    require(f)
    with locked(f):
        d = load(f)
        guard(d, session, "open")
        d["phase"] = args[0]
        d["step"] = None
        d["updated"] = now()
        save(f, d)
    emit(out, d)


def cmd_read(f, args, out):
    d = load(f)
    if not args:
        emit(out, d)
    elif len(args) == 1:
        o, k = resolve(d, args[0])
        emit(out, o[k])
    else:
        raise Fail(2, "read takes at most one key")


def walk(d):
    """Each path location the file holds, as (key path, value), whatever the value: every `files`
    member, each `step_groups` entry's report, each `reviews` entry's diff and return file and each
    `patches` entry's path, in that order, then `lineage.check_file` -- a list entry by its absolute
    index, each where its container holds it."""
    out = []
    files = d.get("files")
    if isinstance(files, dict):
        out += [("files.%s" % m, v) for m, v in files.items()]
    for name, members in (("step_groups", ("report",)), ("reviews", ("diff_file", "return_file")),
                          ("patches", ("path",))):
        entries = d.get(name)
        for i, e in enumerate(entries if isinstance(entries, list) else []):
            if isinstance(e, dict):
                out += [("%s.%d.%s" % (name, i, m), e[m]) for m in members if m in e]
    lineage = d.get("lineage")
    if isinstance(lineage, dict) and "check_file" in lineage:
        out.append(("lineage.check_file", lineage["check_file"]))
    return out


def named(d):
    """Each path the file names that a set may stop naming: every `files` member's, each `step_groups`
    entry's report, each `reviews` entry's diff and return file and each `patches` entry's path, in that
    order, each once -- walk()'s locations but `lineage.check_file`."""
    seen, once = set(), []
    for k, p in walk(d):
        if k != "lineage.check_file" and isinstance(p, str) and os.path.abspath(p) not in seen:
            seen.add(os.path.abspath(p))
            once.append(p)
    return once


def copies_named(d):
    """Every path a path location, tree.snapshot or a durable entry's copy names."""
    out = set(os.path.abspath(p) for _, p in walk(d) if isinstance(p, str))
    tree = d.get("tree")
    if isinstance(tree, dict) and isinstance(tree.get("snapshot"), str):
        out.add(os.path.abspath(tree["snapshot"]))
    durable = d.get("durable")
    for e in durable.values() if isinstance(durable, dict) else []:
        if isinstance(e, dict) and isinstance(e.get("copy"), str):
            out.add(os.path.abspath(e["copy"]))
    return out


def drop(d):
    """Drop each durable entry whose label is a key path that names neither its `of` nor its copy any
    more -- never a note: entry or the tree.snapshot entry -- and return the dropped copies no path
    location and no other entry still names, to delete once the write lands."""
    durable = d.get("durable")
    if not isinstance(durable, dict):
        return []
    gone = []
    for label in list(durable):
        if label.startswith(NOTE) or label == "tree.snapshot":
            continue
        e = durable[label]
        try:
            o, k = resolve(d, label)
            v = o[k]
        except Fail:
            v = None
        if isinstance(e, dict) and (same(v, e.get("of")) or same(v, e.get("copy"))):
            continue
        del durable[label]
        if isinstance(e, dict) and isinstance(e.get("copy"), str):
            gone.append(e["copy"])
    still = copies_named(d)
    return [c for c in gone if os.path.abspath(c) not in still]


def unlink_each(paths, out):
    for p in paths:
        try:
            os.unlink(p)
            out.write(("removed: %s\n" % p).encode("utf-8"))
        except FileNotFoundError:
            pass
        except OSError as e:
            out.write(("left: %s -- %s\n" % (p, e)).encode("utf-8"))


def cmd_set(f, args, stdin, out, session):
    todo = pairs(args, stdin, "set")
    checked(todo)
    require(f)
    want = dict(KEYS)
    dd = durable_dir(f)
    with locked(f):
        d = load(f)
        guard(d, session, "set")
        before = named(d)
        for key, v in todo:
            o, k = resolve(d, key)
            if isinstance(want.get(key), dict) and isinstance(v, dict) and isinstance(o[k], dict):
                o[k] = dict(o[k])
                o[k].update(v)
            else:
                o[k] = v
        gone = drop(d)
        d["updated"] = now()
        save(f, d)
        after = set(os.path.abspath(p) for p in named(d))
        for p in before:
            a = os.path.abspath(p)
            if (a in after or not os.path.basename(a).startswith(TEMP_PREFIX) or not os.path.isfile(a)
                    or os.path.islink(a) or inside(a, dd)):
                continue
            try:
                os.unlink(a)
                out.write(("removed: %s\n" % p).encode("utf-8"))
            except OSError as e:
                out.write(("left: %s -- %s\n" % (p, e)).encode("utf-8"))
        unlink_each([c for c in gone if inside(c, dd)], out)


def cmd_append(f, args, stdin, session):
    todo = pairs(args, stdin, "append")
    lists = [show(key) for key, v in todo if isinstance(v, list)]
    if lists:
        raise Fail(2, "append: the value for %s is a JSON array, which append would add as one entry -- "
                   "give one value per pair (append %s '<a>' %s '<b>'), or write the whole list with "
                   "set %s '<json>'" % (", ".join(lists), lists[0], lists[0], lists[0]))
    refuse("append: the call", [], [], owned(todo))
    require(f)
    with locked(f):
        d = load(f)
        guard(d, session, "append")
        stamp = now()
        for key, v in todo:
            if key == "step_groups" and isinstance(v, dict):
                v = dict(v, started=stamp)
            append_to(d, key, v, "append")
        d["updated"] = stamp
        save(f, d)


def copy_name(label):
    """The copy file name a label has in the durable directory: the label made safe, then a hash of it,
    so two labels never share one. It never begins `dw-impl-`, so no temp-file removal takes it."""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", label).strip("._-")[:60] or "copy"
    return "%s-%s" % (safe, hashlib.sha256(label.encode("utf-8")).hexdigest()[:12])


def named_elsewhere(d, label):
    """Every path a location other than the label's own key names: each other path location,
    tree.snapshot unless it is the label, and each other durable entry's copy."""
    out = set(os.path.abspath(p) for k, p in walk(d) if k != label and isinstance(p, str))
    tree = d.get("tree")
    if label != "tree.snapshot" and isinstance(tree, dict) and isinstance(tree.get("snapshot"), str):
        out.add(os.path.abspath(tree["snapshot"]))
    durable = d.get("durable")
    for other, e in durable.items() if isinstance(durable, dict) else []:
        if other != label and isinstance(e, dict) and isinstance(e.get("copy"), str):
            out.add(os.path.abspath(e["copy"]))
    return out


def cmd_persist(f, args, out, session):
    if len(args) != 2:
        raise Fail(2, "persist takes <label> <file>: a key path, or note:<path>, then the file to copy")
    label, src = args
    try:
        label.encode("utf-8")
        src.encode("utf-8")
    except UnicodeError:
        raise Fail(2, "persist: the label or the file is not UTF-8")
    note = label.startswith(NOTE)
    if note and label == NOTE:
        raise Fail(2, "persist: note: takes the note's path, as note:<path>")
    if not os.path.isfile(src):
        raise Fail(2, "persist: %s is no file to copy" % show(src))
    require(f)
    dd = durable_dir(f)
    with locked(f):
        d = load(f)
        guard(d, session, "persist")
        durable = d.get("durable")
        if not isinstance(durable, dict):
            raise Fail(3, "persist: the run-state file holds no durable object")
        if not note:
            label = absolute(d, label)
            if label != "tree.snapshot" and label not in dict(walk(d)):
                raise Fail(3, "persist: %s names no path location -- a files member, a step_groups report, a "
                              "reviews diff or return file, a patches path, lineage.check_file or tree.snapshot"
                           % show(label))
        os.makedirs(dd, exist_ok=True)
        base = copy_name(label)
        target, elsewhere, n = os.path.join(dd, base), named_elsewhere(d, label), 0
        while os.path.abspath(target) in elsewhere:  # never overwrite a copy another location reads
            n += 1
            target = os.path.join(dd, "%s-%d" % (base, n))
        try:
            r = open(src, "rb")
        except OSError as e:
            raise Fail(2, "persist: cannot read %s: %s" % (show(src), e))
        fd, t = tempfile.mkstemp(dir=dd, prefix=".persist.")
        try:
            with r, os.fdopen(fd, "wb") as w:
                shutil.copyfileobj(r, w)
            os.replace(t, target)
        except BaseException:
            if os.path.exists(t):
                os.unlink(t)
            raise
        old = durable.get(label)
        durable[label] = {"copy": target, "of": src}
        if label == "tree.snapshot":
            d["tree"]["snapshot"] = target
        d["updated"] = now()
        save(f, d)
        if (isinstance(old, dict) and isinstance(old.get("copy"), str) and old["copy"] != target
                and inside(old["copy"], dd) and os.path.abspath(old["copy"]) not in copies_named(d)):
            try:  # silent: persist prints the copy's path alone
                os.unlink(old["copy"])
            except OSError:
                pass
    out.write(("%s\n" % target).encode("utf-8"))


def cmd_remove(f, args, out, session):
    keep = set()
    i = 0
    while i < len(args):
        if args[i] == "--keep" and i + 1 < len(args):
            keep.add(os.path.abspath(args[i + 1]))
            i += 2
        else:
            raise Fail(2, "remove takes only --keep <path> options")
    if not guarded(f):
        raise Fail(4, "refusing to remove %s: not the run-state file's path" % f)
    dd = durable_dir(f)
    if not there(f) and not os.path.lexists(dd):  # nothing to remove: no lock made, nothing created
        out.write(("no run-state file at %s -- nothing else to remove\n" % f).encode("utf-8"))
        return
    removed_file = False
    with locked(f):
        # the file tested again under the lock: one another call wrote while this one waited is guarded
        if there(f):
            removed_file = True
            remove_file(f, dd, keep, out, session)
        rescue(keep, f, dd, out)
        removed_dir = clear(dd)
    if removed_dir:
        out.write(("removed: %s\n" % dd).encode("utf-8"))
    if removed_file:
        out.write(("removed: %s\n" % f).encode("utf-8"))
    else:
        out.write(("no run-state file at %s -- nothing else to remove\n" % f).encode("utf-8"))


def there(f):
    """True where something is at the file's path; 4 where it cannot be reached."""
    try:
        os.lstat(f)
        return True
    except FileNotFoundError:
        return False
    except OSError as e:
        raise Fail(4, "cannot reach the run-state file at %s: %s" % (f, e))


def remove_file(f, dd, keep, out, session):
    """Under the lock: the guard, the temp files the file names, then the file, leaving the tombstone."""
    try:
        d = load(f)
    except Fail:
        d = {}
    guard(d, session, "remove")
    paths = []
    files = d.get("files")
    if isinstance(files, dict):
        paths += [p for p in files.values() if isinstance(p, str)]
    for g in d.get("step_groups") or []:
        if isinstance(g, dict) and isinstance(g.get("report"), str):
            paths.append(g["report"])
    for v in d.get("reviews") or []:
        if isinstance(v, dict):
            paths += [v[k] for k in ("diff_file", "return_file") if isinstance(v.get(k), str)]
    for p in d.get("patches") or []:
        if isinstance(p, dict) and p.get("temp") is True and isinstance(p.get("path"), str):
            paths.append(p["path"])
    lineage = d.get("lineage")
    if isinstance(lineage, dict) and isinstance(lineage.get("check_file"), str):
        paths.append(lineage["check_file"])
    for p in paths:
        a = os.path.abspath(p)
        if inside(a, dd):
            continue  # the durable directory goes whole once cmd_remove has moved a --keep path in it out
        if a in keep:
            out.write(("kept: %s\n" % p).encode("utf-8"))
        elif (os.path.basename(a).startswith(TEMP_PREFIX) and os.path.isfile(a)
              and not os.path.islink(a)):
            os.unlink(a)
            out.write(("removed: %s\n" % p).encode("utf-8"))
        elif os.path.lexists(a):
            out.write(("left: %s -- not a %s* temp file\n" % (p, TEMP_PREFIX)).encode("utf-8"))
    held = d.get("session") if isinstance(d, dict) else None
    os.unlink(f)
    save(tombstone_path(f), {"session": session if held is None else held, "at": now()})


def rescue(keep, f, dd, out):
    """Move each --keep path inside the durable directory out beside the file, as
    implement-run.kept-<its name>, before the directory goes, printing `kept: <that path>`."""
    for a in sorted(keep):
        if inside(a, dd) and os.path.lexists(a) and not os.path.isdir(a):
            moved = os.path.join(os.path.dirname(f), "implement-run.kept-" + os.path.basename(a))
            os.replace(a, moved)
            out.write(("kept: %s\n" % moved).encode("utf-8"))


VERBS = ("init", "open", "read", "peek", "set", "append", "persist", "remove")


def run(argv, stdin, out, repo=".", session=None):
    """One call; session is the caller's CLAUDE_CODE_SESSION_ID, None where it has none."""
    if argv[:1] == ["--repo"]:
        if len(argv) < 2:
            raise Fail(2, "--repo takes a directory")
        repo, argv = argv[1], argv[2:]
    if not argv:
        raise Fail(2, "usage: run-state.py [--repo <dir>] %s ..." % "|".join(VERBS))
    verb, args = argv[0], argv[1:]
    if verb not in VERBS:
        raise Fail(2, "unknown subcommand %s" % verb)
    f = state_path(repo)
    try:
        if verb == "init":
            cmd_init(f, args, stdin, out, session)
        elif verb == "open":
            cmd_open(f, args, out, session)
        elif verb == "read":
            cmd_read(f, args, out)
        elif verb == "peek":
            cmd_peek(f, args, out)
        elif verb == "set":
            cmd_set(f, args, stdin, out, session)
        elif verb == "append":
            cmd_append(f, args, stdin, session)
        elif verb == "persist":
            cmd_persist(f, args, out, session)
        else:
            cmd_remove(f, args, out, session)
    except OSError as e:
        raise Fail(4, "%s: %s" % (f, e))


def utf8_argv(argv):
    """argv as UTF-8 whatever the locale: undo a locale decode back to bytes, then decode as UTF-8."""
    return [os.fsencode(a).decode("utf-8", "surrogateescape") for a in argv]


def selftest():
    import io
    failures = []
    checks = [0]

    def check(name, cond):
        checks[0] += 1
        if not cond:
            failures.append(name)

    said = [""]  # the last call's error message, "" where it succeeded

    def call(argv, stdin="", repo=None, session=None):
        # the session is passed, never read from the environment
        out = io.BytesIO()
        said[0] = ""
        try:
            run((["--repo", repo] if repo else []) + argv, io.StringIO(stdin), out, session=session)
            code = 0
        except Fail as e:
            code = e.code
            said[0] = str(e)
        return code, out.getvalue().decode("utf-8")

    def fresh(**over):
        # only what a caller holds: init gives every other key its default
        d = {"format": 2, "assumptions": ["seeded"]}
        d.update(over)
        return d

    def clean_env(**over):
        # a child's environment with no session in it, so main() writes as a null session unless told
        env = dict(os.environ)
        env.pop("CLAUDE_CODE_SESSION_ID", None)
        env.update(over)
        return env

    me = os.path.abspath(__file__)
    impl = os.path.join(os.path.dirname(os.path.dirname(me)), "commands", "implement.md")
    if os.path.isfile(impl):
        quoted = re.findall(r"which `run-state\.py`'s `KEYS` defines, and no other: `([^`]+)`",
                            open(impl, encoding="utf-8").read())
        check("implement.md quotes KEYS exactly", quoted == [KEYS_LINE])

    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "r [x] q")
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify",
                        "--allow-empty", "-m", "x"], check=True)
        f = state_path(repo)
        here = os.path.dirname(f)
        check("path is the git path", f.endswith(os.path.join(".git", "dev-workflows", "implement-run.json")))

        check("open with no file exits 1", call(["open", "Phase 1.5"], repo=repo)[0] == 1)
        code, out = call(["init"], json.dumps(fresh()), repo)
        check("init creates", code == 0 and os.path.isfile(f) and "moved aside" not in out)
        d = json.load(open(f, encoding="utf-8"))
        check("init keeps the seeded assumptions", d["assumptions"] == ["seeded"])
        check("init holds every key in KEYS, and no other", list(d) == [k for k, _ in KEYS])
        check("init gives an omitted key its default", d["deferred"] == [] and d["step_groups"] == []
              and d["clean_finish"] is True and d["replans_used"] == 0 and d["phase"] == "Phase 1.4"
              and d["session_branch_lift"] is False and d["test_decision"] is None)
        check("init gives an omitted object its members' defaults",
              d["files"] == dict((m, None) for m in dict(KEYS)["files"])
              and d["report"] == {"commands_run": [], "maintenance": [], "notices": [], "phase1_tasks": [],
                                  "confirmed_cause": None})
        check("init defaults pieces and reviews to empty lists", d["pieces"] == [] and d["reviews"] == [])
        check("init defaults check_run_answers to an empty list", d.get("check_run_answers") == [])
        cra = {"path": "core dump.log", "answer": "Commit them with the change"}
        code, _ = call(["append", "check_run_answers", json.dumps(cra)], repo=repo)
        check("append records a check run's answer for a later stop", code == 0
              and json.load(open(f, encoding="utf-8")).get("check_run_answers") == [cra])
        pe = {"name": "p", "files": ["a.py"], "contract": ["c"]}
        re_ = {"round": "first", "scope": "piece:p", "paths": ["a.py"], "diff_file": None,
               "return_file": None, "verdict": None}
        code, _ = call(["init"], json.dumps(fresh(pieces=[pe], reviews=[re_])), repo)
        d2 = json.load(open(f, encoding="utf-8"))
        check("init accepts a pieces entry and a reviews entry", code == 0 and d2["pieces"] == [pe]
              and d2["reviews"] == [re_])
        check("init refuses pieces given as a string", call(["init"], json.dumps(fresh(pieces="x")), repo)[0] == 3)
        check("init refuses a non-object", call(["init"], "[1]", repo)[0] == 2)
        check("init refuses a format other than 2", call(["init"], json.dumps(fresh(format=1)), repo)[0] == 2)

        # a nested member default: a given object keeps its members and takes the rest's defaults
        task_x = os.path.join(tmp, "dw-impl-task-x")
        code, _ = call(["init"], json.dumps(fresh(files={"task_description_file": task_x},
                                                  report={"phase1_tasks": ["t"]})), repo)
        d = json.load(open(f, encoding="utf-8"))
        check("init gives an omitted member its default", code == 0
              and d["files"]["task_description_file"] == task_x and d["files"]["plan_file"] is None
              and d["report"]["phase1_tasks"] == ["t"] and d["report"]["notices"] == []
              and d["report"]["confirmed_cause"] is None)

        # init validates before it moves anything aside: an unknown key or member, or a wrong type, exits 3
        before = sorted(os.listdir(here))
        code, _ = call(["init"], json.dumps(fresh(defered=[])), repo)
        check("init refuses an unknown key, moving nothing", code == 3 and sorted(os.listdir(here)) == before)
        check("init refuses an unknown member", call(["init"], json.dumps(fresh(files={"plan": "x"})), repo)[0] == 3)
        code, _ = call(["init"], json.dumps(fresh(deferred="x")), repo)
        check("init refuses a list given as a string, moving nothing", code == 3
              and sorted(os.listdir(here)) == before)
        check("init refuses an object given as a list", call(["init"], json.dumps(fresh(files=[])), repo)[0] == 3)
        check("init refuses a member of the wrong type",
              call(["init"], json.dumps(fresh(clarifications={"settled": "x"})), repo)[0] == 3)
        check("init refuses a boolean given as a string",
              call(["init"], json.dumps(fresh(clean_finish="true")), repo)[0] == 3)
        check("init refuses an integer given as a boolean",
              call(["init"], json.dumps(fresh(replans_used=True)), repo)[0] == 3)
        check("init takes any value where the default is null",
              call(["init"], json.dumps(fresh(run_flags={"skip_costs": False}, mode="direct")), repo)[0] == 0)

        # stale move-aside: at most one kept, and an unrelated name left alone
        open(os.path.join(here, "implement-run.json.stale-notes.txt"), "w").close()
        olds = ("implement-run.json.stale-20200101T000000Z", "implement-run.json.stale-20210101T000000Z")
        for old in olds:
            open(os.path.join(here, old), "w").close()
        code, out = call(["init"], json.dumps(fresh()), repo)
        stale = sorted(n for n in os.listdir(here) if STALE_RE.match(n))
        check("init moves the file aside", code == 0 and "moved aside: " in out)
        check("one stale file kept, the older ones removed", len(stale) == 1 and stale[0] not in olds)
        check("unrelated stale-named file left", os.path.exists(os.path.join(here, "implement-run.json.stale-notes.txt")))
        a = json.load(open(f, encoding="utf-8"))["assumptions"]
        check("move-aside named once, as an earlier run's, not resumed", len(a) == 2 and a[0] == "seeded"
              and a[1] == "Run-state file an earlier run left, not resumed, moved aside: %s"
              % os.path.join(here, stale[0]))

        # an unparseable file: its own code, and --recover names it as this run's own
        with open(f, "w", encoding="utf-8") as w:
            w.write("{broken")
        check("an unparseable file exits 5", call(["open", "Phase 2A"], repo=repo)[0] == 5)
        code, out = call(["init", "--recover"], json.dumps(fresh()), repo)
        a = json.load(open(f, encoding="utf-8"))["assumptions"]
        moved = [n for n in os.listdir(here) if STALE_RE.match(n)]
        check("--recover names this run's own file", code == 0 and "This run's run-state file" in a[-1]
              and "earlier run" not in a[-1])
        check("--recover names the file it moved aside", len(a) == 2 and len(moved) == 1
              and "none of it carried over, was moved aside as" in a[-1] and a[-1].endswith(moved[0]))

        # open sets phase and prints
        code, out = call(["open", "Phase 1.5"], repo=repo)
        check("open sets phase", code == 0 and json.loads(out)["phase"] == "Phase 1.5"
              and json.load(open(f, encoding="utf-8"))["phase"] == "Phase 1.5")

        # non-ASCII and a path holding " and \ round-trip; the file and the printed output unescaped
        weird = 'dir/ünï cöde "q" b\\c\tt.txt'
        entry = [{"path": weird, "fingerprint": "abc", "status": "??"}]
        code, _ = call(["set", "pre_existing_dirty", json.dumps(entry, ensure_ascii=False)], repo=repo)
        raw = open(f, encoding="utf-8").read()
        check("non-ASCII written as itself", code == 0 and "ünï cöde" in raw and "\\u00fc" not in raw)
        check("quote, backslash and tab escaped in the file", '\\"q\\" b\\\\c\\tt' in raw)
        code, out = call(["read", "pre_existing_dirty"], repo=repo)
        check("read prints non-ASCII unescaped", code == 0 and "ünï cöde" in out and "\\u00fc" not in out)
        check("path reads back unchanged", json.loads(out)[0]["path"] == weird)
        code, out = call(["open", "Phase 1.6"], repo=repo)
        check("open prints non-ASCII unescaped", code == 0 and "ünï cöde" in out and "\\u00fc" not in out)

        # multi-key set: argv pairs and a stdin object, dotted keys
        plan_x = os.path.join(tmp, "dw-impl-plan-x")
        code, _ = call(["set", "class", '"SIGNIFICANT"', "files.plan_file", json.dumps(plan_x)], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set takes several pairs", code == 0 and d["class"] == "SIGNIFICANT"
              and d["files"]["plan_file"] == plan_x)
        code, _ = call(["set"], json.dumps({"routing": {"block": {"classification": "HIGH-RISK"}, "history": ["a"]},
                                             "class": "HIGH-RISK", "coding_model": "m"}), repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set takes a stdin object", code == 0 and d["class"] == "HIGH-RISK" and d["coding_model"] == "m"
              and d["routing"]["history"] == ["a"])
        check("set refuses a path through null", call(["set", "test_decision.command_hint", '"x"'], repo=repo)[0] == 2)
        before = open(f, encoding="utf-8").read()
        check("a bad value changes nothing", call(["set", "class", "not json"], repo=repo)[0] == 2
              and open(f, encoding="utf-8").read() == before)
        check("an odd pair list is refused", call(["set", "class"], repo=repo)[0] == 2)
        code, _ = call(["set", "clas", '"x"', "class", '"SIMPLE"'], repo=repo)
        check("set refuses an unknown key, changing nothing", code == 3
              and json.load(open(f, encoding="utf-8"))["class"] == "HIGH-RISK")
        check("set refuses an unknown member", call(["set", "files.plan", '"x"'], repo=repo)[0] == 3)

        # session_branch_created: null until a session-branch commit this run makes prints
        # created: true, then the <base short sha> specs-repo-git §8.2 says to carry, read for §6's line
        d = json.load(open(f, encoding="utf-8"))
        check("session_branch_created defaults to null", "session_branch_created" in d
              and d["session_branch_created"] is None)
        code, _ = call(["set", "session_branch_created", '"abc1234"'], repo=repo)
        rcode, out = call(["read", "session_branch_created"], repo=repo)
        check("session_branch_created is set and read back", code == 0 and rcode == 0
              and json.loads(out) == "abc1234"
              and json.load(open(f, encoding="utf-8"))["session_branch_created"] == "abc1234")

        # append: onto a list, onto null, into a list entry; an unknown key refused
        code, _ = call(["append", "deferred", '"one"', "deferred", '"two"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("append onto a list", code == 0 and d["deferred"] == ["one", "two"])
        code, _ = call(["append", "defered", '"three"'], repo=repo)
        check("append refuses a missing key", code == 3
              and json.load(open(f, encoding="utf-8"))["deferred"] == ["one", "two"])
        code, _ = call(["append", "code_repo_outcome", '"line"'], repo=repo)
        check("append onto null makes a one-element list", code == 0
              and json.load(open(f, encoding="utf-8"))["code_repo_outcome"] == ["line"])
        call(["append", "triage", json.dumps({"pass": "first", "followed_by": None})], repo=repo)
        code, _ = call(["append", "triage.-1.followed_by", '"review-fixer pass"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("append into the last list entry", code == 0 and d["triage"][-1]["followed_by"] == ["review-fixer pass"])
        check("append refuses a non-list", call(["append", "class", '"x"'], repo=repo)[0] == 2)
        # an array value is refused, never taken as one entry: argv and the stdin object alike
        two = [{"pass": "a", "followed_by": None}, {"pass": "b", "followed_by": None}]
        before = open(f, encoding="utf-8").read()
        code, _ = call(["append", "triage", json.dumps(two)], repo=repo)
        check("append refuses an array value, naming set and one value per pair, writing nothing", code == 2
              and "set triage" in said[0] and "one value per pair" in said[0]
              and open(f, encoding="utf-8").read() == before)
        code, _ = call(["append"], json.dumps({"triage": two}), repo)
        check("append's stdin object refuses an array value the same way", code == 2
              and "set triage" in said[0] and "one value per pair" in said[0]
              and open(f, encoding="utf-8").read() == before)
        code, _ = call(["append", "deferred", '"d"', "triage", json.dumps(two)], repo=repo)
        check("an array value in a later pair writes neither pair", code == 2
              and open(f, encoding="utf-8").read() == before)
        code, out = call(["read", "triage.0.pass"], repo=repo)
        check("read a list entry's member", code == 0 and json.loads(out) == "first")
        check("read refuses an unknown key", call(["read", "phasee"], repo=repo)[0] == 3)

        # set holds every value to KEYS, as init does: an object key's members merge, a slip changes nothing
        code, _ = call(["set", "files", '{"baseline_file": "x"}'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set merges an object key's members, the rest kept", code == 0 and d["files"]["baseline_file"] == "x"
              and d["files"]["plan_file"] == plan_x and list(d["files"]) == list(dict(KEYS)["files"]))
        call(["set", "files.baseline_file", "null", "deferred", "[]"], repo=repo)
        code, _ = call(["set"], json.dumps({"files": {"baseline_file": "x"}, "deferred": ["d"]}), repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set's stdin object merges the same way", code == 0 and d["files"]["baseline_file"] == "x"
              and d["files"]["plan_file"] == plan_x and d["deferred"] == ["d"])
        before = open(f, encoding="utf-8").read()
        check("set refuses a member the key lacks, writing nothing",
              call(["set", "files", '{"bogus": 1}'], repo=repo)[0] == 3 and open(f, encoding="utf-8").read() == before)
        check("set refuses an object key given a string", call(["set", "files", '"x"'], repo=repo)[0] == 3)
        check("set refuses a boolean given as a string", call(["set", "clean_finish", '"no"'], repo=repo)[0] == 3)
        check("set refuses an integer given as a boolean", call(["set", "replans_used", "true"], repo=repo)[0] == 3)
        check("set refuses a member of the wrong type", call(["set", "spec_context.spec_paths", '"x"'], repo=repo)[0] == 3)
        code, _ = call(["set", "routing.block", '{"anything": 1}'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set takes any value where the default is null", code == 0 and d["routing"]["block"] == {"anything": 1}
              and d["routing"]["history"] == ["a"])
        before = open(f, encoding="utf-8").read()
        code, _ = call(["set", "class", '"MODERATE"', "replans_used", '"1"'], repo=repo)
        check("a wrong type in a later pair writes neither pair", code == 3 and open(f, encoding="utf-8").read() == before)
        code, _ = call(["set", "clean_finish", '"no"', "files.bogus", "1"], repo=repo)
        check("set names every slip in the call at once", code == 3 and "files.bogus" in said[0]
              and "clean_finish must be a boolean" in said[0])

        # the pairs form: the key written again before each value
        before = open(f, encoding="utf-8").read()
        code, _ = call(["append", "assumptions", '"a"', '"b"', '"c"'], repo=repo)
        check("a value where a key belongs exits 2, naming the repeat-the-key form, writing nothing", code == 2
              and "append assumptions '\"a\"' assumptions '\"b\"'" in said[0] and open(f, encoding="utf-8").read() == before)
        code, _ = call(["append", "assumptions", '"a"', '"b"'], repo=repo)
        check("an odd count exits 2, naming the repeat-the-key form", code == 2
              and "append assumptions '\"a\"' assumptions '\"b\"'" in said[0])
        check("a key opening with [ or { exits 2 before any lookup",
              call(["set", "[1]", '"x"'], repo=repo)[0] == 2 and call(["set", '{"class": 1}', '"x"'], repo=repo)[0] == 2)
        code, _ = call(["append", "assumptions", '"a"', "assumptions", '"b"'], repo=repo)
        check("append takes the key again before each value", code == 0
              and json.load(open(f, encoding="utf-8"))["assumptions"][-2:] == ["a", "b"])

        # a temp file a set stops naming is removed: dw-impl-, regular, named by none of the three after it
        def mk(name, where=tmp):
            p = os.path.join(where, name)
            open(p, "w").close()
            return p
        ra, rb = mk("dw-impl-return-a"), mk("dw-impl-return-b")
        call(["set", "files.review_return_file", json.dumps(ra)], repo=repo)
        code, out = call(["set", "files.review_return_file", json.dumps(rb)], repo=repo)
        check("a replaced file is removed, its replacement kept", code == 0 and not os.path.exists(ra)
              and os.path.exists(rb) and "removed: %s" % ra in out)
        pp = mk("dw-impl-plan-p")
        call(["set", "files.pending_plan_file", json.dumps(pp)], repo=repo)
        code, out = call(["set", "files.plan_file", json.dumps(pp), "files.pending_plan_file", "null"], repo=repo)
        check("plan promotion keeps the plan, now plan_file's", code == 0 and os.path.exists(pp) and out == "")
        pq = mk("dw-impl-plan-q")
        call(["set", "files.pending_plan_file", json.dumps(pq)], repo=repo)
        code, out = call(["set", "files.pending_plan_file", "null"], repo=repo)
        check("a file nulled that nothing else names is removed", code == 0 and not os.path.exists(pq)
              and "removed: %s" % pq in out)
        notes = mk("notes-n")
        call(["set", "files.summary_file", json.dumps(notes)], repo=repo)
        code, out = call(["set", "files.summary_file", "null"], repo=repo)
        check("a replaced file not named dw-impl- is left", code == 0 and os.path.exists(notes) and out == "")
        rep = mk("dw-impl-code-r")
        call(["set", "step_groups", json.dumps([{"steps": [1], "report": rep}]), "files.failure_file", json.dumps(rep)],
             repo=repo)
        code, out = call(["set", "files.failure_file", "null"], repo=repo)
        check("a file a step_groups report still names is kept", code == 0 and os.path.exists(rep) and out == "")
        target, link = mk("target-t"), os.path.join(tmp, "dw-impl-link-l")
        os.symlink(target, link)
        call(["set", "files.claims_file", json.dumps(link)], repo=repo)
        code, out = call(["set", "files.claims_file", "null"], repo=repo)
        check("a symlink is left", code == 0 and os.path.islink(link) and os.path.exists(target) and out == "")
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            ro = os.path.join(tmp, "ro")
            os.mkdir(ro)
            stuck = mk("dw-impl-stuck-s", ro)
            call(["set", "files.failure_file", json.dumps(stuck)], repo=repo)
            os.chmod(ro, 0o500)
            try:
                code, out = call(["set", "files.failure_file", "null"], repo=repo)
            finally:
                os.chmod(ro, 0o700)
            check("a removal that fails is printed left:, the call exiting 0", code == 0 and os.path.exists(stuck)
                  and out.startswith("left: %s -- " % stuck)
                  and json.load(open(f, encoding="utf-8"))["files"]["failure_file"] is None)

        # the lock: parallel appends keep every entry
        procs = [subprocess.Popen([sys.executable, me, "--repo", repo, "append", "report.notices", json.dumps("n%d" % i)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=clean_env())
                 for i in range(24)]
        codes = [p.wait() for p in procs]
        notices = json.load(open(f, encoding="utf-8"))["report"]["notices"]
        check("parallel appends keep every entry", codes == [0] * 24
              and sorted(notices) == sorted("n%d" % i for i in range(24)))

        # input as UTF-8 under a C locale, UTF-8 mode off: argv and stdin
        env = clean_env(LC_ALL="C", LANG="C", PYTHONUTF8="0", PYTHONIOENCODING="")
        env.pop("PYTHONIOENCODING")
        r1 = subprocess.run([sys.executable, me, "--repo", repo, "set", "branch", json.dumps("feat/ünï", ensure_ascii=False)],
                            env=env, capture_output=True)
        r2 = subprocess.run([sys.executable, me, "--repo", repo, "set"], env=env, capture_output=True,
                            input=json.dumps({"stash_ref": "stash ünï"}, ensure_ascii=False).encode("utf-8"))
        r3 = subprocess.run([sys.executable, me, "--repo", repo, "read", "branch"], env=env, capture_output=True)
        d = json.load(open(f, encoding="utf-8"))
        check("argv read as UTF-8 under LC_ALL=C", r1.returncode == 0 and d["branch"] == "feat/ünï")
        check("stdin read as UTF-8 under LC_ALL=C", r2.returncode == 0 and d["stash_ref"] == "stash ünï")
        check("output written as UTF-8 under LC_ALL=C", r3.returncode == 0 and "feat/ünï".encode("utf-8") in r3.stdout)

        # OSError: its own code, never 1
        os.chmod(f, 0)
        unreadable = not os.access(f, os.R_OK)
        if unreadable:
            check("an unreadable file exits 4, not 1", call(["read"], repo=repo)[0] == 4)
        os.chmod(f, 0o600)

        # invalid UTF-8 in argv: exit 2, the file unchanged
        before = open(f, "rb").read()
        r = subprocess.run([sys.executable, me, "--repo", repo, "set", "branch", b'"\xff"'], capture_output=True,
                           env=clean_env())
        check("invalid UTF-8 in argv exits 2, the file unchanged", r.returncode == 2
              and b"Traceback" not in r.stderr and open(f, "rb").read() == before)
        r = subprocess.run([sys.executable, me, "--repo", repo, "read", b"files.\xff"], capture_output=True,
                           env=clean_env())
        check("an invalid-UTF-8 key exits 3, shown as \\xff", r.returncode == 3
              and b"files.\\xff" in r.stderr and b"udcff" not in r.stderr)

        # an unreadable directory on the path: 4, never 1
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            os.chmod(here, 0o600)
            try:
                code_open = call(["open", "Phase 2A"], repo=repo)[0]
                code_read = call(["read"], repo=repo)[0]
                code_rm = call(["remove"], repo=repo)[0]
            finally:
                os.chmod(here, 0o700)
            check("an unreachable file exits 4, not 1", (code_open, code_read, code_rm) == (4, 4, 4))
            check("the file survives an unreachable remove", os.path.isfile(f))

        # a call with no file creates nothing
        repo2 = os.path.join(tmp, "bare")
        subprocess.run(["git", "init", "-q", repo2], check=True)
        f2 = state_path(repo2)
        codes = [call(c, s, repo2)[0] for c, s in ((["open", "Phase 2A"], ""), (["read"], ""),
                                                    (["set", "class", '"X"'], ""), (["append", "deferred", '"x"'], ""),
                                                    (["set"], '{"class": "X"}'), (["remove"], ""))]
        check("a call with no file exits 1, remove 0", codes == [1, 1, 1, 1, 1, 0])
        check("a call with no file creates nothing", not os.path.exists(os.path.dirname(f2)))

        # guarded remove: temp files named, a --keep path, a non-temp path left, then the file
        def mk(name):
            p = os.path.join(tmp, name)
            open(p, "w").close()
            return p
        plan, summ, kept = mk("dw-impl-plan-1"), mk("dw-impl-summary-1"), mk("dw-impl-diff-1")
        report, patch, user = mk("dw-impl-step-1"), mk("dw-impl-patch-1"), mk("notes.md")
        lineage_check = mk("dw-impl-lineage-1")
        call(["set", "lineage", json.dumps({"check_file": lineage_check, "line": "Lineage: current"})], repo=repo)
        files = {m: None for m in dict(KEYS)["files"]}
        files.update({"plan_file": plan, "summary_file": summ, "test_diff_file": kept, "review_file": user})
        call(["set", "files", json.dumps(files),
              "step_groups", json.dumps([{"steps": [1], "status": "done", "report": report}]),
              "patches", json.dumps([{"path": patch, "temp": True, "outcome": "applied"},
                                     {"path": user, "temp": False, "outcome": "refused"}])], repo=repo)
        code, out = call(["remove", "--keep", kept], repo=repo)
        check("remove succeeds", code == 0 and not os.path.exists(f))
        check("remove takes the temp files", not any(os.path.exists(p) for p in (plan, summ, report, patch)))
        check("remove takes lineage.check_file", not os.path.exists(lineage_check))
        check("remove keeps a --keep path", os.path.exists(kept))
        check("remove leaves a non-temp path", os.path.exists(user) and "left: %s" % user in out)
        check("stale file survives remove", len([n for n in os.listdir(here) if STALE_RE.match(n)]) == 1)
        check("remove with no file is a no-op", call(["remove"], repo=repo)[0] == 0)

        # the check run's two snapshot files: files members, a fresh one replacing the last
        sb1, sa1, sb2 = mk("dw-impl-snapshot-1"), mk("dw-impl-snapshot-2"), mk("dw-impl-snapshot-3")
        check("files holds snapshot_before and snapshot_after",
              {"snapshot_before", "snapshot_after"} <= set(dict(KEYS)["files"]))
        call(["init"], json.dumps(fresh()), repo)
        code, _ = call(["set", "files.snapshot_before", json.dumps(sb1),
                        "files.snapshot_after", json.dumps(sa1)], repo=repo)
        check("set takes the snapshot paths", code == 0)
        code, out = call(["set", "files.snapshot_before", json.dumps(sb2)], repo=repo)
        check("a fresh snapshot_before removes the one it replaces", code == 0 and not os.path.exists(sb1)
              and "removed: %s" % sb1 in out and os.path.exists(sa1))
        code, out = call(["remove"], repo=repo)
        check("remove takes both snapshot files", code == 0 and not os.path.exists(sb2)
              and not os.path.exists(sa1))

        # reviews' diff and return files: set and remove take them like a files member
        rd1, rr1, rd2, rr2 = (mk("dw-impl-diff-1"), mk("dw-impl-return-1"),
                              mk("dw-impl-diff-2"), mk("dw-impl-return-2"))
        call(["init"], json.dumps(fresh()), repo)
        call(["set", "reviews", json.dumps([
            {"round": "first", "scope": "piece:p", "paths": ["a.py"], "diff_file": rd1, "return_file": rr1,
             "verdict": None},
            {"round": "first", "scope": "overall", "paths": [], "diff_file": rd2, "return_file": rr2,
             "verdict": None}])], repo=repo)
        code, out = call(["set", "reviews", json.dumps([
            {"round": "first", "scope": "overall", "paths": [], "diff_file": rd2, "return_file": rr2,
             "verdict": None}])], repo=repo)
        check("a set of reviews that drops an entry removes its diff and return files", code == 0
              and not os.path.exists(rd1) and not os.path.exists(rr1)
              and "removed: %s" % rd1 in out and "removed: %s" % rr1 in out)
        check("a set of reviews keeps the files of the entry it keeps", os.path.exists(rd2)
              and os.path.exists(rr2))
        code, out = call(["remove"], repo=repo)
        check("remove takes a review's files", code == 0 and not os.path.exists(rd2)
              and not os.path.exists(rr2) and "removed: %s" % rd2 in out and "removed: %s" % rr2 in out)

        # init --recover with no file: the line it appends says so, and that nothing was moved aside
        code, out = call(["init", "--recover"], json.dumps(fresh()), repo)
        a = json.load(open(f, encoding="utf-8"))["assumptions"]
        check("--recover with no file names the rebuild, nothing moved aside", code == 0
              and "moved aside:" not in out and len(a) == 2 and "This run's run-state file" in a[-1]
              and "none was moved aside" in a[-1])

        # set into a list entry's member
        call(["set", "step_groups", json.dumps([{"steps": [1], "status": None}, {"steps": [2], "status": None}])],
             repo=repo)
        code, _ = call(["set", "step_groups.-1.status", '"done"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set into the last list entry's member", code == 0 and d["step_groups"][-1]["status"] == "done"
              and d["step_groups"][0]["status"] is None)
        check("set refuses a list entry the file lacks", call(["set", "step_groups.5.status", '"x"'], repo=repo)[0] == 2)

        # remove on an unparseable file: the file still goes
        with open(f, "w", encoding="utf-8") as w:
            w.write("{broken")
        code, out = call(["remove"], repo=repo)
        check("remove on an unparseable file removes it", code == 0 and not os.path.exists(f)
              and "removed: %s" % f in out)
        check("guard refuses another path", not guarded(os.path.join(tmp, "implement-run.json"))
              and not guarded(os.path.join(tmp, "dev-workflows", "other.json"))
              and guarded(f))
        check("unknown subcommand", call(["frob"], repo=repo)[0] == 2)

        # a linked worktree has its own file
        wt = os.path.join(tmp, "w t")
        subprocess.run(["git", "-C", repo, "worktree", "add", "-q", "-b", "wt", wt], check=True,
                       capture_output=True)
        check("a worktree's file is its own", state_path(wt) != f and guarded(state_path(wt)))

        # ---- format 2: the stamps, the session guard, peek, persist, the tombstone, init --resume ----
        g = os.path.join(tmp, "g5 [r] q")
        subprocess.run(["git", "init", "-q", g], check=True)
        gf = state_path(g)
        gd = os.path.dirname(gf)
        dd = os.path.join(gd, "implement-run.d")
        tomb_p = os.path.join(gd, "implement-run.done")
        stamp_re = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        OLD = "2000-01-01T00:00:00Z"

        def st():
            with open(gf, encoding="utf-8") as r:
                return json.load(r)

        def poke(**kv):
            # the file written directly, as a dead run or another session left it
            d = st()
            d.update(kv)
            with open(gf, "w", encoding="utf-8") as w:
                json.dump(d, w)

        def mkf(name, text):
            p = os.path.join(tmp, name)
            with open(p, "w", encoding="utf-8") as w:
                w.write(text)
            return p

        def stamped(v):
            return isinstance(v, str) and bool(stamp_re.match(v))

        def git_path(rel):
            p = subprocess.run(["git", "-C", g, "rev-parse", "--git-path", rel], capture_output=True, text=True,
                               check=True).stdout.rstrip("\n")
            return p if os.path.isabs(p) else os.path.join(os.path.abspath(g), p)

        check("the durable directory and the tombstone are git's own paths",
              git_path("dev-workflows/implement-run.d") == dd and git_path("dev-workflows/implement-run.done") == tomb_p)
        check("KEYS_LINE names every format-2 key", dict(KEYS)["format"] == 2
              and all(" %s " % k in " %s " % KEYS_LINE for k in ("session", "started", "updated", "step",
                                                                 "review_in_hand", "phase46_head", "run_environment",
                                                                 "stash_before", "stopping"))
              and " tree{head snapshot when} " in KEYS_LINE and " durable{}" in KEYS_LINE
              and " note_blobs}" in KEYS_LINE and "code_handoff_choice" not in KEYS_LINE)

        # peek: 1, 5 and 8; on a format-2 file, the file printed and nothing changed, moved or locked
        code, out = call(["peek"], repo=g)
        check("peek with no file exits 1, creating nothing", code == 1 and not os.path.exists(gd))
        os.makedirs(gd)
        with open(gf, "w", encoding="utf-8") as w:
            w.write("{broken")
        check("peek on a file that does not parse exits 5", call(["peek"], repo=g)[0] == 5)
        with open(gf, "w", encoding="utf-8") as w:
            json.dump({"format": 1, "phase": "Phase 3B"}, w)
        code, out = call(["peek"], repo=g)
        check("peek on a format-1 file exits 8, printing nothing", code == 8 and out == "")
        check("peek takes no argument", call(["peek", "phase"], repo=g)[0] == 2)
        os.unlink(gf)

        # init: format 2, session and started stamped, every format-2 key at its default
        code, _ = call(["init"], json.dumps(fresh()), g)
        check("init with a null session writes session null", code == 0 and st()["session"] is None)
        code, _ = call(["init"], json.dumps(fresh()), g, session="A")
        d = st()
        started0 = d["started"]
        check("init writes format 2", code == 0 and d["format"] == 2)
        check("init stamps session, started and updated", d["session"] == "A" and stamped(d["started"])
              and d["updated"] == d["started"])
        check("init gives the format-2 keys their defaults", d["step"] is None and d["review_in_hand"] is None
              and d["tree"] == {"head": None, "snapshot": None, "when": None} and d["phase46_head"] is None
              and d["durable"] == {} and d["run_environment"] is None and d["stash_before"] is None
              and d["stopping"] is None and d["conformance"]["note_blobs"] == {})
        check("tree is never null", call(["set", "tree", "null"], repo=g, session="A")[0] == 3)
        lock = os.path.join(gd, LOCK)
        os.unlink(lock)
        raw, mtime = open(gf, "rb").read(), os.stat(gf).st_mtime_ns
        code, out = call(["peek"], repo=g, session="B")
        check("peek prints a format-2 file, unguarded, changing and locking nothing", code == 0
              and json.loads(out) == json.loads(raw.decode("utf-8")) and open(gf, "rb").read() == raw
              and os.stat(gf).st_mtime_ns == mtime and not os.path.exists(lock))

        # every call that changes the file stamps updated; only init touches session and started
        for verb, argv in (("set", ["set", "class", '"SIMPLE"']), ("open", ["open", "Phase 1.5"]),
                           ("append", ["append", "deferred", '"x"'])):
            poke(updated=OLD)
            code, _ = call(argv, repo=g, session="A")
            d = st()
            check("%s stamps updated, leaving session and started" % verb, code == 0 and stamped(d["updated"])
                  and d["updated"] != OLD and d["session"] == "A" and d["started"] == started0)
        poke(updated=OLD)
        code, _ = call(["set", "class", '"MODERATE"'], repo=g)
        d = st()
        check("a null-session write passes the guard, leaving session as it was", code == 0
              and d["class"] == "MODERATE" and d["session"] == "A" and d["updated"] != OLD)
        poke(session=None)
        code, _ = call(["set", "class", '"SIMPLE"'], repo=g, session="B")
        check("a file whose session is null takes another caller's write, its session left null", code == 0
              and st()["session"] is None)
        poke(session="A")

        # the guard: each guarded call exits 9 on "A" against "B", changing nothing
        src = mkf("dw-impl-src-g", "source")
        call(["set", "files.summary_file", json.dumps(src)], repo=g, session="A")
        before, names = open(gf, "rb").read(), sorted(os.listdir(gd))
        for name, argv, stdin in (("open", ["open", "Phase 2A"], ""), ("set", ["set", "class", '"X"'], ""),
                                  ("append", ["append", "deferred", '"y"'], ""),
                                  ("persist", ["persist", "files.summary_file", src], ""),
                                  ("remove", ["remove"], ""),
                                  ("init --recover", ["init", "--recover"], json.dumps(fresh()))):
            code, _ = call(argv, stdin, g, session="B")
            check("%s exits 9 against another session's file, naming it" % name, code == 9 and "session A" in said[0])
        check("a call the guard refuses changes nothing", open(gf, "rb").read() == before
              and sorted(os.listdir(gd)) == names and os.path.isfile(src))
        check("read is not guarded", call(["read", "class"], repo=g, session="B")[0] == 0)
        code, _ = call(["init"], json.dumps(fresh()), g, session="C")
        check("plain init is not guarded", code == 0 and st()["session"] == "C")

        # the script's own keys: set, append and init refuse each, tree.snapshot in both forms
        before = open(gf, "rb").read()
        for argv in (["set", "session", '"C"'], ["set", "started", json.dumps(OLD)], ["set", "updated", json.dumps(OLD)],
                     ["set", "durable", "{}"], ["set", "tree.snapshot", '"x"'], ["set", "tree", '{"snapshot": "x"}']):
            code, _ = call(argv, repo=g, session="C")
            check("set refuses %s %s, the script's own" % (argv[1], argv[2]), code == 3
                  and "the script alone writes" in said[0])
        code, _ = call(["set"], json.dumps({"tree": {"head": "h", "snapshot": "x"}}), g, session="C")
        check("set's stdin object refuses tree.snapshot as a member of tree", code == 3)
        check("append refuses a script-owned key", call(["append", "session", '"x"'], repo=g, session="C")[0] == 3)
        check("init refuses a script-owned key in its object",
              call(["init"], json.dumps(fresh(session="X")), g, session="C")[0] == 3
              and call(["init"], json.dumps(fresh(tree={"snapshot": "x"})), g, session="C")[0] == 3)
        check("a refused script-owned write changes nothing", open(gf, "rb").read() == before)

        # open resets step; append step_groups stamps started
        call(["set", "step", '"3B.6"'], repo=g, session="C")
        code, out = call(["open", "Phase 3.5"], repo=g, session="C")
        d = st()
        check("open sets phase and resets step to null", code == 0 and json.loads(out)["step"] is None
              and d["step"] is None and d["phase"] == "Phase 3.5")
        code, _ = call(["append", "step_groups", json.dumps({"steps": [1], "status": None, "report": None})],
                       repo=g, session="C")
        call(["append"], json.dumps({"step_groups": {"steps": [2], "status": None, "report": None}}), g, session="C")
        sg = st()["step_groups"]
        check("append step_groups stamps each entry's started", code == 0 and len(sg) == 2
              and all(stamped(e.get("started")) for e in sg) and sg[0]["steps"] == [1])

        # persist: the copy's path printed, {copy, of} recorded, a -1 normalised
        rep = mkf("dw-impl-code-g1", "report one")
        call(["set", "step_groups.-1.report", json.dumps(rep)], repo=g, session="C")
        poke(updated=OLD)
        code, out = call(["persist", "step_groups.-1.report", rep], repo=g, session="C")
        rc = out.rstrip("\n")
        d = st()
        check("persist prints the copy's absolute path, in the durable directory", code == 0 and out == rc + "\n"
              and os.path.isabs(rc) and os.path.dirname(rc) == dd and open(rc, encoding="utf-8").read() == "report one")
        check("persist records {copy, of} under the label, its -1 normalised to the absolute index",
              d["durable"] == {"step_groups.1.report": {"copy": rc, "of": rep}})
        check("persist stamps updated", stamped(d["updated"]) and d["updated"] != OLD)
        s1 = mkf("dw-impl-snap-g1", "snap one")
        code, out = call(["persist", "tree.snapshot", s1], repo=g, session="C")
        sc = out.rstrip("\n")
        d = st()
        check("persist tree.snapshot writes tree.snapshot, to the copy's path", code == 0
              and d["tree"]["snapshot"] == sc and d["durable"]["tree.snapshot"] == {"copy": sc, "of": s1})
        code, _ = call(["set", "tree", json.dumps({"head": "abc", "when": "before commit"})], repo=g, session="C")
        d = st()
        check("set tree's head and when keeps tree.snapshot, its entry and its copy", code == 0
              and d["tree"] == {"head": "abc", "snapshot": sc, "when": "before commit"}
              and d["durable"]["tree.snapshot"]["copy"] == sc and os.path.isfile(sc))
        s2 = mkf("dw-impl-snap-g2", "snap two")
        code, out = call(["persist", "tree.snapshot", s2], repo=g, session="C")
        d = st()
        check("the next persist tree.snapshot replaces the copy", code == 0 and d["tree"]["snapshot"] == out.rstrip("\n")
              and open(d["tree"]["snapshot"], encoding="utf-8").read() == "snap two"
              and d["durable"]["tree.snapshot"]["of"] == s2 and len(os.listdir(dd)) == 2)
        check("persist refuses a file that is not there",
              call(["persist", "files.plan_file", os.path.join(tmp, "absent-g")], repo=g, session="C")[0] == 2)
        check("persist refuses a key the file does not hold",
              call(["persist", "files.plan", s2], repo=g, session="C")[0] == 3)
        check("persist refuses a key that names no path", call(["persist", "class", s2], repo=g, session="C")[0] == 3)
        check("persist refuses a list entry the file lacks",
              call(["persist", "step_groups.9.report", s2], repo=g, session="C")[0] == 2)
        check("persist takes a label and a file", call(["persist", "files.plan_file"], repo=g, session="C")[0] == 2)

        # set drops a copy whose key has moved on; a note: entry and tree.snapshot's stay
        pp = mkf("dw-impl-plan-g1", "plan")
        call(["set", "files.pending_plan_file", json.dumps(pp)], repo=g, session="C")
        pc = call(["persist", "files.pending_plan_file", pp], repo=g, session="C")[1].rstrip("\n")
        note = mkf("note g.md", "a note")
        nc = call(["persist", "note:" + note, note], repo=g, session="C")[1].rstrip("\n")
        code, _ = call(["set", "class", '"SIGNIFICANT"'], repo=g, session="C")
        d = st()
        check("a set that leaves a key naming its of keeps its entry and copy", code == 0
              and "files.pending_plan_file" in d["durable"] and os.path.isfile(pc))
        code, out = call(["set", "files.pending_plan_file", "null"], repo=g, session="C")
        d = st()
        check("pending_plan_file set to null drops its entry and deletes its copy", code == 0
              and "files.pending_plan_file" not in d["durable"] and not os.path.exists(pc)
              and "removed: %s" % pc in out)
        check("a note: entry survives set", d["durable"].get("note:" + note) == {"copy": nc, "of": note}
              and os.path.isfile(nc))
        check("tree.snapshot's entry survives set", d["durable"]["tree.snapshot"]["copy"] == sc and os.path.isfile(sc))
        sm1, sm2 = mkf("dw-impl-sum-g1", "a"), mkf("dw-impl-sum-g2", "b")
        call(["set", "files.summary_file", json.dumps(sm1)], repo=g, session="C")
        smc = call(["persist", "files.summary_file", sm1], repo=g, session="C")[1].rstrip("\n")
        code, out = call(["set", "files.summary_file", json.dumps(sm2)], repo=g, session="C")
        check("a key set to another path drops its entry and deletes its copy", code == 0
              and "files.summary_file" not in st()["durable"] and not os.path.exists(smc))
        cf = mkf("dw-impl-claims-g1", "claims")
        call(["set", "files.claims_file", json.dumps(cf)], repo=g, session="C")
        cc = call(["persist", "files.claims_file", cf], repo=g, session="C")[1].rstrip("\n")
        call(["set", "files.review_file", json.dumps(cc)], repo=g, session="C")
        code, out = call(["set", "files.claims_file", "null"], repo=g, session="C")
        check("a dropped entry's copy that another key still names is kept", code == 0
              and "files.claims_file" not in st()["durable"] and os.path.isfile(cc))

        # the tombstone: init --recover exits 9 where it names another session; --recover keeps the directory
        held = sorted(os.listdir(dd))
        with open(tomb_p, "w", encoding="utf-8") as w:
            json.dump({"session": "Z", "at": OLD}, w)
        before = open(gf, "rb").read()
        code, _ = call(["init", "--recover"], json.dumps(fresh()), g, session="C")
        check("init --recover exits 9 against a tombstone from another session, naming it", code == 9
              and "session Z" in said[0] and open(gf, "rb").read() == before)
        check("init --recover with a null session passes a tombstone naming one, as the guard does",
              call(["init", "--recover"], json.dumps(fresh()), g)[0] == 0)
        with open(tomb_p, "w", encoding="utf-8") as w:
            json.dump({"session": None, "at": OLD}, w)
        code, _ = call(["init", "--recover"], json.dumps(fresh()), g, session="C")
        d = st()
        check("init --recover passes a tombstone whose session is null, leaving it", code == 0
              and os.path.isfile(tomb_p))
        check("init --recover keeps the durable directory, and durable starts empty",
              sorted(os.listdir(dd)) == held and d["durable"] == {} and d["session"] == "C")
        with open(tomb_p, "w", encoding="utf-8") as w:
            json.dump({"session": "C", "at": OLD}, w)
        check("init --recover passes a tombstone of its own session",
              call(["init", "--recover"], json.dumps(fresh()), g, session="C")[0] == 0)

        # plain init empties the durable directory and removes the tombstone
        code, out = call(["init"], json.dumps(fresh()), g, session="C")
        a = st()["assumptions"]
        moved = sorted(n for n in os.listdir(gd) if STALE_RE.match(n))
        check("plain init empties the durable directory and removes the tombstone", code == 0
              and (not os.path.exists(dd) or os.listdir(dd) == []) and not os.path.lexists(tomb_p)
              and "removed: %s" % dd in out)
        check("plain init's line says the earlier run's durable copies were deleted", len(moved) == 1 and len(a) == 2
              and a[-1] == "Run-state file an earlier run left, not resumed, moved aside and its durable copies "
                           "deleted: %s" % os.path.join(gd, moved[0]))

        # remove: the durable directory goes whole, a path inside it skipped unprinted, a tombstone left
        pf = mkf("dw-impl-plan-g2", "plan two")
        call(["set", "files.plan_file", json.dumps(pf)], repo=g, session="C")
        pfc = call(["persist", "files.plan_file", pf], repo=g, session="C")[1].rstrip("\n")
        call(["set", "files.review_file", json.dumps(pfc)], repo=g, session="C")
        code, out = call(["remove"], repo=g, session="C")
        t = json.load(open(tomb_p, encoding="utf-8")) if os.path.isfile(tomb_p) else None
        check("remove takes the file, its temp files and the durable directory", code == 0 and not os.path.exists(gf)
              and not os.path.exists(dd) and not os.path.exists(pf) and "removed: %s" % dd in out)
        check("remove skips a path inside the durable directory, unprinted", pfc not in out)
        check("remove leaves a tombstone naming its session and when", isinstance(t, dict)
              and sorted(t) == ["at", "session"] and t["session"] == "C" and stamped(t["at"]))
        os.unlink(tomb_p)
        os.makedirs(dd)
        open(os.path.join(dd, "orphan"), "w").close()
        code, out = call(["remove"], repo=g, session="C")
        check("remove with no file deletes the durable directory and writes no tombstone", code == 0
              and not os.path.exists(dd) and not os.path.lexists(tomb_p))

        # init --resume: 1, 5 and 8
        code, _ = call(["init", "--resume"], "{}", g, session="E")
        check("init --resume with no file exits 1, creating nothing", code == 1 and not os.path.exists(gf))
        with open(gf, "w", encoding="utf-8") as w:
            w.write("{broken")
        check("init --resume on a file that does not parse exits 5",
              call(["init", "--resume"], "{}", g, session="E")[0] == 5)
        with open(gf, "w", encoding="utf-8") as w:
            json.dump(dict(fresh(format=1), phase="Phase 3B"), w)
        check("init --resume on a format-1 file exits 8", call(["init", "--resume"], "{}", g, session="E")[0] == 8)
        os.unlink(gf)

        # init --resume: in place; its stdin merged; each path location left, repointed or nulled
        lin = os.path.join(tmp, "dw-impl-lineage-g")  # named, never made
        call(["init"], json.dumps(fresh(
            unit_folder=os.path.join(tmp, "no such unit"),
            pre_existing_dirty=[{"path": "gone/file.txt", "fingerprint": "f", "status": " M"}],
            lineage={"check_file": lin, "line": "Lineage: current"}, inputs_read=["a.md"],
            report={"notices": ["n0"]}, routing={"block": {"classification": "MODERATE"}, "history": ["h"]},
            coding_model="m1")), g, session="D")
        live, rep, ret = mkf("dw-impl-plan-g3", "live"), mkf("dw-impl-code-g2", "group"), mkf("dw-impl-ret-g1", "ret")
        gone = os.path.join(tmp, "dw-impl-summary-g9")  # named, never made, no copy
        old_c, new_c = mkf("dw-impl-claims-g2", "old claims"), os.path.join(tmp, "dw-impl-claims-g3")
        call(["set", "files.plan_file", json.dumps(live), "files.review_return_file", json.dumps(ret),
              "files.summary_file", json.dumps(gone), "files.claims_file", json.dumps(new_c),
              "phase", '"Phase 3B"', "step", '"3B.6"'], repo=g, session="D")
        call(["append", "step_groups", json.dumps({"steps": [1], "status": "done", "report": rep})], repo=g, session="D")
        live_c = call(["persist", "files.plan_file", live], repo=g, session="D")[1].rstrip("\n")
        rep_c = call(["persist", "step_groups.-1.report", rep], repo=g, session="D")[1].rstrip("\n")
        ret_c = call(["persist", "files.review_return_file", ret], repo=g, session="D")[1].rstrip("\n")
        snap = mkf("dw-impl-snap-g3", "snap three")
        snap_c = call(["persist", "tree.snapshot", snap], repo=g, session="D")[1].rstrip("\n")
        call(["set", "tree", json.dumps({"head": "abc", "when": "after commit"})], repo=g, session="D")
        call(["persist", "files.claims_file", old_c], repo=g, session="D")  # a copy of another file than the key names
        os.unlink(rep)  # Review Focus 4: the report's temp is gone
        os.unlink(ret)
        os.symlink(os.path.join(tmp, "no-target-g"), ret)  # something left at the name, no file
        os.unlink(snap)
        poke(updated="2026-01-02T03:04:05Z")
        d0 = st()
        stale0, held = sorted(n for n in os.listdir(gd) if STALE_RE.match(n)), sorted(os.listdir(dd))
        code, out = call(["init", "--resume"], json.dumps({
            "coding_model": "m2", "routing": {"block": {"classification": "SIGNIFICANT"}}, "inputs_read": ["b.md"],
            "report.notices": ["n1"], "specs_git": "blocked"}), g, session="E")
        d = st()
        check("init --resume takes the file over in place, moving nothing aside", code == 0
              and "resumed: %s" % gf in out and sorted(n for n in os.listdir(gd) if STALE_RE.match(n)) == stale0
              and sorted(os.listdir(dd)) == held)
        check("init --resume writes session, keeps started and stamps updated", d["session"] == "E"
              and d["started"] == d0["started"] and stamped(d["updated"]) and d["updated"] != d0["updated"])
        check("init --resume appends its line to assumptions",
              d["assumptions"][-1] == "Resumed at Phase 3B step 3B.6 after session D stopped at 2026-01-02T03:04:05Z")
        check("init --resume appends inputs_read and report.notices", d["inputs_read"] == ["a.md", "b.md"]
              and d["report"]["notices"] == ["n0", "n1"])
        check("init --resume writes its other keys as set writes them", d["coding_model"] == "m2"
              and d["specs_git"] == "blocked"
              and d["routing"] == {"block": {"classification": "SIGNIFICANT"}, "history": ["h"]})
        check("init --resume leaves a path whose file is there, though a copy exists",
              d["files"]["plan_file"] == live and os.path.isfile(live_c))
        check("init --resume repoints a step group's missing report to its copy (Review Focus 4)",
              d["step_groups"][0]["report"] == rep_c and os.path.isfile(rep_c))
        check("init --resume repoints a missing path whose of matches, deleting its dw-impl- original",
              d["files"]["review_return_file"] == ret_c and not os.path.lexists(ret) and "removed: %s" % ret in out)
        check("init --resume nulls a missing path with no copy", d["files"]["summary_file"] is None
              and d["lineage"]["check_file"] is None)
        check("init --resume nulls a missing path whose copy is of another file", d["files"]["claims_file"] is None)
        check("init --resume leaves pre_existing_dirty and unit_folder alone",
              d["pre_existing_dirty"][0]["path"] == "gone/file.txt" and d["unit_folder"] == os.path.join(tmp, "no such unit"))
        check("init --resume leaves tree.snapshot, which names its copy", d["tree"]["snapshot"] == snap_c
              and os.path.isfile(snap_c))
        code, _ = call(["set", "step", '"3B.7"'], repo=g, session="E")
        d = st()
        check("a repointed report keeps its key and its copy through a later set", code == 0
              and d["step_groups"][0]["report"] == rep_c and os.path.isfile(rep_c) and "step_groups.0.report" in d["durable"])
        check("the session that was taken over is refused", call(["set", "class", '"X"'], repo=g, session="D")[0] == 9)
        before = open(gf, "rb").read()
        check("init --resume refuses a stdin key outside its list",
              call(["init", "--resume"], '{"class": "X"}', g, session="E")[0] == 3
              and call(["init", "--resume"], json.dumps({"report": {"notices": []}}), g, session="E")[0] == 3)
        check("init --resume refuses a value of the wrong type",
              call(["init", "--resume"], '{"inputs_read": "x"}', g, session="E")[0] == 3)
        check("init --resume refuses a non-object", call(["init", "--resume"], "[1]", g, session="E")[0] == 2)
        check("a refused init --resume changes nothing", open(gf, "rb").read() == before)
        call(["open", "Phase 4"], repo=g, session="E")
        upd = st()["updated"]
        code, _ = call(["init", "--resume"], "{}", g, session="F")
        check("init --resume names the phase alone where step is null", code == 0 and st()["session"] == "F"
              and st()["assumptions"][-1] == "Resumed at Phase 4 after session E stopped at %s" % upd)

        # the new calls, with no file, create nothing
        nf = mkf("dw-impl-plan-g4", "x")
        codes = [call(c, s, repo2, session="A")[0] for c, s in ((["peek"], ""), (["persist", "files.plan_file", nf], ""),
                                                               (["init", "--resume"], "{}"))]
        check("peek, persist and init --resume with no file exit 1, creating nothing", codes == [1, 1, 1]
              and not os.path.exists(os.path.dirname(state_path(repo2))))

        # main() takes the session from CLAUDE_CODE_SESSION_ID, an empty one as null
        def main_call(argv, stdin="", **env):
            return subprocess.run([sys.executable, me, "--repo", g] + argv, input=stdin.encode("utf-8"),
                                  capture_output=True, env=clean_env(**env))
        r = main_call(["init"], json.dumps(fresh()), CLAUDE_CODE_SESSION_ID="S1")
        check("main takes the session from CLAUDE_CODE_SESSION_ID", r.returncode == 0 and st()["session"] == "S1")
        r = main_call(["set", "class", '"X"'], CLAUDE_CODE_SESSION_ID="S2")
        check("main's guard exits 9 for another session", r.returncode == 9 and b"session S1" in r.stderr)
        r = main_call(["set", "class", '"Y"'])
        check("main with the variable unset writes as a null session", r.returncode == 0 and st()["class"] == "Y"
              and st()["session"] == "S1")
        r = main_call(["init"], json.dumps(fresh()), CLAUDE_CODE_SESSION_ID="")
        check("main takes an empty CLAUDE_CODE_SESSION_ID as null", r.returncode == 0 and st()["session"] is None)

        # ---- the review's cases ----
        # persist never overwrites a copy another location names: a resumed pending plan, approved, then a re-plan
        call(["init"], json.dumps(fresh()), g, session="D")
        ap = mkf("dw-impl-plan-g5", "APPROVED")
        call(["set", "files.pending_plan_file", json.dumps(ap)], repo=g, session="D")
        call(["persist", "files.pending_plan_file", ap], repo=g, session="D")
        os.unlink(ap)
        call(["init", "--resume"], "{}", g, session="E")
        cp = st()["files"]["pending_plan_file"]
        call(["set", "files.plan_file", json.dumps(cp), "files.pending_plan_file", "null"], repo=g, session="E")
        call(["persist", "files.plan_file", cp], repo=g, session="E")
        rp = mkf("dw-impl-plan-g6", "UNAPPROVED")
        call(["set", "files.pending_plan_file", json.dumps(rp)], repo=g, session="E")
        code, out = call(["persist", "files.pending_plan_file", rp], repo=g, session="E")
        np_c = out.rstrip("\n")
        d = st()
        check("persist writes a fresh copy where another location names the label's own", code == 0
              and np_c != cp and d["files"]["plan_file"] == cp and open(cp, encoding="utf-8").read() == "APPROVED"
              and open(np_c, encoding="utf-8").read() == "UNAPPROVED"
              and d["durable"]["files.pending_plan_file"] == {"copy": np_c, "of": rp})
        rp2 = mkf("dw-impl-plan-g7", "UNAPPROVED TWO")
        call(["set", "files.pending_plan_file", json.dumps(rp2)], repo=g, session="E")
        code, out = call(["persist", "files.pending_plan_file", rp2], repo=g, session="E")
        check("a later persist of that label still leaves the copy another location names", code == 0
              and out.rstrip("\n") != cp and open(cp, encoding="utf-8").read() == "APPROVED"
              and open(out.rstrip("\n"), encoding="utf-8").read() == "UNAPPROVED TWO")

        # remove --keep: a kept path inside the durable directory is moved out, never deleted
        call(["init"], json.dumps(fresh()), g, session="D")
        kr = mkf("dw-impl-ret-g2", "RET")
        call(["set", "files.review_return_file", json.dumps(kr)], repo=g, session="D")
        call(["persist", "files.review_return_file", kr], repo=g, session="D")
        os.unlink(kr)
        call(["init", "--resume"], "{}", g, session="E")
        kc = st()["files"]["review_return_file"]
        kept_p = os.path.join(gd, "implement-run.kept-" + os.path.basename(kc))
        code, out = call(["remove", "--keep", kc], repo=g, session="E")
        check("remove --keep moves a kept path inside the durable directory out, and names it", code == 0
              and os.path.isfile(kept_p) and open(kept_p, encoding="utf-8").read() == "RET"
              and "kept: %s" % kept_p in out and not os.path.exists(dd) and not os.path.exists(gf))
        if os.path.exists(kept_p):
            os.unlink(kept_p)
        os.makedirs(dd)
        orphan = os.path.join(dd, "orphan-g")
        with open(orphan, "w", encoding="utf-8") as w:
            w.write("O")
        code, out = call(["remove", "--keep", orphan], repo=g, session="E")
        kept_o = os.path.join(gd, "implement-run.kept-orphan-g")
        check("remove --keep with no file moves a kept path out of the durable directory too", code == 0
              and os.path.isfile(kept_o) and "kept: %s" % kept_o in out and not os.path.exists(dd))
        if os.path.exists(kept_o):
            os.unlink(kept_o)

        # of is compared by its absolute path: a relative path, or a persist before its own set, keeps its copy
        call(["init"], json.dumps(fresh()), g, session="E")
        sa = mkf("dw-impl-sum-g5", "S")
        call(["set", "files.summary_file", json.dumps(sa)], repo=g, session="E")
        sa_c = call(["persist", "files.summary_file", os.path.relpath(sa)], repo=g, session="E")[1].rstrip("\n")
        code, _ = call(["set", "class", '"SIMPLE"'], repo=g, session="E")
        check("set keeps an entry whose of names the key's path relatively", code == 0
              and "files.summary_file" in st()["durable"] and os.path.isfile(sa_c))
        cl = mkf("dw-impl-claims-g5", "C")
        cl_c = call(["persist", "files.claims_file", cl], repo=g, session="E")[1].rstrip("\n")
        code, _ = call(["set", "files.claims_file", json.dumps(os.path.relpath(cl))], repo=g, session="E")
        check("a persist before its own set, the set naming the path relatively, keeps its copy", code == 0
              and st()["durable"].get("files.claims_file", {}).get("copy") == cl_c and os.path.isfile(cl_c))
        os.unlink(sa)
        code, out = call(["init", "--resume"], "{}", g, session="F")
        check("init --resume matches of by its absolute path", code == 0
              and st()["files"]["summary_file"] == sa_c)

        # the tombstone names the removed file's session, the caller's only where the file holds none
        call(["init"], json.dumps(fresh()), g, session="D")
        call(["remove"], repo=g)
        t = json.load(open(tomb_p, encoding="utf-8"))
        check("the tombstone names the removed file's session", t["session"] == "D")
        call(["init"], json.dumps(fresh()), g)
        call(["remove"], repo=g, session="C")
        t = json.load(open(tomb_p, encoding="utf-8"))
        check("the tombstone names the caller's session where the file holds none", t["session"] == "C")

        # init --resume checks the file before stdin: no file exits 1 whatever stdin holds
        check("init --resume with no file exits 1 whatever stdin holds",
              [call(["init", "--resume"], s, g, session="E")[0] for s in ("[1]", '{"class": "X"}', "not json")]
              == [1, 1, 1])

        # plain init clears the durable directory before it moves the file aside: a failure leaves the file
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            call(["init"], json.dumps(fresh()), g, session="E")
            stuck = os.path.join(dd, "stuck")
            os.makedirs(stuck)
            open(os.path.join(stuck, "x"), "w").close()
            os.chmod(stuck, 0o500)
            try:
                code, _ = call(["init"], json.dumps(fresh()), g, session="E")
            finally:
                os.chmod(stuck, 0o700)
            check("a plain init that cannot empty the durable directory leaves the file in place", code == 4
                  and os.path.isfile(gf))
            clear(dd)

        # remove with no file takes the lock before it deletes the durable directory
        if fcntl is not None:
            if os.path.exists(gf):
                os.unlink(gf)
            os.makedirs(dd, exist_ok=True)
            lk = os.open(os.path.join(gd, LOCK), os.O_RDWR | os.O_CREAT, 0o600)
            fcntl.flock(lk, fcntl.LOCK_EX)
            p = subprocess.Popen([sys.executable, me, "--repo", g, "remove"], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, env=clean_env())
            time.sleep(1.0)
            waited = p.poll() is None and os.path.isdir(dd)
            fcntl.flock(lk, fcntl.LOCK_UN)
            os.close(lk)
            check("remove with no file waits for the lock before deleting the durable directory", waited
                  and p.wait() == 0 and not os.path.exists(dd))
            # a remove that found no file before the lock re-tests under it: a file written meanwhile is
            # guarded, so a superseded session is refused and the new file's directory stays
            os.makedirs(dd)
            with open(os.path.join(dd, "files.plan_file-b"), "w", encoding="utf-8") as w:
                w.write("B's copy")
            lk = os.open(os.path.join(gd, LOCK), os.O_RDWR | os.O_CREAT, 0o600)
            fcntl.flock(lk, fcntl.LOCK_EX)
            p = subprocess.Popen([sys.executable, me, "--repo", g, "remove"], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE, env=clean_env(CLAUDE_CODE_SESSION_ID="A"))
            time.sleep(1.0)
            with open(gf, "w", encoding="utf-8") as w:  # B's init --recover lands while A waits on the lock
                json.dump(dict(merged(fresh()), session="B"), w)
            fcntl.flock(lk, fcntl.LOCK_UN)
            os.close(lk)
            err = p.communicate()[1]
            check("a remove that found no file re-tests under the lock, refusing another session's new file",
                  p.returncode == 9 and b"session B" in err and os.path.isfile(gf)
                  and os.path.isfile(os.path.join(dd, "files.plan_file-b")))
            os.unlink(gf)
            clear(dd)

        # two locations repointed from one missing original: the original removed once, no left: line
        call(["init"], json.dumps(fresh()), g, session="D")
        two = mkf("dw-impl-plan-g8", "P")
        call(["set", "files.plan_file", json.dumps(two), "files.pending_plan_file", json.dumps(two)], repo=g, session="D")
        call(["persist", "files.plan_file", two], repo=g, session="D")
        call(["persist", "files.pending_plan_file", two], repo=g, session="D")
        os.unlink(two)
        os.symlink(os.path.join(tmp, "no-target-g2"), two)
        code, out = call(["init", "--resume"], "{}", g, session="E")
        check("an original two locations repoint from is removed once, never reported left", code == 0
              and out.count("removed: %s" % two) == 1 and "left: " not in out and not os.path.lexists(two))

        # init --resume: a missing copy is never repointed to; a non-dw-impl- original is never deleted;
        # tree.snapshot is never walked, even where its copy is gone
        call(["init"], json.dumps(fresh()), g, session="D")
        mc, nd = mkf("dw-impl-ret-g3", "R"), mkf("notes-g", "N")
        sn = mkf("dw-impl-snap-g4", "SN")
        call(["set", "files.review_return_file", json.dumps(mc), "files.review_file", json.dumps(nd)], repo=g, session="D")
        mc_c = call(["persist", "files.review_return_file", mc], repo=g, session="D")[1].rstrip("\n")
        nd_c = call(["persist", "files.review_file", nd], repo=g, session="D")[1].rstrip("\n")
        sn_c = call(["persist", "tree.snapshot", sn], repo=g, session="D")[1].rstrip("\n")
        os.unlink(mc)
        os.unlink(mc_c)
        os.unlink(nd)
        os.symlink(os.path.join(tmp, "no-target-g3"), nd)
        os.unlink(sn_c)
        code, out = call(["init", "--resume"], "{}", g, session="E")
        d = st()
        check("init --resume nulls a path whose copy is gone, never repointing to it", code == 0
              and d["files"]["review_return_file"] is None)
        check("init --resume repoints, but never deletes, an original not named dw-impl-",
              d["files"]["review_file"] == nd_c and os.path.lexists(nd))
        check("init --resume leaves tree.snapshot alone though its copy is gone", d["tree"]["snapshot"] == sn_c)

        # a null on either side passes the guard, on every guarded call
        for held, caller in ((None, "B"), ("A", None)):
            for name, argv, stdin in (("open", ["open", "Phase 2A"], ""), ("set", ["set", "class", '"X"'], ""),
                                      ("append", ["append", "deferred", '"y"'], ""),
                                      ("persist", ["persist", "files.summary_file", sn], ""),
                                      ("remove", ["remove"], ""),
                                      ("init --recover", ["init", "--recover"], json.dumps(fresh()))):
                call(["init"], json.dumps(fresh()), g, session=held)
                code, _ = call(argv, stdin, g, session=caller)
                check("%s passes the guard where the %s session is null" % (
                    name, "file's" if held is None else "caller's"), code == 0)

        # ---- fable_escalation, and load's fill of a FILLED key an earlier format-2 release's file lacks ----
        FE0 = {"source": None, "choice": None}
        ks = [k for k, _ in KEYS]
        check("KEYS holds fable_escalation after coding_model", "fable_escalation" in ks
              and ks.index("fable_escalation") == ks.index("coding_model") + 1
              and dict(KEYS)["fable_escalation"] == FE0)
        check("KEYS_LINE names fable_escalation{source choice}",
              " coding_model fable_escalation{source choice} " in " %s " % KEYS_LINE)
        check("FILLED holds only keys KEYS holds, never format", "fable_escalation" in FILLED
              and all(k in dict(KEYS) for k in FILLED) and "format" not in FILLED)
        call(["init"], json.dumps(fresh()), g, session="H")
        check("init gives fable_escalation its default", st().get("fable_escalation") == FE0)
        fe = {"source": "answer", "choice": "fable"}
        code, _ = call(["set", "fable_escalation", json.dumps(fe)], repo=g, session="H")
        rcode, out = call(["read", "fable_escalation"], repo=g, session="H")
        check("set fable_escalation takes {source, choice}, and it reads back equal", code == 0 and rcode == 0
              and json.loads(out) == fe)
        code, _ = call(["set", "fable_escalation.choice", '"claude-fable-5-2"'], repo=g, session="H")
        check("set fable_escalation.choice keeps source", code == 0
              and st().get("fable_escalation") == {"source": "answer", "choice": "claude-fable-5-2"})
        before = open(gf, "rb").read()
        code, _ = call(["set", "fable_escalation", '{"model": "x"}'], repo=g, session="H")
        check("set refuses a fable_escalation member KEYS lacks, writing nothing", code == 3
              and "fable_escalation.model" in said[0] and open(gf, "rb").read() == before)
        code, _ = call(["set", "fable_escalation", '"fable"'], repo=g, session="H")
        check("set refuses fable_escalation given as a string, writing nothing", code == 3
              and "fable_escalation must be an object" in said[0] and open(gf, "rb").read() == before)
        code, _ = call(["init", "--resume"], json.dumps({"fable_escalation": fe}), g, session="I")
        check("init --resume refuses fable_escalation on its stdin, outside its list, writing nothing", code == 3
              and "fable_escalation" in said[0] and open(gf, "rb").read() == before)
        code, _ = call(["init", "--resume"], json.dumps({"routing": {"block": {}}, "coding_model": "opus"}), g,
                       session="I")
        d = st()
        check("a recorded fable_escalation survives init --resume", code == 0 and d["coding_model"] == "opus"
              and d.get("fable_escalation") == {"source": "answer", "choice": "claude-fable-5-2"})

        def lacking(*keys):
            # a file init wrote, the keys deleted from its JSON on disk: an earlier release's file, or a damaged one
            call(["init"], json.dumps(fresh()), g, session="H")
            d = st()
            for k in keys:
                d.pop(k, None)
            with open(gf, "w", encoding="utf-8") as w:
                json.dump(d, w)
            return open(gf, "rb").read()

        raw = lacking("fable_escalation")
        code, out = call(["read", "fable_escalation"], repo=g, session="H")
        check("read of a FILLED key the file lacks prints its default, writing nothing", code == 0
              and json.loads(out) == FE0 and open(gf, "rb").read() == raw)
        code, out = call(["peek"], repo=g, session="H")
        check("peek of a file lacking a FILLED key prints its default, the file's bytes unchanged", code == 0
              and json.loads(out).get("fable_escalation") == FE0 and open(gf, "rb").read() == raw)
        code, _ = call(["set", "fable_escalation.choice", '"fable"'], repo=g, session="H")
        check("set into a FILLED key the file lacks saves the key, its other member at its default", code == 0
              and st().get("fable_escalation") == {"source": None, "choice": "fable"})
        check("the fill hands out a copy, KEYS' default left as it was", dict(KEYS).get("fable_escalation") == FE0)
        lacking("fable_escalation")
        code, _ = call(["set", "class", '"HIGH-RISK"'], repo=g, session="H")
        d = st()
        check("a set of another key saves the FILLED key the file lacked, at its default", code == 0
              and d["class"] == "HIGH-RISK" and d.get("fable_escalation") == FE0)
        lacking("fable_escalation")
        code, _ = call(["append", "deferred", '"x"'], repo=g, session="H")
        d = st()
        check("an append saves the FILLED key the file lacked, at its default", code == 0
              and d["deferred"] == ["x"] and d.get("fable_escalation") == FE0)
        lacking("fable_escalation")
        code, _ = call(["init", "--resume"], "{}", g, session="I")
        check("init --resume on a file lacking a FILLED key writes its default", code == 0
              and st().get("fable_escalation") == FE0)
        lacking("format")
        code, out = call(["peek"], repo=g, session="H")
        check("peek on a file lacking format exits 8: format is never filled", code == 8 and out == "")
        raw = open(gf, "rb").read()
        code, _ = call(["init", "--resume"], "{}", g, session="I")
        check("init --resume on a file lacking format exits 8, writing nothing", code == 8
              and open(gf, "rb").read() == raw)
        lacking("phase", "clean_finish")
        codes = [call(["read", k], repo=g, session="H")[0] for k in ("phase", "clean_finish")]
        code, out = call(["peek"], repo=g, session="H")
        check("no fill outside FILLED: read of another key the file lacks still exits 3", codes == [3, 3]
              and code == 0 and "phase" not in json.loads(out) and "clean_finish" not in json.loads(out))

    if failures:
        for n in failures:
            print("FAIL %s" % n)
        print("run-state selftest: FAIL")
        return 1
    print("run-state selftest: PASS (%d checks)" % checks[0])
    return 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    session = os.environ.get("CLAUDE_CODE_SESSION_ID") or None
    try:
        run(utf8_argv(argv), sys.stdin, sys.stdout.buffer,
            session=utf8_argv([session])[0] if session else None)
        return 0
    except Fail as e:
        sys.stderr.write("run-state.py: %s\n" % e)
        return e.code
    except UnicodeError as e:
        sys.stderr.write("run-state.py: input is not UTF-8, nothing written: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

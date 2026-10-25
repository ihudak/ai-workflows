#!/usr/bin/env python3
"""run-state.py -- /implement's run-state file: create it, open a phase, set, append, read, remove.

The file is `$(git rev-parse --git-path dev-workflows/implement-run.json)` in the code repository
the run works in: per worktree, inside the git directory, never staged. `/implement` Phase 1.4
creates it and every later phase opens with `open`; commands/implement.md says what each key holds
and where it is written. Run every call from the working directory (or pass --repo <dir>). One
`/implement` run per worktree at a time is the precondition; the lock below serialises one run's own
calls, never two runs.

  run-state.py init [--recover]      a JSON object on stdin, merged over KEYS' defaults: every key or
                                     member it omits takes the default KEYS gives it, and it may hold
                                     no key or member KEYS lacks, nor one of the wrong type -- all
                                     checked before anything is moved. A file already there is moved
                                     aside unread, as implement-run.json.stale-<UTC stamp>, after any
                                     older such file is removed, so at most one is kept; the move is
                                     printed and appended to `assumptions` as a file an earlier run
                                     left. Under --recover the line appended names the file as this
                                     run's own, written again, and says whether one was moved aside.
  run-state.py open <phase>          set `phase` and print the file.
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
                                     Once the write lands, each path the file named before the call --
                                     a `files` member, a `writers` report, a `reviews` diff or
                                     return file or a `patches` path --
                                     that none of them names after it is removed, where it is a
                                     regular file, not a symlink, whose name begins `dw-impl-`, and
                                     printed `removed: <path>`; one whose removal fails is printed
                                     `left: <path> -- <error>`, and the call still exits 0.
  run-state.py append <key> <json> [<key> <json> ...]
                                     append each value to its key's list, the key written again
                                     before each value -- append assumptions '"a"' assumptions '"b"'
                                     -- or a JSON object on stdin; a key that is null becomes a
                                     one-element list.
  run-state.py remove [--keep <path>] ...
                                     the end-of-run removal: every temp file `files` names, each
                                     `writers` report, each `reviews` diff and return file and each `patches` path marked `temp`
                                     -- only a regular file whose name begins `dw-impl-`, and never
                                     a --keep path -- then the file itself, only at the git path.

A key is a top-level name or a dotted path into one (`files.plan_file`); a list entry is named by
its index (`triage.-1.followed_by`, the last entry's). `set`, `append` and `read` refuse a key the
file does not hold, and `set` a path through a null value: write that key whole. Every
read-modify-write holds an exclusive lock (fcntl.flock on .implement-run.lock beside the file) and
replaces the file whole (a temp file beside it, then os.replace), so a write is never half done and
parallel calls lose nothing; a value that does not parse changes nothing. Input -- stdin and argv --
is read as UTF-8 whatever the locale, and the file is UTF-8 with non-ASCII written as itself
(ensure_ascii=False), so a path comes back as git's -z record gave it. JSON escapes `"`, `\\` and
control characters -- `\\t`, `\\n`, `\\r` and the like -- in what `open` and `read` print, and each
escape reads back as one character. A call other than `init` that finds no file creates nothing: it
checks for the file before it makes the lock beside it. The lock file, like a stale file, is never
removed.

Exit codes:
  0  done
  1  there is no run-state file (and nothing was created)
  2  usage: bad arguments -- set's or append's among them an odd count, or a key opening with `"`,
     `[` or `{`, a value written where its key belongs -- a value that does not parse, input that
     is not UTF-8, a path through null, no such list entry
  3  a key the file does not hold (set, append, read), or an init object or a set call adding a key
     or member KEYS lacks, or giving one the wrong type
  4  the file could not be reached: an OSError reading or writing it -- an unreadable directory on
     its path included -- or git failing to name it
  5  the run-state file is there and does not parse
Standard library only; `python3 run-state.py --selftest` runs the tests.
"""
import copy
import json
import os
import re
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

# Every key the file holds, and no other, each beside the default init gives it where the caller's
# object omits it. A key whose default is an object holds exactly that object's members -- the ones
# a call may name -- each beside its own default. The default fixes the type: a key or member whose
# default is an object, a list, a boolean, an integer or a string must be given as one; one whose
# default is null takes any JSON value. `init` and `set` both hold what they are given to this list, and
# `set` merges an object given for an object key over the members the file holds.
# A list key's entries are not type-checked; the shape each holds, one entry per item:
#   pieces       {"name", "files": [], "builds_after": []}
#   writer_units {"name", "pieces": []}
#   writers      {"unit", "role": "code"|"test", "agent_id", "model", "reports": [], "status",
#                 "answer": [{"report", "question", "answer"}], "left_to_caller": [],
#                 "first_plan_reports", "resumes": 0, "fresh": 0} -- "model" the model its latest
#                 dispatch ran on; "first_plan_reports" null, or how many of "reports" a re-plan's
#                 approval found it holding
#   test_runs    {"unit", "stage": "unit"|"post-review", "rounds": 0, "status", "rulings_settled": []}
#   reviews      {"scope": "piece:<name>"|"overall", "diff_file", "return_file", "verdict"}
# commands/implement.md quotes this list (KEYS_LINE); the selftest holds the two equal.
KEYS = [
    ("format", 1), ("phase", "Phase 1.4"), ("mode", None), ("key", None), ("source", None),
    ("focus_key", None), ("unit_key", None), ("workitem_key", None), ("unit_folder", None),
    ("run_flags", None), ("specs_git", None), ("specs_merged_branch", None),
    ("spec_context", {"spec_paths": [], "in_scope_ids": None, "applicable_spec": None,
                      "applicable_ard": None, "ard_paths": [], "companion_run": None,
                      "tasks_only": None}),
    ("task_shape", None), ("clarifications", {"settled": [], "answers": []}),
    ("routing", {"block": None, "history": []}), ("class", None), ("coding_model", None),
    ("branch_answer", {"answer": None, "moves": [], "lines": []}), ("branch", None),
    ("stash_ref", None), ("pre_existing_dirty", None), ("session_branch_lift", False),
    ("test_decision", None), ("clean_finish", True),
    ("files", {"task_description_file": None, "plan_file": None, "pending_plan_file": None,
               "summary_file": None, "baseline_file": None,
               "review_diff_file": None, "partial_diff_file": None,
               "review_file": None, "claims_file": None, "failure_file": None}),
    ("pieces", []), ("writer_units", []), ("writers", []), ("test_runs", []), ("reviews", []),
    ("patches", []), ("triage", []),
    ("conformance", {"summary": None, "annotated": [], "gaps": [], "handoff_line": None}),
    ("other_repo_changes", []), ("assumptions", []), ("deferred", []),
    ("report", {"commands_run": [], "maintenance": [], "notices": [], "phase1_tasks": [],
                "confirmed_cause": None}),
    ("code_repo_outcome", None), ("replans_used", 0),
]
KEYS_LINE = " ".join(k + ("{%s}" % " ".join(d) if isinstance(d, dict) else "") for k, d in KEYS)


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


def refuse(what, extra, wrong):
    """Exit 3 naming every key or member KEYS lacks and every wrong type at once, where there is any."""
    if extra or wrong:
        raise Fail(3, "%s %s" % (what, "; ".join(
            x for x in ("holds unknown " + ", ".join(extra) if extra else "",
                        "; ".join(wrong)) if x)))


def merged(d):
    """The init object over KEYS' defaults: each key or member it omits takes its default. Exits 3 on a
    key or member KEYS lacks, or one given with the wrong type, before anything is written."""
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
    refuse("init: the object", extra, wrong)
    return out


def checked(todo):
    """set's pairs held to KEYS as init's object is: exits 3 on a key or member KEYS lacks, or a
    top-level key or an object key's <key>.<member> given a value of another type than its default
    fixes -- every slip in the call named at once, before anything is written. A deeper path or a
    list entry is not checked."""
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
    refuse("set: the call", extra, wrong)


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


PAIRS = ("takes <key> '<json>' [<key> '<json>' ...], the key written again before each value, "
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


def cmd_init(f, args, stdin, out):
    if args not in ([], ["--recover"]):
        raise Fail(2, "init takes only --recover")
    d = parse(stdin.read(), "stdin")
    if not isinstance(d, dict) or d.get("format", 1) != 1:
        raise Fail(2, "init reads a JSON object on stdin, its format 1 where it gives one")
    d = merged(d)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with locked(f):
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
        if args == ["--recover"]:
            d["assumptions"].append(
                "This run's run-state file could not be read back, and was written again from what the run "
                "still held: " + ("the file there was moved aside unread, as %s" % s if s else
                                  "no file was there, so none was moved aside"))
        elif s:
            d["assumptions"].append("Run-state file an earlier run left, moved aside unread: %s" % s)
        save(f, d)
    out.write(("created: %s\n" % f).encode("utf-8"))


def cmd_open(f, args, out):
    if len(args) != 1:
        raise Fail(2, "open takes the phase's name, as its heading names it")
    require(f)
    with locked(f):
        d = load(f)
        d["phase"] = args[0]
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


def named(d):
    """Each path the file names that a set may stop naming: every `files` member's, each report a
    `writers` entry lists, each `reviews` entry's diff and return file and each `patches` entry's
    path, in that order, each once."""
    out = []
    files = d.get("files")
    if isinstance(files, dict):
        out += [p for p in files.values() if isinstance(p, str)]
    writers, reviews, patches = d.get("writers"), d.get("reviews"), d.get("patches")
    for w in writers if isinstance(writers, list) else []:
        if isinstance(w, dict) and isinstance(w.get("reports"), list):
            out += [p for p in w["reports"] if isinstance(p, str)]
    for v in reviews if isinstance(reviews, list) else []:
        if isinstance(v, dict):
            out += [v[k] for k in ("diff_file", "return_file") if isinstance(v.get(k), str)]
    for p in patches if isinstance(patches, list) else []:
        if isinstance(p, dict) and isinstance(p.get("path"), str):
            out.append(p["path"])
    seen, once = set(), []
    for p in out:
        if os.path.abspath(p) not in seen:
            seen.add(os.path.abspath(p))
            once.append(p)
    return once


def cmd_set(f, args, stdin, out):
    todo = pairs(args, stdin, "set")
    checked(todo)
    require(f)
    want = dict(KEYS)
    with locked(f):
        d = load(f)
        before = named(d)
        for key, v in todo:
            o, k = resolve(d, key)
            if isinstance(want.get(key), dict) and isinstance(v, dict) and isinstance(o[k], dict):
                o[k] = dict(o[k])
                o[k].update(v)
            else:
                o[k] = v
        save(f, d)
        after = set(os.path.abspath(p) for p in named(d))
        for p in before:
            a = os.path.abspath(p)
            if (a in after or not os.path.basename(a).startswith(TEMP_PREFIX) or not os.path.isfile(a)
                    or os.path.islink(a)):
                continue
            try:
                os.unlink(a)
                out.write(("removed: %s\n" % p).encode("utf-8"))
            except OSError as e:
                out.write(("left: %s -- %s\n" % (p, e)).encode("utf-8"))


def cmd_append(f, args, stdin):
    todo = pairs(args, stdin, "append")
    require(f)
    with locked(f):
        d = load(f)
        for key, v in todo:
            o, k = resolve(d, key)
            if o[k] is None:
                o[k] = [v]
            elif isinstance(o[k], list):
                o[k].append(v)
            else:
                raise Fail(2, "append: %s is not a list or null" % key)
        save(f, d)


def cmd_remove(f, args, out):
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
    try:
        os.lstat(f)
    except FileNotFoundError:
        out.write(("no run-state file at %s -- nothing to remove\n" % f).encode("utf-8"))
        return
    except OSError as e:
        raise Fail(4, "cannot reach the run-state file at %s: %s" % (f, e))
    with locked(f):
        try:
            d = load(f)
        except Fail:
            d = {}
        paths = []
        files = d.get("files")
        if isinstance(files, dict):
            paths += [p for p in files.values() if isinstance(p, str)]
        for w in d.get("writers") or []:
            if isinstance(w, dict) and isinstance(w.get("reports"), list):
                paths += [p for p in w["reports"] if isinstance(p, str)]
        for v in d.get("reviews") or []:
            if isinstance(v, dict):
                paths += [v[k] for k in ("diff_file", "return_file") if isinstance(v.get(k), str)]
        for p in d.get("patches") or []:
            if isinstance(p, dict) and p.get("temp") is True and isinstance(p.get("path"), str):
                paths.append(p["path"])
        for p in paths:
            a = os.path.abspath(p)
            if a in keep:
                out.write(("kept: %s\n" % p).encode("utf-8"))
            elif (os.path.basename(a).startswith(TEMP_PREFIX) and os.path.isfile(a)
                  and not os.path.islink(a)):
                os.unlink(a)
                out.write(("removed: %s\n" % p).encode("utf-8"))
            elif os.path.lexists(a):
                out.write(("left: %s -- not a %s* temp file\n" % (p, TEMP_PREFIX)).encode("utf-8"))
        os.unlink(f)
    out.write(("removed: %s\n" % f).encode("utf-8"))


def run(argv, stdin, out, repo="."):
    if argv[:1] == ["--repo"]:
        if len(argv) < 2:
            raise Fail(2, "--repo takes a directory")
        repo, argv = argv[1], argv[2:]
    if not argv:
        raise Fail(2, "usage: run-state.py [--repo <dir>] init|open|read|set|append|remove ...")
    verb, args = argv[0], argv[1:]
    if verb not in ("init", "open", "read", "set", "append", "remove"):
        raise Fail(2, "unknown subcommand %s" % verb)
    f = state_path(repo)
    try:
        if verb == "init":
            cmd_init(f, args, stdin, out)
        elif verb == "open":
            cmd_open(f, args, out)
        elif verb == "read":
            cmd_read(f, args, out)
        elif verb == "set":
            cmd_set(f, args, stdin, out)
        elif verb == "append":
            cmd_append(f, args, stdin)
        else:
            cmd_remove(f, args, out)
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

    def call(argv, stdin="", repo=None):
        out = io.BytesIO()
        said[0] = ""
        try:
            run((["--repo", repo] if repo else []) + argv, io.StringIO(stdin), out)
            code = 0
        except Fail as e:
            code = e.code
            said[0] = str(e)
        return code, out.getvalue().decode("utf-8")

    def fresh(**over):
        # only what a caller holds: init gives every other key its default
        d = {"format": 1, "assumptions": ["seeded"]}
        d.update(over)
        return d

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
        check("init gives an omitted key its default", d["deferred"] == [] and d["writers"] == []
              and d["clean_finish"] is True and d["replans_used"] == 0 and d["phase"] == "Phase 1.4"
              and d["session_branch_lift"] is False and d["test_decision"] is None)
        check("init gives an omitted object its members' defaults",
              d["files"] == dict((m, None) for m in dict(KEYS)["files"])
              and d["report"] == {"commands_run": [], "maintenance": [], "notices": [], "phase1_tasks": [],
                                  "confirmed_cause": None})
        check("init refuses a non-object", call(["init"], "[1]", repo)[0] == 2)
        new_keys = ("pieces", "writer_units", "writers", "test_runs", "reviews")
        check("init defaults each one-writer key to an empty list", all(d.get(k) == [] for k in new_keys)
              and all(dict(KEYS).get(k) == [] for k in new_keys))
        check("KEYS drops step_groups, files.test_diff_file, files.test_report_file and files.review_return_file",
              "step_groups" not in dict(KEYS) and "test_diff_file" not in dict(KEYS)["files"]
              and "test_report_file" not in dict(KEYS)["files"]
              and "review_return_file" not in dict(KEYS)["files"])
        check("init refuses files.test_report_file",
              call(["init"], json.dumps(fresh(files={"test_report_file": "x"})), repo)[0] == 3)
        check("init refuses step_groups", call(["init"], json.dumps(fresh(step_groups=[])), repo)[0] == 3)
        check("init refuses files.test_diff_file",
              call(["init"], json.dumps(fresh(files={"test_diff_file": "x"})), repo)[0] == 3)
        code, _ = call(["init"], json.dumps(fresh(
            pieces=[{"name": "p", "files": ["a"], "builds_after": []}],
            writer_units=[{"name": "u", "pieces": ["p"]}],
            writers=[{"unit": "u", "role": "code", "agent_id": "a1", "model": "m", "reports": [], "status": None,
                      "answer": None, "left_to_caller": [], "first_plan_reports": None, "resumes": 0,
                      "fresh": 0}],
            test_runs=[{"unit": "u", "stage": "unit", "rounds": 0, "status": None}],
            reviews=[{"scope": "piece:p", "diff_file": None, "return_file": None, "verdict": None}])), repo)
        d = json.load(open(f, encoding="utf-8"))
        check("init accepts each one-writer key", code == 0 and d["writers"][0]["role"] == "code"
              and d["reviews"][0]["scope"] == "piece:p" and d["pieces"][0]["name"] == "p")
        check("init refuses a one-writer key given as a string",
              call(["init"], json.dumps(fresh(writers="x")), repo)[0] == 3)
        call(["init"], json.dumps(fresh()), repo)
        check("set refuses step_groups", call(["set", "step_groups", "[]"], repo=repo)[0] == 3)
        check("append refuses step_groups", call(["append", "step_groups", "{}"], repo=repo)[0] == 3)
        check("set refuses files.test_diff_file", call(["set", "files.test_diff_file", '"x"'], repo=repo)[0] == 3)
        check("append accepts a writers entry",
              call(["append", "writers", '{"unit": "u", "role": "test"}'], repo=repo)[0] == 0)
        check("init refuses a format other than 1", call(["init"], json.dumps(fresh(format=2)), repo)[0] == 2)

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
        check("move-aside named once, as an earlier run's", len(a) == 2 and a[0] == "seeded"
              and a[1].endswith(stale[0]) and "an earlier run left" in a[1])

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
              and "moved aside unread, as" in a[-1] and a[-1].endswith(moved[0]))

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
        ra, rb = mk("dw-impl-review-a"), mk("dw-impl-review-b")
        call(["set", "files.review_file", json.dumps(ra)], repo=repo)
        code, out = call(["set", "files.review_file", json.dumps(rb)], repo=repo)
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
        call(["set", "writers", json.dumps([{"unit": "u", "reports": [rep]}]), "files.failure_file", json.dumps(rep)],
             repo=repo)
        code, out = call(["set", "files.failure_file", "null"], repo=repo)
        check("a file a writers report still names is kept", code == 0 and os.path.exists(rep) and out == "")
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
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) for i in range(24)]
        codes = [p.wait() for p in procs]
        notices = json.load(open(f, encoding="utf-8"))["report"]["notices"]
        check("parallel appends keep every entry", codes == [0] * 24
              and sorted(notices) == sorted("n%d" % i for i in range(24)))

        # input as UTF-8 under a C locale, UTF-8 mode off: argv and stdin
        env = dict(os.environ, LC_ALL="C", LANG="C", PYTHONUTF8="0", PYTHONIOENCODING="")
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
        r = subprocess.run([sys.executable, me, "--repo", repo, "set", "branch", b'"\xff"'], capture_output=True)
        check("invalid UTF-8 in argv exits 2, the file unchanged", r.returncode == 2
              and b"Traceback" not in r.stderr and open(f, "rb").read() == before)
        r = subprocess.run([sys.executable, me, "--repo", repo, "read", b"files.\xff"], capture_output=True)
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
        files = {m: None for m in dict(KEYS)["files"]}
        files.update({"plan_file": plan, "summary_file": summ, "baseline_file": kept, "review_file": user})
        call(["set", "files", json.dumps(files),
              "writers", json.dumps([{"unit": "u", "status": "done", "reports": [report]}]),
              "patches", json.dumps([{"path": patch, "temp": True, "outcome": "applied"},
                                     {"path": user, "temp": False, "outcome": "refused"}])], repo=repo)
        code, out = call(["remove", "--keep", kept], repo=repo)
        check("remove succeeds", code == 0 and not os.path.exists(f))
        check("remove takes the temp files", not any(os.path.exists(p) for p in (plan, summ, report, patch)))
        check("remove keeps a --keep path", os.path.exists(kept))
        check("remove leaves a non-temp path", os.path.exists(user) and "left: %s" % user in out)
        check("stale file survives remove", len([n for n in os.listdir(here) if STALE_RE.match(n)]) == 1)
        check("remove with no file is a no-op", call(["remove"], repo=repo)[0] == 0)

        # writers' reports and reviews' diff and return files: set and remove take them like a files member
        wr1, wr2 = mk("dw-impl-wreport-1"), mk("dw-impl-wreport-2")
        rd1, rr1, rd2, rr2 = (mk("dw-impl-rdiff-1"), mk("dw-impl-rret-1"),
                              mk("dw-impl-rdiff-2"), mk("dw-impl-rret-2"))
        call(["init"], json.dumps(fresh()), repo)
        call(["set", "writers", json.dumps([{"unit": "u", "reports": [wr1, wr2]}]),
              "reviews", json.dumps([{"scope": "piece:p", "diff_file": rd1, "return_file": rr1, "verdict": None},
                                     {"scope": "overall", "diff_file": rd2, "return_file": rr2, "verdict": None}])],
             repo=repo)
        code, out = call(["set", "writers", json.dumps([{"unit": "u", "reports": [wr1]}])], repo=repo)
        check("a set of writers that drops a report removes it", code == 0 and not os.path.exists(wr2)
              and os.path.exists(wr1) and "removed: %s" % wr2 in out)
        code, out = call(["set", "reviews", json.dumps([{"scope": "overall", "diff_file": rd2,
                                                          "return_file": rr2, "verdict": None}])], repo=repo)
        check("a set of reviews that drops an entry removes its files", code == 0 and not os.path.exists(rd1)
              and not os.path.exists(rr1) and os.path.exists(rd2) and os.path.exists(rr2)
              and "removed: %s" % rd1 in out and "removed: %s" % rr1 in out)
        code, out = call(["remove", "--keep", wr1], repo=repo)
        check("remove takes a review's files and keeps a writers report named --keep", code == 0
              and not os.path.exists(rd2) and not os.path.exists(rr2) and os.path.exists(wr1)
              and "kept: %s" % wr1 in out)

        # init --recover with no file: the line it appends says so, and that nothing was moved aside
        code, out = call(["init", "--recover"], json.dumps(fresh()), repo)
        a = json.load(open(f, encoding="utf-8"))["assumptions"]
        check("--recover with no file names the rebuild, nothing moved aside", code == 0
              and "moved aside:" not in out and len(a) == 2 and "This run's run-state file" in a[-1]
              and "none was moved aside" in a[-1])

        # set into a list entry's member
        call(["set", "writers", json.dumps([{"unit": "a", "status": None}, {"unit": "b", "status": None}])],
             repo=repo)
        code, _ = call(["set", "writers.-1.status", '"done"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set into the last list entry's member", code == 0 and d["writers"][-1]["status"] == "done"
              and d["writers"][0]["status"] is None)
        check("set refuses a list entry the file lacks", call(["set", "writers.5.status", '"x"'], repo=repo)[0] == 2)

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
    try:
        run(utf8_argv(argv), sys.stdin, sys.stdout.buffer)
        return 0
    except Fail as e:
        sys.stderr.write("run-state.py: %s\n" % e)
        return e.code
    except UnicodeError as e:
        sys.stderr.write("run-state.py: input is not UTF-8, nothing written: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""run-state.py -- /implement's run-state file: create it, open a phase, set, append, read, remove.

The file is `$(git rev-parse --git-path dev-workflows/implement-run.json)` in the code repository
the run works in: per worktree, inside the git directory, never staged. `/implement` Phase 1.4
creates it and every later phase opens with `open`; commands/implement.md says what each key holds
and where it is written. Run every call from the working directory (or pass --repo <dir>). One
`/implement` run per worktree at a time is the precondition; the lock below serialises one run's own
calls, never two runs.

  run-state.py init [--recover]      the whole object, as JSON on stdin, holding every key in KEYS
                                     and no other -- checked before anything is moved. A file
                                     already there is moved aside unread, as
                                     implement-run.json.stale-<UTC stamp>, after any older such file
                                     is removed, so at most one is kept; the move is printed and
                                     appended to `assumptions` -- as a file an earlier run left, or,
                                     under --recover, as this run's own file that did not parse.
  run-state.py open <phase>          set `phase` and print the file.
  run-state.py read [<key>]          print the file, or one key, changing nothing.
  run-state.py set <key> <json> ...  set each key to its JSON value; with no pairs, a JSON object of
                                     key: value on stdin. Several keys are written in one replace.
  run-state.py append <key> <json> ...  append each value to its key's list, or a JSON object on
                                     stdin; a key that is null becomes a one-element list.
  run-state.py remove [--keep <path>] ...
                                     the end-of-run removal: every temp file `files` names, each
                                     `step_groups` report and each `patches` path marked `temp`
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
  2  usage: bad arguments, a value that does not parse, input that is not UTF-8, a path through
     null, no such list entry
  3  a key the file does not hold (set, append, read), or an init object lacking or adding a key
  4  the file could not be reached: an OSError reading or writing it -- an unreadable directory on
     its path included -- or git failing to name it
  5  the run-state file is there and does not parse
Standard library only; `python3 run-state.py --selftest` runs the tests.
"""
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

# Every key init requires, and no other: top-level keys, and the members of the objects whose
# members a call may name. commands/implement.md quotes this list (KEYS_LINE); the selftest holds
# the two equal.
KEYS = [
    ("format", None), ("phase", None), ("mode", None), ("key", None), ("source", None),
    ("focus_key", None), ("unit_key", None), ("workitem_key", None), ("unit_folder", None),
    ("run_flags", None), ("specs_git", None),
    ("spec_context", ["spec_paths", "in_scope_ids", "applicable_spec", "applicable_ard",
                      "ard_paths", "companion_run", "tasks_only"]),
    ("task_shape", None), ("clarifications", ["settled", "answers"]),
    ("routing", ["block", "history"]), ("class", None), ("coding_model", None),
    ("branch_answer", ["answer", "moves", "lines"]), ("branch", None), ("stash_ref", None),
    ("pre_existing_dirty", None), ("session_branch_lift", None), ("test_decision", None),
    ("clean_finish", None),
    ("files", ["task_description_file", "plan_file", "summary_file", "baseline_file",
               "test_diff_file", "review_diff_file", "partial_diff_file", "review_file",
               "claims_file", "failure_file"]),
    ("step_groups", None), ("patches", None), ("triage", None),
    ("conformance", ["summary", "annotated", "gaps", "handoff_line"]),
    ("other_repo_changes", None), ("assumptions", None), ("deferred", None),
    ("report", ["commands_run", "maintenance", "notices", "phase1_tasks", "confirmed_cause"]),
    ("code_repo_outcome", None), ("replans_used", None),
]
KEYS_LINE = " ".join(k + ("{%s}" % " ".join(m) if m else "") for k, m in KEYS)


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


def check_keys(d):
    """Every KEYS key and member present, and no other, in an init object."""
    want = [k for k, _ in KEYS]
    missing = [k for k in want if k not in d]
    extra = [k for k in d if k not in want]
    for k, members in KEYS:
        if members and isinstance(d.get(k), dict):
            missing += ["%s.%s" % (k, m) for m in members if m not in d[k]]
            extra += ["%s.%s" % (k, m) for m in d[k] if m not in members]
        elif members and k in d:
            raise Fail(3, "init: %s must be an object holding %s" % (k, ", ".join(members)))
    if missing or extra:
        raise Fail(3, "init: the object %s" % "; ".join(
            x for x in ("lacks " + ", ".join(missing) if missing else "",
                        "holds unknown " + ", ".join(extra) if extra else "") if x))


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
                raise Fail(2, "%s: no list entry %s" % (key, u))
            if last:
                return o, idx
            o = o[idx]
        elif isinstance(o, dict):
            if u not in o:
                raise Fail(3, "%s: the run-state file holds no key %s" % (key, here))
            if last:
                return o, u
            o = o[u]
        else:
            raise Fail(2, "%s: %s is %s -- write that key whole" % (key, ".".join(parts[:i]), json.dumps(o)))
        if o is None:
            raise Fail(2, "%s: %s is null -- write that key whole" % (key, here))


def pairs(args, stdin, verb):
    if args:
        if len(args) % 2:
            raise Fail(2, "%s takes <key> <json> pairs" % verb)
        return [(args[i], parse(args[i + 1], "the value for %s" % args[i])) for i in range(0, len(args), 2)]
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
    if not isinstance(d, dict) or d.get("format") != 1:
        raise Fail(2, "init reads the whole object, with format 1, on stdin")
    check_keys(d)
    if not isinstance(d.get("assumptions"), list):
        raise Fail(2, "init: assumptions must be a list")
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with locked(f):
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
                d["assumptions"].append("This run's run-state file could not be read back, moved aside unread and written again: %s" % s)
            else:
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


def cmd_set(f, args, stdin):
    todo = pairs(args, stdin, "set")
    require(f)
    with locked(f):
        d = load(f)
        for key, v in todo:
            o, k = resolve(d, key)
            o[k] = v
        save(f, d)


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
        for g in d.get("step_groups") or []:
            if isinstance(g, dict) and isinstance(g.get("report"), str):
                paths.append(g["report"])
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
            cmd_set(f, args, stdin)
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

    def call(argv, stdin="", repo=None):
        out = io.BytesIO()
        try:
            run((["--repo", repo] if repo else []) + argv, io.StringIO(stdin), out)
            code = 0
        except Fail as e:
            code = e.code
        return code, out.getvalue().decode("utf-8")

    def fresh(**over):
        d = {}
        for k, members in KEYS:
            d[k] = {m: None for m in members} if members else None
        d.update({"format": 1, "phase": "Phase 1.4", "assumptions": ["seeded"], "deferred": [],
                  "patches": [], "step_groups": [], "triage": []})
        d["files"]["plan_file"] = None
        d["report"].update({"commands_run": [], "notices": []})
        d.update(over)
        return d

    me = os.path.abspath(__file__)
    impl = os.path.join(os.path.dirname(os.path.dirname(me)), "commands", "implement.md")
    if os.path.isfile(impl):
        quoted = re.findall(r"run-state\.py init` requires, and no other: `([^`]+)`", open(impl, encoding="utf-8").read())
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
        check("init keeps the seeded assumptions", json.load(open(f, encoding="utf-8"))["assumptions"] == ["seeded"])
        check("init refuses a non-object", call(["init"], "[1]", repo)[0] == 2)

        # init validates before it moves anything aside
        bad = fresh()
        del bad["deferred"]
        before = sorted(os.listdir(here))
        code, _ = call(["init"], json.dumps(bad), repo)
        check("init refuses a missing key, moving nothing", code == 3 and sorted(os.listdir(here)) == before)
        bad = fresh(defered=[])
        check("init refuses an unknown key", call(["init"], json.dumps(bad), repo)[0] == 3)
        bad = fresh()
        del bad["files"]["baseline_file"]
        check("init refuses a missing member", call(["init"], json.dumps(bad), repo)[0] == 3)

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
        check("--recover names this run's own file", code == 0 and "This run's run-state file" in a[-1]
              and "earlier run" not in a[-1])

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
        code, _ = call(["set", "class", '"SIGNIFICANT"', "files.plan_file", '"/tmp/dw-impl-plan-x"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("set takes several pairs", code == 0 and d["class"] == "SIGNIFICANT"
              and d["files"]["plan_file"] == "/tmp/dw-impl-plan-x")
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
        files.update({"plan_file": plan, "summary_file": summ, "test_diff_file": kept, "review_file": user})
        call(["set", "files", json.dumps(files),
              "step_groups", json.dumps([{"steps": [1], "status": "done", "report": report}]),
              "patches", json.dumps([{"path": patch, "temp": True, "outcome": "applied"},
                                     {"path": user, "temp": False, "outcome": "refused"}])], repo=repo)
        code, out = call(["remove", "--keep", kept], repo=repo)
        check("remove succeeds", code == 0 and not os.path.exists(f))
        check("remove takes the temp files", not any(os.path.exists(p) for p in (plan, summ, report, patch)))
        check("remove keeps a --keep path", os.path.exists(kept))
        check("remove leaves a non-temp path", os.path.exists(user) and "left: %s" % user in out)
        check("stale file survives remove", len([n for n in os.listdir(here) if STALE_RE.match(n)]) == 1)
        check("remove with no file is a no-op", call(["remove"], repo=repo)[0] == 0)
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

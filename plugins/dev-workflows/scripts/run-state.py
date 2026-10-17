#!/usr/bin/env python3
"""run-state.py -- /implement's run-state file: create it, open a phase, set, append, read, remove.

The file is `$(git rev-parse --git-path dev-workflows/implement-run.json)` in the code repository
the run works in: per worktree, inside the git directory, never staged. `/implement` Phase 1.4
creates it and every later phase opens with `open`; commands/implement.md says what each key holds
and where it is written. Run every call from the working directory (or pass --repo <dir>).

  run-state.py init                  the whole object, as JSON on stdin. A file an earlier run left
                                     is moved aside unread, as implement-run.json.stale-<UTC stamp>,
                                     after any older such file is removed, so at most one is kept;
                                     the move is printed and appended to `assumptions`.
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
its index (`triage.-1.followed_by`, the last entry's). A path through a null value is refused: write
that key whole. Every write replaces the file whole (a temp file beside it, then os.replace), so a
write is never half done; a value that does not parse changes nothing. The file is UTF-8 with
non-ASCII text written as itself (ensure_ascii=False), so a path comes back as git's -z record gave
it; JSON still escapes `"` and `\\`, so `\\"` and `\\\\` in what `open` and `read` print are one
character each.

Exit 0: done. Exit 1: there is no run-state file to read or change. Exit 2: usage, a value that does
not parse, a key that does not resolve, or a git failure. Standard library only;
`python3 run-state.py --selftest` runs the tests.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

REL = "dev-workflows/implement-run.json"
STALE_RE = re.compile(r"^implement-run\.json\.stale-\d{8}T\d{6}Z$")
TEMP_PREFIX = "dw-impl-"


class Fail(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code


def state_path(repo):
    try:
        out = subprocess.run(["git", "-C", repo, "rev-parse", "--git-path", REL],
                             capture_output=True, text=True)
    except OSError as e:
        raise Fail(2, "git could not run: %s" % e)
    if out.returncode != 0:
        raise Fail(2, "git rev-parse --git-path failed: %s" % out.stderr.strip())
    p = out.stdout.rstrip("\n")
    return p if os.path.isabs(p) else os.path.join(os.path.abspath(repo), p)


def guarded(path):
    """True only for the run-state file's own path, as git names it."""
    return (os.path.basename(path) == "implement-run.json"
            and os.path.basename(os.path.dirname(path)) == "dev-workflows")


def load(f):
    if not os.path.isfile(f):
        raise Fail(1, "no run-state file at %s" % f)
    try:
        with open(f, encoding="utf-8") as r:
            d = json.load(r)
    except ValueError as e:
        raise Fail(2, "the run-state file at %s does not parse: %s" % (f, e))
    if not isinstance(d, dict):
        raise Fail(2, "the run-state file at %s is not a JSON object" % f)
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


def resolve(d, key):
    """(container, final key) for a dotted key, refusing a path through null."""
    parts = key.split(".")
    o = d
    for i, u in enumerate(parts[:-1]):
        if isinstance(o, list):
            try:
                o = o[int(u)]
            except (ValueError, IndexError):
                raise Fail(2, "%s: no list entry %s" % (key, u))
        elif isinstance(o, dict):
            if u not in o:
                raise Fail(2, "%s: no key %s" % (key, ".".join(parts[:i + 1])))
            o = o[u]
        else:
            raise Fail(2, "%s: %s is %s -- write that key whole" % (key, ".".join(parts[:i + 1]), json.dumps(o)))
        if o is None:
            raise Fail(2, "%s: %s is null -- write that key whole" % (key, ".".join(parts[:i + 1])))
    k = parts[-1]
    if isinstance(o, list):
        try:
            k = int(k)
            o[k]
        except (ValueError, IndexError):
            raise Fail(2, "%s: no list entry %s" % (key, parts[-1]))
    return o, k


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


def cmd_init(f, stdin, out):
    d = parse(stdin.read(), "stdin")
    if not isinstance(d, dict) or d.get("format") != 1:
        raise Fail(2, "init reads the whole object, with format 1, on stdin")
    os.makedirs(os.path.dirname(f), exist_ok=True)
    if os.path.exists(f):
        here = os.path.dirname(f)
        for name in os.listdir(here):
            old = os.path.join(here, name)
            if STALE_RE.match(name) and os.path.isfile(old) and not os.path.islink(old):
                os.unlink(old)
        s = "%s.stale-%s" % (f, time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
        os.replace(f, s)
        out.write(("moved aside: %s\n" % s).encode("utf-8"))
        line = "Run-state file an earlier run left, moved aside unread: %s" % s
        if d.get("assumptions") is None:
            d["assumptions"] = [line]
        elif isinstance(d["assumptions"], list):
            d["assumptions"].append(line)
        else:
            raise Fail(2, "init: assumptions must be a list or null")
    save(f, d)
    out.write(("created: %s\n" % f).encode("utf-8"))


def cmd_open(f, args, out):
    if len(args) != 1:
        raise Fail(2, "open takes the phase's name, as its heading names it")
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
        if isinstance(o, dict) and k not in o:
            raise Fail(2, "%s: no such key" % args[0])
        emit(out, o[k])
    else:
        raise Fail(2, "read takes at most one key")


def cmd_set(f, args, stdin):
    d = load(f)
    for key, v in pairs(args, stdin, "set"):
        o, k = resolve(d, key)
        o[k] = v
    save(f, d)


def cmd_append(f, args, stdin):
    d = load(f)
    for key, v in pairs(args, stdin, "append"):
        o, k = resolve(d, key)
        cur = o.get(k) if isinstance(o, dict) else o[k]
        if cur is None:
            o[k] = [v]
        elif isinstance(cur, list):
            cur.append(v)
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
        raise Fail(2, "refusing to remove %s: not the run-state file's path" % f)
    if not os.path.exists(f):
        out.write(("no run-state file at %s -- nothing to remove\n" % f).encode("utf-8"))
        return
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
    f = state_path(repo)
    if verb == "init" and not args:
        cmd_init(f, stdin, out)
    elif verb == "open":
        cmd_open(f, args, out)
    elif verb == "read":
        cmd_read(f, args, out)
    elif verb == "set":
        cmd_set(f, args, stdin)
    elif verb == "append":
        cmd_append(f, args, stdin)
    elif verb == "remove":
        cmd_remove(f, args, out)
    else:
        raise Fail(2, "unknown subcommand %s" % verb)


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

    base = {"format": 1, "phase": "Phase 1.4", "class": None, "test_decision": None,
            "files": {"plan_file": None, "summary_file": None}, "patches": [],
            "step_groups": [], "triage": [], "assumptions": ["seeded"], "deferred": [],
            "pre_existing_dirty": None}
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "r [x] q")
        subprocess.run(["git", "init", "-q", repo], check=True)
        subprocess.run(["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@t",
                        "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify",
                        "--allow-empty", "-m", "x"], check=True)
        f = state_path(repo)
        check("path is the git path", f.endswith(os.path.join(".git", "dev-workflows", "implement-run.json")))

        check("open with no file exits 1", call(["open", "Phase 1.5"], repo=repo)[0] == 1)
        code, out = call(["init"], json.dumps(base), repo)
        check("init creates", code == 0 and os.path.isfile(f) and "moved aside" not in out)
        check("init keeps the seeded assumptions", json.load(open(f, encoding="utf-8"))["assumptions"] == ["seeded"])
        check("init refuses a non-object", call(["init"], "[1]", repo)[0] == 2)

        # stale move-aside: at most one kept, and an unrelated name left alone
        here = os.path.dirname(f)
        open(os.path.join(here, "implement-run.json.stale-notes.txt"), "w").close()
        for old in ("implement-run.json.stale-20200101T000000Z", "implement-run.json.stale-20210101T000000Z"):
            open(os.path.join(here, old), "w").close()
        code, out = call(["init"], json.dumps(base), repo)
        stale = sorted(n for n in os.listdir(here) if STALE_RE.match(n))
        check("init moves the file aside", code == 0 and "moved aside: " in out)
        check("one stale file kept, the older ones removed", len(stale) == 1 and stale[0] not in (
            "implement-run.json.stale-20200101T000000Z", "implement-run.json.stale-20210101T000000Z"))
        check("unrelated stale-named file left", os.path.exists(os.path.join(here, "implement-run.json.stale-notes.txt")))
        a = json.load(open(f, encoding="utf-8"))["assumptions"]
        check("move-aside named once in assumptions", len(a) == 2 and a[0] == "seeded"
              and a[1].endswith(stale[0]) and "moved aside unread" in a[1])

        # open sets phase and prints
        code, out = call(["open", "Phase 1.5"], repo=repo)
        check("open sets phase", code == 0 and json.loads(out)["phase"] == "Phase 1.5"
              and json.load(open(f, encoding="utf-8"))["phase"] == "Phase 1.5")

        # non-ASCII and a path holding " and \ round-trip, written as UTF-8
        weird = 'dir/ünï cöde "q" b\\c.txt'
        entry = [{"path": weird, "fingerprint": "abc", "status": "??"}]
        code, _ = call(["set", "pre_existing_dirty", json.dumps(entry, ensure_ascii=False)], repo=repo)
        raw = open(f, encoding="utf-8").read()
        check("non-ASCII written as itself", code == 0 and "ünï cöde" in raw and "\\u00fc" not in raw)
        check("quote and backslash escaped in the file", '\\"q\\" b\\\\c' in raw)
        code, out = call(["read", "pre_existing_dirty"], repo=repo)
        check("path reads back unchanged", code == 0 and json.loads(out)[0]["path"] == weird)

        # multi-key set: argv pairs and a stdin object, dotted keys, list index
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

        # append: onto null, onto a list, into a list entry
        code, _ = call(["append", "deferred", '"one"', "deferred", '"two"'], repo=repo)
        code2, _ = call(["append", "conformance_gaps", '"g"'], repo=repo)
        call(["set", "code_repo_outcome", "null"], repo=repo)
        code3, _ = call(["append", "code_repo_outcome", '"line"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("append onto a list", code == 0 and d["deferred"] == ["one", "two"])
        check("append onto a missing key", code2 == 0 and d["conformance_gaps"] == ["g"])
        check("append onto null makes a one-element list", code3 == 0 and d["code_repo_outcome"] == ["line"])
        call(["append", "triage", json.dumps({"pass": "first", "followed_by": None})], repo=repo)
        code, _ = call(["append", "triage.-1.followed_by", '"review-fixer pass"'], repo=repo)
        d = json.load(open(f, encoding="utf-8"))
        check("append into the last list entry", code == 0 and d["triage"][-1]["followed_by"] == ["review-fixer pass"])
        check("append refuses a non-list", call(["append", "class", '"x"'], repo=repo)[0] == 2)
        code, out = call(["read", "triage.0.pass"], repo=repo)
        check("read a list entry's member", code == 0 and json.loads(out) == "first")

        # guarded remove: temp files named, a --keep path, a non-temp path left, then the file
        def mk(name):
            p = os.path.join(tmp, name)
            open(p, "w").close()
            return p
        plan, summ, kept = mk("dw-impl-plan-1"), mk("dw-impl-summary-1"), mk("dw-impl-diff-1")
        report, patch, user = mk("dw-impl-step-1"), mk("dw-impl-patch-1"), mk("notes.md")
        call(["set", "files", json.dumps({"plan_file": plan, "summary_file": summ, "test_diff_file": kept,
                                           "review_file": user, "claims_file": None}),
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
        run(argv, sys.stdin, sys.stdout.buffer)
        return 0
    except Fail as e:
        sys.stderr.write("run-state.py: %s\n" % e)
        return e.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

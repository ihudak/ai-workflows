#!/usr/bin/env python3
"""Tree snapshot: read what a git work tree holds uncommitted, before and after a step, and compare.

Usage:
  tree-snapshot.py snapshot --dir <dir> [--path <path relative to dir>]
  tree-snapshot.py compare <before.json> <after.json>
  tree-snapshot.py --selftest

snapshot prints one JSON object: {"dir", "top", "prefix", "records": [{"xy", "paths"}],
"fingerprints": {path: sha|"-"}, "in_head": {path: bool}}. It reads `git status --porcelain -z
--untracked-files=all` limited to --path, or to <dir> itself, and every path is relative to <dir>.
A rename record whose other path lies outside <dir> keeps it, written with "../". A fingerprint is
`hash-object --no-filters` of the file, the hash of the link text for a symlink, and "-" for anything else.
in_head says whether HEAD holds the path.

compare prints {"paths": [{"path", "before_xy", "after_xy", "before_fp", "after_fp", "in_head",
"changed", "clean_before", "created"}]}, one entry per path in either snapshot, sorted by path.
before_xy is null where the path had no record before; clean_before is "no record before and HEAD holds
it"; created is "no record before, HEAD does not hold it, a record after"; changed is "the record or the
fingerprint differs". A path with no record on either side is not listed.

Path bytes are decoded with surrogateescape and printed as UTF-8, a lone surrogate as a \\udcXX escape.
Exit codes: 0 done; 2 cannot run (not a git work tree, bad arguments, an unreadable or malformed
snapshot file, any other failure).
Standard library only; every git call is `git --no-optional-locks -C <dir>` with :(literal) pathspecs.
"""

import argparse
import io
import json
import os
import posixpath
import shutil
import subprocess
import sys
import tempfile


class CannotRun(Exception):
    pass


def git(directory, *args, data=None):
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", directory, *args],
        input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def text(raw):
    return raw.decode("utf-8", errors="surrogateescape")


def emit(obj):
    out = json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
    sys.stdout.flush()
    sys.stdout.buffer.write(out.encode("utf-8", errors="backslashreplace"))
    sys.stdout.buffer.flush()


def fingerprint(directory, path):
    full = os.path.join(directory, path)
    if os.path.islink(full):
        try:
            target = os.readlink(full)
        except OSError:
            # The link vanished or changed kind between the test and the read.
            return "-"
        r = git(directory, "hash-object", "--stdin", data=os.fsencode(target))
    elif os.path.isfile(full):
        r = git(directory, "hash-object", "--no-filters", "--", path)
    else:
        return "-"
    return text(r.stdout).strip() if r.returncode == 0 and r.stdout.strip() else "-"


def parse_status(raw):
    parts = raw.split(b"\0")
    if parts and parts[-1] == b"":
        parts.pop()
    records, i = [], 0
    while i < len(parts):
        rec = parts[i]
        xy, paths = text(rec[:2]), [text(rec[3:])]
        i += 1
        if ("R" in xy or "C" in xy) and i < len(parts):
            paths.append(text(parts[i]))
            i += 1
        records.append({"xy": xy, "paths": paths})
    return records


def snapshot(directory, path=None):
    directory = os.path.abspath(directory)
    top = git(directory, "rev-parse", "--show-toplevel")
    if top.returncode != 0:
        raise CannotRun("not a git work tree: " + directory)
    prefix = text(git(directory, "rev-parse", "--show-prefix").stdout)
    prefix = prefix[:-1] if prefix.endswith("\n") else prefix
    spec = ":(literal)" + (path if path else ".")
    st = git(directory, "status", "--porcelain", "-z", "--untracked-files=all", "--", spec)
    if st.returncode != 0:
        raise CannotRun("git status failed: " + text(st.stderr).strip())
    base = prefix.rstrip("/") or "."
    records = parse_status(st.stdout)
    for rec in records:
        # Both sides absolute, so relpath never reads the process's working directory.
        rec["paths"] = [posixpath.relpath("/" + p, "/" + base) for p in rec["paths"]]
    fps, in_head = {}, {}
    for rec in records:
        for p in rec["paths"]:
            if p in fps:
                continue
            fps[p] = fingerprint(directory, p)
            in_head[p] = git(directory, "cat-file", "-e", "HEAD:./" + p).returncode == 0
    return {"dir": directory, "top": text(top.stdout).rstrip("\n"), "prefix": prefix,
            "records": records, "fingerprints": fps, "in_head": in_head}


def xy_map(snap):
    # A rename record names two paths; each carries the record's code.
    out = {}
    for rec in snap["records"]:
        for p in rec["paths"]:
            out[p] = rec["xy"]
    return out


def compare(before, after):
    bx, ax = xy_map(before), xy_map(after)
    bf, af = before["fingerprints"], after["fingerprints"]
    paths = []
    for p in sorted(set(bx) | set(ax)):
        b_xy, a_xy = bx.get(p), ax.get(p)
        head = before["in_head"].get(p, after["in_head"].get(p, False))
        paths.append({
            "path": p, "before_xy": b_xy, "after_xy": a_xy,
            "before_fp": bf.get(p), "after_fp": af.get(p), "in_head": head,
            "changed": b_xy != a_xy or bf.get(p) != af.get(p),
            "clean_before": b_xy is None and head,
            "created": b_xy is None and not head and a_xy is not None,
        })
    return {"paths": paths}


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            snap = json.load(fh)
    except (OSError, ValueError) as e:
        raise CannotRun("unreadable snapshot %s: %s" % (path, e))
    ok = (isinstance(snap, dict) and isinstance(snap.get("records"), list)
          and isinstance(snap.get("fingerprints"), dict) and isinstance(snap.get("in_head"), dict)
          and all(isinstance(r, dict) and isinstance(r.get("xy"), str) and isinstance(r.get("paths"), list)
                  and all(isinstance(p, str) for p in r["paths"]) for r in snap["records"]))
    if not ok:
        raise CannotRun("malformed snapshot %s: not the shape snapshot prints" % path)
    return snap


# ---------------------------------------------------------------- selftest

def selftest():
    failures = []

    def check(name, ok, detail=""):
        if not ok:
            failures.append(name + (": " + str(detail) if detail else ""))

    def sh(cwd, *args):
        r = subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com",
                            "-c", "commit.gpgsign=false", "-C", cwd, *args],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode != 0:
            raise RuntimeError("git %s: %s" % (args, r.stderr))
        return r.stdout

    def put(root, rel, content=b"x\n"):
        full = os.path.join(root, rel)
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(content)

    def sha(root, rel):
        return text(sh(root, "hash-object", "--no-filters", "--", rel)).strip()

    def byfile(snap):
        return {p: rec["xy"] for rec in snap["records"] for p in rec["paths"]}

    def cli(*args):
        r = subprocess.run([sys.executable, os.path.abspath(__file__), *args],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return r.returncode, r.stdout.decode("utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "repo")
        os.makedirs(repo)
        sh(repo, "init", "-q")
        for f in ("tracked.txt", "dirty.txt", "gone.txt", "old.txt", "sub/in.txt", "sub/in2.txt"):
            put(repo, f, b"base " + f.encode() + b"\n")
        put(repo, ".gitignore", b"ignored.log\n")
        os.symlink("tracked.txt", os.path.join(repo, "link"))
        sh(repo, "add", "-A")
        sh(repo, "commit", "-q", "-m", "base")

        # Records and fingerprints.
        put(repo, "tracked.txt", b"changed\n")
        put(repo, "newdir/deep/n.txt", b"new\n")
        os.remove(os.path.join(repo, "gone.txt"))
        s = snapshot(repo)
        m = byfile(s)
        check("modified record", m.get("tracked.txt") == " M", m)
        check("untracked in untracked dir", m.get("newdir/deep/n.txt") == "??", m)
        check("deleted record", m.get("gone.txt") == " D", m)
        check("modified fp", s["fingerprints"]["tracked.txt"] == sha(repo, "tracked.txt"))
        check("untracked fp", s["fingerprints"]["newdir/deep/n.txt"] == sha(repo, "newdir/deep/n.txt"))
        check("deleted fp", s["fingerprints"]["gone.txt"] == "-")
        check("in_head", s["in_head"]["tracked.txt"] is True and s["in_head"]["newdir/deep/n.txt"] is False)
        check("prefix empty", s["prefix"] == "")
        sh(repo, "checkout", "-q", "--", "tracked.txt", "gone.txt")
        shutil.rmtree(os.path.join(repo, "newdir"))

        # Paths survive byte for byte, through the CLI and compare.
        names = ["with space.txt", 'quo"te.txt', "café.txt", "new\nline.txt", "bad\udcffbyte.txt"]
        try:  # APFS and other UTF-8-only filesystems refuse a non-UTF-8 name (EILSEQ): nothing to test there
            put(tmp, "bad\udcffbyte.txt")
            os.remove(os.path.join(tmp, "bad\udcffbyte.txt"))
            raw_names = True
        except OSError:
            names.remove("bad\udcffbyte.txt")
            raw_names = False
        before_file = os.path.join(tmp, "before.json")
        after_file = os.path.join(tmp, "after.json")
        rc, out = cli("snapshot", "--dir", repo)
        check("cli snapshot rc", rc == 0, rc)
        with open(before_file, "w", encoding="utf-8") as fh:
            fh.write(out)
        for n in names:
            put(repo, n, b"payload " + os.fsencode(n) + b"\n")
        rc, out = cli("snapshot", "--dir", repo)
        with open(after_file, "w", encoding="utf-8") as fh:
            fh.write(out)
        rc, out = cli("compare", before_file, after_file)
        check("cli compare rc", rc == 0, rc)
        got = {e["path"]: e for e in json.loads(out)["paths"]}
        for n in names:
            e = got.get(n)
            check("path survives " + ascii(n), e is not None, sorted(got))
            if e is not None:
                check("created " + ascii(n), e["created"] and e["changed"] and not e["clean_before"], e)
                check("fp " + ascii(n), e["after_fp"] == sha(repo, n), e)
        check("escape only for the non-UTF-8 byte", ("\\udcff" in out) == raw_names and "café" in out and "\\u00e9" not in out)
        for n in names:
            os.remove(os.path.join(repo, n))

        # Renames.
        sh(repo, "mv", "old.txt", "renamed.txt")
        s = snapshot(repo)
        recs = [r for r in s["records"] if "R" in r["xy"]]
        check("rename one record", len(recs) == 1 and sorted(recs[0]["paths"]) == ["old.txt", "renamed.txt"], s["records"])
        check("rename both fingerprinted", set(s["fingerprints"]) >= {"old.txt", "renamed.txt"}
              and s["fingerprints"]["renamed.txt"] != "-" and s["fingerprints"]["old.txt"] == "-", s["fingerprints"])
        sh(repo, "reset", "-q", "--hard")

        # Symlinks: the link text, not the target.
        os.remove(os.path.join(repo, "link"))
        os.symlink("dirty.txt", os.path.join(repo, "link"))
        s = snapshot(repo)
        want = text(subprocess.run(["git", "-C", repo, "hash-object", "--stdin"], input=b"dirty.txt",
                                   stdout=subprocess.PIPE).stdout).strip()
        check("symlink fp is link text", s["fingerprints"].get("link") == want, s["fingerprints"])
        check("symlink fp is not target", s["fingerprints"].get("link") != sha(repo, "dirty.txt"))
        sh(repo, "reset", "-q", "--hard")

        # A subdirectory --dir.
        put(repo, "sub/in.txt", b"edited\n")
        put(repo, "tracked.txt", b"outside edit\n")
        s = snapshot(os.path.join(repo, "sub"))
        check("sub prefix", s["prefix"] == "sub/", s["prefix"])
        check("sub paths stripped and outside unlisted", byfile(s) == {"in.txt": " M"}, byfile(s))
        s = snapshot(os.path.join(repo, "sub"), "in2.txt")
        check("sub --path narrows", byfile(s) == {}, byfile(s))
        sh(repo, "mv", "tracked.txt", "sub/moved.txt")
        s = snapshot(os.path.join(repo, "sub"), "..")
        rn = [r for r in s["records"] if "R" in r["xy"]]
        check("rename other path outside dir keeps ../", rn and sorted(rn[0]["paths"]) == ["../tracked.txt", "moved.txt"], s["records"])
        sh(repo, "reset", "-q", "--hard")

        # A vanished path.
        check("vanished path fp", fingerprint(repo, "never-was.txt") == "-")
        # A symlink that vanishes between the islink test and the readlink.
        real_readlink = os.readlink

        def gone(*a, **k):
            raise FileNotFoundError("vanished")
        os.readlink = gone
        try:
            got_fp = fingerprint(repo, "link")
        except OSError as e:
            got_fp = e
        finally:
            os.readlink = real_readlink
        check("symlink vanished before readlink fp", got_fp == "-", got_fp)

        # git that cannot be started while fingerprinting is a failure (exit 2), never a "-".
        put(repo, "tracked.txt", b"dirty for the start failure\n")
        real_run, real_stdout, real_stderr = subprocess.run, sys.stdout, sys.stderr

        def no_git(cmd, *a, **k):
            if "hash-object" in cmd:
                raise OSError(11, "Resource temporarily unavailable")
            return real_run(cmd, *a, **k)
        subprocess.run = no_git
        sys.stdout, sys.stderr = io.TextIOWrapper(io.BytesIO(), encoding="utf-8"), io.StringIO()
        try:
            got_rc = main(["snapshot", "--dir", repo])
        except Exception as e:
            got_rc = e
        finally:
            subprocess.run, sys.stdout, sys.stderr = real_run, real_stdout, real_stderr
        check("git start failure while fingerprinting exits 2", got_rc == 2, got_rc)
        sh(repo, "checkout", "-q", "--", "tracked.txt")

        # A snapshot run from a deleted working directory.
        gone_cwd = os.path.join(tmp, "gone-cwd")
        os.makedirs(gone_cwd)
        put(repo, "sub/in.txt", b"edited from a deleted cwd\n")
        r = subprocess.run(["sh", "-c", 'cd "$1" && rmdir "$1" && exec "$2" "$3" snapshot --dir "$4"', "sh",
                            gone_cwd, sys.executable, os.path.abspath(__file__), os.path.join(repo, "sub")],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check("deleted cwd rc", r.returncode == 0, (r.returncode, r.stderr[-300:]))
        try:
            got_recs = byfile(json.loads(r.stdout.decode("utf-8")))
        except ValueError as e:
            got_recs = e
        check("deleted cwd paths stripped", got_recs == {"in.txt": " M"}, got_recs)
        # Any other failure exits 2, never 1: a relative --dir cannot be resolved from a deleted cwd.
        os.makedirs(gone_cwd)
        r = subprocess.run(["sh", "-c", 'cd "$1" && rmdir "$1" && exec "$2" "$3" snapshot --dir sub', "sh",
                            gone_cwd, sys.executable, os.path.abspath(__file__)],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check("any other failure exits 2", r.returncode == 2 and r.stdout == b"", (r.returncode, r.stderr[-300:]))
        sh(repo, "reset", "-q", "--hard")

        # Not a work tree and bad input.
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        rc, _ = cli("snapshot", "--dir", plain)
        check("not a work tree exits 2", rc == 2, rc)
        rc, _ = cli("compare", os.path.join(tmp, "nope.json"), before_file)
        check("unreadable snapshot exits 2", rc == 2, rc)
        rc, _ = cli("frobnicate")
        check("bad arguments exit 2", rc == 2, rc)
        for label, bad in (("record not an object", {"records": ["x"], "fingerprints": {}, "in_head": {}}),
                           ("paths not a list", {"records": [{"xy": " M", "paths": "ab"}], "fingerprints": {}, "in_head": {}}),
                           ("xy not a string", {"records": [{"xy": 1, "paths": ["a"]}], "fingerprints": {}, "in_head": {}}),
                           ("fingerprints not an object", {"records": [], "fingerprints": [], "in_head": {}}),
                           ("in_head not an object", {"records": [], "fingerprints": {}, "in_head": None})):
            bad_file = os.path.join(tmp, "bad.json")
            with open(bad_file, "w", encoding="utf-8") as fh:
                json.dump(bad, fh)
            rc, out = cli("compare", bad_file, before_file)
            check("malformed snapshot exits 2: " + label, rc == 2 and out == "", (rc, out[:200]))

        # compare classifies.
        put(repo, "dirty.txt", b"dirty before\n")
        put(repo, "stays.txt", b"untracked before\n")
        sh(repo, "add", "-N", "stays.txt")
        b = snapshot(repo)
        put(repo, "tracked.txt", b"agent edit\n")
        put(repo, "dirty.txt", b"dirty after\n")
        put(repo, "made.txt", b"made\n")
        put(repo, "ignored.log", b"noise\n")
        a = snapshot(repo)
        c = {e["path"]: e for e in compare(b, a)["paths"]}
        e = c["tracked.txt"]
        check("clean tracked edit", e["changed"] and e["clean_before"] and not e["created"], e)
        e = c["dirty.txt"]
        check("further edit of dirty", e["changed"] and not e["clean_before"] and not e["created"], e)
        e = c["stays.txt"]
        check("untouched dirty", not e["changed"] and not e["created"], e)
        e = c["made.txt"]
        check("created untracked", e["created"] and e["changed"] and not e["clean_before"], e)
        check("ignored file absent", "ignored.log" not in c, sorted(c))

    if failures:
        for f in failures:
            print("FAIL " + f, file=sys.stderr)
        return 1
    print("PASS")
    return 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(prog="tree-snapshot.py", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--dir", required=True)
    s.add_argument("--path")
    c = sub.add_parser("compare")
    c.add_argument("before")
    c.add_argument("after")
    args = ap.parse_args(argv)
    try:
        if args.cmd == "snapshot":
            emit(snapshot(args.dir, args.path))
        else:
            emit(compare(load(args.before), load(args.after)))
    except CannotRun as e:
        print("tree-snapshot: " + str(e), file=sys.stderr)
        return 2
    except Exception as e:
        # Every failure is "cannot run": a caller reads exit 2 as "read nothing", never exit 1.
        print("tree-snapshot: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

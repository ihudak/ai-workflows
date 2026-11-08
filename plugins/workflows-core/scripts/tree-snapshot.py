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
Exit codes: 0 done; 2 cannot run (not a git work tree, bad arguments, an unreadable snapshot file).
Standard library only; every git call is `git --no-optional-locks -C <dir>` with :(literal) pathspecs.
"""

import argparse
import json
import os
import posixpath
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
        r = git(directory, "hash-object", "--stdin", data=os.fsencode(os.readlink(full)))
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
        rec["paths"] = [posixpath.relpath(p, base) for p in rec["paths"]]
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
        snap["records"], snap["fingerprints"], snap["in_head"]
        return snap
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise CannotRun("unreadable snapshot %s: %s" % (path, e))


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
        shutil_rm = os.path.join(repo, "newdir")
        for root, dirs, files in os.walk(shutil_rm, topdown=False):
            for fn in files:
                os.remove(os.path.join(root, fn))
            for dn in dirs:
                os.rmdir(os.path.join(root, dn))
        os.rmdir(shutil_rm)

        # Paths survive byte for byte, through the CLI and compare.
        names = ["with space.txt", 'quo"te.txt', "café.txt", "new\nline.txt", "bad\udcffbyte.txt"]
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
        check("escape only for the non-UTF-8 byte", "\\udcff" in out and "café" in out and "\\u00e9" not in out)
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

        # Not a work tree and bad input.
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        rc, _ = cli("snapshot", "--dir", plain)
        check("not a work tree exits 2", rc == 2, rc)
        rc, _ = cli("compare", os.path.join(tmp, "nope.json"), before_file)
        check("unreadable snapshot exits 2", rc == 2, rc)
        rc, _ = cli("frobnicate")
        check("bad arguments exit 2", rc == 2, rc)

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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

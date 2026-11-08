#!/usr/bin/env python3
"""specs-git.py — the deterministic git primitives of workflows-core:specs-repo-git and
workflows-core:phase-handoff, one implementation every command reaches through those references.

The rules are the references'; this script is their plumbing, and a change to either is a change to
both. It loads session-branch.py as a module, so the §2.1 classifier, the §4 step 5 push-scope walk,
§8.1's mode and the git helper exist once. Python standard library only.

  specs-git.py --specs <root> status
  specs-git.py --specs <root> branch-merged --ref <ref> --default-ref <ref>
  specs-git.py --specs <root> branch-key --branch <name> [--key <K>]...
  specs-git.py --specs <root> push-scope --branch <name> [--session-default-ref <ref>]
  specs-git.py --specs <root> mode --default <name>
  specs-git.py owner-repo --repo <path> [--no-alias]
  specs-git.py --selftest

<root> is the specs repository's top level. Nothing here writes the working tree, the index or a
ref. Output is one JSON object on stdout. Exit 0: it ran, whatever it found. Exit 2: it could not
run (usage, not a repository's top level, a ref that does not resolve, an unexpected git failure,
any other exception), printing one "specs-git: not run (...)" line on stderr; the caller reports it
and the run continues.
"""

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS_REPO_GIT = os.path.join(HERE, "..", "references", "specs-repo-git.md")


def _load_session_branch():
    spec = importlib.util.spec_from_file_location("session_branch", os.path.join(HERE, "session-branch.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sb = _load_session_branch()
NotRun = sb.NotRun


def status(root):
    """specs-repo-git §2.1 staging steps 1-2: every path git status reports, sorted into the ARTIFACT
    paths the terminal commit may stage and every OTHER path. Read with -z, whose records are never
    quoted; a rename or copy record carries its original path as a second field, consumed with it."""
    fields = sb.git(root, "status", "--porcelain", "-z", "--untracked-files=all").stdout.decode(
        "utf-8", "surrogateescape").split("\0")
    artifact, other = set(), set()
    i = 0
    while i < len(fields):
        record = fields[i]
        i += 1
        if not record:
            continue
        path = record[3:]
        if "R" in record[:2] or "C" in record[:2]:
            i += 1  # the original path, which is no record of its own
        (artifact if sb.classify(path) else other).add(path)
    return {"artifact": sorted(artifact), "other": sorted(other)}


def _commit(root, ref):
    """The commit <ref> names, or NotRun where it names none."""
    r = sb.git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}", check=False)
    if r.returncode != 0:
        raise NotRun("%s does not resolve to a commit" % ref)
    return sb.text(r)


def _patch_id(root, diff):
    """The first field of git patch-id --stable over <diff>, or None for a diff with no patch id."""
    out = sb.text(sb.git(root, "patch-id", "--stable", data=diff))
    return out.split()[0] if out else None


def branch_merged(root, ref, default_ref):
    """specs-repo-git §3.5's branch-merged: whether the work on <ref> is on <default_ref>. The first
    of the four tests that holds answers merged, with its number; none holding answers unmerged."""
    _commit(root, default_ref)
    _commit(root, ref)
    if sb.git(root, "merge-base", "--is-ancestor", ref, default_ref, check=False).returncode == 0:
        return {"merged": True, "test": 1}
    cherry = sb.text(sb.git(root, "cherry", default_ref, ref)).splitlines()
    merges = sb.text(sb.git(root, "rev-list", "--merges", "%s..%s" % (default_ref, ref)))
    if cherry and all(line.startswith("-") for line in cherry) and not merges:
        return {"merged": True, "test": 2}
    base = sb.text(sb.git(root, "merge-base", ref, default_ref))
    whole = _patch_id(root, sb.git(root, "diff", "--no-renames", base, ref).stdout)
    if whole:
        since = sb.text(sb.git(root, "patch-id", "--stable", data=sb.git(
            root, "log", "-p", "--no-renames", "--no-merges", "%s..%s" % (base, default_ref)).stdout))
        if whole in (line.split()[0] for line in since.splitlines() if line.strip()):
            return {"merged": True, "test": 3}
    if sb.git(root, "diff", "--quiet", base, ref, check=False).returncode == 1:
        tree = sb.git(root, "merge-tree", "--write-tree", default_ref, ref, check=False)
        lines = sb.text(tree).splitlines()
        if tree.returncode == 0 and lines and lines[0] == sb.text(sb.git(root, "rev-parse", default_ref + "^{tree}")):
            return {"merged": True, "test": 4}
    return {"merged": False, "test": None}


# specs-repo-git §2.2's plugin-branch prefixes, in its order; the selftest fails where they differ.
PREFIXES = ("idea", "prd", "ard", "spec", "epics", "design", "ready", "brd", "frames", "kb", "conformance")


def branch_key(branch, keys):
    """specs-repo-git §3.5's branch-key: the key in the run's own set <keys> the branch was named for.
    Resolved against the keys the run already holds, never read out of the name: a key K is a
    candidate where the rest of the name, past its prefix, is K or begins K- or K_; the longest wins."""
    prefix, _, rest = branch.partition("/")
    if not _ or prefix not in PREFIXES:
        return {"plugin_branch": False, "prefix": None, "key": None}
    found = [k for k in keys if rest == k or rest.startswith(k + "-") or rest.startswith(k + "_")]
    return {"plugin_branch": True, "prefix": prefix, "key": max(found, key=len) if found else None}


def _parents(root, sha):
    """How many parents <sha> has: rev-list --parents prints the commit, then each parent."""
    return len(sb.text(sb.git(root, "rev-list", "--parents", "-n", "1", sha)).split()) - 1


def _first_other(root, paths):
    return next((p for p in paths if not sb.classify(p)), None)


def _commit_paths(root, sha):
    return sb.nul_list(sb.git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root", "--no-renames", sha))


def push_scope(root, branch, session_default_ref=None):
    """specs-repo-git §4 step 5's push-scope: whether every commit a push of <branch> to origin would
    publish is a session-file commit. With <session_default_ref>, §8.4's form for the session branch:
    the default branch counts as published, a merge with exactly two parents passes, and the branch's
    whole change against the default branch must name session files only."""
    _commit(root, "refs/heads/" + branch)
    remote = "refs/remotes/origin/" + branch
    base = remote if sb.git(root, "show-ref", "--verify", "-q", remote, check=False).returncode == 0 else None
    head = "refs/heads/" + branch
    if session_default_ref is None:
        commits, bad = sb.push_scope(root, head, base or "--remotes=origin")
        failed = None
        if bad:
            if _parents(root, bad) == 1:
                failed = {"sha": bad, "reason": "paths", "path": _first_other(root, _commit_paths(root, bad))}
            else:
                failed = {"sha": bad, "reason": "merge", "path": None}
        return {"base": base, "commits": commits, "in_scope": failed is None, "failed": failed}
    _commit(root, session_default_ref)
    nots = [base, session_default_ref] if base else ["--remotes=origin"]
    commits = sb.text(sb.git(root, "rev-list", "--reverse", head, "--not", *nots)).split()
    failed = None
    for c in commits:
        parents = _parents(root, c)
        if parents == 2:
            continue
        paths = _commit_paths(root, c)
        if parents != 1:
            failed = {"sha": c, "reason": "merge", "path": None}
        elif not paths or _first_other(root, paths) is not None:
            failed = {"sha": c, "reason": "paths", "path": _first_other(root, paths)}
        if failed:
            break
    if failed is None:
        whole = sb.nul_list(sb.git(root, "diff", "--name-only", "-z", "--no-renames", "%s...%s" % (session_default_ref, head)))
        other = _first_other(root, whole)
        if other is not None:
            merge = sb.text(sb.git(root, "rev-list", "--merges", "-n", "1", head)) or None
            failed = {"sha": merge, "reason": "branch-path", "path": other}
    return {"base": base, "commits": commits, "in_scope": failed is None, "failed": failed}


_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_USER = re.compile(r"^[^/@]+@")


def owner_repo(url, resolve_alias=True, ssh_config=None):
    """phase-handoff §2.6.1's owner-repo: the [HOST/]OWNER/REPO a gh -R call names, from a remote URL.
    The host is kept save github.com; a non-http(s) host other than github.com is resolved through
    ssh -G first, its alias's HostName taken (ssh.github.com is github.com) — skipped where
    <resolve_alias> is false, as specs-repo-git §2.1's <docs-repo-slug> requires. A slug that is not
    OWNER/REPO gives owner_repo null. <ssh_config> is passed to ssh as -F (the selftest's)."""
    if not url:
        return {"url": None, "host": None, "slug": None, "owner_repo": None}
    host = re.sub(r"[:/].*$", "", _USER.sub("", _SCHEME.sub("", url, count=1), count=1), count=1)
    slug = _USER.sub("", _SCHEME.sub("", url, count=1), count=1)
    slug = re.sub(r"^[^/:]+(:[0-9]+)?[/:]", "", slug, count=1)
    slug = re.sub(r"/+$", "", slug, count=1)
    slug = re.sub(r"\.git$", "", slug, count=1)
    if resolve_alias and not url.startswith(("http://", "https://")) and host != "github.com" \
            and re.match(r"^[A-Za-z0-9]", host) and shutil.which("ssh"):
        cmd = ["ssh"] + (["-F", ssh_config] if ssh_config else []) + ["-G", host]
        try:
            out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=10).stdout
        except (OSError, subprocess.TimeoutExpired):
            out = b""
        real = next((line.split()[1] for line in out.decode("utf-8", "replace").splitlines()
                     if len(line.split()) > 1 and line.split()[0] == "hostname"), "")
        if real == "ssh.github.com":
            host = "github.com"
        elif real:
            host = real
    value = slug if host == "github.com" else "%s/%s" % (host, slug)
    return {"url": url, "host": host, "slug": slug,
            "owner_repo": value if re.match(r"^[^/]+/[^/]+$", slug) else None}


def owner_repo_of(repo, resolve_alias=True):
    """owner_repo over <repo>'s origin remote; nulls where it has none."""
    sb.git(repo, "rev-parse", "--git-dir")
    r = sb.git(repo, "remote", "get-url", "origin", check=False)
    return owner_repo(sb.text(r) if r.returncode == 0 else None, resolve_alias)


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is."""

    def error(self, message):
        print("specs-git: not run (%s)" % message, file=sys.stderr)
        sys.exit(2)


def main():
    ap = Parser(description="The deterministic git primitives of specs-repo-git and phase-handoff.")
    ap.add_argument("--specs", help="the specs repository's top level")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("status")
    p = sub.add_parser("branch-merged")
    p.add_argument("--ref", required=True)
    p.add_argument("--default-ref", required=True)
    p = sub.add_parser("branch-key")
    p.add_argument("--branch", required=True)
    p.add_argument("--key", action="append", default=[])
    p = sub.add_parser("push-scope")
    p.add_argument("--branch", required=True)
    p.add_argument("--session-default-ref")
    p = sub.add_parser("owner-repo")
    p.add_argument("--repo", required=True)
    p.add_argument("--no-alias", action="store_true")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    if not a.cmd:
        print("specs-git: not run (a subcommand is required)", file=sys.stderr)
        return 2
    try:
        if a.cmd == "owner-repo":
            print(json.dumps(owner_repo_of(a.repo, not a.no_alias), indent=2))
            return 0
        if not a.specs:
            raise NotRun("--specs is required")
        top = sb.text(sb.git(a.specs, "rev-parse", "--show-toplevel"))
        if os.path.realpath(top) != os.path.realpath(a.specs):
            raise NotRun("%s is not its repository's top level (%s)" % (a.specs, top))
        result = dispatch(a)
    except (NotRun, OSError) as e:
        print("specs-git: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
        return 2
    except Exception as e:  # anything unexpected is "not run" on one line, never a traceback
        print("specs-git: not run (%s: %s)" % (type(e).__name__, " ".join(str(e).split())), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


def dispatch(a):
    if a.cmd == "status":
        return status(a.specs)
    if a.cmd == "branch-merged":
        return branch_merged(a.specs, a.ref, a.default_ref)
    if a.cmd == "branch-key":
        return branch_key(a.branch, a.key)
    if a.cmd == "push-scope":
        return push_scope(a.specs, a.branch, a.session_default_ref)
    raise NotRun("unknown subcommand %s" % a.cmd)


def selftest():
    """Every rule this script carries, on repositories built at run time."""
    failures = []
    count = [0]
    me = os.path.abspath(__file__)
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ.pop("GIT_USER_INITIALS", None)

    def check(ok, what):
        count[0] += 1
        if not ok:
            failures.append(what)

    class Repo:
        def __init__(self, path):
            self.path = path

        def git(self, *args, check=True, env=None):
            r = subprocess.run(["git", "-C", self.path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=dict(os.environ, **(env or {})))
            if check and r.returncode != 0:
                raise AssertionError("git %s: %s" % (" ".join(args), r.stderr.decode("utf-8", "replace")))
            return r.stdout.decode("utf-8", "surrogateescape").strip()

        def write(self, rel, body):
            full = os.path.join(self.path, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8", newline="") as fh:
                fh.write(body)

        def commit_all(self, message):
            self.git("add", "-A")
            self.git("commit", "-q", "-m", message)
            return self.git("rev-parse", "HEAD")

    def new_repo(base, name="repo"):
        path = os.path.join(base, name)
        os.makedirs(path)
        r = Repo(path)
        r.git("init", "-q", "-b", "main")
        r.git("config", "user.email", "t@example.invalid")
        r.git("config", "user.name", "t")
        r.git("config", "commit.gpgsign", "false")
        r.write("README.md", "specs\n")
        r.commit_all("init")
        return r

    def cli(*args, env=None):
        r = subprocess.run([sys.executable, me, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=dict(os.environ, **(env or {})))
        out = r.stdout.decode("utf-8", "replace")
        try:
            got = json.loads(out) if out.strip() else {}
        except ValueError:
            got = {"_stdout": out}
        got["_rc"] = r.returncode
        got["_err"] = r.stderr.decode("utf-8", "replace")
        return got

    def one_not_run_line(got):
        lines = got.get("_err", "").splitlines()
        return got.get("_rc") == 2 and len(lines) == 1 and lines[0].startswith("specs-git: not run (")

    def scenarios_status(tmp):
        r = new_repo(tmp, "status")
        resume = "specifications/PRD-ACME-1-zahlungsauslösung/dev-workflows/resume.md"
        follow = "specifications/PRD-ACME-2-a b/follow-ups.md"
        frames = "specifications/PRD-ACME-3/design/frame-set/index.md"
        shot = "specifications/PRD-ACME-3/Doc screenshots/a.png"
        prd = "specifications/PRD-ACME-3/prd.md"
        reg = "security/web/register.json"
        threat = "security/web/threat-model.md"
        for p in (resume, follow, frames, shot, prd, reg, threat):
            r.write(p, "x\n")
        r.write("dev-workflows-cost/x.md", "cost\n")
        r.git("add", "dev-workflows-cost/x.md")
        r.git("commit", "-q", "-m", "cost")
        r.git("mv", "dev-workflows-cost/x.md", "dev-workflows-cost/y.md")
        got = status(r.path)
        check(set(got["artifact"]) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the artifact list (%r)" % got)
        check("dev-workflows-cost/x.md" not in got["artifact"] + got["other"],
              "status: a rename's original path is no record of its own (%r)" % got)
        check(set(got["other"]) == {frames, shot, prd, threat}, "status: the other list (%r)" % got)
        check(got["artifact"] == sorted(got["artifact"]) and got["other"] == sorted(got["other"]),
              "status: both lists sorted (%r)" % got)
        got = cli("--specs", r.path, "status")
        check(got["_rc"] == 0 and set(got.get("artifact", [])) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the CLI prints the same object (%r)" % got)
        got = cli("--specs", os.path.join(r.path, "specifications"), "status")
        check(one_not_run_line(got) and "_stdout" not in got and "artifact" not in got,
              "a subdirectory is not the top level: exit 2, one line, no JSON (%r)" % got)
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        got = cli("--specs", plain, "status")
        check(one_not_run_line(got), "a directory that is no repository: exit 2, one line (%r)" % got)
        got = cli("status")
        check(one_not_run_line(got), "no --specs: exit 2, one line (%r)" % got)
        got = cli("--specs", r.path, "no-such-subcommand")
        check(one_not_run_line(got), "an unknown subcommand: exit 2, one line (%r)" % got)

    def lines30(changes=None):
        rows = ["line %02d\n" % n for n in range(1, 31)]
        for n, body in (changes or {}).items():
            rows[n - 1] = body
        return "".join(rows)

    def scenarios_branch_merged(tmp):
        def case(name):
            r = new_repo(tmp, "merged-" + name)
            r.write("f.txt", lines30())
            r.commit_all("thirty lines")
            return r

        r = case("ff")
        r.git("switch", "-q", "-c", "prd/A-1-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--ff-only", "prd/A-1-x")
        check(branch_merged(r.path, "prd/A-1-x", "main") == {"merged": True, "test": 1},
              "branch-merged: a fast-forward is test 1")

        r = case("rebase")
        r.git("switch", "-q", "-c", "prd/A-2-x")
        r.write("a.md", "a\n")
        c1 = r.commit_all("a")
        r.write("b.md", "b\n")
        c2 = r.commit_all("b")
        r.git("switch", "-q", "main")
        r.write("other.md", "o\n")
        r.commit_all("other")
        r.git("cherry-pick", c1, c2)
        check(branch_merged(r.path, "prd/A-2-x", "main") == {"merged": True, "test": 2},
              "branch-merged: a rebase merge is test 2 (%r)" % branch_merged(r.path, "prd/A-2-x", "main"))

        r = case("evil-merge")
        r.git("switch", "-q", "-c", "side")
        r.write("s.md", "s\n")
        s1 = r.commit_all("side")
        r.git("switch", "-q", "main")
        r.git("switch", "-q", "-c", "prd/A-3-x")
        r.git("merge", "-q", "--no-ff", "--no-commit", "side")
        r.write("extra.md", "the branch's own change, inside the merge commit\n")
        r.git("add", "extra.md")
        r.git("commit", "-q", "-m", "merge side, with a change of its own")
        r.git("switch", "-q", "main")
        r.git("cherry-pick", s1)
        got = branch_merged(r.path, "prd/A-3-x", "main")
        check(got == {"merged": False, "test": None},
              "branch-merged: a change of its own inside a merge commit is not merged by test 2 (%r)" % got)

        r = case("squash")
        r.git("switch", "-q", "-c", "prd/A-4-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.write("b.md", "b\n")
        r.commit_all("b")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--squash", "prd/A-4-x")
        r.git("commit", "-q", "-m", "squash")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "dirty\n")
        check(branch_merged(r.path, "prd/A-4-x", "main") == {"merged": True, "test": 3},
              "branch-merged: a squash merge is test 3, with a dirty session file in the tree (GIT-B2) (%r)"
              % branch_merged(r.path, "prd/A-4-x", "main"))

        r = case("drift")
        r.git("switch", "-q", "-c", "prd/A-5-x")
        r.write("f.txt", lines30({10: "branch line 10\n"}))
        r.commit_all("line 10")
        r.git("switch", "-q", "main")
        r.write("f.txt", lines30({12: "main line 12\n"}))
        r.commit_all("line 12")
        check(branch_merged(r.path, "prd/A-5-x", "main") == {"merged": False, "test": None},
              "branch-merged: before its squash the drifted branch is unmerged")
        r.git("merge", "-q", "--squash", "prd/A-5-x")
        r.git("commit", "-q", "-m", "squash line 10")
        got = branch_merged(r.path, "prd/A-5-x", "main")
        check(got == {"merged": True, "test": 4}, "branch-merged: GIT-B1's drifted squash is test 4 (%r)" % got)

        r = case("empty")
        r.git("switch", "-q", "-c", "prd/A-6-x")
        check(branch_merged(r.path, "prd/A-6-x", "main") == {"merged": True, "test": 1},
              "branch-merged: a branch with no commit of its own is test 1")
        r.git("commit", "-q", "--allow-empty", "-m", "nothing")
        r.git("switch", "-q", "main")
        got = branch_merged(r.path, "prd/A-6-x", "main")
        check(got == {"merged": False, "test": None}, "branch-merged: an empty change is never merged by 3 or 4 (%r)" % got)

        r = case("open")
        r.git("switch", "-q", "-c", "prd/A-7-x")
        r.write("a.md", "a\n")
        r.commit_all("a")
        r.git("switch", "-q", "main")
        check(branch_merged(r.path, "prd/A-7-x", "main") == {"merged": False, "test": None},
              "branch-merged: open work is unmerged")
        got = cli("--specs", r.path, "branch-merged", "--ref", "prd/A-7-x", "--default-ref", "main")
        check(got["_rc"] == 0 and got.get("merged") is False and "test" in got, "branch-merged: the CLI (%r)" % got)
        got = cli("--specs", r.path, "branch-merged", "--ref", "prd/no-such", "--default-ref", "main")
        check(one_not_run_line(got), "branch-merged: a ref that does not resolve exits 2 (%r)" % got)

    def scenarios_branch_key(tmp):
        cases = [
            ("spec/PRODUCT-1234-2fa-rollout", ["PRODUCT-1234"], "PRODUCT-1234"),
            ("spec/PRODUCT-1234-2fa-rollout", ["PRODUCT-1234", "PRODUCT-1234-2"], "PRODUCT-1234"),
            ("spec/ACME-77-01-checkout", ["ACME-77", "ACME-77-01"], "ACME-77-01"),
            ("ard/EPIC-008-01_slug", ["EPIC-008-01"], "EPIC-008-01"),
            ("prd/ACME-7", ["ACME-7"], "ACME-7"),
            ("prd/ACME-77-x", ["ACME-7"], None),
            ("prd/ACME-7-x", [], None),
        ]
        for branch, keys, want in cases:
            got = branch_key(branch, keys)
            check(got["plugin_branch"] is True and got["key"] == want,
                  "branch-key: %s with %r resolves to %r (%r)" % (branch, keys, want, got))
        got = branch_key("kb/harvest-2026-11-08", ["ACME-7"])
        check(got == {"plugin_branch": True, "prefix": "kb", "key": None}, "branch-key: a kb/ branch holds no key (%r)" % got)
        got = branch_key("feature/ACME-7-x", ["ACME-7"])
        check(got == {"plugin_branch": False, "prefix": None, "key": None},
              "branch-key: a branch outside the prefixes is no plugin branch (%r)" % got)
        with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
            m = re.search(r"its name matches `\^\(([a-z|]+)\)/`", fh.read())
        check(m is not None and tuple(m.group(1).split("|")) == PREFIXES,
              "branch-key: PREFIXES is specs-repo-git §2.2's alternation (%r)" % (m and m.group(1)))
        r = new_repo(tmp, "branch-key")
        got = cli("--specs", r.path, "branch-key", "--branch", "spec/ACME-77-01-x", "--key", "ACME-77", "--key", "ACME-77-01")
        check(got["_rc"] == 0 and got.get("key") == "ACME-77-01", "branch-key: the CLI (%r)" % got)
        got = cli("--specs", r.path, "branch-key", "--branch", "spec/ACME-77-01-x")
        check(got["_rc"] == 0 and got.get("key") is None, "branch-key: no --key is a keyless run (%r)" % got)

    def with_origin(tmp, name):
        bare = os.path.join(tmp, name + ".git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, name)
        r.git("remote", "add", "origin", bare)
        r.git("push", "-q", "-u", "origin", "main")
        return r

    def scenarios_push_scope(tmp):
        session_file = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        r = with_origin(tmp, "scope-plugin")
        r.git("switch", "-q", "-c", "prd/A-1-x")
        r.write("specifications/PRD-A-1-x/prd.md", "prd\n")
        r.commit_all("deliverable")
        r.git("push", "-q", "-u", "origin", "prd/A-1-x")
        r.write(session_file, "resume\n")
        c = r.commit_all("session")
        got = push_scope(r.path, "prd/A-1-x")
        check(got == {"base": "refs/remotes/origin/prd/A-1-x", "commits": [c], "in_scope": True, "failed": None},
              "push-scope: one session-file commit past the pushed branch (%r)" % got)
        r.write("specifications/PRD-A-1-x/prd.md", "changed\n")
        bad = r.commit_all("deliverable again")
        got = push_scope(r.path, "prd/A-1-x")
        check(got["in_scope"] is False and got["failed"] == {"sha": bad, "reason": "paths",
              "path": "specifications/PRD-A-1-x/prd.md"}, "push-scope: a deliverable path fails (%r)" % got)

        r = with_origin(tmp, "scope-merge")
        r.git("switch", "-q", "-c", "prd/A-2-x")
        r.git("push", "-q", "-u", "origin", "prd/A-2-x")
        r.git("switch", "-q", "-c", "side")
        r.write("specifications/PRD-A-2-x/dev-workflows/resume.md", "r\n")
        r.commit_all("session on side")
        r.git("switch", "-q", "prd/A-2-x")
        r.git("merge", "-q", "--no-ff", "-m", "merge side", "side")
        merge = r.git("rev-parse", "HEAD")
        got = push_scope(r.path, "prd/A-2-x")
        check(got["in_scope"] is False and got["failed"] == {"sha": merge, "reason": "merge", "path": None},
              "push-scope: a merge commit fails (%r)" % got)

        r = with_origin(tmp, "scope-new")
        r.git("switch", "-q", "-c", "prd/A-3-x")
        r.write("specifications/PRD-A-3-x/dev-workflows/resume.md", "r\n")
        c = r.commit_all("session")
        got = push_scope(r.path, "prd/A-3-x")
        check(got == {"base": None, "commits": [c], "in_scope": True, "failed": None},
              "push-scope: a branch never pushed is walked over --remotes=origin (%r)" % got)

        r = with_origin(tmp, "scope-session")
        r.git("switch", "-q", "-c", "session/ab")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "1\n")
        r.commit_all("session 1")
        r.git("push", "-q", "-u", "origin", "session/ab")
        r.git("switch", "-q", "main")
        r.write("main.md", "m\n")
        r.commit_all("main moves")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "session/ab")
        r.git("merge", "-q", "--no-ff", "-m", "NOISSUE Merge main into session/ab", "main")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "2\n")
        r.commit_all("session 2")
        got = push_scope(r.path, "session/ab", session_default_ref="origin/main")
        check(got["in_scope"] is True and got["base"] == "refs/remotes/origin/session/ab" and len(got["commits"]) == 2,
              "push-scope: the session branch admits its merge of the default branch (%r)" % got)
        r.write("specifications/PRD-A-4-x/prd.md", "p\n")
        r.commit_all("a deliverable on the session branch")
        r.git("push", "-q", "origin", "session/ab")
        r.write("specifications/PRD-A-4-x/dev-workflows/resume.md", "3\n")
        r.commit_all("session 3")
        got = push_scope(r.path, "session/ab", session_default_ref="origin/main")
        newest_merge = r.git("rev-list", "--merges", "-n", "1", "refs/heads/session/ab")
        check(got["in_scope"] is False and got["failed"] == {"sha": newest_merge, "reason": "branch-path",
              "path": "specifications/PRD-A-4-x/prd.md"},
              "push-scope: the session branch's whole change must name session files only (%r)" % got)
        got = cli("--specs", r.path, "push-scope", "--branch", "session/ab", "--session-default-ref", "origin/main")
        check(got["_rc"] == 0 and got.get("in_scope") is False, "push-scope: the CLI (%r)" % got)
        got = cli("--specs", r.path, "push-scope", "--branch", "no-such")
        check(one_not_run_line(got), "push-scope: a branch that does not exist exits 2 (%r)" % got)

    def scenarios_owner_repo(tmp):
        conf = os.path.join(tmp, "ssh_config")
        with open(conf, "w", encoding="utf-8") as fh:
            fh.write("Host github-ig.com\n  HostName github.com\n")
        cases = [
            ("git@github.com:acme/docs.git", True, "acme/docs"),
            ("https://github.com/acme/docs", True, "acme/docs"),
            ("ssh://git@git.example.com:2222/team/docs.git", True, "git.example.com/team/docs"),
            ("https://git.example.com/team/docs/", True, "git.example.com/team/docs"),
            ("git@github-ig.com:acme/repo.git", False, "github-ig.com/acme/repo"),
            ("https://github.com/", True, None),
        ]
        if shutil.which("ssh"):
            cases.append(("git@github-ig.com:acme/repo.git", True, "acme/repo"))
        for url, alias, want in cases:
            got = owner_repo(url, resolve_alias=alias, ssh_config=conf)
            check(got["owner_repo"] == want and got["url"] == url,
                  "owner-repo: %s (alias %s) gives %r (%r)" % (url, alias, want, got))
        r = new_repo(tmp, "owner-none")
        got = cli("owner-repo", "--repo", r.path)
        check(got["_rc"] == 0 and all(got.get(k) is None for k in ("url", "host", "slug", "owner_repo")),
              "owner-repo: a repository with no origin gives nulls (%r)" % got)
        r.git("remote", "add", "origin", "https://github.com/acme/docs.git")
        got = cli("owner-repo", "--repo", r.path, "--no-alias")
        check(got["_rc"] == 0 and got.get("owner_repo") == "acme/docs", "owner-repo: the CLI (%r)" % got)
        plain = os.path.join(tmp, "plain-owner")
        os.makedirs(plain)
        got = cli("owner-repo", "--repo", plain)
        check(one_not_run_line(got), "owner-repo: a path that is no repository exits 2 (%r)" % got)

    def scenarios():
        with tempfile.TemporaryDirectory() as tmp:
            scenarios_status(tmp)
            scenarios_branch_merged(tmp)
            scenarios_branch_key(tmp)
            scenarios_push_scope(tmp)
            scenarios_owner_repo(tmp)

    try:
        scenarios()
    except Exception as e:  # a scenario that crashes must not hide the failures before it
        failures.append("selftest crashed: %s: %s" % (type(e).__name__, str(e).strip()[:500]))

    if failures:
        print("specs-git selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("specs-git selftest: PASS (%d checks)" % count[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())

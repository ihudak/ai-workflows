#!/usr/bin/env python3
"""session-branch.py — keep a specs repository's session files on a per-user session branch
where its default branch takes no direct push.

Run by workflows-core:specs-repo-git §8 (session-branch mode), and around each move of the
specs checkout by that reference and by workflows-core:phase-handoff. The rules are that
reference's; this script is their plumbing, and a change to either is a change to both.
Python standard library only.

  session-branch.py --specs <root> mode --default <name>
  session-branch.py --specs <root> sync --branch <b> --default-ref <ref>
  session-branch.py --specs <root> commit --branch <b> --default-ref <ref> --message <m> [--include-ahead]
  session-branch.py --specs <root> lift --branch <b>
  session-branch.py --specs <root> put-back --branch <b> --default-ref <ref>
  session-branch.py --selftest

<root> is the specs repository's top level. Nothing here switches a branch, moves HEAD,
pushes, or writes a working-tree path outside specs-repo-git §2.1's session-file shapes.
The session branch moves only by update-ref with its old value, so a concurrent run fails
instead of overwriting. Output is one JSON object on stdout.
Exit 0: it ran, whatever it found. Exit 2: it could not run (usage, not a repository's top
level, an unexpected git failure); the caller reports it and the run continues.
"""

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS_REPO_GIT = os.path.join(HERE, "..", "references", "specs-repo-git.md")
BRANCH_NAMING = os.path.join(HERE, "..", "references", "branch-naming.md")

# specs-repo-git §2.1's classifier, character for character; the selftest fails where they differ.
ARTIFACT = [
    r"^(specs|specifications|vis)/.+/dev-workflows/",
    r"^documentation/[^/]+/dev-workflows/",
    r"^dev-workflows-feedback/",
    r"^dev-workflows-cost/",
    r"^(specs|specifications|vis)/.+/(implementation|release-notes|follow-ups|pr-draft|[^/]+-implementation-gaps)\.md$",
]
EXCLUDED = (r"^(specs|specifications|vis)/(.+/)?(brd|grounding|interview|design|attachments|revisions"
            r"|bundle-[0-9]{8}|customer-sent-[0-9]{8}|Doc screenshots)/")
_ARTIFACT_RE = [re.compile(p) for p in ARTIFACT]
_EXCLUDED_RE = re.compile(EXCLUDED)

# branch-naming §4's skip list; the selftest fails where they differ.
IDENTITY_SKIP = frozenset(("feat", "feature", "fix", "bugfix", "hotfix", "docs", "chore", "release", "story",
                           "idea", "prd", "ard", "spec", "design", "ready", "brd", "frames", "kb", "session"))

# The appended shapes merge with git's union driver; every other session file keeps the session
# branch's side (merge-tree -X ours). resume.md is overwritten, so it is taken out again.
ATTR_BEGIN = "# BEGIN workflows-core session-branch: written by session-branch.py, do not edit"
ATTR_END = "# END workflows-core session-branch"
ATTRIBUTES = [
    "**/dev-workflows/** merge=union",
    "dev-workflows-feedback/** merge=union",
    "dev-workflows-cost/** merge=union",
    "**/implementation.md merge=union",
    "**/release-notes.md merge=union",
    "**/follow-ups.md merge=union",
    "**/*-implementation-gaps.md merge=union",
    "**/dev-workflows/resume.md !merge",
]
ZERO = "0" * 40


class NotRun(Exception):
    """Something this script cannot do here; main() reports it and exits 2."""


def git(root, *args, env=None, data=None, check=True):
    r = subprocess.run(["git", "-C", root, "-c", "core.quotePath=false", *args], input=data,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env=dict(os.environ, **env) if env else None)
    if check and r.returncode != 0:
        raise NotRun("git %s: %s" % (" ".join(args[:2]), r.stderr.decode("utf-8", "replace").strip()[:300]))
    return r


def text(r):
    return r.stdout.decode("utf-8", "surrogateescape").strip()


def nul_list(r):
    return [x for x in r.stdout.decode("utf-8", "surrogateescape").split("\0") if x]


def classify(path):
    """specs-repo-git §2.1: a session-file shape, and under none of the reserved subdirectories."""
    return any(p.search(path) for p in _ARTIFACT_RE) and not _EXCLUDED_RE.search(path)


def rev(root, ref):
    """The commit <ref> names, or None where it names none."""
    r = git(root, "rev-parse", "--verify", "--quiet", ref + "^{commit}", check=False)
    return text(r) if r.returncode == 0 else None


def blob(root, commit, path):
    """The blob id of <path> at <commit>, or None where the commit lacks it."""
    if commit is None:
        return None
    r = git(root, "rev-parse", "--verify", "--quiet", "%s:%s" % (commit, path), check=False)
    return text(r) if r.returncode == 0 else None


def worktree_blob(root, path):
    """The blob id git would store for the working copy of <path> (clean filters applied), or None."""
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return None
    return text(git(root, "hash-object", "--path", path, "--", path))


def dirty_session_paths(root):
    """Every session-file path git status reports: modified, deleted, staged or untracked."""
    recs = nul_list(git(root, "status", "--porcelain", "-z", "--untracked-files=all"))
    paths, i = set(), 0
    while i < len(recs):
        rec = recs[i]
        i += 1
        xy, path = rec[:2], rec[3:]
        if xy[0] in "RC":
            i += 1  # the original path of a rename or copy rides in the next field
        if classify(path):
            paths.add(path)
    return sorted(paths)


def config(root, key, as_bool=False):
    """A configuration value, or None where it is unset or unreadable."""
    r = git(root, "config", *(["--bool"] if as_bool else []), "--get", key, check=False)
    return text(r) if r.returncode == 0 else None


def valid_identity(root, ident):
    """branch-naming §5: lowercase, [a-z0-9-], a letter or digit first; and a valid branch name."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", ident or ""):
        return False
    return git(root, "check-ref-format", "--branch", "session/" + ident, check=False).returncode == 0


def inferred_identity(root):
    """branch-naming §2.3: local branches, and remote ones without the remote's name, each once."""
    heads = text(git(root, "for-each-ref", "--format=%(refname:lstrip=2)", "refs/heads")).splitlines()
    remotes = text(git(root, "for-each-ref", "--format=%(refname:lstrip=3)", "refs/remotes")).splitlines()
    sample = sorted({n for n in heads + remotes if n and n != "HEAD"})[:200]
    counts = {}
    for name in sample:
        first, sep, _ = name.partition("/")
        if sep and 2 <= len(first) <= 8 and re.fullmatch(r"[a-z0-9][a-z0-9-]*", first) and first not in IDENTITY_SKIP:
            counts[first] = counts.get(first, 0) + 1
    ranked = sorted((-n, c) for c, n in counts.items() if n >= 3 and n * 10 >= len(sample) * 3)
    return ranked[0][1] if ranked else None


def identity(root):
    """branch-naming §2's first three rungs, in order; the first non-empty one decides, never the prompt."""
    for rung, value in (("env", os.environ.get("GIT_USER_INITIALS", "")),
                        ("config", config(root, "user.initials") or ""),
                        ("inferred", inferred_identity(root) or "")):
        if value:
            return (value if valid_identity(root, value) else None), rung
    return None, None


def mode(root, default):
    on = config(root, "workflows.sessionBranch", as_bool=True) == "true"
    refused = config(root, "branch.%s.workflowsPushRefused" % default)
    source = "config" if on else ("refused" if refused else None)
    ident, rung = identity(root)
    return {"mode": "on" if source else "off", "source": source, "identity": ident, "identity_rung": rung,
            "branch": ("session/" + ident) if ident else None}


def selftest():
    """Every rule this script carries, on repositories built at run time."""
    failures = []
    me = os.path.abspath(__file__)
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ.pop("GIT_USER_INITIALS", None)
    devnull = subprocess.DEVNULL

    def check(ok, what):
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

        def configure(self):
            self.git("config", "user.email", "t@example.invalid")
            self.git("config", "user.name", "t")
            self.git("config", "commit.gpgsign", "false")

        def write(self, rel, body, append=False):
            full = os.path.join(self.path, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "a" if append else "w", encoding="utf-8", newline="") as fh:
                fh.write(body)

        def read(self, rel):
            full = os.path.join(self.path, rel)
            if not os.path.exists(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def commit_all(self, message):
            self.git("add", "-A")
            self.git("commit", "-q", "-m", message)

        def run(self, *args, env=None):
            r = subprocess.run([sys.executable, me, "--specs", self.path, *args], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=dict(os.environ, **(env or {})))
            if r.returncode != 0:
                return {"_rc": r.returncode, "_err": r.stderr.decode("utf-8", "replace")}
            return json.loads(r.stdout)

        def state(self):
            return (self.git("status", "--porcelain", "-z", "--untracked-files=all"), self.git("ls-files", "-s"),
                    self.git("rev-parse", "HEAD"), self.git("symbolic-ref", "-q", "HEAD", check=False))

    FB = "specifications/PRD-A-1-x/dev-workflows/A-1-feedback.md"

    def world(tmp):
        """A bare remote whose pre-receive hook refuses main unless ALLOW_MAIN is set, and two clones."""
        seed = Repo(os.path.join(tmp, "seed"))
        subprocess.run(["git", "init", "-q", "-b", "main", seed.path], check=True)
        seed.configure()
        seed.write("specifications/PRD-A-1-x/prd.md", "# PRD\n")
        seed.write(FB, "---\nkey: A-1\n---\n\n## e0\nfirst\n")
        seed.commit_all("base")
        remote = os.path.join(tmp, "remote.git")
        subprocess.run(["git", "clone", "-q", "--bare", seed.path, remote], check=True, stdout=devnull, stderr=devnull)
        hook = os.path.join(remote, "hooks", "pre-receive")
        with open(hook, "w") as fh:
            fh.write('#!/bin/sh\nwhile read o n r; do\n'
                     '  if [ "$r" = refs/heads/main ] && [ -z "$ALLOW_MAIN" ]; then echo "protected" >&2; exit 1; fi\n'
                     'done\nexit 0\n')
        os.chmod(hook, 0o755)
        clones = []
        for name in ("a", "b"):
            path = os.path.join(tmp, name)
            subprocess.run(["git", "clone", "-q", remote, path], check=True, stdout=devnull, stderr=devnull)
            r = Repo(path)
            r.configure()
            clones.append(r)
        return remote, clones[0], clones[1]

    def merge_on_remote(tmp, remote, branch, how):
        """Land <branch> on the remote's main as a merged pull request would: 'merge' or 'squash'."""
        m = Repo(os.path.join(tmp, "maint"))
        if not os.path.exists(m.path):
            subprocess.run(["git", "clone", "-q", remote, m.path], check=True, stdout=devnull, stderr=devnull)
            m.configure()
        m.git("fetch", "-q", "origin")
        m.git("checkout", "-q", "-B", "main", "origin/main")
        if how == "merge":
            m.git("merge", "-q", "--no-ff", "origin/" + branch, "-m", "Merge pull request")
        else:
            m.git("merge", "-q", "--squash", "origin/" + branch)
            m.git("commit", "-q", "-m", "Squashed pull request")
        m.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})

    # ---- the classifier, and its parity with specs-repo-git §2.1 --------------------------
    for path, want in [
        ("specifications/PRD-A-1-x/dev-workflows/A-1-feedback.md", True),
        ("specifications/PRD-A-1-x/EPIC-A-1-1-y/implementation.md", True),
        ("specifications/PRD-A-1-x/follow-ups.md", True),
        ("specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md", True),
        ("documentation/acme-docs/dev-workflows/cost/s.md", True),
        ("dev-workflows-cost/pending-2026-10-06-abcd1234.md", True),
        ("specifications/BRD-B-1-y/brd/source/implementation.md", False),
        ("specifications/PRD-A-1-x/attachments/release-notes.md", False),
        ("specifications/PRD-A-1-x/Doc screenshots/release-notes.md", False),
        ("specifications/PRD-A-1-x/prd.md", False),
        ("README.md", False),
    ]:
        check(classify(path) == want, "classify(%r) should be %s" % (path, want))
    with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
        ref_text = fh.read()
    start = ref_text.index("2. Classify each reported path")
    pats = re.findall(r"`(\^[^`]+)`", ref_text[start:ref_text.index("**OTHER** otherwise.", start)])
    check(pats[:-1] == ARTIFACT, "the script's ARTIFACT patterns equal specs-repo-git §2.1's (%r)" % pats[:-1])
    check(pats[-1:] == [EXCLUDED], "the script's EXCLUDED pattern equals specs-repo-git §2.1's (%r)" % pats[-1:])

    # ---- dirty_session_paths -----------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, _ = world(tmp)
        a.write(FB, "## a1\nmine\n", append=True)
        a.write("specifications/PRD-A-1-zahlungsauslösung/dev-workflows/cost/s 1.md", "cost\n")
        a.write("specifications/PRD-A-1-x/notes.md", "not a session file\n")
        got = dirty_session_paths(a.path)
        check(got == sorted([FB, "specifications/PRD-A-1-zahlungsauslösung/dev-workflows/cost/s 1.md"]),
              "dirty_session_paths lists modified and untracked session files, odd names included (%r)" % (got,))

    # ---- mode and identity ---------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, _ = world(tmp)
        got = a.run("mode", "--default", "main")
        check(got.get("mode") == "off" and got.get("source") is None, "mode is off by default (%r)" % got)
        check(got.get("identity") is None and got.get("branch") is None, "no identity without a rung (%r)" % got)
        a.git("config", "workflows.sessionBranch", "true")
        got = a.run("mode", "--default", "main", env={"GIT_USER_INITIALS": "ab"})
        check(got.get("mode") == "on" and got.get("source") == "config", "the opt-in key turns it on (%r)" % got)
        check(got.get("branch") == "session/ab" and got.get("identity_rung") == "env", "the env rung names it (%r)" % got)
        a.git("config", "--unset", "workflows.sessionBranch")
        a.git("config", "branch.main.workflowsPushRefused", "2026-10-06")
        a.git("config", "user.initials", "cd")
        got = a.run("mode", "--default", "main")
        check(got.get("mode") == "on" and got.get("source") == "refused", "a refusal record turns it on (%r)" % got)
        check(got.get("branch") == "session/cd" and got.get("identity_rung") == "config", "user.initials names it (%r)" % got)
        got = a.run("mode", "--default", "main", env={"GIT_USER_INITIALS": "Not Valid"})
        check(got.get("identity") is None and got.get("identity_rung") == "env",
              "an invalid first rung names nothing and does not fall through (%r)" % got)
        a.git("config", "--unset", "user.initials")
        for b in ("iv-gu/a", "iv-gu/b", "iv-gu/c", "prd/A-1-x", "spec/A-1-x", "session/zz", "session/yy"):
            a.git("branch", b)
        got = a.run("mode", "--default", "main")
        check(got.get("identity") == "iv-gu" and got.get("identity_rung") == "inferred",
              "the guess counts iv-gu and never prd, spec or session (%r)" % got)
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, _ = world(tmp)
        for b in ("prd/A-1-x", "prd/A-2-y", "prd/A-3-z", "session/a", "session/b", "session/c"):
            a.git("branch", b)
        got = a.run("mode", "--default", "main")
        check(got.get("identity") is None, "plugin and session prefixes never become an identity (%r)" % got)
    with open(BRANCH_NAMING, encoding="utf-8") as fh:
        m = re.search(r"skip='\^\(([^)]*)\)\$'", fh.read())
    check(m is not None and frozenset(m.group(1).split("|")) == IDENTITY_SKIP,
          "IDENTITY_SKIP equals branch-naming §4's skip list (%r)" % (m.group(1) if m else None))

    if failures:
        print("session-branch selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("session-branch selftest: PASS")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Keep session files on a per-user session branch.")
    ap.add_argument("--specs", help="the specs repository's top level")
    ap.add_argument("--selftest", action="store_true", help="run the built-in fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("mode")
    p.add_argument("--default", required=True)
    for name in ("sync", "commit", "put-back"):
        p = sub.add_parser(name)
        p.add_argument("--branch", required=True)
        p.add_argument("--default-ref", required=True)
        if name == "commit":
            p.add_argument("--message", required=True)
            p.add_argument("--include-ahead", action="store_true")
    p = sub.add_parser("lift")
    p.add_argument("--branch", required=True)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    if not a.specs or not a.cmd:
        print("session-branch: --specs and a subcommand are required", file=sys.stderr)
        return 2
    try:
        top = text(git(a.specs, "rev-parse", "--show-toplevel"))
        if os.path.realpath(top) != os.path.realpath(a.specs):
            raise NotRun("%s is not its repository's top level (%s)" % (a.specs, top))
        result = dispatch(a)
    except NotRun as e:
        print("session-branch: not run (%s)" % e, file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


def dispatch(a):
    if a.cmd == "mode":
        return mode(a.specs, a.default)
    raise NotRun("subcommand %s is not implemented yet" % a.cmd)


if __name__ == "__main__":
    sys.exit(main())

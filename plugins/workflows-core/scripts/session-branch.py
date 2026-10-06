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


def ensure_attributes(root):
    """Keep exactly one marked block of ATTRIBUTES in $GIT_DIR/info/attributes, other lines untouched."""
    path = text(git(root, "rev-parse", "--git-path", "info/attributes"))
    if not os.path.isabs(path):
        path = os.path.join(root, path)
    try:
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
    except FileNotFoundError:
        old = ""
    block = "\n".join([ATTR_BEGIN, *ATTRIBUTES, ATTR_END]) + "\n"
    if ATTR_BEGIN in old and ATTR_END in old:
        a = old.index(ATTR_BEGIN)
        b = old.index(ATTR_END) + len(ATTR_END)
        rest = old[b:]
        new = old[:a] + block + (rest[1:] if rest.startswith("\n") else rest)
    else:
        new = old + ("\n" if old and not old.endswith("\n") else "") + block
    if new != old:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(new)


def merge_tree_ok(root):
    """This git can merge without a checkout and take a side (merge-tree --write-tree -X)."""
    r = git(root, "merge-tree", "-h", check=False)
    usage = (r.stdout + r.stderr).decode("utf-8", "replace")
    return "--write-tree" in usage and "-X" in usage


def overlay_paths(root, tip):
    """Every session-file path the overlay can hold: the ones git status reports, and the ones where the
    branch differs from HEAD. The second set is what catches an overlay file a run deleted: it was never
    in the index, so git status no longer reports it once it is gone."""
    paths = set(dirty_session_paths(root))
    if tip is not None:
        paths.update(p for p in nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", "HEAD", tip))
                     if classify(p))
    return sorted(paths)


def unpreserved(root, tip):
    """Overlay paths whose working copy (or its absence) is not the branch tip's version."""
    return [p for p in overlay_paths(root, tip) if worktree_blob(root, p) != blob(root, tip, p)]


def write_from(root, commit, path):
    """Write <path> as <commit> holds it (smudge filters applied), or remove it where the commit lacks it."""
    full = os.path.join(root, path)
    if blob(root, commit, path) is None:
        if os.path.lexists(full):
            os.remove(full)
        return
    data = git(root, "cat-file", "--filters", "%s:%s" % (commit, path)).stdout
    os.makedirs(os.path.dirname(full) or root, exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(data)


def align(root, old_tip, new_tip):
    """After the branch moved, bring each session file whose working copy still equals the old tip's
    version to the new tip's. A working copy that differs holds entries of its own and is left."""
    changed = [p for p in nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", old_tip, new_tip))
               if classify(p)]
    done = []
    for p in changed:
        if worktree_blob(root, p) == blob(root, old_tip, p):
            write_from(root, new_tip, p)
            done.append(p)
    return done


def sync(root, branch, default_ref):
    """Bring <default-ref> into the session branch without a checkout: a fast-forward where the branch
    holds nothing of its own, else merge-tree -X ours with the union driver; then align the overlay."""
    ensure_attributes(root)
    ref = "refs/heads/" + branch
    base = rev(root, default_ref)
    if base is None:
        raise NotRun("no such ref: %s" % default_ref)
    tip = rev(root, ref)
    result = {"created": False, "merged": False, "fast_forward": False, "tip": tip, "conflict": [],
              "deferred": [], "aligned": []}
    if tip is None:
        raise NotRun("no such branch: %s" % branch)
    if git(root, "merge-base", "--is-ancestor", base, tip, check=False).returncode == 0:
        return result
    held = unpreserved(root, tip)
    if held:
        result["deferred"] = held
        return result
    if git(root, "merge-base", "--is-ancestor", tip, base, check=False).returncode == 0:
        git(root, "update-ref", ref, base, tip)
        result.update(fast_forward=True, tip=base, aligned=align(root, tip, base))
        return result
    if not merge_tree_ok(root):
        raise NotRun("this git cannot merge without a checkout (merge-tree --write-tree -X)")
    r = git(root, "merge-tree", "--write-tree", "-X", "ours", tip, base, check=False)
    lines = text(r).splitlines()
    if r.returncode == 1:
        result["conflict"] = sorted({ln.split("\t", 1)[1] for ln in lines[1:] if "\t" in ln})
        return result
    if r.returncode != 0 or not lines:
        raise NotRun("merge-tree: %s" % r.stderr.decode("utf-8", "replace").strip()[:300])
    merge = text(git(root, "commit-tree", lines[0], "-p", tip, "-p", base,
                     "-m", "Merge %s into %s" % (default_ref, branch)))
    git(root, "update-ref", ref, merge, tip)
    result.update(merged=True, tip=merge, aligned=align(root, tip, merge))
    return result


def create_at(root, branch, default_ref):
    """A new session branch starts where the checkout's files come from: merge-base HEAD <default-ref>."""
    r = git(root, "merge-base", "HEAD", default_ref, check=False)
    start = text(r) if r.returncode == 0 and text(r) else rev(root, default_ref)
    if start is None:
        raise NotRun("no commit to start %s from" % branch)
    git(root, "update-ref", "refs/heads/" + branch, start, ZERO)
    return start


def ahead_paths(root, default_ref):
    """The files of the commits HEAD holds and <default-ref> lacks, where every one of them is a
    non-merge commit touching session files only (specs-repo-git §4 step 5's push-scope test)."""
    commits = text(git(root, "rev-list", "--reverse", "HEAD", "--not", default_ref)).split()
    paths = set()
    for c in commits:
        if len(text(git(root, "rev-list", "--parents", "-n", "1", c)).split()) != 2:
            return [], commits, True
        files = nul_list(git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "--root", "--no-renames", c))
        if not files or not all(classify(f) for f in files):
            return [], commits, True
        paths.update(files)
    return sorted(paths), commits, False


def commit(root, branch, default_ref, message, include_ahead=False):
    """Commit every dirty session file onto <branch> through a temporary index, then merge
    <default-ref> in and align the overlay. Never touches the checkout, the index or HEAD."""
    ref = "refs/heads/" + branch
    created = False
    tip = rev(root, ref)
    if tip is None:
        tip = create_at(root, branch, default_ref)
        created = True
    paths = overlay_paths(root, tip)
    stranded, not_session = [], False
    if include_ahead:
        extra, ahead, not_session = ahead_paths(root, default_ref)
        stranded = [] if not_session else ahead
        paths = sorted(set(paths) | set(extra))
    committed, changed = None, []
    if paths:
        gitdir = text(git(root, "rev-parse", "--absolute-git-dir"))
        with tempfile.TemporaryDirectory(dir=gitdir, prefix="session-branch-") as td:
            env = {"GIT_INDEX_FILE": os.path.join(td, "index")}
            git(root, "read-tree", tip, env=env)
            entries = []
            for p in paths:
                full = os.path.join(root, p)
                if os.path.isfile(full) and not os.path.islink(full):
                    sha = text(git(root, "hash-object", "-w", "--path", p, "--", p))
                    mode_bits = "100755" if os.stat(full).st_mode & stat.S_IXUSR else "100644"
                    entries.append("%s %s\t%s" % (mode_bits, sha, p))
                else:
                    entries.append("0 %s\t%s" % (ZERO, p))
            git(root, "update-index", "-z", "--index-info",
                data=("\0".join(entries) + "\0").encode("utf-8", "surrogateescape"), env=env)
            tree = text(git(root, "write-tree", env=env))
        if tree != text(git(root, "rev-parse", tip + "^{tree}")):
            committed = text(git(root, "commit-tree", tree, "-p", tip, "-m", message))
            git(root, "update-ref", ref, committed, tip)
            changed = nul_list(git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", tip, committed))
    synced = sync(root, branch, default_ref)
    return {"committed": committed, "files": len(changed), "paths": changed, "created": created,
            "stranded": len(stranded), "ahead_not_session": not_session, "sync": synced}


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

    # ---- sync ------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        base = a.git("rev-parse", "HEAD")
        a.git("branch", "session/aa", base)
        # b moves main on the remote (a teammate's merged pull request)
        b.write(FB, "## team\nfrom b\n", append=True)
        b.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: team\n")
        b.commit_all("team")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("fast_forward") is True and got.get("merged") is False,
              "a branch with nothing of its own is fast-forwarded, not merged (%r)" % got)
        check(a.git("rev-parse", "session/aa") == a.git("rev-parse", "origin/main"), "…to the default ref")
        # a's own commit on the session branch, then the teammate moves main again
        a.git("branch", "-f", "session/aa", "origin/main")
        tmpidx = os.path.join(tmp, "idx")
        env = {"GIT_INDEX_FILE": tmpidx}
        a.git("read-tree", "session/aa", env=env)
        mine = "---\nkey: A-1\n---\n\n## e0\nfirst\n## team\nfrom b\n## a1\nmine\n"
        sha = subprocess.run(["git", "-C", a.path, "hash-object", "-w", "--stdin"], input=mine.encode(),
                             stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        a.git("update-index", "--cacheinfo", "100644,%s,%s" % (sha, FB), env=env)
        rsha = subprocess.run(["git", "-C", a.path, "hash-object", "-w", "--stdin"], input=b"pos: mine\n",
                              stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        a.git("update-index", "--cacheinfo", "100644,%s,%s" % (rsha, "specifications/PRD-A-1-x/dev-workflows/resume.md"), env=env)
        tree = a.git("write-tree", env=env)
        c = a.git("commit-tree", tree, "-p", "session/aa", "-m", "mine")
        a.git("update-ref", "refs/heads/session/aa", c)
        a.write(FB, mine)  # the working copies a real commit leaves preserved
        a.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: mine\n")
        b.write(FB, "## team2\nagain\n", append=True)
        b.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: team2\n")
        b.commit_all("team2")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        before = a.state()
        got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("merged") is True and not got.get("conflict"), "a moved main is merged in (%r)" % got)
        merged = a.git("show", "session/aa:" + FB)
        check("## a1" in merged and "## team2" in merged and "## team\n" in merged,
              "both sides' appended entries survive the union merge (%r)" % merged)
        check(a.read(FB) == merged + "\n" and got.get("aligned") == [FB],
              "the working copy that equalled the old tip now holds the merge (%r)" % got.get("aligned"))
        check(a.git("show", "session/aa:specifications/PRD-A-1-x/dev-workflows/resume.md") == "pos: mine",
              "an overwritten resume.md keeps the session side")
        check(len(a.git("rev-list", "--parents", "-n", "1", "session/aa").split()) == 3, "the merge has two parents")
        check(a.state() == before, "sync moves no checkout, index or HEAD")
        attrs = a.read(".git/info/attributes")
        check(attrs is not None and attrs.count(ATTR_BEGIN) == 1 and "**/dev-workflows/** merge=union" in attrs,
              "the attributes block is written once (%r)" % attrs)
        a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(a.read(".git/info/attributes").count(ATTR_BEGIN) == 1, "and stays one block on a second sync")
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        a.git("branch", "session/aa")
        a.write("specifications/PRD-A-1-x/follow-ups.md", "- [ ] x\n")  # dirty, and not on the branch
        b.write(FB, "## team\n", append=True)
        b.commit_all("team")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        tip = a.git("rev-parse", "session/aa")
        got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("deferred") == ["specifications/PRD-A-1-x/follow-ups.md"] and a.git("rev-parse", "session/aa") == tip,
              "sync defers, moving nothing, while a dirty session file is not on the branch (%r)" % got)
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        a.git("branch", "session/aa")
        env = {"GIT_INDEX_FILE": os.path.join(tmp, "i2")}
        a.git("read-tree", "session/aa", env=env)
        sha = subprocess.run(["git", "-C", a.path, "hash-object", "-w", "--stdin"], input=b"changed\n",
                             stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        a.git("update-index", "--cacheinfo", "100644,%s,%s" % (sha, FB), env=env)
        c = a.git("commit-tree", a.git("write-tree", env=env), "-p", "session/aa", "-m", "mod")
        a.git("update-ref", "refs/heads/session/aa", c)
        a.write(FB, "changed\n")
        b.git("rm", "-q", FB)
        b.git("commit", "-q", "-m", "delete feedback")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("conflict") == [FB] and a.git("rev-parse", "session/aa") == c,
              "a modify/delete merge is reported and moves nothing (%r)" % got)

    # ---- commit ----------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        odd = "specifications/PRD-A-1-x/dev-workflows/cost/:odd name ü.md"
        a.write(FB, "## a1\nmine\n", append=True)
        a.write(odd, "cost\n")
        before = a.state()
        got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        check(got.get("created") is True and got.get("committed"), "the first commit creates the branch (%r)" % got)
        check(sorted(got.get("paths", [])) == sorted([FB, odd]), "it carries both files (%r)" % got)
        check(a.state() == before, "commit moves no checkout, index or HEAD")
        check(a.git("show", "session/aa:" + FB).endswith("## a1\nmine"), "the branch holds the appended entry")
        check(a.git("merge-base", "session/aa", "main") == a.git("rev-parse", "main"), "the branch starts from the checkout's base")
        again = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        check(again.get("committed") is None and again.get("files") == 0, "an unchanged tree commits nothing (%r)" % again)
        a.write(FB, "## a2\nmore\n", append=True)
        tip = a.git("rev-parse", "session/aa")
        got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        check(a.git("rev-parse", "session/aa^") == tip, "a second commit stacks on the first (%r)" % got)
        os.remove(os.path.join(a.path, odd))  # an overlay-only file: never in the index, so git status forgets it
        got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Remove pending")
        check(odd in got.get("paths", []), "a removed overlay file is committed as a deletion (%r)" % got)
        check(subprocess.run(["git", "-C", a.path, "cat-file", "-e", "session/aa:" + odd], stderr=devnull).returncode != 0,
              "…and the branch no longer has it")
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        # main moves on the remote during the run, appending to the same file
        a.write(FB, "## a1\nmine\n", append=True)
        b.write(FB, "## team\nfrom b\n", append=True)
        b.commit_all("team")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        content = a.git("show", "session/aa:" + FB)
        check("## a1" in content and "## team" in content and got["sync"].get("merged") is True,
              "the commit is built first and main merged second, so no entry is lost (%r)" % content)
        check("## team" in (a.read(FB) or ""), "the working copy is aligned to the merged version (%r)" % a.read(FB))
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        # the interim left a session-file commit on local main that origin refused
        a.write(FB, "## stranded\nold\n", append=True)
        a.commit_all("A-1 Add dev-workflows session artifacts (implement)")
        head = a.git("rev-parse", "HEAD")
        got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session",
                    "--include-ahead")
        check(got.get("stranded") == 1 and "## stranded" in a.git("show", "session/aa:" + FB),
              "--include-ahead carries a stranded commit's files (%r)" % got)
        check(a.git("rev-parse", "HEAD") == head, "…and never moves the local default branch")
        a.write("specifications/PRD-A-1-x/prd.md", "# PRD changed\n")
        a.commit_all("a deliverable commit of the user's own")
        got = a.run("commit", "--branch", "session/bb", "--default-ref", "origin/main", "--message", "A-1 Add session",
                    "--include-ahead")
        check(got.get("stranded") == 0 and got.get("ahead_not_session") is True,
              "commits ahead that are not all session-file commits are left alone (%r)" % got)

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
    if a.cmd == "sync":
        return sync(a.specs, a.branch, a.default_ref)
    if a.cmd == "commit":
        return commit(a.specs, a.branch, a.default_ref, a.message, a.include_ahead)
    raise NotRun("subcommand %s is not implemented yet" % a.cmd)


if __name__ == "__main__":
    sys.exit(main())

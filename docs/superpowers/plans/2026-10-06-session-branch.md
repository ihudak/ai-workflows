# Session Branch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** On a specs repository whose default branch takes no direct push, keep every run's session files on a per-user `session/<identity>` branch that the user lands by pull request, without changing any emitter or reader.

**Architecture:** One bundled, self-tested Python script (`plugins/workflows-core/scripts/session-branch.py`) does the git plumbing — mode detection, a commit through a temporary index, a checkout-free merge of the default branch with git's `union` driver, and the overlay's `lift`/`put-back` around every move of the specs checkout. `workflows-core:specs-repo-git` gains §8 stating the rules and calling the script at each step; `phase-handoff`, `branch-naming` and `/implement` gain their hooks.

**Tech Stack:** Python 3 standard library; git ≥ the release whose `git merge-tree` accepts `--write-tree` and `-X` (probed at run time, measured on 2.43); Markdown references executed by agents.

**Spec:** `docs/superpowers/specs/2026-10-06-session-branch-design.md` (approved 2026-10-06).

## Global Constraints

- Every git call is `git -C <specs root>`; the script never changes the working directory, never switches a branch, never moves `HEAD`, never pushes, never force-updates a ref: the session branch moves only by `update-ref <ref> <new> <old>`.
- The script writes working-tree paths only where `specs-repo-git` §2.1's classifier says ARTIFACT, and only in `lift` (return to `HEAD`), `put-back` and the post-merge alignment.
- The one discard is `lift` returning to `HEAD` a session file whose exact content (`git hash-object`) equals the session branch tip's blob.
- Configuration writes: `branch.<branch>.workflowsPushRefused` (existing) and one marked block in `$GIT_DIR/info/attributes`; `workflows.sessionBranch` is the user's key, read and never written.
- Output: one JSON object on stdout; exit 0 whenever it ran (a finding is not an error), exit 2 when it could not run. Never fatal to the run (`specs-repo-git` §1 rule 5).
- Prompt-free; never opens a pull request (spec decision 4).
- Prose: never hard-wrap new paragraphs in files that do not already wrap; match each file's own wrapping. Vendor neutrality (check 13) and identity quarantine (checks 10, 14) hold; nothing names the organisation or the internal repository.
- `CLAUDE.md` stays under 36,000 characters and every `.claude/rules/*.md` under 20,000 (validate-catalog warns past them).

## Amended during planning (rulings against the spec, with reasons)

1. **`commit` builds first and merges second.** The spec's `commit` ran `sync` before writing the working copies. A merge brings entries the working copies do not hold, and writing them over the merged tip would delete those entries. So `commit` builds on the tip the working copies came from, then merges `<default-ref>` in, then aligns every working copy that still equals the previous tip's version to the merged one. Cost if wrong: none found; the order only matters where `<default-ref>` moved during the run.
2. **A new session branch starts at `git merge-base HEAD <default-ref>`, not at `<default-ref>`.** The working copies come from the checkout; a branch started at a newer `<default-ref>` would have them overwrite entries the checkout never saw. The merge that follows the first commit brings `<default-ref>` in with the union driver.
3. **`sync` defers while a dirty session file is not on the branch**, returning `deferred: [...]` and moving nothing, so a merge never strands unpreserved working copies on an old base.
4. **The preflight ends with `put-back` in the mode**, whether or not it moved the checkout, so a run interrupted between `lift` and `put-back` finds its overlay restored at the next run.
5. **Fast-forward where the branch holds nothing of its own.** Where the tip is an ancestor of `<default-ref>`, `sync` moves the branch forward with `update-ref` instead of creating a merge commit.
6. **The overlay's paths are the dirty ones and the ones where the branch differs from `HEAD`.** The spec's `commit` and `lift` read only what `git status` reports. An overlay file that exists only on the session branch is never in the index, so once a run deletes it (§9's pending-cost relocation does) `git status` no longer reports it: its deletion would never be committed, and `put-back` would bring it back. `commit`, `lift` and `sync` therefore read `overlay_paths`.

The spec's text gains a short *Amended during planning* section in Task 9 recording these six.

## Review Focus

1. **Two sessions on one clone at once** — two Claude sessions committing to the same session branch. Expected: `update-ref` with the old value makes the later one fail with exit 2, its files stay in the working tree, and its next run commits them. (Reasoned in review; no test races two processes.)
2. **Line-ending and clean/smudge filters** (`.gitattributes` `text eol=crlf`) on session files. Expected: `lift` treats a CRLF working copy of an LF blob as preserved, and `put-back` writes the smudged form. Test in Task 5.
3. **Paths with spaces, non-ASCII bytes or a leading `:`.** Expected: classified, committed, lifted and put back like any other. Tests in Tasks 1, 4 and 5.
4. **A user who switches or pulls the specs checkout by hand while the overlay is present.** Git refuses, naming the session files. Expected: the environment page tells them what the files are and the two commands that lift and put them back. Docs step in Task 6.
5. **An identity that changes between runs** (`GIT_USER_INITIALS` set later). Expected: a second session branch; the first keeps its commits and its pull request; nothing is lost. Test in Task 2 (the identity follows the first non-empty rung).

---

### Task 1: Script skeleton, the classifier, and its parity with the reference

**Files:**
- Create: `plugins/workflows-core/scripts/session-branch.py`

**Interfaces:**
- Produces: `git(root, *args, env=None, data=None, check=True) -> CompletedProcess` (raises `NotRun` on failure when `check`); `text(r) -> str`; `nul_list(r) -> list[str]`; `classify(path: str) -> bool`; `rev(root, ref) -> str|None`; `blob(root, commit, path) -> str|None`; `worktree_blob(root, path) -> str|None`; `dirty_session_paths(root) -> list[str]`; `class NotRun(Exception)`; constants `ARTIFACT`, `EXCLUDED`, `IDENTITY_SKIP`, `ATTR_BEGIN`, `ATTR_END`, `ATTRIBUTES`, `ZERO`; `selftest() -> int` with helpers `check`, `Repo`, `world`, `merge_on_remote`; `main() -> int`.

- [ ] **Step 1: Write the file with the harness and the failing tests (no implementation of the helpers yet)**

Create `plugins/workflows-core/scripts/session-branch.py`:

```python
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
    raise NotImplementedError


def rev(root, ref):
    raise NotImplementedError


def blob(root, commit, path):
    raise NotImplementedError


def worktree_blob(root, path):
    raise NotImplementedError


def dirty_session_paths(root):
    raise NotImplementedError


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
    raise NotRun("subcommand %s is not implemented yet" % a.cmd)


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run the selftest and watch it fail**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: a `NotImplementedError` traceback from `classify` (the first check calls it), `exit=1`.

- [ ] **Step 3: Implement the helpers**

Replace the five `raise NotImplementedError` bodies:

```python
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
```

- [ ] **Step 4: Run the selftest and watch it pass**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `session-branch selftest: PASS`, `exit=0`.

- [ ] **Step 5: Prove the parity check bites, then commit**

Run: `cp plugins/workflows-core/scripts/session-branch.py /tmp/sb.py && sed -i 's/|pr-draft|/|pr-drafts|/' plugins/workflows-core/scripts/session-branch.py && python3 plugins/workflows-core/scripts/session-branch.py --selftest | head -3; cp /tmp/sb.py plugins/workflows-core/scripts/session-branch.py`
Expected: `FAIL` naming `the script's ARTIFACT patterns equal specs-repo-git §2.1's`; after the copy back, `--selftest` passes again.

```bash
chmod +x plugins/workflows-core/scripts/session-branch.py
git add plugins/workflows-core/scripts/session-branch.py
git commit -m "feat(session-branch): script skeleton, the §2.1 classifier and its parity with the reference"
```

---

### Task 2: `mode` — the two keys and the identity, and `session` in branch-naming's skip list

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` (add `config`, `valid_identity`, `inferred_identity`, `identity`, `mode`; extend `dispatch`; tests)
- Modify: `plugins/workflows-core/references/branch-naming.md` (§2.3 prefix paragraph and §4 snippet's `skip`)

**Interfaces:**
- Consumes: `git`, `text`, `IDENTITY_SKIP` (Task 1).
- Produces: `mode(root, default) -> {"mode": "on"|"off", "source": "config"|"refused"|None, "identity": str|None, "identity_rung": "env"|"config"|"inferred"|None, "branch": str|None}`; `identity(root) -> (str|None, str|None)`.

- [ ] **Step 1: Write the failing tests** — append to `selftest()` before the summary:

```python
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
```

- [ ] **Step 2: Run and watch it fail**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `FAIL` listing the mode checks (`_rc: 2`, "subcommand mode is not implemented yet") and the branch-naming parity check (`session` missing there); `exit=1`.

- [ ] **Step 3: Implement `mode`**

Add above `selftest()`:

```python
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
```

Replace `dispatch`:

```python
def dispatch(a):
    if a.cmd == "mode":
        return mode(a.specs, a.default)
    raise NotRun("subcommand %s is not implemented yet" % a.cmd)
```

In `plugins/workflows-core/references/branch-naming.md`, in §4's snippet change
`skip='^(feat|feature|fix|bugfix|hotfix|docs|chore|release|story|idea|prd|ard|spec|design|ready|brd|frames|kb)$'`
to
`skip='^(feat|feature|fix|bugfix|hotfix|docs|chore|release|story|idea|prd|ard|spec|design|ready|brd|frames|kb|session)$'`,
and in §2.3 change the paragraph that begins **"The nine prefixes of the plugin's own specs-repository branches"** so its first sentence reads:
`**The nine prefixes of the plugin's own specs-repository branches — \`idea\`, \`prd\`, \`ard\`, \`spec\`, \`design\`, \`ready\`, \`brd\`, \`frames\` and \`kb\` (\`specs-repo-git.md\` §2.2) — and \`session\`, its session branches (\`specs-repo-git.md\` §8), are never a candidate.**`
and the §4 sentence after the snippet that begins "`skip` drops the generic prefixes" so it says "and the plugin's nine and `session`, which are never a candidate. When resolving a §1.4 prefix rather than an identity, take the generic names out of `skip` and keep the rest."

- [ ] **Step 4: Run and watch it pass**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `PASS`, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflows-core/scripts/session-branch.py plugins/workflows-core/references/branch-naming.md
git commit -m "feat(session-branch): mode — the opt-in key, the refusal record and the identity; session is never an identity"
```

---

### Task 3: `sync` — keep the session branch current, checkout-free, and align the overlay

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` (add `ensure_attributes`, `merge_tree_ok`, `align`, `sync`; extend `dispatch`; tests)

**Interfaces:**
- Consumes: Task 1 helpers.
- Produces: `sync(root, branch, default_ref) -> {"created": bool, "merged": bool, "fast_forward": bool, "tip": str, "conflict": [str], "deferred": [str], "aligned": [str]}`; `ensure_attributes(root) -> None`; `overlay_paths(root, tip) -> list[str]`; `unpreserved(root, tip) -> list[str]`; `write_from(root, commit, path) -> None`; `align(root, old_tip, new_tip) -> list[str]`.

- [ ] **Step 1: Write the failing tests** — append to `selftest()`:

```python
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
        b.git("rm", "-q", FB)
        b.git("commit", "-q", "-m", "delete feedback")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("fetch", "-q", "origin")
        got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("conflict") == [FB] and a.git("rev-parse", "session/aa") == c,
              "a modify/delete merge is reported and moves nothing (%r)" % got)
```

- [ ] **Step 2: Run and watch it fail**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `FAIL` on the sync checks (`subcommand sync is not implemented yet`); `exit=1`.

- [ ] **Step 3: Implement `sync`**

Add above `selftest()`:

```python
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
```

Extend `dispatch`:

```python
    if a.cmd == "sync":
        return sync(a.specs, a.branch, a.default_ref)
```

- [ ] **Step 4: Run and watch it pass**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `PASS`, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflows-core/scripts/session-branch.py
git commit -m "feat(session-branch): sync — fast-forward or union merge of the default branch, checkout-free, and the overlay aligned"
```

---

### Task 4: `commit` — the temporary-index commit, the stranded commits, then the merge

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` (add `create_at`, `ahead_paths`, `commit`; extend `dispatch`; tests)

**Interfaces:**
- Consumes: `sync`, `align`, `overlay_paths`, `classify`, `rev`, `blob` (Tasks 1, 3).
- Produces: `commit(root, branch, default_ref, message, include_ahead=False) -> {"committed": str|None, "files": int, "paths": [str], "created": bool, "stranded": int, "ahead_not_session": bool, "sync": dict}`.

- [ ] **Step 1: Write the failing tests** — append to `selftest()`:

```python
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
        check(subprocess.run(["git", "-C", a.path, "cat-file", "-e", "session/aa:" + odd]).returncode != 0,
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
```

- [ ] **Step 2: Run and watch it fail**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `FAIL` on the commit checks; `exit=1`.

- [ ] **Step 3: Implement `commit`**

Add above `selftest()`:

```python
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
```

Extend `dispatch`:

```python
    if a.cmd == "commit":
        return commit(a.specs, a.branch, a.default_ref, a.message, a.include_ahead)
```

- [ ] **Step 4: Run and watch it pass**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `PASS`, `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add plugins/workflows-core/scripts/session-branch.py
git commit -m "feat(session-branch): commit — temporary-index commit from the checkout's base, stranded commits carried, then the merge"
```

---

### Task 5: `lift` and `put-back`, and the whole loop across two clones

**Files:**
- Modify: `plugins/workflows-core/scripts/session-branch.py` (add `lift`, `put_back`; extend `dispatch`; tests)

**Interfaces:**
- Consumes: `commit`, `sync`, `write_from`, `unpreserved`, `overlay_paths`, `dirty_session_paths`, `blob`, `worktree_blob` (Tasks 1–4).
- Produces: `lift(root, branch) -> {"lifted": [str], "unpreserved": [str]}`; `put_back(root, branch, default_ref) -> {"written": [str], "removed": [str], "skipped": [str], "sync": dict}`.

- [ ] **Step 1: Write the failing tests** — append to `selftest()`:

```python
    # ---- lift and put-back -----------------------------------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        fu = "specifications/PRD-A-1-x/follow-ups.md"
        a.write(FB, "## a1\nmine\n", append=True)
        got = a.run("lift", "--branch", "session/aa")
        check(got.get("unpreserved") == [FB] and not got.get("lifted") and "## a1" in a.read(FB),
              "lift refuses, and discards nothing, where a session file is not on the branch (%r)" % got)
        a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        a.write(fu, "- [ ] task\n")
        a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        got = a.run("lift", "--branch", "session/aa")
        check(sorted(got.get("lifted", [])) == sorted([FB, fu]) and not got.get("unpreserved"),
              "lift returns preserved files to HEAD (%r)" % got)
        check(a.read(fu) is None and "## a1" not in a.read(FB) and a.git("status", "--porcelain") == "",
              "an untracked one is removed and a tracked one restored: the checkout is clean")
        got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
        check(sorted(got.get("written", [])) == sorted([FB, fu]) and "## a1" in a.read(FB) and a.read(fu),
              "put-back writes the branch's versions back (%r)" % got)
    # the whole loop: two users, a merged pull request, a catch-up through lift and put-back
    for how in ("merge", "squash"):
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\nfrom a\n", append=True)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.git("push", "-q", "-u", "origin", "session/aa")
            merge_on_remote(tmp, remote, "session/aa", how)
            b.write(FB, "## b1\nfrom b\n", append=True)
            b.git("fetch", "-q", "origin")
            got = b.run("lift", "--branch", "session/bb")
            if got.get("unpreserved"):
                b.run("commit", "--branch", "session/bb", "--default-ref", "origin/main", "--message", "A-1 Add session")
                got = b.run("lift", "--branch", "session/bb")
            check(not got.get("unpreserved"), "[%s] b lifts once its files are on its branch (%r)" % (how, got))
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            got = b.run("put-back", "--branch", "session/bb", "--default-ref", "origin/main")
            fb = b.read(FB)
            check("## a1" in fb and "## b1" in fb, "[%s] b's checkout holds a's merged entry and its own (%r)" % (how, fb))
            on_branch = b.git("show", "session/bb:" + FB)
            check("## a1" in on_branch and "## b1" in on_branch, "[%s] …and so does b's session branch" % how)
            a.git("fetch", "-q", "origin")
            got = a.run("lift", "--branch", "session/aa")
            check(not got.get("unpreserved"), "[%s] a lifts (%r)" % (how, got))
            a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.git("diff", "--name-only", "HEAD", "session/aa", "--", FB) == "",
                  "[%s] once its pull request merged, a's branch holds nothing for that file main lacks (%r)" % (how, got))
            check(a.git("status", "--porcelain", "--", FB) == "", "[%s] …so a's checkout shows it clean" % how)
    # a switch to a deliverable branch cut from an older main, with the overlay present
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        a.git("branch", "prd/A-1-x")
        b.write(FB, "## team\n", append=True)
        b.commit_all("team")
        b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
        a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
        a.write(FB, "## a1\n", append=True)
        a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        check(subprocess.run(["git", "-C", a.path, "switch", "-q", "prd/A-1-x"], stdout=devnull,
                             stderr=devnull).returncode != 0, "git refuses the switch over the overlay (the reason for lift)")
        a.run("lift", "--branch", "session/aa")
        a.git("switch", "-q", "prd/A-1-x")
        got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
        fb = a.read(FB)
        check(fb is not None and "## a1" in fb and "## team" in fb, "lift, switch, put-back: nothing lost (%r)" % fb)
    # a working copy that is neither HEAD's nor the branch's is never overwritten
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        a.write(FB, "## a1\n", append=True)
        a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        a.git("checkout", "--", FB)
        a.write(FB, "## typed by hand\n", append=True)
        got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
        check(got.get("skipped") == [FB] and "## typed by hand" in a.read(FB), "put-back skips a foreign working copy (%r)" % got)
    # line endings: an eol=crlf session file is preserved as its LF blob, and put back in CRLF
    with tempfile.TemporaryDirectory() as tmp:
        remote, a, b = world(tmp)
        a.write(".gitattributes", "*.md text eol=crlf\n")
        a.commit_all("crlf")
        os.remove(os.path.join(a.path, FB))
        a.git("checkout", "--", FB)  # checked out again, now in CRLF
        a.write(FB, "## a1\r\n", append=True)
        a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
        got = a.run("lift", "--branch", "session/aa")
        check(not got.get("unpreserved"), "a CRLF working copy of an LF blob counts as preserved (%r)" % got)
        a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
        check("## a1\r\n" in (a.read(FB) or ""), "put-back writes the smudged, CRLF form")
```

- [ ] **Step 2: Run and watch it fail**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `FAIL` on the lift and put-back checks; `exit=1`.

- [ ] **Step 3: Implement `lift` and `put-back`**

Add above `selftest()`:

```python
def lift(root, branch):
    """Return every dirty session file to HEAD, but only once each is preserved on <branch>: its
    working copy is the tip's version. Otherwise list the ones that are not and discard nothing."""
    tip = rev(root, "refs/heads/" + branch)
    held = unpreserved(root, tip)
    if held:
        return {"lifted": [], "unpreserved": held}
    dirty = dirty_session_paths(root)
    for p in dirty:
        tracked = git(root, "ls-files", "--error-unmatch", "--", ":(literal)" + p, check=False).returncode == 0
        if tracked or blob(root, "HEAD", p) is not None:
            git(root, "restore", "--source=HEAD", "--staged", "--worktree", "--", ":(literal)" + p)
        else:
            os.remove(os.path.join(root, p))
    return {"lifted": dirty, "unpreserved": []}


def put_back(root, branch, default_ref):
    """Merge <default-ref> into <branch>, then write each session file where the branch differs from
    HEAD, or remove it where the branch lacks it. A working copy that is neither HEAD's nor the
    branch's version is left as it is and listed in skipped."""
    ref = "refs/heads/" + branch
    if rev(root, ref) is None:
        return {"written": [], "removed": [], "skipped": [], "sync": None}
    synced = sync(root, branch, default_ref)
    tip = rev(root, ref)
    written, removed, skipped = [], [], []
    for p in nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", "HEAD", tip)):
        if not classify(p):
            continue
        want, have = blob(root, tip, p), worktree_blob(root, p)
        if have == want:
            continue
        if have != blob(root, "HEAD", p):
            skipped.append(p)
            continue
        write_from(root, tip, p)
        (removed if want is None else written).append(p)
    return {"written": written, "removed": removed, "skipped": skipped, "sync": synced}
```

Extend `dispatch`:

```python
    if a.cmd == "lift":
        return lift(a.specs, a.branch)
    if a.cmd == "put-back":
        return put_back(a.specs, a.branch, a.default_ref)
```

and change its last line to `raise NotRun("unknown subcommand %s" % a.cmd)`.

- [ ] **Step 4: Run and watch it pass**

Run: `python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "exit=$?"`
Expected: `PASS`, `exit=0`. Then run it three more times in a row and confirm `PASS` each time (fixtures are timing-independent).

- [ ] **Step 5: Mutation check, then commit**

Run: `cp plugins/workflows-core/scripts/session-branch.py /tmp/sb.py && python3 - <<'EOF'
p = "plugins/workflows-core/scripts/session-branch.py"; s = open(p).read()
s = s.replace("    held = unpreserved(root, tip)\n    if held:\n        return {\"lifted\"", "    held = []\n    if held:\n        return {\"lifted\"", 1)
open(p, "w").write(s)
EOF
python3 plugins/workflows-core/scripts/session-branch.py --selftest | head -4; cp /tmp/sb.py plugins/workflows-core/scripts/session-branch.py`
Expected: `FAIL` naming "lift refuses, and discards nothing, where a session file is not on the branch".

```bash
git add plugins/workflows-core/scripts/session-branch.py
git commit -m "feat(session-branch): lift and put-back around a move of the checkout; the two-clone loop, a switch and line endings tested"
```

---

### Task 6: CI, and the pages a user reads

**Files:**
- Modify: `.github/workflows/validate-catalog.yml` (a step running the selftest)
- Modify: `plugins/workflows-core/docs/reference/environment.md` (the `workflows.sessionBranch` key, the overlay, the two hand commands)

- [ ] **Step 1: Add the CI step**

In `.github/workflows/validate-catalog.yml`, after the step that runs `architecture-harvest.py --selftest`, add a step in the same shape:

```yaml
      - name: session-branch selftest
        run: python3 plugins/workflows-core/scripts/session-branch.py --selftest
```

- [ ] **Step 2: Document the key and the overlay**

In `plugins/workflows-core/docs/reference/environment.md`, after the `$SPECS_PATH` section, add a section in the page's own style:

```markdown
### A specs repository whose default branch takes no push

Where your specs repository protects its default branch, the plugin cannot push the session files it commits there — feedback, cost, follow-ups, the implementation record, the release-notes draft and the resume pointer. The first push the server refuses switches that clone to **session-branch mode**; you can switch it on in advance with `git -C "$SPECS_PATH" config workflows.sessionBranch true`. In the mode, those files go to a branch of your own, `session/<your initials>` (from `GIT_USER_INITIALS` or `git config user.initials`), which the plugin keeps merged with the default branch and pushes; merge its pull request to land them. The run's `Specs repo:` line gives the `gh pr create` command the first time.

Until that pull request merges, your specs checkout shows those files as modified or untracked: that is where every command reads and appends them. If git refuses a switch or a pull you make by hand because of them, run `python3 <workflows-core>/scripts/session-branch.py --specs "$SPECS_PATH" lift --branch session/<your initials>` first, and `… put-back --branch session/<your initials> --default-ref origin/<default>` after; the next plugin run does the same on its own. To leave the mode, `git -C "$SPECS_PATH" config --unset workflows.sessionBranch` and `git -C "$SPECS_PATH" config --unset branch.<default>.workflowsPushRefused`, once the session pull request has merged.
```

(`<workflows-core>` is the installed plugin's directory; the page already says where installed plugins live — if it does not, write `~/.claude/plugins/cache/<marketplace>/workflows-core/<version>`.)

- [ ] **Step 3: Run the gates**

Run: `python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . ; echo "EXIT=$?"`
Expected: `EXIT=0`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/validate-catalog.yml plugins/workflows-core/docs/reference/environment.md
git commit -m "ci,docs(session-branch): run the selftest; the environment page documents the mode, its key and the overlay"
```

---

### Task 7: `workflows-core:specs-repo-git` — §8 and its hooks

**Files:**
- Modify: `plugins/workflows-core/references/specs-repo-git.md` (§1 rules 3, 4, 8; §3.4; §3.5; §4 steps 1, 2, 4, 5; §4.1; §5 G2; §6; new §8)

This file is hard-wrapped at about 80 columns in its numbered lists and unwrapped in its paragraphs; match the surrounding form at each edit. Read the whole file before editing (it loads `.claude/rules/workflows-core-git.md`).

- [ ] **Step 1: Add §8** after §7 (the caller contract), as the file's last section:

```markdown
## 8. Session-branch mode — a default branch that takes no push

Where the specs repository's default branch takes no direct push — branch protection, a ruleset, a policy or a hook — this reference keeps the run's session files on a per-user **session branch**, and the user lands them through its pull request. Everything above stands; this section says only what changes in the mode. `${CLAUDE_PLUGIN_ROOT}/scripts/session-branch.py` does the git plumbing, every call `--specs "$SPECS_PATH"`, and a change to either is a change to both. Each call prints one JSON object; exit 2 means it could not run, which is reported with its stderr while the run goes on (§1 rule 5).

### 8.1 When the mode is on

At §3.2 — and at §4 step 1 on a run that ran no preflight — run `… mode --default <default>`. It prints `{mode, source, identity, branch}`. `mode` is `on` where `git config --bool workflows.sessionBranch` prints `true`, the user's own opt-in, which this reference reads and never writes; or where `branch.<default>.workflowsPushRefused` is set, which §4 step 6 records when `origin` refuses a push to the default branch. Both are local to the clone. `branch` is `session/<identity>`, `<identity>` from `branch-naming.md` §2's first three rungs, never its prompt. Where it is null the run commits nothing in the mode: its session files stay in the working tree for the next run, and §6's *no identity* line names `GIT_USER_INITIALS`.

Where the mode is on, carry `session_branch: <branch>` for the whole run. §3.1's gate, `specs_git: misrooted`, G0 and G1 gate the mode exactly as they gate everything else. G2 no longer decides where the files land: in the mode they go to the session branch whatever the checkout stands on (§5).

### 8.2 Committing

In the mode nothing in this reference commits a session file on the checked-out branch. Where §3.4's flush or §4 step 4 would commit, run `… commit --branch <session branch> --default-ref <default-ref> --message "<that step's message>"`, adding `--include-ahead` where HEAD is the default branch. It:

1. creates the session branch where it does not exist, at the commit the checkout's files come from (`git merge-base HEAD <default-ref>`);
2. commits every dirty session-file path (§2.1's classifier) onto it through a temporary index — with `--include-ahead`, also the files of the commits on the local default branch that `<default-ref>` lacks, where every one of them is a session-file commit (the ones a refused push left there) — moving neither the checkout, the index nor HEAD;
3. then merges `<default-ref>` in where the branch lacks it — a fast-forward where the branch holds nothing of its own, else `git merge-tree --write-tree -X ours` with git's `union` driver for the appended shapes, kept as one marked block in `$GIT_DIR/info/attributes` — so a teammate's entries and this run's both survive, and an overwritten file keeps this run's version;
4. and brings each working copy that still matches the branch's previous version up to the merged one.

It prints `{committed, files, paths, created, stranded, ahead_not_session, sync}`. `committed: null` is §4 step 3's *nothing to commit*. A non-empty `sync.conflict` names files the merge could not settle: the commit stands on the unmerged branch and §6's line names them.

### 8.3 The overlay, around every move of the checkout

In the mode the working tree's session files hold the session branch's version wherever it differs from HEAD, so every command keeps reading and appending them where it always has. Git refuses to fast-forward or switch over such a working copy, even a byte-identical one, so every move of the specs checkout is wrapped:

- **Before it, `… lift --branch <session branch>`.** Where a dirty session file is not yet on the session branch it prints `unpreserved: [...]` and changes nothing: run §8.2's `commit`, then `lift` again. A second `unpreserved` skips the move, which the step that wanted it reports as it would a refused switch or pull; nothing is discarded. Otherwise it returns each dirty session file to HEAD — the one discard this reference makes (§1 rule 4), and only of content it has just found on the session branch.
- **After it, `… put-back --branch <session branch> --default-ref <default-ref>`.** It merges `<default-ref>` in as §8.2 step 3 does, then writes each session file where the branch differs from the new HEAD, or removes it where the branch lacks it. A path whose working copy is neither HEAD's nor the branch's is left as it is and listed in `skipped`.

The moves: §3.4's catch-up and §4 step 2's repeat of it; §3.5's B2 (switch, pull, `branch -d`), B4 (switch, pull) and the re-run's switch back; `phase-handoff.md` §2.2's switch onto a new or reused deliverable branch, and its §3.3 row C repair; and a direct `/dev-workflows:implement` run from inside the specs repository, around its own branch and commit (its Pre-Phase 3 and Phase 4.6). **The preflight ends with `put-back` in the mode** whether or not it moved the checkout, so a run interrupted between a `lift` and its `put-back` finds its overlay restored.

### 8.4 Pushing, and the line

§4 step 5 pushes the session branch in place of the checked-out one — `git -C "$SPECS_PATH" push --porcelain -u origin <session branch>` — under step 5's conditions as they stand, and §3.4's retry treats the session branch as the current branch. `push-scope` admits one more kind of commit on this branch alone: the script's own merge of `<default-ref>`, two parents, the second reachable from `<default-ref>`. Step 6 reads the outcome as for any branch. The outcome line is §6's *session branch* row.
```

- [ ] **Step 2: Hook §1.** Append to rule 3: ``The session branch, `session/<identity>` (§8), is the plugin's too, for commit and push only: it is never checked out, switched to, switched away from or deleted, and it is not in that pattern.`` Append to rule 4: ``§8.3's `lift` is the one discard: it returns to HEAD a session file whose exact content it has just found on the session branch.`` Change rule 8's heading sentence to "**Configuration of its own.**" and its text to list `branch.<branch>.workflowsPushRefused` and §8.2's marked block in `$GIT_DIR/info/attributes`, then: "`workflows.sessionBranch` is the user's own key; this reference reads it and never writes it."

- [ ] **Step 3: Hook §3.4.** After the catch-up paragraph's first sentence add: "In session-branch mode (§8) the catch-up is wrapped in `lift` and `put-back` (§8.3)." In the *Dirty ARTIFACT paths exist* bullet add: "In the mode the flush commits through §8.2 and pushes the session branch (§8.4)." In the *No dirty ARTIFACT path* bullet add: "In the mode the session branch is the branch retried."

- [ ] **Step 4: Hook §3.5.** After the table add: "**In session-branch mode** (§8), B2's and B4's switch and pull, and the re-run's switch back, are each wrapped in `lift` and `put-back` (§8.3), and the preflight ends with `put-back`. HEAD on the session branch is not a row's subject: G2 has already kept the run there."

- [ ] **Step 5: Hook §4.** Step 1: after the gate's flags, "then, on a run that ran no preflight, resolve the mode (§8.1)". Step 2: "In session-branch mode, §8.2's `commit` enumerates instead; run §3.4's catch-up wrapped as §8.3 says." Step 4: "In session-branch mode, §8.2's `commit` replaces this step's commit and index restore; its `committed` and `files` fill §6's line." Step 5: "In session-branch mode the branch pushed is the session branch (§8.4)." §4.1: add the bullet "**In session-branch mode** (§8) — on the session branch, whatever the checkout stands on."

- [ ] **Step 6: Hook §5 and §6.** After the G2 block add: "**In session-branch mode** (§8) G2's *Not done* line reads `the preflight did not switch away from it — the plugin manages only branches it created. This run's artifacts WILL be committed on session/<identity>, the session branch this specs repository uses because its default branch takes no push, and not on <branch>.`" In §6's table add, after the *Committed and pushed* row:

```markdown
| Committed on the session branch and pushed (§8) | `Specs repo: committed <sha7> (<N> files) on session/<identity> — pushed; <M> commit(s) not on <default> yet: merge its pull request, or open one with gh pr create --head session/<identity> --base <default>`, `<M>` from `git rev-list --count --no-merges <default-ref>..session/<identity>` |
| Session-branch mode, no identity (§8.1) | `Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set GIT_USER_INITIALS (or git config user.initials), and the next run commits these files` |
```

and after the table: "In session-branch mode the not-pushed rows name the session branch as `<branch>`. Where §8.2 printed `stranded` above 0, append `; your local <default> still holds <K> commit(s) origin refused — their files are on session/<identity> now; drop them with git -C "<SPECS_PATH>" reset --keep origin/<default>, standing on <default>`. Where `sync.conflict` is not empty, append `; merging <default> into session/<identity> left <path>[, …] unsettled — settle them in its pull request`."

- [ ] **Step 7: Read the file end to end, then run the gates and the selftest**

Run: `python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/session-branch.py --selftest; echo "EXIT=$?"`
Expected: `EXIT=0` (the selftest's classifier parity still passes: §2.1 is untouched).

- [ ] **Step 8: Commit**

```bash
git add plugins/workflows-core/references/specs-repo-git.md
git commit -m "feat(specs-repo-git): §8 session-branch mode — the mode, committing through the session branch, the overlay around every move, pushing and the line"
```

---

### Task 8: `phase-handoff` and `/implement`

**Files:**
- Modify: `plugins/workflows-core/references/phase-handoff.md` (§1 rule 4; §2.2; §3.3 row C)
- Modify: `plugins/dev-workflows/commands/implement.md` (Phase 0's direct-run notice; Pre-Phase 3 step 1; Phase 4.6)

- [ ] **Step 1: `phase-handoff`.** Append to §1 rule 4: "save `specs-repo-git.md` §8.3's `lift`, which returns to HEAD only a session file it has just found on the session branch." After §2.2's rule 4 add: "**In session-branch mode** (`specs-repo-git.md` §8), the switch onto `<name>` — creating it or reusing it — is wrapped in that section's `lift` and `put-back` (§8.3); a `lift` that skips the move refuses the handoff with the reason, as a failed switch does." In §3.3, change "On the first choice: `git -C "$SPECS_PATH" switch <default>` then `git -C "$SPECS_PATH" pull --ff-only`, then re-test **once**." so the two commands are followed by "— in session-branch mode wrapped in `lift` and `put-back` (`specs-repo-git.md` §8.3) —".

- [ ] **Step 2: `/implement`.** Read `implement.md` (it loads its rules files). In Phase 0's direct-run notice paragraph ("**On a direct run, print one line and run on**"), add after the two notice forms: "In session-branch mode (`workflows-core:specs-repo-git` §8) the line instead ends `… and the session files it writes into the specs tree go to session/<identity>, as this specs repository's default branch takes no push, never onto this run's branch.`" In Pre-Phase 3 step 1 (the clean-tree check) add as its first sentence: "On a direct run from inside the specs repository in session-branch mode, run §8.3's `lift` first, so neither this check nor the code commit sees a session file; every exit from here on runs §8.3's `put-back` once — Phase 4.6 after its commit, and each stop before it." In Phase 4.6 add after its first paragraph: "On a direct run from inside the specs repository in session-branch mode, run `put-back` (`workflows-core:specs-repo-git` §8.3) after the commit, whatever the push choice."

- [ ] **Step 3: Gates, then commit**

Run: `python3 scripts/validate-catalog.py && ./scripts/check-docs.sh --root . ; echo "EXIT=$?"`
Expected: `EXIT=0`.

```bash
git add plugins/workflows-core/references/phase-handoff.md plugins/dev-workflows/commands/implement.md
git commit -m "feat(phase-handoff,implement): wrap the deliverable switch, row C's repair and a direct run inside the specs repository in lift and put-back"
```

---

### Task 9: Sweep, rules, rationale, the spec's amendments, CHANGELOGs, versions, walkthrough

**Files:**
- Modify: the docs pages that say when session files are pushed (find them by `grep -rln "none at all, one your git configuration" plugins/*/docs`), `.claude/rules/workflows-core-git.md`, `docs/maintainers/rationale.md`, `docs/superpowers/specs/2026-10-06-session-branch-design.md`, every touched plugin's `CHANGELOG.md`, `plugin.json` and `.claude-plugin/marketplace.json`.

- [ ] **Step 1: Docs sweep.** On each page the grep lists, after the sentence that names when the files are not pushed, add: "On a specs repository whose default branch takes no push, they go to your session branch instead, and you merge its pull request (`workflows-core` environment page)." Then sweep the claim's subject — where session files are committed and pushed — across `plugins/` (docs included), `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` by phrase (`committed on`, `pushes only`, `the default branch`, `commit-artifacts`), and read each hit's paragraph against §8.

- [ ] **Step 2: Rules file.** In `.claude/rules/workflows-core-git.md`'s `specs-repo-git` authority paragraph, add before "It bounds the plugin's": "§8's session-branch mode — where the default branch takes no push (opt-in `workflows.sessionBranch`, or the refusal record), session files go to `session/<identity>` through `scripts/session-branch.py`, kept merged with the default branch and lifted and put back around every move of the checkout ([why](../../docs/maintainers/rationale.md#session-branch))." Keep the file under 20,000 characters: `python3 -c "print(len(open('.claude/rules/workflows-core-git.md').read()))"`.

- [ ] **Step 3: Rationale.** Append `## session-branch` to `docs/maintainers/rationale.md`: the problem, the measurements (the fast-forward refusal over a byte-identical working copy; the union merge through `merge-tree`), the user's decisions (by pull request; overlay; automatic and opt-in; the user opens the pull request; a script), the six planning amendments, and the refused alternatives (a second checkout; per-session files; opening the pull request; moving the user's default branch; always-PR, with its reasons).

- [ ] **Step 4: The spec's amendments.** Append to the spec a section `## Amended during planning` listing this plan's six amendments in one line each.

- [ ] **Step 5: Versions and CHANGELOGs.** Fetch `origin/main` and read each touched plugin's current version there; bump `workflows-core` and `dev-workflows` one minor (a new capability), and any other plugin whose docs changed one patch, in `plugin.json` and `marketplace.json` alike. Add a dated entry to each CHANGELOG saying what the user gets: the mode, its two triggers, where the files go, the line with the `gh pr create` command, the overlay and the two hand commands.

- [ ] **Step 6: Walkthrough, and the verification record (written last).** In a scratch directory, build a bare remote whose pre-receive refuses `main` and one clone; run by hand the sequence one run executes — `mode`, a flush `commit`, the catch-up's `lift` / `pull --ff-only --no-rebase` / `put-back`, a deliverable switch wrapped the same way, the terminal `commit`, `git push --porcelain -u origin session/<identity>` — and record each command's JSON and the final `git status` in a `## Verification` section at the end of this plan, with the selftest's last `PASS` line and the gate chain's `EXIT=0`.

- [ ] **Step 7: Gates and commit**

Run the whole chain from `.github/workflows/validate-catalog.yml`'s `run:` steps, including the new selftest; read the printed exit.
Expected: `EXIT=0`, `0 error(s), 0 warning(s)`.

```bash
git add -A
git commit -m "docs(session-branch): pages, rules, rationale and the spec's planning amendments; CHANGELOGs and versions; the walkthrough recorded"
```

---

### Task 10: Whole-branch review (this repository)

- [ ] **Step 1:** Dispatch a fresh reviewer on the most capable model with `git diff origin/main..HEAD`, this plan, the spec, and this plan's *Review Focus* verbatim; READ-ONLY, throwaway repositories allowed under the scratchpad; findings only for this change and stale copies of the claims it edits.
- [ ] **Step 2:** Fix every Critical and Important finding, each with a selftest case that failed first where the finding is in the script; re-review; at most three rounds. After the last round, or once a round has no Important finding, fix its Minor findings without a re-review and say so.

### Task 11: Port to the internal edition (port agent, one review)

- [ ] **Step 1:** Fresh worktree from that repository's `origin/main`. A port agent ports the script (beside its `plugins/dev-workflows/scripts/session-cost.py`, its own §2.1 classifier and branch prefixes, selftest wired to its own references), the reference sections, `/implement`, docs, rules and CHANGELOG — by meaning, whole paragraphs, its own citations; runs its gate chain, adding the selftest to its CI.
- [ ] **Step 2:** One review round on the most capable model; fix every finding without a re-review.

### Task 12: Port to the Copilot edition (port agent, one review)

- [ ] **Step 1:** Fresh worktree; the script under `dev-workflows/scripts/`, its own classifier and prefixes; `_shared/specs-repo-git.md`, `phase-handoff.md`, `branch-naming.md`, `implement/SKILL.md`, docs, instructions (each `.instructions.md` ≤ 20,000 characters), CHANGELOG; CI gains the selftest.
- [ ] **Step 2:** One review round; fix every finding without a re-review.

### Task 13: Land

- [ ] **Step 1:** For each repository: fetch; where `origin/main` moved, merge it into the branch, resolve versions and CHANGELOGs above it, re-run the gates; merge `--no-ff` in a temporary worktree from `origin/main`; run the gate chain there with `ASSERT_PUBLISHED=1`; push (the Copilot edition to each of its remotes); remove the worktrees; delete the merged branches; fast-forward a clean local `main`; watch this repository's CI to its result.

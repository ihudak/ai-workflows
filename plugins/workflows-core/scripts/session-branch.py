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
level, an unexpected git failure, any other exception), printing one "session-branch: not run
(...)" line on stderr; the caller reports it and the run continues.
"""

import argparse
import contextlib
import io
import json
import os
import re
import shutil
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
    r"^security/[^/]+/(runs/|scans/|dev-workflows/|register\.(json|md)$)",
    r"^(specs|specifications|vis)/.+/(implementation|follow-ups|pr-draft|[^/]+-implementation-gaps|_security)\.md$",
]
EXCLUDED = (r"^(specs|specifications|vis)/(.+/)?(brd|grounding|interview|design|attachments|revisions"
            r"|bundle-[0-9]{8}|customer-sent-[0-9]{8}|Doc screenshots)/")
_ARTIFACT_RE = [re.compile(p) for p in ARTIFACT]
_EXCLUDED_RE = re.compile(EXCLUDED)

# branch-naming §4's skip list; the selftest fails where they differ.
IDENTITY_SKIP = frozenset(("feat", "feature", "fix", "bugfix", "hotfix", "docs", "chore", "release", "story",
                           "idea", "prd", "ard", "spec", "epics", "design", "ready", "brd", "frames", "kb", "conformance",
                           "session"))

# The appended shapes merge with git's union driver. The overwritten ones are unset (-merge), so a
# merge keeps the session branch's version whole (merge-tree -X ours) rather than splicing two
# versions line by line; resume.md sits under dev-workflows/, so it is taken out again.
ATTR_BEGIN = "# BEGIN workflows-core session-branch: written by session-branch.py, do not edit"
ATTR_END = "# END workflows-core session-branch"
ATTRIBUTES = [
    "**/dev-workflows/** merge=union",
    "dev-workflows-feedback/** merge=union",
    "dev-workflows-cost/** merge=union",
    "**/implementation.md merge=union",
    "**/follow-ups.md merge=union",
    "**/_security.md merge=union",
    "**/*-implementation-gaps.md merge=union",
    "**/dev-workflows/resume.md -merge",
    "**/pr-draft.md -merge",
    "security/*/register.json -merge",
    "security/*/register.md -merge",
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


# The heading that opens an entry of every block-shaped appended format, pinned from the references
# that define them: implementation-format §1 "## <YYYY-MM-DD> — /implement", feedback-emission §1
# "## <YYYY-MM-DD> — <command> — <category>", /security-workflows:scan §7.3
# "## <YYYY-MM-DD> — /security-workflows:scan", cost-emission §6
# "## <YYYY-MM-DDTHH:MM:SSZ> — <command> — <phase>" (the em dash in UTF-8). A "## " line of any other
# shape inside an entry's body stays in that entry. Never loosened to make a test pass.
ENTRY_HEAD = re.compile(rb"^## \d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z)? \xe2\x80\x94 ", re.M)

# How a session file both sides changed is settled (spec §3.3), by path and never by check-attr: a
# repository .gitattributes outranks any block this script passes. A runs/ or scans/ record has no
# class: where it conflicts, it is refused as anything else is.
_RECORD_RE = re.compile(r"^security/[^/]+/(runs|scans)/")
_REGISTER_RE = re.compile(r"^security/[^/]+/register\.(json|md)$")
_LINES_RE = re.compile(r"(^|/)follow-ups\.md$")
_WHOLE_RE = re.compile(r"(^|/)(dev-workflows/resume|pr-draft|[^/]+-implementation-gaps)\.md$")
_BLOCK_RE = re.compile(r"(^|/)(implementation|_security)\.md$|(^|/)dev-workflows/|^dev-workflows-(feedback|cost)/")


def merge_class(path):
    """The class of a session file: "block" (an appended file, settled as a set of entries), "lines"
    (follow-ups.md, one task per line: git's union), "whole" (an overwritten file: one side's version
    whole), "register" (a security register, rebuilt), or None (not a session file, or a runs/ or
    scans/ record)."""
    if not classify(path) or _RECORD_RE.search(path):
        return None
    if _REGISTER_RE.search(path):
        return "register"
    if _LINES_RE.search(path):
        return "lines"
    if _WHOLE_RE.search(path):
        return "whole"
    if _BLOCK_RE.search(path):
        return "block"
    return None


def split_entries(data):
    """The header (the bytes before the first ENTRY_HEAD line) and the entries, each from an
    ENTRY_HEAD line to the next one or the end."""
    starts = [m.start() for m in ENTRY_HEAD.finditer(data)]
    if not starts:
        return data, []
    return data[:starts[0]], [data[a:b] for a, b in zip(starts, starts[1:] + [len(data)])]


def entry_key(chunk):
    """What a header or an entry is compared by: its bytes with every trailing space, tab and line
    ending removed (its trailing blank lines with them), so an entry last on one side, with or without
    a newline or a blank line after it, matches itself on the other."""
    return chunk.rstrip(b" \t\r\n")


def _line_ending(chunk, last=False):
    """\\r\\n where the chunk's first line ending (with last, its last one) is \\r\\n, else \\n."""
    i = chunk.rfind(b"\n") if last else chunk.find(b"\n")
    return b"\r\n" if i > 0 and chunk[i - 1:i] == b"\r" else b"\n"


def entry_set_merge(base, ours, theirs):
    """Spec §3.3's settlement of a block-shaped appended file both sides changed, from three
    versions; base is None where both sides created it. None (refuse) where the two headers differ,
    or where an entry of base is missing from either side: an edit, a removal, or an addition to the
    last entry. Otherwise ours, given a final line ending where it lacks one, then each entry of
    theirs that ours lacks, in theirs' order, after one empty line, with its trailing blank lines
    dropped and one line ending, its own lines unchanged. Each line ending added is \\r\\n where the
    entry's first line ends \\r\\n (for the one added to ours, where ours' last line ending is
    \\r\\n), else \\n. Base decides only the refusal; it need not be a prefix of either side. A
    caller decides a deleted side."""
    head_o, ents_o = split_entries(ours)
    head_t, ents_t = split_entries(theirs)
    if entry_key(head_o) != entry_key(head_t):
        return None
    have_o = {entry_key(e) for e in ents_o}
    if base is not None:
        have_t = {entry_key(e) for e in ents_t}
        if any(entry_key(e) not in have_o or entry_key(e) not in have_t for e in split_entries(base)[1]):
            return None
    out = ours
    if out and not out.endswith(b"\n"):
        out += _line_ending(out, last=True)
    for e in ents_t:
        k = entry_key(e)
        if k in have_o:
            continue
        end = len(k)
        while e[end:end + 1] in (b" ", b"\t"):  # the last line's own trailing spaces are the entry's
            end += 1
        eol = _line_ending(e)
        out += (eol if out else b"") + e[:end] + eol
    return out


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


def refusal_record(root, branch):
    """specs-repo-git §1 rule 8: the date §4 step 6 recorded when origin refused a push to this
    branch -- a file in the common git directory, which a hardened container's read-only
    .git/config does not stop, standing wherever it exists -- else the config key an older run, or
    a run that could not write the file, recorded; else None. The directory is resolved as
    placed_file resolves its own, so no git newer than the rest of this script needs is assumed."""
    r = git(root, "rev-parse", "--git-common-dir", check=False)
    if r.returncode == 0 and text(r):
        common = text(r) if os.path.isabs(text(r)) else os.path.join(root, text(r))
        path = os.path.join(common, "workflows", "push-refused", branch)
        if os.path.isfile(path):
            try:
                with open(path, encoding="utf-8") as fh:
                    return fh.read().strip() or "an earlier run"
            except (OSError, ValueError):
                return "an earlier run"
    return config(root, "branch.%s.workflowsPushRefused" % branch)


def mode(root, default):
    on = config(root, "workflows.sessionBranch", as_bool=True) == "true"
    refused = refusal_record(root, default)
    source = "config" if on else ("refused" if refused else None)
    ident, rung = identity(root)
    state = "off"
    if source:
        state = "on" if merge_tree_ok(root) else "unsupported"
    return {"mode": state, "source": source, "identity": ident, "identity_rung": rung,
            "branch": ("session/" + ident) if ident else None}


def ensure_attributes(root):
    """Keep exactly one marked block of ATTRIBUTES in the repository's info/attributes, other lines untouched."""
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


def placed_file(root):
    """This worktree's record of the session files the overlay put in it: path -> the blob it last
    wrote there or committed from there. Per worktree, since a second worktree of the same repository
    holds a copy of its own, or none."""
    path = text(git(root, "rev-parse", "--git-path", "session-branch-placed.json"))
    return path if os.path.isabs(path) else os.path.join(root, path)


def read_placed(root):
    try:
        with open(placed_file(root), encoding="utf-8") as fh:
            value = json.load(fh)
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def mark(root, put=None, drop=(), clear=False):
    placed = {} if clear else read_placed(root)
    new = dict(placed)
    new.update(put or {})
    for p in drop:
        new.pop(p, None)
    if new != read_placed(root):
        path = placed_file(root)
        with open(path + ".tmp", "w", encoding="utf-8") as fh:
            json.dump(new, fh, sort_keys=True)
        os.replace(path + ".tmp", path)


# The one session-file shape a run deletes: cost-emission §9 relocates a pending cost file into its
# PRD's folder, then deletes it. Any other absent session file is an overlay not in place.
RUN_DELETES = re.compile(r"^dev-workflows-cost/")


def not_in_place(w, h, path, pv):
    """True where the working copy holds nothing of the run's own: it is HEAD's version, or the
    version this worktree was last given (pv) — the overlay is not in place here (a lift, a second
    worktree, a switch back, a hand removal) or another worktree moved the branch on. An absent file
    is the run's own deletion only in RUN_DELETES' shape, and only where HEAD holds it or this
    worktree held it; any other absent session file is put back."""
    if w is not None:
        return w == h or w == pv
    if RUN_DELETES.search(path):
        return h is None and pv is None
    return True


def unpreserved(root, tip):
    """Overlay paths whose working copy (or its absence) holds something the branch tip does not.
    With no branch yet nothing is preserved: a deleted session file would otherwise compare equal."""
    if tip is None:
        return dirty_session_paths(root)
    placed = read_placed(root)
    out = []
    for p in overlay_paths(root, tip):
        w, t = worktree_blob(root, p), blob(root, tip, p)
        if w != t and not not_in_place(w, blob(root, "HEAD", p), p, placed.get(p)):
            out.append(p)
    return out


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


def union_shaped(root, path):
    """An appended shape: the attributes block gives it git's union driver."""
    out = text(git(root, "check-attr", "-z", "merge", "--", path))
    return out.split("\0")[2:3] == ["union"]


def union_copy(root, path, tip):
    """The three-way union of the working copy and the tip's version, in working-tree form, so an
    entry only the branch holds survives a working copy that lost it (a manual lift, a hand edit);
    the branch's side comes first, its entries being the older.
    The base is the version at merge-base HEAD <tip>, not HEAD's: HEAD can hold what the branch
    never had (a stranded commit), and the tip would then read as deleting it. Union keeps both
    sides of a conflicting hunk, so nothing is dropped, at the price of a stale line beside an
    edited one."""
    r = git(root, "merge-base", "HEAD", tip, check=False)
    base = text(r) if r.returncode == 0 and text(r) else None
    with tempfile.TemporaryDirectory() as td:
        sides = {}
        for name, commit in (("base", base), ("theirs", tip)):
            sides[name] = os.path.join(td, name)
            with open(sides[name], "wb") as fh:
                if blob(root, commit, path) is not None:
                    fh.write(git(root, "cat-file", "--filters", "%s:%s" % (commit, path)).stdout)
        r = git(root, "merge-file", "-p", "--union", sides["theirs"], sides["base"], os.path.join(root, path),
                check=False)
        if r.returncode < 0 or r.returncode > 127:
            raise NotRun("merge-file %s: %s" % (path, r.stderr.decode("utf-8", "replace").strip()[:300]))
        return r.stdout


def write_bytes(root, path, data):
    with open(os.path.join(root, path), "wb") as fh:
        fh.write(data)


def align(root, old_tip, new_tip):
    """After the branch moved, bring each session file whose working copy still equals the old tip's
    version, or the one this worktree was last given, to the new tip's. A working copy that differs
    holds entries of its own and is left."""
    changed = [p for p in nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", old_tip, new_tip))
               if classify(p)]
    placed = read_placed(root)
    done = []
    for p in changed:
        w = worktree_blob(root, p)
        if w == blob(root, old_tip, p) or (w is not None and w == placed.get(p)):
            new = blob(root, new_tip, p)
            mark(root, put={p: new} if new else None, drop=() if new else [p])
            write_from(root, new_tip, p)
            done.append(p)
    return done


def commit_tree(root, tree, parents, message):
    """commit-tree reads no commit.gpgSign, so a user who signs their commits would push unsigned
    session commits; sign them as git commit would."""
    sign = ["-S"] if config(root, "commit.gpgSign", as_bool=True) == "true" else []
    parent_args = [x for p in parents for x in ("-p", p)]
    return text(git(root, "commit-tree", *sign, tree, *parent_args, "-m", message))


def refuse_checked_out(root, branch):
    """The session branch is never stood on; moving it under a checkout would leave that checkout's
    index and files behind its HEAD. Refuse while any worktree has it checked out."""
    where, want = None, "branch refs/heads/" + branch
    for field in nul_list(git(root, "worktree", "list", "--porcelain", "-z")):
        if field.startswith("worktree "):
            where = field[len("worktree "):]
        elif field == want:
            raise NotRun("%s is checked out at %s; switch that checkout back to the default branch" % (branch, where))


def is_ancestor(root, a, b):
    return git(root, "merge-base", "--is-ancestor", a, b, check=False).returncode == 0


def sync(root, branch, default_ref):
    """Bring <default-ref>, and the session branch's own copy on origin where one exists (pushed from
    another clone), into the session branch without a checkout: a fast-forward where the branch holds
    nothing of its own, else merge-tree -X ours with the union driver; then align the overlay."""
    refuse_checked_out(root, branch)
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
    sources = [(default_ref, base)]
    upstream = rev(root, "refs/remotes/origin/" + branch)
    if upstream is not None:
        sources.append(("origin/" + branch, upstream))
    if all(is_ancestor(root, c, tip) for _, c in sources):
        return result
    held = unpreserved(root, tip)
    if held:
        result["deferred"] = held
        return result
    start = tip
    for name, c in sources:
        if is_ancestor(root, c, tip):
            continue
        if is_ancestor(root, tip, c):
            git(root, "update-ref", ref, c, tip)
            tip = c
            result["fast_forward"] = True
            continue
        if not merge_tree_ok(root):
            raise NotRun("this git cannot merge without a checkout (merge-tree --write-tree -X)")
        r = git(root, "merge-tree", "--write-tree", "-X", "ours", tip, c, check=False)
        lines = text(r).splitlines()
        if r.returncode == 1:
            result["conflict"] = sorted(set(result["conflict"]) |
                                        {ln.split("\t", 1)[1] for ln in lines[1:] if "\t" in ln})
            continue
        if r.returncode != 0 or not lines:
            raise NotRun("merge-tree: %s" % r.stderr.decode("utf-8", "replace").strip()[:300])
        merge = commit_tree(root, lines[0], [tip, c], "NOISSUE Merge %s into %s" % (name, branch))
        git(root, "update-ref", ref, merge, tip)
        tip = merge
        result["merged"] = True
    result["tip"] = tip
    if tip != start:
        result["aligned"] = align(root, start, tip)
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
    refuse_checked_out(root, branch)
    ensure_attributes(root)
    ref = "refs/heads/" + branch
    created = False
    tip = rev(root, ref)
    if tip is None:
        tip = create_at(root, branch, default_ref)
        created = True
    paths = overlay_paths(root, tip)
    stranded, not_session, extra = [], False, []
    if include_ahead:
        extra, ahead, not_session = ahead_paths(root, default_ref)
        stranded = [] if not_session else ahead
        paths = sorted(set(paths) | set(extra))
    placed = read_placed(root)
    kept = []
    for p in paths:
        w, t = worktree_blob(root, p), blob(root, tip, p)
        if p in extra or (w != t and not not_in_place(w, blob(root, "HEAD", p), p, placed.get(p))):
            kept.append(p)
    paths = kept
    added, dropped = {}, []
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
                    if blob(root, tip, p) not in (None, worktree_blob(root, p)) and union_shaped(root, p):
                        write_bytes(root, p, union_copy(root, p, tip))
                    sha = text(git(root, "hash-object", "-w", "--path", p, "--", p))
                    mode_bits = "100755" if os.stat(full).st_mode & stat.S_IXUSR else "100644"
                    entries.append("%s %s\t%s" % (mode_bits, sha, p))
                    if sha != blob(root, "HEAD", p):  # a stranded file HEAD holds is not the overlay's
                        added[p] = sha
                else:
                    entries.append("0 %s\t%s" % (ZERO, p))
                    dropped.append(p)
            git(root, "update-index", "-z", "--index-info",
                data=("\0".join(entries) + "\0").encode("utf-8", "surrogateescape"), env=env)
            tree = text(git(root, "write-tree", env=env))
        if tree != text(git(root, "rev-parse", tip + "^{tree}")):
            committed = commit_tree(root, tree, [tip], message)
            git(root, "update-ref", ref, committed, tip)
            changed = nul_list(git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", tip, committed))
        mark(root, put=added, drop=dropped)
    try:
        synced = sync(root, branch, default_ref)
    except NotRun as e:  # the commit stands; the merge waits for a run that can make it
        synced = {"error": str(e)}
    return {"committed": committed, "files": len(changed), "paths": changed, "created": created,
            "stranded": len(stranded), "ahead_not_session": not_session, "sync": synced}


def lift(root, branch):
    """Return every dirty session file to HEAD, but only once each is preserved on <branch>: its
    working copy is the tip's version. Otherwise list the ones that are not and discard nothing.
    Each path leaves the record just before it is touched, and the rest once all are done, so a
    lift that stops partway (a lock) leaves no removed file recorded as held and every untouched one
    still recorded; every restore runs before any removal."""
    tip = rev(root, "refs/heads/" + branch)
    held = unpreserved(root, tip)
    if held:
        return {"lifted": [], "unpreserved": held}
    dirty = dirty_session_paths(root)
    restore, remove = [], []
    for p in dirty:
        tracked = git(root, "ls-files", "--error-unmatch", "--", ":(literal)" + p, check=False).returncode == 0
        (restore if tracked or blob(root, "HEAD", p) is not None else remove).append(p)
    for p in restore:
        mark(root, drop=[p])
        git(root, "restore", "--source=HEAD", "--staged", "--worktree", "--", ":(literal)" + p)
    for p in remove:
        mark(root, drop=[p])
        os.remove(os.path.join(root, p))
    mark(root, clear=True)
    return {"lifted": dirty, "unpreserved": []}


def put_back(root, branch, default_ref):
    """Merge <default-ref> into <branch>, then write each session file where the branch differs from
    HEAD, or remove it where the branch lacks it, wherever the working copy is HEAD's version or the
    one this worktree was last given. Any other working copy holds entries of its own: an appended
    shape is union-merged with the branch's, any other is left and listed in skipped."""
    refuse_checked_out(root, branch)
    ref = "refs/heads/" + branch
    if rev(root, ref) is None:
        return {"written": [], "removed": [], "merged": [], "skipped": [], "sync": None}
    try:
        synced = sync(root, branch, default_ref)
    except NotRun as e:  # put the overlay back over the branch as it stands
        synced = {"error": str(e)}
    tip = rev(root, ref)
    placed = read_placed(root)
    written, removed, skipped, merged = [], [], [], []
    paths = set(nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", "HEAD", tip))) | set(placed)
    for p in sorted(paths):  # the recorded ones too: a stale copy of a file neither HEAD nor the tip has
        if not classify(p):
            continue
        want, have, head, pv = blob(root, tip, p), worktree_blob(root, p), blob(root, "HEAD", p), placed.get(p)
        if have == want:
            if want is not None and want != head and want != pv:
                mark(root, put={p: want})  # in place already, so record it: a later relocation is then a deletion
            continue
        if have is None and not not_in_place(have, head, p, pv):
            skipped.append(p)  # a pending cost file a run relocated: §8.2's commit records the deletion
            continue
        if not not_in_place(have, head, p, pv):
            if have is not None and want is not None and union_shaped(root, p):
                write_bytes(root, p, union_copy(root, p, tip))
                merged.append(p)  # unrecorded: it holds entries of its own for the next commit
            else:
                skipped.append(p)
            continue
        mark(root, put={p: want} if want else None, drop=() if want else [p])
        write_from(root, tip, p)
        (removed if want is None else written).append(p)
    return {"written": written, "removed": removed, "merged": merged, "skipped": skipped, "sync": synced}


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

    def scenarios():
        # ---- the classifier, and its parity with specs-repo-git §2.1 --------------------------
        CLASSIFIED = [
            ("specifications/PRD-A-1-x/dev-workflows/A-1-feedback.md", True),
            ("specifications/PRD-A-1-x/EPIC-A-1-1-y/implementation.md", True),
            ("specifications/PRD-A-1-x/follow-ups.md", True),
            ("specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md", True),
            ("documentation/acme-docs/dev-workflows/cost/s.md", True),
            ("dev-workflows-cost/pending-2026-10-06-abcd1234.md", True),
            ("security/acme-api/runs/0001-20261016T091200Z.json", True),
            ("security/acme-api/scans/20261016T091200Z-eb694d0/patches/F1.patch", True),
            ("security/acme-api/register.json", True),
            ("security/acme-api/dev-workflows/cost/s.md", True),
            ("security/threat-models/policy.md", False),
            ("security/acme-api/register.json.orig", False),
            ("specifications/PRD-A-1-x/EPIC-A-1-1-y/_security.md", True),
            ("specifications/BRD-B-1-y/brd/source/implementation.md", False),
            ("specifications/PRD-A-1-x/release-notes.md", False),
            ("specifications/PRD-A-1-x/attachments/release-notes.md", False),
            ("specifications/PRD-A-1-x/Doc screenshots/release-notes.md", False),
            ("specifications/PRD-A-1-x/prd.md", False),
            ("README.md", False),
        ]
        for path, want in CLASSIFIED:
            check(classify(path) == want, "classify(%r) should be %s" % (path, want))
        with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
            ref_text = fh.read()
        start = ref_text.index("2. Classify each reported path")
        pats = re.findall(r"`(\^[^`]+)`", ref_text[start:ref_text.index("**OTHER** otherwise.", start)])
        check(pats[:-1] == ARTIFACT, "the script's ARTIFACT patterns equal specs-repo-git §2.1's (%r)" % pats[:-1])
        check(pats[-1:] == [EXCLUDED], "the script's EXCLUDED pattern equals specs-repo-git §2.1's (%r)" % pats[-1:])

        # ---- entry_set_merge -------------------------------------------------------------------
        # Spec §3.3's entry-set rule, on the real formats: implementation-format §1's two example
        # blocks, feedback-emission §1's entry, /security-workflows:scan §7.3's _security.md block
        # and a cost-emission §6 entry, each as its reference writes it.
        IMPL_HEAD = "# Implementation — ACME-77-01 order intake\n\n"
        IMPL_1 = ("## 2026-08-31 — /implement\n"
                  "- repo:    orders-service\n"
                  "  branch:  feat/ACME-77-01-order-intake\n"
                  "  base:    main\n"
                  "  commit:  a3f91c2\n"
                  "  pushed:  true\n")
        IMPL_2 = ("## 2026-09-02 — /implement\n"
                  "- repo:    billing-api\n"
                  "  branch:  feat/ACME-77-01-order-intake\n"
                  "  base:    main\n"
                  "  commit:  7be0d41\n"
                  "  pushed:  false            # local only — resolvable on this machine\n")
        # The same day's run recorded again, differing in one line: git's union fuses these two.
        IMPL_2P = IMPL_2.replace("  pushed:  false            # local only — resolvable on this machine\n",
                                 "  pushed:  true\n")
        FB_HEAD = "---\ntype: dev-workflows-feedback\nprd: PRODUCT-1234\nslug: env-ag-update-window\n---\n\n"
        FB_1 = ("## 2026-07-09 — /document — missing-capability\n"
                "\n"
                "```yaml\n"
                "id: PRODUCT-1234-document-cloud-self-hosted-split\n"
                "date: 2026-07-09\n"
                "command: /document           # controlled: exact command name, or n/a\n"
                "plugin_version: 2.9.0\n"
                "origin: auto                 # auto | manual | prompt\n"
                "author: jane.doe@example.com\n"
                "category: missing-capability # controlled, extensible, reuse-first\n"
                "impact: friction             # blocker | friction | polish\n"
                "```\n"
                "\n"
                "**Friction:** One page covered both Cloud and Self-hosted; the Cloud half got pushed\n"
                "back in review because the two products differ here.\n"
                "\n"
                "**Suggested improvement:** Add an optional `cloud|self-hosted` parameter to\n"
                "`/document` so the run scopes to one product.\n")
        FB_2 = (FB_1.replace("— missing-capability\n", "— docs-ux\n")
                .replace("cloud-self-hosted-split", "docs-ux-split-page")
                .replace("category: missing-capability #", "category: docs-ux            #"))
        SEC_HEAD = "# Security — ACME-77-01 order intake\n\n"
        SEC_1 = ("## 2026-10-16 — /security-workflows:scan\n"
                 "- repo:     orders-service\n"
                 "  commit:   eb694d0\n"
                 "  scan:     change scan, effort medium — security/orders-service/scans/20261016T091200Z-eb694d0/\n"
                 "  kind:     scan, role dev\n"
                 "  findings: 0 CRITICAL · 1 HIGH · 1 MEDIUM · 0 LOW\n"
                 "  raised:   [SEC#1], [SEC#2]\n"
                 "  again:    none\n"
                 "  closed:   none\n"
                 "  register: security/orders-service/register.md\n")
        SEC_2 = (SEC_1.replace("eb694d0", "1c0ffee").replace("20261016T091200Z", "20261016T143000Z")
                 .replace("kind:     scan,", "kind:     verify,").replace("1 HIGH · 1 MEDIUM", "0 HIGH · 1 MEDIUM")
                 .replace("raised:   [SEC#1], [SEC#2]", "raised:   none").replace("closed:   none", "closed:   [SEC#1]"))
        SEC_3 = SEC_2.replace("1c0ffee", "d15ea5e").replace("20261016T143000Z", "20261016T170500Z")
        COST_HEAD = "---\ntype: dev-workflows-cost\nprd: PRODUCT-1234\nsession: 5e55a0d1\n---\n\n"
        COST = ("## 2026-07-09T14:22:33Z — /implement — implementation\n"
                "\n"
                "```yaml\n"
                "id: PRODUCT-1234-98760-implement-2026-07-09T14:22:33Z   # timestamp => unique\n"
                "date: 2026-07-09T14:22:33Z\n"
                "command: /implement\n"
                "phase: implementation\n"
                "role: dev\n"
                "prd: PRODUCT-1234\n"
                "epic: EPIC-98760            # present only when an Epic key is in scope\n"
                "plugin_version: 2.10.0\n"
                "duration_s: 1284\n"
                "cost_computed_usd: 3.4821\n"
                "cost_statusline_usd: 3.5102   # present only when the plugin statusline is installed\n"
                "compactions: 1               # present only when the window held a compaction (§2)\n"
                "models:\n"
                "  - {model: claude-opus-5, cost_usd: 2.9114, input_tokens: 12043, output_tokens: 88210,"
                " cache_read_tokens: 2109887, cache_write_tokens: 145002}\n"
                "  - {model: claude-sonnet-5, cost_usd: 0.5707, input_tokens: 45120, output_tokens: 210334,"
                " cache_read_tokens: 880122, cache_write_tokens: 42011}\n"
                "```\n")

        def cost(ts):
            return COST.replace("2026-07-09T14:22:33Z", ts)

        def esm(base, ours, theirs):
            got = entry_set_merge(None if base is None else base.encode(), ours.encode(), theirs.encode())
            return None if got is None else got.decode()

        # split_entries and entry_key
        head, ents = split_entries((IMPL_HEAD + IMPL_1 + "\n" + IMPL_2).encode())
        check(head == IMPL_HEAD.encode() and ents == [(IMPL_1 + "\n").encode(), IMPL_2.encode()],
              "split_entries cuts implementation-format §1's example into its header and two blocks (%r, %r)"
              % (head, ents))
        for fmt, head, entry in (("feedback", FB_HEAD, FB_1), ("_security.md", SEC_HEAD, SEC_1),
                                 ("cost", COST_HEAD, COST)):
            got = split_entries((head + entry).encode())
            check(got == (head.encode(), [entry.encode()]), "split_entries finds the %s entry's heading (%r)" % (fmt, got))
        check(entry_key(b"## x\r\n  a  \r\n\r\n \t\n\n") == b"## x\r\n  a",
              "entry_key drops trailing blank lines and line endings, and nothing before them")
        noted = IMPL_2P + "\n## Notes\nThe billing half waits on the ledger change.\n## 2026-09-03 - retro, not an entry\n"
        head, ents = split_entries((IMPL_HEAD + IMPL_1 + "\n" + noted).encode())
        check(ents == [(IMPL_1 + "\n").encode(), noted.encode()],
              "a ## Notes line, or a dated ## line of another shape, stays inside its entry (%r)" % (ents,))

        # two same-day /implement entries differing in one line stay two, in order, under one header
        base = IMPL_HEAD + IMPL_1
        ours, theirs = base + "\n" + IMPL_2P, base + "\n" + IMPL_2
        got = esm(base, ours, theirs)
        check(got == ours + "\n" + IMPL_2,
              "two same-day /implement entries differing in one line are kept as two, in order (%r)" % got)
        check(got is not None and got.count("# Implementation —") == 1, "…under one header (%r)" % got)
        got = esm(base, base + "\n" + IMPL_2, base + "\n" + noted)
        check(got == base + "\n" + IMPL_2 + "\n" + noted, "an entry holding a ## Notes line is carried whole (%r)" % got)

        # an entry both sides hold is kept once
        base = FB_HEAD + FB_1
        ours = base + "\n" + FB_2
        got = esm(base, ours, ours)
        check(got == ours, "an entry both sides appended leaves ours byte-unchanged (%r)" % got)

        # base need not be a prefix of either side: a merge that reordered them still settles
        C0, E1, B1, E2 = (cost(t) for t in ("2026-07-09T14:22:33Z", "2026-07-10T08:00:00Z",
                                            "2026-07-10T09:30:00Z", "2026-07-11T16:45:10Z"))
        base = COST_HEAD + C0
        ours = base + "\n" + E1 + "\n" + B1
        got = esm(base, ours, base + "\n" + B1)
        check(got == ours, "E1 B1 against B1 leaves ours unchanged (%r)" % got)
        got = esm(base, ours, base + "\n" + B1 + "\n" + E2)
        check(got == ours + "\n" + E2, "E1 B1 against B1 E2 is ours, a blank line, then E2 (%r)" % got)

        # Review Focus 1: an entry with and without its final newline is one entry; ours' last line
        # is never glued to an appended entry
        base = IMPL_HEAD + IMPL_1
        bare = base + "\n" + IMPL_2.rstrip("\n")
        for other in (base + "\n" + IMPL_2, base + "\n" + IMPL_2 + "\n", base + "\n" + IMPL_2 + "\n \n\n"):
            got = esm(base, bare, other)
            check(got == bare + "\n",
                  "an entry last without a final newline matches its copy with one: ours given a newline (%r)" % got)
            got = esm(base, other, bare)
            check(got == other, "…and from the other side, ours unchanged (%r)" % got)
        got = esm(IMPL_HEAD + IMPL_1.rstrip("\n"), IMPL_HEAD + IMPL_1 + "\n" + IMPL_2,
                  IMPL_HEAD + IMPL_1 + "\n" + IMPL_2P)
        check(got == IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P,
              "a base entry that lacked a final newline is not read as edited (%r)" % got)
        got = esm(base, bare, base + "\n" + IMPL_2P)
        check(got == bare + "\n\n" + IMPL_2P,
              "ours ending without a newline keeps its last line whole: a newline, an empty line, the entry (%r)" % got)
        got = esm(base, base + "\n" + IMPL_2, base + "\n" + IMPL_2P.rstrip("\n"))
        check(got == base + "\n" + IMPL_2 + "\n" + IMPL_2P, "an appended entry lacking a final newline is given one (%r)" % got)
        got = esm(base, base + "\n" + IMPL_2, base + "\n" + IMPL_2P + "\n \n\n")
        check(got == base + "\n" + IMPL_2 + "\n" + IMPL_2P, "an appended entry's trailing blank lines are dropped (%r)" % got)
        hard = IMPL_2P.rstrip("\n") + "  \n"
        got = esm(base, base + "\n" + IMPL_2, base + "\n" + hard + "\n")
        check(got == base + "\n" + IMPL_2 + "\n" + hard,
              "…but its last line's own trailing spaces are its bytes, and kept (%r)" % got)

        # Review Focus 2: CRLF content merges in CRLF, with no bare \n added
        def crlf(s):
            return s.replace("\n", "\r\n")

        def bare_lf(s):
            return s is not None and re.search(r"(?<!\r)\n", s) is not None
        base = crlf(SEC_HEAD + SEC_1)
        ours, theirs = base + crlf("\n" + SEC_2), base + crlf("\n" + SEC_3)
        got = esm(base, ours, theirs)
        check(got == crlf(SEC_HEAD + SEC_1 + "\n" + SEC_2 + "\n" + SEC_3) and not bare_lf(got),
              "CRLF sides merge with \\r\\n endings throughout (%r)" % got)
        got = esm(base, ours[:-2], theirs)
        check(got == ours[:-2] + "\r\n\r\n" + crlf(SEC_3) and not bare_lf(got),
              "a CRLF ours lacking its final ending is given \\r\\n, then an empty line, then the entry (%r)" % got)
        got = esm(base, ours, base + crlf("\n" + SEC_3)[:-2])
        check(got == ours + "\r\n" + crlf(SEC_3) and not bare_lf(got),
              "an appended CRLF entry lacking its final ending is given \\r\\n (%r)" % got)

        # both sides created the file: the headers decide
        got = esm(None, FB_HEAD + FB_1, FB_HEAD + FB_2)
        check(got == FB_HEAD + FB_1 + "\n" + FB_2, "add/add with identical headers merges (%r)" % got)
        got = esm(None, FB_HEAD + FB_1, FB_HEAD.rstrip("\n") + "\n" + FB_2)
        check(got == FB_HEAD + FB_1 + "\n" + FB_2, "headers differing only in trailing blank lines match (%r)" % got)
        keyless = "---\ntype: dev-workflows-feedback\nprd: n/a\nslug: 2026-07-09\n---\n\n"
        got = esm(None, FB_HEAD + FB_1, keyless + FB_2)
        check(got is None, "add/add with different headers refuses (%r)" % got)
        got = esm(None, "", COST), esm(None, "", "")
        check(got == (COST, ""), "an empty ours gains no leading empty line and no line ending of its own (%r)" % (got,))

        # an edit, an addition to the last base entry, a removal, a header edit: each refuses
        base = IMPL_HEAD + IMPL_1 + "\n" + IMPL_2
        grown = base + "\n" + IMPL_2P
        for what, changed in (
                ("an edit inside a base entry", base.replace("commit:  a3f91c2", "commit:  a3f91c3")),
                ("an addition to the last base entry", base + "  note:    amended by hand\n"),
                ("a removal of a base entry", IMPL_HEAD + IMPL_2),
                ("an edit of the header", base.replace("order intake", "order intake (renamed)"))):
            for ours, theirs in ((grown, changed), (changed, grown)):
                got = esm(base, ours, theirs)
                check(got is None, "%s refuses (%r)" % (what, got))

        # merge_class: by path, for every path the classifier table holds and the shapes it lacks
        want_class = {
            "specifications/PRD-A-1-x/dev-workflows/A-1-feedback.md": "block",
            "specifications/PRD-A-1-x/EPIC-A-1-1-y/implementation.md": "block",
            "specifications/PRD-A-1-x/follow-ups.md": "lines",
            "specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md": "whole",
            "documentation/acme-docs/dev-workflows/cost/s.md": "block",
            "dev-workflows-cost/pending-2026-10-06-abcd1234.md": "block",
            "security/acme-api/runs/0001-20261016T091200Z.json": None,
            "security/acme-api/scans/20261016T091200Z-eb694d0/patches/F1.patch": None,
            "security/acme-api/register.json": "register",
            "security/acme-api/dev-workflows/cost/s.md": "block",
            "security/threat-models/policy.md": None,
            "security/acme-api/register.json.orig": None,
            "specifications/PRD-A-1-x/EPIC-A-1-1-y/_security.md": "block",
            "specifications/BRD-B-1-y/brd/source/implementation.md": None,
            "specifications/PRD-A-1-x/release-notes.md": None,
            "specifications/PRD-A-1-x/attachments/release-notes.md": None,
            "specifications/PRD-A-1-x/Doc screenshots/release-notes.md": None,
            "specifications/PRD-A-1-x/prd.md": None,
            "README.md": None,
            "specifications/PRD-A-1-x/dev-workflows/resume.md": "whole",
            "specifications/BRD-B-1-y/dev-workflows/resume.md": "whole",
            "specifications/PRD-A-1-x/pr-draft.md": "whole",
            "specifications/PRD-A-1-x/dev-workflows/cost/5e55a0d1.md": "block",
            "dev-workflows-feedback/2026-07-09.md": "block",
            "security/acme/register.md": "register",
            "security/acme/runs/0001-x.json": None,
            "security/acme/scans/20261016T091200Z-eb694d0/implementation.md": None,
        }
        missing = [p for p, _ in CLASSIFIED if p not in want_class]
        check(not missing, "merge_class is checked for every path the classifier table holds (%r)" % missing)
        for path, want in want_class.items():
            check(merge_class(path) == want, "merge_class(%r) should be %r" % (path, want))

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
            # The record is a file in the common git directory, so a clone whose .git/config is
            # read-only (a hardened container) can still keep it; the config key above is read
            # for clones that recorded a refusal before the file existed.
            a.git("config", "--unset", "branch.main.workflowsPushRefused")
            got = a.run("mode", "--default", "main")
            check(got.get("mode") == "off", "with no record the mode is off again (%r)" % got)
            records = os.path.join(a.path, a.git("rev-parse", "--git-common-dir"), "workflows", "push-refused")
            os.makedirs(os.path.join(records, "session"))
            with open(os.path.join(records, "session", "cd"), "w", encoding="utf-8") as fh:
                fh.write("2026-10-07\n")
            got = a.run("mode", "--default", "main")
            check(got.get("mode") == "off", "a record for another branch does not turn it on (%r)" % got)
            with open(os.path.join(records, "main"), "w", encoding="utf-8") as fh:
                fh.write("2026-10-07\n")
            got = a.run("mode", "--default", "main")
            check(got.get("mode") == "on" and got.get("source") == "refused",
                  "a refusal record file turns it on (%r)" % got)
            # The record stands where the file exists, whatever it holds -- an empty or undecodable
            # file too, which must never stop the run.
            with open(os.path.join(records, "main"), "wb") as fh:
                fh.write(b"\xff\xfe")
            got = a.run("mode", "--default", "main")
            check(got.get("mode") == "on" and got.get("source") == "refused",
                  "an undecodable record file still turns it on (%r)" % got)
            open(os.path.join(records, "main"), "w").close()
            got = a.run("mode", "--default", "main")
            check(got.get("mode") == "on" and got.get("source") == "refused",
                  "an empty record file still turns it on (%r)" % got)
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
            odd = "dev-workflows-cost/:odd pending ü.md"  # the shape a run deletes (cost-emission §9)
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
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            os.remove(os.path.join(a.path, FB))  # a run deleted a tracked session file; no session branch yet
            got = a.run("lift", "--branch", "session/aa")
            check(got.get("unpreserved") == [FB] and a.read(FB) is None,
                  "with no session branch, nothing dirty is preserved, a deletion included (%r)" % got)
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
        # the same identity on a second clone: the session branch already on origin is merged in
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\nfrom clone a\n", append=True)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.git("push", "-q", "-u", "origin", "session/aa")
            b.git("fetch", "-q", "origin")
            b.write(FB, "## a2\nfrom clone b\n", append=True)
            got = b.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            on_branch = b.git("show", "session/aa:" + FB)
            check("## a1" in on_branch and "## a2" in on_branch and got["sync"].get("merged") is True,
                  "a session branch already on origin is merged into the new local one (%r)" % on_branch)
            check(b.git("push", "--porcelain", "origin", "session/aa", check=False).find("[rejected]") < 0
                  and b.git("rev-parse", "session/aa") == b.git("ls-remote", "origin", "refs/heads/session/aa").split()[0],
                  "…so its push is a fast-forward")
            check("## a1" in (b.read(FB) or ""), "…and the working copy holds the other clone's entry")
        # a session branch someone checked out is never moved under that checkout
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.run("lift", "--branch", "session/aa")
            a.git("switch", "-q", "session/aa")
            tip = a.git("rev-parse", "session/aa")
            a.write(FB, "## a2\n", append=True)
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(got.get("_rc") == 2 and "checked out" in got.get("_err", "") and a.git("rev-parse", "session/aa") == tip,
                  "commit refuses, moving nothing, while the session branch is checked out (%r)" % got)
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("_rc") == 2 and "checked out" in got.get("_err", ""), "…and so does put-back (%r)" % got)
        # a user who signs commits gets signed session commits: commit-tree reads no commit.gpgSign
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.git("config", "commit.gpgSign", "true")
            a.git("config", "gpg.program", "false")  # a signer that always fails, so an attempt is visible
            a.write(FB, "## a1\n", append=True)
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(got.get("_rc") == 2 and "commit-tree" in got.get("_err", ""),
                  "commit.gpgSign makes the session commit a signed one, so a signer that fails stops it (%r)" % got)
            check(len(got.get("_err", "").splitlines()) == 1 and "gpg failed to sign" in got.get("_err", ""),
                  "git's multi-line error is one 'not run' line, its whole reason on it (%r)" % got)
        # the overlay not in place: a commit never takes that for the run's own deletions or reverts
        CM = ("--default-ref", "origin/main", "--message", "A-1 Add session")
        cost1 = "specifications/PRD-A-1-x/dev-workflows/cost/s1.md"
        rs = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        pr = "specifications/PRD-A-1-x/pr-draft.md"
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\n", append=True)
            a.write(cost1, "cost one\n")
            a.write(rs, "pos: one\n")
            a.write(pr, "draft one\n")
            a.write("dev-workflows-cost/pending-2026-10-06-00000001.md", "pending\n")
            a.run("commit", "--branch", "session/aa", *CM)
            tip = a.git("rev-parse", "session/aa")
            a.run("lift", "--branch", "session/aa")
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("committed") is None and a.git("rev-parse", "session/aa") == tip,
                  "a commit between a lift and its put-back records nothing (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(cost1) == "cost one\n" and a.read(rs) == "pos: one\n" and a.read(pr) == "draft one\n"
                  and "## a1" in (a.read(FB) or ""), "…and put-back brings every file back")
            pend = "dev-workflows-cost/pending-2026-10-06-abcd1234.md"
            a.write(pend, "pending\n")
            a.run("commit", "--branch", "session/aa", *CM)
            os.remove(os.path.join(a.path, pend))  # a run relocated it: a deletion of a file this worktree held
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(pend) is None, "put-back never brings back a held file a run deleted (%r)" % got)
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(pend in got.get("paths", []) and subprocess.run(["git", "-C", a.path, "cat-file", "-e",
                  "session/aa:" + pend], stderr=devnull).returncode != 0, "…and the next commit records it (%r)" % got)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\n", append=True)
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM)
            wt = Repo(os.path.join(tmp, "wt"))
            a.git("worktree", "add", "-q", "-b", "prd/A-1-x", wt.path)
            wt.write("specifications/PRD-A-1-x/dev-workflows/cost/s2.md", "cost two\n")
            got = wt.run("commit", "--branch", "session/aa", *CM)
            check(got.get("paths") == ["specifications/PRD-A-1-x/dev-workflows/cost/s2.md"]
                  and "## a1" in a.git("show", "session/aa:" + FB) and a.git("show", "session/aa:" + cost1) == "cost one",
                  "a commit from a worktree the overlay never reached deletes and reverts nothing (%r)" % got)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## stranded\n", append=True)
            a.commit_all("A-1 Add dev-workflows session artifacts (implement)")
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM, "--include-ahead")
            a.run("lift", "--branch", "session/aa")
            a.git("reset", "-q", "--keep", "origin/main")  # the remedy §6 names for the stranded commits
            got = a.run("commit", "--branch", "session/aa", *CM)
            check("## stranded" in a.git("show", "session/aa:" + FB) and a.git("show", "session/aa:" + cost1) == "cost one",
                  "after the stranded-commit remedy a commit keeps the stranded entry and the cost file (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check("## stranded" in (a.read(FB) or "") and a.read(cost1) == "cost one\n", "…and put-back restores both")
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            tp = "dev-workflows-cost/pending-2026-10-04-00000003.md"
            a.write(tp, "pending\n")
            a.commit_all("on main")
            a.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            os.remove(os.path.join(a.path, tp))  # a run relocates a pending file main already holds
            a.run("commit", "--branch", "session/aa", *CM)
            got = a.run("lift", "--branch", "session/aa")
            check(got.get("lifted") == [tp] and a.read(tp) is not None and a.git("status", "--porcelain") == "",
                  "lift restores a tracked deleted session file once its deletion is on the branch (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(tp) is None, "…and put-back removes it again")
        # a file a stranded commit added survives the remedy and a switch onto an older branch
        s0 = "specifications/PRD-A-1-x/dev-workflows/cost/s0.md"
        for how in ("remedy", "switch"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                a.git("branch", "prd/A-1-x")
                a.write(s0, "cost zero\n")
                a.commit_all("A-1 Add dev-workflows session artifacts (implement)")
                a.run("commit", "--branch", "session/aa", *CM, "--include-ahead")
                a.run("lift", "--branch", "session/aa")
                if how == "remedy":
                    a.git("reset", "-q", "--keep", "origin/main")
                else:
                    a.git("switch", "-q", "prd/A-1-x")
                a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
                a.run("commit", "--branch", "session/aa", *CM)
                check(a.read(s0) == "cost zero\n" and a.git("show", "session/aa:" + s0) == "cost zero",
                      "[%s] a file a stranded commit added stays on the branch and in the tree" % how)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            sp = "dev-workflows-cost/pending-2026-10-05-00000002.md"
            a.write(sp, "pending\n")
            a.commit_all("NOISSUE Add dev-workflows session artifacts (feedback)")
            a.run("commit", "--branch", "session/aa", *CM, "--include-ahead")
            a.git("reset", "-q", "--keep", "origin/main")  # the remedy run without its lift
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(a.git("show", "session/aa:" + sp) == "pending",
                  "a stranded pending file the checkout dropped is never read as the run's relocation (%r)" % got)
        # a lift a lock interrupts leaves nothing to be read as a deletion
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            pend = "dev-workflows-cost/pending-2026-10-06-abcd1234.md"
            a.write(pend, "pending\n")
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            lock = os.path.join(a.path, ".git", "index.lock")
            open(lock, "w").close()
            got = a.run("lift", "--branch", "session/aa")
            os.remove(lock)
            a.run("commit", "--branch", "session/aa", *CM)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("_rc") == 2 and a.git("show", "session/aa:" + pend) == "pending" and a.read(pend) == "pending\n",
                  "a lift a lock interrupts loses no file (%r)" % got)
            os.remove(os.path.join(a.path, pend))  # a later run relocates it
            a.run("commit", "--branch", "session/aa", *CM)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(pend) is None and subprocess.run(["git", "-C", a.path, "cat-file", "-e", "session/aa:" + pend],
                  stderr=devnull).returncode != 0, "…and a relocation after it is recorded, never undone")
        # two worktrees holding the overlay: one's relocation is not undone by the other
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            pend = "dev-workflows-cost/pending-2026-10-06-abcd1234.md"
            a.write(pend, "pending\n")
            a.write(rs, "pos: a\n")
            a.run("commit", "--branch", "session/aa", *CM)
            w2 = Repo(os.path.join(tmp, "w2"))
            a.git("worktree", "add", "-q", "-b", "prd/A-1-x", w2.path)
            w2.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            os.remove(os.path.join(w2.path, pend))  # w2's run relocates the pending file
            w2.write(rs, "pos: w2\n")
            w2.run("commit", "--branch", "session/aa", *CM)
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(subprocess.run(["git", "-C", a.path, "cat-file", "-e", "session/aa:" + pend], stderr=devnull).returncode != 0
                  and a.git("show", "session/aa:" + rs) == "pos: w2",
                  "another worktree's stale copies undo neither a relocation nor a newer resume.md (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(pend) is None and a.read(rs) == "pos: w2\n", "…and put-back brings that worktree up to date")
        # a session file removed by hand is put back, never deleted from the branch — a tracked one too
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            os.remove(os.path.join(a.path, FB))
            got = a.run("commit", "--branch", "session/aa", *CM)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("committed") is None and "## a1" in (a.read(FB) or "") and "## a1" in a.git("show", "session/aa:" + FB),
                  "a tracked session file removed by hand is put back, not deleted (%r)" % got)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM)
            os.remove(os.path.join(a.path, cost1))  # rm, git clean, git stash -u
            got = a.run("commit", "--branch", "session/aa", *CM)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("committed") is None and a.read(cost1) == "cost one\n",
                  "a session file removed by hand is put back, not deleted from the branch (%r)" % got)
        # a catch-up that brings a teammate's new file: put-back merges rather than defers, and keeps it
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            im = "specifications/PRD-A-1-x/implementation.md"
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(im, "## run b\n")
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            a.run("lift", "--branch", "session/aa")
            a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("sync", {}).get("merged") is True and not got["sync"].get("deferred")
                  and a.read(im) == "## run b\n" and "## a1" in (a.read(FB) or ""),
                  "put-back after a catch-up merges the new default branch and keeps a teammate's file (%r)" % got)
        # a hand-edited log keeps the branch's older entries first
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## e-prev\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            a.run("lift", "--branch", "session/aa")
            a.write(FB, "## e-run\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            on = a.git("show", "session/aa:" + FB)
            check("## e-prev" in on and "## e-run" in on and on.index("## e-prev") < on.index("## e-run"),
                  "a union merge puts the branch's entries before the working copy's (%r)" % on)
        # a concurrent session that moves the branch mid-commit wins, and this run's files stay
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            other = a.git("rev-parse", "origin/main")
            stub = os.path.join(tmp, "gpg-stub")
            with open(stub, "w") as fh:
                fh.write('#!/bin/sh\ncat >/dev/null\ngit -C "$SB_REPO" update-ref refs/heads/session/aa "$SB_OTHER"\n'
                         'echo "[GNUPG:] SIG_CREATED D 1 8 00 1 X" >&2\n'
                         'printf -- "-----BEGIN PGP SIGNATURE-----\\n\\nstub\\n-----END PGP SIGNATURE-----\\n"\n')
            os.chmod(stub, 0o755)
            a.git("config", "commit.gpgSign", "true")
            a.git("config", "gpg.program", stub)
            a.write(FB, "## a2\n", append=True)
            got = a.run("commit", "--branch", "session/aa", *CM, env={"SB_REPO": a.path, "SB_OTHER": other})
            check(got.get("_rc") == 2 and a.git("rev-parse", "session/aa") == other and "## a2" in (a.read(FB) or ""),
                  "a branch moved under a commit is left as moved, exit 2, the files kept (%r)" % got)
        # every appended shape merges by union; the overwritten ones do not
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.run("commit", "--branch", "session/aa", *CM)
            for path, want in [(FB, "union"), (cost1, "union"), ("dev-workflows-feedback/x.md", "union"),
                               ("dev-workflows-cost/pending-x.md", "union"),
                               ("documentation/acme/dev-workflows/feedback/x.md", "union"),
                               ("specifications/PRD-A-1-x/implementation.md", "union"),
                               ("specifications/PRD-A-1-x/release-notes.md", "unspecified"),
                               ("specifications/PRD-A-1-x/follow-ups.md", "union"),
                               ("specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md", "union"),
                               ("specifications/PRD-A-1-x/EPIC-A-1-1-y/_security.md", "union"),
                               (rs, "unset"), (pr, "unset"),
                               ("security/acme-api/register.json", "unset"), ("security/acme-api/register.md", "unset")]:
                got = a.git("check-attr", "merge", "--", path).rsplit(": ", 1)[-1]
                check(got == want, "%s merges as %s, not %s" % (path, want, got))
        # an OS error is "could not run" (exit 2), never a traceback
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM)
            a.run("lift", "--branch", "session/aa")
            costdir = os.path.dirname(os.path.join(a.path, cost1))
            os.rmdir(costdir)
            a.write("specifications/PRD-A-1-x/dev-workflows/cost", "a file where a directory goes\n")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("_rc") == 2 and "Traceback" not in got.get("_err", ""), "an OSError exits 2 (%r)" % got)
        # a git whose merge-tree cannot merge without a checkout
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            fake = os.path.join(tmp, "oldgit")
            os.makedirs(fake)
            with open(os.path.join(fake, "git"), "w") as fh:
                fh.write('#!/bin/sh\nfor x in "$@"; do [ "$x" = merge-tree ] && '
                         '{ echo "usage: git merge-tree <branch1> <branch2>" >&2; exit 129; }; done\n'
                         'exec "%s" "$@"\n' % shutil.which("git"))
            os.chmod(os.path.join(fake, "git"), 0o755)
            old = {"PATH": fake + os.pathsep + os.environ.get("PATH", "")}
            a.git("config", "workflows.sessionBranch", "true")
            got = a.run("mode", "--default", "main", env=dict(old, GIT_USER_INITIALS="aa"))
            check(got.get("mode") == "unsupported", "mode says unsupported where merge-tree cannot merge (%r)" % got)
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(FB, "## team\n", append=True)
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            a.write(FB, "## a2\n", append=True)
            got = a.run("commit", "--branch", "session/aa", *CM, env=old)
            check(got.get("committed") and got.get("sync", {}).get("error"),
                  "a commit that lands reports a merge it could not make, rather than exit 2 (%r)" % got)
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
            a.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: typed\n")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            fb = a.read(FB) or ""
            check(got.get("merged") == [FB] and "## typed by hand" in fb and "## a1" in fb,
                  "put-back merges a foreign copy of an appended file with the branch's (%r, %r)" % (got, fb))
            check(got.get("skipped") == [], "…and skips none of the appended shapes (%r)" % got)
        # a hand edit after a manual lift never drops what only the branch holds
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            fu = "specifications/PRD-A-1-x/follow-ups.md"
            a.write(fu, "- [ ] one\n")
            a.commit_all("follow-ups on main")
            a.write(fu, "- [ ] two\n", append=True)
            a.write(FB, "## a1\n", append=True)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.run("lift", "--branch", "session/aa")
            a.write(fu, "- [x] one\n")  # ticked by hand, on HEAD's version
            os.remove(os.path.join(a.path, ".git", "info", "attributes"))  # as on a fresh clone
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            on_branch = a.git("show", "session/aa:" + fu)
            check("- [x] one" in on_branch and "- [ ] two" in on_branch,
                  "commit unions a hand edit with what only the branch held, losing neither (%r)" % on_branch)
            check(a.read(fu) == on_branch + "\n" and "## a1" in a.git("show", "session/aa:" + FB),
                  "…writes the merged copy back, and keeps the other file (%r)" % a.read(fu))
        # an overwritten shape is the working copy's, as before
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            rs = "specifications/PRD-A-1-x/dev-workflows/resume.md"
            a.write(rs, "pos: one\n")
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.run("lift", "--branch", "session/aa")
            a.write(rs, "pos: two\n")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("skipped") == [rs] and a.read(rs) == "pos: two\n", "put-back leaves a foreign resume.md (%r)" % got)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(a.git("show", "session/aa:" + rs) == "pos: two", "commit takes an overwritten file as it stands")
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
        # an unexpected exception is "not run" on one line, exit 2: §6 quotes the first stderr line
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            real, argv = globals()["dispatch"], sys.argv

            def boom(_args):
                raise KeyError("sync")
            globals()["dispatch"] = boom
            sys.argv = [me, "--specs", a.path, "sync", "--branch", "session/aa", "--default-ref", "origin/main"]
            err = io.StringIO()
            try:
                with contextlib.redirect_stderr(err):
                    rc = main()
            except BaseException as e:
                rc = "raised %s" % type(e).__name__
            finally:
                globals()["dispatch"], sys.argv = real, argv
            lines = err.getvalue().splitlines()
            check(rc == 2 and lines == ["session-branch: not run (KeyError: 'sync')"],
                  "an unexpected exception exits 2 with one 'not run' line (%r, %r)" % (rc, lines))
            got = a.run("commit", "--branch", "session/aa")
            check(got.get("_rc") == 2 and got.get("_err", "").splitlines() ==
                  ["session-branch: not run (the following arguments are required: --default-ref, --message)"],
                  "a usage error exits 2 with one 'not run' line (%r)" % got)
            r = subprocess.run([sys.executable, me, "mode", "--default", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            check(r.returncode == 2 and r.stderr.decode().splitlines() ==
                  ["session-branch: not run (--specs and a subcommand are required)"],
                  "a call without --specs exits 2 with one 'not run' line (%r)" % r.stderr)

    try:
        scenarios()
    except Exception as e:  # a scenario that crashes must not hide the failures before it
        failures.append("selftest crashed: %s: %s" % (type(e).__name__, str(e).strip()[:500]))

    if failures:
        print("session-branch selftest: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print("session-branch selftest: PASS")
    return 0


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is: §6 quotes the first stderr line."""

    def error(self, message):
        print("session-branch: not run (%s)" % message, file=sys.stderr)
        sys.exit(2)


def main():
    ap = Parser(description="Keep session files on a per-user session branch.")
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
        print("session-branch: not run (--specs and a subcommand are required)", file=sys.stderr)
        return 2
    try:
        top = text(git(a.specs, "rev-parse", "--show-toplevel"))
        if os.path.realpath(top) != os.path.realpath(a.specs):
            raise NotRun("%s is not its repository's top level (%s)" % (a.specs, top))
        result = dispatch(a)
    except (NotRun, OSError) as e:  # git's stderr can span lines; §6 quotes the first one
        print("session-branch: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
        return 2
    except Exception as e:  # anything unexpected is "not run" on one line, never a traceback
        print("session-branch: not run (%s: %s)" % (type(e).__name__, " ".join(str(e).split())), file=sys.stderr)
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
    if a.cmd == "lift":
        return lift(a.specs, a.branch)
    if a.cmd == "put-back":
        return put_back(a.specs, a.branch, a.default_ref)
    raise NotRun("unknown subcommand %s" % a.cmd)


if __name__ == "__main__":
    sys.exit(main())

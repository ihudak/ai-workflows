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

# follow-ups.md, one task per line, merges with git's union driver. The overwritten shapes and the
# register files are unset (-merge), so a merge keeps the session branch's version whole
# (merge-tree -X ours) rather than splicing two versions line by line. No block-shaped file is
# named: union matches lines, not entries, and fuses two entries that share lines, so sync settles
# such a file from its three blobs (entry_set_merge), and a user's own merge of one stops on a
# conflict rather than fusing two entries silently.
ATTR_BEGIN = "# BEGIN workflows-core session-branch: written by session-branch.py, do not edit"
ATTR_END = "# END workflows-core session-branch"
ATTRIBUTES = [
    "**/follow-ups.md merge=union",
    "**/dev-workflows/resume.md -merge",
    "**/pr-draft.md -merge",
    "**/*-implementation-gaps.md -merge",
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


def _line_ending_form(data):
    """Whether the bytes hold a \\r\\n, and whether they hold a \\n with no \\r before it. Bytes with
    no line ending at all (one line, its final newline stripped) read as the LF form: a merge that
    adds a line after that one completes it with \\n (_line_ending; git's merge-file too, where no
    other line tells it \\r\\n), so it merges with LF versions and is refused beside CRLF ones."""
    return b"\r\n" in data, b"\n" not in data or re.search(rb"(?<!\r)\n", data) is not None


def _forms_differ(*versions):
    """True where the non-empty <versions> (None or empty ones aside) are not all in one line-ending
    form (_line_ending_form): a line in \\r\\n never matches its copy in \\n, so a merge of them would
    keep it twice. The refusal entry_set_merge, keep_branch_only and union_lines share."""
    return len({_line_ending_form(x) for x in versions if x}) > 1


def _ends_blank(data):
    """True where the last line of <data>, which ends with a line ending, is empty or whitespace-only."""
    body = data[:-1]
    if body.endswith(b"\r"):
        body = body[:-1]
    return not body[body.rfind(b"\n") + 1:].strip(b" \t")


def entry_set_merge(base, ours, theirs):
    """Spec §3.3's settlement of a block-shaped appended file both sides changed, from three
    versions; base is None where both sides created it. None (refuse) where the non-empty versions
    are not all in one line-ending form (_line_ending_form: an entry in \\r\\n never matches its copy
    in \\n, so it would be added twice), where the two headers differ, or where an entry of base is
    missing from one side while the other still holds it: an edit, a removal, or an addition to the
    last entry, made on one side alone. An entry of base missing from both sides is an agreed change,
    as a three-way merge takes one: removed on both, it stays removed; edited alike, it is kept once;
    edited differently, both edited versions stay -- a visible duplicate, never a lost edit. Otherwise
    ours, given a final line ending where it lacks one, then each entry of theirs that ours lacks,
    once, in theirs' order, after one empty line (none where ours already ends with a blank line, or
    is empty), with its trailing blank lines dropped and one line ending, its own lines unchanged.
    Each line ending added is \\r\\n where the entry's first line ends \\r\\n (for the one added to
    ours, where ours' last line ending is \\r\\n), else \\n. Base decides only the refusal; it need not
    be a prefix of either side. A caller decides a deleted side."""
    if _forms_differ(base, ours, theirs):
        return None
    head_o, ents_o = split_entries(ours)
    head_t, ents_t = split_entries(theirs)
    if entry_key(head_o) != entry_key(head_t):
        return None
    have_o = {entry_key(e) for e in ents_o}
    if base is not None:
        have_t = {entry_key(e) for e in ents_t}
        if any((entry_key(e) in have_o) != (entry_key(e) in have_t) for e in split_entries(base)[1]):
            return None
    out = ours
    if out and not out.endswith(b"\n"):
        out += _line_ending(out, last=True)
    return _append_entries(out, ents_t, have_o)


def _append_entries(out, entries, have):
    """<out>, which ends with a line ending or is empty, followed by each of <entries> whose key
    <have> lacks, once, in order: after one empty line (none where <out> already ends with a blank
    line, or is empty), with its trailing blank lines dropped and one line ending, its own lines
    unchanged. Each line ending added is \\r\\n where the entry's first line ends \\r\\n, else \\n.
    entry_set_merge's tail, shared with keep_branch_only; <have> gains each key added."""
    for e in entries:
        k = entry_key(e)
        if k in have:
            continue
        end = len(k)
        while e[end:end + 1] in (b" ", b"\t"):  # the last line's own trailing spaces are the entry's
            end += 1
        eol = _line_ending(e)
        out += (eol if out and not _ends_blank(out) else b"") + e[:end] + eol
        have.add(k)
    return out


def keep_branch_only(head, given, working):
    """A block-shaped working copy that commit takes as it is, where the branch still holds the
    version this worktree was last given (<given>), followed by every entry of <given> that neither
    <working> nor HEAD's version (<head>, None where HEAD lacks the file) holds, in <given>'s order,
    as entry_set_merge appends one. An entry HEAD holds that the working copy dropped is a deliberate
    removal (implementation-format §1's move of a block) and stays removed; an entry only the session
    branch holds is put back whatever dropped it -- a restore of HEAD's version, a removal by hand, or
    an edit, whose old version then stays beside the edited one -- so no working copy removes or
    replaces one until the session pull request merges: a visible duplicate, never a lost entry.
    Entries are compared with their line endings taken as \\n, so a copy an editor
    saved in CRLF over LF blobs (core.autocrlf=input smudges nothing) misses nothing. <working>
    unchanged where nothing is missing; None (refuse) where something is, and the non-empty versions
    are not all in one line-ending form, as entry_set_merge refuses."""
    def key(e):
        return entry_key(e).replace(b"\r\n", b"\n")
    held = {key(e) for e in split_entries(working)[1]}
    if head is not None:
        held |= {key(e) for e in split_entries(head)[1]}
    missing = [e for e in split_entries(given)[1] if key(e) not in held]
    if not missing:
        return working
    if _forms_differ(head, given, working):
        return None
    out = working
    if out and not out.endswith(b"\n"):
        out += _line_ending(out, last=True)
    return _append_entries(out, missing, set())


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


def worktree_blob(root, path, write=False):
    """The blob id git would store for the working copy of <path> (clean filters applied), or None;
    with write, the blob is stored. Where git itself reports the tracked working copy unmodified
    against the index (diff-files), it is the index's blob: hash-object reads no index, so under
    core.autocrlf=input it turns a CRLF file's line endings into LF even where the index holds the
    CRLF blob the clean checkout came from, which then read as a copy of its own. An index entry
    marked assume-unchanged or skip-worktree, or not at stage 0, is hashed as before."""
    full = os.path.join(root, path)
    if not os.path.isfile(full):
        return None
    spec = ":(literal)" + path
    if git(root, "diff-files", "--quiet", "--", spec, check=False).returncode == 0:
        recs = nul_list(git(root, "ls-files", "-s", "-v", "-z", "--", spec))
        fields = recs[0].split("\t", 1)[0].split() if len(recs) == 1 else []
        if len(fields) == 4 and fields[0] == "H" and fields[3] == "0":
            return fields[2]
    return text(git(root, "hash-object", *(["-w"] if write else []), "--path", path, "--", path))


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


SETTLED = ("block", "lines")  # the classes settle() merges; any other is one side's version whole


def union_lines(root, path, base, ours, theirs):
    """git's union of a one-task-per-line file (follow-ups.md) from three versions, ours' lines first.
    Each line is one whole task, so union cannot fuse two; base None is an empty base. None (refuse)
    where the non-empty versions are not all in one line-ending form (_forms_differ): union matches
    lines byte for byte, so every task in \\r\\n would stand beside its copy in \\n. A version whose
    last line has no line ending is given one first, in its own form (_line_ending): git's merge-file
    matches such a line with neither its \\n nor its \\r\\n copy, and would keep it twice."""
    if _forms_differ(base, ours, theirs):
        return None
    with tempfile.TemporaryDirectory() as td:
        names = []
        for name, data in (("ours", ours), ("base", base or b""), ("theirs", theirs)):
            if data and not data.endswith(b"\n"):
                data += _line_ending(data, last=True)
            names.append(os.path.join(td, name))
            with open(names[-1], "wb") as fh:
                fh.write(data)
        r = git(root, "merge-file", "-p", "--union", *names, check=False)
        if r.returncode < 0 or r.returncode > 127:
            raise NotRun("merge-file %s: %s" % (path, r.stderr.decode("utf-8", "replace").strip()[:300]))
        return r.stdout


def _task_lines(data):
    """The lines of <data>, each without its line ending, a \\r before the \\n counted as part of it."""
    lines = data.split(b"\n") if data else []
    if lines and not lines[-1]:
        lines.pop()  # the end of the last line, not a line of its own
    return [line[:-1] if line.endswith(b"\r") else line for line in lines]


def keep_branch_only_lines(root, path, head, given, working):
    """keep_branch_only for follow-ups.md: a working copy that commit takes as it is, where the branch
    still holds the version this worktree was last given (<given>), with every line of <given> that
    neither <working> nor HEAD's version (<head>, None where HEAD lacks the file) holds brought back
    by git's union of <given> and <working> over <head> (union_lines), so a HEAD line the copy dropped
    stays dropped. Lines are compared with their line endings taken as \\n, so a copy an editor saved
    in CRLF over LF blobs (core.autocrlf=input smudges nothing) misses nothing. <working> unchanged
    where nothing is missing; None (refuse) where something is, and the non-empty versions are not
    all in one line-ending form, as union_lines refuses."""
    held = set(_task_lines(working)) | set(_task_lines(head))
    if all(line in held for line in _task_lines(given)):
        return working
    return union_lines(root, path, head, given, working)


def settle(root, path, base, ours, theirs):
    """A session file both sides changed, settled from three versions by its class: a block-shaped
    file as a set of entries (entry_set_merge), follow-ups.md by git's union (union_lines). None
    (refuse) where either refuses (the entry-set rule, or versions in two line-ending forms), where
    ours or theirs lacks the file, or for any other class. base is None where neither side's history
    holds it."""
    if ours is None or theirs is None:
        return None
    cls = merge_class(path)
    if cls == "block":
        return entry_set_merge(base, ours, theirs)
    if cls == "lines":
        return union_lines(root, path, base, ours, theirs)
    return None


def worktree_form(root, commit, path):
    """<path> as <commit> holds it, smudge filters applied as a checkout would write it, or None."""
    if blob(root, commit, path) is None:
        return None
    return git(root, "cat-file", "--filters", "%s:%s" % (commit, path)).stdout


def settle_copy(root, path, tip):
    """The working copy of <path> settled with <tip>'s version (settle(), the tip's side first, its
    entries being the older), so an entry only the branch holds survives a working copy that lacks it
    (a lift nobody put back, another worktree's commit). All three in working-tree form, as the working
    copy is, so their line endings agree wherever the checkout gives the file its line endings. The
    base is the version at merge-base HEAD <tip>, not HEAD's: HEAD can hold what the branch never had
    (a stranded commit), and the tip would then read as deleting it. None where settle() refuses (an
    entry edited or removed, the headers differing, or line endings that differ, as a copy saved in
    CRLF over LF blobs under core.autocrlf=input does), or where the tip or the working tree lacks the
    file: the caller leaves the working copy as it is."""
    full = os.path.join(root, path)
    if merge_class(path) not in SETTLED or not os.path.isfile(full) or os.path.islink(full):
        return None
    with open(full, "rb") as fh:
        theirs = fh.read()
    r = git(root, "merge-base", "HEAD", tip, check=False)
    base = worktree_form(root, text(r), path) if r.returncode == 0 and text(r) else None
    return settle(root, path, base, worktree_form(root, tip, path), theirs)


def tree_with(root, tree, entries):
    """<tree> with each of <entries> ("<mode> <sha>\\t<path>", mode 0 removing the path) written over
    it, through a temporary index: the checkout's own index is never touched."""
    gitdir = text(git(root, "rev-parse", "--absolute-git-dir"))
    with tempfile.TemporaryDirectory(dir=gitdir, prefix="session-branch-") as td:
        env = {"GIT_INDEX_FILE": os.path.join(td, "index")}
        git(root, "read-tree", tree, env=env)
        if entries:
            git(root, "update-index", "-z", "--index-info",
                data=("\0".join(entries) + "\0").encode("utf-8", "surrogateescape"), env=env)
        return text(git(root, "write-tree", env=env))


def settle_merge(root, tree, tip, c, conflicted):
    """§8.2 step 3: every block-shaped file and follow-ups.md that the merge base, <tip> and <c> each
    hold differently, settled from those three blobs by settle() and written over merge-tree's <tree>,
    whatever merge-tree wrote for it: -X ours alone keeps only this side's entries, and the marked
    block names no block-shaped file, so a repository .gitattributes picks git's driver for one. The
    merge base is the one git merge-base prints. Returns the tree, and the paths that stop this merge:
    each one settle() refuses, and each other path merge-tree reported conflicted (<conflicted>)."""
    r = git(root, "merge-base", tip, c, check=False)
    mb = text(r) if r.returncode == 0 and text(r) else None

    def changed(a, b):
        out = nul_list(git(root, "diff", "--name-only", "-z", "--no-renames", a, b))
        return {p for p in out if merge_class(p) in SETTLED}

    def read(sha):
        return None if sha is None else git(root, "cat-file", "blob", sha).stdout

    settled, refused = {}, []
    for p in sorted(changed(tip, c) if mb is None else changed(mb, tip) & changed(mb, c)):
        b0, b1, b2 = blob(root, mb, p), blob(root, tip, p), blob(root, c, p)
        if b0 in (b1, b2) or b1 == b2:
            continue  # one side's change alone, or the same change on both, which merge-tree took
        data = settle(root, p, read(b0), read(b1), read(b2))
        if data is None:
            refused.append(p)
        else:
            settled[p] = data
    entries = []
    if settled:
        recs = nul_list(git(root, "ls-tree", "-z", tree, "--", *settled))
        modes = {rec.split("\t", 1)[1]: rec.split(" ", 1)[0] for rec in recs}
        for p, data in sorted(settled.items()):
            if p not in modes:  # merge-tree placed it elsewhere: nothing to write it over
                refused.append(p)
                continue
            sha = text(git(root, "hash-object", "-w", "--stdin", data=data))
            entries.append("%s %s\t%s" % (modes[p], sha, p))
    refused = sorted(set(refused) | (set(conflicted) - set(settled)))
    if refused:
        return tree, refused
    return tree_with(root, tree, entries), []


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


def commit_tree(root, tree, parents, message, env=None):
    """commit-tree reads no commit.gpgSign, so a user who signs their commits would push unsigned
    session commits; sign them as git commit would. The message (bytes, or str written as UTF-8) is
    passed byte for byte through -F -, never -m, which completes its last line; a caller that wants
    a final newline writes it. env carries GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL and GIT_AUTHOR_DATE where
    the commit keeps another commit's authorship (the replay); the committer is always now."""
    sign = ["-S"] if config(root, "commit.gpgSign", as_bool=True) == "true" else []
    parent_args = [x for p in parents for x in ("-p", p)]
    data = message if isinstance(message, bytes) else message.encode("utf-8", "surrogateescape")
    return text(git(root, "commit-tree", *sign, tree, *parent_args, "-F", "-", data=data, env=env))


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
    nothing of its own, else merge-tree -X ours with the block-shaped files and follow-ups.md settled
    from their three blobs (settle_merge); then align the overlay. A source that cannot be settled so
    is not merged at all: its paths are listed in conflict, and each with that source -- <default-ref>
    or origin/<branch>, as given -- in conflicts."""
    refuse_checked_out(root, branch)
    ensure_attributes(root)
    ref = "refs/heads/" + branch
    base = rev(root, default_ref)
    if base is None:
        raise NotRun("no such ref: %s" % default_ref)
    tip = rev(root, ref)
    result = {"created": False, "merged": False, "fast_forward": False, "tip": tip, "conflict": [],
              "conflicts": [], "deferred": [], "aligned": []}
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
        r = git(root, "merge-tree", "--write-tree", "-z", "--name-only", "--no-messages", "-X", "ours", tip, c,
                check=False)
        out = nul_list(r)
        if r.returncode not in (0, 1) or not out:
            raise NotRun("merge-tree: %s" % r.stderr.decode("utf-8", "replace").strip()[:300])
        tree, refused = settle_merge(root, out[0], tip, c, out[1:] if r.returncode == 1 else [])
        if refused:  # no merge commit for this source; the next run tries again
            result["conflict"] = sorted(set(result["conflict"]) | set(refused))
            result["conflicts"] += [{"path": p, "source": name} for p in refused]
            continue
        merge = commit_tree(root, tree, [tip, c], "NOISSUE Merge %s into %s\n" % (name, branch))
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
    <default-ref> in and align the overlay. Never touches the checkout, the index or HEAD.
    A block-shaped working copy, or follow-ups.md, that differs from the tip's version is committed
    as it is where the tip still holds the version this worktree was last given (its record, else
    HEAD's), so a hand edit goes through -- a block-shaped one with every entry of that version that
    neither it nor HEAD's version holds put back after it (keep_branch_only), follow-ups.md, where a
    line of that version is missing from both it and HEAD's, united with that version over HEAD's
    (keep_branch_only_lines), so a line only the session branch held returns while a HEAD line the
    copy dropped stays dropped; where the tip holds another version, the working copy is first
    settled with it (settle_copy). Either is written back, or, where it refuses, the file is left out
    of the commit and as it is in the working tree, and listed in unsettled. A file the tip has no
    version of, any other shape, and a deletion are committed as they are."""
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
    added, dropped, unsettled = {}, [], []
    committed, changed = None, []
    if paths:
        entries = []
        for p in paths:
            full = os.path.join(root, p)
            if os.path.isfile(full) and not os.path.islink(full):
                t = blob(root, tip, p)
                given = placed[p] if p in placed else blob(root, "HEAD", p)
                cls = merge_class(p)
                if cls in SETTLED and t not in (None, worktree_blob(root, p)):
                    with open(full, "rb") as fh:
                        working = fh.read()
                    if t != given:  # the tip holds another version than this worktree was given
                        settled = settle_copy(root, p, tip)
                    elif cls == "block":  # as it is, with any entry only the session branch held
                        head = worktree_form(root, "HEAD", p)
                        settled = keep_branch_only(head, worktree_form(root, tip, p), working)
                    else:  # follow-ups.md: a HEAD line the copy dropped stays dropped, a session-only one returns
                        settled = keep_branch_only_lines(root, p, worktree_form(root, "HEAD", p),
                                                         worktree_form(root, tip, p), working)
                    if settled is None:
                        unsettled.append(p)
                        continue
                    if settled != working:
                        write_bytes(root, p, settled)
                sha = worktree_blob(root, p, write=True)
                mode_bits = "100755" if os.stat(full).st_mode & stat.S_IXUSR else "100644"
                entries.append("%s %s\t%s" % (mode_bits, sha, p))
                if sha != blob(root, "HEAD", p):  # a stranded file HEAD holds is not the overlay's
                    added[p] = sha
            else:
                entries.append("0 %s\t%s" % (ZERO, p))
                dropped.append(p)
        tree = tree_with(root, tip, entries)
        if tree != text(git(root, "rev-parse", tip + "^{tree}")):
            committed = commit_tree(root, tree, [tip], message if message.endswith("\n") else message + "\n")
            git(root, "update-ref", ref, committed, tip)
            changed = nul_list(git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", tip, committed))
        mark(root, put=added, drop=dropped)
    try:
        synced = sync(root, branch, default_ref)
    except NotRun as e:  # the commit stands; the merge waits for a run that can make it
        synced = {"error": str(e)}
    return {"committed": committed, "files": len(changed), "paths": changed, "created": created,
            "stranded": len(stranded), "ahead_not_session": not_session, "unsettled": unsettled, "sync": synced}


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
    one this worktree was last given. Any other working copy holds entries of its own: a block-shaped
    file or follow-ups.md is settled with the branch's (settle_copy) and listed in merged; where that
    refuses, and for any other shape, it is left as it is and listed in skipped."""
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
            settled = settle_copy(root, p, tip)
            if settled is None:
                skipped.append(p)
            else:
                write_bytes(root, p, settled)
                merged.append(p)  # unrecorded: it holds entries of its own for the next commit
            continue
        mark(root, put={p: want} if want else None, drop=() if want else [p])
        write_from(root, tip, p)
        (removed if want is None else written).append(p)
    return {"written": written, "removed": removed, "merged": merged, "skipped": skipped, "sync": synced}


# ---- the replay (spec §3.2, §3.3) ---------------------------------------------------------------------

# The attributes the replay passes to its merge-tree call as -c core.attributesFile=<a temporary file>
# (spec §3.2 step 1), and never writes into info/attributes outside session-branch mode: §8's block,
# line for line -- union for follow-ups.md, -merge for the overwritten shapes and the register files,
# nothing for a block-shaped file. It is the lowest-precedence attribute source, so a repository
# .gitattributes outranks it: replay_commits settles every path both sides changed from its three
# blobs itself, whatever git's merge of that path produced.
REPLAY_BLOCK = "".join(line + "\n" for line in ATTRIBUTES)
_SLUG_RE = re.compile(r"^security/([^/]+)/")


def replay_ok(root):
    """This git can replay without a checkout (spec §3.1 condition 3): merge-tree takes --write-tree
    and a merge base the caller names. Its usage prints --merge-base on git 2.40 and --[no-]merge-base
    from 2.41 on, so "merge-base" alone is looked for."""
    r = git(root, "merge-tree", "-h", check=False)
    usage = (r.stdout + r.stderr).decode("utf-8", "replace")
    return "--write-tree" in usage and "merge-base" in usage


def _tree_entries(root, tree, paths):
    """path -> (mode, object id) for each of <paths> that <tree> holds."""
    out = {}
    if paths:
        for rec in nul_list(git(root, "ls-tree", "-z", tree, "--", *paths)):
            meta, path = rec.split("\t", 1)
            mode, _kind, sha = meta.split()
            out[path] = (mode, sha)
    return out


def _commit_parts(root, c):
    """<c>'s author as commit-tree's environment takes it, and its message byte for byte, read from
    the commit object itself, so no log.showSignature, mailmap or re-encoding reaches either."""
    head, _, message = git(root, "cat-file", "commit", c).stdout.partition(b"\n\n")
    author = next((line[len(b"author "):] for line in head.split(b"\n") if line.startswith(b"author ")), b"")
    lt, gt = author.rfind(b" <"), author.rfind(b"> ")
    if lt < 0 or gt < lt:
        raise NotRun("%s has no author line commit-tree can take" % c)
    name, email, date = (x.decode("utf-8", "surrogateescape") for x in (author[:lt], author[lt + 2:gt], author[gt + 2:]))
    return {"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email, "GIT_AUTHOR_DATE": date}, message


def _fill(root, tree, prefix, dest):
    """Write each file <tree> holds under <prefix> into <dest> at its own path, read by ls-tree and
    cat-file -- never git archive, which honours a repository's export-ignore. Returns how many."""
    blobs = []
    for rec in nul_list(git(root, "ls-tree", "-r", "-z", tree, "--", prefix)):
        meta, path = rec.split("\t", 1)
        _mode, kind, sha = meta.split()
        if kind != "blob":
            continue
        if ".." in path.split("/"):
            raise NotRun("%s holds a path outside its tree: %s" % (tree, path))
        blobs.append((path, sha))
    if not blobs:
        return 0
    out = git(root, "cat-file", "--batch", data="".join(sha + "\n" for _, sha in blobs).encode("ascii")).stdout
    pos = 0
    for path, sha in blobs:  # each answer: "<id> blob <size>\n<content>\n", in the order asked
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].split()[2])
        full = os.path.join(dest, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as fh:
            fh.write(out[nl + 1:nl + 1 + size])
        pos = nl + 1 + size + 1
    return len(blobs)


def _rebuild(root, tree, slug, register_rebuild):
    """`<register_rebuild> rebuild` over <tree>'s security/<slug>/, copied into a temporary root
    (spec §3.3): (the numbers map it printed, {"register.json": bytes, "register.md": bytes}); None
    where it exits non-zero, prints no JSON object, or leaves either file unwritten; ({}, None) where
    <tree> holds nothing under security/<slug>/, so there is nothing to rebuild."""
    with tempfile.TemporaryDirectory(prefix="session-branch-rebuild-") as td:
        if not _fill(root, tree, "security/%s/" % slug, td):
            return {}, None
        r = subprocess.run([sys.executable, "-I", register_rebuild, "rebuild", "--specs", td, "--slug", slug],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            printed = json.loads(r.stdout.decode("utf-8"))
        except ValueError:
            printed = None
        numbers = printed.get("numbers", {}) if isinstance(printed, dict) else None
        if r.returncode != 0 or not isinstance(numbers, dict):
            return None
        files = {}
        for name in ("register.json", "register.md"):
            full = os.path.join(td, "security", slug, name)
            if not os.path.isfile(full):
                return None
            with open(full, "rb") as fh:
                files[name] = fh.read()
        return numbers, files


def replay_commits(root, onto, commits, register_rebuild):
    """Spec §3.2 and §3.3: <commits> -- a run's own session-file commits, oldest first, one parent
    each -- replayed onto <onto> with no checkout. Only objects are written: nothing in the checkout,
    the index or any ref moves. Each commit c, on its parent p, goes through merge-tree --write-tree
    --merge-base=p onto c with REPLAY_BLOCK, never -X. The paths settled are those whose blobs at p,
    onto and c all differ (diff-tree --no-renames of p..onto and p..c); a path onto and c hold alike
    keeps that content. Each is settled by merge_class: "block" (entry_set_merge) and "lines" (git's
    union) by settle(), onto's side first, from the three blobs as stored, refused where either side
    lacks the file or the rule refuses; "whole" is c's version, a deletion included; "register" is
    rebuilt; any other class is refused, as is any other path merge-tree reports conflicted. A
    register is rebuilt wherever both sides changed something under security/<slug>/ that the other
    side does not hold alike: <register_rebuild>'s rebuild over the merged tree's security/<slug>/,
    its two files written back through a temporary index; refused where no script was handed over
    or it fails. A merged tree equal to onto's drops c, its change being there already; otherwise c
    is committed on onto with its author, author date and message byte for byte (commit_tree), each
    file in the mode the merged tree gives it, and onto becomes that commit.
    Returns {tip, replayed: the new commits, dropped: the commits already there, numbers:
    {before_remote, before_run, after}, each slug -> the numbers map rebuild printed on the first
    onto, on the last of <commits> and on the tip, for every register rebuilt, refused: None}. On a
    refusal, refused is {reason: "conflict" or "register-rebuild", path: the first path refused, or
    security/<slug>/}, tip is None, so nothing can be moved onto a partial replay, and numbers are
    empty."""
    tip = rev(root, onto)
    if tip is None:
        raise NotRun("no such commit: %s" % onto)
    first, replayed, dropped, rebuilt = tip, [], [], set()

    def refusal(reason, path):
        return {"tip": None, "replayed": replayed, "dropped": dropped,
                "numbers": {"before_remote": {}, "before_run": {}, "after": {}},
                "refused": {"reason": reason, "path": path}}

    def read(sha):
        return None if sha is None else git(root, "cat-file", "blob", sha).stdout

    def changed(a, b):
        return set(nul_list(git(root, "diff-tree", "-r", "-z", "--no-renames", "--name-only", a, b)))

    with tempfile.TemporaryDirectory(prefix="session-branch-replay-") as td:
        block = os.path.join(td, "attributes")
        with open(block, "w", encoding="utf-8") as fh:
            fh.write(REPLAY_BLOCK)
        for c in commits:
            ids = text(git(root, "rev-list", "--parents", "-n", "1", c)).split()
            if len(ids) != 2:
                raise NotRun("%s is a root or a merge commit, which the replay never takes" % c)
            c, p = ids
            r = git(root, "-c", "core.attributesFile=" + block, "merge-tree", "--write-tree", "-z", "--name-only",
                    "--no-messages", "--merge-base=" + p, tip, c, check=False)
            out = nul_list(r)
            if r.returncode not in (0, 1) or not out:
                raise NotRun("merge-tree: %s" % r.stderr.decode("utf-8", "replace").strip()[:300])
            tree, conflicted = out[0], set(out[1:]) if r.returncode == 1 else set()
            ours, theirs = changed(p, tip), changed(p, c)
            both = sorted(ours & theirs)
            at_p, at_o, at_c = (_tree_entries(root, t, sorted(set(both) | {x for x in ours | theirs if _SLUG_RE.match(x)}))
                                for t in (p, tip, c))

            def sha(held, x):
                return held[x][1] if x in held else None

            def slugs(side):
                return {_SLUG_RE.match(x).group(1) for x in side if _SLUG_RE.match(x) and sha(at_o, x) != sha(at_c, x)}
            regs = sorted(slugs(ours) & slugs(theirs))
            merged = _tree_entries(root, tree, both)
            entries, refused, settled = [], [], set()
            for x in both:
                b0, b1, b2 = sha(at_p, x), sha(at_o, x), sha(at_c, x)
                cls = merge_class(x)
                if b1 == b2 or b0 in (b1, b2) or cls == "register":
                    continue  # one side's change alone, or the same on both: merge-tree's stands; a register is rebuilt
                if cls == "whole" and b2 is None:
                    entries.append("0 %s\t%s" % (ZERO, x))
                elif cls == "whole":
                    entries.append("%s %s\t%s" % (merged.get(x, at_c[x])[0], b2, x))
                elif cls in SETTLED:
                    data = settle(root, x, read(b0), read(b1), read(b2))
                    if data is None:
                        refused.append(x)
                        continue
                    new = text(git(root, "hash-object", "-w", "--stdin", data=data))
                    entries.append("%s %s\t%s" % (merged.get(x, at_c[x])[0], new, x))
                else:
                    refused.append(x)
                    continue
                settled.add(x)
            rebuilt_paths = {x for x in conflicted if merge_class(x) == "register" and _SLUG_RE.match(x).group(1) in regs}
            refused += sorted(conflicted - settled - rebuilt_paths)
            if refused:
                return refusal("conflict", sorted(refused)[0])
            if entries:
                tree = tree_with(root, tree, entries)
            if regs and not register_rebuild:
                return refusal("register-rebuild", "security/%s/" % regs[0])
            reg_entries = []
            for s in regs:
                got = _rebuild(root, tree, s, register_rebuild)
                if got is None:
                    return refusal("register-rebuild", "security/%s/" % s)
                names = ["security/%s/%s" % (s, n) for n in sorted(got[1] or {})]
                held = _tree_entries(root, tree, names)
                for path in names:
                    new = text(git(root, "hash-object", "-w", "--stdin", data=got[1][path.rsplit("/", 1)[1]]))
                    reg_entries.append("%s %s\t%s" % (held.get(path, ("100644",))[0], new, path))
                rebuilt.add(s)
            if reg_entries:
                tree = tree_with(root, tree, reg_entries)
            if tree == text(git(root, "rev-parse", tip + "^{tree}")):
                dropped.append(c)
                continue
            env, message = _commit_parts(root, c)
            tip = commit_tree(root, tree, [tip], message, env=env)
            replayed.append(tip)
    numbers = {"before_remote": {}, "before_run": {}, "after": {}}
    for s in sorted(rebuilt):
        for key, commit in (("before_remote", first), ("before_run", commits[-1]), ("after", tip)):
            got = _rebuild(root, commit, s, register_rebuild)
            if got is None:
                return refusal("register-rebuild", "security/%s/" % s)
            numbers[key][s] = got[0]
    return {"tip": tip, "replayed": replayed, "dropped": dropped, "numbers": numbers, "refused": None}


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

        def add(self, rel, e, eol="\n"):
            """Append an entry as a run appends it: after one empty line, in the file's line endings."""
            self.write(rel, ("\n" + e).replace("\n", eol), append=True)

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

    def entry(date, command, body):
        """A feedback-emission §1 entry, as a run appends it to FB. Two of one day and one command
        share every line but their id and their prose, as two real ones do: the shape git's union
        driver fused into one."""
        slug = re.sub(r"[^a-z0-9]+", "-", body.lower()).strip("-")
        return ("## %s — %s — missing-capability\n"
                "\n"
                "```yaml\n"
                "id: A-1-%s-%s\n"
                "date: %s\n"
                "command: %s\n"
                "plugin_version: 4.40.0\n"
                "origin: auto\n"
                "author: t@example.invalid\n"
                "category: missing-capability\n"
                "impact: friction\n"
                "```\n"
                "\n"
                "**Friction:** %s\n" % (date, command, command.lstrip("/"), slug, date, command, body))

    def today(body):
        """An entry a /implement run appends to FB today."""
        return entry("2026-10-28", "/implement", body)

    def count(text, e):
        """How often the entry <e> stands whole in <text>; git show drops a file's final newline."""
        return (text or "").count(e.rstrip("\n"))

    SEED = ("---\ntype: dev-workflows-feedback\nprd: A-1\nslug: x\n---\n\n"
            + entry("2026-10-01", "/implement", "e0 first"))

    def world(tmp):
        """A bare remote whose pre-receive hook refuses main unless ALLOW_MAIN is set, and two clones."""
        seed = Repo(os.path.join(tmp, "seed"))
        subprocess.run(["git", "init", "-q", "-b", "main", seed.path], check=True)
        seed.configure()
        seed.write("specifications/PRD-A-1-x/prd.md", "# PRD\n")
        seed.write(FB, SEED)
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
        both = IMPL_HEAD + IMPL_1 + "\n" + IMPL_2
        got = esm(None, both, IMPL_HEAD + IMPL_1), esm(None, IMPL_HEAD + IMPL_1, both)
        check(got == (both, both), "add/add where both sides hold an entry keeps it once, from either side (%r)" % (got,))
        got = esm(None, crlf(IMPL_HEAD + IMPL_1), crlf(both))
        check(got == crlf(both) and not bare_lf(got), "add/add of two CRLF sides still merges (%r)" % got)

        # sides in different line-ending forms refuse: no entry of one matches its copy in the other
        got = esm(None, crlf(IMPL_HEAD + IMPL_1), both)
        check(got is None, "add/add of a CRLF side and an LF side refuses (%r)" % got)
        base = IMPL_HEAD + IMPL_1
        for b_, o_, t_ in ((crlf(base), crlf(both), base + "\n" + IMPL_2P),
                           (base, crlf(both), crlf(base + "\n" + IMPL_2P)),
                           (base, both, both.replace("\n", "\r\n", 1)),
                           (IMPL_HEAD, crlf(base), crlf(IMPL_HEAD + IMPL_2))):
            got = esm(b_, o_, t_)
            check(got is None, "three versions not all in one line-ending form refuse (%r)" % got)
        # a version with no line ending at all reads as LF, the ending its last line is completed with
        top = IMPL_HEAD.rstrip("\n")
        got = esm(None, top, IMPL_HEAD + IMPL_1)
        check(got == IMPL_HEAD + IMPL_1, "a header with no line ending at all merges with an LF side, in LF (%r)" % got)
        got = esm(top, IMPL_HEAD + IMPL_1, IMPL_HEAD + IMPL_2)
        check(got == IMPL_HEAD + IMPL_1 + "\n" + IMPL_2, "…as a base too (%r)" % got)
        got = esm(None, top, crlf(IMPL_HEAD + IMPL_1)), esm(top, crlf(base), crlf(both))
        check(got == (None, None), "…and refuses beside a CRLF one (%r)" % (got,))

        # each entry is kept once, and an empty line already ending ours is the separator
        got = esm(base, base + "\n" + IMPL_2, base + "\n" + IMPL_2P + "\n" + IMPL_2P)
        check(got == base + "\n" + IMPL_2 + "\n" + IMPL_2P, "a new entry theirs holds twice is added once (%r)" % got)
        for ours in (base + "\n" + IMPL_2 + "\n", base + "\n" + IMPL_2 + "\n \n"):
            got = esm(base, ours, base + "\n" + IMPL_2P)
            check(got == ours + IMPL_2P, "ours ending in a blank line gains no second one before the entry (%r)" % got)
        ours = crlf(base + "\n" + IMPL_2 + "\n")
        got = esm(crlf(base), ours, crlf(base + "\n" + IMPL_2P))
        check(got == ours + crlf(IMPL_2P), "…in CRLF too (%r)" % got)

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

        # a base entry missing from both sides is an agreed removal or edit, as a three-way merge
        # takes one: it stays removed, an identical edit is kept once, two different edits both stay
        B3 = IMPL_2P.replace("7be0d41", "b3b3b3b")
        got = esm(base, IMPL_HEAD + IMPL_2 + "\n" + IMPL_2P, IMPL_HEAD + IMPL_2 + "\n" + B3)
        check(got == IMPL_HEAD + IMPL_2 + "\n" + IMPL_2P + "\n" + B3,
              "an entry both sides removed stays removed, and each side's addition is kept (%r)" % got)
        fixed = base.replace("commit:  a3f91c2", "commit:  a3f91c3")
        got = esm(base, fixed + "\n" + IMPL_2P, fixed + "\n" + B3)
        check(got == fixed + "\n" + IMPL_2P + "\n" + B3, "the same edit on both sides is kept once (%r)" % got)
        other = base.replace("commit:  a3f91c2", "commit:  a3f91c4")
        got = esm(base, fixed, other)
        check(got == fixed + "\n" + IMPL_1.replace("commit:  a3f91c2", "commit:  a3f91c4"),
              "two different edits of one entry both stay, a visible duplicate rather than a lost edit (%r)" % got)
        # …and the two consequences §8.2 step 3 and spec §3.3 name: a removal on one side against an
        # edit on the other keeps the edit; both sides extending the last entry keep it twice
        got = esm(base, IMPL_HEAD + IMPL_2, fixed)
        check(got == IMPL_HEAD + IMPL_2 + "\n" + IMPL_1.replace("commit:  a3f91c2", "commit:  a3f91c3"),
              "a removal against an edit of one entry keeps the edit, the removal lost (%r)" % got)
        got = esm(base, base + "  note:    ours\n", base + "  note:    theirs\n")
        check(got == base + "  note:    ours\n\n" + IMPL_2 + "  note:    theirs\n",
              "both sides extending the last entry keep it twice, once with each tail (%r)" % got)

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
            a.add(FB, today("a1 mine"))
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
            TEAM, A1, TEAM2 = today("team from b"), today("a1 mine"), today("team2 again")
            b.add(FB, TEAM)
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
            mine = SEED + "\n" + TEAM + "\n" + A1
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
            b.add(FB, TEAM2)
            b.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: team2\n")
            b.commit_all("team2")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            before = a.state()
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("merged") is True and not got.get("conflict"), "a moved main is merged in (%r)" % got)
            merged = a.git("show", "session/aa:" + FB)
            check(merged == (mine + "\n" + TEAM2).rstrip("\n"),
                  "both sides' appended entries survive the merge, each once and whole, the branch's first (%r)" % merged)
            check(a.read(FB) == merged + "\n" and got.get("aligned") == [FB],
                  "the working copy that equalled the old tip now holds the merge (%r)" % got.get("aligned"))
            check(a.git("show", "session/aa:specifications/PRD-A-1-x/dev-workflows/resume.md") == "pos: mine",
                  "an overwritten resume.md keeps the session side")
            check(len(a.git("rev-list", "--parents", "-n", "1", "session/aa").split()) == 3, "the merge has two parents")
            check(a.state() == before, "sync moves no checkout, index or HEAD")
            attrs = a.read(".git/info/attributes")
            check(attrs is not None and attrs.count(ATTR_BEGIN) == 1
                  and "\n".join([ATTR_BEGIN, *ATTRIBUTES, ATTR_END]) + "\n" in attrs,
                  "the attributes block is written once (%r)" % attrs)
            a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            check(a.read(".git/info/attributes").count(ATTR_BEGIN) == 1, "and stays one block on a second sync")
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.git("branch", "session/aa")
            a.write("specifications/PRD-A-1-x/follow-ups.md", "- [ ] x\n")  # dirty, and not on the branch
            b.add(FB, today("team"))
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
            changed = SEED + "\n" + today("a1 mine")
            sha = subprocess.run(["git", "-C", a.path, "hash-object", "-w", "--stdin"], input=changed.encode(),
                                 stdout=subprocess.PIPE, check=True).stdout.decode().strip()
            a.git("update-index", "--cacheinfo", "100644,%s,%s" % (sha, FB), env=env)
            c = a.git("commit-tree", a.git("write-tree", env=env), "-p", "session/aa", "-m", "mod")
            a.git("update-ref", "refs/heads/session/aa", c)
            a.write(FB, changed)
            b.git("rm", "-q", FB)
            b.git("commit", "-q", "-m", "delete feedback")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("conflict") == [FB] and a.git("rev-parse", "session/aa") == c,
                  "a modify/delete merge is reported and moves nothing (%r)" % got)
            check(got.get("conflicts") == [{"path": FB, "source": "origin/main"}],
                  "…naming the default ref as its source (%r)" % got.get("conflicts"))

        # ---- commit ----------------------------------------------------------------------------
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            odd = "dev-workflows-cost/:odd pending ü.md"  # the shape a run deletes (cost-emission §9)
            A1, A2 = today("a1 mine"), today("a2 more")
            a.add(FB, A1)
            a.write(odd, "cost\n")
            before = a.state()
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(got.get("created") is True and got.get("committed"), "the first commit creates the branch (%r)" % got)
            check(sorted(got.get("paths", [])) == sorted([FB, odd]), "it carries both files (%r)" % got)
            check(a.state() == before, "commit moves no checkout, index or HEAD")
            check(a.git("show", "session/aa:" + FB) == (SEED + "\n" + A1).rstrip("\n"), "the branch holds the appended entry")
            check(a.git("merge-base", "session/aa", "main") == a.git("rev-parse", "main"), "the branch starts from the checkout's base")
            again = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(again.get("committed") is None and again.get("files") == 0, "an unchanged tree commits nothing (%r)" % again)
            a.add(FB, A2)
            tip = a.git("rev-parse", "session/aa")
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(a.git("rev-parse", "session/aa^") == tip, "a second commit stacks on the first (%r)" % got)
            check(a.git("show", "session/aa:" + FB) == (SEED + "\n" + A1 + "\n" + A2).rstrip("\n"),
                  "…holding each entry once (%r)" % a.git("show", "session/aa:" + FB))
            os.remove(os.path.join(a.path, odd))  # an overlay-only file: never in the index, so git status forgets it
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Remove pending")
            check(odd in got.get("paths", []), "a removed overlay file is committed as a deletion (%r)" % got)
            check(subprocess.run(["git", "-C", a.path, "cat-file", "-e", "session/aa:" + odd], stderr=devnull).returncode != 0,
                  "…and the branch no longer has it")
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            # main moves on the remote during the run, appending to the same file
            A1, TEAM = today("a1 mine"), today("team from b")
            a.add(FB, A1)
            b.add(FB, TEAM)
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            content = a.git("show", "session/aa:" + FB)
            check(content == (SEED + "\n" + A1 + "\n" + TEAM).rstrip("\n") and got["sync"].get("merged") is True,
                  "the commit is built first and main merged second, so no entry is lost (%r)" % content)
            check(a.read(FB) == content + "\n", "the working copy is aligned to the merged version (%r)" % a.read(FB))
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            # the interim left a session-file commit on local main that origin refused
            STRANDED = today("stranded old")
            a.add(FB, STRANDED)
            a.commit_all("A-1 Add dev-workflows session artifacts (implement)")
            head = a.git("rev-parse", "HEAD")
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session",
                        "--include-ahead")
            check(got.get("stranded") == 1 and count(a.git("show", "session/aa:" + FB), STRANDED) == 1,
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
            A1 = today("a1 mine")
            a.add(FB, A1)
            got = a.run("lift", "--branch", "session/aa")
            check(got.get("unpreserved") == [FB] and not got.get("lifted") and count(a.read(FB), A1) == 1,
                  "lift refuses, and discards nothing, where a session file is not on the branch (%r)" % got)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.write(fu, "- [ ] task\n")
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            got = a.run("lift", "--branch", "session/aa")
            check(sorted(got.get("lifted", [])) == sorted([FB, fu]) and not got.get("unpreserved"),
                  "lift returns preserved files to HEAD (%r)" % got)
            check(a.read(fu) is None and count(a.read(FB), A1) == 0 and a.git("status", "--porcelain") == "",
                  "an untracked one is removed and a tracked one restored: the checkout is clean")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(sorted(got.get("written", [])) == sorted([FB, fu]) and count(a.read(FB), A1) == 1 and a.read(fu),
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
                A1, B1 = today("a1 from a"), today("b1 from b")
                a.add(FB, A1)
                a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
                a.git("push", "-q", "-u", "origin", "session/aa")
                merge_on_remote(tmp, remote, "session/aa", how)
                b.add(FB, B1)
                b.git("fetch", "-q", "origin")
                got = b.run("lift", "--branch", "session/bb")
                if got.get("unpreserved"):
                    b.run("commit", "--branch", "session/bb", "--default-ref", "origin/main", "--message", "A-1 Add session")
                    got = b.run("lift", "--branch", "session/bb")
                check(not got.get("unpreserved"), "[%s] b lifts once its files are on its branch (%r)" % (how, got))
                b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                got = b.run("put-back", "--branch", "session/bb", "--default-ref", "origin/main")
                fb = b.read(FB)
                check(count(fb, A1) == 1 and count(fb, B1) == 1,
                      "[%s] b's checkout holds a's merged entry and its own, each once (%r)" % (how, fb))
                on_branch = b.git("show", "session/bb:" + FB)
                check(count(on_branch, A1) == 1 and count(on_branch, B1) == 1, "[%s] …and so does b's session branch" % how)
                a.git("fetch", "-q", "origin")
                got = a.run("lift", "--branch", "session/aa")
                check(not got.get("unpreserved"), "[%s] a lifts (%r)" % (how, got))
                a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
                check(a.git("diff", "--name-only", "HEAD", "session/aa", "--", FB) == "",
                      "[%s] once its pull request merged, a's branch holds nothing for that file main lacks (%r)" % (how, got))
                check(count(a.git("show", "session/aa:" + FB), A1) == 1, "[%s] …its entry once" % how)
                check(a.git("status", "--porcelain", "--", FB) == "", "[%s] …so a's checkout shows it clean" % how)
        # the same identity on a second clone: the session branch already on origin is merged in
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            A1, A2 = today("a1 from clone a"), today("a2 from clone b")
            a.add(FB, A1)
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.git("push", "-q", "-u", "origin", "session/aa")
            b.git("fetch", "-q", "origin")
            b.add(FB, A2)
            got = b.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            on_branch = b.git("show", "session/aa:" + FB)
            check(count(on_branch, A1) == 1 and count(on_branch, A2) == 1 and got["sync"].get("merged") is True,
                  "a session branch already on origin is merged into the new local one (%r)" % on_branch)
            check(b.git("push", "--porcelain", "origin", "session/aa", check=False).find("[rejected]") < 0
                  and b.git("rev-parse", "session/aa") == b.git("ls-remote", "origin", "refs/heads/session/aa").split()[0],
                  "…so its push is a fast-forward")
            check(count(b.read(FB), A1) == 1, "…and the working copy holds the other clone's entry")
        # a session branch someone checked out is never moved under that checkout
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.run("lift", "--branch", "session/aa")
            a.git("switch", "-q", "session/aa")
            tip = a.git("rev-parse", "session/aa")
            a.add(FB, today("a2"))
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
            a.add(FB, today("a1"))
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
            a.add(FB, today("a1"))
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
                  and count(a.read(FB), today("a1")) == 1, "…and put-back brings every file back")
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
            a.add(FB, today("a1"))
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM)
            wt = Repo(os.path.join(tmp, "wt"))
            a.git("worktree", "add", "-q", "-b", "prd/A-1-x", wt.path)
            wt.write("specifications/PRD-A-1-x/dev-workflows/cost/s2.md", "cost two\n")
            got = wt.run("commit", "--branch", "session/aa", *CM)
            check(got.get("paths") == ["specifications/PRD-A-1-x/dev-workflows/cost/s2.md"]
                  and count(a.git("show", "session/aa:" + FB), today("a1")) == 1 and a.git("show", "session/aa:" + cost1) == "cost one",
                  "a commit from a worktree the overlay never reached deletes and reverts nothing (%r)" % got)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("stranded"))
            a.commit_all("A-1 Add dev-workflows session artifacts (implement)")
            a.write(cost1, "cost one\n")
            a.run("commit", "--branch", "session/aa", *CM, "--include-ahead")
            a.run("lift", "--branch", "session/aa")
            a.git("reset", "-q", "--keep", "origin/main")  # the remedy §6 names for the stranded commits
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(count(a.git("show", "session/aa:" + FB), today("stranded")) == 1 and a.git("show", "session/aa:" + cost1) == "cost one",
                  "after the stranded-commit remedy a commit keeps the stranded entry and the cost file (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(count(a.read(FB), today("stranded")) == 1 and a.read(cost1) == "cost one\n", "…and put-back restores both")
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
            a.add(FB, today("a1"))
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
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", *CM)
            os.remove(os.path.join(a.path, FB))
            got = a.run("commit", "--branch", "session/aa", *CM)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("committed") is None and count(a.read(FB), today("a1")) == 1 and count(a.git("show", "session/aa:" + FB), today("a1")) == 1,
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
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(im, IMPL_HEAD + IMPL_1)
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            a.run("lift", "--branch", "session/aa")
            a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("sync", {}).get("merged") is True and not got["sync"].get("deferred")
                  and a.read(im) == IMPL_HEAD + IMPL_1 and count(a.read(FB), today("a1")) == 1,
                  "put-back after a catch-up merges the new default branch and keeps a teammate's file (%r)" % got)
        # a hand-edited log keeps the branch's older entries first
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            PREV, RUN = today("e-prev"), today("e-run")
            a.add(FB, PREV)
            a.run("commit", "--branch", "session/aa", *CM)
            a.run("lift", "--branch", "session/aa")
            a.add(FB, RUN)  # appended to HEAD's version: the lift was never put back
            got = a.run("commit", "--branch", "session/aa", *CM)
            on = a.git("show", "session/aa:" + FB)
            check(on == (SEED + "\n" + PREV + "\n" + RUN).rstrip("\n") and got.get("unsettled") == [],
                  "the entry-set merge puts the branch's entries before the working copy's, each once (%r)" % on)
        # a concurrent session that moves the branch mid-commit wins, and this run's files stay
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("a1"))
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
            a.add(FB, today("a2"))
            got = a.run("commit", "--branch", "session/aa", *CM, env={"SB_REPO": a.path, "SB_OTHER": other})
            check(got.get("_rc") == 2 and a.git("rev-parse", "session/aa") == other and count(a.read(FB), today("a2")) == 1,
                  "a branch moved under a commit is left as moved, exit 2, the files kept (%r)" % got)
        # only follow-ups.md merges by union; the overwritten and register shapes are unset; no
        # block-shaped file is named, and a clone's older block is rewritten in place
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            info = os.path.join(a.path, ".git", "info", "attributes")
            older = "\n".join([ATTR_BEGIN, "**/dev-workflows/** merge=union", "**/implementation.md merge=union",
                               "**/*-implementation-gaps.md merge=union", ATTR_END]) + "\n"
            with open(info, "w", encoding="utf-8") as fh:
                fh.write("*.bin binary\n" + older + "*.png -diff\n")
            a.run("commit", "--branch", "session/aa", *CM)
            with open(info, encoding="utf-8") as fh:
                got = fh.read()
            check(got == "*.bin binary\n" + "\n".join([ATTR_BEGIN, *ATTRIBUTES, ATTR_END]) + "\n*.png -diff\n",
                  "an older block is rewritten in place, the user's own lines kept (%r)" % got)
            for path, want in [(FB, "unspecified"), (cost1, "unspecified"), ("dev-workflows-feedback/x.md", "unspecified"),
                               ("dev-workflows-cost/pending-x.md", "unspecified"),
                               ("documentation/acme/dev-workflows/feedback/x.md", "unspecified"),
                               ("specifications/PRD-A-1-x/implementation.md", "unspecified"),
                               ("specifications/PRD-A-1-x/release-notes.md", "unspecified"),
                               ("specifications/PRD-A-1-x/follow-ups.md", "union"),
                               ("specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md", "unset"),
                               ("specifications/PRD-A-1-x/EPIC-A-1-1-y/_security.md", "unspecified"),
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
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", *CM)
            b.add(FB, today("team"))
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("fetch", "-q", "origin")
            a.add(FB, today("a2"))
            got = a.run("commit", "--branch", "session/aa", *CM, env=old)
            check(got.get("committed") and got.get("sync", {}).get("error"),
                  "a commit that lands reports a merge it could not make, rather than exit 2 (%r)" % got)
        # a switch to a deliverable branch cut from an older main, with the overlay present
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.git("branch", "prd/A-1-x")
            b.add(FB, today("team"))
            b.commit_all("team")
            b.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})
            a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            check(subprocess.run(["git", "-C", a.path, "switch", "-q", "prd/A-1-x"], stdout=devnull,
                                 stderr=devnull).returncode != 0, "git refuses the switch over the overlay (the reason for lift)")
            a.run("lift", "--branch", "session/aa")
            a.git("switch", "-q", "prd/A-1-x")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            fb = a.read(FB)
            check(count(fb, today("a1")) == 1 and count(fb, today("team")) == 1,
                  "lift, switch, put-back: nothing lost (%r)" % fb)
        # a working copy that is neither HEAD's nor the branch's is never overwritten
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.git("checkout", "--", FB)
            TYPED = today("typed by hand")
            a.add(FB, TYPED)
            a.write("specifications/PRD-A-1-x/dev-workflows/resume.md", "pos: typed\n")
            got = a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            fb = a.read(FB) or ""
            check(got.get("merged") == [FB] and fb == SEED + "\n" + today("a1") + "\n" + TYPED,
                  "put-back merges a foreign copy of an appended file with the branch's (%r, %r)" % (got, fb))
            check(got.get("skipped") == [], "…and skips none of the appended shapes (%r)" % got)
        # a hand edit after a manual lift never drops what only the branch holds
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            fu = "specifications/PRD-A-1-x/follow-ups.md"
            a.write(fu, "- [ ] one\n")
            a.commit_all("follow-ups on main")
            a.write(fu, "- [ ] two\n", append=True)
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            a.run("lift", "--branch", "session/aa")
            a.write(fu, "- [x] one\n")  # ticked by hand, on HEAD's version
            os.remove(os.path.join(a.path, ".git", "info", "attributes"))  # as on a fresh clone
            got = a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            on_branch = a.git("show", "session/aa:" + fu)
            check("- [x] one" in on_branch and "- [ ] two" in on_branch,
                  "commit unions a hand edit with what only the branch held, losing neither (%r)" % on_branch)
            check(a.read(fu) == on_branch + "\n" and count(a.git("show", "session/aa:" + FB), today("a1")) == 1,
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
            a.add(FB, today("a1"), eol="\r\n")
            a.run("commit", "--branch", "session/aa", "--default-ref", "origin/main", "--message", "A-1 Add session")
            got = a.run("lift", "--branch", "session/aa")
            check(not got.get("unpreserved"), "a CRLF working copy of an LF blob counts as preserved (%r)" % got)
            a.run("put-back", "--branch", "session/aa", "--default-ref", "origin/main")
            check(today("a1").replace("\n", "\r\n") in (a.read(FB) or ""), "put-back writes the smudged, CRLF form")

        # ---- §8's merges keep entries whole: the entry-set rule in commit, sync and put-back ----
        IM = "specifications/PRD-A-1-x/EPIC-A-1-1-y/implementation.md"
        PB = ("put-back", "--branch", "session/aa", "--default-ref", "origin/main")

        def block(sha):
            """A same-day /implement block, differing from IMPL_2P only in its commit: git's union fuses two."""
            return IMPL_2P.replace("7be0d41", sha)

        def push_main(r, message="team"):
            """<r> commits everything and lands it on main, as a merged pull request would."""
            r.commit_all(message)
            r.git("push", "-q", "origin", "main", env={"ALLOW_MAIN": "1"})

        def placed_paths(r):
            with open(os.path.join(r.path, r.git("rev-parse", "--git-path", "session-branch-placed.json")),
                      encoding="utf-8") as fh:
                return set(json.load(fh))

        # two commit calls in a row on one implementation.md
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(IM, IMPL_HEAD + IMPL_1)
            push_main(a, "record")
            a.add(IM, IMPL_2)
            a.run("commit", "--branch", "session/aa", *CM)
            a.add(IM, IMPL_2P)
            got = a.run("commit", "--branch", "session/aa", *CM)
            on = a.git("show", "session/aa:" + IM)
            check(on == (IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P).rstrip("\n") and got.get("unsettled") == [],
                  "two commit calls in a row leave each entry once on the session branch (%r, %r)" % (got, on))
        # a commit after a sync merged a teammate's entry: E1 B1 on the branch, B1 at HEAD; with this
        # worktree's record, and without it (HEAD's version then stands for what it was given)
        for record in ("record", "no record"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                E1, B1, E2 = block("e1e1e1e"), block("b1b1b1b"), block("e2e2e2e")
                a.write(IM, IMPL_HEAD + IMPL_1)
                push_main(a, "record")
                b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                a.add(IM, E1)
                a.run("commit", "--branch", "session/aa", *CM)
                b.add(IM, B1)
                push_main(b)
                a.git("fetch", "-q", "origin")
                a.run("lift", "--branch", "session/aa")
                a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                a.run(*PB)
                merged = IMPL_HEAD + IMPL_1 + "\n" + E1 + "\n" + B1
                check(a.read(IM) == merged and a.git("show", "HEAD:" + IM) == (IMPL_HEAD + IMPL_1 + "\n" + B1).rstrip("\n"),
                      "[%s] the catch-up's sync puts E1 B1 on the branch and in the tree, B1 at HEAD (%r)" % (record, a.read(IM)))
                if record == "no record":
                    os.remove(os.path.join(a.path, a.git("rev-parse", "--git-path", "session-branch-placed.json")))
                a.add(IM, E2)
                got = a.run("commit", "--branch", "session/aa", *CM)
                on = a.git("show", "session/aa:" + IM)
                check(on == (merged + "\n" + E2).rstrip("\n") and got.get("unsettled") == [],
                      "[%s] the next commit adds E2 and doubles nothing (%r, %r)" % (record, got, on))
        # a squash-merged session pull request, then a sync; then a second sync
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            A1, B1, A2, B2, A3 = (block(s) for s in ("a1a1a1a", "b1b1b1b", "a2a2a2a", "b2b2b2b", "a3a3a3a"))
            a.write(IM, IMPL_HEAD + IMPL_1)
            push_main(a, "record")
            a.add(IM, A1)
            a.run("commit", "--branch", "session/aa", *CM)
            a.git("push", "-q", "-u", "origin", "session/aa")
            merge_on_remote(tmp, remote, "session/aa", "squash")
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            b.add(IM, B1)
            push_main(b)
            a.git("fetch", "-q", "origin")
            a.add(IM, A2)
            got = a.run("commit", "--branch", "session/aa", *CM)
            want = IMPL_HEAD + IMPL_1 + "\n" + A1 + "\n" + A2 + "\n" + B1
            on = a.git("show", "session/aa:" + IM)
            check(got["sync"].get("merged") is True and on == want.rstrip("\n"),
                  "a sync after a squash-merged session pull request doubles nothing (%r, %r)" % (got, on))
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            b.add(IM, B2)
            push_main(b)
            a.git("fetch", "-q", "origin")
            a.add(IM, A3)
            got = a.run("commit", "--branch", "session/aa", *CM)
            on = a.git("show", "session/aa:" + IM)
            check(got["sync"].get("merged") is True and on == (want + "\n" + A3 + "\n" + B2).rstrip("\n"),
                  "…and a second sync doubles nothing (%r, %r)" % (got, on))
            check(a.read(IM) == on + "\n", "…the working copy aligned to it")
        # both sides appended to one implementation.md: both entries, not -X ours' version; and
        # Review Focus 5: a repository .gitattributes changes no outcome
        outcomes = {}
        for attrs in (None, "* merge=text\n", "* -merge\n", "* merge=union\n"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                fu = "specifications/PRD-A-1-x/follow-ups.md"
                if attrs:
                    a.write(".gitattributes", attrs)
                a.write(IM, IMPL_HEAD + IMPL_1)
                a.write(fu, "- [ ] one\n")
                push_main(a, "record")
                b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                a.add(IM, IMPL_2)
                a.write(fu, "- [ ] mine\n", append=True)
                a.write(rs, "pos: mine\n")
                a.run("commit", "--branch", "session/aa", *CM)
                b.add(IM, IMPL_2P)
                b.write(fu, "- [ ] team\n", append=True)
                b.write(rs, "pos: team\n")
                push_main(b)
                a.git("fetch", "-q", "origin")
                got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
                outcomes[attrs] = (got.get("merged"), got.get("conflict"), a.git("show", "session/aa:" + IM),
                                   a.git("show", "session/aa:" + fu), a.git("show", "session/aa:" + rs))
        want = (True, [], (IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P).rstrip("\n"),
                "- [ ] one\n- [ ] mine\n- [ ] team", "pos: mine")
        check(outcomes[None] == want,
              "a sync keeps both sides' appended entries and tasks whole, and this run's resume.md (%r)" % (outcomes[None],))
        for attrs, got in outcomes.items():
            check(got == outcomes[None], "a repository .gitattributes of %r changes no outcome (%r)" % (attrs, got))
        # the default side edited an entry both sides hold: no merge commit, the path in conflict
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(IM, IMPL_HEAD + IMPL_1)
            push_main(a, "record")
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            a.add(IM, IMPL_2)
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(IM, IMPL_HEAD + IMPL_1.replace("commit:  a3f91c2", "commit:  a3f91c3"))
            push_main(b)
            a.git("fetch", "-q", "origin")
            tip, before = a.git("rev-parse", "session/aa"), a.read(IM)
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("conflict") == [IM] and got.get("merged") is False and a.git("rev-parse", "session/aa") == tip
                  and a.read(IM) == before, "an edited entry on the default side makes no merge commit (%r)" % got)
            check(got.get("conflicts") == [{"path": IM, "source": "origin/main"}],
                  "…and names the default ref as the source (%r)" % got.get("conflicts"))
        # the same identity on two clones: one removed an entry the other's copy still holds and added
        # to; the merge of origin's copy is refused, and its source is named
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("a1 from clone a"))
            a.run("commit", "--branch", "session/aa", *CM)
            a.git("push", "-q", "-u", "origin", "session/aa")
            b.git("fetch", "-q", "origin")
            mine = SEED[:SEED.index("## ")] + today("b1 from clone b")  # e0, an entry main holds, removed by hand
            b.write(FB, mine)
            got = b.run("commit", "--branch", "session/aa", *CM)
            check(got["sync"].get("conflict") == [FB] and got["sync"].get("merged") is False
                  and got["sync"].get("conflicts") == [{"path": FB, "source": "origin/session/aa"}],
                  "a refused merge of origin's copy of the session branch names that copy as its source (%r)" % got)
            check(b.read(FB) == mine and b.git("show", "session/aa:" + FB) == mine.rstrip("\n"),
                  "…the removal committed as it is and the working copy left as it was (%r)" % b.read(FB))
            check("[rejected]" in b.git("push", "--porcelain", "origin", "session/aa", check=False),
                  "…so the push of the session branch is rejected")
            # §6's remedy: the same removal on the other clone; both then merge and push
            a.write(FB, SEED[:SEED.index("## ")] + today("a1 from clone a"))
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("committed") and got.get("unsettled") == [], "clone a commits the same removal (%r)" % got)
            a.git("push", "-q", "origin", "session/aa")
            b.git("fetch", "-q", "origin")
            got = b.run("commit", "--branch", "session/aa", *CM)
            check(got["sync"].get("merged") is True and got["sync"].get("conflicts") == []
                  and b.git("show", "session/aa:" + FB) == (mine + "\n" + today("a1 from clone a")).rstrip("\n"),
                  "with the same removal on both clones, clone b merges clone a's copy, the entry gone (%r)" % got)
            out = b.git("push", "--porcelain", "origin", "session/aa", check=False)
            check("[rejected]" not in out and b.git("rev-parse", "session/aa")
                  == b.git("ls-remote", "origin", "refs/heads/session/aa").split()[0],
                  "…and its push goes through (%r)" % out)
        # Review Focus 3: implementation-format §1's block move, a removal, is committed as it is where
        # the branch has not moved since this worktree was given its version -- by its record, or after
        # a lift cleared the records -- and left out, in unsettled, where another worktree moved it on
        prd_im = "specifications/PRD-A-1-x/implementation.md"
        PRD_TOP, EPIC_TOP = "# Implementation — A-1 x\n\n", "# Implementation — A-1-1 y\n\n"
        LATER, OTHER = block("1a7e2b0"), block("0712e4d")
        for how in ("record", "lifted", "moved on"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                a.write(prd_im, PRD_TOP + IMPL_1 + "\n" + IMPL_2)  # IMPL_2 is the Epic's, written before 4.1.2
                push_main(a, "record")
                a.add(prd_im, LATER)
                a.run("commit", "--branch", "session/aa", *CM)
                if how == "lifted":
                    a.git("push", "-q", "-u", "origin", "session/aa")
                    merge_on_remote(tmp, remote, "session/aa", "merge")
                    a.git("fetch", "-q", "origin")
                    a.run("lift", "--branch", "session/aa")
                    a.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
                    a.run(*PB)
                    check(prd_im not in placed_paths(a), "[lifted] no record holds the file (%r)" % placed_paths(a))
                elif how == "moved on":
                    w2 = Repo(os.path.join(tmp, "w2"))
                    a.git("worktree", "add", "-q", "-b", "prd/A-1-x", w2.path)
                    w2.run(*PB)
                    w2.add(prd_im, OTHER)
                    w2.run("commit", "--branch", "session/aa", *CM)
                on_before = a.git("show", "session/aa:" + prd_im)
                cut = PRD_TOP + IMPL_1 + "\n" + LATER
                a.write(prd_im, cut)
                a.write(IM, EPIC_TOP + IMPL_2)
                got = a.run("commit", "--branch", "session/aa", *CM)
                if how != "moved on":
                    check(got.get("unsettled") == [] and a.git("show", "session/aa:" + prd_im) == cut.rstrip("\n")
                          and a.git("show", "session/aa:" + IM) == (EPIC_TOP + IMPL_2).rstrip("\n"),
                          "[%s] the block move is committed as it is (%r)" % (how, got))
                else:
                    check(got.get("unsettled") == [prd_im] and got.get("paths") == [IM] and a.read(prd_im) == cut
                          and a.git("show", "session/aa:" + prd_im) == on_before,
                          "[moved on] the move is left out, in unsettled, the working copy untouched (%r)" % got)
                    got = a.run("lift", "--branch", "session/aa")
                    check(got.get("unpreserved") == [prd_im] and a.read(prd_im) == cut,
                          "[moved on] …and lift counts it unpreserved, discarding nothing (%r)" % got)
        # settle_copy: another worktree appended to the branch, this one to its working copy; in LF,
        # and in a CRLF working copy of an LF blob, by eol=crlf and by core.autocrlf=true (Review
        # Focus 2): the three versions are read in working-tree form, so their line endings agree
        for form in ("lf", "eol=crlf", "autocrlf=true"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                eol = "\n" if form == "lf" else "\r\n"
                if form == "eol=crlf":
                    a.write(".gitattributes", "*.md text eol=crlf\n")
                    push_main(a, "crlf")
                elif form == "autocrlf=true":
                    a.git("config", "core.autocrlf", "true")
                if form != "lf":
                    os.remove(os.path.join(a.path, FB))
                    a.git("checkout", "--", FB)  # checked out again, now in CRLF
                    check(a.read(FB) == SEED.replace("\n", "\r\n"), "[%s] the working copy is CRLF" % form)
                A1, W1, A2 = today("a1 mine"), today("w1 from another worktree"), today("a2 mine again")
                a.add(FB, A1, eol=eol)
                a.run("commit", "--branch", "session/aa", *CM)
                w2 = Repo(os.path.join(tmp, "w2"))
                a.git("worktree", "add", "-q", "-b", "prd/A-1-x", w2.path)
                w2.run(*PB)
                w2.add(FB, W1, eol=eol)
                w2.run("commit", "--branch", "session/aa", *CM)
                a.add(FB, A2, eol=eol)
                got = a.run("commit", "--branch", "session/aa", *CM)
                want = SEED + "\n" + A1 + "\n" + W1 + "\n" + A2
                check(got.get("unsettled") == [] and a.read(FB) == want.replace("\n", eol),
                      "[%s] commit settles the working copy with the branch's, in its own line endings (%r, %r)"
                      % (form, got, a.read(FB)))
                stored = subprocess.run(["git", "-C", a.path, "cat-file", "blob", "session/aa:" + FB],
                                        stdout=subprocess.PIPE).stdout.decode("utf-8")
                check(stored == want, "[%s] …and commits both entries as an LF blob (%r)" % (form, stored))
        # put-back over a foreign working copy the entry-set rule refuses: skipped, untouched
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", *CM)
            a.git("checkout", "--", FB)
            edited = SEED.replace("**Friction:** e0 first", "**Friction:** e0 first, reworded") + "\n" + today("typed")
            a.write(FB, edited)
            got = a.run(*PB)
            check(got.get("skipped") == [FB] and got.get("merged") == [] and a.read(FB) == edited,
                  "put-back leaves a foreign copy the entry-set rule refuses as it is, in skipped (%r)" % got)
        # where the branch has not moved, an entry only the session branch held is never lost: a copy
        # restored by hand, then appended to, gets it back; a session-only entry edited by hand keeps
        # its old version beside the edited one, the visible cost of that rule
        for how in ("restored, then appended to", "a session-only entry edited by hand"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                A1, NEW = today("a1 mine"), today("new after the restore")
                a.add(FB, A1)
                a.run("commit", "--branch", "session/aa", *CM)
                if how.startswith("restored"):
                    a.git("checkout", "--", FB)
                    a.add(FB, NEW)
                    want = SEED + "\n" + NEW + "\n" + A1
                else:
                    edited = A1.replace("**Friction:** a1 mine", "**Friction:** a1 mine, corrected")
                    a.write(FB, SEED + "\n" + edited)
                    want = SEED + "\n" + edited + "\n" + A1
                got = a.run("commit", "--branch", "session/aa", *CM)
                check(got.get("unsettled") == [] and a.git("show", "session/aa:" + FB) == want.rstrip("\n")
                      and a.read(FB) == want, "[%s] the branch-only entry is put back after the copy (%r, %r)"
                      % (how, got, a.read(FB)))
        # keep_branch_only itself: nothing missing leaves the copy's bytes; entries HEAD holds stay
        # removed; branch-only ones follow in the given version's order, each once; mixed line endings refuse
        given = IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P
        kbo = keep_branch_only
        check(kbo(b"", given.encode(), given.encode()) == given.encode(),
              "keep_branch_only leaves a copy that holds every entry as it is")
        got = kbo(IMPL_HEAD.encode(), given.encode(), crlf(given + "\n" + B3).encode())
        check(got == crlf(given + "\n" + B3).encode(),
              "…a CRLF copy holding every entry of an LF version too: nothing to put back, no refusal (%r)" % got)
        got = kbo((IMPL_HEAD + IMPL_1).encode(), given.encode(), (IMPL_HEAD + "\n").encode())
        check(got == (IMPL_HEAD + "\n" + IMPL_2 + "\n" + IMPL_2P).encode(),
              "keep_branch_only keeps HEAD's dropped entry removed and puts back the branch-only ones (%r)" % got)
        got = kbo(None, (given + "\n" + IMPL_2).encode(), IMPL_HEAD.encode())
        check(got == (IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P).encode(),
              "…with HEAD lacking the file, each entry once (%r)" % got)
        check(kbo(None, given.encode(), crlf(IMPL_HEAD + IMPL_1).encode()) is None,
              "keep_branch_only refuses versions in different line-ending forms")
        # an assume-unchanged entry is hashed, never taken from the index
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.git("update-index", "--assume-unchanged", FB)
            a.add(FB, today("a1"))
            check(worktree_blob(a.path, FB) != a.git("rev-parse", "HEAD:" + FB),
                  "an assume-unchanged working copy that changed is hashed, not read from the index")
        # LF blobs under core.autocrlf=input, which smudges nothing: an editor saves the copy in CRLF and
        # a run appends; the branch has not moved and nothing needs putting back, so it is committed
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.git("config", "core.autocrlf", "input")
            a.write(IM, IMPL_HEAD + IMPL_1)
            push_main(a, "record")
            a.add(IM, IMPL_2)
            a.run("commit", "--branch", "session/aa", *CM)
            a.write(IM, crlf(IMPL_HEAD + IMPL_1 + "\n" + IMPL_2))
            a.add(IM, IMPL_2P, eol="\r\n")
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("committed") and got.get("unsettled") == []
                  and a.git("show", "session/aa:" + IM) == (IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P).rstrip("\n"),
                  "a CRLF copy of LF blobs, appended to, is committed with every entry (%r)" % got)
            got = a.run("lift", "--branch", "session/aa")
            check(got.get("unpreserved") == [] and IM in got.get("lifted", []), "…and lift then moves on (%r)" % got)
        # follow-ups.md restored by hand, then edited, where the branch has not moved: a session-only
        # task comes back; a HEAD task the copy dropped stays dropped; a ticked HEAD task next to a
        # session-only one the copy dropped comes back beside its open copy, as git's union keeps an
        # adjacent pair; where the copy still holds the session-only task, nothing is put back and
        # the tick is committed as it is
        fu = "specifications/PRD-A-1-x/follow-ups.md"
        for top, edit, want in (
                ("- [ ] zero\n- [ ] one\n- [ ] mid\n", "- [ ] one\n- [ ] mid\n",
                 "- [ ] one\n- [ ] mid\n- [ ] two (session only)"),
                ("- [ ] one\n", "- [x] one\n", "- [ ] one\n- [ ] two (session only)\n- [x] one"),
                ("- [ ] one\n", "- [x] one\n- [ ] two (session only)\n", "- [x] one\n- [ ] two (session only)"),
                ("- [ ] one\n", "- [ ] zero\n- [ ] one",  # its last line's newline stripped: still one task
                 "- [ ] zero\n- [ ] one\n- [ ] two (session only)")):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                a.write(fu, top)
                push_main(a, "follow-ups")
                a.write(fu, "- [ ] two (session only)\n", append=True)
                a.run("commit", "--branch", "session/aa", *CM)
                a.git("checkout", "--", fu)
                a.write(fu, edit)
                got = a.run("commit", "--branch", "session/aa", *CM)
                check(got.get("unsettled") == [] and a.git("show", "session/aa:" + fu) == want and a.read(fu) == want + "\n",
                      "a restored follow-ups.md keeps the session-only task (%r, %r)" % (edit, a.git("show", "session/aa:" + fu)))
        # §6's unsettled remedy: the branch's version dropped an entry of the merge base (a teammate's
        # removal another worktree synced in) that the copy still holds; once the copy is the branch's
        # version with this run's entry after it, the next run commits it
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(IM, IMPL_HEAD + IMPL_1 + "\n" + IMPL_2)
            push_main(a, "record")
            a.add(FB, today("a1"))
            a.run("commit", "--branch", "session/aa", *CM)
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            b.write(IM, IMPL_HEAD + IMPL_1)  # implementation-format §1's move, made on main
            push_main(b, "move")
            a.git("fetch", "-q", "origin")
            w2 = Repo(os.path.join(tmp, "w2"))
            a.git("worktree", "add", "-q", "-b", "prd/A-1-x", w2.path)
            w2.run(*PB)  # merges the move into the session branch
            mine = block("d4d4d4d")
            a.add(IM, mine)
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("unsettled") == [IM], "the copy the move left behind is unsettled (%r)" % got)
            a.write(IM, IMPL_HEAD + IMPL_1 + "\n" + mine)  # the branch's version, this run's entry after it
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("unsettled") == [] and a.git("show", "session/aa:" + IM)
                  == (IMPL_HEAD + IMPL_1 + "\n" + mine).rstrip("\n"), "…and the remedy §6 names commits it (%r)" % got)
        # both sides changed a file identically (here a renormalisation to CRLF): git's merge stands
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, SEED.replace("\n", "\r\n"))
            got = a.run("commit", "--branch", "session/aa", *CM)
            b.write(FB, SEED.replace("\n", "\r\n"))
            push_main(b, "crlf")
            a.git("fetch", "-q", "origin")
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            check(got.get("merged") is True and got.get("conflicts") == [],
                  "an identical change on both sides merges, never refused (%r)" % got)
        # a CRLF blob under core.autocrlf=input: a clean checkout is the index's blob, never a foreign copy
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(FB, SEED.replace("\n", "\r\n"))
            push_main(a, "crlf")  # committed with no autocrlf set: the blob holds CRLF
            a.git("config", "core.autocrlf", "input")
            check(worktree_blob(a.path, FB) == a.git("rev-parse", "HEAD:" + FB),
                  "a clean CRLF checkout under autocrlf=input is the index's blob (%r)" % worktree_blob(a.path, FB))
            a.add(FB, today("a1"), eol="\r\n")
            a.run("commit", "--branch", "session/aa", *CM)
            got = a.run("lift", "--branch", "session/aa")
            check(got.get("lifted") == [FB] and a.git("status", "--porcelain") == "", "…it lifts (%r)" % got)
            got = a.run("commit", "--branch", "session/aa", *CM)
            check(got.get("committed") is None and got.get("unsettled") == [],
                  "…a commit between the lift and its put-back reads the clean checkout as not in place (%r)" % got)
            got = a.run(*PB)
            check(got.get("written") == [FB] and got.get("skipped") == [] and count(a.read(FB).replace("\r\n", "\n"),
                  today("a1")) == 1, "…and put-back writes the branch's version over it (%r)" % got)
        # follow-ups.md of LF blobs under core.autocrlf=input, which smudges nothing, its copy saved in
        # CRLF by an editor: git's union matches lines byte for byte, so each CRLF line would stand
        # beside its LF copy. Where the branch has not moved and no task is missing, the copy is
        # committed as it is (stored in LF); where a task must be put back, where the branch moved on,
        # and in put-back, versions in two line-ending forms refuse, and the copy is left as it is
        for how in ("appended", "dropped a session-only task", "moved on", "put-back"):
            with tempfile.TemporaryDirectory() as tmp:
                remote, a, b = world(tmp)
                a.git("config", "core.autocrlf", "input")
                a.write(fu, "- [ ] one\n")
                push_main(a, "follow-ups")
                a.write(fu, "- [ ] two\n", append=True)
                a.run("commit", "--branch", "session/aa", *CM)
                if how == "moved on":
                    w2 = Repo(os.path.join(tmp, "w2"))
                    a.git("worktree", "add", "-q", "-b", "prd/A-1-x", w2.path)
                    w2.run(*PB)
                    w2.write(fu, "- [ ] w2\n", append=True)
                    w2.run("commit", "--branch", "session/aa", *CM)
                on_before = a.git("show", "session/aa:" + fu)
                copy = ("- [ ] one\r\n- [ ] three\r\n" if how.startswith("dropped")
                        else "- [ ] one\r\n- [ ] two\r\n- [ ] three\r\n")
                a.write(fu, copy)
                if how == "put-back":
                    got = a.run(*PB)
                    check(got.get("skipped") == [fu] and got.get("merged") == [] and a.read(fu) == copy,
                          "[crlf follow-ups, %s] the copy is left as it is, in skipped (%r, %r)" % (how, got, a.read(fu)))
                    continue
                got = a.run("commit", "--branch", "session/aa", *CM)
                on = a.git("show", "session/aa:" + fu)
                if how == "appended":
                    check(got.get("committed") and got.get("unsettled") == [] and a.read(fu) == copy
                          and on == "- [ ] one\n- [ ] two\n- [ ] three",
                          "[crlf follow-ups, %s] committed as it is, each task once (%r, %r)" % (how, got, on))
                    got = a.run("lift", "--branch", "session/aa")
                    check(got.get("unpreserved") == [] and fu in got.get("lifted", []),
                          "[crlf follow-ups, %s] …and lift then moves on (%r)" % (how, got))
                else:
                    check(got.get("unsettled") == [fu] and a.read(fu) == copy and on == on_before,
                          "[crlf follow-ups, %s] left out, in unsettled, the copy untouched (%r, %r)" % (how, got, on))
        # the guard itself: three follow-ups.md versions in two line-ending forms are never united
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            head, given, cr = b"- [ ] one\n", b"- [ ] one\n- [ ] two\n", b"- [ ] one\r\n- [ ] two\r\n- [ ] three\r\n"
            check(settle(tmp, fu, head, given, cr) is None, "settle() refuses follow-ups.md versions in two forms")
            got = union_lines(tmp, fu, None, crlf("- [ ] one\n- [ ] two\n").encode(), cr)
            check(got == cr, "…and unites versions in one form, an absent base aside (%r)" % got)
            klo = keep_branch_only_lines
            check(klo(tmp, fu, head, given, cr) == cr,
                  "keep_branch_only_lines leaves a CRLF copy holding every task of LF versions as it is")
            check(klo(tmp, fu, head, given, b"- [ ] one\r\n- [ ] three\r\n") is None,
                  "…and refuses one that must have a task put back")
            # a version with no line ending at all (an editor that strips the final newline) reads as
            # LF: it unites with LF versions and still refuses beside CRLF ones
            got = union_lines(tmp, fu, b"- [ ] one", given, b"- [ ] one\n- [ ] team\n")
            check(got == b"- [ ] one\n- [ ] two\n- [ ] team\n",
                  "a base with no line ending unites with LF versions (%r)" % got)
            got = settle(tmp, fu, b"- [ ] one", crlf("- [ ] one\n- [ ] two\n").encode(), cr)
            check(got is None, "…and is refused beside CRLF ones (%r)" % got)
        # …and in a sync: main's follow-ups.md held one task with no final newline
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(fu, "- [ ] one")
            push_main(a, "follow-ups")
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            a.write(fu, "- [ ] one\n- [ ] mine\n")
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(fu, "- [ ] one\n- [ ] team\n")
            push_main(b)
            a.git("fetch", "-q", "origin")
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            on = a.git("show", "session/aa:" + fu)
            check(got.get("merged") is True and got.get("conflict") == [] and on == "- [ ] one\n- [ ] mine\n- [ ] team",
                  "a sync settles follow-ups.md whose merge base has no final newline (%r, %r)" % (got, on))
        # a last line with no newline matches its copy on the other sides: union_lines ends each
        # version with a line ending in its own form first, where git's merge-file matches it with
        # neither its LF nor its CRLF copy and keeps it twice
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(["git", "init", "-q", tmp], check=True)
            for form, eol in (("LF", "\n"), ("CRLF", "\r\n")):
                for b_, o_, t_, want in (("p\nx\n", "a\np\nx", "p\nx\nb\n", "a\np\nx\nb\n"),
                                         ("p\nx", "p\na\nx\n", "p\nx\nb\n", "p\na\nx\nb\n")):
                    got = union_lines(tmp, fu, *(s.replace("\n", eol).encode() for s in (b_, o_, t_)))
                    check(got == want.replace("\n", eol).encode(),
                          "[%s] a last line with no newline, in ours or in base, is kept once by union_lines (%r)"
                          % (form, got))
            got = keep_branch_only_lines(tmp, fu, b"- [ ] one\n", b"- [ ] one\n- [ ] two\n", b"- [ ] zero\n- [ ] one")
            check(got == b"- [ ] zero\n- [ ] one\n- [ ] two\n",
                  "keep_branch_only_lines puts a task back after a last line with no newline, each once (%r)" % got)
        with tempfile.TemporaryDirectory() as tmp:
            remote, a, b = world(tmp)
            a.write(fu, "- [ ] one\n")
            push_main(a, "follow-ups")
            b.git("pull", "-q", "--ff-only", "--no-rebase", "origin", "main")
            a.write(fu, "- [ ] zero\n- [ ] one")
            a.run("commit", "--branch", "session/aa", *CM)
            b.write(fu, "- [ ] one\n- [ ] team\n")
            push_main(b)
            a.git("fetch", "-q", "origin")
            got = a.run("sync", "--branch", "session/aa", "--default-ref", "origin/main")
            on = a.git("show", "session/aa:" + fu)
            check(got.get("merged") is True and on == "- [ ] zero\n- [ ] one\n- [ ] team",
                  "a sync keeps a session-side last line with no newline once (%r, %r)" % (got, on))

        # ---- the replay (spec §3.2, §3.3): a run's session-file commits onto a remote that moved on ----
        def guarded(name, fn):
            """Run one replay case; a crash fails that case alone, so the rest still run."""
            try:
                fn()
            except Exception as e:
                check(False, "[replay: %s] crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:300]))

        R_SECF = "specifications/PRD-A-1-x/EPIC-A-1-1-y/_security.md"
        R_FU = "specifications/PRD-A-1-x/follow-ups.md"
        R_RS = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        R_PEND = "dev-workflows-cost/pending-2026-10-28-abcd1234.md"
        R_ACC = "specifications/PRD-A-2-café/dev-workflows/A-2-feedback.md"
        R_DOCS = "documentation/acme-docs/dev-workflows/feedback/2026-10-28.md"
        DOCS_HEAD = "---\ntype: dev-workflows-feedback\nprd: n/a\nslug: 2026-10-28\n---\n\n"
        SLUG = "acme-api"
        REG = "security/%s/" % SLUG
        RUN1 = REG + "runs/0001-20261016T091200Z-0a0a0a0a.json"
        RUN2T = REG + "runs/0002-20261028T110000Z-7e7e7e7e.json"  # a teammate's record
        RUN2M = REG + "runs/0002-20261028T100000Z-3a3a3a3a.json"  # this run's, sorting first
        SCAN2 = REG + "scans/20261028T100000Z-eb694d0/report.md"
        AUTHOR = {"GIT_AUTHOR_NAME": "Zoë Writer", "GIT_AUTHOR_EMAIL": "zoe@example.invalid",
                  "GIT_AUTHOR_DATE": "2026-10-28T09:15:00+05:30"}
        MSG = b"A-1 Add dev-workflows session artifacts (implement %d)\n\n  kept as typed, its trailing spaces too  \n\n"
        STUB = (
            "import json, os, sys\n"
            "a = sys.argv[1:]\n"
            "root, slug = a[a.index('--specs') + 1], a[a.index('--slug') + 1]\n"
            "runs = os.path.join(root, 'security', slug, 'runs')\n"
            "names = sorted(n for n in os.listdir(runs) if n.endswith('.json')) if os.path.isdir(runs) else []\n"
            "for n in names:\n"
            "    with open(os.path.join(runs, n), encoding='utf-8') as fh:\n"
            "        json.load(fh)  # a record with conflict markers fails, as register.py's replay does\n"
            "body = {'register.json': json.dumps({'runs': names}, indent=2, sort_keys=True) + '\\n',\n"
            "        'register.md': '<!-- Generated by the stub. -->\\n\\n# Security register: %s\\n\\n' % slug\n"
            "        + ''.join('- [SEC#%d] %s\\n' % (i + 1, n) for i, n in enumerate(names))}\n"
            "for name, text in body.items():\n"
            "    with open(os.path.join(root, 'security', slug, name), 'w', encoding='utf-8', newline='\\n') as fh:\n"
            "        fh.write(text)\n"
            "print(json.dumps({'rebuilt': slug, 'numbers': {'origin-' + n[:-5]: i + 1 for i, n in enumerate(names)}}))\n")

        def stub_register(paths):
            """What STUB writes and prints for a security/<slug>/ holding these run records."""
            names = sorted(os.path.basename(p) for p in paths)
            return (json.dumps({"runs": names}, indent=2, sort_keys=True) + "\n",
                    "<!-- Generated by the stub. -->\n\n# Security register: %s\n\n" % SLUG
                    + "".join("- [SEC#%d] %s\n" % (i + 1, n) for i, n in enumerate(names)),
                    {"origin-" + n[:-5]: i + 1 for i, n in enumerate(names)})

        def run_record(seq, at, origin):
            return json.dumps({"seq": seq, "at": at, "findings": [{"origin": origin, "status": "open"}]},
                              indent=2, sort_keys=True) + "\n"

        def write_register(r, runs):
            js, md, _ = stub_register(runs)
            r.write(REG + "register.json", js)
            r.write(REG + "register.md", md)

        def rworld(tmp, attrs):
            """A bare origin (no hook) and two clones of a seed holding every session-file shape the
            replay settles, under the repository .gitattributes <attrs>, where one is given."""
            seed = Repo(os.path.join(tmp, "seed"))
            subprocess.run(["git", "init", "-q", "-b", "main", seed.path], check=True)
            seed.configure()
            if attrs:
                seed.write(".gitattributes", attrs)
            seed.write("specifications/PRD-A-1-x/prd.md", "# PRD\n")
            seed.write(FB, SEED)
            seed.write(IM, IMPL_HEAD + IMPL_1)
            seed.write(R_SECF, SEC_HEAD + SEC_1)
            seed.write(R_FU, "- [ ] one\n")
            seed.write(R_RS, "pos: base\n")
            seed.write(R_PEND, COST_HEAD + cost("2026-10-27T08:00:00Z"))
            seed.write(R_ACC, SEED)
            seed.write(RUN1, run_record(1, "2026-10-16T09:12:00Z", "s1:v3:aa"))
            write_register(seed, [RUN1])
            seed.commit_all("base")
            remote = os.path.join(tmp, "remote.git")
            subprocess.run(["git", "clone", "-q", "--bare", seed.path, remote], check=True, stdout=devnull, stderr=devnull)
            clones = []
            for name in ("a", "b"):
                r = Repo(os.path.join(tmp, name))
                subprocess.run(["git", "clone", "-q", remote, r.path], check=True, stdout=devnull, stderr=devnull)
                r.configure()
                clones.append(r)
            stub, failing = os.path.join(tmp, "stub-register.py"), os.path.join(tmp, "failing-register.py")
            with open(stub, "w", encoding="utf-8") as fh:
                fh.write(STUB)
            with open(failing, "w", encoding="utf-8") as fh:
                fh.write(STUB + "sys.exit(3)  # it wrote both files and printed its numbers, then failed\n")
            return clones[0], clones[1], {"stub": stub, "failing": failing, None: None}

        def raw(r, *args):
            return subprocess.run(["git", "-C", r.path, "-c", "core.quotePath=false", *args], stdout=subprocess.PIPE,
                                  stderr=devnull).stdout

        def at(r, commit, path):
            """<path> as <commit> holds it, byte for byte, or None."""
            p = subprocess.run(["git", "-C", r.path, "cat-file", "blob", "%s:%s" % (commit, path)],
                               stdout=subprocess.PIPE, stderr=devnull)
            return p.stdout.decode("utf-8") if p.returncode == 0 else None

        def frozen(r):
            return r.state() + (r.git("for-each-ref"),)

        def replay_run(label, tmp, attrs, team, mine, rebuilds=("stub",)):
            """b lands <team>'s edits on origin's main; a commits each of <mine>'s edits, one commit
            each, as a run commits session files, and fetches. With a staged and further edited file
            and an untracked one of the user's own in a's checkout, a's commits are replayed onto
            origin/main once per entry of <rebuilds> (the stub, a failing script, or None). Checks,
            for every call: nothing in the checkout, the index or any ref moved; each replayed commit
            keeps its author, author date and message byte for byte on the one before it; and the
            replay lands no path the run's commits did not carry but the register's two files."""
            a, b, scripts = rworld(tmp, attrs)
            team(b)
            b.commit_all("team")
            b.git("push", "-q", "origin", "main")
            for i, edit in enumerate(mine):
                edit(a)
                a.git("add", "-A")
                with open(os.path.join(tmp, "msg"), "wb") as fh:
                    fh.write(MSG % (i + 1))
                a.git("commit", "-q", "--cleanup=verbatim", "-F", os.path.join(tmp, "msg"), env=AUTHOR)
            a.git("fetch", "-q", "origin")
            a.write("specifications/PRD-A-1-x/prd.md", "# PRD, staged\n")
            a.git("add", "specifications/PRD-A-1-x/prd.md")
            a.write("specifications/PRD-A-1-x/prd.md", "# PRD, staged, then edited again\n")
            a.write("notes.txt", "the user's own, untracked\n")
            commits = a.git("rev-list", "--reverse", "main", "--not", "origin/main").split()
            onto = a.git("rev-parse", "origin/main")
            carried = set()
            for c in commits:
                carried |= set(nul_list(subprocess.run(["git", "-C", a.path, "diff-tree", "--no-commit-id", "-r", "-z",
                                                        "--name-only", c], stdout=subprocess.PIPE)))
            before = frozen(a)
            results = []
            for rb in rebuilds:
                got = replay_commits(a.path, "refs/remotes/origin/main", commits, scripts[rb])
                check(frozen(a) == before, "[replay: %s, %s] nothing in the checkout, the index or any ref moved" % (label, rb))
                if got.get("refused") is None:
                    kept = [c for c in commits if c not in got.get("dropped", [])]
                    check(len(kept) == len(got.get("replayed", [])),
                          "[replay: %s] one new commit per commit not dropped (%r)" % (label, got))
                    parent = onto
                    for old, new in zip(kept, got.get("replayed", [])):
                        show = ("log", "-1", "--date=raw", "--format=%P%x00%an%x00%ae%x00%ad%x00%B")
                        check(raw(a, *show, new).split(b"\0", 1) == [parent.encode()] + raw(a, *show, old).split(b"\0", 1)[1:],
                              "[replay: %s] %s is replayed on %s with its author, date and message byte for byte (%r)"
                              % (label, old[:7], parent[:7], raw(a, *show, new)))
                        parent = new
                    check(got.get("tip") == parent, "[replay: %s] the tip is the last commit made, or onto (%r)" % (label, got))
                    landed = set(nul_list(subprocess.run(["git", "-C", a.path, "diff", "--name-only", "-z", "--no-renames",
                                                          onto, parent], stdout=subprocess.PIPE)))
                    check(landed <= carried | {REG + "register.json", REG + "register.md"},
                          "[replay: %s] it lands only what the run's commits carried (%r)" % (label, landed - carried))
                results.append(got)
            return a, results

        git_version = re.search(r"(\d+)\.(\d+)", subprocess.run(["git", "--version"], stdout=subprocess.PIPE)
                                .stdout.decode("utf-8", "replace"))
        can_replay = git_version is not None and (int(git_version.group(1)), int(git_version.group(2))) >= (2, 40)

        def replay_ok_cases():
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(["git", "init", "-q", tmp], check=True)
                check(replay_ok(tmp) is can_replay,
                      "replay_ok answers yes exactly where git --version is 2.40 or later (%r, %r)"
                      % (replay_ok(tmp), git_version.group(0) if git_version else None))
                # git 2.40 prints --merge-base <commit>; 2.41 and later --[no-]merge-base (Review Focus 6)
                fake = os.path.join(tmp, "fake")
                os.makedirs(fake)
                path = os.environ.get("PATH", "")
                for line, want in (("    --merge-base <commit>", True), ("    --[no-]merge-base <commit>", True),
                                   ("    --[no-]messages", False)):
                    with open(os.path.join(fake, "git"), "w") as fh:
                        fh.write('#!/bin/sh\nfor x in "$@"; do\n  if [ "$x" = merge-tree ]; then\n    cat <<\'EOF\'\n'
                                 "usage: git merge-tree [--write-tree] [<options>] <branch1> <branch2>\n\n"
                                 "    --write-tree          do a real merge instead of a trivial merge\n"
                                 "%s\nEOF\n    exit 129\n  fi\ndone\nexec \"%s\" \"$@\"\n" % (line, shutil.which("git")))
                    os.chmod(os.path.join(fake, "git"), 0o755)
                    os.environ["PATH"] = fake + os.pathsep + path
                    try:
                        got = replay_ok(tmp)
                    finally:
                        os.environ["PATH"] = path
                    check(got is want, "replay_ok reads %r as %s (%r)" % (line.strip(), want, got))
                # the block: union for follow-ups.md, -merge for the overwritten and register shapes,
                # nothing for a block-shaped file
                block = os.path.join(tmp, "replay-attributes")
                with open(block, "w", encoding="utf-8") as fh:
                    fh.write(REPLAY_BLOCK)
                for p, want in ((R_FU, "union"), (R_RS, "unset"), ("specifications/PRD-A-1-x/pr-draft.md", "unset"),
                                ("specifications/PRD-A-1-x/PRD-A-1-implementation-gaps.md", "unset"),
                                (REG + "register.json", "unset"), (REG + "register.md", "unset"), (IM, "unspecified"),
                                (FB, "unspecified"), (R_SECF, "unspecified"), (R_PEND, "unspecified"),
                                (R_DOCS, "unspecified"), (RUN1, "unspecified")):
                    got = subprocess.run(["git", "-C", tmp, "-c", "core.attributesFile=" + block, "check-attr", "merge",
                                          "--", p], stdout=subprocess.PIPE).stdout.decode("utf-8").strip().rsplit(": ", 1)[-1]
                    check(got == want, "REPLAY_BLOCK gives %s merge: %s, not %s" % (p, want, got))
        guarded("replay_ok and REPLAY_BLOCK", replay_ok_cases)

        def replay_cases(attrs):
            tag = attrs.strip() if attrs else "no .gitattributes"
            with tempfile.TemporaryDirectory() as tmp:
                def where(name):
                    os.makedirs(os.path.join(tmp, name))
                    return os.path.join(tmp, name)

                # two same-day entries in each block-shaped format: both kept, the teammate's first
                def same_day():
                    TEAM_FB, MINE_FB = today("team, same day"), today("mine, same day")

                    def team(r):
                        r.add(IM, IMPL_2)
                        r.add(FB, TEAM_FB)
                        r.add(R_SECF, SEC_2)

                    def mine(r):
                        r.add(IM, IMPL_2P)
                        r.add(FB, MINE_FB)
                        r.add(R_SECF, SEC_3)
                    a, (got,) = replay_run("same day, " + tag, where("same-day"), attrs, team, [mine])
                    tip = got.get("tip")
                    check(got.get("refused") is None and len(got.get("replayed", [])) == 1 and got.get("dropped") == []
                          and at(a, tip, IM) == IMPL_HEAD + IMPL_1 + "\n" + IMPL_2 + "\n" + IMPL_2P
                          and at(a, tip, FB) == SEED + "\n" + TEAM_FB + "\n" + MINE_FB
                          and at(a, tip, R_SECF) == SEC_HEAD + SEC_1 + "\n" + SEC_2 + "\n" + SEC_3,
                          "[replay: same day, %s] implementation.md, feedback and _security.md keep both same-day "
                          "entries, the teammate's first (%r, %r)" % (tag, got, tip and at(a, tip, IM)))
                guarded("same day, " + tag, same_day)

                # a byte-identical append on both sides: the commit is already there, and dropped
                def identical():
                    SAME = today("the same entry, appended on both sides")
                    a, (got,) = replay_run("identical, " + tag, where("identical"), attrs,
                                           lambda r: r.add(FB, SAME), [lambda r: r.add(FB, SAME)])
                    check(got.get("refused") is None and got.get("replayed") == [] and len(got.get("dropped", [])) == 1
                          and got.get("tip") == a.git("rev-parse", "origin/main"),
                          "[replay: identical, %s] a commit whose change origin already holds is dropped (%r)" % (tag, got))
                guarded("identical, " + tag, identical)

                # Review Focus 4: a scan commit whose runs/ and scans/ files (and so its register) origin
                # already holds byte for byte, plus a new entry: replayed, the shared files untouched, and no
                # rebuild needed -- none is handed over
                def shared_scan():
                    def shared(r):
                        r.write(RUN2M, run_record(2, "2026-10-28T10:00:00Z", "s2:v3:bb"))
                        r.write(SCAN2, "# Scan report\n\nOne HIGH finding.\n")
                        write_register(r, [RUN1, RUN2M])

                    def team(r):
                        shared(r)
                        r.add(R_SECF, SEC_2)

                    def mine(r):
                        shared(r)
                        r.add(R_SECF, SEC_3)
                    a, (got,) = replay_run("shared scan, " + tag, where("shared-scan"), attrs, team, [mine], rebuilds=(None,))
                    tip = got.get("tip")
                    check(got.get("refused") is None and len(got.get("replayed", [])) == 1
                          and at(a, tip, R_SECF) == SEC_HEAD + SEC_1 + "\n" + SEC_2 + "\n" + SEC_3
                          and all(a.git("rev-parse", "%s:%s" % (tip, p)) == a.git("rev-parse", "origin/main:" + p)
                                  for p in (RUN2M, SCAN2, REG + "register.json", REG + "register.md")),
                          "[replay: shared scan, %s] files both sides hold alike are kept as they are (%r)" % (tag, got))
                guarded("shared scan, " + tag, shared_scan)

                # an overwritten shape both sides changed: c's version whole, a deletion included
                def resume_both():
                    a, (got,) = replay_run("resume.md, " + tag, where("resume"), attrs,
                                           lambda r: r.write(R_RS, "pos: team\n"), [lambda r: r.write(R_RS, "pos: mine\n")])
                    check(got.get("refused") is None and at(a, got.get("tip"), R_RS) == "pos: mine\n",
                          "[replay: resume.md, %s] both sides changed it: c's version (%r)" % (tag, got))
                guarded("resume.md, " + tag, resume_both)

                def resume_deleted():
                    a, (got,) = replay_run("resume.md deleted, " + tag, where("resume-deleted"), attrs,
                                           lambda r: r.write(R_RS, "pos: team\n"),
                                           [lambda r: os.remove(os.path.join(r.path, R_RS))])
                    check(got.get("refused") is None and len(got.get("replayed", [])) == 1
                          and at(a, got.get("tip"), R_RS) is None,
                          "[replay: resume.md deleted, %s] c's deletion stands over the teammate's change (%r)" % (tag, got))
                guarded("resume.md deleted, " + tag, resume_deleted)

                # follow-ups.md appended on both sides: git's union, onto's lines first
                def follow_ups():
                    a, (got,) = replay_run("follow-ups.md, " + tag, where("follow-ups"), attrs,
                                           lambda r: r.write(R_FU, "- [ ] team\n", append=True),
                                           [lambda r: r.write(R_FU, "- [ ] mine\n", append=True)])
                    check(got.get("refused") is None and at(a, got.get("tip"), R_FU) == "- [ ] one\n- [ ] team\n- [ ] mine\n",
                          "[replay: follow-ups.md, %s] both tasks, onto's first (%r)" % (tag, got))
                guarded("follow-ups.md, " + tag, follow_ups)

                # both sides created the same per-date docs feedback file: one header, both entries
                def add_add():
                    TEAM_D, MINE_D = (e.replace("2026-07-09", "2026-10-28") for e in (FB_1, FB_2))
                    a, (got,) = replay_run("add/add, " + tag, where("add-add"), attrs,
                                           lambda r: r.write(R_DOCS, DOCS_HEAD + TEAM_D),
                                           [lambda r: r.write(R_DOCS, DOCS_HEAD + MINE_D)])
                    check(got.get("refused") is None and at(a, got.get("tip"), R_DOCS) == DOCS_HEAD + TEAM_D + "\n" + MINE_D,
                          "[replay: add/add, %s] a per-date file both sides created merges under one header (%r, %r)"
                          % (tag, got, got.get("tip") and at(a, got.get("tip"), R_DOCS)))
                guarded("add/add, " + tag, add_add)

                # a register both sides changed: rebuilt by the handed-over script over the merged
                # security/<slug>/; without one, or where it fails, refused
                def register():
                    def team(r):
                        r.write(RUN2T, run_record(2, "2026-10-28T11:00:00Z", "s2:v3:tt"))
                        write_register(r, [RUN1, RUN2T])

                    def mine(r):
                        r.write(RUN2M, run_record(2, "2026-10-28T10:00:00Z", "s2:v3:mm"))
                        write_register(r, [RUN1, RUN2M])
                    a, (got, none, failing) = replay_run("register, " + tag, where("register"), attrs, team, [mine],
                                                         rebuilds=("stub", None, "failing"))
                    tip = got.get("tip")
                    js, md, after = stub_register([RUN1, RUN2T, RUN2M])
                    check(got.get("refused") is None and at(a, tip, REG + "register.json") == js
                          and at(a, tip, REG + "register.md") == md and at(a, tip, RUN2T) and at(a, tip, RUN2M),
                          "[replay: register, %s] both records kept, the register the rebuild's (%r)" % (tag, got))
                    want = {"before_remote": {SLUG: stub_register([RUN1, RUN2T])[2]},
                            "before_run": {SLUG: stub_register([RUN1, RUN2M])[2]}, "after": {SLUG: after}}
                    check(got.get("numbers") == want and len({json.dumps(m, sort_keys=True) for m in want.values()}) == 3,
                          "[replay: register, %s] the three numbers maps, from onto, c and the rebuilt tree (%r)"
                          % (tag, got.get("numbers")))
                    for what, res in (("no rebuild script", none), ("a rebuild that fails", failing)):
                        check(res.get("refused") == {"reason": "register-rebuild", "path": REG},
                              "[replay: register, %s] %s refuses, naming the register (%r)" % (tag, what, res))
                guarded("register, " + tag, register)

                # a modify/delete, and a runs/ add/add of different content: refused, the path named
                def modify_delete():
                    a, (got,) = replay_run("modify/delete, " + tag, where("modify-delete"), attrs,
                                           lambda r: os.remove(os.path.join(r.path, R_PEND)),
                                           [lambda r: r.add(R_PEND, cost("2026-10-28T09:00:00Z"))])
                    check(got.get("refused") == {"reason": "conflict", "path": R_PEND},
                          "[replay: modify/delete, %s] a pending cost file the teammate relocated refuses (%r)" % (tag, got))
                guarded("modify/delete, " + tag, modify_delete)

                def runs_add_add():
                    def side(origin):
                        def edit(r):
                            r.write(RUN2M, run_record(2, "2026-10-28T10:00:00Z", origin))
                            write_register(r, [RUN1, RUN2M])
                        return edit
                    a, (got,) = replay_run("runs/ add/add, " + tag, where("runs-add-add"), attrs, side("s2:v3:tt"),
                                           [side("s2:v3:mm")])
                    check(got.get("refused") == {"reason": "conflict", "path": RUN2M},
                          "[replay: runs/ add/add, %s] one record name with two contents refuses (%r)" % (tag, got))
                guarded("runs/ add/add, " + tag, runs_add_add)

                # two local commits onto a remote that appended to the same file: both replayed, nothing doubled
                def two_commits():
                    T, A1, A2 = today("team appended"), today("a1, first local commit"), today("a2, second local commit")
                    a, (got,) = replay_run("two commits, " + tag, where("two-commits"), attrs, lambda r: r.add(FB, T),
                                           [lambda r: r.add(FB, A1), lambda r: r.add(FB, A2)])
                    rep = got.get("replayed", [])
                    check(got.get("refused") is None and len(rep) == 2
                          and at(a, rep[0], FB) == SEED + "\n" + T + "\n" + A1
                          and at(a, rep[1], FB) == SEED + "\n" + T + "\n" + A1 + "\n" + A2,
                          "[replay: two commits, %s] both replayed, each entry once (%r)" % (tag, got))
                guarded("two commits, " + tag, two_commits)

                # a session file whose path holds é is settled, not refused
                def accented():
                    TEAM_A, MINE_A = today("team, café"), today("mine, café")
                    a, (got,) = replay_run("é, " + tag, where("accented"), attrs, lambda r: r.add(R_ACC, TEAM_A),
                                           [lambda r: r.add(R_ACC, MINE_A)])
                    check(got.get("refused") is None and at(a, got.get("tip"), R_ACC) == SEED + "\n" + TEAM_A + "\n" + MINE_A,
                          "[replay: é, %s] a path holding é is settled (%r)" % (tag, got))
                guarded("é, " + tag, accented)

        # Review Focus 5: a repository .gitattributes changes no outcome above
        if can_replay:
            for attrs in (None, "* merge=text\n", "* -merge\n", "security/** export-ignore\n"):
                replay_cases(attrs)

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

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
  specs-git.py declined --command /<name> --path <p> [--path <p>]...
  specs-git.py --specs "<value>" specs-root-check
  specs-git.py --specs "<value>" start --command /<name> [--key <K>]... [--commit-key <K>] [--register-rebuild <path>]
               [--rerun] [--resume] [--budget <seconds>]
  specs-git.py --specs "<value>" end --command /<name> [--commit-key <K>] [--register-rebuild <path>] [--no-preflight]
               [--misrooted-stdin] [--session-branch-created <sha7>] [--declined <p>]... [--resume]
  specs-git.py --specs <root> replay --for start|end --command /<name> --branch <name> [--set-upstream] [--timed-out]
  specs-git.py --specs <root> land --branch <name> --default-ref <ref> --command /<name> [--commit-key <K>]
               [--snapshot <file> | --snapshot -] [--register-rebuild <path>] [--here]
  specs-git.py --specs <root> land --default-ref <ref> --retry-held [--register-rebuild <path>]
  specs-git.py --specs <root> land --default-ref <ref> --drop-held <sha7>
  specs-git.py --specs <root> snapshot
  specs-git.py --selftest

declined appends paths to the run's state record (specs_git_state.py, one file per session and command, outside
every repository), creating the record where the command's start never ran. specs-root-check runs addressing §3's
entry point on SPECS_PATH as set, "" meaning unset. start is specs-repo-git §3's specs-preflight for the run of this
session and command: it prints the Environment: line and what §3.1 reports, opens the run's record, then runs §3.2 to
§3.5 in stages saved in that record -- each resumable from its start -- and prints what each does; a push rejected as
non-fast-forward, and a unit of capped calls its budget would not hold, return next, the replay or start --resume, in
a call of its own. end is specs-repo-git §4's commit-artifacts for the run of this
session and command: it reads that record, catches the default branch up, commits the session files and pushes them,
and prints the §6 outcome line with what follows it, removing the record; or it names the replay a rejected push
needs as next, or stops on an error, and keeps the record for what follows. replay is §4 step 6's replay of a push
rejected as non-fast-forward, in a call of its own: it runs session-branch.py's replay in process and prints the §6
row it gives -- for end, end's object, the record removed; for start, the row in its Specs preflight: form and the
next call. In session-branch mode (specs-repo-git §8) start and end run session-branch.py's commit, lift and put-back
in process: start wraps each move of the checkout in lift and put-back and ends the preflight with put-back, end
commits on the session branch and pushes it, and neither hands out a replay. The state and lines modules load only for
the subcommands that need them, so a copy of this script without them still runs the primitives above.

land is specs-repo-git §4 step 1's landing, and loads both modules: the run's own session-file change -- from the
snapshot its start took (snapshot prints one, the map --snapshot takes) to the working copies now -- committed on the
default branch without moving the checkout, by session-branch.py's move_branch, or by a refspec push where another
worktree has the default branch checked out, then lifted out of the working tree; where --branch is the default
branch, or with --here, committed on HEAD's branch instead, its index restored and no file written. A landing refused
is kept as a held commit under refs/workflows/held/, listed in this worktree's held record (rev-parse --git-path
workflows/held.json), which also journals every landing until its lift; --retry-held lands the held commits again, and
--drop-held <sha7> drops one, its files left as they stand.

<root> is the specs repository's top level (branch-merged and branch-key also accept a directory below it,
where specs-repo-git §3.5 classifies under specs_git: misrooted); the <value> specs-root-check, start and end take is
never checked first, so empty, a file or a subdirectory each reaches it. Nothing here but start, end, replay and land
writes the working tree, the index or a ref. Output is one JSON object on stdout. Exit 0: it ran, whatever it found.
Exit 2: it could not run (usage, not a repository's top level, a ref that does not resolve, an unexpected git failure,
any other exception), printing one "specs-git: not run (...)" line on stderr; the caller reports it
and the run continues. start exits 2 only before it saves its record, its first write; after it, a failure is exit 0
with error set and the pre.stopped line, the record saved at the stage it reached. end exits 2 only before its first
write to the repository; after it, a failure is exit 0
with error set and the end.stopped line, and the record stays for end --resume. replay exits 2 only before it finds
its record; after it, a failure is exit 0 with error set and the stopped line, and the record stays as it stood; a
replay a signal ended prints nothing and ends by that signal, the record as it stood for the --timed-out call. land
exits 2 only before its first write to a ref of its own: any held ref's write or removal, whatever makes it, the move
or push of the default branch, or the update-ref of HEAD's branch. The remote-tracking ref a capped fetch refreshes,
to verify a refspec landing's journal, is not one, and objects written before it do not count. After it, a failure is
exit 0 with error set, --retry-held printing beside it what it had done; where a move was under way, the held record
keeps its journal entry for end --resume or the next preflight's held stage, which finish it only where its move is
verified. snapshot exits 2 only before it prints.
"""

import argparse
import contextlib
import importlib.util
import json
import math
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SPECS_REPO_GIT = os.path.join(HERE, "..", "references", "specs-repo-git.md")
ADDRESSING = os.path.join(HERE, "..", "references", "addressing.md")
SESSION_HYGIENE = os.path.join(HERE, "..", "references", "session-hygiene.md")


def _load_session_branch():
    spec = importlib.util.spec_from_file_location("session_branch", os.path.join(HERE, "session-branch.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    sb = _load_session_branch()
except Exception as e:  # a missing or broken session-branch.py is "not run" on one line, never a traceback
    print("specs-git: not run (session-branch.py could not be loaded: %s)" % " ".join(str(e).split()), file=sys.stderr)
    sys.exit(2)
NotRun = sb.NotRun
_LOADED = {}


def _load_module(name):
    """A sibling module by file name, loaded the first time a subcommand needs it; a failure is NotRun."""
    if name not in _LOADED:
        try:
            spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            raise NotRun("%s could not be loaded: %s" % (name, " ".join(str(e).split())))
        _LOADED[name] = module
    return _LOADED[name]


def _flow():
    """The modules the start/end flow subcommands share: (state, lines) — the run's record and every line it
    prints. Part 1's primitives never call it."""
    return _load_module("specs_git_state"), _load_module("specs_git_lines")


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


def declined(command, paths):
    """The paths the run's user declined to stage, appended (unique, in order) to the record of this session
    and <command>; a record the command's start never made is created, marked as not started by the script.
    A record load() returns None for (another version, or unparsable) is overwritten and reported created: it
    serves no later call."""
    state, _ = _flow()
    if not paths:
        raise NotRun("usage: declined needs at least one --path")
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    session = state.session_id()
    rec = state.load(session, command)
    found = rec is not None
    if rec is None:
        rec = state.new(command, session=session, started_by_script=False)
    added = []
    for p in paths:
        if p not in added:
            added.append(p)
    rec["declined"] = rec["declined"] + [p for p in added if p not in rec["declined"]]
    state.save(session, command, rec)
    return {"recorded": added, "record": "found" if found else "created"}


_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://")
_USER = re.compile(r"^[^/@]+@")


def owner_repo(url, resolve_alias=True, ssh_config=None):
    """phase-handoff §2.6.1's owner-repo: the [HOST/]OWNER/REPO a gh -R call names, from a remote URL.
    The host is kept save github.com; a non-http(s) host other than github.com is resolved through
    ssh -G first, its alias's HostName taken (ssh.github.com is github.com) — skipped where
    <resolve_alias> is false, as specs-repo-git §2.1's <docs-repo-slug> requires. A slug that is not
    OWNER/REPO gives owner_repo null; name is the same derivation unvalidated, null only where the
    slug is empty — specs-repo-git §2.1's <docs-repo-slug> source, which a gh-only check must not
    change. <ssh_config> is passed to ssh as -F (the selftest's)."""
    if not url:
        return {"host": None, "slug": None, "name": None, "owner_repo": None}
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
    # The URL itself is never returned: a remote can carry a credential in its userinfo, which
    # the host and slug expressions strip and an echoed URL would print into the transcript.
    return {"host": host, "slug": slug, "name": value if slug else None,
            "owner_repo": value if re.match(r"^[^/]+/[^/]+$", slug) else None}


def owner_repo_of(repo, resolve_alias=True):
    """owner_repo over <repo>'s origin remote; nulls where it has none."""
    sb.git(repo, "rev-parse", "--git-dir")
    r = sb.git(repo, "remote", "get-url", "origin", check=False)
    return owner_repo(sb.text(r) if r.returncode == 0 else None, resolve_alias)


# session-hygiene §7's The line., character for character; the selftest fails where they differ.
SH7_LINE = r'''printf 'Environment: SPECS_PATH=%s (origin %s), REPOS_PATH=%s\n' \
  "$(if [ -n "${SPECS_PATH-}" ]; then realpath -- "$SPECS_PATH" 2>/dev/null || printf '%s' "$SPECS_PATH"; else printf unset; fi)" \
  "$(if [ -n "${SPECS_PATH-}" ]; then git -C "$SPECS_PATH" remote get-url origin 2>/dev/null || printf none; else printf none; fi)" \
  "${REPOS_PATH-unset}"'''


def env_line(specs):
    """session-hygiene §7's Environment: line, as its Bash call prints it in the run's own shell: SH7_LINE run by
    bash with SPECS_PATH set to <specs>, or removed where <specs> is empty, and every other variable and the
    working directory inherited. The line is returned without its newline."""
    env = dict(os.environ)
    if specs:
        env["SPECS_PATH"] = specs
    else:
        env.pop("SPECS_PATH", None)
    try:
        r = subprocess.run(["bash", "-c", SH7_LINE], env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                           timeout=60)
    except subprocess.TimeoutExpired:
        raise NotRun("the Environment line's Bash call did not finish within 60 s")
    if r.returncode != 0:
        raise NotRun("the Environment line's Bash call failed (exit %d)" % r.returncode)
    out = r.stdout.decode("utf-8", "surrogateescape")
    return out[:-1] if out.endswith("\n") else out


# addressing §2's register of reserved subdirectory names, as a whole-name match; the selftest fails where it
# differs from that list, or from session-branch.py's EXCLUDED, which holds the same names but dev-workflows.
RESERVED = re.compile(r"\A(?:brd|grounding|interview|dev-workflows|design|attachments|revisions"
                      r"|bundle-[0-9]{8}|customer-sent-[0-9]{8}|Doc screenshots)\Z")
FOLDER_KINDS = {"brd": "BRD", "prd": "PRD", "epic": "EPIC"}
_FIELD = re.compile(r"^(key|kind):\s*(.+?)\s*$")


def _frontmatter(path):
    """key: and kind: off the lines between a file's opening --- and the next ---, quotes stripped; {} where the
    file opens no frontmatter, closes none, or cannot be read."""
    found = {}
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            if fh.readline(4096).lstrip("\ufeff").rstrip() != "---":
                return {}
            for line in fh:
                line = line.rstrip("\r\n")
                if line.rstrip() == "---":
                    return found
                m = _FIELD.match(line)
                if m and m.group(1) not in found:
                    value = m.group(2)
                    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                        value = value[1:-1]
                    found[m.group(1)] = value
    except OSError:
        pass
    return {}


def _names(directory):
    """The entries of <directory> in byte-wise order of name; none where it cannot be listed."""
    try:
        return sorted(os.listdir(directory), key=os.fsencode)
    except OSError:
        return []


def _carrier(folder):
    """addressing §4's carrier of <folder>: (kind, key) off the first of its top-level files, in byte-wise order,
    whose frontmatter holds key: and a kind: of brd, prd or epic, else off brd/brd-inventory.md; None where none."""
    candidates = [os.path.join(folder, n) for n in _names(folder) if os.path.isfile(os.path.join(folder, n))]
    for path in candidates + [os.path.join(folder, "brd", "brd-inventory.md")]:
        fm = _frontmatter(path)
        if fm.get("key") and fm.get("kind") in FOLDER_KINDS:
            return fm["kind"], fm["key"]
    return None


def _prefixed(name, key):
    """addressing §4.1's prefix test: <name> begins <KIND>-<key>-, <KIND> one of §2's three, <key> the carrier's.
    The key is the one read off the carrier, so nothing is parsed out of the name."""
    return any(name.startswith("%s-%s-" % (kind, key)) for kind in FOLDER_KINDS.values())


def _git_line(path, *args):
    """One rev-parse answer for <path>, or None where git fails there."""
    r = sb.git(path, "rev-parse", *args, check=False)
    return sb.text(r) if r.returncode == 0 else None


def _same(a, b):
    """test's -ef: the same file, by device and inode; False where either cannot be reached."""
    try:
        return os.path.samefile(a, b)
    except OSError:
        return False


def _strays(specs):
    """(b)'s second half, lazily: each immediate subdirectory of <specs>, in byte-wise order, not a reserved name and
    not resolving inside <specs>/specifications/, whose carrier passes the prefix test by its own name."""
    tree = os.path.join(specs, "specifications")
    tree = os.path.realpath(tree) if os.path.isdir(tree) else None
    for name in _names(specs):
        path = os.path.join(specs, name)
        if not os.path.isdir(path) or RESERVED.match(name):
            continue
        real = os.path.realpath(path)
        if tree and (real == tree or real.startswith(tree.rstrip(os.sep) + os.sep)):
            continue
        carrier = _carrier(path)
        if carrier and _prefixed(name, carrier[1]):
            yield name


def _walk(specs):
    """addressing §3's value to set: from the physical <specs> up at most three levels, the first D whose
    D/../specifications is D and whose top level git prints, the same as D/..'s; the physical D/.., or None."""
    d = os.path.realpath(specs)
    for _ in range(4):
        up = os.path.join(d, "..")
        if _same(os.path.join(up, "specifications"), d):
            top = _git_line(d, "--show-toplevel")
            if top is not None and top == _git_line(up, "--show-toplevel"):
                return os.path.realpath(up)
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return None


def _left_behind(lines, specs, walk, two_readings):
    """addressing §3's left-behind line for <specs>: the folders of a nested specifications/, then whichever of
    dev-workflows-feedback/, dev-workflows-cost/ and documentation/<slug>/dev-workflows/ exist; None where none."""
    nested = os.path.join(specs, "specifications")
    folders = [n for n in _names(nested) if os.path.isdir(os.path.join(nested, n))] if os.path.isdir(nested) else None
    dirs = [d for d in ("dev-workflows-feedback", "dev-workflows-cost") if os.path.isdir(os.path.join(specs, d))]
    docs = os.path.join(specs, "documentation")
    dirs += ["documentation/%s/dev-workflows" % slug for slug in _names(docs)
             if os.path.isdir(os.path.join(docs, slug, "dev-workflows"))]
    return lines.left_behind({"<value>": specs, "<the value the walk found>": walk}, folders, dirs, two_readings)


def specs_root_check(specs):
    """addressing §3's specs-root-check on <specs>, SPECS_PATH as set (empty: unset, which tests nothing).

    signal: the first that holds of (a)'s two tests — a-prefix (--show-prefix begins specifications/), a-ef
    (<specs>/../specifications is <specs>, which is no work tree's top level) — then (b)'s two halves — b-self
    (<specs>, by its physical name, is a carrier-bearing folder that passes the prefix test), b-sub (an immediate
    subdirectory is). form: one-line where the walk found a value or any signal but b-sub held; else stray where
    --show-prefix succeeds and is empty or <specs>/specifications/ exists; else two-readings. value: the value the
    walk found. subdirs: the subdirectories the stop names — the first that qualifies, every one in the stray
    form; [] where b-sub did not fire. lines: the stop, then the left-behind line where one applies (never in the
    stray form); [] where no signal holds."""
    result = {"signal": None, "form": None, "value": None, "subdirs": [], "lines": []}
    if not specs or not os.path.isdir(specs):
        return result
    prefix = _git_line(specs, "--show-prefix")
    key = first = None
    strays = _strays(specs)
    if prefix is not None and prefix.startswith("specifications/"):
        signal, choice = "a-prefix", 0 if prefix == "specifications/" else 1
    elif _same(os.path.join(specs, "..", "specifications"), specs) and prefix != "":
        signal, choice = "a-ef", 0
    else:
        carrier = _carrier(specs)
        if carrier and _prefixed(os.path.basename(os.path.realpath(specs)), carrier[1]):
            signal, choice, key = "b-self", 2, carrier[1]
        else:
            first = next(strays, None)
            if first is None:
                return result
            signal, choice = "b-sub", 3
    lines = _load_module("specs_git_lines")
    walk = _walk(specs)
    if walk is not None or signal != "b-sub":
        form = "one-line"
    elif prefix is not None and (prefix == "" or os.path.isdir(os.path.join(specs, "specifications"))):
        form = "stray"
    else:
        form = "two-readings"
    subdirs = [first] if first else []
    top = _git_line(specs, "--show-toplevel") if prefix else None
    if form == "one-line":
        walk_top = _git_line(walk, "--show-toplevel") if walk is not None and _git_line(walk, "--show-prefix") else None
        line = lines.fill("root.one-line", {
            "<value>": specs, lines.placeholder("root.one-line", "<is itself"): choice, "<key>": key,
            "<subdirectory>": first, "<the value the walk found>": walk,
            lines.placeholder("root.one-line", "<the value the walk found |"): 0 if walk is not None else 1,
            "<that repository's top level>": walk_top})
    elif form == "stray":
        subdirs += list(strays)
        line = lines.fill("root.stray", {
            "<value>": specs, lines.placeholder("root.stray", "<the top level"): 0 if prefix == "" else 1,
            "<subdirectory>": subdirs, "<that repository's top level>": top})
    else:
        in_repo = prefix is not None
        line = lines.fill("root.two-readings", {
            "<value>": specs, "<subdirectory>": first,
            lines.placeholder("root.two-readings", "<move them"): 0 if in_repo else 1,
            "<the parent of <value>>": os.path.dirname(os.path.realpath(specs)) if in_repo else None,
            lines.placeholder("root.two-readings", "<, and make"): 1 if in_repo else 0,
            "<that repository's top level>": top})
    out = [line]
    if form != "stray":
        behind = _left_behind(lines, specs, walk, form == "two-readings")
        if behind:
            out.append(behind)
    return {"signal": signal, "form": form, "value": walk, "subdirs": subdirs, "lines": out}


def gate(specs, notices=True):
    """specs-repo-git §3.1's gate on <specs>, SPECS_PATH as set (empty: unset). state: unset; not-a-repo (not a
    directory, or rev-parse --git-dir fails there); read-only (its git directory is not writable); or pass. top and
    git_dir where git gives them. With <notices>, also the lines §3.1 prints and whether they set misrooted: on a
    non-repository path its notice — on the same line as specs-root-check's stop where that finds a signal in a
    directory, its left-behind line after — and where the gate passes, specs-root-check's lines, else the
    below-top-level notice where --show-prefix is not empty. With notices off, state, top and git_dir alone."""
    out = {"state": "unset", "top": None, "git_dir": None}
    found = []
    misrooted = False
    if specs:
        r = sb.git(specs, "rev-parse", "--git-dir", check=False) if os.path.isdir(specs) else None
        if r is None or r.returncode != 0:
            out["state"] = "not-a-repo"
        else:
            out["git_dir"] = os.path.realpath(os.path.join(specs, sb.text(r)))
            out["top"] = _git_line(specs, "--show-toplevel")
            out["state"] = "pass" if os.access(out["git_dir"], os.W_OK) else "read-only"
    if not notices:
        return out
    if out["state"] == "not-a-repo":
        lines = _load_module("specs_git_lines")
        notice = lines.fill("pre.nonrepo", {"<value>": specs,
                                            lines.placeholder("pre.nonrepo", "<is not"): 0 if r is None else 1})
        root = specs_root_check(specs) if r is not None else {"lines": []}
        if root["lines"]:
            misrooted = True
            found = [notice + " " + root["lines"][0]] + root["lines"][1:]
        else:
            found = [notice]
    elif out["state"] == "pass":
        found = specs_root_check(specs)["lines"]
        misrooted = bool(found)
        if not found and _git_line(specs, "--show-prefix"):
            lines = _load_module("specs_git_lines")
            found = [lines.fill("pre.below-top", {"<value>": specs, "<top>": out["top"]})]
            misrooted = True
    return dict(out, misrooted=misrooted, lines=found)


# workflows-core:addressing §1's key grammar, ^[A-Z][A-Z0-9_]*(-\d+)+$, its \d spelt [0-9] (Python's \d takes any
# Unicode digit) and matched whole with fullmatch, so a trailing newline never passes; the selftest pins it to §1.
KEY_RE = re.compile(r"[A-Z][A-Z0-9_]*(-[0-9]+)+")
SHA_RE = re.compile(r"[0-9a-f]{4,40}")
# specs-repo-git §4 step 6: a reason after [remote rejected] that begins with one of these is a push a concurrent
# update or a server fault broke, which failed and is retried; every other reason is a refusal.
TRANSIENT = ("failed to update ref", "failed to lock", "cannot lock ref", "unpacker error", "missing necessary objects")
# The --porcelain flags of a ref origin now holds the commit on: fast-forward, forced, new, and [up to date] -- the
# last where an earlier call's push landed before the harness cut that call short.
PUSHED_FLAGS = (" ", "+", "*", "=")
CAP = 60  # seconds: the cap on a fetch, a pull and a push (sb.git_bounded, workflows-core:bounded-run's mechanism)
LS_REMOTE_CAP = 30
REPLAY_TIMEOUT_MS = 420000  # specs-repo-git §4 step 6: the replay's own Bash call
START_TIMEOUT_MS = 600000  # the Bash call the skill runs start and end in


def _first_line(r, error=False):
    """The first non-empty line of a git call's stderr, else of its stdout; else how it exited. With <error>, the first
    that opens fatal: or error: where one does, so a pull's or a push's progress lines never stand for its error."""
    found = [line.strip() for stream in (r.stderr, r.stdout)
             for line in (stream or b"").decode("utf-8", "replace").splitlines() if line.strip()]
    if error:
        found = [line for line in found if line.startswith(("fatal:", "error:"))] or found
    return found[0] if found else "git exited %d" % r.returncode


def _head_branch(root):
    """The branch HEAD stands on, or None on a detached HEAD."""
    r = sb.git(root, "symbolic-ref", "--short", "-q", "HEAD", check=False)
    return (sb.text(r) or None) if r.returncode == 0 else None


def _today():
    """<YYYY-MM-DD> in a remedy: today's UTC date."""
    return time.strftime("%Y-%m-%d", time.gmtime())


def _swap(text, old, new):
    """<text> with its one <old> replaced by <new>: how a renderer puts a template's variant in (specs_git_lines'
    comments name each); ValueError where <old> is not there, so a reworded template never renders unchanged."""
    if text.count(old) != 1:
        raise ValueError("render: %r is not once in %r" % (old, text[:80]))
    return text.replace(old, new)


def resolve_default(root, fetch):
    """specs-repo-git §3.2: the default branch's name, the ref that represents it, and whether a fetch freshened it.
    The name is the one origin/HEAD names, where origin/<name> resolves; else main, then master, where either is a
    local or an origin branch; else the branch HEAD stands on (None on a detached HEAD). <default-ref> is
    origin/<default> where `remote get-url origin` prints a URL, else refs/heads/<default>. With <fetch>, where that
    remote exists, origin's <default> is fetched, capped at 60 s; offline where the fetch fails."""
    name = None
    r = sb.git(root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD", check=False)
    named = sb.text(r) if r.returncode == 0 else ""
    if named.startswith("refs/remotes/origin/") and sb.rev(root, "origin/" + named[len("refs/remotes/origin/"):]):
        name = named[len("refs/remotes/origin/"):]
    for candidate in ("main", "master"):
        if name is None and (sb.rev(root, "refs/heads/" + candidate) or sb.rev(root, "refs/remotes/origin/" + candidate)):
            name = candidate
    if name is None:
        name = _head_branch(root)
    url = sb.git(root, "remote", "get-url", "origin", check=False)
    remote = "origin" if url.returncode == 0 and sb.text(url) else "none"
    ref = None if name is None else ("origin/" + name if remote == "origin" else "refs/heads/" + name)
    offline = False
    if fetch and remote == "origin" and name is not None:
        offline = sb.git_bounded(root, CAP, "fetch", "origin", name).returncode != 0
    return {"default": name, "default_ref": ref, "remote": remote, "offline": offline}


SB_SCRIPT = os.path.join(HERE, "session-branch.py")  # <the script's path> in specs-repo-git §6's session-branch remedies
SG_SCRIPT = os.path.abspath(__file__)  # <specs-git.py's path> in the held lines' --drop-held command (§3.2, §6)
# A stay's kind (specs-repo-git §4 step 1's landing), the first that holds: mid-run, one kept while another run of the
# session was open there (§3.5), whatever else stayed it; else merged, one branch-merged reads merged (B2's); else
# unkeyed, a branch no key of the run names (B4's). The tuple is in the order of the <which no key of this run names |
# which is merged into <default> | where <command>'s run ...> alternation of g1.landing.not_done, app.landed,
# row.held and row.held-stuck, which is not that precedence.
STAY_KINDS = ("unkeyed", "merged", "mid-run")
# Why the preflight stayed on a branch it would have left (§4 step 1): §3.3 G1, a status that could not run (§2.1),
# a switch git refused (§3.4's merged-branch leave, §3.5's B2 or B4), an early stop before the switch (§1 rule 5),
# another run of the session open on the branch (§3.5).
STAY_REASONS = ("g1", "unlisted", "refused", "stopped", "mid-run")
# The landing's refusal codes -- own_change's and land's own -- each mapped to its reason clause (specs-repo-git §6,
# the landing's reason clause); locked reuses the replay's reason.locked, which names no replay (P15). land's own
# locked status, an index.lock, takes the Locked row in the here form, and on an end --resume whose landing journal is
# left for a later call: a fresh landing that finds one at its start holds the change for reason locked, a cause that
# passes (specs-repo-git §4 step 1 (2)), and end prints the held row with reason.locked. unfinished is an end
# --resume's here-form journal that could not be finished (§4 step 1's here form): on the mid-run row only where HEAD
# still stands on the journal's branch and the open run still stands there; elsewhere the end goes on from step 1 on
# HEAD's branch.
LAND_REASONS = {
    "dropped": "reason.land.dropped", "edited": "reason.land.edited", "forms": "reason.land.forms",
    "deleted": "reason.land.deleted", "folder-gone": "reason.land.folder-gone",
    "register-rebuild": "reason.land.register", "moved": "reason.land.moved",
    "checked-out": "reason.land.checked-out", "locked": "reason.locked", "unfinished": "reason.land.unfinished",
}
# The codes of a held change whose cause will not pass (P22): own_change's. checked-out is permanent only by its
# detail, where the refspec push has nowhere to go (PERMANENT_ROWS); moved and locked pass. unfinished is no held
# change's: its journal entry is dropped and no run retries it, so, like every refusal of the here form, it is marked
# permanent (specs-repo-git §6), outside this set.
LAND_PERMANENT = frozenset({"dropped", "edited", "forms", "deleted", "folder-gone", "register-rebuild"})


# The detail of a refusal on the landing's remote path (ruling C2's refspec push), a JSON object the held record keeps:
# outcome, the refspec push's (failed, rejected, refused), push_check's row (no-remote, elsewhere, remote-deleted,
# refused-before), or origin-lacks, where <default-ref> names no commit, so there is nothing the push could name alone
# to build on (specs-repo-git §4 step 1 (3)); text, the push's reason for failed and rejected, origin's refusal for refused; remote, the remote
# the user's configuration pushes <default> to, for elsewhere; record and date, the push-refusal record -- the one push
# wrote for refused (None where it could write none), and for refused-before the one that stood, with the date it holds
# (specs-repo-git §1 rule 8: the record holds a date, never the refusal's text); record_error, for refused where push
# could write the record neither way, the configuration write's error. Every key is there, None where unused.
CHECKED_OUT_DETAIL = ("outcome", "text", "remote", "record", "date", "record_error")
# reason.land.checked-out's alternative by the detail's outcome. rejected -- origin's <default> moved on between the
# build on <default-ref> and the push -- is a refspec push that failed, its reason git's [rejected] summary: nothing
# was pushed, and the next run builds on the newer <default-ref> and pushes again. refused-before is worded as §6's
# refused-before row words it, from the record's date and path; a refused push with no record takes the unrecorded
# form, CHECKED_OUT_UNRECORDED, as §6's push-refused row does, since nothing turns session-branch mode on.
# remote-deleted and origin-lacks share the fourth, origin has no <default>, true whether origin never had it or no
# longer has it.
CHECKED_OUT_ALTERNATIVE = {"failed": 0, "rejected": 0, "no-remote": 1, "elsewhere": 2, "remote-deleted": 3,
                           "origin-lacks": 3, "refused": 4, "refused-before": 5}
CHECKED_OUT_UNRECORDED = 6


def _checked_out_detail(outcome, **values):
    return dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome=outcome, **values)


def _push_detail(pushed):
    """CHECKED_OUT_DETAIL for a refspec push (push(..., src=)) that did not push: failed or rejected with push's reason
    -- the status line's summary, git's first error line, or the capped push's words -- and, where it gave none, the
    words app.why.failed.none gives a status line with none (specs-repo-git §6); refused with origin's refusal, or git's
    own [remote rejected] where it gave none, and the record push wrote, or, where it could write none, the
    configuration write's error. No text is ever empty, so no clause prints an empty ()."""
    outcome, text = pushed["outcome"], pushed.get("reason") or None
    if outcome in ("failed", "rejected") and text is None:
        text = _load_module("specs_git_lines").T["app.why.failed.none"]
    if outcome != "refused":
        return _checked_out_detail(outcome, text=text)
    return _checked_out_detail(outcome, text=text or "[remote rejected]", record=pushed.get("record") or None,
                               record_error=None if pushed.get("record") else pushed.get("record_error"))


def _row_detail(checked):
    """CHECKED_OUT_DETAIL for push_check's row <checked> that left the refspec push nowhere to go, or no push to make:
    elsewhere with the remote it names, refused-before with the record that stood and its date."""
    row = checked["row"]
    if row == "elsewhere":
        return _checked_out_detail(row, remote=checked.get("remote"))
    if row == "refused-before":
        return _checked_out_detail(row, record=checked.get("record"), date=checked.get("date"))
    return _checked_out_detail(row)



def mode_takes(refused):
    """Whether session-branch mode takes a held change's files from the next run on (specs-repo-git §6, the held row,
    and §3.2's could-not-commit line): its refusal is checked-out with checked_out_values' fifth or sixth alternative --
    a refusal origin made and §4 step 6 recorded, or one already recorded -- so the next run's held stage drops the hold
    (P9) and §8.2's commit takes the files, and the line's tail says so in place of the next run's retry."""
    if not isinstance(refused, dict) or refused.get("reason") != "checked-out":
        return False
    detail = refused.get("detail")
    return (isinstance(detail, dict) and detail.get("outcome") in ("refused", "refused-before")
            and bool(detail.get("record")))

def checked_out_values(lines, detail):
    """reason.land.checked-out's values for a refusal's CHECKED_OUT_DETAIL <detail>, to fill beside <path> (the
    refusal's path, the worktree that has <default> checked out) and <default>: the alternation's index by its outcome
    (CHECKED_OUT_ALTERNATIVE) -- a refused one with no record taking CHECKED_OUT_UNRECORDED -- with <reason> and <the
    refusal> from its text, <remote> from its remote, <date> and <record> from the record's, <error> from its
    record_error. Never raises: None where <detail> is not such an object (no push was tried, or an entry held before
    it was)."""
    if not isinstance(detail, dict) or detail.get("outcome") not in CHECKED_OUT_ALTERNATIVE:
        return None
    k = CHECKED_OUT_ALTERNATIVE[detail["outcome"]]
    if detail["outcome"] == "refused" and not detail.get("record"):
        k = CHECKED_OUT_UNRECORDED
    return {lines.placeholder("reason.land.checked-out", "<the push of"): k,
            "<reason>": detail.get("text"), "<remote>": detail.get("remote"), "<the refusal>": detail.get("text"),
            "<date>": detail.get("date"), "<record>": detail.get("record"), "<error>": detail.get("record_error")}


def _identity(session_branch):
    """<identity> in session/<identity>: the session branch's name past its session/ prefix."""
    if session_branch and session_branch.startswith("session/"):
        return session_branch[len("session/"):]
    return session_branch


class _Session:
    """specs-repo-git §8's calls for one start or end call in session-branch mode, on the checkout <specs> and its
    session branch <branch>. Each session-branch.py entry point runs in process, and one that raises is what that
    script's exit 2 would be: (None, the one line its CLI prints on stderr). <report> takes that line where a lift or a
    put-back could not run, which the step reports while the run goes on (§8's opening); <created> takes <base short
    sha> where a commit made here created the session branch -- a creation by any call but §3.4's flush, which reports
    its own (§8.2). <message> is §4 step 4's. commits: every sb.commit result this object made, in order.
    before_commit: called, where set, just before each sb.commit -- end's, which saves the pending end_commit."""

    def __init__(self, lines, specs, branch, default, default_ref, message, report, created):
        self.lines, self.specs, self.branch, self.default, self.default_ref = lines, specs, branch, default, default_ref
        self.message, self.report, self.created, self.commits = message, report, created, []
        self.before_commit = None

    def call(self, fn, *args):
        try:
            return fn(*args), None
        except Exception as e:  # session-branch.py's main() prints any exception as its one not-run line
            return None, _sb_stderr(e)

    def base(self):
        """<base short sha>: the first seven characters of merge-base HEAD <default-ref>, the commit §8.2 step 1 created
        the branch at -- <default-ref>'s own where they share none, as session-branch.py's create_at takes it."""
        r = sb.git(self.specs, "merge-base", "HEAD", self.default_ref, check=False)
        return ((sb.text(r) if r.returncode == 0 else "") or sb.rev(self.specs, self.default_ref) or "")[:7]

    def commit(self, carry=True):
        """§8.2's commit with §4 step 4's message, --include-ahead where HEAD is the default branch: (its result, None),
        its base set where it created the session branch -- read at once -- and passed to <created> where <carry>;
        (None, the stderr line) where it could not run."""
        include = _head_branch(self.specs) == self.default
        if self.before_commit:
            self.before_commit()
        got, err = self.call(sb.commit, self.specs, self.branch, self.default_ref, self.message, include)
        if got is None:
            return None, err
        if got.get("created"):
            got["base"] = self.base()
            if carry:
                self.created(got["base"])
        self.commits.append(got)
        return got, None

    def put_back(self):
        _, err = self.call(sb.put_back, self.specs, self.branch, self.default_ref)
        if err is not None:
            self.report(err)

    def wrap(self, move):
        """§8.3 around <move>, one move of the checkout: lift; where it prints unpreserved, the commit, then lift again,
        a second unpreserved skipping the move -- (False, text.lift-unpreserved, which the step reports in place of
        git's first error line), nothing lifted and so nothing put back; otherwise the move, then put-back, which runs
        whether the move succeeded, failed or raised -- (True, <move>()'s result). A lift that could not run is reported
        and the move goes on unwrapped, put back after it all the same. The caller checks its budget before this, so
        no budget stop falls between a lift and its put-back."""
        lifted, err = self.call(sb.lift, self.specs, self.branch)
        if lifted is not None and lifted.get("unpreserved"):
            got, cerr = self.commit()
            if got is None:
                self.report(cerr)
            lifted, err = self.call(sb.lift, self.specs, self.branch)
            if lifted is not None and lifted.get("unpreserved"):
                return False, self.lines.fill("text.lift-unpreserved", {"<path>": lifted["unpreserved"],
                                                                        "<identity>": _identity(self.branch)})
        if lifted is None:
            self.report(err)
        try:
            return True, move()
        finally:
            self.put_back()


def catch_up(root, default, default_ref, on_write=None, wrap=None):
    """specs-repo-git §3.4's catch-up, which §4 step 2 runs again: where HEAD is on <default>, <default_ref> is
    origin/<default> and HEAD is strictly behind it, `pull --ff-only --no-rebase origin <default>`, capped at 60 s.
    None where it had nothing to do or succeeded; otherwise its pre.pull-failed line, git's first error line in its
    parenthesis, or the capped pull's words. <on_write> is called just before the pull, the call's first write. <wrap>,
    in session-branch mode with a session branch, is _Session.wrap: the pull runs inside lift and put-back (§8.3),
    after <on_write>, so a budget check there comes before the lift; where a second unpreserved skips the pull, the
    pre.pull-failed line names why in place of git's first error line."""
    if default is None or default_ref != "origin/" + default or _head_branch(root) != default:
        return None
    if sb.git(root, "merge-base", "--is-ancestor", "HEAD", default_ref, check=False).returncode != 0:
        return None
    if sb.rev(root, "HEAD") == sb.rev(root, default_ref):
        return None
    if on_write:
        on_write()
    if wrap is None:
        return _pull_line(root, default)
    done, got = wrap(lambda: _pull_line(root, default))
    if done:
        return got
    return _load_module("specs_git_lines").fill("pre.pull-failed", {"<default>": default, "<git's first error line>": got})


def _pull_line(root, default):
    """`pull --ff-only --no-rebase origin <default>`, capped at 60 s, standing on <default>: None where it succeeded,
    else its pre.pull-failed line -- git's first error line in its parenthesis, or the capped pull's words. The pull
    the catch-up makes, and B2's and B4's after their switch (specs-repo-git §3.5)."""
    p = sb.git_bounded(root, CAP, "pull", "--ff-only", "--no-rebase", "origin", default)
    if p.returncode == 0:
        return None
    lines = _load_module("specs_git_lines")
    why = lines.T["text.pull-capped"] if p.returncode == 124 else _first_line(p, error=True)
    return lines.fill("pre.pull-failed", {"<default>": default, "<git's first error line>": why})


def _literal(paths):
    return [":(literal)" + p for p in paths]


def session_subject(key, command):
    """specs-repo-git §4 step 4's message, which §3.4's flush takes too: `<KEY|NOISSUE> Add dev-workflows session
    artifacts (<command>)`, NOISSUE where the run holds no key."""
    return "%s Add dev-workflows session artifacts (%s)" % (key or "NOISSUE", command)


def commit_session_files(root, message, on_write=None, on_staged=None):
    """specs-repo-git §2.1 steps 1-3 and §4 step 4: stage the ARTIFACT paths status() lists, then commit, by pathspec,
    those git still lists as staged, and bring the index back in step with the new HEAD where a pre-commit hook
    changed what the commit carries, leaving a change somebody else had staged as they staged it. locked where
    index.lock exists, tested before staging; failed where git or a hook refuses (error: the first line of git's error
    or the hook's output). paths: what the commit carries; hook_paths: those of them its pathspecs did not name.
    <on_write> is called just before `git add`, the call's first write; <on_staged>, just before `git commit`, with
    {path: the blob the index holds for it, or None for a staged removal} over the paths the commit is about to name."""
    out = {"status": "nothing", "sha": None, "paths": [], "hook_paths": [], "error": None}
    lock = os.path.join(root, sb.text(sb.git(root, "rev-parse", "--git-path", "index.lock")))
    if os.path.lexists(lock):
        return dict(out, status="locked")
    paths = status(root)["artifact"]
    if not paths:
        return out
    if on_write:
        on_write()
    r = sb.git(root, "add", "-A", "--", *_literal(paths), check=False)
    if r.returncode != 0:
        return dict(out, status="locked") if os.path.lexists(lock) else dict(out, status="failed", error=_first_line(r))
    listed = sb.nul_list(sb.git(root, "diff", "--cached", "--name-only", "-z", "--no-renames", "--", *_literal(paths)))
    if not listed:
        return out
    before = sb.nul_list(sb.git(root, "diff", "--cached", "--name-only", "-z", "--no-renames"))
    if on_staged:
        index = {}
        for entry in sb.nul_list(sb.git(root, "ls-files", "-s", "-z", "--", *_literal(listed))):
            meta, _, path = entry.partition("\t")
            index[path] = meta.split()[1]
        on_staged({p: index.get(p) for p in listed})
    r = sb.git(root, "commit", "-q", "-m", message, "--", *_literal(listed), check=False)
    if r.returncode != 0:
        return dict(out, status="failed", error=_first_line(r))
    sha = sb.text(sb.git(root, "rev-parse", "HEAD"))
    carried = _commit_paths(root, "HEAD")
    differ = set(sb.nul_list(sb.git(root, "diff", "--cached", "--name-only", "-z", "--no-renames")))
    theirs = set(before) - set(listed)
    restore = [p for p in carried if p in differ and p not in theirs]
    if restore:
        sb.git(root, "restore", "--staged", "--", *_literal(restore))
    return dict(out, status="committed", sha=sha, paths=carried, hook_paths=[p for p in carried if p not in set(listed)])


def push_check(root, branch, default, session_branch=None, measure=None, default_ref=None):
    """specs-repo-git §4 step 5's three conditions, in its order, before a push of <branch>: row None where all hold,
    else the §6 row of the first that fails -- not-ours (neither the default branch, nor a plugin branch, nor the
    session branch); no-remote; the four states that leave nowhere to push, elsewhere (remote: where the user's
    configuration pushes it), remote-deleted (ls-remote, 30 s, exits 2 for a branch read as pushed), refused-before
    (record and record_kind: the push-refusal file, else the configuration key; date) and origin-lacks (a plugin
    branch read as never pushed); then scope (push_scope's result, whose failed commit the row names). set_upstream:
    -u where the branch has no upstream, or one under another branch's name on a remote. <measure>, where given,
    measures push-scope in push_scope's place, last as step 5 orders it, and returns None where it could not run --
    start's, which reports that itself; the row is then unmeasured, which no §6 line renders, and nothing is
    pushed. Where <branch> is <session_branch>, §8.4's three differences: the first condition holds, a remote that
    deleted it does not stop the push (no ls-remote is asked), and push-scope counts <default_ref> as published."""
    out = {"row": None, "remote": None, "record": None, "record_kind": None, "date": None, "scope": None,
           "set_upstream": False}
    session = session_branch is not None and branch == session_branch
    plugin = branch_key(branch, [])["plugin_branch"] and branch not in (default, session_branch)
    if branch not in (default, session_branch) and not plugin:
        return dict(out, row="not-ours")
    if sb.git(root, "remote", "get-url", "origin", check=False).returncode != 0:
        return dict(out, row="no-remote")
    elsewhere = sb.config(root, "branch.%s.pushRemote" % branch) or sb.config(root, "remote.pushDefault")
    if elsewhere and elsewhere != "origin":
        return dict(out, row="elsewhere", remote=elsewhere)
    own = "refs/remotes/origin/" + branch
    upstream = sb.text(sb.git(root, "for-each-ref", "--format=%(upstream)", "refs/heads/" + branch))
    tracking = sb.git(root, "show-ref", "--verify", "-q", own, check=False).returncode == 0
    if not session and (upstream == own or (not upstream and tracking)):
        gone = sb.git_bounded(root, LS_REMOTE_CAP, "ls-remote", "--exit-code", "--heads", "origin", "refs/heads/" + branch)
        if gone.returncode == 2:
            return dict(out, row="remote-deleted")
    date = sb.refusal_record(root, branch)
    if date is not None:
        path = sb.refusal_path(root, branch)
        kind, record = (("file", path) if path and os.path.isfile(path)
                        else ("config", "branch.%s.workflowsPushRefused" % branch))
        return dict(out, row="refused-before", record=record, record_kind=kind, date=date or "an earlier run")
    if plugin and upstream != own and not tracking:
        return dict(out, row="origin-lacks")
    scope = measure(root, branch) if measure else push_scope(root, branch, default_ref if session else None)
    if scope is None:
        return dict(out, row="unmeasured")
    if not scope["in_scope"]:
        return dict(out, row="scope", scope=scope)
    merge, remote = sb.config(root, "branch.%s.merge" % branch), sb.config(root, "branch.%s.remote" % branch)
    return dict(out, set_upstream=not (merge and (remote == "." or merge == "refs/heads/" + branch)))


def _record_refusal(root, branch):
    """specs-repo-git §4 step 6: the push-refusal record, the file holding the date `date +%Y-%m-%d` prints (the local
    date), else the configuration key; where neither can be written, record_error is the configuration write's."""
    path = sb.refusal_path(root, branch)
    today = time.strftime("%Y-%m-%d")
    try:
        if path is None:
            raise OSError("git names no common directory")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(today + "\n")
        return {"recorded": "file", "record": path, "record_error": None}
    except OSError:
        pass
    key = "branch.%s.workflowsPushRefused" % branch
    r = sb.git(root, "config", key, today, check=False)
    if r.returncode == 0:
        return {"recorded": "config", "record": key, "record_error": None}
    return {"recorded": None, "record": None, "record_error": _first_line(r, error=True)}


def push(root, branch, set_upstream, src=None):
    """specs-repo-git §4 steps 5-6: `push --porcelain [-u] origin <branch>`, capped at 60 s, its outcome read from the
    --porcelain status line for refs/heads/<branch> alone, never from the exit status or the server's text: pushed for
    a flag in PUSHED_FLAGS; rejected for [rejected], which the replay settles; refused for [remote rejected] with a
    reason that is not TRANSIENT, which writes the push-refusal record (recorded: file, config or None; record; and
    record_error where neither could be written); failed otherwise -- a transient reason, another status, none, or
    the cap -- reason the status line's summary, git's first error line, or the capped push's words. With <src>, a
    commit, the landing's refspec push (§4 step 1, ruling C2): `push --porcelain origin <src>:refs/heads/<branch>`,
    which moves no local branch, its outcome read the same way."""
    lines = _load_module("specs_git_lines")
    out = {"outcome": "failed", "reason": None, "recorded": None, "record": None, "record_error": None}
    target = branch if src is None else "%s:refs/heads/%s" % (src, branch)
    p = sb.git_bounded(root, CAP, "push", "--porcelain", *(["-u"] if set_upstream else []), "origin", target)
    if p.returncode == 124:
        return dict(out, reason=lines.T["text.push-capped"])
    found = sb._porcelain_line(p.stdout, "refs/heads/" + branch)
    if found is None:
        return dict(out, reason=_first_line(p, error=True))
    flag, summary = found.split("\t")[0], _summary(found)
    if flag in PUSHED_FLAGS:
        return dict(out, outcome="pushed")
    if summary.startswith("[rejected]"):
        return dict(out, outcome="rejected", reason=summary)
    refused = _remote_refusal(summary)
    if refused is not None:
        return dict(out, outcome="refused", reason=refused, **_record_refusal(root, branch))
    return dict(out, reason=summary)


def _summary(porcelain):
    """A --porcelain status line's bracketed summary and its reason, its third field; None for no line."""
    fields = (porcelain or "").split("\t", 2)
    return fields[2] if len(fields) == 3 else None


def _remote_refusal(summary):
    """specs-repo-git §4 step 6's first bullet over a status line's <summary>: the reason in parentheses where it is a
    refusal -- [remote rejected] with a reason that does not begin with one of TRANSIENT -- else None."""
    if not (summary or "").startswith("[remote rejected]"):
        return None
    why = summary[len("[remote rejected]"):].strip()
    why = why[1:-1] if why.startswith("(") and why.endswith(")") else why
    return None if why.startswith(TRANSIENT) else why


def _row_line(lines, row, f):
    """specs-repo-git §6's line for <row>, from the facts <f>: sha7, files, branch, default and specs (<SPECS_PATH> as
    the run holds it), and as the row needs them -- remote; record, record_kind (file, config, or None for a refusal
    step 6 could not record), record_error and date; reason; error (Commit failed, and session-not-run's stderr line);
    scope (push_check's), subject (its failed commit's) and hook (the paths a pre-commit hook added to this run's own
    commit, naming the hook variant). In session-branch mode (§8): session_branch, where <branch> is the session
    branch, which the refused rows' remedy names in its own form; scope's branch-path failure, in §6's session-branch
    form, naming the merge commit where failed.sha holds one; F, pushed-session's count; and sync, whose
    conflicts give rejected -- here only the session branch's push-rejected row (§8.4; a replay's rows are
    _replay_line's) -- its conflict ending. mode_on and identity: a push refused on the default branch outside the
    mode, whose remedy says the mode turns on, under <identity>'s session branch or, with none, the no-identity
    words."""
    T = lines.T
    v = {"<sha7>": f.get("sha7"), "<N>": f.get("files"), "<branch>": f.get("branch"), "<default>": f.get("default"),
         "<SPECS_PATH>": f.get("specs"), "<YYYY-MM-DD>": _today(), "<identity>": _identity(f.get("session_branch"))}
    t, tail = T["row.session-rejected" if row == "rejected" else "row." + row], ""
    if row == "remote-deleted" and f.get("branch") == f.get("default"):
        tail = lines.fill("row.remote-deleted.default-tail", v)
    elif row == "elsewhere":
        v["<remote>"] = f.get("remote")
    elif row == "failed":
        v["<reason>"] = f.get("reason")
    elif row == "commit-failed":
        v["<the first line of git's error or the hook's output>"] = f.get("error")
    elif row == "session-not-run":
        v["<the first line of its stderr>"] = f.get("error")
    elif row == "pushed-session":
        v["<F>"] = f.get("F")
    elif row == "rejected":
        origin = "origin/" + (f.get("session_branch") or "")
        if any(c.get("source") == origin for c in (f.get("sync") or {}).get("conflicts") or []):
            t = _swap(t, "; a later run takes them in and pushes", T["row.session-rejected.conflict-ending"])
    elif row in ("refused-before", "push-refused"):
        v.update({"<record>": f.get("record"), "<date>": f.get("date"), "<the reason in parentheses>": f.get("reason")})
        if row == "push-refused" and f.get("record_kind") is None:
            t = _swap(t, "so this is recorded and no later run pushes it", T["app.unrecorded"])
            t = t[:t.index("; to land the commits")]
            v["<error>"] = f.get("record_error")
        else:
            if f.get("session_branch"):  # never stood on, so no reset is named for it
                t = t[:t.index("to land the commits")] + T["app.session.refused-remedy"]
            elif row == "push-refused" and f.get("mode_on"):  # this run is the one that turns the mode on
                remedy = T["app.mode-on"]
                if not f.get("identity"):
                    remedy = _swap(remedy, "session/<identity>", T["app.mode-on.no-identity"])
                t, v["<identity>"] = t[:t.index("to land the commits")] + remedy, f.get("identity")
            if f.get("record_kind") == "config" and 'rm "<record>"' in t:
                t = _swap(t, 'rm "<record>"', T["app.record-unset"]).replace("<record>", T["app.record-key"])
    elif row == "scope":
        failed = f["scope"]["failed"]
        if failed["reason"] == "branch-path":  # §8.4: the session branch's whole change names <path>
            t = T["row.scope.branch-path"]
            v.update({"<path>": failed["path"], "<merge sha7>": (failed["sha"] or "")[:7] or None,
                      "<subject>": f.get("subject")})
        elif f.get("hook"):
            t = T["row.scope.hook"]
            v.update({"<path>": f["hook"][0], "<M-1>": str(len(f["hook"]) - 1) if len(f["hook"]) > 1 else None})
        else:
            if failed["reason"] == "merge":
                t = _swap(t, "which carries <path>", T["row.scope.merge"])
            elif failed["path"] is None:
                t = _swap(t, "which carries <path>", T["row.scope.no-file"])
            v.update({"<sha7>": [f.get("sha7"), failed["sha"][:7]], "<subject>": f.get("subject"), "<path>": failed["path"]})
    return lines.fill(t, v) + tail


def _appends(lines, f):
    """specs-repo-git §6's session-branch appends to the outcome line, in §6's order: the created clause
    (f's created, where f names a session branch), sync.conflict by source -- <default-ref>'s paths, then
    origin/<session branch>'s, each in sync.conflicts' order -- sync.error, each unsettled path then the closing clause
    once, stranded, and unsupported where f's mode is. f: specs, default, default_ref, session_branch, branch (where
    the files stay, for unsupported), mode, and the last sb.commit's sync, unsettled and stranded. The declined append,
    which §6 puts after these, is _declined's, which finish_end and the blocked rows add. The blocked rows and a line on
    a detached HEAD pass the created clause's facts alone, since §6 gives them no other session append; the misrooted
    row takes none, the declined append included."""
    T, out = lines.T, ""
    branch = f.get("session_branch")
    v = {"<identity>": _identity(branch), "<default>": f.get("default"), "<SPECS_PATH>": f.get("specs"),
         "<the script's path>": SB_SCRIPT}
    if branch and f.get("created"):
        out += lines.fill("app.session.created", dict(v, **{"<base short sha>": f["created"]}))
    sync = f.get("sync") or {}
    if branch:
        out += _conflict_clause(lines, "app.session.conflict-default", f.get("default_ref"), sync, v)
        out += _conflict_clause(lines, "app.session.conflict-origin", "origin/" + branch, sync, v)
        if sync.get("error"):
            out += lines.fill("app.session.sync-error", dict(v, **{"<sync.error>": " ".join(str(sync["error"]).split())}))
        for path in f.get("unsettled") or []:
            out += lines.fill("app.session.unsettled", dict(v, **{"<path>": path}))
        if f.get("unsettled"):
            out += T["app.session.unsettled.close"]
        if f.get("stranded"):
            out += lines.fill("app.session.stranded", dict(v, **{"<K>": f["stranded"]}))
    if f.get("mode") == "unsupported":
        out += lines.fill("app.session.unsupported", {"<branch>": f.get("branch")})
    return out


def _conflict_clause(lines, tid, source, sync, v):
    """§6's sync.conflict clause <tid> for the paths <sync>'s conflicts give <source>, in their order; '' where none."""
    paths = _unique([c["path"] for c in (sync or {}).get("conflicts") or [] if c.get("source") == source])
    return lines.fill(tid, dict(v, **{"<path>": paths})) if paths else ""


def _append_facts(specs, rec, branch, session=None):
    """_appends' facts for a line on <branch>: the run's from its record <rec> -- the session branch only where the mode
    is on, the creation a call other than §3.4's flush made -- and <session>, the last sb.commit's sync, unsettled and
    stranded."""
    on = rec.get("mode") == "on"
    return dict({"specs": specs, "default": rec.get("default"), "default_ref": rec.get("default_ref"),
                 "session_branch": rec.get("session_branch") if on else None,
                 "created": rec.get("session_branch_created"), "mode": rec.get("mode"), "branch": branch},
                **(session or {}))


def _mode_on_facts(specs, mode, branch, default):
    """The facts a push refused on <branch> needs for specs-repo-git §6's mode-on remedy: where <branch> is the default
    branch and the mode is off, the refusal's record turns it on from the next run (§8.1), under the identity §8.1
    resolves; else none. Read only where a push was refused."""
    if branch is None or branch != default or mode not in (None, "off"):
        return {}
    return {"mode_on": True, "identity": sb.identity(specs)[0]}


def _specs_half(line):
    """The SPECS_PATH half of session-hygiene §7's Environment: line: SPECS_PATH's real path and its origin."""
    return line.partition("), REPOS_PATH=")[0]


def _values(line):
    """An Environment: line's values, as env.changed names them: the line without its label."""
    return line[len("Environment: "):] if line.startswith("Environment: ") else line


def _g0_block(lines, specs, default):
    """specs-repo-git §5's G0 block for the checkout at <specs>: its detached HEAD's sha7, today's date for the rescue
    branch, and the default branch to rejoin -- where there is none, the first local branch, else main."""
    sha = sb.text(sb.git(specs, "rev-parse", "HEAD"))
    rejoin = default or (sb.text(sb.git(specs, "for-each-ref", "--count=1", "--format=%(refname:short)", "refs/heads"))
                         or "main")
    return lines.fill("g0", {"<SPECS_PATH>": specs, "<sha7>": sha[:7], "<YYYY-MM-DD>": _today(), "<branch>": rejoin})


def _unique(paths):
    out = []
    for p in paths:
        if p not in out:
            out.append(p)
    return out


def _view(rec, declined=()):
    """What step 7 renders from a record besides the row: the declined paths (the record's, then the call's), and the
    §5 block of a guard its start fired (G0's prints with the blocked row instead) with the paths that block lists."""
    rec = rec or {}
    return {"declined": _unique(list(rec.get("declined") or []) + list(declined)),
            "guard_block": None if rec.get("specs_git") == "blocked" else rec.get("guard_block"),
            "guard_paths": list(rec.get("guard_paths") or [])}


def _landed(root, pending):
    """The commit a pending end_commit -- saved just before `git commit` -- is about, where it landed: the tip of its
    branch, whose one parent is the base saved then and which holds, for every path the commit was about to name,
    exactly the blob the index held for it then (a staged removal: no blob at all). Never its message, which a
    prepare-commit-msg or commit-msg hook may rewrite. Its facts as end_commit holds them, hook_paths the paths it
    carries that it was not about to name; None where that commit was not made."""
    tip = sb.rev(root, "refs/heads/" + pending.get("branch", ""))
    staged = pending.get("staged") or {}
    if tip is None or tip == pending.get("base") or not staged:
        return None
    if sb.text(sb.git(root, "rev-list", "--parents", "-n", "1", tip)).split()[1:] != [pending.get("base")]:
        return None
    if any(sb.blob(root, tip, path) != blob for path, blob in staged.items()):
        return None
    carried = _commit_paths(root, tip)
    return {"sha7": tip[:7], "files": len(carried), "branch": pending["branch"], "paths": carried,
            "hook_paths": [p for p in carried if p not in staged]}


def _landed_session(root, rec):
    """In session-branch mode, the run's commits a pending end_commit is about -- {branch, base, session}, saved just
    before the run's first §8.2 commit, base the session branch's tip then, or None where it did not exist -- where any
    landed: the non-merge commits on the branch that neither <base>, the record's <default-ref> nor origin's copy of the
    branch holds (§8.2 step 3's merges bring theirs in). Their facts as end_commit holds them: sha7 the newest, files
    every path they change, the session facts empty (the commit's own output is lost), and, where <base> was None,
    created -- the commit the branch was created at, the oldest's parent. None where none landed."""
    pending = rec["end_commit"]
    branch = pending.get("branch") or ""
    tip = sb.rev(root, "refs/heads/" + branch)
    if tip is None or tip == pending.get("base"):
        return None
    nots = [x for x in (pending.get("base"), rec.get("default_ref"), "refs/remotes/origin/" + branch) if x and sb.rev(root, x)]
    commits = sb.text(sb.git(root, "rev-list", "--no-merges", tip, "--not", *nots)).split()
    if not commits:
        return None
    paths = _unique([p for c in reversed(commits) for p in _commit_paths(root, c)])
    created = None if pending.get("base") else (sb.rev(root, commits[-1] + "^") or "")[:7] or None
    return {"sha7": commits[0][:7], "files": len(paths), "branch": branch, "paths": paths, "hook_paths": [],
            "session": {}, "created": created}


def _end_result(**kw):
    out = {"print": [], "line": None, "row": None, "sha7": None, "files": None, "branch": None, "pushed": False,
           "next": None, "record": None, "error": None}
    out.update(kw)
    return out


def _replay_next(specs, command, branch, set_upstream, for_="end"):
    """The call a rejected push hands the run (specs-repo-git §4 step 6): the replay, in a Bash call of its own, and
    the same with --timed-out where the harness ends that call at its timeout. <for_>: end, or start for §3.4's."""
    run = "python3 %s --specs %s replay --for %s --command %s --branch %s%s" % (
        shlex.quote(os.path.abspath(__file__)), shlex.quote(specs), for_, shlex.quote(command), shlex.quote(branch),
        " --set-upstream" if set_upstream else "")
    return {"run": run, "timeout_ms": REPLAY_TIMEOUT_MS, "on_timeout": run + " --timed-out"}


def _resume_next(command, args, budget=None):
    """The call that goes on with a start the replay or a budget stop interrupted: start --resume, repeating the start
    call's --specs, every --key in order, --commit-key and --register-rebuild as the record's <args> hold them, so the
    resume passes resumable's argument test, and --budget where the record's <budget> holds one (a start call's that
    was not the default) -- how the preflight is split across calls, which no argument test reads; in a Bash call of
    its own, start's 600 s, nothing to run on a timeout."""
    parts = ["--specs", args.get("specs") or "", "start", "--command", command]
    for key in args.get("keys") or []:
        parts += ["--key", key]
    for flag, field in (("--commit-key", "commit_key"), ("--register-rebuild", "register_rebuild")):
        if args.get(field):
            parts += [flag, args[field]]
    if budget is not None:
        parts += ["--budget", "%g" % budget]
    run = " ".join(["python3", shlex.quote(os.path.abspath(__file__))] + [shlex.quote(p) for p in parts + ["--resume"]])
    return {"run": run, "timeout_ms": START_TIMEOUT_MS, "on_timeout": None}


def _stop(run, row, printed, line):
    """An outcome of §4 step 1 -- misrooted, blocked or silent: what it prints, the record removed. A blocked row's
    <line> already carries §6's declined append where it takes one (_declined, _declined_checked); the misrooted row
    takes none, so no git status runs in a path the run has found wrong (§6), and the silent no-op prints nothing."""
    run["state"].remove(run["session"], run["command"])
    return _end_result(print=printed, line=line, row=row, record=run["record"])


def _declined(run, view):
    """specs-repo-git §6's declined append, the last of a line's appends: the paths of <view>'s declined list that
    status() still lists, in phase-handoff §4.1's <artifacts> form; '' where none was declined or none is listed."""
    if not view["declined"]:
        return ""
    listed = status(run["specs"])
    still = set(listed["artifact"]) | set(listed["other"])
    named = [p for p in view["declined"] if p in still]
    return run["lines"].fill("app.declined", {"<path>": run["lines"].artifacts(named)}) if named else ""


def _declined_checked(run, rec, view):
    """_declined on the Blocked (G0) row of a run whose start set specs_git: blocked, where the end tests neither the
    gate nor the run's environment (§4 step 1: the flag is tested first): only where the SPECS_PATH half of the
    Environment: line printed now is the one the record <rec> holds, so git status runs in the repository the start
    checked; '' elsewhere, and where that line or git status cannot run (§6). Wherever it returns '', the row prints as
    it did before the append existed; exit 0 whatever --specs names."""
    try:
        if not rec.get("env_line") or _specs_half(env_line(run["specs"])) != _specs_half(rec["env_line"]):
            return ""
        return _declined(run, view)
    except NotRun:
        return ""


def finish_end(run, row, line, view, commit=None, branch=None, pushed=False, hook=()):
    """specs-repo-git §4 step 7 from a row's <line>: the appends in §6's order -- the declined one last (_declined) --
    then the §5 block a guard's record repeats, then, where the push-scope row's hook variant names <hook>, the hook
    line for those of them the block or the declined paths name; the record removed. <run> holds state, lines, specs,
    session, command, record, and pre (lines printed before the outcome line)."""
    lines = run["lines"]
    line += _declined(run, view)
    printed = list(run.get("pre") or []) + [line]
    if view["guard_block"]:
        printed.append(view["guard_block"])
    swept = [p for p in hook if p in set(view["guard_paths"]) | set(view["declined"])]
    if swept:
        printed.append(lines.fill("app.hook-line", {"<path>": swept, "<sha7>": commit["sha7"]}))
    run["state"].remove(run["session"], run["command"])
    commit = commit or {}
    return _end_result(print=printed, line=line, row=row, sha7=commit.get("sha7"), files=commit.get("files"),
                       branch=branch, pushed=pushed, record=run["record"])


def _end_view(lines, rec, view, default, specs, stay, committed):
    """<view> with the G1 block the run's end repeats in the form specs-repo-git §5 gives the end (_g1_landing): the
    landing form where <stay>, the stay the end's landing ran on, stands; the plain block where none does; under a run
    typed mid-run, the mid-run form; its Not done by <committed>, whether the end committed the run's whole change. A
    G2 block, and none, as they are."""
    rec = rec or {}
    if not view.get("guard_block") or rec.get("guard") != "G1":
        return view
    return dict(view, guard_block=_g1_landing(lines, view["guard_block"], (stay or {}).get("branch"), default,
                                              rec.get("specs") or specs, view["guard_paths"], stay, rec.get("midrun"),
                                              committed))


def _land_clause(lines, refused, default, onto=None):
    """specs-repo-git §6's landing reason clause for the refusal <refused> ({reason, path, detail}): its LAND_REASONS
    template, <path> the refused path, <default>, and <onto> -- <default>, or, in the here form, HEAD's branch <onto>,
    which <branch> names too; checked-out's alternative and values from its detail (checked_out_values), and
    register-rebuild's alternative from its detail, none or failed."""
    reason = refused.get("reason")
    v = {"<path>": refused.get("path"), "<default>": default, "<onto>": onto or default, "<branch>": onto or default}
    if reason == "checked-out":
        v.update(checked_out_values(lines, refused.get("detail")) or {})
    elif reason == "register-rebuild":
        v[lines.placeholder("reason.land.register", "<and this")] = 1 if refused.get("detail") == "failed" else 0
    return lines.fill(LAND_REASONS[reason], v)


def _landing_append(lines, commit, rec):
    """specs-repo-git §6's appends after a landing, in its order, for <commit>, which a landing made on <default>
    (its landing: the journal's pending, with moves and stuck): app.landed, naming the stayed branch and the stay's
    kind from <rec>'s stay; app.landed.unlisted where the run's start could not list the uncommitted paths
    (pre.status-failed in the record's reported, P12); the register clause for each security/<slug>/ the landing's
    rebuild renumbered; app.held.stuck where a path was held alone. '' for a commit no landing made. The session
    appends follow it (_appends), and the declined append comes last (finish_end)."""
    landing = (commit or {}).get("landing")
    if not isinstance(landing, dict):
        return ""
    stay, default = rec.get("stay") or {}, rec.get("default")
    out = lines.fill("app.landed", {"<branch>": stay.get("branch"), "<default>": default, "<command>": stay.get("command"),
                                    lines.placeholder("app.landed", "<which no key"): STAY_KINDS.index(stay.get("kind"))})
    if "pre.status-failed" in (rec.get("reported") or []):
        out += lines.fill("app.landed.unlisted", {"<branch>": stay.get("branch")})
    clause = _register_clause(lines, landing.get("moves"))
    if clause:
        out += "; " + clause
    stuck = landing.get("stuck")
    if stuck:
        out += lines.fill("app.held.stuck", {
            "<path>": stuck["paths"], "<reason clause>": _land_clause(lines, stuck["refused"], default),
            "<SPECS_PATH>": rec.get("specs"), "<sha7>": stuck["sha"][:7], "<default>": default,
            "<specs-git.py's path>": SG_SCRIPT, "<default-ref>": rec.get("default_ref")})
    return out


def _push_step(run, rec, commit, default, view):
    """specs-repo-git §4 steps 5-7 for <commit>, saved in <rec> as end_commit: push_check, then push. A rejected push
    keeps the record at stage end-replay and returns next naming the replay; every other outcome renders its row. In
    session-branch mode -- <commit> on the session branch, its session facts set -- push_check takes §8.4's
    differences, a push that lands is pushed-session with <F>, and a rejection is the session branch's push-rejected
    row, never a replay (§4 step 6: in session-branch mode nothing is replayed). Every line carries §6's session
    appends -- after a landing's (_landing_append), where §4 step 1's landing made <commit> on <default> -- and a push
    refused on the default branch outside the mode names the mode it turns on."""
    lines, specs, branch = run["lines"], run["specs"], commit["branch"]
    session = commit.get("session")
    run["commit"] = commit
    sbranch = branch if session is not None else None
    check = push_check(specs, branch, default, session_branch=sbranch, default_ref=rec.get("default_ref"))
    facts = {"sha7": commit["sha7"], "files": commit["files"], "branch": branch, "default": default, "specs": specs,
             "session_branch": sbranch, "sync": (session or {}).get("sync")}
    hook, pushed = (), False
    if check["row"] is None:
        p = push(specs, branch, check["set_upstream"])
        if p["outcome"] == "rejected" and session is None:
            rec["stage"] = "end-replay"
            run["state"].save(run["session"], run["command"], rec)
            return _end_result(print=list(run.get("pre") or []), sha7=commit["sha7"], files=commit["files"], branch=branch,
                               next=_replay_next(specs, run["command"], branch, check["set_upstream"]),
                               record=run["record"])
        row = {"pushed": "pushed-session" if session is not None else "pushed-default" if branch == default
               else "pushed-plugin", "refused": "push-refused", "failed": "failed", "rejected": "rejected"}[p["outcome"]]
        pushed = p["outcome"] == "pushed"
        facts.update(reason=p["reason"], record=p["record"], record_kind=p["recorded"], record_error=p["record_error"])
        if row == "pushed-session":  # what its pull request shows: the session files not on the default branch yet
            facts["F"] = len(sb.nul_list(sb.git(specs, "diff", "--name-only", "-z", "--no-renames",
                                                "%s...refs/heads/%s" % (rec.get("default_ref"), branch))))
        elif row == "push-refused":
            facts.update(_mode_on_facts(specs, rec.get("mode"), branch, default))
    else:
        row = check["row"]
        facts.update(remote=check["remote"], record=check["record"], record_kind=check["record_kind"], date=check["date"])
        if row == "scope":
            failed = check["scope"]["failed"]
            facts["scope"] = check["scope"]
            facts["subject"] = sb.text(sb.git(specs, "log", "-1", "--format=%s", failed["sha"])) if failed["sha"] else None
            if failed["sha"] and failed["sha"][:7] == commit["sha7"]:  # this run's own commit: a hook added the rest
                hook = [path for path in commit["hook_paths"] if not sb.classify(path)]
                facts["hook"] = hook
    line = (_row_line(lines, row, facts) + _landing_append(lines, commit, rec)
            + _appends(lines, _append_facts(specs, rec, branch, session)))
    return finish_end(run, row, line, view, commit=commit, branch=branch, pushed=pushed, hook=hook)


def end(specs, command, commit_key=None, register_rebuild=None, no_preflight=False, misrooted_notice=None,
        session_branch_created=None, declined=(), resume=False):
    """specs-repo-git §4's commit-artifacts for the run of this session and <command>, steps 1-7, on <specs>
    (SPECS_PATH as set, "" meaning unset). <misrooted_notice>: the lines of a notice that set misrooted outside the
    script (--misrooted-stdin), [] for none. <declined>: paths a declined call could not record. A failure before the
    run's first write -- the catch-up's pull, else `git add`, or, before §4 step 1's landing, the record's save --
    raises, so the caller exits 2 with nothing done; after it, an exception (a signal sb.git_bounded turns into NotRun
    among them) returns error set and the end.stopped line, and the record stays for --resume: a later start replaces
    it, --no-preflight ignores it, and prune removes it after 7 days."""
    state, lines = _flow()
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    if commit_key is not None and not KEY_RE.fullmatch(commit_key):
        raise NotRun("usage: --commit-key %s does not match addressing §1's key grammar" % commit_key)
    if session_branch_created is not None and not SHA_RE.fullmatch(session_branch_created):
        raise NotRun("usage: --session-branch-created takes a commit's short sha, got %s" % session_branch_created)
    session = state.session_id()
    run = {"state": state, "lines": lines, "specs": specs, "session": session, "command": command, "record": None,
           "wrote": False, "pre": [], "commit": None}
    try:
        return _end(run, commit_key, register_rebuild, no_preflight, misrooted_notice, session_branch_created,
                    list(declined), resume)
    except Exception as e:
        if not run["wrote"]:
            raise
        said = " ".join(str(e).split())
        error = said if isinstance(e, NotRun) else type(e).__name__ + (": " + said if said else "")
        line = lines.fill("end.stopped", {"<the error>": error})
        commit = run["commit"] or {}
        block = (run.get("view") or {}).get("guard_block")  # §6: a G1 or G2 block follows the outcome line, this one too
        return _end_result(print=list(run["pre"]) + [line] + ([block] if block else []), line=line,
                           sha7=commit.get("sha7"), files=commit.get("files"), branch=commit.get("branch"),
                           record=run["record"], error=error)


def _end(run, commit_key, register_rebuild, no_preflight, misrooted_notice, session_branch_created, declined, resume):
    state, lines, specs, session, command = (run[k] for k in ("state", "lines", "specs", "session", "command"))
    rec = state.load(session, command)
    if resume and rec is not None and rec.get("end_commit") and state.saved_within(rec):
        pending = rec["end_commit"]
        landing = pending.get("landing")
        if isinstance(landing, dict) and not pending.get("sha7"):  # §4 step 1's landing, cut off before it was saved
            view = _view(rec, declined)
            # first, so a stop from here on repeats the record's block (§6), in the form for an early stop (§5)
            run["view"] = _end_view(lines, rec, view, rec.get("default"), specs, rec.get("stay"), False)
            run["wrote"] = True
            run["record"] = "found"
            got = _resume_landing(run, rec, view, commit_key, landing)
            if got is not None:
                return got
            # the journal dropped, HEAD off the stay's branch: step 1 goes on as for a HEAD that moved (§4 step 1)
        else:
            commit = (pending if pending.get("sha7") else _landed_session(specs, rec) if "session" in pending
                      else _landed(specs, pending))
            if commit is not None:  # the run's commit is made: what follows is past its first write
                view = _view(rec, declined)
                stay = rec.get("stay") if isinstance(landing, dict) else None
                run["view"] = _end_view(lines, rec, view, rec.get("default"), specs, stay, False)  # first, as above
                run["wrote"] = True
                run["record"] = "found"
                if commit is not rec["end_commit"]:
                    created = commit.pop("created", None)
                    if created and not rec.get("session_branch_created"):
                        rec["session_branch_created"] = created
                    rec["end_commit"] = commit
                    state.save(session, command, rec)
                default = rec.get("default") or resolve_default(specs, False)["default"]
                return _push_step(run, rec, commit, default,
                                  _end_view(lines, rec, view, default, specs, stay, not (landing or {}).get("stuck")))

    # Step 1: the record. Each kind but found takes the no-preflight path; an ignored record is replaced or removed.
    if rec is None:
        kind = "missing"
    elif no_preflight:
        kind = "ignored"
    elif rec.get("started_by_script") is False:
        kind = "declined-only"
    else:
        kind = "found"
    run["record"] = kind
    found = kind == "found"
    keep = rec if kind in ("found", "declined-only") else None
    view = run["view"] = _view(keep, declined)

    # Step 1: the flags, in order, the first that holds deciding; a flag's outcome comes before the gate's.
    flag, notice = None, []
    if found and rec.get("specs_git") == "blocked":
        flag = "blocked"
    elif found and rec.get("specs_git") == "misrooted":
        flag, notice = "misrooted", list(rec.get("misrooted_notice") or [])
    if flag is None and misrooted_notice is not None:
        flag, notice = "misrooted", list(misrooted_notice)
    if flag is None and found and rec.get("env_line"):  # D4: the SPECS_PATH half of the line the run's start printed
        now = env_line(specs)
        if _specs_half(now) != _specs_half(rec["env_line"]):
            flag, notice = "misrooted", [lines.fill("env.changed", {
                "<the values the line recorded>": _values(rec["env_line"]), "<the values printed now>": _values(now)})]
    g = None
    if flag is None and not found:  # D3: no preflight recorded its placement tests, so they run here
        g = gate(specs)
        if g["misrooted"]:
            flag, notice = "misrooted", list(g["lines"])
    if flag == "misrooted":
        line = lines.fill("row.misrooted", {})
        return _stop(run, "misrooted", [line] + notice, line)
    if flag == "blocked":  # §6: the created clause, which names no branch the files stay on, then the declined append
        sbranch = rec.get("session_branch") if rec.get("mode") == "on" else None
        line = lines.fill("row.blocked", {}) + _appends(lines, {"session_branch": sbranch, "created": (
            session_branch_created or rec.get("session_branch_created"))}) + _declined_checked(run, rec, view)
        return _stop(run, "blocked", [line] + ([rec["guard_block"]] if rec.get("guard_block") else []), line)

    # Step 1's gate, then G0's state where no flag stands: a commit on a detached HEAD is reachable from no branch.
    if g is None:
        g = gate(specs, notices=False)
    if g["state"] != "pass":
        return _stop(run, "silent", [], None)
    branch = _head_branch(specs)
    if found and rec.get("default"):
        d = {k: rec.get(k) for k in ("default", "default_ref", "remote")}
    else:
        d = resolve_default(specs, False)
    # §8.1's mode and session branch: the record's, which start resolved, else resolved here (step 1, on a run that ran
    # no preflight); the session branch is carried only where the mode is on, and is null there with no identity.
    if found and rec.get("mode"):
        mode, session_branch = rec["mode"], rec.get("session_branch")
    elif d["default"]:
        m = sb.mode(specs, d["default"])
        mode, session_branch = m["mode"], m["branch"] if m["mode"] == "on" else None
    else:
        mode, session_branch = "off", None
    if branch is None:
        if status(specs)["artifact"]:
            line = lines.fill("row.blocked", {}) + _appends(lines, {"session_branch": session_branch, "created": (
                session_branch_created or (keep or {}).get("session_branch_created"))}) + _declined(run, view)
            return _stop(run, "blocked", [line, _g0_block(lines, specs, d["default"])], line)
        line = lines.fill("row.nothing", {}) + _appends(lines, {"session_branch": session_branch, "created": (
            session_branch_created or (keep or {}).get("session_branch_created"))})
        return finish_end(run, "nothing", line, _end_view(lines, keep, view, d["default"], specs, None, False))

    # Step 1's stay (§4 step 1): outside session-branch mode, the record's stay on the branch HEAD stands on, or, where
    # a start that never finished its preflight holds none for it, the one end asks for (_unfinished_stay). A stay whose
    # merged flag is not set is tested once more against the end's commit key (with the run key set beside it): where
    # that names the branch, the run's own, the stay is dropped and the step goes on as below, committing there. Where a
    # stay stands, the landing runs in place of steps 2-4.
    stay = None
    if found and mode != "on":
        stay = rec["stay"] if _stayed_on(rec, branch) else _unfinished_stay(specs, rec, branch, d, mode, commit_key)
        if stay is not None and not stay.get("merged") and branch_key(branch, _run_keys(rec, (commit_key,)))["key"]:
            stay = None

    # Steps 2-4: the catch-up, then the commit. R2's boundary is the first repository write either makes, and just
    # before it the record is saved at stage end -- the one kept, else a new one in place of whatever stood -- with what
    # this call was given; and again just before the commit, with what it is about to make -- outside the mode, before
    # `git commit`, its branch, its base and each path's staged blob (_landed); in the mode, before the run's first
    # §8.2 commit, the session branch and its tip then (_landed_session) -- so --resume finds the run's commit where a
    # kill comes between it and the save naming it.
    message = session_subject(commit_key or (keep or {}).get("commit_key"), command)
    saved = keep if keep is not None else state.new(command, session=session, started_by_script=False, specs=specs)
    saved.update(stage="end", end_commit=None, declined=view["declined"], mode=mode, session_branch=session_branch,
                 default=d["default"], default_ref=d["default_ref"], remote=d["remote"], stay=stay)
    for field, value in (("commit_key", commit_key), ("register_rebuild", register_rebuild),
                         ("session_branch_created", session_branch_created)):
        if value:
            saved[field] = value

    def boundary():
        state.save(session, command, saved)
        run["wrote"] = True

    def about_to_commit(staged):
        saved["end_commit"] = {"branch": branch, "base": sb.rev(specs, "HEAD"), "staged": staged}
        state.save(session, command, saved)

    # §5's G1 block as the end repeats it: until the outcome is known -- and for an early stop, and a line that
    # commits none of the run's files -- in the form that leaves to the outcome line what came of them
    run["view"] = _end_view(lines, keep, view, d["default"], specs, stay, False)
    if stay is not None:
        boundary()

        def on_move(pending):  # the landing's journal, saved just before <default> moves or is pushed (§4 step 1)
            saved["end_commit"] = {"branch": d["default"], "landing": pending}
            state.save(session, command, saved)

        got = land(specs, branch, d["default"], d["default_ref"], message, saved.get("start_dirty"),
                   saved.get("register_rebuild"), facts=_land_facts(stay, command), on_move=on_move,
                   retry_remote=False)
        return _landing_end(run, saved, d, stay, got, view)
    shown = _end_view(lines, keep, view, d["default"], specs, None, True)
    if mode == "on":
        return _end_session(run, saved, d, branch, message, shown, boundary)
    pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary)
    if pulled:
        run["pre"].append(pulled)
    c = commit_session_files(specs, message, on_write=boundary, on_staged=about_to_commit)
    if c["status"] != "committed":
        row = {"nothing": "nothing", "locked": "locked", "failed": "commit-failed"}[c["status"]]
        line = _row_line(lines, row, {"error": c["error"]}) + _appends(lines, _append_facts(specs, saved, branch))
        return finish_end(run, row, line, run["view"], branch=branch)
    commit = {"sha7": c["sha"][:7], "files": len(c["paths"]), "branch": branch, "paths": c["paths"],
              "hook_paths": c["hook_paths"]}
    run["commit"] = commit
    saved["end_commit"] = commit
    state.save(session, command, saved)
    return _push_step(run, saved, commit, d["default"], shown)


def _unfinished_stay(specs, rec, branch, d, mode, commit_key):
    """specs-repo-git §4 step 1's stay for a start that never finished its preflight -- its record at one of start's own
    stages (START_STAGES): its last call stopped early, was cut off, or returned a next the run never made, at its
    budget or for a replay, so it ended before B2's or B4's switch and may have ended before G1's test. Where HEAD stands
    on <branch>, the plugin branch that call returned on (the record's branch), off the default branch and outside
    session-branch mode, ask what G1's test asks: branch-merged HEAD -- read unmerged, with no report, where it cannot
    answer (§3.5) -- then the stay's kind (_stay_kind), against the run key set with the end's <commit_key> beside it;
    return the stay it gives, with the early stop's reason (_stay_record), or None."""
    if (rec.get("stage") not in START_STAGES or mode == "on" or branch is None or branch != rec.get("branch")
            or branch == d["default"] or not d["default_ref"] or not branch_key(branch, [])["plugin_branch"]):
        return None
    try:
        merged = branch_merged(specs, "HEAD", d["default_ref"])["merged"]
    except NotRun:
        merged = False
    kind = _stay_kind(dict(rec, default=d["default"], mode=mode), branch, merged, extra_keys=(commit_key,))
    return _stay_record(rec, branch, kind, "stopped", merged) if kind else None


def _land_facts(stay, command):
    """land's facts for a held entry of the run of <command> that holds <stay>: the stay's kind, flag and branch."""
    return {"kind": stay.get("kind"), "merged": stay.get("merged"), "command": command, "stayed": stay.get("branch")}


def _landing_end(run, saved, d, stay, got, view):
    """specs-repo-git §4 step 1's landing's outcome, from land's <got>, as the end prints it: §3.2's pre.held.landed for
    each held entry it landed first, before the row. landed: the commit saved as end_commit with its landing -- the
    journal's pending, moves and stuck -- then the refspec push's pushed-default row at once, else steps 5-7 on
    <default> (_push_step); held: the held row, its tail by mode_takes, or the held, stuck row where the cause will not
    pass; there, nothing and locked: their rows; any other status raises, so no template id is ever printed. Each row
    carries §6's appends -- the held, held-stuck and there rows, which commit none of the run's files, without the
    unsupported clause -- and is followed by G1's block, from the plain <view>, in the landing form, its Not done the
    not-landed one unless the run's whole change landed (_end_view)."""
    lines, specs, state = run["lines"], run["specs"], run["state"]
    default, branch = d["default"], stay["branch"]
    for h in got["held_landed"]:
        run["pre"].append(lines.fill("pre.held.landed", {"<sha7>": h["sha"][:7], "<N>": h["files"],
                                                        "<default>": default, "<branch>": branch}))
    view = _end_view(lines, saved, view, default, specs, stay, got["status"] == "landed" and not got["stuck"])
    if got["status"] == "landed":
        commit = {"sha7": got["sha"][:7], "files": got["files"], "branch": default, "paths": got["paths"],
                  "hook_paths": [], "landing": dict(got["pending"] or {}, moves=got["moves"], stuck=got["stuck"])}
        run["commit"] = commit
        saved["end_commit"] = commit
        state.save(run["session"], run["command"], saved)
        if not got["pushed"]:
            return _push_step(run, saved, commit, default, view)
        facts = {"sha7": commit["sha7"], "files": commit["files"], "branch": default, "default": default, "specs": specs}
        line = (_row_line(lines, "pushed-default", facts) + _landing_append(lines, commit, saved)
                + _appends(lines, _append_facts(specs, saved, default)))
        return finish_end(run, "pushed-default", line, view, commit=commit, branch=default, pushed=True)
    if got["status"] == "held":
        refused = got["refused"]
        row = "held-stuck" if refused.get("permanent") else "held"
        v = {"<branch>": branch, "<default>": default, "<command>": stay.get("command"),
             lines.placeholder("row." + row, "<which no key"): STAY_KINDS.index(stay["kind"]),
             "<reason clause>": _land_clause(lines, refused, default), "<SPECS_PATH>": saved.get("specs") or specs,
             "<sha7>": got["sha"][:7], "<specs-git.py's path>": SG_SCRIPT, "<default-ref>": d["default_ref"]}
        if row == "held":
            v[lines.placeholder("row.held", "<held for")] = 1 if mode_takes(refused) else 0
        line = lines.fill("row." + row, v)
    elif got["status"] in ("there", "nothing", "locked"):
        row = got["status"]
        line = lines.fill("row." + row, {"<default>": default, "<branch>": branch})
    else:  # kept is the here form's alone, which no landing's journal takes
        raise NotRun("the landing returned %s, for which §4 step 1 gives the landing no row" % got["status"])
    # §6: the held, held-stuck and there rows, none of which commits the files this run, take no unsupported clause
    facts = _append_facts(specs, saved, branch)
    if row in ("held", "held-stuck", "there"):
        facts["mode"] = None
    line += _appends(lines, facts)
    return finish_end(run, row, line, view, branch=branch)


def _resume_landing(run, rec, view, commit_key, landing):
    """end --resume of §4 step 1's landing cut off before its commit was saved: <landing>, the journal's pending, which
    on_move saved as end_commit just before <default> moved or was pushed. With an index.lock standing, nothing is
    applied or lifted: the journal is left for the next preflight's held stage, and the row is Locked. Where the move
    is verified (_verified: <default> holds the journalled commit, or, for a refspec push, origin/<default> does, after
    a fetch), the files are lifted and the journal entry and its ref removed (_finish) -- the paths split off it and
    held alone found again by its c1, the register moves its rebuild made read from the journal (JOURNAL_MOVES) --
    then the landing's outcome as at the end (_landing_end): steps 5-7, or the refspec push's row at once. Otherwise,
    with HEAD still on the stay's branch, the change is landed again from its journal (land's resume), never lifted
    unverified (P6); with HEAD off it -- on <default> or another branch -- the journal entry is dropped, nothing having
    moved and the files still in the working tree, and None is returned: the end goes on from step 1 as one whose HEAD
    moved off the branch it stayed on. A landing's journal is never finished by the here form."""
    lines, specs, state = run["lines"], run["specs"], run["state"]
    d = {k: rec.get(k) for k in ("default", "default_ref", "remote")}
    stay, head = rec.get("stay"), _head_branch(specs)
    if os.path.lexists(sb.git_paths(specs, "index.lock")[0][1]):
        line = lines.fill("row.locked", {}) + _appends(lines, _append_facts(specs, rec, head))
        return finish_end(run, "locked", line, run["view"], branch=head)
    if _verified(specs, landing, d["default"]):
        record = held_entries(specs)
        entry = next((e for e in record if e["c2"] == landing["c2"]), None)
        if entry is not None:
            _finish(specs, [entry], [entry["c2"]])
        stuck = next((e for e in record if e["c1"] == landing["c1"] and e["c2"] != landing["c2"]
                      and (e["refused"] or {}).get("permanent")), None)
        paths = _commit_paths(specs, landing["tip"])
        got = {"status": "landed", "sha": landing["tip"], "files": len(paths), "paths": paths, "refused": None,
               "pushed": bool(landing.get("remote_only")), "held_landed": [],
               "moves": list(landing.get(JOURNAL_MOVES) or []), "pending": landing,
               "stuck": None if stuck is None else {"sha": stuck["c2"], "paths": sorted(stuck["paths"]),
                                                    "refused": stuck["refused"]}}
    elif head is None or head != (stay or {}).get("branch"):
        _held_remove(specs, [landing["c2"]])
        rec["end_commit"] = None
        return None
    else:
        def on_move(pending):
            rec["end_commit"] = {"branch": d["default"], "landing": pending}
            state.save(run["session"], run["command"], rec)

        got = land(specs, head, d["default"], d["default_ref"],
                   session_subject(commit_key or rec.get("commit_key"), run["command"]), rec.get("start_dirty"),
                   rec.get("register_rebuild"), facts=_land_facts(stay, run["command"]), on_move=on_move,
                   resume=landing, retry_remote=False)
    return _landing_end(run, rec, d, stay, got, view)


def _end_session(run, saved, d, head, message, view, boundary):
    """specs-repo-git §4 steps 2-7 in session-branch mode (§8), on the checkout standing on <head>. With no identity
    (§8.1) the run commits nothing in the mode: the catch-up runs unwrapped, and the row is no-identity where session
    files are dirty (else nothing to commit). Otherwise step 2's catch-up runs inside lift and put-back (§8.3), a lift
    or put-back that could not run printed as end.session-not-run before the outcome line (§8's opening); step 4 is
    §8.2's commit, the session-not-run row where it could not run and nothing else of the run's committed. The run's
    commit is the last that committed among its commits -- a lift's unpreserved commit with step 4's message before the
    catch-up, and step 4's -- its file count every path they changed; none committed is nothing to commit, and a step 4
    that could not run after a lift's commit did is reported as end.session-not-run, that commit pushed. Just before the
    first of them the pending end_commit is saved (_landed_session reads it on --resume). A creation by any of them is
    the run's session_branch_created, saved at once; the last commit's sync, unsettled and stranded fill the
    appends."""
    state, lines, specs = run["state"], run["lines"], run["specs"]
    session_branch = saved["session_branch"]

    def ending(row, line, facts=None):  # a row that commits nothing: the block in the form run["view"] holds for it
        return finish_end(run, row, line + _appends(lines, _append_facts(specs, saved, head, facts)), run["view"],
                          branch=head)

    if session_branch is None:
        pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary)
        if pulled:
            run["pre"].append(pulled)
        row = "no-identity" if status(specs)["artifact"] else "nothing"
        return ending(row, lines.fill("row." + row, {}))

    def report(err):
        run["pre"].append(lines.fill("end.session-not-run", {"<the first line of its stderr>": err}))

    def created(base):
        saved["session_branch_created"] = base
        state.save(run["session"], run["command"], saved)

    def pending():
        if not saved.get("end_commit"):
            saved["end_commit"] = {"branch": session_branch, "base": sb.rev(specs, "refs/heads/" + session_branch),
                                   "session": {}}
            state.save(run["session"], run["command"], saved)

    sess = _Session(lines, specs, session_branch, d["default"], d["default_ref"], message, report, created)
    sess.before_commit = pending
    pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary, wrap=sess.wrap)
    if pulled:
        run["pre"].append(pulled)
    if not run["wrote"]:
        boundary()
    c, err = sess.commit()
    made = [x for x in sess.commits if x.get("committed")]
    if c is None and not made:
        return ending("session-not-run", lines.fill("row.session-not-run", {"<the first line of its stderr>": err}))
    if c is None:
        report(err)
    last = c or sess.commits[-1]
    facts = {"sync": last["sync"], "unsettled": last["unsettled"], "stranded": last["stranded"]}
    if not made:
        return ending("nothing", lines.fill("row.nothing", {}), facts)
    paths = _unique([p for x in made for p in x.get("paths") or []])
    commit = {"sha7": made[-1]["committed"][:7], "files": len(paths), "branch": session_branch, "paths": paths,
              "hook_paths": [], "session": facts}
    run["commit"] = commit
    saved["end_commit"] = commit
    state.save(run["session"], run["command"], saved)
    return _push_step(run, saved, commit, d["default"], view)


def classify_replay(result, error, partial, timed_out):
    """specs-repo-git §4 step 6's reading of a replay: the §6 row (replayed, already-there, moved or rejected), the
    <why> of a moved one, and reason, the id of the reason clause the row names -- refused.reason, not-run or
    timed-out -- else None. <result>: session-branch.py's JSON, None where it printed none; <error>: the first line
    of its stderr; <partial>: it exited 2 having printed its JSON first; <timed_out>: the harness ended the Bash call
    at its timeout. In step 6's order: a timeout, then an exit 2 with nothing printed, are push rejected, nothing
    said or nothing done; then the four cases -- pushed; not moved and refused; nothing replayed; else moved, its why
    the first that holds: stopped (<partial>, ahead of every other), later-refused (refused set), moved-on
    ([rejected] in porcelain), refused (a refusal in porcelain, as the first bullet of step 6 reads one: the caller
    writes the push-refusal record and renders the row's refused form), failed (any other porcelain, or none)."""
    if timed_out:
        return {"row": "rejected", "why": None, "reason": "timed-out"}
    if result is None:
        return {"row": "rejected", "why": None, "reason": "not-run"}
    refused = result.get("refused")
    if result.get("pushed"):
        return {"row": "replayed", "why": None, "reason": None}
    if not result.get("moved") and refused:
        return {"row": "rejected", "why": None, "reason": refused["reason"]}
    if not result.get("replayed"):
        return {"row": "already-there", "why": None, "reason": None}
    if partial:
        return {"row": "moved", "why": "stopped", "reason": None}
    if refused:
        return {"row": "moved", "why": "later-refused", "reason": refused["reason"]}
    summary = _summary(result.get("porcelain")) or ""
    if summary.startswith("[rejected]"):
        return {"row": "moved", "why": "moved-on", "reason": None}
    return {"row": "moved", "why": "refused" if _remote_refusal(summary) is not None else "failed", "reason": None}


def _reason_clause(lines, reason, refused, f, later=False):
    """specs-repo-git §6's reason clause for <reason>, <path> being <refused>'s path. <later>: inside app.why.later-refused,
    where checkout-moved reads `… so <branch> was not moved again; …`, an earlier attempt having moved it."""
    T, refused = lines.T, refused or {}
    t = T["reason." + reason]
    v = {"<branch>": f["branch"], "<SPECS_PATH>": f["specs"], "<path>": refused.get("path"),
         "<the first line of its stderr>": f.get("error")}
    if reason == "register-rebuild" and f.get("register_rebuild"):
        t = t[:t.index(", which only")] + T["reason.register-rebuild.failed"]
    elif reason == "would-overwrite":
        paths = refused.get("paths") or [refused.get("path")]
        v["<M>"] = len(paths) - 1 if len(paths) > 1 else None
    elif reason == "push-scope":
        v[lines.placeholder("reason.push-scope", "<path's")] = (refused.get("path") or "")[:7] or None
    elif reason == "checkout-moved" and later:
        t = _swap(t, "so <branch> was not moved;", T["app.why.checkout-moved"])
    return lines.fill(t, v)


def _register_clause(lines, moves):
    """specs-repo-git §6's register clause, once for each security/<slug>/ <moves> names, in their order, joined as the
    row's segment joins them; None where there is no move."""
    clauses = []
    for slug in _unique([m["slug"] for m in moves or []]):
        named = [lines.fill("app.register-move", {"<from>": m["from"], "<to>": m["to"], "<origin>": m["origin"],
                                                  "<whose number>": lines.T["app.register-move." + m["side"]]})
                 for m in moves if m["slug"] == slug]
        clauses.append(lines.fill("app.register-clause", {"<slug>": slug, "<move>": named}))
    return "; ".join(clauses) or None


def _why(lines, cls, result, f):
    """row.moved's <why>, as classify_replay named it (all but the refused form, which replaces the row's end)."""
    why = cls["why"]
    if why == "stopped":
        return lines.fill("app.why.stopped", {"<the first line of its stderr>": f.get("error")})
    if why == "later-refused":
        return lines.fill("app.why.later-refused", {
            "<reason clause>": _reason_clause(lines, cls["reason"], result.get("refused"), f, later=True)})
    if why == "moved-on":
        return lines.fill("app.why.moved-on", {"<branch>": f["branch"], "<attempts>": result.get("attempts")})
    return lines.fill("app.why.failed", {lines.placeholder("app.why.failed", "<the status line"):
                                         _summary(result.get("porcelain")) or lines.T["app.why.failed.none"]})


def _replay_sha7(cls, result, sha7):
    """<sha7> in a replay's row: the replay's tip in the three rows of a replay that moved the branch or found nothing
    left to push (specs-repo-git §6), else <sha7>, the run's own commit."""
    tip = (result or {}).get("tip")
    return tip[:7] if tip and cls["row"] != "rejected" else sha7


def _replay_line(lines, cls, result, f):
    """specs-repo-git §6's row for a replay classify_replay read as <cls>, from <result> (None where it printed none) and
    the facts <f>: sha7 and files (the run's commit), branch, specs (<SPECS_PATH> as the run holds it), default,
    standing (the branch the run stands on, whose remedy switches to <branch> first where they differ), register_rebuild
    (whether the call handed the replay one), error (session-branch.py's stderr line), preflight (§3.4's Specs
    preflight: form, by lines.preflight_form, which drops the opening's <sha7> and <N>), and, for the refused form,
    reason, record, record_kind and record_error as _record_refusal wrote the record, with mode_on and identity where
    it names the default branch outside the mode (_row_line). session_branch: where the reason is reason.session-mode,
    the session branch whose lift and put-back wrap the remedy (§6), the remedy left unwrapped where there is none."""
    T, result, row = lines.T, result or {}, cls["row"]
    t = T["row." + row]
    sha7, files = _replay_sha7(cls, result, f.get("sha7")), f.get("files")
    if f.get("preflight"):  # the opening the Specs preflight: form drops: neither value is printed
        sha7, files = sha7 or "-", 0 if files is None else files
    v = {"<sha7>": sha7, "<N>": files, "<branch>": f["branch"], "<SPECS_PATH>": f["specs"], "<default>": f.get("default")}
    tail = ""
    if row != "rejected":
        replayed, dropped = result.get("replayed") or [], result.get("dropped") or []
        v.update({"<K>": len(replayed) + len(dropped), "<D>": len(dropped) or None,
                  "<the register clause>": _register_clause(lines, result.get("moves"))})
    if row == "replayed" and result.get("upstream_error"):
        tail = lines.fill("app.upstream-error", {"<upstream_error>": result["upstream_error"]})
    elif row == "moved" and cls["why"] == "refused":  # from "but" on: row.moved.refused, then push-refused's own end
        t = t[:t.index("but <why>")] + T["row.moved.refused"]
        v["<the reason in parentheses>"] = f["reason"]
        refused_row = _row_line(lines, "push-refused", dict(f, sha7=sha7, files=files))
        tail = refused_row[refused_row.index("a rule there"):]
    elif row == "moved":
        v["<why>"] = _why(lines, cls, result, f)
    elif row == "rejected":
        refused, remedy = result.get("refused"), T["remedy.rejected"]
        v["<reason clause>"] = _reason_clause(lines, cls["reason"], refused, f)
        if cls["reason"] == "checkout-moved":  # the line ends at its reason clause
            t = t[:t.index("; " + remedy)]
        else:
            new = remedy
            if cls["reason"] == "checked-out":  # run in that worktree, no switch
                new = T["remedy.checked-out"]
                v["<path>"] = refused["path"]
            elif f.get("standing") != f["branch"]:
                new = T["remedy.not-standing"]
                v["<the branch the run stands on>"] = f.get("standing")
            if cls["reason"] == "session-mode" and f.get("session_branch"):  # the overlay's lift and put-back around it
                new = _swap(T["remedy.session-wrap"], "<the remedy as it reads without this wrapping, from its first git on>",
                            new[len("run "):])
                v.update({"<the script's path>": SB_SCRIPT, "<identity>": _identity(f["session_branch"])})
            if new != remedy:
                t = _swap(t, remedy, new)
    line = lines.fill(t, v) + tail
    return lines.preflight_form(line) if f.get("preflight") else line


def _sb_stderr(e):
    """The one line session-branch.py's main() prints on stderr for <e>, which specs-repo-git §4 step 6 quotes: the
    replay runs here in process, and its exits are read as that script's would be."""
    said = " ".join(str(e).split())
    if isinstance(e, (NotRun, OSError)):
        return "session-branch: not run (%s)" % said
    return "session-branch: not run (%s: %s)" % (type(e).__name__, said)


# The words session-branch.py raises a replay a signal ended with, matched whole: git_bounded's, for the fetch or push
# it ended, and replay's own, for a signal it acted on between calls (whose _Signalled is also the cause).
_ENDED_BY = re.compile(r"(?:git \S+ )?ended by signal ([0-9]+)")


class _Ended(BaseException):
    """A signal ended the replay this call ran: no outcome. A BaseException, so no handler of an outcome takes it."""

    def __init__(self, signum):
        BaseException.__init__(self, signum)
        self.signum = signum


def _signal_of(e):
    """The signal that ended sb.replay's call, where one did, else None: a _Signalled on <e> or as its cause (replay
    raises it as NotRun, or as Partial once the branch moved, from it); else either of _ENDED_BY's two forms, whole, on
    <e> or on the cause a Partial carries -- git_bounded gives the number in its words alone."""
    for x in (e, e.__cause__):
        if isinstance(x, sb._Signalled):
            return x.args[0]
        m = _ENDED_BY.fullmatch(str(x)) if isinstance(x, NotRun) else None
        if m:
            return int(m.group(1))
    return None


def _exit_by(signum):
    """End this process by <signum>, as that signal's default action would have, printing nothing."""
    sys.stdout.flush()
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)
    sys.exit(128 + signum)  # where the signal did not end it at once


def _run_replay(specs, branch, register_rebuild, set_upstream, timed_out):
    """sb.replay in process, unless the harness ended the call that ran it: (result, error, partial) as classify_replay
    takes them -- a Partial its result and its line, any other exception no result and its line. A replay a signal
    ended is no outcome: the harness that sent it, at its timeout, has already set aside what this call would print,
    and runs the --timed-out call, which needs the record as it stands; so _Ended is raised, and nothing is rendered or
    recorded."""
    if timed_out:
        return None, None, False
    try:
        return sb.replay(specs, branch, register_rebuild, set_upstream), None, False
    except Exception as e:  # session-branch.py's main() prints any exception as its one not-run line
        signum = _signal_of(e)
        if signum is not None:
            raise _Ended(signum)
        if isinstance(e, sb.Partial):
            return e.result, _sb_stderr(e), True
        return None, _sb_stderr(e), False


def _replay_facts(run, rec, cls, result, error, branch, standing, preflight):
    """The facts _replay_line renders from; where classify_replay found a refusal in porcelain, the push-refusal record
    written first, as specs-repo-git §4 step 6's first bullet writes it, and, on the default branch outside the mode,
    the facts of the remedy that says the mode turns on (§6's moved, not pushed row, its variants included)."""
    commit = run.get("commit") or {}
    f = {"sha7": commit.get("sha7"), "files": commit.get("files"), "branch": branch, "specs": run["specs"],
         "default": rec.get("default"), "standing": standing, "register_rebuild": bool(rec.get("register_rebuild")),
         "error": error, "preflight": preflight}
    if cls["why"] == "refused":
        written = _record_refusal(run["specs"], branch)
        f.update(reason=_remote_refusal(_summary(result.get("porcelain"))), record=written["record"],
                 record_kind=written["recorded"], record_error=written["record_error"])
        f.update(_mode_on_facts(run["specs"], rec.get("mode"), branch, rec.get("default")))
    return f


def replay(specs, for_, command, branch, set_upstream=False, timed_out=False):
    """specs-repo-git §4 step 6's replay for the run of this session and <command>, in a call of its own: sb.replay of
    <branch> in process (unless <timed_out>), with the register_rebuild the record holds, read by classify_replay and
    rendered as its §6 row. <for_> end: end's object for the end_commit the record holds, every append end gives, the
    record removed. <for_> start: {print: [the row in its Specs preflight: form], next, error}, the record advanced --
    from flush (the current branch's replay) to settle, next naming start --resume; at settle-done, <branch> dropped
    from pending, next naming the next queued replay, or, none left, start --resume with the record at disposition.
    Exit 2 only before the record is found; after it, an exception is exit-0 JSON with error set and the stopped
    line, the record kept as it stood -- which is how a record with nothing for this call to replay is refused. A
    replay a signal ended prints nothing and leaves the record as it stood for the --timed-out call: the process ends
    by that signal (_exit_by)."""
    state, lines = _flow()
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    session = state.session_id()
    rec = state.load(session, command)
    if rec is None:
        raise NotRun("no record of %s in this session holds a replay" % command)
    run = {"state": state, "lines": lines, "specs": specs, "session": session, "command": command, "record": "found",
           "pre": [], "commit": None}
    try:
        if for_ == "end":
            return _replay_end(run, rec, branch, set_upstream, timed_out)
        return _replay_start(run, rec, branch, set_upstream, timed_out)
    except _Ended as e:
        _exit_by(e.signum)
    except Exception as e:
        said = " ".join(str(e).split())
        error = said if isinstance(e, NotRun) else type(e).__name__ + (": " + said if said else "")
        if for_ == "start":
            return {"print": [lines.fill("pre.stopped", {"<the error>": error})], "next": None, "error": error}
        line = lines.fill("end.stopped", {"<the error>": error})
        commit = run["commit"] or {}
        landing = (rec.get("end_commit") or {}).get("landing")
        # §6: a G1 or G2 block follows the outcome line, this one too, in the form §5 gives an early stop
        block = _end_view(lines, rec, _view(rec), rec.get("default"), specs, rec.get("stay") if landing else None,
                          False)["guard_block"]
        return _end_result(print=[line] + ([block] if block else []), line=line, sha7=commit.get("sha7"),
                           files=commit.get("files"), branch=commit.get("branch"), record="found", error=error)


def _replay_end(run, rec, branch, set_upstream, timed_out):
    """replay --for end: the replay of the commit end made and saved as end_commit at stage end-replay. A pending
    end_commit (no sha7: end stopped between staging and its commit) is end --resume's, and is refused. A commit §4
    step 1's landing made on <default> takes the landing's appends (_landing_append) and G1's landing form, and the
    branch the run stands on is the stayed one, so the rejected row's remedy switches first."""
    lines = run["lines"]
    commit = rec.get("end_commit") or {}
    if rec.get("stage") != "end-replay" or not commit.get("sha7") or commit.get("branch") != branch:
        raise NotRun("the record holds no commit of %s that end handed to a replay; end --resume finishes this run"
                     % branch)
    run["commit"] = commit
    landing = commit.get("landing") if isinstance(commit.get("landing"), dict) else None
    stay = rec.get("stay") if landing else None
    result, error, partial = _run_replay(run["specs"], branch, rec.get("register_rebuild"), set_upstream, timed_out)
    cls = classify_replay(result, error, partial, timed_out)
    f = _replay_facts(run, rec, cls, result, error, branch, (stay or {}).get("branch") or branch, False)
    shown = dict(commit, sha7=_replay_sha7(cls, result, commit["sha7"]))
    line = (_replay_line(lines, cls, result, f) + _landing_append(lines, commit, rec)
            + _appends(lines, _append_facts(run["specs"], rec, branch)))
    view = _end_view(lines, rec, _view(rec), rec.get("default"), run["specs"], stay, not (landing or {}).get("stuck"))
    return finish_end(run, cls["row"], line, view, commit=shown, branch=branch, pushed=cls["row"] == "replayed")


def _replay_start(run, rec, branch, set_upstream, timed_out):
    """replay --for start: §3.4's replay of the current branch (stage flush, <branch> the one HEAD stands on, which
    the flush pushed -- tested save under <timed_out>, which moves no branch and renders the 420 s row from the record
    alone, so a checkout another session switched during the replay the harness ended still lets start go on), or of
    a branch the settle loop queued (stage settle-done, <branch> in pending, whose standing names the branch the run
    stands on)."""
    state, stage, pending = run["state"], rec.get("stage"), list(rec.get("pending") or [])
    if stage == "flush" and (timed_out or branch == _head_branch(run["specs"])):
        standing = branch
    elif stage == "settle-done" and any(p.get("branch") == branch for p in pending):
        standing = next(p for p in pending if p.get("branch") == branch).get("standing")
    else:
        raise NotRun("the record (stage %s) holds no replay of %s" % (stage, branch))
    result, error, partial = _run_replay(run["specs"], branch, rec.get("register_rebuild"), set_upstream, timed_out)
    cls = classify_replay(result, error, partial, timed_out)
    line = _replay_line(run["lines"], cls, result, _replay_facts(run, rec, cls, result, error, branch, standing, True))
    if stage == "flush":  # the settle loop computes its branches on entering, past the HEAD this replay moved
        rec["stage"], rec["settle_todo"] = "settle", None
    else:
        rec["pending"] = [p for p in pending if p.get("branch") != branch]
        rec["stage"] = "settle-done" if rec["pending"] else "disposition"
    state.save(run["session"], run["command"], rec)
    if stage == "settle-done" and rec["pending"]:
        nxt = _queued_next(run, rec)
    else:
        nxt = _resume_next(run["command"], rec.get("args") or {}, rec.get("budget"))
    return {"print": [line], "next": nxt, "error": None}


# start's budget: the seconds one call may spend, inside the 600 s Bash call the skill runs it in, and what each unit of
# capped calls may take -- each call's cap, and the KILL_AFTER seconds git_bounded gives its process group after it.
DEFAULT_BUDGET = 480
FETCH_COST = CAP + sb.KILL_AFTER
PULL_COST = CAP + sb.KILL_AFTER
PUSH_COST = LS_REMOTE_CAP + sb.KILL_AFTER + CAP + sb.KILL_AFTER  # push_check's ls-remote, then the push
FLUSH_COST = PULL_COST + PUSH_COST  # §3.4: the catch-up's pull or the merged-branch leave's, then the current branch's push
# The record's stages start goes on from, in order; done follows the last.
START_STAGES = ("fetch", "guards", "flush", "settle", "settle-done", "disposition")


class _Stop(Exception):
    """start's budget: the next unit of capped calls could cross it, so the call returns next naming start --resume."""


class _Budget:
    """One start call's budget: a unit of capped calls goes ahead where it is the call's first, or where the time the
    call has spent plus the unit's caps stays inside <seconds>; otherwise _Stop. So every call makes at least one."""

    def __init__(self, seconds):
        self.seconds, self.t0, self.made = seconds, time.monotonic(), False

    def check(self, cost):
        if self.made and time.monotonic() - self.t0 + cost > self.seconds:
            raise _Stop()
        self.made = True


def _emit(run, line):
    run["print"].append(line)


def _save(run):
    run["state"].save(run["session"], run["command"], run["rec"])


def _advance(run, stage):
    run["rec"]["stage"] = stage
    _save(run)


def _g1_block(lines, specs, paths):
    """specs-repo-git §5's G1 block for the OTHER <paths>: <path list> comma-separated on the Found line, shell-quoted
    and space-separated on the Fix line, where it is pasted into a command."""
    return lines.fill("g1", {"<SPECS_PATH>": specs, "<N>": len(paths),
                             "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})


def _g1_landing(lines, block, branch, default, specs, paths, stay, midrun, committed=None):
    """specs-repo-git §5's form of G1's plain <block> -- as rendered for <specs> and the OTHER <paths> -- on a branch
    the run would have left, or under a run typed mid-run, each part replaced unwrapped on its one line, its Found line
    its own. Where <midrun> (the record's: the open run) is set, the mid-run form, whatever the stay's kind and flag
    (P25): Not done g1.landing.not_done's mid-run alternative where the run stays on <branch> (<stay>), else the plain
    block's; an empty Fix, since no switch or commit is to be run while the open run stands there; If ignored
    g1.midrun.if_ignored, naming the open run's command. Otherwise, where <stay> is set, the landing form: Not done
    g1.landing.not_done, the alternative the stay's kind selects (STAY_KINDS); where its merged flag is set,
    g1.merged.fix -- switching to <default> first, so the user's files are not committed on <branch>, which would make
    it read unmerged -- and g1.merged.if_ignored, else the plain Fix and g1.landing.if_ignored. Neither: <block>.
    <committed> is the start's None, or, as the run's end repeats the block (§5), whether the end committed the run's
    whole change -- its landing landed it, no path held alone, or, with no stay, its commit was made: where False, the
    Not done is g1.landing.not_done.unlanded with a stay and g1.not_done.uncommitted without one, the mid-run form's
    included; with neither a stay nor a run typed mid-run, the If ignored is g1.if_ignored.uncommitted too (the
    not-committed form), and otherwise the Fix and If ignored are as they are."""
    kind = lines.placeholder("g1.landing.not_done", "<which no key")
    v = {"<branch>": branch, "<default>": default, "<SPECS_PATH>": specs,
         "<path list>": " ".join(shlex.quote(p) for p in paths)}
    landing = "g1.landing.not_done.unlanded" if committed is False else "g1.landing.not_done"
    if midrun:
        v["<command>"] = midrun.get("command")
        if stay:
            block = _block_part(block, "Not done:", lines.fill(landing, dict(v, **{kind: STAY_KINDS.index("mid-run")})))
        elif committed is False:
            block = _block_part(block, "Not done:", lines.T["g1.not_done.uncommitted"])
        block = _block_part(block, "Fix:", "")
        return _block_part(block, "If ignored:", lines.fill("g1.midrun.if_ignored", v))
    if not stay:
        if committed is not False:
            return block
        block = _block_part(block, "Not done:", lines.T["g1.not_done.uncommitted"])
        return _block_part(block, "If ignored:", lines.T["g1.if_ignored.uncommitted"])
    v["<command>"] = stay.get("command")
    block = _block_part(block, "Not done:", lines.fill(landing, dict(v, **{kind: STAY_KINDS.index(stay["kind"])})))
    if stay.get("merged"):
        block = _block_part(block, "Fix:", lines.fill("g1.merged.fix", v))
        return _block_part(block, "If ignored:", lines.fill("g1.merged.if_ignored", v))
    return _block_part(block, "If ignored:", lines.T["g1.landing.if_ignored"])


def _stayed_on(rec, branch):
    """Whether the record <rec> holds a stay on <branch> (specs-repo-git §4 step 1)."""
    return branch is not None and (rec.get("stay") or {}).get("branch") == branch


def _may_stay(rec, head):
    """Whether a stay can name HEAD's branch <head> (specs-repo-git §4 step 1): a plugin branch other than the default
    branch, outside session-branch mode, where the session files never commit on HEAD (§8.2), and never under
    misrooted, where commit-artifacts commits nothing."""
    return (head is not None and head != rec.get("default") and branch_key(head, [])["plugin_branch"]
            and rec.get("mode") != "on" and rec.get("specs_git") != "misrooted")


def _run_keys(rec, extra_keys=()):
    """The keys a branch is resolved against for §3.5's B3 and B4, a re-run's switch back, and a stay's kind: the run
    key set, the start's commit key and <extra_keys> (the end's commit key), none of them None."""
    return [k for k in list(rec.get("keys") or []) + [rec.get("commit_key"), *extra_keys] if k]


def _stay_kind(rec, head, merged, extra_keys=()):
    """The kind (STAY_KINDS) of the stay the record <rec> keeps on HEAD's branch <head>, which branch-merged read
    <merged>, where the preflight stays there though it would have left it (specs-repo-git §4 step 1); None where no
    stay can name it (_may_stay). Where <merged>, B2's branch: mid-run under a run typed mid-run (§3.5), else merged.
    Else None where branch-key resolves <head> to a key of the run key set, the start's commit key or <extra_keys> (the
    end's commit key) -- B3's branch, the run's own -- and otherwise B4's: mid-run under a run typed mid-run, else
    unkeyed. A key that is None is never one."""
    if not _may_stay(rec, head):
        return None
    if merged:
        return "mid-run" if rec.get("midrun") else "merged"
    if branch_key(head, _run_keys(rec, extra_keys))["key"]:
        return None
    return "mid-run" if rec.get("midrun") else "unkeyed"


def _stay_record(rec, branch, kind, reason, merged):
    """A stay's value (specs_git_state's stay): <branch>, <kind> (STAY_KINDS), <reason> (STAY_REASONS), the merged flag
    <merged>, and command, the open run's where the run was typed mid-run (§3.5), else None."""
    return {"branch": branch, "kind": kind, "reason": reason, "merged": bool(merged),
            "command": (rec.get("midrun") or {}).get("command")}


def _stay(run, branch, kind, reason, merged):
    """Keep <branch> as the run's stay (specs-repo-git §4 step 1), of <kind> (_stay_kind's), with <reason>
    (STAY_REASONS) and the merged flag <merged>. Saved at once, so a kill before the record's next save keeps it --
    the flush's commit after a refused leave, among them, which makes the branch read unmerged."""
    run["rec"]["stay"] = _stay_record(run["rec"], branch, kind, reason, merged)
    _save(run)


def _keep_stay(run, branch, merged, reason):
    """Where the preflight stays on <branch>, which branch-merged read <merged>, though it would have left it: the
    stay _stay_kind gives, kept with <reason>; none where it gives none."""
    kind = _stay_kind(run["rec"], branch, merged)
    if kind is not None:
        _stay(run, branch, kind, reason, merged)


def _ask_stay(run, head, reason):
    """specs-repo-git §3.3's G1, and a preflight that stops early (§1 rule 5): where a stay can name HEAD's branch
    <head> (_may_stay), ask branch-merged HEAD -- a read that moves nothing, which _merged reports once where it cannot
    answer, the branch then reading unmerged -- and keep the stay its answer and the run's keys give (_keep_stay), with
    <reason>."""
    if _may_stay(run["rec"], head):
        _keep_stay(run, head, _merged(run, "HEAD", head)["merged"], reason)


def _block_part(block, label, text):
    """<block> with the part <label> opens -- its line from the label on, and the indented lines that continue it --
    replaced by the label, the padding its line gives it, and <text>, unwrapped on one line; an empty <text> (a Fix
    part with nothing to run, or nothing it can give ready to paste, specs-repo-git §5) leaves the label alone, with no
    padding after it. ValueError where <block> has no such part: it is not a block §5 renders."""
    rows = block.split("\n")
    i = next((k for k, row in enumerate(rows) if row.startswith(label)), None)
    if i is None:
        raise ValueError("_block_part: the block has no %s part" % label)
    j = i + 1
    while j < len(rows) and rows[j].startswith(" "):
        j += 1
    pad = re.match(re.escape(label) + " *", rows[i]).group(0)
    return "\n".join(rows[:i] + [(pad + text).rstrip()] + rows[j:])


def _g2_block(lines, specs, branch, default, variant=None, values=None):
    """specs-repo-git §5's G2 block for <branch>; with <variant> (implement: a direct /implement run from inside the
    specs repository; session and self: session-branch mode, on another branch or on the session branch itself, their
    <identity> in <values>; no-identity: session-branch mode where §8.1 resolves no identity), its Not done, Fix and If
    ignored parts are the g2.<variant>.* prose SRG gives in their place, each unwrapped on its one line. The mode's
    variants take precedence over implement (§5)."""
    block = lines.T["g2"]
    if variant:
        for label, part in (("Not done:", "not_done"), ("Fix:", "fix"), ("If ignored:", "if_ignored")):
            block = _block_part(block, label, lines.T["g2.%s.%s" % (variant, part)])
    return lines.fill(block, dict({"<SPECS_PATH>": specs, "<branch>": branch, "<default>": default}, **(values or {})))


def _inside(top):
    """Whether the current directory is in the work tree whose top level is <top>: a direct /implement run from inside
    the specs repository (specs-repo-git §5)."""
    try:
        here = _git_line(os.getcwd(), "--show-toplevel")
    except OSError:
        return False
    return bool(here and top) and os.path.realpath(here) == os.path.realpath(top)


def _once(run, key, tid, values):
    """A report specs-repo-git prints once in a run however many asks give it: template <tid> filled with <values>,
    printed unless the record's reported list holds <key>, which it then does -- so neither a resume after a budget
    stop nor a --rerun, which carries the list, prints it again."""
    rec = run["rec"]
    if key not in rec["reported"]:
        rec["reported"].append(key)
        _emit(run, run["lines"].fill(tid, values))


def _stderr(e):
    """The one line an entry point's CLI prints on stderr for <e>, which specs-repo-git's reports quote."""
    return "specs-git: not run (%s)" % " ".join(str(e).split())


def _merged(run, ref, branch):
    """branch_merged of <ref>, the branch <branch> or HEAD standing on it, against the record's default ref. Where it
    cannot answer -- a default ref that does not resolve among the causes, as on an origin that holds no default
    branch yet -- specs-repo-git §3.5's report, pre.merged-unknown, once for <branch> in a run; the branch is then
    read unmerged, the answer that never deletes it."""
    rec = run["rec"]
    try:
        if not rec["default_ref"]:
            raise NotRun("the default branch has no ref to test against")
        return branch_merged(run["specs"], ref, rec["default_ref"])
    except NotRun as e:
        _once(run, "pre.merged-unknown " + branch, "pre.merged-unknown",
              {"<branch>": branch, "<the first line of its stderr>": _stderr(e)})
        return {"merged": False, "test": None}


def _status(run):
    """status() of the checkout; where it cannot run, specs-repo-git §2.1's report, pre.status-failed, once in a run,
    and None: G1 then has no path to find and the flush stages nothing, and the preflight goes on."""
    try:
        return status(run["specs"])
    except NotRun as e:
        _once(run, "pre.status-failed", "pre.status-failed", {"<the first line of its stderr>": _stderr(e)})
        return None


def _scope(run, branch):
    """push_scope() of <branch> -- §8.4's form for the session branch in session-branch mode; where it cannot run, §4
    step 5's report, pre.scope-failed, once for <branch> in a run, and None: nothing is pushed, B4 names no count, and
    the preflight goes on."""
    rec = run["rec"]
    session = rec.get("mode") == "on" and branch == rec.get("session_branch")
    try:
        return push_scope(run["specs"], branch, rec["default_ref"] if session else None)
    except NotRun as e:
        _once(run, "pre.scope-failed " + branch, "pre.scope-failed",
              {"<branch>": branch, "<the first line of its stderr>": _stderr(e)})
        return None


def _d_sees(root, branch):
    """specs-repo-git §3.4: whether `branch -d` can see <branch> merged from here -- its upstream, where that ref
    exists, holds its tip; else HEAD does."""
    up = sb.text(sb.git(root, "for-each-ref", "--format=%(upstream)", "refs/heads/" + branch))
    into = up if up and sb.rev(root, up) else "HEAD"
    return sb.git(root, "merge-base", "--is-ancestor", "refs/heads/" + branch, into, check=False).returncode == 0


def _remove_refusal(root, branch):
    """specs-repo-git §1 rule 8: a deleted branch's push-refusal record goes with it -- the file, and the configuration
    key where .git/config can be written (branch -d removed its section there already where it could)."""
    path = sb.refusal_path(root, branch)
    if path:
        try:
            os.remove(path)
        except OSError:
            pass
    key = "branch.%s.workflowsPushRefused" % branch
    if sb.config(root, key) is not None:
        sb.git(root, "config", "--unset", key, check=False)


def _rm_line(run, branch):
    """B2's `rm -f "<record>"`, after a -D line, where <branch>'s push-refusal record file stands: branch -D, unlike -d
    here, does not take the record with it."""
    path = sb.refusal_path(run["specs"], branch)
    if path and os.path.isfile(path):
        _emit(run, run["lines"].fill("pre.advisory-D.rm", {"<record>": path}))


def _delete(run, branch, test=None):
    """`branch -d <branch>`, never -D (specs-repo-git §3.4, and §3.5's B2 with <test>, the branch-merged test that
    answered). Where it deleted the branch -- exit 0, or the branch gone, as git leaves it where it could not write
    .git/config -- the push-refusal record removed, pre.deleted, and pre.b2-config where the branch's configuration
    still stands. Otherwise pre.delete-failed; for B2 on a branch merged by its second, third or fourth test, then
    pre.b2-squash and the record's rm, the branch recorded in advised_D so the run gives the -D line once. Whether
    the branch was deleted."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    r = sb.git(specs, "branch", "-d", branch, check=False)
    if r.returncode != 0 and sb.rev(specs, "refs/heads/" + branch) is not None:
        _emit(run, lines.fill("pre.delete-failed", {"<branch>": branch, "<git's first error line>": _first_line(r, error=True)}))
        if test in (2, 3, 4):
            _emit(run, lines.fill("pre.b2-squash", {"<branch>": branch, "<default>": rec["default"], "<SPECS_PATH>": specs}))
            _rm_line(run, branch)
            if branch not in rec["advised_D"]:
                rec["advised_D"].append(branch)
        return False
    _remove_refusal(specs, branch)
    _emit(run, lines.fill("pre.deleted", {"<branch>": branch}))
    if sb.config(specs, "branch.%s.merge" % branch) or sb.config(specs, "branch.%s.workflowsPushRefused" % branch):
        _emit(run, lines.fill("pre.b2-config", {"<branch>": branch, "<SPECS_PATH>": specs}))
    return True


def _refused_line(lines, specs, branch, default, p, extra=None):
    """specs-repo-git §4 step 6's refusal inside §3.4, for push()'s result <p>: pre.refused, with the remedy §6's push
    refused row gives -- what follows its `no later run pushes it; ` -- in the form <extra>'s facts give it (the session
    branch's, or the one that says the mode turns on: _row_line); or, where the refusal could be recorded neither way,
    its unrecorded form, which names no remedy."""
    T = lines.T
    v = {"<branch>": branch, "<the reason in parentheses>": p["reason"]}
    if p["recorded"] is None:
        t = T["pre.refused"]
        return lines.fill(t[:t.index(", and this is recorded")] + T["pre.refused.unrecorded"],
                          dict(v, **{"<error>": p["record_error"]}))
    row = _row_line(lines, "push-refused", dict({"sha7": "-", "files": 0, "branch": branch, "default": default,
                                                 "specs": specs, "reason": p["reason"], "record": p["record"],
                                                 "record_kind": p["recorded"], "record_error": p["record_error"]},
                                                **(extra or {})))
    opening = "no later run pushes it; "
    v["<the remedy §6's push-refused line gives>"] = row[row.index(opening) + len(opening):]
    return lines.fill("pre.refused", v)


def _session_rejected_preflight(lines, branch, default, sync):
    """specs-repo-git §3.4: the session branch <branch>'s push-rejected row in its Specs preflight: form, and, where
    <sync> (the flush's commit's) gives a conflict the source origin/<branch> -- where the row takes its conflict
    ending -- §6's clause for those paths after it, the clause that ending points at."""
    row = _row_line(lines, "rejected", {"sha7": "-", "files": 0, "branch": branch, "session_branch": branch, "sync": sync})
    v = {"<identity>": _identity(branch), "<default>": default}
    return lines.preflight_form(row) + _conflict_clause(lines, "app.session.conflict-origin", "origin/" + branch, sync, v)


def _push(run, branch, sync=None):
    """specs-repo-git §4 steps 5-6 for <branch> inside §3.4: push_check, its conditions in step 5's order and
    push-scope last, measured by _scope, which reports where it cannot run; then the push. A condition that fails,
    and a push that lands, print nothing here; a refusal and a failure print their Specs preflight: forms. The outcome
    (held where a condition failed or push-scope could not run) and set_upstream, which a rejected push's replay
    repeats. In session-branch mode nothing is replayed (§4 step 6): a rejection of the session branch prints its
    push-rejected row in its Specs preflight: form -- with the conflict ending, followed by §6's clause for origin's
    copy, where <sync>, the flush's commit's, names that source (§3.4) -- and one of a plugin branch prints push
    rejected with reason.session-mode and its remedy wrapped
    in the session branch's lift and put-back; either is outcome unreplayed, which queues and names no replay."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    in_mode = rec.get("mode") == "on"
    sbranch = rec.get("session_branch") if in_mode else None
    check = push_check(specs, branch, rec["default"], session_branch=sbranch, default_ref=rec["default_ref"],
                       measure=lambda root, b: _scope(run, b))
    if check["row"] is not None:
        return {"outcome": "held", "set_upstream": False}
    p = push(specs, branch, check["set_upstream"])
    session = sbranch is not None and branch == sbranch
    if p["outcome"] == "refused":
        extra = {"session_branch": branch} if session else _mode_on_facts(specs, rec.get("mode"), branch, rec["default"])
        _emit(run, _refused_line(lines, specs, branch, rec["default"], p, extra))
    elif p["outcome"] == "failed":
        _emit(run, lines.preflight_form(_row_line(lines, "failed", {"sha7": "-", "files": 0, "branch": branch,
                                                                    "reason": p["reason"]})))
    elif p["outcome"] == "rejected" and in_mode:
        f = {"sha7": "-", "files": 0, "branch": branch, "specs": specs, "default": rec["default"],
             "standing": _head_branch(specs), "register_rebuild": False, "error": None, "preflight": True}
        if session:
            _emit(run, _session_rejected_preflight(lines, branch, rec["default"], sync))
        else:
            _emit(run, _replay_line(lines, {"row": "rejected", "why": None, "reason": "session-mode"}, None,
                                    dict(f, session_branch=sbranch)))
        return {"outcome": "unreplayed", "set_upstream": check["set_upstream"]}
    return {"outcome": p["outcome"], "set_upstream": check["set_upstream"]}


def _pulls(rec):
    """Whether B2's and B4's move pulls: where <default-ref> is origin/<default> (specs-repo-git §3.5, as the catch-up
    in §3.4 names it); with no origin there is nothing to pull."""
    return bool(rec["default"]) and rec["default_ref"] == "origin/" + rec["default"]


def _session(run):
    """start's _Session where specs-repo-git §8.3 wraps the moves: session-branch mode on with a session branch, never
    under misrooted; else None, every move then unwrapped -- with no identity, as §8.1 says. A call that could not run
    prints pre.session-not-run; a creation by a commit made here is saved as session_branch_created (§8.2)."""
    rec, lines = run["rec"], run["lines"]
    if rec.get("mode") != "on" or not rec.get("session_branch") or rec.get("specs_git") == "misrooted":
        return None

    def report(err):
        _emit(run, lines.fill("pre.session-not-run", {"<the first line of its stderr>": err}))

    def created(base):
        rec["session_branch_created"] = base
        _save(run)

    return _Session(lines, run["specs"], rec["session_branch"], rec["default"], rec["default_ref"],
                    session_subject(rec["commit_key"], run["command"]), report, created)


def _closing_put_back(run):
    """specs-repo-git §8.3: the preflight ends with put-back in session-branch mode, whether or not it moved the
    checkout and where a guard ended it, never under misrooted -- here, where start's stages reach done (a guard
    included) or a call stops on an error. Not at a budget stop: that is a boundary between calls, not the preflight's
    end, and none falls between a lift and its put-back -- the budget is checked before each wrapped move's lift, and
    each lift's put-back runs in the same call -- so at every call's return the overlay stands as the last put-back,
    or the run before it, left it."""
    sess = _session(run)
    if sess is not None and run["rec"].get("gate") == "pass":
        sess.put_back()


def _to_default(run, branch, field):
    """B2's and B4's move (specs-repo-git §3.5), which §3.4's merged-branch leave also makes outside session-branch
    mode: switch to the default branch, <field> (b2_left or b4_left) saved as <branch>, then `pull --ff-only --no-rebase
    origin <default>` where _pulls holds, its pre.pull-failed line printed where it fails. git's first error line where
    it refused the switch, nothing moved; else None. In session-branch mode with a session branch this is the one place
    B2's and B4's switch and pull are wrapped in lift and put-back (§8.3, _Session.wrap), the caller's budget checked
    before it; a second unpreserved skips the move, which returns text.lift-unpreserved in place of git's first error
    line, so the step reports it as it would a refused switch (§8.3). With no identity the move runs unwrapped
    (§8.1). A switch that leaves the branch a stay names clears that stay (§4 step 1)."""
    rec, specs = run["rec"], run["specs"]

    def move():
        r = sb.git(specs, "switch", rec["default"], check=False)
        if r.returncode != 0:
            return _first_line(r, error=True)
        rec[field] = branch
        if _stayed_on(rec, branch):
            rec["stay"] = None
        _save(run)
        if _pulls(rec):
            pulled = _pull_line(specs, rec["default"])
            if pulled:
                _emit(run, pulled)
        return None

    sess = _session(run)
    return move() if sess is None else sess.wrap(move)[1]


def _leave(run, branch, test, merged_flush=False):
    """B2's action (specs-repo-git §3.5), which §3.4 also runs to leave a merged branch before its flush
    (<merged_flush>, outside session-branch mode only): _to_default, then `branch -d`. Where git refuses the switch,
    the branch, which both read merged, is kept as the run's stay (§4 step 1, _keep_stay), and §3.4's leave prints
    pre.leave-failed and returns False, its flush going on from the branch. In §3.5 a refused
    switch stops the call (rule 5's pre.stopped), SRG wording no line for it. Where §3.5 reaches this, the session files
    are still dirty only where the flush's commit was Locked or failed, and git can then refuse to carry them -- an
    index.lock refuses every switch -- or, in session-branch mode, where the overlay holds them, which _to_default's
    lift returns to HEAD first. §3.5 can also meet them dirty where status could not run, the dirty set unknown, and
    under misrooted, where §3.4 does not run; §3.5 switches nothing in either (_disposition), so neither reaches this."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default = rec["default"]
    why = _to_default(run, branch, "b2_left")
    if why is not None:
        _keep_stay(run, branch, True, "refused")
        if not merged_flush:
            raise NotRun("git switch %s: %s" % (default, why))
        _emit(run, lines.fill("pre.leave-failed", {"<branch>": branch, "<default>": default,
                                                   "<git's first error line>": why}))
        return False
    _delete(run, branch, test)
    _save(run)
    return True


def _b4(run, branch):
    """B4's action (specs-repo-git §3.5): _to_default, then the report of the branch left, with the count of commits
    on it a push would publish where there are any. A refused switch stops the call, as in _leave's §3.5 case, the
    branch kept as the run's stay (§4 step 1, _keep_stay) before it does."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default = rec["default"]
    why = _to_default(run, branch, "b4_left")
    if why is not None:
        _keep_stay(run, branch, False, "refused")
        raise NotRun("git switch %s: %s" % (default, why))
    scope = _scope(run, branch)
    n = len(scope["commits"]) if scope else 0
    _emit(run, lines.fill("pre.b4", {"<branch>": branch, "<default>": default})
          + (lines.fill("pre.b4.count", {"<N>": n}) if n else ""))


def _fetch(run):
    """Stage fetch, specs-repo-git §3.2: the default branch's name and ref, and the fetch that freshens it; the mode
    (§8.1, never under misrooted), with the session branch where it is on -- null with no identity -- and the second
    fetch, of the session branch alone, best-effort and silent where it fails; and, on a --rerun, §3.5's switch back to
    the branch the earlier start's B4 left, where a key of the new set names it, the commit key among them (_run_keys,
    the keys B3 and B4 read) -- in session-branch mode inside lift
    and put-back (_Session.wrap), a skipped one reported as a refused one -- left undone, pre.rerun-stay printed, where
    status could not run earlier in the run (pre.status-failed in reported, which --rerun carries), the dirty set
    unknown, as _disposition stays then. A gate that did not pass leaves nothing more to do. The budget's one unit here
    covers both fetches: this stage is a call's first, whose first unit always goes ahead."""
    rec, specs = run["rec"], run["specs"]
    if rec["gate"] != "pass":
        return _advance(run, "done")
    run["budget"].check(FETCH_COST)
    rec.update(resolve_default(specs, fetch=True))
    misrooted = rec["specs_git"] == "misrooted"
    if not misrooted and rec["default"]:
        m = sb.mode(specs, rec["default"])
        rec["mode"], rec["session_branch"] = m["mode"], m["branch"] if m["mode"] == "on" else None
        if rec["session_branch"] and rec["remote"] == "origin":  # one fetch naming both would fail whole while origin lacks it
            sb.git_bounded(specs, CAP, "fetch", "origin", "+refs/heads/%s:refs/remotes/origin/%s"
                           % (rec["session_branch"], rec["session_branch"]))
    left = rec["b4_left"]
    if left and not misrooted and branch_key(left, _run_keys(rec))["key"]:
        def current():
            return _head_branch(specs) or sb.text(sb.git(specs, "rev-parse", "--short", "HEAD"))

        def switch_back():
            r = sb.git(specs, "switch", left, check=False)
            if r.returncode != 0:
                return _first_line(r, error=True)
            return None

        if "pre.status-failed" in rec["reported"]:
            _emit(run, run["lines"].fill("pre.rerun-stay", {"<current>": current(), "<branch>": left}))
        else:
            sess = _session(run)
            why = switch_back() if sess is None else sess.wrap(switch_back)[1]
            if why is None:
                rec["b4_left"] = None
            else:
                _emit(run, run["lines"].fill("pre.rerun-failed", {
                    "<branch>": left, "<git's first error line>": why, "<current>": current()}))
    _advance(run, "disposition" if misrooted else "guards")


def _guards(run):
    """Stage guards, specs-repo-git §3.3: the first of G0, G1 and G2 that holds prints its §5 block, saved for end to
    repeat, and ends the preflight; G0 sets specs_git: blocked. G1 on a plugin branch then asks branch-merged HEAD
    (_ask_stay), once its block is in the record, so the stay's save holds both: on a branch the preflight would have
    left -- merged, or one no key of the run, nor its commit key, names -- outside session-branch mode, the stay is
    kept, reason g1, and G1 prints its landing form (§5, _g1_landing), the plain block saved for end; under a run typed
    mid-run, its mid-run form, stay or none. In session-branch mode
    with a session branch, G2 takes §5's session-branch lines, or, on the session branch itself, its own variant; with
    no identity, its no-identity variant."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    head, found, shown = _head_branch(specs), None, None
    if head is None:
        rec["specs_git"] = "blocked"
        found = ("G0", _g0_block(lines, specs, rec["default"]), [])
    else:
        listed = _status(run)
        other = listed["other"] if listed else []
        if other:
            found = ("G1", _g1_block(lines, specs, other), other)
        elif head != rec["default"] and not branch_key(head, [])["plugin_branch"]:
            values = None
            if rec["mode"] == "on" and rec["session_branch"]:
                variant = "self" if head == rec["session_branch"] else "session"
                values = {"<identity>": _identity(rec["session_branch"])}
            elif rec["mode"] == "on":  # no identity: nothing is committed in the mode until one is set (§8.1)
                variant = "no-identity"
            else:
                variant = "implement" if run["command"] == "/implement" and _inside(rec["top"]) else None
            found = ("G2", _g2_block(lines, specs, head, rec["default"], variant, values), [])
    if found is None:
        return _advance(run, "flush")
    if not (rec["specs_git"] == "blocked" and found[0] != "G0"):  # a run --rerun carries blocked keeps G0's block,
        rec.update(guard=found[0], guard_block=found[1], guard_paths=found[2])  # which end repeats with its row
    if found[0] == "G1":  # after the block is in the record, so the stay's save holds both
        _ask_stay(run, head, "g1")
        shown = _g1_landing(lines, found[1], head, rec["default"], specs, found[2],
                            rec["stay"] if _stayed_on(rec, head) else None, rec.get("midrun"))
    _emit(run, shown or found[1])
    _advance(run, "done")


def _flush(run):
    """Stage flush, specs-repo-git §3.4: the catch-up; outside session-branch mode, a merged plugin branch left by B2's
    action before a flush would commit on it, then the dirty session files committed on the current branch and
    pushed, or, with none dirty, the retry of its push -- in the mode, _flush_session. The stage's capped calls are one
    budget unit, checked before the first of them -- before the catch-up's lift in the mode: the stage resumes from its
    start, and a resume that repeated a catch-up whose pull failed would never reach the push. A push origin rejects as
    non-fast-forward returns next naming its replay, the stage left at flush, which the replay advances; the settle
    loop then starts on start --resume."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    rec["settle_todo"] = None  # computed on entering the settle loop, after this branch's replay, if any
    checked = []

    def unit():
        if not checked:
            run["budget"].check(FLUSH_COST)
            checked.append(True)

    default = rec["default"]
    sess = _session(run)
    pulled = catch_up(specs, default, rec["default_ref"], on_write=unit, wrap=sess.wrap if sess else None)
    if pulled:
        _emit(run, pulled)
    if rec["mode"] == "on":
        return _flush_session(run, sess, unit)
    head = _head_branch(specs)
    listed = _status(run)
    dirty = listed["artifact"] if listed else []
    refused = False
    if dirty and head != default and branch_key(head, [])["plugin_branch"]:
        merged = _merged(run, "HEAD", head)
        if merged["merged"]:
            unit()
            refused = not _leave(run, head, merged["test"], merged_flush=True)
            head = _head_branch(specs)
    if dirty:
        c = commit_session_files(specs, session_subject(rec["commit_key"], run["command"]))
        if c["status"] == "locked":
            _emit(run, lines.preflight_form(lines.T["row.locked"]))
        elif c["status"] == "failed":
            _emit(run, lines.preflight_form(_row_line(lines, "commit-failed", {"error": c["error"]})))
        if c["status"] != "committed":
            return _advance(run, "settle")
        if refused:
            _emit(run, lines.fill("pre.merged-flush", {"<branch>": head, "<sha7>": c["sha"][:7], "<default>": default,
                                                       "<SPECS_PATH>": specs}))
    elif not (_scope(run, head) or {}).get("commits"):
        return _advance(run, "settle")
    unit()
    done = _push(run, head)
    if done["outcome"] == "rejected":
        _save(run)
        return _replay_next(specs, run["command"], head, done["set_upstream"], "start")
    _advance(run, "settle")


def _flush_session(run, sess, unit):
    """§3.4's flush in session-branch mode, past the catch-up, where the two cases are one: §8.2's commit, never on
    HEAD -- so no merged-branch leave comes first -- whose creation of the session branch, where it printed created:
    true, is reported here as pre.created.*; then the session branch pushed where it holds commits a push would publish
    and §4 step 5's conditions hold as §8.4 states them (_push: a rejection names no replay). A commit that could not
    run prints pre.session-not-run, and the push of what an earlier run left still goes ahead. With no identity (<sess>
    None) nothing is committed or pushed (§8.1). Nothing else is printed, save step 6's failure lines -- the session
    branch's rejection among them, followed by the conflict clause its ending points at (_session_rejected_preflight)."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    if sess is None:
        return _advance(run, "settle")
    c, err = sess.commit(carry=False)
    if c is None:
        _emit(run, lines.fill("pre.session-not-run", {"<the first line of its stderr>": err}))
    elif c["created"]:
        values = {"<identity>": _identity(sess.branch), "<base short sha>": c["base"]}
        if c["committed"]:
            _emit(run, lines.fill("pre.created.committed", dict(values, **{"<sha7>": c["committed"][:7]})))
        else:
            _emit(run, lines.fill("pre.created.empty", values))
    if sb.rev(specs, "refs/heads/" + sess.branch) is not None and (_scope(run, sess.branch) or {}).get("commits"):
        unit()
        _push(run, sess.branch, sync=(c or {}).get("sync"))
    _advance(run, "settle")


def _settle(run):
    """Stage settle, specs-repo-git §3.4's loop over every other local plugin branch, less the current one and the one
    the merged-branch leave reported, computed on entering it -- past the current branch's replay, if any, so -d's
    test reads the HEAD that replay moved. A branch whose push origin rejects as non-fast-forward is queued in
    pending, {branch, set_upstream, standing}, and replayed after the loop, each replay in a call of its own: where
    any is queued, the stage moves to settle-done and next names the first. Each branch leaves settle_todo, and the
    record is saved, once it is settled, so a resume goes on from the next."""
    rec, specs = run["rec"], run["specs"]
    if rec["settle_todo"] is None:
        head = _head_branch(specs)
        names = sb.text(sb.git(specs, "for-each-ref", "--format=%(refname:lstrip=2)", "refs/heads/")).splitlines()
        rec["settle_todo"] = [b for b in names if b and branch_key(b, [])["plugin_branch"] and b not in (head, rec["b2_left"])]
        _save(run)
    while rec["settle_todo"]:
        _settle_branch(run, rec["settle_todo"][0])
        rec["settle_todo"] = rec["settle_todo"][1:]
        _save(run)
    if rec["pending"]:
        _advance(run, "settle-done")
        return _queued_next(run, rec)
    _advance(run, "disposition")


def _settle_branch(run, branch):
    """One branch of §3.4's loop: merged by ancestry -d can see, deleted as B2 deletes; merged otherwise, the -D
    advisory, once a run; unmerged, its commits a push would publish pushed where step 5's conditions hold."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    if sb.rev(specs, "refs/heads/" + branch) is None:  # gone since the loop listed it
        return
    merged = _merged(run, "refs/heads/" + branch, branch)
    if merged["merged"]:
        if merged["test"] == 1 and _d_sees(specs, branch):
            _delete(run, branch)
        elif branch not in rec["advised_D"]:
            _emit(run, lines.fill("pre.advisory-D", {"<branch>": branch, "<default>": rec["default"], "<SPECS_PATH>": specs}))
            _rm_line(run, branch)
            rec["advised_D"].append(branch)
        return
    commits = (_scope(run, branch) or {}).get("commits")
    if not commits:
        return
    run["budget"].check(PUSH_COST)
    done = _push(run, branch)
    if done["outcome"] == "pushed":
        _emit(run, lines.fill("pre.pushed-left", {"<N>": len(commits), "<branch>": branch}))
    elif done["outcome"] == "rejected":
        rec["pending"].append({"branch": branch, "set_upstream": done["set_upstream"], "standing": _head_branch(specs)})


def _disposition(run):
    """Stage disposition, specs-repo-git §3.5: the first row that applies to the branch HEAD stands on. B1, B3 and a
    branch no row names stay where they are; B2 and B4 switch to the default branch -- under misrooted, they stay and
    print pre.stay instead, and where status could not run in this run (pre.status-failed in reported, which --rerun
    carries), the dirty set unknown, they stay and print pre.stay.unlisted -- the branch then kept as the run's stay
    (§4 step 1, _keep_stay), reason unlisted, B2's and B4's alike. B2's and B4's refused switch keeps it too (_leave,
    _b4). B3 and B4 resolve the branch against the run key set with the start's commit key beside it (_run_keys), the
    keys a stay's kind is read by, so a branch B4 leaves or would have left is always one an unkeyed stay names."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    head, default = _head_branch(specs), rec["default"]
    if head is not None and head != default and branch_key(head, [])["plugin_branch"]:
        merged = _merged(run, "HEAD", head)
        if merged["merged"] or not branch_key(head, _run_keys(rec))["key"]:
            stay = ("pre.stay" if rec["specs_git"] == "misrooted"
                    else "pre.stay.unlisted" if "pre.status-failed" in rec["reported"] else None)
            if stay:
                _emit(run, lines.fill(stay, {"<branch>": head, "<default>": default,
                                             lines.placeholder(stay, "<switched"): 0 if merged["merged"] else 1}))
                if stay == "pre.stay.unlisted":
                    _keep_stay(run, head, merged["merged"], "unlisted")
            else:
                if _pulls(rec):
                    run["budget"].check(PULL_COST)
                if merged["merged"]:
                    _leave(run, head, merged["test"])
                else:
                    _b4(run, head)
    _advance(run, "done")


def _start_stages(run):
    """start's stages from the record's own, each saving the next as it ends: the call the run makes next where a
    stage hands one over -- the current branch's replay at flush, the first queued one at settle-done -- else None."""
    rec = run["rec"]
    while rec["stage"] != "done":
        stage = rec["stage"]
        if stage == "fetch":
            _fetch(run)
        elif stage == "guards":
            _guards(run)
        elif stage == "flush":
            nxt = _flush(run)
            if nxt:
                return nxt
        elif stage == "settle":
            nxt = _settle(run)
            if nxt:
                return nxt
        elif stage == "settle-done":
            if rec["pending"]:
                return _queued_next(run, rec)
            _advance(run, "disposition")
        elif stage == "disposition":
            _disposition(run)
        else:
            raise NotRun("the record's stage %s is none of start's" % stage)
    return None


def _carry(rec, old):
    """--rerun: what the run's earlier start, the record <old>, set that a second preflight in the same run keeps in
    <rec> -- specs_git where this one sets none, with what set it (the misrooted notice; G0's block, which _guards then
    keeps beside a block the re-run prints), the -D advisories given and the once-a-run reports printed, the branch B2
    or the merged-branch leave reported (which §3.4's loop skips for the whole run), the branch B4 left, the declined
    paths, the session branch's creation by a call other than the flush, which the run carries to its end (§8.2), and
    the run's snapshot (§7), since a re-run takes none of its own and _close only narrows the one it carries. Never
    the stay: each preflight derives its own (§4 step 1), so a stay's reason is always one this preflight met -- an
    early stop asks branch-merged afresh (_stop_stay) -- and none survives where this one would no longer leave the
    branch or has left it."""
    if rec["specs_git"] is None and old.get("specs_git"):
        rec["specs_git"] = old["specs_git"]
        if old["specs_git"] == "misrooted":
            rec["misrooted_notice"] = old.get("misrooted_notice")
        else:
            rec.update(guard=old.get("guard"), guard_block=old.get("guard_block"),
                       guard_paths=list(old.get("guard_paths") or []))
    snap = old.get("start_dirty")
    rec.update(advised_D=list(old.get("advised_D") or []), reported=list(old.get("reported") or []),
               b2_left=old.get("b2_left"), b4_left=old.get("b4_left"), declined=list(old.get("declined") or []),
               session_branch_created=old.get("session_branch_created"),
               start_dirty=dict(snap) if isinstance(snap, dict) else None)


def _queued_next(run, rec):
    """The call that replays the first branch <rec>'s pending queue holds (specs-repo-git §3.4, after the loop)."""
    queued = rec["pending"][0]
    return _replay_next(run["specs"], run["command"], queued["branch"], bool(queued.get("set_upstream")), "start")


def _start_result(run, nxt, replaced, error):
    """start's JSON: what this call printed and hands over next, then the run's facts as the record now holds them --
    stay among them, which an end run by hand reads (specs-repo-git §3.3), the run's snapshot (start_dirty), the open
    run it was typed under (midrun), and started, the record's, which names the run's own record (§7)."""
    rec = run["rec"]
    offline = bool(rec.get("offline"))
    return {"print": run["print"], "next": nxt, "specs_git": rec.get("specs_git"), "gate": rec.get("gate"),
            "default": rec.get("default"), "default_ref": rec.get("default_ref"), "remote": rec.get("remote"),
            "offline": offline, "offline_clause": run["lines"].T["text.offline"] if offline else None,
            "session_branch": rec.get("session_branch"), "mode": rec.get("mode"), "guard": rec.get("guard"),
            "branch": rec.get("branch"), "b2_left": rec.get("b2_left"), "b4_left": rec.get("b4_left"),
            "stay": rec.get("stay"), "start_dirty": rec.get("start_dirty"), "midrun": rec.get("midrun"),
            "started": rec.get("started"), "replaced": replaced, "error": error}


def _stop_stay(run):
    """specs-repo-git §1 rule 5's early stop, before the switch §3.4's leave or §3.5's B2 or B4 would make: where
    the gate passed, the default ref is known and HEAD stands on a plugin branch no stay names yet, ask branch-merged
    HEAD (_ask_stay), so a branch the preflight would have left -- merged, or one no key names -- is kept as the run's
    stay (§4 step 1), reason stopped. A stay this preflight already kept for HEAD -- B2's or B4's refused switch,
    which stops the call -- stands as it is; a re-run's preflight starts with none (_carry), so its own stop asks
    afresh."""
    rec = run["rec"]
    head = _head_branch(run["specs"]) if rec.get("gate") == "pass" and rec.get("default_ref") else None
    if head is not None and not _stayed_on(rec, head):
        _ask_stay(run, head, "stopped")


def _close(run):
    """The record saved as the call returns, branch naming where HEAD then stands, and, where the gate passed, the
    run's snapshot narrowed to the paths status() still lists, each keeping its blob (§7) -- left as it stands where
    status cannot run, and where the gate did not pass, since a status there would read another directory."""
    rec = run["rec"]
    passed = rec.get("gate") == "pass"
    rec["branch"] = _head_branch(run["specs"]) if passed else None
    snap = rec.get("start_dirty")
    if snap and passed:
        try:
            dirty = set(status(run["specs"])["artifact"])
        except NotRun:
            dirty = None
        if dirty is not None:
            rec["start_dirty"] = {p: b for p, b in snap.items() if p in dirty}
    _save(run)


def _take_snapshot(run):
    """The run's snapshot (P11; specs-repo-git §7, §4 step 1), taken by a fresh start that is not a --rerun right
    after its first save: where the gate passed and no misrooted flag stands, <default> resolved without a fetch and
    the mode read; outside session-branch mode -- whose commit takes every session file the overlay holds, keeping no
    snapshot apart (§3.5) -- snapshot() of the session files dirty now, each path's blob written, saved at once so a
    kill in the fetch that follows keeps it. Where status cannot run, _status reports it, once in the run (§2.1), and
    no snapshot is taken; where git cannot read the default branch, the mode or a blob, none either: start_dirty stays
    null. Any other exception is a fault, and reaches start's error, as one in a stage does."""
    rec, specs = run["rec"], run["specs"]
    if rec.get("gate") != "pass" or rec.get("specs_git") == "misrooted":
        return
    try:
        default = resolve_default(specs, False)["default"]
        if default and sb.mode(specs, default)["mode"] == "on":
            return
    except (NotRun, OSError):
        return
    if _status(run) is not None:
        try:
            rec["start_dirty"] = snapshot(specs)
        except (NotRun, OSError):
            rec["start_dirty"] = None
    _save(run)


def start(specs, command, keys=(), commit_key=None, register_rebuild=None, rerun=False, resume=False,
          budget=DEFAULT_BUDGET):
    """specs-repo-git §3's specs-preflight for the run of this session and <command>, on <specs> (SPECS_PATH as set,
    "" meaning unset), with the run key set <keys>. A call that is not a resume prints the Environment: line and §3.1's
    notices (reads only), then saves a fresh record at stage fetch -- its first write -- takes the run's snapshot
    (_take_snapshot), save on a --rerun, and prunes; a failure before that save raises, so the caller exits 2 with
    nothing done, and after it every outcome is returned, an exception as error and the pre.stopped line, after
    _stop_stay's ask on a plugin branch (§4 step 1's stay). The
    stages (START_STAGES) then run from the record's own, each saved on entering it and resumable from its start.
    <resume> goes on with the saved stage only where state.resumable holds for this call's arguments; otherwise the
    call runs fresh. <rerun> opens on this command's record, keeping what _carry
    keeps, and saves this call's arguments, its key set among them. A stage that hands a replay over, and a unit of
    capped calls <budget> would not hold, return next: the replay, or start --resume with the record's args. In
    session-branch mode the budget is checked before a wrapped move's lift, never between it and its put-back, so every
    call returns with the overlay in place; the closing put-back runs where the stages reach done or the call stops on
    an error (_closing_put_back), never at a budget stop."""
    state, lines = _flow()
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    for key in list(keys) + ([] if commit_key is None else [commit_key]):
        if not KEY_RE.fullmatch(key):
            raise NotRun("usage: the key %s does not match addressing §1's key grammar" % key)
    if isinstance(budget, bool) or not isinstance(budget, (int, float)) or not math.isfinite(budget) or budget < 0:
        raise NotRun("usage: --budget takes seconds, 0 or more, got %s" % budget)
    session = state.session_id()
    args = {"specs": specs, "keys": list(keys), "commit_key": commit_key, "register_rebuild": register_rebuild}
    old = state.load(session, command)
    run = {"state": state, "lines": lines, "specs": specs, "session": session, "command": command, "print": [],
           "budget": _Budget(budget), "rec": old}
    replaced = None
    fresh = not (resume and old is not None and old.get("stage") in START_STAGES and state.resumable(old, args))
    if fresh:
        env = env_line(specs)
        g = gate(specs)
        rec = state.new(command, session=session, specs=specs, env_line=env, gate=g["state"], top=g["top"],
                        keys=list(keys), commit_key=commit_key, register_rebuild=register_rebuild, args=args,
                        stage="fetch")
        if g["misrooted"]:
            rec.update(specs_git="misrooted", misrooted_notice=list(g["lines"]))
        if rerun and old is not None:
            _carry(rec, old)
        elif old is not None:
            replaced = {"command": command, "started": old.get("started")}
        run["rec"], run["print"] = rec, [env] + list(g["lines"])
    # This call's budget where it is not the default, outside args: how the preflight is split across calls, which the
    # start --resume a budget stop or a replay names repeats, and resumable's argument test never reads.
    run["rec"]["budget"] = None if budget == DEFAULT_BUDGET else budget
    if fresh:
        state.save(session, command, run["rec"])  # the first write: exit 2 is possible only before it
    nxt = error = None
    try:
        try:
            if fresh:
                if not rerun:
                    _take_snapshot(run)
                state.prune(keep_session=session)
            nxt = _start_stages(run)
            if nxt is None:
                _closing_put_back(run)
        except _Stop:
            nxt = _resume_next(command, run["rec"]["args"], run["rec"]["budget"])
        _close(run)
    except Exception as e:
        said = " ".join(str(e).split())
        error = said if isinstance(e, NotRun) else type(e).__name__ + (": " + said if said else "")
        nxt = None
        try:
            _closing_put_back(run)
        except Exception:
            pass
        try:
            _stop_stay(run)
        except Exception:
            pass
        _emit(run, lines.fill("pre.stopped", {"<the error>": error}))
        try:
            _close(run)
        except Exception:
            pass
    return _start_result(run, nxt, replaced, error)


# ---- the landing (specs-repo-git §4 step 1): a run's own session-file change on <default>, the checkout unmoved ------

HELD_REF = "refs/workflows/held/"
# A held entry's fields. One whose refused is None is a journal entry (P6): a landing written before its move.
HELD_FIELDS = ("c1", "c2", "old", "tip", "onto", "branch", "remote_only", "kind", "merged", "command", "refused", "date",
               "paths", "here", "index_before")
PENDING_FIELDS = ("c1", "c2", "old", "tip", "onto", "paths", "remote_only", "here", "index_before")
# A landing journal's own extra field: moves, the renumbering its rebuild of a security register made (sb._moves), so
# a resumed landing prints the register clause the end would have (specs-repo-git §6). An entry with none -- a held
# entry, a here journal, or one an earlier version wrote -- reads as no move.
JOURNAL_MOVES = "moves"
SNAPSHOT_MESSAGE = "specs-git: the session files as the run found them\n"
# push_check's rows that leave the refspec push nowhere to go for good (P22); its refused-before, and a refspec push
# that failed, was rejected or was refused, are transient.
PERMANENT_ROWS = ("no-remote", "elsewhere", "remote-deleted")
_OBJECT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_WRITES = [0]  # the ref writes the landing has made: land and retry_held exit 2 only before their first
_PENDING = [None]  # the journal's pending of the move under way, which LandStopped carries


class LandStopped(Exception):
    """land or retry_held stopped by an exception after its first ref write -- the move or push of <default>, the
    update-ref of HEAD's branch, or a held ref's write or removal: the CLI prints its JSON, exit 0, error set. <pending>
    is the run's own change's journal, where its move was under way, and never a held entry's, whose journal stays in
    its record; the held record keeps that journal entry for land's resume (end --resume) or the next preflight's held
    stage (retry_held), which finish it only where the move is verified. <partial> is retry_held's report of what it
    landed, finished, failed and found stuck before the error, where retry_held raised it."""

    def __init__(self, message, pending=None, partial=None):
        Exception.__init__(self, message)
        self.pending, self.partial = pending, partial


def _wrote():
    _WRITES[0] += 1


def _write_bounded(fn, *args):
    """<fn>(*args) inside the landing's exit-2 boundary: an exception after its first ref write is LandStopped,
    carrying the journal's pending; _Stop, a LandStopped, and an exception before that write go on as they are."""
    before = _WRITES[0]
    _PENDING[0] = None
    try:
        return fn(*args)
    except (_Stop, LandStopped):
        raise
    except Exception as e:
        if _WRITES[0] == before:
            raise
        raise LandStopped(str(e) if isinstance(e, NotRun) else "%s: %s" % (type(e).__name__, e), _PENDING[0],
                          getattr(e, "partial", None)) from e


def held_path(root):
    """This worktree's held record, `rev-parse --git-path workflows/held.json`: per worktree, as session-branch.py's
    placed record is, since the working copies a held entry was taken from are this worktree's alone."""
    path = sb.text(sb.git(root, "rev-parse", "--git-path", "workflows/held.json"))
    return path if os.path.isabs(path) else os.path.join(root, path)


def _entry_ok(e):
    return (isinstance(e, dict) and all(k in e for k in HELD_FIELDS)
            and all(isinstance(e[k], str) and _OBJECT_ID.fullmatch(e[k]) for k in ("c1", "c2"))
            and isinstance(e["paths"], dict) and (e["refused"] is None or isinstance(e["refused"], dict))
            and isinstance(e.get("lift", {}), dict) and isinstance(e.get(JOURNAL_MOVES) or [], list))


def _read_held(path):
    """The entries of the held record at <path>, oldest first: [] where none stands, None where one stands that cannot
    be read. An entry missing a field is left out."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None
    entries = data.get("entries") if isinstance(data, dict) else None
    return [e for e in entries if _entry_ok(e)] if isinstance(entries, list) else None


def held_entries(root):
    """This worktree's held entries, oldest first; [] where its record is absent or unreadable."""
    return _read_held(held_path(root)) or []


def _held_write(root, entries):
    path = held_path(root)
    if not entries:
        if os.path.lexists(path):
            os.remove(path)
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as fh:
        json.dump({"entries": entries}, fh, indent=1, sort_keys=True)
    os.replace(path + ".tmp", path)


def _held_put(root, entry, replace=None):
    """<entry> into the held record, in the place of the entry whose c2 is <replace> (else of its own c2), else last.
    Its ref, refs/workflows/held/<c2>, is written first, so no entry names a commit no ref keeps; a replaced entry's
    ref is removed after. A held entry -- refused set -- keeps no journal moves (JOURNAL_MOVES): it is no journal."""
    if entry.get("refused") is not None and JOURNAL_MOVES in entry:
        entry = {k: v for k, v in entry.items() if k != JOURNAL_MOVES}
    _wrote()
    sb.git(root, "update-ref", HELD_REF + entry["c2"], entry["c2"])
    entries = held_entries(root)
    key = replace or entry["c2"]
    at = next((i for i, e in enumerate(entries) if e["c2"] == key), None)
    if at is None:
        entries.append(entry)
    else:
        entries[at] = entry
    _held_write(root, entries)
    if replace and replace != entry["c2"]:
        sb.git(root, "update-ref", "-d", HELD_REF + replace, check=False)


def _held_remove(root, c2s):
    """Each entry whose c2 is in <c2s> out of the held record, then its ref."""
    c2s = set(c2s)
    if not c2s:
        return
    _wrote()
    _held_write(root, [e for e in held_entries(root) if e["c2"] not in c2s])
    for c in sorted(c2s):
        sb.git(root, "update-ref", "-d", HELD_REF + c, check=False)


def held_drop(root, sha7):
    """`land --drop-held <sha7>` (P22): the held entry whose c2 begins <sha7>, and its ref, removed; its files are left
    as they stand, ordinary uncommitted files from then on. False where no entry matches; NotRun where several do."""
    found = [e for e in held_entries(root) if e["c2"].startswith(sha7)]
    if len(found) > 1:
        raise NotRun("%s names more than one held entry" % sha7)
    if not found:
        return False
    _held_remove(root, [found[0]["c2"]])
    return True


def _tree(root, commit):
    return sb.text(sb.git(root, "rev-parse", commit + "^{tree}"))


def _at(root, commit, paths):
    """An index-info line for each of <paths> as <commit> holds it, mode 0 (removed) where it lacks it."""
    held = sb._tree_entries(root, commit, paths)
    return ["%s %s\t%s" % (held[p][0], held[p][1], p) if p in held else "0 %s\t%s" % (sb.ZERO, p) for p in paths]


def _message(root, commit):
    """<commit>'s message, byte for byte."""
    return sb._commit_parts(root, commit)[1]


def held_rebuild(root, entry, drop):
    """P8: <entry> rebuilt without the paths of <drop> -- its held commit made again on its c1 with those paths at c1's
    versions, the record and the ref following -- or, where no path is left, removed with its ref: None."""
    drop = set(drop) & set(entry["paths"])
    if not drop:
        return entry
    keep = {p: b for p, b in entry["paths"].items() if p not in drop}
    if not keep:
        _held_remove(root, [entry["c2"]])
        return None
    tree = sb.tree_with(root, _tree(root, entry["c2"]), _at(root, entry["c1"], sorted(drop)))
    new = _with_lift(dict(entry, c2=sb.commit_tree(root, tree, [entry["c1"]], _message(root, entry["c2"])), paths=keep))
    _held_put(root, new, replace=entry["c2"])
    return new


def _with_lift(entry):
    """<entry> with its lift overrides (P7 across calls) narrowed to the paths it holds, the field gone where none is
    left."""
    lift = {p: b for p, b in (entry.get("lift") or {}).items() if p in entry["paths"]}
    out = {k: v for k, v in entry.items() if k != "lift"}
    if lift:
        out["lift"] = lift
    return out


ORPHAN_AGE = 3600  # seconds: a held ref whose commit is younger may be one another worktree has not yet listed


def _held_orphans(root):
    """P31: each refs/workflows/held/ ref that no live worktree's held record lists (worktree list --porcelain -z, each
    worktree's rev-parse --git-path workflows/held.json). The refs are listed first and the records read after, so a
    ref another worktree writes meanwhile is not among those judged; and a ref is taken only where its commit's
    committer date is over ORPHAN_AGE old, since a worktree writes an entry's ref before its record, and a held commit
    is made just before its ref. None where a worktree's record cannot be read, so no ref is ever taken for an orphan
    on a guess."""
    refs = []
    for line in sb.text(sb.git(root, "for-each-ref", "--format=%(refname) %(committerdate:raw)", HELD_REF)).split("\n"):
        fields = line.split()
        if len(fields) >= 2 and fields[1].isdigit():  # a ref naming no commit has no date, and is never taken
            refs.append((fields[0], int(fields[1])))
    if not refs:
        return []
    listed = set()
    for field in sb.nul_list(sb.git(root, "worktree", "list", "--porcelain", "-z")):
        if not field.startswith("worktree "):
            continue
        where = field[len("worktree "):]
        r = sb.git(where, "rev-parse", "--git-path", "workflows/held.json", check=False)
        path = sb.text(r)
        got = _read_held(path if os.path.isabs(path) else os.path.join(where, path)) if r.returncode == 0 else None
        if got is None:
            return []
        listed.update(e["c2"] for e in got)
    now = time.time()
    return [ref for ref, when in refs if ref[len(HELD_REF):] not in listed and now - when > ORPHAN_AGE]


def _held_info(e):
    return {"refused": e["refused"], "branch": e["branch"], "kind": e["kind"], "command": e["command"], "sha": e["c2"]}


def snapshot(root):
    """P11, P24: the snapshot a run's start takes -- every ARTIFACT path status() lists, mapped to its working copy's
    blob (written, so a later land reads it), None for a path absent from the working tree. NotRun where status cannot
    run."""
    return {p: sb.worktree_blob(root, p, write=True) for p in status(root)["artifact"]}


def _changed(root, a, b):
    return sorted(sb.nul_list(sb.git(root, "diff-tree", "-r", "-z", "--no-renames", "--name-only", a, b)))


def _own_commits(root, snap, message):
    """The run's own change, as the landing (specs-repo-git §4 step 1) takes it: c1, HEAD's tree with each <snap> path at
    its blob (None: removed), committed on HEAD; c2, c1's tree with each ARTIFACT path status() lists now at its working
    copy (written; its mode from the file; removed where no file stands), committed on c1 with <message>. c2 is None
    where the two trees are one: nothing of the run's."""
    head = _commit(root, "HEAD")
    base = _tree(root, head)
    snap = snap or {}
    modes = {p: m for p, (m, _sha) in sb._tree_entries(root, head, sorted(snap)).items()} if snap else {}
    t1 = sb.tree_with(root, base, ["%s %s\t%s" % (modes.get(p, "100644"), b, p) if b else "0 %s\t%s" % (sb.ZERO, p)
                                   for p, b in sorted(snap.items())]) if snap else base
    c1 = sb.commit_tree(root, t1, [head], SNAPSHOT_MESSAGE)
    entries = []
    for p in status(root)["artifact"]:
        full = os.path.join(root, p)
        if os.path.isfile(full) and not os.path.islink(full):
            mode = "100755" if os.stat(full).st_mode & 0o100 else "100644"
            entries.append("%s %s\t%s" % (mode, sb.worktree_blob(root, p, write=True), p))
        else:
            entries.append("0 %s\t%s" % (sb.ZERO, p))
    t2 = sb.tree_with(root, t1, entries) if entries else t1
    if t2 == t1:
        return c1, None
    return c1, sb.commit_tree(root, t2, [c1], message if message.endswith("\n") else message + "\n")


def _entry(root, c1, c2, default, branch, facts, here):
    """A held entry for the change <c1> to <c2>, not yet journalled: refused None, no tip. Its branch is the stayed
    branch (facts' stayed, else <branch>), or HEAD's for a here entry, whose onto is HEAD's branch too."""
    facts = facts or {}
    stayed = facts.get("stayed")
    return {"c1": c1, "c2": c2, "old": None, "tip": None, "onto": branch if here else default,
            "branch": branch if here or not isinstance(stayed, str) or not stayed else stayed, "remote_only": False,
            "kind": facts.get("kind"), "merged": facts.get("merged"), "command": facts.get("command"), "refused": None,
            "date": _today(), "paths": {p: sb.blob(root, c2, p) for p in _changed(root, c1, c2)}, "here": here,
            "index_before": None}


def _pending(entry):
    """The journal's pending of <entry>: its PENDING_FIELDS, and the moves a landing journal carries ([] for none)."""
    return dict({k: entry[k] for k in PENDING_FIELDS}, **{JOURNAL_MOVES: list(entry.get(JOURNAL_MOVES) or [])})


def _split(root, entry, refused):
    """P29: <entry>'s change split at the paths own_change refused -- (the stuck entry, a commit on c1 holding only those
    paths at c2's versions, refused with the first refusal and permanent; <entry> narrowed to the rest, its c2 made
    again on c1 with the refused paths at c1's versions, or None where nothing is left)."""
    paths = sorted({x["path"] for x in refused})
    msg, first = _message(root, entry["c2"]), refused[0]
    tree = sb.tree_with(root, _tree(root, entry["c1"]), _at(root, entry["c2"], paths))
    stuck = _with_lift(dict(entry, c2=sb.commit_tree(root, tree, [entry["c1"]], msg), old=None, tip=None,
                            remote_only=False, paths={p: entry["paths"].get(p) for p in paths},
                            refused={"reason": first["reason"], "path": first["path"], "detail": first["detail"],
                                     "permanent": True}))
    rest = {p: b for p, b in entry["paths"].items() if p not in paths}
    if not rest:
        return stuck, None
    tree = sb.tree_with(root, _tree(root, entry["c2"]), _at(root, entry["c1"], paths))
    return stuck, _with_lift(dict(entry, c2=sb.commit_tree(root, tree, [entry["c1"]], msg), paths=rest))


def _verified(root, entry, default, check=None):
    """P6: a landing journal's move is verified where <default> holds its tip -- or, for a remote_only one,
    origin/<default>, fetched (capped; <check>(cost) first) where it does not already."""
    tip = entry.get("tip")
    if not tip:
        return False
    ref = ("refs/remotes/origin/" if entry.get("remote_only") else "refs/heads/") + default

    def holds():
        at = sb.rev(root, ref)
        return at is not None and (at == tip or sb.is_ancestor(root, tip, at))
    if holds():
        return True
    if not entry.get("remote_only") or sb.git(root, "remote", "get-url", "origin", check=False).returncode != 0:
        return False
    if check:
        check(FETCH_COST)
    sb.git_bounded(root, CAP, "fetch", "--no-tags", "origin", "+refs/heads/%s:%s" % (default, ref))
    return holds()


_NO_LINK = object()  # _still_held's "no later entry started from this one here"


def _from_snapshot(root, e, p):
    """Whether <e>'s c1 took <p> from its run's snapshot: c1's blob there differs from c1's parent's. That parent is
    HEAD as land read it when it made c1, at the landing -- not when the run started -- so a version the user commits on
    the stayed branch mid-run, after the run took its snapshot, reads as HEAD's too and makes no chain link. Only a path
    taken from the snapshot can have started from another landing's version (P7's chain, step 6's "snapshot blob"); one
    at HEAD's version is the stayed branch's own, committed there, whatever blob it shares with a held entry's c2."""
    return sb.blob(root, e["c1"] + "^", p) != sb.blob(root, e["c1"], p)


def _started_from(root, later, earlier):
    """Whether the change <later> started from <earlier>'s version on a path: one it changes, took from its snapshot,
    and holds in c1 at earlier's c2 blob."""
    return any(p in later["paths"] and _from_snapshot(root, later, p) and sb.blob(root, later["c1"], p) == b
               for p, b in earlier["paths"].items())


def _place(root, chain, landing):
    """<landing> placed in <chain>: before the first landing there that started from it, so a resumed change is the
    oldest of the chain it starts; else last."""
    k = next((k for k, c in enumerate(chain) if _started_from(root, c, landing)), len(chain))
    return chain[:k] + [landing] + chain[k:]


def _lift_source(root, e, p):
    """Where a lift of the landing <e> on <p> takes its version from: (None, its lift override) where it has one (P7
    across calls), else (its c1, c1's blob)."""
    lift = e.get("lift") or {}
    if p in lift:
        return None, lift[p]
    return e["c1"], sb.blob(root, e["c1"], p)


def _write_version(root, e, p, source, want):
    """<p> written back as <want>: from <source>, a commit, by sb.write_from; from <e>'s lift override (<source> None)
    through a tree holding <want> at <p>, or none (removed). An override whose blob git no longer holds -- an entry held
    past gc's pruning -- falls back to <e>'s c1. Returns the blob written, None where the path was removed."""
    if source is None and want is not None and sb.git(root, "cat-file", "-e", want, check=False).returncode != 0:
        source, want = e["c1"], sb.blob(root, e["c1"], p)
    if source is None:
        line = "100644 %s\t%s" % (want, p) if want else "0 %s\t%s" % (sb.ZERO, p)
        source = sb.tree_with(root, _tree(root, e["c1"]), [line])
    sb.write_from(root, source, p)
    return want


def _lift(root, chain):
    """The landing's lift (P7): for each path of the landed changes <chain> (oldest first, each {c1, paths: {path: c2's
    blob}, lift}) whose working copy is still the newest landing's c2 blob, write back the version where the chain
    began: that landing's lift override for the path -- where the chain began, which ends the walk -- else its c1's,
    walked back, only where that c1 took the path from its snapshot (_from_snapshot), through each earlier landing whose
    c2 blob is that version, each step taken the same way. So the stayed branch's checkout shows none of what landed,
    and never less than HEAD. A path whose working copy changed since is left as it stands. Returns [(the landing's
    index in <chain>, {path, blob})], blob the version written back, None where the path was removed."""
    out, seen = [], set()
    for i in range(len(chain) - 1, -1, -1):
        for p in sorted(chain[i]["paths"]):
            if p in seen:
                continue
            seen.add(p)
            if sb.worktree_blob(root, p) != chain[i]["paths"][p]:
                continue
            at = i
            source, want = _lift_source(root, chain[i], p)
            for j in range(i - 1, -1, -1):
                if source and p in chain[j]["paths"] and chain[j]["paths"][p] == want \
                        and _from_snapshot(root, chain[at], p):
                    at = j
                    source, want = _lift_source(root, chain[j], p)
            out.append((i, {"path": p, "blob": _write_version(root, chain[at], p, source, want)}))
    return out


def _carry_lift(root, landed):
    """P7 across calls: after <landed> landed, each entry of the record that started from it on a path -- its c1 took
    the path from its snapshot (_from_snapshot), at landed's c2 blob: one still held, or one this call landed after it,
    whose own carry passes the override on -- takes, as its lift override there, the version landed's own lift goes back
    to (its override, else its c1's), so that entry's later lift returns the path to where the chain began, not to
    <landed>'s version. Its c1 stays as it is, so own_change's input never changes: a deletion chained behind an edit is
    still applied where onto holds the edit."""
    own = landed.get("lift") or {}
    for e in held_entries(root):
        if e.get("here") or e["c2"] == landed["c2"]:
            continue
        lift = dict(e.get("lift") or {})
        for p, b2 in landed["paths"].items():
            if p in e["paths"] and sb.blob(root, e["c1"], p) == b2 and _from_snapshot(root, e, p):
                lift[p] = own[p] if p in own else sb.blob(root, landed["c1"], p)
        if lift != (e.get("lift") or {}):
            _held_put(root, dict(e, lift=lift))


def _finish(root, chain, done):
    """The end of a call that landed <chain> (oldest first): each landing's lift override carried, in order, to the
    entries still held that started from it (_carry_lift, each landing read again from the record, where an earlier
    one's carry may have set its own); then the lift over the chain as the record now holds it (_lift); then <done>'s
    entries and refs removed. Run before a _Stop propagates too, so the overrides are written for every landing made.
    Returns _lift's list."""
    fresh = []
    for c in chain:
        c = next((e for e in held_entries(root) if e["c2"] == c["c2"]), c)
        _carry_lift(root, c)
        fresh.append(c)
    lifted = _lift(root, fresh)
    _held_remove(root, done)
    return lifted


def _still_held(root, entries):
    """P8 over held <entries> (oldest first): c2 -> the set of its paths still held -- each whose working copy is still
    its c2 blob, or the c2 blob of a later entry that started from this one's version (its c1 took the path from its
    snapshot at this one's c2 blob), and is no longer HEAD's. A path edited, committed, removed or restored since leaves
    the entry: a later change that starts from a version committed on the stayed branch starts from HEAD's, and keeps no
    earlier entry's path."""
    keep = {e["c2"]: set() for e in entries}
    for p in sorted({p for e in entries for p in e["paths"]}):
        wc, head = sb.worktree_blob(root, p), sb.blob(root, "HEAD", p)
        ok, later_c1 = False, None
        for e in reversed([e for e in entries if p in e["paths"]]):
            mine = e["paths"][p]
            ok = (wc == mine and wc != head) or (ok and later_c1 == mine)
            if ok:
                keep[e["c2"]].add(p)
            later_c1 = sb.blob(root, e["c1"], p) if _from_snapshot(root, e, p) else _NO_LINK
    return keep


def _apply_p8(root, also=()):
    """P8, the step land's retries and retry_held share before their oldest-first walk: over the held entries of the
    record (refused set), each path changed since it was held -- edited, committed, removed or restored, as
    _still_held reads it, with <also> (the run's own change, in land; in no record, or in it under its own c2, and never
    rebuilt here) as the newest link a held entry's path may chain to -- leaves its entry, rebuilt without it
    (held_rebuild); an entry left with no file is dropped. Returns how many were dropped."""
    skip = {x["c2"] for x in also}
    held = [e for e in held_entries(root) if e["refused"] is not None and not e.get("here") and e["c2"] not in skip]
    keep = _still_held(root, held + list(also))
    dropped = 0
    for e in held:
        gone = set(e["paths"]) - keep[e["c2"]]
        if gone and held_rebuild(root, e, gone) is None:
            dropped += 1
    return dropped


def _land_change(root, entry, default, default_ref, register_rebuild, in_record, remote=True, check=None,
                 on_move=None, own=False):
    """The landing's apply and move for one change -- a held entry retried, or the run's own (<entry>, c1 to c2): applied
    onto <default> by sb.own_change, the paths it refuses split off as one permanent held entry (P29), the rest
    committed on the result, journalled, then moved. C2's test first: where another worktree has <default> checked out,
    the result is built on <default-ref> and pushed by refspec where push_check leaves no row but scope (the push names
    one commit on <default-ref>, so push-scope does not apply), the local branch never moved (ruling C2); <remote> False
    keeps the change off that path (P28), as it stands, and <check>(cost) comes before its capped calls; that path
    never builds on local <default>, whose own commits the push would publish unmeasured, so where <default-ref> names
    no commit -- an origin with no <default>, never or no longer -- the change is held, checked-out with the detail
    origin-lacks, permanent (P22). Otherwise onto is <default-ref>'s commit where local <default> is absent or strictly
    behind it, else local <default> -- <default-ref> naming no commit counting as neither -- which
    sb.move_branch(here=False) moves -- created where it is absent -- and a branch-moved or checkout-moved refusal is
    tried once more on the new tip. <in_record>: the entry stands in the held record, where each change to it replaces
    it. Lifts nothing. Returns status landed (its journal entry standing for the caller's lift), there (onto already
    holds the change), stuck-only (onto already holds every path accepted, and some path was refused), or held (the
    entry in the record, refused set); entry, the change as narrowed (None where nothing is left); stuck, the entry
    split off. A refusal on the remote path is {reason: checked-out, path: that worktree, detail, permanent}, its detail
    the CHECKED_OUT_DETAIL object (_push_detail, _row_detail) -- JSON, so the held record keeps it whole -- which
    checked_out_values turns into reason.land.checked-out's values; held with <remote> False, its detail is the entry's
    own refusal's, or None where it had none (no push was tried)."""
    out = {"status": None, "sha": None, "files": 0, "paths": [], "pushed": False, "refused": None, "stuck": None,
           "numbers": None, "entry": entry, "in_record": in_record, "pending": None}
    moved = 0
    for _attempt in range(4):
        elsewhere = sb.checked_out_at(root, default)
        if elsewhere and not remote:
            refused = entry["refused"] or {"reason": "checked-out", "path": elsewhere[0], "detail": None,
                                           "permanent": False}
            return dict(out, status="held", refused=refused)
        local, upstream = sb.rev(root, "refs/heads/" + default), sb.rev(root, default_ref)
        if elsewhere and upstream is None:  # (3): never built on local <default>, whose commits a push would publish
            refused = {"reason": "checked-out", "path": elsewhere[0], "detail": _checked_out_detail("origin-lacks"),
                       "permanent": True}
            break
        if elsewhere and check:
            check(PUSH_COST)
        if local is None and upstream is None:
            raise NotRun("neither %s nor %s names a commit" % (default, default_ref))
        behind = upstream is not None and (local is None or (local != upstream and sb.is_ancestor(root, local, upstream)))
        onto = upstream if upstream is not None and (elsewhere or behind) else local
        got = sb.own_change(root, onto, entry["c1"], entry["c2"], register_rebuild)
        if got["refused"]:
            stuck, rest = _split(root, entry, got["refused"])
            if in_record and rest is None:
                # the entry becomes its stuck half, in its place: their commits share tree, parent and message, so
                # one made in the same second is the same commit, and removing the entry would remove the stuck one
                _held_put(root, stuck, replace=entry["c2"])
            else:
                _held_put(root, stuck)
                if in_record:
                    _held_put(root, rest, replace=entry["c2"])
            out["stuck"] = out["stuck"] or stuck
            if rest is None:
                return dict(out, status="stuck-only", entry=None, in_record=False)
            entry = rest
        out.update(entry=entry, in_record=in_record)
        if got["tree"] == _tree(root, onto):
            return dict(out, status="stuck-only" if out["stuck"] else "there")
        tip = sb.commit_tree(root, got["tree"], [onto], _message(root, entry["c2"]))
        entry = dict(entry, refused=None, old=onto if elsewhere else local, tip=tip, remote_only=bool(elsewhere),
                     onto=default, **{JOURNAL_MOVES: sb._moves([got["numbers"]]) if got["numbers"] else []})
        _held_put(root, entry, replace=entry["c2"] if in_record else None)
        in_record = True
        out.update(entry=entry, in_record=True, pending=_pending(entry))
        if own:  # LandStopped's pending is the run's own change's; a held entry's journal stays in its record
            _PENDING[0] = out["pending"]
        if on_move:
            on_move(_pending(entry))
        paths = _commit_paths(root, tip)
        landed = dict(out, status="landed", sha=tip, paths=paths, files=len(paths), numbers=got["numbers"])
        message = "specs-git: landed " + tip[:7]
        if elsewhere:
            checked = push_check(root, default, default)
            row = checked["row"]
            if row in (None, "scope"):  # one commit on <default-ref>: push-scope does not apply to it
                _wrote()
                pushed = push(root, default, False, src=tip)
                if pushed["outcome"] == "pushed":
                    return dict(landed, pushed=True)
                detail, permanent = _push_detail(pushed), False
            else:
                detail, permanent = _row_detail(checked), row in PERMANENT_ROWS
            refused = {"reason": "checked-out", "path": elsewhere[0], "detail": detail, "permanent": permanent}
            break
        _wrote()
        if local is None:
            made = sb.git(root, "update-ref", "-m", message, "refs/heads/" + default, tip, sb.ZERO, check=False)
            why = None if made.returncode == 0 else {"reason": "branch-moved", "path": None}
        else:
            why = sb.move_branch(root, default, local, tip, here=False, message=message)
        if why is None:
            return landed
        if why["reason"] in ("branch-moved", "checkout-moved"):
            moved += 1
            if moved < 2:
                continue
            refused = {"reason": "moved", "path": None, "detail": why["reason"], "permanent": False}
        elif why["reason"] == "checked-out":
            continue  # a worktree came between: C2's test, again, takes the refspec push
        else:
            refused = {"reason": why["reason"], "path": why.get("path"), "detail": None, "permanent": False}
        break
    else:
        refused = {"reason": "moved", "path": None, "detail": None, "permanent": False}
    entry = dict(entry, refused=refused, old=None, tip=None, remote_only=False)
    _held_put(root, entry, replace=entry["c2"] if in_record else None)
    return dict(out, status="held", refused=refused, entry=entry, in_record=True)


def _waited_on(entries, paths):
    """Of transient held <entries> (oldest first), those a change on <paths> waits for (P7): each sharing a path with
    it, or with a later one that does."""
    want, out = set(paths), []
    for e in reversed(entries):
        if want & set(e["paths"]):
            out.append(e)
            want |= set(e["paths"])
    return out[::-1]


def _on(root, branch):
    """HEAD names refs/heads/<branch> (symbolic-ref -q HEAD)."""
    head = sb.git(root, "symbolic-ref", "-q", "HEAD", check=False).stdout.strip()
    return head == ("refs/heads/" + branch).encode("utf-8", "surrogateescape")


def _index_blobs(root, paths):
    """path -> the blob the index holds for it at stage 0, None where it holds none."""
    out = dict.fromkeys(paths)
    if paths:
        for rec in sb.nul_list(sb.git(root, "ls-files", "-s", "-z", "--", *_literal(paths))):
            meta, _, p = rec.partition("\t")
            fields = meta.split()
            if len(fields) == 3 and fields[2] == "0" and p in out:
                out[p] = fields[1]
    return out


def _restore_index(root, entry):
    """The here form's last step: `restore --staged` over each path the move's tip carries whose index entry before
    the move was the old tip's (both absent counting as equal) and still is -- one staged since is the user's, and
    stays -- so the index follows HEAD there. The paths restored."""
    before = entry.get("index_before") or {}
    now = _index_blobs(root, sorted(before))
    paths = [p for p in sorted(before) if before[p] == sb.blob(root, entry["old"], p) and now[p] == before[p]]
    if paths:
        sb.git(root, "restore", "--staged", "--", *_literal(paths))
    return paths


def _here_move(root, e, in_record, register_rebuild, on_move, own=True):
    """The here form (P2) for the change <e> on HEAD's branch e["branch"]: own_change onto HEAD, given
    <register_rebuild> as the landing on <default> is, so a register the run changed is rebuilt rather than refusing the
    whole change; any refusal: kept, nothing committed and nothing held; nothing to add: there; else the commit on HEAD,
    the journal entry (here, with index_before), <on_move>, HEAD and index.lock rechecked, `update-ref
    refs/heads/<branch> <tip> <old>`, both rechecked again, the index restored (_restore_index), the entry removed. No
    file is written and nothing lifted. A failed recheck before the move removes the entry, nothing moved: with
    index.lock standing, status locked; with HEAD off the branch, LandStopped carrying no pending, there being no move
    to finish. A failed recheck after it: LandStopped carrying pending, the entry kept for the resume or the held stage.
    """
    branch = e["branch"]
    ref = "refs/heads/" + branch
    head = _commit(root, "HEAD")
    got = sb.own_change(root, head, e["c1"], e["c2"], register_rebuild)
    if got["refused"] or got["tree"] == _tree(root, head):
        if in_record:
            _held_remove(root, [e["c2"]])
        if got["refused"]:
            return {"status": "kept", "refused": dict(got["refused"][0], permanent=True)}
        return {"status": "there"}
    tip = sb.commit_tree(root, got["tree"], [head], _message(root, e["c2"]))
    paths = _commit_paths(root, tip)
    journal = dict(e, old=head, tip=tip, refused=None, here=True, onto=branch, remote_only=False,
                   index_before=_index_blobs(root, paths))
    _held_put(root, journal, replace=e["c2"] if in_record else None)
    pending = _pending(journal)
    if own:  # LandStopped's pending is the run's own change's alone
        _PENDING[0] = pending
    if on_move:
        on_move(dict(pending))
    shown, lock = sb.git_paths(root, "index.lock")[0]
    if not _on(root, branch) or os.path.lexists(lock):
        _held_remove(root, [journal["c2"]])
        if os.path.lexists(lock):
            return {"status": "locked", "refused": {"reason": "locked", "path": shown, "detail": None,
                                                    "permanent": False}}
        raise LandStopped("HEAD left %s before the here form moved it; nothing moved" % branch)
    _wrote()
    moved = sb.git(root, "update-ref", "-m", "specs-git: landed " + tip[:7], ref, tip, head, check=False)
    if moved.returncode != 0:
        _held_remove(root, [journal["c2"]])
        raise LandStopped("%s did not move to %s (%s); nothing moved" % (branch, tip[:7], _first_line(moved, error=True)))
    if not _on(root, branch) or os.path.lexists(lock):
        raise LandStopped("%s moved to %s, but %s before its index was restored; end --resume or the next preflight "
                          "restores it" % (branch, tip[:7], "%s stands" % shown if os.path.lexists(lock)
                                           else "HEAD left it"), pending if own else None)
    _restore_index(root, journal)
    _held_remove(root, [journal["c2"]])
    return {"status": "landed", "sha": tip, "files": len(paths), "paths": paths, "pending": pending}


def _finish_here(root, e, register_rebuild, on_move=None, own=False):
    """P2's here journal finished, only where its move is verified: where HEAD names e's branch and it stands at the
    journalled tip, or has it as an ancestor (the open run's end may have committed on top), the index restored;
    where it stands at the journalled old, the here form again; otherwise the entry removed and the files left as they
    stand. (how, result): finished with _here_move's result, dropped, or locked where index.lock stands, the entry
    left for a later call."""
    branch = e["branch"]
    if os.path.lexists(sb.git_paths(root, "index.lock")[0][1]):
        return "locked", None
    at, on = sb.rev(root, "refs/heads/" + branch), _on(root, branch)
    if on and at is not None and e.get("tip") and (at == e["tip"] or sb.is_ancestor(root, e["tip"], at)):
        _restore_index(root, e)
        _held_remove(root, [e["c2"]])
        paths = _commit_paths(root, e["tip"])
        return "finished", {"status": "landed", "sha": e["tip"], "files": len(paths), "paths": paths}
    if on and at is not None and at == e.get("old"):
        return "finished", _here_move(root, e, True, register_rebuild, on_move, own)
    _held_remove(root, [e["c2"]])
    return "dropped", None


def _default_base(root, default, default_ref):
    """The landing's base must exist: local <default>, or <default-ref>'s commit. Where <default-ref> names no commit --
    an origin with no <default> -- local <default> is the only base left (specs-repo-git §4 step 1 (2)); with another
    worktree on <default>, (3) holds the change instead (_land_change). NotRun where neither names a commit."""
    if sb.rev(root, "refs/heads/" + default) is None:
        _commit(root, default_ref)


def land(root, branch, default, default_ref, message, snap, register_rebuild=None, here=False, facts=None,
         on_move=None, resume=None, retry_remote=True, check=None):
    """specs-repo-git §4 step 1's landing for the checkout standing on <branch> (NotRun otherwise): the run's own
    session-file change -- c1, HEAD with the start's snapshot <snap>, to c2, the working copies now -- committed on
    <default> without moving the checkout, then lifted out of the working tree. In order: index.lock standing, in the
    here form or for a resumed journal, locked, nothing written -- the journal left for a later call; c1 and c2
    (_own_commits), nothing where they are one; index.lock standing, the change held for that cause, refused locked, a
    cause that passes (specs-repo-git §4 step 1 (2)) -- built through a temporary index, and neither the held ref nor
    the held record takes the index's lock -- nothing else applied, retried or lifted; P8 over the held entries, as retry_held
    applies it (_apply_p8, the run's own change their newest link); the transient held entries it waits for retried
    first (P7; locally only where <retry_remote> is false, <check>(cost) before their capped calls), one that stays held
    holding this change, and any held entry behind it, with its refused, which the record takes too; then _land_change;
    then _finish: each landing's lift override carried to the entries still held that started from it, the lift over
    every landing, the journal entries removed. The run's own landing takes its place in the chain before any landing
    that started from it (_place): a resumed change is the oldest of the chain it starts. <here>, forced where <branch>
    is <default>: the here form instead (_here_move). <facts> {kind, merged, command, stayed} go into a held entry;
    <on_move>(pending) is called just before the move or the refspec push, once the journal entry is written; a landing's
    pending carries the moves its register rebuild made (JOURNAL_MOVES), which a resumed landing reports. <resume>,
    an earlier call's pending, is landed again from its c1 and c2 -- lifted only where its move is verified (P6) -- and
    its own journal entry is never retried as a held one. LandStopped's pending is the run's own change's journal alone.
    Returns {status: landed, there, nothing, held, kept or locked (the here form, or a resumed journal, under an
    index.lock); sha: the landed commit, or the held one's c2; files;
    paths; lifted; onto: <default>, or <branch> in the here form; pushed: true only on the refspec push; refused; stuck:
    the paths held alone beside a landing; held_landed: [{sha, files, paths, branch}]; moves (sb._moves); pending}."""
    if _head_branch(root) != branch:
        raise NotRun("HEAD is not on %s" % branch)
    _default_base(root, default, default_ref)
    if resume:  # a journal is finished in its own form: a landing's never by the here form
        here = bool(resume.get("here"))
        if not here and branch == default:
            raise NotRun("a landing's journal is not finished with HEAD on %s" % default)
    else:
        here = bool(here or branch == default)
    return _write_bounded(_land, root, branch, default, default_ref, message, snap, register_rebuild, here, facts,
                          on_move, resume, retry_remote, check)


def _land(root, branch, default, default_ref, message, snap, register_rebuild, here, facts, on_move, resume,
          retry_remote, check):
    out = {"status": None, "sha": None, "files": 0, "paths": [], "lifted": [], "onto": branch if here else default,
           "pushed": False, "refused": None, "stuck": None, "held_landed": [], "moves": [], "pending": None}
    shown, lock = sb.git_paths(root, "index.lock")[0]
    locked = {"reason": "locked", "path": shown, "detail": None, "permanent": False} if os.path.lexists(lock) else None
    if locked and (here or resume):  # nothing moved; a resumed journal is left for a later call
        return dict(out, status="locked", refused=locked)
    record = held_entries(root)
    if resume:
        own = next((e for e in record if e["c2"] == resume["c2"]), None)
        in_record = own is not None
        if own is None:
            own = dict(_entry(root, resume["c1"], resume["c2"], default, branch, facts, here),
                       **{k: resume[k] for k in ("old", "tip", "remote_only", "index_before", JOURNAL_MOVES)
                          if k in resume})
    else:
        c1, c2 = _own_commits(root, snap, message)
        if c2 is None:
            return dict(out, status="nothing")
        own, in_record = _entry(root, c1, c2, default, branch, facts, here), False
    if locked:  # held for a cause that passes: nothing applied or lifted, and the held ref takes no index lock
        held = dict(own, refused=locked)
        _held_put(root, held)
        return dict(out, status="held", sha=held["c2"], files=len(held["paths"]), paths=sorted(held["paths"]),
                    refused=locked)
    if here:
        if resume and own.get("tip"):
            how, got = _finish_here(root, own, register_rebuild, on_move, own=True)
            if how == "locked":
                return dict(out, status="locked", refused={"reason": "locked", "path": shown, "detail": None,
                                                           "permanent": False})
            got = got or {"status": "kept", "refused": {"reason": "unfinished", "path": None, "detail": None,
                                                        "permanent": True}}
        else:
            got = _here_move(root, own, in_record, register_rebuild, on_move)
        return dict(out, **{k: got[k] for k in ("status", "sha", "files", "paths", "refused", "pending") if k in got})
    _apply_p8(root, also=[own])  # as retry_held: one answer for one record
    record = held_entries(root)
    chain, done = [], []
    try:
        waiting = [e for e in record if e["refused"] is not None and not e["refused"].get("permanent")
                   and not e.get("here") and e["c2"] != own["c2"]]
        blocked = {}
        for e in _waited_on(waiting, own["paths"]):
            waits = next((blocked[p] for p in sorted(e["paths"]) if p in blocked), None)
            if waits is None:
                got = _land_change(root, e, default, default_ref, register_rebuild, True, remote=retry_remote,
                                   check=check)
                if got["status"] != "held":
                    if got["entry"] is not None:
                        chain.append(got["entry"])
                        done.append(got["entry"]["c2"])
                    if got["status"] == "landed":
                        out["held_landed"].append({"sha": got["sha"], "files": got["files"], "paths": got["paths"],
                                                   "branch": e["branch"]})
                    continue
                waits = got["refused"]
            elif e["refused"] != waits:  # held behind the entry it waits for, with that entry's refusal
                _held_put(root, dict(e, refused=waits, old=None, tip=None, remote_only=False))
            for p in e["paths"]:
                blocked.setdefault(p, waits)
        hold = next((blocked[p] for p in sorted(own["paths"]) if p in blocked), None)
        if hold is not None:  # held behind the entry it waits for (P7), with its refused
            held = dict(own, refused=hold, old=None, tip=None, remote_only=False)
            _held_put(root, held, replace=own["c2"] if in_record else None)
            out.update(status="held", sha=held["c2"], files=len(held["paths"]), paths=sorted(held["paths"]), refused=hold)
        elif resume and own["refused"] is None and _verified(root, own, default):
            chain = _place(root, chain, own)
            done.append(own["c2"])
            paths = _commit_paths(root, own["tip"])
            out.update(status="landed", sha=own["tip"], files=len(paths), paths=paths, pushed=bool(own["remote_only"]),
                       moves=list(own.get(JOURNAL_MOVES) or []))
        else:
            got = _land_change(root, own, default, default_ref, register_rebuild, in_record, on_move=on_move, own=True)
            out["pending"] = got["pending"]
            stuck = got["stuck"]
            if stuck is not None:
                out["stuck"] = {"sha": stuck["c2"], "paths": sorted(stuck["paths"]), "refused": stuck["refused"]}
            if got["status"] == "held":
                out.update(status="held", sha=got["entry"]["c2"], files=len(got["entry"]["paths"]),
                           paths=sorted(got["entry"]["paths"]), refused=got["refused"])
            else:
                if got["entry"] is not None:
                    chain = _place(root, chain, got["entry"])
                    if got["in_record"]:
                        done.append(got["entry"]["c2"])
                if got["status"] == "landed":
                    out.update(status="landed", sha=got["sha"], files=got["files"], paths=got["paths"],
                               pushed=got["pushed"], moves=sb._moves([got["numbers"]]) if got["numbers"] else [])
                elif got["status"] == "there":
                    out["status"] = "there"
                else:  # stuck-only: only refused paths would have changed onto
                    out.update(status="held", sha=stuck["c2"], files=len(stuck["paths"]), paths=sorted(stuck["paths"]),
                               refused=stuck["refused"])
    except _Stop:
        _finish(root, chain, done)
        raise
    out["lifted"] = sorted({x["path"] for _i, x in _finish(root, chain, done)})
    return out


def retry_held(root, default, default_ref, register_rebuild=None, check=None, retry_remote=True):
    """The held stage's primitive (P6, P7, P9, P28, P31). On a detached HEAD nothing at all (P9). Else orphaned held
    refs removed (_held_orphans: none younger than an hour). Each here journal finished where its move is verified
    (_finish_here) -- never dropped for HEAD's place. With HEAD on <default>, or in session-branch mode (sb.mode, read
    here, so the primitive drops them whether or not its caller tested the mode first), every other entry dropped with
    its ref, its files left to the flush, end's commit or §8.2's. Otherwise: P8 first (_apply_p8, which land's retries
    share); then, oldest first, each landing journal lifted where its move is verified (_verified), else landed again as
    a held entry; each permanent entry reported stuck; each transient one landed by _land_change (C2's test and the
    refspec push included; locally only where <retry_remote> is false; <check>(cost) before its capped calls, whose
    _Stop is raised after the landings so far are lifted), unless an earlier one that stays held shares a path with it
    -- then it is reported failed, and recorded, with that entry's refusal. Then _finish: each landing's lift override
    carried to the entries still held that started from it, the lift over every landing, their entries removed. Returns
    {landed: [{sha, files, paths, branch, lifted}], finished: [{sha, here, lifted}], failed and stuck: [{refused,
    branch, kind, command, sha}], dropped: count}; lifted: [{path, blob}], the blob written back (None where removed),
    for P11's snapshot. An error after its first ref write is LandStopped carrying that object as far as it got
    (_retry_report)."""
    _default_base(root, default, default_ref)
    return _write_bounded(_retry_held, root, default, default_ref, register_rebuild, check, retry_remote)


def _retry_held(root, default, default_ref, register_rebuild, check, retry_remote):
    out = {"landed": [], "finished": [], "failed": [], "stuck": [], "dropped": 0}
    info = []
    try:
        return _retry_body(root, default, default_ref, register_rebuild, check, retry_remote, out, info)
    except _Stop:
        raise
    except Exception as e:  # what was done before the error goes with it: land --retry-held reports it
        e.partial = _retry_report(out, info, {})
        raise


def _retry_report(out, info, per):
    """retry_held's object: <out>, with each landing of <info> after the entries reported already -- landed ones with
    their sha, files, paths and branch, finished journals with their tip -- each with its lifted paths from <per>."""
    rep = dict(out, landed=list(out["landed"]), finished=list(out["finished"]))
    for i, (kind, e, got) in enumerate(info):
        if kind == "landed":
            rep["landed"].append({"sha": got["sha"], "files": got["files"], "paths": got["paths"], "branch": e["branch"],
                                  "lifted": per.get(i, [])})
        else:
            rep["finished"].append({"sha": e["tip"] if got is None else None, "here": False, "lifted": per.get(i, [])})
    return rep


def _retry_body(root, default, default_ref, register_rebuild, check, retry_remote, out, info):
    head = _head_branch(root)
    if head is None:  # P9: nothing is done on a detached HEAD, the orphan sweep included
        return out
    for orphan in _held_orphans(root):
        _wrote()
        sb.git(root, "update-ref", "-d", orphan)
    for e in [e for e in held_entries(root) if e.get("here")]:
        how, got = _finish_here(root, e, register_rebuild)
        if how == "finished" and got["status"] in ("landed", "there"):
            out["finished"].append({"sha": got.get("sha"), "here": True, "lifted": []})
        elif how != "locked":
            out["dropped"] += 1
    rest = [e for e in held_entries(root) if not e.get("here")]
    if head == default or sb.mode(root, default)["mode"] == "on":
        _held_remove(root, [e["c2"] for e in rest])
        out["dropped"] += len(rest)
        return out
    out["dropped"] += _apply_p8(root)
    chain, done, blocked = [], [], {}
    try:
        for e in held_entries(root):
            if e.get("here"):
                continue
            if e["refused"] is None and _verified(root, e, default, check):
                chain.append(e)
                done.append(e["c2"])
                info.append(("finished", e, None))
                continue
            if e["refused"] is not None and e["refused"].get("permanent"):
                out["stuck"].append(_held_info(e))
                continue
            waits = next((blocked[p] for p in sorted(e["paths"]) if p in blocked), None)
            if waits is None:
                got = _land_change(root, e, default, default_ref, register_rebuild, True, remote=retry_remote,
                                   check=check)
                if got["stuck"] is not None:
                    out["stuck"].append(_held_info(got["stuck"]))
                if got["status"] != "held":
                    if got["entry"] is not None:
                        chain.append(got["entry"])
                        done.append(got["entry"]["c2"])
                        info.append(("landed" if got["status"] == "landed" else "finished", got["entry"], got))
                    continue
                if got["refused"].get("permanent"):
                    out["stuck"].append(_held_info(got["entry"]))
                    continue
                e, waits = got["entry"], got["refused"]
            elif e["refused"] != waits:  # held behind the entry it waits for, with that entry's refusal
                e = dict(e, refused=waits, old=None, tip=None, remote_only=False)
                _held_put(root, e)
            out["failed"].append(_held_info(e))
            for p in e["paths"]:
                blocked.setdefault(p, waits)
    except _Stop:
        _finish(root, chain, done)
        raise
    per = {}
    for i, x in _finish(root, chain, done):
        per.setdefault(i, []).append(x)
    return _retry_report(out, info, per)


def _default_of(ref):
    """<default>: --default-ref less origin/ (or refs/remotes/origin/) or refs/heads/."""
    for prefix in ("refs/remotes/origin/", "origin/", "refs/heads/"):
        if ref.startswith(prefix) and len(ref) > len(prefix):
            return ref[len(prefix):]
    raise NotRun("usage: --default-ref is origin/<default> or refs/heads/<default>, got %s" % ref)


def _snapshot_arg(root, value):
    """--snapshot's map, from the file it names or, for -, stdin: {path: blob id or null}, each blob one this repository
    holds; NotRun otherwise."""
    try:
        if value == "-":
            data = sys.stdin.buffer.read().decode("utf-8", "surrogateescape")
        else:
            with open(value, encoding="utf-8", errors="surrogateescape") as fh:
                data = fh.read()
        snap = json.loads(data)
    except (OSError, ValueError) as e:
        raise NotRun("--snapshot could not be read: %s" % " ".join(str(e).split()))
    if not isinstance(snap, dict) or not all(isinstance(p, str) and p and (b is None or (isinstance(b, str) and
                                                                                       _OBJECT_ID.fullmatch(b)))
                                             for p, b in snap.items()):
        raise NotRun("--snapshot is not a map of paths to blob ids or null")
    blobs = sorted({b for b in snap.values() if b})
    if blobs:
        asked = "".join(b + "\n" for b in blobs).encode()
        kinds = sb.text(sb.git(root, "cat-file", "--batch-check=%(objecttype)", data=asked))
        if any(k != "blob" for k in kinds.split("\n")):
            raise NotRun("--snapshot names a blob this repository does not hold")
    return snap


def land_cli(a):
    """The land subcommand (P10): a landing, --retry-held or --drop-held, each printing its JSON object. A landing's
    object carries the refusal it ends on as reason, detail, path and permanent: detail is the refusal's own --
    for checked-out the CHECKED_OUT_DETAIL object {outcome, text, remote, record, date, record_error}, from which
    reason.land.checked-out is worded (checked_out_values); for moved, the move's last refusal (branch-moved or
    checkout-moved) or null; for register-rebuild, none or failed; else null."""
    default = _default_of(a.default_ref)
    _default_base(a.specs, default, a.default_ref)
    if a.retry_held or a.drop_held:
        if (a.retry_held and a.drop_held) or a.branch or a.command or a.commit_key or a.snapshot or a.here \
                or (a.drop_held and a.register_rebuild):
            raise NotRun("usage: --retry-held takes --default-ref and --register-rebuild alone, --drop-held "
                         "--default-ref alone")
        if a.drop_held:
            if not re.fullmatch(r"[0-9a-f]{4,64}", a.drop_held):
                raise NotRun("usage: --drop-held takes a held commit's short sha, got %s" % a.drop_held)
            return {"dropped": held_drop(a.specs, a.drop_held), "sha7": a.drop_held, "error": None}
        try:
            return dict(retry_held(a.specs, default, a.default_ref, a.register_rebuild), error=None)
        except LandStopped as e:  # what retry_held did before the error is reported with it
            return dict(e.partial or {"landed": [], "finished": [], "failed": [], "stuck": [], "dropped": 0},
                        error=str(e))
    if not a.branch or not a.command:
        raise NotRun("usage: land needs --branch and --command, or --retry-held, or --drop-held")
    if not _load_module("specs_git_state").COMMAND_RE.fullmatch(a.command):
        raise NotRun("usage: --command is /<name>, got %s" % a.command)
    if a.commit_key is not None and not KEY_RE.fullmatch(a.commit_key):
        raise NotRun("usage: --commit-key is a key of addressing §1's grammar, got %s" % a.commit_key)
    snap = None if a.snapshot is None else _snapshot_arg(a.specs, a.snapshot)
    out = {"status": None, "sha7": None, "files": 0, "paths": [], "lifted": [], "default": default, "pushed": False,
           "reason": None, "detail": None, "path": None, "permanent": None, "stuck": None, "error": None}
    try:
        got = land(a.specs, a.branch, default, a.default_ref, session_subject(a.commit_key, a.command), snap,
                   a.register_rebuild, a.here, {"kind": None, "merged": None, "command": a.command, "stayed": a.branch},
                   retry_remote=False)  # as end's: earlier held entries land locally only (§4 step 1)
    except LandStopped as e:
        return dict(out, error=str(e))
    refused, stuck = got["refused"] or {}, got["stuck"]
    return dict(out, status=got["status"], sha7=got["sha"][:7] if got["sha"] else None, files=got["files"],
                paths=got["paths"], lifted=got["lifted"], pushed=got["pushed"], reason=refused.get("reason"),
                detail=refused.get("detail"), path=refused.get("path"), permanent=refused.get("permanent"),
                stuck=None if stuck is None else {"sha7": stuck["sha"][:7], "paths": stuck["paths"],
                                                  "reason": stuck["refused"]["reason"], "path": stuck["refused"]["path"]})


class Parser(argparse.ArgumentParser):
    """A usage error is one "not run" line, as every exit 2 is."""

    def error(self, message):
        print("specs-git: not run (usage: %s)" % message, file=sys.stderr)
        sys.exit(2)


def main():
    ap = Parser(description="The deterministic git primitives of specs-repo-git and phase-handoff.")
    ap.add_argument("--specs", help="the specs repository's top level; for specs-root-check, SPECS_PATH as set")
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
    p = sub.add_parser("mode")
    p.add_argument("--default", required=True)
    p = sub.add_parser("declined")
    p.add_argument("--command", required=True)
    p.add_argument("--path", action="append", default=[])
    sub.add_parser("specs-root-check")
    p = sub.add_parser("end")
    p.add_argument("--command", required=True)
    p.add_argument("--commit-key")
    p.add_argument("--register-rebuild")
    p.add_argument("--no-preflight", action="store_true")
    p.add_argument("--misrooted-stdin", action="store_true")
    p.add_argument("--session-branch-created")
    p.add_argument("--declined", action="append", default=[])
    p.add_argument("--resume", action="store_true")
    p = sub.add_parser("start")
    p.add_argument("--command", required=True)
    p.add_argument("--key", action="append", default=[])
    p.add_argument("--commit-key")
    p.add_argument("--register-rebuild")
    p.add_argument("--rerun", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--budget", type=float, default=DEFAULT_BUDGET)
    p = sub.add_parser("replay")
    p.add_argument("--for", dest="for_", required=True, choices=("start", "end"))
    p.add_argument("--command", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--set-upstream", action="store_true")
    p.add_argument("--timed-out", action="store_true")
    p = sub.add_parser("land")
    p.add_argument("--branch")
    p.add_argument("--default-ref", required=True)
    p.add_argument("--command")
    p.add_argument("--commit-key")
    p.add_argument("--snapshot")
    p.add_argument("--register-rebuild")
    p.add_argument("--here", action="store_true")
    p.add_argument("--retry-held", action="store_true")
    p.add_argument("--drop-held")
    sub.add_parser("snapshot")
    a = ap.parse_args()
    try:  # a path comes back as git's -z record gave it, a byte that is no UTF-8 included
        sys.stdout.reconfigure(encoding="utf-8", errors="surrogateescape")
    except AttributeError:
        pass
    if a.selftest:
        return selftest()
    if not a.cmd:
        print("specs-git: not run (a subcommand is required)", file=sys.stderr)
        return 2
    try:
        if a.cmd == "owner-repo":
            print(json.dumps(owner_repo_of(a.repo, not a.no_alias), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "declined":
            print(json.dumps(declined(a.command, a.path), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "specs-root-check":  # the --specs exception: SPECS_PATH as set, never checked first
            if a.specs is None:
                raise NotRun("usage: specs-root-check needs --specs, empty where SPECS_PATH is unset")
            print(json.dumps(specs_root_check(a.specs), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "start":  # the --specs exception, as specs-root-check's
            if a.specs is None:
                raise NotRun("usage: start needs --specs, empty where SPECS_PATH is unset")
            print(json.dumps(start(a.specs, a.command, a.key, a.commit_key, a.register_rebuild, a.rerun, a.resume,
                                   a.budget), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "end":  # the --specs exception, as specs-root-check's
            if a.specs is None:
                raise NotRun("usage: end needs --specs, empty where SPECS_PATH is unset")
            notice = None
            if a.misrooted_stdin:
                notice = [line for line in sys.stdin.buffer.read().decode("utf-8", "replace").splitlines() if line.strip()]
            print(json.dumps(end(a.specs, a.command, a.commit_key, a.register_rebuild, a.no_preflight, notice,
                                 a.session_branch_created, a.declined, a.resume), indent=2, ensure_ascii=False))
            return 0
        if not a.specs:
            raise NotRun("--specs is required")
        top = sb.text(sb.git(a.specs, "rev-parse", "--show-toplevel"))
        # branch-merged reads refs and branch-key no repository at all, so both run where
        # $SPECS_PATH sits below the top level: specs-repo-git §3.5 classifies under misrooted.
        if a.cmd not in ("branch-merged", "branch-key") and os.path.realpath(top) != os.path.realpath(a.specs):
            raise NotRun("%s is not its repository's top level (%s)" % (a.specs, top))
        result = dispatch(a)
    except (NotRun, OSError) as e:
        print("specs-git: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
        return 2
    except Exception as e:  # anything unexpected is "not run" on one line, never a traceback
        st = _LOADED.get("specs_git_state")
        if st is not None and isinstance(e, st.NoSession):
            print("specs-git: not run (%s)" % " ".join(str(e).split()), file=sys.stderr)
            return 2
        print("specs-git: not run (%s: %s)" % (type(e).__name__, " ".join(str(e).split())), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
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
    if a.cmd == "mode":
        return sb.mode(a.specs, a.default)
    if a.cmd == "replay":
        return replay(a.specs, a.for_, a.command, a.branch, a.set_upstream, a.timed_out)
    if a.cmd == "land":
        return land_cli(a)
    if a.cmd == "snapshot":
        return snapshot(a.specs)
    raise NotRun("unknown subcommand %s" % a.cmd)


def selftest():
    """Every rule this script carries, on repositories built at run time."""
    failures = []
    count = [0]
    me = os.path.abspath(__file__)
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    os.environ.pop("GIT_USER_INITIALS", None)
    os.environ.pop("CLAUDE_CODE_SESSION_ID", None)

    def check(ok, what):
        count[0] += 1
        if not ok:
            failures.append(what)

    def utc_day():
        """The UTC date _today() gives now: every expected <YYYY-MM-DD> is read when the line it checks is rendered,
        never fixed at the selftest's start, so a run across 00:00 UTC compares each date with its own render's."""
        return _today()

    def local_day():
        """The local date `date +%Y-%m-%d` gives now, as _record_refusal writes it: read when the record is checked."""
        return time.strftime("%Y-%m-%d")

    def dated(call):
        """<call>()'s result, with the dates a line or record it wrote can carry: the UTC dates (utc_day) and the local
        dates (local_day) read just before the call and just after it -- one each, or two where the call crossed
        midnight. A check accepts either, so no crossing, before the call or during it, fails one."""
        utc, local = utc_day(), local_day()
        got = call()
        return got, sorted({utc, utc_day()}), sorted({local, local_day()})

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

    def cli(*args, env=None, stdin=None, cwd=None, script=None):
        return parsed(subprocess.run([sys.executable, script or me, *args], stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, input=stdin, cwd=cwd, env=dict(os.environ, **(env or {}))))

    def shell(line, env):
        """A next.run (or on_timeout) line as the skill runs it: verbatim, in a Bash call of its own."""
        return parsed(subprocess.run(["bash", "-c", line], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=dict(os.environ, **env)))

    def parsed(r):
        out = r.stdout.decode("utf-8", "replace")
        try:
            got = json.loads(out) if out.strip() else {}
        except ValueError:
            got = {"_stdout": out}
        got["_raw"] = r.stdout
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
        check(not any(p.endswith("/x.md") for p in got["artifact"] + got["other"]),
              "status: a rename's original path is no record of its own (%r)" % got)
        check(set(got["other"]) == {frames, shot, prd, threat}, "status: the other list (%r)" % got)
        check(got["artifact"] == sorted(got["artifact"]) and got["other"] == sorted(got["other"]),
              "status: both lists sorted (%r)" % got)
        got = cli("--specs", r.path, "status")
        check(got["_rc"] == 0 and set(got.get("artifact", [])) == {resume, follow, reg, "dev-workflows-cost/y.md"},
              "status: the CLI prints the same object (%r)" % got)
        check(resume.encode("utf-8") in got["_raw"],
              "status: a non-ASCII path is printed as git gave it, never as a \\u escape (%r)" % got["_raw"][:300])
        got = cli("--specs", os.path.join(r.path, "specifications"), "status")
        check(one_not_run_line(got) and "_stdout" not in got and "artifact" not in got,
              "a subdirectory is not the top level: exit 2, one line, no JSON (%r)" % got)
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        got = cli("--specs", plain, "status")
        check(one_not_run_line(got), "a directory that is no repository: exit 2, one line (%r)" % got)
        got = cli("status")
        check(one_not_run_line(got), "no --specs: exit 2, one line (%r)" % got)
        lone = os.path.join(tmp, "lone")
        os.makedirs(lone)
        shutil.copy(me, os.path.join(lone, "specs-git.py"))
        rr = subprocess.run([sys.executable, os.path.join(lone, "specs-git.py"), "--specs", r.path, "status"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        err = rr.stderr.decode("utf-8", "replace").splitlines()
        check(rr.returncode == 2 and len(err) == 1 and err[0].startswith("specs-git: not run ("),
              "a missing session-branch.py exits 2 with one line, no traceback (%r)" % rr.stderr)
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
        r.write("specifications/x.md", "x\n")
        got = cli("--specs", os.path.join(r.path, "specifications"), "branch-merged", "--ref", "prd/A-7-x", "--default-ref", "main")
        check(got["_rc"] == 0 and got.get("merged") is False,
              "branch-merged: runs where $SPECS_PATH is below the top level, as §3.5 does under misrooted (%r)" % got)
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
        sub_dir = os.path.join(r.path, "specifications")
        os.makedirs(sub_dir)
        got = cli("--specs", sub_dir, "branch-key", "--branch", "spec/ACME-77-01-x", "--key", "ACME-77-01")
        check(got["_rc"] == 0 and got.get("key") == "ACME-77-01",
              "branch-key: runs where $SPECS_PATH is below the top level (%r)" % got)
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

        r = with_origin(tmp, "scope-session-2")
        r.git("switch", "-q", "-c", "session/cd")
        r.write("specifications/PRD-A-5-x/prd.md", "p\n")
        bad = r.commit_all("a deliverable, unpushed")
        got = push_scope(r.path, "session/cd", session_default_ref="origin/main")
        check(got["base"] is None and got["failed"] == {"sha": bad, "reason": "paths", "path": "specifications/PRD-A-5-x/prd.md"},
              "push-scope: a never-pushed session branch walks --remotes=origin and fails a deliverable commit (%r)" % got)
        r.git("switch", "-q", "--orphan", "session/ef")
        r.write("specifications/PRD-A-6-x/dev-workflows/resume.md", "r\n")
        r.git("add", "specifications/PRD-A-6-x/dev-workflows/resume.md")
        r.git("commit", "-q", "-m", "a root commit")
        root = r.git("rev-parse", "HEAD")
        got = push_scope(r.path, "session/ef", session_default_ref="origin/main")
        check(got["failed"] == {"sha": root, "reason": "merge", "path": None}, "push-scope: a root commit fails as merge (%r)" % got)

        r = with_origin(tmp, "scope-session-3")
        r.git("switch", "-q", "-c", "session/gh")
        r.write("specifications/PRD-A-7-x/prd.md", "p\n")
        r.commit_all("a deliverable")
        r.git("push", "-q", "-u", "origin", "session/gh")
        r.write("specifications/PRD-A-7-x/dev-workflows/resume.md", "r\n")
        r.commit_all("session")
        got = push_scope(r.path, "session/gh", session_default_ref="origin/main")
        check(got["failed"] == {"sha": None, "reason": "branch-path", "path": "specifications/PRD-A-7-x/prd.md"},
              "push-scope: branch-path with no merge commit names sha null (%r)" % got)
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
            check(got["owner_repo"] == want and "url" not in got,
                  "owner-repo: %s (alias %s) gives %r (%r)" % (url, alias, want, got))
        for url, name in [("https://bitbucket.example.com/scm/proj/docs.git", "bitbucket.example.com/scm/proj/docs"),
                          ("https://gitlab.example.com/group/sub/docs.git", "gitlab.example.com/group/sub/docs"),
                          ("/srv/git/docs.git", "//srv/git/docs"),
                          ("git@github.com:acme/docs.git", "acme/docs"),
                          ("https://github.com/", None)]:
            got = owner_repo(url, resolve_alias=False)
            check(got["name"] == name, "owner-repo: %s's unvalidated derivation, the <docs-repo-slug> source, is %r (%r)"
                  % (url, name, got))
        r = new_repo(tmp, "owner-none")
        got = cli("owner-repo", "--repo", r.path)
        check(got["_rc"] == 0 and all(got.get(k) is None for k in ("host", "slug", "name", "owner_repo")),
              "owner-repo: a repository with no origin gives nulls (%r)" % got)
        r.git("remote", "add", "origin", "https://x-access-token:ghp_FAKE0123@github.com/acme/docs.git")
        got = cli("owner-repo", "--repo", r.path, "--no-alias")
        check(got["_rc"] == 0 and got.get("owner_repo") == "acme/docs", "owner-repo: the CLI (%r)" % got)
        check(b"ghp_FAKE0123" not in got["_raw"] and b"x-access-token" not in got["_raw"],
              "owner-repo: a credential in the remote URL is never printed (%r)" % got["_raw"])
        plain = os.path.join(tmp, "plain-owner")
        os.makedirs(plain)
        got = cli("owner-repo", "--repo", plain)
        check(one_not_run_line(got), "owner-repo: a path that is no repository exits 2 (%r)" % got)

    def scenarios_mode(tmp):
        r = new_repo(tmp, "mode")
        got = cli("--specs", r.path, "mode", "--default", "main")
        check(got["_rc"] == 0 and got.get("mode") == "off" and got.get("source") is None, "mode: off by default (%r)" % got)
        r.git("config", "workflows.sessionBranch", "true")
        got = cli("--specs", r.path, "mode", "--default", "main", env={"GIT_USER_INITIALS": "ab"})
        check(got["_rc"] == 0 and got.get("mode") in ("on", "unsupported") and got.get("source") == "config"
              and got.get("branch") == "session/ab", "mode: the opt-in key turns it on (%r)" % got)

        # Session-branch mode in start and end (specs-repo-git §8). Each world turns the mode on with
        # workflows.sessionBranch and names its identity with GIT_USER_INITIALS=ab, unless a case says otherwise.
        _, lines = _flow()
        g = globals()
        S = "session/ab"
        SB = os.path.join(HERE, "session-branch.py")
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        A, A_FEED = "prd/ACME-2-a", "specifications/PRD-ACME-2-a/dev-workflows/feedback/"
        B = "prd/B-2-y"
        SUBJECT = "NOISSUE Add dev-workflows session artifacts (/feedback)"

        def mode_world(name, initials="ab", on=True):
            r, env = world(tmp, name)
            if on:
                r.git("config", "workflows.sessionBranch", "true")
            if initials:
                env["GIT_USER_INITIALS"] = initials
            return r, env

        def run_start(env, *args):
            return cli("--specs", env["SPECS_PATH"], "start", "--command", "/feedback", *args, env=env)

        def end_of(env, *args):
            return run_end(env, "/feedback", *args)

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", "refs/heads/" + name, check=False) or None

        def sb_cli(r, env, *args):
            """session-branch.py run as a command runs it, to build a world's overlay."""
            subprocess.run([sys.executable, SB, "--specs", r.path, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           env=dict(os.environ, **env), check=True)

        def untracked(r, path):
            return "?? " + path in r.git("status", "--porcelain", "--untracked-files=all")

        def overlay(r, branch=S):
            """The session paths where <branch> differs from HEAD, and whether the working tree holds <branch>'s version
            of each, or none where <branch> lacks it: specs-repo-git §8.3's overlay in place."""
            if ref(r, branch) is None:
                return [], False
            paths = [p for p in r.git("diff", "--name-only", "HEAD", branch).splitlines() if sb.classify(p)]
            ok = True
            for p in paths:
                want = subprocess.run(["git", "-C", r.path, "show", "%s:%s" % (branch, p)], stdout=subprocess.PIPE,
                                      stderr=subprocess.DEVNULL)
                full, have = os.path.join(r.path, p), None
                if os.path.isfile(full):
                    with open(full, "rb") as fh:
                        have = fh.read()
                ok = ok and have == (want.stdout if want.returncode == 0 else None)
            return paths, ok

        def checked_out(r, branch=S):
            """The worktree path git names for the checkout holding <branch>, as session-branch.py's refusal names it."""
            where = None
            for line in r.git("worktree", "list", "--porcelain").splitlines():
                if line.startswith("worktree "):
                    where = line[len("worktree "):]
                elif line == "branch refs/heads/" + branch:
                    return where
            return None

        def not_run(where):
            return ("Specs preflight: session-branch.py could not run (session-branch: not run (%s is checked out at %s; "
                    "switch that checkout back to the default branch))" % (S, where))

        def pushed_session(sha7, n, f):
            return ("Specs repo: committed %s (%s) on session/ab — pushed; %d session file(s) not on main yet: merge its "
                    "pull request, or open one with gh pr create --head session/ab --base main"
                    % (sha7, "1 file" if n == 1 else "%d files" % n, f))

        def left(branch):
            return ("Specs preflight: left %s for main, since no key of this run names it — the branch and its pull "
                    "request are as they were" % branch)

        def wrapped_world(name):
            """w.md tracked on main as v0 and on B as vB; session/ab holds v1, the overlay over B: git refuses B's
            switch to main over that working copy unless it is lifted first."""
            r, env = mode_world(name)
            w = FEED + "w.md"
            r.write(w, "v0\n")
            r.commit_all("NOISSUE v0")
            r.git("push", "-q", "origin", "main")
            r.write(w, "v1\n")
            sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE w")
            sb_cli(r, env, "lift", "--branch", S)
            r.git("switch", "-q", "-c", B)
            r.write(w, "vB\n")
            r.commit_all("NOISSUE vB")
            r.git("push", "-q", "-u", "origin", B)
            sb_cli(r, env, "put-back", "--branch", S, "--default-ref", "origin/main")
            return r, env, w

        def read(r, path):
            with open(os.path.join(r.path, path), encoding="utf-8") as fh:
                return fh.read()

        # m_created
        r, env = mode_world("m-created")
        main = head(r)
        got = run_start(env)
        want = "Specs preflight: created local session/ab at %s; no session file to commit yet" % main[:7]
        check(got["_rc"] == 0 and got.get("mode") == "on" and got.get("session_branch") == S and got.get("error") is None
              and got.get("print") == [env_line(r.path), want] and ref(r, S) == main and got.get("next") is None,
              "m_created: a clean main creates session/ab at its base and says so, nothing to commit (%r)" % got)
        r, env = mode_world("m-created-dirty")
        main = head(r)
        r.write(FEED + "c.md", "c\n")
        got = run_start(env)
        tip = ref(r, S) or ""
        want = "Specs preflight: created local session/ab at %s, and committed %s on it" % (main[:7], tip[:7])
        check(got.get("print") == [env_line(r.path), want] and r.git("rev-parse", tip + "~1", check=False) == main
              and r.git("log", "-1", "--format=%s", tip, check=False) == SUBJECT,
              "m_created: a dirty session file committed on the new session branch, never on HEAD (%r)" % got)
        paths, ok = overlay(r)
        check(on_origin(r, S) == tip and head(r) == main and on_origin(r) == main and paths == [FEED + "c.md"] and ok,
              "m_created: the session branch pushed, main untouched, the overlay in place after start (%r)" % paths)

        # m_created_by_lift: the catch-up's lift finds l.md unpreserved, and its commit creates session/ab -- a creation
        # by §8.3's call, not the flush's, so it is carried (across a --rerun too) to end's line
        r, env = mode_world("m-created-by-lift")
        other = clone(r, "m-created-by-lift-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        main = head(r)
        r.write(FEED + "l.md", "l\n")
        got = run_start(env)
        check(got.get("print") == [env_line(r.path)] and head(r) == on_origin(r) and on_origin(r, S) == ref(r, S)
              and (record(env, "/feedback") or {}).get("session_branch_created") == main[:7],
              "m_created_by_lift: no pre.created line, the creation saved for end (%r)" % got)
        got = run_start(env, "--rerun")
        check((record(env, "/feedback") or {}).get("session_branch_created") == main[:7], "m_created_by_lift: --rerun carries it")
        r.write(FEED + "l2.md", "l2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 2) + "; this run created local session/ab at " + main[:7]],
              "m_created_by_lift: end's line appends it (%r)" % got)

        # m_land_merged: in the mode the session files never commit on HEAD (§8.2), so no stay is kept and no landing
        # runs: G1 on a merged plugin branch prints the plain block, records no stay, and end commits on session/ab and
        # pushes, as the mode does
        r, env = mode_world("m-land-merged")
        M = "prd/M-1-x"
        r.git("switch", "-q", "-c", M)
        r.write("specifications/PRD-M-1-x/prd.md", "m\n")
        r.commit_all("M-1 work")
        r.git("push", "-q", "-u", "origin", M)
        other = clone(r, "m-land-merged-other")
        other.git("merge", "-q", "--ff-only", "origin/" + M)
        other.git("push", "-q", "origin", "main")
        r.write("notes.md", "n\n")
        r.write(FEED + "d.md", "d\n")
        h = head(r)
        plain = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), plain] and got.get("branch") == M
              and (record(env, "/feedback") or {}).get("stay") is None,
              "m_land_merged: the mode's G1 is the plain block, and no stay is recorded (%r)" % got)
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("row") == "pushed-session" and got.get("print") == [
                  pushed_session(tip[:7], 1, 1) + "; this run created local session/ab at " + h[:7], plain]
              and on_origin(r, S) == tip and head(r) == h and r.git("symbolic-ref", "--short", "HEAD") == M,
              "m_land_merged: end commits on session/ab and pushes, HEAD unmoved (%r)" % got)

        # m_no_stay: G1 on a branch no key of the run names, in the mode -- whose commit takes every session file the
        # overlay holds, keeping no snapshot apart (specs-repo-git §3.5) -- keeps no stay and takes no snapshot, so no
        # object is written for the session file in the working tree
        r, env = mode_world("m-no-stay")
        other_key(r)
        r.write("notes.md", "n\n")
        mine = FEED + "m.md"
        r.write(mine, "m-no-stay\n")
        plain = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        got = run_start(env, "--key", "ACME-1")
        rec = record(env, "/feedback") or {}
        unstored = subprocess.run(["git", "-C", r.path, "cat-file", "-e", r.git("hash-object", "--", mine)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0
        check(got.get("print") == [env_line(r.path), plain] and got.get("mode") == "on"
              and "stay" in got and got["stay"] is None and "start_dirty" in got and got["start_dirty"] is None
              and rec.get("stay") is None and rec.get("start_dirty") is None and unstored,
              "m_no_stay: the plain block, no stay, no snapshot, no object written (%r)" % got)

        # m_end_pushed
        r, env = mode_world("m-end-pushed")
        run_start(env)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got["_rc"] == 0 and got.get("row") == "pushed-session" and got.get("print") == [pushed_session(tip[:7], 1, 1)]
              and got.get("branch") == S and got.get("pushed") is True and got.get("next") is None
              and on_origin(r, S) == tip and r.git("log", "-1", "--format=%s", tip) == SUBJECT
              and record(env, "/feedback") is None,
              "m_end_pushed: committed on session/ab and pushed, <F> counted against main (%r)" % got)
        r.write(FEED + "e2.md", "e2\n")
        got = end_of(env, "--session-branch-created", "abc1234")
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 2) + "; this run created local session/ab at abc1234"],
              "m_end_pushed: --session-branch-created appends the created clause (%r)" % got)
        got = end_of(env)
        check(got.get("row") == "nothing" and got.get("print") == ["Specs repo: no session artifacts to commit"]
              and ref(r, S) == tip, "m_end_pushed: commit's committed null is nothing to commit, nothing pushed (%r)" % got)
        r, env = mode_world("m-no-remote")
        r.git("remote", "remove", "origin")
        r.write(FEED + "n.md", "n\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == ["Specs repo: committed %s (1 file) on session/ab — not pushed: this specs repo has no "
                                   "origin remote; this run created local session/ab at %s" % (tip[:7], head(r)[:7])],
              "m_end_pushed: a not-pushed row names the session branch (%r)" % got)
        r, env = mode_world("m-end-created")
        main = head(r)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [pushed_session(tip[:7], 1, 1) + "; this run created local session/ab at " + main[:7]],
              "m_end_pushed: a session branch end's own commit created is appended as created (%r)" % got)

        # m_no_identity
        r, env = mode_world("m-no-identity", initials=None)
        r.write(RESUME, "r\n")
        got = end_of(env)
        want = ("Specs repo: NOT COMMITTED — session-branch mode is on and no identity names its branch; set "
                "GIT_USER_INITIALS (or git config user.initials), and the next run commits these files")
        check(got["_rc"] == 0 and got.get("row") == "no-identity" and got.get("print") == [want] and untracked(r, RESUME)
              and not r.git("for-each-ref", "refs/heads/session"), "m_no_identity: end commits nothing (%r)" % got)
        r.git("switch", "-q", "-c", B)
        r.write("specifications/PRD-B-2-y/prd.md", "b\n")
        r.git("add", "specifications/PRD-B-2-y/prd.md")
        r.git("commit", "-q", "-m", "B-2 Add the PRD")
        r.git("push", "-q", "-u", "origin", B)
        got = run_start(env)
        placed = os.path.join(r.path, r.git("rev-parse", "--git-path", "session-branch-placed.json"))
        check(got.get("mode") == "on" and got.get("session_branch") is None and got.get("print") == [env_line(r.path), left(B)]
              and got.get("branch") == "main" and untracked(r, RESUME) and not r.git("for-each-ref", "refs/heads/session")
              and not os.path.exists(placed),
              "m_no_identity: start's B4 switches unwrapped, the session file carried, nothing lifted (%r)" % got)

        # m_not_run
        r, env = mode_world("m-not-run")
        r.git("branch", S, "main")
        r.git("worktree", "add", "-q", os.path.join(tmp, "m-not-run-wt"), S)
        where = checked_out(r)
        r.write(RESUME, "r\n")
        got = run_start(env)
        check(got["_rc"] == 0 and got.get("error") is None and where
              and got.get("print") == [env_line(r.path), not_run(where), not_run(where)] and untracked(r, RESUME),
              "m_not_run: the flush's commit and the closing put-back each report it, and the run goes on (%r)" % got)
        got = end_of(env)
        want = ("Specs repo: NOT COMMITTED — session-branch.py could not run (session-branch: not run (%s is checked out "
                "at %s; switch that checkout back to the default branch)); the files stay in your working tree, and the "
                "next run commits them" % (S, where))
        check(got.get("row") == "session-not-run" and got.get("print") == [want] and untracked(r, RESUME),
              "m_not_run: end's session-not-run row names the checkout (%r)" % got)
        # the flush's commit could not run, yet what an earlier run left on the session branch is still pushed (§4 step 5)
        wt = Repo(os.path.join(tmp, "m-not-run-wt"))
        wt.write(FEED + "w.md", "w\n")
        wt.commit_all(SUBJECT)
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), not_run(where), not_run(where)] and on_origin(r, S) == ref(r, S),
              "m_not_run: the session branch's own commits pushed all the same (%r)" % got)

        # m_g2
        found = ("⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE\n\n"
                 "Found:    %s is on branch `%s`, which is neither the default\n"
                 "          branch (`main`) nor a plugin branch (idea/ prd/ ard/ spec/\n"
                 "          epics/ design/ ready/ brd/ frames/ kb/ conformance/).\n")
        def g2_session(path, branch):
            return (found % (path, branch)
                    + "Not done: the preflight did not switch away from it — the plugin manages only branches it created. "
                      "This run's artifacts WILL be committed on session/ab, the session branch this specs repository uses "
                      "because its default branch takes no push, and not on %s.\n"
                      "Fix:\n"
                      "If ignored: nothing changes for the artifacts, and nothing is to be run for them: they reach main "
                      "through session/ab's pull request."
                    % branch)

        def g2_no_identity(path, branch):
            return (found % (path, branch)
                    + "Not done: the preflight did not switch away from it — the plugin manages only branches it created. "
                      "Session-branch mode is on and no identity names its branch, so this run's artifacts will NOT be "
                      "committed until one is set.\n"
                      "Fix:\n"
                      "If ignored: the artifacts stay in your working tree, and the first run after you set "
                      "GIT_USER_INITIALS, or git -C \"%s\" config user.initials, to your initials commits them." % path)

        r, env = mode_world("m-g2")
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env)
        want = g2_session(r.path, "feature/x")
        check(got.get("print") == [env_line(r.path), want] and got.get("guard") == "G2",
              "m_g2: on another branch, G2's session-branch lines (%r)" % got)
        r.git("switch", "-q", "-c", S, "main")
        got = run_start(env)
        want = (found % (r.path, S)
                + "Not done: the preflight did not switch away from it. It is this specs repository's session branch, "
                  "which the plugin commits to only while nothing stands on it, so this run's artifacts will NOT be "
                  "committed.\n"
                  "Fix:      git -C \"%s\" switch main\n"
                  "If ignored: the artifacts stay in your working tree, and the first run after you switch back commits "
                  "them." % r.path)
        check(got.get("print") == [env_line(r.path), want, not_run(checked_out(r))] and got.get("guard") == "G2",
              "m_g2: on session/ab itself its own variant, then the closing put-back's refusal (%r)" % got)
        r, env = mode_world("m-g2-no-identity", initials=None)
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env)
        check(got.get("print") == [env_line(r.path), g2_no_identity(r.path, "feature/x")] and got.get("guard") == "G2"
              and got.get("session_branch") is None, "m_g2: with no identity, its no-identity variant (%r)" % got)
        # §5's precedence: a direct /implement run from inside the specs repository takes the mode's variants
        for initials, block in (("ab", g2_session), (None, g2_no_identity)):
            r, env = mode_world("m-g2-implement-%s" % (initials or "none"), initials=initials)
            r.git("switch", "-q", "-c", "feature/x")
            got = cli("--specs", r.path, "start", "--command", "/implement", env=env, cwd=r.path)
            check(got.get("print") == [env_line(r.path), block(r.path, "feature/x")] and got.get("guard") == "G2",
                  "m_g2: a direct /implement run in the mode takes the mode's variant, identity %r (%r)" % (initials, got))

        # m_unsupported
        r, env = mode_world("m-unsupported")
        fake = os.path.join(tmp, "m-unsupported-bin")
        os.makedirs(fake)
        with open(os.path.join(fake, "git"), "w", encoding="utf-8") as fh:
            fh.write('#!/bin/sh\nfor x in "$@"; do\n  if [ "$x" = merge-tree ]; then\n'
                     '    echo "usage: git merge-tree <base-tree> <branch1> <branch2>" >&2\n    exit 129\n  fi\ndone\n'
                     'exec "%s" "$@"\n' % shutil.which("git"))
        os.chmod(os.path.join(fake, "git"), 0o755)
        env["PATH"] = fake + os.pathsep + os.environ.get("PATH", "")
        r.write(FEED + "u.md", "u\n")
        got = run_start(env)
        check(got.get("mode") == "unsupported" and got.get("session_branch") is None and got.get("print") == [env_line(r.path)]
              and r.git("log", "-1", "--format=%s") == SUBJECT and on_origin(r) == head(r)
              and not r.git("for-each-ref", "refs/heads/session"),
              "m_unsupported: start runs as with the mode off, its flush committing on main (%r)" % got)
        r.write(FEED + "u2.md", "u2\n")
        got = end_of(env)
        want = ("Specs repo: committed %s (1 file) on main — pushed straight to main, and no pull request was opened: this "
                "plugin lands its session files there without review; to land them through a pull request of your own "
                "instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true; "
                "session-branch mode is on for this clone, but this git's merge-tree cannot merge without a checkout (it "
                "needs --write-tree and -X), so these files stay on main until git is upgraded" % (head(r)[:7], r.path))
        check(got.get("row") == "pushed-default" and got.get("print") == [want],
              "m_unsupported: end's line ends with the unsupported clause (%r)" % got)
        r.git("checkout", "-q", "--detach")
        r.write(FEED + "u3.md", "u3\n")
        got = end_of(env)
        check(got.get("row") == "blocked" and (got.get("print") or [""])[0] == "Specs repo: NOT COMMITTED — see the notice below",
              "m_unsupported: no unsupported clause on a detached HEAD, which names no branch (%r)" % got)
        run_start(env)
        got = end_of(env)
        check(got.get("row") == "blocked" and (record(env, "/feedback") is None)
              and (got.get("print") or [""])[0] == "Specs repo: NOT COMMITTED — see the notice below",
              "m_unsupported: nor on the blocked flag start recorded in that mode (%r)" % got)

        # m_wrapped_b4
        r, env, w = wrapped_world("m-wrapped-b4")
        before = overlay(r)
        got = run_start(env)
        paths, ok = overlay(r)
        check(before == ([w], True) and read(r, w) == "v1\n", "m_wrapped_b4: the overlay holds w.md over B (%r)" % (before,))
        check(got.get("print") == [env_line(r.path), left(B)] and got.get("error") is None and got.get("branch") == "main"
              and got.get("b4_left") == B and paths == [w] and ok and read(r, w) == "v1\n" and on_origin(r, S) == ref(r, S),
              "m_wrapped_b4: B4 switches inside lift and put-back, the overlay back over main (%r)" % got)
        # the re-run's switch back is wrapped the same way: B's version of w.md differs from main's
        got = run_start(env, "--rerun", "--key", "B-2")
        paths, ok = overlay(r)
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == B and got.get("b4_left") is None
              and paths == [w] and ok and read(r, w) == "v1\n",
              "m_wrapped_b4: the re-run's switch back inside lift and put-back, the overlay over B again (%r)" % got)

        # m_wrapped_catch_up: origin's main changed follow-ups.md, which the overlay holds, so git refuses the pull over
        # it unless it is lifted first -- start's §3.4 catch-up, and end's §4 step 2 for a run whose preflight never ran
        fu = "specifications/PRD-ACME-1-x/follow-ups.md"
        for kind in ("start", "end"):
            r, env = mode_world("m-catch-up-" + kind)
            r.write(fu, "- [ ] a\n")
            r.commit_all("NOISSUE a")
            r.git("push", "-q", "origin", "main")
            r.write(fu, "- [ ] a\n- [ ] b\n")
            sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE b")
            o = clone(r, "m-catch-up-%s-other" % kind)
            o.write(fu, "- [ ] a\n- [ ] c\n")
            o.commit_all("NOISSUE c")
            o.git("push", "-q", "origin", "main")
            if kind == "start":
                got = run_start(env)
                want, overlaid = [env_line(r.path)], [fu]
            else:  # e.md is not on the session branch yet, so the lift's commit carries it before the pull (§8.3)
                r.git("fetch", "-q", "origin")
                r.write(FEED + "e.md", "e\n")
                got = end_of(env)
                carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
                want, overlaid = [pushed_session(carried[:7], 1, 2)], [FEED + "e.md", fu]
                check(r.git("log", "-1", "--format=%s", carried) == SUBJECT and carried != ref(r, S),
                      "m_wrapped_catch_up: end's run commit is the lift's, step 4's message, below put-back's merge")
            paths, ok = overlay(r)
            check(got.get("print") == want and head(r) == on_origin(r) and read(r, fu) == "- [ ] a\n- [ ] b\n- [ ] c\n"
                  and paths == overlaid and ok and on_origin(r, S) == ref(r, S),
                  "m_wrapped_catch_up: %s's pull inside lift and put-back, origin's change merged into the session "
                  "branch and back over the checkout, which then pushes it (%r)" % (kind, got))

        # m_sync_conflict: origin's main changed implementation.md's header while the session branch edited its entry,
        # so §8.2 step 3 refuses that merge; end says so, and <F> counts what the session branch's pull request shows
        im = "specifications/PRD-ACME-1-x/implementation.md"
        entry = "## 2026-01-01 — /implement\n\n%s\n"
        r, env = mode_world("m-sync-conflict")
        r.write(im, "# Implementation\n\n" + entry % "x")
        r.commit_all("NOISSUE x")
        r.git("push", "-q", "origin", "main")
        r.write(im, "# Implementation\n\n" + entry % "y")
        sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE y")
        o = clone(r, "m-sync-conflict-other")
        o.write(im, "# Implementation log\n\n" + entry % "x")
        o.write("notes.md", "n\n")
        o.commit_all("NOISSUE header, and notes")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
        check(got.get("print") == [pushed_session(carried[:7], 1, 2) + "; merging main into session/ab left " + im
                                   + " unsettled — settle them in its pull request"] and on_origin(r, S) == ref(r, S),
              "m_sync_conflict: the conflict appended, <F> the session files the three-dot diff lists (%r)" % got)

        # m_end_commit_not_run (in process): the lift's commit carried e.md, then step 4's commit could not run
        r, env = mode_world("m-end-commit-not-run")
        other = clone(r, "m-end-commit-not-run-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        r.write(FEED + "e.md", "e\n")
        main = head(r)
        real_commit, made = sb.commit, []

        def second_fails(*args):
            made.append(args)
            if len(made) > 1:
                raise NotRun("boom")
            return real_commit(*args)

        sb.commit = second_fails
        try:
            with in_env(env):
                got = end(r.path, "/feedback")
        finally:
            sb.commit = real_commit
        carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "e.md")
        check(got.get("print") == ["Specs repo: session-branch.py could not run (session-branch: not run (boom))",
                                   pushed_session(carried[:7], 1, 1) + "; this run created local session/ab at " + main[:7]]
              and got.get("row") == "pushed-session"
              and on_origin(r, S) == ref(r, S) and len(made) == 2,
              "m_end_commit_not_run: reported, and the lift's commit is the run's, pushed (%r)" % got)

        # m_branch_path: another clone pushed a deliverable on session/ab; its merge makes the session branch's whole
        # change name a path that is no session file, so §8.4's push-scope fails with branch-path (§6's session form)
        r, env = mode_world("m-branch-path")
        o = clone(r, "m-branch-path-other")
        o.git("switch", "-q", "-c", S)
        o.write("specifications/PRD-ACME-3-z/prd.md", "z\n")
        o.commit_all("ACME-3 Add the PRD, on the session branch")
        o.git("push", "-q", "origin", S)
        main = head(r)
        r.write(FEED + "b1.md", "b1\n")
        got = run_start(env)
        b1 = r.git("log", "-1", "--format=%H", S, "--", FEED + "b1.md")
        merge = r.git("rev-list", "--merges", "-n", "1", S)
        check(got.get("print") == [env_line(r.path), "Specs preflight: created local session/ab at %s, and committed %s on it"
                                   % (main[:7], b1[:7])] and on_origin(r, S) == ref(o, S) and merge,
              "m_branch_path: the flush merges origin's copy and pushes nothing (%r)" % got)
        r.write(FEED + "b2.md", "b2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = ("Specs repo: committed %s (1 file) on session/ab — not pushed: its pull request would also change "
                "specifications/PRD-ACME-3-z/prd.md, which is not one of this plugin's session files, and the branch's newest "
                "merge commit is %s NOISSUE Merge origin/session/ab into session/ab; push session/ab once that change is "
                "ready to go, and the artifacts go with it" % (tip[:7], merge[:7]))
        check(got.get("row") == "scope" and got.get("print") == [want] and got.get("error") is None
              and on_origin(r, S) == ref(o, S) and record(env, "/feedback") is None,
              "m_branch_path: end's push-scope row in its session-branch form, the record removed (%r)" % got)

        # m_end_resume (in process): a kill while §8.2's commit runs; end --resume finds what landed and pushes it
        real_commit = sb.commit

        def killed(*args):
            real_commit(*args)
            raise KeyboardInterrupt

        for name, existing in (("m-end-resume", False), ("m-end-resume-existing", True)):
            r, env = mode_world(name)
            if existing:
                r.git("branch", S, "main")
            main = head(r)
            r.write(FEED + "k.md", "k\n")
            sb.commit = killed
            try:
                with in_env(env):
                    try:
                        end(r.path, "/feedback")
                    except KeyboardInterrupt:
                        pass
            finally:
                sb.commit = real_commit
            pending = (record(env, "/feedback") or {}).get("end_commit") or {}
            check(pending == {"branch": S, "base": main if existing else None, "session": {}},
                  "m_end_resume: the pending end_commit saved before the commit (%s: %r)" % (name, pending))
            got = end_of(env, "--resume")
            carried = r.git("log", "-1", "--format=%H", S, "--", FEED + "k.md")
            want = pushed_session(carried[:7], 1, 1) + ("" if existing else "; this run created local session/ab at "
                                                        + main[:7])
            check(got.get("print") == [want] and got.get("record") == "found" and on_origin(r, S) == ref(r, S)
                  and record(env, "/feedback") is None,
                  "m_end_resume: --resume pushes the commit the kill left unnamed (%s: %r)" % (name, got))

        # m_blocked: both blocked rows carry the created clause, the one session-branch append §6 gives them
        blocked = "Specs repo: NOT COMMITTED — see the notice below; this run created local session/ab at abc1234"
        r, env = mode_world("m-blocked")
        r.git("checkout", "-q", "--detach")
        r.write(RESUME, "r\n")
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "blocked" and len(got.get("print") or []) == 2 and got["print"][0] == blocked
              and got["print"][1].startswith("⚠ SPECS REPO — THIS RUN'S ARTIFACTS WILL NOT BE COMMITTED"),
              "m_blocked: G0's state at end, the created clause appended (%r)" % got)
        got = run_start(env)
        block = (got.get("print") or ["", ""])[1]
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "blocked" and got.get("print") == [blocked, block],
              "m_blocked: the blocked flag start recorded, the created clause appended (%r)" % got)
        os.remove(os.path.join(r.path, RESUME))
        got = end_of(env, "--session-branch-created", "abc1234")
        check(got.get("row") == "nothing" and got.get("print") == [
            "Specs repo: no session artifacts to commit; this run created local session/ab at abc1234"],
              "m_blocked: the detached HEAD's nothing row takes the created clause too (%r)" % got)

        # m_not_finished (in process): §1 rule 5's line takes none of a row's appends, and a G2 block still follows it
        real_check = g["push_check"]

        def broken(*args, **kwargs):
            raise RuntimeError("boom")

        stop = ("Specs repo: NOT FINISHED — the terminal step stopped early (RuntimeError: boom); what it committed or "
                "pushed is as it left it, and the next run's preflight flushes the rest")
        r, env = mode_world("m-not-finished")
        r.git("switch", "-q", "-c", "feature/x")
        block = (run_start(env).get("print") or ["", ""])[1]
        r.write(FEED + "n.md", "n\n")
        r2, env2 = mode_world("m-not-finished-unsupported", on=False)
        seed(env2, "/feedback", mode="unsupported", session_branch_created="abc1234")
        r2.write(RESUME, "r\n")
        g["push_check"] = broken
        try:
            with in_env(env):
                got = end(r.path, "/feedback", session_branch_created="abc1234")
            with in_env(env2):
                got2 = end(r2.path, "/feedback")
        finally:
            g["push_check"] = real_check
        check(got.get("print") == [stop, block] and got.get("error") == "RuntimeError: boom"
              and block == g2_session(r.path, "feature/x"),
              "m_not_finished: no created clause, and the G2 block start saved after the line (%r)" % got)
        check(got2.get("print") == [stop], "m_not_finished: no unsupported clause either (%r)" % got2)
        # a resumed record holding a G1 block, stopped before its push step: the line, then the block, in the
        # not-committed form §5 gives the NOT FINISHED line
        r, env = mode_world("m-not-finished-resume", on=False)
        g1_block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})
        rows = g1_block.split("\n")
        at = {x: next(k for k, row in enumerate(rows) if row.startswith(x)) for x in ("Not done:", "Fix:", "If ignored:")}
        g1_stopped = "\n".join(rows[:at["Not done:"]] + ["Not done: " + lines.T["g1.not_done.uncommitted"]]
                               + rows[at["Fix:"]:at["If ignored:"]] + ["If ignored: " + lines.T["g1.if_ignored.uncommitted"]])
        seed(env, "/feedback", default=None, guard="G1", guard_block=g1_block, guard_paths=["notes.md"],
             end_commit={"sha7": "abc1234", "files": 1, "branch": "main", "paths": [RESUME], "hook_paths": []})
        real_default = g["resolve_default"]
        g["resolve_default"] = broken
        try:
            with in_env(env):
                got = end(r.path, "/feedback", resume=True)
        finally:
            g["resolve_default"] = real_default
        check(got.get("print") == [stop, g1_stopped] and got.get("record") == "found",
              "m_not_finished: end --resume's stop before its push step still repeats the block (%r)" % got)
        r, env = mode_world("m-not-finished-replay")
        seed(env, "/feedback", guard="G2", guard_block="the G2 block")
        got = cli("--specs", r.path, "replay", "--for", "end", "--command", "/feedback", "--branch", "main", env=env)
        check(got.get("_rc") == 0 and got.get("error") and len(got.get("print") or []) == 2
              and got["print"][0].startswith("Specs repo: NOT FINISHED — ") and got["print"][1] == "the G2 block",
              "m_not_finished: replay --for end's stop is followed by the block too (%r)" % got)

        # m_misrooted: §8.1 is never resolved under misrooted, so nothing of the mode runs
        r, env = mode_world("m-misrooted")
        os.makedirs(os.path.join(r.path, "specs"))
        got = cli("--specs", os.path.join(r.path, "specs"), "start", "--command", "/feedback", env=env)
        check(got.get("specs_git") == "misrooted" and got.get("mode") is None and got.get("session_branch") is None
              and len(got.get("print") or []) == 2 and not r.git("for-each-ref", "refs/heads/session"),
              "m_misrooted: no mode, no session branch, no session-branch line (%r)" % got)

        # m_budget_overlay (m9): a catch-up to make and a settle push, at --budget 0, against one call on a copy
        r, env = mode_world("m-budget")
        r.git("switch", "-q", "-c", A, "main")
        r.git("push", "-q", "-u", "origin", A)
        r.write(A_FEED + "f.md", "f\n")
        r.commit_all("NOISSUE f")
        r.git("switch", "-q", "main")
        o_path = FEED + "o.md"
        r.write(o_path, "o\n")
        sb_cli(r, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE o")
        other = clone(r, "m-budget-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        c_bare, c_path = os.path.join(tmp, "m-budget-copy.git"), os.path.join(tmp, "m-budget-copy")
        shutil.copytree(r.bare, c_bare, symlinks=True)
        shutil.copytree(r.path, c_path, symlinks=True)
        copy = Repo(c_path)
        copy.bare = c_bare
        copy.git("remote", "set-url", "origin", c_bare)
        c_env = dict(env, HOME=os.path.join(tmp, "home-m-budget-copy"), CLAUDE_CODE_SESSION_ID="m-budget-copy",
                     SPECS_PATH=c_path)
        os.makedirs(c_env["HOME"])

        def stamp():
            st = os.stat(os.path.join(r.path, o_path))
            return st.st_ino, st.st_mtime_ns

        untouched = stamp()
        calls = [run_start(env, "--budget", "0")]
        check(stamp() == untouched, "m_budget_overlay: the call that stopped before the catch-up lifted nothing")
        states = [overlay(r)]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
            states.append(overlay(r))
        resume0 = " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(r.path), "start", "--command", "/feedback",
                            "--budget", "0", "--resume"])
        check(len(calls) == 3 and all(c["_rc"] == 0 and c.get("error") is None for c in calls)
              and all(c["next"] == {"run": resume0, "timeout_ms": 600000, "on_timeout": None} for c in calls[:-1])
              and calls[-1].get("next") is None and on_origin(r) == head(r) and on_origin(r, A) == ref(r, A)
              and on_origin(r, S) == ref(r, S),
              "m_budget_overlay: a stop before the catch-up's lift, one before the settle push, then the end (%r)"
              % [c.get("print") for c in calls])
        check(states == [([o_path], True)] * 3,
              "m_budget_overlay: at every call's return no lift stands without its put-back (%r)" % states)
        one = run_start(c_env)
        stitched = [p for c in calls for p in c.get("print") or []]

        def trees(repo):
            return repo.git("for-each-ref", "--format=%(refname) %(tree)", "refs/heads")

        check(one.get("next") is None and [p.replace(c_path, r.path) for p in one.get("print") or []]
              == [p.replace(env_line(r.path), env_line(c_path).replace(c_path, r.path)) for p in stitched]
              and trees(copy) == trees(r) and read(copy, o_path) == read(r, o_path)
              and all(on_origin(copy, b) == on_origin(r, b) for b in ("main", A))
              and (record(c_env, "/feedback") or {}).get("stage") == (record(env, "/feedback") or {}).get("stage") == "done",
              "m_budget_overlay: following next ends as one call would (%r, %r)" % (one.get("print"), stitched))

        # m_no_replay: no replay is handed out in session-branch mode
        r, env = mode_world("m-no-replay")
        r.git("switch", "-q", "-c", A, "main")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "m-no-replay-other")
        o.git("switch", "-q", A)
        o.write(A_FEED + "o.md", "o\n")
        o.commit_all("NOISSUE o")
        o.git("push", "-q", "origin", A)
        r.write(A_FEED + "r.md", "r\n")
        r.commit_all("NOISSUE r")
        r.git("switch", "-q", "main")
        r.git("branch", S, "main")
        got = run_start(env)
        rec = record(env, "/feedback") or {}
        p = r.path
        want = ("Specs preflight: %s — push REJECTED: origin's %s has commits this one lacks, and the run could not take "
                "them in: session-branch mode is on, which replays nothing; run python3 \"%s\" --specs \"%s\" lift --branch "
                "session/ab, then git -C \"%s\" switch %s, git -C \"%s\" pull --rebase --no-autostash origin %s and git -C "
                "\"%s\" push origin %s, then switch back to main, then python3 \"%s\" --specs \"%s\" put-back --branch "
                "session/ab --default-ref origin/main" % (A, A, SB, p, p, A, p, A, p, A, SB, p))
        check(got.get("print") == [env_line(p), want] and got.get("next") is None and rec.get("pending") == []
              and rec.get("stage") == "done" and on_origin(r, A) == head(o),
              "m_no_replay: a settle push rejected in the mode names no replay, its remedy wrapped (%r)" % got)
        r, env = mode_world("m-session-rejected")
        run_start(env)
        o = clone(r, "m-session-rejected-other")
        o.git("config", "workflows.sessionBranch", "true")
        o.write(FEED + "o.md", "o\n")
        sb_cli(o, env, "commit", "--branch", S, "--default-ref", "origin/main", "--message", "NOISSUE o")
        o.git("push", "-q", "origin", S)
        r.write(FEED + "r.md", "r\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = ("Specs repo: committed %s (1 file) on session/ab — push REJECTED: origin's session/ab has commits this clone "
                "lacks, pushed from another clone under the same identity; a later run takes them in and pushes" % tip[:7])
        check(got.get("row") == "rejected" and got.get("print") == [want] and got.get("next") is None
              and got.get("pushed") is False and on_origin(r, S) == ref(o, S) and record(env, "/feedback") is None,
              "m_no_replay: end's session push rejected is its own row, no replay named (%r)" % got)
        # m_second_fetch: the next start fetches origin's copy (§8.1), merges it in and pushes, as the row said
        got = run_start(env)
        tip = ref(r, S) or ""
        check(got.get("print") == [env_line(r.path)] and on_origin(r, S) == tip and tip != ref(o, S)
              and subprocess.run(["git", "-C", r.path, "merge-base", "--is-ancestor", ref(o, S), tip]).returncode == 0
              and r.git("rev-parse", "refs/remotes/origin/" + S) == tip,
              "m_second_fetch: origin's session/ab fetched, taken in and pushed (%r)" % got)

        # m_remote_deleted: a session branch origin deleted (its pull request merged) is pushed again (§8.4)
        r, env = mode_world("m-remote-deleted")
        r.write(FEED + "d.md", "d\n")
        run_start(env)
        subprocess.run(["git", "-C", r.bare, "branch", "-q", "-D", S], check=True)
        r.write(FEED + "d2.md", "d2\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        check(got.get("row") == "pushed-session" and got.get("print") == [pushed_session(tip[:7], 1, 2)]
              and on_origin(r, S) == tip, "m_remote_deleted: the push recreates it (%r)" % got)

        # m_include_ahead: commits origin refused left on main go to the session branch, and end names them
        r, env = mode_world("m-include-ahead", on=False)
        r.write(FEED + "s.md", "s\n")
        r.commit_all(SUBJECT)
        refused_at = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
        os.makedirs(os.path.dirname(refused_at))
        with open(refused_at, "w", encoding="utf-8") as fh:
            fh.write("2026-11-01\n")
        main, base = head(r), r.git("rev-parse", "origin/main")
        got = run_start(env)
        tip = ref(r, S) or ""
        want = "Specs preflight: created local session/ab at %s, and committed %s on it" % (base[:7], tip[:7])
        check(got.get("mode") == "on" and got.get("print") == [env_line(r.path), want]
              and r.git("show", "%s:%s" % (tip, FEED + "s.md"), check=False) == "s" and on_origin(r, S) == tip
              and head(r) == main, "m_include_ahead: the flush takes the stranded commit's file (%r)" % got)
        r.write(FEED + "e.md", "e\n")
        got = end_of(env)
        tip = ref(r, S) or ""
        want = (pushed_session(tip[:7], 1, 2) + "; your local main still holds 1 commit(s) origin refused, whose files are "
                "on session/ab now — to drop them, standing on main, run python3 \"%s\" --specs \"%s\" lift --branch "
                "session/ab && git -C \"%s\" reset --keep origin/main && python3 \"%s\" --specs \"%s\" put-back --branch "
                "session/ab --default-ref origin/main" % (SB, r.path, r.path, SB, r.path))
        check(got.get("print") == [want], "m_include_ahead: end's line names the stranded commit (%r)" % got)

        # m_mode_on: a default-branch push origin refused outside the mode turns the mode on, and says so
        mode_on = ("from the next run on, session files go to %s, a branch of your own whose pull request lands them "
                   "(session-branch mode), and these commits' files go there too")
        r, env = mode_world("m-mode-on", on=False)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got = end_of(env)
        want = ("Specs repo: committed %s (1 file) on main — push REFUSED by origin (pre-receive hook declined): a rule "
                "there takes no push of main, so this is recorded and no later run pushes it; " % head(r)[:7]
                + mode_on % "session/ab")
        check(got.get("row") == "push-refused" and got.get("print") == [want],
              "m_mode_on: end's refused default branch names the mode it turns on (%r)" % got)
        got = cli("--specs", r.path, "mode", "--default", "main", env=env)
        check(got.get("mode") == "on" and got.get("source") == "refused", "m_mode_on: the record turns it on (%r)" % got)
        r, env = mode_world("m-mode-on-start", initials=None, on=False)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got = run_start(env)
        want = ("Specs preflight: main not pushed — origin refused it (pre-receive hook declined), and this is recorded so "
                "no later run pushes it; " + mode_on % "a session branch of your own, once GIT_USER_INITIALS names it")
        check(got.get("print") == [env_line(r.path), want],
              "m_mode_on: the flush's refused default branch, with no identity (%r)" % got)

        # m_skipped (in process): a second unpreserved skips the move, which its step reports as a refused one
        real_lift, real_put_back, puts = sb.lift, sb.put_back, []

        def stuck(root, branch):
            return {"lifted": [], "unpreserved": [FEED + "x.md"]}

        def counted(root, branch, default_ref):
            puts.append(branch)
            return real_put_back(root, branch, default_ref)

        why = "lift found %sx.md not yet on session/ab" % FEED
        r, env = mode_world("m-skipped")
        r.git("branch", S, "main")
        other = clone(r, "m-skipped-other")
        other.write("notes.md", "n\n")
        other.commit_all("notes")
        other.git("push", "-q", "origin", "main")
        h = head(r)
        sb.lift, sb.put_back = stuck, counted
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.lift, sb.put_back = real_lift, real_put_back
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not fast-forward main (%s); the run goes on from "
                                   "it as it stands" % why] and head(r) == h and puts == [S] and got.get("error") is None,
              "m_skipped: the catch-up skipped and reported, nothing put back but the closing put-back (%r, %r)" % (got, puts))
        r, env, w = wrapped_world("m-skipped-b4")
        del puts[:]
        sb.lift, sb.put_back = stuck, counted
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.lift, sb.put_back = real_lift, real_put_back
        stop = ("Specs preflight: stopped early (git switch main: %s) — what it did is above, and the next run's preflight "
                "goes on from where this one stands" % why)
        check(got.get("print") == [env_line(r.path), stop] and got.get("error") == "git switch main: " + why
              and got.get("branch") == B
              and puts == [S], "m_skipped: B4's skipped switch stops the call, the closing put-back run (%r, %r)" % (got, puts))

        # m_canned: the renderer over canned sb.commit results and facts
        base = {"specs": "/s", "default": "main", "default_ref": "origin/main", "session_branch": S, "branch": S}
        sync = {"conflict": ["a.md", "b.md", "c.md"],
                "conflicts": [{"path": "a.md", "source": "origin/main"}, {"path": "c.md", "source": "origin/session/ab"},
                              {"path": "b.md", "source": "origin/main"}]}
        origin_clause = ("; origin's copy of session/ab, pushed from another clone, was not merged in: on c.md one clone "
                         "changed what the other clone's copy still holds unchanged (an entry edited or removed, the header "
                         "edited, the file deleted) — make the two copies agree, by making the same change on the clone that "
                         "still holds it (standing on main there; a pending cost file the other relocated is relocated there "
                         "too, never deleted by hand) or by undoing it on the other; the next run on the clone you changed "
                         "commits it, and once that is pushed, a later run here merges and pushes")
        unsettled = ("; %s and session/ab's version of it each hold a change the other lacks, so it was left out of this "
                     "commit and is as it was in your working tree — git -C \"/s\" show session/ab:%s shows the branch's "
                     "version")
        want = ("; this run created local session/ab at 1234567"
                "; merging main into session/ab left a.md, b.md unsettled — settle them in its pull request"
                + origin_clause
                + unsettled % ("x.md", "x.md") + unsettled % ("y.md", "y.md")
                + "; once a copy left out is the branch's version with your own entries added after it, in the line "
                  "endings your checkout gives the file, the next run commits it, and an edit or removal of an entry the "
                  "branch your specs checkout stands on holds can then be made again; until then lift will not discard it, "
                  "so each move of the specs checkout is skipped"
                + "; your local main still holds 2 commit(s) origin refused, whose files are on session/ab now — to drop "
                  "them, standing on main, run python3 \"%s\" --specs \"/s\" lift --branch session/ab && git -C \"/s\" "
                  "reset --keep origin/main && python3 \"%s\" --specs \"/s\" put-back --branch session/ab --default-ref "
                  "origin/main" % (SB, SB))
        got = _appends(lines, dict(base, created="1234567", sync=sync, unsettled=["x.md", "y.md"], stranded=2))
        check(got == want, "m_canned: created, sync.conflict from each source, unsettled and stranded, in §6's order (%r)" % got)
        got = _appends(lines, dict(base, sync={"error": "merge-tree: boom"}))
        check(got == "; the merge of main into session/ab could not run (merge-tree: boom), and the next run tries again",
              "m_canned: sync.error (%r)" % got)
        got = _appends(lines, dict(base, session_branch=None, branch="main", mode="unsupported", created="1234567"))
        check(got == ("; session-branch mode is on for this clone, but this git's merge-tree cannot merge without a "
                      "checkout (it needs --write-tree and -X), so these files stay on main until git is upgraded"),
              "m_canned: unsupported, and no created clause without a session branch (%r)" % got)
        row = dict(base, sha7="abc1234", files=2)
        rejected = ("Specs repo: committed abc1234 (2 files) on session/ab — push REJECTED: origin's session/ab has commits "
                    "this clone lacks, pushed from another clone under the same identity")
        got = [_row_line(lines, "rejected", dict(row, sync=s)) for s in (None, {"conflicts": sync["conflicts"][:1]}, sync)]
        check(got == [rejected + "; a later run takes them in and pushes"] * 2
              + [rejected + ", which a later run takes in only once the two clones' copies agree, as this line says"],
              "m_canned: the session branch's push-rejected row, with its conflict ending where origin's copy was not "
              "merged (%r)" % got)
        check(lines.preflight_form(_row_line(lines, "rejected", dict(row, sha7="-", files=0))).startswith(
            "Specs preflight: session/ab — push REJECTED: "), "m_canned: its Specs preflight: form")
        rec_s = "/s/.git/workflows/push-refused/session/ab"
        key_s = "branch.session/ab.workflowsPushRefused"
        refused = ("Specs repo: committed abc1234 (2 files) on session/ab — push REFUSED by origin (hook declined): a rule "
                   "there takes no push of session/ab, so this is recorded and no later run pushes it; once origin takes "
                   "pushes to session/ab, ")
        before = ("Specs repo: committed abc1234 (2 files) on session/ab — not pushed: origin refused pushes to session/ab "
                  "on 2026-11-01 (%s), and every commit since stays on local session/ab; once origin takes pushes to "
                  "session/ab, ")
        for name, facts, want in (
                ("push refused, file", dict(row, reason="hook declined", record=rec_s, record_kind="file"),
                 refused + "rm \"%s\"" % rec_s),
                ("push refused, config key", dict(row, reason="hook declined", record=key_s, record_kind="config"),
                 refused + "git -C \"/s\" config --unset " + key_s),
                ("refused before, file", dict(row, date="2026-11-01", record=rec_s, record_kind="file"),
                 before % rec_s + "rm \"%s\"" % rec_s),
                ("refused before, config key", dict(row, date="2026-11-01", record=key_s, record_kind="config"),
                 before % key_s + "git -C \"/s\" config --unset " + key_s)):
            got = _row_line(lines, "refused-before" if "before" in name else "push-refused", facts)
            check(got == want, "m_canned: the session branch's refused remedy, %s (%r)" % (name, got))
        on_main = {"sha7": "abc1234", "files": 2, "branch": "main", "default": "main", "specs": "/s",
                   "reason": "hook declined", "record": "/r", "record_kind": "file", "mode_on": True}
        main_refused = ("Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (hook declined): a rule "
                        "there takes no push of main, so this is recorded and no later run pushes it; ")
        for identity, named in (("ab", "session/ab"), (None, "a session branch of your own, once GIT_USER_INITIALS names it")):
            for kind, record_ in (("file", "/r"), ("config", "branch.main.workflowsPushRefused")):
                got = _row_line(lines, "push-refused", dict(on_main, identity=identity, record=record_, record_kind=kind))
                check(got == main_refused + mode_on % named,
                      "m_canned: app.mode-on, identity %r, a %s record (%r)" % (identity, kind, got))
        got = _row_line(lines, "push-refused", dict(on_main, record=None, record_kind=None, record_error="e", identity="ab"))
        check(got == ("Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (hook declined): a rule "
                      "there takes no push of main, but this could not be recorded (e, the configuration write's), so a "
                      "later run pushes main again"), "m_canned: an unrecorded refusal turns nothing on (%r)" % got)
        p_ = {"reason": "hook declined", "recorded": "file", "record": "/r", "record_error": None}
        got = [_refused_line(lines, "/s", "main", "main", p_, {"mode_on": True, "identity": "ab"}),
               _refused_line(lines, "/s", S, "main", dict(p_, record=rec_s), {"session_branch": S})]
        check(got == ["Specs preflight: main not pushed — origin refused it (hook declined), and this is recorded so no "
                      "later run pushes it; " + mode_on % "session/ab",
                      "Specs preflight: session/ab not pushed — origin refused it (hook declined), and this is recorded so "
                      "no later run pushes it; once origin takes pushes to session/ab, rm \"%s\"" % rec_s],
              "m_canned: the Specs preflight: refused forms take the same remedies (%r)" % got)
        moved = {"moved": True, "pushed": False, "attempts": 1, "replayed": ["a" * 40], "dropped": [], "tip": "b" * 40,
                 "porcelain": None, "moves": [], "upstream_error": None, "refused": None}
        got = _replay_line(lines, {"row": "moved", "why": "refused", "reason": None}, moved,
                           dict(on_main, standing="main", register_rebuild=False, error=None, preflight=False,
                                identity="ab"))
        check(got == ("Specs repo: committed bbbbbbb (2 files) on main — origin's main had moved on, so the run replayed "
                      "its 1 commit(s) onto it and moved main there, but push REFUSED by origin (hook declined): a rule "
                      "there takes no push of main, so this is recorded and no later run pushes it; " + mode_on % "session/ab"),
              "m_canned: the replay's refused form on the default branch says the mode turns on (%r)" % got)
        got = _row_line(lines, "pushed-session", dict(row, files=1, F=3))
        check(got == pushed_session("abc1234", 1, 3), "m_canned: pushed-session (%r)" % got)
        bp = ("Specs repo: committed abc1234 (2 files) on session/ab — not pushed: its pull request would also change "
              "specifications/PRD-A-1-x/prd.md, which is not one of this plugin's session files%s; push session/ab once that "
              "change is ready to go, and the artifacts go with it")
        failed = {"sha": "c" * 40, "reason": "branch-path", "path": "specifications/PRD-A-1-x/prd.md"}
        got = [_row_line(lines, "scope", dict(row, scope={"failed": failed}, subject="NOISSUE Merge main into session/ab")),
               _row_line(lines, "scope", dict(row, scope={"failed": dict(failed, sha=None)}, subject=None))]
        check(got == [bp % ", and the branch's newest merge commit is ccccccc NOISSUE Merge main into session/ab", bp % ""],
              "m_canned: push-scope's branch-path form, with a merge commit and with none (%r)" % got)
        got = [_session_rejected_preflight(lines, S, "main", s) for s in (None, {"conflicts": sync["conflicts"][:1]}, sync)]
        plain = ("Specs preflight: session/ab — push REJECTED: origin's session/ab has commits this clone lacks, pushed from "
                 "another clone under the same identity")
        check(got == [plain + "; a later run takes them in and pushes"] * 2
              + [plain + ", which a later run takes in only once the two clones' copies agree, as this line says" + origin_clause],
              "m_canned: the flush's session rejection, its conflict ending followed by the clause it points at (%r)" % got)

    def scenarios_state(tmp):
        state = _load_module("specs_git_state")
        home = os.path.join(tmp, "home")
        os.makedirs(home)
        keep = {k: os.environ.get(k) for k in ("HOME", "CLAUDE_CODE_SESSION_ID")}

        def env(session="s1"):
            os.environ["HOME"] = home
            if session is None:
                os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            else:
                os.environ["CLAUDE_CODE_SESSION_ID"] = session
            return {"HOME": home, "CLAUDE_CODE_SESSION_ID": session} if session else {"HOME": home}

        def raises(exc, fn, *args, **kw):
            try:
                fn(*args, **kw)
            except exc:
                return True
            except Exception:
                return False
            return False

        def tree(base):
            return sorted(os.path.relpath(os.path.join(d, f), base) for d, _, fs in os.walk(base) for f in fs)

        def clean_env(session):
            e = dict(os.environ)
            e["HOME"] = home
            e.pop("CLAUDE_CODE_SESSION_ID", None)
            if session:
                e["CLAUDE_CODE_SESSION_ID"] = session
            return e

        try:
            # s_session_id
            os.environ.pop("CLAUDE_CODE_SESSION_ID", None)
            check(raises(state.NoSession, state.session_id), "s_session_id: unset raises NoSession")
            for bad in ("", "../x", "-x", "a b"):
                os.environ["CLAUDE_CODE_SESSION_ID"] = bad
                check(raises(state.NoSession, state.session_id), "s_session_id: %r raises NoSession" % bad)
            os.environ["CLAUDE_CODE_SESSION_ID"] = "abc\n"
            check(raises(state.NoSession, state.session_id), "s_session_id: a trailing newline raises NoSession")
            os.environ["CLAUDE_CODE_SESSION_ID"] = "ab-12_x.y"
            check(state.session_id() == "ab-12_x.y", "s_session_id: a good id is returned")

            # s_path
            env()
            want = os.path.join(home, ".claude", "dev-workflows", "specs-git", "s1", "create-ard.json")
            check(state.path("s1", "/create-ard") == want, "s_path: the record's home (%r)" % state.path("s1", "/create-ard"))
            check(raises(ValueError, state.path, "s1", "create-ard"), "s_path: a command without its slash is a ValueError")
            check(raises(ValueError, state.path, "s1", "/idea\n"), "s_path: a trailing newline is a ValueError")
            check(raises(ValueError, state.path, "s1", "/Create"), "s_path: an upper-case command is a ValueError")

            # s_roundtrip
            env()
            rec = state.new("/create-ard", started_by_script=False, specs="/x/specs")
            rec["declined"] = ["specifications/PRD-A-1 x/prd.md", "specifikationen/zahlungsauslösung.md"]
            state.save("s1", "/create-ard", rec)
            got = state.load("s1", "/create-ard")
            check(got == rec and got["updated"] and got["started"], "s_roundtrip: save then load returns the record (%r)" % got)
            check(state.FIELDS["declined"] == [] and got["version"] == 1, "s_roundtrip: FIELDS is not mutated by new()")
            check(os.listdir(os.path.join(home, ".claude", "dev-workflows", "specs-git", "s1")) == ["create-ard.json"],
                  "s_roundtrip: no file but create-ard.json is left")
            before = open(state.path("s1", "/create-ard"), encoding="utf-8").read()
            bad = dict(rec, bogus=1)
            check(raises(ValueError, state.save, "s1", "/create-ard", bad)
                  and open(state.path("s1", "/create-ard"), encoding="utf-8").read() == before,
                  "s_roundtrip: an unknown key raises before the file changes")
            check(raises(ValueError, state.new, "/create-ard", bogus=1), "s_roundtrip: new() refuses an unknown key")
            check(oct(os.stat(os.path.dirname(state.path("s1", "/create-ard"))).st_mode & 0o777) == "0o700",
                  "s_roundtrip: the session directory is private")

            # s_unparsable
            with open(state.path("s1", "/create-ard"), "w", encoding="utf-8") as fh:
                fh.write("{")
            check(state.load("s1", "/create-ard") is None, "s_unparsable: a file holding { loads as None")
            with open(state.path("s1", "/create-ard"), "w", encoding="utf-8") as fh:
                json.dump(dict(rec, version=2), fh)
            check(state.load("s1", "/create-ard") is None, "s_unparsable: another version loads as None")

            # s_fields: the stay with its kind, the run's snapshot, the open run and protects; merged_stay no field
            check({"stay", "start_dirty", "midrun", "protects"} <= set(state.FIELDS)
                  and "merged_stay" not in state.FIELDS and state.FIELDS.get("stay", 0) is None
                  and state.FIELDS.get("start_dirty", 0) is None and state.FIELDS.get("midrun", 0) is None
                  and state.FIELDS.get("protects") is True,
                  "s_fields: stay, start_dirty, midrun null and protects true in FIELDS, merged_stay not (%r)"
                  % sorted(state.FIELDS))

            # s_legacy_merged_stay: a record an earlier version wrote, holding merged_stay, loads with it as a stay of
            # kind and flag merged, every new field defaulted, and saves; one whose merged_stay is null, and one holding
            # none of those fields, load with each new field at its default, stay null and present
            NEW = ("stay", "start_dirty", "midrun", "protects")
            want = {"branch": "prd/A-1-x", "kind": "merged", "reason": "g1", "merged": True, "command": None}
            for case, extra, stay in (("merged_stay set", {"merged_stay": {"branch": "prd/A-1-x", "reason": "g1"}},
                                       want),
                                      ("merged_stay null", {"merged_stay": None}, None),
                                      ("no new field", {}, None)):
                legacy = {k: v for k, v in state.new("/specify", specs="/x/specs").items() if k not in NEW}
                legacy.update(extra)
                with open(state.path("s1", "/specify"), "w", encoding="utf-8") as fh:
                    json.dump(legacy, fh)
                got = state.load("s1", "/specify") or {}
                check(all(k in got for k in NEW) and got.get("stay") == stay and got.get("start_dirty") is None
                      and got.get("midrun") is None and got.get("protects") is True and "merged_stay" not in got
                      and got.get("specs") == "/x/specs",
                      "s_legacy_merged_stay: %s loads with stay %r and every new field at its default (%r)"
                      % (case, stay, got))
                check(not raises(Exception, state.save, "s1", "/specify", got)
                      and (state.load("s1", "/specify") or {}).get("stay") == stay,
                      "s_legacy_merged_stay: %s, the loaded record saves (%r)" % (case, state.load("s1", "/specify")))
            state.remove("s1", "/specify")

            # s_keys
            for sess, cmd in (("s1", "/specify"), ("s1", "/feedback"), ("s2", "/specify")):
                state.save(sess, cmd, state.new(cmd, session=sess, specs="%s%s" % (sess, cmd)))
            check(all(state.load(sess, cmd)["specs"] == "%s%s" % (sess, cmd)
                      for sess, cmd in (("s1", "/specify"), ("s1", "/feedback"), ("s2", "/specify"))),
                  "s_keys: each (session, command) loads back its own")

            # s_remove
            check(state.remove("s2", "/specify") is True and state.remove("s2", "/specify") is False,
                  "s_remove: True, then False")
            check(state.load("s2", "/specify") is None and not os.path.exists(os.path.dirname(state.path("s2", "/specify"))),
                  "s_remove: load then None, and s2/ is gone with its last record")
            check(os.path.isdir(os.path.dirname(state.path("s1", "/specify"))), "s_remove: s1/ stays while it holds records")

            # s_prune
            def touch(sess, cmd, days):
                state.save(sess, cmd, state.new(cmd, session=sess))
                t = time.time() - days * 86400
                os.utime(state.path(sess, cmd), (t, t))

            touch("old", "/specify", 8)
            touch("young", "/specify", 6)
            touch("cur", "/specify", 8)
            gone = state.prune("cur")
            check(gone == [state.path("old", "/specify")] and not os.path.exists(os.path.dirname(gone[0])),
                  "s_prune: an 8-day-old record in another session goes with its directory (%r)" % gone)
            check(os.path.exists(state.path("young", "/specify")) and os.path.exists(state.path("cur", "/specify")),
                  "s_prune: a 6-day-old record and the current session's own stay")

            # s_resumable
            rec = state.new("/specify", stage="settle", args={"keys": ["A-1"]})
            rec["updated"] = state._now()
            check(state.resumable(rec, {"keys": ["A-1"]}) is True, "s_resumable: a fresh record at settle with the same args")
            check(state.resumable(dict(rec, stage="done"), {"keys": ["A-1"]}) is False, "s_resumable: stage done")
            check(state.resumable(rec, {"keys": ["A-2"]}) is False, "s_resumable: other args")
            old = time.strftime(state.STAMP, time.gmtime(time.time() - 20 * 60))
            check(state.resumable(dict(rec, updated=old), {"keys": ["A-1"]}) is False, "s_resumable: twenty minutes old")
            check(state.resumable(dict(rec, updated=""), {"keys": ["A-1"]}) is False, "s_resumable: no timestamp")
            check(state.resumable(dict(rec, updated=None), {"keys": ["A-1"]}) is False, "s_resumable: a null timestamp")
            check(state.saved_within(rec) is True and state.saved_within(dict(rec, updated=old)) is False
                  and state.saved_within(dict(rec, updated=old), minutes=30) is True
                  and state.saved_within(dict(rec, updated=None)) is False and state.saved_within({}) is False,
                  "s_resumable: saved_within is the 15-minute window resumable applies")

            # s_declined_cli
            shutil.rmtree(os.path.join(home, ".claude"))
            first = "specifications/PRD-A-1 x/prd.md"
            got = cli("declined", "--command", "/create-ard", "--path", first, "--path", "a.md", env=clean_env("s1"))
            rec = state.load("s1", "/create-ard")
            check(got["_rc"] == 0 and got.get("record") == "created" and got.get("recorded") == [first, "a.md"]
                  and rec and rec["declined"] == [first, "a.md"] and rec["started_by_script"] is False,
                  "s_declined_cli: no record yet creates one (%r)" % got)
            got = cli("declined", "--command", "/create-ard", "--path", "a.md", "--path", "b.md", env=clean_env("s1"))
            rec = state.load("s1", "/create-ard")
            check(got.get("record") == "found" and got.get("recorded") == ["a.md", "b.md"]
                  and rec["declined"] == [first, "a.md", "b.md"],
                  "s_declined_cli: a second call adds b.md only (%r)" % got)
            snapshot = open(state.path("s1", "/create-ard"), encoding="utf-8").read()
            got = cli("declined", "--command", "/idea", "--path", "z.md", env=clean_env("s1"))
            check(got["_rc"] == 0 and open(state.path("s1", "/create-ard"), encoding="utf-8").read() == snapshot
                  and state.load("s1", "/idea")["declined"] == ["z.md"],
                  "s_declined_cli: another command's call leaves /create-ard's record unchanged (%r)" % got)

            # s_declined_no_session
            shutil.rmtree(os.path.join(home, ".claude"))
            env(None)
            got = cli("declined", "--command", "/idea", "--path", "a.md", env={"HOME": home})
            env()
            check(one_not_run_line(got) and not os.path.exists(os.path.join(home, ".claude")),
                  "s_declined_no_session: exit 2, one line, nothing written (%r)" % got)

            # s_usage_prefix
            got = cli("declined", "--path", "a.md", env=clean_env("s1"))
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
                  "s_usage_prefix: a usage error says usage (%r)" % got)
            got = cli("declined", "--command", "/idea", env=clean_env("s1"))
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ")
                  and not os.path.exists(state.path("s1", "/idea")),
                  "s_usage_prefix: no --path is a usage error, nothing written (%r)" % got)
            got = cli("declined", "--command", "idea", "--path", "a.md", env=clean_env("s1"))
            check(one_not_run_line(got), "s_usage_prefix: a command without its slash exits 2 with one line (%r)" % got)

            # s_outside_repo
            r = new_repo(tmp, "state-outside")
            r.write("dirty.md", "x\n")
            before = r.git("status", "--porcelain")
            got = cli("declined", "--command", "/idea", "--path", "a.md", env=clean_env("s1"), cwd=r.path)
            check(got["_rc"] == 0 and r.git("status", "--porcelain") == before,
                  "s_outside_repo: declined from inside a repository leaves its status unchanged (%r)" % got)

            # s_lazy_import
            lone = os.path.join(tmp, "lazy")
            os.makedirs(lone)
            shutil.copy(me, os.path.join(lone, "specs-git.py"))
            shutil.copy(os.path.join(HERE, "session-branch.py"), os.path.join(lone, "session-branch.py"))
            got = cli("--specs", r.path, "status", script=os.path.join(lone, "specs-git.py"), env=clean_env("s1"))
            check(got["_rc"] == 0 and "artifact" in got, "s_lazy_import: status runs without the new modules (%r)" % got)
            got = cli("declined", "--command", "/idea", "--path", "a.md", script=os.path.join(lone, "specs-git.py"),
                      env=clean_env("s1"))
            check(one_not_run_line(got) and "specs_git_state" in got["_err"],
                  "s_lazy_import: declined without its module exits 2 with one line (%r)" % got)
            shutil.copy(os.path.join(HERE, "specs_git_state.py"), os.path.join(lone, "specs_git_state.py"))
            got = cli("--specs", r.path, "status", script=os.path.join(lone, "specs-git.py"), env=clean_env("s1"))
            check(got["_rc"] == 0 and "artifact" in got, "s_lazy_import: status runs without the lines module (%r)" % got)
            got = cli("declined", "--command", "/idea", "--path", "a.md", script=os.path.join(lone, "specs-git.py"),
                      env=clean_env("s1"))
            check(one_not_run_line(got) and "specs_git_lines" in got["_err"],
                  "s_lazy_import: declined without the lines module exits 2 with one line naming it (%r)" % got)
        finally:
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def scenarios_lines(tmp):
        _, lines = _flow()
        T = lines.T
        with open(SPECS_REPO_GIT, encoding="utf-8") as fh:
            srg = fh.read()
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        with open(SESSION_HYGIENE, encoding="utf-8") as fh:
            hygiene = fh.read()

        span = lines.placeholder

        def raises_naming(name, fn, *args):
            try:
                fn(*args)
            except ValueError as e:
                return name in str(e)
            return False

        # l_pins
        got = lines.pins(srg, addressing, hygiene)
        check(got == [], "l_pins: every template is found in its source (%r)" % got)

        # l_pins_bite
        row = "Specs repo: no session artifacts to commit"
        got = lines.pins(srg.replace(row, "Specs repo: no session artefacts to commit"), addressing, hygiene)
        check(srg.count(row) == 1 and len(got) == 1 and got[0].startswith("row.nothing:"),
              "l_pins_bite: one word of the Nothing to commit row changed fails row.nothing alone (%r)" % got)
        got = lines.pins(srg.replace("could not delete merged", "could not remove merged"), addressing, hygiene)
        check(len(got) == 1 and got[0].startswith("pre.delete-failed:"),
              "l_pins_bite: a word of a wording Task 3 wrote fails its template (%r)" % got)
        blocks = lines.section5_blocks(srg)
        got = lines.pins(srg.replace(blocks[1], blocks[1].replace("          artifact area:", "         artifact area:")),
                         addressing, hygiene)
        check(len(got) == 1 and got[0].startswith("g1:"), "l_pins_bite: a §5 block is compared line for line (%r)" % got)
        got = lines.pins(srg, addressing.replace("the plugin moves nothing.]`", "the plugin moves nothing at all.]`"), hygiene)
        check(got and all(f.startswith(("root.left-behind:", "root.left-behind.close:")) for f in got),
              "l_pins_bite: an addressing §3 template is pinned to addressing.md (%r)" % got)

        # l_pins_all: pins() skips no template: every one but the three blocks is found in its source, the landing's
        # rows among them, and one gone from SRG is reported
        got = lines.pins(srg, addressing, hygiene)
        check(got == [], "l_pins_all: every template is found in its source (%r)" % got)
        there = T.get("row.there", "")
        moved = srg.replace(there, there.replace("nothing to commit", "nothing to land"))
        got = lines.pins(moved, addressing, hygiene) if there else []
        check(there and srg.count(there) == 1 and [f.split(":", 1)[0] for f in got] == ["row.there"],
              "l_pins_all: a landing row missing from SRG is reported (%r)" % got)

        # l_ids
        ids = ["g0", "g1", "g2", "g1.merged.fix", "g1.merged.if_ignored"]
        ids += ["g2.%s.%s" % (v, part) for v in ("session", "self", "no-identity", "implement")
                for part in ("not_done", "fix", "if_ignored")]
        # the pins table's ids (the landing, held commits and the run typed mid-run)
        pinned = ["g1.landing.not_done", "g1.landing.if_ignored", "g1.midrun.if_ignored", "g2.midrun.if_ignored",
                  "pre.stay.midrun", "pre.held.landed", "pre.held.failed", "pre.held.stuck", "pre.held.changed",
                  "app.landed", "app.landed.unlisted", "app.held.stuck", "row.held", "row.held-stuck", "row.there",
                  "row.here", "row.midrun-kept", "pre.here.finished", "g1.landing.not_done.unlanded",
                  "g1.not_done.uncommitted"]
        pinned += ["reason.land." + r for r in ("dropped", "edited", "forms", "deleted", "folder-gone", "register",
                                                "moved", "checked-out", "no-preflight", "no-snapshot", "unfinished")]
        ids += pinned
        ids += ["row.remote-deleted.default-tail", "row.scope.merge", "row.scope.no-file", "row.scope.hook", "row.scope.branch-path",
                "row.moved.refused", "row.session-rejected", "row.session-rejected.conflict-ending"]
        ids += ["app." + a for a in (
            "hook-line", "record-key", "record-unset", "unrecorded", "register-clause", "register-move", "upstream-error",
            "register-move.run", "register-move.remote", "why.failed.none",
            "why.later-refused", "why.moved-on", "why.failed", "why.stopped", "session.created", "session.conflict-default",
            "session.conflict-origin", "session.sync-error", "session.unsettled", "session.unsettled.close",
            "session.stranded", "session.unsupported", "why.checkout-moved",
            "session.refused-remedy", "mode-on", "mode-on.no-identity", "declined")]
        ids += ["reason." + r for r in (
            "conflict", "register-rebuild", "register-rebuild.failed", "would-overwrite", "cannot-replay", "in-progress", "locked", "push-scope",
            "checked-out", "fetch-failed", "branch-moved", "cannot-move", "checkout-moved", "not-run", "timed-out",
            "session-mode")]
        ids += ["remedy.rejected", "remedy.not-standing", "remedy.checked-out", "remedy.session-wrap"]
        ids += ["pre." + p for p in (
            "nonrepo", "below-top", "pull-failed", "leave-failed", "merged-unknown", "status-failed", "scope-failed",
            "merged-flush", "refused", "refused.unrecorded", "created.empty",
            "created.committed", "deleted", "delete-failed", "advisory-D", "advisory-D.rm", "pushed-left", "b2-config",
            "b2-squash", "b4", "b4.count", "stay", "stay.unlisted", "rerun-failed", "rerun-stay", "session-not-run",
            "stopped")]
        ids += ["end.stopped", "end.session-not-run", "text.push-capped", "text.pull-capped", "text.lift-unpreserved", "text.offline", "root.one-line",
                "root.stray", "root.two-readings",
                "root.left-behind", "root.left-behind.nested", "root.left-behind.dir", "root.left-behind.close", "env.changed"]
        missing = [i for i in ids if i not in T]
        check(not missing, "l_ids: every id the interface names is a template (missing %r)" % missing)
        check(len(lines.ROWS) == 29 and lines.ROWS[0] == "pushed-plugin"
              and lines.ROWS[-7:] == ("misrooted", "held", "held-stuck", "midrun-kept", "there", "here", "silent")
              and all(("row." + r in T) == (r != "silent") for r in lines.ROWS),
              "l_ids: 29 rows in §6's order, each a row.<id> template but silent (%r)" % (lines.ROWS,))
        check(all("\n" not in t for k, t in T.items() if k not in lines.BLOCKS),
              "l_ids: every template but the three blocks is one line")
        # The landing's refusal codes, read through globals() so that a missing constant fails its check rather than
        # crashing the selftest: each maps to its reason.land.* clause -- locked to reason.locked, which P15 reuses as
        # it stands -- and every code own_change and the landing write is mapped. The coverage half is approximate, a
        # tripwire: it finds the codes by regex over the three functions' source, so a refactor that builds the
        # refusal another way fails it spuriously, and it cannot see _land_change's dynamic why["reason"] (move_branch
        # and _ref_refusal's, all mapped or retried: checked-out, checkout-moved, branch-moved, locked).
        land_reasons, permanent = globals().get("LAND_REASONS"), globals().get("LAND_PERMANENT")
        mapped = land_reasons if isinstance(land_reasons, dict) else {}
        check(mapped and all(v in T and (v.startswith("reason.land.") or (k, v) == ("locked", "reason.locked"))
                             for k, v in mapped.items()),
              "l_ids: every code of LAND_REASONS maps to a reason.land.* template, locked to reason.locked (%r)"
              % (land_reasons,))
        def defined(path, name):
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            start = text.find("\ndef %s(" % name)
            end = text.find("\ndef ", start + 1)
            return "" if start < 0 else text[start:end if end > 0 else len(text)]

        sb_source = defined(SB_SCRIPT, "own_change")
        own_codes = set(re.findall(r'refused\[p\] = \("([a-z-]+)"', sb_source))
        land_source = "".join(defined(os.path.abspath(__file__), f) for f in ("_land_change", "_here_move", "_land"))
        land_codes = set(re.findall(r'(?:refused\s*=\s*(?:entry\["refused"\] or )?|refused=|"refused": )'
                                    r'\{"reason": "([a-z-]+)"', land_source))
        check(own_codes == {"deleted", "folder-gone", "edited", "forms", "dropped", "register-rebuild"}
              and land_codes == {"checked-out", "moved", "locked", "unfinished"}
              and own_codes | land_codes <= set(mapped) and permanent == own_codes,
              "l_ids: LAND_REASONS maps every refusal code own_change and the landing write, and LAND_PERMANENT is "
              "own_change's (%r, %r, %r)" % (sorted(own_codes), sorted(land_codes), permanent))

        # l_constants: the stay's kinds in the order of the alternation that names them, its reasons, and the path
        # <specs-git.py's path> takes
        kinds, reasons, script = (globals().get(n) for n in ("STAY_KINDS", "STAY_REASONS", "SG_SCRIPT"))
        alternations = []
        for tid in ("g1.landing.not_done", "g1.landing.not_done.unlanded", "app.landed", "row.held", "row.held-stuck"):
            try:
                alternations.append(lines._alternatives(lines.placeholder(tid, "<which no key")[1:-1]))
            except (KeyError, ValueError):
                alternations.append(None)
        check(kinds == ("unkeyed", "merged", "mid-run")
              and all(a is not None and len(a) == len(kinds) and "no key" in a[kinds.index("unkeyed")]
                      and "is merged" in a[kinds.index("merged")] and "was open" in a[kinds.index("mid-run")]
                      for a in alternations),
              "l_constants: STAY_KINDS is the order of the <which no key ...> alternation in each template (%r, %r)"
              % (kinds, alternations))
        check(reasons == ("g1", "unlisted", "refused", "stopped", "mid-run")
              and isinstance(script, str) and os.path.isabs(script) and os.path.basename(script) == "specs-git.py"
              and os.path.isfile(script) and os.path.samefile(script, os.path.abspath(__file__)),
              "l_constants: STAY_REASONS gains mid-run last, and SG_SCRIPT is this script's path (%r, %r)"
              % (reasons, script))

        # l_g1_not_done: the plain G1 block's Not done part opens P30's sentence
        rows = T["g1"].split("\n")
        i = next(k for k, row in enumerate(rows) if row.startswith("Not done:"))
        j = i + 1
        while j < len(rows) and rows[j].startswith(" "):
            j += 1
        part = " ".join(" ".join([rows[i][len("Not done:"):]] + rows[i + 1:j]).split())
        check(part.startswith("the preflight did not switch branches, and did not commit or push these files."),
              "l_g1_not_done: the plain G1 block's Not done opens with the files the block lists, true beside the held "
              "stage's commits (%r)" % part[:120])

        # l_g1_end: the forms of G1 the run's end repeats (§5), by whether it committed the run's whole change: with no
        # stay, the plain block, or, where nothing of the run's was committed, the not-committed form -- its Not done
        # and If ignored -- its Fix the plain block's; with a stay, the landing form, or its not-landed Not done; under a run
        # typed mid-run, the mid-run form, whose Not done each outcome picks the same way
        landing = globals().get("_g1_landing")
        S, paths = "/s", ["notes.md"]
        plain = lines.fill("g1", {"<SPECS_PATH>": S, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})

        def parts(block):
            """label -> the part's text, unwrapped (a Not done, Fix or If ignored part of a §5 block)."""
            rows, out, label = block.split("\n"), {}, None
            for row in rows:
                hit = next((x for x in ("Not done:", "Fix:", "If ignored:") if row.startswith(x)), None)
                if hit:
                    label, out[hit] = hit, row[len(hit):].strip()
                elif label and row.startswith(" "):
                    out[label] += " " + row.strip()
                else:
                    label = None
            return out

        unkeyed = {"branch": "prd/B-2-y", "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}
        midrun = {"command": "/specify", "started": "2026-11-10T10:00:00Z", "branch": "prd/B-2-y"}
        stay_m = dict(unkeyed, kind="mid-run", command="/specify")
        kinds = lines.placeholder("g1.landing.not_done", "<which no key")
        v = {"<default>": "main", "<branch>": "prd/B-2-y", "<command>": "/specify"}
        try:
            got = {name: parts(landing(lines, plain, "prd/B-2-y", "main", S, paths, stay, mid, committed))
                   for name, stay, mid, committed in (("plain", None, None, True), ("none", None, None, False),
                                                      ("whole", unkeyed, None, True), ("held", unkeyed, None, False),
                                                      ("m-plain", None, midrun, True), ("m-none", None, midrun, False),
                                                      ("m-whole", stay_m, midrun, True), ("m-held", stay_m, midrun, False))}
        except Exception as e:
            got = {"error": "%s: %s" % (type(e).__name__, e)}
        p0 = parts(plain)
        uncommitted = T.get("g1.not_done.uncommitted", "")
        ignored = T.get("g1.if_ignored.uncommitted", "")
        check(got.get("plain") == p0 and got.get("none", {}).get("Not done:") == uncommitted
              and got["none"]["Fix:"] == p0["Fix:"] and got["none"]["If ignored:"] == ignored
              and "WILL still be committed" not in uncommitted and "WILL still be committed" in p0["Not done:"]
              and "the Specs repo: line above this notice says what came of them" in uncommitted
              and "committed alongside them" in p0["If ignored:"] and "committed alongside" not in ignored
              and "the Specs repo: line above this notice says what came of this run's artifacts" in ignored,
              "l_g1_end: no stay -- the plain block where the end committed; where it did not, the not-committed form, "
              "its Not done and If ignored, the Fix the plain block's (%r)" % got)
        check(got.get("whole", {}).get("Not done:") == lines.fill("g1.landing.not_done", dict(v, **{kinds: 0}))
              and got.get("held", {}).get("Not done:") == lines.fill("g1.landing.not_done.unlanded",
                                                                     dict(v, **{kinds: 0}))
              and got["held"]["If ignored:"] == T["g1.landing.if_ignored"] == got["whole"]["If ignored:"],
              "l_g1_end: a stay -- the landing form, its Not done the not-landed one after any other outcome (%r)" % got)
        midrun_ignored = lines.fill("g1.midrun.if_ignored", v)
        check(got.get("m-plain", {}).get("Not done:") == p0["Not done:"]
              and got.get("m-none", {}).get("Not done:") == uncommitted
              and got.get("m-whole", {}).get("Not done:") == lines.fill("g1.landing.not_done", dict(v, **{kinds: 2}))
              and got.get("m-held", {}).get("Not done:") == lines.fill("g1.landing.not_done.unlanded",
                                                                       dict(v, **{kinds: 2}))
              and all(got.get(k, {}).get("Fix:") == "" and got[k].get("If ignored:") == midrun_ignored
                      for k in ("m-plain", "m-none", "m-whole", "m-held")),
              "l_g1_end: under a run typed mid-run, the mid-run form, its Not done by the same outcomes, a mid-run row "
              "that committed nothing taking the not-committed one (%r)" % got)
        check(raises_naming("no Not done: part", landing, lines, "the G1 block", "b", "main", S, paths, None, None, False),
              "l_g1_end: a block with no Not done part is refused, never rendered unchanged")

        # l_fill_basic
        check(lines.fill("row.nothing", {}) == "Specs repo: no session artifacts to commit", "l_fill_basic: row.nothing")
        check(raises_naming("<reason>", lines.fill, "row.failed", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "main"}),
              "l_fill_basic: a missing value raises ValueError naming its placeholder")
        check(raises_naming("<N>", lines.fill, "row.pushed-plugin", {"<sha7>": "abc1234", "<branch>": "main"}),
              "l_fill_basic: a missing file count raises ValueError naming <N>")
        check(raises_naming("<branch>", lines.fill, "row.failed", {"<sha7>": "a", "<N>": 2, "<branch>": None, "<reason>": "r"}),
              "l_fill_basic: a None value outside an optional segment raises")
        check(raises_naming("repeats a clause", lines.fill, "root.left-behind", {}),
              "l_fill_basic: the left-behind line is never filled whole")

        # l_fill_list
        got = lines.fill("row.scope", {"<sha7>": ["1111111", "2222222"], "<N>": 1, "<branch>": "main",
                                       "<subject>": "Add notes", "<path>": "notes.md"})
        check(got.startswith("Specs repo: committed 1111111 (1 file) on main — ")
              and "the oldest 2222222 Add notes, which carries notes.md;" in got,
              "l_fill_list: the push-scope row's two <sha7>s, in order (%r)" % got)

        # l_fill_optional
        base = {"<sha7>": "abc1234", "<N>": 3, "<branch>": "main", "<K>": 2}
        got = lines.fill("row.replayed", dict(base, **{"<D>": None}))
        check(got.endswith("replayed its 2 commit(s) onto it"), "l_fill_optional: replayed with no <D> (%r)" % got)
        got = lines.fill("row.replayed", dict(base, **{"<D>": "1"}))
        check(got.endswith("onto it, 1 of them already there and dropped"), "l_fill_optional: replayed with <D> (%r)" % got)
        got = lines.fill("row.moved", dict(base, **{"<why>": "the push FAILED (x)"}))
        check("onto it and moved main there, but the push FAILED (x); the commits are on local main" in got and "[" not in got,
              "l_fill_optional: moved with neither optional clause (%r)" % got)
        got = lines.fill("row.moved", dict(base, **{"<why>": "w", "<D>": "1", "<the register clause>": "RC"}))
        check("onto it, 1 of them already there and dropped; RC and moved main there, but w;" in got,
              "l_fill_optional: moved with both optional clauses (%r)" % got)
        got = lines.fill("row.scope.hook", dict(base, **{"<path>": "a.md", "<M-1>": None}))
        check("a pre-commit hook added a.md to this commit" in got, "l_fill_optional: the hook row with one path (%r)" % got)
        got = lines.fill("row.scope.hook", dict(base, **{"<path>": "a.md", "<M-1>": "2"}))
        check("a pre-commit hook added a.md, and 2 more to this commit" in got,
              "l_fill_optional: the hook row with three paths (%r)" % got)
        got = lines.fill("reason.would-overwrite", {"<path>": "a.md", "<M>": None, "<branch>": "main"})
        check(got.startswith("moving the checkout would write over a.md, which you changed"),
              "l_fill_optional: would-overwrite with <M> None (%r)" % got)
        got = lines.fill("reason.would-overwrite", {"<path>": "a.md", "<M>": "2", "<branch>": "main"})
        check(got.startswith("moving the checkout would write over a.md and 2 more, which you changed"),
              "l_fill_optional: would-overwrite with <M> 2 (%r)" % got)
        one = {"<value>": "/r/specifications", span("root.one-line", "<is itself"): 0, "<the value the walk found>": "/r",
               span("root.one-line", "<the value the walk found |"): 0, "<that repository's top level>": None}
        got = lines.fill("root.one-line", one)
        check(got.endswith("Set SPECS_PATH to /r where it is set, and re-run.") and "which is itself a specifications/ directory —" in got,
              "l_fill_optional: the one-line form without its unsupported-layout segment (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{"<the value the walk found>": "/r/specs",
                                                       "<that repository's top level>": "/r"}))
        check(got.endswith("and re-run. /r/specs is not the top level of its repository (/r), and a specs tree inside a larger "
                           "repository is unsupported: this plugin switches branches and commits in that repository."),
              "l_fill_optional: the one-line form with its unsupported-layout segment (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{span("root.one-line", "<the value the walk found |"): 1}))
        check("Set SPECS_PATH to the directory that holds specifications/ where it is set" in got,
              "l_fill_optional: the one-line form naming no value (%r)" % got)
        stray = {"<value>": "/r", span("root.stray", "<the top level"): 0, "<subdirectory>": ["PRD-S-9-x"],
                 "<that repository's top level>": None}
        got = lines.fill("root.stray", stray)
        check(got.endswith("reported here instead.") and "not the top level" not in got,
              "l_fill_optional: the stray form drops its inner segment with no top level (%r)" % got)
        got = lines.fill("root.stray", dict(stray, **{"<value>": "/r/specs", span("root.stray", "<the top level"): 1,
                                                      "<that repository's top level>": "/r"}))
        check(got.endswith("instead. /r/specs is not the top level of its repository (/r), and a specs tree inside a larger "
                           "repository is unsupported: this plugin switches branches and commits in that repository.")
              and "SPECS_PATH is /r/specs, which holds /r/specs/specifications/, and holds" in got,
              "l_fill_optional: the stray form keeps its inner segment where its values are given (%r)" % got)

        # l_fill_list_marker
        got = lines.fill("app.session.conflict-default", {"<path>": ["a.md", "b c.md"], "<identity>": "ab", "<default>": "main"})
        check(got == "; merging main into session/ab left a.md, b c.md unsettled — settle them in its pull request",
              "l_fill_list_marker: <path>[, …] takes the whole list (%r)" % got)
        got = lines.fill("app.hook-line", {"<path>": ["a.md"], "<sha7>": "abc1234"})
        check(got == "Specs repo: a.md is now committed in abc1234, put there by a pre-commit hook, and not pushed",
              "l_fill_list_marker: a one-item list (%r)" % got)
        got = "".join(lines.fill("app.session.unsettled", {"<path>": p, "<identity>": "ab", "<SPECS_PATH>": "/s"})
                      for p in ("a.md", "b c.md")) + lines.fill("app.session.unsettled.close", {})
        check(got.count("so it was left out of this commit") == 2 and "show session/ab:a.md shows" in got
              and "show session/ab:b c.md shows" in got and got.endswith("each move of the specs checkout is skipped")
              and got.count("once a copy left out is the branch's version") == 1,
              "l_fill_list_marker: unsettled once per path, each with its own show, the close once (%r)" % got)

        # l_fill_root_lists
        two = ["PRD-S-9-x", "EPIC-S-9-01-y"]
        got = lines.fill("root.stray", dict(stray, **{"<subdirectory>": two}))
        check(got.count("PRD-S-9-x, EPIC-S-9-01-y") == 2 and "…" not in got and "[" not in got,
              "l_fill_root_lists: the stray form names both subdirectories in each of its two places (%r)" % got)
        got = lines.fill("root.stray", stray)
        check(got.count("PRD-S-9-x") == 2 and ", EPIC" not in got and "folder(s) PRD-S-9-x outside" in got,
              "l_fill_root_lists: with one name, it alone (%r)" % got)
        got = lines.left_behind({"<value>": "/s/specs", "<the value the walk found>": "/s"}, ["PRD-A-2-y", "PRD-A-3-z"],
                                ["dev-workflows-cost", "documentation/guide/dev-workflows"], False)
        want = ("Misrooted runs left: /s/specs/specifications/ (PRD-A-2-y, PRD-A-3-z), which belongs in /s/specifications/, "
                "and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong "
                "place, unless it is moved first; /s/specs/dev-workflows-cost/, which belongs at /s/dev-workflows-cost/; "
                "/s/specs/documentation/guide/dev-workflows/, which belongs at /s/documentation/guide/dev-workflows/, which the "
                "first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first. Move them "
                "yourself, commit the move, then re-run — the plugin moves nothing.")
        check(got == want, "l_fill_root_lists: the left-behind line, two folders and two directories (%r)" % got)
        got = lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, None,
                                ["dev-workflows-feedback", "dev-workflows-cost"], True)
        want = ("If /m is a specs tree under another name, misrooted runs left: /m/dev-workflows-feedback/, which belongs at "
                "the same path at the specs repository's top level; /m/dev-workflows-cost/, which belongs at the same path at "
                "the specs repository's top level. Move them yourself, commit the move, then re-run — the plugin moves nothing.")
        check(got == want, "l_fill_root_lists: the two-readings opening, with no value the walk found (%r)" % got)
        check(lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, None, [], False) is None
              and lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, [], [], False) is None,
              "l_fill_root_lists: nothing left, no line, an empty folder list included")
        got = lines.left_behind({"<value>": "/m", "<the value the walk found>": None}, [], ["dev-workflows-cost"], False)
        check(got == "Misrooted runs left: /m/dev-workflows-cost/, which belongs at the same path at the specs repository's "
              "top level. Move them yourself, commit the move, then re-run — the plugin moves nothing.",
              "l_fill_root_lists: an empty folder list is no nested clause, never () (%r)" % got)

        # l_fill_alternation
        got = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", span("pre.stay", "<switched"): 1})
        check(got.endswith("(it would have switched to main, as no key of this run names it)"),
              "l_fill_alternation: the stay line's second alternative, <default> filled (%r)" % got)
        got = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", span("pre.stay", "<switched"): 0})
        check(got.endswith("(it would have switched to main and deleted it, as it is merged)"),
              "l_fill_alternation: the stay line's first alternative (%r)" % got)
        got = lines.fill("root.one-line", dict(one, **{span("root.one-line", "<is itself"): 2, "<key>": "A-1"}))
        check("which is itself a specs folder, asserting key A-1 — every folder" in got,
              "l_fill_alternation: the signal alternation's third alternative fills <key> (%r)" % got)
        check(raises_naming("no alternative 4", lines.fill, "root.one-line", dict(one, **{span("root.one-line", "<is itself"): 4})),
              "l_fill_alternation: an alternative that does not exist raises")
        got = lines.fill("root.one-line", dict(one, **{"<the value the walk found>": "/walk/value"}))
        check("Set SPECS_PATH to /walk/value where it is set" in got and "the value the walk found" not in got,
              "l_fill_alternation: int 0 on the value-to-set alternation renders the walk's value (%r)" % got)
        check(raises_naming("<the value the walk found>", lines.fill, "root.one-line",
                            dict(one, **{"<the value the walk found>": None})),
              "l_fill_alternation: an alternative naming a placeholder with no value raises naming it")
        walk_alt = span("root.one-line", "<the value the walk found |")
        check(raises_naming("is an alternation", lines.fill, "root.one-line", dict(one, **{walk_alt: "/r"})),
              "l_fill_alternation: a string for an alternation raises")
        check(raises_naming("is an alternation", lines.fill, "pre.stay",
                            {"<branch>": "b", "<default>": "main", span("pre.stay", "<switched"): True}),
              "l_fill_alternation: a bool for an alternation raises")
        check(raises_naming("beginning", span, "root.one-line", "<the value the walk found"),
              "l_fill_alternation: placeholder() refuses a prefix two placeholders share")
        check(span("root.one-line", "<key>") == "<key>" and span("pre.stay", "<default>") == "<default>"
              and span("root.two-readings", "<the parent of") == "<the parent of <value>>",
              "l_fill_alternation: placeholder() finds a placeholder inside an alternation's alternatives")
        check(raises_naming("has 0", span, "pre.stay", "<nothing>"), "l_fill_alternation: placeholder() refuses a key it lacks")

        # l_fill_count
        got1 = lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "prd/A-1-x"})
        got2 = lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "prd/A-1-x"})
        check(got1 == "Specs repo: committed abc1234 (1 file) on prd/A-1-x — pushed"
              and got2 == "Specs repo: committed abc1234 (2 files) on prd/A-1-x — pushed",
              "l_fill_count: singular at one (%r, %r)" % (got1, got2))

        # l_fill_landing: the landing's lines, filled -- the stay's alternation by kind, a held row's reason clause, the
        # stuck lines' two commands quoted whole, and the two new file counts singular at one
        def fill_landing():
            kind = span("app.landed", "<which no key")
            got = [lines.fill("app.landed", {"<branch>": "prd/B-2-y", "<default>": "main", "<command>": "/specify",
                                             kind: k}) for k in range(3)]
            tail = (", so its files were committed on main without leaving prd/B-2-y, and taken out of your working "
                    "tree there")
            check(got == ["; this run's preflight stayed on prd/B-2-y, which no key of this run names" + tail,
                          "; this run's preflight stayed on prd/B-2-y, which is merged into main" + tail,
                          "; this run's preflight stayed on prd/B-2-y, where /specify's run in this session was open "
                          "when this run started" + tail],
                  "l_fill_landing: app.landed by the stay's kind, <default> and <command> filled inside it (%r)" % got)
            clause = lines.fill("reason.land.checked-out", {"<path>": "/w2", "<default>": "main",
                                                            span("reason.land.checked-out", "<the push of"): 0,
                                                            "<reason>": "…"})
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": clause,
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 0})
            check(got.endswith(" without leaving it: another worktree, /w2, has main checked out, and the push of the "
                               "commit by refspec failed (…); they stay in your working tree, held for main, and the "
                               "next run tries again")
                  and got.startswith("Specs repo: NOT COMMITTED — this run's preflight stayed on prd/B-2-y, which "
                                     "no key"),
                  "l_fill_landing: row.held with reason.land.checked-out's failed push (%r)" % got)
            dropped = lines.fill("reason.land.dropped", {"<path>": "specifications/PRD-A-1-x/follow-ups.md",
                                                         "<onto>": "main"})
            S, tool = "/s p", "/plugins/workflows-core/scripts/specs-git.py"
            stuck = {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": dropped, "<SPECS_PATH>": S,
                     "<sha7>": "abc1234", "<specs-git.py's path>": tool, "<default-ref>": "origin/main",
                     "<path>": ["specifications/PRD-A-1-x/follow-ups.md"]}
            want = ["git -C \"%s\" show abc1234" % S,
                    "python3 \"%s\" --specs \"%s\" land --default-ref origin/main --drop-held abc1234" % (tool, S)]
            for tid, values in (("row.held-stuck", dict(stuck, **{span("row.held-stuck", "<which no key"): 1})),
                                ("app.held.stuck", stuck), ("pre.held.stuck", stuck)):
                got = lines.fill(tid, values)
                check(all(("'%s'" % w) in got and shlex.split(w) for w in want)
                      and got.endswith("'%s'" % want[1]) and dropped in got and "<" not in got,
                      "l_fill_landing: %s names both commands, each quoted whole (%r)" % (tid, got))
            got = lines.fill("row.here", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "main", "<command>": "/specify",
                                          span("row.here", "<the next push"): 0})
            check(got.startswith("Specs repo: committed abc1234 (1 file) on main — not pushed yet: /specify's run")
                  and got.endswith("; the next push of main this plugin makes, by that run or a later one, carries it, "
                                   "and that run's files are as they were in your working tree"),
                  "l_fill_landing: row.here singular at one, its first alternative (%r)" % got)
            got = lines.fill("pre.held.landed", {"<sha7>": "abc1234", "<N>": 1, "<default>": "main",
                                                 "<branch>": "prd/B-2-y"})
            check(got.startswith("Specs preflight: committed abc1234 (1 file) on main: the session files an "
                                 "earlier run"),
                  "l_fill_landing: pre.held.landed singular at one (%r)" % got)
            # the held lines' tail: the next run's retry, or, where session-branch mode takes the files, what it does
            refused = lines.fill("reason.land.checked-out", {"<path>": "/w2", "<default>": "main", "<the refusal>": "x",
                                                             span("reason.land.checked-out", "<the push of"): 4})
            mode_tail = ("and the next run, in session-branch mode, drops this hold and commits them as that mode "
                         "commits session files")
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main", "<reason clause>": refused,
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 1})
            check(got.endswith(", so from the next run session-branch mode takes these files; they stay in your "
                               "working tree, " + mode_tail) and "tries again" not in got,
                  "l_fill_landing: row.held's mode tail where session-branch mode takes the files (%r)" % got)
            got = [lines.fill("pre.held.failed", {"<default>": "main", "<reason clause>": refused,
                                                  span("pre.held.failed", "<and the next run tries"): k})
                   for k in (0, 1)]
            check(got[0].endswith("); they stay in your working tree, and the next run tries again")
                  and got[1].endswith("); they stay in your working tree, " + mode_tail),
                  "l_fill_landing: pre.held.failed's two tails (%r)" % got)
            # G1's end forms after a landing that did not land the run's whole change: the not-landed Not done promises
            # nothing, by kind, and names the run's Specs repo: outcome line -- printed above the repeated block -- by
            # what it is, not as "the line above", which in the block is its Found line; the landing, merged and
            # mid-run If ignored lines claim nothing about where this run's artifacts went
            unl = span("g1.landing.not_done.unlanded", "<which no key")
            got = [lines.fill("g1.landing.not_done.unlanded", {"<branch>": "prd/B-2-y", "<default>": "main",
                                                               "<command>": "/specify", unl: k}) for k in range(3)]
            head_ = ("the preflight did not switch branches, and did not commit or push these files. Those files are "
                     "yours, and switching branches would carry them along. This run's own artifacts were to be "
                     "committed at the end of the run on main, not on prd/B-2-y, ")
            tail_ = ", and your checkout is not moved; the Specs repo: line above this notice says what came of them."
            check(got == [head_ + w + tail_ for w in ("which no key of this run names", "which is merged into main",
                                                      "where /specify's run in this session was open when this run "
                                                      "started")]
                  and not any("WILL" in x or "the line above says" in x for x in got),
                  "l_fill_landing: g1.landing.not_done.unlanded by kind, promising nothing, naming the Specs repo: "
                  "line (%r)" % got)
            # G2's mid-run If ignored names the run's Specs repo: line by what it is -- true at the start, where no
            # outcome line is printed yet, and at the end, where it stands above the block -- never "the line above"
            got = lines.fill("g2.midrun.if_ignored", {"<command>": "/specify", "<branch>": "prd/B-2-y"})
            check(got == "nothing is to be run here while /specify's run in this session is open on prd/B-2-y: let it "
                         "finish, or end it, first; this run's Specs repo: line, at its end, says what came of its "
                         "artifacts." and "line above" not in got,
                  "l_fill_landing: g2.midrun.if_ignored names the run's Specs repo: line (%r)" % got)
            neutral = [T[k] for k in ("g1.landing.if_ignored", "g1.merged.if_ignored", "g1.midrun.if_ignored")]
            check(all("nothing of this run's is committed with them" in x.lower() for x in neutral)
                  and not any("reach <default>" in x or "committed without them" in x for x in neutral),
                  "l_fill_landing: the landing, merged and mid-run If ignored lines are true whatever the outcome")
            got = [lines.fill("pre.here.finished", {"<branch>": "main", "<sha7>": "abc1234", "<N>": n}) for n in (1, 2)]
            check(got == ["Specs preflight: finished the commit an earlier run was making on main when it was cut off: "
                          "abc1234 (%s), that run's own session files, committed apart from another run's" % c
                          for c in ("1 file", "2 files")],
                  "l_fill_landing: pre.here.finished, singular at one (%r)" % got)
            got = lines.fill("row.midrun-kept", {"<command>": "/specify", "<branch>": "main",
                                                 "<reason clause>": lines.fill("reason.land.unfinished",
                                                                               {"<branch>": "main"})})
            check(got == "Specs repo: NOT COMMITTED — /specify's run in this session is still open on main, and this "
                         "run's own changes could not be committed apart from that run's: main moved on without the "
                         "commit this run was making on it when it was cut off, so that commit was dropped unfinished; "
                         "they stay in your working tree, and that run's terminal commit takes them with its own",
                  "l_fill_landing: the mid-run row with reason.land.unfinished (%r)" % got)
            # a run typed mid-run whose start took no snapshot -- status could not run, or the start was cut off before
            # taking one -- commits nothing while the open run stands: its clause holds for both causes, so it names
            # neither a preflight that never ran nor a status that failed
            got = lines.fill("row.midrun-kept", {"<command>": "/specify", "<branch>": "prd/B-2-y",
                                                 "<reason clause>": lines.fill("reason.land.no-snapshot", {})})
            check(got == "Specs repo: NOT COMMITTED — /specify's run in this session is still open on prd/B-2-y, and "
                         "this run's own changes could not be committed apart from that run's: this run's start took no "
                         "snapshot of the session files then uncommitted, so nothing tells its files from that run's; "
                         "they stay in your working tree, and that run's terminal commit takes them with its own"
                  and "preflight" not in T["reason.land.no-snapshot"],
                  "l_fill_landing: the mid-run row with reason.land.no-snapshot, true for both causes (%r)" % got)
            # a landing that found an index.lock at its start holds the change for reason locked, a cause that passes:
            # the held row with reason.locked, its retry tail
            got = lines.fill("row.held", {"<branch>": "prd/B-2-y", "<default>": "main",
                                          "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"}),
                                          span("row.held", "<which no key"): 0, span("row.held", "<held for"): 0})
            check(got == "Specs repo: NOT COMMITTED — this run's preflight stayed on prd/B-2-y, which no key of this run "
                         "names, and its files could not be committed on main without leaving it: .git/index.lock is "
                         "held by another git process, or was left by one that died, and this plugin never deletes a "
                         "lock; they stay in your working tree, held for main, and the next run tries again",
                  "l_fill_landing: the held row with reason.locked, an index.lock at the landing's start (%r)" % got)

        try:
            if not all(t in T for t in pinned):
                raise ValueError("the pins table's templates are not all in T")
            fill_landing()
        except ValueError as e:  # a template that lost a placeholder the check names fails here, not the run
            check(False, "l_fill_landing: %s" % e)

        # l_literal_bracket
        got = lines.fill("app.register-move", {"<from>": "7", "<to>": "9", "<origin>": "a", "<whose number>": "the local number"})
        check(got == "[SEC#7] → [SEC#9] (a, the local number)", "l_literal_bracket: [SEC# stays literal (%r)" % got)

        # l_preflight_form
        failed = lines.fill("row.failed", {"<sha7>": "abc1234", "<N>": 2, "<branch>": "main", "<reason>": T["text.push-capped"]})
        got = lines.preflight_form(failed)
        check(got == "Specs preflight: main — push FAILED (the push did not finish within 60 s); the commit is local and a later "
              "run retries it", "l_preflight_form: the push FAILED row (%r)" % got)
        got = lines.preflight_form(lines.fill("row.locked", {}))
        check(got.startswith("Specs preflight: skipped — another session holds the repo"), "l_preflight_form: Locked (%r)" % got)
        got = lines.preflight_form(lines.fill("row.commit-failed", {"<the first line of git's error or the hook's output>": "e"}))
        check(got.startswith("Specs preflight: NOT COMMITTED — the commit failed (e)"), "l_preflight_form: Commit failed (%r)" % got)
        got = lines.preflight_form(lines.fill("row.pushed-plugin", {"<sha7>": "abc1234", "<N>": 1, "<branch>": "prd/A-1-x"}))
        check(got == "Specs preflight: prd/A-1-x — pushed", "l_preflight_form: a singular count (%r)" % got)

        # l_artifacts
        base_dir = "specifications/PRD-A-1-x/"
        check(lines.artifacts([base_dir + "prd.md"]) == base_dir + "prd.md", "l_artifacts: one path")
        check(lines.artifacts([base_dir + "prd.md", base_dir + "a b.md"]) == base_dir + "prd.md, " + base_dir + "a b.md",
              "l_artifacts: two paths, a space kept")
        three = [base_dir + "prd.md", base_dir + "ard.md", base_dir + "x.md"]
        check(lines.artifacts(three) == ", ".join(three), "l_artifacts: three paths")
        four = three + [base_dir + "revisions/prd-1.md"]
        check(lines.artifacts(four) == "4 files under specifications/PRD-A-1-x", "l_artifacts: four in one folder (%r)"
              % lines.artifacts(four))
        spread = three + ["specifications/PRD-A-2-y/defects.md"]
        check(lines.artifacts(spread) == "4 files under specifications", "l_artifacts: four spanning specifications/ (%r)"
              % lines.artifacts(spread))

        # l_fix_lines: every §5 Fix part, rendered with its values, is commands only -- no #, no quote left open: this
        # static check is what guards a paste into an interactive zsh, which does not read # as a comment unless
        # interactivecomments is set -- and runs whole in bash and, where it is on PATH, in zsh, against a git that
        # only logs its arguments, making exactly the git calls it shows. zsh -c is not interactive, so it reads # as a
        # comment whatever INTERACTIVE_COMMENTS says: that run checks the part's syntax and quoting in zsh, never how a
        # # reads there
        shim = os.path.join(tmp, "l-fix-shim")
        os.makedirs(shim)
        log = os.path.join(tmp, "l-fix-calls")
        with open(os.path.join(shim, "git"), "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\nfor a in \"$@\"; do printf '%s|' \"$a\"; done >> \"$GIT_CALLS\"\necho >> \"$GIT_CALLS\"\n")
        os.chmod(os.path.join(shim, "git"), 0o755)
        S, paths = os.path.join(tmp, "a specs repo"), ["my notes.md", "n.md"]
        plain = lines.fill("g1", {"<SPECS_PATH>": S, "<N>": 2,
                                  "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})
        blocks = [("g0", lines.fill("g0", {"<SPECS_PATH>": S, "<sha7>": "abc1234", "<YYYY-MM-DD>": "2026-11-10",
                                           "<branch>": "main"}), ["switch|-c|rescue/2026-11-10|"]),
                  ("g1", plain, ["status|", "add|my notes.md|n.md|", "commit|"]),
                  ("g2", _g2_block(lines, S, "feature/x", "main"), ["switch|main|"]),
                  ("g2.implement", _g2_block(lines, S, "feature/x", "main", "implement"), []),
                  ("g2.session", _g2_block(lines, S, "feature/x", "main", "session", {"<identity>": "ab"}), []),
                  ("g2.self", _g2_block(lines, S, "session/ab", "main", "self", {"<identity>": "ab"}), ["switch|main|"]),
                  ("g2.no-identity", _g2_block(lines, S, "feature/x", "main", "no-identity"), [])]
        landing = globals().get("_g1_landing")  # G1's landing forms (§5): the plain Fix, or merged's switch first
        check(landing is not None, "l_fix_lines: _g1_landing renders G1's landing forms")
        if landing is not None:
            unkeyed = {"branch": "prd/B-2-y", "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}
            merged = {"branch": "prd/A-1-x", "kind": "merged", "reason": "g1", "merged": True, "command": None}
            blocks += [("g1.landing", landing(lines, plain, "prd/B-2-y", "main", S, paths, unkeyed, None),
                        ["status|", "add|my notes.md|n.md|", "commit|"]),
                       ("g1.landing.merged", landing(lines, plain, "prd/A-1-x", "main", S, paths, merged, None),
                        ["switch|main|", "add|my notes.md|n.md|", "commit|"])]
        for name, block, want in blocks:
            rows = block.split("\n")
            i = next((k for k, row in enumerate(rows) if row.startswith("Fix:")), None)
            part = []
            for row in rows[i:] if i is not None else []:
                if part and not row.startswith(" "):
                    break
                part.append(row[len("Fix:"):].strip() if not part else row.strip())
            balanced = True
            for row in part:
                try:
                    shlex.split(row)
                except ValueError:
                    balanced = False
            check(i is not None and not any("#" in row for row in part) and balanced,
                  "l_fix_lines: %s's Fix part is commands only -- no #, which zsh's interactive shell does not read as a "
                  "comment, and no quote left open (%r)" % (name, part))
            for shell in [["bash", "-c"]] + ([["zsh", "-c"]] if shutil.which("zsh") else []):
                if os.path.exists(log):
                    os.remove(log)
                ran = subprocess.run(shell + ["\n".join(part)], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     env=dict(os.environ, PATH=shim + os.pathsep + os.environ.get("PATH", ""),
                                              GIT_CALLS=log))
                calls = open(log, encoding="utf-8").read().splitlines() if os.path.exists(log) else []
                check(i is not None and ran.returncode == 0 and calls == ["-C|%s|%s" % (S, w) for w in want],
                      "l_fix_lines: %s's Fix part runs whole through %s -c, making its git calls (rc %s, %r, %r)"
                      % (name, shell[0], ran.returncode, calls, ran.stderr.decode("utf-8", "replace")[:200]))

    def scenarios_gate(tmp):
        with open(SESSION_HYGIENE, encoding="utf-8") as fh:
            hygiene = fh.read()
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        section7 = hygiene[hygiene.index("\n## 7. "):]
        after = section7[section7.index("**The line.**"):]
        block = after[after.index("```bash\n") + len("```bash\n"):after.index("\n```", after.index("```bash\n"))]

        def carrier(path, key, kind="prd", quote=""):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("---\nkind: %s%s%s\nkey: %s%s%s\n---\n\n# x\n" % (quote, kind, quote, quote, key, quote))

        real = os.path.realpath
        inside = ("every folder lives under $SPECS_PATH/specifications/, so this run would look for and create folders "
                  "in the wrong place; it wrote nothing under that path, and its cost and feedback are reported here "
                  "instead.")
        unsupported = ("is not the top level of its repository (%s), and a specs tree inside a larger repository is "
                       "unsupported: this plugin switches branches and commits in that repository.")
        close = " Move them yourself, commit the move, then re-run — the plugin moves nothing."

        def nonrepo(value, which):
            return ("Specs preflight: SPECS_PATH is %s, which %s — nothing this run writes there is committed or handed "
                    "off; set SPECS_PATH to your specs repository's top level, where it is set, and re-run." % (value, which))

        # g_sh7_pinned
        check(SH7_LINE == block, "g_sh7_pinned: SH7_LINE is session-hygiene §7's fenced block (%r)" % block)

        # g_env_line_equal
        r = new_repo(tmp, "env repo")
        r.git("remote", "add", "origin", "git@github.com:acme/specs.git")
        link = os.path.join(tmp, "env-link")
        os.symlink(r.path, link)
        keep = {k: os.environ.get(k) for k in ("SPECS_PATH", "REPOS_PATH")}
        cwd = os.getcwd()
        try:
            os.chdir(tmp)
            for repos in (None, "/workspace/repos dir"):
                if repos is None:
                    os.environ.pop("REPOS_PATH", None)
                else:
                    os.environ["REPOS_PATH"] = repos
                for value in ("", r.path + "/", link, "env repo", os.path.join(tmp, "no-such"), r.path):
                    env = dict(os.environ)
                    env.pop("SPECS_PATH", None)
                    if value:
                        env["SPECS_PATH"] = value
                    want = subprocess.run(["bash", "-c", block], env=env, stdout=subprocess.PIPE).stdout.decode("utf-8")
                    got = env_line(value)
                    check(got + "\n" == want, "g_env_line_equal: SPECS_PATH %r, REPOS_PATH %r (%r, %r)" % (value, repos, got, want))
            os.environ["SPECS_PATH"] = "/somewhere/else"
            check(env_line("").startswith("Environment: SPECS_PATH=unset (origin none), "),
                  "g_env_line_equal: an empty value is unset whatever the environment holds (%r)" % env_line(""))
            check(env_line("env repo") == "Environment: SPECS_PATH=%s (origin git@github.com:acme/specs.git), REPOS_PATH=%s"
                  % (real(r.path), os.environ.get("REPOS_PATH", "unset")),
                  "g_env_line_equal: a relative path is its real path, with its origin (%r)" % env_line("env repo"))
        finally:
            os.chdir(cwd)
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

        # g_unset
        got = gate("")
        check(got == {"state": "unset", "top": None, "git_dir": None, "misrooted": False, "lines": []},
              "g_unset: unset is silent (%r)" % got)
        check(gate("", notices=False) == {"state": "unset", "top": None, "git_dir": None},
              "g_unset: notices off returns state, top and git_dir alone (%r)" % gate("", notices=False))

        # g_file
        f = os.path.join(tmp, "a-file")
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("x\n")
        got = gate(f)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(f, "is not a directory")] and not got["misrooted"],
              "g_file: a regular file is not a directory (%r)" % got)
        missing = os.path.join(tmp, "no such dir")
        got = gate(missing)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(missing, "is not a directory")],
              "g_file: a path that does not exist is not a directory (%r)" % got)

        # g_plain_dir
        plain = os.path.join(tmp, "gate-plain")
        os.makedirs(plain)
        got = gate(plain)
        check(got["state"] == "not-a-repo" and got["lines"] == [nonrepo(plain, "is not in a git repository")]
              and got["misrooted"] is False and got["top"] is None and got["git_dir"] is None,
              "g_plain_dir: a directory in no repository, no signal (%r)" % got)

        # g_mounted_specifications
        m = os.path.join(tmp, "mount-a", "specifications")
        carrier(os.path.join(m, "PRD-A-1-x", "prd.md"), "A-1")
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set "
                "SPECS_PATH to the directory that holds specifications/ where it is set, and re-run." % (m, inside))
        got = gate(m)
        check(got["state"] == "not-a-repo" and got["misrooted"] is True
              and got["lines"] == [nonrepo(m, "is not in a git repository") + " " + stop],
              "g_mounted_specifications: the notice, then on the same line the one-line stop (%r)" % got)
        got = specs_root_check(m)
        check(got["signal"] == "a-ef" and got["form"] == "one-line" and got["value"] is None and got["subdirs"] == [],
              "g_mounted_specifications: signal a-ef, the one-line form, no value (%r)" % got)
        os.makedirs(os.path.join(m, "specifications", "PRD-A-2-y"))
        os.makedirs(os.path.join(m, "dev-workflows-cost"))
        got = gate(m)
        behind = ("Misrooted runs left: %s/specifications/ (PRD-A-2-y), which belongs in the specs repository's "
                  "specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits "
                  "bookkeeping from, in the wrong place, unless it is moved first; %s/dev-workflows-cost/, which belongs "
                  "at the same path at the specs repository's top level.%s" % (m, m, close))
        check(got["misrooted"] is True and got["lines"] == [nonrepo(m, "is not in a git repository") + " " + stop, behind],
              "g_mounted_specifications: the left-behind line after it, on its own (%r)" % got)

        # g_mounted_other_name
        t = os.path.join(tmp, "mount-b", "tree")
        carrier(os.path.join(t, "PRD-A-1-x", "ard.md"), "A-1", kind="ard")
        carrier(os.path.join(t, "PRD-A-1-x", "prd.md"), "A-1", quote='"')
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds the specs folder PRD-A-1-x directly, and nothing on "
                "disk says whether %s is a specs tree under another name or a specs root. If it is a specs tree under "
                "another name, its folders belong in a directory named specifications/, and SPECS_PATH names that "
                "directory's parent: set SPECS_PATH to the parent of the specifications/ directory %s is a mount of, and "
                "mount that parent whole rather than the tree alone, where it is set. If it is a specs root, move "
                "PRD-A-1-x and every other specs folder beside it into %s/specifications/ yourself and commit the move, "
                "and make %s the top level of a git repository, which it is not. Then re-run — the plugin moves nothing. "
                "This run wrote nothing under that path, and its cost and feedback are reported here instead."
                % (t, t, t, t, t))
        got = gate(t)
        check(got["state"] == "not-a-repo" and got["misrooted"] is True
              and got["lines"] == [nonrepo(t, "is not in a git repository") + " " + stop],
              "g_mounted_other_name: the notice, then on the same line the two-readings stop (%r)" % got)
        parent = os.path.dirname(t)
        check(not any(("SPECS_PATH to %s" % p) in line for line in got["lines"] for p in (parent, real(parent)))
              and not any("the directory that holds specifications/" in line for line in got["lines"]),
              "g_mounted_other_name: no line names a value addressing §3 rules out (%r)" % got)
        got = specs_root_check(t)
        check(got["signal"] == "b-sub" and got["form"] == "two-readings" and got["value"] is None
              and got["subdirs"] == ["PRD-A-1-x"], "g_mounted_other_name: b-sub, two readings (%r)" % got)
        cur = os.path.join(tmp, "mount-b", "cur")
        os.symlink(os.path.join(t, "PRD-A-1-x"), cur)
        got = specs_root_check(cur)
        check(got["signal"] == "b-self" and got["form"] == "one-line"
              and "which is itself a specs folder, asserting key A-1 —" in got["lines"][0],
              "g_mounted_other_name: a link is judged by the folder it reaches, by its physical name (%r)" % got)
        named = os.path.join(tmp, "mount-b", "notes")
        carrier(os.path.join(named, "prd.md"), "A-1")
        alias = os.path.join(tmp, "mount-b", "PRD-A-1-alias")
        os.symlink(named, alias)
        check(specs_root_check(alias)["signal"] is None,
              "g_mounted_other_name: a link's own name never passes the prefix test for it (%r)" % specs_root_check(alias))
        inv = os.path.join(tmp, "mount-c", "other")
        carrier(os.path.join(inv, "BRD-B-1-x", "coverage-ledger.md"), "B-1", kind="coverage-ledger")
        carrier(os.path.join(inv, "BRD-B-1-x", "brd", "brd-inventory.md"), "B-1", kind="brd")
        got = specs_root_check(inv)
        check(got["signal"] == "b-sub" and got["subdirs"] == ["BRD-B-1-x"],
              "g_mounted_other_name: a root BRD folder's carrier is its brd/brd-inventory.md (%r)" % got)

        # g_inside_tree
        r = new_repo(tmp, "inside")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        r.commit_all("a folder")
        spec_dir = os.path.join(r.path, "specifications")
        got = gate(spec_dir)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set SPECS_PATH "
                "to %s where it is set, and re-run." % (spec_dir, inside, real(r.path)))
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [stop]
              and real(got["top"]) == real(r.path) and real(got["git_dir"]) == real(os.path.join(r.path, ".git")),
              "g_inside_tree: <repo>/specifications names <repo> (%r)" % got)
        check(specs_root_check(spec_dir)["signal"] == "a-prefix" and specs_root_check(spec_dir)["value"] == real(r.path),
              "g_inside_tree: signal a-prefix, value <repo> (%r)" % specs_root_check(spec_dir))
        folder = os.path.join(spec_dir, "PRD-A-1-x")
        got = gate(folder)
        check(specs_root_check(folder)["signal"] == "a-prefix" and got["misrooted"] is True
              and got["lines"] == [stop.replace(spec_dir + ", which is itself a specifications/ directory",
                                                folder + ", which is inside the specifications/ directory")],
              "g_inside_tree: a folder inside the tree is the same signal (%r)" % got)
        via = os.path.join(tmp, "inside-link")
        os.symlink(folder, via)
        got = specs_root_check(via)
        check(got["signal"] == "a-prefix" and got["value"] == real(r.path)
              and got["lines"][0].endswith("Set SPECS_PATH to %s where it is set, and re-run." % real(r.path)),
              "g_inside_tree: the walk starts from the physical path, so a link to a folder names <repo> (%r)" % got)
        os.makedirs(os.path.join(spec_dir, "specifications", "PRD-A-2-y"))
        os.makedirs(os.path.join(spec_dir, "dev-workflows-cost"))
        got = gate(spec_dir)
        check(got["misrooted"] is True and got["lines"] == [stop, (
            "Misrooted runs left: %s/specifications/ (PRD-A-2-y), which belongs in %s/specifications/, and which the first "
            "run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is "
            "moved first; %s/dev-workflows-cost/, which belongs at %s/dev-workflows-cost/.%s"
            % (spec_dir, real(r.path), spec_dir, real(r.path), close))],
              "g_inside_tree: what an earlier run left in <repo>/specifications belongs under the value the walk found (%r)"
              % got)

        # g_below_top
        r = new_repo(tmp, "below")
        carrier(os.path.join(r.path, "specs", "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        r.commit_all("a nested tree")
        specs = os.path.join(r.path, "specs")
        got = gate(specs)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [
            "Specs preflight: SPECS_PATH is %s, below the top level of its repository (%s) — a specs tree inside a larger "
            "repository is unsupported, because this plugin switches branches and commits in the repository SPECS_PATH "
            "belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated specs "
            "repository's top level." % (specs, got["top"])] and real(got["top"]) == real(r.path),
              "g_below_top: one line from pre.below-top naming <repo> (%r)" % got)
        nested = os.path.join(specs, "specifications")
        got = gate(nested)
        want = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — %s Set SPECS_PATH "
                "to %s where it is set, and re-run. %s %s" % (nested, inside, real(specs), real(specs),
                                                              unsupported % real(r.path)))
        check(got["misrooted"] is True and got["lines"] == [want] and specs_root_check(nested)["signal"] == "a-ef",
              "g_below_top: the inside-tree notice skips the below-top one, the unsupported clause carried (%r)" % got)

        # g_stray
        r = new_repo(tmp, "stray")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "PRD-S-9-x", "prd.md"), "S-9")
        r.write("dev-workflows-cost/c.md", "cost\n")
        got = gate(r.path)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [
            "SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, the top level of its repository, and holds the specs folder(s) "
            "PRD-S-9-x outside %s/specifications/, where every folder lives. SPECS_PATH names the right directory; move "
            "PRD-S-9-x into %s/specifications/ yourself, commit the move, then re-run — the plugin moves nothing. This run "
            "wrote nothing under %s, and its cost and feedback are reported here instead." % ((r.path,) * 4)],
              "g_stray: the stray-folder form, no left-behind line (%r)" % got)
        carrier(os.path.join(r.path, "EPIC-S-9-01-y", "epic.md"), "S-9-01", kind="epic")
        got = specs_root_check(r.path)
        check(got["form"] == "stray" and got["subdirs"] == ["EPIC-S-9-01-y", "PRD-S-9-x"]
              and got["lines"][0].count("EPIC-S-9-01-y, PRD-S-9-x") == 2 and len(got["lines"]) == 1,
              "g_stray: the loop finished, every stray named in byte-wise order (%r)" % got)
        r = new_repo(tmp, "stray-below")
        carrier(os.path.join(r.path, "specs", "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "specs", "PRD-S-9-x", "prd.md"), "S-9")
        specs = os.path.join(r.path, "specs")
        got = gate(specs)
        check(got["misrooted"] is True and len(got["lines"]) == 1
              and got["lines"][0].startswith("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds %s/specifications/, "
                                             "and holds the specs folder(s) PRD-S-9-x outside" % (specs, specs))
              and got["lines"][0].endswith("reported here instead. %s %s" % (specs, unsupported % real(r.path))),
              "g_stray: below the top level, which holds specifications/, the unsupported clause (%r)" % got)

        # g_two_readings
        r = new_repo(tmp, "two")
        carrier(os.path.join(r.path, "specs", "PRD-A-1-x", "prd.md"), "A-1")
        specs = os.path.join(r.path, "specs")
        top = real(r.path)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which holds the specs folder PRD-A-1-x directly, and nothing on "
                "disk says whether %s is a specs tree under another name or a specs root. If it is a specs tree under "
                "another name, its folders belong in a directory named specifications/, and SPECS_PATH names that "
                "directory's parent: move them into %s/specifications/ yourself, commit the move, and set SPECS_PATH to "
                "%s, where it is set. If it is a specs root, move PRD-A-1-x and every other specs folder beside it into "
                "%s/specifications/ yourself and commit the move; %s %s Then re-run — the plugin moves nothing. This run "
                "wrote nothing under that path, and its cost and feedback are reported here instead."
                % (specs, specs, top, top, specs, specs, unsupported % top))
        got = gate(specs)
        check(got["state"] == "pass" and got["misrooted"] is True and got["lines"] == [stop],
              "g_two_readings: the two-readings form with the unsupported-layout clause (%r)" % got)
        via = os.path.join(tmp, "two-link")
        os.symlink(specs, via)
        got = specs_root_check(via)
        check(got["form"] == "two-readings" and "move them into %s/specifications/ yourself, commit the move, and set "
              "SPECS_PATH to %s, where it is set." % (top, top) in got["lines"][0],
              "g_two_readings: the parent the first reading names is the physical one (%r)" % got)
        os.makedirs(os.path.join(specs, "dev-workflows-feedback"))
        os.makedirs(os.path.join(specs, "documentation", "guide", "dev-workflows"))
        got = gate(specs)
        check(got["lines"][1:] == [
            "If %s is a specs tree under another name, misrooted runs left: %s/dev-workflows-feedback/, which belongs at "
            "the same path at the specs repository's top level; %s/documentation/guide/dev-workflows/, which belongs at "
            "the same path at the specs repository's top level, which the first run after SPECS_PATH is fixed commits "
            "there in the wrong place unless it is moved first.%s" % (specs, specs, specs, close)],
              "g_two_readings: the left-behind line, under the first reading (%r)" % got)

        # g_correct_root
        r = new_repo(tmp, "correct")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "templates", "prd.md"), "A-1")
        carrier(os.path.join(r.path, "README.md"), "A-1")
        os.symlink(os.path.join("specifications", "PRD-A-1-x"), os.path.join(r.path, "PRD-A-1-x"))
        os.symlink(os.path.join("specifications", "PRD-A-1-x"), os.path.join(r.path, "current"))
        got = gate(r.path)
        check(got["state"] == "pass" and got["lines"] == [] and got["misrooted"] is False and specs_root_check(r.path)
              == {"signal": None, "form": None, "value": None, "subdirs": [], "lines": []},
              "g_correct_root: templates/, README.md and a link into the tree are no signal (%r)" % got)
        got = gate(r.path, notices=False)
        check(sorted(got) == ["git_dir", "state", "top"] and got["state"] == "pass",
              "g_correct_root: notices off returns state, top and git_dir alone (%r)" % got)
        r = new_repo(os.path.join(tmp, "clone"), "specifications")
        carrier(os.path.join(r.path, "specifications", "PRD-A-1-x", "prd.md"), "A-1")
        got = gate(r.path)
        check(got["state"] == "pass" and got["lines"] == [] and specs_root_check(r.path)["signal"] is None,
              "g_correct_root: a repository cloned into a directory named specifications is a root (%r)" % got)
        loose = os.path.join(tmp, "mount-d", "loose")
        os.makedirs(os.path.join(loose, "PRD-A-3-z"))
        with open(os.path.join(loose, "PRD-A-3-z", "notes.md"), "w", encoding="utf-8") as fh:
            fh.write("# Notes\n\n---\nkind: prd\nkey: A-3\n---\n")
        with open(os.path.join(loose, "PRD-A-3-z", "open.md"), "w", encoding="utf-8") as fh:
            fh.write("---\nkind: prd\nkey: A-3\n")
        check(specs_root_check(loose)["signal"] is None,
              "g_correct_root: frontmatter is only what opens a file and closes, never a rule further down (%r)"
              % specs_root_check(loose))

        # g_reserved
        para = addressing[addressing.index("**Reserved subdirectory names are not folder kinds.**"):]
        para = para[para.index("never resolved by one —"):para.index("None matches")]
        raw = re.findall(r"`([^`/][^`]*)/`", para)
        names = [n.replace("<YYYYMMDD>", "20261109") for n in raw]
        check(len(names) == 10 and all(RESERVED.match(n) for n in names),
              "g_reserved: RESERVED matches every name of addressing §2's list (%r)" % names)
        check(not any(RESERVED.match(n) for n in ("brd2", "xbrd", "bundle-2026", "bundle-202611090", "PRD-A-1-x",
                                                  "Doc screenshots/", "design ")),
              "g_reserved: RESERVED matches whole names only")
        mine = re.search(r"\(\?:(.+)\)", RESERVED.pattern).group(1).split("|")
        check(sorted(mine) == sorted(n.replace("<YYYYMMDD>", "[0-9]{8}") for n in raw),
              "g_reserved: RESERVED holds addressing §2's names and no other (%r, %r)" % (mine, raw))
        theirs = re.search(r"\(\.\+/\)\?\((.+)\)/$", sb.EXCLUDED).group(1).split("|")
        check(sorted(theirs) == sorted(n for n in mine if n != "dev-workflows") and "dev-workflows" in mine,
              "g_reserved: session-branch.py's EXCLUDED holds the same names but dev-workflows (%r, %r)" % (mine, theirs))

        # g_read_only (skipped as root, for whom no mode bit refuses a write)
        if not (hasattr(os, "geteuid") and os.geteuid() == 0):
            r = new_repo(tmp, "read-only")
            git_dir = os.path.join(r.path, ".git")
            os.chmod(git_dir, 0o555)
            try:
                got = gate(r.path)
                check(got["state"] == "read-only" and got["lines"] == [] and got["misrooted"] is False,
                      "g_read_only: a git directory with no write bit (%r)" % got)
            finally:
                os.chmod(git_dir, 0o755)

        # g_cli
        for value in (m, t, "", spec_dir):
            got = cli("--specs", value, "specs-root-check")
            raw = {k: v for k, v in got.items() if not k.startswith("_")}
            check(got["_rc"] == 0 and raw == specs_root_check(value), "g_cli: %r prints the function's object (%r)" % (value, got))
        got = cli("--specs", f, "specs-root-check")
        check(got["_rc"] == 0 and got.get("signal") is None, "g_cli: a file is passed through unchecked (%r)" % got)
        got = cli("specs-root-check")
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "g_cli: no --specs at all is a usage error (%r)" % got)

    # The run worlds scenarios_end and scenarios_replay share.
    PRD = "specifications/PRD-ACME-1-x/prd.md"
    RESUME = "specifications/PRD-ACME-1-x/dev-workflows/resume.md"
    PLUGIN = "prd/ACME-1-x"

    @contextlib.contextmanager
    def in_env(env):
        keep = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            yield
        finally:
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def world(tmp, name):
        """A bare origin; a clone with the PRD committed and pushed on main; the environment of a run of session
        <name>: HOME under tmp, the session variable, SPECS_PATH naming the clone."""
        bare = os.path.join(tmp, name + ".git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, name)
        r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
        r.commit_all("ACME-1 Add the PRD")
        r.git("remote", "add", "origin", bare)
        r.git("push", "-q", "-u", "origin", "main")
        r.bare = bare
        home = os.path.join(tmp, "home-" + name)
        os.makedirs(home)
        return r, {"HOME": home, "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}

    def other_key(r, name="prd/B-2-y"):
        """A plugin branch no key of the run names, with one commit of its own, pushed with -u, HEAD left on it."""
        r.git("switch", "-q", "-c", name)
        r.write("specifications/PRD-B-2-y/prd.md", "---\nkind: prd\nkey: B-2\n---\n")
        r.commit_all("B-2 Add the PRD")
        r.git("push", "-q", "-u", "origin", name)

    def seed(env, command, **fields):
        """A record as start saves one, its env_line from env_line(<the clone>)."""
        state = _flow()[0]
        specs = fields.pop("specs", env["SPECS_PATH"])
        rec = dict(specs=specs, env_line=env_line(specs), gate="pass", top=os.path.realpath(specs), default="main",
                   default_ref="origin/main", remote="origin", mode="off", branch="main", stage="done",
                   args={"specs": specs, "keys": [], "commit_key": None, "register_rebuild": None})
        rec.update(fields)
        with in_env(env):
            session = env["CLAUDE_CODE_SESSION_ID"]
            state.save(session, command, state.new(command, session=session, **rec))

    def record(env, command):
        with in_env(env):
            return _flow()[0].load(env["CLAUDE_CODE_SESSION_ID"], command)

    def run_end(env, command, *args, specs=None, stdin=b""):
        return cli("--specs", env["SPECS_PATH"] if specs is None else specs, "end", "--command", command, *args,
                   env=env, stdin=stdin)

    def on_origin(r, branch="main"):
        p = subprocess.run(["git", "-C", r.bare, "rev-parse", "--verify", "-q", "refs/heads/" + branch],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        return p.stdout.decode().strip() or None

    def clone(r, name):
        """Another clone of <r>'s origin, beside <r>."""
        path = os.path.join(os.path.dirname(r.path), name)
        subprocess.run(["git", "clone", "-q", r.bare, path], check=True, stderr=subprocess.DEVNULL)
        o = Repo(path)
        o.git("config", "user.email", "o@example.invalid")
        o.git("config", "user.name", "o")
        o.git("config", "commit.gpgsign", "false")
        return o

    def hook(path, body):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\n" + body)
        os.chmod(path, 0o755)

    def head(r):
        return r.git("rev-parse", "HEAD")

    def scenarios_end(tmp):
        state, lines = _flow()
        T = lines.T
        g = globals()
        MIS = ("Specs repo: NOT COMMITTED — SPECS_PATH is misplaced, or the run's environment no longer matches the one "
               "it recorded; see the notice below")
        BLOCKED = "Specs repo: NOT COMMITTED — see the notice below"
        NOTHING = "Specs repo: no session artifacts to commit"
        FIELDS = {"print", "line", "row", "sha7", "files", "branch", "pushed", "next", "record", "error"}

        def files(n):
            return "1 file" if n == 1 else "%d files" % n

        def pushed_default(sha7, specs, n=1):
            return ("Specs repo: committed %s (%s) on main — pushed straight to main, and no pull request was opened: this "
                    "plugin lands its session files there without review; to land them through a pull request of your own "
                    "instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true"
                    % (sha7, files(n), specs))

        def refused_tail(branch, specs, record_text, clear, day):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, %s"
                    % (branch, specs, day, branch, specs, day, branch, specs, branch, branch, clear))

        def appended(paths_text):
            return "; the deliverable at %s remains uncommitted, as you asked" % paths_text

        def plugin_world(name, pushed=True):
            r, env = world(tmp, name)
            r.git("switch", "-q", "-c", PLUGIN)
            if pushed:
                r.git("push", "-q", "-u", "origin", PLUGIN)
            return r, env

        # e_nothing
        r, env = world(tmp, "e-nothing")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard")
        check(got["_rc"] == 0 and got.get("row") == "nothing" and got.get("print") == [NOTHING] and got.get("line") == NOTHING
              and got.get("record") == "found" and got.get("pushed") is False and got.get("sha7") is None
              and got.get("next") is None and got.get("error") is None and record(env, "/create-ard") is None,
              "e_nothing: a clean tree is nothing to commit, the record removed (%r)" % got)
        check({k for k in got if not k.startswith("_")} == FIELDS, "e_nothing: the full field set (%r)" % sorted(got))

        # e_pushed_default
        r, env = world(tmp, "e-pushed-default")
        seed(env, "/create-ard")
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-ard", "--commit-key", "ACME-1")
        h = head(r)
        want = pushed_default(h[:7], r.path)
        check(got["_rc"] == 0 and got.get("row") == "pushed-default" and got.get("print") == [want] and got.get("line") == want
              and got.get("sha7") == h[:7] and got.get("files") == 1 and got.get("branch") == "main"
              and got.get("pushed") is True and record(env, "/create-ard") is None,
              "e_pushed_default: committed, pushed straight to main, (1 file) (%r)" % got)
        check(r.git("log", "-1", "--format=%s") == "ACME-1 Add dev-workflows session artifacts (/create-ard)"
              and "Co-Authored-By" not in r.git("log", "-1", "--format=%B"),
              "e_pushed_default: the subject carries the key and no trailer (%r)" % r.git("log", "-1", "--format=%B"))
        check(on_origin(r) == h and r.git("status", "--porcelain") == "", "e_pushed_default: origin/main holds it, the tree clean")
        r.write(RESUME, "resume 2\n")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "pushed-default"
              and r.git("log", "-1", "--format=%s") == "NOISSUE Add dev-workflows session artifacts (/create-ard)",
              "e_pushed_default: no --commit-key opens the subject NOISSUE (%r)" % got)

        # e_pushed_plugin
        r, env = plugin_world("e-pushed-plugin")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-prd", "--commit-key", "ACME-1")
        h = head(r)
        check(got.get("row") == "pushed-plugin" and got.get("print") == ["Specs repo: committed %s (1 file) on %s — pushed"
                                                                          % (h[:7], PLUGIN)]
              and on_origin(r, PLUGIN) == h and got.get("branch") == PLUGIN, "e_pushed_plugin (%r)" % got)
        r, env = plugin_world("e-pushed-plugin-no-upstream", pushed=False)
        r.git("push", "-q", "origin", PLUGIN)
        r.write(RESUME, "resume\n")
        got = run_end(env, "/create-prd")
        check(got.get("row") == "pushed-plugin" and on_origin(r, PLUGIN) == head(r)
              and r.git("config", "--get", "branch.%s.merge" % PLUGIN, check=False) == "refs/heads/" + PLUGIN,
              "e_pushed_plugin: a branch pushed with no upstream is pushed with -u (%r)" % got)

        # e_not_ours
        r, env = world(tmp, "e-not-ours")
        r.git("switch", "-q", "-c", "feature/x")
        block = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
        seed(env, "/specify", guard="G2", guard_block=block, branch="feature/x")
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        h = head(r)
        want = ("Specs repo: committed %s (1 file) on feature/x — not pushed: this plugin pushes only the default branch and "
                "the branches it creates, so feature/x is yours to push; the artifacts reach the maintainer when you push or "
                "merge it" % h[:7])
        check(got.get("row") == "not-ours" and got.get("print") == [want, block] and on_origin(r, "feature/x") is None,
              "e_not_ours: the row, then G2's block verbatim (%r)" % got)

        # e_no_remote
        r, env = world(tmp, "e-no-remote")
        r.git("remote", "remove", "origin")
        r.write(RESUME, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("record") == "missing" and got.get("row") == "no-remote" and got.get("print") == [
            "Specs repo: committed %s (1 file) on main — not pushed: this specs repo has no origin remote" % head(r)[:7]],
              "e_no_remote (%r)" % got)

        # e_elsewhere
        r, env = world(tmp, "e-elsewhere")
        r.git("config", "branch.main.pushRemote", "fork")
        for remote in ("fork", "upstream"):
            if remote == "upstream":
                r.git("config", "--unset", "branch.main.pushRemote")
                r.git("config", "remote.pushDefault", "upstream")
            seed(env, "/feedback")
            r.write(RESUME, "r %s\n" % remote)
            got = run_end(env, "/feedback")
            want = ("Specs repo: committed %s (1 file) on main — not pushed: your git configuration pushes main to %s, not "
                    "to origin, which is the remote this plugin reads; push it where it belongs yourself" % (head(r)[:7], remote))
            check(got.get("row") == "elsewhere" and got.get("print") == [want] and on_origin(r) != head(r),
                  "e_elsewhere: %s (%r)" % (remote, got))

        # e_remote_deleted
        r, env = plugin_world("e-remote-deleted")
        subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/" + PLUGIN], check=True)
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        want = ("Specs repo: committed %s (1 file) on %s — not pushed: origin has no %s any more, so it was renamed or "
                "deleted there, and this step does not recreate it; the commit stays on local %s"
                % (head(r)[:7], PLUGIN, PLUGIN, PLUGIN))
        check(got.get("row") == "remote-deleted" and got.get("print") == [want] and on_origin(r, PLUGIN) is None,
              "e_remote_deleted: a plugin branch origin deleted (%r)" % got)
        r, env = world(tmp, "e-remote-deleted-default")
        subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/main"], check=True)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — not pushed: origin has no main any more, so it was renamed or "
                "deleted there, and this step does not recreate it; the commit stays on local main; if origin renamed it, "
                "git -C \"%s\" remote set-head origin --auto names the new one" % (head(r)[:7], r.path))
        check(got.get("row") == "remote-deleted" and got.get("print") == [want] and on_origin(r) is None,
              "e_remote_deleted: the default branch's form, with its set-head tail (%r)" % got)

        # e_origin_lacks
        r, env = plugin_world("e-origin-lacks", pushed=False)
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        want = ("Specs repo: committed %s (1 file) on %s — not pushed: origin has no %s, and this plugin puts a branch of "
                "its own there only by handing off its deliverable; the commit stays on local %s until a later handoff of "
                "%s pushes the branch, or you run git -C \"%s\" push -u origin %s"
                % (head(r)[:7], PLUGIN, PLUGIN, PLUGIN, PLUGIN, r.path, PLUGIN))
        check(got.get("row") == "origin-lacks" and got.get("print") == [want] and on_origin(r, PLUGIN) is None,
              "e_origin_lacks (%r)" % got)

        # e_refused_before
        r, env = plugin_world("e-refused-before")
        pushed_tip = head(r)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "prd", "ACME-1-x")
        os.makedirs(os.path.dirname(rec_file))

        def refused_before(sha7, date, record_text, clear, day):
            return ("Specs repo: committed %s (1 file) on %s — not pushed: origin refused pushes to %s on %s (%s), and every "
                    "commit since stays on local %s; " % (sha7, PLUGIN, PLUGIN, date, record_text, PLUGIN)
                    + refused_tail(PLUGIN, r.path, record_text, clear, day))

        for body, date in (("2026-11-01\n", "2026-11-01"), ("", "an earlier run")):
            with open(rec_file, "w", encoding="utf-8") as fh:
                fh.write(body)
            seed(env, "/create-prd", branch=PLUGIN)
            r.write(RESUME, "r %s\n" % date)
            got, days, _ = dated(lambda: run_end(env, "/create-prd"))
            check(got.get("row") == "refused-before"
                  and any(got.get("print") == [refused_before(head(r)[:7], date, rec_file, "rm \"%s\"" % rec_file, d)]
                          for d in days)
                  and on_origin(r, PLUGIN) == pushed_tip,
                  "e_refused_before: the record file holding %r names %s and its path (%r)" % (body, date, got))
        os.remove(rec_file)
        key = "branch.%s.workflowsPushRefused" % PLUGIN
        r.git("config", key, "2026-11-02")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r config\n")
        got, days, _ = dated(lambda: run_end(env, "/create-prd"))
        check(got.get("row") == "refused-before" and any(got.get("print") == [refused_before(
            head(r)[:7], "2026-11-02", key, "git -C \"%s\" config --unset %s" % (r.path, key), d)] for d in days)
              and "rm \"" not in got["line"],
              "e_refused_before: the configuration-key form names the key and its config --unset (%r)" % got)

        # e_push_refused
        r, env = plugin_world("e-push-refused")
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "echo refused by policy >&2\nexit 1\n")
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "prd", "ACME-1-x")
        opening = ("Specs repo: committed %s (1 file) on %s — push REFUSED by origin (pre-receive hook declined): a rule "
                   "there takes no push of %s, ")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got, days, ldays = dated(lambda: run_end(env, "/create-prd"))
        want = [[opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                 + refused_tail(PLUGIN, r.path, rec_file, "rm \"%s\"" % rec_file, d)] for d in days]
        check(got.get("row") == "push-refused" and got.get("print") in want and got.get("pushed") is False
              and os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
              "e_push_refused: refused, the record file written under the common git directory with today's date (%r)" % got)
        shutil.rmtree(os.path.join(r.path, ".git", "workflows"))
        with open(os.path.join(r.path, ".git", "workflows"), "w", encoding="utf-8") as fh:
            fh.write("a file where the record's directory would go\n")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r2\n")
        got, days, ldays = dated(lambda: run_end(env, "/create-prd"))
        want = [[opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                 + refused_tail(PLUGIN, r.path, key, "git -C \"%s\" config --unset %s" % (r.path, key), d)] for d in days]
        check(got.get("row") == "push-refused" and got.get("print") in want and r.git("config", "--get", key) in ldays,
              "e_push_refused: the file cannot be written, so the configuration key is (%r)" % got)
        r.git("config", "--unset", key)
        lock = os.path.join(r.path, ".git", "config.lock")
        open(lock, "w").close()
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r3\n")
        got = run_end(env, "/create-prd")
        os.remove(lock)
        line = got.get("line") or ""
        check(got.get("row") == "push-refused" and line.startswith(opening % (head(r)[:7], PLUGIN, PLUGIN)
                                                                     + "but this could not be recorded (")
              and line.endswith(", the configuration write's), so a later run pushes %s again" % PLUGIN)
              and "to land the commits" not in line and "rm \"" not in line
              and r.git("config", "--get", key, check=False) == "",
              "e_push_refused: neither can be written, so the row says so and names no remedy (%r)" % got)

        # e_scope
        r, env = world(tmp, "e-scope")
        r.write("notes.md", "n\n")
        user = r.commit_all("Add notes")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — not pushed: the push would also publish commits that are not "
                "this plugin's session-file commits, the oldest %s Add notes, which carries notes.md; push main once they "
                "are ready to go, and the artifacts go with them" % (head(r)[:7], user[:7]))
        check(got.get("row") == "scope" and got.get("print") == [want] and on_origin(r) != head(r),
              "e_scope: the user's unpushed commit, its sha7, subject and path (%r)" % got)
        r, env = world(tmp, "e-scope-merge")
        r.git("switch", "-q", "-c", "side")
        r.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/x.md", "f\n")
        r.commit_all("side feedback")
        r.git("switch", "-q", "main")
        r.git("merge", "-q", "--no-ff", "-m", "Merge side", "side")
        merge = head(r)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "scope" and got.get("line") == (
            "Specs repo: committed %s (1 file) on main — not pushed: the push would also publish commits that are not this "
            "plugin's session-file commits, the oldest %s Merge side, which is a merge commit; push main once they are "
            "ready to go, and the artifacts go with them" % (head(r)[:7], merge[:7])),
              "e_scope: a merge commit (%r)" % got)
        generating = ("echo gen > generated.txt\necho g2 > gen2.txt\ngit add generated.txt gen2.txt\n")

        def hook_row(sha7):
            # git lists a commit's paths in byte order, gen2.txt before generated.txt, and the first is the one named
            return ("Specs repo: committed %s (3 files) on main — not pushed: a pre-commit hook added gen2.txt, and 1 more "
                    "to this commit, so it carries more than this plugin's session files; check what the hook added before "
                    "you push main" % sha7)

        def hook_line(sha7):
            return "Specs repo: generated.txt is now committed in %s, put there by a pre-commit hook, and not pushed" % sha7

        r, env = world(tmp, "e-scope-hook")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write("generated.txt", "mine\n")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "generated.txt"})
        seed(env, "/specify", guard="G1", guard_block=block, guard_paths=["generated.txt"])
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        h = head(r)
        check(got.get("row") == "scope" and got.get("print") == [hook_row(h[:7]), block, hook_line(h[:7])]
              and on_origin(r) != h, "e_scope: the hook variant, the block, then the hook line (%r)" % got)
        check(r.git("status", "--porcelain") == "",
              "e_scope: the index is brought back in step with HEAD after the hook (%r)" % r.git("status", "--porcelain"))
        r, env = world(tmp, "e-scope-hook-declined")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify", "--declined", "generated.txt")
        h = head(r)
        check(got.get("row") == "scope" and got.get("print") == [hook_row(h[:7]), hook_line(h[:7])],
              "e_scope: a hook path the declined paths name gets the hook line, and no append now it is committed (%r)" % got)
        r, env = world(tmp, "e-scope-hook-plain")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), generating)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "scope" and got.get("print") == [hook_row(head(r)[:7])],
              "e_scope: no hook line where neither the block nor the declined paths name a hook path (%r)" % got)

        # e_push_failed
        r, env = world(tmp, "e-push-failed")
        missing = os.path.join(tmp, "e-push-failed-missing.git")
        r.git("remote", "set-url", "origin", missing)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        want = ("Specs repo: committed %s (1 file) on main — push FAILED (fatal: '%s' does not appear to be a git "
                "repository); the commit is local and a later run retries it" % (head(r)[:7], missing))
        check(got.get("row") == "failed" and got.get("print") == [want] and got.get("pushed") is False,
              "e_push_failed: git's reason (%r)" % got)

        # e_locked
        r, env = world(tmp, "e-locked")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        h = head(r)
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_end(env, "/create-ard")
        staged = r.git("diff", "--cached", "--name-only")
        os.remove(lock)
        check(got.get("row") == "locked" and got.get("print") == [
            "Specs repo: skipped — another session holds the repo (index.lock); the next run picks the artifacts up"]
              and staged == "" and head(r) == h, "e_locked: nothing staged, nothing committed (%r)" % got)

        # e_commit_failed
        r, env = world(tmp, "e-commit-failed")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_end(env, "/create-ard")
        check(got.get("row") == "commit-failed" and got.get("print") == [
            "Specs repo: NOT COMMITTED — the commit failed (hook says no); the artifacts stay staged, and a later run commits "
            "them once git accepts the commit (a merge concluded, a hook satisfied)"]
              and head(r) == h and r.git("diff", "--cached", "--name-only") == RESUME,
              "e_commit_failed: the hook's output, the session file still staged (%r)" % got)

        # e_blocked
        r, env = world(tmp, "e-blocked")
        h = head(r)
        r.git("switch", "-q", "--detach")

        def g0_on(r, h, days):
            """G0's block as end renders it, one per day of <days> (dated)."""
            return [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                    for d in days]
        g0 = g0_on(r, h, [utc_day()])[0]  # seeded: end prints the block the record holds, never one it renders
        seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0] and head(r) == h
              and record(env, "/specify") is None, "e_blocked: a record carrying blocked repeats G0's block (%r)" % got)
        got, days, _ = dated(lambda: run_end(env, "/specify", "--no-preflight"))
        check(got.get("record") == "missing" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED, b] for b in g0_on(r, h, days)]
              and head(r) == h and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all"),
              "e_blocked: no record, a detached HEAD and something to stage prints G0's block the first time (%r)" % got)
        os.remove(os.path.join(r.path, RESUME))
        got = run_end(env, "/specify", "--no-preflight")
        check(got.get("row") == "nothing" and got.get("print") == [NOTHING], "e_blocked: nothing to stage is nothing (%r)" % got)

        # e_declined_blocked: §6's declined append on both blocked rows, before G0's block
        r, env = world(tmp, "e-declined-blocked")
        h = head(r)
        r.git("switch", "-q", "--detach")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        g0 = g0_on(r, h, [utc_day()])[0]
        seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None, declined=[ard])
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == [BLOCKED + appended(ard), g0] and head(r) == h
              and record(env, "/specify") is None,
              "e_declined_blocked: a record carrying blocked names the declined path, then G0's block (%r)" % got)
        got, days, _ = dated(lambda: run_end(env, "/specify", "--no-preflight", "--declined", ard))
        check(got.get("record") == "missing" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED + appended(ard), b] for b in g0_on(r, h, days)] and head(r) == h,
              "e_declined_blocked: on a detached HEAD with no preflight, the --declined path, then G0's block (%r)" % got)
        # ... and only where --specs still names the repository the start checked (§6): the review's two reproductions,
        # --specs "" from a cwd that is no repository and from another repository holding the path dirty, and --specs
        # naming that other repository -- each the blocked line and G0's block, exit 0, no append
        nowhere = os.path.join(tmp, "e-declined-blocked-nowhere")
        os.makedirs(nowhere)
        other = new_repo(tmp, "e-declined-blocked-other")
        other.write(ard, "theirs\n")
        for label, specs, cwd in (("--specs \"\" from no repository", "", nowhere),
                                  ("--specs \"\" from another repository", "", other.path),
                                  ("--specs naming another repository", other.path, None)):
            seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None, declined=[ard])
            got = cli("--specs", specs, "end", "--command", "/specify", env=env, cwd=cwd)
            check(got["_rc"] == 0 and got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0]
                  and record(env, "/specify") is None,
                  "e_declined_blocked: %s, the blocked line and G0's block alone (%r)" % (label, got))

        # e_declined_misrooted: the misrooted row takes no declined append, and runs no git status in the wrong path
        r, env = world(tmp, "e-declined-misrooted")
        wrong = os.path.join(tmp, "e-declined-misrooted-wrong")
        os.makedirs(wrong)
        notice = ["SPECS_PATH_INSIDE_TREE: the notice the run's start printed"]
        seed(env, "/specify", specs_git="misrooted", misrooted_notice=notice, declined=[PRD], specs=wrong)
        got = run_end(env, "/specify", specs=wrong)
        check(got["_rc"] == 0 and got.get("row") == "misrooted" and got.get("print") == [MIS] + notice
              and record(env, "/specify") is None,
              "e_declined_misrooted: the row and its notice alone, though git status cannot run there (%r)" % got)

        # e_misrooted
        r, env = world(tmp, "e-misrooted")
        notice = ["SPECS_PATH_INSIDE_TREE: the notice the run's start printed", "Misrooted runs left: what it left"]
        seed(env, "/specify", specs_git="misrooted", misrooted_notice=notice)
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_end(env, "/specify")
        check(got.get("row") == "misrooted" and got.get("print") == [MIS] + notice and head(r) == h
              and record(env, "/specify") is None, "e_misrooted: the record's notice, verbatim (%r)" % got)
        changed = ("Environment changed: started in SPECS_PATH=/a (origin none), REPOS_PATH=unset, now SPECS_PATH=/b "
                   "(origin none), REPOS_PATH=unset — nothing more is committed, handed off or recorded here, and what this "
                   "run already wrote stays where it is. Re-run in the container the run started in.")
        got = run_end(env, "/specify", "--no-preflight", "--misrooted-stdin", stdin=(changed + "\n").encode("utf-8"))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, changed]
              and head(r) == h, "e_misrooted: --misrooted-stdin's notice, verbatim (%r)" % got)
        got = run_end(env, "/specify", "--no-preflight", "--misrooted-stdin", stdin=b"")
        check(got.get("row") == "misrooted" and got.get("print") == [MIS] and head(r) == h,
              "e_misrooted: empty stdin is the row and nothing after it (%r)" % got)

        # e_env_changed
        r, env = world(tmp, "e-env-changed")
        recorded = env_line(r.path)
        r.write(RESUME, "r\n")
        h = head(r)

        def env_changed(now):
            return ("Environment changed: started in %s, now %s — nothing more is committed, handed off or recorded here, "
                    "and what this run already wrote stays where it is. Re-run in the container the run started in."
                    % (recorded[len("Environment: "):], now[len("Environment: "):]))

        seed(env, "/create-ard")
        got = run_end(env, "/create-ard", specs="")
        check(got.get("record") == "found" and got.get("row") == "misrooted"
              and got.get("print") == [MIS, env_changed(env_line(""))] and head(r) == h,
              "e_env_changed: --specs \"\" against a recorded path (%r)" % got)
        other = new_repo(tmp, "e-env-other")
        seed(env, "/create-ard")
        got = run_end(env, "/create-ard", specs=other.path)
        check(got.get("row") == "misrooted" and got.get("print") == [MIS, env_changed(env_line(other.path))]
              and head(r) == h and other.git("log", "--format=%s") == "init",
              "e_env_changed: another repository (%r)" % got)
        seed(env, "/create-ard", env_line=recorded.partition("), REPOS_PATH=")[0] + "), REPOS_PATH=/repos/elsewhere")
        got = run_end(env, "/create-ard")
        check(got.get("record") == "found" and got.get("row") == "pushed-default" and on_origin(r) == head(r) != h,
              "e_env_changed: a line differing only in its REPOS_PATH half commits (%r)" % got)

        # e_d3_below_top
        r, env = world(tmp, "e-d3")
        r.write("specs/specifications/PRD-ACME-1-x/prd.md", "---\nkind: prd\nkey: ACME-1\n---\n")
        r.commit_all("a nested specs tree")
        r.write("specs/specifications/PRD-ACME-1-x/dev-workflows/resume.md", "r\n")
        h = head(r)
        specs = os.path.join(r.path, "specs")
        got = run_end(env, "/create-ard", "--no-preflight", specs=specs)
        want = ("Specs preflight: SPECS_PATH is %s, below the top level of its repository (%s) — a specs tree inside a "
                "larger repository is unsupported, because this plugin switches branches and commits in the repository "
                "SPECS_PATH belongs to, so this run switches and commits nothing there; set SPECS_PATH to a dedicated "
                "specs repository's top level." % (specs, r.git("rev-parse", "--show-toplevel")))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, want]
              and head(r) == h, "e_d3_below_top: the below-top-level notice, nothing committed (%r)" % got)

        # e_declined_only
        r, env = world(tmp, "e-declined-only")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        got = cli("declined", "--command", "/create-ard", "--path", ard, env=env)
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("record") == "declined-only" and got.get("row") == "pushed-default"
              and got.get("line") == pushed_default(head(r)[:7], r.path) + appended(ard)
              and on_origin(r) == head(r) and record(env, "/create-ard") is None,
              "e_declined_only: the no-preflight path, the commit made, the declined append (%r)" % got)

        # e_silent
        plain = os.path.join(tmp, "e-silent-plain")
        os.makedirs(plain)
        env = {"HOME": os.path.join(tmp, "home-e-silent"), "CLAUDE_CODE_SESSION_ID": "e-silent", "SPECS_PATH": plain}
        os.makedirs(env["HOME"])
        got = run_end(env, "/feedback")
        check(got["_rc"] == 0 and got.get("row") == "silent" and got.get("print") == [] and got.get("line") is None
              and got.get("record") == "missing", "e_silent: no repository and no flag prints nothing (%r)" % got)

        # e_declined
        r, env = world(tmp, "e-declined")
        r.git("rm", "-q", PRD)
        r.git("commit", "-q", "-m", "drop the PRD")
        r.git("push", "-q", "origin", "main")
        ab = "specifications/PRD-ACME-1-x/a b.md"
        r.write(PRD, "prd\n")
        r.write(ab, "ab\n")
        seed(env, "/create-prd", declined=[PRD, ab])
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended("%s, %s" % (PRD, ab))),
              "e_declined: both declined paths, in the record's order (%r)" % got)
        r.git("add", PRD)
        r.git("commit", "-q", "-m", "ACME-1 the PRD, committed by hand")
        seed(env, "/create-prd", declined=[PRD, ab])
        r.write(RESUME, "r2\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended(ab)), "e_declined: only what is still uncommitted (%r)" % got)
        four = [ab, "specifications/PRD-ACME-1-x/c.md", "specifications/PRD-ACME-1-x/zahlungsauslösung.md",
                "specifications/PRD-ACME-1-x/d e.md"]
        for p in four[1:]:
            r.write(p, "x\n")
        seed(env, "/create-prd", declined=four)
        r.write(RESUME, "r3\n")
        got = run_end(env, "/create-prd")
        check((got.get("line") or "").endswith(appended("4 files under specifications/PRD-ACME-1-x")),
              "e_declined: four paths in one folder (%r)" % got)
        r, env = world(tmp, "e-declined-flag")
        r.git("rm", "-q", PRD)
        r.git("commit", "-q", "-m", "drop the PRD")
        r.git("push", "-q", "origin", "main")
        r.write(PRD, "prd\n")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd", "--declined", PRD)
        check(got.get("record") == "missing" and got.get("line") == pushed_default(head(r)[:7], r.path) + appended(PRD),
              "e_declined: no record and --declined (%r)" % got)

        # e_two_sessions
        r, env = world(tmp, "e-two")
        e1, e2 = dict(env, CLAUDE_CODE_SESSION_ID="s1"), dict(env, CLAUDE_CODE_SESSION_ID="s2")
        seed(e1, "/specify", specs_git="misrooted", misrooted_notice=["s1's notice"])
        r.write("notes.md", "n\n")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": "notes.md"})
        seed(e2, "/specify", guard="G1", guard_block=block, guard_paths=["notes.md"])
        with in_env(e1):
            s1_file = state.path("s1", "/specify")
        before = open(s1_file, encoding="utf-8").read()
        r.write(RESUME, "r\n")
        got = run_end(e2, "/specify")
        check(got.get("row") == "pushed-default" and got.get("print") == [pushed_default(head(r)[:7], r.path), block]
              and open(s1_file, encoding="utf-8").read() == before and record(e2, "/specify") is None,
              "e_two_sessions: s2 commits with its own block; s1's record untouched (%r)" % got)

        # e_stale_no_preflight
        r, env = world(tmp, "e-stale")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["a stale run's notice"])
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard", "--no-preflight")
        check(got.get("record") == "ignored" and got.get("row") == "pushed-default" and on_origin(r) == head(r)
              and record(env, "/create-ard") is None and "a stale run's notice" not in got.get("print", []),
              "e_stale_no_preflight: the stale record ignored and removed, the commit made (%r)" % got)

        # e_missing_record
        r, env = world(tmp, "e-missing")
        r.write(RESUME, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("record") == "missing" and got.get("row") == "pushed-default" and on_origin(r) == head(r)
              and record(env, "/feedback") is None, "e_missing_record: run as the no-preflight path (%r)" % got)

        # e_catch_up
        r, env = world(tmp, "e-catch-up")
        o = clone(r, "e-catch-up-other")
        o.write("other.md", "o\n")
        theirs = o.commit_all("NOISSUE another clone's change")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == theirs and on_origin(r) == head(r)
              and got.get("print") == [pushed_default(head(r)[:7], r.path)],
              "e_catch_up: main fast-forwarded before the commit, the push lands (%r)" % got)
        o.git("pull", "-q", "--ff-only", "origin", "main")
        o.write("other2.md", "o\n")
        o.commit_all("NOISSUE another")
        o.git("push", "-q", "origin", "main")
        r.git("fetch", "-q", "origin")
        missing = os.path.join(tmp, "e-catch-up-missing.git")
        r.git("remote", "set-url", "origin", missing)
        seed(env, "/create-ard")
        r.write(RESUME, "r2\n")
        got = run_end(env, "/create-ard")
        check(got.get("row") == "failed" and len(got.get("print", [])) == 2 and got["print"][0] == (
            "Specs preflight: could not fast-forward main (fatal: '%s' does not appear to be a git repository); the run "
            "goes on from it as it stands" % missing) and got["print"][1] == got.get("line"),
              "e_catch_up: a failed catch-up prints its line before the outcome line (%r)" % got)

        # e_nonff
        r, env = world(tmp, "e-nonff")
        seed(env, "/create-ard")
        o = clone(r, "e-nonff-other")
        o.write("other.md", "o\n")
        o.commit_all("NOISSUE another clone's change")
        o.git("push", "-q", "origin", "main")
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-ard")
        h = head(r)
        nxt = got.get("next") or {}
        rec = record(env, "/create-ard") or {}
        check(got["_rc"] == 0 and got.get("row") is None and got.get("print") == [] and got.get("line") is None
              and nxt.get("run", "").startswith("python3 ")
              and " --specs %s replay --for end --command /create-ard --branch main" % r.path in nxt.get("run", "")
              and "--set-upstream" not in nxt.get("run", "") and nxt.get("timeout_ms") == 420000
              and nxt.get("on_timeout") == nxt.get("run", "") + " --timed-out" and got.get("sha7") == h[:7],
              "e_nonff: next names the replay, in a call of its own (%r)" % got)
        check(rec.get("stage") == "end-replay" and (rec.get("end_commit") or {}).get("sha7") == h[:7]
              and rec["end_commit"].get("branch") == "main" and rec["end_commit"].get("files") == 1
              and rec["end_commit"].get("paths") == [RESUME] and rec["end_commit"].get("hook_paths") == [],
              "e_nonff: the record holds end_commit at stage end-replay (%r)" % rec)
        r, env = plugin_world("e-nonff-upstream", pushed=False)
        r.git("push", "-q", "origin", PLUGIN)
        o = clone(r, "e-nonff-upstream-other")
        o.git("switch", "-q", PLUGIN)
        o.write("specifications/PRD-ACME-1-x/dev-workflows/feedback/o.md", "o\n")
        o.commit_all("NOISSUE another clone's feedback")
        o.git("push", "-q", "origin", PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        check((got.get("next") or {}).get("run", "").endswith(" --branch %s --set-upstream" % PLUGIN),
              "e_nonff: --set-upstream where the push carried -u (%r)" % got)

        # e_resume
        r, env = world(tmp, "e-resume")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_check = g["push_check"]

        def killed(*args, **kw):
            raise KeyboardInterrupt

        stopped = False
        g["push_check"] = killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["push_check"] = real_check
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        rec = record(env, "/create-ard") or {}
        check(stopped and (rec.get("end_commit") or {}).get("sha7") == h[:7] and on_origin(r) != h,
              "e_resume: stopped right after its commit, which the record holds (%r)" % rec)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_resume: the commit is not made again, the push lands (%r)" % got)
        r, env = world(tmp, "e-resume-after-push")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_push = g["push"]

        def push_then_killed(*args, **kw):
            real_push(*args, **kw)
            raise KeyboardInterrupt

        def updates():
            p = subprocess.run(["git", "-C", r.bare, "reflog", "show", "refs/heads/main"], stdout=subprocess.PIPE)
            return len(p.stdout.decode().splitlines())

        stopped = False
        g["push"] = push_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["push"] = real_push
        h = head(r)
        landed = updates()
        check(stopped and on_origin(r) == h and landed == 1, "e_resume_after_push: stopped right after its push landed")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("pushed") is True
              and updates() == landed and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_resume_after_push: [up to date] reads as pushed, nothing pushed twice (%r)" % got)
        r.write(RESUME, "r stale\n")
        seed(env, "/create-ard", end_commit={"sha7": "0000000", "files": 1, "branch": "main", "paths": [RESUME],
                                             "hook_paths": []}, stage="end")
        with in_env(env):
            rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/create-ard")
            rec["updated"] = time.strftime(state.STAMP, time.gmtime(time.time() - 20 * 60))
            with open(state.path(env["CLAUDE_CODE_SESSION_ID"], "/create-ard"), "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == head(r)[:7] != "0000000"
              and on_origin(r) == head(r), "e_resume: an end_commit saved 20 minutes ago runs from step 1 (%r)" % got)

        # e_exit2
        r, env = world(tmp, "e-exit2")
        r.write(RESUME, "r\n")

        def snapshot():
            return (r.git("status", "--porcelain"), head(r), r.git("for-each-ref"),
                    subprocess.run(["git", "-C", r.bare, "for-each-ref"], stdout=subprocess.PIPE).stdout)

        before = snapshot()
        got = cli("--specs", r.path, "end", "--command", "/create-ard",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"}, stdin=b"")
        check(one_not_run_line(got) and snapshot() == before and not os.path.exists(os.path.join(env["HOME"], ".claude")),
              "e_exit2: no session variable, exit 2, one line, nothing changed (%r)" % got)
        for args, what in (((r.path, "/create-ard", "--commit-key", "acme-1"), "a lower-case key"),
                           ((r.path, "/create-ard", "--commit-key", "ACME-1\n"), "a key with a newline"),
                           ((r.path, "create-ard"), "a command without its slash"),
                           ((r.path, "/create-ard", "--session-branch-created", "xyz"), "a creation that is no sha")):
            got = cli("--specs", args[0], "end", "--command", *args[1:], env=env, stdin=b"")
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and snapshot() == before,
                  "e_exit2: %s is a usage exit 2 (%r)" % (what, got))
        got = cli("end", "--command", "/create-ard", env=env, stdin=b"")
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "e_exit2: no --specs at all is a usage error (%r)" % got)
        lone = os.path.join(tmp, "e-exit2-lone")
        os.makedirs(lone)
        shutil.copy(me, os.path.join(lone, "specs-git.py"))
        shutil.copy(os.path.join(HERE, "session-branch.py"), os.path.join(lone, "session-branch.py"))
        got = cli("--specs", r.path, "end", "--command", "/create-ard", env=env, stdin=b"",
                  script=os.path.join(lone, "specs-git.py"))
        check(one_not_run_line(got) and "specs_git_state" in got["_err"] and snapshot() == before,
              "e_exit2: end without its modules exits 2 with one line naming the missing one (%r)" % got)
        real_catch_up = g["catch_up"]

        def unreadable(*args, **kw):
            raise NotRun("a read failed")

        raised = False
        g["catch_up"] = unreadable
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except NotRun:
            raised = True
        finally:
            g["catch_up"] = real_catch_up
        check(raised and snapshot() == before, "e_exit2: a failure before the first repository write raises, so exit 2")

        # e_error_after_write
        r, env = world(tmp, "e-error")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")

        def boom(*args, **kw):
            raise RuntimeError("boom")

        g["push_check"] = boom
        try:
            with in_env(env):
                got = end(r.path, "/create-ard")
        finally:
            g["push_check"] = real_check
        want = ("Specs repo: NOT FINISHED — the terminal step stopped early (RuntimeError: boom); what it committed or pushed "
                "is as it left it, and the next run's preflight flushes the rest")
        check(got.get("error") == "RuntimeError: boom" and got.get("line") == want and got.get("print") == [want]
              and got.get("sha7") == head(r)[:7] and set(got) == FIELDS
              and r.git("log", "-1", "--format=%s") == "NOISSUE Add dev-workflows session artifacts (/create-ard)",
              "e_error_after_write: exit-0 result, error set, the commit made, the stopped line (%r)" % got)
        check(((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == head(r)[:7],
              "e_error_after_write: the record stays, its end_commit for --resume (%r)" % record(env, "/create-ard"))

        # e_kill_in_push: a signal during the push, which sb.git_bounded turns into NotRun, keeps the record
        r, env = world(tmp, "e-kill-in-push")
        seed(env, "/create-ard")
        r.write(RESUME, "r\n")
        real_bounded = sb.git_bounded

        def signalled_push(root, seconds, *args):
            if args and args[0] == "push":
                raise NotRun("git push ended by signal 15")
            return real_bounded(root, seconds, *args)

        sb.git_bounded = signalled_push
        try:
            with in_env(env):
                got = end(r.path, "/create-ard")
        finally:
            sb.git_bounded = real_bounded
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        check(got.get("error") == "git push ended by signal 15" and got.get("sha7") == h[:7] and on_origin(r) != h
              and ((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == h[:7],
              "e_kill_in_push: end.stopped, the commit made and unpushed, the record kept (%r)" % got)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_in_push: --resume pushes the first call's commit, nothing committed twice (%r)" % got)

        # e_kill_after_commit: no record, a kill between the commit and the save that names it
        r, env = world(tmp, "e-kill-after-commit")
        ard = "specifications/PRD-ACME-1-x/ard.md"
        r.write(ard, "ard\n")
        r.write(RESUME, "r\n")
        base = head(r)
        real_commit = g["commit_session_files"]

        def commit_then_killed(*args, **kw):
            real_commit(*args, **kw)
            raise KeyboardInterrupt

        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard", commit_key="ACME-1", register_rebuild="/x/register.py",
                    session_branch_created="abc1234", declined=[ard])
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        rec = record(env, "/create-ard") or {}
        pending = rec.get("end_commit") or {}
        check(stopped and h != base and rec.get("stage") == "end" and rec.get("started_by_script") is False
              and rec.get("declined") == [ard] and rec.get("commit_key") == "ACME-1"
              and rec.get("register_rebuild") == "/x/register.py" and rec.get("session_branch_created") == "abc1234"
              and "sha7" not in pending and pending.get("base") == base and pending.get("branch") == "main"
              and pending.get("staged") == {RESUME: r.git("rev-parse", "HEAD:" + RESUME)},
              "e_kill_after_commit: the record saved at the boundary, the commit about to be made in it (%r)" % rec)
        count = r.git("rev-list", "--count", "HEAD")
        got = run_end(env, "/create-ard", "--commit-key", "ACME-1", "--declined", ard, "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7]
              and got.get("line") == pushed_default(h[:7], r.path) + appended(ard)
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_after_commit: --resume finds the commit where it landed and pushes it (%r)" % got)
        r.write(RESUME, "r2\n")
        base = head(r)
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == base and on_origin(r) == head(r),
              "e_kill_after_commit: a pending commit that was never made runs from step 1 (%r)" % got)
        base = head(r)
        r.write(RESUME, "r3\n")
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        r.write("notes.md", "n\n")
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "Add notes")
        user = head(r)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "scope" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7],
              "e_kill_after_commit: a tip on the base that carries none of the staged paths is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-same-path")
        r.write(RESUME, "mine\n")
        base = head(r)
        seed(env, "/create-ard", stage="end",
             end_commit={"branch": "main", "base": base, "staged": {RESUME: r.git("hash-object", RESUME)}})
        r.write(RESUME, "theirs\n")
        r.git("add", RESUME)
        r.git("commit", "-q", "-m", "a commit of the user's on the same path")
        user = head(r)
        r.write(RESUME, "mine\n")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7]
              and got.get("sha7") != user[:7] and on_origin(r) == head(r),
              "e_kill_after_commit: a tip on the base touching a staged path with other content is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-removal")
        old = "specifications/PRD-ACME-1-x/dev-workflows/feedback/old.md"
        r.write(old, "old\n")
        r.commit_all("NOISSUE an earlier run's feedback")
        r.git("push", "-q", "origin", "main")
        os.remove(os.path.join(r.path, old))
        r.write(RESUME, "r\n")
        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        pending = (record(env, "/create-ard") or {}).get("end_commit") or {}
        check(stopped and pending.get("staged") == {old: None, RESUME: r.git("rev-parse", "HEAD:" + RESUME)},
              "e_kill_after_commit: a staged removal is saved as no blob (%r)" % pending)
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("files") == 2
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h,
              "e_kill_after_commit: a removal matches the path's absence at the tip (%r)" % got)
        r.write(old, "old again\n")
        r.commit_all("NOISSUE the feedback again")
        r.git("push", "-q", "origin", "main")
        base = head(r)
        r.write(RESUME, "y\n")
        seed(env, "/create-ard", stage="end", end_commit={"branch": "main", "base": base,
                                                          "staged": {old: None, RESUME: r.git("hash-object", RESUME)}})
        r.git("add", RESUME)
        r.git("commit", "-q", "-m", "a commit of the user's with the same blob, the removed path kept")
        user = head(r)
        os.remove(os.path.join(r.path, old))
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and r.git("rev-parse", "HEAD~1") == user and got.get("sha7") == head(r)[:7]
              and got.get("sha7") != user[:7], "e_kill_after_commit: a tip still holding a removed path is not the run's (%r)" % got)
        r, env = world(tmp, "e-kill-after-commit-msg")
        hook(os.path.join(r.path, ".git", "hooks", "commit-msg"), "printf '\\nChange-Id: I0123456789\\n' >> \"$1\"\n")
        r.write(RESUME, "r\n")
        stopped = False
        g["commit_session_files"] = commit_then_killed
        try:
            with in_env(env):
                end(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            g["commit_session_files"] = real_commit
        h = head(r)
        count = r.git("rev-list", "--count", "HEAD")
        check(stopped and r.git("log", "-1", "--format=%B").endswith("Change-Id: I0123456789") and on_origin(r) != h,
              "e_kill_after_commit: a commit-msg hook rewrote the message of the commit the kill followed")
        got = run_end(env, "/create-ard", "--resume")
        check(got.get("row") == "pushed-default" and got.get("sha7") == h[:7] and got.get("print") == [pushed_default(h[:7], r.path)]
              and r.git("rev-list", "--count", "HEAD") == count and on_origin(r) == h and record(env, "/create-ard") is None,
              "e_kill_after_commit: a rewritten message still resumes that commit, nothing committed twice (%r)" % got)

        # e_d3_signal
        r, env = world(tmp, "e-d3-signal")
        r.write(RESUME, "r\n")
        h = head(r)
        spec_dir = os.path.join(r.path, "specifications")
        got = run_end(env, "/create-ard", "--no-preflight", specs=spec_dir)
        stop = ("SPECS_PATH_INSIDE_TREE: SPECS_PATH is %s, which is itself a specifications/ directory — every folder "
                "lives under $SPECS_PATH/specifications/, so this run would look for and create folders in the wrong "
                "place; it wrote nothing under that path, and its cost and feedback are reported here instead. Set "
                "SPECS_PATH to %s where it is set, and re-run." % (spec_dir, os.path.realpath(r.path)))
        check(got.get("record") == "missing" and got.get("row") == "misrooted" and got.get("print") == [MIS, stop]
              and head(r) == h, "e_d3_signal: specs-root-check's one-line stop, nothing committed (%r)" % got)

        # e_g0_found: a record with no flag, HEAD detached since its start
        r, env = world(tmp, "e-g0-found")
        seed(env, "/specify")
        h = head(r)
        r.git("switch", "-q", "--detach")
        r.write(RESUME, "r\n")
        got, days, _ = dated(lambda: run_end(env, "/specify"))
        check(got.get("record") == "found" and got.get("row") == "blocked"
              and got.get("print") in [[BLOCKED, b] for b in g0_on(r, h, days)]
              and head(r) == h and record(env, "/specify") is None,
              "e_g0_found: a found record on a detached HEAD prints G0's block, nothing committed (%r)" % got)

        # e_resolve_default
        r, env = world(tmp, "e-resolve")
        check(resolve_default(r.path, False) == {"default": "main", "default_ref": "origin/main", "remote": "origin",
                                                 "offline": False}, "e_resolve_default: no origin/HEAD falls back to main")
        r.git("branch", "trunk")
        r.git("push", "-q", "origin", "trunk")
        r.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk")
        check(resolve_default(r.path, True) == {"default": "trunk", "default_ref": "origin/trunk", "remote": "origin",
                                                "offline": False}, "e_resolve_default: origin/HEAD names it, fetched")
        r.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/renamed")
        check(resolve_default(r.path, False)["default"] == "main",
              "e_resolve_default: origin/HEAD naming a ref that does not exist falls back")
        r.git("remote", "set-url", "origin", os.path.join(tmp, "e-resolve-missing.git"))
        check(resolve_default(r.path, True)["offline"] is True, "e_resolve_default: a failed fetch is offline")
        loc = new_repo(tmp, "e-resolve-local")
        check(resolve_default(loc.path, True) == {"default": "main", "default_ref": "refs/heads/main", "remote": "none",
                                                  "offline": False}, "e_resolve_default: no remote, the local ref, no fetch")
        loc.git("branch", "-m", "main", "master")
        check(resolve_default(loc.path, False)["default"] == "master", "e_resolve_default: then master")
        loc.git("branch", "-m", "master", "work")
        check(resolve_default(loc.path, False)["default"] == "work", "e_resolve_default: then the current branch")

        # e_key_grammar
        with open(ADDRESSING, encoding="utf-8") as fh:
            addressing = fh.read()
        section1 = addressing[addressing.index("## 1. Key grammar"):]
        fence = section1[section1.index("```\n") + 4:section1.index("\n```", section1.index("```\n") + 4)]
        check(fence == r"^[A-Z][A-Z0-9_]*(-\d+)+$" and "^" + KEY_RE.pattern.replace("[0-9]", r"\d") + "$" == fence,
              "e_key_grammar: KEY_RE is addressing §1's grammar, \\d spelt [0-9] (%r)" % fence)
        check(all(KEY_RE.fullmatch(k) for k in ("ACME-1", "ACME-90-01", "A_B2-7-1"))
              and not any(KEY_RE.fullmatch(k) for k in ("acme-1", "ACME", "ACME-1\n", "ACME-١", "ACME-1-")),
              "e_key_grammar: whole keys only, ASCII digits only")

        # e_push_status: push() over canned --porcelain output, for the statuses no local origin gives
        r, env = world(tmp, "e-push-status")
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
        real_bounded = sb.git_bounded

        def canned(status_line, rc=1):
            out = ("To origin\n%s\nDone\n" % status_line) if status_line else ""
            return lambda root, seconds, *args: subprocess.CompletedProcess(["git"] + list(args), rc, out.encode(), b"")

        try:
            for reason in TRANSIENT:
                sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote rejected] (%s x)" % reason)
                got = push(r.path, "main", False)
                check(got["outcome"] == "failed" and got["reason"] == "[remote rejected] (%s x)" % reason
                      and got["recorded"] is None and not os.path.exists(rec_file),
                      "e_push_status: %r is a failed push, never a refusal (%r)" % (reason, got))
            sb.git_bounded = canned(None, 124)
            got = push(r.path, "main", False)
            check(got["outcome"] == "failed" and got["reason"] == T["text.push-capped"], "e_push_status: capped (%r)" % got)
            sb.git_bounded = canned("+\trefs/heads/main:refs/heads/main\taaaaaaa...bbbbbbb (forced update)", 0)
            check(push(r.path, "main", False)["outcome"] == "pushed", "e_push_status: + is pushed")
            sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote failure] (remote failed to report status)")
            got = push(r.path, "main", False)
            check(got["outcome"] == "failed" and got["reason"] == "[remote failure] (remote failed to report status)",
                  "e_push_status: another status is a failed push (%r)" % got)
            sb.git_bounded = canned("!\trefs/heads/main:refs/heads/main\t[remote rejected] (push declined due to "
                                    "repository rule violations)")
            got, _, ldays = dated(lambda: push(r.path, "main", False))
            check(got == {"outcome": "refused", "reason": "push declined due to repository rule violations",
                          "recorded": "file", "record": rec_file, "record_error": None}
                  and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
                  "e_push_status: a host's refusal is recorded (%r)" % got)
        finally:
            sb.git_bounded = real_bounded

        # e_canned: the rows whose facts no repository here produces
        base = {"sha7": "abc1234", "files": 2, "branch": "main", "default": "main", "specs": "/s"}
        got = _row_line(lines, "push-refused", dict(base, reason="r", record_kind="config",
                                                    record="branch.main.workflowsPushRefused"))
        check(got.endswith("once origin takes pushes to main again, git -C \"/s\" config --unset branch.main."
                           "workflowsPushRefused") and "so this is recorded" in got,
              "e_canned: push refused, recorded in the configuration key (%r)" % got)
        got = _row_line(lines, "push-refused", dict(base, reason="r", record_kind=None, record_error="e"))
        check(got == "Specs repo: committed abc1234 (2 files) on main — push REFUSED by origin (r): a rule there takes no "
              "push of main, but this could not be recorded (e, the configuration write's), so a later run pushes main again",
              "e_canned: push refused and unrecorded (%r)" % got)
        got = _row_line(lines, "failed", dict(base, reason=T["text.push-capped"]))
        check(got == "Specs repo: committed abc1234 (2 files) on main — push FAILED (the push did not finish within 60 s); "
              "the commit is local and a later run retries it", "e_canned: a capped push (%r)" % got)
        got = _row_line(lines, "scope", dict(base, subject="s", scope={"failed": {"sha": "f" * 40, "reason": "paths",
                                                                                   "path": None}}))
        check("the oldest fffffff s, which changes no file;" in got, "e_canned: a commit that changes no file (%r)" % got)
        got = _row_line(lines, "scope", dict(base, hook=["a.md"], scope={"failed": {"sha": "abc1234" + "0" * 33,
                                                                                     "reason": "paths", "path": "a.md"}}))
        check("a pre-commit hook added a.md to this commit" in got, "e_canned: the hook variant with one path (%r)" % got)

        # §4 step 1's landing at the run's end (STAY-2; S1, S2): each case a start, then an end, on world with
        # other_key -- HEAD on prd/B-2-y, which no key of the run (ACME-1) names -- and, unless a case says otherwise,
        # notes.md, which is not the plugin's, dirty, so G1 fires and the preflight stays (an unkeyed stay); the run's
        # own session file is written after the start. Each expected line is rendered from the pins, never by the code
        # under test.
        LB = "prd/B-2-y"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        FB = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f.md"
        LEFT = "specifications/PRD-ACME-1-x/dev-workflows/feedback/left.md"
        FUP = "specifications/PRD-ACME-1-x/follow-ups.md"
        COST = "specifications/PRD-ACME-1-x/dev-workflows/cost/abcd1234.md"
        COST_BODY = "# Cost\n\n## 2026-11-10T10:00:00Z — /specify — draft\n\nbody\n"
        ENTRY = "## 2026-11-10 — /feedback — note\n\n%s\n"
        AX = "prd/A-1-x"
        KINDS = lines.placeholder("g1.landing.not_done", "<which no key")
        LANDED = lines.placeholder("app.landed", "<which no key")
        HELD_KIND = lines.placeholder("row.held", "<which no key")
        HELD_TAIL = lines.placeholder("row.held", "<held for")
        STUCK_KIND = lines.placeholder("row.held-stuck", "<which no key")
        CHECKED = lines.placeholder("reason.land.checked-out", "<the push of")
        UNKEYED = {"branch": LB, "kind": "unkeyed", "reason": "g1", "merged": False, "command": None}

        def case(name, fn):
            try:
                fn()
            except Exception as e:  # one case that crashes must not hide the others
                check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:400]))

        def start_of(env, *args):
            return cli("--specs", env["SPECS_PATH"], "start", "--command", "/feedback", "--key", "ACME-1", *args, env=env)

        def lworld(name, notes=True, extra=()):
            """world, <extra> ((path, body) pairs) committed on main and pushed, then other_key; notes.md dirty where
            <notes>."""
            r, env = world(tmp, name)
            for p, body in extra:
                r.write(p, body)
            if extra:
                r.commit_all("ACME-1 Add more")
                r.git("push", "-q", "origin", "main")
            other_key(r, LB)
            if notes:
                r.write("notes.md", "n\n")
            return r, env

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", name, check=False) or None

        def main_of(r):
            return ref(r, "refs/heads/main")

        def read(r, path):
            full = os.path.join(r.path, path)
            if not os.path.isfile(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def gone(r, path):
            return not os.path.lexists(os.path.join(r.path, path))

        def changed(r, rev):
            return sorted(x for x in r.git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).split("\n") if x)

        def show(r, rev, path):
            return r.git("show", "%s:%s" % (rev, path), check=False)

        def held(r):
            return held_entries(r.path)

        def held_refs(r):
            return r.git("for-each-ref", "--format=%(refname)", HELD_REF).split()

        def on_lb(r):
            return r.git("symbolic-ref", "--short", "HEAD") == LB

        def reflog_landed(r):
            return [x for x in r.git("reflog", "--format=%gs", "refs/heads/main").split("\n") if x.startswith("specs-git: landed")]

        def landed(r, n, branch=LB, kind="unkeyed", sha7=None, row=None):
            """The row the landing's commit takes on main -- pushed-default unless <row> gives another line's opening
            -- then app.landed for a stay of <kind> on <branch>."""
            line = row if row is not None else pushed_default(sha7 or (main_of(r) or "")[:7], r.path, n)
            return line + lines.fill("app.landed", {"<branch>": branch, "<default>": "main", LANDED: STAY_KINDS.index(kind)})

        def g1_plain(r):
            return lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})

        def g1_form(r, not_done=None, if_ignored=None):
            """G1's block for notes.md: the plain block, its Not done and If ignored parts replaced, each on one line."""
            rows = g1_plain(r).split("\n")
            at = {x: next(k for k, row in enumerate(rows) if row.startswith(x)) for x in ("Not done:", "Fix:", "If ignored:")}
            nd = rows[at["Not done:"]:at["Fix:"]] if not_done is None else ["Not done: " + not_done]
            ig = rows[at["If ignored:"]:] if if_ignored is None else ["If ignored: " + if_ignored]
            return "\n".join(rows[:at["Not done:"]] + nd + rows[at["Fix:"]:at["If ignored:"]] + ig)

        def g1_land(r, unlanded=False, branch=LB):
            """G1's landing form for an unkeyed stay on <branch> as the end repeats it: whole, or not-landed."""
            tid = "g1.landing.not_done.unlanded" if unlanded else "g1.landing.not_done"
            return g1_form(r, lines.fill(tid, {"<default>": "main", "<branch>": branch, KINDS: 0}), T["g1.landing.if_ignored"])

        def stuck_cmds(r, sha7, default_ref="origin/main"):
            return ("'git -C \"%s\" show %s'" % (r.path, sha7),
                    "'python3 \"%s\" --specs \"%s\" land --default-ref %s --drop-held %s'" % (me, r.path, default_ref, sha7))

        def worktree_on_main(r, name):
            path = os.path.join(tmp, name)
            r.git("worktree", "add", "-q", path, "main")
            return Repo(path)

        def ahead_on_origin(r, name):
            """origin's main one commit ahead of r's: another clone's commit, which r fetches at its start."""
            o = clone(r, name)
            o.write("specifications/PRD-ACME-1-x/notes-other.md", "o\n")
            o.commit_all("ACME-1 Other work")
            o.git("push", "-q", "origin", "main")

        def e_land_g1():
            """Path 1, G1: the run's own file lands on main, the checkout unmoved, the branch and its origin copy unmoved,
            the file lifted, notes.md left dirty."""
            r, env = lworld("e-land-g1")
            br, up = ref(r, "refs/heads/" + LB), on_origin(r, LB)
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            check(first.get("stay") == UNKEYED and got["_rc"] == 0 and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 1), g1_land(r)] and got.get("branch") == "main"
                  and got.get("sha7") == tip[:7] and got.get("pushed") is True and on_origin(r) == tip
                  and changed(r, tip) == [FB] and r.git("log", "-1", "--format=%s", tip) == SUBJECT % ("NOISSUE", "/feedback")
                  and ref(r, "refs/heads/" + LB) == br and on_origin(r, LB) == up and on_lb(r)
                  and gone(r, FB) and r.git("status", "--porcelain") == "?? notes.md" and record(env, "/feedback") is None
                  and held(r) == [] and reflog_landed(r) == ["specs-git: landed " + tip[:7]],
                  "e_land_g1: landed on main, alternative 0, then G1's landing form; the checkout and the branch unmoved, "
                  "the file lifted (%r)" % got)

        def e_land_refused():
            """Path 2, a switch git refused: an index.lock at the start makes B4's switch fail; the end lands."""
            r, env = lworld("e-land-refused", notes=False)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                first = start_of(env)
            finally:
                os.remove(lock)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("stay") == dict(UNKEYED, reason="refused") and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 1)] and changed(r, main_of(r)) == [FB] and gone(r, FB) and on_lb(r),
                  "e_land_refused: the refused switch's stay lands at the end (%r, %r)" % (first.get("stay"), got))

        def e_land_unlisted():
            """Path 3: status could not run at the start, so no snapshot: a leftover dirty before the start lands with the
            run's own file, and the line says so."""
            r, env = lworld("e-land-unlisted", notes=False)
            r.write(LEFT, ENTRY % "left")
            real = g["status"]

            def broken(root):
                raise NotRun("git status: fatal: index file corrupt")

            g["status"] = broken
            try:
                with in_env(env):
                    first = start(r.path, "/feedback", ("ACME-1",))
            finally:
                g["status"] = real
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("stay") == dict(UNKEYED, reason="unlisted") and first.get("start_dirty") is None
                  and got.get("row") == "pushed-default"
                  and got.get("print") == [landed(r, 2) + lines.fill("app.landed.unlisted", {"<branch>": LB})]
                  and changed(r, main_of(r)) == sorted([FB, LEFT]) and gone(r, FB) and gone(r, LEFT),
                  "e_land_unlisted: the leftover lands too, and app.landed.unlisted says so (%r)" % got)

        def e_land_stopped():
            """Path 4: the preflight stopped early before B4's switch."""
            r, env = lworld("e-land-stopped", notes=False)
            real = g["_disposition"]
            g["_disposition"] = boom
            try:
                with in_env(env):
                    first = start(r.path, "/feedback", ("ACME-1",))
            finally:
                g["_disposition"] = real
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(first.get("error") == "RuntimeError: boom" and first.get("stay") == dict(UNKEYED, reason="stopped")
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1)] and gone(r, FB),
                  "e_land_stopped: the early stop's stay lands (%r)" % got)

        def e_land_budget():
            """Path 5: start --budget 0 stopped at its budget, its next never made, so the record holds no stay; end asks
            for one (_unfinished_stay) and lands. And once HEAD has moved to another branch, none is asked for."""
            r, env = lworld("e-land-budget", notes=False)
            first = start_of(env, "--budget", "0")
            rec = record(env, "/feedback") or {}
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check((first.get("next") or {}).get("run") and rec.get("stage") in START_STAGES and rec.get("stay") is None
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, LB, "unkeyed")]
                  and changed(r, main_of(r)) == [FB] and gone(r, FB) and on_lb(r),
                  "e_land_budget: the unfinished start's branch takes the landing (%r, %r)" % (rec.get("stage"), got))
            r, env = lworld("e-land-budget-moved", notes=False)
            start_of(env, "--budget", "0")
            old = main_of(r)
            r.git("switch", "-q", "-c", "prd/B-2-z")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("branch") == "prd/B-2-z" and main_of(r) == old and changed(r, "HEAD") == [FB]
                  and "stayed on" not in (got.get("line") or ""),
                  "e_land_budget_moved: HEAD on a branch the start never stood on: end commits there (%r)" % got)

        def e_land_legacy():
            """P12: a 1.82.0 record -- merged_stay, no start_dirty -- on a merged branch lands against HEAD, every session
            file dirty going with the run's, and no unlisted clause, since no status failure is recorded."""
            r, env = world(tmp, "e-land-legacy")
            r.git("switch", "-q", "-c", AX)
            r.write("specifications/PRD-A-1-x/prd.md", "x\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", AX)
            o = clone(r, "e-land-legacy-other")
            o.git("merge", "-q", "--ff-only", "origin/" + AX)
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            seed(env, "/feedback", branch=AX)
            with in_env(env):
                path = state.path("e-land-legacy", "/feedback")
            with open(path, encoding="utf-8") as fh:
                rec = json.load(fh)
            for k in ("stay", "start_dirty", "midrun", "protects"):
                rec.pop(k, None)
            rec["merged_stay"] = {"branch": AX, "reason": "g1"}
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(rec, fh)
            r.write(LEFT, ENTRY % "left")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 2, AX, "merged")]
                  and changed(r, main_of(r)) == sorted([FB, LEFT]) and gone(r, FB) and gone(r, LEFT)
                  and r.git("symbolic-ref", "--short", "HEAD") == AX,
                  "e_land_legacy: the legacy stay lands against HEAD, no unlisted clause (%r)" % got)

        def e_land_merged():
            """S2: G1 on a fast-forward-merged branch lands (alternative 1), the file lifted, the branch still merged;
            with notes.md cleaned, the next start leaves the branch and deletes it -- which a file left in the working
            tree at a path main now holds would make git refuse."""
            r, env = world(tmp, "e-land-merged")
            r.git("switch", "-q", "-c", AX)
            r.write("specifications/PRD-A-1-x/prd.md", "x\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", AX)
            o = clone(r, "e-land-merged-other")
            o.git("merge", "-q", "--ff-only", "origin/" + AX)
            o.git("push", "-q", "origin", "main")
            r.write("notes.md", "n\n")
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            v = {"<default>": "main", "<branch>": AX, KINDS: 1}
            merged_form = g1_form(r, lines.fill("g1.landing.not_done", v),
                                  lines.fill("g1.merged.if_ignored", v)).split("\n")
            fix = lines.fill("g1.merged.fix", {"<SPECS_PATH>": r.path, "<default>": "main", "<path list>": "notes.md"})
            k = next(i for i, row in enumerate(merged_form) if row.startswith("Fix:"))
            j = next(i for i, row in enumerate(merged_form) if row.startswith("If ignored:"))
            merged_form = "\n".join(merged_form[:k] + ["Fix:      " + fix] + merged_form[j:])
            check(first.get("stay") == dict(UNKEYED, branch=AX, kind="merged", merged=True)
                  and got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, AX, "merged"), merged_form]
                  and gone(r, FB) and branch_merged(r.path, "HEAD", "origin/main")["merged"]
                  and r.git("symbolic-ref", "--short", "HEAD") == AX,
                  "e_land_merged: alternative 1, lifted, the branch still merged (%r)" % got)
            os.remove(os.path.join(r.path, "notes.md"))
            got = start_of(env)
            check("Specs preflight: deleted merged prd/A-1-x" in (got.get("print") or [])
                  and got.get("branch") == "main" and ref(r, "refs/heads/" + AX) is None,
                  "e_land_merged: the next start leaves and deletes the merged branch (%r)" % got)

        def e_land_leftover_kept():
            """S1: a session file dirty before the start is not the run's: only the run's file reaches main, and the
            leftover is as it was."""
            r, env = lworld("e-land-leftover-kept")
            r.write(LEFT, ENTRY % "left")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("print") == [landed(r, 1), g1_land(r)] and changed(r, main_of(r)) == [FB]
                  and show(r, "main", LEFT) == "" and read(r, LEFT) == ENTRY % "left" and gone(r, FB),
                  "e_land_leftover_kept: the leftover stays out of main, unchanged (%r)" % got)

        def e_land_leftover_shared():
            """The run appends to the leftover's own block file: only the appended entry reaches main, and the working
            copy is the leftover's version after the lift."""
            r, env = lworld("e-land-leftover-shared")
            left = "## 2026-11-09 — /specify — left\n\nleft\n"
            mine = "## 2026-11-10 — /feedback — mine\n\nmine\n"
            r.write(FB, left)
            start_of(env)
            r.write(FB, left + mine)
            got = run_end(env, "/feedback")
            on_main = show(r, "main", FB)
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r)]
                  and "mine" in on_main and "left" not in on_main and read(r, FB) == left,
                  "e_land_leftover_shared: the run's entry alone on main, the leftover's version left (%r, %r)"
                  % (got, on_main))

        def e_land_commit_key():
            """The re-test: an unkeyed stay whose branch the end's --commit-key names is the run's own -- dropped, and the
            end commits on it, with the plain block; and, for a run typed mid-run, an unmerged mid-run stay is dropped
            the same way, nothing landing on main."""
            r, env = lworld("e-land-commit-key")
            first = start_of(env)
            old, up = main_of(r), on_origin(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--commit-key", "B-2")
            h = head(r)
            check(first.get("stay") == UNKEYED and got.get("row") == "pushed-plugin"
                  and got.get("print") == ["Specs repo: committed %s (1 file) on %s — pushed" % (h[:7], LB), g1_plain(r)]
                  and on_origin(r, LB) == h and changed(r, h) == [FB] and main_of(r) == old and on_origin(r) == up
                  and r.git("log", "-1", "--format=%s", h) == SUBJECT % ("B-2", "/feedback"),
                  "e_land_commit_key: the stay dropped, committed on the branch, the plain block (%r)" % got)
            r, env = lworld("e-land-commit-key-midrun", notes=False)
            old, up = main_of(r), on_origin(r)
            midrun = {"command": "/specify", "started": "2026-11-10T10:00:00Z", "branch": LB}
            seed(env, "/feedback", branch=LB, keys=["ACME-1"], start_dirty={}, midrun=midrun,
                 stay={"branch": LB, "kind": "mid-run", "reason": "mid-run", "merged": False, "command": "/specify"})
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--commit-key", "B-2")
            check(got.get("error") is None and main_of(r) == old and on_origin(r) == up and on_lb(r)
                  and changed(r, "HEAD") == [FB] and "stayed on" not in (got.get("line") or ""),
                  "e_land_commit_key_midrun: the mid-run stay dropped, nothing landed on main (%r)" % got)

        def e_land_moved():
            """HEAD moved to a new branch before the end: no stay stands there, so end commits where HEAD stands, with G1's
            plain block."""
            r, env = lworld("e-land-moved")
            start_of(env)
            old = main_of(r)
            r.git("switch", "-q", "-c", "prd/B-2-z")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("branch") == "prd/B-2-z" and got.get("sha7") == head(r)[:7] and changed(r, "HEAD") == [FB]
                  and main_of(r) == old and (got.get("print") or [""])[-1] == g1_plain(r)
                  and "stayed on" not in (got.get("line") or ""),
                  "e_land_moved: committed on the branch HEAD moved to, the plain block (%r)" % got)

        def e_land_checked_out_pushed():
            """C2: another worktree has main checked out, behind origin's: the landing builds on origin/main and pushes by
            refspec -- pushed-default at once -- leaving local main and that worktree as they were."""
            r, env = lworld("e-land-co-pushed")
            w2 = worktree_on_main(r, "e-land-co-pushed-w2")
            ahead_on_origin(r, "e-land-co-pushed-other")
            start_of(env)
            local = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            up = on_origin(r) or ""
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, sha7=up[:7]), g1_land(r)]
                  and got.get("pushed") is True and changed(r, up) == [FB] and main_of(r) == local
                  and w2.git("status", "--porcelain") == "" and gone(r, FB) and held(r) == [],
                  "e_land_checked_out_pushed: pushed by refspec, local main and w2 untouched (%r)" % got)

        def e_land_held():
            """A cause that passes: w2 has main checked out and origin cannot be reached, so the refspec push fails and
            the change is held -- the held row, alternative 0, the checked-out clause with the push's reason, ending
            that the next run tries again; the files stay; one held entry."""
            r, env = lworld("e-land-held")
            w2 = worktree_on_main(r, "e-land-held-w2")
            start_of(env)
            os.rename(r.bare, r.bare + ".gone")  # origin unreachable, its URL -- and so the Environment: line -- as it was
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            refused = entries[0]["refused"] if len(entries) == 1 else {}
            detail = refused.get("detail") or {}
            clause = lines.fill("reason.land.checked-out", {"<path>": refused.get("path"), "<default>": "main", CHECKED: 0,
                                                            "<reason>": detail.get("text")})
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": clause})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and refused.get("reason") == "checked-out" and refused.get("permanent") is False
                  and detail.get("outcome") == "failed" and os.path.samefile(refused.get("path"), w2.path)
                  and want.endswith("held for main, and the next run tries again")
                  and read(r, FB) == ENTRY % "mine" and main_of(r) == old and got.get("sha7") is None,
                  "e_land_held: the held row, the files kept, one held entry (%r, %r)" % (got, entries))

        def e_land_checked_out_no_origin():
            """A cause that will not pass: w2 has main checked out and there is no origin, so nowhere to push: the held,
            stuck row, the no-origin alternative, its two commands quoted whole."""
            r, env = lworld("e-land-co-none")
            w2 = worktree_on_main(r, "e-land-co-none-w2")
            r.git("remote", "remove", "origin")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            clause = lines.fill("reason.land.checked-out", {"<path>": entries[0]["refused"]["path"] if entries else None,
                                                            "<default>": "main", CHECKED: 1})
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0, "<reason clause>": clause,
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "refs/heads/main"})
            cmds = stuck_cmds(r, sha7, "refs/heads/main")
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and "there is no origin to push the commit to" in want and all(c in want for c in cmds)
                  and entries[0]["refused"]["permanent"] is True and read(r, FB) == ENTRY % "mine"
                  and w2.git("status", "--porcelain") == "",
                  "e_land_checked_out_no_origin: held stuck, nowhere to push, both commands (%r)" % got)

        def e_land_stuck():
            """The run's only change edits an entry main holds: refused edited, held stuck, nothing committed."""
            r, env = lworld("e-land-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            old = main_of(r)
            r.write(COST, COST_BODY.replace("body", "edited"))
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                 "<reason clause>": lines.fill("reason.land.edited", {"<path>": COST}),
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "origin/main"})
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and all(c in want for c in stuck_cmds(r, sha7)) and main_of(r) == old
                  and read(r, COST) == COST_BODY.replace("body", "edited"),
                  "e_land_stuck: held stuck, reason edited, both commands quoted whole (%r)" % got)

        def e_land_partial():
            """P29: that edit beside a feedback file: the feedback file lands, the cost file is held alone -- the
            landing's row with app.landed, then app.held.stuck naming it -- and the not-landed form."""
            r, env = lworld("e-land-partial", extra=[(COST, COST_BODY)])
            start_of(env)
            r.write(COST, COST_BODY.replace("body", "edited"))
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            stuck = lines.fill("app.held.stuck", {"<path>": [COST], "<reason clause>": lines.fill("reason.land.edited",
                                                                                                {"<path>": COST}),
                                                  "<SPECS_PATH>": r.path, "<sha7>": sha7, "<default>": "main",
                                                  "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck, g1_land(r, unlanded=True)]
                  and changed(r, main_of(r)) == [FB] and gone(r, FB) and read(r, COST) == COST_BODY.replace("body", "edited")
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "e_land_partial: the feedback file landed, the cost file held alone (%r)" % got)

        def e_land_there():
            """P26: the run's change is already on main: the there row, the file taken out, main unmoved."""
            r, env = lworld("e-land-there", notes=False)
            r.git("switch", "-q", "main")
            r.write(FB, ENTRY % "mine")
            r.commit_all("NOISSUE Add dev-workflows session artifacts (/feedback)")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "there"
                  and got.get("print") == [lines.fill("row.there", {"<default>": "main", "<branch>": LB}),
                                           g1_land(r, unlanded=True)]
                  and main_of(r) == old and gone(r, FB) and held(r) == [],
                  "e_land_there: the there row, lifted, main unmoved (%r)" % got)

        def e_land_kill():
            """A kill during the lift: main moved, the files dirty, end_commit's landing saved; end --resume lifts them
            and pushes, the same commit, main moved once."""
            r, env = lworld("e-land-kill")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["_lift"] = real
            tip = main_of(r)
            rec = record(env, "/feedback") or {}
            landing = (rec.get("end_commit") or {}).get("landing") or {}
            check(killed and tip != old and read(r, FB) == ENTRY % "mine" and landing.get("tip") == tip
                  and len(held(r)) == 1,
                  "e_land_kill: main moved, the file dirty, the landing saved (%r)" % rec.get("end_commit"))
            got = run_end(env, "/feedback", "--resume")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r)]
                  and got.get("sha7") == tip[:7] and main_of(r) == tip and on_origin(r) == tip and gone(r, FB)
                  and held(r) == [] and reflog_landed(r) == ["specs-git: landed " + tip[:7]]
                  and record(env, "/feedback") is None,
                  "e_land_kill: end --resume lifts and pushes the same commit, main moved once (%r)" % got)

        def e_land_kill_resumed():
            """A kill during the lift, resumed, where part of the change was held alone (the paths split off it found
            again by its c1: the row keeps app.held.stuck and the not-landed form), and where the change was pushed by
            refspec (its move verified on origin's main after a fetch: the pushed-default row at once)."""
            r, env = lworld("e-land-kill-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            r.write(COST, COST_BODY.replace("body", "edited"))
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            got = run_end(env, "/feedback", "--resume")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            stuck = lines.fill("app.held.stuck", {"<path>": [COST], "<reason clause>": lines.fill("reason.land.edited",
                                                                                                {"<path>": COST}),
                                                  "<SPECS_PATH>": r.path, "<sha7>": sha7, "<default>": "main",
                                                  "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck, g1_land(r, unlanded=True)]
                  and gone(r, FB) and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "e_land_kill_stuck: resumed, the path held alone still named (%r)" % got)
            r, env = lworld("e-land-kill-refspec")
            w2 = worktree_on_main(r, "e-land-kill-refspec-w2")
            start_of(env)
            local = main_of(r)
            r.write(FB, ENTRY % "mine")
            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            up = on_origin(r) or ""
            r.git("update-ref", "-d", "refs/remotes/origin/main")  # the fetch the verification makes brings it back
            got = run_end(env, "/feedback", "--resume")
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1, sha7=up[:7]), g1_land(r)]
                  and got.get("pushed") is True and changed(r, up) == [FB] and on_origin(r) == up
                  and main_of(r) == local and gone(r, FB) and held(r) == [] and w2.git("status", "--porcelain") == "",
                  "e_land_kill_refspec: resumed, the refspec push verified on origin's main, its row at once (%r)" % got)

        def e_land_kill_register():
            """A landing whose register rebuild renumbered a record, cut off during the lift after its move: end --resume
            reads the moves from the journal, and its line carries the register clause the uninterrupted end prints."""
            canned = {"before_remote": {"web": {"o1": 1}}, "before_run": {"web": {"o2": 3}},
                      "after": {"web": {"o1": 2, "o2": 1}}}
            moves = sb._moves([canned])
            clause = "; ".join(
                lines.fill("app.register-clause", {"<slug>": slug, "<move>": [
                    lines.fill("app.register-move", {"<from>": m["from"], "<to>": m["to"], "<origin>": m["origin"],
                                                     "<whose number>": T["app.register-move." + m["side"]]})
                    for m in moves if m["slug"] == slug]})
                for slug in sorted({m["slug"] for m in moves}, key=[m["slug"] for m in moves].index))
            real_own, real_lift = sb.own_change, g["_lift"]

            def own_renumbering(*args, **kw):
                return dict(real_own(*args, **kw), numbers=canned)

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            shown = {}
            for name, kill in (("e-land-register-whole", False), ("e-land-kill-register", True)):
                r, env = lworld(name)
                start_of(env)
                r.write(FB, ENTRY % "mine")
                sb.own_change = own_renumbering
                if kill:
                    g["_lift"] = lift_killed
                try:
                    with in_env(env):
                        got = end(r.path, "/feedback")
                except KeyboardInterrupt:
                    got = None
                finally:
                    sb.own_change, g["_lift"] = real_own, real_lift
                if kill:
                    rec = record(env, "/feedback") or {}
                    journal = ((rec.get("end_commit") or {}).get("landing") or {}).get("moves")
                    got = run_end(env, "/feedback", "--resume")
                    check(journal == moves and moves,
                          "e_land_kill_register: the journal saved through on_move carries the moves (%r)" % journal)
                shown[name] = (got or {}).get("print"), landed(r, 1) + "; " + clause, g1_land(r)
            whole, killed = shown["e-land-register-whole"], shown["e-land-kill-register"]
            check(whole[0] == [whole[1], whole[2]] and killed[0] == [killed[1], killed[2]],
                  "e_land_kill_register: the resumed line carries the register clause the uninterrupted end prints "
                  "(%r)" % (shown,))

        def set_mode(env, mode):
            """The record's mode, as start records it: unsupported on a git whose merge-tree cannot merge without a
            checkout, with session-branch mode opted in."""
            with in_env(env):
                rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/feedback")
                rec["mode"] = mode
                state.save(env["CLAUDE_CODE_SESSION_ID"], "/feedback", rec)

        def e_land_unsupported():
            """I1, §6: in unsupported mode, the held, held-stuck and there rows -- none of which commits the files this
            run -- take no unsupported clause; the nothing row, which §6 does not except, keeps it."""
            unsupported = lines.fill("app.session.unsupported", {"<branch>": LB})
            # held: an index.lock at the landing's start
            r, env = lworld("e-land-unsup-held")
            start_of(env)
            set_mode(env, "unsupported")
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback")
            finally:
                os.remove(lock)
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"})})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)],
                  "e_land_unsupported: the held row takes no unsupported clause (%r)" % got)
            # held, stuck: an entry main holds, edited
            r, env = lworld("e-land-unsup-stuck", extra=[(COST, COST_BODY)])
            start_of(env)
            set_mode(env, "unsupported")
            r.write(COST, COST_BODY.replace("body", "edited"))
            got = run_end(env, "/feedback")
            entries = held(r)
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                 "<reason clause>": lines.fill("reason.land.edited", {"<path>": COST}),
                                                 "<SPECS_PATH>": r.path, "<sha7>": sha7, "<specs-git.py's path>": me,
                                                 "<default-ref>": "origin/main"})
            check(got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)],
                  "e_land_unsupported: the held, stuck row takes no unsupported clause (%r)" % got)
            # there: the run's change already on main
            r, env = lworld("e-land-unsup-there", notes=False)
            r.git("switch", "-q", "main")
            r.write(FB, ENTRY % "mine")
            r.commit_all("NOISSUE Add dev-workflows session artifacts (/feedback)")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            set_mode(env, "unsupported")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "there"
                  and got.get("print") == [lines.fill("row.there", {"<default>": "main", "<branch>": LB}),
                                           g1_land(r, unlanded=True)],
                  "e_land_unsupported: the there row takes no unsupported clause (%r)" % got)
            # nothing: §6 does not except it, so the clause stands
            r, env = lworld("e-land-unsup-nothing")
            start_of(env)
            set_mode(env, "unsupported")
            got = run_end(env, "/feedback")
            check(got.get("row") == "nothing" and got.get("print") == [T["row.nothing"] + unsupported,
                                                                     g1_land(r, unlanded=True)],
                  "e_land_unsupported: the nothing row keeps the unsupported clause (%r)" % got)

        def e_land_resume_moved():
            """I2: a landing cut off before its move, then HEAD switched off the stayed branch: end --resume drops the
            journal entry -- nothing moved, the file still in the working tree -- and goes on as an end whose HEAD
            moved, committing where HEAD stands: on main (pushed), and on a third branch (not on origin)."""
            for to in ("main", "prd/B-2-z"):
                r, env = lworld("e-land-resume-moved-" + to.replace("/", "-"))
                start_of(env)
                r.write(FB, ENTRY % "mine")
                real = g["land"]

                def land_killed(*args, **kw):
                    inner = kw["on_move"]

                    def on_move(pending):
                        inner(pending)
                        raise KeyboardInterrupt
                    kw["on_move"] = on_move
                    return real(*args, **kw)

                g["land"] = land_killed
                try:
                    with in_env(env):
                        end(r.path, "/feedback")
                except KeyboardInterrupt:
                    pass
                finally:
                    g["land"] = real
                old = main_of(r)
                r.git("switch", "-q", *(["main"] if to == "main" else ["-c", to]))
                got = run_end(env, "/feedback", "--resume")
                h = head(r)
                if to == "main":
                    row = pushed_default(h[:7], r.path)
                    ok = got.get("row") == "pushed-default" and on_origin(r) == h and r.git("rev-parse", h + "^") == old
                else:
                    row = lines.fill("row.origin-lacks", {"<sha7>": h[:7], "<N>": 1, "<branch>": to, "<SPECS_PATH>": r.path})
                    ok = got.get("row") == "origin-lacks" and main_of(r) == old
                check(ok and got.get("print") == [row, g1_plain(r)] and changed(r, h) == [FB]
                      and r.git("symbolic-ref", "--short", "HEAD") == to and held(r) == [] and held_refs(r) == []
                      and r.git("status", "--porcelain") == "?? notes.md" and record(env, "/feedback") is None,
                      "e_land_resume_moved: HEAD on %s, the journal dropped, committed where HEAD stands (%r)" % (to, got))
            # no row is ever filled from a status the landing's end has none for (a raw template id)
            run = {"state": state, "lines": lines, "specs": tmp, "session": "x", "command": "/feedback", "record": "found",
                   "wrote": True, "pre": [], "commit": None}
            try:
                _landing_end(run, {}, {"default": "main", "default_ref": "origin/main"}, UNKEYED,
                             {"status": "kept", "held_landed": [], "stuck": None}, {"declined": [], "guard_block": None,
                                                                                   "guard_paths": []})
                raised = None
            except NotRun as e:
                raised = str(e)
            check(raised and "kept" in raised,
                  "e_land_resume_moved: a status with no landing row raises, never prints its id (%r)" % raised)

        def e_land_origin_lacks_default():
            """I3: origin exists but has no main yet (t_merged_unknown's world): G1 keeps an unkeyed stay, and the
            landing builds on local main, as (2) gives it; the push follows push_check's row for main -- none where main
            tracks nothing (push-scope finds every other commit on origin's prd/B-2-y, so the push creates origin's
            main), remote-deleted where main tracks an origin/main origin no longer has."""
            for name, tracks in (("e-land-no-origin-main", False), ("e-land-no-origin-main-tracked", True)):
                bare = os.path.join(tmp, name + ".git")
                subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
                r = new_repo(tmp, name)
                r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
                r.commit_all("ACME-1 Add the PRD")
                r.git("remote", "add", "origin", bare)
                r.bare = bare
                if tracks:
                    r.git("config", "branch.main.remote", "origin")
                    r.git("config", "branch.main.merge", "refs/heads/main")
                env = {"HOME": os.path.join(tmp, "home-" + name), "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}
                os.makedirs(env["HOME"])
                other_key(r, LB)
                r.write("notes.md", "n\n")
                local = main_of(r)
                first = start_of(env)
                r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                tip = main_of(r) or ""
                if tracks:
                    row = (lines.fill("row.remote-deleted", {"<sha7>": tip[:7], "<N>": 1, "<branch>": "main",
                                                             "<SPECS_PATH>": r.path})
                           + lines.fill("row.remote-deleted.default-tail", {"<SPECS_PATH>": r.path}))
                    want = ("remote-deleted", landed(r, 1, row=row), None)
                else:
                    want = ("pushed-default", landed(r, 1), tip)
                check(first.get("stay") == UNKEYED and first.get("default_ref") == "origin/main"
                      and (got.get("row"), got.get("line"), on_origin(r)) == want and got.get("error") is None
                      and tip != local and r.git("rev-parse", tip + "^") == local and changed(r, tip) == [FB]
                      and gone(r, FB) and on_lb(r) and (got.get("print") or [""])[-1] == g1_land(r),
                      "%s: landed on local main, its row from push_check (%r)" % (name.replace("-", "_").replace(
                          "e_land_no_origin_main", "e_land_origin_lacks_default"), got))

        def e_land_origin_lacks_checked_out():
            """New Important 1 (round 2): origin has no main, w2 has main checked out, and local main holds a private
            commit of the user's: the landing never builds on local main for a refspec push, which would publish that
            commit unmeasured -- the change is held stuck (checked-out, origin has no main), nothing pushed, origin and
            both branches as they were."""
            name = "e-land-no-origin-main-co"
            bare = os.path.join(tmp, name + ".git")
            subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
            r = new_repo(tmp, name)
            r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD\n")
            r.commit_all("ACME-1 Add the PRD")
            r.git("remote", "add", "origin", bare)
            r.bare = bare
            env = {"HOME": os.path.join(tmp, "home-" + name), "CLAUDE_CODE_SESSION_ID": name, "SPECS_PATH": r.path}
            os.makedirs(env["HOME"])
            other_key(r, LB)
            r.git("switch", "-q", "main")
            r.write("private.txt", "my private notes\n")
            r.commit_all("my private notes")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            w2 = worktree_on_main(r, name + "-w2")
            local = main_of(r)
            bare_refs = subprocess.run(["git", "--git-dir", bare, "for-each-ref"], stdout=subprocess.PIPE).stdout
            first = start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            entries = held(r)
            refused = entries[0]["refused"] if len(entries) == 1 else {}
            sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
            clause = lines.fill("reason.land.checked-out", {"<path>": refused.get("path"), "<default>": "main",
                                                            CHECKED: 3})
            want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                 "<reason clause>": clause, "<SPECS_PATH>": r.path, "<sha7>": sha7,
                                                 "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
            check(first.get("stay") == UNKEYED and first.get("default_ref") == "origin/main"
                  and got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and clause.endswith("and origin has no main") and refused.get("permanent") is True
                  and (refused.get("detail") or {}).get("outcome") == "origin-lacks"
                  and os.path.samefile(refused.get("path"), w2.path) and main_of(r) == local
                  and subprocess.run(["git", "--git-dir", bare, "for-each-ref"], stdout=subprocess.PIPE).stdout == bare_refs
                  and read(r, FB) == ENTRY % "mine" and w2.git("status", "--porcelain") == "",
                  "e_land_origin_lacks_checked_out: held stuck, nothing pushed, origin unchanged (%r)" % got)

        def e_land_held_mode_takes():
            """row.held's session-branch tail (checked-out's alternatives 4 and 5, mode_takes): w2 has main checked out,
            and origin refuses the refspec push, which is then recorded -- or a refusal was recorded already, after the
            start -- so the next run, in session-branch mode, drops the hold and commits the files as that mode does."""
            for name, alt in (("e-land-held-refused", 4), ("e-land-held-refused-before", 5)):
                r, env = lworld(name)
                worktree_on_main(r, name + "-w2")
                start_of(env)
                if alt == 4:
                    with open(os.path.join(r.bare, "hooks", "pre-receive"), "w", encoding="utf-8") as fh:
                        fh.write("#!/bin/sh\nwhile read old new ref; do [ \"$ref\" = refs/heads/main ] && exit 1; done\n"
                                 "exit 0\n")
                    os.chmod(os.path.join(r.bare, "hooks", "pre-receive"), 0o755)
                else:
                    path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w", encoding="utf-8") as fh:
                        fh.write("2026-11-01\n")
                old = main_of(r)
                r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                entries = held(r)
                refused = entries[0]["refused"] if len(entries) == 1 else {}
                detail = refused.get("detail") or {}
                v = {"<path>": refused.get("path"), "<default>": "main", CHECKED: alt}
                v.update({"<the refusal>": detail.get("text")} if alt == 4 else
                         {"<date>": detail.get("date"), "<record>": detail.get("record")})
                want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 1,
                                               "<reason clause>": lines.fill("reason.land.checked-out", v)})
                check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                      and detail.get("outcome") == ("refused" if alt == 4 else "refused-before") and detail.get("record")
                      and refused.get("permanent") is False and main_of(r) == old and read(r, FB) == ENTRY % "mine"
                      and want.endswith("and the next run, in session-branch mode, drops this hold and commits them as "
                                        "that mode commits session files"),
                      "e_land_held_mode_takes: alternative %d, the session-branch tail (%r, %r)" % (alt, got, entries))

        def e_land_kill_before_move():
            """A kill in on_move -- the journal written, nothing moved: end --resume lands the change once, then lifts
            it, the held record emptied."""
            r, env = lworld("e-land-kill-before")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            killed = False
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                killed = True
            finally:
                g["land"] = real
            rec = record(env, "/feedback") or {}
            check(killed and main_of(r) == old and read(r, FB) == ENTRY % "mine"
                  and ((rec.get("end_commit") or {}).get("landing") or {}).get("tip") and len(held(r)) == 1,
                  "e_land_kill_before_move: the journal written and saved, nothing moved (%r)" % rec.get("end_commit"))
            got = run_end(env, "/feedback", "--resume")
            tip = main_of(r)
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1), g1_land(r)]
                  and tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB]
                  and on_origin(r) == tip and gone(r, FB) and held(r) == [] and len(reflog_landed(r)) == 1,
                  "e_land_kill_before_move: end --resume lands once, then lifts (%r)" % got)

        def e_land_push_rows():
            """Steps 5-7 for the landing's commit on main: offline (failed), no origin (no-remote), and a local main
            holding the user's own unpushed commit (scope), each followed by app.landed."""
            r, env = lworld("e-land-offline")
            start_of(env)
            missing = r.bare
            os.rename(r.bare, r.bare + ".gone")  # origin unreachable, the Environment: line as it was
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = ("Specs repo: committed %s (1 file) on main — push FAILED (fatal: '%s' does not appear to be a git "
                    "repository); the commit is local and a later run retries it" % (tip[:7], missing))
            check(got.get("row") == "failed" and got.get("print") == [landed(r, 1, row=want), g1_land(r)]
                  and changed(r, tip) == [FB] and gone(r, FB),
                  "e_land_offline: committed on main, push FAILED naming main (%r)" % got)
            r, env = lworld("e-land-no-origin")
            r.git("remote", "remove", "origin")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = "Specs repo: committed %s (1 file) on main — not pushed: this specs repo has no origin remote" % tip[:7]
            check(got.get("row") == "no-remote" and got.get("print") == [landed(r, 1, row=want), g1_land(r)]
                  and changed(r, tip) == [FB] and gone(r, FB),
                  "e_land_no_origin: committed on main, no-remote (%r)" % got)
            r, env = lworld("e-land-scope", notes=False)
            r.git("switch", "-q", "main")
            r.write(PRD, "---\nkind: prd\nkey: ACME-1\n---\n\n# PRD, edited\n")
            mine = r.commit_all("ACME-1 my edit")
            r.git("switch", "-q", LB)
            r.write("notes.md", "n\n")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            tip = main_of(r)
            want = lines.fill("row.scope", {"<sha7>": [tip[:7], mine[:7]], "<N>": 1, "<branch>": "main",
                                            "<subject>": "ACME-1 my edit", "<path>": PRD})
            check(got.get("row") == "scope" and got.get("print") == [landed(r, 1, row=want), g1_land(r)]
                  and r.git("rev-parse", tip + "^") == mine and on_origin(r) != tip,
                  "e_land_scope: the scope row names the user's commit (%r)" % got)

        def e_land_nonff():
            """origin's main moved after the start: the push is rejected and next names the replay of main; following it
            replays the landing's commit onto origin's -- main moved by update-ref, HEAD still on the stayed branch --
            the replayed row ending with app.landed."""
            r, env = lworld("e-land-nonff")
            start_of(env)
            ahead_on_origin(r, "e-land-nonff-other")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            run = (got.get("next") or {}).get("run") or ""
            check(got.get("row") is None and " replay --for end --command /feedback --branch main" in run,
                  "e_land_nonff: next names the replay of main (%r)" % got)
            got = shell(run, env) if run else {}
            tip = main_of(r)
            want = ("Specs repo: committed %s (1 file) on main — pushed after a replay: origin's main had moved on, so "
                    "the run replayed its 1 commit(s) onto it" % tip[:7])
            check(got.get("row") == "replayed" and got.get("print") == [landed(r, 1, row=want), g1_land(r)]
                  and on_origin(r) == tip and changed(r, tip) == [FB] and on_lb(r) and gone(r, FB)
                  and record(env, "/feedback") is None,
                  "e_land_nonff: replayed and pushed, main moved by update-ref, HEAD on the stayed branch (%r)" % got)

        def e_land_declined():
            """A declined path: the landing's row, app.landed, then the declined append last."""
            r, env = lworld("e-land-declined")
            start_of(env)
            ard = "specifications/PRD-ACME-1-x/ard.md"
            r.write(ard, "a\n")
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback", "--declined", ard)
            check(got.get("print") == [landed(r, 1) + "; the deliverable at %s remains uncommitted, as you asked" % ard,
                                       g1_land(r)] and read(r, ard) == "a\n",
                  "e_land_declined: app.landed, then the declined append (%r)" % got)

        def e_land_locked():
            """end --resume of a landing journal with an index.lock standing: Locked, nothing landed or lifted, the
            journal left for a later call."""
            r, env = lworld("e-land-locked")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            real = g["land"]

            def land_killed(*args, **kw):
                inner = kw["on_move"]

                def on_move(pending):
                    inner(pending)
                    raise KeyboardInterrupt
                kw["on_move"] = on_move
                return real(*args, **kw)

            g["land"] = land_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["land"] = real
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback", "--resume")
            finally:
                os.remove(lock)
            entries = held(r)
            check(got.get("row") == "locked" and got.get("print") == [T["row.locked"], g1_land(r, unlanded=True)]
                  and main_of(r) == old and read(r, FB) == ENTRY % "mine" and len(entries) == 1
                  and entries[0].get("tip") and entries[0]["refused"] is None,
                  "e_land_locked: Locked, nothing landed, the journal kept (%r)" % got)
            # and where the move is verified -- a kill during the lift -- nothing is lifted under the lock either
            r, env = lworld("e-land-locked-lift")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            real = g["_lift"]

            def lift_killed(*args, **kw):
                raise KeyboardInterrupt

            g["_lift"] = lift_killed
            try:
                with in_env(env):
                    end(r.path, "/feedback")
            except KeyboardInterrupt:
                pass
            finally:
                g["_lift"] = real
            tip = main_of(r)
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback", "--resume")
            finally:
                os.remove(lock)
            entries = held(r)
            check(got.get("row") == "locked" and got.get("print") == [T["row.locked"], g1_land(r, unlanded=True)]
                  and main_of(r) == tip and read(r, FB) == ENTRY % "mine" and len(entries) == 1
                  and entries[0].get("tip") == tip,
                  "e_land_locked: a verified journal is not lifted under the lock either (%r)" % got)

        def e_land_locked_held():
            """An index.lock at the end of a stayed run: the change held for that cause (row.held with reason.locked), one
            transient held entry, nothing committed or lifted; once the lock is gone, the held stage's primitive lands
            it on main and lifts it."""
            r, env = lworld("e-land-locked-held")
            start_of(env)
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            try:
                got = run_end(env, "/feedback")
            finally:
                os.remove(lock)
            entries = held(r)
            want = lines.fill("row.held", {"<branch>": LB, "<default>": "main", HELD_KIND: 0, HELD_TAIL: 0,
                                           "<reason clause>": lines.fill("reason.locked", {"<path>": ".git/index.lock"})})
            check(got.get("row") == "held" and got.get("print") == [want, g1_land(r, unlanded=True)]
                  and len(entries) == 1 and entries[0]["refused"] == {"reason": "locked", "path": ".git/index.lock",
                                                                      "detail": None, "permanent": False}
                  and list(entries[0]["paths"]) == [FB] and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "e_land_locked_held: held for the lock, one transient entry, nothing committed (%r, %r)"
                  % (got, entries))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got.get("landed") or []) == 1 and changed(r, main_of(r)) == [FB] and gone(r, FB) and held(r) == [],
                  "e_land_locked_held: once the lock is gone, the held stage lands it on main (%r)" % got)

        def e_land_mode():
            """Session-branch mode: a stay is never kept there, and a record holding one is not landed: the mode's own
            commit on session/ab, main unmoved."""
            r, env = lworld("e-land-mode", notes=False)
            r.git("config", "workflows.sessionBranch", "true")
            env = dict(env, GIT_USER_INITIALS="ab")
            seed(env, "/feedback", branch=LB, keys=["ACME-1"], mode="on", session_branch="session/ab", start_dirty={},
                 stay=dict(UNKEYED, reason="stopped"))
            old, up = main_of(r), on_origin(r)
            r.write(FB, ENTRY % "mine")
            got = run_end(env, "/feedback")
            check(got.get("row") == "pushed-session" and got.get("branch") == "session/ab" and main_of(r) == old
                  and on_origin(r) == up and on_lb(r) and "stayed on" not in (got.get("line") or ""),
                  "e_land_mode: the mode's outcome, nothing landed (%r)" % got)

        def e_land_hand_edit():
            """N4: prd/B-2-y's follow-ups.md holds a line main lacks; the user ticks it mid-run and the run appends one
            and writes a feedback file: the feedback file lands, follow-ups.md is held alone (dropped), its working copy
            keeping the tick and the new line, main's unchanged; with follow-ups.md the run's only change, held stuck."""
            for name, also in (("e-land-hand-edit", True), ("e-land-hand-edit-only", False)):
                r, env = lworld(name, notes=False, extra=[(FUP, "- [ ] a\n")])
                r.write(FUP, "- [ ] a\n- [ ] b\n")
                r.commit_all("B-2 a follow-up")
                r.write("notes.md", "n\n")
                start_of(env)
                ticked = "- [ ] a\n- [x] b\n- [ ] n\n"
                r.write(FUP, ticked)
                if also:
                    r.write(FB, ENTRY % "mine")
                got = run_end(env, "/feedback")
                entries = held(r)
                sha7 = entries[0]["c2"][:7] if len(entries) == 1 else "?"
                clause = lines.fill("reason.land.dropped", {"<path>": FUP, "<onto>": "main"})
                if also:
                    stuck = lines.fill("app.held.stuck", {"<path>": [FUP], "<reason clause>": clause, "<SPECS_PATH>": r.path,
                                                          "<sha7>": sha7, "<default>": "main",
                                                          "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
                    ok = (got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + stuck,
                                                                                     g1_land(r, unlanded=True)]
                          and changed(r, main_of(r)) == [FB])
                else:
                    want = lines.fill("row.held-stuck", {"<branch>": LB, "<default>": "main", STUCK_KIND: 0,
                                                         "<reason clause>": clause, "<SPECS_PATH>": r.path, "<sha7>": sha7,
                                                         "<specs-git.py's path>": me, "<default-ref>": "origin/main"})
                    ok = got.get("row") == "held-stuck" and got.get("print") == [want, g1_land(r, unlanded=True)]
                check(ok and read(r, FUP) == ticked and show(r, "main", FUP) == "- [ ] a",
                      "%s: follow-ups.md held alone (dropped), the tick kept, main's unchanged (%r)"
                      % (name.replace("-", "_"), got))

        def e_land_register():
            """C: _push_step's rendering of a landing whose rebuild renumbered a record: the register clause after
            app.landed."""
            r, env = world(tmp, "e-land-register")
            r.write(RESUME, "r\n")
            tip = r.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
            move = {"slug": "acme", "origin": "a1b2c3d", "side": "run", "from": 3, "to": 4}
            rec = {"stay": UNKEYED, "default": "main", "default_ref": "origin/main", "specs": r.path, "reported": [],
                   "mode": "off"}
            commit = {"sha7": tip[:7], "files": 1, "branch": "main", "paths": [RESUME], "hook_paths": [],
                      "landing": {"moves": [move], "stuck": None}}
            run = {"state": state, "lines": lines, "specs": r.path, "session": "e-land-register", "command": "/feedback",
                   "record": "found", "wrote": True, "pre": [], "commit": None}
            with in_env(env):
                got = _push_step(run, rec, commit, "main", {"declined": [], "guard_block": None, "guard_paths": []})
            clause = lines.fill("app.register-clause", {"<slug>": "acme", "<move>": [lines.fill("app.register-move", {
                "<from>": 3, "<to>": 4, "<origin>": "a1b2c3d", "<whose number>": T["app.register-move.run"]})]})
            check(got.get("row") == "pushed-default" and got.get("print") == [landed(r, 1) + "; " + clause],
                  "e_land_register: the register clause after app.landed (%r)" % got)

        def e_land_not_finished():
            """An end that stops early inside the landing: the NOT FINISHED line, then G1's landing form with its
            not-landed Not done (§5); the record kept."""
            r, env = lworld("e-land-not-finished")
            start_of(env)
            r.write(FB, ENTRY % "mine")
            real = g["land"]
            g["land"] = boom
            try:
                with in_env(env):
                    got = end(r.path, "/feedback")
            finally:
                g["land"] = real
            stop = lines.fill("end.stopped", {"<the error>": "RuntimeError: boom"})
            check(got.get("print") == [stop, g1_land(r, unlanded=True)] and record(env, "/feedback") is not None,
                  "e_land_not_finished: NOT FINISHED, then the not-landed form (%r)" % got)

        def e_g1_uncommitted():
            """No stay: the plain block after an end that committed nothing of the run's -- Locked, Commit failed, and the
            NOT FINISHED line -- takes the not-committed form, its Not done and If ignored; after a commit, the plain
            block as it was."""
            uncommitted = T["g1.not_done.uncommitted"]
            for name in ("locked", "commit-failed", "stopped"):
                r, env = world(tmp, "e-g1-uncommitted-" + name)
                r.write("notes.md", "n\n")
                seed(env, "/specify", guard="G1", guard_block=g1_plain(r), guard_paths=["notes.md"])
                r.write(RESUME, "r\n")
                lock = os.path.join(r.path, ".git", "index.lock")
                if name == "locked":
                    open(lock, "w").close()
                    try:
                        got = run_end(env, "/specify")
                    finally:
                        os.remove(lock)
                    row = T["row.locked"]
                elif name == "commit-failed":
                    hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
                    got = run_end(env, "/specify")
                    row = lines.fill("row.commit-failed", {"<the first line of git's error or the hook's output>":
                                                           "hook says no"})
                else:
                    real = g["commit_session_files"]

                    def write_then_boom(root, message, on_write=None, on_staged=None):
                        on_write()
                        raise RuntimeError("boom")

                    g["commit_session_files"] = write_then_boom
                    try:
                        with in_env(env):
                            got = end(r.path, "/specify")
                    finally:
                        g["commit_session_files"] = real
                    row = lines.fill("end.stopped", {"<the error>": "RuntimeError: boom"})
                shown = (got.get("print") or ["", ""])
                check(shown == [row, g1_form(r, uncommitted, T["g1.if_ignored.uncommitted"])]
                      and "WILL still be committed" not in shown[-1] and "committed alongside" not in shown[-1],
                      "e_g1_uncommitted: after %s, the not-committed Not done (%r)" % (name, got))

        for name, fn in (("e_land_g1", e_land_g1), ("e_land_refused", e_land_refused),
                         ("e_land_unlisted", e_land_unlisted), ("e_land_stopped", e_land_stopped),
                         ("e_land_budget", e_land_budget), ("e_land_legacy", e_land_legacy),
                         ("e_land_merged", e_land_merged), ("e_land_leftover_kept", e_land_leftover_kept),
                         ("e_land_leftover_shared", e_land_leftover_shared), ("e_land_commit_key", e_land_commit_key),
                         ("e_land_moved", e_land_moved), ("e_land_checked_out_pushed", e_land_checked_out_pushed),
                         ("e_land_held", e_land_held), ("e_land_checked_out_no_origin", e_land_checked_out_no_origin),
                         ("e_land_stuck", e_land_stuck), ("e_land_partial", e_land_partial),
                         ("e_land_there", e_land_there), ("e_land_kill", e_land_kill),
                         ("e_land_kill_resumed", e_land_kill_resumed),
                         ("e_land_kill_register", e_land_kill_register),
                         ("e_land_kill_before_move", e_land_kill_before_move),
                         ("e_land_unsupported", e_land_unsupported), ("e_land_resume_moved", e_land_resume_moved),
                         ("e_land_held_mode_takes", e_land_held_mode_takes),
                         ("e_land_origin_lacks_checked_out", e_land_origin_lacks_checked_out),
                         ("e_land_origin_lacks_default", e_land_origin_lacks_default), ("e_land_push_rows", e_land_push_rows),
                         ("e_land_nonff", e_land_nonff), ("e_land_declined", e_land_declined),
                         ("e_land_locked", e_land_locked), ("e_land_locked_held", e_land_locked_held),
                         ("e_land_mode", e_land_mode), ("e_land_hand_edit", e_land_hand_edit),
                         ("e_land_register", e_land_register), ("e_land_not_finished", e_land_not_finished),
                         ("e_g1_uncommitted", e_g1_uncommitted)):
            case(name, fn)

    def scenarios_land(tmp):
        """specs-repo-git §4 step 1's landing: land, the held record, retry_held, and the land and snapshot subcommands.
        In process where a fault is injected, else as the CLI runs."""
        LB = "prd/B-2-y"
        FUP = "specifications/PRD-ACME-1-x/follow-ups.md"
        FB = "specifications/PRD-ACME-1-x/dev-workflows/feedback/f.md"
        FB2 = "specifications/PRD-ACME-1-x/dev-workflows/feedback/g.md"
        COST = "specifications/PRD-ACME-1-x/dev-workflows/cost/abcd1234.md"
        COST_BODY = "# Cost\n\n## 2026-11-10T10:00:00Z — /specify — draft\n\nbody\n"
        EDITED = COST_BODY.replace("body", "edited")
        ENTRY = "## 2026-11-10 — /feedback — note\n\n%s\n"
        HELD = "refs/workflows/held/"
        MSG = session_subject(None, "/feedback")
        PENDING = {"c1", "c2", "old", "tip", "onto", "paths", "remote_only", "here", "index_before", "moves"}
        CLI_FIELDS = {"status", "sha7", "files", "paths", "lifted", "default", "pushed", "reason", "detail", "path", "permanent",
                      "stuck", "error"}

        def case(name, fn):
            try:
                fn()
            except Exception as e:  # one case that crashes must not hide the others
                check(False, "%s crashed: %s: %s" % (name, type(e).__name__, str(e).strip()[:400]))

        def no_origin(r):
            r.git("remote", "remove", "origin")

        def lworld(name, follow="- [ ] a\n", extra=(), stay=True):
            """world, with follow-ups.md and <extra> ((path, body) pairs) committed on main and pushed; then, where
            <stay>, other_key."""
            r, r.env = world(tmp, name)
            r.write(FUP, follow)
            for p, body in extra:
                r.write(p, body)
            r.commit_all("ACME-1 Add the follow-ups")
            r.git("push", "-q", "origin", "main")
            if stay:
                other_key(r)
            return r

        def ref(r, name):
            return r.git("rev-parse", "--verify", "-q", name, check=False) or None

        def main_of(r):
            return ref(r, "refs/heads/main")

        def held(r):
            return held_entries(r.path)

        def held_refs(r):
            return r.git("for-each-ref", "--format=%(refname)", HELD).split()

        def show(r, rev, path):
            return r.git("show", "%s:%s" % (rev, path), check=False)

        def changed(r, rev):
            return sorted(x for x in r.git("diff-tree", "--no-commit-id", "--name-only", "-r", rev).split("\n") if x)

        def porcelain(r):
            return r.git("status", "--porcelain", "--untracked-files=all")

        def read(r, path):
            full = os.path.join(r.path, path)
            if not os.path.isfile(full):
                return None
            with open(full, encoding="utf-8", newline="") as fh:
                return fh.read()

        def do_land(r, branch=LB, snap=None, default_ref="origin/main", **kw):
            return land(r.path, branch, "main", default_ref, MSG, snap, **kw)

        def worktree(r, name, branch="main"):
            path = os.path.join(tmp, name)
            r.git("worktree", "add", "-q", path, branch)
            return Repo(path)

        def same_path(a, b):
            return a is not None and b is not None and os.path.realpath(a) == os.path.realpath(b)

        @contextlib.contextmanager
        def patched(name, fake):
            real = getattr(sb, name)
            setattr(sb, name, fake)
            try:
                yield real
            finally:
                setattr(sb, name, real)

        def locked_move(calls=None):
            """move_branch answering locked, as a lock left by a git that died would make it: a transient cause."""
            def fake(*_args, **_kw):
                if calls is not None:
                    calls.append(1)
                return {"reason": "locked", "path": ".git/refs/heads/main.lock"}
            return fake

        def kill(_pending):
            raise OSError("killed")

        def stopped(fn):
            try:
                fn()
            except LandStopped as e:
                return e
            return None

        def l_land_unkeyed():
            r = lworld("l-unkeyed")
            old, br, hd = main_of(r), ref(r, "refs/heads/" + LB), ref(r, "HEAD")
            r.write(FB, ENTRY % "mine")
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            got = do_land(r)
            tip = main_of(r)
            check(got["status"] == "landed" and got["sha"] == tip and got["files"] == 2 and got["paths"] == [FB, FUP]
                  and got["pushed"] is False and got["onto"] == "main" and got["refused"] is None and got["stuck"] is None
                  and got["held_landed"] == [] and got["moves"] == [],
                  "l_land_unkeyed: landed on main (%r)" % got)
            check(tip != old and r.git("rev-parse", tip + "^") == old and changed(r, tip) == [FB, FUP]
                  and show(r, tip, FUP) == "- [ ] a\n- [ ] b"
                  and r.git("reflog", "-1", "--format=%gs", "refs/heads/main") == "specs-git: landed " + tip[:7],
                  "l_land_unkeyed: one commit on the old main naming exactly the two paths, its reflog the landing's")
            check(ref(r, "refs/heads/" + LB) == br and ref(r, "HEAD") == hd and r.git("symbolic-ref", "--short", "HEAD") == LB,
                  "l_land_unkeyed: the stayed branch and HEAD unmoved")
            check(porcelain(r) == "" and sorted(got["lifted"]) == [FB, FUP],
                  "l_land_unkeyed: both paths lifted, the checkout clean (%r, %r)" % (porcelain(r), got["lifted"]))
            check(held(r) == [] and held_refs(r) == [], "l_land_unkeyed: no journal entry left")

        def l_land_snapshot():
            r = lworld("l-snapshot")
            r.write(FUP, "- [ ] a\n- [ ] s\n")  # S: another run's line, dirty when this run started
            snap = snapshot(r.path)
            check(snap == {FUP: r.git("hash-object", FUP)}, "l_land_snapshot: the snapshot names S's blob (%r)" % snap)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] mine\n")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] mine"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n" and got["lifted"] == [FUP],
                  "l_land_snapshot: main's commit adds only the run's line, the working copy S after the lift (%r, %r)"
                  % (got, show(r, main_of(r), FUP)))

        def l_land_snapshot_deleted():
            r = lworld("l-snapshot-deleted", extra=[(RESUME, "r\n")])
            os.remove(os.path.join(r.path, RESUME))
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "mine")
            got = do_land(r, snap=snap)
            tip = main_of(r)
            check(snap == {RESUME: None} and got["status"] == "landed" and changed(r, tip) == [FB]
                  and show(r, tip, RESUME) == "r" and read(r, RESUME) is None and read(r, FB) is None,
                  "l_land_snapshot_deleted: a deletion standing at the start is not the run's: it neither lands nor is "
                  "put back (%r, %r)" % (snap, got))

        def l_land_no_snapshot():
            r = lworld("l-no-snapshot")
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            tip = main_of(r)
            check(got["status"] == "landed" and changed(r, tip) == [FB, FUP] and show(r, tip, FUP) == "- [ ] a\n- [ ] s"
                  and porcelain(r) == "",
                  "l_land_no_snapshot: with no snapshot every dirty session file lands, the leftover included (%r)" % got)

        def l_land_behind():
            r = lworld("l-behind")
            o = clone(r, "l-behind-other")
            o.write("specifications/PRD-ACME-1-x/notes.md", "n\n")
            o.commit_all("ACME-1 Add notes")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            local, up = main_of(r), ref(r, "refs/remotes/origin/main")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            tip = main_of(r)
            check(local != up and got["status"] == "landed" and got["sha"] == tip and r.git("rev-parse", tip + "^") == up
                  and got["pushed"] is False,
                  "l_land_behind: built on origin/main, local main fast-forwarded to it (%r)" % got)

        def l_land_absent():
            r = lworld("l-absent")
            r.git("branch", "-q", "-D", "main")
            up = ref(r, "refs/remotes/origin/main")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and main_of(r) == got["sha"] and r.git("rev-parse", got["sha"] + "^") == up,
                  "l_land_absent: no local main: created at the landed commit, on origin/main (%r)" % got)

        def l_land_behind_checked_out():
            r = lworld("l-behind-co")
            o = clone(r, "l-behind-co-other")
            o.write("specifications/PRD-ACME-1-x/notes.md", "n\n")
            o.commit_all("ACME-1 Add notes")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            w2 = worktree(r, "l-behind-co-w2")
            local, up = main_of(r), ref(r, "refs/remotes/origin/main")
            check(w2.git("status", "--porcelain") == "" and w2.git("diff", "--cached") == "",
                  "l_land_behind_checked_out: w2 clean before")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and got["pushed"] is True and on_origin(r) == got["sha"]
                  and r.git("rev-parse", got["sha"] + "^") == up and main_of(r) == local and local != up,
                  "l_land_behind_checked_out: pushed by refspec on origin/main, local main unmoved (%r)" % got)
            check(w2.git("status", "--porcelain") == "" and w2.git("diff", "--cached") == "" and porcelain(r) == ""
                  and held(r) == [] and held_refs(r) == [],
                  "l_land_behind_checked_out: w2 as it was, no staged reversal (%r, %r)"
                  % (w2.git("status", "--porcelain"), w2.git("diff", "--cached")))

        def l_land_checked_out_no_push():
            def refused_before(r):
                path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                os.makedirs(os.path.dirname(path))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("2026-11-01\n")
            for name, setup, ref_name, detail, permanent in (
                    ("l-co-no-remote", no_origin, "refs/heads/main", "no-remote", True),
                    ("l-co-offline", lambda r: r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git")),
                     "origin/main", "failed", False),
                    ("l-co-refused", refused_before, "origin/main", "refused-before", False)):
                r = lworld(name)
                w2 = worktree(r, name + "-w2")
                setup(r)
                local, up = main_of(r), on_origin(r)
                r.write(FB, ENTRY % "mine")
                got = do_land(r, default_ref=ref_name)
                entries = held(r)
                refused = got.get("refused") or {}
                check(got["status"] == "held" and refused.get("reason") == "checked-out"
                      and (refused.get("detail") or {}).get("outcome") == detail
                      and refused.get("permanent") is permanent and same_path(refused.get("path"), w2.path)
                      and got["pushed"] is False and main_of(r) == local and on_origin(r) == up
                      and "?? " + FB in porcelain(r) and len(entries) == 1 and entries[0]["refused"] == refused
                      and entries[0]["tip"] is None and held_refs(r) == [HELD + entries[0]["c2"]] and got["sha"] == entries[0]["c2"],
                      "l_land_checked_out_no_push: %s held, %s, local main unmoved, the file dirty (%r, %r)"
                      % (name, detail, got, entries))

        def l_land_diverged():
            r = lworld("l-diverged")
            r.git("switch", "-q", "main")
            r.write("notes.md", "the user's\n")
            user = r.commit_all("the user's own commit")
            r.git("switch", "-q", LB)
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and r.git("rev-parse", got["sha"] + "^") == user and main_of(r) == got["sha"],
                  "l_land_diverged: landed on top of the user's unpushed commit (%r)" % got)

        def l_land_nothing():
            r = lworld("l-nothing")
            old = main_of(r)
            got = do_land(r)
            check(got["status"] == "nothing" and got["sha"] is None and main_of(r) == old and held(r) == [],
                  "l_land_nothing: nothing dirty, nothing landed (%r)" % got)

        def main_gains(r, body):
            r.git("switch", "-q", "main")
            r.write(FUP, body)
            r.commit_all("ACME-1 follow-ups on main")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", LB)

        def l_land_there():
            r = lworld("l-there")
            main_gains(r, "- [ ] a\n- [ ] b\n")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            got = do_land(r)
            check(got["status"] == "there" and got["sha"] is None and main_of(r) == old and got["lifted"] == [FUP]
                  and porcelain(r) == "" and held(r) == [],
                  "l_land_there: the run's line already on main: no commit, the file lifted (%r)" % got)

        def l_land_there_refused():
            r = lworld("l-there-refused", extra=[(COST, COST_BODY)])
            main_gains(r, "- [ ] a\n- [ ] b\n")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            r.write(COST, EDITED)
            got = do_land(r)
            entries = held(r)
            stuck = got.get("stuck") or {}
            check(got["status"] == "held" and main_of(r) == old and got["lifted"] == [FUP] and read(r, FUP) == "- [ ] a\n"
                  and read(r, COST) == EDITED and stuck.get("paths") == [COST] and got["refused"] == stuck.get("refused")
                  and (got["refused"] or {}).get("reason") == "edited" and (got["refused"] or {}).get("permanent") is True
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST],
                  "l_land_there_refused: no commit, the path already there lifted, the other held, permanent (%r, %r)"
                  % (got, entries))

        def l_land_hook():
            r = lworld("l-hook")
            hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "exit 1\n")
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            check(got["status"] == "landed" and main_of(r) == got["sha"], "l_land_hook: no pre-commit hook runs (%r)" % got)

        def l_land_on_move():
            r = lworld("l-on-move")
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            seen = []

            def on_move(pending):
                seen.append((dict(pending), main_of(r), [dict(e) for e in held(r)]))
            got = do_land(r, on_move=on_move)
            p, at, entries = seen[0] if seen else ({}, None, [])
            check(len(seen) == 1 and set(p) == PENDING and at == old and p.get("old") == old and p.get("tip") == got["sha"]
                  and p.get("here") is False and p.get("remote_only") is False and p.get("onto") == "main"
                  and p.get("moves") == [] and len(entries) == 1 and entries[0]["refused"] is None and entries[0]["tip"] == got["sha"]
                  and entries[0]["c2"] == p.get("c2") and held(r) == [] and held_refs(r) == [],
                  "l_land_on_move: called before the move, the journal entry written; none left after (%r)" % (seen,))

        def l_land_partial():
            r = lworld("l-partial", extra=[(COST, COST_BODY)])
            r.write(COST, EDITED)
            r.write(FB, ENTRY % "mine")
            got = do_land(r)
            entries = held(r)
            stuck = got.get("stuck") or {}
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and stuck.get("paths") == [COST]
                  and (stuck.get("refused") or {}).get("reason") == "edited"
                  and (stuck.get("refused") or {}).get("permanent") is True
                  and len(entries) == 1 and list(entries[0]["paths"]) == [COST] and entries[0]["c2"] == stuck.get("sha")
                  and entries[0]["refused"] == stuck.get("refused")
                  and changed(r, entries[0]["c2"]) == [COST] and r.git("rev-parse", entries[0]["c2"] + "^") == entries[0]["c1"]
                  and read(r, COST) == EDITED and read(r, FB) is None and got["lifted"] == [FB],
                  "l_land_partial: the feedback file lands, the cost file held alone, permanent, unlifted (%r, %r)"
                  % (got, entries))
            r = lworld("l-partial-alone", extra=[(COST, COST_BODY)])
            old = main_of(r)
            r.write(COST, EDITED)
            got = do_land(r)
            check(got["status"] == "held" and (got["refused"] or {}).get("permanent") is True and main_of(r) == old
                  and len(held(r)) == 1 and read(r, COST) == EDITED,
                  "l_land_partial: the cost file alone is held, permanent (%r)" % got)

        def l_land_locked():
            r = lworld("l-locked")
            r.write(FB, ENTRY % "mine")
            lock = os.path.join(r.path, ".git", "index.lock")
            open(lock, "w").close()
            refs = r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes")
            try:
                got = do_land(r)
            finally:
                os.remove(lock)
            entries = held(r)
            refused = got["refused"] or {}
            check(got["status"] == "held" and refused == {"reason": "locked", "path": ".git/index.lock", "detail": None,
                                                           "permanent": False}
                  and r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads", "refs/remotes") == refs
                  and len(entries) == 1 and entries[0]["refused"] == refused and entries[0]["c2"] == got["sha"]
                  and entries[0]["tip"] is None and list(entries[0]["paths"]) == [FB]
                  and held_refs(r) == [HELD + got["sha"]] and got["lifted"] == [] and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: an index.lock at the landing's start holds the change for that cause, transient: "
                  "no branch moved, nothing lifted (%r)" % got)
            # the here form (HEAD on main) holds nothing: locked, nothing moved (specs-repo-git §4 step 1)
            r = lworld("l-locked-here", stay=False)
            r.write(FB, ENTRY % "mine")
            open(lock.replace("l-locked", "l-locked-here"), "w").close()
            try:
                got = do_land(r, branch="main")
            finally:
                os.remove(lock.replace("l-locked", "l-locked-here"))
            check(got["status"] == "locked" and (got["refused"] or {}).get("reason") == "locked" and held(r) == []
                  and held_refs(r) == [] and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: in the here form, locked, nothing held (%r)" % got)
            # a resumed journal (end --resume) is left as it stands for a later call: locked, nothing moved or held anew
            r = lworld("l-locked-resume")
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            before, old = held(r), main_of(r)
            path = os.path.join(r.path, ".git", "index.lock")
            open(path, "w").close()
            try:
                got = do_land(r, resume=e.pending) if e and e.pending else {}
            finally:
                os.remove(path)
            check(got.get("status") == "locked" and held(r) == before and len(before) == 1 and before[0]["tip"]
                  and before[0]["refused"] is None and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "l_land_locked: a resumed journal under the lock is left for a later call (%r)" % got)

        def l_land_resume_on_default():
            """A landing's journal is never finished by the here form: resumed with HEAD on <default>, land refuses
            before any write, the journal and main as they were."""
            r = lworld("l-resume-on-default")
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            before, old = held(r), main_of(r)
            r.git("switch", "-q", "main")
            try:
                do_land(r, branch="main", resume=e.pending if e else None)
                said = None
            except NotRun as x:
                said = str(x)
            check(said and "is not finished with HEAD on main" in said and held(r) == before and len(before) == 1
                  and main_of(r) == old and read(r, FB) == ENTRY % "mine",
                  "l_land_resume_on_default: refused, nothing done (%r)" % said)

        def l_land_old_git():
            fake = os.path.join(tmp, "l-old-git-bin")
            os.makedirs(fake)
            with open(os.path.join(fake, "git"), "w") as fh:
                fh.write('#!/bin/sh\nfor x in "$@"; do\n  if [ "$x" = merge-tree ]; then\n    cat <<\'EOF\'\n'
                         "usage: git merge-tree [--write-tree] [<options>] <branch1> <branch2>\n\n"
                         "    --write-tree          do a real merge instead of a trivial merge\n"
                         "    -X, --strategy-option <option=value>\nEOF\n    exit 129\n  fi\ndone\n"
                         "exec %s \"$@\"\n" % shlex.quote(shutil.which("git")))
            os.chmod(os.path.join(fake, "git"), 0o755)
            plain = lworld("l-old-git-plain")
            plain.write(FB, ENTRY % "mine")
            plain.write(FUP, "- [ ] a\n- [ ] b\n")
            want = do_land(plain)
            r = lworld("l-old-git")
            r.write(FB, ENTRY % "mine")
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            with in_env({"PATH": fake + os.pathsep + os.environ.get("PATH", "")}):
                shim = sb.replay_ok(r.path)
                got = do_land(r)
            check(shim is False and got["status"] == want["status"] == "landed" and got["paths"] == want["paths"]
                  and r.git("rev-parse", got["sha"] + "^{tree}") == plain.git("rev-parse", want["sha"] + "^{tree}")
                  and porcelain(r) == "",
                  "l_land_old_git: under a git without merge-tree --merge-base, the same landing (%r, %r, %r)"
                  % (shim, got, want))

        def l_land_moved():
            for n, status in ((2, "held"), (1, "landed")):
                r = lworld("l-moved-%d" % n)
                old = main_of(r)
                r.write(FB, ENTRY % "mine")
                calls = []
                real = sb.move_branch

                def fake(*args, **kw):
                    calls.append(1)
                    return {"reason": "branch-moved", "path": None} if len(calls) <= n else real(*args, **kw)
                with patched("move_branch", fake):
                    got = do_land(r)
                if n == 2:
                    entries = held(r)
                    check(got["status"] == "held" and got["refused"] == {"reason": "moved", "path": None,
                                                                         "detail": "branch-moved", "permanent": False}
                          and len(calls) == 2 and main_of(r) == old and len(entries) == 1
                          and entries[0]["refused"] == got["refused"] and read(r, FB) == ENTRY % "mine",
                          "l_land_moved: refused twice, held, moved, transient (%r)" % got)
                else:
                    check(got["status"] == "landed" and len(calls) == 2 and main_of(r) == got["sha"] and held(r) == [],
                          "l_land_moved: refused once, landed on the second try (%r)" % got)

        def l_held_chain():
            r = lworld("l-held-chain")
            w2 = worktree(r, "l-held-chain-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            first = do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            second = do_land(r, snap=snap)
            entries = held(r)
            check(first["status"] == "held" and ((first["refused"] or {}).get("detail") or {}).get("outcome") == "failed"
                  and second["status"] == "held" and len(entries) == 2 and second["refused"] == entries[0]["refused"]
                  and snap == {FUP: entries[0]["paths"][FUP]} and entries[1]["c2"] == second["sha"],
                  "l_held_chain: the second landing held behind the first (%r, %r, %r)" % (first, second, entries))
            r.git("worktree", "remove", "--force", w2.path)
            r.git("remote", "set-url", "origin", r.bare)
            got = retry_held(r.path, "main", "origin/main")
            check(show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2" and len(got["landed"]) == 2
                  and [x["branch"] for x in got["landed"]] == [LB, LB] and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [] and held_refs(r) == [],
                  "l_held_chain: both landed in order, each line once, the working copy HEAD's (%r, %r)"
                  % (got, show(r, main_of(r), FUP)))

        def l_held_unrelated():
            r = lworld("l-held-unrelated", extra=[(COST, COST_BODY)])
            r.write(COST, EDITED)
            got = do_land(r)
            check(got["status"] == "held" and got["refused"]["permanent"] is True, "l_held_unrelated: a permanent entry")
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "b")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and len(held(r)) == 1,
                  "l_held_unrelated: a permanent entry on A holds back no landing on B (%r)" % got)
            r = lworld("l-held-unrelated-2")
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            with patched("move_branch", locked_move()):
                got = do_land(r)
            check(got["status"] == "held" and got["refused"] == {"reason": "locked", "path": ".git/refs/heads/main.lock",
                                                                 "detail": None, "permanent": False},
                  "l_held_unrelated: a transient entry (%r)" % got)
            snap = snapshot(r.path)
            r.write(FB, ENTRY % "b")
            got = do_land(r, snap=snap)
            check(got["status"] == "landed" and changed(r, main_of(r)) == [FB] and len(held(r)) == 1
                  and got["held_landed"] == [],
                  "l_held_unrelated: a transient entry on A holds back no landing on B (%r)" % got)
            old = main_of(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] x\n- [ ] y\n")
            calls = []
            with patched("move_branch", locked_move(calls)):
                got = do_land(r, snap=snap)
            entries = held(r)
            check(got["status"] == "held" and got["refused"] == entries[0]["refused"] and len(calls) == 1
                  and main_of(r) == old and len(entries) == 2 and entries[1]["c2"] == got["sha"],
                  "l_held_unrelated: a transient entry on A holds a landing on A behind it, unattempted (%r, %r)"
                  % (got, calls))

        def l_held_then_own():
            r = lworld("l-held-then-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            entry = held(r)[0]
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap)
            check(snap == {FUP: entry["paths"][FUP]} and got["status"] == "landed" and len(got["held_landed"]) == 1
                  and got["held_landed"][0]["branch"] == LB and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2"
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == [] and held_refs(r) == [],
                  "l_held_then_own: the held entry lands first, then the run's own, the file lifted to the entry's c1 "
                  "(%r, %r)" % (got, read(r, FUP)))

        def l_held_then_own_there():
            # as l_held_then_own, but main already holds the run's own line: the own change is there, never journalled,
            # so no carry reaches it, and only the walk-back through the held entry lifts the file to HEAD's version
            r = lworld("l-held-then-own-there")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            o = clone(r, "l-held-then-own-there-other")
            o.write(FUP, "- [ ] a\n- [ ] l2\n")
            o.commit_all("ACME-1 l2")
            o.git("push", "-q", "origin", "main")
            r.git("fetch", "-q", "origin")
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap)
            check(got["status"] == "there" and len(got["held_landed"]) == 1 and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [],
                  "l_held_then_own_there: the entry lands, the own change is there, the file lifted to HEAD's (%r, %r)"
                  % (got, read(r, FUP)))

        def l_retry_local_only():
            r = lworld("l-retry-local")
            worktree(r, "l-retry-local-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            r.git("remote", "set-url", "origin", r.bare)
            up = on_origin(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            got = do_land(r, snap=snap, retry_remote=False)
            check(got["status"] == "held" and on_origin(r) == up and len(held(r)) == 2 and got["held_landed"] == [],
                  "l_retry_local_only: retry_remote=False leaves the entry, the own change held behind it (%r)" % got)
            got = do_land(r, snap=snap)
            o = subprocess.run(["git", "-C", r.bare, "show", "main:" + FUP], stdout=subprocess.PIPE).stdout.decode()
            # the run's own change is the second entry's: it lands as that entry, the own change then there, or -- both
            # commits made in one second, so one c2 -- as the own change itself
            check(got["held_landed"] and got["held_landed"][0]["branch"] == LB and o == "- [ ] a\n- [ ] l1\n- [ ] l2\n"
                  and got["status"] in ("there", "landed") and held(r) == [] and held_refs(r) == []
                  and read(r, FUP) == "- [ ] a\n",
                  "l_retry_local_only: with the default the entries are pushed by refspec (%r, %r)" % (got, o))

        def l_retry_budget():
            r = lworld("l-retry-budget")
            worktree(r, "l-retry-budget-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FB, ENTRY % "one")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FB2, ENTRY % "two")
            do_land(r, snap=snap)
            r.git("remote", "set-url", "origin", r.bare)
            calls = []

            def budget(cost):
                calls.append(cost)
                if len(calls) == 2:
                    raise _Stop()
            raised = False
            try:
                retry_held(r.path, "main", "origin/main", check=budget)
            except _Stop:
                raised = True
            entries = held(r)
            tip = on_origin(r)
            check(raised and calls == [PUSH_COST, PUSH_COST] and len(entries) == 1 and list(entries[0]["paths"]) == [FB2]
                  and show(r, tip, FB) != "" and show(r, tip, FB2) == "" and read(r, FB) is None
                  and read(r, FB2) == ENTRY % "two",
                  "l_retry_budget: the first landed, the second kept, _Stop propagated (%r, %r, %r)" % (raised, calls, entries))

        def first_move_only(calls):
            """move_branch real for its first call, locked after it: the held entry lands, the run's own stays held."""
            real = sb.move_branch

            def fake(*args, **kw):
                calls.append(1)
                return real(*args, **kw) if len(calls) == 1 else locked_move()(*args, **kw)
            return fake

        def stopped_chain(name):
            """E1 and E2 held, chained on follow-ups.md (E2 started from E1's version); a _Stop lands E1 alone."""
            r = lworld(name)
            worktree(r, name + "-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            do_land(r, snap=snap)
            second = held(r)[1]
            r.git("remote", "set-url", "origin", r.bare)
            calls = []

            def budget(cost):
                calls.append(cost)
                if len(calls) == 2:
                    raise _Stop()
            try:
                retry_held(r.path, "main", "origin/main", check=budget)
            except _Stop:
                pass
            return r, second

        def l_chain_partly_stopped():
            r, second = stopped_chain("l-chain-stopped")
            left = held(r)
            check(len(left) == 1 and left[0]["c2"] == second["c2"]
                  and left[0].get("lift") == {FUP: r.git("rev-parse", "HEAD:" + FUP)}
                  and read(r, FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2\n",
                  "l_chain_partly_stopped: E1 landed, E2 kept with its lift where the chain began (%r)" % left)
            got = retry_held(r.path, "main", "origin/main")
            o = subprocess.run(["git", "-C", r.bare, "show", "main:" + FUP], stdout=subprocess.PIPE).stdout.decode()
            check(len(got["landed"]) == 1 and o == "- [ ] a\n- [ ] l1\n- [ ] l2\n" and read(r, FUP) == "- [ ] a\n"
                  and porcelain(r) == "" and held(r) == [],
                  "l_chain_partly_stopped: E2 lands later, the working copy back where the chain began, no E1 line "
                  "(%r, %r)" % (got, read(r, FUP)))

        def l_chain_lift_pruned():
            # an override whose blob git no longer holds (an entry held past gc's pruning): the lift falls back to c1
            r, second = stopped_chain("l-chain-pruned")
            missing = "0" * 39 + "1"
            g["_held_put"](r.path, dict(held(r)[0], lift={FUP: missing}))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["landed"]) == 1 and read(r, FUP) == "- [ ] a\n- [ ] l1\n" and held(r) == []
                  and got["landed"][0]["lifted"] == [{"path": FUP, "blob": r.git("rev-parse", second["c1"] + ":" + FUP)}],
                  "l_chain_lift_pruned: a missing override blob falls back to the entry's c1 (%r)" % got)

        def l_chain_partly_own():
            # E1 lands in land's step 3; the run's own change, started from E1's version, then stays held
            r = lworld("l-chain-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            calls = []
            with patched("move_branch", first_move_only(calls)):
                got = do_land(r, snap=snap)
            left = held(r)
            check(len(got["held_landed"]) == 1 and got["status"] == "held" and len(calls) == 2 and len(left) == 1
                  and left[0]["c2"] == got["sha"] and left[0].get("lift") == {FUP: r.git("rev-parse", "HEAD:" + FUP)}
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1",
                  "l_chain_partly_own: E1 landed, the own change held with its lift where the chain began (%r, %r)"
                  % (got, left))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["landed"]) == 1 and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l1\n- [ ] l2"
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == [],
                  "l_chain_partly_own: it lands later, the working copy back where the chain began, no E1 line (%r, %r)"
                  % (got, read(r, FUP)))

        def l_chain_delete_behind_whole():
            # a deletion chained behind a whole-file edit: E1 resume.md v0 -> v1 lands, E2 v1 -> absent stays held
            r = lworld("l-chain-delete", extra=[(RESUME, "v0\n")])
            r.write(RESUME, "v1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            os.remove(os.path.join(r.path, RESUME))
            calls = []
            with patched("move_branch", first_move_only(calls)):
                got = do_land(r, snap=snap)
            left = held(r)
            check(got["status"] == "held" and len(left) == 1 and show(r, main_of(r), RESUME) == "v1"
                  and left[0].get("lift") == {RESUME: r.git("rev-parse", "HEAD:" + RESUME)},
                  "l_chain_delete_behind_whole: E1 landed, the deletion held with its lift at v0 (%r, %r)" % (got, left))
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["landed"]) == 1 and got["stuck"] == [] and show(r, main_of(r), RESUME) == ""
                  and read(r, RESUME) == "v0\n" and porcelain(r) == "" and held(r) == [],
                  "l_chain_delete_behind_whole: the deletion lands, the working copy back at v0 (%r, %r)"
                  % (got, read(r, RESUME)))

        def l_cli_detail():
            r = lworld("l-cli-detail")
            worktree(r, "l-cli-detail-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FB, ENTRY % "mine")
            got = cli("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback",
                      env=r.env)
            detail = got.get("detail") or {}
            check(got["_rc"] == 0 and got.get("status") == "held" and got.get("reason") == "checked-out"
                  and isinstance(detail, dict) and set(detail) == set(CHECKED_OUT_DETAIL)
                  and detail["outcome"] == "failed" and "nowhere.git" in (detail["text"] or "")
                  and got.get("permanent") is False,
                  "l_cli_detail: a checked-out hold prints its detail whole: the refspec push's outcome and reason (%r)"
                  % got)

        def l_checked_out_detail():
            """Each alternative of reason.land.checked-out, worded from a real refusal of the landing's remote path:
            the detail the held record keeps, mapped by checked_out_values, filled whole."""
            _, lines = _flow()
            nowhere = os.path.join(tmp, "nowhere.git")

            def moved_on(r):  # another clone pushes to origin's main; this clone does not fetch it
                other = r.path + "-other"
                subprocess.run(["git", "clone", "-q", r.bare, other], check=True)
                o = Repo(other)
                o.git("config", "user.email", "t@example.invalid")
                o.git("config", "user.name", "t")
                o.git("config", "commit.gpgsign", "false")
                o.git("switch", "-q", "main")
                o.write("notes.md", "a teammate's\n")
                o.commit_all("a teammate's commit")
                o.git("push", "-q", "origin", "main")

            def refused_before(r):
                path = os.path.join(r.path, ".git", "workflows", "push-refused", "main")
                os.makedirs(os.path.dirname(path))
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write("2026-11-01\n")

            def record_of(r):
                return os.path.join(r.path, ".git", "workflows", "push-refused", "main")

            cases = (
                ("l-cod-failed", lambda r: r.git("remote", "set-url", "origin", nowhere), "origin/main",
                 lambda r, d: d["outcome"] == "failed" and d["text"].startswith("fatal:") and "nowhere.git" in d["text"]
                 and d["remote"] is None and d["record"] is None and d["date"] is None,
                 lambda r, d: "and the push of the commit by refspec failed (%s)" % d["text"]),
                ("l-cod-rejected", moved_on, "origin/main",
                 lambda r, d: d["outcome"] == "rejected" and d["text"].startswith("[rejected]"),
                 lambda r, d: "and the push of the commit by refspec failed (%s)" % d["text"]),
                ("l-cod-no-remote", no_origin, "refs/heads/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="no-remote"),
                 lambda r, d: "and there is no origin to push the commit to"),
                ("l-cod-elsewhere", lambda r: r.git("config", "remote.pushDefault", "fork"), "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="elsewhere", remote="fork"),
                 lambda r, d: "and your git configuration pushes main to fork, not to origin"),
                ("l-cod-remote-deleted",
                 lambda r: subprocess.run(["git", "-C", r.bare, "update-ref", "-d", "refs/heads/main"], check=True),
                 "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="remote-deleted"),
                 lambda r, d: "and origin has no main"),
                # (3): no <default-ref> to build on -- never built on local main -- held as origin has no main
                ("l-cod-origin-lacks", lambda r: r.git("update-ref", "-d", "refs/remotes/origin/main"), "origin/main",
                 lambda r, d: d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="origin-lacks"),
                 lambda r, d: "and origin has no main"),
                ("l-cod-refused", lambda r: hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n"), "origin/main",
                 lambda r, d: d["outcome"] == "refused" and d["text"] == "pre-receive hook declined"
                 and same_path(d["record"], record_of(r)) and d["date"] is None and d["record_error"] is None,
                 lambda r, d: "and origin refuses pushes to main (pre-receive hook declined), so from the next run "
                              "session-branch mode takes these files"),
            )
            rendered, takes = [], {}
            for name, setup, default_ref, holds, want in cases:
                r = lworld(name)
                w2 = worktree(r, name + "-w2")
                setup(r)
                r.write(FB, ENTRY % "mine")
                got = do_land(r, default_ref=default_ref)
                refused = got.get("refused") or {}
                d = refused.get("detail") or {}
                entries = held(r)
                try:
                    ok = isinstance(d, dict) and set(d) == set(CHECKED_OUT_DETAIL) and holds(r, d)
                except (KeyError, TypeError, AttributeError):
                    ok = False
                values = checked_out_values(lines, d)
                try:
                    line = lines.fill("reason.land.checked-out", dict(values or {}, **{"<path>": refused.get("path"),
                                                                                     "<default>": "main"}))
                except ValueError as e:
                    line = "fill: %s" % e
                rendered.append(line)
                check(got["status"] == "held" and refused.get("reason") == "checked-out" and ok
                      and len(entries) == 1 and entries[0]["refused"] == refused
                      and line == "another worktree, %s, has main checked out, %s" % (refused.get("path"), want(r, d)),
                      "l_checked_out_detail: %s's detail kept in the held record, and its clause worded whole (%r, %r)"
                      % (name, d, line))
                check(same_path(refused.get("path"), w2.path), "l_checked_out_detail: %s names the worktree" % name)
                takes[name] = mode_takes(refused)
            check(not any("failed (failed)" in x or "()" in x for x in rendered),
                  "l_checked_out_detail: no clause reads failed (failed) or an empty () (%r)" % rendered)
            def clause(refused):
                values = checked_out_values(lines, refused.get("detail"))
                try:
                    return lines.fill("reason.land.checked-out", dict(values or {}, **{"<path>": refused.get("path"),
                                                                                     "<default>": "main"}))
                except ValueError as e:
                    return "fill: %s" % e

            # refused-before, a record another session wrote mid-run: worded as row.refused-before words it
            r = lworld("l-cod-refused-before")
            w2 = worktree(r, "l-cod-refused-before-w2")
            r.write(FB, ENTRY % "mine")
            snap = snapshot(r.path)  # the run's start
            refused_before(r)        # mid-run
            r.write(FB2, ENTRY % "mine too")
            got = do_land(r, snap=snap)
            refused = got.get("refused") or {}
            d = refused.get("detail") or {}
            line = clause(refused)
            check(d == dict(dict.fromkeys(CHECKED_OUT_DETAIL), outcome="refused-before", date="2026-11-01",
                            record=record_of(r)) and held(r)[0]["refused"] == refused and refused.get("permanent") is False
                  and line == "another worktree, %s, has main checked out, and origin refused pushes to main on "
                              "2026-11-01 (%s), so from the next run session-branch mode takes these files"
                              % (refused.get("path"), record_of(r))
                  and same_path(refused.get("path"), w2.path) and sb.mode(r.path, "main")["mode"] == "on",
                  "l_checked_out_detail: refused-before, its record written mid-run, worded whole from the record's "
                  "date and path; the mode it names is on (%r, %r)" % (d, line))
            rendered.append(line)
            takes["l-cod-refused-before"] = mode_takes(refused)

            # refused, its record writable neither way: the unrecorded form, naming the configuration write's error
            r = lworld("l-cod-unrecorded")
            w2 = worktree(r, "l-cod-unrecorded-w2")
            hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
            os.makedirs(os.path.join(r.path, ".git", "workflows"), exist_ok=True)
            with open(os.path.join(r.path, ".git", "workflows", "push-refused"), "w", encoding="utf-8") as fh:
                fh.write("a file where the record's directory would go\n")
            lock = os.path.join(r.path, ".git", "config.lock")
            with open(lock, "w", encoding="utf-8") as fh:
                fh.write("")
            r.write(FB, ENTRY % "mine")
            try:
                got = do_land(r)
            finally:
                os.remove(lock)
            refused = got.get("refused") or {}
            d = refused.get("detail") or {}
            line = clause(refused)
            error = d.get("record_error") or ""
            check(set(d) == set(CHECKED_OUT_DETAIL) and d["outcome"] == "refused"
                  and d["text"] == "pre-receive hook declined" and d["record"] is None and "config" in error
                  and held(r)[0]["refused"] == refused
                  and line == "another worktree, %s, has main checked out, and origin refuses pushes to main "
                              "(pre-receive hook declined), but this could not be recorded (%s, the configuration "
                              "write's), so a later run pushes main again" % (refused.get("path"), error)
                  and sb.refusal_record(r.path, "main") is None and sb.mode(r.path, "main")["mode"] == "off",
                  "l_checked_out_detail: refused with its record unwritable, worded in the unrecorded form, naming the "
                  "configuration write's error; no record, the mode off (%r, %r)" % (d, line))
            rendered.append(line)
            takes["l-cod-unrecorded"] = mode_takes(refused)
            check(takes == {"l-cod-failed": False, "l-cod-rejected": False, "l-cod-no-remote": False,
                            "l-cod-elsewhere": False, "l-cod-remote-deleted": False, "l-cod-origin-lacks": False,
                            "l-cod-refused": True,
                            "l-cod-refused-before": True, "l-cod-unrecorded": False}
                  and mode_takes(None) is False and mode_takes({"reason": "moved", "detail": "branch-moved"}) is False,
                  "l_checked_out_detail: mode_takes is true exactly where a record turns session-branch mode on, so the "
                  "held lines take their mode tail (%r)" % takes)
            check(not any("failed (failed)" in x or "()" in x or "None" in x for x in rendered[-2:]),
                  "l_checked_out_detail: neither new form reads an empty () or None (%r)" % rendered[-2:])

            # every detail _land_change can produce: from each push outcome _push_detail meets and each row
            # _row_detail meets, and None (held with no push tried); checked_out_values and the fill never raise
            pushes = [{"outcome": o, "reason": why, "record": rec, "record_error": err}
                      for o, why in (("failed", "fatal: x"), ("failed", None), ("rejected", "[rejected] (fetch first)"),
                                     ("rejected", None))
                      for rec, err in ((None, None),)]
            pushes += [{"outcome": "refused", "reason": why, "record": rec, "record_error": err}
                       for why in ("hook declined", "", None)
                       for rec, err in (("/s/.git/workflows/push-refused/main", None),
                                        ("branch.main.workflowsPushRefused", None), (None, "error: could not lock"))]
            rows = [{"row": "no-remote"}, {"row": "elsewhere", "remote": "fork"}, {"row": "remote-deleted"}]
            rows += [{"row": "refused-before", "record": rec, "date": date}
                     for rec, date in (("/s/.git/workflows/push-refused/main", "2026-11-01"),
                                       ("/s/.git/workflows/push-refused/main", "an earlier run"),
                                       ("branch.main.workflowsPushRefused", "2026-11-01"))]
            details = [_push_detail(x) for x in pushes] + [_row_detail(x) for x in rows] + [None]
            problems = []
            for detail in details:
                try:
                    values = checked_out_values(lines, detail)
                    if values is None:
                        if detail is not None:
                            problems.append("no values for %r" % (detail,))
                        continue
                    line = lines.fill("reason.land.checked-out", dict(values, **{"<path>": "/w2", "<default>": "main"}))
                    if "()" in line or "None" in line:
                        problems.append(line)
                except Exception as e:  # any raise is the failure this check is for
                    problems.append("%r raised %s: %s" % (detail, type(e).__name__, e))
            check(problems == [] and len(details) == 20,
                  "l_checked_out_detail: every detail _land_change can produce maps and fills without raising (%r)"
                  % problems)
            # a push that gave no reason takes the words a status line with none gives (specs-repo-git §6)
            got = _push_detail({"outcome": "failed", "reason": None, "record": None})
            check(got["text"] == lines.T["app.why.failed.none"] and checked_out_values(lines, None) is None
                  and checked_out_values(lines, "failed") is None,
                  "l_checked_out_detail: a failed push with no reason reads no status line; no detail object, no values "
                  "(%r)" % got)

        def l_cli_local_retries():
            """Minor 5: the CLI's landing retries earlier held entries locally only, as end's does (§4 step 1): one that
            would need the refspec push stays held, and holds back the run's change on its path."""
            r = lworld("l-cli-local")
            worktree(r, "l-cli-local-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            first = do_land(r)
            r.git("remote", "set-url", "origin", r.bare)  # the refspec push would go through now
            snap_file = os.path.join(tmp, "l-cli-local.snap.json")
            with open(snap_file, "w", encoding="utf-8") as fh:
                json.dump(snapshot(r.path), fh)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            up, local = on_origin(r), main_of(r)
            got = cli("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback",
                      "--snapshot", snap_file, env=r.env)
            detail = got.get("detail") or {}
            check(first["status"] == "held" and got["_rc"] == 0 and got.get("status") == "held"
                  and got.get("reason") == "checked-out" and detail.get("outcome") == "failed"
                  and got.get("pushed") is False and on_origin(r) == up and main_of(r) == local and len(held(r)) == 2,
                  "l_cli_local_retries: the earlier entry stays held, not pushed by refspec, and holds the run's change "
                  "back (%r)" % got)

        def l_here_resume_unfinished():
            """Minor 6: an end --resume whose here-form journal is at neither its tip nor its old commit keeps the change
            with a reason of its own, unfinished, never moved."""
            r = here_world("l-here-unfinished")
            e = stopped(lambda: here_land(r, on_move=kill))
            r.git("commit", "-q", "--allow-empty", "-m", "elsewhere")
            got = here_land(r, resume=e.pending if e else None) if e else {}
            refused = got.get("refused") or {}
            _, lines = _flow()
            clause = lines.fill(LAND_REASONS.get(refused.get("reason"), "reason.land.moved"), {"<branch>": "main",
                                                                                              "<default>": "main"})
            check(got.get("status") == "kept" and refused.get("reason") == "unfinished" and held(r) == []
                  and held_refs(r) == [] and read(r, FUP) == "- [ ] a\n- [ ] mine\n" and read(r, FB) == ENTRY % "mine"
                  and clause == ("main moved on without the commit this run was making on it when it was cut off, "
                                 "so that commit was dropped unfinished")
                  and refused.get("permanent") is True,
                  "l_here_resume_unfinished: kept as unfinished, nothing held, the files as they stand (%r, %r)"
                  % (got, clause))

        def l_split_collision():
            # review exp2: P8 rebuilds a transient entry, then every path left is refused, in one retry_held call; the
            # split's stuck commit is the rebuilt entry's own commit (same tree, parent, message and, pinned, dates)
            r = lworld("l-split-collision", extra=[(RESUME, "v0\n")])
            os.remove(os.path.join(r.path, RESUME))
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.write(FB, ENTRY % "edited")  # P8: the feedback file leaves the entry
            w = worktree(r, "l-split-collision-w2")
            w.write(RESUME, "v9\n")
            w.git("commit", "-q", "-am", "ACME-1 resume.md changed on main")  # the deletion is now refused, deleted
            r.git("worktree", "remove", "--force", w.path)
            with in_env({"GIT_COMMITTER_DATE": "1793700000 +0000", "GIT_AUTHOR_DATE": "1793700000 +0000"}):
                got = retry_held(r.path, "main", "origin/main")
            entries, sha = held(r), ((got["stuck"] or [{}])[0]).get("sha")
            check(len(got["stuck"]) == 1 and got["stuck"][0]["refused"]["reason"] == "deleted" and len(entries) == 1
                  and entries[0]["c2"] == sha and list(entries[0]["paths"]) == [RESUME]
                  and entries[0]["refused"]["permanent"] is True and held_refs(r) == [HELD + sha]
                  and read(r, RESUME) is None and read(r, FB) == ENTRY % "edited",
                  "l_split_collision: the stuck entry reported stands in the record with its ref (%r, %r)"
                  % (got, entries))

        def chain_committed(name, held_own):
            # review exp4: a held entry's version the user then commits on the stayed branch; a later run starts from
            # HEAD's version, with no snapshot of the path, so it does not start from the held entry
            r = lworld(name)
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.git("commit", "-q", "-am", "B-2 the user commits follow-ups.md as it stands")
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            if held_own:
                with patched("move_branch", locked_move()):
                    do_land(r, snap=snap)
                after = held(r)  # land's P8 has dropped the committed entry: the own change is held alone
                return r, (snap, after), retry_held(r.path, "main", "origin/main")
            return r, snap, do_land(r, snap=snap)

        def l_chain_committed_land():
            r, snap, got = chain_committed("l-chain-committed-land", False)
            check(snap == {} and got["status"] == "landed" and got["held_landed"] == []
                  and read(r, FUP) == "- [ ] a\n- [ ] l1\n" and r.git("diff", "HEAD", "--", FUP) == ""
                  and porcelain(r) == "" and held(r) == [] and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l2",
                  "l_chain_committed_land: P8 drops the committed entry in land's step 3 as retry_held does: main "
                  "holds the later change alone, the working copy HEAD's (%r, %r, %r)"
                  % (got, read(r, FUP), show(r, main_of(r), FUP)))

        def l_chain_committed_retry():
            r, (snap, after), got = chain_committed("l-chain-committed-retry", True)
            check(snap == {} and len(after) == 1 and list(after[0]["paths"]) == [FUP]
                  and r.git("rev-parse", after[0]["c1"] + "^") == r.git("rev-parse", "HEAD")
                  and len(got["landed"]) == 1 and got["dropped"] == 0 and read(r, FUP) == "- [ ] a\n- [ ] l1\n"
                  and r.git("diff", "HEAD", "--", FUP) == "" and porcelain(r) == "" and held(r) == []
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] l2",
                  "l_chain_committed_retry: land's P8 drops the committed entry, the later change is held alone and "
                  "retry_held lands it alone, the working copy HEAD's (%r, %r, %r, %r)"
                  % (after, got, read(r, FUP), show(r, main_of(r), FUP)))

        def l_land_pending_own():
            # review exp3: a held entry lands in step 3, then the run's own change fails before its journal
            r = lworld("l-pending-own")
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            with patched("move_branch", locked_move()):
                do_land(r)
            first = held(r)[0]
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            real, calls = sb.own_change, []

            def fail_second(*args, **kw):
                calls.append(1)
                if len(calls) == 2:
                    raise OSError("git failed in the run's own change")
                return real(*args, **kw)
            with patched("own_change", fail_second):
                e = stopped(lambda: do_land(r, snap=snap))
            entries = held(r)
            check(e is not None and e.pending is None and len(entries) == 1 and entries[0]["c2"] == first["c2"]
                  and entries[0]["refused"] is None and entries[0]["tip"] == main_of(r),
                  "l_land_pending_own: LandStopped carries no held entry's pending; that journal stays in its record "
                  "(%r, %r)" % (e and e.pending, entries))

        def l_land_resume_chain():
            # review exp6: the run is killed after its move, before its lift; another run's change, started from its
            # version, is held; end --resume lands that entry in step 3 and lifts the chain from the resumed change
            r = lworld("l-resume-chain")
            r.write(FUP, "- [ ] a\n- [ ] own\n")

            def no_lift(*_args):
                raise OSError("killed before the lift")
            with patched("write_from", no_lift):
                e = stopped(lambda: do_land(r))
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] own\n- [ ] other\n")
            with patched("move_branch", locked_move()):
                do_land(r, snap=snap)
            got = do_land(r, resume=e.pending if e else None)
            check(e is not None and got["status"] == "landed" and len(got["held_landed"]) == 1 and got["lifted"] == [FUP]
                  and read(r, FUP) == "- [ ] a\n" and porcelain(r) == "" and held(r) == []
                  and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] own\n- [ ] other",
                  "l_land_resume_chain: the resumed change is the oldest of the chain it starts, the file lifted to "
                  "HEAD's (%r, %r)" % (got, read(r, FUP)))

        def l_retry_held_blocked():
            # a blocked entry's failed row, and its record, carry the refusal of the entry it waits for
            r = lworld("l-retry-blocked")
            worktree(r, "l-retry-blocked-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] l1\n")
            do_land(r)
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] l1\n- [ ] l2\n")
            do_land(r, snap=snap)
            stale = {"reason": "locked", "path": ".git/refs/heads/main.lock", "detail": None, "permanent": False}
            g["_held_put"](r.path, dict(held(r)[1], refused=stale))
            got = retry_held(r.path, "main", "origin/main")
            first, second = held(r)
            check([x["refused"] for x in got["failed"]] == [first["refused"], first["refused"]]
                  and first["refused"]["reason"] == "checked-out" and second["refused"] == first["refused"],
                  "l_retry_held_blocked: the blocked entry reports, and records, the refusal it waits on (%r, %r)"
                  % (got["failed"], held(r)))

        def l_cli_retry_partial():
            # land --retry-held stopped by an error after a landing reports that landing before the error
            r = lworld("l-retry-partial")
            r.write(FB, ENTRY % "one")
            with patched("move_branch", locked_move()):
                do_land(r)
            snap = snapshot(r.path)
            r.write(FB2, ENTRY % "two")
            with patched("move_branch", locked_move()):
                do_land(r, snap=snap)
            real, calls = sb.own_change, []

            def fail_second(*args, **kw):
                calls.append(1)
                if len(calls) == 2:
                    raise OSError("git failed in the second entry")
                return real(*args, **kw)
            args = argparse.Namespace(specs=r.path, default_ref="origin/main", retry_held=True, drop_held=None,
                                      branch=None, command=None, commit_key=None, snapshot=None, here=False,
                                      register_rebuild=None)
            with patched("own_change", fail_second):
                got = land_cli(args)
            check("git failed in the second entry" in (got.get("error") or "") and len(got["landed"]) == 1
                  and got["landed"][0]["paths"] == [FB] and got["landed"][0]["sha"] == main_of(r)
                  and got["landed"][0]["lifted"] == [] and got["failed"] == [] and got["stuck"] == [],
                  "l_cli_retry_partial: the landing made before the error is reported with it (%r)" % got)

        def l_retry_held_edited():
            r = lworld("l-retry-edited")
            worktree(r, "l-retry-edited-w2")
            r.git("remote", "set-url", "origin", os.path.join(tmp, "nowhere.git"))
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            r.write(FB, ENTRY % "mine")
            do_land(r)
            first = held(r)[0]
            r.write(FB, ENTRY % "edited")
            got = retry_held(r.path, "main", "origin/main", retry_remote=False)
            entries = held(r)
            check(sorted(first["paths"]) == [FB, FUP] and len(entries) == 1 and list(entries[0]["paths"]) == [FUP]
                  and entries[0]["c2"] != first["c2"] and held_refs(r) == [HELD + entries[0]["c2"]]
                  and changed(r, entries[0]["c2"]) == [FUP] and read(r, FB) == ENTRY % "edited"
                  and got["dropped"] == 0 and len(got["failed"]) == 1,
                  "l_retry_held_edited: a held file edited since leaves the entry, rebuilt without it (%r, %r)"
                  % (got, entries))
            r.write(FUP, "- [ ] a\n- [ ] x\n- [ ] edited\n")
            got = retry_held(r.path, "main", "origin/main", retry_remote=False)
            check(got["dropped"] == 1 and held(r) == [] and held_refs(r) == [] and read(r, FB) == ENTRY % "edited"
                  and read(r, FUP) == "- [ ] a\n- [ ] x\n- [ ] edited\n",
                  "l_retry_held_edited: an entry left with no file is dropped, the files untouched (%r)" % got)

        def l_retry_held_on_default():
            r = lworld("l-retry-default")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            old = main_of(r)
            r.git("switch", "-q", "main")
            got = retry_held(r.path, "main", "origin/main")
            check(got["dropped"] == 1 and got["landed"] == [] and held(r) == [] and held_refs(r) == []
                  and read(r, FB) == ENTRY % "mine" and main_of(r) == old,
                  "l_retry_held_on_default: HEAD on main drops the entry, its file left (%r)" % got)

        def l_retry_held_journal():
            r = lworld("l-retry-journal")
            r.write(FB, ENTRY % "mine")

            def no_lift(*_args):
                raise OSError("killed before the lift")
            with patched("write_from", no_lift):
                e = stopped(lambda: do_land(r))
            tip = main_of(r)
            entries = held(r)
            check(e is not None and (e.pending or {}).get("tip") == tip and len(entries) == 1
                  and entries[0]["refused"] is None and entries[0]["tip"] == tip and read(r, FB) == ENTRY % "mine",
                  "l_retry_held_journal: a kill after the move leaves the journal entry (%r)" % entries)
            got = retry_held(r.path, "main", "origin/main")
            check(got["finished"] == [{"sha": tip, "here": False, "lifted": [{"path": FB, "blob": None}]}]
                  and main_of(r) == tip and read(r, FB) is None and held(r) == [] and held_refs(r) == [],
                  "l_retry_held_journal: main holds the tip: lifted only (%r)" % got)

        def l_retry_held_journal_before_move():
            r = lworld("l-retry-before-move")
            old = main_of(r)
            r.write(FUP, "- [ ] a\n- [ ] b\n")
            e = stopped(lambda: do_land(r, on_move=kill))
            entries = held(r)
            check(e is not None and main_of(r) == old and len(entries) == 1 and entries[0]["refused"] is None
                  and entries[0]["tip"] == (e.pending or {}).get("tip") and read(r, FUP) == "- [ ] a\n- [ ] b\n",
                  "l_retry_held_journal_before_move: a kill before the move leaves main at old (%r)" % entries)
            got = retry_held(r.path, "main", "origin/main")
            check(r.git("rev-list", "--count", old + "..main") == "1" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] b"
                  and read(r, FUP) == "- [ ] a\n" and len(got["landed"]) == 1 and held(r) == [],
                  "l_retry_held_journal_before_move: landed again, main moved once, lifted after (%r)" % got)

        def l_held_rebuild():
            r = lworld("l-held-rebuild")
            r.write(FUP, "- [ ] a\n- [ ] x\n")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            entry = dict(held(r)[0], lift={FUP: r.git("rev-parse", "HEAD:" + FUP), FB: None})
            g["_held_put"](r.path, entry)  # a lift override on each path, as a partly landed chain leaves one
            new = held_rebuild(r.path, entry, [FB])
            check(new is not None and list(new["paths"]) == [FUP] and new["c2"] != entry["c2"] and held(r) == [new]
                  and held_refs(r) == [HELD + new["c2"]] and changed(r, new["c2"]) == [FUP]
                  and r.git("rev-parse", new["c2"] + "^") == entry["c1"] and read(r, FB) == ENTRY % "mine"
                  and new.get("lift") == {FUP: entry["lift"][FUP]},
                  "l_held_rebuild: rebuilt without the path, its lift override with it (%r)" % new)
            gone = held_rebuild(r.path, new, [FUP])
            check(gone is None and held(r) == [] and held_refs(r) == [] and read(r, FUP) == "- [ ] a\n- [ ] x\n",
                  "l_held_rebuild: an entry left with no file is dropped")

        def l_held_drop():
            r = lworld("l-held-drop")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            sha7 = held(r)[0]["c2"][:7]
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--drop-held", sha7, env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"dropped", "sha7", "error"}
                  and got.get("dropped") is True and got.get("sha7") == sha7 and held(r) == [] and held_refs(r) == []
                  and read(r, FB) == ENTRY % "mine",
                  "l_held_drop: --drop-held removes the entry and its ref, the file untouched (%r)" % got)
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--drop-held", sha7, env=r.env)
            check(got["_rc"] == 0 and got.get("dropped") is False, "l_held_drop: a second drop finds none (%r)" % got)

        def l_held_orphan_refs():
            r = lworld("l-orphans")
            w2 = worktree(r, "l-orphans-w2")
            base, tree = r.git("rev-parse", "main"), r.git("rev-parse", "main^{tree}")

            def commit_at(seconds_ago, message):
                stamp = "%d +0000" % (time.time() - seconds_ago)
                return r.git("commit-tree", tree, "-p", base, "-m", message,
                             env={"GIT_COMMITTER_DATE": stamp, "GIT_AUTHOR_DATE": stamp})
            listed, old, young, late = (commit_at(7200, "listed"), commit_at(7200, "old"), commit_at(60, "young"),
                                        commit_at(7200, "late"))
            entry = {"c1": base, "c2": listed, "old": None, "tip": None, "onto": "main", "branch": "main",
                     "remote_only": False, "kind": None, "merged": None, "command": "/feedback",
                     "refused": {"reason": "locked", "path": None, "detail": None, "permanent": False},
                     "date": "2026-11-10", "paths": {}, "here": False, "index_before": None}
            g["_held_put"](w2.path, entry)
            for c in (old, young):
                r.git("update-ref", HELD + c, c)
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, old, young)) and held(w2) == [entry]
                  and held(r) == [], "l_held_orphan_refs: three refs, one listed by w2's record")
            r.git("switch", "-q", "--detach")
            retry_held(r.path, "main", "origin/main")
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, old, young)),
                  "l_held_orphan_refs: on a detached HEAD nothing is done, the orphan sweep included (P9) (%r)"
                  % held_refs(r))
            r.git("switch", "-q", LB)
            real, made = g["_read_held"], []

            def racing(path):
                if not made:  # another worktree writes a held ref while this sweep reads the records
                    made.append(r.git("update-ref", HELD + late, late))
                return real(path)
            g["_read_held"] = racing
            try:
                retry_held(r.path, "main", "origin/main")
            finally:
                g["_read_held"] = real
            check(sorted(held_refs(r)) == sorted(HELD + c for c in (listed, young, late)),
                  "l_held_orphan_refs: the unlisted ref over an hour old removed; w2's, one younger than an hour, and one "
                  "written while the records were read, all kept (%r)" % held_refs(r))

        def here_world(name, extra=()):
            r = lworld(name, extra=extra, stay=False)
            r.write(FUP, "- [ ] a\n- [ ] mine\n")
            r.write(FB, ENTRY % "mine")
            return r

        def lock_after_move(r):
            real = sb.git

            def fake(root, *args, **kw):
                out = real(root, *args, **kw)
                if args and args[0] == "update-ref" and "refs/heads/main" in args:
                    open(os.path.join(r.path, ".git", "index.lock"), "w").close()
                return out
            return fake

        def here_land(r, snap=None, **kw):
            return land(r.path, "main", "main", "origin/main", MSG, snap, **kw)

        def l_land_here():
            r = lworld("l-here", stay=False)
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            snap = snapshot(r.path)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] mine\n")
            r.write(FB, ENTRY % "mine")
            old = main_of(r)
            mtimes = [os.stat(os.path.join(r.path, p)).st_mtime_ns for p in (FUP, FB)]
            got = here_land(r, snap)
            tip = main_of(r)
            diff = [x for x in r.git("diff", "HEAD", "--", FUP).splitlines()
                    if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
            check(got["status"] == "landed" and got["sha"] == tip and r.git("rev-parse", tip + "^") == old
                  and changed(r, tip) == [FB, FUP] and show(r, tip, FUP) == "- [ ] a\n- [ ] mine" and got["onto"] == "main"
                  and got["lifted"] == [] and got["pushed"] is False,
                  "l_land_here: main advanced by one commit holding only the run's own (%r)" % got)
            check(r.git("diff", "--cached") == "" and diff == ["+- [ ] s"]
                  and [os.stat(os.path.join(r.path, p)).st_mtime_ns for p in (FUP, FB)] == mtimes
                  and held(r) == [] and held_refs(r) == [],
                  "l_land_here: the index restored, S's line alone left, no file written, no journal (%r, %r)"
                  % (r.git("diff", "--cached"), diff))

        def l_land_here_refused():
            r = lworld("l-here-refused", extra=[(COST, COST_BODY)], stay=False)
            old = main_of(r)
            r.write(COST, EDITED)
            r.write(FB, ENTRY % "mine")
            got = here_land(r)
            check(got["status"] == "kept" and (got["refused"] or {}).get("reason") == "edited" and main_of(r) == old
                  and held(r) == [] and held_refs(r) == [] and read(r, COST) == EDITED,
                  "l_land_here_refused: a refusal keeps the whole change, nothing moved, no journal (%r)" % got)

        def l_land_here_recheck_and_retry():
            r = here_world("l-here-recheck")
            old = main_of(r)
            index_fup = r.git("rev-parse", ":" + FUP)
            with patched("git", lock_after_move(r)):
                e = stopped(lambda: here_land(r))
            tip = main_of(r)
            entries = held(r)
            check(e is not None and (e.pending or {}).get("here") is True and (e.pending or {}).get("tip") == tip
                  and str(e).startswith("main moved to %s, but .git/index.lock stands" % tip[:7])
                  and tip != old and len(entries) == 1 and entries[0]["here"] is True and entries[0]["refused"] is None
                  and entries[0]["index_before"] == {FB: None, FUP: index_fup},
                  "l_land_here_recheck: a lock after the move raises with pending.here, the journal kept (%r)" % entries)
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            check(r.git("diff", "--cached") != "", "l_retry_held_here: the index still on the old tip before")
            got = retry_held(r.path, "main", "origin/main")
            check(got["finished"] == [{"sha": tip, "here": True, "lifted": []}] and r.git("diff", "--cached") == ""
                  and main_of(r) == tip and held(r) == [] and held_refs(r) == [],
                  "l_retry_held_here: the index restored from index_before, a new file included (%r)" % got)
            # the user stages follow-ups.md after the kill: that path's index entry is theirs and stays (exp5)
            r = here_world("l-here-recheck-staged")
            with patched("git", lock_after_move(r)):
                stopped(lambda: here_land(r))
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            r.write(FUP, "- [ ] a\n- [ ] mine\n- [ ] staged by the user\n")
            r.git("add", FUP)
            staged = r.git("rev-parse", ":" + FUP)
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["finished"]) == 1 and r.git("rev-parse", ":" + FUP) == staged
                  and r.git("diff", "--cached", "--name-only") == FUP and held(r) == [],
                  "l_retry_held_here_staged: a path the user staged after the kill stays as they staged it, the rest "
                  "restored "
                  "(%r, %r)" % (got, r.git("diff", "--cached", "--name-only")))

        def l_retry_held_here_old():
            r = here_world("l-here-old")
            old = main_of(r)
            e = stopped(lambda: here_land(r, on_move=kill))
            check(e is not None and main_of(r) == old and held(r)[0]["here"] is True,
                  "l_retry_held_here_old: a kill before the move")
            got = retry_held(r.path, "main", "origin/main")
            check(r.git("rev-list", "--count", old + "..main") == "1" and show(r, main_of(r), FUP) == "- [ ] a\n- [ ] mine"
                  and r.git("diff", "--cached") == "" and len(got["finished"]) == 1 and held(r) == [],
                  "l_retry_held_here_old: the here form again, one commit (%r)" % got)

        def l_retry_held_here_elsewhere():
            r = here_world("l-here-elsewhere")
            stopped(lambda: here_land(r, on_move=kill))
            r.git("commit", "-q", "--allow-empty", "-m", "elsewhere")
            got = retry_held(r.path, "main", "origin/main")
            check(got["dropped"] == 1 and got["finished"] == [] and held(r) == [] and held_refs(r) == []
                  and read(r, FUP) == "- [ ] a\n- [ ] mine\n" and read(r, FB) == ENTRY % "mine",
                  "l_retry_held_here_elsewhere: main at neither: dropped, the files untouched (%r)" % got)

        def l_retry_held_here_ancestor():
            r = here_world("l-here-ancestor")
            with patched("git", lock_after_move(r)):
                stopped(lambda: here_land(r))
            tip = main_of(r)
            os.remove(os.path.join(r.path, ".git", "index.lock"))
            r.write("notes.md", "n\n")
            r.git("add", "notes.md")
            r.git("commit", "-q", "-m", "on top", "--", "notes.md")
            check(main_of(r) != tip and r.git("rev-parse", "main^") == tip
                  and r.git("diff", "--cached") != "", "l_retry_held_here_ancestor: main one commit past the tip")
            got = retry_held(r.path, "main", "origin/main")
            check(len(got["finished"]) == 1 and got["dropped"] == 0 and r.git("diff", "--cached") == "" and held(r) == [],
                  "l_retry_held_here_ancestor: the tip an ancestor: the index restored, finished (%r)" % got)

        def l_land_resume():
            r = lworld("l-resume")
            old = main_of(r)
            r.write(FB, ENTRY % "mine")
            e = stopped(lambda: do_land(r, on_move=kill))
            r.write(FB2, ENTRY % "after")  # written after the kill: no part of the pending change
            got = do_land(r, resume=e.pending if e else None)
            check(e is not None and got["status"] == "landed" and got["held_landed"] == [] and held(r) == []
                  and held_refs(r) == [] and r.git("rev-list", "--count", old + "..main") == "1"
                  and changed(r, main_of(r)) == [FB] and read(r, FB) is None and read(r, FB2) == ENTRY % "after",
                  "l_land_resume: the pending landed again, alone, its journal entry never a held one (%r)" % got)

        def l_land_register():
            r = lworld("l-register")
            r.write(FB, ENTRY % "mine")
            canned = {"before_remote": {"web": {"o1": 1}}, "before_run": {"web": {"o2": 3}},
                      "after": {"web": {"o1": 2, "o2": 1}}}
            real = sb.own_change

            def fake(*args, **kw):
                return dict(real(*args, **kw), numbers=canned)
            with patched("own_change", fake):
                got = do_land(r)
            check(got["status"] == "landed" and got["moves"] and got["moves"] == sb._moves([canned]),
                  "l_land_register: moves as sb._moves gives them (%r)" % got)

        def l_cli_land():
            r = lworld("l-cli")
            r.write(FB, ENTRY % "mine")
            base = ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--command", "/feedback")
            got = cli(*base, env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == CLI_FIELDS
                  and got.get("status") == "landed" and got.get("sha7") == main_of(r)[:7] and got.get("files") == 1
                  and got.get("paths") == [FB] and got.get("lifted") == [FB] and got.get("default") == "main"
                  and got.get("pushed") is False and got.get("error") is None and got.get("reason") is None
                  and r.git("log", "-1", "--format=%s", "main") == "NOISSUE Add dev-workflows session artifacts (/feedback)",
                  "l_cli_land: landed, the session subject (%r)" % got)
            r.write(FB2, ENTRY % "two")
            got = cli(*base, "--commit-key", "ACME-1", env=r.env)
            check(got.get("status") == "landed"
                  and r.git("log", "-1", "--format=%s", "main") == "ACME-1 Add dev-workflows session artifacts (/feedback)",
                  "l_cli_land: --commit-key opens the subject (%r)" % got)
            r.write(FUP, "- [ ] a\n- [ ] s\n")
            snap = {k: v for k, v in cli("--specs", r.path, "snapshot", env=r.env).items() if not k.startswith("_")}
            check(snap == {FUP: r.git("hash-object", FUP)}, "l_cli_land: snapshot prints the map --snapshot takes (%r)" % snap)
            path = os.path.join(tmp, "l-cli-snapshot.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(snap, fh)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] one\n")
            got = cli(*base, "--snapshot", path, env=r.env)
            check(got.get("status") == "landed" and show(r, "main", FUP) == "- [ ] a\n- [ ] one"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n", "l_cli_land: --snapshot <file> honoured (%r)" % got)
            r.write(FUP, "- [ ] a\n- [ ] s\n- [ ] two\n")
            got = cli(*base, "--snapshot", "-", stdin=json.dumps(snap).encode(), env=r.env)
            check(got.get("status") == "landed" and show(r, "main", FUP) == "- [ ] a\n- [ ] one\n- [ ] two"
                  and read(r, FUP) == "- [ ] a\n- [ ] s\n", "l_cli_land: --snapshot - honoured (%r)" % got)
            h = here_world("l-cli-here")
            old = main_of(h)
            got = cli("--specs", h.path, "land", "--branch", "main", "--default-ref", "origin/main", "--command",
                      "/feedback", "--here", env=h.env)
            check(got.get("status") == "landed" and got.get("sha7") == main_of(h)[:7]
                  and h.git("rev-parse", "main^") == old and h.git("diff", "--cached") == "" and got.get("lifted") == [],
                  "l_cli_land: --here on main (%r)" % got)
            got = cli("--specs", r.path, "land", "--default-ref", "origin/main", "--retry-held", env=r.env)
            check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"landed", "finished", "failed", "stuck",
                                                                                     "dropped", "error"},
                  "l_cli_land: --retry-held prints its object (%r)" % got)

        def l_cli_exit2():
            r = lworld("l-cli-exit2")
            r.write(FB, ENTRY % "mine")
            with patched("move_branch", locked_move()):
                do_land(r)
            r.write(FB2, ENTRY % "two")
            nowhere = os.path.join(tmp, "l-cli-exit2-nowhere")
            os.makedirs(nowhere)

            def state_of():
                with open(held_path(r.path), encoding="utf-8") as fh:
                    return r.git("for-each-ref"), porcelain(r), fh.read()
            before = state_of()
            tail = ("--command", "/feedback")
            for what, args in (
                    ("--branch naming a branch HEAD is not on",
                     ("--specs", r.path, "land", "--branch", "main", "--default-ref", "origin/main") + tail),
                    ("a --default-ref that does not resolve",
                     ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/nowhere") + tail),
                    ("--commit-key acme-1",
                     ("--specs", r.path, "land", "--branch", LB, "--default-ref", "origin/main", "--commit-key", "acme-1")
                     + tail),
                    ("no repository", ("--specs", nowhere, "land", "--branch", LB, "--default-ref", "origin/main") + tail),
                    ("--specs below the top level",
                     ("--specs", os.path.join(r.path, "specifications"), "land", "--branch", LB, "--default-ref",
                      "origin/main") + tail)):
                got = cli(*args, env=r.env)
                check(one_not_run_line(got) and "_stdout" not in got and not got["_raw"].strip() and state_of() == before,
                      "l_cli_exit2: %s exits 2 with one line, nothing changed (%r)" % (what, got))

        def l_sb_reused():
            with open(me, encoding="utf-8") as fh:
                src = fh.read()
            found = re.findall(r"^def (own_change|tree_with|commit_tree|move_branch|replay_commits)\b", src, re.M)
            check(found == [], "l_sb_reused: specs-git.py imports session-branch.py's functions, defining none (%r)" % found)

        g = globals()
        for name, fn in sorted(locals().items()):
            if name.startswith("l_") and callable(fn):
                case(name, fn)

    def scenarios_replay(tmp):
        state, lines = _flow()
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        REG = "security/web/register.json"
        END_FIELDS = {"print", "line", "row", "sha7", "files", "branch", "pushed", "next", "record", "error"}
        TIMED = ("session-branch.py did not finish within 420 s, so %s may already stand on the replay (git -C \"%s\" log "
                 "-1 %s shows it); the next run whose preflight gets past its guards retries the push where it stands on "
                 "%s or %s is a plugin branch")

        def plain(specs, branch):
            return 'run git -C "%s" pull --rebase --no-autostash origin %s, then git -C "%s" push origin %s' % (
                specs, branch, specs, branch)

        def rejected(opening, branch, clause, remedy):
            return ("%s — push REJECTED: origin's %s has commits this one lacks, and the run could not take them in: %s%s"
                    % (opening, branch, clause, "; " + remedy if remedy else ""))

        def committed(sha7, branch, n=1):
            return "Specs repo: committed %s (%s) on %s" % (sha7, "1 file" if n == 1 else "%d files" % n, branch)

        def replayed(opening, branch, k, tail=""):
            return ("%s — pushed after a replay: origin's %s had moved on, so the run replayed its %d commit(s) onto it%s"
                    % (opening, branch, k, tail))

        def refused_tail(branch, specs, record_path, day):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, rm \"%s\""
                    % (branch, specs, day, branch, specs, day, branch, specs, branch, branch, record_path))

        def other_pushes(r, name, path, body="o\n", branch="main"):
            o = clone(r, name)
            if branch != "main":
                o.git("switch", "-q", branch)
            o.write(path, body)
            o.commit_all("NOISSUE another clone's session file")
            o.git("push", "-q", "origin", branch)
            return o

        def ended(r, env, command="/create-ard"):
            """end on a push origin rejects as non-fast-forward: the next it hands the run."""
            got = run_end(env, command)
            nxt = got.get("next") or {}
            check(got["_rc"] == 0 and " replay --for end --command %s --branch " % command in nxt.get("run", ""),
                  "%s: end hands the rejected push to the replay (%r)" % (os.path.basename(r.path), got))
            return nxt if nxt.get("run") else {"run": "false", "on_timeout": "false"}

        def origin_files(r, branch, prefix):
            p = subprocess.run(["git", "-C", r.bare, "ls-tree", "-r", "--name-only", branch, "--", prefix],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            return set(p.stdout.decode().split())

        def replay_cli(env, for_, command, branch, *more, specs=None):
            return cli("--specs", specs or env["SPECS_PATH"], "replay", "--for", for_, "--command", command,
                       "--branch", branch, *more, env=env)

        def resume_line(specs, command, *args):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "start", "--command", command]
                            + list(args) + ["--resume"])

        def replay_line(specs, command, branch, *more):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "replay", "--for", "start",
                             "--command", command, "--branch", branch] + list(more))

        # r_replayed
        r, env = world(tmp, "r-replayed")
        seed(env, "/create-ard")
        o = other_pushes(r, "r-replayed-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        got = shell(nxt["run"], env)
        h = head(r)
        want = replayed(committed(h[:7], "main"), "main", 1)
        check(got["_rc"] == 0 and got.get("row") == "replayed" and got.get("print") == [want] and got.get("line") == want
              and got.get("sha7") == h[:7] and got.get("files") == 1 and got.get("branch") == "main"
              and got.get("pushed") is True and got.get("record") == "found" and got.get("next") is None
              and got.get("error") is None and {k for k in got if not k.startswith("_")} == END_FIELDS,
              "r_replayed: next.run prints end's object, the replayed and pushed row (%r)" % got)
        check(h != mine and r.git("rev-parse", "HEAD~1") == head(o) and on_origin(r) == h
              and origin_files(r, "main", FEED) == {FEED + "x.md", FEED + "y.md"} and record(env, "/create-ard") is None,
              "r_replayed: origin/main holds both files, the record removed")

        # r_appends: the declined append and the repeated guard block, as end renders them
        r, env = world(tmp, "r-appends")
        seed(env, "/create-ard", declined=["notes.md"], guard_block="BLOCK")
        r.write("notes.md", "n\n")
        other_pushes(r, "r-appends-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        want = (replayed(committed(head(r)[:7], "main"), "main", 1)
                + "; the deliverable at notes.md remains uncommitted, as you asked")
        check(got.get("row") == "replayed" and got.get("print") == [want, "BLOCK"] and got.get("line") == want
              and record(env, "/create-ard") is None, "r_appends: every append end gives (%r)" % got)

        # r_dropped
        r, env = world(tmp, "r-dropped")
        seed(env, "/create-ard")
        o = other_pushes(r, "r-dropped-other", FEED + "x.md", "x\n")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        theirs = head(o)
        want = ("%s — not pushed, and nothing is left to push: origin's main had moved on and already holds every change "
                "main carries, so main now stands on it" % committed(theirs[:7], "main"))
        check(got.get("row") == "already-there" and got.get("print") == [want] and got.get("sha7") == theirs[:7]
              and got.get("pushed") is False and head(r) == theirs and record(env, "/create-ard") is None,
              "r_dropped: the same change on origin is already there, main moved onto it (%r)" % got)
        r, env = world(tmp, "r-dropped-one")
        seed(env, "/create-ard")
        r.write(FEED + "z.md", "z\n")
        r.commit_all("NOISSUE an earlier run's feedback")
        o = other_pushes(r, "r-dropped-one-other", FEED + "x.md", "x\n")
        r.write(FEED + "x.md", "x\n")
        got = shell(ended(r, env)["run"], env)
        h = head(r)
        want = replayed(committed(h[:7], "main"), "main", 2, ", 1 of them already there and dropped")
        check(got.get("row") == "replayed" and got.get("print") == [want] and on_origin(r) == h
              and r.git("rev-parse", "HEAD~1") == head(o), "r_dropped: one of two commits already there, the <D> clause (%r)" % got)

        # r_register_rebuild
        for name, rebuild, clause in (
                ("r-register", None, "both sides changed the security register security/web/, which only a rebuild "
                                     "settles, and this command hands the run no register.py to rebuild it"),
                ("r-register-failed", "fails", "both sides changed the security register security/web/, which only a "
                                               "rebuild settles, and that rebuild failed")):
            r, env = world(tmp, name)
            r.write(REG, '{"findings": []}\n')
            r.commit_all("NOISSUE the register")
            r.git("push", "-q", "origin", "main")
            if rebuild:
                rebuild = os.path.join(tmp, name + "-rebuild.py")
                with open(rebuild, "w", encoding="utf-8") as fh:
                    fh.write("import sys\nsys.exit(1)\n")
            seed(env, "/scan", register_rebuild=rebuild)
            other_pushes(r, name + "-other", REG, '{"findings": ["o"]}\n')
            r.write(REG, '{"findings": ["r"]}\n')
            nxt = ended(r, env, "/scan")
            mine = head(r)
            got = shell(nxt["run"], env)
            want = rejected(committed(mine[:7], "main"), "main", clause, plain(r.path, "main"))
            check(got.get("row") == "rejected" and got.get("print") == [want] and got.get("sha7") == mine[:7]
                  and got.get("pushed") is False and head(r) == mine and on_origin(r) != mine and record(env, "/scan") is None,
                  "r_register_rebuild: %s — push rejected, nothing moved (%r)" % (name, got))

        # r_checked_out: the branch checked out in a second worktree
        r, env = world(tmp, "r-checked-out")
        seed(env, "/create-ard")
        other_pushes(r, "r-checked-out-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        r.git("worktree", "add", "-q", "-f", os.path.join(tmp, "r-checked-out-wt"), "main")
        wt = [w for w in sb.checked_out_at(r.path, "main") if os.path.realpath(w) != os.path.realpath(r.path)]
        got = shell(nxt["run"], env)
        want = rejected(committed(mine[:7], "main"), "main", "another worktree, %s, has main checked out" % wt[0],
                        plain(wt[0], "main"))
        check(len(wt) == 1 and got.get("row") == "rejected" and got.get("print") == [want]
              and "switch" not in got.get("line", "switch") and head(r) == mine,
              "r_checked_out: the remedy runs in that worktree, no switch (%r)" % got)
        r, env = world(tmp, "r-checked-out-queued")
        W, W_FEED = "prd/ACME-4-w", "specifications/PRD-ACME-4-w/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", W)
        r.git("push", "-q", "-u", "origin", W)
        other_pushes(r, "r-checked-out-queued-other", W_FEED + "o.md", branch=W)
        r.write(W_FEED + "w.md", "w\n")
        r.commit_all("NOISSUE w")
        r.git("switch", "-q", "main")
        r.git("worktree", "add", "-q", os.path.join(tmp, "r-checked-out-queued-wt"), W)
        wt = sb.checked_out_at(r.path, W)
        seed(env, "/specify", stage="settle-done", pending=[{"branch": W, "set_upstream": False, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", W)
        want = rejected("Specs preflight: " + W, W, "another worktree, %s, has %s checked out" % (wt[0], W), plain(wt[0], W))
        check(len(wt) == 1 and got["_rc"] == 0 and got.get("print") == [want] and "switch" not in got["print"][0],
              "r_checked_out: on a branch the run is not standing on, still the worktree's remedy (%r)" % got)

        # r_timed_out
        r, env = world(tmp, "r-timed-out")
        seed(env, "/create-ard")
        other_pushes(r, "r-timed-out-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env)
        mine = head(r)
        got = shell(nxt["on_timeout"], env)
        want = rejected(committed(mine[:7], "main"), "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got["_rc"] == 0 and got.get("row") == "rejected" and got.get("print") == [want] and head(r) == mine
              and on_origin(r) != mine and record(env, "/create-ard") is None,
              "r_timed_out: the 420 s clause, nothing replayed, the record removed (%r)" % got)

        # r_not_run: session-branch.py's replay exits 2 with nothing printed
        r, env = world(tmp, "r-not-run")
        GONE = "prd/ACME-9-gone"
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": "abc1234", "files": 2, "branch": GONE,
                                                                 "paths": [], "hook_paths": []})
        got = replay_cli(env, "end", "/create-ard", GONE)
        want = rejected(committed("abc1234", GONE, 2), GONE,
                        "session-branch.py could not run (session-branch: not run (no such branch: %s))" % GONE,
                        plain(r.path, GONE))
        check(got["_rc"] == 0 and got.get("row") == "rejected" and got.get("print") == [want]
              and record(env, "/create-ard") is None, "r_not_run: the could-not-run clause (%r)" % got)

        # r_refused_form: the replay moved the branch and origin refused its push
        r, env = world(tmp, "r-refused")
        r.git("switch", "-q", "-c", PLUGIN)
        r.git("push", "-q", "-u", "origin", PLUGIN)
        seed(env, "/create-prd", branch=PLUGIN)
        other_pushes(r, "r-refused-other", FEED + "y.md", branch=PLUGIN)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(FEED + "x.md", "x\n")
        nxt = ended(r, env, "/create-prd")
        got, days, ldays = dated(lambda: shell(nxt["run"], env))
        h = head(r)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = [["%s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s there, but push "
                 "REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this is recorded and "
                 "no later run pushes it; %s" % (committed(h[:7], PLUGIN), PLUGIN, PLUGIN, PLUGIN,
                                                  refused_tail(PLUGIN, r.path, rec_file, d))] for d in days]
        check(got.get("row") == "moved" and got.get("print") in want and got.get("pushed") is False
              and on_origin(r, PLUGIN) != h and record(env, "/create-prd") is None,
              "r_refused_form: moved, not pushed, in its refused form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays],
              "r_refused_form: the push-refusal record written as step 6 writes it")

        # r_start_current: the current branch's replay in §3.4's flush
        r, env = world(tmp, "r-start-current")
        other_pushes(r, "r-start-current-other", FEED + "y.md")
        r.write(FEED + "x.md", "x\n")
        r.commit_all("NOISSUE Add dev-workflows session artifacts (/specify)")
        args = {"specs": r.path, "keys": ["ACME-1", "ACME-1-01"], "commit_key": "ACME-1", "register_rebuild": None}
        seed(env, "/specify", stage="flush", args=args)
        got = replay_cli(env, "start", "/specify", "main")
        h = head(r)
        resume = resume_line(r.path, "/specify", "--key", "ACME-1", "--key", "ACME-1-01", "--commit-key", "ACME-1")
        check(got["_rc"] == 0 and {k for k in got if not k.startswith("_")} == {"print", "next", "error"}
              and got.get("print") == [replayed("Specs preflight: main", "main", 1)] and got.get("error") is None
              and got.get("next") == {"run": resume, "timeout_ms": 600000, "on_timeout": None} and on_origin(r) == h,
              "r_start_current: the Specs preflight: form, next names start --resume with the start call's args (%r)" % got)
        check((record(env, "/specify") or {}).get("stage") == "settle",
              "r_start_current: the replay advances the record to the settle loop (%r)" % record(env, "/specify"))
        r, env = world(tmp, "r-start-current-timed-out")
        seed(env, "/specify", stage="flush")
        got = replay_cli(env, "start", "/specify", "main", "--timed-out")
        want = rejected("Specs preflight: main", "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got.get("print") == [want] and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify"),
              "r_start_current: rejected on the branch the run stands on, the remedy names no switch (%r)" % got)
        r, env = world(tmp, "r-start-current-timed-out-moved")
        seed(env, "/specify", stage="flush")
        r.git("switch", "-q", "-c", "elsewhere")
        got = replay_cli(env, "start", "/specify", "main", "--timed-out")
        want = rejected("Specs preflight: main", "main", TIMED % ("main", r.path, "main", "main", "main"),
                        plain(r.path, "main"))
        check(got["_rc"] == 0 and got.get("error") is None and got.get("print") == [want]
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify")
              and (record(env, "/specify") or {}).get("stage") == "settle",
              "r_start_current: --timed-out after another session switched the checkout off the branch still prints the "
              "420 s row and goes on to settle (%r)" % got)

        # r_start_queued: two replays the settle loop queued, each naming the next
        r, env = world(tmp, "r-start-queued")
        Y, Z = "prd/ACME-2-y", "prd/ACME-3-z"
        RES_Y, Z_FEED = "specifications/PRD-ACME-2-y/dev-workflows/resume.md", "specifications/PRD-ACME-3-z/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", Y)
        r.write(RES_Y, "r\n")
        r.commit_all("NOISSUE resume")
        r.git("push", "-q", "-u", "origin", Y)
        r.git("switch", "-q", "-c", Z, "main")
        r.git("push", "-q", "-u", "origin", Z)
        o = clone(r, "r-start-queued-other")
        o.git("switch", "-q", Y)
        o.git("rm", "-q", RES_Y)
        o.git("commit", "-q", "-m", "NOISSUE drop the resume pointer")
        o.git("push", "-q", "origin", Y)
        o.git("switch", "-q", Z)
        o.write(Z_FEED + "o.md", "o\n")
        o.commit_all("NOISSUE o")
        o.git("push", "-q", "origin", Z)
        r.git("switch", "-q", Y)
        r.write(RES_Y, "r2\n")
        r.commit_all("NOISSUE resume again")
        mine_y = head(r)
        r.git("switch", "-q", Z)
        r.write(Z_FEED + "z.md", "z\n")
        r.commit_all("NOISSUE z")
        r.git("switch", "-q", "main")
        pending = [{"branch": Y, "set_upstream": False, "standing": "main"},
                   {"branch": Z, "set_upstream": False, "standing": "main"}]
        seed(env, "/specify", stage="settle-done", pending=pending)
        got = replay_cli(env, "start", "/specify", Y)
        p = r.path
        want = rejected("Specs preflight: " + Y, Y,
                        "both sides changed %s, or the folder holding it, and the run cannot settle it" % RES_Y,
                        'run git -C "%s" switch %s, git -C "%s" pull --rebase --no-autostash origin %s and git -C "%s" push '
                        'origin %s, then switch back to main' % (p, Y, p, Y, p, Y))
        nz = replay_line(p, "/specify", Z)
        check(got["_rc"] == 0 and got.get("print") == [want] and got.get("error") is None
              and got.get("next") == {"run": nz, "timeout_ms": 420000, "on_timeout": nz + " --timed-out"}
              and r.git("rev-parse", Y) == mine_y and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_queued: the first replay switches first and back to main after, next names the second (%r)" % got)
        rec = record(env, "/specify") or {}
        check(rec.get("stage") == "settle-done" and rec.get("pending") == pending[1:],
              "r_start_queued: the first branch dropped from pending (%r)" % rec)
        got = shell(nz, env)
        z = r.git("rev-parse", Z)
        check(got["_rc"] == 0 and got.get("print") == [replayed("Specs preflight: " + Z, Z, 1)]
              and got.get("next") == {"run": resume_line(p, "/specify"), "timeout_ms": 600000, "on_timeout": None}
              and on_origin(r, Z) == z and r.git("rev-parse", Z + "~1") == head(o)
              and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_queued: the last replay names start --resume, HEAD still on main (%r)" % got)
        rec = record(env, "/specify") or {}
        check(rec.get("stage") == "disposition" and rec.get("pending") == [],
              "r_start_queued: nothing left pending, the record on to §3.5 (%r)" % rec)
        r, env = world(tmp, "r-start-queued-upstream")
        seed(env, "/specify", stage="settle-done", pending=[{"branch": Y, "set_upstream": False, "standing": "main"},
                                                           {"branch": Z, "set_upstream": True, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", Y, "--timed-out")
        check((got.get("next") or {}).get("run") == replay_line(r.path, "/specify", Z, "--set-upstream"),
              "r_start_queued: the next replay carries --set-upstream where its queue entry does (%r)" % got)

        # r_start_refused: a queued branch's replay moved it, and origin refused the push
        r, env = world(tmp, "r-start-refused")
        V, V_FEED = "prd/ACME-5-v", "specifications/PRD-ACME-5-v/dev-workflows/feedback/"
        r.git("switch", "-q", "-c", V)
        r.git("push", "-q", "-u", "origin", V)
        o = other_pushes(r, "r-start-refused-other", V_FEED + "o.md", branch=V)
        r.write(V_FEED + "v.md", "v\n")
        r.commit_all("NOISSUE v")
        r.git("switch", "-q", "main")
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        seed(env, "/specify", stage="settle-done", pending=[{"branch": V, "set_upstream": False, "standing": "main"}])
        got, days, ldays = dated(lambda: replay_cli(env, "start", "/specify", V))
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", V)
        want = [["Specs preflight: %s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s "
                 "there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this "
                 "is recorded and no later run pushes it; %s" % (V, V, V, V, refused_tail(V, r.path, rec_file, d))]
                for d in days]
        check(got["_rc"] == 0 and got.get("print") in want and got.get("error") is None
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify")
              and r.git("rev-parse", V + "~1") == head(o) and on_origin(r, V) == head(o)
              and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_refused: moved, not pushed, its refused form in Specs preflight: form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() in [d + "\n" for d in ldays]
              and (record(env, "/specify") or {}).get("stage") == "disposition",
              "r_start_refused: the push-refusal record written, the record on to §3.5")

        # r_exit2: nothing found, nothing done
        r, env = world(tmp, "r-exit2")
        got = replay_cli(env, "end", "/create-ard", "main")
        check(one_not_run_line(got) and "_stdout" not in got, "r_exit2: no record is exit 2, one line (%r)" % got)
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main",
                                                                 "paths": [], "hook_paths": []})
        got = cli("--specs", r.path, "replay", "--for", "end", "--command", "/create-ard", "--branch", "main",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"})
        check(one_not_run_line(got), "r_exit2: no session variable is exit 2 (%r)" % got)
        got = replay_cli(env, "end", "/create-ard", "main", specs=os.path.join(r.path, "specifications"))
        check(one_not_run_line(got), "r_exit2: --specs below the top level is exit 2 (%r)" % got)
        for more, what in ((("--for", "middle"), "an unknown --for"), (("--command", "create-ard"), "a command without its slash")):
            args = {"--for": "end", "--command": "/create-ard"}
            args.update(dict(zip(more[::2], more[1::2])))
            got = cli("--specs", r.path, "replay", "--for", args["--for"], "--command", args["--command"], "--branch",
                      "main", env=env)
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
                  "r_exit2: %s is a usage exit 2 (%r)" % (what, got))
        check(((record(env, "/create-ard") or {}).get("end_commit") or {}).get("sha7") == head(r)[:7],
              "r_exit2: the record untouched by every exit 2")

        # r_found: once the record is found, never an exit 2
        r, env = world(tmp, "r-found")
        o = other_pushes(r, "r-found-other", FEED + "y.md")
        base = head(r)
        r.write(FEED + "x.md", "x\n")
        r.commit_all("NOISSUE Add dev-workflows session artifacts (/create-ard)")
        mine = head(r)
        for stage, pending_commit in (("end", {"branch": "main", "base": base, "staged": {FEED + "x.md": "0" * 40}}),
                                      ("end-replay", {"branch": "main", "base": base, "staged": {FEED + "x.md": "0" * 40}}),
                                      ("end", {"sha7": mine[:7], "files": 1, "branch": "main", "paths": [], "hook_paths": []})):
            seed(env, "/create-ard", stage=stage, end_commit=pending_commit)
            got = replay_cli(env, "end", "/create-ard", "main")
            line = got.get("line") or ""
            check(got["_rc"] == 0 and got.get("row") is None and got.get("sha7") is None and "end --resume" in (got.get("error") or "")
                  and got.get("print") == [line] and got.get("record") == "found"
                  and line.startswith("Specs repo: NOT FINISHED — the terminal step stopped early (")
                  and head(r) == mine and on_origin(r) == head(o)
                  and (record(env, "/create-ard") or {}).get("end_commit") == pending_commit,
                  "r_found: end_commit %r at stage %s is no replay's: refused plainly, nothing replayed, no row, the record "
                  "kept for end --resume (%r)" % (pending_commit, stage, got))
        seed(env, "/specify", stage="done")
        got = replay_cli(env, "start", "/specify", "main")
        check(got["_rc"] == 0 and got.get("error") and got.get("next") is None
              and (got.get("print") or [""])[0].startswith("Specs preflight: stopped early (")
              and (record(env, "/specify") or {}).get("stage") == "done",
              "r_found: a start record with no replay pending is refused plainly, the record kept (%r)" % got)
        seed(env, "/specify", stage="settle-done", pending=[{"branch": Z, "set_upstream": False, "standing": "main"}])
        got = replay_cli(env, "start", "/specify", Y)
        check(got["_rc"] == 0 and got.get("error") and (record(env, "/specify") or {}).get("pending") == [
            {"branch": Z, "set_upstream": False, "standing": "main"}],
              "r_found: a branch the record did not queue is refused plainly (%r)" % got)
        seed(env, "/specify", stage="flush")
        got = replay_cli(env, "start", "/specify", Y)
        check(got["_rc"] == 0 and "holds no replay of %s" % Y in (got.get("error") or "") and got.get("next") is None
              and (record(env, "/specify") or {}).get("stage") == "flush" and head(r) == mine,
              "r_found: at flush, a branch HEAD does not stand on is refused plainly, the record kept (%r)" % got)

        # r_canned: classify_replay and the renderer over results no repository here produces
        tip = "b" * 40
        moved = {"moved": True, "pushed": False, "attempts": 1, "replayed": ["a" * 40], "dropped": [], "tip": tip,
                 "porcelain": None, "moves": [], "upstream_error": None, "refused": None}
        rej = "!\trefs/heads/main:refs/heads/main\t[rejected] (fetch first)"
        declined = "!\t%s:refs/heads/main\t[remote rejected] (pre-receive hook declined)" % tip
        locked = "!\t%s:refs/heads/main\t[remote rejected] (failed to lock refs/heads/main)" % tip
        failure = "!\t%s:refs/heads/main\t[remote failure] (remote failed to report status)" % tip
        cm = {"reason": "checkout-moved", "path": None}
        for args, want in (
                ((None, None, False, True), ("rejected", None, "timed-out")),
                ((None, "e", False, False), ("rejected", None, "not-run")),
                ((dict(moved, pushed=True), None, False, False), ("replayed", None, None)),
                ((dict(moved, pushed=True), "e", True, False), ("replayed", None, None)),
                ((dict(moved, moved=False, replayed=[], tip=None, refused={"reason": "conflict", "path": "a"}), None, False,
                  False), ("rejected", None, "conflict")),
                ((dict(moved, replayed=[], dropped=["c" * 40]), None, False, False), ("already-there", None, None)),
                ((dict(moved, moved=False, replayed=[]), None, False, False), ("already-there", None, None)),
                ((dict(moved, porcelain=rej, refused=cm), "e", True, False), ("moved", "stopped", None)),
                ((dict(moved, porcelain=rej, refused=cm), None, False, False), ("moved", "later-refused", "checkout-moved")),
                ((dict(moved, attempts=3, porcelain=rej), None, False, False), ("moved", "moved-on", None)),
                ((dict(moved, porcelain=declined), None, False, False), ("moved", "refused", None)),
                ((dict(moved, porcelain=locked), None, False, False), ("moved", "failed", None)),
                ((dict(moved, porcelain=failure), None, False, False), ("moved", "failed", None)),
                ((moved, None, False, False), ("moved", "failed", None))):
            got = classify_replay(*args)
            check(got == dict(zip(("row", "why", "reason"), want)),
                  "r_canned: classify_replay(%r) is %r (%r)" % (args, want, got))

        f = {"sha7": "abc1234", "files": 2, "branch": "main", "specs": "/s", "default": "main", "standing": "main",
             "register_rebuild": False, "error": None, "preflight": False}

        def render(result, error=None, partial=False, timed_out=False, **facts):
            return _replay_line(lines, classify_replay(result, error, partial, timed_out), result,
                                dict(f, error=error, **facts))

        opening = committed("bbbbbbb", "main", 2) + " — origin's main had moved on, so the run replayed its 1 commit(s) onto it and moved main there, but "
        closing = "; the commits are on local main, and a later run retries the push"
        for result, error, partial, why, what in (
                (dict(moved, porcelain=rej, refused=cm), None, False,
                 "a later attempt could not take origin's newer commits in: the checkout switched to or from main while "
                 "the run was moving it — another session's preflight or handoff, say — so main was not moved again; the "
                 "next run that commits session files on main settles the push itself", "later refused, checkout-moved"),
                (dict(moved, attempts=3, porcelain=rej), None, False, "origin's main moved on again during each of its 3 "
                                                                       "attempts", "moved on"),
                (dict(moved, porcelain=failure), None, False,
                 "the push FAILED ([remote failure] (remote failed to report status))", "failed with a status line"),
                (moved, None, False, "the push FAILED (no status line)", "failed with none"),
                (dict(moved, porcelain=rej), "session-branch: not run (OSError: [Errno 28] No space left on device)", True,
                 "session-branch.py stopped (session-branch: not run (OSError: [Errno 28] No space left on device))",
                 "stopped")):
            got = render(result, error, partial)
            check(got == opening + why + closing, "r_canned: moved, not pushed — %s (%r)" % (what, got))
        pf = dict(branch="prd/A-1-x", standing="prd/A-1-x", reason="pre-receive hook declined")
        got, days, _ = dated(lambda: render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), record="/r",
                                            record_kind="file", record_error=None, **pf))
        check(got in [("%s — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) onto it and moved "
                       "prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push "
                       "of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                       % (committed("bbbbbbb", "prd/A-1-x", 2), refused_tail("prd/A-1-x", "/s", "/r", d))) for d in days],
              "r_canned: the refused form, recorded (%r)" % got)
        got = render(dict(moved, porcelain=declined), record=None, record_kind=None, record_error="e",
                     reason="pre-receive hook declined")
        check(got == ("%s — origin's main had moved on, so the run replayed its 1 commit(s) onto it and moved main there, "
                      "but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of main, but this "
                      "could not be recorded (e, the configuration write's), so a later run pushes main again"
                      % committed("bbbbbbb", "main", 2)), "r_canned: the refused form, unrecorded (%r)" % got)
        got, days, _ = dated(lambda: render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), preflight=True,
                                            sha7=None, files=None, record="/r", record_kind="file", record_error=None, **pf))
        check(got in [("Specs preflight: prd/A-1-x — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) "
                       "onto it and moved prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule "
                       "there takes no push of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                       % refused_tail("prd/A-1-x", "/s", "/r", d)) for d in days],
              "r_canned: the refused form in its Specs preflight: form, recorded (%r)" % got)
        got = render(dict(moved, porcelain=declined), preflight=True, sha7=None, files=None, record=None, record_kind=None,
                     record_error="e", reason="pre-receive hook declined")
        check(got == ("Specs preflight: main — origin's main had moved on, so the run replayed its 1 commit(s) onto it and "
                      "moved main there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push "
                      "of main, but this could not be recorded (e, the configuration write's), so a later run pushes main "
                      "again"), "r_canned: the refused form in its Specs preflight: form, unrecorded (%r)" % got)
        moves = [{"slug": "api", "origin": "f-9", "side": "run", "from": 2, "to": 5},
                 {"slug": "web", "origin": "f-1", "side": "remote", "from": 3, "to": 4},
                 {"slug": "web", "origin": "f-2", "side": "run", "from": 4, "to": 3}]
        got = render(dict(moved, pushed=True, moves=moves, upstream_error="error: could not lock config file"))
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 1,
                              "; the rebuild of security/api/ renumbered [SEC#2] → [SEC#5] (f-9, the local number), and "
                              "the next run that records in that register lists the lines that cite an old number; the "
                              "rebuild of security/web/ renumbered [SEC#3] → [SEC#4] (f-1, origin's number), [SEC#4] → "
                              "[SEC#3] (f-2, the local number), and the next run that records in that register lists the "
                              "lines that cite an old number; its upstream could not be set (error: could not lock config "
                              "file)"), "r_canned: the register clause per slug, run and remote moves, upstream_error (%r)" % got)
        got = render(dict(moved, replayed=[], dropped=["c" * 40], moves=moves[:1]))
        check(got.endswith("so main now stands on it; the rebuild of security/api/ renumbered [SEC#2] → [SEC#5] (f-9, "
                           "the local number), and the next run that records in that register lists the lines that cite "
                           "an old number"), "r_canned: already there with its register clause (%r)" % got)
        got = render(dict(moved, pushed=True, replayed=["a" * 40], dropped=["c" * 40, "d" * 40]))
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 3, ", 2 of them already there and dropped"),
              "r_canned: <K> counts replayed and dropped, <D> the dropped (%r)" % got)
        got = render(dict(moved, pushed=True), "session-branch: not run (OSError: [Errno 28] No space left on device)", True)
        check(got == replayed(committed("bbbbbbb", "main", 2), "main", 1),
              "r_canned: a Partial whose pushed is true is replayed and pushed (%r)" % got)
        nothing = dict(moved, moved=False, replayed=[], tip=None)
        for refused, clause, what in (
                ({"reason": "would-overwrite", "path": "a.md", "paths": ["a.md"]},
                 "moving the checkout would write over a.md, which you changed, left untracked or ignore — once that is "
                 "clear, the next run that commits session files on main settles the push itself", "would-overwrite, one path"),
                ({"reason": "would-overwrite", "path": "a.md", "paths": ["a.md", "b.md", "c.md"]},
                 "moving the checkout would write over a.md and 2 more, which you changed, left untracked or ignore — once "
                 "that is clear, the next run that commits session files on main settles the push itself",
                 "would-overwrite, three paths"),
                ({"reason": "push-scope", "path": "abcdef1234567890"},
                 "the push would now also publish abcdef1, which is not one of this plugin's session-file commits", "push-scope"),
                ({"reason": "in-progress", "path": ".git/MERGE_HEAD"},
                 "a rebase, merge, cherry-pick or revert, or an unresolved conflict, is in progress in the checkout "
                 "(.git/MERGE_HEAD)", "in-progress"),
                ({"reason": "locked", "path": ".git/index.lock"}, ".git/index.lock is held by another git process, or was "
                 "left by one that died, and this plugin never deletes a lock", "locked"),
                ({"reason": "cannot-replay", "path": None}, "this git cannot replay without a checkout (its merge-tree "
                 "needs --write-tree and --merge-base, git 2.40 or later)", "cannot-replay"),
                ({"reason": "fetch-failed", "path": None}, "fetching origin's main failed", "fetch-failed"),
                ({"reason": "branch-moved", "path": None}, "main moved while the run was replaying it", "branch-moved"),
                ({"reason": "cannot-move", "path": None}, "git could not move the checkout onto the replay (a folder it "
                 "cannot write, say), and nothing moved", "cannot-move")):
            got = render(dict(nothing, refused=refused))
            check(got == rejected(committed("abc1234", "main", 2), "main", clause, plain("/s", "main")),
                  "r_canned: push rejected — %s (%r)" % (what, got))
        got = render(dict(nothing, refused={"reason": "register-rebuild", "path": "security/web/"}), register_rebuild=True)
        check("the security register security/web/, which only a rebuild settles, and that rebuild failed; run git" in got,
              "r_canned: register-rebuild where the call carried a rebuild (%r)" % got)
        got = render(None, "session-branch: not run (no such branch: main)")
        check(got == rejected(committed("abc1234", "main", 2), "main", "session-branch.py could not run (session-branch: "
                              "not run (no such branch: main))", plain("/s", "main")),
              "r_canned: an exit 2 with nothing on stdout (%r)" % got)
        cm_clause = ("the checkout switched to or from main while the run was moving it — another session's preflight or "
                     "handoff, say — so main was not moved; the next run that commits session files on main settles the "
                     "push itself")
        got = render(dict(nothing, refused=cm))
        check(got == rejected(committed("abc1234", "main", 2), "main", cm_clause, None),
              "r_canned: checkout-moved ends at its reason clause, no remedy (%r)" % got)
        got = render(dict(nothing, refused=cm), preflight=True, standing="prd/A-1-x", sha7=None, files=None)
        check(got == rejected("Specs preflight: main", "main", cm_clause, None),
              "r_canned: checkout-moved names no remedy on a branch the run is not standing on either (%r)" % got)
        got = render(dict(nothing, refused={"reason": "fetch-failed", "path": None}), preflight=True, branch="prd/A-1-x",
                     standing="main", sha7=None, files=None)
        check(got == rejected("Specs preflight: prd/A-1-x", "prd/A-1-x", "fetching origin's prd/A-1-x failed",
                              'run git -C "/s" switch prd/A-1-x, git -C "/s" pull --rebase --no-autostash origin prd/A-1-x '
                              'and git -C "/s" push origin prd/A-1-x, then switch back to main'),
              "r_canned: a branch the run is not standing on, switched to first and back after (%r)" % got)
        got = render(dict(moved, attempts=2, porcelain=rej), preflight=True, sha7=None, files=None)
        check(got == "Specs preflight: main — origin's main had moved on, so the run replayed its 1 commit(s) onto it and "
                     "moved main there, but origin's main moved on again during each of its 2 attempts" + closing,
              "r_canned: moved, not pushed, in its Specs preflight: form (%r)" % got)

        # r_in_process: session-branch.py's replay in process, its exits read as its main() prints them
        real_replay = sb.replay

        def raising(e):
            def replay(*args, **kw):
                raise e
            return replay

        try:
            sb.replay = raising(sb.Partial("OSError: [Errno 28] No space left on device", dict(moved, pushed=True)))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (dict(moved, pushed=True), "session-branch: not run (OSError: [Errno 28] No space left on device)",
                          True), "r_in_process: a Partial is its result, its stderr line and partial (%r)" % (got,))
            sb.replay = raising(sb.Partial("git push ended by signal 15", dict(moved, pushed=True)))
            try:
                got = _run_replay("/x", "main", None, False, False)
            except _Ended as e:
                got = ("ended", e.signum)
            check(got == ("ended", 15), "r_in_process: a Partial a signal ended is no outcome: _Ended (%r)" % (got,))
            sb.replay = raising(NotRun("no such branch:\n  main"))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (None, "session-branch: not run (no such branch: main)", False),
                  "r_in_process: a NotRun is nothing printed and its one stderr line (%r)" % (got,))
            sb.replay = raising(RuntimeError("boom"))
            got = _run_replay("/x", "main", None, False, False)
            check(got == (None, "session-branch: not run (RuntimeError: boom)", False),
                  "r_in_process: any other exception as main() prints it (%r)" % (got,))
            sb.replay = raising(AssertionError("called"))
            check(_run_replay("/x", "main", None, False, True) == (None, None, False),
                  "r_in_process: --timed-out runs no replay")
        finally:
            sb.replay = real_replay

        # r_signalled: a replay a signal ended -- the harness's, at its 420 s -- is no outcome: nothing is printed or
        # recorded, the process ends by that signal, and the --timed-out call that follows finds the record intact
        def caused(e, cause):
            e.__cause__ = cause
            return e

        def record_bytes(env, command):
            with in_env(env):
                try:
                    with open(state.path(env["CLAUDE_CODE_SESSION_ID"], command), "rb") as fh:
                        return fh.read()
                except OSError:
                    return None

        class Exited(BaseException):
            pass

        def exits(signum):
            raise Exited(signum)

        endings = (("git_bounded's NotRun", NotRun("git fetch ended by signal 15"), 15),
                   ("replay's NotRun from _Signalled", caused(NotRun("ended by signal 15"), sb._Signalled(15)), 15),
                   ("a Partial from git_bounded's NotRun", caused(sb.Partial("git push ended by signal 15",
                                                                             dict(moved, pushed=False)),
                                                                  NotRun("git push ended by signal 15")), 15),
                   ("a Partial from _Signalled", caused(sb.Partial("ended by signal 1", dict(moved, pushed=True)),
                                                        sb._Signalled(1)), 1))
        g = globals()
        real_exit = g["_exit_by"]
        g["_exit_by"] = exits
        try:
            for k, (what, ending, signum) in enumerate(endings):
                for for_, command, fields in (
                        ("end", "/create-ard", {"stage": "end-replay"}),
                        ("start", "/specify", {"stage": "flush", "args": {"specs": None, "keys": ["ACME-1"],
                                                                          "commit_key": None, "register_rebuild": None}})):
                    r, env = world(tmp, "r-signalled-%d-%s" % (k, for_))
                    fields = dict(fields, end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main", "paths": [],
                                                      "hook_paths": []})
                    if for_ == "start":
                        fields["args"] = dict(fields["args"], specs=r.path)
                    seed(env, command, **fields)
                    before, h = record_bytes(env, command), head(r)
                    sb.replay = raising(ending)
                    got = None
                    try:
                        with in_env(env):
                            replay(r.path, for_, command, "main")
                    except Exited as e:
                        got = e.args[0]
                    finally:
                        sb.replay = real_replay
                    check(got == signum and record_bytes(env, command) == before and head(r) == h,
                          "r_signalled: %s, --for %s — ends by signal %d, the record as it stood (%r)"
                          % (what, for_, signum, got))
                    if k:
                        continue
                    got = replay_cli(env, for_, command, "main", "--timed-out")
                    timed = TIMED % ("main", r.path, "main", "main", "main")
                    if for_ == "end":
                        check(got.get("row") == "rejected" and got.get("print") == [rejected(committed(h[:7], "main"),
                              "main", timed, plain(r.path, "main"))] and record_bytes(env, command) is None,
                              "r_signalled: then --timed-out prints the 420 s row and removes the record (%r)" % got)
                    else:
                        check(got.get("print") == [rejected("Specs preflight: main", "main", timed, plain(r.path, "main"))]
                              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify", "--key", "ACME-1")
                              and (record(env, command) or {}).get("stage") == "settle",
                              "r_signalled: then --timed-out prints the 420 s row, the record on to settle (%r)" % got)
        finally:
            g["_exit_by"] = real_exit
            sb.replay = real_replay
        r, env = world(tmp, "r-signalled-pin")
        sb._pending.append(signal.SIGTERM)
        try:
            sb.git_bounded(r.path, 5, "status")
            pinned = None
        except NotRun as e:
            pinned = _signal_of(e)
        finally:
            del sb._pending[:]
        check(pinned == signal.SIGTERM, "r_signalled: _signal_of reads git_bounded's own words for the signal (%r)" % pinned)
        check(_signal_of(caused(NotRun("stopped"), sb._Signalled(2))) == 2
              and _signal_of(caused(sb.Partial("stopped", {}), sb._Signalled(1))) == 1,
              "r_signalled: a _Signalled cause is read by its type, whatever the words")
        check(_signal_of(NotRun("git fetch --no-tags: error: ended by signal 15")) is None
              and _signal_of(RuntimeError("ended by signal 15")) is None and _signal_of(NotRun("no such branch: x")) is None,
              "r_signalled: an error that only mentions the words is an outcome")

        # r_signalled_child: a real SIGTERM inside the replay's fetch, in a child process
        r, env = world(tmp, "r-signalled-child")
        marker = os.path.join(tmp, "r-signalled-child.fetching")
        r.git("config", "protocol.ext.allow", "always")
        r.git("remote", "set-url", "origin", "ext::sh -c touch%% %s;sleep%% 60" % marker)
        seed(env, "/create-ard", stage="end-replay", end_commit={"sha7": head(r)[:7], "files": 1, "branch": "main",
                                                                 "paths": [], "hook_paths": []})
        before = record_bytes(env, "/create-ard")
        p = subprocess.Popen([sys.executable, me, "--specs", r.path, "replay", "--for", "end", "--command", "/create-ard",
                              "--branch", "main"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=dict(os.environ, **env))
        deadline = time.monotonic() + 30
        while not os.path.exists(marker) and p.poll() is None and time.monotonic() < deadline:
            time.sleep(0.05)
        reached = os.path.exists(marker)
        p.send_signal(signal.SIGTERM)
        try:
            out, err = p.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            p.kill()
            out, err = p.communicate()
        check(reached and p.returncode == -signal.SIGTERM and out == b"" and err == b""
              and record_bytes(env, "/create-ard") == before,
              "r_signalled_child: SIGTERM during the fetch ends the call by it, nothing printed, the record intact "
              "(reached %r, rc %r, out %r, err %r)" % (reached, p.returncode, out[:200], err[:300]))

    def scenarios_start(tmp):
        state, lines = _flow()
        T = lines.T
        g = globals()
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        SPEC = "spec/ACME-1-01-x"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        FIELDS = {"print", "next", "specs_git", "gate", "default", "default_ref", "remote", "offline", "offline_clause",
                  "session_branch", "mode", "guard", "branch", "b2_left", "b4_left", "stay", "start_dirty", "midrun",
                  "started", "replaced", "error"}
        STAY = lines.placeholder("pre.stay", "<switched")

        def run_start(env, command, *args, specs=None, cwd=None):
            return cli("--specs", env["SPECS_PATH"] if specs is None else specs, "start", "--command", command, *args,
                       env=env, cwd=cwd)

        def fields(got):
            return {k for k in got if not k.startswith("_")} == FIELDS

        def follow(got, env):
            """got, then each call the one before it names as next, run as the skill runs it, until one names none."""
            seen = [got]
            while (seen[-1].get("next") or {}).get("run") and len(seen) < 12:
                seen.append(shell(seen[-1]["next"]["run"], env))
            return seen

        def resume_line(specs, command, *args):
            return " ".join(["python3", shlex.quote(me), "--specs", shlex.quote(specs), "start", "--command", command]
                            + list(args) + ["--resume"])

        def subject(r):
            return r.git("log", "-1", "--format=%s")

        def rev(r, branch):
            return r.git("rev-parse", "--verify", "-q", "refs/heads/" + branch, check=False) or None

        def ff_merged(r, name, branch, path):
            """<branch>, cut from r's main with one commit adding <path> and pushed with -u, fast-forward-merged into
            origin's main by another clone; r is left on <branch>, its own main behind origin's."""
            r.git("switch", "-q", "-c", branch, "main")
            r.write(path, "x\n")
            r.commit_all("work on " + branch)
            r.git("push", "-q", "-u", "origin", branch)
            o = clone(r, name)
            o.git("merge", "-q", "--ff-only", "origin/" + branch)
            o.git("push", "-q", "origin", "main")
            return o

        def squash_merged(r, name, branch, path):
            """<branch>, cut from r's main with one commit adding <path>, never pushed; another clone lands the same
            change on origin's main as a commit of its own."""
            r.git("switch", "-q", "-c", branch, "main")
            r.write(path, "s\n")
            r.commit_all("work on " + branch)
            o = clone(r, name)
            o.write(path, "s\n")
            o.commit_all("work on %s, squashed" % branch)
            o.git("push", "-q", "origin", "main")
            return o

        def session_commit(r, branch, prd, command="/feedback", name="f.md"):
            """A session-file commit on <branch>, unpushed."""
            r.git("switch", "-q", branch)
            r.write("specifications/%s/dev-workflows/feedback/%s" % (prd, name), name + "\n")
            r.commit_all(SUBJECT % ("NOISSUE", command))

        def refusal_file(r, branch):
            path = os.path.join(r.path, ".git", "workflows", "push-refused", branch)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("2026-11-01\n")
            return path

        def updates(r, branch):
            """How many times origin's <branch> was written (the bare's reflog, core.logAllRefUpdates on)."""
            p = subprocess.run(["git", "-C", r.bare, "reflog", "show", "refs/heads/" + branch], stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
            return len(p.stdout.decode().splitlines())

        def pushed_default(sha7, specs):
            return ("Specs repo: committed %s (1 file) on main — pushed straight to main, and no pull request was opened: "
                    "this plugin lands its session files there without review; to land them through a pull request of your "
                    "own instead, turn on session-branch mode (§8) with git -C \"%s\" config workflows.sessionBranch true"
                    % (sha7, specs))

        # The landing's pieces (specs-repo-git §4 step 1, §6): the row a landing's commit on main takes once pushed with
        # app.landed, G1's plain block, its §5 forms, and the stay the record holds.
        KINDS = lines.placeholder("g1.landing.not_done", "<which no key")
        LANDED = lines.placeholder("app.landed", "<which no key")

        def lacks_row(r, branch):
            """origin-lacks' line for HEAD's one-file commit on <branch>, a plugin branch origin does not have."""
            return lines.fill("row.origin-lacks", {"<sha7>": head(r)[:7], "<N>": 1, "<branch>": branch,
                                                   "<SPECS_PATH>": r.path})

        def plugin_row(r, branch):
            return "Specs repo: committed %s (1 file) on %s — pushed" % (head(r)[:7], branch)

        def landed_row(r, n, branch, kind="merged"):
            """pushed-default's line for the landing's commit, main's tip, of <n> files, then app.landed for a stay of
            <kind> (STAY_KINDS) on <branch>."""
            sha7 = (r.git("rev-parse", "--verify", "-q", "refs/heads/main", check=False) or "")[:7]
            return (pushed_default(sha7, r.path).replace("(1 file)", "(1 file)" if n == 1 else "(%d files)" % n)
                    + lines.fill("app.landed", {"<branch>": branch, "<default>": "main", LANDED: STAY_KINDS.index(kind)}))

        def g1_plain(r, paths):
            return lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": len(paths),
                                     "<path list>": [", ".join(paths), " ".join(shlex.quote(p) for p in paths)]})

        def g1_form(r, paths, not_done, fix, if_ignored):
            """G1's block for <paths> in one of §5's forms, rendered from the pins and never by the code it checks: the
            plain block's header and Found part, then <not_done>, <fix> (None: the plain block's Fix part) and
            <if_ignored>, each on its one line after its label's padding."""
            rows = g1_plain(r, paths).split("\n")
            at = {label: next(k for k, row in enumerate(rows) if row.startswith(label))
                  for label in ("Not done:", "Fix:", "If ignored:")}
            fixed = rows[at["Fix:"]:at["If ignored:"]] if fix is None else [("Fix:      " + fix).rstrip()]
            return "\n".join(rows[:at["Not done:"]] + ["Not done: " + not_done] + fixed + ["If ignored: " + if_ignored])

        def merged_fix(r, paths):
            return lines.fill("g1.merged.fix", {"<SPECS_PATH>": r.path, "<default>": "main",
                                                "<path list>": " ".join(shlex.quote(p) for p in paths)})

        def g1_landing(r, paths, branch, kind):
            """G1's landing form (§5) at the start, for a stay of <kind> (STAY_KINDS) on <branch>: merged's Fix and If
            ignored where the stay's merged flag is set -- here, kind merged -- else the plain Fix and
            g1.landing.if_ignored."""
            v = {"<default>": "main", "<branch>": branch, KINDS: STAY_KINDS.index(kind)}
            if kind == "merged":
                return g1_form(r, paths, lines.fill("g1.landing.not_done", v), merged_fix(r, paths),
                               lines.fill("g1.merged.if_ignored", v))
            return g1_form(r, paths, lines.fill("g1.landing.not_done", v), None, T["g1.landing.if_ignored"])

        def g1_uncommitted(block):
            """G1's plain <block> as end repeats it after a line that committed none of the run's files (§5): the
            not-committed form, its Not done g1.not_done.uncommitted and If ignored g1.if_ignored.uncommitted, each on
            one line, its Fix as it is."""
            rows = block.split("\n")
            i = next(k for k, row in enumerate(rows) if row.startswith("Not done:"))
            j = i + 1
            while j < len(rows) and rows[j].startswith(" "):
                j += 1
            k = next(x for x, row in enumerate(rows) if row.startswith("If ignored:"))
            return "\n".join(rows[:i] + ["Not done: " + T["g1.not_done.uncommitted"]] + rows[j:k]
                             + ["If ignored: " + T["g1.if_ignored.uncommitted"]])

        def g1_unlanded(r, paths, branch, kind):
            """G1's landing form as end repeats it after a landing that did not land the run's whole change (§5): its
            Not done g1.landing.not_done.unlanded, its Fix and If ignored the landing form's."""
            v = {"<default>": "main", "<branch>": branch, KINDS: STAY_KINDS.index(kind)}
            whole = g1_landing(r, paths, branch, kind).split("\n")
            k = next(i for i, row in enumerate(whole) if row.startswith("Not done:"))
            return "\n".join(whole[:k] + ["Not done: " + lines.fill("g1.landing.not_done.unlanded", v)] + whole[k + 1:])

        def stayed(branch, reason, kind="merged", merged=True):
            return {"branch": branch, "kind": kind, "reason": reason, "merged": merged, "command": None}

        def stay_of(env, command="/feedback"):
            return (record(env, command) or {}).get("stay")

        def untracked(r, path):
            return "?? " + path in r.git("status", "--porcelain", "--untracked-files=all")

        # t_stay_keys_none (in process, first, since the key list it pins is B3's and B4's too, which every start
        # below reads): with no commit key, and an extra key that is None, nothing None reaches branch_key; a key
        # given beside them still resolves the branch
        B = "prd/B-2-y"
        rec = state.new("/feedback", session="t-stay-keys-none", default="main", mode="off", keys=["ACME-1"])
        try:
            kind_of = g["_stay_kind"]
            got = [kind_of(rec, B, False), kind_of(rec, B, False, extra_keys=(None,)),
                   kind_of(rec, B, False, extra_keys=("B-2",)), kind_of(dict(rec, commit_key="B-2"), B, False),
                   kind_of(rec, B, True), kind_of(rec, "main", True), kind_of(rec, "feature/x", False),
                   kind_of(dict(rec, mode="on"), B, True), kind_of(dict(rec, specs_git="misrooted"), B, True),
                   kind_of(rec, None, True)]
        except Exception as e:
            got = "%s: %s" % (type(e).__name__, e)
        check(got == ["unkeyed", "unkeyed", None, None, "merged", None, None, None, None, None],
              "t_stay_keys_none: _stay_kind's kinds, and no None reaching branch_key (%r)" % (got,))

        # t_clean
        r, env = world(tmp, "t-clean")
        got = run_start(env, "/feedback")
        line = env_line(r.path)
        check(got["_rc"] == 0 and fields(got) and got.get("print") == [line] and got.get("specs_git") is None
              and got.get("gate") == "pass" and got.get("default") == "main" and got.get("default_ref") == "origin/main"
              and got.get("remote") == "origin" and got.get("offline") is False and got.get("offline_clause") is None
              and got.get("branch") == "main" and got.get("guard") is None and got.get("next") is None
              and got.get("mode") == "off" and got.get("replaced") is None and got.get("error") is None,
              "t_clean: the Environment line alone, on main, nothing to do (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("stage") == "done" and rec.get("env_line") == line and rec.get("branch") == "main"
              and rec.get("args") == {"specs": r.path, "keys": [], "commit_key": None, "register_rebuild": None},
              "t_clean: the record saved at stage done, with the call's arguments (%r)" % rec)

        # t_unset
        got = run_start(env, "/feedback", specs="")
        check(got["_rc"] == 0 and fields(got) and got.get("print") == [env_line("")] and "SPECS_PATH=unset" in got["print"][0]
              and got.get("gate") == "unset" and got.get("default") is None and got.get("branch") is None
              and got.get("next") is None and got.get("error") is None,
              "t_unset: the Environment line naming SPECS_PATH=unset, nothing else (%r)" % got)
        check((record(env, "/feedback") or {}).get("stage") == "done", "t_unset: a record saved")

        # t_misrooted
        r, env = world(tmp, "t-misrooted")
        r.write("specs/specifications/PRD-A-1-x/prd.md", "---\nkind: prd\nkey: A-1\n---\n")
        r.commit_all("a specs tree inside a larger repository")
        r.git("push", "-q", "origin", "main")
        ff_merged(r, "t-misrooted-other", "prd/A-1-x", "specs/specifications/PRD-A-1-x/ard.md")
        mine = "specs/specifications/PRD-A-1-x/dev-workflows/resume.md"
        r.write(mine, "r\n")
        specs = os.path.join(r.path, "specs")
        below = lines.fill("pre.below-top", {"<value>": specs, "<top>": r.git("rev-parse", "--show-toplevel")})
        h = head(r)
        got = run_start(env, "/feedback", specs=specs)
        want = lines.fill("pre.stay", {"<branch>": "prd/A-1-x", "<default>": "main", STAY: 0})
        check(got.get("print") == [env_line(specs), below, want] and got.get("specs_git") == "misrooted"
              and got.get("branch") == "prd/A-1-x" and head(r) == h
              and "?? " + mine in r.git("status", "--porcelain", "--untracked-files=all"),
              "t_misrooted: the below-top notice and pre.stay's merged variant, no switch, nothing committed (%r)" % got)
        check((record(env, "/feedback") or {}).get("misrooted_notice") == [below],
              "t_misrooted: the notice saved for end to repeat")
        r.git("switch", "-q", "-c", "prd/B-2-y", "main")
        r.write("specs/specifications/PRD-B-2-y/prd.md", "b\n")
        r.commit_all("B-2 Add the PRD")
        h = head(r)
        got = run_start(env, "/feedback", "--key", "A-1", specs=specs)
        want = lines.fill("pre.stay", {"<branch>": "prd/B-2-y", "<default>": "main", STAY: 1})
        check(got.get("print") == [env_line(specs), below, want] and got.get("branch") == "prd/B-2-y" and head(r) == h,
              "t_misrooted: an unmerged branch no key names gets the unkeyed variant (%r)" % got)

        # t_offline
        r, env = world(tmp, "t-offline")
        r.git("remote", "set-url", "origin", os.path.join(tmp, "t-offline-gone.git"))
        got = run_start(env, "/feedback")
        check(got["_rc"] == 0 and got.get("offline") is True
              and got.get("offline_clause") == "offline — ancestry checked against the last-fetched ref"
              and got.get("print") == [env_line(r.path)] and got.get("default_ref") == "origin/main"
              and got.get("error") is None, "t_offline: carried, not printed (%r)" % got)

        # t_g0
        r, env = world(tmp, "t-g0")
        r.git("switch", "-q", "--detach", "HEAD")
        r.write(RESUME, "r\n")
        h = head(r)
        got, days, _ = dated(lambda: run_start(env, "/feedback"))
        blocks = [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                  for d in days]
        block = next((b for b in blocks if got.get("print") == [env_line(r.path), b]), blocks[-1])
        check(got.get("print") == [env_line(r.path), block] and got.get("specs_git") == "blocked" and got.get("guard") == "G0"
              and got.get("branch") is None and head(r) == h,
              "t_g0: a detached HEAD prints G0's block and sets blocked (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("guard_block") == block and rec.get("stage") == "done", "t_g0: the block saved for end (%r)" % rec)

        # t_g1: a plugin branch cut at main's tip holds nothing of its own, so branch-merged reads it merged and G1 takes
        # its landing form (§5), merged's alternative; t_land_merged_b3_g1 below has the plain block on an unmerged branch
        r, env = world(tmp, "t-g1")
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("notes.md", "n\n")
        r.write("my notes.md", "m\n")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_start(env, "/feedback")
        block = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 2,
                                  "<path list>": ["my notes.md, notes.md", "'my notes.md' notes.md"]})
        shown = (got.get("print") or ["", ""])[-1]
        check(got.get("print") == [env_line(r.path),
                                   g1_landing(r, ["my notes.md", "notes.md"], "prd/ACME-9-q", "merged")]
              and block == g1_plain(r, ["my notes.md", "notes.md"]) and got.get("guard") == "G1"
              and got.get("specs_git") is None and got.get("branch") == "prd/ACME-9-q" and head(r) == h
              and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all")
              and "artifact area: my notes.md, notes.md\n" in shown and "add 'my notes.md' notes.md &&" in shown,
              "t_g1: the block lists the paths, comma-separated, then shell-quoted; no flush, no switch (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("guard_paths") == ["my notes.md", "notes.md"] and rec.get("guard_block") == block
              and rec.get("stay") == stayed("prd/ACME-9-q", "g1"),
              "t_g1: the paths saved as guard_paths, the plain block saved, the stay recorded (%r)" % rec)

        # t_g2, t_g2_implement
        r, env = world(tmp, "t-g2")
        r.git("switch", "-q", "-c", "feature/x")
        plain = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), plain] and got.get("guard") == "G2" and got.get("branch") == "feature/x",
              "t_g2: G2's block naming main (%r)" % got)
        implement = (
            "⚠ SPECS REPO — ON A BRANCH THIS PLUGIN DID NOT CREATE\n\n"
            "Found:    %s is on branch `feature/x`, which is neither the default\n"
            "          branch (`main`) nor a plugin branch (idea/ prd/ ard/ spec/\n"
            "          epics/ design/ ready/ brd/ frames/ kb/ conformance/).\n"
            "Not done: the preflight did not switch away from it — the plugin manages only branches it created. This run "
            "changes code here, so its artifacts WILL be committed on the branch it cuts for that, or, if it stops first, on "
            "the branch it then stands on — feature/x, or main after a fresh start — and not pushed unless that branch is "
            "main or its name carries one of this plugin's prefixes.\n"
            "Fix:\n"
            "If ignored: nothing is to be run here: the artifacts stay on that branch until it is pushed or merged, and "
            "reach the maintainer then." % r.path)
        got = run_start(env, "/implement", cwd=os.path.join(r.path, "specifications"))
        check(got.get("print") == [env_line(r.path), implement] and got.get("guard") == "G2",
              "t_g2_implement: /implement from inside the specs work tree gets the direct-run lines (%r)" % got)
        got = run_start(env, "/implement", cwd=tmp)
        check(got.get("print") == [env_line(r.path), plain], "t_g2_implement: /implement run from elsewhere gets the plain block")

        # t_catch_up
        r, env = world(tmp, "t-catch-up")
        o = clone(r, "t-catch-up-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
        o.git("push", "-q", "origin", "main")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and head(r) == head(o) and got.get("branch") == "main",
              "t_catch_up: fast-forwarded silently (%r)" % got)

        # t_catch_up_failed: origin unreachable once the fetch has run
        r, env = world(tmp, "t-catch-up-failed")
        o = clone(r, "t-catch-up-failed-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/feedback"))
        o.git("push", "-q", "origin", "main")
        h, line = head(r), env_line(r.path)
        real_resolve = g["resolve_default"]

        def then_gone(root, fetch):  # once the fetch has run: the snapshot's read before it fetches nothing
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-catch-up-failed-gone.git"))
            return out

        g["resolve_default"] = then_gone
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[0] == line and shown[1].startswith("Specs preflight: could not fast-forward main (")
              and shown[1].endswith("); the run goes on from it as it stands") and head(r) == h and got.get("error") is None,
              "t_catch_up_failed: pre.pull-failed, the run going on from main as it stands (%r)" % got)

        # t_flush
        r, env = world(tmp, "t-flush")
        r.write(RESUME, "r\n")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and "Co-Authored-By" not in r.git("log", "-1", "--format=%B") and on_origin(r) == head(r)
              and r.git("status", "--porcelain") == "", "t_flush: committed and pushed, silent (%r)" % got)
        r.write(RESUME, "r2\n")
        got = run_start(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("print") == [env_line(r.path)] and subject(r) == SUBJECT % ("ACME-1", "/feedback")
              and on_origin(r) == head(r), "t_flush: --commit-key opens the subject (%r)" % got)

        # t_flush_locked
        r, env = world(tmp, "t-flush-locked")
        r.write(RESUME, "r\n")
        h = head(r)
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_start(env, "/feedback")
        os.remove(lock)
        check(got.get("print") == [env_line(r.path), "Specs preflight: skipped — another session holds the repo "
                                   "(index.lock); the next run picks the artifacts up"] and head(r) == h,
              "t_flush_locked: the Locked row in its Specs preflight: form (%r)" % got)

        # t_flush_locked_b4: a Locked flush leaves the session file dirty, and B4's switch, refused under the index.lock,
        # stops the call with rule 5's line
        r, env = world(tmp, "t-flush-locked-b4")
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        r.write(RESUME, "r\n")
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        got = run_start(env, "/feedback")
        os.remove(lock)
        shown = got.get("print") or []
        check(got["_rc"] == 0 and len(shown) == 3 and shown[1] == "Specs preflight: skipped — another session holds the "
              "repo (index.lock); the next run picks the artifacts up"
              and shown[2].startswith("Specs preflight: stopped early (git switch main: fatal: Unable to create '")
              and shown[2].endswith(" — what it did is above, and the next run's preflight goes on from where this one "
                                    "stands") and (got.get("error") or "").startswith("git switch main: ")
              and got.get("branch") == "prd/ACME-9-q" and (record(env, "/feedback") or {}).get("stage") == "disposition",
              "t_flush_locked_b4: B4's refused switch ends the call on pre.stopped, nothing moved (%r)" % got)

        # t_flush_commit_failed
        r, env = world(tmp, "t-flush-commit-failed")
        hook(os.path.join(r.path, ".git", "hooks", "pre-commit"), "echo hook says no >&2\nexit 1\n")
        r.write(RESUME, "r\n")
        h = head(r)
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: NOT COMMITTED — the commit failed (hook says no); the "
                                   "artifacts stay staged, and a later run commits them once git accepts the commit (a "
                                   "merge concluded, a hook satisfied)"] and head(r) == h,
              "t_flush_commit_failed: the Commit failed row in its Specs preflight: form (%r)" % got)

        # t_flush_refused: origin's pre-receive hook refuses the flush's push, on a plugin branch the run stays on
        r, env = world(tmp, "t-flush-refused")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.git("push", "-q", "-u", "origin", PLUGIN)
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "exit 1\n")
        r.write(RESUME, "r\n")
        got, days, _ = dated(lambda: run_start(env, "/feedback", "--key", "ACME-1"))
        p, rec_file = r.path, os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = [[env_line(p), "Specs preflight: %s not pushed — origin refused it (pre-receive hook declined), and this is "
                 "recorded so no later run pushes it; to land the commits on local %s, put them on a branch of their own and "
                 "open a pull request from it — git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin "
                 "session-files-%s — then, standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes "
                 "to %s again, rm \"%s\"" % (PLUGIN, PLUGIN, p, d, PLUGIN, p, d, PLUGIN, p, PLUGIN, PLUGIN, rec_file)]
                for d in days]
        check(got.get("print") in want and os.path.isfile(rec_file) and on_origin(r, PLUGIN) != head(r)
              and got.get("branch") == PLUGIN, "t_flush_refused: the refusal in its Specs preflight: form, recorded (%r)" % got)

        # t_flush_failed: origin unreachable once the fetch has run, so the flush's push fails
        r, env = world(tmp, "t-flush-failed")
        r.write(RESUME, "r\n")
        line = env_line(r.path)

        def then_gone_too(root, fetch):
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-flush-failed-gone.git"))
            return out

        g["resolve_default"] = then_gone_too
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[0] == line and shown[1].startswith("Specs preflight: main — push FAILED (fatal: ")
              and shown[1].endswith("); the commit is local and a later run retries it")
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and got.get("error") is None,
              "t_flush_failed: push FAILED in its Specs preflight: form, git's reason (%r)" % got)

        # t_preflight_forms (canned): the unrecorded refusal, and a push the cap ended
        got = _refused_line(lines, "/s", PLUGIN, "main", {"reason": "a rule", "recorded": None, "record": None,
                                                          "record_error": "error: could not lock config file"})
        check(got == "Specs preflight: %s not pushed — origin refused it (a rule), and this could not be recorded (error: "
                     "could not lock config file), so a later run pushes it again" % PLUGIN,
              "t_preflight_forms: the unrecorded refusal names no remedy (%r)" % got)
        got = lines.preflight_form(_row_line(lines, "failed", {"sha7": "-", "files": 0, "branch": "main",
                                                               "reason": T["text.push-capped"]}))
        check(got == "Specs preflight: main — push FAILED (the push did not finish within 60 s); the commit is local and a "
                     "later run retries it", "t_preflight_forms: a capped push's reason (%r)" % got)

        # t_retry
        r, env = world(tmp, "t-retry")
        r.write(RESUME, "r\n")
        r.commit_all(SUBJECT % ("NOISSUE", "/specify"))
        h = head(r)
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path)] and on_origin(r) == h and head(r) == h,
              "t_retry: an earlier run's unpushed session commit pushed, silent (%r)" % got)

        # t_merged_leave
        A = "prd/A-1-x"
        RES_A = "specifications/PRD-A-1-x/dev-workflows/resume.md"
        r, env = world(tmp, "t-merged-leave")
        ff_merged(r, "t-merged-leave-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write(RES_A, "r\n")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"]
              and got.get("branch") == "main" and got.get("b2_left") == A and rev(r, A) is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A,
              "t_merged_leave: switched to main, the branch deleted, the flush on main (%r)" % got)
        r, env = world(tmp, "t-merged-leave-refused")
        r.write(RES_A, "main's\n")
        r.commit_all("NOISSUE a resume pointer on main")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "-c", A)
        r.write(RES_A, "the branch's\n")
        r.commit_all("A-1 work")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "t-merged-leave-refused-other")
        o.git("merge", "-q", "--ff-only", "origin/" + A)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", A)
        r.write(RES_A, "dirty\n")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = got.get("print") or []
        flushed = lines.fill("pre.merged-flush", {"<branch>": A, "<sha7>": head(r)[:7], "<default>": "main",
                                                  "<SPECS_PATH>": r.path})
        check(len(shown) == 3 and shown[0] == env_line(r.path)
              and shown[1].startswith("Specs preflight: could not switch from merged prd/A-1-x to main (error: ")
              and shown[2] == flushed and got.get("branch") == A and got.get("b2_left") is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r, A) is None,
              "t_merged_leave: a refused switch is reported, the flush on the branch, the cherry-pick line (%r)" % got)

        # t_merged_leave_kept (in process): the leave's pull fails, so -d keeps the branch; the settle loop, which skips the
        # branch the leave reported, does not report it again
        r, env = world(tmp, "t-merged-leave-kept")
        ff_merged(r, "t-merged-leave-kept-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("update-ref", "-d", "refs/remotes/origin/" + A)
        r.write(RES_A, "r\n")

        def then_unreachable(root, fetch):
            out = real_resolve(root, fetch)
            if fetch:
                sb.git(root, "remote", "set-url", "origin", os.path.join(tmp, "t-merged-leave-kept-gone.git"))
            return out

        g["resolve_default"] = then_unreachable
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["resolve_default"] = real_resolve
        shown = got.get("print") or []
        check(len(shown) == 4 and shown[1].startswith("Specs preflight: could not fast-forward main (")
              and shown[2].startswith("Specs preflight: could not delete merged prd/A-1-x (error: ")
              and shown[3].startswith("Specs preflight: main — push FAILED (") and got.get("b2_left") == A
              and rev(r, A) is not None and got.get("branch") == "main",
              "t_merged_leave_kept: the leave's reports once, the settle loop skipping the branch it reported (%r)" % got)
        got = run_start(env, "/feedback", "--rerun")
        shown = got.get("print") or []
        check(got["_rc"] == 0 and len(shown) == 2 and shown[1].startswith("Specs preflight: main — push FAILED (")
              and not any(A in line for line in shown) and (record(env, "/feedback") or {}).get("b2_left") == A,
              "t_merged_leave_kept: --rerun carries b2_left, so its settle loop skips that branch too (%r)" % got)

        # t_merged_unknown: an origin that holds no default branch yet, so branch-merged cannot answer anywhere
        bare = os.path.join(tmp, "t-merged-unknown.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, "t-merged-unknown")
        r.git("remote", "add", "origin", bare)
        env = {"HOME": os.path.join(tmp, "home-t-merged-unknown"), "CLAUDE_CODE_SESSION_ID": "t-merged-unknown",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("branch", "prd/ACME-2-y")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/prd.md", "p\n")
        r.commit_all("ACME-1 Add the PRD")
        r.write(RESUME, "r\n")

        def unknown(branch):
            return ("Specs preflight: could not tell whether %s is merged (specs-git: not run (origin/main does not "
                    "resolve to a commit)), so it reads unmerged" % branch)

        # The leave asks HEAD, the settle loop its branch, B2's row HEAD again: one report for a branch in a run.
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got["_rc"] == 0 and got.get("print") == [env_line(r.path), unknown(PLUGIN), unknown("prd/ACME-2-y")]
              and got.get("branch") == PLUGIN and rev(r, "prd/ACME-2-y") is not None and got.get("error") is None
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and (record(env, "/feedback") or {}).get("reported") == ["pre.merged-unknown " + PLUGIN,
                                                                       "pre.merged-unknown prd/ACME-2-y"],
              "t_merged_unknown: the leave's and the settle loop's asks report, B2's repeats none, all read unmerged "
              "(%r)" % got)
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), unknown("prd/ACME-2-y"), unknown(PLUGIN)]
              and got.get("branch") == PLUGIN, "t_merged_unknown: on a clean tree, the settle loop's and B2's (%r)" % got)
        # --budget 0: an ask made just before a stop is not reported again by the resume that asks it again
        calls = [run_start(env, "/feedback", "--key", "ACME-1", "--budget", "0")]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
        stitched = [p for c in calls for p in c.get("print") or []]
        check(len(calls) == 3 and stitched == [env_line(r.path), unknown("prd/ACME-2-y"), unknown(PLUGIN)]
              and calls[-1].get("next") is None and (record(env, "/feedback") or {}).get("stage") == "done",
              "t_merged_unknown: at --budget 0 each report once across the calls (%r)" % stitched)
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path)], "t_merged_unknown: a --rerun carries the reports, so prints none (%r)" % got)

        # t_status_failed (in process): status cannot run -- one report, G1 finds nothing, the flush stages nothing
        r, env = world(tmp, "t-status-failed")
        r.write(RESUME, "r\n")
        r.write("notes.md", "n\n")
        h = head(r)
        real_status = g["status"]

        def broken_status(root):
            raise NotRun("git status: fatal: index file corrupt")

        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged"]
              and got.get("error") is None and got.get("guard") is None and head(r) == h
              and (record(env, "/feedback") or {}).get("stage") == "done",
              "t_status_failed: reported once, nothing staged, the preflight going on to the end (%r)" % got)

        # t_status_failed_stay (in process): with the dirty set unknown, B2 on a merged plugin branch stays and says so
        r, env = world(tmp, "t-status-failed-stay")
        ff_merged(r, "t-status-failed-stay-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write(RES_A, "r\n")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        stay = lines.placeholder("pre.stay.unlisted", "<switched")
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged",
                                   "Specs preflight: staying on prd/A-1-x — the uncommitted paths could not be listed, so no "
                                   "branch is switched (it would have switched to main and deleted it, as it is merged)"]
              and lines.fill("pre.stay.unlisted", {"<branch>": A, "<default>": "main", stay: 0}) == got["print"][2]
              and got.get("branch") == A and rev(r, A) is not None and got.get("b2_left") is None
              and got.get("error") is None, "t_status_failed_stay: B2 stays and reports, nothing switched (%r)" % got)

        # t_status_failed_stay_b4 (in process): with the dirty set unknown, B4 on an unmerged plugin branch no key names
        # stays and says so
        r, env = world(tmp, "t-status-failed-stay-b4")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",))
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged",
                                   "Specs preflight: staying on spec/ACME-1-01-x — the uncommitted paths could not be listed, "
                                   "so no branch is switched (it would have switched to main, as no key of this run names it)"]
              and lines.fill("pre.stay.unlisted", {"<branch>": SPEC, "<default>": "main", stay: 1}) == got["print"][2]
              and got.get("branch") == SPEC and got.get("b4_left") is None and got.get("error") is None,
              "t_status_failed_stay_b4: B4 stays and reports, nothing switched (%r)" % got)

        # t_rerun_unlisted (in process for the failing call): a start whose B4 leaves a branch, a --rerun whose status
        # fails, then a --rerun whose keys name the branch -- the switch back is left undone, as B2 and B4 are
        r, env = world(tmp, "t-rerun-unlisted")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-2")
        check(got.get("branch") == "main" and got.get("b4_left") == SPEC, "t_rerun_unlisted: B4 leaves the branch (%r)" % got)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",), rerun=True)
        finally:
            g["status"] = real_status
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not list the uncommitted paths (specs-git: not "
                                   "run (git status: fatal: index file corrupt)), so nothing is staged"]
              and got.get("branch") == "main" and got.get("b4_left") == SPEC
              and "pre.status-failed" in ((record(env, "/document") or {}).get("reported") or []),
              "t_rerun_unlisted: the re-run's status fails, its report recorded (%r)" % got)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        check(got.get("print") == [env_line(r.path), "Specs preflight: staying on main — the uncommitted paths could not be "
                                   "listed, so no branch is switched (it would have switched back to spec/ACME-1-01-x, as a "
                                   "key of this run names it)"]
              and lines.fill("pre.rerun-stay", {"<current>": "main", "<branch>": SPEC}) == got["print"][1]
              and got.get("branch") == "main" and r.git("symbolic-ref", "--short", "HEAD") == "main"
              and got.get("b4_left") == SPEC and got.get("error") is None,
              "t_rerun_unlisted: no switch back after the run's status failure (%r)" % got)

        # t_flush_order (in process): the dirty flush tests step 5's conditions in order, push-scope last, so a branch
        # origin lacks stops silently before push-scope is measured
        r, env = world(tmp, "t-flush-order")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.write(RESUME, "r\n")
        real_scope = g["push_scope"]
        measured = []

        def watched_scope(root, branch, session_default_ref=None):
            measured.append(branch)
            raise NotRun("git rev-list: fatal: bad object")

        g["push_scope"] = watched_scope
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["push_scope"] = real_scope
        check(got.get("print") == [env_line(r.path)] and measured == [] and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and on_origin(r, PLUGIN) is None and got.get("error") is None,
              "t_flush_order: origin-lacks stops the push before push-scope is measured, silently (%r, %r)" % (got, measured))

        # t_scope_failed (in process): push-scope cannot run for two branches -- each reported once, neither pushed,
        # B4 naming no count
        r, env = world(tmp, "t-scope-failed")
        Q, P2 = "prd/ACME-9-q", "prd/ACME-3-p"
        r.git("switch", "-q", "-c", P2, "main")
        r.git("push", "-q", "-u", "origin", P2)
        session_commit(r, P2, "PRD-ACME-3-p")
        r.git("switch", "-q", "-c", Q, "main")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        real_scope = g["push_scope"]

        def broken_scope(root, branch, session_default_ref=None):
            if branch in (Q, P2):
                raise NotRun("git rev-list: fatal: bad object")
            return real_scope(root, branch, session_default_ref)

        def scope_failed(branch):
            return ("Specs preflight: could not measure what a push of %s would publish (specs-git: not run (git rev-list: "
                    "fatal: bad object)), so %s is not pushed" % (branch, branch))

        g["push_scope"] = broken_scope
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["push_scope"] = real_scope
        check(got.get("print") == [env_line(r.path), scope_failed(Q), scope_failed(P2),
                                   lines.fill("pre.b4", {"<branch>": Q, "<default>": "main"})]
              and got.get("error") is None and on_origin(r, P2) != rev(r, P2) and got.get("branch") == "main",
              "t_scope_failed: the retry's and the loop's reports, nothing pushed, B4 with no count (%r)" % got)

        # t_settle
        r, env = world(tmp, "t-settle")
        F, P, S = "prd/ACME-2-f", "prd/ACME-3-p", "prd/ACME-4-s"
        ff_merged(r, "t-settle-f", F, "specifications/PRD-ACME-2-f/prd.md")
        squash_merged(r, "t-settle-s", S, "specifications/PRD-ACME-4-s/prd.md")
        s_record = refusal_file(r, S)
        r.git("switch", "-q", "-c", P, "main")
        r.git("push", "-q", "-u", "origin", P)
        session_commit(r, P, "PRD-ACME-3-p")
        r.git("switch", "-q", "main")
        got = run_start(env, "/feedback")
        advisory = lines.fill("pre.advisory-D", {"<branch>": S, "<default>": "main", "<SPECS_PATH>": r.path})
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-2-f",
                                   "Specs preflight: pushed 1 session-file commit(s) left on prd/ACME-3-p", advisory,
                                   'rm -f "%s"' % s_record]
              and rev(r, F) is None and rev(r, S) is not None and on_origin(r, P) == rev(r, P),
              "t_settle: deleted merged, pushed left, the -D advisory with its rm (%r)" % got)
        check((record(env, "/feedback") or {}).get("advised_D") == [S], "t_settle: the advisory recorded")
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("print") == [env_line(r.path)] and (record(env, "/feedback") or {}).get("advised_D") == [S],
              "t_settle: the -D advisory is not given again after start --rerun (%r)" % got)

        # t_settle_delete_failed: a branch merged by ancestry -d can see, but checked out in another worktree
        r, env = world(tmp, "t-settle-delete-failed")
        ff_merged(r, "t-settle-delete-failed-other", F, "specifications/PRD-ACME-2-f/prd.md")
        r.git("switch", "-q", "main")
        elsewhere = os.path.join(tmp, "t-settle-delete-failed-wt")
        r.git("worktree", "add", "-q", elsewhere, F)
        got = run_start(env, "/feedback")
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[1].startswith("Specs preflight: could not delete merged %s (error: " % F)
              and rev(r, F) is not None, "t_settle_delete_failed: -d's refusal, never -D (%r)" % got)

        # t_refusal_record_removed: B2's file record, and the settle loop's configuration-key record
        r, env = world(tmp, "t-refusal-removed")
        K = "prd/K-2-k"
        ff_merged(r, "t-refusal-removed-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("branch", K)
        a_record = refusal_file(r, A)
        r.git("config", "branch.%s.workflowsPushRefused" % K, "2026-11-01")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/K-2-k",
                                   "Specs preflight: deleted merged prd/A-1-x"]
              and not os.path.exists(a_record) and got.get("branch") == "main"
              and r.git("config", "--get", "branch.%s.workflowsPushRefused" % K, check=False) == "",
              "t_refusal_record_removed: each deleted branch's push-refusal record goes with it (%r)" % got)

        # t_b2
        r, env = world(tmp, "t-b2")
        B = "prd/ACME-5-a"
        ff_merged(r, "t-b2-other", B, "specifications/PRD-ACME-5-a/prd.md")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-5-a"]
              and got.get("branch") == "main" and got.get("b2_left") == B and rev(r, B) is None
              and head(r) == on_origin(r), "t_b2: switched, pulled, deleted (%r)" % got)
        r, env = world(tmp, "t-b2-squash")
        Q = "prd/ACME-6-q"
        squash_merged(r, "t-b2-squash-other", Q, "specifications/PRD-ACME-6-q/prd.md")
        q_record = refusal_file(r, Q)
        got = run_start(env, "/feedback")
        shown = got.get("print") or []
        squash = lines.fill("pre.b2-squash", {"<branch>": Q, "<default>": "main", "<SPECS_PATH>": r.path})
        check(len(shown) == 4 and shown[1].startswith("Specs preflight: could not delete merged prd/ACME-6-q (error: ")
              and shown[2] == squash and shown[3] == 'rm -f "%s"' % q_record and got.get("branch") == "main"
              and got.get("b2_left") == Q and rev(r, Q) is not None and os.path.exists(q_record),
              "t_b2: a squash-merged branch is kept, -d's refusal and the -D line after it (%r)" % got)
        check((record(env, "/feedback") or {}).get("advised_D") == [Q], "t_b2: the -D line recorded once for the run")

        # t_b2_config (in process): the branch's configuration left behind where .git/config cannot be written
        r, env = world(tmp, "t-b2-config")
        ff_merged(r, "t-b2-config-other", B, "specifications/PRD-ACME-5-a/prd.md")
        real_config = sb.config

        def stuck(root, key, as_bool=False):
            return "refs/heads/" + B if key == "branch.%s.merge" % B else real_config(root, key, as_bool)

        sb.config = stuck
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            sb.config = real_config
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/ACME-5-a",
                                   lines.fill("pre.b2-config", {"<branch>": B, "<SPECS_PATH>": r.path})],
              "t_b2_config: the configuration line after the deletion (%r)" % got)

        # t_b3_b4, t_rerun
        r, env = world(tmp, "t-b3-b4")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-1-01", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == SPEC and got.get("b4_left") is None,
              "t_b3_b4: a branch a key of the run names stays (%r)" % got)
        got = run_start(env, "/document", "--key", "ACME-2")
        b4 = (lines.fill("pre.b4", {"<branch>": SPEC, "<default>": "main"}) + lines.fill("pre.b4.count", {"<N>": 1}))
        check(got.get("print") == [env_line(r.path), b4] and got.get("branch") == "main" and got.get("b4_left") == SPEC,
              "t_b3_b4: no key names it, so B4 leaves it, with its count (%r)" % got)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        check(got.get("print") == [env_line(r.path)] and got.get("branch") == SPEC and got.get("b4_left") is None
              and got.get("replaced") is None, "t_rerun: back on the branch B4 left (%r)" % got)
        got = run_start(env, "/document", "--key", "ACME-2")
        r.git("branch", "-D", SPEC)
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01")
        shown = got.get("print") or []
        check(len(shown) == 2 and shown[1].startswith("Specs preflight: could not switch back to %s (" % SPEC)
              and shown[1].endswith("); this run goes on from main") and got.get("branch") == "main",
              "t_rerun: a branch deleted meanwhile gives pre.rerun-failed (%r)" % got)

        # t_b4_pull_capped (in process): B4's pull ended by the cap prints its failure line, then B4's report
        r, env = world(tmp, "t-b4-pull-capped")
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        r.git("push", "-q", "-u", "origin", SPEC)
        real_bounded = sb.git_bounded

        def capped_pull(root, seconds, *args):
            if args and args[0] == "pull":
                return subprocess.CompletedProcess(["git"] + list(args), 124, b"", b"")
            return real_bounded(root, seconds, *args)

        sb.git_bounded = capped_pull
        try:
            with in_env(env):
                got = start(r.path, "/document", ("ACME-2",))
        finally:
            sb.git_bounded = real_bounded
        check(got.get("print") == [env_line(r.path), "Specs preflight: could not fast-forward main (the pull did not finish "
                                   "within 60 s); the run goes on from it as it stands",
                                   lines.fill("pre.b4", {"<branch>": SPEC, "<default>": "main"})]
              and got.get("branch") == "main", "t_b4_pull_capped: the capped pull's words, then B4's report (%r)" % got)

        # t_b4_no_remote: with no origin, <default-ref> is refs/heads/main, so B4 switches and pulls nothing
        r = new_repo(tmp, "t-b4-no-remote")
        env = {"HOME": os.path.join(tmp, "home-t-b4-no-remote"), "CLAUDE_CODE_SESSION_ID": "t-b4-no-remote",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("switch", "-q", "-c", "prd/ACME-9-q")
        r.write("specifications/PRD-ACME-9-q/prd.md", "q\n")
        r.commit_all("ACME-9 Add the PRD")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), lines.fill("pre.b4", {"<branch>": "prd/ACME-9-q", "<default>": "main"})
                                   + lines.fill("pre.b4.count", {"<N>": 2})]
              and got.get("default_ref") == "refs/heads/main" and got.get("remote") == "none" and got.get("branch") == "main",
              "t_b4_no_remote: no pull and no pull-failed line where there is no origin (%r)" % got)

        # t_rerun_blocked: a run --rerun carries blocked into prints the re-run's own block and keeps G0's for end. G0's
        # date is one of the days dated() reads just before and just after the call that rendered it, never one fixed at
        # this scenario's start, so a run across 00:00 UTC passes: t_rerun_blocked_midnight runs the case with the clock
        # start reads crossing midnight between this scenario's start and the render, and
        # t_rerun_blocked_midnight_during with it crossing during the call, after the render (injected, in process; no
        # sleeping)
        def rerun_blocked(label, name, first):
            r, env = world(tmp, name)
            r.git("switch", "-q", "--detach", "HEAD")
            h = head(r)
            got, days, _ = dated(lambda: first(env, "/specify"))
            blocks = [lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": d, "<branch>": "main"})
                      for d in days]
            g0 = next((b for b in blocks if got.get("print") == [env_line(r.path), b]), blocks[-1])
            check(got.get("print") == [env_line(r.path), g0] and got.get("specs_git") == "blocked",
                  "%s: G0 first (%r)" % (label, got))
            r.git("switch", "-q", "-c", "feature/x")
            got = run_start(env, "/specify", "--rerun")
            g2 = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
            rec = record(env, "/specify") or {}
            check(got.get("print") == [env_line(r.path), g2] and got.get("specs_git") == "blocked"
                  and got.get("guard") == "G0" and rec.get("guard_block") == g0 and rec.get("guard_paths") == [],
                  "%s: the re-run's G2 printed, G0's fields kept (%r, %r)" % (label, got, rec))
            r.write(RESUME, "r\n")
            got = run_end(env, "/specify")
            check(got.get("row") == "blocked" and got.get("print") == ["Specs repo: NOT COMMITTED — see the notice below", g0]
                  and head(r) == h, "%s: end prints G0's block with the blocked row (%r)" % (label, got))
            return g0
        rerun_blocked("t_rerun_blocked", "t-rerun-blocked", run_start)

        def start_past_midnight(env, command):
            with in_env(env):
                return start(env["SPECS_PATH"], command)
        real_today = g["_today"]
        tomorrow = time.strftime("%Y-%m-%d", time.gmtime(time.time() + 86400))
        g["_today"] = lambda: tomorrow  # the clock _today reads has crossed 00:00 UTC since this scenario started
        try:
            rerun_blocked("t_rerun_blocked_midnight", "t-rerun-blocked-midnight", start_past_midnight)
        finally:
            g["_today"] = real_today
        # ... and with the clock crossing midnight during the call, after the render: G0 carries the day before
        before = time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400))  # a day distinct from tomorrow's
        day = [before]

        def start_then_midnight(env, command):
            got = start_past_midnight(env, command)
            day[0] = tomorrow  # 00:00 UTC passes as start returns, after it rendered G0
            return got
        g["_today"] = lambda: day[0]
        try:
            g0 = rerun_blocked("t_rerun_blocked_midnight_during", "t-rerun-blocked-midnight-during", start_then_midnight)
        finally:
            g["_today"] = real_today
        check(day[0] == tomorrow and before in g0 and tomorrow not in g0,
              "t_rerun_blocked_midnight_during: G0 rendered on the day before the crossing, and checked as such (%r)" % g0)

        # t_rerun_no_record
        r, env = world(tmp, "t-rerun-no-record")
        got = run_start(env, "/release-notes", "--rerun")
        check(got.get("print") == [env_line(r.path)] and got.get("replaced") is None
              and (record(env, "/release-notes") or {}).get("stage") == "done",
              "t_rerun_no_record: a fresh start (%r)" % got)

        # t_rerun_resume
        r, env = world(tmp, "t-rerun-resume")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        r.git("switch", "-q", "-c", SPEC)
        r.write("specifications/PRD-ACME-1-x/EPIC-ACME-1-01-x/specification.md", "s\n")
        r.commit_all("ACME-1-01 Add the specification")
        got = run_start(env, "/document", "--key", "ACME-2")
        check(got.get("b4_left") == SPEC, "t_rerun_resume: the first start's B4 (%r)" % got)
        others = ("prd/ACME-3-a", "prd/ACME-4-b")
        for b in others:
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
            session_commit(r, b, "PRD-" + b[4:], "/document")
        r.git("switch", "-q", "main")

        def back():
            return r.git("reflog", "show", "HEAD").count("moving from main to " + SPEC)

        moved = back()
        got = run_start(env, "/document", "--rerun", "--key", "ACME-2", "--key", "ACME-1-01", "--budget", "0")
        want = resume_line(r.path, "/document", "--key", "ACME-2", "--key", "ACME-1-01", "--budget", "0")
        check(got.get("next") == {"run": want, "timeout_ms": 600000, "on_timeout": None}
              and (record(env, "/document") or {}).get("args", {}).get("keys") == ["ACME-2", "ACME-1-01"]
              and got.get("branch") == SPEC, "t_rerun_resume: next repeats the rerun's own keys, in order (%r)" % got)
        chain = follow(got, env)
        check(len(chain) > 2 and all(c["_rc"] == 0 and fields(c) and c.get("replaced") is None for c in chain[1:])
              and chain[-1].get("next") is None and chain[-1].get("branch") == SPEC
              and (record(env, "/document") or {}).get("stage") == "done",
              "t_rerun_resume: following next continues the same record to done (%r)" % chain[-1])
        check(back() == moved + 1 and all(on_origin(r, b) == rev(r, b) and updates(r, b) == 2 for b in others),
              "t_rerun_resume: the switch back made once, each branch pushed once (%d, %r)"
              % (back() - moved, [updates(r, b) for b in others]))
        seed(env, "/document", stage="settle", settle_todo=None,
             args={"specs": r.path, "keys": ["ACME-2", "ACME-1-01"], "commit_key": None, "register_rebuild": None})
        got = run_start(env, "/document", "--key", "ACME-2", "--resume")
        check((got.get("print") or [None])[0] == env_line(r.path) and got.get("replaced") is not None,
              "t_rerun_resume: the first start's keys fail resumable, and the call runs fresh (%r)" % got)

        # t_nonff_order
        r, env = world(tmp, "t-nonff-order")
        Z = "prd/Z-9-z"
        r.git("switch", "-q", "-c", Z)
        r.write("specifications/PRD-Z-9-z/prd.md", "z\n")
        r.commit_all("Z-9 Add the PRD")
        r.git("push", "-q", "origin", Z)
        r.git("switch", "-q", "main")
        o = clone(r, "t-nonff-order-other")
        o.git("merge", "-q", "--ff-only", "origin/" + Z)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", Z)
        r.git("update-ref", "-d", "refs/remotes/origin/" + Z)
        session_commit(r, "main", "PRD-ACME-1-x", name="s1.md")
        r.write(FEED + "s2.md", "s2\n")
        got = run_start(env, "/feedback")
        nxt = got.get("next") or {}
        check(got.get("print") == [env_line(r.path)] and " replay --for start --command /feedback --branch main" in nxt.get("run", "")
              and nxt.get("timeout_ms") == 420000 and rev(r, Z) is not None,
              "t_nonff_order: the current branch's rejected push hands its replay over first, no settle line (%r)" % got)
        chain = follow(got, env)
        shown = [c.get("print") for c in chain[1:]]
        check(len(chain) == 3 and shown[0] and shown[0][0].startswith("Specs preflight: main — pushed after a replay")
              and chain[1].get("next", {}).get("run") == resume_line(r.path, "/feedback")
              and shown[1] == ["Specs preflight: deleted merged prd/Z-9-z"] and chain[2].get("next") is None
              and (record(env, "/feedback") or {}).get("stage") == "done" and rev(r, Z) is None,
              "t_nonff_order: the replay's line, then the settle line, across the calls (%r)" % shown)
        landed = subprocess.run(["git", "-C", r.bare, "ls-tree", "-r", "--name-only", "main"], stdout=subprocess.PIPE).stdout.decode()
        check(all(p in landed for p in ("specifications/PRD-Z-9-z/prd.md", FEED + "s1.md", FEED + "s2.md")),
              "t_nonff_order: origin's main holds both changes (%r)" % landed)

        # t_replay_stopped: a replay that stops prints pre.stopped and names no next, and the chain ends there
        r, env = world(tmp, "t-replay-stopped")
        o = clone(r, "t-replay-stopped-other")
        o.write(FEED + "o.md", "o\n")
        o.commit_all(SUBJECT % ("NOISSUE", "/specify"))
        o.git("push", "-q", "origin", "main")
        session_commit(r, "main", "PRD-ACME-1-x", name="s1.md")
        got = run_start(env, "/feedback")
        r.git("switch", "-q", "-c", "elsewhere")  # another session moves the checkout before the replay runs
        chain = follow(got, env)
        last = chain[-1]
        check(len(chain) == 2 and last.get("next") is None and last.get("error")
              and (last.get("print") or [""])[0].startswith("Specs preflight: stopped early (")
              and (record(env, "/feedback") or {}).get("stage") == "flush",
              "t_replay_stopped: the chain ends on the replay's pre.stopped, the record as it stood (%r)" % last)

        # t_settle_queue
        r, env = world(tmp, "t-settle-queue")
        Y, X, W = "prd/ACME-2-y", "prd/ACME-3-x", "prd/ACME-9-w"
        for b in (Y, X):
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
        o = clone(r, "t-settle-queue-other")
        for b in (Y, X):
            o.git("switch", "-q", b)
            o.write("specifications/PRD-%s/dev-workflows/feedback/o.md" % b[4:], "o\n")
            o.commit_all(SUBJECT % ("NOISSUE", "/specify"))
            o.git("push", "-q", "origin", b)
            session_commit(r, b, "PRD-" + b[4:])
        r.git("switch", "-q", "-c", W, "main")
        r.write("specifications/PRD-ACME-9-w/prd.md", "w\n")
        r.commit_all("ACME-9 Add the PRD")
        r.git("push", "-q", "-u", "origin", W)
        # At --budget 0 each start call makes one unit of capped calls, so the two rejections queue across calls, and
        # the start --resume the last replay names repeats the budget the record holds.
        calls = [run_start(env, "/feedback", "--budget", "0")]
        while ((calls[-1].get("next") or {}).get("run") and " replay --for start " not in calls[-1]["next"]["run"]
               and len(calls) < 8):
            calls.append(shell(calls[-1]["next"]["run"], env))
        rec = record(env, "/feedback") or {}
        resume0 = resume_line(r.path, "/feedback", "--budget", "0")
        check(len(calls) == 3 and all(c["next"]["run"] == resume0 for c in calls[:-1])
              and [p for c in calls for p in c.get("print") or []] == [env_line(r.path)]
              and calls[-1]["next"]["run"].endswith("replay --for start --command /feedback --branch " + Y)
              and rec.get("stage") == "settle-done" and rec.get("budget") == 0
              and rec.get("pending") == [{"branch": Y, "set_upstream": False, "standing": W},
                                         {"branch": X, "set_upstream": False, "standing": W}],
              "t_settle_queue: both rejections queued, the first replay named (%r, %r)" % (calls[-1], rec))
        chain = follow(calls[-1], env)
        shown = [c.get("print") for c in chain[1:]]
        b4 = lines.fill("pre.b4", {"<branch>": W, "<default>": "main"})
        check(len(chain) == 4 and shown[0][0].startswith("Specs preflight: %s — pushed after a replay" % Y)
              and shown[1][0].startswith("Specs preflight: %s — pushed after a replay" % X)
              and chain[2].get("next") == {"run": resume0, "timeout_ms": 600000, "on_timeout": None} and shown[2] == [b4]
              and on_origin(r, Y) == rev(r, Y) and on_origin(r, X) == rev(r, X) and chain[3].get("branch") == "main"
              and chain[3].get("next") is None,
              "t_settle_queue: the two replays in order, the last naming start --resume with the run's --budget 0, "
              "which runs §3.5 (%r)" % shown)

        # t_budget_resume: --budget 0, followed to its end, against one call with the default budget on a copy
        r, env = world(tmp, "t-budget")
        subprocess.run(["git", "-C", r.bare, "config", "core.logAllRefUpdates", "true"], check=True)
        branches = ("prd/ACME-2-a", "prd/ACME-3-b", "prd/ACME-4-c")
        for b in branches:
            r.git("switch", "-q", "-c", b, "main")
            r.git("push", "-q", "-u", "origin", b)
            session_commit(r, b, "PRD-" + b[4:])
        r.git("switch", "-q", "main")
        c_bare, c_path = os.path.join(tmp, "t-budget-copy.git"), os.path.join(tmp, "t-budget-copy")
        shutil.copytree(r.bare, c_bare, symlinks=True)
        shutil.copytree(r.path, c_path, symlinks=True)
        copy = Repo(c_path)
        copy.bare = c_bare
        copy.git("remote", "set-url", "origin", c_bare)
        c_env = {"HOME": os.path.join(tmp, "home-t-budget-copy"), "CLAUDE_CODE_SESSION_ID": "t-budget-copy",
                 "SPECS_PATH": c_path}
        os.makedirs(c_env["HOME"])
        got = run_start(env, "/feedback", "--budget", "0")
        calls, landed = [got], [sum(on_origin(r, b) == rev(r, b) for b in branches)]
        while (calls[-1].get("next") or {}).get("run") and len(calls) < 8:
            calls.append(shell(calls[-1]["next"]["run"], env))
            landed.append(sum(on_origin(r, b) == rev(r, b) for b in branches))
        check(len(calls) == 4 and landed == [0, 1, 2, 3] and all(c["_rc"] == 0 and fields(c) for c in calls)
              and all(c["next"] == {"run": resume_line(r.path, "/feedback", "--budget", "0"), "timeout_ms": 600000,
                                    "on_timeout": None} for c in calls[:-1]) and calls[-1].get("next") is None,
              "t_budget_resume: each call one push, each naming start --resume, to the end (%r)" % landed)
        check(all(updates(r, b) == 2 for b in branches), "t_budget_resume: every branch pushed exactly once")
        one = run_start(c_env, "/feedback")
        stitched = [p for c in calls for p in c.get("print") or []]
        check(one.get("next") is None and [p.replace(c_path, r.path) for p in one.get("print") or []]
              == [p.replace(env_line(r.path), env_line(c_path).replace(c_path, r.path)) for p in stitched]
              and all(on_origin(copy, b) == on_origin(r, b) for b in branches + ("main",))
              and copy.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
              == r.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
              and {k: v for k, v in (record(c_env, "/feedback") or {}).items() if k in ("stage", "branch", "pending")}
              == {k: v for k, v in (record(env, "/feedback") or {}).items() if k in ("stage", "branch", "pending")},
              "t_budget_resume: the same final state as one call with the default budget (%r)" % one)

        # t_replaced
        r, env = world(tmp, "t-replaced")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["stale"], guard="G1", guard_block="stale block",
             guard_paths=["n.md"], declined=["d.md"], advised_D=["prd/X-1-x"], b4_left="prd/Y-1-y", stage="settle")
        old = record(env, "/create-ard") or {}
        got = run_start(env, "/create-ard")
        rec = record(env, "/create-ard") or {}
        check(got.get("replaced") == {"command": "/create-ard", "started": old.get("started")}
              and got.get("specs_git") is None and got.get("print") == [env_line(r.path)],
              "t_replaced: the stale record reported as replaced (%r)" % got)
        check(all(rec.get(k) == state.FIELDS[k] for k in ("specs_git", "misrooted_notice", "guard", "guard_block",
                                                          "guard_paths", "declined", "advised_D", "b4_left")),
              "t_replaced: the new record holds no flag of the old one (%r)" % rec)

        # t_two_commands
        r, env = world(tmp, "t-two-commands")
        r.write("notes.md", "n\n")
        got = run_start(env, "/specify")
        block_s = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 1, "<path list>": ["notes.md", "notes.md"]})
        check(got.get("print") == [env_line(r.path), block_s], "t_two_commands: /specify's block (%r)" % got)
        spec_rec = record(env, "/specify")
        r.write("notes2.md", "n2\n")
        r.write(FEED + "f.md", "f\n")
        got = run_start(env, "/feedback")
        block_f = lines.fill("g1", {"<SPECS_PATH>": r.path, "<N>": 2,
                                    "<path list>": ["notes.md, notes2.md", "notes.md notes2.md"]})
        check(got.get("print") == [env_line(r.path), block_f], "t_two_commands: /feedback's block (%r)" % got)
        got = run_end(env, "/feedback")
        check(got.get("print") == [pushed_default(head(r)[:7], r.path), block_f] and on_origin(r) == head(r)
              and r.git("show", "--name-only", "--format=", "HEAD") == FEED + "f.md"
              and record(env, "/feedback") is None and record(env, "/specify") == spec_rec,
              "t_two_commands: /feedback's end repeats its own block, /specify's record untouched (%r)" % got)
        got = run_end(env, "/specify")
        check(got.get("print") == ["Specs repo: no session artifacts to commit", g1_uncommitted(block_s)]
              and record(env, "/specify") is None,
              "t_two_commands: /specify's end repeats the block its own start saved, in the form for an end that "
              "committed nothing (%r)" % got)

        # t_prune
        r, env = world(tmp, "t-prune")
        with in_env(env):
            for session, command, days in (("old-session", "/specify", 8), ("new-session", "/specify", 6),
                                           ("t-prune", "/create-ard", 8)):
                state.save(session, command, state.new(command, session=session))
                stamp = time.time() - days * 86400
                os.utime(state.path(session, command), (stamp, stamp))
        run_start(env, "/feedback")
        with in_env(env):
            kept = [os.path.exists(state.path(s, c)) for s, c in (("old-session", "/specify"), ("new-session", "/specify"),
                                                                  ("t-prune", "/create-ard"), ("t-prune", "/feedback"))]
            gone_dir = not os.path.exists(os.path.join(state.root(), "old-session"))
        check(kept == [False, True, True, True] and gone_dir,
              "t_prune: another session's record 8 days old gone, 6 days kept, this session's kept (%r)" % kept)

        # t_resume_stale
        r, env = world(tmp, "t-resume-stale")
        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["Specs preflight: a stale notice"], stage="done")
        real_save = state.save

        def interrupted(*args, **kw):
            raise KeyboardInterrupt

        stopped = False
        state.save = interrupted
        try:
            with in_env(env):
                start(r.path, "/create-ard")
        except KeyboardInterrupt:
            stopped = True
        finally:
            state.save = real_save
        check(stopped and (record(env, "/create-ard") or {}).get("specs_git") == "misrooted",
              "t_resume_stale: a start stopped before its first write leaves the stale record")
        got = run_start(env, "/create-ard", "--resume")
        check(got.get("print") == [env_line(r.path)] and got.get("specs_git") is None and got.get("replaced") is not None,
              "t_resume_stale: a stale record at done is no resume; a fresh preflight (%r)" % got)

        def aged(minutes):
            with in_env(env):
                rec = state.load(env["CLAUDE_CODE_SESSION_ID"], "/create-ard")
                rec["updated"] = time.strftime(state.STAMP, time.gmtime(time.time() - minutes * 60))
                with open(state.path(env["CLAUDE_CODE_SESSION_ID"], "/create-ard"), "w", encoding="utf-8") as fh:
                    json.dump(rec, fh)

        seed(env, "/create-ard", specs_git="misrooted", misrooted_notice=["Specs preflight: a stale notice"], stage="settle",
             settle_todo=None)
        aged(20)
        got = run_start(env, "/create-ard", "--resume")
        check(got.get("print") == [env_line(r.path)] and got.get("specs_git") is None,
              "t_resume_stale: a record saved 20 minutes ago is no resume either (%r)" % got)
        L = "prd/ACME-7-l"
        r.git("switch", "-q", "-c", L, "main")
        r.git("push", "-q", "-u", "origin", L)
        session_commit(r, L, "PRD-ACME-7-l")
        r.git("switch", "-q", "main")
        seed(env, "/create-ard", stage="settle", settle_todo=None)
        got = run_start(env, "/create-ard", "--resume")
        check(got.get("print") == ["Specs preflight: pushed 1 session-file commit(s) left on %s" % L]
              and got.get("replaced") is None and fields(got) and on_origin(r, L) == rev(r, L)
              and (record(env, "/create-ard") or {}).get("stage") == "done",
              "t_resume_stale: a record at settle saved now, the same arguments, continues from settle (%r)" % got)

        # t_exit2_nothing_done
        r, env = world(tmp, "t-exit2")
        r.write(RESUME, "r\n")

        def snapshot():
            return (r.git("status", "--porcelain"), head(r), r.git("branch", "--list"), r.git("for-each-ref"),
                    subprocess.run(["git", "-C", r.bare, "for-each-ref"], stdout=subprocess.PIPE).stdout)

        before = snapshot()
        claude = os.path.join(env["HOME"], ".claude")
        got = cli("--specs", r.path, "start", "--command", "/feedback",
                  env={k: v for k, v in env.items() if k != "CLAUDE_CODE_SESSION_ID"})
        check(one_not_run_line(got) and snapshot() == before and not os.path.exists(claude),
              "t_exit2_nothing_done: no session variable, exit 2, one line, nothing done (%r)" % got)
        for args, what in ((("--key", "bad"), "a key off the grammar"), (("--commit-key", "acme-1"), "a lower-case key"),
                           (("--key", "ACME-1\n"), "a key with a newline"), (("--budget", "-1"), "a negative budget"),
                           (("--budget", "soon"), "a budget that is no number")):
            got = run_start(env, "/feedback", *args)
            check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and snapshot() == before
                  and not os.path.exists(claude), "t_exit2_nothing_done: %s is a usage exit 2 (%r)" % (what, got))
        got = cli("--specs", r.path, "start", "--command", "feedback", env=env)
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: ") and not os.path.exists(claude),
              "t_exit2_nothing_done: a command without its slash (%r)" % got)
        got = cli("start", "--command", "/feedback", env=env)
        check(one_not_run_line(got) and got["_err"].startswith("specs-git: not run (usage: "),
              "t_exit2_nothing_done: no --specs at all is a usage error (%r)" % got)

        # t_error_after_write
        r, env = world(tmp, "t-error")
        r.write(RESUME, "r\n")
        real_settle = g["_settle"]

        def boom(*args, **kw):
            raise RuntimeError("boom")

        g["_settle"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["_settle"] = real_settle
        stop = ("Specs preflight: stopped early (RuntimeError: boom) — what it did is above, and the next run's preflight "
                "goes on from where this one stands")
        check(got.get("error") == "RuntimeError: boom" and got.get("print") == [env_line(r.path), stop] and set(got) == FIELDS
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and (record(env, "/feedback") or {}).get("stage") == "settle",
              "t_error_after_write: exit-0 result, error set, the commit pushed, the record saved (%r)" % got)

        # The landing on a merged plugin branch (S2, §4 step 1): a merged branch the preflight stayed on takes the
        # landing as every stay does -- the run's own session files committed on main, the checkout unmoved, the files
        # lifted -- where an earlier version held them uncommitted. A is fast-forward-merged into origin's main;
        # notes.md is not the plugin's, so G1 fires; RES_A, dirty before the start, is not the run's (S1), so FEED_A,
        # written after it, is the run's own change.
        def merged_world(name):
            r, env = world(tmp, name)
            ff_merged(r, name + "-other", A, "specifications/PRD-A-1-x/prd.md")
            r.write("notes.md", "n\n")
            r.write(RES_A, "r\n")
            return r, env

        def refused_world(name):
            """A merged into origin's main by fast-forward and deleted there, r's main behind it; RES_A differs between
            r's main and A and is dirty, so git refuses the merged-branch leave's switch (t_merged_leave)."""
            r, env = world(tmp, name)
            r.write(RES_A, "main's\n")
            r.commit_all("NOISSUE a resume pointer on main")
            r.git("push", "-q", "origin", "main")
            r.git("switch", "-q", "-c", A)
            r.write(RES_A, "the branch's\n")
            r.commit_all("A-1 work")
            r.git("push", "-q", "-u", "origin", A)
            o = clone(r, name + "-other")
            o.git("merge", "-q", "--ff-only", "origin/" + A)
            o.git("push", "-q", "origin", "main")
            o.git("push", "-q", "origin", "--delete", A)
            r.write(RES_A, "dirty\n")
            return r, env

        FEED_A = "specifications/PRD-A-1-x/dev-workflows/feedback/f.md"

        def gone(r, path):
            return not os.path.lexists(os.path.join(r.path, path))

        def landed_on_main(r, paths):
            """main's tip is the landing's one commit, naming exactly <paths>, and origin's main holds it."""
            tip = rev(r, "main")
            return (tip is not None and on_origin(r) == tip
                    and sorted(r.git("show", "--name-only", "--format=", tip).split()) == sorted(paths))

        # t_land_merged_g1: start prints G1's landing form, merged's alternative, and records the stay; end lands the run's
        # own file on main -- alternative 1 -- and repeats the landing form whole; HEAD and the branch unmoved, the
        # branch still merged, the file lifted, the leftover as it was
        r, env = merged_world("t-land-merged-g1")
        h = head(r)
        landing = g1_landing(r, ["notes.md"], A, "merged")
        got = run_start(env, "/feedback")
        rec = record(env, "/feedback") or {}
        check(got.get("print") == [env_line(r.path), landing] and got.get("guard") == "G1" and got.get("branch") == A
              and fields(got) and got.get("stay") == stayed(A, "g1")
              and rec.get("stay") == stayed(A, "g1") and rec.get("guard_block") == g1_plain(r, ["notes.md"])
              and "WILL be committed at the end of the run on main, not on prd/A-1-x, which is merged into main" in landing
              and "WILL still be committed" not in landing,
              "t_land_merged_g1: G1's landing form printed, the stay recorded, the plain block saved (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got["_rc"] == 0 and got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A), landing]
              and got.get("line") == landed_row(r, 1, A) and got.get("sha7") == (rev(r, "main") or "")[:7]
              and got.get("pushed") is True and got.get("branch") == "main" and landed_on_main(r, [FEED_A])
              and head(r) == h and rev(r, A) == h and r.git("symbolic-ref", "--short", "HEAD") == A
              and gone(r, FEED_A) and untracked(r, RES_A) and branch_merged(r.path, "HEAD", "origin/main")["merged"]
              and record(env, "/feedback") is None,
              "t_land_merged_g1: end lands the run's file on main, the checkout unmoved, the landing form whole (%r)" % got)

        # t_land_merged_next_run: notes.md cleaned, the next run's preflight leaves the merged branch before its flush
        # (§3.4) and lands the leftover on main, pushed
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"] and got.get("branch") == "main"
              and rev(r, A) is None and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and on_origin(r) == head(r)
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A and stay_of(env) is None,
              "t_land_merged_next_run: the next run leaves the branch and commits the files on main (%r)" % got)

        # t_land_merged_fix_line: the review's sequence -- G1's merged-branch Fix line run whole, as printed, through
        # bash -c (its commit's message typed in the editor) after the end landed the run's file: the user's files
        # committed on main, off the merged branch; the next run commits the leftover on main and deletes the branch
        r, env = merged_world("t-land-merged-fix")
        shown = (run_start(env, "/feedback").get("print") or [""])[-1]
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and shown == g1_landing(r, ["notes.md"], A, "merged")
              and got.get("print") == [landed_row(r, 1, A), shown] and gone(r, FEED_A),
              "t_land_merged_fix_line: the landing form, merged's alternative, then end lands (%r)" % got)
        fix = next((x for x in shown.split("\n") if x.startswith("Fix:")), "Fix:")
        editor = os.path.join(tmp, "t-land-merged-fix-editor.sh")  # the commit's message, as a user types it in the editor
        with open(editor, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\necho 'my notes' > \"$1\"\n")
        os.chmod(editor, 0o755)
        ran = subprocess.run(["bash", "-c", fix[len("Fix:"):].strip()], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=dict(os.environ, GIT_EDITOR=editor))
        got = run_start(env, "/feedback")
        check(ran.returncode == 0 and got.get("print") == [env_line(r.path), "Specs preflight: deleted merged prd/A-1-x"]
              and got.get("branch") == "main" and rev(r, A) is None and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A
              and r.git("log", "-1", "--format=%s", "HEAD~1") == "my notes" and r.git("status", "--porcelain") == "",
              "t_land_merged_fix_line: the files reach main, the merged branch deleted (%r)" % got)

        # t_land_merged_committed_on_branch: the plain G1 fix instead, a commit on the merged branch after the end
        # landed, which makes it read unmerged: the next run's flush commits the leftover on it, and B4 then leaves it
        r, env = merged_world("t-land-merged-on-branch")
        run_start(env, "/feedback")
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and landed_on_main(r, [FEED_A]),
              "t_land_merged_committed_on_branch: the end lands (%r)" % got)
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "my notes")
        got = run_start(env, "/feedback")
        check(got.get("print") == [env_line(r.path), lines.fill("pre.b4", {"<branch>": A, "<default>": "main"})
                                   + lines.fill("pre.b4.count", {"<N>": 2})]
              and got.get("branch") == "main" and r.git("log", "-1", "--format=%s", A) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("log", "-1", "--format=%s", A + "~1") == "my notes" and stay_of(env) is None,
              "t_land_merged_committed_on_branch: the leftover committed on the branch, B4's line naming both commits "
              "(%r)" % got)

        # t_land_merged_status_failed (in process): status cannot run at start, so B2 stays (pre.stay.unlisted), the stay
        # is recorded and no snapshot is taken; end, whose status runs, lands against HEAD -- the leftover with the rest
        # -- and says so (app.landed.unlisted); no block, since no guard fired
        r, env = merged_world("t-land-merged-status")
        h = head(r)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        check(got.get("branch") == A and got.get("guard") is None and got.get("error") is None
              and stay_of(env) == stayed(A, "unlisted") and got.get("start_dirty") is None,
              "t_land_merged_status_failed: B2 stays, the stay recorded, no snapshot (%r)" % got)
        got = run_end(env, "/feedback")
        unlisted = lines.fill("app.landed.unlisted", {"<branch>": A})
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A) + unlisted]
              and head(r) == h and landed_on_main(r, [RES_A]) and gone(r, RES_A),
              "t_land_merged_status_failed: end lands the leftover too, and says so (%r)" % got)

        # t_land_merged_leave_refused: git refuses the merged-branch leave's switch, so the flush commits on the branch
        # with the cherry-pick line; a session file written after it is the run's, and lands on main
        r, env = refused_world("t-land-merged-refused")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = got.get("print") or []
        flushed = head(r)
        check(len(shown) == 3 and shown[1].startswith("Specs preflight: could not switch from merged prd/A-1-x to main (")
              and shown[2] == lines.fill("pre.merged-flush", {"<branch>": A, "<sha7>": flushed[:7], "<default>": "main",
                                                              "<SPECS_PATH>": r.path})
              and got.get("branch") == A and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_leave_refused: the flush on the branch, the cherry-pick line, the stay recorded (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)] and head(r) == flushed
              and landed_on_main(r, [FEED_A]) and gone(r, FEED_A),
              "t_land_merged_leave_refused: a session file written after the start lands on main (%r)" % got)
        # with no key naming it, B4 leaves the branch the flush made unmerged, and that clears the stay
        r, env = refused_world("t-land-merged-refused-b4")
        got = run_start(env, "/feedback")
        check(got.get("branch") == "main" and got.get("b4_left") == A and stay_of(env) is None,
              "t_land_merged_leave_refused: a start that leaves the branch clears the stay (%r)" % got)

        # t_land_merged_resume: --budget 0 splits that start across calls; the stay one call records stands through the
        # next
        r, env = world(tmp, "t-land-merged-resume")
        B = "spec/B-1-y"
        r.git("switch", "-q", "-c", B)
        r.git("push", "-q", "-u", "origin", B)
        session_commit(r, B, "PRD-B-1-y")
        r.git("switch", "-q", "main")
        r.write(RES_A, "main's\n")
        r.commit_all("NOISSUE a resume pointer on main")
        r.git("push", "-q", "origin", "main")
        r.git("switch", "-q", "-c", A)
        r.write(RES_A, "the branch's\n")
        r.commit_all("A-1 work")
        r.git("push", "-q", "-u", "origin", A)
        o = clone(r, "t-land-merged-resume-other")
        o.git("merge", "-q", "--ff-only", "origin/" + A)
        o.git("push", "-q", "origin", "main")
        o.git("push", "-q", "origin", "--delete", A)
        r.write(RES_A, "dirty\n")
        calls = follow(run_start(env, "/feedback", "--key", "A-1", "--budget", "0"), env)
        shown = [line for c in calls for line in (c.get("print") or [])]
        check(len(calls) == 3 and calls[-1].get("next") is None and calls[-1].get("branch") == A
              and "Specs preflight: pushed 1 session-file commit(s) left on spec/B-1-y" in shown
              and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_resume: the stay recorded in one call stands through the resume after it (%r)" % shown)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]),
              "t_land_merged_resume: end lands on the stay the split start recorded (%r)" % got)

        # t_land_merged_rerun_clears: a --rerun's preflight derives its own stay; leaving the merged branch, it keeps
        # none
        r, env = merged_world("t-land-merged-rerun")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("branch") == "main" and got.get("b2_left") == A and stay_of(env) is None,
              "t_land_merged_rerun_clears: the re-run leaves the branch and clears the stay (%r)" % got)
        got = run_end(env, "/feedback")
        check(got.get("row") == "nothing", "t_land_merged_rerun_clears: end goes on as before (%r)" % got)

        # t_land_merged_rerun_stopped (in process for the re-run): a re-run's preflight derives its own stay -- G1 gone,
        # it stops early on the merged branch, so the stay is its own, stopped, and end lands with no notice
        r, env = merged_world("t-land-merged-rerun-stopped")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        real_flush = g["_flush"]
        g["_flush"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback", rerun=True)
        finally:
            g["_flush"] = real_flush
        check(got.get("error") == "RuntimeError: boom" and got.get("stay") == stayed(A, "stopped")
              and stay_of(env) == stayed(A, "stopped") and (record(env, "/feedback") or {}).get("guard") is None,
              "t_land_merged_rerun_stopped: the re-run's own reason (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]) and untracked(r, RES_A),
              "t_land_merged_rerun_stopped: the end lands the run's file, and no notice (%r)" % got)

        # t_land_merged_rerun_b3: the user commits on the branch in the middle of the run, so it reads unmerged, and a
        # re-run keyed to it stays by B3: no stay, and end commits on the branch
        r, env = merged_world("t-land-merged-rerun-b3")
        run_start(env, "/feedback", "--key", "A-1")
        r.git("add", "notes.md")
        r.git("commit", "-q", "-m", "my notes")
        got = run_start(env, "/feedback", "--rerun", "--key", "A-1")
        check(got.get("branch") == A and got.get("stay") is None and stay_of(env) is None,
              "t_land_merged_rerun_b3: the re-run on B3 keeps no stay (%r)" % got)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        mine = r.git("rev-list", "-1", "--grep=^my notes$", "HEAD")
        want = lines.fill("row.scope", {"<sha7>": [head(r)[:7], mine[:7]], "<N>": 1, "<branch>": A,
                                        "<subject>": "my notes", "<path>": "notes.md"})
        check(got.get("row") == "scope" and got.get("print") == [want] and got.get("branch") == A and mine
              and on_origin(r, A) != head(r) and not untracked(r, FEED_A),
              "t_land_merged_rerun_b3: end commits on the branch, not pushed past the user's commit (%r)" % got)

        # t_land_merged_b3_g1: an unmerged branch a key of the run names (B3), with G1: the plain block, no stay, and end
        # commits on it as before
        r, env = world(tmp, "t-land-merged-b3")
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/ard.md", "a\n")
        r.commit_all("ACME-1 Add the ARD")
        r.write("notes.md", "n\n")
        r.write(RESUME, "r\n")
        plain = g1_plain(r, ["notes.md"])
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), plain] and got.get("branch") == PLUGIN and stay_of(env) is None,
              "t_land_merged_b3_g1: G1's plain block, no stay (%r)" % got)
        got = run_end(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, PLUGIN), plain]
              and got.get("branch") == PLUGIN and got.get("sha7") == head(r)[:7]
              and subject(r) == SUBJECT % ("ACME-1", "/feedback") and r.git("show", "--name-only", "--format=", "HEAD") == RESUME,
              "t_land_merged_b3_g1: end commits on the branch as before (%r)" % got)

        # t_land_merged_moved: HEAD moved off the merged branch before end (a new plugin branch, as a handoff cuts one):
        # end commits there as before, and repeats G1's plain block, since the commit runs
        r, env = merged_world("t-land-merged-moved")
        run_start(env, "/feedback")
        r.git("switch", "-q", "-c", "prd/A-1-y")
        got = run_end(env, "/feedback")
        check(got.get("row") == "origin-lacks" and got.get("branch") == "prd/A-1-y"
              and got.get("print") == [lacks_row(r, "prd/A-1-y"), g1_plain(r, ["notes.md"])] and got.get("sha7") == head(r)[:7]
              and r.git("show", "--name-only", "--format=", "HEAD") == RES_A and not untracked(r, RES_A),
              "t_land_merged_moved: end commits where HEAD now stands, with G1's plain block (%r)" % got)

        # t_land_merged_stopped (in process): the preflight stops early on the merged branch before its switch; it asks
        # branch-merged then, and the stay is recorded; end lands what the run wrote after it
        r, env = world(tmp, "t-land-merged-stopped")
        ff_merged(r, "t-land-merged-stopped-other", A, "specifications/PRD-A-1-x/prd.md")
        g["_settle"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["_settle"] = real_settle
        check(got.get("error") == "RuntimeError: boom" and got.get("branch") == A
              and stay_of(env) == stayed(A, "stopped"),
              "t_land_merged_stopped: the stop on the merged branch records the stay (%r)" % got)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [RES_A]) and gone(r, RES_A),
              "t_land_merged_stopped: end lands (%r)" % got)

        # t_land_merged_budget: a start that returned at its budget on the merged branch, whose next the run never
        # made, reached neither G1's nor B2's test; end asks branch-merged HEAD itself (§4 step 1) and lands
        r, env = world(tmp, "t-land-merged-budget")
        ff_merged(r, "t-land-merged-budget-other", A, "specifications/PRD-A-1-x/prd.md")
        h = head(r)
        got = run_start(env, "/feedback", "--budget", "0")
        rec = record(env, "/feedback") or {}
        check((got.get("next") or {}).get("run") and rec.get("stage") in START_STAGES and rec.get("branch") == A
              and stay_of(env) is None,
              "t_land_merged_budget: the start stopped at its budget on the branch, no stay (%r)" % rec)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)] and gone(r, RES_A)
              and landed_on_main(r, [RES_A]) and head(r) == h and r.git("symbolic-ref", "--short", "HEAD") == A
              and record(env, "/feedback") is None,
              "t_land_merged_budget: end lands on the branch the start did not leave (%r)" % got)

        # t_land_merged_budget_moved: the same stop, then HEAD on a branch the start never stood on (as a handoff cuts
        # one, at the merged tip): no stay is asked for, and end commits where HEAD stands, as before
        r, env = world(tmp, "t-land-merged-budget-moved")
        ff_merged(r, "t-land-merged-budget-moved-other", A, "specifications/PRD-A-1-x/prd.md")
        run_start(env, "/feedback", "--budget", "0")
        r.git("switch", "-q", "-c", "prd/A-1-y")
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, "prd/A-1-y")]
              and got.get("branch") == "prd/A-1-y" and got.get("sha7") == head(r)[:7] and not untracked(r, RES_A),
              "t_land_merged_budget_moved: end commits on the branch HEAD moved to (%r)" % got)

        # t_land_merged_budget_done: a record whose start finished holds no stay on a branch it did not leave, so end
        # asks nothing and commits there, as before -- the ask is for an unfinished start alone; an unfinished start on
        # a branch now unmerged that a key of the run names (B3's) holds none either, and end commits there
        r, env = world(tmp, "t-land-merged-budget-done")
        ff_merged(r, "t-land-merged-budget-done-other", A, "specifications/PRD-A-1-x/prd.md")
        r.git("fetch", "-q", "origin")
        seed(env, "/feedback", branch=A)
        r.write(RES_A, "r\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-plugin" and got.get("print") == [plugin_row(r, A)] and got.get("branch") == A
              and got.get("sha7") == head(r)[:7] and on_origin(r, A) == head(r) and not untracked(r, RES_A),
              "t_land_merged_budget_done: a finished start's record, end commits (%r)" % got)
        seed(env, "/feedback", branch=A, stage="settle", keys=["A-1"])
        r.write(RES_A, "r2\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-plugin" and got.get("print") == [plugin_row(r, A)] and got.get("branch") == A
              and got.get("sha7") == head(r)[:7] and on_origin(r, A) == head(r),
              "t_land_merged_budget_done: an unfinished start on an unmerged branch a key names, end commits (%r)" % got)

        # t_land_merged_nothing: the stay recorded and nothing of the run's dirty at end: step 3's nothing to commit
        # line stands, then the landing form with its not-landed Not done
        r, env = merged_world("t-land-merged-nothing")
        run_start(env, "/feedback")
        os.remove(os.path.join(r.path, RES_A))
        got = run_end(env, "/feedback")
        check(got.get("row") == "nothing" and got.get("print") == ["Specs repo: no session artifacts to commit",
                                                                  g1_unlanded(r, ["notes.md"], A, "merged")],
              "t_land_merged_nothing: nothing to stage, nothing to commit, the not-landed form (%r)" % got)

        # t_land_merged_declined: a recorded declined path is named on the row, after app.landed, before G1's block
        r, env = merged_world("t-land-merged-declined")
        run_start(env, "/feedback")
        ARD_A = "specifications/PRD-A-1-x/ard.md"
        r.write(ARD_A, "a\n")
        r.write(FEED_A, "f\n")
        got = cli("declined", "--command", "/feedback", "--path", ARD_A, env=env)
        check(got["_rc"] == 0, "t_land_merged_declined: the declined call ran (%r)" % got)
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default"
              and got.get("print") == [landed_row(r, 1, A) + "; the deliverable at %s remains uncommitted, as you asked"
                                       % ARD_A, g1_landing(r, ["notes.md"], A, "merged")]
              and untracked(r, ARD_A) and untracked(r, RES_A) and landed_on_main(r, [FEED_A]),
              "t_land_merged_declined: the row takes the declined append after app.landed (%r)" % got)

        # t_land_merged_g1_unknown: G1 on a plugin branch whose merge cannot be told (an origin with no default branch
        # yet, as in t_merged_unknown): the report once, beside G1's plain block; no stay, none on --rerun; end commits
        # as before
        bare = os.path.join(tmp, "t-land-merged-unknown.git")
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", bare], check=True)
        r = new_repo(tmp, "t-land-merged-unknown")
        r.git("remote", "add", "origin", bare)
        env = {"HOME": os.path.join(tmp, "home-t-land-merged-unknown"), "CLAUDE_CODE_SESSION_ID": "t-land-merged-unknown",
               "SPECS_PATH": r.path}
        os.makedirs(env["HOME"])
        r.git("switch", "-q", "-c", PLUGIN)
        r.write("specifications/PRD-ACME-1-x/prd.md", "p\n")
        r.commit_all("ACME-1 Add the PRD")
        r.write("notes.md", "n\n")
        r.write(RESUME, "r\n")
        plain = g1_plain(r, ["notes.md"])
        got = run_start(env, "/feedback", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), unknown(PLUGIN), plain] and stay_of(env) is None
              and (record(env, "/feedback") or {}).get("reported") == ["pre.merged-unknown " + PLUGIN],
              "t_land_merged_g1_unknown: the report once, G1's plain block, no stay (%r)" % got)
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1")
        check(got.get("print") == [env_line(r.path), plain] and stay_of(env) is None,
              "t_land_merged_g1_unknown: a --rerun reports nothing again, and keeps no stay (%r)" % got)
        got = run_end(env, "/feedback", "--commit-key", "ACME-1")
        check(got.get("row") == "origin-lacks" and got.get("print") == [lacks_row(r, PLUGIN), plain]
              and got.get("sha7") == head(r)[:7] and r.git("show", "--name-only", "--format=", "HEAD") == RESUME,
              "t_land_merged_g1_unknown: end commits on the branch as before (%r)" % got)

        # t_land_merged_refused_kill (in process): a kill right after the flush commits on the branch whose leave git
        # refused -- the commit that makes the branch read unmerged -- finds the stay already saved, and end lands
        r, env = refused_world("t-land-merged-kill")
        real_commit = g["commit_session_files"]

        def commit_then_kill(*args, **kw):
            real_commit(*args, **kw)
            raise KeyboardInterrupt

        g["commit_session_files"] = commit_then_kill
        killed = False
        try:
            with in_env(env):
                start(r.path, "/feedback", ("A-1",))
        except KeyboardInterrupt:
            killed = True
        finally:
            g["commit_session_files"] = real_commit
        check(killed and subject(r) == SUBJECT % ("NOISSUE", "/feedback") and stay_of(env) == stayed(A, "refused"),
              "t_land_merged_refused_kill: the stay saved before the flush commits (%r)" % record(env, "/feedback"))
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default" and got.get("print") == [landed_row(r, 1, A)]
              and landed_on_main(r, [FEED_A]) and gone(r, FEED_A),
              "t_land_merged_refused_kill: end lands on the saved stay (%r)" % got)

        # t_land_merged_g1_kill (in process): a kill right after G1's stay is saved finds G1's block saved beside it, so
        # end's landing repeats that block, in the landing form
        r, env = merged_world("t-land-merged-g1-kill")
        real_stay = g["_stay"]

        def stay_then_kill(*args, **kw):
            real_stay(*args, **kw)
            raise KeyboardInterrupt

        g["_stay"] = stay_then_kill
        killed = False
        try:
            with in_env(env):
                start(r.path, "/feedback")
        except KeyboardInterrupt:
            killed = True
        finally:
            g["_stay"] = real_stay
        rec = record(env, "/feedback") or {}
        check(killed and rec.get("stay") == stayed(A, "g1") and rec.get("guard") == "G1"
              and rec.get("guard_block") == g1_plain(r, ["notes.md"]) and rec.get("guard_paths") == ["notes.md"],
              "t_land_merged_g1_kill: the stay saved with G1's block (%r)" % rec)
        r.write(FEED_A, "f\n")
        got = run_end(env, "/feedback")
        check(got.get("row") == "pushed-default"
              and got.get("print") == [landed_row(r, 1, A), g1_landing(r, ["notes.md"], A, "merged")],
              "t_land_merged_g1_kill: end's landing, then the notice in the landing form (%r)" % got)

        # The run's snapshot (specs-repo-git §7): the session files dirty when a fresh start that is not a --rerun took
        # it, each kept as a blob, narrowed as each call returns to the paths still dirty.
        B = "prd/B-2-y"
        S_FILE = "specifications/PRD-ACME-1-x/dev-workflows/feedback/s.md"

        def blob(r, path):
            """The blob id of <path>'s working copy, as git would store it; nothing written."""
            return r.git("hash-object", "--", path)

        def stored(r, sha):
            return subprocess.run(["git", "-C", r.path, "cat-file", "-e", sha], stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL).returncode == 0

        # t_snap_g1: G1 ends the preflight on a branch no key names; the snapshot names the dirty session file, with a
        # blob the object store holds, and not notes.md, which is not the plugin's
        r, env = world(tmp, "t-snap-g1")
        other_key(r)
        r.write("notes.md", "n\n")
        r.write(S_FILE, "t-snap-g1\n")
        got = run_start(env, "/feedback", "--key", "ACME-1")
        want = blob(r, S_FILE)
        check(got.get("guard") == "G1" and got.get("start_dirty") == {S_FILE: want}
              and (record(env, "/feedback") or {}).get("start_dirty") == {S_FILE: want} and stored(r, want),
              "t_snap_g1: the snapshot names the session file, its blob written (%r)" % got)

        # t_snap_narrowed: on main, the dirty session file the flush commits leaves the snapshot as the call returns
        r, env = world(tmp, "t-snap-narrowed")
        r.write(S_FILE, "t-snap-narrowed\n")
        got = run_start(env, "/feedback")
        check(got.get("start_dirty") == {} and (record(env, "/feedback") or {}).get("start_dirty") == {}
              and subject(r) == SUBJECT % ("NOISSUE", "/feedback")
              and r.git("show", "--name-only", "--format=", "HEAD") == S_FILE,
              "t_snap_narrowed: the flushed session file narrowed out of the snapshot (%r)" % got)

        # t_snap_misrooted: SPECS_PATH below the top level -- no snapshot, and no object written for the session file
        r, env = world(tmp, "t-snap-misrooted")
        nested = "specs/" + S_FILE
        r.write(nested, "t-snap-misrooted\n")
        got = run_start(env, "/feedback", specs=os.path.join(r.path, "specs"))
        check(got.get("specs_git") == "misrooted" and "start_dirty" in got and got["start_dirty"] is None
              and (record(env, "/feedback") or {}).get("start_dirty") is None and not stored(r, blob(r, nested)),
              "t_snap_misrooted: no snapshot, no object written (%r)" % got)

        # t_snap_status_failed (in process): status cannot run, so no snapshot is taken, and its report, once, is in
        # the record's reported -- which end's line reads (§4 step 1)
        r, env = world(tmp, "t-snap-status")
        r.write(S_FILE, "t-snap-status\n")
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["status"] = real_status
        reports = [x for x in got.get("print") or [] if x.startswith("Specs preflight: could not list the uncommitted")]
        check(got.get("error") is None and "start_dirty" in got and got["start_dirty"] is None and len(reports) == 1
              and (record(env, "/feedback") or {}).get("start_dirty") is None
              and "pre.status-failed" in ((record(env, "/feedback") or {}).get("reported") or [])
              and not stored(r, blob(r, S_FILE)),
              "t_snap_status_failed: no snapshot, pre.status-failed reported once and recorded (%r)" % got)

        # t_snap_rerun: a leftover dirty before the run's first start (G1 keeps every preflight from its flush), a
        # session file the run writes after it, then start --rerun: the snapshot is the first start's, the new file not
        # in it; with the leftover gone, the next --rerun narrows it to nothing
        r, env = world(tmp, "t-snap-rerun")
        LEFT, NEW = FEED + "left.md", FEED + "new.md"
        r.write("notes.md", "n\n")
        r.write(LEFT, "t-snap-rerun leftover\n")
        first = run_start(env, "/feedback")
        r.write(NEW, "t-snap-rerun new\n")
        got = run_start(env, "/feedback", "--rerun")
        want = {LEFT: blob(r, LEFT)}
        check(first.get("start_dirty") == want and got.get("start_dirty") == want
              and (record(env, "/feedback") or {}).get("start_dirty") == want,
              "t_snap_rerun: the re-run carries the first start's snapshot, and only that (%r)" % got)
        os.remove(os.path.join(r.path, LEFT))
        got = run_start(env, "/feedback", "--rerun")
        check(got.get("start_dirty") == {} and (record(env, "/feedback") or {}).get("start_dirty") == {},
              "t_snap_rerun: a re-run only narrows the snapshot it carries (%r)" % got)

        # Every stay kept in the record (specs-repo-git §4 step 1): the branch, its kind, its merged flag, its reason.
        # t_stay_g1_unkeyed: G1 on a branch no key of the run names -- the landing form, unkeyed's alternative, with the
        # plain Fix; the plain block saved for end
        r, env = world(tmp, "t-stay-g1-unkeyed")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "ACME-1")
        rec = record(env, "/feedback") or {}
        want = stayed(B, "g1", kind="unkeyed", merged=False)
        shown = (got.get("print") or [""])[-1]
        check(got.get("print") == [env_line(r.path), g1_landing(r, ["notes.md"], B, "unkeyed")]
              and got.get("stay") == want and rec.get("stay") == want
              and rec.get("guard_block") == g1_plain(r, ["notes.md"])
              and "on main, not on prd/B-2-y, which no key of this run names" in shown
              and "Fix:      git -C \"%s\" status\n" % r.path in shown,
              "t_stay_g1_unkeyed: G1's landing form, the stay kept, the plain block saved (%r)" % got)

        # t_stay_g1_keyed: a key of the run names the branch -- the plain block, its reworded Not done, no stay
        r, env = world(tmp, "t-stay-g1-keyed")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "B-2")
        check(got.get("print") == [env_line(r.path), g1_plain(r, ["notes.md"])] and "stay" in got and got["stay"] is None
              and stay_of(env) is None and "did not commit or push" in (got.get("print") or [""])[-1],
              "t_stay_g1_keyed: G1's plain block, no stay (%r)" % got)

        # t_stay_g1_commit_key: the start's commit key names the branch -- no stay
        r, env = world(tmp, "t-stay-g1-commit-key")
        other_key(r)
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--commit-key", "B-2")
        check(got.get("print") == [env_line(r.path), g1_plain(r, ["notes.md"])] and "stay" in got and got["stay"] is None
              and stay_of(env) is None, "t_stay_g1_commit_key: no stay (%r)" % got)

        # t_stay_g1_merged: G1 on a fast-forward-merged branch a key of the run names -- merged wins: the landing form,
        # merged's alternative, its Fix and If ignored; kind and flag merged
        r, env = world(tmp, "t-stay-g1-merged")
        ff_merged(r, "t-stay-g1-merged-other", A, "specifications/PRD-A-1-x/prd.md")
        r.write("notes.md", "n\n")
        got = run_start(env, "/feedback", "--key", "A-1")
        shown = (got.get("print") or [""])[-1]
        check(got.get("print") == [env_line(r.path), g1_landing(r, ["notes.md"], A, "merged")]
              and got.get("stay") == stayed(A, "g1") and stay_of(env) == stayed(A, "g1")
              and "which is merged into main" in shown and "Fix:      git -C \"%s\" switch main && " % r.path in shown,
              "t_stay_g1_merged: the landing form, merged's alternative (%r)" % got)

        # t_stay_unlisted_b4 (in process): status cannot run, so B4 stays and says so, and keeps the branch as a stay
        r, env = world(tmp, "t-stay-unlisted-b4")
        other_key(r)
        g["status"] = broken_status
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["status"] = real_status
        unlisted = lines.fill("pre.stay.unlisted", {"<branch>": B, "<default>": "main",
                                                    lines.placeholder("pre.stay.unlisted", "<switched"): 1})
        want = stayed(B, "unlisted", kind="unkeyed", merged=False)
        check((got.get("print") or [""])[-1] == unlisted and got.get("branch") == B and got.get("error") is None
              and got.get("stay") == want and stay_of(env) == want,
              "t_stay_unlisted_b4: pre.stay.unlisted's B4 alternative, the stay kept (%r)" % got)

        # t_stay_b4_refused: an index.lock -- the flush is Locked, git refuses B4's switch, and the preflight stops,
        # the stay kept before it does
        r, env = world(tmp, "t-stay-b4-refused")
        other_key(r)
        r.write(S_FILE, "t-stay-b4-refused\n")
        lock = os.path.join(r.path, ".git", "index.lock")
        open(lock, "w").close()
        try:
            got = run_start(env, "/feedback", "--key", "ACME-1")
        finally:
            os.remove(lock)
        shown = got.get("print") or [""]
        want = stayed(B, "refused", kind="unkeyed", merged=False)
        check(lines.preflight_form(T["row.locked"]) in shown and str(got.get("error")).startswith("git switch main: ")
              and shown[-1] == lines.fill("pre.stopped", {"<the error>": got.get("error")}) and got.get("branch") == B
              and got.get("stay") == want and stay_of(env) == want,
              "t_stay_b4_refused: Locked, B4's switch refused, pre.stopped, the stay kept (%r)" % got)

        # t_stay_stopped (in process): the preflight stops before B4's switch; the early stop's ask keeps the stay
        r, env = world(tmp, "t-stay-stopped")
        other_key(r)
        real_disposition = g["_disposition"]
        g["_disposition"] = boom
        try:
            with in_env(env):
                got = start(r.path, "/feedback", ("ACME-1",))
        finally:
            g["_disposition"] = real_disposition
        want = stayed(B, "stopped", kind="unkeyed", merged=False)
        check(got.get("error") == "RuntimeError: boom" and got.get("branch") == B and got.get("stay") == want
              and stay_of(env) == want, "t_stay_stopped: the early stop keeps the stay (%r)" % got)

        # t_stay_cleared: a --rerun whose merged-branch leave git refuses keeps a stay, its flush then commits on the
        # branch, and B4 leaves it: the switch that leaves the branch clears the stay
        r, env = refused_world("t-stay-cleared")
        r.write("notes.md", "n\n")
        first = run_start(env, "/feedback")
        os.remove(os.path.join(r.path, "notes.md"))
        got = run_start(env, "/feedback", "--rerun")
        shown = got.get("print") or []
        check(first.get("stay") == stayed(A, "g1")
              and any(x.startswith("Specs preflight: could not switch from merged prd/A-1-x to main (") for x in shown)
              and got.get("branch") == "main" and got.get("b4_left") == A and "stay" in got and got["stay"] is None
              and stay_of(env) is None,
              "t_stay_cleared: the re-run's B4 leaves the branch, and the stay it kept goes with it (%r)" % got)

        # t_start_json: every call's JSON -- a fresh start, a --rerun, a split start and its resumes, SPECS_PATH unset,
        # an early stop -- holds stay, start_dirty, midrun and started, and no merged_stay; started is the record's
        r, env = world(tmp, "t-start-json")
        r.git("switch", "-q", "-c", "spec/B-1-y")
        r.git("push", "-q", "-u", "origin", "spec/B-1-y")
        session_commit(r, "spec/B-1-y", "PRD-B-1-y")  # an unpushed commit the settle loop pushes: --budget 0 splits
        r.git("switch", "-q", "main")
        chain = follow(run_start(env, "/feedback", "--budget", "0"), env)
        started = (record(env, "/feedback") or {}).get("started")
        calls = chain + [run_start(env, "/feedback"), run_start(env, "/feedback", "--rerun"),
                         run_start(env, "/feedback", specs="")]
        real_disposition = g["_disposition"]
        g["_disposition"] = boom
        try:
            with in_env(env):
                calls.append(start(r.path, "/feedback"))
        finally:
            g["_disposition"] = real_disposition
        check(len(chain) > 1 and all(fields(c) and "merged_stay" not in c for c in calls)
              and all(c.get("started") == started for c in chain) and started
              and calls[-1].get("started") == (record(env, "/feedback") or {}).get("started"),
              "t_start_json: stay, start_dirty, midrun and started on every call (%r)" % [sorted(c) for c in calls])

        # t_snap_rerun_unset: a --rerun with SPECS_PATH unset, run from inside another repository, whose status would
        # list none of the run's paths: the gate did not pass, so the carried snapshot is left as it was
        r, env = world(tmp, "t-snap-rerun-unset")
        LEFT = FEED + "left.md"
        r.write("notes.md", "n\n")
        r.write(LEFT, "t-snap-rerun-unset leftover\n")
        first = run_start(env, "/feedback")
        elsewhere = new_repo(tmp, "t-snap-rerun-unset-elsewhere")
        got = run_start(env, "/feedback", "--rerun", specs="", cwd=elsewhere.path)
        want = {LEFT: blob(r, LEFT)}
        check(first.get("start_dirty") == want and got.get("gate") == "unset" and got.get("start_dirty") == want
              and (record(env, "/feedback") or {}).get("start_dirty") == want,
              "t_snap_rerun_unset: the carried snapshot is not narrowed against another repository (%r)" % got)

        # t_stay_b4_commit_key: only the start's commit key names the branch -- B3, as the run key set's own: no B4
        # switch, and no stay
        r, env = world(tmp, "t-stay-b4-commit-key")
        other_key(r)
        h = head(r)
        got = run_start(env, "/feedback", "--commit-key", "B-2")
        check(got.get("branch") == B and got.get("b4_left") is None and head(r) == h
              and r.git("symbolic-ref", "--short", "HEAD") == B and "stay" in got and got["stay"] is None
              and stay_of(env) is None and got.get("print") == [env_line(r.path)],
              "t_stay_b4_commit_key: the commit key names the branch, so B4 does not leave it (%r)" % got)

        # t_rerun_commit_key: a start whose B4 leaves the branch, then a --rerun whose commit key alone names it -- the
        # run's own, as B3 reads it: the re-run switches back, and B3 keeps it there
        r, env = world(tmp, "t-rerun-commit-key")
        other_key(r)
        first = run_start(env, "/feedback", "--key", "ACME-1")
        got = run_start(env, "/feedback", "--rerun", "--key", "ACME-1", "--commit-key", "B-2")
        check(first.get("branch") == "main" and first.get("b4_left") == B
              and got.get("branch") == B and got.get("b4_left") is None
              and r.git("symbolic-ref", "--short", "HEAD") == B and got.get("print") == [env_line(r.path)]
              and stay_of(env) is None,
              "t_rerun_commit_key: the re-run switches back to the branch its commit key names (%r)" % got)

        # t_snap_bug (in process): a coding error inside the snapshot -- an injected TypeError -- reaches the start's
        # error and pre.stopped, never hidden as a snapshot that could not be taken
        r, env = world(tmp, "t-snap-bug")
        r.write(S_FILE, "t-snap-bug\n")
        real_snapshot = g["snapshot"]

        def snapshot_bug(root):
            raise TypeError("a bug in the snapshot")

        g["snapshot"] = snapshot_bug
        try:
            with in_env(env):
                got = start(r.path, "/feedback")
        finally:
            g["snapshot"] = real_snapshot
        check(got.get("error") == "TypeError: a bug in the snapshot"
              and (got.get("print") or [""])[-1] == lines.fill("pre.stopped", {"<the error>": got.get("error")}),
              "t_snap_bug: the TypeError surfaces as the start's error (%r)" % got)

    def scenarios_skill(tmp):
        """The specs-git skill's text, held to the CLI it drives, to the loader that routes to it and to the run-key-set
        file both name; and the session variable, never written with a $ where checks 5 and 9 would read it as one."""
        def read(*parts):
            try:
                with open(os.path.join(HERE, "..", *parts), encoding="utf-8") as fh:
                    return fh.read()
            except OSError:  # a missing file fails the checks that read it, never the whole selftest
                return ""

        skill = read("skills", "specs-git", "SKILL.md")
        loader = read("skills", "reference", "SKILL.md")
        option = re.compile(r"(?<![\w-])--[a-z][a-z0-9-]*")

        def accepted(*sub):
            """The options `specs-git.py [<sub>] --help` lists, as a user meets the parser."""
            got = cli(*(sub + ("--help",)))
            return got["_rc"], got.get("_stdout", ""), set(option.findall(got.get("_stdout", "")))

        rc, top_help, top = accepted()
        listed = re.search(r"\{([a-z,-]+)\}", top_help)
        subcommands = set(listed.group(1).split(",")) if listed else set()
        subs = {s: accepted(s)[2] for s in ("start", "end", "declined")}

        # The one option the skill names that is no option of this script: /docs-brand's, where it says that run calls
        # none of this.
        other = "started `--inline`"

        def skill_problems(text):
            problems = []
            if text.count(other) != 1:
                problems.append("the skill names /docs-brand's --inline %d time(s), not once" % text.count(other))
            union = top | subs["start"] | subs["end"] | subs["declined"]
            for o in sorted(set(option.findall(text.replace(other, ""))) - union):
                problems.append("%s is no option of specs-git.py, or of its start, end or declined" % o)
            for o, where in re.findall(r"^- `(--[a-z][a-z0-9-]*)[^`]*` \((start and end|start|end)\)", text, re.M):
                for s in where.split(" and "):
                    if o not in subs[s]:
                        problems.append("%s, named for %s, is no option of %s" % (o, s, s))
            for call in re.findall(r'specs-git\.py" declined ([^`]*)`', text):
                for o in sorted(set(option.findall(call)) - subs["declined"]):
                    problems.append("%s, in the declined call, is no option of declined" % o)
            return problems

        # k_skill_options
        got = skill_problems(skill)
        check(rc == 0 and {"start", "end", "declined"} <= subcommands and "--specs" in top
              and all("--command" in subs[s] for s in subs) and all("--resume" in subs[s] for s in ("start", "end"))
              and got == [], "k_skill_options: every option the skill names is the CLI's, where it names it (%r, %r)"
              % (sorted(subcommands), got))
        bites = ((skill + "\n`--no-such-option`\n", "--no-such-option is no option"),
                 (skill.replace("- `--no-preflight` (end)", "- `--no-preflight` (start)"), "--no-preflight, named for start"),
                 (skill.replace(other, "started `--inline-x`"), "--inline"),
                 (skill.replace("declined --command /<name> --path", "declined --command /<name> --paths"),
                  "--paths, in the declined call"))
        for text, want in bites:
            got = skill_problems(text)
            check(any(want in p for p in got), "k_skill_options: a skill naming the wrong option fails (%s: %r)" % (want, got))

        # k_skill_fields: every JSON field the skill names is one the script returns
        _, flow_lines = _flow()
        start_keys = set(_start_result({"print": [], "rec": {}, "lines": flow_lines}, None, None, None))
        end_keys = set(_end_result())
        next_keys = set(_replay_next("/s", "/feedback", "main", False)) & set(_resume_next("/feedback", {}))

        def field_problems(text):
            problems = []
            sections = {s.split("\n", 1)[0]: s for s in text.split("\n## ")}
            listed = re.search(r"results from the last `start` JSON(.*?)wherever your command's text reads them",
                               sections.get("Start", ""), re.S)
            if listed is None:
                problems.append("the Start section lists no field it reads")
            named = set(re.findall(r"`([a-z_][a-z0-9_]*)`", re.sub(r"\([^)]*\)", "", listed.group(1) if listed else "")))
            named |= set(re.findall(r"A `([a-z_][a-z0-9_]*)` field", sections.get("Start", "")))
            for f in sorted(named - start_keys):
                problems.append("Start reads %s, which start's JSON does not hold" % f)
            shared = set(re.findall(r"JSON's `([a-z_][a-z0-9_]*)`|JSON (?:names|with) `([a-z_][a-z0-9_]*)`", text))
            for f in sorted({f for pair in shared for f in pair if f} - (start_keys & end_keys)):
                problems.append("the skill reads %s, which start's and end's JSON do not both hold" % f)
            for f in sorted(set(re.findall(r"`next\.([a-z_][a-z0-9_]*)`", text)) - next_keys):
                problems.append("next.%s is no key of the next a replay or a resume returns" % f)
            return problems

        got = field_problems(skill)
        listed = re.search(r"results from the last `start` JSON(.*?)wherever your command's text reads them", skill, re.S)
        check(listed is not None and "`stay`" in listed.group(1) and "stay" in start_keys
              and "`merged_stay`" not in skill and "merged_stay" not in start_keys
              and "`stay` field" in skill.split("## Where the script cannot start", 1)[-1],
              "k_skill_fields: Start names stay, which an end run by hand reads (§3.3), and merged_stay nowhere")
        check(got == [] and {"print", "error", "next", "specs_git", "b2_left", "replaced"} <= start_keys
              and {"run", "timeout_ms", "on_timeout"} == next_keys,
              "k_skill_fields: every JSON field the skill names is the script's (%r)" % got)
        for old, new, want in (("`b2_left`", "`b2_lefts`", "Start reads b2_lefts"),
                               ("A `replaced` field", "A `replacement` field", "Start reads replacement"),
                               ("`next.timeout_ms`", "`next.timeout`", "next.timeout is no key"),
                               ("JSON with `error` set", "JSON with `failure` set", "reads failure")):
            got = field_problems(skill.replace(old, new))
            check(skill.count(old) >= 1 and any(want in p for p in got),
                  "k_skill_fields: a renamed field fails (%s: %r)" % (want, got))

        # k_loader_routes
        para = next((p for p in loader.split("\n\n") if "workflows-core:specs-git" in p), "")
        front = loader.split("---", 2)[1] if loader.startswith("---") else ""
        tools = re.search(r"^allowed-tools:(.*)$", front, re.M)
        check(all(s in para for s in ('Skill(skill: "workflows-core:specs-git", args: "start")', 'args: "end"',
                                      'args: "specs-repo-git specs-preflight"', 'args: "specs-repo-git commit-artifacts"'))
              and tools is not None and "Skill" in [t.strip() for t in tools.group(1).split(",")],
              "k_loader_routes: the loader routes both requests to the skill and may call it (%r)"
              % (tools.group(0) if tools else None))

        # k_key_set_file
        rel = "skills/specs-git/run-key-set.md"
        named = "${CLAUDE_PLUGIN_ROOT}/" + rel
        check(os.path.isfile(os.path.join(HERE, "..", rel)) and named in skill and named in loader,
              "k_key_set_file: %s exists, and the skill and the loader both name it" % rel)

        # k_key_set_quotes: run-key-set.md quotes specs-repo-git word for word -- each of its quotations found,
        # whitespace-collapsed, in §3 up to §3.3, and each paragraph of §3.2 from *Run key set* to its end equal to one of
        # them -- so a word changed on either side fails, and so does a sentence or a paragraph §3.2 gains there
        key_set = read("skills", "specs-git", "run-key-set.md")
        srg = read("references", "specs-repo-git.md")

        def key_set_problems(text, ref):
            try:
                s3 = ref[ref.index("\n## 3. "):ref.index("\n### 3.3")]
                s32 = ref[ref.index("\n### 3.2"):ref.index("\n### 3.3")]
            except ValueError:
                return ["specs-repo-git has no §3, §3.2 or §3.3 heading"]
            quotes = [" ".join(re.sub(r"(?m)^> ?", "", p).split()) for p in text.split("\n\n") if p.startswith(">")]
            paras = s32.split("\n\n")
            first = next((k for k, p in enumerate(paras) if p.lstrip().startswith("**Run key set:**")), None)
            problems = [] if quotes else ["run-key-set.md quotes nothing"]
            if first is None:
                problems.append("§3.2 has no *Run key set* paragraph")
            whole = " ".join(s3.split())
            problems += ["run-key-set.md's quotation %d is not in specs-repo-git §3 (%s…)" % (k + 1, q[:60])
                         for k, q in enumerate(quotes) if q not in whole]
            for p in paras[first:] if first is not None else []:
                c = " ".join(p.split())
                if c and c not in quotes:
                    problems.append("specs-repo-git §3.2's paragraph %s… is not quoted whole in run-key-set.md" % c[:60])
            return problems

        got = key_set_problems(key_set, srg)
        check(got == [] and key_set.count("\n> ") >= 6,
              "k_key_set_quotes: run-key-set.md quotes §3.2 from *Run key set* on, and §3's sentence, word for word (%r)" % got)
        word, said = "contributes **both**", "contributes **each**"
        tail = "`NOISSUE`.\n\n### 3.3"
        for label, text, ref, want in (
                ("a word of the file", key_set.replace(word, said), srg, "quotation 1 is not in"),
                ("the same word of §3.2", key_set, srg.replace(word, said), "quotation 1 is not in"),
                ("a word of §3's sentence", key_set, srg.replace("and resolves afterwards", "and resolves later"),
                 "quotation 6 is not in"),
                ("a sentence §3.2 gains", key_set, srg.replace(tail, "`NOISSUE`. One sentence more.\n\n### 3.3"),
                 "is not quoted whole")):
            got = key_set_problems(text, ref)
            check(key_set.count(word) == 1 and srg.count(word) == 1 and srg.count(tail) == 1
                  and srg.count("and resolves afterwards") == 1 and any(want in p for p in got),
                  "k_key_set_quotes: %s changed fails (%r)" % (label, got))

        # k_branch_check_midrun (P23, M6): branch-check's two mid-run stops -- It does not's (no switch) and It does's
        # (no merge) -- prose a run follows and no template of the script's, each held verbatim in phase-handoff §6.1's
        # bullet and in the part file generated from it, naming no git command: check-branch-check reads which commands
        # request branch-check, never the stop's wording
        handoff = read("references", "phase-handoff.md")
        part_file = read("reference-parts", "phase-handoff", "branch-check.md")
        midrun_stops = {
            "It does not": ("<finding> — <command>'s run in this session is still open on <branch>, so no switch is "
                            "named here: finish or end that run first, then re-run."),
            "It does": ("<finding> — <command>'s run in this session is still open on <branch>, so no merge is named "
                        "here: finish or end that run first, then re-run."),
        }

        def midrun_problems(ref, part):
            try:
                s61 = ref[ref.index("\n### 6.1 "):ref.index("\n### 6.2 ")]
            except ValueError:
                return ["phase-handoff has no §6.1 or §6.2 heading"]
            bullets = {}
            for line in s61.split("\n"):
                m = re.match(r"- \*\*(It does not|It does)\*\*", line)
                if m:
                    bullets[m.group(1)] = line
            problems = []
            for label, stop in sorted(midrun_stops.items()):
                if stop not in bullets.get(label, ""):
                    problems.append("phase-handoff §6.1's *%s* bullet does not hold its mid-run stop verbatim" % label)
                if stop not in part:
                    problems.append("branch-check.md does not hold the *%s* mid-run stop verbatim" % label)
                if "git" in stop or re.search(r"\b(?:switch|merge)\s+(?:<|-|to\b|into\b)", stop):
                    problems.append("the *%s* mid-run stop names a git command" % label)
            return problems

        got = midrun_problems(handoff, part_file)
        check(got == [], "k_branch_check_midrun: both mid-run stops are in their §6.1 bullets and the part file, "
                         "naming no git command (%r)" % got)
        for label, stop in sorted(midrun_stops.items()):
            got = midrun_problems(handoff.replace(stop, ""), part_file)
            check(handoff.count(stop) == 1
                  and got == ["phase-handoff §6.1's *%s* bullet does not hold its mid-run stop verbatim" % label],
                  "k_branch_check_midrun: the *%s* stop dropped from §6.1 fails (%r)" % (label, got))

        # k_no_dollar_session: the directories check-docs.sh's checks 5 and 9 read a $NAME in, of every plugin
        session_var = "CLAUDE_CODE_SESSION_ID"
        written = ("$" + session_var, "${" + session_var)

        def dollar_session(plugins):
            found, scanned = [], set()
            for plugin in sorted(os.listdir(plugins)):
                for d in ("commands", "agents", "references", "hooks", "skills"):
                    for dirpath, _, files in os.walk(os.path.join(plugins, plugin, d)):
                        for name in sorted(files):
                            full = os.path.join(dirpath, name)
                            try:
                                with open(full, encoding="utf-8") as fh:
                                    text = fh.read()
                            except (OSError, UnicodeDecodeError):
                                continue
                            scanned.add(os.path.realpath(full))
                            if any(w in text for w in written):
                                found.append(os.path.relpath(full, plugins))
            return found, scanned

        found, scanned = dollar_session(os.path.join(HERE, "..", ".."))
        check(found == [] and os.path.realpath(SPECS_REPO_GIT) in scanned,
              "k_no_dollar_session: no plugin file checks 5 and 9 read names the session variable after a $ (%r)" % found)
        fake = os.path.join(tmp, "k-dollar", "plugins")
        for rel, body in (("x/hooks/a.sh", "echo " + written[0] + "\n"), ("x/skills/s/SKILL.md", written[1] + "}\n"),
                          ("x/references/plain.md", session_var + "\n"), ("x/scripts/b.py", written[0] + "\n")):
            os.makedirs(os.path.dirname(os.path.join(fake, rel)), exist_ok=True)
            with open(os.path.join(fake, rel), "w", encoding="utf-8") as fh:
                fh.write(body)
        found, _ = dollar_session(fake)
        check(sorted(found) == ["x/hooks/a.sh", "x/skills/s/SKILL.md"],
              "k_no_dollar_session: both written forms found, the plain name and a scripts/ file not (%r)" % found)

    def scenarios():
        with tempfile.TemporaryDirectory() as tmp:
            scenarios_status(tmp)
            scenarios_branch_merged(tmp)
            scenarios_branch_key(tmp)
            scenarios_push_scope(tmp)
            scenarios_owner_repo(tmp)
            scenarios_mode(tmp)
            scenarios_state(tmp)
            scenarios_lines(tmp)
            scenarios_gate(tmp)
            scenarios_end(tmp)
            scenarios_land(tmp)
            scenarios_replay(tmp)
            scenarios_start(tmp)
            scenarios_skill(tmp)

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

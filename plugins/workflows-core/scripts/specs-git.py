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
  specs-git.py declined --command /<name> [--started <stamp>] --path <p> [--path <p>]...
  specs-git.py --specs "<value>" specs-root-check
  specs-git.py --specs "<value>" start --command /<name> [--key <K>]... [--commit-key <K>] [--register-rebuild <path>]
               [--rerun] [--resume] [--budget <seconds>] [--started <stamp>, with --rerun or --resume]
  specs-git.py --specs "<value>" end --command /<name> [--commit-key <K>] [--register-rebuild <path>] [--no-preflight]
               [--misrooted-stdin] [--session-branch-created <sha7>] [--declined <p>]... [--resume] [--started <stamp>]
  specs-git.py --specs <root> replay --for start|end --command /<name> --branch <name> [--set-upstream] [--timed-out]
               [--started <stamp>]
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
import calendar
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
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SELFTEST_FILE = os.path.join(HERE, "..", "..", "..", "scripts", "selftests", "specs_git_selftest.py")


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


def declined(command, paths, started=None):
    """The paths the run's user declined to stage, appended (unique, in order) to the record of this session
    and <command> -- the one <started> names (state.find; specs-repo-git §7's declined --started), else
    <command>.json; a record the command's start never made is created there, marked as not started by the script,
    its started <started> where given (a derived path, P35). A record load() returns None for (another version, or
    unparsable) is overwritten and reported created: it serves no later call."""
    state, _ = _flow()
    if not paths:
        raise NotRun("usage: declined needs at least one --path")
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    session = state.session_id()
    at = _record_at(state, session, command, started)
    rec = state.load(session, command, at=at)
    found = rec is not None
    if rec is None:
        rec = state.new(command, session=session, started_by_script=False)
        if started is not None:
            rec["started"] = started
    added = []
    for p in paths:
        if p not in added:
            added.append(p)
    rec["declined"] = rec["declined"] + [p for p in added if p not in rec["declined"]]
    state.save(session, command, rec, at=at)
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
# detail, where the refspec push has nowhere to go (PERMANENT_ROWS) or nothing to build on (origin-lacks: <default-ref>
# names no commit, specs-repo-git §4 step 1 (3)); moved and locked pass. unfinished is no held change's: its journal
# entry is dropped and no run retries it, so, like every refusal of the here form, it is marked permanent
# (specs-repo-git §6), outside this set.
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


def commit_session_files(root, message, on_write=None, on_staged=None, exclude=()):
    """specs-repo-git §2.1 steps 1-3 and §4 step 4: stage the ARTIFACT paths status() lists, less <exclude> (the held
    files §3.4's flush and §4 step 2 leave out: _held_unchanged), then commit, by pathspec,
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
    left_out = set(exclude)
    paths = [p for p in status(root)["artifact"] if p not in left_out]
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


def _replay_next(specs, command, branch, set_upstream, for_="end", started=None):
    """The call a rejected push hands the run (specs-repo-git §4 step 6): the replay, in a Bash call of its own, and
    the same with --timed-out where the harness ends that call at its timeout. <for_>: end, or start for §3.4's.
    <started>, so the replay reads and writes the record the call that hands it over did (P19): for end, the end's
    --started, repeated; for start, the record's own started, whether or not the start call was given one, as every
    start-side next names it (_resume_next)."""
    run = "python3 %s --specs %s replay --for %s --command %s --branch %s%s%s" % (
        shlex.quote(os.path.abspath(__file__)), shlex.quote(specs), for_, shlex.quote(command), shlex.quote(branch),
        " --set-upstream" if set_upstream else "", " --started " + shlex.quote(started) if started else "")
    return {"run": run, "timeout_ms": REPLAY_TIMEOUT_MS, "on_timeout": run + " --timed-out"}


def _resume_next(command, args, budget=None, started=None):
    """The call that goes on with a start the replay or a budget stop interrupted: start --resume, repeating the start
    call's --specs, every --key in order, --commit-key and --register-rebuild as the record's <args> hold them, so the
    resume passes resumable's argument test, and --budget where the record's <budget> holds one (a start call's that
    was not the default) -- how the preflight is split across calls, which no argument test reads -- and --started
    <started>, the record's own, whether or not the call was given one, so the resume goes on with that record
    (state.find, specs-repo-git §3.5) however long after it is made: past resumable's 15 minutes it starts afresh and
    takes that record over, never setting it aside; in a Bash call of its own, start's 600 s, nothing to run on a
    timeout."""
    parts = ["--specs", args.get("specs") or "", "start", "--command", command]
    for key in args.get("keys") or []:
        parts += ["--key", key]
    for flag, field in (("--commit-key", "commit_key"), ("--register-rebuild", "register_rebuild")):
        if args.get(field):
            parts += [flag, args[field]]
    if budget is not None:
        parts += ["--budget", "%g" % budget]
    if started:
        parts += ["--started", started]
    run = " ".join(["python3", shlex.quote(os.path.abspath(__file__))] + [shlex.quote(p) for p in parts + ["--resume"]])
    return {"run": run, "timeout_ms": START_TIMEOUT_MS, "on_timeout": None}


def _stop(run, row, printed, line):
    """An outcome of §4 step 1 -- misrooted, blocked or silent: what it prints, the record removed. A blocked row's
    <line> already carries §6's declined append where it takes one (_declined, _declined_checked); the misrooted row
    takes none, so no git status runs in a path the run has found wrong (§6), and the silent no-op prints nothing."""
    _remove(run)
    return _end_result(print=printed, line=line, row=row, record=run["record"])


def _put(run, rec):
    """<rec> saved as the run's record: at run["record_path"], the file --started named (state.find), else at
    <command>.json (P19). Every save end, its replay and declined make goes through here."""
    run["state"].save(run["session"], run["command"], rec, at=run.get("record_path"))


def _remove(run):
    """The run's record removed, at run["record_path"] (else <command>.json); then, where that was <command>.json,
    the newest record of the same command parked for this run (state.unpark) restored, its protects as it stands, or
    dropped where §3.5's open-run test no longer finds that run on HEAD's branch (_parked_keep)."""
    state, session, command = run["state"], run["session"], run["command"]
    at = run.get("record_path")
    state.remove(session, command, at=at)
    if at is None or at == state.path(session, command):
        state.unpark(session, command, keep=_parked_keep)


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
    _remove(run)
    commit = commit or {}
    return _end_result(print=printed, line=line, row=row, sha7=commit.get("sha7"), files=commit.get("files"),
                       branch=branch, pushed=pushed, record=run["record"])


def _end_view(lines, rec, view, default, specs, stay, committed):
    """<view> with the G1 block the run's end repeats in the form specs-repo-git §5 gives the end (_g1_landing): the
    landing form where <stay>, the stay the end's landing ran on, stands; the plain block where none does; under a run
    typed mid-run, the mid-run form; its Not done by <committed>, whether the end committed the run's whole change. A
    G2 block in its mid-run form under a run typed mid-run (_g2_midrun), else as it is; none, as it is. A G1 or G2
    block's Fix switch to <default> is judged again (_make_default_fix)."""
    rec = rec or {}
    top = rec.get("specs") or specs
    if view.get("guard_block") and rec.get("guard") == "G2" and rec.get("midrun"):
        return dict(view, guard_block=_g2_midrun(lines, view["guard_block"], rec["midrun"]))
    if view.get("guard_block") and rec.get("guard") == "G2":
        return dict(view, guard_block=_make_default_fix(lines, top, default, rec.get("default_ref"), view["guard_block"]))
    if not view.get("guard_block") or rec.get("guard") != "G1":
        return view
    return dict(view, guard_block=_make_default_fix(lines, top, default, rec.get("default_ref"), _g1_landing(
        lines, view["guard_block"], (stay or {}).get("branch"), default, top, view["guard_paths"], stay,
        rec.get("midrun"), committed)))


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


def _kept_append(lines, kept, branch):
    """specs-repo-git §6's app.start-dirty-kept for the paths <kept> the guard of §4 step 1 (1) left out of the run's
    change -- already uncommitted when the run started, left in the working tree for a later commit on <branch>; ''
    where nothing was kept."""
    if not kept:
        return ""
    return lines.fill("app.start-dirty-kept", {"<path>": list(kept), "<branch>": branch})


def _landing_append(lines, commit, rec):
    """specs-repo-git §6's appends after a landing, in its order, for <commit>, which a landing made on <default>
    (its landing: the journal's pending, with moves and stuck): app.landed, naming the stayed branch and the stay's
    kind from <rec>'s stay; app.landed.unlisted where the run's start could not list the uncommitted paths
    (pre.status-failed in the record's reported, P12); app.start-dirty-kept where the guard left paths out (KEPT,
    _kept_append); the register clause for each security/<slug>/ the landing's
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
    out += _kept_append(lines, landing.get(KEPT), stay.get("branch"))
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
            _mark_held_shown(run, rec)
            _put(run, rec)
            return _end_result(print=list(run.get("pre") or []), sha7=commit["sha7"], files=commit["files"], branch=branch,
                               next=_replay_next(specs, run["command"], branch, check["set_upstream"],
                                                 started=run.get("started")),
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
            + _kept_append(lines, commit.get(KEPT), branch)
            + _appends(lines, _append_facts(specs, rec, branch, session)))
    return finish_end(run, row, line, view, commit=commit, branch=branch, pushed=pushed, hook=hook)


def _record_at(state, session, command, started):
    """The record file --started names (state.find, P19, P35), or None for <command>.json where none is given; NotRun
    where <started> is not a started stamp."""
    if started is None:
        return None
    if not state.STARTED_RE.fullmatch(started):
        raise NotRun("usage: --started takes the started stamp start returned, got %s" % started)
    return state.find(session, command, started)[0]


def end(specs, command, commit_key=None, register_rebuild=None, no_preflight=False, misrooted_notice=None,
        session_branch_created=None, declined=(), resume=False, started=None):
    """specs-repo-git §4's commit-artifacts for the run of this session and <command>, steps 1-7, on <specs>
    (SPECS_PATH as set, "" meaning unset). <misrooted_notice>: the lines of a notice that set misrooted outside the
    script (--misrooted-stdin), [] for none. <declined>: paths a declined call could not record. <started>: the run's
    start's started (--started), which names its record (state.find): every save and the removal go there (P19), and a
    stamp that names no record names the run's own derived path (P35); without it, <command>.json -- save on a
    --no-preflight end that finds there a record a start of the script made, which saves and removes at a derived path
    under a stamp of its own instead, that stamp then its --started (P37). A failure before the
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
           "wrote": False, "pre": [], "commit": None, "started": started,
           "record_path": _record_at(state, session, command, started)}
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
        try:  # this output carries any pre.held.changed line, and the record stays for --resume -- save where a signal
            rec = state.load(session, command, at=run["record_path"]) if _signal_of(e) is None else None  # ended the
            if rec is not None and _mark_held_shown(run, rec):  # call: no outcome, its output set aside by the harness
                _put(run, rec)  # that sent it
        except Exception:
            pass
        block = (run.get("view") or {}).get("guard_block")  # §6: a G1 or G2 block follows the outcome line, this one too
        return _end_result(print=list(run["pre"]) + [line] + ([block] if block else []), line=line,
                           sha7=commit.get("sha7"), files=commit.get("files"), branch=commit.get("branch"),
                           record=run["record"], error=error)


def _end(run, commit_key, register_rebuild, no_preflight, misrooted_notice, session_branch_created, declined, resume):
    state, lines, specs, session, command = (run[k] for k in ("state", "lines", "specs", "session", "command"))
    rec = state.load(session, command, at=run["record_path"])
    # P37 (M2): an end with no start and no --started meets at <command>.json a record a start of the script made --
    # another run's, a later run of its command typed while it is open among them: it never writes or removes that file,
    # but keeps a record of its own at a derived path, under a stamp of its own, as P35 does for a --started that names
    # no record, and never takes that record's end_commit for a resume of its own (§3.5's end with no start)
    apart = (no_preflight and run["record_path"] is None and rec is not None and bool(rec.get("started_by_script")))
    if apart:
        stamp = time.strftime(state.STAMP, time.gmtime())
        run["record_path"], run["started"] = state.stamped(session, command, stamp), stamp
    if resume and not apart and rec is not None and rec.get("end_commit") and state.saved_within(rec):
        pending = rec["end_commit"]
        landing = pending.get("landing")
        here = pending.get("here")
        if isinstance(here, dict) and not pending.get("sha7"):  # §4 step 1's here form, cut off before its row
            view = _view(rec, declined)
            run["view"] = _end_view(lines, rec, view, rec.get("default"), specs, None, False)  # first, as below
            run["wrote"] = True
            run["record"] = "found"
            got = _resume_here(run, rec, view, commit_key, here)
            if got is not None:
                return got
            # the journal dropped: step 1 goes on, from HEAD's branch (§4 step 1's here form)
        elif isinstance(landing, dict) and not pending.get("sha7"):  # §4 step 1's landing, cut off before it was saved
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
                changed = list(pending.get(HELD_CHANGED) or [])
                if commit is not rec["end_commit"]:
                    created = commit.pop("created", None)
                    if created and not rec.get("session_branch_created"):
                        rec["session_branch_created"] = created
                    if changed:  # kept for as long as the record holds that commit, so a resume cut off below finds
                        commit[HELD_CHANGED] = changed  # them again
                    rec["end_commit"] = commit
                    _put(run, rec)
                default = rec.get("default") or resolve_default(specs, False)["default"]
                if changed:  # §4 step 2: the held files the commit took as they stood, saved before it was made
                    held = _held_committed(lines, specs, changed, commit.get("paths") or [], default)
                    if not pending.get(HELD_SHOWN):  # no output that printed them has been returned yet
                        run["pre"].extend(held)
                        run["held_shown"] = bool(held)
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

    # §3.5's end with no start (P5): with no snapshot to tell this run's files from an open run's, where any record of
    # the session but the one --started names is an open run on HEAD's branch, nothing is written and nothing removed
    created = session_branch_created or (keep or {}).get("session_branch_created")
    if not found:
        opened = _open_beside(run, branch, g["top"])
        if opened is not None:
            return _midrun_kept(run, opened, branch, lines.T["reason.land.no-preflight"], view, {
                "specs": specs, "default": d["default"], "default_ref": d["default_ref"], "mode": mode,
                "session_branch": session_branch, "created": created}, remove=False)

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

    # A run typed mid-run (§3.5): the open run tested again (P36), on the branch HEAD is on. While it still stands
    # nothing moves under it -- no catch-up -- and, outside session-branch mode, a start that took no snapshot commits
    # nothing, by the landing or the here form alike, since nothing tells this run's files from that run's (§4 step 1
    # (1)); where it no longer stands, the change is taken against HEAD.
    midrun = rec.get("midrun") if found else None
    standing = bool(midrun) and _midrun_stands(run, midrun, branch, g["top"])
    here = midrun is not None and stay is None and mode != "on" and branch == midrun.get("branch")
    if standing and mode != "on" and (stay is not None or here) and rec.get("start_dirty") is None:
        return _midrun_kept(run, midrun, branch, lines.T["reason.land.no-snapshot"],
                            _end_view(lines, keep, view, d["default"], specs, stay, False),
                            _append_facts(specs, dict(keep, mode=mode, session_branch=session_branch,
                                                      session_branch_created=created, **d), branch))

    # Steps 2-4: the catch-up, then the commit. R2's boundary is the first repository write either makes, and just
    # before it the record is saved at stage end -- the one kept, else a new one in place of whatever stood -- with what
    # this call was given; and again just before the commit, with what it is about to make -- outside the mode, before
    # `git commit`, its branch, its base and each path's staged blob (_landed); in the mode, before the run's first
    # §8.2 commit, the session branch and its tip then (_landed_session) -- so --resume finds the run's commit where a
    # kill comes between it and the save naming it.
    message = session_subject(commit_key or (keep or {}).get("commit_key"), command)
    saved = keep if keep is not None else state.new(command, session=session, started_by_script=False, specs=specs)
    if keep is None and run.get("started"):  # a record at the path --started names is that run's (P35)
        saved["started"] = run["started"]
    saved.update(stage="end", end_commit=None, declined=view["declined"], mode=mode, session_branch=session_branch,
                 default=d["default"], default_ref=d["default_ref"], remote=d["remote"], stay=stay)
    for field, value in (("commit_key", commit_key), ("register_rebuild", register_rebuild),
                         ("session_branch_created", session_branch_created)):
        if value:
            saved[field] = value

    def boundary():
        _put(run, saved)
        run["wrote"] = True

    def about_to_commit(staged):
        saved["end_commit"] = dict({"branch": branch, "base": sb.rev(specs, "HEAD"), "staged": staged},
                                   **({HELD_CHANGED: changed} if changed else {}))
        _put(run, saved)

    # §5's G1 block as the end repeats it: until the outcome is known -- and for an early stop, and a line that
    # commits none of the run's files -- in the form that leaves to the outcome line what came of them
    run["view"] = _end_view(lines, keep, view, d["default"], specs, stay, False)
    if stay is not None:
        boundary()

        def on_move(pending):  # the landing's journal, saved just before <default> moves or is pushed (§4 step 1)
            saved["end_commit"] = {"branch": d["default"], "landing": pending}
            _put(run, saved)

        got = land(specs, branch, d["default"], d["default_ref"], message, saved.get("start_dirty"),
                   saved.get("register_rebuild"), facts=_land_facts(stay, command), on_move=on_move,
                   retry_remote=False)
        return _landing_end(run, saved, d, stay, got, view)
    shown = _end_view(lines, keep, view, d["default"], specs, None, True)
    if mode == "on":
        return _end_session(run, saved, d, branch, message, shown, boundary, catch=not standing)
    if here:  # §4 step 1's here form, in place of steps 2-4; None where its refusal sends the run on to them
        got = _here_end(run, saved, d, branch, message, view, boundary, standing, midrun)
        if got is not None:
            return got
    if not standing:  # §4 step 2's catch-up, never while the open run stands on HEAD's branch (§3.5)
        pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary)
        if pulled:
            run["pre"].append(pulled)
    exclude, changed = _end_held(specs, branch, d["default"], boundary)
    c = commit_session_files(specs, message, on_write=boundary, on_staged=about_to_commit, exclude=exclude)
    if c["status"] != "committed":
        row = {"nothing": "nothing", "locked": "locked", "failed": "commit-failed"}[c["status"]]
        line = _row_line(lines, row, {"error": c["error"]}) + _appends(lines, _append_facts(specs, saved, branch))
        return finish_end(run, row, line, run["view"], branch=branch)
    commit = {"sha7": c["sha"][:7], "files": len(c["paths"]), "branch": branch, "paths": c["paths"],
              "hook_paths": c["hook_paths"]}
    run["commit"] = commit
    saved["end_commit"] = dict(commit, **({HELD_CHANGED: changed} if changed else {}))  # for as long as it is held
    _put(run, saved)
    if changed:
        held = _held_committed(lines, specs, changed, c["paths"], d["default"])
        run["pre"].extend(held)
        run["held_shown"] = bool(held)
    return _push_step(run, saved, commit, d["default"], shown)


def open_run_keys(opened):
    """The <keys> of the clause naming a stopped run's ends (specs-repo-git §3.5, §5, §6): the open run <opened>'s key
    set -- a record's keys, or the keys its midrun carries -- joined by " and "; None where it holds none."""
    keys = [k for k in ((opened or {}).get("keys") or []) if isinstance(k, str) and k]
    return " and ".join(keys) or None


def _midrun_kept(run, opened, branch, clause, view, facts, remove=True):
    """specs-repo-git §6's mid-run row, <opened> the open run (its record, or the midrun naming it: its command, and its
    keys for the clause naming its ends) and <branch> HEAD's, with the reason clause <clause>:
    the session appends of <facts> less the unsupported clause, which the row never takes (P17), then the declined
    append, then the guard's block <view> holds. The record removed, save with <remove> false: an end with no start
    that found a run open writes and removes nothing (P5)."""
    lines = run["lines"]
    line = lines.fill("row.midrun-kept", {"<command>": opened.get("command"), "<keys>": open_run_keys(opened),
                                          "<branch>": branch, "<reason clause>": clause})
    line += _appends(lines, dict(facts, mode=None))
    if remove:
        return finish_end(run, "midrun-kept", line, view, branch=branch)
    line += _declined(run, view)
    printed = list(run["pre"]) + [line] + ([view["guard_block"]] if view.get("guard_block") else [])
    return _end_result(print=printed, line=line, row="midrun-kept", branch=branch, record=run["record"])


def _open_beside(run, head, top):
    """P5's test for an end with no start: the oldest record of the session but the one --started names -- every other
    command's (state.others) and this command's own <name>.json and parked ones (state.mine), though one marked
    protects: false, parked by a restart, never passes -- that the open-run test passes on HEAD's branch <head>, at
    <top>; None where none does."""
    state, session, command = run["state"], run["session"], run["command"]
    named = run["record_path"] if run.get("started") else None
    found = list(state.others(session, command)) + [rec for full, rec in state.mine(session, command) if full != named]
    found.sort(key=lambda rec: str(rec.get("started") or ""))
    now = time.time()
    return next((rec for rec in found if _open_run(rec, head, top, now)), None)


def _midrun_stands(run, midrun, head, top):
    """P36: whether the open run <midrun> ({command, started, branch, keys}), which this run was typed under, still stands
    on HEAD's branch <head>: its record, found by its started (state.find, never another run's), passes the open-run
    test (_open_run) at <top>. False where it no longer does -- its end ran, HEAD left the branch, its record was
    replaced, or marked protects: false by a later start of its command with the same run key set (a restart), or it
    is older than OPEN_DAYS."""
    if head is None or not isinstance(midrun, dict):
        return False
    state = run["state"]
    try:
        if not state.STARTED_RE.fullmatch(midrun.get("started") or ""):
            return False
        _path, rec = state.find(run["session"], midrun.get("command"), midrun["started"])
    except ValueError:
        return False
    return rec is not None and _open_run(rec, head, top, time.time())


def _here_end(run, saved, d, branch, message, view, boundary, standing, midrun):
    """specs-repo-git §4 step 1's here form at the end of a run typed mid-run that holds no stay, HEAD still on the
    branch it started on (<branch>), outside session-branch mode: the record saved (boundary), then land's here form,
    its journal saved as end_commit.here just before HEAD's branch moves (on_move); the outcome by _here_outcome."""
    boundary()

    def on_move(pending):
        saved["end_commit"] = {"branch": branch, "here": pending}
        _put(run, saved)

    got = land(run["specs"], branch, d["default"], d["default_ref"], message, saved.get("start_dirty"),
               saved.get("register_rebuild"), here=True,
               facts={"kind": None, "merged": None, "command": run["command"], "stayed": branch}, on_move=on_move)
    return _here_outcome(run, saved, d, branch, got, view, standing, midrun)


def _here_outcome(run, saved, d, branch, got, view, standing, midrun):
    """The here form's outcome, from land's <got>, on HEAD's <branch>. landed: where the open run still stands
    (<standing>), the here row -- its first alternative on the default branch or a plugin branch, its second on a
    branch this plugin does not push -- nothing pushed; where it no longer stands, the commit saved as end_commit and
    steps 5-7 for HEAD's branch (_push_step), its row the one that push gives, with no mid-run wording (P36); the here
    row carries app.start-dirty-kept where land's guard left paths out (_kept_append). there and
    nothing: step 3's nothing-to-commit row; locked: the Locked row; kept: where the open run stands, the mid-run row
    with the refused path's clause, <default> and <onto> both HEAD's branch (§6), and where it no longer stands, None:
    the step goes on to steps 2-4 (§4 step 1's here form). Each row carries §6's appends -- the mid-run row without the
    unsupported clause -- and G1's or G2's block from the plain <view>, in its mid-run form (_end_view), its Not done
    the not-committed one after a row that committed none of the run's files. Any other status raises."""
    lines, specs = run["lines"], run["specs"]
    default, status = d["default"], got["status"]
    if status == "landed":
        commit = {"sha7": got["sha"][:7], "files": got["files"], "branch": branch, "paths": got["paths"],
                  "hook_paths": []}
        if got.get("kept"):  # the guard's paths, for the row steps 5-7 give it (_push_step), a resumed one's too
            commit[KEPT] = list(got["kept"])
        run["commit"] = commit
        shown = _end_view(lines, saved, view, default, specs, None, True)
        if not standing:
            saved["end_commit"] = commit
            _put(run, saved)
            return _push_step(run, saved, commit, default, shown)
        alt = 0 if branch == default or branch_key(branch, [])["plugin_branch"] else 1
        line = lines.fill("row.here", {"<sha7>": commit["sha7"], "<N>": commit["files"], "<branch>": branch,
                                       "<command>": midrun.get("command"), "<keys>": open_run_keys(midrun),
                                       lines.placeholder("row.here", "<the next push"): alt})
        line += _kept_append(lines, got.get("kept"), branch)
        line += _appends(lines, _append_facts(specs, saved, branch))
        return finish_end(run, "here", line, shown, commit=commit, branch=branch)
    shown = _end_view(lines, saved, view, default, specs, None, False)
    if status == "kept":
        if not standing:
            return None
        clause = _land_clause(lines, got["refused"], branch, onto=branch)
        return _midrun_kept(run, midrun, branch, clause, shown, _append_facts(specs, saved, branch))
    if status in ("there", "nothing", "locked"):
        row = "locked" if status == "locked" else "nothing"
        line = (lines.fill("row." + row, {}) + _kept_append(lines, got.get("kept"), branch)
                + _appends(lines, _append_facts(specs, saved, branch)))
        return finish_end(run, row, line, shown, branch=branch)
    raise NotRun("the here form returned %s, for which §4 step 1 gives it no row" % status)


def _resume_here(run, rec, view, commit_key, journal):
    """end --resume of §4 step 1's here form cut off before its row: <journal>, the here journal's pending, which
    on_move saved as end_commit.here just before HEAD's branch moved. With an index.lock standing, nothing is done:
    the journal is left for a later call, the Locked row. With HEAD off the journal's branch, the journal entry is
    dropped -- so no later preflight commits the same change again there -- and None is returned: the end goes on from
    step 1. Otherwise the open run is tested again (P36) and the journal finished as P2 says (land's resume): the
    branch at its tip, or holding it, the restore step; still at its old tip, the here form again -- each outcome as
    the end gives it (_here_outcome); moved elsewhere, the entry dropped, and, where the open run still stands, the
    mid-run row with the unfinished clause, else None: the end goes on from step 1."""
    lines, specs = run["lines"], run["specs"]
    d = {k: rec.get(k) for k in ("default", "default_ref", "remote")}
    head, midrun = _head_branch(specs), rec.get("midrun") or {}
    if os.path.lexists(sb.git_paths(specs, "index.lock")[0][1]):
        line = lines.fill("row.locked", {}) + _appends(lines, _append_facts(specs, rec, head))
        return finish_end(run, "locked", line, run["view"], branch=head)
    if head is None or head != journal.get("onto"):
        _held_remove(specs, [journal["c2"]])
        rec["end_commit"] = None
        return None
    standing = _midrun_stands(run, midrun, head, gate(specs, notices=False)["top"])

    def on_move(pending):
        rec["end_commit"] = {"branch": head, "here": pending}
        _put(run, rec)

    got = land(specs, head, d["default"], d["default_ref"],
               session_subject(commit_key or rec.get("commit_key"), run["command"]), rec.get("start_dirty"),
               rec.get("register_rebuild"), facts={"kind": None, "merged": None, "command": run["command"],
                                                   "stayed": head}, on_move=on_move, resume=journal)
    if got["status"] == "kept" and (got["refused"] or {}).get("reason") == "unfinished":
        if standing:
            return _midrun_kept(run, midrun, head, _land_clause(lines, got["refused"], head, onto=head),
                                _end_view(lines, rec, view, d["default"], specs, None, False),
                                _append_facts(specs, rec, head))
        rec["end_commit"] = None
        return None
    return _here_outcome(run, rec, d, head, got, view, standing, midrun)


def _end_held(specs, branch, default, boundary):
    """§4 step 2's held files (§1 rule 8), outside session-branch mode, where no stay takes the landing: with HEAD on
    <default>, every held entry but a here journal dropped with its ref (P9) -- boundary() first, the drop being a
    write -- and ([], []); on any other branch (exclude, changed): the files the commit leaves out (_held_unchanged),
    and the held files changed since they were held (P8, _p8_gone), less those, which it commits as they stand."""
    entries = held_entries(specs)
    if not entries:
        return [], []
    if branch == default:
        drop = [e["c2"] for e in entries if not e.get("here")]
        if drop:
            boundary()
            _held_remove(specs, drop)
        return [], []
    exclude = _held_unchanged(specs, branch, default)
    gone = _p8_gone(specs)[1]
    return exclude, sorted(set().union(*gone.values()) - set(exclude))


def _mark_held_shown(run, rec):
    """Where this call's output carries §4 step 2's pre.held.changed lines (run["held_shown"]) and <rec> stays -- a
    rejected push's next naming the replay, or an error no signal caused (a signal's stop is no outcome: the caller
    does not ask) -- end_commit marks them shown (HELD_SHOWN), so a later end --resume rebuilds without printing them
    again. True where it marked; the caller saves <rec>."""
    pending = rec.get("end_commit")
    if run.get("held_shown") and isinstance(pending, dict) and pending.get(HELD_CHANGED):
        pending[HELD_SHOWN] = True
        return True
    return False


def _held_committed(lines, specs, changed, carried, default):
    """After a commit that carried <carried> -- §3.4's flush's, or §4 step 4's -- each held entry rebuilt without the
    files changed since it was held (P8, _apply_p8), where <changed> names any; and §3.4's pre.held.changed line for each
    of <changed> the commit carries, in order."""
    if not changed:
        return []
    _apply_p8(specs)
    carried = set(carried)
    return [lines.fill("pre.held.changed", {"<path>": p, "<default>": default}) for p in changed if p in carried]


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
    lines, specs = run["lines"], run["specs"]
    default, branch = d["default"], stay["branch"]
    for h in got["held_landed"]:
        run["pre"].append(lines.fill("pre.held.landed", {"<sha7>": h["sha"][:7], "<N>": h["files"],
                                                        "<default>": default, "<branch>": branch}))
    view = _end_view(lines, saved, view, default, specs, stay, got["status"] == "landed" and not got["stuck"])
    if got["status"] == "landed":
        commit = {"sha7": got["sha"][:7], "files": got["files"], "branch": default, "paths": got["paths"],
                  "hook_paths": [], "landing": dict(got["pending"] or {}, moves=got["moves"], stuck=got["stuck"],
                                                    **{KEPT: list(got.get("kept") or [])})}
        run["commit"] = commit
        saved["end_commit"] = commit
        _put(run, saved)
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
        line += _kept_append(lines, got.get("kept"), branch)
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
    lines, specs = run["lines"], run["specs"]
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
               "kept": list(landing.get(KEPT) or []),
               "stuck": None if stuck is None else {"sha": stuck["c2"], "paths": sorted(stuck["paths"]),
                                                    "refused": stuck["refused"]}}
    elif head is None or head != (stay or {}).get("branch"):
        _held_remove(specs, [landing["c2"]])
        rec["end_commit"] = None
        return None
    else:
        def on_move(pending):
            rec["end_commit"] = {"branch": d["default"], "landing": pending}
            _put(run, rec)

        got = land(specs, head, d["default"], d["default_ref"],
                   session_subject(commit_key or rec.get("commit_key"), run["command"]), rec.get("start_dirty"),
                   rec.get("register_rebuild"), facts=_land_facts(stay, run["command"]), on_move=on_move,
                   resume=landing, retry_remote=False)
    return _landing_end(run, rec, d, stay, got, view)


def _end_session(run, saved, d, head, message, view, boundary, catch=True):
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
    appends. Without <catch> -- a run typed mid-run whose open run still stands on HEAD's branch (§3.5) -- there is no
    catch-up, which would move HEAD's branch under that run; the mode's commit is as always."""
    lines, specs = run["lines"], run["specs"]
    session_branch = saved["session_branch"]

    def ending(row, line, facts=None):  # a row that commits nothing: the block in the form run["view"] holds for it
        return finish_end(run, row, line + _appends(lines, _append_facts(specs, saved, head, facts)), run["view"],
                          branch=head)

    if session_branch is None:
        pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary) if catch else None
        if pulled:
            run["pre"].append(pulled)
        row = "no-identity" if status(specs)["artifact"] else "nothing"
        return ending(row, lines.fill("row." + row, {}))

    def report(err):
        run["pre"].append(lines.fill("end.session-not-run", {"<the first line of its stderr>": err}))

    def created(base):
        saved["session_branch_created"] = base
        _put(run, saved)

    def pending():
        if not saved.get("end_commit"):
            saved["end_commit"] = {"branch": session_branch, "base": sb.rev(specs, "refs/heads/" + session_branch),
                                   "session": {}}
            _put(run, saved)

    sess = _Session(lines, specs, session_branch, d["default"], d["default_ref"], message, report, created)
    sess.before_commit = pending
    pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary, wrap=sess.wrap) if catch else None
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
    _put(run, saved)
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


def replay(specs, for_, command, branch, set_upstream=False, timed_out=False, started=None):
    """specs-repo-git §4 step 6's replay for the run of this session and <command>, in a call of its own: sb.replay of
    <branch> in process (unless <timed_out>), with the register_rebuild the record holds, read by classify_replay and
    rendered as its §6 row. <for_> end: end's object for the end_commit the record holds, every append end gives, the
    record removed. <for_> start: {print: [the row in its Specs preflight: form], next, error}, the record advanced --
    from flush (the current branch's replay) to settle, next naming start --resume; at settle-done, <branch> dropped
    from pending, next naming the next queued replay, or, none left, start --resume with the record at disposition.
    Exit 2 only before the record is found; after it, an exception is exit-0 JSON with error set and the stopped
    line, the record kept as it stood -- which is how a record with nothing for this call to replay is refused. A
    replay a signal ended prints nothing and leaves the record as it stood for the --timed-out call: the process ends
    by that signal (_exit_by). <started>, the --started the next that names this call carries -- the end's, repeated,
    or the start record's own -- names the record (P19); a next this call returns names the record by its own."""
    state, lines = _flow()
    if not state.COMMAND_RE.fullmatch(command):
        raise NotRun("usage: --command is /<name>, got %s" % command)
    session = state.session_id()
    at = _record_at(state, session, command, started)
    rec = state.load(session, command, at=at)
    if rec is None:
        raise NotRun("no record of %s in this session holds a replay" % command)
    run = {"state": state, "lines": lines, "specs": specs, "session": session, "command": command, "record": "found",
           "pre": [], "commit": None, "started": started, "record_path": at}
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
            + _kept_append(lines, commit.get(KEPT), branch)
            + _appends(lines, _append_facts(run["specs"], rec, branch)))
    view = _end_view(lines, rec, _view(rec), rec.get("default"), run["specs"], stay, not (landing or {}).get("stuck"))
    return finish_end(run, cls["row"], line, view, commit=shown, branch=branch, pushed=cls["row"] == "replayed")


def _replay_start(run, rec, branch, set_upstream, timed_out):
    """replay --for start: §3.4's replay of the current branch (stage flush, <branch> the one HEAD stands on, which
    the flush pushed -- tested save under <timed_out>, which moves no branch and renders the 420 s row from the record
    alone, so a checkout another session switched during the replay the harness ended still lets start go on), of
    <default>, which §3.2's held stage pushed with HEAD elsewhere (stage held: the replay moves it by update-ref alone,
    and the record goes on at guards), or of a branch the settle loop queued (stage settle-done, <branch> in pending,
    whose standing names the branch the run stands on). Its next -- the next queued replay, or start --resume -- names
    the record by its own started, whatever --started this call was given, as every start-side next does."""
    stage, pending = rec.get("stage"), list(rec.get("pending") or [])
    if stage == "flush" and (timed_out or branch == _head_branch(run["specs"])):
        standing = branch
    elif stage == "held" and branch == rec.get("default"):
        standing = _head_branch(run["specs"])
    elif stage == "settle-done" and any(p.get("branch") == branch for p in pending):
        standing = next(p for p in pending if p.get("branch") == branch).get("standing")
    else:
        raise NotRun("the record (stage %s) holds no replay of %s" % (stage, branch))
    result, error, partial = _run_replay(run["specs"], branch, rec.get("register_rebuild"), set_upstream, timed_out)
    cls = classify_replay(result, error, partial, timed_out)
    line = _replay_line(run["lines"], cls, result, _replay_facts(run, rec, cls, result, error, branch, standing, True))
    if stage == "flush":  # the settle loop computes its branches on entering, past the HEAD this replay moved
        rec["stage"], rec["settle_todo"] = "settle", None
    elif stage == "held":  # the push of <default> is the held stage's last step: the guards come next
        rec["stage"], rec["held_attempted"] = "guards", []
    else:
        rec["pending"] = [p for p in pending if p.get("branch") != branch]
        rec["stage"] = "settle-done" if rec["pending"] else "disposition"
    _put(run, rec)
    if stage == "settle-done" and rec["pending"]:
        nxt = _queued_next(run, rec)
    else:
        nxt = _resume_next(run["command"], rec.get("args") or {}, rec.get("budget"), rec.get("started"))
    return {"print": [line], "next": nxt, "error": None}


# start's budget: the seconds one call may spend, inside the 600 s Bash call the skill runs it in, and what each unit of
# capped calls may take -- each call's cap, and the KILL_AFTER seconds git_bounded gives its process group after it.
DEFAULT_BUDGET = 480
FETCH_COST = CAP + sb.KILL_AFTER
PULL_COST = CAP + sb.KILL_AFTER
PUSH_COST = LS_REMOTE_CAP + sb.KILL_AFTER + CAP + sb.KILL_AFTER  # push_check's ls-remote, then the push
FLUSH_COST = PULL_COST + PUSH_COST  # §3.4: the catch-up's pull or the merged-branch leave's, then the current branch's push
# The record's stages start goes on from, in order; done follows the last.
START_STAGES = ("fetch", "held", "guards", "flush", "settle", "settle-done", "disposition")


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
    run["state"].save(run["session"], run["command"], run["rec"], at=run.get("record_path"))


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
    not-committed form), and otherwise the Fix and If ignored are as they are; where True with a stay, the Not done is
    g1.landing.not_done.landed, which says the artifacts were committed and leaves the commit to the outcome line."""
    kind = lines.placeholder("g1.landing.not_done", "<which no key")
    v = {"<branch>": branch, "<default>": default, "<SPECS_PATH>": specs,
         "<path list>": " ".join(shlex.quote(p) for p in paths)}
    landing = {False: "g1.landing.not_done.unlanded", True: "g1.landing.not_done.landed"}.get(committed,
                                                                                          "g1.landing.not_done")
    if midrun:
        v.update({"<command>": midrun.get("command"), "<keys>": open_run_keys(midrun)})
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


# specs-repo-git §3.5's open-run test: how long a record is read as open, and the read of HEAD's reflog for a leave --
# its newest REFLOG_COUNT entries, the call capped at REFLOG_CAP seconds (sb.git_bounded).
OPEN_DAYS = 7
REFLOG_COUNT = 1000
REFLOG_CAP = 30
_REFLOG_ENTRY = re.compile(r"HEAD@\{([0-9]+)\} (.*)")
_CHECKOUT_MOVE = re.compile(r"checkout: moving from (\S+) to (\S+)")


def _started_at(rec):
    """<rec>'s started, in seconds since the epoch; None where it is not a STAMP."""
    try:
        return calendar.timegm(time.strptime(rec.get("started") or "", "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError, AttributeError):
        return None


def _left_since(root, branch, since):
    """Whether HEAD's reflog at <root> shows HEAD leaving <branch> at or after <since> (seconds since the epoch): a
    `checkout: moving from <branch> to <another branch>` entry among the REFLOG_COUNT newest that `reflog show
    --date=unix --format='%gd %gs' HEAD` prints, read newest first and no further back than <since>. A move from a
    branch to itself never counts, nor does a move onto <branch> from another -- an open run's own handoff onto its
    branch. False where the reflog cannot be read -- absent, disabled, or the call fails -- so the protection holds for
    as long as HEAD stands on the branch (specs-repo-git §3.5); a signal that ended the capped call is raised."""
    try:
        r = sb.git_bounded(root, REFLOG_CAP, "reflog", "show", "-n", str(REFLOG_COUNT), "--date=unix",
                           "--format=%gd %gs", "HEAD")
    except (NotRun, OSError) as e:
        if isinstance(e, NotRun) and _signal_of(e) is not None:
            raise
        return False
    if r.returncode != 0:
        return False
    for line in sb.text(r).split("\n"):
        entry = _REFLOG_ENTRY.fullmatch(line)
        if entry is None:
            continue
        if int(entry.group(1)) < since:
            break
        move = _CHECKOUT_MOVE.fullmatch(entry.group(2))
        if move is not None and move.group(1) == branch and move.group(2) != branch:
            return True
    return False


def _on_branch(rec, head):
    """§3.5's branch test: HEAD's branch <head> is the branch the record <rec> recorded, or one branch-key resolves to
    a key of its key set -- an open run that handed off onto its own branch (P13)."""
    return head is not None and (rec.get("branch") == head
                                 or bool(branch_key(head, [k for k in rec.get("keys") or [] if k])["key"]))


def _open_run(rec, head, top, now):
    """specs-repo-git §3.5's open-run test of the record <rec>, against HEAD's branch <head> in the repository whose top
    level is <top>, at <now> (seconds since the epoch): a start of this script made it (started_by_script), and that
    start set no specs_git flag (P34); it stands at done or at one of start's own stages (START_STAGES) and holds no
    end_commit; it is not marked protects: false; its top is <top>; it started within OPEN_DAYS; <head> passes the
    branch test (_on_branch); and HEAD's reflog shows no leave of <head> since its started (_left_since), read last."""
    if not isinstance(rec, dict) or not rec.get("started_by_script") or rec.get("specs_git"):
        return False
    if not (rec.get("stage") == "done" or rec.get("stage") in START_STAGES) or rec.get("end_commit"):
        return False
    if rec.get("protects") is False or not top or not rec.get("top"):
        return False
    if os.path.realpath(rec["top"]) != os.path.realpath(top):
        return False
    since = _started_at(rec)
    if since is None or now - since > OPEN_DAYS * 86400 or not _on_branch(rec, head):
        return False
    return not _left_since(top, head, since)


def _parked_keep(rec):
    """state.unpark's keep for a parked record <rec> (specs-repo-git §3.5): only one marked parked: true (N3), and only
    where the open-run test, applied to it, still finds that run on HEAD's branch -- HEAD, read in the parked record's
    own repository (its top), on the branch it recorded or one a key of it names (_on_branch), and HEAD's reflog
    showing no leave of that branch since its started (_left_since)."""
    top = rec.get("top") if isinstance(rec, dict) else None
    if not rec.get("parked") or not top or not os.path.isdir(top):
        return False
    head, since = _head_branch(top), _started_at(rec)
    if since is None or not _on_branch(rec, head):
        return False
    return not _left_since(top, head, since)


def _keys_differ(rec, keys):
    """M1 (specs-repo-git §3.5): whether the run key set the record <rec>'s start recorded and <keys>, a later start's
    of the same command, differ -- compared as sets, order-insensitive, and only where both hold a key: a second piece
    of work typed while the first stands, which keeps the first run protected. The same set, or either start
    recording none (a keyless command), is a restart, which ends that protection."""
    theirs = {k for k in (rec.get("keys") or []) if k} if isinstance(rec, dict) else set()
    ours = {k for k in keys if k}
    return bool(theirs) and bool(ours) and theirs != ours


def _restarts(state, session, command, keys, head, top, now):
    """The paths of this command's parked records (parked: true) that a plain start with the run key set <keys> ends
    the protection of (specs-repo-git §3.5): each one the open-run test passes on HEAD's branch <head> whose key set is
    not other than <keys> (_keys_differ) -- the same work typed again. A parked record whose key set differs stays
    protecting, as one marked protects: false already protects nothing."""
    return [full for full, o in state.mine(session, command)
            if full != state.path(session, command) and o.get("parked") is True and not _keys_differ(o, keys)
            and _open_run(o, head, top, now)]


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


def _g2_midrun(lines, block, midrun):
    """specs-repo-git §5's mid-run form of a rendered G2 <block>, any variant (P25): its Fix emptied, since no switch is
    to be run while the open run <midrun> ({command, started, branch, keys}) stands on the branch, and its If ignored
    g2.midrun.if_ignored, naming that run's command and branch. How the start prints it, and how end repeats the plain
    block the record keeps."""
    block = _block_part(block, "Fix:", "")
    return _block_part(block, "If ignored:", lines.fill("g2.midrun.if_ignored", {
        "<command>": midrun.get("command"), "<keys>": open_run_keys(midrun), "<branch>": midrun.get("branch")}))


def _make_default_fix(lines, specs, default, ref, block):
    """specs-repo-git §5 part 3: <block> with its Fix line, where that line opens with the switch to <default>
    (g2.self.fix's text, which G2's plain block and g1.merged.fix open with too), opening with fix.make-default in that
    switch's place where refs/heads/<default> names no commit and <ref>, <default-ref>, names one: the branch made with
    no configuration write, its upstream set best-effort behind a `;`, then `switch --no-guess`, so git's guess, whose
    upstream write half-moves the checkout where .git/config cannot be written (§3.5), is never reached, and the line
    runs again after a refused switch. Judged each time a block is printed: a form an earlier print made is turned back
    into the plain switch first, so the start's block and the end's repeat of it each name what the clone needs then.
    Any other block, or one with no default to name, is returned as it is."""
    if not block or not default or not ref:
        return block
    values = {"<SPECS_PATH>": specs, "<default>": default, "<default-ref>": ref}
    switch, made = lines.fill("g2.self.fix", values), lines.fill("fix.make-default", values)
    rows = block.split("\n")
    for i, row in enumerate(rows):
        if not row.startswith("Fix:"):
            continue
        pad = re.match(r"Fix: *", row).group(0)
        text = row[len(pad):]
        text = switch + text[len(made):] if text.startswith(made) else text
        if text == switch or text.startswith(switch + " "):
            missing = sb.rev(specs, "refs/heads/" + default) is None and sb.rev(specs, ref) is not None
            rows[i] = pad + (made + text[len(switch):] if missing else text)
        return "\n".join(rows)
    return block


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
    (§8.1). A switch that leaves the branch a stay names clears that stay (§4 step 1). Where no local <default>
    exists, _make_default creates it first, and the switch takes --no-guess, so git never makes the branch itself
    (§3.5): its own --guess writes an upstream as it switches, and where .git/config cannot be written it leaves the
    index and files on <default>'s tree with HEAD on the branch and exits 1, which this would read as a refusal."""
    rec, specs = run["rec"], run["specs"]

    def move():
        _make_default(specs, rec)
        r = sb.git(specs, "switch", "--no-guess", rec["default"], check=False)
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


def _make_default(specs, rec):
    """specs-repo-git §3.5: where no local <default> exists, create it at <default-ref> by update-ref against the null
    id, which writes no configuration, then set its upstream to origin/<default> best-effort -- a configuration write
    that moves nothing, left unset with no word where .git/config cannot be written. Nothing where the branch exists,
    or where <default-ref> names no commit (the switch that follows then refuses). A switch git then refuses leaves
    this branch at <default-ref>, holding nothing a push would publish."""
    default, ref = rec.get("default"), rec.get("default_ref")
    if not default or not ref or sb.rev(specs, "refs/heads/" + default):
        return
    tip = sb.rev(specs, ref)
    if not tip:
        return
    if sb.git(specs, "update-ref", "refs/heads/" + default, tip, "0" * len(tip), check=False).returncode != 0:
        return
    if rec.get("remote") == "origin" and ref == "origin/" + default:
        sb.git(specs, "branch", "--set-upstream-to=" + ref, default, check=False)


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
    unknown, as _disposition stays then. A run typed mid-run holds no branch B4 left -- its first start switched
    nothing -- so a re-run that carries its open run makes no switch back (specs-repo-git §3.5). A gate that did not pass leaves nothing more to do; otherwise §3.2's held
    stage comes next -- under misrooted, which it never runs under, the disposition. The budget's one unit here covers
    both fetches: this stage is a call's first, whose first unit always goes ahead."""
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

        def switch_back():  # --no-guess: a branch deleted since is never made again from origin's copy (§3.5)
            r = sb.git(specs, "switch", "--no-guess", left, check=False)
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
    _advance(run, "disposition" if misrooted else "held")


def _held_stage(run):
    """Stage held, specs-repo-git §3.2's held stage, after the fetch and before the guards (never under misrooted, which
    _fetch skips past; nothing on a detached HEAD, P9): where this worktree's held record or a held ref stands,
    retry_held with start's budget as its check (P28) -- first, off <default> and outside session-branch mode, the
    held files P8 takes out of their entries kept in held_changed for the flush's line (§3.4) -- then its lines
    (_held_lines) and the run's snapshot updated for each path it lifted (P11). A budget stop inside it prints what
    it did before the stop and propagates, the stage left at held for start --resume, which runs it again from its
    start, passing retry_held the entries already tried and reported (held_attempted), which it keeps and reports
    nowhere again; so does an error after its first write, which start reports. held_attempted is cleared as the
    stage ends. Then, outside session-branch mode with HEAD off <default>, <default>'s push: where local <default>
    holds commits a push would publish (_scope, origin being the remote; not measured where origin/<default> already
    holds local <default>, which leaves none), the budget checked, then _push, pre.pushed-left where it went; a
    rejection saves the record at held and returns next naming replay --for start --branch <default>, which
    _replay_start advances to guards (P21)."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default, head = rec["default"], _head_branch(specs)
    if head is None or not default:
        rec["held_attempted"] = []  # every exit of the stage clears it
        return _advance(run, "guards")
    outside = head != default and rec.get("mode") != "on"
    if held_entries(specs) or sb.text(sb.git(specs, "for-each-ref", "--count=1", "--format=%(refname)", HELD_REF)):
        if outside:
            gone = _p8_gone(specs)[1]
            changed = set().union(*gone.values())
            if changed:
                rec["held_changed"] = sorted(set(rec.get("held_changed") or []) | changed)
                _save(run)
        try:
            got = retry_held(specs, default, rec["default_ref"], rec.get("register_rebuild"),
                             check=lambda cost: run["budget"].check(cost), settled=rec.get("held_attempted") or [])
        except (_Stop, LandStopped) as e:
            _held_lines(run, head, getattr(e, "partial", None))
            raise
        _held_lines(run, head, got)
    local, up = sb.rev(specs, "refs/heads/" + default), sb.rev(specs, "refs/remotes/origin/" + default)
    if outside and rec.get("remote") == "origin" and local is not None \
            and not (up is not None and (local == up or sb.is_ancestor(specs, local, up))):
        commits = (_scope(run, default) or {}).get("commits")
        if commits:
            run["budget"].check(PUSH_COST)
            done = _push(run, default)
            if done["outcome"] == "pushed":
                _emit(run, lines.fill("pre.pushed-left", {"<N>": len(commits), "<branch>": default}))
            elif done["outcome"] == "rejected":
                _save(run)
                return _replay_next(specs, run["command"], default, done["set_upstream"], "start",
                                    started=run.get("started"))
    rec["held_attempted"] = []  # the stage is done: nothing resumes it in this start
    _advance(run, "guards")


def _held_lines(run, head, got):
    """The held stage's lines for retry_held's object <got> (None: nothing to print), in this order: pre.here.finished
    for each here journal it finished with a commit; pre.held.landed for each entry landed, <branch> HEAD's
    <head>; pre.held.failed for each held again, its tail by mode_takes; pre.held.stuck for each that will not
    land, once in a run (reported), so a resume after a budget stop does not print it twice. Each failed and stuck
    entry's c2 goes into held_attempted, which a resumed stage passes retry_held as settled. Then the run's snapshot
    (start_dirty, where the start took one) updated for each path a lift wrote back, landed and finished alike: to
    the blob written back, or out of it where that is HEAD's version (P11), and the record saved."""
    if not got:
        return
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default = rec["default"]
    for f in got.get("finished") or []:
        if f.get("here") and f.get("sha"):
            _emit(run, lines.fill("pre.here.finished", {"<branch>": f["branch"], "<sha7>": f["sha"][:7],
                                                         "<N>": f["files"]}))
    for x in got.get("landed") or []:
        _emit(run, lines.fill("pre.held.landed", {"<sha7>": x["sha"][:7], "<N>": x["files"], "<default>": default,
                                                  "<branch>": head}))
    tail = lines.placeholder("pre.held.failed", "<and the next run")
    for x in got.get("failed") or []:
        _emit(run, lines.fill("pre.held.failed", {"<default>": default, "<reason clause>": _land_clause(
            lines, x["refused"], default), tail: 1 if mode_takes(x["refused"]) else 0}))
    for x in got.get("stuck") or []:
        _once(run, "pre.held.stuck " + x["sha"], "pre.held.stuck", {
            "<default>": default, "<reason clause>": _land_clause(lines, x["refused"], default),
            "<SPECS_PATH>": rec.get("specs") or specs, "<sha7>": x["sha"][:7], "<specs-git.py's path>": SG_SCRIPT,
            "<default-ref>": rec["default_ref"]})
    tried = [x["sha"] for kind in ("failed", "stuck") for x in got.get(kind) or []]
    base = got["settled"] if "settled" in got else (rec.get("held_attempted") or [])  # as P8's rebuilds left it
    rec["held_attempted"] = list(dict.fromkeys(list(base) + tried))
    snap = rec.get("start_dirty")
    if isinstance(snap, dict):
        for x in [x for kind in ("landed", "finished") for y in got.get(kind) or [] for x in y.get("lifted") or []]:
            if x["blob"] == sb.blob(specs, "HEAD", x["path"]):
                snap.pop(x["path"], None)
            else:
                snap[x["path"]] = x["blob"]
    _save(run)


def _guards(run):
    """Stage guards, specs-repo-git §3.3: the first of G0, G1 and G2 that holds prints its §5 block, saved for end to
    repeat, and ends the preflight; G0 sets specs_git: blocked. G1 on a plugin branch then asks branch-merged HEAD
    (_ask_stay), once its block is in the record, so the stay's save holds both: on a branch the preflight would have
    left -- merged, or one no key of the run, nor its commit key, names -- outside session-branch mode, the stay is
    kept, reason g1, and G1 prints its landing form (§5, _g1_landing), the plain block saved for end; under a run typed
    mid-run, its mid-run form, stay or none. In session-branch mode
    with a session branch, G2 takes §5's session-branch lines, or, on the session branch itself, its own variant; with
    no identity, its no-identity variant. Under a run typed mid-run, G2 prints its variant's mid-run form (_g2_midrun),
    the variant's block saved for end."""
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
    elif found[0] == "G2" and rec.get("midrun"):
        shown = _g2_midrun(lines, found[1], rec["midrun"])
    _emit(run, _make_default_fix(lines, specs, rec["default"], rec.get("default_ref"), shown or found[1]))
    _advance(run, "done")


def _flush(run):
    """Stage flush, specs-repo-git §3.4: the catch-up; outside session-branch mode, a merged plugin branch left by B2's
    action before a flush would commit on it, then the dirty session files committed on the current branch and
    pushed, or, with none dirty, the retry of its push -- in the mode, _flush_session. The stage's capped calls are one
    budget unit, checked before the first of them -- before the catch-up's lift in the mode: the stage resumes from its
    start, and a resume that repeated a catch-up whose pull failed would never reach the push. A push origin rejects as
    non-fast-forward returns next naming its replay, the stage left at flush, which the replay advances; the settle
    loop then starts on start --resume. Outside the mode, the held files whose working copy is still the version their
    entry holds are left out (_held_unchanged, read before the merged-branch leave and kept past it): only the rest
    count as dirty, and the commit takes only them; pre.held.changed follows the commit for each file the held stage
    took out of its entry as changed (held_changed) that the commit carries. Under a run typed mid-run (the record's
    midrun), nothing moves under the open run (P20): no catch-up, and, outside session-branch mode, no merged-branch
    leave, no commit on HEAD and no retry of HEAD's push -- the dirty files may be that run's work in progress; in the
    mode, whose commit never lands on HEAD, the mode's commit and push as always."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    rec["settle_todo"] = None  # computed on entering the settle loop, after this branch's replay, if any
    checked = []

    def unit():
        if not checked:
            run["budget"].check(FLUSH_COST)
            checked.append(True)

    default = rec["default"]
    sess = _session(run)
    midrun = rec.get("midrun")
    if not midrun:
        pulled = catch_up(specs, default, rec["default_ref"], on_write=unit, wrap=sess.wrap if sess else None)
        if pulled:
            _emit(run, pulled)
    if rec["mode"] == "on":
        return _flush_session(run, sess, unit)
    if midrun:
        return _advance(run, "settle")
    head = _head_branch(specs)
    listed = _status(run)
    exclude = _held_unchanged(specs, head, default) if listed else []
    left_out = set(exclude)
    dirty = [p for p in listed["artifact"] if p not in left_out] if listed else []
    refused = False
    if dirty and head != default and branch_key(head, [])["plugin_branch"]:
        merged = _merged(run, "HEAD", head)
        if merged["merged"]:
            unit()
            refused = not _leave(run, head, merged["test"], merged_flush=True)
            head = _head_branch(specs)
    if dirty:
        c = commit_session_files(specs, session_subject(rec["commit_key"], run["command"]), exclude=exclude)
        if c["status"] == "locked":
            _emit(run, lines.preflight_form(lines.T["row.locked"]))
        elif c["status"] == "failed":
            _emit(run, lines.preflight_form(_row_line(lines, "commit-failed", {"error": c["error"]})))
        if c["status"] != "committed":
            return _advance(run, "settle")
        for line in _held_committed(lines, specs, list(rec.get("held_changed") or []), c["paths"], default):
            _emit(run, line)
        rec["held_changed"] = []
        if refused:
            _emit(run, lines.fill("pre.merged-flush", {"<branch>": head, "<sha7>": c["sha"][:7], "<default>": default,
                                                       "<SPECS_PATH>": specs}))
    elif not (_scope(run, head) or {}).get("commits"):
        return _advance(run, "settle")
    unit()
    done = _push(run, head)
    if done["outcome"] == "rejected":
        _save(run)
        return _replay_next(specs, run["command"], head, done["set_upstream"], "start", started=run.get("started"))
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
    (§4 step 1, _keep_stay), reason unlisted, B2's and B4's alike -- and under a run typed mid-run (the record's
    midrun), they stay and print pre.stay.midrun, naming the open run's command -- the branch kept as a mid-run stay,
    reason mid-run, outside session-branch mode (_stay_kind). One line where more than one holds (P14): the misrooted
    one, else the unlisted one, else the mid-run one. B2's and B4's refused switch keeps the branch too (_leave,
    _b4). B3 and B4 resolve the branch against the run key set with the start's commit key beside it (_run_keys), the
    keys a stay's kind is read by, so a branch B4 leaves or would have left is always one an unkeyed stay names."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    head, default = _head_branch(specs), rec["default"]
    if head is not None and head != default and branch_key(head, [])["plugin_branch"]:
        merged = _merged(run, "HEAD", head)
        if merged["merged"] or not branch_key(head, _run_keys(rec))["key"]:
            midrun = rec.get("midrun")
            stay = ("pre.stay" if rec["specs_git"] == "misrooted"
                    else "pre.stay.unlisted" if "pre.status-failed" in rec["reported"]
                    else "pre.stay.midrun" if midrun else None)
            if stay:
                _emit(run, lines.fill(stay, {"<branch>": head, "<default>": default,
                                             "<command>": (midrun or {}).get("command"),
                                             lines.placeholder(stay, "<switched"): 0 if merged["merged"] else 1}))
                if stay == "pre.stay.unlisted":
                    _keep_stay(run, head, merged["merged"], "unlisted")
                elif stay == "pre.stay.midrun":
                    _keep_stay(run, head, merged["merged"], "mid-run")
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
    stage hands one over -- <default>'s replay at held, the current branch's at flush, the first queued one at
    settle-done -- else None."""
    rec = run["rec"]
    while rec["stage"] != "done":
        stage = rec["stage"]
        if stage == "fetch":
            _fetch(run)
        elif stage == "held":
            nxt = _held_stage(run)
            if nxt:
                return nxt
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
    the run's snapshot (§7), since a re-run takes none of its own and _close only narrows the one it carries, and the
    open run the earlier start was typed under (midrun), which start then tests again (specs-repo-git §3.5), and the
    run's earlier stamps (started_before, _earlier_stamps), so that any stamp its starts returned names the new record
    (state.find). Never the stay: each preflight derives its own (§4 step 1), so a stay's reason is always one this preflight met -- an
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
               start_dirty=dict(snap) if isinstance(snap, dict) else None,
               midrun=dict(old["midrun"]) if isinstance(old.get("midrun"), dict) else None,
               started_before=_earlier_stamps(old))


def _earlier_stamps(old):
    """The started_before of a record that takes over <old>, a record of the same run (specs-repo-git §7): <old>'s
    own, then <old>'s started -- each stamp once, oldest first."""
    out = []
    for stamp in _load_module("specs_git_state").earlier(old) + [old.get("started")]:
        if isinstance(stamp, str) and stamp and stamp not in out:
            out.append(stamp)
    return out


def _queued_next(run, rec):
    """The call that replays the first branch <rec>'s pending queue holds (specs-repo-git §3.4, after the loop), naming
    <rec> by its own started, as every start-side next does (_resume_next)."""
    queued = rec["pending"][0]
    return _replay_next(run["specs"], run["command"], queued["branch"], bool(queued.get("set_upstream")), "start",
                        started=rec.get("started"))


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
    rec["call_returned"] = True
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
          budget=DEFAULT_BUDGET, started=None):
    """specs-repo-git §3's specs-preflight for the run of this session and <command>, on <specs> (SPECS_PATH as set,
    "" meaning unset), with the run key set <keys>. A call that is not a resume prints the Environment: line and §3.1's
    notices (reads only), then saves a fresh record at stage fetch -- its first write -- takes the run's snapshot
    (_take_snapshot), save on a --rerun, and prunes -- having read, before that save, the open run this one is typed
    under, if any (rec["midrun"]), and parked this command's own record where it is an open run (replaced's parked:
    true), save on a --rerun or on a resume that does not meet the record as a plain start does (below); a failure before that save raises, so the caller exits 2 with nothing done, and after it every outcome is returned, an exception as error and the pre.stopped line, after
    _stop_stay's ask on a plugin branch (§4 step 1's stay). The
    stages (START_STAGES) then run from the record's own, each saved on entering it and resumable from its start.
    <resume> goes on with the saved stage only where state.resumable holds for this call's arguments; otherwise the
    call runs fresh. A resume with no <started> or <rerun> uses <command>.json only where that record is marked
    call_returned false with this call's arguments; any other, marked true or lacking the mark, it meets as a plain
    start does. <rerun> opens on this command's record, keeping what _carry
    keeps -- the open run its first start was typed under among them, tested again as end tests it (_midrun_stands),
    and dropped where it no longer stands; a re-run reads no other record for one, save where it finds no record of its
    own (dropped, or a session id changed since), when it reads them as a first start does, taking no snapshot as no
    re-run does: its first start's reading is lost, and the reading now only protects more -- and saves this call's
    arguments,
    its key set among them. <started>, with <rerun> or <resume> alone (--started, any stamp the run's starts
    returned): the record is the one state.find names, by its started or its started_before; where that is not
    <command>.json -- a parked run's -- a fresh call saves its record under a stamp of its own (state.stamped), parked
    and protects as that record was, and removes the file it replaced, <command>.json untouched; a fresh call keeps the
    record's stamps in started_before (_carry on a re-run; a resume started afresh on its own record likewise), so the
    run's earlier stamps still name the new record, as a re-run the harness stopped before its JSON needs; a resume
    goes on with it in place. A resume with no <started> that starts afresh takes <command>.json as its own record,
    marked call_returned false with this call's arguments -- the harness's stop of this run's own start, which
    returned no next. A plain start or a resume with no <started> writes the
    mark false at its first write, and its JSON, through _close or, on an error, apart from it, writes it true; a named
    call or a re-run, whose run holds a stamp already, never writes it false. A plain
    start parks this command's own open record, and so does a resume with no <started> that meets it as a plain start
    does; any other resume never does, even one that runs fresh, the record being its own run's. A stage that hands a replay over, and a unit of
    capped calls <budget> would not hold, return next: the replay, or start --resume with the record's args. Every
    next names the record by --started, its own started, whether or not this call was given one, so the call it leads
    to reaches that record however long after it is made, and a resume past resumable's 15 minutes takes it over
    rather than setting it aside. In
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
    if started is not None and not (rerun or resume):
        raise NotRun("usage: --started goes with --rerun or --resume, naming the run whose preflight runs again")
    session = state.session_id()
    args = {"specs": specs, "keys": list(keys), "commit_key": commit_key, "register_rebuild": register_rebuild}
    main = state.path(session, command)
    at = _record_at(state, session, command, started) or main
    old = state.load(session, command, at=at)
    run = {"state": state, "lines": lines, "specs": specs, "session": session, "command": command, "print": [],
           "budget": _Budget(budget), "rec": old, "record_path": None if at == main else at, "started": started}
    replaced, park, apart, restarts = None, False, None, []
    # A continuation given no --started is only ever the skill's remake of a first start the harness stopped before
    # it returned its JSON -- every next names the record (_resume_next) -- and that first start, a plain one, marked
    # its record call_returned false at its first write. So it uses <command>.json only where the record is marked so,
    # with this call's arguments; any other record, marked true or lacking the mark, it meets as a plain start does --
    # parked where it is an open run, else set aside (specs-repo-git §3.5). A record an end restored from parked is
    # marked true (state.unpark): the start that left it false was overtaken by the later one that parked it
    if resume and started is None and not rerun:
        resume = old is not None and old.get("call_returned") is False and old.get("args") == args
    fresh = not (resume and old is not None and old.get("stage") in START_STAGES and state.resumable(old, args))
    if fresh:
        env = env_line(specs)
        g = gate(specs)
        rec = state.new(command, session=session, specs=specs, env_line=env, gate=g["state"], top=g["top"],
                        keys=list(keys), commit_key=commit_key, register_rebuild=register_rebuild, args=args,
                        stage="fetch")
        if g["misrooted"]:
            rec.update(specs_git="misrooted", misrooted_notice=list(g["lines"]))
        # A continuation's own record, started afresh: the one --started names, or, named by none, the only record a
        # continuation given no --started uses, marked call_returned false with this call's arguments (above) -- left
        # by a plain start or a continuation given no --started, whose run learns the stamp only from the JSON that
        # call never returned, as the harness's stop of this run's own start leaves it. Taken over, never set aside
        # (replaced)
        own = resume and not rerun and old is not None
        if rerun and old is not None:
            _carry(rec, old)
        elif old is not None and at == main and not own:
            replaced = {"command": command, "started": old.get("started"), "parked": False}
        if own:  # taken over, never set aside (replaced)
            rec["started_before"] = _earlier_stamps(old)
        # §3.5, read before the first save: on a run's first start, the open run this one is typed under -- the oldest
        # record the open-run test passes on HEAD's branch, of another command, or of this one where the two starts'
        # run key sets differ (_keys_differ), but never the run's own; one marked protects: false never passes -- on a
        # re-run, the one its first start found (_carry), tested again as end tests it, never one that started since --
        # save a re-run that finds no record of its own, which reads them as a first start does -- and, on a plain
        # start, this command's own record where it is an open run, parked rather than replaced (the same command typed
        # twice, P4): still protecting where the key sets differ, and marked protects: false where they do not -- the
        # same set, or either empty, a restart -- as is each parked record of this command that is open and holds the
        # same set (_restarts)
        head = _head_branch(specs) if g["state"] == "pass" else None
        plain = not rerun and not resume
        if head is not None:
            now = time.time()
            if rerun and old is not None:
                if rec["midrun"] and not _midrun_stands(run, rec["midrun"], head, g["top"]):
                    rec["midrun"] = None
            else:
                own_path = None if plain else at  # a plain start's run has no record yet: every one is another run's
                found = list(state.others(session, command)) + [o for full, o in state.mine(session, command)
                                                                if full != own_path and _keys_differ(o, keys)]
                found.sort(key=lambda o: str(o.get("started") or ""))
                opened = next((o for o in found if _open_run(o, head, g["top"], now)), None)
                if opened is not None:
                    rec["midrun"] = {"command": opened.get("command"), "started": opened.get("started"),
                                     "branch": head, "keys": list(opened.get("keys") or [])}
            park = plain and old is not None and at == main and _open_run(old, head, g["top"], now)
            if plain:
                restarts = _restarts(state, session, command, keys, head, g["top"], now)
        if at != main:  # the run --started names keeps its record apart from <command>.json, under a stamp of its own
            rec.update(parked=(old or {}).get("parked") is True, protects=(old or {}).get("protects") is not False)
            apart, run["record_path"] = at, state.stamped(session, command, rec["started"])
        run["rec"], run["print"] = rec, [env] + list(g["lines"])
    # Every next this call returns names the record by its own started, named by this call or not (_resume_next)
    run["started"] = run["rec"]["started"]
    # This call's budget where it is not the default, outside args: how the preflight is split across calls, which the
    # start --resume a budget stop or a replay names repeats, and resumable's argument test never reads.
    run["rec"]["budget"] = None if budget == DEFAULT_BUDGET else budget
    # False from the first write of a plain start or a continuation given no --started -- calls whose run learns the
    # stamp only from their JSON -- until that JSON returns (_close, or the error path apart from it): a call the
    # harness stops leaves it so (own, above). Such a continuation goes on only with a record marked so already
    # (above), so only a fresh one writes it here, in its first save. A named call or a re-run, whose run holds a stamp
    # already, never writes it false: it leaves it as the record holds it, a fresh one's new record true
    if started is None and not rerun:
        run["rec"]["call_returned"] = False
    if fresh:
        if park and state.park(session, command, protects=_keys_differ(old, keys)):  # immediately before the first save
            replaced["parked"] = True
        for full in restarts:  # each parked open run of this command with the same key set: a restart (§3.5)
            state.stop_protecting(full)
        state.save(session, command, run["rec"], at=run["record_path"])  # the first write: exit 2 only before it
        if apart and old is not None and apart != run["record_path"]:
            state.remove(session, command, at=apart)
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
            nxt = _resume_next(command, run["rec"]["args"], run["rec"]["budget"], run["started"])
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
        except Exception:  # the JSON still returns, the record's stamp in it: the mark is saved true apart from _close
            run["rec"]["call_returned"] = True
            try:
                _save(run)
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
# A change's own extra field (specs-repo-git §4 step 1 (1)'s guard): kept, the snapshot paths of a class that is not
# appended that _own_commits left out of the change, each changed since the snapshot -- already uncommitted when the
# run started, they stay in the working tree for a later commit on the branch -- carried with the entry into its
# journal (_pending), so the run's row, a resumed one's included, names them (app.start-dirty-kept). Absent: none.
KEPT = "kept"
# end_commit's field for §4 step 2's held files changed since they were held, which its commit takes as they stand:
# saved before the commit is made (about_to_commit) and kept with it for as long as the record holds that commit, as a
# landing's moves are, so every end --resume that finds the commit made rebuilds their entries (_held_committed,
# idempotent) and prints pre.held.changed for them -- save where HELD_SHOWN is set: a call that printed the line
# returned its output and the record stayed (a replay's next, an error no signal caused), so a later resume does not
# print it again. An end that runs from step 1 on the record (a plain end, or --resume past 15 minutes) replaces that
# commit with end_commit None and prints no such line; its own commit, or the next held stage, settles the entry. A
# record without either field reads as none and not shown.
HELD_CHANGED = "held_changed"
HELD_SHOWN = "held_changed_shown"
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
    """The run's own change, as the landing and the here form (specs-repo-git §4 step 1) take it: c1, HEAD's tree with
    each <snap> path at its blob (None: removed), committed on HEAD; c2, c1's tree with each ARTIFACT path status() lists
    now at its working copy (written; its mode from the file; removed where no file stands), committed on c1 with
    <message>. §4 step 1 (1)'s guard (P1): a <snap> path whose class is not appended (sb.merge_class outside
    sb.SETTLED: a whole file, a record or a register) keeps c1's version in c2: already uncommitted when the run
    started, it is the branch's (S1), left out of the change -- neither landed, lifted nor committed here -- and stays
    in the working tree for a later commit on the branch; an appended file's entries added since the start go with the
    change. Returns (c1, c2, kept): c2 None where the two trees are
    one, nothing of the run's; kept the paths so left out whose working copy differs from the snapshot's version,
    sorted."""
    head = _commit(root, "HEAD")
    base = _tree(root, head)
    snap = snap or {}
    modes = {p: m for p, (m, _sha) in sb._tree_entries(root, head, sorted(snap)).items()} if snap else {}
    t1 = sb.tree_with(root, base, ["%s %s\t%s" % (modes.get(p, "100644"), b, p) if b else "0 %s\t%s" % (sb.ZERO, p)
                                   for p, b in sorted(snap.items())]) if snap else base
    c1 = sb.commit_tree(root, t1, [head], SNAPSHOT_MESSAGE)
    entries, kept = [], []
    for p in status(root)["artifact"]:
        full = os.path.join(root, p)
        if p in snap and sb.merge_class(p) not in sb.SETTLED:
            if sb.worktree_blob(root, p) != snap[p]:
                kept.append(p)
            continue
        if os.path.isfile(full) and not os.path.islink(full):
            mode = "100755" if os.stat(full).st_mode & 0o100 else "100644"
            entries.append("%s %s\t%s" % (mode, sb.worktree_blob(root, p, write=True), p))
        else:
            entries.append("0 %s\t%s" % (sb.ZERO, p))
    t2 = sb.tree_with(root, t1, entries) if entries else t1
    if t2 == t1:
        return c1, None, sorted(kept)
    return c1, sb.commit_tree(root, t2, [c1], message if message.endswith("\n") else message + "\n"), sorted(kept)


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
    """The journal's pending of <entry>: its PENDING_FIELDS, the moves a landing journal carries ([] for none), and the
    paths the guard left out of the change (KEPT, [] for none)."""
    return dict({k: entry[k] for k in PENDING_FIELDS}, **{JOURNAL_MOVES: list(entry.get(JOURNAL_MOVES) or []),
                                                          KEPT: list(entry.get(KEPT) or [])})


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


def _verified(root, entry, default, check=None, fetch=True):
    """P6: a landing journal's move is verified where <default> holds its tip -- or, for a remote_only one,
    origin/<default>, fetched (capped; <check>(cost) first) where it does not already, unless <fetch> is false: the
    local refs alone, as the held stage reads them under an index.lock (specs-repo-git §3.2)."""
    tip = entry.get("tip")
    if not tip:
        return False
    ref = ("refs/remotes/origin/" if entry.get("remote_only") else "refs/heads/") + default

    def holds():
        at = sb.rev(root, ref)
        return at is not None and (at == tip or sb.is_ancestor(root, tip, at))
    if holds():
        return True
    if not (fetch and entry.get("remote_only")) \
            or sb.git(root, "remote", "get-url", "origin", check=False).returncode != 0:
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


def _p8_gone(root, also=()):
    """P8's reading of the held record: (the held entries it covers -- refused set, no here journal, none of <also>'s --
    oldest first, {c2: the set of its paths changed since it was held}), each path read as _still_held reads it, with
    <also> as the newest link a held entry's path may chain to. Nothing is written: the held stage reads the paths
    here before retry_held's _apply_p8 rebuilds their entries, for the flush's line (specs-repo-git §3.4)."""
    skip = {x["c2"] for x in also}
    held = [e for e in held_entries(root) if e["refused"] is not None and not e.get("here") and e["c2"] not in skip]
    keep = _still_held(root, held + list(also))
    return held, {e["c2"]: set(e["paths"]) - keep[e["c2"]] for e in held}


def _apply_p8(root, also=(), moved=None):
    """P8, the step land's retries and retry_held share before their oldest-first walk, which a commit that carried
    held files changed since they were held repeats after it (_held_committed): over the held entries of the
    record (refused set), each path changed since it was held -- edited, committed, removed or restored, as
    _still_held reads it (_p8_gone), with <also> (the run's own change, in land; in no record, or in it under its own
    c2, and never rebuilt here) as the newest link a held entry's path may chain to -- leaves its entry, rebuilt without
    it (held_rebuild); an entry left with no file is dropped. <moved>, a dict where given, takes each rebuilt entry's
    old c2 -> its new c2, or None where it was dropped, so retry_held's settled list follows it. Returns how many were
    dropped."""
    held, gone = _p8_gone(root, also)
    dropped = 0
    for e in held:
        if gone[e["c2"]]:
            new = held_rebuild(root, e, gone[e["c2"]])
            if moved is not None:
                moved[e["c2"]] = new["c2"] if new is not None else None
            if new is None:
                dropped += 1
    return dropped


def _held_unchanged(root, head, default):
    """The held files §3.4's flush and §4 step 2 leave out (specs-repo-git §3.4, §4 step 2): [] with HEAD on
    <default>, where the held entries are dropped (P9); on any other branch, each path of an entry of this worktree's
    held record whose working copy is still the version that entry holds -- its c2 blob, None for a removal the working
    tree still lacks -- sorted. A held file changed since is not among them: it is committed as it stands (P8)."""
    if head == default:
        return []
    out = set()
    for e in held_entries(root):
        for p, b in e["paths"].items():
            if p not in out and sb.worktree_blob(root, p) == b:
                out.add(p)
    return sorted(out)


def _land_change(root, entry, default, default_ref, register_rebuild, in_record, remote=True, check=None,
                 on_move=None, own=False):
    """The landing's apply and move for one change -- a held entry retried, or the run's own (<entry>, c1 to c2): applied
    onto <default> by sb.own_change, the paths it refuses split off as one permanent held entry (P29), the rest
    committed on the result, journalled, then moved. C2's test first: where another worktree has <default> checked out,
    the result is built on <default-ref> and pushed by refspec where push_check leaves no row but scope (the push names
    one commit on <default-ref>, so push-scope does not apply), the local branch never moved (ruling C2); <remote> False
    keeps the change off that path (P28), as it stands, and <check>(cost) comes before its capped calls; where an
    origin exists, that path never builds on local <default>, whose own commits the push would publish unmeasured, so
    where <default-ref> names no commit -- an origin with no <default>, never or no longer -- the change is held,
    checked-out with the detail origin-lacks, permanent (P22). With no origin, <default-ref> is local <default> itself
    (specs-repo-git §3.2): the result is built there and then held as no-remote, permanent, nothing being pushable.
    Otherwise onto is <default-ref>'s commit where local <default> is absent or strictly behind it, else local
    <default> -- <default-ref> naming no commit counting as neither -- which
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
    pending carries the moves its register rebuild made (JOURNAL_MOVES), which a resumed landing reports, and the
    paths _own_commits' guard left out of the change ride the entry and its pending as KEPT. <resume>,
    an earlier call's pending, is landed again from its c1 and c2 -- lifted only where its move is verified (P6) -- and
    its own journal entry is never retried as a held one. LandStopped's pending is the run's own change's journal alone.
    Returns {status: landed, there, nothing, held, kept or locked (the here form, or a resumed journal, under an
    index.lock); sha: the landed commit, or the held one's c2; files;
    paths; lifted; onto: <default>, or <branch> in the here form; pushed: true only on the refspec push; refused; stuck:
    the paths held alone beside a landing; held_landed: [{sha, files, paths, branch}]; moves (sb._moves); pending;
    kept: the paths left out for the open run, a resumed journal's as its pending holds them}."""
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
           "pushed": False, "refused": None, "stuck": None, "held_landed": [], "moves": [], "pending": None,
           "kept": []}
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
                       **{k: resume[k] for k in ("old", "tip", "remote_only", "index_before", JOURNAL_MOVES, KEPT)
                          if k in resume})
        out["kept"] = list(resume.get(KEPT) or [])
    else:
        c1, c2, kept = _own_commits(root, snap, message)
        if c2 is None:
            return dict(out, status="nothing", kept=kept)
        own, in_record = _entry(root, c1, c2, default, branch, facts, here), False
        if kept:
            own[KEPT] = kept
        out["kept"] = kept
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


def retry_held(root, default, default_ref, register_rebuild=None, check=None, retry_remote=True, settled=()):
    """The held stage's primitive (P6, P7, P9, P28, P31). On a detached HEAD nothing at all (P9). Else orphaned held
    refs removed (_held_orphans: none younger than an hour). Each here journal finished where its move is verified
    (_finish_here) -- never dropped for HEAD's place. With HEAD on <default>, or in session-branch mode (sb.mode,
    read here, so the primitive drops them whether or not its caller tested the mode first), every other entry
    dropped with its ref, its files left to the flush, end's commit or §8.2's, an index.lock or none, a drop touching
    no index. Otherwise, where an index.lock stands, nothing more: every other entry kept as it is -- none rebuilt,
    landed or lifted, since the process holding the lock may be committing on the branch HEAD stands on, which a lift
    would race -- each permanent one reported stuck, a landing journal verified from the local refs alone (_verified,
    no fetch) reported nowhere, its lift waiting as a here journal's does, every other reported failed with a locked
    refusal naming the lock (the record keeps its own). <settled>: the c2 of each entry this start has already tried
    and reported failed or stuck (the held stage's held_attempted), kept and reported nowhere again -- one P8
    rebuilds under a new c2 following it there, the list as followed returned as settled where one was given; a
    failed one still holding back, with its own refusal, the later entries that share a path with it -- so a resumed
    stage spends no budget on it. Where none stands: P8 first (_apply_p8, which land's retries share); then, oldest
    first, each landing journal lifted where its move is verified (_verified), else landed again as a held entry;
    each permanent entry reported stuck; each transient one landed by _land_change (C2's test and the refspec push
    included; locally only where <retry_remote> is false; <check>(cost) before its capped calls, whose _Stop is
    raised after the landings so far are lifted), unless an earlier one that stays held shares a path with it -- then
    it is reported failed, and recorded, with that entry's refusal. Then _finish: each landing's lift override
    carried to the entries still held that started from it, the lift over every landing, their entries removed.
    Returns {landed: [{sha, files, paths, branch, lifted}], finished: [{sha, here, files, branch, lifted}], failed
    and stuck: [{refused, branch, kind, command, sha}], dropped: count}; lifted: [{path, blob}], the blob written
    back (None where removed), for P11's snapshot; a finished entry's sha is the commit it finished -- a here
    journal's on its branch, a verified landing journal's tip -- or None where it committed nothing (there), files
    that commit's count, and branch the entry's: HEAD's for a here journal, which pre.here.finished names. An error
    after its first ref write is LandStopped carrying that object as far as it got (_retry_report); a _Stop from
    <check> carries it too, as partial, once the landings before it are lifted."""
    _default_base(root, default, default_ref)
    return _write_bounded(_retry_held, root, default, default_ref, register_rebuild, check, retry_remote, settled)


def _retry_held(root, default, default_ref, register_rebuild, check, retry_remote, settled):
    out = {"landed": [], "finished": [], "failed": [], "stuck": [], "dropped": 0}
    info = []
    try:
        return _retry_body(root, default, default_ref, register_rebuild, check, retry_remote, out, info, settled)
    except _Stop:
        raise
    except Exception as e:  # what was done before the error goes with it: land --retry-held reports it
        e.partial = _retry_report(out, info, {})
        raise


def _retry_report(out, info, per):
    """retry_held's object: <out>, with each landing of <info> after the entries reported already -- landed ones with
    their sha, files, paths and branch, finished ones with the commit they finished (a verified journal's tip; None
    for one already there), its file count and their branch -- each with its lifted paths from <per>."""
    rep = dict(out, landed=list(out["landed"]), finished=list(out["finished"]))
    for i, (kind, e, got) in enumerate(info):
        if kind == "landed":
            rep["landed"].append({"sha": got["sha"], "files": got["files"], "paths": got["paths"], "branch": e["branch"],
                                  "lifted": per.get(i, [])})
        else:
            rep["finished"].append({"sha": got["sha"], "here": False, "files": got["files"], "branch": e["branch"],
                                    "lifted": per.get(i, [])})
    return rep


def _retry_body(root, default, default_ref, register_rebuild, check, retry_remote, out, info, settled=()):
    tried, settled = list(settled), set(settled)
    if tried:  # returned on every return where one was given, as P8 below may leave it
        out["settled"] = tried
    head = _head_branch(root)
    if head is None:  # P9: nothing is done on a detached HEAD, the orphan sweep included
        return out
    for orphan in _held_orphans(root):
        _wrote()
        sb.git(root, "update-ref", "-d", orphan)
    for e in [e for e in held_entries(root) if e.get("here")]:
        how, got = _finish_here(root, e, register_rebuild)
        if how == "finished" and got["status"] in ("landed", "there"):
            out["finished"].append({"sha": got.get("sha"), "here": True, "files": got.get("files", 0),
                                    "branch": e["branch"], "lifted": []})
        elif how != "locked":
            out["dropped"] += 1
    rest = [e for e in held_entries(root) if not e.get("here")]
    if head == default or sb.mode(root, default)["mode"] == "on":  # whatever the lock: a drop touches no index
        _held_remove(root, [e["c2"] for e in rest])
        out["dropped"] += len(rest)
        return out
    shown, lock = sb.git_paths(root, "index.lock")[0]
    if rest and os.path.lexists(lock):  # specs-repo-git §3.2: under the lock every entry is kept as it is
        locked = {"reason": "locked", "path": shown, "detail": None, "permanent": False}
        for e in rest:
            if e["c2"] in settled:
                continue
            if e["refused"] is not None and e["refused"].get("permanent"):
                out["stuck"].append(_held_info(e))
            elif e["refused"] is None and _verified(root, e, default, fetch=False):
                continue  # its commit is on <default>: only its lift waits, as a here journal's does
            else:
                out["failed"].append(dict(_held_info(e), refused=locked))
        return out
    moved = {}
    out["dropped"] += _apply_p8(root, moved=moved)
    if tried:  # a settled entry P8 rebuilt keeps its place under its new c2, which the caller keeps (held_attempted)
        tried = list(dict.fromkeys(c for c in (moved.get(c, c) for c in tried) if c))
        settled, out["settled"] = set(tried), tried
    chain, done, blocked = [], [], {}
    try:
        for e in held_entries(root):
            if e.get("here"):
                continue
            if e["c2"] in settled:  # tried by this start already: kept and reported once; one held again still holds
                if e["refused"] is not None and not e["refused"].get("permanent"):  # back, with its cause, the later
                    for p in e["paths"]:  # entries that share a path with it, as on the first pass; a stuck one, none
                        blocked.setdefault(p, e["refused"])
                continue
            if e["refused"] is None and _verified(root, e, default, check):
                chain.append(e)
                done.append(e["c2"])
                info.append(("finished", e, {"sha": e["tip"], "files": len(_commit_paths(root, e["tip"]))}))
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
    except _Stop as stop:  # the landings so far lifted, and reported with the stop, for the held stage's lines
        per = {}
        for i, x in _finish(root, chain, done):
            per.setdefault(i, []).append(x)
        stop.partial = _retry_report(out, info, per)
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
    checkout-moved) or null; for register-rebuild, none or failed; else null. kept names the paths §4 step 1 (1)'s guard
    left out of the change (specs-repo-git), [] for none."""
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
           "reason": None, "detail": None, "path": None, "permanent": None, "stuck": None, "kept": [], "error": None}
    try:
        got = land(a.specs, a.branch, default, a.default_ref, session_subject(a.commit_key, a.command), snap,
                   a.register_rebuild, a.here, {"kind": None, "merged": None, "command": a.command, "stayed": a.branch},
                   retry_remote=False)  # as end's: earlier held entries land locally only (§4 step 1)
    except LandStopped as e:
        return dict(out, error=str(e))
    refused, stuck = got["refused"] or {}, got["stuck"]
    return dict(out, status=got["status"], sha7=got["sha"][:7] if got["sha"] else None, files=got["files"],
                paths=got["paths"], lifted=got["lifted"], pushed=got["pushed"], kept=got["kept"],
                reason=refused.get("reason"),
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
    ap.add_argument("--selftest", action="store_true", help="run the selftest, which the repository keeps under scripts/selftests, and exit")
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
    p.add_argument("--started")
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
    p.add_argument("--started")
    p = sub.add_parser("start")
    p.add_argument("--command", required=True)
    p.add_argument("--key", action="append", default=[])
    p.add_argument("--commit-key")
    p.add_argument("--register-rebuild")
    p.add_argument("--rerun", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--budget", type=float, default=DEFAULT_BUDGET)
    p.add_argument("--started")
    p = sub.add_parser("replay")
    p.add_argument("--for", dest="for_", required=True, choices=("start", "end"))
    p.add_argument("--command", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--set-upstream", action="store_true")
    p.add_argument("--timed-out", action="store_true")
    p.add_argument("--started")
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
        return _run_selftest()
    if not a.cmd:
        print("specs-git: not run (a subcommand is required)", file=sys.stderr)
        return 2
    try:
        if a.cmd == "owner-repo":
            print(json.dumps(owner_repo_of(a.repo, not a.no_alias), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "declined":
            print(json.dumps(declined(a.command, a.path, a.started), indent=2, ensure_ascii=False))
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
                                   a.budget, a.started), indent=2, ensure_ascii=False))
            return 0
        if a.cmd == "end":  # the --specs exception, as specs-root-check's
            if a.specs is None:
                raise NotRun("usage: end needs --specs, empty where SPECS_PATH is unset")
            notice = None
            if a.misrooted_stdin:
                notice = [line for line in sys.stdin.buffer.read().decode("utf-8", "replace").splitlines() if line.strip()]
            print(json.dumps(end(a.specs, a.command, a.commit_key, a.register_rebuild, a.no_preflight, notice,
                                 a.session_branch_created, a.declined, a.resume, a.started), indent=2,
                             ensure_ascii=False))
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
        return replay(a.specs, a.for_, a.command, a.branch, a.set_upstream, a.timed_out, a.started)
    if a.cmd == "land":
        return land_cli(a)
    if a.cmd == "snapshot":
        return snapshot(a.specs)
    raise NotRun("unknown subcommand %s" % a.cmd)


def _run_selftest():
    """The selftest, which lives outside the plugin (SELFTEST_FILE): executed in this module's namespace, since
    its tests reach this script through globals() and __file__. Exit 2 where the file is not there to run."""
    path = os.path.normpath(SELFTEST_FILE)
    try:
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
    except OSError:
        print("specs-git: not run (the selftest is not shipped with the plugin; run it from the repository: "
              "%s is not there)" % path, file=sys.stderr)
        return 2
    scope = globals()
    exec(compile(source, path, "exec"), scope)
    return scope["selftest"]()


if __name__ == "__main__":
    sys.exit(main())

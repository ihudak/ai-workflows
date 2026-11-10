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
next call. The state and lines modules load only for the subcommands that need them, so a copy of this script
without them still runs the primitives above.

<root> is the specs repository's top level (branch-merged and branch-key also accept a directory below it,
where specs-repo-git §3.5 classifies under specs_git: misrooted); the <value> specs-root-check, start and end take is
never checked first, so empty, a file or a subdirectory each reaches it. Nothing here but start, end and replay writes
the working tree, the index or a ref. Output is one JSON object on stdout. Exit 0: it ran, whatever it found. Exit 2:
it could not run (usage, not a repository's top level, a ref that does not resolve, an unexpected git failure,
any other exception), printing one "specs-git: not run (...)" line on stderr; the caller reports it
and the run continues. start exits 2 only before it saves its record, its first write; after it, a failure is exit 0
with error set and the pre.stopped line, the record saved at the stage it reached. end exits 2 only before its first
write to the repository; after it, a failure is exit 0
with error set and the end.stopped line, and the record stays for end --resume. replay exits 2 only before it finds
its record; after it, a failure is exit 0 with error set and the stopped line, and the record stays as it stood; a
replay a signal ended prints nothing and ends by that signal, the record as it stood for the --timed-out call.
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


def catch_up(root, default, default_ref, on_write=None):
    """specs-repo-git §3.4's catch-up, which §4 step 2 runs again: where HEAD is on <default>, <default_ref> is
    origin/<default> and HEAD is strictly behind it, `pull --ff-only --no-rebase origin <default>`, capped at 60 s.
    None where it had nothing to do or succeeded; otherwise its pre.pull-failed line, git's first error line in its
    parenthesis, or the capped pull's words. <on_write> is called just before the pull, the call's first write."""
    if default is None or default_ref != "origin/" + default or _head_branch(root) != default:
        return None
    if sb.git(root, "merge-base", "--is-ancestor", "HEAD", default_ref, check=False).returncode != 0:
        return None
    if sb.rev(root, "HEAD") == sb.rev(root, default_ref):
        return None
    if on_write:
        on_write()
    return _pull_line(root, default)


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


def push_check(root, branch, default, session_branch=None, measure=None):
    """specs-repo-git §4 step 5's three conditions, in its order, before a push of <branch>: row None where all hold,
    else the §6 row of the first that fails -- not-ours (neither the default branch, nor a plugin branch, nor the
    session branch); no-remote; the four states that leave nowhere to push, elsewhere (remote: where the user's
    configuration pushes it), remote-deleted (ls-remote, 30 s, exits 2 for a branch read as pushed), refused-before
    (record and record_kind: the push-refusal file, else the configuration key; date) and origin-lacks (a plugin
    branch read as never pushed); then scope (push_scope's result, whose failed commit the row names). set_upstream:
    -u where the branch has no upstream, or one under another branch's name on a remote. <measure>, where given,
    measures push-scope in push_scope's place, last as step 5 orders it, and returns None where it could not run --
    start's, which reports that itself; the row is then unmeasured, which no §6 line renders, and nothing is
    pushed."""
    out = {"row": None, "remote": None, "record": None, "record_kind": None, "date": None, "scope": None,
           "set_upstream": False}
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
    if upstream == own or (not upstream and tracking):
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
    scope = (measure or push_scope)(root, branch)
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


def push(root, branch, set_upstream):
    """specs-repo-git §4 steps 5-6: `push --porcelain [-u] origin <branch>`, capped at 60 s, its outcome read from the
    --porcelain status line for refs/heads/<branch> alone, never from the exit status or the server's text: pushed for
    a flag in PUSHED_FLAGS; rejected for [rejected], which the replay settles; refused for [remote rejected] with a
    reason that is not TRANSIENT, which writes the push-refusal record (recorded: file, config or None; record; and
    record_error where neither could be written); failed otherwise -- a transient reason, another status, none, or
    the cap -- reason the status line's summary, git's first error line, or the capped push's words."""
    lines = _load_module("specs_git_lines")
    out = {"outcome": "failed", "reason": None, "recorded": None, "record": None, "record_error": None}
    p = sb.git_bounded(root, CAP, "push", "--porcelain", *(["-u"] if set_upstream else []), "origin", branch)
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
    step 6 could not record), record_error and date; reason; error (Commit failed); scope (push_check's), subject (its
    failed commit's) and hook (the paths a pre-commit hook added to this run's own commit, naming the hook variant)."""
    T = lines.T
    v = {"<sha7>": f.get("sha7"), "<N>": f.get("files"), "<branch>": f.get("branch"), "<default>": f.get("default"),
         "<SPECS_PATH>": f.get("specs"), "<YYYY-MM-DD>": _today()}
    t, tail = T["row." + row], ""
    if row == "remote-deleted" and f.get("branch") == f.get("default"):
        tail = lines.fill("row.remote-deleted.default-tail", v)
    elif row == "elsewhere":
        v["<remote>"] = f.get("remote")
    elif row == "failed":
        v["<reason>"] = f.get("reason")
    elif row == "commit-failed":
        v["<the first line of git's error or the hook's output>"] = f.get("error")
    elif row in ("refused-before", "push-refused"):
        v.update({"<record>": f.get("record"), "<date>": f.get("date"), "<the reason in parentheses>": f.get("reason")})
        if row == "push-refused" and f.get("record_kind") is None:
            t = _swap(t, "so this is recorded and no later run pushes it", T["app.unrecorded"])
            t = t[:t.index("; to land the commits")]
            v["<error>"] = f.get("record_error")
        elif f.get("record_kind") == "config":
            t = _swap(t, 'rm "<record>"', T["app.record-unset"]).replace("<record>", T["app.record-key"])
    elif row == "scope":
        failed = f["scope"]["failed"]
        if f.get("hook"):
            t = T["row.scope.hook"]
            v.update({"<path>": f["hook"][0], "<M-1>": str(len(f["hook"]) - 1) if len(f["hook"]) > 1 else None})
        else:
            if failed["reason"] == "merge":
                t = _swap(t, "which carries <path>", T["row.scope.merge"])
            elif failed["path"] is None:
                t = _swap(t, "which carries <path>", T["row.scope.no-file"])
            v.update({"<sha7>": [f.get("sha7"), failed["sha"][:7]], "<subject>": f.get("subject"), "<path>": failed["path"]})
    return lines.fill(t, v) + tail


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
    """An outcome of §4 step 1 -- misrooted, blocked or silent: what it prints, the record removed."""
    run["state"].remove(run["session"], run["command"])
    return _end_result(print=printed, line=line, row=row, record=run["record"])


def finish_end(run, row, line, view, commit=None, branch=None, pushed=False, hook=()):
    """specs-repo-git §4 step 7 from a row's <line>: the appends in §6's order -- the declined one last, naming the
    paths of <view>'s declined list that status() still lists, in phase-handoff §4.1's <artifacts> form -- then the §5
    block a guard's record repeats, then, where the push-scope row's hook variant names <hook>, the hook line for those
    of them the block or the declined paths name; the record removed. <run> holds state, lines, specs, session,
    command, record, and pre (lines printed before the outcome line)."""
    lines = run["lines"]
    if view["declined"]:
        listed = status(run["specs"])
        still = set(listed["artifact"]) | set(listed["other"])
        named = [p for p in view["declined"] if p in still]
        if named:
            line += lines.fill("app.declined", {"<path>": lines.artifacts(named)})
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


def _push_step(run, rec, commit, default, view):
    """specs-repo-git §4 steps 5-7 for <commit>, saved in <rec> as end_commit: push_check, then push. A rejected push
    keeps the record at stage end-replay and returns next naming the replay; every other outcome renders its row."""
    lines, specs, branch = run["lines"], run["specs"], commit["branch"]
    run["commit"] = commit
    check = push_check(specs, branch, default)
    facts = {"sha7": commit["sha7"], "files": commit["files"], "branch": branch, "default": default, "specs": specs}
    hook, pushed = (), False
    if check["row"] is None:
        p = push(specs, branch, check["set_upstream"])
        if p["outcome"] == "rejected":
            rec["stage"] = "end-replay"
            run["state"].save(run["session"], run["command"], rec)
            return _end_result(print=list(run.get("pre") or []), sha7=commit["sha7"], files=commit["files"], branch=branch,
                               next=_replay_next(specs, run["command"], branch, check["set_upstream"]),
                               record=run["record"])
        row = {"pushed": "pushed-default" if branch == default else "pushed-plugin", "refused": "push-refused",
               "failed": "failed"}[p["outcome"]]
        pushed = p["outcome"] == "pushed"
        facts.update(reason=p["reason"], record=p["record"], record_kind=p["recorded"], record_error=p["record_error"])
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
    return finish_end(run, row, _row_line(lines, row, facts), view, commit=commit, branch=branch, pushed=pushed,
                      hook=hook)


def end(specs, command, commit_key=None, register_rebuild=None, no_preflight=False, misrooted_notice=None,
        session_branch_created=None, declined=(), resume=False):
    """specs-repo-git §4's commit-artifacts for the run of this session and <command>, steps 1-7, on <specs>
    (SPECS_PATH as set, "" meaning unset). <misrooted_notice>: the lines of a notice that set misrooted outside the
    script (--misrooted-stdin), [] for none. <declined>: paths a declined call could not record. A failure before the
    run's first repository write -- the catch-up's pull, else `git add` -- raises, so the caller exits 2 with nothing
    done; after it, an exception (a signal sb.git_bounded turns into NotRun among them) returns error set and the
    end.stopped line, and the record stays for --resume: a later start replaces it, --no-preflight ignores it, and
    prune removes it after 7 days."""
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
        return _end_result(print=list(run["pre"]) + [line], line=line, sha7=commit.get("sha7"),
                           files=commit.get("files"), branch=commit.get("branch"), record=run["record"], error=error)


def _end(run, commit_key, register_rebuild, no_preflight, misrooted_notice, session_branch_created, declined, resume):
    state, lines, specs, session, command = (run[k] for k in ("state", "lines", "specs", "session", "command"))
    rec = state.load(session, command)
    if resume and rec is not None and rec.get("end_commit") and state.saved_within(rec):
        commit = rec["end_commit"] if rec["end_commit"].get("sha7") else _landed(specs, rec["end_commit"])
        if commit is not None:  # the run's commit is made: what follows is past its first write
            run["wrote"] = True
            run["record"] = "found"
            if commit is not rec["end_commit"]:
                rec["end_commit"] = commit
                state.save(session, command, rec)
            default = rec.get("default") or resolve_default(specs, False)["default"]
            return _push_step(run, rec, commit, default, _view(rec, declined))

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
    view = _view(keep, declined)

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
    if flag == "blocked":
        line = lines.fill("row.blocked", {})
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
    if branch is None:
        if status(specs)["artifact"]:
            line = lines.fill("row.blocked", {})
            return _stop(run, "blocked", [line, _g0_block(lines, specs, d["default"])], line)
        return finish_end(run, "nothing", lines.fill("row.nothing", {}), view)
    # §8.1's mode, which the record carries on to the replay; session-branch mode is not handled here yet, so every
    # mode commits as off does.
    mode = (rec.get("mode") if found and rec.get("mode") else
            sb.mode(specs, d["default"])["mode"] if d["default"] else "off")

    # Steps 2-4: the catch-up, then the commit. R2's boundary is the first repository write either makes, and just
    # before it the record is saved at stage end -- the one kept, else a new one in place of whatever stood -- with what
    # this call was given; and again just before `git commit`, with the commit about to be made (its branch, its base
    # and each path's staged blob), so --resume finds that commit where a kill comes between it and the save naming it.
    message = session_subject(commit_key or (keep or {}).get("commit_key"), command)
    saved = keep if keep is not None else state.new(command, session=session, started_by_script=False, specs=specs)
    saved.update(stage="end", end_commit=None, declined=view["declined"], mode=mode, default=d["default"],
                 default_ref=d["default_ref"], remote=d["remote"])
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

    pulled = catch_up(specs, d["default"], d["default_ref"], on_write=boundary)
    if pulled:
        run["pre"].append(pulled)
    c = commit_session_files(specs, message, on_write=boundary, on_staged=about_to_commit)
    if c["status"] != "committed":
        row = {"nothing": "nothing", "locked": "locked", "failed": "commit-failed"}[c["status"]]
        return finish_end(run, row, _row_line(lines, row, {"error": c["error"]}), view, branch=branch)
    commit = {"sha7": c["sha"][:7], "files": len(c["paths"]), "branch": branch, "paths": c["paths"],
              "hook_paths": c["hook_paths"]}
    run["commit"] = commit
    saved["end_commit"] = commit
    state.save(session, command, saved)
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
    reason, record, record_kind and record_error as _record_refusal wrote the record."""
    T, result, row = lines.T, result or {}, cls["row"]
    t = T["row." + row]
    sha7, files = _replay_sha7(cls, result, f.get("sha7")), f.get("files")
    if f.get("preflight"):  # the opening the Specs preflight: form drops: neither value is printed
        sha7, files = sha7 or "-", 0 if files is None else files
    v = {"<sha7>": sha7, "<N>": files, "<branch>": f["branch"], "<SPECS_PATH>": f["specs"]}
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
        elif cls["reason"] == "checked-out":  # run in that worktree, no switch
            t = _swap(t, remedy, T["remedy.checked-out"])
            v["<path>"] = refused["path"]
        elif f.get("standing") != f["branch"]:
            t = _swap(t, remedy, T["remedy.not-standing"])
            v["<the branch the run stands on>"] = f.get("standing")
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
    written first, as specs-repo-git §4 step 6's first bullet writes it."""
    commit = run.get("commit") or {}
    f = {"sha7": commit.get("sha7"), "files": commit.get("files"), "branch": branch, "specs": run["specs"],
         "default": rec.get("default"), "standing": standing, "register_rebuild": bool(rec.get("register_rebuild")),
         "error": error, "preflight": preflight}
    if cls["why"] == "refused":
        written = _record_refusal(run["specs"], branch)
        f.update(reason=_remote_refusal(_summary(result.get("porcelain"))), record=written["record"],
                 record_kind=written["recorded"], record_error=written["record_error"])
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
        return _end_result(print=[line], line=line, sha7=commit.get("sha7"), files=commit.get("files"),
                           branch=commit.get("branch"), record="found", error=error)


def _replay_end(run, rec, branch, set_upstream, timed_out):
    """replay --for end: the replay of the commit end made and saved as end_commit at stage end-replay. A pending
    end_commit (no sha7: end stopped between staging and its commit) is end --resume's, and is refused."""
    commit = rec.get("end_commit") or {}
    if rec.get("stage") != "end-replay" or not commit.get("sha7") or commit.get("branch") != branch:
        raise NotRun("the record holds no commit of %s that end handed to a replay; end --resume finishes this run"
                     % branch)
    run["commit"] = commit
    result, error, partial = _run_replay(run["specs"], branch, rec.get("register_rebuild"), set_upstream, timed_out)
    cls = classify_replay(result, error, partial, timed_out)
    f = _replay_facts(run, rec, cls, result, error, branch, branch, False)
    shown = dict(commit, sha7=_replay_sha7(cls, result, commit["sha7"]))
    return finish_end(run, cls["row"], _replay_line(run["lines"], cls, result, f), _view(rec), commit=shown,
                      branch=branch, pushed=cls["row"] == "replayed")


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


def _block_part(block, label, text):
    """<block> with the part <label> opens -- its line from the label on, and the indented lines that continue it --
    replaced by the label, the padding its line gives it, and <text>, unwrapped on one line."""
    rows = block.split("\n")
    i = next(k for k, row in enumerate(rows) if row.startswith(label))
    j = i + 1
    while j < len(rows) and rows[j].startswith(" "):
        j += 1
    pad = re.match(re.escape(label) + " *", rows[i]).group(0)
    return "\n".join(rows[:i] + [pad + text] + rows[j:])


def _g2_block(lines, specs, branch, default, variant=None, values=None):
    """specs-repo-git §5's G2 block for <branch>; with <variant> (implement: a direct /implement run from inside the
    specs repository), its Not done, Fix and If ignored parts are the g2.<variant>.* prose SRG gives in their place,
    each unwrapped on its one line."""
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
    """push_scope() of <branch>; where it cannot run, §4 step 5's report, pre.scope-failed, once for <branch> in a run,
    and None: nothing is pushed, B4 names no count, and the preflight goes on."""
    try:
        return push_scope(run["specs"], branch)
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


def _refused_line(lines, specs, branch, default, p):
    """specs-repo-git §4 step 6's refusal inside §3.4, for push()'s result <p>: pre.refused, with the remedy §6's push
    refused row gives from `to land the commits` on; or, where the refusal could be recorded neither way, its
    unrecorded form, which names no remedy."""
    T = lines.T
    v = {"<branch>": branch, "<the reason in parentheses>": p["reason"]}
    if p["recorded"] is None:
        t = T["pre.refused"]
        return lines.fill(t[:t.index(", and this is recorded")] + T["pre.refused.unrecorded"],
                          dict(v, **{"<error>": p["record_error"]}))
    row = _row_line(lines, "push-refused", {"sha7": "-", "files": 0, "branch": branch, "default": default, "specs": specs,
                                            "reason": p["reason"], "record": p["record"], "record_kind": p["recorded"],
                                            "record_error": p["record_error"]})
    v["<the remedy §6's push-refused line gives>"] = row[row.index("to land the commits"):]
    return lines.fill("pre.refused", v)


def _push(run, branch):
    """specs-repo-git §4 steps 5-6 for <branch> inside §3.4: push_check, its conditions in step 5's order and
    push-scope last, measured by _scope, which reports where it cannot run; then the push. A condition that fails,
    and a push that lands, print nothing here; a refusal and a failure print their Specs preflight: forms. The outcome
    (held where a condition failed or push-scope could not run) and set_upstream, which a rejected push's replay
    repeats."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    check = push_check(specs, branch, rec["default"], measure=lambda root, b: _scope(run, b))
    if check["row"] is not None:
        return {"outcome": "held", "set_upstream": False}
    p = push(specs, branch, check["set_upstream"])
    if p["outcome"] == "refused":
        _emit(run, _refused_line(lines, specs, branch, rec["default"], p))
    elif p["outcome"] == "failed":
        _emit(run, lines.preflight_form(_row_line(lines, "failed", {"sha7": "-", "files": 0, "branch": branch,
                                                                    "reason": p["reason"]})))
    return {"outcome": p["outcome"], "set_upstream": check["set_upstream"]}


def _pulls(rec):
    """Whether B2's and B4's move pulls: where <default-ref> is origin/<default> (specs-repo-git §3.5, as the catch-up
    in §3.4 names it); with no origin there is nothing to pull."""
    return bool(rec["default"]) and rec["default_ref"] == "origin/" + rec["default"]


def _to_default(run, branch, field):
    """B2's and B4's move (specs-repo-git §3.5), which §3.4's merged-branch leave also makes: switch to the
    default branch, <field> (b2_left or b4_left) saved as <branch>, then `pull --ff-only --no-rebase origin <default>`
    where _pulls holds, its pre.pull-failed line printed where it fails. git's result where it refused the switch,
    nothing moved; else None. The one place session-branch mode is to wrap this switch and pull in lift and
    put-back."""
    rec, specs = run["rec"], run["specs"]
    r = sb.git(specs, "switch", rec["default"], check=False)
    if r.returncode != 0:
        return r
    rec[field] = branch
    _save(run)
    if _pulls(rec):
        pulled = _pull_line(specs, rec["default"])
        if pulled:
            _emit(run, pulled)
    return None


def _leave(run, branch, test, merged_flush=False):
    """B2's action (specs-repo-git §3.5), which §3.4 also runs to leave a merged branch before its flush
    (<merged_flush>): _to_default, then `branch -d`. Where git refuses the switch, §3.4's leave prints
    pre.leave-failed and returns False, its flush going on from the branch. In §3.5 a refused switch stops the call
    (rule 5's pre.stopped), SRG wording no line for it. Where §3.5 reaches this, the session files are still dirty
    only where the flush's commit was Locked or failed, and git can then refuse to carry them -- an index.lock refuses
    every switch. §3.5 can also meet them dirty where status could not run, the dirty set unknown, and under
    misrooted, where §3.4 does not run; §3.5 switches nothing in either (_disposition), so neither reaches this."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default = rec["default"]
    r = _to_default(run, branch, "b2_left")
    if r is not None:
        if not merged_flush:
            raise NotRun("git switch %s: %s" % (default, _first_line(r, error=True)))
        _emit(run, lines.fill("pre.leave-failed", {"<branch>": branch, "<default>": default,
                                                   "<git's first error line>": _first_line(r, error=True)}))
        return False
    _delete(run, branch, test)
    _save(run)
    return True


def _b4(run, branch):
    """B4's action (specs-repo-git §3.5): _to_default, then the report of the branch left, with the count of commits
    on it a push would publish where there are any. A refused switch stops the call, as in _leave's §3.5 case."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    default = rec["default"]
    r = _to_default(run, branch, "b4_left")
    if r is not None:
        raise NotRun("git switch %s: %s" % (default, _first_line(r, error=True)))
    scope = _scope(run, branch)
    n = len(scope["commits"]) if scope else 0
    _emit(run, lines.fill("pre.b4", {"<branch>": branch, "<default>": default})
          + (lines.fill("pre.b4.count", {"<N>": n}) if n else ""))


def _fetch(run):
    """Stage fetch, specs-repo-git §3.2: the default branch's name and ref, and the fetch that freshens it; the mode
    (§8.1, never under misrooted); and, on a --rerun, §3.5's switch back to the branch the earlier start's B4 left,
    where a key of the new set names it -- left undone, pre.rerun-stay printed, where status could not run earlier in
    the run (pre.status-failed in reported, which --rerun carries), the dirty set unknown, as _disposition stays then.
    A gate that did not pass leaves nothing more to do."""
    rec, specs = run["rec"], run["specs"]
    if rec["gate"] != "pass":
        return _advance(run, "done")
    run["budget"].check(FETCH_COST)
    rec.update(resolve_default(specs, fetch=True))
    misrooted = rec["specs_git"] == "misrooted"
    if not misrooted and rec["default"]:
        rec["mode"] = sb.mode(specs, rec["default"])["mode"]
    left = rec["b4_left"]
    if left and not misrooted and branch_key(left, rec["keys"])["key"]:
        def current():
            return _head_branch(specs) or sb.text(sb.git(specs, "rev-parse", "--short", "HEAD"))

        if "pre.status-failed" in rec["reported"]:
            _emit(run, run["lines"].fill("pre.rerun-stay", {"<current>": current(), "<branch>": left}))
        else:
            r = sb.git(specs, "switch", left, check=False)
            if r.returncode == 0:
                rec["b4_left"] = None
            else:
                _emit(run, run["lines"].fill("pre.rerun-failed", {
                    "<branch>": left, "<git's first error line>": _first_line(r, error=True), "<current>": current()}))
    _advance(run, "disposition" if misrooted else "guards")


def _guards(run):
    """Stage guards, specs-repo-git §3.3: the first of G0, G1 and G2 that holds prints its §5 block, saved for end to
    repeat, and ends the preflight; G0 sets specs_git: blocked."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    head, found = _head_branch(specs), None
    if head is None:
        rec["specs_git"] = "blocked"
        found = ("G0", _g0_block(lines, specs, rec["default"]), [])
    else:
        listed = _status(run)
        other = listed["other"] if listed else []
        if other:
            found = ("G1", _g1_block(lines, specs, other), other)
        elif head != rec["default"] and not branch_key(head, [])["plugin_branch"]:
            variant = "implement" if run["command"] == "/implement" and _inside(rec["top"]) else None
            found = ("G2", _g2_block(lines, specs, head, rec["default"], variant), [])
    if found is None:
        return _advance(run, "flush")
    if not (rec["specs_git"] == "blocked" and found[0] != "G0"):  # a run --rerun carries blocked keeps G0's block,
        rec.update(guard=found[0], guard_block=found[1], guard_paths=found[2])  # which end repeats with its row
    _emit(run, found[1])
    _advance(run, "done")


def _flush(run):
    """Stage flush, specs-repo-git §3.4 outside session-branch mode: the catch-up; a merged plugin branch left by B2's
    action before a flush would commit on it; then the dirty session files committed on the current branch and
    pushed, or, with none dirty, the retry of its push. The stage's capped calls are one budget unit, checked before
    the first of them: the stage resumes from its start, and a resume that repeated a catch-up whose pull failed
    would never reach the push. A push origin rejects as non-fast-forward returns next naming its replay, the stage
    left at flush, which the replay advances; the settle loop then starts on start --resume."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    rec["settle_todo"] = None  # computed on entering the settle loop, after this branch's replay, if any
    checked = []

    def unit():
        if not checked:
            run["budget"].check(FLUSH_COST)
            checked.append(True)

    default = rec["default"]
    pulled = catch_up(specs, default, rec["default_ref"], on_write=unit)
    if pulled:
        _emit(run, pulled)
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
    carries), the dirty set unknown, they stay and print pre.stay.unlisted."""
    rec, specs, lines = run["rec"], run["specs"], run["lines"]
    head, default = _head_branch(specs), rec["default"]
    if head is not None and head != default and branch_key(head, [])["plugin_branch"]:
        merged = _merged(run, "HEAD", head)
        if merged["merged"] or not branch_key(head, rec["keys"])["key"]:
            stay = ("pre.stay" if rec["specs_git"] == "misrooted"
                    else "pre.stay.unlisted" if "pre.status-failed" in rec["reported"] else None)
            if stay:
                _emit(run, lines.fill(stay, {"<branch>": head, "<default>": default,
                                             lines.placeholder(stay, "<switched"): 0 if merged["merged"] else 1}))
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
    or the merged-branch leave reported (which §3.4's loop skips for the whole run), the branch B4 left and the
    declined paths."""
    if rec["specs_git"] is None and old.get("specs_git"):
        rec["specs_git"] = old["specs_git"]
        if old["specs_git"] == "misrooted":
            rec["misrooted_notice"] = old.get("misrooted_notice")
        else:
            rec.update(guard=old.get("guard"), guard_block=old.get("guard_block"),
                       guard_paths=list(old.get("guard_paths") or []))
    rec.update(advised_D=list(old.get("advised_D") or []), reported=list(old.get("reported") or []),
               b2_left=old.get("b2_left"), b4_left=old.get("b4_left"), declined=list(old.get("declined") or []))


def _queued_next(run, rec):
    """The call that replays the first branch <rec>'s pending queue holds (specs-repo-git §3.4, after the loop)."""
    queued = rec["pending"][0]
    return _replay_next(run["specs"], run["command"], queued["branch"], bool(queued.get("set_upstream")), "start")


def _start_result(run, nxt, replaced, error):
    """start's JSON: what this call printed and hands over next, then the run's facts as the record now holds them."""
    rec = run["rec"]
    offline = bool(rec.get("offline"))
    return {"print": run["print"], "next": nxt, "specs_git": rec.get("specs_git"), "gate": rec.get("gate"),
            "default": rec.get("default"), "default_ref": rec.get("default_ref"), "remote": rec.get("remote"),
            "offline": offline, "offline_clause": run["lines"].T["text.offline"] if offline else None,
            "session_branch": rec.get("session_branch"), "mode": rec.get("mode"), "guard": rec.get("guard"),
            "branch": rec.get("branch"), "b2_left": rec.get("b2_left"), "b4_left": rec.get("b4_left"),
            "replaced": replaced, "error": error}


def _close(run):
    """The record saved as the call returns, branch naming where HEAD then stands."""
    rec = run["rec"]
    rec["branch"] = _head_branch(run["specs"]) if rec.get("gate") == "pass" else None
    _save(run)


def start(specs, command, keys=(), commit_key=None, register_rebuild=None, rerun=False, resume=False,
          budget=DEFAULT_BUDGET):
    """specs-repo-git §3's specs-preflight for the run of this session and <command>, on <specs> (SPECS_PATH as set,
    "" meaning unset), with the run key set <keys>. A call that is not a resume prints the Environment: line and §3.1's
    notices (reads only), then saves a fresh record at stage fetch -- its first write -- and prunes; a failure before
    that save raises, so the caller exits 2 with nothing done, and after it every outcome is returned, an exception as
    error and the pre.stopped line. The stages (START_STAGES) then run from the record's own, each saved on entering
    it and resumable from its start. <resume> goes on with the saved stage only where state.resumable holds for this
    call's arguments; otherwise the call runs fresh. <rerun> opens on this command's record, keeping what _carry
    keeps, and saves this call's arguments, its key set among them. A stage that hands a replay over, and a unit of
    capped calls <budget> would not hold, return next: the replay, or start --resume with the record's args."""
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
                state.prune(keep_session=session)
            nxt = _start_stages(run)
        except _Stop:
            nxt = _resume_next(command, run["rec"]["args"], run["rec"]["budget"])
        _close(run)
    except Exception as e:
        said = " ".join(str(e).split())
        error = said if isinstance(e, NotRun) else type(e).__name__ + (": " + said if said else "")
        nxt = None
        _emit(run, lines.fill("pre.stopped", {"<the error>": error}))
        try:
            _close(run)
        except Exception:
            pass
    return _start_result(run, nxt, replaced, error)


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

        # l_ids
        ids = ["g0", "g1", "g2"]
        ids += ["g2.%s.%s" % (v, part) for v in ("session", "self", "implement") for part in ("not_done", "fix", "if_ignored")]
        ids += ["row.remote-deleted.default-tail", "row.scope.merge", "row.scope.no-file", "row.scope.hook",
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
        ids += ["end.stopped", "text.push-capped", "text.pull-capped", "text.offline", "root.one-line", "root.stray", "root.two-readings",
                "root.left-behind", "root.left-behind.nested", "root.left-behind.dir", "root.left-behind.close", "env.changed"]
        missing = [i for i in ids if i not in T]
        check(not missing, "l_ids: every id the interface names is a template (missing %r)" % missing)
        check(len(lines.ROWS) == 24 and lines.ROWS[0] == "pushed-plugin" and lines.ROWS[-1] == "silent"
              and all(("row." + r in T) == (r != "silent") for r in lines.ROWS),
              "l_ids: 24 rows, each a row.<id> template but silent (%r)" % (lines.ROWS,))
        check(all("\n" not in t for k, t in T.items() if k not in lines.BLOCKS),
              "l_ids: every template but the three blocks is one line")

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
        today = time.strftime("%Y-%m-%d", time.gmtime())
        local_today = time.strftime("%Y-%m-%d")
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

        def refused_tail(branch, specs, record_text, clear):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, %s"
                    % (branch, specs, today, branch, specs, today, branch, specs, branch, branch, clear))

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

        def refused_before(sha7, date, record_text, clear):
            return ("Specs repo: committed %s (1 file) on %s — not pushed: origin refused pushes to %s on %s (%s), and every "
                    "commit since stays on local %s; " % (sha7, PLUGIN, PLUGIN, date, record_text, PLUGIN)
                    + refused_tail(PLUGIN, r.path, record_text, clear))

        for body, date in (("2026-11-01\n", "2026-11-01"), ("", "an earlier run")):
            with open(rec_file, "w", encoding="utf-8") as fh:
                fh.write(body)
            seed(env, "/create-prd", branch=PLUGIN)
            r.write(RESUME, "r %s\n" % date)
            got = run_end(env, "/create-prd")
            check(got.get("row") == "refused-before"
                  and got.get("print") == [refused_before(head(r)[:7], date, rec_file, "rm \"%s\"" % rec_file)]
                  and on_origin(r, PLUGIN) == pushed_tip,
                  "e_refused_before: the record file holding %r names %s and its path (%r)" % (body, date, got))
        os.remove(rec_file)
        key = "branch.%s.workflowsPushRefused" % PLUGIN
        r.git("config", key, "2026-11-02")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r config\n")
        got = run_end(env, "/create-prd")
        check(got.get("row") == "refused-before" and got.get("print") == [refused_before(
            head(r)[:7], "2026-11-02", key, "git -C \"%s\" config --unset %s" % (r.path, key))] and "rm \"" not in got["line"],
              "e_refused_before: the configuration-key form names the key and its config --unset (%r)" % got)

        # e_push_refused
        r, env = plugin_world("e-push-refused")
        hook(os.path.join(r.bare, "hooks", "pre-receive"), "echo refused by policy >&2\nexit 1\n")
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", "prd", "ACME-1-x")
        opening = ("Specs repo: committed %s (1 file) on %s — push REFUSED by origin (pre-receive hook declined): a rule "
                   "there takes no push of %s, ")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r\n")
        got = run_end(env, "/create-prd")
        want = (opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                + refused_tail(PLUGIN, r.path, rec_file, "rm \"%s\"" % rec_file))
        check(got.get("row") == "push-refused" and got.get("print") == [want] and got.get("pushed") is False
              and os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() == local_today + "\n",
              "e_push_refused: refused, the record file written under the common git directory with today's date (%r)" % got)
        shutil.rmtree(os.path.join(r.path, ".git", "workflows"))
        with open(os.path.join(r.path, ".git", "workflows"), "w", encoding="utf-8") as fh:
            fh.write("a file where the record's directory would go\n")
        seed(env, "/create-prd", branch=PLUGIN)
        r.write(RESUME, "r2\n")
        got = run_end(env, "/create-prd")
        want = (opening % (head(r)[:7], PLUGIN, PLUGIN) + "so this is recorded and no later run pushes it; "
                + refused_tail(PLUGIN, r.path, key, "git -C \"%s\" config --unset %s" % (r.path, key)))
        check(got.get("row") == "push-refused" and got.get("print") == [want] and r.git("config", "--get", key) == local_today,
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
        g0 = lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": today, "<branch>": "main"})
        seed(env, "/specify", specs_git="blocked", guard="G0", guard_block=g0, branch=None)
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0] and head(r) == h
              and record(env, "/specify") is None, "e_blocked: a record carrying blocked repeats G0's block (%r)" % got)
        got = run_end(env, "/specify", "--no-preflight")
        check(got.get("record") == "missing" and got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0]
              and head(r) == h and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all"),
              "e_blocked: no record, a detached HEAD and something to stage prints G0's block the first time (%r)" % got)
        os.remove(os.path.join(r.path, RESUME))
        got = run_end(env, "/specify", "--no-preflight")
        check(got.get("row") == "nothing" and got.get("print") == [NOTHING], "e_blocked: nothing to stage is nothing (%r)" % got)

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
        got = run_end(env, "/specify")
        g0 = lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": today, "<branch>": "main"})
        check(got.get("record") == "found" and got.get("row") == "blocked" and got.get("print") == [BLOCKED, g0]
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
            got = push(r.path, "main", False)
            check(got == {"outcome": "refused", "reason": "push declined due to repository rule violations",
                          "recorded": "file", "record": rec_file, "record_error": None}
                  and open(rec_file, encoding="utf-8").read() == local_today + "\n",
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

    def scenarios_replay(tmp):
        state, lines = _flow()
        today = time.strftime("%Y-%m-%d", time.gmtime())
        local_today = time.strftime("%Y-%m-%d")
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

        def refused_tail(branch, specs, record_path):
            return ("to land the commits on local %s, put them on a branch of their own and open a pull request from it — "
                    "git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin session-files-%s — then, "
                    "standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes to %s again, rm \"%s\""
                    % (branch, specs, today, branch, specs, today, branch, specs, branch, branch, record_path))

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
        got = shell(nxt["run"], env)
        h = head(r)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = ("%s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s there, but push "
                "REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this is recorded and "
                "no later run pushes it; %s" % (committed(h[:7], PLUGIN), PLUGIN, PLUGIN, PLUGIN,
                                                 refused_tail(PLUGIN, r.path, rec_file)))
        check(got.get("row") == "moved" and got.get("print") == [want] and got.get("pushed") is False
              and on_origin(r, PLUGIN) != h and record(env, "/create-prd") is None,
              "r_refused_form: moved, not pushed, in its refused form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() == local_today + "\n",
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
        got = replay_cli(env, "start", "/specify", V)
        rec_file = os.path.join(r.path, ".git", "workflows", "push-refused", V)
        want = ("Specs preflight: %s — origin's %s had moved on, so the run replayed its 1 commit(s) onto it and moved %s "
                "there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of %s, so this "
                "is recorded and no later run pushes it; %s" % (V, V, V, V, refused_tail(V, r.path, rec_file)))
        check(got["_rc"] == 0 and got.get("print") == [want] and got.get("error") is None
              and (got.get("next") or {}).get("run") == resume_line(r.path, "/specify")
              and r.git("rev-parse", V + "~1") == head(o) and on_origin(r, V) == head(o)
              and r.git("symbolic-ref", "--short", "HEAD") == "main",
              "r_start_refused: moved, not pushed, its refused form in Specs preflight: form (%r)" % got)
        check(os.path.isfile(rec_file) and open(rec_file, encoding="utf-8").read() == local_today + "\n"
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
        got = render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), record="/r", record_kind="file",
                     record_error=None, **pf)
        check(got == ("%s — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) onto it and moved "
                      "prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule there takes no push "
                      "of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                      % (committed("bbbbbbb", "prd/A-1-x", 2), refused_tail("prd/A-1-x", "/s", "/r"))),
              "r_canned: the refused form, recorded (%r)" % got)
        got = render(dict(moved, porcelain=declined), record=None, record_kind=None, record_error="e",
                     reason="pre-receive hook declined")
        check(got == ("%s — origin's main had moved on, so the run replayed its 1 commit(s) onto it and moved main there, "
                      "but push REFUSED by origin (pre-receive hook declined): a rule there takes no push of main, but this "
                      "could not be recorded (e, the configuration write's), so a later run pushes main again"
                      % committed("bbbbbbb", "main", 2)), "r_canned: the refused form, unrecorded (%r)" % got)
        got = render(dict(moved, porcelain=declined.replace("main", "prd/A-1-x")), preflight=True, sha7=None, files=None,
                     record="/r", record_kind="file", record_error=None, **pf)
        check(got == ("Specs preflight: prd/A-1-x — origin's prd/A-1-x had moved on, so the run replayed its 1 commit(s) "
                      "onto it and moved prd/A-1-x there, but push REFUSED by origin (pre-receive hook declined): a rule "
                      "there takes no push of prd/A-1-x, so this is recorded and no later run pushes it; %s"
                      % refused_tail("prd/A-1-x", "/s", "/r")),
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
        today = time.strftime("%Y-%m-%d", time.gmtime())
        FEED = "specifications/PRD-ACME-1-x/dev-workflows/feedback/"
        SPEC = "spec/ACME-1-01-x"
        SUBJECT = "%s Add dev-workflows session artifacts (%s)"
        FIELDS = {"print", "next", "specs_git", "gate", "default", "default_ref", "remote", "offline", "offline_clause",
                  "session_branch", "mode", "guard", "branch", "b2_left", "b4_left", "replaced", "error"}
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
        got = run_start(env, "/feedback")
        block = lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": today, "<branch>": "main"})
        check(got.get("print") == [env_line(r.path), block] and got.get("specs_git") == "blocked" and got.get("guard") == "G0"
              and got.get("branch") is None and head(r) == h,
              "t_g0: a detached HEAD prints G0's block and sets blocked (%r)" % got)
        rec = record(env, "/feedback") or {}
        check(rec.get("guard_block") == block and rec.get("stage") == "done", "t_g0: the block saved for end (%r)" % rec)

        # t_g1
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
        check(got.get("print") == [env_line(r.path), block] and got.get("guard") == "G1" and got.get("specs_git") is None
              and got.get("branch") == "prd/ACME-9-q" and head(r) == h
              and "?? " + RESUME in r.git("status", "--porcelain", "--untracked-files=all")
              and "artifact area: my notes.md, notes.md\n" in shown and "add 'my notes.md' notes.md &&" in shown,
              "t_g1: the block lists the paths, comma-separated, then shell-quoted; no flush, no switch (%r)" % got)
        check((record(env, "/feedback") or {}).get("guard_paths") == ["my notes.md", "notes.md"],
              "t_g1: the paths saved as guard_paths")

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
            "Fix:      # nothing to do here: they reach the maintainer when that branch is pushed or merged\n"
            "If ignored: the artifacts stay on that branch until it is pushed or merged." % r.path)
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

        def then_gone(root, fetch):
            out = real_resolve(root, fetch)
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
        got = run_start(env, "/feedback", "--key", "ACME-1")
        p, rec_file = r.path, os.path.join(r.path, ".git", "workflows", "push-refused", PLUGIN)
        want = ("Specs preflight: %s not pushed — origin refused it (pre-receive hook declined), and this is recorded so no "
                "later run pushes it; to land the commits on local %s, put them on a branch of their own and open a pull "
                "request from it — git -C \"%s\" branch session-files-%s %s && git -C \"%s\" push -u origin "
                "session-files-%s — then, standing on %s, git -C \"%s\" reset --keep origin/%s; once origin takes pushes "
                "to %s again, rm \"%s\"" % (PLUGIN, PLUGIN, p, today, PLUGIN, p, today, PLUGIN, p, PLUGIN, PLUGIN, rec_file))
        check(got.get("print") == [env_line(p), want] and os.path.isfile(rec_file) and on_origin(r, PLUGIN) != head(r)
              and got.get("branch") == PLUGIN, "t_flush_refused: the refusal in its Specs preflight: form, recorded (%r)" % got)

        # t_flush_failed: origin unreachable once the fetch has run, so the flush's push fails
        r, env = world(tmp, "t-flush-failed")
        r.write(RESUME, "r\n")
        line = env_line(r.path)

        def then_gone_too(root, fetch):
            out = real_resolve(root, fetch)
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

        # t_rerun_blocked: a run --rerun carries blocked into prints the re-run's own block and keeps G0's for end
        r, env = world(tmp, "t-rerun-blocked")
        r.git("switch", "-q", "--detach", "HEAD")
        h = head(r)
        g0 = lines.fill("g0", {"<SPECS_PATH>": r.path, "<sha7>": h[:7], "<YYYY-MM-DD>": today, "<branch>": "main"})
        got = run_start(env, "/specify")
        check(got.get("print") == [env_line(r.path), g0] and got.get("specs_git") == "blocked",
              "t_rerun_blocked: G0 first (%r)" % got)
        r.git("switch", "-q", "-c", "feature/x")
        got = run_start(env, "/specify", "--rerun")
        g2 = lines.fill("g2", {"<SPECS_PATH>": r.path, "<branch>": "feature/x", "<default>": "main"})
        rec = record(env, "/specify") or {}
        check(got.get("print") == [env_line(r.path), g2] and got.get("specs_git") == "blocked" and got.get("guard") == "G0"
              and rec.get("guard_block") == g0 and rec.get("guard_paths") == [],
              "t_rerun_blocked: the re-run's G2 printed, G0's fields kept (%r, %r)" % (got, rec))
        r.write(RESUME, "r\n")
        got = run_end(env, "/specify")
        check(got.get("row") == "blocked" and got.get("print") == ["Specs repo: NOT COMMITTED — see the notice below", g0]
              and head(r) == h, "t_rerun_blocked: end prints G0's block with the blocked row (%r)" % got)

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
        check(got.get("print") == ["Specs repo: no session artifacts to commit", block_s] and record(env, "/specify") is None,
              "t_two_commands: /specify's end repeats the block its own start saved (%r)" % got)

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
            scenarios_replay(tmp)
            scenarios_start(tmp)

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

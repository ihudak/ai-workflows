#!/usr/bin/env python3
"""proposal-record.py — which version of each input an effort proposal priced.

  proposal-record.py record --specs <root> --folder <folder> [--brd-key <KEY> [--excluded <dir>[,<dir>...]]]
  proposal-record.py stamp --proposal <proposal.md> --record <file>
  proposal-record.py check --specs <root> --proposal <proposal.md> [--brd-key <KEY>]
  proposal-record.py --selftest

record: prints the priced-against record of the inputs on disk now -- a slice's input set, or with
--brd-key an umbrella's, over the slices whose brd-link.md names that key as its parent:; --excluded
names the slice folders, by directory name, the umbrella excluded.
stamp: makes the record block in <file> the last thing in <proposal.md>, replacing a record that
already ends it and preserving every other byte; prints {"written": true} or {"written": false}.
check: parses the record <proposal.md> ends with and compares it with the inputs on disk; prints
{"basis": "content", "current", "changed", "added", "removed"} (an umbrella's adding "included" and
"excluded"), or {"basis": "none", "reason": "no-record"} or {"basis": "none", "reason":
"unreadable", "detail"}.

The input sets and the record's grammar are the plugin's proposal-format reference, section 15. The
ids are `git hash-object` ids, so one content checked out with CRLF or with LF hashes alike inside a
repository. Python standard library only.

Exit 0: it ran -- a stale or recordless proposal is a result. Exit 2: it could not run; the cause is
on stderr.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

OPEN = "<!-- priced-against"
CLOSE = "-->"
PROFILE_REL = ".dev-workflows/proposal-profile.yml"
PROFILE_TOKEN = "$SPECS_PATH/" + PROFILE_REL
SLICE_FILES = ("prd.md", "decisions.md", "ard.md", "specification.md", "code-defect-log.md")
ROUND_RE = re.compile(r"round-\d+\.md")
SELF_REVIEW_RE = re.compile(r"self-review-\d{8}(?:-\d+)?\.md")
LINE_RE = re.compile(r"(?P<path>.+) (?P<id>[0-9a-f]{40}|[0-9a-f]{64})(?P<excluded> excluded)?")
BRD_LINK_RE = re.compile(r"[^/]+/brd-link\.md")
PARENT_RE = re.compile(r"parent:\s*(['\"]?)([^'\"\s]+)\1\s*")


class Unrunnable(Exception):
    """The script could not run; main() prints the message and exits 2."""


def _read(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError:
        raise Unrunnable("%s is not UTF-8 text" % path)
    except OSError as e:
        raise Unrunnable("cannot read %s: %s" % (path, e.strerror))


def _write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# ---- self-test ----

def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout


def _put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    _write_text(path, text)


def _blob(raw):
    return hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()


def _slice(tmp, git=True):
    """A specs root holding one slice with every kind of input and every kind of non-input."""
    specs = os.path.join(tmp, "specs")
    folder = os.path.join(specs, "specifications", "BRD-1", "PRD-1-01")
    for rel, body in (
        ("prd.md", "# PRD\n"), ("decisions.md", "# Decision register\n"), ("specification.md", "spec\n"),
        ("code-defect-log.md", "log\n"), ("grounding/code-grounding.md", "cg\n"),
        ("grounding/sub/design-grounding.md", "dg\n"), ("grounding/.DS_Store", "x"), ("grounding/.cache/x.md", "x\n"),
        ("interview/round-1.md", "r1\n"), ("interview/round-12.md", "r12\n"),
        ("interview/customer-questions.md", "q\n"), ("interview/notes.md", "n\n"),
        ("self-review-20261001.md", "sr\n"), ("self-review-20261001-2.md", "sr2\n"), ("self-review-notes.md", "no\n"),
        ("EPIC-1-01-orders/epic.md", "e\n"), ("EPIC-1-01-orders/specification.md", "es\n"),
        ("proposal.md", "# Proposal\n"), ("proposal-brief.md", "brief\n"),
        ("revisions/PRD-1-01_proposal_20261001.md", "old\n"),
        ("brd-link.md", "---\nkind: brd\nkey: PRD-1-01\nparent: BRD-1\n---\n"), ("coverage-ledger.md", "ledger\n"),
    ):
        _put(os.path.join(folder, rel), body)
    _put(os.path.join(specs, PROFILE_REL), "roles: []\n")
    os.symlink(os.path.join(folder, "prd.md"), os.path.join(folder, "grounding", "link.md"))
    if git:
        _git(specs, "init", "-q")
    return specs, folder


SLICE_EXPECTED = [
    PROFILE_TOKEN, "EPIC-1-01-orders/epic.md", "code-defect-log.md", "decisions.md",
    "grounding/code-grounding.md", "grounding/sub/design-grounding.md", "interview/customer-questions.md",
    "interview/round-1.md", "interview/round-12.md", "prd.md", "self-review-20261001-2.md",
    "self-review-20261001.md", "specification.md",
]


def _stamped(tmp, specs, folder, brd_key=None, excluded=()):
    prop = os.path.join(folder, "proposal.md")
    _put(prop, "# Proposal\n\nText.\n")
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, brd_key, list(excluded)))
    stamp(prop, rec)
    return prop, rec


def _brd(tmp):
    specs = os.path.join(tmp, "specs")
    brd = os.path.join(specs, "specifications", "BRD-1")

    def link(name, parent):
        _put(os.path.join(brd, name, "brd-link.md"),
             "---\nkind: brd\nkey: %s\nparent: %s\nclaims: []\n---\n" % (name, parent))

    link("PRD-1-01", "BRD-1")
    _put(os.path.join(brd, "PRD-1-01", "proposal.md"), "p1\n")
    link("PRD-1-02", '"BRD-1"')
    _put(os.path.join(brd, "PRD-1-02", "proposal.md"), "p2\n")
    link("PRD-1-03", "BRD-1")
    link("PRD-9-01", "BRD-9")
    _put(os.path.join(brd, "brd", "brd-inventory.md"), "inv\n")
    _put(os.path.join(brd, "coverage-ledger.md"), "ledger\n")
    _put(os.path.join(specs, PROFILE_REL), "roles: []\n")
    _git(specs, "init", "-q")
    return specs, brd


def case_slice_input_set(tmp):
    specs, folder = _slice(tmp)
    got = sorted(slice_inputs(specs, folder))
    assert got == SLICE_EXPECTED, got


def case_ids_are_git_hash_object_ids(tmp):
    specs, folder = _slice(tmp)
    ids = hash_ids(specs, slice_inputs(specs, folder))
    want = _git(folder, "hash-object", "--", "prd.md").strip()
    assert ids["prd.md"] == want, (ids["prd.md"], want)
    assert all(re.fullmatch(r"[0-9a-f]{40}", v) for v in ids.values()), ids


def case_record_is_sorted_and_parses(tmp):
    specs, folder = _slice(tmp)
    block = record(specs, folder, None, [])
    lines = block.splitlines()
    assert lines[0] == OPEN and lines[-1] == CLOSE, lines
    assert [line.rsplit(" ", 1)[0] for line in lines[1:-1]] == SLICE_EXPECTED, lines
    got = parse(block, umbrella=False)
    assert got["status"] == "ok" and sorted(got["entries"]) == SLICE_EXPECTED, got


def case_stamp_appends_once_and_preserves_the_body(tmp):
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    body = "# Proposal\n\nText without a final newline"
    _put(prop, body)
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, []))
    assert stamp(prop, rec) == {"written": True}
    once = _read(prop)
    assert once.startswith(body + "\n\n" + OPEN + "\n"), repr(once[:80])
    assert stamp(prop, rec) == {"written": False} and _read(prop) == once


def case_stamp_replaces_a_damaged_trailing_record(tmp):
    specs, folder = _slice(tmp)
    prop, rec = _stamped(tmp, specs, folder)
    good = _read(prop)
    lines = good.split("\n")
    i = next(k for k, line in enumerate(lines) if line.startswith("prd.md "))
    lines[i] = "prd.md " + "0" * 40
    _put(prop, "\n".join(lines))
    assert stamp(prop, rec) == {"written": True} and _read(prop) == good


def case_stamp_appends_when_text_follows_a_record(tmp):
    specs, folder = _slice(tmp)
    prop, rec = _stamped(tmp, specs, folder)
    tail = _read(prop) + "\nA paragraph someone added after the record.\n"
    _put(prop, tail)
    assert parse(tail, False)["status"] == "unreadable"
    assert stamp(prop, rec) == {"written": True}
    after = _read(prop)
    assert after.startswith(tail) and parse(after, False)["status"] == "ok", after[-200:]


def case_stamp_never_deletes_text_after_an_unclosed_open_line(tmp):
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    body = "# Proposal\n\n" + OPEN + "\n\nA section the author wrote after a stray line.\n"
    _put(prop, body)
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, []))
    assert stamp(prop, rec) == {"written": True}
    assert _read(prop).startswith(body) and check(specs, prop, None)["current"] is True


def case_stamp_keeps_a_crlf_file_crlf(tmp):
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    _put(prop, "# Proposal\r\n\r\nText.\r\n")
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, []))
    stamp(prop, rec)
    text = _read(prop)
    assert "\n" not in text.replace("\r\n", ""), "a bare LF in a CRLF file"
    assert check(specs, prop, None)["current"] is True
    assert stamp(prop, rec) == {"written": False}


def case_current_whether_untracked_staged_or_committed(tmp):
    specs, folder = _slice(tmp)
    prop, _ = _stamped(tmp, specs, folder)
    assert check(specs, prop, None)["current"] is True
    _git(specs, "add", "-A")
    assert check(specs, prop, None)["current"] is True
    _git(specs, "commit", "-q", "-m", "c")
    assert check(specs, prop, None)["current"] is True


def case_changed_added_removed(tmp):
    specs, folder = _slice(tmp)
    prop, _ = _stamped(tmp, specs, folder)
    _put(os.path.join(folder, "prd.md"), "# PRD, edited\n")
    _put(os.path.join(folder, "ard.md"), "# ARD\n")
    os.remove(os.path.join(folder, "grounding", "code-grounding.md"))
    got = check(specs, prop, None)
    assert got == {"basis": "content", "current": False, "changed": ["prd.md"], "added": ["ard.md"],
                   "removed": ["grounding/code-grounding.md"]}, got


def case_profile_absent_then_added_then_changed(tmp):
    specs, folder = _slice(tmp)
    profile = os.path.join(specs, PROFILE_REL)
    os.remove(profile)
    prop, _ = _stamped(tmp, specs, folder)
    assert PROFILE_TOKEN not in _read(prop)
    _put(profile, "roles: []\n")
    assert check(specs, prop, None)["added"] == [PROFILE_TOKEN]
    prop, _ = _stamped(tmp, specs, folder)
    _put(profile, "roles: [tl]\n")
    assert check(specs, prop, None)["changed"] == [PROFILE_TOKEN]


def case_non_inputs_never_move_the_verdict(tmp):
    specs, folder = _slice(tmp)
    prop, _ = _stamped(tmp, specs, folder)
    for rel in ("proposal-brief.md", "revisions/PRD-1-01_proposal_20261001.md", "revisions/new.md", "brd-link.md",
                "coverage-ledger.md", "interview/notes.md", "EPIC-1-01-orders/specification.md",
                "self-review-notes.md", "grounding/.DS_Store", "grounding/.cache/x.md"):
        _put(os.path.join(folder, rel), "moved\n")
    assert check(specs, prop, None)["current"] is True


def case_crlf_and_lf_checkouts_hash_alike(tmp):
    win, lin = os.path.join(tmp, "win"), os.path.join(tmp, "lin")
    for root, body, autocrlf in ((win, "a\r\nb\r\n", "true"), (lin, "a\nb\n", "false")):
        _put(os.path.join(root, "f", "prd.md"), body)
        _git(root, "init", "-q")
        _git(root, "config", "core.autocrlf", autocrlf)
    a = hash_ids(win, {"prd.md": os.path.join(win, "f", "prd.md")})["prd.md"]
    b = hash_ids(lin, {"prd.md": os.path.join(lin, "f", "prd.md")})["prd.md"]
    assert a == b == _blob(b"a\nb\n"), (a, b)


def case_outside_a_repository_ids_are_raw_content_ids(tmp):
    specs, folder = _slice(tmp, git=False)
    ids = hash_ids(specs, slice_inputs(specs, folder))
    assert ids["prd.md"] == _blob(b"# PRD\n"), ids["prd.md"]


def case_specs_below_the_repository_root(tmp):
    root = os.path.join(tmp, "root")
    os.makedirs(root)
    _git(root, "init", "-q")
    specs, folder = _slice(root, git=False)
    _put(os.path.join(root, ".gitattributes"), "*.md text eol=lf\n")
    _put(os.path.join(folder, "prd.md"), "a\r\nb\r\n")
    ids = hash_ids(specs, slice_inputs(specs, folder))
    assert ids["prd.md"] == _blob(b"a\nb\n"), ids["prd.md"]
    prop, _ = _stamped(tmp, specs, folder)
    assert check(specs, prop, None)["current"] is True


def case_a_moved_folder_keeps_its_record(tmp):
    specs, folder = _slice(tmp)
    prop, _ = _stamped(tmp, specs, folder)
    _git(specs, "add", "-A")
    _git(specs, "commit", "-q", "-m", "c")
    moved = os.path.join(os.path.dirname(folder), "PRD-1-01-renamed")
    _git(specs, "mv", os.path.relpath(folder, specs), os.path.relpath(moved, specs))
    assert check(specs, os.path.join(moved, "proposal.md"), None)["current"] is True


def case_no_record_and_an_inline_mention_are_no_record(tmp):
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    _put(prop, "# Proposal\n\nThe `<!-- priced-against` record is explained elsewhere.\n")
    assert check(specs, prop, None) == {"basis": "none", "reason": "no-record"}


def case_unreadable_records(tmp):
    specs, folder = _slice(tmp)
    prop, _ = _stamped(tmp, specs, folder)
    good = _read(prop)
    pid = re.search(r"^prd\.md ([0-9a-f]{40})$", good, re.M).group(1)
    bad = {
        "not last": good + "Trailing prose.\n",
        "unclosed": good.replace("\n-->\n", "\n"),
        "bad line": good.replace("prd.md " + pid, "prd.md"),
        "short id": good.replace(pid, pid[:39]),
        "duplicate": good.replace("prd.md " + pid, "prd.md %s\nprd.md %s" % (pid, pid)),
        "excluded in a slice record": good.replace("prd.md " + pid, "prd.md %s excluded" % pid),
    }
    for name, text in bad.items():
        _put(prop, text)
        got = check(specs, prop, None)
        assert got["basis"] == "none" and got["reason"] == "unreadable" and got["detail"], (name, got)


def case_editor_whitespace_is_tolerated(tmp):
    specs, folder = _slice(tmp)
    prop, rec = _stamped(tmp, specs, folder)
    _put(prop, _read(prop).replace("\n", "  \n").rstrip(" \n"))
    assert check(specs, prop, None)["current"] is True
    assert stamp(prop, rec) == {"written": True} and check(specs, prop, None)["current"] is True


def case_a_path_with_a_space_round_trips(tmp):
    specs, folder = _slice(tmp)
    _put(os.path.join(folder, "grounding", "a b.md"), "x\n")
    prop, _ = _stamped(tmp, specs, folder)
    assert "\ngrounding/a b.md " in _read(prop) and check(specs, prop, None)["current"] is True


def case_sha256_repository_ids_are_64_characters(tmp):
    specs, folder = _slice(tmp, git=False)
    try:
        _git(specs, "init", "-q", "--object-format=sha256")
    except subprocess.CalledProcessError:
        print("     (this git cannot create a SHA-256 repository; case skipped)")
        return
    prop, _ = _stamped(tmp, specs, folder)
    entries = parse(_read(prop), False)["entries"]
    assert all(len(entry[0]) == 64 for entry in entries.values()), entries
    assert check(specs, prop, None)["current"] is True


def case_umbrella_record(tmp):
    specs, brd = _brd(tmp)
    prop, _ = _stamped(tmp, specs, brd, brd_key="BRD-1", excluded=["PRD-1-02", "PRD-1-03"])
    entries = parse(_read(prop), True)["entries"]
    assert sorted(entries) == [PROFILE_TOKEN, "PRD-1-01/brd-link.md", "PRD-1-01/proposal.md",
                               "PRD-1-02/brd-link.md", "PRD-1-02/proposal.md", "PRD-1-03/brd-link.md",
                               "coverage-ledger.md"], sorted(entries)
    assert sorted(p for p, entry in entries.items() if entry[1]) == ["PRD-1-02/brd-link.md", "PRD-1-03/brd-link.md"]
    got = check(specs, prop, "BRD-1")
    assert got["current"] is True and got["included"] == ["PRD-1-01"], got
    assert got["excluded"] == ["PRD-1-02", "PRD-1-03"], got


def case_umbrella_reports_every_kind_of_move(tmp):
    specs, brd = _brd(tmp)
    prop, _ = _stamped(tmp, specs, brd, brd_key="BRD-1", excluded=["PRD-1-02", "PRD-1-03"])
    _put(os.path.join(brd, "PRD-1-01", "proposal.md"), "p1, re-priced\n")
    _put(os.path.join(brd, "PRD-1-03", "proposal.md"), "p3, priced since\n")
    _put(os.path.join(brd, "PRD-1-04", "brd-link.md"), "---\nkind: brd\nkey: PRD-1-04\nparent: BRD-1\n---\n")
    shutil.rmtree(os.path.join(brd, "PRD-1-02"))
    _put(os.path.join(specs, PROFILE_REL), "roles: [tl]\n")
    got = check(specs, prop, "BRD-1")
    assert got["current"] is False, got
    assert got["changed"] == [PROFILE_TOKEN, "PRD-1-01/proposal.md"], got
    assert got["added"] == ["PRD-1-03/proposal.md", "PRD-1-04/brd-link.md"], got
    assert got["removed"] == ["PRD-1-02/brd-link.md", "PRD-1-02/proposal.md"], got


def case_umbrella_excluded_only_on_brd_link_lines(tmp):
    specs, brd = _brd(tmp)
    prop, _ = _stamped(tmp, specs, brd, brd_key="BRD-1")
    text = re.sub(r"^(coverage-ledger\.md [0-9a-f]{40})$", r"\1 excluded", _read(prop), flags=re.M)
    _put(prop, text)
    assert check(specs, prop, "BRD-1")["reason"] == "unreadable"


def case_cli(tmp):
    specs, brd = _brd(tmp)
    me = [sys.executable, os.path.abspath(__file__)]

    def run(*args):
        return subprocess.run(me + list(args), capture_output=True, text=True)

    r = run("record", "--specs", specs, "--folder", os.path.join(brd, "nope"))
    assert r.returncode == 2 and r.stderr.startswith("proposal-record: "), r
    r = run("record", "--specs", specs, "--folder", brd, "--brd-key", "BRD-1", "--excluded", "PRD-9-01")
    assert r.returncode == 2 and "not a slice" in r.stderr, r
    r = run("record", "--specs", specs, "--folder", os.path.join(brd, "PRD-1-01"), "--excluded", "x")
    assert r.returncode == 2 and "--brd-key" in r.stderr, r
    r = run("record", "--specs", os.path.join(brd, "PRD-1-01"), "--folder", brd)
    assert r.returncode == 2 and "not under" in r.stderr, r
    bad = os.path.join(tmp, "bad.txt")
    _put(bad, "not a record\n")
    prop = os.path.join(brd, "proposal.md")
    _put(prop, "# P\n")
    r = run("stamp", "--proposal", prop, "--record", bad)
    assert r.returncode == 2 and _read(prop) == "# P\n", r
    r = run("record", "--specs", specs, "--folder", brd, "--brd-key", "BRD-1", "--excluded", "PRD-1-03, PRD-1-02")
    assert r.returncode == 0 and r.stdout.startswith(OPEN + "\n"), r
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, r.stdout)
    r = run("stamp", "--proposal", prop, "--record", rec)
    assert r.returncode == 0 and json.loads(r.stdout) == {"written": True}, r
    r = run("check", "--specs", specs, "--proposal", prop, "--brd-key", "BRD-1")
    got = json.loads(r.stdout)
    assert r.returncode == 0 and got["current"] is True and got["excluded"] == ["PRD-1-02", "PRD-1-03"], r


def selftest():
    os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
    os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
    cases = sorted((name, fn) for name, fn in globals().items() if name.startswith("case_"))
    failed = 0
    for name, fn in cases:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = os.path.realpath(tmp)
            os.environ["GIT_CEILING_DIRECTORIES"] = tmp
            try:
                fn(tmp)
                print("ok   " + name)
            except Exception as e:  # any exception is that case failing, and it is named
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    print("selftest: %d/%d passed" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


# ---- implementation ----

def _plain_file(path):
    return os.path.isfile(path) and not os.path.islink(path)


def _plain_dir(path):
    return os.path.isdir(path) and not os.path.islink(path)


def _under(specs, folder):
    if os.path.commonpath([specs, folder]) != specs:
        raise Unrunnable("%s is not under --specs %s" % (folder, specs))


def _add_profile(specs, out):
    path = os.path.join(specs, PROFILE_REL)
    if _plain_file(path):
        out[PROFILE_TOKEN] = path


def slice_inputs(specs, folder):
    """A slice's input set (section 15.1): {record path: absolute path}, present files only."""
    out = {}
    for name in SLICE_FILES:
        path = os.path.join(folder, name)
        if _plain_file(path):
            out[name] = path
    grounding = os.path.join(folder, "grounding")
    if _plain_dir(grounding):
        for dirpath, dirnames, filenames in os.walk(grounding):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and _plain_dir(os.path.join(dirpath, d))]
            for name in filenames:
                path = os.path.join(dirpath, name)
                if not name.startswith(".") and _plain_file(path):
                    out[os.path.relpath(path, folder).replace(os.sep, "/")] = path
    interview = os.path.join(folder, "interview")
    if _plain_dir(interview):
        for name in os.listdir(interview):
            path = os.path.join(interview, name)
            if (ROUND_RE.fullmatch(name) or name == "customer-questions.md") and _plain_file(path):
                out["interview/" + name] = path
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if SELF_REVIEW_RE.fullmatch(name) and _plain_file(path):
            out[name] = path
        elif name.startswith("EPIC-") and _plain_dir(path) and _plain_file(os.path.join(path, "epic.md")):
            out[name + "/epic.md"] = os.path.join(path, "epic.md")
    _add_profile(specs, out)
    return out


def brd_link_parent(path):
    """The parent: a brd-link.md's frontmatter names, or None."""
    if not _plain_file(path):
        return None
    lines = _read(path).lstrip("﻿").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            return None
        m = PARENT_RE.fullmatch(line)
        if m:
            return m.group(2)
    return None


def slices(folder, brd_key):
    """A BRD container's slice folders, by directory name: brd-proposal Phase 2's positive test."""
    return sorted(name for name in os.listdir(folder)
                  if _plain_dir(os.path.join(folder, name))
                  and brd_link_parent(os.path.join(folder, name, "brd-link.md")) == brd_key)


def umbrella_inputs(specs, folder, brd_key):
    """An umbrella's input set (section 15.1): {record path: absolute path}, present files only."""
    out = {}
    for name in slices(folder, brd_key):
        out[name + "/brd-link.md"] = os.path.join(folder, name, "brd-link.md")
        proposal = os.path.join(folder, name, "proposal.md")
        if _plain_file(proposal):
            out[name + "/proposal.md"] = proposal
    ledger = os.path.join(folder, "coverage-ledger.md")
    if _plain_file(ledger):
        out["coverage-ledger.md"] = ledger
    _add_profile(specs, out)
    return out


def hash_ids(specs, inputs):
    """{record path: git hash-object id} for {record path: absolute path}."""
    for path in inputs:
        if len(path.splitlines()) != 1 or CLOSE in path:
            raise Unrunnable("cannot record %r: a path holding a line break or '-->' cannot sit in the record" % path)
    if not inputs:
        return {}
    keys = sorted(inputs)
    # Paths as arguments, never --stdin-paths: git reads those relative to the repository's top level
    # rather than to -C, which breaks a specs root below it.
    paths = [os.path.relpath(inputs[key], specs) for key in keys]
    try:
        run = subprocess.run(["git", "-C", specs, "hash-object", "--", *paths],
                             capture_output=True, text=True, encoding="utf-8")
    except FileNotFoundError:
        raise Unrunnable("git is not installed -- the record's ids are git hash-object ids")
    ids = run.stdout.split()
    if run.returncode != 0 or len(ids) != len(keys):
        raise Unrunnable("git hash-object failed: " + (run.stderr.strip() or "no output"))
    return dict(zip(keys, ids))


def render(ids, excluded=()):
    lines = [OPEN]
    for path in sorted(ids):
        flag = " excluded" if BRD_LINK_RE.fullmatch(path) and path.split("/", 1)[0] in excluded else ""
        lines.append("%s %s%s" % (path, ids[path], flag))
    lines.append(CLOSE)
    return "\n".join(lines) + "\n"


def _lines(text):
    """[(offset, line without its line break)], splitting on LF and CRLF only."""
    out, pos = [], 0
    for raw in text.split("\n"):
        out.append((pos, raw[:-1] if raw.endswith("\r") else raw))
        pos += len(raw) + 1
    return out


def parse(text, umbrella):
    """The record a proposal's text ends with: {"status": "ok" | "no-record" | "unreadable", "entries"
    (path -> (id, excluded)), "detail", "start" (offset of its first line), "trailing" (whether stamp
    may replace it: it ends the file and nothing an author wrote follows it)}."""
    lines = _lines(text)
    opens = [i for i, (_, line) in enumerate(lines) if line.rstrip() == OPEN]
    if not opens:
        return {"status": "no-record"}
    first = opens[-1]
    start = lines[first][0]
    close = next((i for i in range(first + 1, len(lines)) if lines[i][1].strip() == CLOSE), None)
    if close is None:
        return {"status": "unreadable", "detail": "the record is not closed with '-->'", "start": start,
                "trailing": False}
    if any(line.strip() for _, line in lines[close + 1:]):
        return {"status": "unreadable", "detail": "the record is not the last thing in the file", "start": start,
                "trailing": False}
    entries = {}
    for _, line in lines[first + 1:close]:
        m = LINE_RE.fullmatch(line.rstrip())
        if not m:
            detail = "not a '<path> <id>' line: %r" % line
        elif m.group("path") in entries:
            detail = "a path recorded twice: %s" % m.group("path")
        elif m.group("excluded") and not (umbrella and BRD_LINK_RE.fullmatch(m.group("path"))):
            detail = "'excluded' on a line that is not an umbrella's <slice>/brd-link.md: %s" % m.group("path")
        else:
            entries[m.group("path")] = (m.group("id"), bool(m.group("excluded")))
            continue
        return {"status": "unreadable", "detail": detail, "start": start, "trailing": True}
    return {"status": "ok", "entries": entries, "start": start, "trailing": True}


def record(specs, folder, brd_key, excluded):
    specs, folder = os.path.realpath(specs), os.path.realpath(folder)
    _under(specs, folder)
    if excluded and not brd_key:
        raise Unrunnable("--excluded needs --brd-key: only an umbrella excludes slices")
    if brd_key:
        stray = sorted(set(excluded) - set(slices(folder, brd_key)))
        if stray:
            raise Unrunnable("--excluded names a folder that is not a slice of %s: %s" % (brd_key, ", ".join(stray)))
        inputs = umbrella_inputs(specs, folder, brd_key)
    else:
        inputs = slice_inputs(specs, folder)
    return render(hash_ids(specs, inputs), set(excluded))


def stamp(proposal, record_file):
    block = _read(record_file)
    own = parse(block, umbrella=True)
    if own["status"] != "ok" or own["start"] != 0:
        raise Unrunnable("%s does not hold one record block and nothing else" % record_file)
    text = _read(proposal)
    newline = "\r\n" if "\r\n" in text else "\n"
    block = block.replace("\r\n", "\n").rstrip("\n").replace("\n", newline) + newline
    found = parse(text, umbrella=True)
    if found["status"] != "no-record" and found["trailing"]:
        new = text[:found["start"]] + block
    else:
        body = text
        if body and not body.endswith("\n"):
            body += newline
        new = body + (newline if body else "") + block
    if new != text:
        _write_text(proposal, new)
    return {"written": new != text}


def check(specs, proposal, brd_key):
    specs, proposal = os.path.realpath(specs), os.path.realpath(proposal)
    found = parse(_read(proposal), umbrella=brd_key is not None)
    if found["status"] == "no-record":
        return {"basis": "none", "reason": "no-record"}
    if found["status"] == "unreadable":
        return {"basis": "none", "reason": "unreadable", "detail": found["detail"]}
    folder = os.path.dirname(proposal)
    _under(specs, folder)
    inputs = umbrella_inputs(specs, folder, brd_key) if brd_key else slice_inputs(specs, folder)
    now = hash_ids(specs, inputs)
    then = {path: entry[0] for path, entry in found["entries"].items()}
    changed = sorted(p for p in then if p in now and now[p] != then[p])
    added = sorted(p for p in now if p not in then)
    removed = sorted(p for p in then if p not in now)
    out = {"basis": "content", "current": not (changed or added or removed),
           "changed": changed, "added": added, "removed": removed}
    if brd_key:
        links = {p.split("/", 1)[0]: entry[1] for p, entry in found["entries"].items() if BRD_LINK_RE.fullmatch(p)}
        out["included"] = sorted(name for name, excluded in links.items() if not excluded)
        out["excluded"] = sorted(name for name, excluded in links.items() if excluded)
    return out


def _dir(path, flag):
    if not os.path.isdir(path):
        raise Unrunnable("%s %s is not a directory" % (flag, path))
    return path


def _file(path, flag):
    if not os.path.isfile(path):
        raise Unrunnable("%s %s is not a file" % (flag, path))
    return path


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(prog="proposal-record.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--specs", required=True)
    rec.add_argument("--folder", required=True)
    rec.add_argument("--brd-key")
    rec.add_argument("--excluded", default="")
    stm = sub.add_parser("stamp")
    stm.add_argument("--proposal", required=True)
    stm.add_argument("--record", required=True)
    chk = sub.add_parser("check")
    chk.add_argument("--specs", required=True)
    chk.add_argument("--proposal", required=True)
    chk.add_argument("--brd-key")
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            excluded = [name.strip() for name in args.excluded.split(",") if name.strip()]
            sys.stdout.write(record(_dir(args.specs, "--specs"), _dir(args.folder, "--folder"), args.brd_key, excluded))
        elif args.command == "stamp":
            print(json.dumps(stamp(_file(args.proposal, "--proposal"), _file(args.record, "--record"))))
        else:
            print(json.dumps(check(_dir(args.specs, "--specs"), _file(args.proposal, "--proposal"), args.brd_key),
                             ensure_ascii=False))
    except Unrunnable as e:
        print("proposal-record: %s" % e, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))

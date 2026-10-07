#!/usr/bin/env python3
"""proposal-record.py — which version of each input an effort proposal priced.

  proposal-record.py record --specs <root> --folder <folder> [--baseline <file>] [--brd-key <KEY> [--excluded <dir>[,<dir>...]]]
  proposal-record.py stamp --proposal <proposal.md> --record <file> [--excluded <dir>[,<dir>...]]
  proposal-record.py check --specs <root> --proposal <proposal.md> [--brd-key <KEY>]
  proposal-record.py --selftest

record: prints the priced-against record of the inputs on disk now -- a slice's input set, or with
--brd-key an umbrella's, over the slices whose brd-link.md names that key as its parent:; --excluded
names the slice folders, by directory name, the umbrella excluded; --baseline (a slice's only) adds
the prior estimate a proposal reconciles against -- by its $SPECS_PATH/ path under the specs root,
else as <baseline>, recorded but never compared (check lists it as "unverifiable").
stamp: makes the record block in <file> the last thing in <proposal.md>, replacing a record that
already ends it, removing any other record block (whole or damaged) so none hides the author's text,
and preserving every other byte; --excluded re-marks which slices of an umbrella's record are
excluded; prints {"written": true} or {"written": false}.
check: parses the record <proposal.md> ends with and compares it with the inputs on disk; prints
{"basis": "content", "current", "changed", "added", "removed"} -- an umbrella's adding "included",
"excluded", "stale_slices" (each included slice whose own record reads stale, with why) and
"unrecorded_slices" (included slices whose proposal carries no readable record), its "current" also
false while any included slice is stale -- or {"basis": "none", "reason": "no-record"} or {"basis": "none", "reason":
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
BASELINE_TOKEN = "<baseline>"
PARENT_RE = re.compile(r"\s*parent:\s*(['\"]?)([^'\"\s#]+)\1\s*(?:#.*)?")
LEGACY_PRD_RE = re.compile(r"[A-Z][A-Z0-9_]*(?:-\d+)+_[^/]*\.md")


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
        ("grounding/code-grounding.md~", "bak\n"), ("grounding/code-grounding.md.orig", "orig\n"),
        ("grounding/#code-grounding.md#", "autosave\n"), ("grounding/notes.txt", "txt\n"),
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
    os.symlink(os.path.join("..", "prd.md"), os.path.join(folder, "grounding", "link.md"))  # relative, as a repository holds one
    if git:
        _git(specs, "init", "-q")
    return specs, folder


SLICE_EXPECTED = [
    PROFILE_TOKEN, "EPIC-1-01-orders/epic.md", "code-defect-log.md", "decisions.md",
    "grounding/code-grounding.md", "grounding/link.md", "grounding/sub/design-grounding.md", "interview/customer-questions.md",
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
    assert "A paragraph someone added after the record." in after and after.count(OPEN) == 1, after
    assert parse(after, False)["status"] == "ok", after[-200:]


def case_stamp_never_deletes_text_after_an_unclosed_open_line(tmp):
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    body = "# Proposal\n\n" + OPEN + "\n\nA section the author wrote after a stray line.\n"
    _put(prop, body)
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, []))
    assert stamp(prop, rec) == {"written": True}
    after = _read(prop)
    assert after.startswith("# Proposal\n\n\nA section the author wrote after a stray line.\n"), repr(after[:120])
    assert after.count(OPEN) == 1 and check(specs, prop, None)["current"] is True


def case_stamp_unhides_author_text_a_damaged_record_swallowed(tmp):
    specs, folder = _slice(tmp)
    prop, rec = _stamped(tmp, specs, folder)
    good = _read(prop)
    damaged = good.replace("\n-->\n", "\n") + "\n## A section written after the record\n"
    _put(prop, damaged)
    assert stamp(prop, rec) == {"written": True}
    after = _read(prop)
    hidden = after[:after.index("## A section written after the record")]
    assert OPEN not in hidden, "the author's section still sits inside an unclosed comment"
    assert after.count(OPEN) == 1 and check(specs, prop, None)["current"] is True


def case_stamp_moves_a_record_left_mid_file_to_the_end(tmp):
    specs, folder = _slice(tmp)
    prop, rec = _stamped(tmp, specs, folder)
    _put(prop, _read(prop) + "\n## Appended later\n")
    assert stamp(prop, rec) == {"written": True}
    after = _read(prop)
    assert after.count(OPEN) == 1 and after.index("## Appended later") < after.index(OPEN), after
    assert check(specs, prop, None)["current"] is True and stamp(prop, rec) == {"written": False}


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
    assert got == {"basis": "content", "current": False, "changed": ["grounding/link.md", "prd.md"], "added": ["ard.md"],
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
                "self-review-notes.md", "grounding/.DS_Store", "grounding/.cache/x.md", "grounding/code-grounding.md~",
                "grounding/code-grounding.md.orig", "grounding/#code-grounding.md#", "grounding/notes.txt"):
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


def case_stamp_sets_the_excluded_marks(tmp):
    specs, brd = _brd(tmp)
    prop, rec = _stamped(tmp, specs, brd, brd_key="BRD-1", excluded=["PRD-1-03"])
    assert stamp(prop, rec, excluded=["PRD-1-02", "PRD-1-03"]) == {"written": True}
    got = check(specs, prop, "BRD-1")
    assert got["excluded"] == ["PRD-1-02", "PRD-1-03"] and got["included"] == ["PRD-1-01"], got
    assert stamp(prop, rec, excluded=["PRD-1-02", "PRD-1-03"]) == {"written": False}
    try:
        stamp(prop, rec, excluded=["PRD-9-01"])
    except Unrunnable as e:
        assert "PRD-9-01" in str(e)
    else:
        raise AssertionError("an --excluded naming no slice of the record was accepted")


def case_failures_exit_2_never_a_traceback(tmp):
    import contextlib
    import io
    specs, folder = _slice(tmp)
    prop = os.path.join(folder, "proposal.md")
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, []))
    real = globals()["_write_text"]

    def refuse(path, text):
        raise PermissionError(13, "Permission denied", path)

    globals()["_write_text"] = refuse
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = main(["stamp", "--proposal", prop, "--record", rec])
    finally:
        globals()["_write_text"] = real
    assert code == 2 and "proposal-record:" in err.getvalue(), (code, err.getvalue())
    fd = os.open(os.path.join(folder, "grounding").encode() + b"/\xff.md", os.O_WRONLY | os.O_CREAT, 0o644)
    os.close(fd)
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        code = main(["record", "--specs", specs, "--folder", folder])
    assert code == 2 and "proposal-record:" in err.getvalue(), (code, err.getvalue())


def case_a_parent_with_a_comment_or_an_indent_is_still_the_parent(tmp):
    specs, brd = _brd(tmp)
    _put(os.path.join(brd, "PRD-1-04", "brd-link.md"), "---\nkind: brd\nparent: BRD-1   # carved 2026-10\n---\n")
    _put(os.path.join(brd, "PRD-1-05", "brd-link.md"), "---\n  kind: brd\n  parent: 'BRD-1'\n---\n")
    assert slices(brd, "BRD-1") == ["PRD-1-01", "PRD-1-02", "PRD-1-03", "PRD-1-04", "PRD-1-05"], slices(brd, "BRD-1")


def case_a_legacy_named_prd_is_an_input(tmp):
    specs, folder = _slice(tmp)
    os.remove(os.path.join(folder, "prd.md"))
    _put(os.path.join(folder, "PRD-1-01_orders.md"), "# PRD\n")
    _put(os.path.join(folder, "revisions", "PRD-1-01_orders_20260901.md"), "old\n")
    got = slice_inputs(specs, folder)
    assert "PRD-1-01_orders.md" in got and not any(k.startswith("revisions/") for k in got), sorted(got)
    _put(os.path.join(folder, "prd.md"), "# PRD\n")
    assert "PRD-1-01_orders.md" not in slice_inputs(specs, folder)


def case_umbrella_records_its_own_defect_sources(tmp):
    specs, brd = _brd(tmp)
    for rel in ("code-defect-log.md", "grounding/code-grounding.md", "self-review-20261001.md"):
        _put(os.path.join(brd, rel), "x\n")
    prop, _ = _stamped(tmp, specs, brd, brd_key="BRD-1")
    entries = parse(_read(prop), True)["entries"]
    for rel in ("code-defect-log.md", "grounding/code-grounding.md", "self-review-20261001.md"):
        assert rel in entries, sorted(entries)
    _put(os.path.join(brd, "grounding", "code-grounding.md"), "y\n")
    assert check(specs, prop, "BRD-1")["changed"] == ["grounding/code-grounding.md"]


def case_umbrella_reports_stale_and_unrecorded_included_slices(tmp):
    specs, brd = _brd(tmp)
    s1 = os.path.join(brd, "PRD-1-01")
    _put(os.path.join(s1, "prd.md"), "# PRD\n")
    _stamped(tmp, specs, s1)
    prop, _ = _stamped(tmp, specs, brd, brd_key="BRD-1", excluded=["PRD-1-03"])
    got = check(specs, prop, "BRD-1")
    assert got["current"] is True and got["stale_slices"] == {} and got["unrecorded_slices"] == ["PRD-1-02"], got
    _put(os.path.join(s1, "prd.md"), "# PRD, edited\n")
    got = check(specs, prop, "BRD-1")
    assert got["current"] is False and got["changed"] == [] and got["stale_slices"] == {"PRD-1-01": ["prd.md changed"]}, got


def case_an_excluded_unpriced_slice_is_watched_through_its_own_inputs(tmp):
    specs, brd = _brd(tmp)
    s3 = os.path.join(brd, "PRD-1-03")
    _put(os.path.join(s3, "prd.md"), "# PRD\n")
    prop, rec = _stamped(tmp, specs, brd, brd_key="BRD-1", excluded=["PRD-1-02", "PRD-1-03"])
    entries = parse(_read(prop), True)["entries"]
    assert "PRD-1-03/prd.md" in entries and not any(k.startswith("PRD-1-02/") and k.endswith("prd.md") for k in entries), sorted(entries)
    assert check(specs, prop, "BRD-1")["current"] is True
    _put(os.path.join(s3, "grounding", "code-grounding.md"), "verified\n")
    got = check(specs, prop, "BRD-1")
    assert got["current"] is False and got["added"] == ["PRD-1-03/grounding/code-grounding.md"], got
    try:
        stamp(prop, rec, excluded=["PRD-1-02"])
    except Unrunnable as e:
        assert "PRD-1-03" in str(e)
    else:
        raise AssertionError("stamp re-marked a slice whose inputs the record holds instead of a proposal")


def case_a_symlink_counts_as_what_it_points_at(tmp):
    specs, folder = _slice(tmp)
    shared = os.path.join(tmp, "shared")
    _put(os.path.join(shared, "extra-grounding.md"), "shared finding\n")
    os.symlink(shared, os.path.join(folder, "grounding", "shared"))
    os.symlink(os.path.join(folder, "grounding"), os.path.join(folder, "grounding", "sub", "loop"))
    os.symlink(os.path.join(tmp, "nowhere.md"), os.path.join(folder, "grounding", "dangling.md"))
    got = slice_inputs(specs, folder)
    assert "grounding/shared/extra-grounding.md" in got and "grounding/dangling.md" not in got, sorted(got)
    assert not any("/loop/" in k for k in got), sorted(got)
    prop, _ = _stamped(tmp, specs, folder)
    _put(os.path.join(shared, "extra-grounding.md"), "shared finding, revised\n")
    _put(os.path.join(folder, "prd.md"), "# PRD, edited through the link's target\n")
    got = check(specs, prop, None)
    assert got["changed"] == ["grounding/link.md", "grounding/shared/extra-grounding.md", "prd.md"], got


def case_a_baseline_inside_the_specs_root_is_watched(tmp):
    specs, folder = _slice(tmp)
    baseline = os.path.join(specs, "estimates", "prior.md")
    _put(baseline, "prior: 400h\n")
    prop = os.path.join(folder, "proposal.md")
    _put(prop, "# Proposal\n")
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, [], baseline=baseline))
    stamp(prop, rec)
    assert "\n$SPECS_PATH/estimates/prior.md " in _read(prop)
    assert check(specs, prop, None)["current"] is True
    _put(baseline, "prior: 450h\n")
    assert check(specs, prop, None)["changed"] == ["$SPECS_PATH/estimates/prior.md"]
    os.remove(baseline)
    assert check(specs, prop, None)["removed"] == ["$SPECS_PATH/estimates/prior.md"]


def case_a_baseline_outside_the_specs_root_is_recorded_but_not_checked(tmp):
    specs, folder = _slice(tmp)
    baseline = os.path.join(tmp, "elsewhere", "prior-estimate.md")
    _put(baseline, "prior: 400h\n")
    prop = os.path.join(folder, "proposal.md")
    _put(prop, "# Proposal\n")
    rec = os.path.join(tmp, "rec.txt")
    _put(rec, record(specs, folder, None, [], baseline=baseline))
    stamp(prop, rec)
    text = _read(prop)
    assert "\n<baseline> " in text and "elsewhere" not in text, text
    got = check(specs, prop, None)
    assert got["current"] is True and got["unverifiable"] == ["<baseline>"], got
    try:
        record(specs, os.path.dirname(folder), "BRD-1", [], baseline=baseline)
    except Unrunnable:
        pass
    else:
        raise AssertionError("an umbrella record accepted --baseline")


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
    """A file the pricing can read: a regular file, or a symlink to one (a dangling link is none)."""
    return os.path.isfile(path)


def _plain_dir(path):
    return os.path.isdir(path)


def _under(specs, folder):
    if os.path.commonpath([specs, folder]) != specs:
        raise Unrunnable("%s is not under --specs %s" % (folder, specs))


def _add_profile(specs, out):
    path = os.path.join(specs, PROFILE_REL)
    if _plain_file(path):
        out[PROFILE_TOKEN] = path


def _grounding_and_self_reviews(folder, out):
    """Every file under grounding/ (no symlink, no dot-name) and every self-review-<date>.md."""
    grounding = os.path.join(folder, "grounding")
    if _plain_dir(grounding):
        seen = set()
        for dirpath, dirnames, filenames in os.walk(grounding, followlinks=True):
            real = os.path.realpath(dirpath)
            if real in seen:  # a linked directory reached twice, or a link back up the tree
                dirnames[:] = []
                continue
            seen.add(real)
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                path = os.path.join(dirpath, name)
                # grounding records are markdown: an editor's backup or autosave, or any other file, is not one
                if not name.startswith(".") and name.endswith(".md") and _plain_file(path):
                    out[os.path.relpath(path, folder).replace(os.sep, "/")] = path
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if SELF_REVIEW_RE.fullmatch(name) and _plain_file(path):
            out[name] = path


def slice_inputs(specs, folder):
    """A slice's input set (section 15.1): {record path: absolute path}, present files only."""
    out = {}
    for name in SLICE_FILES:
        path = os.path.join(folder, name)
        if _plain_file(path):
            out[name] = path
    if "prd.md" not in out:
        # addressing's legacy fallback: a <KEY>_<slug>.md PRD, which /prd-proposal prices when no prd.md exists
        for name in os.listdir(folder):
            path = os.path.join(folder, name)
            if LEGACY_PRD_RE.fullmatch(name) and _plain_file(path):
                out[name] = path
    _grounding_and_self_reviews(folder, out)
    interview = os.path.join(folder, "interview")
    if _plain_dir(interview):
        for name in os.listdir(interview):
            path = os.path.join(interview, name)
            if (ROUND_RE.fullmatch(name) or name == "customer-questions.md") and _plain_file(path):
                out["interview/" + name] = path
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if name.startswith("EPIC-") and _plain_dir(path) and _plain_file(os.path.join(path, "epic.md")):
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


def umbrella_inputs(specs, folder, brd_key, unpriced=()):
    """An umbrella's input set (section 15.1): {record path: absolute path}, present files only.
    unpriced names the slices it excluded holding no proposal.md: each one's own input set is
    watched instead, under its folder, so a slice that becomes estimable is seen."""
    out = {}
    for name in slices(folder, brd_key):
        if name in unpriced:
            for key, path in slice_inputs(specs, os.path.join(folder, name)).items():
                if key != PROFILE_TOKEN:
                    out[name + "/" + key] = path
        out[name + "/brd-link.md"] = os.path.join(folder, name, "brd-link.md")
        proposal = os.path.join(folder, name, "proposal.md")
        if _plain_file(proposal):
            out[name + "/proposal.md"] = proposal
    for name in ("coverage-ledger.md", "code-defect-log.md"):
        path = os.path.join(folder, name)
        if _plain_file(path):
            out[name] = path
    # the container's own defect sources, which brd-proposal Phase 6 step 3 sweeps
    _grounding_and_self_reviews(folder, out)
    _add_profile(specs, out)
    return out


def hash_ids(specs, inputs):
    """{record path: git hash-object id} for {record path: absolute path}."""
    for path in inputs:
        if len(path.splitlines()) != 1 or CLOSE in path:
            raise Unrunnable("cannot record %r: a path holding a line break or '-->' cannot sit in the record" % path)
        try:
            path.encode("utf-8")
        except UnicodeEncodeError:
            raise Unrunnable("cannot record %r: a file name that is not UTF-8 cannot sit in the record" % path)
    if not inputs:
        return {}
    keys = sorted(inputs)
    # Paths as arguments, never --stdin-paths: git reads those relative to the repository's top level
    # rather than to -C, which breaks a specs root below it.
    paths = [os.path.relpath(inputs[key], specs) for key in keys]
    paths = [inputs[key] if rel.startswith("..") else rel for key, rel in zip(keys, paths)]
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


def _baseline_input(specs, baseline):
    """The --baseline file as a record input: under the specs root by its $SPECS_PATH/ path, which any
    machine can check; outside it by the token alone -- a local path has no place in a document a
    customer receives, and no other machine could open it."""
    if not _plain_file(baseline):
        raise Unrunnable("--baseline %s is not a readable file" % baseline)
    real = os.path.realpath(baseline)
    if os.path.commonpath([specs, real]) == specs:
        return "$SPECS_PATH/" + os.path.relpath(real, specs).replace(os.sep, "/"), real
    return BASELINE_TOKEN, real


def record(specs, folder, brd_key, excluded, baseline=None):
    specs, folder = os.path.realpath(specs), os.path.realpath(folder)
    _under(specs, folder)
    if baseline and brd_key:
        raise Unrunnable("--baseline is a slice proposal's: an umbrella reconciles against no prior estimate")
    if excluded and not brd_key:
        raise Unrunnable("--excluded needs --brd-key: only an umbrella excludes slices")
    if brd_key:
        stray = sorted(set(excluded) - set(slices(folder, brd_key)))
        if stray:
            raise Unrunnable("--excluded names a folder that is not a slice of %s: %s" % (brd_key, ", ".join(stray)))
        unpriced = [name for name in excluded if not _plain_file(os.path.join(folder, name, "proposal.md"))]
        inputs = umbrella_inputs(specs, folder, brd_key, unpriced)
    else:
        inputs = slice_inputs(specs, folder)
    if baseline:
        key, path = _baseline_input(specs, baseline)
        inputs[key] = path
    return render(hash_ids(specs, inputs), set(excluded))


def _remark(block, excluded):
    """The block with exactly the named slices' brd-link.md lines marked excluded."""
    lines, slices_held, priced, moved = [], set(), set(), set()
    for line in block.split("\n"):
        m = LINE_RE.fullmatch(line.rstrip())
        if m and m.group("path").endswith("/proposal.md") and m.group("path").count("/") == 1:
            priced.add(m.group("path").split("/", 1)[0])
        if m and BRD_LINK_RE.fullmatch(m.group("path")):
            name = m.group("path").split("/", 1)[0]
            lines.append("%s %s%s" % (m.group("path"), m.group("id"), " excluded" if name in excluded else ""))
            slices_held.add(name)
            if bool(m.group("excluded")) != (name in excluded):
                moved.add(name)
        else:
            lines.append(line)
    stray = sorted(set(excluded) - slices_held)
    if stray:
        raise Unrunnable("--excluded names a folder that is not a slice this record holds: %s" % ", ".join(stray))
    unpriced = sorted(moved - priced)
    if unpriced:
        raise Unrunnable("--excluded would re-mark a slice the record watches through its own inputs, not a "
                         "proposal: %s -- an unpriced slice's exclusion is fixed when the record is taken" % ", ".join(unpriced))
    return "\n".join(lines)


def _without_record_blocks(text):
    """The text less every record block in it: an OPEN line, the record lines after it, and the CLOSE
    line where one directly follows them -- a damaged block's stray OPEN line included, since an
    unclosed comment hides everything after it from a reader."""
    lines = _lines(text)
    kept, pos, i = [], 0, 0
    while i < len(lines):
        if lines[i][1].rstrip() != OPEN:
            i += 1
            continue
        j = i + 1
        while j < len(lines) and LINE_RE.fullmatch(lines[j][1].rstrip()):
            j += 1
        if j < len(lines) and lines[j][1].strip() == CLOSE:
            j += 1
        kept.append(text[pos:lines[i][0]])
        pos = lines[j][0] if j < len(lines) else len(text)
        i = j
    kept.append(text[pos:])
    return "".join(kept)


def stamp(proposal, record_file, excluded=None):
    block = _read(record_file)
    own = parse(block, umbrella=True)
    if own["status"] != "ok" or own["start"] != 0:
        raise Unrunnable("%s does not hold one record block and nothing else" % record_file)
    block = block.replace("\r\n", "\n").rstrip("\n")
    if excluded is not None:
        block = _remark(block, set(excluded))
    text = _read(proposal)
    newline = "\r\n" if "\r\n" in text else "\n"
    block = block.replace("\n", newline) + newline
    found = parse(text, umbrella=True)
    if found["status"] != "no-record" and found["trailing"]:
        new = _without_record_blocks(text[:found["start"]]) + block
    else:
        body = _without_record_blocks(text)
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
    if brd_key:
        flagged = [p.split("/", 1)[0] for p, entry in found["entries"].items() if BRD_LINK_RE.fullmatch(p) and entry[1]]
        unpriced = [name for name in flagged if name + "/proposal.md" not in found["entries"]]
        inputs = umbrella_inputs(specs, folder, brd_key, unpriced)
    else:
        inputs = slice_inputs(specs, folder)
    unverifiable = []
    for path in found["entries"]:
        if path == BASELINE_TOKEN:
            unverifiable.append(path)
        elif path.startswith("$SPECS_PATH/") and path != PROFILE_TOKEN:  # a --baseline under the specs root
            target = os.path.join(specs, path[len("$SPECS_PATH/"):])
            if _plain_file(target):
                inputs[path] = target
    now = hash_ids(specs, inputs)
    then = {path: entry[0] for path, entry in found["entries"].items() if path not in unverifiable}
    changed = sorted(p for p in then if p in now and now[p] != then[p])
    added = sorted(p for p in now if p not in then)
    removed = sorted(p for p in then if p not in now)
    out = {"basis": "content", "current": not (changed or added or removed),
           "changed": changed, "added": added, "removed": removed}
    if unverifiable:
        out["unverifiable"] = unverifiable
    if brd_key:
        links = {p.split("/", 1)[0]: entry[1] for p, entry in found["entries"].items() if BRD_LINK_RE.fullmatch(p)}
        out["included"] = sorted(name for name, excluded in links.items() if not excluded)
        out["excluded"] = sorted(name for name, excluded in links.items() if excluded)
        stale, unrecorded = {}, []
        for name in out["included"]:
            path = os.path.join(folder, name, "proposal.md")
            if not _plain_file(path):
                continue  # its proposal.md is listed as removed already
            own = check(specs, path, None)
            if own["basis"] == "none":
                unrecorded.append(name)
            elif not own["current"]:
                stale[name] = (["%s changed" % p for p in own["changed"]] + ["%s added" % p for p in own["added"]]
                               + ["%s removed" % p for p in own["removed"]])
        out["stale_slices"] = stale
        out["unrecorded_slices"] = unrecorded
        out["current"] = out["current"] and not stale
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
    rec.add_argument("--baseline")
    stm = sub.add_parser("stamp")
    stm.add_argument("--proposal", required=True)
    stm.add_argument("--record", required=True)
    stm.add_argument("--excluded")
    chk = sub.add_parser("check")
    chk.add_argument("--specs", required=True)
    chk.add_argument("--proposal", required=True)
    chk.add_argument("--brd-key")
    args = parser.parse_args(argv)
    try:
        if args.command == "record":
            excluded = [name.strip() for name in args.excluded.split(",") if name.strip()]
            sys.stdout.write(record(_dir(args.specs, "--specs"), _dir(args.folder, "--folder"), args.brd_key, excluded,
                                    args.baseline))
        elif args.command == "stamp":
            excluded = None if args.excluded is None else [n.strip() for n in args.excluded.split(",") if n.strip()]
            print(json.dumps(stamp(_file(args.proposal, "--proposal"), _file(args.record, "--record"), excluded)))
        else:
            print(json.dumps(check(_dir(args.specs, "--specs"), _file(args.proposal, "--proposal"), args.brd_key),
                             ensure_ascii=False))
    except Unrunnable as e:
        print("proposal-record: %s" % e, file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as e:
        print("proposal-record: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))

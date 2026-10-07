# Proposal Currency by Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every `proposal.md` records which version of each input it priced, and `/brd-proposal` (per slice, and for the umbrella itself, up front) and `/prd-proposal`'s next-step offer decide currency by comparing that record with the inputs on disk.

**Architecture:** One bundled, self-tested, stdlib-only script — `plugins/product-workflows/scripts/proposal-record.py` with `record`, `stamp` and `check` — owns enumeration, hashing (`git hash-object`), the record's grammar and the comparison; the commands call it and never compute an id. `references/proposal-format.md` §15 is the authority the commands cite; the commands, the reviewer, the docs and the rules file are edited to run and describe it. Proposals without a record keep the 3.26.1 time rule.

**Tech Stack:** Python 3 standard library, git ≥ 2.32 (`GIT_CONFIG_GLOBAL` in the self-test), markdown command bodies, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-07-proposal-priced-against-design.md` (ai-workflows, branch `iv-gu/proposal-priced-against`).

## Global Constraints

- Plugin: `product-workflows` in ai-workflows only; the repo is public and vendor-neutral — every example is invented (`PRD-1234-01`, `BRD-1234`), no employer, product or person name.
- Plain `git` only; no tracker CLI, no network.
- Script: Python standard library only; exit 0 whenever it ran, 2 when it could not (cause on stderr); `--selftest` runs in CI.
- Record grammar (spec §2): first line `<!-- priced-against`, last line `-->`, one `<path> <id>` line per input present, sorted by path in byte order, id 40 or 64 lowercase hex; ` excluded` only on an umbrella's `<slice>/brd-link.md` lines; the block is the last thing in the file (only whitespace after).
- Paths folder-relative; the profile written `$SPECS_PATH/.dev-workflows/proposal-profile.yml`.
- A slice's ids are taken at the end of `/prd-proposal` Phase 2; an umbrella's at the end of `/brd-proposal` Phase 5. The authoring phase stamps them and runs `check`; a mid-run move keeps the earlier ids and is reported.
- New stop ids: `PRD_PROPOSAL_RECORD_FAILED`, `BRD_PROPOSAL_RECORD_FAILED`.
- The umbrella stop question is exactly `choices: ["Stop — the umbrella is current (Recommended)", "Re-price it anyway"]`; `--redo` and `--profile` skip it.
- Never `rm -rf`/`rm -r` in the shell; script every edit (Python, exactly-once asserts); check `git diff --summary | grep mode` before each commit.
- Version: the next free product-workflows minor above 3.26.1 at merge (3.27.0 unless taken); the CHANGELOG heading is `— Unreleased` on the branch and dated at merge.
- Commit trailer: `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d`.

## Review Focus

1. **An editor touches the record** (trailing spaces added, final newline dropped) — the record must still parse and `stamp` must restore it byte-exact. Pinned by Task 1's `case_editor_whitespace_is_tolerated`.
2. **`$SPECS_PATH` below the repository root** (a specs folder inside a monorepo) — ids must still be git's, `.gitattributes` at the repository root applying. Pinned by Task 1's `case_specs_below_the_repository_root`.
3. **One profile edit makes every proposal in the specs repository stale** — the profile is shared by every slice and umbrella; the walk's picture must name `proposal-profile.yml` as the cause so an operator sees one reason, not N mysteries. Pinned in Task 4 by the picture naming each path `check` lists (the profile included) — reviewer to confirm the wording.
4. **A proposal written but never stamped** (a run interrupted between Phase 7's write and its `stamp`) — reads `no-record`, falls back to times, and the picture says re-pricing once enables the content check. Pinned by Task 1's `case_no_record_and_an_inline_mention_are_no_record` (script) and Task 4's picture wording (prose).
5. **An umbrella whose included slice carries no record** — the umbrella's verdict must use that slice's time verdict, `undecidable` counting as not current. Pinned in Task 4's umbrella-check paragraph — reviewer to confirm.

---

## File structure

| File | Responsibility | Task |
|---|---|---|
| `plugins/product-workflows/scripts/proposal-record.py` (create, mode 755) | enumerate, hash, render, parse, stamp, compare; `--selftest` | 1 |
| `.github/workflows/validate-catalog.yml` | run the self-test in CI | 1 |
| `plugins/product-workflows/references/proposal-format.md` | §15 authority; census clause (§0, §1); §2 and §4 notes; header line | 2 |
| `plugins/product-workflows/commands/prd-proposal.md` | record at Phase 2, stamp + check at Phase 7, pre-lint and post-triage re-stamp, sibling currency at Phase 11, census, stop id, report | 3 |
| `plugins/product-workflows/agents/proposal-reviewer.md` | the record is machine data, never a finding | 3 |
| `plugins/product-workflows/commands/brd-proposal.md` | per-slice content basis and the umbrella check at Phase 2, Phase 3 rows, record at Phase 5, stamp + check at Phase 8, pre-lint and re-stamp, census, stop id, report, description | 4 |
| `plugins/product-workflows/docs/commands/{prd,brd}-proposal.md`, `docs/reference/proposal-format.md`, `docs/roles-and-phases.md`, `.claude/rules/product-workflows.md`, `references/decision-register-format.md` | human docs, rules, census | 5 |
| `plugins/product-workflows/CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` | release | 6 |

All paths below are relative to the clone's root; `$SCRATCH` is the session's scratch directory, outside the clone.

---

### Task 1: `proposal-record.py` and its CI self-test

**Files:**
- Create: `plugins/product-workflows/scripts/proposal-record.py` (mode 755)
- Modify: `.github/workflows/validate-catalog.yml` (after the "Self-test the promotion signals" step)
- Test: the script's own `--selftest` (25 cases)

**Interfaces:**
- Produces (CLI, consumed by Tasks 3–4):
  - `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py" record --specs <SPECS_PATH> --folder <folder> [--brd-key <KEY> [--excluded <dir>,<dir>]]` → the record block on stdout.
  - `… stamp --proposal <proposal.md> --record <file>` → `{"written": true}` / `{"written": false}`.
  - `… check --specs <SPECS_PATH> --proposal <proposal.md> [--brd-key <KEY>]` → `{"basis": "content", "current": bool, "changed": [...], "added": [...], "removed": [...]}` plus `"included"`, `"excluded"` (lists of slice directory names) with `--brd-key`; or `{"basis": "none", "reason": "no-record"}` / `{"basis": "none", "reason": "unreadable", "detail": str}`.
  - Exit 0 ran; 2 could not run, `proposal-record: <cause>` on stderr.

- [ ] **Step 1: Write the self-test and stubs (RED)**

Write `plugins/product-workflows/scripts/proposal-record.py` as **Block A** (below) followed by this stub block, then `chmod 755` it:

```python
# ---- implementation (stubs: Task 1 Step 3 replaces this block with Block B) ----

def slice_inputs(specs, folder):
    raise NotImplementedError


def brd_link_parent(path):
    raise NotImplementedError


def slices(folder, brd_key):
    raise NotImplementedError


def umbrella_inputs(specs, folder, brd_key):
    raise NotImplementedError


def hash_ids(specs, inputs):
    raise NotImplementedError


def render(ids, excluded=()):
    raise NotImplementedError


def parse(text, umbrella):
    raise NotImplementedError


def record(specs, folder, brd_key, excluded):
    raise NotImplementedError


def stamp(proposal, record_file):
    raise NotImplementedError


def check(specs, proposal, brd_key):
    raise NotImplementedError


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    raise NotImplementedError


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

**Block A** — header, constants, shared helpers, the self-test and its cases:

```python
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
```

- [ ] **Step 2: Run the self-test to verify it fails**

Run: `python3 plugins/product-workflows/scripts/proposal-record.py --selftest; echo "exit $?"`
Expected: 25 `FAIL … NotImplementedError` lines, `selftest: 0/25 passed`, `exit 1`.

- [ ] **Step 3: Replace the stub block with Block B (the implementation)**

```python
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
    paths = "".join(os.path.relpath(inputs[key], specs) + "\n" for key in keys)
    try:
        run = subprocess.run(["git", "-C", specs, "hash-object", "--stdin-paths"], input=paths,
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
```

- [ ] **Step 4: Run the self-test to verify it passes**

Run: `python3 plugins/product-workflows/scripts/proposal-record.py --selftest; echo "exit $?"`
Expected: 25 `ok` lines, `selftest: 25/25 passed`, `exit 0`.

- [ ] **Step 5: Add the CI step**

Python edit of `.github/workflows/validate-catalog.yml`, exactly-once:

```python
p = ".github/workflows/validate-catalog.yml"
s = open(p).read()
old = "        run: python3 plugins/product-workflows/scripts/promotion-signals.py --selftest\n"
assert s.count(old) == 1
s = s.replace(old, old + """
      - name: Self-test the proposal record
        # /product-workflows:prd-proposal and /brd-proposal record, stamp and compare with it which
        # version of each input a proposal priced. Its failure modes are silent: a missed input reads a
        # stale proposal as current, and a stamp that moves a byte rewrites a customer's document.
        # Fixtures are built at run time.
        run: python3 plugins/product-workflows/scripts/proposal-record.py --selftest
""")
open(p, "w").write(s)
```

Run: `python3 -c "import yaml" 2>/dev/null && python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/validate-catalog.yml'))" ; grep -n 'proposal-record.py --selftest' .github/workflows/validate-catalog.yml`
Expected: no YAML error (or no PyYAML installed — then the grep alone), one grep hit.

- [ ] **Step 6: Commit**

```bash
git add plugins/product-workflows/scripts/proposal-record.py .github/workflows/validate-catalog.yml
git diff --cached --summary | grep mode   # expect: create mode 100755 …proposal-record.py, nothing else
git commit -m "feat(product-workflows): proposal-record.py records, stamps and compares which version of each input a proposal priced; self-tested in CI

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

---

### Task 2: `references/proposal-format.md` — §15 and the census clause

**Files:**
- Modify: `plugins/product-workflows/references/proposal-format.md` (header line 8, §0 end line 27, §1 line 48, §2 line 76, §4 after line 121, new §15 at the end)

**Interfaces:**
- Consumes: Task 1's CLI exactly as its Interfaces block states.
- Produces: the anchors the commands cite — `proposal-format.md` §15, §15.1 (input sets), §15.2 (record), §15.3 (script), §15.4 (when taken), §15.5 (what current means).

- [ ] **Step 1: Write the failing check**

Save as `$SCRATCH/t2.py`:

```python
import re
s = open("plugins/product-workflows/references/proposal-format.md").read()
need = ["## 15. The `priced-against` record", "### 15.1 The input sets", "### 15.2 The record",
        "### 15.3 The script, and who runs what", "### 15.4 When the ids are taken", "### 15.5 What current means",
        "**One read is of the record alone**", "the one prose-only scan and the one record-only read",
        "**An archived revision keeps the `priced-against` record", "**After the last section that renders comes the `priced-against` record",
        "in §15 the record of which version of each input a proposal priced"]
missing = [n for n in need if n not in s]
assert not missing, missing
print("t2 ok")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 $SCRATCH/t2.py`
Expected: `AssertionError` listing all eleven strings.

- [ ] **Step 3: Apply the edits**

```python
p = "plugins/product-workflows/references/proposal-format.md"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

rep("rules a reviewer checks, and — in §14 — what an umbrella run adds over a slice's own proposal. Design authority:",
    "rules a reviewer checks, in §14 what an umbrella run adds over a slice's own proposal, and in §15 the record of which version of each input a proposal priced. Design authority:")
rep("classifies each change it records as a correction or a re-estimate (§12).\n\n## 1. What this format governs",
    "classifies each change it records as a correction or a re-estimate (§12). **One read is of the record\n"
    "alone**: `commands/prd-proposal.md`'s next-step offer reads a sibling slice's `priced-against` record\n"
    "(§15) — and nothing else of that sibling's proposal — to decide whether to offer pricing it, and\n"
    "stops nothing.\n\n## 1. What this format governs")
rep("(with the one prose-only scan it names beside it)",
    "(with the one prose-only scan and the one record-only read it names beside it)")
rep("`.md`. The new canonical records `revision_of:` naming the archived snapshot as actually written,\nsuffix included.\n",
    "`.md`. The new canonical records `revision_of:` naming the archived snapshot as actually written,\nsuffix included.\n\n"
    "**An archived revision keeps the `priced-against` record it ended with** (§15): archiving is a move,\n"
    "never a re-render, so each revision still says which inputs it priced.\n")
rep("| 23 | Changelog | **conditional** — renders only on a revision; §12 |\n",
    "| 23 | Changelog | **conditional** — renders only on a revision; §12 |\n\n"
    "**After the last section that renders comes the `priced-against` record (§15)** — on a slice's\n"
    "proposal and an umbrella's alike. It is machine data in an HTML comment, not a section: it is counted\n"
    "against neither this set nor §10's, carries no prose, and is never reviewed for content.\n")
assert s.endswith("the umbrella over it.\n")
s += SECTION_15          # the literal below
open(p, "w").write(s)
```

`SECTION_15` is this text, verbatim (it begins with a blank line):

````markdown

## 15. The `priced-against` record — which version of each input a proposal priced

**Whether a proposal is current is decided by content, not by time.** Every `proposal.md` either
command writes ends with one HTML comment recording the git blob id of every input the run priced,
and a later reader compares those ids with the inputs on disk. A time — a commit's or a file's —
records no version: an input edited locally is newer only than its own last commit, a squash merge
can carry a proposal and the change it never priced in one commit, and a shallow clone gives every
file one time. **A proposal written before this record existed carries none**, and
`commands/brd-proposal.md` Phase 2 decides it by the times it always did, over `prd.md`,
`decisions.md` and `grounding/` alone.

### 15.1 The input sets

**A slice's** — every input `commands/prd-proposal.md` reads to price the folder, paths relative to it:

| Input | Why the pricing reads it |
|---|---|
| `prd.md` | the requirement set the packages cluster |
| `decisions.md` | tier 2's settled-register half; frozen decisions are driver evidence |
| `ard.md` | tier 3 |
| `specification.md` | tier 4; the authored test-case count sizes QA |
| `code-defect-log.md` | defect source 1 (§7) |
| every file under `grounding/`, recursively — regular files only, never a symlink, no name beginning with `.` | tier 2's verified-grounding half; driver evidence; defect source 2 |
| every `interview/round-<N>.md`, and `interview/customer-questions.md` | the register's settledness; the open-items sweep's unanswered customer questions (§8) |
| every `self-review-<YYYYMMDD>.md` | defect source 3 |
| `epic.md` in every immediate `EPIC-*` subfolder | seeds the middle work packages (§7) |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | productivity basis, roles, calendar, engagement model |

**An umbrella's** — paths relative to the BRD folder:

| Input | What a change to it means |
|---|---|
| `<slice>/brd-link.md`, for every slice `commands/brd-proposal.md` Phase 2 enumerates | a slice carved or removed since |
| `<slice>/proposal.md`, for every slice holding one, included or excluded | a slice re-priced since, or one excluded then and priced since |
| `coverage-ledger.md`, the root ledger | the coverage statement (§14) |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | team shape and calendar: peak concurrency and the schedule |

**Not inputs:** `proposal.md` and `proposal-brief.md` (the output, and §8's stability anchor),
`revisions/`, and — in a slice — `brd-link.md` and `coverage-ledger.md`, which `/prd-proposal` reads
only to word a refusal. **An input absent when the run priced has no line**, so its later appearance
is a change: `ard.md` landing after a tier-2 proposal makes it stale, which is the point — the umbrella
above it takes the minimum of its slices' tiers (§14). **The profile is one file for the whole specs
repository**, so correcting it makes every proposal priced under the old one stale — truthfully: a
re-run would price each of them differently.

### 15.2 The record

```
<!-- priced-against
$SPECS_PATH/.dev-workflows/proposal-profile.yml <id>
PRD-1234-01/brd-link.md <id>
PRD-1234-01/proposal.md <id>
PRD-1234-02/brd-link.md <id> excluded
coverage-ledger.md <id>
-->
```

That one is an umbrella's; a slice's has the same shape over its own set, and never an `excluded`.
**The block is the last thing in the file** — only whitespace may follow it — and holds one line per
input present when the run recorded: the path as §15.1 writes it, one space, and the id
`git hash-object` gives the file's content — 40 lowercase hexadecimal characters, or 64 in a
repository using SHA-256 objects — sorted by path in byte order. **In an umbrella's record an excluded
slice's `brd-link.md` line ends ` excluded`**, which is how a later reader knows which slices the
umbrella included; that word appears on no other line. The id is git's because inside a repository
`hash-object` applies the clean filters a commit would — a CRLF and an LF checkout of one file hash
alike — and outside one it still runs. The paths are folder-relative so a folder moved with `git mv`
keeps its record; the profile, which sits outside every folder, keeps its literal `$SPECS_PATH/`
prefix. **An HTML comment** because a proposal is a document a vendor sends a customer: it is
invisible wherever the markdown renders, archived with the revision it belongs to (§2), and committed
and gated with it.

**A record that does not parse is no record** — not the last thing in the file, not closed, a line
that is not `<path> <id>` (or an umbrella's `<slice>/brd-link.md <id> excluded`), an id of any other
length, a path recorded twice. The reader falls back to the time rule and says the record is
unreadable.

### 15.3 The script, and who runs what

**One bundled script computes, writes and compares the record, and nothing else does**:
`${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py`, Python standard library only, self-tested in CI.
Enumerating §15.1, hashing, sorting and parsing are exactly what a run re-deriving them from prose
gets subtly wrong, so **no run computes, copies or edits an id itself**.

| Subcommand | What it does | Run by |
|---|---|---|
| `record --specs <SPECS_PATH> --folder <folder>` | prints a slice's record for the inputs on disk now | `/prd-proposal`, end of Phase 2 |
| `record … --brd-key <KEY> [--excluded <slice-dir>,…]` | prints an umbrella's, the excluded slices marked | `/brd-proposal`, end of Phase 5 |
| `stamp --proposal <proposal.md> --record <file>` | makes the block in `<file>` the last thing in the proposal, replacing a record already ending it, preserving every other byte; prints whether it wrote | the authoring phase, the pre-lint, and after the triage's last edit |
| `check --specs <SPECS_PATH> --proposal <proposal.md> [--brd-key <KEY>]` | compares the record with the inputs on disk | the authoring phase; `/brd-proposal` Phase 2; `/prd-proposal` Phase 11 |

`check` prints `basis: content` with `current` and the `changed`, `added` and `removed` paths — an
umbrella's adding the `included` and `excluded` slices its record names — or `basis: none` with
`reason: no-record`, or `reason: unreadable` and a `detail`. **Exit 0 whenever it ran**: a stale or
recordless proposal is a result, not a failure. Exit 2 when it could not run, the cause on stderr.

### 15.4 When the ids are taken

**Once, when pricing begins, and never again for the same proposal.** `record` writes the block to a
temp file (`command mktemp`, never inside a repository) — `/prd-proposal` at the end of Phase 2, once
the profile is settled and before Phase 3 reads the folder; `/brd-proposal` at the end of Phase 5,
once the walk has settled which slices are excluded and the profile is settled, and before Phase 6
reads a slice's figures. The authoring phase stamps that file's block and runs `check`: where an
input moved while the run was pricing, the record still holds the ids the run began from, so the
proposal reads as stale at once and the final report names each moved input. A record of later ids
would claim the run priced content it may only partly have seen.

### 15.5 What current means

**A slice's proposal is current** where `check` returns `basis: content` and `current: true`, and
**stale** where it returns `current: false`, each path it lists being why. The working-tree content
counts, committed or not: a re-run prices what is on disk. Where `check` returns `basis: none`,
`commands/brd-proposal.md` Phase 2's time rule decides.

**An umbrella is current** where `check --brd-key` returns `current: true` **and** every slice in its
`included` list is itself current by the slice test — a slice whose own inputs moved needs re-pricing,
and so does every umbrella that included it, which is why no slice's `prd.md` sits in the umbrella's
set. A slice with no readable record is judged by its times, and one whose times cannot be ordered
counts as not current. `commands/brd-proposal.md` Phase 2 runs this test before the walk and offers to
stop where the umbrella is current.

**The readers**: `commands/brd-proposal.md` — each slice's record in Phase 2, as the one command
reading another folder's proposal, and its own umbrella's, as an own-folder read — and
`commands/prd-proposal.md`'s next-step offer, which reads a sibling's record and nothing else of it
(§0).
````

- [ ] **Step 4: Run the check to verify it passes**

Run: `python3 $SCRATCH/t2.py && ./scripts/check-docs.sh --root . > $SCRATCH/cd2.txt 2>&1; tail -3 $SCRATCH/cd2.txt`
Expected: `t2 ok`; check-docs ends with its pass line (0 failures).

- [ ] **Step 5: Commit**

```bash
git add plugins/product-workflows/references/proposal-format.md
git diff --cached --summary | grep mode   # expect nothing
git commit -m "docs(product-workflows): proposal-format §15 — the priced-against record: input sets, grammar, the script, when the ids are taken, what current means; the census gains the one record-only read

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

---

### Task 3: `/prd-proposal` records, stamps and reads siblings' records; the reviewer ignores the record

**Files:**
- Modify: `plugins/product-workflows/commands/prd-proposal.md` (census ~line 39; Phase 2 end ~line 335; Phase 7 end ~line 517; Phase 9 steps 1 and 3 ~lines 552 and 584; Phase 10 class paragraph ~line 610; Phase 11 *Current* ~lines 661–667; Phase 12 stop list ~line 710; Final report ~lines 770 and 784)
- Modify: `plugins/product-workflows/agents/proposal-reviewer.md` (Hard rules)

**Interfaces:**
- Consumes: Task 1's `record`, `stamp`, `check` CLI; Task 2's §15, §15.3, §15.4, §15.5 anchors.
- Produces: stop id `PRD_PROPOSAL_RECORD_FAILED`; `$rec` (temp-file path) carried from Phase 2 to Phases 7 and 9.

- [ ] **Step 1: Write the failing check** — `$SCRATCH/t3.py`:

```python
c = open("plugins/product-workflows/commands/prd-proposal.md").read()
a = open("plugins/product-workflows/agents/proposal-reviewer.md").read()
need_c = ["One read is of the `priced-against` record alone", "proposal-record.py\" record --specs",
          "proposal-record.py\" stamp --proposal", "proposal-record.py\" check --specs",
          "PRD_PROPOSAL_RECORD_FAILED: <the cause>", "`PRD_PROPOSAL_RECORD_FAILED` and an unset",
          "**The\n   `priced-against` record is checked here too**", "run Phase 7's `stamp` once more",
          "reads only its `priced-against` record at its next-step offer", "the one record-only read the census",
          "**the `priced-against` record** — stamped", "reads only its `priced-against`\nrecord. The residual risk"]
assert "It never opens a sibling's proposal" not in c
missing = [n for n in need_c if n not in c]
assert not missing, missing
assert "NEVER raise a finding against the `<!-- priced-against … -->` comment" in a
print("t3 ok")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 $SCRATCH/t3.py` — Expected: `AssertionError` (the first assert: the sentence to be replaced is still there).

- [ ] **Step 3: Apply the edits**

```python
p = "plugins/product-workflows/commands/prd-proposal.md"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# census, top of file
rep("parent BRD, as ordinary prose, and never edits one — a stale reference in it goes to *what still\n"
    "needs a human*, fixed by re-running this command.",
    "parent BRD, as ordinary prose, and never edits one — a stale reference in it goes to *what still\n"
    "needs a human*, fixed by re-running this command. One read is of the `priced-against` record alone:\n"
    "a sibling slice's run of this command reads this proposal's record — and nothing else of it — at its\n"
    "next-step offer (Phase 11), to decide whether to offer pricing this slice\n"
    "(`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §15).")

# Phase 2 end: take the ids
rep("the value is not read.\n\n---\n\n## Phase 3 — Grade the readiness tier",
    "the value is not read.\n\n"
    "**Record which version of each input this run prices — now**, once the profile is settled and before\n"
    "Phase 3 reads the folder (`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §15.4):\n\n"
    "```bash\n"
    "rec=$(command mktemp -t proposal-record-XXXXXX)   # never inside a repository\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" record --specs \"$SPECS_PATH\" --folder \"<the resolved folder>\" > \"$rec\"\n"
    "```\n\n"
    "Keep `$rec`'s path: Phase 7 stamps that file and Phase 9 re-stamps it. **Never compute, copy or edit\n"
    "an id yourself** — the script enumerates §15.1's input set, hashes each file and sorts the block.\n"
    "Where it exits 2, or `python3` is not installed, stop with the script's stderr, or the shell's, after\n"
    "the colon:\n"
    "`PRD_PROPOSAL_RECORD_FAILED: <the cause> — a proposal that cannot record what it priced can never be told current or stale. Fix the cause and re-run.`\n\n"
    "---\n\n## Phase 3 — Grade the readiness tier")

# Phase 7 end: stamp + check
rep("Write the whole file as prose that is never hard-wrapped (`workflows-core:prose-formatting`).\n\n---\n\n"
    "## Phase 8 — Author `proposal-brief.md`",
    "Write the whole file as prose that is never hard-wrapped (`workflows-core:prose-formatting`).\n\n"
    "**Then end it with the `priced-against` record, through the script and only through it** (§15.3):\n\n"
    "```bash\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" stamp --proposal \"<folder>/proposal.md\" --record \"$rec\"\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" check --specs \"$SPECS_PATH\" --proposal \"<folder>/proposal.md\"\n"
    "```\n\n"
    "The record holds the ids Phase 2 took, so `check` returning `current: false` means an input moved\n"
    "while this run was pricing: name each path it lists — changed, added or removed — in the final\n"
    "report, and say that the proposal will read as stale to `/product-workflows:brd-proposal` and to a\n"
    "sibling's next-step offer until it is re-run. That is the truthful state: this run priced what it\n"
    "read, and cannot say how much of the moved file it saw. Either call exiting 2 stops the run with\n"
    "`PRD_PROPOSAL_RECORD_FAILED` (Phase 2).\n\n"
    "---\n\n## Phase 8 — Author `proposal-brief.md`")

# Phase 9 step 1: pre-lint the record
rep("   proposal; §4 and §10 are what required-section presence is checked against. Advisory — surface\n"
    "   every finding, inline-fix the mechanical ones, and proceed; the reviewer is the gate.\n2. **The review gate.**",
    "   proposal; §4 and §10 are what required-section presence is checked against. Advisory — surface\n"
    "   every finding, inline-fix the mechanical ones, and proceed; the reviewer is the gate. **The\n"
    "   `priced-against` record is checked here too** (§15.3): re-run Phase 7's `stamp` with the same\n"
    "   `$rec`. `{\"written\": false}` passes; `{\"written\": true}` means the record was missing, altered or\n"
    "   no longer last — a pre-lint finding, already fixed by that run from Phase 2's ids, never from a\n"
    "   fresh hash.\n2. **The review gate.**")

# Phase 9 step 3: re-stamp after the last edit
rep("   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.\n\n"
    "**The recorded verdict names the version it was taken against**",
    "   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.\n\n"
    "**After the last inline edit to `proposal.md` — a triage fix, or an edit a later prompt asked for —\n"
    "run Phase 7's `stamp` once more** with the same `$rec`, so no edit carries a damaged record into the\n"
    "handoff; `{\"written\": true}` there is reported beside the edit that caused it.\n\n"
    "**The recorded verdict names the version it was taken against**")

# Phase 10 class paragraph
rep("nothing, so it moves no class here; nor does `/product-workflows:brd-reconcile`'s stale\n"
    "cross-reference sweep, which reads it as prose, stops nothing and never edits it.)",
    "nothing, so it moves no class here; nor does `/product-workflows:brd-reconcile`'s stale\n"
    "cross-reference sweep, which reads it as prose, stops nothing and never edits it; nor does a sibling\n"
    "slice's run of this command, which reads only its `priced-against` record at its next-step offer\n"
    "and stops nothing.)")

# Phase 11: what current means for a sibling
rep("sibling holds a *stale* one — it would vanish in the commonest case there is. **Current** is\n"
    "`/product-workflows:brd-proposal` Phase 3's test, decided by presence and the times\n"
    "`/product-workflows:brd-proposal` Phase 2 records (a committed, unmodified path's last commit time,\n"
    "else its modification time): a sibling's `proposal.md` exists and is not older than that sibling's\n"
    "`prd.md`, `decisions.md` or `grounding/`, and a time that cannot be ordered (a tie, a shallow clone)\n"
    "counts as not current here, so the option stands for it. It never opens a sibling's proposal, so this is no read of another\n"
    "folder's proposal and the census at the top of this file stands. **Where",
    "sibling holds a *stale* one — it would vanish in the commonest case there is. **Current** is\n"
    "`/product-workflows:brd-proposal` Phase 3's test, decided as `/product-workflows:brd-proposal`\n"
    "Phase 2 decides it (`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §15.5): a sibling's\n"
    "`proposal.md` exists, and\n"
    "`python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" check --specs \"$SPECS_PATH\" --proposal \"<sibling>/proposal.md\"`\n"
    "returns `basis: content` with `current: true` — or, where it returns `basis: none` (a proposal\n"
    "written before the record existed, or one whose record does not parse), the times\n"
    "`/product-workflows:brd-proposal` Phase 2 records show it is not older than that sibling's `prd.md`,\n"
    "`decisions.md` or `grounding/`. A time that cannot be ordered (a tie, a shallow clone), and a `check`\n"
    "that cannot run (exit 2), count as not current here, so the option stands for it — this phase never\n"
    "stops the run. **That reads the sibling's `priced-against` record and nothing else of its\n"
    "proposal** — no figure, no section — the one record-only read the census at the top of this file\n"
    "names. **Where")

# Phase 12 stop list
rep("`PRD_PROPOSAL_BASELINE_UNREADABLE`, `PRD_PROPOSAL_NEEDS_PROFILE` and an unset `$SPECS_PATH` each",
    "`PRD_PROPOSAL_BASELINE_UNREADABLE`, `PRD_PROPOSAL_NEEDS_PROFILE`, `PRD_PROPOSAL_RECORD_FAILED` and an unset `$SPECS_PATH` each")

# Final report
rep("a revision, the archived paths, and whether `--redo` discarded the anchor; the `--baseline` path where",
    "a revision, the archived paths, and whether `--redo` discarded the anchor; **the `priced-against` record** — stamped, and every input Phase 7's `check` found moved during the run, or that none did, and any pre-lint or post-triage re-stamp that wrote; the `--baseline` path where")
rep("as prose, and never edits one. The residual risk",
    "as prose, and never edits one; a sibling slice's run of this command reads only its `priced-against`\nrecord. The residual risk")
open(p, "w").write(s)

p = "plugins/product-workflows/agents/proposal-reviewer.md"
a = open(p).read()
old = "- NEVER return an empty findings list without the per-check account Process step 6 requires.\n"
assert a.count(old) == 1
a = a.replace(old, old +
    "- NEVER raise a finding against the `<!-- priced-against … -->` comment that ends a proposal, nor\n"
    "  count it against §4's or §10's section set. It is machine data the producing command writes and\n"
    "  checks through its bundled script (`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §15),\n"
    "  not a section and not prose.\n")
open(p, "w").write(a)
```

- [ ] **Step 4: Run the checks to verify they pass**

Run: `python3 $SCRATCH/t3.py && ./scripts/check-docs.sh --root . > $SCRATCH/cd3.txt 2>&1; tail -3 $SCRATCH/cd3.txt; python3 scripts/validate-catalog.py > $SCRATCH/vc3.txt 2>&1; tail -3 $SCRATCH/vc3.txt`
Expected: `t3 ok`; check-docs and validate-catalog both end with 0 failures (warnings read and judged).

- [ ] **Step 5: Commit**

```bash
git add plugins/product-workflows/commands/prd-proposal.md plugins/product-workflows/agents/proposal-reviewer.md
git diff --cached --summary | grep mode   # expect nothing
git commit -m "feat(product-workflows): /prd-proposal records which version of each input it priced, stamps it into proposal.md and re-stamps after every edit; its next-step offer judges a sibling by its record; the reviewer never files the record

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

---

### Task 4: `/brd-proposal` — content basis per slice, the umbrella check, the umbrella's own record

**Files:**
- Modify: `plugins/product-workflows/commands/brd-proposal.md` (frontmatter description; census ~line 31; Phase 2 ~lines 220–254; Phase 3 table ~lines 268–270 and paragraph ~274–276; Phase 5 end ~line 405; Phase 8 end ~line 535; Phase 10 steps 1 and 3 ~lines 572 and 608; Phase 13 stop list ~line 709; Final report ~lines 762, 785 and 794)

**Interfaces:**
- Consumes: Task 1's CLI (`check --brd-key` returns `included`/`excluded`); Task 2's §15.3–§15.5.
- Produces: stop id `BRD_PROPOSAL_RECORD_FAILED`; the choice array `["Stop — the umbrella is current (Recommended)", "Re-price it anyway"]`; `$rec` carried from Phase 5 to Phases 8 and 10.

- [ ] **Step 1: Write the failing check** — `$SCRATCH/t4.py`:

```python
c = open("plugins/product-workflows/commands/brd-proposal.md").read()
need = ["first saying whether the umbrella on disk is still current",
        "reading its `priced-against` record to say whether it is current (Phase 2)",
        "**Basis `content` first**", "BRD_PROPOSAL_RECORD_FAILED: <the cause>",
        "**Then say whether the umbrella on disk is current**",
        'choices: ["Stop — the umbrella is current (Recommended)", "Re-price it anyway"]',
        "**`--redo` and\n  `--profile` skip the question**", "`proposal.md` present and stale — basis `content`",
        "present with no readable record, and its time cannot be ordered",
        "`proposal.md` present and current — basis `content`", "`by content` with\nevery input that moved",
        "**Record which version of each input the roll-up prices — now**", "--brd-key <BRD-KEY> --excluded",
        "The record holds the ids Phase 5 took", "re-run Phase 8's `stamp`", "run Phase 8's `stamp` once more",
        "`BRD_PROPOSAL_RECORD_FAILED` and an unset", "**On a run Phase 2 ended**",
        "the umbrella check's verdict at Phase 2", "the `priced-against` record — stamped",
        "reading its `priced-against` record to say whether it is current and anchoring"]
missing = [n for n in need if n not in c]
assert not missing, missing
import re
fm = re.search(r'^description: "(.*)"$', c, re.M).group(1)
assert len(fm) <= 600, len(fm)
print("t4 ok")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 $SCRATCH/t4.py` — Expected: `AssertionError` listing all 21 strings.

- [ ] **Step 3: Apply the edits**

```python
p = "plugins/product-workflows/commands/brd-proposal.md"
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

rep("by rolling up its slices' own proposals: walks each slice",
    "by rolling up its slices' own proposals, first saying whether the umbrella on disk is still current: walks each slice")

rep("run of this same command, anchoring its re-estimate on it (§8), and `proposal-reviewer` inside this\nrun (Phase 10);",
    "run of this same command, reading its `priced-against` record to say whether it is current (Phase 2)\n"
    "and anchoring its re-estimate on it (§8), and `proposal-reviewer` inside this\nrun (Phase 10);")

rep("Record, per slice: its key, its folder, whether `proposal.md` and `proposal-brief.md` are present,\n"
    "and the time of `proposal.md` against those of `prd.md`, `decisions.md` and `grounding/`, with the\n"
    "basis each was taken on — Phase 3 walks that record and decides nothing here. Every path below is\n"
    "relative to `$SPECS_PATH`, and every git call runs as `git -C \"$SPECS_PATH\"`, so the run reads the\n"
    "specs repository wherever it was started. Times are seconds since the epoch, compared as numbers.\n",
    "Record, per slice: its key, its folder, whether `proposal.md` and `proposal-brief.md` are present,\n"
    "and, where `proposal.md` is, whether it is current and the basis that decided it — Phase 3 walks that\n"
    "record and decides nothing here. Every path below is relative to `$SPECS_PATH`, and every git call\n"
    "runs as `git -C \"$SPECS_PATH\"`, so the run reads the specs repository wherever it was started.\n\n"
    "**Basis `content` first** (`${CLAUDE_PLUGIN_ROOT}/references/proposal-format.md` §15.5):\n\n"
    "```bash\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" check --specs \"$SPECS_PATH\" --proposal \"<slice>/proposal.md\"\n"
    "```\n\n"
    "Where it returns `basis: content`, the proposal ends with a well-formed `priced-against` record and\n"
    "the script has compared every input that slice's proposal priced with what is on disk — `ard.md`,\n"
    "`specification.md`, the interview records, the defect sources, the Epics and the profile as well as\n"
    "`prd.md`, `decisions.md` and `grounding/`: `current: true` is current, and `current: false` is\n"
    "stale, every path it lists `changed`, `added` or `removed` being why. The working-tree content\n"
    "counts, committed or not: a re-run would price what is on disk. **Never compute or compare an id\n"
    "yourself.** A script that exits 2, or a missing `python3`, stops the run with the cause after the\n"
    "colon:\n"
    "`BRD_PROPOSAL_RECORD_FAILED: <the cause> — a proposal's currency cannot be decided without the record script. Fix the cause and re-run.`\n\n"
    "**Where it returns `basis: none`** — a proposal written before the record existed (`reason:\n"
    "no-record`), or one whose record does not parse (`reason: unreadable`, its `detail` printed in the\n"
    "walk's picture) — the proposal's time against those of `prd.md`, `decisions.md` and `grounding/`\n"
    "decides, with the basis each was taken on. Times are seconds since the epoch, compared as numbers.\n")

rep("committed later by someone else still reads as current against it — the walk's picture shows each\n"
    "slice's basis for exactly that reason.\n",
    "committed later by someone else still reads as current against it — the walk's picture shows each\n"
    "slice's basis for exactly that reason, and says beside every slice decided by time that re-pricing it\n"
    "once moves it to basis `content`, which records exactly what was priced.\n")

rep("  Carve them first: /product-workflows:brd-split <BRD-KEY> \"<how to cut it>\"\n```\n\n---\n\n## Phase 3 — The readiness walk",
    "  Carve them first: /product-workflows:brd-split <BRD-KEY> \"<how to cut it>\"\n```\n\n"
    "**Then say whether the umbrella on disk is current** — only where the resolved folder already holds a\n"
    "`proposal.md`; a first run has no umbrella to ask about (§15.5):\n\n"
    "```bash\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" check --specs \"$SPECS_PATH\" --proposal \"<folder>/proposal.md\" --brd-key <BRD-KEY>\n"
    "```\n\n"
    "**It is current** where that returns `basis: content` and `current: true` **and** every slice in its\n"
    "`included` list is current by the per-slice test above — a slice found stale, or `undecidable` on a\n"
    "time basis, makes the umbrella not current too. Print the verdict and every reason: each path the\n"
    "script lists `changed`, `added` or `removed` — a slice's `brd-link.md` added is a slice carved since\n"
    "and one removed a slice gone, its `proposal.md` changed is a slice re-priced since, a `proposal.md`\n"
    "added under a slice in the `excluded` list is a slice excluded then and priced since, and the profile\n"
    "or the root ledger changed is named as itself — and each included slice that is not current, with\n"
    "that slice's own reasons. Exit 2 stops the run with `BRD_PROPOSAL_RECORD_FAILED`, as above.\n\n"
    "- **Current** — ask, printing the recommendation beside the array:\n"
    "  `choices: [\"Stop — the umbrella is current (Recommended)\", \"Re-price it anyway\"]`.\n"
    "  **Stop** ends the run here and writes no artifact. It is an operator's finished decision rather\n"
    "  than a refusal, so it carries no stop id and runs the emitter tail (Phase 13) on the way out,\n"
    "  exactly as a completed run does. **Re-price it anyway** continues into the walk. **`--redo` and\n"
    "  `--profile` skip the question** — each already asks for a re-price — and the run prints the verdict\n"
    "  and continues.\n"
    "- **Not current, or `basis: none`** — print the reasons, or *no priced-against record — re-price once\n"
    "  to enable this check* (with the script's `detail` where the reason is `unreadable`), and continue\n"
    "  into the walk without a question.\n\n"
    "**This check decides only whether the run goes on**: every slice still gets its own row and\n"
    "recommendation in the walk below.\n\n"
    "---\n\n## Phase 3 — The readiness walk")

rep("| `proposal.md` present but older than the slice's own `prd.md`, `decisions.md` or grounding files |",
    "| `proposal.md` present and stale — basis `content`: an input it priced changed, added or removed; a time basis: older than its own `prd.md`, `decisions.md` or grounding files |")
rep("| `proposal.md` present, but its time cannot be ordered against its inputs' (Phase 2 basis `undecidable`) |",
    "| `proposal.md` present with no readable record, and its time cannot be ordered against its inputs' (Phase 2 basis `undecidable`) |")
rep("| `proposal.md` present and older than none of them |",
    "| `proposal.md` present and current — basis `content`: every input it priced unchanged; a time basis: older than none of them |")
rep("decide which of the two no-`proposal.md` rows a slice is in; a slice with a `proposal.md` is placed by\n"
    "the times and basis Phase 2 recorded, and the walk's picture names that basis beside it — `by commit`,\n"
    "`by file time` or `undecidable` with its reason — and its tier is the one its proposal already carries.",
    "decide which of the two no-`proposal.md` rows a slice is in; a slice with a `proposal.md` is placed by\n"
    "the basis Phase 2 recorded, and the walk's picture names that basis beside it — `by content` with\n"
    "every input that moved, or `by commit`, `by file time` or `undecidable` with its reason and the note\n"
    "that re-pricing the slice once moves it to basis `content` — and its tier is the one its proposal\n"
    "already carries.")

rep("the value is not read.\n\n---\n\n## Phase 6",
    "the value is not read.\n\n"
    "**Record which version of each input the roll-up prices — now**, once the walk has settled which\n"
    "slices are excluded and the profile is settled, and before Phase 6 reads a slice's figures (§15.4):\n\n"
    "```bash\n"
    "rec=$(command mktemp -t proposal-record-XXXXXX)   # never inside a repository\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" record --specs \"$SPECS_PATH\" --folder \"<the resolved folder>\" --brd-key <BRD-KEY> --excluded <slice-dir>,<slice-dir> > \"$rec\"\n"
    "```\n\n"
    "`--excluded` names every slice folder the walk excluded, by directory name, and is omitted where it\n"
    "excluded none — the record marks those slices, so a later run knows which ones this umbrella\n"
    "included. Keep `$rec`'s path: Phase 8 stamps that file and Phase 10 re-stamps it. **Never compute,\n"
    "copy or edit an id yourself.** Exit 2, or a missing `python3`, stops the run with\n"
    "`BRD_PROPOSAL_RECORD_FAILED` (Phase 2).\n\n"
    "---\n\n## Phase 6")

rep("Write the whole file as prose that is never hard-wrapped (`workflows-core:prose-formatting`).\n\n---\n\n"
    "## Phase 9 — Author `proposal-brief.md`",
    "Write the whole file as prose that is never hard-wrapped (`workflows-core:prose-formatting`).\n\n"
    "**Then end it with the `priced-against` record, through the script and only through it** (§15.3):\n\n"
    "```bash\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" stamp --proposal \"<folder>/proposal.md\" --record \"$rec\"\n"
    "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py\" check --specs \"$SPECS_PATH\" --proposal \"<folder>/proposal.md\" --brd-key <BRD-KEY>\n"
    "```\n\n"
    "The record holds the ids Phase 5 took, so `check` returning `current: false` means an input moved\n"
    "while this run was rolling up — a slice re-priced, carved or removed, the root ledger or the profile\n"
    "changed: name each path it lists in the final report, and say that the next run of this command will\n"
    "report the umbrella as not current until it is re-run. Either call exiting 2 stops the run with\n"
    "`BRD_PROPOSAL_RECORD_FAILED` (Phase 2).\n\n"
    "---\n\n## Phase 9 — Author `proposal-brief.md`")

rep("   rather than an oversight to be corrected. Advisory — surface every finding, inline-fix the\n"
    "   mechanical ones, and proceed; the reviewer is the gate.\n2. **The review gate.**",
    "   rather than an oversight to be corrected. Advisory — surface every finding, inline-fix the\n"
    "   mechanical ones, and proceed; the reviewer is the gate. **The `priced-against` record is checked\n"
    "   here too** (§15.3): re-run Phase 8's `stamp` with the same `$rec`. `{\"written\": false}` passes;\n"
    "   `{\"written\": true}` means the record was missing, altered or no longer last — a pre-lint finding,\n"
    "   already fixed by that run from Phase 5's ids, never from a fresh hash.\n2. **The review gate.**")

rep("   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.\n\n"
    "**The recorded verdict names the version it was taken against**",
    "   `BLOCK`, which raised no BLOCKER, the run ends as Cancel does — and **Cancel** aborts the run.\n\n"
    "**After the last inline edit to `proposal.md` — a triage fix, or an edit a later prompt asked for —\n"
    "run Phase 8's `stamp` once more** with the same `$rec`, so no edit carries a damaged record into the\n"
    "handoff; `{\"written\": true}` there is reported beside the edit that caused it.\n\n"
    "**The recorded verdict names the version it was taken against**")

rep("`BRD_PROPOSAL_NEEDS_PROFILE` and an unset `$SPECS_PATH` each report",
    "`BRD_PROPOSAL_NEEDS_PROFILE`, `BRD_PROPOSAL_RECORD_FAILED` and an unset `$SPECS_PATH` each report")

rep("**On a run the walk ended** — the operator answered \"Price the slice first\" or \"Re-price it first\" —",
    "**On a run Phase 2 ended** — the operator answered *Stop — the umbrella is current* — the report is\n"
    "the umbrella check's verdict and its basis, every slice Phase 2 enumerated with the basis that decided\n"
    "it, and that no artifact was written.\n"
    "**On a run the walk ended** — the operator answered \"Price the slice first\" or \"Re-price it first\" —")
rep("Otherwise:\nthe `require-on-main` return for each included slice;",
    "Otherwise:\nthe umbrella check's verdict at Phase 2 with every reason it printed, or that the folder held no\n"
    "umbrella yet; the `require-on-main` return for each included slice;")
rep("the anchor; the profile's `engagement_model`,",
    "the anchor; the `priced-against` record — stamped, with every input Phase 8's `check` found moved\n"
    "during the run, or that none did, and any pre-lint or post-triage re-stamp that wrote; the profile's `engagement_model`,")
rep("work; every targeted read of an umbrella is an own-folder one — a later run of this command,\n"
    "anchoring its own re-estimate on it (§8), and `proposal-reviewer` inside the run that wrote it;",
    "work; every targeted read of an umbrella is an own-folder one — a later run of this command,\n"
    "reading its `priced-against` record to say whether it is current and anchoring its own re-estimate on\n"
    "it (§8), and `proposal-reviewer` inside the run that wrote it;")
open(p, "w").write(s)
```

- [ ] **Step 4: Run the checks to verify they pass**

Run: `python3 $SCRATCH/t4.py && ./scripts/check-docs.sh --root . > $SCRATCH/cd4.txt 2>&1; tail -3 $SCRATCH/cd4.txt; python3 scripts/validate-catalog.py > $SCRATCH/vc4.txt 2>&1; tail -3 $SCRATCH/vc4.txt`
Expected: `t4 ok`; both gates 0 failures (check 12 sees a two-option array; any warning read and judged).

- [ ] **Step 5: Commit**

```bash
git add plugins/product-workflows/commands/brd-proposal.md
git diff --cached --summary | grep mode   # expect nothing
git commit -m "feat(product-workflows): /brd-proposal judges each slice by its priced-against record (times only for one without), says first whether the umbrella on disk is current and offers to stop, and records the umbrella's own inputs with the excluded slices marked

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

---

### Task 5: Docs, rules and the register's naming sentence

**Files:**
- Modify: `plugins/product-workflows/docs/commands/prd-proposal.md`, `plugins/product-workflows/docs/commands/brd-proposal.md`, `plugins/product-workflows/docs/reference/proposal-format.md`, `plugins/product-workflows/docs/roles-and-phases.md`, `.claude/rules/product-workflows.md`, `plugins/product-workflows/references/decision-register-format.md`

**Interfaces:**
- Consumes: Tasks 1–4's behaviour, stop ids and the umbrella question, as each Interfaces block states.
- Produces: nothing code consumes.

- [ ] **Step 1: Write the failing check** — `$SCRATCH/t5.py`:

```python
P = "plugins/product-workflows/"
def has(path, *needles):
    s = open(path).read()
    missing = [n for n in needles if n not in s]
    assert not missing, (path, missing)
has(P + "docs/commands/prd-proposal.md", "- **`python3`** — the run records", "It ends with a `priced-against` record",
    "One read is of the record alone: a sibling slice's run")
has(P + "docs/commands/brd-proposal.md", "- **`python3`** — for the bundled", "**It says first whether the umbrella on disk is still current.**",
    "A slice whose `proposal.md` is stale is recommended for re-pricing", "first reads its `priced-against` record",
    "whose `priced-against` record still matches every input it priced", "It ends with a `priced-against` record")
has(P + "docs/reference/proposal-format.md", "## Knowing when one is out of date", "One read is of the record alone")
has(P + "docs/roles-and-phases.md", "One more is of the record alone", "to say whether it is still current")
has(".claude/rules/product-workflows.md", "**A proposal's currency is its `priced-against` record**",
    "record which version of each input it prices", "an umbrella already on disk: current?")
has(P + "references/decision-register-format.md", "to compare it with what a proposal priced")
print("t5 ok")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 $SCRATCH/t5.py` — Expected: `AssertionError` on the first file.

- [ ] **Step 3: Apply the edits**

```python
def edit(path, pairs):
    s = open(path).read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:80])
        s = s.replace(old, new)
    open(path, "w").write(s)

P = "plugins/product-workflows/"
edit(P + "docs/commands/prd-proposal.md", [
    ("- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH` and offers to enter a path or cancel.\n\n**Nothing else is required.**",
     "- **`python3`** — the run records which version of each input it priced with product-workflows' bundled script `scripts/proposal-record.py` (standard library only); without it the run stops with `PRD_PROPOSAL_RECORD_FAILED` before it prices anything.\n"
     "- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH` and offers to enter a path or cancel.\n\n**Nothing else is required.**"),
    ("a reader is never handed a number without being told what grade of evidence stands behind it.",
     "a reader is never handed a number without being told what grade of evidence stands behind it. It ends with a `priced-against` record — an HTML comment, invisible wherever the markdown renders — naming the version of every input the run priced: the PRD, the register, the grounding, the ARD and specification, the interview records, the defect sources, the Epics and the shared profile. That record is how [`/brd-proposal`](brd-proposal.md), and a sibling slice's run of this command, later tell whether the proposal is still current ([`proposal-format.md`](../../references/proposal-format.md) §15)."),
    ("and `proposal-reviewer` inside the run that wrote it, under *Gates* above. One read is not a proposal read at all",
     "and `proposal-reviewer` inside the run that wrote it, under *Gates* above. One read is of the record alone: a sibling slice's run of this command reads this proposal's `priced-against` record, and nothing else of it, to decide whether to offer pricing this slice. One read is not a proposal read at all"),
])
edit(P + "docs/commands/brd-proposal.md", [
    ("rather than through a delegated writer — exactly as the sibling authors a slice's proposal.\n",
     "rather than through a delegated writer — exactly as the sibling authors a slice's proposal.\n\n"
     "**It says first whether the umbrella on disk is still current.** Before the walk asks anything, a run on a folder that already holds an umbrella compares that umbrella's `priced-against` record with the slices on disk and prints every reason it is not current — a slice re-priced, carved, removed, or priced after being excluded; an included slice that is itself stale; the root ledger or the profile changed. Where nothing has moved it offers to stop there, writing nothing; `--redo` and `--profile` skip that question. An umbrella written before the record existed says so, and the run carries on.\n"),
    ("A slice whose `proposal.md` is older than its own `prd.md`, `decisions.md` or grounding files is recommended for re-pricing.",
     "A slice whose `proposal.md` is stale is recommended for re-pricing: one carrying a `priced-against` record is stale when any input it priced has changed, appeared or gone since — its PRD, register, grounding, ARD, specification, interview records, defect sources, Epics or the shared profile — and one written before the record existed is stale when it is older than its own `prd.md`, `decisions.md` or grounding files."),
    ("- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH` and offers to enter a path or cancel.\n\n**Nothing else is required, and nothing at this altitude could be**",
     "- **`python3`** — for the bundled `scripts/proposal-record.py`, which decides each slice's and the umbrella's currency and records what this run rolled up; without it the run stops with `BRD_PROPOSAL_RECORD_FAILED`.\n"
     "- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH` and offers to enter a path or cancel.\n\n**Nothing else is required, and nothing at this altitude could be**"),
    ("It does not restate a slice's driver table and never re-derives a slice's hours.",
     "It does not restate a slice's driver table and never re-derives a slice's hours. It ends with a `priced-against` record — invisible wherever the markdown renders — naming the version of every slice proposal, slice link, root ledger and profile it rolled up, and which slices it excluded: that is what the next run's currency check reads."),
    ("a later run of this command, which anchors its re-estimate on the prior figures, and `proposal-reviewer`",
     "a later run of this command, which first reads its `priced-against` record to say whether it is current and anchors its re-estimate on the prior figures, and `proposal-reviewer`"),
    ("three hold a `proposal.md` newer than everything feeding it",
     "three hold a `proposal.md` whose `priced-against` record still matches every input it priced"),
])
edit(P + "docs/reference/proposal-format.md", [
    ("## The programme umbrella\n",
     "## Knowing when one is out of date\n\n"
     "Every proposal ends with a `priced-against` record: an HTML comment, invisible wherever the markdown renders, naming the exact version of every input the run priced. A slice's proposal records its PRD, decision register, grounding, ARD, specification, interview records, defect sources, Epics and the shared proposal profile; an umbrella's records each slice's link and proposal, the root coverage ledger and the profile, and which slices it excluded.\n\n"
     "Whether a proposal is current is decided by comparing that record with what is on disk — contents, not dates, so a fresh clone, a squash merge or a local edit cannot make a stale proposal look current. [`/brd-proposal`](../commands/brd-proposal.md) runs the comparison for every slice in its readiness walk, and first for the umbrella itself: where nothing has moved since the umbrella was written, it says so and offers to stop. Because the profile is shared, correcting it makes every proposal priced under the old one stale. A proposal written before the record existed falls back to comparing times until it is next re-priced.\n\n"
     "## The programme umbrella\n"),
    ("that run archives the prior revision and classifies each change it records as a correction or a re-estimate.\n",
     "that run archives the prior revision and classifies each change it records as a correction or a re-estimate. One read is of the record alone: a sibling slice's run of [`/prd-proposal`](../commands/prd-proposal.md) reads a proposal's `priced-against` record, and nothing else of it, to decide whether to offer pricing that slice.\n"),
])
edit(P + "docs/roles-and-phases.md", [
    ("a later run of `/brd-proposal` anchors its re-estimate on the umbrella it wrote last time",
     "a later run of `/brd-proposal` reads the umbrella it wrote last time to say whether it is still current and anchors its re-estimate on it"),
    ("classifies each change it records as a correction or a re-estimate. It is its own phase rather than part of `brd-to-prd`",
     "classifies each change it records as a correction or a re-estimate. One more is of the record alone: a sibling slice's run of `/prd-proposal` reads a proposal's `priced-against` record, and nothing else of it, at its next-step offer. It is its own phase rather than part of `brd-to-prd`"),
])
edit(".claude/rules/product-workflows.md", [
    ("`/brd-reconcile`'s stale cross-reference sweep reads any proposal under the parent as ordinary prose and never edits one**.",
     "`/brd-reconcile`'s stale cross-reference sweep reads any proposal under the parent as ordinary prose and never edits one; a sibling slice's `/prd-proposal` reads only a proposal's `priced-against` record, at its next-step offer**. **A proposal's currency is its `priced-against` record** — the git blob id of every input it priced, recorded, stamped and compared only by `scripts/proposal-record.py` (`references/proposal-format.md` §15); a proposal without one falls back to times."),
    ("→ [resolve or grill the proposal profile] → grade the readiness tier (1–4)",
     "→ [resolve or grill the proposal profile] → [record which version of each input it prices: proposal-record.py] → grade the readiness tier (1–4)"),
    ("→ write proposal.md + proposal-brief.md (tier ≥ 2) → [pre-lint",
     "→ write proposal.md, ending in the stamped record, + proposal-brief.md (tier ≥ 2) → [pre-lint"),
    ("→ enumerate slices by the positive brd-link.md parent test → the readiness walk",
     "→ enumerate slices by the positive brd-link.md parent test, each slice's currency by its priced-against record (times for one without) → [an umbrella already on disk: current? → offer to stop] → the readiness walk"),
    ("→ [require-on-main: each included slice's proposal.md] → roll up",
     "→ [require-on-main: each included slice's proposal.md] → [record the input versions, excluded slices marked] → roll up"),
])
edit(P + "references/decision-register-format.md", [
    ("direction: a file may name it only to compare its time with a proposal's or to describe another",
     "direction: a file may name it only to compare it with what a proposal priced or to describe another"),
])
```

- [ ] **Step 4: Run the checks to verify they pass**

Run: `python3 $SCRATCH/t5.py && ./scripts/check-docs.sh --root . > $SCRATCH/cd5.txt 2>&1; tail -3 $SCRATCH/cd5.txt; python3 scripts/validate-catalog.py > $SCRATCH/vc5.txt 2>&1; tail -3 $SCRATCH/vc5.txt; ./scripts/check-id-grammar.sh --root . | tail -2`
Expected: `t5 ok`; check-docs 0 failures (check 9's 200-character table-cell limit and the links included), validate-catalog 0 failures, id-grammar clean.

- [ ] **Step 5: Commit**

```bash
git add plugins/product-workflows/docs .claude/rules/product-workflows.md plugins/product-workflows/references/decision-register-format.md
git diff --cached --summary | grep mode   # expect nothing
git commit -m "docs(product-workflows): the priced-against record and the umbrella's up-front currency check in the command pages, the format page, the phase page and the rules; python3 named as a need

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

---

### Task 6: Release, gates, whole-branch review, merge

**Files:**
- Modify: `plugins/product-workflows/CHANGELOG.md`, `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`

- [ ] **Step 1: Version and changelog** — Python edit: `"version": "3.26.1"` → `"3.27.0"` in `plugin.json` (once) and in `marketplace.json` (the product-workflows entry, once); insert under the changelog's header paragraph:

```markdown
## [3.27.0] — Unreleased

### Added
- **Every effort proposal records which version of each input it priced, and its currency is decided by content.** `/prd-proposal` ends `proposal.md` with a `priced-against` record — an HTML comment, invisible wherever the markdown renders — holding the git blob id of every input it priced: `prd.md`, `decisions.md`, `ard.md`, `specification.md`, the code-defect log, every grounding file, the interview rounds and customer questions, the self-reviews, each Epic's `epic.md` and the shared proposal profile. `/brd-proposal`'s readiness walk, and `/prd-proposal`'s next-step offer through the same test, compare that record with the inputs on disk: a proposal is stale when any input changed, appeared or vanished since — so a tier-2 proposal no longer reads as current after its slice's `ard.md` lands, and a squash merge, a fresh clone or a local edit can no longer make a stale proposal look current. A proposal written before this release keeps the 3.26.1 time rule until it is re-priced. The record is computed, stamped and compared only by a new bundled script, `scripts/proposal-record.py` (Python standard library, self-tested in CI); a run that cannot run it stops with `PRD_PROPOSAL_RECORD_FAILED` or `BRD_PROPOSAL_RECORD_FAILED`.
- **`/brd-proposal` says first whether the umbrella on disk is still current.** The umbrella records its own inputs — every slice's `brd-link.md` and `proposal.md`, the root coverage ledger, the profile, and which slices it excluded — and a later run reports, before the walk asks anything, every reason it is not current: a slice re-priced, carved, removed, or priced after being excluded; an included slice that is itself stale; the ledger or the profile changed. Where nothing moved, it offers to stop there and write nothing; `--redo` and `--profile` skip the question.
```

- [ ] **Step 2: Run every gate** (each to a file in `$SCRATCH`, tail read):

```bash
python3 plugins/product-workflows/scripts/proposal-record.py --selftest | tail -1        # selftest: 25/25 passed
python3 scripts/validate-catalog.py --selftest | tail -1 && python3 scripts/validate-catalog.py | tail -2
./scripts/check-id-grammar.sh --selftest | tail -1 && ./scripts/check-id-grammar.sh --root . | tail -1
./scripts/check-docs.sh --selftest > $SCRATCH/cds.txt 2>&1; tail -2 $SCRATCH/cds.txt
./scripts/check-docs.sh --root . | tail -2
npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund >/dev/null && node scripts/mermaid/check-mermaid.mjs --root . | tail -1
for s in plugins/*/scripts/*.py; do grep -q -- '--selftest' "$s" && python3 "$s" --selftest | tail -1; done
git diff --summary main...HEAD | grep mode    # only the new script, 100755
```
Expected: every gate passes; every other script's self-test unchanged.

- [ ] **Step 3: Commit the release**

```bash
git add plugins/product-workflows/CHANGELOG.md plugins/product-workflows/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(release): product-workflows 3.27.0 — proposal currency by content

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018c5oyZambF9QfvUmRnwA4d"
```

- [ ] **Step 4: Whole-branch review** — `review-package` over `git merge-base main HEAD..HEAD`, dispatched to a fresh reviewer on Opus with the spec, this plan, its Review Focus verbatim and the ledger's rulings. Every Critical, Important **and Minor** finding is fixed in the same round (the user's standing rule: minors are bugs), each test-first where code, each against a failing `t*.py`-style check where prose; the full gate list of Step 2 re-run green.

- [ ] **Step 5: Merge** — `git fetch origin`; take the next free product-workflows version above main's (3.27.0 unless taken — then renumber the heading, both manifests and the CHANGELOG entry); merge `origin/main` into the branch, resolving conflicts as main's text plus this change; date the heading (`— 2026-10-07` or the merge day) in a `chore(release): date <version>` commit; re-run Step 2's gates with `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`; `git checkout main && git merge --no-ff iv-gu/proposal-priced-against`; push `main`; watch CI to green; delete the branch, recording its SHA in `$SCRATCH/logs/deleted-branches.txt`.

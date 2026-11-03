#!/usr/bin/env python3
"""Document lineage: record which upstream bytes a document was built from, and tell whether they moved.

The authority for what this script does is workflows-core:document-lineage; the kind table it reads
is lineage-kinds.json beside it. Standard library only.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_FILE = os.path.join(HERE, "lineage-kinds.json")

WITHDRAWN = "<withdrawn>"
NOT_LIVE = re.compile(r" — (?:Superseded by|Withdrawn)\b")
HEADING = re.compile(r"^(#{1,6})\s")
_KINDS = None


def kinds():
    global _KINDS
    if _KINDS is None:
        with open(KINDS_FILE, encoding="utf-8") as fh:
            _KINDS = json.load(fh)["kinds"]
    return _KINDS


def kind_of(path, text=None):
    """The kind-table row name for a document, by its basename; None for a kind the table lacks."""
    base = os.path.basename(path)
    for name, row in kinds().items():
        if any(re.search(p, base) for p in row["match"]):
            return name
    return None


def _strip_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def _norm(lines):
    return " ".join(" ".join(lines).split())


def items(kind, text):
    """Item key -> normalised live content. A not-live item maps to WITHDRAWN and its nested items
    are omitted. Text outside every item is keyed per '## ' section as '§<heading>' ('§header'
    before the first)."""
    row = kinds()[kind]
    starts = [(it["level"], re.compile(it["start"])) for it in row["items"]]
    notes = [re.compile(p) for p in row["notes"]]
    ignore = [re.compile(p) for p in row["ignore_lines"]]
    buckets = {}
    order = []
    stack = []  # [(level, id)]
    section = "§header"
    current = section
    dead_level = None  # inside a not-live item at this level
    notes_level = None  # inside a notes section opened by a heading of this depth

    def put(key, line):
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        if line is not None:
            buckets[key].append(line)

    for line in _strip_frontmatter(text).split("\n"):
        h = HEADING.match(line)
        depth = len(h.group(1)) if h else None
        if notes_level is not None:
            if depth is not None and depth <= notes_level:
                notes_level = None
            else:
                continue
        if depth is not None and any(n.search(line) for n in notes):
            notes_level = depth
            continue
        matched = None
        for level, rx in starts:
            m = rx.search(line)
            if m:
                matched = (level, m.group(1))
                break
        if matched:
            level, ident = matched
            if dead_level is not None and level > dead_level:
                continue
            dead_level = None
            stack = [s for s in stack if s[0] < level] + [(level, ident)]
            current = "/".join(f"[{s[1]}]" for s in stack)
            if NOT_LIVE.search(line):
                buckets[current] = WITHDRAWN
                order.append(current)
                dead_level = level
                continue
            put(current, line)
            continue
        if depth is not None and depth <= 2:
            stack = []
            dead_level = None
            section = "§" + line[depth:].strip()
            current = section
            put(current, None)
            continue
        if dead_level is not None:
            continue
        if any(i.search(line) for i in ignore):
            continue
        put(current, line)
    out = {}
    for key in order:
        val = buckets[key]
        out[key] = val if val == WITHDRAWN else _norm(val)
    return {k: v for k, v in out.items() if v != ""}


def compare(kind, old_text, new_text):
    """Which live items were added, changed or withdrawn between two copies of a document."""
    old, new = items(kind, old_text), items(kind, new_text)
    added, changed, withdrawn = [], [], []
    for key, val in new.items():
        if key not in old:
            if val != WITHDRAWN:
                added.append(key)
        elif val != old[key]:
            (withdrawn if val == WITHDRAWN else changed).append(key)
    for key, val in old.items():
        if key in new or val == WITHDRAWN:
            continue
        parts = key.split("/")
        if any(new.get("/".join(parts[:i])) == WITHDRAWN for i in range(1, len(parts))):
            continue  # nested under an item withdrawn in the new copy: reported once, at its parent
        withdrawn.append(key)
    return {"added": sorted(added), "changed": sorted(changed), "withdrawn": sorted(withdrawn)}


def version_of(kind, text):
    """The document's Version where its kind carries one, else None."""
    if kinds()[kind]["version"] != "header":
        return None
    m = re.search(r"^- \*\*Version\*\*:\s*(\S+)", _strip_frontmatter(text), re.M)
    return m.group(1) if m else None


# --------------------------------------------------------------------------- selftest

SPEC = """---
kind: specification
key: PRD-1
---
# Specification

- **Feature name**: Checkout
- **Version**: 3
- **Created**: 2026-01-01
- **Author**: someone
- **Published**: no
- **Open questions**: 0

## Problem statement

Buyers abandon carts.

## User stories

### [U01]: Pay by card

As a buyer, I want to pay by card, so that I can finish.

#### [AC01]: Card accepted

When the buyer submits a valid card, the system shall record the payment.

##### Test cases

**[TC01]: Valid card — Happy path:** Preconditions: a cart. Steps: 1. pay. Expected result: recorded.

---

### [U02]: Pay by invoice

As a business buyer, I want an invoice, so that I can pay later.

#### [AC01]: Invoice issued

When the buyer chooses invoice, the system shall issue an invoice.
"""

PRD = """---
kind: prd
key: PRD-1
---
# PRD

## User Stories

### [US#1]: Pay by card

As a buyer, I want to pay by card, so that I can finish.

### [US#2]: Pay by invoice

As a business buyer, I want an invoice, so that I can pay later.

## Acceptance Criteria

**For [US#2] — Pay by invoice**

- [AC#4] An invoice is issued within one minute.
"""


def _check(name, cond, detail=""):
    if not cond:
        raise AssertionError(f"{name} failed {detail}")


def selftest():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for t in tests:
        t()
    print(f"selftest: {len(tests)} passed")
    return 0


def test_spec_items_keyed_by_path():
    keys = set(items("specification", SPEC))
    for k in ("[U01]", "[U01]/[AC01]", "[U01]/[AC01]/[TC01]", "[U02]", "[U02]/[AC01]"):
        _check("test_spec_items_keyed_by_path", k in keys, f"missing {k} in {sorted(keys)}")


def test_notes_only_not_moved():
    new = SPEC.replace("- **Open questions**: 0", "- **Open questions**: 1")
    new = new.replace(
        "When the buyer submits a valid card, the system shall record the payment.\n",
        "When the buyer submits a valid card, the system shall record the payment.\n\n"
        "##### Open questions\n\n- [ ] Which card brands?\n"
        "- [x] Engineering proposal (/design): accept the two main brands.\n",
    )
    new += "\n## Engineering review\n\n- The invoice flow needs a tax rule.\n"
    r = compare("specification", SPEC, new)
    _check("test_notes_only_not_moved", r == {"added": [], "changed": [], "withdrawn": []}, str(r))


def test_ac_text_change():
    new = SPEC.replace("shall record the payment.", "shall record the payment and email a receipt.")
    r = compare("specification", SPEC, new)
    _check("test_ac_text_change", r["changed"] == ["[U01]/[AC01]"] and not r["added"] and not r["withdrawn"], str(r))


def test_marker_reports_once():
    new = SPEC.replace("### [U02]: Pay by invoice", "### [U02]: Pay by invoice — Withdrawn 2026-11-03: gone")
    r = compare("specification", SPEC, new)
    _check("test_marker_reports_once", r == {"added": [], "changed": [], "withdrawn": ["[U02]"]}, str(r))


def test_prd_items():
    keys = set(items("prd", PRD))
    for k in ("[US#1]", "[US#2]", "[AC#4]"):
        _check("test_prd_items", k in keys, f"missing {k} in {sorted(keys)}")
    new = PRD.replace("within one minute", "within two minutes")
    r = compare("prd", PRD, new)
    _check("test_prd_items", r["changed"] == ["[AC#4]"], str(r))


def test_no_id_kind():
    old = "---\nkind: epic\n---\n# Epic\n\n## Goal\n\nShip it.\n"
    new = old.replace("Ship it.", "Ship it soon.")
    r = compare("epic", old, new)
    _check("test_no_id_kind", r["changed"] != [] and not r["added"], str(r))
    ws = old.replace("Ship it.", "Ship   it.\n")
    r2 = compare("epic", old, ws)
    _check("test_no_id_kind whitespace", r2 == {"added": [], "changed": [], "withdrawn": []}, str(r2))


def test_version_of():
    _check("test_version_of spec", version_of("specification", SPEC) == "3")
    _check("test_version_of prd", version_of("prd", PRD) is None)


def test_kind_of():
    _check("kind spec", kind_of("specifications/PRD-1-x/specification.md") == "specification")
    _check("kind ard", kind_of("specifications/PRD-1-x/ard-server.md") == "ard")
    _check("kind ard plain", kind_of("specifications/PRD-1-x/ard.md") == "ard")
    _check("kind unknown", kind_of("specifications/PRD-1-x/notes.md") is None)


def main(argv):
    if argv[1:2] == ["--selftest"]:
        return selftest()
    print("usage: lineage.py --selftest | <subcommand> ...", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))

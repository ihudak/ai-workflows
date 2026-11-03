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
    text = text.replace("\r\n", "\n")
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
    return _items(kind, text)[0]


def _key_col(line):
    return len(line) - len(line.lstrip(" -"))


def _items(kind, text):
    """items() and, for a kind whose row carries item_altitude, item key -> its altitude ('' for a
    live item carrying none). The field is read only at the column of the item's own id key, so a
    block-scalar line inside another field is never taken for it."""
    row = kinds()[kind]
    alt_rx = re.compile(row["item_altitude"]) if row.get("item_altitude") else None
    alts = {}
    key_col = None
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
            if alt_rx is not None:
                alts[current] = ""
                key_col = _key_col(line)
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
        if current in alts and _key_col(line) == key_col:
            m = alt_rx.search(line)
            if m:
                alts[current] = m.group(1)
        if any(i.search(line) for i in ignore):
            continue
        put(current, line)
    out = {}
    for key in order:
        val = buckets[key]
        out[key] = val if val == WITHDRAWN else _norm(val)
    return {k: v for k, v in out.items() if v != ""}, alts


def compare(kind, old_text, new_text, altitude=None):
    """Which live items were added, changed or withdrawn between two copies of a document. With an
    altitude (the downstream's), an item whose every live copy carries another altitude is left
    out; an item carrying none, and text outside every item, always count."""
    (old, old_alt), (new, new_alt) = _items(kind, old_text), _items(kind, new_text)
    if altitude is not None:
        def other(key):
            seen = {a[key] for a in (old_alt, new_alt) if key in a}
            return bool(seen) and "" not in seen and altitude not in seen
        old = {k: v for k, v in old.items() if not other(k)}
        new = {k: v for k, v in new.items() if not other(k)}
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


# --------------------------------------------------------------------------- git

class LineageError(Exception):
    pass


def _git(specs, *args, data=None):
    import subprocess
    r = subprocess.run(["git", "-C", specs, *args], input=data, capture_output=True)
    return r.returncode, r.stdout


def _blob_at(specs, ref, path):
    rc, out = _git(specs, "rev-parse", "--verify", "-q", f"{ref}:{path}")
    return out.decode().strip() if rc == 0 else None


def _cat_blob(specs, blob):
    rc, out = _git(specs, "cat-file", "-p", blob)
    return out.decode("utf-8", "replace") if rc == 0 else None


def _hash_bytes(specs, data):
    rc, out = _git(specs, "hash-object", "--stdin", data=data)
    if rc != 0:
        raise LineageError("git hash-object failed")
    return out.decode().strip()


# --------------------------------------------------------------------------- the record

_ENTRY = re.compile(r"^\s*(?:-\s+)?(path|blob|version):\s*(.*?)\s*$")
_TOP = re.compile(r"^(upstreams|accepted):\s*(\[\s*\])?\s*(?:#.*)?$")
_COMMENT = re.compile(r"\s+#.*$")


def _eol_of(text):
    """The line ending the text's first line ends with: CRLF where it does, else LF."""
    i = text.find("\n")
    return "\r\n" if i > 0 and text[i - 1] == "\r" else "\n"


def _split_frontmatter(text):
    """(frontmatter lines or None, body, eol). The lines exclude the two '---' fences and carry no
    line ending; eol is the one the opening fence ends with, and the body is kept byte for byte. A
    closing fence with nothing after it -- not even a line ending -- still closes the frontmatter."""
    eol = _eol_of(text)
    if text.startswith("---" + eol):
        start = 3 + len(eol)
        end = text.find(eol + "---" + eol, start - len(eol))
        if end != -1:
            return text[start:end].split(eol) if end >= start else [], text[end + 2 * len(eol) + 3:], eol
        if text.endswith(eol + "---") and len(text) >= start + 3:
            end = len(text) - 3 - len(eol)
            return text[start:end].split(eol) if end >= start else [], "", eol
    return None, text, eol


def _blocks(fm):
    """{'upstreams': [...], 'accepted': [...]} parsed from frontmatter lines, the other lines, the set
    of the two keys present -- an empty flow list (`upstreams: []`, `[ ]`, with or without a trailing
    comment) is a key present with no entries -- and the index in the other lines where the first of
    them stood. A comment line inside a block, and a trailing comment on a value, are skipped: the
    script writes these blocks, and the next write drops them."""
    found = {"upstreams": [], "accepted": []}
    other = []
    seen = set()
    at = None
    current = None
    for line in fm:
        top = _TOP.match(line)
        if top:
            seen.add(top.group(1))
            if at is None:
                at = len(other)
            current = None if top.group(2) else top.group(1)
            continue
        if current and (line.startswith(" ") or line.startswith("-")) and line.strip():
            if line.strip().startswith("#"):
                continue
            m = _ENTRY.match(line)
            if not m:
                raise LineageError(f"unreadable {current} line: {line!r}")
            if line.lstrip().startswith("-"):
                found[current].append({})
            if not found[current]:
                raise LineageError(f"{current} entry without '-': {line!r}")
            val = m.group(2)
            if not val.startswith('"'):
                val = _COMMENT.sub("", val)
            if m.group(1) == "version":
                val = None if val in ("null", "~", "") else json.loads(val) if val.startswith('"') else val
            found[current][-1][m.group(1)] = val
            continue
        current = None
        other.append(line)
    return found, other, seen, at


def read_record(text):
    fm, _, _ = _split_frontmatter(text)
    if fm is None:
        return {"upstreams": [], "accepted": []}, False
    found, _, seen, _ = _blocks(fm)
    return found, "upstreams" in seen


def _render(name, entries, with_version, keep_empty=False):
    """The block's lines; an empty list renders `name: []` where keep_empty, else nothing."""
    if not entries:
        return [f"{name}: []"] if keep_empty else []
    out = [f"{name}:"]
    for e in entries:
        out.append(f"  - path: {e['path']}")
        out.append(f"    blob: {e['blob']}")
        if with_version:
            v = e.get("version")
            out.append(f"    version: {json.dumps(v) if v is not None else 'null'}")
    return out


def _read(doc):
    with open(doc, encoding="utf-8", newline="") as fh:
        return fh.read()


def _write(doc, text):
    with open(doc, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _write_record(doc, upstreams=None, accepted=None):
    """Rewrite only the upstreams:/accepted: blocks of doc's frontmatter, where the first of them
    stood (at its end where neither did), in the frontmatter's own line ending; every other line and
    the body are kept byte for byte. None keeps a block as is."""
    text = _read(doc)
    fm, body, eol = _split_frontmatter(text)
    if fm is None:
        fm, body = [], text
    found, other, seen, at = _blocks(fm)
    ups = found["upstreams"] if upstreams is None else upstreams
    acc = found["accepted"] if accepted is None else accepted
    # an upstreams: key is a record, even an empty one: written where given or already present
    keep_ups = upstreams is not None or "upstreams" in seen
    block = _render("upstreams", ups, True, keep_ups) + _render("accepted", acc, False)
    if at is None:
        while other and other[-1] == "":
            other.pop()
        at = len(other)
    lines = other[:at] + block + other[at:]
    _write(doc, "---" + eol + eol.join(lines) + eol + "---" + eol + body)


# --------------------------------------------------------------------------- subcommands

def capture(specs, ref, from_ref, from_disk):
    """Each input's path, blob id of the bytes read, and Version: from_ref read at ref, from_disk as
    the working tree holds it."""
    out = []
    for path in from_ref:
        blob = _blob_at(specs, ref, path)
        if blob is None:
            raise LineageError(f"{path} is not on {ref}")
        text = _cat_blob(specs, blob) or ""
        out.append({"path": path, "blob": blob, "version": _version_any(path, text)})
    for path in from_disk:
        full = os.path.join(specs, path)
        try:
            with open(full, "rb") as fh:
                data = fh.read()
        except OSError as exc:
            raise LineageError(f"cannot read {path}: {exc}")
        out.append({"path": path, "blob": _hash_bytes(specs, data),
                    "version": _version_any(path, data.decode("utf-8", "replace"))})
    return out


def _version_any(path, text):
    kind = kind_of(path)
    return version_of(kind, text) if kind else None


def stamp(specs, ref, doc, captured):
    """Write upstreams: from a capture; carry forward each accepted entry still current at ref."""
    found, _ = read_record(_read(doc))
    carried, dropped = [], []
    for e in found["accepted"]:
        (carried if _blob_at(specs, ref, e["path"]) == e["blob"] else dropped).append(e)
    _write_record(doc, upstreams=[{"path": c["path"], "blob": c["blob"], "version": c.get("version")} for c in captured],
                  accepted=carried)
    return {"stamped": doc, "carried": carried, "dropped": dropped}


def check(specs, ref, docs, output=None, accepted_from=()):
    """Walk from docs (paths relative to specs) up recorded upstreams through covered kinds. A link
    counts as accepted where output, or any document in accepted_from, records it accepted."""
    accepted = []
    for src in ([output] if output else []) + list(accepted_from):
        if os.path.exists(src):
            accepted += _accepted_of(src)
    acc = {(a["path"], a["blob"]) for a in accepted}
    res = {"stale": [], "missing": [], "absent": [], "accepted": [], "highest": None, "top_missing": None}
    best = {"stale": None, "missing": None}  # each (depth, document)
    seen = set()

    def note_highest(depth, downstream, which="stale"):
        if best[which] is None or depth > best[which][0]:
            best[which] = (depth, downstream)

    def walk(doc, depth):
        if doc in seen:
            return
        seen.add(doc)
        kind = kind_of(doc)
        if kind is None or not kinds()[kind]["covered"]:
            return
        blob = _blob_at(specs, ref, doc)
        if blob is None:
            res["absent"].append({"downstream": None, "upstream": doc})
            return
        found, has = read_record(_cat_blob(specs, blob) or "")
        if not has:
            if (doc, blob) in acc:
                res["accepted"].append({"missing": doc, "blob": blob})
            else:
                res["missing"].append({"doc": doc, "blob": blob})
                note_highest(depth, doc, "missing")
            return
        for e in found["upstreams"]:
            up = e["path"]
            cur = _blob_at(specs, ref, up)
            if cur is None:
                res["absent"].append({"downstream": doc, "upstream": up})
                continue
            if cur != e["blob"]:
                link = _link(specs, doc, e, up, cur, kinds()[kind].get("altitude"))
                if link is not None:
                    if (up, cur) in acc:
                        res["accepted"].append({"downstream": doc, "upstream": up, "blob": cur})
                    else:
                        res["stale"].append(link)
                        note_highest(depth, doc)
            walk(up, depth + 1)

    for d in docs:
        walk(d, 0)
    if best["stale"] is not None:
        d = best["stale"][1]
        res["highest"] = {"downstream": d, "reviser": kinds()[kind_of(d)]["reviser"]}
    if best["missing"] is not None:
        d = best["missing"][1]
        res["top_missing"] = {"doc": d, "reviser": kinds()[kind_of(d)]["reviser"]}
    return res


def _link(specs, doc, entry, up, cur, altitude=None):
    kind = kind_of(up)
    cur_text = _cat_blob(specs, cur) or ""
    old_text = _cat_blob(specs, entry["blob"])
    link = {"downstream": doc, "upstream": up,
            "recorded": {"blob": entry["blob"], "version": entry.get("version")},
            "current": {"blob": cur, "version": _version_any(up, cur_text)},
            "added": [], "changed": [], "withdrawn": [], "unavailable": old_text is None}
    if old_text is None:
        return link
    diff = compare(kind, old_text, cur_text, altitude) if kind else _compare_plain(old_text, cur_text)
    if not any(diff.values()):
        return None
    link.update(diff)
    return link


def _compare_plain(old, new):
    same = " ".join(_strip_frontmatter(old).split()) == " ".join(_strip_frontmatter(new).split())
    return {"added": [], "changed": [] if same else ["§file"], "withdrawn": []}


_IMPL_BLOCK = re.compile(r"^## \d{4}-\d{2}-\d{2} \u2014 /implement\b", re.M)


def _is_impl(path):
    return os.path.basename(path) == "implementation.md"


def _impl_accepted(text):
    """Every accepted entry recorded inside implementation.md's blocks: an entry's `accepted:` field
    and the `- path:` / `blob:` lines indented under it."""
    out, indent = [], None
    for line in text.splitlines():
        m = re.match(r"^(\s+)accepted:\s*$", line)
        if m:
            indent = len(m.group(1))
            continue
        if indent is None:
            continue
        if not line.strip() or len(line) - len(line.lstrip(" ")) <= indent:
            indent = None
            continue
        e = _ENTRY.match(line)
        if not e or e.group(1) == "version":
            raise LineageError(f"unreadable accepted line: {line!r}")
        if line.lstrip().startswith("-"):
            out.append({})
        if not out:
            raise LineageError(f"accepted entry without '-': {line!r}")
        out[-1][e.group(1)] = e.group(2)
    return out


def _accepted_of(path):
    """The accepted entries a document records: its frontmatter's, or implementation.md's blocks'."""
    text = _read(path)
    return _impl_accepted(text) if _is_impl(path) else read_record(text)[0]["accepted"]


def _accept_into_block(doc, checked):
    """implementation.md: the run's own block -- the last one, written just before -- gains an
    `accepted:` field listing each stale link and missing record this run went on past. Links an
    earlier run accepted stay in that run's block, which check reads too."""
    text = _read(doc)
    if not _IMPL_BLOCK.search(text):
        raise LineageError(f"{doc} holds no /implement block to record the acceptance in")
    new = [(s["upstream"], s["current"]["blob"]) for s in checked.get("stale", [])]
    new += [(m["doc"], m["blob"]) for m in checked.get("missing", [])]
    added, seen = [], set()
    for path, blob in new:
        if (path, blob) not in seen:
            seen.add((path, blob))
            added.append({"path": path, "blob": blob})
    if added:
        lines = ["  accepted:"] + [l for a in added for l in (f"    - path: {a['path']}", f"      blob: {a['blob']}")]
        i = text.rstrip("\r\n").rfind("\n")  # the line ending of the file's last line decides
        eol = "\r\n" if i > 0 and text[i - 1] == "\r" else "\n"
        _write(doc, text.rstrip("\r\n") + eol + eol.join(lines) + eol)
    return {"accepted": doc, "added": added}


def accept(doc, checked):
    """Append accepted entries for each stale link (its upstream at its current blob), each missing
    record (that document at its blob) and each link the check found already accepted, de-duplicated.
    implementation.md records them in its last block instead (_accept_into_block)."""
    if _is_impl(doc):
        return _accept_into_block(doc, checked)
    found, _ = read_record(_read(doc))
    entries = list(found["accepted"])
    keys = {(e["path"], e["blob"]) for e in entries}
    new = [(s["upstream"], s["current"]["blob"]) for s in checked.get("stale", [])]
    new += [(m["doc"], m["blob"]) for m in checked.get("missing", [])]
    # links an earlier run accepted, which the check suppressed: kept across a rewrite of the document
    new += [(a.get("upstream") or a.get("missing"), a["blob"]) for a in checked.get("accepted", [])]
    added = []
    for path, blob in new:
        if (path, blob) not in keys:
            keys.add((path, blob))
            entries.append({"path": path, "blob": blob})
            added.append({"path": path, "blob": blob})
    _write_record(doc, accepted=entries)
    return {"accepted": doc, "added": added}


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
upstreams: []
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


class _Repo:
    """A throwaway specs repository: a PRD folder with prd.md, specification.md and design.md."""

    def __init__(self, tmp):
        import subprocess
        self.root = tmp
        self.sp = subprocess
        self.run("init", "-q", "-b", "main")
        self.run("config", "user.email", "t@example.invalid")
        self.run("config", "user.name", "t")
        self.dir = "specifications/PRD-1-checkout"
        os.makedirs(os.path.join(tmp, self.dir))
        self.prd = f"{self.dir}/prd.md"
        self.spec = f"{self.dir}/specification.md"
        self.design = f"{self.dir}/design.md"

    def run(self, *args):
        r = self.sp.run(["git", "-C", self.root, *args], capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError(f"git {args} failed: {r.stderr}")
        return r.stdout.strip()

    def write(self, rel, text):
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as fh:
            fh.write(text)

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as fh:
            return fh.read()

    def commit(self, msg="c"):
        self.run("add", "-A")
        self.run("commit", "-q", "-m", msg)

    def chain(self):
        """prd -> spec -> design, each downstream stamped against its upstream at main; the PRD
        carries an empty record (no idea under the specs repository), as PRD does."""
        self.write(self.prd, PRD)
        self.commit()
        self.write(self.spec, SPEC)
        stamp(self.root, "main", os.path.join(self.root, self.spec), capture(self.root, "main", [self.prd], []))
        self.commit()
        self.write(self.design, "---\nkind: design\nkey: PRD-1\n---\n# Design\n\n- **Version**: 1\n\n## Approach\n\nCards via the gateway.\n")
        stamp(self.root, "main", os.path.join(self.root, self.design), capture(self.root, "main", [self.spec], []))
        self.commit()


def _with_repo(fn):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        fn(_Repo(tmp))


def test_capture_ref_and_disk():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        r.write(f"{r.dir}/code-grounding.md", "- id: [CG#1]\n  claim: x\n")
        got = capture(r.root, "main", [r.prd], [f"{r.dir}/code-grounding.md"])
        _check("capture ref blob", got[0]["blob"] == r.run("rev-parse", f"main:{r.prd}"), str(got))
        disk = r.run("hash-object", os.path.join(r.root, r.dir, "code-grounding.md"))
        _check("capture disk blob", got[1]["blob"] == disk, str(got))
        _check("capture version", got[0]["version"] is None)
    _with_repo(body)


def test_capture_several_paths_per_flag():
    """document-lineage §5 step 1's form: several paths after one flag, and either flag repeated."""
    import subprocess

    def body(r):
        for name in ("a.md", "b.md", "c.md", "d.md"):
            r.write(name, f"# {name}\n")
        r.commit()
        out = os.path.join(r.root, "capture.json")
        p = subprocess.run([sys.executable, os.path.abspath(__file__), "capture", "--specs", r.root, "--ref", "main",
                            "--from-disk", "a.md", "b.md", "--from-disk", "c.md", "--from-ref", "d.md",
                            "--out", out], capture_output=True, text=True)
        _check("capture several paths exit", p.returncode == 0, p.stderr.strip())
        with open(out, encoding="utf-8") as fh:
            paths = sorted(e["path"] for e in json.load(fh))
        _check("capture several paths recorded once each", paths == ["a.md", "b.md", "c.md", "d.md"], str(paths))
    _with_repo(body)


def test_walk_full_chain():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        res = check(r.root, "main", [r.design])
        _check("walk stale count", len(res["stale"]) == 1, json.dumps(res))
        link = res["stale"][0]
        _check("walk link", link["downstream"] == r.spec and link["upstream"] == r.prd and link["changed"] == ["[AC#4]"], json.dumps(link))
        _check("walk highest", res["highest"] == {"downstream": r.spec, "reviser": "/product-workflows:update-spec <KEY>"}, json.dumps(res["highest"]))
    _with_repo(body)


def test_notes_commit_not_stale():
    def body(r):
        r.chain()
        r.write(r.spec, r.read(r.spec) + "\n## Engineering review\n\n- A tax rule is needed.\n")
        r.commit()
        res = check(r.root, "main", [r.design])
        _check("notes not stale", res["stale"] == [] and res["missing"] == [], json.dumps(res))
    _with_repo(body)


def test_missing_record():
    def body(r):
        r.write(r.prd, PRD)
        r.write(r.spec, SPEC)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("missing listed", [m["doc"] for m in res["missing"]] == [r.spec], json.dumps(res))
        _check("missing top", res["top_missing"]["doc"] == r.spec and res["highest"] is None, json.dumps(res))
        r.write(f"{r.dir}/idea.md", "# Idea\n\n## Problem\n\nCarts.\n")
        r.commit()
        res2 = check(r.root, "main", [f"{r.dir}/idea.md"])
        _check("uncovered top never missing", res2["missing"] == [] and res2["top_missing"] is None, json.dumps(res2))
    _with_repo(body)


def test_accept_suppresses_then_reasks():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        out = os.path.join(r.root, r.design)
        accept(out, check(r.root, "main", [r.design]))
        res = check(r.root, "main", [r.design], output=out)
        _check("accepted suppressed", res["stale"] == [] and len(res["accepted"]) == 1, json.dumps(res))
        r.write(r.prd, PRD.replace("within one minute", "within three minutes"))
        r.commit()
        res = check(r.root, "main", [r.design], output=out)
        _check("moved again asks", len(res["stale"]) == 1, json.dumps(res))
    _with_repo(body)


def test_blob_unavailable():
    def body(r):
        r.chain()
        text = r.read(r.spec)
        bogus = "0123456789abcdef0123456789abcdef01234567"
        r.write(r.spec, re.sub(r"blob: [0-9a-f]{40}", f"blob: {bogus}", text))
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("unavailable", len(res["stale"]) == 1 and res["stale"][0]["unavailable"] is True, json.dumps(res))
    _with_repo(body)


def test_stamp_preserves_unknown_keys():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        original = "---\nkind: specification\nkey: PRD-1\nteam_field: keep me  # exactly\n---\n" + SPEC.split("---\n", 2)[2]
        r.write(r.spec, original)
        doc = os.path.join(r.root, r.spec)
        stamp(r.root, "main", doc, capture(r.root, "main", [r.prd], []))
        after = r.read(r.spec)
        _check("unknown key kept", "team_field: keep me  # exactly\n" in after)
        _check("body kept", after.split("\n---\n", 1)[1] == original.split("\n---\n", 1)[1])
        accept(doc, {"stale": [], "missing": [{"doc": r.prd, "blob": "a" * 40}]})
        stamp(r.root, "main", doc, capture(r.root, "main", [r.prd], []))
        again = r.read(r.spec)
        _check("restamp idempotent on other bytes", again.count("upstreams:") == 1 and "team_field: keep me  # exactly\n" in again, again)
    _with_repo(body)


def test_upstream_absent():
    def body(r):
        r.chain()
        r.run("rm", "-q", r.prd)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("absent not stale", res["stale"] == [] and res["absent"] == [{"downstream": r.spec, "upstream": r.prd}], json.dumps(res))
    _with_repo(body)


def test_stamp_carry_forward():
    def body(r):
        r.chain()
        doc = os.path.join(r.root, r.spec)
        cur = r.run("rev-parse", f"main:{r.prd}")
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": cur}}], "missing": [{"doc": r.design, "blob": "b" * 40}]})
        res = stamp(r.root, "main", doc, capture(r.root, "main", [r.prd], []))
        _check("carried", res["carried"] == [{"path": r.prd, "blob": cur}], json.dumps(res))
        _check("dropped", res["dropped"] == [{"path": r.design, "blob": "b" * 40}], json.dumps(res))
    _with_repo(body)


def _load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def test_consumed_by_not_moved():
    old = "- id: [CG#1]\n  claim: x\n  verdict: CONFIRMED\n  consumed_by: none\n"
    new = old.replace("consumed_by: none", "consumed_by: [specification]")
    r = compare("grounding", old, new)
    _check("test_consumed_by_not_moved", r == {"added": [], "changed": [], "withdrawn": []}, str(r))
    r2 = compare("decisions", old.replace("CG#1", "VD#1"), new.replace("CG#1", "VD#1"))
    _check("test_consumed_by_not_moved decisions", r2 == {"added": [], "changed": [], "withdrawn": []}, str(r2))


def test_engineering_review_notes_all_kinds():
    for kind in ("epic", "prd", "ard", "design"):
        old = "---\nkind: x\n---\n# T\n\n## Goal\n\nShip it.\n"
        new = old + "\n## Engineering review\n\n- [ ] A conformance gap.\n"
        r = compare(kind, old, new)
        _check(f"test_engineering_review_notes_all_kinds {kind}", r == {"added": [], "changed": [], "withdrawn": []}, str(r))


def test_missing_only_has_no_stale_highest():
    def body(r):
        r.write(r.prd, PRD)
        r.write(r.spec, SPEC)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("missing-only highest", res["highest"] is None, json.dumps(res))
        _check("missing-only top_missing", res["top_missing"] == {"doc": r.spec, "reviser": "/product-workflows:update-spec <KEY>"}, json.dumps(res))
    _with_repo(body)


def test_accepted_survive_rewrite():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        out = os.path.join(r.root, r.design)
        accept(out, check(r.root, "main", [r.design]))
        first = check(r.root, "main", [r.design], output=out)
        # the consumer rewrites its output from scratch, losing the accepted: block, then stamps and accepts
        r.write(r.design, "---\nkind: design\nkey: PRD-1\n---\n# Design\n\n- **Version**: 2\n\n## Approach\n\nCards.\n")
        stamp(r.root, "main", out, capture(r.root, "main", [r.spec], []))
        accept(out, first)
        again = check(r.root, "main", [r.design], output=out)
        _check("accepted survive rewrite", again["stale"] == [] and len(again["accepted"]) == 1, json.dumps(again))
    _with_repo(body)




def test_empty_capture_writes_empty_list():
    def body(r):
        r.write(r.spec, SPEC)
        doc = os.path.join(r.root, r.spec)
        stamp(r.root, "main", doc, [])
        text = r.read(r.spec)
        _check("empty list written", "\nupstreams: []\n" in text, text)
        _check("empty list is a record", read_record(text)[1] is True)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("empty record not missing", res["missing"] == [] and res["stale"] == [], json.dumps(res))
    _with_repo(body)


def test_flow_empty_list_replaced():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        r.write(r.spec, "---\nkind: specification\nupstreams: []\nkey: PRD-1\n---\n# S\n")
        doc = os.path.join(r.root, r.spec)
        stamp(r.root, "main", doc, capture(r.root, "main", [r.prd], []))
        text = r.read(r.spec)
        _check("one upstreams key", text.count("upstreams:") == 1 and f"path: {r.prd}" in text, text)
        _check("other keys kept", "kind: specification\n" in text and "key: PRD-1\n" in text, text)
    _with_repo(body)


IMPL = ("# Implementation — PRD-1 checkout\n\n## 2026-01-01 — /implement\n- repo:    orders\n"
        "  commit:  a3f91c2\n  pushed:  true\n\n## 2026-01-02 — /implement\n- repo:    billing\n"
        "  commit:  7be0d41\n  pushed:  false            # local only\n")


def test_accept_into_implementation_block():
    def body(r):
        rel = f"{r.dir}/implementation.md"
        r.write(rel, IMPL)
        doc = os.path.join(r.root, rel)
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}], "missing": [],
                     "accepted": [{"upstream": r.spec, "blob": "d" * 40}]})
        text = r.read(rel)
        _check("no frontmatter", not text.startswith("---"), text)
        _check("earlier blocks unchanged", text.startswith(IMPL), text)
        _check("last block gains accepted", text[len(IMPL):] == f"  accepted:\n    - path: {r.prd}\n      blob: {'c' * 40}\n", text)
    _with_repo(body)


def test_implementation_acceptances_read():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        rel = f"{r.dir}/implementation.md"
        r.write(rel, IMPL)
        doc = os.path.join(r.root, rel)
        accept(doc, check(r.root, "main", [r.design]))
        r.write(rel, r.read(rel) + "\n## 2026-01-03 — /implement\n- repo:    orders\n  commit:  1111111\n  pushed:  true\n")
        res = check(r.root, "main", [r.design], output=doc)
        _check("block acceptance honoured", res["stale"] == [] and len(res["accepted"]) == 1, json.dumps(res))
    _with_repo(body)


def test_accept_implementation_without_block_fails():
    def body(r):
        rel = f"{r.dir}/implementation.md"
        r.write(rel, "# Implementation — PRD-1 checkout\n")
        try:
            accept(os.path.join(r.root, rel), {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}]})
        except LineageError:
            return
        raise AssertionError("accept into an implementation.md with no block must fail")
    _with_repo(body)


def test_accept_adds_no_upstreams_key():
    def body(r):
        rel = f"{r.dir}/_conformance.md"
        r.write(rel, "---\nkind: conformance-record\nkey: PRD-1\n---\n# C\n")
        doc = os.path.join(r.root, rel)
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}], "missing": []})
        text = r.read(rel)
        _check("keys kept", "kind: conformance-record\nkey: PRD-1\n" in text, text)
        _check("no upstreams key", "upstreams" not in text, text)
    _with_repo(body)


def test_prd_covered_missing():
    def body(r):
        r.write(r.prd, "# PRD\n\n## User Stories\n\n### [US#1]: Pay\n\nAs a buyer, I pay.\n")
        r.commit()
        r.write(r.spec, SPEC)
        stamp(r.root, "main", os.path.join(r.root, r.spec), capture(r.root, "main", [r.prd], []))
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("prd missing", [m["doc"] for m in res["missing"]] == [r.prd], json.dumps(res))
        _check("prd reviser", res["top_missing"]["reviser"].startswith("/product-workflows:update-prd"), json.dumps(res))
    _with_repo(body)


def test_accepted_from_union():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        design = os.path.join(r.root, r.design)
        accept(design, check(r.root, "main", [r.design]))
        other = os.path.join(r.root, r.dir, "other.md")
        r.write(f"{r.dir}/other.md", "---\nkind: design\n---\n# O\n")
        res = check(r.root, "main", [r.spec], accepted_from=[design])
        _check("accepted via union", res["stale"] == [] and len(res["accepted"]) == 1, json.dumps(res))
        res2 = check(r.root, "main", [r.spec], accepted_from=[other])
        _check("other doc does not accept", len(res2["stale"]) == 1, json.dumps(res2))
    _with_repo(body)


def test_flow_empty_spaced_and_commented():
    for form in ("upstreams: [ ]", "upstreams: []  # no idea in the specs repository"):
        _check(f"empty form read: {form}", read_record(f"---\nkind: prd\n{form}\n---\n# P\n")[1] is True)
    def body(r):
        r.write(r.prd, "---\nkind: prd\nupstreams: [ ]\nkey: PRD-1\n---\n# P\n")
        stamp(r.root, "main", os.path.join(r.root, r.prd), [])
        text = r.read(r.prd)
        _check("spaced empty list replaced once", text.count("upstreams:") == 1, text)
    _with_repo(body)


def test_comment_inside_block_tolerated():
    blob = "a" * 40
    text = (f"---\nkind: specification\nupstreams:\n  # read by /specify\n  - path: p/prd.md\n"
            f"    blob: {blob}  # the PRD\n    version: null\n---\n# S\n")
    found, has = read_record(text)
    _check("comment skipped", has and found["upstreams"] == [{"path": "p/prd.md", "blob": blob, "version": None}], str(found))


def test_closing_fence_without_newline():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        r.write(r.spec, "---\nkind: specification\nkey: PRD-1\n---")
        stamp(r.root, "main", os.path.join(r.root, r.spec), capture(r.root, "main", [r.prd], []))
        text = r.read(r.spec)
        _check("one frontmatter", text.count("kind: specification") == 1 and text.count("---") == 2, text)
    _with_repo(body)


def test_blocks_keep_position():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        r.write(r.spec, "---\nkind: specification\nupstreams: []\nkey: PRD-1\n---\n# S\n")
        stamp(r.root, "main", os.path.join(r.root, r.spec), capture(r.root, "main", [r.prd], []))
        text = r.read(r.spec)
        _check("upstreams stays before key", text.index("upstreams:") < text.index("key: PRD-1"), text)
    _with_repo(body)


def test_crlf_record_read_and_kept():
    def body(r):
        r.write(r.prd, PRD)
        r.commit()
        crlf = SPEC.replace("\n", "\r\n")
        with open(os.path.join(r.root, r.spec), "w", encoding="utf-8", newline="") as fh:
            fh.write(crlf)
        doc = os.path.join(r.root, r.spec)
        stamp(r.root, "main", doc, capture(r.root, "main", [r.prd], []))
        with open(doc, encoding="utf-8", newline="") as fh:
            text = fh.read()
        _check("no bare LF written", "\n" not in text.replace("\r\n", ""), repr(text[:200]))
        _check("body bytes kept", text.endswith(crlf.split("\r\n---\r\n", 1)[1]), repr(text[-200:]))
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("CRLF record is a record", res["missing"] == [] and res["stale"] == [], json.dumps(res))
    _with_repo(body)


def test_accept_impl_crlf():
    def body(r):
        rel = f"{r.dir}/implementation.md"
        crlf = IMPL.replace("\n", "\r\n")
        with open(os.path.join(r.root, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(crlf)
        doc = os.path.join(r.root, rel)
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}], "missing": []})
        with open(doc, encoding="utf-8", newline="") as fh:
            text = fh.read()
        _check("CRLF kept in the appended field", text.startswith(crlf) and "\n" not in text.replace("\r\n", ""), repr(text[-160:]))
        _check("CRLF field read back", _accepted_of(doc) == [{"path": r.prd, "blob": "c" * 40}], str(_accepted_of(doc)))
    _with_repo(body)


REGISTER = """# Decision register: PRD-1

id: [VD#1]
statement: Buyers pay by card.
options_considered: [card, invoice]
chosen: card
argumentation: |
  The BRD asks for card payment.
evidence: [[CG#1]]
altitude: product
status: decided
consumed_by: none
round: 1

id: [VD#2]
statement: Cards go through the gateway.
options_considered: [gateway, direct]
chosen: gateway
argumentation: |
  altitude: product would be wrong here; this is the ARD's.
evidence: []
altitude: architecture
status: decided
consumed_by: none
round: 1

id: [VD#3]
statement: Receipts are emailed.
options_considered: ["yes", "no"]
chosen: "yes"
argumentation: |
  Written before altitude existed.
evidence: []
status: decided
consumed_by: none
round: 1
"""

GROUNDING = """# Code grounding: PRD-1

- id: [CG#1]
  claim: [BR#1] — the gateway accepts cards
  verdict: CONFIRMED
  evidence:
    - pay/gateway.py:10
  commit: 4f1c9ab0d2e7c35a91b8f6e04c2d7a5b9e13f860
  altitude: implementation
  horizon: current
  consumed_by: none
  outcome: agree
"""

INVENTORY = """---
kind: brd
key: PRD-2
quoted:
  - "[BR#1]"
---

# Inventory: PRD-2

| id | text | source_anchor | defects |
|---|---|---|---|
| [BR#1] | The monthly report lists every invoice. | 2. Monthly report | [DEF#1] |
| [BR#2] | Every monthly report must include the invoice number. | 2. Monthly report | |
"""


def test_altitude_filter_per_downstream():
    vd1 = REGISTER.replace("Buyers pay by card.", "Buyers pay by card or wallet.")
    vd2 = REGISTER.replace("Cards go through the gateway.", "Cards go direct.")
    vd3 = REGISTER.replace("Receipts are emailed.", "Receipts are printed.")
    _check("product ignores architecture", compare("decisions", REGISTER, vd2, "product")["changed"] == [], str(compare("decisions", REGISTER, vd2, "product")))
    _check("architecture sees architecture", compare("decisions", REGISTER, vd2, "architecture")["changed"] == ["[VD#2]"])
    _check("architecture ignores product", compare("decisions", REGISTER, vd1, "architecture")["changed"] == [])
    _check("no altitude counts", compare("decisions", REGISTER, vd3, "product")["changed"] == ["[VD#3]"])
    _check("unfiltered sees all", compare("decisions", REGISTER, vd2)["changed"] == ["[VD#2]"])
    moved = REGISTER.replace("altitude: architecture", "altitude: product")
    _check("moved into product counts", compare("decisions", REGISTER, moved, "product")["changed"] == ["[VD#2]"])
    _check("moved out of architecture counts", compare("decisions", REGISTER, moved, "architecture")["changed"] == ["[VD#2]"])

    def body(r):
        reg = f"{r.dir}/decisions.md"
        r.write(reg, REGISTER)
        stamp(r.root, "main", os.path.join(r.root, reg), [])
        r.commit()
        r.write(r.prd, PRD)
        stamp(r.root, "main", os.path.join(r.root, r.prd), capture(r.root, "main", [reg], []))
        r.commit()
        r.write(reg, r.read(reg).replace("Cards go through the gateway.", "Cards go direct."))
        r.commit()
        res = check(r.root, "main", [r.prd])
        _check("prd not stale on architecture", res["stale"] == [] and res["missing"] == [], json.dumps(res))
        r.write(reg, r.read(reg).replace("Buyers pay by card.", "Buyers pay by card or wallet."))
        r.commit()
        res = check(r.root, "main", [r.prd])
        _check("prd stale on product", [(s["downstream"], s["changed"]) for s in res["stale"]] == [(r.prd, ["[VD#1]"])], json.dumps(res))
        _check("prd reviser", res["highest"]["reviser"].startswith("/product-workflows:update-prd"), json.dumps(res))
    _with_repo(body)


def test_register_link_unfiltered():
    def body(r):
        gr = f"{r.dir}/grounding/code-grounding.md"
        reg = f"{r.dir}/decisions.md"
        os.makedirs(os.path.join(r.root, r.dir, "grounding"))
        r.write(gr, GROUNDING)
        stamp(r.root, "main", os.path.join(r.root, gr), [])
        r.commit()
        r.write(reg, REGISTER)
        stamp(r.root, "main", os.path.join(r.root, reg), capture(r.root, "main", [gr], []))
        r.commit()
        r.write(r.prd, PRD)
        stamp(r.root, "main", os.path.join(r.root, r.prd), capture(r.root, "main", [reg], []))
        r.commit()
        r.write(gr, r.read(gr).replace("the gateway accepts cards", "the gateway accepts cards and wallets"))
        r.commit()
        res = check(r.root, "main", [r.prd])
        _check("register stale on an implementation finding",
               [(s["downstream"], s["upstream"], s["changed"]) for s in res["stale"]] == [(reg, gr, ["[CG#1]"])], json.dumps(res))
        _check("register reviser", res["highest"] == {"downstream": reg, "reviser": "/product-workflows:brd-interview <KEY>"}, json.dumps(res))
    _with_repo(body)


def test_inventory_rows():
    _check("inventory kind", kind_of("specifications/PRD-2-x/brd/brd-inventory.md") == "inventory")
    _check("inventory uncovered", kinds()["inventory"]["covered"] is False)
    new = INVENTORY.replace("must include the invoice number.", "must include the invoice number and date.")
    r = compare("inventory", INVENTORY, new)
    _check("inventory row changed", r == {"added": [], "changed": ["[BR#2]"], "withdrawn": []}, str(r))
    fm = INVENTORY.replace('  - "[BR#1]"\n', '  - "[BR#1]"\n  - "[BR#2]"\n')
    _check("inventory frontmatter not a move", compare("inventory", INVENTORY, fm) == {"added": [], "changed": [], "withdrawn": []})


def test_stamp_register_without_frontmatter():
    def body(r):
        gr = f"{r.dir}/code-grounding.md"
        reg = f"{r.dir}/decisions.md"
        r.write(gr, GROUNDING)
        r.commit()
        r.write(reg, REGISTER)
        stamp(r.root, "main", os.path.join(r.root, reg), capture(r.root, "main", [gr], []))
        text = r.read(reg)
        _check("register frontmatter created", text.startswith("---\nupstreams:\n"), text[:80])
        fm, body_text, _eol = _split_frontmatter(text)
        _check("register body byte-identical", body_text == REGISTER, repr(body_text[:80]))
        _check("register record read", read_record(text)[1] is True and read_record(text)[0]["upstreams"][0]["path"] == gr)
        _check("register items unchanged", items("decisions", text) == items("decisions", REGISTER))
        _check("grounding kind covered", kinds()["grounding"]["covered"] is True and kinds()["decisions"]["covered"] is True)
        _check("grounding reviser", kinds()["grounding"]["reviser"] == "/product-workflows:prd-ground <KEY>")
    _with_repo(body)


def main(argv):
    import argparse
    if argv[1:2] == ["--selftest"]:
        return selftest()
    p = argparse.ArgumentParser(prog="lineage.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--specs", required=True)
    c.add_argument("--ref", required=True)
    c.add_argument("--from-ref", action="extend", nargs="+", default=[])
    c.add_argument("--from-disk", action="extend", nargs="+", default=[])
    c.add_argument("--out", required=True)
    s = sub.add_parser("stamp")
    s.add_argument("--specs", required=True)
    s.add_argument("--ref", required=True)
    s.add_argument("--doc", required=True)
    s.add_argument("--capture", required=True)
    k = sub.add_parser("check")
    k.add_argument("--specs", required=True)
    k.add_argument("--ref", required=True)
    k.add_argument("--output")
    k.add_argument("--accepted-from", action="append", default=[])
    k.add_argument("--out")
    k.add_argument("docs", nargs="+")
    a = sub.add_parser("accept")
    a.add_argument("--doc", required=True)
    a.add_argument("--check", required=True)
    args = p.parse_args(argv[1:])
    try:
        if args.cmd == "capture":
            result = capture(args.specs, args.ref, args.from_ref, args.from_disk)
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(result, fh, indent=2)
        elif args.cmd == "stamp":
            result = stamp(args.specs, args.ref, args.doc, _load_json(args.capture))
        elif args.cmd == "check":
            result = check(args.specs, args.ref, args.docs, output=args.output,
                           accepted_from=args.accepted_from)
            if args.out:
                with open(args.out, "w", encoding="utf-8") as fh:
                    json.dump(result, fh, indent=2)
        else:
            result = accept(args.doc, _load_json(args.check))
    except (LineageError, OSError, ValueError, KeyError) as exc:
        print(f"lineage.py {args.cmd}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

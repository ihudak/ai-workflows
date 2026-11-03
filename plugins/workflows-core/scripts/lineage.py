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


def _split_frontmatter(text):
    """(frontmatter lines or None, body). Frontmatter lines exclude the two '---' fences."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 3)
        if end != -1:
            return text[4:end].split("\n"), text[end + 5:]
    return None, text


def _blocks(fm):
    """{'upstreams': [...], 'accepted': [...]} parsed from frontmatter lines, the other lines, and the
    set of the two keys present — an empty flow list (`upstreams: []`) is a key present with no entries."""
    found = {"upstreams": [], "accepted": []}
    other = []
    seen = set()
    current = None
    for line in fm:
        top = re.match(r"^(upstreams|accepted):\s*(\[\])?\s*$", line)
        if top:
            seen.add(top.group(1))
            current = None if top.group(2) else top.group(1)
            continue
        if current and (line.startswith(" ") or line.startswith("-")) and line.strip():
            m = _ENTRY.match(line)
            if not m:
                raise LineageError(f"unreadable {current} line: {line!r}")
            if line.lstrip().startswith("-"):
                found[current].append({})
            if not found[current]:
                raise LineageError(f"{current} entry without '-': {line!r}")
            val = m.group(2)
            if m.group(1) == "version":
                val = None if val in ("null", "~", "") else json.loads(val) if val.startswith('"') else val
            found[current][-1][m.group(1)] = val
            continue
        current = None
        other.append(line)
    return found, other, seen


def read_record(text):
    fm, _ = _split_frontmatter(text)
    if fm is None:
        return {"upstreams": [], "accepted": []}, False
    found, _, seen = _blocks(fm)
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


def _write_record(doc, upstreams=None, accepted=None):
    """Rewrite only the upstreams:/accepted: blocks of doc's frontmatter; None keeps a block as is."""
    with open(doc, encoding="utf-8") as fh:
        text = fh.read()
    fm, body = _split_frontmatter(text)
    if fm is None:
        fm, body = [], text
    found, other, seen = _blocks(fm)
    ups = found["upstreams"] if upstreams is None else upstreams
    acc = found["accepted"] if accepted is None else accepted
    # an upstreams: key is a record, even an empty one: written where given or already present
    keep_ups = upstreams is not None or "upstreams" in seen
    while other and other[-1] == "":
        other.pop()
    lines = other + _render("upstreams", ups, True, keep_ups) + _render("accepted", acc, False)
    with open(doc, "w", encoding="utf-8") as fh:
        fh.write("---\n" + "\n".join(lines) + "\n---\n" + body)


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
    with open(doc, encoding="utf-8") as fh:
        found, _ = read_record(fh.read())
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
            with open(src, encoding="utf-8") as fh:
                accepted += read_record(fh.read())[0]["accepted"]
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
                link = _link(specs, doc, e, up, cur)
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


def _link(specs, doc, entry, up, cur):
    kind = kind_of(up)
    cur_text = _cat_blob(specs, cur) or ""
    old_text = _cat_blob(specs, entry["blob"])
    link = {"downstream": doc, "upstream": up,
            "recorded": {"blob": entry["blob"], "version": entry.get("version")},
            "current": {"blob": cur, "version": _version_any(up, cur_text)},
            "added": [], "changed": [], "withdrawn": [], "unavailable": old_text is None}
    if old_text is None:
        return link
    diff = compare(kind, old_text, cur_text) if kind else _compare_plain(old_text, cur_text)
    if not any(diff.values()):
        return None
    link.update(diff)
    return link


def _compare_plain(old, new):
    same = " ".join(_strip_frontmatter(old).split()) == " ".join(_strip_frontmatter(new).split())
    return {"added": [], "changed": [] if same else ["§file"], "withdrawn": []}


def accept(doc, checked):
    """Append accepted entries for each stale link (its upstream at its current blob), each missing
    record (that document at its blob) and each link the check found already accepted, de-duplicated."""
    with open(doc, encoding="utf-8") as fh:
        found, _ = read_record(fh.read())
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


def test_accept_creates_frontmatter():
    def body(r):
        rel = f"{r.dir}/implementation.md"
        original = "# Implementation — X\n\n## 2026-01-01 — /implement\n- repo:    orders\n"
        r.write(rel, original)
        doc = os.path.join(r.root, rel)
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}], "missing": []})
        text = r.read(rel)
        _check("frontmatter created", text.startswith("---\naccepted:\n"), text)
        _check("body unchanged", text.split("\n---\n", 1)[1] == original, text)
        _check("no upstreams invented", "upstreams" not in text, text)
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


def main(argv):
    import argparse
    if argv[1:2] == ["--selftest"]:
        return selftest()
    p = argparse.ArgumentParser(prog="lineage.py", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("capture")
    c.add_argument("--specs", required=True)
    c.add_argument("--ref", required=True)
    c.add_argument("--from-ref", action="append", default=[])
    c.add_argument("--from-disk", action="append", default=[])
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

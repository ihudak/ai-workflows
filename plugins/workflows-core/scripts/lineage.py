#!/usr/bin/env python3
"""Document lineage: record which upstream bytes a document was built from, and tell whether they moved.

The authority for what this script does is workflows-core:document-lineage; the kind table it reads
is lineage-kinds.json beside it. Standard library only.

stamp takes --capture once or more, and records the entries of every capture file, in the order given:
an entry repeated exactly is recorded once, and one path at two blobs is refused.
"""

import json
import os
import posixpath
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
    before the first), save a section the kind row drops; an ignored field's lines are left out."""
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
    sec_alt = row.get("section_altitude") or {}
    drop = [re.compile(p) for p in row.get("drop_sections") or []]
    fields = row.get("ignore_fields") or []
    field_rx = re.compile(r"^\s*(?:-\s+)?(?:%s):" % "|".join(map(re.escape, fields))) if fields else None
    skipping = False  # inside an ignored field: its continuation lines run past the key column
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
        if key is None:  # a dropped section's own text
            return
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
            key_col = _key_col(line)
            skipping = False
            if alt_rx is not None:
                alts[current] = ""
            continue
        if depth is not None and depth <= 2:
            stack = []
            dead_level = None
            skipping = False
            name = line[depth:].strip()
            section = None if any(d.search(name) for d in drop) else "§" + name
            current = section
            put(current, None)
            if section is not None and name in sec_alt:
                alts[section] = sec_alt[name]
            continue
        if dead_level is not None:
            continue
        in_item = current is not None and current.startswith("[")
        if skipping:
            if not line.strip() or _key_col(line) > key_col:
                continue
            skipping = False
        if in_item and field_rx is not None and _key_col(line) == key_col and field_rx.search(line):
            skipping = True
            continue
        if in_item and current in alts and _key_col(line) == key_col:
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


def compare(kind, old_text, new_text, altitude=None, skip=frozenset()):
    """Which live items were added, changed or withdrawn between two copies of a document. With an
    altitude (the downstream's), an item — or a section the kind row gives an altitude — whose
    every live copy carries another altitude is left out; an item carrying none, and text outside
    every item in a section with none, always count. An item whose key is in skip is left out."""
    (old, old_alt), (new, new_alt) = _items(kind, old_text), _items(kind, new_text)
    if skip:
        old = {k: v for k, v in old.items() if k.split("/")[0] not in skip}
        new = {k: v for k, v in new.items() if k.split("/")[0] not in skip}
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
    rc, out = _git(specs, "rev-parse", "--verify", "-q", f"{ref}:./{path}")  # ./: from $SPECS_PATH, not the top level
    return out.decode().strip() if rc == 0 else None


_BLOB = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")  # a blob id: SHA-1's 40 lowercase hex, or SHA-256's 64


def _path_in_class(path):
    """document-lineage §1: a recorded path is in its class where each component, split at `/`, is in addressing §2's
    class of a folder's name -- not empty, no `..`, first `_` or a letter or digit of any script, then letters, digits,
    combining marks or `. _ @ + -` -- its bytes read as UTF-8. A path outside it is never read."""
    import unicodedata
    if not isinstance(path, str):
        return False
    try:
        text = os.fsencode(path).decode("utf-8")
    except UnicodeError:
        return False

    def ok(n):
        return (n != "" and ".." not in n and (n[0] == "_" or n[0].isalnum())
                and all(c.isalnum() or c in "._@+-" or unicodedata.category(c).startswith("M") for c in n))
    return all(ok(c) for c in text.split("/"))


def _cat_blob(specs, blob):
    """The blob's text, or None where the clone lacks it -- or where blob is not a blob id (_BLOB): a record's blob is
    committed data, so a value that is not one -- an option, a revision expression such as `main:<path>` -- is never
    handed to git, which would read another object as the recorded copy (document-lineage §2 step 5)."""
    if not isinstance(blob, str) or not _BLOB.match(blob):
        return None
    rc, out = _git(specs, "cat-file", "-p", blob)
    return out.decode("utf-8", "replace") if rc == 0 else None


def _hash_bytes(specs, data, path=None):
    """The blob id of data: hashed with path (relative to specs) where one is given -- that path's clean filter and
    line-ending conversion applied, with no index read -- else of the bytes as they are."""
    rc, out = _git(specs, "hash-object", "--stdin", *(["--path", path] if path else []), data=data)
    if rc != 0:
        raise LineageError("git hash-object failed")
    return out.decode().strip()


class _Adder:
    """`git add -- <path>` run into a scratch index -- a copy of the repository's own, its mtime kept -- and a scratch
    object directory, the repository's object directory an alternate of it, so the repository is left as it was.
    blob(path) is then the blob a commit of the working-tree file would store, by git's own rules: the path's clean
    filter and line-ending conversion, the check that leaves a CRLF copy as it is where the index's blob already
    holds a CR, and a symlink stored as its link text. None where git cannot add the path -- no repository, or a
    path outside its work tree or beyond a symbolic link."""

    def __init__(self, specs):
        self.specs = specs
        self.tmp = None
        self.env = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.tmp is not None:
            self.tmp.cleanup()

    def _setup(self):
        import shutil
        import tempfile
        paths = []
        for name in ("index", "objects"):
            rc, out = _git(self.specs, "rev-parse", "--git-path", name)
            if rc != 0:
                return False
            paths.append(os.path.join(self.specs, out.decode().strip()))
        index, objects = paths
        self.tmp = tempfile.TemporaryDirectory(prefix="lineage-capture-")
        scratch_index = os.path.join(self.tmp.name, "index")
        if os.path.exists(index):
            shutil.copy2(index, scratch_index)
        os.mkdir(os.path.join(self.tmp.name, "objects"))
        alternates = [objects] + [a for a in os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES", "").split(os.pathsep) if a]
        self.env = dict(os.environ, GIT_INDEX_FILE=scratch_index, GIT_OBJECT_DIRECTORY=os.path.join(self.tmp.name, "objects"),
                        GIT_ALTERNATE_OBJECT_DIRECTORIES=os.pathsep.join(alternates))
        return True

    def blob(self, path):
        import subprocess
        if self.env is None and not self._setup():
            return None
        base = ["git", "-C", self.specs, "--literal-pathspecs", "-c", "core.safecrlf=false", "-c", "core.splitIndex=false",
                "-c", "core.fsmonitor=false"]
        if subprocess.run(base + ["add", "-f", "--", path], env=self.env, capture_output=True).returncode != 0:
            return None
        r = subprocess.run(base + ["ls-files", "-s", "-z", "--", path], env=self.env, capture_output=True)
        entries = [rec.split(b"\t", 1)[0].split() for rec in r.stdout.split(b"\0") if rec]
        staged = [e[1].decode() for e in entries if len(e) == 3 and e[2] == b"0"]
        return staged[0] if r.returncode == 0 and len(staged) == 1 else None


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
    """Each input's path, blob id, and Version: from_ref read at ref; from_disk as the working tree holds it, its blob
    the one `git add` would store for it (_Adder), or, where git cannot add the path, its bytes hashed with the path."""
    out = []
    for path in from_ref:
        blob = _blob_at(specs, ref, path)
        if blob is None:
            raise LineageError(f"{path} is not on {ref}")
        text = _cat_blob(specs, blob) or ""
        out.append({"path": path, "blob": blob, "version": _version_any(path, text)})
    with _Adder(specs) as adder:
        for path in from_disk:
            data = _read_input(specs, path)
            blob = adder.blob(path) or _hash_bytes(specs, data, path)
            if _read_input(specs, path) != data:
                raise LineageError(f"{path} changed while it was captured; capture it again")
            out.append({"path": path, "blob": blob, "version": _version_any(path, data.decode("utf-8", "replace"))})
    return out


def _read_input(specs, path):
    try:
        with open(os.path.join(specs, path), "rb") as fh:
            return fh.read()
    except OSError as exc:
        raise LineageError(f"cannot read {path}: {exc}")


def _version_any(path, text):
    kind = kind_of(path)
    return version_of(kind, text) if kind else None


def stamp(specs, ref, doc, captured):
    """Write upstreams: from a capture; carry forward each accepted entry still current at ref."""
    found, _ = read_record(_read(doc))
    carried, dropped = [], []
    for e in found["accepted"]:  # a path outside its class is dropped unread (document-lineage §1)
        (carried if _path_in_class(e["path"]) and _blob_at(specs, ref, e["path"]) == e["blob"] else dropped).append(e)
    _write_record(doc, upstreams=[{"path": c["path"], "blob": c["blob"], "version": c.get("version")} for c in captured],
                  accepted=carried)
    return {"stamped": doc, "carried": carried, "dropped": dropped}


def check(specs, ref, docs, output=None, accepted_from=()):
    """Walk from docs (paths relative to specs) up recorded upstreams through covered kinds. A link
    counts as accepted where output, or any document in accepted_from, records it accepted — read
    from disk, or at ref where it is not on disk. A ref that does not resolve is an error. walked lists
    every document the walk reached: each of docs, and each upstream a record it read names, wherever
    the ref holds that upstream."""
    if _git(specs, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}")[0] != 0:
        raise LineageError(f"no {ref} in {specs} to read the documents at")
    accepted = []
    for src in ([output] if output else []) + list(accepted_from):
        if os.path.exists(src):
            accepted += _accepted_of(src)
            continue
        rel = os.path.relpath(src, specs).replace(os.sep, "/")
        blob = None if rel.startswith("../") else _blob_at(specs, ref, rel)
        text = _cat_blob(specs, blob) if blob else None
        if text is not None:
            accepted += _accepted_of_text(rel, text)
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
        for n, e in enumerate(found["upstreams"], 1):
            up = e["path"]
            if not _path_in_class(up):  # never read, walked or printed: not checkable, by its place (§6 step 3)
                res["stale"].append({"downstream": doc, "upstream": None, "entry": n, "unchecked": "path",
                                     "recorded": {"blob": e.get("blob"), "version": e.get("version")}, "current": None,
                                     "added": [], "changed": [], "withdrawn": [], "unavailable": True})
                note_highest(depth, doc)
                continue
            cur = _blob_at(specs, ref, up)
            if cur is None:
                res["absent"].append({"downstream": doc, "upstream": up})
                continue
            if cur != e["blob"]:
                link = _link(specs, doc, e, up, cur, kinds()[kind].get("altitude"), _skip_set(specs, ref, up))
                if link is not None:
                    if (up, cur) in acc:
                        res["accepted"].append({"downstream": doc, "upstream": up, "blob": cur})
                    else:
                        res["stale"].append(link)
                        note_highest(depth, doc)
            walk(up, depth + 1)

    for d in docs:
        walk(d, 0)
    res["walked"] = sorted(seen)
    if best["stale"] is not None:
        d = best["stale"][1]
        res["highest"] = {"downstream": d, "reviser": kinds()[kind_of(d)]["reviser"]}
    if best["missing"] is not None:
        d = best["missing"][1]
        res["top_missing"] = {"doc": d, "reviser": kinds()[kind_of(d)]["reviser"]}
    return res


def _skip_set(specs, ref, up):
    """The item keys an upstream's kind row names in a file beside it (`skip_items_in`) — the
    grounding's baseline findings, by id in grounding/baselines.md — read at ref. A file missing or
    unreadable names none, and a line naming no id adds nothing."""
    kind = kind_of(up)
    spec = kinds()[kind].get("skip_items_in") if kind else None
    if not spec:
        return frozenset()
    blob = _blob_at(specs, ref, posixpath.join(posixpath.dirname(up), spec["file"]))
    text = (_cat_blob(specs, blob) or "") if blob else ""
    rx = re.compile(r"^\s*(?:-\s+)?%s:\s*\[([A-Z]+#\d+)\]" % re.escape(spec["field"]), re.M)
    return frozenset(f"[{m}]" for m in rx.findall(text))


def _link(specs, doc, entry, up, cur, altitude=None, skip=frozenset()):
    kind = kind_of(up)
    cur_text = _cat_blob(specs, cur) or ""
    old_text = _cat_blob(specs, entry["blob"])
    link = {"downstream": doc, "upstream": up,
            "recorded": {"blob": entry["blob"], "version": entry.get("version")},
            "current": {"blob": cur, "version": _version_any(up, cur_text)},
            "added": [], "changed": [], "withdrawn": [], "unavailable": old_text is None}
    if old_text is None:
        return link
    diff = compare(kind, old_text, cur_text, altitude, skip) if kind else _compare_plain(old_text, cur_text)
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
    return _accepted_of_text(path, _read(path))


def _accepted_of_text(path, text):
    return _impl_accepted(text) if _is_impl(path) else read_record(text)[0]["accepted"]


def _accept_into_block(doc, checked):
    """implementation.md: the run's own block -- the last one, written just before -- gains an
    `accepted:` field listing each stale link and missing record this run went on past. Links an
    earlier run accepted stay in that run's block, which check reads too."""
    text = _read(doc)
    if not _IMPL_BLOCK.search(text):
        raise LineageError(f"{doc} holds no /implement block to record the acceptance in")
    new = [(s["upstream"], s["current"]["blob"]) for s in checked.get("stale", []) if s.get("upstream") is not None]
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
    # a link not checkable names no path, and is never accepted (document-lineage §5 step 2)
    new = [(s["upstream"], s["current"]["blob"]) for s in checked.get("stale", []) if s.get("upstream") is not None]
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
    for area in ("ard-платежі.md", "ard-Cart.md", "ard-v2.api.md", "ard-भुगतान.md", "ard-zahlungsauslo\u0308sung.md"):
        _check("kind ard, an area named in the class: " + area, kind_of("specifications/PRD-1-x/" + area) == "ard")
    for name in ("ard-a b.md", "ard-a..b.md", "ard-$(x).md"):
        _check("kind not ard, a name outside the class: " + name, kind_of("specifications/PRD-1-x/" + name) is None)
    for path in ("specifications/BRD-1-x/ard-seed.md", "specifications/BRD-1-x/PRD-1-01-y/ard-seed.md"):
        _check("kind not ard, the seed /product-workflows:brd-intake writes: " + path, kind_of(path) is None)
    _check("kind ard, an area whose name begins with seed", kind_of("specifications/PRD-1-x/ard-seeds.md") == "ard")
    _check("kind unknown", kind_of("specifications/PRD-1-x/notes.md") is None)


def test_seed_is_an_uncovered_top():
    """ard-seed.md is a slice's input and an uncovered top: the walk compares it whole, as it compares
    prd-seed.md, and never looks for a record of its own (workflows-core:document-lineage §4)."""
    def body(r):
        brd = "specifications/BRD-1-intake"
        os.makedirs(os.path.join(r.root, brd, "PRD-1-01-orders"))
        seed, ard = f"{brd}/ard-seed.md", f"{brd}/PRD-1-01-orders/ard.md"
        r.write(seed, "# Architecture seed\n\n## Architecture decisions\n\n### [AD#1]: One queue\n\n**Rule:** one queue.\n")
        r.commit()
        r.write(ard, "---\nkind: ard\nkey: PRD-1-01\n---\n# Orders ARD\n\n## Architecture decisions\n\n"
                     "### [AD#1]: One queue\n\n**Rule:** one queue.\n")
        stamp(r.root, "main", os.path.join(r.root, ard), capture(r.root, "main", [seed], []))
        r.commit()
        res = check(r.root, "main", [ard])
        _check("seed walked", seed in res["walked"], json.dumps(res["walked"]))
        _check("seed: no record asked of it", res["missing"] == [] and res["top_missing"] is None, json.dumps(res))
        r.write(seed, r.read(seed).replace("one queue.", "two queues."))
        r.commit()
        res = check(r.root, "main", [ard])
        _check("seed moved: compared whole", [(s["upstream"], s["changed"]) for s in res["stale"]] == [(seed, ["§file"])],
               json.dumps(res["stale"]))
    _with_repo(body)


class _Repo:
    """A throwaway specs repository: a PRD folder with prd.md, specification.md and design.md."""

    def __init__(self, tmp):
        import subprocess
        self.root = tmp
        self.sp = subprocess
        self.run("init", "-q", "-b", "main")
        self.run("config", "user.email", "t@example.invalid")
        self.run("config", "user.name", "t")
        # No detached auto-maintenance after a commit: its objects/maintenance.lock comes and goes on its own
        # schedule, under the directory the nothing-written checks list (_repo_state).
        self.run("config", "maintenance.auto", "false")
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


def _crlf_copy(r, rel, text):
    with open(os.path.join(r.root, rel), "w", encoding="utf-8", newline="") as fh:
        fh.write(text.replace("\n", "\r\n"))


def _write_bytes(r, rel, data):
    full = os.path.join(r.root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(data)


def _git_add_oracle(root, rel):
    """git's own answer to what a commit of rel's working copy would store: `git add` into a copy of the
    repository's index, then `ls-files -s` -- index and objects of the copy only, nothing read off this script."""
    import shutil
    import subprocess
    import tempfile
    idx = os.path.join(root, subprocess.run(["git", "-C", root, "rev-parse", "--git-path", "index"],
                                            capture_output=True, text=True, check=True).stdout.strip())
    with tempfile.TemporaryDirectory() as tmp:
        copy = os.path.join(tmp, "index")
        if os.path.exists(idx):
            shutil.copy2(idx, copy)
        env = dict(os.environ, GIT_INDEX_FILE=copy)
        subprocess.run(["git", "-C", root, "add", "-f", "--", rel], env=env, capture_output=True, check=True)
        out = subprocess.run(["git", "-C", root, "ls-files", "-s", "--", rel], env=env,
                             capture_output=True, text=True, check=True).stdout.split()
    return out[1]


def _repo_state(root):
    """What a capture must leave as it found it: the index's bytes and every file under the object directory."""
    git_dir = os.path.join(root, ".git")
    objs = sorted(os.path.relpath(os.path.join(d, f), git_dir) for d, _, fs in os.walk(os.path.join(git_dir, "objects")) for f in fs)
    with open(os.path.join(git_dir, "index"), "rb") as fh:
        return fh.read(), objs


_BODY = PRD.encode()
_BODY2 = PRD.replace("within one minute", "within two minutes").encode()
_CR = lambda b: b.replace(b"\n", b"\r\n")
# Each setting: (name, the config it sets after the blob is committed, the .gitattributes committed after it).
_SETTINGS = [
    ("core.autocrlf=true", [("core.autocrlf", "true")], None),
    ("core.autocrlf=input", [("core.autocrlf", "input")], None),
    ("core.autocrlf=false", [("core.autocrlf", "false")], None),
    ("* text=auto", [("core.autocrlf", "false")], "* text=auto\n"),
    ("* text eol=crlf", [("core.autocrlf", "false")], "* text eol=crlf\n"),
    ("* eol=lf", [("core.autocrlf", "false")], "* eol=lf\n"),
    ("*.md text", [("core.autocrlf", "false")], "*.md text\n"),
    ("*.md filter=x, a clean filter", [("core.autocrlf", "false"), ("filter.x.clean", "sed -e s/minute/MINUTE/"),
                                       ("filter.x.smudge", "cat")], "*.md filter=x\n"),
]
# Each working copy: (name, its bytes from the committed blob's, or None to leave the checkout untouched).
_COPIES = [
    ("unchanged", None),
    ("CRLF", lambda blob: _CR(_BODY)),
    ("LF", lambda blob: _BODY),
    ("changed, CRLF", lambda blob: _CR(_BODY2)),
    ("changed, LF", lambda blob: _BODY2),
]


def test_capture_disk_is_what_git_add_stores():
    """document-lineage §5 step 1: a --from-disk input records the blob `git add` would store for it -- the oracle is
    git itself, adding into a copy of the index -- under every line-ending setting and a clean filter, for an LF and a
    CRLF blob, unchanged, converted or changed copies and a path absent from the index; where the copy is the
    default branch's as git compares it, that is the default branch's blob; and the capture writes nothing into the
    repository."""
    for setting, config, attrs in _SETTINGS:
        for blob_name, blob in (("LF blob", _BODY), ("CRLF blob", _CR(_BODY))):
            def body(r, setting=setting, config=config, attrs=attrs, blob_name=blob_name, blob=blob):
                r.run("config", "core.autocrlf", "false")
                rels = [f"{r.dir}/copy-{n}.md" for n in range(len(_COPIES))]
                for rel in rels:
                    _write_bytes(r, rel, blob)
                r.commit()
                for key, val in config:
                    r.run("config", key, val)
                if attrs is not None:
                    r.write(".gitattributes", attrs)
                    r.commit("attributes")
                for rel, (_, make) in zip(rels, _COPIES):
                    if make is not None:
                        _write_bytes(r, rel, make(blob))
                new = f"{r.dir}/new.md"
                _write_bytes(r, new, _CR(_BODY2))
                before = _repo_state(r.root)
                got = {e["path"]: e["blob"] for e in capture(r.root, "main", [], rels + [new])}
                _check(f"{setting}, {blob_name}: nothing written", _repo_state(r.root) == before)
                import subprocess
                for rel, (copy_name, _) in zip(rels + [new], _COPIES + [("absent from the index", None)]):
                    where = f"{setting}, {blob_name}, {copy_name}"
                    want = _git_add_oracle(r.root, rel)
                    _check(f"{where}: what git add stores", got[rel] == want, f"{got[rel]} != {want}")
                    clean = rel != new and subprocess.run(["git", "-C", r.root, "diff", "--quiet", "main", "--", rel], capture_output=True).returncode == 0
                    if clean:
                        _check(f"{where}: the default branch's blob", got[rel] == r.run("rev-parse", f"main:{rel}"), got[rel])
            _with_repo(body)


def test_capture_disk_lands_as_recorded():
    """The record names the blob that lands: a changed CRLF copy of a blob committed with CRLF, under
    core.autocrlf=true, captured, the downstream stamped, then the copy committed as it stood -- the check finds
    the link current, its recorded blob the one the commit stored."""
    def body(r):
        r.run("config", "core.autocrlf", "false")
        _crlf_copy(r, r.prd, PRD)
        r.commit()
        r.run("config", "core.autocrlf", "true")
        _crlf_copy(r, r.prd, PRD.replace("within one minute", "within two minutes"))
        captured = capture(r.root, "main", [], [r.prd])
        r.write(r.spec, SPEC)
        stamp(r.root, "main", os.path.join(r.root, r.spec), captured)
        r.commit("land the copy and the downstream")
        _check("lands: the blob recorded is the blob stored", captured[0]["blob"] == r.run("rev-parse", f"main:{r.prd}"), str(captured))
        res = check(r.root, "main", [r.spec])
        _check("lands: nothing stale", res["stale"] == [], json.dumps(res["stale"]))
    _with_repo(body)


def test_capture_disk_symlink_is_its_link():
    """A symlinked document read from disk records what git stores for the path -- the link text as a blob -- so a
    check finds it current where nothing moved."""
    def body(r):
        target = f"{r.dir}/prd-body.md"
        r.write(target, PRD)
        os.symlink("prd-body.md", os.path.join(r.root, r.prd))
        r.commit()
        captured = capture(r.root, "main", [], [r.prd])
        _check("symlink: the link's blob", captured[0]["blob"] == r.run("rev-parse", f"main:{r.prd}"), str(captured))
        r.write(r.spec, SPEC)
        stamp(r.root, "main", os.path.join(r.root, r.spec), captured)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("symlink: nothing stale", res["stale"] == [], json.dumps(res["stale"]))
    _with_repo(body)


def test_specs_below_the_top_level():
    """A specs tree below its repository's top level: capture --from-ref reads the path from $SPECS_PATH, and a
    check finds the downstream stale when its upstream moves, never absent."""
    def body(r):
        specs = os.path.join(r.root, "specs")
        sub = "specifications/PRD-1-checkout"
        os.makedirs(os.path.join(specs, sub))
        with open(os.path.join(specs, sub, "prd.md"), "w", encoding="utf-8") as fh:
            fh.write(PRD)
        r.commit()
        captured = capture(specs, "main", [f"{sub}/prd.md"], [])
        _check("subdir: --from-ref names the blob", captured[0]["blob"] == r.run("rev-parse", f"main:specs/{sub}/prd.md"), str(captured))
        with open(os.path.join(specs, sub, "specification.md"), "w", encoding="utf-8") as fh:
            fh.write(SPEC)
        stamp(specs, "main", os.path.join(specs, sub, "specification.md"), captured)
        r.commit()
        with open(os.path.join(specs, sub, "prd.md"), "w", encoding="utf-8") as fh:
            fh.write(PRD.replace("within one minute", "within two minutes"))
        r.commit()
        res = check(specs, "main", [f"{sub}/specification.md"])
        _check("subdir: stale, not absent", res["absent"] == [] and [s["upstream"] for s in res["stale"]] == [f"{sub}/prd.md"], json.dumps(res))
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


def test_blob_outside_class_never_read():
    """document-lineage §2 step 5: a recorded blob that is not a blob id -- 40 or 64 lowercase hex -- is never handed
    to git, so a revision expression naming the upstream's current copy, or an option, never reads as that copy: the
    link is reported moved, its recorded copy unavailable."""
    def body(r):
        r.chain()
        text = r.read(r.spec)
        for bogus in (f"main:./{r.prd}", "HEAD", "--batch-all-objects", "0123456789ABCDEF0123456789ABCDEF01234567"):
            r.write(r.spec, re.sub(r"blob: \S+", f"blob: {bogus}", text, count=1))
            r.commit()
            res = check(r.root, "main", [r.spec])
            _check(f"blob {bogus!r} unavailable",
                   len(res["stale"]) == 1 and res["stale"][0]["unavailable"] is True, json.dumps(res))
    _with_repo(body)


def test_path_outside_class_not_checkable():
    """document-lineage §1 and §6 step 3: a recorded path holding a component outside addressing §2's class is never
    read, walked or written back: check reports the link stale, not checkable, by its place in the record and with
    no path; accept writes nothing for it; and stamp drops, unread, an accepted entry whose path is outside it."""
    def body(r):
        r.chain()
        bad = f"{r.dir}/$(touch PWN).md"
        r.write(bad, PRD)  # a file the ref holds at that name: still never read
        text = r.read(r.spec)
        r.write(r.spec, re.sub(r"path: \S+", f"path: {bad}", text, count=1))
        r.commit()
        res = check(r.root, "main", [r.spec])
        s = res["stale"]
        _check("one unchecked link", len(s) == 1 and s[0].get("unchecked") == "path" and s[0]["upstream"] is None
               and s[0]["entry"] == 1 and s[0]["downstream"] == r.spec, json.dumps(res))
        _check("never walked", bad not in res["walked"] and not res["absent"], json.dumps(res))
        _check("highest is the document holding it", res["highest"]["downstream"] == r.spec, json.dumps(res))
        out = accept(os.path.join(r.root, r.design), res)
        _check("accept writes nothing for it", out["added"] == [], json.dumps(out))
        d = r.read(r.design)
        r.write(r.design, d.replace("---\n# Design", f"accepted:\n  - path: {bad}\n    blob: {'0' * 40}\n---\n# Design", 1))
        st = stamp(r.root, "main", os.path.join(r.root, r.design), capture(r.root, "main", [r.spec], []))
        _check("stamp drops it unread", st["carried"] == [] and len(st["dropped"]) == 1, json.dumps(st))
        _check("no PWN", not os.path.exists(os.path.join(r.root, "PWN")))
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
    for kind in ("epic", "prd", "ard", "threat-model", "design"):
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


def test_accept_after_at_field():
    # implementation-format §1: a block's entry carries `at:` after `pushed:`; `accepted:`, which
    # accept appends at the block's end, lands after it, and the reader still finds it there.
    at = "  at:      2026-01-02T10:00:00Z\n"
    def body(r):
        rel = f"{r.dir}/implementation.md"
        r.write(rel, IMPL + at)
        doc = os.path.join(r.root, rel)
        accept(doc, {"stale": [{"upstream": r.prd, "current": {"blob": "c" * 40}}], "missing": [],
                     "accepted": [{"upstream": r.spec, "blob": "d" * 40}]})
        text = r.read(rel)
        _check("earlier text unchanged", text.startswith(IMPL + at), text)
        _check("accepted after at:", text[len(IMPL):] == at + f"  accepted:\n    - path: {r.prd}\n      blob: {'c' * 40}\n", text)
        got = _accepted_of(doc)
        _check("read back past at:", got == [{"path": r.prd, "blob": "c" * 40}], json.dumps(got))
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


SHA = "4f1c9ab0d2e7c35a91b8f6e04c2d7a5b9e13f860"


def _finding(n, claim, altitude="implementation", verdict="CONFIRMED", extra=""):
    return (f"- id: [CG#{n}]\n  claim: {claim}\n  verdict: {verdict}\n  evidence:\n    - pay/gateway.py:10\n"
            f"  commit: {SHA}\n  altitude: {altitude}\n  horizon: current\n  consumed_by: none\n{extra}  outcome: agree\n")


PIN = "baseline integrity: shop-api is pinned at a verified, unmodified commit"
RUN1 = ("# Code grounding: PRD-1\n\n" + _finding(1, PIN) + "\n" + _finding(2, "[BR#1] — the gateway accepts cards")
        + "\n## Derivation matrix\n\n| element | class | source |\n|---|---|---|\n| invoice number | EXISTS | invoices.number |\n"
        + "\n## Documentation divergences\n\n- docs/pay.md says cards only; [CG#2] shows wallets too.\n")


def _rerun(text=RUN1):
    """What a second /prd-ground run with nothing changed left before product-workflows 3.74.0: the old pin SUPERSEDED with its
    note, the claim finding's outcome re-written, a fresh pin appended after the divergences section,
    a second divergences section appended, the matrix replaced in place with the same rows. A run
    since then replaces the divergences section rather than appending another, but a file an older
    run wrote can still hold two, which is the layout this fixture keeps."""
    t = text.replace("verdict: CONFIRMED\n  evidence:\n    - pay/gateway.py:10\n  commit: " + SHA + "\n  altitude: implementation\n  horizon: current\n  consumed_by: none\n  outcome: agree\n\n- id: [CG#2]",
                     "verdict: SUPERSEDED\n  prior_verdict: CONFIRMED\n  evidence:\n    - pay/gateway.py:10\n  commit: " + SHA + "\n  altitude: implementation\n  horizon: current\n  consumed_by: none\n  outcome: agree\n  notes: superseded by [CG#3]\n\n- id: [CG#2]", 1)
    t = t.replace("[BR#1] — the gateway accepts cards\n  verdict: CONFIRMED\n  evidence:\n    - pay/gateway.py:10\n  commit: " + SHA + "\n  altitude: implementation\n  horizon: current\n  consumed_by: none\n  outcome: agree",
                  "[BR#1] — the gateway accepts cards\n  verdict: CONFIRMED\n  evidence:\n    - pay/gateway.py:10\n  commit: " + SHA + "\n  altitude: implementation\n  horizon: current\n  consumed_by: none\n  outcome: extend")
    assert t != text
    return t + "\n" + _finding(3, PIN) + "\n## Documentation divergences\n\n- docs/pay.md says cards only; [CG#2] shows wallets too.\n"


PINS = frozenset({"[CG#1]", "[CG#3]"})


def _empty(d):
    return not any(d.values())


def test_realistic_rerun_layout():
    re2 = _rerun()
    for alt in ("implementation", "architecture", None):
        _check(f"rerun not moved at {alt}", _empty(compare("grounding", RUN1, re2, alt, PINS)), str(compare("grounding", RUN1, re2, alt, PINS)))
    _check("rerun moved without the pin set", compare("grounding", RUN1, re2) == {"added": ["[CG#3]"], "changed": ["[CG#1]"], "withdrawn": []},
           str(compare("grounding", RUN1, re2)))


def test_claim_change_beside_rerun_reported():
    re2 = _rerun().replace("the gateway accepts cards", "the gateway accepts cards and wallets")
    _check("claim change reported", compare("grounding", RUN1, re2, "implementation", PINS) == {"added": [], "changed": ["[CG#2]"], "withdrawn": []},
           str(compare("grounding", RUN1, re2, "implementation", PINS)))


def test_derivation_matrix_altitude():
    m = RUN1.replace("| invoice number | EXISTS | invoices.number |", "| invoice number | DERIVED | invoices.id |")
    _check("matrix at implementation", compare("grounding", RUN1, m, "implementation")["changed"] == ["§Derivation matrix"], str(compare("grounding", RUN1, m, "implementation")))
    _check("matrix unfiltered", compare("grounding", RUN1, m)["changed"] == ["§Derivation matrix"])
    _check("matrix not architecture", _empty(compare("grounding", RUN1, m, "architecture")))


def test_dropped_sections_not_moved():
    d = RUN1.replace("[CG#2] shows wallets too.", "[CG#2] shows wallets and vouchers.") + "\n## Frame sets covered\n\n- design/checkout — covered\n"
    _check("dropped sections not moved", _empty(compare("grounding", RUN1, d)), str(compare("grounding", RUN1, d)))


def test_finding_after_dropped_section_counts():
    a = RUN1 + "\n" + _finding(4, "[BR#2] — refunds go back to the card")
    _check("finding after dropped section", compare("grounding", RUN1, a) == {"added": ["[CG#4]"], "changed": [], "withdrawn": []}, str(compare("grounding", RUN1, a)))


def test_multiline_notes_ignored():
    base = RUN1.replace("  consumed_by: none\n  outcome: agree\n\n## Derivation", "  consumed_by: none\n  notes: |\n    claim: looks like a key\n    second line\n  outcome: agree\n\n## Derivation")
    n2 = base.replace("    claim: looks like a key\n    second line\n", "    claim: another key\n    third line\n    - a list item\n")
    _check("multi-line notes ignored", _empty(compare("grounding", base, n2)), str(compare("grounding", base, n2)))
    o2 = base.replace("  notes: |\n    claim: looks like a key\n    second line\n  outcome: agree\n\n## Derivation", "  notes: |\n    claim: looks like a key\n    second line\n  outcome: agree\n  horizon: will-change\n\n## Derivation")
    _check("a key after notes is read", compare("grounding", base, o2)["changed"] == ["[CG#2]"], str(compare("grounding", base, o2)))


def test_date_heading_not_moved():
    _check("empty date heading", _empty(compare("grounding", RUN1, RUN1 + "\n## 2026-11-04\n")))


def test_legacy_matrix_moves_once():
    legacy = RUN1.replace("\n## Derivation matrix\n\n", "\n").replace("\n## Documentation divergences\n\n- docs/pay.md says cards only; [CG#2] shows wallets too.\n", "")
    now = legacy.replace("\n| element | class | source |", "\n## Derivation matrix\n\n| element | class | source |")
    _check("legacy matrix moves once", compare("grounding", legacy, now, "implementation") == {"added": ["§Derivation matrix"], "changed": ["[CG#2]"], "withdrawn": []},
           str(compare("grounding", legacy, now, "implementation")))
    _check("then settles", _empty(compare("grounding", now, now + "\n", "implementation")))
    _check("legacy matrix not architecture", _empty(compare("grounding", legacy, now, "architecture")), str(compare("grounding", legacy, now, "architecture")))


def test_baseline_set_is_the_record():
    c = RUN1.replace("the gateway accepts cards", "the gateway accepts wallets")
    _check("a listed id is skipped", _empty(compare("grounding", RUN1, c, None, frozenset({"[CG#2]"}))))


def _grounded_repo(r, baselines):
    gdir = f"{r.dir}/grounding"
    os.makedirs(os.path.join(r.root, gdir))
    gr, reg = f"{gdir}/code-grounding.md", f"{r.dir}/decisions.md"
    r.write(gr, RUN1)
    stamp(r.root, "main", os.path.join(r.root, gr), [])
    if baselines:
        r.write(f"{gdir}/baselines.md", f"- date: 2026-11-01\n  repo: shop-api\n  commit: {SHA}\n  integrity: clean\n  finding: [CG#1]\n")
    r.commit()
    r.write(reg, REGISTER)
    stamp(r.root, "main", os.path.join(r.root, reg), capture(r.root, "main", [gr], []))
    r.write(r.spec, SPEC)
    stamp(r.root, "main", os.path.join(r.root, r.spec), capture(r.root, "main", [gr], []))
    r.commit()
    r.write(gr, _rerun(r.read(gr)))
    if baselines:
        r.write(f"{gdir}/baselines.md", r.read(f"{gdir}/baselines.md") + f"- date: 2026-11-02\n  repo: shop-api\n  commit: {SHA}\n  integrity: clean\n  finding: [CG#3]\n")
    r.commit()
    return gr, reg


def test_unchanged_rerun_not_moved():
    def body(r):
        gr, reg = _grounded_repo(r, baselines=True)
        res = check(r.root, "main", [r.spec, reg])
        _check("rerun: nothing stale", res["stale"] == [], json.dumps(res))
    _with_repo(body)


def test_baselines_absent_counts():
    def body(r):
        gr, reg = _grounded_repo(r, baselines=False)
        res = check(r.root, "main", [r.spec, reg])
        _check("no baselines.md: today's behaviour",
               sorted((s["downstream"], tuple(s["added"]), tuple(s["changed"])) for s in res["stale"])
               == sorted([(r.spec, ("[CG#3]",), ("[CG#1]",)), (reg, ("[CG#3]",), ("[CG#1]",))]), json.dumps(res))
    _with_repo(body)


def test_accepted_from_ref_only():
    def body(r):
        r.chain()
        r.write(r.prd, PRD.replace("within one minute", "within two minutes"))
        r.commit()
        design = os.path.join(r.root, r.design)
        accept(design, check(r.root, "main", [r.design]))
        r.commit()
        os.remove(design)
        res = check(r.root, "main", [r.spec], accepted_from=[design])
        _check("acceptance read at the ref", res["stale"] == [] and len(res["accepted"]) == 1, json.dumps(res))
    _with_repo(body)


def test_unresolvable_ref_fails():
    import contextlib
    import io

    def body(r):
        r.chain()
        try:
            check(r.root, "nope", [r.spec])
            _check("unresolvable ref raises", False)
        except LineageError as exc:
            _check("names the ref", "nope" in str(exc), str(exc))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = main(["lineage.py", "check", "--specs", r.root, "--ref", "nope", "--out", os.path.join(r.root, "c.json"), r.spec])
        _check("main exits non-zero", rc not in (0, None) and "nope" in err.getvalue(), f"{rc} {err.getvalue()}")
    _with_repo(body)


def test_run_section_not_moved():
    dg = "# Design grounding: PRD-1\n\n## 2026-10-12 — grounding run\n\nDesign grounding skipped: no `design/` folder.\n"
    re2 = dg + "\n## 2026-11-04 — grounding run\n\nDesign grounding skipped: no `design/` folder in this slice.\n"
    for alt in ("implementation", "architecture", None):
        _check(f"run section not moved at {alt}", _empty(compare("grounding", dg, re2, alt)), str(compare("grounding", dg, re2, alt)))
    f1 = dg + "\n- id: [DG#1]\n  claim: [BR#1] — the checkout frame shows a total\n  verdict: CONFIRMED\n  altitude: implementation\n"
    f2 = f1.replace("shows a total", "shows a total and a tax line")
    _check("finding in a run section counts", compare("grounding", f1, f2)["changed"] == ["[DG#1]"], str(compare("grounding", f1, f2)))


TM = """---
kind: threat-model
key: PRD-1-02
status: reviewed
---
# Checkout — threat model

## Scope

- **Components:** shop:web
- **Contract rows:** none

## Not considered

_None._

## Threats

### [TH#1]: Payment page framed by another site

- **Category:** T
- **Where:** shop:web
- **Threat:** attacker: a third-party site; action: frames the payment page to trick a customer into confirming; asset: the customer's confirmation of the payment
- **CWE:** —
- **Disposition:** Mitigated by ard.md [AD#2]

### [TH#2]: Payment callback replayed

- **Category:** S
- **Where:** shop:web
- **Threat:** attacker: anyone holding an earlier callback; action: sends it again to mark an unpaid order paid; asset: the order's paid state
- **CWE:** —
- **Disposition:** Deferred to design: how the callback handler rejects a callback it has already processed

### [TH#3]: Another customer's receipt read by its id

- **Category:** I
- **Where:** shop:web
- **Threat:** attacker: a signed-in customer; action: requests a receipt id that is not theirs; asset: other customers' receipts
- **CWE:** [CWE-639](https://cwe.mitre.org/data/definitions/639.html)
- **Disposition:** Accepted — the checkout lead; receipt ids are random UUIDs; review by 2027-02-12

## Inherited threats

- [[PRD-1]] [TH#9] Order total forged in the browser — Mitigated by [[PRD-1]] ard.md [AD#2]
"""


def test_threat_model_kind():
    _check("kind threat-model", kind_of("specifications/PRD-1-x/threat-model.md") == "threat-model")
    _check("kind ard-threat-model is an ARD", kind_of("specifications/PRD-1-x/ard-threat-model.md") == "ard")
    keys = {k for k in items("threat-model", TM) if k.startswith("[")}
    _check("threat-model items", keys == {"[TH#1]", "[TH#2]", "[TH#3]"}, str(sorted(keys)))


def test_threat_model_redisposition_is_a_change():
    new = TM.replace("- **Disposition:** Deferred to design: how the callback handler rejects a callback it has already processed",
                     "- **Disposition:** Accepted — the payments lead; the gateway signs each callback; review by 2027-03-01")
    _check("redisposition fixture", new != TM)
    r = compare("threat-model", TM, new)
    _check("test_threat_model_redisposition_is_a_change", r == {"added": [], "changed": ["[TH#2]"], "withdrawn": []}, str(r))


def test_threat_model_records_ard():
    def body(r):
        ard, tm = f"{r.dir}/ard.md", f"{r.dir}/threat-model.md"
        r.write(ard, "---\nkind: ard\nkey: PRD-1\n---\n# ARD\n\n## Architecture decisions\n\n"
                     "### [AD#1]: x\n\n- **Rule:** the gateway signs each callback\n")
        r.commit()
        r.write(tm, TM)
        stamp(r.root, "main", os.path.join(r.root, tm), capture(r.root, "main", [], [ard]))
        r.commit()
        r.write(ard, r.read(ard).replace("signs each callback", "signs and timestamps each callback"))
        r.commit()
        res = check(r.root, "main", [tm])
        _check("threat model stale on its ARD", res["highest"] == {"downstream": tm, "reviser": "/product-workflows:create-ard <KEY>"}, json.dumps(res))
        _check("threat model link", [(s["upstream"], s["changed"]) for s in res["stale"]] == [(ard, ["[AD#1]"])], json.dumps(res["stale"]))
    _with_repo(body)


def test_stamp_two_captures():
    """stamp's --capture repeated: every capture file's entries, in the order given; one flag as before."""
    import subprocess

    def body(r):
        for name in ("a.md", "m.md", "z.md"):
            r.write(name, f"# {name}\n")
        for name in ("one.md", "two.md"):
            r.write(name, "---\nkind: threat-model\n---\n# Doc\n")
        r.commit()
        script = os.path.abspath(__file__)
        first, second = os.path.join(r.root, "first.json"), os.path.join(r.root, "second.json")
        for out, paths in ((first, ["z.md"]), (second, ["a.md", "m.md"])):
            p = subprocess.run([sys.executable, script, "capture", "--specs", r.root, "--ref", "main",
                                "--from-disk", *paths, "--out", out], capture_output=True, text=True)
            _check("two captures: capture exit", p.returncode == 0, p.stderr.strip())

        def stamped(doc, *captures):
            flags = [a for c in captures for a in ("--capture", c)]
            p = subprocess.run([sys.executable, script, "stamp", "--specs", r.root, "--ref", "main",
                                "--doc", os.path.join(r.root, doc), *flags], capture_output=True, text=True)
            _check("two captures: stamp exit", p.returncode == 0, p.stderr.strip())
            return [(e["path"], e["blob"]) for e in read_record(r.read(doc))[0]["upstreams"]]

        want = [(e["path"], e["blob"]) for e in _load_json(first) + _load_json(second)]
        got = stamped("two.md", first, second)
        _check("two captures: both files' entries, in order", got == want and [p for p, _ in got] == ["z.md", "a.md", "m.md"], str(got))
        one = stamped("one.md", first)
        _check("one capture as before", one == [(e["path"], e["blob"]) for e in _load_json(first)], str(one))
    _with_repo(body)


def _cli(*args):
    import subprocess
    return subprocess.run([sys.executable, os.path.abspath(__file__), *args], capture_output=True, text=True)


def _captured(r, out, *paths):
    p = _cli("capture", "--specs", r.root, "--ref", "main", "--from-disk", *paths, "--out", out)
    _check("capture exit", p.returncode == 0, p.stderr.strip())


def test_stamp_capture_two_blobs_refused():
    """One path in two capture files at two blobs is refused, and the document is left as it was."""
    def body(r):
        r.write("a.md", "# a\n")
        r.write("doc.md", "---\nkind: threat-model\n---\n# Doc\n")
        r.commit()
        early, late = os.path.join(r.root, "early.json"), os.path.join(r.root, "late.json")
        _captured(r, early, "a.md")
        r.write("a.md", "# a, edited\n")
        _captured(r, late, "a.md")
        before = r.read("doc.md")
        p = _cli("stamp", "--specs", r.root, "--ref", "main", "--doc", os.path.join(r.root, "doc.md"),
                 "--capture", early, "--capture", late)
        _check("two blobs: exit 1", p.returncode == 1, f"{p.returncode} {p.stderr.strip()}")
        _check("two blobs: the fixed error", p.stderr.startswith("lineage.py stamp: one path in two capture files at two blobs; capture each input once: a.md"), p.stderr.strip())
        _check("two blobs: document untouched", r.read("doc.md") == before)
    _with_repo(body)


def test_stamp_capture_repeat_recorded_once():
    """An entry in two capture files at one blob, or one file passed twice, is recorded once, in first-seen order."""
    def body(r):
        for name in ("a.md", "b.md", "c.md"):
            r.write(name, f"# {name}\n")
        r.write("doc.md", "---\nkind: threat-model\n---\n# Doc\n")
        r.commit()
        ab, bc = os.path.join(r.root, "ab.json"), os.path.join(r.root, "bc.json")
        _captured(r, ab, "a.md", "b.md")
        _captured(r, bc, "b.md", "c.md")
        doc = os.path.join(r.root, "doc.md")
        for flags, want in ((("--capture", ab, "--capture", bc), ["a.md", "b.md", "c.md"]),
                            (("--capture", ab, "--capture", ab), ["a.md", "b.md"])):
            p = _cli("stamp", "--specs", r.root, "--ref", "main", "--doc", doc, *flags)
            _check("repeat: stamp exit", p.returncode == 0, p.stderr.strip())
            got = [e["path"] for e in read_record(r.read("doc.md"))[0]["upstreams"]]
            _check("repeat: recorded once", got == want, str(got))
    _with_repo(body)


def test_check_lists_walked():
    """check's walked: the docs and every upstream a record it read names, wherever the ref holds it --
    never a document beside them that no record names."""
    def body(r):
        r.chain()
        tm = f"{r.dir}/threat-model.md"
        r.write(tm, TM)
        r.commit()
        res = check(r.root, "main", [r.spec])
        _check("walked: the chain", r.spec in res["walked"] and r.prd in res["walked"], json.dumps(res["walked"]))
        _check("walked: no unrecorded neighbour", tm not in res["walked"], json.dumps(res["walked"]))
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
    s.add_argument("--capture", required=True, action="append")
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
            captured, at = [], {}
            for e in (e for c in args.capture for e in _load_json(c)):
                if at.setdefault(e["path"], e["blob"]) != e["blob"]:
                    raise LineageError(f"one path in two capture files at two blobs; capture each input once: {e['path']}")
                if e not in captured:
                    captured.append(e)
            result = stamp(args.specs, args.ref, args.doc, captured)
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

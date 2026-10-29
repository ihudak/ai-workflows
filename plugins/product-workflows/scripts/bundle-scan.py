#!/usr/bin/env python3
"""bundle-scan.py — /brd-package's plugin-free scan (tokens) and citation-resolution check (citations).

  bundle-scan.py tokens <file-or-directory>... [--prereq-key KEY]... [--captured NAME]...
                        [--captured-path PATH]...
  bundle-scan.py citations <bundle-dir> --key KEY [--prereq-key KEY]... [--copied-key KEY]...
                        [--date YYYYMMDD] [--captured NAME]... [--captured-path PATH]...
                        [--source-basename NAME]... [--manifest NAME] [--known-key KEY]...
                        [--prereq-aux NAME]...
  bundle-scan.py sets <bundle-dir> --key KEY --date YYYYMMDD --manifest NAME --note PATH
                        [--unreviewed-prereq KEY]...
  bundle-scan.py --selftest

citations: runs the bundle-packaging reference's section 6 over an assembled bundle. Documents
partition on the key each bundled name begins with, resolved against --key and --prereq-key, never
parsed out; an unkeyed document, and a --copied-key no document answers to, are dead. Each
partition's corpora -- the inventory and the defect log by their tables' id column, the grounding
files, the decision register and the code-defect log by their records' id keys, padding tolerated --
give the ids its references resolve against: relation 1 (every [PREFIX#n] resolves in its own
partition, save another BRD's key before it, a section 6.2 structured field, [SR#n] and a
placeholder), relation 2 (a class-4 [DG#n] cites a [CG#n] whose claim names the same requirement)
and relation 3 (a bare <name>.md carrying a key, or matching a section 1.1 working filename, names a
bundle file). Record-shaped content that parses to no id is unreadable. A hit in the customer's own
words or naming is reported under customer, for the operator's ruling. A key-shaped word before an id
counts as a BRD's key only where it is --key, a --prereq-key or a --known-key; any other is reported
under unknown_key. It reads section 1.1's filenames and section 6.2's fields from the reference beside
it each run, and stops (exit 2) where it cannot. Prints one line of JSON: partitions, the resolved
and discharged counts, dead, mismatch, ambiguous, unqualified, unknown_key, unreadable, customer
with its groups, and prerequisite_external.

tokens: reads every given file, and every .md or .markdown file under every given directory, and
reports each token of a class the plugin's bundle-packaging reference tabulates in section 1.2 -- a
path rooted at the plugin's install directory, a reference-file citation, a section sign, a slash
command, an agent, subagent type or skill name, a bare decision-row id, a model id. It finds tokens;
it never decides whether the package may ship. Each hit carries the span its position places it in,
and the caller rules on the rest:

  captured-file   the file is one of --captured: a customer's own file copied byte for byte
  inventory-text  the text cell of an inventory row (id | text | source_anchor | defects)
  ledger-text     the text cell of a coverage-ledger row (id | text | disposition | defects | evidence)
  anchor          the source_anchor cell of an inventory row
  locator         a --captured-path (a captured file's path relative to brd/) or a --captured name
  locator-tail    what follows a --captured-path's " > " separator (U+203A), segment by segment, up
                  to the end of the line, a delimiting "|", a backtick, ")" or "]" -- save a certain
                  path, citation, command or agent name there, which a customer's heading is taken
                  never to hold, and which is placed as if no tail were there
  none            none of these

and prerequisite: true where the file's name begins with a --prereq-key key and "-". An inventory
or ledger text hit carries image_row: true where the row's source_anchor names an image before its
first separator, false where it names none, and null on a ledger row, which carries no anchor. A
section sign that opens a source_anchor cell, or that opens the first segment after a captured
path's separator, is no hit (bundle-packaging section 6.3 rule 1): each is counted in
omitted_locator_sections and reported nowhere else.

The family's names are read from the plugins installed beside this one -- every sibling directory
holding .claude-plugin/plugin.json, in the source tree (plugins/<name>/) and in the install cache
(<marketplace>/<name>/<version>/) alike: each plugin's name, its commands and its agents. A slash
command is certain where it is namespaced by a family plugin, or by any *workflows* name a later
split adds, or names a hyphenated family command; any other leading-slash name, a one-word family
command such as /ready among them, is uncertain, since its shape cannot tell a command from a route
the customer's own code names. An agent's filename and a
namespaced name are certain; an agent's bare name is uncertain, since some read as ordinary words.
A path rooted at the install directory is the variable's name, any ".claude/plugins/" path, or the
absolute path of the directory the family's plugins sit in. A namespace or a Skill( call that ends
its line is a hit by itself, so a token wrapped onto the next line is still found. Every other class
is certain.

Prints one line of JSON: {"files": N, "omitted_locator_sections": N, "groups": [...]}. Each group is
one file, token, span, prerequisite and image_row, with its class, whether it is certain, its count
and its lines, in the order of its first hit -- the grouping bundle-packaging section 6.3 rule 4
asks of every report. file is the path relative to the directory it was found under, or the file's
own name where a file was given.

Tables split into cells on every delimiting "|" -- one that opens the row or has a space directly
before it -- as the plugin's brd-format reference, section 2.3, fixes; a "|" with no space before it
is inside a cell.

Exit 0: it ran, with hits or without. Exit 2: an argument names no file or directory, or a file
cannot be read as UTF-8; the cause is one line on stderr and nothing is printed on stdout. Python
standard library only.
"""

import argparse
import datetime
import contextlib
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HERE)
SEP = " › "
SECTION = "§"
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tif", ".tiff")
DOC_EXT = (".md", ".markdown")
INVENTORY_HEADER = ["id", "text", "source_anchor", "defects"]
LEDGER_HEADER = ["id", "text", "disposition", "defects", "evidence"]
# classes a customer's heading path is taken never to hold where the token is certain
PLUGIN_VOCABULARY = ("plugin-root-path", "reference-citation", "slash-command", "agent-or-skill")
SEPARATOR_RE = re.compile(r"[ \t]*\|(?:[ \t]*:?-+:?[ \t]*\|)+[ \t]*$")


class Refused(Exception):
    """An input cannot be read; main() prints the message and exits 2."""


def _stems(d, dirs=False):
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    if dirs:
        return [n for n in names if os.path.isdir(os.path.join(d, n))]
    return [n[:-3] for n in names if n.endswith(".md")]


def family(root=PLUGIN_ROOT):
    """The plugins beside this one: {names, commands, agents, homes}."""
    found = {}
    parent = os.path.dirname(root)
    candidates = []
    for base in (parent, os.path.dirname(parent)):
        for e in _stems(base, dirs=True):
            d = os.path.join(base, e)
            candidates.append(d)
            candidates.extend(os.path.join(d, v) for v in _stems(d, dirs=True))
    for d in candidates:
        pj = os.path.join(d, ".claude-plugin", "plugin.json")
        if os.path.isfile(pj):
            found.setdefault(os.path.realpath(d), d)
    fam = {"names": set(), "commands": set(), "agents": set(), "homes": set()}
    for d in found.values():
        try:
            with open(os.path.join(d, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
                name = json.load(f).get("name") or ""
        except (OSError, ValueError, AttributeError):
            name = ""
        if isinstance(name, str) and re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
            fam["names"].add(name)
        fam["commands"].update(_stems(os.path.join(d, "commands")))
        fam["agents"].update(_stems(os.path.join(d, "agents")))
        for home in (os.path.dirname(d), os.path.realpath(os.path.dirname(d))):
            if len(home) > 1:
                fam["homes"].add(home)
    return fam


def _alt(words):
    return "|".join(re.escape(w) for w in sorted(words, key=lambda w: (-len(w), w)))


def _patterns(fam):
    """Each class's patterns, as (class, regex, certain)."""
    ns = r"[a-z0-9-]*workflows[a-z0-9-]*"
    if fam["names"]:
        ns = "(?:" + _alt(fam["names"]) + "|" + ns + ")"
    cmd_lb = r"(?<![\w/.:~)\]}<-])"
    pats = [
        ("plugin-root-path", re.compile(r"CLAUDE_PLUGIN_ROOT"), True),
        ("plugin-root-path", re.compile(r"\.claude/plugins/"), True),
        ("reference-citation", re.compile(r"(?<![\w-])references/"), True),
        ("reference-citation", re.compile(r"docs/superpowers/"), True),
        ("reference-citation", re.compile(r"Skill\(\s*(?:skill\s*:|$)"), True),
        ("section-sign", re.compile(SECTION), True),
        ("slash-command", re.compile(cmd_lb + "/" + ns + r":(?:[A-Za-z][\w-]*|$)"), True),
        ("agent-or-skill", re.compile(r"subagent_type"), True),
        ("agent-or-skill", re.compile(r"(?<![\w/:-])" + ns + r":(?:[A-Za-z][\w-]*|$)"), True),
        ("decision-row", re.compile(r"(?<![\w#-])D[0-9]+(?![\w#])"), True),
        ("model-id", re.compile(
            r"(?<![\w-])claude-(?:[a-z]+-[0-9]+(?:[-.][0-9]+)*|[0-9]+(?:[-.][0-9]+)*-[a-z]+"
            r"|[0-9]+\.[0-9]+)(?:-[0-9]{8})?(?:\[[^\]\s]*\])?"), True),
    ]
    if fam["homes"]:
        pats.append(("plugin-root-path", re.compile("(?:" + _alt(fam["homes"]) + r")(?=/|$)"), True))
    hyphenated = {c for c in fam["commands"] if "-" in c}
    if hyphenated:
        pats.append(("slash-command", re.compile(
            cmd_lb + "/(?:" + _alt(hyphenated) + r")(?![\w/-])(?!\.\w)"), True))
    pats.append(("slash-command", re.compile(cmd_lb + r"/[a-z][a-z0-9-]*(?![\w/:-])(?!\.\w)"), False))
    if fam["agents"]:
        alt = _alt(fam["agents"])
        pats.append(("agent-or-skill", re.compile(r"(?<![\w-])(?:" + alt + r")\.md(?![\w])"), True))
        pats.append(("agent-or-skill", re.compile(r"(?<![\w/.:-])(?:" + alt + r")(?![\w-])(?!\.md)"), False))
    return pats


def _delimiters(line):
    """Offsets of every delimiting '|' in a table line (brd-format section 2.3, rule 1)."""
    return [i for i, ch in enumerate(line) if ch == "|" and (not line[:i].strip() or line[i - 1] == " ")]


def _cells(line):
    """[(start, end, decoded text)] for each cell of a table line, offsets into the raw line."""
    d = _delimiters(line)
    cells = []
    for a, b in zip(d, d[1:]):
        raw = line[a + 1:b]
        text = raw[1:] if raw.startswith(" ") else raw
        text = text[:-1] if text.endswith(" ") else text
        text = re.sub(r"(\\+)\|", lambda m: "\\" * (len(m.group(1)) // 2) + "|", text)
        cells.append((a + 1, b, text.replace("<br>", "\n")))
    return cells


def _table_kinds(lines):
    """{line index: (kind, cells)} for every row of an inventory or ledger table."""
    rows, kind = {}, None
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            kind = None
            continue
        cells = _cells(line)
        names = [c[2].strip() for c in cells]
        if names == INVENTORY_HEADER:
            kind = "inventory"
        elif names == LEDGER_HEADER:
            kind = "ledger"
        elif kind and not SEPARATOR_RE.match(line):
            rows[i] = (kind, cells)
    return rows


def _image_anchor(anchor):
    head = anchor.split(SEP, 1)[0].strip()
    if not (head.startswith("source/") or head.startswith("source-external/")):
        return False
    return head.lower().endswith(IMAGE_EXT)


def _tail_end(line, j):
    """Where a locator's tail starting at j ends: the line's end, a delimiting '|', '`', ')' or ']'."""
    k = j
    while k < len(line):
        ch = line[k]
        if ch in "`)]" or (ch == "|" and line[k - 1] == " "):
            break
        k += 1
    return k


def _locators(line, captured, paths):
    """(locator ranges, tail ranges, rule-1 section offsets) in one line."""
    locs, tails, rule1 = [], [], set()
    for p in paths:
        for m in re.finditer(r"(?<![\w/.-])" + re.escape(p) + r"(?![\w-])", line):
            locs.append((m.start(), m.end()))
            if line.startswith(SEP, m.end()):
                j = m.end() + len(SEP)
                end = _tail_end(line, j)
                tails.append((j, end))
                if line.startswith(SECTION, j):
                    rule1.add(j)
    for name in captured:
        for m in re.finditer(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])", line):
            locs.append((m.start(), m.end()))
    return locs, tails, rule1


def scan_text(name, text, pats, prereq_keys, captured, paths):
    """(hits, omitted) for one file's text."""
    lines = text.split("\n")
    rows = _table_kinds(lines)
    base = os.path.basename(name)
    whole = base in captured
    prereq = any(base.startswith(k + "-") for k in prereq_keys)
    hits, omitted = [], 0
    for i, line in enumerate(lines):
        row = rows.get(i)
        locs, tails, rule1 = _locators(line, captured, paths)
        anchor = None
        if row and row[0] == "inventory" and len(row[1]) == 4:
            anchor = row[1][2]
            j = anchor[0]
            while j < anchor[1] and line[j] == " ":
                j += 1
            if line.startswith(SECTION, j):
                rule1.add(j)
        seen, found = set(), []
        for cls, rx, certain in pats:
            for m in rx.finditer(line):
                if (m.start(), m.end()) in seen:
                    continue
                if cls == "section-sign" and m.start() in rule1:
                    omitted += 1
                    continue
                seen.add((m.start(), m.end()))
                found.append((m.start(), m.end(), cls, certain))
        # a certain reading of a token shadows an uncertain reading inside it
        sure = [(a, b) for a, b, c, k in found if k]
        found = [f for f in found if f[3] or not any(a <= f[0] < b for a, b in sure)]
        for a, b, cls, certain in sorted(found):
            span, image_row = "none", None
            if whole:
                span = "captured-file"
            elif any(s <= a < e for s, e in locs):
                span = "locator"
            elif any(s <= a < e for s, e in tails) and not (certain and cls in PLUGIN_VOCABULARY):
                span = "locator-tail"
            elif row:
                kind, cells = row
                if len(cells) == (4 if kind == "inventory" else 5):
                    if cells[1][0] <= a < cells[1][1]:
                        span = kind + "-text"
                        image_row = _image_anchor(cells[2][2]) if kind == "inventory" else None
                    elif anchor and anchor[0] <= a < anchor[1]:
                        span = "anchor"
            hits.append({"file": name, "line": i + 1, "class": cls, "token": line[a:b], "span": span,
                         "certain": certain, "image_row": image_row, "prerequisite": prereq})
    return hits, omitted


def _files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs.sort()
                for n in sorted(names):
                    if n.lower().endswith(DOC_EXT):
                        full = os.path.join(root, n)
                        out.append((os.path.relpath(full, p), full))
        elif os.path.isfile(p):
            out.append((os.path.basename(p), p))
        else:
            raise Refused("no such file or directory: " + p)
    return out


def scan(paths, prereq_keys=(), captured=(), captured_paths=(), fam=None):
    pats = _patterns(family() if fam is None else fam)
    files = _files(paths)
    hits, omitted = [], 0
    for name, full in files:
        try:
            with open(full, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise Refused("cannot read " + name + " as UTF-8: " + e.__class__.__name__)
        h, o = scan_text(name, text, pats, list(prereq_keys), set(captured), list(captured_paths))
        hits.extend(h)
        omitted += o
    groups, index = [], {}
    for h in hits:
        k = (h["file"], h["token"], h["span"], h["prerequisite"], h["image_row"])
        if k not in index:
            index[k] = {"file": h["file"], "token": h["token"], "class": h["class"], "span": h["span"],
                        "prerequisite": h["prerequisite"], "image_row": h["image_row"],
                        "certain": h["certain"], "count": 0, "lines": []}
            groups.append(index[k])
        index[k]["count"] += 1
        index[k]["lines"].append(h["line"])
    return {"files": len(files), "omitted_locator_sections": omitted, "groups": groups}



# ---------------------------------------------------------------------------------------------------
# citations: bundle-packaging section 6, run over an assembled bundle
# ---------------------------------------------------------------------------------------------------

REFERENCE = os.path.join(PLUGIN_ROOT, "references", "bundle-packaging.md")
ID_RE = re.compile(r"\[(BR|DEF|CG|DG|VD|CDF|CD|AS|SR)#(n|[0-9]+)\]")
KEY_TOKEN = r"[A-Z][A-Z0-9_]*(?:-[0-9]+)+"
PROSE_KEY_RE = re.compile(r"(?<![\w/-])(" + KEY_TOKEN + r") $")
SLASH_KEY_RE = re.compile(r"(?<![\w/-])(" + KEY_TOKEN + r")/$")
KEY_ANY_RE = re.compile(r"(?<![\w/-])(" + KEY_TOKEN + r")(?![\w-])")
REQ_RE = re.compile(r"\[(?:BR|US|AC|FR)#[0-9]+\]")
MD_TOKEN_RE = re.compile(r"(?<![\w/.<>-])([\w][\w.<>-]*\.md)(?![\w/])")
# Which corpus file each identifier class resolves against (section 6.1's table), by the working
# basename the file's bundled name carries after its key.
CORPUS_FILES = {
    "BR": ("brd-inventory.md",),
    "DEF": ("brd-defect-log.md",),
    "CG": ("code-grounding.md", "design-grounding.md"),
    "DG": ("code-grounding.md", "design-grounding.md"),
    "VD": ("decisions.md",), "CD": ("decisions.md",), "AS": ("decisions.md",),
    "CDF": ("code-defect-log.md",),
}
TABLE_CORPORA = {"brd-inventory.md", "brd-defect-log.md"}
GROUNDING = ("code-grounding.md", "design-grounding.md")
RECORD_ID_RE = re.compile(r"^\s*-?\s*id\s*:\s*(\S.*?)\s*$")
MARKER_RE = re.compile(r"^\s*(Reopened|Reverted|Withdrawn|Superseded) [0-9]{8}:")
# Section 6.2's structured fields, one entry per row of its table: the marker the row's first cell
# carries, the reading the script gives it, and, for a field written `<name>: <value>` on a line, its
# name. FIELD_RE and FIELD_READING are built from this list, so a named field it gains is matched
# with the reading it names; every reading is one READINGS lists. The selftest holds this list equal
# to the table's rows and every entry to a fixture of its own, so a field an authority adds stops CI
# until it is read here and tested.
STRUCTURED_FIELDS = [
    ("conditional_on:", "slash", "conditional_on"), ("blocked_on:", "slash", "blocked_on"),
    ("`prerequisite`", "keyed-else-report", "prerequisite"), ("rejected:", "slash", "rejected"),
    ("customer-amended", "no-id", None), ("resolved-by:", "slash-else-report", "resolved-by"),
    ("a defect entry is raised against", "defect-log-rows", None),
    ("superseded-by:", "ledger-rows", "superseded-by"), ("*Rows* line", "figures-rows", None),
]
READINGS = ("slash", "keyed-else-report", "slash-else-report", "ledger-rows", "defect-log-rows",
            "figures-rows", "no-id")
FIELD_READING = {name: reading for _, reading, name in STRUCTURED_FIELDS if name}
FIELD_RE = re.compile(r"(?<![\w-])(" + "|".join(re.escape(n) for n in FIELD_READING) + r")\s*:")


def _section(text, start, stop):
    a = text.find(start)
    if a < 0:
        return None
    b = text.find(stop, a + len(start))
    return text[a:b if b >= 0 else len(text)]


def reference_text():
    try:
        with open(REFERENCE, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError) as e:
        raise Refused("cannot read the bundle-packaging reference: " + e.__class__.__name__)


def working_names(ref, date=None, source_basenames=()):
    """Section 1.1's working filenames, each a regex over a bare basename (relation 3, shape 2): every
    backticked .md path the section names, in its table and its prose, references/ and commands/ aside."""
    sec = _section(ref, "### 1.1 ", "### 1.2 ")
    if sec is None:
        raise Refused("bundle-packaging.md has no section 1.1 to read the working filenames from")
    names = set()
    for tok in re.findall(r"`([^`\s]+\.md)`", sec):
        if tok.startswith(("references/", "commands/")):
            continue
        names.add(tok.rsplit("/", 1)[-1])
    if not names:
        raise Refused("bundle-packaging.md section 1.1 names no working filename")
    pats = []
    for n in sorted(names):
        if "<file>" in n or "<basename>" in n:
            for b in source_basenames:
                stem = b[:-3] if b.endswith(".md") else b
                pats.append(re.compile(re.escape(stem + ".md") + "$"))
            continue
        rx = re.escape(n)
        rx = rx.replace(re.escape("<YYYYMMDD>"), re.escape(date) if date else "[0-9]{8}")
        rx = rx.replace(re.escape("<N>"), "[0-9]+")
        pats.append(re.compile(rx + "$"))
    return pats


def structured_rows(ref):
    """The first cells of section 6.2's structured-field table."""
    sec = _section(ref, "### 6.2 ", "### 6.3 ")
    if sec is None:
        raise Refused("bundle-packaging.md has no section 6.2 to read the structured fields from")
    rows, inside = [], False
    for line in sec.split("\n"):
        if line.startswith("| Field | Authority |"):
            inside = True
            continue
        if inside:
            if not line.startswith("|"):
                break
            if SEPARATOR_RE.match(line):
                continue
            cells = _cells(line)
            if cells:
                rows.append(cells[0][2])
    return rows


def _partition(base, keys):
    """The key a bundled filename belongs to, resolved against the run's key set, or None."""
    best = None
    for k in keys:
        if base.startswith(k + "-") and (best is None or len(k) > len(best)):
            best = k
    return best


def _corpus_ids(text, table):
    """(ids, record_shaped) for one corpus file, parsed by its owner's layout (section 6.1)."""
    ids, shaped = set(), False
    lines = text.split("\n")
    if table:
        header = False
        for line in lines:
            if not line.lstrip().startswith("|"):
                header = False
                continue
            cells = _cells(line)
            if not cells:
                continue
            if cells[0][2].strip() == "id":
                header = True
                continue
            if header and not SEPARATOR_RE.match(line):
                shaped = True
                m = re.fullmatch(r"\s*\[([A-Z]+)#([0-9]+)\]\s*", cells[0][2])
                if m:
                    ids.add("[%s#%s]" % (m.group(1), m.group(2)))
    else:
        for line in lines:
            m = RECORD_ID_RE.match(line)
            if m:
                shaped = True
                v = re.fullmatch(r"\[([A-Z]+)#([0-9]+)\]", m.group(1))
                if v:
                    ids.add("[%s#%s]" % (v.group(1), v.group(2)))
    return ids, shaped


def _blocks(text):
    """Grounding finding blocks: [{id, class, cites, claim, line}], read as the id parser reads them,
    a block scalar's indented lines joined to its key."""
    out, cur, key, indent = [], None, None, 0
    for i, line in enumerate(text.split("\n")):
        m = re.match(r"^(\s*)-?\s*id\s*:\s*(\[[A-Z]+#[0-9]+\])", line)
        if m:
            cur, key = {"id": m.group(2), "line": i + 1}, None
            out.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("#"):
            cur = None
            continue
        f = re.match(r"^(\s*)([a-z_]+)\s*:\s*(.*)$", line)
        if f and (key is None or len(f.group(1)) <= indent):
            key, indent = f.group(2), len(f.group(1))
            cur[key] = f.group(3).strip()
            if cur[key] in ("|", ">", "|-", ">-"):
                cur[key] = ""
        elif key and line.strip():
            cur[key] = (cur.get(key, "") + " " + line.strip()).strip()
    return out


def _evidence_lines(text):
    """Line indexes inside a grounding block's evidence or control field, where relation 3 stays off."""
    out, inside, indent = set(), False, 0
    for i, line in enumerate(text.split("\n")):
        f = re.match(r"^(\s*)-?\s*([a-z_]+)\s*:", line)
        if f and not line.strip().startswith("- path"):
            lead = len(f.group(1))
            if inside and lead <= indent:
                inside = False
            if f.group(2) in ("evidence", "control"):
                inside, indent = True, lead
                out.add(i)
                continue
        if inside:
            out.add(i)
    return out


def _quoted_spans(base, lines):
    """{line index: [(start, end)]} for the customer's words the figures file and the register quote:
    the figures file's Text, the Says column of its Annotations and its Flow; a [CD#n]'s argumentation,
    its plugin-written Reopened, Reverted, Withdrawn and Superseded paragraphs aside, and its chosen
    where that quotes an answer outside the options (section 6.3)."""
    spans = {}
    if base.endswith("brd-figures.md"):
        section, fence = None, None
        for i, line in enumerate(lines):
            if fence is None and line.startswith("### "):
                section = line[4:].strip()
                continue
            if fence is None and line.startswith("## "):
                section = None
                continue
            if section == "Text":
                f = re.match(r"^(`{3,}|~{3,})(.*)$", line)
                if fence is None:
                    if f:
                        fence = f.group(1)
                    continue
                if f and f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence) and not f.group(2).strip():
                    fence = None  # a closing fence: the same character, at least as long, no info string
                    continue
                spans.setdefault(i, []).append((0, len(line)))
            elif section == "Flow" and line.lstrip().startswith("- "):
                spans.setdefault(i, []).append((0, len(line)))
            elif section == "Annotations" and line.lstrip().startswith("|") and not SEPARATOR_RE.match(line):
                cells = _cells(line)
                if cells and cells[0][2].strip() != "Says":
                    spans.setdefault(i, []).append((cells[0][0], cells[0][1]))
    if base.endswith("decisions.md"):
        record, block, marker = None, None, False
        for i, line in enumerate(lines):
            m = RECORD_ID_RE.match(line)
            if m:
                record, block, marker = m.group(1), None, False
                continue
            f = re.match(r"^(\s*)([a-z_]+)\s*:\s*(\|[-+]?)?(.*)$", line)
            if f and (block is None or len(f.group(1)) <= block):
                cd = bool(record and record.startswith("[CD#"))
                # a [CD#n]'s argumentation, and its chosen where a block scalar carries an answer outside
                # the options (decision-register-format section 1's form for one spanning lines)
                block = len(f.group(1)) if f.group(3) and f.group(2) in ("argumentation", "chosen") else None
                marker = False
                if cd and f.group(2) == "chosen" and "outside the options:" in line:
                    spans.setdefault(i, []).append((line.index("outside the options:"), len(line)))
                if not cd:
                    block = None
                continue
            if block is not None:
                if not line.strip():
                    marker = False
                    continue
                if MARKER_RE.match(line):
                    marker = True
                if not marker:
                    spans.setdefault(i, []).append((0, len(line)))
    return spans


def _key_reading(k, own, known):
    """How a key carried before an id reads: 'own', 'other' (a known BRD) or 'unknown'."""
    if k == own:
        return "own"
    return "other" if k in known else "unknown"


def citations(bundle, key, prereq_keys=(), copied_keys=(), date=None, captured=(), captured_paths=(),
              source_basenames=(), manifest=None, known_keys=(), prereq_aux=(), ref=None):
    ref = reference_text() if ref is None else ref
    names_rx = working_names(ref, date, source_basenames)
    keys = [key] + [k for k in prereq_keys if k != key]
    known = set(keys) | set(known_keys)
    captured, captured_paths, prereq_aux = set(captured), list(captured_paths), set(prereq_aux)
    files = _files([bundle])
    texts = {}
    for name, full in files:
        try:
            with open(full, encoding="utf-8") as f:
                texts[name] = f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise Refused("cannot read " + name + " as UTF-8: " + e.__class__.__name__)
    try:
        bundle_names = {n for _, _, ns in os.walk(bundle) for n in ns}
    except OSError as e:
        raise Refused("cannot list the bundle: " + e.__class__.__name__)
    out = {"partitions": {}, "resolved": 0, "discharged": 0, "dead": [], "mismatch": [], "ambiguous": [],
           "unqualified": [], "unknown_key": [], "unreadable": [], "customer": [], "groups": [],
           "prerequisite_external": []}
    part_of = {}
    for name in texts:
        k = _partition(os.path.basename(name), keys)
        part_of[name] = k
        if k is None:
            out["dead"].append({"file": name, "line": 0, "token": name, "reason": "unkeyed bundle document"})
        else:
            out["partitions"].setdefault(k, []).append(name)
    for k in copied_keys:
        if k not in out["partitions"]:
            out["dead"].append({"file": None, "line": 0, "token": k,
                                "reason": "a prerequisite package copied in answers to no partition"})
    corpus = {}
    for k, names in out["partitions"].items():
        ids = {}
        for name in names:
            base = os.path.basename(name)[len(k) + 1:]
            classes = [c for c, files_ in CORPUS_FILES.items() if base in files_]
            if not classes:
                continue
            got, shaped = _corpus_ids(texts[name], base in TABLE_CORPORA)
            for cls in classes:
                ids.setdefault(cls, set()).update(g for g in got if g.startswith("[" + cls + "#"))
            if shaped and not got:
                out["unreadable"].append({"file": name, "classes": classes})
        corpus[k] = ids

    def resolve(hit, k, tok, cls, span):
        if tok in corpus.get(k, {}).get(cls, set()):
            out["resolved"] += 1
            return
        hit["reason"] = "not in %s's %s corpus" % (k, cls)
        if span:
            hit["span"] = span
            out["customer"].append(hit)
        else:
            out["dead"].append(hit)

    for name, text in texts.items():
        k = part_of[name]
        if k is None:
            continue
        base = os.path.basename(name)
        working = base[len(k) + 1:]
        lines = text.split("\n")
        rows = _table_kinds(lines)
        quoted = _quoted_spans(working, lines)
        whole = base in captured
        in_prereq = k != key
        defect_table = working == "brd-defect-log.md"
        evidence = _evidence_lines(text) if working in GROUNDING else set()
        inventory = corpus.get(k, {}).get("BR", set())
        for i, line in enumerate(lines):
            row = rows.get(i)
            locs, tails, _ = _locators(line, captured, captured_paths)

            def placed(a):
                if whole:
                    return "captured-file", None
                if any(s <= a < e for s, e in locs):
                    return "locator", None
                if any(s <= a < e for s, e in tails):
                    return "locator-tail", None
                if any(s <= a < e for s, e in quoted.get(i, ())):
                    return "quoted", None
                if row:
                    kind, cells = row
                    if len(cells) == (4 if kind == "inventory" else 5):
                        if cells[1][0] <= a < cells[1][1]:
                            return kind + "-text", (_image_anchor(cells[2][2]) if kind == "inventory" else None)
                        if kind == "inventory" and cells[2][0] <= a < cells[2][1]:
                            return "anchor", None
                return None, None

            discharged_cells = []
            if row and row[0] == "ledger" and len(row[1]) == 5:
                idcell = row[1][0]
                if idcell[2].strip() not in inventory:
                    discharged_cells.append((idcell[0], idcell[1]))  # an orphan row's own id
            if defect_table and line.lstrip().startswith("|") and not SEPARATOR_RE.match(line):
                cells = _cells(line)
                if len(cells) >= 4:
                    discharged_cells.extend([(cells[2][0], cells[2][1]), (cells[3][0], cells[3][1])])
            figures_rows = working == "brd-figures.md" and re.match(r"^\s*- \*\*Rows:\*\*", line)
            # each structured field's value: (start, end, reading)
            fields = []
            starts = [fm.start() for fm in FIELD_RE.finditer(line)]
            for fm in FIELD_RE.finditer(line):
                end = min([d for d in _delimiters(line) if d > fm.end()] + [s for s in starts if s > fm.start()]
                          + [len(line)])
                fields.append((fm.end(), end, FIELD_READING[fm.group(1)], fm.group(1)))
            for m in ID_RE.finditer(line):
                cls, num = m.group(1), m.group(2)
                if cls == "SR" or num == "n":
                    continue
                tok, a = m.group(0), m.start()
                hit = {"file": name, "line": i + 1, "token": tok}
                span, image_row = placed(a)
                if image_row is not None:
                    hit["image_row"] = image_row
                if figures_rows or any(s <= a < e for s, e in discharged_cells):
                    out["discharged"] += 1
                    continue
                field = next((f for f in fields if f[0] <= a < f[1]), None)
                before = line[:a]
                if field and field[2] == "ledger-rows":
                    out["discharged"] += 1
                    continue
                if field and field[2] == "keyed-else-report":
                    carried = [x for x in KEY_ANY_RE.findall(line[field[0]:field[1]]) if x != k]
                    if any(x in known for x in carried):
                        out["discharged"] += 1
                    else:
                        out["unqualified"].append(dict(hit, field=field[3]))
                    continue
                sk = SLASH_KEY_RE.search(before)
                if sk:
                    reading = _key_reading(sk.group(1), k, known)
                    if reading == "own":
                        resolve(hit, k, tok, cls, span)
                    elif not field:
                        out["unqualified"].append(dict(hit, field="a slash form outside a structured field"))
                    elif reading == "other":
                        out["discharged"] += 1
                    else:
                        out["unknown_key"].append(dict(hit, key=sk.group(1)))
                    continue
                if field and field[2] == "slash-else-report":
                    out["unqualified"].append(dict(hit, field=field[3]))
                    continue
                pk = PROSE_KEY_RE.search(before)
                if pk:
                    reading = _key_reading(pk.group(1), k, known)
                    if reading == "other":
                        out["discharged"] += 1
                        continue
                    if reading == "unknown":
                        out["unknown_key"].append(dict(hit, key=pk.group(1)))
                        if in_prereq:
                            # that package is never rewritten (section 5): an id qualified by a key of
                            # its own tree is named, never resolved into its partition
                            out["discharged"] += 1
                            continue
                resolve(hit, k, tok, cls, span)
            if whole:
                continue  # a captured file's own text is outside relation 3 (sections 6.2, 6.3 rule 3)
            for m in MD_TOKEN_RE.finditer(line):
                tok = m.group(1)
                if i in evidence:
                    continue
                if line[m.end():m.end() + 1] == ":" and line[m.end() + 1:m.end() + 2].isdigit():
                    continue  # a <file>:<line> locator names a repository file
                shape1 = _partition(tok, keys) is not None
                shape2 = any(rx.match(tok) for rx in names_rx)
                if not (shape1 or shape2):
                    continue
                if manifest and base == manifest and m.start() > 0 and line[m.start() - 1] in "`\"'" \
                        and m.end() < len(line) and line[m.end()] in "`\"'":
                    continue  # the manifest's quotation of a target as written
                if tok in bundle_names:
                    continue
                span, image_row = placed(m.start(1))
                hit = {"file": name, "line": i + 1, "token": tok, "reason": "names no file in the bundle"}
                if span:
                    hit["span"] = span
                    out["customer"].append(hit)
                elif in_prereq and (tok in prereq_aux or _partition(tok, keys) not in (k, None)):
                    # a file of a package that prerequisite carried, or its own prompt or manifest
                    out["prerequisite_external"].append(hit)
                else:
                    out["dead"].append(hit)
    for k, names in out["partitions"].items():
        blocks = []
        for name in names:
            if os.path.basename(name)[len(k) + 1:] in GROUNDING:
                blocks.extend(dict(b, file=name) for b in _blocks(texts[name]))
        by_id = {b["id"]: b for b in blocks}
        for b in blocks:
            if not b["id"].startswith("[DG#") or b.get("class", "").strip() != "4":
                continue
            cites = re.search(r"\[CG#[0-9]+\]", b.get("cites", ""))
            reqs = set(REQ_RE.findall(b.get("claim", "")))
            if not cites or cites.group(0) not in by_id:
                out["dead"].append({"file": b["file"], "line": b["line"], "token": b.get("cites", ""),
                                    "reason": "class-4 cites no [CG#n] in %s" % k})
                continue
            if len(reqs) != 1:
                out["ambiguous"].append({"file": b["file"], "line": b["line"], "token": b["id"],
                                         "requirements": sorted(reqs),
                                         "reason": "its claim names no requirement" if not reqs
                                         else "its claim names more than one requirement"})
                continue
            cited = by_id[cites.group(0)]
            if next(iter(reqs)) not in REQ_RE.findall(cited.get("claim", "")):
                out["mismatch"].append({"file": b["file"], "line": b["line"], "token": b["id"],
                                        "cites": cites.group(0), "claim": b.get("claim", ""),
                                        "cited_claim": cited.get("claim", "")})
    index = {}
    for h in out["customer"]:
        g = (h["file"], h["token"], h.get("span"))
        if g not in index:
            index[g] = {"file": h["file"], "token": h["token"], "span": h.get("span"), "count": 0, "lines": []}
            out["groups"].append(index[g])
        index[g]["count"] += 1
        index[g]["lines"].append(h["line"])
    return out


FIELD_FIXTURES = {}  # marker -> the selftest case that exercises it


def citations_selftest(check):
    ref = reference_text()
    rows = structured_rows(ref)
    markers = [m for m, _, _ in STRUCTURED_FIELDS]
    check("section 6.2's table has one row per structured field the script reads",
          len(rows) == len(STRUCTURED_FIELDS) and all(sum(m in r for r in rows) == 1 for m in markers))
    check("every structured field's reading is one citations() branches on",
          {r for _, r, _ in STRUCTURED_FIELDS} <= set(READINGS))
    wn = working_names(ref, "20261029")
    check("section 1.1's working filenames are read from the reference",
          any(rx.match("decisions.md") for rx in wn) and any(rx.match("self-review-20261029.md") for rx in wn)
          and not any(rx.match("self-review-20261030.md") for rx in wn))

    def run(files, **kw):
        kw.setdefault("key", "K-1")
        with tempfile.TemporaryDirectory() as d:
            for n, t in files.items():
                with open(os.path.join(d, n), "w", encoding="utf-8") as f:
                    f.write(t)
            return citations(d, ref=ref, **kw)

    def fixture(marker, label, cond):
        FIELD_FIXTURES[marker] = label
        check(label, cond)

    inv = "| id | text | source_anchor | defects |\n|---|---|---|---|\n| [BR#1] | a | 2. x | |\n"
    grd = "- id:       [CG#1]\n  claim: [BR#1] — x\n  verdict: CONFIRMED\n\n- id: [CG#12]\n  claim: [BR#1] — y\n"
    r = run({"K-1-brd-inventory.md": inv, "K-1-code-grounding.md": grd,
             "K-1-prompt.md": "See [CG#1], [CG#12], [BR#1], [SR#3] and [BR#n]; [CG#99] is gone.\n"})
    check("padded and unpadded ids parse; [SR#n] and placeholders are no hit; a missing id is dead",
          [h["token"] for h in r["dead"]] == ["[CG#99]"] and r["resolved"] == 8)
    r = run({"K-1-a.md": "x\n", "Z-a.md": "y\n"}, copied_keys=["P-2"], prereq_keys=["P-2", "P-3"])
    check("an unkeyed document is dead, and so is a copied-in prerequisite with no partition",
          sorted(h["reason"] for h in r["dead"]) == ["a prerequisite package copied in answers to no partition",
                                                    "unkeyed bundle document"])
    r = run({"K-1-code-grounding.md": grd, "P-2-code-grounding.md": "- id: [CG#7]\n  claim: [BR#1] — z\n",
             "K-1-brd-inventory.md": inv, "P-2-brd-inventory.md": inv, "K-10-x.md": "z\n",
             "K-1-prompt.md": "Ours [CG#7] dead; P-2 [CG#7] theirs; K-1 [CG#99] own and dead; Q-5 [CG#1]; "
                              "UTF-8 [CG#98].\n"},
            prereq_keys=["P-2", "K-10"], copied_keys=["P-2", "K-10"], known_keys=["Q-5"])
    check("own ids resolve; a known BRD's qualified id is discharged; an unknown key-shaped word is reported",
          sorted(h["token"] for h in r["dead"]) == ["[CG#7]", "[CG#98]", "[CG#99]"] and r["discharged"] == 2
          and [h["key"] for h in r["unknown_key"]] == ["UTF-8"] and r["partitions"]["K-10"] == ["K-10-x.md"])
    reg = ("id: [CD#1]\nconditional_on: P-2/[CD#2]\nchosen: |\n  outside the options: We want \"both\", as [BR#77] says\n\n"
           "id: [VD#2]\nargumentation: |\n  per [CG#55]\n\n"
           "id: [CD#3]\nargumentation: |\n  their [CG#56] words\n\n  Reopened 20261020: by [CD#1], since the\n"
           "  finding [CG#57] moved\n\n  re-decided, per [CG#58]\n")
    fixture("conditional_on:", "conditional_on: another key's decision is discharged",
            run({"K-1-decisions.md": reg}, prereq_keys=["P-2"])["discharged"] == 1)
    r = run({"K-1-decisions.md": reg})
    check("a [VD#n]'s argumentation and a [CD#n]'s Reopened paragraph are the package's own; a [CD#n]'s quoted words are the customer's",
          sorted(h["token"] for h in r["dead"]) == ["[CG#55]", "[CG#57]"]
          and sorted(h["token"] for h in r["customer"]) == ["[BR#77]", "[CG#56]", "[CG#58]"])
    cdl = "id: [CDF#1]\nblocked_on: P-2/[VD#4]\n\nid: [CDF#2]\nblocked_on: K-1/[VD#9]\n"
    r = run({"K-1-code-defect-log.md": cdl}, prereq_keys=["P-2"])
    fixture("blocked_on:", "blocked_on: another key discharged, its own key resolved",
            r["discharged"] == 1 and [h["token"] for h in r["dead"]] == ["[VD#9]"])
    r = run({"K-1-code-grounding.md": "- id: [CG#1]\n  prerequisite: the P-2 decision [VD#1] — x\n"
                                      "- id: [CG#2]\n  prerequisite: switch it, [VD#1]\n",
             "K-1-decisions.md": "id: [VD#1]\n"}, prereq_keys=["P-2"])
    fixture("`prerequisite`", "prerequisite: a value carrying a known key is discharged, a bare one reported, never resolved",
            r["discharged"] == 1 and [h["token"] for h in r["unqualified"]] == ["[VD#1]"] and r["resolved"] == 3)
    led = ("| id | text | disposition | defects | evidence |\n|---|---|---|---|---|\n"
           "| [BR#1] | y | rejected: K-1/[CD#9] | | |\n| [BR#4] | x | rejected: [DEF#1] | | |\n"
           "| [BR#5] | x | superseded-by: [BR#8] | | |\n| [BR#6] | x | covered-here | | |\n")
    r = run({"K-1-coverage-ledger.md": led, "K-1-brd-inventory.md": inv,
             "K-1-brd-defect-log.md": "| id | class | raised on | names | reason | resolution |\n|---|---|---|---|---|---|\n"
                                      "| [DEF#1] | duplicate | [BR#30] | [BR#31] | r | customer-amended K-1 20261020 |\n"})
    fixture("rejected:", "rejected: its own key resolved; orphan rows of any disposition are discharged",
            [h["token"] for h in r["dead"]] == ["[CD#9]"])
    fixture("superseded-by:", "superseded-by: its [BR#n] is discharged",
            r["discharged"] == 6)
    fixture("customer-amended", "customer-amended carries no id: its line yields no entry of any kind",
            not any(h["line"] == 3 and h["file"] == "K-1-brd-defect-log.md"
                    for lst in ("dead", "unqualified", "unknown_key", "customer") for h in r[lst]))
    fixture("a defect entry is raised against", "the parent defect log's raised-on and names cells are discharged",
            not any(h["token"] in ("[BR#30]", "[BR#31]") for h in r["dead"]))
    r = run({"K-1-x.md": "resolved-by: K-1/[CD#9]\nresolved-by: [CG#4]\nprose P-2/[CD#5]\n"},
            prereq_keys=["P-2"])
    fixture("resolved-by:", "resolved-by: its own key resolved, a bare one reported; a slash form in prose is reported",
            [h["token"] for h in r["dead"]] == ["[CD#9]"]
            and sorted(h["token"] for h in r["unqualified"]) == ["[CD#5]", "[CG#4]"])
    r = run({"K-1-brd-figures.md": "## source/i.png\n\n- **Rows:** yields [BR#14]; illustrates [BR#6]\n\n"
                                   "### Text\n\n````text\nsee [BR#77]\n```\nstill [BR#79]\n````\n\n### Flow\n\n- a → [BR#80]\n"})
    fixture("*Rows* line", "the figures Rows line is discharged; its Text, nested fences and Flow are the customer's",
            r["discharged"] == 2 and sorted(h["token"] for h in r["customer"]) == ["[BR#77]", "[BR#79]", "[BR#80]"])
    check("every structured field has a fixture of its own", set(FIELD_FIXTURES) == set(markers))
    r = run({"K-1-decisions.md": "header only\n", "K-1-code-grounding.md": "- id: CG-1\n  claim: x\n"})
    check("a header-only register is empty; a grounding file whose ids are malformed is unreadable, once",
          [h["file"] for h in r["unreadable"]] == ["K-1-code-grounding.md"])
    r = run({"K-1-brief.md": "Their [BR#4]; see notes.md and K-1-gone.md.\n", "K-1-brd-inventory.md": inv},
            captured=["K-1-brief.md"])
    check("a captured file's ids go to the ruling, and its links are outside relation 3",
          [h["span"] for h in r["customer"]] == ["captured-file"] and r["dead"] == [] and r["groups"][0]["count"] == 1)
    inv2 = inv + "| [BR#2] | b | 2. Fields (see [DEF#7]) | |\n"
    r = run({"K-1-brd-inventory.md": inv2})
    check("an id inside an inventory row's source_anchor is the customer's naming",
          [h["span"] for h in r["customer"]] == ["anchor"])
    dg = ("- id: [CG#1]\n  claim: [BR#1] — x\n\n- id: [CG#2]\n  claim: [BR#2] — y\n\n"
          "- id: [DG#1]\n  class: 4\n  cites: [CG#1]\n  claim: the export, per [BR#1], runs\n\n"
          "- id: [DG#2]\n  class: 4\n  cites: [CG#2]\n  claim: [BR#1] — z\n\n"
          "- id: [DG#3]\n  class: 4\n  cites: [CG#9]\n  claim: [BR#1] — w\n\n"
          "- id: [DG#4]\n  class: 4\n  cites: [CG#1]\n  claim: [BR#1] and [BR#2]\n\n"
          "id: [DG#5]\nclass: 4\ncites: [CG#2]\nclaim: |\n  multi-line, about [BR#1]\n")
    r = run({"K-1-design-grounding.md": dg, "K-1-brd-inventory.md": inv + "| [BR#2] | b | 2. y | |\n"})
    check("relation 2: matches pass; mismatches — a dashless block and a block-scalar claim among them — are reported",
          sorted(h["token"] for h in r["mismatch"]) == ["[DG#2]", "[DG#5]"]
          and [h["token"] for h in r["ambiguous"]] == ["[DG#4]"] and any("class-4" in h["reason"] for h in r["dead"]))
    r = run({"K-1-decisions.md": "id: [CD#1]\n",
             "K-1-prompt.md": "Open K-1-decisions.md, not K-1-gone.md; not self-review-20261029.md; "
                              "evidence README.md:12; plain notes.md.\n",
             "K-1-code-grounding.md": "- id: [CG#1]\n  claim: x\n  evidence:\n    - path: README.md\n"
                                      "      lines: [3]\n    - path: decisions.md\n  verdict: CONFIRMED\n"},
            date="20261029", source_basenames=["README.md"])
    check("relation 3: an absent or excluded name is dead; grounding evidence, in either form, is no hit",
          sorted(h["token"] for h in r["dead"]) == ["K-1-gone.md", "self-review-20261029.md"])
    r = run({"K-1-manifest.md": "brd/source/a.md → K-1-a.md — linked as `notes.md`; see decisions.md\n",
             "K-1-a.md": "x\n"}, manifest="K-1-manifest.md", source_basenames=["notes.md"])
    check("only the target the manifest quotes as written is exempt; its own prose is tested",
          [h["token"] for h in r["dead"]] == ["decisions.md"])
    r = run({"P-2-01-q.md": "the parent's row P-2 [BR#12]\n"}, prereq_keys=["P-2-01"], copied_keys=["P-2-01"])
    check("in a copied prerequisite, an id its own tree's key qualifies is named and discharged, never resolved",
          r["dead"] == [] and [h["key"] for h in r["unknown_key"]] == ["P-2"] and r["discharged"] == 1)
    r = run({"K-1-manifest.md": "decisions.md\n", "K-1-a.md": "x\n"}, manifest="K-1-manifest.md")
    check("a manifest name at a line's edge, unquoted, is tested", [h["token"] for h in r["dead"]] == ["decisions.md"])
    r = run({"P-2-x.md": "see P-2-gone.md, Q-9-other.md and P-2-manifest.md\n"},
            prereq_keys=["P-2", "Q-9"], copied_keys=["P-2"], prereq_aux=["P-2-manifest.md"])
    check("in a copied prerequisite, a file of a package it carried, or its own manifest, is named, never a stop; its own missing file is dead",
          [h["token"] for h in r["dead"]] == ["P-2-gone.md"]
          and sorted(h["token"] for h in r["prerequisite_external"]) == ["P-2-manifest.md", "Q-9-other.md"])


# ---------------------------------------------------------------------------------------------------
# sets: bundle-packaging section 7, run over an assembled bundle and the delivery note
# ---------------------------------------------------------------------------------------------------

PART_RE = re.compile(r"^##\s+([0-9]+)\s*[.·:]?\s")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _read(path, name):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise Refused("no " + name + " to read")
    except (OSError, UnicodeDecodeError) as e:
        raise Refused("cannot read " + name + " as UTF-8: " + e.__class__.__name__)


def prompt_parts(lines):
    """{part: (heading line index, end index)} for the prompt's eleven parts, each a '## <N>' heading
    with '.', '·' or ':' after the number, outside a code fence. Anything but parts 1 to 11, once each
    and in order, is refused: the relations below cannot be placed in a prompt whose parts are not."""
    heads, fence = [], None
    for i, line in enumerate(lines):
        f = FENCE_RE.match(line)
        if f:
            if fence is None:
                fence = f.group(1)[0]
            elif f.group(1)[0] == fence:
                fence = None
            continue
        if fence is None:
            m = PART_RE.match(line)
            if m:
                heads.append((int(m.group(1)), i))
    found = [n for n, _ in heads]
    if found != list(range(1, 12)):
        raise Refused("the prompt's part headings are not parts 1 to 11, once each and in order: found %s"
                      % found)
    return {n: (i, heads[k + 1][1] if k + 1 < len(heads) else len(lines)) for k, (n, i) in enumerate(heads)}


LIVE_POSITION = ("open", "decided", "reopened")
# Relation 1's enumerations: the part, the sub-heading Phase 6 renders it under, the prefix its records
# carry, the working name of its source, the filter as written, and the filter as the records' own
# fields test it (section 7.1, "Resolve the filter against the records' own fields").
REGIONS = [
    (6, "Code defects we will repair", "CDF", "code-defect-log.md", "disposition: in-scope",
     lambda r, u: r.get("disposition") == "in-scope"),
    (7, "Open assumptions", "AS", "decisions.md", "status: open", lambda r, u: r.get("status") == "open"),
    (8, "Positions that could still move", "VD", "decisions.md",
     "conditional_on an unreviewed prerequisite, status open, decided or reopened",
     lambda r, u: r.get("status") in LIVE_POSITION and r.get("conditional_on", "").split("/", 1)[0].strip() in u),
    (8, "Code defects whose scope is unsettled", "CDF", "code-defect-log.md", "disposition: conditional",
     lambda r, u: r.get("disposition") == "conditional"),
    (9, "Open assumptions", "AS", "decisions.md", "status: open", lambda r, u: r.get("status") == "open"),
    (11, "Code defects we will not repair", "CDF", "code-defect-log.md", "disposition: out-of-scope",
     lambda r, u: r.get("disposition") == "out-of-scope"),
]
SUBHEAD_RE = re.compile(r"^(#{3,6})\s+(?:[0-9]+(?:\.[0-9]+)*\.?\s+)?(.+?)\s*$")
ANY_HEAD_RE = re.compile(r"^(#{1,6})\s")
ITEM_RE = re.compile(r"^\s*(?:[-*+]\s|[0-9]+[.)]\s|\||#{1,6}\s)")
OPENER_RE = re.compile(r"^[\s*_`]*\[([A-Z]+)#([0-9]+)\]")
RANGE_TAIL_RE = re.compile(r"^[\s*_`]*[–-][\s*_`]*\[([A-Z]+)#([0-9]+)\]")


def _unfenced(lines, start, end):
    """(index, line) for the lines in [start, end) outside a code fence."""
    fence = None
    for i in range(start, end):
        f = FENCE_RE.match(lines[i])
        if f:
            if fence is None:
                fence = f.group(1)[0]
            elif f.group(1)[0] == fence:
                fence = None
            continue
        if fence is None:
            yield i, lines[i]


def regions(lines, parts):
    """{(part, title): (start, end)} for each of REGIONS' sub-headings: from the heading to the next
    heading of its level or higher, or the part's end. A sub-heading Phase 6 renders and the prompt
    lacks is refused: the enumeration under it cannot be placed."""
    out = {}
    for part, title, *_ in REGIONS:
        a, b = parts[part]
        found = None
        for i, line in _unfenced(lines, a + 1, b):
            m = SUBHEAD_RE.match(line)
            if found is None:
                if m and m.group(2) == title:
                    found = (i, len(m.group(1)))
                continue
            h = ANY_HEAD_RE.match(line)
            if h and len(h.group(1)) <= found[1]:
                out[(part, title)] = (found[0], i)
                break
        if found is None:
            raise Refused("part %d of the prompt has no '%s' sub-heading" % (part, title))
        out.setdefault((part, title), (found[0], b))
    return out


def _idkey(rid):
    m = re.match(r"\[([A-Z]+)#([0-9]+)\]", rid)
    return (m.group(1), int(m.group(2)))


def members(lines, prefix):
    """The ids of prefix that open an item -- a list item, a table row's first cell, a heading --
    with a range in that position expanded. An id anywhere else in an item is a mention, not a member
    (section 7.1, "Members open an item")."""
    out = set()
    for _, line in _unfenced(lines, 0, len(lines)):
        m = ITEM_RE.match(line)
        if not m or SEPARATOR_RE.match(line):
            continue
        rest = line[m.end():]
        o = OPENER_RE.match(rest)
        if not o or o.group(1) != prefix:
            continue
        lo = hi = int(o.group(2))
        tail = RANGE_TAIL_RE.match(rest[o.end():])
        if tail and tail.group(1) == prefix:
            lo, hi = sorted((lo, int(tail.group(2))))
        out.update("[%s#%d]" % (prefix, n) for n in range(lo, hi + 1))
    return sorted(out, key=_idkey)


def _records(bundle, name):
    """The records of a register-shaped source, by part 1's reader; an absent file is an empty corpus."""
    path = os.path.join(bundle, name)
    if not os.path.exists(path):
        return []
    return _blocks(_read(path, name))


IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")


def _stem(name):
    return name[:-3] if name.endswith(".md") else name


def manifest_documents(text):
    """The first cells of the table under the manifest's '## Documents' heading (Phase 8 rule 6), each
    the name inside its backticks, '.md' stripped; an image row is out of scope (section 7.1)."""
    lines = text.split("\n")
    try:
        a = next(i for i, l in enumerate(lines) if re.match(r"^##\s+Documents\s*$", l))
    except StopIteration:
        raise Refused("the manifest has no '## Documents' heading to read its document list from")
    names, inside = [], False
    for line in lines[a + 1:]:
        if line.startswith("## "):
            break
        if not line.lstrip().startswith("|"):
            if inside:
                break
            continue
        if SEPARATOR_RE.match(line):
            inside = True
            continue
        if not inside:
            continue  # the header row
        cells = _cells(line)
        if not cells:
            continue
        cell = cells[0][2].strip()
        q = re.fullmatch(r"`([^`]+)`", cell)
        name = q.group(1) if q else cell
        if not name.lower().endswith(IMAGE_EXT):
            names.append(_stem(name))
    if not inside:
        raise Refused("the manifest has no table under '## Documents' to read its document list from")
    return names


CLAUSE_RE = re.compile(r"(?i:the) `([^`]+)` repository at commit `([0-9a-f]{7,40})`")
COMMIT_WORD_RE = re.compile(r"(?<![\w/.\-])([0-9a-f]{7,40})(?![\w/\-]|\.\w)")


def baseline_pairs(text):
    """(repo, commit) for each entry of a baselines document, in order, a repeat recorded once."""
    pairs, repo = [], None
    for line in text.split("\n"):
        m = re.match(r"^\s*-\s*repo\s*:\s*(.+?)\s*$", line)
        if m:
            repo = m.group(1).strip("`")
            continue
        m = re.match(r"^\s*commit\s*:\s*([0-9a-f]{7,40})\s*$", line)
        if m and repo and (repo, m.group(1)) not in pairs:
            pairs.append((repo, m.group(1)))
    return pairs


def _is_pin(word, commits):
    """Section 7.1's commit word: a valid YYYYMMDD date, or a word of hex letters alone, is a pin only
    where it prefixes a baseline commit -- the note is prose, and both read as hex."""
    if any(c.startswith(word) for c in commits):
        return True
    if word.isalpha():
        return False
    if len(word) == 8 and word.isdigit():
        try:
            datetime.datetime.strptime(word, "%Y%m%d")
            return False
        except ValueError:
            pass
    return True


def note_pins(out, note_text, pairs, source):
    """Relation 3: the note's pin clauses and commit words against the baselines' (repo, commit) pairs."""
    text = " ".join(note_text.split())
    base = {}
    for repo, commit in pairs:
        base.setdefault(repo, []).append(commit)
    every = [c for _, c in pairs]
    named, extra, covered, spans = [], [], set(), []
    for m in CLAUSE_RE.finditer(text):
        repo, word = m.group(1), m.group(2)
        spans.append(m.span())
        named.append("%s at %s" % (repo, word))
        hits = sorted({c for c in base.get(repo, []) if c.startswith(word)})
        if hits:
            covered.add(repo)
            if len(hits) > 1:
                out["ambiguous"].append({"relation": 3, "where": "delivery note", "token": word, "commits": hits})
        else:
            extra.append("%s at %s" % (repo, word))
    for m in COMMIT_WORD_RE.finditer(text):
        word = m.group(1)
        if any(a <= m.start() < b for a, b in spans) or not _is_pin(word, every):
            continue
        named.append(word)
        hits = sorted({c for c in every if c.startswith(word)})
        if not hits:
            extra.append(word)
        elif len(hits) > 1:
            out["ambiguous"].append({"relation": 3, "where": "delivery note", "token": word, "commits": hits})
    entry = {"relation": 3, "where": "delivery note", "source": source,
             "filter": "repositories and their pinned commits", "named": named,
             "held": ["%s at %s" % p for p in pairs], "extra": extra,
             "missing": ["%s at %s" % (repo, cs[-1]) for repo, cs in base.items() if repo not in covered]}
    if named and not pairs:
        entry["verdict"] = "unreadable"
        out["unreadable"].append(entry)
    elif entry["missing"] or entry["extra"]:
        entry["verdict"] = "mismatch"
        out["mismatch"].append(entry)
    else:
        entry["verdict"] = "pass"
    out["relations"].append(entry)


def _compare(out, relation, where, source, filter_, named, held, key=_idkey):
    named, held = sorted(set(named), key=key), sorted(set(held), key=key)
    entry = {"relation": relation, "where": where, "source": source, "filter": filter_, "named": named,
             "held": held, "missing": [x for x in held if x not in named],
             "extra": [x for x in named if x not in held]}
    if named and not held:
        entry["verdict"] = "unreadable"
        out["unreadable"].append(entry)
    elif entry["missing"] or entry["extra"]:
        entry["verdict"] = "mismatch"
        out["mismatch"].append(entry)
    else:
        entry["verdict"] = "pass"
    out["relations"].append(entry)


def sets(bundle, key, date, manifest, note, unreviewed=()):
    prompt_name = "%s-customer-review-prompt-%s.md" % (key, date)
    lines = _read(os.path.join(bundle, prompt_name), prompt_name).split("\n")
    where = regions(lines, prompt_parts(lines))
    out = {"relations": [], "mismatch": [], "unreadable": [], "ambiguous": []}
    unreviewed = set(unreviewed)
    sources = {}
    for part, title, prefix, working, filter_, test in REGIONS:
        source = "%s-%s" % (key, working)
        if source not in sources:
            sources[source] = _records(bundle, source)
        held = [r["id"] for r in sources[source] if _idkey(r["id"])[0] == prefix and test(r, unreviewed)]
        a, b = where[(part, title)]
        _compare(out, 1, "part %d, %s" % (part, title), source, filter_, members(lines[a + 1:b], prefix), held)
    # relation 2: the working directory this run assembled holds no never-sent marker, so a review
    # document is every markdown file but the manifest
    try:
        listing = [n for n in os.listdir(bundle) if n.endswith(".md") and n != manifest
                   and os.path.isfile(os.path.join(bundle, n))]
    except OSError as e:
        raise Refused("cannot list the bundle: " + e.__class__.__name__)
    _compare(out, 2, "manifest", "the bundle's listing", "every markdown document but the manifest",
             manifest_documents(_read(os.path.join(bundle, manifest), manifest)), [_stem(n) for n in listing],
             key=str)
    source = "%s-baselines.md" % key
    path = os.path.join(bundle, source)
    pairs = baseline_pairs(_read(path, source)) if os.path.exists(path) else []
    note_pins(out, _read(note, "the delivery note " + os.path.basename(note)), pairs, source)
    return out


SETS_DEFAULT_BODIES = {
    6: "### 6.1 Code defects we will repair\n\nNone.\n",
    7: "### 7.3 Open assumptions\n\nNone.\n",
    8: "### 8.1 Positions that could still move\n\nNone.\n\n### 8.2 Code defects whose scope is unsettled\n\nNone.\n",
    9: "### 9.1 Open assumptions\n\nNone.\n",
    11: "### 11.1 Code defects we will not repair\n\nNone.\n",
}


def _sets_prompt(bodies=None, sep=".", numbers=range(1, 12)):
    bodies = {**SETS_DEFAULT_BODIES, **(bodies or {})}
    return "# K-1 — customer review prompt\n\n" + "".join(
        "## %d%s Part %d\n\n%s\n" % (n, sep, n, bodies.get(n, "Text.\n")) for n in numbers)


SHA_A = "abcdef1234567890abcdef1234567890abcdef12"
SHA_B = "1234567fedcba0987654321fedcba0987654321f"


def _sets_baselines(pairs):
    return "# Grounding baselines: K-1\n\n" + "".join(
        "## 2026-10-%02d — %s\n\n- repo: %s\n  commit: %s\n  verification:\n"
        "    - git -C \"<repo>\" rev-parse HEAD → %s\n  result: clean\n\n" % (i + 1, r, r, c, c)
        for i, (r, c) in enumerate(pairs))


def _sets_manifest(names, extra=""):
    return ("# K-1 — bundle manifest\n\nIntro naming `K-1-gone.md` as context not carried.\n\n## Documents\n\n"
            "| File | What it is | For review? |\n|---|---|---|\n"
            + "".join("| `%s` | d | yes |\n" % n for n in names) + extra
            + "\nImage: `K-1-wire.svg`.\n\n## Your files\n\n| Path | In this bundle |\n|---|---|\n"
              "| `source/a.md` | `K-1-a.md` |\n")


def sets_selftest(check):
    def run(files, note="The `app` repository at commit `abcdef1`.\n", **kw):
        kw.setdefault("key", "K-1")
        kw.setdefault("date", "20261029")
        kw.setdefault("manifest", "K-1-manifest.md")
        with tempfile.TemporaryDirectory() as d:
            b = os.path.join(d, "b")
            os.mkdir(b)
            if "K-1-baselines.md" not in files:
                files = dict(files, **{"K-1-baselines.md": _sets_baselines([("app", SHA_A)])})
            if kw["manifest"] not in files:
                files = dict(files, **{kw["manifest"]: _sets_manifest(
                    [n for n in files if n.endswith(".md")])})
            for n, txt in files.items():
                with open(os.path.join(b, n), "w", encoding="utf-8") as fh:
                    fh.write(txt)
            np_ = os.path.join(d, "note.md")
            with open(np_, "w", encoding="utf-8") as fh:
                fh.write(note)
            return sets(b, note=np_, **kw)

    def refused(fn):
        try:
            fn()
        except Refused as e:
            return str(e)
        return None

    lines = _sets_prompt().split("\n")
    parts = prompt_parts(lines)
    check("sets: '## N.' headings locate parts 1 to 11", sorted(parts) == list(range(1, 12)))
    check("sets: '## N ·' headings locate them too",
          sorted(prompt_parts(_sets_prompt(sep=" ·").split("\n"))) == list(range(1, 12)))
    check("sets: a prompt missing part 8 is refused",
          refused(lambda: prompt_parts(_sets_prompt(numbers=[n for n in range(1, 12) if n != 8]).split("\n"))))
    check("sets: a prompt repeating part 7 is refused",
          refused(lambda: prompt_parts(_sets_prompt(numbers=[1, 2, 3, 4, 5, 6, 7, 7, 8, 9, 10, 11]).split("\n"))))
    l10 = _sets_prompt({10: "### 10.3 The twelve sections\n\nx\n"}).split("\n")
    p10 = prompt_parts(l10)
    at = l10.index("### 10.3 The twelve sections")
    check("sets: a schema heading stays inside part 10", p10[10][0] < at < p10[10][1])
    msg = refused(lambda: run({"K-1-manifest.md": "x\n"}))
    check("sets: an absent prompt is refused, by its name",
          bool(msg) and "K-1-customer-review-prompt-20261029.md" in msg)
    def rec(rid, **fields):
        return "id: %s\n" % rid + "".join("%s: %s\n" % (k, v) for k, v in fields.items()) + "\n"

    def r1(r, part, title):
        return next(x for x in r["relations"] if x["relation"] == 1 and x["where"] == "part %d, %s" % (part, title))

    reg = "# Decision register: K-1\n\n" + rec("[AS#1]", statement="a", status="open") \
        + rec("[AS#2]", statement="b", status="open") + rec("[AS#3]", statement="c", status="withdrawn") \
        + rec("[VD#7]", statement="d", conditional_on="P-2/[CD#3]", status="decided") \
        + rec("[VD#8]", statement="e", conditional_on="P-3/[CD#1]", status="decided") \
        + rec("[VD#9]", statement="f", conditional_on="P-2/[CD#4]", status="superseded") \
        + rec("[VD#11]", statement="g", status="decided") \
        + "id: [AS#4]\nstatement: h\nargumentation: |\n  quoted\n  status: open\nstatus: withdrawn\n\n"
    cdl = rec("[CDF#1]", statement="x", disposition="in-scope") + rec("[CDF#2]", statement="y", disposition="conditional",
                                                                       blocked_on="P-2/[CD#3]") \
        + rec("[CDF#3]", statement="z", disposition="out-of-scope") + rec("[CDF#4]", statement="w", disposition="withdrawn")
    good = {6: "### 6.1 Code defects we will repair\n\n- **[CDF#1]** — x\n",
            7: "### 7.1 Questions held for you\n\n- **Re-puts:** [AS#3]\n\n### 7.3 Open assumptions\n\n"
               "- **[AS#1]** — a, unlike [AS#3]\n- **[AS#2]** — b\n",
            8: "### 8.1 Positions that could still move\n\n| Record | Depends on |\n|---|---|\n"
               "| `[VD#7]` — d, as [VD#11] decided | P-2 [CD#3] |\n\n"
               "### 8.2 Code defects whose scope is unsettled\n\n#### [CDF#2]\n\ny\n",
            9: "### 9.1 Open assumptions\n\n- **[AS#1]**–**[AS#2]**: both open\n\n#### [SR#3]\n\nattacks [AS#3]\n",
            11: "### 11.1 Code defects we will not repair\n\n1. [CDF#3] — z\n"}
    base = {"K-1-decisions.md": reg, "K-1-code-defect-log.md": cdl}
    r = run(dict(base, **{"K-1-customer-review-prompt-20261029.md": _sets_prompt(good)}), unreviewed=["P-2"])
    check("sets relation 1: six faithful enumerations pass — openers, a range, mentions and Re-puts read right",
          [x["verdict"] for x in r["relations"] if x["relation"] == 1] == ["pass"] * 6
          and r1(r, 9, "Open assumptions")["named"] == ["[AS#1]", "[AS#2]"])
    check("sets relation 1: a conditional_on a reviewed prerequisite, or a superseded one, is not in part 8's set",
          r1(r, 8, "Positions that could still move")["held"] == ["[VD#7]"])
    check("sets relation 1: a status inside an argumentation scalar is not the record's",
          "[AS#4]" not in r1(r, 7, "Open assumptions")["held"])
    r = run(dict(base, **{"K-1-customer-review-prompt-20261029.md": _sets_prompt()}), unreviewed=["P-2"])
    check("sets relation 1: sources with members under 'None' bodies are mismatches, by id",
          r1(r, 7, "Open assumptions")["missing"] == ["[AS#1]", "[AS#2]"] and r["mismatch"]
          and r1(r, 11, "Code defects we will not repair")["verdict"] == "mismatch")
    r = run({"K-1-customer-review-prompt-20261029.md": _sets_prompt()})
    check("sets relation 1: both sides empty is the ordinary pass",
          [x["verdict"] for x in r["relations"] if x["relation"] == 1] == ["pass"] * 6)
    inv = dict(good)
    inv[7] = "### 7.3 Open assumptions\n\n- [AS#1] — a\n- [AS#2] — b\n- [AS#5] — invented\n"
    inv[9] = "### 9.1 Open assumptions\n\n- [AS#1]–[AS#4] — four\n"
    r = run(dict(base, **{"K-1-customer-review-prompt-20261029.md": _sets_prompt(inv)}), unreviewed=["P-2"])
    check("sets relation 1: an invention is extra; a range expands to every id it spans",
          r1(r, 7, "Open assumptions")["extra"] == ["[AS#5]"]
          and r1(r, 9, "Open assumptions")["extra"] == ["[AS#3]", "[AS#4]"])
    r = run({"K-1-customer-review-prompt-20261029.md": _sets_prompt(
        {6: "### 6.1 Code defects we will repair\n\n- [CDF#2] — y\n"})})
    check("sets relation 1: a restatement over an absent source is unreadable, not a mismatch",
          r1(r, 6, "Code defects we will repair")["verdict"] == "unreadable" and r["unreadable"])
    msg = refused(lambda: run({"K-1-customer-review-prompt-20261029.md": _sets_prompt({9: "Nothing.\n"})}))
    check("sets relation 1: a missing sub-heading is refused, by part and title",
          bool(msg) and "part 9" in msg and "Open assumptions" in msg)
    def r2(r):
        return next(x for x in r["relations"] if x["relation"] == 2)

    pr = {"K-1-customer-review-prompt-20261029.md": _sets_prompt()}
    docs = ["K-1-customer-review-prompt-20261029.md", "K-1-decisions.md", "K-1-a.md", "K-1-baselines.md"]
    files = dict(pr, **{"K-1-decisions.md": "# Decision register: K-1\n", "K-1-a.md": "x\n", "K-1-wire.svg": "<svg/>",
                        "K-1-baselines.md": _sets_baselines([("app", SHA_A)])})
    r = run(dict(files, **{"K-1-manifest.md": _sets_manifest(docs)}))
    check("sets relation 2: the real manifest's shape passes — its own absence, an image line, the map table",
          r2(r)["verdict"] == "pass" and len(r2(r)["named"]) == 4)
    r = run(dict(files, **{"K-1-manifest.md": _sets_manifest(
        ["K-1-customer-review-prompt-20261029", "K-1-decisions", "K-1-a.md", "K-1-baselines"],
        "| `K-1-wire.svg` | i | yes |\n")}))
    check("sets relation 2: the extension either way matches, and an image row is out of scope",
          r2(r)["verdict"] == "pass")
    r = run(dict(files, **{"K-1-manifest.md": _sets_manifest(
        ["K-1-customer-review-prompt-20261029.md", "K-1-a.md", "K-1-baselines.md", "K-1-ghost.md"])}))
    check("sets relation 2: a document with no row is missing, a row with no document is extra",
          r2(r)["missing"] == ["K-1-decisions"] and r2(r)["extra"] == ["K-1-ghost"] and r2(r) in r["mismatch"])
    msg = refused(lambda: run(dict(files, **{"K-1-manifest.md": "# K-1 — bundle manifest\n\n- `K-1-a.md`\n"})))
    check("sets relation 2: a manifest with no Documents table is refused", bool(msg) and "Documents" in msg)
    def r3(r):
        return next(x for x in r["relations"] if x["relation"] == 3)

    two = {"K-1-baselines.md": _sets_baselines([("app", SHA_A), ("lib", SHA_B), ("app", SHA_A)])}
    wrapped = ("Pull `bundle-20261012/` today, 20261012, as defaced copies are\nnot ours. The `app` repository at commit\n"
               "`abcdef1` and the `lib` repository at commit `1234567`.\n")
    r = run(dict(pr, **two), note=wrapped)
    check("sets relation 3: a wrapped clause, an abbreviation, a commit recorded twice and an all-digit pin pass; "
          "a path, a date and a hex-letter word are no pin",
          r3(r)["verdict"] == "pass" and r["ambiguous"] == [] and len(r3(r)["named"]) == 2)
    r = run(dict(pr, **two), note="The `app` repository at commit `1234567` and the `lib` repository at commit `abcdef1`.\n")
    check("sets relation 3: a swapped pair is a mismatch", r3(r)["verdict"] == "mismatch" and len(r3(r)["extra"]) == 2)
    r = run(dict(pr, **two), note="The `app` repository at commit `abcdef1` and the `web` repository at commit `abcdef1`.\n")
    check("sets relation 3: a repository the baselines lack is extra, and one the note omits is missing",
          r3(r)["verdict"] == "mismatch" and [m.split()[0] for m in r3(r)["missing"]] == ["lib"]
          and [m.split()[0] for m in r3(r)["extra"]] == ["web"])
    amb = {"K-1-baselines.md": _sets_baselines([("app", SHA_A), ("app", "abcdef1999999999999999999999999999999999")])}
    r = run(dict(pr, **amb), note="The `app` repository at commit `abcdef1`.\n")
    check("sets relation 3: an abbreviation prefixing two different commits is ambiguous",
          [a["token"] for a in r["ambiguous"]] == ["abcdef1"])
    r = run(dict(pr, **{"K-1-baselines.md": "# Grounding baselines: K-1\n"}),
            note="The `app` repository at commit `abcdef1`.\n")
    check("sets relation 3: pins over a baselines file that yields none are unreadable", r3(r)["verdict"] == "unreadable")
    r = run(dict(pr, **{"K-1-baselines.md": "# Grounding baselines: K-1\n"}), note="No code was read.\n")
    check("sets relation 3: no pin and no baseline is the ordinary pass", r3(r)["verdict"] == "pass")
    r = run(dict(pr, **two), note="The `app` repository at commit `abcdef1`, the `lib` repository at commit "
                                 "`1234567`; also 9999999.\n")
    check("sets relation 3: a commit word outside a clause that prefixes no baseline is extra",
          r3(r)["extra"] == ["9999999"])
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "K-1-customer-review-prompt-20261029.md"), "w", encoding="utf-8") as fh:
            fh.write(_sets_prompt())
        with open(os.path.join(d, "K-1-manifest.md"), "w", encoding="utf-8") as fh:
            fh.write("## Documents\n\n| File | What | For review? |\n|---|---|---|\n"
                     "| `K-1-customer-review-prompt-20261029.md` | p | yes |\n")
        with open(os.path.join(d, "note.md"), "w", encoding="utf-8") as fh:
            fh.write("x\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(["sets", d, "--key", "K-1", "--date", "20261029", "--manifest", "K-1-manifest.md",
                         "--note", os.path.join(d, "note.md")])
    check("sets: the command line prints one line of JSON and exits 0",
          code == 0 and buf.getvalue().count("\n") == 1 and "relations" in json.loads(buf.getvalue()))


def selftest():
    cases, failed = 0, 0

    def check(label, cond):
        nonlocal cases, failed
        cases += 1
        print(("ok    " if cond else "FAIL  ") + label)
        if not cond:
            failed += 1

    fam = {"names": {"product-workflows", "workflows-core", "prose-style"},
           "commands": {"brd-package", "brd-intake", "design"}, "agents": {"brd-reader", "impl-maintenance"},
           "homes": {"/opt/mkt/plugins"}}

    def run(text, name="K-1-doc.md", **kw):
        kw.setdefault("fam", fam)
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
            return scan([d], **kw)

    def got(r, *keys):
        return [tuple(g[k] for k in keys) for g in r["groups"]]

    S = SECTION
    r = run("Read ${CLAUDE_PLUGIN_ROOT}/x, references/x.md, docs/superpowers/y.md and "
            "/home/u/.claude/plugins/cache/m/p/1/x.md and /opt/mkt/plugins/p/commands/x.md.\n")
    check("plugin-root paths, expanded ones included, and both citation forms are hits",
          [t for t, in got(r, "token")] == ["CLAUDE_PLUGIN_ROOT", "references/", "docs/superpowers/",
                                            ".claude/plugins/", "/opt/mkt/plugins"])
    r = run('Skill(skill: "workflows-core:reference") and subagent_type, prose-style:prose-style-checker\n')
    check("a Skill call, family namespaces and subagent_type are hits",
          got(r, "token") == [("Skill(skill:",), ("workflows-core:reference",), ("subagent_type",),
                              ("prose-style:prose-style-checker",)])
    r = run("Run /brd-package, /design, /prose-style:check; see brd-reader.md, impl-maintenance.md.\n")
    check("hyphenated family commands, namespaced commands and agent filenames are certain; a one-word command is not",
          got(r, "token", "certain") == [("/brd-package", True), ("/design", False),
                                         ("/prose-style:check", True), ("brd-reader.md", True),
                                         ("impl-maintenance.md", True)])
    r = run("The brd-reader and impl-maintenance agents.\n")
    check("an agent's bare name is uncertain",
          got(r, "token", "certain") == [("brd-reader", False), ("impl-maintenance", False)])
    r = run("The /ratings endpoint, /home/u/x, /a.json, https://h/a/b, and/or 1/2, </details>; polls /config.\n")
    check("an unknown leading-slash name is uncertain; paths, URLs, words and closing tags are not hits",
          got(r, "token", "certain") == [("/ratings", False), ("/config", False)])
    r = run("Then run /brd-intake.\n")
    check("a command at a sentence's end is certain", got(r, "token", "certain") == [("/brd-intake", True)])
    r = run("Load it with workflows-core:\nreference, or Skill(\n  skill: x).\n")
    check("a namespace or a Skill( call ending its line is a hit",
          got(r, "token") == [("workflows-core:",), ("Skill(",)])
    r = run("Per D12 and D3, not [DG#3], DEF#2 or 3D.\n")
    check("bare decision-row ids are hits, identifiers are not", got(r, "token") == [("D12",), ("D3",)])
    r = run("Ran on claude-opus-5-5[1m]; also claude-sonnet-4-6, claude-3-5-sonnet-20241022, claude-2.1.\n")
    check("model ids in every shape, with suffixes, are hits",
          got(r, "token") == [("claude-opus-5-5[1m]",), ("claude-sonnet-4-6",),
                              ("claude-3-5-sonnet-20241022",), ("claude-2.1",)])
    r = run("No bundle-20261012 date or abc1234 hash is a token.\n")
    check("a date and a hash are no hit", r["groups"] == [])
    cp = ["source/Customer BRD v2.md", "source/images/Q3 report.png"]
    r = run("See " + S + "3.4; source/Customer BRD v2.md › " + S + " 2 Monthly › " + S
            + " 2.1 D3 Columns`, and D4.\n## source/images/Q3 report.png\n", captured_paths=cp)
    check("a captured path with a space: its tail's opening section omitted, the rest of the tail placed",
          got(r, "token", "span") == [(S, "none"), (S, "locator-tail"), ("D3", "locator-tail"),
                                      ("D4", "none")] and r["omitted_locator_sections"] == 1)
    r = run("In source/Customer BRD v2.md › " + S + " 3 Totals, should D3 hold? Run /brd-package; see brd-reader.md.\n",
            captured_paths=cp)
    check("a certain command or agent name in a tail is placed as if no tail were there",
          got(r, "token", "span") == [("D3", "locator-tail"), ("/brd-package", "none"), ("brd-reader.md", "none")])
    r = run("source/other.md › " + S + " 2\n", captured_paths=cp)
    check("a source/ path naming no captured file is no locator",
          got(r, "token", "span") == [(S, "none")] and r["omitted_locator_sections"] == 0)
    inv = ("| id | text | source_anchor | defects |\n|---|---|---|---|\n"
           "| [BR#1] | Uses claude-sonnet-4-6 per D3 | " + S + " 2 Monthly | [DEF#1] |\n"
           "| [BR#2] | Net total per D4 | source/images/r.png › \"D5 total\" | |\n"
           "| [BR#3] | a \\| D6 inside | x | |\n")
    r = run(inv, name="K-1-brd-inventory.md", captured_paths=["source/images/r.png"])
    check("inventory text and anchor cells are placed, an anchor's opening section omitted",
          got(r, "token", "span", "image_row") == [
              ("claude-sonnet-4-6", "inventory-text", False), ("D3", "inventory-text", False),
              ("D4", "inventory-text", True), ("D5", "locator-tail", None), ("D6", "inventory-text", False)]
          and r["omitted_locator_sections"] == 1)
    led = ("| id | text | disposition | defects | evidence |\n|---|---|---|---|---|\n"
           "| [BR#1] | per D3 | unallocated | | |\n\nAfter the table, D9.\n")
    r = run(led, name="K-1-coverage-ledger.md")
    check("a ledger text cell is placed, text after the table is not",
          got(r, "token", "span", "image_row") == [("D3", "ledger-text", None), ("D9", "none", None)])
    r = run("Their D3 and claude-opus-5-5.\n", name="K-1-brief.md", captured=["K-1-brief.md"])
    check("every hit in a captured file is captured-file",
          got(r, "span") == [("captured-file",), ("captured-file",)])
    r = run("Ran on claude-opus-5-5. | [BR#1] | per D3 | unallocated | | |\n", name="P-2-x.md",
            prereq_keys=["P-2"])
    check("a prerequisite's file is flagged and its spans still computed",
          got(r, "token", "span", "prerequisite") == [("claude-opus-5-5", "none", True), ("D3", "none", True)])
    r = run("Their " + S + " 4.\n", name="P-2-brief.md", prereq_keys=["P-2"], captured=["P-2-brief.md"])
    check("a prerequisite's captured file is captured-file and prerequisite",
          got(r, "span", "prerequisite") == [("captured-file", True)])
    r = run("Ran on claude-opus-5-5.\n", name="P-22-x.md", prereq_keys=["P-2"])
    check("a key is a prefix only at a segment boundary", got(r, "prerequisite") == [(False,)])
    r = run("See K-1-notes" + S + "2.md, and " + S + " here; not K-1-D3-notes.md.\n",
            captured=["K-1-notes" + S + "2.md"])
    check("a hit inside a captured file's bundled name is a locator; -D3- in a name is no bare id",
          got(r, "token", "span") == [(S, "locator"), (S, "none")])
    r = run("D3 and D3\nD3\n")
    check("hits group by file, token and span with their lines",
          r["groups"] == [{"file": "K-1-doc.md", "token": "D3", "class": "decision-row", "span": "none",
                           "prerequisite": False, "image_row": None, "certain": True, "count": 3,
                           "lines": [1, 1, 2]}])
    r = run("D7\n", name="K-1-notes.MARKDOWN")
    check("a .markdown document is scanned", r["files"] == 1 and got(r, "token") == [("D7",)])
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "K-1-bad.md"), "wb") as f:
            f.write(b"\xff\xfe D3\n")
        try:
            scan([d], fam=fam)
            check("a file that is not UTF-8 is refused", False)
        except Refused:
            check("a file that is not UTF-8 is refused", True)
    try:
        scan(["/nonexistent/bundle-scan-selftest"], fam=fam)
        check("a missing path is refused", False)
    except Refused:
        check("a missing path is refused", True)
    with tempfile.TemporaryDirectory() as d:
        for p in ("plugins/a-workflows", "plugins/b"):
            os.makedirs(os.path.join(d, p, ".claude-plugin"))
            os.makedirs(os.path.join(d, p, "agents"))
        with open(os.path.join(d, "plugins/a-workflows/.claude-plugin/plugin.json"), "w") as f:
            f.write('{"name": "a-workflows"}')
        with open(os.path.join(d, "plugins/b/.claude-plugin/plugin.json"), "w") as f:
            f.write('{"name": "b"}')
        open(os.path.join(d, "plugins/b/agents/b-agent.md"), "w").close()
        os.makedirs(os.path.join(d, "cache/m/c/1.0/.claude-plugin"))
        with open(os.path.join(d, "cache/m/c/1.0/.claude-plugin/plugin.json"), "w") as f:
            f.write('{"name": "c"}')
        open(os.path.join(d, "plugins/b/agents/x.md"), "w").close()
        src = family(os.path.join(d, "plugins/a-workflows"))
        cache = family(os.path.join(d, "cache/m/c/1.0"))
        check("the family is read from the source tree and from the install cache",
              src["names"] == {"a-workflows", "b"} and src["agents"] == {"b-agent", "x"}
              and "c" in cache["names"])
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "K-1-a.md"), "w", encoding="utf-8") as f:
            f.write("D1\n")
        with contextlib.redirect_stdout(buf):
            code = main(["tokens", d])
    out = buf.getvalue()
    check("the command line prints one line of JSON and exits 0",
          code == 0 and out.count("\n") == 1 and json.loads(out)["groups"][0]["token"] == "D1")
    fam_here = family()
    check("this plugin's family is found", "product-workflows" in fam_here["names"]
          and "brd-package" in fam_here["commands"] and "brd-reader" in fam_here["agents"])
    citations_selftest(check)
    sets_selftest(check)
    print("SELFTEST " + ("PASS" if not failed else "FAIL") + " (%d cases, %d failed)" % (cases, failed))
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bundle-scan.py")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("tokens")
    t.add_argument("paths", nargs="+")
    t.add_argument("--prereq-key", action="append", default=[])
    t.add_argument("--captured", action="append", default=[])
    t.add_argument("--captured-path", action="append", default=[])
    c = sub.add_parser("citations")
    c.add_argument("bundle")
    c.add_argument("--key", required=True)
    c.add_argument("--prereq-key", action="append", default=[])
    c.add_argument("--copied-key", action="append", default=[])
    c.add_argument("--date")
    c.add_argument("--captured", action="append", default=[])
    c.add_argument("--captured-path", action="append", default=[])
    c.add_argument("--source-basename", action="append", default=[])
    c.add_argument("--manifest")
    c.add_argument("--known-key", action="append", default=[])
    c.add_argument("--prereq-aux", action="append", default=[])
    s = sub.add_parser("sets")
    s.add_argument("bundle")
    s.add_argument("--key", required=True)
    s.add_argument("--date", required=True)
    s.add_argument("--manifest", required=True)
    s.add_argument("--note", required=True)
    s.add_argument("--unreviewed-prereq", action="append", default=[])
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd not in ("tokens", "citations", "sets"):
        ap.print_usage(sys.stderr)
        return 2
    try:
        if a.cmd == "sets":
            result = sets(a.bundle, a.key, a.date, a.manifest, a.note, a.unreviewed_prereq)
        elif a.cmd == "citations":
            result = citations(a.bundle, a.key, a.prereq_key, a.copied_key, a.date, a.captured,
                               a.captured_path, a.source_basename, a.manifest, a.known_key, a.prereq_aux)
        else:
            result = scan(a.paths, a.prereq_key, a.captured, a.captured_path)
    except Refused as e:
        print("bundle-scan.py: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""bundle-scan.py — the plugin-free scan /brd-package runs over its prompt, its delivery note and its bundle.

  bundle-scan.py tokens <file-or-directory>... [--prereq-key KEY]... [--captured NAME]...
                        [--captured-path PATH]...
  bundle-scan.py --selftest

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
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd != "tokens":
        ap.print_usage(sys.stderr)
        return 2
    try:
        result = scan(a.paths, a.prereq_key, a.captured, a.captured_path)
    except Refused as e:
        print("bundle-scan.py: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main())

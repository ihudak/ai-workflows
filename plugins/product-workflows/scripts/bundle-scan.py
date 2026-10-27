#!/usr/bin/env python3
"""bundle-scan.py — the plugin-free scan /brd-package runs over its prompt, its delivery note and its bundle.

  bundle-scan.py tokens <file-or-directory>... [--prereq-key KEY]... [--captured NAME]...
  bundle-scan.py --selftest

tokens: reads every given file, and every *.md file under every given directory, and reports each
token of a class the plugin's bundle-packaging reference tabulates in section 1.2 -- a path rooted at
the plugin's install directory, a reference-file citation, a section sign, a slash command, an agent,
subagent type or skill name, a bare decision-row id, a model id. It finds tokens; it never decides
whether the package may ship. Each hit carries the span the script can place it in by position alone,
and the caller rules on the rest:

  captured-file   the file is one of --captured, the customer's own file copied byte for byte
  prerequisite    the file's name begins with a --prereq-key key and "-": a prerequisite's package
  inventory-text  the text cell of an inventory row (id | text | source_anchor | defects)
  ledger-text     the text cell of a coverage-ledger row (id | text | disposition | defects | evidence)
  anchor          the source_anchor cell of an inventory row
  locator         inside a captured path (source/... or source-external/...) or a --captured name
  none            none of these

An inventory or ledger text hit carries image_row: true where the row's source_anchor names an image
before its first " > " (the separator is the U+203A character), false where it names none, and null
on a ledger row, which carries no anchor. A section sign that opens a source_anchor cell, or that
opens what follows the separator after a captured path, is no hit (bundle-packaging section 6.3
rule 1); each is counted in omitted_locator_sections and reported nowhere else.

A slash command is certain where it is namespaced by a *workflows* plugin or names one of this
plugin's own commands; any other leading-slash name is reported with certain: false, since its shape
cannot tell a command from a route the customer's own code names. Every other class is certain.

Prints {"files": N, "hits": [...], "groups": [...], "omitted_locator_sections": N}. Each hit is
{file, line, class, token, span, certain, image_row}; file is the path relative to the directory it
was found under, or the file's own name where a file was given. groups holds one entry per file,
token and span, with its class, its count and its lines, in the order of their first hit -- the
grouping bundle-packaging section 6.3 rule 4 asks of every report.

Tables split into cells on every delimiting "|" -- one that opens the row or has a space directly
before it -- as the plugin's brd-format reference, section 2.3, fixes; a "|" with no space before it
is inside a cell. A token never spans two lines.

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
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tif", ".tiff")
INVENTORY_HEADER = ["id", "text", "source_anchor", "defects"]
LEDGER_HEADER = ["id", "text", "disposition", "defects", "evidence"]
SEPARATOR_RE = re.compile(r"[ \t]*\|(?:[ \t]*:?-+:?[ \t]*\|)+[ \t]*$")
CAPTURED_PATH_RE = re.compile(r"(?<![\w/.-])source(?:-external)?/[^\s`|)\]>\"']+")


class Refused(Exception):
    """An input cannot be read; main() prints the message and exits 2."""


def _stems(sub):
    d = os.path.join(PLUGIN_ROOT, sub)
    try:
        return sorted(n[:-3] for n in os.listdir(d) if n.endswith(".md"))
    except OSError:
        return []


def _patterns(commands, agents):
    """Each class's patterns, as (class, regex, certain)."""
    ns = r"[a-z0-9-]*workflows[a-z0-9-]*"
    pats = [
        ("plugin-root-path", re.compile(r"CLAUDE_PLUGIN_ROOT"), True),
        ("reference-citation", re.compile(r"(?<![\w-])references/"), True),
        ("reference-citation", re.compile(r"docs/superpowers/"), True),
        ("reference-citation", re.compile(r"Skill\(\s*skill\s*:"), True),
        ("section-sign", re.compile("§"), True),
        ("slash-command", re.compile(r"(?<![\w/.:~)\]-])/" + ns + r":[A-Za-z][\w-]*"), True),
        ("agent-or-skill", re.compile(r"subagent_type"), True),
        ("agent-or-skill", re.compile(r"(?<![\w/:-])" + ns + r":[A-Za-z][\w-]*"), True),
        ("decision-row", re.compile(r"(?<![\w#-])D[0-9]+(?![\w#])"), True),
        ("model-id", re.compile(
            r"(?<![\w-])claude-(?:[a-z]+-[0-9]+(?:[-.][0-9]+)*|[0-9]+(?:[-.][0-9]+)*-[a-z]+)"
            r"(?:-[0-9]{8})?(?:\[[^\]\s]*\])?"), True),
    ]
    if commands:
        alt = "|".join(re.escape(c) for c in commands)
        pats.append(("slash-command", re.compile(r"(?<![\w/.:~)\]-])/(?:" + alt + r")(?![\w/-])(?!\.\w)"), True))
    pats.append(("slash-command", re.compile(r"(?<![\w/.:~)\]-])/[a-z][a-z0-9-]*(?![\w/:-])(?!\.\w)"), False))
    if agents:
        alt = "|".join(re.escape(a) for a in agents)
        pats.append(("agent-or-skill", re.compile(r"(?<![\w-])(?:" + alt + r")\.md(?![\w])"), True))
    return pats


def _delimiters(line):
    """Offsets of every delimiting '|' in a table line (brd-format section 2.3, rule 1)."""
    out = []
    for i, ch in enumerate(line):
        if ch == "|" and (not line[:i].strip() or line[i - 1] == " "):
            out.append(i)
    return out


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


def _locator_ranges(line, captured):
    """(start, end) of every captured path, and of every --captured name, in a line."""
    out = [(m.start(), m.end()) for m in CAPTURED_PATH_RE.finditer(line)]
    for name in captured:
        for m in re.finditer(r"(?<![\w.-])" + re.escape(name) + r"(?![\w-])", line):
            out.append((m.start(), m.end()))
    return out


def _rule1_sections(line, row):
    """Offsets of every section sign in a locator's fixed position (section 6.3 rule 1)."""
    out = set()
    for m in CAPTURED_PATH_RE.finditer(line):
        rest = line[m.end():]
        if rest.startswith(SEP):
            j = m.end() + len(SEP)
            while j < len(line) and line[j] == " ":
                j += 1
            if line[j:j + 1] == "§":
                out.add(j)
    if row and row[0] == "inventory" and len(row[1]) == 4:
        start, end, _ = row[1][2]
        j = start
        while j < end and line[j] == " ":
            j += 1
        if line[j:j + 1] == "§":
            out.add(j)
    return out


def scan_text(name, text, pats, prereq_keys, captured):
    """(hits, omitted) for one file's text."""
    lines = text.split("\n")
    rows = _table_kinds(lines)
    base = os.path.basename(name)
    file_span = None
    if base in captured:
        file_span = "captured-file"
    elif any(base.startswith(k + "-") for k in prereq_keys):
        file_span = "prerequisite"
    hits, omitted = [], 0
    for i, line in enumerate(lines):
        row = rows.get(i)
        skip = _rule1_sections(line, row)
        locs = _locator_ranges(line, captured)
        seen = set()
        found = []
        for cls, rx, certain in pats:
            for m in rx.finditer(line):
                if (m.start(), m.end()) in seen:
                    continue
                if cls == "section-sign" and m.start() in skip:
                    omitted += 1
                    continue
                seen.add((m.start(), m.end()))
                found.append((m.start(), m.end(), cls, certain))
        # a certain slash command shadows the uncertain reading of the same token
        certain_at = {(a, b) for a, b, c, k in found if c == "slash-command" and k}
        found = [f for f in found if not (f[2] == "slash-command" and not f[3]
                                         and any(a <= f[0] < b for a, b in certain_at))]
        for a, b, cls, certain in sorted(found):
            span, image_row = file_span or "none", None
            if not file_span:
                if any(s <= a < e for s, e in locs):
                    span = "locator"
                elif row:
                    kind, cells = row
                    width = 4 if kind == "inventory" else 5
                    if len(cells) == width:
                        if cells[1][0] <= a < cells[1][1]:
                            span = kind + "-text"
                            image_row = _image_anchor(cells[2][2]) if kind == "inventory" else None
                        elif kind == "inventory" and cells[2][0] <= a < cells[2][1]:
                            span = "anchor"
            hits.append({"file": name, "line": i + 1, "class": cls, "token": line[a:b],
                         "span": span, "certain": certain, "image_row": image_row})
    return hits, omitted


def _files(paths):
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, names in os.walk(p):
                dirs.sort()
                for n in sorted(names):
                    if n.endswith(".md"):
                        full = os.path.join(root, n)
                        out.append((os.path.relpath(full, p), full))
        elif os.path.isfile(p):
            out.append((os.path.basename(p), p))
        else:
            raise Refused("no such file or directory: " + p)
    return out


def scan(paths, prereq_keys=(), captured=(), commands=None, agents=None):
    pats = _patterns(_stems("commands") if commands is None else commands,
                     _stems("agents") if agents is None else agents)
    files = _files(paths)
    hits, omitted = [], 0
    for name, full in files:
        try:
            with open(full, encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            raise Refused("cannot read " + name + " as UTF-8: " + e.__class__.__name__)
        h, o = scan_text(name, text, pats, list(prereq_keys), set(captured))
        hits.extend(h)
        omitted += o
    groups, index = [], {}
    for h in hits:
        k = (h["file"], h["token"], h["span"])
        if k not in index:
            index[k] = {"file": h["file"], "token": h["token"], "class": h["class"], "span": h["span"],
                        "certain": h["certain"], "count": 0, "lines": []}
            groups.append(index[k])
        index[k]["count"] += 1
        index[k]["lines"].append(h["line"])
    return {"files": len(files), "hits": hits, "groups": groups, "omitted_locator_sections": omitted}


def selftest():
    cases, failed = 0, 0

    def check(label, cond):
        nonlocal cases, failed
        cases += 1
        if not cond:
            failed += 1
            print("FAIL  " + label)
        else:
            print("ok    " + label)

    def run(text, name="K-1-doc.md", **kw):
        kw.setdefault("commands", ["brd-package", "brd-intake"])
        kw.setdefault("agents", ["brd-reader"])
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, name), "w", encoding="utf-8") as f:
                f.write(text)
            return scan([d], **kw)

    def classes(r):
        return [(h["class"], h["token"]) for h in r["hits"]]

    S = "§"
    r = run("Read ${CLAUDE_PLUGIN_ROOT}/references/x.md and docs/superpowers/specs/y.md.\n")
    check("a plugin-root path and both citation forms are hits",
          ("plugin-root-path", "CLAUDE_PLUGIN_ROOT") in classes(r)
          and ("reference-citation", "references/") in classes(r)
          and ("reference-citation", "docs/superpowers/") in classes(r))
    r = run('Skill(skill: "workflows-core:reference", args: "x") and subagent_type\n')
    check("a Skill call, a workflows namespace and subagent_type are hits",
          ("reference-citation", "Skill(skill:") in classes(r)
          and ("agent-or-skill", "workflows-core:reference") in classes(r)
          and ("agent-or-skill", "subagent_type") in classes(r))
    r = run("Run /brd-package, then /dev-workflows:design; see brd-reader.md.\n")
    check("own commands, namespaced commands and agent filenames are certain hits",
          [(h["token"], h["certain"]) for h in r["hits"]]
          == [("/brd-package", True), ("/dev-workflows:design", True), ("brd-reader.md", True)])
    r = run("The /ratings endpoint, at /home/u/x, /a.json and https://h/a/b, and and/or 1/2; polls /config.\n")
    check("an unknown leading-slash name is uncertain, at a sentence's end too; paths, URLs and words are not hits",
          [(h["token"], h["certain"]) for h in r["hits"]] == [("/ratings", False), ("/config", False)])
    r = run("Then run /brd-intake.\n")
    check("an own command at a sentence's end is certain", [(h["token"], h["certain"]) for h in r["hits"]]
          == [("/brd-intake", True)])
    r = run("Per D12 and D3, not [DG#3], DEF#2 or 3D.\n")
    check("bare decision-row ids are hits, identifiers are not",
          [h["token"] for h in r["hits"]] == ["D12", "D3"])
    r = run("Ran on claude-opus-5-5[1m]; also claude-sonnet-4-6 and claude-3-5-sonnet-20241022.\n")
    check("model ids in both shapes, with suffixes, are hits",
          [h["token"] for h in r["hits"]] == ["claude-opus-5-5[1m]", "claude-sonnet-4-6",
                                              "claude-3-5-sonnet-20241022"])
    r = run("No bundle-20261012 date or abc1234 hash is a token.\n")
    check("a date and a hash are no hit", r["hits"] == [])
    r = run("See " + S + "3.4 and source/brd.md " + "› " + S + " 2 Monthly report.\n")
    check("a section sign after a captured path's separator is omitted, any other is a hit",
          [h["token"] for h in r["hits"]] == [S] and r["omitted_locator_sections"] == 1)
    inv = ("| id | text | source_anchor | defects |\n|---|---|---|---|\n"
           "| [BR#1] | Uses claude-sonnet-4-6 per D3 | " + S + " 2 Monthly | [DEF#1] |\n"
           "| [BR#2] | Net total per D4 | source/images/r.png › \"D5 total\" | |\n"
           "| [BR#3] | a \\| D6 inside | x | |\n")
    r = run(inv, name="K-1-brd-inventory.md")
    got = [(h["token"], h["span"], h["image_row"]) for h in r["hits"]]
    check("inventory text and anchor cells are placed, an anchor's opening section omitted",
          got == [("claude-sonnet-4-6", "inventory-text", False), ("D3", "inventory-text", False),
                  ("D4", "inventory-text", True), ("D5", "anchor", None),
                  ("D6", "inventory-text", False)]
          and r["omitted_locator_sections"] == 1)
    led = ("| id | text | disposition | defects | evidence |\n|---|---|---|---|---|\n"
           "| [BR#1] | per D3 | unallocated | | |\n\nAfter the table, D9.\n")
    r = run(led, name="K-1-coverage-ledger.md")
    check("a ledger text cell is placed, text after the table is not",
          [(h["token"], h["span"], h["image_row"]) for h in r["hits"]]
          == [("D3", "ledger-text", None), ("D9", "none", None)])
    r = run("Their D3 and claude-opus-5-5.\n", name="K-1-brief.md", captured=["K-1-brief.md"])
    check("every hit in a captured file is captured-file",
          {h["span"] for h in r["hits"]} == {"captured-file"} and len(r["hits"]) == 2)
    r = run("Ran on claude-opus-5-5, per D3.\n", name="P-2-grounding.md", prereq_keys=["P-2"])
    check("every hit in a prerequisite's file is prerequisite",
          [(h["token"], h["span"]) for h in r["hits"]] == [("claude-opus-5-5", "prerequisite"),
                                                           ("D3", "prerequisite")])
    r = run("Ran on claude-opus-5-5.\n", name="P-22-x.md", prereq_keys=["P-2"])
    check("a key is a prefix only at a segment boundary", r["hits"][0]["span"] == "none")
    r = run("See K-1-notes" + S + "2.md, and " + S + " here; not K-1-D3-notes.md.\n",
            captured=["K-1-notes" + S + "2.md"])
    check("a hit inside a captured file's bundled name is a locator; -D3- in a name is no bare id",
          [(h["token"], h["span"]) for h in r["hits"]] == [(S, "locator"), (S, "none")])
    r = run("D3 and D3\nD3\n")
    check("hits group by file, token and span with their lines",
          r["groups"] == [{"file": "K-1-doc.md", "token": "D3", "class": "decision-row", "span": "none",
                           "certain": True, "count": 3, "lines": [1, 1, 2]}])
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "K-1-bad.md")
        with open(p, "wb") as f:
            f.write(b"\xff\xfe D3\n")
        try:
            scan([d], commands=[], agents=[])
            check("a file that is not UTF-8 is refused", False)
        except Refused:
            check("a file that is not UTF-8 is refused", True)
    try:
        scan(["/nonexistent/bundle-scan-selftest"], commands=[], agents=[])
        check("a missing path is refused", False)
    except Refused:
        check("a missing path is refused", True)
    buf = io.StringIO()
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "K-1-a.md"), "w", encoding="utf-8") as f:
            f.write("D1\n")
        with contextlib.redirect_stdout(buf):
            code = main(["tokens", d])
    out = json.loads(buf.getvalue())
    check("the command line prints the JSON and exits 0", code == 0 and out["files"] == 1
          and out["hits"][0]["token"] == "D1")
    check("this plugin's own command and agent names are found", "brd-package" in _stems("commands")
          and "brd-reader" in _stems("agents"))
    print("SELFTEST " + ("PASS" if not failed else "FAIL") + " (%d cases, %d failed)" % (cases, failed))
    return 0 if not failed else 1


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bundle-scan.py", add_help=True)
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    t = sub.add_parser("tokens")
    t.add_argument("paths", nargs="+")
    t.add_argument("--prereq-key", action="append", default=[])
    t.add_argument("--captured", action="append", default=[])
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd != "tokens":
        ap.print_usage(sys.stderr)
        return 2
    try:
        result = scan(a.paths, a.prereq_key, a.captured)
    except Refused as e:
        print("bundle-scan.py: " + str(e), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

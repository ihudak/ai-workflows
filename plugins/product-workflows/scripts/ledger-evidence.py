#!/usr/bin/env python3
"""ledger-evidence.py — writes the evidence column of one coverage ledger from a map of [BR#n] to finding ids.

  ledger-evidence.py write --ledger <coverage-ledger.md>     (the map, one JSON object, on standard input)
  ledger-evidence.py --selftest

write: reads the map -- {"[BR#n]": ["[CG#n]", "[DG#n]", ...], ...} -- and rewrites the evidence cell of
every row of the ledger's table: a row the map names takes its ids, every [CG#n] by number and then
every [DG#n] by number, separated by ", "; a row the map does not name, or names with an empty list,
takes an empty cell, one space between its delimiters. Every other cell, and every line that is not a
row of the table, keeps every byte. A row splits into cells on every delimiting "|" -- one that opens
the row or has a space directly before it -- and never on " | ", which merges an empty cell with its
neighbour. Prints {"written": true|false, "rows": N, "with_evidence": N, "empty": N}; written is
false where no byte changed, and the file is then left untouched.

It refuses, and writes nothing, on: no table, or a header that is not the five columns id, text,
disposition, defects, evidence, in that order, with a separator line under it; a row whose cell count
differs from the header's, or with text after its last delimiting "|"; a row whose id is not one
[BR#n], or an id two rows hold; a table row after the table has ended; a map that is not one JSON
object naming each key once; a key that is not a [BR#n], or one naming a [BR#n] the ledger has no row
for; and a value that is not a list of well-formed [CG#n] and [DG#n] ids naming each once. A header's
names and a row's id are read with the whitespace around them ignored, so a ledger written before its
layout was fixed, its cells padded, is read where its rows still split by the rule.

The row shape and the id order are the plugin's coverage-ledger-format reference, section 2; the
cell encoding and the split are its brd-format reference, section 2.3. Python standard library only.

Exit 0: it ran -- written or unchanged. Exit 2: it refused or could not run, and wrote nothing; the
cause is on stderr. No output names a path.
"""

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile

COLUMNS = ["id", "text", "disposition", "defects", "evidence"]
EVIDENCE = COLUMNS.index("evidence")
ROW_ID_RE = re.compile(r"\[BR#[1-9][0-9]*\]")
FINDING_RE = re.compile(r"\[(CG|DG)#([1-9][0-9]*)\]")
SEPARATOR_RE = re.compile(r"[ \t]*\|(?:[ \t]*:?-+:?[ \t]*\|)+[ \t]*")
TABLE_LINE_RE = re.compile(r"[ \t]*\|")


class Refused(Exception):
    """The ledger or the map cannot be written by the rule; main() prints the message and exits 2."""


def _read(path):
    try:
        with open(path, encoding="utf-8", newline="") as fh:
            return fh.read()
    except UnicodeDecodeError:
        raise Refused("the ledger is not UTF-8 text")
    except OSError as e:
        raise Refused("cannot read the ledger: %s" % (e.strerror or type(e).__name__))


def _write_text(path, text):
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
    except OSError as e:
        raise Refused("cannot write the ledger: %s" % (e.strerror or type(e).__name__))


def _lines(text):
    """(content, line ending) per line; the ending is "\\r\\n", "\\n" or "" and joins back byte for byte."""
    out = []
    for raw in re.findall(r"[^\n]*\n|[^\n]+$", text):
        if raw.endswith("\r\n"):
            out.append((raw[:-2], "\r\n"))
        elif raw.endswith("\n"):
            out.append((raw[:-1], "\n"))
        else:
            out.append((raw, ""))
    return out


def _delimiters(line):
    """Offsets of every delimiting | of a table line: the one opening it, and each with a space directly before it."""
    first = len(line) - len(line.lstrip(" \t"))
    return [i for i, ch in enumerate(line) if ch == "|" and (i == first or line[i - 1] == " ")]


def _split(line):
    """(delimiter offsets, closed cells, text after the last delimiter)."""
    delims = _delimiters(line)
    cells = [line[a + 1:b] for a, b in zip(delims, delims[1:])]
    return delims, cells, line[delims[-1] + 1:] if delims else line


def _name(cell):
    """A header name or a row id: the cell decoded (one space each side dropped) and its padding ignored."""
    if cell.startswith(" "):
        cell = cell[1:]
    if cell.endswith(" "):
        cell = cell[:-1]
    return cell.strip()


def _order(fid):
    m = FINDING_RE.fullmatch(fid)
    return (0 if m.group(1) == "CG" else 1, int(m.group(2)))


def parse_map(text):
    """The map on standard input: one JSON object, each [BR#n] key once."""
    def pairs(items):
        seen = {}
        for key, value in items:
            if key in seen:
                raise Refused("the map names %s twice" % key)
            seen[key] = value
        return seen

    try:
        mapping = json.loads(text, object_pairs_hook=pairs)
    except ValueError as e:
        raise Refused("the map on standard input is not JSON: %s" % e)
    if not isinstance(mapping, dict):
        raise Refused("the map on standard input is not a JSON object of [BR#n] to a list of finding ids")
    return mapping


def _check_map(mapping):
    for key, value in mapping.items():
        if not isinstance(key, str) or not ROW_ID_RE.fullmatch(key):
            raise Refused("the map key %s is not a [BR#n]" % json.dumps(key))
        if not isinstance(value, list):
            raise Refused("the map value for %s is not a list of [CG#n] and [DG#n] ids: %s" % (key, json.dumps(value)))
        for fid in value:
            if not isinstance(fid, str) or not FINDING_RE.fullmatch(fid):
                raise Refused("the map value for %s holds %s, which is not one well-formed [CG#n] or [DG#n] id"
                              % (key, json.dumps(fid)))
        dupes = sorted({fid for fid in value if value.count(fid) > 1}, key=_order)
        if dupes:
            raise Refused("the map value for %s names %s more than once" % (key, ", ".join(dupes)))


def _table(lines):
    """Index of the header line and of every row line; refuses a ledger whose table the rule cannot read."""
    start = 0
    if lines and lines[0][0] == "---":
        for i in range(1, len(lines)):
            if lines[i][0] in ("---", "..."):
                start = i + 1
                break
        else:
            raise Refused("its frontmatter opens with --- and never closes, so it holds no table")
    header = next((i for i in range(start, len(lines)) if TABLE_LINE_RE.match(lines[i][0])), None)
    if header is None:
        raise Refused("the ledger holds no table")
    delims, cells, rest = _split(lines[header][0])
    names = [_name(c) for c in cells]
    if names != COLUMNS or rest.strip():
        raise Refused("the header at line %d reads %s, not the five columns %s in that order"
                      % (header + 1, json.dumps(names), " | ".join(COLUMNS)))
    if header + 1 >= len(lines) or not SEPARATOR_RE.fullmatch(lines[header + 1][0]):
        raise Refused("the header at line %d has no separator line under it" % (header + 1))
    rows = []
    i = header + 2
    while i < len(lines) and TABLE_LINE_RE.match(lines[i][0]):
        rows.append(i)
        i += 1
    for j in range(i, len(lines)):
        if TABLE_LINE_RE.match(lines[j][0]):
            raise Refused("line %d is a table row after the table ended at line %d" % (j + 1, i))
    return header, rows


def write(ledger_path, mapping):
    """Rewrites every row's evidence cell from the map; writes nothing and raises Refused where it cannot."""
    _check_map(mapping)
    text = _read(ledger_path)
    lines = _lines(text)
    _header, row_lines = _table(lines)
    seen = {}
    parsed = []
    for i in row_lines:
        content = lines[i][0]
        delims, cells, rest = _split(content)
        if len(cells) != len(COLUMNS):
            raise Refused("the row at line %d has %d cells; the header has %d" % (i + 1, len(cells), len(COLUMNS)))
        if rest.strip():
            raise Refused("the row at line %d has text after its last delimiting |" % (i + 1))
        rid = _name(cells[0])
        if not ROW_ID_RE.fullmatch(rid):
            raise Refused("the row at line %d has the id %s, which is not a [BR#n]" % (i + 1, json.dumps(rid)))
        if rid in seen:
            raise Refused("%s is the id of two rows, at lines %d and %d" % (rid, seen[rid] + 1, i + 1))
        seen[rid] = i
        parsed.append((i, rid, delims))
    missing = sorted((key for key in mapping if key not in seen), key=lambda k: int(k[4:-1]))
    if missing:
        raise Refused("the map names %s, which no row of the ledger holds" % ", ".join(missing))
    filled = 0
    for i, rid, delims in parsed:
        ids = sorted(mapping.get(rid, []), key=_order)
        filled += bool(ids)
        cell = " %s " % ", ".join(ids) if ids else " "
        content = lines[i][0]
        lines[i] = (content[:delims[EVIDENCE] + 1] + cell + content[delims[EVIDENCE + 1]:], lines[i][1])
    new = "".join(content + end for content, end in lines)
    written = new != text
    if written:
        _write_text(ledger_path, new)
    return {"written": written, "rows": len(parsed), "with_evidence": filled, "empty": len(parsed) - filled}


# ---- self-test ----

def _put(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _get(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return fh.read()


HEAD = "---\nkind: coverage-ledger\nkey: KEY-1-01\n---\n\n# Coverage ledger: KEY-1-01\n\n"
HEADER = "| id | text | disposition | defects | evidence |\n|---|---|---|---|---|\n"


def _ledger(tmp, rows, head=HEAD, header=HEADER, tail=""):
    path = os.path.join(tmp, "coverage-ledger.md")
    _put(path, head + header + "".join(rows) + tail)
    return path


def _cells(line):
    """The decoded cells of a row the way brd-format §2.3 reads one, for the assertions below."""
    line = line.rstrip("\n").rstrip("\r")
    first = len(line) - len(line.lstrip(" \t"))
    delims = [i for i, ch in enumerate(line) if ch == "|" and (i == first or line[i - 1] == " ")]
    return [line[a + 1:b][1:-1] for a, b in zip(delims, delims[1:])]


def _row(text, rid):
    for line in text.split("\n"):
        if line.startswith("|") and line[1:].split("|")[0].strip() == rid:
            return line
    raise AssertionError("no row %s in:\n%s" % (rid, text))


def _refused(fn, *args, want):
    try:
        fn(*args)
    except Refused as e:
        assert want in str(e), "refusal %r does not say %r" % (str(e), want)
        return str(e)
    raise AssertionError("not refused; wanted a refusal saying %r" % want)


def case_an_empty_defects_cell_keeps_its_column(tmp):
    # The observed failure, twice: a run split each row on " | ", which merged the empty defects
    # cell `| |` with its neighbour, so the new ids landed in `defects`.
    rows = [
        "| [BR#1] | The report lists every invoice. | unallocated | [DEF#1], [DEF#2] | |\n",
        "| [BR#6] | The page shows the count. | unallocated | | |\n",
        "| [BR#9] | A customer may change it at any time. | unallocated | | |\n",
    ]
    assert len(rows[1].split(" | ")) != len(_cells(rows[1])) + 1, "the fixture no longer discriminates a ' | ' split"
    path = _ledger(tmp, rows)
    got = write(path, {"[BR#1]": ["[CG#2]"], "[BR#6]": ["[CG#7]"], "[BR#9]": ["[CG#10]"]})
    assert got == {"written": True, "rows": 3, "with_evidence": 3, "empty": 0}, got
    text = _get(path)
    assert _cells(_row(text, "[BR#6]")) == ["[BR#6]", "The page shows the count.", "unallocated", "", "[CG#7]"], _row(text, "[BR#6]")
    assert _row(text, "[BR#9]") == "| [BR#9] | A customer may change it at any time. | unallocated | | [CG#10] |"
    assert _row(text, "[BR#1]") == "| [BR#1] | The report lists every invoice. | unallocated | [DEF#1], [DEF#2] | [CG#2] |"


def case_an_empty_evidence_cell_is_one_space_and_a_row_the_map_omits_is_emptied(tmp):
    rows = [
        "| [BR#1] | One. | covered-here | | [CG#1], [CG#4] |\n",
        "| [BR#2] | Two. | covered-here | [DEF#3] | [DG#2] |\n",
        "| [BR#3] | Three. | unallocated | | |\n",
    ]
    path = _ledger(tmp, rows)
    got = write(path, {"[BR#3]": ["[CG#5]"]})
    assert got == {"written": True, "rows": 3, "with_evidence": 1, "empty": 2}, got
    text = _get(path)
    assert _row(text, "[BR#1]") == "| [BR#1] | One. | covered-here | | |"
    assert _row(text, "[BR#2]") == "| [BR#2] | Two. | covered-here | [DEF#3] | |"
    assert _row(text, "[BR#3]") == "| [BR#3] | Three. | unallocated | | [CG#5] |"
    got = write(path, {"[BR#3]": []})
    assert got["with_evidence"] == 0 and _row(_get(path), "[BR#3]") == "| [BR#3] | Three. | unallocated | | |"


def case_an_escaped_pipe_and_a_run_of_backslashes_stay_in_their_cell(tmp):
    # The customer's `a | b` is written `a \| b`, and their `\|` is written `\\\|`.
    text_cell = r"Columns: a \| b, and the literal \\\| sequence, and \\ alone."
    rows = ["| [BR#1] | %s | unallocated | [DEF#1] | |\n" % text_cell]
    path = _ledger(tmp, rows)
    before = _get(path)
    write(path, {"[BR#1]": ["[CG#3]"]})
    after = _get(path)
    assert after == before.replace("| [DEF#1] | |", "| [DEF#1] | [CG#3] |"), after
    assert _cells(_row(after, "[BR#1]"))[1] == text_cell


def case_a_cell_ending_in_a_backslash_ends_at_its_closing_delimiter(tmp):
    rows = ["| [BR#1] | Reports go to C:\\reports\\ | unallocated | | |\n",
            "| [BR#2] | Ends \\ | unallocated | [DEF#1] | |\n"]
    path = _ledger(tmp, rows)
    write(path, {"[BR#1]": ["[DG#1]"], "[BR#2]": ["[CG#2]"]})
    text = _get(path)
    assert _row(text, "[BR#1]") == "| [BR#1] | Reports go to C:\\reports\\ | unallocated | | [DG#1] |"
    assert _row(text, "[BR#2]") == "| [BR#2] | Ends \\ | unallocated | [DEF#1] | [CG#2] |"


def case_a_line_break_in_a_cell_is_kept(tmp):
    rows = ["| [BR#1] | Fields:<br>- Invoice number<br>- Date | unallocated | | |\n"]
    path = _ledger(tmp, rows)
    write(path, {"[BR#1]": ["[CG#2]"]})
    assert _row(_get(path), "[BR#1]") == "| [BR#1] | Fields:<br>- Invoice number<br>- Date | unallocated | | [CG#2] |"


def case_ids_are_written_in_id_order_code_findings_first(tmp):
    rows = ["| [BR#1] | One. | unallocated | | |\n"]
    path = _ledger(tmp, rows)
    write(path, {"[BR#1]": ["[DG#3]", "[CG#10]", "[DG#1]", "[CG#2]"]})
    assert _row(_get(path), "[BR#1]") == "| [BR#1] | One. | unallocated | | [CG#2], [CG#10], [DG#1], [DG#3] |"


def case_a_second_write_with_the_same_map_changes_no_byte(tmp):
    rows = ["| [BR#1] | One. | unallocated | | |\n", "| [BR#2] | Two. | unallocated | [DEF#1] | |\n"]
    path = _ledger(tmp, rows)
    mapping = {"[BR#1]": ["[CG#2]", "[DG#1]"]}
    assert write(path, mapping)["written"] is True
    once = _get(path)
    stat = os.stat(path)
    got = write(path, mapping)
    assert got == {"written": False, "rows": 2, "with_evidence": 1, "empty": 1}, got
    assert _get(path) == once and os.stat(path).st_mtime_ns == stat.st_mtime_ns


def case_every_line_that_is_not_a_row_keeps_every_byte(tmp):
    head = "---\r\nkind: coverage-ledger\r\nkey: KEY-1-01\r\nnote: |\r\n  | not a row\r\n---\r\n\r\n# Coverage ledger: KEY-1-01\r\n\r\n"
    header = "| id | text | disposition | defects | evidence |  \r\n| --- | :--- | --- | --- | --- |\r\n"
    rows = ["| [BR#1] | One. | unallocated | | |\r\n", "| [BR#2] | Two. | unallocated | | |  \r\n"]
    tail = "\r\nA closing line a hand edit left.\r\n"
    path = _ledger(tmp, rows, head=head, header=header, tail=tail)
    before = _get(path)
    write(path, {"[BR#2]": ["[CG#1]"]})
    after = _get(path)
    assert after == before.replace("| Two. | unallocated | | |  \r\n", "| Two. | unallocated | | [CG#1] |  \r\n"), repr(after)


def case_a_ledger_holding_no_row_takes_an_empty_map(tmp):
    path = _ledger(tmp, [])
    before = _get(path)
    assert write(path, {}) == {"written": False, "rows": 0, "with_evidence": 0, "empty": 0}
    assert _get(path) == before


def case_a_pre_layout_ledger_is_read_where_the_parse_holds(tmp):
    header = "| id     | text | disposition | defects | evidence |\n|--------|------|-------------|---------|----------|\n"
    rows = ["| [BR#1]  | One. | unallocated | | [CG#9] |\n"]
    path = _ledger(tmp, rows, header=header)
    write(path, {"[BR#1]": ["[CG#1]"]})
    assert _row(_get(path), "[BR#1]") == "| [BR#1]  | One. | unallocated | | [CG#1] |"


def case_refuses_a_header_that_is_not_the_five_columns(tmp):
    rows = ["| [BR#1] | One. | unallocated | | |\n"]
    for header, want in (
        ("| id | text | defects | disposition | evidence |\n|---|---|---|---|---|\n", "header"),
        ("| id | text | disposition | defects |\n|---|---|---|---|\n", "header"),
        ("| id | text | disposition | defects | evidence | notes |\n|---|---|---|---|---|---|\n", "header"),
        ("| id | text | disposition | defects | evidence |\n| [BR#0] | x | y | | |\n", "separator"),
        ("|id|text|disposition|defects|evidence|\n|---|---|---|---|---|\n", "header"),
        ("", "no table"),
    ):
        path = _ledger(tmp, rows if header else [], header=header)
        before = _get(path)
        _refused(write, path, {}, want=want)
        assert _get(path) == before


def case_refuses_a_row_whose_cell_count_differs(tmp):
    for row, want in (
        ("| [BR#1] | One. | unallocated | |\n", "4 cells"),
        ("| [BR#1] | One | two. | unallocated | | |\n", "6 cells"),
        ("|[BR#1]|One.|unallocated|||\n", "cells"),
        ("| [BR#1] | One. | unallocated | | | trailing\n", "after its last"),
    ):
        path = _ledger(tmp, ["| [BR#2] | Two. | unallocated | | |\n", row])
        before = _get(path)
        _refused(write, path, {"[BR#2]": ["[CG#1]"]}, want=want)
        assert _get(path) == before


def case_refuses_a_duplicate_or_malformed_row_id(tmp):
    for rows, want in (
        (["| [BR#1] | One. | unallocated | | |\n", "| [BR#1] | Again. | unallocated | | |\n"], "two rows"),
        (["| BR#1 | One. | unallocated | | |\n"], "not a [BR#n]"),
    ):
        path = _ledger(tmp, rows)
        before = _get(path)
        _refused(write, path, {}, want=want)
        assert _get(path) == before


def case_refuses_a_table_row_after_the_table_ends(tmp):
    path = _ledger(tmp, ["| [BR#1] | One. | unallocated | | |\n"], tail="\n| [BR#2] | Two. | unallocated | | |\n")
    before = _get(path)
    _refused(write, path, {}, want="after the table")
    assert _get(path) == before


def case_refuses_a_map_naming_a_row_the_ledger_lacks(tmp):
    path = _ledger(tmp, ["| [BR#1] | One. | unallocated | | |\n"])
    before = _get(path)
    _refused(write, path, {"[BR#1]": ["[CG#1]"], "[BR#7]": ["[CG#2]"]}, want="[BR#7]")
    assert _get(path) == before


def case_refuses_a_map_value_that_is_not_a_finding_list(tmp):
    path = _ledger(tmp, ["| [BR#1] | One. | unallocated | | |\n"])
    before = _get(path)
    for value in ("[CG#1]", ["CG#1"], ["[CG#01]"], ["[CG#1]", "[CG#1]"], ["[EV#1]"], ["[CG#1], [DG#2]"], [1], None):
        _refused(write, path, {"[BR#1]": value}, want="[BR#1]")
    _refused(write, path, {"BR#1": ["[CG#1]"]}, want="not a [BR#n]")
    assert _get(path) == before


def case_the_map_is_one_json_object_naming_each_row_once(tmp):
    assert parse_map('{"[BR#1]": ["[CG#1]"]}') == {"[BR#1]": ["[CG#1]"]}
    for text, want in (('{"[BR#1]": ["[CG#1]"], "[BR#1]": []}', "twice"), ("[]", "JSON object"),
                       ("not json", "JSON"), ("", "JSON")):
        _refused(parse_map, text, want=want)


def case_the_cli_writes_reports_and_refuses_with_exit_2(tmp):
    path = _ledger(tmp, ["| [BR#1] | One. | unallocated | | |\n"])
    before = _get(path)
    for stdin, code, out_want, err_want in (
        ('{"[BR#1]": ["[CG#1]"]}', 0, '"written": true', ""),
        ('{"[BR#1]": ["[CG#1]"]}', 0, '"written": false', ""),
        ('{"[BR#2]": ["[CG#1]"]}', 2, "", "ledger-evidence: "),
    ):
        out, err = io.StringIO(), io.StringIO()
        real = sys.stdin
        sys.stdin = io.StringIO(stdin)
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                got = main(["write", "--ledger", path])
        finally:
            sys.stdin = real
        assert got == code, (got, out.getvalue(), err.getvalue())
        assert out_want in out.getvalue() and err_want in err.getvalue(), (out.getvalue(), err.getvalue())
        assert tmp not in out.getvalue() + err.getvalue(), "printed a path outside the repository"
    assert _get(path) != before
    os.remove(path)
    err = io.StringIO()
    real = sys.stdin
    sys.stdin = io.StringIO("{}")
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            got = main(["write", "--ledger", path])
    finally:
        sys.stdin = real
    assert got == 2 and "ledger-evidence: " in err.getvalue() and tmp not in err.getvalue(), err.getvalue()


def selftest():
    cases = sorted((name, fn) for name, fn in globals().items() if name.startswith("case_"))
    failed = 0
    for name, fn in cases:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                fn(os.path.realpath(tmp))
                print("ok   " + name)
            except Exception as e:  # any exception is that case failing, and it is named
                failed += 1
                print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    print("selftest: %d/%d passed" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(prog="ledger-evidence.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    wrt = sub.add_parser("write")
    wrt.add_argument("--ledger", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(write(args.ledger, parse_map(sys.stdin.read()))))
    except Refused as e:
        print("ledger-evidence: %s" % e, file=sys.stderr)
        return 2
    except (OSError, UnicodeError) as e:
        print("ledger-evidence: %s" % type(e).__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""pieces.py -- read a design's `## Pieces` section and assign a diff's paths to its pieces.

/implement splits its code review by the pieces a design draws, and /design and design-reviewer
check the section they write, through this script.

  pieces.py parse <design.md>
      stdout, one JSON object: {"status": "pieces"|"none"|"malformed", "defect": str|null,
      "reason": str|null, "pieces": [{"name": str, "files": [str], "contract": [str]}]}.
      `pieces` is empty unless status is "pieces".
  pieces.py assign <design.md> <paths-file>
      parse's four fields, each piece also carrying "paths" (the paths it matches, in input order),
      plus "unassigned" (the paths no piece matches) and "split" (true exactly when status is
      "pieces" and two or more pieces have a non-empty "paths"). <paths-file> holds NUL-separated
      paths, as `git diff --name-only -z` writes them; an empty file is no paths. A path two pieces
      both match makes the status "malformed", the defect naming the path and both pieces. On
      "none" or "malformed", every path is unassigned and "split" is false.

The format read (design-format's section on pieces):
  The section starts at a line `## Pieces` outside any fenced code block and ends at the next `## `
  heading outside one, or the end of the file. It is `none` when there is no such heading, or the
  section's first non-blank line begins `_N/A`. Otherwise it holds only blank lines, one
  `Reason: <text>` line before the first piece, and pieces, each a `### <name>` line (kebab-case,
  unique) followed by one `- Files: ...` line and an optional `- Contract: ...` line. CRLF is accepted.
  `Files:` is a comma-separated list of backtick-quoted entries, nothing else but commas and spaces.
  `Contract:` is comma-separated plain text, or `none`.

Each Files entry is a pattern relative to the repository's top level: `*` matches any run of
characters except `/`; `**` as a whole path segment matches zero or more segments; `?` matches one
character except `/`; an entry ending in `/` matches everything under that directory; every other
character is literal; an entry with no wildcard matches that one path. No entry may appear in two
pieces.

Exit codes: 0 done; 1 a failed --selftest; 2 usage; 4 <design.md> or <paths-file> cannot be read
(the message on stderr names the path).
Standard library only; `python3 pieces.py --selftest` runs the tests.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


class Fail(Exception):
    def __init__(self, code, msg):
        Exception.__init__(self, msg)
        self.code = code


def show(s):
    """A string as the caller will read it in a message."""
    return s.encode("utf-8", "surrogateescape").decode("utf-8", "replace")


def section_lines(text):
    """The lines of the `## Pieces` section (without line ends), or None where there is none."""
    lines = text.split("\n")
    fence = None  # (char, length) while inside a fenced block
    inside = None
    out = []
    for raw in lines:
        line = raw[:-1] if raw.endswith("\r") else raw
        m = FENCE_RE.match(line)
        if fence is not None:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                    and line.strip() == m.group(1):
                fence = None
            if inside:
                out.append(line)
            continue
        if m:
            fence = (m.group(1)[0], len(m.group(1)))
            if inside:
                out.append(line)
            continue
        if line.startswith("## "):
            if inside:
                break
            if line.rstrip() == "## Pieces":
                inside = True
            continue
        if inside:
            out.append(line)
    return out if inside else None


def parse_files(rest):
    """(entries, defect) for the text after `- Files:`."""
    entries = []
    i, n = 0, len(rest)
    expecting = False
    while True:
        while i < n and rest[i] == " ":
            i += 1
        if i >= n:
            if expecting:
                return None, "a Files list ends in a comma"
            break
        if rest[i] != "`":
            j = rest.find(",", i)
            bad = rest[i:j if j >= 0 else n].strip()
            return None, "the Files entry %s is not in backticks" % show(bad)
        j = rest.find("`", i + 1)
        if j < 0:
            return None, "a Files entry opens a backtick it never closes"
        entry = rest[i + 1:j]
        if not entry.strip():
            return None, "a Files entry is empty"
        entries.append(entry)
        i = j + 1
        expecting = False
        while i < n and rest[i] == " ":
            i += 1
        if i >= n:
            break
        if rest[i] != ",":
            return None, "the text %s follows a Files entry outside its backticks" % show(rest[i:].strip())
        i += 1
        expecting = True
    return entries, None


def malformed(defect, reason=None):
    return {"status": "malformed", "defect": defect, "reason": reason, "pieces": []}


def parse_section(text):
    lines = section_lines(text)
    if lines is None:
        return {"status": "none", "defect": None, "reason": None, "pieces": []}
    for line in lines:
        if line.strip():
            if line.lstrip().startswith("_N/A"):
                return {"status": "none", "defect": None, "reason": None, "pieces": []}
            break
    reason = None
    pieces = []
    seen_entry = {}
    cur = None
    for line in lines:
        s = line.rstrip()
        if not s.strip():
            continue
        if s.startswith("Reason:"):
            if cur is not None or pieces:
                return malformed("the Reason line %s comes after the first piece" % show(s))
            if reason is not None:
                return malformed("the section holds a second Reason line: %s" % show(s))
            reason = s[len("Reason:"):].strip()
            if not reason:
                return malformed("the Reason line is empty")
            continue
        if s.startswith("### "):
            if reason is None:
                return malformed("the section has no Reason line before its first piece")
            name = s[4:].strip()
            if not NAME_RE.match(name):
                return malformed("the piece name %s is not kebab-case" % show(name), reason)
            if any(p["name"] == name for p in pieces):
                return malformed("the piece name %s is used twice" % show(name), reason)
            cur = {"name": name, "files": None, "contract": []}
            cur["_contract_seen"] = False
            pieces.append(cur)
            continue
        if s.startswith("- Files:") and cur is not None:
            if cur["files"] is not None:
                return malformed("the piece %s has a second Files line" % cur["name"], reason)
            entries, defect = parse_files(s[len("- Files:"):])
            if defect:
                return malformed("the piece %s: %s" % (cur["name"], defect), reason)
            if not entries:
                return malformed("the piece %s has a Files line with no entry" % cur["name"], reason)
            for e in entries:
                if e in seen_entry and seen_entry[e] != cur["name"]:
                    return malformed("the Files entry %s is in both %s and %s"
                                     % (show(e), seen_entry[e], cur["name"]), reason)
                seen_entry[e] = cur["name"]
            cur["files"] = entries
            continue
        if s.startswith("- Contract:") and cur is not None:
            if cur["_contract_seen"]:
                return malformed("the piece %s has a second Contract line" % cur["name"], reason)
            cur["_contract_seen"] = True
            body = s[len("- Contract:"):].strip()
            if body.lower() == "none" or not body:
                cur["contract"] = []
            else:
                cur["contract"] = [c.strip() for c in body.split(",") if c.strip()]
            continue
        return malformed("the section holds a line it does not allow: %s" % show(s), reason)
    if reason is None:
        return malformed("the section has no Reason line")
    for p in pieces:
        if p["files"] is None:
            return malformed("the piece %s has no Files line" % p["name"], reason)
        del p["_contract_seen"]
    if len(pieces) < 2:
        return malformed("the section draws %d piece%s; it needs at least two"
                         % (len(pieces), "" if len(pieces) == 1 else "s"), reason)
    return {"status": "pieces", "defect": None, "reason": reason, "pieces": pieces}


def segment_regex(seg):
    out = []
    prev_star = False
    for ch in seg:
        if ch == "*":
            if not prev_star:
                out.append("[^/]*")
            prev_star = True
            continue
        prev_star = False
        out.append("[^/]" if ch == "?" else re.escape(ch))
    return "".join(out)


def glob_to_regex(entry):
    """The compiled pattern for one Files entry, to be used with fullmatch."""
    parts = entry.split("/")
    if parts and parts[-1] == "":
        parts[-1] = "**"
    rx = ""
    last = len(parts) - 1
    for i, p in enumerate(parts):
        if p == "**":
            rx += ".*" if i == last else "(?:[^/]+/)*"
        else:
            rx += segment_regex(p) + ("" if i == last else "/")
    return re.compile(rx, re.DOTALL)


def assign(parsed, paths):
    out = dict(parsed)
    out["pieces"] = [dict(p, paths=[]) for p in parsed["pieces"]]
    out["unassigned"] = []
    out["split"] = False
    if parsed["status"] != "pieces":
        out["pieces"] = []
        out["unassigned"] = list(paths)
        return out
    rxs = [[glob_to_regex(e) for e in p["files"]] for p in parsed["pieces"]]
    for path in paths:
        hit = [i for i, rs in enumerate(rxs) if any(r.fullmatch(path) for r in rs)]
        if len(hit) > 1:
            return {"status": "malformed",
                    "defect": "the path %s is matched by both %s and %s"
                              % (show(path), parsed["pieces"][hit[0]]["name"], parsed["pieces"][hit[1]]["name"]),
                    "reason": parsed["reason"], "pieces": [], "unassigned": list(paths), "split": False}
        if hit:
            out["pieces"][hit[0]]["paths"].append(path)
        else:
            out["unassigned"].append(path)
    out["split"] = sum(1 for p in out["pieces"] if p["paths"]) >= 2
    return out


def read_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise Fail(4, "cannot read %s: %s" % (path, e.strerror or e))


def decode(b):
    return b.decode("utf-8", "surrogateescape")


def emit(value, out):
    s = json.dumps(value, indent=1, ensure_ascii=False) + "\n"
    out.write(s.encode("utf-8", "surrogateescape"))


USAGE = "usage: pieces.py parse <design.md> | assign <design.md> <paths-file> | --selftest"


def run(argv, out):
    if not argv or argv[0] not in ("parse", "assign"):
        raise Fail(2, USAGE)
    if argv[0] == "parse" and len(argv) != 2:
        raise Fail(2, USAGE)
    if argv[0] == "assign" and len(argv) != 3:
        raise Fail(2, USAGE)
    parsed = parse_section(decode(read_bytes(argv[1])))
    if argv[0] == "parse":
        emit(parsed, out)
        return
    raw = read_bytes(argv[2])
    paths = [decode(p) for p in raw.split(b"\0") if p]
    emit(assign(parsed, paths), out)


# ---------------------------------------------------------------------------------------------

def selftest():
    failures = []
    checks = [0]
    me = os.path.abspath(__file__)

    def check(name, cond):
        checks[0] += 1
        if not cond:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        n = [0]

        def cli(*args):
            r = subprocess.run([sys.executable, me] + list(args), capture_output=True)
            return r.returncode, decode(r.stdout), r.stderr.decode("utf-8", "replace")

        def design(text, crlf=False):
            n[0] += 1
            p = os.path.join(tmp, "design%d.md" % n[0])
            if crlf:
                text = text.replace("\n", "\r\n")
            with open(p, "wb") as f:
                f.write(text.encode("utf-8"))
            return p

        def pathsfile(paths):
            n[0] += 1
            p = os.path.join(tmp, "paths%d" % n[0])
            with open(p, "wb") as f:
                f.write(b"".join(x.encode("utf-8", "surrogateescape") + b"\0" for x in paths))
            return p

        def parse(text, crlf=False):
            code, out, _ = cli("parse", design(text, crlf))
            return json.loads(out) if code == 0 else {"status": "exit%d" % code}

        def assign_(text, paths):
            code, out, _ = cli("assign", design(text), pathsfile(paths))
            return json.loads(out) if code == 0 else {"status": "exit%d" % code}

        def pieces_doc(a_files, b_files="`b/**`", a_contract="A, B", b_contract="none"):
            return ("# Design\n\n## Pieces\n\nReason: two parts\n\n### parser\n- Files: %s\n"
                    "- Contract: %s\n\n### runs\n- Files: %s\n- Contract: %s\n\n## Seams\n"
                    % (a_files, a_contract, b_files, b_contract))

        TWO = ("# Design\n\n## Pieces\n\nReason: the parser and the runs change apart\n\n"
               "### parser\n- Files: `src/parser/**`, `src/Lexer.java`\n- Contract: A, B\n\n"
               "### runs\n- Files: `src/runs/*.java`\n- Contract: none\n\n## Seams\n\n### x\n- Files: `q`\n")

        # parse
        r = parse("# Design\n\n## Seams\ntext\n")
        check("parse_none_no_section", r["status"] == "none" and r["pieces"] == [])
        r = parse("# D\n\n## Pieces\n\n_N/A — one coherent change_\n\n## Next\n")
        check("parse_none_na", r["status"] == "none" and r["pieces"] == [])
        r = parse(TWO)
        want = [{"name": "parser", "files": ["src/parser/**", "src/Lexer.java"], "contract": ["A", "B"]},
                {"name": "runs", "files": ["src/runs/*.java"], "contract": []}]
        check("parse_two_pieces", r["status"] == "pieces" and r["pieces"] == want
              and [p["name"] for p in r["pieces"]] == ["parser", "runs"]
              and r["reason"] == "the parser and the runs change apart" and r["defect"] is None)
        check("parse_crlf", parse(TWO, crlf=True) == r)
        check("parse_section_ends_at_next_h2", len(r["pieces"]) == 2)

        def bad(name, text):
            r = parse(text)
            check(name, r["status"] == "malformed" and bool(r["defect"]) and r["pieces"] == [])
            return r

        bad("parse_no_reason", TWO.replace("Reason: the parser and the runs change apart\n", ""))
        bad("parse_empty_reason", TWO.replace("Reason: the parser and the runs change apart", "Reason:   "))
        bad("parse_one_piece", "## Pieces\n\nReason: r\n\n### a\n- Files: `a/**`\n")
        bad("parse_duplicate_name", TWO.replace("### runs", "### parser"))
        bad("parse_bad_name", TWO.replace("### parser", "### Parser"))
        bad("parse_no_files", TWO.replace("- Files: `src/runs/*.java`\n", ""))
        bad("parse_unquoted_entry", TWO.replace("`src/runs/*.java`", "src/runs/*.java"))
        r = bad("parse_writers_line", TWO.replace("- Contract: none", "- Contract: none\n- Writers: one"))
        check("parse_writers_line quotes the line", "Writers: one" in r["defect"])
        bad("parse_same_entry_twice", TWO.replace("`src/runs/*.java`", "`src/parser/**`"))
        bad("parse_entry_outside_backticks", TWO.replace("`src/Lexer.java`", "`src/Lexer.java` x"))
        bad("parse_trailing_comma", TWO.replace("`src/Lexer.java`", "`src/Lexer.java`,"))
        bad("parse_empty_section", "## Pieces\n\n## Next\n")
        r = parse("# D\n\n```\n## Pieces\n\nReason:\n### a\nWriters: one\n```\n\n## Other\n")
        check("parse_ignores_fenced", r["status"] == "none")
        r = parse("# D\n\n~~~md\n## Pieces\n~~~\n")
        check("parse_ignores_tilde_fenced", r["status"] == "none")

        # glob grammar, through assign
        def matched(entry, path):
            r = assign_(pieces_doc("`%s`" % entry, "`zz-never/**`"), [path])
            return r["status"] == "pieces" and r["pieces"][0]["paths"] == [path]

        check("glob_star_one_segment", matched("src/a/*.java", "src/a/X.java")
              and not matched("src/a/*.java", "src/a/b/X.java") and not matched("src/a/*.java", "src/a/X.javax"))
        check("glob_double_star", matched("src/a/**", "src/a/X.java") and matched("src/a/**", "src/a/b/c/X.java")
              and not matched("src/a/**", "src/ab/X.java")
              and matched("**/X.java", "X.java") and matched("**/X.java", "d/e/X.java")
              and not matched("**/X.java", "d/YX.java") and matched("src/**/X.java", "src/X.java")
              and matched("src/**/X.java", "src/a/b/X.java"))
        check("glob_question", matched("src/?.java", "src/a.java") and not matched("src/?.java", "src/ab.java")
              and not matched("src/?.java", "src//.java"))
        check("glob_exact", matched("src/a.b", "src/a.b") and not matched("src/a.b", "src/axb")
              and not matched("src/a.b", "src/a.b/c") and matched("a[1].{x}", "a[1].{x}")
              and not matched("a[1]", "a1"))
        check("glob_trailing_slash", matched("src/a/", "src/a/X.java") and matched("src/a/", "src/a/b/X.java")
              and not matched("src/a/", "src/ab/X.java") and not matched("src/a/", "src/a"))

        # assign
        r = assign_(TWO, ["src/parser/P.java", "src/Lexer.java", "src/runs/R.java", "README.md"])
        pp = dict((p["name"], p["paths"]) for p in r["pieces"])
        check("assign_split", r["split"] is True and pp == {"parser": ["src/parser/P.java", "src/Lexer.java"],
                                                            "runs": ["src/runs/R.java"]}
              and r["unassigned"] == ["README.md"] and r["status"] == "pieces")
        r = assign_(TWO, ["src/parser/P.java", "src/parser/Q.java", "docs/x.md"])
        check("assign_one_piece_touched", r["split"] is False and r["unassigned"] == ["docs/x.md"])
        r = assign_(TWO, ["src/parser/P.java", "src/runs/R.java", "test/parser/PTest.java", "test/runs/RTest.java"])
        check("assign_unassigned_tests", r["unassigned"] == ["test/parser/PTest.java", "test/runs/RTest.java"]
              and r["split"] is True)
        odd = ["x/a b.txt", "x/it's.txt", "x/café.txt", "x/bad\udcff.txt", "x/new\nline.txt"]
        r = assign_(pieces_doc("`x/*`", "`zz-never/**`"), odd)
        check("assign_odd_paths", r["status"] == "pieces" and r["pieces"][0]["paths"] == odd
              and r["unassigned"] == [])
        r = assign_(TWO, ["src/parser/Old.java", "src/runs/New.java"])
        check("assign_rename_touches_both", r["split"] is True)
        r = assign_(pieces_doc("`src/**`", "`src/a/X.java`"), ["src/a/X.java"])
        check("assign_overlap", r["status"] == "malformed" and r["split"] is False
              and "src/a/X.java" in r["defect"] and "parser" in r["defect"] and "runs" in r["defect"])
        r = assign_("# D\n", ["a", "b"])
        check("assign_none_section", r["status"] == "none" and r["unassigned"] == ["a", "b"]
              and r["split"] is False)
        r = assign_(TWO.replace("Reason:", "Rsn:"), ["a"])
        check("assign_malformed_unassigned", r["status"] == "malformed" and r["unassigned"] == ["a"]
              and r["split"] is False)
        r = assign_(TWO, [])
        check("assign_empty_paths", r["split"] is False and r["unassigned"] == []
              and all(p["paths"] == [] for p in r["pieces"]))

        # exit codes
        d = design(TWO)
        e = pathsfile([])
        code, _, err = cli("parse", os.path.join(tmp, "nope.md"))
        check("missing_design_exit_4", code == 4 and "nope.md" in err)
        code, _, err = cli("assign", d, os.path.join(tmp, "nopaths"))
        check("missing_paths_exit_4", code == 4 and "nopaths" in err)
        check("usage_exit_2", cli()[0] == 2 and cli("frob")[0] == 2 and cli("parse")[0] == 2
              and cli("assign", d)[0] == 2 and cli("parse", d, e)[0] == 2)

    if failures:
        for f in failures:
            print("FAIL %s" % f)
        print("pieces selftest: FAIL")
        return 1
    print("pieces selftest: PASS (%d checks)" % checks[0])
    return 0


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    try:
        run(argv, sys.stdout.buffer)
        return 0
    except Fail as e:
        sys.stderr.write("pieces.py: %s\n" % e)
        return e.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

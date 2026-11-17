#!/usr/bin/env python3
r"""backlog-lines.py — the one line reader of the documentation backlog, <top>/.dev-workflows/docs-backlog.yml.

  backlog-lines.py check --repo <top>
  backlog-lines.py moved --repo <top> --base <name> --id <id> [--id <id> ...]
  backlog-lines.py edit  --repo <top> --id <id> --status <status> [--page-path <rel>]
  backlog-lines.py --selftest

It never parses the backlog as YAML -- no YAML parser ships with the plugins -- and reads it line by line, in the one
shape docs-workflows' backlog-format reference states in section 1, under "The line shape a backlog run reads.":
every line a whole item, no value continuing past the line it opens on, so that no line inside a value can pass for a
unit entry. This script is that shape's one implementer. A change to the paragraph is a change here and to --selftest,
in the same commit, and --selftest holds the two together: it reads the paragraph's reasons and the section's schema
from the reference itself, and fails where either disagrees with this script. The file is decoded as UTF-8, strictly,
and split on \n alone; a CR ends a line only before its \n. A unit entry spans from its `- id:` line to the line
before the next line at its indent opening `- `, or the next column-0 line that is neither blank nor a comment.

check tests the shape. It prints {"shape": "ok", "schema_version": "<digits>"|null, "units": <n>, "duplicates":
[<id>...], "duplicates_outside_class": <n>, "ids_outside_class": <n>}: schema_version the top-level key's plain
digits where it is given once, else null; units the number of entries; duplicates each id two or more entries hold,
in file order, printed only where it is in the unit-id class, ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$, and otherwise
counted, once per id, in duplicates_outside_class; ids_outside_class the number of entries whose id is outside that
class. Or it prints {"shape": "out", "line": <n>, "reason": "<word>"}: <n> the first line out of shape, 1-based (0 for
too-large, whose reason is the whole file), and <word> the paragraph's reason for it.

moved tells which of the --id units a branch not merged into the base has moved. It resolves the base as
refs/remotes/origin/<base>, else refs/heads/<base>, and reads HEAD's branch itself. It lists `git for-each-ref
--sort=-committerdate` over refs/heads and refs/remotes/origin, each ref with its object id, full name and short name,
and drops refs/remotes/origin/HEAD, HEAD's branch, <base> and origin/<base> -- by full name, since git shortens
refs/remotes/origin/HEAD to "origin" and shortens a ref another one shadows to "heads/..." or "remotes/..." -- and
every ref whose short name is outside the branch class, ^[A-Za-z0-9_][A-Za-z0-9._/@+-]*$, which is counted in
names_outside_class and named nowhere. Of the rest, newest first, it examines at most 60, and keeps each whose object
id is a full object name, ^[0-9a-f]{40}([0-9a-f]{24})?$, that is not merged into the base and whose backlog differs
from its merge base's (or that shares no merge base with the base), stopping once it has kept 20. A kept ref's backlog
is read by its object id with `git cat-file`, at most 1 MiB, and tested as check tests one. An entry absent there, or a
ref with no backlog, is not moved. A backlog over 1 MiB, out of shape, recorded in the tree as anything but a regular
file (a symbolic link's blob is its target's name, never a file), holding one of the ids twice, or giving one a status
outside ^[a-z][a-z-]{0,31}$ -- or a ref git cannot answer for -- makes the ref unreadable. A unit is moved on a ref
where its status there differs from its status in the working backlog, which must be in shape and hold each --id
exactly once. It prints {"moved": {<id>: [<ref>...]}, "unreadable": [<ref>...], "read": <n>, "more": <n>,
"names_outside_class": <n>}: moved names only the ids some ref moved, each ref by its short name, newest first; read
counts the refs kept, each either compared or unreadable; more counts every ref past the point it stopped.

edit writes one unit's move. It refuses, exit 3, the file untouched: a backlog out of shape, an --id no entry or two
entries hold, an entry with no page_path: line where --page-path is given, a page_path already set to another path
(null, ~ and an empty value are unset), and a backlog that changed while it read it. Otherwise it replaces the
status: value and, where --page-path is given and page_path is unset, the page_path value, keeping each line's indent,
key, trailing comment and line ending and every other byte; checks that the result reads back as that edit, in shape;
writes it atomically, a new file beside the backlog renamed over it; and runs `git -C <top> diff -U0 --no-color
--no-ext-diff --no-textconv -- .dev-workflows/docs-backlog.yml`. Where the lines that diff removes and adds are not
exactly the lines it changed, all inside the entry -- or git cannot show them -- it writes back the bytes it read and
exits 4. It prints {"first": <n>, "last": <n>, "changed": [<n>...]}, the entry's first and last line and the lines it
changed; on exit 3 {"refused": "<why>", "line": <n>|null, "reason": "<word>"|null}, <why> one of shape, id-absent,
id-twice, no-page-path, page-path-set and changed-while-reading; on exit 4 {"undone": "<why>", "first": <n>, "last":
<n>, "changed": [<n>...]}, <why> hunk-outside or diff-failed.

The arguments are tested before anything is read or run: --id against the unit-id class; --base against the branch
class; --status against ^[a-z][a-z-]{0,31}$, less the words YAML reads as something other than a string (null, true,
false, yes, no, on, off, y, n); --page-path against ^[A-Za-z0-9_][A-Za-z0-9._/-]*\.md$ with no empty, . or ..
segment; --repo, a directory, which moved and edit also hold to being a git work tree's top level. A flag given twice
(--id to moved aside), or as --flag=value, refuses the run. <top>/.dev-workflows must be a real directory and the
backlog a regular file, both by lstat: a symbolic link to either is refused, never followed, and the backlog is opened
without following a link and never waited on.

What it prints of the backlog, a ref or an argument is line numbers, counts, fixed words, and values that passed a
class test: a unit id in the unit-id class, a branch name in the branch class, the schema version's digits. A value
that fails is counted, never printed, not even in an error. Outside --selftest it opens no file but the backlog and
writes nothing but the backlog, and it runs git as an argument list, never a shell, with a 30-second timeout per
call, in its own environment less every variable whose name starts with GIT_, plus GIT_TERMINAL_PROMPT=0,
GIT_OPTIONAL_LOCKS=0 and GIT_NO_LAZY_FETCH=1. Git's stderr is never printed.

Exit 0: it ran, and the answer is the one JSON object on stdout -- for check, the shape in or out. Exit 2: it could not
run -- an argument outside its class, a usage error, --repo no directory or no work tree's top level, .dev-workflows
or the backlog refused as above or unreadable, git not run or not answering where moved must have an answer (HEAD,
the base, the branch list), the working backlog out of shape or not holding an --id once (moved), a write that failed
(the backlog unchanged), or an internal error; stdout is empty and stderr holds one line, "backlog-lines: not run
(<why>)", <why> fixed text. One exit 2 follows a write: edit's undo failing, whose <why> says the edit was written and
not undone. Exit 3: edit refused on the file's content before writing; the file is untouched. Exit 4: edit undone; the
file holds the bytes it read. --selftest exits 0 when every case passes and 1 otherwise.

The caller's rule, which fails closed. Any exit but 0, 3 and 4 -- a crash's 1, a signal's -- is read as 2, and so is a
stdout that is not one JSON object. check or moved exiting anything but 0 is a stop, never a skip: never read as in
shape, as no duplicate or as nothing moved. edit exiting 3 or 4 ends the unit, the backlog as it was; edit exiting 2
ends the unit and stops the run, since the backlog may hold a write nobody checked, and the caller restores it from
its own copy.

Python standard library only.
"""

import argparse
import contextlib
import io
import json
import os
import re
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
BACKLOG_DIR = ".dev-workflows"
BACKLOG_NAME = "docs-backlog.yml"
BACKLOG_PATH = BACKLOG_DIR + "/" + BACKLOG_NAME
SHAPE_CAP = 8 * 1024 * 1024  # bytes: a larger backlog is out of shape, too-large
REF_CAP = 1024 * 1024  # bytes: a larger backlog on a ref is unreadable
EXAMINE_CAP = 60  # refs examined at most, newest first
READ_REFS_CAP = 20  # refs kept and read at most
GIT_TIMEOUT = 30  # seconds, every git call

# Every pattern that tests a whole value is used with fullmatch and is ASCII; digits are [0-9].
UNIT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", re.ASCII)
STATUS_RE = re.compile(r"[a-z][a-z-]{0,31}", re.ASCII)
STATUS_RESERVED = ("null", "true", "false", "yes", "no", "on", "off", "y", "n")  # YAML reads these as no string
PAGE_PATH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]*\.md", re.ASCII)
OBJECT_ID_RE = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?", re.ASCII)
BRANCH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/@+-]*", re.ASCII)  # read-only-repos section 3's class
SINGLE_FLAGS = ("--repo", "--base", "--status", "--page-path")  # each taken once: a second refuses the run

# The reasons, one word each, the paragraph's: --selftest holds this tuple to it.
REASONS = ("block-scalar", "anchor", "alias", "tag", "tab", "control", "encoding", "unclosed-quote",
           "unclosed-flow", "trailing", "key", "continuation", "units-twice", "units-not-block", "entry-opener",
           "duplicate-key", "indent", "status", "too-large")

# The fixed <why> of every exit 2; none carries a value from the command line, the backlog or a ref.
WHY_USAGE = "usage: an unknown subcommand or flag, a flag without its value, or a flag given twice"
WHY_REPO = "--repo is not a directory"
WHY_ID = "--id is outside the unit-id class"
WHY_BASE = "--base is outside the branch class"
WHY_STATUS = "--status is outside the status class"
WHY_PAGE_PATH = "--page-path is outside the page-path class"
WHY_DIR = "<top>/.dev-workflows is not a real directory (absent, or a symbolic link)"
WHY_FILE = "the backlog is not a regular file (absent, a symbolic link, or another kind of file)"
WHY_READ = "the backlog could not be read"
WHY_NO_GIT = "git could not be run in --repo"
WHY_NOT_TOP = "--repo is not the top level of a git work tree"
WHY_HEAD = "git could not read HEAD in --repo"
WHY_NO_BASE = "--base names neither origin/<base> nor a local branch <base>"
WHY_LIST = "git could not list the branches of --repo"
WHY_WORKING_SHAPE = "the working backlog is out of shape (run check)"
WHY_WORKING_ID = "an --id is not held by exactly one unit of the working backlog"
WHY_WRITE = "the backlog could not be written; it is unchanged"
WHY_UNDO = "the edit was written and could not be undone; restore the backlog from the copy taken before the edit"
WHY_INTERNAL = "internal error"

_IO = {"git": 0, "reads": 0, "writes": 0}  # what a run did, for --selftest's "nothing read or written"


class NotRun(Exception):
    """The script cannot run; its one argument is the fixed <why>."""


class Out(Exception):
    """A line out of shape: (line, reason), the reason one of REASONS."""

    def __init__(self, line, reason):
        assert reason in REASONS, reason
        super().__init__(line, reason)
        self.line, self.reason = line, reason


# ---- the shape: one line at a time ----

class _Value:
    """A value on its key's or its dash's line: kind (empty, plain, squote, dquote or flow), the span [start, end) of
    its token in the line, and the token's text (a plain scalar's without its trailing spaces)."""
    __slots__ = ("kind", "start", "end", "text")

    def __init__(self, kind, start, end, text):
        self.kind, self.start, self.end, self.text = kind, start, end, text


class _Item:
    """A key, or a sequence item, and what may hang under it: opens is True only for a key whose value is empty."""
    __slots__ = ("line", "key", "value", "opens", "had_child", "inner")

    def __init__(self, line, key, value, inner=None):
        self.line, self.key, self.value, self.inner = line, key, value, inner
        self.opens = value is not None and value.kind == "empty"
        self.had_child = False


class _Frame:
    """An open block: its indent, map or seq, its role (root, units, entry or None), its last item, and its entry."""
    __slots__ = ("indent", "kind", "role", "last", "entry")

    def __init__(self, indent, kind, role=None, entry=None):
        self.indent, self.kind, self.role, self.entry, self.last = indent, kind, role, entry, None


class _Entry:
    """A unit entry: its first and last line, its id (a plain scalar's text) and its keys at the entry's key indent."""
    __slots__ = ("first", "last", "id", "keys")

    def __init__(self, first, uid):
        self.first, self.last, self.id, self.keys = first, None, uid, {}


class _Shape:
    __slots__ = ("schema_version", "entries", "texts")

    def __init__(self, schema_version, entries, texts):
        self.schema_version, self.entries, self.texts = schema_version, entries, texts


KEY_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*):(?= |\Z)", re.ASCII)
DIGITS_RE = re.compile(r"[0-9]{1,20}", re.ASCII)
CLOSER = {"[": "]", "{": "}"}


def _chars(n, line):
    """Out where the line holds a tab or a control character: any C0 control, a CR not ending the line before its \\n,
    U+0085, U+2028 or U+2029."""
    for ch in line:
        o = ord(ch)
        if ch == "\t":
            raise Out(n, "tab")
        if o < 0x20 or o in (0x85, 0x2028, 0x2029):
            raise Out(n, "control")


def _quoted(line, j):
    """The index just past the quoted scalar opening at line[j], closed on this line ('' inside single quotes, a
    backslash escaping the next character inside double quotes); None where it is not closed."""
    q, i = line[j], j + 1
    while i < len(line):
        c = line[i]
        if q == '"' and c == "\\":
            i += 2
            continue
        if c == q:
            if q == "'" and i + 1 < len(line) and line[i + 1] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return None


def _trailing(n, line, end):
    """Out unless what follows a closed quote or flow collection is nothing, spaces, or spaces and a comment."""
    rest = line[end:]
    tail = rest.lstrip(" ")
    if tail and not (tail[0] == "#" and len(tail) < len(rest)):
        raise Out(n, "trailing")


def _flow(n, line, j):
    """The index just past the flow collection opening at line[j], its brackets balanced outside quotes on this line.
    It is read as a YAML reader's tokenizer reads it. Inside a plain scalar -- which spaces do not end; a ` #`, a `,`,
    `?`, `[`, `]`, `{` or `}`, or a `:` before a space, one of those or the line's end does -- a quote or a `#` is the
    scalar's. Anywhere else, between tokens -- after a bracket, a `,`, a `?`, a `:`, a `- ` or a closed quote -- a `#`
    opens a comment and a quote a quoted scalar, which must close on this line, or the collection would go on past
    it; an anchor, an alias or a tag there is out of shape too. The set of
    places read as between tokens is the widest any YAML reader takes, so a reader that disagrees can only refuse more.
    """
    stack, i, plain = [], j, False
    while i < len(line):
        c = line[i]
        if c == " ":
            i += 1
            continue
        if c == "#" and (line[i - 1] == " " or not plain):  # a comment: the rest of the line is not the collection's
            break
        if plain:
            if not (c in ",?[]{}" or (c == ":" and (i + 1 == len(line) or line[i + 1] in " ,[]{}"))):
                i += 1
                continue
            plain = False  # the scalar ends here, and c is read as the token it opens
        if c in "&*!":
            raise Out(n, {"&": "anchor", "*": "alias", "!": "tag"}[c])
        if c in "'\"":
            end = _quoted(line, i)
            if end is None:
                raise Out(n, "unclosed-quote")
            i = end
            continue
        if c in "[{":
            stack.append(c)
            i += 1
            continue
        if c in "]}":
            if not stack or CLOSER[stack.pop()] != c:
                raise Out(n, "unclosed-flow")
            i += 1
            if not stack:
                return i
            continue
        if c in ",?:" or (c == "-" and (i + 1 == len(line) or line[i + 1] == " ")):  # a token of its own
            i += 1
            continue
        i, plain = i + 1, True
    raise Out(n, "unclosed-flow")


def _value(n, line, pos):
    """The value that opens at or after line[pos], once the spaces before it are passed; Out where it is no value
    the shape admits."""
    j = pos
    while j < len(line) and line[j] == " ":
        j += 1
    if j == len(line) or (line[j] == "#" and j > pos):
        return _Value("empty", pos, pos, "")
    c = line[j]
    if c in "|>":
        raise Out(n, "block-scalar")
    if c in "&*!":
        raise Out(n, {"&": "anchor", "*": "alias", "!": "tag"}[c])
    if c in "'\"":
        end = _quoted(line, j)
        if end is None:
            raise Out(n, "unclosed-quote")
        _trailing(n, line, end)
        return _Value("squote" if c == "'" else "dquote", j, end, line[j:end])
    if c in "[{":
        end = _flow(n, line, j)
        _trailing(n, line, end)
        return _Value("flow", j, end, line[j:end])
    # A plain scalar: not opening with a reserved or flow indicator, nor with a -, ? or : that opens a structure.
    if c in "#%@`,]}" or (c in "-?:" and (j + 1 == len(line) or line[j + 1] == " ")):
        raise Out(n, "continuation")
    k = line.find(" #", j)
    body = (line[j:] if k < 0 else line[j:k]).rstrip(" ")
    if ": " in body or body.endswith(":"):  # a mapping inside the value: no plain scalar
        raise Out(n, "continuation")
    return _Value("plain", j, j + len(body), body)


def _mapping(n, line, col):
    """(key, value) where line[col:] is `key:` or `key: value`, the key in the grammar; None where it is no mapping
    line; Out where it is a key outside the grammar, a quoted key or a `? ` key."""
    x = line[col:]
    if x == "?" or x.startswith("? "):
        raise Out(n, "key")
    m = KEY_RE.match(x)
    if m:
        return m.group(1), _value(n, line, col + m.end())
    if x[0] in "'\"":
        end = _quoted(line, col)
        if end is not None:
            after = line[end:].lstrip(" ")
            if after.startswith(":") and (len(after) == 1 or after[1] == " "):
                raise Out(n, "key")
        return None
    if x[0] in "[{":
        return None
    k = x.find(" #")
    body = (x if k < 0 else x[:k]).rstrip(" ")
    if ": " in body or body.endswith(":"):
        raise Out(n, "key")
    return None


def _seq(n, line, col):
    """("map", key, value, key column) or ("value", value) for the item a `- ` line at col opens; Out where the
    item is empty, its value left to the lines below."""
    j = col + 1
    while j < len(line) and line[j] == " ":
        j += 1
    if j == len(line) or line[j] == "#":
        raise Out(n, "continuation")
    got = _mapping(n, line, j)
    if got is not None:
        return "map", got[0], got[1], j
    return "value", _value(n, line, j)


class _Reader:
    """The structure of one backlog, a line at a time: a stack of open blocks, the units key, the entries."""

    def __init__(self):
        self.stack = [_Frame(0, "map", "root")]
        self.entries, self.schema, self.units_item = [], [], None

    def line(self, n, line, i, seq):
        """Place one line that is neither blank nor a comment, at indent i; Out where it is out of shape. Every entry
        the line closes is checked for its status: key only once the line itself has passed, since a line out of
        shape inside an entry -- one under-indented among its keys -- closes nothing."""
        closing = []
        while self.stack[-1].indent > i:
            frame = self.stack.pop()
            if frame.role == "entry":
                frame.entry.last = n - 1
                closing.append(frame.entry)
        self._place(n, line, i, seq)
        for entry in closing:
            if "status" not in entry.keys:
                raise Out(entry.first, "status")

    def end(self, last_line):
        while len(self.stack) > 1:
            frame = self.stack.pop()
            if frame.role == "entry":
                frame.entry.last = last_line
                if "status" not in frame.entry.keys:
                    raise Out(frame.entry.first, "status")

    def _place(self, n, line, i, seq):
        top = self.stack[-1]
        if top.indent < i:  # a block under top's last item
            item = top.last
            if item is None or item.inner is not None:  # nothing to hang under, or between a dash and its keys
                raise Out(n, "indent")
            if not item.opens:  # a value continuing past its line
                raise Out(n, "continuation")
            if item.had_child:  # a second block under one key, at another indent
                raise Out(n, "indent")
            item.had_child = True
            units = item is self.units_item
            if units and not seq:
                raise Out(n, "entry-opener")
            top = _Frame(i, "seq" if seq else "map", "units" if units else None)
            self.stack.append(top)
        if top.kind == "map":
            if seq:  # a block sequence at its key's own indent, or a dash among a mapping's keys
                raise Out(n, "indent")
            got = _mapping(n, line, i)
            if got is None:
                raise Out(n, "continuation")
            key, value = got
            item = _Item(n, key, value)
            if top.role == "root" and key == "units":
                if self.units_item is not None:
                    raise Out(n, "units-twice")
                if not (value.kind == "empty" or (value.kind == "flow" and value.text == "[]")):
                    raise Out(n, "units-not-block")
                self.units_item = item
            elif top.role == "root" and key == "schema_version":
                self.schema.append(value)
            elif top.role == "entry":
                if key in top.entry.keys:
                    raise Out(n, "duplicate-key")
                top.entry.keys[key] = item
                if key == "status" and value.kind != "plain":
                    raise Out(n, "status")
            top.last = item
            return
        if not seq:  # a line at a sequence's indent that does not open `- `
            raise Out(n, "indent")
        got = _seq(n, line, i)
        if top.role == "units" and (got[0] != "map" or got[1] != "id" or got[2].kind != "plain"):
            raise Out(n, "entry-opener")
        if got[0] == "value":
            top.last = _Item(n, None, got[1])
            return
        key, value, col = got[1], got[2], got[3]
        top.last = _Item(n, None, None, inner=col)
        inner = _Frame(col, "map")
        first = _Item(n, key, value)
        if top.role == "units":
            inner.role, inner.entry = "entry", _Entry(n, value.text)
            inner.entry.keys[key] = first
            self.entries.append(inner.entry)
        inner.last = first
        self.stack.append(inner)


def read_shape(data):
    """The backlog's shape, a _Shape, where `data` is in it; Out at the first line out of it."""
    if len(data) > SHAPE_CAP:
        raise Out(0, "too-large")
    segs = data.split(b"\n")
    reader, texts = _Reader(), []
    for k, raw in enumerate(segs):
        n = k + 1
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise Out(n, "encoding")
        texts.append(text)
        line = text[:-1] if text.endswith("\r") and k < len(segs) - 1 else text  # a CRLF line ending
        _chars(n, line)
        if n == 1 and line == "---":
            continue
        i = len(line) - len(line.lstrip(" "))
        rest = line[i:]
        if rest and rest[0].isspace():  # indentation holding anything but ASCII spaces
            raise Out(n, "indent")
        if not rest or rest[0] == "#":
            continue
        seq = rest == "-" or rest.startswith("- ")
        if i == 0 and seq:  # a line opening `- ` at column 0
            raise Out(n, "indent")
        reader.line(n, line, i, seq)
    reader.end(len(segs) - 1 if segs[-1] == b"" else len(segs))
    sv = None
    if len(reader.schema) == 1 and reader.schema[0].kind == "plain" and DIGITS_RE.fullmatch(reader.schema[0].text):
        sv = reader.schema[0].text
    return _Shape(sv, reader.entries, texts)


# ---- the backlog on disk ----

def _open_dir(top):
    """A descriptor of <top>/.dev-workflows, a real directory by lstat and opened without following a link."""
    path = os.path.join(top, BACKLOG_DIR)
    try:
        st = os.lstat(path)
    except OSError:
        raise NotRun(WHY_DIR)
    if not stat.S_ISDIR(st.st_mode):
        raise NotRun(WHY_DIR)
    try:
        dfd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    except OSError:
        raise NotRun(WHY_DIR)
    fst = os.fstat(dfd)
    if not stat.S_ISDIR(fst.st_mode) or (fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino):
        os.close(dfd)
        raise NotRun(WHY_DIR)
    return dfd


def _read_backlog(top):
    """(bytes, mode) of the backlog -- at most SHAPE_CAP + 1 bytes, which is enough to call it too large. It is a
    regular file by lstat, opened without following a link and never waited on; anything else is NotRun."""
    dfd = _open_dir(top)
    try:
        try:
            st = os.stat(BACKLOG_NAME, dir_fd=dfd, follow_symlinks=False)
        except OSError:
            raise NotRun(WHY_FILE)
        if not stat.S_ISREG(st.st_mode):
            raise NotRun(WHY_FILE)
        try:
            fd = os.open(BACKLOG_NAME, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
                         dir_fd=dfd)
        except OSError:
            raise NotRun(WHY_READ)
        try:
            fst = os.fstat(fd)
            if not stat.S_ISREG(fst.st_mode) or (fst.st_dev, fst.st_ino) != (st.st_dev, st.st_ino):
                raise NotRun(WHY_FILE)
            chunks, left = [], SHAPE_CAP + 1
            while left > 0:
                b = os.read(fd, min(left, 1 << 20))
                if not b:
                    break
                chunks.append(b)
                left -= len(b)
        except OSError:
            raise NotRun(WHY_READ)
        finally:
            os.close(fd)
    finally:
        os.close(dfd)
    _IO["reads"] += 1
    return b"".join(chunks), stat.S_IMODE(fst.st_mode)


def _write_backlog(top, data, mode):
    """Replace the backlog with `data` atomically: a new file beside it, written and synced, renamed over it. The
    backlog must still be a regular file; nothing is written through a link. OSError or NotRun where it cannot."""
    dfd = _open_dir(top)
    tmpname = None
    try:
        st = os.stat(BACKLOG_NAME, dir_fd=dfd, follow_symlinks=False)
        if not stat.S_ISREG(st.st_mode):
            raise NotRun(WHY_FILE)
        tmpname = ".%s.%d.%s.tmp" % (BACKLOG_NAME, os.getpid(), os.urandom(4).hex())
        fd = os.open(tmpname, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600, dir_fd=dfd)
        try:
            view = memoryview(data)
            while view:
                view = view[os.write(fd, view):]
            os.fchmod(fd, mode)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.replace(tmpname, BACKLOG_NAME, src_dir_fd=dfd, dst_dir_fd=dfd)
        tmpname = None
        _IO["writes"] += 1
    finally:
        if tmpname is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmpname, dir_fd=dfd)
        os.close(dfd)


# ---- git ----

GIT_SET = {"GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"}


def _git_env():
    """The script's environment less every GIT_ variable -- so a stray GIT_DIR, GIT_WORK_TREE or GIT_INDEX_FILE never
    points git away from <top> -- plus no prompt, no optional lock and no fetch of an object a partial clone lacks."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_SET)
    return env


def _git(top, *args):
    """(git's exit code, its stdout) for `git -C <top> <args>`, an argument list and no shell, within GIT_TIMEOUT
    seconds; None where git cannot be started or does not finish. Its stderr is discarded, never printed."""
    _IO["git"] += 1
    try:
        r = subprocess.run(["git", "-C", top, *args], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, env=_git_env(), timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.returncode, r.stdout


def _require_top(top):
    """NotRun unless <top> is the top level of a git work tree."""
    r = _git(top, "rev-parse", "--show-toplevel")
    if r is None:
        raise NotRun(WHY_NO_GIT)
    path = r[1].rstrip(b"\n")
    if r[0] != 0 or not path or os.path.realpath(os.fsdecode(path)) != os.path.realpath(top):
        raise NotRun(WHY_NOT_TOP)


def _oid(r):
    """The object id a `git rev-parse` or `git merge-base` answered with; None where it did not."""
    if r is None or r[0] != 0:
        return None
    text = r[1].decode("ascii", "replace").strip()
    return text if OBJECT_ID_RE.fullmatch(text) else None


# ---- check ----

def cmd_check(top):
    data, _ = _read_backlog(top)
    try:
        shape = read_shape(data)
    except Out as o:
        return 0, {"shape": "out", "line": o.line, "reason": o.reason}
    counts = {}
    for e in shape.entries:
        counts[e.id] = counts.get(e.id, 0) + 1
    return 0, {"shape": "ok", "schema_version": shape.schema_version, "units": len(shape.entries),
               "duplicates": [i for i, c in counts.items() if c > 1 and _unit_id(i)],
               "duplicates_outside_class": sum(1 for i, c in counts.items() if c > 1 and not _unit_id(i)),
               "ids_outside_class": sum(1 for e in shape.entries if not _unit_id(e.id))}


# ---- moved ----

ABSENT, ERROR = "absent", "error"
FILE_MODES = (b"100644", b"100755")


def _tree_entry(top, commit):
    """(mode, type, object id) of the backlog in `commit`'s tree; ABSENT where there is none; ERROR where git cannot
    say."""
    r = _git(top, "ls-tree", "-z", "--full-tree", commit, "--", BACKLOG_PATH)
    if r is None or r[0] != 0:
        return ERROR
    for record in r[1].split(b"\0"):
        head, tab, name = record.partition(b"\t")
        fields = head.split(b" ")
        if tab and name == BACKLOG_PATH.encode() and len(fields) == 3:
            return fields[0], fields[1], fields[2].decode("ascii", "replace")
    return ABSENT


def _ref_blob(top, base_oid, oid):
    """None where the ref is not kept: merged into the base, no backlog in its tree, or the same backlog as its merge
    base's. ERROR where it is kept and cannot be read. Otherwise the backlog's bytes, at most REF_CAP of them, read by
    object id."""
    if not OBJECT_ID_RE.fullmatch(oid):
        return ERROR
    r = _git(top, "merge-base", "--is-ancestor", oid, base_oid)
    if r is None or r[0] not in (0, 1):
        return ERROR
    if r[0] == 0:
        return None
    entry = _tree_entry(top, oid)
    if entry is ERROR:
        return ERROR
    if entry is ABSENT:
        return None
    mb = _git(top, "merge-base", base_oid, oid)
    if mb is None or mb[0] not in (0, 1):
        return ERROR
    mb_oid = _oid(mb)
    if mb_oid is not None:  # with no merge base at all the ref is kept: there is nothing to compare it with
        mb_entry = _tree_entry(top, mb_oid)
        if mb_entry is ERROR:
            return ERROR
        if mb_entry == entry:
            return None
    mode, kind, blob = entry
    if mode not in FILE_MODES or kind != b"blob" or not OBJECT_ID_RE.fullmatch(blob):
        return ERROR
    size = _git(top, "cat-file", "-s", blob)
    text = size[1].strip() if size is not None and size[0] == 0 else b""
    if not text.isdigit() or int(text) > REF_CAP:
        return ERROR
    r = _git(top, "cat-file", "blob", blob)
    if r is None or r[0] != 0 or len(r[1]) != int(text):
        return ERROR
    return r[1]


def cmd_moved(top, base, ids):
    _require_top(top)
    data, _ = _read_backlog(top)
    try:
        working = read_shape(data)
    except Out:
        raise NotRun(WHY_WORKING_SHAPE)
    own = {}
    for uid in ids:
        hits = [e for e in working.entries if e.id == uid]
        if len(hits) != 1:
            raise NotRun(WHY_WORKING_ID)
        own[uid] = hits[0].keys["status"].value.text
    head = _git(top, "symbolic-ref", "--quiet", "HEAD")
    if head is None or head[0] not in (0, 1):
        raise NotRun(WHY_HEAD)
    head_ref = head[1].decode("utf-8", "surrogateescape").strip() if head[0] == 0 else None
    base_oid = None
    for ref in ("refs/remotes/origin/" + base, "refs/heads/" + base):
        base_oid = _oid(_git(top, "rev-parse", "--verify", "--quiet", "--end-of-options", ref + "^{commit}"))
        if base_oid is not None:
            break
    if base_oid is None:
        raise NotRun(WHY_NO_BASE)
    # The full name is listed beside the short one, and the drops compare full names: the short name of
    # refs/remotes/origin/HEAD is "origin", and a local branch can shadow another ref's short name.
    r = _git(top, "for-each-ref", "--sort=-committerdate", "--format=%(objectname) %(refname) %(refname:short)",
             "refs/heads", "refs/remotes/origin")
    if r is None or r[0] != 0:
        raise NotRun(WHY_LIST)
    drop = {"refs/remotes/origin/HEAD", "refs/heads/" + base, "refs/remotes/origin/" + base, head_ref}
    remaining, outside = [], 0
    for row in r[1].decode("utf-8", "surrogateescape").split("\n"):
        if not row:
            continue
        parts = row.split(" ")
        if len(parts) != 3:
            outside += 1
            continue
        oid, full, short = parts
        if full in drop:
            continue
        if not BRANCH_RE.fullmatch(short):
            outside += 1
            continue
        remaining.append((oid, short))
    moved, unreadable, examined, kept = {}, [], 0, 0
    for oid, name in remaining:
        if examined == EXAMINE_CAP or kept == READ_REFS_CAP:
            break
        examined += 1
        blob = _ref_blob(top, base_oid, oid)
        if blob is None:
            continue
        kept += 1
        theirs = None
        if blob is not ERROR:
            try:
                shape = read_shape(blob)
                theirs = {}
                for uid in ids:
                    hits = [e for e in shape.entries if e.id == uid]
                    if len(hits) > 1 or (hits and not STATUS_RE.fullmatch(hits[0].keys["status"].value.text)):
                        theirs = None
                        break
                    if hits:
                        theirs[uid] = hits[0].keys["status"].value.text
            except Out:
                theirs = None
        if theirs is None:
            unreadable.append(name)
            continue
        for uid, status in theirs.items():
            if status != own[uid]:
                moved.setdefault(uid, []).append(name)
    return 0, {"moved": {uid: moved[uid] for uid in ids if uid in moved}, "unreadable": unreadable, "read": kept,
               "more": len(remaining) - examined, "names_outside_class": outside}


# ---- edit ----

HUNK_RE = re.compile(rb"@@ -([0-9]+)(?:,([0-9]+))? \+([0-9]+)(?:,([0-9]+))? @@")


def _diff_lines(out):
    """(the old side's removed line numbers, the new side's added ones) of a diff's hunks, each hunk's body read
    against its header; None where a body does not match its header."""
    removed, added = set(), set()
    lines = out.split(b"\n")
    k = 0
    while k < len(lines):
        m = HUNK_RE.match(lines[k])
        k += 1
        if not m:
            continue
        old, left_old = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        new, left_new = int(m.group(3)), int(m.group(4) if m.group(4) is not None else 1)
        while left_old > 0 or left_new > 0:
            if k == len(lines):
                return None
            body = lines[k]
            k += 1
            mark = body[:1]
            if mark == b"\\":
                continue
            if mark == b" " and left_old > 0 and left_new > 0:
                old, new, left_old, left_new = old + 1, new + 1, left_old - 1, left_new - 1
            elif mark == b"-" and left_old > 0:
                removed.add(old)
                old, left_old = old + 1, left_old - 1
            elif mark == b"+" and left_new > 0:
                added.add(new)
                new, left_new = new + 1, left_new - 1
            else:
                return None
    return removed, added


def _scalar_text(value):
    """A page_path value's text as YAML reads it, where this reader can say; None where it cannot."""
    if value.kind == "plain":
        return value.text
    if value.kind == "squote":
        return value.text[1:-1].replace("''", "'")
    if value.kind == "dquote" and "\\" not in value.text:
        return value.text[1:-1]
    return None


def _replace(line, value, new):
    """`line` with `value`'s token replaced by `new`; an empty value takes ` <new>` right after its colon. The indent,
    the key, any trailing comment and the line ending are kept."""
    if value.kind == "empty":
        return line[:value.start] + " " + new + line[value.start:]
    return line[:value.start] + new + line[value.end:]


def _refuse(why, line=None, reason=None):
    return 3, {"refused": why, "line": line, "reason": reason}


def cmd_edit(top, uid, status, page_path):
    _require_top(top)
    data, mode = _read_backlog(top)
    try:
        shape = read_shape(data)
    except Out as o:
        return _refuse("shape", o.line, o.reason)
    hits = [e for e in shape.entries if e.id == uid]
    if not hits:
        return _refuse("id-absent")
    if len(hits) > 1:
        return _refuse("id-twice")
    entry = hits[0]
    texts = list(shape.texts)
    st = entry.keys["status"]
    texts[st.line - 1] = _replace(texts[st.line - 1], st.value, status)
    if page_path is not None:
        pp = entry.keys.get("page_path")
        if pp is None:
            return _refuse("no-page-path", entry.first)
        unset = (pp.value.kind == "empty" and not pp.had_child) or (
            pp.value.kind == "plain" and pp.value.text in ("null", "~"))
        if unset:
            texts[pp.line - 1] = _replace(texts[pp.line - 1], pp.value, page_path)
        elif pp.had_child or _scalar_text(pp.value) != page_path:
            return _refuse("page-path-set", pp.line)
    new_data = "\n".join(texts).encode("utf-8")
    changed = [k + 1 for k, (a, b) in enumerate(zip(shape.texts, texts)) if a != b]
    # What it is about to write must read back as the edit, in shape, the entry where it was.
    try:
        after = read_shape(new_data)
    except Out:
        raise NotRun(WHY_INTERNAL)
    back = [e for e in after.entries if e.id == uid]
    if (len(back) != 1 or (back[0].first, back[0].last) != (entry.first, entry.last)
            or back[0].keys["status"].value.text != status
            or (page_path is not None and _scalar_text(back[0].keys["page_path"].value) != page_path)
            or not all(entry.first <= k <= entry.last for k in changed)):
        raise NotRun(WHY_INTERNAL)
    if _read_backlog(top)[0] != data:
        return _refuse("changed-while-reading")
    try:
        _write_backlog(top, new_data, mode)
    except OSError:
        raise NotRun(WHY_WRITE)
    result = {"first": entry.first, "last": entry.last, "changed": changed}
    why = None
    try:
        r = _git(top, "diff", "-U0", "--no-color", "--no-ext-diff", "--no-textconv", "--", BACKLOG_PATH)
        lines = _diff_lines(r[1]) if r is not None and r[0] == 0 else None
        if lines is None:
            why = "diff-failed"
        elif lines[0] != set(changed) or lines[1] != set(changed):
            why = "hunk-outside"
    except Exception:  # whatever went wrong after the write, the write is undone
        why = "diff-failed"
    if why is None:
        return 0, result
    try:
        _write_backlog(top, data, mode)
    except (OSError, NotRun):
        raise NotRun(WHY_UNDO)
    return 4, dict({"undone": why}, **result)


# ---- the command line ----

class _Parser(argparse.ArgumentParser):
    """argparse, whose refusal is the one fixed usage line: its own message can echo an argument."""

    def error(self, message):
        raise NotRun(WHY_USAGE)


def _unit_id(s):
    return UNIT_ID_RE.fullmatch(s) is not None


def _page_path(s):
    return PAGE_PATH_RE.fullmatch(s) is not None and all(seg not in ("", ".", "..") for seg in s.split("/"))


def _args(argv):
    """(the subcommand's function, its arguments), every flag checked; NotRun names the first that fails, and nothing
    is read or run before every flag has passed."""
    # argparse takes --name=value as the flag and its value, and the last of a repeated flag, so a value a caller
    # lets through after its own could replace it. A value is always its own argument, and never opens with -.
    if any(t.startswith("--") and "=" in t for t in argv) or any(argv.count(f) > 1 for f in SINGLE_FLAGS):
        raise NotRun(WHY_USAGE)
    ap = _Parser(prog="backlog-lines.py", add_help=False, allow_abbrev=False)
    sub = ap.add_subparsers(dest="verb")
    cp = sub.add_parser("check", add_help=False, allow_abbrev=False)
    cp.add_argument("--repo")
    mp = sub.add_parser("moved", add_help=False, allow_abbrev=False)
    mp.add_argument("--repo")
    mp.add_argument("--base")
    mp.add_argument("--id", action="append")
    ep = sub.add_parser("edit", add_help=False, allow_abbrev=False)
    ep.add_argument("--repo")
    ep.add_argument("--id", action="append")
    ep.add_argument("--status")
    ep.add_argument("--page-path")
    a = ap.parse_args(argv)
    if a.verb not in ("check", "moved", "edit") or not a.repo:
        raise NotRun(WHY_USAGE)
    if a.verb == "check":
        checks = []
    elif a.verb == "moved":
        if a.base is None or not a.id:
            raise NotRun(WHY_USAGE)
        checks = [(all(_unit_id(i) for i in a.id), WHY_ID), (BRANCH_RE.fullmatch(a.base) is not None, WHY_BASE)]
    else:
        if a.status is None or not a.id or len(a.id) != 1:
            raise NotRun(WHY_USAGE)
        checks = [(_unit_id(a.id[0]), WHY_ID),
                  (STATUS_RE.fullmatch(a.status) is not None and a.status not in STATUS_RESERVED, WHY_STATUS),
                  (a.page_path is None or _page_path(a.page_path), WHY_PAGE_PATH)]
    for ok, why in checks:
        if not ok:
            raise NotRun(why)
    if not os.path.isdir(a.repo):
        raise NotRun(WHY_REPO)
    if a.verb == "check":
        return cmd_check, (a.repo,)
    if a.verb == "moved":
        return cmd_moved, (a.repo, a.base, list(dict.fromkeys(a.id)))
    return cmd_edit, (a.repo, a.id[0], a.status, a.page_path)


def _drop_stdout():
    """Point stdout's descriptor at the null device, so the interpreter's own flush at exit has nothing left to fail
    on and prints nothing of its own."""
    try:
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, sys.stdout.fileno())
        os.close(null)
    except (OSError, ValueError, AttributeError, io.UnsupportedOperation):
        pass


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    try:
        verb, args = _args(argv)
        code, obj = verb(*args)
        text = json.dumps(obj, indent=2, ensure_ascii=True) + "\n"
    except NotRun as e:
        sys.stderr.write("backlog-lines: not run (%s)\n" % e.args[0])
        return 2
    except Exception:  # anything else is a defect here; its text could carry the backlog's, so it is never printed
        sys.stderr.write("backlog-lines: not run (%s)\n" % WHY_INTERNAL)
        return 2
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except BrokenPipeError:  # the reader closed stdout first: nobody is left to read it
        _drop_stdout()
        return code
    except Exception:  # a full disk, an I/O error: stdout may hold part of the object, and the line says so
        _drop_stdout()
        sys.stderr.write("backlog-lines: not run (%s)\n" % WHY_INTERNAL)
        return 2
    return code


# ==== selftest ====

BF_PATH = os.path.join(HERE, os.pardir, "references", "docs-audit", "backlog-format.md")
BF_LEAD = "**The line shape a backlog run reads.**"
MINI = ("schema_version: 1\n"                          # 1
        "units:\n"                                     # 2
        "  - id: U-001\n"                              # 3
        "    title: \"Place an order\"\n"              # 4
        "    roles: [customer]\n"                      # 5
        "    status: missing             # missing|drafted\n"  # 6
        "    page_path: null\n"                        # 7
        "    blocked_by: []\n"                         # 8
        "threshold: 2\n")                              # 9
DRAFTED = MINI.replace("status: missing", "status: drafted")
STATUS6 = "    status: missing             # missing|drafted\n"


class _Fail(Exception):
    pass


def _eq(got, want, what=""):
    if got != want:
        raise _Fail("%s: got %r, want %r" % (what, got, want))


def _true(cond, what):
    if not cond:
        raise _Fail(what)


def _bf_sample():
    """BF section 1's schema block, verbatim: the text between its ```yaml fence and the fence closing it."""
    with open(BF_PATH, encoding="utf-8") as fh:
        text = fh.read()
    section = text.split("\n## 1. The schema\n", 1)[1]
    return section.split("\n```yaml\n", 1)[1].split("\n```\n", 1)[0] + "\n"


def _put(top, data):
    d = os.path.join(top, BACKLOG_DIR)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, BACKLOG_NAME), "wb") as fh:
        fh.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def _get(top):
    with open(os.path.join(top, BACKLOG_DIR, BACKLOG_NAME), "rb") as fh:
        return fh.read()


def _fx(cwd, *args):
    """A fixture's git command, its stdout; HOME is the case's empty directory, so no user configuration is read."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})
    r = subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid",
                        "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false", "-c", "core.autocrlf=false",
                        *args], cwd=cwd, env=env, check=True, stdin=subprocess.DEVNULL, capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def _repo(tmp, data, name="top", branch="main"):
    """A git repository at <tmp>/<name> whose one commit holds the backlog `data`."""
    top = os.path.join(tmp, name)
    os.makedirs(top)
    _fx(top, "init", "-q", "-b", branch)
    _put(top, data)
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "backlog")
    return top


def _branch_with(top, name, data, start="main"):
    """A branch `name` cut from `start` whose one commit sets the backlog to `data` (None removes it); HEAD stays."""
    head = _fx(top, "symbolic-ref", "--short", "HEAD").strip()
    _fx(top, "switch", "-q", "-c", name, start)
    if data is None:
        _fx(top, "rm", "-q", BACKLOG_PATH)
    else:
        _put(top, data)
        _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "backlog on a branch")
    _fx(top, "switch", "-q", head)


def _call(argv):
    """(exit code, stdout, stderr) of main(argv), run in this process with _IO reset first."""
    for k in _IO:
        _IO[k] = 0
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


def _obj(out):
    obj = json.loads(out)
    _true(isinstance(obj, dict), "stdout is one JSON object")
    return obj


def _refused(code, out, err, why):
    _eq((code, out, err), (2, "", "backlog-lines: not run (%s)\n" % why), "exit 2")


def _check(top):
    code, out, err = _call(["check", "--repo", top])
    _eq((code, err), (0, ""), "check's exit and stderr")
    return _obj(out)


def _shape(tmp, data, name="top"):
    top = os.path.join(tmp, name)
    _put(top, data)
    return _check(top)


def _out(tmp, data, line, reason, name="top"):
    _eq(_shape(tmp, data, name), {"shape": "out", "line": line, "reason": reason}, name)


def _ok(units=1, schema="1", duplicates=(), dup_out=0, ids_out=0):
    return {"shape": "ok", "schema_version": schema, "units": units, "duplicates": list(duplicates),
            "duplicates_outside_class": dup_out, "ids_outside_class": ids_out}


def _moved(top, *ids, base="main"):
    argv = ["moved", "--repo", top, "--base", base]
    for i in ids:
        argv += ["--id", i]
    return _call(argv)


def _moved_ok(top, *ids, base="main"):
    code, out, err = _moved(top, *ids, base=base)
    _eq((code, err), (0, ""), "moved's exit and stderr")
    return _obj(out)


def _edit(top, uid, status, page_path=None):
    argv = ["edit", "--repo", top, "--id", uid, "--status", status]
    if page_path is not None:
        argv += ["--page-path", page_path]
    return _call(argv)


# ---- the shape ----

def case_bf_sample_in_shape(tmp):
    """BF section 1's own schema, read from the reference itself, is in shape: one unit, schema_version 1."""
    _eq(_shape(tmp, _bf_sample()), _ok(units=1, schema="1"))


def case_crlf_ok(tmp):
    _eq(_shape(tmp, _bf_sample().replace("\n", "\r\n")), _ok(units=1, schema="1"))


def case_quoted_scalars_in(tmp):
    data = MINI.replace("    title: \"Place an order\"\n",
                        "    title: 'it''s'\n" + r'    priority_reason: "a \" b"' + "\n"
                        + r'    note: "ends \\"' + "\n")
    _eq(_shape(tmp, data), _ok())


def case_block_scalar_out(tmp):
    """A hand-edited priority_reason block holding a line that looks like an entry."""
    _out(tmp, MINI.replace("    roles: [customer]\n", "    priority_reason: |\n      - id: U-002\n"), 5,
         "block-scalar")


def case_quoted_multiline_out(tmp):
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: \"Place an\n      order\"\n"), 4,
         "unclosed-quote")
    # Inside a flow collection a quote between tokens -- after a closing quote, a `:` or a `?` -- opens a quoted scalar
    # to a YAML reader, and this one runs past the line; inside a plain scalar a quote is the scalar's.
    for name, line in (("after-quote", "    roles: [\"a\"' b]\n"), ("after-colon", "    roles: [a, :'b]\n"),
                       ("after-question", "    roles: [a?'b]\n"), ("after-dash", "    roles: [- 'b]\n")):
        _out(tmp, MINI.replace("    roles: [customer]\n", line), 5, "unclosed-quote", name)
    _eq(_shape(tmp, MINI.replace("    roles: [customer]\n", "    roles: [it's, a 'b c, x:'y]\n"), "in-plain"), _ok())


def case_flow_multiline_out(tmp):
    _out(tmp, MINI.replace("    roles: [customer]\n", "    roles: [customer,\n      admin]\n"), 5, "unclosed-flow")
    # A # between a flow's tokens opens a comment to a YAML reader, so the collection goes on to the next line.
    for name, line in (("bracket", "    roles: [#customer]\n"), ("quote", "    roles: [\"a\"#b]\n"),
                       ("comma", "    roles: [a,#b]\n")):
        _out(tmp, MINI.replace("    roles: [customer]\n", line), 5, "unclosed-flow", name)
    _eq(_shape(tmp, MINI.replace("    roles: [customer]\n", "    roles: [a#b, c]\n"), "in-plain"), _ok())


def case_continuation_out(tmp):
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: Place an\n      order\n"), 5,
         "continuation", "deeper")
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: Place an\n    order\n"), 5,
         "continuation", "level")


def case_nested_continuation_out(tmp):
    """A deeper `- ` line under a key with a value on its line is that value's plain continuation to a YAML reader --
    status "missing - drafted" -- so it is out of shape, never read as a list under the key."""
    _out(tmp, MINI.replace(STATUS6, STATUS6 + "      - drafted\n"), 7, "continuation")


def case_anchor_alias_tag_tab_out(tmp):
    title = "    title: \"Place an order\"\n"
    for name, line, reason in (("anchor", "    title: &t Place an order\n", "anchor"),
                               ("alias", "    title: *t\n", "alias"),
                               ("tag", "    title: !!str Place an order\n", "tag"),
                               ("tab", "    title:\t\"Place an order\"\n", "tab"),
                               ("flow-anchor", "    title: [&t a]\n", "anchor")):
        _out(tmp, MINI.replace(title, line), 4, reason, name)


def case_control_out(tmp):
    title = "    title: \"Place an order\"\n"
    for name, line in (("cr", "    title: a\rb\n"), ("ls", "    title: a b\n"), ("nel", "    title: a\u0085b\n"),
                       ("vt", "    title: a\x0bb\n")):
        _out(tmp, MINI.replace(title, line), 4, "control", name)
    _out(tmp, MINI + "# the end\r", 10, "control", "cr-at-eof")


def case_encoding_out(tmp):
    _out(tmp, MINI.encode("utf-8").replace(b"Place an order", b"caf\xe9"), 4, "encoding")


def case_key_out(tmp):
    _out(tmp, MINI.replace(STATUS6, "    \"status\": drafted\n" + STATUS6), 6, "key", "quoted")
    _out(tmp, MINI.replace(STATUS6, "    status : missing\n"), 6, "key", "spaced")
    _out(tmp, MINI.replace(STATUS6, "    ? x\n" + STATUS6), 6, "key", "complex")


def case_second_id_out(tmp):
    _out(tmp, MINI.replace("    roles: [customer]\n", "    id: U-002\n    roles: [customer]\n"), 5, "duplicate-key")


def case_duplicate_status_out(tmp):
    _out(tmp, MINI.replace("    page_path: null\n", "    page_path: null\n    status: drafted\n"), 8,
         "duplicate-key")


def case_column0_entries_out(tmp):
    """units: followed by its entries at column 0, a block sequence at its key's own indent -- and the same inside an
    entry, roles: followed by its items at the entry's key indent."""
    _out(tmp, "schema_version: 1\nunits:\n- id: U-001\n  status: missing\n", 3, "indent")
    _out(tmp, MINI.replace("    roles: [customer]\n", "    roles:\n    - customer\n"), 6, "indent", "in-entry")


def case_nbsp_indent_out(tmp):
    """An entry key indented with U+00A0: after the key indent's spaces, and in place of them."""
    _out(tmp, MINI.replace(STATUS6, "     status: missing\n"), 6, "indent", "after")
    _out(tmp, MINI.replace(STATUS6, "    status: missing\n"), 6, "indent", "instead")


def case_trailing_text_out(tmp):
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: \"a\" b\n"), 4, "trailing", "quote")
    _out(tmp, MINI.replace("    roles: [customer]\n", "    roles: [a] b\n"), 5, "trailing", "flow")


def case_status_missing_out(tmp):
    _out(tmp, MINI.replace(STATUS6, ""), 3, "status")


def case_status_flow_out(tmp):
    _out(tmp, MINI.replace(STATUS6, "    status: [missing]\n"), 6, "status")


def case_entry_indent_non_id_out(tmp):
    _out(tmp, MINI.replace("threshold: 2\n", "  - title: x\n    status: missing\nthreshold: 2\n"), 9, "entry-opener")


def case_too_large_out(tmp):
    data = MINI.encode("utf-8") + (b"# " + b"x" * 1021 + b"\n") * 8193
    _true(len(data) > SHAPE_CAP, "the fixture is above 8 MiB")
    _out(tmp, data, 0, "too-large")


def case_units_twice_out(tmp):
    _out(tmp, MINI + "units:\n  - id: U-002\n    status: missing\n", 10, "units-twice")


def case_units_flow_out(tmp):
    _out(tmp, "schema_version: 1\nunits: [{id: U-1}]\n", 2, "units-not-block")


def case_units_empty_ok(tmp):
    _eq(_shape(tmp, "schema_version: 1\nunits: []\n"), _ok(units=0))


def case_under_indent_out(tmp):
    _out(tmp, MINI.replace("threshold: 2\n", " stray: x\nthreshold: 2\n"), 9, "indent", "under-units")
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "   title: \"Place an order\"\n"), 4, "indent",
         "under-key")


def case_id_quoted_out(tmp):
    _out(tmp, MINI.replace("  - id: U-001\n", "  - id: \"U-001\"\n"), 3, "entry-opener")


def case_duplicate_id(tmp):
    more = "  - id: U-001\n    status: drafted\n  - id: x y\n    status: missing\nthreshold: 2\n"
    _eq(_shape(tmp, MINI.replace("threshold: 2\n", more), "one"), _ok(units=3, duplicates=["U-001"], ids_out=1))
    twice = "  - id: x y\n    status: drafted\n  - id: x y\n    status: missing\nthreshold: 2\n"
    top = os.path.join(tmp, "two")
    _put(top, MINI.replace("threshold: 2\n", twice))
    code, out, err = _call(["check", "--repo", top])
    _eq(_obj(out), _ok(units=3, dup_out=1, ids_out=2), "outside the class")
    _true("x y" not in out + err, "an id outside the class is never printed")


def case_symlink_refused(tmp):
    """A symbolic link at the backlog, or at .dev-workflows, is refused, never followed: exit 2, nothing read."""
    elsewhere = os.path.join(tmp, "elsewhere")
    _put(elsewhere, MINI)
    target = os.path.join(elsewhere, BACKLOG_DIR, BACKLOG_NAME)
    for name, why in (("file", WHY_FILE), ("dir", WHY_DIR)):
        top = _repo(tmp, MINI, name)
        if name == "file":
            os.remove(os.path.join(top, BACKLOG_DIR, BACKLOG_NAME))
            os.symlink(target, os.path.join(top, BACKLOG_DIR, BACKLOG_NAME))
        else:
            os.remove(os.path.join(top, BACKLOG_DIR, BACKLOG_NAME))
            os.rmdir(os.path.join(top, BACKLOG_DIR))
            os.symlink(os.path.join(elsewhere, BACKLOG_DIR), os.path.join(top, BACKLOG_DIR))
        for argv in (["check", "--repo", top], ["moved", "--repo", top, "--base", "main", "--id", "U-001"],
                     ["edit", "--repo", top, "--id", "U-001", "--status", "drafted"]):
            code, out, err = _call(argv)
            _refused(code, out, err, why)
            _eq((_IO["reads"], _IO["writes"]), (0, 0), "%s %s: nothing read or written" % (name, argv[0]))
    _eq(_get(elsewhere), MINI.encode("utf-8"), "the link's target")


def case_not_regular_refused(tmp):
    """A directory or a FIFO at the backlog's path is no regular file: exit 2 at once, nothing read."""
    for name in ("directory", "fifo"):
        top = os.path.join(tmp, name)
        os.makedirs(os.path.join(top, BACKLOG_DIR))
        path = os.path.join(top, BACKLOG_DIR, BACKLOG_NAME)
        os.mkdir(path) if name == "directory" else os.mkfifo(path)
        code, out, err = _call(["check", "--repo", top])
        _refused(code, out, err, WHY_FILE)
        _eq(_IO["reads"], 0, name)


# ---- moved ----

def case_moved_on_branch(tmp):
    seed = _repo(tmp, MINI, "seed")
    up = os.path.join(tmp, "up.git")
    _fx(tmp, "clone", "-q", "--bare", seed, up)
    top = os.path.join(tmp, "top")
    _fx(tmp, "clone", "-q", up, top)
    _branch_with(top, "feat/a", DRAFTED)
    _eq(_moved_ok(top, "U-001"), {"moved": {"U-001": ["feat/a"]}, "unreadable": [], "read": 1, "more": 0,
                                  "names_outside_class": 0}, "on a branch")
    _fx(top, "switch", "-q", "feat/a")  # HEAD's own branch is never examined: the working backlog is its
    _eq(_moved_ok(top, "U-001"), {"moved": {}, "unreadable": [], "read": 0, "more": 0, "names_outside_class": 0},
        "HEAD's branch")
    _fx(top, "switch", "-q", "-c", "ahead", "main")  # a local <base> ahead of origin/<base> is never examined either
    _fx(top, "switch", "-q", "main")
    _put(top, DRAFTED)
    _fx(top, "commit", "-qam", "unpushed move on main")
    _fx(top, "switch", "-q", "ahead")
    _eq(_moved_ok(top, "U-001")["moved"], {"U-001": ["feat/a"]}, "a local base ahead of its remote")
    _fx(top, "switch", "-q", "main")
    _fx(top, "reset", "-q", "--hard", "origin/main")
    _fx(top, "switch", "-q", "-c", "work")
    _fx(top, "switch", "-q", "main")
    _fx(top, "merge", "-q", "--no-ff", "-m", "merge feat/a", "feat/a")
    _fx(top, "push", "-q", "origin", "main")
    _fx(top, "switch", "-q", "work")
    _eq(_moved_ok(top, "U-001"), {"moved": {}, "unreadable": [], "read": 0, "more": 0, "names_outside_class": 0},
        "merged into origin/main")


def case_ref_name_outside_class(tmp):
    top = _repo(tmp, MINI)
    _branch_with(top, "x$(id)", DRAFTED)
    code, out, err = _moved(top, "U-001")
    _eq((code, err), (0, ""))
    _eq(_obj(out), {"moved": {}, "unreadable": [], "read": 0, "more": 0, "names_outside_class": 1})
    _true("$(" not in out + err and "x$" not in out + err, "the name is printed nowhere")


def case_ref_unreadable(tmp):
    top = _repo(tmp, MINI)
    _branch_with(top, "bad-shape",
                 MINI.replace("    roles: [customer]\n", "    priority_reason: |\n      - id: U-002\n"))
    big = DRAFTED + ("# " + "x" * 1021 + "\n") * 1127
    _true(REF_CAP < len(big.encode("utf-8")) < 2 * REF_CAP, "the fixture is about 1.1 MiB")
    _branch_with(top, "big", big)
    _branch_with(top, "twice", DRAFTED.replace("threshold: 2\n", "  - id: U-001\n    status: drafted\nthreshold: 2\n"))
    _branch_with(top, "odd-status", MINI.replace("status: missing", "status: Drafted!"))
    # A committed symbolic link whose target text is itself a backlog moving the unit: git's blob for it is that
    # text, never a file, so it is unreadable and never read as the backlog.
    _fx(top, "switch", "-q", "-c", "linked")
    os.remove(os.path.join(top, BACKLOG_PATH))
    os.symlink(DRAFTED, os.path.join(top, BACKLOG_PATH))
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "a link")
    _fx(top, "switch", "-q", "main")
    res = _moved_ok(top, "U-001")
    _eq(sorted(res["unreadable"]), ["bad-shape", "big", "linked", "odd-status", "twice"])
    _eq((res["moved"], res["read"]), ({}, 5))


def case_absent_not_moved(tmp):
    top = _repo(tmp, MINI)
    _branch_with(top, "gone", None)
    _branch_with(top, "other", MINI.replace("U-001", "U-009"))
    _eq(_moved_ok(top, "U-001"), {"moved": {}, "unreadable": [], "read": 1, "more": 0, "names_outside_class": 0})


def case_twenty_cap(tmp):
    top = _repo(tmp, MINI)
    _branch_with(top, "b00", DRAFTED)
    tree = _fx(top, "rev-parse", "b00^{tree}").strip()
    main_oid = _fx(top, "rev-parse", "main").strip()
    for k in range(1, 22):
        _fx(top, "branch", "b%02d" % k, _fx(top, "commit-tree", tree, "-p", main_oid, "-m", "b%02d" % k).strip())
    res = _moved_ok(top, "U-001")
    _eq((res["read"], res["more"], len(res["moved"]["U-001"]), res["unreadable"]), (20, 2, 20, []))


def case_examined_cap(tmp):
    """70 in-class refs, none qualifying -- 35 merged into the base, 35 not merged whose backlog is the merge base's,
    newest first -- so 60 are examined, none kept."""
    top = _repo(tmp, MINI)
    main_oid = _fx(top, "rev-parse", "main").strip()
    _fx(top, "switch", "-q", "-c", "side")
    with open(os.path.join(top, "other.txt"), "w", encoding="utf-8") as fh:
        fh.write("not the backlog\n")
    _fx(top, "add", "other.txt")
    _fx(top, "commit", "-qm", "another file")
    side_oid = _fx(top, "rev-parse", "HEAD").strip()
    _fx(top, "switch", "-q", "main")
    _fx(top, "branch", "-q", "-D", "side")
    for k in range(70):
        _fx(top, "update-ref", "refs/heads/m%02d" % k, main_oid if k % 2 else side_oid)
    _eq(_moved_ok(top, "U-001"), {"moved": {}, "unreadable": [], "read": 0, "more": 10, "names_outside_class": 0})


def case_no_base(tmp):
    top = _repo(tmp, MINI, branch="trunk")
    code, out, err = _moved(top, "U-001", base="main")
    _refused(code, out, err, WHY_NO_BASE)


def case_moved_working_refused(tmp):
    """moved compares against the working backlog, so one out of shape, or one not holding an --id once, stops it."""
    top = _repo(tmp, MINI)
    _put(top, MINI.replace("    roles: [customer]\n", "    roles: |\n"))
    code, out, err = _moved(top, "U-001")
    _refused(code, out, err, WHY_WORKING_SHAPE)
    _put(top, MINI)
    code, out, err = _moved(top, "U-001", "U-404")
    _refused(code, out, err, WHY_WORKING_ID)


# ---- edit ----

def case_edit_two_keys(tmp):
    """status and a null page_path changed, every other byte equal, CRLF kept, the diff inside the entry."""
    sample = _bf_sample().replace("docs/guides/place-an-order.md", "null").replace("\n", "\r\n")
    top = _repo(tmp, sample)
    before = _get(top)
    code, out, err = _edit(top, "U-001", "drafted", "docs/guides/new-page.md")
    _eq((code, err), (0, ""), "edit")
    res = _obj(out)
    old = before.split(b"\n")
    st = next(k for k, ln in enumerate(old) if ln.startswith(b"    status: missing"))
    pp = next(k for k, ln in enumerate(old) if ln.startswith(b"    page_path: null"))
    want = list(old)
    want[st] = old[st].replace(b"status: missing", b"status: drafted", 1)
    want[pp] = old[pp].replace(b"page_path: null", b"page_path: docs/guides/new-page.md", 1)
    _true(want[st].endswith(b"\r") and want[pp].endswith(b"\r") and b"#" in want[pp], "CRLF and the comment kept")
    _eq(_get(top).split(b"\n"), want, "every other byte")
    first = old.index(b"  - id: U-001\r") + 1
    last = next(k for k, ln in enumerate(old) if ln.startswith(b"tutorial_candidates:"))
    _eq(res, {"first": first, "last": last, "changed": [st + 1, pp + 1]})
    _eq(_fx(top, "diff", "--numstat"), "2\t2\t%s\n" % BACKLOG_PATH, "git's own count")


def case_edit_tilde_null(tmp):
    for name, line in (("tilde", "    page_path: ~\n"), ("empty", "    page_path:\n")):
        top = _repo(tmp, MINI.replace("    page_path: null\n", line), name)
        code, out, err = _edit(top, "U-001", "drafted", "docs/a.md")
        _eq((code, err), (0, ""), name)
        _eq(_obj(out), {"first": 3, "last": 8, "changed": [6, 7]}, name)
        _eq(_get(top), DRAFTED.replace("    page_path: null\n", "    page_path: docs/a.md\n").encode("utf-8"), name)


def case_edit_page_path_set(tmp):
    data = MINI.replace("page_path: null", "page_path: docs/old.md")
    top = _repo(tmp, data)
    code, out, err = _edit(top, "U-001", "drafted", "docs/new.md")
    _eq((code, err), (3, ""))
    _eq(_obj(out), {"refused": "page-path-set", "line": 7, "reason": None})
    _eq(_get(top), data.encode("utf-8"), "untouched")


def case_edit_page_path_same(tmp):
    data = MINI.replace("page_path: null", "page_path: docs/a.md")
    top = _repo(tmp, data)
    code, out, err = _edit(top, "U-001", "drafted", "docs/a.md")
    _eq((code, err), (0, ""))
    _eq(_obj(out), {"first": 3, "last": 8, "changed": [6]})
    _eq(_get(top), data.replace("status: missing", "status: drafted").encode("utf-8"))


def case_edit_no_page_path_key(tmp):
    data = MINI.replace("    page_path: null\n", "")
    top = _repo(tmp, data)
    code, out, err = _edit(top, "U-001", "drafted", "docs/a.md")
    _eq((code, err), (3, ""))
    _eq(_obj(out), {"refused": "no-page-path", "line": 3, "reason": None})
    _eq(_get(top), data.encode("utf-8"), "untouched")


def case_edit_refused_content(tmp):
    """Out of shape, an id no entry holds, an id two entries hold: exit 3 each, the file byte-equal."""
    two = MINI.replace("threshold: 2\n", "  - id: U-001\n    status: drafted\nthreshold: 2\n")
    for name, data, uid, want in (
            ("shape", MINI.replace("    roles: [customer]\n", "    roles: >\n"), "U-001",
             {"refused": "shape", "line": 5, "reason": "block-scalar"}),
            ("absent", MINI, "U-404", {"refused": "id-absent", "line": None, "reason": None}),
            ("twice", two, "U-001", {"refused": "id-twice", "line": None, "reason": None})):
        top = _repo(tmp, data, name)
        code, out, err = _edit(top, uid, "drafted")
        _eq((code, err), (3, ""), name)
        _eq(_obj(out), want, name)
        _eq(_get(top), data.encode("utf-8"), name + " untouched")


def case_edit_changed_while_reading(tmp):
    """A backlog that changed between the edit's read and its write is refused, exit 3, and the change left alone."""
    top = _repo(tmp, MINI)
    theirs = MINI.replace("threshold: 2\n", "threshold: 3\n").encode("utf-8")
    real = globals()["_read_backlog"]
    calls = []

    def racing(path):
        got = real(path)
        if not calls:
            _put(top, theirs)
        calls.append(path)
        return got
    globals()["_read_backlog"] = racing
    try:
        code, out, err = _edit(top, "U-001", "drafted")
    finally:
        globals()["_read_backlog"] = real
    _eq((code, err), (3, ""))
    _eq(_obj(out), {"refused": "changed-while-reading", "line": None, "reason": None})
    _eq(_get(top), theirs, "the other writer's change stands")


def case_edit_not_a_repository(tmp):
    top = os.path.join(tmp, "top")
    _put(top, MINI)
    code, out, err = _edit(top, "U-001", "drafted")
    _refused(code, out, err, WHY_NOT_TOP)
    _eq(_get(top), MINI.encode("utf-8"), "untouched")


def case_edit_undo(tmp):
    """A backlog already dirty on another line: the diff holds a hunk the edit did not make, so the edit is undone."""
    top = _repo(tmp, MINI)
    dirty = MINI.replace("schema_version: 1\n", "schema_version: 1  # touched\n").encode("utf-8")
    _put(top, dirty)
    code, out, err = _edit(top, "U-001", "drafted")
    _eq((code, err), (4, ""))
    _eq(_obj(out), {"undone": "hunk-outside", "first": 3, "last": 8, "changed": [6]})
    _eq(_get(top), dirty, "byte-equal to what it read")


def case_bad_args(tmp):
    """Every argument outside its class: exit 2, the flag named, nothing read, run or written."""
    top = _repo(tmp, MINI)
    stamp = os.stat(os.path.join(top, BACKLOG_DIR, BACKLOG_NAME)).st_mtime_ns
    for argv, why in (
            (["moved", "--repo", top, "--base", "a;b", "--id", "U-001"], WHY_BASE),
            (["moved", "--repo", top, "--base", "-x", "--id", "U-001"], WHY_USAGE),
            (["moved", "--repo", top, "--base", "main", "--id", "../x"], WHY_ID),
            (["edit", "--repo", top, "--id", "../x", "--status", "drafted"], WHY_ID),
            (["edit", "--repo", top, "--id", "U-001\n", "--status", "drafted"], WHY_ID),
            (["edit", "--repo", top, "--id", "U-001", "--status", "Drafted!"], WHY_STATUS),
            (["edit", "--repo", top, "--id", "U-001", "--status", "null"], WHY_STATUS),
            (["edit", "--repo", top, "--id", "U-001", "--status", "drafted", "--page-path", "a/../b.md"],
             WHY_PAGE_PATH),
            (["edit", "--repo", top, "--id", "U-001", "--status", "drafted", "--page-path", "/abs.md"],
             WHY_PAGE_PATH),
            (["edit", "--repo", top, "--id", "U-001", "--status", "drafted", "--page-path", "a//b.md"],
             WHY_PAGE_PATH),
            (["edit", "--repo", top, "--id", "U-001", "--id", "U-002", "--status", "drafted"], WHY_USAGE),
            (["check", "--repo=" + top], WHY_USAGE),
            (["check", "--repo", top, "--repo", top], WHY_USAGE),
            (["check"], WHY_USAGE)):
        code, out, err = _call(argv)
        _refused(code, out, err, why)
        _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "%r: nothing read, run or written" % (argv[1:],))
    _eq(_get(top), MINI.encode("utf-8"), "untouched")
    _eq(os.stat(os.path.join(top, BACKLOG_DIR, BACKLOG_NAME)).st_mtime_ns, stamp, "not rewritten")


def case_shape_paragraph_pinned(tmp):
    """BF section 1's shape paragraph names, in its out-of-shape list, exactly the reasons this script gives."""
    with open(BF_PATH, encoding="utf-8") as fh:
        text = fh.read()
    at = text.index(BF_LEAD)
    bullet = next(ln for ln in text[at:].split("\n") if ln.startswith("- **Out of shape**"))
    words = [w for group in re.findall(r"\((`[a-z][a-z-]*`(?:, `[a-z][a-z-]*`)*)\)", bullet)
             for w in re.findall(r"`([a-z][a-z-]*)`", group)]
    _eq(sorted(words), sorted(REASONS), "the paragraph's reasons")


CASES = (case_bf_sample_in_shape, case_crlf_ok, case_quoted_scalars_in, case_block_scalar_out,
         case_quoted_multiline_out, case_flow_multiline_out, case_continuation_out, case_nested_continuation_out,
         case_anchor_alias_tag_tab_out, case_control_out, case_encoding_out, case_key_out, case_second_id_out,
         case_duplicate_status_out, case_column0_entries_out, case_nbsp_indent_out, case_trailing_text_out,
         case_status_missing_out, case_status_flow_out, case_entry_indent_non_id_out, case_too_large_out,
         case_units_twice_out, case_units_flow_out, case_units_empty_ok, case_under_indent_out, case_id_quoted_out,
         case_duplicate_id, case_symlink_refused, case_not_regular_refused, case_moved_on_branch,
         case_ref_name_outside_class, case_ref_unreadable, case_absent_not_moved, case_twenty_cap,
         case_examined_cap, case_no_base, case_moved_working_refused, case_edit_two_keys, case_edit_tilde_null,
         case_edit_page_path_set, case_edit_page_path_same, case_edit_no_page_path_key, case_edit_refused_content,
         case_edit_changed_while_reading, case_edit_not_a_repository, case_edit_undo, case_bad_args,
         case_shape_paragraph_pinned)


def selftest():
    # The script's own git drops every GIT_ variable, so the user's global git configuration is kept from it by
    # pointing HOME and XDG_CONFIG_HOME at each case's empty directory; the fixtures' git sets GIT_CONFIG_NOSYSTEM too.
    saved = {k: os.environ.get(k) for k in ("HOME", "XDG_CONFIG_HOME")}
    failed = []
    try:
        for fn in CASES:
            name = fn.__name__[len("case_"):]
            with tempfile.TemporaryDirectory() as tmp:
                tmp = os.path.realpath(tmp)
                os.environ["HOME"] = os.environ["XDG_CONFIG_HOME"] = tmp
                try:
                    fn(tmp)
                    print("ok   " + name)
                except Exception as e:  # any exception is that case failing, and it is named
                    failed.append(name)
                    print("FAIL %s: %s: %s" % (name, type(e).__name__, e))
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    if failed:
        print("selftest: FAIL, %d of %d cases, the first %s" % (len(failed), len(CASES), failed[0]))
        return 1
    print("selftest: %d passed" % len(CASES))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))

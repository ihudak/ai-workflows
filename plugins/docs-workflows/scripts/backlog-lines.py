#!/usr/bin/env python3
r"""backlog-lines.py — the one line reader of the documentation backlog, <top>/.dev-workflows/docs-backlog.yml, and the
export of a source repository's commit for /docs-verify's claim reader.

  backlog-lines.py check --repo <top>
  backlog-lines.py moved --repo <top> --base <name> --id <id> [--id <id> ...] [--own-moves]
  backlog-lines.py edit  --repo <top> --id <id> --status <status> [--page-path <rel>] [--from <status>]
                         [--walkthrough <id>] [--block <token>]
  backlog-lines.py export --repo <clone> --commit <oid> --out <dir> --manifest <file> [--whole]
                         [--path <rel> ...]
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

moved tells which of the --id units the base, or a branch not merged into it, has moved. It resolves the base as
refs/remotes/origin/<base>, else refs/heads/<base>, and reads HEAD's branch itself. The base moves a unit where it
moved it after HEAD's branch left it: where the unit's status in the base's backlog, read by object id within a kept
ref's limits below, differs from its working status and from its status at every merge base of HEAD with the base
(`git merge-base --all`), read the same way -- no backlog or no entry there being a status that differs. No merge base
is read where no unit's status in the base's backlog differs from its working status, and the base moves nothing where
a merge base's backlog is the base's own blob. An absent backlog on the base, or an entry absent there, moves nothing.
Where that cannot be told -- the base's backlog unreadable as a kept ref's is, no merge base (an orphan branch, a
shallow clone), git failing or timing out on the merge bases, or a merge base's backlog unreadable -- the base is
unreadable, never compared with the working backlog alone, and moves nothing. Where the base resolved as
origin/<base>, a local <base> that holds commits origin/<base> lacks -- one that is no ancestor of it -- is read as the
base is, by the same rule, so a move made there and not pushed is seen; a local <base> that is an ancestor of
origin/<base>, which then holds every move it holds, is not read, nor one HEAD is on, and one git cannot place is
unreadable. A limit: a move the local <base> holds and origin/<base> no longer does -- origin/<base> force-pushed
without it, or a local merge of a branch whose pull request was then closed -- is named as an unpushed move is, since
nothing either history holds tells the two apart. It lists `git for-each-ref
--sort=-committerdate` over refs/heads and refs/remotes/origin, each ref with its object id, full name and short name,
and drops refs/remotes/origin/HEAD, HEAD's branch, <base> and origin/<base> -- by full name, since git shortens
refs/remotes/origin/HEAD to "origin" and shortens a ref another one shadows to "heads/..." or "remotes/..." -- and
every ref whose short name is outside the branch class, ^[A-Za-z0-9_][A-Za-z0-9._/@+-]*$, which is counted in
names_outside_class and named nowhere. Of the rest, newest first, it examines at most 60, and keeps each whose object
id is a full object name, ^[0-9a-f]{40}([0-9a-f]{24})?$, that is not merged into the base and whose backlog differs
from its merge base's (or that shares no merge base with the base), stopping once it has kept 20. A kept ref's backlog
is read by its object id with `git cat-file`, at most 1 MiB, and tested as check tests one. An entry absent there, or
a ref with no backlog, is not moved. A backlog over 1 MiB, out of shape, recorded in the tree as anything but a
regular file (a symbolic link's blob is its target's name, never a file), holding one of the ids twice, or giving one
a status outside ^[a-z][a-z-]{0,31}$ -- or a ref git cannot answer for -- makes the ref unreadable. A unit is moved on
a ref where its status there differs from its status in the working backlog, which must be in shape and hold each --id
exactly once. With --own-moves it is moved only where the ref changed that status itself: where the status there also
differs from the unit's status in the backlog at the ref's merge base with the base, so that a branch cut before the
unit moved on the base, still holding the older status, moves nothing. That backlog is read by its object id within a
kept ref's limits, and one those limits make unreadable makes the ref unreadable; no backlog there, or no entry for
the unit, is a status that differs; and a ref sharing no merge base with the base is compared as without the flag.
Without it a merge base's backlog is compared with the ref's by tree entry alone, never read. The flag does not change
how the base or the local <base> is read. It prints {"moved": {<id>: [<ref>...]}, "unreadable": [<ref>...], "base":
{"moved": {<id>: [<ref>...]}, "unreadable": [<ref>...]}, "read": <n>, "more": <n>, "names_outside_class": <n>}:
moved names only the ids the base or some ref moved, the base first, by the name it
resolved as -- origin/<base> or <base> -- then the local <base>, as <base>, where it is read, then each ref by its
short name, newest first; unreadable lists the base first where it is unreadable, then the local <base> where it is
read and unreadable, then each unreadable ref; base holds the part of moved and unreadable that the base and the
local <base> give, so that a caller reads a base off it and never off a printed name, which a ref can share -- a local
branch named origin/<base>, where no remote-tracking ref shadows it, is printed as origin/<base>; read counts the refs
kept, each either compared or unreadable, and never counts the base or the local <base>; more counts every ref past
the point it stopped.

edit writes one unit's move. It refuses, exit 3, the file untouched: a backlog out of shape; an --id no entry or two
entries hold; where --from is given, an entry whose status: is another -- tested before the refusals after it; where
--page-path is given, an entry with no page_path: line, or a page_path already set to another path (null, ~ and an
empty value are unset); where --walkthrough is given, an entry with no walkthrough: line, or a walkthrough already set
to another id, unset as page_path is; where --block is given, an entry with no blocked_by: line, or a blocked_by
holding anything but [] or an empty value; and a backlog that changed while it read it. Where the unit already holds
the values asked for, it writes nothing -- the file keeps its bytes and its mtime -- and prints an empty changed.
Otherwise it replaces the status: value -- and the page_path value where --page-path is given and page_path is unset,
the walkthrough value where --walkthrough is given and walkthrough is unset, and the blocked_by value, by [<token>],
where --block is given -- keeping each line's indent, key, trailing comment and line ending and every other byte;
checks that the result reads back as that edit, in shape, each of those keys holding what was asked; and writes it
atomically, a new file beside the backlog renamed over it. Immediately before the rename it reads the backlog again
and refuses, exit 3, one that no longer holds the bytes it read; after it, it reads the backlog back and requires the
bytes it wrote. That narrows the window in which another writer's change is lost to the instant between the last read
and the rename; it does not close it. Then it runs `git -C <top> diff -U0 --no-color --no-ext-diff --no-textconv --
.dev-workflows/docs-backlog.yml`. Where the lines that diff removes and adds are not exactly the lines it changed, all
inside the entry -- or git cannot show them -- it writes back the bytes it read, by the same rename, only where the
file still holds what it wrote, reads them back, and exits 4; where the file no longer holds what it wrote, it writes
nothing back and exits 2. It prints {"first": <n>, "last": <n>, "changed": [<n>...]}, the entry's first and last line
and the lines it changed; on exit 3 {"refused": "<why>", "line": <n>|null, "reason": "<word>"|null}, <why> one of
shape, id-absent, id-twice, status-differs, no-page-path, page-path-set, no-walkthrough, walkthrough-set,
no-blocked-by, blocked and changed-while-reading, and line, where it is not null, the line out of shape, the line
refused or, for a key the entry lacks, the entry's first; on exit 4 {"undone": "<why>", "first": <n>, "last": <n>,
"changed": [<n>...]}, <why> hunk-outside or diff-failed.

export writes one commit of a source repository under --out as regular files, and a manifest of them, for /docs-verify's
claim reader, which reads them with Read, Grep and Glob and runs nothing. --repo must be a clone's top level:
<repo>/.git exists -- tested before any git call, since a directory laid out as a git directory can be committed into
any repository, and git run in it would run the commands its config names -- and `git -c safe.bareRepository=explicit -C
<repo> rev-parse --show-toplevel` prints <repo>'s resolved path. Every git call export makes takes that form. It
refuses, exit 3, commit-absent, where `cat-file -e <oid>^{commit}` fails. Before any git call it opens --out's parent
and --manifest's, each a real directory, without following a link, and it makes both relative to those descriptors, so a
parent swapped for a link meanwhile carries nothing elsewhere. It lists `ls-tree -r -z -l --full-tree <oid>`, each
--path a pathspec `:(literal)<p>` where --whole is absent -- a listing git does not give within 30 seconds, as on a very
large tree, is exit 2 -- and leaves out, counting each and printing none: a symbolic link (link); a submodule
(submodule); any other mode but 100644 and 100755 (other); a name not strict UTF-8, holding an empty, . or .. segment, a
segment .git in any case, a control character, U+2028, U+2029 or a bidirectional control, or above 4,096 bytes, or whose
written path under --out reaches the file system's PATH_MAX, so that no reader could open it by its absolute path
(name); and a blob above 1 MiB (large). Where the clone lacks a blob it would write -- a partial clone's, which the
listing sizes BAD -- it refuses, exit 3, blob-absent. Where what remains is above 50,000 files or 512 MiB (536,870,912
bytes) it refuses, exit 3, over-cap. None of these refusals creates anything. Otherwise it makes --out, mode 0700, and
writes each file under it at its repository path: each directory made, mode 0700, and opened relative to its parent's
descriptor without following a link; each file created exclusively, mode 0600, relative to its directory's descriptor,
without following one. A mkdir or a create failing because the name is taken -- two names one under a file system's case
folding -- or a segment is too long for the file system skips that file, or every file under that directory, counted
name; any other failure is exit 2. A path segment named, in any case, .gitignore, .ignore or .rgignore -- which a search
tool would honour, hiding other files -- or .svn, .hg, .bzr, .jj or .sl -- which the Grep tool passes over wherever they
stand -- is written with .exported appended. The contents come raw from one `cat-file --batch`, by object id -- no
filter and no textconv runs -- each header naming a blob of the size the listing gave, else exit 2, or, where it says
the clone lacks the blob, blob-absent, the partial --out left and no manifest written; where it runs past 300 seconds
export refuses, exit 3, timeout, the partial --out left for the caller to remove and no manifest written. It writes
--manifest last, created exclusively without following a link: for each file written, in tree order, its path as written
and its repository path, the first relative to --out and the second to the clone's top level, each followed by a NUL --
the two equal but for a renamed segment. It checks nothing out, fetches nothing, and leaves the clone's index and
working tree alone. It prints {"files": <n>, "bytes": <n>, "skipped": {"link": <n>, "submodule": <n>, "other": <n>,
"name": <n>, "large": <n>}, "paths": {<p>: "exported"|"absent"|"skipped"}}: files and bytes those written; each --path
exported where it, or a path under it, is in the manifest, absent where the listing holds neither, and skipped
otherwise, a --path compared as git reads a pathspec (./, // and /./ collapsed, . the whole tree, a trailing / or /. a
directory alone). On exit 3 it prints {"refused": "<why>", "files": <n>|null, "bytes": <n>|null}, <why> commit-absent,
blob-absent, over-cap or timeout, the counts those of the files it would write, null for commit-absent and blob-absent.

The arguments are tested before anything is read or run: --id against the unit-id class; --walkthrough against the same
class, less every value YAML reads, written plain as edit writes it, as something other than a string -- a null,
boolean, integer, float or date of YAML 1.1 or of YAML 1.2's core schema, such as null, true, y, 017, 0x1f, 1_000, 1.5,
1e3 or 2026-11-18 -- which would not read back as an id, null as no walkthrough at all (the refusal is a little wider,
refusing a few spellings of digits, _ and . that YAML reads as strings, such as 0_8 or 2026-1-5); --base against the
branch class; --status, --from and --block against ^[a-z][a-z-]{0,31}$, less the words YAML reads as something other
than a string (null, true, false, yes, no, on, off, y, n); --page-path against ^[A-Za-z0-9_][A-Za-z0-9._/-]*\.md$ with
no empty, . or .. segment; --repo, a directory, which moved and edit also hold to being a git work tree's top level, and
export to the absolute-path class -- opening with /, and holding no control character, U+2028, U+2029 or bidirectional
control -- and to being a clone's top level, as its paragraph says; --commit against ^[0-9a-f]{40}([0-9a-f]{24})?$;
--out and --manifest against the absolute-path class, each absent by lstat, in a parent that is a real directory by
lstat, and not naming one entry -- one base name in one directory, however spelled; each --path against the
relative-path class -- not empty, opening with neither / nor -, holding no .. segment and none of those characters --
valid UTF-8 and at most 4,096 bytes. --own-moves and --whole take no value; export takes --whole, a --path, or both. A
flag given twice (--id to moved and --path to export aside), or as --flag=value, refuses the run. <top>/.dev-workflows
must be a real directory and the backlog a regular file, both by lstat: a symbolic link to either is refused, never
followed, and the backlog is opened without following a link and never waited on.

What it prints of the backlog, a ref or an argument is line numbers, counts, fixed words, and values that passed a class
test: a unit id in the unit-id class, a branch name in the branch class, the schema version's digits, a --path in the
relative-path class. A value that fails is counted, never printed, not even in an error. Outside --selftest it opens no
file but the backlog and those export makes, and writes nothing but the backlog and, for export, the files under --out
and the file --manifest names; it runs git as an argument list, never a shell, with a 30-second timeout per call --
export's one cat-file --batch, 300 seconds -- in its own environment less every variable whose name starts with GIT_,
plus GIT_TERMINAL_PROMPT=0, GIT_OPTIONAL_LOCKS=0 and GIT_NO_LAZY_FETCH=1. Git's stderr is never printed.

Exit 0: it ran, and the answer is the one JSON object on stdout -- for check, the shape in or out. Exit 2: it could not
run -- an argument outside its class, a usage error, --repo no directory or no work tree's top level, .dev-workflows or
the backlog refused as above or unreadable, git not run or not answering where moved must have an answer (HEAD, the
base, the branch list), the working backlog out of shape or not holding an --id once (moved), a write that failed (the
backlog unchanged), export's own -- --repo no clone's top level, --out or --manifest refused as above, git not listing
the commit or not giving a blob as it listed it, or a write of the export that failed, a partial --out then left -- or
an internal error; stdout is empty and stderr holds one line, "backlog-lines: not run (<why>)", <why> fixed text. Three
exits 2 follow edit's write, each with a <why> of its own: a write -- the edit's or its undo's -- not reading back as
written; an undo not written, since the backlog no longer held the edit's bytes but another writer's; and an undo that
failed on its own write, the backlog then read again and found to hold the edit's bytes exactly -- where that read finds
other bytes, the undo counts as blocked, and where it fails, as a write not reading back. Exit 3: edit refused on the
file's content before writing, the file untouched; or export refused the commit -- commit-absent, blob-absent or
over-cap, nothing created, or timeout or a blob-absent its cat-file --batch met, a partial --out left and no manifest.
Exit 4: edit undone; the file holds the bytes it read. --selftest exits 0 when every case passes and 1 otherwise.

The caller's rule, which fails closed. Any exit but 0, 3 and 4 -- a crash's 1, a signal's -- is read as 2, and so is a
stdout that is not one JSON object. check or moved exiting anything but 0 is a stop, never a skip: never read as in
shape, as no duplicate or as nothing moved. export exiting 3 leaves that commit unread, and exiting anything else but 0
-- a 4 among them -- is a stop; either way a partial --out is the caller's to remove with its scratch. edit exiting 3 or
4 ends the unit, the backlog as it was. edit exiting 2 ends the unit and stops the run, and what the caller then does
with the backlog turns on stderr's one line, matched whole. Only "backlog-lines: not run (the edit was written and its
undo failed on its own write, so the backlog still holds the edit, unchecked; restore the backlog from the copy taken
before the edit)" has the caller restore the backlog from the copy it took before the edit. Every other line -- the
read-back and the blocked undo after a write among them, an exit 2 before any write, and a crash or a stderr it cannot
read -- leaves the backlog as it is, to be compared with that copy: restoring there could overwrite another writer's
change, and leaving it is the side that cannot destroy one.

Python standard library only.
"""

import argparse
import contextlib
import errno
import io
import json
import os
import posixpath
import re
import stat
import subprocess
import sys
import tempfile
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BACKLOG_DIR = ".dev-workflows"
BACKLOG_NAME = "docs-backlog.yml"
BACKLOG_PATH = BACKLOG_DIR + "/" + BACKLOG_NAME
SHAPE_CAP = 8 * 1024 * 1024  # bytes: a larger backlog is out of shape, too-large
REF_CAP = 1024 * 1024  # bytes: a larger backlog on a ref is unreadable
EXAMINE_CAP = 60  # refs examined at most, newest first
READ_REFS_CAP = 20  # refs kept and read at most
GIT_TIMEOUT = 30  # seconds, every git call
EXPORT_FILE_CAP = 1048576  # bytes: a larger blob is not exported, counted large
EXPORT_FILES_CAP = 50000  # files: an export that would write more is refused, over-cap
EXPORT_BYTES_CAP = 536870912  # bytes: an export that would write more is refused, over-cap
EXPORT_TIMEOUT = 300  # seconds: export's one cat-file --batch
EXPORT_NAME_CAP = 4096  # bytes: a longer tree name is not exported, counted name; a longer --path is refused

# Every pattern that tests a whole value is used with fullmatch and is ASCII; digits are [0-9].
UNIT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", re.ASCII)
STATUS_RE = re.compile(r"[a-z][a-z-]{0,31}", re.ASCII)
STATUS_RESERVED = ("null", "true", "false", "yes", "no", "on", "off", "y", "n")  # YAML reads these as no string
# A plain scalar YAML reads as something other than a string, in every form the unit-id class lets through: YAML 1.1's
# null, bool, int, float and date, by its type repository's expressions (PyYAML resolves the same less y, n and the
# spec's wider float), a date's month and day taken at one digit or two as some loaders read one; and YAML 1.2 core's
# null, bool, int and float. edit writes --walkthrough plain, so such a value would not read back as an id: null, the
# one that matters most, as no walkthrough at all. The pattern is a little wider than those forms: it also takes a few
# spellings of digits, _ and . near them that YAML reads as strings, such as 0_8, as the docstring says.
NON_STRING_RE = re.compile(
    r"null|Null|NULL"
    r"|y|Y|yes|Yes|YES|n|N|no|No|NO|true|True|TRUE|false|False|FALSE|on|On|ON|off|Off|OFF"
    r"|0b[01_]+|0o[0-7]+|0x[0-9a-fA-F_]+|[0-9][0-9_]*"
    r"|[0-9][0-9_]*\.[0-9._]*(?:[eE][-+]?[0-9]+)?|[0-9]+(?:\.[0-9]*)?[eE][-+]?[0-9]+"
    r"|[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}", re.ASCII)
PAGE_PATH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/-]*\.md", re.ASCII)
OBJECT_ID_RE = re.compile(r"[0-9a-f]{40}([0-9a-f]{24})?", re.ASCII)
BRANCH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9._/@+-]*", re.ASCII)  # read-only-repos section 3's class
SINGLE_FLAGS = ("--repo", "--base", "--status", "--page-path", "--own-moves", "--from", "--walkthrough",
                "--block", "--commit", "--out", "--manifest", "--whole")  # each taken once: a second refuses the run
# backlog-run.md section 3's X: the characters its relative-path and absolute-path classes, and export's names, refuse.
X_RE = re.compile(r"[\x00-\x1f\x7f-\x9f  ‪-‮⁦-⁩]")

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
WHY_FROM = "--from is outside the status class"
WHY_WALKTHROUGH = ("--walkthrough is outside the unit-id class, or is a spelling YAML reads as no string, "
                   "or one near such a spelling")
WHY_BLOCK = "--block is outside the status class"
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
# After a write, three: only WHY_UNDO tells the caller to restore; the other two leave the backlog as it is.
WHY_UNDO = ("the edit was written and its undo failed on its own write, so the backlog still holds the edit, "
            "unchecked; restore the backlog from the copy taken before the edit")
WHY_RACED = ("a write of the backlog -- the edit's or its undo's -- did not read back as written: another writer's "
             "bytes, or a failed read; leave the backlog as it is and compare it with the copy taken before the edit")
WHY_UNDO_BLOCKED = ("the edit was written, and its undo was not: the backlog no longer held the edit's bytes but "
                    "another writer's, so nothing was written back; leave the backlog as it is and compare it with "
                    "the copy taken before the edit")
WHY_INTERNAL = "internal error"
# export's.
WHY_REPO_ABS = "--repo is outside the absolute-path class"
WHY_COMMIT = "--commit is outside the object-id class"
WHY_OUT = "--out is outside the absolute-path class, already exists, or its parent is not a real directory"
WHY_MANIFEST = ("--manifest is outside the absolute-path class, already exists, its parent is not a real directory, "
                "or it is --out")
WHY_PATH = "--path is outside the relative-path class, is not UTF-8, or is above 4,096 bytes"
WHY_CLONE = "--repo is not a clone's top level: it holds no .git, or git does not name it its top level"
WHY_TREE = "git could not list the commit's tree"
WHY_BLOB = "git did not give a blob of the commit as its listing named it"
WHY_EXPORT_WRITE = "the export could not be written"

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
    DEL, a C1 control (U+0080 to U+009F, U+0085 among them), U+2028, U+2029, U+FFFE or U+FFFF."""
    for ch in line:
        o = ord(ch)
        if ch == "\t":
            raise Out(n, "tab")
        if o < 0x20 or 0x7F <= o <= 0x9F or o in (0x2028, 0x2029, 0xFFFE, 0xFFFF):
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
    Two families of YAML tokenizer read a flow collection -- pure-Python PyYAML's, and libyaml's with YAML 1.2's --
    and they disagree about a `?` and about where a quote opens a quoted scalar, which can hide a bracket. The shape
    admits only what both read alike, and on one line:
    - a plain scalar ends at a ` #`, a `,`, `[`, `]`, `{` or `}`, or a `:` before a space, one of `,[]{}` or the line's
      end; spaces do not end it, and a quote or a `#` inside it is the scalar's;
    - a `?` outside quotes anywhere in the collection is out of shape (key): one family ends a plain scalar there and
      opens a key, the other keeps it in the scalar;
    - a quote outside a plain scalar opens a quoted scalar, which must close on this line, and only directly after
      `[`, `{`, `,` or a `:` a space follows, spaces between; a quote anywhere else -- after a closed quote or bracket,
      a `- `, or a `:` with no space after it -- is out of shape (unclosed-quote), since one family opens a quoted
      scalar there and the other does not;
    - a `#` outside a plain scalar, or after a space, opens a comment, which leaves the collection open
      (unclosed-flow); an anchor, an alias or a tag where a token starts is out of shape.
    """
    stack, i, plain = [], j, False
    while i < len(line):
        c = line[i]
        if c == " ":
            i += 1
            continue
        if c == "#" and (line[i - 1] == " " or not plain):  # a comment: the rest of the line is not the collection's
            break
        if c == "?":  # the two tokenizer families read it differently, inside a plain scalar or out of one
            raise Out(n, "key")
        if plain:
            if not (c in ",[]{}" or (c == ":" and (i + 1 == len(line) or line[i + 1] in " ,[]{}"))):
                i += 1
                continue
            plain = False  # the scalar ends here, and c is read as the token it opens
        if c in "&*!":
            raise Out(n, {"&": "anchor", "*": "alias", "!": "tag"}[c])
        if c in "'\"":
            k = i - 1
            while line[k] == " ":
                k -= 1
            if not (line[k] in "[{," or (line[k] == ":" and k + 1 < i)):  # not where both families open a scalar
                raise Out(n, "unclosed-quote")
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
        if c in ",:" or (c == "-" and (i + 1 == len(line) or line[i + 1] == " ")):  # a token of its own
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


def _read_at(dfd):
    """(bytes, mode) of the backlog in the open .dev-workflows `dfd` -- at most SHAPE_CAP + 1 bytes, which is enough
    to call it too large. It is a regular file by lstat, opened without following a link and never waited on;
    anything else is NotRun."""
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
    return b"".join(chunks), stat.S_IMODE(fst.st_mode)


def _read_backlog(top):
    """(bytes, mode) of <top>'s backlog, as _read_at reads it."""
    dfd = _open_dir(top)
    try:
        got = _read_at(dfd)
    finally:
        os.close(dfd)
    _IO["reads"] += 1
    return got


class _Changed(Exception):
    """The backlog no longer held what a write expected to replace, so nothing was written."""


def _write_backlog(top, data, mode, expect):
    """Replace the backlog with `data` atomically: a new file beside it, written and synced, renamed over it, and the
    rename synced where the platform allows. Nothing is written through a link.

    Immediately before the rename it reads the backlog again, through the same directory descriptor, and where the
    file no longer holds `expect` it removes its new file and raises _Changed, the backlog untouched. That narrows the
    window in which another writer's change is lost to the instant between that read and the rename; it does not
    close it, since no lock is shared with other writers. OSError or NotRun where it cannot write."""
    dfd = _open_dir(top)
    tmpname = None
    try:
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
        if _read_at(dfd)[0] != expect:  # the last look before the rename: the window stays open only from here
            raise _Changed()
        os.replace(tmpname, BACKLOG_NAME, src_dir_fd=dfd, dst_dir_fd=dfd)
        tmpname = None
        _IO["writes"] += 1
        with contextlib.suppress(OSError):
            os.fsync(dfd)
    finally:
        if tmpname is not None:
            with contextlib.suppress(OSError):
                os.unlink(tmpname, dir_fd=dfd)
        with contextlib.suppress(OSError):  # so an OSError always means the rename did not happen
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


def _read_blob(top, entry):
    """The backlog's bytes at a tree entry, read by object id: a regular file's mode, a blob, at most REF_CAP bytes;
    ERROR otherwise."""
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


def _ref_blob(top, base_oid, oid, with_base=False):
    """None where the ref is not kept: merged into the base, no backlog in its tree, or the same backlog as its merge
    base's. ERROR where it is kept and cannot be read. Otherwise the backlog's bytes, at most REF_CAP of them, read by
    object id. With with_base, a kept ref's answer is a pair: that answer, and the backlog's tree entry at the ref's
    merge base with the base -- ABSENT where there is no merge base, or no backlog in its tree."""
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
    mb_oid, mb_entry = _oid(mb), ABSENT
    if mb_oid is not None:  # with no merge base at all the ref is kept: there is nothing to compare it with
        mb_entry = _tree_entry(top, mb_oid)
        if mb_entry is ERROR:
            return ERROR
        if mb_entry == entry:
            return None
    blob = _read_blob(top, entry)
    return (blob, mb_entry) if with_base else blob


def _statuses(blob, ids):
    """{id: status} of each of `ids` an entry of the backlog `blob` holds; None where the backlog is unreadable: ERROR,
    out of shape, holding one of the ids twice, or giving one a status outside the status class."""
    if blob is ERROR:
        return None
    try:
        shape = read_shape(blob)
    except Out:
        return None
    got = {}
    for uid in ids:
        hits = [e for e in shape.entries if e.id == uid]
        if len(hits) > 1 or (hits and not STATUS_RE.fullmatch(hits[0].keys["status"].value.text)):
            return None
        if hits:
            got[uid] = hits[0].keys["status"].value.text
    return got


UNKNOWN = "unknown"


def _base_moves(top, base_oid, own, ids):
    """The ids the base itself moved since HEAD's branch left it: each whose status in the base's backlog differs from
    its working status and from its status at every merge base of HEAD with the base (`git merge-base --all`), no
    backlog or no entry at a merge base being a status that differs. UNKNOWN where that cannot be told: the base's
    backlog unreadable as a kept ref's is; no merge base (an orphan branch, a shallow clone), or git failing or timing
    out on the merge bases; or a merge base's backlog unreadable. An empty set where no id's status there differs from
    the working one, read before any merge base is, or where a merge base's backlog is the base's own blob."""
    entry = _tree_entry(top, base_oid)
    if entry is ERROR:
        return UNKNOWN
    if entry is ABSENT:
        return set()
    tip = _statuses(_read_blob(top, entry), ids)
    if tip is None:
        return UNKNOWN
    differ = [uid for uid in ids if uid in tip and tip[uid] != own[uid]]
    if not differ:
        return set()
    r = _git(top, "merge-base", "--all", "HEAD", base_oid)
    if r is None or r[0] != 0:
        return UNKNOWN
    forks = r[1].decode("ascii", "replace").split()
    if not forks or not all(OBJECT_ID_RE.fullmatch(f) for f in forks):
        return UNKNOWN
    entries = [_tree_entry(top, fork) for fork in forks]
    if entry in entries:  # the base's backlog is a merge base's: it moved nothing since
        return set()
    if ERROR in entries:
        return UNKNOWN
    at_forks = []
    for fork_entry in entries:
        got = {} if fork_entry is ABSENT else _statuses(_read_blob(top, fork_entry), differ)
        if got is None:
            return UNKNOWN
        at_forks.append(got)
    return {uid for uid in differ if all(tip[uid] != at.get(uid) for at in at_forks)}


def cmd_moved(top, base, ids, own_moves=False):
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
    base_oid = base_name = None
    for ref, name in (("refs/remotes/origin/" + base, "origin/" + base), ("refs/heads/" + base, base)):
        base_oid = _oid(_git(top, "rev-parse", "--verify", "--quiet", "--end-of-options", ref + "^{commit}"))
        if base_oid is not None:
            base_name = name
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
    by_base = _base_moves(top, base_oid, own, ids)
    if by_base is UNKNOWN:
        unreadable.append(base_name)
    else:
        for uid in by_base:
            moved[uid] = [base_name]
    base_moved = {uid: list(names) for uid, names in moved.items()}
    base_unreadable = list(unreadable)
    # A local <base> holding commits origin/<base> lacks -- one that is no ancestor of it, read only where the base
    # resolved as origin/<base> and HEAD is not on the local <base> -- is read as the base is, so a move made there and
    # not pushed is seen. A local <base> that is an ancestor of origin/<base> holds nothing origin/<base> lacks.
    if base_name != base and head_ref != "refs/heads/" + base:
        local_oid = _oid(_git(top, "rev-parse", "--verify", "--quiet", "--end-of-options",
                              "refs/heads/" + base + "^{commit}"))
        if local_oid is not None and local_oid != base_oid:
            behind = _git(top, "merge-base", "--is-ancestor", local_oid, base_oid)
            by_local = UNKNOWN if behind is None or behind[0] not in (0, 1) else (
                set() if behind[0] == 0 else _base_moves(top, local_oid, own, ids))
            if by_local is UNKNOWN:
                unreadable.append(base)
                base_unreadable.append(base)
            else:
                for uid in by_local:
                    moved.setdefault(uid, []).append(base)
                    base_moved.setdefault(uid, []).append(base)
    for oid, name in remaining:
        if examined == EXAMINE_CAP or kept == READ_REFS_CAP:
            break
        examined += 1
        got = _ref_blob(top, base_oid, oid, own_moves)
        if got is None:
            continue
        kept += 1
        blob, mb_entry = got if own_moves and got is not ERROR else (got, ABSENT)
        theirs = _statuses(blob, ids)
        # With --own-moves a ref moves a unit only where it changed the unit's status itself: the status at its merge
        # base, read as the ref's own backlog is read, is the other status it must differ from. No backlog there, or
        # no entry for the unit, differs from any status.
        at_base = {}
        if theirs is not None and mb_entry is not ABSENT:
            at_base = _statuses(_read_blob(top, mb_entry), ids)
        if theirs is None or at_base is None:
            unreadable.append(name)
            continue
        for uid, status in theirs.items():
            if status != own[uid] and status != at_base.get(uid):
                moved.setdefault(uid, []).append(name)
    return 0, {"moved": {uid: moved[uid] for uid in ids if uid in moved}, "unreadable": unreadable,
               "base": {"moved": {uid: base_moved[uid] for uid in ids if uid in base_moved},
                        "unreadable": base_unreadable},
               "read": kept, "more": len(remaining) - examined, "names_outside_class": outside}


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
    """A scalar value's text -- page_path's or walkthrough's -- as YAML reads it, where this reader can say; None where
    it cannot."""
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


def _undo_failed(top, new_data):
    """The <why> for an undo whose own write failed. The write can fail before its last look at the backlog, so what
    the backlog holds is read here, and WHY_UNDO -- the one text that has the caller restore from its copy -- is
    returned only where that read finds the edit's bytes exactly: any other bytes are another writer's
    (WHY_UNDO_BLOCKED), and a read that fails is a failed read (WHY_RACED). This is the only place WHY_UNDO is
    chosen."""
    try:
        now = _read_backlog(top)[0]
    except Exception:
        return WHY_RACED
    return WHY_UNDO if now == new_data else WHY_UNDO_BLOCKED


def _refuse(why, line=None, reason=None):
    return 3, {"refused": why, "line": line, "reason": reason}


def _set_unset(entry, key, new, texts, absent, taken):
    """Set `key`'s value to `new` in `texts` where it is unset -- null, ~, or an empty value with no block under it --
    and leave it where it already reads as `new`. The refusal where the entry has no such line (`absent`, at the
    entry's first line) or the line holds anything else (`taken`, at its line); None otherwise."""
    item = entry.keys.get(key)
    if item is None:
        return _refuse(absent, entry.first)
    unset = (item.value.kind == "empty" and not item.had_child) or (
        item.value.kind == "plain" and item.value.text in ("null", "~"))
    if unset:
        texts[item.line - 1] = _replace(texts[item.line - 1], item.value, new)
    elif item.had_child or _scalar_text(item.value) != new:
        return _refuse(taken, item.line)
    return None


def cmd_edit(top, uid, status, page_path, from_status=None, walkthrough=None, block=None):
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
    st = entry.keys["status"]
    if from_status is not None and st.value.text != from_status:  # the move asked for starts from another status
        return _refuse("status-differs", st.line)
    texts = list(shape.texts)
    texts[st.line - 1] = _replace(texts[st.line - 1], st.value, status)
    if page_path is not None:
        refused = _set_unset(entry, "page_path", page_path, texts, "no-page-path", "page-path-set")
        if refused is not None:
            return refused
    if walkthrough is not None:
        refused = _set_unset(entry, "walkthrough", walkthrough, texts, "no-walkthrough", "walkthrough-set")
        if refused is not None:
            return refused
    if block is not None:
        bb = entry.keys.get("blocked_by")
        if bb is None:
            return _refuse("no-blocked-by", entry.first)
        if not ((bb.value.kind == "empty" and not bb.had_child) or (bb.value.kind == "flow" and bb.value.text == "[]")):
            return _refuse("blocked", bb.line)
        texts[bb.line - 1] = _replace(texts[bb.line - 1], bb.value, "[" + block + "]")
    new_data = "\n".join(texts).encode("utf-8")
    changed = [k + 1 for k, (a, b) in enumerate(zip(shape.texts, texts)) if a != b]
    result = {"first": entry.first, "last": entry.last, "changed": changed}
    if not changed:  # the unit already holds these values: nothing is written, and the file keeps its bytes and mtime
        return 0, result
    # What it is about to write must read back as the edit, in shape, the entry where it was, each key asked for
    # holding what was asked.
    try:
        after = read_shape(new_data)
    except Out:
        raise NotRun(WHY_INTERNAL)
    back = [e for e in after.entries if e.id == uid]
    keys = back[0].keys if len(back) == 1 else {}
    if (len(back) != 1 or (back[0].first, back[0].last) != (entry.first, entry.last)
            or keys["status"].value.text != status
            or (page_path is not None and _scalar_text(keys["page_path"].value) != page_path)
            or (walkthrough is not None and _scalar_text(keys["walkthrough"].value) != walkthrough)
            or (block is not None and (keys["blocked_by"].value.kind, keys["blocked_by"].value.text)
                != ("flow", "[" + block + "]"))
            or not all(entry.first <= k <= entry.last for k in changed)):
        raise NotRun(WHY_INTERNAL)
    try:
        _write_backlog(top, new_data, mode, data)
    except _Changed:
        return _refuse("changed-while-reading")
    except OSError:
        raise NotRun(WHY_WRITE)
    # What landed must be what it wrote, byte for byte, before git is asked about it. Where it is not, another writer
    # replaced it after the rename, and writing back the bytes this run read would lose that writer's change too.
    try:
        landed = _read_backlog(top)[0]
    except Exception:
        landed = None
    if landed != new_data:
        raise NotRun(WHY_RACED)
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
    # The undo writes back only over the edit's own bytes. Which of three things went wrong decides what the caller
    # may do: only an undo that failed on its own write, over a backlog read again and found to hold the edit, leaves
    # the edit in place for the caller's copy to replace.
    try:
        _write_backlog(top, data, mode, new_data)
    except (_Changed, NotRun):  # the backlog no longer held the edit's bytes: another writer's change stands
        raise NotRun(WHY_UNDO_BLOCKED)
    except OSError:  # the undo's own write failed, perhaps before its last look: what the backlog holds is read now
        raise NotRun(_undo_failed(top, new_data))
    try:
        landed = _read_backlog(top)[0]
    except Exception:
        landed = None
    if landed != data:  # the undo landed and another writer replaced it, or it cannot be read back
        raise NotRun(WHY_RACED)
    return 4, dict({"undone": why}, **result)


# ---- export ----

XGIT = ("git", "-c", "safe.bareRepository=explicit", "-C")  # every git call export makes in a source repository
# A search tool reads the first three as rules that hide other files, and the Grep tool passes over the other five
# wherever they stand: a segment of any of these names, in any case, is written with RENAMED_SUFFIX appended.
RENAMED = (b".gitignore", b".ignore", b".rgignore", b".svn", b".hg", b".bzr", b".jj", b".sl")
RENAMED_SUFFIX = b".exported"
SKIP_ERRNOS = (errno.EEXIST, errno.ENAMETOOLONG)  # a name taken under case folding, or a segment too long: skipped
_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_DIR_FLAGS = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | _NOFOLLOW


def _xgit(repo, *args):
    """_git for a source repository: `git -c safe.bareRepository=explicit -C <repo> <args>`, the same environment,
    timeout and discarded stderr."""
    _IO["git"] += 1
    try:
        r = subprocess.run([*XGIT, repo, *args], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, env=_git_env(), timeout=GIT_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.returncode, r.stdout


def _abs_path(s):
    """backlog-run.md section 3's absolute-path class: --repo, --out and --manifest."""
    return s.startswith("/") and X_RE.search(s) is None


def _rel_path(s):
    """backlog-run.md section 3's relative-path class, valid UTF-8 and at most EXPORT_NAME_CAP bytes: --path."""
    try:
        size = len(s.encode("utf-8"))
    except UnicodeEncodeError:
        return False
    return (s != "" and s[0] not in "/-" and ".." not in s.split("/") and X_RE.search(s) is None
            and size <= EXPORT_NAME_CAP)


def _open_parent(path, why):
    """(a descriptor of `path`'s parent, a real directory opened without following a link, and `path`'s base name as
    bytes), where that base name -- neither empty, . nor .. -- names nothing there by lstat; NotRun(why) otherwise.
    export makes --out and --manifest relative to these descriptors, so a parent swapped for a link after the test
    carries nothing elsewhere."""
    head, base = os.path.split(os.fsencode(path))
    if base in (b"", b".", b".."):
        raise NotRun(why)
    try:
        fd = os.open(head, _DIR_FLAGS)
    except OSError:
        raise NotRun(why)
    try:
        os.stat(base, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return fd, base
    except OSError:
        pass
    os.close(fd)
    raise NotRun(why)


def _fresh(path, why):
    """NotRun(why) unless `path` is absent by lstat and its parent is a real directory by lstat: _open_parent's test,
    its descriptor closed."""
    os.close(_open_parent(path, why)[0])


def _same_place(a, b):
    """Whether the paths `a` and `b`, each in a real directory, name one entry: one base name, in one directory."""
    (ha, ba), (hb, bb) = os.path.split(os.fsencode(a)), os.path.split(os.fsencode(b))
    return ba == bb and os.path.samefile(ha, hb)


def _name_in_class(raw):
    """A tree name export writes: strict UTF-8, at most EXPORT_NAME_CAP bytes, no empty, . or .. segment, no segment
    .git in any case, and no character X_RE names."""
    if len(raw) > EXPORT_NAME_CAP:
        return False
    try:
        name = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return X_RE.search(name) is None and all(s not in ("", ".", "..") and s.lower() != ".git"
                                             for s in name.split("/"))


def _written_segment(seg):
    """The segment as export writes it: one of RENAMED, in any case, with RENAMED_SUFFIX appended."""
    return seg + RENAMED_SUFFIX if seg.lower() in RENAMED else seg


def _make_dir(name, dfd):
    """mkdir `name`, mode 0700, in the open directory `dfd`: export's one mkdir, which --selftest wraps."""
    os.mkdir(name, 0o700, dir_fd=dfd)


def _create_file(name, dfd):
    """A descriptor of the new file `name` in the open directory `dfd`: created exclusively, mode 0600, through no
    link. export's one create, which --selftest wraps."""
    return os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW, 0o600, dir_fd=dfd)


def _dir_at(root, want, made, failed):
    """A descriptor of the directory `want`, a tuple of repository segments, under the open directory `root`, each
    level by its written segment: made here where this export has not made it yet, and opened relative to its
    parent's descriptor without following a link. None where a level's mkdir fails EEXIST or ENAMETOOLONG -- that
    level is then in `failed` -- and NotRun on any other failure. A level is keyed by its repository segments, so two
    that write one name -- a renamed segment beside a committed one already ending .exported -- never share a
    directory: the second mkdir fails EEXIST."""
    fd = None
    try:
        fd = os.dup(root)
        for i, seg in enumerate(want):
            key, name = want[:i + 1], _written_segment(seg)
            if key not in made:
                try:
                    _make_dir(name, fd)
                except OSError as e:
                    if e.errno not in SKIP_ERRNOS:
                        raise
                    failed.add(key)
                    return None
                made.add(key)
            child = os.open(name, _DIR_FLAGS, dir_fd=fd)
            os.close(fd)
            fd = child
        got, fd = fd, None
        return got
    except OSError:
        raise NotRun(WHY_EXPORT_WRITE)
    finally:
        if fd is not None:
            os.close(fd)


class _Stream(Exception):
    """cat-file --batch did not answer as asked: killed at the timeout, or a header or a body not as listed."""


class _Missing(Exception):
    """cat-file --batch answered that the clone lacks the object."""


def _blob(proc, oid, size, fd):
    """Copy the blob `oid` from the running cat-file --batch into `fd`: the header naming it, a blob of `size` bytes,
    then its bytes and a line feed. _Missing where the header says the clone lacks it; _Stream where the stream does
    not answer so; NotRun where `fd` cannot be written."""
    try:
        proc.stdin.write(oid + b"\n")
        proc.stdin.flush()
        header = proc.stdout.readline(256)
    except (OSError, ValueError):
        raise _Stream()
    if header == oid + b" missing\n":
        raise _Missing()
    if header != b"%s blob %d\n" % (oid, size):
        raise _Stream()
    left = size
    while left:
        try:
            chunk = proc.stdout.read(min(left, 1 << 20))
        except (OSError, ValueError):
            raise _Stream()
        if not chunk:
            raise _Stream()
        view = memoryview(chunk)
        try:
            while view:
                view = view[os.write(fd, view):]
        except OSError:
            raise NotRun(WHY_EXPORT_WRITE)
        left -= len(chunk)
    try:
        if proc.stdout.read(1) != b"\n":
            raise _Stream()
    except (OSError, ValueError):
        raise _Stream()


def _export_files(repo, keep, out_dir, out_base, skipped):
    """Make --out, `out_base` in the open directory `out_dir`, mode 0700, and write under it each of `keep` --
    (repository path, object id, size), in tree order -- by its written path, its contents from one cat-file --batch.
    ("done", the (written path, repository path, size) of each file written, in tree order); or ("timeout", None)
    where EXPORT_TIMEOUT passed first, or ("blob-absent", None) where cat-file says the clone lacks a blob, --out then
    left as it stands. A mkdir or a create failing EEXIST or ENAMETOOLONG skips the file, counted name in `skipped`;
    any other failure is NotRun."""
    try:
        _make_dir(out_base, out_dir)
        root = os.open(out_base, _DIR_FLAGS, dir_fd=out_dir)
    except OSError:
        raise NotRun(WHY_EXPORT_WRITE)
    _IO["writes"] += 1
    done, made, failed, dirs, dfd, proc, timer, expired = [], set(), set(), None, None, None, None, []
    finished = False
    deadline = time.monotonic() + EXPORT_TIMEOUT
    try:
        try:
            os.fchmod(root, 0o700)
        except OSError:
            raise NotRun(WHY_EXPORT_WRITE)
        if keep:
            _IO["git"] += 1
            try:
                proc = subprocess.Popen([*XGIT, repo, "cat-file", "--batch"], stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, env=_git_env())
            except (OSError, subprocess.SubprocessError):
                raise NotRun(WHY_NO_GIT)

            def expire():
                expired.append(True)
                with contextlib.suppress(OSError):
                    proc.kill()
            timer = threading.Timer(max(deadline - time.monotonic(), 0), expire)
            timer.daemon = True
            timer.start()
        for name, oid, size in keep:
            if expired or time.monotonic() >= deadline:
                return "timeout", None
            segs = name.split(b"/")
            base = _written_segment(segs[-1])
            want = tuple(segs[:-1])
            if any(want[:i] in failed for i in range(1, len(want) + 1)):
                skipped["name"] += 1
                continue
            if want != dirs:
                if dfd is not None:
                    os.close(dfd)
                    dfd = None
                dirs = None
                dfd = _dir_at(root, want, made, failed)
                if dfd is None:
                    skipped["name"] += 1
                    continue
                dirs = want
            try:
                fd = _create_file(base, dfd)
            except OSError as e:
                if e.errno not in SKIP_ERRNOS:
                    raise NotRun(WHY_EXPORT_WRITE)
                skipped["name"] += 1
                continue
            try:
                _blob(proc, oid, size, fd)
            except _Missing:
                return "blob-absent", None
            except _Stream:
                if expired or time.monotonic() >= deadline:
                    return "timeout", None
                raise NotRun(WHY_BLOB)
            finally:
                os.close(fd)
            done.append((b"/".join([_written_segment(s) for s in segs]), name, size))
            _IO["writes"] += 1
        finished = True
        return "done", done
    finally:
        if timer is not None:
            timer.cancel()
        if proc is not None:
            with contextlib.suppress(OSError, ValueError):
                proc.stdin.close()
            if not finished:  # a timeout or a failure: git may be blocked writing a blob nobody will read
                with contextlib.suppress(OSError):
                    proc.kill()
            try:
                proc.wait(timeout=GIT_TIMEOUT)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            with contextlib.suppress(OSError, ValueError):
                proc.stdout.close()
        for fd in (dfd, root):
            if fd is not None:
                with contextlib.suppress(OSError):
                    os.close(fd)


def _path_states(paths, listed, written):
    """{<p>: exported | absent | skipped} for each --path: exported where it, or a path under it, is a repository
    path `written` holds; absent where the listing holds neither; skipped otherwise. A path is compared as git reads
    a pathspec -- ./, // and /./ collapsed, . the whole tree, and a trailing / or /. naming a directory alone."""
    states = {}
    for p in paths:
        raw = p.encode("utf-8")
        norm, dir_only = posixpath.normpath(raw), raw.endswith((b"/", b"/."))

        def under(name):
            return norm == b"." or (name == norm and not dir_only) or name.startswith(norm + b"/")
        states[p] = ("exported" if any(under(n) for n in written) else
                     "absent" if not any(under(n) for n in listed) else "skipped")
    return states


def _path_max(dfd):
    """The longest path, in bytes and counting its terminating NUL, the file system under the open directory `dfd`
    lets a reader open; 4096 where it names no limit."""
    try:
        got = os.fpathconf(dfd, "PC_PATH_MAX")
    except (OSError, ValueError):
        got = None
    return got if got is not None and got > 0 else 4096


def cmd_export(repo, commit, out, manifest, whole, paths):
    out_dir = man_dir = None
    try:
        out_dir, out_base = _open_parent(out, WHY_OUT)
        man_dir, man_base = _open_parent(manifest, WHY_MANIFEST)
        return _export_commit(repo, commit, os.fsencode(out), out_dir, out_base, man_dir, man_base, whole, paths)
    finally:
        for fd in (out_dir, man_dir):
            if fd is not None:
                with contextlib.suppress(OSError):
                    os.close(fd)


def _export_commit(repo, commit, out, out_dir, out_base, man_dir, man_base, whole, paths):
    if not os.path.lexists(os.path.join(repo, ".git")):  # before any git call: see the docstring
        raise NotRun(WHY_CLONE)
    r = _xgit(repo, "rev-parse", "--show-toplevel")
    if r is None:
        raise NotRun(WHY_NO_GIT)
    top = r[1].rstrip(b"\n")
    if r[0] != 0 or not top or os.path.realpath(os.fsdecode(top)) != os.path.realpath(repo):
        raise NotRun(WHY_CLONE)
    r = _xgit(repo, "cat-file", "-e", commit + "^{commit}")
    if r is None:
        raise NotRun(WHY_NO_GIT)
    if r[0] != 0:
        return 3, {"refused": "commit-absent", "files": None, "bytes": None}
    specs = [] if whole else ["--"] + [":(literal)" + p for p in paths]
    r = _xgit(repo, "ls-tree", "-r", "-z", "-l", "--full-tree", commit, *specs)
    if r is None or r[0] != 0:
        raise NotRun(WHY_TREE)
    path_max = _path_max(out_dir)
    listed, keep, absent = [], [], False
    skipped = {"link": 0, "submodule": 0, "other": 0, "name": 0, "large": 0}
    for record in r[1].split(b"\0"):
        if not record:
            continue
        head, tab, name = record.partition(b"\t")
        fields = head.split()
        if not tab or not name or len(fields) != 4:
            raise NotRun(WHY_TREE)
        mode, kind, oid, size = fields
        listed.append(name)
        if mode == b"120000":
            skipped["link"] += 1
        elif mode == b"160000":
            skipped["submodule"] += 1
        elif mode not in FILE_MODES or kind != b"blob":
            skipped["other"] += 1
        elif not _name_in_class(name):
            skipped["name"] += 1
        elif len(out) + 1 + len(b"/".join(_written_segment(s) for s in name.split(b"/"))) >= path_max:
            skipped["name"] += 1  # written, it could not be opened by its absolute path
        elif not OBJECT_ID_RE.fullmatch(oid.decode("ascii", "replace")):
            raise NotRun(WHY_TREE)
        elif size == b"BAD":  # git could not read the blob's size: a partial clone that lacks it
            absent = True
        elif not size.isdigit():
            raise NotRun(WHY_TREE)
        elif int(size) > EXPORT_FILE_CAP:
            skipped["large"] += 1
        else:
            keep.append((name, oid, int(size)))
    if absent:
        return 3, {"refused": "blob-absent", "files": None, "bytes": None}
    total = sum(size for _, _, size in keep)
    if len(keep) > EXPORT_FILES_CAP or total > EXPORT_BYTES_CAP:
        return 3, {"refused": "over-cap", "files": len(keep), "bytes": total}
    how, done = _export_files(repo, keep, out_dir, out_base, skipped)
    if how == "timeout":
        return 3, {"refused": "timeout", "files": len(keep), "bytes": total}
    if how == "blob-absent":
        return 3, {"refused": "blob-absent", "files": None, "bytes": None}
    try:  # last, so a manifest exists only beside a whole export
        fd = os.open(man_base, os.O_WRONLY | os.O_CREAT | os.O_EXCL | _NOFOLLOW, 0o600, dir_fd=man_dir)
    except OSError:
        raise NotRun(WHY_EXPORT_WRITE)
    try:
        view = memoryview(b"".join(written + b"\0" + name + b"\0" for written, name, _ in done))
        while view:
            view = view[os.write(fd, view):]
    except OSError:
        raise NotRun(WHY_EXPORT_WRITE)
    finally:
        os.close(fd)
    _IO["writes"] += 1
    return 0, {"files": len(done), "bytes": sum(size for _, _, size in done), "skipped": skipped,
               "paths": _path_states(paths, listed, [name for _, name, _ in done])}


# ---- the command line ----

class _Parser(argparse.ArgumentParser):
    """argparse, whose refusal is the one fixed usage line: its own message can echo an argument."""

    def error(self, message):
        raise NotRun(WHY_USAGE)


def _unit_id(s):
    return UNIT_ID_RE.fullmatch(s) is not None


def _status(s):
    """The status class, less the words YAML reads as something other than a string: --status, --from and --block."""
    return STATUS_RE.fullmatch(s) is not None and s not in STATUS_RESERVED


def _walkthrough(s):
    """The unit-id class, less every value YAML reads, written plain, as something other than a string, and a few
    spellings of digits, _ and . that YAML reads as strings: --walkthrough."""
    return _unit_id(s) and NON_STRING_RE.fullmatch(s) is None


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
    mp.add_argument("--own-moves", action="store_true")
    ep = sub.add_parser("edit", add_help=False, allow_abbrev=False)
    ep.add_argument("--repo")
    ep.add_argument("--id", action="append")
    ep.add_argument("--status")
    ep.add_argument("--page-path")
    ep.add_argument("--from", dest="from_status")
    ep.add_argument("--walkthrough")
    ep.add_argument("--block")
    xp = sub.add_parser("export", add_help=False, allow_abbrev=False)
    xp.add_argument("--repo")
    xp.add_argument("--commit")
    xp.add_argument("--out")
    xp.add_argument("--manifest")
    xp.add_argument("--whole", action="store_true")
    xp.add_argument("--path", action="append")
    a = ap.parse_args(argv)
    if a.verb not in ("check", "moved", "edit", "export") or not a.repo:
        raise NotRun(WHY_USAGE)
    if a.verb == "check":
        checks = []
    elif a.verb == "moved":
        if a.base is None or not a.id:
            raise NotRun(WHY_USAGE)
        checks = [(all(_unit_id(i) for i in a.id), WHY_ID), (BRANCH_RE.fullmatch(a.base) is not None, WHY_BASE)]
    elif a.verb == "edit":
        if a.status is None or not a.id or len(a.id) != 1:
            raise NotRun(WHY_USAGE)
        checks = [(_unit_id(a.id[0]), WHY_ID),
                  (_status(a.status), WHY_STATUS),
                  (a.page_path is None or _page_path(a.page_path), WHY_PAGE_PATH),
                  (a.from_status is None or _status(a.from_status), WHY_FROM),
                  (a.walkthrough is None or _walkthrough(a.walkthrough), WHY_WALKTHROUGH),
                  (a.block is None or _status(a.block), WHY_BLOCK)]
    else:
        if a.commit is None or a.out is None or a.manifest is None or not (a.whole or a.path):
            raise NotRun(WHY_USAGE)
        checks = [(_abs_path(a.repo), WHY_REPO_ABS),
                  (OBJECT_ID_RE.fullmatch(a.commit) is not None, WHY_COMMIT),
                  (_abs_path(a.out), WHY_OUT),
                  (_abs_path(a.manifest), WHY_MANIFEST),
                  (all(_rel_path(p) for p in a.path or ()), WHY_PATH)]
    for ok, why in checks:
        if not ok:
            raise NotRun(why)
    if not os.path.isdir(a.repo):
        raise NotRun(WHY_REPO)
    if a.verb == "check":
        return cmd_check, (a.repo,)
    if a.verb == "moved":
        return cmd_moved, (a.repo, a.base, list(dict.fromkeys(a.id)), a.own_moves)
    if a.verb == "edit":
        return cmd_edit, (a.repo, a.id[0], a.status, a.page_path, a.from_status, a.walkthrough, a.block)
    _fresh(a.out, WHY_OUT)
    _fresh(a.manifest, WHY_MANIFEST)
    if _same_place(a.out, a.manifest):
        raise NotRun(WHY_MANIFEST)
    return cmd_export, (a.repo, a.commit, a.out, a.manifest, a.whole, list(dict.fromkeys(a.path or ())))


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
FH_PATH = os.path.join(HERE, os.pardir, "references", "finish-and-handoff.md")
VIS_PATH = os.path.join(HERE, os.pardir, "references", "docs-workflow", "visibility.md")
DW_PATH = os.path.join(HERE, os.pardir, "commands", "docs-write.md")
DV_PATH = os.path.join(HERE, os.pardir, "commands", "docs-verify.md")
BR_PATH = os.path.join(HERE, os.pardir, "references", "docs-iteration", "backlog-run.md")
BF_LEAD = "**The line shape a backlog run reads.**"
# backlog-run.md's two marker programs, section 10.1's read and section 10.2's test, find the page-level marker in
# evidence-contract section 3 by this phrase; /docs-write runs them at its Phase 0 and Phase 9, and /docs-verify at
# its Phase 0 and its Phases 1 and 4. docs-verify.md's own marker program, which removes the marker, finds it by the
# same phrase.
EC_MARKER_PHRASE = "this page-level marker, character for character: "
# An internal page's first line after its frontmatter, which backlog-run.md's section 10.2 program, and docs-verify.md's
# marker program and frontmatter program, match as page text.
VISIBILITY_MARKER = "<!-- docs-visibility: internal -->"
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
WALK8 = "    walkthrough: null\n"
MINI_W = MINI.replace("    page_path: null\n", "    page_path: null\n" + WALK8)  # the entry is lines 3 to 9


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


def _fx(cwd, *args, date=None):
    """A fixture's git command, its stdout; HOME is the case's empty directory, so no user configuration is read. A
    `date` (seconds since the epoch) fixes the author and committer dates, for a fixture whose shape turns on them."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})
    if date is not None:
        env.update({"GIT_AUTHOR_DATE": "@%d +0000" % date, "GIT_COMMITTER_DATE": "@%d +0000" % date})
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


def _moved(top, *ids, base="main", own_moves=False):
    argv = ["moved", "--repo", top, "--base", base]
    for i in ids:
        argv += ["--id", i]
    if own_moves:
        argv.append("--own-moves")
    return _call(argv)


def _moved_ok(top, *ids, base="main", own_moves=False, bases=None):
    """moved's object less its `base` member, which is checked here: against `bases`, given as {"moved": ...,
    "unreadable": ...}, or, where none is given, against the entries of `moved` and `unreadable` named <base> or
    origin/<base> -- right only where no ref is printed under a base's name, which a case that makes one says."""
    code, out, err = _moved(top, *ids, base=base, own_moves=own_moves)
    _eq((code, err), (0, ""), "moved's exit and stderr")
    obj = _obj(out)
    _true("base" in obj, "moved prints a base member")
    got = obj.pop("base")
    if bases is None:
        names = (base, "origin/" + base)
        bases = {"moved": {uid: [n for n in refs if n in names] for uid, refs in obj["moved"].items()
                           if any(n in names for n in refs)},
                 "unreadable": [n for n in obj["unreadable"] if n in names]}
    _eq(got, bases, "moved's base member")
    return obj


def _edit(top, uid, status, page_path=None, frm=None, walkthrough=None, block=None):
    argv = ["edit", "--repo", top, "--id", uid, "--status", status]
    for flag, value in (("--page-path", page_path), ("--from", frm), ("--walkthrough", walkthrough),
                        ("--block", block)):
        if value is not None:
            argv += [flag, value]
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
    # In a flow collection a quote opens a quoted scalar only directly after [, {, , or `: `, where both tokenizer
    # families open one; anywhere else outside a plain scalar one family opens a scalar there and the other does not,
    # so the quote is out of shape, closed or not. Inside a plain scalar a quote is the scalar's.
    for name, line in (("after-quote", "    roles: [\"a\"' b]\n"), ("after-closed-quote", "    roles: [\"a\" 'b']\n"),
                       ("after-colon", "    roles: [a, :'b]\n"), ("after-colon-closed", "    roles: [a, :'b']\n"),
                       ("after-dash", "    roles: [- 'b]\n"),
                       ("after-bracket", "    roles: [[a]'b']\n")):
        _out(tmp, MINI.replace("    roles: [customer]\n", line), 5, "unclosed-quote", name)
    for name, line in (("in-plain", "    roles: [it's, a 'b c, x:'y]\n"),
                       ("token-starts", "    roles: [ 'a', \"b\" , ['c'], {d: 'e', f:  \"g\"}]\n")):
        _eq(_shape(tmp, MINI.replace("    roles: [customer]\n", line), name), _ok(), name)


def case_flow_question_out(tmp):
    """A `?` outside quotes in a flow collection is out of shape. libyaml keeps it inside a plain scalar and pure-Python
    PyYAML opens a key there, so a quote after it hides a bracket from one family and not from the other: here libyaml
    reads lines 6 to 9 as one string inside U-001's roles, while a reader taking the quote as a scalar would see a
    second entry, U-002, and edit its status outside any entry a YAML reader knows."""
    data = ("schema_version: 1\n"
            "units:\n"
            "  - id: U-001\n"
            "    status: missing\n"
            "    page_path: null\n"
            "    roles: [a?', [' ]\n"
            "  - id: U-002\n"
            "    status: missing\n"
            "    page_path: null\n"
            "    title: ', ]] # '\n"
            "threshold: 2\n")
    _out(tmp, data, 6, "key", "check")
    top = _repo(tmp, data, "edit")
    code, out, err = _edit(top, "U-002", "drafted", "docs/x.md")
    _eq((code, err), (3, ""), "edit on U-002")
    _eq(_obj(out), {"refused": "shape", "line": 6, "reason": "key"}, "edit on U-002")
    _eq(_get(top), data.encode("utf-8"), "untouched")
    code, out, err = _moved(top, "U-002")
    _refused(code, out, err, WHY_WORKING_SHAPE)
    for name, line in (("mapping", "    roles: {a?', {': 1 }\n"), ("first", "    roles: [?'[']\n"),
                       ("in-plain", "    roles: [what?]\n"), ("after-space", "    roles: [a ?b]\n")):
        _out(tmp, MINI.replace("    roles: [customer]\n", line), 5, "key", name)
    _eq(_shape(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: what? 'yes'\n"), "block"), _ok(),
        "a ? outside a flow collection")


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
    for name, ch in (("cr", "\r"), ("vt", "\x0b"), ("del", "\x7f"), ("c1-first", "\x80"), ("nel", "\x85"),
                     ("c1-last", "\x9f"), ("ls", "\u2028"), ("ps", "\u2029"), ("fffe", "\ufffe"), ("ffff", "\uffff")):
        _out(tmp, MINI.replace(title, "    title: a%sb\n" % ch), 4, "control", name)
    _out(tmp, MINI + "# the end\r", 10, "control", "cr-at-eof")
    _eq(_shape(tmp, MINI.replace(title, "    title: \"caf\u00e9 \u00a0 \ufffd\"\n"), "printable"), _ok(),
        "printable non-ASCII")


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
    _out(tmp, MINI.replace(STATUS6, "    \u00a0status: missing\n"), 6, "indent", "after")
    _out(tmp, MINI.replace(STATUS6, "\u00a0\u00a0\u00a0\u00a0status: missing\n"), 6, "indent", "instead")


def case_trailing_text_out(tmp):
    _out(tmp, MINI.replace("    title: \"Place an order\"\n", "    title: \"a\" b\n"), 4, "trailing", "quote")
    _out(tmp, MINI.replace("    roles: [customer]\n", "    roles: [a] b\n"), 5, "trailing", "flow")


def case_status_missing_out(tmp):
    _out(tmp, MINI.replace(STATUS6, ""), 3, "status")


def case_status_flow_out(tmp):
    _out(tmp, MINI.replace(STATUS6, "    status: [missing]\n"), 6, "status")


def case_document_start_line_one_only(tmp):
    """BF section 1's `---` as line 1 only: in shape on line 1, a CRLF ending included; out of shape on a later line,
    or with anything after it on line 1 -- so each side of the reader's line-1 test turns a case red."""
    _eq(_shape(tmp, "---\n" + MINI, "first"), _ok(), "line 1")
    _eq(_shape(tmp, "---\r\n" + MINI, "first-crlf"), _ok(), "line 1, CRLF")
    _out(tmp, "schema_version: 1\n---\n" + MINI.split("\n", 1)[1], 2, "continuation", "second")
    _out(tmp, MINI + "---\n", 10, "continuation", "last")
    _out(tmp, "--- x\n" + MINI, 1, "continuation", "first-trailing")


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
    _fx(top, "switch", "-q", "-c", "ahead", "main")  # a local <base> ahead of origin/<base> is read as the base is
    _fx(top, "switch", "-q", "main")
    _put(top, DRAFTED)
    _fx(top, "commit", "-qam", "unpushed move on main")
    _fx(top, "switch", "-q", "ahead")
    _eq(_moved_ok(top, "U-001")["moved"], {"U-001": ["main", "feat/a"]}, "a local base ahead of its remote")
    _fx(top, "switch", "-q", "main")
    _fx(top, "reset", "-q", "--hard", "origin/main")
    _fx(top, "switch", "-q", "-c", "work")
    _fx(top, "switch", "-q", "main")
    _fx(top, "merge", "-q", "--no-ff", "-m", "merge feat/a", "feat/a")
    _fx(top, "push", "-q", "origin", "main")
    _fx(top, "switch", "-q", "work")
    # work was cut before the merge, so origin/main moved U-001 after work left it: the base names it.
    _eq(_moved_ok(top, "U-001"), {"moved": {"U-001": ["origin/main"]}, "unreadable": [], "read": 0, "more": 0,
                                  "names_outside_class": 0}, "merged into origin/main")


def case_ref_name_outside_class(tmp):
    top = _repo(tmp, MINI)
    _branch_with(top, "x$(id)", DRAFTED)
    code, out, err = _moved(top, "U-001")
    _eq((code, err), (0, ""))
    _eq(_obj(out), {"moved": {}, "unreadable": [], "base": {"moved": {}, "unreadable": []}, "read": 0, "more": 0,
                    "names_outside_class": 1})
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


def _with(name, wrapper, thunk):
    """thunk() with this module's global `name` replaced by `wrapper`; the original comes back however it ends."""
    real = globals()[name]
    globals()[name] = wrapper
    try:
        return thunk()
    finally:
        globals()[name] = real


def case_edit_changed_while_reading(tmp):
    """Another writer changes the backlog after the edit read it: the last look before the rename sees it, so the
    edit is refused, exit 3, the other writer's bytes stand and no new file is left beside them."""
    top = _repo(tmp, MINI)
    theirs = MINI.replace("threshold: 2\n", "threshold: 3\n").encode("utf-8")
    calls = []
    real = _read_backlog

    def racing(path):
        got = real(path)
        if not calls:
            _put(top, theirs)
        calls.append(path)
        return got
    code, out, err = _with("_read_backlog", racing, lambda: _edit(top, "U-001", "drafted"))
    _eq((code, err), (3, ""))
    _eq(_obj(out), {"refused": "changed-while-reading", "line": None, "reason": None})
    _eq(_get(top), theirs, "the other writer's change stands")
    _eq(sorted(os.listdir(os.path.join(top, BACKLOG_DIR))), [BACKLOG_NAME], "no new file left")


def case_edit_changed_after_write(tmp):
    """Another writer replaces the backlog after the edit's rename: the read-back finds bytes it did not write, so the
    edit stops, exit 2, and writes nothing back, which would lose that writer's change too."""
    top = _repo(tmp, MINI)
    theirs = MINI.replace("threshold: 2\n", "threshold: 3\n").encode("utf-8")
    calls = []
    real = _read_backlog

    def racing(path):
        if len(calls) == 1:  # the read-back after the write
            _put(top, theirs)
        calls.append(path)
        return real(path)
    code, out, err = _with("_read_backlog", racing, lambda: _edit(top, "U-001", "drafted"))
    _refused(code, out, err, WHY_RACED)
    _eq(_get(top), theirs, "not undone over the other writer")


def case_edit_undo_blocked(tmp):
    """The diff calls for an undo, but another writer changed the backlog after the edit's read-back: the undo's last
    look sees bytes the edit did not write, so nothing is written back, exit 2 with the blocked undo's own text -- leave
    the backlog, compare it -- and that writer's bytes stand. Where the undo lands and another writer then replaces it,
    the undo's read-back says so, exit 2 with the read-back's text, and those bytes stand too."""
    dirty = MINI.replace("schema_version: 1\n", "schema_version: 1  # touched\n")
    theirs = MINI.replace("threshold: 2\n", "threshold: 3\n").encode("utf-8")
    top = _repo(tmp, MINI, "blocked")
    _put(top, dirty)
    real_git = _git

    def racing_git(path, *args):
        got = real_git(path, *args)
        if args[:1] == ("diff",):
            _put(top, theirs)
        return got
    code, out, err = _with("_git", racing_git, lambda: _edit(top, "U-001", "drafted"))
    _refused(code, out, err, WHY_UNDO_BLOCKED)
    _eq(_get(top), theirs, "the other writer's bytes, as that writer left them")
    top = _repo(tmp, MINI, "landed")
    _put(top, dirty)
    real_read, calls = _read_backlog, []

    def racing_read(path):
        if len(calls) == 2:  # the undo's read-back: its rename has landed, and another writer replaces it now
            _put(top, theirs)
        calls.append(path)
        return real_read(path)
    code, out, err = _with("_read_backlog", racing_read, lambda: _edit(top, "U-001", "drafted"))
    _refused(code, out, err, WHY_RACED)
    _eq(_get(top), theirs, "the other writer's bytes, as that writer left them")


def _undo_write_fails(before=None):
    """A stand-in for _write_backlog whose second call -- the undo's -- runs the real function with no entropy for its
    new file's name, so it raises OSError before its last look at the backlog; `before` runs first, as another actor."""
    real, calls = _write_backlog, []

    def failing(*args):
        calls.append(args)
        if len(calls) != 2:
            return real(*args)
        if before is not None:
            before()

        def no_entropy(k):
            raise OSError("no space left on device")
        saved = os.urandom
        os.urandom = no_entropy
        try:
            return real(*args)
        finally:
            os.urandom = saved
    return failing


def case_edit_undo_failed(tmp):
    """The diff calls for an undo and the undo's own write fails before its last look, over a backlog that, read
    again, holds the edit: exit 2 with WHY_UNDO, the one text that has the caller restore from its copy. The
    docstring's caller rule quotes that line whole, finish-and-handoff's section 6.4 quotes it byte for byte (a caller
    matches the line whole against that copy), no other text after a write says to restore, and the one function
    that names WHY_UNDO is the one that reads the backlog first."""
    dirty = MINI.replace("schema_version: 1\n", "schema_version: 1  # touched\n")
    top = _repo(tmp, MINI)
    _put(top, dirty)
    code, out, err = _with("_write_backlog", _undo_write_fails(), lambda: _edit(top, "U-001", "drafted"))
    _refused(code, out, err, WHY_UNDO)
    _eq(_get(top), dirty.replace("status: missing", "status: drafted").encode("utf-8"), "the edit, still in place")
    doc = " ".join(__doc__.split())
    _true(" ".join(("backlog-lines: not run (%s)" % WHY_UNDO).split()) in doc, "the caller rule quotes WHY_UNDO whole")
    with open(FH_PATH, encoding="utf-8") as fh:
        _true(("`backlog-lines: not run (%s)`" % WHY_UNDO) in fh.read(),
              "finish-and-handoff section 6.4 quotes WHY_UNDO's line byte for byte")
    _true("restore" in WHY_UNDO and "restore" not in WHY_RACED and "restore" not in WHY_UNDO_BLOCKED,
          "only WHY_UNDO says to restore")
    import ast
    with open(os.path.abspath(__file__), encoding="utf-8") as fh:
        src = fh.read()
    code = src[:src.index("# ==== selftest ====")]
    tree = ast.parse(code)
    users = sorted({f.name for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)
                    for node in ast.walk(f) if isinstance(node, ast.Name) and node.id == "WHY_UNDO"})
    _eq(users, ["_undo_failed"], "the functions that name WHY_UNDO")
    # The whole module, not only its functions: a module-level alias of WHY_UNDO is a use outside _undo_failed.
    inside = {id(n) for f in ast.walk(tree) if isinstance(f, ast.FunctionDef) and f.name == "_undo_failed"
              for n in ast.walk(f)}
    outside = [type(n.ctx).__name__ for n in ast.walk(tree)
               if isinstance(n, ast.Name) and n.id == "WHY_UNDO" and id(n) not in inside]
    _eq(outside, ["Store"], "outside _undo_failed, WHY_UNDO is only assigned, once")
    _true("'WHY_UNDO'" not in code and '"WHY_UNDO"' not in code, "no code names WHY_UNDO by string")


def case_marker_phrase_pinned(tmp):
    """The backlog runs read the page-level marker out of evidence-contract section 3 by one phrase, in
    backlog-run.md's two programs -- section 10.1's read and section 10.2's test, which /docs-write runs at its Phase 0
    and at its Phase 9, and /docs-verify at its Phase 0 and its Phases 1 and 4 -- and in docs-verify.md's one program
    of its own, the marker program that removes it at its Phase 6 and tests for it at its Phase 10. The phrase stands
    in that section directly before the marker, once, and in each of the three programs, so a reword of either side
    turns the build red, not a run after its review; docs-write.md holds no program of its own that searches by it."""
    with open(os.path.join(HERE, os.pardir, "references", "docs-audit", "evidence-contract.md"), encoding="utf-8") as fh:
        ec = fh.read()
    sec = ec[ec.index("\n## 3. "):ec.index("\n## 4. ")]
    _eq(sec.count(EC_MARKER_PHRASE + "`[NEEDS CLARIFICATION: "), 1,
        "evidence-contract section 3 gives the marker directly after the phrase, once")
    _eq(ec.count(EC_MARKER_PHRASE), 1, "the phrase stands nowhere else in evidence-contract")
    with open(BR_PATH, encoding="utf-8") as fh:
        br = fh.read()
    _eq(br.count('r"' + EC_MARKER_PHRASE + '`(\\[NEEDS CLARIFICATION: [^`]*\\])`"'), 2,
        "backlog-run's section 10.1 and 10.2 programs search by the phrase, byte for byte")
    _eq(br.count("character for character: `("), 2, "no program of backlog-run searches by another phrase")
    with open(DW_PATH, encoding="utf-8") as fh:
        dw = fh.read()
    _eq(dw.count("character for character: `("), 0, "docs-write holds no program of its own that searches by it")
    with open(DV_PATH, encoding="utf-8") as fh:
        dv = fh.read()
    _eq(dv.count('r"' + EC_MARKER_PHRASE + '`(\\[NEEDS CLARIFICATION: [^`]*\\])`"'), 1,
        "docs-verify's marker program searches by the phrase, byte for byte")
    _eq(dv.count("character for character: `("), 1, "docs-verify holds that one program searching by it, and no other")


def case_edit_undo_failed_over_another_writer(tmp):
    """The review's reproduction: another writer replaces the backlog after the edit's read-back, and the undo's own
    write fails before its last look. The read that follows finds that writer's bytes, so the exit 2 is the blocked
    undo's -- leave the backlog -- never WHY_UNDO's restore, and those bytes stand."""
    dirty = MINI.replace("schema_version: 1\n", "schema_version: 1  # touched\n")
    theirs = MINI.replace("threshold: 2\n", "threshold: 3\n").encode("utf-8")
    top = _repo(tmp, MINI)
    _put(top, dirty)
    real_git = _git

    def racing_git(path, *args):
        got = real_git(path, *args)
        if args[:1] == ("diff",):
            _put(top, theirs)
        return got
    code, out, err = _with("_git", racing_git, lambda: _with(
        "_write_backlog", _undo_write_fails(), lambda: _edit(top, "U-001", "drafted")))
    _refused(code, out, err, WHY_UNDO_BLOCKED)
    _eq(_get(top), theirs, "the other writer's bytes, as that writer left them")


def case_edit_undo_failed_unreadable(tmp):
    """The undo's own write fails and the backlog cannot then be read -- another actor has put a symbolic link in its
    place -- so the exit 2 is the failed read's, WHY_RACED: leave the backlog and compare, never restore."""
    dirty = MINI.replace("schema_version: 1\n", "schema_version: 1  # touched\n")
    top = _repo(tmp, MINI)
    _put(top, dirty)
    elsewhere = os.path.join(tmp, "elsewhere.yml")
    path = os.path.join(top, BACKLOG_DIR, BACKLOG_NAME)

    def swap_in_a_link():
        with open(elsewhere, "wb") as fh:
            fh.write(MINI.encode("utf-8"))
        os.remove(path)
        os.symlink(elsewhere, path)
    code, out, err = _with("_write_backlog", _undo_write_fails(swap_in_a_link), lambda: _edit(top, "U-001", "drafted"))
    _refused(code, out, err, WHY_RACED)
    _true(os.path.islink(path), "the link is left where it is")
    with open(elsewhere, "rb") as fh:
        _eq(fh.read(), MINI.encode("utf-8"), "the link's target, untouched")


def case_edit_noop(tmp):
    """The unit already holds the values asked for: exit 0, changed empty, nothing written -- the same bytes, inode
    and mtime."""
    data = DRAFTED.replace("page_path: null", "page_path: docs/a.md")
    top = _repo(tmp, data)
    path = os.path.join(top, BACKLOG_DIR, BACKLOG_NAME)
    before = os.stat(path)
    for page_path in (None, "docs/a.md"):
        code, out, err = _edit(top, "U-001", "drafted", page_path)
        _eq((code, err), (0, ""), "no-op %r" % page_path)
        _eq(_obj(out), {"first": 3, "last": 8, "changed": []}, "no-op %r" % page_path)
        _eq(_IO["writes"], 0, "nothing written")
    after = os.stat(path)
    _eq((after.st_ino, after.st_mtime_ns), (before.st_ino, before.st_mtime_ns), "inode and mtime")
    _eq(_get(top), data.encode("utf-8"), "bytes")


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


# ---- moved --own-moves ----

def _units(*pairs):
    """A backlog in shape holding one entry per (id, status), in order."""
    return ("schema_version: 1\nunits:\n"
            + "".join("  - id: %s\n    status: %s\n    page_path: null\n    blocked_by: []\n" % p for p in pairs)
            + "threshold: 2\n")


def _open_draft_repo(tmp, name="top"):
    """C1's repository. main holds U-001 drafted, U-002 missing, U-003 drafted. docs/w-u-002 was cut while U-001 was
    still missing on main and moved U-002 to drafted; docs/v-u-003 was cut after and moved U-003 to verified."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing"), ("U-003", "drafted")), name)
    _branch_with(top, "docs/w-u-002", _units(("U-001", "missing"), ("U-002", "drafted"), ("U-003", "drafted")))
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing"), ("U-003", "drafted")))
    _fx(top, "commit", "-qam", "U-001 drafted on main")
    _branch_with(top, "docs/v-u-003", _units(("U-001", "drafted"), ("U-002", "missing"), ("U-003", "verified")))
    return top


def _moved_json(moved, unreadable=(), read=0, outside=0):
    return {"moved": moved, "unreadable": list(unreadable), "read": read, "more": 0, "names_outside_class": outside}


def case_own_moves_open_draft_branch(tmp):
    """C1: an open draft branch cut before U-001 was drafted on main still holds it as missing. Without --own-moves
    that branch moves U-001; with the flag a ref moves a unit only where it changed the unit's status itself."""
    top = _open_draft_repo(tmp)
    _eq(_moved_ok(top, "U-001", "U-003"),
        _moved_json({"U-001": ["docs/w-u-002"], "U-003": ["docs/v-u-003"]}, read=2), "without the flag")
    _eq(_moved_ok(top, "U-001", "U-003", own_moves=True), _moved_json({"U-003": ["docs/v-u-003"]}, read=2),
        "with it")
    _eq(_moved_ok(top, "U-002", own_moves=True), _moved_json({"U-002": ["docs/w-u-002"]}, read=2),
        "the open branch's own move still counts")


def case_own_moves_real_move(tmp):
    """A branch that moved U-001 itself is moved, flag or not -- where its merge base held the unit at the base's
    status, where the merge base had no backlog, and where its backlog had no entry for the unit."""
    for name, at_base in (("real", DRAFTED), ("no-backlog", None), ("no-entry", DRAFTED.replace("U-001", "U-009"))):
        top = os.path.join(tmp, name)
        os.makedirs(top)
        _fx(top, "init", "-q", "-b", "main")
        if at_base is None:
            with open(os.path.join(top, "README"), "w", encoding="utf-8") as fh:
                fh.write("no backlog yet\n")
        else:
            _put(top, at_base)
        _fx(top, "add", "-A")
        _fx(top, "commit", "-qm", "the merge base")
        _branch_with(top, "docs/v-u-001", DRAFTED.replace("status: drafted", "status: verified"))
        _put(top, DRAFTED)
        with open(os.path.join(top, "NEXT"), "w", encoding="utf-8") as fh:
            fh.write("main moves on\n")
        _fx(top, "add", "-A")
        _fx(top, "commit", "-qm", "main moves on")
        want = _moved_json({"U-001": ["docs/v-u-001"]}, read=1)
        _eq(_moved_ok(top, "U-001"), want, name + " without the flag")
        _eq(_moved_ok(top, "U-001", own_moves=True), want, name + " with it")


def case_own_moves_no_merge_base(tmp):
    """An orphan branch shares no merge base with the base: it is compared as without the flag, and moved."""
    top = _repo(tmp, MINI)
    _fx(top, "switch", "-q", "--orphan", "orphan")
    _put(top, DRAFTED)
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "an unrelated history")
    _fx(top, "switch", "-q", "main")
    want = _moved_json({"U-001": ["orphan"]}, read=1)
    _eq(_moved_ok(top, "U-001"), want, "without the flag")
    _eq(_moved_ok(top, "U-001", own_moves=True), want, "with it")


def case_own_moves_merge_base_unreadable(tmp):
    """With --own-moves the merge base's backlog is read by object id within the ref's own limits. Out of shape (the
    flow tokenizer's `?` rule), over 1 MiB, a symbolic link, holding the id twice, or giving it a status outside the
    class, it makes the ref unreadable, and read counts it. Without the flag that merge base is never read, and the
    same ref is moved."""
    big = MINI + ("# " + "x" * 1021 + "\n") * 1127
    _true(REF_CAP < len(big.encode("utf-8")) < 2 * REF_CAP, "the fixture is about 1.1 MiB")
    for name, at_base in (("shape", MINI.replace("    roles: [customer]\n", "    roles: [a?', [' ]\n")),
                          ("big", big),
                          ("linked", None),
                          ("twice",
                           MINI.replace("threshold: 2\n", "  - id: U-001\n    status: missing\nthreshold: 2\n")),
                          ("odd-status", MINI.replace("status: missing", "status: Missing!"))):
        top = os.path.join(tmp, name)
        path = os.path.join(top, BACKLOG_PATH)
        os.makedirs(os.path.join(top, BACKLOG_DIR))
        _fx(top, "init", "-q", "-b", "main")
        if at_base is None:  # a committed link, whose blob is its target's text, never a file
            os.symlink(MINI, path)
        else:
            _put(top, at_base)
        _fx(top, "add", "-A")
        _fx(top, "commit", "-qm", "the merge base")
        _fx(top, "switch", "-q", "-c", "docs/w-u-001")
        os.remove(path)
        _put(top, DRAFTED)
        _fx(top, "add", "-A")
        _fx(top, "commit", "-qm", "U-001 drafted on a branch")
        _fx(top, "switch", "-q", "main")
        os.remove(path)
        _put(top, MINI)
        _fx(top, "add", "-A")
        _fx(top, "commit", "-qm", "main moves on")
        _eq(_moved_ok(top, "U-001", own_moves=True), _moved_json({}, unreadable=["docs/w-u-001"], read=1),
            name + " with the flag")
        _eq(_moved_ok(top, "U-001"), _moved_json({"U-001": ["docs/w-u-001"]}, read=1), name + " without it")


def case_own_moves_unchanged_without_flag(tmp):
    """Without --own-moves, moved prints what it printed before the flag existed, byte for byte, with the `base` member
    B48 added: every key, a moved unit, an unreadable ref and a name outside the class, pinned to a literal."""
    top = _open_draft_repo(tmp)
    _branch_with(top, "bad-shape", DRAFTED.replace("    roles: [customer]\n", "    roles: |\n"))
    _branch_with(top, "x$(id)", DRAFTED)
    code, out, err = _moved(top, "U-001", "U-003")
    _eq((code, err), (0, ""), "exit and stderr")
    _eq(out, '{\n'
             '  "moved": {\n'
             '    "U-001": [\n'
             '      "docs/w-u-002"\n'
             '    ],\n'
             '    "U-003": [\n'
             '      "docs/v-u-003"\n'
             '    ]\n'
             '  },\n'
             '  "unreadable": [\n'
             '    "bad-shape"\n'
             '  ],\n'
             '  "base": {\n'
             '    "moved": {},\n'
             '    "unreadable": []\n'
             '  },\n'
             '  "read": 3,\n'
             '  "more": 0,\n'
             '  "names_outside_class": 1\n'
             '}\n', "stdout, byte for byte")


def _note(top, text, date=None):
    """A commit on the branch HEAD is on that changes a file other than the backlog."""
    with open(os.path.join(top, "NOTES"), "a", encoding="utf-8") as fh:
        fh.write(text + "\n")
    _fx(top, "add", "-A", date=date)
    _fx(top, "commit", "-qm", text, date=date)


def case_base_merge_commit(tmp):
    """M1: `stale` is cut, then docs/w-u-001 drafts U-001 and main merges it by a merge commit, so that branch is merged
    and examined no more. Standing on stale, the base moved U-001 after stale left it: the base names it."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "branch", "stale")
    _branch_with(top, "docs/w-u-001", _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "merge", "-q", "--no-ff", "-m", "merge docs/w-u-001", "docs/w-u-001")
    _fx(top, "switch", "-q", "stale")
    _eq(_moved_ok(top, "U-001", "U-002"), _moved_json({"U-001": ["main"]}), "flag or not")
    _eq(_moved_ok(top, "U-001", "U-002", own_moves=True), _moved_json({"U-001": ["main"]}), "with --own-moves")


def case_base_squash_branch_deleted(tmp):
    """M3: as M1, merged by a squash and the drafting branch deleted, so no other ref holds the move: the base names
    U-001, the one ref that does."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "branch", "stale")
    _branch_with(top, "docs/w-u-001", _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "merge", "-q", "--squash", "docs/w-u-001")
    _fx(top, "commit", "-qm", "squash docs/w-u-001")
    _fx(top, "branch", "-q", "-D", "docs/w-u-001")
    _fx(top, "switch", "-q", "stale")
    _eq(_moved_ok(top, "U-001", "U-002"), _moved_json({"U-001": ["main"]}))


def case_base_own_draft_not_moved(tmp):
    """M7: the branch HEAD is on drafted U-001 itself, unmerged; the base's status differs from the working one but is
    its status at the merge base, so the base moved nothing: a command verifying that branch's own draft takes it."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "switch", "-q", "-c", "docs/docs-write-u-001")
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "commit", "-qam", "docs: draft U-001")
    _eq(_moved_ok(top, "U-001", own_moves=True), _moved_json({}), "with --own-moves")
    _eq(_moved_ok(top, "U-001"), _moved_json({}), "without it")


def case_base_reset_on_branch_not_moved(tmp):
    """M8: main holds U-001 drafted; a branch cut from it moves U-001 back to missing by hand, to redraft it. The base
    has not moved U-001 since the branch left it, so it names nothing."""
    top = _repo(tmp, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "switch", "-q", "-c", "redo-u-001")
    _put(top, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "commit", "-qam", "U-001 back to missing, to redraft")
    _eq(_moved_ok(top, "U-001", "U-002"), _moved_json({}))


def case_base_criss_cross_every_merge_base(tmp):
    """R5b: main and w merge each other crosswise, so they share two merge bases -- M1, where main drafted U-001, and
    W1, a commit of w's dated after it, which `git merge-base` alone picks. w then resets U-001 to missing. The base
    holds U-001 at M1's status, so it has not moved it since w took M1: read at every merge base, it names nothing."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")))
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "add", "-A", date=1700000100)
    _fx(top, "commit", "-qm", "M1: U-001 drafted on main", date=1700000100)
    m1 = _fx(top, "rev-parse", "HEAD").strip()
    _fx(top, "switch", "-q", "-c", "w", "HEAD~1")
    _note(top, "W1, dated after M1", date=1700000200)
    w1 = _fx(top, "rev-parse", "HEAD").strip()
    _fx(top, "switch", "-q", "main")
    _fx(top, "merge", "-q", "--no-ff", "-m", "M2: merge W1", w1, date=1700000300)
    _fx(top, "switch", "-q", "w")
    _fx(top, "merge", "-q", "--no-ff", "-m", "W2: merge M1", m1, date=1700000400)
    _put(top, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "add", "-A", date=1700000500)
    _fx(top, "commit", "-qm", "W3: U-001 reset to missing, to redraft", date=1700000500)
    _eq(sorted(_fx(top, "merge-base", "--all", "HEAD", "main").split()), sorted([m1, w1]), "two merge bases")
    _eq(_fx(top, "merge-base", "HEAD", "main").strip(), w1, "the one `git merge-base` alone picks")
    _eq(_moved_ok(top, "U-001"), _moved_json({}))


def case_base_shallow_unknown(tmp):
    """R6: a depth-1 clone holds no merge base of its branches with origin/main. Where the base's status differs from
    the working one, whether the base moved the unit cannot be told: the base is unreadable and names nothing -- for
    the branch's own draft (U-002), and for a unit origin/main did draft (U-001) alike."""
    seed = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")), "seed")
    _fx(seed, "branch", "redo")
    _put(seed, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(seed, "commit", "-qam", "U-001 drafted on main")
    _fx(seed, "switch", "-q", "redo")
    _put(seed, _units(("U-001", "missing"), ("U-002", "drafted")))
    _fx(seed, "commit", "-qam", "redo drafts U-002")
    _fx(seed, "switch", "-q", "main")
    _note(seed, "main moves on")
    top = os.path.join(tmp, "top")
    _fx(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--depth", "1", "--no-single-branch",
        "file://" + seed, top)
    _fx(top, "switch", "-q", "redo")
    for ids, own in ((("U-002",), True), (("U-001",), False)):
        res = _moved_ok(top, *ids, own_moves=own)
        _eq((res["moved"], res["unreadable"]), ({}, ["origin/main"]), "%s" % (ids,))


def case_base_orphan_unknown(tmp):
    """R7: an orphan branch shares no history with the base, so no merge base tells whether the base moved a unit
    whose statuses differ: the base is unreadable and names nothing."""
    top = _repo(tmp, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "switch", "-q", "--orphan", "w")
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "w's own backlog")
    _eq(_moved_ok(top, "U-001", own_moves=True), _moved_json({}, unreadable=["main"]))


def case_base_fork_backlog_unreadable(tmp):
    """R10: the merge base's backlog holds U-001 twice, so its status there cannot be read: the base is unreadable and
    names nothing, never falling back to comparing the base with the working backlog alone."""
    top = _repo(tmp, _units(("U-001", "drafted"), ("U-002", "missing")))
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing")).replace(
        "threshold: 2\n", "  - id: U-001\n    status: drafted\nthreshold: 2\n"))
    _fx(top, "commit", "-qam", "U-001 twice at the fork")
    _fx(top, "switch", "-q", "-c", "w")
    _put(top, _units(("U-001", "missing"), ("U-002", "missing")))
    _fx(top, "commit", "-qam", "w repairs the backlog, U-001 missing")
    _fx(top, "switch", "-q", "main")
    _put(top, _units(("U-001", "drafted"), ("U-002", "missing")))
    _fx(top, "commit", "-qam", "main repairs it, U-001 drafted")
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001"), _moved_json({}, unreadable=["main"]))


THREE = (("U-001", "missing"), ("U-002", "missing"), ("U-003", "missing"))


def _cloned(tmp, data):
    """A clone at <tmp>/top of a bare origin whose one commit holds the backlog `data`, and a second clone at
    <tmp>/other, which moves origin/main without touching top's local main."""
    seed = _repo(tmp, data, "seed")
    up = os.path.join(tmp, "up.git")
    _fx(tmp, "clone", "-q", "--bare", seed, up)
    top, other = os.path.join(tmp, "top"), os.path.join(tmp, "other")
    _fx(tmp, "clone", "-q", up, top)
    _fx(tmp, "clone", "-q", up, other)
    return top, other


def _commit_units(top, message, *pairs):
    """A commit on the branch HEAD is on that sets the backlog to one entry per (id, status)."""
    _put(top, _units(*pairs))
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", message)


def case_local_base_unpushed_move(tmp):
    """L1: w is cut, then the local main drafts U-001 and is not pushed, so origin/main lacks the move. origin/main
    moved nothing since w left it; the local main moved U-001: it is named, after the base, by its local name."""
    top, _ = _cloned(tmp, _units(*THREE))
    _fx(top, "branch", "w")
    _commit_units(top, "U-001 drafted on the local main, unpushed", ("U-001", "drafted"), *THREE[1:])
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({"U-001": ["main"]}))
    _eq(_moved_ok(top, "U-001", own_moves=True), _moved_json({"U-001": ["main"]}), "--own-moves reads it alike")


def case_local_base_diverged(tmp):
    """L3: the local main drafts U-002, unpushed; origin/main drafts U-001 after w was cut. Each names the move it
    holds, origin/main first."""
    top, other = _cloned(tmp, _units(*THREE))
    _fx(top, "branch", "w")
    _commit_units(top, "U-002 drafted on the local main", THREE[0], ("U-002", "drafted"), THREE[2])
    _commit_units(other, "U-001 drafted on origin", ("U-001", "drafted"), *THREE[1:])
    _fx(other, "push", "-q", "origin", "main")
    _fx(top, "fetch", "-q", "origin")
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({"U-001": ["origin/main"], "U-002": ["main"]}))


def case_local_base_behind_not_read(tmp):
    """L2c: w is cut; the local main takes origin/main's draft of U-001, and origin/main then resets U-001 to missing
    by hand. A local main that is an ancestor of origin/main holds no move origin/main lacks, so it is not read --
    read, it would name U-001, which origin/main holds as missing."""
    top, other = _cloned(tmp, _units(*THREE))
    _fx(top, "branch", "w")
    _commit_units(other, "U-001 drafted on origin", ("U-001", "drafted"), *THREE[1:])
    _fx(other, "push", "-q", "origin", "main")
    _fx(top, "pull", "-q", "--ff-only", "origin", "main")
    _commit_units(other, "U-001 reset to missing by hand", *THREE)
    _fx(other, "push", "-q", "origin", "main")
    _fx(top, "fetch", "-q", "origin")
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({}))


def case_local_base_holds_working_branch(tmp):
    """L5: w drafts U-003 and the local main merges w, unpushed. The move is w's own, at its merge base with the local
    main, so nothing is named. Then the local main drafts U-001 too: that move, made after it took w, is named."""
    top, _ = _cloned(tmp, _units(*THREE))
    _fx(top, "switch", "-q", "-c", "w")
    _commit_units(top, "w drafts U-003", THREE[0], THREE[1], ("U-003", "drafted"))
    _fx(top, "switch", "-q", "main")
    _fx(top, "merge", "-q", "--no-ff", "-m", "merge w on the local main", "w")
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({}), "w's own draft")
    _fx(top, "switch", "-q", "main")
    _commit_units(top, "U-001 drafted on the local main", ("U-001", "drafted"), THREE[1], ("U-003", "drafted"))
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({"U-001": ["main"]}), "a move made after it took w")


def case_local_base_same_draft_on_origin(tmp):
    """L9: the local main and origin/main each merge the branch that drafts U-001, and origin/main then resets U-001 to
    missing by hand; w is cut from origin/main after. w's merge base with the local main holds the draft, so the local
    main has not moved U-001 since w left it."""
    top, other = _cloned(tmp, _units(*THREE))
    _fx(top, "switch", "-q", "-c", "docs/w-u-001")
    _commit_units(top, "draft U-001", ("U-001", "drafted"), *THREE[1:])
    _fx(top, "push", "-q", "origin", "docs/w-u-001")
    _fx(top, "switch", "-q", "main")
    _fx(top, "merge", "-q", "--no-ff", "-m", "merge docs/w-u-001 on the local main", "docs/w-u-001")
    _fx(other, "fetch", "-q", "origin")
    _fx(other, "merge", "-q", "--no-ff", "-m", "merge docs/w-u-001 on origin", "origin/docs/w-u-001")
    _commit_units(other, "U-001 reset to missing by hand", *THREE)
    _fx(other, "push", "-q", "origin", "main")
    _fx(other, "push", "-q", "origin", "--delete", "docs/w-u-001")
    _fx(top, "fetch", "-q", "--prune", "origin")
    _fx(top, "branch", "-q", "-D", "docs/w-u-001")
    _fx(top, "switch", "-q", "-c", "w", "origin/main")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({}))


def case_local_base_head_on_it(tmp):
    """L6: HEAD on the local main, ahead of origin/main by a draft of U-001. The working backlog is the local main's,
    so it names nothing, and origin/main has moved nothing."""
    top, _ = _cloned(tmp, _units(*THREE))
    _commit_units(top, "U-001 drafted on the local main", ("U-001", "drafted"), *THREE[1:])
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({}))


def case_local_base_shallow_unknown(tmp):
    """L10: a depth-1 clone whose local main is ahead of origin/main by a draft of U-001. No merge base tells whether
    the local main moved it since w left it: the local main is unreadable and names nothing."""
    seed = _repo(tmp, _units(*THREE), "seed")
    _fx(seed, "branch", "w")
    _note(seed, "main moves on")
    top = os.path.join(tmp, "top")
    _fx(tmp, "-c", "protocol.file.allow=always", "clone", "-q", "--depth", "1", "--no-single-branch",
        "file://" + seed, top)
    _commit_units(top, "U-001 drafted on the local main", ("U-001", "drafted"), *THREE[1:])
    _fx(top, "switch", "-q", "w")
    _eq(_moved_ok(top, "U-001", "U-002", "U-003"), _moved_json({}, unreadable=["main"], read=1))


def case_ref_named_as_a_base(tmp):
    """F1: with no origin the base is the local main, and a local branch named origin/main -- which git prints as
    origin/main, no remote-tracking ref shadowing it -- drafts U-001. It is a ref, not a base: moved names it, and its
    base member names no base, so a caller never takes it for the base by its printed name."""
    top = _repo(tmp, _units(*THREE))
    _fx(top, "switch", "-q", "-c", "origin/main")
    _commit_units(top, "a branch named origin/main drafts U-001", ("U-001", "drafted"), *THREE[1:])
    _fx(top, "switch", "-q", "-c", "w", "main")
    _eq(_moved_ok(top, "U-001", bases={"moved": {}, "unreadable": []}),
        _moved_json({"U-001": ["origin/main"]}, read=1))


def case_own_moves_bad_args(tmp):
    """--own-moves is a bare flag of moved: given twice, with a value, or to another verb, exit 2, nothing read."""
    top = _repo(tmp, MINI)
    moved = ["moved", "--repo", top, "--base", "main", "--id", "U-001"]
    for argv in (moved + ["--own-moves", "--own-moves"], moved + ["--own-moves=yes"], moved + ["--own-moves", "yes"],
                 ["edit", "--repo", top, "--id", "U-001", "--status", "drafted", "--own-moves"],
                 ["check", "--repo", top, "--own-moves"]):
        code, out, err = _call(argv)
        _refused(code, out, err, WHY_USAGE)
        _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "%r: nothing read, run or written" % (argv[3:],))


# ---- edit --from, --walkthrough, --block ----

def _stat(top):
    st = os.stat(os.path.join(top, BACKLOG_PATH))
    return st.st_ino, st.st_mtime_ns


def _edit_refused(top, data, want, *args, **flags):
    """edit exits 3 with `want`, writing nothing: the bytes, the inode and the mtime as they were."""
    before = _stat(top)
    code, out, err = _edit(top, *args, **flags)
    _eq((code, err), (3, ""), "exit and stderr")
    _eq(_obj(out), want)
    _eq(_IO["writes"], 0, "nothing written")
    _eq(_get(top), data.encode("utf-8"), "untouched")
    _eq(_stat(top), before, "inode and mtime")


def case_edit_from_refused(tmp):
    """--from names a status the entry does not hold: exit 3, status-differs, its status line -- tested after the id
    and before anything else, a missing page_path line included."""
    top = _repo(tmp, MINI)
    _edit_refused(top, MINI, {"refused": "status-differs", "line": 6, "reason": None}, "U-001", "verified",
                  frm="drafted")
    _edit_refused(top, MINI, {"refused": "id-absent", "line": None, "reason": None}, "U-404", "verified",
                  frm="drafted")
    data = MINI.replace("    page_path: null\n", "")
    top = _repo(tmp, data, "no-page-path")
    _edit_refused(top, data, {"refused": "status-differs", "line": 6, "reason": None}, "U-001", "verified",
                  "docs/a.md", frm="drafted")


def case_edit_from_ok(tmp):
    """--from names the entry's status: the edit goes on, as without it -- and with --walkthrough, the verify move."""
    top = _repo(tmp, DRAFTED)
    code, out, err = _edit(top, "U-001", "verified", frm="drafted")
    _eq((code, err), (0, ""))
    _eq(_obj(out), {"first": 3, "last": 8, "changed": [6]})
    _eq(_get(top), DRAFTED.replace("status: drafted", "status: verified").encode("utf-8"))
    data = MINI_W.replace("status: missing", "status: drafted")
    top = _repo(tmp, data, "verify")
    code, out, err = _edit(top, "U-001", "verified", frm="drafted", walkthrough="U-001")
    _eq((code, err), (0, ""), "the verify move")
    _eq(_obj(out), {"first": 3, "last": 9, "changed": [6, 8]}, "the verify move")
    _eq(_get(top), data.replace("status: drafted", "status: verified").replace(WALK8, "    walkthrough: U-001\n")
        .encode("utf-8"), "the verify move")


def case_edit_walkthrough_unset(tmp):
    """An unset walkthrough line -- null, ~, or an empty value, with a comment or without -- takes the id; every other
    byte is kept, a CRLF ending and the comment included."""
    for name, line, want in (("null", WALK8, "    walkthrough: U-001\n"),
                             ("tilde", "    walkthrough: ~\n", "    walkthrough: U-001\n"),
                             ("empty", "    walkthrough:\n", "    walkthrough: U-001\n"),
                             ("commented", "    walkthrough:   # none yet\n", "    walkthrough: U-001   # none yet\n")):
        for eol in ("\n", "\r\n"):
            label = name + ("-crlf" if eol == "\r\n" else "")
            data = MINI_W.replace(WALK8, line).replace("\n", eol)
            top = _repo(tmp, data, label)
            code, out, err = _edit(top, "U-001", "missing", walkthrough="U-001")
            _eq((code, err), (0, ""), label)
            _eq(_obj(out), {"first": 3, "last": 9, "changed": [8]}, label)
            _eq(_get(top), MINI_W.replace(WALK8, want).replace("\n", eol).encode("utf-8"), label)


def case_edit_walkthrough_other(tmp):
    """A walkthrough line naming another id, or holding a block, is set: exit 3, walkthrough-set, its line."""
    for name, lines in (("other", "    walkthrough: W-9\n"), ("quoted", "    walkthrough: 'W-9'\n"),
                        ("child", "    walkthrough:\n      id: U-001\n")):
        data = MINI_W.replace(WALK8, lines)
        top = _repo(tmp, data, name)
        _edit_refused(top, data, {"refused": "walkthrough-set", "line": 8, "reason": None}, "U-001", "drafted",
                      walkthrough="U-001")


def case_edit_walkthrough_same(tmp):
    """A walkthrough line already reading as the id is left as it is, quoted or plain."""
    data = MINI_W.replace(WALK8, "    walkthrough: \"U-001\"\n")
    top = _repo(tmp, data)
    code, out, err = _edit(top, "U-001", "drafted", walkthrough="U-001")
    _eq((code, err), (0, ""))
    _eq(_obj(out), {"first": 3, "last": 9, "changed": [6]})
    _eq(_get(top), data.replace("status: missing", "status: drafted").encode("utf-8"), "the line unchanged")
    data = MINI_W.replace(WALK8, "    walkthrough: U-001\n")
    top = _repo(tmp, data, "plain")
    before = _stat(top)
    code, out, err = _edit(top, "U-001", "missing", walkthrough="U-001")
    _eq((code, out and _obj(out), err), (0, {"first": 3, "last": 9, "changed": []}, ""), "plain, nothing to change")
    _eq((_get(top), _stat(top)), (data.encode("utf-8"), before), "plain, nothing written")


def case_edit_no_walkthrough_key(tmp):
    top = _repo(tmp, MINI)
    _edit_refused(top, MINI, {"refused": "no-walkthrough", "line": 3, "reason": None}, "U-001", "drafted",
                  walkthrough="U-001")


def case_edit_block_sets(tmp):
    """An empty blocked_by -- [] or an empty value, with a comment or without -- takes [<token>]. The record move's
    three flags together change two lines; over a backlog dirty on another line the same edit is undone, exit 4."""
    for name, line, want in (("flow", "    blocked_by: []\n", "    blocked_by: [claims-unresolved]\n"),
                             ("empty", "    blocked_by:\n", "    blocked_by: [claims-unresolved]\n"),
                             ("commented", "    blocked_by:   # none\n",
                              "    blocked_by: [claims-unresolved]   # none\n")):
        data = MINI.replace("    blocked_by: []\n", line)
        top = _repo(tmp, data, name)
        code, out, err = _edit(top, "U-001", "missing", block="claims-unresolved")
        _eq((code, err), (0, ""), name)
        _eq(_obj(out), {"first": 3, "last": 8, "changed": [8]}, name)
        _eq(_get(top), data.replace(line, want).encode("utf-8"), name)
    data = MINI_W.replace("status: missing", "status: drafted")
    want = data.replace(WALK8, "    walkthrough: U-001\n").replace("blocked_by: []", "blocked_by: [claims-unresolved]")
    top = _repo(tmp, data, "record")
    code, out, err = _edit(top, "U-001", "drafted", frm="drafted", walkthrough="U-001", block="claims-unresolved")
    _eq((code, err), (0, ""), "the record move")
    _eq(_obj(out), {"first": 3, "last": 9, "changed": [8, 9]}, "the record move")
    _eq(_get(top), want.encode("utf-8"), "the record move")
    top = _repo(tmp, data, "undone")
    dirty = data.replace("schema_version: 1\n", "schema_version: 1  # touched\n")
    _put(top, dirty)
    code, out, err = _edit(top, "U-001", "drafted", frm="drafted", walkthrough="U-001", block="claims-unresolved")
    _eq((code, err), (4, ""), "undone")
    _eq(_obj(out), {"undone": "hunk-outside", "first": 3, "last": 9, "changed": [8, 9]}, "undone")
    _eq(_get(top), dirty.encode("utf-8"), "byte-equal to what it read")


def case_edit_block_refused(tmp):
    """A blocked_by holding anything but [] or an empty value -- a token, the same token, a block sequence, null, ~, or
    an empty flow sequence spelled other than [] -- is blocked: exit 3, its line."""
    for name, lines in (("token", "    blocked_by: [env-down]\n"),
                        ("same-token", "    blocked_by: [claims-unresolved]\n"),
                        ("sequence", "    blocked_by:\n      - env-down\n"),
                        ("null", "    blocked_by: null\n"),
                        ("tilde", "    blocked_by: ~\n"),
                        ("spaced", "    blocked_by: [ ]\n")):
        data = MINI.replace("    blocked_by: []\n", lines)
        top = _repo(tmp, data, name)
        _edit_refused(top, data, {"refused": "blocked", "line": 8, "reason": None}, "U-001", "missing",
                      block="claims-unresolved")


def case_edit_no_blocked_by_key(tmp):
    data = MINI.replace("    blocked_by: []\n", "")
    top = _repo(tmp, data)
    _edit_refused(top, data, {"refused": "no-blocked-by", "line": 3, "reason": None}, "U-001", "missing",
                  block="claims-unresolved")


def case_edit_record_noop(tmp):
    """The record move over a unit that already holds what it asks: exit 0, changed empty, nothing written."""
    for name, data, flags in (("status", DRAFTED, {}),
                              ("walkthrough", MINI_W.replace("status: missing", "status: drafted")
                               .replace(WALK8, "    walkthrough: U-001\n"), {"walkthrough": "U-001"})):
        top = _repo(tmp, data, name)
        before = _stat(top)
        code, out, err = _edit(top, "U-001", "drafted", frm="drafted", **flags)
        _eq((code, err), (0, ""), name)
        _eq(_obj(out), {"first": 3, "last": 8 if name == "status" else 9, "changed": []}, name)
        _eq(_IO["writes"], 0, name + ": nothing written")
        _eq((_get(top), _stat(top)), (data.encode("utf-8"), before), name + ": bytes, inode and mtime")


# --walkthrough values in the unit-id class that YAML reads, written plain, as no string, one row per form: null (the
# one that would read back as no walkthrough), YAML 1.1's and 1.2's booleans, integers (decimal, 1.1's octal, hex,
# binary, underscores; 1.2's octal), floats (1.1's dotted forms, the spec's wider one, 1.2's exponent forms) and a date
# (two digits each, as YAML 1.1 has it, and one, as some loaders take it). `~` is outside the class already, and its row
# holds that too.
NON_STRING_IDS = ("null", "Null", "NULL", "~", "true", "True", "FALSE", "yes", "No", "ON", "off", "y", "N", "123", "0",
                  "017", "08", "0x1F", "0o17", "0b101", "1_000", "1__", "1.5", "1.", "1.2.3", "1e3", "1E-3", "1.5e3",
                  "2026-11-18", "2026-1-5")
# Ids near those forms that YAML reads as strings, which --walkthrough takes.
STRING_IDS = ("U-001", "W-9", "1-2", "inf", "nan", "x1e3", "0x", "0b2", "1_000e3", "1.2-3", "2026-11", "Y2K",
              "nullable", "onboarding", "yes-no")


def case_edit_new_flags_bad_args(tmp):
    """Each new flag outside its class, given twice or as --flag=value: exit 2, nothing read, run or written. A
    --walkthrough YAML reads as no string is outside its class; one near such a form passes."""
    top = _repo(tmp, MINI)
    before = _stat(top)
    edit = ["edit", "--repo", top, "--id", "U-001", "--status", "drafted"]
    for extra, why in ((["--from", "Drafted!"], WHY_FROM), (["--from", "null"], WHY_FROM),
                       (["--walkthrough", "../x"], WHY_WALKTHROUGH), (["--walkthrough", "U-001\n"], WHY_WALKTHROUGH),
                       (["--block", "a b"], WHY_BLOCK), (["--block", "true"], WHY_BLOCK),
                       (["--from", "drafted", "--from", "drafted"], WHY_USAGE),
                       (["--walkthrough", "U-001", "--walkthrough", "U-001"], WHY_USAGE),
                       (["--block", "x", "--block", "x"], WHY_USAGE), (["--block=x"], WHY_USAGE),
                       (["--from"], WHY_USAGE)) + tuple((["--walkthrough", v], WHY_WALKTHROUGH)
                                                        for v in NON_STRING_IDS):
        code, out, err = _call(edit + extra)
        _refused(code, out, err, why)
        _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "%r: nothing read, run or written" % (extra,))
    for v in STRING_IDS:
        _eq(_args(edit + ["--walkthrough", v])[1][5], v, "%r passes" % v)
    for flag in ("--from", "--walkthrough", "--block"):  # edit's flags, unknown to moved
        code, out, err = _call(["moved", "--repo", top, "--base", "main", "--id", "U-001", flag, "x"])
        _refused(code, out, err, WHY_USAGE)
    _eq((_get(top), _stat(top)), (MINI.encode("utf-8"), before), "untouched")


# ---- export ----

def _bytes_of(path):
    with open(path, "rb") as fh:
        return fh.read()


def _put_files(top, files, execs=()):
    """Each of `files`, {path: bytes}, under `top` -- a str value is the target of a symbolic link made there -- and
    each path in `execs` made executable."""
    for rel, data in files.items():
        p = os.path.join(top, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if isinstance(data, str):
            os.symlink(data, p)
        else:
            with open(p, "wb") as fh:
                fh.write(data)
        if rel in execs:
            os.chmod(p, 0o755)


def _src(tmp, files, name="src", execs=()):
    """A source repository at <tmp>/<name> whose one commit holds `files`, as _put_files writes them; (its path, the
    commit's object id)."""
    top = os.path.join(tmp, name)
    os.makedirs(top)
    _fx(top, "init", "-q", "-b", "main")
    _put_files(top, files, execs)
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "source")
    return top, _fx(top, "rev-parse", "HEAD").strip()


def _fx_in(cwd, data, *args):
    """_fx with `data` on git's stdin."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})
    r = subprocess.run(["git", "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid", *args],
                       cwd=cwd, env=env, check=True, input=data, capture_output=True)
    return r.stdout.decode("utf-8", "replace")


def _commit_entry(top, mode, oid, path):
    """A commit on top of HEAD adding the index entry `path`, with `mode` and object `oid`, which no working tree
    file need hold; the new commit's object id."""
    _fx(top, "update-index", "--add", "--cacheinfo", "%s,%s,%s" % (mode, oid, path))
    _fx(top, "commit", "-qm", "an entry")
    return _fx(top, "rev-parse", "HEAD").strip()


def _xdir(tmp):
    """A new directory to hold an export's --out and --manifest: (it, --out, --manifest)."""
    d = os.path.join(tmp, "x")
    os.mkdir(d)
    return d, os.path.join(d, "out"), os.path.join(d, "out.files")


def _export(repo, commit, out, manifest, *flags):
    return _call(["export", "--repo", repo, "--commit", commit, "--out", out, "--manifest", manifest, *flags])


def _export_ok(repo, commit, out, manifest, *flags):
    """export's JSON object and its stdout, where it exits 0 with an empty stderr."""
    code, stdout, err = _export(repo, commit, out, manifest, *flags)
    _eq((code, err), (0, ""), "export's exit and stderr")
    return _obj(stdout), stdout


def _manifest(path):
    """The manifest's pairs, (written path, repository path) as bytes, its NUL-separated layout checked."""
    data = _bytes_of(path)
    if not data:
        return []
    _true(data.endswith(b"\0"), "the manifest ends with a NUL")
    parts = data[:-1].split(b"\0")
    _eq(len(parts) % 2, 0, "the manifest holds pairs")
    return list(zip(parts[0::2], parts[1::2]))


def _files(out):
    """{path relative to `out`, as bytes: bytes} of every file under `out`; anything but a directory or a regular
    file -- a symbolic link among them -- fails the case."""
    got, root = {}, os.fsencode(out)
    for dirpath, dirnames, filenames in os.walk(root):
        for n in dirnames + filenames:
            p = os.path.join(dirpath, n)
            st = os.lstat(p)
            _true(stat.S_ISDIR(st.st_mode) or stat.S_ISREG(st.st_mode), "%r is a directory or a regular file" % p)
            if stat.S_ISREG(st.st_mode):
                got[os.path.relpath(p, root)] = _bytes_of(p)
    return got


def _skipped(**counts):
    return dict({"link": 0, "submodule": 0, "other": 0, "name": 0, "large": 0}, **counts)


def case_export_whole_tree(tmp):
    """--whole over nested directories, an executable and a non-ASCII UTF-8 name: each file byte-equal under --out,
    mode 0600 in a tree of mode 0700, the manifest pairing each written path with its repository path in tree order,
    files and bytes right, nothing else written, and the clone's index and working tree untouched -- with a GIT_DIR,
    GIT_WORK_TREE, GIT_INDEX_FILE and GIT_OBJECT_DIRECTORY in the environment naming another repository, which no git
    call export makes may read."""
    files = {"README.md": b"# top\n", "src/app.ts": b"export const x = 1;\r\n", "src/deep/er/mod.py": b"X = 2\n",
             "bin/run.sh": b"#!/bin/sh\necho hi\n", "docs/café.md": "café — ok\n".encode("utf-8")}
    top, oid = _src(tmp, files, execs=("bin/run.sh",))
    _eq(_fx(top, "ls-tree", "HEAD", "bin/run.sh").split(" ")[0], "100755", "the fixture's executable")
    status = _fx(top, "status", "--porcelain")
    index = os.path.join(top, ".git", "index")
    before = (_bytes_of(index), os.stat(index).st_mtime_ns)
    other, _ = _src(tmp, {"other.txt": b"another repository\n"}, name="other")
    hostile = {"GIT_DIR": os.path.join(other, ".git"), "GIT_WORK_TREE": other, "GIT_INDEX_FILE": index + ".other",
               "GIT_OBJECT_DIRECTORY": os.path.join(other, ".git", "objects")}
    saved = {k: os.environ.get(k) for k in hostile}
    d, out, man = _xdir(tmp)
    os.environ.update(hostile)
    try:
        obj, _ = _export_ok(top, oid, out, man, "--whole")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    _eq(_files(out), {k.encode("utf-8"): v for k, v in files.items()}, "the files written")
    tree = [p.encode("utf-8") for p in _fx(top, "ls-tree", "-r", "-z", "--name-only", oid).split("\0") if p]
    _eq(_manifest(man), [(p, p) for p in tree], "the manifest, in tree order")
    _eq(obj, {"files": 5, "bytes": sum(len(v) for v in files.values()), "skipped": _skipped(), "paths": {}})
    _eq(sorted(os.listdir(d)), ["out", "out.files"], "nothing else written")
    for dirpath, dirnames, filenames in os.walk(out):
        _eq(stat.S_IMODE(os.stat(dirpath).st_mode), 0o700, "%s's mode" % dirpath)
        for n in filenames:
            _eq(stat.S_IMODE(os.stat(os.path.join(dirpath, n)).st_mode), 0o600, "%s's mode" % n)
    _eq((_bytes_of(index), os.stat(index).st_mtime_ns), before, "the clone's index untouched")
    _eq(_fx(top, "status", "--porcelain"), status, "the clone's working tree untouched")


def case_export_links_not_followed(tmp):
    """A committed link to a file outside the repository, and one to a directory holding files: no path made for
    either, skipped.link 2, and the file outside -- the sentinel -- and its directory unchanged. A directory export
    has just made, --out or one under it, swapped for a link to that directory before export opens it: exit 2, and
    nothing written through the link."""
    outside = os.path.join(tmp, "outside")
    os.mkdir(outside)
    sentinel = os.path.join(outside, "secret.txt")
    _put_files(outside, {"secret.txt": b"secret\n", "more.txt": b"more\n"})
    mtime = os.stat(sentinel).st_mtime_ns
    top, oid = _src(tmp, {"a.txt": b"a\n", "lnfile": sentinel, "lndir": outside})
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole")
    _eq(sorted(os.listdir(out)), ["a.txt"], "no path made for either link")
    _eq(_files(out), {b"a.txt": b"a\n"}, "the regular file alone")
    _eq(_manifest(man), [(b"a.txt", b"a.txt")])
    _eq(obj, {"files": 1, "bytes": 2, "skipped": _skipped(link=2), "paths": {}})
    _eq((_bytes_of(sentinel), os.stat(sentinel).st_mtime_ns), (b"secret\n", mtime), "the sentinel unchanged")
    _eq(sorted(os.listdir(outside)), ["more.txt", "secret.txt"], "nothing written outside")
    top2, oid2 = _src(tmp, {"a.txt": b"a\n", "c/d.txt": b"d\n"}, name="src2")
    real = _make_dir
    for victim, base in ((b"c", "o1"), (b"o2", "o2")):  # a directory under --out, and --out itself
        def swapping(name, dfd):  # another process swaps the new directory for a link before it is opened
            real(name, dfd)
            if name == victim:
                os.rmdir(name, dir_fd=dfd)
                os.symlink(outside, name, dir_fd=dfd)
        out2, man2 = os.path.join(d, base), os.path.join(d, base + ".files")
        code, stdout, err = _with("_make_dir", swapping, lambda: _export(top2, oid2, out2, man2, "--whole"))
        _refused(code, stdout, err, WHY_EXPORT_WRITE)
        _eq(sorted(os.listdir(outside)), ["more.txt", "secret.txt"], "%r swapped: nothing written through it" % victim)


def case_export_submodule_skipped(tmp):
    """A gitlink entry: skipped.submodule 1, nothing made for it."""
    top, first = _src(tmp, {"a.txt": b"a\n"})
    oid = _commit_entry(top, "160000", first, "vendor/lib")
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole")
    _eq(obj, {"files": 1, "bytes": 2, "skipped": _skipped(submodule=1), "paths": {}})
    _eq(sorted(os.listdir(out)), ["a.txt"], "nothing made for the submodule")


def case_export_name_out_of_class(tmp):
    """Names holding a newline, a tab and a U+202E: skipped.name 3, none in stdout or the manifest. And a tree a
    committer built by hand, holding a directory .GIT, which git itself refuses to add: skipped name. A name above
    4,096 bytes is outside the class; one under it whose path under --out reaches the file system's PATH_MAX, which no
    reader could open by its absolute path: skipped name."""
    names = ("new\nline.txt", "tab\there.txt", "bidi‮txt.md")
    top, oid = _src(tmp, dict({"ok.txt": b"ok\n"}, **{n: b"x\n" for n in names}))
    d, out, man = _xdir(tmp)
    obj, stdout = _export_ok(top, oid, out, man, "--whole")
    _eq(obj, {"files": 1, "bytes": 3, "skipped": _skipped(name=3), "paths": {}})
    _eq(_files(out), {b"ok.txt": b"ok\n"})
    raw = _bytes_of(man)
    for n in names:
        _true(n.encode("utf-8") not in raw, "%r is not in the manifest" % n)
        _true(n not in stdout and json.dumps(n)[1:-1] not in stdout, "%r is not in stdout" % n)
    blob = _fx(top, "rev-parse", oid + ":ok.txt").strip()
    sub = _fx_in(top, b"100644 blob %s\tconfig\n" % blob.encode(), "mktree").strip()
    tree = _fx_in(top, b"040000 tree %s\t.GIT\n100644 blob %s\tok.txt\n" % (sub.encode(), blob.encode()),
                  "mktree").strip()
    crafted = _fx(top, "commit-tree", "-m", "crafted", tree).strip()
    out2, man2 = os.path.join(d, "out2"), os.path.join(d, "out2.files")
    obj, _ = _export_ok(top, crafted, out2, man2, "--whole")
    _eq((obj["skipped"], sorted(os.listdir(out2))), (_skipped(name=1), ["ok.txt"]), "a .GIT segment, in any case")
    _eq((_name_in_class(b"a/" * 2047 + b"bc"), _name_in_class(b"a/" * 2048 + b"b")), (True, False),
        "the name class: 4,096 bytes and no more")
    child = _fx_in(top, b"100644 blob %s\t%s\n" % (blob.encode(), b"f" * 60), "mktree").strip()
    for _ in range(19):  # with the one below, 20 directories of 200 bytes over a 60-byte file: 4,080 bytes
        child = _fx_in(top, b"040000 tree %s\t%s\n" % (child.encode(), b"s" * 200), "mktree").strip()
    tree = _fx_in(top, b"040000 tree %s\t%s\n100644 blob %s\tok.txt\n" % (child.encode(), b"s" * 200,
                                                                         blob.encode()), "mktree").strip()
    deep = _fx(top, "commit-tree", "-m", "deep", tree).strip()
    out3, man3 = os.path.join(d, "out3"), os.path.join(d, "out3.files")
    obj, _ = _export_ok(top, deep, out3, man3, "--whole")
    _eq((obj["skipped"], sorted(os.listdir(out3))), (_skipped(name=1), ["ok.txt"]), "a path past PATH_MAX under --out")


def case_export_ignore_files_renamed(tmp):
    """.gitignore, sub/.ignore and .rgignore are written as that name plus .exported, byte-equal, the manifest
    pairing each with its repository path, nothing skipped; a committed .gitignore.exported beside a .gitignore makes
    the second create fail EEXIST, skipped name."""
    files = {".gitignore": b"ignored-*\n", "sub/.ignore": b"*.log\n", ".rgignore": b"*\n", "sub/a.log": b"log\n"}
    top, oid = _src(tmp, files)
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole")
    _eq(_files(out), {b".gitignore.exported": b"ignored-*\n", b"sub/.ignore.exported": b"*.log\n",
                      b".rgignore.exported": b"*\n", b"sub/a.log": b"log\n"}, "the files written")
    _eq(_manifest(man), [(b".gitignore.exported", b".gitignore"), (b".rgignore.exported", b".rgignore"),
                         (b"sub/.ignore.exported", b"sub/.ignore"), (b"sub/a.log", b"sub/a.log")])
    _eq(obj, {"files": 4, "bytes": 22, "skipped": _skipped(), "paths": {}})
    top2, oid2 = _src(tmp, {".gitignore": b"ignored-*\n", ".gitignore.exported": b"committed\n"}, name="src2")
    out2, man2 = os.path.join(d, "out2"), os.path.join(d, "out2.files")
    obj, _ = _export_ok(top2, oid2, out2, man2, "--whole", "--path", ".gitignore.exported")
    _eq(_files(out2), {b".gitignore.exported": b"ignored-*\n"}, "the renamed file, the committed one skipped")
    _eq(_manifest(man2), [(b".gitignore.exported", b".gitignore")])
    _eq(obj, {"files": 1, "bytes": 10, "skipped": _skipped(name=1), "paths": {".gitignore.exported": "skipped"}})


def case_export_large_file_skipped(tmp):
    """Files of 1,048,576 and 1,048,577 bytes: the first exported, the second counted large; a --path naming the
    second is skipped."""
    top, oid = _src(tmp, {"cap.bin": b"a" * 1048576, "over.bin": b"b" * 1048577})
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole", "--path", "over.bin")
    _eq(obj, {"files": 1, "bytes": 1048576, "skipped": _skipped(large=1), "paths": {"over.bin": "skipped"}})
    _eq(_files(out), {b"cap.bin": b"a" * 1048576})


def case_export_over_cap(tmp):
    """EXPORT_FILES_CAP set to 3 over four files: exit 3, over-cap, files 4, --out not created; EXPORT_BYTES_CAP set
    one under the bytes the same; each cap met exactly exports."""
    top, oid = _src(tmp, {"a": b"1", "b": b"22", "c": b"333", "d": b"4444"})
    d, out, man = _xdir(tmp)
    for cap, value in (("EXPORT_FILES_CAP", 3), ("EXPORT_BYTES_CAP", 9)):
        code, stdout, err = _with(cap, value, lambda: _export(top, oid, out, man, "--whole"))
        _eq((code, err), (3, ""), cap)
        _eq(_obj(stdout), {"refused": "over-cap", "files": 4, "bytes": 10}, cap)
        _eq(os.listdir(d), [], cap + ": nothing created")
    for cap, value in (("EXPORT_FILES_CAP", 4), ("EXPORT_BYTES_CAP", 10)):
        out, man = os.path.join(d, cap), os.path.join(d, cap + ".files")
        obj, _ = _with(cap, value, lambda: _export_ok(top, oid, out, man, "--whole"))
        _eq((obj["files"], obj["bytes"]), (4, 10), cap + " met exactly")


def case_export_commit_absent(tmp):
    """An object id the clone does not hold, and one naming a blob: exit 3, commit-absent, nothing created."""
    top, oid = _src(tmp, {"a.txt": b"a\n"})
    d, out, man = _xdir(tmp)
    for commit in ("de" * 20, _fx(top, "rev-parse", oid + ":a.txt").strip()):
        code, stdout, err = _export(top, commit, out, man, "--whole")
        _eq((code, err), (3, ""), commit)
        _eq(_obj(stdout), {"refused": "commit-absent", "files": None, "bytes": None}, commit)
        _eq(os.listdir(d), [], "nothing created")


def case_export_paths_at_ref(tmp):
    """An older commit, --path a file and a directory, without --whole: only those exported, at that commit, both
    exported. A --path holding a glob character, or opening as pathspec magic does, is a literal path."""
    top, old = _src(tmp, {"src/a.ts": b"old a\n", "src/sub/b.ts": b"old b\n", "lib/c.ts": b"c\n", "README.md": b"r\n",
                          "lit/a*b.txt": b"star\n", "lit/aXb.txt": b"x\n"})
    _put_files(top, {"src/a.ts": b"new a\n", "lib/d.ts": b"d\n"})
    _fx(top, "add", "-A")
    _fx(top, "commit", "-qm", "newer")
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, old, out, man, "--path", "README.md", "--path", "src", "--path", "lit/a*b.txt",
                        "--path", ":/lib")
    _eq(_files(out), {b"README.md": b"r\n", b"src/a.ts": b"old a\n", b"src/sub/b.ts": b"old b\n",
                      b"lit/a*b.txt": b"star\n"})
    _eq(obj, {"files": 4, "bytes": 19, "skipped": _skipped(),
              "paths": {"README.md": "exported", "src": "exported", "lit/a*b.txt": "exported", ":/lib": "absent"}})


def case_export_path_states(tmp):
    """--whole with --path a file, a directory (also as ./dir/ and dir/.), an absent path, a prefix of a name that is
    no path, a link, and a file spelled as a directory (f.txt/.): exported, exported, exported, exported, absent,
    absent, skipped, absent -- f.txt/. as git lists it without --whole."""
    top, oid = _src(tmp, {"f.txt": b"f\n", "dir/g.txt": b"g\n", "dir/h.txt": b"h\n", "ln": "f.txt"})
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole", "--path", "f.txt", "--path", "dir", "--path", "./dir/",
                        "--path", "dir/.", "--path", "gone.txt", "--path", "di", "--path", "ln", "--path", "f.txt/.")
    _eq(obj["paths"], {"f.txt": "exported", "dir": "exported", "./dir/": "exported", "dir/.": "exported",
                       "gone.txt": "absent", "di": "absent", "ln": "skipped", "f.txt/.": "absent"})
    _eq(obj["skipped"], _skipped(link=1))
    out2, man2 = os.path.join(d, "out2"), os.path.join(d, "out2.files")
    obj, _ = _export_ok(top, oid, out2, man2, "--path", "f.txt/.")
    _eq((obj["files"], obj["paths"]), (0, {"f.txt/.": "absent"}), "f.txt/. without --whole")


def case_export_out_refused(tmp):
    """--out existing, a link, a dangling link or under a linked parent; --manifest existing, under a linked parent or
    --out itself, however spelled: exit 2 each, nothing run or written. --manifest planted as a link while the export
    runs: exit 2, the link's target untouched. --out's parent swapped for a link after the test: the export and its
    manifest land in the directory tested, now moved, and nothing under the link's target."""
    top, oid = _src(tmp, {"a.txt": b"a\n"})
    d = os.path.join(tmp, "x")
    real = os.path.join(tmp, "real")
    for p in (d, real, os.path.join(d, "taken")):
        os.mkdir(p)
    os.symlink(real, os.path.join(d, "linkout"))
    os.symlink(os.path.join(tmp, "nowhere"), os.path.join(d, "dangling"))
    os.symlink(real, os.path.join(d, "linkparent"))
    _put_files(d, {"taken.files": b""})
    listing = sorted(os.listdir(d))
    j = lambda *p: os.path.join(d, *p)
    for out, man, why in ((j("taken"), j("m"), WHY_OUT), (j("linkout"), j("m"), WHY_OUT),
                          (j("dangling"), j("m"), WHY_OUT), (j("linkparent", "out"), j("m"), WHY_OUT),
                          (j("out"), j("taken.files"), WHY_MANIFEST), (j("out"), j("linkparent", "m"), WHY_MANIFEST),
                          (j("out"), j("out"), WHY_MANIFEST), (j("out"), "/" + j("out"), WHY_MANIFEST),
                          (j("out"), j(".", "out"), WHY_MANIFEST)):
        code, stdout, err = _export(top, oid, out, man, "--whole")
        _refused(code, stdout, err, why)
        _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "%s, %s: nothing read, run or written" % (out, man))
    _eq((sorted(os.listdir(d)), os.listdir(real), os.path.lexists(os.path.join(tmp, "nowhere"))),
        (listing, [], False), "nothing written")
    victim = os.path.join(real, "victim")
    _put_files(real, {"victim": b"keep\n"})
    real_create = _create_file

    def planting(name, dfd):  # another process plants the manifest path as a link, mid-export
        if not os.path.lexists(j("m2")):
            os.symlink(victim, j("m2"))
        return real_create(name, dfd)
    code, stdout, err = _with("_create_file", planting, lambda: _export(top, oid, j("o2"), j("m2"), "--whole"))
    _refused(code, stdout, err, WHY_EXPORT_WRITE)
    _eq(_bytes_of(victim), b"keep\n", "the planted link's target untouched")
    parent, moved, elsewhere = os.path.join(tmp, "p"), os.path.join(tmp, "p.moved"), os.path.join(tmp, "elsewhere")
    for p in (parent, elsewhere):
        os.mkdir(p)
    real_xgit = _xgit

    def swapping(repo, *args):  # another process swaps --out's parent for a link while git lists the tree
        if args[0] == "ls-tree":
            os.rename(parent, moved)
            os.symlink(elsewhere, parent)
        return real_xgit(repo, *args)
    obj, _ = _with("_xgit", swapping, lambda: _export_ok(top, oid, os.path.join(parent, "out"),
                                                         os.path.join(parent, "out.files"), "--whole"))
    _eq((sorted(os.listdir(moved)), os.listdir(elsewhere), obj["files"]), (["out", "out.files"], [], 1),
        "written in the directory tested, nothing through the link")


def case_export_bare_repo_refused(tmp):
    """--repo laid out as a git directory with no .git, its config naming a core.fsmonitor that would write a
    sentinel: exit 2, no git call made, no sentinel. With an empty .git directory beside it, which git without
    safe.bareRepository=explicit passes over to take --repo itself as the repository, its top level --repo: exit 2.
    A clone's subdirectory holding an empty .git directory, which git passes over to name the clone its top level:
    exit 2."""
    gitdir, sentinel = os.path.join(tmp, "gitdir"), os.path.join(tmp, "sentinel")
    _fx(tmp, "init", "-q", "--bare", gitdir)
    for key, value in (("core.bare", "false"), ("core.worktree", gitdir), ("core.fsmonitor", "touch " + sentinel)):
        _fx(tmp, "config", "-f", os.path.join(gitdir, "config"), key, value)
    d, out, man = _xdir(tmp)
    code, stdout, err = _export(gitdir, "ab" * 20, out, man, "--whole")
    _refused(code, stdout, err, WHY_CLONE)
    _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "no git call made")
    _eq((os.path.lexists(sentinel), os.listdir(d)), (False, []), "no sentinel, nothing created")
    os.mkdir(os.path.join(gitdir, ".git"))
    code, stdout, err = _export(gitdir, "ab" * 20, out, man, "--whole")
    _refused(code, stdout, err, WHY_CLONE)
    _eq((os.path.lexists(sentinel), os.listdir(d)), (False, []), "an empty .git: no sentinel, nothing created")
    top, oid = _src(tmp, {"a.txt": b"a\n", "sub/b.txt": b"b\n"})
    os.mkdir(os.path.join(top, "sub", ".git"))
    code, stdout, err = _export(os.path.join(top, "sub"), oid, out, man, "--whole")
    _refused(code, stdout, err, WHY_CLONE)
    _eq(os.listdir(d), [], "a subdirectory: nothing created")


def case_export_bad_args(tmp):
    """Each export argument outside its class, a flag missing or given twice, or --flag=value: exit 2, nothing read,
    run or written; export's flags are unknown to the other verbs."""
    top, oid = _src(tmp, {"a.txt": b"a\n"})
    d, out, man = _xdir(tmp)
    base = {"--repo": top, "--commit": oid, "--out": out, "--manifest": man}

    def argv(extra, **swap):
        flags = dict(base, **{"--" + k: v for k, v in swap.items()})
        return ["export"] + [t for k, v in flags.items() if v is not None for t in (k, v)] + extra
    for args, why in ((argv(["--whole"], commit="HEAD"), WHY_COMMIT), (argv(["--whole"], commit=oid[:39]), WHY_COMMIT),
                      (argv(["--path", "../x"]), WHY_PATH), (argv(["--path", "/x"]), WHY_PATH),
                      (argv(["--path", "a\tb"]), WHY_PATH), (argv(["--path", "a‮b"]), WHY_PATH),
                      (argv(["--path", "a" * 4097]), WHY_PATH), (argv(["--path", "x\udcff"]), WHY_PATH),
                      (argv(["--whole"], repo="rel"), WHY_REPO_ABS), (argv(["--whole"], out="rel"), WHY_OUT),
                      (argv(["--whole"], repo=top + "\x01"), WHY_REPO_ABS), (argv(["--whole"], out=out + "\t"), WHY_OUT),
                      (argv(["--whole"], manifest=man + "\n"), WHY_MANIFEST),
                      (argv(["--whole"], manifest="rel/m"), WHY_MANIFEST),
                      (argv(["--whole"], repo=os.path.join(tmp, "absent")), WHY_REPO),
                      (argv([]), WHY_USAGE), (argv(["--whole", "--whole"]), WHY_USAGE),
                      (argv(["--whole"], commit=None), WHY_USAGE), (argv(["--whole", "--commit", oid]), WHY_USAGE),
                      (argv(["--path=a.txt"]), WHY_USAGE), (argv(["--path"]), WHY_USAGE),
                      (["check", "--repo", top, "--whole"], WHY_USAGE),
                      (["moved", "--repo", top, "--base", "main", "--id", "U-001", "--path", "a"], WHY_USAGE),
                      (["edit", "--repo", top, "--id", "U-001", "--status", "drafted", "--out", out], WHY_USAGE)):
        code, stdout, err = _call(args)
        _refused(code, stdout, err, why)
        _eq(dict(_IO), {"git": 0, "reads": 0, "writes": 0}, "%r: nothing read, run or written" % (args[1:],))
    _eq(os.listdir(d), [], "nothing created")
    _eq(_args(argv(["--path", "a" * 4096]))[1][5], ["a" * 4096], "a --path of 4,096 bytes passes")


def case_export_no_filter_run(tmp):
    """The clone's config naming a filter.x.clean, a filter.x.smudge and a diff.x.textconv, each a command that would
    write a sentinel, and a committed .gitattributes `* filter=x diff=x`: each file's raw blob bytes written, and no
    sentinel. A listing whose size is not its blob's, and a 100644 entry naming a tree, which ls-tree lists as a blob:
    exit 2, no manifest."""
    files = {".gitattributes": b"* filter=x diff=x\n", "a.txt": b"raw a\r\n", "b.md": b"raw b\n"}
    top, oid = _src(tmp, files)
    sentinel = os.path.join(tmp, "sentinel")
    for key in ("filter.x.clean", "filter.x.smudge", "diff.x.textconv"):
        _fx(top, "config", key, "touch '%s'; cat" % sentinel)
    _fx(top, "cat-file", "--filters", oid + ":a.txt")
    _true(os.path.lexists(sentinel), "the fixture's filter runs where git is asked to run it")
    os.unlink(sentinel)
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole")
    _eq(_files(out), {k.encode("utf-8"): v for k, v in files.items()}, "each file's raw blob bytes")
    _eq(obj["files"], 3)
    _true(not os.path.lexists(sentinel), "no filter or textconv ran")
    real = _xgit

    def lying(repo, *args):  # the last file's listed size one short, its blob's last byte a line feed
        r = real(repo, *args)
        return (r[0], r[1].replace(b"      6\tb.md", b"      5\tb.md")) if args[0] == "ls-tree" else r
    out2, man2 = os.path.join(d, "out2"), os.path.join(d, "out2.files")
    code, stdout, err = _with("_xgit", lying, lambda: _export(top, oid, out2, man2, "--whole"))
    _refused(code, stdout, err, WHY_BLOB)
    _true(not os.path.lexists(man2), "a blob not as listed: no manifest written")
    tree_oid = _fx(top, "rev-parse", oid + "^{tree}").strip()
    raw = b"100644 a.txt\0" + bytes.fromhex(tree_oid)  # a file entry whose object is a tree
    crafted = _fx(top, "commit-tree", "-m", "a tree as a file",
                  _fx_in(top, raw, "hash-object", "-t", "tree", "-w", "--literally", "--stdin").strip()).strip()
    out3, man3 = os.path.join(d, "out3"), os.path.join(d, "out3.files")
    code, stdout, err = _export(top, crafted, out3, man3, "--whole")
    _refused(code, stdout, err, WHY_BLOB)
    _true(not os.path.lexists(man3), "a tree listed as a file: no manifest written")


def case_export_timeout(tmp):
    """EXPORT_TIMEOUT set to 0.000001: exit 3, timeout, and no manifest written."""
    top, oid = _src(tmp, {"a.txt": b"a\n", "b.txt": b"b\n"})
    d, out, man = _xdir(tmp)
    code, stdout, err = _with("EXPORT_TIMEOUT", 0.000001, lambda: _export(top, oid, out, man, "--whole"))
    _eq((code, err), (3, ""))
    _eq(_obj(stdout), {"refused": "timeout", "files": 2, "bytes": 4})
    _true(not os.path.lexists(man), "no manifest written")


def case_export_name_collision(tmp):
    """A create forced in-process to fail EEXIST for one name, and a committed directory name of 256 bytes (a real
    ENAMETOOLONG): both skipped, skipped.name 2, every other file exported, exit 0."""
    top, _ = _src(tmp, {"a.txt": b"a\n", "b.txt": b"b\n", "c/d.txt": b"d\n"})
    blob = os.path.join(tmp, "blob")
    _put_files(tmp, {"blob": b"long\n"})
    oid = _commit_entry(top, "100644", _fx(top, "hash-object", "-w", blob).strip(), "y" * 256 + "/f.txt")
    real = _create_file

    def colliding(name, dfd):
        if name == b"b.txt":
            raise OSError(errno.EEXIST, "forced")
        return real(name, dfd)
    d, out, man = _xdir(tmp)
    obj, _ = _with("_create_file", colliding, lambda: _export_ok(top, oid, out, man, "--whole"))
    _eq(obj, {"files": 2, "bytes": 4, "skipped": _skipped(name=2), "paths": {}})
    _eq(_files(out), {b"a.txt": b"a\n", b"c/d.txt": b"d\n"})
    _eq(_manifest(man), [(b"a.txt", b"a.txt"), (b"c/d.txt", b"c/d.txt")])


def case_export_renamed_in_any_case(tmp):
    """An ignore file's name in another case -- .IGNORE, sub/.RgIgnore, .GitIgnore -- which a file system that folds
    case answers for .ignore, .rgignore or .gitignore; and the five names the Grep tool passes over wherever they
    stand -- .svn, .hg, .bzr, .jj and .sl, as a directory or a file, in any case: each segment written with .exported
    appended, byte-equal, the manifest pairing each with its repository path, nothing skipped. A committed
    .hg.exported directory beside .hg: one of the two skipped, name, never merged into the other."""
    files = {".IGNORE": b"*\n", "sub/.RgIgnore": b"*\n", ".GitIgnore": b"x-*\n", ".hg/hgrc": b"[ui]\n",
             "tools/.svn/entries": b"12\n", ".jj/x": b"jj\n", ".sl": b"sl\n", ".BZR/y": b"bzr\n", "sub/a.ts": b"a\n"}
    top, oid = _src(tmp, files)
    d, out, man = _xdir(tmp)
    obj, _ = _export_ok(top, oid, out, man, "--whole", "--path", ".hg/hgrc", "--path", "sub/.RgIgnore")
    written = {".IGNORE": ".IGNORE.exported", "sub/.RgIgnore": "sub/.RgIgnore.exported",
               ".GitIgnore": ".GitIgnore.exported", ".hg/hgrc": ".hg.exported/hgrc",
               "tools/.svn/entries": "tools/.svn.exported/entries", ".jj/x": ".jj.exported/x", ".sl": ".sl.exported",
               ".BZR/y": ".BZR.exported/y", "sub/a.ts": "sub/a.ts"}
    _eq(_files(out), {written[k].encode(): v for k, v in files.items()}, "the files written")
    tree = [p.encode() for p in _fx(top, "ls-tree", "-r", "-z", "--name-only", oid).split("\0") if p]
    _eq(_manifest(man), [(written[p.decode()].encode(), p) for p in tree], "the manifest, in tree order")
    _eq(obj, {"files": 9, "bytes": sum(len(v) for v in files.values()), "skipped": _skipped(),
              "paths": {".hg/hgrc": "exported", "sub/.RgIgnore": "exported"}})
    top2, oid2 = _src(tmp, {".hg/a": b"theirs\n", ".hg.exported/b": b"committed\n"}, name="src2")
    out2, man2 = os.path.join(d, "out2"), os.path.join(d, "out2.files")
    obj, _ = _export_ok(top2, oid2, out2, man2, "--whole")
    _eq((obj["files"], obj["skipped"], len(_files(out2))), (1, _skipped(name=1), 1), "one written, one skipped")


def case_export_parent_ignore_files(tmp):
    """Ignore files above --out -- a .rgignore, an .ignore and a .gitignore, each naming every file -- change nothing
    the export writes, and it writes no ignore file of its own: the files that outrank a parent's rules for a search
    tool, an .ignore and a .rgignore each holding !*, are the caller's to write beside its exports, never this
    script's."""
    files = {"a.txt": b"a\n", "node_modules/m.js": b"m\n", ".hidden/h.log": b"h\n", "src/app.ts": b"x\n"}
    top, oid = _src(tmp, files)
    d, out, man = _xdir(tmp)
    _put_files(tmp, {".rgignore": b"*\n", ".ignore": b"*\n", ".gitignore": b"*\n"})
    _put_files(d, {".rgignore": b"*.ts\nnode_modules/\n"})
    obj, _ = _export_ok(top, oid, out, man, "--whole")
    _eq(_files(out), {k.encode(): v for k, v in files.items()}, "every file written")
    _eq((sorted(os.listdir(d)), sorted(os.listdir(out))), ([".rgignore", "out", "out.files"],
                                                           [".hidden", "a.txt", "node_modules", "src"]),
        "no ignore file of the export's own")


def case_export_blob_absent(tmp):
    """A blobless partial clone lacking an older commit's blob, which ls-tree -l lists with the size BAD: exit 3,
    blob-absent, nothing created, whether a --path names it or --whole takes it, and no fetch made for it. A blob the
    listing sized that cat-file --batch then lacks: blob-absent, and no manifest."""
    src, old = _src(tmp, {"a.txt": b"old\n", "b.txt": b"b\n"})
    _put_files(src, {"a.txt": b"new\n"})
    _fx(src, "commit", "-qam", "newer")
    _fx(src, "config", "uploadpack.allowFilter", "true")
    clone = os.path.join(tmp, "clone")
    _fx(tmp, "clone", "-q", "--filter=blob:none", "file://" + src, clone)
    packs = sorted(os.listdir(os.path.join(clone, ".git", "objects", "pack")))
    d, out, man = _xdir(tmp)
    for flags in (["--path", "a.txt"], ["--whole"]):
        code, stdout, err = _export(clone, old, out, man, *flags)
        _eq((code, err), (3, ""), flags)
        _eq(_obj(stdout), {"refused": "blob-absent", "files": None, "bytes": None}, flags)
        _eq(os.listdir(d), [], "%r: nothing created" % (flags,))
    _eq(sorted(os.listdir(os.path.join(clone, ".git", "objects", "pack"))), packs, "no fetch made")
    real = _xgit

    def sized(repo, *args):  # the listing gives the absent blob a size: cat-file --batch then lacks it
        r = real(repo, *args)
        return (r[0], r[1].replace(b"    BAD\ta.txt", b"      4\ta.txt")) if args[0] == "ls-tree" else r
    code, stdout, err = _with("_xgit", sized, lambda: _export(clone, old, out, man, "--path", "a.txt"))
    _eq((code, err), (3, ""))
    _eq(_obj(stdout), {"refused": "blob-absent", "files": None, "bytes": None})
    _true(not os.path.lexists(man), "no manifest written")
    _eq(sorted(os.listdir(os.path.join(clone, ".git", "objects", "pack"))), packs, "still no fetch made")


def case_visibility_marker_pinned(tmp):
    """The visibility marker is page text three programs match: backlog-run.md's section 10.2 program, which
    /docs-write runs at its Phase 9 and /docs-verify at its Phases 1 and 4, and docs-verify.md's marker program and
    frontmatter program, which /docs-verify runs from its Phase 6 to its Phase 10. visibility.md section 5 states it
    on a line of its own, once; backlog-run.md holds it as its program's Python literal, once, and docs-verify.md as
    its two programs', twice; and docs-write.md, which holds no copy of a program, holds the literal nowhere."""
    with open(VIS_PATH, encoding="utf-8") as fh:
        vis = fh.read()
    sec = vis[vis.index("\n## 5. "):vis.index("\n## 6. ")]
    _eq(sec.split("\n").count(VISIBILITY_MARKER), 1, "visibility.md section 5 states the marker on a line, once")
    with open(BR_PATH, encoding="utf-8") as fh:
        br = fh.read()
    _eq(br.count('"' + VISIBILITY_MARKER + '"'), 1, "backlog-run's section 10.2 program holds its literal, once")
    with open(DW_PATH, encoding="utf-8") as fh:
        dw = fh.read()
    _eq(dw.count('"' + VISIBILITY_MARKER + '"'), 0, "docs-write holds the marker's literal nowhere")
    with open(DV_PATH, encoding="utf-8") as fh:
        dv = fh.read()
    _eq(dv.count('"' + VISIBILITY_MARKER + '"'), 2, "docs-verify's marker and frontmatter programs hold its literal")


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
         case_quoted_multiline_out, case_flow_question_out,
         case_flow_multiline_out, case_continuation_out, case_nested_continuation_out,
         case_anchor_alias_tag_tab_out, case_control_out, case_encoding_out, case_key_out, case_second_id_out,
         case_duplicate_status_out, case_column0_entries_out, case_nbsp_indent_out, case_trailing_text_out,
         case_status_missing_out, case_status_flow_out, case_document_start_line_one_only,
         case_entry_indent_non_id_out, case_too_large_out,
         case_units_twice_out, case_units_flow_out, case_units_empty_ok, case_under_indent_out, case_id_quoted_out,
         case_duplicate_id, case_symlink_refused, case_not_regular_refused, case_moved_on_branch,
         case_ref_name_outside_class, case_ref_unreadable, case_absent_not_moved, case_twenty_cap,
         case_examined_cap, case_no_base, case_moved_working_refused, case_edit_two_keys, case_edit_tilde_null,
         case_edit_page_path_set, case_edit_page_path_same, case_edit_no_page_path_key, case_edit_refused_content,
         case_edit_changed_while_reading, case_edit_changed_after_write, case_edit_undo_blocked, case_edit_undo_failed,
         case_edit_undo_failed_over_another_writer, case_edit_undo_failed_unreadable,
         case_edit_noop,
         case_edit_not_a_repository, case_edit_undo, case_bad_args,
         case_own_moves_open_draft_branch, case_own_moves_real_move, case_own_moves_no_merge_base,
         case_own_moves_merge_base_unreadable, case_own_moves_unchanged_without_flag, case_own_moves_bad_args,
         case_base_merge_commit, case_base_squash_branch_deleted, case_base_own_draft_not_moved,
         case_base_reset_on_branch_not_moved, case_base_criss_cross_every_merge_base, case_base_shallow_unknown,
         case_base_orphan_unknown, case_base_fork_backlog_unreadable,
         case_local_base_unpushed_move, case_local_base_diverged, case_local_base_behind_not_read,
         case_local_base_holds_working_branch, case_local_base_same_draft_on_origin, case_local_base_head_on_it,
         case_local_base_shallow_unknown, case_ref_named_as_a_base,
         case_edit_from_refused, case_edit_from_ok, case_edit_walkthrough_unset, case_edit_walkthrough_other,
         case_edit_walkthrough_same, case_edit_no_walkthrough_key, case_edit_block_sets, case_edit_block_refused,
         case_edit_no_blocked_by_key, case_edit_record_noop, case_edit_new_flags_bad_args,
         case_export_whole_tree, case_export_links_not_followed, case_export_submodule_skipped,
         case_export_name_out_of_class, case_export_ignore_files_renamed, case_export_large_file_skipped,
         case_export_over_cap, case_export_commit_absent, case_export_paths_at_ref, case_export_path_states,
         case_export_out_refused, case_export_bare_repo_refused, case_export_bad_args, case_export_no_filter_run,
         case_export_timeout, case_export_name_collision, case_export_renamed_in_any_case,
         case_export_parent_ignore_files, case_export_blob_absent,
         case_visibility_marker_pinned,
         case_shape_paragraph_pinned, case_marker_phrase_pinned)


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

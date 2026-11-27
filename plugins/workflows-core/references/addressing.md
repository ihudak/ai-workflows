# Addressing — Shared Reference

The key grammar, the directory-naming convention, and the folder-resolution rule for **every** folder
under `$SPECS_PATH/specifications/` — a BRD, a PRD, or an Epic alike. This file is where addressing is
defined once rather than reinvented per caller. Design authority:
`docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` §§4–5 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-31-specs-native-pipeline-design.md` retrieves it).

**Consumed by every command that addresses a folder in the specs tree.** Each calls `resolve-address`
(§3) and, where it reads its address before touching the filesystem, `read-key` (§1) — or, where it
mints a key, `key-valid`; the three that create the folder their address names print `key-summary`
(§1) on a missing key. Those commands
are what `grep -l resolve-address plugins/*/commands/*.md` returns — re-run it rather than keeping a
list or a count here, since both went stale in this paragraph — and they, with the one shared
authority §7 names, all reach the tree through this file; `product-workflows:brd-format` and
`product-workflows:coverage-ledger-format` cite it for the key grammar and folder resolution neither
of them restates.

## 1. Key grammar

```
^[A-Z][A-Z0-9_]*(-\d+)+$
```

A key is one or more hyphen-numeric segments after a leading alphabetic token. `ACME-90`,
`ACME-90-01` and `ACME-90-01-01` are all valid — the grammar fixes no depth. **Shape is not depth**:
how many segments a key carries says nothing about where its folder sits, which §3 bounds at three
levels below `specifications/` regardless.

**One grammar, one namespace.** There is no second, narrower grammar for a "tracker" key: the plugin
reads no tracker, mints its own keys, and validates every key against this one expression. A caller
that re-states this grammar locally instead of citing this section is the defect family the plugin
source repository's `docs/maintainers/rationale.md` records under `resolve-against-a-known-set` — the
copies drift, and a key that is valid here hard-stops somewhere else.

**Shape only, never checked against anything.** A key names a folder in `$SPECS_PATH`, not a record
in a system that could confirm it exists. Validating shape and validating existence are two different
questions, and this section answers only the first; §3 answers the second.

### Entry point: `key-valid <KEY>`

Returns `valid` when `<KEY>` matches the grammar above, `invalid` otherwise. Takes no other input and
touches no filesystem — a pure string test, safe to call before `$SPECS_PATH` is even resolved.

### Entry point: `read-key <TOKEN>`

**Reads a key the operator typed as an address, where `key-valid` tests one.** Three readings, tried
in this order, the first that holds winning:

1. **A key.** Where `key-valid <TOKEN>` is `valid`: `key: <TOKEN>`, `prefix: none`.
2. **A folder's whole name.** Where `$SPECS_PATH/specifications/` is a directory, `<TOKEN>` is in
   §2's class — checked as text for a `'`, then with §2's program, before any command names it; a
   token outside it is no folder's whole name, and this reading is not tried — and the resolution
   program's `name` mode (§3) finds exactly one directory at most three levels below it named
   `<TOKEN>` exactly — §2's reserved names never counted, nor anything under them — that program
   holds the folder's path to §3's *The path's class*, and `read-key` returns **`misnamed`** where a
   component of it is outside the class, or where the program could not read it, or found none and
   could not list a directory that may hide it (§3, `reason: unreadable`), or would print a path
   that is not a printable value (§3, `reason: control`), no command having named the
   folder; otherwise the program reads that folder's carrier (§4), and the name begins
   `<KIND>-<key>-` (§4.1, `<KIND>` one of §2's three, `<key>` the key the carrier asserts) or, a legacy name (§5), `<key>-`: `key:` that
   key and `prefix:` that kind, or `none` for a legacy name. A name that begins with neither is §4's
   hard stop on a key that disagrees with its folder name; a folder with no carrier yields nothing
   here, and its key or an `@<path>` still reaches it (§5).
3. **A key behind its folder's kind prefix.** Where `<TOKEN>` is one of §2's three folder kinds and a
   hyphen — `BRD-`, `PRD-` or `EPIC-` — followed by a rest `key-valid` finds valid: `key: <the rest>`,
   `prefix: <that kind>`.

Where `$SPECS_PATH` is unset the second reading cannot be tried, and a token neither of the others takes returns **`needs-tree`** rather than `invalid`: a caller whose address is required takes its own `$SPECS_PATH` stop on it, wherever in its order that check stands, rather than a key-grammar stop the token may never have been meant to meet, and — that stop answered with a path — reads the token again with `read-key`, from the top of the step that first read it, its own `invalid` stop applying to the result; a caller with a direct mode reads it as no address, since with no tree to look in a whole name cannot be told from prose. Anything else is `invalid` — a `$SPECS_PATH` holding no `specifications/` included, where no name can match.

**`misnamed` is `resolve-address`'s stop of that name (§3), wherever the token is read**: `resolve-address` returns `status: misnamed` on it, and a caller that reads its address with `read-key` before resolving takes that stop at the step that read it, never its own `invalid` stop, and a mode test (`workflows-core:run-flags` §3) reads the token as an address — the token named a folder, and the folder's name, or one above it, is what the stop is about.

**The line.** A reading other than the first prints one line —
`Read '<TOKEN>' as the key <key> — <prefix>- is a folder kind prefix, not part of a key.` for the
third, `Read '<TOKEN>' as the key <key> — the name of its folder, <path below specifications/>.` for
the second — once per run, at the first step that reads the token for its key: a step that only decides whether a token is an address (a mode test, `workflows-core:run-flags` §3) prints nothing and hands on the token as typed, and every step after that first read is handed the key.

**Why it exists.** Every folder the family creates is named `<KIND>-<KEY>-<slug>` (§2), so the
prefixed form and the whole name are what an operator sees in the tree, and typing either is the
natural gesture: a live `/dev-workflows:design EPIC-BOOK-1-01` stopped with "not a key" beside the
Epic folder `EPIC-BOOK-1-01-alerts-service/`, and the operator read the stop as "not found".

**It cannot misread a key, and it parses nothing.** A key's leading token holds no hyphen and the
segment after it is numeric, so a kind, a hyphen and a key — whose own leading token is alphabetic —
never passes `key-valid`, which is tried first, and `EPIC-008`, a key beginning with a kind token
(§2), stays the key `EPIC-008`. A whole name is matched against the folders the tree holds and its
key read off the carrier, never split out of the name (§4), and it is tried before the prefixed
reading, so a name whose slug is all digits (`PRD-ACME-1-2024`) is read as its folder and never as the
key `ACME-1-2024`. The prefix is matched against the closed set of §2's three kinds and the rest held
to the whole grammar above — so nothing is extracted by pattern.

**The second reading reads the tree, and where it runs decides which tree.** A caller that resolves
its address before its preflight reads the checkout as it stands, as its resolution does anyway. A
caller that reads its key before the preflight — its run key set being that key (§3.2 of
`workflows-core:specs-repo-git`) — reads a whole name on the checkout the preflight may then switch
away from; it resolves the key read after the preflight as always. **A whole name that then resolves `absent` stops the run, whatever the command**: the folder it named was on the checkout before the preflight moved it, and creating one for its key would make a second. The stop names the token, the branch it was read on and the branch the run now stands on; a caller whose `absent` is already a stop adds those two branches to its own stop's text and, in place of its remedies, says to merge the branch the name was read on and re-run; a caller that goes on keyless on `absent` (`/dev-workflows:vuln`) takes this stop instead.

**From a reading that is not the first, the run's key is `key`, never the token typed** — in every
later step and in everything the run prints or writes — so neither a prefix nor a slug reaches a
message, branch, commit subject or file. **It reads an address, never a key to mint**: a key an
operator supplies or a command proposes for a new child folder (`/product-workflows:brd-split`,
`/product-workflows:epics`) is held to `key-valid` alone, and only the key, never a whole name, is
validated for shape only. **A command that creates the folder its address names where resolution
returns `absent`** — `/product-workflows:idea` and `/product-workflows:create-prd` a `PRD-` folder,
`/product-workflows:brd-intake` a `BRD-` one — creates it only where `prefix` is `none` or that kind and the token was not a whole name, and otherwise stops before creating anything — a key behind a prefix of another kind with:
`'<TOKEN>' names a <prefix>- folder, and this command creates a <its kind>- folder — re-run it with the bare key <key>.`
and a whole name of any kind with the stop above, since its folder was there before the preflight.

### Entry point: `key-summary`

**What a missing-key stop prints beneath itself, so the person typing a key sees the keys already
taken.** Called by the stops of the three commands that create the folder their address names where
resolution returns `absent` (above) — `/product-workflows:idea` (`IDEA_NEEDS_KEY`),
`/product-workflows:create-prd` (`CREATE_PRD_NEEDS_KEY`) and `/product-workflows:brd-intake`
(`BRD_INTAKE_NEEDS_KEY`) — where the key is absent or invalid. **It proposes no key and validates
none**: the operator still types the key, and `read-key` reads it as any other. A key read off this
checkout need not be the next one free on a branch it cannot see, and the prefix a new document takes
is the team's to choose.

**It reads keys as §3 resolves them, never out of a name or a key's shape.** Every folder at most
three levels below `specifications/` (§3's bound), passing over §2's reserved subdirectories and
everything below them, has its key read off its carrier (§4) — never off a document that is not one,
such as a customer's source copied under `brd/` or a vendored attachment. A symbolic link, a hidden
directory and an unreadable one are passed over. A folder directly under
`specifications/` counts as **top-level**, one below another folder as **nested**: where the folder
sits decides it, never how many segments its key carries (§1, *Shape is not depth*). Within one
leading token, the highest top-level key is the one whose numeric segments, compared in order as
numbers, come last — a key read, never one built. Run it and print what it prints:

```bash
python3 - "$SPECS_PATH" <<'EOF'
import os, re, stat, sys, unicodedata
KEY = re.compile(r"[A-Z][A-Z0-9_]*(-[0-9]+)+")
RESERVED = {"brd", "grounding", "interview", "dev-workflows", "design", "attachments", "revisions", "Doc screenshots"}
root = os.path.join(sys.argv[1], "specifications") if len(sys.argv) > 1 and sys.argv[1] else ""
if not root or not os.path.isdir(root):
    print("No specs tree to list keys from — $SPECS_PATH is unset or holds no specifications/.")
    sys.exit(0)
def frontmatter(path):  # a file that is no regular file, a FIFO say, reads as none and is never waited on
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        with open(fd, encoding="utf-8-sig", errors="replace") as fh:
            if not stat.S_ISREG(os.fstat(fd).st_mode) or fh.readline().strip() != "---":
                return {}
            fields = {}
            for line in fh:
                if line.strip() == "---":
                    return fields
                name, sep, value = line.partition(":")
                if sep and name.strip() in ("key", "kind"):
                    fields[name.strip()] = value.strip().strip("\"'")
    except OSError:
        pass
    return {}
def listing(folder):  # an unreadable folder is passed over, never a traceback under the stop
    try:
        return os.listdir(folder)
    except OSError:
        return []
def in_class(name):  # §2's class, on the name's bytes read as UTF-8
    try:
        n = os.fsencode(name).decode("utf-8")
    except UnicodeError:
        return False
    return n != "" and ".." not in n and (n[0] == "_" or n[0].isalnum()) and all(c.isalnum() or c in "._@+-" or unicodedata.category(c).startswith("M") for c in n)
def carrier_key(folder):  # §4: top-level files named in the class, in byte-wise order, else brd/brd-inventory.md
    names = sorted((n for n in listing(folder) if in_class(n) and os.path.isfile(os.path.join(folder, n))), key=os.fsencode)
    for name in names + [os.path.join("brd", "brd-inventory.md")]:
        fields = frontmatter(os.path.join(folder, name))
        if fields.get("kind") in ("brd", "prd", "epic") and KEY.fullmatch(fields.get("key", "")):
            return fields["key"]
    return None
top, nested, best = {}, {}, {}
def walk(folder, depth):
    for name in sorted(listing(folder)):
        path = os.path.join(folder, name)
        if name.startswith(".") or os.path.islink(path) or not os.path.isdir(path) or name in RESERVED or name.startswith(("bundle-", "customer-sent-")):
            continue
        key = carrier_key(path)
        if key:
            token, numbers = key.split("-")[0], tuple(int(n) for n in key.split("-")[1:])
            if depth == 1:
                top[token] = top.get(token, 0) + 1
                if token not in best or numbers > best[token][0]:
                    best[token] = (numbers, key)
            else:
                nested[token] = nested.get(token, 0) + 1
        if depth < 3:
            walk(path, depth + 1)
walk(root, 1)
tokens = sorted(set(top) | set(nested), key=lambda t: (-top.get(t, 0), -nested.get(t, 0), t))
if not tokens:
    print("No key is in this specs tree yet.")
    sys.exit(0)
print("Keys already in this specs tree, by prefix — this checkout as it stands; another branch may hold more:")
for t in tokens[:10]:
    highest = "highest " + best[t][1] if t in best else "no top-level key"
    print(f"  {t} — {highest} ({top.get(t, 0)} top-level, {nested.get(t, 0)} nested)")
if len(tokens) > 10:
    print(f"  …and {len(tokens) - 10} more prefixes")
EOF
```

At most ten prefixes are listed, most top-level keys first, so hundreds of keys come to a handful of
lines.

## 2. Directory naming

```
<KIND>-<KEY>-<slug>/          kind ∈ BRD | PRD | EPIC
```

**Two invariants, and §3's bound is derived from the second:**

1. **Kinds appear in a fixed order down any path** — `BRD` → `PRD` → `EPIC`, each optional at the top.
   An idea-route PRD folder sits directly under `specifications/`; a BRD-route PRD folder is the
   slice folder inside its BRD. Both are `PRD-` folders, both are where the `prd.md` is authored, and
   both hold their Epics one level below. **The `BRD-` folder itself is never one of them**: it is a
   container, and `prd.md`, `ard.md` and `specification.md` are authored in the `PRD-` slice folders
   under it, never beside `brd/` and `coverage-ledger.md`
   (`product-workflows:coverage-ledger-format` §5).
2. **No path holds two folders of the same kind.** Every level is therefore identifiable from its own
   name without reading its parent, and the tree is at most three levels deep.

**Reserved subdirectory names are not folder kinds.** A folder under `specifications/` may hold
fixed-name subdirectories whose names carry no key and that are never resolved by one — `brd/`,
`grounding/`, `interview/`, `dev-workflows/`, `design/` (exported frame sets, one per immediate subdirectory, each
indexed per `references/grounding-format.md` §6.1–§6.2), `attachments/` (the text and markdown sources a run copied
into the folder — `product-workflows:idea-format`, *Vendored sources*), `revisions/` (a document's archived
prior revisions — `/product-workflows:update-prd` and `/product-workflows:create-prd` for a PRD, `product-workflows:proposal-format` for a proposal),
`bundle-<YYYYMMDD>/` (a customer package — `product-workflows:bundle-packaging`), `customer-sent-<YYYYMMDD>/`
(the material a `--sent` run records — `/product-workflows:brd-reconcile`), and `Doc screenshots/` (images `/docs-workflows:document`
stages for a page — that command's own Phase 5.6). None matches §3's `*-<KEY>-*` glob,
so resolution passes over them without a rule of its own, and none carries a `brd-link.md`, so
`/brd-split`'s positive test excludes them by construction rather than by an exclusion list.

**Each reserved name is defined once, elsewhere, and cited here.** This list is the register of names
resolution must pass over; it is not where any of them acquires its meaning. `brd/` is
`product-workflows:brd-format`'s (§1.1 for its `source/` capture, §2 for the inventory inside it),
`grounding/` is `references/grounding-format.md`'s (§2 for the finding files it holds, which
`/product-workflows:prd-ground` Phase 8 writes), `interview/` is `/product-workflows:brd-interview`'s
(Phase 9, which writes each round record, with `product-workflows:interview-tagging` §5 owning what a
round is), `dev-workflows/` is `references/specs-repo-git.md` §2.1's, `design/` is
`grounding-format.md` §6.1's — with §6.2 owning the index every set inside it must carry —
`attachments/` is `idea-format.md`'s, and each other name is the owner cited beside it in the list
above; a name added here without an authority to cite is a name two files will disagree about.
`specs-repo-git.md` §2.1's classifier excludes every name in the list but `dev-workflows/`, so that
a file a run copied in is never committed as a session file, and a name added here is added there too —
and to the `RESERVED` sets and prefixes of `key-summary` (§1) and of the resolution program (§3), so neither reads a key off a file a run copied in.

**A user whose own key begins with a kind token gets `PRD-PRD-1234-…`.** That is a documented
consequence of a documented convention, not a defect, and it is not hypothetical: a key like
`EPIC-008` yields `PRD-EPIC-008-01-orders` and `EPIC-EPIC-008-01-01-intake`. We cannot dodge every key
any user might pick, and a convention that can be relied on is worth more than one that bends. The
convention is stated in the README and in `docs/`; a user who then names their work `PRD-…` has chosen
the collision.

**The class of a folder's name — a read-side guard, not a naming rule.** A folder's name, read back
from the tree, is data: the family's commands wrote it, or a person did, and a command that builds a
shell command from it would run a `$(`, a backtick or a quote it held. So a caller that cites this
paragraph holds such a name to one class before any command is built from it. **A name is in the
class** where it is not empty, its first character is `_` or a letter or digit of any script, every
later character is a letter, a digit or a combining mark of any script, or one of `. _ @ + -`, and
it holds no `..` — in regular-expression terms, matched whole:

```
^(?!.*\.\.)[\p{L}\p{N}_][\p{L}\p{N}\p{M}._@+-]*$
```

**Test it with this program**, which needs no `grep` that knows Unicode classes, each name handed to
it as one single-quoted argument, never in a here-document, which a line of the name could end:

```
python3 -I -c 'import os, sys, unicodedata as u
def ok(a):
    try:
        n = os.fsencode(a).decode("utf-8")
    except UnicodeError:
        return False
    return n != "" and ".." not in n and (n[0] == "_" or n[0].isalnum()) and all(c.isalnum() or c in "._@+-" or u.category(c).startswith("M") for c in n)
ns = sys.argv[1:]
bad = [i for i, a in enumerate(ns, 1) if not ok(a)]
if bad:
    print(bad[0])
sys.exit(1 if bad else 0 if ns else 2)' '<name>'
```

**The name is in the class only where the program exits 0**; any other exit — 1, its refusal, 2
where it was handed no name, 127 where no `python3` runs, or any other — means it is outside.
**Handed several names**, each as one more single-quoted argument after the first — as §3's *The
path's class* hands it the components of one path — it exits 0 only where every one is in the
class. On its refusal, exit 1, it prints on its standard output the place, counting from 1, of the
first that is outside it — printed, never carried in the exit status, which wraps at 256 and would
read a name at place 256 as in the class — and any exit but 0 and 1 shows none of them in it. It
tests a name's bytes, read as UTF-8 (`os.fsencode`), so a Python that decoded its arguments in
another encoding — a C locale's, on an older Python — still tests the name a listing printed, and a
name that is not UTF-8 is outside. `str.isalnum()` holds for exactly the letters
and digits of Unicode's `L` and `N` categories, and a category opening `M` is a combining mark.
**First, as text, the name is checked for a `'`**, the one character that ends a single-quoted word:
a name holding one is outside the class and is never handed to the program, nor is any other command
built from it. A name read from a listing holds no line feed: git's listings quote a name holding
one (below), and the checkout's print it as `?` (*A folder refused by its name*), so a name is one
line either way, and a name holding `?` is outside the class whichever it held.
**Why a name in the class is safe in a command**, single-quoted or double-quoted: no shell
metacharacter, quote, backslash or `$` passes, nor any whitespace, nor a control or format character
(categories `Cc` and `Cf`, a bidirectional override among them); every character it admits outside
ASCII is encoded in bytes no shell treats as syntax; its first character is never `-`, which a
command would read as an option, nor `.`, so it is never `.` or `..`; and it holds no `..` anywhere,
which git reads as a range in an object name such as `<ref>:./<path>`. **So a path built from
folder names stays double-quoted in the family's commands** — `"$SPECS_PATH/<path>"`, `"./<P>"`,
`"<ref>:./<path>"` — and is never rewritten to single quotes for safety: inside double quotes a
shell still acts on a `$`, a backtick, a `"` and a `\`, and a path whose every component is in the
class holds none of them. **That holds only while every entry point of a folder's name read from the
tree into a command tests the class**: §3's `resolve-address`, on each component of every path a
record it returns carries (§3, *The path's class*), its resolution program reading every other
folder it meets itself, a command built from no name; and every caller that lists the folders under a
folder, which tests each name it reads before a command is built from it and cites *A folder refused
by its name* below — as §4 holds a carrier's file name, and each caller that lists files holds each
file's. A command built from a folder's name that passed neither test is a defect of the caller that
built it, fixed by the test, never by other quotes. **A folder whose name is
outside the class is named in words and never read** — by its position in the listing, or as a
folder named outside this class, never by its name: nothing is built from its name, and the caller
says what it therefore leaves out. Where git lists the names, the listing pins
`-c core.quotePath=false`, so a name holding a letter outside ASCII prints as it stands, not in git's
quoted form; a name holding a control character, `"` or `\` is still printed quoted, opening `"`, and
is outside the class. The reserved subdirectory names above are no folders' names and are passed over
before the test, untested and unnamed — `Doc screenshots/` holds a space. A name a command creates
is not tested here.

**A folder refused by its name, among the folders a caller lists under a folder `<P>`** — `<P>`
the folder's path relative to `$SPECS_PATH`, as the caller holds it. The caller names it by its
position: `entry <n> of the checkout's listing of <P>'s folders`, `<n>` its place, counting from 1,
among the lines `(cd "$SPECS_PATH" && find "./<P>" -mindepth 1 -maxdepth 1 -type d -print0) 2>/dev/null | LC_ALL=C sort -z | tr '\n\0' '?\n'`
prints — one line per folder, in byte-wise order: `find` ends each path with a NUL, which no name
holds, `sort -z` orders them, and `tr` prints a line feed inside a name as `?` before each NUL
becomes a line's end, so a name holding a line feed is still one line and moves no other folder's
place — or, for a folder only `<default-ref>` holds, `entry <n> of the default branch's listing of
<P>'s folders`, among the lines its `git -C "$SPECS_PATH" -c core.quotePath=false ls-tree -d
--name-only "<default-ref>" -- "./<P>/"` prints — and gives the remedy: `rename it into
workflows-core:addressing §2's class — letters, digits and combining marks of any script and
. _ @ + -, first a letter, a digit or _, no .. — or move it out of <P>`. **Whether it may be an
Epic folder** — one holding an `epic.md` — is read off a listing of `<P>`'s files, compared as text,
its name entering no command: in the checkout, a line of
`(cd "$SPECS_PATH" && find "./<P>" -mindepth 2 -maxdepth 2 -type f -name epic.md -print0) 2>/dev/null | tr '\n\0' '?\n'`
that is, whole, `./<P>/<its name>/epic.md`, `<its name>` as the listing of `<P>`'s folders printed
it; on `<default-ref>`, a line of
`git -C "$SPECS_PATH" -c core.quotePath=false ls-tree -r --name-only "<default-ref>" -- "./<P>/"`
that is, whole, `<P>/<its name>/epic.md`. A folder no such line names holds no `epic.md` either
listing can show, and a caller that says what it leaves out for an Epic leaves it out of that.
**Whether it may be a slice** — for a caller listing a BRD folder's subdirectories, one holding a
`brd-link.md` — is read the same way, from the same two listings, `brd-link.md` in place of
`epic.md`; a folder neither listing shows holding one is no slice, and the caller passes over it.
**In the checkout's listings a `?` stands in for a line feed**, so a name printed holding `?` may
hold either, and two folders can print alike — `a?z` for one named `a?z` and for one named `a`, a
line feed, `z`. A line naming that printed name then holds for each, and each is said to be what it
may be: each may be an Epic folder, or a slice, which is all either test says, and the caller names
each by its own position. Either folder is outside the class for its name, whatever it holds, so
neither is read.
**A file refused by its name**, among the files a caller lists in a folder `<P>`, is named the same
way: `entry <n> of the checkout's listing of <P>'s files`, `<n>` its place, counting from 1, among
the lines `(cd "$SPECS_PATH" && find "./<P>" -mindepth 1 -maxdepth 1 -type f -print0) 2>/dev/null | LC_ALL=C sort -z | tr '\n\0' '?\n'`
prints, one line per file, as the listing of its folders prints one per folder. **A folder that
cannot be listed is never an empty one.** The checkout's listings discard `find`'s errors, so a
caller that must tell a `<P>` it cannot read from one holding nothing runs the listing as
`(set -o pipefail; <the listing>)` and reads its exit: where `<P>` is a directory
(`test -d "$SPECS_PATH/<P>"`) and that exit is not 0, `find` could not read it, and the caller
takes it as unreadable — naming it, and what it therefore did not read — never as empty.

**What it covers, and what it does not.** Every name `<KIND>-<KEY>-<slug>` whose slug holds only
letters, digits and combining marks of any script and `-` is inside it — the slug
`/product-workflows:brd-intake` derives from a heading in another script, `zahlungsauslösung-anforderungen`
for one, among them — and so are §5's legacy `<KEY>_<slug>` and `<KEY>-<slug>` of such a slug. **It
is tested on the path a run's own address resolved**, by §3's `resolve-address` (*The path's
class*), on each component of it below `$SPECS_PATH` — the folder itself and each folder above it up
to `specifications/`, the PRD folder above an Epic and a slice's `BRD-` folder among them — so a
command a run builds from its resolved folder, or from a folder above it, is built from names in the
class. **And it is tested on a name a caller reads from a listing** — of the folders or the files
under a folder the run holds: under the run's own folder, under the PRD folder above an Epic (an Epic
run's siblings among them), or under a fixed path such as a register's `runs/`, each caller naming
which. And it is tested on the token `read-key`'s whole-name reading looks for, before the lookup
(§1). **It is not tested on an `@<path>` that lies below `$SPECS_PATH` in neither of §3's two forms**
(*The path's class*): its names are the operator's own, typed or the working directory's, against
which a relative one is made absolute. Nor on `$SPECS_PATH` itself, which the operator set. The
resolution program prints neither where it is not a printable value, though (§3, *A printable
value*): it refuses such a path wherever it lies (§3, `reason: control`). A key's
glob candidates that do not survive its filter are not tested either: the resolution program reads
them itself, and no command names them (§3, `resolve-key`). The callers that cite this paragraph say which names they test.

## 3. Resolution

### Entry point: `resolve-address <ARG> [<KIND>]`

**The caller-facing entry point.** Every command calls this one. `<KIND>`, when supplied, narrows the
search and refuses a mismatch; a caller that does not yet know the kind must not have to guess, because
the kind is frequently what decides the run's mode.

0. **Where `$SPECS_PATH` is set, run `specs-root-check` (below) first, whichever form `<ARG>` takes.**
   Its `misrooted` is a hard stop; otherwise take the branch `<ARG>` selects.
1. **`<ARG>` begins with `@` → the path branch.** Strip the `@`, and hand what is left to the
   resolution program's `path` mode (below) **before any command names it** — written as one
   single-quoted word, each `'` in it written `'\''`, the one form in which no text the operator typed
   can act. The program holds the path to *The path's class* (below) in both its forms and returns
   `status: misnamed` where it is outside; otherwise it takes a directory as itself and a file as its
   parent directory, reads that folder's `kind:` and `key:` off §4's carrier itself, and the record is
   `form: path`. The program's `path:` is the folder's lexical path, the one later commands name it by.

   **No glob, no tree walk, no ambiguity, and no §5 fallback** — the operator has already answered the
   question resolution exists to ask, and re-deriving an answer they supplied would only introduce a way
   to disagree with them. Past step 0, a path still needs two checks: its class, above, and its kind —
   a `<KIND>` argument that disagrees with the folder's own `kind:` is a stop naming both.

   **A path to a folder with no carrier** — one written before §4's rule, whose artifacts assert no
   `kind:` or `key:` (§5) — returns `kind` and `key` both **empty**: this branch searched for no key
   that could stand in, as §5's does, and none is parsed out of the name. The `<KIND>` check above
   refuses no such folder, since nothing is asserted to disagree. The caller places it by §4.1's
   positive evidence as it would any unprefixed folder, and a caller that needs the key — for an
   artifact's `key:`, a branch, a commit subject or a stop's text — stops, naming the folder and the
   two ways on: give it a carrier (§5), or, where its name is still unprefixed, address it by its
   `<KEY>` instead, which §5's fallback resolves with that key — a prefixed name with no carrier is
   found by no key at all (§5).

2. **Anything else → the key branch.** `read-key <ARG>` (§1); on `invalid` or `needs-tree`, return `status: invalid`, and on `misnamed`, `status: misnamed`.
   Otherwise `resolve-key <key> [<KIND>]`, `<key>` being the key it read, and return `form: key` with
   its `prefix`. A caller that read its address with `read-key` before resolving passes the key it read, so the token is read, and its line printed, once.

**An `@<path>` a caller reads before it resolves.** A caller that tells an `@<path>` address from
another `@` token — by whether its path names an existing directory under `$SPECS_PATH/specifications/`
— or reads its folder's key before it resolves, for its run key set, makes step 1's call first, as
step 1 makes it, before any command names the path: the program's `path` mode, which on `misnamed`
stops the run there with that status's stop (below), no command having named the folder. Its
`directory:` and `tree:` lines say whether the path names an existing directory and whether that
lies under `$SPECS_PATH/specifications/`; its `key:` is the key the folder's carrier asserts, empty
where it has none.

**Every `path` a record carries is in §2's class, each component of it below `$SPECS_PATH`** — save
an `@<path>` that lies below it in neither form (*The path's class*, below). The resolution program
holds every folder to that test before any command names it: the path branch's (step 1), the folder
`read-key`'s whole-name reading matched (§1), and each candidate that survives `resolve-key`'s
filter (its step 1a), every candidate having been read by the program itself, no command naming it.
Where a folder is outside the class the record is `status: misnamed`, and no command has named that
folder or any folder under it. So a command a caller builds from a resolved folder's path — or from
the PRD folder above an Epic, or a slice's `BRD-` folder, each a component of that path — is built
from names in the class, and §2 says why the double quotes it stands in are then safe. **Every value
the program prints is a printable value**, a path it does not test included (*A printable value*,
below).

**The path's class.** A folder's path is in the class where every component of it below
`$SPECS_PATH` is in §2's class. **Two forms of the path are tested, each compared with
`$SPECS_PATH` in the same form.** The **lexical** form is the path made absolute against the
working directory — the logical path the shell keeps for it, in the `PWD` environment value, where
that names the directory the process stands in, else that directory's own path — its `.` and empty components dropped and each `..` taken with the component before it, as
text, no symbolic link resolved: the form a record carries, and the one every command names the
folder by. The **physical** form is the path with every symbolic link resolved. A path lies below
`$SPECS_PATH` in a form where, in that form, it begins with `$SPECS_PATH` and a `/`; in each form
where it does, drop that prefix and split the rest at each `/` — `specifications`, then each folder
below it down to the folder itself, on an Epic's path its PRD folder and on a slice's its `BRD-`
folder among them — and test those components. **The resolution program computes both forms and
tests both itself**, handed the path as one argument, so no shell word ever holds a path it has not
tested, and no command names a folder by its physical form, which can hold a name — the target of a
symbolic link that leads out of `$SPECS_PATH` — that this test never saw. The two forms cover a
`$SPECS_PATH` that is itself a symbolic link, which an `@<path>` may reach by its target's route: that
path lies below it physically, and its components there are tested. The key branch needs no
physical form: the program's candidates are directories and no symbolic link, so below
`specifications/` their two forms are one.

**A caller that holds a path as text and tests it without the program** — a path a scan printed, or
one a file holds — tests its components in one form, lexical, below `$SPECS_PATH`, as text and with
§2's program, in this order. Check each as text for a `'`. Where one holds one, hand the components
before it — none where it is the first, which is then the first outside the class — in order, each as
one single-quoted argument, to §2's program in one call: exit 0 → the
component holding the `'` is the first outside the class; exit 1 → the component at the place it
prints is; any other exit → no component can be shown in the class, and the caller names no `<P>` and
builds no command from any of them. Where none holds a `'`, hand them all to the program in one call,
read the same way. **`<P>`, the components before the first outside the class, is then in the class
whole, every one of them tested**, and only such a `<P>` names a folder in the listing a stop reads
its entry off (*A folder refused by its name*, §2).

**A path below `$SPECS_PATH` in neither form is not tested.** That is an `@<path>` outside
`$SPECS_PATH`: in the layout `specs-repo-git` §3.1 supports, outside the work tree of the
repository `$SPECS_PATH` names, as `/product-workflows:specify`, `/product-workflows:create-ard` and
`/product-workflows:epics` carry such a folder in `prd_outside`; in a specs tree inside a larger
repository — the unsupported layout *specs-root-check* names — anywhere else in that repository too,
though inside its work tree; and anywhere at all while `$SPECS_PATH` is unset, `@.` among them. Its
names are the operator's own: typed, or the working directory's, against which a relative path is
made absolute and which the operator chose — with no `$SPECS_PATH` there is no tree to tell them
from. A folder below `$SPECS_PATH` is tested even where it lies in another repository nested there,
which those three commands carry as `prd_outside` too. **A path below `$SPECS_PATH` in neither form
is still checked before it is printed, though not against the class**: where it, or `$SPECS_PATH`
itself, is not a printable value (below) — it holds a line feed or another control character, or a
bidirectional control, or is not UTF-8 — the program refuses it (`reason: control`, below) rather
than print it, since a line break in a value would end the line it is printed on and begin one a
caller reads as a field of the record, and a bidirectional control would show it as another path.

**`status: misnamed` is a hard stop for every caller that resolves its own address**, issued here as
`ambiguous`'s and `misrooted`'s are: a caller that maps the record's statuses onto outcomes of its own
names `misnamed` as this stop, never as `none` or `absent`. **It covers a folder the program could
not read too** (`reason: unreadable`): a candidate whose files it could not list, or one holding a
file it could not read among those §4 tries before the carrier — either may be the folder the key
names — and, where nothing survives, a directory whose subfolders it could not list, which may hide
it — so an unreadable tree is never taken as `absent`, and a caller that creates the folder it did
not find never makes a second beside one it could not read. **And it covers a path the program will
not print** (`reason: control`, *The resolution program*). **A reader whose resolution
never stops its run takes `misnamed` as it takes `ambiguous`, never as `found`**, and names it in its
own mapping: an emitter's tier, as no match (`workflows-core:feedback-emission`,
`workflows-core:cost-emission`); `workflows-core:pre-lint`, as a hit reported and not fixed;
`/dev-workflows:design`'s *Another design under this PRD answers it*, which asks again; the run key
set of `/workflows-core:prompt`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me`,
which a key resolving to anything but `found` leaves empty; and `product-workflows:coverage-ledger-format`
§6.2's delegated rows, `unresolved`. The stop names the folder by its position and never by its name,
and prints no command built from its path:

`ADDRESS_FOLDER_NAME: <subject> — entry <n> of the checkout's listing of <P>'s folders, at depth <d> below SPECS_PATH (<SPECS_PATH>) — is named outside workflows-core:addressing §2's class of a folder's name (letters, digits and combining marks of any script and . _ @ + -, first a letter, a digit or _, no ..), so this run reads nothing under it and stops. Rename that folder into the class, or move it out of <P>, then re-run.`

**On `reason: unreadable`** the message reads, after the dash, `— could not be read, so this run cannot tell what it holds and stops before reading anything under it. Make it readable, or move it out of <P>, then re-run.`

**On `reason: control`**, which the program prints with no `parent:`, the message is `ADDRESS_FOLDER_NAME: <subject> — its path holds a line feed, another control character or a bidirectional control, or is not UTF-8, so this run prints none of it and stops before reading anything under it. Rename each directory on that path whose name holds such a character or is not UTF-8 — setting SPECS_PATH anew where one is in it — then re-run.`

`<subject>` is the program's `subject:` line. It names the folder the branch looked for — `The
folder the address names` on the path branch, `The folder whose whole name was typed` from
`read-key`'s whole-name reading, `A folder the search for <KEY> matched` from `resolve-key`, `<KEY>`
the key searched for — or, where nothing matched and the folder the stop is about is a directory the
program could not list, `A folder the search for <KEY> had to look inside` (`A folder the search for
the name <TOKEN> had to look inside` from the whole-name reading). **Where that folder, or one above
it on its path, is named outside the class, the stop is about the first such folder, on `reason:
name` whatever the reason was**, and where that is a folder above it, its subject says so: `A folder
above the one the address names`, `A folder above the one whose whole name was typed`, `A folder
above one the search for <KEY> matched`, `A folder above one the search for <KEY> had to look
inside`, or `A folder above one the search for the name <TOKEN> had to look inside`. `<P>` is the
path, relative to `$SPECS_PATH`, of the folders before the one the stop is about — every one of them
in the class, which the program tests before it prints `<P>`, `.` where none comes before it — and
`<d>` that one's place in *The path's class*'s split, `specifications` being 1, `<n>` its place in
§2's listing of `<P>`'s folders (*A folder refused by its name*): the program prints `<P>`, `<n>` and
`<d>`, from one listing of `<P>`, and a caller testing a path as text reads `<n>` off that listing as
text, the name entering no command. Where the program's `entry:` is empty — the folder is gone from that listing, or `<P>` could
not be listed — the stop reads `<subject> — a folder below <P> —` in place of the entry; where it
prints no `parent:` on `reason: unreadable` — an `@<path>` outside `$SPECS_PATH` it could not read —
`<subject> could not be read`.

**Where the program prints no `status:` line, or exits non-zero** — 127 where no `python3` runs, or 1
on a traceback — **nothing is resolved**: the run stops, `ADDRESS_FOLDER_NAME: <subject> could not be resolved — the resolution program, which needs python3, exited <exit> — so this run reads nothing under it and stops. Re-run where python3 runs.`,
and no caller takes that as `absent` or as any other status, a caller that creates the folder it did
not find among them.

### Entry point: `specs-root-check`

**Refuse a `$SPECS_PATH` that points inside the tree.** `resolve-address` runs this as its step 0,
before either branch, so it runs on both address forms. Every folder this file addresses lives under
`$SPECS_PATH/specifications/`. A `$SPECS_PATH` set to `specifications/` itself, to a mount of it, or
to a folder inside it therefore resolves every key `absent`. A caller that creates the folder it did
not find would then create `<that path>/specifications/<KIND>-<KEY>-<slug>/` inside the tree, and
once one has, later runs find folders only in that nested tree.

**Why an `@<path>` is tested too.** A set-but-misrooted variable is a misconfiguration on every run,
whichever form the operator typed. An `@<path>` run that passed Phase 0 untested would meet the same
stop later, at a key resolution taken after its expensive work: `ard-resolution.md`'s, `/release-notes`
Phase 6's, or `/epics` Phase 2.6's. A caller that mapped every status but `found` onto "none" would
instead go on silently without the ARD or specification it should have read.

**What it tests, and where.** It tests only where `$SPECS_PATH` is set. Two signals are tested, (a)
by either of two tests, each against the filesystem and none by parsing a name:

- **(a) `$SPECS_PATH` is, or is inside, the `specifications/` directory.** Either of two tests shows
  it:
  - **`git -C "$SPECS_PATH" rev-parse --show-prefix` prints `specifications/`, or a prefix beginning
    with it**, i.e. it is the `specifications/` directory directly under a git work tree's top level,
    or any directory inside that one, a folder of any name included. **This test runs whether or not
    `$SPECS_PATH/specifications/` exists.** One that does is the damage a run made
    before this check existed, which created its folders at `specifications/specifications/`. A
    precondition that skipped it would keep the plugin reading the nested tree forever, and the
    users it would skip are exactly the ones who already met the misroot.
  - **`[ "$SPECS_PATH/../specifications" -ef "$SPECS_PATH" ]`, where `$SPECS_PATH` is not itself a
    git work tree's top level.** Where `git -C "$SPECS_PATH" rev-parse --show-prefix` succeeds, it
    must print a non-empty prefix. A specs repository cloned into a directory that happens to be
    named `specifications` is a repository root, not a directory inside one, whether or not it holds
    a `specifications/` yet. This test too runs whether or not `$SPECS_PATH/specifications/` exists.
    It catches the same misroot below a directory that is not a repository's top level
    (`<repo>/specs/specifications`), and a `specifications/` directory mounted on its own under that
    name, including one a run already wrote a nested `specifications/` into. Neither has a
    repository prefix for the first test to read.
- **(b) `$SPECS_PATH` is, or directly holds, a specs folder.** Either `$SPECS_PATH` itself has a §4
  carrier, or an immediate subdirectory whose name is not one of §2's reserved subdirectory names has
  one. **A carrier counts only where its directory's name passes §4.1's prefix test**: it begins
  `<KIND>-<key>-`, with `<KIND>` one of §2's three and `<key>` the key read off that carrier.
  **`$SPECS_PATH`'s own name is tested physically** (`cd -P`), so a `$SPECS_PATH` reached through a
  symlink is judged by the folder it reaches, never by the name of the link. **A subdirectory is
  tested by its own name**, and **one whose physical path resolves inside
  `$SPECS_PATH/specifications/` is skipped**. A convenience link at a correct root, such as
  `current -> specifications/PRD-A-1-a`, points into the tree rather than out of it, and must not
  stop every keyed run. The test applies whether or not `$SPECS_PATH/specifications/` exists. Every folder the plugin creates is kind-prefixed (§2), so a
  folder the tree holds passes the test. A carrier that is no specs folder does not: a `templates/`
  or `_templates/` copy of the plugin's own templates, or a `README.md` or `docs/` page carrying
  `key:` and a folder `kind:`. Those never stop a run, at a fresh root or a populated one. A nested
  `specifications/` that a misrooted run already wrote therefore cannot hide this signal. That covers
  a PRD folder an earlier `/idea` wrote `specifications/PRD-…` into, and a `specifications/`
  directory mounted under another name after any run wrote into it. This is the signal for that
  mount, whose parent (a) cannot see, and for a `$SPECS_PATH` pointing at a PRD or Epic folder in the
  tree, with or without keyed folders below it. Reserved subdirectories are skipped because
  `revisions/` holds archived copies of a PRD and `brd/` holds the inventory, and both of those assert
  their parent's key and kind. Stop testing at the first that qualifies; the stray-folder form of the
  stop below finishes the loop and names every subdirectory that qualifies.
  **What neither signal sees, as a class: a `$SPECS_PATH` that is, or holds only, folders not named
  `<KIND>-<key>-`, and that lies outside any work tree's top-level `specifications/`.** Inside a
  repository, (a)'s first test catches every such path by its prefix, a legacy unprefixed folder
  (§5) included. Outside one, a mount of a legacy folder, or of a PRD folder under another name,
  holding no prefixed folder below it, passes unseen. (a)'s second test still catches a mount named
  `specifications`.

A specs repository nothing has been written into yet has no `specifications/` and prints an empty
prefix, so it matches nothing and is never a stop. A `$SPECS_PATH` below its repository's top level
that holds `specifications/` (`<repo>/specs`) prints another prefix and is not stopped here either.
It is the first of the two unsupported layouts below, which `specs-repo-git` §3.1 reports in a
notice, and this check does not try to tell it apart.

**The value to set.** Walk up from `$(cd -P -- "$SPECS_PATH" && pwd)`, starting with that directory
itself and going at most three levels above it (§3's bound). Take the first directory `D` for which
`[ "$D/../specifications" -ef "$D" ]` holds **and** `git -C "$D" rev-parse --show-toplevel` succeeds
and prints the same path as `git -C "$D/.." rev-parse --show-toplevel`. **The value the walk found**
is `$(cd -P -- "$D/.." && pwd)`. Below and in the stop it is always written
`<the value the walk found>`, and `<value>` always means `$SPECS_PATH` as set: the two are different
paths in every case this check stops. **Both halves of the test are required.**
- **`-P`**: a `$SPECS_PATH` reached through a symlink (`H/specs → R/specifications`) resolves `..`
  logically to `H` without it. Setting `SPECS_PATH=H` would then pass this check and send the next
  creating command to `H/specifications/`.
- **The work-tree test**: a `specifications/` directory bind-mounted at `/workspace/specifications`
  has `/workspace` as its parent, which is not a repository. Naming it would send the operator from
  this stop straight to `specs-preflight`'s "not a repository" notice, which is the very symptom
  this check exists to prevent.

The value the walk found is `R` for an ordinary repository, through a symlink too, and for a PRD or
Epic folder inside one. Where `git -C "<the value the walk found>" rev-parse --show-prefix` prints a
non-empty prefix, as it does for `<repo>/specs` when `$SPECS_PATH` is `<repo>/specs/specifications`,
the stop still names it, since that is where `specifications/` sits. It does not present it as a
supported configuration, though: it adds that a specs tree inside a larger repository is
unsupported, so following it ends this stop and draws `specs-repo-git` §3.1's notice instead. Where no
directory on the walk passes, as with a mount of either kind, no path can be established, and the
stop says *the directory that holds `specifications/`* instead.

**Any signal is a hard stop, `status: misrooted`**, issued here as `ambiguous`'s is, so no caller
proceeds past it. A caller that maps the record's statuses onto outcomes of its own names
`misrooted` as a stop, never as `none` or `absent`. **The stop also sets `specs_git: misrooted` for
the whole run**, as `specs-repo-git` §3.3 G0 sets `specs_git: blocked`. A stopped run still runs its
emitter tail (`specs-repo-git` §4), and under that flag every emitter falls to its report-only tier:
cost (`cost-emission` §8), feedback (`feedback-emission` §2), follow-ups (`followup-emission` §2) and
`resume.md` (`session-hygiene` §1). `commit-artifacts` skips with the notice repeated, so the run
writes nothing under `$SPECS_PATH`.

**The stop is one line**, naming the variable, its value, the signal and the value to set, plus the
unsupported-layout clause where it applies. **Where only (b)'s second half fired and the walk found no
value**, that one-line form has nothing true to name, because the folder that fired sits beside `$SPECS_PATH`'s
tree rather than above it. The stop takes one of two other forms instead, chosen in this order. Where
the walk did find a value, `$SPECS_PATH` lies at or below a `specifications/` directory and the form
above is right, whichever signal fired.

- **The stray-folder form**, where `git -C "$SPECS_PATH" rev-parse --show-prefix` succeeds and either
  prints nothing, so `$SPECS_PATH` is a work tree's top level, or `$SPECS_PATH/specifications/` exists.
  The variable names the right directory, and specs folders sit beside `specifications/` rather than
  in it. The stop names no value to set. It finishes (b)'s loop and names every subdirectory that
  qualifies, with `<value>/specifications/` as where they belong, and nothing else, plus the
  unsupported-layout clause where `--show-prefix` is not empty: `<repo>/specs` holding
  `specs/specifications/` and a hand-placed `specs/PRD-S-9-x/` is that case.
- **The two-readings form** everywhere else: where `rev-parse` fails, or where `$SPECS_PATH` is below
  its repository's top level and holds no `specifications/`. Nothing on disk tells the two layouts
  apart. `$SPECS_PATH` may be a specs tree under another name: a `specifications/` directory mounted
  on its own, or a directory in a repository that holds folders the way `specifications/` does. Its
  own nested `specifications/`, where there is one, is then what a misrooted run left. Or it may be a
  specs root whose folders belong in a `specifications/` below it. The stop states both readings and
  what each needs, and the operator chooses. **The first reading always names the `specifications/`
  the folders end up in and sets `$SPECS_PATH` to that directory's parent**, never merely *the
  directory that holds it*: for `R/specs` holding PRD folders directly, that parent is `R`, which
  holds no `specifications/` yet, so every key would come back `absent` and a creating command would
  make `R/specifications/…` unstopped. Where `rev-parse` succeeds, the folders move into a
  `specifications/` beside `$SPECS_PATH` and the value is `$SPECS_PATH`'s parent. Where it fails, the
  path is a mount of some `specifications/` directory, which only the operator can name, and the
  value is that directory's parent, mounted whole. Where `rev-parse`
  fails, the second reading also needs `$SPECS_PATH` made a repository's top level, since
  `specs-repo-git` §3.1 reports a non-repository `$SPECS_PATH` on every run. Where it succeeds, the
  second reading carries the unsupported-layout clause.

**Where a run made while misrooted left anything behind, it adds one more line naming it.** That
covers a nested `$SPECS_PATH/specifications/` and the folders in it, and any of
`$SPECS_PATH/dev-workflows-feedback/`, `$SPECS_PATH/dev-workflows-cost/` and
`$SPECS_PATH/documentation/<slug>/dev-workflows/` that exist. **It is never added in the stray-folder
form**: there `specifications/` and those directories are where they belong. In the two-readings form
it is added under the first reading only, and the line says so, because under the second those
directories are where they belong too.
Each item is named with where it belongs: the nested folders in
`<the value the walk found>/specifications/`, and each bookkeeping directory at the same path under
`<the value the walk found>`. Where the walk found no value, they belong in *the specs repository's
`specifications/`* and at *its top level*.

What each one costs is not the same. `specs-repo-git` §2.1's classifier never stages
`dev-workflows-feedback/` or `dev-workflows-cost/` left at that depth, so G1 fires on every later
run, and a pending cost there never reconciles. **A `documentation/<slug>/dev-workflows/` and a
nested `specifications/` are worse, because part of each is committed in the wrong place.** Seen from
the repository's top level, which is where porcelain prints from, every path under either begins
`specifications/`. Their bookkeeping matches §2.1's `^(specs|specifications|vis)/.+/dev-workflows/`
shape, and an `implementation.md` or another of §2.1's single files in a nested folder matches its
single-file shape, so the classifier takes both for artifacts. **While `$SPECS_PATH` stays
misrooted they are never committed**: `git -C "$SPECS_PATH" add` names a path that does not exist
from there, which fails. **The first run after the variable is fixed commits them, in the wrong
place, unless they are moved first.** A deliverable in a nested folder is OTHER and fires G1 on
every run instead. A nested tree left in place also lies within `resolve-address`'s three-level
search (§3) from the corrected root, so a key whose folder only that tree holds resolves into it.
The line says so for each, and each has to be moved like the rest. **The plugin
moves nothing and gives no commands**: a move has to be right in every state the repository might
be in, and only the operator can see that state:

`SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which <is itself a specifications/ directory | is inside the specifications/ directory | is itself a specs folder, asserting key <key> | holds the specs folder <subdirectory> directly> — every folder lives under $SPECS_PATH/specifications/, so this run would look for and create folders in the wrong place; it wrote nothing under that path, and its cost and feedback are reported here instead. Set SPECS_PATH to <the value the walk found | the directory that holds specifications/> where it is set, and re-run.[ <the value the walk found> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]`
`[stray-folder form: SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, <the top level of its repository | which holds <value>/specifications/>, and holds the specs folder(s) <subdirectory>[, <subdirectory>…] outside <value>/specifications/, where every folder lives. SPECS_PATH names the right directory; move <subdirectory>[, <subdirectory>…] into <value>/specifications/ yourself, commit the move, then re-run — the plugin moves nothing. This run wrote nothing under <value>, and its cost and feedback are reported here instead.[ <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository.]]`
`[two-readings form: SPECS_PATH_INSIDE_TREE: SPECS_PATH is <value>, which holds the specs folder <subdirectory> directly, and nothing on disk says whether <value> is a specs tree under another name or a specs root. If it is a specs tree under another name, its folders belong in a directory named specifications/, and SPECS_PATH names that directory's parent: <move them into <the parent of <value>>/specifications/ yourself, commit the move, and set SPECS_PATH to <the parent of <value>> | set SPECS_PATH to the parent of the specifications/ directory <value> is a mount of, and mount that parent whole rather than the tree alone>, where it is set. If it is a specs root, move <subdirectory> and every other specs folder beside it into <value>/specifications/ yourself and commit the move<, and make <value> the top level of a git repository, which it is not | ; <value> is not the top level of its repository (<that repository's top level>), and a specs tree inside a larger repository is unsupported: this plugin switches branches and commits in that repository>. Then re-run — the plugin moves nothing. This run wrote nothing under that path, and its cost and feedback are reported here instead.]`
`[<in the two-readings form only: If <value> is a specs tree under another name, m|M>isrooted runs left: <value>/specifications/ (<folder>, …), which belongs in <the value the walk found>/specifications/ | the specs repository's specifications/, and which the first run after SPECS_PATH is fixed searches for keys and commits bookkeeping from, in the wrong place, unless it is moved first; <value>/<bookkeeping directory>/, which belongs at <the value the walk found>/<bookkeeping directory>/ | the same path at the specs repository's top level[, which the first run after SPECS_PATH is fixed commits there in the wrong place unless it is moved first]; …. Move them yourself, commit the move, then re-run — the plugin moves nothing.]`

**It offers no option to set the path**, unlike *Required path environment variable unset*'s
*Set <VAR>* (`workflows-core:escalation-rules`). The wrong value lives in the environment, so a per-run override
would leave the next run, and every command that resolves no address, pointed at the same place. A
command that runs `specs-preflight` ahead of resolution (`/idea`) would also already have run it
against the wrong path. No signal holding → the branch `resolve-address` was going to take.

**Two layouts this does not support, each for its own reason.**
- **A specs tree inside a larger repository**: `$SPECS_PATH` below its repository's top level, as
  `<repo>/specs` holding `specs/specifications/` is. **The reason is git.** This plugin switches
  branches and commits in the repository `$SPECS_PATH` belongs to, and in one that also holds
  anything else, that moves the checkout of everything it holds. This check does not stop it;
  `specs-repo-git` §3.1 reports it in a notice and states the rule.
- **A specs root that is itself a subdirectory named `specifications`**: `<repo>/specifications`,
  holding its tree at `<repo>/specifications/specifications/`. **The reason is detection.** It prints
  the prefix `specifications/` and is byte-for-byte the damaged tree that (a)'s first test exists to
  catch, so it stops on every run, with its own `specifications/` or without one.
  `specs-repo-git` §2.1's classifier accepts the shape, but the stop's remedies, setting
  `SPECS_PATH=<repo>` and moving the tree up a level, turn it into the ordinary layout. Being below
  its repository's top level, it is also an instance of the first layout.

`workflows-core:specs-repo-git` §3.1 runs these same signals at run start, exactly as defined here,
sets the same `specs_git: misrooted` flag, and reports them in a notice that never stops the run: one line, plus one more line naming
anything a misrooted run left behind, exactly as the stop's. That notice is how a run that
resolves no address learns the cause.

### Entry point: `resolve-key <KEY> [<KIND>]`

Reached through `resolve-address`, whose step 0 has already run `specs-root-check`. **Run it as the
resolution program's `key` mode (below)**, which makes steps 1 to 5 and §5's fallback itself, reading
every candidate in-process, and prints the record. No command is built from a candidate's name.

1. **Glob `specifications/**/*-<KEY>-*`, bounded at three levels below `specifications/`** —
   directories only, no symbolic link, no hidden directory, and none of §2's reserved subdirectories
   nor anything under them, so a frame set under `design/` or a file whose name merely matches is no
   candidate. Do not
   narrow the glob by `<KIND>`: the folder **prefix** and the asserted **`kind:`** are allowed to
   differ, and on the BRD route they routinely do — `/brd-split` creates a slice as a `PRD-` folder
   whose `brd-link.md` asserts `kind: brd`, so globbing `BRD-<KEY>-*` for `<KIND> = brd` would miss a
   folder that exists, fall through to §5, miss again, and return `absent`. `<KIND>` is applied in
   step 2 instead, against what each candidate asserts.
1a. **The class, on the survivors alone.** Once step 2 and, where it ran, §5's fallback have kept
   their candidates, a survivor whose path holds a component outside §2's class makes the record
   `status: misnamed`, before steps 3 to 5 count anything, and the program names it by its position
   (§3, `ADDRESS_FOLDER_NAME`). A candidate outside the class that does not survive — a folder whose
   key merely extends `<KEY>`, an Epic under its PRD among them — is dropped like any other: the program
   read it, and no command named it. So a folder named outside the class stops the resolution of the
   key it asserts alone — or, where it asserts none, of each key §5's fallback matches its name
   against — and a run on its PRD, or on a sibling, goes on to meet it in a listing that refuses it by
   its position.
2. **Filter the candidates by what each one asserts.** A glob matches *names*, and a name is not an
   assertion. Read each candidate's carrier and keep only those whose own frontmatter says `key: <KEY>` — and,
   where `<KIND>` was supplied, whose `kind:` equals it. This is §4's read, applied as a filter rather
   than only to the winner, and it is the only place `<KIND>` narrows anything. **This step is not optional and it is not
   tidiness**: `*-<KEY>-*` matches every folder whose key merely *extends* `<KEY>`, and a child keyed
   from its parent is the default wherever a command mints one. `/brd-split` proposes "the parent's key plus the next
   unused two-digit segment" and nests the child inside the parent, so on a tree holding
   `BRD-ACME-90-billing-intake/` with children `PRD-ACME-90-01-invoicing/` and
   `PRD-ACME-90-02-dunning/`, the bare glob returns **three** matches for `ACME-90` — and step 4 would
   hard-stop as `ambiguous` on a tree that is entirely correct, making the parent unaddressable by all
   six `/brd-*` commands and `/prd-ground` from the moment its first child exists. Exactly one of those three asserts
   `key: ACME-90`.
3. **Exactly one surviving candidate** → `status: found`.
4. **No surviving candidate** → apply §5's legacy fallback. Still nothing → `status: absent` — save
   where the program could not read a candidate, or could not list a directory that may hide one,
   which is `misnamed` with `reason: unreadable` (§3), never `absent`. The
   caller decides whether that is a stop or a folder to create; this resolver never creates one.
   **A folder that matched the glob but asserts a different key is not a match**, so a legacy parent
   holding a prefixed child no longer returns the child: before the filter, `ACME-90-billing/` with
   `PRD-ACME-90-01-invoicing/` inside it globbed to exactly one match — the child — and returned
   `found` for it silently, with §5's fallback never reached because the prefixed glob had not missed.
5. **More than one surviving candidate** → `status: ambiguous`, a **hard stop naming every match**. Two
   folders *asserting* one key is a defect in the tree, and choosing between them would pick silently —
   the one failure mode a resolver must never have. Name `@<path>` in the stop as the way through it.

### The resolution program

**The one way a run reads the tree for an address.** It lists and reads the folders itself, so no
command is ever built from a folder's name it meets, and prints the record's fields, one `<field>: <value>`
per line, a path only where every component of it below `$SPECS_PATH` is in §2's class, and no value
that is not a printable value (below). Its arguments are `"$SPECS_PATH"` — the variable, expanded by the shell, never its text written in — the mode, and
the mode's one value: a key §1's grammar holds, a token §2's program has passed, or, in `path` mode,
the operator's path, single-quoted with each `'` in it written `'\''`; and `<KIND>` (`brd`, `prd`,
`epic`, or empty) last in `key` mode:

```bash
python3 -I - "$SPECS_PATH" key '<KEY>' '<KIND>' <<'EOF'
import os, re, stat, sys, unicodedata
RESERVED = {b"brd", b"grounding", b"interview", b"dev-workflows", b"design", b"attachments", b"revisions", b"Doc screenshots"}
KEY = re.compile(r"[A-Z][A-Z0-9_]*(-[0-9]+)+")  # §1's grammar
def ok(name):  # §2's class, on a name's bytes read as UTF-8
    try:
        n = name.decode("utf-8")
    except UnicodeError:
        return False
    return n != "" and ".." not in n and (n[0] == "_" or n[0].isalnum()) and all(c.isalnum() or c in "._@+-" or unicodedata.category(c).startswith("M") for c in n)
record, subject = [], b""
def out(*parts):  # one line of the record, which done() prints
    record.append(b"".join(p if isinstance(p, bytes) else p.encode() for p in parts))
BIDI = set("\u061c\u200e\u200f\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069")  # the bidirectional controls
def printable(line):  # a printable value (below): UTF-8, no Cc, no U+2028 or U+2029, no bidirectional control, so it can neither end its line, begin another, nor show its characters out of order
    try:
        return not any(unicodedata.category(c) == "Cc" or c in "\u2028\u2029" or c in BIDI for c in line.decode("utf-8"))
    except UnicodeError:
        return False
def done():  # prints the record, or, where any line of it is not printable, the refusal in its place and nothing of the record
    lines = record if all(printable(line) for line in record) else [b"status: misnamed", b"reason: control", b"subject: " + subject]
    sys.stdout.buffer.write(b"".join(line + b"\n" for line in lines))
    sys.exit(0)
def dirs(folder):  # its directories, no symbolic link, byte-wise order; raises OSError where it cannot be listed
    return sorted(e.name for e in os.scandir(folder) if e.is_dir(follow_symlinks=False))
def reserved(name):
    return name in RESERVED or name.startswith((b"bundle-", b"customer-sent-"))
def frontmatter(path):  # raises OSError where the file is there and cannot be read, a FIFO or other non-regular file among them, opened without waiting on it
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError):
        return {}
    with os.fdopen(fd, "rb") as fh:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError("not a regular file")
        lines = fh.read().decode("utf-8-sig", "replace").split("\n")
    if not lines or lines[0].strip() != "---":
        return {}
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        k, sep, v = line.partition(":")
        if sep and k.strip() in ("key", "kind"):
            fields[k.strip()] = v.strip().strip("\"'")
    return {}
def carrier(folder):  # §4: its first top-level file named in §2's class, byte-wise, asserting a folder kind and a key §1's grammar holds, else brd/brd-inventory.md; raises OSError where the folder cannot be listed, or a file tried before the carrier cannot be read
    files = sorted(e.name for e in os.scandir(folder) if e.is_file(follow_symlinks=False) and ok(e.name))
    for name in files + [os.path.join(b"brd", b"brd-inventory.md")]:
        f = frontmatter(os.path.join(folder, name))
        if f.get("kind") in ("brd", "prd", "epic") and KEY.fullmatch(f.get("key", "")):
            return f["kind"], f["key"]
    return None
def stop(base, rel, subjects, why):  # status: misnamed: the first folder on rel named outside the class, else rel's own, by its position in one listing of <P>, every component of <P> in the class
    if base is None:  # an @<path> below $SPECS_PATH in neither form, which it cannot read: no position
        out("status: misnamed")
        out("reason: ", why)
        out("subject: ", subjects[0])
        return
    comps = rel.split(b"/")
    d = next((i for i, c in enumerate(comps, 1) if not ok(c)), None)
    why, d = ("name", d) if d else (why, len(comps))
    parent = b"/".join(comps[:d - 1])
    try:
        names = dirs(os.path.join(base, parent) if parent else base)
    except OSError:
        names = []
    n = next((i for i, c in enumerate(names, 1) if c == comps[d - 1]), None)
    out("status: misnamed")
    out("reason: ", why)
    out("subject: ", subjects[0] if d == len(comps) else subjects[1])
    out("parent: ", parent if parent else b".")
    out("entry: ", str(n) if n else "")
    out("depth: ", str(d))
def outside(rel):
    return not all(ok(c) for c in rel.split(b"/"))
specs, mode, arg = os.fsencode(sys.argv[1]).rstrip(b"/"), sys.argv[2], os.fsencode(sys.argv[3])
kind = sys.argv[4] if len(sys.argv) > 4 else ""
if mode == "key" and not (KEY.fullmatch(arg.decode("utf-8", "replace")) and kind in ("", "brd", "prd", "epic")) or mode == "name" and not ok(arg):
    out("status: invalid")  # a value the mode does not take: nothing is read
    done()
walk, blind = [], []  # (rel path below $SPECS_PATH, its name, its depth); the directories it could not list
def descend(rel, depth):
    try:
        names = dirs(os.path.join(specs, rel))
    except OSError:
        blind.append(rel)
        return
    for name in names:
        if reserved(name) or name.startswith(b"."):
            continue
        walk.append((rel + b"/" + name, name, depth))
        if depth < 3:
            descend(rel + b"/" + name, depth + 1)
if mode in ("key", "name") and specs and os.path.isdir(os.path.join(specs, b"specifications")):
    descend(b"specifications", 1)
if mode == "key":  # resolve-key: steps 1 to 5, §5's fallback, step 1a on the survivors
    found, unread, legacy = [], [], False
    def keep(rel, missing_ok):
        try:
            c = carrier(os.path.join(specs, rel))
        except OSError:
            unread.append(rel)
            return
        if (c is None and missing_ok) or (c and c[1] == arg.decode() and (not kind or c[0] == kind)):
            found.append((rel, c))
    for rel, name, depth in walk:
        if b"-" + arg + b"-" in name:
            keep(rel, False)
    if not found and not unread:  # §5: the unprefixed form, the top level first, one level inside only where it kept none
        for level in (1, 2):
            for rel, name, depth in walk:
                if depth == level and re.match(re.escape(arg) + rb"[-_]+.", name):
                    keep(rel, True)
            if found or unread:
                legacy = True
                break
    matched = (b"A folder the search for " + arg + b" matched", b"A folder above one the search for " + arg + b" matched")
    subject = matched[0]
    bad = [rel for rel, c in found if outside(rel)]
    if bad:
        stop(specs, bad[0], matched, "name")
    elif unread:
        stop(specs, unread[0], matched, "unreadable")
    elif not found and blind:
        stop(specs, blind[0], (b"A folder the search for " + arg + b" had to look inside", b"A folder above one the search for " + arg + b" had to look inside"), "unreadable")
    elif not found:
        out("status: absent")
    elif len(found) > 1:
        out("status: ambiguous")
        for rel, c in found:
            out("match: ", specs, b"/", rel)
    else:
        rel, c = found[0]
        out("status: found")
        out("path: ", specs, b"/", rel)
        out("kind: ", c[0] if c else "")
        out("key: ", c[1] if c else arg)
        out("legacy: ", "true" if legacy else "false")
elif mode == "name":  # §1's whole-name reading, the token held to §2's class
    hits = [rel for rel, name, depth in walk if name == arg]
    typed = (b"The folder whose whole name was typed", b"A folder above the one whose whole name was typed")
    subject = typed[0]
    if len(hits) > 1:
        out("status: ambiguous")
    elif not hits and blind:
        stop(specs, blind[0], (b"A folder the search for the name " + arg + b" had to look inside", b"A folder above one the search for the name " + arg + b" had to look inside"), "unreadable")
    elif not hits:
        out("status: absent")
    elif outside(hits[0]):
        stop(specs, hits[0], typed, "name")
    else:
        try:
            c = carrier(os.path.join(specs, hits[0]))
        except OSError:
            stop(specs, hits[0], typed, "unreadable")
        else:
            out("status: found")
            out("path: ", specs, b"/", hits[0])
            out("kind: ", c[0] if c else "")
            out("key: ", c[1] if c else "")
elif mode == "path":  # §3 step 1: the path an @<path> names, lexical and physical, tested before anything of it is read
    here = os.environ.get("PWD", "")
    try:
        here = here if os.path.isabs(here) and os.path.samefile(here, ".") else os.getcwd()
    except OSError:
        here = os.getcwd()
    here = os.fsencode(here)
    target = os.path.normpath(os.path.join(here, arg))
    forms = []
    if specs:
        forms.append((os.path.normpath(os.path.join(here, specs)), target))
        forms.append((os.path.realpath(specs), os.path.realpath(target)))
    named = (b"The folder the address names", b"A folder above the one the address names")
    subject = named[0]
    bad = [(base, p[len(base) + 1:]) for base, p in forms if p.startswith(base + b"/") and outside(p[len(base) + 1:])]
    if bad:
        stop(bad[0][0], bad[0][1], named, "name")
    elif not os.path.exists(target):
        out("status: absent")
    else:
        folder = target if os.path.isdir(target) else os.path.dirname(target)
        places = [(base, f[len(base) + 1:]) for (base, _), f in zip(forms, (folder, os.path.realpath(folder))) if f.startswith(base + b"/")]
        try:
            c = carrier(folder)
        except OSError:
            stop(places[0][0] if places else None, places[0][1] if places else b"", named, "unreadable")
        else:
            out("status: found")
            out("path: ", folder)
            out("directory: ", "true" if os.path.isdir(target) else "false")
            out("tree: ", "true" if any(rel.startswith(b"specifications/") for base, rel in places) else "false")
            out("kind: ", c[0] if c else "")
            out("key: ", c[1] if c else "")
done()
EOF
```

- **`key '<KEY>' '<KIND>'`** — `resolve-key`, steps 1 to 5 and §5's fallback. It prints `status:`
  `found`, with `path:`, `kind:`, `key:` and `legacy:`; `ambiguous`, with one `match:` line for each
  survivor; `absent`; `misnamed`, with `reason:` (`name`, `unreadable` or `control`), `subject:`
  and, but on `control`, `parent:` (`<P>`), `entry:` (`<n>`, empty where it could not be read) and
  `depth:` (`<d>`) for `ADDRESS_FOLDER_NAME`; or `invalid`, reading nothing, where `<KEY>` is not a
  key §1's grammar holds or `<KIND>` is not `brd`, `prd`, `epic` or empty.
- **`name '<TOKEN>'`** — §1's whole-name reading: `status: found`, with `path:`, `kind:` and `key:`,
  both empty where the folder has no carrier; `misnamed`, as above; `absent` where no folder has that
  name and none it could not list may hide one; `ambiguous` where more than one has; `invalid`,
  reading nothing, where `<TOKEN>` is outside §2's class.
- **`path '<the path>'`** — §3 step 1, and *An `@<path>` a caller reads before it resolves*: both
  forms of the path tested, then `status: found`, with `path:` (the folder's lexical path),
  `directory:`, `tree:`, `kind:` and `key:`; `misnamed`, as above, `parent:`, `entry:` and `depth:`
  omitted for a path outside `$SPECS_PATH` it could not read; or `absent` where the path names
  nothing.

It reads names as bytes and writes them as UTF-8, whatever the locale. **A printable value** is
UTF-8 and holds no control character — category `Cc`, a line feed and a carriage return among
them — no U+2028 or U+2029, which a reader may take for a line break, and no bidirectional control —
U+061C, U+200E, U+200F, U+202A to U+202E, U+2066 to U+2069 — which would show its characters in
another order than they stand. Every other character passes, the format characters among them: a
zero-width non-joiner or joiner (U+200C, U+200D), which Persian, Arabic-script and Indic names and
emoji hold, is part of a name, not a trick on its reader. This is the one statement of the rule, and
each program of the family that prints a name read back from the tree, where §2's class does not
already hold it, holds the name to it. **It prints the record whole or not at all**: where any line
of it is not a printable value, it prints `status: misnamed`, `reason: control` and `subject:` in its
place, so no value, a path it does not test included, can end its line, begin one a caller reads as
a field, or show as another. It walks
what `key-summary` walks (§1): three levels below `specifications/`, passing over a symbolic link, a
hidden directory and every reserved subdirectory (§2) with everything under it; a directory it cannot
list is the `unreadable` reason above, never an empty one, and so is a folder holding a file it
cannot read among those §4 tries before the carrier, never a folder with no carrier. It reads a
carrier as §4 says — a file named outside §2's class is none, nor is one whose `key:` §1's grammar
does not hold — and takes in `key` mode only a `<KEY>` that grammar holds, so a `key:` it prints is
always a key. A folder whose name matches no form the mode looks for is never read.

### The resolution record

```yaml
status:  found | absent | ambiguous | invalid | misrooted | misnamed   # misrooted: specs-root-check's hard stop; misnamed: a folder's name outside §2's class, a folder unread, or a path not printed (§3)
path:    <absolute path of the resolved folder>   # found only
kind:    brd | prd | epic                         # found only; empty on a folder with no carrier (§5)
key:     <the folder's asserted key>              # found only; read, never parsed (§4) — on a folder with no carrier, the key searched for (§5), or empty on a path to one (§3 step 1)
form:    key | path                               # which form the caller supplied
prefix:  none | BRD | PRD | EPIC                  # form: key only — the kind prefix read-key (§1) read off the token
legacy:  true | false                             # true when §5's fallback resolved it
matches: [ <absolute path>, … ]                   # ambiguous only
```

**A caller whose Phase 0 stops on what this returns, before it has a deliverable, a branch or a handoff, has refused, and still runs its emitter tail** as `workflows-core:specs-repo-git` §4's *A run that refuses before it has written anything* settles it: the cost entry and the terminal commit, and no feedback, follow-ups or `resume.md`. A
live `/dev-workflows:design` that stopped on `invalid` ran none of it, and the next command of the
session was charged its tokens.

**`resolve-key` terminates because the bound is a constant, not a property of the key or of the tree.** Three
levels are scanned, each enumerating a finite set of directories; nothing found on disk can raise
that. So `resolve-key` always answers, and always after a bounded number of scans.

**The key's segment count buys no depth.** The default key `/brd-split` proposes is the parent's key
plus one more numeric segment (`/product-workflows:brd-split` Phase 3), and an operator may supply any key
satisfying §1 instead, including one that adds no segment. Either resolves identically: a segment count
is a naming convention, never a depth declaration, and §1's grammar deliberately fixes no depth.

## 4. The kind and the key are read, never parsed

`resolve-address` returns a folder's `kind` and `key` by **reading frontmatter**, never by splitting the
directory name.

**A directory name is not a safe place to parse from.** `PRD-ACME-90-01-orders` divides into key and
slug only under a rule about where numeric segments stop, and a slug beginning with a numeric segment
falsifies it. More fundamentally, a key re-derived by pattern is a key nothing in the tree ever
asserted — the standing rule `CLAUDE.md` states as *Resolve an identifier against a known set* —
so every match is a guess that a longer or differently-shaped identifier defeats. Reading the field
turns the guess into an assertion.

**Which artifact carries it is not a fixed filename at the folder's top level**, and must not be
written down as one there. The rule is:

> The command that creates a folder writes a keyed artifact into it in the same act, so a folder is
> never keyless — not even between its creation and its first document. (A folder written before
> this rule can be; §5 says what resolving one returns.) A resolver reads `kind:` and
> `key:` off the folder's **carrier**, found in this order:
>
> 1. **The folder's top level.** Take its files whose names are in §2's class, in byte-wise order of
>    name, and the carrier is the first whose frontmatter holds a `key:` that §1's grammar holds and a
>    `kind:` naming a folder kind — `brd`, `prd` or `epic`, §2's three kinds as the resolution record
>    (§3) spells them.
> 2. **Else `brd/brd-inventory.md`.** Where no top-level file qualifies, the carrier is the
>    inventory inside the reserved `brd/` subdirectory — the one file below the top level that is
>    ever read for this.

**A carrier's `key:` is a key, and its file's name is in the class, for every reader.** A file whose
`key:` §1's grammar does not hold is no carrier, as `key-summary` (§1) has always read one, so no
reader hands on as a key text a file holds — a `'`, a `$(` — into a branch name, a `--key` argument
or a commit subject. **A file's name enters a command only where it is in §2's class.** Resolution
reads a carrier with its resolution program (§3), which lists and reads the folder itself and builds
no command from a name, as `key-summary`'s program does (§1), and `specs-git.py`'s `specs-root-check`
reads one in-process too; each passes over a file named outside the class, as the rule above says.
The resolution program takes a file it cannot read, among those the two steps above try before the
carrier, as a folder it cannot read (§3, `reason: unreadable`), never as a folder with no carrier,
since that file may be the carrier; a `brd/brd-inventory.md` that is no regular file, a FIFO say,
counts as one it cannot read, and the program opens it without waiting on it. `key-summary`'s program
opens such a file the same way and reads it as holding no key.
Any other reader that opens a folder's top-level files
with a command — a `head` or a `sed` on `<folder>/<file>` — first checks each name as §2 checks a
folder's: as text for a `'`, then with its program, all of them in one call; on its refusal, exit 1,
the name at the place it prints is outside the class, and the names after it are handed to it again,
until it exits 0. A file whose name is outside the class is passed over unread, and is no carrier
for any reader: every carrier the family writes has a fixed name in the class.

**Why a kind outside the three is passed over.** A document's `kind:` names what that document is —
`ard`, `specification`, `design` — and an idea-route PRD folder holding an `ard.md` would otherwise
resolve as kind `ard`, a value the resolution record (§3) has no place for. **Why byte-wise order.**
"The first artifact" meant nothing until an order was fixed, and a slice shows why it matters: its
`brd-link.md` asserts `kind: brd` and its `prd.md` `kind: prd`, and a resolver that read whichever
it had opened anyway — which this rule used to allow — could return either for one folder. Byte-wise
order puts `brd-link.md` first, which is the reading the family's container refusals already give as
their reason for testing a directory prefix rather than an asserted kind: a slice asserts `brd`.

**Why step 2 exists.** `/brd-intake` creates a root BRD folder whose only artifact naming a folder
kind is the inventory it writes inside `brd/` (`product-workflows:brd-format` §2.1), and no command
writes one at a root's top level, so that inventory is a root's only carrier. The
`coverage-ledger.md` `/brd-intake` writes at the top level carries `key:` beside a `kind:` naming its
own document (`product-workflows:coverage-ledger-format` §2), which step 1 passes over — so step 1
alone finds nothing in that folder, and a strict reading of this rule left every root BRD
unresolvable. It is **one named file, not an enumeration of carriers per kind**: such a list would
go stale the first time a command writes a new artifact, and nothing in `scripts/` would catch it,
while this exception names the single place the family's own reserved subdirectory holds the
folder's identity.

**A reserved subdirectory is otherwise not a candidate for this test.** A frame-set index carries its
*parent's* `key:` while sitting in a directory named for the set (`design/checkout-flow/`), so every
frame-set index in the tree presents an apparent disagreement. Testing it there would tell an operator
their tree is broken on the ordinary `@<path>`-to-a-frame-set gesture, where the right answer is the
consuming command's own redirect (`/frames`'s `FRAMES_NOT_A_SPEC_FOLDER`: re-run against the folder
above). §2's reserved subdirectories are passed over by key resolution and are passed over here too,
save the one file step 2 reads — and step 2 reads it for the folder `brd/` sits in, whose key it
carries, never for `brd/` itself.

**A `key:` that disagrees with its folder name is a hard stop naming both.** That is the whole cost of
carrying identity in two places, and it buys the conversion of a hand-rename from a silent divergence
into a message.

### 4.1 A folder is placed by its prefix — or, where it has none, by positive evidence

**The level a run works at — a BRD container, a PRD folder or an Epic folder — is read off the
folder's kind prefix, never off the `kind:` its carrier asserts.** A BRD-route slice is a `PRD-`
folder whose carrier, `brd-link.md`, asserts `brd` (above), so a level taken from the asserted kind
puts every slice at the one level it is not. A `BRD-` folder is a container, a `PRD-` folder is
PRD-level, and an `EPIC-` folder is Epic-level, its PRD folder being the folder above it.

**A folder is prefixed only where its name begins `<KIND>-<key>-`**, `<KIND>` one of §2's three and
`<key>` the key this section read off its carrier — a test against a key the run already holds, so
nothing is parsed out of the name. A name that merely begins with a kind token is not prefixed: §5's
legacy name starts with the key, and a key may itself begin with a kind token (§2), so
`EPIC-008-01-orders/`, keyed `EPIC-008-01`, is a legacy folder and not an Epic folder — it does not
begin `EPIC-EPIC-008-01-`.

**A folder with no prefix is placed by positive evidence, in this order, and never by the absence of
a file.** It is one §5's fallback resolved (`legacy: true`), or an unprefixed folder an `@<path>`
names, which §3 resolves without the fallback and so without the flag.

1. **A BRD container** where it holds `coverage-ledger.md` or `brd/brd-inventory.md` and no
   `brd-link.md` naming a `parent:` — `product-workflows:coverage-ledger-format` §5.1's test, which
   that section owns and argues. It is taken first, as it is there, so that no evidence of a lower
   level can place a container at one.
2. **Epic-level** where the resolved `kind` is `epic`.
3. **PRD-level** where the resolved `kind` is `prd`, or where a `brd-link.md` names a `parent:` — a
   legacy BRD-route slice, whose carrier asserts `brd`.

A folder none of the three places is never guessed at: the caller stops, naming the folder and what
it carries — and, where what it carries is an `idea.md` and no `prd.md`, naming
`/product-workflows:create-prd <KEY>` too, the run whose `prd.md` places it by rule 3 when the caller
is re-run (on an `@<path>`, which returns no key for such a folder, §3 step 1 says how the operator
supplies it) — save where the folder holds its PRD under its pre-rename file name, which that
command never reads: there the caller prints *The rename* below, and names no run. That command is named by a caller for which it is a way on: one working at the PRD
level, which the placing lets re-run, or a BRD-route command refusing the folder, which names it as
the idea route's next step (`/product-workflows:brd-interview`'s and `/product-workflows:brd-split`'s
`*_EMPTY_INVENTORY` stops for a folder that is neither a slice nor a container and `/product-workflows:prd-ground`'s two no-link stops in its Phase 0 step 6 among them). `/product-workflows:brd-intake` names no command for the folder it refuses, and its
own stop says why. **That stop binds a caller that needs the folder placed, and not every caller does:**
one that refuses only the levels it does not work at tests for those and proceeds on the rest, and
where what it writes asserts `kind: prd` beside the key, that file places the folder from then on.
`/product-workflows:create-prd` and `/product-workflows:idea` are two such callers, each stating its
own test. On a folder with no prefix, `/create-prd` refuses only what rules 1 and 2 place and writes
`prd.md`, and `/idea` refuses only what rules 1 and 2 place or a `brd-link.md` naming a `parent:`
marks as a slice, and writes `idea.md`. A legacy folder holding an `idea.md` and nothing any rule above
reads — where the idea route handed off before the prefixes, an `idea.md` then asserting no `kind:`
or `key:` (§5) — is the ordinary case: it is placed by none of the three until one of them writes
its file into it, and by rule 3 from then on.

**The rename — a folder holding its PRD under its pre-rename file name, and no `prd.md`.** That file
is a top-level `.md` file whose name is the folder's key followed by `_`, other than `<KEY>_ARD.md` —
the test `workflows-core:phase-handoff` §4.4's `prd.md` rung makes. A folder written before the kind
prefixes may hold one, beside an `idea.md` asserting no `kind:` or `key:` or alone (§5); no rule
above places it, since a PRD under that name asserts no `kind:` either, and
`/product-workflows:create-prd` reads `prd.md` alone and would write a second PRD beside it. Such a
folder may hold its ARD under its pre-rename name too, `<KEY>_ARD.md`, which
`/product-workflows:create-ard` reads as no ARD at all and writes a second beside (§5). So the stop
of a caller above — a placement stop, or a BRD-route command's refusal naming `/create-prd` as the
idea route's next step — names no run for such a folder, whether or not it holds an `idea.md`, and
prints the rename itself, `<path>` being the folder's path relative to `$SPECS_PATH`, `<name>` the
PRD file's name, `<SPECS_PATH>` the specs directory, and `<the way on>` what the caller gives as the
way on once the folder holds a `prd.md` — its own re-run, typed out, or, for a refusal, the run it
names after `/create-prd`. **Before it prints a command, it holds `<name>` and each component of
`<path>` below `specifications/` to the class of §2**, each checked for a `'` and handed to §2's
program; the command is printed only where all are in the class (the form below), and otherwise the
rename is said in words alone (*Where a name is outside the class*, below). `<KEY>_ARD.md` needs no
test: `<KEY>` is a key §1's grammar holds.

`<KEY>'s PRD is <path>/<name>, under its file name from before the artifact filenames lost their keys, so nothing places this folder — do not run /product-workflows:create-prd here, which reads prd.md alone and would write a second PRD beside it. Rename that file to prd.md ('git -C "<SPECS_PATH>" mv -- "<path>/<name>" "<path>/prd.md"', or, where git does not track it, 'mv -- "<SPECS_PATH>/<path>/<name>" "<SPECS_PATH>/<path>/prd.md"') and give it the frontmatter fields kind: prd and key: <KEY>, which no file written under the old name carries<the ARD clause>, commit the result — each new file, with the old name's removal where git tracked the old file — and land that commit on the specs repository's default branch (workflows-core:addressing §5); then <the way on>.`

**The ARD clause**, where the folder also holds `<KEY>_ARD.md` and no `ard.md`, and empty otherwise:
`; rename <path>/<KEY>_ARD.md to ard.md in the same change ('git -C "<SPECS_PATH>" mv -- "<path>/<KEY>_ARD.md" "<path>/ard.md"', or, where git does not track it, 'mv -- "<SPECS_PATH>/<path>/<KEY>_ARD.md" "<SPECS_PATH>/<path>/ard.md"') and give it kind: ard and key: <KEY>, or a later /product-workflows:create-ard writes a second ARD beside it`.

**On a specs tree that is no git repository** there is nothing to commit or land, and the second
sentence reads `Rename that file to prd.md ('mv -- "<SPECS_PATH>/<path>/<name>" "<SPECS_PATH>/<path>/prd.md"') and give it the frontmatter fields kind: prd and key: <KEY>, which no file written under the old name carries<the ARD clause>; then <the way on>.`,
its ARD clause naming the `mv` alone.

**Where a name is outside the class**, no command is printed and no name either, since printing it
would hand a person a command built from it: the stop reads `<KEY>'s PRD is a file in this folder whose name begins <KEY>_, under its file name from before the artifact filenames lost their keys, so nothing places this folder — do not run /product-workflows:create-prd here, which reads prd.md alone and would write a second PRD beside it. Rename that file to prd.md and give it the frontmatter fields kind: prd and key: <KEY>[, and <KEY>_ARD.md to ard.md, giving it kind: ard and key: <KEY>,] in one change, committed and landed on the specs repository's default branch where the specs tree is a git repository (workflows-core:addressing §5) — no command is printed for it, since that file's name or its folder's path holds a character outside workflows-core:addressing §2's class; then <the way on>.`,
the bracketed part printed only where the folder holds `<KEY>_ARD.md` and no `ard.md`.

Once renamed and given those fields, `prd.md` places the folder by rule 3. **On an `@<path>` to a
folder with no carrier**, which returns no key (§3 step 1), there is no key to make the test with,
and none is parsed out of a file's name: where the stop names `/create-prd <KEY>`, it follows it
with `— unless the folder holds its PRD as <KEY>_<slug>.md, under its file name from before the artifact filenames lost their keys: then rename that file to prd.md and give it kind: prd and key: <KEY>, and any <KEY>_ARD.md to ard.md with kind: ard and key: <KEY> (workflows-core:addressing §5), and do not run /product-workflows:create-prd, which would write a second PRD beside it.`

**What a caller does at each level is its own, and so is its refusal of a level it does not work
at.** Where a refusal names the slices under a container, it finds them by
`/product-workflows:brd-split` Phase 0 step 9's positive test — each immediate subdirectory carrying
a `brd-link.md` whose `parent:` names the container — and never by a name match. **Each
subdirectory's name is held to §2's class before its `brd-link.md` is read**, and one outside it
that may be a slice (§2, *Whether it may be a slice*) is named by its position, with its remedy, as
§2's *A folder refused by its name* says, `<P>` the container's path, in place of a slice, nothing of
it read; one that may not be is passed over, as a folder holding no `brd-link.md` is.

## 5. The legacy layout

A specs repo written before the kind prefixes existed holds `specifications/<KEY>-<slug>/`, with a BRD
slice, or a per-Epic subfolder, one level inside its parent. `resolve-key` therefore falls back to the **unprefixed** form —
matching `<KEY>{-|_}<slug>/` directly under `specifications/` first and one level inside a folder there
only where the top level kept no candidate, tolerating a human-adjusted slug and a stray extra `-`/`_`
immediately after the key, exactly as the pre-prefix resolution did. The resolution program reads its
candidates at each of those two levels itself, as it reads the glob's, and holds the survivors alone
to §3's *The path's class*, exactly as `resolve-key` step 1a holds the glob's: a survivor outside it
returns `status: misnamed`.

**It matches on the folder name, and §3 step 2's filter drops only a candidate that asserts a
different key.** The pre-prefix resolution read no frontmatter at all — `brd-addressing.md` §2 and
each command's own feature-folder step matched the directory name alone
(`git show 8e2ec7b9^:plugins/dev-workflows/references/brd-addressing.md`) — and the artifacts a
pre-prefix folder holds usually assert nothing: `idea.md` gained `kind:` and `key:` on 2026-09-01
(7c1e19f7), a day after the prefixes (8e2ec7b9), and a PRD still named `<KEY>_<slug>.md`, or a
`brd-link.md` of that time, carries no `key:` either. So a fallback candidate is kept where §4 finds
it a carrier asserting `key: <KEY>` (and, where `<KIND>` was supplied, that kind), **or where §4
finds it no carrier at all**; one whose carrier
asserts another key is dropped, exactly as §3 step 2 drops it. Filtering out a folder that asserts
nothing would make unaddressable every folder this section exists to reach.

**What the record carries for a folder with no carrier.** `key` is the `<KEY>` the caller searched
for — a key the run already holds, which the name match tested the folder against, never one parsed
out of the name — and `kind` is empty. (An `@<path>` to such a folder searched for nothing, so both
are empty there; §3 step 1 says what its caller does.) The caller places the folder by §4.1's positive evidence, never
by a kind nothing asserted, and §4's hard stop on a key that disagrees with its folder name does not
fire, because nothing is asserted to disagree. A `<KIND>` argument refuses no such folder, for the
same reason. Once a command writes a keyed artifact into it — `/product-workflows:create-prd` writing
`prd.md` into a legacy folder holding only an `idea.md` is the ordinary case — that artifact is its
carrier from then on.

**The fallback is reached only after the prefixed glob has already missed**, so a prefixed tree resolves
exactly as it would if this section did not exist. A run that resolves through it sets `legacy: true`
and reports it **once per run** as deprecated. `@<path>` bypasses it along with §3's glob and filter.

**No migration command ships.** A user's specs repo is theirs, it is a git repository they review, and a
renaming script that cannot be tested against their tree is a liability. Renaming a folder is one
`git mv`, and the fallback above means they need never do it — **but a folder with no carrier is
renamed only together with the edit that gives it one**, in the same commit: add `key: <KEY>` and
its folder kind to the artifact §4 will read as its carrier — `prd.md`, or `idea.md` where the folder
holds no `prd.md` (`kind: prd`), `epic.md` (`kind: epic`), a slice's `brd-link.md` or a root's
`brd/brd-inventory.md` (`kind: brd`). Keeping a candidate that asserts nothing is this fallback's
exception alone: renamed without a carrier, the folder is found by §3's glob and dropped by its step
2 filter, which keeps only a folder asserting the key, while this fallback no longer matches its name
— so no key resolves it, and only an `@<path>` reaches it.

**The fallback covers the folder name and nothing inside it, which is a narrowing of what this
paragraph used to claim.** It said the fallback meant a user need never rename, unqualified — and that
covered filenames it never reached. Every command resolves an artifact by its **current** name and none
carries a fallback of its own, so a folder written before the artifact filenames lost their keys still
needs its `<KEY>_<slug>.md` renamed to `prd.md` and its `<KEY>_ARD.md` to `ard.md`. Two more `git mv`s,
and unlike the folder nothing resolves them for you: a command meeting the old filename reads the
artifact as absent, and where that stops it, most stops name a remedy written for a folder that never
had one — the never-produced stops of `/product-workflows:prd-proposal`,
`/product-workflows:create-ard` and `/product-workflows:specify` name the rename instead, and a stop
on a folder §4.1 places at no level prints it (§4.1, *The rename*). **Each
renamed file also takes the `kind:` and `key:` its format now carries** — `kind: prd` and
`key: <KEY>` on `prd.md`, `kind: ard` and the key on `ard.md` — because those fields arrived in the
same commit as the keyless filenames (1da74804), so no file written under the old names carries
them. A `prd.md` asserting no `kind:` is no carrier and no PRD: §4 passes over it, so a folder holding
nothing else keyed is placed by nothing in §4.1, and every command that gates on `prd.md`'s own
`kind: prd` — `/product-workflows:epics`, `/product-workflows:prd-ground`,
`/product-workflows:brd-split` — reads the folder as holding no PRD. **The
unqualified claim was load-bearing in the wrong direction** — a resolver for the legacy artifact names
is derivable from it, and was derived in full, before anyone measured how many trees it would serve.
State the boundary here so the derivation stops at this paragraph.

## 6. Nesting

A PRD folder produced by `/brd-split` is not a sibling of its BRD — it lives **inside** it, and its Epics
live inside it in turn:

```
specifications/BRD-<PARENT-KEY>-<slug>/PRD-<CHILD-KEY>-<slug>/EPIC-<EPIC-KEY>-<eslug>/
```

`resolve-address <CHILD-KEY>` finds the middle folder through §3's glob without the caller ever supplying
the parent key — resolution alone locates a PRD folder from its own key.

**The folder `/brd-split` creates for a slice *is* the folder its PRD is authored in.** A slice exists
precisely to become a PRD, so giving it a directory of its own with a PRD directory nested inside bought a
level of tree for nothing. The merged folder holds the slice's own bookkeeping — `brd-link.md`,
`coverage-ledger.md`, `decisions.md` — beside the documents authored from it, which is what the idea route's
PRD folder already does with `idea.md`.

**Nothing is created below a PRD folder except its Epics** — invariant 2 of §2 says so, and this is the
path it forbids:

```
specifications/BRD-<KEY>-<slug>/PRD-<KEY>-<slug>/PRD-<KEY>-<slug>/     # never created
```

**Why, rather than a second inheritance rule.** A slice inherits `brd/source/` and its **requirement**
defect log from its BRD (`product-workflows:brd-format` §2.1, §4 — the route's separate code-defect log is
slice-owned and inherits nothing). A slice of a slice would have a parent holding neither: its
inventory header would name a `source:` path that does not exist, and a `rejected: [DEF#n]` disposition
taken against it would cite a defect log that is not there. Chasing every inheritance up to the
source-owning root would fix that, but nothing in practice needs it, and one rule beats two. **Every "its
parent's" in this route is therefore literal**: a PRD folder's parent is always a BRD that owns the source
document — which is what makes its one live inheritance, the parent's defect log behind a
`rejected: [DEF#n]`, a single hop.

**The cap is on nesting, never on allocation.** A folder whose ledger could not be walked would keep every
row `unallocated` forever and could never become PRD-eligible
(`product-workflows:coverage-ledger-format` §4, §5) — which would make slicing pointless, since a slice exists
precisely to become a PRD. Refusing a further child, not the walk, is the whole of the cap.

## 7. The shared fallback for existing commands

Every command outside the `/brd-*` family, `/prd-ground` and `/prd-proposal` that addresses a PRD
directory once resolved it as the flat form `specifications/<KEY>-<slug>/`, which on its own cannot see
a nested PRD (`/create-prd` on the BRD route authors into the `PRD-` slice folder one level inside a
BRD). **Every command that addresses a folder now reaches the tree through `resolve-address` (§3)**,
which searches every level §3 bounds and carries §5's fallback — so the fallback is reached by calling
§3, and a caller cites §3 (and §5 for the fallback itself), not this section. One shared rule, defined
here once rather than reinvented per caller.

**Re-derive the set; do not read it off this section.** `grep -l resolve-address plugins/*/commands/*.md`
returns every command that resolves a folder in the specs tree. No total is kept here, deliberately:
this section once carried two — *"twelve files"*, *"eleven commands cite this section"* — and both went
false, the second because no command cites it to reach the fallback (each cites §3; `/brd-split`
cites only its *Adoption is additive* rule) and both because the set grew past the table below
(`/implement`, `/vuln` and `/brd-proposal` resolve through §3 and are in no row of it).

**The table is a finding aid, not the set.** It names the resolving step, and what the resolved
directory is for, for eleven of those commands — all but the five `/brd-*` route commands,
`/prd-ground`, the proposal pair, `/implement` and `/vuln`. For `/frames` the directory is a folder of
any kind whose frame sets it indexes. A command absent from the table is not absent from the fallback.
The eleven rows:

| Command | Step (by name) | What the resolved directory is for |
|---|---|---|
| `/create-prd` | *Feature folder*, Phase 0 — Resolve inputs | the PRD it authors, and its rung-1 `idea.md` |
| `/update-prd` | *Feature folder*, Phase 0 — Resolve inputs | the frozen draft, any ARD, and the spec it grounds on |
| `/create-ard` | *Feature folder*, Phase 0 — Resolve input | the PRD it reads and the ARD it writes |
| `/epics` | *Resolve the PRD dir*, Phase 2.6 — PRD-level spec enrichment (optional) | the optional PRD-level spec |
| `/specify` | *Resolve the feature folder*, Phase 0 — Resolve input | the spec it authors, and each Epic subfolder under it |
| `/design` | *Map onto the specs repo + require the spec on main*, Phase 0 — Resolve input | the merged spec it takes over |
| `/ready` | *Map onto the specs repo (PRD dir + optional Epic subdir)*, Phase 0 — Resolve input | every artifact it judges |
| `/idea` | *Resolve the address*, Phase 0 step 1 | the folder `idea.md` is written into on the first write |
| `/release-notes` | *`run_phase`*, under *Resolve the run's stage*, Phase 0 — Load | the `run_phase` signal |
| `/document` | *Resolve the address*, Phase 0 step 1 | the `specs` files it grounds documentation in |
| `/frames` | *The address (mandatory)*, Phase 0 step 1 | the folder whose `design/*/` frame sets it indexes |

**One shared authority calls it too, and it is not a command:**

- `references/ard-resolution.md`, from step 1 of its *Resolution (most-specific first)*. It is where the
  fallback reaches an **ARD**: `/create-ard`, `/design`, `/implement`, `/specify`, `/epics` and `/ready`
  delegate ARD lookup to it rather than resolving an ARD path themselves, so their own resolution of a
  folder would not have found an ARD in a nested directory. `/implement` in particular reaches an ARD
  solely through it, though it resolves its own positional address with §3 on a keyed run.

**Where a handoff crosses two callers, both must resolve through §3.** `/create-prd` redirects to
`/update-prd` on finding an existing PRD (its *Prior PRD* step), including one found through this
fallback; `/idea` writes `idea.md` into the folder `/create-prd` then reads, resolving it with this
file's §3 on its first write and **never relocating it afterwards** (D7). A redirect, or a first write
into a folder a command with a narrower resolution then has to find again, is a dead-end handoff, which
is why neither was deferred as low-risk.

**Adoption is additive, for every caller.** §5's fallback is reached only where the prefixed glob already
returned nothing, so a key whose folder resolves at the first attempt resolves exactly as it did before
the fallback existed — and where a command creates the folder it did not find, it still creates it
with the §2 prefix: the fallback honors a legacy folder that exists, it never proposes one. The one shared authority creates nothing at all — `ard-resolution.md` is a reader, so for it the additive
claim is simply that a resolvable key returns what it returned before: the same `found` / `none` /
`unmerged`.

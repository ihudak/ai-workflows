#!/usr/bin/env python3
"""Assemble the parts of a split shared reference into committed files, and gate them.

A split reference stays ONE source file under plugins/workflows-core/references/. A
declaration block directly after its H1 line names its parts, and region markers in the
body say which part owns each line:

    <!-- reference-parts
    part core always
    part review needs=finding-triage/re-review
    part maintainer private
    alias review "§ Review gate" "A recorded verdict names the version it was taken against"
    -->

    <!-- part: core -->
    ...
    <!-- /part -->

`part <name> [always] [private] [needs=<part>|<other-ref>/<part>[,...]]`. Exactly one part is
`always`: it comes with every part. A `private` part is covered like any other but generates
no file and is never requestable. `alias <part> "<name>" ...` adds rule-index names that are
not headings. Every non-blank line after the block lies in exactly one region; regions never
nest; a part may own several regions.

The RULE INDEX of a reference is every heading inside a part (its text, `#` marks dropped)
plus every alias, each mapped to its one part. Matching normalises case, strips `*`,
backticks and quotes, collapses whitespace and drops trailing punctuation; two names that
normalise equal in different parts are an error.

`generate` writes plugins/workflows-core/reference-parts/<name>/index.md (the rule index and
the part list) and one <part>.md per non-private part: a header line, a title, a sentence
saying `${CLAUDE_PLUGIN_ROOT}` in it is workflows-core's root, the rule index, then the always
part, the part and the parts of its file it needs (transitively) IN SOURCE ORDER, then each
part of another reference it needs, under a `Bundled from workflows-core:<ref>, part <part>:`
line. It deletes every file under reference-parts/ that no declaration produces.

WHY GENERATED FILES rather than extraction at load time: the agent that most needs a part,
review-fixer, has no Bash, and a skill's allowed-tools grants no tool its caller lacks;
doc-fixer has neither Bash nor the loader and reads its reference by path. A generated file
is one Read for every caller, and the model never assembles the always part itself
(docs/maintainers/rationale.md, "reference-parts").

`check-parts` is the gate on the sources and the tree: declarations, regions, coverage, index
uniqueness, dependency resolution, no relative link in a split source (a generated file sits
one directory deeper, where it would not resolve), and freshness -- it regenerates in memory
and compares byte for byte, so a source edited without `generate` fails, naming the file.
A positional pointer inside a part ("above", "below", "the next section") is printed as
`FLAG <file>:<line>: <word>` and does not fail: whether it crosses a part boundary is a
reading's call, not a pattern's.

`check-citations` gates the callers: the split list in the loader skill equals the declared
set; every consumer file (commands/, agents/, references/ of the dependent plugins,
CHANGELOG.md excluded) that cites a split reference carries the load-by-part preamble as a
paragraph of its own; every explicit part request -- `args: "<split> <part>"`, or a read of
reference-parts/<split>/<part>.md -- names a requestable part or `index`; and every citation
-- in the consumers and in workflows-core's own commands/, agents/ and references/ -- is
PLACED. The unit is one sentence and one cited reference. A name in that sentence (an
italic, bold, backticked or quoted span, or a § reference) that the cited reference's index
holds places it on that part, and names of several parts place it on each of them, since the
preamble has the run load the part that holds each rule. An explicit request places it on
the part requested, and fails where its sentence names a rule that the loads of that
sentence's calls do not hold -- each part with its needs and the always part, or everything
where one of them loads the whole reference: a call converted to the wrong part. A run reads
a sentence whole before it acts, so the calls of one sentence are one load in any order, and
a rule named before its call is held by it; no other sentence's call counts. Where a
PARAGRAPH makes explicit part requests of a reference, its sentences may apply "its" rules
leaning on the paragraph's loads. A sentence citing a split reference is judged as that
citation for the names that reference's index holds; any other name in a sentence of the
paragraph, where a requested reference's index holds it, passes only where a load made AT
OR BEFORE that sentence holds it, never a later one, erring toward failing. Those loads are
the explicit part requests, the explicit whole loads and the parts bare citations are
placed on, of every split reference the paragraph cites whose index holds the name; a bare
citation naming no rule loads nothing there, since the run may read a name the gate cannot
and load only its part. A paragraph making no part request is not read this way: measured
over the live tree, that widening fired only on correct prose. No name places a citation on
the whole reference, which is what the preamble then loads, so it passes and is counted
whole, as does an explicit whole load (`args: "<split>"`). A citation naming a rule held in
a private part fails, explicit or bare, and so does any other sentence naming one in a
paragraph read that way: its text is what no part load brings. A name that matches entries
in two parts fails: every name in an index has one part, so the guard is the index's own
uniqueness error, which fails check-citations, before it reads a citation, as it fails
check-parts. The census `placed N, whole M` is printed per reference, N counting each part
a citation is placed on; `--verbose` lists each whole citation as
`WHOLE <file>:<line>: workflows-core:<split>`.

IT FAILS CLOSED. A scan that finds no declaration fails both subcommands, and a declared
reference no consumer cites fails check-citations: a gate that matched nothing proves
nothing when it passes.

WHAT IT CANNOT SEE: whether a run loads the part when it reaches a citation -- the preamble
tells it to; the rule-by-rule reading and the live runs check that it does. A name the gate
does not read as a span ("rule 6", "the overflow rule") places nothing, so its citation is
counted whole: the census is how such citations are found. Nor does it see which reference
a § number belongs to: in a paragraph read for its other sentences, one pointing into an
unsplit reference is read against every split reference the paragraph cites.

Usage:
    python3 scripts/reference-parts.py [--root DIR] generate
    python3 scripts/reference-parts.py [--root DIR] check-parts
    python3 scripts/reference-parts.py [--root DIR] check-citations [--verbose]
    python3 scripts/reference-parts.py --selftest

`--root` defaults to the repository holding this script. Exit 0 on a pass, 1 on any
problem, 2 on a usage error. `--selftest` runs every case under
scripts/fixtures/reference-parts/ and asserts each one's exit code AND what it must print --
for a red case the message naming the defect and the number of problems, since a fixture red
for some other reason would hold the exit code at 1 just the same.
"""

from __future__ import annotations

import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------- config
# Every name is a plain assignment: nothing a shell exports changes what a run checks.
CORE_PLUGIN_REL = "plugins/workflows-core"
DEPENDENT_PLUGIN_RELS = (
    "plugins/dev-workflows",
    "plugins/product-workflows",
    "plugins/docs-workflows",
    "plugins/security-workflows",
)
LOADER_SKILL_REL = "plugins/workflows-core/skills/reference/SKILL.md"
LOADER_SKILL = "workflows-core:reference"
REF_DIR = "references"
PARTS_DIR = "reference-parts"
SCAN_DIRS = ("commands", "agents", "references")

# Ruling 1's two texts, count-free; {list} is the declared set, alphabetical and backticked.
PREAMBLE = (
    "These shared references load by part — {list}. A citation of one names a rule: before "
    "applying it, load the part that holds it, `Skill(skill: \"{loader}\", args: \"<name> "
    "<part>\")`, the part its rule index names (`args: \"<name> index\"` loads the index; every "
    "part carries it), unless that part is already in this conversation. A citation that "
    "names no rule the index holds loads the whole reference, `args: \"<name>\"`. Never apply "
    "a rule of these references from memory."
)
SKILL_OPENING = "These references load by part: {list}."
SKILL_OPENING_LEAD = "These references load by part:"

CORE_NAME = os.path.basename(CORE_PLUGIN_REL)
SCRIPT_REL = "scripts/reference-parts.py"

# ---------------------------------------------------------------- shared patterns
PART_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DECL_OPEN = re.compile(r"^\s*<!--\s*reference-parts\b")
REGION_OPEN = re.compile(r"^<!-- part: (\S+) -->$")
REGION_CLOSE = re.compile(r"^<!-- /part -->$")
ANY_MARKER = re.compile(r"<!--\s*/?\s*part\b")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*(?:[ \t]#+[ \t]*)?$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
POSITIONAL = re.compile(r"\b(?:above|below)\b|\bthe (?:next|previous) section\b", re.I)
CODE_SPAN = re.compile(r"`([^`\n]*)`")
INLINE_LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*<?([^)\s>]+)")
REF_LINK_DEF = re.compile(r"^\s{0,3}\[(?!\^)[^\]\n]+\]:\s*<?(\S+?)>?(?:\s|$)")
ABSOLUTE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|/|#|\$)")


def norm(name: str) -> str:
    """The rule-index matching form of a name."""
    s = name.replace("*", "").replace("`", "")
    s = re.sub("[\"'“”‘’]", "", s)
    s = re.sub(r"§\s+(?=\d)", "§", s)
    s = " ".join(s.split()).lower()
    return re.sub(r"[\s.,;:!?]+$", "", s)


def listing(names) -> str:
    """`a`, `b`, `c` and `d` -- alphabetical; `a` and `b` for two; `a` for one."""
    q = ["`%s`" % n for n in sorted(names)]
    return q[0] if len(q) == 1 else ", ".join(q[:-1]) + " and " + q[-1]


def collapse(text: str) -> str:
    return " ".join(text.split())


def paragraphs(text: str):
    return [collapse(p) for p in re.split(r"\n[ \t]*\n", text) if p.strip()]


class Fences:
    """Tracks fenced code blocks line by line: a heading or link inside one is not one."""

    def __init__(self):
        self.open = None  # (char, length) of the open fence

    def step(self, line: str) -> bool:
        """Feed one line; True when the line is inside a fence or is a fence line."""
        m = FENCE.match(line)
        if self.open is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                self.open = (m.group(1)[0], len(m.group(1)))
                return True
            return False
        if m and m.group(1)[0] == self.open[0] and len(m.group(1)) >= self.open[1] and not m.group(2).strip():
            self.open = None
        return True


# ---------------------------------------------------------------- the sources
class Part:
    def __init__(self, name, line):
        self.name, self.line = name, line
        self.always = self.private = False
        self.needs = []      # [(ref name or None for this file, part name)]
        self.regions = []    # [(first content line number, [content lines])]
        self.headings = []   # [display text]
        self.aliases = []    # [display text]


class Ref:
    def __init__(self, name, rel):
        self.name, self.rel = name, rel
        self.title = None
        self.parts = {}      # declaration order
        self.errors = []     # declarations, regions, coverage, needs, index
        self.link_errors = []
        self.flags = []
        self.index = {}      # norm -> part, every part (uniqueness)
        self.entries = []    # [(display, part)] for the public index, in index order

    @property
    def always(self):
        return next((p.name for p in self.parts.values() if p.always), None)

    def public(self):
        return [p for p in self.parts.values() if not p.private]

    def err(self, line, msg):
        self.errors.append("%s%s: %s" % (self.rel, ":%d" % line if line else "", msg))


def parse_source(root: Path, path: Path):
    """A Ref for a split source, or None for a reference that is not split."""
    rel = path.relative_to(root).as_posix()
    name = path.relative_to(root / CORE_PLUGIN_REL / REF_DIR).with_suffix("").as_posix()
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(DECL_OPEN.match(l) or ANY_MARKER.search(CODE_SPAN.sub("", l)) for l in lines):
        return None
    ref = Ref(name, rel)
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first is None or not lines[first].startswith("# "):
        ref.err(None, "a split reference opens with its H1 line, and the declaration follows it")
        return ref
    ref.title = lines[first][2:].strip()
    start = next((i for i in range(first + 1, len(lines)) if lines[i].strip()), None)
    if start is None or lines[start].strip() != "<!-- reference-parts":
        ref.err(start + 1 if start is not None else None,
                "the <!-- reference-parts declaration must directly follow the H1 line")
        return ref
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "-->"), None)
    if end is None:
        ref.err(start + 1, "the reference-parts declaration is never closed with -->")
        return ref
    aliases = []
    for i in range(start + 1, end):
        n, words = i + 1, lines[i].split()
        if not words:
            continue
        if words[0] == "part" and len(words) >= 2:
            pname = words[1]
            if not PART_NAME.match(pname) or pname == "index":
                ref.err(n, "'%s' is not a part name -- lowercase letters, digits and dashes, never 'index'" % pname)
                continue
            if pname in ref.parts:
                ref.err(n, "part '%s' is declared twice" % pname)
                continue
            part = Part(pname, n)
            for w in words[2:]:
                if w == "always":
                    part.always = True
                elif w == "private":
                    part.private = True
                elif w.startswith("needs=") and len(w) > 6:
                    for dep in w[6:].split(","):
                        if not dep:
                            continue
                        other, _, dpart = dep.rpartition("/")
                        part.needs.append((other or None, dpart))
                else:
                    ref.err(n, "part '%s': unknown word '%s' -- always, private or needs=" % (pname, w))
            ref.parts[pname] = part
        elif words[0] == "alias" and len(words) >= 3:
            rest = lines[i].split(None, 2)[2]
            names = re.findall(r'"([^"]*)"', rest)
            if not re.fullmatch(r'(\s*"[^"]*")+\s*', rest) or not all(x.strip() for x in names):
                ref.err(n, "an alias line is `alias <part> \"<name>\" ...`, every name quoted and non-empty")
                continue
            aliases.append((n, words[1], names))
        else:
            ref.err(n, "unknown declaration line '%s' -- a line is `part ...` or `alias ...`" % lines[i].strip())
    if any(DECL_OPEN.match(l) for l in lines[end + 1:]):
        ref.err(None, "carries a second reference-parts declaration")
    if ref.errors:
        return ref

    # The body: regions, coverage, headings, links, flags.
    fences, current, gap = Fences(), None, []

    def report_gap():
        if gap:
            more = " (%d more non-blank line(s), to line %d)" % (len(gap) - 1, gap[-1]) if len(gap) > 1 else ""
            ref.err(gap[0], "a non-blank line lies in no part region -- every non-blank line after the "
                            "declaration lies in exactly one%s" % more)
            gap.clear()

    for i in range(end + 1, len(lines)):
        n, line, s = i + 1, lines[i], lines[i].strip()
        mo, mc = REGION_OPEN.match(s), REGION_CLOSE.match(s)
        if mo:
            if current is not None:
                ref.err(n, "region '%s' opens inside region '%s' (opened at line %d) -- regions never nest"
                        % (mo.group(1), current[0].name, current[1]))
                return ref
            if mo.group(1) not in ref.parts:
                ref.err(n, "region '%s' names no declared part" % mo.group(1))
                return ref
            report_gap()
            current = (ref.parts[mo.group(1)], n, [])
            continue
        if mc:
            if current is None:
                ref.err(n, "<!-- /part --> closes no open region")
                return ref
            if fences.open is not None:
                ref.err(n, "region '%s' closes inside a fenced block" % current[0].name)
                return ref
            current[0].regions.append((current[1] + 1, current[2]))
            current = None
            continue
        if ANY_MARKER.search(CODE_SPAN.sub("", line)):
            ref.err(n, "malformed marker -- a region opens with `<!-- part: <name> -->` and closes with "
                       "`<!-- /part -->`, each alone on its line")
            return ref
        fenced = fences.step(line)
        if current is None:
            if s:
                gap.append(n)
            continue
        current[2].append(line)
        if not fenced:
            h = HEADING.match(line)
            if h and h.group(2):
                current[0].headings.append(h.group(2))
            plain = CODE_SPAN.sub("", line)
            targets = INLINE_LINK.findall(plain)
            m = REF_LINK_DEF.match(plain)
            if m:
                targets.append(m.group(1))
            for t in targets:
                if not ABSOLUTE.match(t):
                    ref.link_errors.append("%s:%d: relative link '%s' -- a generated part sits one directory "
                                           "deeper than its source, where it would not resolve" % (rel, n, t))
        if not current[0].private:
            for m in POSITIONAL.finditer(line):
                ref.flags.append("FLAG %s:%d: %s" % (rel, n, m.group(0)))
    if current is not None:
        ref.err(current[1], "region '%s' is never closed" % current[0].name)
        return ref
    report_gap()

    always = [p.name for p in ref.parts.values() if p.always]
    if len(always) != 1:
        ref.err(None, "%d parts are marked always%s -- exactly one part is"
                % (len(always), " (%s)" % ", ".join(always) if always else ""))
    for p in ref.parts.values():
        if p.always and p.private:
            ref.err(p.line, "part '%s' is marked always and private -- the always part comes with every part" % p.name)
        if not p.regions:
            ref.err(p.line, "part '%s' has no region" % p.name)
    for n, pname, names in aliases:
        if pname not in ref.parts:
            ref.err(n, "alias names part '%s', which is not declared" % pname)
        elif ref.parts[pname].private:
            ref.err(n, "alias names part '%s', which is private -- a run never requests it" % pname)
        else:
            ref.parts[pname].aliases.extend(names)
    for p in ref.parts.values():
        for display in p.headings + p.aliases:
            key = norm(display)
            if not key:
                continue
            if key in ref.index and ref.index[key] != p.name:
                ref.err(None, "rule name '%s' is in two parts, %s and %s -- an index name places exactly one"
                        % (key, ref.index[key], p.name))
                continue
            if key not in ref.index:
                ref.index[key] = p.name
                if not p.private:
                    ref.entries.append((display, p.name))
    return ref


def load(root: Path):
    """Every split reference under the core reference dir, keyed by name; and the problems
    that stop a run before it can check anything (vacuity)."""
    base = root / CORE_PLUGIN_REL / REF_DIR
    refs = {}
    for path in sorted(base.rglob("*.md")) if base.is_dir() else []:
        ref = parse_source(root, path)
        if ref is not None:
            refs[ref.name] = ref
    if not refs:
        return refs, ["no file under %s/%s carries a reference-parts declaration -- the scan found nothing "
                      "to check" % (CORE_PLUGIN_REL, REF_DIR)]
    for ref in refs.values():
        if ref.errors:
            continue
        for p in ref.parts.values():
            for other, dep in p.needs:
                label = "%s/%s" % (other, dep) if other else dep
                if other is None or other == ref.name:
                    target = ref
                elif other not in refs:
                    ref.err(p.line, "part '%s' needs '%s', but %s:%s declares no parts" % (p.name, label, CORE_NAME, other))
                    continue
                else:
                    target = refs[other]
                    if target.errors:
                        continue
                if dep not in target.parts:
                    ref.err(p.line, "part '%s' needs '%s', which %s does not declare" % (p.name, label, target.name))
                elif target.parts[dep].private:
                    ref.err(p.line, "part '%s' needs '%s', which is private" % (p.name, label))
    return refs, []


def broken(refs):
    """Names of the references that cannot be assembled: their own errors, or a need that
    reaches a reference with errors."""
    bad = {n for n, r in refs.items() if r.errors}
    changed = True
    while changed:
        changed = False
        for n, r in refs.items():
            if n not in bad and any(o and o in bad for p in r.parts.values() for o, _ in p.needs):
                bad.add(n)
                changed = True
    return bad


# ---------------------------------------------------------------- assembly
def closure(refs, ref, part):
    """{ref name: set of parts} a request for `part` of `ref` loads, and per other reference the
    parts named across a file boundary, in discovery order."""
    included, named, queue = {}, {}, [(ref.name, ref.always), (ref.name, part)]
    while queue:
        r, p = queue.pop(0)
        if p in included.setdefault(r, set()):
            continue
        included[r].add(p)
        if r != ref.name:
            queue.append((r, refs[r].always))
        for other, dep in refs[r].parts[p].needs:
            o = other or r
            if o != r and o != ref.name and dep not in named.setdefault(o, []):
                named[o].append(dep)
            queue.append((o, dep))
    return included, named


def text_of(ref, parts):
    regions = sorted((first, lines) for p in parts for first, lines in ref.parts[p].regions)
    chunks = []
    for _, lines in regions:
        lo, hi = 0, len(lines)
        while lo < hi and not lines[lo].strip():
            lo += 1
        while hi > lo and not lines[hi - 1].strip():
            hi -= 1
        if lo < hi:
            chunks.append("\n".join(lines[lo:hi]))
    return "\n\n".join(chunks)


def header(ref):
    return ("<!-- generated by %s from %s/%s/%s.md — never edit; edit the source and run python3 %s generate -->"
            % (SCRIPT_REL, CORE_PLUGIN_REL, REF_DIR, ref.name, SCRIPT_REL))


def index_block(ref):
    blocks = ["## Rule index of `%s`" % ref.name,
              "Every rule name in `%s`, with the part that holds it; `%s` comes with every part. Load a part with "
              "`Skill(skill: \"%s\", args: \"%s <part>\")`, unless it is already in this conversation."
              % (ref.name, ref.always, LOADER_SKILL, ref.name)]
    if ref.entries:
        blocks.append("\n".join("- %s → `%s`" % (d, p) for d, p in ref.entries))
    return "\n\n".join(blocks)


def expected_tree(refs):
    """{repo-relative path: (text, source path)} of every generated file, for each reference
    that assembles; and the names of those that do not."""
    out, bad = {}, broken(refs)
    for ref in refs.values():
        if ref.name in bad:
            continue
        base = "%s/%s/%s/" % (CORE_PLUGIN_REL, PARTS_DIR, ref.name)
        plist = []
        for p in ref.public():
            notes = (["comes with every part"] if p.always else []) + (
                ["needs " + ", ".join("`%s`" % ("%s/%s" % (o, d) if o else d) for o, d in p.needs)] if p.needs else [])
            plist.append("- `%s`%s" % (p.name, " — " + "; ".join(notes) if notes else ""))
        out[base + "index.md"] = ("\n\n".join(
            [header(ref), "# %s — index" % ref.title, index_block(ref), "## Parts of `%s`" % ref.name,
             "\n".join(plist)]) + "\n", ref.rel)
        for p in ref.public():
            included, named = closure(refs, ref, p.name)
            blocks = [header(ref), "# %s — part %s" % (ref.title, p.name),
                      "`${CLAUDE_PLUGIN_ROOT}` in this file is `%s`'s root, whichever plugin's run reads it." % CORE_NAME,
                      index_block(ref), "---", text_of(ref, included[ref.name])]
            for other in [r for r in included if r != ref.name]:
                parts = named[other]
                which = "part " + parts[0] if len(parts) == 1 else "parts " + ", ".join(parts[:-1]) + " and " + parts[-1]
                blocks += ["---", "Bundled from %s:%s, %s:" % (CORE_NAME, other, which),
                           text_of(refs[other], included[other])]
            out[base + p.name + ".md"] = ("\n\n".join(b for b in blocks if b) + "\n", ref.rel)
    return out, bad


def actual_tree(root):
    base = root / CORE_PLUGIN_REL / PARTS_DIR
    return sorted(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file()) if base.is_dir() else []


def source_problems(refs):
    return [e for r in refs.values() for e in r.errors + r.link_errors]


# ---------------------------------------------------------------- subcommands
def cmd_generate(root, _verbose):
    refs, vacuous = load(root)
    problems = source_problems(refs)
    if problems:
        for p in problems:
            print("ERROR " + p)
        print("reference-parts generate: FAIL -- %d problem(s); nothing written" % len(problems))
        return 1
    if vacuous:
        print("no reference carries a reference-parts declaration; removing every generated file")
    want, _ = expected_tree(refs)
    written = removed = 0
    for rel, (text, _src) in sorted(want.items()):
        path = root / rel
        if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
            print("wrote " + rel)
            written += 1
    for rel in actual_tree(root):
        if rel not in want:
            (root / rel).unlink()
            print("removed " + rel)
            removed += 1
    base = root / CORE_PLUGIN_REL / PARTS_DIR
    if base.is_dir():
        for d in sorted((p for p in base.rglob("*") if p.is_dir()), key=lambda p: -len(p.parts)):
            if not any(d.iterdir()):
                d.rmdir()
    print("reference-parts generate: %d written, %d removed" % (written, removed))
    return 0


def cmd_check_parts(root, _verbose):
    refs, vacuous = load(root)
    problems = vacuous + source_problems(refs)
    want, bad = expected_tree(refs)
    # A reference whose source fails is not judged for freshness: generate refuses to run on
    # it, so its files cannot be repaired until the source is, and every one would be noise.
    bad |= {n for n, r in refs.items() if r.link_errors}
    skip = tuple("%s/%s/%s/" % (CORE_PLUGIN_REL, PARTS_DIR, n) for n in bad)
    want = {rel: v for rel, v in want.items() if not rel.startswith(skip)}
    have = [r for r in actual_tree(root) if not r.startswith(skip)]
    for rel, (text, src) in sorted(want.items()):
        if rel not in have:
            problems.append("%s: missing -- generate builds it from %s; run python3 %s generate" % (rel, src, SCRIPT_REL))
        elif (root / rel).read_bytes() != text.encode("utf-8"):
            problems.append("%s: stale -- differs from what generate builds from %s; run python3 %s generate"
                            % (rel, src, SCRIPT_REL))
    for rel in have:
        if rel not in want:
            problems.append("%s: no declaration produces it -- generate removes it" % rel)
    for p in problems:
        print("ERROR " + p)
    for r in refs.values():
        for f in r.flags:
            print(f)
    if problems:
        print("reference-parts check-parts: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("reference-parts check-parts: PASS -- %d split reference(s), %d generated file(s) fresh"
          % (len(refs), len(want)))
    return 0


# ---------------------------------------------------------------- citations
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_ROW = re.compile(r"^\s*\|")
BLOCKQUOTE = re.compile(r"^\s*>\s?")
ABBREV = re.compile(r"(?:\be\.g|\bi\.e|\betc|\bcf|\bvs|\bviz)\.$", re.I)
BOUNDARY = re.compile(r"[.!?][\"'”’)\]*_`]*\s+(?=[A-Z0-9*`\"“(\[§/])")
SPANS = (re.compile(r"\*{1,2}([^*\n]+?)\*{1,2}"), re.compile(r'"([^"\n]+)"'), re.compile(r"“([^”\n]+)”"))
SECTION_NUM = re.compile(r"§\s*(\d+(?:\.\d+)*)")
SECTION_NAME = re.compile(r"§\s+([A-Za-z][^)(|,;:—–.\n]*)")
TOKEN = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(CORE_NAME) + r":([A-Za-z0-9][A-Za-z0-9_-]*)")
CALL = re.compile(r'"' + re.escape(LOADER_SKILL) + r'"\s*,\s*args:\s*"([^"]*)"')
WHOLE_PATH = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(REF_DIR) + r"/([A-Za-z0-9][A-Za-z0-9_-]*)\.md\b")
PART_PATH = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(PARTS_DIR) + r"/([A-Za-z0-9][A-Za-z0-9_-]*)/([^/\s`)\"]+)\.md\b")


def blocks_of(text):
    """Paragraphs, list items, table rows and headings, each as (joined text, [(offset, line)]);
    a fenced line is a block of its own. A sentence never crosses a block."""
    out, cur, fences = [], None, Fences()

    def flush():
        nonlocal cur
        if cur:
            out.append(cur)
        cur = None

    for n, line in enumerate(text.splitlines(), 1):
        if fences.step(line):
            flush()
            out.append((line, [(0, n)], False))
            continue
        if not line.strip():
            flush()
            continue
        table = bool(TABLE_ROW.match(line))
        starts = table or HEADING.match(line) or LIST_ITEM.match(line)
        body = LIST_ITEM.sub("", BLOCKQUOTE.sub("", line), count=1).strip()
        if starts or cur is None or cur[2]:
            flush()
            cur = (body, [(0, n)], table)
            if HEADING.match(line):
                flush()
        else:
            joined, at, t = cur
            cur = (joined + " " + body, at + [(len(joined) + 1, n)], t)
    flush()
    return out


def line_at(at, offset):
    n = at[0][1]
    for o, ln in at:
        if o <= offset:
            n = ln
    return n


def mask(text):
    return CODE_SPAN.sub(lambda m: " " * len(m.group(0)), text)


def guard(text):
    """The text with every span's inside masked, so no boundary falls within one. Its delimiters
    stay, so a sentence that opens with a span still starts one, and so does a mark that ends a
    sentence inside it (`*Rule.* Next`)."""
    def hide(m):
        a, b = m.start(1) - m.start(0), m.end(1) - m.start(0)
        inner = m.group(1)
        kept = inner[-1] if inner and inner[-1] in ".!?" else ""
        return m.group(0)[:a] + "X" * (len(inner) - len(kept)) + kept + m.group(0)[b:]
    for pat in (CODE_SPAN,) + SPANS:
        text = pat.sub(hide, text)
    return text


def sentences(text, table):
    """[(start, end)] of each sentence; a boundary never falls inside a span."""
    if table:
        cuts = [m.start() for m in re.finditer(r"\|", mask(text))]
    else:
        guarded = guard(text)
        cuts = [m.end() for m in BOUNDARY.finditer(guarded) if not ABBREV.search(guarded[:m.start() + 1])]
    edges = [0] + cuts + [len(text)]
    return [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]


def names_in(sentence):
    """The rule names one sentence may carry -- emphasis, backtick and quote spans, § references
    -- each as a list of readings, of which the first the index holds is the name."""
    found = [[m.group(1)] for m in CODE_SPAN.finditer(sentence)]
    plain = mask(sentence)
    for pat in SPANS:
        found += [[m.group(1)] for m in pat.finditer(plain)]
    found += [["§" + m.group(1)] for m in SECTION_NUM.finditer(plain)]
    for m in SECTION_NAME.finditer(plain):
        # `§ <name>` names a heading, or an alias written with its `§`; the name runs to the
        # next delimiter, and its leading runs of words are read longest first.
        words = m.group(1).split()
        found.append([r for k in range(len(words), 0, -1)
                      for r in (" ".join(words[:k]), "§ " + " ".join(words[:k]))])
    return found


def covers(refs, ref, part):
    return closure(refs, ref, part)[0][ref.name]


def scan_files(root, rels):
    for rel in rels:
        for d in SCAN_DIRS:
            base = root / rel / d
            if base.is_dir():
                for path in sorted(base.rglob("*.md")):
                    if path.name != "CHANGELOG.md":
                        yield path


def cmd_check_citations(root, verbose):
    refs, vacuous = load(root)
    problems = vacuous + [e for r in refs.values() for e in r.errors]
    if problems:
        for p in problems:
            print("ERROR " + p)
        print("reference-parts check-citations: FAIL -- %d problem(s); fix the declarations first" % len(problems))
        return 1
    split = sorted(refs)

    # The loader skill names the declared set.
    skill = root / LOADER_SKILL_REL
    want = SKILL_OPENING.format(list=listing(split))
    if not skill.is_file():
        problems.append("%s: missing -- the loader skill must open a paragraph with \"%s\"" % (LOADER_SKILL_REL, want))
    else:
        paras = paragraphs(skill.read_text(encoding="utf-8"))
        if not any(p.startswith(want) for p in paras):
            said = next((p for p in paras if p.startswith(SKILL_OPENING_LEAD)), None)
            reads = ("it reads \"%s\"" % (said.split(". ")[0].rstrip(".") + ".")) if said else \
                "no paragraph opens with \"%s\"" % SKILL_OPENING_LEAD
            problems.append("%s: no paragraph opens with the split list the declarations give, \"%s\" -- %s"
                            % (LOADER_SKILL_REL, want, reads))

    preamble = PREAMBLE.format(list=listing(split), loader=LOADER_SKILL)
    census = {n: [0, []] for n in split}   # placed, [whole locations]
    consumer_cites = {n: 0 for n in split}
    consumers = set(scan_files(root, DEPENDENT_PLUGIN_RELS))
    for path in sorted(consumers | set(scan_files(root, [CORE_PLUGIN_REL]))):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        cited = set()
        for joined, at, table in blocks_of(text):
            groups = {}   # (sentence, ref) -> one citation: its line, the parts it requests, ...
            spans = sentences(joined, table)

            def group(offset, name):
                s = next(i for i, (a, b) in enumerate(spans) if a <= offset < b)
                return groups.setdefault((s, name), {"line": line_at(at, offset), "parts": [], "bad": 0,
                                                     "whole_call": False})

            def request(offset, name, part):
                g, ref = group(offset, name), refs[name]
                if part == "index" or (part in ref.parts and not ref.parts[part].private):
                    g["parts"].append(part)
                    return
                g["bad"] += 1
                if part in ref.parts:
                    problems.append("%s:%d: requests part '%s' of %s:%s, which is private -- never requestable"
                                    % (rel, line_at(at, offset), part, CORE_NAME, name))
                else:
                    problems.append("%s:%d: requests part '%s' of %s:%s, which has no such part -- requestable: %s"
                                    % (rel, line_at(at, offset), part, CORE_NAME, name,
                                       ", ".join([p.name for p in ref.public()] + ["index"])))

            for m in CALL.finditer(joined):
                toks = m.group(1).split()
                if not toks or toks[0].startswith("<") or toks[0] not in refs:
                    continue
                if len(toks) == 1:
                    group(m.start(), toks[0])["whole_call"] = True
                elif toks[1].startswith("<"):
                    continue
                elif len(toks) > 2:
                    group(m.start(), toks[0])["bad"] += 1
                    problems.append("%s:%d: requests '%s' -- a split reference takes one part token"
                                    % (rel, line_at(at, m.start()), m.group(1)))
                else:
                    request(m.start(), toks[0], toks[1])
            for m in PART_PATH.finditer(joined):
                if m.group(1) in refs and not m.group(2).startswith("<"):
                    request(m.start(), m.group(1), m.group(2))
            for pat in (TOKEN, WHOLE_PATH):
                for m in pat.finditer(joined):
                    if m.group(1) in refs:
                        group(m.start(), m.group(1))

            def read(ref, text_):
                """The parts a stretch of text names rules of: (public parts, private matches)."""
                hits, private = [], []
                for readings in names_in(text_):
                    found = next(((r, ref.index[norm(r)]) for r in readings if norm(r) in ref.index), None)
                    if found is None:
                        continue
                    if ref.parts[found[1]].private:
                        if found not in private:
                            private.append(found)
                    elif found[1] not in hits:
                        hits.append(found[1])
                return hits, private

            def private_fails(private, line, name):
                # A private part is never loaded by part, so a rule a run must apply is never in one.
                for r, p in private:
                    problems.append("%s:%d: names '%s', in private part '%s' of %s:%s -- text no part load brings"
                                    % (rel, line, r.strip(), p, CORE_NAME, name))

            def held_by(ref, parts):
                return set().union(*(covers(refs, ref, p) for p in parts if p != "index"))

            # Each citation is judged on its own sentence. A run reads a sentence whole before it
            # acts, so the calls of one sentence are one load, in any order: an explicit request is
            # judged against the loads of that sentence's calls -- each part with its needs and the
            # always part, or everything where one of them loads the whole reference -- and never
            # against another sentence's. Each citation also records the load the run makes at its
            # sentence, for the sentences after it: `loads[name]` is [(sentence, the parts held, or
            # None for the whole reference, or "index" for a lookup)]. An explicit call is a load
            # whatever its sentence names; a bare citation loads the parts it is placed on. A bare
            # citation the gate reads no name in loads nothing here: the run may read a name the
            # gate cannot and load only that name's part, so counting it whole could hold a later
            # rule the run never loaded.
            loads = {n: [] for (_, n) in groups}
            for (s, name), g in sorted(groups.items(), key=lambda kv: kv[1]["line"]):
                cited.add(name)
                if path in consumers:
                    consumer_cites[name] += 1
                ref, made = refs[name], loads[name]
                held = held_by(ref, g["parts"])
                if g["whole_call"]:
                    made.append((s, None))
                if g["parts"]:
                    made.append((s, held))
                    if "index" in g["parts"]:
                        made.append((s, "index"))
                hits, private = read(ref, joined[spans[s][0]:spans[s][1]])
                if private:
                    private_fails(private, g["line"], name)
                    continue
                if g["parts"]:
                    lacking = [] if g["whole_call"] else [h for h in hits if h not in held]
                    if lacking and "index" not in g["parts"]:
                        # An `index` request is a lookup: the run loads what the index then names.
                        problems.append("%s:%d: requests part %s of %s:%s, but its sentence names a rule of part %s, "
                                        "which that load does not hold"
                                        % (rel, g["line"], ", ".join(g["parts"]), CORE_NAME, name, ", ".join(lacking)))
                    else:
                        census[name][0] += len(set(g["parts"]))
                    continue
                if g["bad"]:
                    continue
                if g["whole_call"] or not hits:
                    census[name][1].append("%s:%d" % (rel, g["line"]))
                    continue
                # A bare citation is placed on the part of each rule its sentence names: the
                # preamble has the run load the part that holds each rule before applying it.
                made.append((s, held_by(ref, hits)))
                census[name][0] += len(hits)

            def holds(name, u, part):
                """Whether a load of `name` made at or before sentence `u` holds `part`."""
                return any(h is None or h == "index" or part in h for s, h in loads[name] if s <= u)

            # Where a paragraph makes explicit part requests of a reference, each of its sentences
            # may apply "its" rule leaning on the paragraph's loads. A name such a sentence carries
            # that its own citation's reference holds was judged above, as that citation. Any other
            # name a requested reference's index holds is read against every split reference the
            # paragraph loads, in any form, whose index holds it, and passes where a load of any of
            # them made AT OR BEFORE the sentence holds it -- never a later one, erring toward
            # failing. A paragraph making no part request is not read this way: measured over the
            # live tree with the four rulebooks trial-split, that widening fired only on correct
            # prose (docs/maintainers/rationale.md, "reference-parts").
            requested = {n for (_, n), g in groups.items() if g["parts"]}
            for u, (a, b) in enumerate(spans if requested else ()):
                own = {n for (i, n) in groups if i == u}
                lacking, private = {}, {}
                for readings in names_in(joined[a:b]):
                    if any(norm(r) in refs[n].index for n in own for r in readings):
                        continue
                    found = [(n, hit) for n in sorted(loads) if n not in own
                             for hit in [next(((r, refs[n].index[norm(r)]) for r in readings
                                               if norm(r) in refs[n].index), None)] if hit]
                    if not any(n in requested for n, _ in found):
                        continue
                    if any(not refs[n].parts[p].private and holds(n, u, p) for n, (r, p) in found):
                        continue
                    for n, (r, p) in found:
                        if refs[n].parts[p].private:
                            private.setdefault(n, []).append((r, p))
                        elif p not in lacking.setdefault(n, []):
                            lacking[n].append(p)
                for n in sorted(set(lacking) | set(private)):
                    if private.get(n):
                        private_fails(private[n], line_at(at, a), n)
                    elif lacking.get(n):
                        problems.append("%s:%d: a sentence citing %s:%s no other way names a rule of part %s, which "
                                        "no load of it at or before that sentence in its paragraph holds"
                                        % (rel, line_at(at, a), CORE_NAME, n, ", ".join(lacking[n])))
        if cited and path in consumers and preamble not in paragraphs(text):
            problems.append("%s: cites %s but does not carry the load-by-part preamble as a paragraph of its own"
                            % (rel, ", ".join("%s:%s" % (CORE_NAME, n) for n in sorted(cited))))

    for n in split:
        if consumer_cites[n] == 0:
            problems.append("%s:%s is declared split, but no file in the dependent plugins' commands/, agents/ or "
                            "references/ cites it -- the scan found nothing" % (CORE_NAME, n))
    for p in problems:
        print("ERROR " + p)
    for n in split:
        placed, whole = census[n]
        print("%s:%s: placed %d, whole %d" % (CORE_NAME, n, placed, len(whole)))
        if verbose:
            for loc in whole:
                print("WHOLE %s: %s:%s" % (loc, CORE_NAME, n))
    if problems:
        print("reference-parts check-citations: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("reference-parts check-citations: PASS -- %d split reference(s)" % len(split))
    return 0


# ---------------------------------------------------------------- selftest
# One fixture tree per case under scripts/fixtures/reference-parts/<case>/, laid out as the repo
# is, and run through the CLI with --root. A step asserts the exit code AND what it must print;
# a red step also counts its ERROR lines, since a fixture red for some other reason would hold
# the exit code at 1 just the same. Each red fixture carries one defect, or one per message it
# asserts. The generated trees in the green fixtures were written by hand from the layout above
# before the generator existed, so freshness there is a test of the generator's output. After a
# deliberate change to that layout, rerun `generate --root scripts/fixtures/reference-parts/<case>`
# on each green fixture and read the diff -- never on stale_generated, which is stale on purpose.
class Step:
    def __init__(self, argv, want_exit, must_print=(), errors=None, flags=None, on_copy=False, post=None, absent=()):
        self.argv, self.want_exit, self.must_print = list(argv), want_exit, list(must_print)
        self.errors, self.flags, self.on_copy, self.post = errors, flags, on_copy, post
        self.absent = list(absent)


def _order(rel, wanted, absent=()):
    """A post-check: the generated file holds every `wanted` string, in that order, and none of
    `absent`."""
    def check(_fixture, root):
        text = (root / rel).read_text(encoding='utf-8')
        at = [text.find(s) for s in wanted]
        if -1 in at:
            return '%s lacks %r' % (rel, wanted[at.index(-1)])
        if at != sorted(at):
            return '%s holds %s out of order' % (rel, wanted)
        for s in absent:
            if s in text:
                return '%s holds %r, which it must not' % (rel, s)
        return None
    return check


def _unchanged(fixture, root):
    """A post-check: the run left the copy byte-identical to its fixture."""
    stack = [filecmp.dircmp(fixture, root)]
    while stack:
        d = stack.pop()
        if d.left_only or d.right_only or d.diff_files:
            return 'generate changed a fresh tree: %s' % (d.left_only + d.right_only + d.diff_files)
        stack.extend(d.subdirs.values())
    return None


A = 'plugins/workflows-core/references/alpha.md'
G = 'plugins/workflows-core/reference-parts'
U = 'plugins/dev-workflows/commands/use.md'
SK = 'plugins/workflows-core/skills/reference/SKILL.md'
CASES = [
    # The cited heading is an italic span wrapped across two lines and the preamble is
    # hard-wrapped, as command files are; pickers holds a fenced `# Resume` line, no heading; and
    # notes.md, which is not split, quotes the marker syntax in code spans.
    ('minimal', 'one always part, one part, one consumer citing it by heading', [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, flags=0),
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 1, whole 0', 'check-citations: PASS'], errors=0),
        Step(['generate'], 0, ['0 written, 0 removed'], errors=0, on_copy=True, post=[_unchanged]),
    ]),
    ('uncovered_line', 'a line outside every region', [
        Step(['check-parts'], 1, [A + ':16: a non-blank line lies in no part region'], errors=1),
    ]),
    ('nested_region', 'a region opened inside another', [
        Step(['check-parts'], 1, [A + ":11: region 'pickers' opens inside region 'core'", 'regions never nest'], errors=1),
    ]),
    # alpha's block misspells `needs=` as `need=` and carries an unknown line; beta's never closes.
    ('malformed_declaration', 'a misspelt need=, an unknown declaration line and an unclosed block', [
        Step(['check-parts'], 1, [A + ":5: part 'pickers': unknown word 'need=beta/detail' -- always, private or needs=",
                                  A + ":6: unknown declaration line 'parts core pickers'",
                                  'plugins/workflows-core/references/beta.md:3: the reference-parts declaration is '
                                  'never closed with -->'], errors=3),
    ]),
    # alpha opens a region with `<!--part: pickers-->`; beta closes one inside a fenced block.
    ('malformed_marker', 'a marker not in the exact form, and a region closed inside a fence', [
        Step(['check-parts'], 1, [A + ':16: malformed marker -- a region opens with `<!-- part: <name> -->`',
                                  "plugins/workflows-core/references/beta.md:12: region 'core' closes inside a "
                                  "fenced block"], errors=2),
    ]),
    ('two_always', 'two parts marked always', [
        Step(['check-parts'], 1, [A + ': 2 parts are marked always (core, pickers) -- exactly one part is'], errors=1),
    ]),
    ('unknown_need', 'a need naming no part, and one naming a reference that is not split', [
        Step(['check-parts'], 1, [A + ":5: part 'pickers' needs 'nosuch', which alpha does not declare",
                                  A + ":5: part 'pickers' needs 'ghost/rule', but workflows-core:ghost declares no parts"],
             errors=2),
    ]),
    # The alias differs from the heading in case, spacing, emphasis and a trailing full stop.
    ('ambiguous_name', 'one rule name, after normalising, in two parts', [
        Step(['check-parts'], 1, [A + ": rule name 'closed-vocabulary pickers' is in two parts, core and pickers"],
             errors=1),
        Step(['check-citations'], 1, [A + ": rule name 'closed-vocabulary pickers' is in two parts, core and pickers",
                                      'fix the declarations first'], errors=1),
    ]),
    # Generated from older pickers text; core.md deleted since; old.md left by a removed part.
    ('stale_generated', 'a stale, a missing and an orphaned generated file; generate repairs all three', [
        Step(['check-parts'], 1, [G + '/alpha/pickers.md: stale -- differs from what generate builds from ' + A,
                                  G + '/alpha/core.md: missing -- generate builds it from ' + A,
                                  G + '/alpha/old.md: no declaration produces it -- generate removes it'], errors=3),
        Step(['generate'], 0, ['2 written, 1 removed'], errors=0, on_copy=True),
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, on_copy=True),
    ]),
    ('relative_link', 'inline and reference-definition relative links, beside links that are not', [
        Step(['check-parts'], 1, [A + ":19: relative link 'vocabulary.md'",
                                  A + ":21: relative link 'vocabulary-list.md'"], errors=2),
    ]),
    ('unknown_part_request', 'a request for no such part, one for a private part and one for two parts', [
        Step(['check-citations'], 1, [U + ":19: requests part 'nosuch' of workflows-core:alpha, which has no such part"
                                          " -- requestable: core, pickers, index",
                                      U + ":21: requests part 'maintainer' of workflows-core:alpha, which is private",
                                      U + ":23: requests 'alpha pickers core' -- a split reference takes one part "
                                          "token"],
             errors=3),
    ]),
    # bare.md carries no preamble; glued.md runs it into the paragraph before; kept.md is right.
    ('missing_preamble_sentence', 'one citing file without the preamble, one with it run into another paragraph', [
        Step(['check-citations'], 1, [
            'plugins/dev-workflows/commands/bare.md: cites workflows-core:alpha but does not carry the load-by-part '
            'preamble as a paragraph of its own',
            'plugins/dev-workflows/commands/glued.md: cites workflows-core:alpha but does not carry the load-by-part '
            'preamble as a paragraph of its own'], errors=2),
    ]),
    ('skill_list_mismatch', "the loader's split list names a reference no declaration splits", [
        Step(['check-citations'], 1, [SK + ': no paragraph opens with the split list the declarations give',
                                      'These references load by part: `alpha` and `beta`.'], errors=1),
    ]),
    ('no_declarations', 'vacuity: no reference carries a declaration', [
        Step(['check-parts'], 1, ['no file under plugins/workflows-core/references carries a reference-parts '
                                  'declaration -- the scan found nothing to check'], errors=1),
        Step(['check-citations'], 1, ['no file under plugins/workflows-core/references carries a reference-parts '
                                      'declaration -- the scan found nothing to check'], errors=1),
    ]),
    ('no_citations', 'vacuity: a declared reference no consumer cites', [
        Step(['check-citations'], 1, ["workflows-core:alpha is declared split, but no file in the dependent plugins' "
                                      "commands/, agents/ or references/ cites it"], errors=1),
    ]),
    # One bare sentence names a pickers rule and a stops rule: the run loads both parts, so the
    # citation is placed on both and the census counts two.
    ('citation_names_two_parts', 'a bare sentence naming rules of two parts is placed on both', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 2, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # Beside the red request (core, naming a pickers rule), one requests pickers and names core's.
    ('request_lacks_named_rule', 'an explicit part request whose own sentence names a rule that part lacks', [
        Step(['check-citations'], 1, [U + ":15: requests part core of workflows-core:alpha, but its sentence names a "
                                          "rule of part pickers, which that load does not hold",
                                      'workflows-core:alpha: placed 1, whole 0'], errors=1),
    ]),
    # A call loading core, then a sentence citing nothing that applies "its" pickers rule: the
    # sentence is red, judged against the core load before it; the call's own sentence holds, so
    # the call is placed. Green beside it: a call loading pickers, and a bare stops citation in a
    # paragraph of its own, which the first paragraph's loads never reach.
    ('request_scope_is_paragraph', 'a sentence citing nothing is judged against the loads before it in its paragraph', [
        Step(['check-citations'], 1, [U + ":15: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 3, whole 0'], errors=1),
    ]),
    # A call loading stops whose own sentence applies a pickers rule, then a call loading pickers.
    ('wrong_call_before_right_call', 'a wrong-part call is not saved by a later right-part call', [
        Step(['check-citations'], 1, [U + ":15: requests part stops of workflows-core:alpha, but its sentence names a "
                                          "rule of part pickers, which that load does not hold"], errors=1),
    ]),
    # The mirror: the right-part call first, then the wrong-part call naming the rule. The rule is
    # in the conversation by then, so the run loses nothing; the call is still the wrong part.
    ('wrong_call_after_right_call', "a call's sentence is judged against that sentence's calls, never an earlier one", [
        Step(['check-citations'], 1, [U + ":15: requests part stops of workflows-core:alpha, but its sentence names a "
                                          "rule of part pickers, which that load does not hold"], errors=1),
    ]),
    # Stops loaded, a citation-free sentence applying a pickers rule, then pickers loaded.
    ('free_sentence_before_right_call', 'a sentence citing nothing is never held by a load after it', [
        Step(['check-citations'], 1, [U + ":15: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds"], errors=1),
    ]),
    # The maintainer part is private; an explicit request and a bare citation each name its heading,
    # the bare one beside a public heading, which must not let the private name drop; and a sentence
    # citing nothing names it after a pickers call.
    ('private_rule_cited',
     'a rule of a private part, named by an explicit citation, a bare one and a sentence citing nothing', [
        Step(['check-citations'], 1, [U + ":15: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings",
                                      U + ":17: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings",
                                      U + ":19: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings"], errors=3),
    ]),
    # An index request whose own sentence names a stops rule, and one followed by a sentence citing
    # nothing that names a pickers rule: the run loads what the index names, so both hold.
    ('index_request_is_a_lookup', 'an index request holds the rules its sentence and the sentences after it name', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 2, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # Two calls in one paragraph, each sentence applying its own part's rule; then two calls
    # followed by a citation-free sentence applying both rules, which only both loads hold.
    ('two_calls_one_paragraph',
     "each call's sentence is held by its own call, and a later sentence by both loads before it", [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 4, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # A call, then a sentence carrying a bare citation of another part's rule.
    ('call_beside_bare_citation', "a sentence with its own citation is judged as that citation, not as the call's", [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 2, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # The pickers rule is named before the parenthetical call that loads it, in one sentence.
    ('rule_named_before_its_call', 'a rule named before its own call in one sentence is held by that call', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 1, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # Two calls, then both their rules, in one sentence; and a whole load beside a part request in
    # one sentence, then a rule of a third part, which only the whole load holds.
    ('two_calls_one_sentence', "the calls of one sentence are one load, held together in any order", [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 3, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # A whole load, then a stops call, then a sentence citing nothing that applies a pickers rule.
    ('whole_load_before_free_sentence', 'an earlier whole load holds a later sentence citing nothing', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 1, whole 1', 'check-citations: PASS'], errors=0),
    ]),
    # A stops call, a bare citation placed on pickers, then a sentence citing nothing that applies
    # the pickers rule: green. Beside it, red: a bare citation that names no rule, which the gate
    # counts as no load, since the run may read a name there the gate cannot and load only its part.
    ('bare_citation_before_free_sentence',
     "a bare citation's parts hold a later sentence; one naming no rule holds none", [
        Step(['check-citations'], 1, [U + ":17: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 3, whole 1'], errors=1),
    ]),
    # A bare stops citation, then a sentence citing nothing that names a pickers rule as a reason,
    # in a paragraph making no part request. Reading such a paragraph was measured over the live
    # tree and fired only on correct prose, so the gate does not read it.
    ('no_request_no_paragraph_read', 'a paragraph making no part request is not read for sentences citing nothing', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 1, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # alpha and beta each hold a rule named Closed-vocabulary pickers, alpha in pickers, beta in
    # detail. Green: alpha's stops and beta's detail loaded, then the name in a sentence citing
    # nothing, which beta's load holds; and the name in a sentence citing beta, which is judged as
    # that citation, never against alpha's loads. Red: alpha's stops and beta's other loaded, then
    # the name, which neither load holds.
    ('name_in_two_references', "a name is held by any loaded reference whose index holds it, and a sentence citing "
                               "one reference is that citation only for that reference's names", [
        Step(['check-citations'], 1, [U + ":19: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      U + ":19: a sentence citing workflows-core:beta no other way names a rule of "
                                          "part detail, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 3, whole 0',
                                      'workflows-core:beta: placed 3, whole 0'], errors=2),
    ]),
    # Italic, bold, backticked, straight- and curly-quoted spans; §N; a § heading; a § alias; a
    # path citation inside workflows-core; a name after "e.g.". A § name reads longest first, so
    # `§ Key dir not found` is never the pickers alias `Key dir`. The three whole citations each
    # follow a sentence that names the rule -- one opening with a span, one ending inside one.
    ('name_forms', 'each form a name takes places its citation, and only within its own sentence', [
        Step(['check-citations', '--verbose'], 0, ['workflows-core:alpha: placed 10, whole 3',
                                                   'WHOLE ' + U + ':33: workflows-core:alpha',
                                                   'WHOLE ' + U + ':35: workflows-core:alpha',
                                                   'WHOLE ' + U + ':37: workflows-core:alpha'], errors=0),
    ]),
    ('renamed_heading_reported', 'a citation of a renamed heading passes as whole, and --verbose names it', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 0, whole 1'], errors=0, absent=['WHOLE ']),
        Step(['check-citations', '--verbose'], 0, ['WHOLE ' + U + ':15: workflows-core:alpha'], errors=0),
    ]),
    ('positional_flagged', '"the next section" inside a part is flagged, never failed', [
        Step(['check-parts'], 0, ['FLAG ' + A + ':19: the next section', 'check-parts: PASS'], errors=0, flags=1),
    ]),
    # review.md carries alpha's text, then beta's always part and detail -- never beta's other.
    ('cross_file_bundle', "a part needing another reference's part carries it after a Bundled from line", [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, post=[
            _order(G + '/alpha/review.md',
                   ['Alpha core: the station rule.', 'Alpha review:', 'Bundled from workflows-core:beta, part detail:',
                    'Beta core: the orchestrator triages.', 'Beta detail:'], absent=['Beta other'])]),
    ]),
    ('source_order', 'a part owning two regions with a needed part between them assembles in source order', [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, post=[
            _order(G + '/alpha/a.md', ['Order one', 'Order two', 'Order three', 'Order four']),
            _order(G + '/alpha/b.md', ['Order one', 'Order three'], absent=['Order two', 'Order four'])]),
    ]),
]


def _run(root, argv):
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--root', str(root)] + argv,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def _selftest() -> int:
    fixtures = Path(__file__).resolve().parent / 'fixtures' / 'reference-parts'
    rc = 0
    for name, desc, steps in CASES:
        fixture = fixtures / name
        why = None
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / name
            shutil.copytree(fixture, copy)
            for step in steps:
                root = copy if step.on_copy else fixture
                got, out = _run(root, step.argv)
                lines = out.splitlines()
                if got != step.want_exit:
                    why = '%s: expected exit %d, got %d\n%s' % (' '.join(step.argv), step.want_exit, got, out)
                    break
                missing = [m for m in step.must_print if m not in out]
                if missing:
                    why = '%s: exit %d was right, but it never printed %s\n%s' % (' '.join(step.argv), got, missing, out)
                    break
                n_err = sum(1 for l in lines if l.startswith('ERROR '))
                if step.errors is not None and n_err != step.errors:
                    why = '%s: expected %d ERROR line(s), got %d\n%s' % (' '.join(step.argv), step.errors, n_err, out)
                    break
                n_flag = sum(1 for l in lines if l.startswith('FLAG '))
                if step.flags is not None and n_flag != step.flags:
                    why = '%s: expected %d FLAG line(s), got %d\n%s' % (' '.join(step.argv), step.flags, n_flag, out)
                    break
                present = [m for m in step.absent if m in out]
                if present:
                    why = '%s: printed %s, which it must not\n%s' % (' '.join(step.argv), present, out)
                    break
                for post in step.post or ():
                    why = why or post(fixture, root)
                if why:
                    break
        if why is None:
            print('ok    %s -- %s' % (name, desc))
        else:
            print('FAIL  %s -- %s: %s' % (name, desc, why))
            rc = 1
    print('SELFTEST PASS' if rc == 0 else 'SELFTEST FAIL')
    return rc


COMMANDS = {"generate": cmd_generate, "check-parts": cmd_check_parts, "check-citations": cmd_check_citations}
USAGE = ("usage: reference-parts.py [--root DIR] generate|check-parts|check-citations [--verbose]\n"
         "       reference-parts.py --selftest")


def main(argv) -> int:
    if argv == ["--selftest"]:
        return _selftest()
    root, verbose, command, rest = Path(__file__).resolve().parent.parent, False, None, list(argv)
    while rest:
        a = rest.pop(0)
        if a == "--root" and rest:
            root = Path(rest.pop(0))
        elif a == "--verbose":
            verbose = True
        elif a in COMMANDS and command is None:
            command = a
        else:
            print(USAGE, file=sys.stderr)
            return 2
    if command is None:
        print(USAGE, file=sys.stderr)
        return 2
    if not root.is_dir():
        print("ERROR --root '%s' is not a directory" % root, file=sys.stderr)
        return 2
    return COMMANDS[command](root.resolve(), verbose)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Assemble the parts of a split shared reference, and the entry-point files of a reference that
is not split, into committed files, and gate them; and gate that every command presenting a choice
list loads the question rules before its first question.

A split reference stays ONE source file under plugins/workflows-core/references/. A
declaration block directly after its H1 line names its parts, and region markers in the
body say which part owns each line:

    # Alpha rules

    <!-- reference-parts
    part core always
    part pickers needs=wording
    part stops
    part wording helper
    part maintainer private
    alias pickers "§1"
    alias stops "§4"
    -->

    <!-- part: core -->
    ...
    <!-- /part -->

`part <name> [always] [private] [helper] [needs=<part>|<other-ref>/<part>[,...]]`. Exactly one
part is `always`: it comes with every part. A `private` part is covered like any other but
generates no file and is never requestable. A `helper` part is covered, generates no file and
is never requestable either, but another part may name it in `needs=`, and its text comes with
every part that brings it, directly or through a part it needs; a helper no requestable part
of its own reference brings, or one marked always or private, is an error. `alias <part>
"<name>" ...` adds rule-index names that are not headings. Every non-blank line after the
block lies in exactly one region; regions never nest; a part may own several regions.

The RULE INDEX of a reference is every heading inside a part (its text, `#` marks dropped)
plus every alias, each mapped to its one part. Matching normalises case, strips `*`,
backticks and quotes, collapses whitespace and drops trailing punctuation; two names that
normalise equal in different parts are an error.

`generate` writes plugins/workflows-core/reference-parts/<name>/index.md (the rule index and
the part list) and one <part>.md per requestable part -- neither private nor a helper. In the
rule index each name is a code span, so one starting with a number renders as itself, and a
rule of a helper names the requestable parts that bring it; the part list names helpers only
as such. Each part file holds a header line, a title, a line under it naming every part the
file holds -- in the example's pickers.md, `This file holds parts `core` and `pickers`, with
helper part `wording`.`: its own reference's requestable parts, then its helpers, then each
other reference's parts it bundles, each in declaration order -- a sentence saying
`${CLAUDE_PLUGIN_ROOT}` in it is workflows-core's root, the rule index, then the always part,
the part and the parts of its file it needs (transitively) IN SOURCE ORDER, then each part of
another reference it needs, under a `Bundled from workflows-core:<ref>, part <part>:` line. It
deletes every file under reference-parts/ that no declaration produces.

WHY GENERATED FILES rather than extraction at load time: the agent that most needs a part,
review-fixer, has no Bash, and a skill's allowed-tools grants no tool its caller lacks;
doc-fixer has neither Bash nor the loader and reads its reference by path. A generated file
is one Read for every caller, and the model never assembles the always part itself
(docs/maintainers/rationale.md, "reference-parts").

AN ENTRY-POINT FILE is a second, narrower mechanism, for a reference that does NOT load by part:
one entry point gets a generated file holding that entry point and the sections it needs. It
has no rule index and no citation placement: every other request means the whole file, and so does
every citation but one of a section the file holds, which the loader serves from the file -- from its
text wherever a read of it, or of the whole reference, made in the run is in the conversation, and
otherwise by reading it inside a `##` section that requests the entry point and the whole reference
anywhere else (OUT-OF-FILE CITATIONS, below). A declaration
block directly after the H1 line names each such entry
point, and region markers select the lines its file holds:

    # Gamma steps

    <!-- reference-entry-files
    entry check-it holds=1,3
    partial check-it 4.0 "never infer"
    -->

    <!-- entry: check-it -->
    ...
    <!-- /entry -->

`entry <entry> holds=<§>[,<§>...]` names an entry point -- the first word of a code span in one
of the reference's headings outside a fenced block, as the loader reads one -- and the sections
its file holds whole. A § is the number a heading opens with (`## 3. ...`, `### 3.1 ...`), and
it covers its subsections: `3` covers `3.1` to `3.7`, and the section runs to the next heading
that is neither numbered under it nor an unnumbered one deeper than its own. `partial <entry>
<§> "<phrase>" ...` names a section the file holds in part, with phrases that identify the held
text. A section held whole is declared once, its subsections with it: no other § of its entry,
held whole or in part, is it or lies under it, and no § held in part has it under it; one § held
in part under another is allowed. Regions never nest and never close inside a fenced block, and
the markers take the `part` regions' exact form with `entry` for `part`, save that an entry region
may name several entries, space-separated, each once -- `<!-- entry: check-it make-it -->` -- and its
lines are then in each one's file: two entry points that need one section share its region. A line
outside every region belongs to no entry file: unlike a split reference, a line needs no region. A region line
inside a numbered section lies inside one its entry holds whole or in part, so the line under
the file's title names every section the file holds text of; a line before the first numbered
heading is in no section and free. `generate` writes
plugins/workflows-core/reference-parts/<ref>/<entry>.md for each entry point: the header line
and the `${CLAUDE_PLUGIN_ROOT}` sentence a part file carries; the title `# <H1> — entry point
<entry>`; under it the line `This file holds entry point `check-it` of `gamma`: §1 and §3, and
in part §4.0 ("never infer"). Any other section is in the whole reference: `Skill(skill:
"workflows-core:reference", args: "gamma")`. This file is <N> lines long.` -- each list in
source order, phrases as declared, <N> the generated file's own line count, so a run reading it in
ranges knows where it ends; then the regions' text in source order. check-parts' byte-for-byte
freshness compare covers the count. Its deletion of every file no declaration
produces counts these files as produced.

`check-parts` is the gate on the sources and the tree: declarations, regions, coverage, index
uniqueness, dependency resolution, no relative link in a split source (a generated file sits
one directory deeper, where it would not resolve), and freshness -- it regenerates in memory
and compares byte for byte, so a source edited without `generate` fails, naming the file.
A positional pointer inside a part ("above", "below", "the next section") is printed as
`FLAG <file>:<line>: <word>` and does not fail: whether it crosses a part boundary is a
reading's call, not a pattern's. A positional pointer inside an entry region prints the same
FLAG line and does not fail either, since an entry-point file too holds only some of its
reference's text. On an entry-point declaration it fails on a block out of place, unclosed or
carried twice, a malformed line or marker, an entry declared twice, a partial line naming an
undeclared entry, a section held whole declared beside one it is, lies under or has under it, a
nested region, one closed inside a fenced block, one naming no declared entry or one naming an entry
twice; on an entry
that is no entry point of its reference; on a § no heading opens with; on a non-blank line of a
section held whole that lies in no region of its entry; on a region line inside a numbered
section its entry neither holds whole nor holds in part; on a phrase of a section held in part
that no region text of its entry inside that section holds, phrase and text each normalised as
the rule index normalises names -- and on a phrase naming a numbered rule, `rule <N>`, where no
region line of its entry inside that section opens the rule's own list item, `N.`, since the
section's opening line may mention the rule while the rule itself lies outside every region; and
on an entry-point file that is stale, missing or produced
by no declaration. Its PASS line counts the split references, the entry-point files and every
generated file.

`check-citations` gates the callers: the split list in the loader skill equals the declared
set; where any entry point is declared, a paragraph of the loader skill opens with `These entry
points read their own file: `<ref> <entry>`, ...`, the declared pairs alphabetical, as the split
list is, and carries two sentences word for word: ENTRY_PATH, giving each file's path, which the
entry-point rules do not repeat, and ENTRY_TRIGGER, which has a request on such a reference read
the loader's entry-point rules, `${CLAUDE_PLUGIN_ROOT}/skills/reference/entry-files.md`
(ENTRY_RULES_REL), with or before its other reads -- the one sentence that puts them in front of
the run; for each pair a sentence of those rules reads `The file for `<ref> <entry>` holds
<held>.`, <held> being the generated file's own list led by `the text before §<n>` where a region
of the entry holds text before its reference's first numbered heading, §<n> -- the loader serves a
citation of a held section from that file, so the list it names is the declaration's, neither more
nor less -- and no paragraph of the loader skill holds such a sentence: its body comes with every
request, so the list is in the rules alone; an entry-point declaration check-parts fails stops it
before it reads a citation, as a split declaration does; every consumer file (commands/, agents/,
references/ of the dependent plugins,
CHANGELOG.md excluded) that cites a split reference carries the load-by-part preamble as a
paragraph of its own; every explicit part request -- `args: "<split> <part>"`, or, in
workflows-core's own files, a read of reference-parts/<split>/<part>.md -- names a requestable
part or `index`, never a helper; a consumer file that reads a reference-parts/<ref>/<part>.md
path fails, the failure naming the loader call to make instead, since `${CLAUDE_PLUGIN_ROOT}`
there is its own plugin's root, which holds no reference-parts/; every
entry-point request -- `args: "<ref> <token>"` on a reference that does not load by part, the
token no `<placeholder>` -- names an entry point of it, the first word of a code span in one of
its headings outside a fenced block, since the loader stops the run on any other token (a first
token naming no reference file is check 16's, in scripts/check-docs.sh), and the census
`entry-point requests ...: N, M distinct` is printed; and every citation -- in the consumers and
in workflows-core's own commands/, agents/ and references/ -- is PLACED. The unit is one
sentence and one cited reference. A name in that
sentence that the cited reference's index holds places it on that part, and names of several
parts place it on each of them, since the preamble has the run load the part that holds each
rule. A name is an italic, bold, backticked or quoted span, read with any code span inside it,
or a § reference that belongs to the citation; a possessive `§ <Name>'s` is read as the
section `<Name>`. A § reference belongs to a reference citation, split or not -- a
`<plugin>:<name>` token naming a reference file of that plugin the tree holds, a loader call,
a call of a skill SKILL_REFERENCES ties to the one reference it loads, or a path: the one a
`§N of <citation>` phrase names, with nothing between the number and "of", or a `§ <Name> of
<citation>` phrase where <Name> is a section of that reference -- in its index if split, else
a heading of its file; else the nearest before it in its sentence; else the first after it
there; else, in a sentence citing nothing, the nearest in an earlier sentence of its
paragraph; else none, and it names nothing. An explicit request places it on the part
requested, and fails where its sentence names a rule that the loads of that sentence's calls
do not hold -- each part with its needs and the always part, or everything where one of them
loads the whole reference: a call converted to the wrong part. A failure naming a rule a
helper holds names the parts that bring it, as the index does. An `index` request is a lookup,
so its sentence passes whatever public rule it names: the run loads what the index names. A
run reads a sentence whole before it acts, so the calls of one sentence are one load in any
order, and a rule named before its call is held by it; no other sentence's call counts. Where
a PARAGRAPH cites a split reference, in any form, its sentences may apply "its" rules leaning
on the paragraph's loads. A sentence citing a split reference is judged as that citation for
the names that reference's index holds; any other name in a sentence of the paragraph, where
a cited split reference's index holds it, passes only where a load made AT OR BEFORE that
sentence holds it, never a later one, erring toward failing. Those loads are the explicit part
requests, the explicit whole loads and the parts bare citations are placed on, of every split
reference the paragraph cites whose index holds the name, and a bare citation naming no rule
loads the whole reference, which is where the preamble sends it (`args: "<split>"`); an `index`
load holds every later sentence, as the lookup it is. A § reference in a sentence citing
nothing is read against the loads of the reference it belongs to alone. A paragraph making no
part request is read this way too: that reading was first refused as firing only on correct
prose, and re-measured on the tree before the rule-by-rule reading four of its six hits were
gaps that reading found, so it is on. No
name places a citation on the whole reference, which is what the preamble then loads, so it
passes and is counted whole, as does an explicit whole load (`args: "<split>"`). A citation
naming a rule held in a private part fails, explicit or bare, and so does any other sentence
naming one in a paragraph read that way: its text is what no part load brings. A name that
matches entries in two parts fails: every name in an index has one part, so the guard is the
index's own uniqueness error, which fails check-citations, before it reads a citation, as it
fails check-parts. The census `placed N, whole M` is printed per reference, N counting each
part a citation is placed on; `--verbose` lists each whole citation as
`WHOLE <file>:<line>: workflows-core:<split>`.

OUT-OF-FILE CITATIONS. Where an entry point is declared, check-citations holds the files it scans to
what the loader serves from that entry point's file. The unit is a `##` section -- from a `##` heading
outside a fenced block to the next heading of level 1 or 2 -- whose text requests a declared entry
point, `args: "<ref> <entry>"`. There the loader serves a citation of a section the file holds from
the file, before the request or after it, and reads the whole reference for any other; so each
sentence of that section citing <ref> -- a `workflows-core:<ref>` token, a loader call or a path -- or
carrying a § reference that belongs to a citation of <ref>, by the rule above, is judged by its own
numbered § references of <ref>. Each passes where it lies under a § the entry holds whole, or is a §
held in part and the sentence holds one of that section's phrases, each normalised as a rule name is;
any other fails, `ERROR <file>:<line>: cites workflows-core:<ref> §<n>, which the <entry> file does not
hold, in a section that reads only that file -- ...`. A sentence citing <ref> by no § reference of it,
with no request of the entry point among its calls, cites no section and fails the same way, `with no
section` for `§<n>`. A whole load of <ref> at or before the sentence in its section holds every §:
`args: "<ref>"`, or a request of an entry point that has no file of its own, which the loader answers
with the whole reference -- a sentence's calls are one load in any order, and a load after the sentence
holds nothing. Before the first `##` section requesting an entry point in its file, a sentence citing
<ref> by a token, a path or a call other than that request fails whatever § it names, unless its own
calls load the whole reference: a run loads the whole reference there, ahead of the request, and the
file then saves nothing. A § reference in a sentence citing nothing is not read there, since the
citation it leans on is. After the first section requesting an entry point, the file's text is in the
conversation, so the loader serves a citation of a section it holds there from that text, as a lookup,
and reads the whole reference for any other: so, outside every section requesting it and until the
file's first whole load of <ref> -- the first sentence whose calls load it whole, by the forms above --
each sentence citing <ref> is judged as one inside a requesting section is, against every entry point
the file has already requested, and fails `ERROR <file>:<line>: cites workflows-core:<ref> §<n>, which
the <entry> file does not hold, after the first `##` section requesting `<ref> <entry>` and before any
load of the whole reference in this file, so a run loads the whole reference here -- ...`, or `with no
section`, where it cites a section the file does not hold or none; that first whole load's own sentence
passes, and every sentence after it is not read, since the whole reference is in the conversation
from then on. Whole loads are counted from calls alone: a citation that loads the whole reference is
the failure this reports, never a load that excuses the citations after it. The census `entry-point
file <ref> <entry>: N request section(s), M citation(s) checked` counts the sections requesting each
entry point and every sentence judged for it, a request's own included. A tree declaring no entry
point runs none of this; a declared entry point that no section requests fails (IT FAILS CLOSED).

THE QUESTION RULES. `check-questions` gates the step that loads `escalation-rules core` -- §0's
array shape, choice lists presented verbatim, the `(Recommended)` marker, a selection that carries no
text -- which every question a run asks follows. It is a subcommand of its own, not part of
check-citations, because its subject is a command's questions, not a reference's declaration: its
fail-closed rule would fail every tree that declares references and asks nothing, as check-citations'
fixture trees do. It reads every markdown file under `commands/`
of workflows-core and of every dependent plugin (QUESTION_PLUGIN_RELS) for each one's FIRST QUESTION:
the first line, fenced or not, holding `choices:`; holding both `phase-handoff` and `§4.3` -- the
consent array that reference's §4.3 has a command present, as /frames does with no `choices:` of its
own; or stating a prompt of 2–4 options the command builds at run time, `2–4 options` (or `2-4`)
on a line naming no `choices` array -- /feedback's one grouped prompt of its metadata, with no
`choices:` of its own -- whichever comes first. A line naming `choices` arrays beside `2–4 options`
states the arrays' rule ("Use `choices` arrays; 2–4 options"), not a prompt, and is no question. A
command with no such line is not read. A command with one fails, `ERROR <file>:<line>: asks the user a
question before its **Load the question rules.** step -- add the step before this line`, unless a STEP
starts on an earlier line: a paragraph or
list item outside every fenced block that opens, its list marker dropped, with `**Load the question
rules.**` and holds the loader call `Skill(skill: "workflows-core:reference", args: "escalation-rules
core")`. A citation of that reference inside a rule statement is no step, since a run reads it as a
source note; nor is a step inside a fenced block, which a run prints. The first question is a line,
not a phase: a question before the first `##` heading needs the step before it, not merely under that
heading. The census `question rules: N command(s) present a choice list, M load the rules first` is
printed, and `--verbose` lists each asking command's step line and first question line.

IT FAILS CLOSED. A scan that finds no reference-parts declaration fails check-parts and
check-citations, and a declared reference no consumer cites fails check-citations: a gate that
matched nothing proves nothing when it passes. Entry-point files are outside that guard: a tree
declaring none passes their checks. But a declared entry point that no `##` section of a scanned
file requests, `args: "<ref> <entry>"`, fails check-citations, as a declared reference no consumer
cites does: its out-of-file check would judge nothing. A scan that finds no command presenting a
choice list fails check-questions.

WHAT IT CANNOT SEE: whether a run loads the part when it reaches a citation -- the preamble
tells it to; the rule-by-rule reading and the live runs check that it does. A name the gate
does not read as a span ("rule 6", "the overflow rule") places nothing, so its citation is
counted whole: the census is how such citations are found. A § reference belongs to a citation
by position, and by its words only in a `§N of <citation>` phrase or a `§ <Name> of
<citation>` one naming its section: "§4, which `workflows-core:gamma` defines" after a call of
another reference belongs to that call, and a § in a sentence citing nothing, with no citation
before it in its paragraph, names nothing, so one leaning on a later sentence's call goes
unread. A bare citation the gate counts whole holds every later sentence of its paragraph,
though a run that reads its rule another way ("the overflow rule") may load only that rule's
part. And an explicit request whose sentence names no rule is placed on the part it requests,
whichever that is, so a call converted to the wrong part passes there: each next-phase-offer
lane request names its lane's rule in its sentence ("`next-phase-offer dev`, the *Dev — build,
verify & deliver* lane"), so the gate places and pins it, but a request written without one
is held by review alone. The out-of-file check gives a § reference to a citation by that same
position, so a § a sentence means as another reference's -- "emit its §5 notice" after a citation of
<ref>, or a § after a bare `<name>.md`, which is no citation -- is judged as <ref>'s and fails where
the file lacks it, and a § in a sentence citing nothing, with no citation before it in its paragraph,
names nothing, so a bare pointer into <ref> there goes unread. It reads a § only by its number: one
written as a name (`§ Stop contract`) is not read, so a sentence citing <ref> by such a name alone
fails as citing no section. It reads a file in the order of its text, so a section a run reaches
before an earlier one -- a definition a later phase invokes -- is judged by where it stands. It
judges a file by its own text alone, never by the references it loads: a command's section that
loads another reference is not judged for that reference's citations of <ref>, and a reference is
judged only where it requests the entry point itself, so one that reaches <ref> by a path or a
citation, with no request of its own, goes unseen. And whether
a failing sentence only explains or applies a rule the file lacks is the reading's call, not the gate's:
it fails both. check-questions cannot see whether a run
executes the step when it reaches it -- the step says to, and the live runs check that it does -- nor
whether the step's text is the agreed paragraph, since it reads only the lead and the call. It sees a
question only as a `choices:` line, a line naming `phase-handoff` and `§4.3`, or a line stating a prompt
of 2–4 options: a question asked in prose with no array and no option count before the step goes unseen,
and so does a prompt stated on a line that also names a `choices` array, which it reads as the arrays'
rule; a line that only mentions `choices:`, or `2–4 options` without that rule's subject, counts as a
question, erring early.

Usage:
    python3 scripts/reference-parts.py [--root DIR] generate
    python3 scripts/reference-parts.py [--root DIR] check-parts
    python3 scripts/reference-parts.py [--root DIR] check-citations [--verbose]
    python3 scripts/reference-parts.py [--root DIR] check-questions [--verbose]
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
# The loader's entry-point rules: what each entry point's file holds and which requests it serves. The
# loader's body comes with every request, so it names this file, which a request on a reference with an
# entry-point file reads with or before its other reads, and holds no held list itself.
ENTRY_RULES_REL = "plugins/workflows-core/skills/reference/entry-files.md"
ENTRY_RULES_SPAN = "`${CLAUDE_PLUGIN_ROOT}/%s`" % os.path.relpath(ENTRY_RULES_REL, CORE_PLUGIN_REL)
# A core skill whose call loads one reference, so its `skill:` token cites it: a § reference after it
# belongs to that reference. Every other skill's `skill:` token is no citation; a loader call cites
# by its `args:`.
SKILL_REFERENCES = {"model-routing": "model-routing/classification"}
REF_DIR = "references"
PARTS_DIR = "reference-parts"
SCAN_DIRS = ("commands", "agents", "references")

# Ruling 1's two texts, count-free; {list} is the declared set, alphabetical and backticked.
PREAMBLE = (
    "These shared references load by part — {list}. A citation of one names a rule: before "
    "applying it, load the part that holds it, `Skill(skill: \"{loader}\", args: \"<name> "
    "<part>\")`, the part its rule index names, unless that part is already in this conversation word "
    "for word; never guess a part's name — until you hold the index (every part carries it), load it "
    "with `args: \"<name> index\"`. A citation that names no rule the index holds loads the whole "
    "reference, `args: \"<name>\"`. Never apply a rule of these references from memory."
)
SKILL_OPENING = "These references load by part: {list}."
SKILL_OPENING_LEAD = "These references load by part:"
# {list} is every declared `<ref> <entry>` pair, alphabetical and backticked. The loader skill's paragraph
# opening with it carries ENTRY_PATH and ENTRY_TRIGGER word for word: the entry-point rules name no path, so
# ENTRY_PATH is where a run learns where each file is, and ENTRY_TRIGGER is the one sentence that puts every
# entry-point rule in front of a request on such a reference.
ENTRY_OPENING = "These entry points read their own file: {list}."
ENTRY_OPENING_LEAD = "These entry points read their own file:"
ENTRY_PATH = "Each one's file is `${CLAUDE_PLUGIN_ROOT}/%s/<the reference>/<the entry point>.md`." % PARTS_DIR
ENTRY_TRIGGER = ("A request on one of their references, with or without a second argument, reads the entry-point rules, "
                 "%s, with or before its other reads, unless their text is in this conversation word for word, and "
                 "follows them." % ENTRY_RULES_SPAN)
# One per declared entry point, in ENTRY_RULES_REL: {pair} is `<ref> <entry>`, {held} what its file holds
# (held_text).
ENTRY_HOLDS = "The file for `{pair}` holds {held}."
ENTRY_HOLDS_LEAD = "The file for `{pair}` holds"

# check-questions: the step every command that presents a choice list makes before its first question,
# and what marks that question -- a `choices:` array, phase-handoff §4.3's consent array presented, or a
# prompt the command builds at run time and states as 2–4 options. A line naming `choices` arrays states
# the arrays' rule, not a prompt: "Use `choices` arrays; 2–4 options" asks nothing.
QUESTION_PLUGIN_RELS = DEPENDENT_PLUGIN_RELS + (CORE_PLUGIN_REL,)
QUESTION_DIR = "commands"
QUESTION_STEP_LEAD = "**Load the question rules.**"
QUESTION_STEP_ARGS = "escalation-rules core"
QUESTION_ARRAY = "choices:"
QUESTION_HANDOFF = ("phase-handoff", "§4.3")
QUESTION_PROMPT = re.compile(r"2[–-]4 options")
QUESTION_RULE = re.compile(r"`choices` arrays?\b")

CORE_NAME = os.path.basename(CORE_PLUGIN_REL)
SCRIPT_REL = "scripts/reference-parts.py"
ROOT_SENTENCE = "`${CLAUDE_PLUGIN_ROOT}` in this file is `%s`'s root, whichever plugin's run reads it." % CORE_NAME

# ---------------------------------------------------------------- shared patterns
PART_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DECL_OPEN = re.compile(r"^\s*<!--\s*reference-parts\b")
ENTRY_DECL_OPEN = re.compile(r"^\s*<!--\s*reference-entry-files\b")
# Per region word: the opening marker, the closing marker, and anything that looks like either. A part
# region names one part; an entry region names one entry or more, space-separated.
MARKERS = {w: (re.compile(r"^<!-- %s: (%s) -->$" % (w, names)), re.compile(r"^<!-- /%s -->$" % w),
               re.compile(r"<!--\s*/?\s*%s\b" % w))
           for w, names in (("part", r"\S+"), ("entry", r"\S+(?: \S+)*"))}
SECTION = re.compile(r"^\d+(?:\.\d+)*$")
HOLDS = re.compile(r"^holds=(\d+(?:\.\d+)*(?:,\d+(?:\.\d+)*)*)$")
HEADING_NUMBER = re.compile(r"^(\d+(?:\.\d+)*)\.?(?=\s|$)")
RULE_PHRASE = re.compile(r"^rule (\d+)$")   # a partial phrase naming a numbered rule, normalised
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
        self.always = self.private = self.helper = False
        self.needs = []      # [(ref name or None for this file, part name)]
        self.regions = []    # [(first content line number, [content lines])]
        self.headings = []   # [display text]
        self.aliases = []    # [display text]


class Source:
    """A reference file under the core reference dir that carries a declaration."""

    def __init__(self, name, rel):
        self.name, self.rel = name, rel
        self.title = None
        self.errors = []     # declarations, regions, coverage, and the rest each kind checks
        self.flags = []      # FLAG lines: a positional pointer in text a generated file holds

    def err(self, line, msg):
        self.errors.append("%s%s: %s" % (self.rel, ":%d" % line if line else "", msg))


class Ref(Source):
    def __init__(self, name, rel):
        super().__init__(name, rel)
        self.parts = {}      # declaration order
        self.link_errors = []
        self.index = {}      # norm -> part, every part (uniqueness)
        self.entries = []    # [(display, part)] for the public index, in index order

    @property
    def always(self):
        return next((p.name for p in self.parts.values() if p.always), None)

    def public(self):
        """The requestable parts, each with a file of its own: neither private nor a helper."""
        return [p for p in self.parts.values() if not p.private and not p.helper]

    def helpers(self):
        return [p for p in self.parts.values() if p.helper]


class EntryDecl:
    """One declared entry point: the § numbers its file holds whole, as declared; per § it holds in
    part, the phrases that identify the held text; and its regions, each as (first, last) content
    line numbers of the source, in source order."""

    def __init__(self, line, holds):
        self.line = line
        self.holds = holds
        self.partial = {}
        self.regions = []
        self.opening = None   # the § of the first numbered heading, where a region holds text before it


class EntryRef(Source):
    def __init__(self, name, rel, lines):
        super().__init__(name, rel)
        self.lines = lines
        self.entries = {}    # entry -> EntryDecl, declaration order


def ids(root: Path, path: Path):
    """A core reference file's name (`model-routing/classification`) and repo-relative path."""
    return (path.relative_to(root / CORE_PLUGIN_REL / REF_DIR).with_suffix("").as_posix(),
            path.relative_to(root).as_posix())


def declares(lines, opener, word):
    """Whether a source carries a declaration or a region marker of `word` outside a code span."""
    return any(opener.match(l) or MARKERS[word][2].search(CODE_SPAN.sub("", l)) for l in lines)


def declaration_block(src, lines, keyword, opener, kind):
    """The (first, last) line indexes of the `<!-- <keyword>` block directly after the H1 line, with
    src.title set; or None, the reason reported on `src`. A second block is reported too."""
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first is None or not lines[first].startswith("# "):
        src.err(None, "%s opens with its H1 line, and the declaration follows it" % kind)
        return None
    src.title = lines[first][2:].strip()
    start = next((i for i in range(first + 1, len(lines)) if lines[i].strip()), None)
    if start is None or lines[start].strip() != "<!-- " + keyword:
        src.err(start + 1 if start is not None else None,
                "the <!-- %s declaration must directly follow the H1 line" % keyword)
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].strip() == "-->"), None)
    if end is None:
        src.err(start + 1, "the %s declaration is never closed with -->" % keyword)
        return None
    if any(opener.match(l) for l in lines[end + 1:]):
        src.err(None, "carries a second %s declaration" % keyword)
    return start, end


def quoted_names(rest):
    """The names of a `"<name>" ...` list, every one quoted and non-empty; None for any other text."""
    names = re.findall(r'"([^"]*)"', rest)
    return names if re.fullmatch(r'(\s*"[^"]*")+\s*', rest) and all(x.strip() for x in names) else None


def more(numbers):
    """` (N more non-blank line(s), to line M)` after the first of several line numbers."""
    return " (%d more non-blank line(s), to line %d)" % (len(numbers) - 1, numbers[-1]) if len(numbers) > 1 else ""


def walk_regions(src, lines, start, word, names):
    """The body from line index `start`, as events: ("open", n, names) where `<!-- <word>: <name> -->`
    opens a region; ("close", names, first, last) where `<!-- /<word> -->` closes it, first and last
    being its content line numbers; ("line", n, line, the open region's names or None, whether the line
    is fenced) for every other line; and ("halt",) after a marker error, reported on `src`, which ends
    the walk. `names` is a tuple: one name for a part region, one or more for an entry region. A region
    names only members of `names`, each once, never nests, and never closes inside a fenced block."""
    opener, closer, anything = MARKERS[word]
    fences, current = Fences(), None   # (names, the line number of its opening marker)
    for i in range(start, len(lines)):
        n, line, s = i + 1, lines[i], lines[i].strip()
        mo, mc = opener.match(s), closer.match(s)
        opened = tuple(mo.group(1).split(" ")) if mo else ()
        if mo and current is not None:
            src.err(n, "region '%s' opens inside region '%s' (opened at line %d) -- regions never nest"
                    % (mo.group(1), " ".join(current[0]), current[1]))
        elif mo and any(o not in names for o in opened):
            src.err(n, "region '%s' names no declared %s" % (next(o for o in opened if o not in names), word))
        elif mo and len(set(opened)) < len(opened):
            src.err(n, "region names '%s' twice -- an %s region names each %s once"
                    % (next(o for o in opened if opened.count(o) > 1), word, word))
        elif mo:
            current = (opened, n)
            yield ("open", n, current[0])
            continue
        elif mc and current is None:
            src.err(n, "<!-- /%s --> closes no open region" % word)
        elif mc and fences.open is not None:
            src.err(n, "region '%s' closes inside a fenced block" % " ".join(current[0]))
        elif mc:
            yield ("close", current[0], current[1] + 1, n - 1)
            current = None
            continue
        elif anything.search(CODE_SPAN.sub("", line)):
            src.err(n, "malformed marker -- a region opens with `<!-- %s: <name> -->` and closes with "
                       "`<!-- /%s -->`, each alone on its line" % (word, word))
        else:
            yield ("line", n, line, current and current[0], fences.step(line))
            continue
        yield ("halt",)
        return
    if current is not None:
        src.err(current[1], "region '%s' is never closed" % " ".join(current[0]))
        yield ("halt",)


def parse_source(root: Path, path: Path):
    """A Ref for a split source, or None for a reference that is not split."""
    name, rel = ids(root, path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if not declares(lines, DECL_OPEN, "part"):
        return None
    ref = Ref(name, rel)
    block = declaration_block(ref, lines, "reference-parts", DECL_OPEN, "a split reference")
    if block is None:
        return ref
    start, end = block
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
                elif w == "helper":
                    part.helper = True
                elif w.startswith("needs=") and len(w) > 6:
                    for dep in w[6:].split(","):
                        if not dep:
                            continue
                        other, _, dpart = dep.rpartition("/")
                        part.needs.append((other or None, dpart))
                else:
                    ref.err(n, "part '%s': unknown word '%s' -- always, private, helper or needs=" % (pname, w))
            ref.parts[pname] = part
        elif words[0] == "alias" and len(words) >= 3:
            names = quoted_names(lines[i].split(None, 2)[2])
            if names is None:
                ref.err(n, "an alias line is `alias <part> \"<name>\" ...`, every name quoted and non-empty")
                continue
            aliases.append((n, words[1], names))
        else:
            ref.err(n, "unknown declaration line '%s' -- a line is `part ...` or `alias ...`" % lines[i].strip())
    if ref.errors:
        return ref

    # The body: regions, coverage, headings, links, flags.
    gap = []

    def report_gap():
        if gap:
            ref.err(gap[0], "a non-blank line lies in no part region -- every non-blank line after the "
                            "declaration lies in exactly one%s" % more(gap))
            gap.clear()

    for event in walk_regions(ref, lines, end + 1, "part", ref.parts):
        if event[0] == "halt":
            return ref
        if event[0] == "open":
            report_gap()
            continue
        if event[0] == "close":
            _, (pname,), first, last = event
            ref.parts[pname].regions.append((first, lines[first - 1:last]))
            continue
        _, n, line, pnames, fenced = event
        if pnames is None:
            if line.strip():
                gap.append(n)
            continue
        part = ref.parts[pnames[0]]
        if not fenced:
            h = HEADING.match(line)
            if h and h.group(2):
                part.headings.append(h.group(2))
            plain = CODE_SPAN.sub("", line)
            targets = INLINE_LINK.findall(plain)
            m = REF_LINK_DEF.match(plain)
            if m:
                targets.append(m.group(1))
            for t in targets:
                if not ABSOLUTE.match(t):
                    ref.link_errors.append("%s:%d: relative link '%s' -- a generated part sits one directory "
                                           "deeper than its source, where it would not resolve" % (rel, n, t))
        if not part.private:
            for m in POSITIONAL.finditer(line):
                ref.flags.append("FLAG %s:%d: %s" % (rel, n, m.group(0)))
    report_gap()

    always = [p.name for p in ref.parts.values() if p.always]
    if len(always) != 1:
        ref.err(None, "%d parts are marked always%s -- exactly one part is"
                % (len(always), " (%s)" % ", ".join(always) if always else ""))
    for p in ref.parts.values():
        if p.always and p.private:
            ref.err(p.line, "part '%s' is marked always and private -- the always part comes with every part" % p.name)
        if p.helper and (p.always or p.private):
            ref.err(p.line, "part '%s' is marked helper and %s -- a helper comes only with a part that brings it"
                    % (p.name, "always" if p.always else "private"))
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


def within(inner, outer):
    """Whether § `inner` is § `outer` or lies under it: `3.1` and `3` are within `3`, `31` is not."""
    return inner == outer or inner.startswith(outer + ".")


def section_extents(heads, end):
    """{§ number: (first, last) line numbers} of each numbered heading in `heads` -- (line number,
    level, § number or None) of every heading outside a fenced block, in source order. A section runs
    to the next heading that is neither numbered under it (`3.1` under `3`) nor an unnumbered one
    deeper than its own, or to line `end`; the first heading with a number owns it."""
    out = {}
    for k, (n, level, num) in enumerate(heads):
        if num and num not in out:
            stop = next((m for m, lv, nm in heads[k + 1:] if not (nm.startswith(num + ".") if nm else lv > level)),
                        end + 1)
            out[num] = (n, stop - 1)
    return out


def parse_entry_source(root: Path, path: Path):
    """An EntryRef for a reference declaring entry-point files, or None for one that declares none."""
    name, rel = ids(root, path)
    lines = path.read_text(encoding="utf-8").splitlines()
    if not declares(lines, ENTRY_DECL_OPEN, "entry"):
        return None
    ref = EntryRef(name, rel, lines)
    block = declaration_block(ref, lines, "reference-entry-files", ENTRY_DECL_OPEN,
                              "a reference declaring entry-point files")
    if block is None:
        return ref
    start, end = block
    partials = []   # (line number, entry, §, phrases)
    for i in range(start + 1, end):
        n, words = i + 1, lines[i].split()
        if not words:
            continue
        if words[0] == "entry":
            holds = HOLDS.match(words[2]) if len(words) == 3 and PART_NAME.match(words[1]) else None
            if holds is None:
                ref.err(n, "an entry line is `entry <entry> holds=<§>[,<§>...]`, the entry lowercase letters, digits "
                           "and dashes")
            elif words[1] in ref.entries:
                ref.err(n, "entry '%s' is declared twice" % words[1])
            else:
                ref.entries[words[1]] = EntryDecl(n, holds.group(1).split(","))
        elif words[0] == "partial":
            phrases = quoted_names(lines[i].split(None, 3)[3]) if len(words) >= 4 and SECTION.match(words[2]) else None
            if phrases is None:
                ref.err(n, "a partial line is `partial <entry> <§> \"<phrase>\" ...`, every phrase quoted and non-empty")
            else:
                partials.append((n, words[1], words[2], phrases))
        else:
            ref.err(n, "unknown declaration line '%s' -- a line is `entry ...` or `partial ...`" % lines[i].strip())
    partial_at = {}   # (entry, §) -> the line declaring it
    for n, entry, sec, phrases in partials:
        if entry not in ref.entries:
            ref.err(n, "partial names entry '%s', which is not declared" % entry)
        else:
            ref.entries[entry].partial.setdefault(sec, []).extend(phrases)
            partial_at.setdefault((entry, sec), n)
    # A section held whole is declared once, its subsections with it: no other § of its entry, held whole
    # or in part, is it or lies under it, and no § held in part has it under it.
    tail = " -- a section held whole is declared once, its subsections with it"
    for entry, decl in ref.entries.items():
        for j, sec in enumerate(decl.holds):
            other = next((o for o in decl.holds[:j] if within(sec, o) or within(o, sec)), None)
            if other == sec:
                ref.err(decl.line, "entry '%s' holds §%s whole twice%s" % (entry, sec, tail))
            elif other:
                outer, inner = (other, sec) if within(sec, other) else (sec, other)
                ref.err(decl.line, "entry '%s' holds §%s whole, which covers §%s, held whole too%s"
                        % (entry, outer, inner, tail))
        for sec in decl.partial:
            for held in dict.fromkeys(decl.holds):
                if within(sec, held):
                    ref.err(partial_at[(entry, sec)], "entry '%s' holds §%s whole, which covers §%s, held in part too%s"
                            % (entry, held, sec, tail))
                elif within(held, sec):
                    ref.err(partial_at[(entry, sec)], "entry '%s' holds §%s in part, which covers §%s, held whole too%s"
                            % (entry, sec, held, tail))
    if ref.errors:
        return ref

    # The body: regions, and the numbered headings that bound each section. `body` maps the number of
    # every line that is no marker to its text, and `owner` each region line's to the entries its region
    # names.
    body, owner, heads = {}, {}, []
    for event in walk_regions(ref, lines, end + 1, "entry", ref.entries):
        if event[0] == "halt":
            return ref
        if event[0] == "close":
            _, names, first, last = event
            for entry in names:
                ref.entries[entry].regions.append((first, last))
            owner.update((k, names) for k in range(first, last + 1))
        elif event[0] == "line":
            _, n, line, names, fenced = event
            body[n] = line
            if names is not None:
                ref.flags += ["FLAG %s:%d: %s" % (rel, n, m.group(0)) for m in POSITIONAL.finditer(line)]
            h = None if fenced else HEADING.match(line)
            if h and h.group(2):
                num = HEADING_NUMBER.match(h.group(2))
                heads.append((n, len(h.group(1)), num and num.group(1)))
    extent, points = section_extents(heads, len(lines)), entry_points(path)

    # The text before the first numbered heading, which no § names: whether a region of each entry
    # holds any of it.
    if extent:
        first_sec = min(extent, key=lambda s: extent[s][0])
        for decl in ref.entries.values():
            if any(body[k].strip() for a, b in decl.regions for k in range(a, b + 1) if k < extent[first_sec][0]):
                decl.opening = first_sec
    for entry, decl in ref.entries.items():
        if entry not in points:
            ref.err(decl.line, "entry '%s' is not an entry point of %s:%s -- not the first word of a code span in any "
                               "of its headings; %s" % (entry, CORE_NAME, name, "its entry points: " +
                                                       either(sorted(points), "and") if points else "it has none"))
        for sec, at in [(s, decl.line) for s in decl.holds] + [(s, partial_at[(entry, s)]) for s in decl.partial]:
            if sec not in extent:
                ref.err(at, "§%s names no section of %s:%s -- no heading opens with that number" % (sec, CORE_NAME, name))
        # A section held whole: every non-blank line of it, its heading included, lies in this entry's regions.
        for sec in (s for s in decl.holds if s in extent):
            first, last = extent[sec]
            gap = [k for k in range(first, last + 1) if body.get(k, "").strip() and entry not in owner.get(k, ())]
            if gap:
                ref.err(gap[0], "§%s is held whole by entry '%s', but this line of it lies in no `%s` region%s"
                        % (sec, entry, entry, more(gap)))
        # Every region line inside a numbered section lies inside one the entry holds whole or in part,
        # so the line under the file's title names every section the file holds text of; a line in no
        # numbered section, before the first, is free.
        spans, stray = [extent[s] for s in list(decl.holds) + list(decl.partial) if s in extent], {}
        for first, last in decl.regions:
            for k in range(first, last + 1):
                inside = [s for s, (a, b) in extent.items() if a <= k <= b]
                if body[k].strip() and inside and not any(a <= k <= b for a, b in spans):
                    stray.setdefault(max(inside, key=lambda s: extent[s][0]), []).append(k)
        for sec, at in stray.items():
            ref.err(at[0], "this line of a `%s` region lies in §%s, which entry '%s' neither holds whole nor holds in "
                           "part%s" % (entry, sec, entry, more(at)))
        # A section held in part: each phrase, normalised as a rule name is, is in this entry's region
        # text inside that section -- and a phrase naming a numbered rule, `rule <N>`, only where a region
        # line there opens the rule's own item, `N.`: the section's opening line may mention the rule
        # while the rule itself lies outside every region.
        for sec, phrases in ((s, p) for s, p in decl.partial.items() if s in extent):
            first, last = extent[sec]
            mine = [body[k] for k in range(first, last + 1) if entry in owner.get(k, ())]
            held = norm(" ".join(mine))
            for phrase in phrases:
                rule = RULE_PHRASE.match(norm(phrase))
                if rule and not any(item.group(0).strip() == rule.group(1) + "."
                                    for item in map(LIST_ITEM.match, mine) if item):
                    ref.err(partial_at[(entry, sec)], "§%s is held in part by entry '%s', but no `%s` region in it holds "
                                                      "\"%s\" -- a phrase naming a numbered rule is held only by the "
                                                      "rule's own item, `%s.`, never by a mention of it"
                            % (sec, entry, entry, phrase, rule.group(1)))
                elif norm(phrase) not in held:
                    ref.err(partial_at[(entry, sec)], "§%s is held in part by entry '%s', but no `%s` region in it holds "
                                                      "\"%s\"" % (sec, entry, entry, phrase))
    return ref


def core_references(root: Path):
    base = root / CORE_PLUGIN_REL / REF_DIR
    return sorted(base.rglob("*.md")) if base.is_dir() else []


def load_entries(root: Path):
    """Every reference under the core reference dir that declares entry-point files, keyed by name.
    None declaring any is no problem: entry-point files are not part of the vacuity guard."""
    refs = {}
    for path in core_references(root):
        ref = parse_entry_source(root, path)
        if ref is not None:
            refs[ref.name] = ref
    return refs


def entry_files(root: Path):
    """{reference: {entry: EntryDecl}} for every declared entry point, as its source declares it, and {}
    for a tree declaring none. It never returns a declaration it could not read whole: where any
    reference's entry-point declaration fails a check check-parts makes on the source, it raises
    ValueError naming every such problem, and the caller stops before judging anything against it."""
    refs = load_entries(root)
    problems = [e for r in refs.values() for e in r.errors]
    if problems:
        raise ValueError("entry-point declarations fail check-parts:\n" + "\n".join(problems))
    return {name: ref.entries for name, ref in refs.items()}


def load(root: Path):
    """Every split reference under the core reference dir, keyed by name; and the problems
    that stop a run before it can check anything (vacuity)."""
    refs = {}
    for path in core_references(root):
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
    # A helper has no file: its text reaches a run only inside a requestable part that brings it, and
    # its own reference's index sends its rules to such a part. So each helper needs a part of its own
    # reference that brings it; one that only another reference's part brings has nowhere to send them.
    bad = broken(refs)
    for ref in refs.values():
        if ref.name not in bad:
            for h in ref.helpers():
                if not carriers(refs, ref, h.name):
                    ref.err(h.line, "part '%s' is a helper no requestable part of %s:%s brings -- its index has no "
                                    "part to send its rules to" % (h.name, CORE_NAME, ref.name))
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
    return joined([region for p in parts for region in ref.parts[p].regions])


def joined(regions):
    """The text of regions, each (first line number, [lines]), in source order: each trimmed of its
    blank edge lines, and one blank line between two."""
    chunks = []
    for _, lines in sorted(regions):
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


def code(text):
    """`text` as one inline code span, whatever backticks it holds: a name starting with a number or
    a list marker renders as itself, never as a nested list."""
    fence = "`" * (max((len(r) for r in re.findall("`+", text)), default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return fence + pad + text + pad + fence


def either(names, word="or", quote="`"):
    """`a`, `b` or `c` -- in the order given."""
    q = ["%s%s%s" % (quote, n, quote) for n in names]
    return q[0] if len(q) == 1 else ", ".join(q[:-1]) + " %s " % word + q[-1]


def carriers(refs, ref, part):
    """The requestable parts of `ref` whose file brings `part`, in declaration order."""
    return [p.name for p in ref.public() if part in closure(refs, ref, p.name)[0][ref.name]]


def index_block(refs, ref):
    lead = "Every rule name in `%s`, with the part that holds it; `%s` comes with every part." % (ref.name, ref.always)
    if ref.helpers():
        lead += (" A rule of a helper part, which has no file of its own, is listed with the parts that bring it;"
                 " load any one of them.")
    lead += (" Load a part with `Skill(skill: \"%s\", args: \"%s <part>\")`, unless it is already in this "
             "conversation word for word." % (LOADER_SKILL, ref.name))
    blocks = ["## Rule index of `%s`" % ref.name, lead]
    if ref.entries:
        blocks.append("\n".join("- %s → %s" % (code(d), either(carriers(refs, ref, p)) if ref.parts[p].helper
                                                 else "`%s`" % p) for d, p in ref.entries))
    return "\n\n".join(blocks)


def holds_line(refs, ref, included):
    """The line under a part file's title naming every part it holds: its own reference's requestable
    parts, then its helpers, then each other reference's parts it bundles, each in declaration order."""
    def held(r):
        names = [p for p in refs[r].parts.values() if p.name in included[r]]
        plain, helpers = [p.name for p in names if not p.helper], [p.name for p in names if p.helper]
        text = "part%s %s" % ("s" if len(plain) > 1 else "", either(plain, "and"))
        if helpers:
            text += ", with helper part%s %s" % ("s" if len(helpers) > 1 else "", either(helpers, "and"))
        return text
    line = "This file holds " + held(ref.name)
    for other in [r for r in included if r != ref.name]:
        line += ", and `%s:%s`'s %s" % (CORE_NAME, other, held(other))
    return line + "."


def expected_tree(refs):
    """{repo-relative path: (text, source path)} of every split reference's generated file, for each
    reference that assembles; and the names of those that do not."""
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
        if ref.helpers():
            plist.append("\nHelper parts, each with no file of its own and never requested, come only with a part that "
                         "brings them: %s." % either([h.name for h in ref.helpers()], "and"))
        out[base + "index.md"] = ("\n\n".join(
            [header(ref), "# %s — index" % ref.title, index_block(refs, ref), "## Parts of `%s`" % ref.name,
             "\n".join(plist)]) + "\n", ref.rel)
        for p in ref.public():
            included, named = closure(refs, ref, p.name)
            blocks = [header(ref), "# %s — part %s" % (ref.title, p.name), holds_line(refs, ref, included),
                      ROOT_SENTENCE, index_block(refs, ref), "---", text_of(ref, included[ref.name])]
            for other in [r for r in included if r != ref.name]:
                parts = named[other]
                which = "part " + parts[0] if len(parts) == 1 else "parts " + ", ".join(parts[:-1]) + " and " + parts[-1]
                blocks += ["---", "Bundled from %s:%s, %s:" % (CORE_NAME, other, which),
                           text_of(refs[other], included[other])]
            out[base + p.name + ".md"] = ("\n\n".join(b for b in blocks if b) + "\n", ref.rel)
    return out, bad


def held_text(decl, opening=False):
    """What an entry-point file holds: the sections held whole, then those held in part, each in source
    order, the phrases of each in declaration order -- and first, with `opening`, the text before the
    first numbered heading where a region holds some. The generated file's line under its title says
    it without that text; the loader skill's ENTRY_HOLDS sentence says it with it."""
    def ordered(sections):
        return sorted(sections, key=lambda s: [int(x) for x in s.split(".")])
    whole = (["the text before §" + decl.opening] if opening and decl.opening else []) + \
        ["§" + s for s in ordered(decl.holds)]
    text = either(whole, "and", "")
    if decl.partial:
        text += ", and in part " + either(["§%s (%s)" % (s, either(decl.partial[s], "and", '"'))
                                           for s in ordered(decl.partial)], "and", "")
    return text


def entry_line(ref, entry, decl, count):
    """The line under an entry-point file's title: held_text, the whole reference's load, and the file's
    own line count, so a run reading it in ranges knows where it ends without `wc -l`."""
    return "This file holds entry point `%s` of `%s`: %s. Any other section is in the whole reference: " \
           "`Skill(skill: \"%s\", args: \"%s\")`. This file is %d lines long." \
           % (entry, ref.name, held_text(decl), LOADER_SKILL, ref.name, count)


def entry_tree(entries):
    """{repo-relative path: (text, source path)} of every entry-point file, for each reference whose
    declaration and regions hold."""
    out = {}
    for ref in entries.values():
        if ref.errors:
            continue
        for entry, decl in ref.entries.items():
            text = joined([(first, ref.lines[first - 1:last]) for first, last in decl.regions])
            def build(count):
                blocks = [header(ref), "# %s — entry point %s" % (ref.title, entry),
                          entry_line(ref, entry, decl, count), ROOT_SENTENCE, text]
                return "\n\n".join(b for b in blocks if b) + "\n"
            # The count line is one line whatever its number, so the count of a build with any number
            # is the count of the file it names.
            body = build(0)
            out["%s/%s/%s/%s.md" % (CORE_PLUGIN_REL, PARTS_DIR, ref.name, entry)] = (
                build(body.count("\n")), ref.rel)
    return out


def actual_tree(root):
    base = root / CORE_PLUGIN_REL / PARTS_DIR
    return sorted(p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file()) if base.is_dir() else []


def source_problems(refs, entries):
    return ([e for r in refs.values() for e in r.errors + r.link_errors]
            + [e for r in entries.values() for e in r.errors])


# ---------------------------------------------------------------- subcommands
def cmd_generate(root, _verbose):
    refs, vacuous = load(root)
    entries = load_entries(root)
    problems = source_problems(refs, entries)
    if problems:
        for p in problems:
            print("ERROR " + p)
        print("reference-parts generate: FAIL -- %d problem(s); nothing written" % len(problems))
        return 1
    if vacuous and not entries:
        print("no reference carries a reference-parts declaration; removing every generated file")
    want, _ = expected_tree(refs)
    want.update(entry_tree(entries))
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
    entries = load_entries(root)
    problems = vacuous + source_problems(refs, entries)
    want, bad = expected_tree(refs)
    made = entry_tree(entries)
    want.update(made)
    # A reference whose source fails is not judged for freshness: generate refuses to run on
    # it, so its files cannot be repaired until the source is, and every one would be noise.
    bad |= {n for n, r in refs.items() if r.link_errors} | {n for n, r in entries.items() if r.errors}
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
    for r in list(refs.values()) + list(entries.values()):
        for f in r.flags:
            print(f)
    if problems:
        print("reference-parts check-parts: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("reference-parts check-parts: PASS -- %d split reference(s), %d entry file(s), %d generated file(s) fresh"
          % (len(refs), len(made), len(want)))
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
POSSESSIVE = re.compile(r"['’]s$")
# The words give a § to the citation right after them in two forms only: `§4 of <citation>`, with
# nothing between the number and "of"; and `§ <Name> of <citation>`, where <Name> is a section of
# that citation's reference -- its index if split, else a heading of its file.
OF_TAIL = r"\s+of\s+`?(?:Skill\(\s*)?(?:skill:\s*)?(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?$"
OF_NUMBER = re.compile(r"§\s*\d+(?:\.\d+)*" + OF_TAIL)
OF_NAME = re.compile(r"§\s+([A-Za-z][\w'’ .-]*?)" + OF_TAIL)
TOKEN = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(CORE_NAME) + r":([A-Za-z0-9][A-Za-z0-9_-]*)")
CALL = re.compile(r'"' + re.escape(LOADER_SKILL) + r'"\s*,\s*args:\s*"([^"]*)"')
WHOLE_PATH = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(REF_DIR) + r"/([A-Za-z0-9][A-Za-z0-9_-]*)\.md\b")
PART_PATH = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(PARTS_DIR) + r"/([A-Za-z0-9][A-Za-z0-9_-]*)/([^/\s`)\"]+)\.md\b")
# Every reference citation, split or not, that a § reference can belong to: a `<plugin>:<name>`
# token naming a reference file of that plugin the tree holds, a loader call, a call of a skill
# SKILL_REFERENCES names, a path.
ANY_TOKEN = re.compile(r"(?<![A-Za-z0-9_-])([a-z][a-z0-9-]*):([A-Za-z0-9](?:[A-Za-z0-9_/-]*[A-Za-z0-9])?)")
ANY_CALL = re.compile(r'"' + re.escape(LOADER_SKILL) + r'"\s*,\s*args:\s*"\s*([^"\s]*)')
SKILL_CALL = re.compile(r'skill:\s*"' + re.escape(CORE_NAME) + r':([A-Za-z0-9][A-Za-z0-9_-]*)"')
ANY_PATH = re.compile(r"(?<![A-Za-z0-9_.-])(" + re.escape(REF_DIR) + "|" + re.escape(PARTS_DIR) +
                      r")/([A-Za-z0-9][A-Za-z0-9_/-]*)\.md\b")
NO_CITATION = object()   # what a § reference belongs to where no citation it could lean on exists


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


def keep_code(text):
    """The text with each code span's emphasis and quote marks blanked and the rest kept, so a
    span never opens or closes inside code, and a name holding code (`*The `(x)` rule*`) reads
    whole."""
    return CODE_SPAN.sub(lambda m: re.sub("[*\"“”]", " ", m.group(0)), text)


def names_in(sentence):
    """The rule names one sentence may carry: [(offset, readings, is_section)] -- emphasis,
    backtick and quote spans, and § references -- each with the readings, of which the first the
    index holds is the name. A § inside a code span is no § reference."""
    found = [(m.start(), [m.group(1)], False) for m in CODE_SPAN.finditer(sentence)]
    kept, plain = keep_code(sentence), mask(sentence)
    for pat in SPANS:
        found += [(m.start(), [m.group(1)], False) for m in pat.finditer(kept)]
    found += [(m.start(), ["§" + m.group(1)], True) for m in SECTION_NUM.finditer(plain)]
    for m in SECTION_NAME.finditer(plain):
        # `§ <name>` names a heading, or an alias written with its `§`; the name runs to the
        # next delimiter, and its leading runs of words are read longest first. A possessive
        # (`§ Reporting's terms`) ends the name: it is read as the section, after the words as
        # written up to it and before anything shorter.
        words = m.group(1).split()
        cut = next((k for k, w in enumerate(words) if POSSESSIVE.search(w)), None)
        if cut is None:
            heads = [" ".join(words[:k]) for k in range(len(words), 0, -1)]
        else:
            heads = ([" ".join(words[:k]) for k in range(len(words), cut, -1)]
                     + [" ".join(words[:cut] + [POSSESSIVE.sub("", words[cut])])]
                     + [" ".join(words[:k]) for k in range(cut, 0, -1)])
        found.append((m.start(), [r for h in heads for r in (h, "§ " + h)], True))
    return found


def covers(refs, ref, part):
    return closure(refs, ref, part)[0][ref.name]


# A code span as CommonMark reads one: a run of backticks, then text, then a run of the same length,
# so ``a `b` c`` is one span holding a `b` c, never an empty span and `b`.
HEADING_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")


def entry_points(path):
    """The entry points of a reference that does not load by part: the first word of each code span
    in one of its headings, a heading inside a fenced block being none -- `resolve-address` in
    `### Entry point: `resolve-address <ARG> [<KIND>]``, and `key-list` in `## `key-summary` and
    `key-list``, as the second span."""
    names, fences = set(), Fences()
    for line in path.read_text(encoding="utf-8").splitlines():
        h = None if fences.step(line) else HEADING.match(line)
        if h and h.group(2):
            names.update(m.group(2).split()[0] for m in HEADING_SPAN.finditer(h.group(2)) if m.group(2).split())
    return names


def level2_sections(text):
    """{line number: the line of the `##` heading whose section holds it, or None} -- a `##` section
    runs to the next heading of level 1 or 2 outside a fenced block, and a line before the first `##`
    heading, or under a `#` one, is in none."""
    out, current, fences = {}, None, Fences()
    for n, line in enumerate(text.splitlines(), 1):
        h = None if fences.step(line) else HEADING.match(line)
        if h and len(h.group(1)) <= 2:
            current = n if len(h.group(1)) == 2 else None
        out[n] = current
    return out


def loads_whole(toks, ref, entries):
    """Whether a loader call's tokens load all of `ref`, a reference declaring entry-point files: no second
    token, or one naming an entry point with no file of its own, which the loader answers with the whole
    reference; a placeholder loads nothing."""
    return toks[0] == ref and (len(toks) == 1 or toks[1] not in entries) and not toks[-1].startswith("<")


def holds_cited(decl, number, sentence):
    """Whether an entry-point file holds §`number` for the sentence citing it: under a § it holds whole,
    or a § it holds in part where one of that section's phrases is in the sentence, each normalised as
    a rule name is."""
    if any(within(number, h) for h in decl.holds):
        return True
    return any(norm(p) in norm(sentence) for p in decl.partial.get(number, ()))


def scan_files(root, rels, dirs=SCAN_DIRS):
    """Every markdown file under each plugin's `dirs`, CHANGELOG.md excluded, in plugin, directory and
    path order."""
    for rel in rels:
        for d in dirs:
            base = root / rel / d
            if base.is_dir():
                for path in sorted(base.rglob("*.md")):
                    if path.name != "CHANGELOG.md":
                        yield path


def cmd_check_citations(root, verbose):
    refs, vacuous = load(root)
    entries = load_entries(root)
    problems = vacuous + [e for r in list(refs.values()) + list(entries.values()) for e in r.errors]
    if problems:
        for p in problems:
            print("ERROR " + p)
        print("reference-parts check-citations: FAIL -- %d problem(s); fix the declarations first" % len(problems))
        return 1
    split = sorted(refs)
    declared = entry_files(root)   # never raises here: a failing declaration stopped the run above
    entry_census = {(r, e): [0, 0] for r, es in declared.items() for e in es}   # request sections, citations

    # The loader skill names the declared set, and the declared entry points where there are any.
    skill = root / LOADER_SKILL_REL
    want = SKILL_OPENING.format(list=listing(split))
    if not skill.is_file():
        problems.append("%s: missing -- the loader skill must open a paragraph with \"%s\"" % (LOADER_SKILL_REL, want))
    else:
        paras = paragraphs(skill.read_text(encoding="utf-8"))
        lists = [(want, SKILL_OPENING_LEAD, "split list")]
        pairs = ["%s %s" % (n, e) for n, r in entries.items() for e in r.entries]
        if pairs:
            lists.append((ENTRY_OPENING.format(list=listing(pairs)), ENTRY_OPENING_LEAD, "entry list"))
        for opening, lead, what in lists:
            if not any(p.startswith(opening) for p in paras):
                said = next((p for p in paras if p.startswith(lead)), None)
                reads = ("it reads \"%s\"" % (said.split(". ")[0].rstrip(".") + ".")) if said else \
                    "no paragraph opens with \"%s\"" % lead
                problems.append("%s: no paragraph opens with the %s the declarations give, \"%s\" -- %s"
                                % (LOADER_SKILL_REL, what, opening, reads))
        # The entry-point rules: the loader's paragraph opening with the entry list names them, they name
        # each declared entry point's held list as its declaration and regions give it -- the loader
        # serves a citation of a held section from the file -- and the loader's body, which comes with
        # every request, holds none of those lists itself.
        if pairs:
            refs_with = listing(n for n, r in entries.items() if r.entries)
            opened = next((p for p in paras if p.startswith(ENTRY_OPENING_LEAD)), None)
            for sentence, why in ((ENTRY_PATH, "the entry-point rules name no path, so this sentence is where a run "
                                               "learns where each file is"),
                                  (ENTRY_TRIGGER, "it is the one sentence that has a request on %s read the entry-point "
                                                  "rules" % refs_with)):
                if opened is not None and sentence not in opened:
                    problems.append("%s: the paragraph opening with the entry list lacks \"%s\" -- %s"
                                    % (LOADER_SKILL_REL, sentence, why))
            for n, r in entries.items():
                for e in r.entries:
                    if any(ENTRY_HOLDS_LEAD.format(pair="%s %s" % (n, e)) in p for p in paras):
                        problems.append("%s: names what the file of `%s %s` holds, which the entry-point rules, %s, "
                                        "name -- the loader's body comes with every request, so the list is in the "
                                        "rules alone" % (LOADER_SKILL_REL, n, e, ENTRY_RULES_REL))
            rules = root / ENTRY_RULES_REL
            if not rules.is_file():
                problems.append("%s: missing -- a request on %s reads it with or before its other reads, for what each "
                                "entry point's file holds" % (ENTRY_RULES_REL, refs_with))
            else:
                rule_paras = paragraphs(rules.read_text(encoding="utf-8"))
                for n, r in entries.items():
                    for e, d in r.entries.items():
                        pair = "%s %s" % (n, e)
                        held = ENTRY_HOLDS.format(pair=pair, held=held_text(d, opening=True))
                        if not any(held in p for p in rule_paras):
                            lead = ENTRY_HOLDS_LEAD.format(pair=pair)
                            said = next((p[p.index(lead):] for p in rule_paras if lead in p), None)
                            reads = ("it reads \"%s\"" % (re.split(r"(?<=\)|\")\.\s|(?<=[0-9])\.\s", said)[0].rstrip(".")
                                                         + ".")) if said else "no sentence opens with \"%s\"" % lead
                            problems.append("%s: the loader names what the file of `%s` holds as its declaration gives "
                                            "it, \"%s\" -- %s" % (ENTRY_RULES_REL, pair, held, reads))

    preamble = PREAMBLE.format(list=listing(split), loader=LOADER_SKILL)
    plugins_dir, resolved = root / os.path.dirname(CORE_PLUGIN_REL), {}

    def is_reference(plugin, name):
        """Whether `<plugin>:<name>` names a reference file the tree holds -- resolved, never
        guessed. A directory is no reference: a command or skill shares its name with one."""
        if (plugin, name) not in resolved:
            base = plugins_dir / plugin / REF_DIR
            resolved[(plugin, name)] = ".." not in name.split("/") and (base / (name + ".md")).is_file()
        return resolved[(plugin, name)]

    core_refs, sections = root / CORE_PLUGIN_REL / REF_DIR, {}

    def is_section(key, path, name):
        """Whether `name` is a section of the cited reference: in its index if split, else a heading
        of the file the citation resolves to."""
        if key in refs:
            return any(norm(r) in refs[key].index for r in (name, "§ " + name))
        if path not in sections:
            heads, fences = set(), Fences()
            for line in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
                h = None if fences.step(line) else HEADING.match(line)
                if h and h.group(2):
                    heads.add(norm(h.group(2)))
            sections[path] = heads
        return norm(name) in sections[path]

    census = {n: [0, []] for n in split}   # placed, [whole locations]
    consumer_cites = {n: 0 for n in split}
    named_entry_points, entry_requests = {}, []   # path -> its entry points; [(reference, token)]

    def entry_request(rel, line, name, token):
        """An entry-point request on a reference that does not load by part names one of its entry
        points, or the loader stops the run that makes it. A first token naming no reference file
        is check 16's (scripts/check-docs.sh), and a placeholder names nothing."""
        path = core_refs / (name + ".md")
        if token.startswith("<") or ".." in name.split("/") or not path.is_file():
            return
        if path not in named_entry_points:
            named_entry_points[path] = entry_points(path)
        entry_requests.append((name, token))
        if token not in named_entry_points[path]:
            have = sorted(named_entry_points[path])
            problems.append("%s:%d: requests entry point '%s' of %s:%s, which is not the first word of a code span "
                            "in any of its headings -- %s"
                            % (rel, line, token, CORE_NAME, name,
                               "its entry points: " + either(have, "and") if have else "it has none"))
    consumers = set(scan_files(root, DEPENDENT_PLUGIN_RELS))
    for path in sorted(consumers | set(scan_files(root, [CORE_PLUGIN_REL]))):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        cited = set()
        blocks = blocks_of(text)
        # The out-of-file citation check's unit: each `##` section whose text requests a declared entry
        # point, `args: "<ref> <entry>"`; `asked[ref]` maps each such section's heading line to the
        # entries it requests, and `whole_in` holds each (ref, section) a whole load has been made in.
        section_of, asked, whole_in = level2_sections(text), {}, set()
        for joined, at, _ in blocks:
            for m in CALL.finditer(joined):
                toks, sec = m.group(1).split(), section_of.get(line_at(at, m.start()))
                if len(toks) == 2 and toks[1] in declared.get(toks[0], ()) and sec is not None:
                    asked.setdefault(toks[0], {}).setdefault(sec, set()).add(toks[1])
        first_asked = {r: {e: min(s for s, es in secs.items() if e in es) for e in set().union(*secs.values())}
                       for r, secs in asked.items()}
        # Where the file first loads each such reference whole, as (block, sentence): after the first section
        # requesting an entry point, a citation the file does not hold fails until then.
        first_whole = {}
        for bi, (joined, at, table) in enumerate(blocks):
            for m in CALL.finditer(joined):
                t = m.group(1).split()
                if t and t[0] in asked and t[0] not in first_whole and loads_whole(t, t[0], declared[t[0]]):
                    first_whole[t[0]] = (bi, next(i for i, (a, b) in enumerate(sentences(joined, table))
                                                  if a <= m.start() < b))
        for r, secs in asked.items():
            for es in secs.values():
                for e in es:
                    entry_census[(r, e)][0] += 1
        for bi, (joined, at, table) in enumerate(blocks):
            groups = {}   # (sentence, ref) -> one citation: its line, the parts it requests, ...
            spans = sentences(joined, table)

            def group(offset, name):
                s = next(i for i, (a, b) in enumerate(spans) if a <= offset < b)
                return groups.setdefault((s, name), {"line": line_at(at, offset), "parts": [], "bad": 0,
                                                     "whole_call": False})

            def request(offset, name, part):
                g, ref = group(offset, name), refs[name]
                if part == "index" or (part in ref.parts and not ref.parts[part].private
                                       and not ref.parts[part].helper):
                    g["parts"].append(part)
                    return
                g["bad"] += 1
                if part in ref.parts and ref.parts[part].helper:
                    problems.append("%s:%d: requests part '%s' of %s:%s, which is a helper -- it comes only with a part "
                                    "that brings it: %s" % (rel, line_at(at, offset), part, CORE_NAME, name,
                                                          either(carriers(refs, ref, part))))
                elif part in ref.parts:
                    problems.append("%s:%d: requests part '%s' of %s:%s, which is private -- never requestable"
                                    % (rel, line_at(at, offset), part, CORE_NAME, name))
                else:
                    problems.append("%s:%d: requests part '%s' of %s:%s, which has no such part -- requestable: %s"
                                    % (rel, line_at(at, offset), part, CORE_NAME, name,
                                       ", ".join([p.name for p in ref.public()] + ["index"])))

            for m in CALL.finditer(joined):
                toks = m.group(1).split()
                if not toks or toks[0].startswith("<"):
                    continue
                if toks[0] not in refs:
                    if len(toks) > 1:
                        entry_request(rel, line_at(at, m.start()), toks[0], toks[1])
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
                if m.group(1) in refs and not m.group(2).startswith("<") and path not in consumers:
                    request(m.start(), m.group(1), m.group(2))
                elif path in consumers and not m.group(2).startswith("<"):
                    # `${CLAUDE_PLUGIN_ROOT}` is the reading plugin's root, and only workflows-core's holds
                    # reference-parts/: outside it, a part file read by path opens nothing.
                    if m.group(1) in refs:
                        group(m.start(), m.group(1))["bad"] += 1
                    problems.append("%s:%d: reads %s/%s/%s.md by path outside %s, whose plugin root alone holds "
                                    "%s/ -- load it with `Skill(skill: \"%s\", args: \"%s %s\")`"
                                    % (rel, line_at(at, m.start()), PARTS_DIR, m.group(1), m.group(2), CORE_NAME,
                                       PARTS_DIR, LOADER_SKILL, m.group(1), m.group(2)))
            for pat in (TOKEN, WHOLE_PATH):
                for m in pat.finditer(joined):
                    if m.group(1) in refs:
                        group(m.start(), m.group(1))

            # A § reference belongs to a reference citation, split or not: the one a `§4 of` or
            # `§ <Name> of` phrase names (the name a section of that reference); else the nearest
            # before it in its sentence; else the first after it there (a rule named before its
            # parenthetical call); else, in a sentence citing nothing, the nearest in an earlier
            # sentence of the paragraph; else to none, and names nothing. Each citation is
            # (offset, the split reference it cites or None, the reference file it resolves to).
            own_refs = root / Path(rel).parts[0] / Path(rel).parts[1] / REF_DIR
            cites = [(m.start(), m.group(1) if m.group(1) in refs else None, core_refs / (m.group(1) + ".md"))
                     for m in ANY_CALL.finditer(joined)]
            cites += [(m.start(), m.group(2) if m.group(1) == CORE_NAME and m.group(2) in refs else None,
                       plugins_dir / m.group(1) / REF_DIR / (m.group(2) + ".md"))
                      for m in ANY_TOKEN.finditer(joined) if is_reference(m.group(1), m.group(2))]
            cites += [(m.start(), SKILL_REFERENCES[m.group(1)] if SKILL_REFERENCES[m.group(1)] in refs else None,
                       core_refs / (SKILL_REFERENCES[m.group(1)] + ".md"))
                      for m in SKILL_CALL.finditer(joined) if m.group(1) in SKILL_REFERENCES]
            for m in ANY_PATH.finditer(joined):
                key = m.group(2) if m.group(1) == REF_DIR else m.group(2).split("/")[0]
                where = own_refs if m.group(1) == REF_DIR and (own_refs / (m.group(2) + ".md")).is_file() else core_refs
                cites.append((m.start(), key if key in refs else None, where / (key + ".md")))
            cites.sort(key=lambda c: c[0])
            names = [[(a + o, rd, sec) for o, rd, sec in names_in(joined[a:b])] for a, b in spans]

            def owner_of(s, offset):
                """The citation a § reference at `offset` in sentence `s` belongs to, as (offset, the
                split reference it cites or None, the reference file it resolves to); None for none."""
                a, b = spans[s]
                after = [c for c in cites if offset <= c[0] < b]
                if after:
                    named = OF_NAME.match(joined, offset, after[0][0])
                    if OF_NUMBER.match(joined, offset, after[0][0]) or (
                            named and is_section(after[0][1], after[0][2], named.group(1))):
                        return after[0]
                before = [c for c in cites if a <= c[0] < offset]
                earlier = [c for c in cites if c[0] < a]
                return before[-1] if before else after[0] if after else earlier[-1] if earlier else None

            def owner(s, offset):
                c = owner_of(s, offset)
                return NO_CITATION if c is None else c[1]

            # The out-of-file citation check (the docstring's "OUT-OF-FILE CITATIONS"). In a `##` section
            # requesting a declared entry point, the loader serves a citation of a section that entry's
            # file holds from the file, and reads the whole reference for any other: so each sentence
            # there citing the reference -- or carrying a § reference that belongs to a citation of it --
            # is judged by its own § references, and passes where each is held, or where a whole load of
            # the reference is made at or before it in the section. Before the first section requesting
            # the entry point, a citation loads the whole reference ahead of the request, so a sentence
            # citing it there fails unless it loads the whole reference itself. After that section, until
            # the file first loads the reference whole, a citation of a section the file holds is a lookup
            # the file's text in the conversation serves, and any other loads the whole reference: so each
            # such sentence outside every requesting section is judged as one inside, against the file
            # already read, and passes from that first whole load on.
            here = at[0][1]
            here_sec = section_of.get(here)
            for r in sorted(asked):
                inside = asked[r].get(here_sec)
                # Early only before the file's first request of any entry point of r: once one file is
                # read, a citation is judged against the files already requested, whatever comes later.
                early = [] if inside or any(first < here for first in first_asked[r].values()) else \
                    sorted(first_asked[r])
                late = [] if inside or early else sorted(e for e, first in first_asked[r].items() if first < here)
                if not inside and not early and not late:
                    continue
                rpath, decls = core_refs / (r + ".md"), declared[r]
                for u, (a, b) in enumerate(spans):
                    if late and r in first_whole and (bi, u) > first_whole[r]:
                        break
                    calls = [(m.start(), m.group(1).split()) for m in CALL.finditer(joined) if a <= m.start() < b]
                    whole = any(loads_whole(t, r, decls) for _, t in calls if t)
                    requests = {o for o, t in calls if len(t) == 2 and t[0] == r and t[1] in decls}
                    ours = [c for c in cites if a <= c[0] < b and c[2] == rpath]
                    if early:
                        direct = [c for c in ours if c[0] not in requests]
                        if not direct:
                            continue
                        for e in early:
                            entry_census[(r, e)][1] += 1
                        if not whole:
                            problems.append("%s:%d: cites %s:%s before the first `##` section requesting %s, so a run "
                                            "loads the whole reference ahead of that request -- load the whole reference "
                                            "in this sentence, or reword it so it implies no load"
                                            % (rel, line_at(at, direct[0][0]), CORE_NAME, r,
                                               either(["%s %s" % (r, e) for e in early])))
                        continue
                    numbers = []   # (offset, §) of each numbered § reference belonging to a citation of r
                    for offset, readings, section in names[u]:
                        c = owner_of(u, offset) if section else None
                        num = re.fullmatch(r"§(\d+(?:\.\d+)*)", readings[0]) if c and c[2] == rpath else None
                        if num:
                            numbers.append((offset, num.group(1)))
                    if not ours and not numbers:
                        continue
                    holders = inside or late
                    for e in holders:
                        entry_census[(r, e)][1] += 1
                    if whole and inside:
                        whole_in.add((r, here_sec))
                    if whole or (r, here_sec) in whole_in:
                        continue
                    where = ("in a section that reads only that file" if inside else
                             "after the first `##` section requesting %s and before any load of the whole reference in "
                             "this file, so a run loads the whole reference here" % either(["%s %s" % (r, e) for e in late]))
                    tail = (", which the %s file does not hold, %s -- name a section it holds, load the whole reference "
                            "at or before this sentence, or reword it so it implies no load"
                            % (" or ".join(sorted(holders)), where))
                    said = set()
                    for offset, n in numbers:
                        if n not in said and not any(holds_cited(decls[e], n, joined[a:b]) for e in holders):
                            said.add(n)
                            problems.append("%s:%d: cites %s:%s §%s%s" % (rel, line_at(at, offset), CORE_NAME, r, n, tail))
                    if ours and not numbers and not requests:
                        problems.append("%s:%d: cites %s:%s with no section%s"
                                        % (rel, line_at(at, ours[0][0]), CORE_NAME, r, tail))

            def read(name, s):
                """The parts sentence `s` names rules of `name`'s in -- every span, and each §
                reference that belongs to a citation of `name` -- as (public parts, private matches)."""
                ref, hits, private = refs[name], [], []
                for offset, readings, section in names[s]:
                    if section and owner(s, offset) != name:
                        continue
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

            def label(ref, part):
                """A lacking part as a failure names it: a helper by the parts that bring it, which a run
                loads instead, as the index does."""
                return part if not ref.parts[part].helper else "%s (helper %s)" % (
                    either(carriers(refs, ref, part), quote=""), part)

            # Each citation is judged on its own sentence. A run reads a sentence whole before it
            # acts, so the calls of one sentence are one load, in any order: an explicit request is
            # judged against the loads of that sentence's calls -- each part with its needs and the
            # always part, or everything where one of them loads the whole reference -- and never
            # against another sentence's. Each citation also records the load the run makes at its
            # sentence, for the sentences after it: `loads[name]` is [(sentence, the parts held, or
            # None for the whole reference, or "index" for a lookup)]. An explicit call is a load
            # whatever its sentence names; a bare citation loads the parts it is placed on, and one
            # naming no rule the index holds loads the whole reference, which is what the preamble
            # sends it to (`args: "<name>"`).
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
                hits, private = read(name, s)
                if private:
                    private_fails(private, g["line"], name)
                    continue
                if g["parts"]:
                    lacking = [] if g["whole_call"] else [h for h in hits if h not in held]
                    if lacking and "index" not in g["parts"]:
                        # An `index` request is a lookup: the run loads what the index then names.
                        problems.append("%s:%d: requests part %s of %s:%s, but its sentence names a rule of part %s, "
                                        "which that load does not hold"
                                        % (rel, g["line"], ", ".join(g["parts"]), CORE_NAME, name,
                                           "; ".join(label(ref, h) for h in lacking)))
                    else:
                        census[name][0] += len(set(g["parts"]))
                    continue
                if g["bad"]:
                    continue
                if g["whole_call"] or not hits:
                    if not g["whole_call"]:
                        made.append((s, None))   # named no rule: the preamble loads it whole
                    census[name][1].append("%s:%d" % (rel, g["line"]))
                    continue
                # A bare citation is placed on the part of each rule its sentence names: the
                # preamble has the run load the part that holds each rule before applying it.
                made.append((s, held_by(ref, hits)))
                census[name][0] += len(hits)

            def holds(name, u, part):
                """Whether a load of `name` made at or before sentence `u` holds `part`."""
                return any(h is None or h == "index" or part in h for s, h in loads[name] if s <= u)

            # Where a paragraph cites a split reference, in any form, each of its sentences may apply
            # "its" rule leaning on the paragraph's loads. A name such a sentence carries that its own
            # citation's reference holds was judged above, as that citation, and so was every §
            # reference in a sentence that cites anything, which belongs to a citation in that sentence. A
            # § reference in a sentence citing nothing belongs to the nearest citation in an earlier
            # sentence, and where that is a split reference's, it is read against that reference's loads
            # alone. Any other name a cited split reference's index holds is read against every split
            # reference the paragraph cites whose index holds it, and passes where a load of any of them
            # made AT OR BEFORE the sentence holds it -- never a later one, erring toward failing. A
            # paragraph making no part request is read too: first refused as firing only on correct
            # prose, this reading, re-measured on the tree before the rule-by-rule reading, fired six
            # times, four of them on gaps that reading found (docs/maintainers/rationale.md, "reference-parts").
            for u, (a, b) in enumerate(spans if loads else ()):
                own = {n for (i, n) in groups if i == u}
                lacking, private = {}, {}
                bare = not any(a <= c[0] < b for c in cites)
                for offset, readings, section in names[u]:
                    if section:
                        n = owner(u, offset) if bare else None
                        hit = n in loads and next(((r, refs[n].index[norm(r)]) for r in readings
                                                   if norm(r) in refs[n].index), None)
                        if hit and (refs[n].parts[hit[1]].private or not holds(n, u, hit[1])):
                            if refs[n].parts[hit[1]].private:
                                private.setdefault(n, []).append(hit)
                            elif hit[1] not in lacking.setdefault(n, []):
                                lacking[n].append(hit[1])
                        continue
                    if any(norm(r) in refs[n].index for n in own for r in readings):
                        continue
                    found = [(n, hit) for n in sorted(loads) if n not in own
                             for hit in [next(((r, refs[n].index[norm(r)]) for r in readings
                                               if norm(r) in refs[n].index), None)] if hit]
                    if not found:
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
                                        % (rel, line_at(at, a), CORE_NAME, n,
                                           "; ".join(label(refs[n], h) for h in lacking[n])))
        if cited and path in consumers and preamble not in paragraphs(text):
            problems.append("%s: cites %s but does not carry the load-by-part preamble as a paragraph of its own"
                            % (rel, ", ".join("%s:%s" % (CORE_NAME, n) for n in sorted(cited))))

    for n in split:
        if consumer_cites[n] == 0:
            problems.append("%s:%s is declared split, but no file in the dependent plugins' commands/, agents/ or "
                            "references/ cites it -- the scan found nothing" % (CORE_NAME, n))
    # Fail-closed, as for a split reference no consumer cites: an entry point no section requests runs
    # none of the out-of-file check, which would pass on nothing.
    for (r, e), (sections_n, _) in entry_census.items():
        if sections_n == 0:
            problems.append("%s:%s declares a file for entry point `%s`, but no `##` section of a scanned file requests "
                            "it, `args: \"%s %s\"` -- the out-of-file check found nothing to judge" % (CORE_NAME, r, e, r, e))
    for p in problems:
        print("ERROR " + p)
    for n in split:
        placed, whole = census[n]
        print("%s:%s: placed %d, whole %d" % (CORE_NAME, n, placed, len(whole)))
        if verbose:
            for loc in whole:
                print("WHOLE %s: %s:%s" % (loc, CORE_NAME, n))
    print("entry-point requests on references that do not load by part: %d, %d distinct"
          % (len(entry_requests), len(set(entry_requests))))
    for (r, e), (sections_n, cites_n) in entry_census.items():
        print("entry-point file %s %s: %d request section(s), %d citation(s) checked" % (r, e, sections_n, cites_n))
    if problems:
        print("reference-parts check-citations: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("reference-parts check-citations: PASS -- %d split reference(s)" % len(split))
    return 0


def first_question(lines):
    """The 1-based line of a command's first question, or None: the first line, fenced or not, holding
    `choices:`, holding both `phase-handoff` and `§4.3`, or stating a prompt of 2–4 options -- `2–4 options`
    on a line that names no `choices` array, whose rule such a line states instead."""
    for n, line in enumerate(lines, 1):
        if QUESTION_ARRAY in line or all(w in line for w in QUESTION_HANDOFF) or (
                QUESTION_PROMPT.search(line) and not QUESTION_RULE.search(line)):
            return n
    return None


def question_steps(text):
    """The first line of each question-rules step in a command: a paragraph or list item outside every
    fenced block that opens, its list marker dropped, with the step's lead and holds the loader call
    `args: "escalation-rules core"`. A fenced one is printed, not run, so it is none."""
    fenced, fences = set(), Fences()
    for n, line in enumerate(text.splitlines(), 1):
        if fences.step(line):
            fenced.add(n)
    out = []
    for joined, at, table in blocks_of(text):
        n = at[0][1]
        if table or n in fenced or not joined.startswith(QUESTION_STEP_LEAD):
            continue
        if any(" ".join(m.group(1).split()) == QUESTION_STEP_ARGS for m in CALL.finditer(joined)):
            out.append(n)
    return out


def cmd_check_questions(root, verbose):
    problems, asking, loading = [], 0, 0
    for path in scan_files(root, QUESTION_PLUGIN_RELS, (QUESTION_DIR,)):
        text = path.read_text(encoding="utf-8")
        first = first_question(text.splitlines())
        if first is None:
            continue
        asking += 1
        name = path.relative_to(root).as_posix()
        steps = question_steps(text)
        if steps and steps[0] < first:
            loading += 1
        else:
            problems.append("%s:%d: asks the user a question before its %s step -- add the step before this line"
                            % (name, first, QUESTION_STEP_LEAD))
        if verbose:
            print("ASKS %s: step at line %s, first question at line %d" % (name, steps[0] if steps else "none", first))
    if not asking:
        problems.append("no command under %s presents a choice list -- the scan matched nothing, and a gate that "
                        "matched nothing proves nothing when it passes"
                        % either(["%s/%s/" % (r, QUESTION_DIR) for r in QUESTION_PLUGIN_RELS], quote=""))
    for p in problems:
        print("ERROR " + p)
    print("question rules: %d command(s) present a choice list, %d load the rules first" % (asking, loading))
    if problems:
        print("reference-parts check-questions: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("reference-parts check-questions: PASS -- %d command(s) load the question rules before their first question"
          % loading)
    return 0


# ---------------------------------------------------------------- selftest
# One fixture tree per case under scripts/fixtures/reference-parts/<case>/, laid out as the repo
# is, and run through the CLI with --root. A step asserts the exit code AND what it must print;
# a red step also counts its ERROR lines, since a fixture red for some other reason would hold
# the exit code at 1 just the same. Each red fixture carries one defect, or one per message it
# asserts. The generated trees in the green fixtures were written by hand from the layout above
# before the generator existed, so freshness there is a test of the generator's output. After a
# deliberate change to that layout, rerun `generate --root scripts/fixtures/reference-parts/<case>`
# on each green fixture and read the diff -- never on stale_generated or entry_stale, each stale on
# purpose, and on stale_helper_file only on a copy, keeping the wording.md it leaves on purpose. The
# post-checks on minimal, helper_part, cross_file_bundle and source_order pin the part files' own
# lines, and entry_minimal's the entry-point file's, which a regenerated fixture cannot.
class Step:
    def __init__(self, argv, want_exit, must_print=(), errors=None, flags=None, on_copy=False, post=None, absent=(),
                 pre=None):
        self.argv, self.want_exit, self.must_print = list(argv), want_exit, list(must_print)
        self.errors, self.flags, self.on_copy, self.post = errors, flags, on_copy, post
        self.absent, self.pre = list(absent), pre


def _rewrite(rel, *pairs):
    """A pre-step for an on-copy step: in the copy's `rel`, replace each `old` -- found exactly once --
    with its `new`, in order."""
    def edit(root):
        path = root / rel
        text = path.read_text(encoding='utf-8')
        for old, new in pairs:
            if text.count(old) != 1:
                return '%s holds %r %d time(s), not once' % (rel, old, text.count(old))
            text = text.replace(old, new)
        path.write_text(text, encoding='utf-8')
        return None
    return edit


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


def _no_file(rel):
    """A post-check: the tree holds no file at `rel`."""
    def check(_fixture, root):
        return '%s exists, and no declaration may produce it' % rel if (root / rel).exists() else None
    return check


def _entry_files(want):
    """A post-check: entry_files gives `want`, {reference: {entry: (holds, partial, regions)}}."""
    def check(_fixture, root):
        got = {r: {e: (d.holds, d.partial, d.regions) for e, d in es.items()} for r, es in entry_files(root).items()}
        return None if got == want else 'entry_files gives %r, not %r' % (got, want)
    return check


def _entry_files_raise(*words):
    """A post-check: entry_files raises ValueError naming each of `words`, never returning a declaration
    that check-parts fails."""
    def check(_fixture, root):
        try:
            got = entry_files(root)
        except ValueError as e:
            missing = [w for w in words if w not in str(e)]
            return 'entry_files raised, but never named %s' % missing if missing else None
        return 'entry_files returned %r on a declaration check-parts fails' % sorted(got)
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
ER = 'plugins/workflows-core/skills/reference/entry-files.md'
EPATH = (SK + ": the paragraph opening with the entry list lacks \"Each one's file is "
         "`${CLAUDE_PLUGIN_ROOT}/reference-parts/<the reference>/<the entry point>.md`.\" -- the entry-point rules "
         "name no path, so this sentence is where a run learns where each file is")
ETRIGGER = (SK + ': the paragraph opening with the entry list lacks "A request on one of their references, with or '
            'without a second argument, reads the entry-point rules, '
            '`${CLAUDE_PLUGIN_ROOT}/skills/reference/entry-files.md`, with or before its other reads, unless their '
            'text is in this conversation word for word, and follows them." -- it is the one sentence that has a '
            'request on `gamma` read the entry-point rules')
E = 'plugins/workflows-core/references/epsilon.md'
QA = 'plugins/dev-workflows/commands/ask.md'
QSTEP = ('**Load the question rules.** Load `escalation-rules core` now, with `Skill(skill: "workflows-core:reference", '
         'args: "escalation-rules core")`, before this run asks the user anything: every question it asks follows '
         'them — two to four options, presented verbatim with the `(Recommended)` marker where one is recommended, '
         'and a selection that carries no text.')
CASES = [
    # The cited heading is an italic span wrapped across two lines and the preamble is
    # hard-wrapped, as command files are; pickers holds a fenced `# Resume` line, no heading; and
    # notes.md, which is not split, quotes the marker syntax in code spans.
    ('minimal', 'one always part, one part, one consumer citing it by heading', [
        Step(['check-parts'], 0, ['check-parts: PASS -- 1 split reference(s), 0 entry file(s), 3 generated file(s) fresh'],
             errors=0, flags=0, post=[
            _order(G + '/alpha/pickers.md', ['# Alpha rules — part pickers', 'This file holds parts `core` and `pickers`.',
                                             '`${CLAUDE_PLUGIN_ROOT}` in this file']),
            _order(G + '/alpha/core.md', ['# Alpha rules — part core', 'This file holds part `core`.'])]),
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
        Step(['check-parts'], 1, [A + ":5: part 'pickers': unknown word 'need=beta/detail' -- always, private, helper or needs=",
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
    # alpha's block names a part index, a part outside [a-z0-9-], a part twice and an unclosed alias,
    # and its body opens a second block; beta's block follows a sentence, not its H1. generate
    # refuses the tree and writes nothing.
    ('declaration_line_errors', 'every declaration-line defect is reported, and generate writes nothing on any', [
        Step(['check-parts'], 1, [A + ":5: 'index' is not a part name -- lowercase letters, digits and dashes, never 'index'",
                                  A + ":6: 'Pickers' is not a part name",
                                  A + ":7: part 'core' is declared twice",
                                  A + ':8: an alias line is `alias <part> "<name>" ...`, every name quoted and non-empty',
                                  A + ': carries a second reference-parts declaration',
                                  'plugins/workflows-core/references/beta.md:3: the <!-- reference-parts declaration must '
                                  'directly follow the H1 line'], errors=6),
        Step(['generate'], 1, ['generate: FAIL -- 6 problem(s); nothing written'], errors=6, on_copy=True,
             post=[_unchanged]),
    ]),
    # alpha opens a region for a part it never declared; beta closes a region twice; gamma's last
    # region is never closed, so its lines would reach no part.
    ('region_errors', 'a region naming no declared part, a stray close and an unclosed region', [
        Step(['check-parts'], 1, [A + ":11: region 'ghost' names no declared part",
                                  'plugins/workflows-core/references/beta.md:10: <!-- /part --> closes no open region',
                                  "plugins/workflows-core/references/gamma.md:7: region 'core' is never closed"],
             errors=3),
    ]),
    # alpha's always part is private, a part owns no region, an alias names an undeclared part and one
    # a private part; beta's detail needs its private part.
    ('part_declaration_errors', 'always and private together, a part with no region, a bad alias and a private need', [
        Step(['check-parts'], 1, [A + ":4: part 'core' is marked always and private",
                                  A + ":6: part 'empty' has no region",
                                  A + ":8: alias names part 'ghost', which is not declared",
                                  A + ":9: alias names part 'maintainer', which is private",
                                  "plugins/workflows-core/references/beta.md:5: part 'detail' needs 'maintainer', which "
                                  "is private"], errors=5),
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
    ('missing_loader_skill', 'the loader skill is missing, so nothing names the split list', [
        Step(['check-citations'], 1, [SK + ': missing -- the loader skill must open a paragraph with "These references '
                                           'load by part: `alpha`."'], errors=1),
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
    # citing nothing names it after a pickers call, once as a span and once as a § heading.
    ('private_rule_cited',
     'a rule of a private part, named by an explicit citation, a bare one and a sentence citing nothing', [
        Step(['check-citations'], 1, [U + ":15: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings",
                                      U + ":17: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings",
                                      U + ":19: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings",
                                      U + ":21: names 'Why the pickers exist', in private part 'maintainer' of "
                                          "workflows-core:alpha -- text no part load brings"], errors=4),
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
    # the pickers rule; and a stops call, a bare citation naming no rule, which the preamble sends
    # to the whole reference, then the same sentence. Both hold.
    ('bare_citation_before_free_sentence',
     "a bare citation's parts hold a later sentence, and one naming no rule holds them all", [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 3, whole 1', 'check-citations: PASS'], errors=0),
    ]),
    # A paragraph making no part request is read like any other. Red: a bare stops citation, then a
    # sentence citing nothing that names a pickers rule as a reason, which no load at or before it
    # holds. Green beside it: the same shape with the reason's own citation, placed on pickers.
    ('paragraph_without_request_is_read', 'a paragraph making no part request is read for its sentences citing nothing', [
        Step(['check-citations'], 1, [U + ":15: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 3, whole 0'], errors=1),
    ]),
    # alpha and beta each hold a rule named Closed-vocabulary pickers, alpha in pickers, beta in
    # detail. Green: alpha's stops and beta's detail loaded, then the name in a sentence citing
    # nothing, which beta's load holds; and the name in a sentence citing beta, which is judged as
    # that citation, never against alpha's loads. Red: alpha's stops and beta's other loaded, then
    # the name, which neither load holds; and, after alpha's stops and a bare citation of beta placed
    # on detail, a §2 of beta's (its other part) leaning on that citation, which no load of beta holds.
    ('name_in_two_references', "a name is held by any loaded reference whose index holds it, and a sentence citing "
                               "one reference is that citation only for that reference's names", [
        Step(['check-citations'], 1, [U + ":19: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part pickers, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      U + ":19: a sentence citing workflows-core:beta no other way names a rule of "
                                          "part detail, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      U + ":21: a sentence citing workflows-core:beta no other way names a rule of "
                                          "part other, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 4, whole 0',
                                      'workflows-core:beta: placed 4, whole 0'], errors=3),
    ]),
    # A dependent plugin's agent reads a part file by path, which its own plugin root does not hold:
    # red, naming the loader call. A workflows-core agent reads one by path rightly, placed on
    # pickers; and reads one naming no part: red.
    ('part_path_outside_core', 'a part file read by path outside workflows-core fails; inside it, the path is a request', [
        Step(['check-citations'], 1, ['plugins/dev-workflows/agents/fixer.md:12: reads reference-parts/alpha/pickers.md '
                                      'by path outside workflows-core, whose plugin root alone holds reference-parts/ '
                                      '-- load it with `Skill(skill: "workflows-core:reference", args: "alpha pickers")`',
                                      "plugins/workflows-core/agents/core-fixer.md:9: requests part 'nosuch' of "
                                      "workflows-core:alpha, which has no such part",
                                      'workflows-core:alpha: placed 1, whole 0'], errors=2),
    ]),
    # alpha aliases §1 to pickers and §4 to stops; gamma is a core reference and delta a plugin's
    # own, neither split. Green: a §4 after a gamma call in a sentence that called alpha before it,
    # and in a later sentence; after a `workflows-core:gamma` token, a `dev-workflows:delta` token
    # and a `references/delta.md` path. Red: a §4 in a sentence citing nothing after a pickers
    # call, which belongs to that call and names alpha's stops rule; and a §4 right after one.
    ('section_belongs_to_nearest_citation',
     'a § reference belongs to the nearest reference citation before it, in its sentence or an earlier one', [
        Step(['check-citations'], 1, [U + ":25: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part stops, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      U + ":27: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part stops, which that load does not hold",
                                      'workflows-core:alpha: placed 6, whole 0'], errors=2),
    ]),
    # The same alpha and gamma. A § no citation precedes in its sentence belongs to the first
    # citation after it there. Green: a §1 before a pickers call; a §4 before a gamma call, then
    # a pickers call; and a §4 after a gamma call, then a pickers call, the citation before it
    # winning. Red: a §4 before a pickers call, which names alpha's stops rule; and the same after
    # a gamma call in an earlier sentence, since the citation after it in its own sentence wins.
    ('section_before_any_citation', 'a § with no citation before it in its sentence belongs to the first one after it', [
        Step(['check-citations'], 1, [U + ":17: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part stops, which that load does not hold",
                                      U + ":23: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part stops, which that load does not hold",
                                      'workflows-core:alpha: placed 3, whole 0'], errors=2),
    ]),
    ('section_in_sentence_citing_nothing', 'a § in a sentence citing nothing belongs to the nearest earlier citation', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 3, whole 0', 'check-citations: PASS'], errors=0),
    ]),
    # alpha aliases §4 to stops; model-routing/classification is a core reference, not split. Green:
    # a §4 after a `workflows-core:model-routing` skill call, which loads that reference. Red: a §4
    # after a `workflows-core:frames` skill call, no citation, so it leans on the pickers call.
    ('skill_call_cites_its_reference',
     "a skill's `skill:` token cites only a reference the skill map names; the loader cites by its args", [
        Step(['check-citations'], 1, [U + ":17: a sentence citing workflows-core:alpha no other way names a rule of "
                                          "part stops, which no load of it at or before that sentence in its "
                                          "paragraph holds",
                                      'workflows-core:alpha: placed 2, whole 0'], errors=1),
    ]),
    # dev-workflows' references/ holds a directory upgrade/ and a file upgrade/handoff.md. Green: a §4
    # after the `dev-workflows:upgrade/handoff` token, a reference file. Red: a §4 after the
    # `dev-workflows:upgrade` token, which names a command, so the §4 belongs to the pickers call.
    ('command_token_is_no_citation', 'a token is a citation only where its plugin holds that reference file', [
        Step(['check-citations'], 1, [U + ":17: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part stops, which that load does not hold",
                                      'workflows-core:alpha: placed 1, whole 0'], errors=1),
    ]),
    # alpha's marker part holds the heading The `(Recommended)` marker is unconditional. Green: a
    # bare italic and a bare bold citation of it, each placed. Red: a pickers call whose sentence
    # names it, which the failure says is part marker's.
    ('name_holding_code_span', 'a name holding a code span reads whole, and is placed on the part that holds it', [
        Step(['check-citations'], 1, [U + ":19: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part marker, which that load does not hold",
                                      'workflows-core:alpha: placed 2, whole 0'], errors=1),
    ]),
    # alpha's review part holds the heading On re-review, and pickers the shorter alias On. Green: a
    # bare `§ On re-review’s terms` (curly), and a review call's `§ On re-review's terms` (straight)
    # and `§ On re-review’s terms` (curly), each read as the section, never as the shorter On. Red: a
    # pickers call whose sentence names it, which the failure says is part review's.
    ('possessive_section_name', "a possessive § name (`§ <Name>'s`) is read as the section `<Name>`", [
        Step(['check-citations'], 1, [U + ":19: requests part pickers of workflows-core:alpha, but its sentence names a "
                                          "rule of part review, which that load does not hold",
                                      'workflows-core:alpha: placed 3, whole 0'], errors=1),
    ]),
    # alpha aliases §4, Stop rule and § Missing key to stops; gamma is a core reference, not split,
    # holding the heading Key dir not found, and so is delta, dev-workflows' own. Green, each after a
    # pickers call: `§4 of `workflows-core:gamma``, `§ Key dir not found of` it, and `§4 of` its path
    # -- each gamma's, ahead of the call before it; `§ Key dir not found of` delta's path and of
    # `dev-workflows:delta`, each delta's own file, never workflows-core's; and, after a gamma call,
    # `§ Key dir not found of `workflows-core:alpha``, `§ Stop rule of` it (an alias, no heading) and
    # `§ Missing key of` it (an alias written with its §), each placed on alpha's stops. Red: after a
    # gamma call, `§4 of` a pickers call; and, after a pickers call, a § with words between it and
    # "of" -- `§4 to every key of`, `§ Key dir not found to the keys of`, `§4 for each folder of` --
    # which position gives to the pickers call, each naming alpha's stops rule.
    ('section_of_citation', 'only `§N of <citation>`, or `§ <Name> of` it with <Name> its section, names that citation', [
        Step(['check-citations'], 1, [U + ":%d: requests part pickers of workflows-core:alpha, but its sentence names "
                                          "a rule of part stops, which that load does not hold" % n for n in (19, 23, 25, 27)]
             + ['workflows-core:alpha: placed 8, whole 0'], errors=4),
    ]),
    # alpha's pickers needs the helper wording, and review needs pickers, so both bring it. pickers.md
    # carries wording's text in source order and its holds line names wording as a helper, no
    # wording.md is generated, the index sends Wording to pickers or review, and the part list names
    # wording only as a helper. Green: a bare citation of *Wording*, and a pickers call naming it.
    # Red: a request naming the helper; a stops call naming *Wording*, which stops does not bring, its
    # failure naming the parts that do; and, after a stops call, a sentence citing nothing, then the
    # stops call's own sentence, each naming a pickers rule and *Wording*, every lacking entry named
    # and the entries separated by semicolons.
    ('helper_part', 'a helper part has no file, comes with the parts that bring it, and is never requested', [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, post=[
            _order(G + '/alpha/pickers.md', ['# Alpha rules — part pickers',
                                             'This file holds parts `core` and `pickers`, with helper part `wording`.',
                                             '`${CLAUDE_PLUGIN_ROOT}` in this file', '## Closed-vocabulary pickers',
                                             '## Wording', 'Helper text']),
            _order(G + '/alpha/review.md', ['This file holds parts `core`, `pickers` and `review`, with helper part '
                                            '`wording`.']),
            _order(G + '/alpha/index.md', ['- `Wording` → `pickers` or `review`', '- `pickers` — needs `wording`',
                                           'Helper parts', '`wording`.'], absent=['- `wording`', 'This file holds']),
            _no_file(G + '/alpha/wording.md')]),
        Step(['check-citations'], 1, [U + ":19: requests part 'wording' of workflows-core:alpha, which is a helper -- it "
                                          "comes only with a part that brings it: `pickers` or `review`",
                                      U + ":21: requests part stops of workflows-core:alpha, but its sentence names a "
                                          "rule of part pickers or review (helper wording), which that load does not hold",
                                      U + ":23: a sentence citing workflows-core:alpha no other way names a rule of part "
                                          "pickers; pickers or review (helper wording), which no load of it at or before "
                                          "that sentence in its paragraph holds",
                                      U + ":25: requests part stops of workflows-core:alpha, but its sentence names a "
                                          "rule of part pickers; pickers or review (helper wording), which that load does "
                                          "not hold",
                                      'workflows-core:alpha: placed 3, whole 0'], errors=4),
        Step(['generate'], 0, ['0 written, 0 removed'], errors=0, on_copy=True, post=[_unchanged]),
    ]),
    # helper_part's tree, with a wording.md left from when wording was requestable.
    ('stale_helper_file', 'a file left for a helper part is one no declaration produces', [
        Step(['check-parts'], 1, [G + '/alpha/wording.md: no declaration produces it -- generate removes it'], errors=1),
        Step(['generate'], 0, ['0 written, 1 removed'], errors=0, on_copy=True, post=[_no_file(G + '/alpha/wording.md')]),
    ]),
    # alpha's helper spare is brought by no part; beta marks its always part a helper; gamma marks a
    # helper private; epsilon's helper detail is brought only by delta, another reference.
    ('helper_declaration_errors', 'a helper its own reference does not bring, or one marked always or private, fails', [
        Step(['check-parts'], 1, [A + ":7: part 'spare' is a helper no requestable part of workflows-core:alpha brings",
                                  "plugins/workflows-core/references/beta.md:4: part 'core' is marked helper and always",
                                  "plugins/workflows-core/references/gamma.md:6: part 'hidden' is marked helper and private",
                                  "plugins/workflows-core/references/epsilon.md:5: part 'detail' is a helper no "
                                  "requestable part of workflows-core:epsilon brings -- its index has no part to send its "
                                  "rules to"], errors=4),
    ]),
    # Italic, bold, backticked, straight- and curly-quoted spans; §N; a § heading; a § alias; a
    # path citation inside workflows-core; a name after "e.g.". A § name reads longest first, so
    # `§ Key dir not found` is never the pickers alias `Key dir`. The three whole citations each
    # follow a sentence that names the rule -- one opening with a span, one ending inside one -- so
    # each is counted whole, and each sentence before it, naming a rule no load before it holds, fails.
    ('name_forms', 'each form a name takes places its citation, and only within its own sentence', [
        Step(['check-citations', '--verbose'], 1, [U + ":%d: a sentence citing workflows-core:alpha no other way names "
                                                       "a rule of part %s, which no load of it at or before that "
                                                       "sentence in its paragraph holds" % (n, p)
                                                   for n, p in ((33, 'pickers'), (35, 'pickers'), (37, 'stops'))]
             + ['workflows-core:alpha: placed 10, whole 3', 'WHOLE ' + U + ':33: workflows-core:alpha',
                'WHOLE ' + U + ':35: workflows-core:alpha', 'WHOLE ' + U + ':37: workflows-core:alpha'], errors=3),
    ]),
    # steps is a core reference that does not load by part: `specs-preflight` is a heading's whole code
    # span, `resolve-address` the first word of `resolve-address <ARG> [<KIND>]`, the second call
    # wrapped across two lines; `key-list` the second code span of its heading; and `emit-note` the
    # first word of ``emit-note `<KIND>` ``, a double-backtick span holding a single-backtick one. A
    # placeholder token names nothing to check.
    ('entry_point_named', "an entry-point request naming the first word of a heading's code span passes", [
        Step(['check-citations'], 0, ['entry-point requests on references that do not load by part: 4, 4 distinct',
                                      'check-citations: PASS'], errors=0),
    ]),
    # The same steps, with a section The shortlist, a fenced `## `fenced-step`` line and the double-backtick
    # span ``emit-note `kind` ``. Beside a green `specs-preflight`: a section's name, whose heading has no
    # code span; `resolve`, a prefix of an entry point; `run`, a word of a heading outside its code span;
    # a heading inside a fence; and `kind`, a word inside a double-backtick span, never its first.
    ('entry_point_unnamed', 'an entry-point request naming no first word of a heading code span fails', [
        Step(['check-citations'], 1, [U + ":%d: requests entry point '%s' of workflows-core:steps, which is not the first "
                                          "word of a code span in any of its headings -- its entry points: "
                                          "`emit-note`, `resolve-address` and `specs-preflight`" % (n, t)
                                      for n, t in ((23, 'shortlist'), (25, 'resolve'), (27, 'run'), (29, 'fenced-step'),
                                                   (31, 'kind'))]
             + ['entry-point requests on references that do not load by part: 6, 6 distinct'], errors=5),
    ]),
    ('renamed_heading_reported', 'a citation of a renamed heading passes as whole, and --verbose names it', [
        Step(['check-citations'], 0, ['workflows-core:alpha: placed 0, whole 1'], errors=0, absent=['WHOLE ']),
        Step(['check-citations', '--verbose'], 0, ['WHOLE ' + U + ':15: workflows-core:alpha'], errors=0),
    ]),
    ('positional_flagged', '"the next section" inside a part is flagged, never failed', [
        Step(['check-parts'], 0, ['FLAG ' + A + ':19: the next section', 'check-parts: PASS'], errors=0, flags=1),
    ]),
    # review.md carries alpha's text, then beta's always part and detail -- never beta's other -- and
    # its holds line names both references' parts.
    ('cross_file_bundle', "a part needing another reference's part carries it after a Bundled from line", [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, post=[
            _order(G + '/alpha/review.md',
                   ["This file holds parts `core` and `review`, and `workflows-core:beta`'s parts `core` and `detail`.",
                    'Alpha core: the station rule.', 'Alpha review:', 'Bundled from workflows-core:beta, part detail:',
                    'Beta core: the orchestrator triages.', 'Beta detail:'], absent=['Beta other'])]),
    ]),
    ('source_order', 'a part owning two regions with a needed part between them assembles in source order', [
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, post=[
            _order(G + '/alpha/a.md', ['This file holds parts `core`, `a` and `b`.', 'Order one', 'Order two',
                                       'Order three', 'Order four']),
            _order(G + '/alpha/b.md', ['This file holds parts `core` and `b`.', 'Order one', 'Order three'],
                   absent=['Order two', 'Order four']),
            # A heading starting with a number and holding a code span is one inert code span.
            _order(G + '/alpha/index.md', ['- ``2. The `second` half`` → `a`'])]),
    ]),
    # Entry-point files. Each tree is minimal's, with gamma, a reference that does not load by part,
    # declaring entry check-it: §1 and §3 whole, §4.0 in part. Its regions hold a scope line before §1,
    # §1, §3 -- whose §3.1 says "above", flagged, and whose §3.2 holds a fenced `## 4.` line, no heading --
    # and §4.0's heading and its *Never infer* rule; §2, whose "below" is in no region and never flagged,
    # and the rest of §4 lie outside every region, so check-it.md holds neither.
    ('entry_minimal', 'an entry-point file holds its regions in source order, under its own title and holds line', [
        Step(['check-parts'], 0, ['FLAG plugins/workflows-core/references/gamma.md:28: above',
                                  'check-parts: PASS -- 1 split reference(s), 1 entry file(s), 4 generated file(s) fresh'],
             errors=0, flags=1, post=[
            _order(G + '/gamma/check-it.md',
                   ['# Gamma steps — entry point check-it',
                    'This file holds entry point `check-it` of `gamma`: §1 and §3, and in part §4.0 ("never infer"). Any '
                    'other section is in the whole reference: `Skill(skill: "workflows-core:reference", args: "gamma")`. '
                    'This file is 36 lines long.',
                    '`${CLAUDE_PLUGIN_ROOT}` in this file', 'Scope: the steps', '## 1. Hard rules',
                    '## 3. `check-it` — the entry point', '## 4. Not a heading', '### 4.0 The downstream classes',
                    '*Never infer'],
                   absent=['`make-it`', '## 4. Reporting', 'Each artifact is in one class', '<!-- entry', '<!-- /entry']),
            _entry_files({'gamma': {'check-it': (['1', '3'], {'4.0': ['never infer']}, [(9, 16), (24, 38), (44, 46)])}})]),
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 1 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
        Step(['generate'], 0, ['0 written, 0 removed'], errors=0, on_copy=True, post=[_unchanged]),
    ]),
    # entry_minimal's tree with a second entry point, make-it, holding §1 and §2: §1 lies in one region
    # naming both entries, so each file holds it. The consumer requests check-it in Phase 0 and make-it
    # in Phase 2, and between them cites §1, which check-it's file holds: a run has read that file by
    # then, so the sentence is judged against it, and make-it's later request does not make it early.
    ('entry_shared_region', 'a region naming two entries puts its lines in both files; a citation after the first '
                            'request is judged against the files already requested', [
        Step(['check-parts'], 0, ['FLAG plugins/workflows-core/references/gamma.md:25: below',
                                  'FLAG plugins/workflows-core/references/gamma.md:33: above',
                                  'check-parts: PASS -- 1 split reference(s), 2 entry file(s), 5 generated file(s) fresh'],
             errors=0, flags=2, post=[
            _order(G + '/gamma/make-it.md',
                   ['# Gamma steps — entry point make-it',
                    'This file holds entry point `make-it` of `gamma`: §1 and §2. Any other section is in the whole '
                    'reference: `Skill(skill: "workflows-core:reference", args: "gamma")`. This file is 16 lines long.',
                    '## 1. Hard rules', '2. `check-it` is fatal by design.', '## 2. `make-it` — the producer'],
                   absent=['Scope: the steps', '## 3. `check-it`', '<!-- entry', '<!-- /entry']),
            _entry_files({'gamma': {'check-it': (['1', '3'], {'4.0': ['never infer']},
                                                 [(10, 12), (16, 19), (29, 43), (49, 51)]),
                                    'make-it': (['1', '2'], {}, [(16, 19), (23, 25)])}})]),
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked',
                                      'entry-point file gamma make-it: 1 request section(s), 1 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
        Step(['generate'], 0, ['0 written, 0 removed'], errors=0, on_copy=True, post=[_unchanged]),
    ]),
    # entry_shared_region's tree, make-it's region naming an entry no line declares beside it.
    ('entry_region_list_undeclared', 'a region naming several entries names only declared ones', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:22: region 'nope' names no declared "
                                  "entry"], errors=1),
    ]),
    # entry_shared_region's tree, its shared region naming make-it twice.
    ('entry_region_names_twice', 'a region names each entry once', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:15: region names 'make-it' twice -- "
                                  "an entry region names each entry once"], errors=1),
    ]),
    # entry_minimal's tree, its consumer requesting nothing: no scanned file requests check-it, so the
    # out-of-file check judges nothing -- which fails, closed, as a split reference no consumer cites does.
    ('entry_unrequested', 'a declared entry point that no scanned file requests fails', [
        Step(['check-citations'], 1, ["workflows-core:gamma declares a file for entry point `check-it`, but no `##` "
                                      "section of a scanned file requests it, `args: \"gamma check-it\"` -- the "
                                      "out-of-file check found nothing to judge",
                                      'entry-point file gamma check-it: 0 request section(s), 0 citation(s) checked'],
             errors=1),
    ]),
    # check-it.md lacks §3.1's line; generate repairs it.
    ('entry_stale', 'an entry-point file that differs from its regions is stale; generate repairs it', [
        Step(['check-parts'], 1, [G + '/gamma/check-it.md: stale -- differs from what generate builds from '
                                  'plugins/workflows-core/references/gamma.md'], errors=1),
        Step(['generate'], 0, ['1 written, 0 removed'], errors=0, on_copy=True),
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, on_copy=True),
    ]),
    # gamma declares entry nope, whose regions hold §1; its only entry point is make-it.
    ('entry_not_entry_point', 'an entry declaration naming no entry point of its reference fails', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:4: entry 'nope' is not an entry point of "
                                  "workflows-core:gamma -- not the first word of a code span in any of its headings; its "
                                  "entry points: `make-it`"], errors=1),
        Step(['check-citations'], 1, ["plugins/workflows-core/references/gamma.md:4: entry 'nope' is not an entry point",
                                      'fix the declarations first'], errors=1, post=[_entry_files_raise("entry 'nope'")]),
    ]),
    # gamma holds §3 whole, but a line of §3.2, after a fenced `## 4.` line, lies outside every region.
    ('entry_section_not_covered', 'a line of a section held whole outside every region of its entry fails', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:25: §3 is held whole by entry 'check-it', "
                                  "but this line of it lies in no `check-it` region"], errors=1),
    ]),
    # gamma holds §4.0 in part by "never infer", which §4.0 holds only outside its check-it region.
    ('entry_partial_phrase_missing', "a phrase of a section held in part that no region text of its entry holds fails", [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:5: §4.0 is held in part by entry 'check-it', "
                                  "but no `check-it` region in it holds \"never infer\""], errors=1),
    ]),
    # entry_minimal's gamma, holding §5 in part by "rule 2" too: its region in §5 holds the section's opening
    # line, which mentions rule 2, while the rule's own item, `2.`, lies outside every region. On a copy, the
    # item in a region of its own is held, and the file regenerated from it passes.
    ('entry_partial_rule_mention', 'a phrase naming a numbered rule is held by the rule\'s own item, not a mention', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:6: §5 is held in part by entry 'check-it', "
                                  "but no `check-it` region in it holds \"rule 2\" -- a phrase naming a numbered rule is "
                                  "held only by the rule's own item, `2.`, never by a mention of it"], errors=1),
        Step(['generate'], 0, ['1 written, 0 removed'], errors=0, on_copy=True,
             pre=_rewrite('plugins/workflows-core/references/gamma.md',
                          ('2. A consumer executes `check-it` before its first scan.\n',
                           '<!-- entry: check-it -->\n2. A consumer executes `check-it` before its first scan.\n'
                           '<!-- /entry -->\n'))),
        Step(['check-parts'], 0, ['check-parts: PASS'], errors=0, on_copy=True),
    ]),
    ('entry_skill_list_mismatch', "the loader's entry list names an entry point no declaration gives a file", [
        Step(['check-citations'], 1, [SK + ': no paragraph opens with the entry list the declarations give, "These entry '
                                           'points read their own file: `gamma check-it`."',
                                      'it reads "These entry points read their own file: `gamma check-it` and `gamma '
                                      'other`."'], errors=1),
    ]),
    # entry_minimal's tree, its loader skill carrying no entry list at all; its entry-point rules are right.
    ('entry_skill_list_missing', "a loader skill naming no entry point beside a declared one fails", [
        Step(['check-citations'], 1, [SK + ': no paragraph opens with the entry list the declarations give, "These entry '
                                           'points read their own file: `gamma check-it`." -- no paragraph opens with '
                                           '"These entry points read their own file:"'], errors=1),
    ]),
    # The layout before the entry-point rules moved out of the loader's body: entry_minimal's tree, its
    # loader skill holding the held list and naming no rules file, and no entry-files.md. Each of the three
    # fails, red beside entry_minimal's green.
    ('entry_rules_missing', "a held list in the loader's body and no entry-point rules file fail", [
        Step(['check-citations'], 1, [EPATH, ETRIGGER,
                                      ER + ': missing -- a request on `gamma` reads it with or before its other '
                                           "reads, for what each entry point's file holds",
                                      SK + ': names what the file of `gamma check-it` holds, which the entry-point '
                                           'rules, ' + ER + ', name -- the loader\'s body comes with every request, so '
                                           'the list is in the rules alone'], errors=4),
    ]),
    # entry_minimal's tree, its entry-list paragraph naming the rules file in a reworded trigger, "Its rules are
    # `...`.", which tells no request to read them: the trigger sentence is pinned word for word, red beside
    # entry_minimal's green ...
    ('entry_trigger_reworded', "an entry-list paragraph naming the rules file without the pinned trigger fails", [
        Step(['check-citations'], 1, [ETRIGGER], errors=1),
    ]),
    # ... and the paragraph without the sentence giving each file's path, which the entry-point rules do not repeat.
    ('entry_path_sentence_missing', "an entry-list paragraph without the pinned file-path sentence fails", [
        Step(['check-citations'], 1, [EPATH], errors=1),
    ]),
    # The held list, red beside entry_minimal's green: entry_minimal's tree, its entry-point rules naming
    # what check-it's file holds with §2 added, which the declaration does not hold, ...
    ('entry_skill_holds_extra', "an entry-point rules held list naming a section the declaration does not hold fails", [
        Step(['check-citations'], 1, [ER + ': the loader names what the file of `gamma check-it` holds as its declaration '
                                           'gives it, "The file for `gamma check-it` holds the text before §1, §1 and §3, '
                                           'and in part §4.0 ("never infer")." -- it reads "The file for `gamma check-it` '
                                           'holds the text before §1, §1, §2 and §3, and in part §4.0 ("never infer")."'],
             errors=1),
    ]),
    # ... and with §4.0's part left out, which the declaration holds.
    ('entry_skill_holds_short', "an entry-point rules held list leaving out a section the declaration holds fails", [
        Step(['check-citations'], 1, [ER + ': the loader names what the file of `gamma check-it` holds as its declaration '
                                           'gives it, "The file for `gamma check-it` holds the text before §1, §1 and §3, '
                                           'and in part §4.0 ("never infer")." -- it reads "The file for `gamma check-it` '
                                           'holds the text before §1, §1 and §3."'], errors=1),
    ]),
    # gamma holds §3 whole and §2.6 in part; a check-it region starts in §2.5, neither held nor held in
    # part, and runs on into §2.6, whose heading and owner-repo text it rightly holds.
    ('entry_region_outside_sections', "a region line in a numbered section its entry declares neither way fails", [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:15: this line of a `check-it` region lies in "
                                  "§2.5, which entry 'check-it' neither holds whole nor holds in part"], errors=1),
    ]),
    # gamma opens a region inside another; delta closes one inside a fenced block; epsilon opens one
    # for an entry it never declared.
    ('entry_region_errors', 'a nested entry region, one closed inside a fence and one naming no declared entry', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:10: region 'check-it' opens inside region "
                                  "'check-it' (opened at line 7) -- regions never nest",
                                  "plugins/workflows-core/references/delta.md:12: region 'check-it' closes inside a "
                                  "fenced block",
                                  "plugins/workflows-core/references/epsilon.md:13: region 'undeclared' names no declared "
                                  "entry"], errors=3),
    ]),
    # gamma declares an entry twice, two malformed entry lines, a malformed partial line, a partial
    # for an entry it never declares and an unknown line; delta holds a § and declares a partial §
    # that no heading of it opens with; epsilon declares a section held whole beside one it overlaps --
    # §1 twice, §3 and its §3.1, §3.2 in part under held §3, §1 in part as well as whole, and §2 in part
    # over held §2.1 -- and, green beside them, §2.2 in part under §2 in part.
    ('entry_declaration_errors', 'every entry declaration-line defect is reported', [
        Step(['check-parts'], 1, ["plugins/workflows-core/references/gamma.md:5: entry 'check-it' is declared twice",
                                  'plugins/workflows-core/references/gamma.md:6: an entry line is `entry <entry> '
                                  'holds=<§>[,<§>...]`',
                                  'plugins/workflows-core/references/gamma.md:7: an entry line is `entry <entry> '
                                  'holds=<§>[,<§>...]`',
                                  'plugins/workflows-core/references/gamma.md:8: a partial line is `partial <entry> <§> '
                                  '"<phrase>" ...`, every phrase quoted and non-empty',
                                  "plugins/workflows-core/references/gamma.md:9: partial names entry 'ghost', which is not "
                                  "declared",
                                  "plugins/workflows-core/references/gamma.md:10: unknown declaration line 'entries "
                                  "check-it holds=1' -- a line is `entry ...` or `partial ...`",
                                  'plugins/workflows-core/references/delta.md:4: §9 names no section of '
                                  'workflows-core:delta -- no heading opens with that number',
                                  'plugins/workflows-core/references/delta.md:5: §7 names no section of '
                                  'workflows-core:delta -- no heading opens with that number']
             + [E + m + ' -- a section held whole is declared once, its subsections with it' for m in (
                 ":4: entry 'check-it' holds §1 whole twice",
                 ":4: entry 'check-it' holds §3 whole, which covers §3.1, held whole too",
                 ":5: entry 'check-it' holds §3 whole, which covers §3.2, held in part too",
                 ":6: entry 'check-it' holds §1 whole, which covers §1, held in part too",
                 ":8: entry 'make-it' holds §2 in part, which covers §2.1, held whole too")], errors=13),
    ]),
    # The out-of-file citation check. Each tree is entry_minimal's -- check-it holds §1 and §3 whole and
    # §4.0 in part by "never infer" -- with a consumer whose `## Phase 0` requests `gamma check-it` and
    # whose Phase 1 cites alpha. In that section a sentence citing gamma is judged by its own § references.
    ('entry_cite_held', 'a citation of a section the entry-point file holds, in the section requesting it, passes', [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    ('entry_cite_out_of_file', "a citation of a section the entry-point file lacks, in the section requesting it, fails", [
        Step(['check-citations'], 1, [U + ":18: cites workflows-core:gamma §2.3, which the check-it file does not hold, in "
                                          "a section that reads only that file -- name a section it holds, load the whole "
                                          "reference at or before this sentence, or reword it so it implies no load",
                                      'entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked'],
             errors=1),
    ]),
    ('entry_cite_partial_without_phrase', 'a section held in part, cited without its phrase, fails', [
        Step(['check-citations'], 1, [U + ":18: cites workflows-core:gamma §4.0, which the check-it file does not hold, in "
                                          "a section that reads only that file"], errors=1),
    ]),
    ('entry_cite_partial_with_phrase', 'a section held in part, cited with its phrase in the sentence, passes', [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    # A sentence citing nothing, whose § belongs to the gamma citation in the sentence before it: §2.3 red,
    # and its twin leaning on §3.1, which the file holds, green.
    ('entry_cite_free_sentence_out_of_file', "a § in a sentence citing nothing, leaning on an earlier citation of "
                                             "the reference, is judged as that reference's", [
        Step(['check-citations'], 1, [U + ":18: cites workflows-core:gamma §2.3, which the check-it file does not hold, in "
                                          "a section that reads only that file",
                                      'entry-point file gamma check-it: 1 request section(s), 3 citation(s) checked'],
             errors=1),
    ]),
    ('entry_cite_free_sentence_held', "a § in a sentence citing nothing, leaning on an earlier citation, passes where "
                                      "the file holds it", [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 3 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    ('entry_cite_bare', 'a citation naming no section, in the section requesting the file, fails', [
        Step(['check-citations'], 1, [U + ":18: cites workflows-core:gamma with no section, which the check-it file does "
                                          "not hold, in a section that reads only that file"], errors=1),
    ]),
    # Phase 0: a whole load in an earlier paragraph, then §2.3. Phase 2, which requests check-it too: a
    # request of the make-it entry point, which reads the whole reference, then §2.3 in the next sentence.
    ('entry_cite_after_whole_load', 'a whole load at or before the citation in its section holds any section', [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 2 request section(s), 6 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    ('entry_cite_before_whole_load', 'a whole load after the citation in its sentence order does not hold it', [
        Step(['check-citations'], 1, [U + ":18: cites workflows-core:gamma §2.3, which the check-it file does not hold, in "
                                          "a section that reads only that file"], errors=1),
    ]),
    # After the first section requesting check-it, in a section that requests nothing, until the file first
    # loads gamma whole. Red: Phase 1 cites §3.1, which the file holds -- a lookup its text serves, green --
    # and Phase 9 cites §2.3, which it does not, with no whole load before it. Its green twin: the same, the
    # §2.3 sentence loading the whole reference itself.
    ('entry_cite_later_section', "a citation of a section the file lacks, in a later section before any whole load, "
                                 "fails", [
        Step(['check-citations'], 1, [U + ":28: cites workflows-core:gamma §2.3, which the check-it file does not hold, "
                                          "after the first `##` section requesting `gamma check-it` and before any load of "
                                          "the whole reference in this file, so a run loads the whole reference here -- "
                                          "name a section it holds, load the whole reference at or before this sentence, "
                                          "or reword it so it implies no load",
                                      'entry-point file gamma check-it: 1 request section(s), 3 citation(s) checked'],
             errors=1),
    ]),
    ('entry_cite_later_section_whole_load', "the same citation passes where its own sentence loads the whole reference", [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 3 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    # Phase 8 loads gamma whole, so Phase 9's §2.3 after it is a lookup that read serves: not judged.
    ('entry_cite_later_section_after_whole_load', 'a citation in a later section after a whole load of the reference '
                                                  'is not judged', [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    # Before the first section requesting check-it, a citation of a held section loads the whole reference
    # ahead of the request: red; with a whole load in its own sentence, green.
    ('entry_cite_before_request_section', 'a citation before the first section requesting the file fails', [
        Step(['check-citations'], 1, [U + ":13: cites workflows-core:gamma before the first `##` section requesting "
                                          "`gamma check-it`, so a run loads the whole reference ahead of that request -- "
                                          "load the whole reference in this sentence, or reword it so it implies no load",
                                      'entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked'],
             errors=1),
    ]),
    ('entry_cite_before_request_whole_load', 'a citation before the first requesting section that loads the whole passes', [
        Step(['check-citations'], 0, ['entry-point file gamma check-it: 1 request section(s), 2 citation(s) checked',
                                      'check-citations: PASS'], errors=0),
    ]),
    # check-questions: a command's first question -- a `choices:` line, fenced or not, a line naming
    # phase-handoff's §4.3, or a line stating a prompt of 2–4 options -- needs a **Load the question rules.**
    # step on an earlier line. Each tree holds
    # one asking command; the loaded and missing trees also hold one that asks nothing, which is not counted.
    ('question_rules_loaded', 'the question-rules step before the first choices: array passes', [
        Step(['check-questions'], 0, ['question rules: 1 command(s) present a choice list, 1 load the rules first',
                                      'check-questions: PASS'], errors=0),
    ]),
    ('question_rules_missing', 'a choices: array and no question-rules step fails', [
        Step(['check-questions'], 1, [QA + ':10: asks the user a question before its **Load the question rules.** '
                                           'step -- add the step before this line',
                                      'question rules: 1 command(s) present a choice list, 0 load the rules first'],
             errors=1),
    ]),
    ('question_rules_after_question', 'a step after the first choices: array does not hold it', [
        Step(['check-questions'], 1, [QA + ':6: asks the user a question before its **Load the question rules.** step',
                                      'question rules: 1 command(s) present a choice list, 0 load the rules first'],
             errors=1),
        Step(['check-questions', '--verbose'], 1, ['ASKS ' + QA + ': step at line 8, first question at line 6'],
             errors=1),
    ]),
    # The model-gate question sits before the first `##` heading: a step under Phase 0 comes too late. On a
    # copy, the step moved up beside the strip step, before the gate, passes.
    ('question_rules_before_intro_question', 'a question before the first ## heading needs the step before it', [
        Step(['check-questions'], 1, [QA + ':6: asks the user a question before its **Load the question rules.** step'],
             errors=1),
        Step(['check-questions'], 0, ['question rules: 1 command(s) present a choice list, 1 load the rules first',
                                      'check-questions: PASS'], errors=0, on_copy=True,
             pre=_rewrite(QA, (QSTEP + '\n\n', ''),
                          ('**The model gate runs next.**', QSTEP + '\n\n**The model gate runs next.**'))),
    ]),
    ('question_rules_fenced_array', 'a choices: array inside a fenced block is a question too', [
        Step(['check-questions'], 1, ['plugins/security-workflows/commands/ask.md:9: asks the user a question before '
                                      'its **Load the question rules.** step'], errors=1),
    ]),
    ('question_rules_fenced_step', 'a step inside a fenced block is printed, not run, so it is no step', [
        Step(['check-questions'], 1, [QA + ':11: asks the user a question before its **Load the question rules.** step',
                                      'question rules: 1 command(s) present a choice list, 0 load the rules first'],
             errors=1),
    ]),
    ('question_rules_parenthetical_only', 'a rule statement citing escalation-rules core in parentheses is no step', [
        Step(['check-questions'], 1, ['plugins/product-workflows/commands/ask.md:7: asks the user a question before '
                                      'its **Load the question rules.** step'], errors=1),
    ]),
    ('question_rules_presents_handoff_array', "presenting phase-handoff §4.3's array is a question with no choices: of "
                                              "its own", [
        Step(['check-questions'], 1, ['plugins/workflows-core/commands/hand.md:9: asks the user a question before '
                                      'its **Load the question rules.** step',
                                      'question rules: 1 command(s) present a choice list, 0 load the rules first'],
             errors=1),
    ]),
    # A prompt the command builds at run time, stated as 2–4 options with no `choices:` line of its own, as
    # /feedback's confirmation is. Each tree's preamble also states the arrays' rule, "`choices` arrays; 2–4
    # options", ahead of the strip step: a rule, not a prompt, so the red's question is the prompt line, and
    # the green's step, after that rule, still comes first.
    ('question_rules_runtime_prompt', 'a prompt stated as 2–4 options, with no step before it, fails', [
        Step(['check-questions'], 1, ['plugins/workflows-core/commands/note.md:11: asks the user a question before its '
                                      '**Load the question rules.** step',
                                      'question rules: 1 command(s) present a choice list, 0 load the rules first'],
             errors=1),
    ]),
    ('question_rules_runtime_prompt_loaded', 'a prompt stated as 2–4 options, after the step, passes', [
        Step(['check-questions'], 0, ['question rules: 1 command(s) present a choice list, 1 load the rules first',
                                      'check-questions: PASS'], errors=0),
    ]),
    ('question_rules_no_asking_command', 'vacuity: no command presents a choice list', [
        Step(['check-questions'], 1, ['the scan matched nothing',
                                      'question rules: 0 command(s) present a choice list, 0 load the rules first'],
             errors=1),
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
                if step.pre and not step.on_copy:
                    # A pre-step edits the tree it is given: run on the fixture, it would edit the committed tree.
                    why = '%s: a pre-step edits its tree, so its step runs on the copy -- set on_copy' % ' '.join(step.argv)
                    break
                root = copy if step.on_copy else fixture
                why = step.pre(root) if step.pre else None
                if why:
                    break
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


COMMANDS = {"generate": cmd_generate, "check-parts": cmd_check_parts, "check-citations": cmd_check_citations,
            "check-questions": cmd_check_questions}
USAGE = ("usage: reference-parts.py [--root DIR] generate|check-parts|check-citations|check-questions [--verbose]\n"
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

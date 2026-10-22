---
name: reference
description: Read a shared workflows-core reference by name, or one part of a reference that loads by part, and optionally execute one of its entry points.
user-invocable: false
allowed-tools: Read, Bash
---

The invocation arguments name one reference file and, optionally, a second
argument: one entry point within it — an entry point is the first word of a
code span in one of that reference's headings, for example `resolve-address`
in "### Entry point: `resolve-address <ARG> [<KIND>]`" — or, for a reference
that loads by part, one part of it.

Work from the reference's own words, never from memory or a summary. On a
reference that does not load by part, the text a request needs is the whole
file, whichever entry point the request names; with no second argument, it
is the whole file on any reference — save, either way, a request that an
entry point's own file serves, as the paragraph on those entry points says.
A read short of every line — a section, a range, a search — covers no
request that needs the whole file; consecutive
ranges from its first line to its last are one read of every line. Where the text
this request needs is already in this conversation word for word, from a
read made in this run, work from that text and read nothing, within one
bound: reuse an earlier read to execute an entry point only where that read
was made in the current phase — the `##` section of the command now running,
a `## Phase`, a `## Step` or any other `##` section, the text before its
first `##` heading counting as one; or, for an agent, its whole dispatch,
since an agent's run is one unit — and read it again otherwise; to look up a
rule, any read in this run serves. Read it whenever those words are not in
front of you now, whatever removed them — it was never read, only a different
part of it was read, or an earlier read has since been replaced by a summary
or cleared; a summary of a reference is never its text. Where you cannot
tell, read it. A read of the whole file covers every entry point in it,
within that bound.

These references load by part: `escalation-rules`, `finding-triage`,
`next-phase-offer` and `session-hygiene`. For one of these, a second
argument names a part: read
`${CLAUDE_PLUGIN_ROOT}/reference-parts/<the first argument>/<the second argument>.md`,
which holds the part, the reference's always part, the parts it needs and
the reference's rule index, and names every part it holds in the line under
its title; `index` reads that directory's `index.md`, the index alone. A
second argument naming no file there names no part, and that is no stop:
report the argument that named no part, read that directory's `index.md`,
and then read the part file the index names for the rule your step applies
— or, where the index names no part for that rule, read the whole reference
as below, which is what `args: "<name>"` loads. Never read anything else in
its place, and never apply a rule you have not read. With no second
argument, read the whole reference as below. A read of the whole reference
covers each of its parts, save what a part bundles from another reference,
and a part already read covers itself and every part the line under its
title names.
On any other reference, a second argument names an entry point; where it
names none of that reference's entry points, the request fails: report the
argument that named nothing, and stop as your command, or your agent, stops.

These entry points read their own file: `phase-handoff require-on-main`.
Each one's file is
`${CLAUDE_PLUGIN_ROOT}/reference-parts/<the reference>/<the entry point>.md`,
holding the entry point and the sections it needs and naming them in the
line under its title. The file for `phase-handoff require-on-main` holds
the text before §1, §1, §2.2, §2.6.1, §3 and §4.4, and in part §4.0
("never infer") and §5 ("rule 2" and "rule 3"). A request whose second
argument names the entry point reads the file and executes the entry point
from it. A request with no second argument, made for a citation of a section
the file holds — of one it holds in part, only for the text its quoted
phrase names — executes nothing and needs only that section's text, so it
is a lookup: wherever that text is in this conversation word for word, from
a read of the file or of the whole reference made in this run, in whatever
phase, it works from that text and reads nothing. Only where that text is
not in front of you does it read: the file, inside a `##` section whose text
also requests that entry point, before the citation or after it; the whole
reference, anywhere else. So a `##` section requesting the entry point
reads the file at most once, wherever the citation stands: where the
citation comes first and reads the file, the request executes the entry
point from that read, made in the current phase; where the request reads it
first, the citation is a lookup. Every other request on that reference reads
the whole reference, as the paragraph after this one says: a second argument
naming any other entry point, and a request with no second argument made for
a citation of a section the file does not hold, of a section it holds in
part for text its quoted phrase does not name — §4.0 for anything but its
*Never infer* rule, §5 for any rule but rules 2 and 3 — or of no section. A
read of the whole reference covers the file, within the same bound on reuse
as any read.

To read the whole reference — with no second argument, where the index of a
reference that loads by part names no part for the rule your step applies,
or with any second argument on a reference that does not load by part, in
each case save a request the paragraph above answers from an entry point's
own file — read
`${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md`. Reading the
whole reference means reading every line of it: where one read cannot hold
the file, read it in consecutive ranges from its first line to its last.

Whether the text was read now or is already in this conversation, treat it as
the single source of truth for the current step. When a second argument names
an entry point, execute that entry point of it inline. Never paraphrase or
summarise its contents.

---
name: reference
description: Read a shared workflows-core reference by name, or one part of a reference that loads by part, and optionally execute one of its entry points.
user-invocable: false
allowed-tools: Read, Bash
---

The invocation arguments name one reference file and, optionally, a second
argument: one entry point within it — an entry point is a name a heading of
that reference carries in a code span — or, for a reference that loads by
part, one part of it.

Work from the reference's own words, never from memory or a summary. Where
the text this request needs is already in this conversation word for word,
from a read made in this run, work from that text and read nothing. Read it
otherwise: when it was never read, when only a different part of it was
read, or when a compaction has replaced the earlier read with a summary — a
summary of a reference is never its text. A read of the whole file covers
every entry point in it.

These references load by part: `escalation-rules`, `finding-triage`,
`next-phase-offer` and `session-hygiene`. For one of these, a second
argument names a part: read
`${CLAUDE_PLUGIN_ROOT}/reference-parts/<the first argument>/<the second argument>.md`,
which holds the part, the reference's always part, the parts it needs and
the reference's rule index; `index` reads that directory's `index.md`, the
index alone. A second argument naming no file there is an error: stop and
report it, never read something else instead. With no second argument,
read the whole reference as below. A read of the whole reference covers
each of its parts, save what a part bundles from another reference, and a
part already read covers itself and every part it holds. On any other
reference, a second argument names an entry point, and one naming none of
its entry points is an error too: stop and report it, never read it as
something else.

To read the whole reference — with no second argument, or with an entry
point of any other reference — read
`${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md`.

Whether the text was read now or is already in this conversation, treat it as
the single source of truth for the current step. When a second argument names
an entry point, execute that entry point of it inline. Never paraphrase or
summarise its contents.

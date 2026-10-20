---
name: reference
description: Read a shared workflows-core reference by name, and optionally execute one of its entry points.
user-invocable: false
allowed-tools: Read, Bash
---

The invocation arguments name one reference file and, optionally, one entry
point within it.

Work from the reference's own words, never from memory or a summary. Where
the text this request needs is already in this conversation word for word,
from a read made in this run, work from that text and read nothing. Read it
otherwise: when it was never read, when only a different part of it was
read, or when a compaction has replaced the earlier read with a summary — a
summary of a reference is never its text. A read of the whole file covers
every entry point in it.

To read it, read `${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md`
and treat it as the single source of truth for the current step. When a
second argument is present, execute that entry point of it inline. Never
paraphrase or summarise its contents.

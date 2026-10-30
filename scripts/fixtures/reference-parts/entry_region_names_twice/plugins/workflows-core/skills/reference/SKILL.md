---
name: reference
description: Read a shared workflows-core reference by name, and optionally one part of it.
---

The invocation arguments name one reference file and, optionally, one entry
point within it.

These references load by part: `alpha`. For one of these, a second argument
names a part.

These entry points read their own file: `gamma check-it` and `gamma make-it`. Each one's file is
`${CLAUDE_PLUGIN_ROOT}/reference-parts/<the reference>/<the entry point>.md`.
A request on one of their references, with or without a second argument,
reads the entry-point rules, `${CLAUDE_PLUGIN_ROOT}/skills/reference/entry-files.md`,
with or before its other reads, unless their text is in this conversation word
for word, and follows them.

---
name: reference
description: Read a shared workflows-core reference by name, and optionally one part of it.
---

The invocation arguments name one reference file and, optionally, one entry
point within it.

These references load by part: `alpha`. For one of these, a second argument
names a part.

These entry points read their own file: `gamma check-it`. For one of these,
read the entry point's file under reference-parts/, and first the entry-point rules,
`${CLAUDE_PLUGIN_ROOT}/skills/reference/entry-files.md`.

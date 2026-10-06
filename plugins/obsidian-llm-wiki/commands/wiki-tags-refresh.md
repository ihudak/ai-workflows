---
name: wiki-tags-refresh
description: Scan the vault (or a target directory) for tags used in page frontmatter and page bodies, diff against the vault's tag-index.md, prompt to approve new tags and clean stale ones, then update tag-index.md in place. Run after heavy ingest sessions.
argument-hint: "[directory]"
allowed-tools: Read Write Edit Glob Grep Bash
---

Read `skills/wiki-tags-refresh/SKILL.md` fully, then run the tag sync for: $ARGUMENTS

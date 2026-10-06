---
name: wiki-query
description: Answer a question using the compiled wiki, with citations to wiki pages and original source files. Uses qmd semantic search when configured, falls back to index-guided reading otherwise. Offers to save substantive answers as new wiki pages.
argument-hint: "<question>"
allowed-tools: Read Glob Grep Bash
---

Read `skills/wiki-query/SKILL.md` fully, then answer the following question using the wiki: $ARGUMENTS

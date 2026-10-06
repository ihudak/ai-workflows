---
name: wiki-scan
description: Scan a directory (or all source directories) for files not yet ingested or changed since last ingest. Shows a diff report, asks for confirmation, then batch-ingests new and changed files. Archives processed .raw/ files.
argument-hint: "[directory]"
allowed-tools: Read Write Edit Glob Grep Bash
---

Read `skills/wiki-scan/SKILL.md` fully, then run the scan workflow for: $ARGUMENTS

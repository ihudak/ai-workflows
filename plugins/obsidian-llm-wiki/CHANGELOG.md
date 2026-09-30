# Changelog

All notable changes to the **obsidian-llm-wiki** plugin are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow semver at the plugin level.

## [0.4.4] — 2026-09-30

### Fixed

- **`skills/_shared/vault-conventions.md` named 2 of the 4 commands that write outside `wiki/`**, while the authoritative copy inside `wiki-init/SKILL.md`'s own vault block named all four — two live instructions disagreeing about the same boundary. Synced to the complete set (`/wiki-task`, `/wiki-tasks-extract`, `/wiki-tags-refresh`, `/wiki-init`), derived from the commands themselves, with a note that the two copies move together.

## [0.4.3] — 2026-09-24

### Changed — the marketplace is now `shipwright`, and the repository `ihudak/ai-workflows`

The marketplace was `ihudak-plugins`, at `ihudak/ihudak-claude-plugins`. GitHub redirects the old repository URL, but the marketplace name is part of every install key (`<plugin>@ihudak-plugins`), so moving to the new name means registering the marketplace again. Removing a marketplace uninstalls the plugins installed from it, so reinstall each one you had:

```bash
claude plugin marketplace remove ihudak-plugins
claude plugin marketplace add ihudak/ai-workflows
claude plugin install <plugin>@shipwright
```

Run the last line once per plugin you use, then restart Claude Code. Environment variables and your specs, docs and code repositories are not touched. This plugin's `homepage` and `repository` now point at the new repository.

## [0.4.2] — 2026-09-23

### Changed
- The worked examples in `wiki-lint`, `wiki-query`, `wiki-scan` and `wiki-schema` use a neutral example work area — the meeting folder `Meetings/ACME/` and the tag `acme` / `#acme` — in place of one that named a real organisation's internal team. Every skill uses the same pair, so the examples still agree with one another. Examples only; no behaviour changes.
- The remaining worked examples are neutral too: `wiki-scan`'s changed-file line reads `Projects/Products/P1234 MCP server for Acme.md`, the disambiguating qualifier in `wiki-save` and `wiki-schema` reads `MCP Server (Acme).md`, and `wiki-schema`'s work-area tag row reads `#acme` `#platform` `#cloud` — each in place of a name taken from a real organisation's internal products. Examples only; no behaviour changes.

## [0.4.1]

### Fixed
- Every copy of *"`/wiki-task` and `/wiki-tasks-extract` are the only wiki commands
  allowed outside `wiki/` and `.raw/`"* — `AGENTS.md`, `CLAUDE.md`, `README.md` (and its
  layout block's *"only directory wiki writes to"*), both blocks `wiki-init` writes into a
  vault, and `wiki-schema` (its *"All other wiki operations remain wiki-directory-only"*
  and *"write exclusively here"*). `/wiki-init` writes `.obsidian/copilot/` and the wiki
  blocks in the vault's `CLAUDE.md` and `.github/copilot-instructions.md`, and
  `/wiki-tags-refresh` updates `.obsidian/copilot/tag-index.md`. Each copy now names all
  four commands and what each writes.
- The two blocks `wiki-init` writes into a vault said *"Write only to `wiki/`"* one line
  above an exception naming `.raw/`. They now name every write into `.raw/`: the
  `.raw/_processed/` archive, `/wiki-scan`'s markdown conversion of an HTML file written
  beside it, and `/wiki-init` creating `.raw/` and its `.gitkeep`; `wiki-schema`'s
  *"All other wiki operations"* sentence names the first two. Re-run `/wiki-init` to sync
  a vault's copies.
- `skills/_shared/task-rules.md` said it is *"Referenced by `/wiki-task` and
  `/wiki-tasks-extract`"*; `/wiki-init` also copies it into a vault as
  `.obsidian/copilot/task-creation-rules.md`, and `wiki-schema` and `tag-index-template.md`
  point to it. The header now names them all.

## [0.4.0]

### Changed
- `wiki-tags-refresh` now scans the entire vault by default (excludes `.obsidian/`)
  instead of only `wiki/`, and accepts an optional `[directory]` argument to scope
  the scan. The stale-tag removal check always re-verifies vault-wide usage before
  suggesting removal, excluding only `tag-index.md` itself (not all of `.obsidian/`)
  so genuine uses elsewhere in `.obsidian/` still protect a tag from removal.
  Ported from the `ihudak-copilot-plugins` sibling repo; updated `wiki-schema` and
  the `wiki-init` vault-doc templates to match.

### Fixed
- `wiki-tags-refresh`'s file-collection scan no longer breaks on vault filenames
  containing spaces (`find | xargs awk` now uses `-print0`/`xargs -0`).
- `wiki-tags-refresh`'s inline-tag collection actually returns results now — the
  previous `grep -v "^#"` filter discarded every match, since `grep -oh` only ever
  emits strings that already start with `#` (pre-existing bug, now fixed).
- `wiki-tags-refresh`'s stale-tag check now uses an exact tag match instead of an
  unanchored substring match, so `#api` no longer false-matches `#api/rest`.
- Grep flags in `wiki-tags-refresh` are now placed before the pattern/path operands
  for portability to non-GNU (BSD/macOS) grep.

## [0.3.1]

### Fixed
- Corrected README/CHANGELOG install-path references to point at the actual
  `~/.claude/plugins/cache/<marketplace>/...` location (was the non-resolving
  `~/.claude/plugins/data/...@.../` form).

## [0.3.0]

### Added
- **wiki-task** command & skill — create individual tasks from natural language
  with effort estimation, tagging, and Jira linking in Obsidian Tasks format.
- **wiki-tasks-extract** command & skill — batch-extract tasks from wiki content
  after ingest.

## [0.2.0]

### Changed
- Ported from standalone Claude Code config to marketplace plugin format.
- Skills use SKILL.md with YAML frontmatter.
- Orchestrator skills declare `allowed-tools:` in frontmatter.
- Path references use `${CLAUDE_PLUGIN_ROOT}/` (agents/skills/hooks) or `~/.claude/plugins/cache/<marketplace>/obsidian-llm-wiki/<version>/` (installed content).
- Hooks: `SessionStart`, `PostCompact`, and `Stop` via `hooks.json`.

## [0.1.0]

### Added
- Initial release with nine commands & skills: wiki-init, wiki-ingest, wiki-scan,
  wiki-query, wiki-save, wiki-lint, wiki-hot, wiki-tags-refresh, wiki-schema.
- Hooks: `SessionStart` and `Stop` via `hooks.json`.
- AGENTS.md for GitHub Copilot compatibility.
- CLAUDE.md with vault-path configuration and command reference.

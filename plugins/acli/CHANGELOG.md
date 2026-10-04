# Changelog

## 0.1.3 — 2026-10-04

### Fixed

- **Safety said never to add `--yes`, while seven examples and two tips added it.** The rule is now
  stated as what it always meant: an agent's shell cannot answer `acli`'s confirmation prompt, so the
  user approves the exact set in the conversation first, and `--yes` carries that approval. Every
  `--yes` example is marked as running after approval, and the Selectors and Tips sections say the
  same instead of "add `--yes` to skip".
- **Safety listed some writes and left others out** — `create` and `create-bulk`, `comment update`
  and `--edit-last`, `filter update`, `sprint update --state closed`, `link delete`, Confluence blog
  creates. It now defines a write as every command that is not a read, names the reads, and groups
  the rest by consequence.

## 0.1.2 — 2026-09-24

### Changed — the marketplace is now `shipwright`, and the repository `ihudak/ai-workflows`

The marketplace was `ihudak-plugins`, at `ihudak/ihudak-claude-plugins`. GitHub redirects the old repository URL, but the marketplace name is part of every install key (`<plugin>@ihudak-plugins`), so moving to the new name means registering the marketplace again. Removing a marketplace uninstalls the plugins installed from it, so reinstall each one you had:

```bash
claude plugin marketplace remove ihudak-plugins
claude plugin marketplace add ihudak/ai-workflows
claude plugin install <plugin>@shipwright
```

Run the last line once per plugin you use, then restart Claude Code. Environment variables and your specs, docs and code repositories are not touched. This plugin's `homepage` and `repository` now point at the new repository.

## 0.1.1

### Fixed

- **Redundant `skills` manifest key.** `.claude-plugin/plugin.json` declared
  `"skills": ["./skills"]`, but per the Claude Code plugin reference the default `skills/`
  directory is *always* scanned and the `skills` field only *adds* to that scan — so the entry
  registered the same directory twice and diverged from the sibling plugins in this marketplace,
  which omit the key. Removed; `skills/acli/SKILL.md` is still discovered by the default scan.

## 0.1.0

- Initial release. Skill body derived from `ziegenberg/pi-skill-acli` (MIT © Daniel Ziegenberg),
  vendored as a first-party plugin. Adds headless-container authentication guidance and a
  destructive-operation Safety policy on top of upstream.

---
paths:
  - "plugins/**"
  - ".claude-plugin/marketplace.json"
  - "CLAUDE.md"
---

# Plugin updates

Loaded when a file under `plugins/` — the content an update ships — or `.claude-plugin/marketplace.json` is read, or `CLAUDE.md`, into which a CLI command must never be written unverified. Moved out of `CLAUDE.md` to keep it under its 36,000-character warning; evidence is in `docs/maintainers/rationale.md`.

## Updating installed plugins after editing

After pushing an edit, update the affected plugin on each machine so Claude Code picks up the new content:

```bash
claude plugin update dev-workflows@shipwright
claude plugin update product-workflows@shipwright
claude plugin update docs-workflows@shipwright
claude plugin update workflows-core@shipwright
```

- **`claude plugin update` requires a restart to apply** — the CLI says so itself.
- **There is no `claude plugin reinstall`.** The verb is `update`. Verify a command against `claude plugin --help` before writing it into `CLAUDE.md` or `.claude/rules/` — agents run what those files say, and a command that does not exist fails in a way that looks like a broken plugin. ([why](../../docs/maintainers/rationale.md#plugin-update-cli))
- **Update `prose-style` with `docs-workflows` past 1.1.3** (`claude plugin update prose-style@shipwright`): beside a `prose-style` older than 0.4.0, `/release-notes` records its style check `DEGRADED`.
- **Update the plugin that holds the file you edited — not the one whose workflow you were thinking about.** An update re-fetches exactly one plugin: the shared references, shared agents and family-meta commands are `workflows-core`'s, the product-definition commands and their agents and references `product-workflows`'s, the documentation commands `docs-workflows`'s. Otherwise the run picks up the old content and the change looks like it did not land.
- **`claude plugin marketplace update <marketplace>` does NOT update installed plugins.** It refreshes the *catalogue* — what the marketplace advertises — which is what makes a newly added plugin installable. An already-installed plugin stays at the version it was installed at. Use `claude plugin update` per plugin, or the `/plugins` interface (next bullet). ([why](../../docs/maintainers/rationale.md#plugin-update-cli))
- **The `/plugins` interface inside Claude Code upgrades what is already installed**, and **AutoUpdate** is settable per plugin there, after which nothing above is needed. This is a human step: an agent cannot drive that interface, so it uses the per-plugin `update` command.
- **A renamed plugin blocks marketplace update entirely** — not just its own, but every plugin from that marketplace. The remedy is to remove the marketplace and its plugins and reinstall from scratch (`claude plugin marketplace remove`, then `add`, then install each plugin), and the cost lands on every user, so weigh it before renaming one.
- `claude plugin validate <path>` validates a plugin or marketplace manifest, or the skills, agents and commands in a directory — a local pre-flight cheaper than a failed install. `claude plugin tag [path]` creates a `{name}--v{version}` git tag for a plugin release, **validating that `plugin.json` and any enclosing marketplace entry agree**, as `scripts/validate-catalog.py` also asserts — the last place to catch a disagreement.

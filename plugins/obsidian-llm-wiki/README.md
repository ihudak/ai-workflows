# obsidian-llm-wiki

LLM Wiki pattern for an active Obsidian vault, inspired by Andrej Karpathy's approach
to building a persistent, compounding knowledge base with an LLM. Compiles knowledge
from meetings, projects, daily notes, and raw sources into a cross-referenced wiki at
`wiki/`. Supports both **Claude Code** and **GitHub Copilot** as first-class agents.

---

## What It Does

- Ingests source notes (meetings, daily notes, project docs, research) into structured wiki pages
- Deduplicates and cross-links related concepts automatically
- Answers questions from the compiled wiki with page-level citations
- Tracks delta changes so re-processing skips unchanged files
- Maintains a hot cache (`hot.md`) for session continuity across agent restarts
- Governs tags against your vault's tag index

---

## Vault Prerequisites

### 1. Vault Location

The plugin defaults to `~/obsidian_vault`. Override with `VAULT_PATH`:

```bash
export VAULT_PATH=/path/to/your/vault
```

### 2. Create the Raw Inbox Directory

The wiki uses `.raw/` as an inbox for ad-hoc source files (articles, clippings, raw
notes) that don't fit an existing source directory. Create it once in your vault root:

```bash
cd /path/to/your/vault
mkdir .raw
touch .raw/.gitkeep   # so git tracks the empty directory
```

### 3. Expected Vault Directory Structure

The plugin reads from these directories (never writes to them):

```
obsidian_vault/
├── Meetings/           ← meeting notes (read-only source)
├── Daily/              ← daily notes (read-only source)
├── Projects/           ← project context, decisions, tech stack (read-only source)
│   ├── Products/
│   ├── Data Generators/
│   └── Jira/
├── Customers/          ← customer context (read-only source)
├── People/             ← people / contacts (read-only source)
├── Clippings/          ← web clippings (read-only source)
├── Research/           ← research notes (read-only source)
├── .raw/               ← ad-hoc inbox (wiki may archive processed files here)
│   └── _processed/     ← auto-created; archived files moved here after ingest
│       └── YYYY-MM/
├── wiki/           ← wiki output (where every wiki page is written)
│   ├── _index.md
│   ├── _log.md
│   ├── _manifest.json
│   ├── hot.md
│   └── <topic-pages>.md
└── .obsidian/
    └── copilot/
        └── tag-index.md   ← approved tag list (wiki reads; /wiki-tags-refresh updates)
```

---

## Installation

Complete installation has three parts: (A) install the plugin into your agent, (B)
configure your vault path if it differs from the default, (C) integrate the wiki layer
into your vault's instruction files (one-time, commit to the vault repo).

For the marketplace install shared across the `shipwright` plugins, see the [repo-root setup guide](../../README.md); the vault-specific steps below are unique to this plugin.

### Part A — Install the Plugin

#### Claude Code (marketplace)

The marketplace is registered as **`shipwright`** (pointing to `ihudak/ai-workflows`
on GitHub). If it is not yet registered on your machine, add it once via Claude Code settings
or the `/plugin` command, then install:

```
/plugin install obsidian-llm-wiki@shipwright
```

Plugin content installs under `~/.claude/plugins/cache/<marketplace>/obsidian-llm-wiki/<version>/`; persistent plugin state (if any) lives under `~/.claude/plugins/data/obsidian-llm-wiki-<marketplace>/`.
Hooks activate automatically: session start reads `hot.md`, session end updates it.

#### Claude Code (local / development)

```bash
cc --plugin-dir /path/to/obsidian-llm-wiki
```

#### GitHub Copilot (marketplace)

Register the marketplace once, then install:
```bash
copilot plugin marketplace add ihudak/ihudak-copilot-plugins
copilot plugin install obsidian-llm-wiki@ihudak-copilot-plugins
```

Plugin installs to `~/.copilot/installed-plugins/ihudak-copilot-plugins/obsidian-llm-wiki/`.

---

### Part B — Set Vault Path

The plugin defaults to `~/obsidian_vault` (the `obsidian_vault` folder in your home
directory). If your vault is elsewhere, set `VAULT_PATH` in your shell profile:

```bash
# macOS / Linux / WSL — add to ~/.zshrc or ~/.bash_profile
export VAULT_PATH="$HOME/path/to/your/obsidian_vault"
```

```powershell
# Windows PowerShell profile
$env:VAULT_PATH = "$env:USERPROFILE\path\to\your\obsidian_vault"
```

**WSL note:** if your vault lives on the Windows side, use the Linux mount path:
```bash
export VAULT_PATH="/mnt/c/Users/<YourWindowsUsername>/path/to/obsidian_vault"
```

---

### Part C — Vault Integration (one-time, commit to vault repo)

After completing Parts A and B, run `/wiki-init`.
This command handles the entire vault integration automatically:

- Creates the `.raw/` inbox
- Bootstraps `wiki/` with skeleton files (`_index.md`, `_log.md`, `_manifest.json`, `hot.md`)
- Copies the wiki schema into `.obsidian/copilot/wiki-schema.md`
- Bootstraps `.obsidian/copilot/tag-index.md` from template (if absent)
- Syncs `.obsidian/copilot/task-creation-rules.md` from plugin source
- Merges the wiki block into `CLAUDE.md` and `.github/copilot-instructions.md` idempotently

**Re-run `/wiki-init` after every plugin update** to keep the schema and instruction files in sync.

Then commit the vault changes:

```bash
git add .raw/.gitkeep wiki/ .obsidian/copilot/wiki-schema.md \
        .obsidian/copilot/tag-index.md .obsidian/copilot/task-creation-rules.md \
        CLAUDE.md .github/copilot-instructions.md
git commit -m "Add obsidian-llm-wiki integration"
git push
```

---

## Usage

### Commands

Both Copilot and Claude Code use the same `/wiki-*` slash commands with identical
behaviour.

| Command | Description |
|---------|-------------|
| `/wiki-ingest @filepath` | Ingest one source file into the wiki |
| `/wiki-scan [directory]` | Scan directory for unprocessed files; batch-ingest new/changed |
| `/wiki-query <question>` | Answer from the compiled wiki with citations |
| `/wiki-save` | Save the current conversation as a wiki page |
| `/wiki-lint` | Run a wiki health check and produce a lint report |
| `/wiki-hot` | Manually refresh the hot cache |
| `/wiki-tags-refresh [directory]` | Sync tags with `.obsidian/copilot/tag-index.md`; scans the whole vault by default |
| `/wiki-task <description>` | Create a single task from natural language (effort, tags, priority, dates) |
| `/wiki-tasks-extract [wiki-path]` | Batch-extract tasks from wiki content after ingest |
| `/wiki-init` | Initialize vault integration (first run or after plugin update) |

Both agents produce identical output and write to the same wiki files. Switching
between Claude Code and Copilot mid-project is seamless.

---

## How It Works

### Three-Layer Source Model

```
Layer 1 — Read-only sources
  Meetings/, Daily/, Projects/, Customers/, People/, Clippings/, Research/

Layer 2 — Ad-hoc inbox
  .raw/   ← drop files here for ingest; archived to .raw/_processed/ after

Layer 3 — Wiki output
  wiki/   ← structured pages, index, log, hot cache
```

### Wiki Page Types

| Type | When Used |
|------|-----------|
| `concept` | Reusable technical or domain concept |
| `entity` | Named thing: person, product, team, customer |
| `decision` | Architecture / product decision with rationale |
| `pattern` | Repeatable workflow or approach |
| `source-summary` | Condensed summary of a source document |

### Delta Tracking

`wiki/_manifest.json` records a content hash for every ingested source file.
`/wiki-scan` hashes each file before ingest and skips unchanged ones — re-running over
a large directory is fast.

### Hot Cache

`wiki/hot.md` is a rolling ≤300-word summary of recent wiki activity. It
gives the agent instant context at session start without re-reading hundreds of pages.

- **Claude Code**: auto-read at session start (SessionStart hook), auto-updated at
  session end (Stop hook), re-read after context compaction (PostCompact hook).
- **Copilot**: read via standing instruction in `AGENTS.md` before every wiki operation.

Use `/wiki-hot` to manually refresh the cache at any time.

### Semantic Search

`/wiki-query` uses the **qmd MCP** (if the wiki collection is registered) for semantic
vector search across all wiki pages. Falls back to index-guided reading when qmd is not
configured — useful for Copilot, which doesn't have MCP access.

---

## Tag Governance

The wiki only uses tags from `.obsidian/copilot/tag-index.md`. When ingest encounters
a concept that needs a tag not in the index, it records `tag-needed: <proposed>` in
`_log.md` rather than inventing a tag.

Run `/wiki-tags-refresh [directory]` after heavy ingest sessions to:

1. Scan page frontmatter and bodies for tags in use — the whole vault by default,
   or a given directory
2. Diff against `tag-index.md`
3. Prompt for approval of new tags and removal of stale ones
4. Update `tag-index.md` in place

---

## Boundary Rules

Wiki operations **never** write to or delete files in:
`Meetings/`, `Daily/`, `Projects/`, `Customers/`, `People/`, `Clippings/`, `Research/`

The only directory wiki cleans up (besides `wiki/`) is `.raw/`, where it
archives processed files to `.raw/_processed/YYYY-MM/`.

Wiki operations write only to `wiki/` and `.raw/`, with four exceptions, each to fixed
files only:

- `/wiki-task` and `/wiki-tasks-extract` intentionally write to `Projects/` files and
  `Tasks.md`.
- `/wiki-tags-refresh` updates `.obsidian/copilot/tag-index.md`.
- `/wiki-init` writes the vault's integration files — `.obsidian/copilot/` (the schema,
  the task rules, and a tag index where none exists) and its wiki blocks in `CLAUDE.md`
  and `.github/copilot-instructions.md`.

---

## License

MIT

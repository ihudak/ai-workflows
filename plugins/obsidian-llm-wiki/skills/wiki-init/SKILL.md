---
name: wiki-init
description: "Initialize or re-initialize the vault for the LLM wiki pattern: creates the .raw/ inbox and the wiki/ skeleton files, syncs the wiki schema and task rules to .obsidian/copilot/, and merges wiki blocks into CLAUDE.md and .github/copilot-instructions.md. Safe to re-run: existing pages and skeleton files are never overwritten. Triggers on: wiki-init, initialize the wiki, set up the wiki, bootstrap the wiki, init wiki, wiki setup, wiki initialize, set up obsidian-llm-wiki."
allowed-tools: Read Write Edit Glob Grep Bash
---

# wiki-init

Initialize or re-initialize vault integration. Safe to re-run after plugin updates —
existing wiki pages and data files are never overwritten.

---

## Step 1 — Resolve VAULT_PATH

```bash
VAULT="${VAULT_PATH:-${HOME}/obsidian_vault}"
[ -d "${VAULT}" ] || { echo "ERROR: vault not found at ${VAULT}. Set VAULT_PATH to your vault location."; exit 1; }
echo "Vault: ${VAULT}"
```

**Each shell block below resolves `VAULT` again on its first line.** A block may run as a fresh shell,
where an assignment from an earlier step is gone and `${VAULT}` expands to nothing — `mkdir -p "/.raw"`
at the filesystem root. A path a later step writes with the Write tool, `${VAULT}/…`, is the path this
step printed, written out.

---

## Step 2 — Create .raw/ inbox

```bash
VAULT="${VAULT_PATH:-${HOME}/obsidian_vault}"
mkdir -p "${VAULT}/.raw"
touch "${VAULT}/.raw/.gitkeep"
```

---

## Step 3 — Bootstrap wiki/ skeleton files

Create the wiki directory and all four skeleton files. Skip any file that already exists —
never overwrite existing data.

```bash
VAULT="${VAULT_PATH:-${HOME}/obsidian_vault}"
mkdir -p "${VAULT}/wiki"
```

**`wiki/_index.md`** — create only if absent:

```markdown
---
type: meta
title: "Wiki Index"
updated: YYYY-MM-DD
---

# Wiki Index

## Concepts
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

## Entities
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

## Decisions
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

## Patterns
| Page | Summary | Tags | Updated |
|------|---------|------|---------|

## Sources
| Page | Summary | Tags | Updated |
|------|---------|------|---------|
```

**`wiki/_log.md`** — create only if absent:

```markdown
---
type: meta
title: "Ingest Log"
updated: YYYY-MM-DD
---

# Wiki Ingest Log

(Entries prepended by /wiki-ingest, /wiki-save, /wiki-scan, /wiki-lint, /wiki-tags-refresh, /wiki-hot, /wiki-init)
```

**`wiki/_manifest.json`** — create only if absent:

```json
{
  "ingested": [],
  "last_run": null
}
```

**`wiki/hot.md`** — create only if absent:

```markdown
# Recent Context

## Last Updated
(never — no wiki sessions yet)

## Current Focus
(none)

## Recent Changes
(none)
```

Use today's date (YYYY-MM-DD) in the `updated:` fields of files you create.

---

## Step 4 — Sync wiki-schema to vault

Read `skills/wiki-schema/SKILL.md` fully.

Create the target directory if needed:
```bash
VAULT="${VAULT_PATH:-${HOME}/obsidian_vault}"
mkdir -p "${VAULT}/.obsidian/copilot"
```

Write the full content of `skills/wiki-schema/SKILL.md` to
`${VAULT}/.obsidian/copilot/wiki-schema.md`. **Always overwrite** — this is the sync
mechanism that keeps the vault schema up to date after plugin updates.

---

## Step 4a — Bootstrap tag-index.md (if absent)

Check whether `${VAULT}/.obsidian/copilot/tag-index.md` exists.

- **If it exists**: skip — never overwrite a user's tag vocabulary.
- **If it does not exist**: read `skills/_shared/tag-index-template.md` fully and
  write the template content to `${VAULT}/.obsidian/copilot/tag-index.md`.

---

## Step 4b — Sync task-creation-rules to vault

Read `skills/_shared/task-rules.md` fully.

Write the content to `${VAULT}/.obsidian/copilot/task-creation-rules.md`. **Always
overwrite** — the plugin's `_shared/task-rules.md` is the canonical source.
This keeps the vault copy in sync after plugin updates, just like wiki-schema.

---

## Step 5 — Merge wiki block into CLAUDE.md

Target: `${VAULT}/CLAUDE.md`

If this file does not exist, skip and note it in the report.

Check whether the file contains a `<!-- WIKI_BLOCK_START -->` anchor:

- **Anchor found**: replace the entire span from `<!-- WIKI_BLOCK_START -->` to
  `<!-- WIKI_BLOCK_END -->` (inclusive) with the wiki block below.
- **Anchor not found**: append the wiki block at end of file (one blank line before it).

The `<!-- WIKI_BLOCK_START -->` / `<!-- WIKI_BLOCK_END -->` HTML comments are the
idempotent merge anchors — they allow safe re-runs without duplicating content.

<!-- WIKI_BLOCK_START -->
## Wiki

Compiled knowledge base at `wiki/`. Plugin: `obsidian-llm-wiki`.
Full schema at `.obsidian/copilot/wiki-schema.md`.

`wiki/hot.md` is auto-read at session start and auto-updated at session end
by the plugin hooks. When hot.md content appears at session start, silently absorb it
as context — do not announce it, do not summarise it. Run `/wiki-hot` to refresh manually.

### Wiki Commands

| Command | Description |
|---------|-------------|
| `/wiki-ingest @filepath` | Ingest one source file into the wiki |
| `/wiki-scan [directory]` | Scan directory for unprocessed files; batch-ingest new/changed |
| `/wiki-query <question>` | Answer from the compiled wiki with citations |
| `/wiki-save` | Save current conversation as a wiki page |
| `/wiki-lint` | Run wiki health check, produce lint report |
| `/wiki-hot` | Manually refresh the hot cache |
| `/wiki-tags-refresh [directory]` | Sync tags with tag-index.md; scans the whole vault by default |
| `/wiki-task <description>` | Create a single task from natural language |
| `/wiki-tasks-extract [wiki-path]` | Batch-extract tasks from wiki content |
| `/wiki-init` | Re-initialize vault integration after plugin install/update |

### Wiki Boundary Rules

Wiki operations MUST NEVER write to: `Meetings/`, `Daily/`, `Projects/`, `Customers/`,
`People/`, `Clippings/`, `Research/`. Read these directories; never modify them.
Write only to `wiki/`, and to `.raw/` only to archive a processed file under
`.raw/_processed/YYYY-MM/` or, in `/wiki-scan`, to write an HTML file's markdown
conversion beside it (`/wiki-init` also creates `.raw/` itself and its `.gitkeep`).

**Exceptions**: `/wiki-task` and `/wiki-tasks-extract` intentionally write to `Projects/`
files and `Tasks.md`; `/wiki-tags-refresh` updates `.obsidian/copilot/tag-index.md`;
`/wiki-init` writes `.obsidian/copilot/` and the wiki blocks in `CLAUDE.md` and
`.github/copilot-instructions.md`. These are the only wiki commands that write outside
`wiki/` and `.raw/`.

Only use tags from `.obsidian/copilot/tag-index.md`. Never invent new tags.
<!-- WIKI_BLOCK_END -->

---

## Step 6 — Merge wiki section into .github/copilot-instructions.md

Target: `${VAULT}/.github/copilot-instructions.md`

If this file does not exist, skip and note it in the report.

Check whether the file contains a `<!-- WIKI_BLOCK_START -->` anchor:

- **Anchor found**: replace the entire span from `<!-- WIKI_BLOCK_START -->` to
  `<!-- WIKI_BLOCK_END -->` (inclusive) with the wiki block below.
- **Anchor not found**: append the wiki block at end of file (one blank line before it).

The `<!-- WIKI_BLOCK_START -->` / `<!-- WIKI_BLOCK_END -->` HTML comments are the
idempotent merge anchors — they allow safe re-runs without duplicating content.

<!-- WIKI_BLOCK_START -->
## Wiki

The vault has a compiled knowledge base at `wiki/` managed by the
`obsidian-llm-wiki` Copilot plugin.

### Hot Cache — Automatic via Hooks

`wiki/hot.md` is managed automatically by plugin hooks:
- **SessionStart** — hot.md is read silently and injected as context
- **Stop** — the agent is prompted to update hot.md before ending the session

No manual steps needed. To force a hot cache refresh mid-session, run `/wiki-hot`.

### Wiki Commands

| Command | Description |
|---------|-------------|
| `/wiki-ingest @filepath` | Ingest one source file into the wiki |
| `/wiki-scan [directory]` | Scan directory for unprocessed files |
| `/wiki-query <question>` | Answer from the compiled wiki with citations |
| `/wiki-save` | Save current conversation as a wiki page |
| `/wiki-lint` | Run wiki health check |
| `/wiki-hot` | Refresh the hot cache (run at END of every wiki session) |
| `/wiki-tags-refresh [directory]` | Sync tags with tag-index.md; scans the whole vault by default |
| `/wiki-task <description>` | Create a single task from natural language |
| `/wiki-tasks-extract [wiki-path]` | Batch-extract tasks from wiki content |
| `/wiki-init` | Re-initialize vault integration after plugin update |

### Wiki Schema

Full vault conventions (page types, frontmatter, tags, cross-linking) at:
`.obsidian/copilot/wiki-schema.md`

Read the schema fully before any operation that creates or modifies wiki pages.

### Wiki Boundary Rules

Wiki operations MUST NEVER write to: `Meetings/`, `Daily/`, `Projects/`, `Customers/`,
`People/`, `Clippings/`, `Research/`. Read these directories; never modify them.
Write only to `wiki/`, and to `.raw/` only to archive a processed file under
`.raw/_processed/YYYY-MM/` or, in `/wiki-scan`, to write an HTML file's markdown
conversion beside it (`/wiki-init` also creates `.raw/` itself and its `.gitkeep`).

**Exceptions**: `/wiki-task` and `/wiki-tasks-extract` intentionally write to `Projects/`
files and `Tasks.md`; `/wiki-tags-refresh` updates `.obsidian/copilot/tag-index.md`;
`/wiki-init` writes `.obsidian/copilot/` and the wiki blocks in `CLAUDE.md` and
`.github/copilot-instructions.md`. These are the only wiki commands that write outside
`wiki/` and `.raw/`.

Only use tags from `.obsidian/copilot/tag-index.md`. Never invent new tags.
If a concept needs a new tag, flag it with `tag-needed: <proposed>` and let the user
approve it via `/wiki-tags-refresh`.
<!-- WIKI_BLOCK_END -->

---

## Step 7 — Report

Print a structured summary of what happened:

```
wiki-init complete
──────────────────────────────────────────────────
Vault: ${VAULT}

Infrastructure
  .raw/                              ✓ ready
  wiki/                              ✓ ready

Skeleton files (skip = already existed)
  _index.md          [created | skipped]
  _log.md            [created | skipped]
  _manifest.json     [created | skipped]
  hot.md             [created | skipped]

Schema & rules sync
  .obsidian/copilot/wiki-schema.md           [synced | skipped — .obsidian/copilot/ not found]
  .obsidian/copilot/tag-index.md             [created from template | skipped — already exists]
  .obsidian/copilot/task-creation-rules.md   [synced | skipped — .obsidian/copilot/ not found]

Instruction file merges
  CLAUDE.md                          [section added | section updated | skipped — not found]
  .github/copilot-instructions.md    [section added | section updated | skipped — not found]
──────────────────────────────────────────────────
```

Then always print the session workflow:

```
Session workflow:
  SESSION START  — hot cache loads automatically via hooks (SessionStart)
  SESSION END    — hot cache updates automatically via hooks (Stop)
  MANUAL REFRESH — run `/wiki-hot` to force a hot cache refresh mid-session
  AFTER UPDATE   — run `/wiki-init` to sync wiki-schema.md with the new plugin version
```

---

## Step 8 — Suggest vault commit

Do not run git commands. Just suggest:

```
Next step: commit these changes to your vault repo so other machines get the
integration on git pull:

  git add .raw/.gitkeep wiki/ .obsidian/copilot/wiki-schema.md \
          .obsidian/copilot/tag-index.md .obsidian/copilot/task-creation-rules.md \
          CLAUDE.md .github/copilot-instructions.md
  git commit -m "chore: initialize obsidian-llm-wiki integration"
```

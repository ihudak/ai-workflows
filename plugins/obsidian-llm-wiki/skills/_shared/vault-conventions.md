# Vault Conventions — Shared Reference

Structural conventions for an Obsidian vault with integrated task and project management.
Referenced by `/wiki-task`, `/wiki-tasks-extract`, and other skills that need to locate
files or understand vault layout.

All paths below are relative to the vault root (`$VAULT`).

---

## Directory Layout

```
vault/
├── Daily/                          # Daily notes (YYYY-MM-DD ddd.md)
├── Weekly/                         # Weekly notes (YYYY-WW.md)
├── Projects/
│   └── Products/                   # Main project area
│       ├── PXXXXX <name>.md        # Individual project files
│       └── Product Index.md        # Master project dashboard
├── Tasks.md                        # Unstructured / fallback task list
├── Tasks Summary.md                # Query-based task dashboard
├── Knowledge/                      # Reference materials
├── Meetings/                       # Meeting notes
├── People/                         # Team & capability info
├── Procedures/                     # Process checklists
├── _templates/                     # Templater templates
├── _archive/                       # Archived content
├── wiki/                           # LLM wiki knowledge base
├── .raw/                           # Wiki source inbox
└── .obsidian/
    └── copilot/                    # Agent knowledge base files
```

Not all directories are required. Skills must check existence before accessing.

---

## Project File Structure

Project files live under `Projects/` (often `Projects/Products/`).
The naming convention is `PXXXXX <Name>.md` but may vary by vault.

### Frontmatter Schema

```yaml
---
name: "Project Name"
category: <category>
status: IMPL                        # IMPL, BACKLOG, DONE, etc.
archived: false                     # Must be false to add tasks
tags:
  - task                            # Must have this tag to receive tasks
  - <area-tag>
type: project
jira:                               # Optional — Jira integration
  id: TICKET-XXXXX
  rank: <lexicographic-string>
  status: <jira-status>
  order: <number>                   # Sorting in project index
owner: "[[Person Name]]"            # Optional
---
```

### Key Frontmatter Fields for Task Skills

| Field | Required for tasks? | Check |
|-------|-------------------|-------|
| `archived` | Yes | Must be `false` or absent |
| `tags` | Yes | Must include `task` |
| `status` | No | Informational only |

### Section Layout

```markdown
# Project Title

## Assignments
(people, teams, owners)

## Static Items
(links, docs, dependencies)

## Work Items
### Tasks              ← Insert new tasks here
### Notes

## Archived Tasks      ← NEVER insert incomplete tasks here
```

The `### Tasks` section is the only valid insertion point for new tasks.
Archive sections are excluded from dashboard queries.

---

## Tasks.md Structure

`Tasks.md` at the vault root is the fallback target when no project file matches.

```markdown
---
tags:
  - task
---

# Tasks

# Regular
(recurring tasks)

# Irregular
(one-off tasks — default insertion point for fallback)

# Archive
(completed task archive — never insert incomplete tasks here)
```

Insert fallback tasks under `# Irregular`.

If `Tasks.md` does not exist, create it with the minimal structure above
(just frontmatter + `# Tasks` + `# Irregular`).

---

## Daily Note Format

- **Path**: `Daily/YYYY-MM-DD ddd.md` (e.g., `Daily/2026-02-17 Mon.md`)
- **Structure**: Header → Tasks (query-based) → Worklog → Retrospective → Goals → Notes
- **Rule**: Never add tasks to Daily notes unless the user explicitly requests it.
  Daily-note tasks are hard to reschedule.

---

## Weekly Note Format

- **Path**: `Weekly/YYYY-WW.md` (e.g., `Weekly/2026-W08.md`)
- **Structure**: Header → ToDo (this week) → Retrospective → Week Goals → Worklog → Notes

---

## Date Formats

| Context | Format | Example |
|---------|--------|---------|
| Daily notes | `YYYY-MM-DD ddd.md` | `2026-02-17 Mon.md` |
| Weekly notes | `YYYY-WW.md` | `2026-W08.md` |
| Task dates | `YYYY-MM-DD` | `2026-02-17` |

---

## Archive Strategy

- Projects: set `archived: true` in frontmatter → excluded from dashboards
- Old daily/weekly notes: moved to `_archive/`
- Completed tasks: moved to project's "Archived Tasks" section (or Tasks.md "# Archive")

---

## Task Query System

The vault uses the **Obsidian Tasks plugin** for query-based dashboards.

### Common Filters

```
not done                            # Incomplete tasks
happens on YYYY-MM-DD              # Scheduled for date
due before YYYY-MM-DD              # Due before date
tags include #tag                   # Has tag
tags do not include #hide           # Excludes tag
filter by function task.status.symbol === '/'  # In-progress
priority is Highest                 # Priority filter
```

### Common Sorting

```
sort by urgency                     # Built-in urgency score
sort by priority                    # By priority level
sort by scheduled                   # By schedule date
sort by function task.status.symbol # By status
```

---

## Wiki Layer

Wiki directories can exist at two levels:

- **Vault-level**: `wiki/` (default) with inbox at `.raw/`
- **Project-level**: `Projects/<Category>/<project>/wiki/` with inbox at `Projects/<Category>/<project>/.raw/`

Both follow the same schema (see `wiki-schema` skill).

---

## Read-Only Zones

Skills that create or modify content must never write to:
`Meetings/`, `Daily/`, `Customers/`, `People/`, `Clippings/`, `Research/`.

Exceptions — the complete set of wiki commands that write outside `wiki/` and `.raw/`,
derived from the commands themselves rather than from this list:

- `/wiki-task` and `/wiki-tasks-extract` may write to `Projects/` files and `Tasks.md`
  (task insertion is explicitly allowed outside the wiki boundary).
- `/wiki-tags-refresh` updates `.obsidian/copilot/tag-index.md`.
- `/wiki-init` writes `.obsidian/copilot/` (the schema, tag-index and task-rules copies),
  creates `.raw/` and its `.gitkeep`, and maintains the wiki blocks in the vault's own
  agent-instruction files.

This paragraph named only the first two for as long as it existed, while the authoritative copy
inside `wiki-init/SKILL.md`'s own vault block named all four — two live instructions disagreeing
about the same boundary. Keep them in step: a new outside-`wiki/` writer belongs in both.

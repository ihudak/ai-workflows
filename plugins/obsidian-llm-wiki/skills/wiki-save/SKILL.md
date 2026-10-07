---
name: wiki-save
description: >
  Save the current conversation or a specific insight as a permanent wiki page.
  Determines the best page type, drafts the page, shows it for approval, then writes
  it to wiki/ and updates _index.md, _log.md, and hot.md.
  Triggers on: wiki-save, save this to the wiki, save this conversation, file this
  insight, add this to the wiki, wiki save, keep this.
allowed-tools: Read Write Edit Glob Grep Bash
---

# wiki-save

Read `skills/wiki-schema/SKILL.md` fully before proceeding.

Invoke with: `/wiki-save`

---

## Step 1 — Resolve VAULT_PATH

Vault path: `~/obsidian_vault` by default; set `VAULT_PATH` to override. WSL users with a Windows-side vault must set `VAULT_PATH` explicitly (e.g. `/mnt/c/Users/<name>/obsidian_vault`).

---

## Step 2 — Scan the conversation

Read the current conversation and identify the most valuable knowledge to preserve:
- Non-obvious insights or synthesis across multiple topics
- Decisions made with explicit rationale
- Patterns or reusable approaches discovered
- Research findings that took significant effort

**Skip if**: the content is already in the wiki, is a simple lookup question, is
a temporary debugging exchange with no lasting insight, or is a step-by-step setup
procedure already documented elsewhere. If it's already in the wiki, offer to update
the existing page instead.

---

## Step 3 — Determine page type

| If the conversation produced… | Use type |
|-------------------------------|----------|
| A synthesised analysis or answered a specific question | `concept` or `decisions/` |
| A definition or explanation of a technical idea | `concept` |
| An architectural, product, or strategic decision | `decision` |
| A reusable approach, pattern, or gotcha | `pattern` |
| A summary of external material discussed | `source-summary` (place in `sources/`) |
| Notes about a specific person, team, or customer | `entity` |

If the user specifies a type explicitly, use it.

---

## Step 4 — Suggest a title and location

Derive a short, descriptive Title Case title from the conversation topic.

Check that no page with this filename already exists anywhere in the vault:
```bash
find "<the resolved vault path>" -name "<the proposed title>.md"
```

If a conflict exists, propose a qualified name (e.g., `MCP Server (Acme).md`).

Suggest: `"Save as [[<type>/<proposed-title>]]?"` — wait for user confirmation or
alternative title before drafting.

---

## Step 5 — Draft the page

Write the page content:
- Declarative present tense throughout. Write the knowledge itself, not the conversation.
  Not: "The user asked about X and Claude explained…"
  Yes: "X works by doing Y. The key consideration is Z."
- Cross-link every mentioned concept, entity, or decision on first mention.
- Apply the correct frontmatter schema from `wiki-schema` (type, wiki-status: developing,
  created, updated, tags from tag-index.md, related wikilinks).
- 100–300 lines. If it would be longer, split into related pages and link them.
- Do NOT add Dataview queries.

---

## Step 6 — Show draft and wait for approval

Display the full draft (frontmatter + body). Ask:
```
Save this page? [yes / edit / cancel]
```

If the user says **edit**: apply requested changes and show again.
If the user says **cancel**: discard and stop.
Only write to disk on explicit **yes**.

---

## Step 7 — Write the page

Write to `wiki/<type-folder>/<title>.md`.

---

## Step 8 — Update _index.md

Add a row for the new page in the correct section. Update the `updated:` date on
`_index.md`. Sort the section alphabetically.

---

## Step 9 — Append to _log.md

New entry at the TOP:
```markdown
## [YYYY-MM-DD] save | <page title>
- Type: <type>
- Location: [[<type-folder>/<title>]]
- From: conversation about <brief topic description>
```

---

## Step 10 — Update hot.md

Add the new page to `## Recent Changes` in `hot.md`. Update `## Last Updated`. Keep
total file ≤300 words.

---

## Finish

```
Saved: [[<type-folder>/<title>]]
Index updated. Log updated. Hot cache updated.
```

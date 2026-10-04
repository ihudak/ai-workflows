# example-docs changelog entries — writing guidelines

Single source of truth for writing `changelog:` frontmatter entries on
example-docs pages. Applied by the `docs-frontmatter` skill and, in the `/document` write path, read directly by `doc-planner`, `doc-writer`, and `doc-reviewer`.

## Format

Changelog entries live in the `changelog` frontmatter property:

```yaml
changelog:
  - 2022-03-25 <change2 description>
  - YYYY-MM-DD <change1 description>
```

- Use a two-digit month (e.g. `04` for April).
- With multiple entries, list the **newest change first**.
- Limit each entry — including the leading `-`, date, and description — to **200 characters**.

## Why changelog entries are business critical

- The changelog date is the basis for date-based search results on the main
  search page. Without it, the date-based search filter does not work.
- Entries are visible to customers via the "Updated on MMM D, YYYY" link on a page.

## Writing change descriptions

- **Meaningful entries.** Terse, from the customer's point of view. Don't write
  vague descriptions like "Updated page to match the new UI." Answer "to what
  effect?" — highlight significant changes, new features, or deletions.
- **No internal render mechanics.** Never name the publishing machinery in an entry — "Self-hosted-only", "Cloud-only", "space", "content root". Readers of a page do not know those concepts exist. Describe what changed for the customer on the page they are reading; where something renders is the build's business, not theirs.
- **Never on first publish.** Do not create a changelog entry when a page is
  first published; the published timestamp is used instead.
- **No "hidden" entries.** "Hiding" is an internal unpublish mechanism, not
  meaningful to customers. Rewrite as "Page retired because…" or "Feature X is
  no longer available, and its documentation has been removed."
- **Avoid section titles** unless strictly necessary; they bloat entries and
  change over time.
- **Page context matters.** Customers read entries as `<Page title>: <entry>`.
  The entry must make sense alongside the page title.

## Grammar and style

- **Period rule (verify before finalizing EVERY entry):**
  - If the entry is a **complete sentence**, it **MUST end with a period**.
  - If the entry is a **phrase / fragment**, it **MUST NOT** end with a period.
- Write in the **past tense**.
- Use **active verbs**.
- Do **not** use the verb "documented".
- Do **not** overuse "added" — see the examples for alternatives.
- Keep each description to a **single paragraph**.
- Do not use short forms like "info" or "max".

## Examples

| Page title | Changelog description | Notes |
|---|---|---|
| Infrastructure Monitoring mode | Clarified information around auto-injection and added a section on filtering hosts based on injection status. | ✔️ Complete sentence; ends with a period; 107 characters. |
| Start/stop/restart the agent | Described how to start/stop/restart all agent services, not just the main service. | ✔️ Complete sentence; ends with a period. |
| Synthetic events | Additional JavaScript event example on changing the user for each monitor execution | ✔️ Phrase; **no** period. |
| Webhooks | Moved Webhooks documentation from the Notification section to the Developer section; links and content remain the same. | ✔️ Page-move with from/to; ends with a period; 117 characters. |
| Managing labels and templates | Moved the section on managing templates to a page of its own | ✔️ A split, recorded on the page the content left; phrase; **no** period. |
| Managing labels | New page, split from earlier page on managing labels and templates | ❌ A new page gets no entry — its published date covers it. Record the split on the page the content left. |
| Install XYZ | Updated installation instructions. | ❌ To what effect? Rewrite highlighting the main changes. |
| <Any topic> | Page hidden because of feature deprecation. | ❌ Don't expose "hiding". Rewrite as "Page retired because…". |
| Credential vault | Created topic. | ❌ A new page gets no entry (see **Never on first publish**); its published date covers it. |
| Uninstall <anything> | How to uninstall the application module | ❌ Don't reuse a section heading. Rewrite as "Added a section on uninstalling the application module." |

## Owners policy (self-hosted pages)

- Applies to changed pages under `self-hosted/_content/**` only.
- Ensure every ID in `default-owners.txt` is present in the page's `owners:`
  list. **Union only — never remove existing owners.**
- `default-owners.txt` ships a placeholder ID as part of the built-in worked
  example. Both consumers — the `changelog-owners-reminder` hook and the
  `docs-frontmatter` skill — read that bundled file directly, under
  `${CLAUDE_PLUGIN_ROOT}`; a profile's `frontmatter.default_owners` names that
  same bundled file — the value both of its writers, `/docs-profile` and
  `/docs-init`, are instructed to put there — and no consumer resolves it.

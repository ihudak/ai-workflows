---
name: docs-frontmatter
description: Apply documentation-page frontmatter conventions — changelog entries and page owners — when creating or editing a docs page under any content root declared by the applicable docs profile (an in-repo .dev-workflows/docs-profile.yml, else the built-in default). Use whenever you change a documentation page's content or frontmatter in a docs repository, or when the user mentions a page changelog, page owners, or docs frontmatter.
user-invocable: true
allowed-tools: Read, Edit, Glob, Grep, Bash
---

# Documentation frontmatter conventions

Apply when creating or editing `.md` pages under any `spaces[].content_root` declared by
the applicable docs profile. Three conventions, all in the
page's YAML frontmatter, applied in the same pass: changelog entries, self-hosted-docs
owners, and the core metadata fields.

## 1. Changelog (changed existing pages only)

For every **changed existing** page (NOT brand-new pages — first publish uses the
`published` timestamp instead), prepend a `changelog:` entry dated **today**:

1. Get today's date: run `date +%F` (yields `YYYY-MM-DD`, two-digit month).
2. Prepend the entry as the **first** list item under `changelog:` (newest first):
   ```yaml
   changelog:
     - <today> <change description>
     - <older entries unchanged>
   ```
3. Keep each entry — including the leading `- ` and date — within **200 characters**.
4. Write the description per the guidelines reference. The most-missed rule:
   **the period rule — verify before finalizing each entry:**
   - complete sentence → **ends with a period**;
   - phrase / fragment → **no period**.
   Also: past tense; active verbs; meaningful and customer-facing; no "documented";
   don't overuse "added"; no section titles; never expose "hidden"; no short forms
   ("info", "max"); single paragraph.

Full rules and worked examples (source of truth):
`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/changelog-guidelines.md`

## 2. Owners (changed self-hosted pages only)

For changed pages in a space listed in `frontmatter.owners_spaces` that have — or should have — an
`owners:` block, ensure every required ID is present. **Union only — never remove
existing owners.**

1. Read the required IDs (ignore `#` comments and blank lines):
   `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/default-owners.txt`
2. If the page has no `owners:` block but one is warranted (most self-hosted pages
   carry owners), add one containing the required IDs.
3. If an `owners:` block exists, add any required IDs that are missing and leave
   all existing owners in place.

Pages in a space not listed in `frontmatter.owners_spaces` are out of scope for the owners rule.

## 3. Metadata fields (all pages)

Set/validate the core frontmatter fields per the guidelines reference:

- `title` — required; sentence case; no trailing period.
- `description` — required; **120–160 characters** (SEO). Warn if outside the band.
- `meta.content-type` — **mandatory on new pages**; one of the enum
  (`how-to`, `tutorial`, `explanation`, `reference`, `get-started`,
  `troubleshooting`, `upgrade`, `best-practices`, `app`, `extension`).
  **Never `overview`** (deprecated); `release-notes` pages are
  not authored here: `/release-notes` drafts the note.
- `meta.i18n-priority` — optional number (lower = higher priority).
- `meta.generation` — `latest` / `classic` array (advisory; a `latest`-only page
  that surfaces in Self-hosted breaks the build — use both when unsure).
- `published` — creation date on new pages only; never pair it with a first-publish
  changelog entry.

Detect which optional fields the neighbourhood uses by sampling 2–3 adjacent pages;
never strip unknown/pre-existing fields.

Full field rules (source of truth):
`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/frontmatter-guidelines.md`

## Notes

- A warn-only `PostToolUse` hook (`changelog-owners-reminder`) reminds about these
  same checks if this skill did not fire; applying the conventions here keeps it
  silent.
- This does not duplicate the repo's CI (`pnpm docs:lint`); it gets the
  frontmatter right at edit time so the PR is not bounced later.

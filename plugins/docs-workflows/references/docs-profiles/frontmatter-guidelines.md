# example-docs frontmatter fields — writing guidelines

Single source of truth for the **frontmatter metadata fields** on example-docs
pages. Companion to
[`changelog-guidelines.md`](changelog-guidelines.md) (the `changelog:` property)
and [`default-owners.txt`](default-owners.txt) (the `owners:` block) — those two
conventions are documented separately and only cross-linked here.

Applied by the `docs-frontmatter` skill and the `/document` docs
pipeline (`doc-planner` plans, `doc-writer` writes, `doc-reviewer` checks) **only
under the example-docs profile** — a generic docs repo is unaffected by the
`## Fields` below. The one exception is the last section, *Reserved keys for the
docs-workflow family*, which binds **any** docs repo the family writes into.

## Fields

### `title` (required)

Concise, sentence-case page title. No trailing period.

### `description` (required — SEO)

The search-result / social-preview snippet. **120–160 characters.** Shorter
under-describes the page for SEO; longer is truncated in results. A description
outside this band is a **warning**, not a hard block.

### `meta.content-type` (mandatory)

Mandatory metadata on every new page; visible in the page header. Implements the
Diátaxis content model extended with product-specific types. One of:

| Value | Use |
|---|---|
| `how-to` | Task/goal-oriented "how-to guide" |
| `tutorial` | Learning-oriented, step-by-step |
| `explanation` | Concept / background |
| `reference` | Options, flags, schema fields, API |
| `get-started` | Getting-started guide |
| `troubleshooting` | Problem/resolution |
| `upgrade` | Upgrade guide |
| `best-practices` | Best-practices guide |
| `app` | An app's documentation |
| `extension` | An extension's documentation |
| `release-notes` | Release-notes pages — **never authored by `/document`**: `/release-notes` drafts the note; listed for completeness only |

- **`overview` is deprecated — never set it on new content.**
- A missing or invalid `content-type` on a **new** page is a **BLOCKER** at review.

### `meta.i18n-priority` (optional)

An integer translation-priority signal (lower = higher priority). Advisory —
set it when the page's translation priority is known; otherwise omit.

### `meta.generation` (advisory)

Array of `latest` / `classic` (both experiences → `[classic, latest]`). Governs
which product experience the page applies to. **Build caveat:** a page tagged
`latest`-only that also surfaces in the Self-hosted docs breaks the build — when in
doubt for cross-experience/deployment/API/CLI content, use both. Advisory here;
match the convention on adjacent pages.

### `published` (new pages only)

Creation date (`YYYY-MM-DD`) on brand-new pages. Do **not** add a `changelog:`
entry on first publish — the `published` timestamp is used instead (see
[`changelog-guidelines.md`](changelog-guidelines.md)).

## Detecting conventions

Field presence and shape vary by area. Sample 2–3 adjacent pages under the
target's directory to confirm which optional fields (`tags`, `readtime`,
`solution`, `core-technology`, `app-id`, …) the neighbourhood uses, and match
them. **Never strip unknown/pre-existing frontmatter fields** — union, don't
replace.

## Enforcement summary (doc-reviewer)

| Field | Severity when wrong/absent |
|---|---|
| `meta.content-type` (new page) | **BLOCKER** — missing or not in the enum |
| `description` | **warning** (MAJOR/MINOR) — outside 120–160 chars |
| `title` (new page) | MAJOR — missing |
| `meta.i18n-priority`, `meta.generation` | advisory note only |

## Reserved keys for the docs-workflow family

Design authority: `docs/superpowers/specs/2026-08-29-docs-workflow-family-design.md` §8.6, D18 (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-08-29-docs-workflow-family-design.md` retrieves it). The docs-workflow family reserves four frontmatter keys — `type`, `audience`, `visibility`, `unit` — on **any** docs repo its commands scaffold or write into, not only one carrying the example-docs profile, and touches nothing else in this skill's territory; the reservation binds `/docs-audit`, which ships and reads one of them — `unit`, to match a page back to its backlog unit (`### unit` below) — and the family's later commands, `/docs-write` among them, as they ship. What is unchanged: the fields above, and `docs-frontmatter`'s ownership of the schema as a whole, are unchanged by this section.

### `type` (RESERVED)

Diátaxis or engineering type; the same vocabulary as a backlog unit's `type`, which is the coverage grid's second axis (`references/docs-audit/coverage-model.md` §3). The grid is computed from the backlog's `units[]`, not from this key. The vocabulary depends on `audience`:

| `audience` | `type` values |
|---|---|
| `user` | `tutorial \| how-to \| reference \| explanation` |
| `engineering` | `architecture \| decision \| runbook \| api-reference` |

### `audience` (RESERVED)

`user` or `engineering`.

### `visibility` (RESERVED)

`public` or `internal` — the build the page belongs to. The shipped two-build split does not read this key: it decides by path, a page being internal because it sits under `docs/internal/` (`references/docs-workflow/visibility.md` §1), and every directory stub the scaffold writes carries the value its path implies. It **defaults from `audience` but is independently settable** (D12): API reference is engineering-audience and usually public; a runbook naming hostnames is not.

### `unit` (RESERVED)

The backlog unit id. **It has a reader today and no automated writer**, which is the asymmetry to hold on to: `/docs-audit --refresh` reads it to match an existing page back to its unit and move that unit's `status` (`references/docs-audit/backlog-format.md` §3), and it never writes it — that command writes no documentation content at all. Putting the id onto a page is a person's act on the route the family actually supports today; `/docs-write` (a later spec) is to take that over, and drift (`/docs-drift`, a later spec still) is to read it as well. Every stub `/docs-init` scaffolds leaves it absent, so a page acquires it when somebody claims a backlog unit for it.

### Related fields, none of them reserved

- `order` — generates the nav. Without it MkDocs takes order from `mkdocs.yml` and the field is decorative.
- `review_by` — the calendar backstop for rot no diff can see: a page can go wrong with no code change at all.
- `evidence` — what the page's claims rest on.
- `readtime` is **computed**, never typed: word count divided by ~200 wpm, refreshed on every write. A hand-maintained reading time is wrong within two edits.

`changelog` and `owners` keep their own conventions ([`changelog-guidelines.md`](changelog-guidelines.md) and [`default-owners.txt`](default-owners.txt)) and are unaffected by this section.

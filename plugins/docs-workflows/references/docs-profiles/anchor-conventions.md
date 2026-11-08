# Anchor conventions (example-docs)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

How `/document` authors, links, and verifies heading anchors on example-docs
pages — the `{:#id}` syntax, the link forms that reference an anchor, the
`docstack` tool that validates them, and the rule for reconciling a docs anchor
against a product deep link.

This is the single source of truth for the mechanics. `doc-writer` (authoring
anchors and links), `doc-reviewer` (dimension 5 — structural integrity), and
`doc-planner` (planning section anchors for cross-links) all cite it; none
inlines these facts. The counts below were measured on 2026-08-10 against the
docs repo mounted at `/workspace/docs` (`cloud/_content` + `self-hosted/_content`)
and are cited so no future run re-derives them.

## 1. One `{:#id}` per heading — multi-anchor is unsupported

A heading carries at most one hardcoded anchor, written as a kramdown-style
`{:#id}` suffix on the heading line:

```markdown
## Configure the connector {:#configure-connector}
```

**1,580 files** under `cloud/_content` + `self-hosted/_content` use this
single-anchor syntax (`grep -rEl '^#{1,6} .*\{:#[a-zA-Z0-9_-]+\}\s*$'`).
Multi-anchor syntax on one heading — `{:#a #b}`, aliasing two ids to the same
section — appears **0 times** in the repo (`grep -rE '\{:#[^}]*#'`).

**Multi-anchor is unsupported.** Do not author `{:#a #b}` expecting either id
to resolve; if a section needs a second stable id, add a second heading instead
of stacking ids on one heading.

## 2. Link forms

The table has four rows. Each is either measured against the docs repo in this
pass or cited to an existing convention — the Occurrences column says which.
Use the whole-page form when the target is the page itself, the cross-page form
when linking into a specific section of another page, the same-page form only
within the page that owns the anchor, and the tabgroup form when the link
target is a specific tab rather than a heading-owned section.

| Form | Purpose | Occurrences |
|---|---|---|
| `[text](<postid>)` | whole page | not measured in this pass — cited to the existing `internal_links.convention` |
| `[text](<postid>#<anchor>)` | cross-page section | 19,560 (measured) |
| `[text](#<anchor>)` | same-page section | 4,006 (measured) |
| `{{#tabgroup anchor='id'}}` | mints an anchor on a tab group | 698 (measured) |

The `{{#tabgroup anchor='id'}}` form is distinct from the heading-level
`{:#id}` syntax in §1 — it mints an anchor on the tab group component itself,
not on a heading, and is the form to use when the link target is a specific tab
rather than a section.

## 3. Tooling — `validate-anchors`

The example-docs repo's `docstack` CLI (invoked via the `docstack` script in
the example-docs repo's own `package.json`:
`"docstack": "node .docstack/dist/apps/cli/bin/cli.mjs"`; it is not a
standalone binary and is not exposed as its own npm script) exposes a
`validate-anchors` command:

```bash
pnpm docstack validate-anchors
```

Its registered description is **"Validate if anchors point to hardcoded ids."**
An anchor link must target a hardcoded `{:#id}` (§1) — not an id the build
generates automatically from heading text — or `validate-anchors` flags it.
Run this before relying on a newly authored anchor link.

## 4. Reconciling a product deep link

Product code sometimes deep-links straight into a docs page section, e.g. a
UI element that opens `.../some-page#some-anchor`. When shipped product code
deep-links to `#some-anchor` on a docs page, **the docs page's authored anchor
matches the product's** — the product is the harder side to change and ships
on its own release cycle, so the docs page conforms to it, not the reverse.

**Anti-pattern, named explicitly:** do not defer this reconciliation on an
in-session judgment that the anchor syntax "appears unsupported." That
judgment is not a substitute for checking §1–§3 above, and it is exactly the
kind of unverified hunch this reference exists to prevent from being
re-derived per run.

If the docs anchor genuinely cannot be made to match the product's deep link
(for example, the target section was restructured and no single heading
maps to it), do not resolve the mismatch silently — record it and route it
through the normal Phase 5.8 discrepancy-escalation path (see
`workflows-core:source-truth` §7 for the protocol: take the decision a
conformance record already holds where an open entry matches the claim
by its requirement (§7.8, Phase 5.8 step 0); otherwise present the
analysis, ask the user, and record the decision — never pick a side on
the run's own judgment).

## 5. Consumers

- `doc-writer` — authors anchors on new/edited headings and the link forms in
  §2 that reference them.
- `doc-reviewer` — dimension 5 (structural integrity) checks anchor form
  against §1 and the `validate-anchors` contract in §3.
- `doc-planner` — plans section anchors for cross-links when the checklist
  calls for linking into a specific section of another page.

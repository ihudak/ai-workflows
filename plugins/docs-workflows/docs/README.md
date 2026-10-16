# docs-workflows documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| see how the seven commands fit together | [Workflow overview](workflow.md) |
| go from no documentation at all to a populated portal | [The documentation route](docs-workflow.md) |
| start documenting a project that has no docs | [`/docs-init`](commands/docs-init.md) |
| work out what documentation the product is missing | [`/docs-audit`](commands/docs-audit.md) |
| know what to do with the backlog `/docs-audit` wrote | [The documentation route](docs-workflow.md) |
| document a feature from its PRD and its shipped diffs | [`/document`](commands/document.md) |
| make a one-off prose edit in a docs repo | [`/document`](commands/document.md) — direct mode |
| teach this plugin what a docs repository looks like | [`/docs-profile`](commands/docs-profile.md) |
| pick up a logo and brand colours from the product's own code | [`/docs-brand`](commands/docs-brand.md) |
| serve the docs and get a URL to open in a browser | [`/docs-serve`](commands/docs-serve.md) |
| draft the note that announces a change | [`/release-notes`](commands/release-notes.md) |
| keep internal pages out of a published documentation site | [Documentation visibility](reference/docs-visibility.md) |
| understand what a run cost | [Session cost](reference/session-cost.md) |

Three pages orient you before you touch a command: [Getting started](getting-started.md) installs the plugin and sets the environment variables it reads, [Workflow overview](workflow.md) shows the seven commands as one diagram, including the two modes of `/document`, and [The documentation route](docs-workflow.md) is the ordered procedure from an empty repository to a populated portal — the steps that run a command and, written out in full, the ones you do by hand. Every other page below documents one command, one shared subsystem, or one whole inventory.

## Commands

- [`/docs-init`](commands/docs-init.md) — scaffold a documentation repository for a project that has none: a product-shaped page skeleton with a stub in every section, two builds over one content root, Vale, a CI workflow with the visibility gates, and the profile `/document`, `/docs-serve`, `/docs-brand` and `/docs-audit` read.
- [`/docs-profile`](commands/docs-profile.md) — scan a documentation repository and write or refresh the machine-readable profile `/document` consumes, as a reviewable pull request.
- [`/docs-brand`](commands/docs-brand.md) — extract a logo and a rough primary/accent colour pair from a product's own code and apply them to the docs site, standalone or `--inline` from `/docs-init`.
- [`/docs-serve`](commands/docs-serve.md) — start, stop, or check a profiled repo's dev server, and report a URL that actually opens from the host.
- [`/docs-audit`](commands/docs-audit.md) — enumerate what documentation the product is missing, from its own code and the specs tree, into a coverage grid and a prioritised backlog you keep in the repository.
- [`/document`](commands/document.md) — write or update product documentation: a one-shot direct edit, or the full keyed feature-documentation workflow.
- [`/release-notes`](commands/release-notes.md) — draft a release-notes Summary for a resolved PRD, shaped by the destination it resolves to.

## Reference

- [Agents](reference/agents.md) — the subagent inventory: what each of the eleven agents does and which command dispatches it.
- [References](reference/references.md) — the reference-doc inventory under `references/`, grouped by concern.
- [Skills](reference/references.md#skills) — the one bundled skills entry, `docs-frontmatter`: what it is for, and whether it is user-invocable.
- [Environment](reference/environment.md) — every environment variable the plugin reads, and what it configures.
- [Hooks](reference/hooks.md) — the two bundled hooks and what each one does.
- [Documentation visibility](reference/docs-visibility.md) — the two-build public/internal model a scaffolded portal uses, the two traps that make the obvious checks useless, and the CI gates that assert on built output instead.
- [Coverage model](reference/docs-coverage-model.md) — what counts as a documentation surface and how the seven kinds are found — five in code, two in the specs tree — how a surface differs from a backlog unit, which page types a surface earns, and what decides the order they get written in.
- [Documentation backlog](reference/docs-backlog.md) — the file an audit writes and you keep: where it lives, what each block holds, the states a page moves through and which of them anything automates yet, and what the coverage fraction actually counts.
- [Evidence and walkthroughs](reference/docs-evidence.md) — what a page's claims are allowed to rest on for each audience, the three kinds of evidence, what an unverified claim looks like on the page, and how to walk a verification checklist by hand.
- [Session cost](reference/session-cost.md) — which commands here emit a cost entry, what they charge to, and where the file lands.

## Where the rest lives

This plugin is the documentation half of a family. Four sibling plugins matter to it — two it declares as dependencies, and two whose output it reads without depending on either:

- **`workflows-core`** — the shared reference corpus every command here loads through the `reference` skill (addressing, the specs-repo git and phase-handoff entry points, model routing, escalation and finding triage, cost/feedback/follow-up emission, docs grounding, doc-structure conventions, the PRD format), plus the `doc-fixer` and `impl-maintenance` agents these commands dispatch. It is a declared dependency, so installing this plugin installs it.
- **`prose-style`** — the complementary semantic prose pass `docs-style-checker` runs alongside the repo's own linter, and the fallback linter when a repo configures none. Also a declared dependency.
- **`product-workflows`** — the product-definition half of the pipeline, which produces the idea, the PRD, the ARD, the specification and the Epics that `/document` and `/release-notes` read.
- **`dev-workflows`** — the build half, which produces the design and the implementation: the record of what was built, and the commits whose diffs a keyed run summarises.

Neither pipeline plugin is a dependency in either direction; this plugin installs and runs without either of them, against a specs tree someone else filled in.

## Status

This plugin ships 7 slash commands, 11 agents, 24 reference files and 2 hooks — and it ships one bundled skills entry, `docs-frontmatter`. Most of it moved here from `dev-workflows` in the third increment of the marketplace split, and behaves as it did there but for one deliberate change: `prose-style` is now a declared dependency, so the branches that used to skip or degrade the style check when it was absent are gone. Otherwise only the namespace these commands answer to and the way they reach the shared corpus have changed. The `preload-context` hook is the one thing that was split rather than moved, because `dev-workflows` still needs its half.

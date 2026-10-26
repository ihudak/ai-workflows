# prose-style

A pluggable prose style checker and writing aid for Claude Code. It checks the writing in product documentation, planning documents (Epics, PRDs, ARDs), release notes and any other prose that should read consistently — terminology, voice and tone, grammar, formatting, UI interaction verbs, inclusive language, and the accessibility of the prose itself.

It ships a **vendor-neutral baseline**, so it is useful with no configuration at all, and it **layers your organization's own style guide on top** when you point it at one. Every resolution miss falls back silently to the baseline.

This plugin ships three slash commands — [`/prose-review-pr`](docs/commands/prose-review-pr.md), [`/prose-review-docs`](docs/commands/prose-review-docs.md) and [`/prose-style-refresh`](docs/commands/prose-style-refresh.md) — two agents, `prose-style-checker` and `prose-fixer`, the `prose-style-rules` skill, and the eight baseline reference files under `references/`. `docs-workflows` and `product-workflows` install it as a declared dependency and run its checker on their own drafts.

See [the documentation index](docs/README.md) for installation, the overlay, and the full command, agent and reference inventory.

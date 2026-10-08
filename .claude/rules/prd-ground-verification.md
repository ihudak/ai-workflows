---
paths:
  - "plugins/product-workflows/**"
  - "plugins/dev-workflows/commands/design.md"
  - "plugins/dev-workflows/commands/ready.md"
  - "plugins/dev-workflows/commands/implement.md"
  - "plugins/workflows-core/references/addressing.md"
  - "plugins/workflows-core/commands/frames.md"
  - "plugins/docs-workflows/commands/document.md"
  - "plugins/docs-workflows/commands/release-notes.md"
---

# `/prd-ground` — blind verification

Loaded with `.claude/rules/brd-route.md`, whose `paths:` it shares. Split out of `.claude/rules/brd-route.md` to keep that file under 20,000 characters; the route's map lines, `/prd-ground`'s among them, and its other invariants are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

- **`/prd-ground`'s verification is blind by construction, batched, and never weakened per finding.** The derive dispatch carries a finding's premise and source and never its `verdict`, `evidence`, `control` or `cites` (`workflows-core:grounding-format` §8); a batch's composition never depends on a finding's answer; and every finding in Phase 7's verification set gets its own Opus re-derivation on every run — no cheaper tier, no sample, no repository-scope finding standing in for the ones under it, and no outcome carried forward from an earlier run; an on-file finding this run could not verify keeps the outcome it had and is reported as not verified by this run — it is never reported as verified — and an own-run one stops the run. Read the rationale before proposing any of those as a saving. ([why](../../docs/maintainers/rationale.md#verifier-blind-batched))

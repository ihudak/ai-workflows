---
paths:
  - "plugins/product-workflows/**"
  - "plugins/dev-workflows/commands/design.md"
  - "plugins/dev-workflows/commands/ready.md"
  - "plugins/dev-workflows/commands/implement.md"
  - "plugins/dev-workflows/commands/conformance.md"
  - "plugins/workflows-core/references/addressing.md"
  - "plugins/workflows-core/references/cost-emission.md"
  - "plugins/workflows-core/commands/frames.md"
  - "plugins/docs-workflows/commands/document.md"
  - "plugins/docs-workflows/commands/release-notes.md"
  - "plugins/security-workflows/commands/scan.md"
---

# `/prd-ground` — blind verification

Loaded with `.claude/rules/brd-route.md`, whose `paths:` it shares. Split out of `.claude/rules/brd-route.md` to keep that file under 20,000 characters; the route's map lines, `/prd-ground`'s among them, and its folder-kind invariants are there, the sibling re-cut's in `.claude/rules/brd-route-recut.md`; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

- **`/prd-ground`'s verification is blind by construction, batched, and never weakened per finding.** The derive dispatch carries a finding's premise and source and never its `verdict`, `evidence`, `control` or `cites` (`workflows-core:grounding-format` §8); a batch's composition never depends on a finding's answer; and every finding in Phase 7's verification set gets its own Opus re-derivation on every run — no cheaper tier, no sample, no repository-scope finding standing in for the ones under it, and no outcome carried forward from an earlier run (what counts as one is the next invariant); an on-file finding this run could not verify keeps the outcome it had and is reported as not verified by this run — it is never reported as verified — and an own-run one stops the run. Read the rationale before proposing any of those as a saving. ([why](../../docs/maintainers/rationale.md#verifier-blind-batched))
- **An earlier session of this run is not an earlier run** (`docs/superpowers/specs/2026-11-24-run-folder-design.md`, D14). A run lasts from its first start until it finishes or the user chooses *Start over*, so a session that resumes a stopped `/prd-ground` from its run folder continues the same run, and reuses this run's own saved `mode: derive` and `mode: compare` results wherever their fingerprints still match (`commands/prd-ground.md` Phase 5, *Saved dispatches*). A saved verifier result whose agent file or model has changed since is redone, save one the user keeps by answering *Resume and keep them*, and never kept where it was written below Opus (Phase 2, `This command's own rule withholds *keep*`). *Start over* deletes the run folder, and a run that finishes removes it, so no earlier run's outcome is ever reused. Where the run keeps a folder, every derive dispatch runs in its `blind` area, apart from every grounder's result, and `grounding-verifier` in derive mode reads nothing under the run folder but its own `result_path` file. A change that reuses a verifier result across *Start over* or from another run, or that puts a derive dispatch's input or result where a grounder's lies, breaks the invariant above. ([why](../../docs/maintainers/rationale.md#verifier-blind-batched))

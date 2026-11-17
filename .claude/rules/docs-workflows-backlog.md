---
paths:
  - "plugins/docs-workflows/**"
  - "plugins/product-workflows/commands/epics.md"
  - "plugins/product-workflows/agents/epic-*.md"
  - "plugins/product-workflows/docs/commands/epics.md"
---

# docs-workflows — the docs backlog: `/docs-audit` and the backlog runs

Loaded with `.claude/rules/docs-workflows.md`, whose `paths:` it shares. Split out of `.claude/rules/docs-workflows.md` to keep that file under 20,000 characters; the plugin's other rules are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Workflow map

```
/docs-audit          → [resolve-docs-repo (signal-positive)] → resolve <top> + read the profile → [confirm/record source_repos[] where the key is absent — recorded only where a profile exists] → [require nothing on main: this command gates on no prior phase] → [code-scanner×N over the recorded repos (parallel, cap 4, default branch — the session's own repository on another branch read there by ref, `workflows-core:scan-refresh`'s fixed-policy case) + the caller's own $SPECS_PATH read for the `decision` and `release` kinds] → [§8.5 seeded round 2; a theme still unresolved is named, never flattened into a gap] → [docs-auditor: surfaces[] with volatility from git log density] → [ia-planner@Opus: cross each surface with the types it earns, rank on four signals, propose tutorial candidates] → [mint a picked tutorial candidate — --refresh only] → write .dev-workflows/docs-backlog.yml + reconcile existing pages by their `unit:` frontmatter key → [docs-audit-reviewer@Opus] → [triage: verify each finding; the orchestrator applies survivors — no fixer and no re-review (D25)] → impl-maintenance → commit-artifacts   (no branch and no commit in the docs repo: the backlog is left in the working tree for the operator to review and commit; resolves no docs grounding (`.claude/rules/docs-grounding.md`); its cost and feedback land under $SPECS_PATH/documentation/<docs-repo-slug>/, ahead of pending, because this run has no PRD and never will — D19; report-only if misrooted)
                      └── docs-auditor (docs-workflows)       (used by /docs-audit)
                      └── ia-planner (docs-workflows)         (used by /docs-audit)
                      └── docs-audit-reviewer (docs-workflows) (used by /docs-audit)
```

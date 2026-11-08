---
paths:
  - "plugins/workflows-core/**"
  - "plugins/*/commands/*.md"
  - "plugins/*/agents/*.md"
---

# workflows-core — the model-routing authority and its callers

Loaded with `.claude/rules/workflows-core.md`, whose `paths:` it shares: the callers below change when a command or agent in another plugin does. Split out of `.claude/rules/workflows-core.md` to keep that file under 20,000 characters; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Model routing reference

`plugins/workflows-core/references/model-routing/classification.md` is the
**single source of truth** for:

- Task complexity classification (`SIMPLE` / `MODERATE` / `SIGNIFICANT` /
  `HIGH-RISK`)
- The model fallback chain (Opus 5.5 → 5 → 4.8 → 4.7 → 4.6 → Sonnet 5.5 → Sonnet 5 → Sonnet 4.6 → Sonnet 4.5)
- The mandatory Opus code-review checklist
- The `model_routing` YAML handoff block shared between commands and agents
- The `phase: verify-resume` protocol for review-gated verification
- The large-input scan fan-out policy (§8): the input-shape trigger, the `resolved-folder read → parallel code-scanner (cap 4) → Opus synthesis` pattern, the SIGNIFICANT floor it imposes, and §8.5's opt-in seeded second round with its rule that an unresolved theme is named, never flattened into a gap ([why](../../docs/maintainers/rationale.md#model-routing-fan-out))
- `defect-reporter`'s tier: under `--skip-feedback` it runs on the §2.1 Sonnet chain, the tier of the `impl-maintenance` it replaces (recorded as `defect_model` in the `model_routing` block). No `classification.md` chain names Haiku; the Haiku rows the `haiku` alias resolves against, which serve as Haiku's chain wherever `run-flags` says chain row, are `workflows-core:run-flags` §2's ([why](../../docs/maintainers/rationale.md#defect-reporter-tier))
- §10, enforced model — `run_flags.enforced_model` (`workflows-core:run-flags`) bypasses every chain's own per-step selection: every `model_routing` field naming a **dispatched** step (never the orchestrator's own inline work) resolves to the enforced id, every dispatch passes it as `model:` explicitly (overriding a frontmatter pin) in §5's dispatch form (the id itself where the tool's `model` parameter accepts ids; its family name in a §2 family-only harness, where `run-flags` §2 honours only a bare family alias or its family's newest chain row), a nested dispatch propagates it to its own `task` calls, and every gate or degrade path that tests `current_model` for an Opus session does not fire

## Model routing callers

Thirty commands invoke the `workflows-core:model-routing` skill (`grep -l 'workflows-core:model-routing' plugins/*/commands/*.md | wc -l`) and must load and follow `plugins/workflows-core/references/model-routing/classification.md` at the start of every invocation: `/design`, `/implement`, `/ready`, `/conformance`, `/upgrade`, `/vuln` — all six of `dev-workflows`'s — `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/update-spec`, `/epics`, `/brd-intake`, `/prd-ground`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`, `/prd-proposal`, `/brd-proposal`, `/promote-decisions` — sixteen of `product-workflows`'s seventeen — plus six of `docs-workflows`'s seven (`/document`, `/docs-profile`, `/release-notes`, `/docs-init`, `/docs-brand`, `/docs-audit`), `workflows-core`'s own `/frames` and `security-workflows`' one, `/security-workflows:scan`. The remaining commands (`/docs-serve`, `/harvest-decisions`, `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`, `/statusline`, `/diagnose-session` — one of `docs-workflows`'s seven, one of `product-workflows`'s seventeen and six of `workflows-core`'s seven) are exempt — `/docs-serve` starts a process and reports a URL, with no task to classify, `/harvest-decisions` runs a bundled script with no model judgement, `/diagnose-session`'s `session-analyst` is pinned by its own frontmatter, and `/feedback` names `model-routing` only as one of its friction categories, which is not a load. An agent that reads a field of the `model_routing` block receives it in its prompt — its handoff file declares the input, and §4's list is the authority; every other agent is sent none and has its tier pinned by its own frontmatter or by the dispatch's `model:` argument. No agent re-reads it for routing; `code-review`, `code-writer` and `risk-planner` load it for its criteria, `code-writer` for §1.1's triggers alone (`grep -ln 'args: "model-routing' plugins/*/agents/*.md` returns the three).

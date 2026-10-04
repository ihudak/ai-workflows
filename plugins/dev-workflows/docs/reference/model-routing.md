# Model routing reference

Every command here classifies its own task before doing real work, and that classification decides how much planning, authoring, and review rigor the rest of the run applies — and, for one command, which model the session itself must be running on. This page covers the four things a user can observe or influence about that; the full policy — including the mechanics agents don't need restated here — lives in `workflows-core:model-routing/classification`, named again at the end.

## What gets classified

| Class | Plain meaning |
|---|---|
| `SIMPLE` | Trivial, mechanical, low blast radius — a typo, a comment, a single-line tweak. |
| `MODERATE` | A localized feature or fix in 1–3 files, well-understood, no security implications. |
| `SIGNIFICANT` | Multi-file or cross-cutting, non-trivial design, real correctness risk. |
| `HIGH-RISK` | Security-, data-, or contract-sensitive — a mistake here causes an outage or a breach. |

All five commands in this plugin load the `model-routing` skill, run this classification as an early step, and state their class plus a one-line reason: `/implement`, `/vuln`, `/upgrade`, `/design`, and `/ready`. Twenty-one more do the same from the companion plugins that ship them (`grep -l 'workflows-core:model-routing' plugins/*/commands/*.md`, run from the repository root, returns all twenty-six): `/workflows-core:frames`; `product-workflows`'s `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, the six commands of the BRD-to-PRD route, and its two effort-proposal commands `/prd-proposal` and `/brd-proposal`; and `docs-workflows`'s `/docs-workflows:document`, `/docs-workflows:release-notes`, `/docs-workflows:docs-profile`, `/docs-workflows:docs-init`, `/docs-workflows:docs-brand` and `/docs-workflows:docs-audit`. Each command has a typical class for its own kind of work (an implementation run is typically `MODERATE` unless it is given more than one repository) but escalates when the task in front of it warrants it. What over-escalating costs differs by command — from an extra Opus planner call to a hard stop requiring an Opus session (`## What classification changes` below has the breakdown) — while misclassifying downward can ship bugs regardless of which command you're running, so the policy's own rule is to escalate one level whenever in doubt.

## What classification changes

`SIMPLE` and `MODERATE` continue on whatever model the session is already running, with nothing extra added on their account.

`SIGNIFICANT` and `HIGH-RISK` change different things depending on which command you're running, because three distinct patterns share this classification:

- **`/implement` and `/upgrade`** delegate planning (or a planning critique) to a dedicated Opus sub-agent (`risk-planner`) before implementation starts — or, for `/implement`, mid-implementation, where a raise calls for it (below) — then add a separate Opus `code-review` gate afterward, before tests run; at `SIMPLE`/`MODERATE` neither one is dispatched at all.
- **The reviewer-gated authoring commands** — `/design` and `/ready` here — already run their own reviewer agent on Opus by a fixed frontmatter pin (`design-reviewer`, `readiness-reviewer`), regardless of classification (except under `--enforce-model`; see below). There is no separate delegated planner sub-agent in this pattern. What classification changes here is grill depth and authoring rigor, not whether the review runs on Opus — [Agents reference](agents.md) carries the complete list of which agents are pinned and which commands dispatch them. The companion `product-workflows` plugin's own `/create-prd`, `/create-ard`, `/specify`, and `/epics` follow the same pattern with their own reviewers, documented on that plugin's model-routing page.
- **`/vuln`** is a third: it runs the same Opus `code-review` gate, triage, and `review-fixer` cycle at `SIGNIFICANT`/`HIGH-RISK`, but dispatches no `risk-planner` and has no frontmatter-pinned authoring reviewer of its own.
- **`/design` adds a further, stricter gate:** at `SIGNIFICANT`/`HIGH-RISK` it will not author against a weaker model — it requires the session itself to already be running on an Opus-tier model, because its authoring happens inline rather than through a delegated sub-agent. If it isn't, the run stops and offers to relaunch on Opus, with an explicit override to proceed anyway that gets logged in the final report (except under `--enforce-model`, which does not fire this gate at all; see below) — unless no Opus tier is reachable at all, in which case the stop stands but the relaunch offer does not, there being nothing to relaunch onto: the choice is then to proceed on the Sonnet floor or cancel. The companion `product-workflows` plugin's `/create-ard` gates the same classification on the same condition, the session's own current model, and its `/specify` and `/create-prd` don't gate this way at all; they degrade to the best available model and record the degradation instead of stopping.

## What floors or raises a classification

`/implement` has one classification floor beyond the ordinary triggers: **multi-source input**. Handing it more than one code repository, or any directory input (a saved file folder, or a spec/design folder), floors the run at `SIGNIFICANT` even if nothing else about the change looks that size — a large multi-source brief is cross-cutting by nature, and it also triggers a parallel per-repo scan fan-out documented in the full policy below. The floor is overridable at plan approval if you judge the work genuinely smaller than its input footprint suggests.

`/implement`'s class can also rise after Phase 1.5, before any file is written: Phase 2A re-tests it against the ordinary triggers once its plan names the steps and files the change touches, and again after every revision of that plan — after a down-classification you accepted at plan approval, only on a trigger a later revision adds, so the re-test never undoes your acceptance. A raise is overridable at plan approval exactly as the floor is. A run planned as `SIMPLE`/`MODERATE` that first meets, while implementing, a trigger its plan did not name (one of the classification policy's concrete triggers, such as a schema or migration, authentication, a public contract, concurrency or more than 3–5 non-test files; not its catch-all of unclear requirements, large unknowns or otherwise high blast radius, whose unknowns are asked about instead) is raised too and re-planned with `risk-planner` — and, should you accept a down-classification there, continues on its plan at the lower class.

## The fallback chain

Every `SIGNIFICANT`/`HIGH-RISK` Opus step resolves against the same ordered list, taking the first model available in the environment:

1. `claude-opus-5-5`
2. `claude-opus-5`
3. `claude-opus-4-8`
4. `claude-opus-4-7`
5. `claude-opus-4-6`
6. `claude-sonnet-5-5` (fallback only — the report notes that no Opus was available)
7. `claude-sonnet-5` (further fallback)
8. `claude-sonnet-4-6` (further fallback)
9. `claude-sonnet-4-5` (further fallback — the report notes "no Opus or Sonnet 5.5/5/4.6 available")

Where the environment's agent tool selects models by family name only (`opus`, `sonnet`, `haiku`, `fable`), as Claude Code's does today, a row counts as available when its family is: the chain lands on the first row of an available family, the dispatch passes that family's name, and which version of the family runs is the harness's choice rather than the run's. The run's routing record still names the row it resolved.

`claude-sonnet-4-5` is the floor, except where you enforce one model ([below](#enforcing-one-model)), which bypasses this list altogether. If nothing in the list is available, the run stops and asks how to proceed rather than silently downgrading. You never pick a model for any of this yourself — the orchestrator resolves the chain automatically against what your environment has available, and every downgrade from the top of the chain is announced in the run's own report rather than happening quietly.

## Enforcing one model

`--enforce-model=<model>` (persistent default: `WORKFLOWS_ENFORCE_MODEL`, read only by the companion `workflows-core` plugin) pins every subagent the command dispatches to one model, bypassing the fallback chain above. It overrides a frontmatter pin too — an agent pinned `model: opus`, such as `code-review` or `design-reviewer`, still runs on the enforced model, since the dispatch's own `model:` argument wins over the pin. What it does not change: classification still runs and still decides which steps happen — a `SIGNIFICANT`/`HIGH-RISK` task still gets its plan and review gates, just on the enforced model rather than the fallback chain's pick. The orchestrator itself is not switched — it cannot be, from inside a running command — so it stays on whatever model the session is already running under; when that differs from the enforced model, the run prints one relaunch advisory naming both rather than silently ignoring the mismatch. Every gate or degrade path that otherwise requires or prefers an Opus-tier session — `/design`'s HARD gate among them — does not fire under `--enforce-model`: the user already chose the model, and that one relaunch advisory is the only notice a session/enforced mismatch gets. **Where the agent tool selects models by family only**, as Claude Code's does today, a family alias (`opus`, `sonnet`, `haiku`, `fable`) enforces that family and the harness picks its version; a version-specific value (`opus5.5`, `claude-opus-5-5`) is honoured only when it names its family's newest model in the fallback chains (for Haiku, which no fallback chain names, in the Haiku rows `run-flags` keeps) — `claude-opus-5-5` for Opus, `claude-sonnet-5-5` for Sonnet, and `claude-haiku-4-5` for Haiku, so `haiku4.5` is accepted too — and then runs as the family name, so `--enforce-model=opus5.5` runs everything on the harness's Opus rather than guaranteeing Opus 5.5. An older version (`opus5`) stops the run before any work, saying the harness selects by family only and suggesting `--enforce-model=opus`. The report's `Model routing: bypassed` line says what the dispatches were actually passed, and what you asked for where that differs. The full mechanics — the alias table, precedence against the environment variable, and the two ways an invalid or unreachable model stops the run before any work happens — are `workflows-core:run-flags`'s, and the variable itself is documented on [`workflows-core`'s environment reference](../../../workflows-core/docs/reference/environment.md).

---

The full policy — the classification triggers in detail, the `model_routing` handoff block, the mid-tier detection chain used for mechanical steps, the mandatory Opus code-review checklist, the large-input scan fan-out, and enforced-model routing (§10) — is authoritative in `workflows-core:model-routing/classification`, a reference the companion `workflows-core` plugin ships rather than this one. This page is a summary of it, not a substitute for it.

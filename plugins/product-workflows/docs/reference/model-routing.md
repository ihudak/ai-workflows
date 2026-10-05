# Model routing reference

Every command here classifies its own task before doing real work, and that classification decides how much grilling depth and authoring rigor the rest of the run applies — and, for three commands, whether the session itself must be running on Opus. This page covers the four things a user can observe or influence about that; the full policy — including the mechanics agents don't need restated here — lives in `workflows-core:model-routing/classification`, named again at the end.

## What gets classified

| Class | Plain meaning |
|---|---|
| `SIMPLE` | Trivial, mechanical, low blast radius. |
| `MODERATE` | A localized brief or requirement set, well-understood, no unusual scope. |
| `SIGNIFICANT` | Multi-repo, cross-cutting, or an unusually large requirement/slice count. |
| `HIGH-RISK` | Security-, data-, or contract-sensitive — a mistake here misdirects the product itself. |

Fourteen of this plugin's fifteen commands load the `model-routing` skill, run this classification as an early step, and state their class plus a one-line reason: `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, `/brd-intake`, `/prd-ground`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`, `/prd-proposal`, and `/brd-proposal`. `/harvest-decisions` does not: it runs a bundled script with no model judgement, so there is no task to classify. Each command has a typical class for its own kind of work (a Product Requirements Document authoring run is typically `MODERATE`; an unusually large BRD requirement count or slice fan-out is typically `SIGNIFICANT`) but escalates when the task in front of it warrants it.

## What classification changes

`SIMPLE` and `MODERATE` continue on whatever model the session is already running, with nothing extra added on their account.

`SIGNIFICANT` and `HIGH-RISK` change different things depending on which command you're running, because two distinct patterns share this classification here:

- **The reviewer-gated authoring commands** — `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, `/prd-ground`, `/brd-package`, `/prd-proposal`, and `/brd-proposal` — already run their own reviewer agent on Opus by a fixed frontmatter pin (`prd-reviewer`, `ard-reviewer`, `spec-reviewer`, `epic-reviewer`, `grounding-verifier`, `brd-package-reviewer`, and `proposal-reviewer` respectively — seven pinned agents across nine commands, since `/create-prd` and `/update-prd` share one and the two proposal commands share another), regardless of classification (except under `--enforce-model`; see below). What classification changes here is grill depth and authoring rigor, not whether the review runs on Opus — [Agents reference](agents.md) carries the complete list of which agents are pinned and which commands dispatch them.
- **`/idea` has no reviewer at all** — its bounded grill (`--deep` for relentless) is the gate, and classification affects how relentlessly it grills rather than which agent gets dispatched.
- **`/brd-intake`, `/brd-split`, `/brd-interview`, and `/brd-reconcile` dispatch no Opus-pinned reviewer either** — the first's two Opus-pinned agents, `figure-reader` and `brd-reader`, extract rather than review, and the other three are interactive/interview commands whose only Opus-tier work, where any exists, is a reviewer another command in the route already ran. Classification here governs analysis depth (how thoroughly the defect walk, the allocation walk, or the reconciliation sweep is carried out), not a review gate.

**Three commands add a further, stricter gate** — `/create-ard`, `/prd-proposal`, and `/brd-proposal`. At `SIGNIFICANT`/`HIGH-RISK` none of the three will author against a weaker model: each gates on the session's own current model, exactly as the companion `dev-workflows` plugin's `/design` does, because in all three the authoring happens inline on that model rather than through a delegated sub-agent. If the session is not Opus-tier, the run stops and offers to relaunch on Opus, with an explicit override to proceed anyway that gets logged in the final report (except under `--enforce-model`, which does not fire this gate at all; see below) — unless no Opus tier is reachable at all, in which case the stop stands but the relaunch offer does not, there being nothing to relaunch onto: the choice is then to proceed on the Sonnet floor or cancel. `/specify` and `/create-prd` don't gate this way on the same classification — they degrade to the best available model and record the degradation instead of stopping.

## What floors a classification

**Four of those fourteen commands floor their classification at `SIGNIFICANT`, and all four floor for the same kind of reason** — what the run *produces or changes*, never how much of it there was to read. Four out of fourteen sharing one reason is a pattern in this plugin, not an exception:

- **`/prd-proposal` and `/brd-proposal`** — the run produces a number a customer will make a commercial decision on, and the format's own [residual-risk rule](proposal-format.md#the-risk-the-format-cannot-remove) states it plainly: a plausible number with a defensible-looking argument is more dangerous than an obviously rough one. An umbrella compounds it, because a reader checking one is checking a roll-up rather than a derivation.
- **`/brd-package`** — the adversarial self-review's own output gates the run (a self-review that finds nothing is a rubber stamp), and the rendered prompt is the one artifact this plugin produces that an outside party pastes into an agent and runs, with nobody from the delivery team present to correct it.
- **`/brd-reconcile`** — the run freezes customer authority into the decision register, and its propagation sweep writes dispositions into registers belonging to BRDs the run was never pointed at.

**None of the four is about size** — each says so in its own words, and a one-package tier-1 proposal floors exactly as a programme umbrella does, a two-question reconciliation exactly as a fifty-question one. **Past that the four differ, in two ways worth knowing before you read a run's `model_routing` block.** Two of them also document an escalation above the floor: `/prd-proposal` and `/brd-proposal` record `SIGNIFICANT | HIGH-RISK` and each names what would warrant the step up — a contested register or a baseline the operator already doubts, a slice excluded that a reader will expect to be there. `/brd-package` and `/brd-reconcile` record a bare `SIGNIFICANT` and floor there, with no escalation documented. And what the floor costs differs along the same line: for `/prd-proposal` and `/brd-proposal` it combines with the stricter gate above, so both need an Opus session or an explicit, logged override (except under `--enforce-model`, which does not fire that gate at all; see below), while `/brd-package` and `/brd-reconcile` degrade to the best available model and record the degradation instead of stopping.

**One command floors on its input instead, and it is the only one.** `/prd-ground` floors at `SIGNIFICANT` when Phase 1 resolved more than one repository — the repository half of the multi-source rule the companion `dev-workflows` plugin's `/implement` applies, cited by name in `/prd-ground`'s own Phase 2. So the distinction worth carrying is narrower than "nothing here floors on input": what is never a floor in this plugin is **the address** (in `/implement` it is one, a resolved specs folder being a folder input). A PRD, an Epic, or a BRD is always a single addressed item, and in this plugin addressing one is not a multi-source trigger — which is why `/idea` says outright that even a `--ground-code` run does not floor. What can be multi-source is how many repositories a grounding pass touches, and in the one command where that changes the risk, the floor is written down.

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

`--enforce-model=<model>` (persistent default: `WORKFLOWS_ENFORCE_MODEL`, read only by the companion `workflows-core` plugin) pins every subagent the command dispatches to one model, bypassing the fallback chain above. It overrides a frontmatter pin too — an agent pinned `model: opus`, such as `prd-reviewer` or `ard-reviewer`, still runs on the enforced model, since the dispatch's own `model:` argument wins over the pin. What it does not change: classification still runs and still decides which steps happen — a `SIGNIFICANT`/`HIGH-RISK` task still gets its full grill depth and review gate, just on the enforced model rather than the fallback chain's pick. The orchestrator itself is not switched — it cannot be, from inside a running command — so it stays on whatever model the session is already running under; when that differs from the enforced model, the run prints one relaunch advisory naming both rather than silently ignoring the mismatch. Every gate or degrade path that otherwise requires or prefers an Opus-tier session — `/create-ard`'s, `/prd-proposal`'s and `/brd-proposal`'s stops among them — does not fire under `--enforce-model`: the user already chose the model, and that one relaunch advisory is the only notice a session/enforced mismatch gets. **Where the agent tool selects models by family only**, as Claude Code's does today, a family alias (`opus`, `sonnet`, `haiku`, `fable`) enforces that family and the harness picks its version; a version-specific value (`opus5.5`, `claude-opus-5-5`) is honoured only when it names its family's newest model in the fallback chains (for Haiku, which no fallback chain names, in the Haiku rows `run-flags` keeps) — `claude-opus-5-5` for Opus, `claude-sonnet-5-5` for Sonnet, and `claude-haiku-4-5` for Haiku, so `haiku4.5` is accepted too — and then runs as the family name, so `--enforce-model=opus5.5` runs everything on the harness's Opus rather than guaranteeing Opus 5.5. An older version (`opus5`) stops the run before any work, saying the harness selects by family only and suggesting `--enforce-model=opus`. The report's `Model routing: bypassed` line says what the dispatches were actually passed, and what you asked for where that differs. The full mechanics — the alias table, precedence against the environment variable, and the two ways an invalid or unreachable model stops the run before any work happens — are `workflows-core:run-flags`'s, and the variable itself is documented on the companion `workflows-core` plugin's own environment reference page.

---

The full policy — the classification triggers in detail, the `model_routing` handoff block, the mid-tier detection chain used for mechanical steps, and enforced-model routing (§10) — is authoritative in `workflows-core:model-routing/classification`, a reference the companion `workflows-core` plugin ships rather than this one. This page is a summary of it, not a substitute for it.

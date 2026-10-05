# product-workflows

A role-based pipeline of 15 slash commands for the product-definition side of the workflow plugin family. Its spine runs idea refinement → Product Requirements Document → architecture → Epic breakdown → specification, with an Opus-backed review gate behind every artifact from the PRD onward — `/idea` is gated by its own bounded grill instead; alongside it sits a six-command BRD-to-PRD route that grounds a customer's requirements document, settles it with them, and seeds the PRD, ARD and specification the ladder above hands off to — its grounding step, `/prd-ground`, also runs optionally on the idea route's own PRD, after `/create-prd`. The table below is the complete list. The shared foundation every command here draws on — the addressing grammar, the git and phase-handoff entry points, model routing, escalation and triage, and the emitters — ships in the companion `workflows-core` plugin; the engineering half of the pipeline this hands off to — `/design`, `/implement`, `/ready` — ships in the companion `dev-workflows` plugin.

> Part of the `shipwright` marketplace — see the [repo-root setup guide](../../README.md) for marketplace install + prerequisites.

## What it does

| Role | Commands | What it does |
|------|----------|--------------|
| PM | [`/idea`](docs/commands/idea.md), [`/create-prd`](docs/commands/create-prd.md), [`/update-prd`](docs/commands/update-prd.md) | Refine a raw idea, then author or refresh the Product Requirements Document. |
| PM *(BRD route — inventory)* | [`/brd-intake`](docs/commands/brd-intake.md), [`/brd-split`](docs/commands/brd-split.md) | Intake a customer BRD verbatim, extract its inventory, then split it: on the root from a mandatory instruction to carve slices, and again on each grounded slice to allocate it. |
| PA *(grounding, either route)* | [`/prd-ground`](docs/commands/prd-ground.md) | Ground a slice's claims against code and design — mandatory on the BRD route, gating `/brd-split`; optional after `/create-prd` on the idea route. A root is never ground. |
| PM *(BRD route — customer loop)* | [`/brd-interview`](docs/commands/brd-interview.md), [`/brd-package`](docs/commands/brd-package.md), [`/brd-reconcile`](docs/commands/brd-reconcile.md) | Decide the BRD's open questions, package what only the customer can settle, then reconcile the review that comes back and sweep what it overturned. |
| PA *(optional)* | [`/create-ard`](docs/commands/create-ard.md), [`/harvest-decisions`](docs/commands/harvest-decisions.md) | Author an Architecture Requirements/Decision Document grounded in the mounted code, and keep the team's decisions where later ARDs find them. |
| PE | [`/epics`](docs/commands/epics.md), [`/specify`](docs/commands/specify.md) | Break a PRD into Epics, then author an org-standard specification through a grill. |
| PM *(effort proposal — optional, gates nothing on the build ladder)* | [`/prd-proposal`](docs/commands/prd-proposal.md) | Price one PRD folder: work packages, hours by role, a range from per-package confidence, every driver evidenced. Graded by readiness rather than gated on an ARD or a specification. |
| PM *(effort proposal — optional, gates nothing on the build ladder)* | [`/brd-proposal`](docs/commands/brd-proposal.md) | Roll a BRD container's priced slices into one programme umbrella: one row per included slice, the cross-slice effort no slice holds, and coverage from the root ledger. Not a sum. |

Fourteen agents (see [Agents](docs/reference/agents.md)) carry the BRD grounding and reconciliation, PRD/ARD/spec/proposal review, and Epic writing and review these commands share. Twelve reference pages (see [References](docs/reference/references.md)) define the BRD, code-defect-log, decision-register, coverage-ledger, customer-review, idea, ARD, specification and effort-proposal artifact formats, and the link walk `/brd-intake` and `/idea` share.

## Documentation

| Page | What's there |
|------|--------------|
| [Documentation index](docs/README.md) | The full "I want to…" lookup table, plus the command, agent, and reference inventories. |
| [Getting started](docs/getting-started.md) | Install, environment variables, and your first `/idea` run. |
| [Workflow overview](docs/workflow.md) | The fifteen commands as one diagram. |
| [Roles and phases](docs/roles-and-phases.md) | What PM, PA, and PE each own and hand off. |
| [BRD workflow](docs/brd-workflow.md) | The six-command BRD-to-PRD route as its own diagram, with its parameter table. |
| [Agents](docs/reference/agents.md) | The subagent inventory the commands dispatch internally. |
| [References](docs/reference/references.md) | The reference-doc inventory under `references/`. |
| [Environment](docs/reference/environment.md) | Every environment variable the plugin reads. |
| [Hooks](docs/reference/hooks.md) | The one bundled hook, what it injects, and why it never blocks Claude. |
| [Model routing](docs/reference/model-routing.md) | The task-complexity classification and model fallback chain. |
| [Session cost](docs/reference/session-cost.md) | Which commands emit a cost entry, what they charge to, and where it lands. |

## Recommended environment

Mount every repository, your docs clone and your specs repo under one `/workspace`, matching this plugin's defaults, with [`ihudak/ai-containers`](https://github.com/ihudak/ai-containers). Outside a container the commands still work — set `$REPOS_PATH`, `$DOCS_PATH` and `$SPECS_PATH` yourself.

## License

MIT — see [LICENSE](LICENSE).

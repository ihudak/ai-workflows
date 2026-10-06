# product-workflows documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| understand the whole pipeline first | [Workflow overview](workflow.md) |
| know what my role is responsible for | [Roles and phases](roles-and-phases.md) |
| see all six commands of the BRD-to-PRD route as one diagram, plus the edges it hands over on, with a parameter table | [BRD workflow](brd-workflow.md) |
| turn a customer BRD into a grounded inventory with every requirement allocated | [`/brd-intake`](commands/brd-intake.md), [`/prd-ground`](commands/prd-ground.md), [`/brd-split`](commands/brd-split.md) |
| ground an idea-route PRD's own requirements against code and design before architecting it | [`/prd-ground`](commands/prd-ground.md) |
| decide an allocated BRD's open questions without asking the wrong party | [`/brd-interview`](commands/brd-interview.md) |
| package a decided BRD for a customer whose reviewer has nothing installed | [`/brd-package`](commands/brd-package.md) |
| freeze a returned customer review into decisions and sweep what it overturned | [`/brd-reconcile`](commands/brd-reconcile.md) |
| turn a raw idea into something actionable | [`/idea`](commands/idea.md) |
| write or refresh a Product Requirements Document | [`/create-prd`](commands/create-prd.md), [`/update-prd`](commands/update-prd.md) |
| record an architecture decision | [`/create-ard`](commands/create-ard.md) |
| keep the team's architecture decisions where the next ARD finds them | [`/harvest-decisions`](commands/harvest-decisions.md) |
| break a PRD into Epics | [`/epics`](commands/epics.md) |
| write a specification | [`/specify`](commands/specify.md) |
| price a requirement set — work packages, hours by role, a range with its evidence | [`/prd-proposal`](commands/prd-proposal.md) |
| roll a BRD's priced slices into one programme proposal, with its coverage computed from the ledger | [`/brd-proposal`](commands/brd-proposal.md) |
| read an effort proposal, or know what one guarantees before sending it | [Effort proposals](reference/proposal-format.md) |
| understand what a run cost | [Session cost](reference/session-cost.md) |

Four pages orient you before you touch a command: [Getting started](getting-started.md) installs the plugin and sets your environment variables; [Workflow overview](workflow.md) shows the whole pipeline as one diagram; [BRD workflow](brd-workflow.md) shows the second route into a PRD — from a customer-supplied BRD to a grounded, allocated, decided inventory, back out through a customer review the plugin waits on, and on into the PRD pipeline through the BRD route — as its own diagram; [Roles and phases](roles-and-phases.md) says what each role owns and hands off. Every other page below documents one command, one shared subsystem, or — for [Agents](reference/agents.md) and [References](reference/references.md) — one whole inventory.

## Commands

- [`/prd-ground`](commands/prd-ground.md) — pin every mounted repository, ground a slice's `[BR#n]` requirements on the BRD route or a PRD's own `[AC#n]`/`[FR#n]` rows on the idea route (optional and ungated there), and independently re-derive every live finding on Opus.
- [`/brd-intake`](commands/brd-intake.md) — intake a customer BRD verbatim, with the files it links, extract its requirement inventory, and write a coverage ledger with every row unallocated.
- [`/brd-interview`](commands/brd-interview.md) — tag every open question `[G]`/`[V]`/`[C]` before it is asked, answer the `[G]`s from the findings, and record the delivery team's decisions.
- [`/brd-package`](commands/brd-package.md) — attack the decided package, then render a plugin-free customer prompt and a de-Obsidianised bundle for a reviewer with nothing installed.
- [`/brd-proposal`](commands/brd-proposal.md) — roll a BRD container's slice proposals into one programme umbrella: one row per included slice, the cross-slice effort that exists in no slice, and coverage computed from the root ledger.
- [`/brd-reconcile`](commands/brd-reconcile.md) — freeze the customer's returned answers as `[CD#n]` once an operator confirms each one, then sweep every dependent BRD and every stale cross-reference.
- [`/brd-split`](commands/brd-split.md) — on a root, propose and key slices from a mandatory slicing instruction; on a slice, walk every ledger row to a recorded fate.
- [`/create-ard`](commands/create-ard.md) — author an Architecture Requirements/Decision Document for a PRD, or for one Epic inside it, grounded on the mounted code.
- [`/create-prd`](commands/create-prd.md) — turn a refined idea plus a key into a reviewed Product Requirements Document.
- [`/epics`](commands/epics.md) — break a Product Requirements Document into reviewed child Epic drafts.
- [`/harvest-decisions`](commands/harvest-decisions.md) — harvest every merged ARD's decisions into the team architecture knowledge base `/create-ard`, `/specify` and `/dev-workflows:design` ground on.
- [`/idea`](commands/idea.md) — refine a raw prompt, file, community post, or existing PRD into a one-page idea brief.
- [`/prd-proposal`](commands/prd-proposal.md) — author an effort proposal for one PRD folder: work packages, hours by package and role, and a range whose width comes from per-package confidence, with every cost driver citing a record on disk.
- [`/specify`](commands/specify.md) — author an org-standard specification for one item through a relentless grill.
- [`/update-prd`](commands/update-prd.md) — refresh an existing Product Requirements Document.

## Reference

- [Agents](reference/agents.md) — the subagent inventory: what each helper agent does and which command calls it.
- [References](reference/references.md) — the reference-doc inventory under `references/`, grouped by concern.
- Skills — this plugin ships 0 bundled skills of its own. The `model-routing` skill every command here but `/harvest-decisions` loads at its classification step ships in `workflows-core`, alongside the classification reference it resolves.
- [Environment](reference/environment.md) — every environment variable the plugin reads, and what it configures.
- [Hooks](reference/hooks.md) — the bundled hook and what it does.
- [Model routing](reference/model-routing.md) — the task-complexity classification and model fallback chain commands apply before acting.
- [Effort proposals](reference/proposal-format.md) — the two customer-facing estimate documents: hours never money, the readiness tiers, the confidence bands, and what a cost driver may cite.
- [Session cost](reference/session-cost.md) — how a run's dollar cost is computed, attributed, and persisted.
- [Session feedback](reference/session-feedback.md) — two different signals about the plugin itself: this plugin's own automatic capture, and the companion plugin's `/workflows-core:feedback`, which logs what you tell it, and `/workflows-core:prompt*`, which captures a bad result, your correction, and the good result that came out of it.
- [Resume and checkpoints](reference/resume-and-checkpoints.md) — session hygiene: checkpointing state and resuming a long-running command.

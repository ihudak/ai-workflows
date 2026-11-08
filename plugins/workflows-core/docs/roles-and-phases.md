# Roles and phases

The workflow plugin family charges every cost-emitting run to a `phase` and a `role`. The phases are the stages of a product's lifecycle; each is listed here with the role it is charged to and the pipeline commands that charge it, and the sections below say how this plugin's own commands land on them:

- **`prd-creation`** (`pm`) — shaping an idea and writing its PRD: `/idea`, `/create-prd`, and a `/release-notes` run on a PRD with no specification or design yet.
- **`prd-update`** (`pm`) — revising an existing PRD: `/update-prd`.
- **`brd-to-prd`** (`pm`) — taking a customer's business requirements document to its PRDs: `/brd-intake`, `/brd-split`, `/brd-interview`, `/brd-package` and `/brd-reconcile`, and `/prd-ground`, which charges this phase on either route.
- **`proposal`** (`pm`) — an effort proposal over a set of requirements: `/prd-proposal` and `/brd-proposal`.
- **`architecture`** (`pa`) — the architecture record: `/create-ard`.
- **`specification`** (`pe`) — writing or revising a specification: `/specify` and `/update-spec`.
- **`epic-refinement`** (`pe`) — breaking a PRD into Epics, or refining one: `/epics`.
- **`planning`** (`dev`) — an engineering design: `/design`.
- **`readiness`** (`dev`) — the readiness check of a PRD or an Epic: `/ready`.
- **`implementation`** (`dev`) — writing the code: `/implement`.
- **`conformance`** — checking delivered work against its documents: `/conformance`, charged to `dev` on an Epic and to `pe` on a PRD, or on a BRD container it refuses.
- **`security-audit`** — a code repository's security scan and its findings register: `/security-workflows:scan`, charged to `dev` for a key run without `--triage` or `--verify-fixes` and to `sec` for every other run.
- **`documenting`** (`dev`) — writing documentation: `/document`, and a `/release-notes` run on a PRD that already has a specification or a design.
- **`docs-scaffold`** (`dev`) — setting up and branding a documentation repository: `/docs-init` and a standalone `/docs-brand` (a `/docs-brand` that `/docs-init` runs inline is charged to `/docs-init`).
- **`docs-audit`** (`dev`) — finding what documentation a product is missing: `/docs-audit`.

One more phase is this plugin's own rather than a lifecycle stage: **`plugin-feedback`**, with role `n/a`, for a run about the plugin itself ([below](#plugin-feedback)). This page says what `workflows-core`'s own seven commands do with these labels.

## No command here owns a phase

None of the seven commands in this plugin advances a product increment, so none of them mints a lifecycle phase of its own. Two mechanisms get them a label anyway:

- **Inheritance.** [`/feedback`](commands/feedback.md), [`/prompt`](commands/prompt.md), [`/prompt-brainstorm`](commands/prompt-brainstorm.md) and [`/prompt-grill-me`](commands/prompt-grill-me.md) resolve the **target command** whose output they are correcting or remarking on, and take that command's `phase`/`role` pair: its fixed pair from the list above, or, for a command whose pair is worked out at run time — `/release-notes`, [`/frames`](commands/frames.md) or `/conformance` — the pair that command's own run resolves to. A `/prompt` correcting a `/specify` output is priced as `specification`/`pe`; one correcting a `/design` output as `planning`/`dev`. The cost of fixing a phase's output belongs to that phase. **A `/security-workflows:scan` target is the exception**: its role is known only inside the scan run itself and reaches no command correcting it, so these four inherit its phase and record the role as `n/a` (*security-audit*, below).
- **Inference from the folder.** `/frames` reads the `kind` of the folder it resolved and charges accordingly — a frame set in a folder asserting `kind: brd`, a BRD container or a BRD-route slice, to `brd-to-prd`/`pm`, and one in a folder asserting `prd` or `epic` to `prd-creation`/`pm`, an Epic folder under a slice included. A run that stopped before it resolved such a folder is charged to `prd-creation`/`pm` too.

[`/statusline`](commands/statusline.md) emits nothing at all: it sets a configuration value rather than running a task. [`/diagnose-session`](commands/diagnose-session.md) is charged to `plugin-feedback` outright, below.

The four phases these commands can land on with a pair of their own, rather than one inherited whole, are described below: the two `/frames` reaches from a folder, the `plugin-feedback` fallback, and `security-audit`, whose phase a correction inherits without its role. Every other phase in the list above is reachable here only by inheritance, its pair taken whole. `product-workflows`, `dev-workflows`, `docs-workflows` and `security-workflows` each describe the ones their own commands emit on their own Roles and phases page.

### prd-creation

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: prd` or `kind: epic` — an idea-route PRD folder, or any Epic folder, one under a BRD-route slice included and by any of the four correction commands whose target command emits it. On either path, being in this phase means the spend is the PM's product-definition work on a PRD or one of its Epics — refining an idea, authoring the PRD, or indexing the frame sets that are the folder's own design record — and it says nothing about how far that folder has come: `/frames` lands here on a folder already holding a merged specification or design as readily as on one holding neither. A `/frames` run that stopped before it resolved a folder of a kind it indexes is charged here too, for want of a kind to charge it by; that spend is a refused run's, not product-definition work.

### brd-to-prd

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: brd` — a BRD container, or a BRD-route slice, though the slice is a `PRD-` folder — and by inheritance in the same way. On either path, being in this phase means the spend belongs to a customer-supplied BRD's route to its PRDs — its inventory being extracted, grounded, split, decided, packaged, or reconciled, or a frame set in one of its folders being indexed — and, as under *prd-creation*, nothing about how far the folder has come: a slice `/frames` indexes may already hold its PRD.

### security-audit

Role `n/a` here. Reached by any of the four correction commands whose target command is `/security-workflows:scan`: they inherit its phase and record no role, because the scan's own role, `dev` for a key run without `--triage` or `--verify-fixes` and `sec` for every other run, is known only inside the scan run, which passes it to its own cost entry, and it reaches no command correcting it. Being in this phase means the spend is a code repository's security audit — a scan, an import, a triage or a fix verification recorded in that repository's findings register — or the correction of one. `security-workflows`' own Roles and phases page describes the phase and the two roles the scan itself records.

### plugin-feedback

Role `n/a`. This is the fallback for `/feedback` and the three `/prompt*` commands, which reach it only after each first tries to inherit, and the fixed phase of `/diagnose-session`, which inherits nothing: a diagnosis is about the plugin itself, whichever command it reads. For the four, it applies where no target command resolves, where the target has no attribution row of its own, or where the target is itself one of them or `/diagnose-session`. Being in this phase means the run was about **the plugin itself** rather than the product, and no lifecycle phase owns it. `n/a` is the absence of a role recorded rather than guessed; aggregation should treat it as unattributed rather than folding it into `dev`.

---

**A second, unrelated `phase:` vocabulary exists in this family.** The model-routing resume phases — `full`, `verify-resume`, `regression-resume` — say how far a re-entered run must re-execute after a review or a failed test. They share nothing with the cost vocabulary but the field name. See [Session cost](reference/session-cost.md) for the mechanics of cost attribution itself.

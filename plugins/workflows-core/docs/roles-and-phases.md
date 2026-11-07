# Roles and phases

The `dev-workflows` plugin family charges every cost-emitting run to a `phase` and a `role`. The lifecycle phases, each with the role it is charged to, are:

- `prd-creation` (`pm`) — a PRD is being refined or authored, the design frame sets of a PRD or Epic folder are being indexed, or release notes are being drafted early, before any specification or design exists.
- `prd-update` (`pm`) — an existing PRD is being refreshed or re-done.
- `brd-to-prd` (`pm`) — a customer-supplied BRD is on its route to PRDs: extracted, grounded, split, decided, packaged or reconciled.
- `proposal` (`pm`) — a requirement set is being priced into an effort proposal.
- `architecture` (`pa`) — architecture decisions are being recorded for a PRD or one of its Epics.
- `specification` (`pe`) — a specification is being authored, or a merged one revised.
- `epic-refinement` (`pe`) — a PRD is being broken down into Epic drafts.
- `planning` (`dev`) — an engineering design is being authored from a merged specification.
- `implementation` (`dev`) — code is being written, tested and reviewed.
- `readiness` (`dev`) — the workflow phase is being derived from the ARD, specification and design record.
- `conformance` (`dev` for an Epic run, `pe` for a PRD run) — what was built is being checked against what was specified.
- `documenting` (`dev`) — a product's documentation is being written or updated, or release notes are being drafted once engineering work exists.
- `docs-scaffold` (`dev`) — a documentation repository is being scaffolded or branded.
- `docs-audit` (`dev`) — a documentation repository is being audited.
- `security-audit` (`dev` or `sec`) — a code repository's security findings are being scanned, imported, triaged or verified.

<!-- re-derive: the phase column of the table in references/cost-emission.md section 7, plus its inference paragraphs, which alone name the phases a command reaches only by inference (conformance, security-audit) -->

Beside these this plugin has its own `plugin-feedback` phase: the feedback commands reach it only when there is nothing to inherit, and `/diagnose-session` always lands there. The lifecycle vocabulary belongs to the pipeline plugins whose commands own the lifecycle. This page says only what `workflows-core`'s own seven commands do with it, because that is the part a reader of *these* commands needs.

## No command here owns a phase

None of the seven commands in this plugin advances a product increment, so none of them mints a lifecycle phase of its own. Two mechanisms get them a label anyway:

- **Inheritance.** `/feedback`, `/prompt`, `/prompt-brainstorm` and `/prompt-grill-me` resolve the **target command** whose output they are correcting or remarking on, and take that command's `phase`/`role` pair: the fixed pair it always emits, or, for a command whose pair depends on the run — `/release-notes`, `/frames` and `/conformance` — the pair that run resolves to. A `/prompt` correcting a `/specify` output is priced as `specification`/`pe`; one correcting a `/design` output as `planning`/`dev`. The cost of fixing a phase's output belongs to that phase. **A `/security-workflows:scan` target is the exception**: its role is the one the scan run itself ran under, which reaches no command correcting it, so these four inherit its phase and record the role as `n/a` (*security-audit*, below).
- **Inference from the folder.** `/frames` reads the `kind` of the folder it resolved and charges accordingly — a frame set in a folder asserting `kind: brd`, a BRD container or a BRD-route slice, to `brd-to-prd`/`pm`, and one in a folder asserting `prd` or `epic` to `prd-creation`/`pm`, an Epic folder under a slice included.

`/statusline` emits nothing at all: it sets a configuration value rather than running a task. `/diagnose-session` is charged to `plugin-feedback` outright, below.

The four phases these commands can land on with a pair of their own, rather than one inherited whole, are described below: the two `/frames` reaches from a folder, the `plugin-feedback` fallback, and `security-audit`, whose phase a correction inherits without its role. Every other lifecycle phase is reachable here only by inheritance, its pair taken whole. `product-workflows`, `dev-workflows` and `security-workflows` each describe the ones their own commands emit on their roles-and-phases pages; `docs-workflows` has no such page, so its phases — `documenting`, `docs-scaffold` and `docs-audit` — are the ones in the list at the top of this page, and that plugin's own Session cost reference page says which of its commands emits each.

### prd-creation

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: prd` or `kind: epic` — an idea-route PRD folder, or any Epic folder, one under a BRD-route slice included — and by any of the four correction commands whose target command emits it. On either path, being in this phase means the spend is the PM's product-definition work on a PRD or one of its Epics — refining an idea, authoring the PRD, or indexing the frame sets that are the folder's own design record — and it says nothing about how far that folder has come: `/frames` lands here on a folder already holding a merged specification or design as readily as on one holding neither.

### brd-to-prd

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: brd` — a BRD container, or a BRD-route slice, though the slice is a `PRD-` folder — and by inheritance in the same way. On either path, being in this phase means the spend belongs to a customer-supplied BRD's route to its PRDs — its inventory being extracted, grounded, split, decided, packaged, or reconciled, or a frame set in one of its folders being indexed — and, as under *prd-creation*, nothing about how far the folder has come: a slice `/frames` indexes may already hold its PRD.

### security-audit

Role `n/a` here. Reached by any of the four correction commands whose target command is `/security-workflows:scan`: they inherit its phase and record no role, because the scan's own role, `dev` for a key run without `--triage` or `--verify-fixes` and `sec` for every other run, belongs to the scan run itself, which records it on its own cost entry, and reaches no command correcting it. Being in this phase means the spend is a code repository's security audit — a scan, an import, a triage or a fix verification recorded in that repository's findings register — or the correction of one. `security-workflows`' own Roles and phases page describes the phase and the two roles the scan itself records.

### plugin-feedback

Role `n/a`. This is the fallback for `/feedback` and the three `/prompt*` commands, which reach it only after each first tries to inherit, and the fixed phase of `/diagnose-session`, which inherits nothing: a diagnosis is about the plugin itself, whichever command it reads. For the four, it applies where no target command resolves, where the target has no attribution row of its own, or where the target is itself one of them or `/diagnose-session`. Being in this phase means the run was about **the plugin itself** rather than the product, and no lifecycle phase owns it. `n/a` is the absence of a role recorded rather than guessed; aggregation should treat it as unattributed rather than folding it into `dev`.

---

**A second, unrelated `phase:` vocabulary exists in this family.** The model-routing resume phases — `full`, `verify-resume`, `regression-resume` — say how far a re-entered run must re-execute after a review or a failed test. They share nothing with the cost vocabulary but the field name. See [Session cost](reference/session-cost.md) for the mechanics of cost attribution itself.

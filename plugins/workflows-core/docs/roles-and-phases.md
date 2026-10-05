# Roles and phases

The `dev-workflows` plugin family charges every cost-emitting run to a `phase` and a `role`. The phases are the **lifecycle** phases carried as fixed pairs in `references/cost-emission.md` §7 — read them off its table; this page keeps no count of them, because a count here went stale each time a plugin added a phase — plus this plugin's own `plugin-feedback` phase, which §7 has no fixed row for: the feedback commands reach it only when there is nothing to inherit, and `/diagnose-session` through a target it always passes as `n/a`. The lifecycle vocabulary belongs to the pipeline plugins whose commands own the lifecycle. A sibling page that counts lifecycle phases counts them without the fallback, which is not a disagreement: each treats the fallback apart from the lifecycle phases it lists. This page says only what `workflows-core`'s own seven commands do with it, because that is the part a reader of *these* commands needs.

## No command here owns a phase

None of the seven commands in this plugin advances a product increment, so none of them mints a lifecycle phase of its own. Two mechanisms get them a label anyway:

- **Inheritance.** `/feedback`, `/prompt`, `/prompt-brainstorm` and `/prompt-grill-me` resolve the **target command** whose output they are correcting or remarking on, and take that command's own fixed `phase`/`role` pair. A `/prompt` correcting a `/specify` output is priced as `specification`/`pe`; one correcting a `/design` output as `planning`/`dev`. The cost of fixing a phase's output belongs to that phase.
- **Inference from the folder.** `/frames` reads the `kind` of the folder it resolved and charges accordingly — a frame set in a folder asserting `kind: brd`, a BRD container or a BRD-route slice, to `brd-to-prd`/`pm`, and one in a folder asserting `prd` or `epic` to `prd-creation`/`pm`, an Epic folder under a slice included.

`/statusline` emits nothing at all: it sets a configuration value rather than running a task. `/diagnose-session` is charged to `plugin-feedback` outright, below.

The three phases those two mechanisms can land on directly are described below. Every other phase in §7 is reachable here only by inheritance. `product-workflows` and `dev-workflows` each describe the ones their own commands emit on their roles-and-phases pages; `docs-workflows` has no such page, so its phases — `documenting`, `docs-scaffold` and `docs-audit` — are defined by §7's rows, and that plugin's own session-cost reference page (`docs/reference/session-cost.md` in `docs-workflows`) says which of its commands emits each.

### prd-creation

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: prd` or `kind: epic` — an idea-route PRD folder, or any Epic folder, one under a BRD-route slice included — and by any of the four correction commands whose target command emits it. On either path, being in this phase means the spend is the PM's product-definition work on a PRD or one of its Epics — refining an idea, authoring the PRD, or indexing the frame sets that are the folder's own design record — and it says nothing about how far that folder has come: `/frames` lands here on a folder already holding a merged specification or design as readily as on one holding neither.

### brd-to-prd

Role `pm`. Reached by `/frames` when the folder it resolved asserts `kind: brd` — a BRD container, or a BRD-route slice, though the slice is a `PRD-` folder — and by inheritance in the same way. On either path, being in this phase means the spend belongs to a customer-supplied BRD's route to its PRDs — its inventory being extracted, grounded, split, decided, packaged, or reconciled, or a frame set in one of its folders being indexed — and, as under *prd-creation*, nothing about how far the folder has come: a slice `/frames` indexes may already hold its PRD.

### plugin-feedback

Role `n/a`. This is the fallback for `/feedback` and the three `/prompt*` commands, which reach it only after each first tries to inherit, and the fixed phase of `/diagnose-session`, which inherits nothing: a diagnosis is about the plugin itself, whichever command it reads. For the four, it applies where no target command resolves, where the target has no attribution row of its own, or where the target is itself one of them or `/diagnose-session`. Being in this phase means the run was about **the plugin itself** rather than the product, and no lifecycle phase owns it. `n/a` is the absence of a role recorded rather than guessed; aggregation should treat it as unattributed rather than folding it into `dev`.

---

**A second, unrelated `phase:` vocabulary exists in this family.** The model-routing resume phases — `full`, `verify-resume`, `regression-resume` — say how far a re-entered run must re-execute after a review or a failed test. They share nothing with the cost vocabulary but the field name. See [Session cost](reference/session-cost.md) for the mechanics of cost attribution itself.

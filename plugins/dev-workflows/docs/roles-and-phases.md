# Roles and phases

[Workflow overview](workflow.md) shows where each command sits in the pipeline. This page says what each role is accountable for, and — in its second half — what each cost-attribution phase means when you see it on a cost report or a run's output.

## The handover model

Every phase ends the same way: a producing command lands its deliverable on the specs repo's default branch — not merely written to disk, and not merely committed to a branch of its own. What the next command in the chain does when that hasn't happened yet depends on which state it finds, and two states show up often enough that you will actually hit them.

- **The artifact exists but sits on an unmerged branch** — a pull request open, or one that never got opened. The next command stops cold and names the branch (and the open PR, if there is one) rather than guessing at content that might still change underneath it.
- **The artifact does not exist on any branch at all.** The next command treats it as absent and falls back to whatever it already did before this artifact existed — an absent optional input is never promoted into a new prerequisite. `/design`'s `specification.md` is this plugin's one exception: it is not optional, and its absence is a hard stop. (The companion `product-workflows` has several of its own — each command whose gated input was never optional, which `workflows-core:phase-handoff` §3.4 lists.)

`/ready` is the one caller whose own gate lets it keep going past a stop like this (`/product-workflows:brd-reconcile` also reads a stopping row without stopping, at two sites and never at its ordinary Phase 0 gate — its cross-BRD write guard, and the redundancy check a `--sent` run makes at Phase 0 step 6, which reads the gate inverted; `workflows-core:phase-handoff` §3.7): because its whole job is to report on readiness, an artifact it can't verify becomes a finding that caps its verdict at `PARTIAL` rather than a reason to halt.

## Where PM/PA/PE hand off

- **Owns, upstream of this plugin:** turning a raw prompt, community post, RFE, or existing PRD into a refined idea, then a Product Requirements Document, an optional Architecture Requirements/Decision Document, Epic breakdown, and an org-standard specification — plus a six-command BRD-to-PRD route that feeds the same ladder from a customer-supplied BRD instead of a PM-authored idea. All of it ships in the companion `product-workflows` plugin now: `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/epics`, `/specify`, and `/brd-intake`, `/prd-ground`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`. PM, PA, and PE are documented in full — what each owns, consumes, produces, and hands over at every seam of its own — on `product-workflows`'s own Roles and phases page.
- **Hands over at the seam:** `/product-workflows:specify` lands `specification.md` on the specs repo's default branch, and `/design` refuses to start until it finds that specification there — this plugin's one hard exception to the optional-input rule above. `/design`, `/implement`, and `/ready` also each consult the applicable ARD once `/product-workflows:create-ard` has landed one there.
- **Cost phase(s) upstream of this plugin:** `prd-creation`, `prd-update`, `brd-to-prd`, `architecture`, `specification`, `epic-refinement`, and `proposal` — roles `pm`/`pa`/`pe` — all documented on `product-workflows`'s own Roles and phases page, not restated here.

## Dev — build, verify, and deliver

- **Owns:** the engineering design, the implementation, and the documentation of the shipped feature — plus deriving the workflow phase from the artifacts on record — and, with `--claimed`, checking a status you declare against it — which this role checks but never sets.
- **Runs:** `/design`, `/implement`, `/ready`; also the companion plugin's `/docs-workflows:document`, the final run of `/docs-workflows:release-notes` once a specification or design already exists, and — outside the pipeline spine, whenever a documentation repository has to be created or re-branded — `/docs-workflows:docs-init` and `/docs-workflows:docs-brand`, and, to find what a portal is missing, `/docs-workflows:docs-audit`.
- **Consumes:** the merged `specification.md` (plus the ARD, when one exists), then the merged `design.md`, then the code under `$REPOS_PATH`; `/ready` additionally consumes the artifacts present for the PRD or Epic in question.
- **Produces:** `design.md`, landed on the specs repo's default branch; code committed on a feature branch in `$REPOS_PATH`, then pushed where you said so, the repository has an `origin` and the push itself succeeded — and opened as a pull request where you asked for one and the run could open it at all, the run's own `Code repo:` outcome line being what says which of those happened; product documentation in the external docs repo; the final release-notes draft; and, from `/ready`, a `SUPPORTED` / `PARTIAL` / `NOT-SUPPORTED` verdict plus an optional `_readiness.md` snapshot, committed and handed off only behind your consent.
- **Hands over at the seam:** `/design` is this plugin's one hard exception to the optional-input rule above — it stops outright if `specification.md` is not found on the specs repo's default branch. It then lands `design.md` the same way. `/implement` gates its own in-scope `specification.md` / `design.md` the same way the companion plugin's `/product-workflows:create-ard` and `/product-workflows:specify` gate the PRD — an unmerged one is a hard stop, but an absent one is not: the run behaves exactly as it did before this gate existed (on a multi-component PRD, `/implement` Phase 1 asks about a missing Epic specification or design, offering to continue), and a direct-prompt run (which resolves no in-scope spec/design at all) is unaffected either way. `/ready` is the opposite extreme, and the exception named [above](#the-handover-model): it is the one caller whose own gate never stops it, turning an unmerged or missing artifact into a finding that caps its verdict at `PARTIAL` instead of halting. (`/product-workflows:brd-reconcile` also reads a stopping row without stopping, but at two sites and never at its ordinary Phase 0 gate: its cross-BRD write guard, and a `--sent` run's redundancy check at Phase 0 step 6 — `workflows-core:phase-handoff` §3.7.)
- **Cost phase(s):** `planning` (`/design`), `implementation` (`/implement`), `readiness` (`/ready`), `documenting` (`/docs-workflows:document`, in the companion plugin), `docs-scaffold` (`/docs-workflows:docs-init` and a standalone `/docs-workflows:docs-brand`, in the same plugin), and `docs-audit` (`/docs-workflows:docs-audit`, in the same plugin) — all role `dev`.

**Why there is no separate verification role.** `/ready` derives a phase from the artifacts and reports on it. Its `_readiness.md` is a record rather than a handoff — the one command that reads it, `/implement` at Phase 0.5, only softens a non-blocking recommendation — and it is normally run by the same person who just wrote the design or is about to start the implementation. Giving it a lane of its own would suggest a handover that does not happen — so it sits in `dev`, the role that already owns everything it verifies.

## Cost-attribution phases

Every cost-emitting command tags its cost line with a `phase` and a `role`. Three phases are reached by this plugin's three cost-emitting commands; each entry below names the command that emits it and what being in that phase means. Seven more lifecycle phases exist for the companion `product-workflows` plugin's own commands, and three more for the companion `docs-workflows` plugin's — `documenting`, from `/docs-workflows:document`, `docs-scaffold`, from `/docs-workflows:docs-init` and a standalone `/docs-workflows:docs-brand`, and `docs-audit`, from `/docs-workflows:docs-audit` — not restated here: the product phases are documented on `product-workflows`'s own Roles and phases page, the documentation ones on `docs-workflows`' session-cost page, and `workflows-core:cost-emission` §7 is the authority for every pair. Each of the three below can also be reached **by inheritance**: the companion `workflows-core` plugin's `/workflows-core:prompt`, `/workflows-core:feedback`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me` adopt the phase and role of whatever they are correcting, so a correction to a `/design` output is a second entry in `planning`.

### planning

Emitted by `/design`, role `dev`. Being in this phase means an engineering `design.md` is being authored from a merged specification, grounded strictly in the mounted code.

### implementation

Emitted by `/implement`, role `dev`. Being in this phase means code is actually being written, tested, and reviewed.

### readiness

Emitted by `/ready`, role `dev`. Being in this phase means the workflow phase is being derived from the ARD / spec / design record, never changed.

### plugin-feedback

The fallback phase (`plugin-feedback`, role `n/a`) for a `/workflows-core:prompt`/`/workflows-core:feedback`/`/workflows-core:prompt-brainstorm`/`/workflows-core:prompt-grill-me` run with no target command to inherit from, and the phase every `/workflows-core:diagnose-session` run is charged to — documented in full on the companion `workflows-core` plugin's own Roles and phases page, since none of this plugin's three cost-emitting commands emits it directly.

---

**A second, unrelated `phase:` vocabulary exists in this plugin.** The model-routing resume phases — `full`, `verify-resume`, `regression-resume` — are what `/vuln` and `/upgrade` pass to their fixer/executor agents to say how far a re-entered run should re-execute after a review or a failed test. Neither `/vuln` nor `/upgrade` emits a cost-attribution phase at all; they sit outside the phases above entirely. The two vocabularies share a field name, `phase`, and nothing else — one names where a run sits in the product lifecycle, the other names how much of a single command's own work must be redone.

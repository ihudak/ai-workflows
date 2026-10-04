# Workflow states (embedded — shared reference)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Maps each **workflow phase** on the PRD and Epic ladders to (a) its owning role,
(b) the pipeline command that drives the transition into it, and (c) the **expected artifacts**
that should exist at that status. This is the rubric `readiness-reviewer` applies and the
source for the readiness verdict; it also feeds the PM/PA/PE/Dev workflow graph.

**Nothing outside this tree declares a status, so the artifacts are the source of truth.** The ladder
below is read in the direction its *expected artifacts* column already supports: a phase is what the
artifacts present imply, and `/ready` reports that. This reference still NEVER stores status — it
interprets what is on disk.

**An operator who keeps a tracker can still have the divergence check** the old reading gave them, by
passing what it says to `/ready --claimed "<status>"`. What is genuinely lost without that flag is
the ability to catch a *wrong* declaration: a derived phase cannot contradict itself. That is the
stated cost of removing the mirror, not an oversight.

## PRD status ladder

`Open → Problem stated → Usecases defined → Ready for Implementation → Implementation → Release Preparation → Post GA`

| Status | Role | Transition command | Expected artifacts |
|---|---|---|---|
| Open | PM | — | PRD stub |
| Problem stated | PM | /idea, /create-prd | PRD with Problem/Goal |
| Usecases defined | PM | /create-prd | PRD with user stories / use cases |
| Ready for Implementation | PE→Dev | /epics, /specify, /design | Epics defined, or a broad PRD-level slice — the PRD folder holding a flat specification.md — or both; each in-scope Epic, and the slice where one stands, Refined+ with specification.md AND design.md; coverage complete; ARD (if any) respected; no cross-artifact contradictions. **On a multi-component PRD** (below): the ARD with `## Contracts`, the PRD-level specification.md, Epics defined, and each in-scope Epic Refined+ with specification.md AND design.md — no PRD-level design.md |
| Implementation | Dev | /implement | code in progress (past the readiness gate) |
| Release Preparation | Dev/PM | /document, /release-notes | docs + release notes |
| Post GA | PM | — | shipped |

**A multi-component PRD** (`workflows-core:components` §3 — its known set has two or more components) reads the *Ready for Implementation* row's second clause. There the flat `specification.md` is a **requirements source**: its end-to-end acceptance criteria are split across one-component Epics, each designed and implemented on its own, so the slice is never a unit of design or implementation and no PRD-level `design.md` is expected. The ARD's `## Contracts` is what makes those Epics fit together, which is why it is expected there rather than optional. A single-component PRD reads the first clause, unchanged.

## Epic status ladder

`Open → In Preparation → Refined → In Progress → In Review → Closed`

| Status | Role | Transition command | Expected artifacts |
|---|---|---|---|
| Open | PE | /epics | Epic draft |
| In Preparation | PE | /specify | specification.md being authored |
| Refined | PE→Dev | /specify, /design | specification.md AND design.md present; coverage complete; ARD (if any) respected — **the Epic-level readiness gate** |
| In Progress | Dev | /implement | code in progress (past the gate) |
| In Review | Dev | /implement | PRs in review (past the gate) |
| Closed | Dev | — | merged/done |

**The broad PRD-level slice is read on this ladder too, and its `Open` rung is one it can never
occupy.** The PRD row above calls the slice *the PRD folder holding a flat `specification.md`*, and
`/ready` derives its phase on this ladder exactly as it derives an Epic's — but `Open`'s expected
artifact is an *Epic draft*, an `epic.md`, and the slice is a PRD folder rather than an `EPIC-`
folder: `/epics` is the only command that creates an `epic.md` and it creates one only into an
`EPIC-` folder (D6). So the slice's ladder is read from **In Preparation**, and the permanently absent
`epic.md` is not an artifact it straddles — a slice carrying `specification.md` and `design.md` is
*Refined*, not the lower rung the straddle rule would otherwise name. Nothing else about the ladder
changes for it, and an Epic, which can hold an `epic.md`, is read from `Open` as before.

> **Refine — two ways in, one mode.** `/epics` re-refines an Epic that already exists rather than
> partitioning the PRD again, and it reaches that mode from either end. **Named:** address the
> `EPIC-` folder itself (`/epics <EPIC-KEY>`) and the run re-grounds and sharpens that one Epic's
> `epic.md` in place. **Detected:** run `/epics <PRD>` where Epics under that PRD carry
> `refinement_candidate: true` — near-empty drafts left as placeholders — and the run offers
> to fill them in and partition the PRD's scope across them, instead of drafting net-new; the offer
> is confirmable, and declining it gives the ordinary net-new run. Either way it is the same
> `Open → Epic draft` transition and the same `EPIC-<PRD-KEY>-NN-<eslug>/epic.md` shape: refine
> iterates on a draft this command wrote, since **`/epics` is the only command that creates an
> `EPIC-` folder** (D6) and every one of them sits under a PRD folder. There is no `<EPIC-KEY>.md`
> file at either end — the folder carries the key, the filename carries the kind.

## Readiness targets (for `/ready`)

- **PRD** — "ready for AI-driven development" = the artifacts support the transition into **Ready for Implementation**.
- **Epic** — = the artifacts support the transition into **Refined** (spec **and** design present). **In Progress / In Review / Closed** are *past* the gate — `/ready` reports the gate is moot.

The rubric is advisory: an org may skip an optional artifact (e.g. no ARD) — that downgrades to a MINOR finding, never a hard block on its own. **Except on a multi-component PRD**, where the ARD with `## Contracts` and the PRD-level specification are expected artifacts of *Ready for Implementation* (above): their absence leaves the PRD below that rung, as any other missing expected artifact does.

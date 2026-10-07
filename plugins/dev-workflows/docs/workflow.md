# Workflow overview

This is the `dev-workflows` pipeline top to bottom — every command shown here, in the order the roles typically hand work to each other. This plugin's spine picks up from `specification.md`, which the companion `product-workflows` plugin's PRD → architecture → Epic breakdown → specification ladder (and its six-command BRD-to-PRD route) lands on the specs repo's default branch: `/design → /implement` carries it the rest of the way to shipped code, `/ready` verifies the artifacts alongside that spine, and the companion `docs-workflows` plugin closes the PRD out with `/docs-workflows:document` and `/docs-workflows:release-notes`.

```mermaid
flowchart TD
    subgraph PMPRD["PM/PA/PE — product-workflows (upstream)"]
        specify["/product-workflows:specify"]:::prod
        createard["/product-workflows:create-ard"]:::prod
        harvest["/product-workflows:harvest-decisions"]:::prod
    end
    subgraph DEV["Dev — build, verify & deliver"]
        design["/design"]:::dev -->|design.md| implement["/implement"]:::dev
        ready["/ready"]:::dev
    end
    subgraph ANY["Anytime — standalone maintenance & utilities"]
        maint["/vuln · /dev-workflows:upgrade"]:::dev
    end

    specify -->|specification.md| design
    createard -.->|ard.md| design
    harvest -.->|team decisions| design
    design -.->|design.md + specification.md| ready
    ready -.->|_readiness.md — advisory| implement
    implement -.->|code + implementation.md, in docs-workflows| docsplugin["/docs-workflows:document · /docs-workflows:release-notes"]:::docs

    classDef prod fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    classDef dev fill:#dcfce7,stroke:#15803d,color:#14532d
    classDef docs fill:#fef3c7,stroke:#b45309,color:#78350f
```

The diagram draws `specification.md` and the ARD reaching `/design`, and `/ready` reading what `/design` leaves, but `/implement` and `/ready` also resolve the applicable ARD and the in-scope `specification.md`/`design.md` once they exist — each edge is drawn once to keep the diagram readable, not because the others do not consult those artifacts. `/ready`'s verdict, `_readiness.md`, is advice `/implement` reads; it blocks nothing.

Three nodes in this diagram are not this plugin's commands and are drawn for continuity only: `/product-workflows:specify`, where this plugin's spine picks up, `/product-workflows:create-ard`, whose ARD `/design` respects, and `/product-workflows:harvest-decisions`, whose team decision records `/design` grounds on. All three ship in the companion `product-workflows` plugin, alongside `/idea`, `/create-prd`, `/update-prd`, `/epics`, and the six-command BRD-to-PRD route that feeds it — that plugin's own Workflow overview page carries the full upstream diagram. The combined `/docs-workflows:document · /docs-workflows:release-notes` handoff hanging off `/implement` ships in the companion `docs-workflows` plugin and is documented there.

The diagram above shows where each command sits in the pipeline; [Roles and phases](roles-and-phases.md) says what each role is accountable for and what it hands over at each seam.

**One command name in this plugin collides with a Claude Code built-in of the same name: `/upgrade`.** Typing the bare form reaches Claude Code's own command instead of the plugin's, so use the qualified `/dev-workflows:upgrade`. **`/design` collides on some accounts:** Claude Code's own `/design`, which makes a Design artifact, is switched on for some accounts only, and where it is on the bare form can reach it, so type `/dev-workflows:design` there. `/release-notes`, drawn here for context, collides the same way as `/upgrade` and is qualified `/docs-workflows:release-notes`; `/statusline` and `/feedback` collide too and are qualified `/workflows-core:statusline` and `/workflows-core:feedback`. Each ships in a companion plugin. No other command in this plugin is known to collide today, so the rest work either way, and among this plugin's own commands the diagram above spells out the qualified form only where a collision is certain.

## Roles

| Role | Runs | Produces → lands at |
|---|---|---|
| **Dev** | `/design`, `/implement`, `/ready` (then `/docs-workflows:document` and a final `/docs-workflows:release-notes`); off the spine, `docs-workflows`' `/docs-init`, `/docs-brand` and `/docs-audit` | `design.md` on the specs repo's default branch; code committed on a branch in `$REPOS_PATH`, the push and the pull request behind a consent choice; a read-only readiness verdict that sets no status |
| **Anytime** | `/vuln`, `/upgrade` | a fixed CVE or a completed upgrade, committed on a feature branch in `$REPOS_PATH` |

The PM, PA, and PE roles that produce this plugin's own input — `specification.md` — ship in the companion `product-workflows` plugin; see [Roles and phases](roles-and-phases.md) for where this plugin's spine picks up and that plugin's own Roles and phases page for what each of those three roles owns.

## Artifact homes

- **`$SPECS_PATH/specifications/PRD-<KEY>-<slug>/`** — the shared, team-visible home for `specification.md` and `design.md`, in the `EPIC-` folders below the PRD folder (a BRD route puts the same PRD folder one level down, inside `BRD-<KEY>-<slug>/`, per the companion `product-workflows` plugin's own conventions). `/design` lands its file here, then hands it onto the specs repo's default branch for `/implement` to find.
- **`$REPOS_PATH`** — the mounted code clones. `/implement`, `/upgrade`, and `/vuln` each work here on a feature branch and each finish it the same way ([`code-handoff.md`](reference/references.md)): the work is committed without asking — unless its secret scan finds a possible secret, which is put to you first — and pushing it and opening a pull request sit behind a consent choice asked once and then reused — put again only where a later unit's outcome differs from the one you answered under, in either direction. `/vuln` does that once per fixed CVE, `/upgrade` commits once per component and pushes once for the batch.
- **Plugin bookkeeping** — feedback and session-cost files — lives under `<PRD-dir>/dev-workflows/` inside `$SPECS_PATH` on a run that resolved a PRD folder (a keyless run writes them at the specs root instead, under `dev-workflows-feedback/` and `dev-workflows-cost/`), committed and pushed alongside the specs artifacts it describes. Two records land outside that subfolder, beside the artifacts they are about: follow-up tasks, in the folder the run resolved (`/implement`'s in the folder of the unit it implemented) — see [Follow-ups](reference/follow-ups.md) for the full ladder — and `/implement`'s `implementation.md`, in the folder of the unit implemented.

## Sources of truth

- **The artifacts** are the source of truth for workflow *status* — [`workflow-states.md`](../references/workflow-states.md) is read in the direction its *expected artifacts* column supports, and `/ready` derives the phase from what is on disk. An operator who keeps a tracker can still check a declared status against it with `/ready --claimed "<status>"`.
- **The specs repo's default branch** is the source of truth for whether a phase's deliverable is actually *done*. A producing command lands its artifact there; the next command in the chain stops while the artifact sits on an unmerged branch the commands cut, and treats one no such branch carries — written only to disk, or committed only to a branch of your own — as absent, falling back from it or, for a few, stopping. See [Roles and phases](roles-and-phases.md) for what happens when the artifact is on an unmerged branch instead, or missing entirely.

## Cross-cutting commands

These ship in companion plugins and run against the same specs tree, outside this plugin's own role pipeline:

- **In `workflows-core`.** The specs-tree frame-set indexer, the plugin-feedback commands and the session diagnosis: `/workflows-core:frames`, `/workflows-core:feedback`, `/workflows-core:prompt`, `/workflows-core:prompt-brainstorm`, `/workflows-core:prompt-grill-me` and `/workflows-core:diagnose-session`, whose only write there is its cost entry. `/workflows-core:statusline` ships there too and is the one that does not meet the criterion above — it configures your terminal status line and touches the specs tree not at all.
- **In `docs-workflows`.** The documentation half this plugin's Dev role hands off to, plus the cold-start scaffold that creates the repository it writes into and the audit that finds what that repository is missing: `/docs-workflows:document`, `/docs-workflows:release-notes`, `/docs-workflows:docs-init`, a standalone `/docs-workflows:docs-brand`, and `/docs-workflows:docs-audit` — the five that emit their own session bookkeeping here. The plugin's other two, `/docs-workflows:docs-profile` and `/docs-workflows:docs-serve`, work only inside a documentation repository: neither runs a specs preflight or a terminal commit, so neither writes anything into the specs tree.
- **In `product-workflows`.** The PRD → architecture → Epic breakdown → specification ladder this plugin's spine picks up from, and the six-command BRD-to-PRD route that feeds it — `/product-workflows:idea`, `/product-workflows:create-prd`, `/product-workflows:update-prd`, `/product-workflows:create-ard`, `/product-workflows:epics`, `/product-workflows:specify`, the route's own `/product-workflows:brd-intake`, `/product-workflows:brd-split`, `/product-workflows:prd-ground`, `/product-workflows:brd-interview`, `/product-workflows:brd-package` and `/product-workflows:brd-reconcile`, and its two effort-proposal commands `/product-workflows:prd-proposal` and `/product-workflows:brd-proposal`, which price a requirement set in hours and gate nothing on this ladder.

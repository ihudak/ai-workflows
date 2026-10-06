# Family map

This page shows the whole plugin family on one diagram: every slash command of `product-workflows`, `dev-workflows`, `docs-workflows` and `workflows-core`, from the two ways work enters — `/idea` and `/brd-intake` — to shipped code, its documentation and its release notes. Each lane is a **role**. Each command is **coloured by the plugin that ships it**. Labels name artifacts or explicitly marked actions; gray manual steps are not commands.

```mermaid
flowchart TD
    subgraph KEY["Legend"]
        kprod["product-workflows"]:::prod
        kdev["dev-workflows"]:::dev
        kdocs["docs-workflows"]:::docs
        kcore["workflows-core"]:::core
        kmanual["Manual work — no command"]:::manual
    end

    subgraph BRDR["PM — BRD route (entry for a customer's requirements document)"]
        brdintake["/brd-intake"]:::prod
        splitroot["/brd-split (root)"]:::prod
        splitslice["/brd-split (slice)"]:::prod
        brdinterview["/brd-interview"]:::prod
        brdpackage["/brd-package"]:::prod
        brdreconcile["/brd-reconcile"]:::prod
    end
    subgraph CUST["Customer — off-platform, nothing installed"]
        review["reviews the bundle"]:::cust
    end
    subgraph PMR["PM — idea route and the PRD"]
        idea["/idea"]:::prod
        createprd["/create-prd"]:::prod
        updateprd["/update-prd"]:::prod
        rnearly["/docs-workflows:release-notes (PRD draft / refresh)"]:::docs
    end
    subgraph EST["PM — effort proposals (gate nothing)"]
        prdproposal["/prd-proposal"]:::prod
        brdproposal["/brd-proposal"]:::prod
    end
    subgraph PA["PA — grounding and architecture"]
        groundbrd["/prd-ground (BRD slice)"]:::prod
        groundprd["/prd-ground (idea PRD)"]:::prod
        createard["/create-ard"]:::prod
    end
    subgraph PE["PE — breakdown and specification"]
        epics["/epics"]:::prod
        specify["/specify"]:::prod
    end
    subgraph DEV["Dev — build and verify"]
        design["/dev-workflows:design"]:::dev
        ready["/ready"]:::dev
        implement["/implement"]:::dev
    end
    subgraph DOC["Dev — documentation and release notes"]
        document["/document (keyed)"]:::docs
        rnfinal["/docs-workflows:release-notes (final)"]:::docs
    end
    subgraph PORTAL["Dev — documentation portal, off the spine"]
        docsinit["/docs-init"]:::docs
        docsbrand["/docs-brand"]:::docs
        docsprofile["/docs-profile"]:::docs
        docsserve["/docs-serve"]:::docs
        docsaudit["/docs-audit"]:::docs
        manualdocs["Manual: select unit, write, verify and publish"]:::manual
        documentdirect["/document (direct — optional prose help)"]:::docs
    end
    subgraph ANY["Anytime"]
        frames["/frames"]:::core
        improve["/workflows-core:feedback · /prompt · /prompt-brainstorm · /prompt-grill-me"]:::core
        diagnose["/diagnose-session"]:::core
        statusline["/workflows-core:statusline"]:::core
        maint["/vuln · /dev-workflows:upgrade"]:::dev
    end

    brdintake -->|"inventory + ledger"| splitroot
    splitroot -->|"a PRD- slice folder"| groundbrd
    groundbrd -->|"verified [CG#n]/[DG#n]"| splitslice
    splitslice -->|"allocated ledger"| brdinterview
    brdinterview -->|"decisions.md + held [C] questions"| brdpackage
    brdpackage -->|"review bundle"| review
    review -->|"the returned review"| brdreconcile
    brdreconcile -->|"frozen decisions.md — PRD-eligible"| createprd
    brdreconcile -->|"frozen decisions.md"| createard
    brdreconcile -->|"frozen decisions.md"| specify
    brdinterview -.->|"decisions.md — no customer review, PRD-eligible"| createprd
    brdinterview -.->|"decisions.md — no customer review needed"| createard
    brdinterview -.->|"decisions.md — no customer review needed"| specify

    idea -->|"idea.md"| createprd
    createprd -.->|"prd.md — idea route only, optional"| groundprd
    groundprd -.->|"findings — a claim CONFIRMED"| updateprd
    groundprd -.->|"findings"| createard
    groundprd -.->|"findings"| specify
    createprd -.->|"existing prd.md — revise"| updateprd
    updateprd -.->|"updated prd.md — existing ARD"| createard
    updateprd -.->|"updated prd.md — existing specification"| specify
    updateprd -.->|"updated prd.md — existing Epics"| epics
    updateprd -.->|"updated prd.md — existing release note"| rnearly
    createprd -->|"prd.md"| createard
    createprd -->|"prd.md"| epics
    createprd -->|"prd.md"| specify
    createprd -.->|"prd.md"| rnearly
    createprd -.->|"prd.md"| prdproposal
    prdproposal -->|"each slice's proposal.md"| brdproposal
    createard -.->|"ard.md"| epics
    epics -->|"epic.md"| specify
    specify -.->|"optional PRD-level specification.md"| epics

    specify -->|"specification.md"| design
    design -->|"design.md"| implement
    design -.->|"design.md + specification.md"| ready
    ready -.->|"_readiness.md — advisory"| implement
    implement -->|"code + implementation.md"| document
    implement -.->|"implementation.md — diff grounding on"| rnfinal

    docsinit -.->|"a new docs repo + profile"| document
    docsinit -.->|"call: inline unless --no-brand"| docsbrand
    docsprofile -.->|"docs profile"| document
    docsinit -->|"source_repos[] in the profile"| docsaudit
    docsprofile -.->|"docs profile"| docsaudit
    docsinit -->|"docs profile"| docsserve
    docsprofile -.->|"dev_servers block"| docsserve
    docsbrand -.->|"action: preview the branded site"| docsserve
    createard -.->|"ard.md"| docsaudit
    rnfinal -.->|"release-notes.md"| docsaudit
    docsaudit -->|".dev-workflows/docs-backlog.yml"| manualdocs
    manualdocs -.->|"action: optional prose edit"| documentdirect
    documentdirect -.->|"edited pages — unit tracking stays manual"| manualdocs
    manualdocs -.->|"action: periodic --refresh"| docsaudit
    frames -.->|"design/ frame-set index"| groundbrd
    frames -.->|"design/ frame-set index"| groundprd

    classDef prod fill:#dbeafe,stroke:#1d4ed8,color:#1e3a8a
    classDef dev fill:#dcfce7,stroke:#15803d,color:#14532d
    classDef docs fill:#fef3c7,stroke:#b45309,color:#78350f
    classDef core fill:#ede9fe,stroke:#6d28d9,color:#4c1d95
    classDef cust fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef manual fill:#f3f4f6,stroke:#6b7280,color:#1f2937,stroke-dasharray:5 5
```

## Reading it

- **Solid arrows carry the main inputs**, to commands or to manual work. **Dashed arrows** carry optional inputs, conditional reruns, advice (`/ready`'s verdict), or explicit `action:` / `call:` labels. An artifact edge is not an automatic invocation. Whether a command also waits for its input to be merged is a per-command gate, described on its own page.
- **`/prd-ground` is one command drawn separately for each route**, not a missing `/brd-ground`. A root BRD is split first, then each slice is grounded before its allocation walk and interview. An idea-route PRD may be grounded but never enters `/brd-split`. BRD authoring also reads the slice's findings after the decision handoff; those extra input edges are omitted here.
- **The BRD route joins the PRD ladder at the slice folder**, not at an `idea.md`. The three authoring commands are alternatives, not a sequence, and each gates the slice's `decisions.md`. `/brd-reconcile` offers them once the customer's answers are frozen. `/brd-interview` offers them directly when every question was settled from the findings, so the slice needs no customer review — `/create-prd` there, as after a reconciliation, only where a row the slice claims is `covered-here`.
- **`/update-prd` offers reruns for existing downstream artifacts** — architecture, specification, Epics and release notes — and recommends a rerun when the update invalidates one. These edges do not require creating artifacts that do not yet exist. The specification-to-Epics edge is optional enrichment from a PRD-level `specification.md`, not a requirement to specify before splitting.
- **`/docs-workflows:release-notes` is drawn twice** to show PRD-driven drafts or refreshes and the post-implementation note. The final run reads nothing `/document` writes, so the two documentation commands are independent. This command, `/dev-workflows:upgrade`, `/workflows-core:statusline` and `/workflows-core:feedback` use qualified names because their bare names collide with built-ins, and `/dev-workflows:design` because its bare name does on the accounts Claude Code's own `/design` is switched on for.
- **The audit backlog has a manual implementation stage.** Select an actionable unit, write its page, maintain its `unit:` metadata and backlog `page_path` / `status`, verify its claims, and publish it. `/document` direct mode can help with a described prose edit, but it never reads the backlog or manages unit status; keyed mode remains the feature-documentation route. `/docs-write` is planned, not shipped. The `docs-workflows` documentation route page describes the manual procedure; `--refresh` re-audits coverage and does not replace verification.
- **`/ready` sits beside the spine, not on it.** Its verdict is advice `/implement` reads; it blocks nothing.
- **The Anytime lane hands no deliverable to the pipeline** except `/frames`' frame-set index, which `/prd-ground`'s design grounding needs. The portal lane prepares the documentation repository `/document` writes into, and `/docs-serve` only previews it.

## The detail, per plugin

Each plugin's own workflow page draws its commands in full, with the loops and conditions this map leaves out:

- `product-workflows` — its Workflow overview page, and its BRD workflow page for the six-command route with its re-entry loops.
- `dev-workflows` — its Workflow overview page.
- `docs-workflows` — its Workflow overview page, and its docs workflow page for the portal procedure.
- `workflows-core` — [Workflow](workflow.md), for what this plugin gives the other three.

The roles are described on each plugin's Roles and phases page; this plugin's own is [Roles and phases](roles-and-phases.md).

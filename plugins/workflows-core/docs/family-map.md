# Family map

This page shows the whole plugin family on one diagram: every slash command of `product-workflows`, `dev-workflows`, `docs-workflows`, `security-workflows` and `workflows-core`, from the two ways work enters — `/idea` and `/brd-intake` — to shipped code, its documentation and its release notes. Each lane is a **role**. Each command is **coloured by the plugin that ships it**. Labels name artifacts or explicitly marked actions; gray manual steps are not commands.

**Where to start.** The nodes outlined in red and marked ▶ are the entry points:

- **An idea of your own** — `/idea <PRD-KEY>`, then `/create-prd`.
- **A customer's business requirements document** — `/brd-intake <BRD-KEY> @<brd-file>`, the start of the six-command BRD route.
- **A documentation portal for a project that has none** — `/docs-init`, once per documentation repository; a documentation repository that already exists is profiled with `/docs-profile` instead.
- **Anytime** — the commands in the Anytime lane start on their own and hand nothing to the pipeline, save `/frames`.

```mermaid
flowchart TD
    subgraph KEY["Legend"]
        kprod["product-workflows"]:::prod
        kdev["dev-workflows"]:::dev
        kdocs["docs-workflows"]:::docs
        kcore["workflows-core"]:::core
        ksec["security-workflows"]:::sec
        kmanual["Manual work — no command"]:::manual
        kentry["▶ entry point — start here"]:::entry
    end

    subgraph BRDR["PM — BRD route (entry for a customer's requirements document)"]
        brdintake["▶ start — /brd-intake"]:::prod
        splitroot["/brd-split (root)"]:::prod
        splitslice["/brd-split (slice)"]:::prod
        brdinterview["/brd-interview"]:::prod
        brdpackage["/brd-package"]:::prod
        brdreconcile["/brd-reconcile"]:::prod
        groundbrd["/prd-ground (BRD slice)"]:::prod
    end
    subgraph CUST["Customer — off-platform, nothing installed"]
        review["reviews the bundle"]:::cust
    end
    subgraph PMR["PM — idea route and the PRD"]
        idea["▶ start — /idea"]:::prod
        createprd["/create-prd"]:::prod
        updateprd["/update-prd"]:::prod
        rnearly["/docs-workflows:release-notes (PRD draft / refresh)"]:::docs
        groundprd["/prd-ground (idea PRD)"]:::prod
    end
    subgraph EST["PM — effort proposals (gate nothing)"]
        prdproposal["/prd-proposal"]:::prod
        brdproposal["/brd-proposal"]:::prod
    end
    subgraph PA["PA — architecture"]
        createard["/create-ard"]:::prod
        harvest["/harvest-decisions"]:::prod
        promote["/promote-decisions"]:::prod
    end
    subgraph PE["PE — breakdown and specification"]
        epics["/epics"]:::prod
        specify["/specify"]:::prod
        conformanceprd["/dev-workflows:conformance (PRD)"]:::dev
    end
    subgraph DEV["Dev — build and verify"]
        design["/dev-workflows:design"]:::dev
        ready["/ready"]:::dev
        implement["/implement"]:::dev
        conformanceepic["/conformance (Epic)"]:::dev
        secscan["/security-workflows:scan"]:::sec
    end
    subgraph SEC["Security Engineer — audit"]
        secrepo["/security-workflows:scan — a repository, --verify-fixes, --triage"]:::sec
    end
    subgraph DOC["Dev — documentation and release notes"]
        document["/document (keyed)"]:::docs
        rnfinal["/docs-workflows:release-notes (final)"]:::docs
    end
    subgraph PORTAL["Dev — documentation portal, off the spine"]
        docsinit["▶ docs start — /docs-init"]:::docs
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
    splitroot -.->|"Ground now (operator-elected, after the split PR merges)"| groundbrd
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
    createprd -.->|"idea route — the PRD folder, at any readiness"| prdproposal
    splitroot -.->|"BRD route — each slice, at any readiness"| prdproposal
    prdproposal -->|"BRD route — each slice's proposal.md, rolled up for the BRD"| brdproposal
    createard -.->|"ard.md"| epics
    epics -->|"epic.md"| specify
    specify -.->|"optional PRD-level specification.md"| epics
    createard -.->|"merged ard.md"| harvest
    harvest -.->|"team decision records"| createard
    harvest -.->|"team decision records"| specify
    harvest -.->|"team decision records"| design
    harvest -.->|"team decision records"| promote
    promote -.->|"accepted org ADRs — grounding"| createard

    specify -->|"specification.md"| design
    design -->|"design.md"| implement
    design -.->|"design.md + specification.md"| ready
    ready -.->|"_readiness.md — advisory"| implement
    implement -->|"code + implementation.md"| document
    implement -->|"Epic: the Dev, before its pull request merges"| conformanceepic
    conformanceepic -.->|"fix the code — a follow-up"| implement
    conformanceepic -.->|"the Dev's proposed decisions"| conformanceprd
    conformanceprd -.->|"PRD: the PE, every Epic merged — amend the document"| specify
    conformanceprd -.->|"amend the PRD"| updateprd
    implement -.->|"implementation.md — diff grounding on"| rnfinal
    conformanceepic -.->|"action: then the security scan, still before the merge"| secscan
    secscan -.->|"fix — a follow-up + patch, on the Epic's branch"| implement
    secscan -.->|"action: once a fix has merged, or decisions await review"| secrepo
    secrepo -.->|"fix — an /implement prompt line, or a follow-up with a key"| implement

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
    classDef sec fill:#ccfbf1,stroke:#0f766e,color:#134e4a
    classDef cust fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef manual fill:#f3f4f6,stroke:#6b7280,color:#1f2937,stroke-dasharray:5 5
    classDef entry stroke:#dc2626,stroke-width:3px
    class idea,brdintake,docsinit entry
```

## Reading it

- **Solid arrows carry the main inputs**, to commands or to manual work. **Dashed arrows** carry optional inputs, conditional reruns, advice (`/ready`'s verdict), or explicit `action:` / `call:` labels. An artifact edge is not an automatic invocation. Whether a command also waits for its input to be merged is a per-command gate, described on its own page.
- **`/prd-ground` is one command drawn separately for each route**, not a missing `/brd-ground`. A root BRD is split first, then each slice is grounded before its allocation walk and interview. An idea-route PRD may be grounded but never enters `/brd-split`. BRD authoring also reads the slice's findings after the decision handoff; those extra input edges are omitted here.
- **The BRD route joins the PRD ladder at the slice folder**, not at an `idea.md`. The three authoring commands are alternatives, not a sequence, and each gates the slice's `decisions.md`. `/brd-reconcile` offers them once the customer's answers are frozen. `/brd-interview` offers them directly when every question was settled from the findings, so the slice needs no customer review — `/create-prd` there, as after a reconciliation, only where a row the slice claims is `covered-here`.
- **`/update-prd` offers reruns for existing downstream artifacts** — architecture, specification, Epics and release notes — and recommends a rerun when the update invalidates one. These edges do not require creating artifacts that do not yet exist. The specification-to-Epics edge is optional enrichment from a PRD-level `specification.md`, not a requirement to specify before splitting.
- **`/docs-workflows:release-notes` is drawn twice** to show PRD-driven drafts or refreshes and the post-implementation note. The final run reads nothing `/document` writes, so the two documentation commands are independent. This command, `/dev-workflows:upgrade`, `/workflows-core:statusline` and `/workflows-core:feedback` use qualified names because their bare names collide with built-ins, and `/dev-workflows:design` because its bare name does on the accounts Claude Code's own `/design` is switched on for.
- **The audit backlog has a manual implementation stage.** Select an actionable unit, write its page, maintain its `unit:` metadata and backlog `page_path` / `status`, verify its claims, and publish it. `/document` direct mode can help with a described prose edit, but it never reads the backlog or manages unit status; keyed mode remains the feature-documentation route. `/docs-write` is planned, not shipped. The `docs-workflows` documentation route page describes the manual procedure; `--refresh` re-audits coverage and does not replace verification.
- **The PA lane keeps its own decisions.** `/harvest-decisions` turns the decisions of merged ARDs into team records that `/create-ard`, `/specify` and `/dev-workflows:design` ground on; `/promote-decisions`, run in the architecture repository, proposes organisation ADRs from them, and once one is accepted grounding cites the ADR instead of the record. The product-workflows Workflow overview page draws the whole loop.
- **`/ready` sits beside the spine, not on it.** Its verdict is advice `/implement` reads; it blocks nothing.
- **`/dev-workflows:conformance` is drawn twice, once per role.** In the Dev lane the Dev checks an Epic before its pull request merges, on its branch, and the decisions are proposals; in the PE lane the PE checks the whole PRD once every Epic has merged, ruling on every Dev decision, and the PE's decisions are final.
- **`/security-workflows:scan` is never run for you, and it is drawn once per role.** In the Dev lane it is the Dev's scan of their own Epic: offered after the Epic's `/conformance`, it runs before the merge, on the Epic's branch, reads code through Claude Security, a plugin outside the family, and records what it finds in the specs repository. A finding marked fix comes back to `/implement`, which continues on the Epic's branch, so the fix joins the open pull request. In the Security Engineer lane are that role's own runs: a scan across a repository, `--verify-fixes`, which closes fixes once they have merged, and `--triage`, which reviews the Dev's decisions; those decisions never wait on that review. Both nodes are teal, because a colour names the plugin, not the role.
- **The Anytime lane hands no deliverable to the pipeline** except `/frames`' frame-set index, which `/prd-ground`'s design grounding needs. The portal lane prepares the documentation repository `/document` writes into, and `/docs-serve` only previews it.

## The detail, per plugin

Each plugin's own workflow page draws its commands in full, with the loops and conditions this map leaves out:

- `product-workflows` — its Workflow overview page, and its BRD workflow page for the six-command route with its re-entry loops.
- `dev-workflows` — its Workflow overview page.
- `docs-workflows` — its Workflow overview page, and its docs workflow page for the portal procedure.
- `security-workflows` — its Workflow overview page.
- `workflows-core` — [Workflow](workflow.md), for what this plugin gives the other four.

The roles are described on each plugin's Roles and phases page; this plugin's own is [Roles and phases](roles-and-phases.md).

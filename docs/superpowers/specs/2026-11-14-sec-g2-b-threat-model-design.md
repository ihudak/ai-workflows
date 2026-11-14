# SEC-G2 B: the ARD threat model

Date: 2026-11-14. Status: draft, revision 3 (after Fable's builder review and its re-check), for the maintainer's approval. Roadmap row **B** of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` ("ARD threat model: `threat-model.md`, with security decisions proposed as `[AD#N]` through `/create-ard`"), the first of SEC-G2's three sub-projects (B, then C, then D). It depends on A (the scan and its findings registers) and on E (SEC-G1, the architecture feedback loop).

Every decision is written with a recommended answer. The four marked **(maintainer)** at the end are the calls only the maintainer can make; the rest are the author's, stated so they can be corrected.

## Intent

A product architect who designs a feature's architecture with `/create-ard` records decisions, components and contracts, and since SEC-G1 is challenged by the weaknesses the security registers already show for the repositories the work touches. Nothing yet asks, of the **planned** architecture, *what can an attacker do at each component and at each interface between them, and what does the architecture do about it?* Claude Security answers a similar question of the code as it stands, at scan time; it cannot answer it for a design not yet built, and keeps its own model only in memory (`/security-workflows:scan` copies its four report files and nothing else).

B adds that question to `/create-ard`, as an optional step the PA takes in the same run as the ARD. Its output is a second document beside the ARD, `threat-model.md`: one numbered threat per concrete attack on a named component or contract, each with one disposition. A threat the architecture answers is answered by ordinary `[AD#N]` decisions in the ARD, so everything the family already does with ARD decisions applies unchanged: every reviewer treats a violated Rule as a BLOCKER, `/conformance` traces it against the merged code, and once `/harvest-decisions` has minted the team record, SEC-G1's "prevented" test sees it through its `Prevents:` CWE. A threat left to the detailed design is handed to sub-project C; an accepted residual risk is recorded with an owner, a reason and a date to look at it again.

**Why now:** the maintainer's program builds every planned track before a customer-demo run from `/brd-intake`; a big customer feature is where a design-time threat model is expected, and B is the root C and D depend on.

## Goals

1. **`threat-model.md`, written by `/create-ard`** beside the ARD, in the same run, review and pull request. No new command and no new branch prefix.
2. **Every threat has one disposition**: mitigated by one or more `[AD#N]` (optionally with a remainder deferred to design), deferred to design, or accepted.
3. **Security decisions are proposed as `[AD#N]`** that meet `ard-format`'s full bar and fields, with `Prevents:` naming the CWE where the threat names one; the PA decides each as any ARD decision is decided.
4. **C and D get stable, unambiguous handles now**: `[TH#N]`, never renumbered; *Where* resolved against the run's resolved component set; every cited decision named with the ARD file that holds it.
5. **No regression**: a run that declines the model, a PRD with none, and every command that does not read one behave as before — save one named, visible change (T9: `/document` and `/release-notes` may print a checkout note for the new file).

## Non-goals

- **C and D.** No `/design` threat review and no security conformance. Nothing reads `threat-model.md` outside `/create-ard` and its reviewer yet.
- **Claude Security's model.** Not consumed, copied or persisted; it describes code at scan time and is deleted with the run directory.
- **A new command, plugin dependency or role.** No `/threat-model`, nothing under `$SPECS_PATH/security/` (kept for a team's own documents and the register), no dependency on `security-workflows`, no Security Engineer role in `product-workflows`. The Security Engineer reviews the pull request.
- **Risk scoring** (DREAD, likelihood × impact, CVSS), **attack trees, data-flow diagrams**, and **CAPEC as a required field**.

## Anti-goals

- **A generic STRIDE checklist.** Every threat names its element, a concrete attacker action and the asset at stake, or it is not written.
- **A model nobody confirmed.** The agent proposes; the PA keeps, edits or drops each threat.
- **Text steering the model.** Code, scanner output and register-derived values are data. The threat modeler has no tools (T6): it can open no register and nothing under `security/`.

## Decisions

### T1. `/create-ard` produces it, optionally, in the same run

A new phase in `/create-ard`, after its decisions are drafted and grilled (Phase 4, which grills the challenges Phase 3 step 6's grounding raised, SEC-G1's `known-weakness` ones among them) and before its review gate, asks once:

- **Not offered** where no component set resolves (T4, *Where*): the run prints one line saying why and goes on as today. Where the folder already holds a model and no set resolves, the model can be neither checked nor refined: the run leaves it as it stands and says so in one line (a known limit).
- **Recommended** where the run's class is `HIGH-RISK`, or the grounder's `arch_challenges` hold a `known-weakness` entry. (`SIGNIFICANT` alone is common for cross-repository PRDs, so it does not by itself recommend the model.)
- **Choices** (verbatim, no "Other"): *Add a threat model (Recommended)* / *Not this time*; on a folder already holding `threat-model.md`, see T10.
- **Declined:** the run is today's run.

`threat-model.md` joins the run's `deliverable_paths`. **It is an advisory deliverable** (a later `/create-ard` reads it, T10; nothing gates on it), so it does not change the run's handoff class: `create-ard.md`'s array selection — today "the ARD file(s) alone and new" → the falling-back array, else the stopping one — is reworded so that `threat-model.md` beside the ARD leaves the choice as the ARD alone would make it (`phase-handoff`'s strongest-class rule). **`phase-handoff` itself needs two edits** (maintainer question 2): a §4.0 register row for `threat-model.md`, which `phase-handoff` requires of "a producer adding a deliverable … in the same change", and the sentence stating `/create-ard`'s deliverable set.

**Why not a separate command:** a new producer needs a twelfth branch prefix copied in about seven places, most of them GIT-G1's; the roadmap says the decisions are proposed "through `/create-ard`"; and `/create-ard` already holds the components, contracts, code scan, grounding and Opus gate. **Why not `security-workflows`:** it depends on Claude Security, and no family plugin may depend on it.

### T2. The PA owns it; the run costs as `/create-ard` does

The PA authors and records; the cost entry is `/create-ard`'s existing `architecture` / `pa` row.

### T3. A separate file beside the ARD

`threat-model.md`, in the folder of the ARD it accompanies: a PRD folder, an Epic folder, or a BRD-route slice (the kind gate tests the artifact, never the folder's asserted kind). One per folder, covering that folder's `ard.md` and any `ard-<area>.md`.

- **Never `ard-*.md`**: three readers take any `ard-<x>.md` as a per-area ARD (`ard-resolution`, the lineage table, the harvest, which would mint team records from it).
- **Frontmatter `kind: threat-model`**, naming no folder kind, so the file is never read as the folder's carrier.

**Why not a section of `ard.md`:** the roadmap names the file; the model has a different reader (the Security Engineer) and rate of change, and C and D consume it on its own.

### T4. The format: `workflows-core:threat-model-format`

In `workflows-core` because `/design` and `/conformance` (`dev-workflows`) will read it in C and D, and a reference crosses a plugin boundary only from `workflows-core` (`ard-format` itself is `product-workflows`', which is why consumers read ARDs through `workflows-core:ard-resolution`). The shape, for the plan to fix exactly:

- **Frontmatter**: `kind: threat-model`, the key, `status` as the ARD's, the lineage record.
- **`## Scope`**: the component ids and contract rows considered; **`## Not considered`**: what was left out and why.
- **`## Threats`**: one `### [TH#N] <title>` each, with:
  - **Category**: one STRIDE letter, optional to fill — a completeness prompt, never a score; a field is cheaper to drop later than to add.
  - **Where**: component ids, and the contract row's decision where the threat crosses a boundary. **Resolved against the run's resolved component set** — `ard-resolution`'s step 4 and `workflows-core:components` §3 — never against the ARD's own `components:` alone, which only a PRD-level ARD carries; contract rows exist only in a PRD-level ARD with two or more `kind: code` components, so an Epic-level threat names its `target:` component and, where it crosses a boundary, a contract row of the PRD-level ARD it inherits.
  - **Threat**: the attacker, the action and the asset.
  - **CWE**: optional, in the family's link form.
  - **Disposition**, one of:
    - `Mitigated by <decisions>` — one or more decisions, each named as **the ARD file and its id** (`ard.md [AD#3]`, `ard-payments.md [AD#2]`, or for the inherited PRD-level ARD its folder's key in the wikilink form, `[[<KEY>]] ard.md [AD#4]`, which pre-lint would otherwise rewrite a bare key into), since each ARD file numbers its own series; optionally followed by `; the rest deferred to design: <what>`;
    - `Deferred to design: <what the design must answer>`;
    - `Accepted — <owner>; <reason>; review by <YYYY-MM-DD>`.
  - **Superseded by `[TH#M]`** / **Withdrawn — `<reason>`**, as `product-workflows:ard-format`'s superseding rules: never renumbered, never deleted.
- **`## Inherited threats`** (an Epic's model): the PRD-level model's live threats as bullets — never `### [TH#N]` headings, so numbering and the lineage regex skip them. An Epic adds only threats its `target:` component raises. A BRD-route slice's model inherits none (a container holds no ARD).
- **Across folders**, a threat is named by its folder's key in the wikilink form and its id (`[[<KEY>]] [TH#2]`); a PRD and an Epic model both start at `[TH#1]`.

### T5. One new ID prefix: `[TH#N]`

`TH` is unused in the tree. It joins `check-id-grammar.sh`'s alternation, fixtures and selftest; `.claude/rules/gates-id-grammar.md` and `CLAUDE.md`'s list of taught prefixes; `pre-lint`'s auto-link branch 1 **and its scope** (today "PRD, ARD, Epic files only", which gains `threat-model.md`); and the new lineage row's items regex. Reviewer and pre-lint wording describes the dash form without quoting it, so no new `id-grammar-ok` marker is needed.

**No `[MT#N]`.** A mitigation the architecture owns is an `[AD#N]`; one it cannot own is the design's (C). A third ID kind would duplicate one of them.

### T6. `threat-modeler` proposes

A new `product-workflows` agent, pinned to Opus in its frontmatter as `ard-reviewer` is; `/create-ard`'s `model_routing` block gains its line. **It has no tools** — declared in the form that grants none, which the plan verifies with `claude plugin validate` and `validate-catalog.py` (omitting `tools:` grants every tool): everything arrives in the brief, and the command reads the weakness-classes JSON's fields itself (as the skill allows) and passes them inline. Dispatched once per run with:

- the drafted ARD's resolved components, contracts and decisions, from the run;
- the code scan the run already made, inline;
- where Phase 3 step 6's weakness-classes call ran (`security_registers: ON` and an id passed), the classes' validated fields, inline — each class a candidate threat named by its CWE, never by any register text. A class a live decision already prevents arrives disposed as `Mitigated by` that decision; a class the PA answered *Not in this ARD* in Phase 4 is proposed only as deferred, accepted or dropped, never as a new decision.

It returns up to **25 candidates**, ranked: on a contract row first, then those naming a CWE the registers show, then the rest; the overflow is named in one line. A candidate it proposes as `Mitigated by` carries a **full proposed decision** — title, Binds, Prevents (with the CWE), a testable Rule, Alternatives — and passes `ard-format`'s three-part bar; one that fails the bar is proposed as `Deferred to design` instead. It writes nothing and carries the untrusted-content block.

### T7. The PA walks the candidates

Four candidates per question call; each with its fields and four choices (verbatim, no "Other"): *Record an [AD#N] for it* / *Defer to design* / *Accept the risk* / *Not a threat — drop it*. Free text is normalised into one of the four or re-asked.

- **Record an [AD#N]**: the proposed decision is grilled as any ARD decision is (the Phase 4 path SEC-G1's challenge uses); an existing live decision may be named instead. A proposed decision may not reopen a verified or customer decision on the BRD route (`[VD#n]`, `[CD#n]`); a conflict goes to the ARD's `## Open questions`.
- **Accept the risk**: owner and reason, then the review horizon, as the scan's acceptance asks it: *90 days (Recommended)* / *30 days* / *180 days*.
- **Drop**: not written.

The PA may add a threat the agent did not propose.

### T8. The review gate: one review over both documents

The `ard-reviewer` dispatch for the folder's `ard.md` (its input contract needs an ARD path) also receives `threat-model.md`, the folder's other ARD files and, on a refine, the prior model. **One review and one fix cycle cover both documents**, under `/create-ard`'s existing cap; **a fix to a model finding never adds or changes a decision** — it re-disposes the threat — so the model's review cannot change the ARD after the ARD's verdict. Dimensions:

- BLOCKER: a threat with no disposition, or more than one kind of disposition; a *Where* id not in the resolved component set; a `Mitigated by` naming a decision that is not live in the ARD file it names; an acceptance missing its owner, reason or date; a renumbered or deleted `[TH#N]` against the prior model.
- MAJOR: a decision recorded for a threat missing a field `ard-format` requires (as `ard-reviewer` already raises it).
- MINOR: a component or contract row in `## Scope` that no threat names and `## Not considered` does not explain.

**After the one fix cycle**, where every unresolved BLOCKER is the model's and the folder held no model before this run, `/create-ard` asks its own question once, before the shared per-BLOCKER escalation (whose four-option array is fixed and shared by eight commands): *Hand off the ARD without the threat model* / *Settle the model's findings*. The first drops the new model from `deliverable_paths` and does not write it into the specs tree (an unwritten draft leaves no uncommitted path for the next preflight, and no unreviewed model for the next run to find); the ARD is never held hostage by its optional companion. On a refine there is no such escape: re-disposing the blocking threats (T10) is always possible.

### T9. Lineage: a covered kind, recording the ARD

A `threat-model` row in `lineage-kinds.json`: matches `^threat-model\.md$`, items `[TH#N]`, altitude `architecture`, reviser `/product-workflows:create-ard <KEY>`, and the same exclusions as the `ard` row (the lines `/conformance` writes), so D can write into it later without making it look revised. **It records the folder's ARD files**, captured in Phase 6 after the ARD's own `stamp` and `accept` (the ARD is the model's real input, and the lineage rule only bars recording a document that records this one); an Epic's model also records the PRD folder's `threat-model.md`. It records nothing else: an upstream check walks on through each covered upstream's own record, and re-capturing the PRD at Phase 6 would break "captured when the run reads the input". The chain prose places it after the folder's ARDs.

The visible change elsewhere: `/document` and `/release-notes` keep every path a kind matches, so they may print a checkout note naming `threat-model.md`.

### T10. A refine run

Phase 0 detects `threat-model.md` beside the ARD and hands a copy of it (`prior_threat_model`, as `prior_ard`) to the reviewer and pre-lint. Whenever the folder holds a model — one from an earlier run, or one this run drafted — and a set resolves, **the run checks it mechanically, whatever the PA answers** — every cited decision live in the ARD file it names, every *Where* id still in the set — **twice**: at the new phase, to choose its question, and again in Phase 6 before the model is stamped, since Phase 5's fixes and manual fix notes can still supersede a decision.

- **The check passes:** *Refine the threat model (Recommended)* / *Leave it as it is*.
- **The check fails:** *Leave it* is not offered. **The forced part is only a re-disposition of the stale entries** — no modeler dispatch and no candidate walk: each stale threat is re-disposed through T7's four choices, and `Deferred to design` or `Accepted` is always available with no new decision, so the PA can always finish. A stale model would send C and D to dead decisions.
- **The second check fails** (Phase 5 changed a decision after the first): the run re-disposes the newly stale entries before the model is stamped, offering only *Defer to design*, *Accept the risk* or naming an existing live decision — never a new decision, which would change the ARD after its review (T8).
- **On an existing `[TH#N]`, *Not a threat — drop it* means `Withdrawn`**, with the reason; a threat is never deleted.
- **A refine** keeps every `[TH#N]`, re-dispatches the modeler with the current threats (it proposes only what the changed architecture adds), and lists every acceptance past its review date for the PA to renew, re-dispose or keep. **The model follows the ARD's refine-versus-fresh semantics**: whatever *Start fresh* does to the ARD's numbering, it does to `[TH#N]`.

### T11. Pages, counts and claims

- The `/create-ard` page gains *The threat model*; references and agents pages gain their rows; the family map's PA lane and the `roles-and-phases` pages name the output; the security plugin's roles page says the Security Engineer reviews it in the pull request.
- **Counts and inventories**: `CLAUDE.md`'s `product-workflows` subagent count, its `workflows-core` reference count and the hard-constraint ID list; the counts in `.claude/rules/product-workflows.md` and `.claude/rules/workflows-core.md`; `create-ard.md`'s description; check 16's preamble on the new agent; the `product-workflows` plugin description (896 characters: new wording replaces old).
- **Claim sweep** (refinements 4–8): the roadmap row B gains *Built as SEC-G2 B*; the feature-gaps review's SEC-G2 row narrows to C and D; the security plugin's dated *Not built yet* note stays as history, and the new release gets its own entry.
- **Sizes**: `workflows-core.md`, `security-workflows.md`, the coupling file and `CLAUDE.md` are near their limits; the plan measures and splits or moves before adding.

### T12. Versions and coupling

`workflows-core` minor (format reference, lineage row, pre-lint), `product-workflows` minor (`/create-ard`, `threat-modeler`, `ard-reviewer`), the ID gate and its rules, and a `security-workflows` page-only patch. One coupling bullet stating what breaks: a newer `/create-ard` beside an older core cannot load `threat-model-format` and its lineage row is unknown — update both together. No runtime fallback.

## What is left to the builder

Field wording and order; the decision-pair syntax (T4); where the phase sits in `/create-ard`'s numbering, between the decisions and the review; the reviewer's dimension wording; the selftest fixtures; whether `HIGH-RISK`'s recommendation also names `classification` §1.1's two security bullets, if `/create-ard` records which bullets fired.

## Risks

- **`create-ard.md` grows** (about 1,000 lines): the phase cites the format reference and the agent for its detail.
- **Noise**: the 25 cap, the element + action + asset rule and the reviewer's *Where* check.
- **An `[AD#N]` added for a threat changes the ARD**: the review runs after T7, over both files, and T10's check runs after the ARD's last write.

## Questions for the maintainer

1. **Optional, or required at `HIGH-RISK`?** Recommended: optional everywhere (the ARD itself is optional, and an absent optional input never becomes a prerequisite); recommended at `HIGH-RISK` or a `known-weakness` challenge.
2. **Two edits to `phase-handoff`, a GIT-G1 file** (T1): its deliverable register row and the sentence naming `/create-ard`'s set. Recommended: B makes them, named in the pull request for the GIT-G1 owner (as SEC-G1's one CI step was). The alternative hands them to the GIT-G1 owner, and B ships only after they land.
3. **Who may accept a design-time risk?** Recommended: the PA alone, with the pull request as the Security Engineer's check — the page says so. The alternative marks each acceptance unconfirmed until a Security Engineer confirms it, as the register does a Dev's; that needs a confirming step B does not otherwise have.
4. **What is below the architecture?** Recommended: a mitigation that fails the decision bar, and a gap whose answer is a product requirement, both become `Deferred to design` — the requirement gap also as an ARD open question naming the `[TH#N]`, for `/update-prd`. D then traces nothing for them until C ships. The alternative relaxes the decision bar for security decisions.

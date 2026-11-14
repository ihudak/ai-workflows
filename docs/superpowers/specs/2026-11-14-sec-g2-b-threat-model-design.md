# SEC-G2 B: the ARD threat model

Date: 2026-11-14. Status: draft for the maintainer's approval. Roadmap row **B** of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` ("ARD threat model: `threat-model.md`, with security decisions proposed as `[AD#N]` through `/create-ard`"), the first of SEC-G2's three sub-projects (B, then C, then D). It depends on A (the scan and its findings registers) and on E (SEC-G1, the architecture feedback loop).

Every decision below is written with a recommended answer. The ones marked **(maintainer)** at the end are the calls only the maintainer can make; everything else is the author's call, stated so it can be corrected.

## Intent

A product architect who designs a feature's architecture with `/create-ard` today records decisions, components and contracts, and since SEC-G1 is challenged by the weaknesses the security registers already show for the repositories the work touches. Nothing yet asks, of the **planned** architecture, *what can an attacker do at each component and at each interface between them, and what does the architecture do about it?* Claude Security answers a similar question of the code as it already stands, at scan time; it cannot answer it for a design that is not built yet, and it keeps its own model only in memory (`/security-workflows:scan` copies its four report files and nothing else).

B adds that question to `/create-ard`, as an optional step the PA takes in the same run as the ARD. Its output is a second document beside the ARD, `threat-model.md`: one numbered threat per concrete attack on a named component or contract, each with exactly one disposition. A threat the architecture answers is answered by an ordinary `[AD#N]` decision in the ARD, so everything the family already does with ARD decisions applies to it unchanged: every reviewer treats a violated Rule as a BLOCKER, `/conformance` traces it against the merged code, the harvest carries it into the team's decision records, and SEC-G1's "prevented" test sees it through its `Prevents:` CWE. A threat left to the detailed design is handed to sub-project C, and an accepted residual risk is recorded with an owner, a reason and a date to look at it again.

**Why now:** the maintainer's program builds every planned track before a customer demo run from `/brd-intake`; a big customer feature is exactly where a design-time threat model is expected, and B is the root C and D depend on.

## Goals

1. **`threat-model.md`, written by `/create-ard`** beside the ARD it accompanies, in the same run, the same review and the same pull request. No new command and no new branch prefix.
2. **Every threat has exactly one disposition**: mitigated by an `[AD#N]`, deferred to the detailed design, or accepted (owner, reason, review date). A threat with none, or two, fails the review.
3. **Security decisions are proposed as `[AD#N]`** with a testable Rule, and with `Prevents:` naming the CWE where the threat names one. The PA confirms each before it is written; no decision is written without the PA (SEC-G1's rule, kept).
4. **C and D get stable handles now**: every threat is `[TH#N]`, never renumbered, and names the component ids and contract rows it lives on, resolved against the ARD's own `components:` and `## Contracts`.
5. **No regression**: a run that declines the threat model, a PRD with none, and every command that does not read one behave exactly as before.

## Non-goals

- **C and D.** No `/design` threat review and no security conformance. B records what they will need (Goal 4) and nothing reads `threat-model.md` outside `/create-ard` and its reviewer yet.
- **Claude Security's model.** Not consumed, copied or persisted: it describes code as it is, at scan time, and is deleted with the run directory. B models the plan.
- **A new command, plugin dependency or role.** No `/threat-model`, nothing under `$SPECS_PATH/security/` (which `specs-repo-git` keeps for a team's own documents and the register), no dependency on `security-workflows`, and no Security Engineer role in `product-workflows`. The Security Engineer reviews the pull request as any reviewer does.
- **Risk scoring.** No DREAD, likelihood × impact or CVSS. The disposition is the decision; a score invites false precision.
- **Attack trees, data-flow diagrams, CAPEC as a required field.** CAPEC may be linked like a CWE; nothing requires it.

## Anti-goals (would make B a failure even if it works)

- **A generic STRIDE checklist.** Thirty threats of the form "an attacker could spoof a user" are noise the PA will learn to skip. Every threat names its element, a concrete attacker action and the asset at stake, or it is not written.
- **A threat model nobody confirmed.** The agent proposes; the PA keeps, edits or drops each threat. Nothing is written on the agent's word.
- **Text steering the model.** Code, scanner output and register-derived values are data. The threat modeler reads no register and opens nothing under `security/`, as SEC-G1's agents do not.

## Decisions

### T1. `/create-ard` produces it, optionally, in the same run

A new phase in `/create-ard`, after its decisions are drafted and before its review gate, asks once whether to add a threat model:

- **Recommended** where the run's complexity class is `SIGNIFICANT` or `HIGH-RISK`, where the PRD touches `classification` §1.1's security triggers, or where SEC-G1's grounding raised a `known-weakness` challenge; otherwise offered without the recommendation.
- **Choices** (2–4, verbatim, no "Other"): *Add a threat model (Recommended)* / *Not this time*. On a refine run whose folder already holds `threat-model.md`, the question is *Refine the threat model (Recommended)* / *Leave it as it is*.
- **Declined:** the run is exactly today's run.

`threat-model.md` joins the run's `deliverable_paths`, so the existing `ard/` handoff commits and proposes it with the ARD in one pull request. No change to `phase-handoff`, `specs-repo-git` or any GIT-G1 file.

**Why not a separate command:** a new producer needs a twelfth branch prefix, copied in about seven places (`phase-handoff`, `specs-repo-git`, `branch-naming`, `specs-git.py` and its selftest, `session-branch.py`, three generated parts), most of them GIT-G1's; and the roadmap says the decisions are proposed "through `/create-ard`". `/create-ard` already holds every input the model needs: the components, the contracts, the code scan, the grounding and the Opus gate. **Why not `security-workflows`:** it depends on Claude Security, and no family plugin may depend on it.

### T2. The PA owns it; the run costs as `/create-ard` does

The PA authors and records; the run's cost entry is `/create-ard`'s existing `architecture` / `pa` row. The Security Engineer's touchpoints stay the register (through SEC-G1) and the pull request.

### T3. A separate file beside the ARD

`threat-model.md`, in the same folder as the ARD it accompanies: the PRD folder for a PRD-level ARD, the Epic folder for an Epic-level one; a BRD-route slice like any PRD folder (the kind gate tests the artifact, never the folder's asserted kind). One per folder, covering the folder's ARD and any per-area `ard-<area>.md`.

- **Never `ard-*.md`**: three readers take any `ard-<x>.md` as a per-area ARD (`ard-resolution`, the lineage table, the harvest, which would mint team records from it).
- **Frontmatter `kind: threat-model`**, which names no folder kind, so the file is never read as the folder's carrier (`addressing`'s rule; precedents `kind: design`, `kind: conformance-record`).

**Why not a section of `ard.md`:** the roadmap names the file; a threat model is read by a different audience (the Security Engineer), at a different rate of change, and C and D will consume it on its own. The cost of a file — one lineage row, one format reference, one pre-lint block — is paid once.

### T4. The format: a `workflows-core` reference

`workflows-core:threat-model-format` (core, because `/design` and `/conformance` in `dev-workflows` will read it in C and D, and a reference crosses a plugin boundary only from `workflows-core`; `ard-format` itself is `product-workflows`', which is why consumers read ARDs through `workflows-core:ard-resolution`). The shape, for the plan to fix exactly:

- **Frontmatter**: `kind: threat-model`, the key, `status` as the ARD's, and the lineage record.
- **`## Scope`**: the components (by id) and the contract rows (by their `[AD#N]`) the model considered, read from the ARD in the same run, and **`## Not considered`**: what was left out and why (a component out of the PRD's scope, a third-party system the team does not run).
- **`## Threats`**: one `### [TH#N] <title>` each, with:
  - **Category**: one STRIDE letter (S, T, R, I, D, E) — a prompt for completeness, not a score.
  - **Where**: one or more component ids from the ARD's `components:`, and the contract row's `[AD#N]` where the threat crosses a boundary. Resolved against those sets, never parsed from prose (`CLAUDE.md`, *resolve against a known set*).
  - **Threat**: the attacker, the action and the asset, in one or two sentences.
  - **CWE**: optional, in the family's link form.
  - **Disposition**, exactly one of:
    - `Mitigated by [AD#N]` — a live decision in this ARD, or one the Epic inherits from its PRD's ARD;
    - `Deferred to design` — the detailed design answers it (sub-project C will review these);
    - `Accepted — <owner>; <reason>; review by <YYYY-MM-DD>`.
  - **Superseded by `[TH#M]`** / **Withdrawn — `<reason>`**, as `product-workflows:ard-format`'s superseding rules: never renumbered, never deleted.
- **An Epic-level model** inherits its PRD's threats read-only, as an Epic-level ARD inherits the PRD's decisions (`inherits:` and *Inherited invariants*; a BRD-route slice's model inherits the slice's, and the slice's own the parent BRD folder's, as the ARD does); it adds only threats its own components and contracts raise.

### T5. One new ID prefix: `[TH#N]`

`TH` is unused (checked against the gate's alternation and every bracketed prefix in the tree). It joins `check-id-grammar.sh`'s alternation (and its fixtures and selftest), `pre-lint`'s branch 1, `CLAUDE.md`'s list of taught prefixes, and a lineage items regex.

**No `[MT#N]` mitigation IDs.** A mitigation the architecture owns is an `[AD#N]` — already traced, enforced and harvested. One the architecture cannot own belongs to the design (C) and will be recorded there. A third ID kind would duplicate one of the two.

### T6. A new agent proposes; the PA disposes

`product-workflows:threat-modeler`, pinned to the Opus chain (`model-routing/classification` gains it in its caller list). It is dispatched once per run with:

- the drafted ARD's components, contracts and decisions (from the run, not re-read);
- the code scan the run already made (`code-scanner`'s results), for components that exist;
- SEC-G1's weakness-class JSON fields for the repositories the work touches — each class is a candidate threat the agent must consider, named by its CWE, never by any register text.

It returns candidate threats as structured data (the T4 fields, with a proposed disposition and, for `Mitigated by`, a proposed decision: title, testable Rule, `Prevents:` CWE). It writes nothing, reads no register, opens nothing under `security/`, carries the untrusted-content block, and holds **at most 25 candidates**, ranked: those on a contract row first, then those naming a CWE the registers show, then the rest; the overflow is named in one line, never silently dropped.

### T7. The PA walks the candidates

In batches, each candidate shown with its fields and a four-choice question (verbatim, no "Other"): *Record an [AD#N] for it* / *Defer to design* / *Accept the risk* / *Not a threat — drop it*. A free-text answer is normalised into one of the four or re-asked.

- **Record an [AD#N]**: the proposed decision is shown in full; the PA confirms or edits it; it is added to the ARD's decisions in the ARD's own format, numbered after the last, with `Prevents:` where the threat names a CWE. The threat's disposition becomes `Mitigated by [AD#N]`. An existing decision may be named instead of a new one.
- **Accept the risk**: asks for the owner and the reason; the review date defaults to 180 days ahead.
- **Drop**: the candidate is not written.

The PA may also add a threat the agent did not propose, in the same fields.

### T8. The review gate: `ard-reviewer` gains the threat model

Same run, so the same reviewer and the same one-fix-cycle cap. New dimensions, each a BLOCKER unless stated:

- every `[TH#N]` has exactly one disposition;
- every **Where** names a component id in `components:` or a contract row's `[AD#N]`;
- every `Mitigated by [AD#N]` names a live decision this folder's ARD holds or inherits;
- every acceptance has an owner, a reason and a date;
- a decision recorded for a threat has a testable Rule;
- (MAJOR) a component or contract row no threat names and `## Not considered` does not list.

### T9. Lineage: a covered kind at architecture altitude

A `threat-model` row in `lineage-kinds.json`: matches `^threat-model\.md$`, items `[TH#N]`, altitude `architecture`, reviser `/product-workflows:create-ard <KEY>`. It records the same upstreams as the ARD written in the same run (the PRD, `epic.md` for an Epic, the grounding, the decisions) and never records `ard.md`, its sibling output, not its input (`document-lineage`'s rule that a producer never records a document below its own output). `document-lineage`'s kind table and chain prose gain it; `lineage.py --selftest` covers it.

### T10. A refine run

A re-run of `/create-ard` on a folder holding `threat-model.md` reads it, offers to refine it (T1), and:

- keeps every `[TH#N]`, superseding or withdrawing rather than renumbering;
- re-dispatches the threat modeler with the current threats, so it proposes only what the changed architecture adds;
- lists every acceptance whose review date has passed, for the PA to renew, re-dispose or keep (one line each in the report).

### T11. Pages and claims

- The `/create-ard` page gains *The threat model*; the references page gains the format reference; the agents page gains `threat-modeler`; the family map's PA lane and the `roles-and-phases` pages name the new output; the security plugin's roles page says the Security Engineer reviews it in the pull request.
- **Claim sweep** (refinements 4–8): the roadmap row B gains *Built as SEC-G2 B*; the security plugin's *Not built yet* note and the feature-gaps review's SEC-G2 row are narrowed to C and D.

### T12. Versions and coupling

`workflows-core` minor (format reference, lineage row, ID gate, pre-lint, model-routing caller list) and `product-workflows` minor (`/create-ard`, `threat-modeler`, `ard-reviewer`); a `security-workflows` page-only patch if its roles page changes. One coupling bullet: a newer `/create-ard` beside an older core finds no `threat-model-format` and no lineage row — it must stop the threat-model phase with one line and run as today; an older `/create-ard` beside a newer core never offers the phase.

## What is left to the builder

The exact field wording and order in the format; the batch size in T7; the reviewer dimension wording; how the inherited-threat citation reads (following the ARD's inherited-decision form); where in `/create-ard`'s phase numbering the new phase sits, so long as it is after the decisions and before the review; the selftest fixtures.

## Risks

- **`create-ard.md` grows** (about 1,000 lines). Mitigation: the threat-model phase is short and cites the format reference and the agent for the detail.
- **Noise** (the anti-goal). Mitigation: the 25 cap, the "element + action + asset" rule in the agent and the reviewer's Where check.
- **An `[AD#N]` added for a threat changes the ARD the reviewer already read.** The review runs after T7, over both files.
- **The 180-day default** may not fit every team; it is a default the PA changes per acceptance.

## Questions for the maintainer

1. **(maintainer) Optional, or required at `HIGH-RISK`?** Recommended: optional everywhere, recommended at `SIGNIFICANT`/`HIGH-RISK`, the security triggers or a `known-weakness` challenge (T1). Required would make `/create-ard` refuse to finish a `HIGH-RISK` ARD without one.
2. **(maintainer) STRIDE as the category set?** Recommended: yes, as a completeness prompt only (T4). The alternative is no categories at all, CWE only.
3. **(maintainer) The 180-day default review date for an accepted threat** (T7) — the same horizon as the register's "a fix made in the last 180 days".

# SEC-G2 C: the design threat review

Date: 2026-11-14. Status: **draft for the maintainer's approval**. Roadmap row **C** of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:103` ("Design threat review: threats per interface of `design.md`, with amendments proposed through `/design`"; dependencies "A; B where present"), the second of SEC-G2's three sub-projects (B, then C, then D). It builds on B as built — `docs/superpowers/specs/2026-11-14-sec-g2-b-threat-model-design.md`, revision 3.2, on `feat/sec-g2-b-threat-model` — and on E (SEC-G1, `docs/superpowers/specs/2026-11-13-sec-g1-architecture-feedback-design.md`).

Every decision is written with a recommended answer. The four marked **(maintainer)** at the end are the calls only the maintainer can make; the rest are the author's, stated so they can be corrected. Statements about the tree cite `file:line` at B's head (`9ddad5f0`); a paragraph opening **Inference** is the author's reading, not the code's.

## Intent

B gave the architecture a threat model: `threat-model.md` beside the ARD, one `[TH#N]` per concrete attack, each with one disposition. Two of the three dispositions are closed when the model merges — a threat `Mitigated by` an `[AD#N]` binds every later artifact through that decision's Rule, and an `Accepted` one has an owner and a date. The third, `Deferred to design: <what the design must answer>`, is a debt handed down, and nothing collects it: `/dev-workflows:design` does not read the model (`plugins/workflows-core/references/threat-model-format.md:7`), so today a deferred threat is answered only if the Dev happens to open the file.

C makes `/design` collect it. In the same run as the design, after the interfaces are settled and before the review, an optional step asks of the **designed** interfaces what B asked of the planned architecture: which of the model's threats land on this design, what does the design do about each, and what do its own interfaces invite that the architecture could not see? Each answer is a design decision the Dev takes in the grill — an amendment to `design.md` — recorded with a testable Rule and the test that checks it, so that D can trace it to merged code. A threat the design cannot answer goes back to the architect.

**Why now:** B is built and its deferred threats have no reader; D cannot trace a mitigation that was never written down.

## What exists today

Facts the decisions rest on.

- **`design.md` defines no ids and its interfaces have none.** `## Interfaces / contracts` holds signatures and shapes; an interface joins the ARD only where it is a contract row, by that row's `[AD#N]` (`plugins/dev-workflows/references/design-format.md:114-115`). The lineage table records the design kind as `items: []`, "cites spec ids, defines none" (`plugins/workflows-core/scripts/lineage-kinds.json:54-70`).
- **`/design` never edits the ARD.** A deviation goes into `## ARD deviations` of `design.md` and a `- [ ]` open question (`plugins/dev-workflows/commands/design.md:224`; `plugins/workflows-core/references/ard-resolution.md:109-117`).
- **`/design` already writes notes into a document another plugin's command owns**: `## Engineering review` and `- [ ]` questions in `specification.md`, never its ids (`design-format.md:334-340`). `/dev-workflows:conformance` does the same to `prd.md`, `epic.md` and `ard.md` (`plugins/dev-workflows/commands/conformance.md:344-348`).
- **The lineage row for `threat-model` already excludes `## Engineering review` and checkbox lines**, "so a /dev-workflows:conformance note (sub-project D) never reads as a revision" (`lineage-kinds.json:121-141`).
- **A design must hand off with zero open questions** (`design-format.md:68-72`; `design.md:540`).
- **`/design`'s advisory channel to the architect is the pull request**: each `Architecture deviation:` line goes verbatim into `body_facts` (`design.md:547`), and it and the `Known weakness:` line are advisory, with no reviewer finding (`design-format.md:316`, `:320`).
- **`/design` already holds the registers' weakness classes** where `security_registers` is `ON`: its Phase 4 makes the `workflows-core:weakness-classes` call and carries the JSON's path (`design.md:304`); the grill answers a `known-weakness` challenge as a `Known weakness:` line (`design.md:345`).
- **`dev-workflows` depends only on `workflows-core`** (`plugins/dev-workflows/.claude-plugin/plugin.json:12-14`), so it cannot dispatch `product-workflows:threat-modeler`.
- **`/conformance` traces four documents, and `design.md` is not one**: `document: <specification.md | epic.md | prd.md | ard.md>` (`plugins/dev-workflows/references/conformance-format.md:74`; `references/handoff/conformance-tracer.md:26`). An item with no id is traced by quoted text.
- **`threat-model.md` is an advisory deliverable with two named readers**, and the claim that no other command reads it as a threat model stands in the format's opening and §8, in `.claude/rules/threat-model.md:26-30` and in `phase-handoff`'s register row (`plugins/workflows-core/references/phase-handoff.md:414`). The rules file says C must sweep it.
- **B's identity rules bind a threat once it stands on the default branch**, and the PA alone accepts a risk (`threat-model-format.md:74`, `:82`).

## Goals

1. **Every deferred threat that lands on a design is answered in that design, or visibly not.** The applicable set is resolved, never guessed.
2. **The answers are amendments the Dev decides in `/design`** — to `design.md`'s own sections — in the same run, review and pull request. No new command and no new branch prefix.
3. **D gets a handle now**: a design-level entry with a stable id, a testable Rule, the components it binds, the test that checks it and the `[TH#N]` it answers.
4. **The architect's file stays the architect's.** `/design` never writes, re-disposes or numbers a `[TH#N]`.
5. **No regression**: a design with no threat model on the default branch, and a run that declines the review, write the `design.md` they write today.

## Non-goals

- **D.** No security conformance; `/conformance`'s inventory and its `document:` enum are D's to extend.
- **Re-modelling the architecture.** C proposes no `[AD#N]` and re-disposes nothing; a threat that needs either goes back to `/create-ard`.
- **A review with no model.** Where no threat model stands on the default branch, the registers still reach the design as SEC-G1's `known-weakness` challenge, unchanged (maintainer question 4).
- **Ids for interfaces**, risk scoring, attack trees, data-flow diagrams — as B.
- **A dependency on `security-workflows` or `product-workflows`**, a new command, a new role.
- **`/implement` enforcing the answers.** `code-review`'s converge dimension traces `[Uxx]`/`[ACxx]`/`[TCxx]`; adding design-level entries to it is D's question.

## Anti-goals

- **A second threat model.** The design holds answers and the few threats its own interfaces add, never a copy of B's.
- **An answer nobody confirmed, or nobody can test.** The agent proposes; the Dev decides each; a `Mitigated` entry without a testable Rule and a test is a BLOCKER.
- **Text steering the model.** Model field text, code, scanner-derived values and an existing design's text are data; the proposing agent can read no file (D5).

## Decisions

### D1. A step of `/design`, optional, in the same run

A new step in `/design`'s Phase 5, after the two tracks and any interface fan-out have settled the interfaces and before the overlap read and the play-back that close the grill (`design.md:426`), so that its answers are read against what they overlap and confirmed at the gate like every other decision.

- **Not offered** where Phase 2.5 returned `status: none`; where no threat model passes D2's gate; or where no component set resolves (D3). No model anywhere prints nothing; any other case prints one line saying why.
- **Recommended** where at least one applicable threat is deferred, or the class is `HIGH-RISK`, or the grounder's digest holds a `known-weakness` challenge.
- **Choices** (verbatim, no "Other"): *Review the design's threats (Recommended)* / *Not this time*, the question's text giving the applicable threats by count and disposition. With no trigger, neither option carries the marker.
- **Declined:** the run is today's run. The final report carries one line, `Threat review: declined — <n> deferred threat(s) unanswered`, and `design.md` gains nothing.

**Why not a separate command:** the same ledger as B's T1 — a twelfth branch prefix, and the roadmap says "through `/design`". **Why not `design-reviewer` alone:** a reviewer rules on a finished draft; the roadmap asks for amendments *proposed*, which the Dev must decide before the review, not after it.

### D2. What it reads, and the gate

Two known paths, never a search: `<feature_folder>/threat-model.md` and, on an Epic run, the same file in the PRD folder above it — every `EPIC-` folder sits under a PRD folder (`design.md:547`), which on the BRD route is the slice. The test is the file and its `kind: threat-model`, never the folder's asserted kind. It reads the PRD-level model itself, never an Epic model's `## Inherited threats` bullets, which are copies (`threat-model-format.md:38`).

- **The gate.** Each path goes through `require-on-main` before it is read, as the family's hard constraint requires of a consumer. **Every row but `pass` falls back**: the model is not read, no review is offered, and one line names the path and the row. An absent optional input never becomes a prerequisite, and a model in flux never stops a design; an unmerged ARD beside it has already stopped the run (`ard-resolution.md:91`). This moves `threat-model.md` from *advisory* to *gated — falling back* in `phase-handoff` §4.0 and adds a §3.4 row (maintainer question 3).
- **B's check, read-only.** The run executes format §6's mechanical check on each model against Phase 2.5's ARD files and components. A stale live threat is listed in one line naming `/product-workflows:create-ard <KEY>` and left out of the walk; C never clears it.
- **The weakness classes** from Phase 4's existing call, their validated fields only, as B passes them (`plugins/product-workflows/commands/create-ard.md`, Phase 4.3 step 5, *Weakness classes*). No register is opened and no new call is made.
- **Lineage.** Where the review runs, each model read is captured at its first read and joins `design.md`'s `upstreams:` at Phase 7's stamp. A later re-disposition of a `[TH#N]` then shows the design stale through the existing upstream check, which is the feedback loop D7's hand-back relies on. A declined review records no model.

### D3. Which threats apply — resolved against known sets

- **An Epic folder's own model:** every live threat (it holds only what the Epic's target raises).
- **The PRD folder's model, on an Epic with a `target:`:** each live threat whose Where holds the target id, or whose `contract <pair>` names a row of Phase 2.5's `contracts` whose producer or consumers name the target — the rule B's brief uses for an Epic's contracts.
- **The PRD folder's model, on an Epic with no `target:`, or on a broad PRD-level design:** every live threat.

Of those, a **deferred** threat — `Deferred to design: …`, or `Mitigated by …; the rest deferred to design: …` — must be answered. A plainly `Mitigated by` threat already binds the design through its decisions' Rules in `applicable_ard`, and an `Accepted` one is context; both reach the agent and the reviewer as context only.

**The design's component set**, which a new entry's Where names: the Epic's `target:`; else Phase 2.5's `components`; else the ids on the model's `## Scope` line. Where none resolves, the review is not offered.

### D4. What it writes: `## Threat review` in `design.md`, with `[DT#N]` entries

An **optional** section of `design-format` (present only where a review ran; its absence means none ran, and needs no `_N/A_` line, as `## Pieces`, `design-format.md:76-80`), appended after the existing sections so no section number moves. It holds a line naming the models read, a `Considered, no threat:` list, and one entry per threat:

```markdown
### [DT#N]: <title>

- **Answers:** [[<KEY>]] [TH#N] | —
- **Where:** <component id>[, …]; interface <its contract pair, or its label in ## Interfaces / contracts>
- **Threat:** attacker: …; action: …; asset: …      (a new threat; an answered one cites the model's)
- **CWE:** <link> | —
- **Disposition:** <exactly one of the three forms below>
- **Test:** <the ## Test strategy line that checks the Rule> | —
```

1. `Mitigated — Rule: <testable statement>`. The answer is a design decision like any other: it lands in `## Interfaces / contracts`, `## Error handling & edge cases` and `## Test strategy`, and the entry points at it.
2. `Not this design's — <where it is answered, or why it does not arise here>`.
3. `Returned to the architect — <why the design cannot answer it>` (D7).

- **`[DT#N]` is one new id prefix**, unused in the tree, numbered per `design.md` from `[DT#1]`, with B's identity rules: bound once on the default branch, never renumbered or deleted, `- **Withdrawn:** <why>` for one made moot. It joins the id-grammar gate, its fixtures, `CLAUDE.md`'s list and pre-lint's design block. The design lineage row keeps `items: []`.
- **Every answered threat is named in the cross-folder form** `[[<KEY>]] [TH#N]`, since a PRD and an Epic model both start at `[TH#1]` (`threat-model-format.md:84`).
- **On a revision** of a design that already holds the section: entries keep their ids; an entry whose threat is no longer live or no longer deferred is withdrawn mechanically, naming the new disposition.

**Why one id for both kinds of entry:** D reads one heading form and joins to the model through `Answers`. **Why an id at all:** an id-less item is traced by quoted text and orphaned on the first edit. **Why not answer in `threat-model.md`:** one PRD-level threat can be answered by several Epics' designs, which one Disposition line cannot hold; the PA alone disposes; and `Deferred to design` stays true once the design has answered. This does not reopen B's "no `[MT#N]`": that rule keeps mitigation ids out of the model, and a `[DT#N]` identifies the threat as the design sees it.

### D5. `design-threat-modeler` proposes

A new `dev-workflows` agent, pinned to Opus, built on B's inert pattern (`.claude/rules/threat-model.md:32`): `tools: ["CronList", "ListAgents"]`, foreground only, **call no tool**, everything in one brief, every value one line, labels at column one, the untrusted-content block, and every refusal failing closed to "no candidate; the Dev may add their own". The brief carries the applicable threats (deferred, mitigated and accepted, labelled), the design's settled interfaces and boundary behaviour from `_design-session.md`, the component set, the contract rows, the code scan, the weakness-class fields with whether the grill already answered each, and on a revision the current entries.

It returns one proposed answer per deferred threat — a Rule, where it lands, its test — and up to **15** new candidates, ranked: on a boundary interface first, then those naming a CWE the registers show, then the rest. A candidate it cannot give a testable Rule is proposed as returned. **A mechanical backstop** drops any candidate holding a `SEC#n` id or a register path the brief did not carry.

**Why not reuse `threat-modeler`:** it is `product-workflows`', which `dev-workflows` does not depend on, and its contract is the ARD decision bar. Moving it to `workflows-core` would rename an agent B has just shipped for a brief that shares only its shape.

### D6. The Dev walks them

Four per question call, choices verbatim, free text normalised or re-asked (as B's T7).

- **A deferred threat:** *Answer it in this design* / *Not this design's* / *Return it to the architect*.
- **A new candidate:** *Answer it in this design* / *Propose it to the architect* / *Not a threat — drop it*.

*Answer it* grills the Rule as any design decision is grilled, and may not depart from an inherited `[AD#N]` Rule except as an ARD deviation (`design.md:417-418`). The Dev may add a threat. **The Dev never accepts a risk** (maintainer question 1).

### D7. Going back to the architect

For each `Returned` entry — a deferred threat handed back, or a new threat proposed — the run appends one `- [ ]` line under `## Engineering review` of the model that holds the threat (a proposal: the feature folder's model, else the PRD folder's), created at the end of the file where absent: the design's key, the `[TH#N]` or the proposed threat's Where and Threat, the reason, and the `[DT#N]`. The amended model joins `deliverable_paths`. It writes no `[TH#N]` block and no Disposition (maintainer question 2).

- **It does not block the handoff.** `design-reviewer` notes each as MINOR, as it does a recorded ARD deviation (`plugins/dev-workflows/agents/design-reviewer.md:196`); every `Returned` line goes verbatim into `body_facts` and the final report with `/product-workflows:create-ard <KEY>`; and D reports the threat unanswered until it is re-disposed.
- **`/create-ard` closes the loop:** on a refine, its Phase 4.3 lists the model's open notes beside the modeler's candidates, the PA disposes each through T7's choices, and the note is ticked with the outcome. `threat-model-format` §3 gains the optional section, and pre-lint's *Threat model* block allows it.

### D8. The review gate: one review, one document

`design-reviewer`'s brief gains the applicable threats and the model paths; a conditional dimension, skipped silently without them:

- BLOCKER: an applicable deferred threat no live entry answers; an entry with no disposition or more than one; a `Mitigated` entry with no Rule, or whose Test names no `## Test strategy` line; an `Answers` naming a threat that is not applicable; a renumbered or deleted `[DT#N]`.
- MAJOR: a Rule that cannot be tested, or that the design's own sections do not carry out; a design that falsifies an accepted threat's stated reason.
- MINOR: a `Returned` entry; a boundary interface no entry and no `Considered` line names.

One review and one fix cycle under the existing cap; fixes are ordinary edits to `design.md`. **No escape question**, unlike B's T8: the section is part of the document under review, and the shared per-BLOCKER escalation already offers an override.

### D9. Pages, counts, claims, versions

- **Claim sweep**, by subject — the model's readers: the format's opening and §8, `.claude/rules/threat-model.md` invariant 5 and its authority paragraph, `phase-handoff`'s register row, B's pages, roadmap row C (*Built as SEC-G2 C*), the feature-gaps review's SEC-G2 row (narrowed to D).
- **Counts and inventory**: `dev-workflows`' subagent count and workflow-map line, the `/design` page's new section, the agents and reference pages, the id list, `gates-id-grammar.md`, `/design`'s `model_routing` line. The cost entry is `/design`'s existing row.
- **Versions**: `workflows-core` minor (format, pre-lint, `phase-handoff`, the id gate), `dev-workflows` minor, `product-workflows` minor (`/create-ard`'s note walk), a `security-workflows` page-only patch. One coupling bullet: a newer `/design` beside an older core finds no `Engineering review` allowance and no gate row; beside an older `product-workflows`, its notes are written and never walked.

## Where the code leaves a choice open

- **`deliverable_paths` outside `feature_folder`.** `phase-handoff` §2.9 calls them "literal repo-relative paths" and I found no rule confining them to the folder; an Epic design amending the PRD folder's model relies on that. The builder verifies it against §2.2's stack test first.
- **`/design` on a design already on the default branch.** Phase 5.5 speaks of "a design this run revises" (`design.md:451`), but I found no single statement of the revision path; D4's revision rules attach wherever the builder finds it.
- **The upstream check's `docs`.** Whether a model joins Phase 2.5's `upstream-check` (`design.md:226`) as well as the record is the builder's; D2's read-only check already covers a model stale against its ARD.

## What is left to the builder

The step's number; field wording and order; the note's exact line; the agent's name; the 15 cap; whether a `Target span` component joins the component set; the reviewer's dimension wording; fixtures and selftests.

## Risks

- **`design.md` (684 lines) and `design-format` grow**: the step cites the format and the agent for detail.
- **Two Epic designs append to one PRD-level model** on separate branches: an end-of-file conflict, trivial to merge, named on the page.
- **A returned threat ships unanswered**: it is in the pull request, in the model as an open note, and in D's report; the lineage record brings the PA's answer back to the design.
- **Noise**: the cap, the element + action + asset rule, and `Not a threat — drop it`.

## Questions for the maintainer

1. **Who decides at design level?** Recommended: the Dev answers or returns each threat and never accepts a risk; a returned threat does not block the design's handoff, and the PA re-disposes it in `/create-ard`. The alternative lets the Dev accept, marked unconfirmed until the PA confirms, as the register does a Dev's — a confirming step C does not otherwise have.
2. **May `/design` write into `threat-model.md`?** Recommended: yes, `- [ ]` notes under `## Engineering review` only, never a `[TH#N]` block — as it does to `specification.md` and `/conformance` does to `ard.md`, and as the lineage row already allows. The alternative keeps every word in `design.md` and the pull request, and the PA finds returned threats there.
3. **Three edits to `phase-handoff`, a GIT-G1 file**: a §3.4 row for `/design`'s falling-back gate on the model, its §4.0 register row moved from advisory to gated, and the sentence naming `/design`'s deliverable set. Recommended: C makes them, named in the pull request for the GIT-G1 owner, as B did. The alternative hands them to that owner, and C ships after they land.
4. **Is the review offered where no threat model exists?** Recommended: no — the roadmap's "B where present" is met by SEC-G1's `known-weakness` challenge, which already brings the registers to every design, and a model-less review would have nowhere to return a threat. The alternative offers it at `HIGH-RISK`, writing `[DT#N]` entries with no `Answers` and no hand-back.

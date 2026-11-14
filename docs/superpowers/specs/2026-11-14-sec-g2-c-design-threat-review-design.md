# SEC-G2 C: the design threat review

Date: 2026-11-14. Status: **approved** by the maintainer 2026-11-14 (revision 2.1), with the recommended answer to each of the three questions below.

Every decision is written with a recommended answer. The three marked **(maintainer)** at the end are the calls only the maintainer can make; the rest are the author's, stated so they can be corrected. Statements about the tree cite `file:line` at B's head (`9ddad5f0`); a paragraph opening **Inference** is the author's reading, not the code's.

## Intent

B gave the architecture a threat model: `threat-model.md` beside the ARD, one `[TH#N]` per concrete attack, each with one disposition. Two of the three dispositions are closed when the model merges — a threat `Mitigated by` an `[AD#N]` binds every later artifact through that decision's Rule, and an `Accepted` one has an owner and a date. The third, `Deferred to design: <what the design must answer>`, is a debt handed down, and nothing collects it: `/dev-workflows:design` does not read the model (`plugins/workflows-core/references/threat-model-format.md:7`), so today a deferred threat is answered only if the Dev happens to open the file.

C makes `/design` collect it. In the same run as the design, after the interfaces are settled and before the review, an optional step asks of the **designed** interfaces what B asked of the planned architecture: which of the model's threats land on this design, what does the design do about each, and what do its own interfaces invite that the architecture could not see? Each answer is a design decision the Dev takes in the grill — an amendment to `design.md` — recorded with a testable Rule and the test that checks it, so that D can trace it to merged code. A threat the design cannot answer is recorded as returned to the architect, in the design and in its pull request.

**Why now:** B is built and its deferred threats have no reader; D cannot trace a mitigation that was never written down.

## What exists today

Facts the decisions rest on.

- **`design.md` defines no ids and its interfaces have none.** `## Interfaces / contracts` holds signatures and shapes; an interface joins the ARD only where it is a contract row, by that row's `[AD#N]` (`plugins/dev-workflows/references/design-format.md:114-115`). The lineage table records the design kind as `items: []`, "cites spec ids, defines none" (`plugins/workflows-core/scripts/lineage-kinds.json:54-70`).
- **`/design` never edits the ARD**, and the rule behind it is role separation: a deviation is recorded by the consumer "in its **own** artifact, NEVER in the ARD (role separation: the ARD is the architect's)" (`plugins/workflows-core/references/ard-resolution.md:109-117`; `plugins/dev-workflows/commands/design.md:224`).
- **The Dev's writes upstream are narrow.** `/design` writes `## Engineering review` and `- [ ]` questions into `specification.md`, never its ids (`design-format.md:334-340`). Into `ard.md` only `/conformance`'s **PRD run**, the PE's, writes a note (`plugins/dev-workflows/commands/conformance.md:344-348`); the Dev's Epic run proposes only. So nothing today has a Dev write into the architect's file.
- **`/create-ard` reads no `## Engineering review` note**: the phrase appears in none of `create-ard.md`, `ard-reviewer.md`, `ard-format.md` or `threat-model-format.md` (`grep -c 'Engineering review'` over the four prints 0 each), although the lineage row for `threat-model` excludes such a section (`lineage-kinds.json:121-141`).
- **`/design` has no revision path.** It detects a prior `_design-session.md` (`design.md:148-150`), never a prior `design.md`; Phase 5.5 mentions "a design this run revises" only for `## Pieces` (`design.md:451`).
- **A design must hand off with zero open questions** (`design-format.md:68-72`; `design.md:540`).
- **`/design`'s advisory channel to the architect is the pull request**: each `Architecture deviation:` line goes verbatim into `body_facts` (`design.md:547`), and it and the `Known weakness:` line are advisory, with no reviewer finding (`design-format.md:316`, `:320`).
- **`/design` already holds the registers' weakness classes** where `security_registers` is `ON` (`design.md:304`), and the grill answers a `known-weakness` challenge as a `Known weakness:` line (`design.md:345`).
- **`dev-workflows` depends only on `workflows-core`** (`plugins/dev-workflows/.claude-plugin/plugin.json:12-14`), so it cannot dispatch `product-workflows:threat-modeler`.
- **`/conformance` traces four documents, and `design.md` is not one** (`plugins/dev-workflows/references/conformance-format.md:74`; `references/handoff/conformance-tracer.md:26`).
- **`require-on-main` returns `stopped` and, only where that is false, `on_main: pass | pass_amending | absent | unmanaged`**; "a caller tests `stopped` before `on_main`" (`plugins/workflows-core/references/phase-handoff.md:371-385`). A falling-back caller already exists: `/brd-interview`'s defect-log row, where "on `absent`, as on every stopping row (§3.7), the run makes no such offer" (`phase-handoff.md:340`).
- **`threat-model.md` is an advisory deliverable with two named readers**; the claim that no other command reads it as a threat model stands in the format's opening and §8, in `.claude/rules/threat-model.md:26-30` and in `phase-handoff`'s register row (`phase-handoff.md:414`).
- **B's identity rules bind a threat once it stands on the default branch**, and the PA alone accepts a risk (`threat-model-format.md:74`, `:82`) — B's maintainer question 3, answered.

## Goals

1. **Every deferred threat that lands on a design is answered in that design, or visibly not.** The applicable set is resolved, never guessed.
2. **The answers are amendments the Dev decides in `/design`** — to `design.md`'s own sections — in the same run, review and pull request. No new command and no new branch prefix.
3. **D gets a handle now**: a design-level entry with a stable id, a testable Rule, the components it binds, the test that checks it and the `[TH#N]` it answers.
4. **`threat-model.md` stays the architect's alone.** `/design` writes nothing into it.
5. **No regression**: a design with no threat model on the default branch, and a run that declines the review, write the `design.md` they write today.

## Non-goals

- **D.** No security conformance; `/conformance`'s inventory and its `document:` enum are D's to extend.
- **`/create-ard`'s intake of returned threats** — a named follow-up (D7). In `product-workflows` C changes pages and one thing more: `create-ard.md` cites the backstop and the one-line rule where it states them today (D5).
- **Re-modelling the architecture.** C proposes no `[AD#N]` and re-disposes nothing.
- **A review with no model** (maintainer question 3).
- **A revision path for `/design`.** C adds only the prior copy its own section needs (D4).
- **Ids for interfaces**, risk scoring, attack trees, data-flow diagrams — as B.
- **A dependency on `security-workflows` or `product-workflows`**, a new command, a new role.
- **`/implement` enforcing the answers** — D's question.

## Anti-goals

- **A second threat model.** The design holds answers and the few threats its own interfaces add, never a copy of B's.
- **An answer nobody confirmed, or nobody can test.** The agent proposes; the Dev decides each; a `Mitigated` entry without a testable Rule and a test is a BLOCKER.
- **Text steering the model.** Model field text, code, scanner-derived values and a prior design's text are data; the proposing agent can read no file (D5).

## Decisions

### D1. A step of `/design`, optional, asked once per design

A new step in `/design`'s Phase 5, after the two tracks and any interface fan-out have settled the interfaces and before the overlap read and the play-back that close the grill (`design.md:426`), so that its answers are read against what they overlap and confirmed at the gate like every other decision. In the section-by-section write mode (`design.md:314`) it runs after the last section's gate and its edits go to the whole-artifact gate.

- **Not offered** where Phase 2.5 returned `status: none`; where no model is read (D2); or where no component set resolves (D3). No model anywhere prints nothing; any other case prints one line saying why.
- **Recommended** where at least one applicable threat is deferred, or the class is `HIGH-RISK`, or the grounder's digest holds a `known-weakness` challenge.
- **Choices** (verbatim, no "Other"): *Review the design's threats (Recommended)* / *Not this time*, the question's text giving the applicable threats by count and disposition. With no trigger, neither option carries the marker.
- **Declined:** the run is today's run. The final report carries `Threat review: declined — <n> deferred threat(s) unanswered`.
- **An existing `## Threat review` survives a decline, a fallback and a not-offered run**: the section is kept verbatim, named in the final report as *kept, not reviewed against the model*, and named so to `design-reviewer`, which then judges none of it but D8's identity check against the prior copy — so a hand-deleted or renumbered `[DT#N]` cannot pass in a section nobody reviewed.
- **Resume and loop.** The answer, each disposed candidate and the numbered interface list (D5) are recorded in `_design-session.md` as they settle, so a resumed run skips what is settled. In the *Next Epic* loop (`design.md:549`) the step is the Epic's, asked again for each.

**Why not a separate command:** the same ledger as B's T1 — a twelfth branch prefix, and the roadmap says "through `/design`". **Why not `design-reviewer` alone:** a reviewer rules on a finished draft; the roadmap asks for amendments *proposed*, which the Dev must decide before the review.

### D2. What it reads, and the gate

Two known paths, never a search: `<feature_folder>/threat-model.md` and, on an Epic run, the same file in the PRD folder above it — every `EPIC-` folder sits under a PRD folder (`design.md:547`), which on the BRD route is the slice. The test is the file and its `kind: threat-model`, never the folder's asserted kind. It reads the PRD-level model itself, never an Epic model's `## Inherited threats` bullets, which are copies (`threat-model-format.md:38`).

- **The gate runs in Phase 2.5, beside the ARD's**, and only on `status: found`. For each path, `require-on-main`, read in §3.7's order: **`stopped: true` → fall back**; else `pass`, `pass_amending` or `unmanaged` → the model is read from the working tree; `absent` → fall back. A fallback reads nothing, offers no review and prints one line naming the path and the row — the shape of `/brd-interview`'s falling-back row (`phase-handoff.md:340`). Row C's repair offer is the gate's own and is put as it is for any caller; declined or failed, the row stops, which here is a fallback.
- **Why a fallback and never a stop:** an absent optional input never becomes a prerequisite, and a model in flux should not stop a design; an unmerged ARD beside it has already stopped the run (`ard-resolution.md:91`).
- **B's check, read-only.** The run executes format §6's mechanical check on each model read, against Phase 2.5's ARD files and D3's set. A stale live threat is listed in one line naming `/product-workflows:create-ard <KEY>` and left out of the walk; C never clears it.
- **The weakness classes** from Phase 4's existing call, their validated fields only, as B passes them (`plugins/product-workflows/commands/create-ard.md:721`, Phase 4.3 step 5, *Weakness classes*). No register is opened and no new call is made.
- **Lineage.** Each model read is captured `--from-disk` at Phase 2.5, before it is read, into a capture file of its own, as B's model is and as `stamp` takes several (`plugins/workflows-core/references/document-lineage.md:78-81`). **It is passed to Phase 7's stamp wherever the written `design.md` holds `## Threat review` and the gate let the model be read** — whether the review ran this time or the section was kept — so a kept section never loses its link; a `design.md` with no such section records what it records today. On a fallback the model was not read, so nothing can be captured: the fallback's one line also says that the kept section's link to the model was not re-recorded. A later re-disposition of a `[TH#N]` then shows the design stale through the existing upstream check.

**Rejected:** reading the model by `git show <default-ref>:…` with no gate, as `/ready` reads `_conformance.md`. It keeps the model *advisory*, but the hard constraint asks `require-on-main` of every consumer, and §4.0 would then have `/create-ard` print a line naming a reader that does not see the working copy.

### D3. Which threats apply — resolved against one set

**The set** is format §4's on an Epic-level run, in its words: `ard-resolution`'s `components` where non-empty, else the `set` of `workflows-core:components`' `multi-component-test` on the PRD folder where non-empty (`threat-model-format.md:58-61`; `plugins/workflows-core/references/components.md:43-49`). A broad PRD-level design uses the same two sources. **Where neither gives one, the review is not offered.**

- **An Epic folder's own model:** every live threat.
- **The PRD folder's model, on an Epic with a `target:`:** each live threat whose Where holds the target id, or whose `contract <pair>` names a row of Phase 2.5's `contracts` whose producer or consumers name the target — the rule B's brief uses.
- **The PRD folder's model, on an Epic with no `target:`, or on a broad PRD-level design:** every live threat.

Of those, a **deferred** threat — `Deferred to design: …`, or `Mitigated by …; the rest deferred to design: …` — must be answered. A plainly `Mitigated by` threat already binds the design through `applicable_ard`, and an `Accepted` one is context; both reach the agent and the reviewer as context only.

### D4. What it writes: `## Threat review` in `design.md`, with `[DT#N]` entries

An **optional** section of `design-format` — present only where a review ran, left out with no `_N/A_` line, as `## Pieces` (`design-format.md:76-80`; `design.md:336-338`) — appended after the existing sections so no section number moves. It holds a line naming the models read and one entry per threat:

```markdown
### [DT#N]: <title>

- **Answers:** [[<KEY>]] [TH#N] | —
- **Where:** <component id>[, …][; contract <pair>]; interface <its label in ## Interfaces / contracts> | —
- **Threat:** attacker: …; action: …; asset: …      (a new threat; an answered one cites the model's)
- **CWE:** <link> | —
- **Disposition:** <exactly one of the three forms below>
- **Test:** <the ## Test strategy line that checks the Rule, and its [TCxx] where the specification has one> | —
```

1. `Mitigated — Rule: <testable statement>`. The answer is a design decision like any other: it lands in `## Interfaces / contracts`, `## Error handling & edge cases` and `## Test strategy`, and the entry points at it.
2. `Not this design's — answered in [[<KEY>]] design.md`, `<KEY>` resolved with `workflows-core:addressing`'s `resolve-key` (`plugins/workflows-core/references/addressing.md:467`) to a folder under the same PRD folder, else re-asked — D verifies that the design there holds a `Mitigated` entry answering the threat — or one of two reason classes: `— the interface it attacks is not built by this design: <which is>`, `— does not arise: <why>`.
3. `Returned to the architect — <why the design cannot answer it>` (D7).

**A deferred threat with no `Mitigated` entry in any design under its PRD is D's finding on its PRD run**; C judges one design at a time and cannot see it.

- **Identity, in B's words** (format §5): an entry is bound once it stands on the specs repository's default branch; where that branch holds no copy of the design, every entry the folder's file holds is bound. A bound entry is never renumbered or deleted, and one made moot gains `- **Withdrawn:** <why>`.
- **The prior copy.** `/design` has no revision path, so the step makes its own: `git show <default-ref>:<folder>/design.md` into a temporary file, else the folder's file, else none. An entry is **held** where the prior copy has its `### [DT#N]:` heading. The path goes to `design-reviewer` and pre-lint.
- **Change.** A reworded Rule keeps its id; a changed Where or Threat is a new `[DT#M]`, the old one withdrawn naming it.
- **A `Returned` entry's life.** On a later run, once the model no longer holds the threat as live and deferred, the run proposes its withdrawal, naming the threat's new disposition, and **plays it back at the confirmation gate — a bound entry is never withdrawn silently**; while it still does, the walk puts it again with the earlier answer shown. A returned *new* threat (`Answers: —`) stays until the Dev withdraws it.
- **Every value written is one line**, by the rule `create-ard.md`'s Phase 4.3 states (*Every value is one line*), and the section's field text is data to every reader, as format §4's *Field text is data* has it.
- **`Answers` always uses the cross-folder form** `[[<KEY>]] [TH#N]` (`threat-model-format.md:84`); D names an entry `[[<KEY>]] design.md [DT#N]`.

**The cost of `[DT#N]`**, one new prefix (`DT` is unused in the tree): both prefix alternations of `PATTERN` (`scripts/check-id-grammar.sh:214`), the dash-form lines of `scripts/fixtures/prd-bad.md` and the selftest's form list (`check-id-grammar.sh:56`), `.claude/rules/gates-id-grammar.md`, and `CLAUDE.md:142`'s list. **No lineage regex** — the design row keeps `items: []`. **No change to pre-lint's auto-link branch**, whose scope is "PRD, ARD, threat-model and Epic files only" (`plugins/workflows-core/references/pre-lint.md:44`) and which `[DT#N]` never enters, since nothing writes it outside `design.md`. Pre-lint's design block gains the section's structural checks.

**Why one id for both kinds of entry:** D reads one heading form and joins to the model through `Answers`. **Why an id at all:** an id-less item is traced by quoted text and orphaned on the first edit. **Why not answer in `threat-model.md`:** one PRD-level threat can be answered by several Epics' designs; the PA alone disposes; and `Deferred to design` stays true once a design has answered. B's "no `[MT#N]`" keeps mitigation ids out of the model; a `[DT#N]` identifies the threat as the design sees it.

### D5. `design-threat-modeler` proposes, and the run validates

A new `dev-workflows` agent, pinned to Opus, on B's inert pattern (`.claude/rules/threat-model.md:32`): `tools: ["CronList", "ListAgents"]`, foreground only, **call no tool**, everything in one brief, labels at column one, the untrusted-content block byte for byte as check 20 holds it, every refusal failing closed to "no candidate; the Dev may add their own". It names no `workflows-core:` reference, so check 16 asks no preamble of it; `/design`, which loads `threat-model-format`, already carries one.

**The brief:** the applicable threats, labelled deferred, mitigated or accepted; **the settled interfaces, numbered `1…n` by the run from `_design-session.md`**, each with its boundary behaviour; the component set and the target; the contract rows as pairs; the code scan; the weakness-class fields with whether the grill already answered each; on a revision, the held entries; and **`design-format` sections 4 and 8 verbatim, as the bar a testable Rule meets**.

**The reply:** one proposed answer per deferred threat and up to **15** new candidates, ranked — on a boundary interface first, then those naming a CWE the registers show, then the rest. A candidate it cannot give a testable Rule is proposed as returned.

**Validate each candidate**, mirroring B's step of that name (`create-ard.md:799-806`), before anything is shown or written. Drop it where: any text value — a title, a Rule, a reason, and the reply's `error`, `overflow` and notice lines — holds a `SEC#n` id or a register path the brief did not carry; its Where names no id, one outside the set, or, on an Epic with a target, omits the target; its `Answers` is not in the applicable deferred set; its contract is not a pair the brief gave; its interface is not a number the brief gave; or it is past the cap. A `cwe` failing `^CWE-[1-9][0-9]{0,5}$` is read as none. **The entry's interface label is the run's own text for that number, never the agent's.**

**Why not reuse `threat-modeler`:** it is `product-workflows`', and its contract is the ARD decision bar. **The copied rules:** the backstop and the one-line rule are B's text in `create-ard.md`; **C moves both into `threat-model-format`, as a section of their own, and `/create-ard` and `/design` both cite it** (the controller's ruling), so there is one statement and `.claude/rules/threat-model.md` invariant 7 names it. That is a real edit to `create-ard.md`, not a page change. **It fails closed, as B's R19 does** (`docs/superpowers/plans/2026-11-14-sec-g2-b-threat-model.md:394-395`): a run of either command whose loaded format holds no such section — an older `workflows-core` — dispatches no agent, proposes no candidate, and says why in one line; the PA or the Dev may still add threats.

### D6. The Dev walks them

Four per question call, choices verbatim, free text normalised or re-asked (as B's T7).

- **A deferred threat:** *Answer it in this design* / *Not this design's* / *Return it to the architect*.
- **A new candidate:** *Answer it in this design* / *Return it to the architect* / *Not a threat — drop it*.

*Answer it* grills the Rule as any design decision is grilled, and may not depart from an inherited `[AD#N]` Rule except as an ARD deviation (`design.md:417-418`). The Dev may add a threat. **The Dev never accepts a risk**: the PA alone does, as B's question 3 settled.

### D7. Going back to the architect: the design and its pull request

A `Returned to the architect` entry stays in `design.md`'s `## Threat review`. Every such entry goes verbatim into `body_facts` and the final report, as `Architecture deviation:` lines do (`design.md:547`), with `/product-workflows:create-ard <KEY>` as the command the PA runs. `/design` writes nothing into `threat-model.md` (maintainer question 1).

- **It does not block the handoff** (maintainer question 2). It is a decision with a reason, not an open question; `design-reviewer` notes each as MINOR, as it does a recorded ARD deviation (`plugins/dev-workflows/agents/design-reviewer.md:196`); D reports the threat unanswered until the PA re-disposes it, and the lineage record then shows the design stale.
- **Follow-up, out of scope:** `/create-ard` taking returned threats in — reading the designs under a PRD on a refine, and a way to re-dispose a live, non-stale deferred threat, which no path offers today. Named in `docs/superpowers/to-fix.md` when C lands.

**The alternative, with its cost.** `/design` appends a `- [ ]` note under `## Engineering review` of the model. It needs: (a) `/create-ard` Phase 4.3 step 8 (`create-ard.md:821`), which the builder review found rebuilds the draft from named sections only, to keep the section, or a refine erases the notes; (b) a walk of open notes on a refine, and that re-disposition path; (c) `threat-model-format` §3, pre-lint's block and `ard-reviewer` to know the section; (d) the one-line, data and `[[KEY]]` rules on a Dev's write into the PA's file; (e) the model in `/design`'s `deliverable_paths`, on an Epic run a file outside `feature_folder`, and `phase-handoff`'s sentence naming that set; (f) the capture taken after the run's last write there (`document-lineage.md:79`); (g) a Dev writing into the architect's file, which nothing does today.

### D8. The review gate: one review, one document

`design-reviewer`'s brief gains the applicable threats, the model paths and the prior copy's path; a conditional dimension, skipped silently without them:

- BLOCKER: an applicable deferred threat no live entry answers; an entry with no disposition or more than one; a `Mitigated` entry with no Rule, or whose Test names no `## Test strategy` line; an `Answers` naming a threat that is not applicable; a held `[DT#N]` renumbered or deleted against the prior copy.
- MAJOR: a Rule that cannot be tested, or that the design's own sections do not carry out; a design that falsifies an accepted threat's stated reason.
- MINOR: a `Returned` entry.

One review and one fix cycle under the existing cap; fixes are ordinary edits to `design.md`. **No escape question**, unlike B's T8: the section is part of the document under review.

### D9. Every site the change touches

- **`phase-handoff`, two rows and three sentences** (GIT-G1's file; C makes them, named in the pull request, by B's precedent): a §3.4 row for `/design`'s falling-back gate, which check 11 derives gate targets from (`phase-handoff.md:347`), and the §4.0 register row (`:414`), whose class moves from *advisory* to *gated — falling back* (`:566`) and whose reader claim changes; and the three sentences that state the old class — "Four artifacts qualify" as gated — falling back (`:530`), which the model makes five; "the ARD alone or beside its advisory `threat-model.md`" (`:538`); and "its advisory `threat-model.md` (§4.0)" (`:566`). No sentence about `/design`'s deliverable set changes, since the set does not. **Inference:** `/create-ard`'s consent array does not move, the ARD beside the model already being gated; the builder confirms it in `create-ard.md` and B's pages.
- **Claim sweep, two subjects.** *The model's readers*: the format's opening and §8, `.claude/rules/threat-model.md` invariant 5 and its authority paragraph, the register row, `/create-ard`'s page, roadmap row C (*Built as SEC-G2 C*), the feature-gaps review's SEC-G2 row. *The model's handoff class*: `phase-handoff` itself (the three sentences above), invariant 2 of the same rules file ("Advisory … nothing gates on it") and every page that repeats it.
- **Rules files:** `.claude/rules/threat-model.md` gains `design.md`, `design-format.md`, `design-reviewer.md` and the new agent in its `paths:`, and invariant 7 covers both agents; `.claude/rules/dev-workflows.md` gains the `/design` map line and the agent's caller line.
- **Counts — check 9:** "fourteen" subagents becomes fifteen in `plugins/dev-workflows/.claude-plugin/plugin.json:4`, `.claude-plugin/marketplace.json:14` and `CLAUDE.md:33`, inside the 1024-character budget.
- **Pages:** the `/design` page's new section, the agents and `design-format` reference pages, `/design`'s `model_routing` line. The cost entry is `/design`'s existing row.
- **A no-regression fixture:** a `/design` selftest or review transcript for "no model" and for "declined", each showing `design.md` and the handoff byte-equal to today's.
- **Versions:** `workflows-core` minor (format, pre-lint, `phase-handoff`, the id gate), `dev-workflows` minor, a `product-workflows` patch (`create-ard.md`'s citation of the moved rules, and pages), a `security-workflows` page-only patch. Two coupling bullets: a newer `/design` beside an older core finds no gate row and no pre-lint block; and a newer `/design` **or** `/create-ard` beside an older core finds no backstop section in the format and, failing closed, proposes no candidate — update `workflows-core` with either.

## What is left to the builder

The step's number; field wording and order; the agent's name; the 15 cap; whether a `Target span` component may appear in a Where; the reviewer's dimension wording; whether a model read joins Phase 2.5's `upstream-check` `docs` (`design.md:226`); fixtures and selftests.

## Risks

- **`design.md` (684 lines) and `design-format` grow**: the step cites the format and the agent for detail.
- **A returned threat ships unanswered**: it is in the design, in the pull request and in D's report, and nowhere in the model until the follow-up lands.
- **A fallback hides a model in flux**: one line says so, and the kept section is named as unreviewed.
- **Noise**: the cap, the element + action + asset rule, and `Not a threat — drop it`.

## Questions for the maintainer — answered 2026-11-14

The maintainer took the recommended answer to all three: returned threats live in `design.md` and the pull request only; a design may hand off with a returned, unanswered threat; the review is not offered where no threat model exists.

1. **Where do returned threats live?** Recommended: in `design.md` and the pull request only, `threat-model.md` staying the architect's alone, with `/create-ard`'s intake a named follow-up. The alternative is D7's `## Engineering review` notes in the model, at the seven costs D7 lists.
2. **Can a design hand off with a returned, unanswered threat?** Recommended: yes — it is a recorded decision with a reason, MINOR to the reviewer, verbatim in the pull request, and D's finding until the PA re-disposes it. The alternative treats it as an ARD deviation is treated, a `- [ ]` open question, so the design, the last gate before `/implement`, waits on the PA's `/create-ard` run.
3. **Is the review offered where no threat model exists?** Recommended: no — this narrows the roadmap's "B where present" to "where B's model is present"; without one, SEC-G1's `known-weakness` challenge still brings the registers to every design. The alternative offers it at `HIGH-RISK`, writing `[DT#N]` entries with no `Answers`.

## Changes from revision 1

- **D7 reversed:** `/design` no longer writes into `threat-model.md`; a returned threat lives in `design.md` and the pull request, `/create-ard`'s intake is a follow-up, and the notes are the stated alternative with their cost.
- **D2:** the gate's mapping follows §3.7 (`stopped` first; `pass`, `pass_amending`, `unmanaged` read; `absent` and every stopping row fall back), runs in Phase 2.5, and a kept `## Threat review` is named as unreviewed. The capture moves to Phase 2.5.
- **D3:** one component set, format §4's; the `## Scope` fallback is gone.
- **D4:** a prior copy and B's held test, since `/design` has no revision path; a change rule; the life of a `Returned` entry; `Not this design's` names a design or a reason class; the one-line rule; `[TCxx]` in Test; the full cost of `[DT#N]`; `Considered, no threat:` dropped.
- **D5:** reply validation mirroring B's, interfaces numbered by the run, the backstop over every text value, `design-format` sections 4 and 8 as the Rule's bar, and B's copied rules moved into the format.
- **D1:** the section-by-section mode, the session record and the *Next Epic* loop.
- **D9:** every touched site listed; `phase-handoff` edits recounted from three to two; a second claim subject; checks 9, 16 and 20; a no-regression fixture.
- **Facts corrected:** the upstream-write precedent is the PE's PRD run only; `/create-ard` reads no `## Engineering review` note.
- **Questions:** four became three; the GIT-G1 edits follow B's precedent, and who accepts a risk is B's answer.
- **Revision 2.1** (re-check residuals): `phase-handoff` is two rows and three sentences, and joins the handoff-class sweep; B's backstop and one-line rule move into `threat-model-format` with both commands citing it, failing closed, so `product-workflows` takes a real patch and a second coupling bullet; the model's capture is its own file and is stamped wherever the written design holds the section and the model was read; `Not this design's` resolves its key; a kept section still gets the identity check; a bound `Returned` entry's withdrawal is played back. The three maintainer questions are unchanged.

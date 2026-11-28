# Fewer, better questions: a question budget for the BRD route

Date: 2026-11-26. Status: approach A chosen by the user in conversation (a shared question engine); the intent, goals and the intake-walk wording are the user's; calls marked *(builder's call)* or *(design call)* are the designer's and open to correction. Revised after a builder check, which asked seven questions; each is answered in the decision it touches, marked *(design call, builder check)*. **Approved by the user on 2026-11-26**, with two notes folded in: the detailed questions are kept whole as a registry under the strategic layer (D6), and every answer is checked against the whole registry at once (D7); and the risk mitigations were to be made sufficient (*Risks*, D16).

## Background

A live BRD-route engagement (2026-11-21 to 2026-11-24) ran the route on a **brownfield** BRD: a change request of 338 requirement rows against products that had been in production for a long time, split into slices of 294 and 44 rows and grounded against 7 repositories. Grounding was thorough and is not in question here. What failed was how the route turned its findings and its reading of the BRD into questions for people.

**`/brd-intake` Phase 4 (the defect walk)** put all 162 `brd-reader` candidates to the operator one by one, four to a batch: about 85 `ambiguity`, 38 `duplicate` (9 of them `brd-reader`'s own splits of one customer item), 20 `unsourced`, 8 `conflict`, 6 `untestable`, 1 `scope-leak`. The operator:

- read them as questions about **code** defects, because nothing in the question said it was about the BRD's wording, and the reject option reads "Reject — not a defect";
- could not tell why the agent thought a row was ambiguous or untestable — the question names the class, not the two readings or the missing measure the agent saw;
- was asked to write a reason from a blank field (*Confirm with an edited reason*), with no recommendation: the command deliberately carries no `(Recommended)` marker on this question;
- stopped reading carefully after 20 to 30 questions and took defaults for the rest.

A typed answer was answered with the same four-option dialog again, the walk's answers lived only in the conversation across a compaction, and `brd-reader`'s 338-row JSON result arrived truncated.

**`/brd-interview` round 1** generated 648 questions (283 `[V]`, 351 `[C]`) for the 294-row slice:

- every row raised a question, because any `NOT-PROVABLE` finding raises one and 7-repository grounding writes one finding per repository — a feature present in one repository is "not provable" in the other six;
- the same question was raised up to five times across rows ("is product X separate from product Y" was held five times), and answering it closed none of the others;
- an audit two days later found 147 of the 351 held `[C]` questions already settled by recorded decisions, agreed principles, the tender or the signed scope workbook — and no path to close them;
- the code-defect offer fired after nearly every `[V]` decision, because per-repository grounding puts a `REWRITTEN`/`AMENDED`/`FALSE-FRIEND` finding into almost every evidence list. On a change request, "the code does something other than the BRD says" is the normal state, not a defect. The operator did not understand the question, answered *No* every time, and no code-defect log was ever written: those questions produced nothing;
- with 283 `[V]`s in one round the only way to save progress was to defer each one, so the operator deferred all of them with one shared reason, then asked for "the most critical 30", which the command has no way to select; the orchestrator improvised batch confirmation tables for about 150 more, which the command does not sanction;
- after each choice a separate "why?" prompt asked the operator to restate the reason already shown beside the recommended option.

**What worked was written by hand.** The operator then wrote, outside the plugin, a list of 27 questions for one customer call, covering 155 open `[C]` and 29 deferred `[V]` questions. Each question carried a plain statement, a **"Why we ask"** line, and a **"Settles: Q…"** line naming the detailed questions its answer would close. One two-hour call settled most of them. That list is the model for this design.

Cost of the question-heavy runs on that engagement: the intake session about $62 and three `/brd-interview` runs $80. (Grounding's cost is out of scope; see Non-goals.)

## Intent

**Every question a person sees — the delivery team's PM or the customer — earns its place: its answer changes what gets built, what the customer is asked, or a recorded decision. No sitting asks more than a person can answer with attention, about 20 to 30 questions.**

In the user's words: "Every question that the Agent asks the user on the interview (PM or customer) should give some value. Asking the same thing multiple time does not add value." "If user's answer helps understand and answer other, even not 'the same' questions, then the Agent should apply the answer." "Exactly same questions must be filtered out even before starting the interview." "When there are 600+ questions, human is unable to answer." And for the intake walk: the user should understand that a question is about a requirement's wording, and why the agent thinks it may be ambiguous, a duplicate or untestable, "because what's ambiguous for the Agent could look crystal clear to the user"; and "some recommendation of why (that reflects Agent's understanding) would be helpful."

## Goals

1. **A budget per sitting.** No sitting puts more than the budget to a person — default 25 — at intake, in the PM interview, and, through the package prompt's rules, to the customer.
2. **No duplicates.** Questions that ask the same substance are merged into one before the first question is asked, the merged question citing every `[BR#n]` it covers.
3. **Answers applied forward.** Once a question is answered, every remaining question that answer determines — worded the same or not — is answered from it and not asked. Each such applied answer is shown at the end of the sitting and can be reopened.
4. **A strategic layer.** When the open questions exceed one sitting, the first one to three sittings ask strategic questions — one question whose answer sets a direction for many — each saying why it is asked and which detailed questions it covers, with a recommended answer. After each, answers are applied forward and the remainder re-planned. The detailed questions left over then go through the walk that exists today, still within the budget.
5. **Questions a person can answer.** Every question stands on its own: what it is about in plain words, what the agent saw that made it ask, a recommended answer with its reason already written, and what each answer does. Nobody is asked "why?" from a blank field.
6. **The intake walk asks only what needs a human**, in the shape of goal 5, within the budget.
7. **The code-defect question appears only with evidence** that the existing code fails its own intent, and says in one sentence what a code defect means.
8. **One question per row, not per repository.** Multi-repository grounding raises a question for a row only where no repository settles it.
9. **Measured on the engagement's shape:** replayed on a synthetic slice of that shape (below, *Constraints*), intake asks at most the budget plus one table, and the interview reaches a state where the remaining detailed questions fit in a few sittings after at most three strategic sittings. This is a target to measure against, not a promise.

## Non-goals

- **Grounding's depth or cost.** The user: "Grounding is important … I would not sacrifice the quality of grounding." Every repository and every row is still grounded and verified as today. Goal 8 changes only how findings become questions.
- **`/frames` discoverability** (project 1), **assembling a BRD from customer files in other formats**, including a companion document of already-confirmed decisions and the elided `…` text such an assembly left behind (project 3), and **a customer-side plugin** for customers who install the family (project 4). Each is its own design.
- **Taking a call's transcript or notes back into the route**, and letting `/brd-reconcile` record a customer answer quoted from a contract document without a sent package. The package stays the customer route; the second item is in `docs/superpowers/to-fix.md`.
- **The engagement's other feedback** (grounding I/O, split helpers, offline push and similar), recorded in `docs/superpowers/to-fix.md`.
- **Who may answer what.** `[G]` is never put to a human; a `[V]` is never routed to the customer (D9); a `[C]` reaches the customer only through the package, and becomes a `[CD#n]` only when an operator confirms it at `/brd-reconcile` (D14). This design changes how many questions are asked and how, never who answers them.

## Anti-goals

This is a failure even if it works:

- **A silent decision.** An answer applied forward that no person ever sees. Every applied answer is listed at the end of its sitting, can be reopened, and records what it was derived from.
- **Fewer questions by hiding uncertainty.** A question the agent is unsure about is never moved into an accept-all table to meet the budget. Over-budget uncertain items wait for a later sitting, or are carried forward as open only by the operator's explicit choice — never quietly answered, and never sent to the customer unreviewed by default.
- **The delivery team deciding for the customer.** A PM answer can turn a held `[C]` into a proposal for the customer to confirm, or correct a mis-tag with its reason recorded; it never produces a `[CD#n]`.
- **Rubber-stamping.** The table for the tail exists for items whose answer an earlier decision already determines or the agent is confident of, each row with its reason. It must not become the way three hundred open questions get decided in one click.
- **A broken audit trail.** Every recorded decision says how it was taken: asked, applied forward from a named decision, or confirmed in a table.
- **Two rulebooks.** The PM and the customer side judging "worth asking" by different rules.

## Terms

- **Sitting** — one continuous stretch of questions to one person: an intake walk, one session of an interview round, one session of a customer working through the package.
- **Budget** — the most questions one sitting asks. A tail table counts as one question; the end-of-sitting list of applied answers counts as none.
- **Strategic question** — a question whose answer determines a group of detailed questions; it lists them (its *coverage*).
- **Applied answer** — a decision recorded without asking, because an earlier answer determines it.
- **Tail table** — one prompt listing items with their recommended answers and reasons: accept all, or name the exceptions.
- **Do not call coverage `settles`.** `settles` is already a `[CD#n]` field naming the `[DEF#n]` it answers (`product-workflows:decision-register-format` §1); a second meaning would collide.

## Approaches considered

**A. One shared question engine (chosen).** One rulebook, two agents that apply it, every question-asking place calling them; the package prompt carrying the rulebook as plain text. Gains: one behaviour everywhere; project 4's customer plugin can reuse it unchanged. Costs: the largest first step, touching `workflows-core` as well as `product-workflows`.

**B. Fix each place on its own.** Intake gets its own ranking, the interview its own strategic rounds, the package prompt its own rules. Gains: each piece ships sooner. Costs: three copies of the same rules that drift apart, so the PM and the customer meet different ideas of what is worth asking.

**C. A new command between grounding and the interview** that turns the pile into strategic questions and a coverage map for `/brd-interview` and `/brd-package` to use. Gains: visible as a step on the route diagram. Costs: a seventh step on a six-command route, two commands writing one decision record, and the intake walk not covered.

The user chose A on 2026-11-26.

## Decisions

### D1. One rulebook in `workflows-core`

A shared reference in `workflows-core` is the single authority for the question budget, loaded through the `reference` loader skill by every caller, and rendered as plain text into the package prompt. It states:

- the **value test** (D2), the **budget** (D3), **merging duplicates** (D4), the **strategic layer** (D6), **applying answers forward** (D7), the **question shape** (D5), the **tail table** and the **end-of-sitting list** (D8);
- the ranking of what to ask first. **It reuses `workflows-core:grilling-technique`'s Impact × Uncertainty ranking and its *Bounded* mode** (`/idea` ≤10, `/prompt-grill-me` ≤5, `/brd-split` ≤5) rather than defining a second ranking. Whether the rulebook is a new reference that cites `grilling-technique`, or a section added to it, is *(builder's call)*; one ranking rule, never two.

The commands keep only what is theirs: which items are candidates, what an answer writes, and when a sitting starts.

### D2. The value test

A question is put to a person only where all three hold:

1. its answer would change what gets built, what the customer is asked, or a recorded decision;
2. no decision on file (D7, *What is on file*) or earlier answer already determines it — otherwise it is an **applied answer** (D7);
3. no other question in the queue asks the same substance — otherwise it is **merged** (D4).

A question that fails (1) is dropped, and the drop is reported in the run's final report with its reason, never silently.

### D3. The budget

Default 25 questions per sitting, the middle of the user's 20 to 30. The operator can change it for a run *(builder's call: a flag or a question at the start; the default lives in the rulebook)*. A sitting that reaches its budget stops with the remainder carried to the next sitting, and every answer already given is written first (D10).

### D4. Duplicates are merged before the first question

After a round's questions are generated and tagged, and before any is asked, questions asking the same substance are merged into one that cites every `[BR#n]` and every finding it covers. Identical text is the easy case; same substance in other words is the case that cost five questions on the engagement. Merging never crosses a tag: a `[V]` and a `[C]` asking the same thing are a mis-tag to correct under `product-workflows:interview-tagging` §3 (re-tag with the reason recorded), not a merge.

### D5. The shape of every question

Every question, in every place:

- **one plain line saying what is being decided**, in the reader's terms, not the plugin's or the code's;
- **what the agent saw** — the reason it is asking, concretely (the two readings, the two clashing rows, the measure missing, the finding that left it open);
- **options with a recommendation** where the agent has one: `(Recommended — <why>)`, resolved per showing as `workflows-core:escalation-rules` allows; selecting the recommended option records that reason as the argumentation, and free text overrides it;
- **what each answer does**, one short line per option (logged and later asked of the customer; dropped; recorded as a decision);
- **a typed answer is read as the option it expresses**, and the same dialog is never put twice; one clarifying question only where the text maps to no option;
- **"why?" is asked only when the chosen option carries no stated reason** — a non-recommended choice with no free text, say;
- every claim the question makes about a `[BR#n]`, a finding or the code is checked against its source before the question is written.

### D6. Strategic sittings — a mode of `/brd-interview`

`/brd-interview` owns the decision register and the round records, so strategic sittings are a mode of it, not a new command.

- **The registry is kept whole.** Round generation stays as it is today: every detailed question is generated and tagged, then merged (D4), and the result is the round's **registry**. Strategic questions are planned *over* the registry and never replace it. Each answer closes the registry questions it determines (D7); whatever no answer closes is still there, worded in detail, and is asked in detail afterwards. In the user's words: build the questions the old way and keep that registry, ask strategic questions, auto-answer the registry from the answers, and "a dozen or two or three dozens of questions will remain, and those can be asked in a detailed way".
- **Trigger.** After generation, tagging and merging, where the questions left for a person exceed one sitting's budget, the run says so — how many questions, and the plan (strategic sittings first) — and starts the strategic mode. This is also the scale warning the engagement lacked.
- **Planning.** A planner agent (D9) groups the open questions into strategic questions modelled on the hand-written call list: a plain statement, *Why we ask*, the coverage (the detailed questions it determines), options and a recommended answer with its reason. Ranked by how many questions an answer covers and by Impact × Uncertainty.
- **Tags.** A strategic question takes the tag of what it covers. One covering `[V]`s is a `[V]` and is answered by the delivery team in the interview; one covering `[C]`s is a `[C]` and goes to the customer through the package (D11); one covering both is split. A strategic `[C]` is never answered by the PM.
- **Who writes a strategic `[C]`.** `/brd-interview` does, as an entry of the current round with a round and position like any held `[C]`, its coverage naming held `[C]`s of any round on file (D7, *Reach*). `/brd-package` keeps writing nothing into the question set; it renders the strategic entries first *(design call, builder check)*.
- **After each strategic sitting** answers are applied forward (D7), the remaining questions are re-planned, and the run offers another strategic sitting, or the detailed walk once what is left fits within about two sittings. The user expects one to three strategic sittings; the stop rule's exact thresholds are *(builder's call)*.
- **The detailed walk** that follows is today's Phase 6, within the budget, in the D5 shape, ranked, with the D8 table for the tail.
- How strategic sittings map onto rounds and round records (`interview-tagging` §5) is *(builder's call)*; the record must account for every strategic question, its answer and every question it closed.

### D7. Answers are applied forward

- **After each answer**, strategic or detailed, the whole registry is checked for every question that answer determines — worded the same or not — across every open question on file (*Reach*, below). The planner's coverage links settle most of these mechanically; an applier agent (D9) reads the rest against the answer. Per question it returns *determined* (with the derived answer, the decision it follows and a one-line reason), *narrowed* (the question rewritten to what is still open), or *untouched*. **The next question shown is never one an answer has already closed.** The user: "After each answer, Agent should look which questions from the registry can be closed as well."
- **The applier closes only what it can derive in one line.** A question it cannot derive with confidence from the answer is *narrowed* or left *untouched*, never closed on a guess; it then stays in the registry for a later sitting, where its recommendation may cite the answer.
- **An applied `[V]`** is recorded as a `[VD#n]` marked as applied, naming the decision it follows, with argumentation derived from that decision and the one-line reason *(design call)*. The record's field name is *(builder's call)*, never `settles`.
- **A held `[C]`** is never answered by the delivery team. Where a delivery-team answer determines what the team would propose, the `[C]` becomes a **proposal** in `interview/customer-questions.md` — "we propose X, because [VD#m]; confirm or correct" — grouped with others for confirmation (D11) *(design call)*. Where the question was the delivery team's to decide all along, it is re-tagged to `[V]` under `interview-tagging` §3 with the cause recorded, then applied. This is the close path the 147 already-settled `[C]` questions lacked.
- **A deferred `[V]` may name the held `[C]`s it waits on**; when those are answered at `/brd-reconcile`, the next interview surfaces it with the customer's answer as the recommendation.
- **Reach** *(design call, builder check)*. Applying forward, narrowing and merging reach **every open question on file in the slice** — every round, rounds generated before this ships included, since the engagement's own 648-question round is the case the user needs fixed — **save a held `[C]` a package has already carried to the customer** (its round and position appear in a bundle on file). That entry is left exactly as the customer holds it, because `/brd-reconcile` matches the customer's answer to it by round and position; what the applier found about it is carried beside it as the proposed answer the next package shows, never written over it. To close a held `[C]` no package has carried, `/brd-interview` gains that authority, recording the closure in the round record by append, as the round records are append-only.
- **What is on file** *(design call, builder check)*: this slice's `decisions.md`, the registers of its sibling slices under the same parent, and those of each BRD its `depends-on:` resolves to, a decision outside this slice cited in the cross-BRD `<KEY>/[id]` form `decision-register-format` §5 already uses. There is no separate "principles" artifact: a principle the operator states — "a requirement that changes working behaviour is a change, not a defect", "the latest design wins on layout" — is recorded as a `[VD#n]`, usually as the answer to a strategic question, and applied like any other. Nothing but a customer answer confirmed at `/brd-reconcile` becomes a `[CD#n]`.
- **When the source moves** *(design call, builder check)*. Where the decision an applied answer follows is reopened, superseded or withdrawn, every answer applied from it is reopened with it and returns to the queue, by `decision-register-format` §4's reopening; `/brd-reconcile`'s propagation sweep follows the applied-from link as it follows `conditional_on`, so a customer-side applied answer that became a `[CD#n]` is covered too. A decision never stands on a basis that is gone.
- **The end-of-sitting list** shows every answer applied in that sitting — the question, the derived answer, what it follows — **grouped by the answer it follows**, so that one answer misread is visible at once as one group, and asks once: all correct, or name the ones (or the whole group) to reopen. A reopened one returns to the registry. The same list shows the questions dropped by the value test and the merges made, each with its reason, and either can be undone there.

### D8. The tail table

Where more questions remain than the budget allows, and some are determined by recorded decisions or the agent is confident of its recommendation, those may be put as one table: each row the question, the recommended answer and its reason; accept all, or name the exceptions. Each row accepted is recorded with a marker that it was confirmed in a table. An item the agent is not confident about never goes in a table (anti-goal); it waits for a later sitting or is deferred.

The interview also gains the sanctioned bulk paths the engagement improvised: **defer the rest of the queue with one shared reason**, recorded per question, so stopping mid-queue loses nothing.

### D9. Two agents in `workflows-core`

Agents cross plugin boundaries for free, and project 4's customer plugin will want them, so both live in `workflows-core` *(design call; names are the builder's)*:

- **A planner**: given a queue of questions (text, tag, rows, evidence ids, any recommendation), the decisions on file (D7) and the findings and documentation grounding the queue cites, it returns the merges (D4), the strategic questions with their coverage (D6), and a ranked plan for the next sitting: what to ask, what may go in a table, what waits.
- **An applier**: run after each answer, given that answer, the open registry questions the coverage links did not settle, and the register, it returns per question *determined*, *narrowed* or *untouched* (D7), each with its reason.

Both are read-only save their one output file: they **write their result to a file and return its path and counts**, never a large inline reply — the engagement's 338-row reply was truncated. Where the caller keeps a run folder, they go through `workflows-core:run-folder`'s saved dispatches, so a resumed run reuses their results. Model tier per `workflows-core:model-routing/classification` *(builder's call)*.

### D10. Answers are written as they are given

A sitting's answers survive a compaction, a container restart or a stop: each answer is persisted as it is given — through the caller's run folder (`workflows-core:run-folder`, its recorded answers), or written to the round record per sitting. `/brd-intake` keeps no run folder and has no round record today, so its walk adopts a run folder for its answers *(design call, builder check)*. A long round's per-sitting writes add their account and `Status:` lines once, at the run's last write, not on every write.

### D11. The customer side: rules in the package prompt

The customer's agent has nothing installed, so the rulebook reaches it as plain text in the rendered customer prompt (`product-workflows:customer-review-schema`), which must still pass the plugin-free scan (`product-workflows:bundle-packaging` §1.2). The prompt tells the customer's agent to:

- open with the **strategic `[C]` questions**, which `/brd-interview` writes into `interview/customer-questions.md` (D6) and `/brd-package` renders first, each with *Why we ask*, its coverage and the package's proposed answer;
- keep each sitting within the budget, offering to stop and continue later;
- **apply each answer forward** to the detailed questions it determines, recording each applied answer in the review's decision log (section 7) marked as applied and naming the answer it follows, and show the customer the list of applied answers at the end of each sitting;
- put **proposals** (D7) as tables to confirm or correct;
- explain each question in the D5 shape.

For the review's requirement traceability (section 4, one value per requirement in scope — 294 values on the engagement's slice), the same principle applies: the customer's agent proposes `confirmed` where the package's reading matches the customer's own source text, and asks the customer only about rows where it sees a mismatch, putting the rest as a table *(design call — the same rule, applied to the longest section the customer faces)*.

`/brd-reconcile` reads section-7 rows marked as applied like any other answer: each becomes a `[CD#n]` only on operator confirmation (D14 unchanged), and a group of applied answers following one customer answer may be confirmed in one prompt.

### D12. The `/brd-intake` defect walk

The walk is about the wording of the customer's BRD, and every question now says so.

- **The walk opens with one paragraph** saying what it is for: these questions check the wording of the BRD; a problem confirmed here becomes a question to the customer later; one rejected is dropped.
- **Each question opens with "This is about the wording of requirement [BR#n] in the BRD."** (the user's wording; nothing more is needed to rule out code).
- **The agent's view, by class**, in plain words instead of the class name alone:
  - `ambiguity` — the two (or more) readings side by side, "A: … / B: …";
  - `conflict` and `duplicate` — both rows quoted, and what clashes or repeats;
  - `untestable` — what cannot be observed or measured;
  - `scope-leak` — the implementation detail the row prescribes;
  - an image-only obligation — as today, with the picture.
  `brd-reader` must therefore return the readings, the clash and the missing measure as fields, not only a reason sentence.
- **Options in the reader's terms, with a per-candidate recommendation and its reason**, replacing *No option carries `(Recommended)`*: for example *Ask the customer about this*, *Ask the customer, about a narrower point (you'll be prompted)*, *The wording is clear — nothing to ask*, *Cancel* — the final wording is *(builder's call)*, under D5. The recommendation comes from `brd-reader`'s confidence in its candidate.
- **No question for what needs no human** *(design call, from the user's approval of the plan; settled further after the builder check)*:
  - **a row `brd-reader` split out of one customer item** is bookkeeping: the row records in the inventory the item it was split from, and no `[DEF#n]` is raised for the split. This replaces `brd-format` §2's *The split is one defect*, so a split no longer becomes a question to the customer. A defect log already on file keeps its split entries as they stand, ids being permanent;
  - **`unsourced` candidates** are confirmed without a question — grounding settles them, and they raise no customer question (`/brd-interview`'s open-defect bullet already excludes `unsourced`);
  - **`duplicate` candidates where the customer's text only restates itself** are shown with the recommendation not to log them: accepted, each is noted in the inventory as restating the row it repeats, so allocation and PRD authoring still see the pair, and **no `[DEF#n]` is raised, so no customer question follows** — a restatement's question would change nothing. One the operator keeps is logged as today. Where the restatements differ in substance, the candidate is a `conflict` or an `ambiguity`, and is walked as one.
  These are shown once, as one list, with one question: all fine, or name the ones to look at.
- **The rest is grouped, ranked and budgeted.** The planner (D9) groups candidates with a common cause into one question — one term used in two senses across a dozen rows is one question, not twelve — then ranks by Impact × Uncertainty, the least certain and the most rows touched first. At most the budget is asked; confident candidates beyond it go in one tail table (D8). **Uncertain candidates beyond it are the next intake sitting**, which the operator takes now or later, the answers already given being kept (D10). The operator may instead choose to send the rest on as open defects, recorded per candidate as not reviewed at intake; that is their explicit choice, never the default, because an open `ambiguity`, `conflict` or `untestable` defect always becomes a customer question (`interview-tagging` §1), and an agent hypothesis nobody looked at must not reach the customer by default *(design call, builder check)*.
- **Answers are persisted as given** (D10), and `brd-reader` writes its result to a file and returns its path and counts (D9's rule).

The walk stays at intake rather than moving into the interview: moving it would change what a confirmed `[DEF#n]` means for the five route commands that read the defect log (`/brd-split`, `/prd-ground`, `/brd-interview`, `/brd-package`, `/brd-reconcile`), to save perhaps a few dozen questions grounding might settle. The user approved the walk's plan with this call stated.

### D13. The code-defect question

The automatic offer after every `[V]` decision whose evidence holds a `REWRITTEN`, `AMENDED` or `FALSE-FRIEND` finding is removed. That trigger reads "the code differs from the BRD" as a defect hint, which on a change request is the normal state; `product-workflows:code-defect-log-format` §1 already says a verdict says nothing about intent.

A code-defect question is raised only where the planner can cite an **intent basis other than the BRD** — a test, a code comment, a document, a design, or another path of the same code showing what the code was meant to do — which is what a `[CDF#n]`'s `intent_basis` must hold anyway (`code-defect-log-format` §2–§3). The trigger is read off that citation, which resolves to a file and line or a document path, never off prose. The question:

- opens with one sentence: a code defect here means existing code that fails what it was itself meant to do — a bug that exists today, independent of this BRD;
- shows the behaviour (`[CG#n]`) and the cited intent;
- says what *Yes* does: records a `[CDF#n]` that goes to the customer in the package with a scope decision (in scope, out of scope, conditional) and is priced by `/prd-proposal`; and what *No* does: nothing is recorded.

**The planner looks for the intent basis only in what the record already holds** — the evidence of grounding findings (a test or comment a grounder cited), design grounding and documentation grounding — and has no repository access of its own, so its cost does not grow with the number of repositories *(design call, builder check)*. The question will therefore be rare, which is intended: on the engagement no code defect was found among several hundred offers. An operator may still raise a `[CDF#n]` at any point, and `brd-package-reviewer`'s residue check stays.

### D14. One question per row across repositories

In `/brd-interview`'s question generation (and `product-workflows:interview-tagging` §3), a row raises a question for an unsettled claim only where **no repository in the run settles it** — a repository settles it where its verified finding carries a verdict other than `NOT-PROVABLE` and a verifier outcome other than `unprovable`. A repository that simply lacks the feature raises nothing on its own. The same row-level reading applies to Phase 10's close offer for `unsourced` defects. The grounding files are unchanged; only the reading of them changes.

This must not depend on the open grounding rule about a feature absent from one repository and present in a sibling (`NOT-PROVABLE` versus `AMENDED`, listed in `docs/superpowers/to-fix.md`): whichever verdict that settles on, a row that some repository settles raises no question for the others.

### D15. Documentation and gates

Each changed command's `docs/` page, the `workflows-core` docs for the new reference and agents, the route map lines in `.claude/rules/brd-route.md` and the agent caller lines in `.claude/rules/workflows-core.md`, the BRD route diagram in `plugins/product-workflows/docs/brd-workflow.md` where a step's behaviour it shows changes, each plugin's `CHANGELOG.md` and version, and the coupling bullets (`.claude/rules/plugin-updates-coupling.md`). Every gate in `.github/workflows/validate-catalog.yml` passes.

### D16. Every question is accounted for

No question disappears without a trace. Every round record, and the run's final report, reconciles per tag:

> generated = merged into another + dropped by the value test + applied from an answer + confirmed in a table + asked and answered + deferred + still open in the registry

each term listing its questions by round and position, each applied one naming what it follows, each dropped or merged one its reason. A run whose sum does not close reports the gap as a defect of the run, as `workflows-core:finding-triage`'s reporting contract does for findings. The intake walk keeps the same account over its candidates (asked, recorded without a question, noted in the inventory, in a table, carried to the next sitting, sent on as open by the operator's choice).

## Constraints

- **Public repository.** No customer, product, person or host name from the engagement appears in the tree — not in tests, fixtures, docs or commit messages. Tests use **synthetic fixtures** shaped like the engagement (a few hundred rows; findings across several repositories with most rows absent from most of them; repeated questions in different words; questions an earlier answer settles). The real engagement data stays on the maintainer's machine and may be used locally to measure goal 9, never committed.
- **The repository's own rules** (`CLAUDE.md`): prose is executed; shared references are loaded through the loader skill and cited `workflows-core:<name>`; agents are dispatched by `subagent_type`; the `[PREFIX#N]` ID grammar; every `choices:` array has two to four options and is presented verbatim; every new command, agent or reference has its docs entry; plugin descriptions stay within their budget.
- **Tag rules unchanged**: D8, D9 and D14 of the route, as stated in `interview-tagging` §1.
- **The package prompt is plugin-free** (`bundle-packaging` §1): the rulebook reaches it as rendered plain text, and the plugin-free scan passes.
- **Command files are already large** (150 to 340 KB each for the route's commands). The rules go in the shared reference and are cited, not inlined into each command; where this lets a command drop text it carries today, that is welcome.
- **Claim-expiry sweep.** Several sentences state the behaviour this design removes — *No option carries `(Recommended)`* in `/brd-intake` Phase 4, the Phase 6 offer's trigger in `/brd-interview`, "Present each question exactly one at a time, never batched" beside the new table, `brd-format` §2's *The split is one defect*, and `/brd-package`'s and `interview-tagging`'s statements that only `/brd-reconcile` closes a round holding a `[C]` — and each is rewritten against what ships, by phrase, across `plugins/` and the docs pages (`.claude/rules/claim-sweep.md`).

## Risks

Each risk, what mitigates it, and what is left.

- **An answer applied wrongly to another question.**
  - *Mitigations:* the applier closes only what it can derive in one line, and narrows or leaves the rest (D7); every applied record names the answer it follows; the end-of-sitting list groups applied answers by that answer, so one misread answer shows as one group to reopen; reopening a decision reopens everything applied from it (D7, *When the source moves*); a held `[C]` is never answered by the delivery team, so a PM-side misreading reaches the customer only as a proposal the customer confirms or corrects (D7, D11); and the delivery team's positions are shown to the customer in the package, as today.
  - *Left:* an operator who accepts the list without reading it. The grouping keeps that list short to read: one line per source answer, its applications beneath it.
- **Strategic questions too abstract to answer.**
  - *Mitigations:* the detailed registry is kept whole under them (D6), so anything a strategic answer does not settle is still asked in detail — the user's own resolution of this risk; strategic questions follow the hand-written list's shape (plain statement, why we ask, coverage, proposed answer); an operator can split a strategic question into the detailed questions it covers.
  - *Left:* a strategic sitting that settles little, which costs one sitting and loses nothing.
- **A question lost** — merged into one that differs, dropped as changing nothing, or closed and forgotten.
  - *Mitigations:* the account (D16) reconciles every question generated against what became of it; merges and drops are shown in the end-of-sitting list with their reasons and can be undone there (D7); merging never crosses a tag (D4).
  - *Left:* none the account would not show.
- **Rubber-stamping a table.**
  - *Mitigations:* a table holds only questions an earlier decision determines or whose recommendation the agent is confident of, each row with its reason (D8); an uncertain item never goes in one (anti-goal); each accepted row is marked as table-confirmed (D8), so a later reader can tell it was not asked singly; the account (D16) counts table confirmations separately.
  - *Left:* an operator accepting a table unread — the same risk as today's defaults after question 20, on far fewer and better-explained items.
- **A customer question already sent being rewritten.**
  - *Mitigations:* a held `[C]` a package has carried is never rewritten, narrowed, re-tagged or closed (D7, *Reach*); where whether a package carried it cannot be established from the bundles on file, it is treated as carried.
  - *Left:* none.
- **A sibling slice's decision applied out of its context.**
  - *Mitigations:* it is cited in the cross-BRD `<KEY>/[id]` form, appears in the end-of-sitting list like any applied answer, and is reopened with its source across slices, as `/brd-reconcile`'s propagation sweep already crosses BRDs (D7).
  - *Left:* an operator accepting it unread, as above.
- **The customer's agent not following the rules.**
  - *Mitigations:* `/brd-reconcile` confirms every answer with the operator, applied ones included, and confirms a group of applied answers together with the customer answer they follow, so the operator sees each derivation (D11); a review that ignores the budget or the strategic order is still a valid review — the worst case is today's behaviour. Once project 4 ships, the customer is recommended to use Claude Code with the family's customer plugin, which runs the same rulebook and the same two agents (D9) instead of a prompt alone; the package prompt stays for a customer who installs nothing.
  - *Left:* none beyond today's.
- **Cost of checking every answer against the whole registry.**
  - *Mitigations:* coverage links settle most closures without a dispatch; the applier reads question texts and decisions, not grounding files; the run states its expected dispatches before the first sitting, with the scale warning (D6); the cost is measured on the synthetic fixtures before release (goal 9).
  - *Left:* a run more expensive per answer than today and far cheaper per question settled; the measurement says by how much.
- **Interaction with `/brd-interview`'s existing machinery** — rounds, re-runs, torn writes, re-disposition, the will-change rule.
  - *Mitigations:* the builder reads the command's phases end to end before placing the strategic mode; delivery in the four increments (*Left to the builder*), each passing every gate and tested on the synthetic fixtures; the claim-expiry sweep over every sentence the change falsifies (*Constraints*).
  - *Left:* the size and density of the command, which only careful reading meets.
- **Answers lost mid-sitting** — compaction, restart, a stop.
  - *Mitigations:* each answer is persisted as it is given, through a run folder (D10), the intake walk included.
  - *Left:* none beyond the run folder's own limits.

## Left to the builder

- The names of the rulebook reference and the two agents, and the field names for coverage, applied answers and table-confirmed records (never `settles`).
- Whether the rulebook is a new reference or a section of `grilling-technique` (one ranking rule either way).
- How the budget is set per run; the strategic mode's stop thresholds within "one to three strategic sittings".
- How strategic sittings map onto rounds and round records.
- How the after-each-answer check is kept cheap — coverage links first, the applier for the rest — within the rule that every answer is checked against the whole registry before the next question.
- Model tiers for the agents.
- The final option wording in the intake walk and the code-defect question, within D5.
- **Delivery order**, suggested as increments that each ship value: (1) the rulebook, the question shape and the intake walk; (2) in the interview: merging, one question per row, applying forward, the bulk paths and the code-defect change; (3) strategic sittings; (4) the package prompt and `/brd-reconcile`'s reading of applied answers.
- The synthetic fixtures and how goal 9 is measured.

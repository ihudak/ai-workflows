# Grilling technique (embedded — shared reference)

The interview technique the authoring commands (`/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`), `/brd-split`, `/prompt-grill-me`, and `/prd-proposal` and `/brd-proposal` (for their proposal profile) use to
refine an artifact one decision at a time. Embedded here so callers have **no runtime dependency**;
technique adapted from mattpocock grill-me/grilling. Each caller cites this file and states its own
**depth** and **stage list**; this reference owns only the mechanics.

## Mechanics

- Ask exactly **ONE** question at a time; wait for the answer before the next. Never batch — a firehose is bewildering.
- For every question, give your **recommended answer**, so the user reacts to a proposal, not a blank prompt.
- **Fact-vs-decision split:** if a question can be answered from the artifact, code, or context, explore and answer it yourself; put only genuine **decisions** to the user. **Where the fact needs more than a read — a sweep across repositories, a search the caller already dispatches an agent for — fetch it rather than asking**: finding a fact is the run's job and never the user's, and a question that hands the user a lookup spends their turn on the half of the work they are worst placed to do. Bound it to a fact a question **actually being asked** turns on; a speculative dispatch is cost with no question behind it. (Ported from the upstream technique this file forks — `## Relationship` below. Its *don't block on the dispatch* half is deliberately **not** ported: that rule works by asking the rest of the frontier meanwhile, which one-question-at-a-time has no way to do.)
- **A decision the source already states is settled, not a gap.** An explicit inclusion, exclusion, or constraint in the material the caller ingested (the prompt, the markdown source, the `idea.md`, the PRD) or in an earlier answer is a decision the user has already made. Do not re-ask it as if it were open, and never let a question, a recommended answer, **or the rationale behind a recommendation** assume the opposite. Check each recommendation's reasoning against the stated scope before you put it: a rationale that rests on a premise the source contradicts is a defect even when the recommendation would survive the correction, because an unchallenged answer then records a correct decision on a false premise. To argue for revisiting a stated decision, raise it as an explicit challenge that quotes the source (*"the source excludes X — '…' — I'd revisit it because …"*); never build on the opposite silently. A hedged statement (*"maybe except X"*) is a decision to confirm, not to drop: ask it with the quote, and recommend the source's position unless you have evidence against it.
- **Force terminology precision.** When a term is overloaded or fuzzy (e.g. "user" vs. "buyer" vs. "payer"; "enable" vs. "install"), name the ambiguity and make the user pick a precise meaning before building on it.
- **Ask from the frontier.** The **frontier** is every decision whose prerequisites are already settled — the questions answerable *now*, without guessing at an answer not yet heard. Ask **one** of them, then recompute: each answer settles a decision and pushes the frontier outward, unblocking questions that depended on it. A question whose answer depends on another still open is not on the frontier and is not asked yet. This is dependency order named rather than described, and the name is what makes "is this askable yet?" a test rather than a feeling. (Also ported — see below; upstream asks the **whole** frontier in one round, and that half is not ported.)
- Continue until you and the user reach a **shared understanding** for the current section, then write that section.

## Autonomous / background invocation

When the command runs with **no human turn available** to answer (autonomous or background
invocation), do NOT fabricate answers to genuine **decision** questions. The fact-vs-decision split
still holds — facts you resolve yourself — but a genuine decision that would otherwise go to the user
is **recorded as an open question** rather than self-answered. Never grill yourself into a fabricated
decision.

**Which notation is used is the artifact's choice, not the depth's.** Use whatever the caller's own
format authority defines: `[NEEDS CLARIFICATION]` for `idea.md`
(`product-workflows:idea-format`) — including under `--deep`, which changes the
depth but never the file format — and `- [ ]` for the PRD / ARD / specification / design artifacts
whose formats define it. Keying the notation on depth was a defect: `/idea --deep` is the one caller
whose depth changes at runtime, and writing `- [ ]` into an `idea.md` would leave zero
`[NEEDS CLARIFICATION]` markers, compute `status: refined` (`idea-format.md` — refined **iff** zero
open markers remain), and hand an idea carrying unresolved decisions to `/create-prd`.

## Relationship to the upstream technique it was adapted from

**This file is a fork, not a copy, and the fork is deliberate.** The technique is adapted from
mattpocock's `grill-me` / `grilling`, which now ships as a skill in the official marketplace
(`mattpocock-skills:grilling`). **It is not a drop-in replacement for this file**, and a future
reader who notices it there should read this section before proposing the swap.

**Where the two diverge, and which way to jump:**

| | Upstream | Here |
|---|---|---|
| Question cadence | **Batched**: computes a *frontier* of decisions whose prerequisites are settled and asks the whole frontier in one numbered round | **One at a time**, never batched (Mechanics, above) |
| Depth | Relentless by construction — done when the frontier is empty | **Two depths, caller-declared** (below), three callers bounded |
| No human turn available | Not addressed — the model assumes somebody answering rounds | Recorded as an open question, never self-answered (above) |
| Altitude | One conversation, one altitude | Gap categories scale to the caller's altitude (below) |

**The three rows below the first are why this file exists**, and they are not improvements on the
technique — they are **caller management** upstream has no reason to carry. This plugin invokes the
same technique from ten commands (`grep -l grilling-technique plugins/*/commands/*.md`), at two depths
and under differing caps, and a run of any of them may find no human turn available at all. A single-context skill has nothing to say about a `≤5` cap, about what to write
when nobody is there to answer, or about the difference between a product-altitude quality
expectation and an engineering NFR.

**The first row is a genuine disagreement, and upstream may well have the better of it** for the
relentless callers: numbering the round and attaching a recommended answer to each question answers
this file's own "a firehose is bewildering" objection, and it costs fewer round-trips on a long
grill. It is not adopted because `/product-workflows:brd-split`'s ledger walk — a grilling caller whose
own rule, independent of this file, forbids batching — presents rows one at a time by that rule, and
because a cadence that differs by caller is worse than one that is merely debatable.

**Adopting it wholesale would make a plugin outside this family a mid-run dependency.**
`references/dependencies.md` is the authority on which relationships are allowed and draws the line
in one place: a hard, host-resolved `dependencies` entry is for another plugin *of this family*
(`dev-workflows` on `workflows-core`), while everything outside it is an optional companion resolved
at runtime, where a miss must degrade one feature and never break a run. Grilling is **mid-run in ten commands**, which is a different risk from
`/prompt-brainstorm`'s single terminal hand-off to `superpowers:brainstorming`.

**Read upstream for ideas, not for parity — and three have already been taken.** Its *frontier*
framing, its rendered question format, and its rule that a fact is fetched rather than asked are all
in the Mechanics and Depth sections above, each marked where it landed. **Each was ported in part,
and the part left behind was left behind for the same reason every time**: the half that depends on
asking a whole round at once. Upstream's frontier is *asked* wholesale where ours supplies the next
question; its numbering counts a round where ours counts against a cap; its fetch-a-fact rule is
non-blocking because the rest of the round proceeds meanwhile. A future port should expect the same
split rather than assume an idea arrives whole. Port deliberately, record it here, and do not cite
upstream at runtime.

## Depth (the caller chooses)

- **Bounded** — a capped set of the highest Impact×Uncertainty questions, then stop; unresolved high-impact gaps are recorded (e.g. `[NEEDS CLARIFICATION]`). Used by `/idea` (≤10; `--deep` switches to relentless), `/prompt-grill-me` (≤5) and `/brd-split` (≤5, and only when given a slicing instruction).
  **A bounded caller states what its cap costs, because that is what sizes it.** For `/idea` an unresolved gap becomes a marker inside the shipped artifact, so a low cap leaves a hole and ≤10 earns its length. For `/brd-split` an unplaced row simply reaches its own ledger walk without a recommendation, in a Phase 4 that settles every row anyway — one at a time, or inside its Step 1 bulk offer, which names each row it would write and lets any of them be held back to the one-at-a-time walk — the residue has a free fallback, so its cap is lower and its questions carry a further gate of the caller's own (`/product-workflows:brd-split` Phase 1.5: ask only where one answer places more than one row). Neither the extra gate nor the differing numbers are this file's to fix; what this file fixes is that a caller declaring **bounded** owes a stated cap rather than an open-ended interview called capped.
- **Relentless** — keep walking the tree until convergence, no cap. Used by `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`, and by `/prd-proposal` and `/brd-proposal` for their proposal profile.

**A bounded caller numbers its questions against its cap; a relentless one does not.** Render a
bounded question as `Q<n>/<cap>` — `Q3/5`, `Q7/10` — so the user can see what they are committing to
before answering. **The denominator is the cap, not a plan**: a bounded grill that converges at
`Q2/5` is finished, not truncated, and stops there. A relentless caller has no denominator to show —
`Q4/?` is noise — so it numbers nothing, and its questions carry the recommended answer and nothing
else. (The rendered-question idea is ported from upstream; its own format numbers a whole round,
which does not apply here — see below.)

## Ambiguity taxonomy (gap-categories, altitude-aware)

Categories the grill scans to *find* gaps — they feed the existing **Impact × Uncertainty** ranking of what to ask. This is **not** a user-facing menu and adds **no** mandatory questions: bounded callers still cap at their stated bound; relentless callers still stop at convergence. Scale the categories to the caller's altitude:

- **All altitudes:** overloaded/fuzzy **terminology**; **pre-mortem / assumption audit** (which unstated assumption, if wrong, breaks this?); **second-order effects** (what does this change downstream?).
- **Product altitude** (`/idea`, `/create-prd`): unstated **quality expectations** (implied latency, scale, availability, or compliance expectations) framed as product outcomes — not engineering NFRs.
- **Engineering altitude** (`/specify`, `/design`): the full **NFR** set (performance, scalability, reliability, observability, security/compliance); **integration / external-dependency** gaps; **implicit enum branch** (a field with N values where only some are specified — the rest are an untested branch).

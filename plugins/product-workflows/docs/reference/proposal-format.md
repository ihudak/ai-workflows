# Effort proposals

**An effort proposal answers one question: how much human delivery time will this requirement set take, in hours.**

It answers it with a range rather than a figure, it says how confident it is in each part of the range, and every reason the number is what it is points at a record on disk that a reader can open. It carries no money at all.

This page is about the subsystem — what the two documents are for, how to read one, and what the plugin will and will not put in them. The commands that write them are [`/prd-proposal`](../commands/prd-proposal.md), for one PRD folder, and [`/brd-proposal`](../commands/brd-proposal.md), for a BRD container's slices rolled into one programme.

## The two documents

| File | Written | For |
|---|---|---|
| `proposal.md` | always | the customer — scope, packages, hours, range, assumptions, exclusions |
| `proposal-brief.md` | at tier 2 and above | the meeting — a short pre-read arguing why the number is what it is |

Both land in the folder the run resolved, beside the PRD or the BRD they price, so the traceability section is relative links that resolve rather than names a reader has to go and find.

## Hours, never money

**No rate, no currency symbol, no monetary total for human hours — at any tier, under any flag.** A rate is contractual, it belongs in a document this pipeline does not produce, and a rate card committed to a shared git repository is a disclosure waiting to happen. The proposal states hours; whoever prices them does that elsewhere.

**There is a second quantity in this family called "cost", and it is unrelated.** [Session cost](session-cost.md) is the USD your Claude session spent running the command. It is model spend, it is measured in dollars, and it has nothing to do with the hours in the document the run just wrote. The two never appear in the same sentence in either artifact, and the run prints them as two separate things.

## Readiness is graded, not gated

You do not need an ARD, a specification, or anything beyond the PRD to get a proposal. What those artifacts change is the **tier** — a grade printed in the header, beside the date, so a reader is never handed a number without being told what stands behind it.

| Tier | Reached when the folder holds | What changes |
|---|---|---|
| 1 · Indicative | the PRD | the document says outright that the drivers are not known |
| 2 · Grounded | \+ verified grounding, \+ a settled decision register | drivers carry evidence; the floor for a document you send |
| 3 · Architected | \+ an ARD | discovery becomes translating an architecture, not authoring one |
| 4 · Specified | \+ a specification | QA is sized from the authored test cases |

The tier is a **ceiling on confidence**, never the confidence itself: tier 1 caps every package at Low, tier 2 at Medium, tier 4 at High, and tier 3 at High only for a package an `[AD#n]` covers. Evidence can push a package lower; nothing pushes it above its tier.

**A tier-1 proposal is still a real document** — scope, packages, team, schedule, a ranged number, every assumption and dependency. What it does not carry is the argument for why the number is what it is, which is also why the brief does not render below tier 2 no matter what you pass: a two-page pre-read explaining a large number, written when the reasons are unknown, is the one artifact this subsystem must not produce.

Raising the tier is what narrows the range. [`/prd-ground`](../commands/prd-ground.md) supplies **one of the two** conditions tier 2 asks for — the verified grounding — on either route; the other is a settled decision register, which only the BRD-to-PRD route produces, so a ground idea-route folder still grades tier 1 and the run says the register is what capped it. [`/create-ard`](../commands/create-ard.md) takes a folder to tier 3 and [`/specify`](../commands/specify.md) to tier 4 — and each command's next-step offer names the one that would move the grade, together with the plain statement that re-running the proposal afterwards narrows the range.

## Reading the range

Every work package carries a confidence grade with a stated reason, and the grade fixes the band around its expected hours:

| Confidence | Band |
|---|---|
| High | −15 % / +30 % |
| Medium | −20 % / +40 % |
| Low | −45 % / +80 %, plus a declared re-estimate gate |

**Low and high are a credible range, not best and worst cases** — the document says so in as many words. A band that departs from its grade's default, in either direction, carries a reason; a band narrower than the default of the grade one step above is a defect the reviewer blocks, because a Medium package priced tighter than any High package claims a precision its own grade denies.

A **Low** package always names the event that will trigger its re-estimate — a profiling result, an arriving decision, a load measurement. A wide range with a dated gate is honest; a narrow range over unprofiled work is not. Declaring the gate is mandatory at Low. Committing that no hours are spent before it fires is a separate, optional promise you attach where delivery genuinely should not begin yet — it is not something the grade imposes on its own.

## What a cost driver is allowed to cite

The document prints a **naive baseline** first, at every tier: what the requirement would cost read at face value, with no correctness, completeness or enforcement obligation. The drivers then explain the gap between that and the real number.

**A driver that cites nothing from this closed set does not render at all:**

1. a **verified grounding finding** — a `[CG#n]` or `[DG#n]` carrying its verifier outcome, cited with the `file:line` the finding itself records;
2. a **frozen decision** — a `[VD#n]` or `[CD#n]` in the register, for scope the customer added after the baseline;
3. a **confirmed code defect** — a `[CDF#n]`, or a finding the run asked you to confirm.

The narrowing is per driver, not global: a driver making a claim about the code cites class 1, because a decision cannot evidence a statement about a repository. The point of the rule is that it is mechanically checkable — a candidate driver with no citation is dropped and named in the run's report, rather than left to authorial care.

## Work packages, and the one that is never an option

Requirements cluster by **delivery seam** — what can be built, tested and accepted independently. Two packages are always present: discovery and design first, test/UAT/release last. Where `EPIC-` folders exist under the folder they seed the middle packages; where they do not, nothing is missing and the document says nothing about it. [`/epics`](../commands/epics.md) is never a prerequisite.

**A defect-remediation package is created automatically and never appears in the scope-lever or priced-options table.** Where the folder records an unrepaired code defect, its repair becomes its own package. Offering a customer the option of deferring a defect the vendor's own work found returns that deferral carrying the customer's authority on a question the vendor's policy has already answered — so it is disclosed as a schedule fact where it will not fit, and never tendered as a lever.

## Identifiers, and which form they appear in

`[WP#n]` names a work package and `[ED#n]` names a cost driver. Both are the plugin's own and stay in that bracketed form.

**A requirement, though, is cited in the form its own source document carries it.** Most of what this plugin writes is read by you, and what a customer does see of the rest — [`/brd-package`](../commands/brd-package.md)'s bundle — arrives with a prompt that explains the plugin's own records to them; a proposal is read by the **customer** with no such prompt, who wrote those identifiers in their own document in their own notation. Rendering this plugin's bracketed form to a reader who has never seen it makes the traceability section unusable to its only reader. That is also why the two proposal artifacts sit outside the auto-link collision check the pre-lint applies to PRD, ARD and Epic files — that check protects documents that get pasted into a tracker, and these are sent to a customer instead. Every other pre-lint check still runs.

## Re-running one, and what a revision owes

A re-run archives the previous documents under `revisions/` and treats the prior figures as an **anchor**: a package's expected hours carry forward unless something feeding them changed, and where a figure moves the changelog names the cause. A figure that moved with no cited cause is a defect. `--redo` discards the anchor deliberately, for when the previous estimate is known to be wrong.

The changelog classifies each row, and the classification is the point:

- a change that **withdraws or contradicts something the previous revision told the customer** is a **correction**;
- a figure that simply moved is a **re-estimate**.

Corrections come first, in the customer's own terms, and are never netted off against a re-estimate. A revision that quietly cancels a withdrawn claim against a new number is exactly the document this rule exists to prevent.

## Knowing when one is out of date

Every proposal ends with a `priced-against` record: an HTML comment, invisible wherever the markdown renders, naming the exact version of every input the run priced. A slice's proposal records its PRD, decision register, grounding, ARD, specification, interview records, defect sources, Epics and the shared proposal profile; an umbrella's records each slice's link and proposal, the root coverage ledger, the container's own defect sources and the profile, which slices it excluded, and — for an excluded slice not yet priced — that slice's own inputs, so its becoming estimable shows.

Whether a proposal is current is decided by comparing that record with what is on disk — contents, not dates, so a fresh clone, a squash merge or a local edit cannot make a stale proposal look current. [`/brd-proposal`](../commands/brd-proposal.md) runs the comparison for every slice in its readiness walk, and first for the umbrella itself: where nothing has moved since the umbrella was written, it says so and offers to stop. Because the profile is shared, correcting it makes every proposal priced under the old one stale. A proposal written before the record existed falls back to comparing times until it is next re-priced.

## The programme umbrella

[`/brd-proposal`](../commands/brd-proposal.md) writes the same two documents one altitude up, over a BRD's slices. Three things are worth knowing as a reader:

- **It is not a sum.** Each of the three adjustments is named in the document rather than absorbed into a total: the cross-slice effort that exists in no slice, a de-duplication where two slices priced the same work, and peak concurrency instead of summed FTEs.
- **It reads slice figures; it never re-derives them.** A figure it cannot read out of a slice's proposal is a defect in that proposal, reported and fixed there.
- **Coverage is computed, not asserted.** The proportion of the container's requirements the programme covers comes from the root coverage ledger, and the remainder is enumerated by identifier — because "two slices were excluded" tells a customer nothing about which of their requirements are unpriced.

Its tier is the minimum of its included slices' tiers, and it prints the mix. One tier-1 slice therefore withholds the brief for the whole programme.

## What a proposal does not do

**It gates nothing, and nothing on the build ladder waits on it.** No command of that ladder reads `proposal.md`, requires one, or behaves differently because one exists — [`/create-ard`](../commands/create-ard.md), [`/specify`](../commands/specify.md), [`/epics`](../commands/epics.md) and the design and implementation commands downstream each resolve the same folder and neither know nor care. No tier withholds permission to begin work. The one command that reads another folder's proposal as a proposal is the sibling umbrella rolling a slice's into a programme-level one, which is a second proposal rather than a phase of the build. Every other such read is an own-folder one: a later run of the producing command, opening the proposal it left there as its re-estimate anchor (the umbrella's run first reading its `priced-against` record, to say whether it is still current), and the review agent inside the run that wrote it. One read is not a proposal read at all: [`/brd-reconcile`](../commands/brd-reconcile.md)'s stale-cross-reference sweep scans every markdown file under a parent BRD as prose, a proposal among them, and never edits one it hits — the hit goes to *what still needs a human*, because re-running [`/prd-proposal`](../commands/prd-proposal.md) or [`/brd-proposal`](../commands/brd-proposal.md) is the correction, and that run archives the prior revision and classifies each change it records as a correction or a re-estimate. One read is of the record alone: a sibling slice's run of [`/prd-proposal`](../commands/prd-proposal.md) reads a proposal's `priced-against` record, and nothing else of it, to decide whether to offer pricing that slice.

**It is a document a vendor sends a customer.** It is not a phase, and it is never a prerequisite for building anything.

## The risk the format cannot remove

**A plausible number with a defensible-looking argument is more dangerous than an obviously rough one.** The tier in the header, the mandatory naive baseline, the rule that drops an unevidenced driver, and per-package confidence are the mitigations. They do not remove the risk, and the person who sends the document is the one carrying it.

Two limits are worth knowing rather than discovering. The umbrella's de-duplication check finds shared work only where two slices cite the **same** finding identifier — genuinely shared work described from two different findings is not detected, and the programme total then overstates. And a productivity basis captured once and never revisited silently mis-scales every later proposal, which is why the profile is shown back for confirmation on every run rather than read silently.

## See also

- [`/prd-proposal`](../commands/prd-proposal.md) — prices one PRD folder: the flags, the gate, the phases, and what each tier changes in a live run.
- [`/brd-proposal`](../commands/brd-proposal.md) — the programme umbrella: the readiness walk, the three adjustments, and the coverage statement.
- [`proposal-format.md`](../../references/proposal-format.md) — the authority both commands author against and the reviewer checks: the full section sets, the tier and confidence tables, and the closed evidence set.
- [Agents](agents.md) — `proposal-reviewer`, the Opus-pinned review gate both commands dispatch.
- [Roles and phases](../roles-and-phases.md) — the `proposal` cost phase, and why it is its own phase rather than part of the BRD route.
- [Session cost](session-cost.md) — the other quantity called cost, and why it is never the one in the document.
- [The BRD-to-PRD route](../brd-workflow.md) — where a slice's grounding, decision register and coverage ledger come from.

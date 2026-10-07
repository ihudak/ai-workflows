# Effort-proposal format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical shape of the two artifacts `/prd-proposal` and `/brd-proposal` write: the section set
each carries, the two identifier namespaces they mint, the readiness tiers that cap confidence, the
confidence grades that fix the range, the closed set of evidence classes a cost driver may cite, the
rules a reviewer checks, in §14 what an umbrella run adds over a slice's own proposal, and in §15 the record of which version of each input a proposal priced. Design authority:
`docs/superpowers/specs/2026-09-08-proposal-commands-design.md` (removed from the tree 2026-09-23; `git show 62e791e8:docs/superpowers/specs/2026-09-08-proposal-commands-design.md` retrieves it).

**Written by `commands/prd-proposal.md` and `commands/brd-proposal.md`; reviewed against by
`agents/proposal-reviewer.md`.** The one command that reads **another folder's** proposal as a
proposal is `commands/brd-proposal.md`, which rolls each slice's into the umbrella; no command of
the build ladder opens one at all. The other targeted readers open only their own folder's:
`commands/prd-proposal.md` and `commands/brd-proposal.md` each open the canonical `proposal.md` a
prior run of theirs left there — §8's stability anchor, read in Phase 6 and archived only in the
`proposal.md`-authoring phase that follows it, **Phase 7 in `/prd-proposal` and Phase 8 in
`/brd-proposal`** (the two do not share the number: `/prd-proposal`'s Phase 8 authors the *brief*),
which is what lets §12's changelog name the cause of every figure that moved, and `commands/brd-proposal.md` first reads its umbrella's `priced-against` record in Phase 2, to say whether it is still current (§15.5) — and the reviewer
above opens the `proposal.md` it is handed and refuses without it. **That own-folder read is why an
umbrella's `proposal.md` is classed `advisory` rather than `unread`** in
`workflows-core:phase-handoff` §4.0: a later run of the command that wrote it is a reader like any
other. **One read is not a proposal read at all**: `commands/brd-reconcile.md`'s
stale-cross-reference sweep scans every markdown file under a parent BRD as prose, a proposal among
them, and never edits one it hits — the hit goes to *what still needs a human*, because a proposal
has its own revision model: re-running the command that wrote it archives the prior revision and
classifies each change it records as a correction or a re-estimate (§12).
**One read is of the record alone**: `commands/prd-proposal.md`'s next-step offer reads a sibling
slice's `priced-against` record (§15) — and nothing else of that sibling's proposal — to decide
whether to offer pricing it, and stops nothing.

## 1. What this format governs, and the two quantities it must never conflate

An effort proposal states **what human delivery time a requirement set will take, in hours** — by
work package, by role, as a range, with an argument for the number that resolves to records on disk.

**The family already measures a different quantity called "cost".** `workflows-core:cost-emission`
records **model spend in USD** for a run of a command. The two are unrelated, and no sentence in
either artifact, in either command, or in this file may let a reader take one for the other.

**Neither artifact carries money at all** — no rate, no currency symbol, no monetary total for human
hours, at any tier, under any flag. Rates are contractual and belong in a document this pipeline does
not produce, and a git-committed rate card is a disclosure waiting to happen.

**A proposal gates nothing on the build ladder.** `/create-ard`, `/specify`, `/epics`, `/design`,
`/implement` and `/ready` each resolve the same folder and neither know nor care whether it holds a
proposal: none requires one, reads one, or behaves differently because one exists, and no grade in
this file withholds permission to begin work. The one command that reads **another folder's**
proposal as a proposal is `/brd-proposal`, which gates on a slice's in order to roll it into the
umbrella — a second proposal rather than a phase of the build. **Every other such read is an
own-folder one, and §0 above is the census** (with the one prose-only scan and the one record-only read it names beside it): a
later run of either producing command, opening the `proposal.md` it left there as §8's stability
anchor (an umbrella's run first reading its `priced-against` record, in Phase 2), and `agents/proposal-reviewer.md` inside the run that wrote it. Do not restate that census
here as "the one reader" — an unscoped form of this sentence stood on six surfaces against §0, and
this is the sentence it was copied from. A proposal is a document a vendor sends a customer; it is
not a phase and never a prerequisite for building anything.

## 2. The two artifacts, where they live, and how a revision is archived

| Artifact | Path | Rendered when |
|---|---|---|
| the proposal | `<folder>/proposal.md` | always |
| the rationale brief | `<folder>/proposal-brief.md` | tier ≥ 2 **and** `--no-brief` not given (§5) |

`<folder>` is the resolved folder itself — the `PRD-` slice for `/prd-proposal`, the `BRD-` container
for `/brd-proposal` — so the traceability section is relative links that resolve rather than names a
reader must go and find.

**Both artifacts open with a header block carrying the readiness tier beside the date.** A reader is
never handed a number without being told what grade of evidence stands behind it.

**A revision archives its predecessor before overwriting it**, following the canonical-plus-archived
convention `commands/update-prd.md` Phase 3 already establishes: the prior `proposal.md` moves to
`<folder>/revisions/<KEY>_proposal_<YYYYMMDD>.md` and the prior `proposal-brief.md` to
`<folder>/revisions/<KEY>_proposal-brief_<YYYYMMDD>.md`. **Where that name is already taken by any
file in `revisions/`**, whoever wrote it, the archive takes the first name not taken of
`<KEY>_proposal_<YYYYMMDD>-2.md`, `-3`, and so on (the brief likewise), the suffix going before
`.md`. The new canonical records `revision_of:` naming the archived snapshot as actually written,
suffix included.

**An archived revision keeps the `priced-against` record it ended with** (§15): archiving is a move,
never a re-render, so each revision still says which inputs it priced.

## 3. Two identifier namespaces, and deliberately only two

`[WP#n]` names a work package. `[ED#n]` names an estimate driver. Every hours figure, confidence
grade, schedule row, acceptance clause and scope lever attaches to a `[WP#n]`; every driver row to an
`[ED#n]`. Ids are contiguous, assigned once, and never renumbered within a revision chain.

**A re-estimate gate is a property of its `[WP#n]`, not a namespace of its own.** The family already
carries fifteen bracketed namespaces, and a sixteenth earning its keep is a higher bar than a
seventeenth being conceivable.

**Both stay in the bracketed form** even though the requirements they cite do not (§11): they are the
plugin's own identifiers, and nothing pastes a work-package label into a tracker. A mnemonic label for
a package is carried as the package's **title**, never as its identifier.

## 4. `proposal.md` — the section set

In this order. Two sections are conditional and are marked; every other section renders at every
tier, and a section with nothing to say says so rather than being omitted.

| # | Section | Notes |
|---|---|---|
| 1 | Header block | tier, date, `revision_of` where one exists, the engagement model from the profile |
| 2 | Scope | what is being estimated, in the customer's own terms |
| 3 | The naive baseline | §8 — mandatory at every tier, and printed before the drivers |
| 4 | Cost drivers | the `[ED#n]` table; at tier 1 an explicit statement that the drivers are **not known** |
| 5 | Work packages | the `[WP#n]` set — §7 |
| 6 | Hours by package and role | the `[WP#n]` × role grid, carrying an **Expected**, a **Low** and a **High** total column per package plus a totals row and a totals column — the shape the arithmetic check reconciles in both directions |
| 7 | Confidence and range | per package, with a stated reason; §6 |
| 8 | Re-estimate gates | one row per `[WP#n]` carrying one, with its trigger event — **and, at tier 1, the document-level row §5 fixes wherever §5's bullets write a gate at all**, in the same table, naming the document where a per-package row names its `[WP#n]`. Where §5 writes none, the section says why rather than leaving the tier-1 cap unexplained |
| 9 | Delivery approach | how the packages sequence into deliverable increments |
| 10 | Team composition | roles and counts, from the profile |
| 11 | Indicative schedule | with peak concurrency, never a sum of FTEs |
| 12 | Assumptions | |
| 13 | Dependencies | including everything §8's open-items sweep produced |
| 14 | Risks | |
| 15 | What the range does **not** cover | §9 — a different list from section 20 |
| 16 | Engagement governance | shaped by `engagement_model` — cadence, reporting, who accepts on each side, and what each model makes of all three |
| 17 | Change control | shaped by `engagement_model` |
| 18 | Scope levers and priced options | shaped by `engagement_model` — the `[WP#n]`s that may be dropped, deferred or taken up, and what each does to the range. **This is the priced-options table §7's defect-package prohibition names**, and a defect-remediation package never renders in it |
| 19 | Acceptance | per package, which is why a package must be independently acceptable |
| 20 | Exclusions from scope | |
| 21 | Traceability | requirement identifiers → `[WP#n]`, in the form §11 fixes |
| 22 | Reconciliation to a prior estimate | **conditional** — renders only under `--baseline`; absent is not a gap and is never apologised for |
| 23 | Changelog | **conditional** — renders only on a revision; §12 |

**After the last section that renders comes the `priced-against` record (§15)** — on a slice's
proposal and an umbrella's alike. It is machine data in an HTML comment, not a section: it is counted
against neither this set nor §10's, carries no prose, and is never reviewed for content.

## 5. Readiness tiers, and the ceiling each puts on confidence

The tier is **graded, never gated**, and this section adds no refusal of its own. The only hard
refusal on readiness is the absence of the caller's own gated input, which that caller's
`require-on-main` already performs — `prd.md` for `/prd-proposal`, each included slice's
`proposal.md` for `/brd-proposal`.

| Tier | Reached when the resolved folder holds | What the tier changes |
|---|---|---|
| **1 · Indicative** | `prd.md` | the driver section states outright that the drivers are not known; standing banner in the header |
| **2 · Grounded** | \+ verified grounding, \+ a settled decision register | drivers carry evidence; **the floor for a document that goes to a customer** |
| **3 · Architected** | \+ `ard.md` | discovery becomes translation of an existing architecture rather than authoring one |
| **4 · Specified** | \+ `specification.md` | QA is sized from the authored test-case count; the definition of done is built from the acceptance criteria |

**Both tier conditions reuse rules that already exist.** *Verified grounding* means every finding
carries a verifier outcome — `workflows-core:grounding-format`'s rule that a finding without an
outcome is not evidence. *A settled register* means **a `decisions.md` is present and every interview
round it names is settled**, the test `commands/brd-package.md` already applies, a torn write
(`references/decision-register-format.md` §8) naming no round. **The presence half
is not redundant**: a folder holding no register at all names no round, so a condition worded only as
*every round is settled* is vacuously true there — and combined with grounding, which is reachable on
either route, it would grade a folder with no register at all at tier 2 and unlock the brief this
section's own floor withholds.

**The tier caps confidence; it never sets it.** Range width is computed bottom-up from per-package
confidence (§6). The tier is a ceiling: evidence can only push a package lower.

**Both tables above are read over a `PRD-` folder.** A `BRD-` container holds no `prd.md`, `ard.md`
or `specification.md` of its own — those are authored in the slices under it — so an umbrella's tier
is not graded off this ladder at all: it is the minimum of its included slices' tiers (§14), and the
ceiling that minimum sets is then the ceiling in the second table.

| Tier | Highest grade any package may carry |
|---|---|
| **1 · Indicative** | **Low** |
| **2 · Grounded** | **Medium** |
| **3 · Architected** | **High** for a package an `[AD#n]` covers; **Medium** for one it does not |
| **4 · Specified** | **High** |

**At tier 1 the document carries at most one document-level re-estimate gate, and whether it carries
one at all is decided by what capped the folder** — never **§8's no-hours commitment**, attached per
package against a trigger nobody has scheduled. **The per-package re-estimate gates themselves still
render, and at this tier every package carries one**: the ceiling in the table above puts every
package at Low, where §6 makes a declared gate mandatory, and §4's section 8 is the single table
those rows and the document-level row share. What tier 1 forbids is the commitment, not the gate.
**A document-level gate is written only where the thing that would lift the cap has a producer on
this folder's own route**, and the two halves of tier 2 differ on exactly that:

- **Grounding is missing — whether or not the register is missing with it.** The gate's trigger is
  grounding the folder, and it has a producer on either route: `commands/prd-ground.md` runs on
  `route: idea` as readily as on a slice. **A folder missing both halves takes this bullet, not the
  one below** — a fresh idea-route folder holding nothing but `prd.md` is that case and the ordinary
  one — because grounding is the half a run on this folder's own route can actually supply, and the
  bullet below presupposes it in its own first words. Naming grounding unconditionally would instead
  write a trigger that has *already fired* into a proposal for a folder that command has run on,
  which is reachable on either route.
- **The folder is already ground and the register is the missing half.** On the BRD route the trigger
  is settling the register, produced by `commands/brd-interview.md` and `commands/brd-reconcile.md` on
  a slice. **On the idea route it has no producer at all, so no gate is written** — the document says
  plainly that nothing available on this folder's route settles a register, and that the tier-1 ceiling
  therefore stands. The idea-route limitation is **disclosed rather than mitigated** — the paragraph
  below says so of the cap itself, and a gate is a mitigation. Writing one here would be the worse of
  the two errors above: not a trigger that has already fired, but a customer-facing commitment to a
  re-estimate no run on this route can ever honour.

The grade stays Low because Low is honest. **What does not ride on it is a prohibition** (§8).

**The brief does not render below tier 2**, irrespective of the flag: its spine is the driver
argument, and below tier 2 that spine does not exist. A two-page pre-read explaining why a number is
large, written when the reasons are unknown, is the one artifact this format must not produce.

**An idea-route PRD caps at tier 1 today, and that is a truthful grade rather than a defect.** **The
cap rests on the register alone.** `commands/prd-ground.md` runs on `route: idea`, gating `prd.md`
rather than a ledger, so *verified grounding* is reachable from a folder `/idea` and `/create-prd`
built — it is the optional, ungated run that supplies that half of tier 2 on **either** route. What
no idea-route folder can reach is the other half: a `decisions.md` holds a decision only from
`commands/brd-interview.md`, which settles each round into it, and `commands/brd-reconcile.md`,
which freezes the customer's `[CD#n]`s into it and writes the dependent BRDs' registers in its
propagation sweep — **and both run only on a BRD slice**; every other write into one —
`commands/create-prd.md`'s `[AS#n]` for a customer-authority gap, which may create the file, and the
`consumed_by` stamps the build ladder puts on records it drew on — also happens only on a BRD slice,
so the cap holds for the same reason whichever writer is named. So an idea-route folder that has
been ground still grades tier 1, and it grades there because it holds no register — which is what
the run prints as the cap, rather than a claim that nothing was ground. **The limitation is
disclosed rather than mitigated**: the tier is printed, the brief is withheld, the driver section
says outright that the drivers are unknown, and no re-estimate gate is written for a trigger this
route does not produce. A code scan discovers capability; grounding asks whether a specific claim is
true of a specific commit, and only the second can carry a driver. A tier-1 proposal is still a real
document — scope, packages, team, schedule, a ranged number, every assumption and dependency. What
it does not carry is the argument for why the number is what it is.

## 6. Confidence grades, the default band, and what a deviation costs

| Confidence | Band about the expected figure |
|---|---|
| **High** | −15 % / +30 % |
| **Medium** | −20 % / +40 % |
| **Low** | −45 % / +80 %, and a declared re-estimate gate (§8) is **mandatory**, not optional |

**The band is the default the command computes, and any deviation from it — in either direction —
carries a stated reason in the confidence section.** Widening and narrowing are treated alike: an
earlier draft allowed free widening, and measured against the document this format is derived from it
failed three of that document's ten packages, all of them narrower than their grade's default on at
least one side. One of the three had been downgraded a grade between revisions and had kept the band
of the grade it left, which is drift no author notices and no reader can see.

**Severity, because a deviation is not one thing:**

- a deviation with **no stated reason** is a **recommendation**;
- a band **narrower than the default of the grade one step above** is a **BLOCKER** — a Medium
  package priced tighter than any High package claims precision its own grade denies, and no reason
  rescues that.

**Both comparisons carry a one-percentage-point tolerance.** Whole-hour rounding moves a band by up to
a point, and without the tolerance the rule fires on arithmetic rather than on judgement.

**Confidence is stated per package with a reason, and the document says in as many words that the low
and high figures describe a credible range rather than best and worst cases.**

## 7. Work packages

Requirements cluster by **delivery seam** — what can be built, tested and accepted independently. That
property is load-bearing: sections 9 and 19 of §4 both rest on it, and a package that cannot be
accepted on its own makes both of them false.

**Two packages are always present:** a discovery-and-design package first, and a test/UAT/release
package last. Where `EPIC-` folders exist under the resolved folder they seed the clustering of the
middle packages; where they do not, nothing is missing and the document says nothing about it. Epics
are never required.

**A defect-remediation package is created automatically, and it is never a scope lever.** Where the
folder holds an unrepaired code defect, its repair is its own `[WP#n]`. Asking a customer to authorise
deferring a defect the vendor's own work found returns that deferral carrying the customer's authority
on a question the vendor's policy has already answered.

**Three sources are swept and unioned**, because the obvious single source is necessary and nowhere
near sufficient — `code-defect-log.md` has one writer and it records only defects a decision turned on:

1. **`code-defect-log.md`** — every `[CDF#n]` whose disposition is `open`, `in-scope` or
   `conditional`, save one `references/decision-register-format.md` §8 calls a torn write, which
   no round recorded raising. Needs no confirmation: a standing `[CDF#n]` is a defect somebody already
   adjudicated.
2. **A verified grounding finding whose own text records a defect** rather than a capability.
   **Operator confirmation required.**
3. **An `[SR#n]` self-review finding** in the packaged bundle, where one exists, naming a code defect
   and dispositioned `accepted-risk` or `escalated-to-customer`. **Operator confirmation required.**

**Both filters name the values they admit, because neither vocabulary has a value meaning
*resolved*.** `code-defect-log-format.md` §4 fixes five dispositions and states that there is **no
`fixed` disposition** — nothing on this route builds anything, so a repaired defect keeps whatever
disposition it had — and a filter reading *not recorded as resolved* would therefore admit all five.
The two source 1 excludes are excluded for opposite reasons: `withdrawn` means the intent basis was
wrong and there was never a defect, and `out-of-scope` means the repair is recorded and deliberately
not this engagement's work. Neither may be priced into a mandatory scope §7 then forbids the customer
from declining. A `conditional` entry **is** packaged, and its `blocked_on` is carried into §4 section
13 as a dependency: what the repair waits on is what a reader needs in order to schedule it, and
dropping the field would put a package in the document with no statement of what it turns on.

**Source 3's four values are `commands/brd-package.md`'s**, and the two it admits are the two under
which the defect the finding names is still standing. `rejected-with-reason` refused the finding
outright and never reached the customer; `fixed` records a correction made against the finding inside
the packaging run. **Where a `fixed` disposition corrected a bundle document rather than the code it
named, the code defect is still standing** — and it reaches this sweep through source 1 or source 2,
both of which read records of the code rather than records of the bundle.

Sources 2 and 3 need confirmation because neither is a defect *register*: a finding may already be
repaired, or may not be the vendor's to repair. A confirmed defect from any source is identical
downstream — same package, same exclusion from the lever table.

**A defect-remediation package never renders into the scope-lever table or the priced-options table.**
Where it cannot fit the delivery window, that is disclosed as a schedule fact, not tendered as an
option.

## 8. The estimate

**The naive baseline is computed and printed first**, at every tier: what the requirement would cost
if read at face value, with no correctness, completeness or enforcement obligation. It is the anchor
that makes the real number legible — without it the driver table has no subject.

**Every driver cites evidence from a closed set of three classes**, each resolving to something on
disk an independent reader can open:

1. a **verified grounding finding** — `[CG#n]` or `[DG#n]`, carrying the verifier outcome without
   which `workflows-core:grounding-format` says it is not evidence, cited with the `file:line` the
   finding itself records;
2. a **frozen decision** — `[VD#n]` or `[CD#n]` in the register, for the driver class that is *scope
   the customer added after the baseline*;
3. a **confirmed code defect** — `[CDF#n]`, or a §7-confirmed finding from either other source.

**A driver citing nothing from that set does not render at all.** The value of the rule is that it is
mechanically checkable rather than a matter of authorial care.

**The narrowing is per-driver, not global: a driver making a claim about the code cites class 1**,
because a decision cannot evidence a statement about a repository. Restricting the whole set to
grounding was the first draft of this rule and it was wrong — in the source engagement a driver worth
roughly a tenth of the estimate cited four decisions and no code, and was the single row the customer
was most likely to recognise as theirs.

**Hours per package and role** are derived from the requirement count and kind inside the package, the
drivers touching it, and the profile's productivity basis and hours-per-developer-day. **QA effort is
sized from the authored test-case count at tier 4 and from a stated ratio below it, and the document
says which of the two it used** — a ratio silently replaced by a count is a change of basis a reader
is entitled to see.

**A package graded Low carries a declared re-estimate gate naming its trigger event** — a profiling
result, an arriving decision, a load measurement. A wide range with a dated gate is an honest artifact;
a narrow range over unprofiled work is not.

**The no-hours commitment belongs to a gate, not to a grade.** An earlier draft attached *"no
implementation hours inside this package are incurred before the gate"* to the Low grade itself, which
composed with §5's tier-1 ceiling to make the ordinary output of this format a document forbidding any
work from starting. **The commitment is a property the operator attaches to a particular declared
gate**, where delivery genuinely should not begin before a trigger fires. Declaring the gate is
mandatory at Low; making the commitment is not, and a gate without one is a re-estimate promise rather
than a stop.

**Open items become dependencies automatically.** Open assumption records, unanswered customer
questions from the interview round, and any code defect recorded as blocking render into section 13
and into the brief's *what is needed before week 1* list. Derived from the register, never authored —
so a question raised of the customer and not yet answered cannot vanish between the review package and
the proposal.

**The stability rule, which is what makes a re-run safe.** A re-run always re-derives its inputs, but
the prior revision is an **anchor**: a package's expected hours carry forward unchanged unless
something feeding them changed, and where a figure moves the changelog (§12) names the cause. A figure
that moved with no cited cause is a defect. `--redo` discards the anchor deliberately, for when the
prior estimate is known to be wrong.

## 9. The range carries its own exclusions, and they are not the document's exclusions

Section 15 of §4 is a **short block stating what the low-to-high band does not cover** — a reversal of
a settled decision, a discovery that materially more of the system is live than the evidence records,
customer-side delay on a named dependency, a decision resolved in the direction that widens scope.

**This is a different list from section 20, exclusions from scope**, and conflating them is how a
reader concludes the high figure is a ceiling. It is not: it is the top of a band computed under stated
conditions, and this block is the conditions. They are two sections rather than one for that reason.

## 10. `proposal-brief.md` — the section set

The brief is a short pre-read, derived from the same resolved data set as the proposal and never
re-authored from it. **Its spine is the driver argument** — the naive baseline, why the number is not
that, and what the largest single share of the estimate is owed to.

**The spine is not the whole brief.** It also carries, in the customer's own terms and each derived
rather than written fresh:

| # | Section | Derived from |
|---|---|---|
| 1 | The driver argument | §8's baseline and `[ED#n]` table |
| 2 | Corrections this revision owes the customer | §12's correction rows |
| 3 | Reconciliation to their prior estimate | §4 section 22, where `--baseline` was given |
| 4 | Each deliberately-unpriced item, with the gate that will price it | §8's re-estimate gates |
| 5 | What is needed before week 1 | §8's open-items sweep |
| 6 | Any requirement where the vendor's architecture and the customer's own text still contradict each other | the register and the grounding findings |

**Every figure the brief repeats matches the proposal**, and every item in rows 2–6 that the proposal
carries reaches the brief. A spine-only brief is a defect, not a shorter brief: the brief is the
document that gets read first.

## 11. Which form a requirement is cited in

**A proposal cites a requirement in the form the source artifact carries it.** Most of what the
plugin writes is read by the operator or pasted into a tracker, and what a customer does see of the
rest — `commands/brd-package.md`'s bundle — arrives with a prompt that explains the plugin's own
records to them (`references/bundle-packaging.md`); a proposal is read by the **customer** with no
such prompt, who wrote those identifiers in their own document in their own form. Rendering the
plugin's bracketed form to a reader who has never seen it makes the traceability section unusable to
its only reader.

**The two artifacts sit outside `workflows-core:pre-lint`'s *Auto-link collision* check, which is
scoped to PRD, ARD and Epic files, and that exclusion is deliberate rather than an oversight.** That
check is an auto-link detector for documents that get pasted into a tracker, and these two are not —
they are sent to a customer, as a document. Everything else `pre-lint` performs — its universal checks,
identifier integrity, required-section presence — does run.

**The `[WP#n]` and `[ED#n]` namespaces the proposal mints are the plugin's own and stay bracketed**
(§3). **A conversion in either direction is the defect** the reviewer looks for: an identifier read from
a source artifact keeps that artifact's form, and one the proposal minted keeps the bracketed form.

## 12. The changelog section, and the classification that is its whole value

Rendered on a revision only. One row per moved figure or changed section, each with a direction and a
pointer to the section that now carries it, generated by diffing against the anchor.

**Each row is classified, and the classification is computed rather than written:**

- a change that **withdraws or contradicts a statement the previous revision made to the customer** is
  a **correction**;
- a figure that moved is a **re-estimate**.

**Corrections are listed first, are stated in the customer's own terms, and are never folded into a net
total.** A revision that quietly nets a withdrawn claim against a re-estimate is precisely the artifact
this rule exists to prevent.

## 13. The risk this format cannot remove, stated to the operator who sends the document

**A plausible number with a defensible-looking argument is more dangerous than an obviously rough one.**
The tier in the header, the mandatory naive baseline, the citation rule that prevents a driver rendering
without evidence, and per-package confidence are the mitigations. The residual risk is real, and the
person sending the document is the one carrying it.

**Two limits of the checks, stated rather than left to be discovered.** The de-duplication check in an
umbrella run detects shared work only where two slices cite the **same** finding identifier; genuinely
shared work described from two different findings is not detected and the umbrella overstates. And a
productivity basis captured once and never revisited silently mis-scales every later proposal, which is
why the profile is shown back for confirmation on every run rather than read silently.

## 14. The umbrella — what `/brd-proposal` adds over a slice's own proposal

Everything above governs both artifacts at both altitudes. This section states the additions, and it
adds only: `commands/brd-proposal.md` renders §4's same twenty-three-row section set and mints from
§3's same two namespaces, at programme altitude.

**The umbrella carries one row per included slice — hours, range, tier and confidence — read out of
that slice's own `proposal.md` and never re-derived.** Detail stays in the slice proposals: the
umbrella does not restate a slice's `[ED#n]` driver table, does not re-cluster its `[WP#n]`s, and does
not recompute its hours from the requirement set. A figure an umbrella run cannot read out of a slice
proposal is a defect in that proposal, to be reported and re-run there. What the umbrella adds around
the rows is its own — aggregated roles, one team, one schedule, the cross-slice dependency graph, and
the coverage statement below — plus the three adjustments.

**The roll-up is not a sum, and each adjustment is named in the document rather than absorbed into a
total.** A programme total a reader cannot decompose into the slice rows plus a named adjustment is a
total nobody can check, and an unnamed adjustment is indistinguishable from an arithmetic error.

1. **Umbrella effort that exists in no slice** — programme management across slices, cross-slice
   integration, one release and one acceptance campaign rather than one per slice. It takes its own
   `[WP#n]`s in the umbrella's own contiguous series and its own `[ED#n]`s under §8's closed evidence
   set, and it is an addition to the row-set total, stated as one.
2. **De-duplication, which is mechanically detectable.** Two slices that priced the same discovery
   activity or the same shared component **cite the same verified finding identifier** in their driver
   tables. Every finding identifier claimed by more than one included slice is flagged, and the
   operator rules on whether it is genuinely two pieces of work; where it is not, the deduction is a
   named adjustment and never an edit to a slice's own figures. **The limit of the check is disclosed
   in the document itself**, not merely known to the operator: shared work described from two
   different findings is not detected, and the umbrella then overstates (§13).
3. **Sequencing.** Slices sharing a team do not add their FTE figures; peak concurrency is computed
   from the programme schedule, which is §4 section 11's rule applied across slices rather than within
   one. Slice order comes from `depends_on` in each slice's PRD frontmatter; a slice whose PRD records
   none contributes no edge, and the document says so rather than inferring one from folder order.

**§7's two fixed packages are read at programme altitude, and its defect sweep is not repeated.** The
discovery-and-design package is the cross-slice one, and the test/UAT/release package is the single
campaign the first adjustment above names — both are the umbrella's own, not a sum of the slices'.
The defect sweep, though, has already run in every slice that was priced, and each confirmed defect
is inside that slice's row: an umbrella that swept a slice's sources again would price the same
repair twice, so it sweeps only what the container itself holds and reports what it found there.

**The umbrella's tier is the minimum of its included slices' tiers, and it prints the mix.** A
programme cannot claim to be specified because three of its five slices are. §5's ceiling for that
minimum tier then caps every package the umbrella mints of its own, and §5's brief floor is read
against that same minimum — so one tier-1 slice withholds `proposal-brief.md` for the whole programme.
**§5's tier-1 document-level gate reads here as the umbrella's own, and it names which slices**: its
trigger is §5's own — whatever capped each of them — applied per included slice whose tier set the
minimum and named by key, because the umbrella grades no folder of its own and an unqualified trigger
would name nothing at this altitude. **§5's producerless case cannot arise here**: every included
slice is a `PRD-` folder under a `BRD-` container, so a register-capped slice always has
`commands/brd-interview.md` as its trigger's producer, and the gate is always writable. The
per-package gates §6 makes mandatory at Low are declared for the `[WP#n]`s the umbrella mints of its
own; a slice's own gates are inside that slice's row and are not restated at this altitude.

**Ranges are summed, and stated as summed**, carrying §6's caveat that low and high are not
simultaneous outcomes. A statistical roll-up would be narrower and unexplainable in the meeting this
document exists to survive; that trade is refused here and recorded so it is not proposed later.

**The coverage statement is computed from the resolved container's own `coverage-ledger.md` and never
asserted.** Every row of that ledger falls into one of four classes, over the six dispositions
`coverage-ledger-format.md` §3 defines: `covered-by` an **included** slice, and therefore priced;
`covered-by` an **excluded** slice; still `unallocated`, meaning never sliced and therefore never
estimated; or terminal (`deferred-to`, `rejected`, `superseded-by`), disclosed with the reason the
ledger records. The umbrella states what proportion of the container's requirements it covers **and
enumerates the remainder by identifier** — in the form §11 fixes, which is the customer's own — because
"two slices were excluded" tells that customer nothing about which of their requirements are unpriced.
It is recomputed on every run, so it cannot go stale, and where no ledger is on disk the document says
so and claims no proportion rather than substituting the union of the slices' own ledgers, which would
measure coverage of what was sliced rather than of what the customer asked for.

**Two sections read differently at this altitude, and neither is optional.** §4 section 15 (what the
range does not cover) additionally carries the de-duplication limit above and every slice-level
condition that would move the programme band; §4 section 22 never renders, because `/brd-proposal`
takes no `--baseline` — a prior estimate reconciles against the slice that was estimated, not against
the umbrella over it.

## 15. The `priced-against` record — which version of each input a proposal priced

**Whether a proposal is current is decided by content, not by time.** Every `proposal.md` either
command writes ends with one HTML comment recording the git blob id of every input the run priced,
and a later reader compares those ids with the inputs on disk. A time — a commit's or a file's —
records no version: an input edited locally is newer only than its own last commit, a squash merge
can carry a proposal and the change it never priced in one commit, and a shallow clone gives every
file one time. **A proposal written before this record existed carries none**, and
`commands/brd-proposal.md` Phase 2 decides it by the times it always did, over `prd.md`,
`decisions.md` and `grounding/` alone.

### 15.1 The input sets

**A slice's** — every input `commands/prd-proposal.md` reads to price the folder, paths relative to it:

| Input | Why the pricing reads it |
|---|---|
| `prd.md` — or, where none exists, the `<KEY>_<slug>.md` PRD `workflows-core:addressing` §5's legacy fallback accepts | the requirement set the packages cluster |
| `decisions.md` | tier 2's settled-register half; frozen decisions are driver evidence |
| `ard.md` | tier 3 |
| `specification.md` | tier 4; the authored test-case count sizes QA |
| `code-defect-log.md` | defect source 1 (§7) |
| every `.md` file under `grounding/`, recursively, no name beginning with `.` — an editor's backup, an autosave or any other file is not a grounding record | tier 2's verified-grounding half; driver evidence; defect source 2 |
| every `interview/round-<N>.md`, and `interview/customer-questions.md` | the register's settledness; the open-items sweep's unanswered customer questions (§8) |
| every `self-review-<YYYYMMDD>.md` | defect source 3 |
| `epic.md` in every immediate `EPIC-*` subfolder | seeds the middle work packages (§7) |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | productivity basis, roles, calendar, engagement model |
| the `--baseline` file, where one was given | section 22's reconciliation to a prior estimate |

**A symlink counts as the file or directory it points at** — the pricing reads through it, so the
record does too — and a dangling one is no input; a directory reached twice through links is walked
once. **The `--baseline` file is recorded by where it sits**: under `$SPECS_PATH` by its
`$SPECS_PATH/` path, which any machine can check; outside it as `<baseline>` — its id recorded, its
path not, since a local path has no place in a document a customer receives and no other machine
could open it — so its currency is never compared, and `check` lists it under `unverifiable`.

**An umbrella's** — paths relative to the BRD folder:

| Input | What a change to it means |
|---|---|
| `<slice>/brd-link.md`, for every slice `commands/brd-proposal.md` Phase 2 enumerates | a slice carved or removed since |
| `<slice>/proposal.md`, for every slice holding one, included or excluded | a slice re-priced since, or one excluded then and priced since |
| `coverage-ledger.md`, the root ledger | the coverage statement (§14) |
| `code-defect-log.md`, every file under `grounding/` and every `self-review-<YYYYMMDD>.md` in the BRD folder itself, read as a slice's are | the container's own defect sources, which `commands/brd-proposal.md` Phase 6 step 3 sweeps |
| for every slice the umbrella excluded that holds no `proposal.md`: that slice's own input set above, its paths under `<slice>/` (the profile once, for all) | an excluded unpriced slice whose inputs moved, so it may be estimable now; one excluded although estimable reads stale only when its inputs move |
| `$SPECS_PATH/.dev-workflows/proposal-profile.yml` | team shape and calendar: peak concurrency and the schedule |

**Not inputs:** `proposal.md` and `proposal-brief.md` (the output, and §8's stability anchor),
`revisions/`, and — in a slice — `brd-link.md` and `coverage-ledger.md`, which `/prd-proposal` reads
only to word a refusal. **An input absent when the run priced has no line**, so its later appearance
is a change: `ard.md` landing after a tier-2 proposal makes it stale, which is the point — the umbrella
above it takes the minimum of its slices' tiers (§14). **The profile is one file for the whole specs
repository**, so correcting it makes every proposal priced under the old one stale — truthfully: a
re-run would price each of them differently.

### 15.2 The record

```
<!-- priced-against
$SPECS_PATH/.dev-workflows/proposal-profile.yml <id>
PRD-1234-01/brd-link.md <id>
PRD-1234-01/proposal.md <id>
PRD-1234-02/brd-link.md <id> excluded
coverage-ledger.md <id>
-->
```

That one is an umbrella's; a slice's has the same shape over its own set, and never an `excluded`.
**The block is the last thing in the file** — only whitespace may follow it — and holds one line per
input present when the run recorded: the path as §15.1 writes it, one space, and the id
`git hash-object` gives the file's content — 40 lowercase hexadecimal characters, or 64 in a
repository using SHA-256 objects — sorted by path in byte order. **In an umbrella's record an excluded
slice's `brd-link.md` line ends ` excluded`**, which is how a later reader knows which slices the
umbrella included; that word appears on no other line. The id is git's because inside a repository
`hash-object` applies the clean filters a commit would — a CRLF and an LF checkout of one file hash
alike — and outside one it still runs. The paths are folder-relative so a folder moved with `git mv`
keeps its record; the profile, which sits outside every folder, keeps its literal `$SPECS_PATH/`
prefix. **An HTML comment** because a proposal is a document a vendor sends a customer: it is
invisible wherever the markdown renders, archived with the revision it belongs to (§2), and committed
and gated with it.

**A record that does not parse is no record** — not the last thing in the file, not closed, a line
that is not `<path> <id>` (or an umbrella's `<slice>/brd-link.md <id> excluded`), an id of any other
length, a path recorded twice. The reader falls back to the time rule and says the record is
unreadable.

### 15.3 The script, and who runs what

**One bundled script computes, writes and compares the record, and nothing else does**:
`${CLAUDE_PLUGIN_ROOT}/scripts/proposal-record.py`, Python standard library only, self-tested in CI.
Enumerating §15.1, hashing, sorting and parsing are exactly what a run re-deriving them from prose
gets subtly wrong, so **no run computes, copies or edits an id itself**.

| Subcommand | What it does | Run by |
|---|---|---|
| `record --specs <SPECS_PATH> --folder <folder> [--baseline <file>]` | prints a slice's record for the inputs on disk now | `/prd-proposal`, end of Phase 2 |
| `record … --brd-key <KEY> [--excluded <slice-dir>,…]` | prints an umbrella's, the excluded slices marked | `/brd-proposal`, end of Phase 5 |
| `stamp --proposal <proposal.md> --record <file> [--excluded <slice-dir>,…]` | makes the block in `<file>` the last thing in the proposal, replacing a record already ending it and removing any other — a damaged one's stray opening line, which hides what follows it, included — and preserving every other byte; `--excluded` sets an umbrella's excluded marks; prints whether it wrote | the authoring phase, the pre-lint, and after the triage's last edit |
| `check --specs <SPECS_PATH> --proposal <proposal.md> [--brd-key <KEY>]` | compares the record with the inputs on disk | the authoring phase; `/brd-proposal` Phase 2; `/prd-proposal` Phase 11 |

`check` prints `basis: content` with `current` and the `changed`, `added` and `removed` paths — an
umbrella's adding the `included` and `excluded` slices its record names, `stale_slices` (each included
slice whose own record reads stale, with why — which also makes `current` false) and
`unrecorded_slices` (each included slice whose proposal carries no readable record), and on a slice's,
`unverifiable` where it records a `<baseline>` — or `basis: none` with
`reason: no-record`, or `reason: unreadable` and a `detail`. **Exit 0 whenever it ran**: a stale or
recordless proposal is a result, not a failure. Exit 2 when it could not run, the cause on stderr.
A caller treats any non-zero exit as could-not-run: a missing `python3` exits otherwise.

### 15.4 When the ids are taken

**Once, when pricing begins, and never again for the same proposal.** `record` writes the block to a
temp file (`command mktemp`, never inside a repository) — `/prd-proposal` at the end of Phase 2, once
the profile is settled and before Phase 3 reads the folder; `/brd-proposal` at the end of Phase 5,
once the walk has settled which slices are excluded and the profile is settled, and before Phase 6
reads a slice's figures. The authoring phase stamps that file's block and runs `check`: where an
input moved while the run was pricing, the record still holds the ids the run began from, so the
proposal reads as stale at once and the final report names each moved input. A record of later ids
would claim the run priced content it may only partly have seen.

### 15.5 What current means

**A slice's proposal is current** where `check` returns `basis: content` and `current: true`, and
**stale** where it returns `current: false`, each path it lists being why. The working-tree content
counts, committed or not: a re-run prices what is on disk. Where `check` returns `basis: none`,
`commands/brd-proposal.md` Phase 2's time rule decides.

**An umbrella is current** where `check --brd-key` returns `current: true` — which the script already
makes false while any included slice's own record reads stale, naming it under `stale_slices` — **and**
every slice under `unrecorded_slices` is current by its times, one whose times cannot be ordered
counting as not current. A slice whose own inputs moved needs re-pricing, and so does every umbrella
that included it, which is why no included slice's `prd.md` sits in the umbrella's set; an excluded
slice holding no proposal is the opposite case, watched through its own inputs (§15.1), because
nothing else would show it becoming estimable. `commands/brd-proposal.md` Phase 2 runs this test before the walk and offers to
stop where the umbrella is current.

**The readers**: `commands/brd-proposal.md` — each slice's record in Phase 2, as the one command
reading another folder's proposal, and its own umbrella's, as an own-folder read — and
`commands/prd-proposal.md`'s next-step offer, which reads a sibling's record and nothing else of it
(§0).

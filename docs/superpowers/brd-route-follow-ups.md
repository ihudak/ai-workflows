# BRD-route follow-ups, from a live engagement

> **Removed from the tree 2026-09-23:** every design spec and plan this record cites under `docs/superpowers/specs/` or `docs/superpowers/plans/` (the one exception being `docs/superpowers/specs/2026-09-22-claude-md-split-design.md`, which stays). Each is still retrievable at its cited path with `git show 62e791e8:<path>`.

Reported by the operator after running the BRD route against a real customer engagement, on a **pre-split** version of the plugin. Triaged against the tree at `b774016`; each entry records whether it still reproduces. Ordered as reported — by what it cost that day.

Per **S18**, nothing releases while any of these is open.

**Status, 2026-09-22: nothing here is open, and this line is the one to read first.** Every entry below records its own disposition and they are what this paragraph is derived from — `BRD-1` to `BRD-6`, `R-1` to `R-5`, `E-1` to `E-5`, `E-7`, and `G3-1` to `G3-3` all **closed**; `E-6` **retired**; `E-8` was a recorded **question** about the strength of a guarantee, *not an S18 blocker as filed*, decided 2026-10-28 with its remainder moved to `docs/superpowers/to-fix.md` D31; `G3-4` and *Recorded, not counted as defects* were never defects. **Re-derive this from the entries rather than trusting the sentence** — it is prose, and no gate in `scripts/` reads this file. The dated paragraphs below are kept as the sequencing records they were, and their tense is historical: each says what was still ahead on the day it was written, not what is ahead now. Where one of them named a gate or a defect as still blocking, this line is what settles it.

**Three design gates, sequenced. All three have shipped** — the plan as written on 2026-09-06, when gate 3 was still ahead:

1. **Slice-first grounding and interviewing** — `docs/superpowers/specs/2026-09-06-slice-first-grounding-design.md`. **Shipped in `product-workflows` 2.0.0.** Closed BRD-5 and the per-slice interview package request.
2. **The sibling re-cut** — that spec's §8, settled in `docs/superpowers/specs/2026-09-07-sibling-re-cut-design.md`. A slice grounding shows is too big hands its deferred rows to a new sibling, by re-pointing `covered-by` against the owner's own `deferred-to`. **Shipped in `product-workflows` 2.1.0.**
3. **Idea-route grounding** — **SHIPPED** in `product-workflows` 3.0.0 / `workflows-core` 1.3.0, which also renames `/brd-ground` to `/prd-ground`. That spec's §5. Verified `[CG#n]` findings for a PRD folder authored from an idea, which needs a claim source chosen deliberately since there is no `[BR#n]` inventory. **Spec written 2026-09-07** — `docs/superpowers/specs/2026-09-07-idea-route-grounding-design.md`. It also renames `/brd-ground` to `/prd-ground`, which makes the increment `product-workflows` 3.0.0.

**The release-gating set is no longer only the gates.** Three further defects were reported on 2026-09-07 by an operator running the route on a second live engagement, recorded below as E-1, E-2 and E-3. Per S18 they gate the release exactly as the gates do. **Sequenced: E-1 (closed 2026-09-07), then gate 3, then E-2 and E-3.** E-1 goes first because it is in the verification phase, which is route-agnostic — ship gate 3 first and the idea route inherits it, and the fix then has two routes' worth of surface. E-2 and E-3 both live where gate 3 does not go: E-2 is entirely inside `/brd-package`, and E-3 is additive in a route-agnostic phase with nothing for the new route to inherit, so designing it after gate 3 means designing it once with both routes visible rather than for one and re-checking on two.

**Status, 2026-09-06 (BRD-5 updated 2026-09-07).** BRD-1, BRD-2, BRD-3, BRD-4 and BRD-6 are **closed** — see each entry. BRD-5's design question was settled the same day by brainstorming, merged with the feature request into one design; that design shipped in `product-workflows` 2.0.0, closing both.

## BRD-1 — `/brd-split` passes silently when a BRD has indexed frame sets and no design grounding

**CLOSED 2026-09-06** — two presence relations now run ahead of the count in `/brd-split` Phase 0 step 7, each failing when its own side comes up empty: `code-grounding.md` on main recording no `[CG#n]` (`BRD_SPLIT_NO_FINDINGS`), and a `design/` subdirectory covered by no entry in `design-grounding.md`'s frame-set list (`BRD_SPLIT_DESIGN_NOT_GROUND`, which names `/brd-ground <KEY> --no-code` as the repair). `/brd-ground` Phase 8 now writes that list — every subdirectory on disk, covered or not — which is what makes the relation checkable rather than inferred. A set explicitly skipped with `--no-design` passes and is recorded in `slices.md` as a limit on what the split could check. The gate executes `require-on-main` against `design-grounding.md` rather than reading the worktree: `--no-code` hands that file off in its own commit, so the "one commit stages them all" implication `/brd-split` inherits from its code gate does not reach it — without the gate, the repair the stop recommends could satisfy the stop with an unmerged file. `/brd-interview` carried the identical vacuous count and was fixed with it; the first pass fixed only `/brd-split`. The gate executes `require-on-main` against `design-grounding.md` rather than reading the worktree: `--no-code` hands that file off in its own commit, so the "one commit stages them all" implication `/brd-split` inherits from its code gate does not reach it — without the gate, the repair the stop recommends could satisfy the stop with an unmerged file.

**Originally reported:** The gate counts findings on file and asks whether each carries a verifier outcome — so **zero findings means zero missing outcomes** and the gate is vacuously satisfied. `EPIC-008` had two indexed frame sets and no `grounding/design-grounding.md`, and the split sailed through. A slice can reach build with its designs never reconciled.

**The gate is the wrong shape, not merely too weak.** It tests a property of the findings that exist; the failure is findings that do not. The fix is a presence relation, not a stricter count: **`design/` holding an indexed frame set while `grounding/design-grounding.md` does not exist is itself the defect.** That is the same "a relation that comes up empty must fail rather than pass" rule `check-docs.sh` states for its own checks — applied here to a runtime gate rather than a build gate.

## BRD-2 — `/brd-ground` has no `--no-code`, so BRD-1's fix is unreachable without risking the code grounding

**CLOSED 2026-09-06** — `--no-code` ships as a run mode: `grounding/code-grounding.md` is read-only for the whole run, no `[CG#n]` is produced, and every finding on file keeps its verdict, evidence and verifier outcome, un-renumbered, un-re-verified, un-rewritten. Repositories are still resolved and pinned, because a class-4 `[DG#n]` is pinned to the commit of the `[CG#n]` it cites. Documentation grounding and the derivation matrix are off under it (both write into the read-only file), and it is refused alongside `--no-design`, `--rebaseline`, an explicit `--derivation-matrix`, or against a BRD with no verified code grounding to build on.

**Originally reported:** `--no-design` appears 4 times in `brd-ground.md`; `--no-code` appears **0**. The inverse flag was never built.

The cost is concrete: on finding BRD-1, re-running `/brd-ground` to add the missing design grounding would have re-derived code grounding and put **278 verified findings** at risk. A flag that exists in one direction and not the other is not a symmetry gap — it is the difference between a fixable state and an unfixable one.

## BRD-3 — `/brd-reconcile` gates on `/brd-package`, so an out-of-band customer review can never be reconciled

**CLOSED 2026-09-06** — `--sent <path>` (repeatable) names what the customer was actually sent; each path is copied verbatim into `customer-sent-<YYYYMMDD>/` and committed beside the review before anything reads either. What the gate protects is that a quotation is checkable against a committed copy of its source document; `--sent` supplies that copy from the other direction, so the invariant holds and only its provenance changes. It replaces the package gate and nothing else, is refused where a handed-off package already exists, and the run records which of the two it worked from. The description's "from anywhere" — which meant *at any path* and was read as *of any provenance* — now says the former outright.

**Originally reported:** Its own description (`brd-reconcile.md:3`) says it takes the returned review **"from anywhere"**. Phase 0 raises `BRD_RECONCILE_NEEDS_PACKAGE` — *"no customer package on file … run `/product-workflows:brd-package` first"* — and `BRD_RECONCILE_PACKAGE_NOT_HANDED_OFF` when one exists but was never merged.

Two real customer reviews **predating the plugin** cannot become `[CD#n]` by any route. Two live contradictory instructions in one file is a defect in its own right (`workflows-core:instruction-file-maintenance`); here it also blocks the work.

## BRD-4 — a class-1 design finding is structurally unverifiable as dispatched

**CLOSED 2026-09-06** — `grounding-verifier` now requires `inventory` for every `[DG#n]`, and `/brd-ground` Phase 7 passes it: the Phase 0 step 8 claim list, unchanged, exactly as `design-grounder` was handed it. A `[DG#n]` is a reconciliation between the frame set and the inventory, and the dispatch had been supplying one side of it. It is required on classes 2, 3 and 4 as well as on class 1, because `design-grounder` already refuses to produce any `[DG#n]` without the inventory — so a caller holding a finding necessarily holds the list — and a per-class conditional is one more thing to get wrong in the direction that table exists to prevent.

**Originally reported:**

A class-1 finding asserts *"the frame shows X and no requirement asks for X"* — a **negative over the whole inventory**. `grounding-verifier`'s design-only row does not supply the inventory, so the verifier **correctly** returned `NOT-PROVABLE` and said why.

The verifier is behaving properly; the dispatch is short an input. It needs the inventory alongside the frames. Worth noting the good half: the agent reported *why* it could not prove the claim rather than guessing — the failure surfaced because the contract worked.

## BRD-5 — grounding a slice re-derives what the parent already established

A slice's inventory is a **byte-copy** of the parent's rows against the same pins, so **258 of 281 findings** would have come back identical. The route says a slice is ground exactly as its parent is, and there is no sanctioned inheritance path — so the operator took a **documented deviation** instead, which is the right move and should not have been necessary.

**Operator ruling, 2026-09-06 — this is not an inheritance problem.** The slice is the *primary* grounding site, not the derived one: slice grounding is far more detailed than the BRD's, so where the two disagree the slice wins. And the BRD-level pass is frequently not run at all — a customer asks for everything up front and then cuts scope to cut cost, so grounding and the customer interview happen **per slice only**, with nothing ever ground or interviewed at the BRD level. That is the normal case, not a degraded one.

So the question to settle is not "what may a slice inherit" but **"what is the BRD level still for once the slice carries the work"** — and the two open items below fall out of it rather than standing alone:

- **That claim was wrong, and triage against the tree found it wrong.** `/brd-interview` and `/brd-package` gate the **resolved** folder's own artifacts, and a slice holds its own findings, ledger, register and `[C]` set — so those two already work slice-first. As shipped, `/brd-split` on a root requires no grounding at all — its forcing gate is a mandatory slicing instruction (`BRD_SPLIT_NEEDS_INSTRUCTION`), because a root is never ground and has no findings to cluster candidate slices from; grounding only happens once a slice exists, at `/brd-ground`.
- **Inheritance survives as the smaller half.** Where a BRD-level pass *was* run, re-deriving 258 identical findings is still waste — but it is now an optimisation over an optional input, not the mechanism the route depends on.

**SETTLED 2026-09-06 by brainstorming, shipped in `product-workflows` 2.0.0 — see `docs/superpowers/specs/2026-09-06-slice-first-grounding-design.md`.** Grounding and the customer interview happen at the slice and nowhere else; the root keeps intake and the ledger and gives up both entirely, enforced by refusal rather than offered as a choice. The inheritance half disappears with it — there is no root pass to inherit. The feature request below is closed by the same design, by construction rather than by a patch.

## BRD-6 — the `[CG#n]` id key is written two ways in one file

**CLOSED 2026-09-06** — `workflows-core:grounding-format` gains §2.1, which fixes the on-disk serialisation (one space after every colon, never alignment padding, keys in §2's order, an inapplicable field omitted rather than empty) and states the reading rule that outlives the fix: resolve an id against the finding set you parsed, never by column, and report a disagreeing count as a parse failure rather than an absence. `/brd-ground` Phase 8 cites it as the writer's contract — **and so do both grounder agents**, whose Output templates taught the column-aligned spelling the section forbids and were what the model producing the findings actually copied. Fixing only the file's writer left the defect intact one hop upstream; a review caught it.

**Originally reported:** Aligned in section 1 (`- id:       [CG#1]`), single-space in section 2. A `^  - id: \[CG#` regex silently matches only one of them. **Cost a false "140 phantom gaps" report earlier in the same engagement.**

This is this repo's own "resolve against a known set, never parse out of free text" rule meeting an emitted artifact: the *writer* is inconsistent, so every reader that pattern-matches is wrong in a way that looks like data. Fix the writer, and say which spelling is canonical.

## Filed elsewhere, recorded here so the set is complete
- **#71** — `/frames` never converges on an unreadable frame.
- **#73** — blind verification. Still only drafted in the operator's scratchpad.

## Feature request — customer interview packages per slice

Today the customer loop is BRD-level. The request, in priority order:

1. **Per-slice packages are the valuable form.** With many slices, a customer sees fewer questions per package, so answers are more accurate and worth more.
2. **BRD-level should become optional**, or at least **question-capped**, since the follow-ups will arrive on the slices anyway.
3. Ideally both levels exist and the operator chooses.

Not a defect. Recorded here because it changes `/brd-package` and `/brd-interview`'s addressing model — a slice is already a first-class folder, so the addressing exists; what does not is the decision about where a round lives and how the two levels compose.

**SETTLED 2026-09-06 by the same design.** Packages are per-slice because the slice is the only level, so this needs nothing built: the "BRD-level optional or question-capped" half dissolves rather than being implemented.

---

# Review ledger — opened 2026-09-06 by the whole-diff review of the ledger-closing commits

Three Opus reviewers ran over `7b47f23..ed4334c` on orthogonal dimensions — claims against the tree, contradictions and text the change falsified, and class completeness. They returned **54 raw findings, ~35 distinct**. Everything attributable to that diff is fixed in the commit that carries this section. What follows is what the review surfaced that the diff did **not** introduce — pre-existing defects the review found while checking it.

Per **S18** these gate the release exactly as the BRD-route defects did. None is script-visible: all seven build gates were green with every one of them in the tree.

**Status, 2026-09-06 (later the same day): R-1 through R-5 are all closed.** Each entry below records how. None was script-visible — all seven gates were green with every one of them in the tree, before and after.

## R-1 — `/ready` has no non-emptiness guard on `requirements[]`, where `/epics` has exactly that guard

**CLOSED** — an empty `requirements[]` now prints `not assessed — PRD states no requirements` instead of a 0-of-0 roll-up that reads as 100%, raises it as a BLOCKER readiness finding (the severity is what makes it settle the verdict under the reviewer's own rubric), and settles at `NOT-SUPPORTED`. A middle attempt reused the template's `"derived (coarse)"` alternative, which asserts a derivation that never runs here, and specified a cap with no mechanism at either station; `readiness-reviewer` applies the same cap independently, so a dispatch that skipped the caller cannot produce a `SUPPORTED` either.

**The first attempt at this was wrong and is worth recording.** It made the emptiness a hard stop, copied from `/epics`, which refuses it. A review caught that `dev-workflows:workflow-states` has rungs — `Open` (*PRD stub*), `Problem stated` (*PRD with Problem/Goal*) — where a PRD legitimately states no requirements, so the stop would have refused the run on exactly the early-stage PRDs `/ready` exists to report on. The remedy was imported across a boundary that was never checked: refusing is right for an **authoring** command whose output would otherwise contradict nothing, and wrong for a **reporting** one whose contract is to describe what it finds.

`/epics` refuses an empty ground truth outright, naming the reason: proceeding "would let every Epic pass coverage vacuously". `/ready` builds the same `requirements[]` ground truth from the same PRD and has no such test; `readiness-reviewer` refuses only on the field being *absent*, not empty. A PRD stating no requirement IDs yields a 0/0 = 100% coverage roll-up and can return **SUPPORTED** — the verdict `/implement` is offered on. Same class as BRD-1, same shape as the `/brd-split` and `/brd-interview` gates fixed this week, in two commands that read one file and disagree.

## R-2 — `/brd-reconcile` never gates on a reader digest that yielded nothing

**CLOSED** — `BRD_RECONCILE_EMPTY_DIGEST`, built on the presence facts the digest already recorded and nothing consumed. It reads the verdict written in section 2: `approved` beside three empty sets is a customer who agreed, and is recorded as the approval it is; any other verdict, or a section 2 that is absent or gives none, is a review contradicting itself or a parse that failed. A first version keyed on all twelve sections being `stated-none`, which the schema makes unreachable — sections 1, 2, 9 and 11 always carry content — so every clean approval landed in the stop.

`BRD_RECONCILE_UNCONFIRMED`, `UNDISPOSED_CORRECTION` and `UNSWEPT` all count *undisposed* items, so a `customer-review-reader` return with zero decisions, zero `required_changes` and zero challenges satisfies all three vacuously: the run freezes zero `[CD#n]`, sweeps nothing, writes a reconciliation record and reports success. The presence half already exists and is unused — the digest records each of the twelve sections as `present`, `stated-none` or `absent`, "two facts that are never merged", and nothing branches on it.

## R-3 — `/brd-package` step 7 is vacuous on zero round files

**CLOSED** — `BRD_PACKAGE_ROUNDS_NOT_ON_MAIN`, with the round set **derived from `decisions.md`'s `round` fields** rather than from the `interview/` listing, and `require-on-main` per round. Deriving the set is what makes a partial merge visible: enumerating the directory finds the rounds that landed and never learns a third was owed, which is the case the gate exists for. A first attempt tested only *zero* round files and enumerated the directory — it would have passed the partial merge it was written to catch.

Step 8's `BRD_PACKAGE_NOTHING_TO_REVIEW` gained a sibling too: it read a BRD with no `[VD#n]` as **finished** ("every question its rounds asked was settled from verified findings"), which is right for a BRD that was interviewed and wrong for one that never was. It now tests `interview/` and names `/brd-interview` where the directory is empty.

*"Stop unless every question in every round carries either a terminal disposition or the holding state"* is vacuously true with no round files. Largely covered by step 8's `BRD_PACKAGE_NOTHING_TO_REVIEW`, which does test presence — the live hole is a `decisions.md` carrying `[VD#n]` whose round records never merged. Note this rests on the same "one commit stages the siblings" assumption `--no-code` falsified for `/brd-split`; `/brd-reconcile` carries an explicit paragraph qualifying it and `/brd-package` does not.

## R-4 — `--docs <path>` is declared by the shared reference for nine consumers and parsed by one

**CLOSED** — implemented in the other eight rather than narrowing the contract, each with the rule that the flag and its value are stripped together before any remaining-argument classification.

**It took three passes, and the reason is worth keeping.** The first put `--docs` in eight Usage lines; four of those commands had **no flag-parsing step at all**, so the flag would have been read as a positional token — which in `/create-ard` and `/specify` trips their one-address refusal and stops the run, and in `/create-prd` and `/release-notes` is read as the address or as `@idea.md`. A review caught the first two; a mechanical sweep of **every flag every command documents against where it actually parses it** caught the other two. That sweep is the thing that should have been run first: the finding was never "two commands are missing a rung", it was "a documented flag with no parsing site is a class", and the same sweep confirms the remaining commands are clean (`--rules` in both guideline reviewers is consumed at its dispatch, and the three `/brd-*` commands that name `--no-docs` do so to say they refuse it). Narrowing would have left an operator whose docs are not at `$DOCS_PATH` able only to turn grounding off, which is BRD-2's shape.

`workflows-core:docs-grounding` §1's *Flags first* rung declares `--docs <path>` for all nine of its consumers. **Only `/idea` parses it.** The other eight take `--no-docs` and nothing else, and several then classify `$ARGUMENTS` "minus every recognised flag" — so `--docs` and its path argument fall through into the address classification. This is BRD-2's shape and slightly worse: the off switch exists everywhere, the point-it-elsewhere switch exists once, and the shared reference documents it as though it existed in all nine. An operator whose docs are not at `$DOCS_PATH` can only turn grounding off.

## R-5 — `phase-handoff.md` §4.0's register classifies 13 artifacts against a `deliverable_paths` universe of ~30

**CLOSED** — the register is now derived from the `deliverable_paths` declarations rather than from memory, and carries every artifact they name, including the ones with no reader. It also states the rule the last two increments kept re-deriving: **a reader that stops on an artifact gates that artifact**, because a stop is only as reliable as the ref it reads.

§4.0 now says outright that it classifies the artifacts whose class a producer has had to resolve, rather than everything the family hands off, and that an unlisted path is unclassified rather than unread — so a producer is no longer misled. Every artifact those declarations name now carries a row, including the ones with no reader found — listed rather than omitted, so absence from the table means unclassified and never unread. Most ride in a set that already contains a gated path and are carried by the strongest-class rule, which is why nothing has misbehaved yet — `/brd-ground --no-code` was the first set containing no classified path at all, and it is what exposed this.

## Recorded, not counted as defects

- The three reviewers each independently confirmed the `/frames` consent-array contradiction, which is the strongest signal in the set that the dimensions were genuinely orthogonal rather than three passes at the same reading.
- `grounding-verifier` gained `STALE_INDEX` rather than having the claim deleted from three files: `/brd-ground` Phase 7 already handled that status with a well-reasoned remedy the agent could never trigger, so the contract was the half that was wrong.


---

# Engagement ledger — opened 2026-09-07 from a second live engagement

Reported by an operator running the BRD route against a live customer engagement, on the **published
pre-split** plugin. Each entry records what was reported, what triage against the tree at `702e066`
actually found — **two of the three reports were partly misdiagnosed, and the corrections change the
fix** — and where it sits relative to gate 3.

Per **S18** these gate the release exactly as the BRD-route and review defects did. None is
script-visible: all seven build gates are green with every one of them in the tree.

## E-1 — a verifier outcome is never checked against the verdict the verifier re-derived

**CLOSED 2026-09-07** — shipped in `product-workflows` 2.2.0 and `workflows-core` 1.2.0. `grounding-format` §8 now normalises an `agree` or `extend` carrying a differing `own_verdict` to `contradict`, acted on by the branch that believes the re-derivation and recorded rather than silent; `unprovable` is explicitly never normalised. §2.1 names the record's field set **closed** — §2's fields plus `outcome` and `notes` — and `grounding-verifier` says the same from the emitting end. `/brd-ground` Phase 7 reconciles before acting, Phase 8 writes the closed set, and the Final report names every normalisation or an explicit "none". `/brd-split` gained a fourth Phase 0 test and `/brd-interview` a third, refusing a block that carries a key the format does not define; the stop names the hand repair rather than `--rebaseline`, which would re-derive a verified corpus to delete a line no command wrote. `/brd-package` gained nothing — it has no findings gate, and a `--rebaseline` that moves the findings forces a new interview round through `/brd-interview`'s check.

**Bounded fix, was sequenced BEFORE gate 3.**

**Reported as:** `/brd-ground` never reconciles a finding's `verdict:` with its verifier's verdict, so
every `contradict` leaves the record stating two verdicts at once. Three corpora were counted by hand
— 62 findings in a parent BRD's code grounding, 19 of 44 in a slice's design grounding, 51 of 142 in
a slice's freshly-ground code grounding.

**Triage: the central claim is false, and two real defects sit underneath it.** Phase 7's `contradict`
branch already does exactly what the report proposes as the fix — *"the finding is rewritten, and the
rewrite retains the same id. Replace the finding's `verdict` and `evidence` with the verifier's
`own_verdict` and `own_evidence`, and keep a one-line note of the pre-rewrite verdict"* — and has done
since `/brd-ground` was first added (`e7aac79`). The report's "withhold `SUPERSEDED`" point is
likewise already honoured: that branch never uses it.

**(a) Phase 7 never validates `outcome` against `own_verdict`.** `grounding-verifier` returns
`own_verdict` **unconditionally**, on all four outcomes. §8 defines `agree` as *"reaches the same
verdict"* and `extend` as *"the claim holds, but…"*, so either arriving with a differing `own_verdict`
is the agent violating its own contract — and Phase 7's `agree` and `extend` branches both say *keep
the finding's verdict* with no check. Nothing detects it, and the written record shows only
`outcome: agree`. **The disagreement leaves no trace**, which is worse than the reported symptom
because it is invisible rather than visibly contradictory.

**The report's remedy is wrong on one branch and must not be applied blanket.** Normalising *any*
disagreeing outcome to `contradict` would break `unprovable`, where `own_verdict: NOT-PROVABLE`
differs from the finding's verdict **by definition** and Phase 7 deliberately keeps the finding's
verdict — *"the verifier's own search settling nothing either way is not the same as it being
wrong."* The normalisation belongs to `agree` and `extend` only.

**(b) Nothing validates a written finding block against the format it must match.**
`workflows-core:grounding-format` §2.1 **does** fix the serialisation — `outcome` and any verifier
`notes` follow §2's keys, and `own_verdict` is not among the fields to write. So a corpus carrying a
`verifier:` block with a second verdict is a writer emitting a field the format does not define. The
format is right; nothing enforces it. That is BRD-6's family one level up, and BRD-6's own lesson
applies — fixing the file's writer without fixing the agent template the model actually copies leaves
the defect one hop upstream.

**The best idea in the report is its cheap extension.** `/brd-split`, `/brd-interview` and
`/brd-package` all gate on *"every finding carries a verifier outcome"*, which a finding stating two
verdicts satisfies, because an outcome is present. Extending it to *"and no finding's outcome
disagrees with its own verifier"* is BRD-1's presence-relation lesson applied again, and would have
caught all three corpora at the next command instead of at customer-package time.

## E-2 — the bundle is never checked for whether an identifier citation resolves

**CLOSED 2026-09-08** — shipped in `product-workflows` 3.1.0 and `workflows-core` 1.3.2. `bundle-packaging.md` §6 owns a citation-resolution check that `/brd-package` Phase 8 rule 8 runs over the assembled bundle beside the plugin-free scan; `grounding-format` §6.3 gained the correctness half of the class-4 citation rule. Three relations — every identifier reference resolves inside its own source package's corpus; a class-4 `[DG#n]` cites a `[CG#n]` about the same requirement; every bundle-referencing markdown filename token names a document that is in the bundle. Three stops: `BRD_PACKAGE_DEAD_CITATION`, `BRD_PACKAGE_CITATION_MISMATCH`, `BRD_PACKAGE_CORPUS_UNREADABLE`.

**Four things the report could not have known, each found by reading the tree and each changing what was built.** `[SR#n]` had to be exempt entirely — the self-review is excluded by rule while its content reaches the customer *filtered* by id, so a check without the exemption fires on every package. A prerequisite package is copied in wholesale with its own corpus numbered from 1, so the resolution set partitions **on the `<BRD-KEY>` each bundle document's filename carries** — chosen over partitioning by subtree because the discriminator then travels with the document and a flattened bundle partitions identically, where a subtree test would resolve every id against one corpus **and pass**. Relation 3 had to be scoped to tokens that actually claim to be bundle references, or a correct `docs/api.md:12` in a finding's `evidence` refuses the bundle. And `design-grounding.md` is legitimately written as *"a short note when design grounding was skipped"*, so a present, non-empty, zero-id corpus is ordinary — the parse-failure stop is drawn on **record-shaped content**, not on a zero count.

**The report's checks 3 and 4 collapsed into one relation.** A working filename is not in the bundle, so it fails the same test a dead one does, and one mechanism cannot drift from itself.

**What it deliberately cannot see, stated in §6.4:** a reference that *describes* a bundle document where rule 1 requires it to *name* one; a citation resolving to the right id but wrong in a way relation 2 does not test; an identifier class with no corpus row; the delivery note, which is not a bundle document; and a corpus whose records are *all* malformed identically, which reads as empty — the run still stops, as dead citations.

**Known consequence, recorded because it is not a defect:** relation 2 will refuse bundles that ship today, and the repair is by hand, because the plugin still has no supported mechanism for narrowing a parent's verified findings to a slice's claimed subset. That gap remains its own entry below.

**Bounded fix, sequenced after gate 3.**

**Reported as:** `/brd-package` runs a plugin-free scan and a de-Obsidianising pass, and correctly
exempts identifiers from the scan because `[BR#n]`/`[CG#n]`/`[DG#n]` are how a returned review cites
the package. Nothing then checks that they land. Three failures were observed in shipped bundles: 16
of 17 class-4 `cites` resolving to a finding about a *different* requirement; 11 references naming ids
above the highest the corpus contains; and a guaranteed dead reference, because
`bundle-packaging.md` §1.1 excludes the self-review while bundle documents name it in prose, which
§2's rule 2 does not govern.

**Triage: real as reported.** There is no citation-resolution check anywhere in `/brd-package` or
`bundle-packaging.md`. `workflows-core:grounding-format` §6.3 requires a class-4 `cites` to be
**present** — *"A `[DG#n]` of this class carrying no `[CG#n]` citation is incomplete"* — and nothing
requires it to be **correct**. The report's four checks are sound, and its own points 3 and 4 are
rules the plugin already states and nothing enforces. The single highest-value test is its point 2:
for a class-4 `cites`, require the cited finding's `claim` to name the same `[BR#n]` as the citing
finding. Both values are already in the records being copied.

**One severity correction: the mechanism that produced the worst failure is retired.** The 16-of-17
case had a slice carrying its **parent's** design findings, which requires the parent to have been
ground. Slice-first grounding removed root grounding entirely — a root is never ground, so there are
no parent findings for a slice to carry — and the sibling re-cut explicitly moves no findings. That
corpus came from the documented hand deviation recorded in BRD-5, on a pre-split tree. The defect
stays real: existing bundles carry it, and a bundle check must catch a broken citation however it got
there. It is not a live regression source.

**Recorded as a separate gap, not folded in:** the plugin has no supported mechanism for narrowing a
parent's verified findings to a slice's claimed subset. Under slice-first that operation should no
longer be needed; if a live route still reaches it, that is its own entry rather than part of this
one.

## E-3 — the route has nowhere to record a defect in the code

**Architectural; own brainstorm and spec, sequenced after gate 3.**

**Reported as:** `/brd-ground` spends its whole effort reading code at pinned commits and routinely
establishes that the code is broken — an active regression, a missing index the code assumes, a write
path that never sets a column. `brd-format.md` §4's `[DEF#n]` log is for **requirement** defects, and
Phase 8 writes findings, the derivation matrix and documentation divergences, none of which is a
defect record. So a code defect lands in a decision's `argumentation` as prose, where nothing consumes
it: two instances in one register, both asserting the defect *"is recorded"* when nothing held one,
both surviving drafting, the round record and a first adversarial review.

**Triage: real and correctly diagnosed.** `brd-format` §4's resolutions are every one of them about
the requirement or the document — `customer-amended`, `withdrawn`, `resolved-by: [CG#n]`, `open` —
and note that third one's direction: a grounding finding can **settle** a requirement defect, so
findings already flow *into* that log and nothing flows out. A grep for any code-defect record across
`plugins/product-workflows/` returns nothing. `decision-register-format` §2 makes `argumentation`
mandatory free prose, which is exactly where the fact goes when there is nowhere else.

**Two separable items, and the order matters.**

- **E-3a, the capability gap** — no code-defect record exists. A new artifact, an id namespace, a
  writer, a resolution vocabulary, and consumers that treat an entry as work.
- **E-3b, the correctness bug** — a decision's argumentation can assert a defect *is recorded* while
  nothing holds one, after which the register reads as handled. This is the half that makes it a
  defect rather than a feature request, and the half that can reach a customer, since the register's
  content feeds the bundle.

**The proposed gate is the right idea in the wrong order.** It treats the symptom: the operator wrote
prose because there was nowhere else to write. Build E-3a and the pressure the report itself names
("one register field removes that pressure") is gone, after which the gate guards against regression
rather than standing alone. Shipping the gate first is a refusal with no destination — the dead-end
shape `workflows-core:grounding-format` §6.1 already forbids for `NO_INDEX`.

**Measure the gate's trigger before building it.** `CLAUDE.md` records a measured rejection of a
prose-proxy check (stop routing), where every proxy tried either fired on correct content or caught
none of the real defects. **This one is not that class, and the difference is the reason it is worth
building:** it tests an assertion against a checkable artifact, which is the shape of checks 8, 11, 15
and 16 that all shipped. Only the trigger phrase is prose-fragile — *"recorded as a defect against
it"* against *"recorded as such"* — so the candidate pattern is measured against the tree first, as
this repo requires of any widening.

**A requirement on E-3a, carried from the report's second-order point:** the record needs a field for
a **scope condition that cannot be settled yet** — "whether the new surface renders this is a property
of code nobody has written". Without one, a decision is forced to assert the repair is in scope and
contradict its own stated boundary, which is what happened. That is a requirement, not a
nice-to-have.

**Recorded because it is the strongest argument for the gate:** this defect was found because the
register created to fix it contained the same unrecorded claim.

**Two constraints to settle early, noted 2026-09-08 before the brainstorm and not obvious from the entry above.**

- **The `product-workflows` blurb is the binding constraint on this increment specifically.** It stands at 988 of 1024 characters and warns on every `validate-catalog.py` run (G3-4). E-2 and E-4 were a gate and a wording change and needed no blurb text; **E-3a is a capability** — a new artifact with its own id namespace — which is exactly the kind of change a `description` is expected to mention. With 36 characters left, that edit must **trim**, not append. Decide what comes out at design time, not at the version bump, or the increment stalls at its last step.
- **E-3a may want to be designed alongside the narrowing gap, not after it.** E-2 shipped a check that refuses a bundle whose class-4 citations name the wrong requirement, and the repair is by hand because the plugin has no supported way to narrow a parent's verified findings to a slice's claimed subset — its own open entry. If E-3a gives the route a place to record code-level findings with a resolution vocabulary, the two problems touch the same records. Worth one question at the start of the brainstorm rather than a discovery in the middle of it.


---

**CLOSED 2026-09-08** — both halves, on branch `iv-gu/code-defect-record`. `product-workflows` 3.3.0, `workflows-core` 1.3.3. Spec `docs/superpowers/specs/2026-09-08-code-defect-record-design.md`, plan `docs/superpowers/plans/2026-09-08-code-defect-record.md`.

**What shipped.** `references/code-defect-log-format.md` defines `[CDF#n]` in `<BRD-dir>/code-defect-log.md` — slice-owned, unlike the parent-owned `[DEF#n]` requirement log. Each entry cites one verified `[CG#n]` for the behaviour and names its **intent basis separately**, because `workflows-core:grounding-format` §1 makes grounding adjudicate a claim and gives it no authority over the code's own intent. Five dispositions, no `fixed` one. `/brd-interview` is the only writer: Phase 6 offers to raise an entry on a **structural** trigger — the decision's own `evidence` holding a `REWRITTEN`, `AMENDED` or `FALSE-FRIEND` finding — and a later round may re-disposition an entry already on file. `decision-register-format` §1 gained a twelfth field, `defects`, deliberately not in `evidence`, which §6's will-change rule inspects. E-3b's backstop is `brd-package-reviewer`'s sixth hunt class.

**The design reversed itself once, on the operator's argument, and the reversal is the important part.** An earlier draft excluded the log from the customer bundle as delivery-side bookkeeping, and paid for it with a §6.3 exemption plus an inverse stop-the-run rule. A defect disposed `in-scope` **is** the delivery boundary — the repair has to happen inside the PRD's scope or the feature cannot ship — so the customer agreeing to that scope must be able to see it. The log ships (parts 6, 8 and 11 of the prompt), `[CDF#n]` is an ordinary ninth citation class with an ordinary corpus, and **both special cases were deleted**. E-4's repo-first route had already made the concealment illusory: a customer who pulls the specs repository sees the folder anyway, so the rule held on one delivery route and failed silently on the other.

**The prose-trigger gate this entry anticipated was measured and NOT built.** The tree holds two `argumentation:` examples in total and no corpus of real registers, so the measurement that justified checks 8, 11, 15 and 16 cannot be produced for it. Do not re-propose it without a corpus.

**Cost, recorded because it is the reason this class keeps recurring.** Roughly two dozen glob-coverage defects were fixed across the branch — prose deriving an obligation from an enumeration the change grew. Three were functional rather than cosmetic: the reviewer's Output schema would have **rejected** its own new class; `/brd-package` never handed the reviewer the log at all while its own text demanded it supply the contract exactly; and two sweep-scope tables would have let a write reach a disposition the operator owns.

---

## E-5 — a `[CDF#n]`'s `blocked_on` is outside `/brd-reconcile`'s propagation sweep

**CLOSED 2026-09-08 in `product-workflows` 3.3.3 — and the measurement falsified most of this entry before the fix was written.** Three results, none of them derivable from the text below.

1. **"Goes stale invisibly" is false inside the parent tree.** Phase **11**'s stale cross-reference sweep — not Phase 10 — names *"the code-defect log"* in its scope, searches every changed id as text whitespace-tolerantly, and roots at *"the parent's folder — the source-owning BRD's directory and every slice inside it."* A `code-defect-log.md` hit already took `needs-a-human`, whose stated reason is verbatim E-3's rule. The entry named the wrong sweep and therefore the wrong severity.
2. **`prerequisite` is a third cross-BRD pointer and is deliberately outside both sweeps.** A `will-change` finding stays a true record of its pinned commit and is superseded by a later finding at a later commit (`workflows-core:grounding-format` §5) — there is nothing for a sweep to reopen. So this was one field, not three. That distinction now ships beside the fix, because it is the test for any future widening: **`blocked_on` moves a *disposition*, which is a position, and reopening positions whose ground has shifted is what these sweeps are for; `prerequisite` moves nothing.**
3. **The design question the entry called open was already answered.** *"Who re-settles it, through which channel"* — `needs-a-human`, which *"travels into what still needs a human"*, a section of `reconciliation-<date>.md` that the final report prints **in full**. No new channel was needed and none was added.

**So the real gap was one shape: a `[CDF#n]` in a dependent BRD outside this parent's tree.** Phase 10 reaches such a BRD (its declared-dependents scan covers `specifications/` and three levels down) but walks decisions and `[AS#n]` only; Phase 11 reaches the log but stops at the parent. **The fix reuses both**: Phase 11's *first* search — the literal-id one — also runs over Phase 10's already-resolved swept set. No new traversal, no new outcome, no fifth disposition (Phase 10's four are closed by design).

**Two claims moved with it, in the same change, because a widening that leaves its own justification standing is the defect class this repo tracks.** The sweep's opening now says the parent root bounds everything *except* search 1, and *"the guard is why this sweep's root being the parent's folder is safe"* became **writing root** — since search 1 now reads wider than the sweep writes. **The write surface deliberately did not move**: outside the parent the only outcomes are `still-true` and `needs-a-human`, never `updated`, so the cross-BRD write guard's own table stays true as written. The second search does not follow either — it cannot be reduced to a pattern and needs a reader who knows what the old position claimed, which is affordable over one parent and is not over the tree.

**Carried out as its own entry, deliberately: E-8.** The entry's recommended candidate answer assumed `/brd-interview` would re-ask; it does not read the reconciliation record at all. That is consistent rather than broken — but if it *is* wrong, it is wrong on the within-parent common path first, so it is decided there and not under this entry's exotic case.

---

### The original entry, as filed


**Parked deliberately during E-3, not a slip.** `code-defect-log-format.md` §5 gives `blocked_on` the same `<BRD-KEY>/<decision-id>` shape as `conditional_on`, but `/brd-reconcile` Phase 10's propagation sweep walks only records carrying `conditional_on`. So a `[CDF#n]` blocked on another BRD's decision goes stale invisibly when that decision moves — verbatim the failure `decision-register-format` §5 argues `conditional_on` exists to prevent.

**Why it was not folded into E-3.** A sweep that *finds* a stale `blocked_on` needs a writer for it in `/brd-reconcile`, and E-3 closed that command against unilateral writes to the log precisely because the operator owns every disposition and the customer channel must not reach one. So the fix is a design question — who re-settles a scope condition when its prerequisite moves, and through which channel — not a wording change. It needs its own brainstorm.

**Blocks release under S18.** It is a known defect in shipped behaviour.

**Four things noted 2026-09-08 immediately after E-3 merged, none of them derivable from the entry above.**

- **There are now TWO closed channels, not one, and the brainstorm must open by naming both.** E-3 closed `/brd-reconcile` twice over: its section-12 correction table gained a `refused-with-reason` row so a *customer's* correction against a `[CDF#n]` is surfaced to the operator rather than applied in place, and Phase 11's structured-record carve-out gained a fourth row so the propagation sweep's own `updated` outcome cannot write a disposition either. Both were deliberate and both are right. So "let the sweep write it" is not a small widening — it reopens the hole two separate rules were just written to close.
- **The strongest candidate answer already exists in the tree and should be the brainstorm's starting point rather than a mid-session discovery.** E-3 taught `/brd-interview` to **re-disposition** an existing `[CDF#n]` in a later round (`disposition` and `blocked_on` only; `id`, `statement`, `behaviour`, `intent`, `intent_basis` and `round` are immovable). So the shape that fits the existing writer model is: the sweep **reports** a stale `blocked_on` and writes nothing, and the operator re-settles it in the next `/brd-interview` round. That preserves "one writer" and needs no new channel. Test it against the case where no further round is planned before packaging — that is where it may fail.
- **Measure whether this is live before designing for it, the way E-2's severity correction had to be.** A `[CDF#n]` reaches the sweep only where its `blocked_on` carries the **qualified** `<BRD-KEY>/<decision-id>` form; `code-defect-log-format.md` §5's other sanctioned spelling is prose naming no bracketed identifier, which has nothing to sweep and never goes stale in this way. So the defect's whole surface is qualified-form entries under a prerequisite BRD whose decisions can move — the same precondition `conditional_on` already has. It may be narrower than the entry above implies.
- **Settle G3-4's remaining open question first.** Its `/prd-ground` legacy-fallback bullet is marked *reachability unproven*: a folder whose `prd.md` is present but does not assert what the branch expects. If it proves reachable it is another blocker, and it is bounded work. Knowing that before E-5 is planned beats discovering it mid-increment — the same argument this ledger already makes for measuring a gate's trigger before building it.

---

## E-8 — a `needs-a-human` item has no mechanical carry-forward into the next interview round

**DECIDED 2026-10-28 — the trigger widens (feature-gaps review BRD-G1, batch B25, product-workflows 3.58.0).** `/brd-interview`'s re-disposition trigger now takes an entry the latest reconciliation record of any slice under the parent flags `needs-a-human`, by the `[CDF#n]` `/brd-reconcile`'s record now names for such a hit. What that leaves open, the no-further-round case below first, is `docs/superpowers/to-fix.md` D31.

**Raised 2026-09-08 while measuring E-5, and deliberately not folded into it.**

`/brd-reconcile`'s stale cross-reference sweep sends a hit it may not correct to `needs-a-human`, which *"travels into what still needs a human"* — a section of `reconciliation-<date>.md`, printed **in full** in the run's final report. For a `code-defect-log.md` hit that is the whole channel: **`/brd-interview` does not read the reconciliation record**, verified — its only `reconciliation` mention is an unrelated `[DG#n]` sense — and its re-disposition trigger fires on an entry still `open`, or `conditional` on a `blocked_on` **this round has settled**. A `blocked_on` settled by *another* BRD's reconciliation is neither. So the operator carries it between runs by reading a report.

**This is very possibly correct, and the entry says so.** The section is named *what still needs a human*; it exists precisely to hold what no command may act on, and E-3 wrote two carve-outs to stop a sweep driving a disposition. Teaching the interview to prompt from another command's sweep output is adjacent to reopening that, and needs its own argument rather than inheriting one.

**What has to be decided, and on which evidence.** Whether a report line is a strong enough guarantee that a `conditional` `[CDF#n]` is re-settled before packaging — or whether the trigger should widen to include an entry the last reconciliation flagged. **Decide it on the within-parent common path**, which has behaved this way since E-3 shipped; E-5's cross-parent case is the exotic instance and would mis-size it. Test the answer against the case the E-3 notes already flag: **no further interview round is planned before packaging**, which is where a report-carried item is likeliest to be lost.

**Not an S18 blocker as filed** — nothing misbehaves, and the item does reach a committed artifact and the operator. It is a question about the strength of a guarantee.

---

## E-6 — `/prd-ground` is the one PRD-reading command that does not know the legacy PRD filename, and it stops the operator with a remedy they cannot perform

**RETIRED 2026-09-08 without implementing the resolver — the operator's call, on reachability, and the reasoning is recorded so it is not re-derived.** Every finding below is reachable only on a specs repo written before the artifact filenames lost their keys and never renamed since. Traced per finding rather than assumed as a class: the `/update-prd` ↔ `/create-prd` loop needs `/create-prd` to *find* a PRD in order to redirect, and on a current tree with no `prd.md` it finds nothing and authors one; the `<KEY>_*.md` glob collision sits in a fallback that fires only where the ref carries no `prd.md`, and on a current tree that glob then matches nothing. So the population is exactly the set of un-renamed pre-rename trees, which the operator — the only party known to have held one — reports is empty and would in any case fix by hand, with a brainstorm, against the tree in front of them.

**What was taken instead, because the alternative was leaving a false promise standing.** `addressing` §5 said the fallback meant a user "need never" rename, unqualified — and **this entire spec is derivable from that sentence**, which is how it was derived. §5 now states the boundary: the fallback covers the folder name and nothing inside it, and a pre-rename tree renames its own artifacts. Shipped in `workflows-core` 1.3.4. Three commands contradicted the narrowed rule and moved with it (`product-workflows` 3.3.1): `/create-ard` and `/specify` dropped the key-globbed PRD fallback at their `require-on-main` gates — a fallback that matched nothing on a current tree and, on the one tree it was written for, also matched that tree's `<KEY>_ARD.md` — and `/create-prd` step 6 dropped its claim that a pre-rename file is identified by `kind: prd`, a field the same change introduced. **The live defect the investigation surfaced was therefore fixed; only the legacy tolerance was declined.**

**Kept for its archaeology, not for its plan:** `docs/superpowers/specs/2026-09-08-legacy-artifact-resolution-design.md`, marked not-implemented — kept in the tree until 2026-09-23, and in history since (`git show 62e791e8:docs/superpowers/specs/2026-09-08-legacy-artifact-resolution-design.md`). Its §1 records how a rule that existed, and was deliberately kept by `75029fe`, was deleted by `469c656` under the judgement that *"Duplicating those is not the drift risk that duplicating a key grammar was"* — and what the duplication then cost. That is worth keeping whether or not the resolver is ever built.

**The reachability lesson, stated plainly because this session paid for it twice.** G3-4 asked a reachability question and the answer closed it. E-6 was opened out of that same investigation and was *not* asked the same question — the design was measured, specified and approved before anyone counted the trees it would serve. Ask it first.

---

### The original entry, as filed

**Found 2026-09-08 while settling G3-4's reachability question**, which asked about a different half of the same split and turned out to be unreachable.

**The defect.** `/prd-ground`'s legacy-fallback split (Phase 0, the `route:` resolution) decides between the idea route and the interrupted-intake branch on **`prd.md` being present and asserting `kind: prd`**. A genuine legacy idea-route folder — `specifications/<KEY>-<slug>/` written before `1da7480` (2026-08-31) — holds `idea.md` and **`<KEY>_<slug>.md`**, because that commit renamed the artifact at the same time as it introduced `kind:`. So `prd.md` is **absent**, the split takes the interrupted-intake branch, and the run stops with:

`PRD_GROUND_NO_INVENTORY: <BRD-KEY> has no brd/brd-inventory.md and no brd-link.md naming a parent — this reads as an interrupted intake, not a slice. Re-run '/product-workflows:brd-intake <BRD-KEY> @<brd-file>' to complete it`

That operator has an idea-route PRD folder. There is no `<brd-file>`; there never was one. **The remedy names a command whose required argument the addressee cannot supply** — the same family as E-4 (a package telling repo-pullers to unzip an archive) and E-3b (an argumentation citing a record nothing holds).

**Measured, not assumed: `/prd-ground` is the only one of five.** `grep -rln '<KEY>_<slug>' plugins/ --include=*.md | grep -v CHANGELOG` returns `create-prd.md`, `specify.md`, `create-ard.md`, `update-prd.md` and its docs page. `/prd-ground` returns **zero** hits. Every other command that reads a PRD already handles both filenames; `/create-prd` step 6 is the worked example — *"A specs repo written before the rename holds `<KEY>_<slug>.md` instead"*.

**Scope, so severity is not overstated.** `/prd-ground` on the idea route is optional and ungated, so nothing on the BRD route is affected and no gated artifact is involved. It misroutes an idea-route operator working on a pre-rename tree, and `workflows-core:addressing` §5 exists precisely so those trees keep working (*"the fallback means they need never do it"* — rename their folders).

**The fix is a widening with existing precedent, not a new rule**: the split tests for the PRD **either way**, exactly as the other four commands do. What needs care is the `kind:` half — a pre-rename file predates `kind:` too, so a test demanding `kind: prd` of the legacy name would refuse the very artifact it just learned to find.

**Blocks release under S18.** A known defect in shipped behaviour.

**WIDENED 2026-09-08 during its own brainstorm — this entry under-counted the class, and the measurement is the correction.** `/prd-ground` is not the only one of five. The grep this entry cites returns `/update-prd` twice, but both hits are the **revision-archive** naming (`revisions/<KEY>_<slug>_<YYYYMMDD>.md`), not legacy-PRD reading: its step 4 says the PRD *"is the `prd.md` in the folder step 3 resolved — the only copy there is, and therefore authoritative without a test."* So `/update-prd` does not know the legacy name either, and its `UPDATE_PRD_NO_PRD` remedy names `/create-prd`, which **does** find the legacy file and redirects back — **a closed loop in which neither command can run.** Two further defects sit in the very commands this entry named as the correct precedent: `/create-ard` and `/specify` fall back to a `` `<PRD>_*.md` `` entry, which matches the legacy ARD `<PRD>_ARD.md` — `1da7480`'s own diff names it — and `_ARD.md` sorts first, so the PRD gate gates the ARD; and `/create-prd` says the legacy file is identified by `kind: prd`, a field that same commit introduced **alongside** the rename, so no legacy file can carry it. `/epics` refuses outright, and `/release-notes`, `/document`, `/ready` and `/implement` degrade silently. The shared authority carries the false premise as well: `coverage-ledger-format` §5.1 defines a legacy idea-route PRD folder as one *"holding `idea.md` and `prd.md`"*.

**Root cause, located.** `75029fe` kept the rule on purpose — *"`prd-source-resolution.md` keeps the `issue_type: ValueIncrement` check alongside the filename … which that check is what identifies inside it."* `469c656` then deleted that file, judging *"Duplicating those is not the drift risk that duplicating a key grammar was."* It was: what remained was three lines, not two, and the third was the legacy identification. Both callers lost it in the same commit.

**Design approved 2026-09-08** at `docs/superpowers/specs/2026-09-08-legacy-artifact-resolution-design.md` — one owner (`workflows-core:addressing` §3's new `resolve-artifact` entry point plus §5.1's closed legacy-filename table), ten consumers, four plugins. **The lesson this entry keeps paying for**: an enumeration written from memory is short, and only a sweep run against the tree is a count.

---

## E-7 — `relevant_for_release_notes` encodes a premise its owner rejects

**CLOSED 2026-09-08.** Retired in `workflows-core` 1.3.5, `product-workflows` 3.3.2 and `docs-workflows` 1.1.2. `/release-notes` now has **no worthiness gate at all** — Phase 2 is *Plan + approval*, and the run's one refusal is `RELEASE_NOTES_NEEDS_KEY` on an address that does not resolve. **A value left in an existing PRD is inert**, the operator's call: `/create-prd` only ever wrote a `no` where someone confirmed one, so the population is effectively empty and a reader tolerance for a retired field is a claim with its own expiry date. Each of the three retirement sites records *why*, so the field is not reintroduced as an obvious-looking convenience.

**One defect fell out of it that had nothing to do with the premise.** `docs-workflows/docs/commands/release-notes.md` still documented the gate's *retired* implementation — that Phase 2 read the flag *"straight from the imported PRD frontmatter — never from the authored specs draft"* — which is exactly the instruction the command reversed when the import was cut, and which had made the stop permanently unreachable. **The command was fixed and its page was never swept**, so the page had been describing a broken behaviour for as long as the fix had been shipped. It is gone with the gate it described.

**Raised by the operator 2026-09-08 while approving E-6's design**, which had named the field's `/release-notes` worthiness gate as a defect surface. It is not one: **every PRD is relevant for release notes, so no field is needed for that.**

**Not a defect, and recorded as such.** Nothing misbehaves — `/create-prd` already defaults the field to `yes`, and `/release-notes` proceeds silently where it is absent. What is wrong is that the field exists at all: it asks a question with one answer, and the stop it feeds (`RELEASE_NOTES_NOT_RELEVANT`, overridable) can only ever fire on a value nobody should write. So this is a design change, not an S18 blocker, and folding it into E-6's legacy-resolution increment would have mixed two unrelated blast radii.

**Measured surface: nine sites across five files and two plugins, plus `CLAUDE.md`.** `workflows-core:prd-format`'s frontmatter block; `/create-prd`'s capture (*"defaults to `yes`; ask only …"*); `/release-notes`'s gate, its stop and its own rule sentence; `docs-workflows/docs/commands/release-notes.md` × 3; and `CLAUDE.md`'s `/release-notes` key invariant (*"an explicit `false` stops with `RELEASE_NOTES_NOT_RELEVANT` (overridable); absent proceeds silently"*).

**What the fix has to settle**, so it is not taken as a pure deletion: retiring the gate removes `/release-notes`'s only refusal, and `CLAUDE.md`'s own rule holds that **a rewrite which narrows a rule is a deletion and is itemised separately**. A PRD carrying `relevant_for_release_notes: no` on an existing tree must be handled deliberately — read and ignored, or read and reported — rather than becoming a field nothing mentions while the value sits in the file.

---

# Open after gate 3 — G3-1, G3-2, G3-3, E-2, E-3 and E-4 closed 2026-09-08; G3-4 stands as constraints; E-5, E-6 and E-7 opened

## E-4 — the package tells every reviewer to extract an archive, including the ones who pull the repository

**CLOSED 2026-09-08** — shipped in `product-workflows` 3.2.0. **The prompt now names no delivery route; the delivery note names the actual one.** They have different readers, and that is what settles which may assume anything: the note is a covering letter to a named customer whose situation the operator knows, while the prompt is handed on to a colleague, an agent, or whoever actually reviews — so a prompt naming a route is wrong for some of its readers about the first thing it tells them. The archive command left the prompt entirely; assembling an archive is a delivery-team action.

**The route is settled once, at the delivery note, and half of it is derived rather than asked** — the operator's refinement on the original entry, and better than what this entry proposed. The repository route exists only where the handoff's consent choice was **accepted**: a bundle on no ref is a bundle nobody can pull. So a declined handoff takes the archive route without asking and says why; an accepted one asks, recommending the repository. On that route **no archive is produced at all**, and the note carries the repository, the committed `bundle-<YYYYMMDD>/` by path, and the instruction to open the prompt there.

**The constraint that survived, and looks like an inconsistency until you see why:** even on the repository route the *prompt* must not name the specs-repo path. Rule 1 holds that a path is correct exactly once, in the directory layout one machine had. The note carries the path, the prompt carries filename search — the note says where to stand, the prompt works once you are standing there.

**This entry under-counted its own sites, twice.** It recorded three; there were nine, and the sweep after implementation found two more — rule 4's argument for filenames over paths, and the 200-word ceiling's, both *justifications* naming an attachment rather than statements about delivery. Rule 4's mattered: naming only the archive case read as though a committed bundle could be addressed by path, which is the one reading that breaks rule 1 for the route now recommended. **The pattern across this session is consistent — an enumeration written from memory is short, and only a sweep run against the tree is a count.**

**Raised by the operator 2026-09-08 while approving E-2. Recorded rather than folded in:** E-2's relations are mechanical checks over identifiers and filenames; this one needs an input the run does not have, and that is a design decision, not a check.

`bundle-packaging.md` §5 already states the bundle serves **both** delivery routes with one artifact — *"A customer with access to the repository pulls the bundle directly and needs nothing else. Everyone else gets one archive command."* The route is real and documented. **Nothing anywhere records which route a given package is taking**, so every site that mentions delivery assumes the archive.

**Site 1 is the defect; the other two are friction.**

1. **`commands/brd-package.md` Phase 6, Part 1's OS note, rendered unconditionally into the customer's own prompt.** It says *"extract the archive to a real folder before pointing anything at it: a file browser will show you the contents of a `.zip` without extracting it…"*, and Part 1's *what to put on the machine* line says *"the extracted bundle"*. For a customer who pulled the specs repo — **the common case, per the operator: most customers work in the same specs repository and already have every file** — that instruction names a file they were never sent, in the one document whose entire job is to be followable by somebody with no context and no plugin. It is the same failure class the de-Obsidianising pass exists to prevent: an instruction that looks actionable, is not, and gives the reader no way to tell which.
2. **Phase 8 prints the archive command unconditionally**, with an absolute path, at the end of every run. Harmless to a repo customer, but it is the run's only statement about delivery and it names one route.
3. **Phase 10's `choices:` array** offers *"Send it — the delivery note is printed above and the archive command is in the report"*, describing the archive as the thing that gets sent.

**What the fix has to settle first, which is why this is not a one-line edit:** the run cannot know the route, and the two honest ways to give it one differ in cost. Either the operator declares it (a Phase 0 question or a flag, which is one more thing to get wrong and one more state to document), or Part 1 is authored to cover both routes in one sentence and stops assuming — cheaper, no new input, and it makes the prompt correct for every reader at the cost of one clause a repo customer skips. The second is the better default on this route's own evidence, since every other Part 1 line is written to be true for every reviewer.

**Not a regression and not urgent:** the archive route works, and a reviewer who was in fact sent a zip is told the right thing. What is wrong is that the common case is documented as the exception.

## G3-1 — `dev-workflows/docs/reference/environment.md:11` lost `/prd-ground` from an enumeration

**CLOSED 2026-09-08** — the line now names `/prd-ground` alongside the glob. The class sweep was re-run across `plugins/` before the fix rather than after it, and this remained the only instance: every other surviving `/brd-*` mention is about the shared `brd` **prefix** — which `/prd-ground` does still carry on the BRD route — and each of those either names the command explicitly already or is correct as a statement about the route. That distinction is the durable one: the rename shrank the command **glob** and left the **prefix** sharing intact, so a sweep that treats the two as the same thing over-fires as readily as one that misses.

**Small, documentation-only, and an instance of gate 3's own signature defect class**, which is why it is recorded rather than waved through.

The line reads *"The same gate applies to the companion `product-workflows` plugin's `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, and **every `/brd-*` command**"*, describing the stop-and-offer behaviour on an unset `SPECS_PATH`. `/prd-ground` Phase 0 step 3 stops identically, with the same `choices:` array — verified — but it is named nowhere, and the `/brd-*` glob stopped reaching it the day the rename shipped.

**This is the glob-coverage regression class**: prose that derives an obligation from a glob the rename shrank, invisible to `grep -r 'brd-ground'` because the sentence never contained that string. Gate 3 found and fixed **fifteen** instances of it across three plugins; this one survived because the file was opened by neither the literal-name sweep nor the class sweep that followed. Found by the final whole-branch review's own re-run of the class sweep, after the fix wave — which is the argument for running that sweep again at the end rather than trusting the fix list.

Fix is one line: name `/prd-ground` alongside the glob. Nothing about a run misbehaves; a reader is simply told the gate applies to five commands where it applies to six.


## G3-2 — two build gates fail from the main checkout whenever a worktree exists under `.worktrees/`

**CLOSED 2026-09-08** — both scripts now exclude a `.worktrees/`/`worktrees/` directory **at the scan root**, each through the root-anchored mechanism it already had (`validate-catalog.py`'s `SKIP_PREFIXES`, `check-id-grammar.sh`'s `EXCLUDED_SUBTREES`). Anchoring is the whole of it: `worktrees` is an ordinary word, and a bare name-match at any depth would hide a real manifest or a real violation nested under any directory called that — the identical argument `SKIP_PREFIXES` already carried for `fixtures`. Each script gained a **paired** selftest case, and both pairs were proven to discriminate by running degraded implementations: with the exclusion removed the green case fails, and with the exclusion rewritten as an unanchored name-match the red case fails. Verified end to end by creating a worktree and re-running the three tree-walking gates from the main checkout — **0 errors where this entry measured 10**.

A general "skip everything gitignored" was considered and not taken: it would make two build gates depend on `git` being available and on the scan root being a work tree, which neither selftest's temporary fixture tree is. The named-directory exclusion covers the only way this state arises and adds no failure mode.

**Found during gate 3's merge, by the merged-result verification the finishing discipline mandates.** Not a defect the branch introduced, and invisible until someone uses a worktree.

`scripts/validate-catalog.py .` and `scripts/check-id-grammar.sh --root .` both walk the filesystem from the repo root **without excluding gitignored directories**. A git worktree at `.worktrees/<name>/` is a second full copy of the tree, so:

- `validate-catalog.py` reports **one ERROR per plugin** — *"plugin name '<x>' is already declared by .worktrees/…"* — because every plugin name now appears twice, plus a duplicate description WARN. Measured: 10 errors, 3 warnings on a tree with one worktree present.
- `check-id-grammar.sh` walks into `.worktrees/…/scripts/fixtures/`, whose **negative test fixtures deliberately contain dash-form IDs** (`[AC-2]`, `[SM-1]`), and reports them as live violations.

`check-docs.sh` is unaffected — it iterates its own `PLUGIN_RELS` list rather than walking the tree, which is exactly why it stayed green while the other two went red.

**Why it matters beyond the annoyance:** the merged-result gate run is the last check before a branch lands, and it runs from the main checkout while the worktree is still on disk — so the two gates fail for a reason that has nothing to do with the merge, at the precise moment someone is deciding whether the merge was sound. The correct reading is "remove the worktree, re-run", and nothing says so. On gate 3 the sequence was: merge → 10 errors → investigate → confirm the merge was identical to the verified branch tip → remove worktree → all seven green.

**Fix:** have both scripts skip gitignored paths, or at minimum skip a `.worktrees/`/`worktrees/` directory at the repo root. `check-docs.sh`'s list-driven approach is the shape that already works.


## G3-3 — check 11 cannot enforce `<merge-clause>` on any offer of `/create-ard` or `/specify`, anywhere in the tree

**CLOSED 2026-09-08** — `phase-handoff.md` §3.4's `/create-ard` and `/specify` rows now read ``the PRD (`prd.md`)``, and check 11's target extractor picks both up. **Re-measured rather than trusted, as this entry instructed:** the writer set was extracted afresh for all six in-family commands (`/brd-intake`, `/brd-split`, `/brd-interview`, `/brd-package`, `/brd-reconcile`, `/prd-ground`) and none declares `prd.md`, so the widening fires on nothing — the final review's correction confirmed by measurement, not by re-reading the paragraph that made it. `prd.md` is the right name to write because `/create-ard`'s own Phase 0 resolves exactly it on the ref, falling back to the legacy `<KEY>_*.md` form; the row states the gate target, so it had to be checked against the gate rather than assumed from the filename convention.

**Three rows of that table still name their target in prose, and were deliberately left**: the ARD row (`/specify` `/design` `/implement` `/epics` `/ready`) and the `/ready` row (`ARD / spec / design`). Both were measured the same way and would **also** fire on nothing — no in-family command declares `ard.md`, `specification.md` or `design.md`. They were not batched in for a reason that is not scope timidity: unlike the PRD, whose gate resolves a single known filename, an ARD may be **split per area** (`/create-ard` hands off "the ARD file(s)"), and `/ready`'s row covers three artifacts with three resolution rules. Naming one filename in either row would put a claim in the row-F table that the gate does not make. Each needs its own consumer read first; the zero-fire measurement is done and is not the blocker.

**Pre-existing, parked during gate 3 on reasoning the final review then corrected. It is ready to take.**

`check-docs.sh` check 11 gates the `<merge-clause>` placeholder by intersecting the offering run's declared `deliverable_paths` with the offered command's `require-on-main` target, read from `workflows-core:phase-handoff` §3.4's row-F table. Rows 10 and 11 name that target as the prose **"the PRD"** where every other row names a backticked filename, so the intersection has nothing to match and the relation never fires for either command. Nothing shipped is wrong — every such offer gate 3 added carries the placeholder — but they are held by review alone.

**The parking reasoning was wrong and the correction is the useful part.** It was parked partly on the estimate that naming `` `prd.md` `` in those two rows "would newly gate every offer of `/create-ard` and `/specify` across the tree (`/create-prd`, `/update-prd`, `/brd-reconcile` and others)", making it a scope explosion mid-plan. The final whole-branch review measured it instead: **check 11 only ever examines commands matching the family globs**, so `/create-prd` and `/update-prd` are unreachable by it; only `/brd-reconcile` is in-family; and the writer set extracted for all six in-family commands shows **none declares `prd.md`**. So the widening fires on **nothing** inside the gate's scope — which is precisely the criterion this repository uses to accept a widening ("fires-on-nothing means take it", the same measurement on which check 13's widening was taken and check 11's earlier one twice refused).

**Fix:** name `` `prd.md` `` in `phase-handoff.md` §3.4 rows 10 and 11, run `./scripts/check-docs.sh --root .`, and confirm the fire count is zero before committing. Re-measure rather than trusting the paragraph above — that is the whole lesson of this entry.

## G3-4 — recorded as constraints and open questions, not defects

Neither is a bug; both are written down because S18 is a promise about *known* state and these are known.

- **CLOSED 2026-09-08 by E-3.** ~~The `product-workflows` manifest `description` is 988 of its 1024 characters, tripping `validate-catalog.py`'s 900-char warning.~~ E-3's own capability forced the trim this bullet demanded: the closing dependency sentence came out — roughly 150 characters restating `plugin.json`'s machine-readable `dependencies` field, which is where a host actually reads it — and the blurb now stands at **852** in both editions, byte-identical. `validate-catalog.py .` reports **0 errors, 0 warnings**, where it had reported two since this bullet was written. **The rule the bullet stated survives its own closure**: a capability replaces wording, it never appends, and what comes out is decided at design time rather than at the version bump.
- **CLOSED 2026-09-08.** ~~`workflows-core:grounding-format` §1 has an em-dash clause butting against a pre-existing parenthetical.~~ The list is now bracketed by a matched pair of em-dashes and *checked against a pinned revision* closes the main clause it belongs to; the design-grounding case, which was the parenthetical, is its own sentence. Cosmetic throughout — no rule moved, and the section says exactly what it said before.
- **ANSWERED 2026-09-08, and the answer moved: the case asked about is unreachable, and the investigation found an adjacent one that is not.** ~~Open question, reachability unproven: `/prd-ground`'s legacy-fallback branch routes a folder whose `prd.md` is present but does not assert `kind: prd` to the interrupted-intake stop.~~ **Unreachable as asked.** `kind:` frontmatter arrived in `1da7480` (2026-08-31), and that same commit renamed the artifact: before it, the PRD file was `<KEY>_<slug>.md` and carried no `kind:`; after it, `prd.md` carries `kind: prd` and `product-workflows:prd-reviewer` verifies the field on every `/create-prd` and `/update-prd` run. So a `prd.md` **present without** `kind: prd` is producible only by hand-renaming a pre-2026-08-31 file without touching its frontmatter. The ledger's original reading was right, and for the right reason. **But the *absent* half of that same split is reachable, and it is a defect — see E-6.**

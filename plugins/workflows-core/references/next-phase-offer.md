# Next-phase offer (embedded — shared reference)

The family-wide contract for the **next-phase offer**: the guidance every pipeline command
surfaces at the end of its run, naming the natural next command(s). Cited by all pipeline
commands so the routing graph and the offer rules live in ONE place (the same shape as
`emit-block` in `feedback-emission.md`).

## The offer contract (7 rules)

1. **Guidance-only** — the offer NAMES the next command(s); it NEVER auto-invokes anything.
2. **Role-labeled** — it names the concrete command(s) for the next step, tagged with the owning
   role (PM / PA / PE / Dev), even on a handoff — one person may wear several hats and just keep
   going. Never a bare "hand off to PA".
3. **Adaptive to outcome** — a clean run points forward; a BLOCK / incomplete / cancelled run
   recommends resolving THAT first, not advancing.
4. **Mode-aware** — the forward recommendation is a PIPELINE handoff. In a command's direct /
   ad-hoc mode (no PRD/Epic context — `/dev-workflows:implement` direct, `/docs-workflows:document` doc-edit) it is OMITTED,
   not invented.
5. **Epic fan-out** — a command operating at **Epic scope** offers TWO branches (and `/dev-workflows:implement` names one more before them for each other code repository it recorded a change for: the run from that repository, addressed to the unit it implemented, the Epic itself where it was one):
   - **Depth** — the next command for the SAME Epic (`/dev-workflows:design <EPIC>` → `/dev-workflows:implement <EPIC>`).
   - **Breadth** — the SAME command for the NEXT Epic under the PRD (`/dev-workflows:design <EPIC-1>` →
     `/dev-workflows:design <EPIC-2>`).

   So a team can go `/dev-workflows:design E1 → /dev-workflows:design E2 → /dev-workflows:implement E1 → /dev-workflows:implement E2` OR
   `/dev-workflows:design E1 → /dev-workflows:implement E1 → /dev-workflows:design E2 …` — their call. Applies to the per-Epic commands
   only: `/product-workflows:create-ard <EPIC>`, `/product-workflows:specify <EPIC>`, `/dev-workflows:design <EPIC>`,
   `/dev-workflows:implement <EPIC>`. `/docs-workflows:document` and `/docs-workflows:release-notes` are PRD-level (whole-feature, run
   once after ALL Epics are implemented) and do NOT fan out.
6. **Fully qualified when printed** — every command name the run PRINTS for the user to invoke is
   written `/<plugin>:<command>`, fully qualified with the plugin that ships it. A bare `/<command>` can resolve to a Claude Code built-in of
   the same name — Claude Code's own `/release-notes`, `/upgrade`, and `/statusline` all collide
   today, and the built-in wins — so the bare form is NEVER printed. Prose that describes the
   pipeline to a reader of the family's own source keeps the short form.
7. **One address, never a pair** — every offer prints exactly ONE positional address, because every
   keyed command takes exactly one (D4: a key encodes its own ancestry, so an Epic address is all an
   Epic-scoped run needs and the PRD is derived from the folder above it). An offer written
   `/product-workflows:specify <PRD> <Epic>` names an argument form no command accepts: the run reads the
   first token, and the second either disagrees with it or is refused. Write `/product-workflows:specify
   <EPIC>` for an Epic-scoped step and `/product-workflows:specify <PRD>` for a PRD-scoped one — the
   prefix of the folder the address resolves to is what sets the altitude, and a folder with none is
   placed by what it holds (`${CLAUDE_PLUGIN_ROOT}/references/addressing.md` §4.1), so the offer
   never has to say it twice.

**A next-step offer that names a downstream command must also name the merge.** The downstream command executes `require-on-main` (`${CLAUDE_PLUGIN_ROOT}/references/phase-handoff.md` §3) and stops while this phase's pull request is open, so an offer that reads "next: `/product-workflows:create-ard <KEY>`" without "once the pull request is merged" sends the user into a stop they were not warned about.

**And it must name it truthfully, which means the clause is never unconditional.** A run that staged nothing, or whose handoff the user declined, opened no pull request — and "once the pull request above is merged" then parks the operator waiting for a merge that will never happen, on a run they could often start immediately. Worse, the failing outcomes differ from each other — of those two, only one has a branch to name, and they are not the only two §4.1 defines. So an offer carries the clause as the placeholder **`<merge-clause>`**, resolved from the `Phase handoff:` line `phase-handoff.md` §4.1 actually emitted. **Where a run emitted more than one — §4.1 names `/brd-reconcile` as the only producer that does — the clause resolves from the line reporting the handoff of the artifact the offered command's gate targets**, which is the run's own deliverable rather than any ancillary one it also landed; there, `/brd-package` and `/prd-ground` — and, through `decisions.md`, `/create-prd`, `/create-ard` and `/specify` — gate on what the reconciliation record's handoff carried, not on the canonicalised customer review:

| §4.1 outcome | `<merge-clause>` resolves to |
|---|---|
| Committed, pushed, PR opened | `(once the pull request above is merged)` |
| PR already existed | `(once the pull request above is merged)` |
| PR not opened | `(once you open the pull request for <branch> and it is merged)` |
| Push failed | `(once <branch> is pushed, its pull request opened, and merged)` |
| No remote | `(once <branch> is merged into the default branch — this specs repo has no remote, so no pull request will do it)` |
| Nothing to commit | `(its inputs are already on the default branch — you can run it now)` |
| Declined by the user | `(once this run's artifacts reach the default branch — they are written but not there)` |
| Gate failed | `(once this run's artifacts reach the default branch — the handoff did not run)` |
| Anything else, or unresolvable | `(once this phase's artifacts are on the default branch)` |

`Branch name substituted` is an append to another line rather than an outcome of its own — whatever branch the emitted line ends up naming is the branch the clause names. **The table resolves every one of §4.1's eight outcome rows, and the catch-all is for a line that could not be read at all** — never for an outcome §4.1 defines. It stood at six for a release, and both omissions dropped something the run was holding: *PR already existed* fell to a catch-all that never named the pull request the operator has to merge, and *No remote* to one that never named the local branch the artifacts are committed on. **Three rows name a branch, and which three is the point**: §4.1's declined and gate-failed lines carry none, because on those paths `handoff-to-main` committed nothing, so there is no branch in existence to send anyone to — where *No remote* **does** commit, on a branch that exists and that nothing in that repository will ever push, so it is exactly a row that must name one. Count the branch-naming rows off the table rather than off this sentence: the property is *committed something*, and a row added without a branch where it committed one is the defect this paragraph exists to catch.

**Where the placeholder sits in the text, which is a convention of its own and stood in one adopter rather than here.** It never goes inside the code span that carries the command. In prose it takes a span of its own, after the command's — `/product-workflows:specify` and `/dev-workflows:design` write it that way — and in a `choices:` option it is plain text, which is how `/product-workflows:update-prd` writes it in both its offer box and its array. **The reason is the table above**: every value the placeholder resolves to is a parenthesised English sentence, so a clause inside the command's span makes the one line an operator copies end in a positional token of prose — and on an offer that *is* that one line, nothing beside it marks where the command ends. Inside an option it follows the command, its address, and any role or `(Recommended)` label; a purpose clause may follow it in turn, as `/product-workflows:brd-reconcile`'s *Package again* option does, so "last token of the option" is the common shape and not the rule. **Re-derive it rather than trusting this paragraph** — `grep -rn '<merge-clause>' plugins/*/commands/*.md`, and read each hit for whether the token sits inside a span that also holds a command; today none does, in prose or in an array. The test is the placeholder's own span and never the option's: an option may legitimately carry a code span for something else, and a few do.

**Where this rule applies: every next-step offer the dependent plugin family prints — `product-workflows`, `dev-workflows` and `docs-workflows` each print them, and `workflows-core` prints none (this paragraph's own close, and *Not pipeline nodes* below); the commands named here are the ones this convention binds, and every one of them that names a downstream gate its run feeds carries the placeholder.** The `<merge-clause>` placeholder is the convention the `/product-workflows:brd-*` commands write their offers to — the five of the BRD-to-PRD route, and the programme umbrella `/product-workflows:brd-proposal` beside them, which matches the same glob without being a phase of that route — and an offer added to any of them carries it where it names a downstream gate the offering run feeds. `/product-workflows:prd-ground` left that family the day its own rename shipped — the rename made it stop matching `brd-*` — but every offer it prints still names a downstream command whose `require-on-main` gate that same run feeds, exactly as the route's five do, so it carries the convention too, under its own glob, `` `/product-workflows:prd-*` ``. It is equally the convention of the **six** older pipeline offers, converted after the route shipped: `/product-workflows:create-prd`'s and `/product-workflows:update-prd`'s *Next steps* phases, `/product-workflows:create-ard`'s *Next-step offer (adaptive)* phase, the `### Next step` sections of `/product-workflows:specify` and `/dev-workflows:design`, and `/product-workflows:idea`'s Phase 5 handoff offer. Four of the first five hardcoded "once the pull request above is merged" on runs that reach outcomes opening no pull request; the fifth, `/product-workflows:update-prd`, named two downstream commands that gate this run's own PRD and stated no wait at all. **The sixth was left off this list for a round and was defective the whole time**: `/idea` Phase 5 recommended `/product-workflows:create-prd <KEY>` with no clause of any kind, while `/create-prd` Phase 0 step 3 rung 1 runs `require-on-main` on the very `idea.md` whose pull request that offer had just opened — this rule's own named failure, in the one adopter the rule's own adopter list omitted. It carries the placeholder now; and its `status: draft` branch, which hands nothing off so no row of the table above could resolve, names the `@<path>` read form instead of a wait. No offer in that family now names a downstream gate its own run feeds and states the wait unconditionally, and an offer added anywhere in it that names such a gate carries the placeholder. **An offer that names none does not**, and `/product-workflows:brd-proposal` is the case: it hands off an artifact no `require-on-main` gate targets — a later run of that same command reads it, which is a read and not a gate — and its own next-step options name no gate its run feeds, so it carries no clause anywhere — which is why the rule is stated against the gate the offer names rather than against membership of the family. This reference ships in `workflows-core`, which prints no next-phase offer of its own: `/workflows-core:frames` makes only its §4.3 handoff offer (see its paragraph below), and that offer carries no clause on purpose: nothing runs `require-on-main` on a frame-set index, so no downstream gate reads what it writes. **Both proposal commands match those globs and are inside the rule by name rather than by adoption.** `/product-workflows:prd-proposal` and `/product-workflows:brd-proposal` author effort proposals, and both are covered by the two globs already named — there is no version of that work in which they sit outside this gate. The placeholder appears in exactly one option across the pair: `/prd-proposal`'s offer of `/brd-proposal`, whose `require-on-main` gate targets the `proposal.md` that same run has just written. Every other option either names a command gating on `prd.md`, which neither proposal command writes, or names the offering command itself.

**A gate enforces adoption, and it enforces exactly one half of this rule.** `scripts/check-docs.sh` check 11 asserts that every `choices:` option in the `/product-workflows:brd-*` and `/product-workflows:prd-*` families naming a command whose `require-on-main` target the offering run writes carries the `<merge-clause>` token. It derives those families from **every** such glob the scope paragraph above names — not only the first — the gate targets from `phase-handoff.md` §3.4's table, and what a run writes from each command's own `deliverable_paths` list. **Three things it does not check, and each is a place a defect has lived or can live:**

1. **Presence, not resolution.** The gate sees the token `<merge-clause>` in the option text. It cannot see which row of the table above a run resolves it to. Picking the wrong row is a real, shipped defect — an offer once told the operator to name a branch on a **declined** handoff, where `handoff-to-main` committed nothing and §4.1's declined line carries no branch. A reader who assumes the gate covers resolution will reintroduce that. The table above, and the sentence that three of its rows name a branch, are enforced by review alone.
2. **`choices:` arrays only.** An offer written as prose — a `### Next step` paragraph, a final-report sentence — is invisible to it. The universal minimum surface this contract defines is exactly the surface the gate does not cover.
3. **Declared paths only.** A run's writer set is what its command file lists after `deliverable_paths` =. A file a run writes but never declares there is not in that set, so an offer that should carry the clause because of it will not be asked to. This under-fires rather than over-fires, and a family command whose declaration yields nothing at all turns the build red rather than going quiet.

The gate is a floor under the convention, never a substitute for reading it: an offer can satisfy check 11 and still be false.

**The family scope is deliberate, and recorded here so widening is not re-proposed without new evidence.** Adoption is family-wide, as the scope paragraph above says; the gate is not. **Re-measured on the current tree, after `/update-prd`'s `deliverable_paths` declaration was corrected to name its grounding-file writes as backticked filenames.** Removing the family filter and running check 11 over every command in `product-workflows` — the plugin whose `/brd-*` and `/prd-*` families are this gate's scope — fires on **one** site and catches **none** of the six offers converted for the paragraph above. `/document` and `/implement`, two of the three sites an earlier measurement named, ship from `docs-workflows` and `dev-workflows` respectively and so fall outside this scope; `/update-prd`, the third, no longer fires — its `deliverable_paths` = declaration used to list what it writes in prose only ("the canonical PRD file", "the archived snapshot file"), which left the writer-extractor nothing to check any of its options against and dropped the whole command's offers out of coverage, but that declaration now also names `grounding/code-grounding.md` and `grounding/design-grounding.md` as backticked filenames (for the same reason the `consumed_by` write they carry needs committing), which gives the extractor a non-empty writer set and retires this hit; the two downstream offers that intersect it (`/specify`, `/create-ard`) already carry `<merge-clause>` in their option text, so nothing newly fails either. The one site that remains is `/product-workflows:specify`'s Phase 0 "PRD with 0 Epics" branch, which offers `/product-workflows:epics` with no clause — but it is a mid-run redirect rather than an offer, taken long before the offering run reaches its own handoff phase, so there is no §4.1 outcome line for a clause to resolve from. The six real defects this rule was written to fix stay invisible to the widened check as well, and for the same two reasons already given above: `/specify`'s and `/design`'s `### Next step` offers carry the intersection the check looks for but are missed for being prose, and the `choices:`-array offers among the six are missed because `phase-handoff.md` §3.4 and each offering command's own `deliverable_paths` declaration both name their targets in prose rather than as backticked filenames. A `choices:` array in `product-workflows` is a refusal or a mid-run branch point as often as it is an offer, and nothing in the file marks which; a gate that cannot tell them apart blocks correct work, and a gate that blocks correct work gets disabled. Same verdict, and the same reason, as the stop-routing check `scripts/check-docs.sh` records as never shipped. **The measurement is recorded here so widening is not re-proposed without new numbers: one correct site fired on, zero of six defects caught.**

**Resolving this placeholder is not a rewording.** The array is still presented verbatim per `${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md`'s *Choice lists are presented verbatim*, exactly as `<BRD-KEY>` or `<KEY>` is substituted in the same strings. A command that instead told the orchestrator to *adjust the wording* of an option would be contradicting that convention, which is why the variation lives in a placeholder and not in an instruction.

## Surface

The universal minimum is an adaptive **`### Next step`** section at the END of the command's
Final Report (guidance-only prose). A command MAY additionally present a richer interactive
`choices:` offer (the reference commands `/product-workflows:idea`, `/product-workflows:create-prd`, `/product-workflows:create-ard` do) — compatible,
not required.

**When there are more forward options than the array can hold.** `AskUserQuestion` renders at most
four options (`${CLAUDE_PLUGIN_ROOT}/references/escalation-rules.md` §0), and several offers have
more forward steps than that. The prose is what carries the complete set — it is the universal
minimum precisely because it has no arity limit — so an overflowing offer resolves like this, and
never by silently deleting a route:

1. **List every option in the prose**, above the prompt, each with the command that runs it. A route
   named in prose is a route the operator can still take.
2. **The array carries `Stop here` plus the three the run's own outcome makes most likely**, in the
   same order the prose lists them. Rule 3 (adaptive to outcome) is what decides "most likely"; where
   a command already drops options on their own triggers, that filtering runs first and the cap
   applies to what survives it.
3. **Say, in one line, that the prose list is longer than the prompt** and that anything on it is
   reachable through the harness's free-text option. A demoted route the operator cannot find is the
   same defect as a deleted one.

An offer whose options fit in four does none of this: the prose stays the universal minimum and the
array carries every option.

## The routing graph (role-aware)

**PM — ideation & framing**

- `/product-workflows:idea` — refined → `/product-workflows:create-prd <KEY>` (PM), with
  `/product-workflows:create-prd <KEY> @<path to idea.md>` beside it where the handoff was declined
  or its gate failed; draft → `/product-workflows:idea <KEY> <the same source>` (PM, refine) or
  `/product-workflows:create-prd <KEY> @<path to idea.md>` (PM, proceed on a draft — not recommended).
  The `@<path>` is what reads an `idea.md` on no ref directly: `/create-prd <KEY>` alone names such a
  file and does not read it in contract — it reaches it only through its same-session rung or a path
  the operator types (`/product-workflows:idea` Phase 5).
- `/product-workflows:create-prd <ADDRESS>`:
  `/docs-workflows:release-notes <PRD>` (PM — draft the release note; recommended clear next step); hand to PA
  *(optional)* → `/product-workflows:create-ard <PRD>`; or hand to PE → `/product-workflows:epics <PRD>` (or `/product-workflows:specify <PRD>`).
- `/product-workflows:update-prd <KEY>` — re-entry, not a linear node: reached when `/product-workflows:create-prd` redirects an existing-PRD call, or when a later phase forces a PRD refresh. Its Phase 6 offers re-runs only for existing downstream artifacts, recommends those affected by the update, and skips the picker when none exist, without skipping terminal bookkeeping. Candidate routes are `/docs-workflows:release-notes <PRD>` (PM), `/product-workflows:create-ard <PRD>` (PA), `/product-workflows:epics <PRD>` (PE), and `/product-workflows:specify <PRD>` (PE).

**PM / PA — the BRD-to-PRD route**

- `/product-workflows:brd-intake <BRD-KEY> @<brd-file>` — the route's entry point → hand to PM →
  `/product-workflows:brd-split <BRD-KEY> "<how to cut it>"` (PM; the instruction is mandatory on a
  root, since a root is never ground and carries no finding to cluster by).
- `/product-workflows:brd-split <BRD-KEY>` on a root (`split_mode: full`) → `/product-workflows:prd-ground <CHILD-KEY>` (PA) once per child that **gained a row this run** — the slices the run keyed and still claiming at least one `[BR#n]`, plus any standing child its walk newly resolved a row to — each such child re-entering the route at grounding. **The set is what the run did, never what the tree looks like afterwards**, and both directions of that matter: a non-empty child that gained nothing has grounding that still covers everything it claims, so offering a re-run for it asks an operator to re-derive work nothing needs; and a **standing receiver** — a child that already stood and has just been given a row, the one whose grounding demonstrably no longer covers what it claims — is the child that most needs the offer and is exactly what a set defined over emptiness would miss. A child whose `claims:` list is empty — including one the parent's walk emptied by withdrawing a claim, **provisional or committed**, leaving it holding only orphan rows — is a standing empty child (`/product-workflows:brd-split` Phase 7), and grounding it stops at `PRD_GROUND_EMPTY_INVENTORY`, so it is not offered either. The root's own key is offered no further: `/product-workflows:brd-interview` refuses any root outright.
- `/product-workflows:prd-ground <CHILD-KEY>` (PA) → `/product-workflows:brd-split <CHILD-KEY>` (PM),
  which always runs `allocate-only` here (`/product-workflows:prd-ground` never resolves a root) and
  creates no further child → `/product-workflows:brd-interview <CHILD-KEY>` (PM).
- `/product-workflows:brd-interview <BRD-KEY>` → `/product-workflows:brd-package <BRD-KEY>` (PM), offered
  only where this run's own state is one `/product-workflows:brd-package` would accept
  (`/product-workflows:brd-package` Phase 0 owns that test); otherwise → another
  `/product-workflows:brd-interview <BRD-KEY>` round (PM), or `/product-workflows:prd-ground <BRD-KEY>` (PA)
  for a question no finding bears on yet. Where nothing is left for the customer to review, the slice is
  decided and hands over from here, with no reconciliation: → `/product-workflows:create-ard <BRD-KEY>`
  (PA, optional) or `/product-workflows:specify <BRD-KEY>` (PE), and `/product-workflows:create-prd <BRD-KEY>`
  (PM) where the slice is PRD-eligible — the same conditions `/product-workflows:brd-reconcile`'s
  advancing list applies (`/product-workflows:brd-interview`'s next-step phase owns that list).
- `/product-workflows:brd-package <BRD-KEY>` → *(the customer reviews it off-platform, and the round
  holding each customer question stays open until the answer comes back)* →
  `/product-workflows:brd-reconcile <BRD-KEY> @<review-file>` (PM).
- `/product-workflows:brd-reconcile <BRD-KEY> @<review-file>` → the route's hand-over into the PRD
  pipeline for a slice the customer reviewed (a slice needing no review hands over from
  `/product-workflows:brd-interview`, above), and its own re-entry. **Re-entry:** another `/product-workflows:brd-interview <BRD-KEY>`
  round where this run reopened a decision and no round stays open holding only questions held for the
  customer — a round open on a *deferred*, *untagged* or *needs grounding* question is one that run
  resumes — `/product-workflows:brd-package <BRD-KEY>` where questions
  remain for the customer, or `/product-workflows:prd-ground <BRD-KEY> --rebaseline` where the review
  challenged a code claim. **Advance is offered off the slice key this run reconciled** —
  `/product-workflows:brd-reconcile` itself never resolves a root, so there is no level of its own
  left to test here. The BRD route on `/product-workflows:create-prd`, `/product-workflows:create-ard`
  and `/product-workflows:specify` all ship, and that command's next-step phase offers all three off
  that key. Each of the three still refuses a `BRD-` folder in its own Phase 0
  (`CREATE_PRD_BRD_NOT_SLICED`, `CREATE_ARD_BRD_NOT_SLICED`, `SPECIFY_BRD_NOT_SLICED`;
  `product-workflows:coverage-ledger-format` §5) — a defense this offer never needs to invoke, since
  the key it hands over is always the slice `/product-workflows:brd-reconcile` was given.
  **The three are offered only on a run that left nothing to re-enter for.** Advance and re-entry are
  separate arrays, not one: where that run reopened a
  decision, left a `[C]` held for the customer, left a finding for a `--rebaseline` pass, or could
  only record a dependent's sweep, all three advance options are dropped, because a `reopened` record
  may not be consumed downstream (`product-workflows:decision-register-format` §3) and all three consume
  the register. On an advancing slice run, `/product-workflows:create-prd <SLICE-KEY>` carries the further
  condition that the reconciled ledger leaves no row `unallocated` and at least one `covered-here`
  (`product-workflows:coverage-ledger-format` §5, the two refusals its Phase 0 raises); the other two
  carry none of their own: neither reads the ledger as an authoring input, and although both now run the PRD gate on every
  route, that gate's `absent` branch proceeds — a slice holding no authored `prd.md` is the ordinary
  state for both, since `/product-workflows:create-prd` is a prerequisite for neither. **That difference is where the conditions come from, and it matters:**
  the level test and `/create-prd`'s eligibility test are each enforced by the offered command's own
  Phase 0, so offering either wrongly hands over a run that stops;
  the advance/re-entry split is enforced **nowhere downstream** — `/create-ard` on the BRD route and
  `/specify` on the BRD route treat an `open` or `reopened` record as an open question to record rather
  than as a stop — so the station that offers them must make it: `/product-workflows:brd-reconcile` for a slice the customer reviewed, and `/product-workflows:brd-interview`, whose `nothing-to-review` state keeps a reopened record's list apart from the one that offers the three, for a slice that needs no review. **All
  three carry `<merge-clause>`**: on the BRD route each runs `require-on-main` against the slice's
  `decisions.md` (`phase-handoff.md` §3.4), which this run's second handoff — the reconciliation
  record's — lands, so each stops while that pull request is open and the clause resolves from that
  handoff's line (the multi-handoff rule above).

**PM — effort proposals (optional, and they gate nothing on the build ladder)**

- `/product-workflows:prd-proposal <PRD-KEY>` — **depth** → `/product-workflows:brd-proposal <BRD-KEY>`
  (PM), where the folder has a parent BRD, **carrying `<merge-clause>`**: that command runs
  `require-on-main` against the very `proposal.md` this run wrote. **Breadth** →
  `/product-workflows:prd-proposal <SIBLING-SLICE-KEY>` (PM), for the next sibling holding no current
  proposal. And, below tier 4, **the command that would raise the tier** —
  `/product-workflows:create-ard <KEY>` at tier 2, `/product-workflows:specify <KEY>` at tier 3 — named
  together with the plain statement that re-running the proposal afterwards narrows the range. Neither
  of those two carries a clause: both gate on `prd.md`, which a proposal run does not write.
- `/product-workflows:brd-proposal <BRD-KEY>` — **no forward advance.** The umbrella is the end of this
  branch, not a phase in the build ladder. It offers re-runs: `/product-workflows:prd-proposal
  <SLICE-KEY>` for each slice its readiness walk found stale or excluded, and itself once those land.
- **Neither is a prerequisite for the build ladder.** `/product-workflows:create-ard`,
  `/product-workflows:specify`, `/product-workflows:epics`, `/dev-workflows:design`,
  `/dev-workflows:implement` and `/dev-workflows:ready` each resolve the same folder and neither know
  nor care whether it holds a proposal — none reads `proposal.md`, requires one, or behaves
  differently because one exists, and no readiness tier withholds permission to begin work
  (`product-workflows:proposal-format` §1). The pair's own internal read above is real and stays
  inside the pair: `/product-workflows:brd-proposal`'s `require-on-main` against a slice's
  `proposal.md` never reaches into the pipeline above it. These two are offered *from* the pipeline
  and never gate *into* it.

**PA — architecture (optional)**

- `/product-workflows:create-ard <PRD>` (PRD-level) → PE → `/product-workflows:epics <PRD>` (recommended) or `/product-workflows:specify <PRD>`.
  *(No `/dev-workflows:design` — no Epics yet.)*
- `/product-workflows:create-ard <EPIC>` (Epic-level) → `/product-workflows:specify <EPIC>` (recommended) or Dev →
  `/dev-workflows:design <EPIC>`.

**PE — breakdown & specification**

- `/product-workflows:specify <PRD>` (PRD-level spec) → `/product-workflows:epics <PRD>`.
- `/product-workflows:epics <PRD>` → `/product-workflows:specify <EPIC>` (per Epic); optional PA → `/product-workflows:create-ard <EPIC>`.
  **Every `/product-workflows:epics` option above and below is conditional on the folder it names
  holding an authored `prd.md`** (`kind: prd`): `/epics` accepts a PRD folder or an `EPIC-` folder
  under one and refuses everything else (`/product-workflows:epics` Phase 0 step 1b). Where the
  caller's PRD folder — the resolved folder itself on a PRD-level run, its parent on an Epic-level
  one — holds no PRD, which the BRD route reaches legitimately since `/product-workflows:create-prd`
  is not a prerequisite for `/product-workflows:create-ard` there, the offer is
  `/product-workflows:create-prd <PRD>` instead, `<PRD>` being that tested folder's own key and
  never an Epic's, **and only where that command can itself run**: it refuses more than one shape —
  three on the BRD route, and an `EPIC-` folder on either, which is why the key is the PRD folder's
  — so on a BRD-route slice the two data refusals on that slice's own ledger are tested first and
  the offer resolves to `/product-workflows:brd-split` against one of two keys, or to no option at
  all, where either fails (`product-workflows:coverage-ledger-format` §5.2, the authority, applied
  by each offering command). An offer whose run stops the moment it starts is the same defect the
  `<merge-clause>` rules below exist to prevent, one command further on: a next step the operator
  cannot take from the state the report describes.
- `/product-workflows:specify <EPIC>` (Epic-level spec) → Dev → `/dev-workflows:design <EPIC>`.

**Dev — build, verify & deliver**

- `/dev-workflows:design <EPIC>` → optionally `/dev-workflows:ready <EPIC>` (verify readiness) →
  `/dev-workflows:implement <EPIC>` — each `<PRD>` in place of `<EPIC>` after a broad PRD-level
  design, whose Epic is null: the next address is the folder the design was written into.
- `/dev-workflows:ready <ADDRESS>` → **SUPPORTED** → `/dev-workflows:implement <ADDRESS>` (the same address); **PARTIAL / NOT-SUPPORTED**
  → resolve the named gaps, then re-run `/dev-workflows:ready`. *(Read-only verifier;
  not itself a linear pipeline node — an optional gate before build.)*
- `/dev-workflows:implement <EPIC>` → first, where it recorded a change another code repository needs, the run from that repository, addressed to the unit the run implemented (the Epic itself, where it was one); then finish remaining Epics (breadth); once ALL Epics implemented →
  `/docs-workflows:document <PRD>` → `/docs-workflows:release-notes <PRD>`. *(Direct mode → no forward offer.)*
- `/docs-workflows:document <PRD>` (PRD-level, after all Epics) → `/docs-workflows:release-notes <PRD>`. *(Doc-edit mode → no
  forward offer.)*
- `/docs-workflows:release-notes <PRD>` (PRD-level) → leaf/closure: release note drafted; continue any pending
  PA/PE phase, else the PRD is fully processed.

## Not pipeline nodes

`/dev-workflows:vuln`, `/dev-workflows:upgrade`, `/workflows-core:feedback`, `/workflows-core:prompt*`, `/docs-workflows:docs-profile`, `/workflows-core:statusline`, `/workflows-core:frames`, and the reviewer
commands are NOT part of the linear PRD→docs pipeline and carry no next-phase offer. `/workflows-core:frames`
repairs a folder's frame-set indexes and advances no phase; it makes the §4.3 handoff offer its
deliverables require and no next-phase offer at all, so no `<merge-clause>` arises — nothing runs
`require-on-main` on a frame-set index.

**`/docs-workflows:docs-init`, `/docs-workflows:docs-brand`, `/docs-workflows:docs-serve` and `/docs-workflows:docs-audit` are not pipeline nodes either, but each does print a `### Next step`** — in this file's universal-minimum prose form, guidance only and never auto-invoked, because such a run leaves the operator with an obvious next action (push the drafted docs-repo pull request; serve the site; write its pages; read the backlog, correct what is wrong in it and commit it) even though it advances no PRD phase. None of the four carries a `<merge-clause>`: the pull requests `/docs-init` and a standalone `/docs-brand` draft target the docs repository, not `$SPECS_PATH`, `/docs-audit` leaves one tracked file in that repository and drafts no pull request at all, and none of the four runs `handoff-to-main` or feeds any command's `require-on-main` gate. Each states that omission in its own body; `scripts/check-docs.sh` check 11 does not see it, since no `/docs-*` glob is in its scope.

## Session hygiene co-fires here

The `### Next step` this contract produces is immediately followed by a
`### Context hygiene` block (`${CLAUDE_PLUGIN_ROOT}/references/session-hygiene.md`): the compact-vs-clear
choice reads the SAME role labels computed here (same role → `/compact`; role handoff →
`/clear`). This reference owns the role graph; `session-hygiene.md` only reads it.

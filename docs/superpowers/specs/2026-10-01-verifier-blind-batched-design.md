# Blind, batched grounding verification — `/prd-ground` Phase 7

Date: 2026-10-01. Status: implemented on branch `iv-gu/verifier-blind`. Issues: #73, #74.

## Problem

**#73 — the verifier is handed the answer.** `workflows-core:grounding-format` §8 defines verification as an independent re-derivation that starts from the requirement premise, never from the finding's evidence, and `product-workflows:grounding-verifier`'s Process step 2 forbids reading `evidence`, `control` or `cites` until its own derivation is done. But `/prd-ground` Phase 7 tells the orchestrator to "supply the finding exactly as the agent's own Inputs contract declares it — including `evidence` … never to withhold a field the contract lists", and leaves the sequencing "the agent's to enforce on itself". An agent cannot un-see text in its own context window. In the run that reported this, four of eight verifier dispatches said so unprompted in their `notes`. The risk is anchoring toward `agree` on exactly the failure that run found most: an original citing something real but adjacent.

**#74 — verification scales as findings, one Opus agent each.** Phase 5 sends every claim to every repository (no pre-filtering, deliberately), and Phase 7 dispatches one `grounding-verifier` per finding. A 138-claim BRD over two repositories produced 278 findings and needed 278 Opus dispatches in about 70 sequential batches of four. 200 of the 278 were `NOT-PROVABLE`, 117 of them from one frontend repository answering backend claims. The cost is only visible at Phase 7, after both fan-outs have been paid for.

Two amplifiers the issue did not name, found while reading Phase 7:

1. **Every re-run re-verifies the whole corpus on file.** Phase 7's set includes every non-`SUPERSEDED` `[CG#n]` at an unmoved pin, because §8 treats an earlier run's findings as unverified. Adding a third repository to a grounded BRD re-verifies all 276 existing findings.
2. **Any Phase 7 stop discards the whole pass.** Nothing is written before Phase 8, so a stop at finding 270 of 278 loses all the verifications before it, and Phase 5's own-run findings with them.

## Goals

1. The re-derivation is blind **by construction**: the finding's answer is never in the deriving agent's context.
2. Phase 7's dispatch count follows batches, not findings.
3. The operator sees the cost before anything is paid for — when choosing repositories, wherever Phase 1 asks for them.
4. A transient contract break by the agent does not discard the pass.

## Non-goals

- Weakening any single finding's verification — no cheaper model tier, no sampling, no repository-scope finding standing in for individual re-derivations (D1).
- Carrying a verifier outcome forward from an earlier run (D2).
- Checkpointing Phase 7 for resume across runs (D4).
- Changing Phase 5's no-pre-filtering rule, the membership of Phase 7's verification set, the reconciliation and write rules that act on a returned outcome, or `/brd-split`'s gate. (The live smoke run later found a pre-existing defect that changed the membership by one exclusion — §1.)
- Continuing a running agent with follow-up messages. Nothing in the plugin family relies on agent continuation, and the commands must run in harnesses that lack it.

## Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | Per-finding guarantee | Unchanged: every finding gets its own full, independent re-derivation on the Opus chain. Only packaging and scheduling change |
| D2 | Re-runs | Re-verify every finding on file, as today |
| D3 | Architecture | Two steps per batch — a blind re-derivation (`mode: derive`), then a comparison (`mode: compare`) |
| D4 | A stop mid-pass | Retry an incomplete result once, through the step that failed; no checkpoint |
| D5 | Agent shape | One agent, `grounding-verifier`, with two modes — not two agents |
| D6 | Batch composition | By repository (`[CG#n]`) or frame set (`[DG#n]`), ordered by id, capped at 25, never dependent on a finding's verdict, evidence or control |
| D7 | `provenance` | No longer passed to the agent; Phase 7 keeps it for its own write rules |

**D2's reasons.** Batching cuts a re-run's cost by the same factor it cuts a first run's, so what carry-forward would save is small. Carry-forward needs a stamp saying which verifier contract an outcome was reached under, and something has to bump that stamp whenever the agent, `grounding-format` or the model changes; no gate would check it, and a missed bump silently carries a stale outcome forward — the state §8 exists to prevent. And on unchanged code, a re-verification is the only way an error the first verifier made ever surfaces.

## 1. Batching

- **Membership is unchanged.** Phase 7 builds the set exactly as today: this run's own findings (Phase 3's baselines, Phase 5's claim findings, Phase 6's successors), the on-file `[CG#n]` at unmoved pins, never an on-file `[DG#n]`, and the `--no-code` variant. One exclusion was added after the live smoke run: every earlier baseline finding, meaning each `[CG#n]` a `grounding/baselines.md` entry records. An unmoved repository's is one Phase 8 now supersedes for the fresh one Phase 3 mints (`grounding-format` §4.1), so re-verifying it would spend an Opus pass on a block retired in the same run. Any other repository's is pinned where no unmoved repository stands, which Phase 3's shared-pin check guarantees, so it was never the run's to re-check.
- **Grouping.** A `[CG#n]` batches with the other `[CG#n]` of its repository. A `[DG#n]` batches with the other `[DG#n]` of its frame set; a class-4 `[DG#n]` carries, in addition, the repository and commit of the `[CG#n]` it cites, so a frame-set batch can hold several repository pairs.
- **Order and cap.** Within a group, findings are ordered by requirement id (`[CG#n]`) or by finding id (`[DG#n]`, since one requirement can carry several), and cut into batches of at most **25**. The cap is defined in Phase 7, which names every shipped site that quotes it. This design spec is a record, not one of those sites. Phase 1's cost statement quotes the cap's value, since the operator has to see the number.
- **Baselines.** Each repository's baseline `[CG#n]` goes in that repository's first batch. Its re-derivation is the `baseline-integrity` re-run that both steps perform first anyway (`grounding-format` §4.1), and it owes no positive control: those three commands are git's report over the whole checkout, not a search (§2.2, added after the live smoke run).
- **Composition never depends on the answer.** Nothing about a finding's `verdict`, `evidence` or `control` may decide which batch it lands in or where. A batch of "the `NOT-PROVABLE` ones" would tell the blind step what the original concluded.
- **Scale.** The reported run becomes 2 repositories × ⌈138/25⌉ = 6 batches × 2 steps ≈ 24 dispatches, at most 4 concurrent, where it was 278.

## 2. The verifier's contract (`agents/grounding-verifier.md`)

**Both modes.** The Opus frontmatter pin, read-only posture, and the fail-closed row selection of the Inputs table (which anchors each finding requires) are unchanged. Each batch runs Process step 1 — establish the source, `baseline-integrity` against the pinned commit — once, before any re-derivation or comparison (in derive mode, after the field check of §2.1, which needs no I/O). Batch-level refusals are today's: `REPO_MISSING`, `COMMIT_MISMATCH`, `FRAME_SET_MISSING`, `NO_INDEX`, `STALE_INDEX`, applying to every finding in the batch. `INPUT_MISSING` is per finding: one finding short of a field its row requires does not refuse its batch-mates. A `mode` that is absent or reads anything but `derive` or `compare` is a batch `INPUT_MISSING`: the agent never guesses a mode from the shape of the entries.

### 2.1 `mode: derive` — the blind re-derivation

- **Inputs:** the source anchors (`repo_path` + `commit`; `frame_set_dir` + `inventory`; for a class-4 `[DG#n]`, both), and per finding its `id`, its `claim` as recorded (the premise under test), and, for a `[DG#n]`, its `class`.
- **Never in the input:** `verdict`, `evidence`, `control`, `cites` — nor compare's own `cited` and `derived` — and no path into `$SPECS_PATH` other than `frame_set_dir`.
- **`INPUT_UNBLIND`** (new, batch-level refusal): a derive dispatch carrying any of the six fields above is refused whole, naming the field and the finding. The agent never "mitigates" a contaminated input.
- **New hard rule:** under `$SPECS_PATH`, read nothing outside `frame_set_dir`. Frame sets live in a folder's `design/` directory, so `frame_set_dir` is itself under `$SPECS_PATH`; its sibling `grounding/`, where every on-file original lives, is not to be opened.
- **Per-item independence:** each finding is worked from its own premise. A fact the agent established for one finding (for example, "this repository holds no persistence layer") may be cited for another only after checking it bears on that finding's premise, and each finding's `own_evidence` stands on its own.
- **Returns per finding:** `finding_id`, `status` (`OK` | `INPUT_MISSING`), `own_verdict`, `own_evidence` (never blank), `own_control` wherever its own verdict owes one under §2.2's closed-set rule, and `notes`.

### 2.2 `mode: compare` — the comparison

- **Inputs:** the batch's original findings in full (today's dispatch fields, `provenance` excepted) and the derive result for each; for a class-4 `[DG#n]`, also the record of the `[CG#n]` it cites, as this run holds it at dispatch, since step 3 compares against it. A `[CG#n]` this phase later rewrites reaches its class-4 citers through the sweep, as today.
- **Process:** re-run `baseline-integrity` (the repository may have moved between the steps); settle whether the **original** owes a control and **run** any it owes (today's step 3a, unchanged); settle whether the **blind verdict** owes one; decide the outcome from the two records and the control run (today's step 4, unchanged).
- **`INCOMPLETE`** (new, per finding), in two cases. Where the blind verdict lacks only its owed control — an `own_verdict` that owes one, a non-blank `own_evidence`, no `own_control` — the entry still carries `outcome` and `control_outcome`, so the outcome is still readable after a retry. Where `derived` is malformed — absent, with no `own_verdict`, or with a blank `own_evidence` — there is no usable blind result, and the entry carries no outcome.
- **New hard rule:** compare never revises the blind result — not `own_verdict`, `own_evidence` or `own_control`. It has seen the original, so anything it re-derived would not be independent. It may add `notes`.
- **`blind_disputed`** (added after the final live smoke run): compare returns `true` only where the blind result's own evidence does not establish its own verdict under `grounding-format` §3, with the reason in `notes`. It never returns `true` because the original's verdict differs, and the flag changes neither `own_*` nor the outcome.
- **Returns per finding:** today's return fields — `status`, `finding_id`, `outcome`, `own_verdict`, `own_evidence`, `own_control`, `control_outcome`, `commit`, `notes` — plus `blind_disputed`, with `own_*` passed through from the derive result.

### 2.3 Removed

- The "first instruction" paragraph and Process step 2's "if you catch yourself having glanced … discard your search and restart it": the issue shows self-blinding does not hold, and the derive input now carries nothing to glance at.
- The `provenance` input and Process step 5. With a blind derivation, "never search an inherited finding less hard" holds by construction.
- The hard rule "NEVER read `finding.evidence` … before completing your own independent re-derivation" becomes the derive mode's `INPUT_UNBLIND` refusal plus the `$SPECS_PATH` rule.

The frontmatter `description` is rewritten as a stable capability blurb naming both modes.

## 3. Phase 7 orchestration (`commands/prd-ground.md`)

1. Build the set (unchanged) and cut it into batches (§1).
2. **Derive dispatches**, one per batch, at most four per Agent message. The paragraph beginning "Supply the finding **exactly as the agent's own Inputs contract declares it**" is replaced: the derive step is handed the question and never the answer, and the anchor rules (`class`, `frame_set_dir`, `inventory` always on a `[DG#n]`) are kept.
3. **Compare dispatches**, one per batch, each starting as soon as its derive batch returns.
4. **Statuses.** A batch-level refusal takes today's stop and message (`PRD_GROUND_VERIFY_COMMIT_MISMATCH`, `REPO_MISSING` … `STALE_INDEX`), naming the batch's findings. `INPUT_UNBLIND` and `INPUT_MISSING` stop the run and fire `emit-block` per Phase 11's capture-at-block invariant: this command built the dispatch wrong.
5. **Retry once.** A finding is incomplete when a step's return omits it, when its `own_evidence` comes back blank, when compare marks it `INCOMPLETE`, or when compare's echo of the blind result differs from the derive return. The echo differs only in a structured value: `own_verdict`, an evidence entry's `path` or `lines`, or `own_control`'s result. A reworded note is never a difference, because the orchestrator relays `derived` by hand and the final live smoke run paraphrased notes in both runs. It is re-dispatched once through the step that failed, as a batch of its own — for `INCOMPLETE`, a fresh derive of that finding, then a compare. After its retry, an `agree`, `extend` or `unprovable` whose blind verdict lacks only its owed control proceeds through the reconciliation and control normalisation — the record keeps the original's control, which compare ran — and the report notes it — `unprovable` too, since its branch writes neither the blind verdict nor its control. A finding still incomplete after its retry in any other way — missing from a return, a blank `own_evidence`, an `INCOMPLETE` entry with no outcome, a differing echo, or a `contradict` lacking its owed control — is not verified: an **on-file** one writes nothing, keeps its earlier outcome, is reported "not verified by this run", and the run continues; an **own-run** one stops with `PRD_GROUND_VERIFY_INCOMPLETE`, mirroring the incomplete-return rule under `contradict`.
6. **A disputed `contradict`** (added after the final live smoke run). A compare entry flagged `blind_disputed` whose `contradict` comes from a differing `own_verdict`, and not from the control normalisation, gets one fresh derive and one compare. A `contradict` the control normalisation forces is never disputable, even where `own_verdict` also differs: that route takes precedence, and it is deterministic. Where the two blind verdicts agree, the `contradict` proceeds on the second opinion's returns. Where they differ, the outcome is normalised to `unprovable`, the finding keeps its verdict, its notes state both blind verdicts and the first compare's dispute reason, and the report flags it "verification inconclusive — two blind re-derivations disagreed". The second opinion is not a retry; its own dispatches get one retry each.
7. **Unchanged from here:** reconciling `outcome` against `own_verdict`, the control normalisation, the own-run and on-file `contradict` writes, the class-4 sweep — whose re-dispatch now goes through both steps, batched per frame set, each finding it dispatches with one retry of its own — and "Nothing reaches Phase 8 unverified".
8. **Model routing.** Both steps take `review_model` (the §2 Opus chain, equal to the frontmatter pin). Under §10, both take `run_flags.enforced_model`. No new `model_routing` field.
9. **Final report.** The verifier tally opens with a filled-in verification block, Phase 1's arithmetic as the run came out. It gives K, N, the batches per repository and per frame set, the derive, compare, retry and second-opinion dispatches, and the on-file claim findings re-verified, since a headless run did not print Phase 1's line in either final smoke run. The tally also names every retry by finding id and step, and every dispute with how it settled.

## 4. Phase 1 cost warning

Printed as the first output of Phase 1, on every run that grounds code, whether or not the repositories are then prompted for — K filled in where they were named up front, left as the symbol where they are still to be prompted for. (It was first placed immediately before the repository prompt, and the live smoke run, handed its repositories up front, never reached it.) It never prints under `--no-code`, because no `[CG#n]` is produced or verified there. `/prd-ground` Phase 1 holds the line it prints and the definition of each symbol, and it is the authority on both; this spec does not quote the line. In summary, the line gives the claim count N, and the K×N claim findings plus K baselines that K repositories produce. It gives their verification batches and dispatches, K×⌈(N+1)/25⌉ each in two steps, because a repository's baseline counts toward its batches, plus ⌈D/25⌉×2 for each frame set that returns D design findings. It names the review model, which is Opus unless `--enforce-model` sets another, and it gives M, the on-file claim findings (baselines excluded) a re-run re-verifies.

## 5. Authorities and ripple

- **`workflows-core:grounding-format` §8** gains the structural rule: the step that re-derives is handed the premise and the source, and nothing of the finding's answer; verification is a blind re-derivation followed by a comparison. The Inputs matrix stays owned by the agent. §4.1's "Verification is unchanged" paragraph is re-read against the new process.
- **Sweep by subject**, over refinement 4's scope, counting before and after (refinements 6–8). Subjects: one verifier instance per finding; the verifier's `provenance` input; reading `evidence`/`control`/`cites` only after Process step 2; the self-enforced sequencing; and every citation of a Process step number, since the steps renumber. Known citing files: `commands/brd-split.md`, `commands/brd-interview.md`, `commands/brd-package.md`, `agents/design-grounder.md`, `agents/figure-reader.md`, `references/idea-format.md` (product-workflows); `references/read-only-repos.md`, `references/phase-handoff.md`, `agents/frame-describer.md`, `commands/frames.md` (workflows-core).
- **Docs tree:** `product-workflows/docs/commands/prd-ground.md`, both `docs/reference/agents.md` pages, `product-workflows/docs/reference/model-routing.md`, `product-workflows/docs/brd-workflow.md`.
- **Rules:** the `/prd-ground` line of `.claude/rules/brd-route.md`'s workflow map, which describes the verifier step.
- **`docs/maintainers/rationale.md`:** a new section holding the evidence (four of eight verifiers reporting contamination; the 278-dispatch arithmetic) and the rejected alternatives below, linked from the rule it explains.

## 6. Rejected alternatives

| Alternative | Why not |
|---|---|
| Keep one dispatch, seal the originals in a file the agent opens after deriving | Blind by instruction again; the issue's own second choice |
| Blind derive, with Phase 7 doing the comparison itself | Running controls and judging agreement moves to the session's model, which need not be Opus (conflicts with D1), and every result lands in the orchestrator's context |
| Per-finding two-step dispatch | Fixes #73 by doubling #74 |
| Continue the same agent with the withheld fields | Agent continuation is not available in every harness these commands run in |
| A cheaper tier or a sample for `NOT-PROVABLE` | Weakens a finding's verification (D1). A wrong `NOT-PROVABLE` where the code contradicts the premise sends a question to `/brd-interview`'s operator without the fact that would settle it |
| One repository-scope finding standing in for its `NOT-PROVABLE` mass | Same (D1): the claims under it are never individually re-derived |
| Carry outcomes forward across runs | D2 |
| Checkpoint and resume | D4: with batching, a lost pass is about 24 dispatches; resume brings validity, location and clean-up questions of its own |

## 7. Verification

1. The full gate chain from `.github/workflows/validate-catalog.yml`, as one `&&` chain, exit code read.
2. The sweep counts of §5, before and after.
3. An independent Opus review of the diff, then a fix wave for everything it finds, before any push.
4. A live smoke run, on a fixture built under the session scratchpad: an idea-route PRD folder with at most five `[FR#n]` rows and one small repository.
   - First run: the derive dispatches carry none of the four answer fields; outcomes come back through compare.
   - Plant an on-file `[CG#n]` with a wrong verdict at the current pin and re-run: it comes back `contradict`, is superseded, and gains a successor.
   - Dispatch `grounding-verifier` directly in derive mode with an `evidence` field: `INPUT_UNBLIND`.
   - Dispatch it directly in compare mode with a derive result whose absence verdict carries no `own_control`: `INCOMPLETE`. Phase 7's retry handling is verified by reading.

## 8. Release

- product-workflows: minor bump (the agent contract and Phase 7 change). workflows-core: minor bump (§8). Dated `CHANGELOG.md` sections; `plugin.json` and `marketplace.json` agree.
- The implementation branches from `main` after #70's fix (`iv-gu/specs-path-depth`) merges, so the version bumps do not collide.
- After merge, #73 and #74 are closed with a comment naming the commits.

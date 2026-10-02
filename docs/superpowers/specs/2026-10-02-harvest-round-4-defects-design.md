# Upstream harvest round 4 — Round 1: six defects in text we already ship

Date: 2026-10-02. Status: design approved in conversation; spec awaiting review. Branch: `iv-gu/harvest-r4` in all three editions.

## Background

A survey of the four upstreams this family borrows from, against the round-2 baseline (`docs/superpowers/harvest/NEXT.md`, *Harvest round 2*, surveyed 2026-08-21), found 21 portable items. The windows surveyed:

| Upstream | From | To | Commits |
|---|---|---|---|
| obra/superpowers | `b36e0829` (v6.3.0) | `8ca22dba` (v6.4.2) | 2 squashed releases |
| mattpocock/skills | `5b15a47` | `d81f3a1` (v1.3, unreleased changesets) | 39 |
| BMAD-METHOD | `67d876f1` | `4f61d4e7` (v6.12.0 + Unreleased) | 229 |
| github/spec-kit | `27f50f7e` (1.0.1) | `4a339209` (1.0.13) | 264 |

Six of the 21 are **defects in text the three editions already ship** — each found by reading an upstream fix and then finding the same failure in our own copy. This round fixes those six. Items 7–21 are recorded as backlog in `NEXT.md` (§ Release below) and are out of scope here.

The three editions: **this repository** (canonical — the `workflows-core`, `dev-workflows`, `product-workflows` and `docs-workflows` plugins), **the internal edition** (one `plugins/dev-workflows` plugin carrying the same workflows), and **the Copilot edition** (`ihudak-copilot-plugins`, `dev-workflows/skills/<name>/SKILL.md`, `skills/_shared/`, `agents/`). Paths below are relative to each edition's repository root.

## Goals

1. Each of the six defects is unreachable in all three editions after the round.
2. Every statement of each changed claim is found and rewritten — the full population, not the sites the edit started from (`CLAUDE.md` § Editing discipline, refinement 8).
3. Every verification check is shown red on the pre-change tree and green after it.

## Non-goals

- Items 7–21 of the survey (triage outcomes, re-review dispositions, effect-based severity, review focus, code-review edge cases and standards discovery, `/implement` look-before-asking, design contracts, PR merge-danger, `bug-diagnosis` drift, `impl-maintenance` check-vs-standard, `/epics` dependency checks, acceptance-criteria tests, redaction).
- Moving the internal and Copilot editions off their **rounds** rhythm for relentless callers, or this edition onto it. Recorded as a divergence (§ Release), not changed.
- Following mattpocock's rename of "decision tree" back to "design tree". Our reason for "decision tree" is our own: "design tree" collides with the `design.md` artifact.
- Editing `references/specification-format.md` (frozen).

## Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | How a landed ref is read (item 1) | From the merge that landed it: `<landing>^1...<branch_from>`. A fast-forward has no merge to read the fork point from and goes to the existing key-commit fallback. Rejected: always reading the recorded commit alone (`<commit>^!`) — it reads one run's commit where a branch carries several |
| D2 | `resolved_via` for a landed ref (item 1) | Unchanged — `local_ref` in this edition, the strategy's own value in the other two. The `base` sha in the output already says which range was read, and a new enum value would widen two report templates for no reader |
| D3 | An empty range (item 1) | Never a resolution, on any path — the forge-CLI path of the other two editions included |
| D4 | What dimension 10 judges (item 2) | The code as it stands after the change, starting from the diff. `exceeds` alone judges the diff |
| D5 | `exceeds` severity (item 2) | `MINOR`; `MAJOR` where it builds what the plan's or design's `Out of scope` names. Report-only: never escalated onto the spec |
| D6 | Grilling rhythm (items 4, 5) | Unchanged in every edition |
| D7 | The play-back and a bounded cap (item 5) | The play-back asks no decision, so it spends no slot of a bounded caller's cap |
| D8 | Versions | New behaviour → minor; a fix or wording → patch. This edition: `workflows-core` 1.10.0, `dev-workflows` 4.5.0, `product-workflows` 3.11.3, `docs-workflows` 1.4.6. Internal edition `dev-workflows` 2.66.0. Copilot edition `dev-workflows` 2.35.0 |
| D9 | Order and landing | This edition first, then the internal edition (a near-copy), then the Copilot edition (hand-adapted, never `cp`). Each edition: gates green, a whole-branch review to zero findings, then merge, push, delete the branch. The internal edition lands by the same route its 2.65.x releases took this week |

## Item 1 — `diff-summarizer` reports an empty diff for merged work

**Source.** superpowers `5bf4e780`, `skills/subagent-driven-development/scripts/review-package`: exit 3 where a review range is empty or HEAD does not descend from BASE, so a wrong range can no longer yield a clean review of nothing.

**Defect — this edition.** `plugins/docs-workflows/agents/diff-summarizer.md` takes each element's diff as `git diff <branch_to>...<branch_from>`. Once `branch_from` has landed on `branch_to` by a merge commit or a fast-forward, it is an ancestor of `branch_to`, the three-dot range's merge base *is* `branch_from`, and the range is empty. Nothing checks for zero files, so the element returns `resolved_via: local_ref`, `files_changed: 0`, `status: OK`. `/document` and `/release-notes` — which usually run after the merge — then write documentation without the code. The **Key-commit fallback** is reached only where `branch_from` is absent from the clone, so it never fires here. Reproduced in a scratch repository: three-dot range 0 files after `merge --no-ff`; the landing merge's `^1...<branch_from>` returns the branch's own two files.

**Defect — the internal and Copilot editions.** `agents/diff-summarizer.md` Strategy 1 derives the base as `merge-base <target_branch> <head>`, which returns `head` itself once the PR has merged; Strategy 2 picks a head and inherits the same derivation. The default PR filter is MERGED-only, so these strategies meet exactly the case they cannot read. Strategy 3 reads a merge commit correctly, but only after 1 and 2 have failed — and an empty range is not a failure today.

**Change — this edition.**
- `agents/diff-summarizer.md`, after the *`refs` is the shape the callers have* paragraph: a new rule. Before taking an element's diff, test `git merge-base --is-ancestor <branch_from> <branch_to>`. Not landed → the three-dot range as today. Landed →
  1. `landing` = the last line of `git rev-list --first-parent --ancestry-path <branch_from>..<branch_to>` — the oldest commit on `branch_to`'s first-parent line that descends from `branch_from`;
  2. where `landing` exists, has two or more parents, and `branch_from` is **not** an ancestor of `<landing>^1` (it arrived through a later parent), the element's diff is `<landing>^1...<branch_from>` — the branch's own work from its fork point, which is what the three-dot range read before the merge;
  3. otherwise — a fast-forward, or `branch_from` on `branch_to`'s first-parent line itself — there is no merge to read a fork point from, and the element goes to the Key-commit fallback.
- **An empty range is never a resolution.** Where the range an element resolved to changes no file, it is not reported `local_ref`: it goes to the Key-commit fallback, and where that finds nothing, to `unresolved_prs` with the range named in the reason.
- The Key-commit fallback's *Reached only where* sentence widens to the two new entries; its exclusivity wording is swept (refinement 3).
- `## Hard rules`: one new rule — never report an empty range as resolved.
- `references/handoff/diff-summarizer.md`: the same rule, stated where the handoff states the range.
- `plugins/workflows-core/references/implementation-format.md` §1, *Branch for convenience, commit for durability*: rewritten to what is true per merge style. After a merge commit or a fast-forward the recorded commit is reachable from the base; after a squash-merge it survives only while a clone still holds it, which is why `diff-summarizer` falls back to the key-commit search there.

**Change — the internal and Copilot editions.** `agents/diff-summarizer.md` Strategies 1 and 2: once a head is chosen, test `merge-base --is-ancestor <head> <target_branch>` before deriving the base. Landed → locate `landing` as above; where it is a merge that brought `head` in through a later parent, base = `<landing>^1` and the diff is `<landing>^1...<head>` under the strategy's own `resolved_via`; otherwise fall through to Strategy 3. One rule beside *If all four strategies fail*: a strategy — the forge-CLI path included — whose range changes no file has not resolved the PR, and falls through. A one-line hard rule, as in this edition. `references/handoff/diff-summarizer.md` (Copilot: `skills/_shared/handoff/diff-summarizer.md`) where it states a strategy's range.

**Claim subject to sweep.** How `diff-summarizer` turns a ref into a range, and when its fallback is reached — in the agent, its handoff, `implementation-format.md`, both callers' phases that build `refs`, and each edition's `docs/` pages for `/document`, `/release-notes` and the agent table.

## Item 2 — code review's spec coverage reads the diff only

**Source.** spec-kit `68b94af0` (#4621), `templates/commands/converge.md` §4: verify every task whether or not it is ticked ("completion claims are not evidence"), verify current behaviour, and flag code that "contradicts, exceeds, or falls outside the stated intent". `unrequested` was in upstream's gap set when this family adopted *converge* in July; the adoption left it out without recording why.

**Defect.** `plugins/dev-workflows/agents/code-review.md` dimension 10 says *"trace each `in_scope_ids` requirement against the diff"*. A keyed `/implement` run's in-scope IDs are the whole unit's (`commands/implement.md`, the in-scope `specs` rule), and the Epic picker offers *"implement anyway"* on an Epic that already holds a record. So a requirement an earlier run delivered is absent from this diff and classified `missing` — `MAJOR` with no recorded deferral. That sends `review-fixer` after work that exists, and step 7.5 writes a spurious `- [ ]` note onto the spec. The `implements [ACxx]` tags `risk-planner` puts on plan steps are claims about coverage, and nothing marks them as such. Nothing reports code that does more than the plan or spec asks.

**Change (all three editions).** Dimension 10:
- classifies each in-scope requirement against **the code as it stands after the change**: start from the diff; where the diff does not deliver a requirement, search the codebase before classifying it; a requirement already present is `satisfied`, counted as *already present*;
- states that a plan step's `implements [ID]` tag, an earlier implementation record and a ticked box are claims, not evidence — the behaviour is verified in the code either way;
- adds **`exceeds`**: behaviour this change adds that no in-scope requirement and no plan step asks for, judged on the diff only (code that predates the change is not this change's over-build). Severity per D5.

The output template's coverage line gains the *already present* count and an `exceeds` count, and its finding line gains `exceeds`. `commands/implement.md` step 7.5 states that `exceeds` is reported in Phase 5 and never written onto the spec; the Phase 5 report template's conformance line lists `exceeds` beside `missing`/`partial`/`contradicts`. The internal edition's `commands/implement.md` and the Copilot edition's `skills/implement/SKILL.md` carry the same two sites.

**Claim subject to sweep.** What dimension 10 classifies against, and its classification set — in the agent, `/implement` (step 7.5, Phase 4.5, Phase 5, Hard rules), the `docs/` pages for `/implement` and the agent table, and the rules and instruction files of each edition (`.claude/rules/` here; the internal edition's `.claude/rules/`; the Copilot edition's `.github/instructions/`, each kept under 20,000 characters).

## Item 3 — `risk-planner` carries a rule upstream has withdrawn

**Source.** superpowers `8ca22dba` (#2333), `skills/writing-plans/SKILL.md`. *No Placeholders* — including "steps that describe what without how" — was removed and replaced by *What a Step Contains*: a step is unambiguous, not complete. Upstream measured plans at a quarter of the time and about a third of the tokens, still catching 9/9 planted defects, and names Opus over-implementing at plan time as the cause. spec-kit `072ab333` (#4430), `templates/commands/tasks.md`, adds the companion rule: quote a recorded field constraint verbatim in the task, because "the implementing agent can silently invent its own value".

**Defect.** `plugins/dev-workflows/agents/risk-planner.md` *Planning discipline* → *No placeholders* still says *"any step that says *what* without *how* … a fresh engineer could not act on"* — the withdrawn wording, on an agent that runs on the Opus chain. `NEVER produce code patches` stops a full patch but not a step written at pseudo-code size. Nothing asks a step to carry the constraint values the design records; `code-review` dimension 1 checks code against the plan, and dimension 10 traces only `[Uxx]`/`[ACxx]`/`[TCxx]` IDs, so a constraint recorded only in `design.md` is checked by nothing.

**Change (all three editions).** *No placeholders* is replaced by **Unambiguous, not complete**: a step is done when the implementer can do exactly one reasonable thing from it. It names the file; for anything new, its exact signature; every value the spec or design pins, **quoted verbatim** — a maximum length, required vs nullable, an enum's values, a validation rule — never paraphrased or left to be looked up; and for a verification step, the command and the output that means it passed. The self-review before returning checks for both failures — a line that decides nothing (the existing examples kept) and a step that writes the body the implementer would write — plus a **proportion check**: a plan several times longer than the change it describes has written the code.

**Claim subject to sweep.** The planner's step-content rule — the agent, its `docs/` agent-table row, and any page that quotes *No placeholders*. `CHANGELOG.md` and `docs/superpowers/` keep the history.

## Item 4 — stale "design tree" wording

**Source.** mattpocock `3bb587f` renamed it "decision tree"; `a4b2009` renamed it back. Our 2026-07-29 harvest adopted "decision tree" for our own reason (D6, Non-goals).

**Defect.** The July rename reached the reference only. This edition: 7 command sites (`dev-workflows/commands/design.md`; `product-workflows/commands/{create-prd,create-ard,specify}.md`; `product-workflows/commands/idea.md` ×3) and 1 docs page (`product-workflows/docs/reference/model-routing.md`) still say "design tree" — and this edition's reference has since replaced *walk the tree* with **ask from the frontier**, so "walk the design tree in dependency order" names a mechanic the reference no longer defines. The internal and Copilot editions' references contradict themselves — *"Walk the decision tree"* in Mechanics, *"Map the design tree"* in Rhythm — and their callers and `docs/` pages carry "design tree" too.

**Change.** This edition: *walk the design tree in dependency order* → *ask from the frontier*; *seed the design tree* and *walks the design tree* → wording in the reference's own terms (settled decisions, the frontier). The internal and Copilot editions: "design tree" → "decision tree" at every site, the reference's Rhythm included. **Expected after-count of "design tree"** outside `CHANGELOG.md` and `docs/superpowers/`: 0 in each edition (refinement 7: before-count taken and stated in the plan).

## Item 5 — this edition's grill has no confirmation gate; no edition plays its understanding back

**Source.** mattpocock `grilling`, last line (`0e9a072`, current): do not act on the understanding until the user confirms it. superpowers `5bf4e780` (#2258), `skills/brainstorming/SKILL.md`, *Establish Shared Understanding*: write the understanding back — outcome, constraints, success criteria, what the user said separated from what was assumed — and invite correction.

**Defect.** `plugins/workflows-core/references/grilling-technique.md` Mechanics ends *"Continue until you and the user reach a **shared understanding** for the current section, then write that section"*, which leaves the judgement that the interview is done with the agent. The internal and Copilot editions adopted upstream's confirmation gate (their `grilling-technique.md` Mechanics, *The confirmation gate*, and the autonomous-invocation rule that the gate cannot be self-satisfied); the July harvest here skipped it as "already a superset", which covered only the autonomous half. No edition plays the understanding back for correction at the gate.

**Change — this edition.** The last Mechanics bullet becomes **the confirmation gate**, ported from the other editions without their rounds references: shared understanding is the user's to declare; the gate fires wherever understanding is about to become an artifact or an irreversible step — before writing a section, and again before a reviewer dispatch, a handoff or a commit; a caller that writes section by section closes it per section. Which callers those are is named by an observable trigger — the caller's own interview-technique paragraph says it writes *each section* or *that stage's section* — not by a list. *Autonomous / background invocation* gains the rule that the gate cannot be self-satisfied, and the understanding is reported unconfirmed. *Relationship to the upstream technique* records the port. The callers' *continue to shared understanding then write …* clauses (`design.md`, `create-prd.md`, `create-ard.md`, `specify.md`) and `/idea`'s technique sentence say *clear the confirmation gate before writing …*, as the other editions' callers do.

**Change — all three editions.** At the gate, **play the understanding back**: a few lines stating what is settled for the part about to be written — the intended outcome, the constraints, what success looks like — marking what the user said and what was inferred, then asking for confirmation or correction. The play-back asks no decision and spends no slot of a bounded caller's cap (D7).

**Claim subject to sweep.** When the grill may write — every "shared understanding" sentence and every caller's interview-technique paragraph, plus the `docs/` pages that describe the grill (`/prompt-grill-me`, `/idea`, the getting-started pages).

## Item 6 — `test-baseliner` can record a failing suite as passing

**Source.** spec-kit `d743a695` (#4604), `.github/workflows/bug-test.md`: capture the original exit code before filtering output; successful filtering must not hide a command failure.

**Defect.** `plugins/dev-workflows/agents/test-baseliner.md` capture step 2 says only to run each suite's command; *Exit status is the result where the output yields no other* (a `Make`-row, `declared` or `hinted` suite with no parseable counts) makes the exit status that suite's only result. Nothing forbids running the command through `| tail` or `| grep`, whose exit status is the filter's, so a failing suite exits 0 and is recorded passing — silently, and on exactly the suites with nothing else to go on.

**Change (all three editions).** Capture step 2 gains: run each suite's command as it stands, never piped through a filter; where output is too long to read whole, redirect it to a temp file and capture the status in the same call (`<command> > <file> 2>&1; echo "exit=$?"`), then read the file. Verify step 3 applies capture step 2's rule by citation. `references/handoff/test-baseliner.md` and `docs/reference/test-suite-detection.md` are swept for any statement of how a suite's status is read.

## Release

- **Changelogs and versions** per D8, each `CHANGELOG.md` section dated before it reaches `main` (check 18). Copilot: `dev-workflows/.plugin/plugin.json` and the marketplace entry.
- **Harvest record.** `docs/superpowers/harvest/NEXT.md` gains a *Harvest round 4* entry, written last (after the final fix wave): the four baselines above; what Round 1 shipped, with each edition's merge commit and version; the backlog (items 7–21, each with its upstream source, one-line rationale and the editions it applies to); the items considered and rejected again with their reasons; and two recorded divergences — the rhythm split (D6) and the upstream rename back to "design tree" (Non-goals).
- **Installed copies.** After pushing: `claude plugin update` for `workflows-core`, `dev-workflows`, `product-workflows` and `docs-workflows` `@shipwright`, then a restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

## Verification

- **Gates.** Each edition's own chain (`.github/workflows/validate-catalog.yml` here), run as one `&&` chain and read by its printed exit code.
- **Red-before, green-after.** For each item, a check that fails on the pre-change tree and passes after: item 1 by a scratch repository driven through the agent's own commands (merge commit, fast-forward, squash, and a not-yet-landed branch), plus a grep for the new rule in each file of its population; items 2–6 by greps for the retired strings (count 0 after) and the new rule names (count ≥ 1 in every file of the population), each with its scope and command stated beside the number.
- **Review.** A whole-branch review per edition, fixed to zero findings — minors and nits included — before merge. Cross-edition parity is checked by diffing each changed passage of the internal and Copilot editions against this edition's, dialect differences aside.

## Risks

- **Item 1's ancestry-path lookup on unusual histories** — an octopus merge, a branch merged into an intermediate branch before `branch_to`, or a merge whose first parent is the feature branch (merged "backwards"). The second-parent test (`branch_from` not an ancestor of `<landing>^1`) sends every such case to the fallback rather than to a wrong range; the plan's scratch-repository check covers the intermediate-branch case explicitly.
- **Item 2's codebase search costs Opus tokens** on runs with many in-scope IDs. Bounded: it runs only for a requirement the diff does not deliver.
- **Item 5 adds a turn** to every grilling caller. That turn is the point; D7 keeps it off a bounded caller's cap.

# Lean context, D: the Phase-0 handoff check reads its own part, and every asking command loads the question rules first

D follows lean context part 1 (`2026-10-20-lean-context-loader-design.md`, merged as `0f68a91e`; verification record `docs/superpowers/verification/2026-10-20-lean-context-loader.md`). It is two small changes that the part-1 live runs showed were worth making. Each has a measured reason. Part 3, which turns procedures into scripts, follows D and is not in it.

## Why

Part 1 made every run work from a reference's own words and never from a slice of it (Rulings 68 and 69). Its seven blind runs found nothing worse, but every run cost more: +6% to +56% against its comparison. The extra cost is the procedure references, read whole, early in the run, and carried on every later call. A read costs its size once to write to the cache, and then its size again on every later call that carries it, so a read at the start of a run costs far more than the same read at the end.

The user's decision after run 7 was to split the large procedure references by entry point, as part 1 split the four rulebooks. The dependency maps part 1 made before deciding (`docs/superpowers/research/2026-10-20-lean-context-loader-maps/`) were then read against that plan. **The user's rule: a split needs a reason and an outcome better than before; it is not done for its own sake, and quality stays above cost within reason.** Measured against that rule:

| Reference | Carried cost in part 1's seven runs | What one entry point needs (maps) | Outcome |
|---|---|---|---|
| `specs-repo-git` (120k) | $7.49 | `specs-preflight` 86%, `commit-artifacts` 71% | **Not split.** Most of the file is rare-case machinery (session-branch mode, guards, a misrooted `SPECS_PATH`, 64% of it), which every entry point must have in front of it. Part 3's script is the way to stop reading it. |
| `phase-handoff` (138k) | $5.59 | `require-on-main` 44% (49% with §2.2, which two consumers' checks apply); the handoff phase (consent plus `handoff-to-main`) 82% | **Split for `require-on-main` only** (this design, A). The check runs at Phase 0, so its read is carried by the whole run. The handoff phase needs most of the file and runs late, so it keeps reading the whole file. |
| `addressing` (65k) | $2.82 | `resolve-address` 80% | Not split: about 13k a run, against some 260 citations to re-place. |
| `model-routing/classification` (46k) | $1.94 | not mapped | Not split: about $0.28 a run at most, less than mapping and verifying a split would cost. |
| `cost-emission` (67k) | $1.28 | `emit-cost` 80–90% | Not split; read at the end of a run, and largely scriptable (part 3). |
| `run-flags` (31k) | $0.39 | `strip-run-flags` 86% | Not split. |

The consent step was first estimated at "a few k". The map shows it needs about 63% of the file, because the offered array is checked against the deliverable's class register (§4.0) and the next phase's row-F table (§3.4). A handoff phase therefore reads the whole file, as it does today.

**Part 1's own splits were re-checked against the same rule, by cost rather than by characters**, from the seven runs (each part read priced where it happened, against one whole read at the first moment a part was needed): `escalation-rules` about $0.55 split against $0.85 unsplit, `next-phase-offer` $0.30 against $0.43, `finding-triage` $0.22 against $0.30, `session-hygiene` $0.14 against $0.17. The one case where a split costs more is `session-hygiene` in a run that reads both its parts at the very end — about half a cent. Nothing is un-split.

**The question rules.** In runs 4 (`/security-workflows:scan`) and 7 (`/dev-workflows:design`), the run never loaded `escalation-rules core` — §0's array shape, *Choice lists are presented verbatim*, the `(Recommended)` marker, *A selection carries no text* — yet asked the user questions. Today's `main` before part 1 skipped it the same way (sessions `f9684b8b` and `beebc3f3`), so it is pre-existing. Both commands cite it, but inside a rule statement — `/design`'s "**Rule: Ask, don't guess.** … (`Skill(skill: "workflows-core:reference", args: "escalation-rules core")` §0)" — and a run reads a citation inside a rule as a source note, not as a step. The output complied, because the commands restate the rule; the user decided it must still be loaded, as an explicit step.

## Decided by the user

- **Quality first, within reason.** "Keeping the quality above the costs (as long as it's reasonable — we're not paying $1M for 1% of quality gain)."
- **No split without a reason and a better outcome.** "If splitting makes something worse, we should not do it."
- D is: `phase-handoff`'s Phase-0 check as its own part; the handoff phase reads the whole file; `escalation-rules core` as an explicit load step in every command that asks; nothing from part 1 un-split; `model-routing/classification` not measured further.
- Quality is checked as in part 1: blind live runs against the latest results, plus Claude's rule-by-rule reading. A difference is a finding to judge: worse is a defect to fix; better is an improvement, recorded where a user sees it.

## Goals

1. **A consumer's Phase-0 `require-on-main` reads its own part** — about half of `phase-handoff` — instead of the whole file, with every rule that check applies in front of it.
2. **Every command that asks the user a question loads `escalation-rules core` as a step of its own**, before the first question it can ask.
3. **Nothing a run does changes**, beyond loading the question rules where it did not before: every step, question, review, fix and record stays.

## Non-goals

- Splitting `specs-repo-git`, `addressing`, `cost-emission`, `run-flags` or `model-routing/classification` (measured above; part 3 takes `specs-repo-git` first).
- Narrowing the handoff phase: the consent step and `handoff-to-main` keep reading the whole file, and the reuse rule keeps it to one read per phase.
- Narrowing `require-on-main` per caller to its own §3.4 rows (27–30%). The maps call it fragile: rows are multi-caller, `/conformance` has none, and the interpretive prose after the table binds several callers. §3.4 stays whole in the part. *(My call.)*
- Un-splitting any of part 1's four rulebooks.
- The internal editions.

## Anti-goals (a failure even if the numbers improve)

- A run applying a `require-on-main` rule — a stop's four-part format, the owner/repo derivation for the pull-request probe, a §3.4 row — that is not in front of it.
- A question asked before the question rules are loaded, in any command this design converts.
- A request for the new part, made where the whole file was needed, quietly narrowing a later step.

## The design

### A. `require-on-main` has its own generated file

- **The source stays one file**, `plugins/workflows-core/references/phase-handoff.md`. Checks 11 and 16 keep reading it, and every citation of `phase-handoff` keeps meaning the whole file.
- **One generated file holds the entry point and everything it needs**, produced by `scripts/reference-parts.py` from markers in the source, committed, and gated for freshness exactly as part 1's part files are. Per the map (`phase-handoff.md` §2.2), it needs: the preamble (its scope line and *The principle*); §1, the hard rules — rule 5, "`require-on-main` is fatal by design", is cited nowhere in §3, yet §3.7 relies on it; all of §3, §3.4 whole; §2.6's `OWNER_REPO` derivation, which §3.5's probe uses; §4.4, the stop contract, which no line inside §3 points at; §4.0's *Never infer an artifact's merged-ness from a sibling's gate*; and §5's header with rules 2 and 3. The map puts that at about 60k of 137k.
- **It also holds every rule a consumer's check step applies from outside §3.** Read at `11a4fa70`, two consumers' check steps apply §2.2's rules: `/conformance` Phase 0 step 5 (§2.2 rules 3–4, to tell which branch holds the newer record) and `/brd-reconcile`'s cross-BRD write guard (§2.2 rule 3). So §2.2 joins the part, about 6.7k more — about 67k, 49% of the file. *(My call: under half of the file, and the alternative is a whole read at Phase 0 in those two commands, which is what the split exists to stop.)*
- **A citation at the check step that only explains is reworded so it implies no load.** The other out-of-part citations in the consumers' check sections explain rather than apply — "which is why §4.0 classes it advisory" (`/brd-split`), "the three dots are load-bearing, as in §2.2" (`/conformance`), §2.3 and §4.1 asides (`/brd-package`, `/prd-ground`, `/create-prd`). Under the preamble, a citation of `phase-handoff` loads the reference, so each would pull the whole file in beside the part. Each is reworded the way part 1 stopped three reviewer agents' `finding-triage` citations from implying a load, within check 16's contract. The plan re-derives the list against the tree; the builder check found six such sites in five commands.
- **A gate holds it**: in a `##` section that requests `phase-handoff require-on-main`, a citation of a `phase-handoff` section the part does not hold fails, closed, unless that sentence also loads the whole reference.
- **Restructure before generating, so the needs are visible in the text** (map §2.5): §3 says that every stopping row's message follows the stop contract, by name; the *Never infer* rule is stated where a consumer reads it, or declared; §2.6's derivation becomes a named block, which §3.5, `code-handoff`, `finish-and-handoff` and `architecture-promotion` can name; and the preamble, §1 and §5 rules 2–3 are declared. Positional pointers that would cross out of the part become names.
- **Its cross-file needs are stated, not assumed, and keep today's semantics.** `require-on-main` uses `specs-repo-git` §3.1, §3.2, §3.3 and §8, and `read-only-repos` (map §2.3). The run looks them up: any read of `specs-repo-git` made in this run serves, as the loader's reuse rule allows for looking up a rule, and a run with none in the conversation loads it whole. That is what happens today — in most consumers the preflight has read `specs-repo-git` in the same phase, while `/ready` (Phase 1), `/epics` (Phase 2.6), `/brd-proposal` (Phase 4) and `/brd-reconcile` (its cross-BRD write guard) run the check a phase or more after their preflight. The part says so; it adds no read those four do not make today. *(My call: requiring a same-phase read would add a 120k read to those four runs, and Goal 3 keeps every run as it is.)*
- **Requests.** `args: "phase-handoff require-on-main"` reads the generated file and executes the entry point. Every other request — `args: "phase-handoff"`, `args: "phase-handoff handoff-to-main"` — reads the whole source, as today. The loader skill (and the `model-routing` skill's copy of its rule, where it states one) names this file. How it is named (a list beside part 1's split list, or the rulebooks' mechanism with a part the handoff requests never touch) is the builder's call, under one constraint: no request but `require-on-main` changes what it reads.
- **The reuse rule is unchanged.** Ruling 69's bound still holds: the part is read where the check executes, and a later step that needs any other section of `phase-handoff` reads the whole file, because a partial read covers no request for the whole.
- **Callers.** The 18 `require-on-main` call sites in 14 files keep their request form. `/brd-interview` Phase 0 step 6 executes `require-on-main` with no loader call — it reaches §3 through its whole-file load at Phase 10 — and gets an explicit request at that step. Any other consumer that reaches `require-on-main` without a call is found and converted the same way.

### B. The question rules load as a step

- **Every command that presents the user a choice list** loads `escalation-rules core` with `Skill(skill: "workflows-core:reference", args: "escalation-rules core")` as an imperative step of its own, placed before the first question the run can reach. Not a parenthetical inside a rule statement; the existing citations stay as citations. At `11a4fa70` that is the 31 commands whose text holds a `choices:` array, in all five plugins, plus `/frames`, which presents `phase-handoff` §4.3's consent array and has none of its own (re-derive the set). Commands that only ask free-text questions — `/diagnose-session`, `/feedback`, `/prompt-grill-me` — present no choice list and are out: core's rules govern choice lists. *(My call.)*
- `core` is 10.1k, read once early; a command that later loads another `escalation-rules` part reads core again inside that part, as part 1 designed. That repetition is accepted: it is mid-run or late, and the measured split still costs less than the whole file.
- **A gate holds it**: a command with a `choices:` array, or one that presents `phase-handoff` §4.3's array, and no such step before its first question fails, closed — as `reference-parts.py check-citations` fails a missing load-by-part paragraph. Where the gate cannot tell a step from a citation, it says what it accepts, and the live runs and the reading check the rest.

## The quality check

- **The reading.** Claude reads the generated `require-on-main` file against every consumer's Phase-0 step and the rows it applies: every rule that consumer's check applies must be in the part or in a load the step makes. And it reads each converted command's first question against its new load step. Each difference is classified, as in part 1; a worse one is fixed before the runs.
- **The live runs** — the five of part 1's seven that D changes, on the `ihudak-e2e` copies, restored with part 1's restore scripts (now in `~/e2e-live/lean-context-part1/`), with answers replayed as part 1 replayed them. Each is compared blind against part 1's run of it, which is today's `main`:

| Run | What D changes in it | Part 1's session |
|---|---|---|
| `/dev-workflows:conformance BOOK-2-01-02` | Phase-0 `require-on-main`; core load | `cd041db4` |
| `/product-workflows:prd-ground BOOK-2-01` | Phase-0 `require-on-main`; core load | `8fa7aefc` |
| `/security-workflows:scan BOOK-2-01-02` | core load (it skipped it in part 1) | `796118d3` |
| `/dev-workflows:implement BOOK-2-01-02` (route 3) | Phase-0 `require-on-main`; core load | `586ecaf9` |
| `/dev-workflows:design BOOK-1-01` | Phase-0 `require-on-main`; core load (it skipped it in part 1) | `6adf2f0b` |

`/release-notes` and run B's direct `/implement` are left out: neither reaches `require-on-main`, and their commands' core load is the same edit route 3 and `/conformance` exercise. *(My call.)* A blind judge (Opus) compares each pair. A result judged worse is attributed from the transcripts first; a re-run of part 1 on the same inputs is the fallback, since part 1 is today's `main`.

**D is done when:**

1. Every gate passes, the two new checks included.
2. The reading finds nothing worse.
3. No blind comparison finds a result worse because of D.
4. The measurements are reported run by run, as in part 1: reference characters read into the main session, main-session cache reads, total and main cost against part 1's run — with the Phase-0 `phase-handoff` read at the part's size in every consumer run, and `escalation-rules core` loaded before the first question in all five. There is no cost bar.

## Constraints

- Prose is executed: every moved sentence is re-read where it lands, for both faces of *A sentence is true in the context it was written in* (`CLAUDE.md` § Editing discipline).
- The claim sweep runs on every rule whose location or extent changes, and on every sentence that says `phase-handoff` is read whole at Phase 0 or that the procedure references stay whole (`.claude/rules/claim-sweep.md`) — part 1's verification record is history and is not edited.
- `workflows-core` takes a minor version; each dependent whose commands change takes its own bump; each changelog section is dated before it reaches `main`; `.claude/rules/plugin-updates.md` gets a coupling line wherever a dependent needs the new `workflows-core`.
- The docs tree documents the generated `require-on-main` file and the two new checks (`check-docs.sh`'s docs checks; `.claude/rules/gates-reference-parts.md`).
- Checks 11, 16 and 20 keep passing unchanged in what they enforce.
- The verification record is written last, with the SDD rulings and ledger preserved beside it.

## Left to the builder

- How the loader names the generated `require-on-main` file, under A's constraint.
- The marker form for an entry point's generated file, if it differs from part 1's part markers.
- The exact restructure of §2.6, §3, §4.0 and §4.4, within A's list.
- The exact wording and placement of each command's load step, within B.
- How the new checks recognise a load step and an out-of-part citation, within "fails closed".

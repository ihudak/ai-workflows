# Lean context, part 1: the shared loader reads less, never a rule less

The first of three parts of the lean-context work that follows sub-project F part 1 (`2026-10-17-implement-coding-subagents-design.md`). Part 2 splits `/dev-workflows:implement`'s own text into a core plus per-phase files; part 3 turns procedures that usually conclude "nothing to do" into scripts. Each part has its own design, plan and live check. This document is part 1 only.

## Why

F part 1 moved `/implement`'s coding into subagents so the orchestrator would carry less. The re-measurement on 2026-10-20 (route 3, the three-file [SEC#1] fix, on the `ihudak-e2e` copies) showed the orchestrator still carries too much: its cost entry was $18.91 against $15.63 before F, all of the gap in the main session, whose subagents now cost less than before. Its first call held 181k tokens — a 65k floor any fresh session carries in this setup, plus 116k of `implement.md` (part 2's subject) — and over the run it read about 473k characters of reference text, roughly half of it not needed for that run.

One cause is shared by every command in the family. The loader skill (`plugins/workflows-core/skills/reference/SKILL.md`), through which 37 commands and 28 agents read `workflows-core`'s 37 references (about 1.03M characters), says:

> Read `${CLAUDE_PLUGIN_ROOT}/references/<the first argument>.md` and treat it as the single source of truth for the current step. When a second argument is present, execute that entry point of it inline. Never paraphrase, summarise, or cache its contents.

So every call reads a whole file, and a second call for the same file reads it again. Two consequences, both measured:

- **The same file read twice in one run.** The 21 producer call sites that load all of `phase-handoff` (136.5k characters) for their consent step then call the loader again for `handoff-to-main`, reading the file a second time — about 273k characters where the run needs 112k. `/specify`, `/epics` and `/design` load `escalation-rules` (53.8k) up to four times each.
- **Whole rulebooks loaded for one rule.** `review-fixer` reloads all of `finding-triage` (18.1k) on every dispatch to apply its patch gate (1.6k). Route 3 read all 18.1k to triage a review that returned no findings (about 2.7k applies). The 23 resume-pointer steps load all of `session-hygiene` (11.8k) for its §1 (5.3k).

The commit that added the loader (`a0663947`) records why it exists — a command cannot resolve another plugin's `${CLAUDE_PLUGIN_ROOT}` — but no reason for "never cache". Its evident intent, which this design keeps, is that a run works from the reference's own words, never from memory or a paraphrase.

## What was measured before deciding

Five read-only maps (session scratch, `loader-map/*.md`) traced, for each large reference, what every requested entry point depends on elsewhere in its file. They settled what this part does and does not do:

- **Procedure references do not slice safely.** Most entry points need 70–90% of their file: `specs-repo-git`'s two entry points 71–86%, `cost-emission`'s `emit-cost` 80–90%, `addressing`'s `resolve-address` 80%, `run-flags`' `strip-run-flags` 86%, `feedback-emission` 67–78%, `followup-emission` 84%. And a narrower load drops rules silently, in at least seven places found — among them: cost and feedback files filed under a wrong directory because their path rule lives in `specs-repo-git` and they never load it; `require-on-main` stops losing their fix commands because the stop contract (`phase-handoff` §4.4) is pointed at only by callers; `unit-branch`'s whole-key boundary living in another section, so that `ACME-7` would match `[ACME-77]`; the nine `docs-grounding` callers dispatching and consuming the grounder with no further load, correct today only because the first load read the whole file.
- **Rulebook references do split**, behind a few fixes, because callers use them rule by rule: `escalation-rules`, `next-phase-offer`, `finding-triage`, `session-hygiene`.

## Decided by the user

- The whole family, not `/implement` alone.
- **Quality first.** "If the shared reference loader saves a few bucks at the cost of the quality degradation, then we keep the quality."
- A small run whose risk or complexity class is high keeps the whole route; one implementer, no second coding path. (Binding on parts 2 and 3; nothing in part 1 changes a route.)
- Quality is checked by **the same live runs compared blind against today's results**, plus Claude's own rule-by-rule reading of how a run behaves under the old instructions and under the new. A difference is a finding to judge: worse is a defect to fix; better is an improvement, recorded where a user would see it.
- The blind set (below), chosen by Claude from the demo's recorded runs and approved.
- Part 1 is this narrowed form: no reading the same reference twice; the four rulebooks split behind a gate; the procedure references stay whole.

## Goals

1. **No reference is read twice in one run** when its text is still in the conversation word for word.
2. **The four rulebooks load by part**: a caller that needs one rule loads that rule's part plus the part that binds every caller, not the whole file.
3. **A gate proves no rule went missing**: every rule a converted caller cites lies in a part it loads. The same gate is the safety net part 2 needs when it splits `implement.md`.
4. **Nothing a run does changes**: every step, question, review, fix and record stays; only how much text the run reads changes.

## Non-goals

- Slicing any procedure reference: `specs-repo-git`, `phase-handoff` (its entry points, and the new consent part one map proposed), `cost-emission`, `addressing`, `run-flags`, `feedback-emission`, `followup-emission`, `implementation-format`, `components`, `docs-grounding`. They stay whole files; goal 1 removes their repeated reads.
- `untrusted-content` (9.5k, 28 command loads, about 4k saved each): check 20 pins it as one file; left for later.
- Splitting `implement.md` (part 2) and scripting procedures (part 3).
- Deleting rationale or history. Where a part needs a rule that sits in a history paragraph, the rule moves; the history stays in the file.
- References that commands read by path from their own plugin (`dev-workflows`' `code-handoff`, `bug-diagnosis`). Route 3 read one `code-handoff` section twice in a single message; that is part 2's subject.
- The internal editions. Part 1 is written so it can be ported; porting is not in scope.

## Anti-goals (a failure even if the numbers improve)

- A run that no longer has a rule in front of it at the moment the rule applies.
- A model improvising a rule it used to read — the silent failure every map warned of.
- A part that silently lacks a rule its caller cites, or a request for a part that does not exist falling back to something else without saying so.
- A reuse that works from memory: a reference judged "already read" when its words are no longer in the conversation.

## The design

### A. Reuse within a run

The loader's instruction keeps "treat it as the single source of truth" and "never paraphrase or summarise", and replaces "never cache" with a reuse rule:

- Where the text the request needs — the whole file, or the requested part — is present **word for word** earlier in this conversation, from a read in this run, the run works from that text and reads nothing again.
- Otherwise it reads it: the file was never read, was read only in part and the request needs another part, or a compaction has replaced the earlier read with a summary. A summary of a reference is never its text.
- A request for a part is covered by an earlier read of the whole file.

This alone removes `phase-handoff`'s second read on every producer run and `escalation-rules`' repeated reads, for every caller, with no change to any caller.

### B. Parts for the four rulebooks

**One source file per reference, parts marked inside it; each part assembled ahead of time into a generated file.** *(My call.)*

- **The source stays one file.** Maintainers edit only the marked reference; checks 11, 16 and 20 keep the files they are keyed to.
- **The always part.** Each split reference marks one part that comes with every part, whatever the caller asks for.
- **Declared dependencies.** A part names the other parts it needs, in its own file or in another split reference where the coupling is always on — the review gate's rules in `escalation-rules` send every `BLOCK` that stays blocked to `finding-triage`'s on-re-review rules 2–3, so the review part declares them.
- **A generator assembles each part's file**: the always part, the part, its declared dependencies (transitively, across files where declared) and the rule index (C), in one file under a generated directory beside the references, headed "generated from `<reference>` — never edit". It is committed, and the gate fails when any generated file differs from what the generator produces from its source.
- **Why generated files rather than extraction at load time.** The agent that most needs a part, `review-fixer` (about 16.5k saved per dispatch), has no Bash, and Claude Code's `allowed-tools` grants a skill no tool its caller lacks; `doc-fixer` has neither Bash nor the loader and reads its reference by path. A generated file is one `Read` for every caller, and the model never assembles the always part itself.
- **Request form.** `args: "<name> <part>"` — the second token names a part on a split reference, as it names an entry point on the others today. The loader reads that part's generated file. An unknown part name is an error the run stops on, never a silent fall-back. A request with no part token reads the whole source file, exactly as today, so a caller that is not converted keeps working unchanged.
- **The reuse rule (A) applies to parts as to files**: a part whose generated file is already in the conversation word for word is not read again, and neither is any part of a source file already read whole.

The parts, from the maps (sizes in characters; the always part first):

| Reference | Always part | Other parts |
|---|---|---|
| `escalation-rules` (53.8k) | core, 7.3k — the precedence sentence, §0, *Choice lists are presented verbatim*, *The `(Recommended)` marker is unconditional*, *When a choice list fires* | closed-vocabulary pickers 7.9k (their 7 owners only); Phase-0 stops 4.9k (*key dir not found*, *Required path environment variable unset*); scan escalations 11.0k (repo resolution, stashing and dirty tree, refresh blocked, read-only mount); branch prefix 1.7k; the review gate 21.0k (*A recorded verdict names the version…* through the three *Review verdict BLOCK* rules, one block) |
| `next-phase-offer` (41.8k) | the offer contract, about 12.7k — rules 1–7, the merge clause and its resolution table, the surface section, the co-firing note | one routing-graph part per lane (0.6–7.0k); the `/epics` precondition (about 1.5k); the overflow rule for mid-run pickers. The maintainer material (adopter history, check-11 coverage, the widening measurement, about 11.5k) belongs to no part a run requests |
| `finding-triage` (18.1k) | the station rule (the orchestrator triages, never the fixer) | the patch gate 1.6k (fixer agents); the verification steps 2.1k (`/conformance`); a no-findings part about 2.7k; the triage step, settle prompts, on-re-review and reporting for orchestrators |
| `session-hygiene` (11.8k) | "guidance only — never auto-invokes `/compact`, `/clear`, `/rename`" | the resume pointer, §1, 5.3k (the 23 terminal steps); the guidance, §2–§5, about 7.3k (at the final report) |

**Fixes that must land before the split** (each from the maps; the plan re-derives the list against the files):

- `escalation-rules`: line 25's "see the next section" points at the wrong section — name *Closed-vocabulary pickers*; the paragraph saying what *Specify a different absolute path* does sits inside the `/epics` variant and moves to a lead-in the repo-resolution group shares; the unspent re-review's trigger ("the offer above counts such a verdict") and U1's "(above)" are restated by name; "A verdict that is not `BLOCK` spends neither half of the cap", now the opening of a history paragraph, is stated as the rule.
- `next-phase-offer`: the only statement of when `<merge-clause>` is **not** attached lives in the adopter-history paragraph and moves into the contract; the `/epics` precondition becomes its own part, since every lane that offers `/epics` needs it.
- `finding-triage`: the no-findings part states its three cases in its first lines — a `PASS` needs only the declined-to-judge rulings and the report line; a first review that is not `PASS` still reaches the settle prompt, since "no finding survives" is then vacuously true; a re-review that is `BLOCK` still takes on-re-review rules 2–3 — and sends the last two to their parts. The verification part maps keep, unverified and dismiss onto `/conformance`'s own outcomes. The first-review rule inside on-re-review rule 2, which `/implement`'s first review applies, is placed where that review loads it. The settle section's two pointers into on-re-review are made self-sufficient.
- Every positional pointer ("above", "below", "the next section", row numbers) that would cross a part boundary becomes a name.

**Callers.** A caller's citations reach their parts through the index (C), so most callers need no edit beyond the preamble. Explicit loader calls of the four rulebooks — which today load the whole file — become part requests at the step that needs the rule: `review-fixer`'s patch gate on every dispatch, `/conformance`'s verification, the 23 resume steps, the review-gated commands' review part, the 7 picker owners. Three reviewer agents (`docs-audit-reviewer`, `docs-scaffold-reviewer`, `proposal-reviewer`) cite `finding-triage` only to say the caller triages; they need nothing from it, so their citation stops implying a load, within check 16's contract.

### C. How a citation reaches its part

*(My call.)* Callers cite these rulebooks hundreds of times without a loader call — `escalation-rules` alone has 244 mentions in 46 files, 37 of which cite it with no explicit call, through the Core-references preamble ("Load it with `Skill(… args: "<name>")`"). Rewriting every citation as a part request would be hundreds of edits, and leaving them meaning "the whole file" would cancel the saving. Instead a citation names a rule, and the rule's part is loaded when the citation is reached:

- **Every generated part file opens with the reference's rule index**: each rule name — heading, italic or bold rule name, § number — with the one part that holds it. The always part is in every part file, so whichever part a run loads first brings the index with it.
- **The preamble gains one sentence for split references**: a citation of a split reference names a rule; before applying it, load the part the index gives for it, unless that part is already in the conversation; never apply such a rule from memory. Where no part of that reference has been loaded yet, the first load is the part the citation's rule maps to — the preamble names how to find it without the index (the generated directory lists one file per part, and the always part's file name is fixed).
- **Rules inside a part that cite another split reference** reach it the same way — except the always-on couplings, which the part declares and the generator bundles (B).
- **Timing comes from the citation itself**: a rule's part is loaded at the step that cites it, not earlier in the run. A rule a command relies on at run start — `/create-ard` Phase 2 and `/specify` Step B read `escalation-rules`' *A finding left open that needs a decision is recorded in the artifact* there — is loaded there, at run start, because that is where the command cites it.
- **What it costs**: a part is a loader call the first time a run cites one of its rules; reuse (A) makes every later citation of the same part free. A run that cites several parts makes several small loads where it made one large one.

### D. The gate

A new gate, run in CI with the others:

- Every split reference's markers are well formed: one always part, every part named once, every declared dependency names an existing part, and every rule name in the index maps to exactly one part.
- Every generated part file is exactly what the generator produces from its source.
- Every citation of a split reference's rule — in a command, an agent, another reference, or another part — resolves through the index to exactly one part; and every explicit part request names an existing part.
- **It fails closed**: a citation of a split reference it cannot place is a failure, never a pass; a rule name that matches two parts is a failure; a scan that matches nothing fails, as checks 11 and 20 do.
- Inside a part, a positional pointer is flagged.
- **What it cannot see**: whether a run loads the part at the moment the citation is reached. That is the preamble's instruction, checked by the rule-by-rule reading (E) and the live runs, not by the gate.

*(My call.)* It is a script of its own beside `check-id-grammar.sh`, not a check in `check-docs.sh`, whose body is shared byte for byte with the internal editions; the internal editions would otherwise receive a gate with nothing to check.

### E. The rule-by-rule reading

Before the live runs, Claude reads each converted caller under the old load and the new: what the caller had in front of it at each step before, what it has after, and every rule now absent at the moment it applies. Each difference is classified — worse is a defect fixed before the runs; better is an improvement, named in the changelog where a user would see it. The reading is written down for the reviewers.

## The quality check

The blind set, run on the `ihudak-e2e` copies with the start states restored from git, after part 1 is complete:

| Run | Baseline |
|---|---|
| `/dev-workflows:implement BOOK-2-01-02` (route 3, SIGNIFICANT keyed bug fix) | `beebc3f3`, 2026-10-20 |
| `/dev-workflows:implement`, direct, MODERATE (run B's Books-list filter) | `5023b937`, 2026-10-19 |
| `/dev-workflows:conformance BOOK-2-01-02` | demo `cba500c`, 2026-10-16 |
| `/product-workflows:prd-ground BOOK-2-01` | demo `8fe4723`, 2026-10-12 |
| `/docs-workflows:release-notes BOOK-2-01` | demo `68bf77f`, 2026-10-12 |
| `/security-workflows:scan`, whole repository | demo `d65028a2`, 2026-10-16 |
| `/dev-workflows:design BOOK-1-01` | demo `c78ffdb`, 2026-10-08 |

- Answers are replayed from each baseline's recorded session where it exists; `/release-notes`' session is gone, so its questions are answered as the baseline's artifacts show.
- A blind reviewer (Opus) compares each new result with its baseline.
- The demo baselines come from older plugin versions. Where a new result is judged worse, today's version runs on the same inputs, to tell whether part 1 or an earlier change caused it.

**Part 1 is done when:**

1. Every gate passes, the new one included.
2. The rule-by-rule reading finds nothing worse.
3. No blind comparison finds a result worse because of part 1.
4. The measurements are reported, run by run: reference characters read in the main session, main-session cache reads, and each cost entry against its baseline — with the repeated `phase-handoff` read gone from the producer runs. There is no cost bar; quality decides.

## Constraints

- Prose is executed: every moved sentence is re-read where it lands, and every pointer it carried (CLAUDE.md § Editing discipline, both faces of *A sentence is true in the context it was written in*).
- The claim sweep runs on every rule whose location or extent changes (`.claude/rules/claim-sweep.md`).
- `workflows-core` gets a minor version; each dependent whose text changes gets its own bump, its changelog section dated before it reaches `main`, and `.claude/rules/plugin-updates.md` a coupling line: a caller that requests a part needs the loader that serves parts.
- The docs tree documents the loader's request form and the new gate (`check-docs.sh`'s docs checks; `.claude/rules/gates.md`).
- Checks 11, 16 and 20 keep passing unchanged in what they enforce.

## Left to the builder

- The marker syntax, the generator's interface and its self-test, and the generated directory's name and place (it must sit where check 16's corpus relations still hold).
- The part names and the index format.
- The exact preamble sentence for split references, within C.
- Which explicit loader calls become part requests, per caller, with the gate as the check.
- How the gate recognises a cited rule, within "fails closed".
- How the reviewer agents' `finding-triage` citation stops implying a load.

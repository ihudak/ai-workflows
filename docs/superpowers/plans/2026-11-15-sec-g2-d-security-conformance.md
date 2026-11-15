# SEC-G2 D — Security Conformance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/dev-workflows:conformance` traces every threat-model mitigation to code — each design's `[DT#N]` Rules as new requirements, each `Mitigated by` pair joined to the `[AD#N]` Rule it names — lists where every threat that applies to the unit stands, and never accepts a mitigation's discrepancy.

**Architecture:**
- No new command, agent, branch prefix, id prefix, role, script or plugin dependency. `/conformance` gains requirements in Phase 1, two handoff fields and two output lines for the same tracers, a wider Phase 3 re-read, a narrower walk for mitigations, and one optional section and one header line in the same record.
- Each `threat-model.md` is read **from the default branch by `git show`, with no gate**. `workflows-core:phase-handoff` §5 rule 2 gains the carve-out that makes that lawful, and `CLAUDE.md`'s hard constraint the matching clause.
- `workflows-core:threat-model-format` gains §10 (*The threats that land on a unit*), one sentence in §6 and a restated test in §9. `workflows-core:ard-resolution` adds `file:` to each invariant. `workflows-core:source-truth` §7.8 leaves a `design.md` entry out of the open entries. `/dev-workflows:ready` gains a seventh condition on the record's `Threats:` line.
- Nothing is written into `threat-model.md`, a `design.md` or a findings register, and no threat model becomes a prerequisite.

**Tech Stack:** markdown prose that agents execute; one comment string in `lineage-kinds.json`; generated reference parts (`scripts/reference-parts.py generate`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-15-sec-g2-d-security-conformance-design.md`, revision 3.1, approved by the maintainer 2026-11-15 with the four recommended answers. Cited below as *D1*…*D11*. Its two reviews (`.superpowers/design-review-1.md`, `design-review-2.md`) hold the code facts it rests on. Executors read the design with this plan: a decision it states is not repeated here.

**Execution (already chosen):** subagent-driven. Opus implements every task. **A task marked [security-sensitive] has its task review routed to Fable; one marked [mechanical] to Opus.** Fable reviews the whole branch at the end.

**Base:** worktree `/home/ihudak/dev/ai-tools/ai-workflows-wt/sec-g2d`, branch `feat/sec-g2-d-security-conformance`, `main` at `ec60ad47` plus the design commits. Every line number below was read there and is a finding aid only: **locate every site by the quoted phrase.** C as built is the model for every pattern: `docs/superpowers/plans/2026-11-14-sec-g2-c-design-threat-review.md` (its rulings cited as *C's R<n>*), `/design`'s Phase 2.5, `.claude/rules/threat-model.md`. *Format §N* is `plugins/workflows-core/references/threat-model-format.md`.

**The GIT-G1 edits — every one, with its approval:**

| # | Edit | Approval |
|---|---|---|
| G1 | `phase-handoff.md` §4.0, the `threat-model.md` register row: one sentence naming `/dev-workflows:conformance` as an ungated reader of the default branch's copy | Question 2, by name (a truth edit) |
| G2 | `phase-handoff.md` §5 rule 2: the carve-out for a consumer that reads `<default-ref>`'s copy alone | Question 2, by name (**a new rule**) |
| G3 | `CLAUDE.md` § Hard constraints: the matching clause, replacing wording | Question 2, by name |
| G4 | `reference-parts/phase-handoff/require-on-main.md`, regenerated; never hand-edited | Follows G2 (the design's GIT-G1 list) |
| G5 | `conformance.md` Phase 6: `body_facts` gains the threat lines | The design's GIT-G1 edit 3; **Question 1 below asks the maintainer to confirm it** |
| G6 | `conformance.md` Phase 0 step 4: the clause "a `design.md` is context" | Standing OK — truth-only, named by D11; the gate is unchanged |

Nothing else of GIT-G1's is edited. Named in the pull request as left for its owner: `.claude/rules/workflows-core-handoff.md` and `.claude/rules/workflows-core-git.md` (neither restates rule 2; the count of sixteen `require-on-main` callers stays true), `phase-handoff.md`'s "one row" clause in §4.1, and `/conformance`'s *Ending early* (R9).

**Questions for the maintainer** are at the end. Tasks 1 to 6 do not depend on them; Task 7 step 6 waits on Question 1.

## Global Constraints

### What is not ours

- **Never edited:** `plugins/workflows-core/references/specs-repo-git.md`, `plugins/workflows-core/scripts/specs-git.py`, `.github/workflows/validate-catalog.yml`, `.claude/rules/workflows-core-git.md` (19,993 characters) and `.claude/rules/workflows-core-handoff.md`.
- **`phase-handoff.md` takes G1 and G2 and nothing else.** Its generated files come from `python3 scripts/reference-parts.py generate`.
- **In `conformance.md`, leave GIT-G1's sections alone:** *Ending early*; Phase 0's specs preflight, `branch-check`, step 4's gate (save G6's clause), step 5's record check; Phase 6's class paragraphs, arrays and printed lines (save G5); Phase 9's `commit-artifacts`. **Never add text inside one of them beyond a named edit.** A step that finds it needs one stops and reports to the controller.
- **`/design` is unchanged** (D2): `plugins/dev-workflows/commands/design.md` takes no edit on this branch.
- **`threat-model.md`, every `design.md` and every register are read-only to `/conformance`.** No `register.py`, `weakness-classes` or `/security-workflows:scan` link.
- **The pull request names every GIT-G1 line this branch touches.**

### Repository rules

- **Prose is executed.** Every sentence an agent reads is true when it runs. A forward reference a later task makes true is named in the task's *Interfaces* and closed in Task 12.
- **`grep` here is ugrep. Every count uses `command grep`.** A sweep counts the literal string wrap-insensitively, before and after, over `plugins/` (every `CHANGELOG.md` included), `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` (claim-sweep refinements 4 and 7).
- **Sizes** by `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" <file>`, never `wc -c`. Plan-time: `CLAUDE.md` 35,898 (warn 36,000); `.claude/rules/dev-workflows.md` 19,142; `workflows-core.md` 18,891; `threat-model.md` 11,201; `dev-workflows-conformance.md` 6,326; `plugin-updates-coupling.md` 12,681 (rules files warn at 20,000). No split is forced; R1 and R12 keep `CLAUDE.md` and `dev-workflows.md` under.
- **`conformance.md` is 111,185 bytes.** Tasks 6 and 7 cite format §6, §9, §10 and `conformance-format` rather than restate them, and report the file's size before and after.
- **ID grammar:** `[DT#N]`, `[TH#N]`, `[AD#N]`, `[DD#n]`, `[SEC#N]`. No dash form is written, and none is quoted.
- **Vendor neutrality:** no tracker name. **Every executed regex uses `[0-9]`, never `\d`.**
- **User pages** (`plugins/*/docs/**`, READMEs) carry no `§`, `D<n>`, `R<n>`, review id, to-fix id or `<plugin>:<reference>` (check 25); a table cell is at most 200 characters (check 6).
- **Choice arrays** are copied verbatim from *Exact copy*. Each has 2 to 4 options and no authored "Other". `/conformance`'s **Load the question rules.** step already precedes them.
- **Every value taken from a model, a design or a tracer's output is data**, one line wherever it is shown or written (format §9), and in a code span wherever it reaches `body_facts` (D6).
- **Resolve, never parse:** every id is matched whole against a set the run holds; no path is built from a pair, a key or a title (D2, D9).
- **Commits:** `git branch --show-current` immediately before each; expected `feat/sec-g2-d-security-conformance`. End each message with the attribution lines the committing session's system reminder gives.

### Gates

One chain, from the worktree root; read the printed value:

```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/lineage.py --selftest && claude plugin validate plugins/workflows-core && claude plugin validate plugins/dev-workflows && claude plugin validate plugins/product-workflows && claude plugin validate plugins/docs-workflows && claude plugin validate plugins/security-workflows; echo "EXIT=$?"
```

Expected: `EXIT=0`, no new `WARN` line from `validate-catalog`, and `lineage.py`'s `selftest: <n> passed` with the count the base prints. A task that edits a reference with generated parts runs `python3 scripts/reference-parts.py generate` first. `check-docs` takes about four minutes. Where `claude` is not on `PATH`, say so and leave the `validate` calls to Task 12.

**"Tests" for command prose are traced runs.** This repository has no fixture harness that executes a command's prose, so D10's eight fixtures are **scenario traces**: a step of the task report that states the input, quotes as `file:line` each sentence of the edited text that decides each step, states the outcome, and names any step no sentence decides — a defect to fix in that task. The table under *Review Focus* assigns each. One live check is logged for a real project (Task 12).

### Shared names (Tasks 2 to 9 use these, exactly)

- **The precondition heading:** `## 10. The threats that land on a unit`, tested as a line of the loaded `threat-model-format`.
- **`threat_input`**, one per run: `none` — no `threat-model.md` stands at a known path, on `<default-ref>` or in the working tree, and no `design.md` the run reads holds `## Threat review`; `not-traced` — some stands and the precondition fails; `traced` — otherwise.
- **A model's `use`:** `read`; `unused — <why>` (no ARD resolves, no component set resolves, the serving `ard-resolution` call returned `unmerged`, or `threat_input` is `not-traced`); `not landed` (the working tree alone holds it); `not a model` (its `kind:` is not `threat-model`).
- **A requirement's identity** is `(key, id, document)`. New ids: `[DT#N]` with `document: design.md`; `[AD#n] Rule (ard-<area>.md)` with `document: ard-<area>.md`. A decision of `ard.md` keeps `[AD#n] Rule` and `document: ard.md`.
- **A mitigation** (D5): a `[DT#N]` Rule, or an `[AD#n]` Rule that a live, non-stale threat in scope names in `Mitigated by`. **Walk-only mitigations:** every `[AD#n]` Rule of an unused model's folder's ARD files and of the PRD-level ARD it inherits — for the arrays alone, never `mitigation: true`.
- **States:** `verified`, `open`, `not checked`, `unanswered`, `accepted`, `review due`, `stale`, `unreadable`, in the header's order below. **`unanswered` reasons:** `returned to the architect`; `answered elsewhere — not verified on this run`; `no design takes it`; `no design answers it`.

### Exact copy

**The walk's arrays for a mitigation** (D5), each asked on its own, never in a cluster:

```
choices: ["Fix the code", "Amend the document", "Cancel"]
choices: ["Confirm Dev's decision — <decision>", "<the other of the two>", "Cancel"]
choices: ["Overrule — fix the code", "Overrule — amend the document", "Cancel"]
choices: ["Mark it resolved — the code now matches", "Keep Dev's decision — amend the document", "Cancel"]
choices: ["Mark it resolved — the code now matches", "Cancel"]
```

In the second, `<decision>` is `fix-code` or `amend-document` and `<the other of the two>` is the other's label of the first array.

**Printed lines:**
- `Threats: not traced — update workflows-core`
- `Threats: <path> is not on the default branch — not read`
- `Threats: <path> not used — <why>`, `<why>` one of: `no ARD resolves for it`, `no component set resolves`, `its ARD is not on the default branch`.
- `Threats: no accept is offered on <n> architecture Rule(s) — a threat model the run could not use may rest on them` — once, where walk-only mitigations exist.
- `conformance-tracer (<repo_slug>): <n> section(s) dropped — each heading names no requirement routed to it`

**The record's header line**, after `Verdicts:` (`conformance-format` §2 pins it; `/ready` parses it):

```
- **Threats:** <n> verified · <n> open · <n> not checked · <n> unanswered · <n> accepted · <n> review due · <n> stale · <n> unreadable[ — not read: <each model unused or not landed, each design not read>]
- **Threats:** not traced — update workflows-core
```

Every count is written, zero included. **The record's section**, before `## Discrepancies`:

```markdown
## Threats

- **Models read:** <each model's path relative to $SPECS_PATH, or none>
- [[<KEY>]] [TH#N] <title> — <state>[ — <reason>][ — <each mitigation, with its verdict or [DD#n]>]
- [[<KEY>]] [DT#N] <title> — <state> — <why it stands alone>
```

**The no-exit sentence** (D7), on each Next-step line for `unanswered — returned to the architect`, `unanswered — no design takes it`, and `open` on a decision the team will not build: `No command re-disposes a live threat that is not stale yet: the architect supersedes the decision, or waits for the intake of returned threats.`

**G1**, inserted in the register row before `No other command reads it as a threat model.`: `` `/dev-workflows:conformance` reads it too, ungated and never from the working tree: `<default-ref>`'s copy alone, at its Phase 1, for the models of the unit it checks (§5 rule 2's reader that executes no gate). ``

**G2**, appended to §5 rule 2 after `A gate that fires after a scan has already spent what it was meant to save.`: `` **One kind of consumer executes no gate.** A consumer that reads a deliverable only as `<default-ref>` holds it — by §3.2's read-only primitive, `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`, never from the working tree or any other ref — cannot read content that has not landed, so it executes no `require-on-main` on that deliverable; it names, in one line, a copy the working tree holds that `<default-ref>` does not. `/dev-workflows:conformance` reads each `threat-model.md` so, at its Phase 1. On a specs tree that is no git repository there is no other copy, and the file is read. ``

**G3**, in `CLAUDE.md`'s bullet opening `A phase is not finished until`: `` every consumer executes `require-on-main` before expensive work; `` becomes `` every consumer executes `require-on-main` as `workflows-core:phase-handoff` §5 rule 2 says; ``, and later in the same sentence `` (`workflows-core:phase-handoff` §3.4 names `` becomes `` (its §3.4 names ``. Net about one character.

### Rulings where the design is silent or leaves it to the builder

- **R1 — `CLAUDE.md`'s room.** G3 is net-zero. The rules table's `threat-model.md` row gains two paths (Task 9), about 45 characters; no other `CLAUDE.md` edit is planned. Task 9 measures: at 35,990 or above, Question 3's move applies.
- **R2 — the precondition is tested only where threat input exists.** A run whose `threat_input` would be `none` loads no `threat-model-format` and prints nothing, so goal 5 holds beside any `workflows-core`.
- **R3 — on a `not-traced` run, a `[DT#N]` entry on file is carried forward as it stands**: never `resolved`, never `requirement withdrawn`, its follow-up kept. The run cannot tell.
- **R4 — the tracer names what reaches a check on a line of its own.** A `mitigation: true` section adds `- reached by: <file:line@commit>, one per call site | none — searched <the searches run> | not owed — <the Rule's shape, in a few words>`, so Phase 3 has a location to re-read. `none` on a Rule that owes one makes the verdict `partial`, its `shipped:` ending `the check is not called`.
- **R5 — where each threat stands is computed once, in Phase 5, after the walk and before the record is written.** The set of mitigations is fixed in Phase 1, which is all the walk needs.
- **R6 — `/ready`'s new condition is the seventh, appended.** "Six conditions" becomes seven, and "the last" becomes "the sixth" wherever a copy says which condition the block test is (Task 8's sweep). Renumbering condition 6 would move more text.
- **R7 — a `Threats:` line `/ready` cannot read fails closed.** More than one such line, or one in neither pinned form, fails condition 7 with `threats line unreadable — re-run /dev-workflows:conformance <PRD>`.
- **R8 — the Final report gains `### Threats`**, between `### Verdicts` and `### Discrepancies`, only where `threat_input` is not `none`: the header's counts, then every threat and stand-alone entry not `verified` or `accepted`, grouped by owner (Dev, PA), one line each.
- **R9 — *Ending early* takes no edit.** D adds no stop and no run-ending answer: each new array's *Cancel* is "Phase 4's walk *Cancel*", which the section names. Task 7 verifies it; a new stop found there goes to the controller.
- **R10 — the model's read cites `phase-handoff` as Phase 0 step 5.2 does** ("`workflows-core:phase-handoff` §3.2's read-only primitives"), and `check-citations` decides whether the pointer is cited or worded.
- **R11 — the legacy match is run where the record is read, once.** Task 6 applies D3's one-time rule to the unit's record and, on a PRD run, each Epic's, before Phase 3's entry re-check; a matched entry is rewritten in the new form when the record is written, and an Epic record is never rewritten for it.
- **R12 — `dev-workflows.md`'s edits are net-zero words** ("six" → "seven", "the last" → "the sixth"); `/conformance`'s map line and every new invariant go to `.claude/rules/dev-workflows-conformance.md`.
- **R13 — `review due` reads the record's `Run:` date** as the run will write it, the writer's own date; the date test is `python3 -c 'import sys,datetime as d; print(d.date.fromisoformat(sys.argv[1]) < d.date.fromisoformat(sys.argv[2]))' "<review-by>" "<Run: date>"`, and anything but `False` is `review due`.

## Review Focus

Inputs a reasonable Dev or PE will hit that no gate exercises, most likely first. Each has a scenario trace in its owning task. T-numbers also cover D10's eight fixtures (F1 to F8).

| # | Input | Expected | Trace |
|---|---|---|---|
| RF1 (F2) | Epic run; the PRD folder's landed model defers a threat that reaches the Epic's target only through a contract row; the Epic's `design.md` has no `## Threat review` | `unanswered — no design answers it`, the design named; Next step Dev → `/dev-workflows:design <KEY>`; nothing stops | Task 7 |
| RF2 | The architect's uncommitted refine in the working tree drops a threat the default branch's model holds; a second folder holds a `threat-model.md` on no ref | The landed threat is listed; the stray file gets the `not on the default branch` line, binds nothing and withholds nothing | Task 6 |
| RF3 | A D-era `dev-workflows` beside a `workflows-core` with no §10, on a unit with a landed model | `Threats: not traced — update workflows-core`; no model read, no `[DT#N]` handed; no accept on the folder's `[AD#n]` Rules; `/ready` holds the rung | Tasks 6, 7, 8 |
| RF4 (F6, F7) | PRD run; an Epic record, hand-edited, lists a mitigation under `## Satisfied`; another Epic entry decided `accept` on a mitigation | The mitigation is traced in full and re-read; the `accept` is put at the third array, applied as an overrule; until answered, *Cancel* included, the threat is `open` | Task 7 |
| RF5 (F8) | An area-split folder: `ard-cart.md` and `ard-payments.md` each hold `[AD#2]`; the record on file holds `[AD#2] Rule`, `document: ard.md` | Two requirements, each with its file; the old entry is `orphaned`; with one area file holding the number, it matches | Task 6 |
| RF6 | A tracer's output holds a section headed for a requirement not routed to it, a mitigation in two sections, an evidence path `git ls-tree` does not list, and `SEC#12` | The stray section dropped and counted; the doubled one *unverified*; the two matches withheld and their requirement *unverified*; nothing the agent wrote is echoed | Task 6 |
| RF7 (F4) | A `[DT#N]` Rule "passwords are stored as argon2id hashes" with a test; another whose check exists, is never called, and has no test | The first owes no call site and reads as its code does; the second is `partial`, the check not called and the test missing | Tasks 5, 6 |
| RF8 | A mitigation's question answered in free text "accept it as shipped"; a mitigation sharing an evidence location with two ordinary discrepancies | Asked again, the text saying only the architect accepts, in the model; the mitigation is asked alone and the other two cluster | Task 7 |
| RF9 (F5) | A landed model whose folder resolves no ARD; and a PRD with no Epic folder whose model's ARD call returns `unmerged` | Each `unused`, named in the header's `not read:`; accept withheld on the walk-only Rules; the run does not stop | Tasks 6, 7 |
| RF10 (F3) | A design's entry `Returned to the architect` on a deferred threat | `unanswered — returned to the architect`, PA route with the no-exit sentence | Task 7 |
| F1 | No model at a known path, no `## Threat review` in any design read | Today's tracer input, arrays, record, report, pull-request body and lineage | Task 12 (NR1) |

---

### Task 1: `phase-handoff` — the reader that executes no gate, and `CLAUDE.md`'s clause [security-sensitive]

**Files:**
- Modify `plugins/workflows-core/references/phase-handoff.md`: G1 (the row opening `` | `threat-model.md`, beside an ARD | gated | ``) and G2 (§5 rule 2), each verbatim from *Exact copy*.
- Regenerate `plugins/workflows-core/reference-parts/phase-handoff/` (expect `require-on-main.md` alone to change: G1's row lies outside every `<!-- entry -->` region).
- Modify `CLAUDE.md` § Hard constraints: G3.

**Interfaces:** produces the rule Task 6's read relies on. **Forward reference:** G1 and G2 name a read `/conformance` makes only from Task 6.

- [ ] **Step 1: Before counts.** Count `No other command reads it as a threat model` (expect 7 files, as at plan time), `executes no gate` (expect 0) and `before expensive work` (record it) over the sweep scope.
- [ ] **Step 2: Check §3.2's primitive.** Read `phase-handoff.md` §3.2 and confirm the read G2 quotes is the primitive it gives (at plan time §3.2 writes the object as `<ref>:./<path>`); where the command differs, G2 quotes §3.2's own, and the report says so.
- [ ] **Step 3: Apply G1 and G2**, then `python3 scripts/reference-parts.py generate`. `git diff --stat` shows `phase-handoff.md` and `require-on-main.md` only.
- [ ] **Step 4: Apply G3.** Itemise in the report what the cut words said and where each now stands: "before expensive work" is §5 rule 2's first sentence; the §3.4 pointer is kept. Measure `CLAUDE.md`: expect 35,898 ± 3.
- [ ] **Step 5: Contradiction read.** Read §5 whole, §4.0's class table and the *advisory* row, and `require-on-main.md`'s copy of rule 2: no sentence still says every consumer gates. Report each sentence read.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): phase-handoff §5 rule 2 — a reader of the default branch's copy alone executes no gate`.

### Task 2: `threat-model-format` — §10, §6's sentence, §9's restated test [security-sensitive]

**Files:**
- Modify `plugins/workflows-core/references/threat-model-format.md`.
- Modify `.claude/rules/threat-model.md`: a new invariant 9, and the authority paragraph's section list gains `(§10)`.
- Modify `plugins/workflows-core/docs/reference/references.md`: the format's row, in words.

**Interfaces:** produces the heading `## 10. The threats that land on a unit`, placed after §9 and before `## Example`; §6's no-path sentence; §9's test for an agent given a repository. Tasks 6 and 7 cite all three.

- [ ] **Step 1: §10.** Take, in `/design`'s own words, exactly the sentences of `design.md`'s Phase 2.5 step 7 that D2 lists: the three bullets; ids and pairs compared whole; the PRD folder's model read itself, never `## Inherited threats` bullets; and the malformed rule with its four causes, such a threat landing whatever its Where. Reword only what names `/design`'s own run ("this design" → "the unit", "Phase 2.5's `contracts`" → "the `contracts` `ard-resolution` returned"). Then D's two sentences, marked as `/dev-workflows:conformance`'s alone: a stale threat is listed whatever its Where, since staleness is tested before landing; and a threat an in-scope live entry answers is in scope. Then: a PRD run applies no filter. The section says `/dev-workflows:design` states the same rule in its own Phase 2.5 and does not yet cite this section.
- [ ] **Step 2: §6.** Add `/design`'s sentence, generalised: a pair is read only in the file of `ard_paths` whose folder and whole basename it names, and no path is ever built from one. Add `/dev-workflows:conformance` to who runs the check: read-only, at its Phase 1, on each model it reads, against the ARD files `ard-resolution` returned (`ard_paths`) and its own resolved set; it lists each stale threat and clears none. **Forward reference** to Task 6.
- [ ] **Step 3: §9.** Restate the test for an agent given a repository (D9): for `dev-workflows:conformance-tracer`, a match is one the agent could have been given where the traced ref holds it — a path that `git ls-tree` at that ref lists, a `SEC#` id that `git grep` at that ref finds — and any other match is withheld. Add `/dev-workflows:conformance` to the section's list of commands, as one that dispatches an agent that reads code and holds its output, not a proposal, to the backstop. The two patterns and the three binding rules are not changed.
- [ ] **Step 4: The invariant.** `.claude/rules/threat-model.md` invariant 9: format §10 and `/design`'s Phase 2.5 step 7 state one rule and change together; the two sentences that are `/conformance`'s alone are named; `/design` moves onto §10 by a logged follow-up (Task 11), because beside an older core a `/design` citing §10 would lose its review.
- [ ] **Step 5: Diff check.** List §10's sentences beside `design.md`'s, one per line, in the report; every difference is one Step 1 allows.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): threat-model-format §10 — the threats that land on a unit; §6 builds no path, §9 for an agent given a repository`.

### Task 3: `ard-resolution` — each invariant carries its file [mechanical]

**Files:** Modify `plugins/workflows-core/references/ard-resolution.md`; `plugins/workflows-core/docs/reference/references.md` only where its row states the output's fields.

**Interfaces:** produces `file: <basename of the ARD file that holds the decision>` on each `invariants` entry, after `source:`. Additive: a caller that reads no `file:` behaves as before. Task 6 builds requirement identities from it.

- [ ] **Step 1:** Add `file:` to the output block and one sentence under it: the basename, whole, of the file of `ard_paths` the decision was read in — `ard.md` or `ard-<area>.md` — never a path, and never derived from the id.
- [ ] **Step 2: *Consumers*.** `/conformance`'s bullet gains: it reads each invariant's `file`, and `contracts`; on a PRD with no Epic folder it makes a PRD-level call only where a threat model stands in the PRD folder, where `unmerged` stops nothing. The sentence `` and `components` alone by `/conformance` `` becomes true to that (count the phrase before, 1, and after, 0). **Forward reference** to Task 6.
- [ ] **Step 3:** Read the *No-regression rule* section against the addition and report that no sentence there is made false.
- [ ] **Step 4: Gates. Step 5: Commit:** `feat(sec-g2): ard-resolution — each invariant carries the file that holds it`.

### Task 4: The record — `conformance-format`, and `source-truth` §7.8 [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/references/conformance-format.md` (§2, §3, §5, §6).
- Modify `plugins/workflows-core/references/source-truth.md` §7.8, *Which entries are open*.
- Modify `.claude/rules/workflows-core.md` (the `source-truth` paragraph, one clause) and `.claude/rules/dev-workflows-conformance.md` (*The record's readers*).

**Interfaces:** produces the header line and `## Threats` of *Exact copy*; the `document:` values; §5's exception; the rule that a `design.md` entry is not open. Tasks 6 to 8 write and read them. **Forward reference:** the command writes none of it until Task 7.

- [ ] **Step 1: §2.** Add the `Threats:` header line after `Verdicts:` and `## Threats` before `## Discrepancies`, both forms verbatim, with: when each is written (wherever `threat_input` is not `none`; otherwise neither, and a record without them is not read as zero); the section rewritten whole each run, nothing carried forward; states and reasons as *Shared names* gives them, the state function itself cited as `/dev-workflows:conformance` Phase 5's; titles and reasons as data, one line. `Not traced:` still names no `design.md` and no model — reword its sentence "a `design.md`, which is context and never traced" to say a design's `[DT#N]` Rules are traced as requirements while the design is still not a document the line names.
- [ ] **Step 2: §2, `## Satisfied`.** A `[DT#N]`'s line lists its `test:` location among its evidence, so a deleted test moves it. A PRD run's drift check never skips a mitigation (D8).
- [ ] **Step 3: §3.** `document:` becomes `<specification.md | epic.md | prd.md | ard.md | ard-<area>.md | design.md>`. State the id form for an area file's decision and D3's one-time match rule: an entry or `## Satisfied` line on file as `[AD#n] Rule` with `document: ard.md` matches the new id where exactly one area file of the folder holds that number, and is otherwise `orphaned`. A `[DT#N]` entry decided `amend-document` carries no note: its `effect:` names `/dev-workflows:design <KEY>`.
- [ ] **Step 4: §5.** The exception to "carries each decided entry forward without asking again" and to "asks only about those": an entry on file decided `accept` whose requirement is now a mitigation is put again, keeps its `[DD#n]`, and its earlier decision is shown; a PRD record's own entry whose `ruling:` confirms a Dev's `accept` is put again as an overrule. A `[DT#N]` on file that is withdrawn or no longer `Mitigated` is `requirement withdrawn`.
- [ ] **Step 5: §6.** `/dev-workflows:ready` also reads the `Threats:` line (**forward reference** to Task 8). `/document` and `/release-notes` read no `design.md` entry: §7.8 leaves it out.
- [ ] **Step 6: §7.8.** In *Which entries are open*, rule 2 gains: drop an entry whose `document:` is `design.md` — a mitigation the design owns, settled in the design and never by a documentation decision; it is not open here and is reported by no reader of this list. Read the rest of §7.8 for a sentence that enumerates `document:` values or says every entry maps, and correct each.
- [ ] **Step 7: Sweeps.** Count before and after, by subject: *what a re-run carries forward* (`conformance-format` §5's two bullets); *the `document:` values* (`command grep -rn 'epic.md | prd.md | ard.md'`: 2 files at plan time; the handoff file's copy is Task 5's).
- [ ] **Step 8: Gates. Step 9: Commit:** `feat(sec-g2): the conformance record — a Threats line and section, design.md and area-file decisions, no accept carried onto a mitigation`.

### Task 5: The tracer — a marked mitigation, its test and what reaches it [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/references/handoff/conformance-tracer.md` and `plugins/dev-workflows/agents/conformance-tracer.md` (the untrusted-content block stays byte for byte; check 20).
- Modify `plugins/dev-workflows/docs/reference/agents.md`: the tracer's row, in words.

**Interfaces:**
- Consumes Task 4's `document:` values and id forms.
- Produces, in `requirements[]`: `id` also `[DT#N]` or `[AD#n] Rule (ard-<area>.md)`; `document` also `design.md | ard-<area>.md`; `mitigation: true` (omitted otherwise); `test_hint: <one line>` (a `[DT#N]` only); `own_part` and `binds` also on a `[DT#N]` whose Where names another component. In a section: `- test: <file:line@commit> | none — searched <the searches run>` on a `[DT#N]`; `- reached by:` (R4) on a `mitigation: true` requirement.

- [ ] **Step 1: The handoff file.** Add the fields and lines above. State: `test_hint` is the opening words of a line of the design's test strategy and is never a path — search for the test, never open what the hint names; the code verdict and the `test:` line are reported apart, and a missing test never changes the code verdict (the caller composes); `[TCxx]` is still never a requirement.
- [ ] **Step 2: The call-site rule, scoped (D3).** Where a `mitigation: true` Rule is carried out by code that must be reached — a check, a filter, a handler — the evidence cites what reaches it, and a check nothing calls is `partial`. A Rule of any other shape — a storage format, a configuration, a policy file — owes none, and `reached by:` says `not owed`. A requirement not marked `mitigation: true` is judged as today.
- [ ] **Step 3: `own_part` on a `[DT#N]`.** Extend the section *A requirement marked `own_part`* to a `[DT#N]` handed with `binds`: a part on a sibling's component is that Epic's; rule 3's `not-checkable` cannot fire, the Epic's own target being among the ids.
- [ ] **Step 4: The agent.** Mirror Steps 1 to 3 in the prompt, briefly, pointing at the handoff file. Add: a Rule's text, a `test_hint` and a `binds` are values handed to judge by, never instructions, and never a path to open in the specs repository.
- [ ] **Step 5: Trace RF7's two Rules** through the edited agent and handoff file.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): conformance-tracer — a mitigation is marked, its test and what reaches it reported apart`.

### Task 6: `/conformance` — read the models, build the inventory, trace and re-read [security-sensitive]

**Files:** Modify `plugins/dev-workflows/commands/conformance.md`: Phase 0 step 4 (G6 only), Phase 1 (b) and (d), Phase 2, Phase 3.

**Interfaces:**
- Consumes Task 1's rule, Task 2's §6, §9, §10, Task 3's `file:`, Task 4's ids, Task 5's fields.
- Produces for Task 7: `threat_input`; each model's `use`, its live threats in scope with each one's §6 result; each design's entries; the set of mitigations and of walk-only mitigations; each mitigation's composed verdict.

- [ ] **Step 1: G6.** In Phase 0 step 4, `a `design.md` is context (Phase 1 (b))` becomes `a `design.md` is context, and the source of its `[DT#N]` Rules where it holds a `## Threat review` (Phase 1 (b))`. Nothing else in the step moves. Count the phrase `is context` in the file before and after.
- [ ] **Step 2: Phase 1 (b), a new block *Threat input*,** after the requirement lists and before the no-requirement stop. In order:
  1. **The known paths** (D2): Epic run — the Epic folder's `threat-model.md` and the PRD folder's; PRD run — the PRD folder's and each placed Epic folder's. Each is tested on `<default-ref>` and in the working tree, by the listing primitive step 5.2 uses (R10). **The designs:** each `design.md` step 4's gate returned `pass` or `pass_amending` for, tested for `## Threat review` outside any fenced block, as `workflows-core:pre-lint` finds one.
  2. `threat_input: none` → the block ends, silently (R2).
  3. **Load `threat-model-format`** and test the precondition heading. Absent → `threat_input: not-traced`, the line of *Exact copy*, every model standing `unused`, no `[DT#N]` in the inventory.
  4. **Each model**, read by `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`; a tree that is no git repository reads the file. Working tree only → `not landed`, with its line. `kind:` not `threat-model` → `not a model`, silently dropped. No gate, no repair, no lineage (`upstream-check` takes no model).
  5. **Which `ard-resolution` call serves it** (D2): an Epic folder's model, that Epic's call; the PRD folder's, the PRD-level part of any Epic's call; on a PRD with no Epic folder, a PRD-level call made only here, whose Rules join the inventory, and whose `unmerged` stops nothing and leaves the model `unused`. `status: none`, or no component set by format §4's two sources → `unused`, with its line.
  6. **The check and the scope:** format §6 read-only per model against `ard_paths` and the set; format §10 for which live threats land (a PRD run applies no filter).
  7. **The `[DT#N]` requirements** (D3): each live entry whose Disposition opens `Mitigated — Rule: `, with `key`, `id`, `document: design.md`, `text` the Rule and `test_hint` its Test text, each one line.
  8. **The joins:** each `Mitigated by` pair of a threat in scope resolves, by `file:` and number, to an `[AD#n]` Rule of the inventory, or its part is `not checked`; never by number alone.
- [ ] **Step 3: Phase 1 (b), the identity of an area file's decision.** Every `[AD#n]` Rule whose `file` is not `ard.md` takes the id and `document:` of *Shared names* — on every run, whatever `threat_input` is, since the collision is a shipped defect (D3). Then R11's legacy match.
- [ ] **Step 4: Phase 1 (d).** One bullet: on a PRD run a mitigation is exempt from the `## Satisfied` skip and is traced in full every time (D8).
- [ ] **Step 5: Phase 2.** Routing of a `[DT#N]` as any requirement of its unit; `own_part: true` with its Where ids as `binds` on an Epic run with a `target:` where its Where names any other component; `mitigation: true` on each `[DT#N]` and each joined `[AD#n]`, never on a walk-only one. **Values in, never specs-repository paths** (D9): no model, design, title or Threat line is handed. **Compose** (D3): the code verdict merges across repositories as today; a test found in any traced repository of the unit counts; code `satisfied` with no test anywhere is `partial`, `shipped:` ending `the test is missing`.
- [ ] **Step 6: Phase 2, what comes back** (D9), only where the run handed a `[DT#N]` or a `mitigation: true`: the label check, with its printed line; a mitigation returned in two sections is *unverified*; format §9's backstop over every text value of a mitigation's section, resolved against the traced ref, a withheld match making the requirement *unverified* with what would settle it stated in the run's own words.
- [ ] **Step 7: Phase 3.** Re-read every `satisfied` mitigation at its evidence, its `reached by:` and its `test:` location; one that cannot be confirmed is *unverified*. One sentence says what the read confirms — the lines exist and reach the check — and what it does not: that they run in production.
- [ ] **Step 8: Traces** RF2, RF3 (this task's half), RF5, RF6, RF7 and RF9 (its half). Report `conformance.md`'s size before and after.
- [ ] **Step 9: Gates. Step 10: Commit:** `feat(sec-g2): /conformance traces each design's [DT#N] Rules and joins each Mitigated-by pair — the model read from the default branch`.

### Task 7: `/conformance` — where each threat stands, the walk, the record, the report [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/commands/conformance.md`: Phase 4, Phase 5, Phase 6 (G5 only), Phase 7, *Invariants*.
- Modify `plugins/workflows-core/references/escalation-rules.md` (the row `the `/conformance` decision picker`), `plugins/workflows-core/references/next-phase-offer.md` (the two `/dev-workflows:conformance` bullets); regenerate their parts.
- Modify `.claude/rules/dev-workflows-conformance.md`: the map line, and an invariant block *Mitigations and threats*.

**Interfaces:** consumes Task 6's run values and Task 4's record. Produces the record Task 8 reads.

- [ ] **Step 1: Phase 4.** A mitigation, and a walk-only mitigation, is asked on its own with the array of *Exact copy* its form takes, and never joins a cluster; the walk-only line is printed once. **Put again** (D5): the unit's own entry decided `accept` on what is now a mitigation, at the first array with its earlier decision shown; a PRD record's own entry confirming a Dev's `accept`, at the third. Amend the paragraph opening `An entry the record on file already decided is not asked again` to carry the exception. **Free text that would accept** is normalised into no option and asked again, the text saying only the architect accepts a risk, in the threat model.
- [ ] **Step 2: Phase 5, effects.** *Fix the code*: today's follow-up. *Amend the document* on an `[AD#n]`: today's, the PRD run's note written into the file `document:` names — `ard-<area>.md` for an area file's decision, which today is addressed to an `ard.md` the folder may not hold. On a `[DT#N]`: no note on either run, `effect:` naming `/dev-workflows:design <KEY>`. An overrule from the third array is applied as an overrule is today (`ruling: overrules`, `superseded-by`).
- [ ] **Step 3: Phase 5, *Where each threat stands*** (R5): D4's function, as the design writes it — the four ordered rules; the mitigated part; the deferred part with *M*; the stand-alone entries; a withdrawn `[DT#N]`. Write it once, here, as an ordered list; `conformance-format` cites it. An amended mitigation leaves its threat `open` (D5); an unanswered put-again entry, a *Cancel* included, leaves it `open`. R3 and R13 apply.
- [ ] **Step 4: Phase 5, the record.** The `Threats:` line and `## Threats` per `conformance-format` §2, only where `threat_input` is not `none`.
- [ ] **Step 5: Phase 7.** `### Threats` (R8). `### Next step` adds D7's routes: Dev → `/dev-workflows:design <KEY>` for `unanswered — no design answers it` and a `[DT#N]` decided *Amend the document*; PA → `/product-workflows:create-ard <KEY>` for `stale`, `review due`, `unreadable`, and the three no-exit states, each with the no-exit sentence; the scan stays after a clean Epic run. `next-phase-offer`'s two bullets gain the same routes, and `an `amend-document` decision → the command its note names` gains `, or `/dev-workflows:design <KEY>` for a `[DT#N]`, which takes no note`. `escalation-rules`' row gains the mitigation forms: no `accept` on a mitigation, on any form.
- [ ] **Step 6: G5** (after Question 1's answer). In Phase 6, `body_facts` gains: `the `Threats:` line's counts and, one line each, every threat and stand-alone entry not `verified` or `accepted`, its title and reason in a code span`. Nothing else in Phase 6 moves.
- [ ] **Step 7: *Invariants*.** Add: NEVER accept a mitigation's discrepancy, on any array or from free text; NEVER write into `threat-model.md`, a `design.md` or a findings register; NEVER gate, repair or stop on a threat model; a threat reads `verified` only on a trace and a re-read made in this run. Reword `every open discrepancy is put to them` only if Step 1 made it false. Verify R9: list every stop and run-ending answer this branch added to the file; expect none.
- [ ] **Step 8: The rules file.** The map line gains the threat input, the mitigation walk and the `Threats` record parts, in the line's own style. The invariant block states: the default branch's copy and why no gate; no accept; the unused-model withholding; the PRD run's full trace; "located and re-read", not C's structural guarantee.
- [ ] **Step 9: Traces** RF1, RF3 (its half), RF4, RF8, RF9 (its half) and RF10. Each array of *Exact copy* is in the file verbatim: `command grep -F` each. Report the file's size.
- [ ] **Step 10: Gates** (with `generate` first). **Step 11: Commit:** `feat(sec-g2): /conformance lists where each threat stands and never accepts a mitigation`.

### Task 8: `/ready` — the `Threats:` line and the rung [security-sensitive]

**Files:** Modify `plugins/dev-workflows/commands/ready.md` (Phase 1 step 2b); `plugins/dev-workflows/references/workflow-states.md`; `.claude/rules/dev-workflows.md`; `.claude/rules/dev-workflows-conformance.md`.

**Interfaces:** consumes the header line `conformance-format` §2 pins.

- [ ] **Step 1: Before counts** of `six conditions` (3 files at plan time) and of each phrase saying which condition is last, over the sweep scope and `ready.md`.
- [ ] **Step 2: Condition 7.** After condition 6: the record's `- **Threats:**` line holds nothing against the rung — a record with no such line passes, absence being the normal case, unlike condition 2's coverage lines; a line that reads, whole, `not traced — update workflows-core` fails; a line whose `open` count is above zero fails; R7's unreadable line fails. `unanswered`, `review due` and `stale` are the architect's and hold nothing.
- [ ] **Step 3: The reasons**, appended to the ordered list: `threats not traced — update workflows-core, then re-run /dev-workflows:conformance <PRD>`; `<n> threat(s) open`; R7's.
- [ ] **Step 4: The sweep** (R6, R12). Every copy of the count and of "the last" reads true; `ready.md`'s own "conditions 1–5" and "condition 6" pointers are re-read, each one, and left where still true. After counts. Measure `dev-workflows.md`: expect 19,142 ± 10.
- [ ] **Step 5: Trace** RF3's `/ready` half, and a record written before this release (no line): it passes condition 7.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): /ready — an open threat, or threats not traced, holds Delivery verified`.

### Task 9: The claim sweeps — who reads the model, and what C said D would do [mechanical]

**Files:** `threat-model-format.md` (the opening and §8); `.claude/rules/threat-model.md` (`paths:`, the opening paragraph, the authority paragraph, invariants 2, 5 and 8); `CLAUDE.md` (the rules table's `threat-model.md` row); `plugins/workflows-core/scripts/lineage-kinds.json` (`_source` only); `.claude/rules/workflows-core-triage.md` (what Phase 3 re-checks).

**Interfaces:** consumes Tasks 6 and 7, which make each sentence true. Produces the wording Task 10's pages repeat.

- [ ] **Step 1: Enumerate by subject** — the model's readers — never by wording: `command grep -rln 'threat-model\|threat model' plugins CLAUDE.md README.md .claude/rules docs/maintainers`, each hit read for a statement of who reads the model or that D will. Table every statement, with its before count: `Four readers by name` (2 files), `No other command reads it as a threat model` (7), `is to read it later` (1), `conformance` followed by `later` (2), `will add `/dev-workflows:conformance`` (1), `sub-project D` (2).
- [ ] **Step 2: The reader sentence.** Five readers by name: `/dev-workflows:conformance` joins, as the one that reads the default branch's copy, ungated, at its Phase 1, for the unit it checks, and judges no threat's sufficiency. One wording across the format's opening and §8 and the rules file. Invariant 5's "D must sweep this bullet" paragraph is removed, its claim having expired; invariant 8 widens from `/design` to "neither `/design` nor `/conformance` writes into it".
- [ ] **Step 3: `paths:`** of `.claude/rules/threat-model.md` gains `plugins/dev-workflows/commands/conformance.md` and `plugins/dev-workflows/references/conformance-format.md`; `CLAUDE.md`'s table row follows, by its `dir/`: `a`, `b` convention. Measure `CLAUDE.md` (R1).
- [ ] **Step 4: `_source`.** Replace `so a /dev-workflows:conformance note (sub-project D) never reads as a revision` with wording true of D as built: no command writes a note into the model. `notes` and `ignore_lines` stay. First `command grep -rn 'sub-project D' plugins/workflows-core/scripts scripts`: no selftest pins the string.
- [ ] **Step 5: The triage rule.** `/conformance`'s Phase 3 also re-reads each `satisfied` mitigation; one clause.
- [ ] **Step 6: Exclusivity probe** (refinement 3) over the same scope for the model's readers and for the record's writer. After counts against the table.
- [ ] **Step 7: Gates. Step 8: Commit:** `docs(sec-g2): the threat model's fifth reader — every copy of the claim`.

### Task 10: Pages [mechanical]

**Files** (each in words; check 25):
- `plugins/dev-workflows/docs/commands/conformance.md` — what is traced; the threat states and who owns each; the walk without accept on a mitigation; **what `verified` does not claim** (the lines exist and reach the check; not that the attack fails); the three states with no exit yet (D7, Question 3's answer); the `not traced` line.
- `plugins/dev-workflows/docs/commands/ready.md`, `docs/workflow.md`, `docs/roles-and-phases.md`, `docs/reference/references.md` — the rung's new condition; the record's new parts.
- `plugins/workflows-core/docs/reference/references.md`, `docs/family-map.md` — the model's readers; §7.8's rule.
- `plugins/product-workflows/docs/commands/create-ard.md`, `docs/workflow.md` — the model's readers; what brings the architect back.
- `plugins/docs-workflows/docs/commands/document.md` and `release-notes.md` — where each says which conformance entries it takes: a design's entry is none of them.
- `plugins/security-workflows/docs/roles-and-phases.md` — conformance runs before the scan and traces mitigations; the scan still owns what the code lets through.

**Interfaces:** consumes every earlier task's names.

- [ ] **Step 1:** For each page, derive every claim from the command or reference that runs it, never from this plan. Before and after counts of `No other command reads it as a threat model` on the four pages that hold it.
- [ ] **Step 2: Gates. Step 3: Commit:** `docs(sec-g2): security conformance on the pages`.

### Task 11: Release [mechanical]

**Files:** `.claude-plugin/plugin.json` and `CHANGELOG.md` of all five plugins; `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`; `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`; `docs/superpowers/to-fix.md`; `docs/superpowers/to-test-on-real-project.md`.

- [ ] **Step 1: Merge.** `git fetch origin`; where `origin/main` moved, `git merge --no-edit origin/main` (never rebase), keep both sides, and re-derive every count and size this plan touched.
- [ ] **Step 2: Versions, read from `origin/main` now.** At plan time: `workflows-core` 1.92.0, `dev-workflows` 4.67.0, `docs-workflows` 1.39.7, `product-workflows` 3.82.1, `security-workflows` 0.12.4. `workflows-core` and `dev-workflows` take the next free **minor**; the other three the next **patch** (D11). `plugin.json` equals `marketplace.json`. Each CHANGELOG section is dated with the landing day (UTC), never `— Unreleased`, in its own plugin's terms; `workflows-core`'s names G1 and G2.
- [ ] **Step 3: Two coupling bullets** (D11), both naming `workflows-core`: a D-era `dev-workflows` beside an older core traces no threat and says so; an older `workflows-core` beside a D-era record takes a `[DT#N]` entry as open and carries it to the release-notes writer — update it before `/release-notes` on such a PRD. State that an older `docs-workflows` beside a D-era core is safe. Measure the file; above 19,000, move the oldest bullets to a history file as the last split did.
- [ ] **Step 4: The roadmap and the review.** Row D gains `*Built as SEC-G2 D:*` with the design's path and the five versions, in row C's form, saying it is a dimension of `/dev-workflows:conformance`, not a command of `security-workflows`. The feature-gaps review's SEC-G2 row and heading resolve.
- [ ] **Step 5: `to-fix.md`**, a section *From SEC-G2 D*: `/design` moves onto format §10; the area-file collision, as a shipped defect D fixed, with the one-time match rule; RETURNED-INTAKE widened to any live, non-stale threat and marked scheduled next (Question 3's answer).
- [ ] **Step 6: `to-test-on-real-project.md`**, headed with this release's versions: an Epic run on a real Epic whose design holds a `[DT#N]` entry traces it, reports its test apart, and writes the `Threats:` line; what a miss looks like.
- [ ] **Step 7: Gates.** Measure `CLAUDE.md` and every rules file this branch touched. **Step 8: Commit:** `release(sec-g2): security conformance — workflows-core <X>, dev-workflows <Y>, and three page patches`.

### Task 12: Close [security-sensitive]

- [ ] **Step 1: Consistency.** Every array, printed line and record form of *Exact copy* is verbatim in the file that owns it, and the precondition heading is identical in the format and the command (`command grep -F` each). The handoff file's fields equal what Phase 2 hands and the tracer's prompt names. `conformance-format`'s states equal Phase 5's and `/ready`'s reading.
- [ ] **Step 2: Forward references**, each now true: Task 1's read, Task 2's §6 runner, Task 3's consumer bullet, Task 4's writer and `/ready` reader.
- [ ] **Step 3: No regression (goal 5).** Trace **NR1** (F1) through the finished `conformance.md`, quoting the `file:line` that decides each step: no model at a known path, no section in any design read → no reference loaded, nothing printed, today's tracer input, arrays, record, report, `body_facts` and lineage. Then **NR2**: an `ard.md`-only folder with `[AD#n]` Rules and no model → the four-option array on each. Then list every hunk of `git diff origin/main...HEAD -- plugins/dev-workflows/commands/conformance.md` with the condition under which it acts; a hunk that acts on NR1 beyond the known-path probes and the section test is a defect — save Task 6 step 3's area-file identity, which acts only on an area-split folder and is named in the pull request.
- [ ] **Step 4: GIT-G1 audit.** `git diff origin/main...HEAD --stat` shows nothing under `.github/`, `specs-repo-git.md`, `specs-git.py`, `workflows-core-git.md` or `workflows-core-handoff.md`. `phase-handoff.md`'s diff is G1 and G2 exactly; the generated files' diffs are regeneration alone. In `conformance.md`, every hunk's heading context lies outside GIT-G1's sections, save G5 and G6. `design.md`'s diff is empty.
- [ ] **Step 5: The sweeps, closed.** Re-run every before/after count of Tasks 1, 4, 8, 9 and 10; each equals its intended value. Run the exclusivity probe once more, and a contradiction read for "every consumer executes `require-on-main`" and for "accept" beside "mitigation".
- [ ] **Step 6: The full CI list.** Every step `validate-catalog.yml` runs, in order — each `--selftest`, and the mermaid gate where `node` exists.
- [ ] **Step 7: The PR text**, drafted for the controller: G1 to G6, each with its approval; the files left for the GIT-G1 owner; the four approved answers and the answers to the questions below; the area-file identity change and its one-time rule; what `verified` does not claim; the three states with no exit and the follow-up scheduled; NR1 and NR2; the five versions; the attribution lines the session's system reminder gives for pull requests.
- [ ] **Step 8: The whole-branch review** is the controller's: Fable reviews the branch against the design and this plan.

## Questions for the maintainer

1. **Is G5 — the threat lines in `/conformance`'s Phase 6 `body_facts` — covered by the design's approval?** The design lists it as GIT-G1 edit 3, "in case the maintainer counts a command's handoff step as GIT-G1's"; question 2's answer names only the two `phase-handoff` edits and the `CLAUDE.md` clause. It is new behaviour, so the standing truth-edit OK does not cover it. **Recommended: yes** — one clause, as C's Task 10 added one to `/design`'s `body_facts`, named in the pull request. Without it the architect and the Dev learn of an `unanswered` threat from the record and the report alone (D7 loses one of its three channels).
2. **Are traced runs enough for D10's fixtures?** The repository has no harness that executes command prose, so the plan makes all eight fixtures scenario traces, with one live check logged for a real project. **Recommended: yes**, as B and C did. The alternative is a fixture specs tree and a scripted harness: a new script, a CI step in `validate-catalog.yml` (GIT-G1's file) and a larger build.
3. **If `CLAUDE.md` reaches 35,990 after the table row grows, may `## Conventions` (five bullets) move to `.claude/rules/plugin-authoring.md`?** That file loads with every read, and C moved *Adding a new plugin* there the same way. **Recommended: yes**, itemised line by line, only if the measurement requires it. The alternative is to leave `threat-model.md`'s row in `CLAUDE.md` unabbreviated and accept the 36,000 warning.

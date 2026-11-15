# SEC-G2 D — Security Conformance — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/dev-workflows:conformance` traces every threat-model mitigation to code — each design's `[DT#N]` Rules as new requirements, each `Mitigated by` pair joined to the `[AD#N]` Rule it names — lists where every threat that applies to the unit stands, and never accepts a mitigation's discrepancy.

**Architecture:**
- No new command, agent, branch prefix, id prefix, role, script or plugin dependency. `/conformance` gains requirements in Phase 1, handoff fields and output lines for the same tracers, a wider Phase 3 re-read, a narrower walk for mitigations, and one optional section and one header line in the same record.
- Each `threat-model.md` is read **from the default branch by `git show`, with no gate**. `workflows-core:phase-handoff` §5 rule 2 gains the carve-out that makes that lawful, and `CLAUDE.md`'s hard constraint the matching clause. On a PRD run where the PRD folder's own threat model stands, the PRD folder's `design.md` joins the existing document gate, and one PRD-level `ard-resolution` call becomes §3.7's fifth site.
- `workflows-core:threat-model-format` gains §10 (*The threats that land on a unit*), one sentence in §6 and a restated test in §9. `workflows-core:ard-resolution` adds `file:` to each invariant. `workflows-core:source-truth` §7.8 leaves a `design.md` entry out of the open entries. `/dev-workflows:ready` gains a seventh condition on the record's `Threats:` line.
- Nothing is written into `threat-model.md`, a `design.md` or a findings register, and no threat model becomes a prerequisite.

**Tech Stack:** markdown prose that agents execute; one comment string in `lineage-kinds.json`; generated reference parts (`scripts/reference-parts.py generate`); the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-15-sec-g2-d-security-conformance-design.md`, revision 3.1, approved by the maintainer 2026-11-15 with the four recommended answers, and amended at plan review (its note under the Status line). Cited below as *D1*…*D11*. Executors read the design with this plan: a decision it states is not repeated here.

**Answers and rulings at plan review** (2026-11-15; the review is `.superpowers/plan-review-1.md`, its findings cited as *C1*, *I1*…, *M1*…):
- **Maintainer 1 — G5 is approved by name:** `/conformance`'s `body_facts` carries the threat states. New behaviour.
- **Maintainer 2 — the PRD folder's `design.md` is gated on a PRD run** (C1), in Phase 0 step 4's existing `require-on-main` gate, as each Epic's is. Two GIT-G1 edits, both approved: G8 and G9. **Controller's refinement: only where the PRD folder's own threat model stands** (R15; N2); where none does, that design is neither gated nor read, as today.
- **Maintainer 3 — a fifth §3.7 site, approved by name** (C2): `/conformance`'s one PRD-level `ard-resolution` call, on which no stopping row stops. G10 and G11 are approved. **Maintainer 4 (after plan review 2, `.superpowers/plan-review-2.md`, findings *N1*…) — row C's repair offer is withheld there, approved by name:** `/conformance` puts no repair offer on row C at that site; the model falls back as unused and the run carries on.
- **Controller — G7** rides the standing truth-edit OK. **D10's fixtures are traced runs plus one live check**, named in the `dev-workflows` CHANGELOG as a departure from the design. **`CLAUDE.md`'s `## Conventions` moves to `.claude/rules/plugin-authoring.md` only if a measurement forces it** (R1).
- **Maintainer 5 (at Task 1's review, `.superpowers/sdd/2026-11-15-sec-g2-d-security-conformance/task-1-review.md`) — G2 is narrowed to gated deliverables, approved by the maintainer 2026-11-15:** its kind reads `a gated deliverable (§4.0)` in place of `a deliverable`, so `/ready`'s and `/brd-reconcile`'s existing default-branch reads of advisory artifacts, which name no working-tree copy, are not of it.

No question is open.

**Execution (already chosen):** subagent-driven. Opus implements every task. **A task marked [security-sensitive] has its task review routed to Fable; one marked [mechanical] to Opus.** Fable reviews the whole branch at the end.

**Base:** worktree `/home/ihudak/dev/ai-tools/ai-workflows-wt/sec-g2d`, branch `feat/sec-g2-d-security-conformance`, `main` at `ec60ad47` plus the design commits. Every line number below was read there and is a finding aid only: **locate every site by the quoted phrase.** C as built is the model for every pattern: `docs/superpowers/plans/2026-11-14-sec-g2-c-design-threat-review.md`, `/design`'s Phase 2.5, `.claude/rules/threat-model.md`. *Format §N* is `plugins/workflows-core/references/threat-model-format.md`.

**The GIT-G1 edits — every one, with its approval:**

| # | Edit | Task | Approval |
|---|---|---|---|
| G1 | `phase-handoff.md` §4.0, the `threat-model.md` register row: `/dev-workflows:conformance` as an ungated reader of the default branch's copy | 1 | Design question 2, by name (truth edit) |
| G2 | `phase-handoff.md` §5 rule 2: the carve-out for a consumer that reads `<default-ref>`'s copy alone | 1 | Design question 2, by name (**new rule**) |
| G3 | `CLAUDE.md` § Hard constraints: the matching clause, replacing wording | 1 | Design question 2, by name |
| G4 | `reference-parts/phase-handoff/require-on-main.md`, regenerated, never hand-edited | 1 | Follows G2, G9, G10 |
| G5 | `conformance.md` Phase 6: `body_facts` gains the threat lines | 9 | Maintainer answer 1, by name (**new behaviour**) |
| G6 | `conformance.md` Phase 0 step 4: the clause "a `design.md` is context" | 6 | Standing OK — truth-only, named by D11 |
| G7 | `conformance.md` Phase 6, the annotated-document list: `ard.md` becomes `ard.md` or an `ard-<area>.md` | 9 | Standing OK — truth-only (controller's ruling) |
| G8 | `conformance.md` Phase 0 step 4: on a PRD run where the PRD folder's own threat model stands, the PRD folder's `design.md` joins the gated set | 6 | Maintainer answer 2, as the controller refined it (**new gated path**) |
| G9 | `phase-handoff.md` §3.4, `/dev-workflows:conformance`'s row: the PRD run's set gains the PRD folder's `design.md`, where the PRD folder's own threat model stands | 1 | Maintainer answer 2, as refined (truth edit) |
| G10 | `phase-handoff.md` §3.7: the count word and one passage — `/conformance` is the fifth caller that reads a stopping row without stopping | 1 | Maintainer answers 3 and 4, by name — the fifth site, and no repair offer on row C there |
| G11 | `ard-resolution.md`, *No-regression rule*: the `unmerged` sentence and the paragraph opening `Any other stopping state` gain that one call | 3 | Maintainer answers 3 and 4, by name |
| G12 | `ready.md`, the paragraph opening `Key distinction from every other consumer`: its list of §3.7's callers gains `/conformance`'s site | 1 | Standing OK — truth-only, a copy of G10's claim (C's precedent) |

Nothing else of GIT-G1's is edited. Named in the pull request as left for its owner, each still true: `.claude/rules/workflows-core-handoff.md` and `.claude/rules/workflows-core-git.md` (the count of sixteen `require-on-main` callers stands), `phase-handoff.md`'s "one row" clause in §4.1, and `/conformance`'s *Ending early* (R9).

## Global Constraints

### What is not ours

- **Never edited:** `plugins/workflows-core/references/specs-repo-git.md`, `plugins/workflows-core/scripts/specs-git.py`, `.github/workflows/validate-catalog.yml`, `.claude/rules/workflows-core-git.md` (19,993 characters) and `.claude/rules/workflows-core-handoff.md`.
- **`phase-handoff.md` takes G1, G2, G9 and G10 and nothing else.** Its generated files come from `python3 scripts/reference-parts.py generate`.
- **In `conformance.md`, leave GIT-G1's sections alone:** *Ending early*; Phase 0's specs preflight, `branch-check`, step 4's gate (save G6 and G8), step 5's record check; Phase 6's class paragraphs, arrays and printed lines (save G5 and G7); Phase 9's `commit-artifacts`. **Never add text inside one of them beyond a named edit.** A step that finds it needs one stops and reports to the controller.
- **`/design` is unchanged** (D2): `plugins/dev-workflows/commands/design.md` takes no edit on this branch.
- **`threat-model.md`, every `design.md` and every register are read-only to `/conformance`.** No `register.py`, `weakness-classes` or `/security-workflows:scan` link.
- **The pull request names every GIT-G1 line this branch touches.**

### Repository rules

- **Prose is executed.** Every sentence an agent reads is true when it runs. A forward reference a later task makes true is named in the task's *Interfaces* and closed in Task 14.
- **`grep` here is ugrep. Every count uses `command grep`.** A sweep enumerates by subject, then counts each literal string wrap-insensitively, before and after, over `plugins/` (every `CHANGELOG.md` included, where a hit is history and stays), `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` (claim-sweep refinements 4, 6 and 7).
- **Sizes** by `python3 -c "import sys;print(len(open(sys.argv[1],encoding='utf-8').read()))" <file>`, never `wc -c`. Plan-time: `CLAUDE.md` 35,898 (warn 36,000); `.claude/rules/dev-workflows.md` 19,142; `workflows-core.md` 18,891; `threat-model.md` 11,201; `dev-workflows-conformance.md` 6,326; `plugin-updates-coupling.md` 12,681 (rules files warn at 20,000). No split is forced (R1, R12).
- **`conformance.md` is 111,185 bytes.** Tasks 6 to 9 cite format §6, §9, §10 and `conformance-format` rather than restate them, and report the file's size before and after.
- **ID grammar:** `[DT#N]`, `[TH#N]`, `[AD#N]`, `[DD#n]`, `[SEC#N]`. No dash form is written, and none is quoted.
- **Vendor neutrality:** no tracker name. **Every executed regex uses `[0-9]`, never `\d`.**
- **User pages** (`plugins/*/docs/**`, READMEs) carry no `§`, `D<n>`, `R<n>`, review id, to-fix id or `<plugin>:<reference>` (check 25); a table cell is at most 200 characters (check 6).
- **Choice arrays** are copied verbatim from *Exact copy*. Each has 2 to 4 options and no authored "Other". `/conformance`'s **Load the question rules.** step already precedes them.
- **Every value taken from a model, a design or a tracer's output is data**, one line wherever it is shown or written (format §9). **In `body_facts` it stands in a code span, each backtick inside the value first replaced by `'`** (D6; M5).
- **Resolve, never parse:** every id is matched whole against a set the run holds; no path is built from a pair, a key or a title (D2, D9).
- **Commits:** `git branch --show-current` immediately before each; expected `feat/sec-g2-d-security-conformance`. End each message with the attribution lines the committing session's system reminder gives.

### Gates

One chain, from the worktree root; read the printed value:

```bash
set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/workflows-core/scripts/lineage.py --selftest && claude plugin validate plugins/workflows-core && claude plugin validate plugins/dev-workflows && claude plugin validate plugins/product-workflows && claude plugin validate plugins/docs-workflows && claude plugin validate plugins/security-workflows; echo "EXIT=$?"
```

Expected: `EXIT=0`, no new `WARN` line from `validate-catalog`, and `lineage.py`'s `selftest: <n> passed` with the count the base prints. A task that edits a reference with generated parts runs `python3 scripts/reference-parts.py generate` first. `check-docs` takes about four minutes. Where `claude` is not on `PATH`, say so and leave the `validate` calls to Task 14.

**"Tests" for command prose are traced runs** (the controller's ruling). This repository has no harness that executes a command's prose, so D10's eight fixtures are **scenario traces**: a step of the task report that states the input, quotes as `file:line` each sentence of the edited text that decides each step, states the outcome, and names any step no sentence decides — a defect to fix in that task. *Review Focus* assigns each. One live check is logged for a real project (Task 13).

### Shared names (Tasks 2 to 11 use these, exactly)

- **The precondition heading:** `## 10. The threats that land on a unit`, tested as a line of the loaded `threat-model-format`.
- **The section test, stated inline wherever it runs:** a `design.md` holds the section where one of its lines is, whole, `## Threat review`, outside any fenced block. It names `pre-lint` in words only, never as a citation, so it loads nothing (I13).
- **`threat_input`**, one per run: `none` — no `threat-model.md` stands at a known path, on `<default-ref>` or in the working tree, and no `design.md` the run reads holds the section; `not-traced` — some stands and the precondition fails, or `threat-model-format` cannot be loaded; `traced` — otherwise.
- **A model's `use`:** `read`; `unused — <why>`; `not landed` (the working tree alone holds it); `not a model` (its `kind:` is not `threat-model`). **`<why>` is one of six, the same words in the printed line and in the record's `not read:`** (M3): `no ARD resolves for it`; `no component set resolves`; `the Epic's target is not in the component set` (I7); `its ARD is not on the default branch`; `its ARD's working copy differs from the default branch's`; `threats not traced`.
- **A design not read** (M2): a `design.md` Phase 0 step 4's gate returned `absent` for, in a folder whose model is `read`. No other design is "not read": one the gate stops on has stopped the run.
- **A requirement's identity** is `(key, id, document)`. New ids: `[DT#N]` with `document: design.md`; `[AD#n] Rule (ard-<area>.md)` with `document: ard-<area>.md`. A decision of `ard.md` keeps `[AD#n] Rule` and `document: ard.md`.
- **The join of a pair** (I1) is on three things, never fewer: the folder the pair names — the model's own folder for `<ARD file> [AD#N]`, the PRD folder for `[[<KEY>]] ard.md [AD#N]` where `<KEY>` equals, whole, the run's `<PRD>` — the `file:`, and the number. It is the requirement whose `key` is that folder's key, whose `document:` is that basename and whose id carries that number. None, or more than one → that part is `not checked`.
- **A mitigation** (D5): a `[DT#N]` Rule, or an `[AD#n]` Rule a live, non-stale threat in scope joins to. **Walk-only mitigations:** every `[AD#n]` Rule of an unused model's folder's ARD files and of the PRD-level ARD it inherits — for the arrays alone, never `mitigation: true`.
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
- `Threats: <path> not used — <why>`
- `Threats: no accept is offered on <n> architecture Rule(s) — a threat model the run could not use may rest on them` — once, where walk-only mitigations exist.
- `conformance-tracer (<repo_slug>): <n> section(s) dropped — each heading names no requirement routed to it`

**The record's header line**, after `Verdicts:` (`conformance-format` §2 pins it):

```
- **Threats:** <n> verified · <n> open · <n> not checked · <n> unanswered · <n> accepted · <n> review due · <n> stale · <n> unreadable[ — not read: <each model unused, as "<path> (<why>)"; each model not landed; each design not read>]
- **Threats:** not traced — update workflows-core
```

Every count is written, zero included. **`/ready` reads it so** (R7; M11): only lines before the record's first `## ` heading; a line is the header line where it matches, whole, `^- \*\*Threats:\*\* ([0-9]+) verified · ([0-9]+) open · ([0-9]+) not checked · ([0-9]+) unanswered · ([0-9]+) accepted · ([0-9]+) review due · ([0-9]+) stale · ([0-9]+) unreadable( — not read: .+)?$` or `^- \*\*Threats:\*\* not traced — update workflows-core$`; the `not read:` tail is never parsed.

**The record's section**, before `## Discrepancies`:

```markdown
## Threats

- **Models read:** <each model's path relative to $SPECS_PATH, or none>
- [[<KEY>]] [TH#N] <title> — <state>[ — <reason>][ — <each mitigation, with its verdict or [DD#n]>]
- [[<KEY>]] [DT#N] <title> — <state> — <why it stands alone>
```

**The backstop's two commands** (I14), `<clone>` and `<ref>` those of the tracer whose section holds the match, never another repository's: a path match — a prefix, since the pattern ends at `register.`, `runs/` or `scans/` — is carried where `git -C <clone> ls-tree -r --name-only <ref>` prints at least one line that begins with the match, each `\` in the match first read as `/` (N5); a `SEC#<n>` where `git -C <clone> grep -q -E -e 'SEC#[[:space:]]*<n>([^0-9]|$)' <ref>` exits 0.

**The no-exit sentence** (D7), on each Next-step line for `unanswered — returned to the architect`, `unanswered — no design takes it`, and `open` on a decision the team will not build: `No command re-disposes a live threat that is not stale yet: the architect supersedes the decision, or waits for the intake of returned threats.`

**G1**, inserted in the register row before `No other command reads it as a threat model.`: `` `/dev-workflows:conformance` reads it too, ungated and never from the working tree: `<default-ref>`'s copy alone, at its Phase 1, for the models of the unit it checks (§5 rule 2's consumer that executes no gate). ``

**G2**, appended to §5 rule 2 after `A gate that fires after a scan has already spent what it was meant to save.`: `` **One kind of consumer executes no gate.** A consumer that reads a gated deliverable (§4.0) only as `<default-ref>` holds it — by `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`, the object name written as §3.2 writes one, never from the working tree or any other ref — cannot read content that has not landed, so it executes no `require-on-main` on that deliverable; it names, in one line, a copy the working tree holds that `<default-ref>` does not. `/dev-workflows:conformance` reads each `threat-model.md` so, at its Phase 1. On a specs tree that is no git repository there is no other copy, and the file is read. ``

**G3**, in `CLAUDE.md`'s bullet opening `A phase is not finished until`: `` every consumer executes `require-on-main` before expensive work; `` becomes `` every consumer gates or reads the default branch's copy alone (`workflows-core:phase-handoff` §5 rule 2); ``, and later in the same sentence `` (`workflows-core:phase-handoff` §3.4 names `` becomes `` (its §3.4 names ``. Net about +12.

**G9**, in §3.4's `/dev-workflows:conformance` row: `` on a PRD run `prd.md`, the PRD-level `specification.md`, and each Epic's `` becomes `` on a PRD run `prd.md`, the PRD-level `specification.md`, the PRD folder's `design.md` where the default branch holds a `threat-model.md` in that folder, and each Epic's ``.

**G10**, in §3.7: `**Four callers read a stopping row without stopping, by design.**` becomes `**Five callers read a stopping row without stopping, by design.**`, and, after the last caller's passage and before the sentence `No other caller may take any of these exceptions`: `` `/dev-workflows:conformance` is the fifth, at one site: on a PRD run of a PRD with no Epic folder whose folder holds a `threat-model.md`, its Phase 1 calls `ard-resolution.md` at PRD level only to learn which decisions that model's threats rest on, and on any stopping row leaves the model unused, says so in one line, puts no repair offer on row C — the switch and pull would move the checkout, and `<default-ref>`, under records and a model the run has already read — and continues — the model is an optional input, and a run that makes no such call where no model stands must not stop because one does. Every other `ard-resolution` call of that command stops as before. ``

### Rulings where the design is silent or leaves it to the builder

- **R1 — `CLAUDE.md`'s room.** G3 nets about +12 and the rules table's `threat-model.md` row gains about 62 (Task 11): about 35,972. Task 11 measures; at 35,990 or above, `## Conventions`' five bullets move to `.claude/rules/plugin-authoring.md`, byte for byte and itemised line by line, as C moved *Adding a new plugin*. Not otherwise.
- **R2 — the precondition is tested only where threat input exists.** A run whose `threat_input` would be `none` loads no reference and prints nothing, so goal 5 holds beside any `workflows-core`.
- **R3 — on a `not-traced` run, a `[DT#N]` entry on file is carried forward as it stands**: never `resolved`, never `requirement withdrawn`, its follow-up kept.
- **R4 — the tracer names what reaches a check on a line of its own**, on a `mitigation: true` section: `- reached by: <file:line@commit>, one per call site | none — searched <the searches run> | not owed — <the Rule's shape, in a few words>`. **The orchestrator, not the tracer, has the last word on it** (I6): Phase 2's compose demotes `satisfied` with `reached by: none — searched …` to `partial`, `shipped:` ending `the check is not called`; Phase 3 judges the Rule's shape itself from the Rule's text, and a `satisfied` mitigation whose Rule is carried out by code that must be reached and whose section says `not owed`, or holds no `reached by:` line, is *unverified*.
- **R5 — where each threat stands is computed once, in Phase 5, after the walk and before the record is written.**
- **R6 — `/ready`'s new condition is the seventh, appended.** Every "condition 6" pointer in `ready.md` stays true; every statement of how many conditions there are, and of which is last, is swept (Task 10).
- **R7 — a `Threats:` line `/ready` cannot read fails closed.** More than one header-position line opening `- **Threats:**`, or one matching neither pattern of *Exact copy*, fails condition 7 with `threats line unreadable — re-run /dev-workflows:conformance <PRD>`.
- **R8 — the Final report gains `### Threats`**, between `### Verdicts` and `### Discrepancies`, only where `threat_input` is not `none`: the header's counts, then one flat list of every threat and stand-alone entry not `verified` or `accepted`, each line ending with its owner's route.
- **R9 — *Ending early* takes no edit.** D adds no stop and no run-ending answer: each new array's *Cancel* is "Phase 4's walk *Cancel*", G8's gate is "step 4's gate", and the fifth-site call stops nothing. Task 9 verifies it.
- **R10 — the model's read cites `phase-handoff` as Phase 0 step 5.2 does**, and `check-citations` decides whether a pointer is cited or worded.
- **R11 — the legacy match** (D3's one-time rule; I4). (a) **Exact identity first:** the rule is tried only for an entry or `## Satisfied` line on file that matches no requirement of the inventory, reads `[AD#n] Rule` with `document: ard.md`, and sits in a folder whose `ard.md` holds no live decision of that number; it then matches where exactly one area file of that folder holds that number, and is otherwise `orphaned`. (b) **The unit's own record** is rewritten in the new form when the record is written. **An Epic record is never rewritten for it, and a PRD entry that rules on or lists a legacy-form Epic entry keeps that Epic entry's heading and `document:` verbatim**, so every heading-and-`document:` comparison — `workflows-core:source-truth` §7.8 rule 1, Phase 4's paragraph opening `An entry the record on file already decided`, Phase 5's *An overrule held back*, and `conformance-format` §5's last paragraph — still matches with no edit to any of them; such a PRD entry reaches its inventory requirement by (a). **One re-ask is expected** (N8): once an Epic's own re-run rewrites its record in the new form, the PRD record's entry still holds the legacy heading until the next PRD run, where Phase 4's same-requirement test fails once and the PE is asked again; that run then writes the new form. (c) **The population cannot be counted here** — this repository holds no specs tree — so D3's rule is kept, not cut; Task 6 says so in its report.
- **R12 — `dev-workflows.md`'s edits are net-zero words**; `/conformance`'s map line and every new invariant go to `.claude/rules/dev-workflows-conformance.md`.
- **R13 — `review due`:** the review date is tested first against `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`; one that fails is `review due`. One that passes is compared with the record's `Run:` date as the run will write it: `python3 -c 'import sys,datetime as d; print(d.date.fromisoformat(sys.argv[1]) < d.date.fromisoformat(sys.argv[2]))' "<review-by>" "<Run: date>"`, and anything but `False` is `review due`.
- **R14 — the fifth site** (maintainer 3; C2). The PRD-level `ard-resolution` call is made only on a PRD run of a PRD with no Epic folder, only where `threat_input` is `traced` and the PRD folder's model was read from `<default-ref>`. **Every stopping row of its gate leaves the model `unused`**: rows D and E with `its ARD is not on the default branch`; every other stopping row with `its ARD's working copy differs from the default branch's`. **No repair offer is put on row C** (maintainer 4): the switch and pull would move the checkout, and `<default-ref>`, under records and a model the run has already read. G10 is the withholding — per-site handling of row C is §3.7's, the gate's own text — so Task 6 only makes the call. Row B′ prints the second of those two reasons, which is loose for a branch that is merely behind; the pull request says so (N9). On any return but `found`, no Rule of that call joins the inventory.
- **R15 — the PRD folder's `design.md`** (maintainer 2, the controller's refinement; C1) **is gated only where the PRD folder's own threat model stands — `<default-ref>` holds a `threat-model.md` in the PRD folder, or, on a tree that is no git repository, the working tree does** (N2: an Epic folder's model can put no `## Threat review` into the PRD folder's design, since `/design` on a PRD-level design reads the feature folder's model alone), tested in Phase 0 step 4 by the listing primitive step 5.2 uses, before the gate. Where none stands it is neither gated nor read, exactly as today: C offers no threat review without a model, so no `## Threat review` can be there, and D10's run with no model stays byte-equal. Where one stands it is gated, read and lineage-checked exactly as an Epic's is: `absent` falls back and is named nowhere a missing Epic design is not; a stopping row stops the run on that row's remedy. The test is the model's presence, not the §10 precondition, which Phase 1 learns later: on a `not-traced` run the design is gated and then unused. The CHANGELOG and the pull request say: on a PRD whose own threat model stands, an unlanded PRD-level `design.md` now stops the run, as an Epic's does.
- **R16 — what a *Cancel* leaves** (I5). The walk has no skip: a *Cancel* ends the run and writes nothing, so the record on file stands. An `accept` on what is now a mitigation leaves its threat `open` only where this run did not put the entry — a PRD record's `final` entry seen on an Epic run, or a `lists:` entry. The residue goes in the pull request: a record written before D with an `accept` on a mitigation keeps passing `/ready`, having no `Threats:` line, until a D-era run completes.

## Review Focus

Inputs a reasonable Dev or PE will hit that no gate exercises. Each has a scenario trace in its owning task; F-numbers are D10's eight fixtures.

| # | Input | Expected | Trace |
|---|---|---|---|
| RF1 (F2) | Epic run; the PRD folder's landed model defers a threat that reaches the Epic's target only through a contract row; the Epic's `design.md` has no `## Threat review` | `unanswered — no design answers it`, the design named; Next step Dev → `/dev-workflows:design <KEY>`; nothing stops | Task 9 |
| RF2 | The architect's uncommitted refine drops a threat the default branch's model holds; a second folder holds a `threat-model.md` on no ref | The landed threat is listed; the stray file gets the `not on the default branch` line, binds nothing and withholds nothing | Task 6 |
| RF3 | A D-era `dev-workflows` beside a `workflows-core` with no §10, on a unit with a landed model | `Threats: not traced — update workflows-core`; no model read, no `[DT#N]` handed; no accept on the folder's `[AD#n]` Rules; `/ready` holds the rung | Tasks 6, 8, 10; whole in 14 |
| RF4 (F6, F7) | PRD run; an Epic record, hand-edited, lists a mitigation under `## Satisfied`; another Epic entry decided `accept` on a mitigation | The mitigation is traced in full and re-read; the `accept` is put at the third array and applied as an overrule; on *Cancel* nothing is written and the record on file stands | Tasks 6, 8; whole in 14 |
| RF5 (F8) | An area-split folder: `ard-cart.md` and `ard-payments.md` each hold `[AD#2]`; the record on file holds `[AD#2] Rule`, `document: ard.md`. Then the same with an `ard.md` that also holds a live `[AD#2]` | Two requirements, each with its file; the old entry `orphaned`; with one area file holding the number and no `ard.md` decision of it, it matches; with `ard.md`'s own `[AD#2]`, it is that decision's by exact identity and the legacy rule is never tried | Task 6 |
| RF6 | A tracer's output holds a section headed for a requirement not routed to it, a mitigation in two sections, a register path no listed file begins with, another one a listed file does begin with, and `SEC#12` where the ref holds only `SEC#123` | The stray section dropped and counted; the doubled one *unverified*; the first path and the id withheld and their requirement *unverified*, the second path carried; nothing the agent wrote is echoed | Task 7; again in 14 |
| RF7 (F4) | Three `[DT#N]` Rules: "passwords are stored as argon2id hashes", with a test; a check that exists, is never called and has no test; a check-shaped Rule the tracer returns `satisfied` with `reached by: not owed` | The first owes no call site; the second is `partial`, the check not called and the test missing; the third is *unverified* | Tasks 5, 7 |
| RF8 | A mitigation's question answered in free text "accept it as shipped"; a mitigation sharing an evidence location with two ordinary discrepancies | Asked again, the text saying only the architect accepts, in the model; the mitigation is asked alone and the other two cluster | Task 8 |
| RF9 (F5) | A landed model whose folder resolves no ARD; a PRD with no Epic folder whose PRD-level call meets rows D and C | Each `unused`, named in `not read:`; accept withheld on the walk-only Rules; no repair offered; the run does not stop | Tasks 6, 8; whole in 14 |
| RF10 (F3) | A design's entry `Returned to the architect` on a deferred threat | `unanswered — returned to the architect`, PA route with the no-exit sentence | Task 9 |
| RF11 | An Epic folder with its own `ard.md` under a PRD with `ard.md`, both holding `[AD#1]`; the Epic's model says `Mitigated by ard.md [AD#1]`, the PRD's `[[<PRD>]] ard.md [AD#1]` is unrelated | The Epic folder's `[AD#1]` alone is the mitigation and loses *Accept as shipped*; the PRD's keeps the four-option array | Task 6; again in 14 |
| RF12 | An Epic whose `target:` is not in the component set, under a PRD whose landed model mitigates by `[AD#3]` | The model `unused — the Epic's target is not in the component set`; no accept on the walk-only Rules | Task 6; again in 14 |
| RF13 | A PRD with no Epic folder: a landed model defers a threat, and the PRD folder's `design.md` answers it with a `Mitigated` `[DT#1]` | The model stands, so the design is gated and read; `[DT#1]` is traced; the threat follows its Rule, never `unanswered — no design answers it`. The same PRD with no model: the design is neither gated nor read. The same on a tree that is no git repository: the gate returns `unmanaged`, and the model and the design are both read. With a model in an Epic folder only: the PRD-level design is not gated | Task 6 |
| F1 | No model at a known path, no `## Threat review` in any design read | Today's tracer input, arrays, record, report, pull-request body and lineage | Task 14 (NR1) |

---

### Task 1: `phase-handoff` — the consumer that executes no gate, the fifth site, and `CLAUDE.md`'s clause [security-sensitive]

**Files:**
- Modify `plugins/workflows-core/references/phase-handoff.md`: G1, G2, G9, G10, each verbatim from *Exact copy*.
- Regenerate `plugins/workflows-core/reference-parts/phase-handoff/` (expect `require-on-main.md` alone to change: G1's row lies outside every `<!-- entry -->` region; §3.4, §3.7 and §5 rule 2 lie in `require-on-main` regions).
- Modify `CLAUDE.md` § Hard constraints: G3. Modify `plugins/dev-workflows/commands/ready.md`: G12.

**Interfaces:** produces the rules Task 6's read, gate and call rely on. **Forward references:** G1, G2, G9, G10 and G12 name behaviour `/conformance` has only from Task 6.

- [ ] **Step 1: Before counts.** `No other command reads it as a threat model` (7 files at plan time), `executes no gate` (0), `before expensive work` (record it), `Four callers read a stopping row` (2: the reference and its generated file). Then enumerate **by subject** every statement of which callers read a stopping row without stopping: `command grep -rn 'without stopping' plugins .claude/rules CLAUDE.md`, each hit read. At plan time the copies are §3.7, its generated file, and `ready.md`'s *Key distinction* paragraph; §6.3's "Two callers read a stop of §6.1" is `branch-check`'s and is not this claim. **The phrase misses copies worded otherwise** (N4): also read every hit of `stops when`, `never stop`, and `save` beside `threat model`, over the same scope and `plugins/*/docs`. At plan time that finds the user page `plugins/dev-workflows/docs/commands/ready.md`, the bullet opening `The gated ARD/spec/design themselves` ("Every other command of this plugin that gates an artifact … stops … save `/design` on a threat model beside the ARD"), which is true only from Task 6 and is edited in Task 10; list it in the report as owed there.
- [ ] **Step 2:** Confirm §3.2 still writes the object name as `<ref>:./<path>`. G2 credits `git show` to no section (I2).
- [ ] **Step 3: Apply G1, G2, G9 and G10**, then `python3 scripts/reference-parts.py generate`. `git diff --stat` shows `phase-handoff.md` and `require-on-main.md` only.
- [ ] **Step 4: G12.** In `ready.md`'s paragraph, the list of other callers gains `/dev-workflows:conformance` at one site, its PRD-level `ard-resolution` call for a threat model, in the list's own style. Nothing else in the paragraph moves.
- [ ] **Step 5: Apply G3.** Itemise what the cut words said and where each now stands: `require-on-main` by name and "before expensive work" are §5 rule 2's first sentence; the §3.4 pointer is kept. Measure `CLAUDE.md`: expect about 35,910.
- [ ] **Step 6: Contradiction read.** §3.7 whole (the sentence before it, "every caller then stops, save at the sites named below", still holds), §5 whole, §4.0's class table, and `require-on-main.md`'s copies: no sentence still says every consumer gates, or that four callers read a stopping row. Report each sentence read. After counts.
- [ ] **Step 7: Gates. Step 8: Commit:** `feat(sec-g2): phase-handoff — a reader of the default branch's copy alone executes no gate; /conformance is §3.7's fifth caller`.

### Task 2: `threat-model-format` — §10, §6's sentence, §9's restated test, and who reads the model [security-sensitive]

**Files:**
- Modify `plugins/workflows-core/references/threat-model-format.md`.
- Modify `.claude/rules/threat-model.md`: the authority paragraph, invariants 2, 5 and 8, a new invariant 9.
- Modify `plugins/workflows-core/docs/reference/references.md`: the format's row, in words.

**Interfaces:** produces the heading `## 10. The threats that land on a unit`, placed after §9 and before `## Example`; §6's no-path sentence; §9's test for an agent given a repository; the one reader sentence Tasks 11 and 12 repeat. **Forward references**, all to Task 6: the §6 runner and the fifth reader.

- [ ] **Step 1: §10.** Take, in `/design`'s own words, exactly the sentences of `design.md`'s Phase 2.5 step 7 that D2 lists: the three bullets; ids and pairs compared whole; the PRD folder's model read itself, never `## Inherited threats` bullets; and the malformed rule with its four causes, such a threat landing whatever its Where. **The only rewordings allowed:** what names `/design`'s own run ("this design" → "the unit", "Phase 2.5's `contracts`" → "the `contracts` `ard-resolution` returned"), and the two pointers that dangle once moved (M6) — "as step 6 reads one" becomes §6's own description of a threat, and "the three forms below" becomes "the three forms §4 gives". Then D's two sentences, marked as `/dev-workflows:conformance`'s alone: a stale threat is listed whatever its Where, since staleness is tested before landing; and a threat an in-scope live entry answers is in scope. Then: a PRD run applies no filter. The section says `/dev-workflows:design` states the same rule in its own Phase 2.5 and does not yet cite this section.
- [ ] **Step 2: §6.** Add `/design`'s sentence, generalised: a pair is read only in the file of `ard_paths` whose folder and whole basename it names, and no path is ever built from one. Add `/dev-workflows:conformance` to who runs the check: read-only, at its Phase 1, on each model it reads, against the ARD files `ard-resolution` returned (`ard_paths`) and its own resolved set; it lists each stale threat and clears none.
- [ ] **Step 3: §9.** Restate the test for an agent given a repository (D9): for `dev-workflows:conformance-tracer`, a match is one the agent could have been given where the traced ref holds it, by the two commands of *Exact copy*, written here verbatim; any other match is withheld. Say why the second command ends as it does: *it compares whole matches*, so `SEC#12` is not found in `SEC#123`. Add `/dev-workflows:conformance` to the section's list of commands, as one that dispatches an agent that reads code and holds its output to the backstop. The two patterns and the three binding rules are not changed.
- [ ] **Step 4: The reader sentence** (I8), one wording in the format's opening and §8 and the rules file's invariant 5: five readers by name — `/dev-workflows:conformance` joins, as the one that reads the default branch's copy, ungated, at its Phase 1, for the unit it checks, and judges no threat's sufficiency. The format's `is to read it later` and `conformance` … `later` sentences go, the "two `dev-workflows` commands read it" sentence loses its "now" and "later"; invariant 5's "D must sweep this bullet" paragraph is removed, its claim expired; invariant 2 says the model has two readers of two kinds, `/design`'s falling-back gate and `/conformance`'s ungated default-branch read; invariant 8 widens to "neither `/design` nor `/conformance` writes into it". Before and after counts: `Four readers by name` (2 files → 0), `is to read it later` (2 files → 1, the `workflows-core` CHANGELOG, which stays; M9), `will add `/dev-workflows:conformance`` (1 → 0).
- [ ] **Step 5: Invariant 9.** Format §10 and `/design`'s Phase 2.5 step 7 state one rule and change together; the two sentences that are `/conformance`'s alone are named; `/design` moves onto §10 by a logged follow-up (Task 13), because beside an older core a `/design` citing §10 would lose its review. The authority paragraph's section list gains §10.
- [ ] **Step 6: Diff check.** List §10's sentences beside `design.md`'s, one per line, in the report; every difference is one Step 1 allows.
- [ ] **Step 7: Gates. Step 8: Commit:** `feat(sec-g2): threat-model-format §10 — the threats that land on a unit; §6 builds no path, §9 for an agent given a repository; a fifth reader`.

### Task 3: `ard-resolution` — each invariant carries its file; the one call that does not stop [security-sensitive]

**Files:** Modify `plugins/workflows-core/references/ard-resolution.md`; `plugins/workflows-core/docs/reference/references.md` only where its row states the output's fields or which caller stops.

**Interfaces:** produces `file: <basename of the ARD file that holds the decision>` on each `invariants` entry, after `source:`. Additive: a caller that reads no `file:` behaves as before. Task 6 builds identities and joins from it, with the folder (`source`) beside it.

- [ ] **Step 1:** Add `file:` to the output block, and to step 3's tuple, `AD#N {id, binds, prevents, rule, source, file}` (M7). One sentence: the basename, whole, of the file of `ard_paths` the decision was read in — `ard.md` or `ard-<area>.md` — never a path, never derived from the id; **a basename alone names no decision**, since an Epic folder's `ard.md` and the inherited PRD folder's each number from `[AD#1]`: `source` says which folder.
- [ ] **Step 2: G11.** In *No-regression rule*, the sentence opening `A caller that gets `status: unmerged` **stops**` gains a second exception beside `/ready`: `/dev-workflows:conformance`'s one PRD-level call for a threat model, on a PRD with no Epic folder, which leaves the model unused and continues (`phase-handoff` §3.7's fifth site). The paragraph opening `**Any other stopping state of that gate stops the caller as `unmerged` does.**` gains the same exception, and says, in G10's words, that the call puts no repair offer on row C. Read the whole file after the edit — the sentence `Reading it as `unmerged` would stop every consumer but `/ready`` stands outside the section (N6) — and list, in the report, each sentence about who stops, with its truth after the edit — **expect the two sentences changed, any other the read finds false corrected to the same exception, and none left false** (this replaces draft 1's step, which expected none changed).
- [ ] **Step 3: *Consumers*.** `/conformance`'s bullet gains: it reads each invariant's `file`, and `contracts`; and that one call. The sentence `` and `components` alone by `/conformance` `` is corrected (count before 1, after 0). **Forward reference** to Task 6.
- [ ] **Step 4: Gates. Step 5: Commit:** `feat(sec-g2): ard-resolution — each invariant carries its file; /conformance's PRD-level call for a threat model stops on no row`.

### Task 4: The record — `conformance-format`, and `source-truth` §7.8 [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/references/conformance-format.md` (§2, §3, §5, §6).
- Modify `plugins/workflows-core/references/source-truth.md` §7.8, *Which entries are open*.
- Modify `.claude/rules/workflows-core.md` (the `source-truth` paragraph, one clause) and `.claude/rules/dev-workflows-conformance.md` (*The record's readers*).

**Interfaces:** produces the header line and `## Threats` of *Exact copy*; the `document:` values and id forms; §5's exception; R11's rule; the rule that a `design.md` entry is not open. Tasks 5 to 10 consume them (Task 5 its `document:` values and ids; M13). **Forward reference:** the command writes none of it until Task 9.

- [ ] **Step 1: §2.** Add the `Threats:` header line after `Verdicts:` and `## Threats` before `## Discrepancies`, both forms verbatim, with `/ready`'s reading of the line as *Exact copy* gives it; when each is written (wherever `threat_input` is not `none`; otherwise neither, and a record without them is not read as zero); the section rewritten whole each run; states, reasons, the six `<why>` words and "a design not read" as *Shared names* gives them; the state function cited as `/dev-workflows:conformance` Phase 5's; titles and reasons as data, one line. `Not traced:` still names no `design.md` and no model — reword "a `design.md`, which is context and never traced" to say a design's `[DT#N]` Rules are traced as requirements while the design is not a document that line names.
- [ ] **Step 2: §2, `## Satisfied` and `## Unverified`.** A `[DT#N]`'s line lists its `test:` location among its evidence, so a deleted test moves it. The sentences saying a later PRD run re-traces a `## Satisfied` requirement "only where the code at its evidence … changed" gain the exception: a mitigation is traced in full every time (D8).
- [ ] **Step 3: §3.** `document:` becomes `<specification.md | epic.md | prd.md | ard.md | ard-<area>.md | design.md>`. State the id form for an area file's decision, and R11 whole, (a) and (b). A `[DT#N]` entry decided `amend-document` carries no note: its `effect:` names `/dev-workflows:design <KEY>`.
- [ ] **Step 4: §5.** The exception to "carries each decided entry forward without asking again" and to "asks only about those": an entry on file decided `accept` whose requirement is now a mitigation is put again, keeps its `[DD#n]`, and its earlier decision is shown; a PRD record's own entry whose `ruling:` confirms a Dev's `accept` is put again as an overrule. A `[DT#N]` on file that is withdrawn or no longer `Mitigated` is `requirement withdrawn`. The last paragraph (`superseded-by`, "with the same `document:`") is read against R11 (b) and left unedited.
- [ ] **Step 5: §6.** `/dev-workflows:ready` also reads the `Threats:` line (**forward reference** to Task 10). `/document` and `/release-notes` read no entry whose `document:` names `design.md`: §7.8 leaves it out.
- [ ] **Step 6: §7.8.** In *Which entries are open*, rule 2 gains: drop an entry whose `document:` names `design.md` (M8) — a mitigation the design owns, settled in the design and never by a documentation decision; it is not open here and is reported by no reader of this list. Read the rest of §7.8 for a sentence that enumerates `document:` values or says every entry maps, and correct each; rule 1's heading-and-`document:` comparison is read against R11 (b) and left unedited.
- [ ] **Step 7: Sweeps**, counted before and after: *what a re-run carries forward* (§5's two bullets); *the `document:` values* (`command grep -rn 'epic.md | prd.md | ard.md'`: 2 files at plan time, the handoff file's copy being Task 5's); *what a later run re-traces* in this file (Step 2).
- [ ] **Step 8: Gates. Step 9: Commit:** `feat(sec-g2): the conformance record — a Threats line and section, design.md and area-file decisions, no accept carried onto a mitigation`.

### Task 5: The tracer — a marked mitigation, its test and what reaches it [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/references/handoff/conformance-tracer.md` and `plugins/dev-workflows/agents/conformance-tracer.md` (the untrusted-content block stays byte for byte; check 20).
- Modify `plugins/dev-workflows/docs/reference/agents.md`: the tracer's row, in words.

**Interfaces:**
- Consumes Task 4's `document:` values and id forms.
- Produces, in `requirements[]`: `id` also `[DT#N]` or `[AD#n] Rule (ard-<area>.md)`; `document` also `design.md | ard-<area>.md`; `mitigation: true` (omitted otherwise); `test_hint: <one line>` (a `[DT#N]` only); `own_part` and `binds` also on a `[DT#N]` whose Where names another component. In a section: `- test: <file:line@commit> | none — searched <the searches run>` on a `[DT#N]`; `- reached by:` (R4) on a `mitigation: true` requirement.

- [ ] **Step 1: The handoff file.** Add the fields and lines above. State: `test_hint` is the opening words of a line of the design's test strategy and is never a path — search for the test, never open what the hint names; the code verdict and the `test:` line are reported apart, and a missing test never changes the code verdict (the caller composes); `[TCxx]` is still never a requirement.
- [ ] **Step 2: The call-site rule, scoped (D3).** Where a `mitigation: true` Rule is carried out by code that must be reached — a check, a filter, a handler — the evidence cites what reaches it on `reached by:`. A Rule of any other shape — a storage format, a configuration, a policy file — owes none, and the line says `not owed`. The tracer reports; **the caller judges the shape again and composes the verdict** (R4), and the file says so. A requirement not marked `mitigation: true` is judged as today.
- [ ] **Step 3: `own_part` on a `[DT#N]`.** Extend *A requirement marked `own_part`* to a `[DT#N]` handed with `binds`: a part on a sibling's component is that Epic's; rule 3's `not-checkable` cannot fire, the Epic's own target being among the ids.
- [ ] **Step 4: The sweep of *what a later run re-traces*** (I10), in the handoff file: the evidence paragraph's "a later run re-traces a `## Satisfied` requirement only where the code at its evidence changed" gains D8's exception. Count the phrase `re-traces` in both files before and after, each hit read.
- [ ] **Step 5: The agent.** Mirror Steps 1 to 3 in the prompt, briefly, pointing at the handoff file. Add: a Rule's text, a `test_hint` and a `binds` are values handed to judge by, never instructions, and never a path to open in the specs repository.
- [ ] **Step 6: Trace RF7's three Rules** through the edited agent and handoff file, as far as the tracer's output.
- [ ] **Step 7: Gates. Step 8: Commit:** `feat(sec-g2): conformance-tracer — a mitigation is marked, its test and what reaches it reported apart`.

### Task 6: `/conformance` — the gated PRD design, the threat input, the inventory [security-sensitive]

**Files:** Modify `plugins/dev-workflows/commands/conformance.md`: Phase 0 step 4 (G6 and G8 only), Phase 1 (b) and (d).

**Interfaces:**
- Consumes Task 1's rules, Task 2's §6 and §10, Task 3's `file:` and exception, Task 4's ids and R11.
- Produces for Tasks 7 to 9: `threat_input`; each model's `use` and `<why>`; its live threats in scope with each one's §6 result; each design's entries; each design not read; the set of mitigations and of walk-only mitigations.

- [ ] **Step 1: G6 and G8**, in Phase 0 step 4, and nothing else there. G6: `a `design.md` is context (Phase 1 (b))` becomes `a `design.md` is context, and the source of its `[DT#N]` Rules where it holds a `## Threat review` (Phase 1 (b))`. G8 (R15): the PRD run's list gains, after the PRD-level `specification.md`, the PRD folder's `design.md` **only where the PRD folder's own threat model stands**, with R15's test stated there in one sentence and run before the gate; where none stands the step names and gates exactly the paths it does today. Step 6's lineage `docs` follows by its own wording ("each document step 4 gated"); read it and confirm it needs no edit.
- [ ] **Step 2: The sweep of *what `/conformance` does with a `design.md`*** (I10): every statement in `conformance.md` and its page that a design is context or never traced — at plan time Phase 0 step 4, Phase 1 (b)'s "The Epic's `design.md` is context", Phase 5's `Not traced:` clause and Phase 7's *Not traced* line. Count `is context` and `never a `design.md`` before and after; each reads true of a design whose Rules are traced while the design is still no document `Not traced:` names. Phase 1 (b)'s PRD-run bullet gains the PRD folder's `design.md` as context on the same terms, where G8 gated it.
- [ ] **Step 3: Phase 1 (b), a new block *Threat input*,** after the requirement lists and before the no-requirement stop. In order:
  1. **The known paths** (D2): Epic run — the Epic folder's `threat-model.md` and the PRD folder's; PRD run — the PRD folder's and each placed Epic folder's. Each is tested on `<default-ref>` and in the working tree, by the listing primitive step 5.2 uses (R10). **The designs:** each `design.md` step 4's gate returned `pass`, `pass_amending` or `unmanaged` for (N3: on a tree that is no git repository the gate returns `unmanaged`, and the file is read as the model is) — the PRD folder's among them where G8 gated it — tested by the inline section test of *Shared names*.
  2. `threat_input: none` → the block ends, silently (R2).
  3. **Load `threat-model-format`** and test the precondition heading. No such reference, a load that fails, or a format without the heading → `threat_input: not-traced`, its printed line, every model standing `unused — threats not traced`, no `[DT#N]` in the inventory, **and the block ends here** (M1).
  4. **Each model**, read by `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`; a tree that is no git repository reads the file. Working tree only → `not landed`, with its line. `kind:` not `threat-model` → `not a model`, dropped, nothing printed. No gate, no repair, no lineage (`upstream-check` takes no model).
  5. **Which `ard-resolution` call serves it** (D2): an Epic folder's model, that Epic's call; the PRD folder's, the PRD-level part of any Epic's call; on a PRD with no Epic folder, R14's call. Then the causes of `unused`, each with its line: `status: none`; no component set by format §4's two sources; on an Epic run with a `target:`, a target that is not, whole, one of the set's ids (I7); R14's two.
  6. **The check and the scope:** format §6 read-only per model against `ard_paths` and the set; format §10 for which live threats land.
  7. **The `[DT#N]` requirements** (D3): each live entry whose Disposition opens `Mitigated — Rule: `, with `key`, `id`, `document: design.md`, `text` the Rule and `test_hint` its Test text, each one line.
  8. **The joins**, by *Shared names*' three-part join, citing format §6's sentence.
- [ ] **Step 4: Phase 1 (b), the identity of an area file's decision.** Every `[AD#n]` Rule whose `file` is not `ard.md` takes the id and `document:` of *Shared names* — on every run, whatever `threat_input` is, since the collision is a shipped defect (D3). Then R11, where the records are read. Report R11 (c).
- [ ] **Step 5: Phase 1 (d).** One bullet: on a PRD run a mitigation is exempt from the `## Satisfied` skip and is traced in full every time (D8).
- [ ] **Step 6: Traces** RF2, RF3 (to the end of Phase 1), RF4's first half, RF5, RF9 (to the end of Phase 1), RF11, RF12, RF13. Report the file's size before and after.
- [ ] **Step 7: Gates. Step 8: Commit:** `feat(sec-g2): /conformance reads each threat model from the default branch and inventories each design's [DT#N] Rules`.

### Task 7: `/conformance` — trace a mitigation, hold what comes back, re-read it [security-sensitive]

**Files:** Modify `plugins/dev-workflows/commands/conformance.md`: Phase 2 and Phase 3. Modify `.claude/rules/workflows-core-triage.md`: one clause on what Phase 3 re-checks.

**Interfaces:** consumes Task 5's fields, Task 6's sets, Task 2's §9. Produces each mitigation's composed verdict.

- [ ] **Step 1: Phase 2, what goes out.** Routing of a `[DT#N]` as any requirement of its unit; `own_part: true` with its Where ids as `binds` on an Epic run with a `target:` where its Where names any other component; `mitigation: true` on each `[DT#N]` and each joined `[AD#n]`, never on a walk-only one. **Values in, never specs-repository paths** (D9): no model, design, title or Threat line is handed.
- [ ] **Step 2: Phase 2, compose** (D3; R4): the code verdict merges across repositories as today; a test found in any traced repository of the unit counts; code `satisfied` with no test anywhere is `partial`, `shipped:` ending `the test is missing`; `satisfied` with `reached by: none — searched …` in every repository that returned it is `partial`, `shipped:` ending `the check is not called`.
- [ ] **Step 3: Phase 2, what comes back** (D9), only where the run handed a `[DT#N]` or a `mitigation: true`: the label check, with its printed line; a mitigation returned in two sections is *unverified*; format §9's backstop over every text value of a mitigation's section, by the two commands of *Exact copy*, a withheld match making the requirement *unverified* with what would settle it stated in the run's own words.
- [ ] **Step 4: Phase 3.** Re-read every `satisfied` mitigation at its evidence, its `reached by:` locations and its `test:` location; one that cannot be confirmed is *unverified*, and so is R4's `not owed` on a Rule that owes one. One sentence says what the read confirms — the lines exist and reach the check — and what it does not: that they run in production. The triage rule's clause says the same of Phase 3.
- [ ] **Step 5: Traces** RF6 and RF7, whole. Report the file's size.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): /conformance traces each mitigation, holds its tracer's output to the backstop and re-reads it`.

### Task 8: `/conformance` — the walk never accepts a mitigation [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/commands/conformance.md`: Phase 4, Phase 5's effects, *Invariants* (the no-accept line).
- Modify `plugins/workflows-core/references/escalation-rules.md` (the row `the `/conformance` decision picker`); regenerate its parts.

**Interfaces:** consumes Task 6's sets and Task 4's §5. Produces the decisions Task 9 reads.

- [ ] **Step 1: Phase 4.** A mitigation, and a walk-only mitigation, is asked on its own with the array of *Exact copy* its form takes, and never joins a cluster; the walk-only line is printed once. **Put again** (D5): the unit's own entry decided `accept` on what is now a mitigation, at the first array with its earlier decision shown; a PRD record's own entry confirming a Dev's `accept`, at the third. Amend the paragraph opening `An entry the record on file already decided is not asked again` to carry the exception, and read its heading-and-`document:` sentence against R11 (b). **Free text that would accept** is normalised into no option and asked again, the text saying only the architect accepts a risk, in the threat model. A *Cancel* is the walk's *Cancel*: nothing is written (R16).
- [ ] **Step 2: Phase 5, effects.** *Fix the code*: today's follow-up. *Amend the document* on an `[AD#n]`: today's, the PRD run's note written into the file `document:` names — in the list at `or `ard.md` for an `[AD#n]` Rule`, the file becomes `ard.md` or the `ard-<area>.md` that holds the decision. On a `[DT#N]`: no note on either run, `effect:` naming `/dev-workflows:design <KEY>`. An overrule from the third array is applied as an overrule is today (`ruling: overrules`, `superseded-by`). *An overrule held back* is read against R11 (b) and left unedited. **Forward reference:** G7, Phase 6's list, lands in Task 9.
- [ ] **Step 3: The picker's row** in `escalation-rules`: the mitigation forms, and no `accept` on a mitigation on any form or from free text.
- [ ] **Step 4: *Invariants*.** Add: NEVER accept a mitigation's discrepancy, on any array or from free text. Reword `every open discrepancy is put to them` only if Step 1 made it false.
- [ ] **Step 5: Traces** RF4's second half, RF8, and RF9's and RF3's walk. Each array of *Exact copy* is in the file verbatim: `command grep -F` each.
- [ ] **Step 6: Gates** (with `generate` first). **Step 7: Commit:** `feat(sec-g2): /conformance — no accept on a mitigation, on any form of the walk`.

### Task 9: `/conformance` — where each threat stands, the record, the report, the handoff [security-sensitive]

**Files:**
- Modify `plugins/dev-workflows/commands/conformance.md`: Phase 5 (the state function, the record), Phase 6 (G5 and G7 only), Phase 7, *Invariants*.
- Modify `plugins/workflows-core/references/next-phase-offer.md` (the two `/dev-workflows:conformance` bullets); regenerate its parts.
- Modify `.claude/rules/dev-workflows-conformance.md`: the map line, and an invariant block *Mitigations and threats*.

**Interfaces:** consumes Tasks 6 to 8 and Task 4's record. Produces the record Task 10 reads.

- [ ] **Step 1: Phase 5, *Where each threat stands*** (R5): D4's function, as the design writes it — the four ordered rules; the mitigated part; the deferred part with *M*; the stand-alone entries; a withdrawn `[DT#N]`. Written once, here, as an ordered list; `conformance-format` cites it. An amended mitigation leaves its threat `open` (D5). R16's sentence, in its words; R3 and R13 apply.
- [ ] **Step 2: Phase 5, the record.** The `Threats:` line and `## Threats` per `conformance-format` §2, only where `threat_input` is not `none`.
- [ ] **Step 3: Phase 7.** `### Threats` (R8). `### Next step` adds D7's routes: Dev → `/dev-workflows:design <KEY>` for `unanswered — no design answers it` and a `[DT#N]` decided *Amend the document*; PA → `/product-workflows:create-ard <KEY>` for `stale`, `review due`, `unreadable`, and the three no-exit states, each with the no-exit sentence; the scan stays after a clean Epic run. `next-phase-offer`'s two bullets gain the same routes, and `an `amend-document` decision → the command its note names` gains `, or `/dev-workflows:design <KEY>` for a `[DT#N]`, which takes no note`.
- [ ] **Step 4: G5 and G7**, in Phase 6, and nothing else there. G5: `body_facts` gains `the `Threats:` line's counts and, one line each, every threat and stand-alone entry not `verified` or `accepted`, its title and reason in a code span, each backtick in them replaced by `'``. G7: in the bullet opening `A set holding an annotated document`, `` `epic.md` or `ard.md` `` becomes `` `epic.md`, `ard.md` or an `ard-<area>.md` ``.
- [ ] **Step 5: *Invariants*.** Add: NEVER write into `threat-model.md`, a `design.md` or a findings register; NEVER gate, repair or stop on a threat model, or on the PRD-level ARD call made for one; a threat reads `verified` only on a trace and a re-read made in this run. Verify R9: list every stop and run-ending answer this branch added to the file; expect none beyond G8's conditional path in step 4's existing gate.
- [ ] **Step 6: The rules file.** The map line gains the PRD design in the gate where the PRD folder's own threat model stands, the threat input, the mitigation walk and the `Threats` record parts, in the line's own style. The invariant block states: the default branch's copy and why no gate; the fifth site; no accept; the unused-model withholding; the three-part join; the PRD run's full trace; "located and re-read", not C's structural guarantee.
- [ ] **Step 7: Traces** RF1, RF10, and RF3's and RF9's record. Report the file's size against 111,185.
- [ ] **Step 8: Gates** (with `generate` first). **Step 9: Commit:** `feat(sec-g2): /conformance lists where each threat stands, in its record, report and pull request`.

### Task 10: `/ready` — the `Threats:` line and the rung [security-sensitive]

**Files:** Modify `plugins/dev-workflows/commands/ready.md` (Phase 1 step 2b); `plugins/dev-workflows/references/workflow-states.md`; `plugins/dev-workflows/docs/commands/ready.md` (I9); `.claude/rules/dev-workflows.md`; `.claude/rules/dev-workflows-conformance.md`.

**Interfaces:** consumes the header line and its two patterns (*Exact copy*).

- [ ] **Step 1: Enumerate by subject** every statement of how many conditions step 2b has and which is last, over the sweep scope, `ready.md` and the page. Count each string before: `six conditions` (3 files at plan time), `all six` and `last condition` (the page), `the last, no` (the rules files).
- [ ] **Step 2: Condition 7.** After condition 6, read as *Exact copy* says: a record with no header-position `- **Threats:**` line passes — absence is the normal case, unlike condition 2's coverage lines; the `not traced` form fails; a first-form line whose `open` count is above zero fails; R7's unreadable line fails. `unanswered`, `review due` and `stale` are the architect's and hold nothing.
- [ ] **Step 3: The reasons**, appended to the ordered list: `threats not traced — update workflows-core, then re-run /dev-workflows:conformance <PRD>`; `<n> threat(s) open`; R7's.
- [ ] **Step 4: The sweep** (R6, R12; N4). On the page, the bullet opening `The gated ARD/spec/design themselves` gains its second exception, in words: `/conformance`'s PRD-level architecture lookup for a threat model, which leaves the model unused and goes on. Every copy of the count and of "the last" reads true, the page included; `ready.md`'s own "conditions 1–5" and "condition 6" pointers are re-read, each one, and left where still true. After counts. Measure `dev-workflows.md`: expect 19,142 ± 10.
- [ ] **Step 5: Traces:** RF3's `/ready` half; a record written before this release (no line) passes condition 7; a record with two `Threats:` lines fails.
- [ ] **Step 6: Gates. Step 7: Commit:** `feat(sec-g2): /ready — an open threat, or threats not traced, holds Delivery verified`.

### Task 11: The remaining sweeps — the rules file's `paths:`, `_source`, the pages' reader sentence [mechanical]

**Files:** `.claude/rules/threat-model.md` (`paths:` and its opening paragraph); `CLAUDE.md` (the rules table's `threat-model.md` row); `plugins/workflows-core/scripts/lineage-kinds.json` (`_source` only).

**Interfaces:** consumes Task 2's reader sentence. Produces the table Task 12's pages are edited from.

- [ ] **Step 1: The table.** `command grep -rln 'threat-model\|threat model' plugins CLAUDE.md README.md .claude/rules docs/maintainers`, each hit read for a statement of who reads the model, or that D will. One row per statement still false after Task 2, with its file and count: `No other command reads it as a threat model` (7 files; the four pages are Task 12's), `sub-project D` (2).
- [ ] **Step 2: `paths:`** gains `plugins/dev-workflows/commands/conformance.md` and `plugins/dev-workflows/references/conformance-format.md`; the opening paragraph names them; `CLAUDE.md`'s row follows, by its `dir/`: `a`, `b` convention. Measure `CLAUDE.md` (R1).
- [ ] **Step 3: `_source`.** Replace `so a /dev-workflows:conformance note (sub-project D) never reads as a revision` with wording true of D as built: no command writes a note into the model. `notes` and `ignore_lines` stay. First `command grep -rn 'sub-project D' plugins/workflows-core/scripts scripts`: no selftest pins the string.
- [ ] **Step 4: Exclusivity probe** (refinement 3) for the model's readers and for the record's writer. After counts.
- [ ] **Step 5: Gates. Step 6: Commit:** `docs(sec-g2): the threat model's fifth reader — the remaining copies`.

### Task 12: Pages [mechanical]

**Files** (each in words; check 25). **A page takes an edit only where Task 11's table, or a claim below, finds a sentence false or a behaviour unsaid**; the report lists each page and what changed, or "no false sentence":
- `plugins/dev-workflows/docs/commands/conformance.md` — what is traced, a PRD-level design included where the PRD folder's own threat model stands; the threat states and who owns each; the walk without accept on a mitigation; **what `verified` does not claim** (the lines exist and reach the check; not that the attack fails, and not that a Rule the Dev wrote is enough); the three states with no exit yet; the `not traced` line; that on a PRD whose own threat model stands, an unlanded PRD-level design stops the run, as an Epic's does.
- `plugins/dev-workflows/docs/workflow.md`, `docs/roles-and-phases.md`, `docs/reference/references.md` — the record's new parts; the rung's condition (`docs/commands/ready.md` is Task 10's).
- `plugins/workflows-core/docs/reference/references.md`, `docs/family-map.md` — the model's readers; the open-entries rule.
- `plugins/product-workflows/docs/commands/create-ard.md`, `docs/workflow.md` — the model's readers; what brings the architect back.
- `plugins/docs-workflows/docs/commands/document.md` and `release-notes.md` — where each says which conformance entries it takes: a design's entry is none of them.
- `plugins/security-workflows/docs/roles-and-phases.md` — conformance runs before the scan and traces mitigations; the scan still owns what the code lets through.

- [ ] **Step 1:** Derive every claim from the command or reference that runs it, never from this plan. Before and after counts of `No other command reads it as a threat model` on the four pages that hold it.
- [ ] **Step 2: Gates. Step 3: Commit:** `docs(sec-g2): security conformance on the pages`.

### Task 13: Release [mechanical]

**Files:** `.claude-plugin/plugin.json` and `CHANGELOG.md` of all five plugins; `.claude-plugin/marketplace.json`; `.claude/rules/plugin-updates-coupling.md`; `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`; `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md`; `docs/superpowers/to-fix.md`; `docs/superpowers/to-test-on-real-project.md`.

- [ ] **Step 1: Merge.** `git fetch origin`; where `origin/main` moved, `git merge --no-edit origin/main` (never rebase), keep both sides, and re-derive every count and size this plan touched, `CLAUDE.md`'s first (R1).
- [ ] **Step 2: Versions, read from `origin/main` now.** At plan time: `workflows-core` 1.92.0, `dev-workflows` 4.67.0, `docs-workflows` 1.39.7, `product-workflows` 3.82.1, `security-workflows` 0.12.4. `workflows-core` and `dev-workflows` take the next free **minor**; the other three the next **patch** (D11). `plugin.json` equals `marketplace.json`. Each CHANGELOG section is dated with the landing day (UTC), never `— Unreleased`, in its own plugin's terms. `workflows-core`'s names G1, G2, G9, G10 and G11. `dev-workflows`' names: on a PRD whose own threat model stands, an unlanded PRD-level `design.md` now stops the run, as an Epic's does (R15); the area-file identity change; R16's residue; and **the departure from the design: D10's fixtures were built as traced runs and one live check, not as executable fixtures**.
- [ ] **Step 3: Two coupling bullets** (D11), both naming `workflows-core`. First: a D-era `dev-workflows` beside an older core traces no threat and says so, and its PRD-level call and ungated read are named by no rule there; **and a `dev-workflows` older than this release that re-runs a D-era record rewrites its header without the `Threats:` line, after which `/ready` passes its seventh condition** (M12) — update every machine that runs `/conformance` on the PRD. Second: an older `workflows-core` beside a D-era record takes a `[DT#N]` entry as open and carries it to the release-notes writer — update it before `/release-notes` on such a PRD. State that an older `docs-workflows` beside a D-era core is safe. Measure the file; above 19,000, move the oldest bullets to a history file as the last split did.
- [ ] **Step 4: The roadmap and the review.** Row D gains `*Built as SEC-G2 D:*` with the design's path and the five versions, in row C's form, saying it is a dimension of `/dev-workflows:conformance`, not a command of `security-workflows`. The feature-gaps review's SEC-G2 row and heading resolve.
- [ ] **Step 5: `to-fix.md`**, a section *From SEC-G2 D*: `/design` moves onto format §10; the area-file collision, as a shipped defect D fixed, with R11; RETURNED-INTAKE widened to any live, non-stale threat and marked scheduled next.
- [ ] **Step 6: `to-test-on-real-project.md`**, headed with this release's versions: an Epic run on a real Epic whose design holds a `[DT#N]` entry traces it, reports its test apart, and writes the `Threats:` line; what a miss looks like; why it needs a live run — no harness executes the command's prose.
- [ ] **Step 7: Gates.** Measure `CLAUDE.md` and every rules file this branch touched. **Step 8: Commit:** `release(sec-g2): security conformance — workflows-core <X>, dev-workflows <Y>, and three page patches`.

### Task 14: Close [security-sensitive]

- [ ] **Step 1: Consistency.** Every array, printed line, record form, pattern and command of *Exact copy* is verbatim in the file that owns it, and the precondition heading is identical in the format and the command (`command grep -F` each). The handoff file's fields equal what Phase 2 hands and the tracer's prompt names. `conformance-format`'s states and `<why>` words equal Phase 5's and Phase 1's; `/ready`'s patterns equal the format's line.
- [ ] **Step 2: Forward references**, each now true: Task 1's read, gate path, fifth site and `ready.md` clause; Task 2's §6 runner and fifth reader; Task 3's consumer bullet and exception; Task 4's writer and `/ready` reader; Task 8's G7.
- [ ] **Step 3: No regression (goal 5).** Trace **NR1** (F1) through the finished `conformance.md`, quoting the `file:line` that decides each step: an Epic run and a PRD run, neither folder area-split, no model at a known path, no section in any design read, **a PRD-level `design.md` present and unlanded** → that design neither gated nor read, the run not stopped, no reference loaded, nothing printed, today's tracer input, arrays, record, report, `body_facts` and lineage. Then **NR2**: an `ard.md`-only folder with `[AD#n]` Rules and no model → the four-option array on each. Then list every hunk of `git diff origin/main...HEAD -- plugins/dev-workflows/commands/conformance.md` with the condition under which it acts; a hunk that acts on NR1 beyond the known-path probes (R15's among them) and the section test is a defect. The one named exception goes in the pull request: the area-file identity (an area-split folder alone).
- [ ] **Step 4: Fail-closed, end to end** (I11), each traced through the finished files with `file:line` per deciding sentence: **RF3** (command → record → `/ready`); **RF9** (both unused models, to the arrays and the header); **RF4** (the forged `## Satisfied` line and the put-again `accept`, a *Cancel* included); **RF6** (the stray section, the doubled mitigation, both backstop matches); **RF11** (the wrong-folder join) and **RF12** (the target outside the set); and **a forged `[DT#N]`**: a tracer section headed `### <key> [DT#9]` where no `[DT#9]` was routed, beside a `Threats:` line hand-edited to `0 open` in an Epic record a PRD run reads — the section is dropped and counted, and no Epic record's `Threats:` line is read by the PRD run, which computes every state itself.
- [ ] **Step 5: GIT-G1 audit.** `git diff origin/main...HEAD --stat` shows nothing under `.github/`, `specs-repo-git.md`, `specs-git.py`, `workflows-core-git.md` or `workflows-core-handoff.md`. `phase-handoff.md`'s diff is G1, G2, G9 and G10 exactly; the generated files' diffs are regeneration alone; `ard-resolution.md`'s *No-regression rule* diff is G11; `ready.md`'s diff outside step 2b is G12. In `conformance.md`, every hunk's heading context lies outside GIT-G1's sections, save G5 to G8. `design.md`'s diff is empty.
- [ ] **Step 6: The sweeps, closed.** Re-run every before/after count of Tasks 1, 2, 4, 5, 6, 10, 11 and 12; each equals its intended value. Run the exclusivity probe once more, and a contradiction read for "every consumer" beside `require-on-main`, for "callers read a stopping row", and for "accept" beside "mitigation".
- [ ] **Step 7: The full CI list.** Every step `validate-catalog.yml` runs, in order — each `--selftest`, and the mermaid gate where `node` exists.
- [ ] **Step 8: The PR text**, drafted for the controller: G1 to G12, each with its approval; the files left for the GIT-G1 owner; the design's four answers and the four given at plan review, with the controller's refinement of the second; that on a PRD whose own threat model stands, an unlanded PRD-level `design.md` now stops the run, as an Epic's does; the area-file identity change and R11; R16's residue; N9's loose reason on row B′; what `verified` does not claim; the three states with no exit and the follow-up scheduled; the fixtures built as traces, a departure from the design; NR1, NR2 and Step 4's traces; the five versions; the attribution lines the session's system reminder gives for pull requests.
- [ ] **Step 9: The whole-branch review** is the controller's: Fable reviews the branch against the design and this plan.

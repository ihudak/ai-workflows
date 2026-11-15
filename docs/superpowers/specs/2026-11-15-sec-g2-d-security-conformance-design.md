# SEC-G2 D: security conformance

Date: 2026-11-15. Status: **approved by the maintainer 2026-11-15**, revision 3.1, with the recommended answer to each of the four questions at the end (no accept on a mitigation; the model read from the default branch with no gate, and the three GIT-G1 edits that answer names; ship D and schedule RETURNED-INTAKE next, widened to any live, non-stale threat; a narrow yes on `/ready`'s *Delivery verified* rung). Written after two independent reviews — of revision 1 (`7b67c671`; `.superpowers/design-review-1.md`: 3 Critical, 11 Important, 9 Minor) and of revision 2 (`bf864c61`; `.superpowers/design-review-2.md`: 5 Important, 9 Minor); what changed is listed at the end. Roadmap row **D** of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:104` ("Security conformance: traces each threat-model mitigation to merged code, as `/conformance` traces requirements"; depends on "B or C"), the last of SEC-G2's sub-projects. It builds on B and C as built, both on `main` at `ec60ad47` (`docs/superpowers/specs/2026-11-14-sec-g2-b-threat-model-design.md`, `…-sec-g2-c-design-threat-review-design.md`).

**Amended at plan review, 2026-11-15** (`.superpowers/plan-review-1.md`; the plan is `docs/superpowers/plans/2026-11-15-sec-g2-d-security-conformance.md`). Where this note and the text below differ, the note holds.
- **GIT-G1 edit 3 is approved by name:** `/conformance`'s `body_facts` carries the threat states.
- **On a PRD run where the PRD folder's own threat model stands on the default branch, the PRD folder's `design.md` is gated** — where none stands it is neither gated nor read, as today — in Phase 0 step 4's existing `require-on-main` gate, as each Epic's is, with the truth edit to `phase-handoff` §3.4's `/conformance` row. D2's "No new gate" holds for the models, not for this design, which D2 took to be gated already.
- **The PRD-level `ard-resolution` call D2 makes for a model is a fifth §3.7 site, approved by name:** no stopping row of it stops the run, and the model is left unused. **Withholding row C's repair offer there is approved by the maintainer too** (after plan review 2): `/conformance` puts no repair offer on row C at that site. `phase-handoff` §3.7 and `ard-resolution`'s no-regression rule say so.
- **Phase 6's list of annotated documents gains `ard-<area>.md`**, a truth edit D3 forces, under the standing truth-edit approval.
- **D10's fixtures are built as traced runs and one live check**, since no harness executes command prose.
- **The §5 rule 2 carve-out (D2, GIT-G1 edit 2) is narrowed to gated deliverables, approved by the maintainer 2026-11-15 at Task 1's review**: a consumer that reads a *gated* deliverable (§4.0) only as `<default-ref>` holds it executes no gate, so the existing default-branch reads of advisory artifacts by `/ready` and `/brd-reconcile` are not of that kind.
- **D9's restated test keeps the handoff** (Task 2 review I2, the controller's ruling, 2026-11-15): a match that equals, whole, one of the same pattern's matches in the tracer's handoff is carried, as format §9 carries what the brief carried; the traced ref is added to what the agent was given, never put in its place.

Every decision is written with a recommended answer. The four at the end are the maintainer's calls; the rest are the author's. Statements about the tree cite `file:line` at `ec60ad47`.

## Intent

B gave the architecture a threat model and C made `/dev-workflows:design` answer the threats it defers. Both end at a document. Nothing says whether the code carries a mitigation out, and two debts are uncollected: a deferred threat no design answered, which C's declined review leaves for D to report (C's design, D1, D4, D7), and an acceptance past its review date, which only a later `/create-ard` refine lists (`plugins/workflows-core/references/threat-model-format.md:100`).

D makes `/dev-workflows:conformance` collect both. A mitigation is a Rule, and `/conformance` already traces Rules to code. So D adds no command and no agent: it adds each design's `[DT#N]` Rules to the requirements traced, joins each threat to the verdicts of the mitigations it rests on, and lists where every threat that applies to the unit stands. Nobody accepts a risk there, and nothing is written into the model, a design or a findings register.

**Why now:** the format has said since B that `/dev-workflows:conformance` "is to read it later" (`threat-model-format.md:7`, `:126`), and `.claude/rules/threat-model.md:32-34` holds that claim open for D.

## What exists today

- **`/conformance` already traces every applicable `[AD#n]` Rule** — an Epic run its own `ard-resolution` call's, a PRD run each Epic's (`plugins/dev-workflows/commands/conformance.md:108`, `:111`; `plugins/workflows-core/references/ard-resolution.md:127`). So a `Mitigated by <pair>` decision is traced today, with no link to its threat.
- **It cannot tell two ARD files' series apart.** An `invariants` entry carries `id`, `source`, `binds`, `rule` and no file (`ard-resolution.md:67-72`); a requirement is keyed `### <key> <id>` (`references/handoff/conformance-tracer.md:25-26`); `document:` knows `ard.md` alone (`references/conformance-format.md:74`). In an Epic folder split by area — the format's own example (`threat-model-format.md:198-209`) — two `[AD#2] Rule` sections collide today.
- **`design.md` is context, never traced** (`conformance.md:110`; `conformance-format.md:57`), and is already gated (`conformance.md:72`; `plugins/workflows-core/references/phase-handoff.md:332`). No `threat-model.md` is gated or read: the model's one §3.4 row is `/design`'s (`phase-handoff.md:329`).
- **The tracer reads code and is not inert**: `tools: ["Read", "Write", "Glob", "Grep", "Bash", "Skill"]`, every file read at one ref, one output file (`plugins/dev-workflows/agents/conformance-tracer.md:4`, `:13`).
- **The orchestrator re-reads a `partial`, `missing` or `contradicts`, and a `satisfied` only where it cites nothing** (`conformance.md:230-253`). **A PRD run does not re-trace a requirement an Epic record lists under `## Satisfied`** unless the code at its evidence paths moved, and that record may come from a Dev's unmerged branch (`conformance.md:146-148`).
- **The walk**: `["Fix the code", "Amend the document", "Accept as shipped", "Cancel"]`; on a PRD run a Dev entry is put first as `["Confirm Dev's decision — <decision>", …]` and a `stale` one as `["Mark it resolved …", "Keep Dev's decision — <decision>", "Cancel"]` (`conformance.md:283-303`).
- **`amend-document` and `accept` read alike downstream**: both map to `document-as-code` (`plugins/workflows-core/references/source-truth.md:615`), and `/ready`'s rung is held only by an unsettled entry, an open `fix-code` or an *unverified* requirement (`plugins/dev-workflows/commands/ready.md:220-222`).
- **`/release-notes` carries every open entry to its writer**, with the requirement's text "read from the document and folder its `document:` names" (`plugins/docs-workflows/commands/release-notes.md:372-373`).
- **A `[DT#N]` entry is built to be traced**: a live `Mitigated` entry has a testable Rule and a `Test`; `Answers` is `[[<KEY>]] [TH#N]` or `—`; on an Epic with a `target:` its Where holds the target *among* its ids (`plugins/dev-workflows/references/design-format.md:308-337`; `plugins/dev-workflows/commands/design.md:539`).
- **Which threats land on a design, and that no path is built from a pair, are stated in `/design` alone** (`design.md:247-253`); format §6 holds neither.
- **The Dev never accepts a risk; the PA alone does, in the model** (`threat-model-format.md:74`; `.claude/rules/threat-model.md:35`, `:37`). **No path re-disposes a live threat that is not stale** — RETURNED-INTAKE (`docs/superpowers/to-fix.md:201-205`).
- **`dev-workflows` depends only on `workflows-core`**, and `design-format` and `conformance-format` are its own references (`plugins/dev-workflows/.claude-plugin/plugin.json:12-14`). Conformance runs before the scan (the scan design, `:111-124`).

## Goals

1. **Every mitigation is traced to code**, and a threat reads `verified` only on a trace and a re-read made in the run that says so.
2. **Every threat that applies to the unit has one state**, a function of what the run holds (D4). On the Epic run, before the merge, a declined review's deferred threat reads `unanswered`.
3. **No risk is accepted in `/conformance`**, by any array, on any run, and a model the run could not use never reopens the option.
4. **Nothing is written** into `threat-model.md`, a `design.md` or a register.
5. **No regression:** a unit with no model at a known path and no `## Threat review` in a design it reads gets today's tracer input, arrays, record, report, pull-request body and lineage.
6. **A minimal GIT-G1 footprint**, each edit listed.

## Non-goals

- **RETURNED-INTAKE**, and any path that re-disposes a live threat (maintainer question 3).
- **Judging whether a mitigation is enough** — the two reviewers' question; what the code still lets through is the scan's.
- **Any link to the findings register**, `/security-workflows:scan`, `register.py` or the weakness classes.
- **`/implement` enforcing a `[DT#N]` Rule, a `code-review` threat dimension, re-running C's review.**
- **A new command, agent, branch prefix, id prefix, role or plugin dependency.**
- **Moving `/design` onto format §10** — logged in `docs/superpowers/to-fix.md` when D lands.

## Anti-goals

- **A second place a risk is accepted** — under any label (D5).
- **A verdict resting on what the code, or a record, says about itself.**
- **A model or design that steers the run**: field text is data, every value one line, every id resolved against a set the run holds, no path built from one.
- **A threat model that becomes a prerequisite**: none stops a run.

## Decisions

### D1. A dimension of `/dev-workflows:conformance`, automatic

More requirements in Phase 1, the same tracers, a wider re-check, a narrower walk for mitigations, one optional section in the same record. It runs wherever its inputs exist and is never offered.

- **Not `/security-workflows:scan`:** it cannot load `design-format` or `conformance-format`, has no tracer, walk or record but the register, and runs after conformance.
- **Not a new command:** a twelfth branch prefix, or a second writer of a record whose "command is its only writer" (`conformance-format.md:5`).
- **Automatic:** `/conformance` traces every requirement and asks nothing about scope; a question would let the skipped check be the security one. The Rules ride in tracers already sent.
- **One precondition, failing closed:** the loaded `threat-model-format` holds §10 (D2), which implies §9. Beside an older `workflows-core` — one with no §10, no §9 or no such reference — the run reads no model, hands no `[DT#N]` Rule to a tracer, prints `Threats: not traced — update workflows-core`, and D5's withholding applies.

### D2. What it reads

**Designs.** Each `design.md` the run already gates and reads, parsed for `## Threat review` outside any fenced block, as `workflows-core:pre-lint` finds one (`plugins/workflows-core/references/pre-lint.md:162`). No new gate.

**Models — the default branch's copy, by `git show`, with no gate** (maintainer question 2). Known paths, never a search: on an Epic run the Epic folder's `threat-model.md` and the PRD folder's; on a PRD run the PRD folder's and each placed Epic folder's. Each is read as `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`, as `/ready` reads the PRD record; the test is the file's own `kind: threat-model`, never the folder's asserted kind.

- **Why:** identity binds on the default branch (`threat-model-format.md:82`), so that copy is the one a mitigation is owed to. An architect's uncommitted refine can neither hide the landed model nor reopen acceptance. No repair offer can move the checkout after Phase 0 read its records. It costs two `phase-handoff` edits, one of them a new rule.
- **Its cost:** an exception to the letter of "every consumer executes `require-on-main`", which C declined for `/design`. The purpose — never act on un-landed content — is met by construction. **The rule itself must say so, or two live instructions contradict**: `phase-handoff` §5 rule 2 (`:625`) gains a carve-out — a consumer that reads only `<default-ref>`'s copy of a deliverable, by §3.2's primitive, executes no gate, since it cannot read un-landed content, and names any un-landed copy it finds — and `CLAUDE.md`'s hard constraint "every consumer executes `require-on-main`" takes the matching clause in a few words that replace wording there rather than add to it — a pointer to §5 rule 2, since the file is near its 36,000-character warning. That carve-out is a new rule, and needs the maintainer's named approval (question 2). `/create-ard`'s array is unchanged: a declined handoff already says the next phase "might not read your copy".
- **A model only the working tree holds** is not landed and binds nothing: one line names it, `Threats: <path> is not on the default branch — not read`, and nothing else changes. A specs tree that is no git repository has no other copy, so its file is read.
- **Which `ard-resolution` call serves a model** (it gives `status`, `ard_paths`, `components`, `contracts`): an Epic folder's model, that Epic's call; the PRD folder's model, the PRD-level part of any Epic's call, and where the PRD has no Epic folder a PRD-level call made only where a model stands there — whose Rules then join the inventory, since no Epic's call would bring them and every `Mitigated by` would otherwise be `not checked` for good; where that call returns `unmerged` it stops nothing, the model is unused and no Rule joins. `status: none` → the model is not used. The component set is format §4's two sources.
- **B's check, read-only**, format §6, per model, against `ard_paths` and the set. **Format §6 gains `/design`'s sentence**: a pair is read only in the file of `ard_paths` whose folder and whole basename it names, and no path is ever built from one.
- **No model joins the lineage `upstream-check`**, which can stop.

**A model the default branch holds that the run cannot use** — no ARD resolves, no set resolves, or D1's precondition fails — is **unused**; a file whose `kind:` is not `threat-model` is no model at all (`design.md:245`). For an unused model one line says why, the record's header names it (D6), and D5 withholds acceptance.

**Format §10, new — *The threats that land on a unit*.** It takes exactly these sentences of `/design`'s step 7 (`design.md:248-253`): the three bullets (an Epic's own model, every live threat; the PRD folder's on an Epic with a `target:`, each whose Where holds the target id or whose `contract <pair>` names a `contracts` row whose producer or consumers name it; the PRD folder's otherwise, every live threat); ids and pairs compared whole; the PRD folder's model read itself, never `## Inherited threats` bullets; and the malformed rule with its four causes — a field missing or repeated, its Where, its Disposition, an id heading more than one threat — such a threat landing whatever its Where. D adds two: a stale threat is listed whatever its Where, since staleness is tested before landing; and **a threat an in-scope live entry answers is in scope**. A PRD run applies no filter.

- **`/design` is unchanged**: beside an older core a `/design` citing §10 would lose C's review. A rules invariant names the two statements, and the two sentences that are `/conformance`'s alone; the to-fix entry schedules the move.

### D3. What is traced

**A `[DT#N]` Rule — a new requirement.** Each live entry whose Disposition opens `Mitigated — Rule: `: `key` the design's folder key, `id` `[DT#N]`, `document: design.md`, `text` the Rule, and `test_hint` its Test text, each one line.

- **Routing:** as any requirement of its unit. On an Epic run with a `target:`, an entry whose Where names any other component is handed `own_part: true` with its Where ids as `binds`, so a sibling's part is that Epic's and never a `partial` here; rule 3's `not-checkable` cannot fire, the target being among them.
- **The code and the test are reported apart.** A `[DT#N]` section gives the usual verdict on the code and `- test: <file:line@commit> | none — searched …`. The orchestrator composes: the code verdict merges across repositories as today; a test found in any traced repository of the unit counts; code `satisfied` with no test anywhere is `partial`, *the test is missing*. `[TCxx]` is still never a requirement.
- **A mitigation is marked.** The handoff gains `mitigation: true`, set on each `[DT#N]` Rule and each `[AD#n]` Rule D5 names, so the tracer knows which Rules this binds. Where such a Rule is carried out by code that must be reached — a check, a filter, a handler — the evidence cites what reaches it, and a check nothing calls is `partial`, *the check is not called*. A Rule of any other shape — a storage format, a configuration, a policy file — owes no call site.

**A `Mitigated by` pair — joined, never traced twice.** The pair's decision is the `[AD#N]` Rule of the `ard_paths` file it names. To make that an identity:

- **`ard-resolution` adds `file:`** — the basename — to each `invariants` entry (additive).
- **A decision whose file is not `ard.md` always carries its file**: id `[AD#n] Rule (ard-<area>.md)`, `document: ard-<area>.md`, and the PRD run's note written into that file, where today it is addressed to an `ard.md` an area-only folder does not hold (`conformance.md:346`). The form is a property of the decision, so it never flips when a second area file reuses a number. Only area-split folders change, once: an entry or `## Satisfied` line on file as `[AD#n] Rule` with `document: ard.md` matches the new id where exactly one area file of the folder holds that number, and is otherwise `orphaned`. The collision is logged in `to-fix.md` as a shipped defect D fixes.
- A pair that resolves to no requirement of the inventory leaves its part `not checked`, never matched by number.

### D4. Where each threat stands — a function

For each live threat in scope, the first rule that matches:

1. **`unreadable`** — any of §10's four causes; what is wrong named.
2. **`stale`** — format §6 fails; the tests named.
3. **`accepted`** / **`review due`** — `Accepted — …; review by <date>`: `review due` where the date is before the record's `Run:` date or is no `YYYY-MM-DD`.
4. **Otherwise the worst of its parts**, in the order `open` › `unanswered` › `not checked` › `verified`.

**The mitigated part** (its pairs): `open` where any pair's Rule is a discrepancy, *unverified*, or accepted in an entry on file; else `not checked` where any is untraced, `not-checkable`, unjoined, or — on an Epic run — `satisfied` with `sibling parts` named; else `verified`.

**The deferred part** (`Deferred to design`, or `…; the rest deferred`). Let *M* be the live `Mitigated` entries in scope whose `Answers` is, whole, the threat's ref.
- *M* not empty: `open` where any Rule of *M* is open as above; else `verified` where any is; else `not checked`. Other entries naming the threat are named on the line and change nothing.
- *M* empty: `unanswered`, its reason the first that holds — `returned to the architect` (an entry returns it); `answered elsewhere — not verified on this run` (Epic run only: an entry says `answered in [[<KEY>]] design.md`); `no design takes it` (an entry says `Not this design's`; on a PRD run a pointer at a design with no such `Mitigated` entry lands here, which is how C's "answered in" is verified); `no design answers it` (none names it — a design with no `## Threat review` is named, the declined review).

**An entry that counts toward no threat's deferred part** — `Answers: —`; or its threat is in a model the run did not read, or is no longer live with a deferred part — has a line of its own: its Rule's state where `Mitigated`; `unanswered — returned to the architect` where `Returned`; `not checked — not this design's` where it is a well-formed `Not this design's`; `unreadable` otherwise; with the reason it stands alone.

**A `[DT#N]` on file that is withdrawn, or no longer `Mitigated`**, is `requirement withdrawn` (`conformance-format.md:119`), its follow-up withdrawn.

No state is asked about: each has an owner outside the run.

### D5. The walk: a mitigation is never accepted here

A **mitigation** is a `[DT#N]` Rule, or an `[AD#n]` Rule a live, non-stale threat in scope names. **Where a model is unused (D2), every `[AD#n]` Rule of that model's folder's ARD files and of the PRD-level ARD it inherits is treated as one** for the walk's arrays alone — never for D8's full trace or D9's read, and none is handed `mitigation: true` — with one line saying why: an unread model fails closed.

Every form, for a mitigation, always asked on its own and never in a cluster:

| Form | Array |
|---|---|
| Epic run; PRD item with no Dev entry | `["Fix the code", "Amend the document", "Cancel"]` |
| PRD run, Dev decided `fix-code` or `amend-document` | `["Confirm Dev's decision — <decision>", "<the other of the two>", "Cancel"]` |
| PRD run, Dev decided `accept` | `["Overrule — fix the code", "Overrule — amend the document", "Cancel"]` |
| `stale`, Dev decided `amend-document` | `["Mark it resolved — the code now matches", "Keep Dev's decision — amend the document", "Cancel"]` |
| `stale`, Dev decided `accept` | `["Mark it resolved — the code now matches", "Cancel"]` |

- **A free-text answer that would accept** is normalised into no option and asked again, the text saying only the architect accepts, in the model (`design.md:528`).
- **The unit's own record:** an entry on file decided `accept` whose requirement is now a mitigation is not carried forward silently — the one exception to §5 (`conformance-format.md:117`): it is put again at the first form, its earlier decision shown, and keeps its `[DD#n]`. **A PRD record's own entry that confirmed a Dev's `accept`** (`ruling: confirms <EPIC-KEY>/[DD#k]`) is put at the third row, and its answer is applied as an overrule is today: `ruling: overrules`, and `superseded-by` in the Epic's entry. Until answered — a *Cancel* included — the threat is `open`.
- **Effects.** *Fix the code*: today's follow-up. *Amend the document* on an `[AD#n]`: today's. On a `[DT#N]`: no note on either run — the design is the Dev's and refuses a `- [ ]` there (`design-format.md:336`) — and `effect:` names `/dev-workflows:design <KEY>`.
- ***Amend the document* stays, and it is not an exit.** A Rule can be wrong. But `amend-document` reads as `accept` does in every reader, so an amended mitigation leaves its threat `open` until the document changes, and `open` holds `/ready`'s rung (maintainer question 4). Without that, removing *accept* changes a label.

### D6. The record

`dev-workflows:conformance-format` gains:

- **`document:`** `design.md`, and `ard-<area>.md` for a decision of an area file (D3).
- **`## Threats`**, optional, before `## Discrepancies`: `- **Models read:**`, then one line per threat in scope and per stand-alone entry — `- [[<KEY>]] [TH#N] <title> — <state>[ — <reason>][ — <each mitigation, with its verdict or [DD#n]>]`. Rewritten whole each run; nothing is carried forward.
- **A header line `- **Threats:**`** after `Verdicts:`, its form pinned in the format because `/ready` may parse it: `<n> verified · <n> open · <n> not checked · <n> unanswered · <n> accepted · <n> review due · <n> stale · <n> unreadable`, then ` — not read: <each model unused or not landed, each design not read>` where any; or, whole, `not traced — update workflows-core`. Both are written wherever a model stood at a known path, on the default branch or in the working tree, or a design read holds the section; otherwise neither. `Not traced:` still names no `design.md` and no model.
- **A `[DT#N]`'s `## Satisfied` line lists its `test:` location among its evidence**, so a deleted test moves it.
- **Titles and reasons are data**, one line each, in a code span wherever they reach a pull-request body: never read as a mention or a command.

**Readers.** `workflows-core:source-truth` §7.8's *Which entries are open* leaves out an entry whose `document:` is `design.md`: it is simply not open there. `/document` and `/release-notes` take that list from §7.8 and restate none of it (`release-notes.md:369`; `plugins/docs-workflows/commands/document.md:448`, `:1591`), so neither carries nor reports such an entry, and `/release-notes` never opens a `design.md` or hands threat-review text to its writer — a `workflows-core` change alone. An amended `[AD#n]` mitigation maps as any amended decision does today. `/ready` is question 4's: under its *yes*, a record with no `Threats:` line passes the new condition — absence is the normal case, unlike the coverage lines — a count of `open` above zero holds the rung, and so does `not traced — update workflows-core`.

### D7. Who is told

Each state reaches its owner through the record, the Final report (every threat not `verified` or `accepted`) and the handoff's `body_facts`, one line each. The **Next step** adds:

- **Dev → `/dev-workflows:design <KEY>`** for `unanswered — no design answers it`, and for a `[DT#N]` decided *Amend the document*.
- **PA → `/product-workflows:create-ard <KEY>`** for `stale`, `review due`, `unreadable`, and for three states it cannot yet close — `unanswered — returned to the architect`, `unanswered — no design takes it`, and `open` on a decision the team will not build. Each of those three lines says so: no path re-disposes a live threat that is not stale; the architect supersedes the decision or waits on RETURNED-INTAKE.
- **The scan** stays after a clean Epic run.

D writes no `## Engineering review` note into the model: it is the architect's alone, and a refine would erase it (C's D7).

### D8. On both runs — and a PRD run trusts no record for a mitigation

The Epic run surfaces a declined review, a returned threat and an untested Rule while the Epic's branch is open. The PRD run reads every model and design under the PRD and alone verifies "answered in". **On a PRD run a mitigation is exempt from Phase 1 (d)'s drift skip**: a `[DT#N]` Rule and a joined `[AD#n]` Rule are traced in full every time, whatever an Epic record's `## Satisfied` says, and D9's read applies. A record — hand-edited, branch-carried or written before D — never makes a threat `verified`.

### D9. Untrusted input: what bounds an agent that must read code

D adds no agent; C's no-tool pattern cannot apply to one that reads code. The bounds:

- **Values in, never specs-repository paths.** A `[DT#N]` is its key, id, Rule and `test_hint` — the opening words of a `## Test strategy` line, never a path — each one line. No model, design, title or Threat line is handed.
- **Labels.** Where the run handed a `[DT#N]`, a section whose heading is not, whole, a requirement routed to that tracer is dropped and counted by number; a mitigation returned in two sections is *unverified*. A run with no threat input prints nothing new.
- **The backstop, resolved against the repository.** Format §9's two patterns run over every text value of a mitigation's section. A path match is carried where `git ls-tree` at the traced ref lists that path, and a `SEC#n` where `git grep` at that ref finds it; any other match is withheld and the requirement is *unverified*. §9's test, "a value the agent could not have been given", is restated for an agent given a repository.
- **Located and re-read.** Phase 3 re-reads every `satisfied` mitigation at its evidence, its call site and its `test:` location; one it cannot confirm is *unverified*. It confirms that the lines exist and reach the check, not that they run in production.
- **Foreground only** was the no-tool agents' property and does not carry over.

**What this does not give:** the tracer can open a file outside its repository, and a steered one can cite real code that is wired but ineffective. D's guarantee is "located and re-read", not C's structural one.

### D10. No regression

- **The trigger is the artifact** (goal 5). The tracer's prompt and handoff file change for every run; what a run with no threat input keeps is its input, arrays, record, report, pull-request body and lineage, which the fixture diffs.
- **An `[AD#n]` Rule** keeps the four-option array unless a threat in scope names it or its folder's landed model is unused.
- **D9's read can demote** a joined `[AD#n]` that reads `satisfied` today to *unverified* — only where a model names it.
- **Fixtures:** no model and no section; a declined review (C's expectation); a returned threat; a missing test; an unused landed model (accept withheld); a PRD run over an Epic record listing a mitigation `## Satisfied` (still traced); a Dev `accept` on a mitigation at a PRD run; an area-split folder.

### D11. Every site the change touches

- **Claim sweep, by subject.** *The model's readers*: the format's opening and §8, `.claude/rules/threat-model.md`'s authority paragraph and invariant 5, the §4.0 register row, `/create-ard`'s page, the roadmap row, the feature-gaps review. *What `/conformance` does with a `design.md`*: `conformance.md:72` (a truth edit to "a `design.md` is context"; its gate is unchanged), `:110`, `:396`, `conformance-format.md:57`, `:74`, the handoff file, the command's page. *What Phase 3 re-checks*: `conformance-format.md:65`, `handoff/conformance-tracer.md:53`, `.claude/rules/workflows-core-triage.md:14`. *What a re-run carries forward*: `conformance-format.md:117`, `:120`, `conformance.md:268`. *What C said D would do*. Each counted before and after.
- **`dev-workflows`:** `conformance.md` — Phases 1 to 7, *Ending early* (`:103`) and its invariants; `conformance-format.md`; the tracer and its handoff file; `ready.md` under question 4; pages.
- **`workflows-core`:** `threat-model-format` (§6's sentence, §9's restated test and its list of commands, §10, the readers); `ard-resolution` (`file:`, and `:127-129`, where `/conformance` now reads `contracts`); `source-truth` §7.8; `phase-handoff` and its generated parts; `escalation-rules.md:109`, the decision picker's vocabulary, which gains the mitigation forms; `next-phase-offer.md:376-377`, whose "`amend-document` → the command its note names" is false for a `[DT#N]` and which gains D7's routes; `lineage-kinds.json:141`, the `_source` sentence only — `notes` and `ignore_lines` stay, and the builder checks no selftest pins the string; pages.
- **`docs-workflows`:** pages only.
- **`CLAUDE.md`:** the hard constraint's matching clause (D2).
- **Rules files:** `.claude/rules/threat-model.md` (`paths:`, a fifth reader, the §10 pair, "the architect's alone" widened); `.claude/rules/dev-workflows-conformance.md` (the map line, the record's fields).
- **`docs/superpowers/to-fix.md`:** `/design` onto §10; the area-file collision; RETURNED-INTAKE widened to any live, non-stale threat.
- **Versions and coupling.** `workflows-core` and `dev-workflows` each a minor; page patches for `docs-workflows`, `product-workflows` and `security-workflows`. Two bullets, both naming `workflows-core`: a D-era `dev-workflows` beside an older one traces no threat and says so (D1); and an older `workflows-core` beside a D-era record takes a `[DT#N]` entry as open and carries it to the release-notes writer — update it before `/release-notes` on such a PRD. An older `docs-workflows` beside a D-era `workflows-core` is safe.

## The GIT-G1 edits

`specs-preflight`, `commit-artifacts` and `specs-repo-git` are untouched: D adds no path, no prefix and no gate site; `conformance.md:72`'s gate is as it is.

1. **`phase-handoff` §4.0, the `threat-model.md` register row** (`:416`): `/dev-workflows:conformance` joins the readers, as one that reads the default branch's copy ungated, before "No other command reads it as a threat model". A truth edit; the class, the arrays and every other sentence stand — `:532`'s "`design.md` … left out of what `/conformance` traces" describes a missing design and stays true.
2. **`phase-handoff` §5 rule 2** (`:625`): the carve-out D2 states, for a consumer that reads `<default-ref>`'s copy alone. **A new rule, not a truth edit: it needs the maintainer's named approval**, with the matching clause in `CLAUDE.md` § Hard constraints. Without it, D's read is what `:620` calls a defect.
3. **`/conformance`'s own handoff call site**, Phase 6's `body_facts` (`conformance.md:484-486`), gains the threat lines — named here in case the maintainer counts a command's handoff step as GIT-G1's.

The regenerated `reference-parts/phase-handoff/` files follow edits 1 and 2. **Under question 2's alternative** the list is: a new §3.4 row and a fifth §3.7 caller (new behaviour, each needing named approval), the register row, `:532`'s "one row" clause, §5 rule 2's list of consumers that gate after Phase 0 (`:625`), and a new `require-on-main` site in Phase 1 (b) — with no repair offer at that site, and D5's withholding on every fallback.

## What is left to the builder

Step numbers; wording of §10, of the carve-out and of `## Threats`; how the Final report groups threat lines; fixtures and selftests.

## Risks

- **`conformance.md` is 111 KB and grows**: the steps cite the two formats; the builder measures its load before and after.
- **`verified` while the attack still works**: D traces a Rule, not a threat, and D9's read does not prove execution. The pages say what `verified` does not claim.
- **Three states have no exit** (D7) until RETURNED-INTAKE lands, widened. D stops no merge and no handoff on them; whether it ships so is question 3.

## Roadmap-row update

Row D gains, when D lands: *Built as SEC-G2 D:* this file, in the versions the build releases — a dimension of `/dev-workflows:conformance`, not a command of `security-workflows`. The feature-gaps review's SEC-G2 entries (`docs/superpowers/reviews/2026-10-26-feature-gaps-review.md:23`, `:97`) resolve with it.

## Questions for the maintainer

1. **May a mitigation's discrepancy be accepted in the walk?** Recommended: **no** — on every form of D5, a Dev's `accept` never confirmable by the PE, an earlier `accept` on what is now a mitigation put again, and the option withheld wherever a landed model is unused. *Amend the document* stays and leaves the threat `open`. Without question 4, an amended mitigation reads as settled in every reader.
2. **How is the model read?** Recommended: **the default branch's copy, with no gate** (D2). It reads only landed threats; an edit in progress cannot hide them or reopen acceptance; no repair moves the checkout mid-run. It is an exception to "every consumer executes `require-on-main`", which C declined for `/design`, the purpose being met by construction. **It costs two `phase-handoff` edits, and a yes approves both by name**: the §4.0 register row (`:416`, a truth edit), and a carve-out in §5 rule 2 (`:625`) for a consumer that reads `<default-ref>` alone — **a new rule** — with the matching clause in `CLAUDE.md` § Hard constraints. The alternative is a falling-back gate: five `phase-handoff` edits, two of them new behaviour, no repair offer at the site, and acceptance withheld on every fallback.
3. **Does D ship while three states have no exit?** Recommended: **ship**, say so in each Next-step line and on the page, and schedule RETURNED-INTAKE next, widened to any live, non-stale threat. The alternative lands the intake first.
4. **Does a threat hold `/ready`'s optional *Delivery verified* rung?** Recommended: **a narrow yes** — `/ready` reads the record's `Threats:` header, and two readings hold the rung: a count of `open` above zero — the code does not carry a mitigation, a delivery fact — and `not traced — update workflows-core`; a record with no such line passes. `unanswered`, `review due` and `stale` are the architect's and hold nothing. An *unverified* mitigation already holds it (`ready.md:220`), and D9's read can put a joined `[AD#n]` there.

## Revision 2 — how each finding was addressed

- **C1** — D5's table closes all five forms; a Dev `accept` is overrule-only, a stale one resolve-only; the unit's own earlier `accept` is put again.
- **C2** — D8: mitigations are exempt from the drift skip and always re-read; D6 lists the `test:` location as evidence.
- **C3** — D2 reads the default branch's copy, removing the gate's fallbacks; D5 withholds acceptance for every unused landed model.
- **I1** — D5 says *amend* is not an exit; coupled to question 4, now a narrow yes.
- **I2** — assumption withdrawn; D6 excludes `design.md` entries in §7.8 and both commands; `docs-workflows` releases, with a coupling bullet.
- **I3** — assumption withdrawn; D3: `ard-resolution` adds `file:`, and a colliding folder's ids and `document:` carry the file. Scoped to colliding folders so no other record changes.
- **I4** — D2 names the call that serves each model.
- **I5** — no gate, so no repair; the alternative carries "no repair offer".
- **I6** — D2 lists §10's sentences, moves the no-path rule into §6, takes the four causes, and settles stale-before-landing; D11 lists `contracts`.
- **I7** — D4 is an ordered function; all seven cases are defined (the date now reads `Run:`).
- **I8** — D3 routes a multi-component entry `own_part` with its Where as `binds`.
- **I9** — D11 and the GIT-G1 list gain every site named; the new-gate sites fall away with the gate.
- **I10** — D9 resolves a match against the traced ref; D1 covers a format with no §9.
- **I11** — D7 carries the caveat on all three states; the risk is corrected.
- **M1** — `:532` is left; counts restated under both alternatives. **M2** — D6 writes the header wherever a model stood. **M3** — no gate site; §5 rule 2 (`:625`) named under the alternative. **M4** — D9 scopes the label check. **M5** — D3 reports code and test apart. **M6** — D10 says what byte-equality covers. **M7** — question 4 and D10. **M8** — D1's one precondition. **M9** — D6's code span.
- **Rulings 3, 4, 7** — D9 states "located and re-read" and requires the call site; D2 and D11 list §10 and log the move; D11 limits the lineage edit to `_source`.
- **Proportion** — revision 1's D8, three risks, the *Not touched* list and question 4 are cut.

## Revision 3 — how each finding of review 2 was addressed

- **N1** — D2 and GIT-G1 edit 2: a carve-out in `phase-handoff` §5 rule 2 (`:625`) with the matching `CLAUDE.md` clause, named a new rule; question 2 asks for both edits in one answer.
- **N2** — D3: a decision whose file is not `ard.md` always carries it; the one-time match rule is given.
- **N3** — D3: `mitigation: true` in the handoff; the call-site rule binds only a Rule carried out by code that must be reached.
- **N4** — D6 and D11: the §7.8 fix is `workflows-core`'s alone, the entry is not open and not reported, `docs-workflows` takes a page patch, and the coupling bullet names `workflows-core` only.
- **N5** — D5: a PRD record's own confirming entry is put at the third row and applied as an overrule; D11 sweeps `:117`, `:120` and `conformance.md:268`.
- **N6** — D6 pins the header's form, an absent line passing and `not traced` holding the rung. **N7** — D2: a wrong `kind:` is no model; D5: "treated as one" binds the arrays alone. **N8** — the unresolved-ref clause is cut. **N9** — D11 names `:72` a truth edit. **N10** — `source-truth.md:615`. **N11** — D2: the PRD-level call's Rules join the inventory. **N12** — D4: `not checked — not this design's`. **N13** — the line is limited to the working tree. **N14** — the invariant names `/conformance`'s two sentences.

# RETURNED-INTAKE: `/create-ard` takes in the threats sent back to the architect

Date: 2026-11-16. Status: **approved by the maintainer 2026-11-16**, revision 3, with the recommended answer to each of the three questions at the end: the `open`-on-a-decision threat is found in the conformance records read from `<default-ref>` by §11's test, approving GIT-G1 edits 1 and 2 (truth) and 3 (a new printed line at `/conformance`'s handoff step) by name; the route of a stand-alone `Returned` entry behind a re-disposed, superseded or withdrawn threat moves to the Dev's `/dev-workflows:design`; and GIT-G1 edit 4 is the one sentence naming the PRD-level run's read, with the Epic-level run's ungated reads logged, not fixed. Written after two independent reviews — of revision 1 (`.superpowers/design-review-1.md`: 1 Critical, 9 Important, 8 Minor) and of revision 2 (`.superpowers/design-review-2.md`: 2 Important, 6 Minor, no third review asked); what changed is listed at the end. The track is the `RETURNED-INTAKE` entry of `docs/superpowers/to-fix.md:201-206`, scheduled next after SEC-G2 D by the maintainer's answer to that design's third question, which widened it to any live threat that is not stale (`docs/superpowers/specs/2026-11-15-sec-g2-d-security-conformance-design.md:3`, `:236`). It builds on SEC-G2 B, C and D as built, on `main` at `8ee5bb809` (`workflows-core` 1.95.0, `product-workflows` 3.83.2, `dev-workflows` 4.69.0).

The three questions at the end are the maintainer's calls; every other decision is the author's. Statements about the tree cite `file:line` at `8ee5bb809`. `create-ard.md`, `design.md` and `conformance.md` are the command files; *the format* is `plugins/workflows-core/references/threat-model-format.md`; `ph` is `plugins/workflows-core/references/phase-handoff.md`.

## Intent

Three states of a live threat are routed to the architect and no command closes them. `/dev-workflows:conformance` sends the PA to `/product-workflows:create-ard <KEY>` for `unanswered — returned to the architect`, `unanswered — no design takes it` and an `open` on a decision the team will not build, each line ending `No command re-disposes a live threat that is not stale yet: …` (`conformance.md:704`). `design-format` tells the Dev that "the architect takes it up with `/product-workflows:create-ard`" (`plugins/dev-workflows/references/design-format.md:334`). But a `/create-ard` refine takes no threat review and no conformance record into its threat model, and puts a question only about a stale threat or an acceptance past its date (`create-ard.md:812-816`, `:881-885`).

This design makes that run read both at its Phase 4.3 step 3, and put each such threat to the architect by the dispositions step 7 already offers. It adds no command, agent, id prefix, branch prefix, gate or field of the model.

**One noun.** *A threat sent back* is a live threat of the model, readable and not stale, that a design or a conformance record sends to the architect, in one or more of the three kinds D2 defines. Every copy of the rule uses that noun.

## What exists today

- **A refine asks about two populations.** Step 3 puts `["Refine the threat model (Recommended)", "Leave it as it is"]`, or, where a threat is stale, `["Refine the threat model (Recommended)", "Re-dispose only the stale threats"]` (`create-ard.md:812-816`). Step 7 walks each stale threat with a four-option array, and on `refined` each acceptance past its date with `["Renew it — a new review date", "Re-dispose it", "Keep it as it stands"]`, whose *Re-dispose it* "puts this step's four-option question, as for a threat stale on its Disposition" (`:881-885`).
- **One path already re-disposes a live threat that is not stale, unasked:** a free-text correction at step 9's gate, which "re-disposes it in place" where it changes only the Disposition and otherwise supersedes or withdraws (`create-ard.md:905`). Nothing brings a returned threat to it.
- **Identity.** A threat is bound on the default branch; a re-disposition rewrites only its Disposition line and keeps its id (format `:80-83`). The PA alone accepts a risk, in the model (format `:74`).
- **`/conformance` reads a design's entries so** (`conformance.md:132`): each `### [DT#N]:` heading at the start of a line in the section, `N` matching `^[1-9][0-9]*$`, with its block to the next `### ` or `## ` heading, live where the block holds no `- **Withdrawn:**` item; a `Mitigated` entry counts only where its block holds `- **Disposition:**` exactly once and its `[DT#N]` heads one entry. An unreadable threat takes its state before any part is read (`:484`). The two `unanswered` reasons come from entries (`:489`); a mitigation is `open` where an entry "that is not `resolved`, `orphaned` or `requirement withdrawn`" names it (`:481`), and goes to the architect where that entry "is not, whole, `fix-code`" (`:704`).
- **A record's entry is structured**: `### [DD#n] <requirement id>`, `document: <file>, in <KEY>`, `decision:` with `status:`, `flags:` (`plugins/dev-workflows/references/conformance-format.md:93-108`). `workflows-core:source-truth` §7.8 reads records for a documentation run, **from the working tree, "never from the default branch"** (`plugins/workflows-core/references/source-truth.md:587`); `/dev-workflows:ready` keeps a test of its own on the default branch's copy (`conformance-format.md:167`).
- **A consumer that reads a gated deliverable only as `<default-ref>` holds it executes no gate** (`ph:628`; `CLAUDE.md:151`). `_conformance.md` is advisory and gated by nobody (`ph:418`).
- **An Epic-level `/create-ard` run already reads its Epic's `specification.md` and `design.md` from the working tree at Phase 2, ungated**, as context (`create-ard.md:483-488`, `:628`); no `ph` §3.4 row names either, and both are gated deliverables (`ph:414`).
- **`/create-ard` cannot load `design-format` or `conformance-format`** — `dev-workflows`' references (`.claude/rules/threat-model.md:24`).

## Goals

1. **A refine shows the architect every threat sent back**, from sources that have landed, unasked.
2. **Each is put as a question whose answers are the model's own dispositions.**
3. **`threat-model.md` stays the architect's alone**; `/create-ard` writes no design and no record.
4. **Nothing read from a design or a record is written anywhere or handed to an agent.** It is shown in a question's text, and nowhere else.
5. **No question, array or written file changes** where nothing is sent back (D8).
6. **A minimal GIT-G1 footprint**, every edit listed for approval by name.

## Non-goals

- **A new command, agent, id prefix, branch prefix, role, plugin dependency or model field.**
- **Any change to `threat-modeler` or `ard-reviewer`**, to how `/conformance` works a state out, to its record's form, to `/ready`'s rung or to `source-truth`.
- **Stopping anything**: a design may hand off with a threat unanswered (C's question 2).
- **Gating or moving Phase 2's older read** of the Epic's `specification.md` and `design.md` — logged (question 3).
- **Suppressing a threat the architect kept as it stands**; **moving `/conformance` onto §11**; **splitting Phase 4.3 out of `create-ard.md`** — each logged.

## Anti-goals

- **A second place a risk is accepted**: only the architect, only in this run, only into the model.
- **A design, record or folder name that steers the run**: every value read has a shape test or is compared whole with one the run composed (D5).
- **A source that decides**: it nominates a threat for a question and settles nothing.
- **A prerequisite**: no design and no record is required.

## Decisions

### D1. Two sources, each read as the default branch holds it

**Designs** carry the two `unanswered` kinds; **records' entries** carry the third. Both are read at Phase 4.3 step 3, after its check, only where the folder holds a model, `fresh` is `false` and a set resolved.

- **Which files, by known path.** For the model's folder `F`: `F/design.md` and `F/_conformance.md`. Where `F` is a PRD folder (a BRD-route slice included): also each Epic folder's two files, the Epic folders being those directly under `F` that `<default-ref>` lists, placed by prefix, as `/conformance` lists a PRD's Epics (`conformance.md:67`). Where `F` is an Epic folder: also the PRD folder's `_conformance.md`, since a PRD run's record holds entries on an Epic's decisions.
- **How.** `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`, written as `ph` §3.2 writes one. No gate, no repair offer, nothing switched. On a specs tree that is no git repository there is no other copy, and the file is read.
- **A folder name passes a guard before it reaches a command** — the gap FOLDER-NAME-CLASS names (`to-fix.md:265`). An Epic folder is read only where its name matches, whole, `^EPIC-[A-Za-z0-9._-]+$` and begins, whole, `EPIC-<its carrier's key>-`, the carrier being its `epic.md` at the ref, as `workflows-core:addressing` §4.1 counts a carrier (`addressing.md:311`); any other is named in words, by its position in the listing, and neither of its files is read. It is a fail-closed shell guard, not a naming rule, and a class stated in `addressing` §2 would replace it. **Two limits:** a legacy Epic folder with no prefix, which `/conformance` places by its resolved kind (`conformance.md:62`), and a folder whose slug holds any other character, are not read; each is named.
- **What is true of the designs, per run kind.** A **PRD-level run** reads every design under its folder only as `<default-ref>` holds it: it is `ph` §5 rule 2's consumer that executes no gate. An **Epic-level run** reads its Epic's `design.md` so for the intake, and also, at Phase 2, from the working tree as context — the older ungated read. It is not that consumer, and nothing this track writes into `ph` says it is: both reads are stated in `create-ard.md` and the rules invariant, and logged in `to-fix.md` (question 3). Either way the intake itself takes nothing from an unlanded copy: for a design the working tree holds and the ref does not, the run prints `Threat model: <path> is not on the default branch — it nominates nothing`.
- **Why the default branch.** Identity binds there for a threat and an entry alike, so only a bound entry or a landed ruling nominates.
- **Why not the record's `## Threats` lines.** They put a free-text title before the state (`conformance-format.md:50`), no run reads them back (`:78`), and an `open` line does not say what its entry decided.
- **Rejected: a `require-on-main` gate per design** — a §3.4 row and a §3.7 site per folder, with a repair offer that can move the checkout mid-run. **Rejected: the working tree's records** — one GIT-G1 edit, not three, but an unlanded ruling nominates, and each record becomes a file the run read, which `ph` §2.2's stack test takes as an input (`create-ard.md:275`; `ph:224`).

### D2. Which threats are sent back — format §11, new

`workflows-core:threat-model-format` gains **§11, *Threats sent back to the architect***. It holds everything that is rule and not flow — the file list, the kinds, the entry reading, D5's shape tests and fixed line texts — so the command gains only step 3's table, one paragraph of step 7 and the no-§11 line. It is written **in `/conformance`'s words**, as §10 took `/design`'s.

**The threats tested** are the model's live threats that the check did not find stale and that are readable by format §10's test — a field missing or repeated, its Where, its Disposition in none of the three forms, an id heading more than one threat. An unreadable threat is never sent back: one line names it by id, and it keeps its own route, the review. `<ref>` is `[[<K>]] [TH#N]`, composed from the run's own key for the folder and the threat's id.

**An entry**, as `conformance.md:132` reads one: each `### [DT#N]:` heading at the start of a line in the design's `## Threat review`, outside any fenced block, the section running to the next `## ` heading, the block to the next `### ` or `## ` heading; live where its block holds no `- **Withdrawn:**` list item at the start of a line. It **answers** a threat where its block holds `- **Answers:**` exactly once, its value, whole, `<ref>`. **Its Disposition is read only where its block holds `- **Disposition:**` exactly once** — for all three openings below, and for D4's entry, whose one `Answers` is, whole, `—`. It is ***M*** where that Disposition opens `Mitigated — Rule: ` and its `[DT#N]` heads one entry of the design.

A threat takes **every kind that holds**:

1. **`returned`** — its Disposition opens `Deferred to design: ` or holds `; the rest deferred to design: `; no live *M* entry of a design read answers it; and a live entry answering it bears a Disposition opening `Returned to the architect — `.
2. **`taken by no design`** — the same, save that none returns it and one bears a Disposition opening `Not this design's — `.
3. **`open on a decision`** — its Disposition opens `Mitigated by `, and a record read holds an entry naming a pair's decision whose `status:` is not `resolved`, whose `flags:` name neither `orphaned` nor `requirement withdrawn`, whose block holds no `superseded-by:` line — what a PRD run writes into an Epic entry the PE overrules (`conformance.md:437`) — and whose `decision:` is, whole, `amend-document` or `accept`. It names the decision where its heading's requirement id is, whole, `[AD#n] Rule` for a decision of `ard.md` or `[AD#n] Rule (ard-<area>.md)` for an area file's, and its `document:` line is, whole, that file and the key of the folder holding it. A `[[<PRD-KEY>]] ard.md` pair counts only where the key is, whole, the run's PRD key (format §6, `:94`).

A threat no entry and no record names is not sent back: `no design answers it` is the Dev's.

- **The record test is §11's own, as `/ready`'s is its own** — not §7.8's, whose *The copy read* forbids this copy. **The record set** is D1's files. A record is read only where its frontmatter `key:` is, whole, the run's key for its folder and it holds no line beginning `<<<<<<<` or `>>>>>>>`; another is named in one line and not read. **No instant is used**: the test orders no two records, so `At:` and its guard are never read; each entry found is shown with its record's `Run:` date (D5). An overruled Epic entry is dropped by its `superseded-by:` line, which needs no precedence and no instant; an Epic's entry and a PRD's on one decision are otherwise both shown. §11 puts a known-set test on `decision:` where `/conformance` says "not, whole, `fix-code`", so a malformed decision nominates nothing.
- **Compose and compare, never extract.** No key, id or path is taken out of a design or a record, save the two ids D5 shape-tests and shows.
- **It is a nomination.** A record may be older than the code and a design may not have landed, so §11 decides only who is asked; *Keep it as it stands* is always an answer.
- **Two statements, changed together.** Kinds 1 and 2 and the entry reading restate `conformance.md:132` and `:489`; kind 3 restates `:481` and `:704`. `/conformance` cannot cite §11 yet — beside an older `workflows-core` it would lose its states, as `/design` and §10. A rules invariant names the pair, says the record test is §11's own, as `.claude/rules/dev-workflows-conformance.md` says of `/ready`'s, and carries a recipe: `command grep -rlF "is, whole, the threat's ref" plugins --exclude=CHANGELOG.md`, a phrase of `conformance.md:489` that only that file holds today and that §11 takes verbatim, so the recipe lists the two copies and no other file. `to-fix.md` logs `/conformance`'s move onto §11.
- **`design-format` section 15 and `conformance-format` §6 name their new reader**, as §6 does for `/release-notes`: the fields §11 reads, and that a change to one is a change to §11.

### D3. How each is put — step 7 widened, two new arrays at step 3

**Step 3**, its text listing each threat sent back with its kinds:

| The check finds | Sent back | `choices:` |
|---|---|---|
| no stale threat | none | `["Refine the threat model (Recommended)", "Leave it as it is"]` — today's |
| a stale threat | none | `["Refine the threat model (Recommended)", "Re-dispose only the stale threats"]` — today's |
| no stale threat | one or more | `["Refine the threat model (Recommended)", "Re-dispose only the threats sent back", "Leave it as it is"]` |
| a stale threat | one or more | `["Refine the threat model (Recommended)", "Re-dispose only the stale threats and those sent back"]` |

Each *Re-dispose only …* option → `state: redisposed`, steps 7 to 9, no dispatch and no walk. *Leave it as it is* stays where no threat is stale: a threat sent back is not wrong, as a stale one is. The report names each one left.

**Step 7**, on `refined` and `redisposed`, at most four questions per call as step 6 puts them: each threat sent back takes `choices: ["Re-dispose it", "Keep it as it stands"]`, its text naming the threat, its Disposition, each kind and what sent it back (D5), and saying no option is recommended. *Keep it as it stands* changes nothing. *Re-dispose it* puts step 7's four-option question, as for a threat stale on its Disposition (`create-ard.md:885`'s sentence):

| Answer | What it does to the threat |
|---|---|
| *Record an [AD#N] for it* | confirms a live decision the architect names, or grills a new one, as step 6 does → `Mitigated by <pair>`, with `; the rest deferred to design: <what>` where the grill leaves a rest |
| *Defer to design* | `Deferred to design: <what the design must answer>`, the current text offered to keep or replace: the architect's answer to the Dev is the reworded question, and the format gains no note field |
| *Accept the risk* | owner, reason and review horizon, as step 6 asks; the architect alone |
| *Not a threat — withdraw it* | its reason → `- **Withdrawn:** <reason>` |

The first three are re-dispositions: the threat keeps its `[TH#N]` (format §5). A changed Where or Threat is a supersession and stays step 9's correction, which the question's text says. Free text is normalised into the array or asked again. The arrays are step 7's own, so `escalation-rules`' picker vocabulary gains nothing.

- **A `redisposed` run that changed no threat** — every answer *Keep it as it stands*, and no stale threat — writes no draft: `state: left`, and the report says each was kept. So it costs no review, no stamp and no handoff of an unchanged model (`create-ard.md:799`, `:890`).
- **A stale threat is the stale walk's alone.** §11 does not test it, and its question is today's.
- **The threat open on a decision is put like any.** The architect may supersede the decision — in Phase 4's grill, or as a correction to the ARD draft at step 9, after which step 8's check finds the threat stale and the stale walk puts it — and the question's text says so. Or they keep the decision and accept, defer or re-rest the threat: that is the gap, since only the architect accepts a risk and no question reached a threat that is not stale.
- **Why two questions.** The acceptance walk already does it, an explicit *Keep* is honest where nothing forces a change, and four options leave no room for a fifth.
- **A limit.** The three forms are exclusive, so accepting a threat that reads `Mitigated by <pair>; the rest deferred …` drops its pairs. The text quotes the Disposition it replaces.

### D4. A returned threat that answers none of the model's

A Dev may return a threat the design's own interfaces add: `Answers: —` (`design-format.md:329`). **It is listed, never converted**: step 3's text names each — `[[<its design's key>]] design.md [DT#N]`, with its Threat line and reason under D5's bounds — and says *Refine the threat model* is where the architect adds a threat of their own, typed by them (step 6's *The PA's own threats*). The report carries its key and id alone. The run makes no link, and the entry stays until the Dev withdraws it. It follows from two standing decisions — the model is the architect's alone, and returned threats live in `design.md` and the pull request only — so it is not a question. **Rejected: a candidate built from it**, which would write a Dev's or an agent's text into the architect's file.

### D5. Untrusted input: every value has a test, and is shown once

- **Nothing read from a design or a record is written** — into the model, an ARD draft, `threat_model.report` or any file — **or reaches an agent**: `threat-modeler`'s eleven fields (`create-ard.md:826`) and `ard-reviewer`'s brief are unchanged. A `Deferred to design:` text is the architect's typed or confirmed answer, drafted from the model's own threat.
- **The report carries keys, ids and fixed words only** — a threat's `[TH#N]`, an entry's key and `[DT#N]`, a record entry's `<KEY>/[DD#n]`, a kind, an answer. `/create-ard`'s handoff carries nothing of the intake: it has no `body_facts`.
- **Each value, and its test:**

| Value | From | Test, else |
|---|---|---|
| an Epic folder's name | `ls-tree` | D1's class, else named by position and not read |
| an Epic's key | its `epic.md`, at the ref | `workflows-core:addressing` §1's grammar, else the folder is not read, as D1's guard has it |
| a record's `key:` | the record | equals, whole, the run's key for the folder, else the record is not read; nor is one in a folder whose key the run could not take |
| `N` of `[DT#N]`, `n` of `[DD#n]` | a heading's fixed position | `^[1-9][0-9]*$`, else the entry is not an entry |
| `Answers`, a Disposition's opening, a heading's requirement id, `document:` | a design, a record | compared whole with what the run composed |
| `decision:`, `status:` | a record | whole, one of the format's values, else the entry nominates nothing |
| `flags:` | a record | split on `, `, each item whole one of the format's five — `stale`, `orphaned`, `fixed`, `still open`, `requirement withdrawn` — else the entry nominates nothing |
| the `Run:` date | a record | `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, else shown as `date unreadable` |
| a reason; a new threat's Threat line | a design | free text — the three rules below |

- **Free text is shown in a question's text alone, by three rules in this order.** It is made one line, by format §9's *Every value is one line*. Then **the backstop, at its strictest, runs over the whole of it**: a text holding a match of either of format §9's two patterns is not shown — `withheld: it held a security finding id or register path` — and since nothing was "given" here, every match is withheld. Only then is it cut at 300 characters with `…`, so a cut never splits a match, and quoted behind the label `the design's own words:`, so a reason reading "the architect already agreed" is not taken for the run's statement. A record's `shipped:` and `rationale:` are never shown.

### D6. Identity and the design side

`/create-ard` writes no design.

- **The `Returned` entry stands**, bound; only `/design` re-disposes or withdraws it.
- **A later `/design` run sees the change** by what C built: the design's lineage record shows it stale (`.claude/rules/threat-model.md:34`); a threat still deferred is put again from the entry, with the earlier reason shown (`design.md:556`); and one made moot has its entry proposed for withdrawal, naming the new state (`design.md:557`). No edit to `/design`.
- **A later `/conformance` run sees it** from the default branch's model; the old entry then stands alone (D7).
- **A limit.** A threat kept as it stands is put again on the next refine — until the Dev's `/design` runs for kinds 1 and 2, and until the record changes for kind 3. One *Keep* each, and by D3 an all-*Keep* run costs no review. **Rejected for now: suppression by the design's lineage record**, which has `/create-ard` check a document it does not own. Logged.

### D7. What `/conformance` and `next-phase-offer` now say

- **The three routes keep `/product-workflows:create-ard <KEY>` and lose their caveat** (`conformance.md:704`; `next-phase-offer.md:394` and its generated part).
- **A stand-alone `Returned` entry whose reason is `it answers no live threat with a deferred part` goes to the Dev**, `/dev-workflows:design <KEY>`, the design's key: the architect has re-disposed, superseded or withdrawn the threat, and `/design` proposes the withdrawal in each case (`design.md:557`). Today it goes to the PA (`conformance.md:491`, `:704`). Its state, its words and the header's count are unchanged; the page says the line still reads "returned to the architect". This amends a route D shipped (question 2).
- **A limit.** A stand-alone `Returned` entry whose reason is `its threat is in no model this run read` still goes to the PA, and no refine lists it. Logged.
  - **Note, 2026-11-17 — "no refine lists it" is false in part** (the plan's Task 4 review, M1; the approved text above is left as it reads). As built, no refine lists it where its `[[…]]` names no folder whose model a refine reads; where it names a folder whose model `/conformance` left unused, or that only the working tree holds, a refine of that folder lists the threat. `docs/superpowers/to-fix.md` logs it so, as STANDALONE-NO-MODEL.

### D8. No regression

- **A folder with no model**, one *Start fresh* discards, and a run with no set never reach the read.
- **A model with nothing sent back: no question, array or written file changes.** Not byte-equal: the run makes its `git show` reads, may print D1's line for an unlanded design or a line for a folder, record or threat it did not read, and, beside an older `workflows-core`, prints the line below on every refine of a model.
- **No reference is loaded for the intake** but the format step 3 already loads.
- **One precondition, failing closed**: where the loaded format holds no heading `## 11.`, the run reads no design and no record, prints `Threat model: threats sent back not read — update workflows-core`, and goes on as today.
- **Fixtures, as traced runs**: no model; a model and no design; a returned threat, each of the four answers; an all-*Keep* run; a threat taken by no design; one open on a decision, superseded at step 9; a threat holding kinds 1 and 3; an unreadable threat; a duplicated `[DT#N]`; a returned new threat; a design only in the working tree; an Epic-level run; a folder name outside the class; a format with no §11; a reason holding a `SEC#n`.

### D9. Every site the change touches

- **The claim sweep is by subject over refinement 4's scope** (`.claude/rules/claim-sweep.md`), each count taken before and after; no hand list is the set. The subjects: *what re-disposes a live threat that is not stale*; *what a refine proposes, and what each step 3 option walks*; *who reads `_conformance.md`, and how many*; *what `/create-ard` reads*; *where a returned threat goes*. Copies revision 1 missed, as a start: `plugins/product-workflows/docs/workflow.md:137`, `plugins/product-workflows/docs/commands/create-ard.md:152`, `plugins/dev-workflows/docs/commands/conformance.md:130`, `plugins/workflows-core/reference-parts/next-phase-offer/dev.md:199`. The exclusivity probe runs over "only the stale", "only what", "no command", "three more commands".
- **`product-workflows`:** `create-ard.md` (steps 3 and 7, `threat_model.report`, *Final report*, and a sentence at Phase 2 naming the Epic-level run's two reads of its Epic's `design.md`), about 2 to 3 KB; pages; `CHANGELOG.md`.
- **`workflows-core`:** the format (§11; §5's and §6's sentences on a re-disposition and a refine; §9's opening); `next-phase-offer` and its part; `phase-handoff` and its parts; pages; `CHANGELOG.md`.
- **`dev-workflows`:** `conformance.md` (`:704`, `:576`); `design-format` section 15; `conformance-format` §6; pages; `CHANGELOG.md`.
- **Rules files, measured before writing** — `.claude/rules/product-workflows.md` is 18,017 characters of 20,000: `threat-model.md` (a new invariant: the two sources, the default branch, shown and never copied, the pair and its recipe, §11's own record test, the Epic-level run's ungated reads; invariants 4 and 8); `product-workflows.md` (the map line); `dev-workflows-conformance.md` (the record's readers); the coupling file. `.claude/rules/workflows-core.md`, at 19,166, is not touched.
- **Untouched:** `threat-modeler`, `ard-reviewer`, `design.md`, `ready.md`, `source-truth`, `pre-lint`, `lineage-kinds.json`, `escalation-rules`, `specs-repo-git`, every script and gate.

### D10. Versions and coupling

A minor each for `workflows-core`, `product-workflows` and `dev-workflows`. Three bullets:

- **`product-workflows` beside an older `workflows-core`**: no §11, so nothing sent back is read, and the run says so. Update `workflows-core`.
- **`dev-workflows` or `workflows-core` beside an older `product-workflows`**: the report sends the architect to a `/create-ard` that lists nothing — the misleading direction, which nothing detects. Update `product-workflows` with either.
- **`product-workflows` beside an older `dev-workflows`**: its report still says no command re-disposes such a threat, and sends a re-disposed threat's old entry to the PA. Update `dev-workflows`.

## The GIT-G1 edits

**Each needs the maintainer's approval by name.** `specs-preflight`, `commit-artifacts`, `specs-repo-git`, `branch-check`, `ph` §3.4's table and §3.7's sites, and every section of `/create-ard`'s own handoff (`create-ard.md:1010`) are untouched. No `require-on-main` caller is added or changed.

1. **`ph` §4.0, the `_conformance.md` register row** (`ph:418`) — **truth edit**: `/product-workflows:create-ard` joins the readers, from `<default-ref>` alone, at its Phase 4.3, for D1's records. "None runs `require-on-main` on it" stands.
2. **`ph` §4.0, the advisory class's sentence on a reader that does not read the working copy** (`ph:403`) — **truth edit**: its `_conformance.md` case gains `/create-ard`, which reads an Epic's record so too.
3. **A new printed line at `/dev-workflows:conformance`'s handoff step** (`conformance.md:576`) — **new behaviour**, obliged by edit 2's rule. On an Epic or a PRD run whose record holds an entry on an `[AD#n]` Rule decided `amend-document` or `accept`, above the array and below the `/ready` line where there is one, verbatim: `/product-workflows:create-ard reads this record only on the default branch — declined, a refine of the threat model does not see this run's decisions until this record merges.` An Epic run prints no such line today.
4. **`ph` §5 rule 2** (`ph:628`) — **truth edit**: after "`/dev-workflows:conformance` reads each `threat-model.md` so", one sentence that a PRD-level `/product-workflows:create-ard` run reads each `design.md` under its folder so, at its Phase 4.3. Nothing else: the sentence claims no exclusivity, so its silence on the Epic-level run is not false; the rule carries no admission of that run's reads and no pointer to a repository-only file.

The regenerated `reference-parts/phase-handoff/` files follow edits 1, 2 and 4.

## What is left to the builder

Step numbering inside steps 3 and 7; the wording of §11 and of each question's text; the fixed lines D5 and D8 name only in part; `threat_model.report`'s lines; the fixtures; measuring `create-ard.md`'s load before and after.

## Risks

- **`create-ard.md` is 220 KB.** §11 holds the rule; the command gains 2 to 3 KB.
- **Two statements of `/conformance`'s rules** (D2), held together by an invariant and a recipe until `/conformance` can cite §11.
- **§11's record test is a third "open" test**, beside §7.8's and `/ready`'s. It is narrower than either and only nominates.

## The `to-fix` and roadmap updates

- **`docs/superpowers/to-fix.md`**: RETURNED-INTAKE (`:201-206`) is closed, naming this file and the versions released, and `:199` and `:242` reworded. FOLDER-NAME-CLASS (`:265`) notes that this track's sites carry a guard of their own, which a class stated in `addressing` §2 replaces. New entries: a threat kept as it stands is put again (D6); the three-form limit (D3); the Epic-level run's ungated reads — Phase 2's of its Epic's `specification.md` and `design.md` from the working tree, and the intake's of that `design.md` from the ref; `/conformance`'s move onto §11; the stand-alone entry whose threat is in no model read (D7); Phase 4.3's weight in a 220 KB command.
- **The roadmap** (`docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:103-104`): rows C and D each gain *Its follow-up, the intake of threats sent back, built as RETURNED-INTAKE:* this file, with its versions.

## Questions for the maintainer

1. **How is the threat open on a decision found, and which GIT-G1 edits follow?** That it is taken in is already decided. Recommended: **the records' entries, from `<default-ref>` alone, by §11's own test** — approving by name edit 1, edit 2 and edit 3, which is a new printed line at `/conformance`'s handoff step, not a truth edit. Alternatives: the working tree's records (edit 1 only; an unlanded ruling nominates, and the run's branch can be cut elsewhere); or no record read — the architect names any live `[TH#N]` to re-dispose, from the model's own ids (no edit 1 to 3; the run does not show the threat unasked).
2. **May this track change one route D shipped?** Recommended: **yes** — a stand-alone `Returned` entry behind a threat the architect has re-disposed, superseded or withdrawn goes to the Dev's `/dev-workflows:design` (D7).
3. **GIT-G1 edit 4, and the Epic-level run's ungated reads.** Recommended: **approve one sentence in §5 rule 2 naming the PRD-level run's read alone, and log the Epic-level run's reads** of its own `specification.md` and `design.md` in `to-fix.md`, stated in `create-ard.md` and the rules invariant. Alternatives: omit edit 4; write the admission into the rule; or fix the reads now — a ref-only Phase 2 read, a change to what an Epic-level ARD takes as context, or a new §3.4 row.

## Revision 2 — how each finding was addressed

- **C1** — D1 states the two run kinds apart; the unlanded-design line says "nominates nothing"; edit 4 is narrowed and question 3 asks for it; the Phase 2 read is logged with both files.
- **I1** — the §7.8 dependency is cut: §11's record test is its own, with its record set, its malformed test, and no instant or guard (D2). `source-truth` is untouched.
- **I2** — §11 takes `/conformance`'s entry reading, its exactly-once Disposition, its duplicated-`[DT#N]` rule and its unreadable-threat rule, with a recipe and a `to-fix` entry.
- **I3** — the stale-and-sent-back case and its fixture are cut. **I4** — an all-*Keep* `redisposed` run is `state: left` (D3).
- **I5** — edit 3 is classed new behaviour, at `:576`, with its text and condition. **I6** — question 1 asks only how, and the edits.
- **I7** — D1 states a class for the folder names it writes. **I8** — D5's table gives every value its test; the backstop covers every free text; the report carries ids and fixed words, and D4 conforms; `body_facts` is gone.
- **I9** — D9 gives subjects and scope, with the missed copies as a start.
- **M1** — the `inputs_read` inference about a `<default-ref>` read is cut. **M2** — every kind that holds. **M3** — format §6's key rule cited. **M4** — named as a limit (D7). **M5** — D8 reworded. **M6** — four per call. **M7** — budgets measured; `workflows-core.md` no longer touched. **M8** — labelled, quoted, cut at 300 characters.
- **Rulings** — the asked-again entry covers kind 3; rule moved into §11; revision 1's D4 folded into D3, its question 3 into D4, its question 4 into question 3; *What exists today* and Risks cut.

## Revision 3 — how each finding of review 2 was addressed

- **N1** — kind 3 drops an entry holding a `superseded-by:` line, so an overruled Epic entry nominates nothing; D2 names the status apart from the two flags; D5's table gives `flags:` its split and known set.
- **N2** — edit 4 names the PRD-level run's read alone, with no admission and no pointer to `to-fix.md`; the Epic-level run's reads are logged there and stated in `create-ard.md` and the rules invariant; question 3 recommends that.
- **N3** — D1's guard is tied to `EPIC-<its carrier's key>-`, called a guard, and its two limits named. **N4** — the carrier is `epic.md`. **N5** — the Disposition is exactly-once for all three openings and for D4's entry. **N6** — one line, then the backstop over the whole text, then the cut. **N7** — a record in a folder whose key the run could not take is not read. **N8** — the three `CHANGELOG.md` files are named.
- **Rulings** — the invariant says the record test is §11's own; the recipe's phrase is named (D2); the `to-fix` entry says what replaces the guard.

# RETURNED-INTAKE: `/create-ard` takes in the threats sent back to the architect

Date: 2026-11-16. Status: **draft, revision 1 — awaiting review, then the maintainer's answers to the four questions at the end.** The track is the `RETURNED-INTAKE` entry of `docs/superpowers/to-fix.md:201-206`, scheduled next after SEC-G2 D by the maintainer's answer to that design's third question, which widened it to any live threat that is not stale (`docs/superpowers/specs/2026-11-15-sec-g2-d-security-conformance-design.md:3`, `:236`). It builds on SEC-G2 B, C and D as built, all on `main` at `8ee5bb809` (`workflows-core` 1.95.0, `product-workflows` 3.83.2, `dev-workflows` 4.69.0).

Every decision is written with a recommended answer. The four at the end are the maintainer's calls; the rest are the author's. Statements about the tree cite `file:line` at `8ee5bb809`; `create-ard.md`, `design.md` and `conformance.md` are the command files, `plugins/product-workflows/commands/create-ard.md` and `plugins/dev-workflows/commands/{design,conformance}.md`, and *the format* is `plugins/workflows-core/references/threat-model-format.md`. What I could not ground is marked **assumption**.

## Intent

Three states of a live threat are routed to the architect and no command closes them. `/dev-workflows:conformance` sends the PA to `/product-workflows:create-ard <KEY>` for `unanswered — returned to the architect`, `unanswered — no design takes it` and an `open` on a decision the team will not build, each line ending `No command re-disposes a live threat that is not stale yet: the architect waits for the intake of returned threats, or, for a threat open on a decision, supersedes that decision.` (`conformance.md:704`). `design-format` already tells the Dev that "the architect takes it up with `/product-workflows:create-ard`" (`plugins/dev-workflows/references/design-format.md:334`), and `/design` prints that command beside every returned entry (`design.md:572`). But a `/create-ard` refine reads no design's threat review and no conformance record, and puts a question only about a stale threat or an acceptance past its date (`create-ard.md:812-816`, `:881-885`).

This design makes that run read both, at its Phase 4.3 step 3, and put each such threat to the architect by the dispositions step 7 already offers. It adds no command, no agent, no id prefix, no branch prefix, no gate and no field of the model.

**One noun.** *A threat sent back* is a live threat of the model that is not stale and that a design or a conformance record sends to the architect, in one of the three kinds D2 defines. Every copy of the rule uses that noun, so the next sweep finds them.

## What exists today

- **A refine asks about two populations.** Step 3 checks the folder's model and puts `["Refine the threat model (Recommended)", "Leave it as it is"]`, or, where a threat is stale, `["Refine the threat model (Recommended)", "Re-dispose only the stale threats"]` (`create-ard.md:812-816`). Step 7 walks each stale threat with a four-option array, and on `refined` each acceptance past its date with `["Renew it — a new review date", "Re-dispose it", "Keep it as it stands"]`, whose *Re-dispose it* "puts this step's four-option question, as for a threat stale on its Disposition" (`:881-885`).
- **One path already re-disposes a live threat that is not stale, unasked:** at step 9's confirmation gate "a correction to a held threat … that changes only its Disposition re-disposes it in place, and any other change … supersedes it or withdraws it, as step 7 does" (`create-ard.md:905`). It is reached only on a run that holds a draft, by free text, and nothing brings a returned threat to it. The `to-fix` entry's "no path" is true of a put question, not of this correction.
- **Identity.** A threat is bound once it stands on the default branch; a re-disposition rewrites only the Disposition line and keeps the id; a changed Where or Threat is a new `[TH#M]` superseding the old; a moot one is withdrawn (format `:80-83`). A stale Disposition clears on a re-disposition (`:106`).
- **The PA alone accepts a risk**, in the model (format `:74`; `.claude/rules/threat-model.md:35`). The Dev never does (`design.md:540`), and `/conformance` accepts no mitigation's discrepancy (D's D5).
- **A design's entry** is `### [DT#N]: <title>` under `## Threat review`, six fields each a list item at the start of a line, `Answers` being `[[<KEY>]] [TH#N]` or `—`, its Disposition one of `Mitigated — Rule: `, `Not this design's — …` and `Returned to the architect — <why>`, live while it carries no `- **Withdrawn:**` item (`design-format.md:308-338`). It is bound on the default branch as a threat is (`:337`).
- **A later `/design` run** puts a deferred threat again from its `Returned` entry, showing the earlier reason (`design.md:537`, `:556`), and proposes the entry's withdrawal once the model no longer holds the threat as live and deferred (C's design, `docs/superpowers/specs/2026-11-14-sec-g2-c-design-threat-review-design.md:119`). A design records the model in its lineage, and that check compares the model's threats with the copy the design recorded (`.claude/rules/threat-model.md:34`).
- **`/conformance` works every threat's state out itself**, from the default branch's model and the designs it gates, and reads no record's `## Threats` back (`plugins/dev-workflows/references/conformance-format.md:78`). The two `unanswered` reasons this track cares about come from design entries alone (`conformance.md:489`); the third state comes from a record entry's `decision:` (`:704`: "an `[AD#n]` mitigation whose entry is not, whole, `fix-code`").
- **A stand-alone `Returned` entry** — one whose threat is no longer live with a deferred part — still reads `unanswered — returned to the architect` and is still routed to the PA (`conformance.md:491`, `:704`).
- **A record's entry is structured**: a `### [DD#n] <requirement id>` heading, `document: <file>, in <KEY>`, `decision:` with `status:`, `flags:`, `superseded-by:` (`conformance-format.md:93-108`). `workflows-core:source-truth` §7.8 is the one authority on which entries are open and on the mapping `amend-document` or `accept` → `document-as-code` (`plugins/workflows-core/references/source-truth.md:606-615`), and two commands of another plugin already read records by it without loading `conformance-format` (`conformance-format.md:163-167`).
- **Two reads are already sanctioned without a gate.** A consumer that reads a gated deliverable only as `<default-ref>` holds it executes no `require-on-main` and names, in one line, a copy the working tree holds that the ref does not (`plugins/workflows-core/references/phase-handoff.md:628`; `CLAUDE.md:151`). `_conformance.md` is advisory, gated by nobody, and `/dev-workflows:ready` reads it from `<default-ref>` alone (`phase-handoff.md:418`).
- **`/create-ard` cannot load `design-format` or `conformance-format`**: both are `dev-workflows`' references, and a reference crosses a plugin boundary only from `workflows-core` (`.claude/rules/threat-model.md:24`).

## Goals

1. **A refine shows the architect every threat sent back**, from sources that have landed, without being asked to look.
2. **Each is put as a question whose answers are the model's own dispositions**: mitigated by a decision, deferred to design, accepted by the architect, or withdrawn; a supersession stays step 9's.
3. **`threat-model.md` stays the architect's alone**, and `/create-ard` writes no design and no record.
4. **Nothing read from a design or a record is written anywhere or handed to an agent.** It is shown to the architect, one line, and that is all.
5. **No regression** (D9).
6. **A minimal GIT-G1 footprint**, every edit listed for approval by name.

## Non-goals

- **A new command, agent, id prefix, branch prefix, role, plugin dependency or field of the model.**
- **Any change to `threat-modeler` or `ard-reviewer`** — neither brief gains a field.
- **Any change to how `/conformance` works a state out**, to its record's form or to `/ready`'s rung. D8 changes one route of its *Next step*.
- **Stopping anything.** No threat sent back stops a `/create-ard` run, its handoff, a design or a merge: a design may hand off with one unanswered (C's question 2).
- **Suppressing a threat the architect already answered by keeping it deferred** (D7's limit; logged).
- **Gating the Epic's `design.md` that an Epic-level run already reads at Phase 2** (`create-ard.md:487`) — an older read, logged, not this track's.
- **Moving `/design` onto format §10** (DESIGN-ON-S10 stands).

## Anti-goals

- **A second place a risk is accepted**: only the architect, only in this run, only into the model.
- **A design or a record that steers the run**: no path, key or id is built from their text, and none of it reaches a file or a brief.
- **A record that decides**: a source nominates a threat for a question and settles nothing.
- **A prerequisite**: no design and no record is required, and an absent one changes nothing.

## Decisions

### D1. Two sources, both read as the default branch holds them

**Designs** carry the two `unanswered` kinds; **conformance records' entries** carry the third. Both are read at Phase 4.3 step 3, after its check, only where the folder holds a model, `fresh` is `false` and a set resolved — the run that already loads the format and asks a question.

- **Which files, by known path, never by a search.** For the model's folder `F`: `F/design.md` and `F/_conformance.md`; where `F` is a PRD folder (a BRD-route slice included), also each Epic folder's `design.md` and `_conformance.md`, the Epic folders being those directly under `F` that `<default-ref>` lists, placed by prefix and keyed by their own carrier, as `/conformance` lists a PRD's Epics (`conformance.md:67`); where `F` is an Epic folder, also the PRD folder's `_conformance.md`, since a PRD run lists an Epic model's threats.
- **How.** `git -C "$SPECS_PATH" show "<default-ref>:./<path>"`, the object name written as `phase-handoff` §3.2 writes one. No gate, no repair offer, nothing switched. For a design this is `phase-handoff` §5 rule 2's consumer that executes no gate, and it owes that rule's one line: `Threat model: <path> is not on the default branch — its threat review is not read`, for a design the working tree holds and the ref does not. On a specs tree that is no git repository there is no other copy, and the file is read.
- **Why the default branch.** Identity binds there, for a threat and for an entry alike, so only a bound `Returned` entry or a landed ruling nominates. A Dev's uncommitted draft, or a PE's declined record, cannot. And a `<default-ref>` read is not a read of a file under `$SPECS_PATH`, so `inputs_read` (`create-ard.md:275`), which `phase-handoff` §2.2's stack test reads (`phase-handoff.md:224`), is unchanged: where the run's branch is cut does not move.
- **Why not the record's `## Threats` lines**, as the `to-fix` entry sketches. They put a free-text title before the state (`conformance-format.md:50`), so a state would be parsed out of free text; no run reads them back (`:78`); and an `open` line does not say whether its entry is `fix-code`. The entries are structured, and §7.8 already says which are open.
- **Why not designs alone.** The fact that the team will not build a decision is a person's ruling, and it is written only in a record's entry.
- **Rejected: a `require-on-main` gate on each design.** It adds a §3.4 row and a §3.7 site per folder, with a repair offer that can move the checkout mid-run — D's question 2, answered the same way.
- **Rejected: the working tree's records**, as §7.8's documentation runs read them. It needs one GIT-G1 edit, not three, but each record then joins `inputs_read` and can change where the stack test cuts the run's branch, and an unlanded ruling would nominate (question 1).

### D2. Which threats are sent back — format §11, new

`workflows-core:threat-model-format` gains **§11, *Threats sent back to the architect***, the one statement of the rule, since `/create-ard` can load neither `dev-workflows` reference. It states exactly what is read of each source; everything else in either file is not read.

For each live threat of the model that the check did not find stale, `<ref>` being `[[<K>]] [TH#N]` composed by the run from its own key for the folder and the threat's own id:

1. **`returned`** — its Disposition has a deferred part (`Deferred to design: `, or `; the rest deferred to design: `); no live entry of a design read answers it with a Disposition opening `Mitigated — Rule: `; and one answers it with a Disposition opening `Returned to the architect — `.
2. **`taken by no design`** — the same, save that no entry returns it and one answers it with a Disposition opening `Not this design's — `.
3. **`open on a decision`** — its Disposition opens `Mitigated by `, and for a pair of it a record read holds an entry that §7.8's *Which entries are open* leaves open, that its *mapping* maps to `document-as-code`, and that names that pair's decision: its heading's requirement id is, whole, `[AD#n] Rule` for a decision of `ard.md` or `[AD#n] Rule (ard-<area>.md)` for an area file's, and its `document:` line names, whole, that file and the key of the folder holding it.

An entry *answers* a threat where its `- **Answers:**` value is, whole, `<ref>`. An entry is a `### [DT#N]:` heading at the start of a line under the design's `## Threat review`, outside any fenced block, `N` matching `^[1-9][0-9]*$`, live where its block holds no `- **Withdrawn:**` list item at the start of a line. A threat takes the first kind that holds; a threat no entry and no record names is not sent back — `no design answers it` is the Dev's (`conformance.md:704`), and stays so.

- **Compose and compare, never extract.** The run builds `<ref>` and each requirement id from what it holds — its key, the model's ids, the pairs of the model's own Disposition — and compares whole. No key, id or path is taken out of a design or a record, save a `[DT#N]` or `[DD#n]` read at its heading's fixed position and shown, never resolved.
- **It is a nomination.** A record may be older than the code, and a design under the PRD may not have landed. So §11 decides only who is asked; the question says what each source said and when (the record's `Run:` date), and *Keep it as it stands* is always an answer (D3).
- **Two statements of one rule.** Kinds 1 and 2 restate, for a model's own run, what `/conformance` Phase 5's *the deferred part* computes (`conformance.md:489`). A rules invariant names the pair, changed together; `/conformance` does not cite §11, since beside an older `workflows-core` it would lose its states.
- **The two `dev-workflows` formats name their new reader**: `design-format` section 15 and `conformance-format` §6 each gain the sentence the latter already carries for `/release-notes` — the fields §11 reads, and that a change to one is a change to §11 too.

### D3. How each is put — a widening of step 7, and two new arrays at step 3

No new path. The four-option question and the `redisposed` state already exist; step 3 gains the entry point and step 7 a third population, beside the stale threats and the acceptances past their date.

**Step 3**, its text listing each threat sent back with its kind:

| The check finds | Threats sent back | `choices:` |
|---|---|---|
| no stale threat | none | `["Refine the threat model (Recommended)", "Leave it as it is"]` — today's |
| a stale threat | none | `["Refine the threat model (Recommended)", "Re-dispose only the stale threats"]` — today's |
| no stale threat | one or more | `["Refine the threat model (Recommended)", "Re-dispose only the threats sent back", "Leave it as it is"]` |
| a stale threat | one or more | `["Refine the threat model (Recommended)", "Re-dispose only the stale threats and those sent back"]` |

Each new *Re-dispose only …* option → `state: redisposed`, steps 7 to 9, no dispatch and no walk, as today's. *Leave it as it is* stays where no threat is stale: a threat sent back is not wrong, as a stale one is; the report names each one left.

**Step 7**, on `refined` and `redisposed`: each threat sent back that is not in `stale` takes `choices: ["Re-dispose it", "Keep it as it stands"]`, its text naming the threat, its current Disposition, its kind and what sent it back (D5), and saying no option is recommended. *Keep it as it stands* changes nothing. *Re-dispose it* puts step 7's four-option question, as for a threat stale on its Disposition — the sentence the acceptance paragraph already uses (`create-ard.md:885`):

| Answer | What it does to the threat |
|---|---|
| *Record an [AD#N] for it* | confirms a live decision the architect names, or grills a new one, as step 6 does; the Disposition becomes `Mitigated by <pair>`, with `; the rest deferred to design: <what>` where the grill leaves a rest |
| *Defer to design* | `Deferred to design: <what the design must answer>` — the current text offered to keep or replace, so the architect's answer to the Dev is the reworded question; no note field is added to the format |
| *Accept the risk* | owner and reason, then the review horizon, as step 6 asks; `Accepted — <owner>; <reason>; review by <date>`; the architect alone |
| *Not a threat — withdraw it* | the reason, then `- **Withdrawn:** <reason>` |

Each of the first three is a re-disposition: the threat keeps its `[TH#N]` (format §5). A change to its Where or to what its Threat line means is a supersession, and stays a correction at step 9's gate, which the question's text says. Free text is normalised into the array or asked again, as step 6's. The arrays are step 7's own, verbatim, so `workflows-core:escalation-rules`' picker vocabulary gains nothing.

- **A stale threat that was also sent back** is step 7's stale question alone; its text adds what sent it back.
- **Why two questions, not one.** The acceptance walk already does it, an explicit *Keep* is honest where nothing forces a change, and the four-option array has no room for a fifth.
- **Rejected: a dedicated array** with *Keep it deferred* and *Supersede it*. It would be a second vocabulary for the same four dispositions, and a supersession needs a typed Where, which step 9 already handles.
- **A limit, stated.** The format has three exclusive forms, so accepting a threat that reads `Mitigated by <pair>; the rest deferred …` drops its pairs. The question's text quotes the Disposition it replaces; an architect who wants both supersedes it into two threats at step 9.

### D4. The threat open on a decision is listed, with the same question

Its exit in D's words is "supersede that decision", which is ordinary ARD work. Two things follow, and the intake serves both.

- **Supersede the decision** — in Phase 4's grill, or as a correction to the ARD draft at step 9, which that gate already applies in place (`create-ard.md:905`). The threat then fails format §6's test 3, step 8's check finds it, and the stale walk puts it. Nothing new is needed but the telling: the question's text names the pair, the entry as `<KEY>/[DD#n]` with its decision and status, and says this.
- **Keep the decision and re-dispose the threat** — accept the risk, defer it, or rest it on another decision. This is the gap: only the architect accepts a risk, only in the model, and no question reached a threat that is not stale.

So it is listed and put as D3 puts any. **Rejected: offering it as a path only** — a line saying "supersede that decision". It leaves an architect who will not supersede with no way to accept the risk but a free-text correction, and question 1's alternative is exactly this.

### D5. Untrusted input: shown once, copied nowhere

Design text and record text are data. The bounds are structural:

- **Nothing read from either is written** — into the model, an ARD draft, `threat_model.report`, a pull-request body or any file. A `Deferred to design:` text is the architect's typed or confirmed answer, drafted from the model's own threat; a reason for acceptance or withdrawal is typed.
- **Nothing read from either reaches an agent.** `threat-modeler`'s brief keeps its eleven fields (`create-ard.md:826`) and `ard-reviewer`'s its own; the reply contracts do not change. An agent sees a re-disposed threat only as the model states it.
- **What is shown**, in a question's text alone: the entry as `[[<design's key>]] design.md [DT#N]`, the key the run's own for that folder; its kind in fixed words; and its reason — the text after `Returned to the architect — ` or `Not this design's — ` — as one line, by format §9's *Every value is one line*. For a record entry: `<KEY>/[DD#n]`, its `decision:` and `status:` where each is, whole, one of the format's values, and the record's `Run:` date; never its `shipped:` or `rationale:`.
- **The backstop, at its strictest.** A reason holding a match of either of format §9's two patterns is not shown: the text reads `its reason withheld: it held a security finding id or register path`. Here nothing was "given", so every match is withheld.
- **The report and the handoff carry keys, ids and fixed words only**, as D's `body_facts` does.
- **No path or id is built from them** (D2).

### D6. A returned threat that answers none of the model's

A Dev may return a threat the design's own interfaces add: `Answers: —` (`design-format.md:329`). It names no threat of the model, so no question can be put about one.

**It is listed, never converted.** Where a design read holds a live `Returned` entry whose `Answers` is `—`, step 3's text and the report name it — `[[<design's key>]] design.md [DT#N]`, with its Threat line and reason shown under D5's bounds — and say that *Refine the threat model* is where the architect adds a threat of their own (step 6's *The PA's own threats*), typed by them. The run copies nothing from it and makes no link: the design's entry stays until the Dev withdraws it, as C has it. **Rejected: turning it into a candidate** — it would write a Dev's, or an agent's, text into the architect's file, which D5 forbids (question 3).

### D7. Identity and the design side

`/create-ard` writes no design: the design is the Dev's.

- **The `Returned` entry stands as it is.** It is bound; only `/design` re-disposes or withdraws it.
- **A later `/design` run sees the change** by what C built: the design's lineage record shows it stale once the model's threat changes; a threat still deferred is put again from the entry, with the model's reworded question beside the earlier reason (`design.md:556`); and one no longer live and deferred has its entry proposed for withdrawal, naming the new disposition (C's D4). No edit to `/design`.
- **A later `/conformance` run sees it** from the default branch's model: `Mitigated by` → its mitigated part's state; `Accepted` → `accepted`; withdrawn → no line. The design's old entry then stands alone (D8).
- **A limit, stated.** A threat the architect keeps deferred is still returned until the Dev's next `/design`, so the next refine puts it again; *Keep it as it stands* is one answer. **Rejected for now: suppressing it by the design's lineage record**, which would have `/create-ard` run a lineage check on a document it does not own. Logged in `to-fix.md`.

### D8. What `/conformance` and `next-phase-offer` now say

Three sentences become false or misleading when the intake lands, and are rewritten against what it enforces:

- **The three routes keep `/product-workflows:create-ard <KEY>` and lose their caveat** (`conformance.md:704`; `plugins/workflows-core/references/next-phase-offer.md:394`, with its generated part): a refine there lists the threat and puts it to the architect.
- **A stand-alone `Returned` entry whose reason is `it answers no live threat with a deferred part` goes to the Dev**, `/dev-workflows:design <KEY>`, the design's key: the architect has answered, and the entry is the Dev's to withdraw. Today it goes to the PA (`conformance.md:491`, `:704`), who could do nothing with it. Its state and the header's count are unchanged. Every other stand-alone reason keeps its route. This amends a route D shipped (question 2).
- **The pages**: `plugins/dev-workflows/docs/commands/conformance.md:120` ("Three states have no exit yet"), `plugins/product-workflows/docs/commands/create-ard.md:118` and `:169`, and `/design`'s page where it says what the architect does with a returned threat.

### D9. No regression

- **A folder with no model**, a model *Start fresh* discards, and a run with no component set never reach the read: steps 1, 2 and 4 are untouched.
- **A model with no threat sent back** gets today's two arrays, today's question text, today's step 7, draft, review, write, stamp and report. The run makes its `git show` reads and prints nothing for them, with one exception it owes `phase-handoff` §5 rule 2: the line naming a design the working tree holds and the default branch does not.
- **`source-truth` is loaded only** where a record stands at a known path and the model holds a live, non-stale threat whose Disposition opens `Mitigated by `.
- **One precondition, failing closed**, as B's and D's: where the loaded format holds no heading `## 11.` — an older `workflows-core` — the run reads no design and no record, prints `Threat model: threats sent back not read — update workflows-core`, and goes on as today.
- **Fixtures, as traced runs** (no harness executes command prose): no model; a model and no design; a returned threat, each of the four answers and *Keep*; a threat taken by no design; a threat open on a decision, with the decision superseded at step 9; a stale threat also sent back; a returned new threat; a design only in the working tree; a format with no §11; a reason holding a `SEC#n`.

### D10. Every site the change touches

- **Claim sweep, by subject, each counted before and after** (`.claude/rules/claim-sweep.md`, refinements 6 to 8). *What re-disposes a live threat that is not stale*: `conformance.md:704`, the two pages above, `next-phase-offer.md:394` and its part, `to-fix.md:201-206`, format §5's examples of a re-disposition (`:83`) and §6's "a refine lists it" (`:102`). *What a refine proposes*: `create-ard.md:813` ("a refine proposes only what this run's architecture adds and lists each acceptance past its review date"), the page. *What `/create-ard` reads*: the map line in `.claude/rules/product-workflows.md:42`; `conformance-format.md:163` and `phase-handoff.md:418`, the record's readers; `.claude/rules/workflows-core.md:32`, §7.8's consumers. *Where a returned threat goes*: `design-format.md:334`, `design.md:572`, C's and D's designs (history, left). The exclusivity probe runs over "only the stale", "only what", "no command".
- **`product-workflows`:** `create-ard.md` — step 3, step 7, the `threat_model` record (`report`), *Final report*; its page; `CHANGELOG.md`.
- **`workflows-core`:** the format (§11; §5 and §6's sentences; §9's opening, which lists what each command holds to it); `next-phase-offer` and its part; `phase-handoff` and its parts (below); pages; `CHANGELOG.md`.
- **`dev-workflows`:** `conformance.md` (`:704`, and the line above its handoff array, below); `design-format` section 15 and `conformance-format` §6 (their new reader); pages; `CHANGELOG.md`.
- **Rules files:** `.claude/rules/threat-model.md` — a new invariant (the intake: its two sources, the default branch, shown and never copied, the pair §11 makes with `/conformance`'s Phase 5), and invariants 4 and 8, which say what a refine and a stale line do; `.claude/rules/product-workflows.md` (the map line); `.claude/rules/workflows-core.md` (§7.8's consumers); `.claude/rules/dev-workflows-conformance.md` (the record's readers); the coupling file.
- **Untouched:** `threat-modeler`, `ard-reviewer`, `design.md`, `ready.md`, `pre-lint`, `lineage-kinds.json`, `escalation-rules`, `specs-repo-git`, every script and gate.

### D11. Versions and coupling

`workflows-core` and `product-workflows` each a minor; `dev-workflows` a minor, for D8's route. Three bullets, each naming the plugins to update together:

- **`product-workflows` beside an older `workflows-core`**: the format has no §11, so the run reads nothing sent back and says so (D9). Safe; update `workflows-core`.
- **`dev-workflows` or `workflows-core` beside an older `product-workflows`**: the report sends the architect to a `/create-ard` that lists nothing. This is the misleading direction, and nothing can detect it — update `product-workflows` with either.
- **`product-workflows` beside an older `dev-workflows`**: its report still says no command re-disposes such a threat, which is now false, and sends a re-disposed threat's old entry to the PA. Nothing breaks; update `dev-workflows`.

## The GIT-G1 edits

**Every one needs the maintainer's approval by name.** `specs-preflight`, `commit-artifacts`, `specs-repo-git`, `branch-check`, §3.4's table, §3.7's sites and `/create-ard`'s own handoff call (`create-ard.md:1010`: its `deliverable_paths`, arrays and body) are untouched. **No `require-on-main` caller is added or changed, and no §3.4 row**: the designs are read under §5 rule 2's existing sentence, and the record is advisory.

1. **`phase-handoff` §4.0, the `_conformance.md` register row** (`phase-handoff.md:418`): `/product-workflows:create-ard` joins the readers — from `<default-ref>` alone, at its Phase 4.3, the records at the known paths D1 names. A truth edit; "None runs `require-on-main` on it" and the class stand.
2. **`phase-handoff` §4.0, the advisory class's sentence on a reader that does not read the working copy** (`:403`): its first case, "`_conformance.md`'s PRD record, which `/dev-workflows:ready` reads on the default branch", gains `/create-ard`, which reads an Epic's record so too. A truth edit.
3. **`/dev-workflows:conformance`'s handoff call site**: the line it prints above the array for a reader of the default branch alone (`conformance.md:563`, `:579`) names `/create-ard`'s refine too, on an Epic run as on a PRD run. A truth edit that edit 2's rule obliges, at a command's handoff step.
4. **`phase-handoff` §5 rule 2** (`:628`): the sentence "`/dev-workflows:conformance` reads each `threat-model.md` so, at its Phase 1" gains the second consumer of that kind, `/create-ard` and the designs under its folder. A truth edit, and the one I could omit: the rule covers the read without it, and the sentence claims no exclusivity. Recommended, so the rule names every consumer that relies on it.

The regenerated `reference-parts/phase-handoff/` files follow edits 1, 2 and 4. **Under question 1's alternative** (no record read) the list is edit 4 alone.

## What is left to the builder

Step numbering inside steps 3 and 7; the wording of §11 and of each question's text; how `source-truth` §7.8 is loaded for the one test, and whether the builder measures `create-ard.md`'s load before and after; `threat_model.report`'s lines; the fixtures.

## Risks

- **`create-ard.md` is 220 KB and grows.** §11 holds the rule; the command's steps cite it. The builder measures.
- **A stale nomination.** A record older than the code, or a design under the PRD that has not landed, can nominate a threat that is already answered. The question shows the source and its date, and *Keep it as it stands* costs one answer.
- **Asked again.** D7's limit: a threat kept deferred is put on every refine until the Dev's `/design` runs.
- **Two statements of the deferred-part rule** (D2), held together only by a rules invariant.
- **An Epic-level run already reads the Epic's `design.md` from the working tree at Phase 2, with no gate I could find** (`create-ard.md:487`; no §3.4 row names it). **Assumption**: I read Phase 0's gates and §3.4 and found none; I did not trace every path. Logged, not fixed here.

## The `to-fix` and roadmap updates

- **`docs/superpowers/to-fix.md`**: the RETURNED-INTAKE entry (`:201-206`) is closed, naming this file and the versions the build releases; `:199` and `:242`, which introduce it, are reworded. Three entries are added: a threat kept deferred is put again until `/design` runs (D7); the three-form limit on accepting a partly mitigated threat (D3); and the Epic-level run's ungated read of `design.md` at Phase 2 (Risks).
- **The roadmap** (`docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md:103-104`): rows C and D each gain *Its follow-up, the intake of threats sent back, built as RETURNED-INTAKE:* this file, in the versions the build releases.

## Questions for the maintainer

1. **Does the intake read the conformance records, and so take in the threat open on a decision?** Recommended: **yes** — the entries, from `<default-ref>` alone, by `source-truth` §7.8's two rules (D1, D2, D4). **A yes approves GIT-G1 edits 1, 2 and 3 by name.** The alternative reads designs only: the two `unanswered` kinds are taken in, the `open` one keeps a line saying "supersede that decision", an architect who keeps the decision can accept the risk only by a free-text correction at step 9, and the GIT-G1 list falls to edit 4. A third way, the working tree's records, needs edit 1 alone but lets an unlanded ruling nominate and can move where the run's branch is cut.
2. **May this track change one route D shipped?** Recommended: **yes** — a stand-alone `Returned` entry behind a threat the architect has re-disposed goes to the Dev's `/dev-workflows:design`, not back to the PA (D8). Without it, `/conformance` keeps sending the architect to a `/create-ard` that has nothing left to ask.
3. **What becomes of a returned threat that answers none of the model's?** Recommended: **listed, never converted** (D6) — the architect adds a threat of their own, in their words. The alternatives are a candidate built from the design's text, which writes a Dev's text into the architect's file, or silence, which leaves `/conformance`'s line for it with no exit.
4. **GIT-G1 edit 4, by name.** Recommended: **approve** — one clause naming `/create-ard`'s design read in §5 rule 2, so the rule lists both consumers that execute no gate. Declined, the read still stands under the rule as written, and the sentence names one of two.

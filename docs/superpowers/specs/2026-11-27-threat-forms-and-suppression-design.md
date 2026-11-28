# THREE-FORMS and KEPT-PUT-AGAIN: a threat's decisions beside an accepted rest, and a suppression the refine owns

Date: 2026-11-27. Status: **approved by the maintainer on 2026-11-28, all four questions answered as recommended** (see *Questions only the maintainer can answer*, where each answer is recorded) — revision 2, after one builder check (a fresh Opus agent reading only this design and the files it cites), whose eighteen findings are folded in as *Revision 2* at the end lists. It designs the two open entries of `docs/superpowers/to-fix.md`'s *From RETURNED-INTAKE* that wait for a design batch: **THREE-FORMS** (`to-fix.md:248-252`) and **KEPT-PUT-AGAIN** (`to-fix.md:242-247`), the latter as fix batch B44 narrowed it to its suppression part. It builds on SEC-G2 B, C and D and on RETURNED-INTAKE as built, on `main` at `66154b2fb` (`workflows-core` 1.100.5, `product-workflows` 3.88.5, `dev-workflows` 4.71.4). Statements about the tree cite `file:line` at that commit. `create-ard.md`, `design.md` and `conformance.md` are the command files; *the format* is `plugins/workflows-core/references/threat-model-format.md`; *the intake* is `plugins/workflows-core/references/threat-intake.md`.

Every decision is written with a recommended answer and the alternatives weighed. The questions at the end are the calls only the maintainer can make; the rest are the author's, stated so they can be corrected.

## Intent

Two defects of the threat model's life after RETURNED-INTAKE.

**THREE-FORMS.** A Disposition takes exactly one of three forms (format `:69-72`), and the one that holds decisions — `Mitigated by <pair>[, <pair>…]`, optionally followed by `; the rest deferred to design: <what>` — has no way to say that the rest is accepted. So every re-disposition writes a whole new line, and a threat's live decisions go with the old one: *Defer to design* writes `Deferred to design: …` (`create-ard.md:950`, `:958`), *Accept the risk* writes `Accepted — …` (`:951`), and even *Record an [AD#N] for it* writes `Mitigated by <that pair>` (`:949`), keeping none of the pairs the threat already held. The fix is a form that keeps the pairs beside an accepted rest, and a re-disposition that asks before it drops a live decision.

**KEPT-PUT-AGAIN.** A threat sent back to the architect (`threat-intake.md:3`) that the architect answers *Keep it as it stands* — or re-disposes so that it is still sent back — is put to them again on every later refine, because what sent it back still sends it (`threat-intake.md:119`), and `/dev-workflows:conformance` keeps routing it to the architect (`conformance.md:906`). The fix is a record of the architect's answer in the document `/product-workflows:create-ard` owns — the model — compared, on a later refine, with what the refine already reads, so a threat is put again only once what sent it back has changed.

The two share a design because they share their readers, and because THREE-FORMS makes more answers that leave a threat sent back.

## What exists today

- **The three forms** (format `:69-72`) and **the bar** (`:73`); a re-disposition rewrites the Disposition line and keeps the id (`:83`).
- **Who rewrites a Disposition.** `/create-ard` Phase 4.3 step 7 — the stale walk (`create-ard.md:957-959`), the acceptance walk's *Re-dispose it* (`:961`) and the sent-back walk's *Re-dispose it* (`:963`); step 8's check, which puts a held stale threat to step 7's question (`:980`); step 9's corrections, typed whole (`:985`); Phase 5's model findings, whose Fix `ard-reviewer` gives as a re-disposition (`create-ard.md:1025`; `ard-reviewer.md:64`); and Phase 6 step 2's second check, with *Defer to design*, *Accept the risk* or *Name a live decision* (`create-ard.md:1057`). None of them keeps a pair the old line held. The sent-back walk's question text says *Defer to design* and *Accept the risk* "drop any pair the Disposition holds" (`:963`) — and says nothing of *Record*, which drops them too.
- **Where the pairs end.** Readers cut a Disposition's pairs at `; the rest deferred to design: `: the intake (`threat-intake.md:77`), pre-lint (`pre-lint.md:97`), and `/conformance`'s joins (`conformance.md:177`) and *The Rules a threat rests on* (`:181`), which name the form "with or without `; the rest deferred to design: …`". The format's check reads a `Mitigated by`'s pairs (format `:100`).
- **Who reads an acceptance.** `/conformance` rule 3 (`conformance.md:639`) and rule 1's exception for a faulted date (`:637`); the intake's same exception (`threat-intake.md:7`); pre-lint's acceptance shape (`pre-lint.md:96`); the acceptance walk (`create-ard.md:961`); `ard-reviewer`'s BLOCKER (`ard-reviewer.md:60`); `design-reviewer`'s MAJOR on a design that falsifies an accepted threat's reason (`design-reviewer.md:211`); `/create-ard`'s handoff, "each risk it accepts, with its owner and review date" (`create-ard.md:1090`, its `body_facts`).
- **`/design` classes a threat** `deferred`, `mitigated` or `accepted` by its Disposition's form (`design.md:319`), and words a moot entry's withdrawal by the threat's new form (`design.md:617`).
- **A Keep writes nothing.** *Keep it as it stands* changes nothing (`create-ard.md:963`), and a `redisposed` run that changed no threat writes no draft (`:965`; `threat-intake.md:121`). The intake's own text and report say each such threat is put again (`threat-intake.md:119`, `:123`), and `/conformance`'s routes and `next-phase-offer`'s say so too (`conformance.md:906`; `plugins/workflows-core/references/next-phase-offer.md:493`, generated into `plugins/workflows-core/reference-parts/next-phase-offer/dev.md:218`).
- **The model's lineage.** The kind table's `threat-model` row (`plugins/workflows-core/scripts/lineage-kinds.json:121-142`) compares each `### [TH#N]` item and each `## ` section's own text, and leaves out `## Engineering review` (`notes`) and `- [ ]` lines (`ignore_lines`). A design that read the model records it (SEC-G2 C, D2), and `/dev-workflows:implement` (`implement.md:447`) and `/conformance` (`conformance.md:137`) run `upstream-check` over designs, which walks on into the model. **So a line written into the model in a compared place reads every design that recorded the model as stale**, and `IMPLEMENT_UPSTREAM_STALE` asks the Dev about it.
- **The intake reads each design and record at `<default-ref>`** by `git show`, at a known path (`threat-intake.md:48`), and shows what it read only in a question's text: "Nothing read from a design or a record is written" (`:125`). `/create-ard` writes no `design.md` and no `_conformance.md` (`.claude/rules/threat-model.md:38`, invariant 8).
- **RETURNED-INTAKE's D6 rejected, for now, "suppression by the design's lineage record, which has `/create-ard` check a document it does not own"** (`docs/superpowers/specs/2026-11-16-returned-intake-design.md:150`).

### What was measured, and what could not be

- **The readers of a Disposition's form**: `command grep -rlE "rest deferred to design|Mitigated by |Accepted — |Deferred to design" plugins --exclude=CHANGELOG.md` prints 11 files: the format, the intake, `pre-lint.md`, `lineage.py` (its selftest fixture only), `create-ard.md`, `ard-reviewer.md`, the `/create-ard` page, `design.md`, `design-reviewer.md`, the `/design` page and `conformance.md`. Four more read a Disposition's text as data or a threat's state without naming a form: `threat-modeler.md`, `design-threat-modeler.md`, `next-phase-offer.md` (with its generated part) and the `/conformance` page (`command grep -rlE "Disposition" plugins/*/agents plugins/dev-workflows/docs`, read hit by hit). *The readers' changes* below takes each.
- **The examples that hold each form**, over every tracked file (`git ls-files | xargs grep -h -- '<form>'`): plain `Mitigated by` 3 lines (the format's example twice, `lineage.py:1800`), `Deferred to design:` 4 (the format, `lineage.py` twice, one of them a replacement string), `Accepted — ` 3 (the format, `lineage.py` twice), **`Mitigated by …; the rest deferred to design: ` 1, and it is the grammar line of `docs/superpowers/plans/2026-11-14-sec-g2-b-threat-model.md:150`, not an instance**. No file under `scripts/fixtures/` holds a threat model. So no shipped example or fixture holds form 1's remainder, and none holds `; the rest accepted — ` or a `## Answered when sent back` section.
- **Not measurable on this machine:** how many models, re-dispositions of a threat holding pairs, and *Keep* answers exist on the specs trees the family runs on. `$SPECS_PATH` here is a demo tree of two folders holding no `threat-model.md`, no `## Threat review` and no record `## Threats` (`grep -rl` over it prints nothing). RETURNED-INTAKE shipped on 2026-11-16 and has no live run recorded here. Each fix below serves a population this repository cannot count, and both are designed so that a tree with none of the new text reads exactly as today (*Migration and compatibility*).

## Goals

1. **A threat's live decisions survive a re-disposition**, unless the architect drops them on purpose.
2. **The architecture can mitigate part of a threat and accept the rest**, in one Disposition, with the acceptance's owner, reason and review date read wherever an acceptance is read today.
3. **A threat the architect has answered is not put to them again** until what sent it back changes — tested only from the model `/create-ard` owns and the designs and records its intake already reads.
4. **`/conformance` sends the architect only to a refine that will ask them something.**
5. **No regression**: a model holding only today's forms and no new section reads, checks, routes and lineage-compares exactly as today, under every reader.

## Non-goals

- **A new command, agent, id prefix, branch prefix, role or plugin dependency.**
- **Any change to `threat-modeler` or `design-threat-modeler`**: neither proposes an accepted rest, since the PA alone accepts a risk (SEC-G2 B, question 3).
- **A Disposition with both a deferred and an accepted rest** (D1).
- **Moving `/conformance` or `/design` onto the intake or format §10** — CONFORMANCE-ON-INTAKE and DESIGN-ON-S10 stay as logged.
- **Changing `/conformance` Phase 6's `/create-ard` line itself**, its two arms, or E3-NOT-LANDED's limit; D11 says where this design touches them.
- **Splitting Phase 4.3 out of `create-ard.md`** (PHASE-43-WEIGHT).

## Anti-goals

- **A second place a risk is accepted**: only the architect, only in `/create-ard`, only in the model — an accepted rest included.
- **A suppression read off a document `/create-ard` does not own** — no design's lineage record, no field `/design` or `/conformance` writes for this purpose, no write into either's file.
- **Free text from a design or a record written into the model**: the new section holds keys, ids, known-set values, dates and git object ids, each composed by the run or shape-tested (D7).
- **A suppression that fails toward silence**: every case it cannot test puts the threat again.

## Decisions — THREE-FORMS

### D1. The accepted rest is a second remainder of form 1, not a fourth form

Form 1 becomes, exactly:

```
Mitigated by <pair>[, <pair>…]
Mitigated by <pair>[, <pair>…]; the rest deferred to design: <what the design must answer>
Mitigated by <pair>[, <pair>…]; the rest accepted — <owner>; <reason>; review by <YYYY-MM-DD>
```

**One form with an optional remainder of two kinds.** The pairs come first, as today. Where anything follows them it is, whole, one remainder: `; the rest deferred to design: ` with a non-empty text after it, or `; the rest accepted — ` followed by an acceptance exactly as form 3 writes one after `Accepted — ` — an owner, `; `, a reason, `; review by `, a date. The accepted rest is an acceptance in every sense format §4 gives one: the PA alone writes it, it names its owner, reason and review date, and it is read wherever an acceptance is read (D4).

**Where the pairs end** — the one rule every reader takes: the pairs are the text after `Mitigated by `, up to `; the rest deferred to design: ` or `; the rest accepted — `, whichever comes first, where it holds either; otherwise the whole of it. A pair holds no `; ` — its ARD file is `ard.md` or a name in `workflows-core:addressing` §2's class, which admits no `;`, and a `[[<PRD-KEY>]]` holds a key of §1's grammar — so the first marker always ends the pairs. A Disposition holding neither marker is cut exactly as today, so no existing model reads differently (D5). Where the deferred text itself holds `; the rest accepted — `, the first marker wins and the whole tail is the deferred text.

**"Three forms" stays true.** Format §4, §10, `ard-reviewer` and `/design` each say a Disposition takes "exactly one of three forms", or "none of the three forms"; with the remainder inside form 1, every such sentence stays true, and the claim sweep (*Build order*) rewrites only the sentences that spell form 1 out.

**Alternatives weighed.**
- **A fourth form**, with the same syntax. Rejected: it adds nothing a reader can test, and turns "exactly one of three forms" into a sentence to rewrite in four files and two pages, each a copy the sweep must find.
- **Form 3 widened, accepted first** — `Accepted — <owner>; <reason>; review by <date>; mitigated in part by <pair>…`. Rejected: the pairs then follow free text, so no reader can cut them without parsing a reason; and an older `/conformance` would read the threat as plainly `accepted` by its rule 3 — a clean state, nothing listed. Pairs first, an older `/conformance` reads the threat's mitigated part as `not checked` (D5), which is listed. Either way it may join none of the pairs and offer *Accept as shipped* on their Rules; that is a coupling bullet's (D5), not a reason to choose.
- **A sixth field**, `- **Residual:** Accepted — …`, beside a plain `Mitigated by`. Rejected: "the five fields … every one present" and every reader's exactly-once test would gain a field; the Disposition would no longer be one line; and an older reader would silently read the threat as wholly mitigated and lose the acceptance's review date — silence, not a stale line.
- **Both remainders at once** (`…; the rest deferred to design: …; the rest accepted — …`). Rejected for now: a threat whose rest is part the design's and part accepted is better split into two threats by the architect, and no defect asks for it. Such a line takes none of the forms, so it is unreadable (format §10), never misread.

### D2. Every re-disposition asks before it drops a live decision

**Where it is asked.** Wherever a threat's Disposition is rewritten by a question — Phase 4.3 step 7's three walks, step 8's re-ask of a stale threat (step 7's question for a held one, step 6's for one this run recorded), Phase 5's model finding whose Fix the architect takes, and Phase 6 step 2 — and the answer is *Record an [AD#N] for it*, *Defer to design* or *Accept the risk* (or, at Phase 6 step 2, *Name a live decision that answers it*), and the threat's current Disposition holds one or more **live pairs** — pairs naming a decision that is live in the ARD file the pair names, read as format §6's test 3 reads one — the run asks once more, before writing:

- one live pair: `choices: ["Keep <the pair> beside it<recommended>", "Drop it — the new disposition stands alone"]`;
- two or more: `choices: ["Keep <the live pairs, joined by \", \"> beside it<recommended>", "Keep only some of them (you'll be prompted for which)", "Drop them — the new disposition stands alone"]`, *Keep only some of them* asking in plain text for the pairs to keep, each compared whole with one of the live pairs and asked again otherwise.

Its text names the threat, its current Disposition, which pairs are live, and — on a threat stale on its Disposition — which pairs fail test 3 and so go whatever the answer. **The marker** is written as `<recommended>`, as step 8 already writes one (`create-ard.md:979`): it resolves to ` (Recommended)` on the first option, and to nothing where a live pair is the decision of a record entry that sends the threat back as `open on a decision` (intake §3, kind 3) or where the threat is stale on its Where (below); there the text says no option is recommended and why — keeping a nominated pair keeps the threat open on that decision; a new Where may not be one the old decisions answer. A free-text answer is normalised into the array or asked again.

**A threat stale on its Where** (`create-ard.md:959`): its first three answers give the disposition to the new `[TH#M]` that supersedes it, and the old threat's live pairs are offered for that new threat's Disposition by the same question, no option marked. The old threat keeps its line, as a superseded threat does.

**The old remainder is never carried.** Whatever remainder the old line held — `; the rest deferred to design: …` or `; the rest accepted — …` — is replaced by what the answer writes: on *Record*, by the grill's rest (D3) or by none; on *Defer to design*, by the deferred rest; on *Accept the risk*, by the accepted rest. The question's text quotes the old remainder and says the answer replaces it. Where the answer is *Defer to design* and the old remainder was deferred, its text is offered to keep or replace, as step 7 offers a current deferred text today (`create-ard.md:963`); where the answer is *Accept the risk* and the old remainder was accepted, its owner and reason are offered to keep or replace — the model's own text, never a design's or a record's.

**What is written**, `<kept>` the pairs kept, in the order the old line held them:

| Answer | Kept | Disposition |
|---|---|---|
| *Record an [AD#N] for it* — a new or named decision `<new>` | any | `Mitigated by <kept>, <new>` (`<new>` once, where it is among `<kept>`), with the grill's rest, as step 6 writes one (D3) |
| *Defer to design* | some | `Mitigated by <kept>; the rest deferred to design: <what>` |
| *Accept the risk* | some | `Mitigated by <kept>; the rest accepted — <owner>; <reason>; review by <YYYY-MM-DD>` |
| any | none (*Drop*, or no live pair) | today's line |

Phase 6 step 2 adds no decision: keeping a live pair is no new decision, so its rule that no `[AD#N]` is recorded after the review holds. Step 9's corrections and Phase 5's manual fix notes are typed whole and need no question: a correction may write either remainder itself, held to the loaded format by pre-lint and the check like any correction.

**`ard-reviewer` is unchanged.** Its Fix vocabulary (`ard-reviewer.md:64`) stays as it is — at most three options, each a re-disposition, a supersession, a withdrawal or a correction — and D2's question follows whichever re-disposition the architect takes from it, so whether the pairs stay is decided in one place.

**The question's text at the sent-back walk** (`create-ard.md:963`; `threat-intake.md` §6) stops saying that *Defer to design* and *Accept the risk* drop any pair, and says instead that each of the first three answers asks whether to keep the live decisions.

**Alternatives weighed.**
- **Keep the live pairs by default, with no question.** Rejected: on a threat open on a decision (kind 3) the nominated pair is usually what the architect means to drop, and keeping it silently keeps the threat sent back.
- **One question per pair.** Rejected as costlier for the common case; *Keep only some of them* covers it.
- **Relabelling step 7's four options** ("Defer the rest to design — keeps its decisions"). Rejected: the array is full at four, and dropping every pair would then need a fifth.

### D3. An accepted rest can be written wherever a rest is left

At step 6, *Record an [AD#N] for it* writes `; the rest deferred to design: <what>` "where the candidate's `rest_deferred` or the grill leaves a rest" (`create-ard.md:949`). Where a rest is left, the run now asks `choices: ["Defer the rest to design<recommended>", "Accept the rest (you'll be prompted for the owner and reason)"]`, `<recommended>` resolving to ` (Recommended)` where the candidate's `rest_deferred` proposed it and to nothing otherwise, its text saying the PA alone accepts a risk. *Accept the rest* asks as step 6's *Accept the risk* does — owner and reason in plain text, then the review horizon — and writes `; the rest accepted — …`. The same question follows a step 7 *Record an [AD#N] for it* whose grill leaves a rest. `threat-modeler` is unchanged: it proposes only a deferred rest.

**Alternative:** the accepted rest only on re-disposition (D2). Rejected: a form the architect can reach only by re-disposing a threat they have just recorded would be an odd door, and the question costs one call only where a rest is left.

### D4. What every reader does with an accepted rest

| Reader | Today | With an accepted rest |
|---|---|---|
| Format §4 | three forms, form 1's remainder deferred only | D1's grammar and cut rule; *An acceptance* covers an accepted rest; the example gains one threat in the new remainder |
| Format §5 | a re-disposition rewrites the line | adds: a re-disposition may keep the threat's live pairs (`/create-ard`'s choice) |
| Format §6 | test 3 reads `Mitigated by`'s pairs; "an acceptance past its review date is not stale" | pairs cut by D1; the sentence covers an accepted rest |
| Format §10 | "its one Disposition takes none of the three forms §4 gives" | unchanged words; §4's forms now include the remainder |
| Intake §1 | unreadable, save an `Accepted — ` Disposition faulted for its review date alone | the exception also covers a Disposition whose accepted rest is faulted for its date alone |
| Intake §3 | the deferred part: opens `Deferred to design: ` or holds `; the rest deferred to design: `; kind 3: opens `Mitigated by ` | unchanged, and a sentence: an accepted rest is no deferred part, so a threat holding one is never kind 1 or 2, and may be kind 3 |
| Intake §4 | pairs up to `; the rest deferred to design: ` | D1's cut |
| Pre-lint *Threat model* | openings; the `Accepted — ` shape; pairs up to the deferred marker | the acceptance shape also binds an accepted rest; D1's cut |
| `/create-ard` step 3 | live threats by count and disposition | a threat mitigated with an accepted rest is counted apart, as `mitigated, the rest accepted` |
| `/create-ard` steps 6, 7, Phase 5, Phase 6 step 2 | — | D2 and D3 |
| `/create-ard` step 7, acceptance walk | each `Accepted — ` past its date | also each accepted rest past its date; *Renew it* rewrites the date inside the remainder, pairs and owner kept; *Re-dispose it* puts D2's question after the four-option one. A threat that is also sent back (kind 3) takes this question first; the sent-back walk then puts it only where this answer did not re-dispose it, so no threat is asked twice about one line |
| `/create-ard` step 8 | `## Inherited threats` copies a Disposition | unchanged: the copy is verbatim |
| `/create-ard` handoff `body_facts` | "each risk it accepts, with its owner and review date" | **no edit**: an accepted rest is a risk the model accepts; the builder confirms the run composes it so, and any wording change there is a GIT-G1 question (D11) |
| `ard-reviewer` | BLOCKER: more than one form, "`Mitigated by …; the rest deferred to design: …` is one form"; an acceptance missing a part | "and so is `Mitigated by …; the rest accepted — …`"; the acceptance BLOCKER covers an accepted rest; its Fix vocabulary unchanged (D2) |
| `/design` Phase 2.5 step 7 (and format §10, its twin under invariant 9) | `mitigated` for `Mitigated by …` with no deferred remainder | states `mitigated` for an accepted rest too: the design binds through the pairs and has nothing to answer; its list of forms, which the malformed test reads, gains the remainder |
| `/design` Phase 5 part 11, *Made moot* | `now mitigated in the ARD` | `now mitigated in the ARD, the rest accepted` where the Disposition holds an accepted rest |
| `design-reviewer` | MAJOR: a design that falsifies an accepted threat's reason | "an `accepted` threat, or a `mitigated` one whose Disposition holds an accepted rest" |
| `design-threat-modeler`, `threat-modeler` | the Disposition as data | unchanged |
| `/conformance` Phase 1 (b) step 8, *The Rules a threat rests on* | "with or without `; the rest deferred to design: …`" | "with or without `; the rest deferred to design: …` or `; the rest accepted — …`" — so the pairs are mitigations (no *Accept as shipped*) and Rules a threat rests on; **the second is a GIT-G1 reach change** (D11) |
| `/conformance` *Walk-only mitigations* | a Disposition in none of the three forms | unchanged words; an accepted rest faulted for its date alone is read as a faulted `Accepted — ` Disposition is read (see *A pre-existing ambiguity* below) |
| `/conformance` Phase 5 rule 1 | its faulted-date exception | covers an accepted rest faulted for its date alone, the threat going on to rule 4 |
| `/conformance` Phase 5 rule 4 | parts: mitigated, deferred; order `open` › `unanswered` › `not checked` › `verified` | a third part, **the accepted part**: `review due` or `accepted`, by rule 3's date test on the text after the Disposition's last `; review by `; the order becomes `open` › `unanswered` › `review due` › `not checked` › `accepted` › `verified`; where the two parts' states differ, the reason names the other part's |
| `conformance-format` §2 | the `## Threats` line and the `Threats:` header | unchanged form; one sentence that a threat mitigated with an accepted rest takes one state by Phase 5's order |
| Lineage | items compared by text | unchanged: a rewritten Disposition is a changed item, as today |

**Why that order.** `accepted` comes after `not checked` and before `verified`, so a threat whose pairs are verified and whose rest is accepted reads `accepted` — never `verified`, which SEC-G2 D keeps for a threat whose every part rests on a trace (its goal 1). `review due` comes before `not checked`: the date's passing is a fact the run established and has an owner's route (the PA's), while `not checked` is an absence the line's own mitigation verdicts already show. `unanswered` and the accepted part never meet, since an accepted rest has no deferred part. The header's eight counts and `/ready`'s rung, which reads `open` alone, are unchanged.

**A pre-existing ambiguity, logged.** `/conformance`'s *Walk-only mitigations* (`conformance.md:179`) makes every `[AD#n]` Rule of a folder walk-only where a threat's Disposition "takes none of format §4's three forms", while its rule 1 (`:637`) reads an `Accepted — ` Disposition faulted for its review date alone as readable. A literal reader takes such an acceptance as walk-only. This design does not settle it: it states an accepted rest's faulted date "as a faulted `Accepted — ` Disposition is read", so both follow one answer, and logs the question as **FAULTED-DATE-WALK-ONLY** in `to-fix.md`.

### D5. Migration and compatibility of the forms

**No migration.** A model holding only today's three forms reads exactly as before under every reader: D1's cut rule is today's wherever a line holds no `; the rest accepted — `, and no tracked example holds that string. A line written by hand before the build that happens to hold it would read as the new remainder — a string no command writes today.

**A precondition at the writer — one test for both fixes.** `/create-ard` offers D2's *Keep* and D3's *Accept the rest*, and reads or writes D6's section, only where the format it loaded holds a line that is, whole, `## 11. Threats answered when sent back` — one heading, landing in the same `workflows-core` release as the accepted rest, tested as `/create-ard` already tests §9's. Otherwise it runs as today, its question text still saying the pairs are dropped. So D2 and D3 write no line an older pre-lint, check or §10 would reject; a correction the architect types whole at step 9 or in Phase 5's notes may still write one, and is then held to the loaded format by pre-lint and the check like any other correction.

**Older readers of a model holding an accepted rest**, written by a teammate's newer install:

| Older plugin | What it does | Direction |
|---|---|---|
| `workflows-core` (format, intake, pre-lint) | its pair rule cuts at the deferred marker alone, so the last "pair" holds the remainder and names no decision: format §6's test 3 fails. `/conformance` takes rule 1 first — §10 finds the Disposition in none of the forms — so `unreadable`; `/design` runs the check (step 6) before its malformed test (step 7), so the threat is `stale`, left out of the review with its stale line; the intake does not test a stale threat; pre-lint MAJOR | loud, toward the architect |
| `dev-workflows` beside a newer `workflows-core` | `/design` classes it `mitigated` by its own list, which reads `Mitigated by …` with no deferred remainder so (`design.md:319`) — safe; `/conformance` loads the newer format, so the threat is readable, but its own step 8 names only the deferred remainder, so the pairs may join no requirement: the mitigated part reads `not checked`, **a pair's Rule may be offered *Accept as shipped***, and its rule 4 has no accepted part (`conformance.md:640`), so an accepted rest past its date reads `not checked`, never `review due`, and the PA is never routed to renew it | the misleading direction — a coupling bullet: update `dev-workflows` with `workflows-core` |
| `product-workflows` beside a newer `workflows-core` | its check and pre-lint read the line right; its step 7 drops pairs as today | today's defect, no worse |

## Decisions — KEPT-PUT-AGAIN

### D6. The record of an answer lives in the model, in a section of its own

`threat-model.md` gains an optional last section, **`## Answered when sent back`**, written by `/create-ard` alone, one bullet per threat the architect answered when it was sent back:

```markdown
## Answered when sent back

- [TH#2] — answered 2026-11-27 — [[ACME-90-02]] design.md [DT#3] blob 9f2c1e7a4b0d3c5e8f61a2b7c4d9e0f1a3b5c7d9
- [TH#5] — answered 2026-11-27 — [[ACME-90]] _conformance.md [DD#4] amend-document final, [[ACME-90-02]] _conformance.md [DD#2] amend-document proposed
```

**Its grammar** (format §11). The section runs from a line that is, whole, `## Answered when sent back` to the next `## ` heading or the end of the file. A **bullet** is a line matching, whole, `^- \[TH#([1-9][0-9]*)\] — answered ([0-9]{4}-[0-9]{2}-[0-9]{2}) — (.+)$`; its tail, split on `, `, is its **sources**, each matching, whole, one of:

```
^\[\[([A-Z][A-Z0-9_]*(-[0-9]+)+)\]\] design\.md \[DT#[1-9][0-9]*\] blob ([0-9a-f]{40}|[0-9a-f]{64})$
^\[\[([A-Z][A-Z0-9_]*(-[0-9]+)+)\]\] _conformance\.md \[DD#[1-9][0-9]*\] (amend-document|accept) (proposed|final)$
```

— the key in `workflows-core:addressing` §1's grammar, which holds no `, `; a record source only ever names an entry that nominates, so its decision and status are of the nominating values. A line in the section that is not a bullet in this form, or a bullet with a source in neither form, answers nothing. A reader takes out of a bullet only its `[TH#N]` and its date; every source it tests is one it composed itself and compares whole with the bullet's split tail.

It comes after `## Threats`, and after `## Inherited threats` on an Epic-level model. Its bullets are no threats: under no `### [TH#N]` heading, outside `## Threats`, so format §6, §10, pre-lint's per-threat checks and the lineage items regex never see them, and pre-lint's id-series rule already counts a `[TH#N]` cited outside a heading as a reference. The keys stand in the wikilink form, which pre-lint's auto-link check discards; a bare `<KEY>/[DD#n]` there would be an auto-link hit.

**Lineage leaves it out.** The kind table's `threat-model` row gains the section's heading under `notes` — the mechanism that row already uses for `## Engineering review` — so writing a bullet changes nothing any `upstream-check` compares: no design that recorded the model reads stale, and no `/implement` or `/conformance` run asks about it. Without that exclusion, every *Keep* would prompt every design under the model.

**Who reads it.** `/create-ard`'s intake, to suppress (D8); `/conformance`, to route (D10). `/design` and both proposing agents read nothing of it: `/design` reads a model's threats, and the agents get composed lines, never the file. **Two agents do read the file whole** — `ard-reviewer`, which reads the model end to end (`ard-reviewer.md:34`) as `/create-ard`'s Phase 5 dispatch hands it the draft (`create-ard.md:1025`), and `design-reviewer`, which reads each path *Threat model paths* names (`design-reviewer.md:49`, `:52`) — so the section's values reach both; D7 says what that relaxes. Each is told the section is the run's own record, data like every line of the model, and takes no finding. Pre-lint checks nothing in it. A model with no such section is a model in which nothing has been answered.

**Alternatives weighed.**
- **A list item in the threat's block**, `- **Kept:** <date> — <sources>`, after its five fields. Rejected: the threat block is a lineage item, so the line would read every recording design stale. The kind table's `ignore_fields` cannot leave it out as `lineage.py` stands: it matches `<name>:` with no `**`, at the item's own key column (`lineage.py:79`, `:153`), and a `### [TH#N]` heading's key column is 0 while a `- **Kept:**` line's is 2 (`_key_col`, `lineage.py:63`), so it would need a change to the script; the one row using the field today is a `- id:` item's (`lineage-kinds.json:162`); format §4, pre-lint and `ard-reviewer` would each learn a sixth list item; and an older `/create-ard`'s refine keeps a held threat's lines, so a *Kept:* line would survive beside a Disposition the older run rewrote. A section of its own is dropped whole by an older run's rebuild of named sections — the safe direction (*Migration and compatibility*).
- **A field in the record's entry.** Rejected: `/create-ard` writes no `_conformance.md` (invariant 8), whose "command is its only writer" (`conformance-format.md:5`); `/conformance` cannot know the architect answered unless it reads the model, which makes the model the source anyway; and it would cover kind 3 alone, never a design's returned entry.
- **A field in the design's entry.** Rejected for the same reasons: `/create-ard` writes no `design.md`.
- **The design's lineage record** — RETURNED-INTAKE's D6, rejected there. Still rejected: nothing about that objection has changed, and D7 takes from it the one property worth having — a design's change is what re-opens a threat — without reading `/design`'s record (D9).
- **No record: the status quo.** One question per threat per refine, and `/conformance` sends the architect to a refine that asks again the same question. It is the cost KEPT-PUT-AGAIN logs.

### D7. A bullet names each source that sent the threat back, by a fingerprint the refine can take again

A **source** is what intake §6's *What sent each kind* already names: a design's entry, for kinds 1 and 2, and a record's entry that nominates, for kind 3. A bullet names each source that still sends the threat back after the architect's answer, in the order the run found them, joined by `, `:

- **A design's entry**: `[[<KEY>]] design.md [DT#N] blob <id>` — `<KEY>` the run's own key for the design's folder; `[DT#N]` the entry's, shape-tested as intake §6 tests it; `<id>` the git blob id of that `design.md` as `<default-ref>` holds it, `git -C "$SPECS_PATH" rev-parse --verify --quiet "<default-ref>:./<path>"`, `<path>` the run's own path for the file — the same object the intake's `git show` reads — matching, whole, `^[0-9a-f]{40}$` or `^[0-9a-f]{64}$`. On a specs tree that is no git repository, `git hash-object --no-filters -- "$SPECS_PATH/<path>"` (it runs outside a repository; measured on git 2.53.0).
- **A record's entry**: `[[<KEY>]] _conformance.md [DD#n] <decision> <status>` — `<KEY>` the run's own key for the record's folder; `[DD#n]` shape-tested; `<decision>` and `<status>` the entry's, each one of the known values intake §4 lists.

**Why a design's blob.** A design changes on the default branch when the Dev's `/dev-workflows:design` lands a re-answer — the event that should put the threat to the architect again. Its entry's id does not change on a re-answer (a re-disposition keeps a `[DT#N]`), and its reason is free text the model may not hold. The blob id is git's, of a file the intake already reads at that ref; it interprets nothing in the design. It is conservative: any landed change to the design puts the threat again — one more question, never one missed.

**How often the blob moves — a systematic link, not noise.** Every landed `/design` run rewrites `design.md`, its lineage frontmatter at least (`plugins/workflows-core/references/document-lineage.md:25`, `:29`), so every such run moves the blob. And any change to the model outside the section — a re-disposition of any threat, D2's among them — reads every design that recorded the model stale, which prompts the Dev to re-run `/design`. A landed re-run then puts each threat that design returned to the architect again. That is the intended event, not an unrelated one: `/design` puts every threat a held `Returned` entry answers to the Dev again on each run (`design.md` Phase 5 part 11, *Put again*), so a landed re-run is a re-answer of each, even where the Dev's words did not change. Only a hand edit to a design is truly unrelated. The alternative — a fingerprint of the design without its frontmatter, or of the entry alone — would need a hashing program over text extracted from a design, and would keep suppressing a threat the Dev was just asked about and answered again in the same words. Question 2 carries the choice.

**A source that cannot be fingerprinted** — a `rev-parse` or `hash-object` that exits non-zero, or an id outside the shape — gives no bullet: the threat it sent back is written no bullet in this run, so the next refine puts it again. At `/conformance` (D10) the same failure leaves the PA's route standing.

**Why a record's entry fields, not its blob.** Every `/conformance` re-run rewrites the whole record and its `Run:` line, so a record's blob would put the threat again on every re-run. An entry carried forward keeps its `[DD#n]`, decision and status (`conformance-format` §5); a new ruling, a changed decision or a PRD run's confirming entry is a new or different source.

**Alternatives weighed.** The entry's id alone (misses a Dev's re-answer); a hash of the entry's text (finer, but a new hashing program over text extracted from a design, and a derived copy of free text in the model); the record's `Run:` date (re-puts on every re-run).

**What this relaxes — two rules, not one.** The intake's rule is that nothing read from a design or a record "is written … or reaches an agent" (`threat-intake.md:125`; RETURNED-INTAKE goal 4 and D5), and invariant 11 says the same — "never written into the model … nor briefed to `threat-modeler` or `ard-reviewer`" — under the title *shown and never kept* (`.claude/rules/threat-model.md:41`). Both become: nothing read from a design or a record is written or reaches an agent **save the keys, ids, known-set values and blob ids D7 names, written into the model's `## Answered when sent back` alone, and read there by whatever reads the model file** — `ard-reviewer` and `design-reviewer` (D6) — each value composed by the run or shape-tested: the values the run's report already carries, and git's object id. No free text, no title, no reason reaches the file or an agent. The invariant's title, its two sentences and the intake's sentence change together. That is a real change to an approved anti-goal, and question 2 asks for it.

**The alternative kept out of the recommendation**: brief each reviewer a copy of the model with the section removed — a temporary file at `/create-ard`'s Phase 5 dispatch and its *Prior threat model*, and another at each `/design` path *Threat model paths* names — so the "reaches an agent" half stands. It costs two copies in two commands, for values that carry nothing an agent could take as an instruction.

### D8. The test, and when a bullet is written

**The test (format §11, new).** A threat sent back is **answered already** where the model's `## Answered when sent back` holds exactly one bullet whose `[TH#N]` is, whole, the threat's id, that bullet is in D6's form, and **every source that sends the threat back on this run is, whole, one of the bullet's sources** — the same entry with an equal blob id, or the same entry with the same decision and status. A source the bullet does not name, or names with another blob, decision or status, means it is not answered already. A bullet's sources that no longer send the threat back change nothing, so a Dev who withdraws one of two returning entries does not re-open the threat. Each reader composes the sources from what it read, and compares whole; nothing is taken out of a bullet but its `[TH#N]` and its date, each shape-tested. A bullet not in the form answers nothing.

**At the refine** (intake §6, `/create-ard` step 3 and step 7):
- A threat answered already is **not put** — not in step 3's arrays, not in step 7's sent-back walk, on *Refine the threat model* or *Re-dispose only …* alike. Step 3's text names each, one line: `[TH#N] sent back as before — you answered it on <date>; not put again until what sent it back changes; to re-dispose it now, choose Refine the threat model and correct it at the confirmation gate`. Where every threat sent back is answered already, the arrays are the two of today's rows that have nothing sent back. The run's report names it `[TH#N] sent back — <kinds> — answered already <date> — <sources>`, `<sources>` in the forms the report already prints (`threat-intake.md:123`) — `[[<KEY>]] design.md [DT#N]` and `<KEY>/[DD#n]`, never a blob id.
- **Which threats get a bullet — one rule, applied to the model as the run finally writes it.** For each threat of `sent_back`, take its line as the run leaves it and apply intake §3's kinds to it again, against the sources `sent_back` holds — reading nothing again. Where it is still live and still takes a kind, and the run asked about it in any walk — the sent-back walk's *Keep it as it stands* or *Re-dispose it*, the stale walk, the acceptance walk (which puts a kind-3 threat with an accepted rest first, D4), a step 9 correction, a Phase 5 fix or a Phase 6 step 2 answer — it gets a bullet: today's UTC date and each source that still sends it back. Where it was answered already and the run did not touch its line, its bullet stands as it was, its date unchanged. Where it no longer takes a kind, is no longer live, or has a source D7 could not fingerprint, it gets no bullet.
- **One bullet per `[TH#N]`; liveness wins.** The section the run writes holds, for each threat, at most one bullet: the one the rule above gives, replacing any bullet the folder's file held for it; for a live threat the run did not find sent back at all, the bullet the file held, as it stood (a threat sent back again later by the same unchanged sources is still answered); for a superseded or withdrawn threat, none. A line not in D6's form is dropped, and the report names it by its position in the section.
- **When the section is composed.** At step 8, into the draft, so step 9 plays it back; and again, by the same rule, at Phase 6 step 3, just before the model is written, since Phase 5's fixes and Phase 6 step 2 can still re-dispose, supersede or withdraw a threat. On `left` the section stands as it is; under *Start fresh*'s discard it goes with the model.
- **The precondition** is D5's one test. `/create-ard` reads and writes the section only where the format it loaded holds the heading `## 11. Threats answered when sent back` and the intake was read (step 3's existing test). Otherwise — no such heading, no intake, an old one, a failed load — the section stands in the draft exactly as the folder's file holds it, nothing is suppressed, and every threat sent back is put as today.
- **What the run could not read decides nothing new**: where a listing failed, a source it missed sends nothing back on this run, as today (`threat-intake.md:26`), so it neither re-opens nor closes a threat; a threat with any source the bullet does not name is put again.
- **What the run holds for it.** `threat_model.sent_back` (`create-ard.md:862`) keeps every threat sent back, an answered-already one among them, marked so with its bullet's date — the walks skip a marked one — and gains, per design source, its blob id, and per record source, its `decision:`, its `status:` and the pair whose decision it names — D2's marker reads the last — each composed or shape-tested as above, so step 8 writes the bullets from the record and reads nothing again.
- **The `still deferred to design` line** (`threat-intake.md:123`) is printed as today, for an answered-already threat too, and now reads `[TH#N] still deferred to design — /dev-workflows:design <KEY> puts it to the Dev again; a refine puts it to you again once that design changes on the default branch`.
- **The `left` path at step 7 stays** (`create-ard.md:965`), its condition gaining "and gave no threat a new bullet": where the precondition fails, a *Keep* still writes nothing, so an all-*Keep* `redisposed` run must still end there; where it holds, a *Keep* gives a bullet, and the run goes on to steps 8 and 9 with a draft. Its printed line (`threat-intake.md:121`) and the intake's sentence that step 9 is put only where the run changes a threat's line or an ARD draft (`threat-intake.md:118`) each gain "or a bullet of `## Answered when sent back`".

**A limit.** A bullet is the architect's own file's text; a hand-written bullet with the right fingerprints silences a threat until its sources change. The model's pull request is the check, as for every other line of the model.

### D9. What changed since RETURNED-INTAKE's D6

D6 rejected suppression **by the design's lineage record**: `/create-ard` would read `/design`'s `upstreams:` block and judge, from what `/design` recorded, whether the Dev had answered since. D7 reads nothing `/design` records. The blob id is a property of the default branch's object at a path the intake already reads with `git show` (`threat-intake.md:48`); the suppression's own state — what was answered, against what — is in the model, which `/create-ard` owns and writes. What D6 left logged is closed without the read D6 refused.

### D10. `/conformance` stops sending the architect to a refine that will not ask

`/conformance` loads the format and reads the model from `<default-ref>` already (`conformance.md:167`), so it reads the section with it. Where the loaded format holds `## 11. Threats answered when sent back` (tested as `/conformance` tests §10's heading), for a threat's own line in one of the three states routed to the architect for being sent back — `unanswered — returned to the architect`, `unanswered — no design takes it`, and `open` on a decision the team will not build — it applies format §11's test to the sources it holds for that line:

- for the first, each in-scope entry answering the threat whose Disposition opens `Returned to the architect — `; for the second, each opening `Not this design's — `; each as `[[<KEY>]] design.md [DT#N]` with the blob id of its design at `<default-ref>` — the run's own path, by `git rev-parse` as D7 takes it, `git hash-object` on a specs tree that is no git repository;
- for the third, each entry of the record this run writes that is **on** a Rule one of the threat's pairs names and **nominates**, both by the tests Phase 6 already states for its `/create-ard` line (`conformance.md:759`) — the same entries the intake's kind 3 counts — as `[[<KEY>]] _conformance.md [DD#n] <decision> <status>`. An entry on a `[DT#N]` mitigation, or one that nominates nothing, is no source, as it is none at the refine.

**A source `/conformance` cannot fingerprint** — a `rev-parse` that exits non-zero, as for a design read from the working tree that the default branch does not hold, or an id outside the shape — makes the threat not answered already: the PA's route stands.

**Where the threat is answered already, the PA's route is not offered**: the line's route in `### Threats` and `### Next step` reads `answered by the architect <date> — /product-workflows:create-ard puts it again once what sent it back changes`, and every Dev route the line takes today stays — a returned threat's `/dev-workflows:design` on each design that returned it. So a kept `taken by no design` or `open` line names no command, as a PRD run's `not checked` names none: the architect has answered, and what remains is between the two roles. The state, the reason, the record's `## Threats` line and header, and `body_facts` are unchanged.

**Why this holds on an Epic run**, which sees fewer sources than a PRD-level refine: §11's test is a subset test, so the run that sees a new source — that Epic's own `/conformance` — routes the architect, and a run that sees only unchanged sources does not. `next-phase-offer`'s `dev` lane (`next-phase-offer.md:493`, and its generated part) says the same.

**Older and newer.** An older `workflows-core` has no §11: `/conformance` routes as today, the safe direction. A model only the working tree holds is never read by `/conformance` (step 4's `not landed`), so a section only the architect's clone holds leaves the PA route standing until it lands.

**Alternative:** keep the PA route with a qualifier. Rejected: goal 4 — the route would still send the architect to a run that asks nothing.

### D11. The GIT-G1 footprint, and the two pending E3 decisions

**One GIT-G1 edit, needing the maintainer's approval by name**: *The Rules a threat rests on* (`conformance.md:181`) — what Phase 6's `/product-workflows:create-ard` line tests — gains the accepted remainder beside the deferred one (D4). It adds no arm and changes no wording of the line (`:755-760`); it widens the set of Rules the line's arms read to the pairs of a threat with an accepted rest, which a refine reads as kind 3 like any `Mitigated by` threat's. Without it, a declined record holding an `amend-document` on such a pair would print no line, though a refine would see the decision only once the record merges.

**It is not independent of the intake.** Invariant 11 makes the intake's §4 test of an entry that names a pair's decision and nominates, and this paragraph of `/conformance`, two copies of one rule changed together (`.claude/rules/threat-model.md:41`). So the answer binds both. **On approval**, both take D1's cut. **On a decline**, *The Rules a threat rests on* stays as it is, and the intake's kind 3 takes the same narrower reading — a threat whose Disposition holds an accepted rest is never `open on a decision` — while D1's cut still serves format §6, pre-lint and `/conformance`'s step 8, so such a threat's pairs are still checked and still mitigations, never offered *Accept as shipped*. The cost of a decline is that a refine never sends such a threat back for an entry the team will not build; D2's kind-3 marker then never fires for it.

**No other GIT-G1 site changes.** `specs-preflight`, `commit-artifacts`, `specs-repo-git`, `phase-handoff` and its register rows, `/create-ard`'s handoff (its `body_facts` sentence already reads an accepted rest as a risk the model accepts — D4), and `/conformance`'s `body_facts` are untouched; a model whose only change is its new section rides `/create-ard`'s existing handoff, as a re-disposed model does.

**Narrowing E3's arm (a)** — pending with the maintainer. Arm (a) prints wherever the record holds an entry on a Rule a threat rests on decided `amend-document` or `accept`, whatever its state. D10's suppression adds a case where that line warns about nothing: an entry carried forward unchanged, which a bullet names, puts nothing at the next refine whether or not the record merges. This design proposes no condition for it; whatever narrowing the maintainer settles applies to the widened set of Rules too, and could, if the maintainer wishes, also leave out an entry a bullet names unchanged.

**E3-NOT-LANDED** — pending with the maintainer. Its limit — a model only the working tree holds makes no Rule one a threat rests on — applies unchanged to an accepted rest's pairs, and D10 adds the same limit for the section: `/conformance` never reads an unlanded section. Neither decision is taken here.

## The readers' changes, by plugin

- **`workflows-core`** — the format: §3 (the new section, optional, last), §4 (D1's grammar and cut, *An acceptance*, the example), §5 (a sentence on kept pairs), §6 (the cut; an accepted rest past its date is not stale), new **§11, *Threats answered when sent back*** (D6's form and lineage note, D7's sources and fingerprints, D8's test, the writer, the readers), §8 (the readers of the section). The intake: §1, §3, §4 (D4), §6 (D2's question text; D8's not-put rule, write rule, report outcome, `still deferred` line, `left` line and step-9 sentence; the value table's new rows — a blob id, and a bullet read back — and the relaxed rule of D7). Pre-lint's *Threat model* block (D4; the section checked for nothing). `lineage-kinds.json`'s `threat-model` row (`notes`, `_source`), and `lineage.py`'s selftest (*Test plan*). `next-phase-offer` and its generated part (D10). The references page.
- **`product-workflows`** — `create-ard.md`: Phase 4.3 step 3 (counts; the answered-already filter and line), step 6 (D3), step 7 (D2 in three walks; the acceptance walk; the sent-back walk's filter and text), step 8 (the section's rewrite), step 9 untouched, Phase 5's model-finding paragraph (D2), Phase 6 step 2 (D2), the Final report, the precondition (D5) beside the intake's existing one, `threat_model.sent_back`'s new fields (D8), the left path's condition (D8) and Phase 6 step 3's second composition of the section (D8). `ard-reviewer.md` (D4; the section is the run's record and takes no finding; its Fix vocabulary unchanged). The `/create-ard` page.
- **`dev-workflows`** — `conformance.md`: Phase 1 (b) step 8 and *The Rules a threat rests on* (D4, the latter under D11's approval), Phase 5 rules 1 and 4 (D4), `### Threats` and `### Next step` (D10). `design.md`: Phase 2.5 step 7 (D4, kept equal to format §10 under invariant 9) and Phase 5 part 11 (D4). `design-reviewer.md` (D4; the section takes no finding, D6). `conformance-format.md` §2 (one sentence). The `/conformance` and `/design` pages.
- **Rules and inventories** — `.claude/rules/threat-model.md` (authority paragraph: §11 and the new section; invariant 4's re-disposition; invariant 8 untouched; invariant 11's title, *shown and never kept*, and its "never written … nor briefed" sentence relaxed together, as D7 says). It holds 18,936 characters of its 20,000-character warning, so the plan measures first and moves text to `docs/maintainers/rationale.md` before adding. `.claude/rules/dev-workflows-conformance.md` (the routes); the coupling file (*Versions and coupling*). `CLAUDE.md`'s *Shared authorities* line — "a threat's fields and its one disposition" — stays true and is untouched.

**Untouched:** `threat-modeler`, `design-threat-modeler`, `ready.md`, `source-truth`, `escalation-rules` (the two new arrays are `/create-ard`'s own), `phase-handoff`, every script but `lineage.py`'s selftest, every gate.

## Migration and compatibility

- **No migration.** A model with only today's forms and no `## Answered when sent back` reads exactly as today under every reader (D5). Every threat sent back is put as today until the architect answers it once under the new build.
- **Versions.** A minor each for `workflows-core`, `product-workflows` and `dev-workflows`.
- **Coupling bullets**, each saying what breaks:
  - **`product-workflows` beside an older `workflows-core`**: no accepted rest offered, no section written or read (D5's precondition and §11's absence); today's behaviour, said in one line. Update `workflows-core`.
  - **`workflows-core` beside an older `dev-workflows`**: a model holding an accepted rest may have its pairs joined to nothing, a pair's Rule offered *Accept as shipped*, and an accepted rest past its date read `not checked`, never `review due`, so the PA is not routed to renew it — the misleading direction (D5); `/conformance` still routes a kept threat to the architect. Update `dev-workflows` with `workflows-core`.
  - **`workflows-core` beside an older `product-workflows`**: an older refine's rebuild drops the section (it rebuilds named sections, SEC-G2 C's D7 found), so every answered threat is put again — the safe direction — and its re-disposition still drops pairs. Update `product-workflows`.
  - **An older `workflows-core` on a teammate's machine** reading a model with the section: its lineage row compares the section's text, so each design that recorded the model before the section changed reads stale there, and `/implement` asks about it, until that machine updates. Update `workflows-core`.

## Test and live-check plan

No harness executes command prose, so each case is a traced run, as SEC-G2 D's D10 and RETURNED-INTAKE's fixtures were, plus the selftest and the live checks below.

- **`lineage.py` selftest** (two new cases): a model whose only change is a `## Answered when sent back` bullet compares as unchanged against a design's recorded copy; a threat whose Disposition gains `; the rest accepted — …` compares as changed.
- **Traced runs — THREE-FORMS:** a sent-back returned threat `Mitigated by ard.md [AD#2]; the rest deferred to design: X`, answered *Accept the risk* → *Keep* (`…; the rest accepted — …`) and → *Drop* (`Accepted — …`); the same with *Defer to design* (rest re-worded, pair kept); *Record an [AD#N] for it* naming a new decision with two live pairs and *Keep only some of them*; a threat stale on one of two pairs (the dead pair goes, D2's question lists only the live one); a kind-3 threat (no option marked); Phase 6 step 2's *Defer to design* with a live pair; step 6's *Accept the rest*; an accepted rest past its date at the acceptance walk (*Renew it* keeps the pairs); `/conformance` on an accepted rest with verified pairs (`accepted`), with the date passed (`review due`, the reason naming `verified`), and with a pair `open` (`open`); `/design` classing it `mitigated` and *Made moot* wording; pre-lint on a faulted accepted rest (MAJOR); an older `workflows-core` reading the line (`unreadable` at `/conformance`, `stale` by test 3 at `/design`, MAJOR at pre-lint); a threat stale on its Where whose new `[TH#M]` keeps the old live pairs; an old deferred remainder replaced on *Record* + *Keep*, the question quoting it.
- **Traced runs — KEPT-PUT-AGAIN:** *Keep* on a returned threat → a bullet with the design's blob; the next refine with the design unchanged → not put, step 3's rows for nothing sent back; the design re-landed → put again; a second design newly returning it → put again; a Dev withdrawing one of two returning entries → still not put; kind 3 *Keep* → a record bullet; a `/conformance` re-run carrying the entry forward → still not put; its decision changed → put again; a listing failure → put again; an old intake, or a format with no §11 → section kept as the file holds it, all put; an all-*Keep* `redisposed` run beside a format with no §11 → `state: left`; a threat put again and kept again → one bullet, the new one; an answered threat superseded at Phase 6 step 2 → its bullet dropped at Phase 6 step 3; a kind-3 threat with an accepted rest re-disposed at the acceptance walk → a bullet, and not put twice; `/conformance` on an answered returned threat (Dev route only), an answered `taken by no design` (no command), an unanswered one (PA route as today), and beside an older `workflows-core` (PA route as today); `upstream-check` on a design after a *Keep* reads it current.
- **Live checks** (`docs/superpowers/to-test-on-real-project.md`, a new section): on a specs copy with a PRD, an ARD and a model, run the RETURNED-INTAKE live check's setup (`to-test-on-real-project.md:231`), then — a refine answering *Keep*, a second refine asking nothing of it, `/dev-workflows:design` re-landing the returning design, a third refine putting it again; and a re-disposition to `…; the rest accepted — …` followed by `/dev-workflows:conformance` on the Epic, its line reading `accepted` and its Rule offered no *Accept as shipped*.

## Build order

1. **`workflows-core`** — the format (§3, §4, §5, §6, §8, §11, the example), the intake, pre-lint, the lineage row and selftest, `next-phase-offer` and its regenerated part, the references page, `CHANGELOG.md`. It lands first: the other two test for its sentences and fail closed without them.
2. **`product-workflows`** — `create-ard.md`, `ard-reviewer.md`, the page, `CHANGELOG.md`; the load of `create-ard.md` measured before and after (239,846 characters now; Phase 4.3 is 38,940).
3. **`dev-workflows`** — `conformance.md` (the GIT-G1 sentence only under D11's approval), `design.md`, `design-reviewer.md`, `conformance-format.md`, the pages, `CHANGELOG.md`.
4. **Rules, coupling, `to-fix.md`** — the rules files, measured first; the four coupling bullets above; THREE-FORMS and KEPT-PUT-AGAIN closed with this file and the versions; FAULTED-DATE-WALK-ONLY logged (D4); CONFORMANCE-ON-INTAKE's entry notes that §11's test is stated once, in the format, which `/conformance` cites.

**The claim sweep is by subject**, over refinement 4's scope, each count taken before and after (`.claude/rules/claim-sweep.md`), no hand list being the set: *the forms a Disposition takes, and where its pairs end*; *what a re-disposition does to a threat's pairs* (the "drop any pair" sentence and its page copy); *who reads an acceptance*; *when a threat sent back is put again* (the intake's two sentences, `create-ard.md`'s step 3 text, `conformance.md`'s Next step and E3 paragraph, `next-phase-offer` and its part, the `/create-ard` and `/conformance` pages, `to-fix.md`); *what is written from a design or a record* (the intake, invariant 11, RETURNED-INTAKE's notes are history and stay). The exclusivity probe runs over "nothing read", "never written", "changes nothing", "only the stale".

## Risks

- **A *Keep* now writes the model.** An answer that left a threat sent back cost nothing before; now it rides a review and a handoff, once, in exchange for every later question. `create-ard.md`'s step 3 text says so.
- **The blob moves on every landed `/design` run** (D7). Any change to the model outside the section reads its designs stale, a Dev who re-runs and lands `/design` moves the blob, and each threat that design returned is put to the architect once more — by design, since that run put each to the Dev again. A hand edit to a design does the same with no re-answer behind it. Both are one more question, the safe direction; how often they happen on real trees could not be measured here.
- **Three statements of the routing rule** — `conformance.md`, `next-phase-offer` and its part — and §11's test stated once, in the format.
- **`create-ard.md` grows** in a phase PHASE-43-WEIGHT already logs; the rules move to the format and the intake wherever they are rule and not flow.

## Questions only the maintainer can answer

**Answered on 2026-11-28: all four as recommended.** Q1 yes (D1–D3); Q2 yes, with the three things it brings (D6–D8); Q3 approved by name, so *The Rules a threat rests on* takes D1's cut and the intake's kind 3 with it (D11's approval branch); Q4 as recommended (D10). The alternatives below are kept as the record of what was weighed.

1. **THREE-FORMS — an accepted rest as form 1's second remainder, and a question before any live decision is dropped?** Recommended: **yes** — `Mitigated by <pairs>; the rest accepted — <owner>; <reason>; review by <date>` (D1), D2's keep question at every re-disposition, and D3's rest question where a rest is left. Alternatives: a fourth form of the same syntax; a separate `Residual:` field; keeping pairs by default with no question.
2. **KEPT-PUT-AGAIN — a `## Answered when sent back` section in the model, fingerprinted by the design's blob and the record entry's fields?** Recommended: **yes**, approving with it three things it brings (D6–D8): the relaxation of RETURNED-INTAKE's rule — and of invariant 11, title included — that nothing read from a design or a record "is written … or reaches an agent", to the keys, ids, known-set values and blob ids D7 names, written into that section alone and read there by `ard-reviewer` and `design-reviewer`, which read the model file; an answer that leaves a threat sent back now writing the model once; and the blob moving on every landed `/design` run, so a threat the Dev was asked about again is put to the architect again. Alternatives: brief each reviewer a copy without the section, keeping "reaches an agent" whole; fingerprint a design without its frontmatter (a hashing program, and a re-answer in the same words stays suppressed); a `Kept:` line inside the threat's block; the status quo.
3. **GIT-G1, by name: may *The Rules a threat rests on* — which `/conformance` Phase 6's `/create-ard` line tests — take a threat with an accepted rest?** Recommended: **approve** (D11). It adds no arm and no wording to the line. The answer also binds the intake's kind-3 test, its other copy under invariant 11: on a decline, such a threat is never sent back as open on a decision, and its pairs stay mitigations. It does not touch the pending narrowing of arm (a) or E3-NOT-LANDED, which this design leaves to you.
4. **What does `/conformance` route for a threat the architect has answered?** Recommended: **drop the PA's route, keep every Dev route the line takes today, and add none** — so an answered `taken by no design` or `open on a decision` line names no command (D10). Alternatives: keep the PA route with a qualifier; add a Dev route for `taken by no design`, to the design that said it is not its own.

## Revision 2 — the builder check, and what it changed

One fresh Opus agent read revision 1 (`ad04a7d16`) and only the files it cites, as a builder would, and returned eighteen findings: one that blocked the build, nine ambiguities and eight minor. It confirmed every `file:line` it checked — 50-odd citations across the format, the intake, pre-lint, the three commands, both reviewers, `next-phase-offer`, the lineage table and script, and the rules file — save that the nominate test it cited sits at `conformance.md:759`, used above. It did not check the pages, SEC-G2 C's finding that an older refine rebuilds named sections only, or whether `/create-ard`'s handoff `body_facts` is a GIT-G1 clause; those stay the plan's to confirm. How each finding was addressed:

- **1, blocking — the section's values reach two agents.** `ard-reviewer` reads the model end to end and `design-reviewer` reads each model path, so D7 now relaxes "reaches an agent" beside "is written", and invariant 11's title with them; D6 names both readers; question 2 carries it, with the stripped-copy alternative.
- **2 — two bullets for one threat.** D8: one bullet per `[TH#N]`, this run's replacing the old; liveness wins.
- **3 — the `left` path.** D8: it stays, its condition gaining "and gave no threat a new bullet"; the intake's step-9 sentence joins the sweep.
- **4 — `/conformance`'s kind-3 sources.** D10: only entries on a Rule a pair names that nominate, by `conformance.md:759`'s tests.
- **5 — question 3 binds the intake.** D11 and question 3 say what is built on approval and on a decline.
- **6 — the blob moves on every landed `/design` run.** D7 and *Risks* state it as the intended event; question 2 carries the frontmatter-free alternative.
- **7 — `ard-reviewer`'s Fix vocabulary.** Unchanged; D2's question alone decides.
- **8 — a threat stale on its Where.** D2: its new `[TH#M]` is offered the old live pairs, no option marked.
- **9 — the old remainder.** D2: never carried, quoted in the question, the model's own text offered back.
- **10 — corrections.** D5's claim narrowed to D2 and D3; a typed correction is held to the loaded format.
- **11 — `/design` beside an older `workflows-core`.** D5's table and the test plan: `stale` by test 3, not `malformed`.
- **12 — `review due` lost beside an older `dev-workflows`.** D5's table and the coupling bullet say so.
- **13 — an unmarked array.** D2 and D3 write `<recommended>`, as step 8 does.
- **14 — "still sent back" unstated.** D8: one rule, intake §3 re-applied to the line as the run leaves it, against held sources, for any threat asked about in any walk.
- **15 — a bullet outliving a later re-disposition.** D8: the section is composed again at Phase 6 step 3; step 3's line no longer points at a gate *Leave it as it is* never reaches.
- **16 — a source that cannot be fingerprinted.** D7 and D10: no bullet; the PA route stands.
- **17 — two precondition tests.** D5 and D8: one, the §11 heading.
- **18 — the bullet's grammar.** D6 gives its regexes and the section's extent; D8 keeps the report's source forms, blob-free.

Of the four questions, findings 1 and 6 were folded into question 2 and finding 5 into question 3; the builder judged questions 1, 2 and 4 the maintainer's, and raised no fifth.

# THREE-FORMS and KEPT-PUT-AGAIN: a threat's decisions beside an accepted rest, and a suppression the refine owns

Date: 2026-11-27. Status: **draft, for the maintainer.** It designs the two open entries of `docs/superpowers/to-fix.md`'s *From RETURNED-INTAKE* that wait for a design batch: **THREE-FORMS** (`to-fix.md:248-252`) and **KEPT-PUT-AGAIN** (`to-fix.md:242-247`), the latter as fix batch B44 narrowed it to its suppression part. It builds on SEC-G2 B, C and D and on RETURNED-INTAKE as built, on `main` at `66154b2fb` (`workflows-core` 1.100.5, `product-workflows` 3.88.5, `dev-workflows` 4.71.4). Statements about the tree cite `file:line` at that commit. `create-ard.md`, `design.md` and `conformance.md` are the command files; *the format* is `plugins/workflows-core/references/threat-model-format.md`; *the intake* is `plugins/workflows-core/references/threat-intake.md`.

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

- one live pair: `choices: ["Keep <the pair> beside it (Recommended)", "Drop it — the new disposition stands alone"]`;
- two or more: `choices: ["Keep <the live pairs, joined by \", \"> beside it (Recommended)", "Keep only some of them (you'll be prompted for which)", "Drop them — the new disposition stands alone"]`, *Keep only some of them* asking in plain text for the pairs to keep, each compared whole with one of the live pairs and asked again otherwise.

Its text names the threat, its current Disposition, which pairs are live, and — on a threat stale on its Disposition — which pairs fail test 3 and so go whatever the answer. **The marker:** ` (Recommended)` on the first option, save where a live pair is the decision of a record entry that sends the threat back as `open on a decision` (intake §3, kind 3): there no option is marked, and the text says that keeping that pair keeps the threat open on that decision. A free-text answer is normalised into the array or asked again.

**What is written**, `<kept>` the pairs kept, in the order the old line held them:

| Answer | Kept | Disposition |
|---|---|---|
| *Record an [AD#N] for it* — a new or named decision `<new>` | any | `Mitigated by <kept>, <new>` (`<new>` once, where it is among `<kept>`), with the grill's rest, as step 6 writes one (D3) |
| *Defer to design* | some | `Mitigated by <kept>; the rest deferred to design: <what>` |
| *Accept the risk* | some | `Mitigated by <kept>; the rest accepted — <owner>; <reason>; review by <YYYY-MM-DD>` |
| any | none (*Drop*, or no live pair) | today's line |

Phase 6 step 2 adds no decision: keeping a live pair is no new decision, so its rule that no `[AD#N]` is recorded after the review holds. Step 9's corrections and Phase 5's manual fix notes are typed whole and need no question: a correction may write either remainder itself.

**`ard-reviewer`'s Fix vocabulary** (`ard-reviewer.md:64`) gains "each keeping the threat's live pairs beside it, as `Mitigated by <pairs>; the rest deferred to design: …` or `…; the rest accepted — …`, where the architect so chooses" — the options it already gives the architect, never an edit already settled.

**The question's text at the sent-back walk** (`create-ard.md:963`; `threat-intake.md` §6) stops saying that *Defer to design* and *Accept the risk* drop any pair, and says instead that each of the first three answers asks whether to keep the live decisions.

**Alternatives weighed.**
- **Keep the live pairs by default, with no question.** Rejected: on a threat open on a decision (kind 3) the nominated pair is usually what the architect means to drop, and keeping it silently keeps the threat sent back.
- **One question per pair.** Rejected as costlier for the common case; *Keep only some of them* covers it.
- **Relabelling step 7's four options** ("Defer the rest to design — keeps its decisions"). Rejected: the array is full at four, and dropping every pair would then need a fifth.

### D3. An accepted rest can be written wherever a rest is left

At step 6, *Record an [AD#N] for it* writes `; the rest deferred to design: <what>` "where the candidate's `rest_deferred` or the grill leaves a rest" (`create-ard.md:949`). Where a rest is left, the run now asks `choices: ["Defer the rest to design", "Accept the rest (you'll be prompted for the owner and reason)"]`, ` (Recommended)` on the first where the candidate's `rest_deferred` proposed it and on neither otherwise, its text saying the PA alone accepts a risk. *Accept the rest* asks as step 6's *Accept the risk* does — owner and reason in plain text, then the review horizon — and writes `; the rest accepted — …`. The same question follows a step 7 *Record an [AD#N] for it* whose grill leaves a rest. `threat-modeler` is unchanged: it proposes only a deferred rest.

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
| `ard-reviewer` | BLOCKER: more than one form, "`Mitigated by …; the rest deferred to design: …` is one form"; an acceptance missing a part | "and so is `Mitigated by …; the rest accepted — …`"; the acceptance BLOCKER covers an accepted rest; D2's Fix vocabulary |
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

**A precondition at the writer.** `/create-ard` offers D2's *Keep* and D3's *Accept the rest* only where the format it loaded states the accepted rest — it tests for one fixed sentence of §4, named by the plan — and otherwise runs as today, its question text still saying the pairs are dropped. So a newer `product-workflows` beside an older `workflows-core` writes no line the older pre-lint, check and §10 would reject.

**Older readers of a model holding an accepted rest**, written by a teammate's newer install:

| Older plugin | What it does | Direction |
|---|---|---|
| `workflows-core` (format, intake, pre-lint) | §10 finds the Disposition in none of the forms: `unreadable` at `/conformance`, `malformed` at `/design`, not tested by the intake, MAJOR at pre-lint | loud, toward the architect |
| `dev-workflows` beside a newer `workflows-core` | `/design` classes it `mitigated` (safe); `/conformance` loads the newer format, so the threat is readable, but its own step 8 names only the deferred remainder, so the pairs may join no requirement: the mitigated part reads `not checked`, and **a pair's Rule may be offered *Accept as shipped*** | the misleading direction — a coupling bullet: update `dev-workflows` with `workflows-core` |
| `product-workflows` beside a newer `workflows-core` | its check and pre-lint read the line right; its step 7 drops pairs as today | today's defect, no worse |

## Decisions — KEPT-PUT-AGAIN

### D6. The record of an answer lives in the model, in a section of its own

`threat-model.md` gains an optional last section, **`## Answered when sent back`**, written by `/create-ard` alone, one bullet per threat the architect answered when it was sent back:

```markdown
## Answered when sent back

- [TH#2] — answered 2026-11-27 — [[ACME-90-02]] design.md [DT#3] blob 9f2c1e7a4b0d3c5e8f61a2b7c4d9e0f1a3b5c7d9
- [TH#5] — answered 2026-11-27 — [[ACME-90]] _conformance.md [DD#4] amend-document final, [[ACME-90-02]] _conformance.md [DD#2] amend-document proposed
```

It comes after `## Threats`, and after `## Inherited threats` on an Epic-level model. Its bullets are no threats: under no `### [TH#N]` heading, outside `## Threats`, so format §6, §10, pre-lint's per-threat checks and the lineage items regex never see them, and pre-lint's id-series rule already counts a `[TH#N]` cited outside a heading as a reference. The keys stand in the wikilink form, which pre-lint's auto-link check discards; a bare `<KEY>/[DD#n]` there would be an auto-link hit.

**Lineage leaves it out.** The kind table's `threat-model` row gains the section's heading under `notes` — the mechanism that row already uses for `## Engineering review` — so writing a bullet changes nothing any `upstream-check` compares: no design that recorded the model reads stale, and no `/implement` or `/conformance` run asks about it. Without that exclusion, every *Keep* would prompt every design under the model.

**Who reads it.** `/create-ard`'s intake, to suppress (D8); `/conformance`, to route (D10). `/design`, `design-reviewer` and both proposing agents read nothing of it. `ard-reviewer` is told it is the run's own record and takes no finding. Pre-lint checks nothing in it. A model with no such section is a model in which nothing has been answered.

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

**Why a design's blob.** A design changes on the default branch when the Dev's `/dev-workflows:design` lands a re-answer — the event that should put the threat to the architect again. Its entry's id does not change on a re-answer (a re-disposition keeps a `[DT#N]`), and its reason is free text the model may not hold. The blob id is git's, of a file the intake already reads at that ref; it interprets nothing in the design. It is conservative: any landed change to the design, related or not, puts the threat again — one more question, never one missed.

**Why a record's entry fields, not its blob.** Every `/conformance` re-run rewrites the whole record and its `Run:` line, so a record's blob would put the threat again on every re-run. An entry carried forward keeps its `[DD#n]`, decision and status (`conformance-format` §5); a new ruling, a changed decision or a PRD run's confirming entry is a new or different source.

**Alternatives weighed.** The entry's id alone (misses a Dev's re-answer); a hash of the entry's text (finer, but a new hashing program over text extracted from a design, and a derived copy of free text in the model); the record's `Run:` date (re-puts on every re-run).

**What this relaxes.** The intake's rule that nothing read from a design or a record is written (`threat-intake.md:125`; RETURNED-INTAKE goal 4 and D5) becomes: nothing read from a design or a record is written **save, into the model's `## Answered when sent back` alone, the keys, ids, known-set values and blob ids D7 names**, each composed by the run or shape-tested — the values the run's report already carries, and git's object id. No free text, no title, no reason. That is a real change to an approved anti-goal, and question 2 asks for it.

### D8. The test, and when a bullet is written

**The test (format §11, new).** A threat sent back is **answered already** where the model's `## Answered when sent back` holds exactly one bullet whose `[TH#N]` is, whole, the threat's id, that bullet is in D6's form, and **every source that sends the threat back on this run is, whole, one of the bullet's sources** — the same entry with an equal blob id, or the same entry with the same decision and status. A source the bullet does not name, or names with another blob, decision or status, means it is not answered already. A bullet's sources that no longer send the threat back change nothing, so a Dev who withdraws one of two returning entries does not re-open the threat. Each reader composes the sources from what it read, and compares whole; nothing is taken out of a bullet but its `[TH#N]` and its date, each shape-tested. A bullet not in the form answers nothing.

**At the refine** (intake §6, `/create-ard` step 3 and step 7):
- A threat answered already is **not put** — not in step 3's arrays, not in step 7's sent-back walk, on *Refine the threat model* or *Re-dispose only …* alike. Step 3's text names each, one line: `[TH#N] sent back as before — you answered it on <date>; not put again until what sent it back changes; a correction at the confirmation gate re-disposes it`. Where every threat sent back is answered already, the arrays are the two of today's rows that have nothing sent back. The run's report names it `[TH#N] sent back — <kinds> — answered already <date> — <sources>`.
- A threat the run puts that the architect answers so that it is still sent back — *Keep it as it stands*; or a re-disposition after which it still takes a kind against the same sources, as a deferred re-disposition of a returned threat does, or D2's *Keep* of a nominated pair — gains a bullet: today's UTC date and each source that still sends it back, read off what the run already holds and never read again.
- **The section is rewritten at step 8**, on `refined` and `redisposed`: the bullets this run wrote; each bullet of a threat answered already, as it stood; each other bullet whose `[TH#N]` heads a live threat of the draft, as it stood; and none for a threat no longer live. A bullet not in the form is dropped, and the report names it by its position. On `left` the section stands as it is; under *Start fresh*'s discard it goes with the model.
- **The precondition.** `/create-ard` reads and writes the section only where the format it loaded holds the heading `## 11. Threats answered when sent back` and the intake was read (step 3's existing test). Otherwise — no such heading, no intake, an old one, a failed load — the section stands in the draft exactly as the folder's file holds it, nothing is suppressed, and every threat sent back is put as today.
- **What the run could not read decides nothing new**: where a listing failed, a source it missed sends nothing back on this run, as today (`threat-intake.md:26`), so it neither re-opens nor closes a threat; a threat with any source the bullet does not name is put again.
- **What the run holds for it.** `threat_model.sent_back` (`create-ard.md:862`) gains, per design source, its blob id, and per record source, its `decision:`, its `status:` and the pair whose decision it names — D2's marker reads the last — each composed or shape-tested as above, so step 8 writes the bullets from the record and reads nothing again.
- **The `still deferred to design` line** (`threat-intake.md:123`) is printed as today, for an answered-already threat too, and now reads `[TH#N] still deferred to design — /dev-workflows:design <KEY> puts it to the Dev again; a refine puts it to you again once that design changes on the default branch`.
- **The `left` path at step 7** (`create-ard.md:965`): an answer to a threat sent back now always writes a bullet or rewrites a line, so a `redisposed` run that put a threat sent back always sets a draft. The builder keeps the path as a guard or removes it, says which, and sweeps its printed line (`threat-intake.md:121`).

**A limit.** A bullet is the architect's own file's text; a hand-written bullet with the right fingerprints silences a threat until its sources change. The model's pull request is the check, as for every other line of the model.

### D9. What changed since RETURNED-INTAKE's D6

D6 rejected suppression **by the design's lineage record**: `/create-ard` would read `/design`'s `upstreams:` block and judge, from what `/design` recorded, whether the Dev had answered since. D7 reads nothing `/design` records. The blob id is a property of the default branch's object at a path the intake already reads with `git show` (`threat-intake.md:48`); the suppression's own state — what was answered, against what — is in the model, which `/create-ard` owns and writes. What D6 left logged is closed without the read D6 refused.

### D10. `/conformance` stops sending the architect to a refine that will not ask

`/conformance` loads the format and reads the model from `<default-ref>` already (`conformance.md:167`), so it reads the section with it. Where the loaded format holds `## 11. Threats answered when sent back` (tested as `/conformance` tests §10's heading), for a threat's own line in one of the three states routed to the architect for being sent back — `unanswered — returned to the architect`, `unanswered — no design takes it`, and `open` on a decision the team will not build — it applies format §11's test to the sources it holds for that line:

- for the first, each in-scope entry answering the threat whose Disposition opens `Returned to the architect — `; for the second, each opening `Not this design's — `; each as `[[<KEY>]] design.md [DT#N]` with the blob id of its design at `<default-ref>` — the run's own path, by `git rev-parse` as D7 takes it, `git hash-object` on a specs tree that is no git repository;
- for the third, each entry of the record this run writes that holds a mitigation of the threat open and is not, whole, `fix-code`, as `[[<KEY>]] _conformance.md [DD#n] <decision> <status>`.

**Where the threat is answered already, the PA's route is not offered**: the line's route in `### Threats` and `### Next step` reads `answered by the architect <date> — /product-workflows:create-ard puts it again once what sent it back changes`, and every Dev route the line takes today stays — a returned threat's `/dev-workflows:design` on each design that returned it. So a kept `taken by no design` or `open` line names no command, as a PRD run's `not checked` names none: the architect has answered, and what remains is between the two roles. The state, the reason, the record's `## Threats` line and header, and `body_facts` are unchanged.

**Why this holds on an Epic run**, which sees fewer sources than a PRD-level refine: §11's test is a subset test, so the run that sees a new source — that Epic's own `/conformance` — routes the architect, and a run that sees only unchanged sources does not. `next-phase-offer`'s `dev` lane (`next-phase-offer.md:493`, and its generated part) says the same.

**Older and newer.** An older `workflows-core` has no §11: `/conformance` routes as today, the safe direction. A model only the working tree holds is never read by `/conformance` (step 4's `not landed`), so a section only the architect's clone holds leaves the PA route standing until it lands.

**Alternative:** keep the PA route with a qualifier. Rejected: goal 4 — the route would still send the architect to a run that asks nothing.

### D11. The GIT-G1 footprint, and the two pending E3 decisions

**One GIT-G1 edit, needing the maintainer's approval by name**: *The Rules a threat rests on* (`conformance.md:181`) — what Phase 6's `/product-workflows:create-ard` line tests — gains the accepted remainder beside the deferred one (D4). It adds no arm and changes no wording of the line (`:755-760`); it widens the set of Rules the line's arms read to the pairs of a threat with an accepted rest, which a refine reads as kind 3 like any `Mitigated by` threat's. Without it, a declined record holding an `amend-document` on such a pair would print no line, though a refine would see the decision only once the record merges.

**No other GIT-G1 site changes.** `specs-preflight`, `commit-artifacts`, `specs-repo-git`, `phase-handoff` and its register rows, `/create-ard`'s handoff (its `body_facts` sentence already reads an accepted rest as a risk the model accepts — D4), and `/conformance`'s `body_facts` are untouched; a model whose only change is its new section rides `/create-ard`'s existing handoff, as a re-disposed model does.

**Narrowing E3's arm (a)** — pending with the maintainer. Arm (a) prints wherever the record holds an entry on a Rule a threat rests on decided `amend-document` or `accept`, whatever its state. D10's suppression adds a case where that line warns about nothing: an entry carried forward unchanged, which a bullet names, puts nothing at the next refine whether or not the record merges. This design proposes no condition for it; whatever narrowing the maintainer settles applies to the widened set of Rules too, and could, if the maintainer wishes, also leave out an entry a bullet names unchanged.

**E3-NOT-LANDED** — pending with the maintainer. Its limit — a model only the working tree holds makes no Rule one a threat rests on — applies unchanged to an accepted rest's pairs, and D10 adds the same limit for the section: `/conformance` never reads an unlanded section. Neither decision is taken here.

## The readers' changes, by plugin

- **`workflows-core`** — the format: §3 (the new section, optional, last), §4 (D1's grammar and cut, *An acceptance*, the example), §5 (a sentence on kept pairs), §6 (the cut; an accepted rest past its date is not stale), new **§11, *Threats answered when sent back*** (D6's form and lineage note, D7's sources and fingerprints, D8's test, the writer, the readers), §8 (the readers of the section). The intake: §1, §3, §4 (D4), §6 (D2's question text; D8's not-put rule, write rule, report outcome and `still deferred` line; the value table's new rows — a blob id, and a bullet read back — and the relaxed rule of D7). Pre-lint's *Threat model* block (D4; the section checked for nothing). `lineage-kinds.json`'s `threat-model` row (`notes`, `_source`), and `lineage.py`'s selftest (*Test plan*). `next-phase-offer` and its generated part (D10). The references page.
- **`product-workflows`** — `create-ard.md`: Phase 4.3 step 3 (counts; the answered-already filter and line), step 6 (D3), step 7 (D2 in three walks; the acceptance walk; the sent-back walk's filter and text), step 8 (the section's rewrite), step 9 untouched, Phase 5's model-finding paragraph (D2), Phase 6 step 2 (D2), the Final report, and the precondition (D5) beside the intake's existing one. `ard-reviewer.md` (D4; D2's Fix vocabulary; the section takes no finding). The `/create-ard` page.
- **`dev-workflows`** — `conformance.md`: Phase 1 (b) step 8 and *The Rules a threat rests on* (D4, the latter under D11's approval), Phase 5 rules 1 and 4 (D4), `### Threats` and `### Next step` (D10). `design.md`: Phase 2.5 step 7 (D4, kept equal to format §10 under invariant 9) and Phase 5 part 11 (D4). `design-reviewer.md` (D4). `conformance-format.md` §2 (one sentence). The `/conformance` and `/design` pages.
- **Rules and inventories** — `.claude/rules/threat-model.md` (authority paragraph: §11 and the new section; invariant 4's re-disposition; invariant 8 untouched; invariant 11's "never written" sentence relaxed as D7 says). It holds 18,936 characters of its 20,000-character warning, so the plan measures first and moves text to `docs/maintainers/rationale.md` before adding. `.claude/rules/dev-workflows-conformance.md` (the routes); the coupling file (*Versions and coupling*). `CLAUDE.md`'s *Shared authorities* line — "a threat's fields and its one disposition" — stays true and is untouched.

**Untouched:** `threat-modeler`, `design-threat-modeler`, `ready.md`, `source-truth`, `escalation-rules` (the two new arrays are `/create-ard`'s own), `phase-handoff`, every script but `lineage.py`'s selftest, every gate.

## Migration and compatibility

- **No migration.** A model with only today's forms and no `## Answered when sent back` reads exactly as today under every reader (D5). Every threat sent back is put as today until the architect answers it once under the new build.
- **Versions.** A minor each for `workflows-core`, `product-workflows` and `dev-workflows`.
- **Coupling bullets**, each saying what breaks:
  - **`product-workflows` beside an older `workflows-core`**: no accepted rest offered, no section written or read (D5's precondition and §11's absence); today's behaviour, said in one line. Update `workflows-core`.
  - **`workflows-core` beside an older `dev-workflows`**: a model holding an accepted rest may have its pairs joined to nothing, and a pair's Rule offered *Accept as shipped* — the misleading direction (D5); `/conformance` still routes a kept threat to the architect. Update `dev-workflows` with `workflows-core`.
  - **`workflows-core` beside an older `product-workflows`**: an older refine's rebuild drops the section (it rebuilds named sections, SEC-G2 C's D7 found), so every answered threat is put again — the safe direction — and its re-disposition still drops pairs. Update `product-workflows`.
  - **An older `workflows-core` on a teammate's machine** reading a model with the section: its lineage row compares the section's text, so each design that recorded the model before the section changed reads stale there, and `/implement` asks about it, until that machine updates. Update `workflows-core`.

## Test and live-check plan

No harness executes command prose, so each case is a traced run, as SEC-G2 D's D10 and RETURNED-INTAKE's fixtures were, plus the selftest and the live checks below.

- **`lineage.py` selftest** (two new cases): a model whose only change is a `## Answered when sent back` bullet compares as unchanged against a design's recorded copy; a threat whose Disposition gains `; the rest accepted — …` compares as changed.
- **Traced runs — THREE-FORMS:** a sent-back returned threat `Mitigated by ard.md [AD#2]; the rest deferred to design: X`, answered *Accept the risk* → *Keep* (`…; the rest accepted — …`) and → *Drop* (`Accepted — …`); the same with *Defer to design* (rest re-worded, pair kept); *Record an [AD#N] for it* naming a new decision with two live pairs and *Keep only some of them*; a threat stale on one of two pairs (the dead pair goes, D2's question lists only the live one); a kind-3 threat (no option marked); Phase 6 step 2's *Defer to design* with a live pair; step 6's *Accept the rest*; an accepted rest past its date at the acceptance walk (*Renew it* keeps the pairs); `/conformance` on an accepted rest with verified pairs (`accepted`), with the date passed (`review due`, the reason naming `verified`), and with a pair `open` (`open`); `/design` classing it `mitigated` and *Made moot* wording; pre-lint on a faulted accepted rest (MAJOR); an older `workflows-core` reading the line (`unreadable` / `malformed`).
- **Traced runs — KEPT-PUT-AGAIN:** *Keep* on a returned threat → a bullet with the design's blob; the next refine with the design unchanged → not put, step 3's rows for nothing sent back; the design re-landed → put again; a second design newly returning it → put again; a Dev withdrawing one of two returning entries → still not put; kind 3 *Keep* → a record bullet; a `/conformance` re-run carrying the entry forward → still not put; its decision changed → put again; a listing failure → put again; an old intake → section kept, all put; `/conformance` on an answered returned threat (Dev route only), an answered `taken by no design` (no command), an unanswered one (PA route as today), and beside an older `workflows-core` (PA route as today); `upstream-check` on a design after a *Keep* reads it current.
- **Live checks** (`docs/superpowers/to-test-on-real-project.md`, a new section): on a specs copy with a PRD, an ARD and a model, run the RETURNED-INTAKE live check's setup (`to-test-on-real-project.md:231`), then — a refine answering *Keep*, a second refine asking nothing of it, `/dev-workflows:design` re-landing the returning design, a third refine putting it again; and a re-disposition to `…; the rest accepted — …` followed by `/dev-workflows:conformance` on the Epic, its line reading `accepted` and its Rule offered no *Accept as shipped*.

## Build order

1. **`workflows-core`** — the format (§3, §4, §5, §6, §8, §11, the example), the intake, pre-lint, the lineage row and selftest, `next-phase-offer` and its regenerated part, the references page, `CHANGELOG.md`. It lands first: the other two test for its sentences and fail closed without them.
2. **`product-workflows`** — `create-ard.md`, `ard-reviewer.md`, the page, `CHANGELOG.md`; the load of `create-ard.md` measured before and after (239,846 characters now; Phase 4.3 is 38,940).
3. **`dev-workflows`** — `conformance.md` (the GIT-G1 sentence only under D11's approval), `design.md`, `design-reviewer.md`, `conformance-format.md`, the pages, `CHANGELOG.md`.
4. **Rules, coupling, `to-fix.md`** — the rules files, measured first; three coupling bullets; THREE-FORMS and KEPT-PUT-AGAIN closed with this file and the versions; FAULTED-DATE-WALK-ONLY logged (D4); CONFORMANCE-ON-INTAKE's entry notes that §11's test is stated once, in the format, which `/conformance` cites.

**The claim sweep is by subject**, over refinement 4's scope, each count taken before and after (`.claude/rules/claim-sweep.md`), no hand list being the set: *the forms a Disposition takes, and where its pairs end*; *what a re-disposition does to a threat's pairs* (the "drop any pair" sentence and its page copy); *who reads an acceptance*; *when a threat sent back is put again* (the intake's two sentences, `create-ard.md`'s step 3 text, `conformance.md`'s Next step and E3 paragraph, `next-phase-offer` and its part, the `/create-ard` and `/conformance` pages, `to-fix.md`); *what is written from a design or a record* (the intake, invariant 11, RETURNED-INTAKE's notes are history and stay). The exclusivity probe runs over "nothing read", "never written", "changes nothing", "only the stale".

## Risks

- **A *Keep* now writes the model.** An answer that left a threat sent back cost nothing before; now it rides a review and a handoff, once, in exchange for every later question. `create-ard.md`'s step 3 text says so.
- **The blob is coarse.** An unrelated landed edit to a design re-opens the threats it sent back: one more question, the safe direction.
- **Three statements of the routing rule** — `conformance.md`, `next-phase-offer` and its part — and §11's test stated once, in the format.
- **`create-ard.md` grows** in a phase PHASE-43-WEIGHT already logs; the rules move to the format and the intake wherever they are rule and not flow.

## Questions only the maintainer can answer

1. **THREE-FORMS — an accepted rest as form 1's second remainder, and a question before any live decision is dropped?** Recommended: **yes** — `Mitigated by <pairs>; the rest accepted — <owner>; <reason>; review by <date>` (D1), D2's keep question at every re-disposition, and D3's rest question where a rest is left. Alternatives: a fourth form of the same syntax; a separate `Residual:` field; keeping pairs by default with no question.
2. **KEPT-PUT-AGAIN — a `## Answered when sent back` section in the model, fingerprinted by the design's blob and the record entry's fields?** Recommended: **yes**, approving with it the relaxation of RETURNED-INTAKE's "nothing read from a design or a record is written" to the keys, ids, known-set values and blob ids D7 names, in that section alone, and accepting that an answer leaving a threat sent back now writes the model once (D6–D8). Alternatives: a `Kept:` line inside the threat's block; the status quo.
3. **GIT-G1, by name: may *The Rules a threat rests on* — which `/conformance` Phase 6's `/create-ard` line tests — take a threat with an accepted rest?** Recommended: **approve** (D11). It adds no arm and no wording to the line, and is independent of the pending narrowing of arm (a) and of E3-NOT-LANDED, which this design leaves to you.
4. **What does `/conformance` route for a threat the architect has answered?** Recommended: **drop the PA's route, keep every Dev route the line takes today, and add none** — so an answered `taken by no design` or `open on a decision` line names no command (D10). Alternatives: keep the PA route with a qualifier; add a Dev route for `taken by no design`, to the design that said it is not its own.

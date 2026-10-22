# Rulings — lean context, part 1

The decision ledger records 88 rulings, R1 to R88, each once. `grep -c '^Ruling [0-9]' 2026-10-20-lean-context-loader-ledger.md` counts them in the ledger copy beside this file, and a script over the same lines found no number missing and none repeated. None is marked USER or "user decision" in the ledger, so none is marked here as the user's own. Several cite the user's stated priorities — R7 ("user: quality over cost"), R9 ("user: fix all known bugs"), R15 (a Fable implementer needs the user's ask) and R69, R84 and R85 ("quality first"; R69 was also "named to the user") — but the ledger does not mark them as the user's decisions, so they are not counted. The user's own decisions are unnumbered ledger entries, listed after the tables. Two rulings were reversed later (R35 by R75; R13's measured refusal by R85), two were replaced (R16 by R19; R78 by R84), and one corrected a controller error in another (R88 corrects R85's history). The branch was not yet merged when this was written: at `f02b4c39` it carries workflows-core 1.44.0, dev-workflows 4.30.0, product-workflows 3.35.0, docs-workflows 1.17.0 and security-workflows 0.2.0.

"Cost if wrong" is the ledger's own wording, shortened where needed. `not stated` means the ledger gives no cost for that ruling. "R" numbers are ruling numbers.

The ledger itself is beside this file, unchanged, in `2026-10-20-lean-context-loader-ledger.md`: each ruling's full wording, and the task, review and fix-round entries around it. Where this summary and the ledger differ, the ledger's wording is the record; where a ruling and the shipped text disagree, the shipped text is the authority.

Boundary notes. The pre-flight scan's rulings (R1–R7) open the first section. Task 2's review also covered Task 1's carried gate commit, so R22, a gate ruling, sits with Task 2. The gate-maintenance dispatch between Tasks 4 and 5 (R28 and R31's work, and R32–R34) sits with the splits. The ledger writes R77 before R74–R76, because the loader strand reported first; the tables list them in number order. Task 14, the live runs, made no numbered ruling.

## Pre-flight and the gate (Task 1)

R1–R19: the pre-flight scan, then `scripts/reference-parts.py`, its five fix rounds and the breaker.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 1 | The consumer preamble paragraph and the loader's paragraph name the split references without a count; the gate builds the list alphabetically, in backticks: "`a`, `b`, `c` and `d`". | A count word would need a number-word table and breaks on a fixture of one. | Two sentences reworded. | amended by R45 and R81 |
| 2 | Task 0 is the controller's scratch check; at the base it passes 3 of 102 checks, the three that test a state already holding. | not stated | not stated | |
| 3 | Task 5 runs `check-citations --verbose` locally for its alias census before Task 7 wires the check into CI; a non-zero exit there is expected. | Task 5 needs the census before Task 7 adds the gate to CI. | None. | |
| 4 | Task 6's markers must leave check 11's parse of `next-phase-offer`'s scope paragraph intact; check 11 passing is the test, and a marker that breaks it moves, never the check. | The pre-flight flagged the markers as a risk to check 11. | None. | |
| 5 | Task 1 keeps `.claude/rules/gates.md` under 20,000 characters; if its pointer clause cannot fit, the implementer reports and the controller rules. | The file was near the 20,000-character warning. | One more ruling. | |
| 6 | Task 7 also sweeps "workflows-core's layout and the loader" in `.claude/rules/workflows-core.md`, and `CLAUDE.md`'s Structure block if it lists the directories. | Task 7's file list left out the rules file that describes the layout and the loader. | One more file touched. | |
| 7 | Implementers and task reviewers run on Opus; a scoped re-review runs on Sonnet for a fix diff of one or two files, on Opus otherwise. | The user's priority, quality over cost; executed prose across about 60 files. | Higher token spend. | |
| 8 | A bare citation whose sentence names rules held by different parts places each name on its own part, never a failure. "A name that matches entries in two parts fails" stays, as a guard. The explicit-part-request check stays. | The run loads each part, per the preamble; the explicit check catches a call converted to the wrong part. | A sentence that should have been split loads two parts. | |
| 9 | Task 1's review findings (a rule in a private part, unpinned fail-closed branches, Minors 1–3) are fixed in the same round; Minor 1 scopes the explicit-request check to its paragraph; Minor 4 (45 characters left in `gates.md`) goes to Task 7. | The user's rule: fix all known bugs. | One round's edits. | |
| 10 | A call's own sentence is judged against that call's load only; a citation-free sentence is judged against the loads made at or before it in its paragraph, never a later one. | A rule must be in front of the run when it applies (the spec's anti-goal). | A correct paragraph that applies a rule before its load is reported, and rewritten to load first. | narrowed by R11 |
| 11 | Within one sentence, the calls are one order-free union. | A run reads a sentence whole before acting, and this repository's prose often names a rule before its parenthetical loader call. | A wrong-part call in a sentence that also loads the right part passes, which the run itself covers. | |
| 12 | The loads "at or before" a citation-free sentence are every load the run makes there: explicit part requests, explicit whole loads, and the parts a bare citation's names place on. | The check had counted only part requests. | None. | clarified by R17 |
| 13 | The citation-free check is widened to every paragraph that loads the reference in any form only if a measurement first shows it catches more than correct prose; otherwise it is not widened, and the refusal is reported. | Out-of-scope item 1 of fix round 3. | One measured widening. | measured in round 4 (11 hits, all on correct prose), so not widened; the refusal reversed by R85 |
| 14 | In a citation-free sentence, a name is checked against each split reference loaded in the paragraph whose index holds it; a sentence citing reference R is judged as that citation only for R's names. | Out-of-scope item 2 of fix round 3. | None. | |
| 15 | Fix round 4 goes to a fresh Opus implementer. | A more capable model would be Fable, which needs the user's ask; the open items are logic and wording, not capability. | One more round. | |
| 16 | A § reference is attributed to the nearest reference citation before it in its sentence; a § with none before it names nothing. | Two § references were read as the wrong reference's, a false red. | A § written before its reference's citation goes unchecked. | superseded by R19 |
| 17 | A bare citation naming no rule counts as a whole load for later sentences. | The preamble sends it to `args: "<name>"`, which holds every rule; the gate models what the run does. | None. | |
| 18 | The name extractor keeps code spans inside italic and bold spans, so such names match their headings; no masked alias is added. | A known bug, fixed now. | None. | |
| 19 | A § is attributed to the nearest citation before it in its sentence; failing that, the first after it in the sentence; failing that, the nearest in an earlier sentence of its paragraph; else it names nothing. It is measured on the trial trees before it lands. | Task 1's breaker: it closes the probe that passed a wrong-part call, and the "Then stop as §4 says." shape. | A § leaning on a distant citation is read against it. | supersedes R16; refined by R28 and R34 |

## The loader reuses what a run read (Task 2)

R20–R23. Task 2's review package began at Task 1's carried gate commit, so it also reviewed R19's implementation.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 20 | The `model-routing` skill gets the same reuse rule, its opening reworded so that its read instruction no longer comes first. | The sweep is by subject, how the loader reads; deleting the word alone would leave that unstated. | One more file changed. | |
| 21 | The loader's last paragraph is restructured: "single source of truth" and executing the entry point bind whether the text was read now or reused; only the read instruction sits in the read branch. The same in `model-routing`. | Task 2 review Minor 6: a reuse run skipped both. | One paragraph reworded. | |
| 22 | The gate resolves a skill call against a known skill-to-reference map in its config (`model-routing` → `model-routing/classification`), so that call is a citation for § attribution; any other skill token is none. | Resolve against a known set. | One config entry. | |
| 23 | "When a second argument names an entry point" replaces "is present". | Once Task 7 lets a second argument name a part, "is present" would contradict it. | Task 7 rewords one clause. | |

## The four rulebooks split (Tasks 3–6) and the gate maintenance

R24–R37: `session-hygiene` (Task 3), `finding-triage` (Task 4), the gate-maintenance dispatch, `escalation-rules` (Task 5). Task 6, `next-phase-offer`, made no ruling.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 24 | `session-hygiene`'s definitions of `<KEY>` and `<role>` (§4) sit in `core`, where the resume-pointer template reaches them. | Naming §4 instead would make every resume step load `guidance`, which is the whole file again. | One sentence carried by every part. | |
| 25 | The `### Context hygiene` alias is dropped; Task 7 converts the nine "ALWAYS end with a `### Context hygiene` block" bullets to load `guidance` explicitly. | It names a command's output block, not a rule, and as an alias it failed 12 sentences that only describe the block. | Nine bullets reworded in Task 7. | |
| 26 | The `Location` and `Skipped` aliases stand. | They are §1's own bold labels, and Task 7's conversion of the `/docs-*` commands needs them. | Two index entries. | |
| 27 | Task 4's extra edit is accepted: `finding-triage`'s summary of re-review survivors now carries on-re-review rule 1's exception, and Task 11's changelog names it. | The summary had been stale since `e4204891`, a known bug in a file the task edits. | One sentence. | |
| 28 | One gate-maintenance dispatch after Task 4's review: the gate reads a possessive § name, attributes a "§N of <citation>" phrase to that citation, and wraps index names in code spans; it gets its own scoped review. | Task 4's concern 2 and two deferred gate minors. | One more small dispatch. | its "§N of" attribution narrowed by R34 |
| 29 | `finding-triage`'s line reads "On a PASS WITH RECOMMENDATIONS whose survivors hold none its fixer takes, the caller continues without one." | Standing alone after the split, the old sentence read as covering a fully emptied set, which the lead sends to the settle prompt. | None. | |
| 30 | The lead's "(§ On re-review)" gains "; the caller's own text names which of its reviews are re-reviews". | The lead leaned on the re-review definition. | None. | |
| 31 | The gate gains a `helper` part kind: covered, needable by other parts, generating no file, never requestable. `finding-triage`'s three helpers take it. | Helper parts were public files that did not stand alone. | One declaration flag. | |
| 32 | No gate change for "§ On re-review's" after an `escalation-rules` call in the two proposal commands; Task 8 names `workflows-core:finding-triage` beside it. | A run would read it as `escalation-rules`' too; the fix belongs in the prose a run reads. | Two sentences reworded. | |
| 33 | A helper's rules appear in the index against the requestable parts that bring it, never against the helper. | No request may name a helper. | None. | |
| 34 | The numbered form attributes only on "§N of <citation>" with nothing between; the named form only where the name resolves in that reference; otherwise position decides. Red cases pin both probes, and the docs are narrowed. | Review Important: the gate accepted up to eight words between the § and "of <citation>". | None. | narrows R28 |
| 35 | `escalation-rules`' `review` part keeps its `finding-triage` re-review bundle. | The review gate's rules send runs to on-re-review rules 2–3, and five of the twelve review-gated commands load no `finding-triage` of their own. | About 4k tokens per run that loads both. | reversed by R75 |
| 36 | The open-question rule stays in `review`. | The maps make it unsafe alone: it leans on rules P, Q and R by name. | One ~50k load for one rule in `epic-writer`. | |
| 37 | An option label whose meaning the reference defines counts as a rule name for an alias (`Set <VAR>`, `Proceed`); an output block never does (R25). | Task 5 review Minor 3, and Task 4's `Proceed` alias. | Two index entries. | |

## The callers load by part (Tasks 7–10)

R38–R65: the loader and the preamble with `session-hygiene`'s callers (Task 7), then `finding-triage`'s (Task 8), `escalation-rules`' (Task 9) and `next-phase-offer`'s (Task 10).

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 38 | `scripts/check-docs.sh`'s check-16 header stays untouched on this branch; its stale second-token wording and census go to the user at the merge as a cross-edition fix; `gates.md` § Check 16 states the second-token rule. | The script's body is shared byte for byte with the internal editions. | One stale comment until ported. | open: put to the user at the merge; the ledger records no answer |
| 39 | Accepted: `/promote-decisions` loading a section by a name with no entry point now stops the run (R23), and the rationale's "Tasks 7–10". | Task 7 concern 2. | None. | |
| 40 | The loader's part paragraph moves after the reuse paragraph, its wording unchanged. | Every read instruction follows the reuse rule (R21's order). | None. | |
| 41 | Of the 21 `session-hygiene` citations still counted whole, each gets its rule named wherever the sentence makes it plain; the rest stay whole and are listed. | Task 7 owns `session-hygiene`'s callers. | A few sentences reworded. | |
| 42 | The 15 printed § citations stay, and Task 11's changelog names them. | A precise pointer is a user-visible improvement; reverting would re-read the whole 11.8k at report time. | One changelog line. | |
| 43 | The loader says "A read of the whole reference covers each of its parts, save what a part bundles from another reference". | The unqualified sentence was false for a part that bundles another reference. | None. | |
| 44 | The loader defines an entry point as a name a heading of that reference carries in a code span, so the stop is decidable; every live token is confirmed. | "Entry point" was undefined, so the stop turned on judgement. | A stop on a token no heading carries, which is the error it should be. | refined by R71 |
| 45 | R1's preamble reads "…unless that part is already in this conversation word for word"; the gate's preamble constant, its fixtures and all 39 insertions change together. | Task 7 review Minor 5. | A scripted re-insertion. | amends R1 |
| 46 | A caller that re-reviews requests `re-review` at its first triage step; one that never re-reviews requests `triage`; never both in sequence. | `re-review` holds `triage`: about 20.1k against the whole file's 21.4k, where the two in sequence read 16.1k + 20.1k. | A first review that never reaches its re-review carries about 4k more. | |
| 47 | Accepted: the verify alias "verification step", classification's "§ The step", and the fixes to `workflows-core-triage.md`. | Task 8 concern 2. | None. | |
| 48 | `Skill` is removed from `docs-scaffold-reviewer`'s tools where it cites no core reference, and the docs agents table's tools are fixed. | Known bugs, one of them pre-existing. | An agent without a tool it does not use. | |
| 49 | The scratch check's `/implement` assertion tests `re-review` and `no-findings`, and no `triage` request. | The old assertion predated R46. | None. | |
| 50 | `grilling-technique`'s `review` load mid-grill stays, to be measured in Task 14. | It is no worse than today's whole load, and the grilling commands load `review` at their gate anyway. | About 50k carried earlier in a grill. | |
| 51 | `/promote-decisions` reaching `branch-naming`'s new citation loads `escalation-rules` whole. | It has no preamble paragraph and no direct citation of a split reference; no rule is lost. | One whole load. | |
| 52 | P (*A recorded verdict names the version it was taken against*) becomes part `version-line`, which `review` needs; P's two forward pointers become a sentence naming which callers make those offers; `/vuln` and `/upgrade` request `version-line`. | The maps rate P safe after a restructure; those two commands then load about 3k, not about 50k. | One part carved, two calls changed. | P's sentence replaced by R53 |
| 53 | P's sentence names the two rules instead of copying their caller lists. | A copy of the lists would be a third copy that drifts; a name is never a positional pointer. | One sentence. | amends R52 |
| 54 | `/vuln`'s and `/upgrade`'s own text states that the command makes neither of the two offers. | A command states its own behaviour, and P stays free of caller names (R53). | One sentence per command. | amended in place: the ruling's sentence was false on two paths and was reworded in fix round 1; a `NEEDS HUMAN` clause followed in fix round 2 |
| 55 | The ten calls that apply only P request `version-line`. | A step loads what it uses; a later step that makes an offer loads `review` through its own citation. | None. | |
| 56 | Accepted: 25 bare citations of `next-phase-offer` became explicit requests. | Each is the first citation on its offer path, so the lane loads once. | None. | |
| 57 | The docs commands' "merge-clause rule" sentences keep the named rule, which loads `contract`. | Plain wording would mislead. | About 15.6k at a docs command's end. | |
| 58 | The early `contract` loads in `/brd-reconcile` and `/brd-split` request `brd`, which holds it. | The later lane load then reuses it, as R46 did for `finding-triage`. | None. | |
| 59 | A lane request that exists only inside a fenced report template gets an explicit loader call in the prose of the step that prints it. | A fence is printed, never executed (check 16 relation 4). | One sentence per site. | |
| 60 | Four aliases are added to `next-phase-offer`'s declaration. | They are rule names, not output blocks. | Four index entries. | |
| 61 | Six commands move their lane's explicit call to the step that prints the report; the Invariants line keeps the citation without a call. | An Invariants call could load early, or never. | Six moved sentences. | applied with the Task 10 reviewer's mode and branch conditions |
| 62 | Two `escalation-rules` sentences italicise the rule names they mean, so they place. | Naming only; no meaning changes. | Two spans. | |
| 63 | `/brd-package`'s Phase 0 rationale sentence becomes a bare lane-named citation, not an explicit 23k load. | It applied no rule, and it loaded on the `NOTHING_TO_REVIEW` stop for nothing. | None. | its Phase 10 consequence (next-phase-offer reading W3) fixed by R79 |
| 64 | `/conformance`'s and `/security-workflows:scan`'s Invariants take the bare lane-named form, as R61 does for the six. | Their calls had become no-ops in Invariants. | None. | |
| 65 | The scratch check's Task 10 test is not extended. | The Task 10 reviewer verified each caller's lane by hand, and Task 12's reading re-reads every converted call. | A later regression in a lane is caught by Task 12 or the final review, not by the scratch check. | |

## Versions and changelogs (Task 11)

R66–R67.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 66 | Accepted: one reverse-coupling exception. A `/promote-decisions` older than product-workflows 3.35.0 asks the 1.44.0 loader for a section by a name no heading code span carries, and the loader stops; the coupling line and workflows-core's changelog say so. | The stop is loud, never silent, and the family's update instruction updates all five plugins together. | An older `/promote-decisions` stops until product-workflows is updated. | |
| 67 | Accepted: the sweep's Invariants edits in three docs commands, and the docs-workflows count fix (22 pages, 24 files). | Task 11 concerns 2 and 3. | None. | |

## The rule-by-rule reading and its fixes (Task 12)

R68–R84: the five readings' WORSE items, fixed in two dispatches (A: the loader, the preamble and the gate; B: the references, the commands and the changelogs), and their reviews.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 68 | On a reference that does not load by part, the text a request needs is the whole file, whichever entry point it names; a read of some of its lines covers none; a whole read is every line, in consecutive ranges where one read cannot hold it. Both skill copies. | Loader reading W1: this is the safety the spec rests the procedure references on. | None. | refined by R83; stands by the user's decisions at 11:50Z and after run 7 |
| 69 | A run reuses an earlier read to execute an entry point only where that read was made in the current phase; to look up a rule, any read in the run serves. | Loader reading W2, quality first: it keeps the measured adjacent savings and gives up only the reuse of a procedure from far back, whose fidelity is unmeasured; a refinement of spec goal 1, named to the user. | A second read of `specs-repo-git`, `phase-handoff` or `run-flags` late in long runs. | refined by R82; stands by the user's decisions at 11:50Z and after run 7 |
| 70 | The re-read rule reads "whenever those words are not in front of you now, whatever removed them … Where you cannot tell, read it." Both copies. | Loader reading W3: the trigger listed three causes and gave no default. | None. | |
| 71 | An entry point is the first word of a code span in one of that reference's headings. | Loader reading W4a: a run comparing the token with the whole span would stop. | None. | refines R44 |
| 72 | `check-citations` also fails an `args: "<ref> <token>"` on a reference that does not load by part whose token is no such first word, with red and green cases. | Loader reading W4b: no gate checked entry-point tokens. | One more relation. | |
| 73 | The stop reads "the request fails: report the argument that named nothing, and stop as your command stops". | Loader reading W4c: a loader stop would bypass the command's own stop path. | None. | |
| 74 | Each of seven `session-hygiene` callers names `workflows-core:session-hygiene` §2 in the sentence that makes the `/compact` or `/clear` suggestion. | Session-hygiene reading: seven blocks applied §2 while their citation named only §1. | None. | |
| 75 | `escalation-rules`' `review` part drops its `finding-triage` re-review bundle; its pointers into § On re-review apply only where the caller triages. | Finding-triage reading W1 and escalation-rules reading W3: five commands that never triage got triage rules contradicting their own text, and every triaging caller has loaded `re-review` by then (R46). | A triaging caller that reaches `review` before its triage step loads `re-review` through the citation. | reverses R35 |
| 76 | `/implement`'s PASS WITH RECOMMENDATIONS bullet follows its authority: a fully emptied set takes the first settle prompt; a partly emptied set with nothing for the fixer goes on to step 7.5. The changelog names the alignment. | Finding-triage reading W2: the bullet contradicted the reference. | One more question on an emptied PASS WITH RECOMMENDATIONS. | |
| 77 | `workflows-core`'s `docs/reference/references.md` states the new stop. | Loader reading N7. | None. | |
| 78 | `/release-notes` requests `pa` and `pe` beside `dev` at its next-step step, or names them so that they place. | Next-phase-offer reading W1: the run must know which commands the pending PA and PE phases are. | About 4k more at one step. | replaced by R84 |
| 79 | Every step that prints an array carrying `<merge-clause>` loads its lane before the array: `/brd-interview`, `/brd-package`, and five pre-existing sites. | Next-phase-offer reading W2, W3 and N1; known bugs. | None. | |
| 80 | `/brd-reconcile`'s naming sentence carries the *Closed-vocabulary pickers* citation; `/release-notes` cites the zero-match rule's `/document` variant. | Escalation-rules reading W1 and W2. | None. | |
| 81 | The preamble says never to guess a part's name, and to load the index first; on a second argument naming no part, the loader reports it, reads the index and requests the part the index names, never reading anything else in its place. R1's preamble is amended again. | Escalation-rules reading X1: a guessed part name was a loader stop. | One index read on a mistyped guess. | amends R1 |
| 82 | The bound's "phase" is the `##` section of the command now running, the text before its first `##` heading counting as one, or an agent's whole dispatch. Both copies. | Dispatch A review Minor 5. | None; the bound only decides a re-read. | refines R69 |
| 83 | "A read short of every line — a section, a range, a search — covers no request", so consecutive ranges that reach the last line are one whole read. Both copies. | Dispatch A review Minor 4. | None. | refines R68; its wording completed in Task 13's fix wave (final review M3) |
| 84 | `/release-notes`' next-step step loads the whole `next-phase-offer` in place of `dev` plus `pa` and `pe`. | `dev`, `pa` and `pe` together are larger than the whole file, and "pending" is defined across the lanes: the released behaviour, quality first (dispatch B review Important 1). | About 23.5k more than `dev` alone on a run with nothing pending. | replaces R78; the ruling's "44,842 chars" is a byte count, 44,451 characters (ledger, dispatch B fix round 1) |

## The final whole-branch review (Task 13)

R85–R88: the final review over `b1f3adba..a5b278b3`, its one fix wave, and the re-review's residuals.

| # | Decided | Why | Cost if wrong | Status |
|---|---|---|---|---|
| 85 | The paragraph widening is adopted: a rule name in a paragraph whose sentence names no reference is checked against the paragraph's citations; two sentences name their reference; the refused case becomes a red case; the rationale, rules file, docstring and comment state the history. | Final review I1, quality first: the refusal rested on evidence the reading falsified. | A correct sentence must name its reference. | reverses R13's refusal; its history count corrected by R88 |
| 86 | `gates-reference-parts.md` states the blind spot, and every lane-request sentence names its lane by its italic rule name, so the gate places and pins it. | Final review M1: lane-request sentences named no rule. | About 30 one-phrase edits. | |
| 87 | The generator writes one line under each part file's title naming every part the file holds. | Final review M2. | One line per part file. | |
| 88 | The controller corrects five sentences directly, with no second fix wave: the widening's history in the docstring, a comment, the rules file and the rationale, and an inverted `brd-proposal` sentence in workflows-core's changelog. | The re-review found the history false — the brief had misread the measurement — and the changelog sentence inverted. | None. | corrects R85's history |

## The user's decisions

None of these is a numbered ruling. Each is an entry the ledger marks USER DECISION. The ledger gives times in UTC without dates; the dates follow from the live runs' windows.

| When | Decided |
|---|---|
| 2026-10-21, 09:15Z | The scan slot is an Epic-key scan, `/security-workflows:scan BOOK-2-01-02`, in place of the spec's baseline `d65028a2`, a `--verify-fixes` run on whose start state today's plugin stops before the scanner runs; the runs go shortest first: conformance, prd-ground, release-notes, scan, run B, route 3, design. This settles the scan question the ledger had left "USER DECISION pending". |
| 2026-10-21, 11:50Z | Continue as is; Rulings 68 and 69 stand; decide with the full data after the seven runs. |
| 2026-10-22, 09:3x Z (the ledger gives no minute) | (1) Cost: option A, keep part 1 as is; Rulings 68 and 69 stand. Option D, splitting the large procedure references by entry point, is the next sub-project, with its own spec. (2) Run 5: an attribution run on today's `main` on the same inputs, then a blind three-way comparison. (3) The unloaded `escalation-rules core`, which is pre-existing, goes into that sub-project as an explicit load step in every asking command; it is not fixed in part 1. |

The ledger also records the user's choice of subagent-driven execution (2026-10-20 10:02) and two instructions to continue after a pause; those are not marked USER DECISION.

## Rulings later corrected, amended or reversed

- Reversed: R35 by R75 (the `review` part's bundle); R13's refusal of the paragraph widening by R85.
- Replaced: R16 by R19 (§ attribution); R78 by R84 (`/release-notes` loads the whole `next-phase-offer`).
- Amended by a later ruling: R1 by R45 and R81; R52 by R53; R10 narrowed by R11; R12 clarified by R17; R19 refined by R28 and R34; R28 narrowed by R34; R44 refined by R71; R68 refined by R83; R69 refined by R82.
- A consequence fixed by a later ruling: R63 left `/brd-package`'s Phase 10 array ahead of its only load (next-phase-offer reading W3), fixed by R79.

The ledger marks two errors as the controller's own:

- R85 → R88: R85 stated the widening's history from the controller's misreading ("caught 4 of the 6 gaps"); the widening had fired six times, four of the hits on gaps the reading found, and R88 corrects the five sentences.
- R54: "the controller's sentence was false on two paths"; the implementer reworded it in Task 9's fix round 1, and a `NEEDS HUMAN` clause followed in fix round 2. No later ruling; amended in place.

One figure was corrected in the ledger without a ruling: R84's "44,842 chars" was the byte count, and the changelog states 44.5k characters (44,451).

Amended in place under their own number, not counted above: R54 (as above) and R83 (its wording completed in Task 13's fix wave).

One ruling waits on the user: R38's question, whether to fix `check-docs.sh`'s stale check-16 header and port the shared body to the internal editions, was to be put at the merge.

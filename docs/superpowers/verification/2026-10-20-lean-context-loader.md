# Lean context, part 1 — verification record

Branch `iv-gu/lean-context-loader`, HEAD `f02b4c39`, 52 commits on base `b1f3adba` (`git rev-list --count b1f3adba..f02b4c39`). Plan `docs/superpowers/plans/2026-10-20-lean-context-loader.md`, spec `docs/superpowers/specs/2026-10-20-lean-context-loader-design.md`. Written last: after Task 13's fix wave and Task 14's seven live runs, and before the changelogs are dated and the branch merges. The 88 rulings are summarised in `2026-10-20-lean-context-loader-rulings.md`, and the SDD ledger is copied unchanged in `2026-10-20-lean-context-loader-ledger.md`.

**Status: three of the spec's four done-criteria are met. The fourth is reported, and one clause of it is not met.**

- **Gates.** The unreleased gate chain prints `EXIT=0`. The run with `ASSERT_PUBLISHED=1` comes after the changelogs are dated, by the controller, and is not claimed here.
- **The reading.** It found 23 WORSE findings across five strands. Every one was fixed before the live runs (Rulings 68–84).
- **The blind comparisons.** None found a result worse because of part 1. Two ranked a baseline first (runs 3 and 5); in both, today's `main` on the same inputs ranked below the new run, so the gap predates part 1.
- **The measurements.** Reported for all seven runs. The repeated `phase-handoff` read is **not** gone: two of the four runs that reached a `phase-handoff` handoff step read the whole file twice. Rulings 68 and 69 cause it, and the user kept both rulings after seeing the cost (section 4).

**Sources.** The run figures are quoted from each run's `measure.txt`, the verdicts from each run's blind `verdict.md`, and the reading counts from the five reading files. All of these were scratch and no longer exist; the ledger copy keeps the figures they gave. The versions, the gate line, the census and the `phase-handoff` counts were re-derived for this record, with the command or method beside each.

## 1. What shipped

Versions, read from each `plugins/<name>/.claude-plugin/plugin.json` at `f02b4c39`. All five match the versions the plan's Task 11 set.

| Plugin | Version | Changelog section at `f02b4c39` |
|---|---|---|
| workflows-core | 1.44.0 | `## [1.44.0] — Unreleased` |
| dev-workflows | 4.30.0 | `## [4.30.0] — Unreleased` |
| product-workflows | 3.35.0 | `## [3.35.0] — Unreleased` |
| docs-workflows | 1.17.0 | `## [1.17.0] — Unreleased` |
| security-workflows | 0.2.0 | `## [0.2.0] — Unreleased` |

What part 1 does:

- **The loader reuses what a run already read.** The `reference` skill, and the `model-routing` skill's copy of its rule, work from a reference already in the conversation word for word, instead of reading it on every call. On a reference that does not load by part, a request needs every line of the file (Ruling 68). A read is reused to execute an entry point only within the `##` section where it was made; any read serves to look up a rule (Rulings 69, 82).
- **Four rulebooks load by part.** `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene` each stay one marked source file. `scripts/reference-parts.py` generates their parts, each with the rule index, under `plugins/workflows-core/reference-parts/`. `python3 scripts/reference-parts.py check-parts` prints "4 split reference(s), 31 generated file(s) fresh".
- **A new gate.** `scripts/reference-parts.py` (`--selftest`, `check-parts`, `check-citations`) runs in CI and fails closed.
- **The callers request parts.** Commands, agents and references in all five plugins request the part a step needs, or cite a rule by name so the preamble loads its part.

## 2. The spec's four done-criteria

### 2.1 Every gate passes

The chain is the `run:` steps of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain, run on the worktree at `f02b4c39` with these three files added, by the scratch script `gates-unreleased.sh` (scratch, no longer exists). It runs without `ASSERT_PUBLISHED`. Its steps: `validate-catalog.py` (selftest, run); `check-id-grammar.sh` (selftest, `--root .`); `check-docs.sh` (selftest, `--root .`); `reference-parts.py` (selftest, `check-parts`, `check-citations`); the mermaid gate (`npm ci`, selftest, `--root .`); the selftests of `session-cost.py`, `secret-scan.py`, `run-state.py`, `architecture-harvest.py`, `promotion-signals.py`, `proposal-record.py`, `register.py`, `key-discovery.py`, `bounded.py` and `session-branch.py`; and the check that every plugin citing `bounded.py` carries an identical copy.

It printed:

```
EXIT=0
```

Not claimed here: the run with `ASSERT_PUBLISHED=1`, which arms check 18 and passes only once the `— Unreleased` sections are dated.

### 2.2 The rule-by-rule reading finds nothing worse

Five readers read every converted caller under the released load and the new one (Task 12). Their counts:

| Strand | Read | WORSE | BETTER | NEUTRAL |
|---|---|---|---|---|
| The loader | 22 items over seven scenarios | 4 | 8 | 10 |
| `session-hygiene` | 87 caller steps | 7 | 15 | 65 |
| `finding-triage` | 57 caller steps | 2 | 10 | 45 |
| `next-phase-offer` | 42 caller steps | 3 | 8 | 31 |
| `escalation-rules` | 276 caller steps (29 first prompts, 230 citations, 17 uncited applications) | 7 rows in three items, plus X1, not counted as a row | 18 | 251 |

The loader's counts are its reading file's "Counts" line. The other four were re-counted for this record by a script over each reading file's table rows, one verdict per row. Every count matches the ledger's "Task 12 … reading" line for its strand.

That is 23 WORSE findings: the loader's four items and the other strands' 19 rows. They overlap in one place: `escalation-rules` W3 (five rows) and `finding-triage` W1 are the same defect seen from two strands.

Every WORSE row and its fix:

| Strand | WORSE | Fixed by | Commit |
|---|---|---|---|
| Loader | W1: an entry-point request on a reference that does not load by part was never said to need the whole file | R68, refined by R83 | `53d54478`, `532759bf` |
| Loader | W2: a procedure could be executed from a read made phases earlier | R69, refined by R82 | `53d54478`, `532759bf` |
| Loader | W3: the re-read trigger listed three causes and gave no default | R70 | `53d54478` |
| Loader | W4: the entry-point stop had no "first word" definition, no gate and no stop path | R71, R72, R73 | `53d54478` |
| `session-hygiene` | Seven blocks applied §2 (the `/compact` or `/clear` suggestion) while citing only §1: `/brd-intake`, `/brd-split`, `/brd-package`, `/prd-ground`, `/update-prd`, `/brd-interview`, `/brd-reconcile` | R74 | `906dcb91` |
| `finding-triage` | W1: `escalation-rules`' `review` part brought triage rules into five commands that never triage | R75 | `906dcb91` |
| `finding-triage` | W2: `/implement`'s PASS WITH RECOMMENDATIONS bullet contradicted the reference on an emptied survivor set | R76 | `906dcb91` |
| `next-phase-offer` | W1: `/release-notes`' next step depended on lanes the step did not load | R78, replaced by R84 (the whole file) | `906dcb91`, `a5b278b3` |
| `next-phase-offer` | W2, W3: `/brd-interview` and `/brd-package` printed `<merge-clause>` before loading its rules | R79, with the five pre-existing sites of N1 | `906dcb91` |
| `escalation-rules` | W1: `/brd-reconcile`'s missing-reason picker ran without the pickers rule | R80 | `906dcb91` |
| `escalation-rules` | W2: `/release-notes`' zero-match escalation ran without the `scan` part | R80 | `906dcb91` |
| `escalation-rules` | W3, five rows: the `review` bundle of `finding-triage` W1 | R75 | `906dcb91` |
| `escalation-rules` | X1, not a row: a run's first bare citation needed the index, and a guessed part name stopped the loader | R81 | `53d54478` |

Checked against the ledger: every WORSE finding is fixed, and none is left open. Dispatch A (the loader, the preamble and the gate) was approved with six Minor findings, all fixed in one round. Dispatch B (the references, the commands and the changelogs) needed one fix round, which produced R84, and ended with nothing open. The ledger then records "Task 12: complete (commits f572003f..a5b278b3, review clean)". The final whole-branch review (Task 13, `final-review.md`, scratch) found that "every Task 12 fix … hold[s]". The reading itself was not re-run after the fixes.

### 2.3 No blind comparison finds a result worse because of part 1

Each run was replayed on the `ihudak-e2e` copies from a restored start state, and a judge compared the results blind, with run identities masked. The letter mappings are the ledger's.

| Run | Command | New session | Compared with | Verdict | Part 1's share |
|---|---|---|---|---|---|
| 1 | `/dev-workflows:conformance BOOK-2-01-02` | `cd041db4` (X) | baseline `84b4783c` (Y) | **Equivalent** | The baseline wrote the better record (its `[AD#1]`/`[AD#4]` reading, `## Satisfied` lines to format); the new run gave the user the more accurate account. The new run's own slips are not attributable to part loads (ledger). |
| 2 | `/product-workflows:prd-ground BOOK-2-01` | `8fa7aefc` (Y) | demo baseline `8fe4723`, no transcript (X) | **New better** | The new run's grounding files are clean and plugin-free; the baseline's carried about ten plugin tokens that `/brd-package` would stop on. The baseline was better on an optional derivation matrix and a richer pull request. |
| 3 | `/docs-workflows:release-notes BOOK-2-01` | `ec3e00d0` (C) | demo baseline `68bf77f` (B); today's `main`, `f9684b8b` (A) | **B > C > A**; C > A directly | The baseline's note was the most accurate and conformant, and only its run noticed that all three notes drop the PRD's starting-state fact. Today's `main` misses it too and ranks below the new run, so the gap is not part 1's. |
| 4 | `/security-workflows:scan BOOK-2-01-02` | `796118d3` (X) | baseline `bf055d1f` (Y) | **New better** | Same register and records; the new run left one consistent next step and a resume pointer free of stale pull-request numbers. See the process finding in section 4. |
| 5 | `/dev-workflows:implement`, direct, MODERATE (the Books-list filter) | `67b859d4` (Y; C) | baseline `5023b937` (X; B); today's `main`, `a759c4a3` (A) | Two-way: **baseline better, narrowly**. Three-way: **C > A > B** | The three-way supersedes the two-way (section 5). |
| 6 | `/dev-workflows:implement BOOK-2-01-02` (route 3) | `586ecaf9` (X) | baseline `beebc3f3`, today's `main` (Y) | **Equivalent** | Byte-identical non-test fix, same suite results. A first "X better" rested on the baseline's report being cut by the controller's extraction window; the judge re-judged it on the full text. |
| 7 | `/dev-workflows:design BOOK-1-01` | `6adf2f0b` (X) | baseline `77d89bc1`, dev-workflows 4.22.3 (Y) | **New better** | The baseline's images are never built under the tags its manifest pulls, its rollout step wipes the store's data, and it misses a defect and leaves a bound unrecorded as an `[AD#5]` deviation. The baseline was stronger on the data layer and its tests. |

Differences from the spec's blind set, each recorded in the ledger:

- The scan slot is an Epic-key scan, by the user's decision at 09:15Z (section 4), because the spec's baseline `d65028a2` is a `--verify-fixes` run on whose start state today's plugin stops before the scanner runs.
- Runs 2 and 3 have no baseline transcript, so their questions were answered as the baselines' artifacts show.
- Run 3's first two sessions loaded the installed plugins (today's `main`), not the branch. The first, `f9684b8b`, ran on the exact start state and was kept as run 3's today's-`main` reference; run 3 was then restored and replayed on the branch.

Criterion 3 is met. Only runs 3 and 5 ranked a baseline above the new run, and in both, today's `main` on the same inputs ranked below it.

### 2.4 The measurements, run by run

"Reference text" is the shared-reference text read into the main session. "Cache reads" and "main cost" are the main session's alone. "Total" is the session's cost over the run's window. Each cell is new / comparison, quoted from the run's `measure.txt`; the change in total is computed from those two figures.

| Run | Comparison | Reference text | Cache reads | Main cost | Total | Change in total |
|---|---|---|---|---|---|---|
| 1 conformance | baseline `84b4783c` | 865.0k / 419.8k chars | 28.3M / 22.5M | $11.77 / $8.43 | $12.45 / $9.19 | +35% |
| 2 prd-ground | baseline, no transcript | 807.6k / — | 29.3M / — | $12.51 / — | $17.69 / — | cost entry $16.07 / $15.12 (ledger): +6% |
| 3 release-notes | today's `main`, `f9684b8b` | 718.9k / 245.7k | 22.7M / 17.4M | $8.71 / $6.65 | $9.03 / $6.91 | +31% |
| 4 scan | baseline `bf055d1f` | 396.0k / 224.2k | 16.6M / 17.1M | $6.69 / $6.23 | $8.25 / $7.74 | +7% |
| 5 run B | baseline `5023b937` | 517.1k / 197.6k | 37.6M / 35.5M | $13.12 / $11.72 | $18.52 / $15.75 | +18% |
| 5 run B | today's `main`, `a759c4a3` | 517.1k / 276.0k | 37.6M / 36.2M | $13.12 / $12.07 | $18.52 / $17.51 | +6% |
| 6 route 3 | baseline `beebc3f3`, today's `main` | 832.4k / 372.8k | 79.1M / 46.6M | $24.67 / $15.55 | $29.69 / $19.05 | +56% |
| 7 design | baseline `77d89bc1` | 915.7k / 425.9k | 73.5M / 58.2M | $24.50 / $20.56 | $31.82 / $26.76 | +19% |

Notes on the comparisons:

- Run 2's window total includes waits of 1,805 s and 2,764 s at two prompts. Its baseline was a warm re-run after a stop, and the ledger gives only its cost entry.
- Run 3's demo baseline has no transcript, so the measured comparison is today's `main` on the same start state and answers.
- Run 6's paths diverged: the new run's review raised a finding, which added an *Open finding* and a *Re-review* prompt; the baseline's review passed with no findings.
- Run 7's baseline window runs to 11:30:52Z and includes two turns after its final report. Cut at the final report, the ledger gives $24.98 total and $18.78 main, which makes the change +27%.

There is no cost bar; quality decides. The cost rose in every run with a comparison, from +6% to +56% in total. Section 4 attributes it.

**The repeated `phase-handoff` read.** The spec asks for the measurements "with the repeated `phase-handoff` read gone from the producer runs". It is not gone.

Method: from each `measure.txt`'s reference-read list, a pass is one `phase-handoff` loader call and the reads of the file that follow it, up to the next such call. A pass is a whole read when its reads together cover every line. `phase-handoff.md` has 517 lines at `f02b4c39` (`wc -l`) and is the same at `b1f3adba` (`git diff --stat b1f3adba f02b4c39 -- plugins/workflows-core/references/phase-handoff.md` prints nothing). A read under 1k characters returned an error, not text, and is left out.

| Run | Whole reads of `phase-handoff` (new run) | `phase-handoff` text read, new / comparison |
|---|---|---|
| 1 conformance | **2**: Phase 0's `require-on-main`, and Phase 6's consent load (`args: "phase-handoff"`) | 277.4k / 138.6k (four slices) |
| 2 prd-ground | **0**: lines 1–344 at Phase 0, lines 345–517 at the `handoff-to-main` call, then lines 1–224 again | 183.7k / no transcript |
| 3 release-notes | **1**: the consent load | 138.9k / 4.3k (two `sed` slices) |
| 4 scan | 0: no `phase-handoff` read | 0 / 0 |
| 5 run B | 0: no `phase-handoff` read | 0 / 0 |
| 6 route 3 | **1**: Phase 0's `require-on-main`; no later `phase-handoff` load | 138.7k / 49.7k (one slice) |
| 7 design | **2**: Phase 0's `require-on-main`, and Phase 7's consent load (`args: "phase-handoff"`) | 277.1k / 129.7k (three slices) |

What the counts show:

- **The repeat the spec measured is gone.** The spec counted a consent load followed by a second loader call for `handoff-to-main` in the same step. In runs 1, 3 and 7 the consent load was the handoff phase's only `phase-handoff` call: no `phase-handoff handoff-to-main` call follows it in any of the three.
- **A repeat across phases remains, in runs 1 and 7.** Phase 0's `require-on-main` read the whole file, and the handoff phase read it whole again. That is what Rulings 68 and 69 require: a procedure reference is read whole, and an earlier read is reused to execute an entry point only within the `##` section where it was made. The handoff phase executes `handoff-to-main` in a later section than Phase 0, so the run reads the file again.
- **Run 2 read less than Ruling 68 asks.** Neither of its passes covered every line: Phase 0 read lines 1–344, and the `handoff-to-main` call read only lines 345–517. The ledger records this ("a slice, despite Ruling 68's every-line text").
- **No comparison read the whole file twice.** They read slices: the baselines of runs 1 and 7 read each line about once, in pieces; run 6's baseline read one slice; today's `main` in run 3 read two `sed` slices.

So criterion 4 is reported, but its clause "with the repeated `phase-handoff` read gone from the producer runs" is not met as written: two of the four runs that reached a `phase-handoff` handoff step (runs 1, 2, 3 and 7) still read it whole twice. The user saw the cost of this second read and kept Rulings 68 and 69 (section 4).

## 3. The census

Re-derived for this record. Command, run in the worktree at `f02b4c39`:

```
python3 scripts/reference-parts.py check-citations --verbose
```

It exits 0 and ends "reference-parts check-citations: PASS -- 4 split reference(s)". "Placed" counts the citations the gate places on a part; "whole" counts those it reads as loading the whole reference.

| Split reference | Placed | Whole | The whole citations |
|---|---|---|---|
| `escalation-rules` | 240 | 2 | `brd-interview.md:1499`, `brd-package.md:666`: negative mentions (ledger, Task 9) |
| `finding-triage` | 71 | 0 | — |
| `next-phase-offer` | 87 | 3 | `release-notes.md:622`, `:635`, `:766`: the whole load Ruling 84 chose |
| `session-hygiene` | 105 | 4 | `conformance.md:436` and `scan.md:480`, each standing for a whole block; `impl-maintenance.md:167` and its handoff reference's `:74`, example paths (ledger, Task 7) |

The same run counts 307 entry-point requests on references that do not load by part, using 16 distinct tokens.

## 4. The cost finding and the user's decisions

**The cost comes from the procedure references read whole, not from the split rulebooks.** The ledger's breakdown for runs 1–6, reference characters into the main session, new against comparison:

- `specs-repo-git`: 246k, read whole at the preflight and again at `commit-artifacts` (Rulings 68 and 69), against 77–111k in slices.
- `phase-handoff`: 139–277k against 50–139k.
- `addressing`: 67k against about 2k.
- `cost-emission`: 70k against 15–33k.
- `model-routing/classification`: 48k against about 22k.
- The four split rulebooks' parts: 2–24k each.

**The early whole reads carry the cost.** The scratch script `refcost.py` prices each reference read in a main session as tokens (characters / 4) × ($8 per million for the 1-hour cache write + $0.20 per million × the main calls after it). Its output, `refcost-all.txt` (scratch), gives runs 1–6; the ledger gives run 7 and run 5's today's-`main` figure.

| Run | New | Comparison |
|---|---|---|
| 1 conformance | $3.62 | $1.75, baseline |
| 2 prd-ground | $3.20 | no transcript |
| 3 release-notes | $2.91 | $1.00, today's `main` |
| 4 scan | $1.68 | $0.88, baseline |
| 5 run B | $2.19 | $0.89, baseline; $1.29, today's `main` (ledger) |
| 6 route 3 | $5.33 | $1.99, today's `main` |
| 7 design | $5.92 (ledger) | $2.11 (ledger) |

`refcost-all.txt` holds no run-7 row, so run 7's figures are the ledger's. The repeated whole reads, which dropping Ruling 69 would save, came to $0.00–0.75 per run, because they come late. The cost is the early whole reads that every later call carries: `phase-handoff`, `specs-repo-git`, `addressing`, `classification` and `run-flags` (ledger).

The options put to the user after run 7 (ledger): **A**, keep part 1 as is; **B**, drop Ruling 69; **C**, allow section reads of the procedure references again; **D**, split the large procedure references by entry point, with their needs, as part 1 did for the rulebooks.

**The user's decisions**, each marked USER DECISION in the ledger. The ledger gives times in UTC without dates; the dates follow from the runs' windows in each `measure.txt`.

| When | Decided |
|---|---|
| 2026-10-21, 09:15Z | The scan slot is an Epic-key scan, `/security-workflows:scan BOOK-2-01-02`, in place of `d65028a2` (the research picked session `bf055d1f` as its baseline). The runs go shortest first: conformance, prd-ground, release-notes, scan, run B, route 3, design. |
| 2026-10-21, 11:50Z | After run 1's cost: continue as is; Rulings 68 and 69 stand; decide with the full data after the seven runs. |
| 2026-10-22, 09:3x Z, after run 7 (the ledger gives no minute) | (1) Keep part 1 as is: option A; Rulings 68 and 69 stand. Option D, splitting `phase-handoff`, `specs-repo-git`, `addressing`, `model-routing/classification`, `run-flags` and `cost-emission` by entry point, is the next sub-project, with its own spec. (2) Run 5 gets an attribution run on today's `main` on the same inputs, then a blind three-way comparison. (3) The unloaded `escalation-rules core` goes into that sub-project, as an explicit load step in every command that asks; it is not fixed in part 1. |

**Process finding: `escalation-rules core` was never loaded in runs 4 and 7.**

- Run 4 (scan) called the loader only for `run-flags`, `addressing` and `model-routing`. It read `specs-repo-git`, `implementation-format`, `read-only-repos`, `feedback-emission` and `cost-emission` by path, and never loaded `next-phase-offer dev`, `session-hygiene resume-pointer` or `escalation-rules core`. It still printed correct next steps and the `/compact` or `/clear` hint, and wrote `resume.md`. Runs 1 and 3 loaded every part (ledger).
- Run 7 (design) never loaded `escalation-rules core`, whose "Ask, don't guess" the command restates inline, nor `version-line` or `untrusted-content`. It read `next-phase-offer dev` and `session-hygiene guidance` by path. Its output complied anyway: its questions had the §0 shape, and its version line named the edits.
- **Attribution: pre-existing, not part 1.** Today's `main` skips the same: sessions `f9684b8b` (run 3's today's-`main` run) and `beebc3f3` (run 6's baseline) never load `escalation-rules` at all. Part 1 runs load more parts, not fewer: runs 5, 6 and 7 load `escalation-rules review`. The ledger's reading of the cause: a parenthetical citation of a rule the command restates is read as a source note, not as a load step.
- By the user's decision (3) above, the fix goes into the next sub-project.

## 5. Run 5: the two-way verdict and its attribution

**The two-way verdict ranked the baseline narrowly better.** The baseline was `5023b937` (X) and the new run `67b859d4` (Y). Both built, both passed (74 and 77 tests), and both suites killed every mutant the judge tried. The new run was more correct: it showed no "No books match" while the list loaded or after a failed load. Against it: five post-re-review edits that went unreviewed (disclosed, and allowed by the one-re-review cap), a count slip, stale spec line numbers, and a branch confirmation it promised and did not give. The ledger found no rule absent at its step and judged the divergence "not clearly part 1".

**The attribution run.** By the user's decision, today's `main` (dev-workflows 4.29.0, workflows-core 1.43.0, loaded from the plugin cache) ran on the same inputs as session `a759c4a3`, 2026-10-22 09:52–11:50Z. It cost $17.51 in total (main $12.07), against the new run's $18.52 (main $13.12) and the baseline's $15.75 (main $11.72) (`measure-attr.txt` and `measure.txt`).

**The three-way verdict ranks C (new) > A (today's `main`) > B (baseline).** C over A is narrow; A over B is clear. All three applied, built and passed (A 76, B 74, C 77 Karma tests). Against 17 mutants, C killed 17, A 16 (its failed-load path is untested), and B 15 of the 15 that apply to it.

**The three-way supersedes the two-way.** The spec sends a result judged worse to today's version on the same inputs, to tell whether part 1 caused it. The three-way is that comparison, and it ranks the new run above today's `main`. It also ranks the baseline last. The baseline shows "No books match" while the list loads and after a failed load, which the three-way judge confirmed with a probe and weighed decisively; the two-way judge had seen the same edge and called it "real but small". So the two-way's narrow preference for the baseline does not survive, and run 5 shows no part-1 defect. No fix round followed.

**The `CLAUDE.md` difference.** The baseline and today's-`main` runs each committed an unrelated `CLAUDE.md` line about running the tests without watch mode; the new run did not. Their orchestrators had added an improvised "decision point / session note" about watch mode to the Phase 4.5 change summary, beyond its template. The template is identical in 4.29.0 and on the branch. The new run's summary followed the template, so its instructions agent found nothing to add. This is run variance, not part 1 (ledger).

## 6. The test bed after the runs

From the ledger's "Task 14 CLEANUP" entry. Both copies were backed up before the cleanup.

- **The code copy.** Pull requests #3 and #4 are closed, and run 5's two replay branches are deleted. `feat/BOOK-2-01-02-storefront-ratings` was force-pushed back to `eb694d0` (with a lease on `e45e1a7`), which drops run 6's commits `d5dab21` and `e45e1a7` from the copy. The local branch is at `eb694d0`, and `master` (`af46545`) is checked out. Pull request #1 is open at `eb694d0` and #2 at `29eb857`, as before Task 14.
- **The specs copy.** Pull requests #2, #4 and #5 are closed, and the `brd/`, `prd/`, `design/` and `conformance/` branches are deleted. A restore commit, `3600a92`, sits on `main` with the tree of `40aa165`, the `main` from before Task 14, and is pushed. Only `main` is on the remote.
- **The demo repositories.** The snapshot matched 18 of 18 before run 1, after run 7, before the attribution run and after the cleanup.

## 7. Not covered here

- The gate run with `ASSERT_PUBLISHED=1`, the dating of the changelogs, the merge and the push. They are the controller's, after this record.
- Ruling 38's question to the user: whether to fix `check-docs.sh`'s stale check-16 header and port the shared body to the internal editions. The ledger records it for the merge and holds no answer yet.

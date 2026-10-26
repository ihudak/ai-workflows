# Review of a980e58 — piece review (dev-workflows 4.32.0), against its design

**Date:** 2026-10-26 · **Commit:** `a980e585` (merge of `iv-gu/implement-piece-review` into `main`; first parent `bf9cc825`, second `dd11ef27`) · **Design:** `docs/superpowers/specs/2026-10-25-implement-piece-review-design.md` · **Plan:** `docs/superpowers/plans/2026-10-25-implement-piece-review.md` · **Verification record:** `docs/superpowers/verification/2026-10-25-implement-piece-review.md`

**Method.** Read-only, on a detached worktree at `a980e585`. Four parallel reviewers covered (1) `pieces.py` and `run-state.py`, run against hand-built fixtures; (2) `commands/implement.md` against design §2 and §3.1; (3) `code-review`, `design-reviewer`, `design-format` and `/design` against §3.1 points 4 and 6 and §3.2; (4) release hygiene, the records, the §4–§6 obligations and the merge. Every finding below was then re-checked against the tree by the orchestrating session: script findings by reproduction, prose findings by reading the quoted text in place. Line numbers are at `a980e585`.

**Verdict.** No BLOCKER and no MAJOR. The build follows the design closely, and wherever it departs, nearly every departure is recorded in the CHANGELOG or as a ruling. One departure from the shared triage authority is not reconciled (F1). Two loops lack a stated bound (F2, and N1, which is unreachable), and one silent fallback hides drawn pieces (F3).

## Findings

| # | Severity | Where | Finding |
|---|---|---|---|
| F1 | MINOR | `plugins/dev-workflows/commands/implement.md:991` | Split-round dedup contradicts `workflows-core:finding-triage` § The step, unreconciled |
| F2 | MINOR | `plugins/dev-workflows/commands/design.md:405` | Phase 5.5's malformed/overlap fix loop has no bound |
| F3 | MINOR | `plugins/dev-workflows/scripts/pieces.py:163-167`, `references/design-format.md:220-221` vs `:261-262` | `_N/A` followed by drawn pieces reads silently as one piece |
| F4 | MINOR | `plugins/dev-workflows/scripts/pieces.py:269-278, 307-309` | A non-UTF-8 diff path on a `none` design writes invalid UTF-8 JSON |
| F5 | MINOR | `docs/superpowers/verification/2026-10-25-implement-piece-review.md:259` (P22), `docs/superpowers/to-fix.md:131` | Design §4's "draws no pieces" `/design` test was never run on a small Epic; nothing tracks it |
| F6 | MINOR | verification record `:257-258` (P21) | Design §5's to-fix entry was replaced by a ruling the design said not to make |
| F7 | MINOR | `pieces.py` `--selftest` | Selftest gaps (listed below) |
| N1 | NIT | `implement.md:994` | Re-classification re-run loop has no bound (unreachable on a split round) |
| N2 | NIT | `implement.md:991` | Re-review selection's conditions read as a conjunction |
| N3 | NIT | `commands/design.md:451` | Phase 6's re-check trigger omits the `Target` line |
| N4 | NIT | `docs/commands/design.md:72, 80` | Docs page drops conditions the command states |
| N5 | NIT | design §3.1 pt 2 vs `agents/design-reviewer.md` *Pieces* | Design says the reviewer "refuses" a malformed section; build grades it a declinable `MAJOR`, with no ruling |
| N6 | NIT | `pieces.py:197-221`, `:105-110`, `:128-131` | Parser leniencies and one empty defect message |
| N7 | NIT | `.claude/rules/dev-workflows-implement.md:23` | Edited bullet now parses ambiguously |
| N8 | NIT | verification record `:5, :21, :30` | Record's state and gate result predate the merge of `main` |
| N9 | NIT | `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md:169` | IMP-G1's *Current state* contradicts its *Resolved* heading |

### F1 — Split-round dedup contradicts `finding-triage`, and the conflict is not reconciled (MINOR)

- **Text.** `implement.md:991`: "a finding a later review of the round raises at a location and with a claim an earlier review's finding holds is that same finding, verified once, and takes its disposition — the match made between findings only".
- **Authority.** `plugins/workflows-core/references/finding-triage.md:86-90`: "For each finding, **before any grouping or deduplication**: 1. Verify its own claimed consequence … Another finding's outcome, however adjacent, never settles this one." The triage sub-step tells the run to load and follow that reference, so the executing agent holds two instructions that disagree.
- **Failure scenario.** A piece review raises a finding that triage dismisses. The overall review then raises the same claim at the same site, backed by cross-piece evidence the piece reviewer could not see. Followed literally, `implement.md` gives the overall finding the dismissal without verifying it, which throws away the very edge the overall review exists for. Followed literally, `finding-triage` has the run verify both findings, and "one finding" no longer holds.
- **Against the design.** §3.1 pt 5 does want "a finding two scopes both made is one finding". §6, though, says combining scopes is `/implement`'s own step, "where it needs a change in the shared reference, `.claude/rules/plugin-updates.md` gets the coupling bullet". Plan Task 5 step 1 asks for wording that satisfies `finding-triage`, or else a recorded ruling. Neither happened. The plan's `:278` carries the sentence over from the shelved branch, and no P-ruling or coupling bullet covers it. `plugins/workflows-core` is unchanged in this merge.
- **Fix direction.** Either verify every finding first and merge afterwards (the overall finding is verified, and a confirmed duplicate collapses into one), which satisfies `finding-triage` with no shared change, or amend `finding-triage` to license this merge and add the coupling bullet.

### F2 — `/design` Phase 5.5's fix loop has no bound (MINOR)

- **Text.** `commands/design.md:405`: "`status: malformed` → fix the section in the file … and run it again, until it prints `none` or `pieces` … removing the section, which leaves one piece, always ends this". An overlap is "fixed as a malformed section is, and both commands run again".
- **Defect.** The sentence names an exit, removing the section, but never says when to take it. A run whose rewrites keep trading one defect or overlap for another has no rule that stops it. It asks the user nothing, as the design requires, but it is not sure to end. Design §2's anti-goal on bounded loops names `/implement`'s review loop, and the same principle applies here.
- **Fix direction.** Give an explicit cap, e.g. "after a second `malformed` result, remove the section and name the removal in the Final report".

### F3 — An `_N/A` line followed by drawn pieces reads silently as one piece (MINOR)

- **Contradiction inside `design-format.md`.** `:220-221` allow `_N/A — <why>_` only "as its only line", and the section "holds nothing else". `:261-262` say it reads as `none` "where the section's first non-blank line begins `_N/A`", which is what `pieces.py:163-167` does. `line.lstrip()` also accepts an indented `_N/A`, though "every line of the section starts at the beginning of its line".
- **Reproduced.** A section of `_N/A — one change_`, then `Reason: r` and two pieces, gives `"status": "none"`.
- **Effect.** A hand edit that leaves a stale `_N/A` above real pieces makes every consumer ignore them, with no message. `/implement` makes one review and prints nothing, because `none` is not "unusable". `design-reviewer` takes the `status: none` path and can at most recommend drawing pieces that are already drawn. Design §3.1 pt 2 wants a section the run cannot use to be named as unusable.
- **Fix direction.** Read the section as `none` only when the `_N/A` line is its only non-blank line, and anything else as `malformed`. Then align `:261-262` with that.

### F4 — A non-UTF-8 diff path on a `none` design writes invalid UTF-8 JSON (MINOR)

- **Defect.** The not-UTF-8 check runs only on `status: pieces`. On `none`, the commonest case, the raw bytes go into `unassigned` on stdout, and on the malformed-by-UTF-8 result the raw path is in `unassigned` too. The docstring (`:16-20`) says a non-UTF-8 path "makes the status malformed" without that qualification.
- **Reproduced.** `printf 'x/\xff\0' > p; printf '# D\n' > none.md; pieces.py assign none.md p | python3 -c '…json.loads(…decode("utf-8"))'` gives `UnicodeDecodeError … byte 0xff in position 92`.
- **Effect.** `implement.md:962` routes "output that does not parse" to `design.md's ## Pieces unusable … reviewed as one piece` and records it in `assumptions`. A strict reader would therefore print a false "unusable" on a design with no Pieces section. `/design` is safe because its reader uses `errors="replace"`. The population is small, since it needs a non-UTF-8 file name in the diff.
- **Fix direction.** Emit with `ensure_ascii=True` (`json.dumps`'s default) after decoding paths with `surrogateescape`, or drop the raw paths from the output.

### F5 — The design's one-piece `/design` test never ran on a small Epic (MINOR)

- **Design §4.** "An Epic that should get one piece (`BOOK-1-01` …): it should draw none." The live run drew four. Ruling P22 holds that the expectation was an unmeasured premise and that four pieces hold under the format's `Reason:` model. The design's status note records the same.
- **P22 is sound on its ground.** The earlier `/implement EPIC-BOOK-1-01` ledger (`docs/superpowers/verification/2026-10-17-implement-coding-subagents-ledger.md:228-229`) records HIGH-RISK, 101 files and +8,909 lines, against BOOK-3-01's 36 files and +4,161.
- **Still missing.** No run shows `/design` declining pieces on a change one reviewer can review in depth, so the guard against over-drawing (design §2's last anti-goal) is untested live. `to-fix.md` PR2 tracks only the cost of more than two pieces.
- **A signal worth noting.** In both runs `/design` offered its piece count as the `(Recommended)` option, and neither `design-reviewer` pass questioned the `Reason:` (record `:178`, `:206`).
- **Fix direction.** Add a to-fix item: one `/design` run on a genuinely small Epic, expecting no `## Pieces`.

### F6 — Design §5's to-fix entry was replaced by a ruling (MINOR)

- **Design §5.** The mocked-writer test-strategy finding "goes into `docs/superpowers/to-fix.md` … One instance, recorded, not ruled on."
- **What happened.** Ruling P21 decides instead that `/design` itself has none of this defect, on one `/design` run (BOOK-3-01), and writes no entry. The ledger (`:109`) still refers to "the to-fix entry Task 9 writes". The deviation is disclosed, with its cost if wrong, but it is a ruling made from a single sample where the design asked for a record, not a ruling.
- **Fix direction.** Write the one-line to-fix entry the design asked for, citing P21 as current evidence, and correct the ledger's reference.

### F7 — `pieces.py` selftest gaps (MINOR)

Each of these behaves as documented when run by hand, but nothing pins it:
- `_N/A` followed by other lines (F3);
- a non-UTF-8 path on `none`, and stdout encoding generally (F4);
- a paths file with no trailing NUL, or with consecutive NULs;
- case sensitivity, and dotfiles (`*.py` matches `.hidden.py`);
- `**` as the whole entry, and `a/**/`;
- a `## Pieces` heading with trailing whitespace or CRLF, when only that line has it;
- a closing fence longer than its opener;
- kebab-case edges (`-a`, `a-`);
- `Contract:` before `Files:`, and an empty `- Contract:` line.

### NITs

- **N1** (`implement.md:994`). The `### Re-classification` arm's **Re-run the full review** re-invokes `code-review` without limit. Each answer adds a review beyond design §3.1 pt 5's bound. It is unreachable on a split round, because `code-review` never returns a Re-classification on a brief with `Scope:`, and the unbounded re-run was already true at `MODERATE` before this change.
- **N2** (`implement.md:991`). "a review of each such piece that has no review yet, whose first-round review left a survivor …, or whose fresh diff differs …" chains three alternatives with commas and one final "or", so it reads as a conjunction that contradicts itself. Write "or whose" before the second clause too.
- **N3** (`commands/design.md:451`). Phase 6 re-runs the pieces check after an edit to `## Pieces` or the `Repos` line. The `- **Target**:` line also decides which repository `Files:` patterns are relative to (`design-format.md:248`), and it is not in the trigger. This is rare, since `Target` comes from the Epic.
- **N4** (`docs/commands/design.md:72, 80`). The page says Phase 5.5 always runs `assign` and that a malformed section or an overlap "is fixed before the review". The command adds "where Phase 4 recorded a commit", and has three report-and-continue exceptions: a non-zero exit, a non-UTF-8 path, and no recorded commit.
- **N5** (design §3.1 pt 2: "`design-reviewer` refuses such a section"). The build grades a malformed section `MAJOR`, which Phase 6 offers and the user may decline. That follows plan Task 2 step 3, and `/implement`'s fallback degrades safely, but no ruling records the design's "refuses" becoming a declinable `MAJOR`. In practice only overlap among files the design creates reaches review unfixed.
- **N6** (`pieces.py`).
  - `- Contract:` before `- Files:` is accepted, though the format fixes the order (`:197-221`).
  - A second `## Pieces` section is ignored (`:105-110`), and the format states no uniqueness rule either way.
  - `` `a`,, `c` `` yields the defect message "the Files entry  is not in backticks", with an empty name (`:128-131`).
- **N7** (`.claude/rules/dev-workflows-implement.md:23`). "returns no `### Re-classification` on a `MODERATE` brief or one with a `Scope:` line naming only `SIMPLE` on a higher one" now lets "naming only `SIMPLE`" attach to the `Scope:` clause. `implement.md:994` and `code-review.md` are unambiguous. A comma after "line" fixes it.
- **N8** (verification record `:5, :21, :30`). "Not yet merged", "runs beside workflows-core 1.45.0" and the gate chain's `EXIT=0` were measured at `7c436653`, before `8f96c887` merged `main` (workflows-core 1.47.0, security-workflows 0.4.0, product-workflows 3.37.0). No dev-workflows value moved, but the record does not cover the merged tree. This review's gate run does (below).
- **N9** (`feature-gaps-review.md:169`). IMP-G1's heading says "Resolved by dev-workflows 4.32.0", but its *Current state* line still says "no spec … no plan, no branch/commit".

## Design points verified as implemented faithfully

- **§3.1 pt 1–3, when it splits.**
  - A split needs a `design.md` in `applicable_spec` with a `## Pieces` that `pieces.py assign` reads, and the review diff's own paths, never a writer's report, must touch two or more pieces.
  - A section the run cannot use, or a script failure, gives one review with the printed line, recorded in `assumptions`, asking nothing.
  - One touched piece, or none, gives today's review.
- **§3.1 pt 4, the split review.**
  - Piece reviews are dispatched in one response. Each gets its piece diff and a `Scope:` naming the piece, its files and its `Contract:` items, plus `applicable_ard` and `Spec-named tests` but no `applicable_spec`.
  - The overall review follows. It gets the whole diff, the piece returns, and the unassigned paths to review in depth. It checks contracts on both sides, duplicated helpers, conventions and cross-piece behaviour, and raises nothing a piece review raised.
  - Only the overall review traces requirements. It writes `conformance.summary` and feeds step 7.5.
  - Every return is written to its own file before it is read.
- **§3.1 pt 5, triage and fixes.**
  - The round's verdict is the worst of its scopes'.
  - Settle prompts and the offer are asked once per round.
  - One `review-fixer` pass takes every survivor.
  - The re-review round re-runs each piece whose diff changed and each piece that handed the fixer a finding (read from triage records, never the Fix Report), then the overall review.
  - Step 8 is one unsplit review.
  - The bound holds on every reachable path: the first round is pieces + 1, the re-review round at most pieces + 1, and step 8 is one review.
- **§3.1 pt 6.** `Spec-named tests:` is on every `/implement` brief that carries `applicable_spec`, step 8's included, and on piece reviews. `/vuln` and `/upgrade` are untouched: the input is `/implement`-only and optional.
- **§3.1 pt 7.**
  - The Phase 5 report lists `<round> — <scope> — <verdict>` and `overall (<n> only here)`.
  - The cost section counts every review.
  - The implementation record (Phase 4.7) is unchanged.
- **§2 anti-goals, unsplit path.**
  - The only change on a run that does not split is the `Spec-named tests:` line, one deterministic `pieces.py assign` call (only where a `design.md` is in scope, temp file trapped, nothing printed), and the sanctioned "unusable" line.
  - No second coding path was added, and the coding flow is unchanged.
  - No one-writer machinery leaked into `plugins/`: `run-lock`, `SendMessage` resumes, writer units, `Writers:` and `Builds after:` occur only as `pieces.py` selftest cases for malformed input.
- **§3.2 format, `/design` and `design-reviewer`.**
  - The section matches the design's block.
  - Reason and boundary are both required, with no count rule.
  - Tests go in `Files:`, and shared tests in none.
  - Names are kebab-case and unique.
  - An unnamed file goes to the overall review and is not barred from editing.
  - `/design` asks nothing new.
  - `design-reviewer` judges the reason and the boundary, and a missing-but-needed section draws at most a `MINOR`.
  - The multi-repository exclusion, which the design does not mention, is recorded as rulings P13 and P14 and stated consistently in every copy.
- **Departures recorded.** The exclusion of companion runs, the "has no review yet" re-review clause, the fallback to one review when the re-review round no longer splits, and the one-shot Re-classification re-invocation all appear in the CHANGELOG and invariants.
- **Scripts.**
  - `pieces.py` implements every malformed case `design-format` lists and rejects nothing it doesn't.
  - Matching is a hand-built `re.fullmatch` with no `fnmatch`, case folding, locale or normalisation, so it is deterministic and identical on macOS and Linux (§7).
  - Exit codes are 0, 1, 2 and 4, as the callers expect.
  - `run-state.py`'s `pieces` and `reviews` keys are type-checked, are handled by `set` and `remove` as `files` members are, and are held equal to `implement.md`'s key list by the selftest.
- **§4 proof.**
  - Run C ran, with its split pre-checked.
  - Four blind judges compared C with A, labels swapped within pairs: all rated C slightly better, with no BLOCKER or MAJOR. One judge compared C with B.
  - Cost was measured by agent, scope and main session.
  - The $84.51 overrun past $80 was explained before release (record §3, the rationale, the CHANGELOG intro) and accepted by the user.
- **§5.** The 2026-10-24 design carries its status note. The one-writer A/B record and its ledger exist, and no one-writer code is in this merge.
- **§6.**
  - The claim-expiry sweep finds no stale "exactly one review" statement in `plugins/`, `CLAUDE.md`, `.claude/rules/` or `docs/maintainers/`.
  - Section-inclusion rules are updated wherever they live.
  - The counts in `CLAUDE.md` still hold: 14 agents and 19 reference files.
  - The CHANGELOG is dated, and `plugin.json` and `marketplace.json` agree on 4.32.0.
  - `plugins/workflows-core` is unchanged, every cited workflows-core rule exists at 1.45.0, and so no coupling bullet is needed (F1 aside).
- **The merge.** The tree of `a980e585` equals its second parent's, and the earlier merge `8f96c887` dropped nothing from #76 (B02), #77 (B04) or #78 (B07).

## Gate chain

The full chain of `.github/workflows/validate-catalog.yml`'s `run:` steps, run as one `&&` chain on the worktree at `a980e585`, exits 0. That run includes `pieces.py --selftest` (PASS, 52 checks) and `run-state.py --selftest` (PASS, 97 checks).

This covers the merged tree, which the verification record's own gate run (at `7c436653`) does not (N8). The gates pass, yet each finding above stands: none of the gates can see these defects.

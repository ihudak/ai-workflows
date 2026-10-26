# Post-merge review of #82–#85 and #87

**Date:** 2026-10-26 · **Method:** read-only. Five parallel Opus reviewers each took one merged PR, its batch entries (`2026-10-26-fix-batches.md`, `2026-10-26-bugs-review.md`, `2026-10-26-feature-gaps-review.md`) or, for #85, the findings of `2026-10-26-piece-review-a980e58-review.md`, and judged the merge against them and the tree. Each finding was verified at the merge commit, and #83's MAJOR 1 was re-checked on `main` at `417c5c85`. Line numbers are at each PR's merge commit. The gates pass at every merge.

**Verdict.** Every entry the five PRs claim is fixed or recorded as split off, except BRD3-B2 (partly, #83) and PRD2-PROP-B6 (partly, #82). The PRs introduce 2 MAJOR, 13 MINOR and 12 NIT defects. Fix #83's MAJOR 1 first: it is a live contradiction in a shared reference.

## #83 — B10, `/brd-reconcile` (merge `80df9e1d`)

| # | Sev | Where | Defect | Fix |
|---|---|---|---|---|
| 83.1 | MAJOR | `plugins/workflows-core/references/phase-handoff.md:333` (and `reference-parts/phase-handoff/require-on-main.md:206`) | Says `/brd-reconcile` takes the exception "at two sites and never at its ordinary Phase 0 gate … No other caller may take either exception". BRD3-B19's fix (`brd-reconcile.md:330-336`) now proceeds past a stopping row or row F on the most recent prompt while the package is undetermined. The run loads both instructions, and following the shared one re-creates BRD3-B19. The same "two exceptions" claim is in `dev-workflows/commands/ready.md:24`, `dev-workflows/docs/commands/ready.md:54, :82`, and both plugins' `docs/roles-and-phases.md:12`. | Add the undetermined-package fallback to §3.7 as a third site, regenerate the part, and update the five copies. — **Fixed in workflows-core 1.54.0, dev-workflows 4.37.0, product-workflows 3.44.0** |
| 83.2 | MAJOR | `brd-reconcile.md:2210` (Phase 10) with the adoption rule `:1146-1150` | Adopting a `frozen` pass counts the adopted records as this run's, but not the records Phase 5 step 3 superseded or reopened because of them. Those are missing from the changed-id set, from Phase 12's "reopened or superseded here" (`:2620`), from the Final report (`:3119`) and from Phase 14's *this run reopened* (`:2817`). A dependent `conditional_on` a superseded `[CD#2]` can then only take `inherited-unchanged`, the BRD3-B3 shape again, and `advance_ready` can read `yes` over a record the stopped run reopened. | On adoption, read the register for `Superseded … by` and `Reopened` paragraphs that name an adopted id, and count those records as this run's in Phases 10, 12 and 14 and in the Final report. |
| 83.3 | MINOR | `product-workflows/docs/brd-workflow.md:283` | The flag table, which claims to show "exactly what each command accepts today" (`:271`), lists only `--sent` for `/brd-reconcile`, not BRD3-B13's `--free-text`. | Add it. |
| 83.4 | MINOR | `brd-reconcile.md:2697-2702` | Phase 12 says where the dated file "already exists, this run adds a new pass beneath … under its own heading". Phase 5 now opens the pass, so the file always exists by Phase 12, and a literal reading writes a second heading. | Say that the same-day append happens when Phase 5 opens the pass. |
| 83.5 | NIT | `brd-reconcile.md:325-329`; `.claude/rules/brd-route.md:29`; the docs artifact table | "before anything else reads a file", yet the gate now reads the review's section-1 `Package reviewed:` line first. | Name that read as the one exception, in all three places. |

BRD3-B2 is only partly fixed: 83.2, plus the gaps the PR itself recorded as to-fix D20 (a)–(c).

## #84 — B11, `/brd-package` (merge `14934af5`)

| # | Sev | Where | Defect | Fix |
|---|---|---|---|---|
| 84.1 | MINOR | `brd-reconcile.md:1834-1847` against the class-1 table `:1851-1870` | The new section-12 resolution sends a row that names a bundled filename to its working document. Before, every such row was class 2. Class 1 has no row for `grounding/code-grounding.md`, `design-grounding.md`, `baselines.md`, `interview/customer-questions.md` or the parent's `brd/brd-defect-log.md`, so those fall to "Corrected in place". A customer row can then rewrite a verified `[CG#n]`, or write to the parent's defect log, which the cross-BRD guard (`:109-116`) does not list for this phase. | Add class-1 rows for those documents (refuse, naming each one's owner; guard the parent's log), or rule that a resolved document with no row is `refused-with-reason`. |
| 84.2 | MINOR | `product-workflows/CHANGELOG.md:12`; `docs/commands/brd-package.md:273-277` | Both say same-dated files beside no bundle are scratch and overwritten. The command (`commands/brd-package.md:505-524`) treats them as scratch only when the self-review is on no ref and no directory holds a prompt naming this key and date; otherwise it stops with `BRD_PACKAGE_BUNDLE_EXISTS`. | State both stop conditions in both places. |
| 84.3 | MINOR | `commands/brd-package.md:1490-1493` (rule 5) | "never parsed from a name alone — a key that list does not hold is named in part 2 all the same". The only source of such a key is the filename, so it is parsed and then written into the customer prompt. This contradicts `bundle-packaging.md:505` and `CLAUDE.md`'s resolve-against-a-known-set rule. | Report the unmatched file as unresolved in the Final report, and name no key for it in part 2. |
| 84.4 | MINOR | `commands/brd-package.md:1492-1493`, `:1564-1567` | Rules 5 and 8 add Final-report items (an unresolved key; a reference to a package not included) that the Final report's list (`:1848-1871`) does not carry, though it lists rule 7's like item. | Add both to the list. |
| 84.5 | NIT | `docs/commands/brd-package.md:184` | "plus a manifest and any dependency package". Rule 5 now copies only the prerequisite's own files, as `:202` and `:464` say. | "plus a manifest and each prerequisite's own files". |

## #82 — B09, the proposals (merge `3ef18497`)

| # | Sev | Where | Defect | Fix |
|---|---|---|---|---|
| 82.1 | MINOR | `prd-proposal.md:254-255` against `:736-739`; `brd-proposal.md:164-166` against `:803-806` | PRD2-PROP-B6's fix archives a lone brief (no `proposal.md`) in Phase 8, but Phase 10's `deliverable_paths` declares archives only "on a revision". The archive is classed OTHER by `phase-handoff` §2.3 and left untracked. Rare, because it needs a hand-deleted `proposal.md`. | Declare "a brief Phase 8/9 archived, on any run" apart from the revision clause, in both commands and both docs pages. |
| 82.2 | MINOR | `docs/commands/brd-proposal.md:78` | The page still says nothing narrows a check to an umbrella and that check 6 grades no umbrella. `proposal-reviewer.md:175-187, :343-347` now give check 6 an umbrella form and make check 10 `N/A` there, and `commands/brd-proposal.md:715-720` says so. | Rewrite the sentence to match the command. |
| 82.3 | NIT | `prd-proposal.md:691-695`; `brd-proposal.md:759-763` | FBB-B10's attribution re-check fires only after the last edit to `proposal.md`, so a later fix to `proposal-brief.md` alone is never re-checked. | Trigger it on the last inline edit to either artifact. |
| 82.4 | NIT | `docs/commands/prd-proposal.md:65`, `brd-proposal.md:71`; `.claude/rules/product-workflows.md:47` | The docs' "what the handoff commits" leaves out the profile (which `:51` / `:55` of the same pages say it commits), and the rules map line leaves out the archived prior. | Add each. |
| 82.5 | NIT | `workflows-core/CHANGELOG.md:11` (1.49.0) | "a stronger class beside": for `/brd-proposal` the umbrella `proposal.md` is advisory, the same class as the profile, not a stronger one. | "an equal or stronger class". — **Fixed in workflows-core 1.54.0** |

PRD2-PROP-B6 is partly fixed (82.1).

## #87 — B12, `/document` (merge `417c5c85`)

| # | Sev | Where | Defect | Fix |
|---|---|---|---|---|
| 87.1 | MINOR | `docs-workflows/docs/workflow.md:83` | Still says keyed `/document` "finishes on a branch". Since 1.19.0 a "no branch" answer at *Revise plan* leaves the pages uncommitted. The PR qualified `getting-started.md:101` and `docs/commands/document.md:69`, not this page. | Add the same qualifier. — **Fixed in docs-workflows 1.23.0** |
| 87.2 | MINOR | `commands/document.md:943` | Phase 6.4's new exit names two cases ("where the re-run found nothing, and on *Proceed to review anyway*"). Two more outcomes that are not Cancel have no exit: the `NEEDS HUMAN` "skip the check" (`:934`) and "Show remaining violations and let me fix manually" (`:938`). An agent can read the list as closed and jump to Phase 7, which re-creates DOC-A-B2. | "On every outcome of this branch but Cancel, go on to Phase 6.5." — **Fixed in docs-workflows 1.23.0** |
| 87.3 | MINOR (judgement) | `commands/release-notes.md:505` with `commands/document.md:777` | `/release-notes` presents `/document`'s Phase 5.8 per-claim prompt, which now marks "Document as intended (spec) (Recommended)". In `/release-notes` that choice publishes the specification's phrasing in customer-facing notes, with no marker, over shipped code that contradicts it (`:512`). Before, nothing was recommended. The CHANGELOG reports only the label change, and D22 covers only the batch array. | Give `/release-notes` its own per-claim array, or widen D22 to cover the recommendation. — **Recorded as to-fix D23 (the user's decision)** |
| 87.4 | NIT | `docs/commands/document.md:93` | "PASS WITH RECOMMENDATIONS with no MAJOR survivor … goes straight on": where triage dismissed every finding, `finding-triage`'s first settle prompt comes first (`document.md:1099`). | Say so. — **Fixed in docs-workflows 1.23.0** |
| 87.5 | NIT | `docs/commands/document.md:63` | D4's exception is stated without its new override: a base named at *Revise plan* puts the gate back (`document.md:324, :514, :573`). | Add it. — **Fixed in docs-workflows 1.23.0** |
| 87.6 | NIT | `docs/superpowers/to-fix.md:124` (D22) | "`release-notes.md` Phase 4's code-discrepancy step": it is Phase 6, "Render the draft" (`release-notes.md:401-518`). | "Phase 6's". — **No change needed: D22 was closed and removed from to-fix in docs-workflows 1.20.0 (batch B13)** |

## #85 — the fixes to piece review (merge `4e2423d9`)

F1–F7 and N1–N9 are fixed. F3 and F4 were reproduced against the old and new `pieces.py`; the selftest passes 76 checks. N8 is partly fixed (85.1).

| # | Sev | Where | Defect | Fix |
|---|---|---|---|---|
| 85.1 | MINOR | `docs/superpowers/verification/2026-10-25-implement-piece-review.md:276` | "No file under `plugins/dev-workflows` changed between `7c436653` and `a980e585`": `CHANGELOG.md` did, at `d61872a6` (the intro's cost text) and `dd11ef27` (the date). The conclusion holds, since no §2 value is in the CHANGELOG. | "no file but `CHANGELOG.md` (`d61872a6`'s intro, `dd11ef27`'s date)". — **Fixed in the verification record (no plugin change)** |
| 85.2 | MINOR | `dev-workflows/commands/design.md:571` | The Final report item names only the multi-repo removal of `## Pieces`. F2 adds a second removal, a section its one fix leaves malformed or overlapping, which Phase 5.5 (`:405`) and Phase 6 (`:451`) say to report. | Add "or one its one fix left malformed or overlapping (Phase 5.5, Phase 6)". — **Fixed in dev-workflows 4.38.0** |
| 85.3 | NIT | `design-format.md:276-277`; `pieces.py:22-23`; `CHANGELOG.md:17` | "a byte that is not [UTF-8], in a path or in the design's own text, is written `\xNN`": design text quoted in `defect` passes through `show()` (`errors="replace"`) and prints `�`. The output is valid UTF-8 all the same. | Use `escaped()` in the defect messages, or qualify the claim. — **Fixed in dev-workflows 4.38.0** |
| 85.4 | NIT | `design.md:405` | "a section still malformed, or still overlapping, after it is removed": reads as a section malformed after its removal. | "a section its one fix leaves malformed or overlapping is removed, never fixed a second time". — **Fixed in dev-workflows 4.38.0** |
| 85.5 | NIT | `design.md:405` | "remove the section … which then prints `none`": with a second `## Pieces` heading (malformed since 4.33.0), removing one leaves the other. | "remove every `## Pieces` section". — **Fixed in dev-workflows 4.38.0** |
| 85.6 | NIT | `dev-workflows/docs/commands/implement.md:96` | N1's new stop (a further `### Re-classification` after **Re-run** stops the run) is not on the page. | Add "and a third stops the run". — **Fixed in dev-workflows 4.38.0** |

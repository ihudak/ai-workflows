# D32 — Document lineage, part 4: `/document` and `/release-notes` report the chain

Date: 2026-11-03. To-fix entry: **D32**, follow-up (3). Builds on parts 1–3 (`2026-11-03-d32-document-lineage-design.md`, `2026-11-03-d32-lineage-part2-prd-ard-design.md`, `2026-11-03-d32-lineage-part3-brd-design.md`), whose decisions bind here unchanged: the record format, the moved rule, the full walk, the altitude filter, and `/ready`'s caller that never asks (`workflows-core:document-lineage` §6 step 6).

## Intent

`/docs-workflows:document` (keyed mode) and `/docs-workflows:release-notes` describe work that already shipped, or, for a release note drafted at the PM stage, the PRD's intent. Today neither reads a lineage record, so a chain that went stale above the work — a PRD revised after its specification and design were written, an Epic's specification behind its `epic.md` — is never named to the person documenting it.

The maintainer's framing: **a stale link is one more cause of "the PRD says something the code does not do"**, no different from a requirement that was overlooked at a later phase. It is reported with the other discrepancies, not treated as a reason to stop. `/document` already reports discrepancies claim by claim (its Phase 5.8, against the code diffs it always reads); `/release-notes` reports them when diff grounding is on. Lineage adds the *cause*, named once, before either run spends anything.

## Decisions (the maintainer's)

1. **Report, never ask.** Both commands run `upstream-check` as a caller that never asks (§6 step 6), as `/dev-workflows:ready` does: each stale link is a warning line naming the document to revise and its reviser, each missing record a note line, and nothing is asked, accepted or stored. Neither command stops on a lineage outcome.
2. **Neither command records.** No `upstreams:` and no `accepted:` is written anywhere — not on a docs page, not on `release-notes.md`. A docs page lives in the docs repository, outside the specs tree lineage covers, and carries no provenance by rule (`workflows-core:doc-structure-conventions` §1). A release note's `read:` lines already record what it described (`docs-workflows:release-note-types` §1), an upstream record on `release-notes.md` would read as stale after every PRD revision, and nothing downstream reads either output.
3. **`/release-notes` with diff grounding off is a separate gap, tracked, not fixed here.** With grounding off — it is opt-in — the note is written from the PRD alone and no claim is checked against the code, so once a specification or design exists, a requirement never built reaches the note unreported, whether it was overlooked or added later. That predates lineage. A new `docs/superpowers/to-fix.md` entry records it; this part only adds the stale-chain warning, which is the one signal such a run gets.

## Goals

- A stale link above the work either command describes is named before the run's first agent dispatch, and again in its Final report, with the document to revise and the command that revises it.
- `/release-notes` shows the warning before it asks whether to ground in the diffs, so the operator answers that question knowing the PRD may be ahead of the code.

## Non-goals

- No `require-on-main` gate for either command. Neither gates its inputs today, and this part adds none.
- No record of what a docs page was built from (docs-drift detection). That would be a new specs-tree artifact; out of D32.
- No change to Phase 5.8, `doc-planner`, `release-notes-writer` or `source-truth`: the warning is not handed to any agent.
- No change to `lineage.py` or the kind table: the script's `check` already serves a caller that never asks.

## Anti-goals

- A lineage outcome that stops, or asks, in either command.
- Any lineage text on a rendered docs page or in a release note's body.

## The builder's calls (mine; the builder may revisit with a ledgered ruling)

- **Which documents.** `/ready`'s per-unit rule (§6 step 6), over the scope each command already reads by (`workflows-core:implementation-format` §4): on an Epic-addressed run the focus Epic alone; otherwise each `EPIC-` folder directly under the PRD folder and the PRD folder itself — each unit's `specification.md` and `design.md` where present, with the same two as `--accepted-from`, and no `--output`. **Present** is `/ready`'s inventory test: in the working tree or on `<default-ref>`. Neither command has that inventory step, so the check step lists the units itself, from the placed folder, before Phase 3's own listing. A link accepted in its own unit is reported as *accepted in this unit* and is no warning. **Where no unit in scope holds either document** — a PM-stage `/release-notes` run, or a `/document` run on a PRD nothing was specified under — the one check takes `prd.md` alone, as both `docs` and `--accepted-from` (it is that unit's own document, so an acceptance its `/create-prd` run recorded is honoured, not re-warned on every run), so a PRD behind its idea or decision register is still named. Starting from the bottom of the chain is what reaches the case that matters here, a PRD revised after its specification: `prd.md` alone would miss it.
- **A document the check could not read is said, never counted as current.** The script reports a document missing from `<default-ref>` — checked or upstream — as `absent`, never as stale (§2 case 6), and §6 step 3 hides it because a gate owns it. Neither command has a gate, so for a caller with none, §6 step 6 shows each `absent` entry as a note line, `<doc>: not on <default-ref> — its chain was not checked`, and the report line never says `current` while one is listed: where every checked document was absent it reads `Lineage: not checked — <doc…> not on <default-ref>`. A run with no specs repository to read — an `@<path>` run with `$SPECS_PATH` unset, or one leading outside its work tree — runs no check and reports `Lineage: not checked — no specs repository`. This is a widening of §6 step 6 and §7 for a gateless caller; `/ready`, which gates first, is unaffected.
- **Where, in `/document`.** Mode A Phase 0, at the end of step 1 — after the placement stops and `branch-check`, before step 2 resolves the docs repository, since step 4(c)'s inline profiling can dispatch agents and the check must come before any dispatch — its result shown in the Readiness table, which gains a `Lineage` row. The caller is `/document`'s keyed mode: Mode B has no address, runs no check, and its report carries no `Lineage:` line; the callers list says "keyed mode".
- **Where, in `/release-notes`.** Phase 0, once the folder is placed and `focus_key` is known, shown before Phase 1 asks about diff grounding. Where a stale link was found and diff grounding is then declined, the Phase 2 plan says that claims drawn from the PRD are not checked against the code.
- **Report line.** Both Final reports carry §7's `Lineage: <n> stale link(s), <m> unrecorded — reported` (or `current`, or `not checked — <reason>`), with each line under it.
- **Script failure.** A non-zero exit is a warning line naming the script's first stderr line, never a stop, as for `/ready`.
- **The ref.** The check reads the default branch, as every caller does. A document present only on an unmerged branch is not in the walk; neither command says anything about that beyond what the script reports.

## Touched files (for the plan)

`workflows-core:document-lineage` — its callers list, §6 step 6, which today names `/ready` alone as the caller that never asks, and §7's report line, both widened for a caller with no gate; docs-workflows' `commands/document.md` and `commands/release-notes.md`, their `docs/commands/` pages, and `docs/reference/references.md` where it lists what each command cites; the rules maps (`.claude/rules/docs-workflows.md`'s `/document (keyed)` line, `.claude/rules/release-notes.md`'s line), each under 20,000 characters; `docs/superpowers/to-fix.md` (D32 follow-up 3 done; the new grounding-off entry). Releases: workflows-core and docs-workflows minor bumps, dated CHANGELOGs, `marketplace.json`, a coupling bullet. A claim sweep (refinements 3, 7, 8) for every sentence saying `/ready` is the only caller that never asks, that `/document` or `/release-notes` reads no lineage, and for the D32 entry's "Left: (3)".

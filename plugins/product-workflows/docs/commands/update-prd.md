# /update-prd

Refreshes an existing Product Requirements Document — routine updates and the rarer obstacle-driven re-do alike — gated by the same Opus review as [`/create-prd`](create-prd.md).

## Who runs it

`/update-prd` runs in the [pm](../roles-and-phases.md#pm--product-management) role, cost-attribution phase [prd-update](../roles-and-phases.md#prd-update) — distinct from `prd-creation` because this command refreshes an existing PRD rather than authoring one from scratch.

## Synopsis

```
/update-prd <KEY> [@transcript-or-notes ...] [--no-docs] [--docs <path>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

- **`<KEY>`** (mandatory) — the existing PRD's key. Format-validated only (`^[A-Z][A-Z0-9_]*(-\d+)+$`). The grammar fixes no depth, and that is what lets [`/create-prd`](create-prd.md) redirect here with a three-segment key — a PRD it authored inside a BRD slice on the BRD route. A two-segment key validates exactly as it always did.
- **`[@transcript-or-notes ...]`** (optional) — one or more paths to a transcript or notes file, read as secondary, read-only grounding for the grill.
- **`[--no-docs]`** — turns off documentation grounding for the run (see [What it needs](#what-it-needs)).
- **`[--docs <path>]`** — points documentation grounding at that root for this run instead of `${DOCS_PATH:-/workspace/docs}`. The flag and its value are stripped together before the address is parsed.

All three run flags apply to this command. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips Phase 7's session-cost entry, still advancing the checkpoint and dropping any deferred cost record a ceded `/prompt-brainstorm` or `/prompt-grill-me` run left pending in this session (`workflows-core:run-flags` §5 step 3) — see [Session cost](../reference/session-cost.md). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 7's maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance` — see [Session feedback](../reference/session-feedback.md). `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `workflows-core:docs-grounder`, `prose-style:prose-style-checker`, `prd-reviewer` (overriding its frontmatter Opus pin), `workflows-core:impl-maintenance`, and, under `--skip-feedback`, `defect-reporter` — to one model, and it is also the flag that changes a degrade path: Phase 1.5 otherwise records a degradation in `notes` when no Opus resolves anywhere in the environment — the grill and authoring still run on `current_model` regardless — which does not happen under enforcement, since every dispatched step then uses the enforced model instead — see [Model routing](../reference/model-routing.md).

## How it runs

```mermaid
flowchart TD
    p0["Phase 0 — Resolve inputs"] --> p1["Phase 1 — Configure"]
    p1 --> p15["Phase 1.5 — Classify + model routing"]
    p15 --> p2["Phase 2 — Read the base + grounding"]
    p2 --> p3["Phase 3 — Update via grill"]
    p3 --> p35["Phase 3.5 — Prose style check"]
    p35 --> p36["Phase 3.6 — Structural pre-lint"]
    p36 --> p4["Phase 4 — Review gate"]
    p4 --> p5["Phase 5 — Handoff (canonical + archive) + handoff"]
    p5 --> p6["Phase 6 — Next steps"]
    p6 --> p7["Phase 7 — Session maintenance, feedback & cost"]
```

Four subagents are dispatched — three of them unconditionally, `docs-grounder` only when documentation grounding resolves: `workflows-core:docs-grounder` (Phase 2, read-only grounding on the shipped product docs — default ON when `$DOCS_PATH` resolves, advisory, never a gate), `prose-style:prose-style-checker` (Phase 3.5, a non-gating quality pass, exactly as in [`/create-prd`](create-prd.md)), `prd-reviewer` (Phase 4, Opus-pinned), and `workflows-core:impl-maintenance` (Phase 7, session lessons-learned), each against the model recorded in `model_routing`. `prose-style` is a declared dependency of `product-workflows`, so Phase 3.5 has no absent case to skip.

Phase 6 offers re-runs only for downstream artifacts that already exist, recommending any whose assertions the update changed. With no surviving route, it skips the picker and continues through context guidance and Phase 7's bookkeeping. Otherwise the picker contains the surviving routes plus `Stop here`; when that exceeds four options, every route remains in prose and the prompt carries the three most relevant routes plus `Stop here`, with free-text access to the rest.

## What it needs

- **`<KEY>`** — mandatory; absent or malformed stops the run with `UPDATE_PRD_NEEDS_KEY`. It must resolve to a PRD-level folder: an Epic folder stops the run with `UPDATE_PRD_EPIC_FOLDER` before anything in it is read, since an Epic is never where a PRD lives. Where the folder above holds a `prd.md`, the stop names that PRD's key as the likely target, and [`/epics`](epics.md) for re-refining the Epic itself (on the Epic's key where its folder holds an `epic.md`, otherwise on the PRD's). Where the folder above is a `PRD-` folder holding no `prd.md`, it names [`/create-prd`](create-prd.md) on that folder's own key instead — on a BRD slice only where the slice's own coverage ledger clears the two data refusals, and otherwise naming what the ledger calls for, or nothing where the ledger is missing — and anywhere else it names no parent and says so.
- **`$SPECS_PATH`** (required) — if unset, the run stops naming `SPECS_PATH` and offers to enter a path or cancel.
- **The PRD**, at the resolved folder's `prd.md` — the only current copy there is (earlier revisions are archived under `revisions/` and never read as the base), and therefore the base without a freshness test. A `prd.md` that exists but cannot be read stops the run with `UPDATE_PRD_BASE_UNREADABLE` before anything is written. The base is read, and every refusal of the resolved folder taken, only after the specs-repo preflight has settled the specs checkout's branch, so a stale plugin branch cannot make a merged `prd.md` look absent or serve a stale one as the base. On a run carrying `specs_git: misrooted` (a misplaced `$SPECS_PATH`) the preflight switches no branch; it names a stale one it stays on, and that branch can still do either.
- **Secondary grounding** (all optional and read-only): a frozen specs-repo draft (**prd.md**), any **ard.md**, **specification.md**, `grounding/code-grounding.md` and `grounding/design-grounding.md`, and the `@transcript`/notes path(s) passed on the command line. None of these gate the run. Where a discovered **ard.md**, **specification.md**, or either grounding file is not on the specs repo's default branch, the Phase 1 confirmation flags it as unapproved — advisory only, never a reason to stop.
- **Grounding findings** (optional, either route) — where `grounding/code-grounding.md` and/or `grounding/design-grounding.md` are discovered, every `[CG#n]`/`[DG#n]` finding on file is read; a finding with no verifier outcome is not evidence and grounds nothing. Carried into the Phase 3 grill with the same **grill-rank** consumption the docs digest uses — the highest-value case is a `[CG#n]` whose verdict says an `[AC#n]` the PRD asks for is already satisfied at the pinned commit, which is scope this update can drop or narrow rather than a defect to raise. Where neither file was discovered, this step is a silent skip.
- **Documentation grounding** (optional, on by default) — turned off with `--no-docs`; a miss is a silent skip, never a gate.
- **No repos.** `/update-prd` is cwd-agnostic and product-level — it never mounts or scans code.

**`/update-prd` is deliberately excluded from `require-on-main`.** It never executes that consumer entry point at all, on any input, and it is not alone in that — [`/idea`](idea.md) and [`/brd-intake`](brd-intake.md) never execute it either, each opening a route and so waiting on no earlier phase — but it is the one authoring command that works from a PRD earlier phases wrote and still gates on none of them. Its authoritative base is the resolved folder (above), not a gated specs artifact, so subjecting the secondary grounding to `require-on-main` would block a legitimate refresh purely because an unrelated ARD happened to sit on an unmerged branch — the command reports that state instead of stopping on it.

## What it produces

- The **canonical** PRD, overwritten in place at the feature folder's **prd.md**, with `revision_of` (the archived snapshot's path, as actually written) and `built_from_date` (the date the update was built from) added to its frontmatter. Everything already there that records where the PRD came from is carried through unchanged — `sources`, `derived_from`, `seeded_from_prd`, and, on a PRD [`/create-prd`](create-prd.md) authored on the BRD route, `brd_key`, `brd_parent` and `depends_on`. Those three are preserved, never authored: this command reads no BRD tree for content — its only reads of a slice's `brd-link.md` and `coverage-ledger.md` word Phase 0's stops and carry nothing into the PRD — so it mints none of them and adds none to a PRD that arrived without them — and **no command of the build ladder reads any of the three** — neither [`/epics`](epics.md) nor `/dev-workflows:ready` does. `brd_key` and `brd_parent` are acted on by no command (`prd-reviewer` only checks that the pair is present together), and `depends_on`'s one reader is [`/brd-proposal`](brd-proposal.md), which takes slice order from it to compute peak concurrency — an estimate, gating nothing. They are preserved because provenance that survives an update is the precondition for any future consumer: this command reads no BRD tree for content, so dropping them at the first refresh would leave a slice's PRD indistinguishable from an ordinary one with nothing left to restore it from.
- An **archived snapshot** of the prior canonical PRD, copied immediately before the run's first write to **prd.md** — the grill edits that file live, so this is taken in Phase 3, once — to `<feature-folder>/revisions/<KEY>_<slug>_<YYYYMMDD>.md`, `<slug>` being the folder's own name less its `<KIND>-<KEY>-` prefix, or less `<KEY>-` on a legacy unprefixed folder, and the name being `<KEY>_<YYYYMMDD>.md` where nothing remains. Where that name is already taken by any file, the first free of that name with `-2`, `-3`, … inserted before `.md` is used, and `revision_of` records the name actually written. Where the copy fails, the run stops with `UPDATE_PRD_ARCHIVE_FAILED` before writing anything.
- Behind Phase 5's consent choice, both files are committed, pushed, and a pull request opened against the specs repo's default branch.
- *(The run used to end with a manual reminder to copy the updated body back into a tracker and refresh the export it read from. Neither step exists: the PRD is where every downstream command reads it.)*

**Where `grounding/code-grounding.md` and/or `grounding/design-grounding.md` were discovered, Phase 5 closes the consumption loop**: it sets `consumed_by: PRD` on each `[CG#n]`/`[DG#n]` finding this update actually drew on — never a finding read for context and unused, and never one with no verifier outcome — and stages both grounding files alongside the canonical PRD and its archived snapshot, since an uncommitted consumption record is one no later run can read. **This is the first time `PRD` is written onto a grounding finding record** — [`/create-ard`](create-ard.md) and [`/specify`](specify.md) already write `ARD` and `specification` at their own altitudes, and [`/create-prd`](create-prd.md) already writes `PRD`, but only onto a `decisions.md` decision record on the BRD route, never inside a grounding file, since it reads no `grounding/` file on either route.

## Gates

- **Phase 3.5 — Prose style check**, mirroring [`/create-prd`](create-prd.md) exactly: `prose-style:prose-style-checker` (unconditional — `prose-style` is a declared dependency of `product-workflows`) applies MAJOR fixes inline and re-runs once; a non-gating quality pass.
- **Phase 3.6 — Structural pre-lint** (`workflows-core:pre-lint`), advisory only — mechanical findings fixed inline, content gaps left for the grill.
- **Phase 4 — `prd-reviewer`**, Opus-pinned by frontmatter (`model: opus`, no override unless `--enforce-model`/`WORKFLOWS_ENFORCE_MODEL` enforces one), reviewing the whole updated PRD against `workflows-core:prd-format`. `PASS` / `PASS WITH RECOMMENDATIONS` proceeds. `BLOCK` triggers one inline fix cycle and one re-review; a persistent `BLOCK` is escalated per `workflows-core:escalation-rules`'s "Review verdict BLOCK … — commands that fix inline" choices, exactly as in [`/create-prd`](create-prd.md). If no Opus model resolves at all, the run degrades to the best available model and records the degradation — unless a model is enforced, in which case the enforced model is used instead and no degradation is recorded.

## Example

Refresh a PRD with new call notes, after the specs draft has already been reviewed once:

```
/product-workflows:update-prd PRODUCT-1234 @call-notes.md
```

The run resolves the feature folder, reads its `prd.md` as the base, grills the changes against it, and rewrites the canonical file while archiving the prior revision. **Requirement ids never move**: a requirement whose meaning changes gets a new id and the old one is marked `Superseded by` it, a dropped one is marked `Withdrawn` in place, and none is renumbered, reused or deleted, so every Epic, coverage row and grounding finding citing an id still points at the same requirement. `prd-reviewer` checks the update against the archived base.

## See also

- [Roles and phases](../roles-and-phases.md) — what the `pm` role owns and hands off at the `prd-update` seam.
- [`/create-prd`](create-prd.md) — the greenfield sibling that authors a PRD from scratch. `/create-prd` redirects **here** when it finds a PRD already authored; going the other way, a resolved folder holding no `prd.md` stops this run with `UPDATE_PRD_NO_PRD`, and that stop names `/create-prd` only where that command can itself run — it refuses three BRD-route shapes, not one (and an Epic folder, which this run has already refused), so on a BRD-route slice the stop resolves to [`/brd-split`](brd-split.md) against the slice or its parent, or to no command at all, where a data refusal would fire or the slice's coverage ledger is missing or unreadable.
- [`/create-ard`](create-ard.md), [`/specify`](specify.md), [`/epics`](epics.md), and the companion plugin's `/docs-workflows:release-notes` — the role re-runs `/update-prd`'s Phase 6 offers when an ARD, spec, or release note already exists.
- [Model routing](../reference/model-routing.md) — the classification and Opus fallback chain `prd-reviewer` runs under.
- [Session cost](../reference/session-cost.md), [Session feedback](../reference/session-feedback.md), and [Resume and checkpoints](../reference/resume-and-checkpoints.md) — the terminal Phase 7 bookkeeping every run emits.
- `workflows-core:prd-format` — the canonical structure the PRD is updated and reviewed against.
- [`/prd-ground`](prd-ground.md) — the optional, ungated run, on either route, whose `[CG#n]`/`[DG#n]` findings this command reads and marks `consumed_by: PRD`.
- `workflows-core:grounding-format` — the finding record, the six verdicts, and the `consumed_by` field this command is the first to write onto a grounding finding.

# /ready

Verifies whether the ARD, specification, and design artifacts on record actually justify a PRD or Epic's derived phase — read-only, and it never stops on an artifact it can't confirm.

## Who runs it

`/ready` runs in the [dev](../roles-and-phases.md#dev--build-verify-and-deliver) role, cost-attribution phase [readiness](../roles-and-phases.md#readiness) — being in this phase means the workflow phase is being derived from the ARD / spec / design record, never changed.

## Synopsis

```
/ready <ADDRESS> [--claimed "<status>"] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

**`--claimed "<status>"`** (optional) — a workflow phase you declare, typically pasted from whatever tracker you keep. The run compares it against the phase it derives from the artifacts and reports any divergence; a claim **above** the derived phase caps the verdict, a claim below is reported and does not.

**Without it, the run cannot catch a wrong claim** — a derived phase cannot contradict itself, so `/ready` reports what the artifacts show and nothing more. That is the cost of having no mirror to check against, and the flag is how anyone who does keep a tracker gets the check back, whichever tracker it is.

All three run flags apply to this command. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips Phase 8's session-cost entry, still advancing the checkpoint and dropping any deferred cost record a ceded `/prompt-brainstorm` or `/prompt-grill-me` run left pending in this session (`workflows-core:run-flags` §5 step 3) — see [Session cost](../reference/session-cost.md). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 6's maintenance step to bugs-only, dispatching `defect-reporter` in place of Agent 4 (`impl-maintenance`) — see [Session feedback](../reference/session-feedback.md). `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `readiness-reviewer` included, overriding its frontmatter Opus pin — to one model, bypassing the Sonnet-floor fallback described below — see [Model routing](../reference/model-routing.md).

`$ARGUMENTS` is a **single positional address** — a `<KEY>`, or an `@<path>` naming a folder in the specs tree. The resolved folder decides the altitude and the ladder it is judged on — by its prefix, never by the kind it asserts, since a BRD-route slice is a `PRD-` folder asserting `kind: brd`. A BRD container is tested first: a `BRD-` folder, or a legacy unprefixed one holding `coverage-ledger.md` or `brd/brd-inventory.md` and no `brd-link.md` naming a `parent:`, is on neither ladder and stops the run (`READY_BRD_NOT_SLICED`), naming each of its slices to check instead or, where it has none, `/product-workflows:brd-split` to carve one. Otherwise an `EPIC-` folder is an Epic-level run on the Epic ladder and a `PRD-` folder a PRD-level one on the PRD ladder; a legacy unprefixed folder — including one whose key happens to begin with a kind token, which is not a prefix — is placed by what it holds: a resolved `kind: epic` on the Epic ladder, a resolved `kind: prd` or a `brd-link.md` naming a `parent:` on the PRD ladder. The two-key form is retired, because the second key was always derivable from the first. The container stop and the placement are taken only after the specs-repo preflight has settled the specs checkout's branch, so a stale plugin branch cannot hide a slice from the listing or the file that places the folder. On a run carrying `specs_git: misrooted` (a misplaced `$SPECS_PATH`) the preflight switches no branch; it names a stale one it stays on, and that branch can still hide either.

**A PRD folder holding a flat `specification.md` is a broad PRD-level slice beside its Epics** — the unit `/design` designs and `/implement` implements as one, save on a multi-component PRD (see *Multi-component PRDs*) — and a PRD-level run judges it as one more row of its per-Epic inventory rather than by a check of its own: its phase is derived on the Epic ladder from the PRD folder's own `specification.md`, `design.md` and `implementation.md`, the PRD's readiness needs it at `Refined` or past it as it needs every in-scope Epic, and the report names it `broad slice`. A block an `/implement` run before 4.1.2 left in the PRD folder's `implementation.md` for an Epic it chose there counts toward the slice until you move it into that Epic's own `implementation.md` — `workflows-core:implementation-format` §1 says how.

## How it runs

`/ready` has 11 `## Phase` headings. The diagram below collapses the deterministic, orchestrator-inline phases and shows the one real decision the run makes after it already has a verdict in hand: whether to commit and hand off the readiness snapshot.

```mermaid
flowchart TD
    p0["Phase 0 — Resolve input"] --> p1["Phase 1 — Clarify + artifact inventory"]
    p1 --> p15["Phase 1.5 — Classify"]
    p15 --> p2["Phase 2 — Read ground truth"]
    p2 --> p25["Phase 2.5 — Resolve ARD"]
    p25 --> p3["Phase 3 — Deterministic skeleton"]
    p3 --> p4["Phase 4 — Readiness review"]
    p4 --> p5["Phase 5 — Write report"]
    p5 --> d1{"Hand off _readiness.md? (§4.3 consent choice)"}
    d1 -->|"Branch + commit + push + PR"| p678["Phase 6 — Post-run maintenance & feedback / Phase 7 — Emit follow-up tasks / Phase 8 — Session cost"]
    d1 -->|"Write only — no commit"| p678
```

Two named subagents are dispatched: `readiness-reviewer` (Phase 4, the sole judgment-heavy delegate — Opus, frontmatter-pinned, dispatched regardless of classification (unless `--enforce-model` overrides it)), and `workflows-core:impl-maintenance` (Phase 6, session lessons-learned). Phase 6 also dispatches three general-purpose agents beside `impl-maintenance` — a documentation review, a knowledge-base review and an instructions review — on the same Sonnet chain. `/ready` has **no delegated writer or implementation subagent** — Phase 3's coverage map, status-expectation checklist, and repo-availability check are built mechanically, orchestrator-inline, from Phase 2's folder read and Phase 1's artifact inventory. `impl-maintenance` and the three general-purpose agents run at `detection_model` — the Sonnet chain; `readiness-reviewer` keeps its frontmatter Opus pin regardless of classification (unless `--enforce-model` overrides it), falling to the Sonnet floor (recorded as a degradation) only when no Opus is available at all. Classification is typically `MODERATE` — bounded scope, a single PRD or Epic, read-only, no code changes — escalating to `SIGNIFICANT` only for an unusually large multi-Epic PRD whose coverage chain spans many Epics and repos.

### Multi-component PRDs

On a PRD with two or more components, *Ready for Implementation* expects the ARD with `## Contracts`, the PRD-level specification, and a specification and design for every in-scope Epic — and no PRD-level design, because there the PRD-level specification is designed and implemented through its Epics. The report adds a `Contract coverage` section: each Epic's target, and every interface a consumer uses that no Epic produces, one produced by an Epic that does not target its producer, and a consumer that does not depend on its producer.

## What it needs

- **A PRD or Epic address** — with none, or with a token that fails the key grammar, the run stops (`READY_NEEDS_KEY`); `/ready` has no direct-prompt behaviour. An address resolving to a `BRD-` container stops too (`READY_BRD_NOT_SLICED`).
- **`$SPECS_PATH`** — must resolve; `/ready` reads the ARD/spec/design artifacts from there and writes `_readiness.md` back into the same feature folder. If unset, the run stops and asks for a path.
- **A clean specs-repo checkout on `main`/`master`** — `/ready` reads artifacts from a clean default branch, never a branch of its own; a dirty or non-main checkout triggers a warn-and-ask rather than a silent read, because it may show unmerged, in-flight artifacts as if they were the handed-off truth.
- **The gated ARD/spec/design themselves — `/ready` is the one command whose gated inputs never stop it.** Every other consumer of `require-on-main` (`workflows-core:phase-handoff` §3) and `workflows-core:ard-resolution` stops when a gated artifact resolves off the specs repo's default branch — save `/product-workflows:brd-reconcile` at two sites and never at its ordinary Phase 0 gate: its cross-BRD write guard, and a `--sent` run's redundancy check at Phase 0 step 6, which reads the gate inverted (`phase-handoff` §3.7). `/design`'s `specification.md` is the extreme case of that rule — this plugin's one gated input that genuinely stops on absence, not merely on being unmerged; the companion `product-workflows` commands whose gated input was never optional stop on absence too (`phase-handoff` §3.4). `/ready` is the mirror opposite for every artifact it checks: an artifact authored only on a branch, or on `main` but unconfirmed, or unverifiable against any ref, becomes a readiness finding that caps the verdict at `PARTIAL`; an artifact that is absent outright is recorded as a coverage gap. Reporting readiness is `/ready`'s whole function, so a run that stops instead of reporting has failed at the one thing it exists to do.
- **An optional ARD** (Phase 2.5, via `workflows-core:ard-resolution`) — `status: none` skips the ARD-conformance dimension entirely; `status: found` carries its `[AD#N]` invariants into the review; `status: unmerged` carries the same invariants forward **and never stops** — the one exemption `workflows-core:ard-resolution`'s no-regression rule names — adding an "ARD authored, not handed off" finding instead.
- **Mounted repos under `$REPOS_PATH`, best-effort presence only.** Phase 3(c) derives candidate repo names from the `repo:` entries of each in-scope Epic's `implementation.md`, and of the broad slice's, any `design.md`'s confirmed-repos header, and any ARD's `grounded_repos:` frontmatter, then checks which are mounted. This is informative context for the reviewer, never a hard gate — unlike `/design`'s Phase 3, `/ready` never dispatches `workflows-core:code-scanner` and never scans code.

## What it produces

A `SUPPORTED` / `PARTIAL` / `NOT-SUPPORTED` verdict with a requirement coverage roll-up (N/M requirements covered, each `❌` gap named — or `not assessed — PRD states no requirements`, where the verdict is `NOT-SUPPORTED` because nothing was verified rather than because something failed) and the full `readiness-reviewer` Findings section, by dimension. `/ready` **authors nothing** in the PRD/Epic/ARD/spec/design sense — its only authored write is `_readiness.md`, overwritten on every run at the PRD dir (PRD-level check) or the Epic subdir (Epic-level check).

`_readiness.md` is committed and handed off only behind the `workflows-core:phase-handoff` §4.3 consent choice — the **advisory** variant, whose second option says no command stops on this rather than promising a downstream stop, because nothing gates `_readiness.md` and `/implement` only reads it for a one-line advisory — creating `ready/<KEY>-<slug>`, never automatically. Declining leaves it uncommitted; the terminal `commit-artifacts` step stages only `$SPECS_PATH`'s bounded session-artifact paths and never `_readiness.md` itself.Phase 7 additionally emits one follow-up per named readiness gap on a `PARTIAL`/`NOT-SUPPORTED` verdict, plus a standing reminder to reconcile any status you keep elsewhere with the artifacts; a clean `SUPPORTED` run qualifies no follow-ups at all.

## Gates

Phase 4 dispatches `readiness-reviewer` — Opus (unless `--enforce-model` overrides it), frontmatter-pinned, mandatory on every run regardless of classification — with the Phase 3 mechanical skeleton (coverage map, status-expectation checklist, repo availability), the Phase 3(0) derived phase with the artifacts that placed it there, any `--claimed` value, and the Phase 2.5 `applicable_ard` when one resolved. No verdict is written or reported without it. `readiness-reviewer` is the plugin's **only reviewer that does joint cross-artifact analysis** — the reviewers that gate the artifacts it reads (`prd-reviewer`, `ard-reviewer`, `epic-reviewer`, `spec-reviewer`, `design-reviewer`), and this plugin's `code-review`, are each scoped to judging one artifact's own quality; several also read a companion artifact for traceability or non-contradiction (`design-reviewer` reads the source `specification.md`, `ard-reviewer` reads an inherited PRD-level ARD, `spec-reviewer` reads `applicable_ard`, `epic-reviewer` reads sibling Epics), but none of them synthesizes a verdict across artifacts the way `readiness-reviewer` does.

Because `/ready` authors nothing, there is no fixer to dispatch and no `BLOCK`/re-review cycle — the gate's outcome *is* the verdict and its Findings section, not a pass/fail loop feeding a fix. A `⚠` artifact state (authored on a branch, unconfirmed on main, or unverifiable against any ref) is recorded as a `MAJOR`-or-worse finding for the reviewer's "Status consistency" dimension, but it never stops the run — it only caps how high the verdict can land.

## Example

Check whether an Epic is really ready to move into `Refined`:

```
/dev-workflows:ready EPIC-98760
```

The run resolves `EPIC-98760` with `resolve-address`; its folder's `EPIC-` prefix is what sets the altitude and the Epic ladder, so no second key is passed and none is accepted. It reads that Epic and the parent PRD's artifacts from the resolved tree, resolves any applicable ARD, locates the Epic's `specification.md`/`design.md` and checks each against the specs repo's default branch (never stopping on what it finds), builds the coverage map and status-expectation checklist, and dispatches `readiness-reviewer`. It prints the verdict with its coverage roll-up and Findings, writes `_readiness.md` into the Epic subdir, and offers to commit and hand it off — declining leaves the snapshot written but uncommitted.

## See also

- [Roles and phases](../roles-and-phases.md) — what the `dev` role owns, including the handover-model exception `/ready` gets: the one caller whose own gate never stops it, where every other command's own gate is fatal (save `/brd-reconcile`'s cross-BRD write guard and its `--sent` redundancy check — `workflows-core:phase-handoff` §3.7), and why verification is not a lane of its own.
- [`/design`](design.md) — the opposite extreme on the same gate: `/design` stops outright when its `specification.md` is absent, the only gated input in this plugin that does (`workflows-core:phase-handoff` §3.4 lists the companion `product-workflows` commands that do too), while `/ready` reads that same class of artifacts and never stops on any of them.
- `/product-workflows:create-ard` and `/product-workflows:specify` — the upstream commands, shipped in the companion `product-workflows` plugin, whose ARD and `specification.md` `/ready` verifies (via `design.md`, whose upstream is `/design`, in the same chain).
- [Model routing](../reference/model-routing.md) — the classification rules and the `readiness-reviewer` Opus pin, including its Sonnet-floor fallback.
- [Session cost](../reference/session-cost.md), [Session feedback](../reference/session-feedback.md), and [Follow-ups](../reference/follow-ups.md) — the terminal Phase 6–8 bookkeeping every run emits.
- `workflows-core:phase-handoff` and `workflows-core:ard-resolution` — the gates `/ready` reads but is the one caller that never stops on.
- [`workflow-states.md`](../../references/workflow-states.md) — the PRD and Epic status ladders, expected-artifacts columns, and readiness targets `readiness-reviewer` applies.

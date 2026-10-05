---
paths:
  - "plugins/product-workflows/**"
  - "plugins/dev-workflows/commands/design.md"
  - "plugins/dev-workflows/commands/ready.md"
  - "plugins/dev-workflows/commands/implement.md"
  - "plugins/docs-workflows/commands/release-notes.md"
  - "plugins/workflows-core/references/addressing.md"
  - "plugins/workflows-core/references/grilling-technique.md"
  - "plugins/workflows-core/references/prd-format.md"
---

# product-workflows — invariants, workflow map, agent callers

Loaded when a file under `plugins/product-workflows/` is read, or `/design`'s, `/ready`'s, `/implement`'s or `/release-notes`' command file, or `workflows-core:addressing`, `workflows-core:grilling-technique` or `workflows-core:prd-format` — the files outside the plugin that the PRD-creation invariants below bind. Repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

The BRD route's map lines and its slice-kind, PRD-eligibility, sibling re-cut and route-detection invariants are in `.claude/rules/brd-route.md`, split out to keep each rules file under 20,000 characters.

## Plugin facts

The six-command BRD-to-PRD route (`/brd-intake` → `/brd-split` → `/prd-ground` → `/brd-split` → `/brd-interview` → `/brd-package` → `/brd-reconcile`, the second `/brd-split` running once per slice the first carved) grounds a customer's requirements document, settles it with them, and seeds the PRD, ARD and specification.

The two effort-proposal commands `/prd-proposal` and `/brd-proposal` price a graded requirement set in human hours — never money — and **gate nothing downstream: no command of the build ladder reads a proposal, the one command that reads *another folder's* as a proposal being the sibling umbrella `/brd-proposal`, whose gate stays inside the pair — every other targeted read is an own-folder one: a later run of the producing command opening its own folder's as a re-estimate anchor, and `proposal-reviewer` inside the run that wrote it; `/brd-reconcile`'s stale cross-reference sweep reads any proposal under the parent as ordinary prose and never edits one**.

**`brd-` names the route, not the folder kind, and `/prd-ground` is the only one of the six that leaves the route** — it also runs, optionally and ungated, on an idea-route PRD folder with no BRD anywhere in its ancestry, grounding that PRD's own `[AC#n]`/`[FR#n]` rows the same way it grounds a slice's `[BR#n]` rows on the BRD route. Four of the six route commands refuse a root outright (`/prd-ground`, `/brd-interview`, `/brd-package` and `/brd-reconcile`, each with its own `*_ROOT_LEVEL` stop), so "runs on a slice" is the wrong test for which one renames: `/brd-intake` and `/brd-split` are route commands that genuinely run at root, while interviewing, packaging and reconciling exist only because a customer handed over a BRD and will never run anywhere else — `/prd-ground` alone left the route, which is why it alone carries the `prd-` name.

`/epics`, `/create-prd`, and `/update-prd` all run `prose-style-checker` unconditionally as a non-gating quality pass, with no branch left for `prose-style` being absent.

## Docs tree

`product-workflows` carries 28 pages — the four top-level pages `docs/README.md` (the index), `getting-started.md`, `workflow.md` and `roles-and-phases.md`, plus `brd-workflow.md`, 14 command pages under `docs/commands/` and 9 reference pages under `docs/reference/`.

## Workflow map

The `product-workflows` commands' lines of the family workflow map outside the BRD route, and the caller lines of the agents `plugins/product-workflows/agents/` ships that the route does not own. The route's lines are in `.claude/rules/brd-route.md`.

```
/epics               → [resolve-docs-grounding — a deliberate exception to §5 rule 2's ordering] → [require-on-main: PRD-level specification.md] → [multi-component-prereqs: Contracts + PRD-level spec, where the ARD's code components are ≥2] → read the resolved folder → [docs-grounder] → [code-scanner×N (parallel, optional)] → [no ARD set: confirm components, asked only where ≥2 are proposed; then the same prereqs] → writing (one target per Epic) → [prose-style-checker] → [doc-fixer] → [epic-reviewer@Opus] → [triage: verify each finding] → [doc-fixer] → impl-maintenance → commit-artifacts
/idea                → [walk every link read-only (product-workflows:linked-sources); past two levels / 12 pages / 6 images, the operator decides] → [figure-reader@Opus ×N (parallel, ≤10 per dispatch, cap 4)] → idea-reader → [docs-grounder (when $DOCS_PATH valid)] → [code-scanner×N (--ground-code, cap 4, broad-then-narrow)] → (embedded grilling) → write idea.md in its final folder (no relocation, D7) → vendor the sources read (markdown → `attachments/`, images → `design/idea-sources/` + its index) and repoint idea.md's links onto the copies → [handoff-to-main: idea.md + every vendored path] → impl-maintenance → commit-artifacts
/create-prd           → [require-on-main: idea.md; on the BRD route, the slice's decisions.md] → [docs-grounder] → (embedded grilling; a prior prd.md in the folder is archived to revisions/ before the first write) → [prd-reviewer@Opus] → write PRD → [on the BRD route, triage each gap the grill could not close by whose authority settles it; a customer-authority one becomes a new [AS#n] in decisions.md, roundless, which /brd-package already carries to the customer] → [handoff-to-main: PRD, plus decisions.md on the BRD route] → impl-maintenance → commit-artifacts
/update-prd           → [resolve-address on the specs tree] → [docs-grounder] → (embedded grilling, diffs against base; archive the base to revisions/ before the first write) → [prd-reviewer@Opus] → write canonical → [handoff-to-main: PRD] → impl-maintenance → commit-artifacts
/create-ard          → [require-on-main: PRD; on the BRD route, the slice's decisions.md] → [read the PRD folder's prd.md — the folder above the Epic, on an Epic-level run] → [wherever the PRD folder — the folder above the Epic, on an Epic-level run — holds grounding/, seed Phase 3's themes from its [CG#n]/[DG#n] findings before falling back to PRD/Epic themes] → [ls $REPOS_PATH → enumerate-components → confirm components → code-scanner×N (confirmed set, parallel, cap 4)] → [docs-grounder + architecture-grounder@Opus (when $ARCHITECTURE_REPO_PATH resolves)] → (embedded grilling) → [ard-reviewer@Opus] → write ARD → [wherever that PRD folder holds grounding/, stamp consumed_by: ARD on findings drawn on] → [handoff-to-main: ARD] → impl-maintenance → commit-artifacts
/specify             → [require-on-main: PRD; on the BRD route, the slice's decisions.md] → read the resolved folder → [wherever the PRD folder — the folder above the Epic, on an Epic-level run — holds grounding/, seed the theme extraction from its [CG#n]/[DG#n] findings before falling back to PRD-derived themes] → [code-scanner×N (parallel, cap 4, soft gate)] → [docs-grounder] → (embedded grilling) → [spec-reviewer@Opus] → write specification.md → [wherever that PRD folder holds grounding/, stamp consumed_by: specification on findings drawn on] → [handoff-to-main: specification.md] → impl-maintenance → commit-artifacts
/prd-proposal        → [require-on-main: prd.md] → [resolve or grill the proposal profile] → grade the readiness tier (1–4) → derive work packages by delivery seam (+ a defect-remediation package from three sources, never a scope lever) → derive [ED#n] drivers, each citing a verified grounding finding, a frozen decision or a confirmed defect → hours by [WP#n] and role, ranged bottom-up from per-package confidence under the tier's ceiling → write proposal.md + proposal-brief.md (tier ≥ 2) → [pre-lint, minus its auto-link collision check] → [proposal-reviewer@Opus] → [triage: verify each finding] → [handoff-to-main: both artifacts + the archived prior] → impl-maintenance → commit-artifacts   (gates nothing downstream: no command of the build ladder reads a proposal, the one command reading *another folder's* as a proposal being the sibling umbrella /brd-proposal, whose gate stays inside the pair; a later run of this command reads its own folder's as a re-estimate anchor)
/brd-proposal        → [resolve a BRD- container; a PRD- or EPIC- folder is refused] → enumerate slices by the positive brd-link.md parent test → the readiness walk (stop / exclude-and-disclose / re-run, recommendation computed, decision the operator's; a slice whose proposal is current is included without a question) → [require-on-main: each included slice's proposal.md] → roll up, naming all three adjustments (umbrella effort, de-duplication on shared finding ids, peak concurrency rather than summed FTE) → coverage computed from the root ledger, remainder enumerated by identifier → write proposal.md + proposal-brief.md (tier ≥ 2, the tier being the minimum of the included slices') → [pre-lint, minus its auto-link collision check] → [proposal-reviewer@Opus] → [triage] → [handoff-to-main] → impl-maintenance → commit-artifacts   (the umbrella is the end of this branch, not a phase in the build ladder)
                      └── epic-reviewer (product-workflows)          (used by /epics)
                      └── epic-writer (product-workflows)            (used by /epics)
                      └── prd-reviewer (product-workflows)           (used by /create-prd, /update-prd)
                      └── ard-reviewer (product-workflows)           (used by /create-ard)
                      └── spec-reviewer (product-workflows)          (used by /specify)
                      └── idea-reader (product-workflows)            (used by /idea)
                      └── figure-reader (product-workflows)          (used by /brd-intake, /idea)
                      └── proposal-reviewer (product-workflows)      (used by /prd-proposal, /brd-proposal)
```

## Invariants

### Key invariants for the PRD-creation flow (`/idea`, `/create-prd`, `/create-ard`, `/specify`)

The flow also runs through `/design` and `/ready`; their own bullets are in `.claude/rules/dev-workflows.md` § Invariants. The ARD-respect rule and the rule that a phase is not finished until its artifact is on the specs repo's default branch are in `CLAUDE.md`.

- Each authoring command is gated by its own Opus reviewer (`prd-reviewer`, `ard-reviewer`, `spec-reviewer`, `design-reviewer`; `/ready` by `readiness-reviewer`); `/idea` has no reviewer — its bounded grill is the gate
- Only `/idea`'s embedded grill is **bounded** (≤10 questions; `--deep` switches it to relentless), with leftover gaps becoming capped `[NEEDS CLARIFICATION]` markers + logged assumptions; `/create-prd`, `/create-ard`, `/specify`, and `/design` (and `/update-prd`) grill **relentlessly** to convergence with no cap (`workflows-core:grilling-technique`)
- PRD / ARD / `specification.md` / `design.md` are written under `$SPECS_PATH/specifications/<KIND>-<KEY>-<slug>/` (kind `BRD`/`PRD`/`EPIC`, per `addressing.md` §2 — the unprefixed form is the deprecated legacy layout); `/idea` writes `idea.md` into that same folder on its first write, which is why it takes a mandatory key
- `/create-ard` grounds on mounted repos it discovers (`$REPOS_PATH` listing + theme→component proposal, `workflows-core:components` §2 + confirm/mount-or-descope); it never reads PRs. At PRD level it writes the confirmed list to `components:` and, with two or more `kind: code` components, authors `## Contracts`
- **On a multi-component PRD** (`workflows-core:components` §3) every Epic has one `target:`, the PRD-level ARD carries `## Contracts`, and the PRD-level spec is a requirements source designed and implemented through its Epics (taking it whole is an override `/design` and `/implement` offer). `/epics` and `/implement` stop with a recommended way forward where the contract or a prerequisite artifact is missing, offering to continue without it; `/ready` caps its verdict instead. A single-component PRD meets none of this beyond `/epics` Phase 5.5's question where two components are proposed, the `target:` on its Epics, and what a target drives — its design's `Target` line, `/specify`'s and `/design`'s narrowing to it, `/design`'s re-split question and `design-reviewer`'s *Target & contract*, `/implement`'s target-repository question, `/ready`'s target repositories, `epic-reviewer`'s *Single target*, a focus run's split, and `/epics` Phase 9's `### Targets`
- An `AD#N` is never rewritten in place on a refine — downstream artifacts cite it by ID — so a changed decision is a new `AD#N` and the old one carries `**Superseded by:**` (one made moot with no replacement, `**Withdrawn:**`); `workflows-core:ard-resolution` leaves either out of `invariants`, and every live decision records its `**Alternatives:**` (`plugins/product-workflows/references/ard-format.md` § Superseding a decision)
- `/idea` Phase 5 hands `idea.md` off via `handoff-to-main` (`workflows-core:phase-handoff` §2) behind the §4.3 consent choice. **There is no relocation**: the key is a mandatory argument precisely so the brief lands in its final folder on the first write, and `/create-prd <KEY>` finds it there
- `/create-prd <KEY>` derives `idea.md` in-contract from the resolved feature folder and gates it via `require-on-main` (`workflows-core:phase-handoff` §3); an explicit `@<path>` argument is out-of-contract — read where it sits, never relocated, never gated
- `/create-prd` DOES write `release_versions` / `change_type` / `release_notes_category` — whichever the operator volunteers, **never asking for any of them** — **a reversal** (`workflows-core:prd-format`). They were tracker dropdowns returned by an import; nothing returns them now, so each is authored where it is known. `/release-notes` reads `change_type` and `release_notes_category` from `prd.md` and takes the release from `--version` or its grill, never from `release_versions`, which no command acts on. `prd-reviewer` does not require them, since each may legitimately be unknown at authoring time
- `/idea` takes one source — an inline prompt or an `@<path>` markdown file — and types nothing from a tracker export; prior art is not discovered by anything
- `/idea` Phase 4 has no write-path gate and no `prd_disposition`: the operator named the folder on the command line, so there is nothing left to derive or to branch on

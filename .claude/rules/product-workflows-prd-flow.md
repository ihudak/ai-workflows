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

# product-workflows — the PRD-creation flow's invariants

Loaded with `.claude/rules/product-workflows.md`, whose `paths:` it shares. Split out of `.claude/rules/product-workflows.md` to keep that file under 20,000 characters; its plugin facts, workflow map and agent callers are there; repo-wide rules are in `CLAUDE.md`; evidence is in `docs/maintainers/rationale.md`.

## Invariants

### Key invariants for the PRD-creation flow (`/idea`, `/create-prd`, `/create-ard`, `/specify`)

The flow also runs through `/design` and `/ready`; their own bullets are in `.claude/rules/dev-workflows.md` § Invariants. The ARD-respect rule and the rule that a phase is not finished until its artifact is on the specs repo's default branch are in `CLAUDE.md`.

- Each authoring command is gated by its own Opus reviewer (`prd-reviewer`, `ard-reviewer`, `spec-reviewer`, `design-reviewer`; `/ready` by `readiness-reviewer`); `/idea` has no reviewer — its bounded grill is the gate
- Only `/idea`'s embedded grill is **bounded** (≤10 questions; `--deep` switches it to relentless), with leftover gaps becoming capped `[NEEDS CLARIFICATION]` markers + logged assumptions; `/create-prd`, `/create-ard`, `/specify`, and `/design` (and `/update-prd` and `/update-spec`) grill **relentlessly** to convergence with no cap (`workflows-core:grilling-technique`)
- PRD / ARD / `specification.md` / `design.md` are written under `$SPECS_PATH/specifications/<KIND>-<KEY>-<slug>/` (kind `BRD`/`PRD`/`EPIC`, per `addressing.md` §2 — the unprefixed form is the deprecated legacy layout); `/idea` writes `idea.md` into that same folder on its first write, which is why it takes a mandatory key
- `/create-ard` grounds on mounted repos it discovers (`$REPOS_PATH` listing + theme→component proposal, `workflows-core:components` §2 + confirm/mount-or-descope); it never reads PRs. At PRD level it writes the confirmed list to `components:` and, with two or more `kind: code` components, authors `## Contracts`
- **On a multi-component PRD** (`workflows-core:components` §3) every Epic has one `target:`, the PRD-level ARD carries `## Contracts`, and the PRD-level spec is a requirements source designed and implemented through its Epics (taking it whole is an override `/design` and `/implement` offer). `/epics` and `/implement` stop with a recommended way forward where the contract or a prerequisite artifact is missing, offering to continue without it; `/ready` caps its verdict instead. A single-component PRD meets none of this beyond `/epics` Phase 5.5's question where two components are proposed, the `target:` on its Epics, and what a target drives — its design's `Target` line, `/specify`'s and `/design`'s narrowing to it, `/design`'s re-split question and `design-reviewer`'s *Target & contract*, `/implement`'s target-repository question, `/ready`'s target repositories, `epic-reviewer`'s *Single target*, a focus run's split, and `/epics` Phase 9's `### Targets`
- An `AD#N` is never rewritten in place on a refine — downstream artifacts cite it by ID — so a changed decision is a new `AD#N` and the old one carries `**Superseded by:**` (one made moot with no replacement, `**Withdrawn:**`); `workflows-core:ard-resolution` leaves either out of `invariants`, and every live decision records its `**Alternatives:**` (`plugins/product-workflows/references/ard-format.md` § Superseding a decision)
- `/idea` Phase 5 hands `idea.md` off via `handoff-to-main` (`workflows-core:phase-handoff` §2) behind the §4.3 consent choice. **There is no relocation**: the key is a mandatory argument precisely so the brief lands in its final folder on the first write, and `/create-prd <KEY>` finds it there
- `/create-prd <KEY>` derives `idea.md` in-contract from the resolved feature folder and gates it via `require-on-main` (`workflows-core:phase-handoff` §3); an explicit `@<path>` idea argument is out-of-contract — read where it sits, never relocated, never gated; an `@` token naming an existing directory under `$SPECS_PATH/specifications/` is instead the address, resolved through `resolve-address`'s `@<path>` branch — the form every key-first `product-workflows` command takes in place of its key, as the way through the shared `ambiguous` stop
- `/create-prd` DOES write `release_versions` / `change_type` / `release_notes_category` — whichever the operator volunteers, **never asking for any of them** — **a reversal** (`workflows-core:prd-format`). They were tracker dropdowns returned by an import; nothing returns them now, so each is authored where it is known. `/release-notes` reads `change_type` and `release_notes_category` from `prd.md` and takes the release from `--version` or its Phase 1 question, never from `release_versions`, which no command acts on. `prd-reviewer` does not require them, since each may legitimately be unknown at authoring time
- `/idea` takes one source — an inline prompt or an `@<path>` markdown file — and types nothing from a tracker export; prior art is not discovered by anything
- `/idea` Phase 4 has no write-path gate and no `prd_disposition`: the operator named the folder on the command line, so there is nothing left to derive or to branch on

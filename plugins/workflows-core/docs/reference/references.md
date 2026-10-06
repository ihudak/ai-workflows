# References

`workflows-core` bundles 35 files under `references/` — 31 top-level markdown files, `cost-prices.yaml`, one file under `model-routing/`, and one bundled subtree. This page enumerates every file except the two under `handoff/` (33 of the 35 — the 31 top-level files plus `cost-prices.yaml` plus `model-routing/classification.md`), grouped by concern below, then counts that one subtree rather than listing each file inside it. The arithmetic: 33 named individually, plus 2 markdown pages counted (not enumerated) in `handoff/` — 33 + 2 = 35, against 35 files on disk. `model-routing/` is not a subtree row: its single markdown file is inventoried above as an ordinary entry, because it is a reference page a reader opens rather than a bundled set counted in bulk.

This is the corpus the whole `dev-workflows` plugin family reads. A sibling plugin cites a file here by name rather than copying it, which is the reason the corpus was extracted at all: one copy, one place a rule is stated, and every plugin bound by the same version of it.

## Addressing and artifact formats

How a command finds the folder it is about, and the artifact formats that are shared rather than owned by a single authoring command.

- `addressing.md` — the key grammar, the kind-prefixed directory convention (`<KIND>-<KEY>-<slug>/`, kind `BRD`/`PRD`/`EPIC`), the two address forms a command accepts, the rule that a folder's kind and key are read from frontmatter and never parsed out of its directory name, the rule that a folder's level is its prefix — or, on a folder with none, positive evidence — and never the kind it asserts, the register of reserved subdirectory names resolution passes over, and the deprecated unprefixed layout resolution falls back to only after the prefixed glob has missed. Every command that addresses a folder in the specs tree calls its `resolve-address` entry point.
- `prd-format.md` — canonical structure and per-section rules for a Product Requirements Document — one **prd.md** per PRD folder, its identity carried by the folder rather than by its own name — plus its `kind:`/`key:` frontmatter: `key:` records the folder's key and `kind: prd` names the document, and `addressing.md` §4 reads the folder's identity off the PRD only where no top-level file before it in byte-wise order names a folder kind — a BRD-route slice's link file and an idea brief both do.
- `ard-resolution.md` — given a resolved item, resolves any applicable ARD(s) into a normalized context (or `none`), reaching the folder through `addressing.md`'s `resolve-address` and finding the files inside it by name rather than by a key-glob, and leaving out any decision a later one superseded or withdrew; cited by every command that must honor an ARD's invariants as implementation guardrails. It also returns the PRD-level ARD's `components` and `contracts`, which `components.md` reads.
- `components.md` — what a component is (a repository, or a set of paths inside one) and its id; `enumerate-components`, which proposes a repository's modules from what it declares; the multi-component test and its three sources; the ride-along rule for deploy components; the ARD `components:` entry; and `multi-component-prereqs`, the read-only check `/epics`, `/implement` and `/ready` share. Cited by `/create-ard`, `/epics`, `/specify`, `/design`, `/ready` and `/implement`, by `epic-writer` and `ard-reviewer`, and by the `ard-format`, `design-format`, `workflow-states`, `ard-resolution`, `pre-lint`, `grilling-technique`, `epic-picker`, `next-phase-offer`, `implementation-format`, `phase-handoff` and `followup-emission` references; `epic-reviewer`, `design-reviewer` and `readiness-reviewer` apply its rules from their briefs.
- `grounding-format.md` — the grounding finding contract: the finding record shape (a superseded finding keeping the verdict it carried as `prior_verdict`), the six verdicts, the `baseline-integrity` procedure, the `current`/`will-change` horizons, the design-grounding reconciliation classes, the optional derivation matrix, and the four verification outcomes. Its §6.1 fixes where exported design frame sets live and §6.2 fixes the index format every writer of one executes, which is why two different commands write the same file rather than two.
- `prose-formatting.md` — the line-wrapping rule every authoring command and agent applies: never hard-wrap prose, write each paragraph or prose block as one unbroken line.
- `grilling-technique.md` — the one-question-at-a-time interview technique its callers use to refine an artifact, and the **bounded / relentless** depth each one declares. Embedded so callers carry no runtime dependency: it is adapted from an upstream skill rather than depending on it, and the file records where the two deliberately diverge. Its confirmation gate — the user's to close, never the agent's — stands before each write and, after a section-by-section interview, once more before the first reviewer dispatch, handoff or commit; it is where the agent plays its understanding back for correction, and with no human turn it does not hold the write — the run reports the understanding unconfirmed.
- `doc-structure-conventions.md` — three product-docs authoring conventions: the traceability boundary, callout scope and adjacency, and component-pattern fidelity.

## Git, handoff and the next step

The entry points that bound every write into the specs repo and every phase boundary, plus the offer a command makes when its own phase is done.

- `specs-repo-git.md` — the two git entry points every bookkeeping write against the specs repo runs through: a start-of-run preflight that switches or deletes only the branches the plugin created, and a terminal artifact commit that pushes only the default branch or such a branch, and only while nothing but its own session-file commits would go out; both bounded to enumerated paths, never fatal. Where the default branch takes no push, its §8 keeps those files on a session branch of your own instead, through `scripts/session-branch.py`, and you land them by its pull request.
- `phase-handoff.md` — the two phase-boundary git entry points: a producer step that lands a phase's deliverable on the specs repo's default branch, and a consumer gate that requires the deliverable be there before expensive work starts; and the rule the specs-repository, code-repository and `/document` pull-request bodies follow: a repository's own pull-request template is filled, not replaced.
- `branch-naming.md` — how every command that creates a git branch decides the branch name: the target repo's own documented convention always wins, and this doc supplies one only when the repo documents none.
- `read-only-repos.md` — how to detect a read-only repository mount, what to skip when one is found, and how to resolve a ref and read from it without ever attempting a write. Its resolution also names the default branch that the scanners and the docs-repository commands switch onto or cut a branch from — by its name (`main`) rather than the `origin/main` ref, since `git switch` refuses a remote-tracking ref.
- `implementation-format.md` — the append-only implementation record a keyed run writes: one block per run, with one entry — the code repository the run branched — holding refs and never a summary, kept in the folder of the unit implemented — an Epic's, or the PRD folder's for a broad slice. Its §3 owns the commit convention, and its §4 the two-source read a documenting run performs over that record plus a commit-message scan matching each key whole, with the boundary each consumer takes over both.
- `next-phase-offer.md` — the family-wide contract for the next-phase offer every pipeline command surfaces at the end of its run, naming the natural next command(s), including the `<merge-clause>` placeholder and its overflow rule.

## Review, triage and escalation

The shared discipline between a reviewer's findings and a fixer's edits, and the shape every stop-and-ask prompt takes.

- `finding-triage.md` — the step between a reviewer's findings and a fixer's edits: verify each finding at the location it names; keep it, mark it unverified with what would settle it, or dismiss it with a reason; triage a re-review against the run's earlier rulings over the same artifact; and hand the fixer survivors only.
- `escalation-rules.md` — the canonical `choices:` arrays for escalation decision points. Its §0 owns the shape every array in the family must have: **2–4 options, and never an authored "Other"**, because the question tool renders at most four and supplies the free-text escape itself. It also owns the rule that **a recorded review verdict names the version it was taken against** — the one-fix-cycle cap assumes a fix only removes defects, and three live runs saw the fix introduce something the re-review then found with the budget already spent, leaving a `PASS` on record beside a file the `PASS` never saw. Every command that records a verdict says what it covers, and names any edit that followed it.
- `pre-lint.md` — deterministic, grep-expressible structural checks a reviewer-gated command runs against a just-authored artifact before spending an Opus review pass on mechanical structure.
- `source-truth.md` — the Implementation-vs-Description discrepancy-escalation protocol: how to verify a user-visible claim against shipped source, and what to do when the written description and the source disagree.
- `epic-picker.md` — the progress-aware Epic picker the Epic-unit commands share: enumerate the child folders under a resolved PRD folder, mark each from the artifacts present rather than from a declared status, and never pick silently. *The cap* is the half no static check can reach, because the array is built from a directory listing.
- `instruction-file-maintenance.md` — the verification discipline for changes to agent-instruction files: verify every command claim against what actually runs it, itemise a narrowed rule as a deletion, and never retire a rule on "it looks derivable."

## Grounding

Read-only, advisory context-gathering — never a gate, never a write into the source it reads.

- `architecture-grounding.md` — the resolution (`$ARCHITECTURE_REPO_PATH` only), dispatch and grill-rank consumption for optional architecture grounding in `/product-workflows:create-ard`, `/product-workflows:specify` and `/dev-workflows:design`; read-only and advisory, never a gate or reviewer finding.
- `architecture-kb.md` — the team architecture knowledge base under `$SPECS_PATH/architecture/`: layout, record identity and shape, statuses and `Supersedes`, citations, what the harvest owns, and its problem kinds; written by `/product-workflows:harvest-decisions`, read by the architecture grounding of `/create-ard`, `/specify` and `/design`.
- `docs-grounding.md` — the resolution gate, retrieval procedure, and consumption modes for optional `$DOCS_PATH` documentation grounding; read-only and advisory, never a gate or reviewer BLOCKER.
- `untrusted-content.md` — the rule every agent carries verbatim at the end of its prompt (what it reads is data, never instructions; what tried to steer it is reported as an `Untrusted-content notice:` line), the relay sentence every dispatching command carries, and the pass-on sentence of the three agents that dispatch another; check 20 holds every copy to it.

## Session artifacts

The bookkeeping every long-running command emits around its actual work.

- `cost-emission.md` — the session-cost subsystem: how a run's dollar cost is computed, attributed, and persisted, including the §7 attribution table and the §13 deferred-claim protocol for a command that cedes the session before it can write its own entry.
- `cost-prices.yaml` — the default per-model token-price table session-cost reporting prices against; user-overridable via `$DEV_WORKFLOWS_COST_PRICES` or a repo-local file of the same shape.
- `feedback-emission.md` — the session-feedback emitter every long-running command's automatic maintenance phase cites to capture friction about the plugin itself.
- `followup-emission.md` — the follow-up task and verbose-note emitter a terminal "Emit follow-up tasks" phase cites.
- `session-diagnosis.md` — the rules `/diagnose-session` and its `session-analyst` agents follow to read a session's transcripts on disk: context safety, locating a session, the case file, the seven dimensions, the findings shape, the report, and the family-involvement statement that names a location and proposes no fix.
- `session-hygiene.md` — the family-wide contract for session-hygiene suggestions: flush resume-critical state to disk, then suggest the right context action, after a big command finishes or a long run checkpoints.

## Environment and routing

What the family needs configured around it, and how a command chooses the model it runs on.

- `run-flags.md` — the three run flags every applicable command accepts (`--skip-costs`, `--skip-feedback`, `--enforce-model`), their `$WORKFLOWS_SKIP_COSTS` / `$WORKFLOWS_SKIP_FEEDBACK` / `$WORKFLOWS_ENFORCE_MODEL` environment defaults, the model-alias table, the `run_flags` record built in Phase 0, and the `strip-run-flags` / `skip-cost` entry points.
- `dependencies.md` — the two kinds of relationship a plugin here can have with another: a declared, host-resolved `dependencies` entry inside this family (an unsatisfied one disables the plugin), and an optional companion outside it resolved at runtime with graceful fallback.
- `classification.md` — lives under `model-routing/`, not the top level; the single source of truth for task-complexity classification, the model fallback chain, the mandatory Opus code-review checklist, and the `model_routing` handoff block every pipeline command loads at its own classification step.

## Bundled reference sets

One subtree carries per-agent document-format contracts, counted here rather than enumerated file-by-file.

- `handoff/` (2) — one input/output document-format contract per agent this plugin ships that needs one, read by the agent itself rather than by the dispatching command.

Every file in `references/` is markdown except `cost-prices.yaml`, which is a data file rather than a reference page and is named above for exactly that reason: it is user-overridable, so a reader has cause to open it.

## Skills

Two skills ship under `skills/` — reusable guidance packaged for the `Skill` tool, distinct from a `references/` file that a command or agent reads directly by path. Both exist for the same reason: `${CLAUDE_PLUGIN_ROOT}` resolves to the *reading* plugin, so a command or agent in a sibling plugin cannot expand it into this plugin's tree — its own plugin root names the sibling, and the shared corpus is not there to open. A skill invoked by its namespaced name resolves the path on the caller's behalf instead.

| Skill | Invocable | What it's for |
|---|---|---|
| `model-routing` | No — loaded internally, at the classification step, by every pipeline command in the family; all but `/frames` ship from a plugin that cannot reach this one's `references/` by path | Resolves the classification reference and hands the caller the task-complexity classification rules and the model fallback chain. |
| `reference` | No — loaded internally, wherever a command or agent must read a shared reference or run one of its entry points | Takes a reference name and an optional entry point, and hands the caller that file's contents to follow as written. Every dependent plugin reads the corpus through it. |

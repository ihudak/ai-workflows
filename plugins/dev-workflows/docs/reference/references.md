# References reference

`dev-workflows` bundles 15 files under `references/` — 5 top-level markdown files and three bundled subtrees. This page enumerates the 5 top-level files, grouped by concern below, then counts the three subtrees rather than listing each file inside them — every file in them is cited by name too, by the command or agent that reads it. The arithmetic: 5 named individually, plus 5 + 3 + 2 = 10 markdown pages counted (not enumerated) across the three subtrees — 5 + 10 = 15, which is every file on disk. Nothing here is non-markdown any more: the defaults file and the owners list that used to sit inside `docs-profiles/` left with that subtree, so `*.md` counts and `find <dir> -type f` counts now agree everywhere on this page.

The shared corpus every plugin in this family reads — the addressing grammar, the git and phase-handoff entry points, model routing, escalation and triage, cost/feedback/follow-up emission, the grounding and grilling conventions, and the PRD format — ships in the companion `workflows-core` plugin and is enumerated on its own references page. The PRD-ladder authoring formats — the BRD, decision-register, coverage-ledger, customer-review, idea, ARD, and specification formats — ship in the companion `product-workflows` plugin, alongside the commands that author against them. The documentation corpus — the gate ledger, the repo-verification-gate extractor, the toolchain preflight, the docs-repo finish-and-handoff mechanics, the release-note type map, the `docs-profiles/` authoring conventions, and the `docs-workflow/` portal-scaffold set (the tree and its stubs, the public/internal visibility model, the docs-repo resolution ladder, and the brand-contrast thresholds) — ships in the companion `docs-workflows` plugin, alongside the commands that read it. What is listed here is what `dev-workflows` itself carries.

## Authoring formats

The canonical structure each artifact type is authored and reviewed against, plus the shared conventions every authoring command applies while writing one.

- `design-format.md` — canonical structure and per-section rules for an engineering design — **design.md** — plus its `kind:`/`key:` frontmatter; `/design` authors against it, `design-reviewer` reviews against it, `interface-designer` reads its `## Seams` categories, and `/ready` reads its repos header. The PRD-ladder formats one altitude up — the PRD, ARD, specification, and idea brief this design's own specification descends from — ship in the companion `product-workflows` plugin now.

## Review and triage

The gates a written artifact passes through before it counts as done. The triage discipline itself, and the escalation and pre-lint conventions the gates share, are `workflows-core`'s; the verification-gate ledger and the repo-checklist extractor are `docs-workflows`'s.

- `workflow-states.md` — maps each workflow phase on the PRD and Epic ladders to its owning role, the command that drives the transition into it, and the artifacts expected to exist at that status; the rubric `readiness-reviewer` applies.
- `bug-diagnosis.md` — the bug-diagnosis discipline `/implement` follows for a bug-shaped task: a deterministic repro before hypothesizing, ranked falsifiable hypotheses, tagged and cleaned-up instrumentation, a regression test at a correct seam.

## Session artifacts

The bookkeeping every long-running command emits around its actual work. The emitters themselves — cost, feedback, follow-ups, hygiene — are `workflows-core`'s; what stays here is the code repository's own git finish and the context strategy an over-long implementation run applies.

- `code-handoff.md` — the `finish-code-branch` entry point: what a command does with the code it just changed, executed against the **code** repository rather than `$SPECS_PATH`. The commit is prompt-free and only the push and the pull request sit behind a consent choice, because an uncommitted tree is recoverable by nobody while a commit on a branch is recoverable by anyone. Owns the gate (including the check that HEAD is on the branch the caller named — `git commit` writes to HEAD while `git push -u origin <branch>` pushes the ref *named*, so a mismatch reports a push that never happened), the staging carve-outs for a dirty tree and a pushed stash, the commit written through a message **file** rather than `-m` (an inline message command-substitutes `$(…)` and backticks out of free text such as an NVD description), the base-branch ladder whose lower rungs are existence probes rather than name sources, the `gh` capability probe with its existing-pull-request check and no-CLI fallback, the split-call form for a per-unit loop, and the `Code repo:` outcome line. A run whose gates failed is still committed and still offered for push — only its pull request degrades, to a draft carrying a DO-NOT-MERGE banner. It is also the one git reference that stages at repository scope, and §1 says why that divergence from its two siblings is deliberate. The pull request's body holds a Summary, the before and the after the run observed as Evidence, a Merge danger call — a one-way or two-way door, and its blast radius — and the Review; where the repository carries one pull-request template at a path the reference lists, the body is that template, filled. Consumed by `/implement`, `/upgrade`, and `/vuln`.
- `context-management.md` — strategies for an implementation run whose step list is too long to complete in one context window without degrading.

## Bundled reference sets

Three subtrees carry bundled guidance too large or too domain-specific to enumerate file-by-file; each is counted here instead.

- `handoff/` (5) — one input/output document-format contract per agent, read by the agent itself, and two ways besides: `handoff/test-baseliner.md` by `vuln-fixer` and `upgrade-executor`, which dispatch it, and `handoff/vuln-fixer.md` and `handoff/upgrade-executor.md` by `/vuln` and `/upgrade`, which read those agents' returns against them.
- `upgrade/` (3) — component-specific upgrade guidance, consulted by `upgrade-planner` and `upgrade-executor`, and by `/upgrade` itself, whose Phase 1 inventory reads `upgrade/ecosystems.md`.
- `fix-vuln/` (2) — CVE-remediation guidance, consulted by `vuln-research` and `vuln-fixer`.

All three subtrees are markdown only, so each figure above is both its `*.md` count and its `find <dir> -type f` count. The one subtree that held non-markdown data — `docs-profiles/`, with its defaults file and owners list — moved to `docs-workflows` with the commands that read it, and its entry is on that plugin's own references page.

# References reference

`docs-workflows` bundles 24 files under `references/` — six top-level markdown files and four bundled subtrees. This page enumerates the six top-level files, the four in `docs-workflow/` and the three in `docs-audit/`, which are enumerated as well as counted because each is a distinct entry point a command names — grouped by concern below — then counts the other two subtrees rather than listing each file inside them, although commands and agents cite files in both of those by name too. The arithmetic: six named individually, plus 5 + 4 + 4 + 3 = 16 markdown pages across the four subtrees — 6 + 16 = 22 accounted for, against 24 files on disk. The remaining two are non-markdown data or templates inside the `docs-profiles/` subtree, deliberately not listed as reference pages: a defaults file and an owners list, neither of them prose a reader would open. The subtree figures below are markdown-page counts specifically; the two data files already sit inside that same subtree and are not part of that count, so nobody should later "correct" a subtree figure by adding them back in.

The shared corpus every plugin in this family reads — the addressing grammar, the git and phase-handoff entry points, model routing, escalation and triage, cost/feedback/follow-up emission, the docs-grounding and doc-structure conventions, and the PRD format — ships in the companion `workflows-core` plugin and is enumerated on its own references page, reached through the loader skill rather than by path. What is listed here is what `docs-workflows` itself carries.

## Verification gates

The accounting a documentation run keeps about what it actually verified, and the two extractors that decide what there was to verify.

- `gate-ledger.md` — the six verification-gate outcomes (`RAN` / `DEGRADED` / `FAILED` / `UNAVAILABLE` / `SKIPPED_BY_USER` / `NOT_APPLICABLE`), the rule that no outcome is orchestrator-assignable to mean "I decided not to run this", the per-mode gate registry, the `UNAVAILABLE` conversion prompt, and the reviewer contract; consumed by `/document` and by the agents whose gates it registers, and cited by `/docs-init`, which borrows its distinction between an unrun gate and a passed one for its own verification.
- `repo-verification-gates.md` — how to extract a docs repo's own pre-PR checklist into the `repo_verification_gates` block a reviewer can check the written files against, augmenting the plugin's own gates rather than overriding them.
- `toolchain-preflight.md` — the environment check `/document` runs at Phase 0, deriving the required tool set from the resolved profile, the repo's config signals and the repo's own documented prerequisites; the tool→gate map; and the prompt that fires only when a required tool is missing. `/docs-init` runs the same check at its Phase 2 but derives nothing — there is no profile yet — and hands it a fixed set of its own. The file says which test each tool takes, by asking the shell — and the directory — that will run it: a tool the plugin runs through `bash -c` or as `command <name>` — `bash`, `curl`, `lsof`, `ps`, `vale` and every dev server's tool — is asked of that same child shell, which runs no alias of yours and no shell function of yours that you have not exported, while a build or lint command's tool, which runs in the Bash tool's own shell, is asked of that shell, where your aliases and functions apply exactly as they will when the command runs. Either test runs from the directory the command runs from, so a tool a profile records as a path — `node_modules/.bin/vitepress` — resolves as it will at run time, and an alias pointing somewhere that is not there passes, to fail at the gate like any other environmental failure. `/docs-serve` runs no preflight, but tests its own tools with the first of those tests — not a bare `command -v` in your shell, which an alias or a shell function named after the tool passes; `/document`'s render check uses it too — and takes the file's definition of a command's tool, with that test, before it starts a server, and its set-aside of a leading `cd <dir> &&` and `VAR=value` words when it matches a recorded command to a process's command line. The file also defines, once, the five names Vale reads its configuration from and how the plugin runs Vale over one — a lint and `vale sync` alike, on the repository's configuration with no global Vale configuration and no `VALE_CONFIG_PATH`, as a clean CI runner has neither, and with the limit it states for a configuration that sets no `StylesPath`, which keeps the machine's shared default styles directory — which `docs-style-checker`, `docs-scaffold-reviewer` and `/docs-init` cite.

## Git and handoff

The one handoff mechanic that belongs to a single command rather than to the family, executed against a **docs** repository.

- `finish-and-handoff.md` — the mechanics `/document` (keyed mode) uses for its inline-profiling-branch handling and its finish-and-handoff step: squash, opt-in push, copy-paste PR draft. The specs repo's own git entry points, and the code repo's, are elsewhere — `workflows-core:specs-repo-git` and `workflows-core:phase-handoff` for the first, the pipeline plugin's `dev-workflows:code-handoff` for the second.

## Finding the work

How the two documentation commands find the code a feature changed, beyond the implementation record.

- `key-discovery.md` — how `/document` (keyed mode) and `/release-notes` run the whole-key commit scan, its probe and the optional GitHub pull-request search through `scripts/key-discovery.py`, and how a merged pull request's landed commits join the scan's result while every other pull request found is listed, never read.

## Authoring formats

- `release-note-types.md` — the release-note section map (`## Breaking changes` / `## Feature updates` / `## Fixes`, all three in one **release-notes.md** under a release-version heading, each draft under a scope comment naming the PRD or Epic it was drafted for and every commit its run read, which is what bounds a later run rather than any date), the per-section draft shape and prose rules, the deprecation-note rule, and Change Type sourcing; consulted by `release-notes-writer`, cited by `/release-notes` for its own invariants, and named by `docs-workflow/scaffold-tree.md` and by two `workflows-core` references, `prd-format` and `implementation-format`.

## The documentation-portal scaffold

`docs-workflow/` (4) — the bulky, stable content the portal-scaffolding commands write, held here so the command bodies stay orchestration. Each file is enumerated rather than merely counted, because each is a named entry point a command cites when it says which part it is executing.

- `docs-workflow/scaffold-tree.md` — what a scaffolded documentation portal contains: the directory tree and why each section is standard, the per-directory stubs with their frontmatter and their "what does not belong here" half, the `nav:` generation rule, the two MkDocs configs, and the Vale config with its vocabulary-seeding rule.
- `docs-workflow/visibility.md` — the two-build public/internal model, the two traps that make the obvious checks useless (the dev server is not the build; snippets cross the boundary invisibly), the two output-level CI gates and the conditional third, the marker convention both halves of gate 2 depend on, and the CI workflow the scaffold writes.
- `docs-workflow/repo-resolution.md` — the shared docs-repo resolution ladder, in its two opposite forms (`/document` resolves its repository by a ladder of its own, whose differences from this one the file records): `resolve-docs-repo` for a command that needs a docs repository that already exists, and `resolve-scaffold-target` for the one command that needs a place to make one, plus the shared signal set both test against.
- `docs-workflow/contrast.md` — the WCAG 2.2 contrast thresholds a derived brand palette is held to, the relative-luminance formula with a worked example, and what a failing colour does (reported with its measured ratio, applied only on the operator's confirmation).

## The documentation audit

`docs-audit/` (3) — the vocabulary a documentation audit is written in and the two contracts that vocabulary produces, held here so that one file defines each name and no command or agent re-derives it. Enumerated rather than merely counted, for the same reason as `docs-workflow/` above: each file is a named entry point a command cites when it says which part it is executing.

- `docs-audit/coverage-model.md` — what a documentation **surface** is and where each of the seven kinds is derived from — a part of a code repository for five, the specs tree for `decision` and `release` — the page-**type** vocabulary and the `(surface, audience, type)` coverage grid it is the second axis of, why tutorials are the one quadrant a human picks rather than the audit generating it, the four prioritisation signals and the guard that stops volatility excluding a surface instead of merely ranking it, the five paths a backlog **unit** enters by with the consequence of the hand-written one, and the definition of done.
- `docs-audit/backlog-format.md` — `.dev-workflows/docs-backlog.yml` in full: the schema with its `sources[]`, `surfaces[]`, `units[]`, `tutorial_candidates[]`, `coverage` and `threshold` blocks, why surfaces and units are two tables rather than one, the unit status lifecycle with the three transitions a command writes today — the mint to `missing`, and a refresh's `missing` → `drafted` and `missing` → `published` — and the one edge that deliberately does not exist, what `blocked_by` carries, what a `coverage` fraction counts, the file's one home at the docs repo's git top level, and the invariant tying `visibility` to `page_path`.
- `docs-audit/evidence-contract.md` — what a documentation claim may rest on: the one interface with its user and engineering implementations, the three evidence kinds (`code`, `walkthrough`, `artifact`) and what each records, the rule that a marked claim never becomes prose fact by default, the walkthrough file with its closed action vocabulary, and how a walkthrough is executed as a checklist today and by a driver later without the format changing.

## Bundled reference sets

Two further subtrees carry bundled guidance too large or too domain-specific to enumerate file-by-file; each is counted here instead.

- `docs-profiles/` (5) — docs-profile authoring conventions for the built-in `example-docs` worked example (frontmatter, changelog, anchors, render verification, the docs-profile schema). Who consults it is derived rather than listed here: `grep -rl docs-profiles plugins/docs-workflows/commands plugins/docs-workflows/agents plugins/docs-workflows/skills plugins/docs-workflows/hooks`, run from the repository root, returns every command, agent, skill and hook that reads a file in it, and that recipe is the authority on the set. A list kept here went stale as commands and agents gained citations, which is why none is kept.
- `handoff/` (4) — one input/output document-format contract per agent, read by the agent itself — and, for `docs-auditor` and `ia-planner`, also by `/docs-audit`, which builds each dispatch's brief from the file: one each for `diff-summarizer`, `release-notes-writer`, `docs-auditor` and `ia-planner`. The last two are a matched pair — `ia-planner`'s input block is `docs-auditor`'s output block, verbatim — so a field added to one is added to the other in the same edit, and the volatility window and its buckets are written once, in `docs-auditor`'s, for both of them to read.

One of these subtrees (`docs-profiles/`) also holds the data and template files named in the introduction above, so its `*.md` count here is smaller than `find <dir> -type f` would report; `handoff/`, `docs-workflow/` and `docs-audit/` are markdown only, and for them the two counts agree.

## Skills

One skill ships under `skills/` — reusable guidance packaged for the `Skill` tool, distinct from a `references/` file that a command or agent reads directly by path. The `model-routing` skill every pipeline command invokes at its classification step, and the `reference` loader that reaches the shared corpus, both ship in `workflows-core`.

| Skill | Invocable | What it's for |
|---|---|---|
| `docs-frontmatter` | Yes | Applies documentation frontmatter conventions — changelog entries, page owners, core metadata fields — when editing a page under any content root the applicable docs profile declares. |

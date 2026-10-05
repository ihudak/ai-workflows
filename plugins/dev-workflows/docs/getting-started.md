# Getting started

This page takes you from zero to your first successful run — install the plugin, set the environment variables it reads, install the status line, and run `/design` end to end. Once you have done this once, [Workflow overview](workflow.md) shows the whole pipeline and [Roles and phases](roles-and-phases.md) says what your role owns at each step.

## Install

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. Install plugins

```bash
claude plugin install dev-workflows@shipwright
```

`dev-workflows` declares one hard dependency, installed automatically alongside it: `workflows-core`, its shared foundation — the addressing grammar, the git and phase-handoff entry points, model routing, escalation and triage, and the emitters. The companion `product-workflows` plugin is not a dependency in either direction: `/design` consumes the `specification.md` it produces, but `dev-workflows` installs and runs without it, against a specification someone else's product work already landed on the specs repo's default branch. The companion `docs-workflows` plugin is likewise independent: `/implement` hands off to its `/docs-workflows:document` and `/docs-workflows:release-notes`, but neither is required for this plugin's own five commands to run.

**What you also need, and it is not a plugin.** Nothing beyond `gh`, when present, for opening the pull requests it drafts — the pipeline otherwise reads and writes one markdown tree plus the mounted code repositories. It is not network-free, and the capability is not confined to two commands: every one of the five declares `WebFetch` in its own `allowed-tools`, and three of the plugin's agents carry a web grant — `vuln-research` for the NVD lookup, `upgrade-planner` for package-registry queries, and `risk-planner`, dispatched by `/implement` as well as `/upgrade`, which holds the family's only `WebSearch`. `grep -ln 'WebFetch\|WebSearch' plugins/dev-workflows/agents/*.md` re-derives that set rather than trusting this list. If you keep your work in a tracker as well, syncing the two is yours to arrange; no command here learns whether one exists.

**One more that is not in this marketplace.** [`superpowers`](https://github.com/obra/superpowers) is a separate Claude Code plugin, recommended rather than required: the companion `workflows-core` plugin's `/prompt-brainstorm` cedes its Phase 3 to `superpowers:brainstorming`, and the brainstorm → plan → subagent-driven-development flow this plugin's own development uses comes from it. Without it that one hand-off has nowhere to go; everything else degrades gracefully. Note that *grilling* is **not** an external dependency — the relentless-interrogation technique `/design`'s own embedded interview runs is bundled here, in `workflows-core:grilling-technique`.

**What you do not need for this plugin.** The marketplace also ships `obsidian-llm-wiki` (compiling a vault into a cross-referenced wiki), `acli` (an Atlassian CLI reference skill) <!-- vendor-token-ok: names the subject of a sibling plugin this one does not use -->, `prose-style` (the prose linter the companion `product-workflows` and `docs-workflows` plugins depend on), and `guideline-reviewers` (the API- and UI-guideline review commands, moved out of this plugin). None of the four is used by `dev-workflows` today: none of its five remaining commands dispatches a prose-style checker or a guideline reviewer, and `acli` is referenced nowhere in it. Install them if you want them for their own sake; see the [marketplace README](../../../README.md).

## Update

```bash
claude plugin marketplace update shipwright
claude plugin update dev-workflows@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update dev-workflows@shipwright` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same thing with a picker. This page used to say the first line alone was enough; it is not, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one.

## What you set on your machine

`dev-workflows` reads four environment variables. One is required for the pipeline to have anywhere to write (`SPECS_PATH`); the rest are optional and each degrades to a documented default or a silent skip.

### `SPECS_PATH`

The **shared, team-visible repository for the AI-authored documents** — the Product Requirements Document, the ARD, `specification.md`, and `design.md`, each under a kind-prefixed folder — `specifications/PRD-<KEY>-<slug>/`, with `EPIC-` folders below it. This is the reason a second store exists at all: it is the medium through which one role hands work to the next. A producing command lands its artifact on the specs repo's default branch, and the next command in the chain refuses to start expensive work until it finds that artifact there — not merely written to disk, and not merely committed to a branch of its own. See [Roles and phases](roles-and-phases.md) for what each seam hands over and what happens when an artifact is missing or stuck on an unmerged branch. Set it to the root of a dedicated specs repository, the directory that holds `specifications/`, never to `specifications/` itself: a run that resolves an address against the latter stops and names the value to set instead ([Environment](reference/environment.md)).

### `REPOS_PATH`

Where your code clones live — one directory, or a colon-separated list of them. It has a sensible built-in default, so most readers never need to set it at all; see [Environment](reference/environment.md) for the exact value and resolution order. `/design` builds a slug→clone map from the top-level directories under `$REPOS_PATH` and matches each confirmed repo on its `git remote get-url origin` slug, **never on its directory name**, so a clone renamed on disk is still found as long as its `origin` remote is intact; `/implement`, `/upgrade`, and `/vuln` work directly in the code repository they are run against.

### `DOCS_PATH`

Your shipped product documentation's clone — **read-only** in its role as a grounding root. None of this plugin's own five commands grounds against it. Nine commands do, and every one of them ships from a companion plugin: eight from `product-workflows` (`/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, `/brd-intake` and `/prd-ground`) and `/docs-workflows:release-notes` from `docs-workflows`. Separately, `/docs-workflows:document` prefers this variable as a docs-repo discovery **hint** — a write target, not grounding. It is documented here only because [`code-handoff.md`](reference/references.md)'s git finish states plainly that it never touches this path either — a boundary statement, not a consumer. The plugin never writes to `DOCS_PATH`.

### `GIT_USER_INITIALS`

Your branch identifier. Branch naming is **repo-rule-first**: every branch-creating command reads the target repo's own documented convention and follows it as written. Where that convention has a name-or-initials segment, `GIT_USER_INITIALS` fills it; where it does not, the convention is followed without it, and this variable is simply unused for that repo.

## Install the status line

**Worth doing before your first real run.** The command that installs it ships in the companion `workflows-core` plugin rather than this one, which is why every form below is qualified. Two things come out of it.

The visible half is a permanent multi-line status line at the bottom of your terminal — session identity, git state, context usage, running cost, tokens, and rate limits — so you can see a long command spending your budget while it spends it, rather than finding out in the final report.

The half you don't see is the **cost cross-check**. Session-cost reporting works without the status line: it reads the session transcript and prices it against the bundled table. What the status line adds is a second, independent figure — Claude Code's own reported cost, captured per render — which the cost phase differences into a per-invocation delta. Where the two disagree, the gap is the signal that the bundled price table has drifted and needs refreshing. Install it and you get both numbers; skip it and you still get a cost report, just without anything to calibrate it against. (Even with it installed, the first cost phase of a session has no baseline yet and omits the second figure; it appears from the second command onward.)

See [Session cost](reference/session-cost.md) for what the report contains and where it lands. The command is idempotent, backs up anything it would overwrite, and changes no workflow-command behaviour.

```
/workflows-core:statusline
```

Claude Code ships its own built-in `/statusline` command, so typing the bare form reaches that instead of the companion plugin's — always use the qualified `/workflows-core:statusline`.

## Where to run it

Run the plugin in an AI container — strongly recommended: a command run there can reach only what you mount into it and the network you allow.

The plugin runs commands a repository declares, with your permissions: its test command, its build, the linter it configures, and — in `/upgrade` and `/vuln` — the install of the dependency versions it moves to — though for npm, yarn, pnpm, pip and pipenv without their install scripts or source builds: the run names what it skipped, and runs it only for the packages you name with `--allow-install-scripts`. Bundler, Poetry, uv, PDM, Hatch, Composer, NuGet, Go, Cargo, Maven and Gradle install as before. Its agents treat what they read in a repository — its `CLAUDE.md` included — as data that never adds a task or changes a verdict, and report text that tries to steer them, but a declared command is a value that rule lets through on purpose: running a repository's tests is the task. On your own host, point the plugin only at repositories you would build yourself.

## Your first run

`/design` is where this plugin's spine picks up, once the companion `product-workflows` plugin's `/product-workflows:specify` has landed a `specification.md` on the specs repo's default branch. It takes the same address that named the specification.

```
/design EPIC-98760
```

`EPIC-98760` resolves the Epic within its PRD, the same key `/product-workflows:specify` used to land `specification.md`. Nothing looks it up beyond the specs tree, and no tracker is read.

Here is what to expect:

1. **A gate.** `/design` refuses to start if `specification.md` is not found on the specs repo's default branch — this plugin's one hard exception to the "absent input falls back" rule (the companion `product-workflows` commands whose gated input was never optional stop too, as `workflows-core:phase-handoff` §3.4 lists).
2. **Grounding and a grill.** It resolves any applicable ARD, derives and confirms the implementation repos under `$REPOS_PATH`, hard-stops if none is mounted, scans the confirmed set, then grills you through challenging the spec and designing the implementation.
3. **A written design.** It writes `design.md` into the same specs feature folder, then offers to commit, push, and open a pull request against the specs repo's default branch. Once that lands, `/implement EPIC-98760` picks up the design and starts the code change.

From here, [Workflow overview](workflow.md) shows where every other command sits relative to `/design`, and [Roles and phases](roles-and-phases.md) says what happens at each handoff along the way — including where `product-workflows`'s own PRD → architecture → Epic breakdown → specification ladder hands off into this one.

# ai-workflows

Ivan Gudak's open-source Claude Code plugin marketplace, **Shipwright**: plugins that take work from an idea or a business requirements document to shipped, documented software. It is installed as the `shipwright` marketplace.

**Moving from `ihudak-plugins`?** This repository used to be `ihudak/ihudak-claude-plugins`, with the marketplace named `ihudak-plugins`. See [Moving from the old marketplace name](#moving-from-the-old-marketplace-name).

## Plugins

| Plugin | Description |
|--------|-------------|
| [dev-workflows](plugins/dev-workflows/) | Five slash commands for design → implementation → readiness, upgrade, and vuln fixing, with Opus-backed planning and review gates. Needs `workflows-core`. [Docs](plugins/dev-workflows/docs/README.md) |
| [product-workflows](plugins/product-workflows/) | Fourteen slash commands: idea → PRD → ARD → specification, a six-command BRD-to-PRD route, effort proposals. Needs `workflows-core` and `prose-style`. [Docs](plugins/product-workflows/docs/README.md) |
| [guideline-reviewers](plugins/guideline-reviewers/) | Two standalone commands: `/api-guideline-reviewer` reviews OpenAPI specs against bundled REST/IAM guidance; `/guideline-reviewer` reviews code/UI against bundled design-system and a11y standards. |
| [workflows-core](plugins/workflows-core/) | Shared foundation for the workflow plugin family — addressing, git handoff, model routing, emission — plus six utility commands. [Docs](plugins/workflows-core/docs/README.md) |
| [docs-workflows](plugins/docs-workflows/) | Seven commands: scaffold, brand and serve a docs portal, audit its coverage, write pages, profile, release notes. Needs `workflows-core`, `prose-style`. [Docs](plugins/docs-workflows/docs/README.md) |
| [prose-style](plugins/prose-style/) | Pluggable prose style enforcement: `/prose-review-pr`, `/prose-review-docs`, `/prose-style-refresh`, plus sub-agents `product-workflows` and `docs-workflows` use. Vendor-neutral, overridable baseline. |
| [obsidian-llm-wiki](plugins/obsidian-llm-wiki/) | Ten slash commands for compiling Obsidian vault knowledge into a persistent, cross-referenced wiki with task management; supports Claude Code and GitHub Copilot. |
| [acli](plugins/acli/) | Atlassian CLI (`acli`) skill for Jira and Confluence — search, work items, comments, attachments, boards, sprints, pages. From [pi-skill-acli](https://github.com/ziegenberg/pi-skill-acli) (MIT). |

## How the plugins fit together

`product-workflows`, `dev-workflows` and `docs-workflows` form one pipeline, from an idea or a customer's requirements document to shipped, documented code, and `workflows-core` is the foundation all three depend on. The **[family map](plugins/workflows-core/docs/family-map.md)** draws every command of the four on one diagram: grouped by role, coloured by plugin, with the deliverable each command hands the next. Each plugin's own workflow page carries the detail.

## Prerequisites

- **Claude Code** — the plugins install into Claude Code (some `obsidian-llm-wiki` commands also support GitHub Copilot).
- **`superpowers`** *(recommended)* — the Claude Code plugin `workflows-core` leans on for `/prompt-brainstorm`, and that the whole family uses for its brainstorm → plan → subagent-driven-development flow. No hard dependency; commands degrade gracefully without it.
- **`gh` + `gh auth login`** *(recommended)* — lets the family open the pull requests it drafts — a phase handoff's in the specs repo, `/implement`, `/vuln` and `/upgrade`'s in the code repo, and the `gh pr create` `/document` offers you for the docs branch it wrote. It buys nothing for diff reading, which is pure local `git` on any host.
- **`vale`** *(optional for `/document`; required by `/docs-init`)* — a prose linter for docs. `/document` falls back to a repo lint script, then the `prose-style` plugin, when `vale` is absent. `/docs-init` cannot: the repository it scaffolds lints with Vale in its own verification phase and in CI, so its toolchain preflight requires `vale`, together with `mkdocs`, `python3` and `pip` (or `uv`).
- **`curl`** and **`bash`** *(required by `/docs-serve`)* — it judges a dev server's port with `curl`, and starts, tests and signals the process group it runs each server in with `bash`. Off Linux it also needs `lsof` and `ps`, which macOS ships; on Linux it reads the socket and process tables from `/proc`, so a slim container needs nothing beyond those two. `/document`'s opt-in render check uses both too, and without either falls back to a table of pages to check by hand.
- **Recommended environment: [`ihudak/ai-containers`](https://github.com/ihudak/ai-containers)** — mounts every repository and your specs repo under one `/workspace` umbrella (repos at `/workspace/<repo>`, the specs repo at `/workspace/specs`), so the default `$REPOS_PATH` (`/workspace`) and an exported `SPECS_PATH` just work; it also installs `gh` and mounts the host `gh` auth. Outside a container the commands still work — set `$REPOS_PATH` yourself and manage `gh` login.

## Installation

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. Install plugins

```bash
claude plugin install dev-workflows@shipwright
claude plugin install product-workflows@shipwright
claude plugin install prose-style@shipwright
claude plugin install obsidian-llm-wiki@shipwright
claude plugin install acli@shipwright
claude plugin install guideline-reviewers@shipwright
claude plugin install workflows-core@shipwright
claude plugin install docs-workflows@shipwright
```

### 3. Configure environment variables

The workflow plugins resolve their inputs and outputs through three core environment variables — plus an optional `DOCS_PATH`, read-only as a documentation-grounding root and a write target for the docs commands that write a docs repository. Export them in your shell profile (or rely on the AI-Container defaults):

```bash
export SPECS_PATH="/workspace/specs"   # shared store: specifications, designs, ARDs
export REPOS_PATH="/workspace"         # where your code clones live (default: /workspace)
export DOCS_PATH="/workspace/docs"     # optional: your product docs clone; read-only for grounding (default: /workspace/docs)
export GIT_USER_INITIALS="iv-gu"       # optional: branch prefix for every command that creates a branch in a code or docs repo
```

- **`SPECS_PATH`** — the shared, team-visible store for a ticket's `specification.md` / `design.md` / ARD under `specifications/<KIND>-<KEY>-<slug>/…` (kind `BRD`/`PRD`/`EPIC`). It names the root of a dedicated specs repository, the directory that holds `specifications/`, never `specifications/` itself, which a run resolving an address stops on. Required by the commands that stop without it — `grep -lE 'Set SPECS_PATH|Required path environment variable unset' plugins/*/commands/*.md` lists them. `/implement`, `/document` in keyed mode and `/release-notes` are among them on a `<KEY>` address; an `@<path>` address and the direct modes do not need it; `/epics` and `/docs-audit`, among others, read the specs tree where it is set without carrying that stop.
- **`REPOS_PATH`** — where code clones live; a single directory or a colon-separated list. Defaults to `/workspace`. The match is by `git remote get-url origin` slug where a command was handed the slug; where a command lists candidates to offer you instead (`/create-ard`, bare `/idea --ground-code`, `/docs-init`, `/docs-brand` where neither its `--from` nor the docs profile's recorded source repositories settle the repository, and `/docs-audit` where those recorded repositories do not settle the set), your answer is resolved against that listing, so a rename changes the name a clone is offered under, never whether it is offered.
- **`DOCS_PATH`** *(optional)* — your product documentation's clone (default `/workspace/docs`), in **two roles**. As a **grounding root** it is read-only: when it is an existing directory containing markdown, the commands that ground on shipped docs — among them `/idea`, `/create-prd`, `/specify`, `/epics` and `/release-notes` — read it through the read-only `docs-grounder` agent, never write to it, and treat every miss as a silent, non-blocking skip. Disable grounding per run with `--no-docs`, or override the root with `--docs <path>`. As a **write target** it is a docs repository like any other: `/docs-init` scaffolds one there when nothing is there yet, and every other `docs-workflows` command that resolves a docs repository — `/document`, `/docs-profile`, `/docs-brand`, `/docs-audit` and `/docs-serve` — writes into the one it resolves there (`/docs-audit` its backlog, `/docs-serve` the record of the server it started). The two roles are different uses of one variable, not a contradiction; `plugins/workflows-core/references/docs-grounding.md` owns the first and `plugins/docs-workflows/references/docs-workflow/repo-resolution.md` the second.
- **`GIT_USER_INITIALS`** *(optional)* — your branch identifier, used verbatim (no trailing `/`) by every command that creates a branch in a code or documentation repository; `plugins/workflows-core/references/branch-naming.md` names them. Branch naming is **repo-rule-first**: each command reads the target repo's own `CONTRIBUTING.md` / `README.md` / `DOCUMENTATION-GUIDELINES.md` / `CLAUDE.md` and follows the convention documented there. Where that convention has a name/initials segment — as `example-docs` does (`<your-name-or-initials>/<JIRA-ISSUE-KEY>-<short-branch-name>`) — this variable fills it, giving `iv-gu/PRODUCT-1234-add-oauth`. Where it has none (say a plain `feat/<slug>` repo), the convention is followed as written and no initials are injected. Only when a repo documents no convention at all does this variable become the whole prefix. When unset, the commands fall back to `git config user.initials`, then infer from existing branch names, then ask. Full algorithm: `plugins/workflows-core/references/branch-naming.md`.

### 4. Run `/workflows-core:statusline` first

After installing, run `/workflows-core:statusline` once. The command ships in `workflows-core`, so install that plugin too (step 2 above lists it). It installs the family's multi-line status line (session identity, git, context, cost, tokens, rate limits) into `~/.claude/settings.json` and enables the Option-B snapshot used by session-cost reporting. It is idempotent and backs up anything it would overwrite, and it changes no workflow-command behavior.

```
/workflows-core:statusline
```

> Claude Code ships its own built-in `/statusline` command (backed by the `statusline-setup` agent) that configures a plain, single-line status line. Since the plugin's command shares that name, typing the bare `/statusline` runs Claude Code's built-in flow instead — always use the fully-qualified `/workflows-core:statusline` to install the family's status line.

### 5. Update after new releases

Two steps, and the second is the one that actually changes what runs:

```bash
claude plugin marketplace update shipwright
claude plugin update dev-workflows@shipwright
claude plugin update product-workflows@shipwright
claude plugin update prose-style@shipwright
claude plugin update obsidian-llm-wiki@shipwright
claude plugin update acli@shipwright
claude plugin update guideline-reviewers@shipwright
claude plugin update workflows-core@shipwright
claude plugin update docs-workflows@shipwright
```

**The `/plugins` interface is the easiest route, and it does update installed plugins.** Run `/plugins` inside Claude Code and update the marketplace from there: unlike the CLI's `marketplace update`, that path upgrades what you already have. You can also turn on **AutoUpdate** per plugin there, after which they keep themselves current and none of the above is needed.

**If a plugin has been renamed, marketplace update will not update anything** — not that plugin and not the others. The remedy is to remove the marketplace and its plugins and install from scratch:

```bash
claude plugin marketplace remove shipwright
claude plugin marketplace add ihudak/ai-workflows
```

then reinstall the plugins you want, per step 2.

### Moving from the old marketplace name

Until 2026-09-24 this marketplace was named `ihudak-plugins` and lived at `ihudak/ihudak-claude-plugins`. GitHub redirects the old repository URL. The marketplace name, though, is part of every install key (`dev-workflows@ihudak-plugins`), so moving to the new name means re-registering. Removing a marketplace uninstalls the plugins installed from it, so reinstall each one you had afterwards:

```bash
claude plugin marketplace remove ihudak-plugins
claude plugin marketplace add ihudak/ai-workflows
claude plugin install workflows-core@shipwright
```

Then run `claude plugin install <plugin>@shipwright` for each other plugin you use (the list is in step 2), and restart Claude Code. Your environment variables and your specs, docs and code repositories are not touched.

**`marketplace update` from the CLI refreshes the catalogue, not your installed plugins.** It updates what the marketplace advertises — which is what makes a newly added plugin installable — but an already-installed plugin stays at the version you installed. `claude plugin update <plugin>` is what upgrades one from the command line, and **it requires restarting Claude Code to apply.** Update only the plugins you actually have.

This page used to say `marketplace update` alone was enough. It is not, and the symptom is quiet: `claude plugins list` keeps reporting the old version while the catalogue advertises the new one, so the content looks current and is not.

## Directory structure

The environment variables expect these layouts:

```
$SPECS_PATH/                      # shared, team-visible store
  specifications/PRD-<KEY>-<slug>/  # prd.md, ard.md (+ EPIC-<KEY>-NN-<slug>/ holding specification.md, design.md)

$REPOS_PATH/                      # code clones (default /workspace)
  <repo>/                         # discovered by directory name; matched by origin slug where the command was handed one

$DOCS_PATH/                       # optional: product docs clone (default /workspace/docs)
  ...                             # e.g. an example-docs checkout; read-only for grounding, written by the docs commands
```

## Adding new plugins

1. Create a subdirectory under `plugins/` with the plugin name.
2. Add `.claude-plugin/plugin.json` (name, description, author).
3. Add `commands/`, `agents/`, `hooks/`, and/or `skills/` as needed.
4. For hooks, add a `hooks/hooks.json` declaring the registrations.
5. Register the plugin in `.claude-plugin/marketplace.json`.
6. Commit and push to `main`.

## License

MIT — see [LICENSE](LICENSE).

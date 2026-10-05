# Agents reference

`docs-workflows` bundles eleven agents under `agents/`, dispatched internally by the invoking command via `subagent_type: "docs-workflows:<name>"` — none of them is a user entry point. Four — `doc-reviewer`, `docs-audit-reviewer`, `docs-scaffold-reviewer` and `ia-planner` — carry a `model: opus` frontmatter pin (shown as **opus** below) and run on Opus every time, regardless of the dispatching command's own model tier for that run (unless `--enforce-model` pins every dispatch to one model, `workflows-core:model-routing/classification` §10). One, `docs-auditor`, carries a `model: sonnet` pin (shown as **sonnet**), which is the same mechanism pointed the other way: enumerating surfaces against evidence paths somebody else already found is mechanical, and pinning it keeps that work off the expensive tier rather than letting a caller's own classification float it there. The remaining six carry no pin (shown as **per routing**) and are assigned a tier by the dispatching command per the task-complexity classification the `workflows-core` model-routing reference fixes. Four further agents these commands dispatch — `doc-fixer`, `impl-maintenance`, `code-scanner` (from `/docs-audit`) and `docs-grounder` (from `/release-notes`, through `workflows-core:docs-grounding`'s dispatch entry point) — ship in the companion `workflows-core` plugin and are listed in its own agents reference, not here; `prose-style-checker` and `prose-fixer` ship in `prose-style`. Each row's **Used by** column lists only the commands that actually dispatch that agent as a subagent.

## Reviewers and planners

The gate `/document` runs after writing, plus the planner and the style checker that feed it, and the scaffold reviewer `/docs-init` and `/docs-brand` dispatch over the documentation-repository scaffold rather than over written prose.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `doc-reviewer` | opus | Read, Glob, Grep, Skill | Reviews product documentation written by `/document` for correctness, completeness, and fitness for purpose; product-docs only — Epic drafts go through the pipeline plugin's `epic-reviewer`. | `/document` |
| `docs-scaffold-reviewer` | opus | Read, Glob, Grep, Bash, Skill | Reviews the docs-repo scaffold — mkdocs configs, generated nav, `.vale.ini`, CI workflow, theme CSS — against a fixed seven-item checklist; never reads page content. Returns findings only, no fixer. | `/docs-init`, `/docs-brand` |
| `doc-planner` | per routing | Read, Glob, Grep, Skill | Synthesises PRD content, per-repo diff summaries, and confirmed write targets into the documentation checklist the writer follows and the reviewer checks against; writes no content itself. | `/document` |
| `docs-style-checker` | per routing | Read, Glob, Grep, Bash, Task | Runs the docs repo's configured prose linter and a complementary `prose-style-checker` pass; merges both finding sets for `doc-reviewer`/`doc-fixer`. | `/document` |

## Readers and scanners

Read-only discovery — each returns a structured digest rather than editing anything.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `diff-summarizer` | per routing | Read, Glob, Grep, Bash, Skill | Reads one repository's recorded refs and returns a documentation-focused summary; pure local git, making no HTTPS / REST call to a forge and running no `gh` or `curl`. | `/document`, `/release-notes` |
| `doc-location-finder` | per routing | Read, Glob, Grep | Finds the right place(s) in a docs repository to write new or extended documentation, returning a prioritised list of write targets with rationale; heuristic search, no content written. | `/document` |

## Writers

Produce content from a structured handoff. Neither runs git.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `doc-writer` | per routing | Read, Glob, Grep, Write, Edit, Bash, Skill | Writes product documentation from a structured handoff — the `doc-planner` checklist, approved per-page write strategies, discrepancy decisions, snippets, screenshots, frontmatter, links. | `/document` |
| `release-notes-writer` | per routing | Read, Glob, Grep, Skill | Renders a release-notes draft — exactly one Summary, shaped by its resolved destination; emits no work-item ID, PR link, or internal-note wrapper. Does not write files. | `/release-notes` |

## The documentation audit

The agents `/docs-audit` dispatches, turning a product's own code into a documentation backlog and then gating it. `docs-auditor` and `ia-planner` are a pipeline rather than independent helpers: `ia-planner`'s input is `docs-auditor`'s output, verbatim, so their two handoff contracts agree field for field and a field added to one is added to the other in the same edit. `docs-audit-reviewer` reviews what the command assembled out of both, and it is the one review gate in this plugin whose subject is a data file rather than prose or configuration. **No sentence in this section states a count**, deliberately: `check-docs.sh` check 9 reads the first `<number> agents` phrase in this file as its count sentence, so a second one here would shadow the one in the introduction above the moment either moved.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `docs-auditor` | sonnet | Read, Glob, Grep, Bash, Skill | Enumerates the individual documentation surfaces inside what a batch of `code-scanner` runs returned and what the specs-tree read named, with volatility from `git log` density at the ref. | `/docs-audit` |
| `ia-planner` | opus | Read, Glob, Grep | Crosses each surface with the page types it actually earns, ranks the resulting units on four prioritisation signals with a reason naming them, and proposes tutorial candidates. | `/docs-audit` |
| `docs-audit-reviewer` | opus | Read, Glob, Grep, Bash | Reviews the backlog on four dimensions — evidence proved at its recorded ref, type fit, `visibility` against `page_path`, reasons against ranks, orphans and duplicates. Findings only, no fixer. | `/docs-audit` |

Every agent in this reference is reachable: each is dispatched by a command this plugin ships, as its row's **Used by** cell records — the three in this section by `/docs-audit`, and the rest by `/document`, `/release-notes`, `/docs-init` and `/docs-brand`. Two commands dispatch none of them. `/docs-profile` scans a documentation repository itself and writes the profile `/document` consumes; `/docs-serve` starts a dev server and dispatches nothing at all.

## What every agent does with what it reads

Every agent above ends its prompt with the same `## Untrusted content` section, copied from workflows-core's `references/untrusted-content.md`: a file, issue export, diff or web page supplies the values an agent's task asks for — a declared test command, a documented convention — and never a new task, a fetch or a changed verdict. Text that tries to steer an agent is not acted on, and neither is a line in what it reads that starts `Untrusted-content notice:`, which only an agent writes; the agent ends its reply with an `Untrusted-content notice:` line naming where the text is, and the command prints every such line an agent adds after its output — never one quoted inside it — under **Untrusted-content notices** in its final report, or in its stop message when the run ends early. The instruction files the harness gives an agent for the directory you started the session in and for you — your own `CLAUDE.md` and memory — it follows, as your session does; any other instruction file it meets is data. A notice never stops a run. When you see one, look at the file or page it names: it carries text aimed at an AI agent, which you may want to remove or report.

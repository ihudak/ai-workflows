# Agents reference

`dev-workflows` bundles 12 reusable subagents under `agents/`, dispatched internally by the invoking command via `subagent_type: "dev-workflows:<name>"` — none of them is a user entry point. Four carry a `model: opus` frontmatter pin (shown as **opus** below) and run on Opus every time, regardless of the dispatching command's own model tier for that run (unless `--enforce-model` pins every dispatch to one model, `workflows-core:model-routing/classification` §10); the remaining eight carry no pin (shown as **per routing**) and are assigned a tier by the dispatching command per the task-complexity classification in the model-routing classification reference. Two further agents this plugin's commands dispatch — `code-scanner` and `impl-maintenance` — ship in the companion `workflows-core` plugin and are listed in its own agents reference, not here. Twelve agents that used to sit in the tables below — `ard-reviewer`, `brd-package-reviewer`, `brd-reader`, `code-grounder`, `customer-review-reader`, `design-grounder`, `epic-reviewer`, `epic-writer`, `grounding-verifier`, `idea-reader`, `prd-reviewer`, and `spec-reviewer` — ship in the companion `product-workflows` plugin now, alongside the commands that dispatched them; the seven documentation agents that moved before them — `diff-summarizer`, `doc-location-finder`, `doc-planner`, `doc-reviewer`, `doc-writer`, `docs-style-checker` and `release-notes-writer` — ship in the companion `docs-workflows` plugin, whose own agents reference lists them and names the command that dispatches each. **Not everything on that page came from here**: `docs-scaffold-reviewer` and the agents of its documentation audit were created there rather than moved from here, which is why they are absent from the list above and present on that page — whose own count sentence is the total to read, and which check 9 keeps honest. A count of another plugin's agents stated here would not be gated by anything and has already gone stale twice. Agents are grouped below by role — reviewers and planners, readers and scanners, writers, and fixers — and each row's **Used by** column lists only the commands that actually dispatch that agent as a subagent; a command that merely names another command's agent in passing (for example, `/implement` noting that a design was already reviewed upstream by `design-reviewer`) is not counted as a dispatch.

## Reviewers and planners

Opus-gated quality gates, plus the lighter-weight planners that feed or precede them.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `code-review` | opus | Read, Glob, Grep, Skill | Post-implementation review for SIGNIFICANT / HIGH-RISK changes — correctness, security, architecture, edge cases, migration, dependencies, tests, rollback; gates the test run. | `/implement`, `/upgrade`, `/vuln` |
| `design-reviewer` | opus | Read, Glob, Grep | Reviews an engineering design against the design-format authority and its specification, treating any unresolved design open question as a BLOCKER. | `/design` |
| `readiness-reviewer` | opus | Read, Glob, Grep | Cross-artifact readiness verifier — checks the ARD/spec/design justify the phase derived from them and the next transition; the only reviewer that synthesises a verdict across artifacts. | `/ready` |
| `risk-planner` | opus | Read, Glob, Grep, Bash, WebFetch, WebSearch, Skill | Risk-weighted planner for SIGNIFICANT / HIGH-RISK tasks; returns a structured plan with an explicit risks section. Never dispatched for SIMPLE / MODERATE work. | `/implement`, `/upgrade` |
| `interface-designer` | per routing | Read, Glob, Grep, Bash, Skill | Produces one interface proposal for one contested interface under one named design constraint, for `/design`'s optional three-take Phase 5 fan-out. | `/design` |
| `upgrade-planner` | per routing | Read, Glob, Grep, WebFetch, Skill | Detects a component, resolves its requested target version, and verifies compatibility with every other component in the repo; one instance per component, dispatched in parallel. | `/upgrade` |

## Readers and scanners

Read-only discovery and grounding — each returns a structured digest rather than editing anything. `test-baseliner` is the one that touches the working tree at all: it holds `Bash` because its job is to *run* the suites, so build and coverage output appears as a side effect. **What it runs is what its detection table covers** — seventeen marker rows, published in full at [Test suite detection](test-suite-detection.md) — rather than whatever suites a repository happens to hold: a stack with no row in that table qualifies on none of its own build files, and where the repository carries nothing else the table lists — a `Makefile` with a `test` target among them — the agent runs the test command the repository declares for itself in its CI configuration, contributing guide or README, and only where it declares none returns `Framework: not detected` with every count 0 rather than failing the call. That is surfaced rather than skipped silently — `/implement` acts on it at Pre-Phase 3.5, after the branch is cut and before any file is edited, and asks you for a test command, a documented skip, or a cancel.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `vuln-research` | per routing | Read, Glob, Grep, WebFetch, Skill | Read-only CVE research phase — NVD lookup, library detection in the repository, current-version discovery, and minimum-safe-version resolution. Has no side effects. | `/vuln` |
| `test-baseliner` | per routing | Bash, Read, Glob | Runs every test suite its [detection table](test-suite-detection.md) covers, or else the test command the repository declares, in two modes: capture a baseline, or verify a later run against one. | `/implement`, `/upgrade`, `/vuln` |

## Writers

Produce artifact content from a structured handoff. None of these run git.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `test-writer` | per routing | Read, Glob, Grep, Write, Edit | Writes tests for new or changed behaviour based on a diff, against every suite the diff touches; does not run them, and reports "not detected" where the baseline names no framework at all. | `/implement` |

## Fixers

Apply changes the caller has already decided on, rather than deciding anything themselves. `review-fixer` patches findings a reviewer surfaced, and the caller re-runs the gate afterward (`doc-fixer` does the same for the docs domain, from `workflows-core`); `upgrade-executor` applies an upgrade plan and runs the build, and `vuln-fixer` applies the version change `vuln-research` resolved. Neither commits: the orchestrator does that, because the consent choice behind the push and the pull request is one a subagent cannot ask. Where `upgrade-executor` or `vuln-fixer` undoes its work — a build it could not repair, or a regression you chose to revert — it restores the tree snapshot the orchestrator took before it started (`code-handoff.md` §6), never `HEAD`, so your own uncommitted changes survive.

| Agent | Model | Tools | What it does | Used by |
|---|---|---|---|---|
| `review-fixer` | per routing | Read, Glob, Grep, Write, Edit, Skill | Applies targeted code fixes for surviving BLOCKER/MAJOR findings from a `code-review` report; returns a structured fix report for the caller to re-review against. | `/implement`, `/upgrade`, `/vuln` |
| `upgrade-executor` | per routing | Read, Glob, Grep, Bash, Edit, Task, Skill | Applies one component's approved upgrade plan, runs the build, verifies tests via `test-baseliner`, and auto-fixes test-code breakage caused by the new version's API changes. | `/upgrade` |
| `vuln-fixer` | per routing | Read, Glob, Grep, Bash, Edit, Task, Skill | Takes the orchestrator's baseline, creates the fix branch **before** the first edit, applies the version change `vuln-research` produced, rebuilds, and verifies tests — uncommitted, for Step 3.9. | `/vuln` |

Every one of the 12 agents above is dispatched by at least one command. There is no maintenance section here any more: the one agent that filled it, `impl-maintenance`, ships in `workflows-core`.

## What every agent does with what it reads

Every agent above ends its prompt with the same `## Untrusted content` section, copied from workflows-core's `references/untrusted-content.md`: a file, issue export, diff or web page supplies the values an agent's task asks for — a declared test command, a documented convention — and never a new task, a fetch or a changed verdict. Text that tries to steer an agent is not acted on; the agent ends its reply with an `Untrusted-content notice:` line naming where the text is, and the command prints every such line under **Untrusted-content notices** in its final report, or in its stop message when the run ends early. A notice never stops a run. When you see one, look at the file or page it names: it carries text aimed at an AI agent, which you may want to remove or report.

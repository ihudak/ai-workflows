# Getting started

This page takes you from zero to your first successful run — install the plugin, set the environment variables it reads, and run `/idea` end to end. Once you have done this once, [Workflow overview](workflow.md) shows the whole pipeline and [Roles and phases](roles-and-phases.md) says what your role owns at each step.

## Install

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. Install plugins

```bash
claude plugin install product-workflows@shipwright
```

`product-workflows` is the plugin this documentation covers. It declares two hard dependencies, installed automatically alongside it: `workflows-core`, its shared foundation, and `prose-style`, whose `prose-style-checker` is `/epics`'s primary style checker and the unconditional Phase 3.5 pass every PRD-authoring command here runs. Neither is optional here — an absent `prose-style` would leave those commands with no absent case to degrade into, which is why the plugin declares it rather than reaching for it at runtime. The companion `dev-workflows` plugin is not a dependency in either direction: it produces `specification.md`'s downstream consumer (`/dev-workflows:design`), but `product-workflows` installs and runs without it, against a specs tree someone else's engineering work will eventually fill in.

**What you also need, and it is not a plugin.** Nothing beyond `gh`, when present, for opening the pull requests it drafts — without it a run reports the branch it pushed and leaves the pull request to you. The specs repo is the one markdown tree the pipeline *writes*; it also reads your product-docs clone under `$DOCS_PATH` and, where a command grounds on code, the clones under `$REPOS_PATH`, which are no markdown tree at all. If you keep your work in a tracker as well, syncing the two is yours to arrange; no command here learns whether one exists.

**What you do not need for this plugin.** The marketplace also ships `obsidian-llm-wiki`, `acli` and `guideline-reviewers` — none of them is used by `product-workflows`. Install them if you want them for their own sake; see the [marketplace README](../../../README.md).

## Update

```bash
claude plugin marketplace update shipwright
claude plugin update product-workflows@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update product-workflows@shipwright` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same thing with a picker. This page used to say the first line alone was enough; it is not, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one.

## What you set on your machine

`product-workflows` reads four environment variables. One is required for the pipeline to have anywhere to write (`SPECS_PATH`); the other three are optional and each degrades to a documented default or a silent skip.

### `SPECS_PATH`

The **shared, team-visible repository for the AI-authored documents** — the idea brief, the Product Requirements Document, the ARD, `specification.md`, and every BRD-route artifact, each under a kind-prefixed folder — `specifications/PRD-<KEY>-<slug>/` or `specifications/BRD-<KEY>-<slug>/`, with `EPIC-` folders below a PRD. This is the reason a second store exists at all: it is the medium through which one role hands work to the next. A producing command lands its artifact on the specs repo's default branch, and the next command in the chain refuses to start expensive work until it finds that artifact there — not merely written to disk, and not merely committed to a branch of its own. See [Roles and phases](roles-and-phases.md) for what each seam hands over and what happens when an artifact is missing or stuck on an unmerged branch. Set it to the root of a dedicated specs repository, the directory that holds `specifications/`, never to `specifications/` itself: a run that resolves an address against the latter stops and names the value to set instead ([Environment](reference/environment.md)).

### `REPOS_PATH`

Where your mounted implementation and design code clones live — one directory, or a colon-separated list of them. It has a sensible built-in default, so most readers never need to set it at all; see [Environment](reference/environment.md) for the exact value and resolution order. `/create-ard` and `/idea` (with `--ground-code`) list top-level directories under `$REPOS_PATH` and offer them to you, so a repo renamed on disk is offered under its new name rather than lost — except where `/idea`'s `--ground-code <repo>,<repo>` names one, since every comma-separated part must match a top-level **basename** to be read as a repo at all. `/prd-ground` instead grounds against the repositories `grounding/baselines.md` pins by commit.

### `ARCHITECTURE_REPO_PATH`

A **read-only** clone of your organisation's architecture repository — its technology radar, standards, principles, patterns and ADRs. Set it and `/create-ard` grounds the ARD in it: the decisions it settles are cited, and every departure from it is recorded as an open question. Unset, `/create-ard` runs exactly as without it.

### `DOCS_PATH`

Your shipped product documentation's clone — **read-only** in its role as a grounding root, which is the only role this plugin gives it. Eight of this plugin's commands ground against what is already published, so a new draft does not contradict or duplicate an existing page: `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/epics`, `/brd-intake`, and `/prd-ground`. The plugin never writes to `DOCS_PATH`; every miss — unset, missing, or no markdown found — is a silent, non-blocking skip. Disable per-run with `--no-docs` — and, in `/prd-ground`, also with `--no-code` — or override the root with `--docs <path>`, which all eight parse.

## Your first run

`/idea` is the pipeline's entry point. It takes **one argument you choose yourself** — the key that names the folder this idea will live in — because there is nowhere keyless to write: the brief lands in its final folder on the first write and is never moved afterwards. Point it at whatever you already have in mind: an inline prompt, or a markdown file with `@path`.

```
/idea ACME-77 a lightweight way for on-call engineers to silence a noisy alert for one hour without editing the alerting rule
```

`ACME-77` is yours to invent — nothing looks it up, and no tracker is read. It only has to match `^[A-Z][A-Z0-9_]*(-\d+)+$`.

Here is what to expect:

1. **A bounded grill.** `/idea` asks you up to ten questions, one at a time, to sharpen the idea before writing anything — scope, who it is for, what "done" looks like. Answer as best you can; a question you cannot answer yet becomes a logged `[NEEDS CLARIFICATION]` marker rather than a blocker. (`--deep` drops the cap and grills to convergence instead.)
2. **A written brief.** It writes `idea.md` — a lean one-page brief — into `$SPECS_PATH/specifications/PRD-ACME-77-<slug>/`, creating that folder if it does not exist. If `DOCS_PATH` is set and readable, the idea is also checked against what is already documented.
3. **A handoff.** At the end it offers to commit the brief, push it, and open a pull request against the specs repo's default branch. Once that lands, `/create-prd ACME-77` finds `idea.md` in the same folder and takes over.

If your starting point is a customer-supplied requirements document instead of a prompt, [BRD workflow](brd-workflow.md) shows the alternative entry point: `/brd-intake` in place of `/idea`.

From here, [Workflow overview](workflow.md) shows where every other command sits relative to `/idea`, and [Roles and phases](roles-and-phases.md) says what happens at each handoff along the way.

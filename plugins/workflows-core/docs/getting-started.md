# Getting started

Add the marketplace, then install this plugin:

```bash
claude plugin marketplace add ihudak/ai-workflows
claude plugin install workflows-core@shipwright
```

To pick up later changes:

```bash
claude plugin marketplace update shipwright
claude plugin update workflows-core@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same with a picker. This page used to say the first line alone was enough; it is not, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one.

## What this plugin is

`workflows-core` is the shared foundation of the `dev-workflows` plugin family. Most of what it ships is not a command: it is the reference corpus the sibling plugins read — `dev-workflows`, `product-workflows`, and `docs-workflows` all declare it as a dependency — the `model-routing` skill every pipeline command loads at its classification step, and six agents any of them may dispatch. If you have installed a plugin from that family, you want this one installed too.

It does ship six commands of its own, and one of them is worth running first — see below.

## What you set on your machine

`workflows-core` reads eight environment variables, and every one of them is read by a reference this plugin ships — for seven of the eight, the only read anywhere in this plugin. `SPECS_PATH` is the exception: `/frames` gates on it in its own Phase 0 and refuses to run without it. One is required for anything in the family to have somewhere to write (`SPECS_PATH`); the rest are optional and each degrades to a documented default or a silent skip. [Environment](reference/environment.md) has the exact defaults and failure behaviour.

### `SPECS_PATH`

The **shared, team-visible store for the AI-authored documents** and for every run's bookkeeping — cost entries, session feedback, follow-ups. It has no default: nothing is guessed, and with it unset those entries degrade to report-only rather than being written somewhere else. `/frames` is the exception among this plugin's commands — *"every path this command reads or writes is under it"* — so it stops in Phase 0 rather than degrading. Set it to the root of a dedicated specs repository, the directory that holds `specifications/`, never to `specifications/` itself: a run that resolves an address against the latter stops and names the value to set instead ([Environment](reference/environment.md)).

### `REPOS_PATH`

Where your code clones live — one directory, or a colon-separated list of them. It has a sensible built-in default, so most readers never need to set it. The command resolves a repository under it and hands `code-scanner` an absolute `repo_path` — no agent reads `REPOS_PATH` itself.

### `DOCS_PATH`

A **read-only** clone of your shipped product documentation, used by `docs-grounder` to ground a draft against what is already published. Never written to as a grounding root — a `docs-workflows` command that resolves `$DOCS_PATH` as the documentation repository it edits writes into it, which is a different use of the same path; every grounding miss is a silent, non-blocking skip.

### `GIT_USER_INITIALS`

Your branch identifier. Branch naming is repo-rule-first: where the target repo's own documented convention has a name-or-initials segment, this fills it; where it does not, the variable is simply unused for that repo.

### `DEV_WORKFLOWS_COST_PRICES`

An optional path to your own price table, overriding the bundled `references/cost-prices.yaml` that session-cost reporting prices tokens against. It is the variable of the eight you are least likely ever to set — the bundled defaults are used until you do. It keeps its original name so a setting already exported on a working machine is not silently ignored.

### `WORKFLOWS_SKIP_COSTS`

Persistent default for the `--skip-costs` run flag every applicable command accepts — the command still advances the session-cost checkpoint, but never writes a cost entry. `workflows-core:run-flags` is the single source of truth for this and the other two run flags.

### `WORKFLOWS_SKIP_FEEDBACK`

Persistent default for the `--skip-feedback` run flag — narrows an applicable command's maintenance phase to bug capture only, dropping the in-session Lessons Learned report. See `workflows-core:run-flags`.

### `WORKFLOWS_ENFORCE_MODEL`

Persistent default for the `--enforce-model` run flag — pins every subagent an applicable command dispatches to one model (an alias, a full model id, or `routing` for no enforcement), bypassing model-routing's own per-step selection. Where the agent tool selects models by family only, a version-specific value is honoured only for its family's newest model and runs as the family name; the harness picks the version. See `workflows-core:run-flags`.

## Install the status line

**Worth doing before your first real run.** Two things come out of it.

The visible half is a permanent multi-line status line at the bottom of your terminal — session identity, git state, context usage, running cost, tokens, and rate limits — so you can see a long command spending your budget while it spends it.

The half you don't see is the **cost cross-check**: Claude Code's own reported cost, captured per render, which the cost phase differences into a per-invocation delta. Where that disagrees with the computed figure, the gap is the signal that the bundled price table has drifted. See [Session cost](reference/session-cost.md).

```
/workflows-core:statusline
```

Claude Code ships its own built-in `/statusline` command, so typing the bare form reaches that instead of this plugin's — always use the qualified form.

## The other five commands

Four of them are how you tell the plugin family it got something wrong: [`/feedback`](commands/feedback.md) logs a note in your own words, while [`/prompt`](commands/prompt.md), [`/prompt-brainstorm`](commands/prompt-brainstorm.md) and [`/prompt-grill-me`](commands/prompt-grill-me.md) capture a correction you just made and then act on it — directly, by redesigning it, or by grilling it. The fifth, [`/frames`](commands/frames.md), rebuilds the index an exported design frame set must carry before anything else can read it.

See the [documentation index](README.md) for everything else, including the [Workflow overview](workflow.md).

# Getting started

This page takes you from zero to your first successful run — install the plugin, set the environment variables it reads, and run `/document` end to end. If the project you want to document has no documentation repository at all, start with [Your first run on a project with no docs](#your-first-run-on-a-project-with-no-docs) instead. Once you have done this once, [Workflow overview](workflow.md) shows how the seven commands fit together.

## Install

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. Install the plugin

```bash
claude plugin install docs-workflows@shipwright
```

Two other plugins arrive with it, because they are **declared dependencies** rather than suggestions. `workflows-core` carries the shared reference corpus every command here loads at runtime — an unsatisfied dependency disables the plugin instead of letting it half-run, which is the intended behaviour: there is no degraded mode to fall back to. `prose-style` is the complementary semantic prose pass the style check runs alongside a repo's own linter, and the fallback linter when a repository configures none.

**What you do not need.** The two companion pipeline plugins, `product-workflows` and `dev-workflows`, are not dependencies in either direction. `/document` and `/release-notes` read a folder in a specs tree; whether the plugin that authored that folder is installed on *your* machine makes no difference. Install `product-workflows` if you also author ideas, PRDs, ARDs, specifications and Epics, and `dev-workflows` if you also design and implement.

**What you also need, and it is not a plugin.** A prose linter helps but is not required — `vale`, a repo lint script, `markdownlint` or `remark` are all detected if present, and `prose-style` covers the run when none of them is. Because `prose-style` arrives as a declared dependency, a repository with no linter of its own is still style-checked rather than waved through; what a missing `vale` costs you is its lexical pass — the one your CI runs on your pull request, where your CI runs Vale — which is why the Phase 0 toolchain preflight names it. **`/docs-init` is the exception, and needs `vale` outright** — together with `git`, `python3` and `pip` (or `uv`), and `mkdocs` — because the repository it scaffolds lints with Vale both in its own verification phase and in its CI workflow; its preflight reports any of them missing before a single file is written. **`/docs-serve` needs `curl` and `bash`**, and off Linux `lsof` and `ps` too, both of which macOS ships; on Linux it reads which process holds a port from `/proc`, so a Linux container that ships neither `lsof` nor `ps` — even one that drops root before you could install them — runs it as it is, given `curl` and `bash`.

## Update

```bash
claude plugin marketplace update shipwright
claude plugin update docs-workflows@shipwright
claude plugin update prose-style@shipwright
```

**Both kinds of step are needed, and the `plugin update` lines are the ones that change what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same with a picker. This page used to say the first line alone was enough; it is not, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one. **Update `prose-style` with it**: 0.4.0 is the release whose checker applies the specs repository's house-style rules to `/release-notes`' draft, and beside an older one that command records its style check `DEGRADED` and says to update `prose-style`.

## What you set on your machine

This plugin reads four environment variables. None is required for a direct-mode `/document` edit, for `/docs-profile`, or for `/docs-init`; a keyed run wants the first, and the rest degrade to a documented default or a silent skip. [Environment](reference/environment.md) has the exact resolution order and failure behaviour for each.

### `SPECS_PATH`

The shared, team-visible repository holding the Product Requirements Document folder a keyed run reads, and the one place a run commits its own session bookkeeping. Set it to the root of your dedicated specs clone, the directory that holds `specifications/`, never to `specifications/` itself: a keyed run against the latter stops and names the value to set instead ([Environment](reference/environment.md)). Without it, neither `/document` nor `/release-notes` has anything to resolve a key against, and each stops on a key address, naming the variable and offering to set it or cancel; given an `@<path>` address instead, `/release-notes` runs on and falls back to attributing its cost to the PM's early phase.

### `REPOS_PATH`

Where your code clones live — one directory, or a colon-separated list of them. It defaults to `/workspace`, so most readers never set it. A keyed `/document` run resolves each repository its implementation record and commit scan name to a local clone under here, matched by `git remote get-url origin` slug and **never by directory name**, so a clone renamed on disk is still found as long as its `origin` remote is intact.

### `DOCS_PATH`

Where your product documentation's clone lives, defaulting to `/workspace/docs`. `/document` prefers it as a docs-repo discovery hint when your current working directory carries no documentation signals — in a container the docs clone is usually mounted right here, which makes this the common fast path — and `/docs-init` scaffolds a new documentation repository here when nothing is there yet. `/release-notes` reads the same variable for optional grounding against what is already published, and **as a grounding root it is read-only**: that is the one role in which nothing writes into it. Writing into the docs repository it points at is a different role, not a contradiction.

### `GIT_USER_INITIALS`

Your branch identifier, used by every run that creates a branch in a documentation repository — `/document` in keyed mode, `/docs-profile`, `/docs-init`, and a standalone `/docs-brand`. Branch naming is repo-rule-first: each reads the target repo's own documented convention and follows it as written, and this variable only fills a name-or-initials segment where the convention asks for one. A repository `/docs-init` has just created documents no convention yet, so there the fallback prefix and this variable are the whole of it.

## Your first run on a project with no docs

If there is no documentation repository yet, `/docs-init` makes one:

```
/docs-workflows:docs-init /workspace/docs
```

It resolves the target (and refuses outright if that directory already looks like a documentation repository — pointing you at `/docs-profile` instead, which is the command for one that already exists), offers to `git init` an empty or absent directory outside every git work tree (a target below a work tree's top level, existing or not, stops the run), confirms which code repositories the portal will document, branches, then writes the page skeleton, both build configs, `.vale.ini` with a project vocabulary seeded with the product name and the few technical words the scaffold's own pages use (so the scaffold passes its own lint gate, locally and in CI alike), a CI workflow carrying the visibility gates, and `.dev-workflows/docs-profile.yml`. It runs `/docs-brand --inline` to pick up a logo and colours from the product's own code, verifies that both builds and the linter actually work, gates the whole diff on an Opus review, and leaves it on a branch with a drafted pull request. It never pushes and never merges.

Then `/docs-workflows:docs-serve` serves the result and reports a URL you can open in your browser — it opens nothing itself — and `/document` starts filling it in. Skip straight to the next section if your documentation repository already exists.

## Your first run

Start with `/docs-profile`, once per documentation repository:

```
/docs-workflows:docs-profile ~/repos/your-docs
```

It scans the repository, proposes a `.dev-workflows/docs-profile.yml` and complementary `CLAUDE.md` guidance, and leaves both on a branch with a drafted pull-request message. It never pushes or auto-merges. Skip this step and `/document` still runs — it falls back to a bundled default profile, or offers to profile the repository inline.

Then document a feature from its PRD:

```
/docs-workflows:document ACME-77
```

Here is what to expect. The run resolves the docs repository and its profile, reads the resolved PRD folder, resolves the repositories its implementation record and commit scan name to local clones, summarises their diffs in parallel, finds where each page belongs, plans the documentation, writes it, runs the style check, and gates the result on an Opus review before finishing on a branch with a copy-paste pull-request draft. For a one-off typo fix, pass a file or a description instead of a key — `/docs-workflows:document @note.md` — and the run takes the much shorter direct-mode path.

From here, [Workflow overview](workflow.md) shows where `/release-notes` fits, and the [documentation index](README.md) links every command page and inventory.

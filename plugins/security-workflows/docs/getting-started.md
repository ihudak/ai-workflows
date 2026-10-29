# Getting started

This page takes you from zero to your first recorded scan: install the plugin, set the one environment variable it reads, check the two things Claude Security needs, and run `/security-workflows:scan` on an Epic before its pull request merges. Once you have done this once, [Workflow overview](workflow.md) shows where the command sits in the family's delivery, and [Roles and phases](roles-and-phases.md) says who runs which mode.

## Install

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. In a scripted install, add Anthropic's official marketplace

Run `claude plugin marketplace add anthropics/claude-plugins-official` before the install below. An interactive Claude Code session registers this marketplace on its first start, so you need the step only where a script — a container launcher, a CI job — installs the plugin before any interactive session has run with that Claude Code configuration: without it, Claude Security, which installs from that marketplace, is left out, and this plugin cannot load.

### 3. Install the plugin

```bash
claude plugin install security-workflows@shipwright
```

Two other plugins arrive with it, because they are **declared dependencies** rather than suggestions:

- **`workflows-core`**, from this marketplace, carries the shared reference corpus the command loads at runtime: the addressing grammar, the specs-repo git entry points, escalation, cost and feedback emission, and the format of the findings register itself.
- **Claude Security** (`claude-security`, from Anthropic's official `claude-plugins-official` marketplace) does every scan and every patch. This plugin never scans by itself: it runs Claude Security's own skill, then records, triages and routes what that skill reports. This marketplace's catalogue allows a dependency on that marketplace, which is what lets Claude Code install a plugin from another marketplace alongside this one.

An unsatisfied dependency disables the plugin instead of letting it half-run, which is the intended behaviour: there is no degraded mode to fall back to.

**What you do not need.** No other family plugin depends on this one, and this one depends on none of `dev-workflows`, `product-workflows` and `docs-workflows`. A scan addressed by a key reads the Epic's `implementation.md`, which `/dev-workflows:implement` writes, and a finding marked fix goes to `/dev-workflows:implement` as a follow-up, so install `dev-workflows` too if you build with the family: that is where the Dev's scan is offered from. A scan of a repository path needs neither.

**What you also need, and it is not a plugin.**

- **`python3` 3.9 or newer on your `PATH`.** Claude Security needs it, and every run but `--triage` stops at setup with `SECURITY_PREREQ_PYTHON` on an older one. The family's own scripts want 3.11: the repo-root [Prerequisites](../../../README.md#prerequisites) give each tool's minimum and the reason for it.
- **Dynamic workflows.** Claude Security runs its scan as a dynamic workflow, through the `Workflow` tool. Turn on the *Dynamic workflows* row in `/config`; on Pro it is off by default. A run that scans stops at setup with `SECURITY_PREREQ_WORKFLOWS` where the tool is not available. `--import` and `--triage` scan nothing, and do not need it.
- **A session on Opus, recommended.** Claude Security's scan agents run on your session model, and nothing inside a running command can change it. On Opus the run asks nothing about it. On Sonnet or below it asks first, recommending that you cancel and rerun after `/model opus`, since the scan may find fewer or weaker issues. On Fable it asks nothing, since you chose Fable, and its confirmation says that Fable's safety filters will re-run some of the scan's requests on Opus. The scan never moves to Fable on its own.
- **`git`, and a code repository with an `origin` remote.** The register is kept per code repository, under the last path segment of `origin`'s URL, and a repository with no `origin` stops with `SECURITY_USAGE`.

## Update

```bash
claude plugin marketplace update shipwright
claude plugin update security-workflows@shipwright
claude plugin update workflows-core@shipwright
claude plugin update dev-workflows@shipwright
```

**Both kinds of step are needed, and the `plugin update` lines are the ones that change what runs.** `marketplace update` refreshes the catalogue, which is what the marketplace advertises, while an already-installed plugin stays at the version you installed. `claude plugin update` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same with a picker. **Update `workflows-core` with it**: the command loads the register's format, the Epic-branch lookup and the cost rules from that plugin, and commits the register on paths only a current `workflows-core` stages. **Update `dev-workflows` with it too**, where you build with the family: a fix goes to `/dev-workflows:implement`, and only its 4.28.0 or later continues on the Epic's branch and starts from the scan's patch — an older one cuts a fresh branch, so the fix lands in a second pull request.

## What you set on your machine

This plugin reads one environment variable, and every run needs it. [Environment](reference/environment.md) has its exact resolution and failure behaviour.

### `SPECS_PATH`

The shared, team-visible specs repository. The findings register lives in it, one per code repository under `security/<repo-slug>/`, and it is the one place a run commits its session bookkeeping. Set it to the root of your dedicated specs clone, the directory that holds `specifications/`, never to `specifications/` itself. Where it is unset, or names no existing directory, the run stops before it resolves anything, naming the variable and offering to set it or cancel. A run addressed by a key also resolves the Epic's or PRD's folder under it, and appends its unit note there.

**What the plugin does not read.** It has no `REPOS_PATH`. A run addressed by a key scans the code repository this session is open in, and a run addressed by a path scans that path's repository.

### Claude Code's skill-listing budget

Set it once, whichever plugins you install: the repo-root [installation step](../../../README.md#4-raise-claude-codes-skill-listing-budget) says how, and how to check that it is enough. `/security-workflows:scan` is typed-only (`disable-model-invocation: true`), so it takes no room in the list of skills the model picks from, and asking in prose does not start it: type the command. Claude Security's own skill is model-invocable, so it does take room.

## Where it sits in the delivery

The command runs at two moments, by two roles ([Roles and phases](roles-and-phases.md)):

```
Dev, one Epic, on its branch, before the merge:
  /dev-workflows:implement <EPIC>       the code is committed on the Epic's branch; implementation.md records repo, branch, commit
  /dev-workflows:conformance <EPIC>     a fix-code decision  -> /dev-workflows:implement <EPIC>, on the Epic's branch
  /security-workflows:scan <EPIC>       a fix decision       -> /dev-workflows:implement <EPIC>, on the Epic's branch
  the pull request is reviewed and merged

After the merge:
  /dev-workflows:conformance <PRD>                       the PE, once every Epic has merged
  /security-workflows:scan <repo-path> --verify-fixes    the Security Engineer: closes the fixes on evidence
  /security-workflows:scan <repo-path> --triage          the Security Engineer: reviews what awaits review, whenever
```

**Before the merge the scan is the Dev's.** `/dev-workflows:implement` offers `/dev-workflows:conformance` and then the scan, and `/dev-workflows:conformance` offers the scan where it decided no fix, for each repository whose Epic branch it traced before the merge. Each is offered, never run for you. A finding you mark fix comes back to `/dev-workflows:implement`, which continues on the Epic's branch, so the fix joins the open pull request. **After the merge the Security Engineer closes and reviews.** `--verify-fixes` closes a fix once a scan that covers its changed file no longer reports it, and `--triage` reviews the Dev's decisions whenever the Security Engineer gets to it. Nothing the Dev does waits for either.

**Claude Security's own tip.** After a `git push` or a `gh pr create`, Claude Security suggests a scan of the branch's changes. A report you make that way, by running `/claude-security` yourself, is recorded with `--import`, without paying for the scan twice: `/security-workflows:scan <KEY | repo-path> --import <report dir>`.

## Where it reads and writes

The command reasons about source code. It never runs anything against a deployed system, never writes exploit code, and never applies a patch.

In the code repository it writes only what a scan needs: the report directory Claude Security leaves at the scan root (or in the session's working directory, where the session is open in a subdirectory of it), `CLAUDE-SECURITY-<timestamp>/`, which carries its own `.gitignore`; on a change scan, a fast-forward or a switch to the Epic's branch, the switch only after you agree to it; for `--verify-fixes`, a temporary worktree it removes on every path; and a report folder copied out of a temporary worktree to the repository's root, where the run did not record that report, or where you chose to remove an idle worktree a crashed run left, so that `--import` can record it. Everything it records goes to `$SPECS_PATH`. Its maintenance agents write nothing on their own there: an edit they propose, to a documentation page or a `CLAUDE.md`, is applied only where you accept it, and left uncommitted; a knowledge-base entry goes under your `~/.claude/memory/` ([Where the command writes](workflow.md#where-the-command-writes)).

**A credential in a report can reach the specs repository.** Claude Security's redaction of credential values in its report is best effort, and the run asks before copying a report where Claude Security says the redaction may have failed. A credential it misses without saying so is copied into the register, then committed and pushed with the run's session files, as bookkeeping that no pull request reviews; once pushed, only a history rewrite takes it out. Keep the specs repository private, with access no wider than the code repository's, and rotate any credential you find in a scan folder. [`/security-workflows:scan`](commands/scan.md#triage) says which files to read, and when.

## Your first run

Run it from the code repository the Epic was implemented in, once `/dev-workflows:implement` and `/dev-workflows:conformance` are done:

```
/security-workflows:scan ACME-7-01
```

Here is what to expect. The run resolves the Epic's folder and runs the specs-repo preflight. It takes the repository this session is open in, fetches it, and finds the Epic's branch from the latest block for this repository in the Epic's `implementation.md`. It reserves the finding numbers that run records on other session branches of the specs repository have taken, offers to remove a temporary worktree that a crashed run left, and checks `python3`, the `Workflow` tool and your session model. Where you stand on the Epic's branch with a clean tree, it scans the branch's tip in place; where the branch is elsewhere, it asks to switch. One confirmation states what it will scan and at which effort, `high` for a change scan, and that the scan may take a while and use a significant number of tokens. Then Claude Security scans the branch's changes against its base.

The run copies the report into the register, shows every finding in one triage table, and asks Claude Security for patches for the ones you mark fix. It records the run, prints its report, and only then writes each fix as a follow-up for `/dev-workflows:implement`, after showing you the lines first.

A whole repository is the Security Engineer's: `/security-workflows:scan /workspace/acme-api` scans it at `medium`, and Claude Security's own scope question lets you narrow it. [`/security-workflows:scan`](commands/scan.md) has every mode, question and stop, and the [documentation index](README.md) links every page.

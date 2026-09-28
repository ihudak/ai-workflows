# Environment reference

[Getting started](../getting-started.md) says what each variable is *for* and what to export before your first use of this plugin. This page says what each variable **is** — its default, what happens when it is unset, and what happens when it points somewhere unreadable. The plugin reads eight user-settable variables. The rest of the names its own inventory check encounters while scanning for `$VAR` reads are never user-settable and stay out of scope here: `CLAUDE_PLUGIN_ROOT` and `ARGUMENTS` are runtime plumbing Claude Code itself sets for every plugin invocation, and `OSTYPE`, `BASH_SOURCE`, `BASH_REMATCH`, `ROOT` and `OWNER_REPO` are shell built-ins or internal template names, not plugin configuration.

Every one of the eight is read by a reference this plugin ships — the corpus is where the reads live, and the corpus is here — and for seven of the eight that is the only read anywhere in this plugin. `$SPECS_PATH` is the exception: `/frames` Phase 0 step 0 gates on it in the command's own body and stops the run on an unset one. Where any of this plugin's other commands names the variable, it is as the scope of the shared entry points they cite, which do the reading. The set is the union of what any downstream plugin needs, plus the price-table override and the three run-flag defaults that `workflows-core:run-flags` owns: `docs-workflows` reads all four of the others (`$GIT_USER_INITIALS` included, since it branches a docs repository); `dev-workflows` reads three of the four — it grounds nothing in documentation, so `$DOCS_PATH` is not among the variables its own commands or references read — `dev-workflows:code-handoff` names it only to say it never touches it — while `$GIT_USER_INITIALS` is, since it branches a code repository; `product-workflows` reads three of the four as well — it never creates a branch in a code or docs repo, so `$GIT_USER_INITIALS` is not among the variables its own commands or references touch.

## `$SPECS_PATH`

- **`$SPECS_PATH`** — the shared, team-visible store the whole family writes its artifacts and bookkeeping into. It is the one write root with no default: nothing is guessed.

**Resolution.** Used verbatim as a directory path. `specs-repo-git.md`'s preflight and terminal commit run every git call as `git -C "$SPECS_PATH"` and never change the working directory.

**When unset.** Cost, feedback and follow-up entries fall through to their report-only tier — the run says what it would have written and writes nothing. Nothing is ever written into the current working directory instead, since it may be a code repository. **`/frames` does not degrade — it stops.** *"Every path this command reads or writes is under it"*, so its Phase 0 step 0 applies `escalation-rules.md`'s *Required path environment variable unset* rule and refuses the run — `choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`, with no "continue without it".

**When it points somewhere unreadable or unwritable.** The same degradation, reported rather than fatal.

## `$REPOS_PATH`

- **`$REPOS_PATH`** — where your code clones live; one directory, or a colon-separated list. Defaults to `/workspace`.

**Resolution.** The **command** resolves a repository under it and hands the agent an absolute `repo_path` — no agent reads `$REPOS_PATH` itself. The match is by `git remote get-url origin` slug where the command was handed the slug; where it lists candidates to offer you instead, your answer is resolved against that listing rather than matched against a directory name, so a rename changes the name a clone is offered under, never whether it is offered.

**When unset.** The default applies. A repository that is simply not mounted is reported as unresolvable rather than guessed at.

**When it points somewhere unreadable.** The scan reports the miss; `read-only-repos.md` covers the narrower case of a mount that is readable but not writable, which is scanned at a pinned ref rather than refused.

## `$DOCS_PATH`

- **`$DOCS_PATH`** — your shipped product documentation's clone, **read-only** in its role as a docs-grounding root — the role this plugin's `docs-grounding.md` and `docs-grounder` give it. Defaults to `/workspace/docs`. (`docs-workflows`' docs commands also use it as a write target for a docs repository — a different role, not a contradiction.)

**Resolution.** `docs-grounding.md` gates on it being a readable directory holding at least one markdown file; `docs-grounder` reads it and never writes to it.

**When unset.** The default is tried, and every miss — unset, missing, or no markdown found — is a silent, non-blocking skip. Grounding is advisory, never a gate.

**When it points somewhere unreadable.** The same silent skip.

## `$GIT_USER_INITIALS`

- **`$GIT_USER_INITIALS`** — your branch identity string; no default, and nothing fails when it is absent.

**Resolution.** It is rung 1 of the identity ladder `branch-naming.md` applies wherever a command creates a git branch. The rungs run in order, stopping at the first non-empty result: this variable, then `git config user.initials`, then inference from existing branch names, then a prompt.

**When unset.** The ladder falls through — there is no error, only degradation to a less certain source. Where the target repo's documented convention has no name-or-initials segment, the variable is simply unused for that repo.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal string, not a path.

## `$DEV_WORKFLOWS_COST_PRICES`

- **`$DEV_WORKFLOWS_COST_PRICES`** — optional override path for the token-price table session-cost reporting prices against; this plugin ships its own default table, so setting it is never required.

**Resolution.** First-found-wins, three tiers: `$DEV_WORKFLOWS_COST_PRICES` (a path) → a repo-local `cost-prices.yaml` → the bundled `${CLAUDE_PLUGIN_ROOT}/references/cost-prices.yaml`. Whichever file resolves must carry a top-level `models:` map keyed by model id — a file missing that wrapper, override or default, prices every model as `cost_usd: null` rather than raising an error.

**When unset.** Resolution falls straight through to the repo-local file, then the bundled default. This is the variable of the eight most users never touch.

**When it points somewhere unreadable.** Treated the same as "not set at this tier" — resolution continues down the same chain rather than failing the run.

**Its name keeps the `DEV_WORKFLOWS_` prefix deliberately.** The variable predates this plugin, and renaming it would silently ignore every setting already exported on a working machine. See [Session cost](session-cost.md) for what the table prices.

## `$WORKFLOWS_SKIP_COSTS`

- **`$WORKFLOWS_SKIP_COSTS`** — the persistent default for the `--skip-costs` run flag; a command it applies to still computes and advances the session-cost checkpoint, but never writes a cost entry into `$SPECS_PATH`.

**Resolution.** Read as a boolean: `1`, `true` or `yes`, matched case-insensitively, is on; any other value, and an unset variable, is off. A `--skip-costs` flag on the command line always overrides it. `run-flags.md` §1 is the single source of truth for the flag/env precedence and boolean grammar shared by all three run flags.

**When unset.** Off — the command's cost phase runs exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

## `$WORKFLOWS_SKIP_FEEDBACK`

- **`$WORKFLOWS_SKIP_FEEDBACK`** — the persistent default for the `--skip-feedback` run flag; narrows a command's maintenance phase to bug capture only (`run-flags.md` §4).

**Resolution.** Same boolean grammar as `$WORKFLOWS_SKIP_COSTS` above, read by `run-flags.md` §1; a `--skip-feedback` flag on the command line always overrides it.

**When unset.** Off — the maintenance phase dispatches `impl-maintenance` exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

## `$WORKFLOWS_ENFORCE_MODEL`

- **`$WORKFLOWS_ENFORCE_MODEL`** — the persistent default for the `--enforce-model` run flag; pins every subagent a command dispatches to one model, bypassing model-routing's own per-step selection.

**Resolution.** An alias, a full model id, or `routing`; resolved against `run-flags.md` §2's alias table and reachability check. Unset, or set to `routing`, means no enforcement. An `--enforce-model=<value>` flag on the command line always overrides it.

**When unset.** No enforcement — model routing selects each step's model exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

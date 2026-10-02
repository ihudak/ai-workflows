# Environment reference

[Getting started](../getting-started.md) says what each variable is *for* and what to export before your first use of this plugin. This page says what each variable **is** — its default, what happens when it is unset, and what happens when it points somewhere unreadable. The plugin reads eight user-settable variables. The rest of the names its own inventory check encounters while scanning for `$VAR` reads are never user-settable and stay out of scope here: `CLAUDE_PLUGIN_ROOT` and `ARGUMENTS` are runtime plumbing Claude Code itself sets for every plugin invocation, and `OSTYPE`, `BASH_SOURCE`, `BASH_REMATCH`, `ROOT` and `OWNER_REPO` are shell built-ins or internal template names, not plugin configuration.

Every one of the eight is read by a reference this plugin ships — the corpus is where the reads live, and the corpus is here — and for seven of the eight that is the only read anywhere in this plugin. `$SPECS_PATH` is the exception: `/frames` Phase 0 step 0 gates on it in the command's own body and stops the run on an unset one. Where any of this plugin's other commands names the variable, it is as the scope of the shared entry points they cite, which do the reading. The set is the union of what any downstream plugin needs, plus the price-table override and the three run-flag defaults that `workflows-core:run-flags` owns: `docs-workflows` reads all four of the others (`$GIT_USER_INITIALS` included, since it branches a docs repository); `dev-workflows` reads three of the four — it grounds nothing in documentation, so `$DOCS_PATH` is not among the variables its own commands or references read — `dev-workflows:code-handoff` names it only to say it never touches it — while `$GIT_USER_INITIALS` is, since it branches a code repository; `product-workflows` reads three of the four as well — it never creates a branch in a code or docs repo, so `$GIT_USER_INITIALS` is not among the variables its own commands or references touch.

## `$SPECS_PATH`

- **`$SPECS_PATH`** — the shared, team-visible store the whole family writes its artifacts and bookkeeping into. It is the one write root with no default: nothing is guessed.

**Resolution.** Used verbatim as a directory path. `specs-repo-git.md`'s preflight and terminal commit run every git call as `git -C "$SPECS_PATH"` and never change the working directory.

**When unset.** Cost, feedback and follow-up entries fall through to their report-only tier — the run says what it would have written and writes nothing. Nothing is ever written into the current working directory instead, since it may be a code repository. **`/frames` does not degrade — it stops.** *"Every path this command reads or writes is under it"*, so its Phase 0 step 0 applies `escalation-rules.md`'s *Required path environment variable unset* rule and refuses the run — `choices: ["Set SPECS_PATH (enter the path)", "Cancel"]`, with no "continue without it".

**When it points somewhere unreadable or unwritable.** The same degradation, never fatal. A `.git` that resolves but is not writable is a read-only specs mount, a normal state, and degrades silently. A path that is not a directory, or not a git repository at all, is never supported, so `specs-preflight` reports it in a notice, one line naming the variable and the path (`specs-repo-git.md` §3.1). Where that path is a `specifications/` directory mounted on its own, the line also names which of the two signals in the next paragraph it matches, and the notice adds the stop's second line where it has one.

**When it points inside the specs tree.** `$SPECS_PATH` is the root of a dedicated specs repository, the directory that holds `specifications/`. It is never `specifications/` itself, nor a folder inside it. **Two layouts are unsupported, each for its own reason.** The first is **a specs tree inside a larger repository**, because the plugin switches branches and commits in the repository `$SPECS_PATH` belongs to, which there would move the checkout of everything else that repository holds. The second is given below. A `$SPECS_PATH` below its repository's top level that the check below does not stop draws a `specs-preflight` notice naming the top level, and the run goes on. Where `$SPECS_PATH` is set, `resolve-address` first tests, for every command that resolves an address, `/frames` among them, two signals (`workflows-core:addressing` §3, `specs-root-check`), on a `<KEY>` and an `@<path>` address alike: `$SPECS_PATH` is, or is inside, a `specifications/` directory rather than a repository root, or it is, or directly holds, a specs folder — one whose artifacts assert a `key:` and a folder kind and whose name begins with that kind and key (for `$SPECS_PATH` itself, its physical name; a subfolder that is a link back into its own `specifications/` is skipped), so a root's templates, `README.md` or `docs/` never count, fresh or populated. What neither signal sees is a `$SPECS_PATH` outside any repository's top-level `specifications/` that is, or holds only, folders not named `<KIND>-<key>-`, such as a mount of a legacy unprefixed folder. Either one stops the run with `SPECS_PATH_INSIDE_TREE` where it resolves its address, naming the variable, its value, the signal and the value to set: the directory that physically holds that `specifications/`, symlinks resolved, where it lies in the same git work tree, and otherwise *the directory that holds `specifications/`*. Where that directory is not its repository's top level, the stop adds that the layout is unsupported. It stops before any folder is searched or created, since every key would otherwise resolve to nothing and a creating command would create its folder at `specifications/specifications/…`. An `@<path>` address is tested too, because a run that passed its own resolution on one would otherwise meet the same stop at a later lookup by key, of an ARD or a specification, after its expensive work. **An earlier run's damage is caught too.** Where `$SPECS_PATH` is the `specifications/` directory directly under a repository root or anything inside it, or is itself a specs folder, or holds specs folders directly, the run stops whether or not a nested `specifications/` exists. Where one does, or where misrooted runs left bookkeeping under `$SPECS_PATH`, the stop adds one more line naming each and where it belongs. Feedback and pending cost under `dev-workflows-feedback/` and `dev-workflows-cost/` there are never committed. A `documentation/<slug>/dev-workflows/` there, and the bookkeeping and any `implementation.md` in a nested `specifications/`, are not committed while the variable stays wrong, but the first run after it is fixed commits them in the wrong place unless they are moved first. A nested `specifications/` left in place is also searched for keys once the variable is fixed, so a key whose folder only it holds resolves there. The line says which. Move them yourself, commit the move, then re-run: the plugin moves nothing and gives no commands. A run that resolves no address is not stopped: `specs-preflight` tests the same signals at run start, on an ordinary checkout as well as on a mount, and prints a notice naming the variable, its value, the signal and the value to set, with every addition the stop would make, then runs on. Both a stopped and a noticed run carry `specs_git: misrooted`: cost, feedback and follow-ups stay in the printed output, no `resume.md` is written, and the specs-repository steps commit nothing, hand nothing off and switch no branch. The preflight still fetches, and names any branch it stayed on where it would otherwise have switched. **A stopped run writes nothing under `$SPECS_PATH`.** A noticed run that goes on writes what the command itself writes — its deliverable, and any draft or record it keeps beside it, such as `implementation.md` — where the command puts it, and leaves it there uncommitted. That bound is the specs-repository steps' alone. A command that changes code or documentation still branches and commits in the repository it changed, and where that repository also holds the specs tree, its branch moves the specs checkout too, which is one more reason that layout is unsupported. Where `$SPECS_PATH` names the right directory — a repository's top level, or a directory in a repository holding `specifications/` (`workflows-core:addressing` §3 states the exact condition) — but holds stray specs folders beside `specifications/`, the stop says so, names every stray folder and `specifications/` as where they belong, and adds the unsupported-layout clause where that directory is below its repository's top level. Where nothing on disk says whether `$SPECS_PATH` is a specs root or a specs tree under another name — a path that is no repository, or one below its repository's top level holding no `specifications/` — the stop states both readings and what each needs, and you choose. Under the first, the folders belong in a directory named `specifications/`, and the stop names that directory and sets `SPECS_PATH` to its parent. There is no option to enter a path for the one run: fix the variable where it is set. A specs repository nothing has been written into yet matches neither signal and runs as before. **The second unsupported layout is a specs root that is itself a subdirectory named `specifications`**, holding its tree at `specifications/specifications/`. Its reason is detection rather than git: it cannot be told from that damage, so it stops on every run. Set `SPECS_PATH` to the repository root and move the tree up a level, as the stop says.

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

- **`$WORKFLOWS_SKIP_COSTS`** — the persistent default for the `--skip-costs` run flag; a command it applies to still advances the session-cost checkpoint (pricing nothing), but never writes a cost entry into `$SPECS_PATH`.

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

**Resolution.** An alias, a full model id, or `routing`; resolved against `run-flags.md` §2's alias table and reachability check. Unset, set but empty, or set to `routing` (matched case-insensitively, as the aliases are) means no enforcement. An `--enforce-model=<value>` flag on the command line always overrides it. Where the agent tool's `model` parameter accepts only family names (`opus`, `sonnet`, `haiku`, `fable`), as Claude Code's does today, a family alias enforces that family and the harness picks its version, and a version-specific value (`opus5.5`, `claude-opus-5-5`) is honoured only when it is its family's newest row (in `references/model-routing/classification.md`'s chain, or for Haiku in `run-flags.md` §2's Haiku rows), and is then passed as the family name, so `opus5.5` runs on whatever Opus the harness selects — while any other version-specific value (an older row such as `opus5`, an id on no chain, or a Fable id) stops `RUN_FLAGS_MODEL_UNAVAILABLE` with a message suggesting the bare family (`run-flags.md` §2).

**When the value is bad.** On a run whose command line gives no `--enforce-model` of its own, a value matching none of `run-flags.md` §2's forms stops every command `--enforce-model` applies to with `RUN_FLAGS_BAD_MODEL`, and a value that resolves to an unreachable model stops it with `RUN_FLAGS_MODEL_UNAVAILABLE` — both before any write, when the run flags are stripped, each message tagging the value `(from WORKFLOWS_ENFORCE_MODEL)` so the environment, not the command line, is the thing to fix. A command it does not apply to (`run-flags.md` §3 step 3) ignores it silently, bad value or not.

**When unset.** No enforcement — model routing selects each step's model exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

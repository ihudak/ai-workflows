# Environment reference

[Getting started](../getting-started.md) says what each variable is *for* and what to export before your first use of this plugin. This page says what each variable **is** — its default, what happens when it is unset, and what happens when it points somewhere unreadable. The plugin reads nine user-settable variables.

The nine are what the whole family needs: each is read by a reference this plugin ships, inside whichever plugin's command is running, and `/frames` also checks `$SPECS_PATH` itself and stops on an unset one. Four of the nine are the price-table override and the three run-flag defaults; of the other five, the sibling plugins' own commands use these:

- `dev-workflows` uses `$SPECS_PATH`, `$REPOS_PATH`, `$GIT_USER_INITIALS`, since it branches a code repository, and `$ARCHITECTURE_REPO_PATH`, through `/design`'s architecture grounding — not `$DOCS_PATH`, since it grounds nothing in documentation.
- `product-workflows` uses `$SPECS_PATH`, `$REPOS_PATH`, `$DOCS_PATH` and `$ARCHITECTURE_REPO_PATH`, through `/create-ard`, `/specify`, `/update-spec` and `/promote-decisions`, and `$GIT_USER_INITIALS`, since `/promote-decisions` branches the architecture repository.
- `docs-workflows` uses `$SPECS_PATH`, `$REPOS_PATH`, `$DOCS_PATH` and `$GIT_USER_INITIALS`, since it branches a docs repository — not `$ARCHITECTURE_REPO_PATH`, since it authors no ARD.
- `security-workflows` uses `$SPECS_PATH` alone of its own.

All four, and this plugin's own commands that commit session files, also read `$GIT_USER_INITIALS` to name your session branch where your specs repository is in session-branch mode (*Session branch*, under `$GIT_USER_INITIALS` below) — `security-workflows` there and nowhere else.

## `$SPECS_PATH`

- **`$SPECS_PATH`** — the shared, team-visible store the whole family writes its artifacts and bookkeeping into. It is the one write root with no default: nothing is guessed.

**Resolution.** Used verbatim as a directory path. The specs-repository preflight and the terminal commit run every git call as `git -C "$SPECS_PATH"` and never change the working directory.

**When unset.** Cost, feedback and follow-up entries fall through to their report-only tier — the run says what it would have written and writes nothing. Nothing is ever written into the current working directory instead, since it may be a code repository. **`/frames` does not degrade — it stops.** *"Every path this command reads or writes is under it"*, so before it reads the address it stops and asks you to choose *Set SPECS_PATH*, which then asks for the path and uses it for the rest of the run, or *Cancel*, which ends the run — there is no option to continue without it.

**When it points somewhere unreadable or unwritable.** The same degradation, never fatal. A `.git` that resolves but is not writable is a read-only specs mount, a normal state, and degrades silently. A path that is not a directory, or not a git repository at all, is never supported, so `specs-preflight` reports it in a notice, one line naming the variable and the path. Where that path is a `specifications/` directory mounted on its own, the line also names which of the two signals under *When it points inside the specs tree* below it matches, and the notice adds the stop's second line where it has one.

**When it points inside the specs tree.** `$SPECS_PATH` must name the root of a dedicated specs repository — the directory that holds `specifications/` — never `specifications/` itself, nor a folder inside it. Two layouts are unsupported: a specs tree inside a larger repository, and a specs root that is itself a subdirectory named `specifications`. Pointed inside the tree, a run that resolves an address stops with `SPECS_PATH_INSIDE_TREE`, and any other run prints a `specs-preflight` notice and goes on — save on a checkout whose `.git` is read-only, where the preflight does nothing and prints none; a specs tree inside a larger repository draws a notice too, and either way the run commits nothing to the specs repository. To fix it, point `SPECS_PATH` at the root of a dedicated specs repository where the variable is set — the stop names the value to set, or the folders to move — and re-run.

- **A specs tree inside a larger repository** is unsupported because the plugin switches branches and commits in the repository `$SPECS_PATH` belongs to, which there would move the checkout of everything else that repository holds. A `$SPECS_PATH` below its repository's top level that the inside-tree check (below) does not stop draws a `specs-preflight` notice naming the top level, and the run goes on, treated as misplaced (below).
- **A specs root that is itself a subdirectory named `specifications`**, holding its tree at `specifications/specifications/`, is unsupported for detection rather than git: it cannot be told from the damage a misrooted run leaves (below), so it stops on every run. Set `SPECS_PATH` to the repository root and move the tree up a level, as the stop says.
- **The check.** Where `$SPECS_PATH` is set, `resolve-address` first tests, for every command that resolves an address, `/frames` among them, two signals, on a `<KEY>` and an `@<path>` address alike. An `@<path>` address is tested too, because a run that passed its own resolution on one would otherwise meet the same stop at a later lookup by key, of an ARD or a specification, after its expensive work.
- **The two signals.** `$SPECS_PATH` is, or is inside, a `specifications/` directory rather than a repository root; or it is, or directly holds, a specs folder — one whose artifacts assert a `key:` and a folder kind and whose name begins with that kind and key (for `$SPECS_PATH` itself, its physical name; a subfolder that is a link back into its own `specifications/` is skipped). So a root's templates, `README.md` or `docs/` never count, fresh or populated, and a specs repository nothing has been written into yet matches neither signal and is not stopped.
- **What neither signal sees** is a `$SPECS_PATH` outside any repository's top-level `specifications/` that is, or holds only, folders not named `<KIND>-<key>-`, such as a mount of a legacy unprefixed folder.
- **The stop.** Either signal stops the run with `SPECS_PATH_INSIDE_TREE` where it resolves its address, naming the variable, its value, the signal and the value to set: the directory that physically holds that `specifications/`, symlinks resolved, where it lies in the same git work tree, and otherwise *the directory that holds `specifications/`*. Where that directory is not its repository's top level, the stop adds that the layout is unsupported. It stops before any folder is searched or created, since every key would otherwise resolve to nothing and a creating command would create its folder at `specifications/specifications/…`. There is no option to enter a path for the one run: fix the variable where it is set.
- **Stray specs folders.** Where `$SPECS_PATH` names the right directory — a repository's top level, or a directory in a repository holding `specifications/` — but holds stray specs folders beside `specifications/`, the stop says so, names every stray folder and `specifications/` as where they belong, and adds the unsupported-layout clause where that directory is below its repository's top level.
- **When nothing on disk can tell.** Where nothing on disk says whether `$SPECS_PATH` is a specs root or a specs tree under another name — a path that is no repository, or one below its repository's top level holding no `specifications/` — the stop states both readings and what each needs, and you choose. Under the specs-tree reading, the folders belong in a directory named `specifications/`, and the stop names that directory and tells you to set `SPECS_PATH` to its parent.
- **Damage an earlier run left.** Where `$SPECS_PATH` is the `specifications/` directory directly under a repository root or anything inside it, or is itself a specs folder, or holds specs folders directly, the run stops whether or not a nested `specifications/` exists. Where one does, or where misrooted runs left bookkeeping under `$SPECS_PATH`, the stop adds one more line naming each, where it belongs, and which of these applies to it. Move them yourself, commit the move, then re-run: the plugin moves nothing and gives no commands.
  - Feedback and pending cost under `dev-workflows-feedback/` and `dev-workflows-cost/` there are never committed.
  - A `documentation/<slug>/dev-workflows/` there, and the bookkeeping and any `implementation.md` in a nested `specifications/`, are not committed while the variable stays wrong, but the first run after it is fixed commits them in the wrong place unless they are moved first.
  - A nested `specifications/` left in place is also searched for keys once the variable is fixed, so a key whose folder only it holds resolves there.
- **A run that resolves no address** is not stopped: `specs-preflight` tests the same signals at run start — on a checkout whose `.git` is writable, and on a path that is not a git repository at all, such as a `specifications/` directory mounted on its own — and prints a notice naming the variable, its value, the signal and the value to set, with every addition the stop would make, then runs on. On a checkout whose `.git` is read-only the preflight does nothing, so no notice is printed there. A command that runs its preflight before it resolves its address — `/product-workflows:idea`, and `/dev-workflows:vuln` on an address — prints that notice first and then stops, both naming the same cause.
- **What a stopped or noticed run does.** A stopped run and a noticed one alike — the notice for a specs tree inside a larger repository included — treat `$SPECS_PATH` as misplaced for the rest of the run: cost, feedback and follow-ups stay in the printed output, no `resume.md` is written, and the specs-repository steps commit nothing, hand nothing off and switch no branch. Where `$SPECS_PATH` is a git repository with a writable `.git`, the preflight still fetches, and names any branch it stayed on where it would otherwise have switched. A stopped run writes nothing under `$SPECS_PATH`. A noticed run that goes on writes what the command itself writes — its deliverable, and any draft or record it keeps beside it, such as `implementation.md` — where the command puts it, and leaves it there uncommitted. That bound is the specs-repository steps' alone: a command that changes code or documentation still branches and commits in the repository it changed, and where that repository also holds the specs tree, its branch moves the specs checkout too, which is one more reason that layout is unsupported.

**When it changes under a resumed conversation.** Each run of `specs-preflight` first prints one line, `Environment: SPECS_PATH=<real path> (origin <url|none>), REPOS_PATH=<value|unset>`, and the conversation carries it wherever it is resumed. Before the run hands its deliverable off, and before each write of its tail — feedback, cost, follow-ups, `resume.md` — the run compares the environment it now stands in with that line, and once more at its terminal commit where the record the run's start made stands — the file that start keeps under `~/.claude/dev-workflows/specs-git/`, which a run whose session id changed before its end does not find — comparing there only `$SPECS_PATH`'s real path and its `origin`, the one check a run that hands nothing off and writes nothing in its tail meets. Where they differ — a conversation resumed in another container, with `claude --resume` or a continuation — it prints `Environment changed: …` once, naming both, and from there commits, hands off and records nothing more in the specs repository, without asking, as it does for a misplaced `$SPECS_PATH`: its bookkeeping stays in the printed output, and what it already wrote stays where it is. Re-run in the container the run started in. A deliverable a command writes before its handoff is not covered — it lands where `$SPECS_PATH` names at that moment — save on the two commands whose session file records the environment, `/dev-workflows:design` and `/product-workflows:specify`, which compare before that write too.

### A specs repository whose default branch takes no push

Where your specs repository protects its default branch, the plugin cannot push the session files it commits there — feedback, cost, follow-ups, the implementation record, the resume pointer and the security register. The first push the server refuses switches that clone to **session-branch mode**; you can switch it on in advance with `git -C "$SPECS_PATH" config workflows.sessionBranch true` — on the host, where your container mounts `.git/config` read-only, since the write fails there. In the mode, those files go to a branch of your own, `session/<identity>` — your identity from `$GIT_USER_INITIALS`, `git config user.initials` or the prefix your branches already share (see `$GIT_USER_INITIALS` below) — which the plugin keeps merged with the default branch and pushes; merge its pull request to land them. A run that finds no `session/<identity>` in your clone, the first in the mode among them, creates it there and says so: in its `Specs preflight:` line where the preflight's flush created it, and otherwise in its `Specs repo:` line. The run's `Specs repo:` line gives the `gh pr create` command that opens it.

Until that pull request merges, your specs checkout shows those files as modified or untracked: that is where every command reads and appends them. A file you remove (`rm`, `git clean`, `git stash -u`) or restore to its committed version is simply put back at the next run — save a pending cost file under `dev-workflows-cost/`, whose removal reads as its relocation and leaves your session branch. An entry only your session branch holds cannot be removed or rewritten by hand until that pull request merges: the next run puts it back, beside your edit. If git refuses a switch or a pull you make by hand because of them, run `python3 ~/.claude/plugins/cache/<marketplace>/workflows-core/<version>/scripts/session-branch.py --specs "$SPECS_PATH" lift --branch session/<identity>` first, and the same with `put-back --branch session/<identity> --default-ref origin/<default>` after; the next plugin run puts them back on its own too. Where `lift` prints a non-empty `unpreserved` list, it has changed nothing: those files hold entries not yet on your session branch, so run any plugin command first, which commits them, then lift — save a file the run's `Specs repo:` line says holds a change your session branch's version lacks, or the other way round: no run commits that file until your copy is the branch's version, which `git -C "$SPECS_PATH" show session/<identity>:<path>` shows, with your own entries added after it, in the line endings your checkout gives the file; an edit or removal of an entry the branch your specs checkout stands on holds can then be made again. Once that pull request has merged, you can leave the mode: `git -C "$SPECS_PATH" config --unset workflows.sessionBranch`, and remove the push-refusal record: `(cd "$SPECS_PATH" && rm -f "$(git rev-parse --git-common-dir)/workflows/push-refused/<default>")`, and `git -C "$SPECS_PATH" config --unset branch.<default>.workflowsPushRefused`, where the record is that configuration key instead — on a clone whose record an older release of this plugin wrote, or where the file could not be written. The record is a file because some containers mount `.git/config` read-only; there, also run the `config --unset` on the host. In such a container every `git push -u` the commands run ends with `error: could not write config file` (or `could not lock config file`), sometimes after git has said the branch is "set up to track": the branch **is** pushed, and only its upstream is not recorded, which no command needs. If your identity changes (you set `GIT_USER_INITIALS` later), the next run starts a second session branch that carries everything the first one held; close the first one's pull request once the second one's has merged.

## `$REPOS_PATH`

- **`$REPOS_PATH`** — where your code clones live; one directory, or a colon-separated list. Defaults to `/workspace`.

**Resolution.** The **command** resolves a repository under it and hands the agent the repository's absolute path — no agent reads `$REPOS_PATH` itself. The match is by `git remote get-url origin` slug where the command was handed the slug; where it lists candidates to offer you instead, your answer is resolved against that listing rather than matched against a directory name, so a rename changes the name a clone is offered under, never whether it is offered.

**When unset.** The default applies. A repository that is simply not mounted is reported as unresolvable rather than guessed at.

**When it points somewhere unreadable.** The scan reports the miss; a mount that is readable but not writable is a narrower case and is scanned at a pinned ref rather than refused.

## `$DOCS_PATH`

- **`$DOCS_PATH`** — your shipped product documentation's clone, **read-only** in its role as a docs-grounding root — the role this plugin's docs grounding and `docs-grounder` give it. Defaults to `/workspace/docs`. (`docs-workflows`' docs commands also use it as a write target for a docs repository — a different role, not a contradiction.)

**Resolution.** Docs grounding gates on it being a readable directory holding at least one markdown file; `docs-grounder` reads it and never writes to it.

**When unset.** The default is tried, and every miss — unset, missing, or no markdown found — is a silent, non-blocking skip. Grounding is advisory, never a gate.

**When it points somewhere unreadable.** The same silent skip.

## `$ARCHITECTURE_REPO_PATH`

- **`$ARCHITECTURE_REPO_PATH`** — a local clone of your organisation's architecture repository (technology radar, standards, principles, patterns, ADRs). No default.

**Resolution.** `--no-arch` forces architecture grounding off; otherwise the variable when set. A validity gate then has to pass: a readable directory holding a catalog (`index.yaml`, `index.json`, `catalog.yaml`), a radar file (`radar.{yaml,yml,json,csv}` at the root or under `radar/`), or an ADR folder with a markdown file. Nothing scans for a clone — no repository name is common enough to search for.

**When unset.** Architecture grounding is `OFF` with a line naming this variable, and the run proceeds exactly as without it; the team knowledge base under `$SPECS_PATH/architecture/` is resolved separately, and still read where it exists.

**When it points somewhere invalid.** `OFF` with a reason naming the variable and what failed — never an error, never a gate or reviewer finding.

**Directory layout.** The layouts `architecture-grounder` recognises — catalog, radar, decision, standards, principles, patterns and reference-architecture folders — are listed in that agent. Grounding never writes, fetches, pulls or switches the clone — only `/product-workflows:promote-decisions` writes an architecture repository, on a branch of its own; `/product-workflows:create-ard`, `/product-workflows:specify`, `/product-workflows:update-spec` and `/dev-workflows:design` report its branch, commit, date, uncommitted changes and staleness instead.

## `$GIT_USER_INITIALS`

- **`$GIT_USER_INITIALS`** — your branch identity string; no default, and nothing fails when it is absent.

**Resolution.** It is rung 1 of the identity ladder every command applies wherever it creates a git branch. The rungs run in order, stopping at the first non-empty result: this variable, then `git config user.initials`, then inference from existing branch names, then a prompt.

**When unset.** The ladder falls through — there is no error, only degradation to a less certain source. Where the target repo's documented convention has no name-or-initials segment, the variable is simply unused for that repo.

**Session branch.** In session-branch mode (see `$SPECS_PATH` above) the same ladder names your session branch, `session/<identity>`, but stops before its prompt, since those steps never ask: with no identity, the run leaves its session files uncommitted and its `Specs repo:` line says to set this variable.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal string, not a path.

## `$DEV_WORKFLOWS_COST_PRICES`

- **`$DEV_WORKFLOWS_COST_PRICES`** — optional override path for the token-price table session-cost reporting prices against; this plugin ships its own default table, so setting it is never required.

**Resolution.** First-found-wins, three tiers: `$DEV_WORKFLOWS_COST_PRICES` (a path) → a repo-local `cost-prices.yaml` → the bundled `${CLAUDE_PLUGIN_ROOT}/references/cost-prices.yaml`. Whichever file resolves must carry a top-level `models:` map keyed by model id — a file missing that wrapper, override or default, prices every model as `cost_usd: null` rather than raising an error.

**When unset.** Resolution falls straight through to the repo-local file, then the bundled default. Of the nine variables, this is the one most users never touch.

**When it points somewhere unreadable.** Treated the same as "not set at this tier" — resolution continues down the same chain rather than failing the run.

**Its name keeps the `DEV_WORKFLOWS_` prefix deliberately**: renaming it would silently ignore every setting already exported on a working machine. See [Session cost](session-cost.md) for what the table prices.

## Run flags

Three flags change what a run does around its work, and each has an environment variable, below, as its persistent default. A flag on the command line always wins over its variable; with neither, the flag is off. A flag may stand anywhere in a command's arguments — save inside the free-text request of a command that takes one, such as `/implement` or `/feedback`, where only the flags before the request starts and those it ends with are read.

| Flag | What it does | Its default |
|---|---|---|
| `--skip-costs` | The run writes no cost entry. The session's cost checkpoint still advances, so the next run's window starts where it should. | `$WORKFLOWS_SKIP_COSTS` |
| `--skip-feedback` | The maintenance phase records bugs in the plugin only, and drops the in-session Lessons Learned report. | `$WORKFLOWS_SKIP_FEEDBACK` |
| `--enforce-model=<model>` | Every subagent the run dispatches runs on one model, in place of model routing's choice for each step. | `$WORKFLOWS_ENFORCE_MODEL` |

`--skip-costs` and `--skip-feedback` are on when given bare, and `=false` turns one off for a single run against its variable. `--enforce-model` takes its model after `=` or as the next argument, and accepts:

- a family — `opus`, `sonnet`, `haiku` or `fable` — which runs every dispatch on that family's model;
- a family's newest model named by version, such as `opus5.5` or `claude-opus-5-5`, which runs as the family, since Claude Code's agent tool chooses models by family only; an older version stops the run and says to name the family instead;
- `routing`, which turns enforcement off, as an unset variable does.

Any other value, or a model the session cannot reach, stops the run before it writes anything. A command a flag does not apply to ignores it. For example, `/dev-workflows:implement ACME-77-01 --enforce-model=opus --skip-feedback` runs every dispatch on Opus and writes no Lessons Learned report. The Model routing pages of `dev-workflows` and `product-workflows` say what enforcing one model changes for their commands.

## `$WORKFLOWS_SKIP_COSTS`

- **`$WORKFLOWS_SKIP_COSTS`** — the persistent default for the `--skip-costs` run flag; a command it applies to still advances the session-cost checkpoint (pricing nothing), but never writes a cost entry into `$SPECS_PATH`.

**Resolution.** Read as a boolean: `1`, `true` or `yes`, matched case-insensitively, is on; any other value, and an unset variable, is off. A `--skip-costs` flag on the command line always overrides it.

**When unset.** Off — the command's cost phase runs exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

## `$WORKFLOWS_SKIP_FEEDBACK`

- **`$WORKFLOWS_SKIP_FEEDBACK`** — the persistent default for the `--skip-feedback` run flag; narrows a command's maintenance phase to bug capture only.

**Resolution.** Same boolean grammar as `$WORKFLOWS_SKIP_COSTS` above; a `--skip-feedback` flag on the command line always overrides it.

**When unset.** Off — the maintenance phase dispatches `impl-maintenance` exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

## `$WORKFLOWS_ENFORCE_MODEL`

- **`$WORKFLOWS_ENFORCE_MODEL`** — the persistent default for the `--enforce-model` run flag; pins every subagent a command dispatches to one model, bypassing model-routing's own per-step selection.

**Resolution.** An alias, a full model id, or `routing`; resolved against the run flags' alias table and reachability check. Unset, set but empty, or set to `routing` (matched case-insensitively, as the aliases are) means no enforcement. An `--enforce-model=<value>` flag on the command line always overrides it. Where the agent tool's `model` parameter accepts only family names (`opus`, `sonnet`, `haiku`, `fable`), as Claude Code's does today, a family alias enforces that family and the harness picks its version, and a version-specific value (`opus5.5`, `claude-opus-5-5`) is honoured only when it is its family's newest row (in the model-routing chain, or for Haiku in the run flags' Haiku rows), and is then passed as the family name, so `opus5.5` runs on whatever Opus the harness selects — while any other version-specific value (an older row such as `opus5`, an id on no chain, or a Fable id) stops `RUN_FLAGS_MODEL_UNAVAILABLE` with a message suggesting the bare family.

**When the value is bad.** On a run whose command line gives no `--enforce-model` of its own, a value matching none of these forms stops every command `--enforce-model` applies to with `RUN_FLAGS_BAD_MODEL`, and a value that resolves to an unreachable model stops it with `RUN_FLAGS_MODEL_UNAVAILABLE` — both before any write, when the run flags are stripped, each message tagging the value `(from WORKFLOWS_ENFORCE_MODEL)` so the environment, not the command line, is the thing to fix. A command it does not apply to ignores it silently, bad value or not.

**When unset.** No enforcement — model routing selects each step's model exactly as if the variable did not exist.

**When it points somewhere unreadable.** Not applicable — this variable holds a literal value, not a path.

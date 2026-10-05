# Changelog

All notable changes to the **guideline-reviewers** plugin are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versions follow semver at the plugin level.
A section headed `— Unreleased` has not been published yet; where more than one of them stands, they all ship together in the next release.

## [1.1.0] — 2026-10-05

### Added
- **Both agents treat what they read as data, never instructions.** Each ends its prompt with the untrusted-content block the repository keeps in `workflows-core`'s reference: content supplies the values a task asks for and never a new task, a fetch or a changed verdict, and an agent reports what tried to steer it as an `Untrusted-content notice:` line.
- **Both commands that dispatch an agent relay those notices** under `Untrusted-content notices:` in their final report, or in the stop message of a run that ends early. The sentence cites nothing: this plugin does not depend on `workflows-core`, so its loader may not be installed.

## [1.0.3] — 2026-09-24

### Changed — the marketplace is now `shipwright`, and the repository `ihudak/ai-workflows`

The marketplace was `ihudak-plugins`, at `ihudak/ihudak-claude-plugins`. GitHub redirects the old repository URL, but the marketplace name is part of every install key (`<plugin>@ihudak-plugins`), so moving to the new name means registering the marketplace again. Removing a marketplace uninstalls the plugins installed from it, so reinstall each one you had:

```bash
claude plugin marketplace remove ihudak-plugins
claude plugin marketplace add ihudak/ai-workflows
claude plugin install <plugin>@shipwright
```

Run the last line once per plugin you use, then restart Claude Code. Environment variables and your specs, docs and code repositories are not touched. This plugin's `homepage` and `repository` now point at the new repository.

## [1.0.2] — 2026-09-23

### Changed — a neutral example header name

`api-guideline-reviewer`'s tenant-header check and the Spectral ruleset comment beside it gave spelling-drift examples prefixed with an organisation's initials. They now use a neutral `Acme-Tenant` / `AcmeTenant`. The rule itself is unchanged.

## [1.0.1] — 2026-09-18

### Fixed — the overlay variables are written with one `$`

Both agents' rule-overlay tables named their third rung `$$UI_GUIDELINES_PATH` and `$$API_GUIDELINES_PATH`, and both command pages copied it. Run by bash, `$$` is the shell's own process id, so the rung an agent transcribed literally tested a directory named like `188847UI_GUIDELINES_PATH`, which never exists — and a miss at that rung falls through silently to the bundled baseline, which is what the rung is designed to do, so an overlay set through either variable was never read and nothing said so. All four sites now read `$UI_GUIDELINES_PATH` and `$API_GUIDELINES_PATH`, as the commands and `docs/reference/environment.md` already did.

### Fixed — each linter runs in the reviewed project, not in the session's directory

Both agents ran their linter bare — `npx --no-install eslint`, or the repository's lint script, and `spectral` / `npx --no-install @stoplight/spectral-cli` — and a subagent's Bash tool starts every call in the session's directory, which need not be the reviewed repository. `npx --no-install` resolves its tool from the directory it runs in, so from anywhere else it printed *"npx canceled due to missing packages"* and the lint was skipped as a missing binary — a silent `a11y_check: none` or `lint_source: none` — or it ran under another repository's configuration. A monorepo whose packages keep their own linter was skipped even with the session at its top level. Each agent now partitions the files it reviews and runs each partition's probes and its one lint from that partition's directory, each as one `(builtin cd "<dir>" >/dev/null && …)` subshell — `builtin cd`, its output discarded, so a `cd` function or alias of the user's, which the Bash tool's shell carries, neither runs nor prints into the linter's output — merging the findings, each keyed by its file, so files reviewed together from two packages that each keep their own linter setup are each linted in their own; the report carries one `a11y_check` or `lint_source` line per partition where the files span more than one, each naming its directory.

- **`guideline-reviewer`** partitions by each file's nearest package directory — the nearest directory at or above it, up to its repository's git top level, that holds a `package.json`, else the top level; files in no repository have no top level to walk up to and form one partition in the deepest directory that holds them all — which is where Node resolves the project's ESLint, and lets ESLint find its own configuration, looking upward from there. Whether `eslint-plugin-jsx-a11y` applies is read from the configuration ESLint resolves for the files (`eslint --print-config`), never from one directory's `package.json` or config file: a `package.json` that merely declares ESLint is not a configuration, and a package config that `extends` a shared one need never name the plugin. The runtime-harness check reads every `package.json` from the partition's directory up to the top level. Under Yarn Plug'n'Play, which keeps no `node_modules` for `npx` to find, the probe and the lint run through Yarn from the same directory — `yarn run -B eslint`, and `yarn run -T -B eslint` where only the root workspace declares ESLint — `-B` so that a package script named `eslint`, which Yarn otherwise runs in the binary's place, is never run with the probe's or the lint's arguments. 1.0.0 linted such a repository through its lint script, run by the runner its lockfile names, and it is still linted.
- **`api-guideline-reviewer`** partitions by the nearest directory holding a Spectral ruleset or a `package.json` declaring the CLI, else the top level — the rule `docs-workflows`' `docs-style-checker` and `prose-style`'s `/prose-review-pr` and `/prose-review-docs` already follow for Vale — and its ruleset is the nearest `.spectral.*` up to the top level, no longer only one at the repository's root. Spectral lints each partition's specs in one run, where it ran once per spec. For a spec in no repository, which has no top level to stop at, both searches stop at the spec's own directory. The ruleset is passed to Spectral by its absolute path, because the lint runs from the partition's directory: a path relative to the repository's top level names no file there, and Spectral would stop with *"Error running Spectral!"*, which the agent reads as no CLI resolved, reviewing the spec without its lint. The command page and the getting-started page named `.spectral.yaml` alone as the ruleset that wins over the bundled one, although the agent took `.spectral.yml` and `.spectral.json` as well; every site names all three now.

A repository whose ESLint configuration and `package.json` sit at its top level is linted from there — from where 1.0.0 linted it with the session standing in it — a Yarn Plug'n'Play one included. A monorepo that keeps its configuration at the top level has each package's files linted under the configuration ESLint resolves from that package's directory.

### Fixed — `guideline-reviewer` no longer promises that its lint matches CI

Its rationale said a repository's CI "will run exactly that on the PR", and that wrapping the repository's own configuration "guarantees the local result matches what CI checks". Neither holds for a repository with no CI. Nor does it hold where CI lints other files, passes flags of its own or pins other versions, or lints from another directory: ESLint 9 reads the flat configuration of the directory it runs in, and this release lints each file from its package directory. The rationale now says what wrapping buys: the repository's own rule set, as ESLint resolves it for each file. It also says when CI reports the same. `api-guideline-reviewer` made no such claim.

### Fixed — `guideline-reviewer` reads a lint script's findings from a file, and never lets Corepack download a runner

It preferred the repository's lint script, run through the runner its lockfile names — `pnpm` for a `pnpm-lock.yaml`, `yarn` for a `yarn.lock`, `npm` for a `package-lock.json` or `npm-shrinkwrap.json`, `bun` for a `bun.lockb` — and parsed the JSON from the script's standard output, where `npm run`, `pnpm run` and Yarn 1's `yarn run` each print a banner of their own around ESLint's output: npm and pnpm the script's name and the command it runs, ahead of it; Yarn 1 its version and the command ahead of it and a `Done in …` line after. Under any of the three the parse failed, the run recorded an `a11y_attempt`, and every linter finding was lost — wherever it preferred the lint script, on a repository whose lockfile is a `package-lock.json`, an `npm-shrinkwrap.json`, a `pnpm-lock.yaml` or a Yarn 1 `yarn.lock` (measured with npm 11.14.1, pnpm 9.15.0 and Yarn 1.22.22). Yarn 2 and later print nothing around a script's output; `bun` was not measured. The script is now handed ESLint's `--format json --output-file <file>`, `<file>` a fresh path outside every repository, and the JSON is read from that file, which is then removed with `command rm -f --`, so an `rm` alias or function of the user's never keeps it.

Running `yarn` or `pnpm` let Corepack, which supplies both wherever Node.js enables it, download the release a repository's `packageManager` field pins wherever the machine lacked it — an install the agent's own rule forbids. Every command the check runs through a package runner now carries `COREPACK_ENABLE_NETWORK=0`, which Corepack reads and a runner it does not manage ignores. Where Corepack manages the runner and the machine lacks the pinned release, the runner exits with Corepack's *"Network access disabled by the environment"*, and the check records that attempt and goes on without the lint, installing nothing.

### Fixed — `guideline-reviewer` keeps only the reviewed files' findings

It preferred the repository's lint script where one accepts file arguments — a script named `lint`, `lint:js`, `lint:ts` or `eslint` — and kept every `jsx-a11y/` message in the JSON the script produced. A script such as `"eslint": "eslint src"` lints all of `src/` beside the files it is handed, so the review reported accessibility findings in files outside the review, against its own rule that the check is scoped to the files under review. It now keeps only the entries whose `filePath` is one of the partition's reviewed files, whatever else the lint covered, and only then their `jsx-a11y/` messages. Measured with ESLint 9.39 and `eslint-plugin-jsx-a11y` 6.10 through `npm run eslint`: the script linted both files of `src/` when handed one, and the filter kept that one's `jsx-a11y/alt-text` alone, where the `ruleId` filter alone, 1.0.0's, kept both files' — wherever 1.0.0's parse succeeded at all, which under `npm`, `pnpm` and Yarn 1 it did not (above).

### Fixed — the ESLint output file is created with `command mktemp`

`guideline-reviewer`'s accessibility branch named the file it gives ESLint `--output-file` with a bare `mktemp`, which the agent's own shell resolves through any alias or shell function of that name before `mktemp` runs — so the path the linter writes to, and the agent then reads, is whatever that printed. It now runs `command mktemp`.

### Fixed — the ESLint output file goes when branch 1 gives up, not only when it is read

`guideline-reviewer`'s accessibility branch removed its `--output-file` only "once it is read", and the two-minute timeout — like any other branch-1 failure — falls through to branch 2 without reading it, so the file was left in the system's temporary directory with nothing to remove it. The removal now also fires where branch 1 gives up.

### Fixed — the reference inventory no longer says each subtree carries one vendored file

1.0.0's `docs/reference/references.md` opened by saying each subtree "also carries one vendored non-markdown file", while `api-guidelines/` carries two — `spectral/ruleset.yaml` and `template/openapi-template.yaml` — and the same page's arithmetic paragraph, below the subtree table, says so, so a reader who trusted the opening counted 37 files where 38 ship. The opening no longer states a per-subtree count at all and points at the arithmetic, which is where the counts are derived. No check in `scripts/` validates that clause: check 9 reads the same opening sentence, but only its `38` total, which was already right.

### Fixed — an overlay directory that resolves to nothing is no longer silent

1.0.0's `docs/reference/environment.md` told an operator to lay an overlay out *"identically to the bundled subtree it overlays"*, in the same sentence that calls it a flat directory of `.md` files. The two halves agree for `$UI_GUIDELINES_PATH` — `references/guidelines/` is flat — and contradict each other for `$API_GUIDELINES_PATH`, whose subtree is two levels deep: all 24 of its markdown files sit under `permission-guidelines/` or `rest-api-guidelines/`. An operator who followed the clause put their rules a level down, which answers neither agent's rung — order 3 resolves only where the variable *"names a readable directory containing ≥1 `.md` file"*, and a directory of subdirectories holds none of its own. The run then fell back to the bundled baseline **silently**, by design: the agents' Step B fell through without a word and Step D forbade a note about it, so the only signal was `rules_source: baseline`, which is also what an operator who set nothing gets. That is the same failure mode as the `$$UI_GUIDELINES_PATH` entry above, reached through a documented layout rather than a shell bug.

Both agents now split the fall-through. A candidate that does not exist or cannot be read is still silent — a missing overlay is the normal case. A candidate that **is** a readable directory and holds no `.md` file of its own is not: the agent falls through as before and emits `rules_overlay_skipped:<absolute path>` beside `rules_source`, naming the directory and what it looked for, for every such candidate and even where a later order resolves. Both commands' flag text, `/guideline-reviewer`'s dispatch block, both command pages and `docs/reference/environment.md` say so, and the documentation now describes the real layout: an overlay is flat whatever shape the subtree it overlays has, because matching is by file name and never by path.

### Fixed — an overlay file whose name is in the API baseline twice matches both

`references/api-guidelines/` holds two files called `Introduction.md`, one under each of its subtrees, and Step C's rules were written against *"a baseline file"*, singular. Layering was harmless either way, but `<!-- api-guidelines: replace -->` was genuinely undecided — it could have dropped one of the two or both, and nothing said which. An overlay file matches **every** baseline file of its name: it layers over both, and the marker replaces both. `references/guidelines/` repeats no name, so `/guideline-reviewer` states the matching rule without the case.

### Fixed — the reference inventory's table header sits over the columns it describes

1.0.0's `docs/reference/references.md` carried a three-column table whose header row was shifted one column against its body: the column headed **Markdown files** held a prose description, and the column headed **What it holds** held provenance. The markdown counts were never in the "Markdown files" column at all — they are the `(24)` / `(11)` parentheticals in column 1, which is where `check-docs.sh` check 4 reads them. As printed, the table stated that an OpenAPI template, a Spectral ruleset and a checker script are markdown files, three lines below the opening sentence that names all three as the corpus's non-markdown files and seven above the arithmetic paragraph that counts them as such. The header now reads **Subtree (markdown files) | What it holds | Derived from**, so each cell sits under its own heading and the counts stay in column 1 untouched. Each *What it holds* cell also says which of its items the count leaves out, since a cell describes the whole subtree while the parenthetical beside it counts only the markdown in it.

### Fixed — the corpus's third non-markdown file is no longer called prose

The same page closed on a trichotomy over the whole corpus — the Spectral ruleset *runs*, the checker script is *invoked*, *"Everything else is prose the agents read"* — which put `api-guidelines/template/openapi-template.yaml`, a starter OpenAPI document, in the prose bucket nine lines after the page named it as one of three vendored non-markdown files. `api-guideline-reviewer` agrees with the opening rather than the closing: it loads the template as its own labelled kind, listed apart from the guidance prose. The sentence now names all three and says what the template is.

## [1.0.0] — 2026-09-02

### Added — extracted from `dev-workflows` 3.25.0

`/api-guideline-reviewer` and `/guideline-reviewer`, their two agents, and the 38 reference files they read shipped as part of `dev-workflows` through its 3.25.0 release. This plugin carries all of it forward unchanged: both commands behave exactly as they did there — same flags, same resolution order, same bundled guidance corpora, same overlay mechanism (`$UI_GUIDELINES_PATH` / `$API_GUIDELINES_PATH`, still overlaid at `<repo-root>/.dev-workflows/{ui,api}-guidelines/`, unchanged so an existing overlay keeps resolving). Only the install location and the command prefix moved: `/dev-workflows:guideline-reviewer` is gone, and the bare command names keep working once this plugin is installed alongside or instead of `dev-workflows`.

This is the first increment of the marketplace split designed in `docs/superpowers/specs/2026-09-02-marketplace-split-design.md`. See `dev-workflows`'s own `CHANGELOG.md` 3.25.0 entry for what stayed behind and why these two commands were the right thing to extract first.

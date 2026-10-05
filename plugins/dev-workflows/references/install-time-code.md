# Install-time code (shared reference)

`/vuln` and `/upgrade` move a dependency to a new version and install it. A release can ship code that runs while it is installed — an npm package's `preinstall`, `install` or `postinstall` script, or the build of a Python source distribution, which runs its build backend — and that code runs with the user's permissions, in a container and on a host alike. `vuln-fixer` and `upgrade-executor` therefore install without it, name what they skipped with the command that would run, and run it only for the packages the user named with `--allow-install-scripts` on the command line. `fix-vuln/build-systems.md` and `upgrade/ecosystems.md` write every install that way, and check 21 of `scripts/check-docs.sh` fails the build on an install command in either of them, or in this file, that does not.

## Install without it

| Ecosystem | Recognised by | Install, add or update |
|---|---|---|
| npm | `package-lock.json` | `npm install --ignore-scripts …` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --ignore-scripts`, `pnpm add --ignore-scripts …` |
| yarn classic | `yarn.lock`, no `.yarnrc.yml`, and no `packageManager` field naming `yarn@2` or later | `yarn install --ignore-scripts`, `yarn add --ignore-scripts …` |
| yarn berry | `yarn.lock` with a `.yarnrc.yml`, or a `packageManager` field naming `yarn@2` or later | edit `package.json`, then `yarn install --mode=skip-build` |
| pip | `requirements.txt` | `pip install --only-binary=:all: -r requirements.txt` |
| pipenv | `Pipfile` | `PIP_ONLY_BINARY=:all: pipenv install …` — pip reads `PIP_ONLY_BINARY` from the environment pipenv runs it in |

pnpm 10 builds a dependency only when the project lists it in `onlyBuiltDependencies`; the flag holds back even those, and the list below is read from the installed packages either way. Go, Cargo, Maven, Gradle and NuGet run no dependency code at install time. Bundler builds native extensions as a matter of course, and Poetry, uv, PDM, Hatch and Composer have their own no-build or no-scripts settings that this file does not yet adopt — all of them install as their own sections say.

**The project's own install scripts.** `--ignore-scripts` also skips the root `package.json`'s own `preinstall`, `install`, `postinstall` and `prepare` scripts, a workspace member's, and the `node-gyp rebuild` npm runs for a root `binding.gyp`. Those are the repository's declared commands, which the agent runs as it runs its build: right after the install, in the same step and before building, with `npm run <script>` (or the package manager's own `run`) — with one exception: a script whose command installs, rebuilds or bootstraps packages (a package manager's install, ci, add or rebuild, a lerna bootstrap, and the like) would run dependency install code by that route, so it is not run but listed, as `project:<hook> (<ecosystem>: <hook>: <command>)`.

**Never run a dependency's install-time code to make a build pass.** Dropping the flag, `npm rebuild`, `pnpm rebuild`, `yarn rebuild`, a `--no-binary` install, a project script of the kind just excepted, or a change to a project or user configuration that enables scripts — none of these is an automatic fix. Only the packages named with `--allow-install-scripts` run install-time code, as the last section says; a build or a test run that fails without them is what the list below is for.

## Name what was skipped

**Before the install**, record which packages are on disk: the name and version in every `package.json` under `node_modules` (under `node_modules/.pnpm/` for pnpm). **After it**, write `skipped_install_scripts:` with one entry per package that is on disk now but was not before — a new package, or a new version of one — and carries install-time code, plus every project script excepted above, or `[]` when there is none:

- npm, pnpm and yarn with a `node_modules` linker: its `package.json` declares a `preinstall`, `install` or `postinstall` script — the entry is `<name>@<version> (<ecosystem>: <hook>: <command>)`, with the command exactly as that `package.json` writes it — or it ships a `binding.gyp` and declares neither `preinstall` nor `install`, which npm runs as `install: node-gyp rebuild (binding.gyp)`.
- yarn berry under Plug'n'Play, which writes no `node_modules`: every package whose `yarn.lock` entry the install added or changed and whose `package.json`, read from its archive in the yarn cache, declares one of those scripts, as above.
- pip and pipenv: the install refused the package for want of a wheel and named it ("No matching distribution found for <name>" — with `==<version>` where the requirement pins one), as `<name>[@<version>] (pip: source build)`. That refusal fails the install, and the agent handles it as a build failure. pip names one refused package at a time, so a later run can name another.

Measuring against the disk, not the lockfile, is what covers a clone that was never installed: every package arrives in that install without its scripts, and each one that has any is listed. A package that was on disk before the install keeps what its scripts built then, and is never listed.

## After a revert

A revert (`code-repo-handoff.md` §6.2) restores the tracked files, not `node_modules`, which still holds the new versions, unbuilt — and the next install in the same run would put the old versions back without their scripts, losing what those built. So after any revert in a Node project, restore `node_modules` to the lockfile: run the install from the first section again, then rebuild — `npm rebuild <names>`, `pnpm rebuild <names>` or `yarn rebuild <names>` — exactly the packages the install put back at the versions recorded before this unit's install. Those are versions that were installed, scripts and all, before the run began, so this restores the user's own state rather than running new code; nothing else is rebuilt. Name what was restored in `notes`.

## Allow it for named packages

A request carrying `allow_install_scripts: [<name>…]` — the names the user gave `--allow-install-scripts`, a package name or `project:<hook>` — runs this before building. For npm, pnpm, yarn and a `project:<hook>`, install as above, then run it for each allowed name the install listed as skipped. For pip and pipenv, run it in place of the plain install, naming every allowed name: pip builds from source only the named packages the requirements need, and any other package without a wheel is still refused and listed.

| Ecosystem | Allow |
|---|---|
| npm, yarn classic | `npm rebuild <names>` |
| pnpm | `pnpm rebuild <names>` — with pnpm 10, only a package the project lists in `onlyBuiltDependencies` builds; for any other, `notes` says so, the agent changes no configuration, and the summary names the setting |
| yarn berry | `yarn rebuild <names>` |
| a `project:<hook>` | `npm run <hook>` (or the package manager's own `run`) |
| pip | in place of the plain install: `pip install --only-binary=:all: --no-binary=<names> -r requirements.txt` — the named packages build from source, every other package still installs as a wheel or is refused and named |
| pipenv | `pipenv run pip install --only-binary=:all: --no-binary=<names> <name>==<version> …`, one command for every allowed name, with the versions `Pipfile.lock` pins; then `PIP_ONLY_BINARY=:all: pipenv install` again |

An allowed package leaves `skipped_install_scripts:`; for npm, pnpm and yarn, a name the install did not list is not run, and `notes` says so. An allow command that fails is a build failure, with the command and its error in `notes`. A package the allowed build in turn needs, and that has no wheel, is refused and listed like any other — the next run names it too.

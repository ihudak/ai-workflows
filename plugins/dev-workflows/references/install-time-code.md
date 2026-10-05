# Install-time code (shared reference)

`/vuln` and `/upgrade` move a dependency to a new version and install it. A release can ship code that runs while it is installed — an npm package's `preinstall`, `install` or `postinstall` script, or the build of a Python source distribution, which runs its build backend — and that code runs with the user's permissions, in a container and on a host alike. `vuln-fixer` and `upgrade-executor` therefore install without it, name what they skipped with the command that would run, and run it only for the packages the user named with `--allow-install-scripts` on the command line. `fix-vuln/build-systems.md` and `upgrade/ecosystems.md` write every install that way, and check 21 of `scripts/check-docs.sh` fails the build on an install command in either of them, in this file, or in the two agents and two commands, that does not.

## Install without it

| Ecosystem | Recognised by | Install, add or update |
|---|---|---|
| npm | `package-lock.json` | `npm install --ignore-scripts …` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --ignore-scripts`, `pnpm add --ignore-scripts …` |
| yarn classic | `yarn.lock`, no `.yarnrc.yml`, and no `packageManager` field naming `yarn@2` or later | `yarn install --ignore-scripts`, `yarn add --ignore-scripts …` |
| yarn berry | `yarn.lock` with a `.yarnrc.yml`, or a `packageManager` field naming `yarn@2` or later | edit `package.json`, then `yarn install --mode=skip-build` |
| pip | `requirements.txt`, or a `pyproject.toml` or `setup.py` installed as the project | `pip install --only-binary=:all: -r <requirements file>`, or `pip install --only-binary=:all: -e .` |
| pipenv | `Pipfile` | `PIP_ONLY_BINARY=:all: pipenv lock`, `PIP_ONLY_BINARY=:all: pipenv install …` — pip reads `PIP_ONLY_BINARY` from the environment pipenv runs it in, and its lock step, run without it, builds a source distribution to read its metadata |

pnpm 10 builds a dependency only when the project lists it in `onlyBuiltDependencies`; the flag holds back even those, and the list below is read from the installed packages either way. Go, Cargo, Maven, Gradle and NuGet run no dependency code at install time. Bundler builds native extensions as a matter of course, and Poetry, uv, PDM, Hatch and Composer have their own no-build or no-scripts settings that this file does not yet adopt — all of them install as their own sections say.

**What the flags do not stop.** pip builds a requirement given as a version-control URL (`git+…`, `hg+…`, `svn+…`, `bzr+…`), as a URL to anything but a `.whl`, or as a local path (`./pkg`, `-e ./pkg`, `<name> @ file:…`), whatever `--only-binary` says; pipenv builds a `Pipfile` entry of that kind (`git =`, `path =`, `file =`) while it locks, whatever `PIP_ONLY_BINARY` says. So before pip or pipenv installs anything, read the requirements as text — each requirements file the install names and every file it pulls in with `-r` or `-c`, the dependency lists of `pyproject.toml`, `setup.cfg` or `setup.py`, or the `Pipfile` — and never by asking pip to resolve them, which builds the same metadata. The project itself (`.`, `-e .`) is not one of them. Each such requirement, unless allowed, is listed as `<name> (pip: source build, <url or path>)`, and:

- in a requirements file, the install runs from a copy of that file, written outside the repository, without its line — and a file it pulls in with `-r` or `-c` is copied the same way;
- anywhere else — a dependency list or a `Pipfile`, where no line can be left out — nothing is installed, and the agent handles it as a build failure.

**A project that turns scripts off itself** — `ignore-scripts=true` in an `.npmrc` (`npm config get ignore-scripts` prints `true`), or `enableScripts: false` in `.yarnrc.yml` — has decided for its own scripts too. The agent runs none of the project's install scripts and no allow command there; `notes` says so, and the summary names the setting. `npm rebuild` in such a project prints success and runs nothing, so running it would report as built a package that was not.

**The project's own install scripts.** `--ignore-scripts` also skips the root `package.json`'s own `preinstall`, `install`, `postinstall` and `prepare` scripts, each workspace member's, and the `node-gyp rebuild` npm runs for a root `binding.gyp`. Those are the repository's declared commands, which the agent runs as it runs its build: right after the install, in the same step and before building — each with npm, whatever the package manager, and with every package manager's scripts turned off in its environment:

`npm_config_ignore_scripts=true YARN_IGNORE_SCRIPTS=true YARN_ENABLE_SCRIPTS=false npm run <hook>` — for a workspace member, `npm --prefix <member path> run <hook>` in the same environment.

Run any other way, `npm run install` also runs `preinstall` and `postinstall`, yarn's and pnpm's own `run` start those pre and post hooks whatever the environment says, and a hook that calls `npm rebuild <name>` — or runs a file that does — runs that package's install code. In that environment each runs only the hook it names, and no dependency's code. Under yarn berry, which npm cannot run, the command is `yarn run <hook>` in the same environment. One kind is not run but listed: a hook whose command installs, rebuilds or bootstraps packages (a package manager's install, ci, add or rebuild, a lerna bootstrap, and the like), as `project:<hook> (<ecosystem>: <hook>: <command>)` — `project:<member path>:<hook>` for a workspace member's.

**Never run a dependency's install-time code to make a build pass.** Dropping the flag, `npm rebuild`, `pnpm rebuild`, `yarn rebuild`, a `--no-binary` install, a project script of the kind just excepted, or a change to a project or user configuration that enables scripts — none of these is an automatic fix. Only the packages named with `--allow-install-scripts` run their install-time code, as the last section says; a build or a test run that fails without them is what the list below is for.

## Name what was skipped

**Before the install**, record which packages are on disk: the name and version in every `package.json` under `node_modules` (under `node_modules/.pnpm/` for pnpm). **After it**, write `skipped_install_scripts:` with one entry per package that is on disk now but was not before — a new package, or a new version of one — and carries install-time code, plus every project script excepted above, or `[]` when there is none:

- npm, pnpm and yarn with a `node_modules` linker: its `package.json` declares a `preinstall`, `install` or `postinstall` script — the entry is `<name>@<version> (<ecosystem>: <hook>: <command>)`, with the command exactly as that `package.json` writes it — or it ships a `binding.gyp` and declares neither `preinstall` nor `install`, which npm runs as `install: node-gyp rebuild (binding.gyp)`.
- yarn berry under Plug'n'Play, which writes no `node_modules`: every package whose `yarn.lock` entry the install added or changed — every package in `yarn.lock` where `.yarn/install-state.gz` did not exist before the install, the mark of a project never installed here — and whose `package.json`, read from its archive in the yarn cache, declares one of those scripts, as above.
- pip and pipenv: every requirement "What the flags do not stop" left out, and every package the install refused for want of a wheel ("No matching distribution found for <name>" — with `==<version>` where the requirement pins one), as `<name>[@<version>] (pip: source build)`. A refusal fails the install, and the agent handles it as a build failure. pip stops at the first package it refuses, so before installing the agent checks each requirement it would take from an index — each requirements-file line the install keeps, or each package the `Pipfile` names, with its version specifier — with `pip download --only-binary=:all: --no-deps -d <a directory outside the repository> <requirement>`, which fetches wheels and builds nothing, and lists every one refused. A package that only a refused one needs is named by a later run.

Measuring against the disk, not the lockfile, is what covers a clone that was never installed: every package arrives in that install without its scripts, and each one that has any is listed. A package that was on disk before the install keeps what its scripts built then, and is never listed.

## After a revert

A revert (`code-repo-handoff.md` §6.2) restores the tracked files, not `node_modules`, which still holds the new versions, unbuilt. So after any revert in a Node project — the agent's own on any call, or the orchestrator's (§6.3) — restore `node_modules` to the lockfile: record which packages are on disk, then run the install from the first section again. It replaces only the packages whose version the revert moved back and leaves every other one as it was. Each package it put back that carries install-time code goes in the list like a skipped one, as `<name>@<version> (<ecosystem>: <hook>: <command>) — restored unbuilt: <rebuild command>`, the rebuild command being `npm rebuild <name>` (npm and yarn classic), `pnpm rebuild <name>` or `yarn rebuild <name>`. That command is the user's to run, never the agent's: nothing on disk says whether that version was built before the run, and in a clone that never built it, it would run code no one allowed.

## Allow it for named packages

A request carrying `allow_install_scripts: [<name>…]` — the names the user gave `--allow-install-scripts`: a package, `project:<hook>` or `project:<member path>:<hook>` — runs this before building, except in a project that turns scripts off itself. For npm, pnpm, yarn and a project script, install as above, then run it for each allowed name the install listed as skipped. For pip, run it in place of the plain install, naming every allowed name; an allowed requirement of the kind "What the flags do not stop" leaves out stays in, and builds. For pipenv, write the configuration the table gives and run the commands under it.

| Ecosystem | Allow |
|---|---|
| npm, yarn classic | `npm rebuild <names>` |
| pnpm | `pnpm rebuild <names>` — with pnpm 10, only a package the project lists in `onlyBuiltDependencies` builds; for any other, `notes` says so, the agent changes no configuration, and the summary names the setting |
| yarn berry | `yarn rebuild <names>` — it builds the root workspace too, running the root's own `postinstall`; where that is a listed `project:postinstall` the user did not allow, the agent runs nothing and `notes` says why |
| a project script | its own command from "The project's own install scripts", in the same environment |
| pip | in place of the plain install: `pip install --only-binary=:all: --no-binary=<names> -r <requirements file>`, or `pip install --only-binary=:all: --no-binary=<names> -e .` — the named packages build from source, every other package still installs as a wheel or is refused and named |
| pipenv | a pip configuration file outside the repository holding `[install]`, `only-binary = :all:` and then `no-binary = <names>` — in that order, the one pip honours — then `PIP_CONFIG_FILE=<that file> pipenv lock` and `PIP_CONFIG_FILE=<that file> pipenv install` in place of the plain ones: the named packages build, any other without a wheel is still refused, and `Pipfile.lock`'s hashes are still checked |

An allowed package leaves `skipped_install_scripts:`; for npm, pnpm and yarn, a name the install did not list is not run, and `notes` says so. An allow command that fails is a build failure, with the command and its error in `notes`. A package the allowed build in turn needs, and that has no wheel, is refused and listed like any other — the next run names it too.

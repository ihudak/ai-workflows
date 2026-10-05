# Install-time code (shared reference)

`/vuln` and `/upgrade` move a dependency to a new version and install it. A release can ship code that runs while it is installed — an npm package's `preinstall`, `install` or `postinstall` script, or the build of a Python source distribution, which runs its build backend — and that code runs with the user's permissions, in a container and on a host alike. `vuln-fixer` and `upgrade-executor` therefore install without it, name what they skipped, and run it only for the packages the user allows. `fix-vuln/build-systems.md` and `upgrade/ecosystems.md` write every install that way, and check 21 of `scripts/check-docs.sh` fails the build on an install command in either of them, or in this file, that does not.

## Install without it

| Ecosystem | Recognised by | Install, add or update |
|---|---|---|
| npm | `package-lock.json` | `npm install --ignore-scripts …` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --ignore-scripts`, `pnpm add --ignore-scripts …` |
| yarn classic | `yarn.lock`, no `.yarnrc.yml`, and no `packageManager` field naming `yarn@2` or later | `yarn install --ignore-scripts`, `yarn add --ignore-scripts …` |
| yarn berry | `yarn.lock` with a `.yarnrc.yml`, or a `packageManager` field naming `yarn@2` or later | edit `package.json`, then `yarn install --mode=skip-build` |
| pip | `requirements.txt` | `pip install --only-binary=:all: -r requirements.txt` |
| pipenv | `Pipfile` | `PIP_ONLY_BINARY=:all: pipenv install …` — pip reads `PIP_ONLY_BINARY` from the environment pipenv runs it in |

pnpm 10 builds a dependency only when the project lists it in `onlyBuiltDependencies`; `--ignore-scripts` holds back even those, and the list below is read from the installed packages either way. Bundler, Poetry, uv, PDM, Hatch, Composer, NuGet, Go, Cargo, Maven and Gradle install as their own sections say: Go, Cargo, Maven and Gradle run no dependency code at install time, Bundler builds native extensions as a matter of course, and the rest have no wheels-only or no-scripts setting this file can rely on across their versions.

**The project's own install scripts still run.** `--ignore-scripts` also skips the root `package.json`'s own `preinstall`, `install`, `postinstall` and `prepare` scripts — a `patch-package` step, a code generator. They are the repository's declared commands, which the agent runs as it runs its build: after the install, run each one the root `package.json` declares, with `npm run <script>` (or the package manager's own `run`).

**Never run a dependency's install-time code to make a build pass.** Dropping the flag, `npm rebuild`, `pnpm rebuild`, `yarn rebuild`, a `--no-binary` install, or a change to a project or user configuration that enables scripts — none of these is an automatic fix. Only a request's `allow_install_scripts:` runs install-time code, and only as the last section says. A build or a test run that fails after such an install is the case the next section exists for: name the packages, and leave allowing them to the user.

## Name what was skipped

**Before the install**, record which packages are on disk: the name and version in every `package.json` under `node_modules` (under `node_modules/.pnpm/` for pnpm). **After it**, write `skipped_install_scripts:` with one entry per package that is on disk now but was not before — a new package, or a new version of one — and carries install-time code, or `[]` when there is none:

- npm, pnpm and yarn with a `node_modules` linker: its `package.json` declares a `preinstall`, `install` or `postinstall` script — the entry is `<name>@<version> (<ecosystem>: <hook>: <command>)`, with the command exactly as that `package.json` writes it — or it ships a `binding.gyp` and declares none, which npm runs as `install: node-gyp rebuild (binding.gyp)`.
- yarn berry under Plug'n'Play, which writes no `node_modules`: every package whose `yarn.lock` entry the install added or changed and whose manifest (`yarn info <name>@<version> --json`) declares one of those scripts, as above.
- pip and pipenv: the install refused the package for want of a wheel and named it ("No matching distribution found for <name>" — with `==<version>` where the requirement pins one), as `<name>[@<version>] (pip: source build)`. That refusal fails the install, and the agent handles it as a build failure. pip names one refused package at a time, so a later run can name another.

Measuring against the disk, not the lockfile, is what covers a clone that was never installed: every package arrives in that install without its scripts, and each one that has any is listed. A package that was on disk before the install keeps what its scripts built then, and is never listed.

## Allow it for named packages

A request carrying `allow_install_scripts:` lists entries from an earlier return of the same CVE or component, exactly as that return wrote them. Run this for each of them — after the install on a full call, and before the verify on a `verify-resume` or a `regression_decision: retry-with-install-scripts` — then build or verify as the call would:

| Ecosystem | Allow |
|---|---|
| npm, yarn classic | `npm rebuild <names>` |
| pnpm | `pnpm rebuild <names>` — with pnpm 10, only a package the project lists in `onlyBuiltDependencies` builds; for any other, `notes` says so, and the agent changes no configuration |
| yarn berry | `yarn rebuild <names>` |
| pip | in place of the plain install: `pip install --only-binary=:all: --no-binary=<names> -r requirements.txt` — the named packages build from source, every other package still installs as a wheel or is refused and named |
| pipenv | per name, `pipenv run pip install --only-binary=:all: --no-binary=<name> <name>==<version>`, with the version `Pipfile.lock` pins where the entry has none; then `PIP_ONLY_BINARY=:all: pipenv install` again |

For npm, pnpm and yarn, an entry runs only while its package is on disk at the entry's version — the revert after a failed build restores the tracked files, not `node_modules`, so a retry finds the new version still there; an entry whose package is not is not run, and `notes` says so. An allowed package leaves `skipped_install_scripts:`; a package the allowed build in turn needs, and that has no wheel, is refused and listed like any other.

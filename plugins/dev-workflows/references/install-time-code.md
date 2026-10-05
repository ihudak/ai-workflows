# Install-time code (shared reference)

`/vuln` and `/upgrade` move a dependency to a new version and install it. A release can ship code that runs while it is installed — an npm package's `preinstall`, `install` or `postinstall` script, or the build of a Python source distribution, which runs its `setup.py` — and that code runs with the user's permissions, in a container and on a host alike. `vuln-fixer` and `upgrade-executor` therefore install without it, name what they skipped, and run it only for the packages the user allows. `fix-vuln/build-systems.md` and `upgrade/ecosystems.md` write every install that way, and check 21 of `scripts/check-docs.sh` fails the build on an install line in either of them, or in this file, that does not.

## Install without it

| Ecosystem | Recognised by | Install, add or update |
|---|---|---|
| npm | `package-lock.json` | `npm install --ignore-scripts …` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --ignore-scripts`, `pnpm add --ignore-scripts …` |
| yarn classic | `yarn.lock` and no `.yarnrc.yml` | `yarn install --ignore-scripts`, `yarn add --ignore-scripts …` |
| yarn berry | `yarn.lock` and a `.yarnrc.yml` | edit `package.json`, then `yarn install --mode=skip-build` |
| pip | `requirements.txt` | `pip install --only-binary=:all: -r requirements.txt` |
| pipenv | `Pipfile` | `PIP_ONLY_BINARY=:all: pipenv install …` |

pnpm 10 already holds dependency build scripts back unless a project allows them; the flag changes nothing there, and the list below is read from the installed packages either way. Bundler, Poetry, Go, Cargo, Maven and Gradle install as their own sections say: Go, Cargo, Maven and Gradle run no dependency code at install time, Bundler builds native extensions as a matter of course, and Poetry's installer has no wheels-only setting this file can rely on across its versions.

**Never drop the flag to make a build pass.** A build or a test run that fails after such an install is the case the list below exists for: name the packages, and leave allowing them to the user.

## Name what was skipped

**Before the install**, record which packages are on disk: the name and version in every `package.json` under `node_modules` (under `node_modules/.pnpm/` for pnpm). **After it**, write `skipped_install_scripts:` with one entry per package that is on disk now but was not before — a new package, or a new version of one — and carries install-time code, or `[]` when there is none:

- npm, pnpm and yarn with a `node_modules` linker: its `package.json` declares a `preinstall`, `install` or `postinstall` script — the entry is `<name>@<version> (<ecosystem>: <hook>: <command>)`, with the command exactly as that `package.json` writes it — or it ships a `binding.gyp` and declares none, which npm runs as `install: node-gyp rebuild (binding.gyp)`.
- yarn berry under Plug'n'Play, which writes no `node_modules`: the packages the install's own output names as not built, each as `<name>@<version> (yarn: build skipped)`.
- pip and pipenv: the install refused the package for want of a wheel and named it ("No matching distribution found for <name>==<version>"), as `<name>@<version> (pip: source build)`. That refusal fails the install, and the agent handles it as a build failure.

Measuring against the disk, not the lockfile, is what covers a clone that was never installed: every package arrives in that install without its scripts, and each one that has any is listed. A package installed before the change keeps what its scripts built then, and is never listed.

## Allow it for named packages

A request carrying `allow_install_scripts: [<name>…]` installs as above, then runs this for exactly the named packages, before building:

| Ecosystem | Allow |
|---|---|
| npm, yarn classic | `npm rebuild <names>` |
| pnpm | `pnpm rebuild <names>` |
| yarn berry | `yarn rebuild <names>` |
| pip | per name, `pip install --no-binary=<name> <name>==<version>`; then the `--only-binary=:all:` install again |
| pipenv | per name, `pipenv run pip install --no-binary=<name> <name>==<version>`; then the install again |

A name this install did not list as skipped is not run, and `notes` says so. An allowed package leaves `skipped_install_scripts:`.

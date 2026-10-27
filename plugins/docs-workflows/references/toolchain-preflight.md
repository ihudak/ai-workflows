# Toolchain preflight (shared)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names, unless that part is already in this conversation word for word; never guess a part's name — until you hold the index (every part carries it), load it with `args: "<name> index"`. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

Single source of truth for verifying, before a run writes anything, that the tools its gates invoke
are actually present.

Consumed by `/document` (both modes) at Phase 0, and by `/docs-init` at Phase 2 step 3 — which **skips §2's derivation** (its Phase 7 still runs Vale in the form §2, source 2, gives) and hands §3 a fixed set of its own (`git`, `python3`/`pip` or `uv`, `mkdocs`, `vale`). All three of §2's sources are empty for it: there is no profile yet, because it is the run that writes the first one; an absent or empty scaffold target carries no config signals; and it documents no `Prerequisites` of its own until this run has written them. It is the one consumer of the preflight that derives nothing. `/docs-serve` runs no preflight, but its Mode dispatch tests its own tools as §3 tests a tool run through `bash -c` or as `command <name>`, its Phase 2 takes §2's set-aside of a leading `cd <dir> &&` and `VAR=value` words when it compares a recorded command with a process's command line, and its Phase 4 takes §2's definition of a command's tool, and §3's test for one, before it starts a server. Two agents cite it without running a preflight: `docs-style-checker` takes §2, source 2, for the names Vale reads its configuration from and §3 for its linter rung's tool test, and `docs-scaffold-reviewer` takes §2, source 2, for how it runs Vale over a scaffold. Pairs with
`${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md` — the preflight decides whether to start; the ledger
records what actually happened. §2, source 2, is also where this plugin says how it runs Vale.

---

## 1. Why this runs first

A `/document` run started in a container without `vale` and without `pnpm` still produces a branch, a
commit, and a PR draft. No linter ran and no server booted, so the documentation is worse — but the PR
exists and CI is green, and nothing signals that anything went wrong. The failure is silent, and it is
the run's own environment that caused it.

That is knowable at Phase 0 for the cost of one probe per tool (§3). Without a preflight the run
discovers it one gate at a time, at Phase 6.4 and Phase 6.5, after the documentation is written.

## 2. Deriving the required set

Run this **after profile resolution** — the profile is what names the commands. Union three sources;
de-duplicate by binary name.

1. **The resolved profile.** Take the **tool** of every `commands.*` value (including every
   `commands.per_space.<space>.*` value), every `builds[].command`, and every
   `dev_servers.servers[].command`. **A command's tool is its first whitespace-separated token that
   is neither part of a leading `cd <dir> &&` nor a leading `VAR=value` assignment**, set aside in
   whatever order they lead: `"pnpm docs:lint"` ⇒ `pnpm`; `"cd website && pnpm docs:build"` — the
   form `/docs-profile` records for a script found below the top level — ⇒ `pnpm`;
   `"NODE_ENV=production pnpm build"` ⇒ `pnpm`. The first token alone will not do: `cd` is a shell
   builtin, so `command -v cd` exits 0 on every host and every command it leads would read as
   runnable. This is the one definition of a command's tool, and §3 says how each is tested;
   `docs-profiles/render-verification.md` §1 and §2, `/document` Phase 6.5 Steps 1 and 2 and
   `/docs-serve` Phase 4 cite both. Where the profile records any `dev_servers.servers[]` entry, add
   `bash` and `curl` too, and `ps` where `test -r /proc/net/tcp` fails — off Linux: the render smoke
   check that boots those servers starts and stops them under `bash`, probes their ports with `curl`,
   and reads their process groups from `/proc` on Linux and with `ps` elsewhere, and cannot run
   without any of them (`docs-profiles/render-verification.md` §2, **Portability**). Add every entry in
   `profile.prerequisites` as a named prerequisite (these are prose, not binaries — record them for
   reporting, and check them only when the prose names a checkable path or binary).
2. **Repo config signals**, checked at `repo_root` — and, where the caller resolved the site to a
   directory below it, in every directory from that one up to `repo_root`: `/document` keyed mode
   passes `docs_repo_resolved` (its Phase 0 step 2), and direct mode the `site_root` its own Phase 0
   step 3 resolves. A monorepo's site keeps its `.vale.ini`, lockfile and lint configuration beside
   itself or in a directory above it, not necessarily at the top level — a site directory of
   `website/docs` finds `website/.vale.ini` one level up, as Vale's own search, which climbs from the
   directory Vale runs in, finds it. A signal found in any of those directories implies its tool,
   and so does a lockfile in any directory a profile command's leading `cd <dir>` names (source 1),
   taken relative to `repo_root` — that is where the command runs its tool:

   | Signal file | Implies |
   |---|---|
   | a Vale configuration file — any of the five names below | `vale` |
   | `pnpm-lock.yaml` | `pnpm` |
   | `package-lock.json` | `npm` |
   | `yarn.lock` | `yarn` |
   | `.markdownlint.json` / `.markdownlint.jsonc` | `markdownlint` |
   | `.remarkrc*` | `remark` |

   **Vale reads its configuration from five file names, not one** — `.vale`, `_vale`, `vale.ini`,
   `.vale.ini` and `_vale.ini` — and this is where this plugin defines them. In each directory it
   searches, Vale takes the first of them in that order, and the nearest directory holding any of
   them wins over a farther `.vale.ini` (Vale 3.21). So the checks in this plugin that decide
   whether and on what Vale runs — this source, `docs-style-checker`'s first rung and
   `docs-scaffold-reviewer`'s Vale dimension — look for all five: a site whose only one is
   `_vale.ini` is linted by Vale all the same, and a test for `.vale.ini` alone records that no
   repository linter is configured.

   **How this plugin runs Vale — a lint and `vale sync` alike — is defined here too, once: on the
   repository's configuration, with no global configuration file and no `VALE_CONFIG_PATH`, as a
   clean CI runner has neither.** A clean runner has no global
   Vale configuration file and no `VALE_CONFIG_PATH`, and it has Vale's default StylesPath, which
   is where `vale sync` installs a configuration's packages when that configuration sets no
   `StylesPath` of its own. So every Vale run goes from the directory holding the configuration it
   is to read, as one subshell in one Bash call, in one of two forms, chosen by whether that file
   sets `StylesPath` — a `StylesPath` key, written with `=` or `:`, with the case as written,
   above its first `[section]` header, the one place Vale accepts the key (anywhere else it stops
   with `E201`, and a key in any other case it ignores, with `W101`):

   - **It sets one:** `(builtin cd "<that directory>" >/dev/null && unset VALE_CONFIG_PATH && command vale --no-global <arguments>)`.
   - **It sets none:** `(builtin cd "<that directory>" >/dev/null && unset VALE_CONFIG_PATH && h=$(command mktemp -d) && { XDG_CONFIG_HOME="$h" command vale <arguments>; s=$?; command rm -r -- "$h"; exit $s; })`,
     which removes the directory it made and exits with Vale's own status.

   Every part is there for a reason (Vale 3.21, measured, and read from its source). Vale merges
   the user's global configuration file — `~/.config/vale/.vale.ini` on Linux, wherever
   `vale ls-dirs` names it elsewhere — under the repository's, so a style enabled only on this
   machine raises findings the repository's rules never would, a rule turned off only here goes
   silent where a clean runner raises it, and with no repository configuration at all Vale lints
   by the global one alone. `--no-global` drops that file **and Vale's default StylesPath with
   it**: Vale adds its default path only where `--no-global` is absent, so `VALE_STYLES_PATH`,
   which moves that path, does not bring it back. That is right only where the configuration
   names a StylesPath of its own. There a clean runner's default path holds nothing, `vale sync`
   having installed into the repository's, while this machine's may hold styles of its own — and
   a style it holds under a name the repository's also carries has its rules merged into the
   repository's. Where the configuration sets none, its packages and custom styles live in the
   default path, a layout Vale documents as valid, and `--no-global` stops a lint with
   `E100 … style '<name>' does not exist on StylesPath` and `vale sync` with
   `E100 [initPath] … unable to initialize StylesPath`. So the second form keeps the default path
   and sets aside the global file alone: Vale looks for that file under `XDG_CONFIG_HOME`, a
   fresh, empty directory there holds none, and the default StylesPath comes from
   `XDG_DATA_HOME`, or `VALE_STYLES_PATH` where that is set, which the form leaves as they are.
   `VALE_CONFIG_PATH`, where the environment sets it, names a file Vale reads **instead** of
   searching, so the repository's own is never read and `vale sync` installs the packages that
   file names; neither `--no-global` nor `XDG_CONFIG_HOME` stops it, and clearing it in the
   subshell does. The `cd` is there because Vale reads the first configuration it finds in the
   directory it runs in or one above it, never beside the files, and a Bash call starts in the
   session's directory, which need not be the repository's. It is `builtin cd`, its output
   discarded, because the Bash tool's shell carries the user's aliases and shell functions
   (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/render-verification.md` §2, **Portability**): a
   `cd` of the user's would otherwise run in its place, and one that prints would put its output
   ahead of Vale's. `builtin`, not `command`: that shell is bash or zsh, and zsh's `command` runs
   no builtin, only a `cd` found on `PATH` — Linux has none, so `command cd` there is a command not
   found, and macOS has `/usr/bin/cd`, which changes only its own child process's directory, so
   `command cd` there exits 0 and Vale runs wherever the session stands. For the same reason every external
   utility the forms run is `command <name>` — `mktemp`, `vale` and `rm`, whose `rm -i` or `rm -I` alias
   would otherwise ask before removing the directory, be answered no from the Bash tool's empty
   standard input, and leave the directory behind — and `--` ends `rm`'s options. So a `vale` that
   only an alias or a function provides never runs here, which is why §3 tests `vale` by the test it gives a tool the run calls as `command <name>`, not by the one it gives a tool the Bash tool's own shell runs. What neither form makes equal is the
   styles themselves: the packages this machine synced are the versions it synced, and a runner
   syncs its own. **The second form keeps more of the machine than that, and this is its limit.**
   The default StylesPath it keeps is one directory for every project on this machine whose
   configuration sets no `StylesPath`, and Vale reads every configuration file in that
   directory's `.vale-config/`, ahead of the repository's own: the configuration a package ships,
   as `Hugo` and `MDX` do, which `vale sync` writes there after clearing what the last sync into
   that directory left. So it holds whatever the machine's latest `vale sync` into it wrote, for
   whichever project ran it, and until this repository is synced again a lint can raise what a
   clean runner does not, or stay silent where one raises (Vale 3.21: another project's file
   there turning a rule off silenced that rule's alert under this form, and under the first form
   changed nothing). No lint here syncs first to cure it — a sync is a network call and a write into
   a directory other projects read — so the remedy is the operator's: `vale sync` for this
   repository, in this form. `docs-style-checker`'s first rung, `docs-scaffold-reviewer`'s Vale dimension,
   and `/docs-init`'s Phase 4 sync and Phase 7 lint each run Vale this way.

   Separately, when any lockfile is present, check `node_modules/` beside it — or, beside a
   `yarn.lock`, a `.pnp.cjs`, which a Yarn Plug'n'Play install keeps instead — as an
   **installed-dependencies** signal. A present `pnpm` with absent dependencies fails just as
   completely as a missing `pnpm`.
3. **The repo's documented prerequisites.** Grep `repo_root`'s `CONTRIBUTING.md`, `CONTRIBUTION.md`,
   and `README.md` for a heading matching `Prerequisites` (case-insensitive) and read that section.
   Best-effort: extract named tools and minimum versions where stated. Nothing found ⇒ contribute
   nothing. Never fail the preflight on an unparseable Prerequisites section.

**Direct mode has no profile.** `/document` Mode B resolves `repo_root` from **the edit target** — the directory it was given, or an `@file`'s directory — falling back to cwd only where the input names no path at all, and uses
sources **2 and 3 only**. It anchored on cwd unconditionally until a live run showed the consequence: invoked against one repository from inside another, the preflight read the repo it was standing in while the style check ran against the repo it was editing. Source 1 contributes nothing there. `/document` direct mode reads the same guidance files again in the same pass for `${CLAUDE_PLUGIN_ROOT}/references/repo-verification-gates.md` §2 — do both in one read, not two.

## 3. Checking

- **Binaries — each tested by running `command -v` in the shell, and from the directory, that will
  run it.** Every Bash call runs in the Bash tool's own shell, bash or zsh, which carries the
  user's aliases and shell functions — Claude Code's shell snapshot re-applies them — while a
  command the run starts inside an explicit `bash -c` gets a child shell that carries neither; and
  every command the profile records runs from the docs repository, not from the session's
  directory. So whether a tool counts as present depends on which shell asks and where it asks
  from, and the way to find out is to ask **that** shell, from **there** — never to emulate it.
  **This is where the plugin says which test a tool takes**, and the tool checks its gates and
  servers rest on cite this split: `/docs-serve`'s Mode dispatch and Phase 4, `/document` Phase
  6.5's Steps 1 and 2 with `docs-profiles/render-verification.md` §1 and §2, `docs-style-checker`'s
  third rung, and this preflight, `/docs-init`'s included.
  - **A tool the run starts through an explicit `bash -c`, or runs as `command <name>`** — of
    those checked for here: `bash`, which runs every call on a process group as
    `command bash -c`; `curl`, which every probe and request runs as `command curl`; off Linux,
    `lsof` and `ps`, which the process and socket reads run as `command <name>`
    (`docs-profiles/render-verification.md` §2, **Portability**); the tool of every
    `dev_servers.servers[].command`, which `render-verification.md` §2 step 2 and `/docs-serve`
    Phase 4 start inside an explicit `command bash -c`; and `vale`, which every Vale run in this
    plugin calls as `command vale` (§2, source 2) — is asked of a child `bash`, the shell an
    explicit `bash -c` start gets:
    `command bash -c 'builtin cd "<dir>" >/dev/null && command -v "<tool>"'` — present when it
    exits 0. **`bash` takes this test first, whether or not §2 put it in the required set, and an
    absent `bash` ends the form.** The call runs
    *through* `bash`, so with none installed every tool asked this way exits 127 and reads missing
    though it is installed — `vale` among them, and with it a `style_check` the run would have
    passed (measured: on a `PATH` carrying `curl` and `vale` and no `bash`, this form exits 127 for
    both, while the own-shell form below finds both). Report `bash` as the missing tool, once; the
    tools it would have tested were never tested, so none of them is reported missing and no gate
    is predicted from them (§5). That child shell expands no alias of the user's and takes no shell function of theirs
    save one they exported, which it imports and which a start inside one would run too — and a
    tool the run calls as `command <name>` rather than starting inside `bash -c` needs a real
    binary for the same reason, `command` keeping an alias and a function of that name out of it. `command bash` keeps an alias or a function named `bash` out of it, as
    `command` keeps them out of the process and socket reads, and `builtin cd` keeps a `cd` alias
    or a `cd` function out. **A bare `command -v <tool>` in the Bash tool's own shell will not do
    here**: it reports an alias or a function of that name, exiting 0 where the start exits 127.
  - **Every other tool, which a gate runs in the Bash tool's own shell** — the tool of every
    `commands.*` and `builds[].command` value (`/document` Phase 6.5 Step 1's builds,
    `docs-style-checker`'s lint rungs), the tools §2's other signals imply — a lockfile's package
    manager, `markdownlint`, `remark` — and `/docs-init`'s `git`, `python3`, `pip` or `uv`, and
    `mkdocs` — is tested in that same shell, from that same directory:
    `( builtin cd "<dir>" >/dev/null && command -v "<tool>" )` — present when it exits 0. The
    user's aliases and functions then apply exactly as they will when the gate runs the command,
    and `command -v` reports each: a binary's path, a function's name, or an alias's definition,
    in bash and zsh alike. The subshell and the `builtin` are what keep it honest — the
    parentheses leave the session's own directory where it was, and `builtin` runs neither a `cd`
    function nor a `cd` alias of the user's.
  - **`<dir>`, either way, is the directory the command runs from** — `repo_root`, where every
    command the profile records runs, or the directory a leading `cd <dir>` (§2 source 1) names
    under it. That is what resolves a **path-valued** tool, `node_modules/.bin/vitepress` and the
    like, a form a profile may record for a dev-server command: `command -v` resolves a name
    containing `/` against the directory it runs in, so `node_modules/.bin/vitepress dev docs` is
    asked from `repo_root` and `cd website && node_modules/.bin/vitepress dev` from
    `<repo_root>/website`, each exactly as the run will resolve it, and an absolute path resolves
    from anywhere. **Never ask from the session's directory**, which need not be the docs
    repository (§6): a present path-valued tool then reads missing, and the preflight prompts on a
    healthy container (§7). A `<dir>` that does not exist reads the tool missing in both forms,
    which is what the command would meet there too.
  - **A tool that resolves to something that is not there still fails when the gate runs it**, and
    the gate records that as it records any other environmental failure: an alias whose value
    names a wrapper that is not installed passes the own-shell test, exactly as it passes in the
    shell that will expand it. The preflight's job is to catch what it can see from where the
    command will run, not to prove the thing at the end of an alias chain exists.
  - **A tool both kinds run** — a package manager whose builds run in the Bash tool's own shell
    and whose dev servers start inside `command bash -c` — takes both tests, each for the gates
    its own commands power; where the two disagree, the `toolchain` block carries a row for each
    (§4).

  Measured with bash 5.2, with `expand_aliases` on as the snapshot sets it, and with zsh 5.8, each
  as the Bash tool's shell, every form run as the Bash tool runs one and every tool checked against
  the gate that would run it. An alias-provided `mkdocs` in five shapes — an absolute path, one
  beginning `~/`, one beginning with an expansion of the home-directory variable, one led by
  `NO_COLOR=1`, and a chain through a second alias — and a
  function-provided one: the own-shell test and the build it gates agree on every one. An
  alias-provided, a function-provided and an absent `mkdocs`: the child test and the boot that
  child shell makes agree on every one, and so do they on an **exported** bash function, which both
  run. A real `node_modules/.bin/vitepress` under a repository root: from a session directory that
  is not that root, both tests find it and the boot runs it. `command bash` holds against a `bash`
  alias and a `bash` function, and `builtin cd` against a `cd` alias and a `cd` function. What
  these tests still cannot see is narrow, and is named here rather than counted: a zsh **global**
  alias (`alias -g`) on `bash` is expanded in any position, so the test and the start alike run
  something else — one on the tool's own name is no longer a limit, since the test reports it and
  the shell expands it; an **exported** bash function named after a tool the run calls as
  `command <name>` — `vale`, `curl`, and off Linux `lsof` and `ps` — reads present here though
  `command <name>` bypasses it and exits 127; a shadow on `command` itself, an alias or a shell
  function of that name, defeats the `command` prefix these forms rest on, as it defeats every
  other `command <name>` read in this plugin (measured in both shells); and macOS's zsh 5.9 is
  unchecked.
- Directory signals (`node_modules/`): `test -d`; a Yarn Plug'n'Play `.pnp.cjs`: `test -f`.
- Never install anything. Never modify the repo. This step is read-only.

## 4. The `toolchain` block

```yaml
toolchain:
  - tool: <binary name; for a tool containing "/", the path §3 tested; or a directory signal such as "node_modules">
    status: present | missing
    source: <profile.commands | profile.prerequisites | .vale.ini | pnpm-lock.yaml | CONTRIBUTING.md Prerequisites | …>
    required_by: [<gate ids from gate-ledger.md §4 whose primary mechanism runs this tool>]
    fallback_for: [<gate ids whose registered fallback runs it>]   # omitted when there are none
```

`required_by` and `fallback_for` map each tool onto the gates it powers, which — with §5's per-build
test for `build_check`, whose fallback depends on which build's servers a tool serves — is what lets
the preflight predict the run's outcome before the run (§5 says what that prediction assumes):

| Tool | Typically required by | Fallback for |
|---|---|---|
| the repo's prose linter (`vale`, `markdownlint`, `remark`) | `style_check` | — |
| the package manager (`pnpm` / `npm` / `yarn`) | `style_check`, `build_check`, `render_smoke_check` | `build_check`, where a dev-server command runs it |
| installed dependencies present (`node_modules`, or a Yarn Plug'n'Play `.pnp.cjs`) | every gate the package manager powers | as the package manager |
| `git` | `source_truth_verification` | — |
| `bash`, `curl`, and off Linux `ps` (the smoke check's own tools) | `render_smoke_check` | `build_check` |

Derive both from where the tool came from, a tool being a command's tool as §2 source 1 defines it:
the tool of a command `build_check` runs — a `builds[].command`, `commands.build`, or
`commands.per_space.<space>.build` (`docs-profiles/render-verification.md` §1) — powers
`build_check`; the tool of a `dev_servers` command powers `render_smoke_check`, and so do `bash`,
`curl` and, off Linux, `ps`, which that check runs itself. **Those same tools also run `build_check`'s
registered fallback** — the Step 2 dev-server boot that stands in for a build that will not run
(`gate-ledger.md` §4) — so each of them carries `fallback_for: [build_check]`. A tool with an empty
`required_by` is reported but never blocks.

A tool §3 tests both ways — one a build or lint command and a dev-server command both run — takes
one row where the two tests agree, and two where they do not: **one row per test, each carrying the
gates the commands that take that test power, and each row's `status` that test's own answer**. The
own-shell test's row carries the gates its build and lint commands power; the child-shell test's row
carries the gates its dev servers power — `render_smoke_check` in `required_by`, `build_check` in
`fallback_for`. **Which of the two is the `present` one is whatever the tests say, and both ways
round are reachable.** A `pnpm` that only a shell function of the user's provides is present to
their own shell and missing to the child: the dev-server row is the `missing` one, predicting
`render_smoke_check` `DEGRADED`, and the build and lint row is `present`, leaving the builds it runs
to run. A tool that only an **exported** bash function provides, on a host where the Bash tool's
shell is zsh, is the other way about — zsh takes no bash function out of the environment, while the
child `bash` imports it and runs it (measured, zsh 5.8): the build and lint row is the `missing`
one and the dev-server row the `present` one, and each is right about its own commands. Never
derive a row's `status` from the kind of gates it carries.

## 5. Reporting and the prompt

**When every required tool is present, say nothing beyond one line in the caller's readiness output.**
A preflight that prompts on a healthy container becomes one more thing to click through, and dies the
way the Phase 6.4 gate died.

When one or more required tools are **missing**, print the `toolchain` rows (missing first), then the
consequence — each affected gate and the outcome it is predicted to record: `DEGRADED` where the gate's
registered fallback (`gate-ledger.md` §4) still runs without the missing tool, and `UNAVAILABLE`
where neither the primary nor the fallback can (`gate-ledger.md` §2). A gate is affected where a
missing tool's `required_by` names it. Its fallback still runs where no missing tool's
`fallback_for` names it — except `build_check`'s, which is decided **per build**, by the test
`/document` Phase 6.5 Step 1 makes when that build will not run: a build that will not run keeps its
fallback — the Step 2 boot of **that build's own servers** — where `bash`, `curl` — off Linux, `ps`
too — and the tool of one of those servers (§2, tested as §3 tests it) are all present, and never on
the strength of another build's server, which compiles another space or another configuration. In
this test a package manager whose installed dependencies are missing counts as missing, by the rule
`docs-profiles/render-verification.md` §2 step 1 states for the tool check, for a build and a server
alike, since it fails as completely. `build_check` is
`DEGRADED` where every build that will not run keeps its fallback, and `UNAVAILABLE` where any does
not. A build's own servers are the ones Step 1 names — for a `builds[]` entry, the server whose
`visibility` pairs with the entry's; for a space's `commands.per_space.<space>.build`, that space's
servers; for the flat `commands.build`, every server — taken here from every server the profile
records for it, since no page is written yet, where Step 1 counts only those Step 2 boots for an
affected page. So with the build tool and `curl` both missing, `build_check` is `UNAVAILABLE`, not
`DEGRADED`, because the boot that stands in for the build probes its server with `curl`; and where
one space builds with a missing `mkdocs` but serves through a present `pnpm` while another space's
server tool is missing, it is `DEGRADED`, because the build that will not run keeps its own server's
boot.

**A profile that records no build command at all** — no `builds[]`, no
`commands.per_space.<space>.build`, no `commands.build` — gives `build_check` no primary, so no
tool's `required_by` names it. The gate still applies: its precondition is a buildable write context
(`gate-ledger.md` §4), not a build command, and the Step 2 boot is then its only proof
(`docs-profiles/render-verification.md` §1), so it records `UNAVAILABLE` wherever that boot cannot
run. On such a profile `build_check` is therefore affected wherever a missing tool's `fallback_for`
names it, and is decided as one build that will not run, whose own servers are every server the
profile records: `UNAVAILABLE` where `bash` or `curl` — or, off Linux, `ps` — is missing or every
server's tool is, `DEGRADED` otherwise.

**What the `build_check` prediction assumes.** The preflight runs before any page is written, so it
cannot know which servers Step 2 will boot. It assumes that, for every build that will not run,
Step 2 will boot one of the servers that kept that build's fallback here — that one of them
publishes an affected page. Where none does — the build whose tool is missing is the internal one,
and every affected page is published by the public server — Step 1 finds none of those servers
among the ones Step 2 boots, so the build's fallback cannot run. The row
then records the decision the user takes at this prompt, `SKIPPED_BY_USER` (or `FAILED` with that
decision beside another build's content failure, `gate-ledger.md` §2), where the consequence line
predicted `DEGRADED`. The line is a prediction from the profile alone; Step 1 and `/document`'s
Ledger (final) record what the run found. No question is asked twice either way, since Step 1 keeps
the decision this prompt records.

Then ask, the question's own text carrying the consequence — each missing tool and each affected
gate with the outcome it is predicted to record — since *Continue anyway* records exactly those
(`workflows-core:epic-picker` *The cap*):

```
choices: ["Cancel — re-run in the docs container (Recommended)", "Continue anyway — record the degraded gates"]
```

Example consequence line:

> With `vale` and `pnpm` missing, this run would record `style_check` **DEGRADED** (only
> `prose-style-checker` runs; the repo's own linter would not),
> `build_check` **UNAVAILABLE** (its fallback, the dev-server boot, runs `pnpm` too), and
> `render_smoke_check` **DEGRADED** (no server can start without `pnpm`, so every affected page goes
> to the manual pages-to-visit table, the fallback that needs no tool).

The line names a linter or a build CI runs on the pull request only where the repository's CI runs
it, as a `ci_still_checks` line does (`gate-ledger.md` §6).

- **"Cancel"** → stop the run. This check has written nothing; where `/document`'s inline profiling wrote before it, committing a generated profile on a branch, `/document`'s own stop says what it left.
- **"Continue anyway"** → for each gate named in the consequence line, **pre-seed** its ledger row's
  expected outcome and carry the user's choice verbatim, so that when the gate is reached its row
  records `SKIPPED_BY_USER` (or `DEGRADED` where a fallback does run) with `user_decision` already
  attributed. A pre-seeded row is still overwritten by what actually happens — a tool that turns out
  to work records `RAN`.

The preflight is itself a ledger gate: `toolchain_preflight`, phase 0, no fallback. Record its own row
(`RAN` when the check completed, whatever the findings; `FAILED` only if the check itself could not be
performed).

## 6. Location reporting

The caller has already resolved its target repo. The preflight does not re-resolve it — it reports
`repo_root`, and when `repo_root` differs from cwd it says so on its own line. **A divergence by
itself never prompts**: writing into `${DOCS_PATH:-/workspace/docs}` from a different working
directory is the normal AI-container case.

## 7. Hard rules

- NEVER install, upgrade, or configure a tool. Report and ask.
- NEVER modify any file under `repo_root`.
- NEVER prompt when every required tool is present.
- NEVER move the `(Recommended)` marker off "Cancel" in §5 — the "Choice lists are presented verbatim"
  rule in `workflows-core:escalation-rules` binds this prompt.
- NEVER fail the run because a `Prerequisites` section could not be parsed; source 3 is best-effort.
- NEVER treat a tool with an empty `required_by` as blocking.

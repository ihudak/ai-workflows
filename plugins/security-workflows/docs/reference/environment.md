# Environment reference

[Getting started](../getting-started.md) says what the variable is *for* and what to export before your first run. This page says what it **is**: where its value comes from, what happens when it is unset, and what happens when it points somewhere the plugin cannot use. The plugin reads one user-settable variable. The other names its own inventory check meets while scanning for `$VAR` reads are never user-settable: `CLAUDE_PLUGIN_ROOT` and `ARGUMENTS` are runtime plumbing Claude Code sets for every plugin invocation. The run flags' environment defaults, `WORKFLOWS_SKIP_COSTS`, `WORKFLOWS_SKIP_FEEDBACK` and `WORKFLOWS_ENFORCE_MODEL`, are read by `workflows-core`, whose own environment page documents them.

## `SPECS_PATH`

- **`SPECS_PATH`** is the shared, team-visible specs repository: the findings register lives in it, a run addressed by a key resolves its unit's folder in it, and every run commits its session bookkeeping there. Every run needs it, and it has no built-in default.

**Resolution.** Read from the shell environment, and tested at Phase 0 step 3, after the arguments are parsed and before anything is resolved, because the register lives under it on every run. Every git call against it is `git -C "$SPECS_PATH"`, never a `cd`, so the code repository the session stands in is untouched.

**When unset.** Where it is unset, or names no existing directory, the run stops naming it and asks: *Set SPECS_PATH*, which takes the path in plain text, carries it for this run once it names an existing directory, and asks again where it does not; or *Cancel*, which ends the run. A path set this way lasts for the run only; set the variable where you set your others to keep it.

**When it is misplaced.** `$SPECS_PATH` is the root of a dedicated specs repository, the directory that holds `specifications/`, never `specifications/` itself nor a folder inside it. A run addressed by a key resolves it with `workflows-core`'s address resolution, which stops with `SPECS_PATH_INSIDE_TREE` where `$SPECS_PATH` sits inside a specs tree, naming the value to set. Every run then runs the specs-repo preflight, and where that finds `$SPECS_PATH` misplaced the run stops with `SECURITY_SPECS_MISROOTED` before it writes anything: no scan folder, run record, unit note or follow-up. The register can be read in such a place but not written, so a run there would record nothing.

**When it cannot be committed.** Where the preflight finds the specs checkout on a detached HEAD, the run carries `specs_git: blocked`: the register is still written, and the terminal commit leaves it uncommitted and says why. Where the specs repository's default branch takes no push, the register travels on your own session branch, as every session file does, and reaches the default branch when that branch's pull request merges; no run waits for that ([Security register](security-register.md)).

**When it has no remote.** A run fetches the specs repository's `session/*` branches to reserve the finding numbers other runs have taken, and fetches nothing where `origin` has no URL or the specs repository is a read-only mount. That fetch never stops the run; one that fails or times out is named in the report's `### Register` section, and the refs are read as last fetched.

**When it changes under a resumed conversation.** The specs-repo preflight first prints one line, `Environment: SPECS_PATH=<real path> (origin <url|none>), REPOS_PATH=<value|unset>`, and the conversation carries it wherever it is resumed. Before each write of the run's tail — its feedback, the follow-ups, the cost entry, the resume pointer — the run compares the environment it now stands in with that line. Where they differ — a conversation resumed in another container, with `claude --resume` or a continuation — it prints `Environment changed: …` once, naming both, and from there records and commits nothing more in the specs repository, without asking: those entries stay in the printed output, and the terminal commit is skipped. The register and the unit note, written in Phase 7 before the tail, are not covered: they land where `$SPECS_PATH` names at that moment, and stay there uncommitted. Re-run in the container the run started in.

**What lives under it.**

- `security/<repo-slug>/` holds one code repository's register: its scans, its run records, the derived `register.json` and `register.md`, and the cost entries of the runs on that repository that had no key. [Security register](security-register.md) describes the layout.
- `_security.md` in a PRD or Epic folder is the unit note a run addressed by a key appends to.
- A run addressed by a key files its cost entry under the unit's PRD folder ([Session cost](session-cost.md)).

**What the plugin does not read.** There is no `REPOS_PATH` here: the preflight's `Environment:` line above names its value, as it does wherever the preflight runs, and nothing in a scan uses it. A run addressed by a key scans the code repository this session is open in, `git rev-parse --show-toplevel` from the working directory; a run addressed by a path scans that path's repository; and `--import <dir>` takes the repository holding `<dir>`.

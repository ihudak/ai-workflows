# Bounded run (shared reference)

Single source of truth for running a command under a time cap on every host. macOS ships no `timeout` binary, so a call written as a bare `timeout <N>s <cmd>` fails there with `command not found` — and a caller that reads a failed call as "skip" (a slug→clone map skipping a directory, a qmd probe dropping to the fallback) then silently skips everything.

A cap the Bash tool's own timeout holds — `docs-style-checker`'s linter pass, `guideline-reviewer`'s ESLint run — needs no wrapper, and is never written as a `timeout` prefix either. Consumers: every command, agent and reference that caps a call in the shell — the slug→clone maps and clone-identity lines of `/dev-workflows:design`, `/dev-workflows:ready`, `/docs-workflows:document`, `/docs-workflows:release-notes`, `/product-workflows:create-ard`, `/product-workflows:epics`, `/product-workflows:idea`, `/product-workflows:prd-ground` and `/product-workflows:specify`; `workflows-core:components` §1; `workflows-core:docs-grounding` step 3.5; and `docs-grounder`.

## The call — `scripts/bounded.py <seconds> <command…>`

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bounded.py" <N> <command…>
```

with `<N>` the cap in whole seconds — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bounded.py" 5 git -C <dir> remote get-url origin 2>/dev/null`. It is a script, called by its path like every other, so a run that has never read this file runs it all the same. `${CLAUDE_PLUGIN_ROOT}` is the plugin whose file makes the call — a command's own plugin, and `workflows-core` for this plugin's references and agents — so `workflows-core`, `dev-workflows`, `docs-workflows` and `product-workflows` each ship the same `scripts/bounded.py`, and CI fails a copy that differs from `workflows-core`'s.

- **The Bash tool call** that runs it sets the tool's timeout to at least (N+5)·1000 ms, so the cap fires before the tool kills the call.
- **The command** inherits stdin, stdout and stderr and runs in a session of its own — a process group of its own, with no controlling terminal. The cap ends that group whole: SIGTERM, then SIGKILL two seconds later for whatever of it is left, so nothing the command started outlives the cap. A SIGTERM, SIGHUP or SIGINT sent to the script is passed on to the group the same way, as GNU `timeout` passes it on. A command that exits by itself before the cap leaves what it started in the background running, as under `timeout`.
- **Exit codes**, as GNU `timeout` reports them: `124` the cap ended the command; `127` it was not found; `126` it could not be run; `128 + N` signal N ended it; `2` a usage error; anything else is the command's own. A caller that does not tell a timeout from the command's own failure treats both as a failed call.
- **It takes the same branch on every host that has `python3`** (3.9 or newer), a prerequisite the repository's README lists: every bundled script needs it. On macOS it comes with the Command Line Tools, as `git` does, so a host that can run the slug→clone maps' `git` can run this. A host without it gets exit 127 from every capped call, as it would from any of the plugin's scripts. It is tested in CI by `python3 scripts/bounded.py --selftest` (21 cases): the exit codes; stdin, stdout and stderr passed through; a command that ignores SIGTERM, starts a child that ignores it, or starts a child of its own; and a signal sent to the script.

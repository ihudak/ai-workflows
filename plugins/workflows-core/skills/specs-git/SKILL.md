---
name: specs-git
description: Runs a command's specs-repository start and end (specs-preflight, commit-artifacts) through specs-git.py, and says which of its lines to print and where.
user-invocable: false
allowed-tools: Bash, Skill
---

# specs-git — a run's specs-repository start and end

The argument names the entry point: `start`, `end` or `declined`. `workflows-core:specs-repo-git` §3 to §8 are the rules, and `${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py` runs them and asks nothing. This text is what your run executes; it never reads that reference to run its start or its end. A run that another command started `--inline` (`/docs-brand` under `/docs-init`) calls none of this.

## The call

Each call is one Bash call, with a timeout of 600000 ms:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" --specs "${SPECS_PATH-}" <start|end> --command /<name> …
```

Where your run took `$SPECS_PATH` from the *Set SPECS_PATH* answer, open the call with `export SPECS_PATH='<the value>';`. Pass:

- `--command /<name>` — the command now running, as its commit message names it: `/create-ard`, `/scan`, `/feedback` — the slash and the name, never the plugin.
- `--key <K>` (start), once for each key of the run key set, as `${CLAUDE_PLUGIN_ROOT}/skills/specs-git/run-key-set.md` defines it — read that file before your first start call, unless its text is in this conversation word for word. Where your command's start paragraph names its key set, take its words.
- `--commit-key <K>` (start and end) — the one key the run addressed: an Epic run's own key, never its parent's; a slice's key; where several, the first resolved. At start, only where it is already resolved. At end, the key your command's commit paragraph names for `<KEY>`. Omit it for none; the commit then reads `NOISSUE`.
- `--register-rebuild <path>` (start and end) — only where your command hands `register_rebuild`: that path.
- `--rerun` (start) — only on a second start in one run with a changed key set: `/document` and `/release-notes`, after the operator entered a slice key at their BRD-container stop.
- `--no-preflight` (end) — where your run stopped before its start call.
- `--misrooted-stdin` (end) — where your run carries `specs_git: misrooted` from anything but this skill's start — `specs-root-check`'s `SPECS_PATH_INSIDE_TREE:` stop, `env-check`'s `Environment changed:` line, or `session-hygiene` §6's `RESUME_ENVIRONMENT_CHANGED:` line — with that notice, verbatim, on stdin: `<<'EOF'`, the notice, `EOF`.
- `--session-branch-created <sha7>` (end) — where a session-branch `commit` or `lift` that your command, or its handoff, ran printed `created: true` (`/implement` keeps it as run-state `session_branch_created`): the `<base short sha>` taken then.
- `--declined '<path>'` (end), once for each path — only where a `declined` call below could not run.

## Start

Make the call where your command's start step stands, once its run key set is known. Then **print every entry of the JSON's `print`, verbatim and in order, as your next output** — the `Environment:` line first, then each notice or line, an entry of several lines inside a `text` fence. These are the lines your command's text tells you to emit at its preflight: print each once. For the rest of the run, read the preflight's results from the last `start` JSON — the first call's, or the last `start --resume` a `next` led to: `specs_git` (`blocked` or `misrooted`), `default`, `default_ref`, `remote`, `offline` and `offline_clause`, `session_branch`, `branch`, `b2_left` and `merged_stay` — wherever your command's text reads them, and `merged_stay` wherever you run your end by hand (below). A `replaced` field names a record an unfinished earlier run of this command left in this session; it changes nothing you do.

## End

Make the call where your command's commit step stands: its last action, or the step before a phase that hands the session elsewhere. Its `print` is any line that comes before the run's `Specs repo:` line — a failed catch-up's, say — then that line, then any notice it repeats, then any line that follows it. Put them where your command says — in its final report, or here as the run's last output — verbatim, in order and once; nothing after them restates the report.

## When the JSON names `next`

Print that call's `print` first. Then run `next.run` exactly as given, as a Bash call of its own with `next.timeout_ms` as its timeout, and treat what it returns the same way, until `next` is null. Where such a call ends with no exit status of its own — the harness stopped it at its timeout — run `next.on_timeout`, or, where that is null, the same call again. Where a first `start` or `end` call ends that way, make it again with `--resume` added.

## Declined

Where a handoff's consent choice is answered with its second or third option, run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/specs-git.py" declined --command /<name> --path '<path>'`, one `--path` for each path of that handoff's `deliverable_paths`. It prints nothing for you to show. Where it exits 2 on a line that does not begin `specs-git: not run (usage:`, keep the paths and pass them to your end as `--declined`.

## Where the script cannot start

Exit 2 means it did nothing: one `specs-git: not run (…)` line on stderr. Where that line begins `specs-git: not run (usage:`, your call was wrong: correct it and make it again. Otherwise print the line and run this entry point by hand from the reference — `Skill(skill: "workflows-core:reference", args: "specs-repo-git")`, then its §3 for start or its §4 for end — and, where this is your start, run your end by hand too. Where this is your end and the script ran your start, the merged-branch stay §4 step 1 reads is that start's `merged_stay` field. JSON with `error` set did part of its work and says so in `print`: print it and go on; never run that entry point again by hand.

## Citations

Which citations of `workflows-core:specs-repo-git`, by name or by its file's path, this text and the script's output serve, and which still read the reference, is the `reference` loader's paragraph on `specs-repo-git`. The run key set is `run-key-set.md`, beside this file.

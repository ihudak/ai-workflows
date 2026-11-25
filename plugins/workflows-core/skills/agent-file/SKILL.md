---
name: agent-file
description: Prints the absolute path of a workflows-core agent's definition file, for a sibling plugin's command that saves that agent's dispatch in its run folder.
user-invocable: false
allowed-tools: Bash
---

# agent-file — a `workflows-core` agent's definition file

The argument is one agent's name, as `subagent_type: "workflows-core:<agent>"` names it: `code-scanner`, `doc-fixer`. A command in another plugin needs that agent's file to save the agent's dispatch in its run folder — the `--agent-file` of `workflows-core:run-folder`'s `run-dispatch` and `run-writer`, and the file `changed-agents` passes — and its own `${CLAUDE_PLUGIN_ROOT}` names its own plugin, not this one. This text is what your run executes: it reads nothing more.

## The call

Where the argument does not match `^[a-z0-9-]+$` — it is empty, or holds a space, a `.`, a `/` or a quote — make no call: the skill's result is nothing.

Otherwise make one Bash call, `<agent>` being the argument:

```bash
test -f "${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md" && printf '%s\n' "${CLAUDE_PLUGIN_ROOT}/agents/<agent>.md"
```

## What it prints

- **A path** — the agent's definition file. Pass it, between single quotes, as `--agent-file` for every dispatch of that agent this run saves, and as `<file>` in `changed-agents`' `--agent <agent>=<file>`. Call the skill again for that agent only where this line is no longer in front of you.
- **Nothing** — no such agent ships here (the call exits 1 and prints nothing), or the argument was refused. That is no error, and you print no `NOTE:`: the dispatch runs unsaved, as it does without a run folder, with no `dispatch`, `writer` or `done` call for it.

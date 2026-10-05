# /diagnose-session

Reads a session's transcripts on disk and reports what happened in a run of this plugin family that went wrong — repeated work, an ignored plan, stumbles, a step that did not fire, a run too slow or too expensive — with a `path:line` citation behind every finding.

## Who runs it

Whoever wants to know why a run went the way it did: the engineer who ran it, or the family's maintainer reading a report someone else wrote. It runs outside the role pipeline, at any time, on the current session or a past one, and it is charged to no phase: it emits no session-cost entry, dispatches no maintenance agent and routes no model. [Workflow overview](../workflow.md#cross-cutting-commands) groups it with the commands that improve the plugin family; where `/feedback` logs a note in your words, this command finds the evidence for one.

## Synopsis

```
/workflows-core:diagnose-session [<session-id> | <transcript path>] [<what went wrong>]
```

A token naming an existing file or directory is the session's path; a token shaped like a session id is looked up in the harness's session store; with neither, the session is the current one. The rest is your description of what went wrong, where the problem intake starts. The three run flags are accepted and reported as not applicable.

## What it needs

- **A problem statement you agree to.** Phase 1 asks one question at a time until it can name the session, the turn range if you know it, what you expected, what happened, and what you care about — wall-clock, tokens, repeated actions, or one specific action. *"It took too long"* is where that starts, not where it ends. A request already scoped to one event, or to what a running session is doing now, is its own statement. Nothing is read until you have answered.
- **The session's transcripts**, readable on this machine. For Claude Code they are under `~/.claude/projects/<cwd-slug>/`, with each session's subagent transcripts beside it; the current session is the newest transcript there that holds this run's own invocation, so another session running in the same directory is not mistaken for it. A past session is confirmed by quoting its first prompt and timestamp, never by recency alone.

## What it produces

A case directory per run, `~/.claude/workflows-core/diagnoses/<session-id>-<timestamp>/`, outside every repository, holding:

- **`case.md`** — the agreed problem statement, the session files with their sizes, the environment the records show, and the record meanings and extraction commands every reader uses.
- **`report.md`** — the verdict, a `path:line` after every claim and a confidence; the sessions examined; a timeline with one row per prompt; the findings of seven dimensions — timeline, plan adherence, repeated work, stumbles, claims and evidence, conflicting instructions, cost and time; the family's involvement; and what was not read.

The family's involvement is `not indicated`, `possible` or `likely`, with the command, phase, agent or reference the evidence touches, named as a location. The report never proposes a fix: where involvement is possible or likely, the final report prints a ready-to-run `/workflows-core:feedback` line carrying a summary redacted as feedback is, and you decide whether to log it.

It never writes to `$SPECS_PATH`, never commits anything, and never modifies a session file.

## Gates

No reviewer. The safeguards are rules every reader follows: measure a transcript before reading it and never print a record whole, since one line can exceed a megabyte; read only the paths the case file names; and drop any finding that cites no `path:line`, or whose cited line does not show what it says. Phase 3 dispatches seven `session-analyst` agents in parallel, one per dimension (split by line range on a long transcript); a dimension whose analyst could not run is named in the report's coverage, never written by the orchestrator.

## Example

```
/workflows-core:diagnose-session "the /implement run re-ran the whole test suite three times before the review"
```

The run asks which session and which turn, confirms the problem statement with you, locates the transcripts, writes the case file, dispatches the seven analysts, checks the lines its verdict rests on, and writes the report — then shows it, with its path.

See [`references/session-diagnosis.md`](../reference/references.md) for the rules it follows.

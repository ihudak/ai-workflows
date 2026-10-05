# Session diagnosis (embedded authority)

The rules `/diagnose-session` and `session-analyst` follow when they read a session's transcripts on disk to say what happened in a run of this plugin family that went wrong. Adapted from superpowers' *diagnosing-superpowers* skill.

**The command reports; it does not diagnose the plugin.** Every finding cites the `path:line` it rests on, and every number comes from the transcript or from a command run against it, never from memory. A report says whether the family was involved (§7) and stops there: what to change is the maintainer's call, made through `/feedback` or the family's repository, never by this command.

## 1. Context safety

One transcript line can exceed a megabyte, or embed a whole earlier history. Printing one can overflow the context of whoever reads it. Every reader of a session file, the command and every analyst alike, follows these rules for every file, every time:

1. **Measure before reading.** `wc -lc "<file>"`, and the long lines: `awk '{ if (length($0) > 100000) print NR, length($0) }' "<file>"`.
2. **Never print a record whole.** Never `cat` a session file, and never `grep` one for its content. Find line numbers and counts first (`grep -n … | cut -d: -f1`, `jq -r '.type' "<file>" | sort | uniq -c`), then extract small fields from named lines (`sed -n '<N>p' "<file>" | jq -c '{…}'`, or `| cut -c1-500`), using the extraction commands the case file records (§3).
3. **Narrow anything over 500 characters.** A command that returns more than 500 characters for one record gets a tighter field or a shorter slice.
4. **Read-only.** Never modify, move or delete a session file.

## 2. Locating a session

**Resolve each session to verified absolute paths.** A path the user supplies is used as given, once it exists. A session id is looked for under the harness's session store. With neither, the session is the current one.

**Claude Code's store** — starting points observed in its transcripts, which every run verifies against the records in front of it rather than assumes, since a later Claude Code may write them differently:

- **Main transcript:** `~/.claude/projects/<cwd-slug>/<session-id>.jsonl`, `<cwd-slug>` being the absolute working directory with every `/` and `.` replaced by `-`. **The current session** is the newest `*.jsonl` there **whose last records hold this run's own invocation** of `/diagnose-session`; the newest file alone is not enough, since another session may be running in the same directory.
- **Subagent transcripts:** `~/.claude/projects/<cwd-slug>/<session-id>/subagents/agent-*.jsonl`, each beside an `agent-*.meta.json`. A tool result too large to keep inline may sit under `<session-id>/tool-results/`.
- **Record meanings:** each line is one JSON record with a `type`. A `type: user` record whose `.message.content` is a string is typed text, which is the user's prompt, a command invocation (`<command-name>` tags), or harness-injected text (`isMeta: true`; a compaction summary carries `isCompactSummary: true`; a `<task-notification>` or `<local-command-caveat>` is the harness's, not the user's). A `type: user` record whose content is an array of `tool_result` blocks is tool output. A `type: assistant` record carries `.message.content` blocks (`text`, `thinking`, `tool_use`), `.message.model` and `.message.usage`. A `type: system` record's `subtype` names an event: `compact_boundary`, `turn_duration`, `stop_hook_summary`, `local_command`. Every record carries a `timestamp`.
- **Usage counts once per API message.** One API response is written as several `type: assistant` records sharing one `.message.id`, each repeating `.message.usage`: in a subagent transcript the first is often a streaming partial with a few output tokens, and a later record carries the final usage. Count each message id once, at the record with the most output tokens. A record whose usage is missing is unknown, never zero.

**Another harness** has its own store; GitHub Copilot CLI, for one, keeps a directory per session under `~/.copilot/session-state/`. Find it from the harness's own documentation, help or configuration, or by bounded inspection of the filesystem, and record what was found as the case file asks. Never assume one harness's format in another's files.

**Confirm identity.** A past session is confirmed by quoting its first human prompt and its first timestamp, never by recency alone. Name every candidate rejected, with the reason, or `none`. Where the evidence cannot tell two candidates apart, ask the user for what would.

**Enumerate the session's subagent transcripts**, each with the line in the main transcript that dispatched it where one can be found.

## 3. The case file

`/diagnose-session` writes `case.md` into the run's case directory before any analyst runs, and every analyst reads it first. It holds:

```markdown
# Case: <session-id>

Case directory: <absolute path>
Created: <ISO timestamp>

## Problem statement

<One paragraph, agreed with the user: the session, the turn range if known, what was expected, what happened, and the observable that matters — wall-clock, tokens, repeated actions, one specific action.>

## Sessions

| Role | Session id | Absolute path | Lines | Bytes | Longest line (bytes) | First prompt (first 120 characters) | First timestamp |
|---|---|---|---|---|---|---|---|

Rejected candidates: <id — path — why>, or "none".
Still running when read: yes | no (<mtime>, <lines>)

## Environment

- Harness and version, where a record or a command shows it: <value, or "unknown">
- Models seen: <model id — where>
- Family plugins seen: <plugin@version — the record or path that shows it, or "unknown">
- Instruction files the session loaded (paths only): <list, or "none found">

## Record meanings

- Extraction commands: <the bounded commands every reader uses>
- Human prompts: <how they are told apart from injected text and tool results, with a line that shows each>
- Tool calls and results: <how a call is matched to its result>
- Usage: <the fields, and the once-per-message rule as verified here, or "unavailable">
- Timing: <the fields and their units, or "unavailable">
- Compaction and resume: <where they are recorded, or "none found">
- Unresolved: <what could not be established, or "none">
```

Label every environment value with where it came from: a record in the session, a command run now (which is today's state, not the session's), or `unknown`.

## 4. The seven dimensions

Each analyst works one dimension over the files the case file names, within a line range where the brief gives one, and reports only what the records show. A missing step is reported as missing; whether it was wrong is the reader's call.

1. **Timeline.** One row per human prompt: its line, its time, and what ran in that turn — the family's commands (their invocation records), the agents dispatched (`subagent_type` on the dispatching `tool_use`), the skills invoked, including each `workflows-core:reference` load and its `args`, and the hooks that fired. Where a family command ran, read its text at the version the session ran (a skill or reference load records the install directory it read from) and report each step that text says runs at that point with no record of it.
2. **Plan adherence.** Recover the agreed plan: a plan or design the user approved in the conversation, a plan or spec file written in the session, a todo list, or a numbered checklist in the assistant's text, each step quoted with its `path:line`. Map each step to what ran, and report steps skipped, run out of order, changed without saying so, or added with no step behind them, and any drift right after a compaction or a resume.
3. **Repeated work.** Group the tool calls by tool and key — the path for a read, edit or write; the whole command for a shell call; the description and the first 80 characters of the prompt for a dispatch; the query for a search. Report a group at or over its threshold: 3 reads or searches, 2 edits, 2 shell commands (status checks and test runs exempt), 2 dispatches with one description. Say what came between the repetitions — a write to that file, a compaction, a correction from the user, or nothing — and report a conclusion the assistant reached twice, quoting both places.
4. **Stumbles.** Every point where the run stopped going forward: a tool result marked as an error, a failed command, a retry of the same call in the same turn, an edit later undone, the assistant backtracking in its own words, a user correcting the step before, a permission denial, a hook failure, an API error or overload, an aborted turn, and a compaction mid-task. For each: its line, what failed, and what followed — recovered in the same turn, recovered later at line N, or never. Group identical repeated failures, with a count.
5. **Claims and evidence.** Not a review of what the session built. Each test run with its result; each claim of *done*, *fixed*, *passing* or *verified* with no tool result in that turn that shows it; each commit whose message claims work no tool call did; each reviewer finding acknowledged and not acted on, or dismissed with no reason given.
6. **Conflicting instructions.** Two of the user's instructions that cannot both hold; a user instruction against an instruction file the session loaded; an instruction to skip or override a step, a rule or a review, and what happened after. Quote both sides and report what the assistant did. Who was right is not this dimension's call.
7. **Cost and time.** Tokens per turn and per subagent transcript, counted per §2's once-per-message rule, with the five largest turns; wall-clock per turn from the timestamps or the recorded turn durations, the five longest, and every gap over ten minutes; the ten largest tool results by size; each compaction, with what the run was doing when it fired; and each subagent with its tokens, its duration and the turn that dispatched it. Where the family's own cost entries cover the window, compare with them and say where they disagree.

## 5. Findings

An analyst returns exactly this, and nothing else:

```markdown
## <Dimension> findings

- finding: <one sentence: what happened>
  evidence: <absolute path>:<line> — "<quote, at most 200 characters>"
  turns: <first human turn>–<last>
  confidence: high | medium | low

Checked: <the files, line ranges and commands examined>
```

A dimension with nothing to report returns `- none found` and its `Checked:` line. **A finding with no `path:line` is discarded** by the command, so an analyst never writes one.

## 6. The report

`/diagnose-session` writes `report.md` into the case directory, filled in this order, every section present:

1. **Problem statement** — as the case file has it.
2. **Verdict** — what the evidence shows happened around the reported problem, in prose, a `path:line` after every claim, with a confidence (high, medium or low) and what would raise it.
3. **Sessions examined** — the case file's table, without its first-prompt column.
4. **Environment** — the case file's section, each value labelled with where it came from.
5. **Timeline** — one row per human prompt: turn, line, time, the request in one line, and the events (commands, agents, compactions, errors, aborts).
6. **Findings** — one subsection per dimension, in §4's order, each finding as §5 gives it, or `none found — checked: <what>`.
7. **Family involvement** — §7.
8. **Coverage** — the ranges and files not read, and why; harness records that were unavailable; whether the session was still running; and what the user should check for themselves.

## 7. Family involvement

One of `not indicated`, `possible` or `likely`, with the evidence lines, and the command, phase, agent or reference whose text the evidence touches, named as a location. **It names no defect and proposes no edit**: a finding that the plugin did something is evidence for whoever decides what changes, and a suggested fix in a report would be read as a decision already made.

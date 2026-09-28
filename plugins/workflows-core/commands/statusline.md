---
name: statusline
description: Install the plugin family's multi-line status line (session identity, git, context bar, cost, tokens, rate limits) into your Claude Code settings. Vendors the script to a stable per-user path, backs up anything it would overwrite, and enables the Option B cost snapshot used by session cost reporting.
allowed-tools: Read Write Edit Bash
---

Install the plugin family's status line: $ARGUMENTS

`/workflows-core:statusline` installs the plugin's multi-line, truecolor status
line and wires it into `~/.claude/settings.json`. The shipped script also
writes the per-session **cost snapshot** that enables Option B of session cost
reporting (see `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md` §5).
Installation is **idempotent** and **backs up** anything it would overwrite.
This is the only change the command makes; it changes no workflow-command
behavior.

Note: Claude Code ships its own built-in `/statusline` command (backed by the
`statusline-setup` agent), so the bare `/statusline` resolves to Claude Code's
built-in flow. This is one instance of the general rule — see rule 6 of
`${CLAUDE_PLUGIN_ROOT}/references/next-phase-offer.md`: printed command names
are always fully qualified. Direct users to `/workflows-core:statusline`.

---

## Phase 1 — Resolve paths

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. No run flag applies to this command; `strip-run-flags` reports an explicit one as ignored. It takes no positional arguments to protect, but a stray flag must not be misread.

1. Source script: `${CLAUDE_PLUGIN_ROOT}/scripts/statusline-command.sh`.
2. Stable install path: `~/.claude/dev-workflows/statusline-command.sh`
   (per-user, survives plugin re-installs). Create `~/.claude/dev-workflows/` if
   missing.
3. Settings file: `~/.claude/settings.json`.

## Phase 2 — Preflight & back up

1. Read `~/.claude/settings.json` (treat a missing file as `{}`).
2. If a `statusLine` block already exists, print it and **back it up** to
   `~/.claude/settings.json.dev-workflows.bak` (do NOT overwrite an existing
   backup — suffix `-2`, `-3`, … ).
3. If `~/.claude/dev-workflows/statusline-command.sh` already exists, back it up
   the same way (`.bak`, then `-2`, … ) before overwriting.
4. Verify `bash` and `jq` are available; if `jq` is missing, do the Phase 4 JSON
   merge with `python3` instead — never hand-edit `settings.json` blindly.

## Phase 3 — Install the script

Copy the source script to the stable install path and `chmod +x` it. Verify it is
non-empty and begins with a `#!` shebang.

## Phase 4 — Merge the settings block (confirm first)

Show the user the exact change and ask to confirm
(`choices: ["Install", "Cancel"]`) BEFORE writing settings.
On confirm, MERGE (never clobber sibling keys) so that:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash ~/.claude/dev-workflows/statusline-command.sh"
  }
}
```

Use `jq '. + {statusLine: {type:"command", command:"bash ~/.claude/dev-workflows/statusline-command.sh"}}'`
(or the `python3` `json` equivalent), writing to a temp file and moving it into
place, so a failed merge never truncates `settings.json`. Preserve all other keys.

## Phase 5 — Report

Confirm the install path, the settings change, and any backups created. Tell the
user the status line takes effect on the next render / new session, and that the
per-session cost snapshot (Option B) is now enabled. This command NEVER commits
and writes only under `~/.claude/`.

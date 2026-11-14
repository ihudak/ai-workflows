# /statusline

Installs the plugin's multi-line status line into your Claude Code settings, enabling — given `jq` — the per-session cost snapshot session-cost reporting reads.

## Who runs it

`/statusline` runs outside the role pipeline — no role, no cost-attribution phase. [Workflow overview](../workflow.md#cross-cutting-commands) groups it under Setup, and recommends running it first: install it once, right after installing the plugin, so the cost snapshot it enables (given `jq`) is already in place before your first pipeline command runs.

**Claude Code ships its own built-in `/statusline` command** (backed by its own `statusline-setup` agent). The bare `/statusline` always resolves to that built-in, never to this one — **always type the qualified form, `/workflows-core:statusline`.** Three other commands in this family collide with a Claude Code built-in the same way — this plugin's [`/feedback`](feedback.md), the companion `dev-workflows` plugin's `/upgrade` and the companion `docs-workflows` plugin's `/release-notes` — and are qualified for the same reason; `dev-workflows`' `/design` collides with Claude Code's own `/design`, which makes a Design artifact, on the accounts that command is switched on for. No other command in this plugin is known to collide.

## Synopsis

```
/workflows-core:statusline
```

Takes no arguments. None of the three run flags apply to this command ([`environment.md`](../reference/environment.md)) — `strip-run-flags` still runs first, so an explicit `--skip-costs`, `--skip-feedback` or `--enforce-model` is recognized and reported ignored rather than misread as a positional argument. Before it changes your settings, it shows the exact change and asks you to confirm: *Install* or *Cancel*.

## What it needs

- **Local access to `~/.claude/settings.json`**, which it reads and writes, first backing up any `statusLine` block it already holds to `settings.json.dev-workflows.bak` beside it, and write access under `~/.claude/dev-workflows/` — nothing else. This command reads no `$SPECS_PATH`, runs no specs-repo preflight, and creates no branch.
- **`bash` and `jq`** — the installed script reads every field Claude Code hands it with `jq`, and renders nothing and writes no cost snapshot without it on the `PATH` it runs with — the one Claude Code started with, which need not be your shell's. Where the command's own shell finds no `jq` it says so above the confirmation question and again in its report, still installs on confirm — the line works from its next render once `jq` is installed — and does the settings merge with `python3` rather than hand-editing the JSON.

## What it produces

Installs the vendored script to a stable per-user path (`~/.claude/dev-workflows/statusline-command.sh`, `chmod +x`'d) and merges a `statusLine` block into `~/.claude/settings.json`, preserving every other key. **It is idempotent and backs up anything it would overwrite** — an existing `statusLine` block, or an existing installed script — suffixing `-2`, `-3`, … rather than clobbering a prior backup. Installing it also enables — given `jq`, as *What it needs* says — the per-session **cost snapshot** behind the [status-line cross-check](../reference/session-cost.md#status-line-cross-check), the `cost_statusline_usd` figure a cost entry carries beside the computed one. **This is the only settings change the command makes**, and it never commits anything; every write stays under `~/.claude/` — though enabling the cost snapshot does change what every cost-emitting command's Session cost line reports.

## Updates

The installed script is a copy, so a plugin update does not change it by itself. The plugin's [`statusline-refresh` hook](../reference/hooks.md) closes that gap: at every session start it compares the installed copy with the script the installed plugin version ships, and where they differ it puts the new one in place, keeping the old one as `statusline-command.sh.prev`. So after a `claude plugin update` of `workflows-core` and a restart, the new status line arrives with nothing to re-run.

**It replaces only a copy it can prove is unedited.** The install records the installed script's SHA-256 in `~/.claude/dev-workflows/statusline-command.sh.sha256`, and the hook replaces the script only while it still matches that record, then records the new one. A copy you edit by hand stops matching, and from then on the hook leaves it alone; run `/workflows-core:statusline` again to go back to the shipped script and to updates.

**An install made before 1.89.0 has no record**, so the hook leaves it alone too, unless it already equals the shipped script, in which case the hook records it and updates follow from then on. Run `/workflows-core:statusline` once to start following updates. Without `shasum` or `sha256sum` the hook does nothing, and the status line stays at the version last installed.

## Usage limits

The status line's fourth line shows your usage limits, as far as Claude Code or your account tells it:

- **`5h` and `7d`**: your rolling five-hour and weekly windows. Claude Code hands them to the status line itself, only for claude.ai Pro, Max and Ultra subscribers, and only after the session's first response.
- **`spend`**: your spend against a limit a Claude apps gateway sets for you — the percentage, and the dollar amounts and period once Claude Code has them. You set nothing: it appears only where your Claude Code is routed through such a gateway, which Claude Code reports by itself.
- **Plan usage, opt-in.** Claude Code passes no other limit to the status line, so an Enterprise seat's monthly usage budget and the per-model weekly windows (`7d-opus`, `7d-sonnet`, `7d-fable`, and any other a plan carries) show nothing by default. Set `WORKFLOWS_STATUSLINE_PLAN_USAGE=1` — in the `env` block of `~/.claude/settings.json`, so the status line inherits it — and the script reads them from your account's usage endpoint, the one Claude Code's own `/usage` and the desktop app read: `usage` with your spend against the monthly budget, and one bar per per-model window that has a value — a weekly one too where the endpoint lists it only among its limits, as it lists a plan's Fable limit. Each window is drawn once. To do so it reads your Claude Code login token from the macOS Keychain, or from `~/.claude/.credentials.json` elsewhere, and sends it to Anthropic only; the token is never printed, never written to disk and never put on a command line, and an expired one is skipped, never refreshed. The call runs in the background, at most once every five minutes, into `~/.claude/dev-workflows/plan-usage.json`, so a render never waits on the network; a cache more than an hour old is not drawn. The endpoint is not a public API: a field it stops sending drops out of the line, and a field it sends only under an internal name is not shown. It needs `curl`.

A window Claude Code already passed is never drawn twice.

## Gates

No reviewer, no branch, no commit. The one checkpoint is the explicit confirmation question, shown against the exact settings diff, before your settings are written.

## Example

```
/workflows-core:statusline
```

Run this once, first, right after installing the plugin. It backs up any existing `statusLine` block or installed script, installs the script, merges the new block into `~/.claude/settings.json` on confirmation, and reports the paths touched. The status line takes effect on the next render or new session.

## See also

- [Workflow overview](../workflow.md) — where this command sits among the cross-cutting commands, and why its qualified form is the only one that reaches it.
- [Session cost](../reference/session-cost.md#status-line-cross-check) — the status-line cross-check this command's cost snapshot enables, given `jq`.
- [`/feedback`](feedback.md), in this plugin, `/release-notes`, in the `docs-workflows` plugin, and `/upgrade`, in `dev-workflows` — the other three commands whose bare form also reaches a Claude Code built-in; `/design`, in `dev-workflows`, can reach one on the accounts Claude Code's own `/design` is switched on for.

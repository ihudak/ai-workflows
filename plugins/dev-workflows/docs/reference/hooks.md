# Hooks reference

`dev-workflows` bundles one hook, declared in `hooks/hooks.json` and installed automatically with the plugin — there is nothing to opt into separately. It is advisory: **a hook never blocks Claude.** The script ends in an unconditional `exit 0` regardless of what it detects or whether its own logic errors out, by contract — a hook exists to notify or remind, never to gate a tool call.

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `preload-context` | `UserPromptSubmit` | — | On a matched `/implement`, `/vuln` or `/dev-workflows:upgrade` prompt, injects git/model-routing/specs context; a near-instant no-op otherwise. |

**`notify-done` and `test-notify` moved to `workflows-core`.** `notify-done` and `test-notify` are session-wide — one fires on every `Stop`, the other on every `Bash` tool call — so neither was ever specific to this plugin's commands. They now ship from `workflows-core`, which every plugin in the family declares as a dependency, so a user who installs `product-workflows` or `docs-workflows` without this plugin gets them too. See [`workflows-core`'s hooks reference](../../../workflows-core/docs/reference/hooks.md).

The companion `docs-workflows` and `product-workflows` plugins each ship their own `preload-context` — `docs-workflows`'s covering `/document` and `/docs-workflows:release-notes`, `product-workflows`'s covering `/epics` — plus `docs-workflows`'s `changelog-owners-reminder`, which warns about a docs page's changelog and owners frontmatter. `/epics` moved out of this plugin's own regex when it moved to `product-workflows`; `preload-context` itself was **split** across all three plugins rather than moved, so each now preloads only for its own commands.

## What each hook does, in detail

### `preload-context` (`hooks/preload-context.sh`)

Runs on every `UserPromptSubmit` event. It reads the submitted prompt from stdin JSON (trying the `prompt`, `user_prompt`, and `message` keys in turn for compatibility across Claude Code versions) and matches it in two branches: `^/(dev-workflows:)?(implement|vuln)[[:space:]]+[^[:space:]-]` accepts either form, and `^/(dev-workflows:)(upgrade)[[:space:]]+[^[:space:]-]` accepts the **qualified form only**. That asymmetry is deliberate: Claude Code ships its own built-in `/upgrade` and the built-in wins, so a bare `/upgrade` never reaches this plugin and preloading for it would inject a repo scan into a run that is not ours. `/implement` and `/vuln` have no built-in of the same name. Anything else, including a bare command with no argument, exits immediately with no output. For a match, it routes by command: `/implement`, `/vuln`, and `/upgrade` all get full context (a model-routing reminder, the current branch, `git status --short`, the last 5 commits, and a directory listing when the cwd has 30 or fewer entries), plus specs context (`$SPECS_PATH` and the current branch — not `$REPOS_PATH`, which `/implement` does not read) when `/implement`'s own argument looks like an address. `/epics` moved to the companion `product-workflows` plugin along with the rest of its own `preload-context` routing, and no longer matches this regex at all. Every other command is not matched at all, so no context is injected for it — including `/document` and `/release-notes`, which the sibling `docs-workflows` plugin's hook of the same name matches instead, and `/epics`, which the sibling `product-workflows` plugin's hook now matches. All three plugins' regexes are pairwise disjoint by construction — each accepts only its own plugin's literal name as a prefix and only its own plugin's command names — so on a machine with any two or all three plugins installed, every script runs on every prompt and at most one of them ever emits.

## Why none of this blocks you

The script above ends `exit 0` unconditionally — the exit code is never derived from what the hook found, so an unreadable prompt payload or a missing `git` never stops a tool call, a turn, or the run itself. It also guards on `command -v python3` up front and exits 0 immediately when it is absent, degrading to silence rather than failing.

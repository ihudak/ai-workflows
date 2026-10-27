# Hooks reference

`product-workflows` bundles one hook, declared in `hooks/hooks.json` and installed automatically with the plugin — there is nothing to opt into separately: a single `UserPromptSubmit` hook, `preload-context`. The hook is advisory: **it never blocks Claude.** The script ends in an unconditional `exit 0` regardless of what it detects or whether its own logic errors out, by contract — a hook exists to notify or remind, never to gate a tool call.

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `preload-context` | `UserPromptSubmit` | — | On an `/epics <address>` prompt, injects `$SPECS_PATH` and `$REPOS_PATH` context that run resolves against; a near-instant no-op otherwise. |

Two sibling plugins each ship a `preload-context` hook of their own: `dev-workflows`'s covers `/implement`, `/vuln`, and `/dev-workflows:upgrade`; `docs-workflows`'s covers `/document` and `/docs-workflows:release-notes`. `/dev-workflows:upgrade` and `/docs-workflows:release-notes` are written qualified because that is the only form their hooks match — Claude Code ships a built-in of each bare name and the built-in wins, so a bare `/upgrade` or `/release-notes` never reaches the plugin at all. **`/document` is not one of them**, though it sits last in that list: its own regex makes the plugin prefix optional (`^/(docs-workflows:)?(document)…`), because no built-in shares the name, so it matches the bare form too — which is what each sibling's own hooks page states and what this page used to contradict by grouping it with `/release-notes`. Each sibling's own hooks page states that asymmetry where its script enforces it. A `UserPromptSubmit` hook fires whichever plugin ships it, so on a machine carrying two or three of these plugins, every one of their `preload-context` scripts runs on every prompt — but the three plugins' regexes are disjoint by command name, and each also accepts only its own plugin-name prefix, so no single prompt can match more than one of them. Installing this plugin alone, without either sibling, is a supported configuration, and it is the reason this hook lives here rather than being shared: `${CLAUDE_PLUGIN_ROOT}` resolves to the plugin that *ships* a hook, and a hook cannot source a sibling plugin's file to reuse its logic — a dependency grants installation, never file access.

## What the hook does, in detail

### `preload-context` (`hooks/preload-context.sh`)

Runs on every `UserPromptSubmit` event. It reads the submitted prompt from stdin JSON (trying the `prompt`, `user_prompt`, and `message` keys in turn for compatibility across Claude Code versions) and matches it against `^/(product-workflows:)?(epics)[[:space:]]+[^[:space:]-]` — `/epics`, bare or prefixed with this plugin's own namespace, followed by at least one non-flag argument. Anything else, including a bare `/epics` with no argument or `/epics --help`, exits immediately with no output, so a misfire never injects noise.

For a match it injects specs context: `$REPOS_PATH` (or its `/workspace` default, noted as such), `$SPECS_PATH` (or a note that it is unset and that a command that needs it asks for it), and the current git branch when the working directory is inside a git repository. `/epics` is the one command this plugin ships that this hook covers — the other thirteen are keyed but resolve their own address through `resolve-address` without needing a pre-injected hint, and none of them was added to the regex.

## Why this never blocks you

The script ends `exit 0` unconditionally — the exit code is never derived from what the hook found, so a prompt payload that will not parse, or a command it does not recognize, never stops a tool call, a turn, or the run itself. It also guards on `command -v python3` up front and exits 0 immediately when python3 is absent, degrading to silence rather than failing.

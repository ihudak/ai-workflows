# Environment reference

[Getting started](../getting-started.md) says what the variable is *for*. This page says what it **is** — its default, what happens when it is unset or unreadable, and the layout it expects. The plugin reads one user-settable variable. The other names that appear in its files are not yours to set for this plugin: `CLAUDE_PLUGIN_ROOT` and `ARGUMENTS` are plumbing Claude Code sets for every plugin, and `VALE_CONFIG_PATH` is Vale's own, which the review commands clear for their Vale run so it reads the repository's configuration.

## `$PROSE_STYLE_PATH`

**What it is.** An absolute path to a directory of `.md` files carrying your organization's own style rules — the third place the overlay is looked for, after `--rules <path>` and the repository's own `.prose-style/rules/`.

**Default.** Unset. There is no default path.

**Unset, unreadable, or holding no `.md` file.** A silent, non-blocking fall-through to the baseline alone. Nothing is printed beyond the review's `Rules:` line, which reads `baseline`.

**Layout.** A flat directory of `.md` files. A file whose name matches a baseline file (`word-list.md`, `terminology.md`, …) layers over it; a file matching none is an additional rule source; a first line of `<!-- prose-style: replace -->` replaces the baseline file of the same name. [The overlay](overlay.md) has the whole precedence table.

**Written by.** [`/prose-style-refresh`](../commands/prose-style-refresh.md), where it is the overlay directory that resolves first. Nothing else in the plugin writes to it.

# prose-style documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| see the three commands and how they relate | [Workflow](workflow.md) |
| review the documentation a pull request changed | [`/prose-review-pr`](commands/prose-review-pr.md) |
| review files or a directory, and fix what is safe to fix | [`/prose-review-docs`](commands/prose-review-docs.md) |
| regenerate my organization's overlay from its style guide | [`/prose-style-refresh`](commands/prose-style-refresh.md) |
| layer my organization's style guide over the baseline | [The overlay](reference/overlay.md) |

## Commands

- [`/prose-review-pr`](commands/prose-review-pr.md) — review the markdown files a pull request changed, by its number or its branch.
- [`/prose-review-docs`](commands/prose-review-docs.md) — review markdown files or directories, and with `--fix` apply the safe fixes.
- [`/prose-style-refresh`](commands/prose-style-refresh.md) — regenerate your overlay from the style-guide source you configure.

## Reference

- [The overlay](reference/overlay.md) — where your own rules are found, how they layer over the baseline, and the dialect the checker infers where they say nothing.
- [Agents](reference/agents.md) — `prose-style-checker` and `prose-fixer`, and the violation schema they share.
- [References](reference/references.md) — the eight baseline files under `references/`, and the `prose-style-rules` skill that loads them while writing.
- [Environment](reference/environment.md) — `$PROSE_STYLE_PATH`.

## Status

This plugin ships three slash commands and two agents, plus the 8 reference files they check against — and one bundled skills entry, `prose-style-rules`. It writes nothing to `$SPECS_PATH` and opens no branch; `/prose-review-docs --fix` and `/prose-review-pr`'s fix offer edit the files they reviewed, and `/prose-style-refresh` writes only your overlay directory.

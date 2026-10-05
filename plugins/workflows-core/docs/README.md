# workflows-core documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| see the whole plugin family on one diagram — roles, plugins, and what each command hands the next | [Family map](family-map.md) |
| see where these commands sit | [Workflow](workflow.md) |
| know which cost phase a run is charged to | [Roles and phases](roles-and-phases.md) |
| tell the plugin family it got something wrong | [`/feedback`](commands/feedback.md), [`/prompt`](commands/prompt.md) |
| turn a correction into a redesign or a grilling | [`/prompt-brainstorm`](commands/prompt-brainstorm.md), [`/prompt-grill-me`](commands/prompt-grill-me.md) |
| see live cost and context while you work | [`/statusline`](commands/statusline.md) — **run this first** |
| make a folder of exported design frames readable | [`/frames`](commands/frames.md) |
| understand what a run cost | [Session cost](reference/session-cost.md) |

## Commands

- [`/feedback`](commands/feedback.md) — log a note about the plugin itself, for the maintainer to aggregate.
- [`/frames`](commands/frames.md) — (re)build the index every `design/<frame-set>/` of one resolved folder must carry before anything can read it.
- [`/prompt`](commands/prompt.md) — log a correction you just made to a command's output, then apply the fix directly.
- [`/prompt-brainstorm`](commands/prompt-brainstorm.md) — log a correction, then hand off to `superpowers:brainstorming` to redesign it together.
- [`/prompt-grill-me`](commands/prompt-grill-me.md) — log a correction, then grill the fix inline with a bounded interrogation.
- [`/statusline`](commands/statusline.md) — install the plugin family's multi-line status line into your Claude Code settings.

## Reference

- [Agents](reference/agents.md) — the seven agents this plugin bundles, and which commands dispatch them.
- [References](reference/references.md) — the reference corpus under `references/`, which the whole plugin family reads.
- [Skills](reference/references.md#skills) — the two bundled skills, `model-routing` and `reference`: what each is for, and whether it is user-invocable.
- [Environment](reference/environment.md) — every environment variable this plugin reads, and what it configures.
- [Hooks](reference/hooks.md) — the two session-wide hooks this plugin bundles, and why they live here rather than in a pipeline plugin.
- [Session cost](reference/session-cost.md) — how a run's dollar cost is computed, attributed, and persisted.
- [Session feedback](reference/session-feedback.md) — what `/feedback` and the three `/prompt*` commands record, and where it lands.

## Status

This plugin ships 6 slash commands, 7 agents, and 33 reference files. Most of what it carries is not a command: it is the shared corpus and the agents the sibling plugins in this family — `dev-workflows`, `product-workflows`, and `docs-workflows` — read and dispatch, extracted here so more than one plugin can depend on one copy. All three declare it, which is what makes it shared rather than merely reused.

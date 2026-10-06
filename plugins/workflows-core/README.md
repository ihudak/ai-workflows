# workflows-core

Shared foundation for the `dev-workflows` plugin family: the addressing grammar and specs-repo git entry points, phase handoff, model routing, escalation and finding-triage rules, cost/feedback/follow-up emission, and the grounding and grilling conventions every authoring command applies. It also carries seven slash commands — the family-meta utilities, `/frames`, the design-frame-set indexer, and `/diagnose-session`, which reads a session's transcripts to say why a run went wrong — plus the agents any plugin in the family may dispatch.

> Part of the `shipwright` marketplace — see the [repo-root setup guide](../../README.md) for marketplace install + prerequisites.

## What it does

Most of this plugin is not a command at all. It is the corpus a sibling plugin reads: 36 files under `references/`, reached through the `reference` loader skill, the `model-routing` skill that resolves the classification rules, and ten agents dispatched by name. The seven commands it does ship are the ones that belong to no single pipeline — they act on the plugin family itself, or on the specs tree rather than on a phase of it.

| Group | Commands | What it does |
|-------|----------|--------------|
| Plugin feedback | [`/feedback`](docs/commands/feedback.md), [`/prompt`](docs/commands/prompt.md), [`/prompt-brainstorm`](docs/commands/prompt-brainstorm.md), [`/prompt-grill-me`](docs/commands/prompt-grill-me.md) | Log friction about the plugin itself, or capture a correction you just made and act on it. |
| Session diagnosis | [`/diagnose-session`](docs/commands/diagnose-session.md) | Read a session's transcripts and report, with evidence, what happened in a run that went wrong. |
| Setup | [`/statusline`](docs/commands/statusline.md) | Install the plugin family's multi-line status line into your Claude Code settings. |
| Specs-tree repair | [`/frames`](docs/commands/frames.md) | (Re)build the index every exported design frame set must carry before anything can read it. |

`/statusline` and `/feedback` each collide with a Claude Code built-in of the same name, so type the qualified `/workflows-core:statusline` and `/workflows-core:feedback`.

## Documentation

| Page | What's there |
|------|--------------|
| [Documentation index](docs/README.md) | The command list and the reference inventories. |
| [Getting started](docs/getting-started.md) | Install, environment variables, and what this plugin is for. |
| [Workflow overview](docs/workflow.md) | Where these seven commands sit relative to the pipeline they serve. |
| [Roles and phases](docs/roles-and-phases.md) | The cost-attribution phases these commands reach, and how. |
| [Agents](docs/reference/agents.md) | The ten agents this plugin bundles and who dispatches them. |
| [References](docs/reference/references.md) | The reference corpus under `references/`. |
| [Environment](docs/reference/environment.md) | Every environment variable this plugin reads. |
| [Hooks](docs/reference/hooks.md) | The two session-wide hooks this plugin bundles, and why they live here. |
| [Session cost](docs/reference/session-cost.md) | How a run's dollar cost is computed, attributed, and persisted. |
| [Session feedback](docs/reference/session-feedback.md) | What `/feedback` and `/prompt*` record, and where it lands. |

## License

MIT — see [LICENSE](LICENSE).

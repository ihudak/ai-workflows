# guideline-reviewers

Two standalone review commands, and the guidance they review against: an OpenAPI specification against bundled REST API and IAM permission-naming guidance, and application code or UI against bundled public design-system and accessibility standards. Neither command consumes a workflow artefact or produces one.

This plugin ships two slash commands, [`/api-guideline-reviewer`](docs/commands/api-guideline-reviewer.md) and [`/guideline-reviewer`](docs/commands/guideline-reviewer.md), each dispatching its own agent against the guidance bundled under `references/`.

See [the documentation index](docs/README.md) for the full command, agent, and reference inventory.

## Documentation

| Page | What's there |
|------|--------------|
| [Documentation index](docs/README.md) | The "I want to…" lookup table and the full inventory. |
| [Getting started](docs/getting-started.md) | Install, and what each command needs before its first run. |
| [Workflow overview](docs/workflow.md) | The two commands and how they relate, as one diagram. |
| [`/api-guideline-reviewer`](docs/commands/api-guideline-reviewer.md) | Review an OpenAPI specification against the bundled REST API and IAM permission-naming guidance. |
| [`/guideline-reviewer`](docs/commands/guideline-reviewer.md) | Review application code or a UI against the bundled design-system and accessibility guidance. |
| [Agents](docs/reference/agents.md) | The two agents, one per command. |
| [References](docs/reference/references.md) | The guidance bundled under `references/` that each review cites. |
| [Environment](docs/reference/environment.md) | Every environment variable the plugin reads. |

# dev-workflows

A role-based pipeline of 6 slash commands for the engineering side of the workflow plugin family. Its spine runs design → implementation, with readiness verification alongside it and a conformance check closing it — `/design → /implement → /conformance`, `/ready` — picking up from the merged `specification.md` that the companion `product-workflows` plugin's PRD → architecture → Epic breakdown → specification ladder (and its six-command BRD-to-PRD route) hands off, with Opus-backed risk planning, code review, and design review gates along the way; around that spine sit CVE remediation and dependency upgrades. The table below is the complete list. The shared foundation every command here draws on — the addressing grammar, the git and phase-handoff entry points, model routing, escalation and triage, and the emitters — ships in the companion `workflows-core` plugin; the documentation tail `/implement` hands off to — `/docs-workflows:document` and `/docs-workflows:release-notes` — ships in the companion `docs-workflows` plugin.

> Part of the `shipwright` marketplace — see the [repo-root setup guide](../../README.md) for marketplace install + prerequisites.

## What it does

Every command owns one role's step in the pipeline and hands a concrete artifact to the next. See [Workflow overview](docs/workflow.md) for the diagram and [Roles and phases](docs/roles-and-phases.md) for what each role is accountable for.

| Role | Commands | What it does |
|------|----------|--------------|
| PM/PA/PE | Moved to the sibling `product-workflows` plugin | Refine an idea into a PRD, ground an architecture decision or a BRD's requirements, break a PRD into Epics, author a specification, and run the six-command BRD-to-PRD route. |
| Dev | [`/design`](docs/commands/design.md), [`/implement`](docs/commands/implement.md), [`/ready`](docs/commands/ready.md), [`/conformance`](docs/commands/conformance.md) | Design against the spec, implement it under review gates, check readiness, and check what was built against the spec. Documenting and release notes moved to `docs-workflows`. |
| Anytime — maintenance | [`/vuln`](docs/commands/vuln.md), [`/upgrade`](docs/commands/upgrade.md) | Remediate a CVE, or upgrade a dependency. |
| Anytime — guideline review | Moved to the sibling `guideline-reviewers` plugin | Review an OpenAPI spec or app UI against bundled guidelines. |
| Anytime — specs-tree repair, status line, plugin feedback | Moved to the sibling `workflows-core` plugin | Index an exported design frame set, install the status line, and log friction or a correction about the plugin itself. |
| Dev/PM — documentation & release notes | Moved to the sibling `docs-workflows` plugin | Write product documentation, profile a docs repo, and draft the release note. |

## Documentation

| Page | What's there |
|------|--------------|
| [Documentation index](docs/README.md) | The full "I want to…" lookup table, plus the command and reference inventories. |
| [Getting started](docs/getting-started.md) | Install, environment variables, status line, your first `/design` run. |
| [Workflow overview](docs/workflow.md) | The whole pipeline as one diagram. |
| [Roles and phases](docs/roles-and-phases.md) | What each role owns and hands off. |
| [Agents](docs/reference/agents.md) | The subagent inventory the commands dispatch internally. |
| [Test suite detection](docs/reference/test-suite-detection.md) | Which test stacks a run finds and runs, and what happens to one it does not. |
| [References](docs/reference/references.md) | The reference-doc inventory under `references/`. |
| [Environment](docs/reference/environment.md) | Every environment variable the plugin reads. |
| [Hooks](docs/reference/hooks.md) | The bundled hooks and what each does. |
| [Model routing](docs/reference/model-routing.md) | Task-complexity classification and the model fallback chain. |
| [Session cost](docs/reference/session-cost.md) | How a run's dollar cost is computed, attributed, and persisted. |
| [Session feedback](docs/reference/session-feedback.md) | Two signals: what you report, and what your corrections reveal. |
| [Follow-ups](docs/reference/follow-ups.md) | How a command emits follow-up tasks into the specs tree. |
| [Resume and checkpoints](docs/reference/resume-and-checkpoints.md) | Session hygiene for a long-running command. |

## Recommended environment

Mount every repository and your specs repo under one `/workspace`, matching this plugin's defaults, with [`ihudak/ai-containers`](https://github.com/ihudak/ai-containers). Outside a container the commands still work — set `$REPOS_PATH` and `$SPECS_PATH` yourself; see [Environment](docs/reference/environment.md).

## License

MIT — see [LICENSE](LICENSE).

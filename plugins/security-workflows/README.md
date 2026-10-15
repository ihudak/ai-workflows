# security-workflows

A security audit role for the workflow plugin family. Its one command, `/security-workflows:scan <KEY | repo-path> [--import <dir> | --triage | --verify-fixes] [--effort medium|high]`, runs Anthropic's Claude Security plugin on the branch a PRD or Epic was implemented on, before it merges, or across a whole repository, and records what it finds in the specs repository as a findings register per code repository. The shared foundation it draws on — the addressing grammar, the git entry points, escalation and triage — ships in the companion `workflows-core` plugin; Claude Security is installed with it.

> Part of the `shipwright` marketplace — see the [repo-root setup guide](../../README.md) for marketplace install + prerequisites.

## What it does

A Dev runs the command on their Epic before its pull request merges. A Security Engineer runs it across a repository, with `--triage` and `--verify-fixes`. A Dev is never blocked by the Security Engineer: a Dev's decisions take effect at once and are reviewed afterwards. See [Workflow overview](docs/workflow.md) for the diagram and [Roles and phases](docs/roles-and-phases.md) for what each role is accountable for.

| Role | Command | What it does |
|------|---------|--------------|
| Dev | [`scan`](docs/commands/scan.md) | Scan the branch an Epic was implemented on before it merges, triage every finding in one batch, and hand a fix to `/dev-workflows:implement`. |
| Security Engineer | [`scan`](docs/commands/scan.md) | Scan a whole repository, review the decisions Devs took, and confirm a fix by a later scan that no longer reports it. |

## Documentation

| Page | What's there |
|------|--------------|
| [Documentation index](docs/README.md) | The full "I want to…" lookup table. |
| [Getting started](docs/getting-started.md) | Install, environment variables, your first scan. |
| [Workflow overview](docs/workflow.md) | The whole flow as one diagram. |
| [Roles and phases](docs/roles-and-phases.md) | What each role owns and hands off. |
| [Security register](docs/reference/security-register.md) | The findings register the command writes into the specs repository. |
| [Environment](docs/reference/environment.md) | Every environment variable the plugin reads. |
| [Session cost](docs/reference/session-cost.md) | How a run's dollar cost is computed, attributed, and persisted. |

## Recommended environment

Mount every repository and your specs repo under one `/workspace`, matching this plugin's defaults, with [`ihudak/ai-containers`](https://github.com/ihudak/ai-containers). Outside a container the command still works — set `$REPOS_PATH` and `$SPECS_PATH` yourself; see [Environment](docs/reference/environment.md).

## License

MIT — see [LICENSE](LICENSE).

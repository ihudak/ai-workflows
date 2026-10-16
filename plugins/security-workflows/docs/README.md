# security-workflows documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| see where the security scan sits in the family's delivery | [Workflow overview](workflow.md) |
| know what my role runs and decides | [Roles and phases](roles-and-phases.md) |
| scan my Epic's branch before its pull request merges | [`/security-workflows:scan`](commands/scan.md) — with the Epic's key |
| scan a whole repository | [`/security-workflows:scan`](commands/scan.md) — with a repository path |
| close fixes once they have merged | [`/security-workflows:scan`](commands/scan.md) — `--verify-fixes` |
| review the decisions a Dev took, and the risks due for review | [`/security-workflows:scan`](commands/scan.md) — `--triage` |
| record a report I made with `/claude-security` myself | [`/security-workflows:scan`](commands/scan.md) — `--import` |
| read the findings register, or know how a finding is closed | [Security register](reference/security-register.md) |
| set the environment variable it reads | [Environment](reference/environment.md) |
| understand what a run cost | [Session cost](reference/session-cost.md) |

Three pages orient you before you run the command: [Getting started](getting-started.md) installs the plugin, its two dependencies and what Claude Security needs on your machine; [Workflow overview](workflow.md) shows the command's runs, by role, beside `/dev-workflows:implement` and Claude Security as one diagram; and [Roles and phases](roles-and-phases.md) says what the Dev and the Security Engineer each run and decide. Every other page below documents the command or one part of what it keeps.

## Commands

- [`/security-workflows:scan`](commands/scan.md) — audit an Epic's branch before its pull request merges, or a whole repository, with Claude Security; record what it finds in the specs repository's findings register for that code repository; triage every finding in one batch; and hand each fix to `/dev-workflows:implement`. `--verify-fixes` closes fixes on evidence, `--triage` reviews decisions, and `--import` records a report you made yourself.

## Reference

- [Security register](reference/security-register.md) — the findings register the command keeps per code repository: where it lives, why it is bookkeeping, the statuses and their diagram, a false positive against an accepted risk, what awaits security review, how a finding is closed, and how findings are numbered.
- [Environment](reference/environment.md) — the one environment variable the plugin reads, and what happens when it is unset or misplaced.
- [Session cost](reference/session-cost.md) — which commands emit a cost entry, what they charge to, and where it lands.

## Where the rest lives

This plugin is the security audit of a family. Three plugins matter to it — two it declares as dependencies, and one whose output it reads without depending on it:

- **`workflows-core`** — the shared reference corpus the command loads through the `reference` skill: the addressing grammar, the specs-repo git entry points, escalation, the Epic-branch lookup, cost, feedback and follow-up emission, and the format of the findings register itself, which is the authority on everything the [Security register](reference/security-register.md) page describes. It is a declared dependency, so installing this plugin installs it.
- **Claude Security** — Anthropic's `claude-security` plugin, from its official marketplace, which does every scan and every patch. Also a declared dependency.
- **`dev-workflows`** — the build half of the pipeline: `/dev-workflows:implement` writes the `implementation.md` a change scan finds the Epic's branch in, offers the scan, and takes each fix back on the Epic's branch, and `/dev-workflows:conformance` runs before the scan. Neither plugin depends on the other: a scan of a repository path needs no other family plugin.

## Status

This plugin ships one command, `/security-workflows:scan`, and two scripts: `register.py`, the register's only writer, and the capped-call helper every family plugin carries. It ships 0 bundled skills, no agents, no hooks and no reference files of its own: the register's format is a `workflows-core` reference, since a reference does not cross a plugin boundary and any family plugin can load one from there.

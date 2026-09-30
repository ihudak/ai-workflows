# dev-workflows documentation

| I want to… | Go to |
|---|---|
| install this and set it up | [Getting started](getting-started.md) |
| understand the whole pipeline first | [Workflow overview](workflow.md) |
| know what my role is responsible for | [Roles and phases](roles-and-phases.md) |
| write a specification, then a design | `/product-workflows:specify` — ships in the companion `product-workflows` plugin — then [`/design`](commands/design.md) |
| build the thing | [`/implement`](commands/implement.md) |
| document it, then announce it | `/docs-workflows:document`, `/docs-workflows:release-notes` — both ship in the companion `docs-workflows` plugin |
| check whether a ticket is really ready | [`/ready`](commands/ready.md) |
| fix a CVE or upgrade a dependency | [`/vuln`](commands/vuln.md), [`/upgrade`](commands/upgrade.md) |
| find out whether my test stack is covered | [Test suite detection](reference/test-suite-detection.md) |
| understand what a run cost | [Session cost](reference/session-cost.md) |
| turn a raw idea into a PRD, or work the BRD-to-PRD route | Moved to the sibling `product-workflows` plugin |

Three pages orient you before you touch a command: [Getting started](getting-started.md) installs the plugin and sets your environment variables; [Workflow overview](workflow.md) shows the whole pipeline as one diagram; [Roles and phases](roles-and-phases.md) says what each role owns and hands off. Every other page below documents one command, one shared subsystem, or — for [Agents](reference/agents.md) and [References](reference/references.md) — one whole inventory.

## Commands

- [`/design`](commands/design.md) — take over a merged specification and author a reviewed engineering design, grounded strictly in the mounted code.
- [`/implement`](commands/implement.md) — classify, plan, implement, test, and review a code change end to end.
- [`/ready`](commands/ready.md) — derive the workflow phase from the ARD/spec/design record and report what is missing to leave it; `--claimed` checks a status you declare against it.
- [`/upgrade`](commands/upgrade.md) — plan and execute a library, framework, runtime, or build-tool upgrade.
- [`/vuln`](commands/vuln.md) — research and fix a CVE, one dependency or code change at a time.

The PM/PA/PE commands that used to sit here — `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/epics`, `/specify`, and the six-command BRD-to-PRD route (`/brd-intake`, `/brd-split`, `/prd-ground`, `/brd-interview`, `/brd-package`, `/brd-reconcile`) — ship in the companion `product-workflows` plugin now, alongside the agents and reference files that supported them.

## Reference

- [Agents](reference/agents.md) — the subagent inventory: what each helper agent does and which command calls it.
- [Test suite detection](reference/test-suite-detection.md) — the seventeen marker rows `test-baseliner` scans for, what each one runs, the repository-declared test command it falls back to for a stack the table does not list, and what adding one takes.
- [References](reference/references.md) — the reference-doc inventory under `references/`, grouped by subtree.
- Skills — this plugin ships 0 bundled skills of its own. The `model-routing` skill every pipeline command loads at its classification step ships in `workflows-core`, alongside the classification reference it resolves; `docs-frontmatter`, the one skill that used to ship here, moved to `docs-workflows` with the `docs-profiles/` conventions it applies.
- [Environment](reference/environment.md) — every environment variable the plugin reads, and what it configures.
- [Hooks](reference/hooks.md) — the bundled hooks and what each one does.
- [Commit convention](reference/commit-convention.md) — end your commit subject with `[<key>]`, and what that buys you when the companion plugin's `/docs-workflows:document` and `/docs-workflows:release-notes` look for the diff.
- [Model routing](reference/model-routing.md) — the task-complexity classification and model fallback chain commands apply before acting.
- [Session cost](reference/session-cost.md) — how a run's dollar cost is computed, attributed, and persisted.
- [Session feedback](reference/session-feedback.md) — two different signals about the plugin itself: this plugin's own automatic capture, and the companion plugin's `/workflows-core:feedback`, which logs what you tell it, and `/workflows-core:prompt*`, which captures a bad result, your correction, and the good result that came out of it.
- [Follow-ups](reference/follow-ups.md) — how a command records follow-ups in the specs tree.
- [Resume and checkpoints](reference/resume-and-checkpoints.md) — session hygiene: checkpointing state and resuming a long-running command.

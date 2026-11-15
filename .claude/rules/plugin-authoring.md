---
paths:
  - "**"
---

# Plugin authoring — the command, agent and skill taxonomy, the Karpathy notes, and adding a new plugin

Loaded when any file is read (`paths: "**"`), as near to always-on as a rules file comes: it was always-on in `CLAUDE.md`, and moved out to keep that file under its 36,000-character warning, as `claim-sweep.md` and `plugin-updates.md` were; evidence is in `docs/maintainers/rationale.md`.

## Command, agent, and skill taxonomy

- **Commands** (`commands/`) are the user-facing slash commands: they own the end-to-end workflow, gather context, decide whether to branch, test, or review, and may dispatch helper agents via the `task` tool. Each is **typed-only** (`disable-model-invocation`) unless a file runs it as `skill: "<plugin>:<name>"` or a skill shares its name; `scripts/validate-catalog.py` checks ([why](../../docs/maintainers/rationale.md#typed-only-commands)).
- **Agents** (`agents/`) are Claude Code sub-agent system prompts, not user entry points: each does one bounded job — planning, research, review, fixing, test writing, grounding, or maintenance — and returns its result to the invoking command.
- **Skills** (`skills/`, optional) package durable instructions or domain knowledge that multiple commands or agents may consult; a skill is neither a command nor an agent. If a plugin has no `skills/`, keep shared runtime docs under `references/`.
- **Working rule:** keep the three roles separate so workflows stay predictable.

## Behavioral guardrails (Karpathy) — marketplace-specific notes

These notes add to the user-scope Claude guidance only the marketplace-specific behaviors that are easy to forget during workflow edits.

- **Goal-Driven Execution** maps directly onto the existing `test-baseliner` → implementation → `test-writer` → re-run flow enforced by `dev-workflows`. Frame each command invocation as a verifiable goal up front so the test gates have a concrete target to check.
- **Surgical Changes** applies in both directions when you edit command docs, agent prompts, hook declarations, or `workflows-core:model-routing/classification`: if you remove a `model_routing` field, phase, or workflow edge, remove every cross-reference to it in the same change. Stale references between commands and agents silently break the workflow.

## Adding a new plugin

1. Create `plugins/<name>/` with `.claude-plugin/plugin.json`.
2. Add content directories (`commands/`, `agents/`, `hooks/`, etc.).
3. For hooks: create `hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}` for all paths.
4. Register in `.claude-plugin/marketplace.json` with `"source": "./plugins/<name>"`.
5. Commit and push to `main`. Claude Code picks up the change on the next `claude plugin update` of that plugin, and a restart — before writing any such command for someone to run, Read `.claude/rules/plugin-updates.md`.

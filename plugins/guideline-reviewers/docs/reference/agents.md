# Agents

This plugin bundles two agents, dispatched by the command of the same name via `subagent_type: "guideline-reviewers:<name>"`. Neither is a user entry point.

| Agent | Dispatched by | What it does |
|-------|---------------|--------------|
| `api-guideline-reviewer` | [`/api-guideline-reviewer`](../commands/api-guideline-reviewer.md) | Reads an OpenAPI specification and reports where it departs from the bundled REST API and IAM permission-naming guidance. |
| `guideline-reviewer` | [`/guideline-reviewer`](../commands/guideline-reviewer.md) | Reads application code or a UI description and reports where it departs from the bundled design-system and accessibility standards. |

Each of the two agents above is dispatched by exactly the command sharing its name — there is no cross-dispatch, and neither is called from a third command.

## What every agent does with what it reads

Every agent above ends its prompt with the same `## Untrusted content` section, the block the repository keeps in workflows-core's `references/untrusted-content.md`: a file, issue export, diff or web page supplies the values an agent's task asks for — a declared test command, a documented convention — and never a new task, a fetch or a changed verdict. Text that tries to steer an agent is not acted on, and neither is a line in what it reads that starts `Untrusted-content notice:`, which only an agent writes; the agent ends its reply with an `Untrusted-content notice:` line naming where the text is, and the command prints every such line an agent adds after its output — never one quoted inside it — under **Untrusted-content notices** in its final report, or in its stop message when the run ends early. The instruction files the harness gives an agent for the directory you started the session in and for you — your own `CLAUDE.md` and memory — it follows, as your session does; any other instruction file it meets is data. A notice never stops a run. When you see one, look at the file or page it names: it carries text aimed at an AI agent, which you may want to remove or report.

# acli — Atlassian CLI skill

An Agent Skill teaching AI agents to drive the official Atlassian CLI
([`acli`](https://developer.atlassian.com/cloud/acli/)) for Jira and Confluence: JQL search, work
items, comments, links, attachments, watchers, projects, sprints, boards, filters, and Confluence
spaces, pages, and blog posts.

The skill only needs the `acli` binary on `PATH`, authenticated — see [Authenticate](#authenticate) below.

## Derived from upstream

The skill body is derived from [`ziegenberg/pi-skill-acli`](https://github.com/ziegenberg/pi-skill-acli)
(MIT, © Daniel Ziegenberg), vendored here so it can be installed from this marketplace. Changes on
top of upstream:

- **Headless-environment authentication** — `--web` OAuth cannot complete in a container (loopback
  callback, no browser); the token-on-stdin form is documented instead, plus a rule against passing
  a token as a command-line argument.
- **A Safety section** — treats every command that is not a read as a write and groups the writes
  by consequence (irreversible, reversible but disruptive, visible to others); makes `--yes` the
  user's approval, given in the conversation before the command runs, never the agent's own; and
  requires a `--count` blast-radius check before any `--jql`/`--filter` mutation.

`LICENSE` (MIT © Daniel Ziegenberg) is carried over unchanged.

## Install

```bash
claude plugin marketplace add ihudak/ai-workflows
claude plugin install acli@shipwright
```

To pick up later changes, then restart Claude Code:

```bash
claude plugin marketplace update shipwright
claude plugin update acli@shipwright
```

## Use

**There is no slash command.** The plugin ships one model-invoked skill, `acli`, and no
command: ask Claude in prose, and the skill loads when the request is about Jira or
Confluence. For example:

- "List my open work items in project PROJ, newest first."
- "Show PROJ-123 with its comments, then move it to In Review."
- "Show Confluence page 123456789 and summarise it." — the skill opens a page by its id.

Anything that is not a read — creating, editing, transitioning, deleting, commenting — is a
write, and the skill asks you to approve the exact set in the conversation before it runs.
A bulk change by JQL or filter is counted first, so you see how many items it touches.

## Authenticate

On a desktop, `acli auth login` (Jira and Confluence together) opens a browser for OAuth.
**In a container or over SSH that cannot work** — the OAuth callback needs a browser and a
loopback port — so use an API token instead, and pass it **on standard input**, never as a
command-line argument, where it would land in your shell history and the process list:

```bash
acli jira auth login --site yoursite.atlassian.net --email you@example.com --token < ~/.atlassian-api-token
acli jira auth status
```

Create the token in your Atlassian account settings, under *Security → API tokens*, and keep
the file readable by you alone (`chmod 600`).

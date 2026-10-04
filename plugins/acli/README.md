# acli — Atlassian CLI skill

An Agent Skill teaching AI agents to drive the official Atlassian CLI
([`acli`](https://developer.atlassian.com/cloud/acli/)) for Jira and Confluence: JQL search, work
items, comments, links, attachments, watchers, projects, sprints, boards, filters, and Confluence
spaces, pages, and blog posts.

The skill only needs the `acli` binary on `PATH`; it authenticates via `acli … auth login`.

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

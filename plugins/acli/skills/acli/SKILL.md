---
name: acli
description: Interact with Atlassian Cloud (Jira and Confluence) via the acli CLI. Use for Jira work items (search with JQL, view, create, edit, transition, assign, comment, link, clone, delete, archive), projects, sprints, boards, filters, and Confluence pages, spaces, and blog posts. Requires acli to be installed and authenticated.
---

# Atlassian CLI (acli)

Interact with Atlassian Cloud — Jira work items, projects, sprints, boards, filters, and
Confluence content — using the `acli` CLI.

## Prerequisites

- `acli` must be installed (`acli --version` to check) and authenticated
  - OAuth (Jira + Confluence together): `acli auth login`
  - Product-scoped OAuth: `acli jira auth login --web` / `acli confluence auth login`
  - API token: `acli jira auth login --site <site>.atlassian.net --email <you>@... --token`
  - Verify with `acli auth status` (global) or `acli jira auth status` / `acli confluence auth status`
- For multi-account setups, switch the active account with `acli jira auth switch` /
  `acli confluence auth switch`

- **Headless environments (containers, CI, remote shells):** `--web` OAuth cannot complete, because
  the callback is a loopback URL only a browser on the same machine can open. Use the API-token
  form and feed the token on **stdin**:

  ```bash
  echo "$ATLASSIAN_API_TOKEN" | acli jira auth login \
      --site "<site>.atlassian.net" --email "<you>@example.com" --token
  ```

  `acli` stores profiles *and* credentials under `~/.config/acli`, so wherever that directory
  persists, one login serves every later session.
- **Never pass a token as a command-line argument.** It lands in shell history and in the process
  list. Pipe it on stdin as above, never echo it back into the conversation, and never write it to
  a file in the repository.

> **Note:** `acli` has no global `--site`/`--account` flag. The active account is chosen via
> `acli <product> auth switch`. Targeting a different project is done per-command with
> `--project`/`--key`, not a global flag.

## Safety

`acli` writes to live Jira and Confluence. **Every command that is not a read is a write** — reads
are `view`, `list`, `search`, `status`, the `list-*` commands, `link type`, `comment visibility`,
and the `--generate-json` templates (`auth` commands change only your local login). Ask the user
before running any write, naming the command and what it will touch.

**`--yes`/`-y` is the user's approval, never yours.** Commands that act on several items prompt for
confirmation, and an agent's shell cannot answer that prompt — so the approval happens in the
conversation first, and only then do you add `--yes` to run it. Never add it on your own initiative.
Every `--yes` in the examples below stands for that approval having been given.

The writes that matter most:

**Irreversible:** `jira workitem delete`, `jira project delete`, `jira sprint delete`,
`jira board delete`, `jira field delete`, `jira workitem comment delete`,
`jira workitem attachment delete`, `confluence space delete`.

**Reversible but disruptive:** `jira workitem archive`, `jira project archive`,
`confluence space archive`, bulk `jira workitem edit`, `jira workitem transition`,
`jira workitem comment create` and `--edit-last` (post immediately and notify watchers),
`jira sprint update --state closed`, `jira workitem link delete`.

**Visible to others:** `jira workitem create` / `create-bulk`, `assign`, `clone`,
`comment update`, `watcher remove`, `jira filter update` (shared filters change for everyone who
uses them), `jira project` / `board` / `sprint` creates and updates, and Confluence `space` and
`blog` creates and updates.

The `--key`, `--jql` and `--filter` selectors can hit hundreds of items in one command. Before any
mutating command driven by `--jql` or `--filter`, count the blast radius first and show the user
the number:

```bash
acli jira workitem search --jql "<the same jql>" --count
```

Use `--yes` only after the user has approved that exact set of items.

## Work Items

> **Important:** Jira comments are posted **immediately** and notify watchers — there is no
> draft/review concept in `acli`. When iterating on feedback, avoid posting many comments in a
> loop: use `acli jira workitem comment create --edit-last` to amend your own most recent
> comment, or update it by ID with `acli jira workitem comment update`. See [Comments](#comments).

```bash
# Search work items with JQL (the primary way to list issues)
acli jira workitem search --jql "project = <project_key>"
acli jira workitem search --jql "assignee = currentUser() AND status != Done"
acli jira workitem search --jql "project = <project_key>" --paginate          # fetch all pages
acli jira workitem search --jql "project = <project_key>" --count             # just the count
acli jira workitem search --jql "project = <project_key>" --fields "key,summary,status" --csv
acli jira workitem search --jql "project = <project_key>" --limit 50 --json

# Search using a saved filter ID
acli jira workitem search --filter <filter_id> --web

# View work item details (key is a positional argument)
acli jira workitem view <issue_id>
acli jira workitem view <issue_id> --fields "*all"
acli jira workitem view <issue_id> --fields "summary,comment"
acli jira workitem view <issue_id> --json

# Create a work item
acli jira workitem create --summary "New Task" --project "<project_key>" --type "Task"
acli jira workitem create --summary "Bug" --project "<project_key>" --type "Bug" --assignee "@me" --label "bug,cli"
acli jira workitem create --from-file workitem.txt --project "<project_key>" --type "Bug"
acli jira workitem create --generate-json            # print a JSON template
acli jira workitem create --from-json workitem.json  # create from JSON

# Bulk create from JSON or CSV
acli jira workitem create-bulk --generate-json
acli jira workitem create-bulk --from-json issues.json
acli jira workitem create-bulk --from-csv issues.csv

# Edit work items (accepts --key, --jql, or --filter selectors; see Selectors)
acli jira workitem edit --key "<issue_id_1>,<issue_id_2>" --summary "New summary" --yes   # after approval
acli jira workitem edit --jql "project = <project_key> AND status = Open" --assignee "@me" --yes   # after approval
acli jira workitem edit --key "<issue_id>" --remove-assignee --yes        # after approval

# Transition (move to another status)
acli jira workitem transition --key "<issue_id>" --status "In Progress"
acli jira workitem transition --jql "project = <project_key>" --status "Done" --yes   # after approval

# Assign (--assignee accepts @me, default, or an email/account ID)
acli jira workitem assign --key "<issue_id>" --assignee "@me"
acli jira workitem assign --jql "project = <project_key>" --assignee "user@atlassian.com" --yes   # after approval
acli jira workitem assign --key "<issue_id>" --remove-assignee

# Clone within the same site, or to another project/site
acli jira workitem clone --key "<issue_id>" --to-project "<project_key>"

# Delete / archive / unarchive
acli jira workitem delete --key "<issue_id_1>,<issue_id_2>" --yes   # after approval
acli jira workitem archive --jql "project = <project_key> AND status = Done" --yes   # after approval
acli jira workitem unarchive --key "<issue_id>"
```

## Comments

```bash
# Add a comment (posted immediately, notifies watchers)
acli jira workitem comment create --key "<issue_id>" --body "This is a comment"
acli jira workitem comment create --jql "project = <project_key>" --body-file comment.txt --yes   # after approval
acli jira workitem comment create --key "<issue_id>" --body "Updated" --edit-last   # amend your last comment
acli jira workitem comment create --key "<issue_id>" --editor                       # open $EDITOR

# List comments
acli jira workitem comment list --key "<issue_id>"

# Update a comment (by comment ID)
acli jira workitem comment update --key "<issue_id>" --id 10001 --body "Updated text"
acli jira workitem comment update --key "<issue_id>" --id 10001 --body "Internal" --visibility-role "Administrators"
acli jira workitem comment update --key "<issue_id>" --id 10001 --body-adf comment.adf.json   # ADF body

# Delete a comment
acli jira workitem comment delete --key "<issue_id>" --id 10023

# Discover visibility options (roles/groups) for restricted comments
acli jira workitem comment visibility --role --project "PROJ"
acli jira workitem comment visibility --group
```

## Selectors (JQL, Keys, Filters)

Most mutating work-item commands — `edit`, `transition`, `assign`, `comment create`, `clone`,
`delete`, `archive` — accept the **same three selectors** to choose which work items to act on:

- `--key "<issue_id_1>,<issue_id_2>"` — explicit comma-separated keys
- `--jql "project = <project_key> AND ..."` — a JQL query
- `--filter 10001` — a saved filter ID

```bash
# Same edit applied to everything matching a JQL query
acli jira workitem edit --jql "project = <project_key> AND status = Open" --assignee "@me" --yes   # after approval

# Act on a saved filter's results
acli jira workitem transition --filter <filter_id> --status "Done" --yes   # after approval

# Bulk via a file (one key per line, or comma/space separated)
acli jira workitem delete --from-file issues.txt --yes   # after approval
```

These commands prompt for confirmation before acting on multiple items. Add `--yes` (`-y`) only
once the user has approved that exact set — see [Safety](#safety) — and `--ignore-errors` to continue
past failures when operating on many items.

JQL tips:
- `currentUser()` — the authenticated user
- `project = <project_key>`, `status = "In Progress"`, `priority = High`
- Combine with `AND` / `OR`; quote values containing spaces

## Links, Attachments & Watchers

```bash
# Links
acli jira workitem link create --out <issue_id> --in <issue_id> --type "Blocks"
acli jira workitem link create --generate-json            # template for --from-json bulk linking
acli jira workitem link list --key "<issue_id>"
acli jira workitem link delete --id 10001
acli jira workitem link type                              # available link types

# Attachments
acli jira workitem attachment list --key "<issue_id>"
acli jira workitem attachment delete --id 12345

# Watchers
acli jira workitem list-watchers --key "<issue_id>"            # preferred (watcher list is deprecated)
acli jira workitem watcher remove --key "<issue_id>" --user 5b10ac8d82e05b22cc7d4ef5
```

## Projects

```bash
# List
acli jira project list --recent          # up to 20 recently viewed
acli jira project list --paginate        # all projects
acli jira project list --limit 50 --json

# View
acli jira project view --key "<project_key>"

# Create (company-managed projects can be cloned with --from-project)
acli jira project create --key "NEW<project_key>" --name "New Project"
acli jira project create --from-project "<project_key>" --key "<new_project_key>" --name "New Project" --lead-email "user@atlassian.com"

# Update
acli jira project update --project-key "<project_key>" --name "Renamed Project"

# Delete / archive / restore
acli jira project delete --key "<project_key>"
acli jira project archive --key "<project_key>"
acli jira project restore --key "<project_key>"
```

## Sprints

```bash
# View a sprint
acli jira sprint view --id 123

# List work items in a sprint (requires board + sprint IDs)
acli jira sprint list-workitems --board 6 --sprint 1
acli jira sprint list-workitems --board 6 --sprint 1 --jql "status != Done" --json

# Create a sprint on a board
acli jira sprint create --name "Sprint 1" --board 5
acli jira sprint create --name "Sprint 2" --board 5 --start 2025-01-01 --end 2025-01-14 --goal "Q1 work"

# Update (name, goal, state, dates)
acli jira sprint update --id 37 --name "Sprint 1 - Final"
acli jira sprint update --id 37 --state closed

# Delete one or more sprints
acli jira sprint delete --id 37,42,55 --yes   # after approval
```

## Boards

```bash
# Search boards
acli jira board search
acli jira board search --project "<project_key>" --type scrum
acli jira board search --name "platform" --json

# View a board and its sprints/projects
acli jira board view --id 123
acli jira board list-sprints --id 123 --state active,closed
acli jira board list-projects --id 123

# Create / delete
acli jira board create --name "My Scrum Board" --type scrum --filter-id 10040 --location-type project --project "<project_key>"
acli jira board delete --id 123,456 --yes   # after approval
```

## Filters

```bash
# List your filters / favourites
acli jira filter list --my
acli jira filter list --favourite

# Search filters
acli jira filter search --owner user@atlassian.com --name "report"

# View and reuse a filter (its ID feeds `workitem search --filter`)
acli jira filter view --id 12345
acli jira workitem search --filter 12345

# Update
acli jira filter update --id 10001 --name "Open bugs" --jql "project = TEST AND status = Open"
```

## Confluence

```bash
# Spaces
acli confluence space list
acli confluence space list --type personal --json
acli confluence space view --id 123456 --include-all
acli confluence space create --key SPACEKEY --name "Space Name" --description "..."
acli confluence space update --key SPACEKEY --name "New Name"
acli confluence space archive --key SPACEKEY
acli confluence space restore --key SPACEKEY

# Pages (view by ID)
acli confluence page view --id 123456789
acli confluence page view --id 123456789 --body-format storage --json

# Blog posts
acli confluence blog list --space-id 12345 --limit 25
acli confluence blog view --id 98765 --body-format atlas_doc_format
acli confluence blog create --space-id 12345 --title "Release Notes" --body "<p>Content</p>"
acli confluence blog create --generate-json                 # template for --from-json
acli confluence blog create --from-json ./blog_payload.json
```

## Authentication

```bash
# Global OAuth (covers Jira + Confluence together)
acli auth login
acli auth status
acli auth switch
acli auth logout

# Product-scoped (OAuth or API token)
acli jira auth login --web
acli jira auth login --site "mysite.atlassian.net" --email "user@atlassian.com" --token   # token via stdin
acli jira auth status
acli jira auth switch --site mysite.atlassian.net --email "user@atlassian.com"

acli confluence auth login
acli confluence auth status
```

## Tips

- Prefer `--json` (or `--csv`) and pipe through `jq` for structured output
- Use `--paginate` to fetch every page of a list; `--limit N` to cap a single page
- `acli jira workitem view` takes the key as a positional argument: `acli jira workitem view <issue_id>`
- `--assignee` accepts `@me`, `default`, an email, or an account ID
- Mutating commands that act on multiple items prompt for confirmation — add `--yes` (`-y`) only after
  the user has approved that exact set in the conversation ([Safety](#safety))
- Reuse saved filters: `acli jira filter view --id <id>` to find a filter ID, then `acli jira workitem search --filter <id>`
- `acli` covers Jira and Confluence as separate auth contexts: `acli jira ...` vs `acli confluence ...`
- For Rovo Dev (Atlassian's AI coding agent) use `acli rovodev ...` — it has its own `acli rovodev auth login`

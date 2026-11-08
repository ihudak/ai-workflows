# Getting started

This page takes you from zero to your first successful run — install the plugin, set the environment variables it reads, and run [`/idea`](commands/idea.md) end to end. Once you have done this once, [Workflow overview](workflow.md) shows the whole pipeline and [Roles and phases](roles-and-phases.md) says what your role owns at each step.

## Install

### 1. Add this marketplace to Claude Code (once)

```bash
claude plugin marketplace add ihudak/ai-workflows
```

### 2. Install plugins

```bash
claude plugin install product-workflows@shipwright
```

`product-workflows` is the plugin this documentation covers. It declares two hard dependencies, installed automatically alongside it: `workflows-core`, its shared foundation, and `prose-style`, whose `prose-style-checker` is [`/epics`](commands/epics.md)'s primary style checker and the unconditional Phase 3.5 pass every PRD-authoring command here runs. Neither is optional here — an absent `prose-style` would leave those commands with no absent case to degrade into, which is why the plugin declares it rather than reaching for it at runtime. The companion `dev-workflows` plugin is not a dependency in either direction: it produces `specification.md`'s downstream consumer (`/dev-workflows:design`), but `product-workflows` installs and runs without it, against a specs tree someone else's engineering work will eventually fill in. A PE installs it all the same, for one command: `/dev-workflows:conformance <PRD-KEY>`, the PE's check of a PRD once every Epic has merged, is a `dev-workflows` command, and the only one the PE role runs (`claude plugin install dev-workflows@shipwright`).

**What you also need, and it is not a plugin.** Claude Code itself — no other agent runs these plugins — with a session started on Opus 5.5 or later, on macOS, Linux or WSL2 rather than native Windows, and `git`, `bash` 5 and `python3` 3.11 on your `PATH`, plus `jq` for the status line and `/workflows-core:diagnose-session`; the repo-root [Prerequisites](https://github.com/ihudak/ai-workflows#prerequisites) give each one's minimum version and the reason for it. Beyond those, `gh`, when present, opens the pull requests it drafts — without it a run reports the branch it pushed and leaves the pull request to you. The specs repo is the one markdown tree the pipeline *writes*; it also reads your product-docs clone under `$DOCS_PATH` and, where a command grounds on code, the clones under `$REPOS_PATH`, which are no markdown tree at all. If you keep your work in a tracker as well, syncing the two is yours to arrange; no command here learns whether one exists.

**What you do not need for this plugin.** The marketplace also ships `acli` and `guideline-reviewers` — none of them is used by `product-workflows`. Install them if you want them for their own sake; see the [marketplace README](https://github.com/ihudak/ai-workflows#readme).

## Update

```bash
claude plugin marketplace update shipwright
claude plugin update product-workflows@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update product-workflows@shipwright` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same thing with a picker. The first line alone is not enough, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one.

## What you set on your machine

`product-workflows` reads four environment variables. One is required for the pipeline to have anywhere to write (`SPECS_PATH`). The other three are optional, and each behaves differently when it is missing. `REPOS_PATH` falls back to `/workspace`; where no entry of it exists, `/create-ard`, `/specify`, `/update-spec`, `/epics` with its code scan on, `/prd-ground` and `/brd-split`'s *Ground now* ask you to set it, and `/prd-ground` offers only *Set REPOS_PATH* or *Cancel*. An unset `ARCHITECTURE_REPO_PATH` turns architecture grounding `OFF`, with a line naming the variable, and the run goes on without it. `DOCS_PATH` falls back to `/workspace/docs`, and any miss there is a silent skip that never asks and never stops the run. [Environment](reference/environment.md) has the detail for each.

### `SPECS_PATH`

The **shared, team-visible repository for the AI-authored documents** — the idea brief, the Product Requirements Document, the ARD, `specification.md`, and every BRD-route artifact, each under a kind-prefixed folder — `specifications/PRD-<KEY>-<slug>/` or `specifications/BRD-<KEY>-<slug>/`, with `EPIC-` folders below a PRD. This is the reason a second store exists at all: it is the medium through which one role hands work to the next. A producing command lands its artifact on the specs repo's default branch, and the next command in the chain does not read it from anywhere else: while it sits on an unmerged branch the commands cut, that command stops and names the branch, and one written only to disk, or committed only to a branch of your own, it treats as absent — most commands fall back from that, a few stop. See [Roles and phases](roles-and-phases.md) for what each seam hands over and what happens when an artifact is missing or stuck on an unmerged branch. Set it to the root of a dedicated specs repository, the directory that holds `specifications/`, never to `specifications/` itself: a run that resolves an address against the latter stops and names the value to set instead ([Environment](reference/environment.md)).

### `REPOS_PATH`

Where your mounted implementation and design code clones live — one directory, or a colon-separated list of them. It has a sensible built-in default, so most readers never need to set it at all; see [Environment](reference/environment.md) for the exact value and resolution order. [`/create-ard`](commands/create-ard.md) and `/idea` (with `--ground-code`) list top-level directories under `$REPOS_PATH` and offer them to you, so a repo renamed on disk is offered under its new name rather than lost — except where `/idea`'s `--ground-code <repo>,<repo>` names one, since every comma-separated part must match a top-level **basename** to be read as a repo at all. [`/prd-ground`](commands/prd-ground.md) instead grounds against the repositories `grounding/baselines.md` pins by commit.

### `ARCHITECTURE_REPO_PATH`

A clone of your organisation's architecture repository — its technology radar, standards, principles, patterns and ADRs. Set it and `/create-ard`, [`/specify`](commands/specify.md) and [`/update-spec`](commands/update-spec.md) ground their work in it: an ARD cites the decisions it settles and records every departure as an open question, and a specification records a conflict as an open question; `/dev-workflows:design` does the same for a design, recording each departure under its risks. Unset, they still read the team's harvested decisions under `$SPECS_PATH/architecture/` where they exist, and otherwise run exactly as without it. Grounding never writes, fetches or pulls it; [`/product-workflows:promote-decisions`](commands/promote-decisions.md) is the one command that writes an architecture repository, proposing ADRs on a branch of their own.

### `DOCS_PATH`

Your shipped product documentation's clone — **read-only** in its role as a grounding root, which is the only role this plugin gives it. Nine of this plugin's commands ground against what is already published, so a new draft does not contradict or duplicate an existing page: `/idea`, [`/create-prd`](commands/create-prd.md), [`/update-prd`](commands/update-prd.md), `/create-ard`, `/specify`, `/update-spec`, `/epics`, [`/brd-intake`](commands/brd-intake.md), and `/prd-ground`. The plugin never writes to `DOCS_PATH`; every miss — unset, missing, or no markdown found — is a silent, non-blocking skip. Disable per-run with `--no-docs` — and, in `/prd-ground`, also with `--no-code` — or override the root with `--docs <path>`, which all nine parse.

### Claude Code's skill-listing budget

**Set this once, in `~/.claude/settings.json`, whichever plugins you install.** Claude Code shows the model one list of every installed plugin's skills and model-invocable commands, and gives that list 1% of the context window — 8,000 characters in a 200K-token session, and in every subagent on a 200K model. Past that it shortens every description in the list, and the model can no longer tell which skill fits a task. This marketplace's commands are nearly all typed-only and take no room in the list — the few another command runs for you, such as `/prd-ground`, do — and its skills do too, and so does every other plugin, Claude Code's own skills and your personal ones: every plugin of the `shipwright` marketplace, installed together, takes about 5,800 characters. Add this top-level key to the settings file:

```json
"skillListingBudgetFraction": 0.025
```

That gives 20,000 characters at 200K and 100,000 at 1M; a session pays only for what is listed, never for the budget, and the change applies from the next session. **Check that it is enough**: start one session with `claude --debug`, then search `~/.claude/debug/latest` for `Skill listing over budget: <N> skills, <X> chars > <Y> budget`. If that line is there, the list still overflows: set the fraction to at least X ÷ 800,000 (for X = 32,000, `0.04`), or turn off skills you do not use with `/skills`. The `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable sets a fixed number of characters instead, and overrides the setting.

## Install the status line

**Worth doing before your first real run.** The command that installs it ships in the companion `workflows-core` plugin rather than this one, so its form is qualified:

```
/workflows-core:statusline
```

It puts a multi-line status line at the bottom of your terminal — session identity, git state, context usage, running cost, tokens and rate limits — so you can watch a long command spend while it runs. Given `jq`, it also enables the **status-line cross-check**: every command of this plugin that writes a cost entry gains it, so each cost entry then carries Claude Code's own figure for the run beside the one computed from the bundled price table, and a gap between the two over a window with no compaction says the price table needs refreshing. Skip it and you still get a cost report, with nothing to check it against; even with it, a session's first cost phase has no baseline yet and leaves the second figure out. See [Session cost](reference/session-cost.md) for what an entry holds; the companion plugin's Session cost page describes the cross-check in full. The command is idempotent, backs up anything it would overwrite, and changes no command's behaviour.

Claude Code ships its own built-in `/statusline` command, so typing the bare form reaches that instead of the companion plugin's — always use the qualified `/workflows-core:statusline`.

## Where to run it

Run the plugin in an AI container — strongly recommended: a command run there can reach only what you mount into it and the network you allow.

Two commands start from text that often comes from outside your team. `/brd-intake` reads a customer's document, every file it links and the images it links; `/idea` reads the note you hand it — a saved community post among them — and the pages and images that note links. Both walk the links read-only, and a link to a web address is recorded and never fetched. `/brd-intake` asks before it takes a file from outside the document's own folder, and asks you to convert one that is neither markdown nor an image; `/idea` asks before it reads further than two levels of links, twelve pages or six images. Later, [`/brd-reconcile`](commands/brd-reconcile.md) reads the review the customer sends back. Every agent these commands dispatch treats what it reads as data that never adds a task or changes a verdict, and reports text that tries to steer it; the command prints each report under **Untrusted-content notices** in its final report. A notice never stops a run, so open the file it names and decide what to do about it. The commands themselves run shell commands with your permissions, which is what a container limits: on your own host, hand the plugin only documents you would open yourself.

## Before you start

`SPECS_PATH` must name the root of your specs repository, the directory that holds `specifications/`. Every command hands its document to the next one through that repository's default branch, so check three things first:

- **It is a git repository.** Where it is a directory that is not one, each run prints a notice naming `SPECS_PATH` and goes on: it writes its document, but commits nothing and hands nothing off.
- **Its default branch has a commit.** The next command checks the previous one's document against that branch, and stops where the branch does not exist yet.
- **It has an `origin` remote, for the pull requests.** Without one, a handoff still commits on a plugin branch, but pushes nothing and opens no pull request, and it reports that the phase is not handed off; the run says so before it asks. You then merge that branch into your default branch yourself.

```bash
export SPECS_PATH="$HOME/specs"             # the repository root that holds specifications/
git -C "$SPECS_PATH" rev-parse --git-dir     # succeeds only in a git repository
git -C "$SPECS_PATH" remote get-url origin   # prints where pull requests go; an error means no origin
```

Put the `export` line in your shell profile, so every Claude Code session starts with it.

## Your first run

`/idea` is the pipeline's entry point. It takes **one argument you choose yourself** — the key that names the folder this idea will live in — because there is nowhere keyless to write: the brief lands in its final folder on the first write and is never moved afterwards. Point it at whatever you already have in mind: an inline prompt, or a markdown file with `@path`.

```
/idea ACME-77 a lightweight way for on-call engineers to silence a noisy alert for one hour without editing the alerting rule
```

**Type the command.** Every command in this plugin but one is typed-only (`disable-model-invocation: true`): it stays out of the list of skills the model picks from, which keeps that list inside Claude Code's budget, so asking in prose — "turn this idea into a brief" — does not start it. The one is `/prd-ground`, which [`/brd-split`](commands/brd-split.md)'s *Ground now* runs for you; it refuses to start any other way you did not type it.

`ACME-77` is yours to invent — nothing looks it up, and no tracker is read. It only has to match `^[A-Z][A-Z0-9_]*(-\d+)+$`.

Here is what to expect:

1. **A bounded grill.** `/idea` asks you up to ten questions, one at a time, to sharpen the idea before writing anything — scope, who it is for, what "done" looks like. Answer as best you can. A high-impact question still open when the grill stops, one you could not answer included, is written into the brief as a `[NEEDS CLARIFICATION]` marker, three at most — and any open marker leaves the brief a draft (`status: draft`), not a refined brief. (`--deep` drops the cap and grills to convergence instead.)
2. **A written brief.** It writes `idea.md` — a lean one-page brief — into `$SPECS_PATH/specifications/PRD-ACME-77-<slug>/`, creating that folder if it does not exist. If `DOCS_PATH` is set and readable, the idea is also checked against what is already documented.
3. **A handoff, for a refined brief only.** Where no marker is left open (`status: refined`), it offers to commit the brief, push it, and open a pull request against the specs repo's default branch. Merge that pull request — or, with no `origin` remote, merge the plugin branch it committed on into your default branch yourself — then run [`/create-prd`](commands/create-prd.md) `ACME-77`, which finds `idea.md` in the same folder and takes over. While the pull request is still open, `/create-prd ACME-77` stops and names it. **A draft is never handed off**, and nothing is asked; the run names two ways forward instead. The recommended one is to re-run `/idea ACME-77` with the same source, which re-opens the brief and puts each open marker to you; closing them all makes it refined, and that run offers the handoff. The other, for a PRD grilled from the draft as it stands, is `/create-prd ACME-77 @<the absolute path of idea.md>`, which reads the brief where it sits.

## Your first BRD-route run

When you start from a business requirements document (BRD) a customer handed you, rather than from your own idea, [`/brd-intake`](commands/brd-intake.md) takes the place of `/idea`, and the route is longer. The document is copied in and split into slices; each slice is checked against the code and its open questions are decided; and the questions only the customer can answer go to them in a package. This section is one pass through it. [BRD workflow](brd-workflow.md) has the whole route, its diagram and every flag.

**Use a key of its own.** A key names one folder, and `ACME-77` already names the idea's folder above; `/brd-intake` refuses a key that names an idea-route PRD folder. This walkthrough uses `ACME-80` for the BRD and `ACME-80-01` for its first slice.

The commands, in order:

```
/brd-intake ACME-80 @orders-brd.md
/brd-split ACME-80 "cover order entry and the monthly report first"
/prd-ground ACME-80-01 --repos orders-service,web-app
/brd-split ACME-80-01
/brd-interview ACME-80-01
/brd-package ACME-80-01
/brd-reconcile ACME-80-01 @<the review file the customer returned>
```

**Merge each pull request before you type the next command.** Every step ends with the same handoff offer as `/idea`, and most steps read the previous step's files from the default branch and stop, naming the pull request, while it is still open. With no `origin` remote, merge each plugin branch into your default branch yourself.

1. **Intake.** `/brd-intake ACME-80 @orders-brd.md`. The document must already be markdown: a PDF is refused, never converted. The run walks every link the document makes and asks before it takes a file from outside the document's own folder. It copies the document and what it links into a new `BRD-ACME-80-<slug>/` folder byte for byte, has every linked image transcribed, extracts a `[BR#n]` requirement inventory, asks you to confirm each defect it suspects in the document, and writes a coverage ledger with every row `unallocated`. Merge its pull request.
2. **Carve slices.** [`/brd-split`](commands/brd-split.md) `ACME-80 "<how to cut it>"`. On the root, a slicing instruction in your own words is mandatory while any row is still `unallocated`. The run proposes slices for you to confirm, offers each a key — `ACME-80-01`, `ACME-80-02` and so on, which you accept or replace — and creates each as a `PRD-` folder inside the BRD folder. Then it walks every ledger row to a fate: a named slice, deferred, rejected against a logged defect, or superseded. Merge its pull request: the next step stops until the slice's ledger and inventory are on the default branch. Its *Ground now* option waits for that merge and then runs step 4 for you, so do step 3 first.
3. **Prepare the slice for grounding.**
   - **Clone the code** the requirements are about under `$REPOS_PATH` (`/workspace` unless you set it), each clone checked out at the commit you want grounded. Grounding pins every repository at the commit it finds, and never switches a branch, fetches or pulls. Where you cannot clone the code, a PA or PE can run step 4 for you.
   - **Export any design frames** — screens or mockups, as images — into one folder per set under the slice's own `design/` directory, such as `BRD-ACME-80-<slug>/PRD-ACME-80-01-<slug>/design/checkout/`. Then run `/workflows-core:frames ACME-80-01`, which writes the index each set needs, and merge the pull request it opens. A set with no index is skipped, and step 5 then stops until the set is indexed and ground. With no `design/` folder at all, the design pass is skipped and the run says so.
4. **Ground.** [`/prd-ground`](commands/prd-ground.md) `ACME-80-01 --repos orders-service,web-app`. Without `--repos` it lists the clones it found and asks. It prints the cost first: every requirement is checked against every repository you name, and every finding is re-derived blind on Opus before it counts. It writes `[CG#n]` code findings and `[DG#n]` design findings under the slice's `grounding/`. Merge its pull request: the next step stops until the findings are on the default branch.
5. **Allocate the slice.** `/brd-split ACME-80-01`. On a slice it runs `allocate-only`: no instruction is needed and nothing is carved. It walks the slice's own rows to a fate, `covered-here` — built in this slice — among them. Merge its pull request.
6. **Decide.** [`/brd-interview`](commands/brd-interview.md) `ACME-80-01`. It tags every open question `[G]` (answered from the findings, never asked), `[V]` (asked of you, your reasons recorded) or `[C]` (held for the customer), then writes the decision register, `decisions.md`, and the round's record. Merge its pull request: the next step stops until the register is on the default branch. Where it offers another round instead of packaging, run it again. Where it settled every question from the findings, nothing goes to the customer, and it offers the hand-over in step 10 straight away.
7. **Package.** [`/brd-package`](commands/brd-package.md) `ACME-80-01`. It attacks its own package first and asks you to settle each finding. Then it writes a self-contained prompt for the customer, a short delivery note and a dated `bundle-<YYYYMMDD>/`. Merge its pull request — where the customer pulls the specs repository, the bundle is there only once it is merged — then send the delivery note.
8. **Wait for the customer.** They review the bundle with an AI agent of their own and nothing installed, and return one file: committed beside the bundle by pull request, or sent back to you. The route waits here.
9. **Reconcile.** Run [`/brd-reconcile`](commands/brd-reconcile.md) `ACME-80-01 @<path>` on the file they sent; where they committed it beside the bundle, merge their pull request and run `/brd-reconcile ACME-80-01` with no path. It freezes each answer as a `[CD#n]` decision once you confirm it against the customer's own words, applies their corrections, and sweeps what the answers overturned. Merge its pull request.
10. **Hand over.** Where nothing is left to go round again, `/brd-reconcile` offers [`/specify`](commands/specify.md) `ACME-80-01` and [`/create-ard`](commands/create-ard.md) `ACME-80-01`, and `/create-prd ACME-80-01` where the slice is PRD-eligible — no claimed row still `unallocated`, and at least one `covered-here`. Otherwise it names the step to repeat, such as another `/brd-interview` round, another `/brd-package`, or `/prd-ground ACME-80-01 --rebaseline` where the customer challenged a claim about the code.

Repeat steps 3 to 10 for every other slice the split carved. The [Glossary](reference/glossary.md) explains the route's terms — slice, ledger, `covered-here`, `[G]`/`[V]`/`[C]` and the rest.

From here, [Workflow overview](workflow.md) shows where every other command sits relative to `/idea` and `/brd-intake`, and [Roles and phases](roles-and-phases.md) says what happens at each handoff along the way.

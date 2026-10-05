---
name: harvest-decisions
description: Harvest the decisions of every ARD on the specs repository's default branch into the team architecture knowledge base at $SPECS_PATH/architecture/ — one record per [AD#N], reconciled on every run (superseded, withdrawn, applied in, deviated in), never deleted, handed off by pull request. Deterministic — a bundled script, no model judgment. /create-ard grounds on the live records.
allowed-tools: Read Bash Glob Grep Skill
---

Harvest the ARDs' decisions into the team architecture knowledge base: $ARGUMENTS

`/harvest-decisions` turns every `[AD#N]` in the ARDs on the specs repository's default branch into a record under `$SPECS_PATH/architecture/` — the folder `/create-ard`'s architecture grounding reads as its team root — and reconciles the records it wrote before: a decision its own ARD supersedes or withdraws, or that a later ARD names in `**Supersedes:**`, changes status; the designs and other artifacts citing it are listed on it; nothing is ever deleted. The format is `workflows-core:architecture-kb` (Skill(skill: "workflows-core:reference", args: "architecture-kb")). The work is the bundled script `${CLAUDE_PLUGIN_ROOT}/scripts/architecture-harvest.py`, which reads the default branch only, so a run on an unchanged branch changes nothing. This command dispatches no agent, routes no model and emits no cost or feedback entry.

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Usage: `/product-workflows:harvest-decisions [--dry-run]` — `--dry-run` shows the plan and stops. Any other argument stops the run with this usage line.

## Phase 0 — Preflight

1. **`$SPECS_PATH` unset** → stop: `HARVEST_NEEDS_SPECS_PATH: set SPECS_PATH to your specs repository and run /product-workflows:harvest-decisions again.`
2. **`command -v python3` fails** → stop: `/product-workflows:harvest-decisions needs python3 — the harvest is a bundled script.`
3. **`specs-preflight`** (`workflows-core:specs-repo-git` §3, Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")) with an empty run key set — a keyless run, so §3.5's row B4 moves the checkout off any unmerged plugin branch. Keep its `<default-ref>` and flags. `specs_git: misrooted` → stop with its notice: the script reads the repository's top level.
4. **The checkout must be on the default branch.** `git -C "$SPECS_PATH" branch --show-current` other than `<default-ref>`'s branch (`<default-ref>` without its `origin/`) → stop, naming the branch and what kept the preflight there (§3.3: G0 a detached HEAD, G1 a dirty path, G2 your own branch): the `kb/` branch is cut from the checkout, so a harvest from anywhere else would carry that branch's commits into its pull request.
5. **An earlier harvest not yet merged stops the run.** Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/architecture-harvest.py" --specs "$SPECS_PATH" --ref "<default-ref>" --pending-kb`; it prints `{"pending": [<branch>, …]}` — the `kb/` branches, local or `origin/`, that are neither ancestors of `<default-ref>` nor carry an `architecture/` tree it has held, so a squash or rebase merge counts as merged. Exit 2 → stop with its stderr line. Any pending → stop, naming each branch and, where `gh` is available, its open pull request (`gh pr list -R <owner/repo> --head <branch without origin/> --state open --json url`): `An earlier harvest is not merged yet: <branch> [<pull request>]. Merge it — or delete the branch if you closed its pull request — and run /product-workflows:harvest-decisions again; a second harvest would re-propose what that one carries.`

## Phase 1 — Plan

Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/architecture-harvest.py" --specs "$SPECS_PATH" --ref "<default-ref>" --layout prd --dry-run`.

- **Exit 2** → stop with its stderr line. Nothing was written.
- **Exit 0** → parse the JSON plan from stdout; keep its `sha`.
- **`no_ards: true`** → report `Nothing to harvest: no ARD on <default-ref>.` and every problem, then stop.
- **`create`, `update`, `supersede`, `withdraw` and `files` all empty** → report `Knowledge base up to date: <live> live records.` and every problem, then stop.
- **`--dry-run`** → print the plan below and stop.

**The plan, as printed:** one line per non-empty change kind with its count and ids (`create`, `update`, `supersede`, `withdraw`, then `kept`), every path in `files` — so a change to `index.yaml` or `README.md` alone is shown, never only asked about — the `live` count, then each problem as `<kind> — <file>:<line> — <detail>` followed by the fix `workflows-core:architecture-kb` §8 gives for that kind.

## Phase 2 — Apply

`choices: ["Apply", "Cancel"]`. **Cancel** → stop; nothing written. **Apply** → run the script again without `--dry-run`, with `--ref <sha> --layout prd` — the dry run's commit, so the plan it writes is the one shown, by construction. Exit 2 → stop with its stderr line. The written paths are the plan's `files`.

## Phase 3 — Hand off

Invoke Skill(skill: "workflows-core:reference", args: "phase-handoff") and run its §4.3 push-target probe, then present its **advisory** array verbatim — no command stops on the knowledge base; `/create-ard` reads the working copy:

`choices: ["Branch + commit + push + open PR to main (Recommended)", "Just write the files — I'll handle git (no command stops on this; what reads it reads your working copy)", "Cancel"]`

On the first choice, execute `handoff-to-main` (Skill(skill: "workflows-core:reference", args: "phase-handoff handoff-to-main"), §2) with `prefix: kb`; no `feature_folder` (§2.2's keyless form names the branch `kb/harvest-<YYYY-MM-DD>`); `deliverable_paths` = the plan's `files`; `title: NOISSUE Harvest ARD decisions into architecture/`; and `body_facts` = the counts per change kind, the live count, the problem count and the `sha` harvested. Emit its §4.1 outcome line in the final report.

## Phase 4 — Terminal commit

Execute `commit-artifacts` (Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts"), §4) as the run's last action and emit its §6 outcome line, per that file's §7 caller contract — this run writes no bookkeeping file of its own, so it commits only what an earlier run left.

## Final report

The plan's counts and ids; every problem with its fix; the `Phase handoff:` outcome line; the `Specs repo:` outcome line; then `The next /product-workflows:create-ard grounds on <live> live records once this is on <default-ref>.`

# /docs-audit

Enumerates what documentation a product is missing — from its own code and from the committed documents in the specs tree — and writes a prioritised backlog you keep in the documentation repository.

## Who runs it

`/docs-audit` is the command between having a documentation portal and knowing what to put in it. It runs against a documentation repository that **already exists**, so on a fresh portal it follows [`/docs-init`](docs-init.md), and on one that has been filling up it runs again whenever the product grows a surface. [Workflow overview](../workflow.md) draws it in its own *Plan* group, reading the profile's recorded source repositories. **Nothing consumes the backlog automatically** — no command of this family opens it or takes a unit id from it — so the edge out of it is an operator's: you read it, pick a unit, and write that page. [The documentation workflow](../docs-workflow.md) is the written procedure for doing that, automated steps and manual ones alike.

It classifies as **SIGNIFICANT** — a cross-cutting synthesis of every scanned repository — and its review gate is Opus regardless of class (unless `--enforce-model` pins it to another model — `workflows-core:model-routing/classification` §10), because every command of the portal-building set that writes an artefact — `/docs-init`, `/docs-brand` and this one — passes a high-tier review with no tiering by unit. That is not every command in the plugin: `/document` in direct mode takes a style check and no review gate, `/release-notes` a light gate, `/docs-profile` no review gate at all, and `/docs-serve` writes no artefact and runs none.

**It writes no documentation content.** Its output is a coverage grid and a backlog: a table of the things a product could be documented against, a table of the pages those things earn, a written reason under every rank, and a proposed set of tutorial candidates for you to pick from. Turning one of those units into a page is a separate act, and the parts of it that no command does yet are written out as a manual procedure in [The documentation workflow](../docs-workflow.md).

## Synopsis

```
/docs-audit [<docs-repo-path>] [--audience user|engineering|both] [--refresh] [--threshold <n>] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]
```

Every recognized flag is stripped from the arguments before the remaining token is read as the optional docs-repo path — `--audience` and `--threshold` each together with the value after it, or that value would be read as the path. `--audience` takes `user`, `engineering` or `both` and defaults to `both`; it filters which units are minted and never which units the coverage grid counts. `--threshold <n>` takes a positive integer and sets the priority at or below which a unit has to be published for the backlog to count as done. `--refresh` re-derives the backlog against today's code instead of writing a new one; without it, a run that finds a backlog already there asks before doing anything.

All three run flags apply to this command. `--skip-costs` (or `WORKFLOWS_SKIP_COSTS`) skips Phase 9's session-cost entry, still advancing the checkpoint and dropping any deferred cost record a ceded `/prompt-brainstorm` or `/prompt-grill-me` run left pending in this session (`workflows-core:run-flags` §5 step 3) — see [Session cost](../reference/session-cost.md). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Phase 7's maintenance step to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance`: under the flag only real defects are persisted, never the in-session Lessons Learned report — `docs-workflows` ships no dedicated session-feedback reference page, so this paragraph is that explanation. `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `code-scanner`, `docs-auditor` (overriding its frontmatter Sonnet pin), `ia-planner` (overriding its frontmatter Opus pin), `docs-audit-reviewer` (overriding its frontmatter Opus pin) and `impl-maintenance` (or, under `--skip-feedback`, `defect-reporter` in its place) — to one model, bypassing the detection/Opus-review split described below.

## What it needs

- **A documentation repository that already exists** — resolved by `resolve-docs-repo` (`docs-workflow/repo-resolution.md` §1), the signal-positive ladder: the given path, else the working directory or `$DOCS_PATH` where either carries a documentation signal, else a search one level under `$REPOS_PATH`, else it asks. The rung that answered is always reported.
- **The code repositories the portal documents.** Read from the profile's `source_repos[]` where `/docs-init` or an earlier audit recorded it. Where the key is absent the run prints the candidates under `$REPOS_PATH` and confirms the set with you, then writes it into the profile so the next run does not ask again.
- **A profile is wanted but not required.** With one, the run reads the content roots it reconciles pages over and hands the reviewer the site layout. Without one it still runs — it says so, reconciles over the whole repository instead, and reports the reviewer's layout check as not performed rather than as passed.
- **A resolved repository it can write into.** Checked at Phase 0, not at the write: the resolver hands that check to its caller, and a refusal is only worth anything while you are still being asked things. An unwritable one stops with `DOCS_AUDIT_NOT_WRITEABLE`.
- **`$SPECS_PATH`**, for two of the seven surface kinds and for its own session bookkeeping. A run with no specs tree earns its other five kinds and says which two it did not.

## Phases

| Phase | What happens |
|---|---|
| 0 — Resolve | Strip flags; resolve the repository and report the rung; run the specs-repo preflight; read the profile and the source repositories; settle what kind of run this is against any backlog already there. |
| 1 — Model routing | Classify SIGNIFICANT and record the routing block. The review model is pinned to the Opus chain regardless (unless `--enforce-model`, §10). |
| 2 — Scan | Dispatch one `code-scanner` per repository in a single response, capped at 4 concurrent, asking about all seven surface kinds; one narrow second round for a theme the first could not settle. |
| 2.5 — The specs-tree read | Enumerate the `decision` and `release` surfaces, which come from no code repository: the ARDs under the specifications tree, and the release-notes drafts grouped by version. |
| 3 — Enumerate surfaces | `docs-auditor` turns those answers into the `surfaces[]` table, with `volatility` measured from commit density at the scanned ref. |
| 4 — Type and prioritise | `ia-planner` crosses each surface with the page types it actually earns, ranks the units on four signals with a written reason, and proposes tutorial candidates. |
| 4.5 — Tutorial mint | On a refresh, a candidate you marked `picked: true` becomes a unit — once, with its id recorded on the candidate so no later run mints it again. |
| 5 — Reconcile and write | Merge against what the file already holds, match existing pages to units, compute coverage, and write `.dev-workflows/docs-backlog.yml`. |
| 5.5 — Review gate | Dispatch `docs-audit-reviewer` at Opus over the written file, triage its findings, and apply the survivors in the orchestrator. |
| 6 — Report | The coverage grid, the top twenty units with their reasons, and the consolidated report. |
| 7–9 — Emitter tail | Session maintenance and feedback, follow-ups, then cost, the resume pointer, and the terminal bookkeeping commit. |

The file is written in Phase 5 rather than Phase 6 because the reviewer reviews a file on disk: it takes the backlog's path, so the backlog has to exist before the gate can run. Nothing else about the order changes — the review still precedes the report, and the survivors it produces are applied to that same file.

## Gates

**Phase 5.5 — the review gate.** `docs-audit-reviewer` runs on Opus over four fixed dimensions, and three of them assert a relationship *between two artefacts*: every recorded evidence path against the repository at the commit it was claimed from, every unit against the surface it names, and every written reason against the surfaces enumerated in the same file. That is exactly what a reviewer reading one block at a time cannot see — each entry looks well-formed on its own. The fourth is a pair of fields inside one unit, `visibility` against `page_path`, where each value is legal and only the pairing is wrong.

Findings are triaged by the orchestrator before anything is applied: each is verified at the location it names, every dismissal is recorded with a reason that disposes of that finding's own claim and every unverified finding with what would settle it, and only survivors are acted on. There is no backlog fixer — the orchestrator applies survivors to the file itself, surfaces one whose fix is not a safe mechanical patch rather than guessing at it, and runs no re-review. A BLOCKER that is neither fixed nor explicitly overridden stops the run. Where triage leaves no finding behind a verdict other than `PASS` standing (every one dismissed or unverified), you settle the verdict at a prompt instead: proceeding continues the run, keeping a `BLOCK` verdict takes that same stop, and keeping any other verdict, or cancelling, ends the run there — the backlog stays on disk, the report names the review as cancelled, and the run's bookkeeping still finishes.

**What the run guarantees that no agent it dispatches can.** Each agent guarantees its own rules only within its own return, and only the run holds the file — so on a refresh it hands each of them what the file already contains, or their id-collision, occupied-cell and preserve-your-fields rules have nothing to check against. A surface whose churn measurement failed comes back marked unknown, which the backlog schema does not admit — the run writes `medium` for it and names every such surface in the report, because a silent `medium` is worse than an illegal value. A theme the scan could not settle is carried through as unresolved and never as a gap: a gap asserts that a page is missing, an unresolved theme asserts only that the scan could not tell. On a refresh the run applies the schema's mechanical re-ranking test — where the stored reason is exactly the one this run derived, nothing was hand-edited and both fields take the new values; where it differs, your values stand and the run reports the pair it would have written instead. And the tutorial mint of Phase 4.5 is the run's alone: the planner is forbidden to produce a tutorial unit at all.

**The run is read-only about your edits.** A unit is never deleted: one whose surface has left the scan is marked `blocked_by: [surface-removed]` and reported, one whose recorded page is no longer there is marked `[page-missing]`, and what to do about either is yours to decide. The four fields you own on a tutorial candidate, and a `priority_reason` you corrected, are never rewritten.

## Outputs

- **`.dev-workflows/docs-backlog.yml`** at the documentation repository's git top level — the surfaces, the units, the tutorial candidates, the coverage grid and the threshold. See [Documentation backlog](../reference/docs-backlog.md) for what each block holds and [Coverage model](../reference/docs-coverage-model.md) for what the words in it mean.
- **`source_repos[]` in the profile**, where the run confirmed a set the profile did not record.
- **The printed coverage grid and the top twenty units.** Read those first: everything downstream obeys this file, so a reason that is wrong here is wrong on every page written from it.
- **A session cost entry and any feedback**, filed under `$SPECS_PATH/documentation/<docs-repo-slug>/` — per documentation repository rather than in the pending queue, because an audit has no PRD and never will — unless the run carries `specs_git: misrooted` (a misplaced `$SPECS_PATH`), when the entry stays in the run's output. See [Session cost](../reference/session-cost.md).

**No branch and no commit in the documentation repository, ever.** The backlog is left in the working tree for you to read, correct and commit with the rest of your work. Where a project `.gitignore` rule would keep it out of version control, the run reports the path, the rule and the file it is in, writes the backlog anyway, and says it is not committable until that rule changes — it never force-adds past a project's own rule. The terminal bookkeeping commit is a different repository: it stages only the session-artifact paths inside `$SPECS_PATH`.

## Failure modes

- `DOCS_AUDIT_UNKNOWN_AUDIENCE` — `--audience` named something other than `user`, `engineering` or `both`.
- `DOCS_AUDIT_BAD_THRESHOLD` — `--threshold` was not a positive integer.
- `DOCS_AUDIT_UNKNOWN_FLAG` — a token beginning `--` survived flag stripping. Any such token stops the run rather than being read as a path, because the resolver takes the first positional token as given and a mistyped flag would otherwise become the repository. `--docs` and `--no-docs` are among them: this command is not a documentation-grounding consumer under any of that subsystem's three modes, so neither is one of its flags.
- `DOCS_AUDIT_NO_SOURCES` — no code repository resolved and no specs tree to read, so there is nothing to enumerate surfaces from.
- `DOCS_AUDIT_UNKNOWN_SCHEMA` — the backlog already there declares a schema version this release does not read. Nothing is written: a run that carried on would silently drop whatever the later version added.
- `DOCS_AUDIT_AUDITOR_INPUT_MISSING` / `DOCS_AUDIT_PLANNER_INPUT_MISSING` — one of the two agents refused to start because an input it enumerates was absent. The stop names it.
- `DOCS_AUDIT_UNRESOLVED_BLOCKER` — a BLOCKER finding from `docs-audit-reviewer` was neither fixed nor accepted by you, or you kept a `BLOCK` verdict after triage left no finding behind it standing. The backlog the run wrote stays on disk, reviewed and not fixed.
- `DOCS_AUDIT_NOT_WRITEABLE` — the resolved repository's git top level cannot be written to, so there is nowhere to put the backlog.

**Every one of those stops still finishes the run's bookkeeping.** A stop prints its line, reports it, and then runs the emitter tail: the cost entry and any feedback are recorded and the terminal commit into `$SPECS_PATH` still happens. The exceptions are the three flag stops — `DOCS_AUDIT_UNKNOWN_AUDIENCE`, `DOCS_AUDIT_BAD_THRESHOLD` and `DOCS_AUDIT_UNKNOWN_FLAG` — and a Cancel where the repository ladder asks you to choose or name one: each ends the run before any repository is resolved, and so has nothing to file an entry against.
- A run that enumerated no surface at all is not a failure: no plan is made, no backlog is written, an existing one is left exactly as it was, and the report says whether the product genuinely has none of these things or the scan could not tell.
- Cancelling at the overwrite prompt — the one a run without `--refresh` raises when a backlog is already there — writes nothing. The cost entry is still recorded.

## Example

```
/docs-workflows:docs-audit /workspace/docs
```

Resolves `/workspace/docs`, reads its profile, scans the two code repositories `source_repos[]` records plus the specs tree, enumerates the surfaces they hold, crosses each with the page types it earns, ranks the result, writes the backlog and prints a coverage grid with the twenty units worth writing first.

```
/docs-workflows:docs-audit --refresh --threshold 1
```

The same run against an existing backlog: surfaces and coverage re-derived against today's code, every unit and every field you own preserved, priorities updated where you had not edited the reason, a picked tutorial candidate minted into a unit, and the done threshold tightened to priority 1.

## See also

- [`/docs-init`](docs-init.md) — the cold-start command that creates the repository this one audits, and records the source-repo set it reads.
- [`/docs-profile`](docs-profile.md) — writes the profile for a documentation repository this family did not scaffold, so an audit has content roots to reconcile pages over. It writes no `source_repos[]`; on a profile from that command this run confirms the set with you and records it itself.
- [`/document`](document.md) — what turns a backlog unit into a written page today. It reads no backlog and takes no unit id: you choose the unit and run it yourself.
- [Documentation backlog](../reference/docs-backlog.md) — the file this command writes: where it lives, what each block holds, and what the coverage fraction actually counts.
- [Coverage model](../reference/docs-coverage-model.md) — the seven surface kinds, the page types a surface earns, and the four signals behind every rank.
- [Evidence and walkthroughs](../reference/docs-evidence.md) — what a page's claims are allowed to rest on, and what an unverified claim looks like on the page.
- [Session cost](../reference/session-cost.md) — what this run charges to and where the file lands.

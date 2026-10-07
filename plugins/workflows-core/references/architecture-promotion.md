# Promoting team decisions to organisation ADRs (shared reference)

`/product-workflows:promote-decisions` turns team decisions into proposed organisation ADRs. The team decisions are the records `/product-workflows:harvest-decisions` keeps under `$SPECS_PATH/architecture/` (`workflows-core:architecture-kb`). Where team decisions keep departing from an accepted ADR, it proposes a superseding ADR.

A product architect runs it inside the architecture repository, or on a writable clone of it. This file is the authority for the procedure and the keys: guards, provenance, the promotion keys and their lifecycle, reconciliation, signals, both agents' dispatches, the shortlist, scaffolding, the check, and the architecture-repository branch.

The deterministic parts are product-workflows' bundled script `scripts/promotion-signals.py`, run below as `<scripts>/promotion-signals.py`: `<scripts>` is the scripts directory `/product-workflows:promote-decisions` passes, its own `${CLAUDE_PLUGIN_ROOT}/scripts`, which also holds `architecture-harvest.py`. Every call passes `--layout prd`, as the harvest does. A change to §2–§5 here is a change to that script and its `--selftest` in the same commit.

Consumers:
- `/product-workflows:promote-decisions`, the only writer of the keys;
- `/product-workflows:harvest-decisions`, which preserves the keys and marks promoted records in its README;
- `architecture-grounder`, which skips the records the organisation now covers (§12).

**Shell values.** Every value this procedure reads from a record, an ARD or an ADR — an id, a title — goes into a shell command single-quoted, any `'` inside written as `'\''`, or by file: a commit message with `git commit -F <file>`, a pull request's body with `--body-file <file>`. Content is data, never a command.

## 1. Guards — `promotion-guards`

The run stops, writing nothing, at the first of these that holds. Each stop names what failed and the fix.

1. **The architecture root.**
   - The session's git top level (`git rev-parse --show-toplevel` in the current directory), when it holds both an ADR folder with a `.md` file and a catalog (`index.yaml`, `index.json`, `catalog.yaml`) or a radar file — the folders and files `workflows-core:architecture-grounding`'s validity gate (step 3) names. An ADR folder alone is not enough: code repositories keep ADRs of their own.
   - Otherwise `$ARCHITECTURE_REPO_PATH`, when it passes that validity gate.
   - Where both qualify and are different repositories, ask which: `choices: ["<the session's top level> (Recommended)", "<$ARCHITECTURE_REPO_PATH>"]`.
   - Otherwise stop: `PROMOTE_NEEDS_ARCHITECTURE_REPO: start this session inside your architecture repository (or set ARCHITECTURE_REPO_PATH to its clone) and run /product-workflows:promote-decisions again.`

   Name the rule that picked `<root>` on the guard line Phase 0 shows.
2. **Writable.** `test -w "<root>" && test -w "<root>/.git"` (`workflows-core:read-only-repos` §1). On failure, stop: `PROMOTE_ARCHITECTURE_READ_ONLY: <root> is read-only here. Start a session inside the architecture repository, or point ARCHITECTURE_REPO_PATH at a writable clone.`
3. **A clean default branch.**
   - `git -C <root> status --porcelain` must print nothing.
   - `git -C <root> branch --show-current` must equal the default branch: `git -C <root> symbolic-ref --short refs/remotes/origin/HEAD` without its `origin/`, else `main`.

   Otherwise stop, naming the dirty paths or the branch. The command never stashes or pulls the user's clone, and switches it only to its own branch and back (§11.1).

   Then `git -C <root> fetch --quiet origin <branch>`, best-effort and never fatal, and compare with `origin/<branch>` where it exists:
   - **Ahead** — `git -C <root> rev-list --count origin/<branch>..HEAD` above 0 → stop: `the default branch carries <N> local commits origin does not have — push or drop them first: the run's pull request would carry them.`
   - **Behind** — `git -C <root> rev-list --count HEAD..origin/<branch>` above 0 → `the architecture repository is <N> commits behind origin/<branch> — pull it before drafting, or numbers may collide`, and ask: `choices: ["Continue", "Stop — I'll pull first"]`.

   `<arch-ref>` is `origin/<branch>` where that ref exists, else `<branch>`.
4. **The specs repository.**
   - `$SPECS_PATH` unset → stop: `PROMOTE_NEEDS_SPECS_PATH: set SPECS_PATH to your specs repository.`
   - Then `specs-preflight` (`workflows-core:specs-repo-git` §3), as a keyless run. Keep its `<default-ref>`. `specs_git: misrooted` → stop with its notice, as `/product-workflows:harvest-decisions` does: the scripts read the repository's top level.
   - `git -C "$SPECS_PATH" cat-file -e <default-ref>:architecture/index.yaml` fails → stop: `PROMOTE_NEEDS_KNOWLEDGE_BASE: there are no team decision records on <default-ref> yet — run /product-workflows:harvest-decisions first.`
   - The checkout must be on `<default-ref>`'s branch, as `/product-workflows:harvest-decisions` Phase 0 step 4 requires.
   - `git -C "$SPECS_PATH" status --porcelain -- architecture/` prints anything → stop: `PROMOTE_KB_UNCOMMITTED: <paths> under architecture/ are uncommitted — an earlier run's marks, a harvest or a hand edit. Commit and hand them off, or discard them, and run again: this run reads the default branch, so it would propose those records again.`
5. **No knowledge-base change in flight.** `python3 "<scripts>/architecture-harvest.py" --specs "$SPECS_PATH" --ref "<default-ref>" --pending-kb`, exactly as `/product-workflows:harvest-decisions` Phase 0 step 5 runs it and with its stop. Any pending `kb/` branch, a harvest's or an earlier promotion's, stops the run.

## 2. The provenance lines

Written by `adr-drafter` at the top of an ADR's Context, and never edited by hand:

`Origin: team decisions <id>[, <id>…] — <specs repository name>`

`Proposes to supersede: <ADR id>`

- **The Origin line** comes first, wherever the draft names records. **Ids** are record ids (`<KEY>-AD<N>`, `architecture-kb.md` §2), comma-separated, before the ` — `.
- **Specs repository name:** the last path segment of `git -C "$SPECS_PATH" remote get-url origin` without `.git`, else the directory name. Reconciliation counts only the Origin lines that name this repository, so other teams sharing the architecture repository never show up as unknown records.
- **The supersede line** follows it in a superseding draft — or comes first, where a superseding draft's evidence is only designs' and ARDs' departures and so names no record. Such a draft carries no Origin line and no key: its pull request and its supersede line track it.
- **Placement:** the body, never the frontmatter, so no frontmatter tooling of the architecture repository is affected.
- **Lookup:** reconciliation (§4) finds a promotion by its Origin line, and a pending successor by its supersede line, never by the ADR number. A renumbered ADR is still found.

## 3. The promotion keys

Frontmatter keys on a team record. `architecture-kb.md` §6 preserves any key it does not own, after the owned ones. Only `/product-workflows:promote-decisions` writes these, through `promotion-signals.py --mark`:

| Key | Values | Meaning |
|---|---|---|
| `promotion` | `proposed` | an ADR naming the record in its Origin line is drafted and not yet decided |
| | `accepted` | that ADR is accepted — or later deprecated or superseded, which is history |
| | `rejected` | that ADR was rejected or withdrawn |
| | `declined` | the architect decided against promoting it |
| | `covered` | an existing ADR or standard already says it |
| `promoted_to` | an artifact id | with `proposed`, `accepted`, `rejected` (the drafted ADR) and `covered` (the artifact that already says it) |
| `promotion_note` | one line | required with `declined`; set to `<ADR> was rejected` (or `withdrawn`) by reconciliation; free with `covered` |

**An artifact's id** is its frontmatter `id:`, else its file stem's leading `<letters>-<digits>` (`ADR-0004`), else the whole stem: letters, digits, `.`, `_` and `-`, which is what `--mark` accepts. The scout, reconciliation and the scaffold all use this rule. In link text, the signals recognise an artifact by an upper-case id (`ADR-0004`, `STD-API-001`) or a numbered stem of three or more digits and a word (`0005-use-outbox`); a lower-case id such as `adr-0005` is not counted as friction.

A record with `promotion: proposed`, `accepted` or `covered` is never a candidate. One with `declined` or `rejected` is a candidate only under `--reconsider`.

## 4. Reconcile — `promotion-reconcile`

Run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --ref "<default-ref>" --arch "<root>" --arch-ref "<arch-ref>" --specs-name '<§2's specs repository name>' --layout prd --reconcile`. Exit 2 → stop with its stderr line.

- **`changes`:** each is a key change the run will write (§11.2). An ADR's status is read from its frontmatter, a `## Status` section or a `Status:` label; `accepted`, `approved`, `deprecated` and `superseded` count as accepted, `proposed` and `draft` as proposed, `rejected` and `withdrawn` as rejected. A live ADR wins over a rejected one, so a record re-proposed under `--reconsider` follows its new ADR.
- **`superseding`:** the proposed ADRs whose supersede line names an ADR. Add the ADRs an open pull request proposes to supersede, from the lines its body carries (§11.1 step 6): `gh pr list -R <OWNER_REPO> --state open --search '"Proposes to supersede" in:body' --json url,body` — `<OWNER_REPO>` being the architecture repository's `origin` derived as `workflows-core:phase-handoff` §2.6 derives it, an SSH alias resolved and a host other than `github.com` kept — where `gh` is available; without it, report `open pull requests not checked for superseding proposals`. Each named ADR has a successor pending, so §6 passes it to the scout and §7 never offers it again until that successor is decided.
- **`unresolved`:** each is a record marked `proposed` whose ADR is on no Origin line on `<arch-ref>`. Its pull request decides what happens. Search with `gh pr list -R <OWNER_REPO> --state all --search '<promoted_to> in:title,body' --json number,state,mergedAt,url,headRefName`. Where several come back, those whose head branch is this command's (`…promote-<date>`) decide, any other only where none is; among them, an open one decides, then a merged one, then a closed one:
  - **Closed and unmerged:** the key is cleared (`"<id>": null` in the mark plan), so the record can be proposed again.
  - **Open:** it stays `proposed`, reported as `pending — <url>`.
  - **Merged:** it stays `proposed`, reported as a problem: `<promoted_to>'s pull request merged, but no ADR on <arch-ref> names <id> in an Origin line — restore the line, and the next run records the ADR's status`.
  - **None found:** the branch was kept local, the push failed, or the pull request was never opened. It stays `proposed`, reported as `pending — no pull request found for <promoted_to>: push its branch and open one`. Under `--reconsider` the key is cleared instead, so the next run, after this run's handoff merges, proposes the record again.
  - **`gh` unavailable:** it stays `proposed`, reported as `pending — pull request not checked`.
- **`problems`:** each is reported, never acted on. `unknown-status` leaves the records an ADR names as they are; `invalid-id` is an ADR whose id is no artifact id, which names nothing; `invalid-key` is a hand-edited `promoted_to` that is no artifact id, never searched for.

## 5. Signals — `promotion-signals`

Run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --ref "<default-ref>" --layout prd --signals` (with `--reconsider` when given). Exit 2 → stop with its stderr line.

- Write the JSON to `command mktemp -t dw-promotion-signals-XXXXXX.json`, never inside a repository.
- No record with `candidate: true` and no artifact with friction → report `Nothing to promote: <n> live records, every one decided.` and go to §11.2 with only §4's marks, or stop if there are none. No architecture branch is cut.

## 6. Comparison — `dispatch-promotion-scout`

```
→ Agent (subagent_type: "workflows-core:promotion-scout", model: <review_model — §2 Opus chain; under §10, run_flags.enforced_model>):
  > "Compare these team decisions with the organisation's architecture and return the YAML:
  >
  > arch_root:           <root>
  > specs_root:          <$SPECS_PATH>
  > signals:             <the §5 JSON file>
  > candidates:          [<record id>, …]
  > pending_superseding: [<ADR id from §4's superseding list>, …]"
```

It is pinned to the §2 Opus chain for the reason `architecture-grounding.md` gives for `architecture-grounder`: a missed contradiction is the costly failure. `--enforce-model` overrides the pin.

- **`status: ERROR`, or a failed dispatch** → stop, naming its error. Nothing is drafted from a comparison that did not run.
- **`EMPTY`** → as §5's nothing-to-promote.

## 7. The shortlist

Print two numbered lists, each capped at `--max` (default 10), then the rest:

1. **Promotion candidates.** Records with `relation: new`, ranked by, in turn:
   - cluster size, in distinct groups (the record's own plus its cluster's);
   - then `cited_by` length;
   - then scope `prd`, before `epic`, before `area`;
   - then `applied_in`.

   A record with `deviated_in` or `deviated_elsewhere` entries ranks below every one without. **A cluster is one row:** a record that a higher-ranked row's cluster lists gets no row of its own, and is named in that row's reasons instead. Each row reads `<n>. <id> — <title> — <reasons>`. The reasons come from the signals in plain words, e.g. `decided in 3 PRDs (ACME-1, ACME-7, ACME-9); cited by 2 other PRDs; applied in 2 designs; deviated from once in ACME-9`.
2. **Superseding candidates.** The scout's `superseding` entries, ranked by distinct folders, then evidence count; an entry with an `allowed_by` artifact ranks below every one without. Each row reads `<n>. <ADR id> — <title> — <reasons>`, the reasons naming each `allowed_by` artifact first: the departures may need no new ADR at all.
3. **Already covered.** Records with `relation: covered`. Each row reads `<n>. <id> — covered by <artifact id> <title>`.
4. **Conflicts with no superseding candidate.** Records with `relation: conflicts` that are not in a superseding entry, listed unnumbered for information.
5. **Reported only.** Listed unnumbered; this command drafts no change to them:
   - every `signals.artifacts` entry that is not an ADR — a standard or a radar entry designs and ARDs depart from — with its folders and friction count;
   - every ADR in §4's `superseding` list, as `<ADR id> — successor <ADR id> proposed`.

Numbers run on across the lists. Then ask, in prose, because a pick list this long is not a `choices` array (`workflows-core:escalation-rules` §0):

`Reply with what to do, by number: draft <n,…>; decline <n> — <reason>; covered <n,…>, or covered <n> — <artifact id> for a promotion row. Anything you leave out is left as it is and may come back next run.`

- **`draft`** applies to any numbered row.
- **`decline`** applies to a promotion or covered row.
- **`covered`** applies to a covered row, with the scout's `artifact.id`. On a promotion row it takes the artifact the architect names, `covered <n> — <artifact id>`, which must be the id §3's rule gives a file in `<root>`.
- A superseding row carries no key, so leaving it out is how it is declined.

Restate the answer as a table: number, id, action, title, reason.
- **Overlapping picks merge.** Picks that share a record — two rows whose clusters overlap, or a promotion and a superseding row naming one record — are merged into one draft, shown once with every row it came from. A merge holding a superseding row is a superseding draft: its records are every row's, and its title is the superseding row's.
- **Title.** A draft's title is the record's title for one record, the rule a cluster shares in a few words, or `Supersede <ADR id> with <the replacement>` for a superseding pick; the architect corrects it with **Change it**. A title holds only letters, digits, spaces and `- , . ( ) /`: the template's frontmatter takes it unquoted, where `:`, ` #`, a quote or a leading `[`, `{`, `*`, `&`, `!`, `|`, `>`, `%` or `@` breaks or cuts the YAML.

Then `choices: ["Go ahead", "Change it"]`. **Change it** asks again. On **Go ahead**, before anything is written, check the marks the answer already fixes — §4's changes and clears, every decline and cover — with §11.1 step 2's `--check`: a refused decline or cover is asked again, and a refused change of §4's is reported as a problem and left out. An answer naming a number not shown, applying an action to a row it does not apply to, or declining without a reason, is asked again for that item only.

- A **cluster** pick drafts one ADR naming every undecided record of the cluster in its Origin line — one with no `promotion` key, or, under `--reconsider`, one `declined` or `rejected`. Any other member is shown in the row's reasons and never named: a record is on one live Origin line at a time, and §4 reports a second as `multiple-origins`.
- A **superseding** pick drafts one ADR proposing to supersede that ADR, naming the conflicting records, where there are any (§2).
- **Covered** marks the record `covered` with that artifact id.
- **Decline** marks it `declined` with the reason.

## 8. Scaffold — `promotion-scaffold`

Only when the answer drafts at least one ADR. Before the first write, cut the branch §11.1 step 1 names. Then, for each draft in pick order, record every path and line this section writes for it:

1. **Template:** the first that exists of `templates/ADR-template.md`, `docs/adr/template.md`, `docs/adr/adr-template.md` or `adr-template.md`, else the newest existing ADR's frontmatter keys and `##` headings.
2. **Number, file and frontmatter:** the next number past the highest in the ADR folder, zero-padded as the existing files are, with a file name that follows their pattern (`ADR-NNNN-<slug>.md` where they look like that). Fill `id`, `title` (the title §7's table confirmed), `status: proposed` and `date` (today), and any section or category key the template carries, from the values the existing ADRs use.
   - **Catalog:** where a catalog (`index.yaml`, `index.json` or `catalog.yaml`) lists decisions, append an entry shaped like the existing ones, with `status: proposed`.
3. **The overview row.** Where the ADR folder's `README.md` has a table of ADRs — under the matching section's heading where it groups them — append `| [<id>](<file>) | <title> | proposed | <date> |` to that table, matching its columns. A repository that keeps such a table usually checks that it lists every ADR.

**A stop after the branch is cut** — §10's second failure, §11.1 steps 2, 3 and 5 (a refused check, stray paths, a commit a hook refuses) — leaves the clone on `<branch>` with the run's files uncommitted. The stop names the branch and those paths, and the two ways on:
- **fix and commit them by hand** — no record is marked, so the next run offers them again until the ADRs merge with their Origin lines;
- **or discard them:** `git -C <root> reset -q -- <every path the run wrote>`, `git -C <root> restore -- <the paths it modified>`, `rm -f` each new file, check that `git -C <root> status --porcelain` prints nothing, then `git -C <root> switch <default branch>` and `git -C <root> branch -D <branch>`.

## 9. Draft — `dispatch-adr-drafter`

One dispatch per draft, in sequence:

```
→ Agent (subagent_type: "workflows-core:adr-drafter", model: <review_model — §2 Opus chain; under §10, run_flags.enforced_model>):
  > "Write the body of this ADR and return the YAML:
  >
  > adr_path:   <absolute path of the scaffolded file>
  > kind:       promotion | superseding
  > records:    [<absolute path of each record>, …]
  > sources:    [<absolute path of each record's source ARD in $SPECS_PATH>, …]
  > supersedes: { id, title, path, rule } | none
  > evidence:   [<file:line>, …] | none
  > specs_name: <§2's specs repository name>
  > signals:    [<one line per record: applied_in, cited_by, deviated_elsewhere counts>, …]"
```

A drafted ADR is checked against §2: given records, its Context opens with the Origin line, naming exactly those records and `<specs_name>`; a superseding draft carries the supersede line, naming `supersedes.id`; one given no records carries no Origin line. One that fails is re-dispatched once, then treated as an error.

`status: ERROR` or a failed dispatch → report that ADR as `not drafted — <error>` and take its scaffold back out: `rm -f` its new file, and delete from the catalog and the overview table exactly the entry and the row §8 recorded for it, by editing those lines out. Never `git checkout` those files: they hold every other draft's entries too. Its paths leave §11's list. When no draft is left, skip §10 and the rest of §11.1: restore every file the run modified (`git -C <root> restore -- <the paths it modified>`) and `rm -f` any new file still there, check that `git -C <root> status --porcelain` prints nothing, then switch back and delete the branch (`git -C <root> switch <default branch>`, then `git -C <root> branch -d <branch>`, which holds no commit of the run's).

## 10. Check — `promotion-check`

- **The repository's own decision tests.** Where `fitness-functions/` or `tests/` hold test files that read the ADR folder (they name it), run them from `<root>`:

  ```
  uv run --no-project --no-build --quiet --with pytest python -m pytest -q <those files>
  ```

  adding a `--with` for each third-party module they import. Where there are none, report `no decision tests found`.
- **On a failure,** show it, fix what the run wrote, and run again once. A second failure stops the run before §11, leaving the branch for the architect, with the failing test named.
- **Without `uv`, or offline,** report `decision tests not run — <reason>`. Never report a pass that did not run.

## 11. Hand off

### 11.1 The architecture repository — `finish-architecture-branch`

1. **Branch.** `workflows-core:branch-naming` resolves the name repo-rule-first and confirms it (§1.3). Its §3 slug for this command is `promote-<YYYY-MM-DD>`, which a convention such as `feat/adr-<slug>` turns into `feat/adr-promote-<YYYY-MM-DD>`; under a convention with no ADR marker of its own, the slug is `adr-promote-<YYYY-MM-DD>`. Its §2.4 fallback prefix is `feat/`, and a name that exists takes its §3 short-SHA suffix. Cut it with `git -C <root> switch -c <branch>` before §8 writes anything.
2. **Check the marks.** Build §11.2's mark plan now, into the file §11.2 then writes from, and run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --layout prd --mark <file> --check`. Exit 2 → stop with its stderr line, before anything is committed: a plan refused after the push would leave the drafted records unmarked, and the next run would propose them again.
3. **Stage exactly what the run wrote.** `git -C <root> add -- <each path §8 and §9 wrote>`. `git -C <root> status --porcelain` must show nothing unstaged and nothing else staged; otherwise stop, naming the stray paths.
4. **Scan.** No secret scanner ships with product-workflows; the final report says the scan did not run.
5. **Commit.** `git -C <root> commit -F <file>`, the file holding `docs(adr): propose <n> ADR(s) from team decisions` (`propose ADR-NNNN …` for one). Where the repository documents a commit convention, it governs. No `Co-Authored-By` trailer is added that the repository's convention does not ask for.
6. **Consent.** `choices: ["Push the branch and open a pull request (Recommended)", "Keep the commit local — I'll push it"]`. Then:
   - `git -C <root> push -u origin <branch>`; where git cannot write `<root>`'s `.git/config` — a container that mounts it read-only — `-u` cannot record the upstream, and the config error git prints after pushing is not a failed push: the exit status and the `-> <branch>` line decide, and nothing here reads the upstream;
   - `gh pr create -R <OWNER_REPO> --head <branch> --title '<title>' --body-file <file>`, where `gh` is available and authenticated to that host; else print the compare URL on that same resolved host, or, for a remote with no web host, the pushed branch and the body file's path.
   - The body lists each draft (id, title, kind), the records it came from with their signals, a `Proposes to supersede: <ADR id>` line for each superseding draft, and the decision-test line. Where the repository's own rules (its `AGENTS.md`, `CONTRIBUTING.md` or `CODEOWNERS`) route ADR changes to human review, the body ends by saying so.
   - Never force-push; never merge.
   - **Keep the commit local** with a superseding draft that names no record: say that the next run offers `<ADR id>` again until this branch is pushed and its pull request is open — nothing else records that proposal.
7. **Back to the default branch.** `git -C <root> switch <default branch>`, pushed or not: the commit stays on its branch, and the next run starts from the default branch §1.3 requires. The final report says to pull it once the pull request merges.

### 11.2 The specs repository

The mark plan:
- §4's changes and clears;
- one `proposed` per drafted ADR, for every record in its Origin line, whether or not its branch was pushed — §4 reports a pull request it cannot find;
- one `declined` (with the reason) and one `covered` (with its artifact id: the scout's, or the one the architect named) per answer.

It is one file, `{"marks": {…}}` in `command mktemp -t dw-promotion-marks-XXXXXX.json`, the one §11.1 step 2 checked. Where no ADR was drafted, §11.1 did not run: write and check it here first with `--check`, exactly as that step does. Then run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --layout prd --mark <file>`. Exit 2 → stop with its stderr line; nothing was written.

Then `workflows-core:phase-handoff` §4.3's push-target probe and its **gated — stopping** array — this command stops while records are uncommitted (§1.4) — and `handoff-to-main` (§2):
- `prefix: kb`, no `feature_folder` (§2.2's keyless form names `kb/promote-<YYYY-MM-DD>`);
- `deliverable_paths` = the `written` list;
- `title: NOISSUE Record promotion of team decisions`;
- `body_facts` = the counts per key value, and the architecture pull request's URL.

Declining the handoff leaves the marks uncommitted in the working tree; the next run stops at §1.4 until they are committed or discarded.

## 12. Effect on grounding

A record whose `promotion` is `accepted` or `covered` is bound by the organisation artifact in its `promoted_to`. `architecture-grounder` skips it (its Method step 4), so the decision is never cited twice.

## Invariants

- Runs only where the architecture repository is writable (§1.2), from a clean default branch that is not ahead of origin. It never stashes or pulls, and switches only to its own branch and back.
- Never edits an existing ADR, never changes an ADR's status, and never merges: a superseded ADR changes only when a human accepts its successor.
- The keys are written only by `promotion-signals.py --mark`, only into `$SPECS_PATH/architecture/decisions/`, and only on a `kb/` branch, after the plan was checked.
- One knowledge-base change at a time: a pending `kb/` branch stops both this command and `/product-workflows:harvest-decisions`, and uncommitted changes under `architecture/` stop this command.
- Never reports a check as passed that did not run.

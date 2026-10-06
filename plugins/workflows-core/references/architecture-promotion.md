# Promoting team decisions to organisation ADRs (shared reference)

`/product-workflows:promote-decisions` turns team decisions into proposed organisation ADRs. The team decisions are the records `/product-workflows:harvest-decisions` keeps under `$SPECS_PATH/architecture/` (`workflows-core:architecture-kb`). Where team decisions keep departing from an accepted ADR, it proposes a superseding ADR.

A product architect runs it inside the architecture repository, the only place that repository is writable from an AI container. This file is the authority for the procedure and the keys: guards, provenance, the promotion keys and their lifecycle, reconciliation, signals, both agents' dispatches, the shortlist, scaffolding, the check, and the architecture-repository branch.

The deterministic parts are product-workflows' bundled script `scripts/promotion-signals.py`, run below as `<scripts>/promotion-signals.py`: `<scripts>` is the scripts directory `/product-workflows:promote-decisions` passes, its own `${CLAUDE_PLUGIN_ROOT}/scripts`, which also holds `architecture-harvest.py`. Every call passes `--layout prd`, as the harvest does. A change to §2–§5 here is a change to that script and its `--selftest` in the same commit.

Consumers:
- `/product-workflows:promote-decisions`, the only writer of the keys;
- `/product-workflows:harvest-decisions`, which preserves the keys and marks promoted records in its README;
- `architecture-grounder`, which skips the records the organisation now covers (§12).

## 1. Guards — `promotion-guards`

The run stops, writing nothing, at the first of these that holds. Each stop names what failed and the fix.

1. **The architecture root.**
   - It is the session's git top level (`git rev-parse --show-toplevel` in the current directory) when that directory passes `workflows-core:architecture-grounding`'s validity gate (step 3: a catalog, a radar file, or a `.md` file in an ADR folder).
   - Otherwise it is `$ARCHITECTURE_REPO_PATH` when that passes the gate.
   - Otherwise stop: `PROMOTE_NEEDS_ARCHITECTURE_REPO: start this session inside your architecture repository (or set ARCHITECTURE_REPO_PATH to its clone) and run /product-workflows:promote-decisions again.`
2. **Writable.** `test -w "<root>" && test -w "<root>/.git"` (`workflows-core:read-only-repos` §1). On failure, stop: `PROMOTE_ARCHITECTURE_READ_ONLY: <root> is read-only here — an AI container mounts every repository except the session's own project read-only. Start a session inside the architecture repository, or run on a host.`
3. **A clean default branch.** Two checks:
   - `git -C <root> status --porcelain` must print nothing;
   - `git -C <root> branch --show-current` must equal the default branch: `git -C <root> symbolic-ref --short refs/remotes/origin/HEAD` without its `origin/`, else `main`.

   Otherwise stop, naming the dirty paths or the branch. The command never stashes, switches or pulls the user's clone.

   Report how far behind the default branch is, after `git -C <root> fetch --quiet origin <branch>`, which is best-effort and never fatal: `git -C <root> rev-list --count HEAD..origin/<branch>`. Ahead of nothing and behind N > 0 → `the architecture repository is N commits behind origin/<branch> — pull it before drafting, or numbers may collide`. The architect chooses whether to continue: `choices: ["Continue", "Stop — I'll pull first"]`.

   `<arch-ref>` is `origin/<branch>` where that ref exists, else `<branch>`.
4. **The specs repository.**
   - `$SPECS_PATH` unset → stop: `PROMOTE_NEEDS_SPECS_PATH: set SPECS_PATH to your specs repository.`
   - Then `specs-preflight` (`workflows-core:specs-repo-git` §3), as a keyless run. Keep its `<default-ref>`.
   - `git -C "$SPECS_PATH" cat-file -e <default-ref>:architecture/index.yaml` fails → stop: `PROMOTE_NEEDS_KNOWLEDGE_BASE: there are no team decision records on <default-ref> yet — run /product-workflows:harvest-decisions first.`
   - The checkout must be on `<default-ref>`'s branch, as `/product-workflows:harvest-decisions` Phase 0 step 4 requires.
5. **No knowledge-base change in flight.** `python3 "<scripts>/architecture-harvest.py" --specs "$SPECS_PATH" --ref "<default-ref>" --pending-kb`, exactly as `/product-workflows:harvest-decisions` Phase 0 step 5 runs it and with its stop. Any pending `kb/` branch, a harvest's or an earlier promotion's, stops the run.

## 2. The provenance line

The first line of an ADR's Context, written by `adr-drafter` and never edited by hand:

`Origin: team decisions <id>[, <id>…] — <specs repository name>`

- **Ids** are record ids (`<KEY>-AD<N>`, `architecture-kb.md` §2), comma-separated, before the ` — `.
- **Specs repository name:** the last path segment of `git -C "$SPECS_PATH" remote get-url origin` without `.git`, else the directory name.
- **Placement:** the body, never the frontmatter, so no frontmatter tooling of the architecture repository is affected.
- **No record, no line.** A superseding draft whose evidence is only designs' and ARDs' departures names no record, so it carries no Origin line: its pull request alone tracks it, and no key is written for it.
- **Lookup:** reconciliation (§4) finds a promotion by this line, never by the ADR number. A renumbered ADR is still found.

## 3. The promotion keys

Frontmatter keys on a team record. `architecture-kb.md` §6 preserves any key it does not own, after the owned ones. Only `/product-workflows:promote-decisions` writes these, through `promotion-signals.py --mark`:

| Key | Values | Meaning |
|---|---|---|
| `promotion` | `proposed` | an ADR naming the record in its Origin line is drafted and not yet decided |
| | `accepted` | that ADR is accepted — or later deprecated or superseded, which is history |
| | `rejected` | that ADR was rejected |
| | `declined` | the architect decided against promoting it |
| | `covered` | an existing ADR or standard already says it |
| `promoted_to` | an artifact id | with `proposed`, `accepted`, `rejected` (the drafted ADR) and `covered` (the artifact that already says it) |
| `promotion_note` | one line | required with `declined`; set to `<ADR> was rejected` by reconciliation; free with `covered` |

A record with `promotion: proposed`, `accepted` or `covered` is never a candidate. One with `declined` or `rejected` is a candidate only under `--reconsider`.

## 4. Reconcile — `promotion-reconcile`

Run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --ref "<default-ref>" --arch "<root>" --arch-ref "<arch-ref>" --layout prd --reconcile`. Exit 2 → stop with its stderr line.

- Each `changes` entry is a key change the run will write (§11.2's specs branch).
- Each `unresolved` entry is a record marked `proposed` whose ADR is on no Origin line on `<arch-ref>`. Its promotion pull request decides what happens:
  - Search with `gh pr list -R <owner/repo of origin> --state all --search "<promoted_to> in:title,body" --json number,state,mergedAt,url`.
  - **Closed and unmerged:** the key is cleared (`"<id>": null` in the mark plan), so the record can be proposed again.
  - **Open, or `gh` unavailable:** it stays `proposed` and is reported as `pending — <url or "pull request not checked">`.
- Each `problems` entry is reported, never acted on.

## 5. Signals — `promotion-signals`

Run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --ref "<default-ref>" --layout prd --signals` (with `--reconsider` when given). Exit 2 → stop with its stderr line.

- Write the JSON to `command mktemp -t dw-promotion-signals-XXXXXX.json`, never inside a repository.
- No record with `candidate: true` and no artifact with friction → report `Nothing to promote: <n> live records, every one decided.` and go to the handoff with only §4's changes, or stop if there are none.

## 6. Comparison — `dispatch-promotion-scout`

```
→ Agent (subagent_type: "workflows-core:promotion-scout", model: <review_model — §2 Opus chain; under §10, run_flags.enforced_model>):
  > "Compare these team decisions with the organisation's architecture and return the YAML:
  >
  > arch_root:  <root>
  > specs_root: <$SPECS_PATH>
  > signals:    <the §5 JSON file>
  > candidates: [<record id>, …]"
```

It is pinned to the §2 Opus chain for the reason `architecture-grounding.md` gives for `architecture-grounder`: a missed contradiction is the costly failure. `--enforce-model` overrides the pin.

- **`status: ERROR`, or a failed dispatch** → stop, naming its error. Nothing is drafted from a comparison that did not run.
- **`EMPTY`** → as §5's nothing-to-promote.

## 7. The shortlist

Print two numbered lists, each capped at `--max` (default 10), then the covered records:

1. **Promotion candidates.** Records with `relation: new`, ranked by, in turn:
   - cluster size, in distinct groups (the record's own plus its cluster's);
   - then `cited_by` length;
   - then scope `prd`, before `epic`, before `area`;
   - then `applied_in`.

   A record with `deviated_in` or `deviated_elsewhere` entries ranks below every one without. Each row reads `<n>. <id> — <title> — <reasons>`. The reasons come from the signals in plain words, e.g. `decided in 3 PRDs (ACME-1, ACME-7, ACME-9); cited by 2 other PRDs; applied in 2 designs; deviated from once in ACME-9`.
2. **Superseding candidates.** The scout's `superseding` entries, ranked by distinct folders, then evidence count; an entry with an `allowed_by` artifact ranks below every one without. Each row reads `<n>. <ADR id> — <title> — <reasons>`, the reasons naming each `allowed_by` artifact first: the departures may need no new ADR at all.
3. **Already covered.** Records with `relation: covered`. Each row reads `<n>. <id> — covered by <artifact id> <title>`.
4. **Conflicts with no superseding candidate.** Records with `relation: conflicts` that are not in a superseding entry. They are listed for information under the promotion list, unnumbered.

Numbers run on across the lists. Then ask, in prose, because a pick list this long is not a `choices` array (`workflows-core:escalation-rules` §0):

`Reply with what to do, by number: draft <n,…>; decline <n> — <reason>; covered <n,…>. Anything you leave out is left as it is and may come back next run.`

Restate the answer as a table: number, id, action, title, reason. A draft's title is the record's title for one record, the rule a cluster shares in a few words, or `Supersede <ADR id> with <the replacement>` for a superseding pick; the architect corrects it with **Change it**. A title never holds a colon: the template's frontmatter takes it unquoted, where `: ` breaks the YAML. Then `choices: ["Go ahead", "Change it"]`. **Change it** asks again. An answer naming a number not shown, or declining without a reason, is asked again for that item only.

- A **cluster** pick drafts one ADR naming every undecided record of the cluster in its Origin line. A member whose `promotion` is already `proposed`, `accepted` or `covered` is shown in the row's reasons and never named again: a record is on one Origin line at a time, and §4 reports a second as `multiple-origins`.
- A **superseding** pick drafts one ADR proposing to supersede that ADR, naming the conflicting records, where there are any (§2).
- **Covered** marks the record `covered` with the scout's `artifact.id`.
- **Decline** marks it `declined` with the reason.

## 8. Scaffold — `promotion-scaffold`

Before the first write, cut the branch §11.1 names. Then, for each draft in pick order:

1. **Template:** the first that exists of `templates/ADR-template.md`, `docs/adr/template.md`, `docs/adr/adr-template.md` or `adr-template.md`, else the newest existing ADR's frontmatter keys and `##` headings.
2. **Number, file and frontmatter:** the next number past the highest in the ADR folder, zero-padded as the existing files are, with a file name that follows their pattern (`ADR-NNNN-<slug>.md` where they look like that). Fill `id`, `title` (the title §7's table confirmed), `status: proposed` and `date` (today), and any section or category key the template carries, from the values the existing ADRs use.
   - **Catalog:** where a catalog (`index.yaml`, `index.json` or `catalog.yaml`) lists decisions, append an entry shaped like the existing ones, with `status: proposed`.
3. **The overview row.** Where the ADR folder's `README.md` has a table of ADRs — under the matching section's heading where it groups them — append `| [<id>](<file>) | <title> | proposed | <date> |` to that table, matching its columns. A repository that keeps such a table usually checks that it lists every ADR.

Every path this section writes is recorded for §11.

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

`status: ERROR` or a failed dispatch → leave that ADR's scaffold in place, report it as `not drafted — <error>`, and keep it out of §11's commit: revert its file, its index entry and its README row with `git -C <root> checkout -- <paths>` and `rm -f <new file>`. A drafted ADR given records whose Context does not open with §2's line is re-dispatched once, then treated as an error; one given none must carry no Origin line.

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

1. **Branch.** `workflows-core:branch-naming` resolves the name, repo-rule-first, with the slug `promote-<YYYY-MM-DD>`. Where the repository documents no convention, its existing branches decide; `feat/adr-<slug>` is the common shape, giving `feat/adr-promote-<YYYY-MM-DD>`. A convention with no ADR marker of its own takes the slug `adr-promote-<YYYY-MM-DD>`. Cut it with `git -C <root> switch -c <branch>` before §8 writes anything, taking the lowest free `-2`, `-3`… suffix if the name exists.
2. **Stage exactly what the run wrote.** `git -C <root> add -- <each path §8 and §9 wrote>`. `git -C <root> status --porcelain` must show nothing unstaged and nothing else staged; otherwise stop, naming the stray paths.
3. **Scan.** No secret scanner ships with product-workflows; the final report says the scan did not run.
4. **Commit.** `git -C <root> commit -m "<title>"`, `<title>` = `docs(adr): propose <n> ADR(s) from team decisions` (`propose ADR-NNNN …` for one). Where the repository documents a commit convention, it governs. No `Co-Authored-By` trailer is added that the repository's convention does not ask for.
5. **Consent.** `choices: ["Push the branch and open a pull request (Recommended)", "Keep the commit local — I'll push it"]`. Then:
   - `git -C <root> push -u origin <branch>`;
   - `gh pr create -R <owner/repo> --head <branch> --title "<title>" --body-file <tmp>`, where `gh` is available and knows the remote's host; else print the compare URL, or, for a remote with no web host, the pushed branch and the body file's path.
   - The body lists each draft (id, title, kind), the records it came from with their signals, each superseded ADR, and the decision-test line. Where the repository's own rules (its `AGENTS.md`, `CONTRIBUTING.md` or `CODEOWNERS`) route ADR changes to human review, the body ends by saying so.
   - Never force-push; never merge.

### 11.2 The specs repository

Collect the marks:
- §4's changes and clears;
- one `proposed` per drafted ADR, for every record in its Origin line;
- one `declined` (with the reason) and one `covered` (with the scout's artifact) per answer.

Write them as `{"marks": {…}}` to `command mktemp -t dw-promotion-marks-XXXXXX.json`, and run `python3 "<scripts>/promotion-signals.py" --specs "$SPECS_PATH" --layout prd --mark <file>`. Exit 2 → stop with its stderr line; nothing was written.

Then `workflows-core:phase-handoff` §4.3's push-target probe and its **advisory** array, and `handoff-to-main` (§2):
- `prefix: kb`, no `feature_folder` (§2.2's keyless form names `kb/promote-<YYYY-MM-DD>`);
- `deliverable_paths` = the `written` list;
- `title: NOISSUE Record promotion of team decisions`;
- `body_facts` = the counts per key value, and the architecture pull request's URL.

## 12. Effect on grounding

A record whose `promotion` is `accepted` or `covered` is bound by the organisation artifact in its `promoted_to`. `architecture-grounder` skips it (its Method step 4), so the decision is never cited twice.

## Invariants

- Runs only where the architecture repository is writable (§1.2), from a clean default branch it never stashes, switches or pulls.
- Never edits an existing ADR, never changes an ADR's status, and never merges: a superseded ADR changes only when a human accepts its successor.
- The keys are written only by `promotion-signals.py --mark`, only into `$SPECS_PATH/architecture/decisions/`, and only on a `kb/` branch.
- One knowledge-base change at a time: a pending `kb/` branch stops both this command and `/product-workflows:harvest-decisions`.
- Never reports a check as passed that did not run.

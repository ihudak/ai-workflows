# Components (embedded — shared reference)

Single source of truth for what a **component** is, how a repository's components are proposed, when a PRD is **multi-component**, the **ride-along** rule, and the `multi-component-prereqs` check. `/create-ard`, `/epics`, `/specify`, `/design`, `/ready` and `/implement` cite this file, as do `epic-writer`, `ard-reviewer`, and the `ard-format`, `design-format`, `workflow-states`, `ard-resolution`, `pre-lint`, `grilling-technique`, `epic-picker` and `next-phase-offer` references; none of them keeps a copy of a rule stated here. `epic-reviewer`, `design-reviewer` and `readiness-reviewer` carry no `Skill` tool and so never load it: each states, from its brief, the checks it makes against §1 and §4.

**Why it exists.** `/implement` changes code in one repository per run, so an Epic that spans two repositories is half a companion change before any code is written. A PRD that changes a client and a server, or several modules of one repository, is therefore split into one Epic per component, and the interfaces between the components are fixed in the PRD-level ARD's `## Contracts` section (`product-workflows:ard-format`) so that the Epics on either side fit together after each is implemented on its own.

## 1. Component and id

A **component** is a repository, or a set of paths inside one repository, that an Epic can target. Its **id** is:

- `<repo-slug>` for a whole repository — `client-repo`;
- `<repo-slug>:<path>` for a module inside one — `bookstore:orders`, `bookstore:k8s`, `bookstore:.github/workflows`.

`<repo-slug>` is derived the way every slug→clone map in this family derives it: `timeout 5 git -C <dir> remote get-url origin 2>/dev/null`, a trailing `.git` stripped, the URL's last path segment. `<path>` is relative to the repository's top level, POSIX-separated, with no leading `./` and no trailing `/`.

A component also has a **kind** — `code` (the default) or `deploy` — and its **paths**: the id's own `<path>`, the whole repository for a bare slug, or the list a confirmer grouped under it (§5).

### 1.1 `component-of <repo-slug> <path>`

A path inside a repository belongs to the component of that repository whose paths hold the **longest** prefix of it, compared segment by segment; a bare-slug component holds every path of its repository. A path no component of the set holds belongs to none, and is reported as such — never assigned to the nearest-looking one.

## 2. `enumerate-components <repository top level>`

Proposes the components a repository **declares**. It reads these, and nothing else:

| Source | Read | Each entry becomes |
|---|---|---|
| Gradle | `settings.gradle` / `settings.gradle.kts` `include` entries | `:a:b` → path `a/b`. Where `project(':x').projectDir` is set to a literal path, that path; where it is set any other way, the module is proposed with a note that its path is unresolved, and the confirmer supplies it |
| Maven | the top-level `pom.xml` `<modules>` | each `<module>` path |
| npm / yarn | the top-level `package.json` `workspaces` (array, or its `packages` field) | each glob, expanded against the tree |
| pnpm | `pnpm-workspace.yaml` `packages` | each glob, expanded against the tree |
| Cargo | the top-level `Cargo.toml` `[workspace] members` | each glob, expanded |
| Go | `go.work` `use` | each directory |
| Top-level build file | every top-level directory not already proposed holding `package.json`, `pom.xml`, `build.gradle`, `build.gradle.kts`, `Cargo.toml`, `go.mod` or `pyproject.toml` | that directory, `kind: code` |
| Deploy or config | the top-level directories `k8s`, `helm`, `charts`, `terraform`, `deploy`, and `.github/workflows` | that directory, `kind: deploy` |

Every build-system entry is `kind: code`. **A repository that declares no modules** — none of the build-system rows, Gradle to Go — **is itself a code component**, its id the bare slug and its paths the whole repository, proposed beside any top-level build-file or deploy directory it also holds; `component-of` (§1.1) then gives each path to the most specific of them. A repository that declares modules is an aggregator, and its root is not proposed.

**The output is a proposal, never a set.** The confirmer — the architect in `/create-ard`, the user in `/epics` Phase 5.5 — keeps, drops, adds and groups entries (§5). A directory the table does not name (a lambda folder with only scripts, a `database/` of init files) is not proposed; the confirmer adds it where a PRD touches it. That gap is the honest result of reading only what the repository declares, and a wider pattern is not the answer to it (`CLAUDE.md` § Editing discipline, *resolve an identifier against a known set*).

Worked examples: `bookstore` (a Gradle multi-project) proposes fourteen — its eleven `include`d modules, `web` (code, through `web/package.json`), and `k8s` and `.github/workflows` (deploy); a client repository with a root `package.json` and `.github/workflows/` proposes two — `client-repo` (code, the whole repository) and `client-repo:.github/workflows` (deploy).

## 3. `multi-component-test <PRD folder>`

Returns `{multi_component, set, set_source}`. The **known set** comes from the first of these that exists:

1. **`ard`** — the PRD-level ARD's `components:` (`product-workflows:ard-format`), read through `workflows-core:ard-resolution`'s `components` field. An ARD with no `components:` key (every ARD written before this reference existed) supplies nothing, and the next source is tried.
2. **`epics-run`** — inside one `/epics` run with no ARD set, the set its Phase 5.5 confirmed.
3. **`epic-targets`** — the distinct `target:` values of the `epic.md` in each `EPIC-` folder directly under the PRD folder.

`multi_component` is true when the set has **two or more `kind: code` components**. A deploy component counts for nothing here: a module that only rides along on it (§4), or deploys through it in another repository, needs no contract with it, so `orders` plus `k8s` is one code component and the PRD is not multi-component — though its Epics still take one target each. Under `epic-targets`, which carries no kind, an id whose path is one of §2's deploy directories counts as `kind: deploy`. With no source, the set is empty and the PRD is not multi-component.

The third source is what keeps a PRD that `/epics` split without an ARD — its prerequisites stop's override (§6) — multi-component for `/design`, `/ready` and `/implement`, which have no ARD set to read. **A target is checked as being *in* the set where the source is `ard` or `epics-run`** — a set somebody confirmed; under `epic-targets` the set *is* the targets, so there is nothing to check. Outside an `/epics` run only `ard` and `epic-targets` occur.

## 4. Ride-along

An Epic may change files of a `kind: deploy` component **in the same repository as its target**, where those files exist only to deploy or configure the target — its Deployment manifest, its environment variable, its pipeline job — without that component counting as a second target. It declares each one under `### In scope`:

    - Also touches: <component id> — <why>

Two limits, both enforced by `epic-reviewer` and `design-reviewer`:

- **Same repository only.** A deploy component in another repository (a separate gitops repository) is never ridden along: `/implement` cannot change it in the same run, so it is its own Epic.
- **`kind: deploy` only.** A `kind: code` component is never ridden along; a change there is a second target, and the Epic splits.

A deploy component is still a target in its own right — for an infrastructure-only PRD, or where a change there is the work rather than support for it.

## 5. The ARD `components:` entry

The PRD-level ARD's `components:` frontmatter (`product-workflows:ard-format`) lists the components **this PRD touches** — not every module the repository has:

```yaml
components:
  - id: bookstore:orders
  - id: bookstore:common
    paths: [common, exceptions]
  - id: bookstore:k8s
    kind: deploy
```

`kind` defaults to `code`; `paths` defaults to the id's own path, or the whole repository for a bare slug. **`paths` is how a confirmer groups**: two modules that always change together become one component, so they are never forced into two Epics. Grouping is recorded nowhere else, so it is `/create-ard`'s to make: an `/epics` run without an ARD keeps, drops and adds components but does not group them. A grouped component's id names one of its paths. Every entry's repository is in the ARD's `grounded_repos`, or is named under its `## Open questions`.

## 6. `multi-component-prereqs`

Inputs: the resolved PRD folder and its key, the Epic key (or null), and `scope` — `epics`, `implement` or `ready`. **It writes nothing, dispatches no agent, asks nothing and never stops**; each caller decides what a returned row means.

1. Run §3. Where `multi_component` is false, return `{multi_component: false}` and nothing else — the caller proceeds exactly as it did before this reference existed.
2. **Prerequisites** (`epics` and `implement` scope; at `ready` scope the Ready rung of `dev-workflows:workflow-states` already lists them). Each row is `present` (on `<default-ref>`), `not_on_default` (not there, but in the `$SPECS_PATH` worktree or on a plugin branch) or `missing`, tested with `workflows-core:phase-handoff` §3.2's read-only primitives — the ref-existence test, `git -C "$SPECS_PATH" cat-file -e "<default-ref>:./<path>" 2>/dev/null`, and the plugin-branch scan — and never with `require-on-main`, whose repair offer is a prompt. Where `<default-ref>` itself does not exist, every row is `unverified` with that reason.
   - `ard_contract` — the PRD folder's `ard.md`, **and** `ard-resolution`'s `contracts` not null. An ARD present without a `## Contracts` section is `missing`.
   - `prd_spec` — the PRD folder's flat `specification.md`.
   - `epic_target` (`implement` scope) — read from the Epic's `epic.md`, not tested on a ref: `present` where it carries a `target:` (in the set, where §3's source is `ard`), `missing` where it carries none, `outside_set` where the ARD's set does not hold it.
   - `epic_spec`, `epic_design` (`implement` scope) — the Epic folder's `specification.md` and `design.md`.
3. **Target** (`implement` scope): the Epic's `target:`, or `none`; `in_set` where `set_source` is `ard`; and `target_repo_matches` — the target's `<repo-slug>` against the slug of the repository the run stands in (§1's derivation, from its top level): `true`, `false`, `unknown` where that repository has no `origin`, or `null` where the Epic has no target (the `epic_target` row reports that).
4. **Targets** (`ready` scope): one row per `epic.md` in an `EPIC-` folder directly under the PRD folder — its key, its `target:` or `none`, and `in_set` where `set_source` is `ard`.
5. **Contract coverage** (`implement` and `ready` scope), where `ard-resolution`'s `contracts` is not null. Read the `epic.md` in every `EPIC-` folder directly under the PRD folder for its `target:`, its `## Contract` lines (`- Produces: [AD#N] — …`, `- Consumes: [AD#N] — …`; every `[AD#N]` on such a line counts) and its `## Dependencies`. Then report each gap by `AD#N`:
   - `unknown_ad` — an Epic cites an `[AD#N]` that is not an interface row;
   - `consumed_unproduced` — an Epic consumes a row whose status is `new` or `changed`, and no Epic whose target is the row's producer produces it;
   - `produced_off_target` — an Epic produces a row whose producer is not its target;
   - `consumer_not_dependent` — a consumer's `## Dependencies` does not name, by key, the Epic that produces what it consumes;
   - `unproduced_row` (`ready` scope only) — a `new` or `changed` row no Epic produces.

   At `implement` scope only gaps naming this Epic — as consumer or producer — are returned. A row with status `exists` is satisfied by the code, so consuming it is never a gap.

Return shape:

```yaml
multi_component: true | false
set_source: ard | epics-run | epic-targets
prerequisites:            # epics and implement scope
  - {name: ard_contract | prd_spec | epic_target | epic_spec | epic_design, state: present | not_on_default | missing | outside_set | unverified, path: <path>, reason: <text or null>}
target: {id: <id or none>, in_set: true | false | null, target_repo_matches: true | false | unknown | null}   # implement scope
targets: [{epic: <key>, id: <id or none>, in_set: true | false | null}]                                 # ready scope
coverage_gaps: [{kind: unknown_ad | consumed_unproduced | produced_off_target | consumer_not_dependent | unproduced_row, ad: AD#N, epic: <key or null>, detail: <text>}]
```

**The earliest gap's remedy**, which `/epics` and `/implement` recommend, is the remedy for the first row that is not `present`, in ladder order — `ard_contract`, `prd_spec`, `epic_target`, `epic_spec`, `epic_design`:

- a `missing` row → the command that authors it: `ard_contract` → `/product-workflows:create-ard <PRD>`, `prd_spec` → `/product-workflows:specify <PRD>`, `epic_spec` → `/product-workflows:specify <EPIC>`, `epic_design` → `/dev-workflows:design <EPIC>`;
- `epic_target` `missing` or `outside_set` → `/product-workflows:epics <EPIC>`, whose refine mode re-drafts the Epic with a target from the set;
- a `not_on_default` row → landing that artifact on the default branch — merging the branch or pull request that carries it;
- an `unverified` row → settling `$SPECS_PATH`'s default branch, which the row's reason names;
- with every row `present`, a coverage gap → `/product-workflows:epics <PRD>`.

## Consumers (informative)

- `/create-ard` — Phase 3 proposes theme→component with §2 and writes the confirmed list to `components:` (§5); Phase 4 authors `## Contracts` when two or more are `kind: code`.
- `/epics` — §3 for the known set; Phase 5.5 with §2 and §1.1 where no ARD supplies one; §6 at `epics` scope for its prerequisites stop; §4 in `epic-writer`'s rules.
- `/specify`, `/design` — the Epic's target narrows the repositories and the scan; §3 decides whether `/design <PRD>` designs a flat spec.
- `/ready` — §6 at `ready` scope for its targets and contract-coverage tables.
- `/implement` — §3 in its picker; §6 at `implement` scope at the start of Phase 1.
- `epic-writer` — §1, §4 and §5; `ard-reviewer` — §5. `epic-reviewer`, `design-reviewer` and `readiness-reviewer` apply §1 and §4 from their briefs without loading this file.

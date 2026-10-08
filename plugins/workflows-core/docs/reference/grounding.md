# Grounding sources

The family's authoring commands read more than the folder they were given: the shipped product docs, the organisation's architecture repository, the team's own harvested decisions, the mounted code, and — for `/prd-ground` — exported design frames. This page lists every one of those sources in one place: what it feeds, which commands read it, what turns it on, the line a run prints about it, and how to turn it off. Every source is **read-only** and **advisory** — a miss turns that source off with a reason and never stops the run — except where a command's own page says a repository is required. The shared references under `references/` are the authority; each command's page says how it uses what it reads.

## At a glance

| Source | Read by | Turned on by | Off switch |
|---|---|---|---|
| [Shipped product docs](#shipped-product-docs) | `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/brd-intake`, `/epics`, `/prd-ground`, `/release-notes` | `$DOCS_PATH` (default `/workspace/docs`) holding markdown; `--docs <path>` for one run | `--no-docs` |
| [Architecture repository](#architecture-repository) | `/create-ard`, `/specify`, `/dev-workflows:design` | `$ARCHITECTURE_REPO_PATH` naming a valid architecture repository | `--no-arch` |
| [Team decision records](#team-decision-records) | `/create-ard`, `/specify`, `/dev-workflows:design` | `$SPECS_PATH/architecture/`, built by `/harvest-decisions` | `--no-arch` |
| [Mounted code](#mounted-code) | `/idea`, `/epics`, `/create-ard`, `/specify`, `/prd-ground`, `/dev-workflows:design`; diffs in `/document`, `/release-notes` | clones under `$REPOS_PATH` (default `/workspace`) | per command — see below |
| [Design frames](#design-frames) | `/prd-ground` | a frame set under the folder's `design/`, indexed by `/frames` | `--no-design` |

The status lines are printed in the command's configure or plan step; the off switch is stated beside them. There is no prior-art search in this family: what you hand `/idea` is the only prior art it reads.

## Shipped product docs

- **Feeds:** what the product already does and how the published docs say it — challenges such as "already documented", a terminology mismatch or a contradiction. The grill ranks them in `/idea`, `/create-prd`, `/update-prd`, `/create-ard`, `/specify` and `/brd-intake`; the writer gets them as background in `/epics` and `/release-notes`; `/prd-ground` reads them as the lead's context. Agent: `docs-grounder`.
- **Turned on by:** `$DOCS_PATH`, default `/workspace/docs`, when it is a readable directory with at least one markdown file; `--docs <path>` points a run at another root. Retrieval uses a `qmd` index where one covers the root, else keyword search.
- **Status line:** `docs grounding: ON <root> (retrieval: …)` or `docs grounding: OFF (<reason>)`.
- **Off switch:** `--no-docs`.
- **Not used by** `/document`, which treats `$DOCS_PATH` only as a hint for which docs repository to write, nor by `/brd-split`. Reference: `references/docs-grounding.md`.

## Architecture repository

- **Feeds:** the organisation's technology radar, standards, principles, patterns and accepted ADRs. `architecture-grounder` returns what binds the work and what it contradicts — a decision or standard it breaks, a hold or retire ring, a technology the radar does not list.
- **Turned on by:** `$ARCHITECTURE_REPO_PATH` alone — nothing scans for a clone. The root must hold a catalog, a radar file or an ADR folder; a set but invalid value turns grounding off with a reason naming it. The clone is never fetched, pulled or switched.
- **Status line:** `architecture grounding: ON <root> (<branch> @ <sha>, <date>)` — with `; uncommitted changes`, `; HEAD on no remote branch — links omitted` or `; last commit <N> days old — refresh the clone` where they apply — or `architecture grounding: OFF (<reason>)`.
- **Off switch:** `--no-arch`. Reference: `references/architecture-grounding.md`.

## Team decision records

- **Feeds:** the team's own architecture decisions — one record per `[AD#N]` of every merged ARD, under `$SPECS_PATH/architecture/` — to the same `architecture-grounder` as a second, team root. A run does not re-read the decisions it already inherits from its own ARD, and skips a record whose decision has been promoted to an accepted organisation ADR or marked as covered by one; it cites that ADR instead. The `product-workflows` Workflow overview page draws how `/harvest-decisions` builds the records and `/promote-decisions` promotes them.
- **Turned on by:** `$SPECS_PATH/architecture/` holding `index.yaml` or a record under `decisions/`. It is resolved independently of `$ARCHITECTURE_REPO_PATH`, so it is read where no architecture repository is set.
- **Status line:** `team decisions: ON <specs>/architecture (<N> live records)` — `; differs from <default-ref>` when your working copy of the records is not the default branch's — or `team decisions: OFF (<reason>)`.
- **Off switch:** `--no-arch`, which turns off both architecture roots. References: `references/architecture-grounding.md`, `references/architecture-kb.md`.

## Mounted code

- **Feeds:** what the code already does — through `code-scanner`, one instance per repository, and in `/prd-ground` through `code-grounder`, which writes verified `[CG#n]` findings; and, for `/document` and `/release-notes`, what the implementation changed, through `diff-summarizer`.
- **Turned on by:** clones under `$REPOS_PATH` (default `/workspace`, colon-separated for several), and per command:
  - `/idea` — only with `--ground-code [<repo>,…]`.
  - `/epics` — on by default; the configure step asks whether to examine code.
  - `/create-ard` — always: it proposes the repositories for the work's themes and you confirm the set.
  - `/specify` — a light scan of the target or candidate repositories; an unmounted one becomes an open question.
  - `/prd-ground` — always, unless `--no-code` reuses the verified code grounding already on file.
  - `/dev-workflows:design` — every implementation repository the design spans must be mounted.
  - `/document` (keyed mode) — the repositories the implementation record and the commit scan name, always.
  - `/release-notes` — only when you turn diff grounding on in Phase 1 (default off).
- **Status line:** none of its own — the run shows the repository set it resolved or proposes.
- **Off switch:** omit `--ground-code` (`/idea`), answer no at the code question (`/epics`), leave diff grounding off (`/release-notes`). The other commands have none: a repository can only be descoped, and the run records what it could not ground. `/prd-ground --no-code` is a run mode that adds design grounding over code grounding already on file, not a way to skip code. Reference: [Environment](environment.md#repos_path).

## Design frames

- **Feeds:** what an exported design shows — `design-grounder` reads each frame set and writes `[DG#n]` findings beside `/prd-ground`'s code findings.
- **Turned on by:** a frame set under the resolved folder's `design/` subdirectory, one subdirectory per set, carrying the index `/frames` builds; no `design/` folder means the pass is skipped and the run says so.
- **Off switch:** `--no-design`. Reference: `references/grounding-format.md`.

# Architecture Requirements/Decision Document (ARD) format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical structure and rules for an ARD authored by `/create-ard`. `ard-reviewer` reviews against
this file, and `/ready` reads its `grounded_repos:` frontmatter. The ARD is **architecture** — invariants, grounded as-is findings, and cross-cutting
decisions — NOT product requirements (that is the PRD) and NOT a per-Epic implementation plan (that is
`/design`). One shape; **depth scales with altitude**: a PRD-level ARD stays at invariants + frame; an
Epic-level ARD goes deeper on that Epic's repos/areas.

## Altitude & scope

- **PRD-level** (`/create-ard <PRD-KEY>`) — cross-cutting invariants + broad-but-shallow grounding across the affected repos.
- **Epic-level** (`/create-ard <EPIC-KEY>` — one address; the Epic's key encodes its ancestry, so the PRD is the folder above it and is never typed beside it, D4) — deeper grounding on the Epic's repos/areas; **inherits the PRD-level ARD's `AD#N` read-only** and must not contradict them.
- **Per-area** — a big Epic spanning separable areas in one repo (e.g. backend `server/` + frontend `ui/`) may split into `ard-<area>.md` beside the folder's `ard.md` (grill-decided).
- **Multi-component** — a PRD-level ARD whose `components:` lists two or more `kind: code` components (`workflows-core:components` §3) also carries `## Contracts`: the interfaces between those components, fixed here so that the one-component Epics on either side fit together once each is implemented on its own.

## Frontmatter

```yaml
---
kind: ard                    # what this document is
key: <KEY>                   # this folder's key — must match the folder name
title: <PRD or Epic title> — ARD
scope: prd | epic
prd: <PRD-KEY — or, on the BRD route, the slice's parent BRD key (the route resolves a PRD- slice folder and refuses a BRD- container)>
epic: <EPIC-KEY | null — on the BRD route, always the slice's own key>
area: <name | null>
status: draft | reviewed
grounded_repos:
  - <repo-slug @ absolute path>
components:                  # PRD level only — the components this PRD touches (workflows-core:components §5)
  - id: <repo-slug> | <repo-slug>:<path>
    kind: code | deploy      # optional; default code
    paths: [<path>, ...]     # optional; default the id's own path, or the whole repository for a bare slug
inherits: <path to the PRD folder's ard.md | null — on the BRD route, the parent BRD folder's ard.md>
derived_from: <path to the PRD file, canonical prd.md — or, in a BRD folder that holds no PRD, that folder's ard-seed.md>
---
```

**`components:` is the known set every Epic target is resolved against.** The architect confirms it in `/create-ard` Phase 3, and it lists the components this PRD touches, never every module a repository has. Every entry's repository is in `grounded_repos` or is named under `## Open questions`. It is written by a PRD-level run only — on the BRD route, a slice's own `/create-ard <SLICE>`, whose ARD carries `scope: epic` (below) yet is its slice's PRD-level ARD — and an Epic's ARD carries none; the PRD-level ARD's set applies to its Epics. An ARD with no `components:` key — every ARD written before the key existed — supplies no set, and §3 then takes the set from an `/epics` run's confirmation or from the targets the PRD's Epics carry, where either exists (`workflows-core:components` §3).

**Unknown frontmatter keys are preserved.** Every command that rewrites this file keeps fields it does not recognise, in place and unmodified — the same rule `workflows-core:prd-format` states for a PRD, and for the same reason: a user's own field must survive a run that did not author it. `workitem_key` is the documented example, and it is reserved rather than special-cased.

**`prd`, `epic` and `derived_from` are widened for the BRD route, and the widening is confined to
them.** Under `/create-ard` on the BRD route the run holds a **BRD key**, which addresses a folder under
`$SPECS_PATH` and may carry a third numeric segment (`workflows-core:addressing` §1 fixes no
depth), so `prd` and `epic` are validated against that grammar — `^[A-Z][A-Z0-9_]*(-\d+)+$` — rather
than any narrower form; `ard-reviewer` applies exactly this and `commands/create-ard.md` writes
exactly this, from one resolution rather than two. `scope` follows the same pairing it always did: a
source-owning BRD is `prd`, a slice is `epic`, because a slice sits where an Epic sits — one level
down, inheriting its parent's `AD#N` read-only. `derived_from` names the PRD file when the folder
holds one (the ordinary case, since this route is normally reached from
`/create-prd` on the BRD route's own next-step offer) and the folder's `ard-seed.md` when it does not: the
field records provenance, and naming a PRD path in a folder that holds no PRD would name a file that
does not exist. No widening here reaches a **tracker** key — none of these fields is one.

## Sections

- `## Context` — the problem/goal frame from the PRD (Epic-level adds the Epic's scope).
- `## Grounding findings (architecture as-is)` — what exists today, each claim citing a real `file:line` in a `grounded_repos` entry. An unmounted/descoped repo appears only under Open questions — NEVER as an invented "as-is" claim.
- `## Architecture decisions` — `### [AD#N]: <title>`, each with **Binds:** (what it constrains) · **Prevents:** (the divergence it stops) · **Rule:** (a single testable statement) · **Alternatives:** (each other option weighed, one line each, with the reason it lost). A decision a later one replaced also carries **Superseded by:** `[AD#M] — <why>`, and one made moot with no replacement **Withdrawn:** `<why>` (§ Superseding a decision). Epic-level lists inherited PRD-level ADs read-only under "Inherited invariants" — the live ones only.
- `## Cross-repo / component approach` — the Capability→Architecture map (which capability lands in which repo/component). On a multi-component ARD each capability names the component ids it lands in, and one that lands in two or more `kind: code` components is a capability `## Contracts` must give an interface row; a deploy component a capability only rides along on (`workflows-core:components` §4), or deploys through in another repository, adds none.
- `## Contracts` — **PRD level, and only when `components:` has two or more `kind: code` entries.** An interface table, then three subsections:

  | AD | Producer | Consumers | Kind | Status | Artifact |
  |---|---|---|---|---|---|
  | [AD#3] | bookstore:orders | bookstore:carts, bookstore:web | REST | new | — |

  `AD` is the `[AD#N]` whose Rule states the interface; `Producer` is one component id and `Consumers` one or more, all from `components:`; `Kind` is `REST`, `message`, `shared schema`, `shared library` or `generated client`; `Status` is `new`, `changed`, or `exists` (already in the code, cited under Grounding findings); `Artifact` is the path in the producer where the contract is a code file — an OpenAPI or `.proto` file, an entity module, a generated client — else `—`. Then `### Schema ownership` (which component owns each shared shape), `### Versioning and compatibility` (how each interface changes without breaking the other side), and `### Landing order` (an ordered list of component ids; a producer of a `new` or `changed` row whose `Artifact` is a code file comes before every one of its consumers). **With no interface row** — two code components neither of which calls the other, such as two services that only share a deploy directory — the table is empty and `### Schema ownership` and `### Versioning and compatibility` read `_N/A — no interface_`; `### Landing order` is still written. **The table is the one place producer, consumers and status are written**; each row's `AD#N` stays under `## Architecture decisions` with its Binds, Prevents and Rule, so the `AD#N` series stays single. An Epic-level ARD inherits these rows read-only, as it inherits PRD-level `AD#N`.
- `## Stack & invariants` — pinned versions / conventions that must hold.
- `## Edge cases & risks`.
- `## Open questions` — incl. ungrounded/descoped repos.
- `## Deferred` — PRD-level → per-Epic `/create-ard` / `/design`; Epic-level → `/design` / `/implement`.

## Quality rules

- Every "as-is" claim cites a grounded `file:line`; no fabricated/uncited architecture.
- `AD#N` are **testable** and non-overlapping (Binds/Prevents/Rule each populated, and Alternatives on every live decision).
- An `AD#N` earns its place only when the decision is **hard to reverse** AND **surprising without context** AND the result of a **real trade-off**; a decision missing any of the three is an ordinary implementation choice (leave it to `/design`), not an architecture decision. **One stated case meets the bar by what it is:** an interface row's `AD#N` — an interface that crosses two components, which both sides ship against and so cannot reverse alone. **Alternatives** is the record of that trade-off: a decision that beat no other option was not one — save an interface row's `AD#N`, whose Alternatives names the other interface shapes weighed or reads `none weighed`. An ARD written before the field existed still resolves as before; its decisions gain the field when a refine touches the ARD.
- On a multi-component ARD, every capability the Capability→Architecture map lands in two or more `kind: code` components has an interface row, and every row's components are in `components:`.
- **PRD-level carries NO per-repo detailed solutions** — that is `/design`'s job.
- An Epic-level ARD may go deeper but stays architecture, not an implementation plan.
- Grounding is **architect-driven** (repos confirmed by the architect), never derived from PRs (which do not exist at ARD time).

## Architecture governance

Where `/create-ard` ran with architecture grounding ON (`workflows-core:architecture-grounding`), the ARD records what the architecture repository says about its decisions:

- **Citation.** A governance artifact is cited only as a markdown link whose text is its id and title — `[ADR-0012 Use one message broker](<url>)` — in the **Rule** of the decision it settles or constrains, or in **Alternatives** where it is why an option lost. Every governance id of that shape matches a tracker's issue-key pattern, and the link is what keeps it from auto-linking (`workflows-core:pre-lint` § Auto-link collision); a bare id, or one in inline code, is a pre-lint finding. Where the digest gives no URL, the link target is the artifact's path relative to the architecture repository.
- **Baseline.** `## Stack & invariants` opens with `Architecture governance: <repository name> @ <short-sha> (<date>)` — or `Architecture governance: <repository name> (not a git checkout)` — and lists, as links, the standards that bind the work. A relative link target resolves against the repository named there.
- **Deviation.** Each of these is an `## Open questions` entry naming the governing artifact as a link, how the ARD departs from it, and that the departure needs an architecture review or a new ADR in the architecture repository superseding it: a decision that departs from an `accepted` ADR or an `active` standard; keeping or adopting a technology in the radar's `hold` or `retire` ring; adopting a technology the radar does not list. An entry about a technology the code already uses cites where it does — a `file:line` in a `grounded_repos` entry, as every as-is claim must.
- **Not an as-is claim.** A governance citation states what the organisation requires, not what the code does, so it needs no `grounded_repos` entry; `## Grounding findings` keeps its rule that every claim there cites a `file:line` in one.

Where grounding was OFF, nothing in this section is required.

## Superseding a decision

- **A refine never changes what an existing `[AD#N]` requires** — nor does starting fresh over an ARD already on the specs repo's default branch, the only place downstream commands read one from. `design.md`, deviation records (`ard-resolution.md`), Epic drafts and readiness verdicts cite a decision by its ID, and a Rule rewritten in place silently changes what each of those citations means. A changed decision is a new `[AD#M]`; the old one keeps its heading, ID and text and gains `**Superseded by:** [AD#M] — <why>`. Wording that leaves the Rule's meaning unchanged is not a change.
- **A decision made moot with no replacement** — a scope cut, a dropped requirement — keeps its place the same way and gains `**Withdrawn:** <why>` instead.
- **A superseded or withdrawn decision binds nothing.** `ard-resolution.md` leaves it out of `invariants`, so no consumer enforces it, and an Epic-level ARD neither lists it under "Inherited invariants" nor is held to it. A reader of the ARD's own text treats it the same way. An Epic-level ARD's "Inherited invariants" list is a snapshot: a PRD-level decision superseded after it was written binds nothing from then on, because `ard-resolution.md` reads the PRD-level ARD itself, and the next refine of the Epic-level ARD drops it from the list.
- **`Superseded by` names a live `[AD#M]` in the same ARD.** An Epic-level ARD never supersedes or withdraws a PRD-level decision — a change there is a refine of the PRD-level ARD.
- IDs stay contiguous over live, superseded and withdrawn decisions alike; none is ever deleted or renumbered.
- **An interface row in `## Contracts` names a live `AD#N`.** When its decision is superseded, the row's `AD` cell moves to the replacement; when it is withdrawn, the row goes with it.

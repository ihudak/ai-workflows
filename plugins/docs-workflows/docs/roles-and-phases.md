# Roles and phases

[Workflow overview](workflow.md) shows where each command sits. This page says which role each of this plugin's commands runs in, what that role produces and hands over, and, at the end, what each cost-attribution phase means when you see it on a cost report or in a run's output.

**A command's role is fixed by the command, with one exception.** [`/document`](commands/document.md), in both its modes, [`/docs-init`](commands/docs-init.md), [`/docs-audit`](commands/docs-audit.md), [`/docs-write`](commands/docs-write.md), [`/docs-verify`](commands/docs-verify.md) and [`/docs-brand`](commands/docs-brand.md) always run in the `dev` role — a `/docs-brand` that `/docs-init` runs `--inline` is charged with that `/docs-init` run. [`/release-notes`](commands/release-notes.md) is the exception: it runs at two points in a PRD's life, and works out which one from the PRD folder ([below](#prd-creation)). [`/docs-profile`](commands/docs-profile.md) and [`/docs-serve`](commands/docs-serve.md) run in no role at all ([below](#outside-the-roles-docs-profile-and-docs-serve)).

## Dev — document what shipped, and keep the portal

- **Owns:** the product documentation of a shipped feature, and the documentation repository it is published from — its scaffold, its brand, the backlog of what it is still missing, and the pages drafted from that backlog and verified.
- **Runs:**
  - `/document <KEY>` (keyed mode) once a PRD's or an Epic's work has shipped, and `/document` with an `@file` or a description (direct mode) for a one-off edit;
  - `/release-notes <PRD>` again once a `specification.md` or a `design.md` exists — the late run;
  - `/docs-init`, for a product with no documentation repository, which also runs `/docs-brand --inline` unless you pass `--no-brand`; `/docs-brand` on its own, to apply a logo and colours from the product's code; `/docs-audit`, to find what the portal is missing; `/docs-write`, to draft the page for each unit of that backlog; and `/docs-verify`, to walk a drafted user page or read an engineering page's claims in the code, and move its unit to `verified`.
- **Consumes:** keyed `/document` reads the PRD folder — the PRD, a specification where one exists, and `implementation.md` — and the diffs of the refs it names and of the commits its scan for the unit's keys finds, from clones under `$REPOS_PATH`; `/docs-audit` reads the code repositories the profile records, or a set you confirm where it records none, the specs tree, the documentation repository's own pages, and its existing backlog; `/docs-brand` reads one code repository; `/docs-write` reads the profile, and the whole backlog to select its units, then, for each unit it drafts in turn, the code repositories its evidence names, at their default branch, any architecture decision record it rests on, at the specs repository's default branch, and any walkthrough the unit names; `/docs-verify` reads the profile and the backlog, then, for the one unit it takes, its page and — for a user page — its walkthrough, where it has one, and each image file you name, or — for an engineering page — the code repositories the page's `evidence:` names, at their default branch, and any architecture decision record it names, at the specs repository's default branch.
- **Produces:**
  - pages in the documentation repository. Keyed `/document` squashes its work on the branch it cut, where the plan you approved cuts one, offers to push that branch, and writes a pull-request draft for you to open; direct mode leaves its edits uncommitted on the branch you are on, and creates no branch and no commit;
  - from `/docs-init` and a standalone `/docs-brand`, a branch with a commit and a drafted pull request, never pushed;
  - from `/docs-audit`, the backlog, `.dev-workflows/docs-backlog.yml`, left in the working tree for you to review and commit, with the profile where the run recorded `source_repos[]` in it;
  - from `/docs-write`, one commit per unit on a branch — the page, its navigation and the unit's move to `drafted` — with one push offer and a pull-request draft printed in its report, never opened;
  - from `/docs-verify`, one commit on a branch — the page with your answers or the readings you took applied, a user page's walkthrough and images with it, and the unit's move to `verified` — or, where a claim does not resolve, one commit of the backlog's record of why, and, where a walk does not finish, one commit of the walkthrough with your answers; with one push offer and a pull-request draft printed in its report, never opened;
  - from the late `/release-notes`, a draft appended to `release-notes.md` in the PRD folder.
- **Hands over:** each documentation-repository branch to that repository's own review, through the pull request you push and open; each page `/docs-write` drafted to `/docs-verify`, which walks it with you or reads it, and a page it cannot verify, such as an explanation page, to you, to verify by hand; each verified page to you, to publish; the release-notes draft to the specs repository's default branch by a pull request, offered behind a consent question, and from there to whoever publishes release notes; and the backlog to you, to read, correct and commit — with the profile, where the run recorded `source_repos[]` in it, since `/docs-write` and `/docs-verify` start only once both are committed. A later `/docs-audit --refresh` reads the backlog back: it re-derives what the file says about the code — the sources, the surfaces and every coverage figure — and keeps every unit, one you added by hand included, with its title, roles, page path and walkthrough, your `threshold`, your tutorial picks, and a unit's `priority` where you also edited its `priority_reason`; a unit's `status` and `blocked_by` change only where the run finds a page for a unit still `missing`, or a surface or page that has gone ([The documentation backlog](reference/docs-backlog.md)). [`/docs-serve`](commands/docs-serve.md) checks only whether the file exists, to choose the next step it offers.
- **Cost phases:** `documenting`, `docs-scaffold` and `docs-audit`, all role `dev`.

The companion `dev-workflows` plugin's own Roles and phases page describes the rest of the Dev role — design, implementation, readiness and conformance.

## PM — the early release note

- **Runs:** `/release-notes <PRD>` on a PRD with no `specification.md` and no `design.md` under its folder yet. Epics may or may not exist: a PRD can have drafted Epics while it is still in product hands, so Epic presence plays no part.
- **Produces:** the release-notes draft, appended to `release-notes.md` in the PRD folder. Nothing is built yet, so the diff-grounding question recommends the PRD alone, and the note carries no documentation link and never asks for one.
- **Hands over:** the draft, by the same consented pull request into the specs repository's default branch, to whoever publishes release notes.
- **Cost phase:** `prd-creation`, role `pm`.

The companion `product-workflows` plugin's own Roles and phases page describes the PM role in full.

## Outside the roles: `/docs-profile` and `/docs-serve`

Neither command emits a cost entry, so neither is charged to a phase or a role. `/docs-profile` writes or refreshes the profile the other commands read, as a reviewable pull request; keyed `/document` also runs it inline, on a documentation repository that has no profile of its own and is not shaped like the plugin's built-in default one. `/docs-serve` starts, stops or checks the documentation site's dev server, or runs the site's build, and records nothing but its own run state. A correction to either through `workflows-core`'s feedback or `/prompt` commands is charged to `plugin-feedback`, since neither has a phase to inherit.

## Cost-attribution phases

Every cost-emitting command tags its cost line with a `phase` and a `role`. This plugin's seven cost-emitting commands reach four phases. Each can also be reached **by inheritance**: the companion `workflows-core` plugin's `/workflows-core:prompt`, `/workflows-core:feedback`, `/workflows-core:prompt-brainstorm` and `/workflows-core:prompt-grill-me` take the phase and role of the run they correct — for `/release-notes`, the pair its own inference gives. [Session cost](reference/session-cost.md) says where each entry lands.

### documenting

Emitted by `/document` in both modes, with a fixed `documenting`/`dev` pair, by `/docs-write` and `/docs-verify` with the same fixed pair, and by `/release-notes` where a `specification.md` or a `design.md` exists under the PRD's folder. Being in this phase means product documentation is being written, or verified, for work engineering has started on or shipped.

### prd-creation

Emitted by `/release-notes`, role `pm`, where neither a `specification.md` nor a `design.md` exists under the PRD's folder. The companion `product-workflows` plugin's `/idea` and `/create-prd` charge it too, and so does the companion `workflows-core` plugin's `/workflows-core:frames` on a folder asserting `kind: prd` or `kind: epic`. Being in this phase means the spend is the PM's product-definition work on a PRD, here its first release note.

### docs-scaffold

Emitted by `/docs-init` and by a standalone `/docs-brand`, role `dev`. A `/docs-brand` that `/docs-init` runs `--inline` emits nothing of its own: `/docs-init`'s one entry covers the whole scaffold, branding included. Being in this phase means a documentation repository is being set up or re-branded.

### docs-audit

Emitted by `/docs-audit`, role `dev`. Being in this phase means the documentation a product is missing is being worked out into a coverage grid and a backlog; no page is written.

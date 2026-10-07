# The backlog format — `.dev-workflows/docs-backlog.yml`

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Single source of truth for the file a documentation audit writes and every later command of this family reads: the schema in full (§1), why surfaces and units are two tables rather than one (§2), the unit status lifecycle and which of its transitions have a writer today (§3), what `blocked_by` carries (§4), what a `coverage` fraction counts (§5), where the file lives (§6), and the leak-guarding invariant between two fields, `visibility` and `page_path`, which no single-field validation can see (§7) — the other relations between two fields, a unit's `type` to its `audience` and its `evidence` to its `surface`, are §1's.

Consumed by `/docs-audit` and by the agents it dispatches — `docs-auditor`, `ia-planner` and `docs-audit-reviewer` — and, as they ship, by Spec 2's `/docs-write` and `/docs-verify` and Spec 3's `/docs-drift`, each of which names the section it is executing rather than restating it.

The vocabulary this file is written in is not defined here. **A surface kind, the page-`type` vocabulary, the four prioritisation signals, the five entry paths and the definition of done are all `${CLAUDE_PLUGIN_ROOT}/references/docs-audit/coverage-model.md`'s** — §2, §3, §5, §6 and §7 respectively. This file says what the *file* looks like; that one says what the words in it mean. Restating either half in the other is the drift this pair of files exists to prevent.

Its entry points, so a command can say which part it is executing: **the schema** (§1), **the lifecycle** (§3), **the coverage definition** (§5), **the file's location** (§6), and **the visibility invariant** (§7).

---

## 1. The schema

```yaml
schema_version: 1
generated_at: 2026-08-29
generated_by: docs-audit
sources:                              # every repo scanned, at the ref scanned
  - { repo: example-webapp, path: /workspace/example-webapp, ref: <sha>, scanned_at: <iso8601> }
  - { repo: example-api,     path: /workspace/example-api,     ref: <sha>, scanned_at: <iso8601> }
surfaces:                             # the denominator, enumerated once
  - id: order-placement
    kind: task                        # role|task|concept|reference|service|decision|release
    title: "Place an order"
    roles: [customer, admin]
    evidence:
      - { repo: example-webapp, path: src/routes/orders/new.tsx }
      - { repo: example-api,     path: app/controllers/api/v2/orders_controller.rb }
    volatility: high                  # high|medium|low, from git log density
units:                                # what gets written; many units per surface
  - id: U-001
    surface: order-placement          # a surface id, or null for a hand-written unit with no code behind it
    journey: []                       # surface ids a surface: null unit still fans out from; empty otherwise
    title: "Place an order"
    audience: user                    # user|engineering
    visibility: public                # public|internal — defaults from audience, set independently
    type: how-to                      # user: tutorial|how-to|reference|explanation
                                      # engineering: architecture|decision|runbook|api-reference
    roles: [customer]
    priority: 1
    priority_reason: "blocks primary journey; 2 roles; 3 evidence paths across 2 repos"
    churn_adapted: false
    status: missing                   # missing|drafted|verified|published|stale
    page_path: docs/guides/place-an-order.md   # the page, once one exists; the key is always present, null until then
    walkthrough: null                 # W-001 once composed
    evidence: []                      # hand-given evidence, written only on a surface: null unit
    blocked_by: []
tutorial_candidates:                  # ia-planner proposes; a human picks by editing this block
  - role: customer
    journey: [order-placement, payment, order-tracking]   # surface ids, in order
    rationale: "shortest path through the three highest-priority customer tasks"
    picked: false                     # a human sets this true; /docs-audit --refresh then mints its unit
    unit: null                        # the id of the unit that mint produced; null until it has run
coverage:
  user:        { tutorial: "0/2", how-to: "3/14", reference: "0/6", explanation: "1/5" }
  engineering: { architecture: "0/3", decision: "2/2", runbook: "0/4", api-reference: "0/1" }
threshold: 2                          # "done" = every unit with priority <= threshold is published
```

`surfaces[].kind` takes the seven values `coverage-model.md` §2 fixes; `units[].type` takes the eight `coverage-model.md` §3 fixes, four legal under each `audience`. Neither list is restated here, and a run that needs one loads that file rather than reading this block's comments as the authority — a comment is an illustration of the schema, not a definition of its vocabulary.

**`schema_version` gets the opposite disposition from an unrecognised `status`, and the contrast is the reason each is right.** A `status` a reader does not know is one unit's business: the reader reports that unit and leaves it alone (§3). A `schema_version` it does not know is a claim about the **whole file**, so a reader that met one and carried on would write a file it does not understand — silently dropping whatever the later version added, on every block it rewrote. So: where an **existing** backlog's `schema_version` is not a version this reader knows — higher, absent, or unparseable — the run **reports the file and writes nothing into it**. A run creating the file writes `1`, which is what this increment reads and writes.

**`surface: null` is a legal value and the schema admits it.** `coverage-model.md` §6's entry path 5 creates exactly this unit: one a human added for a page the code does not imply, with no surface to attach to. Three consequences, each of which some later reader would otherwise have to invent:

- **`units[].evidence` is where that unit's hand-given evidence lives**, in the entry shape `evidence-contract.md` §2 fixes. It is written **only** on a `surface: null` unit — every other unit's evidence is its surface's, which is §2's whole reason for two tables — and it is empty otherwise. The page, once written, still records its own `evidence:` frontmatter as every page does; the unit-level list is what the writer starts from, at a point where no page exists yet.
- **`units[].evidence` is not what drift reads, and recording it buys no drift coverage.** Drift diffs a **surface**'s evidence paths between `sources[].ref` and today, so a unit with no surface is outside that mechanism however full its own `evidence` list is — which is `coverage-model.md` §6's point: such a unit relies on its `review_by` date alone. The list is for the writer, not for drift.
- **`units[].journey` is the one exception to that**, and it exists for the tutorial mint below. A `surface: null` unit carrying a non-empty `journey` — a list of surface ids — fans out from every surface it names, so drift reaches it exactly as it reaches an ordinary unit. **That is a carve-out from `coverage-model.md` §6's sentence, not a disagreement with it**: §6 is written about its own entry path 5, the hand-written unit, whose `journey` is empty and which does rely on `review_by` alone; the tutorial mint is entry path 4, and it is the one null that carries a journey. So the run reports the `surface: null` count §6 requires **and, beside it, how many of those carry a `journey`**: one number covering both would say nothing about how much of the backlog drift cannot see, which is the only thing that count is for.

**At most one unit per `(surface, audience, type)` cell, over the units that name a surface.** A second unit in the same cell is a duplicate — two pages claiming to be the one page about that thing for that reader — and it inflates **both halves** of §5's fraction, so the figure moves while nothing was written. Where a surface genuinely earns two pages of one type, that is two surfaces or one page: `roles` is a list, so one `how-to` serves the customer and the admin without a second unit. `docs-audit-reviewer` checks this, because no single unit is wrong on its own. **A `surface: null` unit is outside the rule** — it shares no surface with anything, so two hand-written how-tos with no code behind them are two legitimate pages and not a duplicate.

**`threshold` is written once and preserved thereafter.** The **initial** run writes `threshold: 2` and says in its report that this is a starting value rather than a decision — priority 1 and 2 are the units whose absence blocks a journey or spans several roles, which is the smallest set anybody would call done. Every **later** run reads what is in the file and writes it back unchanged; nothing re-derives it, so an operator who moved it to 1 or 3 keeps it.

**`tutorial_candidates[]` is the one block a run proposes and never decides.** Which journey a role should learn first is the judgement `coverage-model.md` §4 states no scan can make, so `ia-planner` writes candidates and a human picks by setting `picked: true`. Two rules keep that act from being undone by the next run. A `--refresh` run **never rewrites `role`, `journey`, `rationale` or `picked` on an entry already in the file** — the four fields a human owns — and appends only candidates for a role that has none; regenerating the block would silently discard a `picked: true`, which is the one authority this quadrant has. Where it would have proposed a different journey for a role that already carries a candidate, it **says so in its report and changes nothing**: the block is the human's, and a better idea is worth telling them about and not worth overwriting them with. **`unit:` is the single field a run writes into an existing entry**, and only where it is still `null` — which is the second rule: a picked candidate is minted **once**, the mint records the new unit's id there, and an entry whose `unit:` is already set is never minted again. Without that recorded id, every later `--refresh` would mint a second tutorial unit for the same journey, each with a fresh id and none of them colliding with anything — a duplicate the collision rule in §8 cannot see, because nothing was reused.

**What the mint writes, in full, because "mints its unit" is otherwise an instruction nobody can follow.** A candidate's `journey` is a *list* of surface ids and `units[].surface` is a single one, so the mint cannot simply copy it across. It writes: `surface: null` with `journey` copied from the candidate — the sanctioned null that is **not** drift-blind, per the third bullet above, and the reason this unit needs no `evidence` of its own; `type: tutorial` and `audience: user`, which is what a tutorial is; `roles: [<the candidate's role>]`; `visibility: public`, the default `audience: user` implies; `title` composed from the role and the journey, and expected to be edited by hand; `priority` taken as the **best (numerically lowest) priority among the units of the surfaces the journey names**, because a tutorial is worth what the tasks it teaches are worth — and, where none of those surfaces carries a unit, the current `threshold`, so the unit lands at the boundary rather than silently at the top or the bottom; `priority_reason` naming its provenance and carrying the candidate's `rationale` verbatim (`"picked tutorial candidate for customer: <rationale>; ranked with the highest-priority task it teaches"`); and `churn_adapted: false`, `status: missing`, `page_path: null`, `walkthrough: null`, `evidence: []`, `blocked_by: []`. Both `priority` and `priority_reason` are then the operator's to correct, and the preservation rule below is what keeps that correction.

**What a `--refresh` re-derives and what it preserves.** The rule is not "everything is regenerated except the block that says otherwise", which is what a single preservation rule standing alone implies. A refresh **re-derives** `generated_at`, `sources[]`, `surfaces[]` (with their `evidence` and `volatility`) and every `coverage` figure — all of them statements about the code as it is now. It **preserves**: every unit already in the file, with its `page_path`, its `walkthrough`, its `title`, its `roles`, and its hand-written `surface: null`, `journey` and `evidence`; every hand-added unit, which is indistinguishable from any other unit once written and is not re-derived away; `threshold`; and the four human fields of every `tutorial_candidates[]` entry. **`status` and `blocked_by` are neither re-derived nor untouched, and the distinction matters**: a refresh writes each only through the two rules that define its writes — §3's reconciliation of a unit still `missing` against a page carrying its id, and §4's `[surface-removed]` and `[page-missing]` tokens — and changes them in no other way, so a `verified` unit is still `verified` afterwards and a token a run added last time is still there. **A `priority_reason` already in the file is preserved, and the priority the run would now derive is reported beside it rather than written over it** — `coverage-model.md` §6 puts the operator in this file to correct exactly that field, and they corrected it for a reason the scan cannot see. **The test is mechanical, so no run has to guess what a human touched**: the run derives this unit's priority and its reason; where the stored `priority_reason` is exactly the reason this run derives, nothing was edited and both fields take the new values; where it differs, both stored values stand and the run reports the pair it would have written.

---

## 2. Why surfaces and units are separate tables

One surface spawns several units across quadrants, and **drift is detected per surface and then fans out to that surface's units** — one detection, many consequences. A single flat list would do one of two things, both worse: duplicate the evidence on every unit, so that the same file path is recorded four times and can disagree with itself; or keep one row per surface and lose the fan-out, so that a change to a route has no way of reaching the three pages written about it.

`sources[].ref` is what makes drift computable at all. A backlog that recorded only *what* was scanned could tell you that a page exists; one that records the ref it was scanned at can tell you that the code has moved since. It is the commit `prep.scanned_ref` resolved to when the scan returned (`workflows-core:read-only-repos` §7), never that name itself, for the reason that section gives: a claim about a repository is only checkable against the exact commit it was made from, and a branch name moves.

---

## 3. The unit status lifecycle

`status` takes one of five values — `missing`, `drafted`, `verified`, `published`, `stale` — and moves along the transitions below and no others.

**The enum is closed against every writer that ships today, and open to a later spec adding to it — which is a property of this contract rather than a hedge, because the design already contains the sixth value.** The design's frozen schema fixes these five; the same design's process-capture section draws a lifecycle with a sixth, `captured`, reached from `missing` and from `stale` and leading to `drafted`, on the reasoning that a process-shaped unit (a `how-to` or a `tutorial`) cannot be drafted before somebody has walked and recorded the process. **The two disagree, and this file follows the five**, because nothing in this increment writes or reads a sixth and a value no writer produces is a state a reader has to handle for no benefit. So: **a reader of this file treats an unrecognised `status` as a value a later spec added, never as a corrupt file** — it reports the unit and leaves it alone, rather than refusing the backlog or normalising the value away. That one rule is what makes the addition cheap when it comes, and it is why this is stated here instead of being left for whoever meets the contradiction while implementing the capture command.

| From | To | What moves it | Which command writes it |
|---|---|---|---|
| *(none)* | `missing` | `/docs-audit` mints the unit | **`/docs-audit`, in this increment** |
| `missing` | `drafted` | a page is written for the unit — or `--refresh` finds one that still carries a marked claim | Spec 2's `/docs-write`; **and `/docs-audit --refresh`, in this increment** |
| `drafted` | `verified` | the page's claims are resolved | Spec 2's `/docs-verify` |
| `verified` | `published` | the page ships | **None, in any spec** — see below |
| `published` | `stale` | the code under the page moved | Spec 3's `/docs-drift` |
| `stale` | `drafted` | the unit is re-queued for rewriting | Spec 3's `/docs-drift` |
| `missing` | `published` | `--refresh` finds a page carrying this unit id **and carrying no marked claim** | **`/docs-audit --refresh`, in this increment** |

**Three values have a command writing them in this increment — `missing`, `drafted` and `published` — and every writer is `/docs-audit`**: the initial run mints units as `missing`, and a `--refresh` run reconciles a unit against a page already carrying its id (`coverage-model.md` §6, entry path 2), landing it on `published` or on `drafted` by the test below. `verified` and `stale` have no writer here at all, and the rows that name one name a command that does not ship yet. **Until Specs 2 and 3 ship, a human moves a unit between the rest by editing this file** — which is the same authority `coverage-model.md` §6's entry path 5 already gives them over the file's contents, exercised on one field.

**The reconciliation reads the page, and that read is what keeps the coverage figure honest.** A page can carry a `[NEEDS CLARIFICATION]` marker — `evidence-contract.md` §3 *requires* one wherever a claim could not be verified, and a person writing a page by hand is taught to leave it there. So a reconciliation that published every tagged page it found would take a page with an unresolved claim in it straight to the one state §5 counts, breaking `coverage-model.md` §8's rule against reporting green over a unit nothing verified — with a command of **this** increment, not a later one. So `--refresh` reads the page it matched:

- **No marked claim** → `published`. The unit records the human's assertion that the page is done, and the residual paragraph below stands: it rests on their tag and on no walkthrough.
- **One or more marked claims** → `drafted`, and the run reports the page, the unit and how many markers it found.

**`drafted` is the right landing and not a compromise.** Its own definition is *a page is written for the unit*, which is exactly the state in front of the run: the page exists, so `missing` would be a lie the reconciliation exists to correct, and its claims are unwalked, so `published` is the lie the coverage rule exists to prevent. The unit is then where an ordinary written page is, waiting for the verification pass, and no new value and no new rule was needed to say so.

**One row says *None, in any spec*, and it is the row that matters most.** `verified → published` is the page shipping — a branch merged and a site deployed — which is an act in the repository and not a command of this family: `/docs-write` writes the page, `/docs-verify` resolves its claims and moves it to `verified`, and neither of them claims this edge. So **a person moves a unit to `published` on the ordinary route, in this increment and after Specs 2 and 3 ship**, and the only automated write of that value anywhere is the `--refresh` reconciliation two rows below. Stating it here is the point: the state §5's coverage fraction counts is the one state no command of this family assigns on the route pages actually take. **A page can be merged at any status, and that is not this edge** — a page carrying marked claims ships with them showing (`evidence-contract.md` §3), and its unit still does not reach `published`: on the ordinary route it has not been `verified`, and a reconciliation that meets it sends it to `drafted`. What the edge records is the unit being done, which is why it starts at `verified` and at nothing else.

**`drafted → published` is not a transition, and its absence is a mechanism rather than an oversight.** `drafted` is the state of a page this family wrote and knows it has not walked: the writing pass leaves marked claims behind precisely because it could not resolve them (`evidence-contract.md` §3). An edge from there to `published` would let the family certify its own prose on the strength of having written it, and because §5's coverage fraction counts `published` units, the grid would then go green over exactly the pages nobody checked. The only route from `drafted` to `published` runs through `verified`.

**`missing → published` is not that same edge wearing a different name, and the difference is who is asserting what.** It fires only where a page exists carrying this unit's id in its `unit:` frontmatter key while the unit is still `missing`, **and that page carries no marked claim** — which means a person wrote that page, wrote that id onto it, and left nothing in it that says a claim went unchecked. The transition records **a human's assertion that the page is done**, which is the same authority that lets a human edit this file at all; `drafted → published` would be the family's assertion about output it knows to be unwalked, and a marked page found by the reconciliation is exactly that output, which is why it lands on `drafted` rather than here. The residual is worth stating rather than leaving to be discovered: a coverage figure raised this way rests on that person's tag and on no walkthrough — the absence of a marker says nobody recorded an unresolved claim, not that anybody walked one — and what catches it later is the page's own `review_by` date and the evidence contract the next command to touch it applies.

---

## 4. `blocked_by`

`blocked_by` is an **open list** of short tokens naming what is stopping this unit, empty on a unit nothing is stopping. It is open because the reasons a page cannot be written are not enumerable in advance — an unavailable environment, an undecided product question, a dependency on another unit — and a closed enum would force every one of them into a wrong bucket or out of the file.

**Two values are written in this increment, and both follow the same shape: record, report, leave the `status` alone.**

**`[surface-removed]`** — a `--refresh` run that no longer finds a unit's surface in the scan adds it and reports the unit; the unit's `status` is not changed, because nothing about the page has moved. **A unit whose `surface` is `null` has no surface to lose and is never marked `[surface-removed]`** — the check runs over units that name a surface, and a run that skipped that exemption would fire on every hand-written unit (§1) on every run, reporting a removal nothing removed.

**`[page-missing]`** — a `--refresh` run whose unit carries a `page_path` that no longer resolves in the docs repository adds it and reports the unit, leaving the `status` untouched. It is the mirror of `[surface-removed]` and takes the same disposition for the same reason: a page that is not where the backlog says it is has been moved, renamed, or never committed, and a run cannot tell those apart — least of all from a `published` unit, where clearing the status would erase the record that a page once shipped. So the finding is recorded and the person reading the report decides.

**A unit is never silently deleted, and never deleted at all by a run.** A surface disappearing from a scan is as likely to be a scan that failed or a repository that was not mounted as it is a feature that was genuinely removed — so the run records what it observed and leaves the judgement to the person reading the report, who can delete the unit by hand if the removal was real.

---

## 5. What `coverage` counts

**Per `(audience, type)` cell, `coverage` reports the fraction of that cell's units which have reached `published`** — the numerator is that cell's units whose `status` is `published`, the denominator is every unit in that cell whatever its status. `coverage-model.md` §7 states the same definition and **the two move together**: change one and change the other in the same edit, and treat `coverage-model.md` §7 as the authority where they ever disagree. Two files disagreeing about what a coverage fraction counts is how a grid comes to report done over prose nobody checked.

**It is not the number of units whose page exists.** A unit can have a `page_path`, a written page and a `status` of `drafted` and contribute **nothing** to its cell's numerator, and that is the whole point of the fraction: §3's missing `drafted → published` edge is the mechanism, and this definition is what makes the mechanism visible in a number somebody reads. A coverage figure derived from "has a `page_path`" would be green the moment prose existed.

Every figure in `coverage` is derived from the `units[]` table **in the same run that writes it**. A fraction carried forward from a previous run, or adjusted by hand, describes a backlog that is no longer the one in the file.

`threshold` is the priority at or above which `coverage-model.md` §7's definition of done applies — every unit whose `priority` is less than or equal to it must be `published`. It is a number the operator sets; nothing derives it, and §1 states what the initial run seeds it with and why every later run writes it back unchanged.

---

## 6. Where the file lives

`docs-backlog.yml` lives at **`<top>/.dev-workflows/docs-backlog.yml`**, where `<top>` is the **git work-tree top level of the resolved docs repository** — what `git -C <resolved> rev-parse --show-toplevel` prints, or the resolved directory itself where it is in no git work tree. That is the one home `references/docs-profiles/docs-profile-schema.md` already pins for `docs-profile.yml` and for `/docs-serve`'s `docs-serve.state.json`, and this file joins them there rather than inventing a second rule.

**The distinction matters exactly where the resolved directory is not the top level** — a `site/` beside the code, a `website/` in a monorepo. The backlog is at the top level in both cases, never beside the content root: **one repository has one backlog, however many content roots it publishes**, because the denominator is the product's surfaces and a product does not acquire a second set of them by publishing two sites.

**The file is tracked, and reviewed in a pull request.** In a repository this family scaffolded that follows from the scaffold's own `.gitignore` block, which ignores `/.dev-workflows/docs-serve.state.json` by name and deliberately not the directory, because that directory also holds the committed `docs-profile.yml` (`references/docs-workflow/scaffold-tree.md`, *`.gitignore`*). **That argument reaches only the repositories this family wrote, and `/docs-audit` runs against repositories it never scaffolded**, whose own `.gitignore` may carry a `.dev-workflows/` or a `*.yml` line nobody thought about. So the run does not assume it: it tests the path it is about to write with `git -C <top> check-ignore -v <path>` and, on a match, **reports the path, the matching line and its file rather than force-adding past the project's own rule** — the backlog is still written, and the run says plainly that it will not be committed until somebody changes that line. A tracked backlog is the point of the file; an untracked one written in silence is the failure worth catching. That is what makes `coverage-model.md` §6's entry path 5 a sanctioned act rather than a workaround: a human editing the backlog is proposing a change through the same review everything else in the repository goes through.

---

## 7. `visibility` and `page_path` are not independent

`visibility` and `page_path` look like two free fields on a unit and are not. **The shipped two-build split decides by path**: a page is internal because it sits under `docs/internal/`, which is what `exclude_docs` drops from the public build (`references/docs-workflow/visibility.md` §1, and `references/docs-profiles/frontmatter-guidelines.md` says so outright of the frontmatter key). Nothing in either build reads a `visibility` value.

**So the invariant is: `visibility: internal` ⇒ `page_path` under the internal tree.** A unit marked `visibility: internal` whose `page_path` falls outside `docs/internal/` describes a page that **ships publicly**, and no build objects — gate 1 passes, because nothing links across a boundary; gate 2 passes, because the page carries no internal marker to find. The field says internal, the artefact is public, and the two agree with each other nowhere.

This is `docs-audit-reviewer`'s to check, because it is a relationship between two fields and no single-field validation can see it: `visibility: internal` is a legal value, `docs/guides/x.md` is a legal path, and only the pair is wrong.

**The invariant is stated one way round on purpose, and the direction is the one where the cost lands.** `visibility: internal` on a public path is a **leak** — content somebody marked internal, published, with both build gates green. The other pairing, `visibility: public` on a path under `docs/internal/`, is a disagreement too, and it **fails safe**: the page simply does not ship, and a missing page is noticed far sooner than an extra one. Report both; only the first is an invariant, because only the first is a leak.

---

## 8. Hard rules

- NEVER delete a unit. A run records a `blocked_by` token and reports it; deletion is a human's act (§4).
- NEVER write a `coverage` figure that was not derived from the `units[]` table in the same run (§5).
- NEVER count a unit toward `coverage` on the strength of its page existing. The numerator is `published` units and nothing else (§5).
- NEVER mark a unit `published` on a page carrying a marked claim. A reconciliation that finds one lands the unit on `drafted` (§3).
- NEVER write a second unit into a `(surface, audience, type)` cell that already has one (§1).
- NEVER mint a unit id that collides with one already in the file, and never mint a second unit for a `tutorial_candidates[]` entry whose `unit:` is already set (§1).
- NEVER rewrite `role`, `journey`, `rationale` or `picked` on a `tutorial_candidates[]` entry already in the file, or a `priority_reason` a human has edited (§1).
- NEVER write into a backlog whose `schema_version` this reader does not know (§1).
- NEVER write a `page_path` for a page that does not exist.
- NEVER write a `page_path` that contradicts the unit's `visibility` (§7).
- NEVER move a unit to `published` from `drafted`. The route runs through `verified` (§3).
- NEVER mark a `surface: null` unit `[surface-removed]`. It has no surface to lose (§4).
- NEVER re-derive the surface kinds, the type vocabulary, the prioritisation signals or the definition of done here. They are `coverage-model.md`'s, cited by section.

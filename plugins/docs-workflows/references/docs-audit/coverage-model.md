# The coverage model — surfaces, page types, and how a unit is ranked

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names, unless that part is already in this conversation word for word; never guess a part's name — until you hold the index (every part carries it), load it with `args: "<name> index"`. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

Single source of truth for the vocabulary a documentation audit is built on: what a **surface** is and where each kind comes from (§2), what a page's **type** is and what the coverage grid is a grid of (§3), which quadrant does not automate (§4), the four **prioritisation signals** and the one guard on them (§5), how a **unit** enters the backlog (§6), and what **done** means (§7).

Consumed by `/docs-audit` and by the agents it dispatches — `docs-auditor`, `ia-planner` and `docs-audit-reviewer` — each of which names the part of this file it is executing rather than restating it. These names are defined once, here; a command or agent body that re-derives them is the defect this file exists to prevent, because two copies of a vocabulary drift and then disagree about what a run produced.

Its entry points, so a command can say which part it is executing: **the surface kinds** (§2), **the type vocabulary and the grid** (§3), **the signals** (§5), **the entry paths** (§6), and **the done criterion** (§7).

---

## 1. Why a denominator

An audit cannot list what is missing without a denominator — the set of things a product could be documented against. It builds one from code, and from the specs tree's committed decisions and release-notes drafts (§2), so the denominator is derived rather than asserted, and can be rebuilt when either moves.

---

## 2. Surfaces

A **surface** is a thing in the product that documentation can be about. Five of the seven kinds are enumerated mechanically from the scanned repositories; `decision` and `release` are enumerated from the specs tree, by `/docs-audit`'s own read (its Phase 2.5):

| Surface kind | Derived from | Feeds |
|---|---|---|
| `role` | The authorisation model — roles, permissions, policy objects | The role axis of every user unit |
| `task` | Routes, controller actions, UI flows, forms | **how-to** guides |
| `concept` | Domain models, the ubiquitous language in the code, state machines | **explanation** pages |
| `reference` | API endpoints, configuration keys, jobs, data schemas, CLI | **reference** pages |
| `service` | Deployables, containers, external integrations | engineering **architecture** pages |
| `decision` | ADRs and ARDs already present in the specs repo | engineering **decision** records |
| `release` | `/release-notes` drafts under `$SPECS_PATH`, grouped by release version | **What's new** pages: one per major version, plus its maintenance page |

Roles are a coverage **dimension**, not a nice-to-have: *what can a user in role R actually do* is the question user documentation exists to answer, and it is the reason walkthroughs are role-scoped. A `role` surface therefore does two things at once — it earns its own page, and it becomes an axis on every user unit (§6).

Because the enumeration is mechanical, it is only as good as the scan behind it. **A theme the scan could not resolve is named, never enumerated as a surface with `missing` cells**: a `missing` cell asserts that a page does not exist, while an unresolved theme asserts only that the scan could not tell, and flattening the second into the first puts units in the backlog that nothing verified (`workflows-core:model-routing/classification` §8.5).

---

## 3. Page types

**Diátaxis is used at exactly one level: it is the page `type`, and nothing else.** It is the second axis of the coverage grid, and it is a reserved frontmatter key — `references/docs-profiles/frontmatter-guidelines.md`, *Reserved keys for the docs-workflow family*, which fixes `type` alongside `audience`, `visibility` and `unit`. Do not confuse it with `meta.content-type`, a differently-named enum the plugin's own `docs-frontmatter` skill owns; the two are separate keys, and the coverage grid's axis is the page type as a backlog unit records it — the grid is computed from `units[]` and reads no page's frontmatter. It is **not** the navigation, **not** the folder tree, and **not** a per-surface quota.

**That reserved-key section states the same user and engineering type vocabulary this section does, and the two copies move together.** It is the one sanctioned second *authoritative* copy, because the frontmatter side has to state what a page may write and the coverage side has to state what a cell may be. They agree today, which is exactly when a drift between them would be invisible: change one and change the other in the same edit, and treat this file as the authority where they ever disagree. **It is not the only other place the eight names are written**: `backlog-format.md` §1's schema comments, `commands/docs-audit.md`'s Final Report *Coverage* template, and two human-facing pages, `docs/reference/docs-coverage-model.md` and `docs/docs-workflow.md`, list them illustratively and are no authority — but a change to the vocabulary goes stale in them too, so sweep them with it. `grep -rl 'api-reference' plugins/docs-workflows --exclude=CHANGELOG.md` finds every file that names the vocabulary.

**Both halves of that are one rule, and a reader who takes only the first mis-builds the nav.** The quadrant discipline governs what a page *is*, and the mechanism is the key itself: `type` is single-valued, so a page that answers two kinds of question has no legal value and is two pages. What the reader sees is a product-shaped portal, organised by what the product does rather than by any of the eight type names — the engineering four as much as the Diátaxis four, since `internal/runbooks/` is the same mistake as `how-to/` and is likelier to look reasonable. Neither statement weakens the other: the first is an authoring constraint, the second is an information-architecture one, and a scaffold that applies the first to the directory tree has mistaken a page property for a layout.

Coverage is a grid of `(surface, audience, type)` cells, each one of `exists | missing | stale`.

- **user** types: `tutorial`, `how-to`, `reference`, `explanation`
- **engineering** types: `architecture`, `decision`, `runbook`, `api-reference`

---

## 4. Tutorials do not automate

Three of the four user quadrants are derivable from code: a `task` surface implies a `how-to`, a `concept` surface implies an `explanation`, and a `reference` surface implies a `reference` page. **The fourth is not.** A tutorial is a curated primary journey for a role — which of the many things a role can do is the one worth learning first, and in what order — and nothing in the code says that.

So the audit **proposes** and a human picks: the shortest path through the highest-value tasks for each role becomes a tutorial candidate. Stating that plainly is better than pretending the quadrant automates, because which journey is worth learning first is the one judgement no gate in this family can re-derive: the walkthrough can confirm every step and still confirm the wrong tutorial.

**How the human picks is settled: the candidates are a marked section of the backlog, not an interactive picker.** `ia-planner` writes them into a `tutorial_candidates:` block in `docs-backlog.yml`, and the human picks by editing that file. Three reasons, in order of weight: the candidate set is one journey per role and therefore unbounded by construction, where an `AskUserQuestion` array renders at most four options (`workflows-core:escalation-rules` §0); the operator is already in this file, reading the top-ranked units and correcting each `priority_reason`, so picking there adds no new interaction; and hand-editing the backlog is entry path 5 of §6 — a sanctioned act rather than a workaround.

---

## 5. Prioritisation

Four signals, combined into a rank, with a written `priority_reason` on every unit:

1. **Blocks the primary journey** — can a user in role R accomplish the main thing at all without this page? **Highest weight.**
2. **Role breadth** — how many roles touch the surface.
3. **Evidence availability** — write first what can be grounded now. A page that cannot be verified is a page that ships wrong.
4. **Volatility, inverted** — measured from `git log` density per surface path over a trailing window. High churn lowers rank.

**The guard on signal 4: volatility only ever *ranks*, and can never *exclude*.** A surface nobody has finished changing is still a surface a user meets today, so an excluded one is a documentation gap the audit has hidden from itself rather than a cost it has avoided.

So where a high-volatility surface also scores high on signal 1, **the unit is written**. What changes is its `type`, not its existence: the choice is biased away from step-by-step (`how-to`, and screenshots in particular) toward `explanation` and `reference`, which survive churn because they describe what a thing is rather than which control to click. The unit records `churn_adapted: true` with the reason, so the choice is visible to the next reader rather than silently baked into a type nobody can account for.

---

## 6. How a unit enters the backlog

**One unit is one page.** A surface is a thing in the product; a unit is a page about it. The two are separate tables in the backlog because one surface usually earns several pages, and because drift is detected per **surface** and then fans out to that surface's units — one detection, many consequences.

**A unit is created by crossing a surface with the types that surface actually earns — never by a mechanical cross-product.** That judgement is `ia-planner`'s. `order-placement`, a `task` surface, earns a `how-to` and probably a `reference` for the endpoint behind it; it does **not** earn an `architecture` page. A `concept` surface earns an `explanation`. A `role` surface earns the roles page *and* becomes a dimension on every user unit (§2). A mechanical cross-product gives **every** surface eight units, one per type, most of which are pages nobody should write — and each one that goes unwritten is then a `missing` cell the coverage figure reports, so the cross-product corrupts §7's done criterion as well as the backlog.

Five entry paths, and only the first three are automatic:

| # | Path | Automatic | Produces |
|---|---|---|---|
| 1 | `/docs-audit` — the initial run | Yes | Every unit the enumerated surfaces earn. This is where a backlog comes from on day one |
| 2 | `/docs-audit --refresh` — a later run | Yes | Units for surfaces that did not exist before: a new route, a new role, a new integration, a new release. Existing pages are matched back to their units and marked `published` |
| 3 | `/docs-drift`, when that command ships | Yes | No new units. It moves existing ones to `stale` and re-queues them |
| 4 | Tutorial selection | No | The audit proposes candidates; a human picks, and the picks become units. The one quadrant that does not automate (§4) |
| 5 | A human editing `docs-backlog.yml` | No | Anything the code does not imply — a page answering a question a customer actually asked, a migration guide, a policy, a comparison |

Path 5 is a normal act rather than a workaround, and the backlog is a tracked file reviewed in a pull request precisely so that it is one.

**Path 5 has one consequence that must be stated rather than discovered.** A unit's `surface` is what drift watches. A hand-written unit therefore does one of two things: it **attaches to an existing surface**, and then drift covers it exactly like any other unit; or it declares **`surface: null`** with its `evidence` given by hand, in which case **drift cannot tell when it goes stale** and the unit relies on its `review_by` date alone. That is an acceptable trade and not a defect — some pages genuinely have no code behind them — but it is a trade, so the audit reports the **count** of `surface: null` units on every run, and it never grows unnoticed. **Read that as being about *this* path's units, because one other kind of `surface: null` unit exists and it is not drift-blind**: path 4's minted tutorial carries a `journey` — the list of surface ids its route crosses — and drift fans out to it from every surface it names (`backlog-format.md` §1). So the run reports two numbers rather than one: how many units carry no surface, and how many of those also carry no `journey`. The second is the one that says how much of the backlog drift genuinely cannot see, which is the only thing this count was ever for.

---

## 7. Definition of done

Documentation work has no natural end, so this family defines one:

> **Done** = every backlog unit at or above a chosen priority threshold has a published page, and every claim on those pages is either evidence-backed or visibly marked.

`coverage` in the backlog reports, per `(audience, type)` cell, the fraction of that cell's units which have reached `published` — which is what makes that sentence checkable, and what makes a cell's figure move only when a page has actually been verified and shipped rather than merely drafted. "We wrote a lot of docs" is not a completion criterion; a coverage grid with a threshold is.

---

## 8. Hard rules

- NEVER re-derive the surface kinds (§2) or the type vocabulary (§3) in any other file. Cite this file and name the section — the one sanctioned second authoritative copy of the type vocabulary is the frontmatter-side statement §3 names, and the two move together; the illustrative copies §3 lists move with them.
- NEVER let volatility exclude a surface. Signal 4 ranks, and only ranks (§5).
- NEVER cross-product a surface with every type. A unit exists for a type the surface actually earns (§6).
- NEVER report coverage green over a unit nothing verified. A unit carrying unconfirmed claims is not `published`, and the coverage fraction counts published units (§7); a scan theme that could not be resolved is not a surface (§2).
- NEVER apply the quadrant discipline to the navigation or the folder tree. It is the page `type` and nothing else (§3).
- NEVER generate a tutorial and present it as picked. The audit proposes; the human picks by editing the backlog (§4).

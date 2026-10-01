# The documentation backlog

The audit's output is one file: **`.dev-workflows/docs-backlog.yml`**, a list of every page your product could have, what each one is about, which ones exist, and what order the rest are worth writing in. It is not a report you read once — it is a file you keep, edit, argue with in a pull request, and re-run the audit against.

This page explains what is in it and how to work with it. The runnable version — the one `/docs-audit` and its agents execute — is the plugin's own `references/docs-audit/backlog-format.md`. The vocabulary the file is written in (what a surface is, what a page type is, what decides priority) is on [the coverage model page](docs-coverage-model.md).

## Where it lives, and why it is committed

The backlog sits at **the git top level of your docs repository**, in `.dev-workflows/`, beside the profile `/docs-profile` writes and the state file `/docs-serve` keeps. That is one home and not a per-site one: if your repository publishes two sites — a `site/` beside the code, a `website/` in a monorepo — there is still **one backlog**, because the denominator is your product's surfaces and publishing twice does not give you a second set of them.

**It is meant to be tracked in git and reviewed in a pull request**, exactly like the profile beside it. In a repository this plugin scaffolded it will be: the scaffold's `.gitignore` ignores only `/docs-serve`'s state file by name and deliberately not the `.dev-workflows/` directory. Your repository may not be one of those, and its own `.gitignore` may well have a line that catches this path — so the run checks, and if something ignores the file it **tells you the path, the rule and the file the rule is in, rather than force-adding past it.** The backlog is still written; you decide whether to change the rule.

**Editing it by hand is normal.** It is one of the five ways a page gets into the backlog, and the intended way for anything the code does not imply — a migration guide, a policy page, a comparison, the question a customer actually asked. Because the file is reviewed like code, a hand-added page is a proposal somebody can disagree with rather than a private note.

## What is in it

| Block | Holds | Written by |
|---|---|---|
| `sources` | Every repository the run scanned, with the commit it was scanned at | The audit |
| `surfaces` | The denominator — every thing in the product documentation could be about | The audit |
| `units` | One entry per page: what it is about, who for, what type, what priority, what state | The audit, then you |
| `tutorial_candidates` | Proposed first journeys, one per role. **You pick** by setting `picked: true` | Proposed by the audit, picked by you |
| `coverage` | A fraction per audience-and-type cell | The audit, derived from `units` |
| `threshold` | The priority at or above which "done" applies | Seeded at 2 by the first run, yours thereafter |

Two things in that table are worth reading twice. **`sources` records a commit, not just a path** — that is what later makes it possible to say the code has moved since a page was written, rather than only that the code exists. And **`tutorial_candidates` is the one block the audit will not decide for you**: which journey a role should learn first is a judgement no scan can make, so the audit proposes and you pick by editing the file.

Your picks are safe from the next run. A `--refresh` never rewrites the four fields you own on an entry that is already there — the role, the journey, the rationale and `picked` — and only appends candidates for a role that has none, so `picked: true` is never quietly undone. The one field a run does write into an existing entry is `unit`, and only while it is still empty: when a picked candidate becomes a real unit, the run records that unit's id there, which is what stops the next run from minting a second page for the same journey.

**Two rules bind a unit you add by hand.** There is **at most one unit per surface, audience and page type** — a second is a duplicate that moves the coverage fraction without anything being written, and a page serving two roles is one unit with two roles listed, not two units. And a unit for a page the code does not imply sets **`surface: null`** and gives its evidence on the unit itself; such a page has nothing for drift to watch, so it relies on its `review_by` date, and every run tells you how many of these you have.

## The states a page moves through

Every unit carries a `status`. These are the transitions, and the only ones:

```mermaid
stateDiagram-v2
  [*] --> missing: "/docs-audit mints the unit"
  missing --> drafted: "a page is written, or --refresh finds one with unchecked claims"
  drafted --> verified: "its claims are walked"
  verified --> published: "the page ships"
  published --> stale: "the code moved under it"
  stale --> drafted: "re-queued"
  missing --> published: "/docs-audit --refresh finds a page carrying this unit id and no unresolved claim markers"
```

**Three of those seven transitions have a command behind them today, and it is `/docs-audit` every time.** The initial run mints units as `missing`; a `--refresh` run that finds a page already carrying the id of a unit still `missing` moves that unit to `published` or to `drafted`, by the test in the next paragraph. The rest are drawn for commands that make it up the road — `verified` belongs to the verification command of the next spec, `stale` to the drift command of the one after, and the writing command of the next spec also moves a unit to `drafted` when it writes the page — and **until those ship, you move a unit between those states by editing the file.** The diagram shows the model, not seven pieces of automation you have today.

**The refresh reads the page before it decides, and this is the part worth knowing if you write pages by hand.** A page with a `[NEEDS CLARIFICATION]` marker left in it has a claim nobody checked — that marker is exactly what you are meant to leave (see [Evidence and walkthroughs](docs-evidence.md)). So a refresh that found such a page and published its unit would put an unchecked claim straight into the coverage figure. It does not: **a matched page with no marker takes its unit to `published`, and a matched page with a marker takes it to `drafted`**, with the page, the unit and the marker count in the run's report. Resolve the markers, then move the unit to `verified` yourself by editing the file: a refresh reads a page only for a unit still `missing`, so it never revisits one it left `drafted`. Until the verification command lands, that edit is how a unit leaves `drafted`.

**One arrow has no command behind it in any of the three specs, now or later: `verified → published`.** That is the page shipping — a branch merged, a site deployed — which happens in your repository rather than in a command here. **You mark a unit `published`**, today and after the rest of the family lands. It is worth knowing which arrow that is, because `published` is the state the coverage fraction counts.

**There is deliberately no arrow from `drafted` to `published`, and that missing arrow is doing real work.** `drafted` means a page exists whose claims have not been walked — the writing pass leaves markers behind exactly where it could not confirm something. If a page could go straight from there to `published`, the coverage figure would go green over the pages nobody checked, which is the one number in this file worth having. The only route runs through `verified`.

The arrow from `missing` to `published` is not that same jump under another name. It fires only when a page already exists carrying the unit's id **and carrying no unresolved marker** — which means **a person wrote that page, tagged it, and left nothing in it saying a claim went unchecked**, and the audit is recording their judgement rather than making one of its own. Worth knowing what it rests on, though: that tag, and no walkthrough. The absence of a marker means nobody recorded an unresolved claim, not that anybody walked one — the page's `review_by` date and the evidence rules are what catch that later.

## What the coverage fraction counts

`coverage` reports, per audience-and-type cell, **the fraction of that cell's units that have reached `published`**. Not the fraction whose page exists. A unit can have a written page, a `page_path` and a status of `drafted`, and contribute **nothing** to the numerator — which is the point: a coverage grid that counted prose would be green the moment somebody typed, and this one only moves when a page has been checked and shipped.

Every figure is recomputed from the `units` list in the same run that writes it. If you hand-edit a status, the number is stale until the next run; re-running the audit is what settles it.

## One trap worth knowing before you hand-edit

A unit carries both `visibility` (`public` or `internal`) and `page_path`. They look independent and are not. **The two-build split decides by path**: a page is internal because it sits under `docs/internal/`, which is what the public build drops. Nothing in either build reads `visibility`.

So a unit marked `visibility: internal` whose `page_path` is outside `docs/internal/` describes **a page that ships publicly**, and no build will complain — the link gate passes because nothing crosses a boundary, and the marker gate passes because the page carries no internal marker to find. The field says one thing and the artefact does another. If you set `visibility: internal` by hand, put the path under the internal tree in the same edit; the review gate checks the pair, because neither field is wrong on its own.

## What a run will never do to this file

- **Delete a unit.** A `--refresh` that can no longer find a unit's surface marks it `blocked_by: [surface-removed]` and reports it, leaving the status alone. A surface vanishing from a scan is as likely to be a repository that was not mounted as a feature that was really removed, and a run cannot tell those apart. Deleting it is your call. A unit whose `page_path` no longer resolves gets the mirror treatment — `blocked_by: [page-missing]`, reported, status untouched — because a page that has moved, been renamed, or was never committed look identical from here, and clearing a `published` status would erase the record that a page once shipped.
- **Write a coverage figure it did not derive from the units in the same run.**
- **Mint a second unit for a tutorial candidate it has already minted one for.**
- **Overwrite your tutorial picks.**

## See also

- [The coverage model](docs-coverage-model.md) — surfaces, page types, and what decides the order pages get written in.
- [Evidence and walkthroughs](docs-evidence.md) — what a page's claims are allowed to rest on, and how a claim gets checked.

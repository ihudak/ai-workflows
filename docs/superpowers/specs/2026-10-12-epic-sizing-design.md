# Epic sizing for one agent run — design

**Date:** 2026-10-12 · **Plugin:** product-workflows (`/epics`, `epic-writer`, `epic-reviewer`) · **Status:** approved in conversation, awaiting spec review

## 1. Problem and intent

`/epics` gives every Epic exactly one `target:` component, so each lands in one technology its developer knows. That rule is right and stays. Its side effect was not intended: within one component the writer is told to *"prefer fewer, larger Epics when the PRD direction is validated; split only at a genuine risk or feedback-loop boundary"* (`epic-writer.md` *Sizing / sequencing*; `epics.md` Phase 2), and the reviewer has no size dimension. So all of a component's work tends to become one Epic, whatever its size.

Measured on the BOOK-1 demo PRD (`~/dev/demo/bookstore-specs`, six Epics):

| Epic | Suggested stories | Acceptance criteria | Requirements covered |
|---|---|---|---|
| 01 alerts-service | 7 | 8 | 21 |
| 05 web-alerts-ui | 8 | 8 | 18 |
| 06 ingest-journey | 5 | 6 | 3 |
| 03 books-removal-and-reset | 4 | 4 | 6 |
| 02 storage-restock-notice | 4 | 3 | 4 |
| 04 clients-reserved-data | 2 | 3 | 2 |

Downstream does not split a big Epic for the agent. `/design` writes one `design.md` per Epic. `/implement` has the session model work through every step itself in one context (Phase 3A/3B "Work through each step in order"); only `[P]`-marked steps may go to fresh subagents (`context-management.md`), one Opus `code-review` covers the whole diff, and the fix loop is capped at two attempts.

**Intent (the user's):** keep the per-component split for technology fit, and size each Epic so one `/implement` run can do it well — quality first, accepting more `/design`, `/implement` and `/conformance` runs and more pull requests, since poor quality returns as bugs.

## 2. Decisions

**D1 — The limit.** An Epic holds at most **5 acceptance criteria** and at most **4 suggested stories**. It is over the limit where it has more than 5 or more than 4. Each is counted as the top-level `- ` bullets directly under `## Acceptance criteria` and `## Suggested stories` — a guard criterion counts like any other. A count, never a judgement.

**D2 — One authority for the numbers.** `/epics` owns them, as `size_limit: {criteria: 5, stories: 4}`, and hands them to `epic-writer` and `epic-reviewer` in their briefs. Neither agent states the numbers itself; the docs page states them as the current values. Calibrating the limit later is one edit.

**D3 — The writer splits as it drafts.** `epic-writer`'s *Sizing / sequencing* step drops "prefer fewer, larger Epics". Work for one component that would exceed the limit becomes several Epics on the **same** `target:`, cut along story boundaries:
- each carries its own stories, the criteria those stories satisfy, the requirements they cover (`## Covers`) and its own `## Independent Test`;
- they are ordered so none depends on a later one, and keyed consecutively in that order;
- each is titled by the user value it delivers (the reviewer's *Goal clarity* rule), never "part 1";
- an `[AD#N]` interface keeps exactly one producing Epic; a consumer in the same component comes after it;
- a criterion or story that bundles several independently testable behaviours to stay under the limit is not a way under it.

The wide-refactor sequencing (expand → migrate-in-batches → contract) and the one-target rule are unchanged.

**D4 — The plan states the rule.** Phase 2's sizing bullet becomes: one Epic per component, sized for one agent run — no Epic over the limit, split along its stories. A plan revision may name work to keep whole and why; the writer then writes that Epic whole, with the operator's words as its `kept_whole` reason (D8).

**D5 — The run counts, then asks about misses.** After `epic-writer` returns (a new step at the end of Phase 6, before clarifications, style, review and handoff, so everything after it sees the final set), `/epics` counts every Epic this run wrote or refined. For each over the limit with no `kept_whole`:

```
choices: ["Split it along its stories (Recommended)", "Keep it whole — give the reason", "Cancel"]
```

- **Split** re-dispatches `epic-writer` on that Epic to split it (D3), then counts again. A split result still over the limit is asked about once more, without *Split*: `["Keep it whole — give the reason", "Cancel"]`.
- **Keep it whole** asks for the reason in plain text and records it (D8).
- **Cancel** ends the run as the command's other cancels do.
- A typed answer is acted on as the option it expresses; anything else is asked again.

**D6 — The reviewer checks size.** `epic-reviewer` gains a conditional *Epic size* dimension, active when the brief carries `size_limit`:
- an Epic over the limit with no `kept_whole`, whose folder holds no `specification.md`, `design.md` or `implementation.md` → **MAJOR**;
- one with `kept_whole` → no finding; its reason is noted;
- one whose folder holds any of those three → reported, never a finding (D7: it cannot be split);
- a criterion or story bundling several independently testable behaviours → **MAJOR**, whatever the count.

**D7 — Re-splitting with `/epics <EPIC-KEY>`.** The focus run counts the Epic after refining it.
- **Over the limit, and its folder holds no `specification.md`, `design.md` or `implementation.md`** → D5's question. On *Split*, the Epic **keeps its key and the first slice** — the one the others depend on — and the new slices take the next unused keys; their `## Dependencies` and `_coverage.md` are updated. This reuses the writer's existing focus-run split (`mode: both`), with size as the reason instead of a component move.
- **Over the limit, but already specified, designed or implemented** → no split is offered; the report says it is oversized and that its specification, design or implementation describes the whole Epic.

**D8 — Records.**
- `epic.md` gains one optional frontmatter field, `kept_whole: "<reason>"`, written only from the operator's words — a D5 answer or a D4 plan revision — never from the writer's own judgement.
- Phase 9's report gains a `### Sizing` block: each Epic's criteria and story counts; the Epics split and what from; the Epics kept whole and why; and, on a full PRD run, every existing Epic over the limit — with `/epics <EPIC-KEY>` where D7 allows a split, or why not.
- `_coverage.md` keeps its shape: each requirement still in exactly one Epic's `## Covers`.

**D9 — Unchanged.** One target per Epic; `/design`'s *Re-split* for a component move; the wide-refactor sequencing; requirement coverage; a full PRD run never re-drafts an existing Epic; `/specify`, `/design`, `/implement` and `/conformance`.

**D10 — Docs and release.** The two statements of "prefer fewer, larger Epics" (`epics.md` Phase 2, `epic-writer.md` *Sizing / sequencing*) are rewritten, with the claim swept by subject and counted before and after (`.claude/rules/claim-sweep.md`). `docs/commands/epics.md` gains a sizing section. CHANGELOG entry; product-workflows **3.32.0**.

## 3. Out of scope

- Running `/implement`'s steps in fresh subagents with per-step review — a larger change to the most complex command; revisit only if smaller Epics still show quality falling with size.
- A flag or setting for the limit — D2 keeps it one edit; add one only if calibration shows teams need different numbers.
- Splitting an Epic already specified, designed or implemented (D7).

## 4. Testing

- String assertions per decision, written failing first: the writer's split rule and its loss of "fewer, larger"; the Phase 2 bullet; the count step and both D5 arrays; D7's eligibility condition and key rule; the `kept_whole` field; the reviewer dimension; the `### Sizing` block; the docs section.
- The full CI gate chain.
- Opus review rounds until nothing above Minor remains.
- **Calibration, live:** `/epics` on the BOOK-2-01 demo PRD, then its `/conformance` results — discrepancies per Epic against Epic size — to confirm or move the limit.

## 5. Risks

- **The limit is a guess** until calibrated (D2 makes moving it cheap).
- **More Epics** mean more runs, pull requests and handoffs — the accepted trade.
- **Gaming the count** with compound criteria or fat stories — D3 rules it out for the writer and D6 makes it a MAJOR for the reviewer, beside the existing *Acceptance criteria* and *Suggested stories* dimensions.

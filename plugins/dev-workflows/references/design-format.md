# Design format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical structure and per-section rules for an engineering `design.md`. `/design` authors
against this file; `design-reviewer` reviews against it, `interface-designer` reads its `## Seams` dependency categories, and `/ready` reads its `- **Repos**:` header. **Net-new — authored for the dev-workflows
plugin, no import source.**

## Principle — decision-dense, scalable

A `design.md` records **engineering decisions**, not prose. Include a section only when it carries a
real decision for this change; omit a section that does not apply and replace it with a one-line
`_N/A — <why>_`. Never pad. The classification (`SIMPLE` → `HIGH-RISK`) scales how many sections appear
and how deep each goes — a `SIMPLE` design is a few decisions; a `HIGH-RISK` design is thorough across
every section.

**Natural-language prose is the default medium; a decision-encoding snippet is the exception.** Where
a snippet — a state machine, reducer, schema, or type shape — encodes a decision *more precisely than
prose can*, inline it (note it if it came from a prototype) and trim it to the decision-rich parts.
Never paste a whole prototype; the snippet earns its place only by pinning down a decision prose would
leave ambiguous.

## Frontmatter

```yaml
---
kind: design                 # what this document is
key: <KEY>                   # this folder's key — must match the folder name
---
```

`key:` records the folder's key, so that nothing downstream parses one out of a directory name, and
`kind:` names this document. Neither makes this file the folder's carrier: `workflows-core:addressing`
§4 reads a folder's kind and key off the folder's carrier, found in §4's order — `brd-link.md` in a
BRD-route slice, `idea.md` or `prd.md` in an idea-route PRD folder, `epic.md` in an Epic folder —
and passes over `kind: design`, so the carrier is never this file. The filename is `design.md` and
carries no key: the folder supplies identity, the filename supplies kind.

## Header

```
# Design

- **Feature name**: <human-readable name>
- **Spec**: <specification.md path, or the Epic key it designs>
- **Classification**: SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK
- **Version**: 1
- **Created**: <YYYY-MM-DD>
- **Author**: <whoami>
- **Repos**: <the confirmed implementation repos this design spans>
- **Target**: <the Epic's `target:` component id — omit the line where the Epic carries none>
- **Open questions**: 0
```

Rules: **`Open questions` MUST be 0 to hand off.** A `design.md` is the last gate before code, so any
unresolved `- [ ]` under its `## Open questions` hard-blocks (`design-reviewer` BLOCKER; Phase 7
refuses; `/implement` refuses). This is the opposite of `specification.md`, where open questions are
tolerated. `Classification` matches the Phase 1.5 result and governs section inclusion below.

## Sections (in order)

Each section header is `## <name>`. Inclusion: **core** = always present (even `SIMPLE`); **scaled** =
present for `MODERATE`+ or whenever the change touches that concern, else a one-line `_N/A — why_`.

1. **## Context & problem** (core) — 2–5 sentences from the spec: who is affected, what the change
   delivers. Reference, don't restate, the spec.
2. **## Requirements coverage** (core) — a table/list tracing every in-scope spec item / user story
   (`[Uxx]`) / acceptance criterion (`[ACxx]`) to how this design addresses it, with a **challenge
   note** per row where the design questioned or refined the spec (`validated` / `questioned` /
   `proposed-change`). Every in-scope requirement is addressed or explicitly deferred with a reason.
   This is where the "challenge the spec" track lands in the design.
3. **## Architecture & components** (core) — the components changed/added and their responsibilities;
   a diagram or bullet decomposition. Name real modules/files where the code scan revealed them.
   Favor **deep modules** (small interface, substantial implementation — see `## Seams` for the
   depth / deletion-test / two-adapters vocabulary).
   **Record at least one rejected alternative, and why** — as a short `### Alternatives considered`
   block inside this section. This is **unconditional**: it applies to every design, whether or not the
   Phase 5 interface fan-out ran. `risk-planner` already demands the same of plans ("Name at least one
   alternative that was rejected and the reason"); a design is the weaker artifact if it does not. When
   the fan-out ran, the losing takes fill this with real trade-offs and are named as such (take,
   constraint, why it lost); otherwise the author names alternatives by hand. An "alternative" that was
   never plausible ("we considered not having an interface") is theatre — see `design-reviewer`.
4. **## Interfaces / contracts** (core) — exact signatures, API shapes, schemas, events, config keys
   the change introduces or alters. Concrete types, not prose promises. **A boundary interface** is one the change introduces or alters on the producing side, which another component (`workflows-core:components` §1: a repository, or a module inside one) or a consumer outside the system calls or receives the messages of — an endpoint, a published event, a library's public API, a command-line tool's parsed output — and never one that only code inside the same component uses. It also states, here or against it under `## Error handling & edge cases`, the behaviour a schema does not carry, as concretely as the types: what a caller gets on each failure and what state the failure leaves, its side effects, and, wherever they apply, whether a repeated request or a redelivered message repeats a side effect, ordering, and timeouts. A change that introduces one states that behaviour whole; a change that alters one states the behaviour it changes, and that the rest is unchanged. The shape of an order request does not say whether retrying it creates a second order. On a multi-component PRD (`workflows-core:components` §3), also name each interface the Epic's `## Contract` produces — its `[AD#N]`, how this design meets that row's Rule, and, where this design implements its behaviour, its producer-side test in `## Test strategy` — and each it consumes — its `[AD#N]`, and the stub or test double `## Test strategy` uses for it, or, where a contract Epic builds that interface as a code artifact (its ARD row's `Artifact`), that artifact as built, or, where the row's `Status` is `exists`, the interface as it already runs. **A consumer whose repository is not the artifact's** names how it gets the artifact: a published package pinned to a version, or a copy that records its source path and the revision it was taken at. The pin or the revision is recorded when the package is added or the copy taken, usually by `/implement`, since the artifact may not be built yet when this design is written. The copy is never edited in place: it changes only by being taken again from its source at a newer revision, which it records.
5. **## Seams** (scaled) — where the change is exercised under test; prefer the **highest** seam that
   still isolates the change. Name the seam per component. Judge seam/module quality by: **deep module**
   (a small interface over substantial implementation — prefer depth over many shallow pass-throughs);
   the **deletion test** (would removing this module concentrate complexity meaningfully, or merely
   relocate it? if only relocate, it may not earn its keep); the **two-adapters heuristic** (one
   hypothetical consumer = a *speculative* seam — do not introduce it yet; introduce a seam when a
   second real consumer exists — YAGNI for seams).
   **Classify each seam's dependency category** — it decides how the seam can be tested, and
   `## Test strategy` keys off it:
   - **in-process** — pure computation, in-memory state, no I/O. Test through the interface directly;
     no adapter needed.
   - **local-substitutable** — a real local stand-in exists (PGLite for Postgres, an in-memory
     filesystem). Test with the stand-in; the seam is internal, so no port at the external interface.
   - **remote-but-owned** — your own service across a network boundary. Define a **port** at the seam;
     an in-memory adapter for tests, HTTP/gRPC for production.
   - **true-external** — a third party you do not control. Injected port; tests supply a mock adapter.

   A category implying only one adapter is a hypothetical seam — the two-adapters heuristic above
   already says not to introduce it yet.

   **When an interface is *contested*** — any one of these — `/design` Phase 5 offers the three-take
   interface fan-out; `--design-twice` forces the fan-out itself, with no offer:
   - two or more adapters are plausible for the same seam;
   - the interface spans a process or network boundary, so its shape decides what can be tested locally;
   - three or more callers share the shape;
   - two or more candidate shapes for the same interface are already recorded in `_design-session.md` and
     none has been eliminated (count the recorded candidates — do not judge whether an argument between
     them is "discriminating"; that is the unobservable form this list exists to avoid). `/design`
     Phase 5 records each live candidate as it arises, not only the settled outcome — that is what makes
     this signal countable.
6. **## Data flow** (scaled) — how data moves through the changed path; state transitions; persistence.
7. **## Error handling & edge cases** (scaled) — failure modes, boundaries, and the defined behaviour
   for each.
8. **## Test strategy** (core) — what is tested and how (unit / integration / e2e), keyed to the seams;
   cite existing test prior art in the scanned repos.
   Key each seam's approach to the **dependency category** recorded for it in `## Seams` — a
   remote-but-owned seam tested without a port, or a true-external dependency tested without a mock
   adapter, is a mismatch `design-reviewer` flags.
   **Each boundary interface** (section 4) has a producer-side test: one that drives the real
   implementation through the interface and checks the behaviour sections 4 and 7 state for it — the
   failure cases they state included, and, for an altered interface, the behaviour the change touches.
   A consumer's tests against a stub show that the consumer handles the stated behaviour, never that
   the producer has it. A design that only builds a contract artifact — a contract Epic's OpenAPI or
   `.proto` file, entity module or generated client — implements no behaviour, so it has no
   producer-side test; its strategy checks the artifact itself: that it parses or compiles, and, where
   it changes an artifact consumers already use, that it stays compatible with the version they use.
   A stub or test double for a consumed interface models the failures its `[AD#N]` Rule or section 4
   states, as well as the success shape.
9. **## Risks & mitigations** (scaled) — engineering risks (performance, concurrency, data-loss, blast
   radius) and the mitigation or explicit acceptance for each. Each `Architecture deviation:` line (§ Architecture governance) is recorded here. A repository added to a targeted Epic's design at `/design` Phase 3, or another component of the target's own repository the design must change, is recorded here as `- Target span: <component> — <why>`: in another repository `/implement` will plan the change as a companion change, and in the same one it implements it beyond the Epic's target, and the line is what says so before it does.
10. **## Migration / rollout / backward-compatibility** (scaled) — schema/data migration, feature
    flags, rollout order, compat guarantees. `_N/A — why_` when the change is additive and
    self-contained.
11. **## Out of scope** (core) — what this design deliberately does not cover (bounds the
    implementation).
12. **## Open questions** (core; MUST be empty to hand off) — genuinely unresolved engineering items as
    `- [ ]`. Any present blocks handoff; resolve them in the grill, or push a genuinely undecidable one
    onto the `specification.md` as a spec-level `- [ ]` for the PM (the design then waits on it).

## Architecture governance

Where `/design` ran with architecture grounding ON (`workflows-core:architecture-grounding`), the design records what the architecture repository and the team's knowledge base (`workflows-core:architecture-kb`) say about its decisions:

- **Citation.** An artifact that settles or constrains a design decision — an `accepted` ADR, an `active` standard, an `accepted` team record — is cited as a markdown link whose text is its id and title, `[ADR-0012 Use one message broker](<url>)`, in the section that makes the decision, or in `### Alternatives considered` where it is why an option lost. A team record's link target is relative from `design.md` to `architecture/decisions/<id>.md`. Where the digest gives an organisation artifact no URL, the target is its path relative to the architecture repository, and `## Architecture & components` opens with `Architecture governance: <repository name> @ <short-sha> (<date>)` — or `Architecture governance: <repository name> (not a git checkout)` — so the reader knows what it resolves against.
- **Deviation.** One line under `## Risks & mitigations` for each departure: a decision that departs from an `accepted` ADR, an `active` standard or an `accepted` team record; keeping or adopting a technology in the radar's `hold` or `retire` ring; adopting a technology the radar does not list —
  `- Architecture deviation: <governing artifact as a link, or "radar: <technology> not listed"> — <what deviates> — <why> — flag: architect`
  A line about a technology the code already uses cites where it does, as a `file:line`. Like an ARD deviation (`workflows-core:ard-resolution` § Deviation-record convention), it is the architect's to adjudicate; unlike one, it is advisory: it is not an open question, it never blocks handoff, and `design-reviewer` raises no finding on it.
- **Team records.** A design never supersedes a team record — only an ARD does, through `/product-workflows:create-ard`. A departure the team should adopt for everyone is recorded as a deviation and taken there.

Where grounding was OFF, nothing in this section is required.

## Traceability & identifiers

- Every in-scope spec item and user story (`[Uxx]`) appears in **Requirements coverage** (addressed or
  explicitly deferred).
- Reference spec IDs (`[Uxx]` / `[ACxx]` / `[TCxx]`) rather than restating them; a design section that
  duplicates a `specification.md` section **verbatim** should reference it instead (both docs live in
  the same per-Epic folder).
- Where the design proposes changing an AC/TC, it does **not** rewrite the spec's IDs — it records the
  proposal in the spec's `## Engineering review` section (see the command) and references it here.

## Engineering-review edits to the specification

`/design` records spec challenges **into `specification.md`** (not only here): an `## Engineering
review` section plus new `- [ ]` open questions on the spec. When the spec is `Published: yes`,
annotate only — never mutate existing `[Uxx]` / `[ACxx]` / `[TCxx]` IDs (those route through the specs
repo's human change-management). This design doc's **Requirements coverage** cross-references those
spec edits.

## Provenance

Net-new, authored for the dev-workflows plugin — no upstream import source. The grilling technique
`/design` uses to author against this format is embedded in `commands/design.md` (adapted from
mattpocock grill-me/grilling), so `/design` has no runtime plugin dependency.

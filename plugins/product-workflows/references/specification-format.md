# Specification format (embedded authority)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

The canonical structure and per-stage rules for a product `specification.md`. `/specify` authors
against this file; `spec-reviewer` reviews against it. This is an embedded snapshot — see Provenance.

## Frontmatter

```yaml
---
kind: specification          # what this document is
key: <KEY>                   # this folder's key — must match the folder name
---
```

**Unknown frontmatter keys are preserved.** Every command that rewrites this file keeps fields it does not recognise, in place and unmodified — the same rule `workflows-core:prd-format` states for a PRD, and for the same reason: a user's own field must survive a run that did not author it. `workitem_key` is the documented example, and it is reserved rather than special-cased.

`key:` records the folder's key, so that nothing downstream parses one out of a directory name, and
`kind:` names this document. Neither makes this file the folder's carrier: `workflows-core:addressing`
§4 reads a folder's kind and key off the folder's carrier, found in §4's order — `brd-link.md` in a
BRD-route slice, `idea.md` or `prd.md` in an idea-route PRD folder, `epic.md` in an Epic folder —
and passes over `kind: specification`, so the carrier is never this file. The filename is
`specification.md` and carries no key: the folder supplies identity, the filename supplies kind.

## Header

```
# Specification

- **Feature name**: <human-readable feature name>
- **Version**: 1
- **Created**: <YYYY-MM-DD>
- **Author**: <whoami>
- **Published**: no
- **Open questions**: <N>
```

Rules: `Published` starts `no` (only a human sets `yes`). `Open questions` must equal the count of
`- [ ]` items across all "Open questions" sub-headings. Sections appear in stage order:
Problem statement → Scope → User stories (with nested Acceptance criteria → Test cases).

## Stage 1 — Problem statement

`## Problem statement` — who is affected and the problem today; why the current situation is
insufficient; why solving it matters now (business/user impact). Validation:
- Solution-free (describe the problem, not the fix).
- ≤ 1500 characters (excluding the Open questions sub-heading + items).
- No technology/implementation details.
- Infer reasonable defaults; raise genuine uncertainty as `- [ ]` under an `### Open questions`
  sub-heading (omit the sub-heading if none). Never fabricate specifics.

## Stage 2 — Scope

`## Scope` with **In scope** and **Out of scope** lists. Validation:
- In scope: ≥ 1 delivered behaviour (or `- [ ] What must this feature deliver?`); *what*, not *how*
  (no SDK classes/internal APIs/DB tables/code paths unless the problem statement requires them as
  constraints); ordered by contribution to the problem.
- Out of scope: only meaningful, confusable exclusions; ordered by confusability. Don't invent
  exclusions to fill the list.
- Coverage scan (drafting aid): configuration lifecycle; runtime lifecycle; failure states;
  paired-state transitions (every state-changing behaviour needs an inverse/recovery, an explicit
  exclusion, or an open question); cardinality; sensitive data; customer visibility.
- `### Open questions` only for unclear include/exclude boundaries; omit if none.

## Stage 3 — User stories

`## User stories`; each `### [U01]: <title>` … `### [U02]: <title>` (incrementing, contiguous),
separated by `---`, in the form `As a [role], I want [capability], so that [benefit].` Validation:
- Answers who (specific role, not "the user"/"everyone"), what (concrete capability), why
  (observable/measurable benefit), and how completion is verifiable.
- Split stories combining unrelated capabilities; merge stories too thin to verify independently.
- No implementation detail; replace vague verbs (support/manage/handle/surface) with concrete
  behaviour (displayed/stored/rejected/transmitted/recorded/changed).
- Ordered by contribution to the problem (core-value story first, then supporting, then
  lifecycle/visibility/auditability).
- `#### Open questions` per story only for assumptions/decisions needing stakeholder input; omit if none. Four hashes, not three: heading depth alone places an open-questions heading under its story or its criterion, and `###` is the story-heading level, so a three-hash heading here opens a sibling of the story and belongs to neither.

## Stage 4 — Acceptance criteria (EARS)

Under each user story, `#### [AC01]: <title>` … (AC numbering restarts at `AC01` per story,
contiguous). One EARS statement each. Order by how directly each verifies the story's core benefit
(primary outcome first, then supporting, then failure/edge, then auditability). EARS patterns
(mandatory verb `shall`):
- **Ubiquitous:** `The [system] shall [response].`
- **Event-driven:** `When [preconditions] [trigger], the [system] shall [response].`
- **State-driven:** `While [state], the [system] shall [response].` (`During` = synonym.)
- **Optional feature:** `Where [feature is included], the [system] shall [response].` (build/licence
  optionality only — NOT user preferences, which are `While`.)
- **Unwanted behaviour:** `If [preconditions] [unwanted condition], then the [system] shall [response].`
- **Compound:** combine two of the above; use sparingly.
Validation:
- Uses `shall`; `[system]` names a specific component (not "the system"); `[response]` is measurable
  with a concrete verb.
- Display criteria (status/details/errors/summaries) name the exact fields shown (e.g. outcome,
  timestamp, failure message, acting user, identifier, change type).
- No implementation *how*; split any criterion with `and` between two verbs; `While` for runtime
  state, `Where` for static/data conditions.
- An exact-message criterion for one fault states its scope — *with no other fault present* — or the
  order the faults are checked in, so a test can tell which message wins when two apply.
- A loading, empty or waiting state states how a bounded wait ends it (the result arriving, a timeout
  and what it shows); a control's state (disabled, hidden, read-only) states its inverse — when it is
  enabled, shown or editable again.
- AC-level `##### Open questions` under the criterion; story-level `#### Open questions` after the last AC.

## Stage 5 — Test cases

Under each AC, `##### Test cases` with `**[TC01]: <title> — <Category>:**` (TC numbering restarts at
`TC01` per AC, contiguous). Category ∈ `Happy path` / `Negative / boundary` / `State / lifecycle` /
`Security / privacy` / `Audit / observability`, chosen by what the expected result verifies (not by
position). Each test: **Preconditions**, **Steps** (numbered), **Expected result** (single pass/fail
outcome asserting the *parent* AC's behaviour, reusing the AC's exact terms). Validation:
- ≥ 1 happy-path AND ≥ 1 negative/boundary per AC; add state/lifecycle, security/privacy,
  audit/observability where the criterion warrants.
- Self-contained (own preconditions/data; never depends on another test's outcome).
- Asserts only what its parent AC states: an expected result that checks a behaviour the criterion
  does not name needs that behaviour added to the criterion (or a criterion of its own) first.
- Ordered within an AC by criticality (primary success first).
- Open questions: `- *Open questions:* [q]` on a test, or an `Open questions` sub-heading for broader
  items.

Each field takes this literal micro-format — match it exactly, so every test case reads the same
field by field to `spec-reviewer`, to `/design` and `/implement`, which trace each `[TCxx]`, and to a
person scanning the spec:

```
**[TC01]: <title> — Happy path:**
- *Preconditions:* <state>
- *Steps:* 1. <action> 2. <action>
- *Expected result:* <single pass/fail outcome asserting the parent AC>
```

## Identifier conventions

`[Uxx]` unique+contiguous document-wide; `[ACxx]` unique+contiguous within each story; `[TCxx]`
unique+contiguous within each AC. After `Published: yes`, IDs are contracts — never silently
change/remove; changes are traced via the specs repo's change-management (human-run).

**Renumbering a large specification.** Where a fix cycle has to renumber a whole story's ACs or TCs —
a story split, or criteria reordered before the spec is published — rewrite that story as one section,
renumbering it top to bottom, rather than patching IDs one by one across a long file, then re-run the
structural pre-lint's ID checks (`/specify` Phase 5.5) over the whole file. Never renumber an ID a
published specification carries.

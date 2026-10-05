# Release-note destinations & shapes — source of truth

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

Consulted by `release-notes-writer` to decide **where a release note lands and what shape it must
take**. This file is the single authority for the section map, the per-section draft shape,
the per-section prose rules, the deprecation-note rule, the effective-version rule (§6), and Change
Type sourcing. The `/release-notes` command cites this file for its own invariants (§1/§3 for the
draft shape, §4 for the documentation-link rule, §6 for the effective version) but never re-derives
the writer's decision; the agent applies it and returns a proposed destination plus any gaps.

The Change Type is a **field on the PRD, inferred where the PRD does not carry a routable one, and confirmed where that inference is uncertain** (§7). It is never written into the draft
and never collected as a field — the agent resolves it only to pick the destination and the shape.

## 1. The section map

**The three destinations are three sections of one `release-notes.md` in the PRD folder**, and the
Change Type selects a **section** exactly as it selected a file before. The taxonomy is unchanged —
breaking change / feature update / fix is universal, and every rule below about shape, prose and
deprecation applies to a section exactly as it applied to a file. Only *where a draft lands* changed.

**The release version is the heading those three sit under**, because in one file nothing else says
which release a section belongs to — and it sits **one level above them**, `# <version>`, since
each section is `## …` and each titled draft opens with its own `### <feature title>` (§3). Those
three levels are the file's whole outline, and they are what `/release-notes` Phase 8 appends by: a
version's part of the file runs from its `#` heading to the next `#` heading, and a section runs from
its `##` heading to the next `##` or `#` heading, so a draft appended at the end of its section, or a
section at the end of its version's part, never lands inside the next. A version at the sections'
own level would end at the first section, and a section at the drafts' title level at the first
draft. A run whose version the operator declined files under `# Unreleased`. The file's title,
`# Release notes — <PRD> <slug>`, is its first line, names the PRD folder's key and slug — on a run
addressed to an Epic as on one addressed to the PRD — and names no version.

**Each draft records its scope and what its run read, in one HTML comment directly above it:**

```
<!-- release-note scope: ACME-77-01 2026-09-20
read: orders-service 3f9a1c2b4e5d 7be0d41c9a2f
read: billing-api 1c2d3e4f5a6b
-->
```

The first line names `<KEY>` — the PRD folder's key on a run addressed to the PRD and the Epic's on
one addressed to an Epic — and the date the run appended the draft. Each `read:` line names a
repository, by the `repo:` name the implementation records use or, for one only the scan reached, the
slug the run resolved it by, and then **every commit the run read there**: each block's `commit:`
whose diff it read, each commit its scan kept whose diff it read, and each commit a key-commit
fallback drew on. **The qualifier is on both of the first two, not only the first** — neither the blocks nor the scan
opens a diff, the one reading a record and the other commit *messages*, so both hand a commit over
on the strength of having found it and neither on the strength of having read it, and a run that
wrote out what it had merely found would advance the boundary past work no note describes. (The
scan does run inside a clone, and so does the `git rev-parse` that resolves a block's abbreviated
`commit:` for this comparison — running there is not reading a diff.) **A
commit is written as the first 12 characters of its full SHA**, as `git log --format=%H` prints it —
never a shorter or a longer prefix — which is long enough that two commits of one repository do not
share it in practice and short enough to keep the comment readable; every comparison against a read
set takes the same 12 characters of a SHA resolved in that repository, a block's abbreviated
`commit:` resolved with `git rev-parse` first. **The comparison is on the SHA alone, and the
repository name is a label for whoever reads the file.** One repository can be named two ways across
two notes — a block's `repo:` in one, the slug the scan resolved in the other — and matching on the
pair would then miss a drop the earlier note had earned; a SHA is a content hash, so twelve
characters of one no more repeat across the handful of repositories a PRD touches than within one.
Group the `read:` lines by repository for readability, never to scope a lookup. A commit the run
could not resolve was not read and is not written, so a later run reads it again. A run that read no
commit — diff grounding off, or nothing resolved — writes the one line `read: none`, and its note
covers no commit.

The file is one per PRD and a note may be drafted for one Epic, so without the comment nothing in the
file says whose work a note described or what it saw, and the comment is what `/release-notes` takes
its boundary from, for the blocks it reads and the commits its scan keeps alike: a PRD's note covers
every implementation record under the PRD and an Epic's that Epic's record alone, and a note covers
exactly the commits its `read:` lines name (`workflows-core:implementation-format` §4). An HTML
comment renders as nothing and is not a heading, so it moves none of the boundaries above, and it is
**not part of the draft**: every rule below binds the draft beneath it, and the operator's paste
starts there. **A note that records no read set falls back to its date**, which `implementation-format`
§4 bounds and says what it loses: a comment of the one-line form
`<!-- release-note scope: <KEY> <YYYY-MM-DD> -->`, the shape this release replaced before it
shipped, and a draft with no scope line at all, which is every one appended before `docs-workflows`
1.2.2. A draft with no scope line counts as the PRD's, which is how
the file's one boundary treated it then, and is dated by the file's last write before a scope line
first reached it: the latest commit to the file whose version carries none, or, where the file
carries no scope line yet, its own last-written date, as before.


The Change Type selects the **section** of that one file:

| Change Type | Section | Draft shape |
|---|---|---|
| `Breaking change` | `## Breaking changes` | plain **Category:** label + `### title` + prose |
| `New technology support` | `## Feature updates` | plain **Category:** label + `### title` + prose |
| `Bug fix` | `## Fixes` | one or two self-contained sentences — **no label, no title** |
| `not applicable` | — | not routable: inferred as for an absent value (§7), and the draft lands in the section the inference picks |

**The three-file model this replaced is gone, not merely renamed.** Drafts once landed in generated
snippet files under `<space>/_snippets/release-notes/<product>/<sprint>/`, written into a docs repo by
an automation this plugin no longer talks to; a curated `spotlight.md` sat beside them and was never a
destination this command could choose. Nothing here writes into a docs repo any more, so a draft's
destination is a heading in `release-notes.md` and nothing else. The taxonomy is untouched.

## 2. Classification order

Determine the destination by the nature of the change, not by how the source frames it. Take the
first match, in this order:

1. **Breaking change** — the change forces customers to act to avoid disruption.
2. **Bug fix** — the change is a completed correction restoring intended behavior.
3. **New technology support** — anything else that adds or enhances a capability. **For a PRD this
   is the overwhelmingly common case**; do not reach for `Bug fix` because a PRD
   mentions fixing something.

Tie-breakers:
- A change that both improves something and forces customer action → **Breaking change**.
- A change that both corrects expected behavior and is delivered automatically → **Bug fix**.
- **A change that deprecates anything is NEVER a `Bug fix`.** A deprecation forces customers to act
  before its end-of-life date, so it is never a completed correction. It classifies as `Breaking
  change` when the customer must act now, else `New technology support` when a new capability
  supersedes the old one. **A deprecation therefore never routes to `fixes`** — which is what leaves
  the §5 deprecation note room to live in a titled Summary.

Emit the classification with a confidence signal. When confidence is low (the source supports two
destinations roughly equally), record a `gaps[]` entry (`field: change_type`,
`recommended_action: "ask user"`) carrying the proposed value. The command confirms it by
**consequence** — the shape and the section it lands under — never by presenting the bare enum labels.

## 3. Draft shape per section

The **Summary** is the customer-facing body the PM publishes wherever release notes are published — the
thing this file's rules shape. There is exactly one per run (§6). Its structure depends on the
destination:

### `## Feature updates` and `## Breaking changes`

Render exactly:

```markdown
**Category:** <category_label>

### <feature title>

<prose>
```

Omit the category label entirely when the PRD carries no `release_notes_category` (§7).

### `## Fixes`

Render **one self-contained sentence**, or two when the conditions or the resolution need a second —
no category label, no `###` title, and no key (the automation appends the key when it publishes). A
shipped entry looks like:

```markdown
Fixed an issue where the **GET account audits** endpoint of the Account Management API would return a `500` error instead of a `504` error in case of a timeout.
```

## 4. Prose rules per section

### Titled sections (`## Feature updates`, `## Breaking changes`)
- **Title** — what changed, or the value it brings, in sentence case; no leading "New feature:", no
  trailing period. Aim for **80 characters or fewer**: the command reports the count and never
  blocks on it.
- **First paragraph** — about two sentences, roughly 35 words: what changed and why it matters (a
  breaking note's "Starting with …" clause, where §6 calls for one, comes on top).
- **A second paragraph does exactly one job** — compatibility (what the change works with or
  requires), scope (who or what it applies to, and what it excludes), or a required action. In a
  breaking note the Action plan is that paragraph. Never "how it works" detail, and never a list of
  every place the feature appears; that is the documentation's job.

### Breaking change
- **Present tense.** State plainly what is breaking — the reader is scanning for impact, so do not
  bury it behind a benefit statement.
- **Say when it takes effect where the heading does not** (§6) — a later release, or the end-of-life
  date of a far-off deprecation.
- **The Action plan.** Directions or a link to remediate, in their own paragraph that opens with the
  literal bold label `**Action plan:**`. **Every breaking note carries one**: §2 defines a breaking
  change as one that forces the customer to act, so a breaking note with nothing to do contradicts
  its own section, and a fixed label is what a reader scanning the section looks for. Never invent the
  remediation: when the source states none, the paragraph is `**Action plan:**
  <!-- TODO: action plan -->` and the writer records a `field: prose` gap.
- Voice: write "you"/"your"; start with verbs.
- **An upcoming change is announced the same way.** A note that warns of a break in a later release
  is still a breaking note: it names that later release (or date) and what to do before then.

### Feature update
- Lead with **customer value**, present tense; mention a previous limitation only as a subordinate
  clause or a later sentence.
- **Link to documentation only on a dev-phase run.** `/release-notes` runs twice in a PRD's life, and
  the two runs have different link realities:
  - **PM phase** — no `specification.md` and no `design.md` under the PRD's specs dir. The feature is
    not built and the documentation does not exist yet. **Omit the link entirely**; do not ask for one.
  - **Dev phase** — either file is present (the same signal
    `workflows-core:cost-emission` §7 uses to infer `phase`/`role`). The author
    can supply a redirect short link that will later point at the page `/document` publishes.
  **Never invent a URL** at either phase.
- Editorial hierarchy — lead with the new or recommended path; demote a deprecated, legacy, or
  manual-only option to a trailing sentence or a `> Note:` line, never an equal peer.
- Enumeration or comparison → a short intro sentence + a bulleted list, **bolding** each option's name.
- **Bold** UI element / screen / field names; inline `code` for filenames, identifiers, flags, and
  config keys.
- State the concrete benefit, not hedged prose.

### Fixes
- **Past tense**, one sentence (two at most): symptom + resolution. **Open with a past-tense verb**
  — "Fixed", "Resolved", "Changed", "Removed", "Updated" — never an article or inline code, so every
  entry in the section reads at a glance as a completed correction.
- Include the conditions necessary for the problem to occur when they fit the sentence (what action,
  what environment, what input).
- **No hedging** (`could`, `sometimes`, `might`) — except when describing a potential security
  exposure, which must not be stated as fact.
- **No internal jargon, variable names, or code references.** Customer-facing API details (endpoints,
  status codes, response shapes) are fine.
- **No internal workflow terms** — never `ported from`, `merged from`, or `backported`.

## 5. Deprecation note (orthogonal to the destination)

A deprecating change is never a `Bug fix` (§2's third tie-breaker), so it always lands in a **titled**
destination and the note always has room. Which titled destination is independent: a
`New technology support` note can announce that a new capability deprecates an old one, and a
`Breaking change` may itself be a deprecation.

**Trigger** — one or more of:
- The PRD deprecates a capability, or a new capability supersedes/deprecates an old one.
- The whole PRD is a deprecation.

**Not a trigger: a deprecation this change does not make.** "Deprecat*" wording is where to look,
not the test. A deprecation the PRD puts out of scope (an out-of-scope list, a non-goal), leaves to
later or other work, or mentions only as background — one announced earlier, or another product's —
gives this note none.

**When triggered**, the Summary carries a **deprecation note** — a trailing `> Note:` line or a short
labeled sentence — stating:
- what is deprecated,
- the **end-of-life date** — **required**,
- the **end-of-support date** — optional.

**Dates** — never invent them. Derive a date from the source only when the source states it. If a
required end-of-life date is not available, record a `gaps[]` entry (`field: deprecation_eol`,
`recommended_action: "ask user"`) and place a `<!-- TODO: end-of-life date -->` placeholder in the
draft prose. Format dates per the prose-style (e.g. `November 30, 2026`).

Not every PRD deprecates something. Raise this only on the trigger above, and ask only for what the PRD
does not already state.

## 6. General rules (all destinations)

- **Exactly one Summary.** Emit **one** Summary for the note — never one block per declared
  release version.
- **A release version only where the heading cannot say it.** The version is the `#` heading the
  draft is filed under (§1). **Feature updates and fixes name no release version**, and a breaking
  change that takes effect in the release it is filed under names none either: never "Starting with
  version 1.305…", "in 344", etc. for that release. A breaking note that takes effect in a **later**
  release must say when, because its heading names the release that announces the break, not the
  one that makes it: it opens `Starting with <release>, …`, the release written as the PRD names it
  (`version 3.0`). The exception is a deprecation far enough out that only its date is known (for
  example, the end of 2028): its end-of-life date (§5) says when, and the note names no version.
  **Never invent a version, and never take it from the heading.**

  **For a breaking note, where it comes from — first match wins:**
  1. **The PRD's body names the release the change takes effect in, and it is later than the release
     the note is filed under** → that release. Under `# Unreleased`, the release that ships the
     change is not yet known, so this rung fires only where the PRD itself says the named release
     comes after the one that ships the change. Compare releases as versions, not as strings
     (`1.24.0` is `version 1.24`), and never read the PRD's `release_versions` frontmatter, which
     `/release-notes` does not read (`workflows-core:prd-format`).
  2. **The break is itself a deprecation, and the PRD names no release** → its end-of-life date (§5)
     says when; no release. While that date is unknown, the draft carries rung 3's placeholder and
     gap as well, marked as one the end-of-life answer settles: a supplied date removes both, an
     answer that leaves the end-of-life marker leaves this marker too, unasked — the open date is the
     real question — and an answer that the change is no deprecation after all leaves the gap to be
     asked.
  3. **The PRD says the break comes in a later release and names none** — including a break beside a
     deprecation the note also announces → a `Starting with <!-- TODO: effective version -->, …`
     placeholder and a `field: effective_version` gap.
  4. Anything else — the change takes effect in the release the note is filed under, or, under
     `# Unreleased`, in whichever release ships it → no clause.
- **Another component's versions are fine in any note** when the source states them — "agent
  versions 1.241 and earlier".
- **The Change Type never appears as text in the draft.** It selects the destination and the shape;
  the PM sets the field on the PRD.
- **Link text names its target.** "Learn more", "here", "this page" and "click here" fail; write
  "For details, see [Configure log ingestion](…)".
- **No internal names.** Never a codename, a feature-flag name, an internal component, service or team
  name, or a person's name — the customer sees none of them. Name the product and UI terms instead.
- **No marketing superlatives** — "seamless", "powerful", "revolutionary", "best-in-class". State the
  concrete benefit.
- Translate the technical change into customer-value language (product and UI terms).
- Assert only what the source supports; preserve the facts the source supports.
- These rules complement, and do not duplicate, the prose-style checks run in the command's
  style-gate phase.

## 7. Sourcing the Change Type and the category label

**Change Type — two rungs:**

1. **Authored PRD frontmatter** — `change_type`, where the PRD carries one. Authoritative: when
   present, no confirmation prompt fires.

   Two values are **not routable** and fall through to rung 2 (§2 inference): `not applicable`
   (§1 maps it to no section, and nothing stops such a run — `/release-notes` has no gate that reads
   the field — so it is inferred like an absent value and a note is drafted), and `Bug fix` on a
   change that trips §5's deprecation trigger (§2's third tie-breaker bars a deprecation from
   `fixes`, and §5's required end-of-life note has nowhere to live there).
2. **Infer** — classify per §2, then, where the inference is low-confidence, **confirm it with the
   operator by shape and destination, never by enum label**. This was the fallback rung and is now
   the ordinary one: nothing supplies the field from outside, so most runs reach it.

**The category label — one rung.** It is your organization's product/solution taxonomy (e.g. `Platform`,
`Application Observability | Distributed Tracing`, `Infrastructure Observability | Kubernetes`) and it
is exactly the PRD's `release_notes_category`:

1. **Authored PRD frontmatter** — `release_notes_category`, where the PRD carries one. Use it
   verbatim as the label.

**Absent, the draft carries no category label**: the line is omitted, and the label is never
inferred, guessed or asked for — a taxonomy term is the organization's, and one the operator has not
chosen is one this plugin would be inventing. A draft without the line is complete; a note that
should carry one gets it from `release_notes_category` added to the PRD.

**Both used to be dropdowns set outside the plugin and returned by an import**, which is why the
Change Type ladder's first rung was authoritative and its second was a fallback. Nothing returns them now,
so the PRD is the only place either can be authored (see `workflows-core:prd-format`).

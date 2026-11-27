# Structural pre-lint (embedded — shared reference)

Deterministic, grep-expressible structural checks the reviewer-gated commands run against a
just-authored artifact **before** dispatching their Opus reviewer — so an Opus review pass is not
consumed BLOCKing on mechanical structure. **Advisory:** surface findings, inline-fix the mechanical
ones, leave content gaps for the author, then proceed to the reviewer. Pre-lint **never hard-stops**
on its own; the reviewer remains the gate.

Each caller cites this file, states its **artifact type** and the **file(s)** to check, runs three
things — the **Universal checks**, then the **key-collision** check when the artifact is a PRD, an
ARD, a threat model or an Epic file, then its **artifact-specific block** — and surfaces the findings. Severities: **BLOCKER**
(missing required section, duplicate ID, stray generic placeholder), **MAJOR** (a structural rule
broken), **MINOR** (ID gap, informational count). Inline-fix only the mechanical (renumber a duplicate
ID this run introduced, never one the artifact already carried; delete a stray placeholder token); anything needing content goes back to the author/grill.

## Universal checks (every artifact)

1. **Placeholder scan** — `grep -nE "\b(TBD|TODO|FIXME|XXX)\b|<[a-z][a-z0-9 _./,'()-]*>" <file>`. Any hit →
   BLOCKER (a shipped artifact carries no placeholder). Does NOT flag `[NEEDS CLARIFICATION]` or
   `- [ ]` open questions — those are counted per-artifact below. The class takes an apostrophe, a
   comma and parentheses because a placeholder written as a phrase — `<the service's dev port>`,
   `<value, e.g. 30>`, `<port (dev)>` — is still one: without them, one reached three Epics of a live
   run. **Do not widen it to "anything up to `>`".** That was measured on a live specs tree and caught
   `<the ISBN>` in an API template — `?isbn=<the ISBN>`, the notation an ARD's Rule and an Epic's
   criteria use for a request's parameter — which this pattern leaves alone, its class holding no
   capital letter; the absent `:` keeps a markdown autolink (`<https://…>`) out as well.
   **Inside code, the `<…>` half reads only what code cannot be.** Code is literal by the author's
   own markup — `<fieldset>`, `EventEmitter<number>`, a `<b>` fixture, a design's decision written as
   a code block — so: a `<…>` hit inside a **fenced block** is discarded; one inside an **inline code
   span** is discarded where its content is a single token (`<fieldset>`, `<n>`) and kept where it
   holds a space — `` `<path or glob>` `` is a template slot left unfilled, the shape `design-format`'s
   own *Pieces* template writes, and markup or a generic type never holds one. **`TBD`, `TODO`,
   `FIXME` and `XXX` are flagged everywhere**, code included: a `// TODO` in a design's code block is
   work left undone. Without the fenced-block exclusion a block that *is* the decision could never
   reach zero BLOCKERs. **A display format with a variable part** — a count in a label, a parameter
   in a URL — goes in inline code with a one-token slot (`` `(<n> ratings)` ``) or names the variable
   in words ("the rating count in parentheses"); bare in prose, it reads as a placeholder and is
   flagged.
2. **Identifier integrity** — for each ID series the artifact uses (below), the numbers form a
   contiguous run from the scheme's base with no duplicates. A duplicate → BLOCKER; a gap → MINOR.
3. **Required-section presence** — every mandatory heading listed for the artifact is present
   (`grep -nF '## <heading>' <file>`). A missing required heading → BLOCKER.

## Auto-link collision (PRD, ARD, threat-model and Epic files only)

An artifact whose body is pasted into a tracker must contain no token that tracker will auto-link. The pattern below matches the two-segment issue-key shape every common tracker links on; **it is an auto-link detector, not a key validator**, and its narrowness is exactly what makes it correct. Run:

    grep -nE '\b[A-Z]{2,10}-[0-9]+\b' <file>

For the PRD, run against the body **below the frontmatter** — `/create-prd` pastes only that, and the
frontmatter's `key:` / `ref:` / `seeded_from_prd:` / `revision_of:` legitimately carry keys.
For the ARD and the threat model, scan **below the frontmatter**. For Epic files, scan **below the frontmatter** as well —
`epic-writer` writes `kind:`, `key:` and `target:` there, and `key:` legitimately carries the Epic's
key; scanning the whole file reported that line on every Epic of a live run.

Discard a hit ONLY when it is a deliberate tracker reference: inside a wikilink (`[[KEY-123]]`), inside
a markdown link (link text or URL), or inside a fenced code block. Inline code (`` `KEY-123` ``) is NOT excluded and IS flagged.
Classify every surviving hit into exactly one of four branches, and name the branch in the finding — the taxonomy is not exhaustive by assumption, so a hit that fits none of the first three belongs in the fourth:

1. **A requirement ID** (`US`/`AC`/`SM`/`SMC`/`UC`/`FR`/`AD`/`TH` prefix) → **BLOCKER**; convert it to `[PREFIX#N]`. Mechanical, so inline-fix it under the standard pre-lint contract.
2. **A specs-tree key** → **BLOCKER**. Extend the hit over every `-<digits>` segment that follows it — the grep matches only two segments, so on `ACME-90-01` it reports `ACME-90` — and resolve that whole key with `workflows-core:addressing`'s `resolve-key` (resolution against the tree, never a pattern). `found` puts it in this branch; `absent` sends it on to branch 3 or 4; `ambiguous`, and `misnamed` — a folder named outside `workflows-core:addressing` §2's class, which it reads nothing of — are each reported with the hit and never stop the run, since pre-lint never hard-stops. A key in this branch is wrapped as `[[KEY]]`, the whole key, the specs tree's own traceability form (`workflows-core:doc-structure-conventions` §1). Mechanical — the resolution is the confirmation — so inline-fix it. Where the hit sits in inline code, which a wikilink cannot enter, take the key out of the span and write the wikilink beside it.
3. **A real tracker ticket** (a key in a project that actually exists, and resolving to no specs folder) → **BLOCKER**; wrap it as `[[KEY-123]]` so a tracker and a wiki-style importer both read it as the deliberate reference it is. Not mechanical — confirm the key with the author before wrapping.
4. **None of these — a standards, protocol, or algorithm reference** such as `ISO-8601`, `RFC-8446`, `TLS-13`, `SHA-256`, or `HTTP-2` → **MINOR**; leave the token **exactly as written** and report it. It is correct prose that happens to match the grep, so there is nothing in the artifact to fix. NEVER rewrite it as `[PREFIX#N]` and NEVER wrap it in a wikilink — `[[ISO-8601]]` is a dangling link to a ticket that does not exist, and the inline-fix clauses of branches 1 and 2 do not reach this branch. If a tracker project genuinely shares the prefix, that is the author's call to make, never the linter's.

The ARD is not itself pasted anywhere, but `epic-writer` copies its `AD` references into Epic
drafts, which are. Catching it at the source is cheaper than catching it downstream.
The threat model is not pasted anywhere either. It is checked because it can name another folder's key — on an Epic-level model, an inherited decision's or threat's — which the specs tree writes as a `[[KEY]]` link, and because its own ids keep the `[TH#N]` form.

## PRD — `prd.md` (`/create-prd`; format `prd-format.md`)

- Required headings: `## Problem`, `## Goal`, `## Target audience`, `## User Stories`,
  `## Acceptance Criteria`, `## Scope`, `## Success Metrics`.
- ID series: `[US#N]` (in `### [US#N]:` headings), `[AC#N]`, `[SM#N]` — each contiguous from 1, superseded and withdrawn ids counted (`prd-format.md` § Changing a requirement). An id counts where it is defined — its `### [US#N]:` heading, or the id that opens its own line or list item — and one cited anywhere else (a `Superseded by` marker, an FR's *Implements:*, a cross-reference) is a reference, never a duplicate. A mechanical fix renumbers only a duplicate this run introduced, never an id the PRD already carried. **A story id repeated as a `### [US#N]:` heading under `## Acceptance Criteria` is the usual duplicate**, and renumbering is the wrong fix for it: name the fix in the finding — group that story's criteria under a `**For [US#N] — <title>**` label line (`prd-format.md` § Spine) — and, where this run wrote the heading, make it inline.
  Plus `[SMC#N]` (counter-metrics), `[UC#N]`, `[FR#N]` when those adapt-in clusters are present.
- Report the count of `[NEEDS CLARIFICATION]` (a relentless-grilled PRD should converge to 0; >0 → MINOR).

## ARD — `ard.md` (`/create-ard`; format `ard-format.md`)

- Required headings: `## Context`, `## Grounding findings (architecture as-is)`,
  `## Architecture decisions`, `## Cross-repo / component approach`, `## Stack & invariants`,
  `## Edge cases & risks`, `## Open questions`, `## Deferred`.
- ID series: `[AD#N]` (in `### [AD#N]:` headings) — contiguous, no dupes.
- Each `### [AD#N]` block carries all three sub-fields `**Binds:**`, `**Prevents:**`, `**Rule:**`
  (a missing one → MAJOR), and a live one `**Alternatives:**` too (missing → MAJOR, or MINOR on a
  decision the run's `prior_ard` copy already held without it).
- A `**Superseded by:**` line names an `[AD#M]` that exists in the same ARD and is neither superseded
  nor withdrawn; a `**Withdrawn:**` line carries a reason.
- **Contracts — only when the frontmatter `components:` has two or more `kind: code` entries** (an entry's `kind` defaults to `code`) (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §5). `## Contracts` is then a required heading (missing → BLOCKER), with `### Schema ownership`, `### Versioning and compatibility` and `### Landing order` under it (a missing one → MAJOR). Every interface-table row's `AD` cell names an `[AD#N]` that has a `### [AD#N]` heading (else BLOCKER); every `Producer` and `Consumers` value is an `id` in `components:` (else MAJOR); every `Status` is `new`, `changed` or `exists` (else MAJOR). With fewer than two code entries `## Contracts` is not required, and its absence is not reported.

## Threat model — `threat-model.md` (`/create-ard`; format `${CLAUDE_PLUGIN_ROOT}/references/threat-model-format.md`)

- Frontmatter `kind: threat-model` (else MAJOR).
- Required headings: `## Scope`, `## Not considered`, `## Threats`.
- ID series: `[TH#N]` (in `### [TH#N]:` headings) — contiguous from 1, no duplicates, superseded and withdrawn threats counted. An id counts where its `### [TH#N]:` heading defines it; one cited anywhere else — a `**Superseded by:**` line, an `## Inherited threats` bullet, another folder's `[[KEY]] [TH#N]` — is a reference, never a duplicate.
- Each `### [TH#N]` block carries `- **Where:**`, `- **Threat:**` and `- **Disposition:**` (a missing one → MAJOR). Its Threat line holds `attacker:`, `action:` and `asset:` (a missing one → MAJOR). Its `- **Category:**`, where it is not `—`, is one of `S`, `T`, `R`, `I`, `D`, `E` (else MINOR).
- A live block — one carrying neither `**Superseded by:**` nor `**Withdrawn:**`, each counted only as its own list item at the start of a line (`- **Superseded by:**`, `- **Withdrawn:**`) and never where it is written inline inside another field's text — has a Disposition opening `Mitigated by `, `Deferred to design: ` or `Accepted — ` (else MAJOR). An `Accepted — ` Disposition matches `review by [0-9]{4}-[0-9]{2}-[0-9]{2}` and holds a non-empty owner and a non-empty reason ahead of it, `; `-separated as the format writes them (else MAJOR).
- On a live block, each decision pair — every `, `-separated element after `Mitigated by `, up to any `; the rest deferred to design: `, and the pair after the Where's `; contract ` — matches `^(\[\[[^]]+\]\] )?ard(-[^ ]*)?\.md \[AD#[0-9]+\]$`, and its ARD file, where it is not `ard.md`, is, whole, in `workflows-core:addressing` §2's class of a folder's name — the class `workflows-core:ard-resolution` holds an area file's name to — tested as that section tests one: checked as text for a `'`, then handed, as one single-quoted argument, to its `python3 -I -c` program, in the class only where it exits 0 (else MAJOR): a pair names the ARD file that holds its decision, so `Mitigated by [AD#2]` is MAJOR, and an area file in letters of any script is named as `ard-resolution` reads it.
- A `**Superseded by:**` line names a `[TH#M]`, other than its own threat's id, that has a `### [TH#M]:` heading in the same file (else MAJOR). Where the line is new — the run holds no prior copy of the model, or the prior copy's same `[TH#N]` block does not carry it — that `[TH#M]` is also live (else MAJOR). An older line may name a threat since superseded or withdrawn in turn: the format never rewrites it, and a reader follows the chain. A `**Withdrawn:**` line carries a reason (else MAJOR).
- A `### [TH#N]` heading under `## Inherited threats` → MAJOR: an inherited threat is written as a bullet, so that neither this model's `[TH#N]` series nor its lineage items count it.
- Where the run holds a prior copy of the model — `/create-ard`'s `threat_model.prior`, where it is not `none` — every `[TH#N]` with a `### [TH#N]:` heading there still has one here (else MAJOR): a threat is never renumbered or deleted, and the reviewer BLOCKs the same defect.
- Of this block's findings, inline-fix only a duplicate `[TH#N]` this run introduced, under the opening's inline-fix contract; every other finding of this block goes back to the author.

## spec — `specification.md` (`/specify` and `/update-spec`; format `specification-format.md`)

- Required headings: `## Problem statement`, `## Scope`, `## User stories`; header fields
  `- **Published**:` and `- **Open questions**:`.
- ID series: `[Uxx]` (in `### [Uxx]:`) contiguous document-wide; `[ACxx]` (in `#### [ACxx]:`)
  contiguous within each story; `[TCxx]` (in `**[TCxx]:`) contiguous within each AC — a superseded or
  withdrawn item counted, since it keeps its number (`specification-format.md` § Identifier
  conventions). A heading line ending in ` — Superseded by …` or ` — Withdrawn …` in any other form
  than that section's two → MAJOR, naming the line.
- **Open-questions header consistency:** the integer in `- **Open questions**: N` must equal the
  count of `- [ ]` items in the file (`grep -cE '^[[:space:]]*- \[ \]' <file>`). Mismatch → MAJOR.
- **Per-criterion test coverage:** under each live `#### [ACxx]:` — one whose heading, and whose
  story's, carries neither marker — its live `**[TCxx]: <title> — <Category>:**`
  lines carry at least one `Happy path` and at least one `Negative / boundary` category
  (`specification-format.md` Stage 5). An `[ACxx]` missing either → MAJOR, naming the story, the
  criterion and the category it lacks. Read the category after the last ` — ` of the line, as the
  format writes it; a criterion with no test case at all lacks both.

## Epic — per-Epic file (`/epics`; template in `product-workflows:epic-writer`, NOT a `*-format.md` doc)

- Required headings per Epic file: `## Goal`, `## Business value`, `## Scope`, `### In scope`,
  `### Out of scope`, `## Acceptance criteria`, `## Independent Test`, `## Dependencies`, `## Covers`,
  `## Suggested stories`, `## References`.
- Acceptance criteria are Given/When/Then bullets (`grep -nE '^- Given .*, when .*, then ' <file>`;
  a `## Acceptance criteria` section with zero G/W/T bullets → MAJOR).
- `[NEEDS CLARIFICATION]` count ≤ 3 per Epic (epic-writer cap; >3 → MAJOR).
- `## Covers` references parent-PRD IDs in bracketed form — any series `prd-format.md` § Changing a
  requirement lists (`[US#N]`, `[AC#N]`, `[SM#N]`, `[SMC#N]`, `[UC#N]`, `[FR#N]`), and, where `/epics`
  folded in a PRD-level specification, its `[Uxx]` and `[Uxx/ACxx]` ids; Epics do not mint their own
  criterion IDs.
- A `_coverage.md` file is present in the output dir.
- Refined Epic files (from `/epics` refinement mode — `EPIC-<EPIC-KEY>-<eslug>/epic.md`, the keyed
  folder and keyless filename `epic-writer` writes; never `<EPIC-KEY>.md`, which that agent forbids)
  carry a `## Scope` with real in/out bullets (not just the summary).

## design — `design.md` (`/design`; format `design-format.md`)

- Required (core) headings: `## Context & problem`, `## Requirements coverage`,
  `## Architecture & components`, `## Interfaces / contracts`, `## Test strategy`, `## Out of scope`,
  `## Open questions`; header field `- **Open questions**:`.
- Scaled sections `## Seams`, `## Data flow`, `## Error handling & edge cases`, `## Risks & mitigations`,
  `## Migration / rollout / backward-compatibility`, `## Observability & release verification` are
  present for MODERATE+ **or** replaced by a
  one-line `_N/A — <why>_`; a MODERATE+ design missing `## Seams` with no `_N/A_` → MAJOR.
- Report the `- [ ]` count under `## Open questions` (design-format requires 0 to hand off — the
  design-reviewer enforces the hard block; pre-lint only reports it).
- **Unscoped `kubectl` operational command** — a rollout, a rollback step or a runbook that restarts,
  deletes or scales every workload of a kind in a namespace, where it meant one:

      grep -nE 'kubectl( +(-n|--namespace)( +|=)[^ `|;&]+)* +(rollout +restart|delete|scale)( +[a-z][a-z.]*)?( +(-n|--namespace)( +|=)[^ `|;&]+| +(--all|--all-namespaces|-A)| +--replicas=[0-9]+)* *($|[`|;&#\\])' <file>

  A hit is a command that names at most a resource kind and otherwise only a namespace, `--all` or a
  replica count — no resource name, no `-l`/`--selector`, no `-f`. Each → **MAJOR**, advisory: quote
  the line and ask the author to name the resource or a selector. Unlike the placeholder scan, this
  one reads code blocks too, where such a command is usually written; a namespace flag before the
  verb, a trailing `#` comment and a `\` line continuation are matched, and a command split across
  lines with its resource on the next line is not — read those by hand. Never inline-fixed: which
  resource was meant is the author's to say. A `kubectl get` or any other read-only verb is outside
  the pattern.
- **`## Threat review` (`design-format.md` section 15) — only where the draft holds a line `## Threat review` outside any fenced block.** The section runs from that line to the next `## ` heading outside a fenced block, or the end of the file; an entry runs from its `### [DT#` heading to the next `### ` or `## ` heading. Each finding of this group is MAJOR, save a missing Disposition and a dash-form id, which are BLOCKER; the numbering's are universal check 2's.
  - The section holds a `- **Models read:**` line.
  - ID series: `[DT#N]`, in `### [DT#N]` headings, each counted with or without its colon — contiguous from `[DT#1]`, withdrawn entries counted. It joins the series universal check 2 (*Identifier integrity*) reads, which finds a repeated or a missing number at that check's own severity. An id counts where its `### [DT#N]` heading defines it, its colon aside; one cited anywhere else — a `- **Withdrawn:** superseded by [DT#M]` line, another folder's `[[KEY]] design.md [DT#N]` — is a reference, never a duplicate. Every `### [DT#` heading carries the colon after its `]`.
  - Each entry holds `- **Answers:**`, `- **Where:**`, `- **Threat:**`, `- **CWE:**`, `- **Disposition:**` and `- **Test:**`, each once and in that order, each a list item at the start of a line. A missing Disposition → BLOCKER.
  - The Answers value, the text after `- **Answers:** `, matches `^(\[\[[^]]+\]\] \[TH#[0-9]+\]|—)$`.
  - The Disposition value, the text after `- **Disposition:** `, matches one of `^Mitigated — Rule: \S`, `^Not this design's — (answered in \[\[[^]]+\]\] design\.md$|the interface it attacks is not built by this design: \S|does not arise: \S)` and `^Returned to the architect — \S`.
  - On a live entry — one with no `- **Withdrawn:**` list item at the start of a line — whose Disposition opens `Mitigated — Rule: `, the Test value is not `—`.
  - The section holds no `- [ ]` line.
  - An entry id written with a dash in place of its `#`, bracketed or bare, anywhere in the draft → BLOCKER.

  A design never enters the *Auto-link collision* check, whose scope is PRD, ARD, threat-model and Epic files, so `DT` is not among that check's requirement-ID prefixes.
- **Bound `[DT#N]` entries — wherever the caller hands a prior design's path whose `## Threat review` holds a `### [DT#N]` heading, whether or not the draft holds a `## Threat review` section.** Each file's `## Threat review` is found outside any fenced block, as the group's trigger finds it. Every `[DT#N]` with a `### [DT#N]` heading in that file's `## Threat review`, its colon aside, still heads an entry in the draft's `## Threat review` (else BLOCKER, one per missing id): a bound entry is never renumbered or deleted, so a draft whose section is gone has deleted every one.

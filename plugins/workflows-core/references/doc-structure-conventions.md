# Doc structure conventions (shared)

Single source of truth for how a written page is **structured** and what it may **contain**,
independent of any single docs repo. This reference is repo-agnostic: it governs the shape of prose,
callouts, and reusable components for whatever docs repo `/document` or `/docs-write` writes into. Consumed by `/document`, `/docs-write` and `/epics`, and by `doc-planner`, `doc-writer`, and `doc-reviewer`. Repo-specific
conventions — frontmatter fields, changelog format, terminology lists, component syntax — live under
the `docs-workflows` plugin's `references/docs-profiles/`, not here.

Consumed by `doc-writer`, `doc-planner`, and `doc-reviewer` — `doc-writer` and `doc-reviewer` for `/docs-write` too.

---

## 1. The traceability boundary

**The rendered page carries no source provenance.** keys, PR URLs, and `<!-- KEY: … -->` HTML
comments belong in the commit message and in the run's handoff — never in body prose, never in a
changelog entry, never as a comment in the markdown.

**Scope: rendered product-docs pages** — the pages `/document` and `/docs-write` write into a docs repo. This section
does not govern **specs-tree documents**, such as the `epic.md` files `/epics` writes,
where a `[[KEY]]` wikilink is the native idiom and the required traceability form. It resolves
nowhere — the specs tree is a git repository, not a vault — and does not need to: it names a key,
not a page.

| Where | Carries |
|---|---|
| Rendered page | The customer-facing claim only. |
| Commit message | The key and the summary (`profile.commit_convention`); a backlog run's commit names its unit's id instead, which is no key. |
| Run handoff / final report | Per-claim attribution to resolved keys and to the refs `diff-summarizer` named. |

A changelog entry is reader-visible "what changed on this page" prose, so it is covered by the rule
above: a key never belongs in it. `docs-workflows:doc-writer`, `docs-workflows:doc-planner`, and `/docs-workflows:document`
each state that instance; this section is their authority — they are instances of this rule, not
competing ones.

**One exception.** `${CLAUDE_PLUGIN_ROOT}/references/source-truth.md` §7.6 defines an
`<!-- intentional-discrepancy: … -->` HTML comment that IS written into the rendered page, and its
text does cite a key. It is a user-decided gap flag, not provenance, and `doc-reviewer`'s
Source-code accuracy dimension checks for it. Do not remove this marker as a stray provenance
comment; see `${CLAUDE_PLUGIN_ROOT}/references/source-truth.md` §7.6 for its exact format.

**Outside the rule, because none is provenance:** the evidence contract's frontmatter keys `unit:` and `evidence:`, which a backlog run writes and `/docs-workflows:docs-audit --refresh` reads (`docs-workflows:docs-audit/evidence-contract` §2, `docs-workflows:docs-audit/backlog-format` §3), a walkthrough's image-slot comment `<!-- docs-image-slot: <slot> -->`, and the visibility marker `<!-- docs-visibility: internal -->` (`docs-workflows:docs-workflow/visibility` §5).

## 2. Callout scope and adjacency

A callout that qualifies one member of a set is placed **with that member**, never as an
**unqualified** trailing block after the set (rule 3 below is the one permitted alternative):

1. **With-the-member placement.** When a step or section presents mutually exclusive options, each
   option owns its callouts, placed immediately beneath it.
2. **Whole-set callouts in the lead-in.** A callout that applies to the whole set goes in the lead-in,
   **before** the options — never after them, where position alone reads as "and finally, this
   applies to everything above".
3. **Explicit scope naming.** Where placement alone could still mislead — including the case where a
   callout genuinely must stay adjacent to the whole set — the callout names its own scope in its
   first clause, for example *"This applies only to the Private Container Registry option."* A
   trailing callout that opens this way satisfies this section; it is a compliant alternative to
   rule 1, not a tolerated violation, and enforcers must not flag it.

**Worked example.** Illustrative only — the syntax below (`{{#callout}}`) is one repo's component; the
rule does not require it. A four-option list presents ways to configure a registry — a built-in
*cluster* registry, a customer-owned private registry, and two public registries. A callout describing
an ARM (multi-architecture image) limitation specific to the built-in cluster registry is placed after
all four options, as a single trailing block. Positioned there, it reads as a constraint on all four
options, including the customer-owned private registry — where it is false, since the customer
controls that registry's contents and can hold multi-arch images. The fix is not rewording; it is
placement — move the callout under the one option it actually describes, or, if it must stay adjacent
to the set, open it with *"This applies only to the built-in cluster registry."*

**Reviewer severity: MAJOR.** A callout whose position admits a broader reading than intended changes
what the customer believes is required or prohibited — a correctness failure, not a stylistic one. A
callout that names its own scope per rule 3 **and stays adjacent to the set it qualifies** admits no
broader reading, so it is not this finding. Rule 3 licenses that placement and no other: scope naming
cures ambiguous adjacency, not absent adjacency, so a scope-labelled callout parked away from its set
— several sections later, or beneath an unrelated option — is still this finding.

## 3. Component-pattern fidelity

Before writing a content shape that recurs across a docs area — mutually exclusive options,
collapsible detail, tabular reference, and so on — sample the surrounding content area and reuse the
dominant component for a matching shape. Never invent an ad-hoc structure where a sibling pattern
already exists for that shape.

The evidence takes this block shape:

```yaml
component_patterns:
  - shape: mutually-exclusive-options
    component: "{{#tabgroup}} / {{#tab title='…'}}"
    evidence: "guides/container-registries/use-public-registry.md:176"
    count: 4
```

`{{#tabgroup}}` above is a worked example from one docs repo's own component syntax, shown only to
illustrate the block shape — it is not a required or default component.

`shape` is an **open vocabulary**, not a closed enum: the planner names what it observes in the
sampled pages. The shapes named above are seed examples, not the permitted set.

**No component list is vendored.** This rule carries no catalog of components to choose from for any
repo, including an example-docs one: the evidence comes from the sampled sibling pages of whatever
repo is in front of the run, never from a reference table shipped anywhere in the plugin family. A repo's own authoring
guidance may separately document that a component exists; which shape it is idiomatic for is still
read off the sibling pages.

**Reviewer severity: MINOR.** A divergence from an established sibling pattern still renders — this is
a consistency and scannability finding, not a correctness one.

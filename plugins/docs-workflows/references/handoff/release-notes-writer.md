# release-notes-writer Handoff Format

## Input

```yaml
folder_read: <the YAML the orchestrator assembled by reading the PRD folder — the resolved folder, or the one above it where the address named an Epic folder — the PRD frontmatter and body, the Epic set, and the artifacts present, the render input scoped to that Epic's folder where the dispatch says so; the orchestrator names its keys in the dispatch, since no schema file defines them>
diff_summaries:      <optional array of diff-summarizer outputs; one entry per repo; omit when diff-grounding is off>
code_repos:          <optional array of {slug, path}; provided when diff-grounding is on — enables the code half of the writer's Source-truth check (8b); the acceptance-criteria half (8a) runs without it>
change_type:            <change_type from the resolved PRD's frontmatter; null otherwise — nothing returns it from outside, so a value that is absent or not routable is inferred, and confirmed in the command's own grill where the inference is low-confidence>
release_notes_category: <release_notes_category from the resolved PRD's frontmatter; null otherwise — used verbatim as the category label>
run_phase:                       <"pm" | "dev" — inferred by the command from whether specification.md / design.md exist under the PRD's specs dir; gates the release-note-types.md §4 documentation-link rule only>
model_routing:
  classification: MODERATE
  reason: <from orchestrator>
  current_model: <model name>
  planning_model: n/a
  review_model: n/a
  implementation_model: <model name>
  opus_available: true | false
  gate_tests_on_review: false
docs_grounding:      <optional docs-grounder digest (docs_references + docs_challenges); omit when docs grounding was OFF/EMPTY>
```

Refuse to run without `folder_read`. Emit exactly one Summary per run.

## Output

```yaml
status: OK | PARTIAL

release_notes_block:
  target_format: example-docs-release-notes-v1
  change_type:  <one of: "Breaking change" | "New technology support" | "Bug fix">   # selects the destination + shape; NEVER rendered as text
  destination:  <one of: "## Breaking changes" | "## Feature updates" | "## Fixes">  # a section of release-notes.md, per release-note-types.md §1
  category_label: <the PRD's release_notes_category verbatim, e.g. "Platform | Settings"; null when the PRD carries none — the label line is then omitted>
  feature_title: <5–10 word headline; sentence case; no leading "New feature:"; no trailing period. null for the fixes destination.>
  prose: |
    <shaped customer-facing body; no work-item IDs; no PR links; no release version. For the titled
    destinations: a 2–4 sentence paragraph, or a short intro sentence + a bulleted list when the
    feature enumerates discrete options. For the fixes destination: ONE self-contained past-tense
    sentence. See release-note-types.md §3 (shape) and §4 (prose rules).>
  combined_rendered: |
    <the exact text the PM publishes wherever release notes are published. For a titled destination:
    "**Category:** <category_label>", a blank line, "### <feature_title>", a blank line,
    then <prose> — with the category label omitted entirely when category_label is null. For the
    fixes destination: <prose> alone. NEVER a "Change type:" line, a "Release-notes category:" line,
    or a "--- Summary ---" divider.>

gaps:
  - field:              <feature_title | prose | change_type | deprecation_eol>
    kind:               <acceptance-criteria | source-truth; required for discrepancies from step 8, omitted for other gaps>
    reason:             <why this is low-confidence or missing. For change_type: the destination was inferred and the source supports two destinations roughly equally; the proposed value is still set on release_notes_block. For deprecation_eol: a deprecation was detected but the required end-of-life date is not derivable from the source.>
    recommended_action: "ask user" | "mark TODO in draft" | "note in report"
    draft_phrasing:     <only for kind: acceptance-criteria — the draft's contradictory wording, verbatim>
    criteria_phrasing:  <only for kind: acceptance-criteria — the acceptance criterion, verbatim>
    criteria_location:  <only for kind: acceptance-criteria — the supplied artifact and criterion identifier or heading>
    prd_phrasing:       <only for kind: source-truth — intended wording supported by the PRD, never a draft error flagged by step 8a>
    source_phrasing:    <only for kind: source-truth — what the source code actually shows>
    source_location:    <only for kind: source-truth — file:line the source_phrasing was verified against>
```

The two discrepancy kinds have disjoint evidence fields. An `acceptance-criteria` gap needs no code evidence and never requests an implementation-gap report. A `source-truth` gap requires verified code evidence; where both kinds concern the same claim, its `prd_phrasing` uses the cited criterion rather than the contradictory draft.

`status: PARTIAL` when at least one gap has `recommended_action: "ask user"`.

## Status codes

| Status    | Meaning                                                              |
|-----------|---------------------------------------------------------------------|
| `OK`      | Draft rendered; the Summary has its prose and, when the PRD supplied one, its category label.|
| `PARTIAL` | Draft rendered but at least one gap needs the user (low-confidence destination, missing end-of-life date, or an unverifiable claim). |

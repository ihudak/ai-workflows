# Source-Code Truth (Shared Policy)

This document is the **single source of truth** for one of the most important
rules in the `dev-workflows` plugin family:

> **Verify against the implementation; escalate every discrepancy to the user.**
> The source code is what customers will use. PRDs, design specs,
> and prose descriptions are the *starting point*, not the *spec* — they may
> be outdated, aspirational, simplified, or wrong. Every user-visible claim in
> generated documentation MUST be verified against the implementation, and
> every disagreement between the description and the source MUST be surfaced
> to the user for an explicit decision. **The plugin is the analyst; the user
> is the decision-maker.** The plugin never silently picks a winner.

Every sub-agent that synthesises documentation (`doc-planner`, `doc-writer`,
`doc-reviewer`, `release-notes-writer`) MUST apply this principle.

---

## 1. The principle

Customers do not read your PRDs. They read the docs, click the UI,
hit the API. So the docs must reflect what shipped — but the *what shipped*
question is sometimes a product-management question, not a code-truth question.

When a PRD says "user picks Latest / Previous / specific version" and
the source code shows four presets (Latest / Previous / **Older** / specific),
that's a discrepancy. The plugin **doesn't** automatically pick one side;
it presents the discrepancy and asks the user. The user has context the plugin
doesn't (PM intent, sprint planning, agreed scope, customer expectations).

**When a spec is provided, the spec markdown is the authoritative "intended"
source.** Some runs (notably `/document`) pass an implementation spec — the
resolved folder's `specification.md` and `design.md`, and each `EPIC-*/`
subfolder's `epic.md`, `specification.md` and `design.md`, whichever exist.
When that spec is present, *it* defines the
intended behaviour: it is the agreed, current contract for what should ship.
The PRD (`prd.md`) then **corroborates** the spec (it is the older customer-narrative
phrasing) and the source code remains the **"actual"** — what shipped. So the
comparison becomes three-way: the spec says what was *intended*, the PRD echoes
it (and may have drifted), and the code shows what is *actual*. When no spec
is provided, behaviour is unchanged: the PRD is the "intended" starting point and
the comparison is the original two-way (PRD vs. code).

The authoritative file set, when a spec is provided:

- **Authoritative ("intended"):** `specification.md` and `design.md` at
  either level — the PRD folder's own and each `EPIC-*/` subfolder's — and
  each Epic's `epic.md`.
- **Corroborating:** the PRD, `prd.md` — the narrative the three-way
  comparison checks the spec against, never part of the spec itself.
- **Ignore:** `idea.md` and `prompt.md` (pre-spec brainstorming) and any
  rendered HTML mirrors of the above.

The user might decide:

- **"Document as intended (spec)"** — describe the agreed contract. When a
  spec is present this is the spec phrasing; when it is absent it is the PRD
  phrasing. Often the right call: the spec is the current agreement and the
  code can be brought into line.
- **"Document as actual (code)"** — the implementation is the spec in practice;
  update the spec or the PRD separately. Often the right call: the implementer found
  extra value or the intended phrasing was simplified for stakeholder
  consumption.
- **"Skip this claim and report"** — neither side is wrong, but the discrepancy
  is too subtle to ship docs around; flag it for the team and leave the
  paragraph out for now.

The plugin's job is to **detect the discrepancy and present the analysis** in
the form of a table:

| # | Claim | PRD | Spec | Code | Source location | Verdict |

with one row per discrepancy and three per-row choices (when no spec was
provided, the **Spec** column reads `(no spec)` and the comparison is the
original two-way). See §7 for the escalation protocol.

If the description and the code AGREE, the docs still cite the verified
source so they do not silently drift when a future ticket revision diverges
from what shipped.

## 2. What MUST be verified

The **"intended"** phrasing for every claim is taken from the **spec markdown
when a spec is provided**, falling back to the PRD's description when no spec is
present. When a spec is present, the authoritative file set is
`specification.md` and `design.md` at either level (the PRD folder's and each
`EPIC-*/` subfolder's) and each Epic's `epic.md`; `prd.md` is the PRD, the
corroborating side; and `idea.md`, `prompt.md`, and any rendered HTML mirrors
are ignored. The
**"actual"** phrasing is always taken from the source code.

For every documentation page, snippet, or release-notes entry produced by a
command of a plugin that depends on this one — `/document` and
`/release-notes` today — verify the following classes of user-visible claim
against the source code:

| Claim type | Where to verify in code |
|---|---|
| **Enum / dropdown options** (e.g. "Latest / Previous / Older stable") | Settings schema JSON (`*.schema.json` under `settings-schemas/`), data source classes (`*DataSource.java`), Java/TypeScript `enum` declarations, OpenAPI schema `enum:` fields |
| **UI labels and button text** (e.g. "Add update window", "Update now to target version") | `displayName:` / `label:` / `title:` constants in schema JSON, `i18n` / `.properties` resource bundles, React/Angular templates, `addItemButton:` metadata in schema files |
| **Menu paths** (e.g. "Settings > Deployment > Gateway updates") | UI route definitions, navigation manifests, `schemaGroups:` in schema files, `meta:` blocks |
| **Default values** | Schema `default:` fields, constant declarations (`DEFAULT_*`, `final static …`), `uiDefaultValue:` metadata |
| **Feature flags / maturity gates** | `featureFlag:` metadata in schemas, `@FeatureFlag` annotations, FF config files |
| **API endpoint paths, params, response shapes** | OpenAPI specs in the source repo, REST controller / resource implementations, request/response DTOs |
| **Field nullability / validation rules** | Schema `nullable:`, `minObjects:`, `precondition:` blocks; validator classes; `@Nonnull` annotations |
| **Concurrency / scope rules** ("one AG per group, one per zone") | Algorithm implementations, throttle/lock classes, scope filter expressions |
| **Permission / role gates** | Access-rule classes (`*AccessRule.java`), `@RequiresPermission` annotations, IAM scope declarations |
| **Headline counts** ("3 options", "4 modes", "supports X variants") | Always derived from the enumeration in the source; never copied from the description |
| **Commands, CLI invocations, and copy-paste code blocks** (helm/kubectl/pnpm invocations, flags, image references, chart names, registry paths, YAML keys inside fenced blocks) | Chart and manifest files in the source repo (`Chart.yaml`, `values.yaml`, `templates/**`), the CI/release workflow that publishes the artifact, sibling docs pages that already carry the same command, and `--help` / usage strings in the CLI source |
| **Lifecycle dates and milestones** (end-of-life, end-of-support, shutdown, sunset, availability dates) | UI notice strings and banner constants, announcement/config expiry values, feature-flag sunset metadata, sibling announcement pages that already carry the date |

**Lifecycle dates compare by milestone, not by surface form.** "EOY 2027",
"end of 2027", "December 31, 2027", and "stops working on January 1, 2028"
all denote one boundary and are **not** a discrepancy. A discrepancy exists
only when the milestones genuinely differ — for example "EOL by mid-2027"
against "stops working on January 1, 2028". Dates have more semantically
equivalent phrasings than any other claim type; a verifier that compares
strings floods Phase 5.8 with non-discrepancies and trains users to dismiss
the table.

## 3. How to verify (techniques)

Sub-agents performing verification SHOULD use these techniques in order of
specificity:

### 3.0 Spec markdown (the "intended" baseline, when a spec is provided)

When the run provides a spec, read the spec tree to establish the
authoritative **intended** phrasing for each claim before verifying it against
code. Read `specification.md` and `design.md` at either level — the PRD
folder's and each `EPIC-*/` subfolder's — and each Epic's `epic.md`; read
`prd.md` as the PRD, the corroborating side, not as spec; ignore `idea.md`,
`prompt.md`, and any rendered HTML mirrors.

```bash
grep -rn "<claim-keyword>" <spec_dir> \
  --include="*.md" 2>/dev/null \
  | grep -E "/(specification|design|epic)\.md:"
```

This is the source of the `spec_phrasing` field (§4.2). When no spec is
provided, there is no spec-markdown technique to run and `spec_phrasing` is
recorded as `(no spec)`.

### 3.1 Settings schema JSON (highest signal)

```bash
find <repo_path> -name "*.schema.json" 2>/dev/null \
  | xargs grep -l "<schema-id-or-keyword>" 2>/dev/null
```

Then read the file. Schema JSON declares the canonical enums, defaults,
validators, and UI labels. If the doc topic touches a Settings 2.0 feature,
this is the most reliable source.

### 3.2 Data source / option provider classes

When schema fields are dynamically populated (e.g. `subType: "datasource"`
in the schema), the runtime options come from a Java/TypeScript class
referenced by the schema's `datasource.identifier`:

```bash
grep -rn "DATA_SOURCE_ID = \"<identifier>\"" <repo_path> --include="*.java"
```

Read the class to find the actual option values and their display names.

### 3.3 Constant declarations

```bash
grep -rn "public static final String <NAME>\|const <NAME> =" <repo_path>
```

### 3.4 OpenAPI specs

```bash
find <repo_path> -name "openapi*.yaml" -o -name "openapi*.json" 2>/dev/null
```

For REST endpoint documentation, the OpenAPI spec is authoritative for
paths, params, request/response shapes, and enum values.

### 3.5 UI source

For button labels, menu items, and React/Angular templates:

```bash
grep -rn "<exact-string-the-doc-uses>" <repo_path>/ui --include="*.ts" --include="*.tsx" --include="*.html"
```

### 3.6 Tests as a fallback

If neither schema nor code yields the answer, test files often encode the
shipped behaviour:

```bash
grep -rn "<feature-name>" <repo_path> --include="*Test.java" --include="*.spec.ts"
```

### 3.7 Commands and fenced code blocks

A reader runs a documented command verbatim, so a wrong flag or a wrong registry path is a
customer-facing defect with no recovery. Verify every command the docs introduce or change:

```bash
# the artifact's own definition
find <repo_path> \( -name Chart.yaml -o -name values.yaml \) 2>/dev/null

# the published name/path, as the release pipeline writes it
grep -rn "<chart-or-image-name>" <repo_path>/.github/workflows <repo_path>/.ci 2>/dev/null

# what the docs already say elsewhere — sibling pages are strong corroboration
grep -rn "<command-head>" <docs_repo_path> --include="*.md" 2>/dev/null
```

A command that no source confirms is `NOT_FOUND`, not "probably fine". Record it as a
`verification_warning` like any other claim and let the caller escalate it.

## 4. Sub-agent responsibilities

### 4.1 High-signal claim types (use case A)

Enum changes, new schema files, new constants, and renamed labels are
high-signal evidence for downstream verification. The consulting agent
(doc-planner, §4.2) verifies these the same way as every other
user-visible claim — by reading shipped source directly with the §3
techniques, not by relying on a PR summary to have surfaced them.

### 4.2 `doc-planner` (use case A)

The orchestrator passes `code_repos:` as an input — a list of
`{slug, path}` records pointing to the local clones used by the
diff-summarizer. When a spec is provided, the orchestrator also passes the
spec directory. The claim's **intended** phrasing comes from the **spec when
present, falling back to the PRD when absent.** doc-planner MUST:

1. Extract every user-visible claim from the proposed checklist (option
   names, button labels, default values, counts, menu paths, mode names,
   schema field names, UI flow steps).
2. When a spec is provided, run the **`spec-markdown`** technique (§3.0)
   against the spec tree to capture the intended phrasing for each claim.
3. For each claim, run the appropriate technique from §3 against the
   `code_repos` to verify the claim.
4. For each claim, emit a `verification_warnings` entry with one of these
   findings (added v1.8.0 — finer-grained than v1.7.0):
   - **`VERIFIED`** — source agrees with the claim. (Recommend omitting from
     the list to reduce noise; OR include with a single line for audit.)
   - **`CONTRADICTED`** — source has a different value/label/count. Record
     the `prd_phrasing`, the `spec_phrasing`, AND the `source_phrasing`
     verbatim. Do NOT pick a winner.
   - **`NOT_FOUND`** — the PRD or spec mentioned a behavior/UI element that has
     zero trace in the source. Implementation-gap candidate. Record the
     intended phrasing and the locations checked.
   - **`AMBIGUOUS`** — multiple plausible source matches with different
     phrasing; verification can't pick one.
   In every case record `spec_phrasing` verbatim alongside `prd_phrasing`
   and `source_phrasing`. **When no spec was provided, record
   `spec_phrasing: "(no spec)"`** — behaviour is then unchanged (intended =
   the PRD, two-way comparison).
5. **Do NOT rewrite the topic notes to match the source** (v1.8.0 change).
   Leave the claim as the intended phrasing had it; the orchestrator will
   prompt the user per discrepancy at Phase 5.8 (impl-prd) and the user
   decides whether to document as intended (spec), document as actual (code),
   or skip.

### 4.3 `doc-reviewer` (use case A)

The orchestrator also passes `code_repos:` to the reviewer. The reviewer
runs the **Source-code accuracy** dimension: spot-check 3–5 user-visible
claims per file against the source using §3 techniques. **Severity rule
(updated v1.8.0):** a documented claim that does NOT appear in the source
is a **BLOCKER** UNLESS the doc contains an explicit intentional-discrepancy
marker explaining the gap. See §7 for the marker format.

**Note on `release-notes-writer`:** This agent applies the same source-truth verification to the specific option/label/count claims its draft makes (when `code_repos` is provided), and on every run checks its conditional and quantitative claims against the acceptance criteria it was handed. Its `gaps[]` separates `kind: acceptance-criteria` (draft versus cited criterion, an authoring discrepancy) from `kind: source-truth` (PRD-supported intent versus verified code). The release-notes command resolves the criteria kind first without an implementation-gap report; only a separate source-truth gap with code evidence reaches this reference's intended-versus-actual decision flow.

## 5. Hard rules

- NEVER copy a PRD's option list, count, label, or default
  value into the docs without running source verification on it.
- NEVER trust a PRD's "User Story" section as the spec — it is
  the customer-narrative phrasing, often simplified.
- NEVER trust a PRD's date — descriptions are often months old
  and may pre-date the actual implementation.
- **NEVER silently pick a winner** when source and description disagree
  (changed in v1.8.0). The plugin is the analyst; the user is the
  decision-maker. See §7 for the escalation protocol.
- When source verification is impossible (no code repos provided, source
  not yet implemented, generated code), surface that as a
  `verification_warning` with `finding: NOT_FOUND` and
  `technique: "no-source-evidence"` — never silently emit unverified
  user-visible claims.
- Reviewer severity rule: a customer-visible option / label / count
  that does not appear in the source is **BLOCKER**, not CONCERN —
  unless an intentional-discrepancy marker is present (§7).
- Bug-report draft destination is the same PRD folder used for
  the release-notes draft (auto-discovered by the orchestrator at
  the resolved PRD folder). File name:
  `<KEY>-implementation-gaps.md`. Same hard rule as for release-notes:
  **NEVER `/tmp/`** — container restarts wipe it.

## 6. Example (drawn from a real run)

The PRD's "User Story" said:

> A specific stable version available on the cluster (e.g., `1.327`).
> [implied 3 presets: Latest / Previous / specific]

Source — `cluster-repo/shared/core.platform.autoupdate/src/main/java/com/example/core/platform/autoupdate/agent/settings/datasource/PrivateAgentAutoUpdateDataSource.java` lines 35–38:

```java
public static final String LATEST_VALUE = "latest";
public static final String PREVIOUS_VALUE = "previous";
public static final String OLDER_VALUE = "older";

private static final int ENTRY_LIMIT = 3; // only latest, previous and older can be selected
```

The source shipped **4 options** (Latest / Previous / **Older** / specific
main version). The PRD's "User Story" missed "Older".

- v1.6.0 shipped the 3-option PRD phrasing — caught only in a manual
  review round.
- v1.7.0 added source verification but defaulted to silently picking the
  source side.
- v1.8.0 surfaces the discrepancy as a §7 table and asks the user.

The §7 table for this discrepancy (with the added **Spec** column) reads:
`| 1 | Target version preset list | "Latest, Previous, specific" | "Latest, Previous, Older, specific" | "Latest, Previous, Older, specific" | …/PrivateAgentAutoUpdateDataSource.java:35 | CONTRADICTED |`
— here a spec was provided and its phrasing matched the code, so the PRD
narrative is the side that drifted; with no spec the **Spec** cell would read
`(no spec)`.

A complementary example from the same PRD, also caught by manual review:
the PRD's "UI changes" section described renaming `Settings > Updates` to
`Settings > Deployment`. The source (`ClusterSettingsMenu.java:1404`)
still has `.withTitle("Updates")` — zero hits for any "Deployment" rename
anywhere in the cluster repo. v1.7.0 would have rewritten the doc to say
"Settings > Updates"; v1.8.0 instead presents the discrepancy and lets the
user decide whether to document the *shipped* path or document the *promised*
path and file a bug against the implementation team for the missing rename.

---

## 7. Discrepancy escalation protocol (added v1.8.0)

When `doc-planner` (or any sub-agent doing source verification) emits one
or more `verification_warnings` with finding `CONTRADICTED`, `NOT_FOUND`,
or `AMBIGUOUS`, the orchestrator MUST follow this protocol before
proceeding to Phase 6.3 (writing).

The protocol is **three-way** when a spec was provided — it compares the
**PRD** narrative, the **Spec** (authoritative "intended"), and the **Code**
("actual"). When no spec was provided it stays two-way in effect: the **Spec**
cell reads `(no spec)` and the run behaves exactly as the original PRD-vs-code
protocol.

### 7.1 Present the analysis table

Build a single ask_user prompt showing every discrepancy in a table:

```
| # | Claim                      | PRD                                        | Spec                                | Code                                | Source location                                 | Verdict      |
|---|----------------------------|--------------------------------------------|-------------------------------------|-------------------------------------|-------------------------------------------------|--------------|
| 1 | Target version preset list | "Latest stable, Previous stable, specific" | "Latest, Previous, Older, specific" | "Latest, Previous, Older, specific" | …/PrivateAgentAutoUpdateDataSource.java:35 | CONTRADICTED |
| 2 | Menu rename                | "Settings > Updates → Settings > Deployment" | "Settings > Updates"              | "Settings > Updates" (unchanged)    | …/ClusterSettingsMenu.java:1404                 | NOT_FOUND    |
| 3 | Deferral window default    | "deferred until window closes"             | "deferred to next window"           | "deferred to next window"           | …/UpdateWindowSettings.java:88                  | SPEC-VS-PRD |
```

The **Verdict** column carries the §4.2 finding (`CONTRADICTED`, `NOT_FOUND`,
`AMBIGUOUS`) and one additional verdict: **`SPEC-VS-PRD`** — the spec differs
from the PRD narrative (regardless of whether code matches the spec). The
spec is authoritative, so a `SPEC-VS-PRD` row is surfaced to flag that the
PRD should be updated to match the spec; the recommended action for it
is "Document as intended (spec)". When no spec was provided the **Spec** cell
reads `(no spec)` and `SPEC-VS-PRD` cannot occur.

This table is informational — display it before asking decisions.

### 7.2 Ask the user how to proceed (batch first)

```
ask_user(
  question: "<N> discrepancies between the intended phrasing (spec when present, else the PRD) and the source code were found (see table above). How would you like to handle them?",
  choices: [
    "Decide per discrepancy (Recommended)",
    "Document as intended (spec) for ALL",
    "Document as actual (code) for ALL",
    "Skip & report for ALL (drafts a bug report; no claims documented)"]
)
```

(When no spec was provided, "Document as intended (spec)" uses the PRD
phrasing — the original two-way behaviour.)

### 7.3 Per-discrepancy decision (if user chose "Decide per discrepancy")

For each discrepancy in turn:

```
ask_user(
  question: "Discrepancy #<n>: <claim>\n  - PRD: <prd_phrasing>\n  - Spec: <spec_phrasing>\n  - Code: <source_phrasing>\n  - Source location: <file:line>\n\nHow would you like to handle this one?",
  choices: [
    "Document as intended (spec) (Recommended) — describe the agreed contract (spec phrasing; PRD phrasing when no spec); the orchestrator drafts a bug-report so you can file a defect when the code lags",
    "Document as actual (code) — match what shipped; users see what's there",
    "Skip & report — the docs leave this paragraph out; the bug-report draft still records the gap (drafts a bug)",
    "Cancel the whole run"]
)
```

(When no spec was provided, "Document as intended (spec)" uses the PRD
phrasing.)

### 7.4 Record decisions

Maintain a `discrepancy_decisions` record keyed by discrepancy number. Each
entry records the intended phrasing from the spec (`spec_phrasing`, `(no spec)`
when none was provided) alongside the PRD and source phrasing. The `decision`
field is one of `document-as-spec`, `document-as-code`, or `skip-and-report`:

```yaml
discrepancy_decisions:
  - number:           1
    claim:            "Target version preset list"
    prd_phrasing:    "Latest stable, Previous stable, specific"
    spec_phrasing:    "Latest, Previous, Older, specific"
    source_phrasing:  "Latest, Previous, Older, specific"
    source_location:  ".../PrivateAgentAutoUpdateDataSource.java:35"
    decision:         "document-as-spec"
    rationale:        <user-provided text if "Other...">
  - number:           2
    claim:            "Menu rename"
    prd_phrasing:    "Settings > Updates → Settings > Deployment"
    spec_phrasing:    "(no spec)"
    source_phrasing:  "Settings > Updates (unchanged)"
    source_location:  ".../ClusterSettingsMenu.java:1404"
    decision:         "skip-and-report"
    rationale:        <user text>
```

Pass this record to Phase 6.3 (writer). The writer:

- For `document-as-spec` decisions: use the intended phrasing verbatim in the
  docs — the `spec_phrasing` when a spec was provided, the `prd_phrasing`
  when it was `(no spec)`. When the code lags the intended phrasing, also
  insert an intentional-discrepancy marker (see §7.6) at the start of the
  enclosing section.
- For `document-as-code` decisions: use the source phrasing verbatim in the
  docs.
- For `skip-and-report` decisions: omit the claim from the docs entirely.

### 7.5 Emit the bug-report draft

When `discrepancy_decisions` contains ANY entry with decision
`document-as-spec` (where the code lags the intended phrasing),
`skip-and-report`, or `document-as-code` **where the PRD phrasing asserts a
specific value that contradicts the source**, the writer MUST emit a
Markdown file alongside the release-notes draft in the resolved PRD folder. Skip a `document-as-code` entry whose PRD phrasing is vague
or non-committal — "several registries" against a source with four is loose,
not wrong. When the two readings are arguable, emit: the output is a draft
the user reviews, so a spurious entry costs a paragraph while a miss leaves
a wrong customer-facing claim in the ticket indefinitely.

```
<PRD-folder>/<KEY>-implementation-gaps.md
```

Format:

```markdown
# <KEY> — Implementation gaps found during documentation

Generated <YYYY-MM-DD>. File these as defects against the implementation
team (or amend the PRD if the gap is intentional).

## Gap <n>: <claim>

- **PRD phrasing**: <prd_phrasing>
- **Spec phrasing**: <spec_phrasing>   (`(no spec)` when none was provided)
- **Source state**: <source_phrasing>
- **Source location**: <file:line>
- **User decision in docs**: <decision>
- **Docs status**: <"described as intended (spec), awaiting implementation"
                    | "omitted from docs"
                    | "documented as shipped; the source ticket carries an
                    incorrect claim">
- **Suggested action**: <for a `document-as-spec` / `skip-and-report` gap:
                    raise a defect with the team that owns
                    <source_location>'s component, with a link to
                    <KEY> and a link to this gap analysis
                    | for a `document-as-code` gap: correct the source
                    ticket — the implementation is right — rather than
                    filing a defect against the implementation team>
```

The bug-report draft uses the same hard-rule for destination as the
release-notes draft (the PRD folder, never `/tmp/`, never inside the docs repo).

### 7.6 Intentional-discrepancy marker format (for the writer)

For `document-as-spec` decisions where the code lags the intended phrasing,
the writer inserts this marker immediately before the affected prose:

```markdown
<!-- intentional-discrepancy: <KEY> intends
"<spec_phrasing>" (spec; "<prd_phrasing>" per the PRD when no spec) but the
source at <file:line> currently has "<source_phrasing>". User decision:
document intended phrasing pending implementation.
See <KEY>-implementation-gaps.md gap #<n>. -->
```

`doc-reviewer`'s Source-code accuracy dimension (§4.3) recognises this
marker and treats the discrepancy as intentional (not BLOCKER) when it
is present.

### 7.7 When source-verification is impossible

If the orchestrator didn't pass `code_repos`, OR the code repos are
empty/unreachable: doc-planner emits a single `verification_warnings`
entry per user-visible claim with `finding: NOT_FOUND`,
`technique: "no-source-evidence"`. The orchestrator presents the same
§7.1 table (with the **Code** cell `"(not verifiable)"`, and the **Spec**
cell `(no spec)` when no spec was provided) and the same §7.2/§7.3 prompts;
"Document as intended (spec)" is then the natural default since no source-side
phrasing is available to contradict it.

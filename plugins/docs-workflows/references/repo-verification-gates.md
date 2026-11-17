# Repo verification gates (shared)

Single source of truth for extracting a documentation repository's **own** pre-PR checklist and
applying it to the files a run just wrote.

Consumed by `doc-planner` (`/document` keyed mode), by `/document` Mode B directly — direct mode has
no planner, so its orchestrator performs the extraction itself — and by `/docs-workflows:docs-write`,
whose orchestrator, with no planner either, does the same. All three produce the same block, and all
three feed the `repo_checklist` gate in `${CLAUDE_PLUGIN_ROOT}/references/gate-ledger.md`.

---

## 1. Why

A docs repo publishes the checks a human reviewer applies before merging. `example-docs` puts them
in `CONTRIBUTING.md` under `## PR checklist` — a Contributors minimum check and an InfoDevs advanced
check covering frontmatter fields, changelog conformance, sensitive information, duplicate headings,
terminology, and "Validate the change. The validation must pass with no errors or warnings."

Those are exactly the checks a generated PR should already satisfy. Consuming them is not optional
politeness: a run that ignores them ships work a reviewer will bounce.

## 2. Finding the checklist

Scan the repo root (and `.claude/`) for `CONTRIBUTING.md`, `CONTRIBUTION.md`, `README.md`,
`CLAUDE.md`, `STYLE.md`, and `DOCUMENTATION-GUIDELINES.md`. In each, look for a checklist section —
headings matching, case-insensitively, `PR checklist`, `Before you submit`, `Before submitting`,
`Definition of done`, `Review checklist`, `Submission checklist`, or `Merge checklist`. Read every
sub-section beneath it.

Nothing found ⇒ emit `repo_verification_gates: []`. That is a normal outcome, not an error.

## 3. What to extract

Include an item when it is **checkable against the files this run wrote**:

| Kind | Examples |
|---|---|
| `frontmatter` | required fields present; `description` meets the repo's guidelines; `changelog` present and conforming |
| `content` | no sensitive information (hostnames, IP addresses, API tokens); no placeholder text left behind |
| `structure` | no duplicate headings; no walls of text; images referenced the way the repo requires |
| `terminology` | product names spelled and capitalised per the repo's list |
| `validation` | "run a local build and check the local preview"; "run source validation"; "the validation must pass with no errors or warnings" |

Exclude anything that is not about the written files: PR title conventions, reviewer assignment,
branch mechanics, ticket hygiene, release timing.

## 4. The block

```yaml
repo_verification_gates:        # [] when the repo publishes no checklist
  - check:  <one checkable requirement, phrased as a testable assertion>
    source: <file + section, e.g. "CONTRIBUTING.md § PR checklist → Advanced check (InfoDevs)">
    kind:   frontmatter | content | structure | terminology | validation
```

## 5. Applying it

- **`/document` keyed mode** — `doc-planner` emits the block during its guidance scan; `doc-reviewer`
  holds the written files against each entry; `/document` Phase 6.4 records the `repo_checklist`
  ledger row.
- **`/document` direct mode** — there is no planner. The orchestrator extracts the block itself at
  Phase 0, in the same pass that reads the repo's `Prerequisites` for
  `${CLAUDE_PLUGIN_ROOT}/references/toolchain-preflight.md` §2 source 3, checks the edited files
  against it at Phase 3.5, and records the `repo_checklist` row there.
- **`/docs-workflows:docs-write`** — there is no planner either. The orchestrator extracts the block
  itself, as direct mode does, checks each unit's page, and the entries the run added for it, against
  it at its Phase 6, and records the `repo_checklist` row there (`gate-ledger.md` §9); each unit's brief
  carries the block to `doc-writer` and `doc-reviewer` (`${CLAUDE_PLUGIN_ROOT}/references/docs-iteration/unit-brief.md` §2).

A `validation`-kind entry is **not** satisfied by reading files — it names a command the run must
actually have executed. Whether it ran is the business of the `style_check` / `build_check` ledger
rows. Record it in the block so a reviewer can see it was required, and let the ledger carry whether
it happened.

## 6. Hard rules

- NEVER emit an entry that cannot be checked against the files this run wrote.
- NEVER paraphrase a repo rule into a different requirement. Quote or tightly restate the repo's own
  wording, and always name its `source` file and section — a consumer must be able to cite it.
- These gates **augment, never override** the plugin's built-in references. Where one conflicts with a
  built-in rule, record both and note the conflict; never silently pick a winner.
- NEVER treat an empty block as a failure. A repo without a checklist is normal.

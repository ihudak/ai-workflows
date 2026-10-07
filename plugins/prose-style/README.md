# prose-style

A pluggable prose style checker and writing aid for Claude Code.

## What it does

Checks and improves the writing in product documentation, planning documents (Epics,
PRDs, ARDs), release notes, and any other prose that should read consistently —
terminology, voice and tone, grammar, formatting, UI interaction verbs, inclusive
language, and the accessibility of the prose itself.

It ships a **vendor-neutral baseline** so it is useful with no configuration at all, and
it **layers your organization's own style guide on top** when you point it at one. The
overlay augments and overrides the baseline; every resolution miss falls back silently
to the baseline, so a machine with nothing configured behaves exactly like a machine
that has never heard of your style guide.

## Components

| Component | Type | Purpose |
|---|---|---|
| 8 reference docs | `references/` | The vendor-neutral baseline rule set |
| `prose-style-checker` | agent | Resolves the active rules, checks files, outputs violations in the `docs-style-checker` schema |
| `prose-fixer` | agent | Applies safe, mechanical fixes for violations found by `prose-style-checker` |
| `prose-style-rules` | skill | Writing aid — loadable by any agent producing prose |
| `/prose-review-pr` | command | Reviews doc changes from a pull request (by PR ID or branch name) |
| `/prose-review-docs` | command | Reviews markdown files at a path; supports `--fix` for auto-correction |
| `/prose-style-refresh` | command | Regenerates your overlay from your configured style-guide source |

The three commands are typed-only (`disable-model-invocation: true`): type them, since a
request in prose does not start one. That keeps them out of the list of skills the model
picks from, inside Claude Code's budget for it; the `prose-style-rules` skill stays in it.

---

## The overlay

The plugin has one baseline and at most one overlay.

### Resolution order

The **baseline** is always loaded:

```
${CLAUDE_PLUGIN_ROOT}/references/
```

The **overlay** is the first of these that resolves — first hit wins, and the search
stops there:

| Order | Source | Resolves when |
|---|---|---|
| 1 | the `rules_path` input (or `--rules <path>` on a command) | it is a readable directory holding ≥1 `.md` file |
| 2 | `<repo-root>/.prose-style/rules/` | same |
| 3 | `$PROSE_STYLE_PATH` | same |
| 4 | *(none)* | always — the baseline alone is the rule set |

`<repo-root>` is the repository a caller names in the checker's `repo_root` input — a
caller that checks a copy of a file kept outside its repository, as `/release-notes` does
with its draft, names the repository the file belongs to — and otherwise
`git rev-parse --show-toplevel` for the files being checked, falling back to the working
directory's repository, and, where neither is in a repository, to the deepest directory that
holds every file being checked, whose own `.prose-style/rules/` is then order 2. The checker's
output echoes the `<repo-root>` it took as `repo_root` — `none` where a caller's `rules_path`
resolved and it named no `repo_root`, since order 2 is then never reached — so a caller that named
one can tell its input was honoured; the input and the echo arrived together, in 0.4.0.

**Every miss is a silent, non-blocking fallback.** A missing `.prose-style/` directory,
an unset `$PROSE_STYLE_PATH`, an unreadable path, a directory with no markdown in it —
each falls through to the next order without an error, a warning, or a prompt. The only
report is one `Rules:` line in the review output. The overlay is never a gate: nothing
in this plugin fails because your style guide is not configured.

### Precedence

The overlay layers on top of the baseline, per file name:

| Situation | Result |
|---|---|
| Overlay file has the same name as a baseline file | Both are in force; the overlay is layered on top |
| Overlay and baseline conflict on the same term or rule | **The overlay wins** |
| A term appears under an overlay's `## Allowed` heading | The matching baseline rule is suppressed |
| Overlay file's first line is `<!-- prose-style: replace -->` | That baseline file is **not read**; the overlay replaces it |
| Overlay file's name matches no baseline file | Read as an additional rule source, at overlay authority |
| Baseline file has no overlay counterpart | Fully in force |

The overlay can therefore add rules, tighten rules, contradict rules, and switch rules
off — without editing anything the plugin ships.

**No rule set reaches a heading the caller names in `fixed_headings`.** A caller writing to
a format whose section headings are fixed — a PRD's `## User Stories`, an Epic's
`## Independent Test` — passes those headings, and the checker raises nothing on them,
whatever the baseline or an overlay says, because a renamed heading breaks every check and
reader that finds the section by it. `/create-prd`, `/update-prd` and `/epics` pass their
formats' headings; the input arrived in 0.7.0.

### Worked example

Your organization uses "workspace" where the product used to say "tenant", writes in
British English, follows AP style (no serial comma), and ships a desktop-only app where
"click" is accurate.

Create the overlay in the repo you write docs in:

```bash
mkdir -p .prose-style/rules
```

`.prose-style/rules/terminology.md`:

```markdown
# Acme terminology

## Canonical terms

| ✅ Use | ❌ Do not use | Note |
|---|---|---|
| workspace | tenant, org, account space | One workspace per customer environment |
| Acme Agent | agent, ACME agent, acme-agent | Full name at first mention; "the agent" after |

## Deprecated terms

| Retired term | Replacement | Retired in |
|---|---|---|
| control center | admin console | 2025.3 |
```

`.prose-style/rules/word-list.md`:

```markdown
# Acme word list

## Allowed

| Term | Why |
|---|---|
| click | Acme Desktop is mouse-only; "click" is accurate. |

| ❌ Avoid | ✅ Use instead | Severity |
|---|---|---|
| behavior | behaviour | NIT |
| color | colour | NIT |
| license (noun) | licence (noun) | NIT |
```

`.prose-style/rules/formatting.md`:

```markdown
<!-- prose-style: replace -->

# Acme formatting

We follow AP style, not Chicago.

## Serial comma — do not use

- ✅ ingest, transform and query
- ❌ ingest, transform, and query

## Headings

Sentence case, no closing punctuation. (Unchanged from the baseline, restated here
because this file replaces it.)
```

Now run a review:

```
/prose-review-docs docs/
```

The report opens with `Rules: overlay: /repo/.prose-style/rules`, and:

- "tenant" is a MAJOR `Prose.Terminology.WrongTerm` violation — an overlay rule.
- "click" is **not** flagged, even though the baseline flags it — the `## Allowed`
  entry suppresses it.
- "behaviour" is **not** flagged as a British spelling — the overlay's own table
  reverses the direction.
- "ingest, transform, and query" is flagged — `formatting.md` carries the `replace`
  marker, so the baseline's serial-comma requirement was never loaded.
- Everything the overlay says nothing about — voice and tone, grammar, accessibility,
  UI verbs — is still checked against the baseline.

Note what the `replace` marker cost: because `.prose-style/rules/formatting.md` replaces
the baseline file, the baseline's heading, number, date, acronym, list, and link-text
rules are gone too. Use `replace` only when you intend to own the whole topic; layering
is almost always the better choice.

### Sharing an overlay across repos

Put the rules directory somewhere central and export the variable:

```bash
export PROSE_STYLE_PATH="$HOME/acme-style/rules"
```

A repo-local `.prose-style/rules/` still wins over it, so a team can keep a house style
globally and let one repo diverge.

### Keeping the overlay current

`/prose-style-refresh` regenerates the overlay from the source you configure in
`<overlay>/source.yml` — a set of URLs, a git repository, or a local directory. It has
no built-in style-guide URL: with nothing configured it asks where the rules should come
from, and it never writes into the shipped baseline. See
[`commands/prose-style-refresh.md`](commands/prose-style-refresh.md) for the
`source.yml` schema.

---

## Commands

### `/prose-review-pr` — review PR documentation changes

Reviews the markdown files changed in a pull request. Works with merge-commit
conventions (finds PRs by number in `git log`) and also accepts source branch names.

**Usage:**

```
/prose-review-pr 9089
/prose-review-pr 9089 --repo /workspace/product-docs
/prose-review-pr feat/improve-install-guide
/prose-review-pr my-branch --doc-type product-docs
/prose-review-pr my-branch --rules ~/acme-style/rules
```

**Arguments:**

| Argument | Description |
|---|---|
| `<PR number>` | Finds the merge commit or remote branch for that PR |
| `<branch name>` | Diffs the branch against the default branch |
| `--repo <path>` | Override the repo path (default: current working directory) |
| `--doc-type <type>` | Severity calibration: `product-docs` (default), `epic`, `prd`, `ard`, `general` |
| `--rules <path>` | Override overlay discovery for this run |

**What it does:**
1. Finds changed `.md` files from the PR diff.
2. Runs `prose-style-checker` on those files.
3. Runs Vale if the repo carries a Vale configuration file (`.vale.ini`, or one of the other names Vale reads: `.vale`, `_vale`, `vale.ini`, `_vale.ini`) and Vale is installed — on that configuration, never merged with your global Vale configuration or replaced by `VALE_CONFIG_PATH`; where it sets no `StylesPath`, Vale's shared default styles directory is read with it, and `/prose-review-pr` step 6 says what that directory can hold.
4. Reports violations with file, line, severity, and suggested fix.
5. Shows violations in diff context so you see what changed alongside what violated.
6. Offers to auto-fix via `prose-fixer`.

### `/prose-review-docs` — review documentation files or directories

Reviews one or more markdown files (or a whole directory tree). Optionally applies safe
automatic fixes.

**Usage:**

```
/prose-review-docs docs/get-started/
/prose-review-docs docs/get-started/index.md
/prose-review-docs docs/setup/ docs/config/auth.md
/prose-review-docs docs/ --fix
/prose-review-docs docs/ --severity MINOR
/prose-review-docs docs/ --doc-type product-docs --fix
/prose-review-docs docs/ --rules ~/acme-style/rules
```

**Arguments:**

| Argument | Description |
|---|---|
| `<path>` | File or directory path (multiple allowed; directories are recursive) |
| `--fix` | After reviewing, apply safe mechanical fixes via `prose-fixer` |
| `--doc-type <type>` | Severity calibration (default: `product-docs`) |
| `--severity <level>` | Only report violations at this level or above (default: show all) |
| `--rules <path>` | Override overlay discovery for this run |

**What it does:**
1. Recursively finds all `.md` files in the specified path(s).
2. Runs `prose-style-checker` on those files.
3. Runs Vale if available, on the repository's configuration, as `/prose-review-pr` does.
4. Reports violations grouped by file.
5. With `--fix`: applies safe fixes via `prose-fixer`, then re-checks to verify.

### `/prose-style-refresh` — refresh your overlay

Regenerates the overlay rules from your configured source. See
[The overlay](#the-overlay) above.

**Usage:**

```
/prose-style-refresh
/prose-style-refresh --source https://style.example.com/docs
/prose-style-refresh --from ~/acme-style-guide/
/prose-style-refresh --dry-run
```

---

## Agents

### `prose-style-checker`

Read-only checker. Takes a list of file paths and a doc type, resolves the active rule
set, and returns violations in the standard schema. Never modifies files. Its step 1 is
the canonical statement of the overlay resolution — the commands and the skill follow it.

### `prose-fixer`

Fix agent. Takes violations from `prose-style-checker` and applies safe, mechanical
fixes — terminology swaps, excluded-word replacements, spelling-variant corrections, UI
interaction verbs. Skips anything ambiguous (voice/tone rewrites, heading changes, serial
commas). Reports what was fixed and what was left for manual review. It applies the
`suggestion` it is handed and never re-derives a rule, so an overlay override reaches the
fix unchanged.

**Fixable categories:** canonical-term swaps, deprecated terms, product-name casing,
excluded words, single-word patronizing deletions, spelling variants, wrong compounds,
awkward contractions, number formatting, UI interaction verbs.

**Unfixable (skipped):** passive voice, hedge words, wordiness, heading text changes,
serial commas, date reformatting, structural grammar, trademark symbols, alt text, link
text, sensory instructions, heading structure.

---

## Skill

### `prose-style-rules`

Load it in any agent that writes prose. It resolves the same baseline-plus-overlay rule
set and carries a quick checklist, so content comes out correctly styled instead of being
corrected afterwards.

---

## Reference docs (the baseline)

`references/` holds distilled, actionable rules — not copies of any vendor's style guide.
Each file names the public authorities it is grounded in.

| File | Covers | Grounded in |
|---|---|---|
| `terminology.md` | Naming rules, trademarks, third-party names, and the schema for declaring your own terms | Microsoft, Google, Apple, Chicago |
| `word-list.md` | Excluded and discouraged words, confusables, compounds, spelling, and the entry schema | Microsoft, Google, Merriam-Webster, Conscious Style Guide |
| `voice-and-tone.md` | Clarity, directness, respect, helpfulness, contractions, passive voice | Microsoft, Google, Apple, plainlanguage.gov |
| `grammar.md` | Sentences, tense, person, agreement, verbs, modifiers, parallelism | Chicago, Microsoft, Google |
| `formatting.md` | Headings, numbers, punctuation, lists, dates, acronyms, links, code, emoji | Microsoft, Google, Chicago, AP, WCAG |
| `ui-interactions.md` | Select, go to, open, enter, sign in, turn on/off, control naming | Microsoft, Apple, Google |
| `accessibility.md` | WCAG prose criteria, inclusive language, internationalization | W3C WCAG 2.2, Conscious Style Guide, Google, Microsoft |
| `top-10-tips.md` | The pre-publish checklist | Microsoft, Google, plainlanguage.gov, WCAG |

Where two authorities disagree — the serial comma (Chicago vs. AP), spaced em dashes,
"click" vs. "select" — the baseline picks one, names the split in the file, and marks it
as an overlay point.

The baseline deliberately ships **no organization-specific terms**. `terminology.md`
holds naming *rules* plus the schema for declaring your own; the terms themselves are
yours to supply.

---

## Violation schema

Both `prose-style-checker` and `prose-fixer` use this schema (compatible with
`docs-style-checker` from `docs-workflows`):

```yaml
file:       <absolute path>
line:       <line number>
rule:       Prose.<Category>.<RuleName>
severity:   BLOCKER | MAJOR | MINOR | NIT
message:    <human-readable description>
suggestion: <proposed fix>
```

Rule prefixes: `Prose.Terminology`, `Prose.WordList`, `Prose.VoiceTone`, `Prose.Grammar`,
`Prose.Formatting`, `Prose.UI`, `Prose.Accessibility`. Overlay-sourced rules use the same
prefixes, so a consumer never has to special-case the source.

`prose-style-checker` also returns `rules_source` — `baseline` or `overlay:<path>` — so a
caller can report which rule set produced the findings. MAJOR is the severity ceiling;
this checker never emits BLOCKER.

---

## How it fits with the dev-workflows family

This plugin supplies the **complementary semantic pass** that the `docs-style-checker` agent in `docs-workflows` always runs alongside a repo's own linter. Fallback is what it becomes in one branch of that ladder — the sole pass, when no primary rung produced a result — not the relationship:

- **`/document`** (keyed mode) Phase 6.4 dispatches `docs-style-checker`, which runs the
  chain **internally**: the repo's primary linter (Vale/markdownlint) **and**
  `prose-style-checker` as a complementary semantic / cross-page-consistency pass, with
  both finding sets merged and deduped. `/document` never invokes `prose-style-checker`
  separately. `docs-workflows` declares this plugin as a dependency, so that complementary
  pass has no absent case — it is also what carries the check on a repo with no linter of
  its own.
- **`/epics`** Phase 6.2 invokes `prose-style-checker` directly (Epic drafts live in the
  specs tree, where no repo linter runs). `/create-prd`, `/update-prd`, and
  `/release-notes` invoke it directly too.
- **`/prose-review-pr` and `/prose-review-docs`** are standalone — invoke them directly
  without going through the `dev-workflows` pipeline.

---

## Installation

This plugin is part of the `shipwright` marketplace. Install it through Claude Code's
plugin system — it will be available alongside `dev-workflows`.

For marketplace install and prerequisites, see the [repo-root setup guide](../../README.md).

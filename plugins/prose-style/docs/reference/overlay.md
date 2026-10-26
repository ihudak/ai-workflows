# The overlay

The plugin has one baseline and at most one overlay. The baseline — the eight files under `references/` — is always loaded. The overlay is your organization's own rules, layered on top of it.

## Where the overlay is found

The first of these that resolves is the overlay, and the search stops there — two overlays are never merged:

| Order | Source | Resolves when |
|---|---|---|
| 1 | `--rules <path>` on a command, or the `rules_path` a calling plugin passes | it is a readable directory holding at least one `.md` file |
| 2 | `<repo-root>/.prose-style/rules/` | the same |
| 3 | `$PROSE_STYLE_PATH` | the same |
| 4 | *(none)* | always — the baseline alone is the rule set |

`<repo-root>` is the repository the checked files belong to: the one a calling plugin names, where it checks a copy kept outside its repository, as `/release-notes` does with its draft; otherwise the repository holding the first file checked, then the working directory's, and, outside any repository, the deepest directory holding every checked file.

**Every miss is a silent fall-through.** A missing `.prose-style/` directory, an unset `$PROSE_STYLE_PATH`, an unreadable path, a directory with no markdown in it — each falls through to the next order with no error, warning or question. The only report is the `Rules:` line in the review's summary. Nothing in this plugin fails because your style guide is not configured.

## How an overlay file layers

Per file name:

| Situation | Result |
|---|---|
| An overlay file has the same name as a baseline file | Both are in force; the overlay is layered on top |
| The two conflict on the same term or rule | **The overlay wins** |
| A term is listed under an overlay file's `## Allowed` heading | The matching baseline rule is suppressed |
| An overlay file's first line is `<!-- prose-style: replace -->` | That baseline file is **not read**; the overlay replaces it |
| An overlay file's name matches no baseline file | It is read as an additional rule source, at overlay authority |
| A baseline file has no overlay counterpart | It is fully in force |

Only `.md` files in the overlay directory are rules; a `source.yml`, a README or an editor's leftovers are ignored. An overlay can therefore add rules, tighten them, contradict them and switch them off, without editing anything the plugin ships.

**A heading a calling plugin names as fixed is never checked.** A plugin writing a format whose section headings are fixed — a PRD's `## User Stories`, an Epic's `## Independent Test` — passes those headings, and no rule, the overlay's included, raises anything on them, because renaming one would break every check and reader that finds the section by it.

## The dialect, where the overlay says nothing

Two baseline rules pick a side of a split: the spelling variant (American English: *behavior*, *color*, *catalog*) and the em dash (closed: *word—word*). Each is meant to be flipped by an overlay, and an overlay that restates either settles it.

**Where no overlay restates them, the checker infers each from the files it checks** rather than taking the baseline's side on trust. It counts the British and American spellings in the prose — never in code, links or frontmatter, and never an `-ise`/`-ize` ending, which British Oxford spelling writes with a `z` — and the spaced and closed dashes, and holds the files to the majority: a specs tree written in British English with spaced dashes is flagged only where it departs from that. Where the files give no evidence, or a tie, nothing is raised for that rule. The `Rules:` line reports what was settled and how:

```
Rules: baseline; dialect: british spelling (inferred), spaced dashes (inferred)
```

An overlay is still the way to fix the dialect once for every file, and the only way where a document is too short to show one.

## A worked example

Your organization says "workspace" where the product used to say "tenant", writes British English, follows AP style (no serial comma), and ships a desktop-only app where "click" is accurate. In the repository you write docs in, create `.prose-style/rules/` with three files.

`terminology.md`:

```markdown
# Acme terminology

## Canonical terms

| ✅ Use | ❌ Do not use | Note |
|---|---|---|
| workspace | tenant, org, account space | One workspace per customer environment |

## Deprecated terms

| Retired term | Replacement | Retired in |
|---|---|---|
| control center | admin console | 2025.3 |
```

`word-list.md`:

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
```

`formatting.md`:

```markdown
<!-- prose-style: replace -->

# Acme formatting

We follow AP style, not Chicago.

## Serial comma — do not use

- ✅ ingest, transform and query
- ❌ ingest, transform, and query
```

Now `/prose-review-docs docs/` opens with `Rules: overlay: /repo/.prose-style/rules`, and:

- "tenant" is a MAJOR `Prose.Terminology.WrongTerm` violation — an overlay rule;
- "click" is **not** flagged, though the baseline flags it — the `## Allowed` entry suppresses it;
- "behaviour" is **not** flagged — the overlay's own table reverses the direction, and the dialect reads `(overlay)`;
- "ingest, transform, and query" is flagged — `formatting.md` replaces the baseline's, so the baseline's serial-comma rule was never loaded;
- everything the overlay says nothing about — voice and tone, grammar, accessibility, UI verbs — is still checked against the baseline.

Note what the `replace` marker cost: the baseline's heading, number, date, acronym, list and link-text rules went with the serial comma. Use `replace` only when you mean to own the whole topic; layering is almost always the better choice.

## Sharing and refreshing an overlay

Put the rules directory somewhere central and point [`$PROSE_STYLE_PATH`](environment.md) at it; a repository's own `.prose-style/rules/` still wins, so a team can keep a house style everywhere and let one repository diverge. [`/prose-style-refresh`](../commands/prose-style-refresh.md) regenerates the overlay from your style guide's own source.

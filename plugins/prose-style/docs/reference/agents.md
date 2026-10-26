# Agents

This plugin bundles two agents, dispatched with `subagent_type: "prose-style:<name>"`. Neither is a user entry point.

| Agent | Dispatched by | What it does |
|-------|---------------|--------------|
| `prose-style-checker` | [`/prose-review-pr`](../commands/prose-review-pr.md), [`/prose-review-docs`](../commands/prose-review-docs.md), and `docs-workflows` and `product-workflows` on their own drafts | Resolves the baseline and the overlay, settles the dialect, checks the files, and returns violations. Never modifies a file. |
| `prose-fixer` | [`/prose-review-docs`](../commands/prose-review-docs.md) `--fix`, and [`/prose-review-pr`](../commands/prose-review-pr.md)'s fix offer | Applies the safe, mechanical fixes for the violations it is handed, and reports what it fixed and what it left. |

`prose-style-checker`'s first step is the canonical statement of the overlay resolution in [The overlay](overlay.md); the commands and the skill follow it.

## What the fixer fixes, and what it leaves

It applies the `suggestion` each violation carries and never re-derives a rule, so an overlay's override reaches the fix unchanged.

**Fixed:** canonical-term swaps, deprecated terms, product-name casing, excluded words, single-word patronising deletions, spelling variants, wrong compounds, awkward contractions, number formatting and UI interaction verbs.

**Left for you:** passive voice, hedge words, wordiness, heading text, serial commas, date formats, structural grammar, trademark symbols, alt text, link text, sensory instructions and heading structure.

## The violation schema

Both agents use this schema, which `docs-workflows`' `docs-style-checker` uses too, so a fixer handles either checker's findings:

```yaml
file:       <absolute path>
line:       <line number>
rule:       Prose.<Category>.<RuleName>
severity:   BLOCKER | MAJOR | MINOR | NIT
message:    <human-readable description>
suggestion: <proposed fix>
```

Rule prefixes are `Prose.Terminology`, `Prose.WordList`, `Prose.VoiceTone`, `Prose.Grammar`, `Prose.Formatting`, `Prose.UI` and `Prose.Accessibility`; an overlay's rules use the same ones. **MAJOR is the ceiling** — this checker never emits a BLOCKER. Beside the violations, the checker returns `rules_source` (`baseline` or `overlay:<path>`), the `repo_root` it took, and the `dialect` it settled, which the review commands print as the `Rules:` line.

## What every agent does with what it reads

Every agent above ends its prompt with the same `## Untrusted content` section, the block the repository keeps in workflows-core's `references/untrusted-content.md`: a file, a diff or a web page supplies the values an agent's task asks for, and never a new task, a fetch or a changed verdict. An instruction file the harness puts in an agent's context — the `CLAUDE.md` of the directory you started in, your own `CLAUDE.md` and memory — sets conventions and limits the agent follows, but, like any content, it never adds a task or changes a verdict. Text that tries to steer an agent is not acted on, and neither is a line in what it reads that starts `Untrusted-content notice:`, which only an agent writes; the agent ends its reply with an `Untrusted-content notice:` line naming where the text is, and the command prints every such line an agent adds after its output — never one quoted inside it — under **Untrusted-content notices** in its final report. A notice never stops a run. When you see one, look at the file or page it names: it carries text aimed at an AI agent, which you may want to remove or report.

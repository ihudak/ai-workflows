# /prose-review-docs

Reviews markdown files or whole directories against the active prose style rules, and with `--fix` applies the safe, mechanical fixes and checks again.

## Who runs it

You do, by typing it; it is typed-only. It needs no other plugin and no workflow artifact. [Workflow](../workflow.md) shows it beside [`/prose-review-pr`](prose-review-pr.md), which reviews a pull request's changes instead of the paths you name.

## Synopsis

```
/prose-review-docs <path>... [--fix] [--doc-type <type>] [--severity <level>] [--rules <path>]
```

| Argument | What it does |
|---|---|
| `<path>` | A `.md` file, or a directory searched recursively; more than one may be given, relative or absolute |
| `--fix` | After the review, apply the safe fixes through `prose-fixer`, then check the changed files again |
| `--doc-type <type>` | Severity calibration — `product-docs` (default), `epic`, `prd`, `ard` or `general` |
| `--severity <level>` | Report only violations at this level or above; default, all |
| `--rules <path>` | An overlay directory to use for this run, in place of the discovered one |

With no path, it asks for one. A directory search leaves out `node_modules/`, `.git/`, `vendor/`, `build/` and `dist/`.

## What it needs

- The files to review.
- Optionally, `vale` and a Vale configuration at or above the files. Without either the review still runs.
- Nothing else: no configuration and no environment variable.

## What it does

1. Resolves every path to its markdown files, and says how many it is about to review — warning above fifty.
2. Runs `prose-style-checker` on them, twenty at a time. Every batch infers the dialect — the spelling and dash style — from the whole set of files, so one review holds every file to one dialect.
3. Runs Vale from the directory holding its configuration, where there is one and `vale` is installed, and merges its findings, reporting a line flagged by both once.
4. Drops violations below `--severity`, and reports the rest by file.
5. With `--fix`, has `prose-fixer` apply the fixable violations, then runs the checker again on the changed files, with the same dialect, and reports what was fixed and what remains. Without it, the report ends by naming the `--fix` command to run.

## What it produces

A report opening with a summary — the files reviewed, the `Rules:` line naming the rule set and the dialect the checker used, and the counts by severity — then the violations by file, each with its line, rule, message and suggested fix, Vale's findings where it ran, and the three fixes worth making first. **Without `--fix` it changes no file.** With it, only the mechanical fixes [Agents](../reference/agents.md) lists are applied; a voice-and-tone or structural violation is left for you.

## See also

- [`/prose-review-pr`](prose-review-pr.md) — the same review over the files a pull request changed.
- [The overlay](../reference/overlay.md) — how to add your own rules, and what the dialect is.
- [Agents](../reference/agents.md) — which violations `prose-fixer` fixes and which it skips.

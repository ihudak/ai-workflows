# /prose-review-pr

Reviews the markdown files a pull request changed against the active prose style rules — the bundled baseline, plus your organization's overlay where one is configured — and shows each violation in the diff context that introduced it.

## Who runs it

You do, by typing it; it is typed-only. It needs no other plugin and no workflow artifact. [Workflow](../workflow.md) shows where it sits beside [`/prose-review-docs`](prose-review-docs.md), which reviews files you name rather than a pull request's changes.

## Synopsis

```
/prose-review-pr <PR number | branch name> [--repo <path>] [--doc-type <type>] [--rules <path>]
```

| Argument | What it does |
|---|---|
| `<PR number>` | All digits: finds the pull request's merge commit, or its remote branch |
| `<branch name>` | Anything else that is not a flag: diffs the branch against the default branch |
| `--repo <path>` | The repository to read; default, the current working directory |
| `--doc-type <type>` | Severity calibration — `product-docs` (default), `epic`, `prd`, `ard` or `general` |
| `--rules <path>` | An overlay directory to use for this run, in place of the discovered one |

With no target, it asks for a pull-request number or a branch name.

## What it needs

- A git repository holding the pull request's commits or its branch.
- Optionally, `vale` and a Vale configuration in the repository. Without either the review still runs, and the report says Vale was not available.
- Nothing else: no configuration and no environment variable.

## What it does

1. Finds the changed files: a pull request number is looked up as a merge commit (`Pull request #<N>: …` or `… (#<N>)`) and otherwise as a remote branch; a branch name is diffed against the default branch.
2. Keeps the `.md` files, leaving out `CHANGELOG.md`, `README.md`, `CONTRIBUTING.md`, `RELEASING.md` and anything under `node_modules/`, `.git/`, `vendor/`, `build/` or `dist/`. A file the pull request deleted is skipped and listed.
3. Runs `prose-style-checker` on the files that remain.
4. Runs Vale where the repository carries a Vale configuration and `vale` is installed — on that configuration alone, never merged with your global one — and merges its findings, reporting a line flagged by both once.
5. Reports the violations by file, each beside the diff hunk it falls in.
6. Offers to fix the safe ones through `prose-fixer`.

## What it produces

A report opening with a summary — the files changed, the `Rules:` line naming the rule set and the dialect the checker used, and the counts by severity — then the violations by file in diff context, Vale's findings where it ran, the deleted files it skipped, and the three fixes worth making first. **It changes no file during the review.** Only when you accept its fix offer does `prose-fixer` edit the files, applying the mechanical fixes and leaving the rest for you.

## See also

- [`/prose-review-docs`](prose-review-docs.md) — the same review over files or directories you name, with `--fix`.
- [The overlay](../reference/overlay.md) — what the `Rules:` line reports, and how to add your own rules.
- [Agents](../reference/agents.md) — the checker and the fixer, and the violation schema.

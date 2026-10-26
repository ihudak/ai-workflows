# Getting started

Add the marketplace, then install this plugin:

```bash
claude plugin marketplace add ihudak/ai-workflows
claude plugin install prose-style@shipwright
```

You may already have it: `docs-workflows` and `product-workflows` both declare it as a dependency, so installing either installs this plugin too. `dev-workflows` does not use it.

To pick up later changes:

```bash
claude plugin marketplace update shipwright
claude plugin update prose-style@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same with a picker.

It runs in Claude Code only. It needs nothing else to start: no configuration, no environment variable, and no linter. Where a repository carries a Vale configuration and `vale` is installed, the two review commands run Vale beside the checker and report both.

## What you can set on your machine

### `PROSE_STYLE_PATH`

Optional. A directory of `.md` files holding your organization's own style rules — terminology, word list, formatting choices — shared across every repository you work in. A repository's own `.prose-style/rules/` directory wins over it, so a team can keep a house style globally and let one repository diverge. Unset is the normal case: the checker uses the baseline alone, and says which rule set it used in one `Rules:` line.

```bash
export PROSE_STYLE_PATH="$HOME/acme-style/rules"
```

[The overlay](reference/overlay.md) is the full resolution order and how an overlay file layers over the baseline; [Environment](reference/environment.md) is what the variable does when it is unset or unreadable.

## Run it

```
/prose-style:prose-review-docs docs/
/prose-style:prose-review-pr 9089
```

Type them: the three commands are typed-only (`disable-model-invocation: true`), which keeps them out of the list of skills the model picks from, so asking in prose does not start them. The `prose-style-rules` skill stays in that list, so an agent writing prose can load it. See the [documentation index](README.md) for everything else, including the [Workflow](workflow.md) page.

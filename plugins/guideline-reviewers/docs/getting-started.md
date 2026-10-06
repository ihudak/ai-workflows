# Getting started

Add the marketplace, then install this plugin:

```bash
claude plugin marketplace add ihudak/ai-workflows
claude plugin install guideline-reviewers@shipwright
```

To pick up later changes:

```bash
claude plugin marketplace update shipwright
claude plugin update guideline-reviewers@shipwright
```

**Both steps are needed, and the second is the one that changes what runs.** `marketplace update` refreshes the catalogue — what the marketplace advertises — while an already-installed plugin stays at the version you installed. `claude plugin update` upgrades it, and **requires restarting Claude Code to apply.** The interactive `/plugins` interface does the same with a picker. This page used to say the first line alone was enough; it is not, and the symptom is quiet — `claude plugins list` keeps reporting the old version while the catalogue advertises the new one.

This plugin is standalone — it depends on no other plugin, consumes no workflow artifact, and produces none. It ships two commands, [`/api-guideline-reviewer`](commands/api-guideline-reviewer.md) and [`/guideline-reviewer`](commands/guideline-reviewer.md); neither needs anything set up before its first run.

## What you can set on your machine

Both variables below are optional. Unset is the normal case for most readers — each degrades silently to the bundled baseline.

### `UI_GUIDELINES_PATH`

Your organization's own UI rules, as a **flat** directory of `.md` files — files at its top level, matched to the baseline by name. The bundled guidelines are a vendor-neutral baseline distilled from public standards (Apple HIG, Material Design 3, Fluent 2, WCAG 2.2, the ARIA APG); rules specific to your design system have no public equivalent and should not ship in a public plugin, so `/guideline-reviewer` layers this directory over the baseline instead. Unset is the normal case and degrades silently to the baseline alone.

### `API_GUIDELINES_PATH`

The same idea for `/api-guideline-reviewer` — your own scope grammar, header spellings, or error-envelope contract, layered over the bundled public-source baseline. Flat here too, even though the subtree it overlays is nested: put the files at the top level. This governs the *prose* rules; the executable half is separate, where your repo's own `.spectral.yaml`, `.spectral.yml` or `.spectral.json` takes precedence over the bundled Spectral ruleset. Unset degrades silently.

See [Environment](reference/environment.md) for the exact resolution order, the layout each variable expects, and what an unreadable path — or a readable one holding no `.md` file — does.

### Claude Code's skill-listing budget

**Set this once, in `~/.claude/settings.json`, whichever plugins you install.** Claude Code shows the model one list of every installed plugin's skills and model-invocable commands, and gives that list 1% of the context window — 8,000 characters in a 200K-token session, and in every subagent on a 200K model. Past that it shortens every description in the list, and the model can no longer tell which skill fits a task. This marketplace's commands are typed-only and take no room in the list, but its skills do, and so does every other plugin, Claude Code's own skills and your personal ones: every plugin of the `shipwright` marketplace, installed together, takes about 5,600 characters. Add this top-level key to the settings file:

```json
"skillListingBudgetFraction": 0.025
```

That gives 20,000 characters at 200K and 100,000 at 1M; a session pays only for what is listed, never for the budget, and the change applies from the next session. **Check that it is enough**: start one session with `claude --debug`, then search `~/.claude/debug/latest` for `Skill listing over budget: <N> skills, <X> chars > <Y> budget`. If that line is there, the list still overflows: set the fraction to at least X ÷ 800,000 (for X = 32,000, `0.04`), or turn off skills you do not use with `/skills`. The `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable sets a fixed number of characters instead, and overrides the setting.

## Run it

```
/guideline-reviewers:api-guideline-reviewer specs/openapi.yaml
/guideline-reviewers:guideline-reviewer app/src/pages/SettingsPage.tsx
```

Type them: both are typed-only (`disable-model-invocation: true`), which keeps them out of the list of skills the model picks from, so asking in prose does not start them. Both commands are standalone reviewers — neither reads nor writes `$SPECS_PATH`, opens a branch, or expects a prior workflow artifact; each prints its subagent's verdict directly. See the [documentation index](README.md) for everything else, including [Workflow overview](workflow.md).

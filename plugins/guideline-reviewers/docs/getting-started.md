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

## Run it

```
/guideline-reviewers:api-guideline-reviewer specs/openapi.yaml
/guideline-reviewers:guideline-reviewer app/src/pages/SettingsPage.tsx
```

Type them: both are typed-only (`disable-model-invocation: true`), which keeps them out of the list of skills the model picks from, so asking in prose does not start them. Both commands are standalone reviewers — neither reads nor writes `$SPECS_PATH`, opens a branch, or expects a prior workflow artifact; each prints its subagent's verdict directly. See the [documentation index](README.md) for everything else, including [Workflow overview](workflow.md).

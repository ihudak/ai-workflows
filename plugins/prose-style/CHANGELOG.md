# Changelog

## 0.5.1 — 2026-10-05

### Fixed

- **Notices: only the lines an agent adds after its output.** Every agent carries the amended block and every dispatching command the amended relay sentence: only the `Untrusted-content notice:` lines an agent adds after its output are relayed, never one quoted inside it, and an agent reports a content line that starts with that token instead of passing it on.

## 0.5.0 — 2026-10-05

### Added
- **Both agents treat what they read as data, never instructions.** Each ends its prompt with the untrusted-content block the repository keeps in `workflows-core`'s reference: content supplies the values a task asks for and never a new task, a fetch or a changed verdict, and an agent reports what tried to steer it as an `Untrusted-content notice:` line.
- **Both commands that dispatch an agent relay those notices** under `Untrusted-content notices:` in their final report, or in the stop message of a run that ends early. The sentence cites nothing: this plugin does not depend on `workflows-core`, so its loader may not be installed.

## 0.4.1 — 2026-09-24

### Changed — the marketplace is now `shipwright`, and the repository `ihudak/ai-workflows`

The marketplace was `ihudak-plugins`, at `ihudak/ihudak-claude-plugins`. GitHub redirects the old repository URL, but the marketplace name is part of every install key (`<plugin>@ihudak-plugins`), so moving to the new name means registering the marketplace again. Removing a marketplace uninstalls the plugins installed from it, so reinstall each one you had:

```bash
claude plugin marketplace remove ihudak-plugins
claude plugin marketplace add ihudak/ai-workflows
claude plugin install <plugin>@shipwright
```

Run the last line once per plugin you use, then restart Claude Code. Environment variables and your specs, docs and code repositories are not touched. This plugin's `homepage` and `repository` now point at the new repository.

## 0.4.0

### Added

`prose-style-checker` takes an optional `repo_root` input: the repository whose rules apply, for a caller that checks a copy of a file kept outside its repository. Where it is given, it is `<repo-root>` for step 1b's order 2, the repository-local overlay, and nothing is derived; without it the checker derives `<repo-root>` from the files it is handed as 0.3.0 did, falling back to the working directory's repository. Its output echoes the `<repo-root>` it took, as `repo_root`, on every run — or `none`, where a caller's `rules_path` resolved and it named no `repo_root`, since order 2 is then never reached. That is how a caller that named one knows the input was honoured, since a 0.3.0 checker ignores the input and returns no such field. `/release-notes` checks its draft in a scratch file outside every repository, so that neither the checker nor the fixer sees the sections earlier runs appended to `release-notes.md`, and names the specs repository with it — without it, such a copy took the rules of whatever repository the session stood in, or none. The README's overlay section says the same.

### Fixed

`skills/prose-style-rules/SKILL.md` ended its `<repo-root>` ladder at "no overlay" where `prose-style-checker` step 1b ends at the deepest common parent of the files it was handed, so the two read as a contradiction once this release corrected the README to the checker's form. The skill's rung now says the difference is the input rather than the rule: a checker is handed a file list, and content being written has no path yet to take a parent of.

`skills/prose-style-rules/SKILL.md` and `commands/prose-style-refresh.md` both said `/prose-style-refresh` asks the skill for the baseline directory **because `${CLAUDE_PLUGIN_ROOT}` does not expand in a slash-command body**. That was verified false in a live run — the variable does expand there — and the marketplace's `CLAUDE.md` records the claim as retired. The mechanism is unchanged; the reason that holds is now the one both files state: the skill is where the baseline's location is written down together with the rule that nothing writes into it, so the one command that writes overlays takes the path from there rather than restating either.

`/prose-review-pr` told a run whose repository's default branch is not `main` to resolve it with `git symbolic-ref refs/remotes/origin/HEAD` "and use that". That prints `refs/remotes/origin/<name>`, which is not a name: put in place of `main` inside `origin/main...origin/<branch>` it makes `origin/refs/remotes/origin/master`, a revision git rejects, and in the local-branch forms it quietly diffs against the remote instead. The instruction also sat in the branch-name path alone, so it did not cover the PR-number path or step 7's context diff. Step 2 now opens with **The default branch**: take the name from `symbolic-ref --quiet --short`, which prints `origin/<name>`, strip the `origin/`, and put that name in `main`'s place in every form that names the default branch; where `origin/HEAD` is unset, the name is `master` when only `origin/master` exists, else `main`. The arguments table's branch-name row, which said the branch is diffed against `main`, now says against the default branch. The command never switches branches, so nothing here moved HEAD; the defect was a diff that failed or read the wrong base. The name counts only where `origin/<name>` exists: after a remote renames its default branch and a clone fetches with `--prune`, `symbolic-ref` still prints the deleted branch — `origin/master` — and exits 0, so a name the `rev-parse --verify --quiet origin/<name>` probe rejects is treated as an unset `origin/HEAD`.

`/prose-review-pr` ran Vale bare after a `git -C <repo_path> rev-parse --show-toplevel` line that changes no directory, and Vale reads the first `.vale.ini` it finds in the directory it runs in or above it — so the documented `--repo /workspace/product-docs` usage, with the session elsewhere, stopped with `E100 [.vale.ini not found]` or linted under another repository's rules or the machine's own. Step 6 now finds the `.vale.ini` where Vale's own search would, in `<repo_path>` and then in each directory above it up to the repository's top level, the nearest first — so `--repo` naming a site's `website/docs` finds `website/.vale.ini` — and runs Vale in a subshell from the directory holding it. `/prose-review-docs` step 5 ran the same bare `vale` over files anywhere, having found their `.vale.ini` at or above them; it now runs from that directory the same way.

Both looked for `.vale.ini` alone, while Vale reads its configuration from five file names — `.vale`, `_vale`, `vale.ini`, `.vale.ini` and `_vale.ini`, the first of them in that order within one directory — so a repository configured through `_vale.ini` was reported as having no Vale configuration and never linted by it. Both now look for all five, and the README's summary of `/prose-review-pr` says so.

Both also ran Vale on whatever configuration the machine supplied besides the repository's. Vale merges the user's global configuration — `~/.config/vale/.vale.ini` on Linux — under the repository's, so a style enabled only on the reviewer's machine raised findings the repository's rules never would, and a rule turned off only there went silent where the repository enables it; measured with Vale 3.21, a global config turning `Vale.Repetition` off made a repeated word the repository's config flags disappear from the report. And `VALE_CONFIG_PATH`, where the environment set it, named a file Vale read in place of the repository's. Both commands now run Vale inside the same subshell with the global file and `VALE_CONFIG_PATH` set aside, as a clean runner has neither, in the form `/prose-review-pr` step 6 defines and `/prose-review-docs` step 5 cites, which the configuration decides: where it sets `StylesPath`, `unset VALE_CONFIG_PATH && vale --no-global …`; where it sets none, `unset VALE_CONFIG_PATH` and Vale run with `XDG_CONFIG_HOME` pointed at a fresh, empty directory, which hides the global file and nothing else. The form's `cd` is `builtin cd` with its output discarded, and its `mktemp`, `vale` and `rm` run as `command <name>`, `--` ending `rm`'s options, because the Bash tool's shell carries the user's aliases and shell functions: measured with Vale 3.21 under bash and zsh, a `cd` function that prints put its output ahead of Vale's, a `vale` alias adding `--no-exit` turned Vale's exit 1 into 0, and an `rm -i` alias left the temporary directory behind with its prompt in the output, answered no from the empty standard input. `builtin`, not `command`, for the `cd`: that shell is bash or zsh, and zsh runs no builtin through `command`, only a `cd` found on `PATH` — Linux has none, so `command cd` there is a command not found, and macOS has `/usr/bin/cd`, which changes only its own child process's directory, so `command cd` there exits 0 and Vale runs wherever the session stands. So the Vale findings are the repository's configuration's, and the README's summaries say so — save that a configuration setting no `StylesPath` keeps Vale's default StylesPath, one directory for every such project on the machine, whose package configuration the latest `vale sync` into it wrote, another project's included, is read with it: step 6 states that limit, and neither command syncs to cure it. `--no-global` alone would not do: it also drops Vale's default StylesPath, where a configuration that sets no `StylesPath` keeps its synced packages and custom styles — a layout Vale documents as valid — so on such a repository it prints `E100 … style '<name>' does not exist on StylesPath` where 0.3.0 printed Vale's findings.

The README's overlay section said the search for `<repo-root>` falls back from the files' repository to the working directory's, "falling back to no repo-local overlay". `prose-style-checker` step 1b's last rung does not: where neither is in a repository, it takes the deepest directory that holds every file being checked as `<repo-root>`, and that directory's own `.prose-style/rules/` is order 2. The README now says so.

`prose-style-checker`'s *When to invoke* list and the README's *How it fits* section still named `/document`'s "Jira mode" and called Epic drafts "vault-internal", both retired: `/document` has a keyed mode, and `/epics` writes its drafts into the specs tree. Both now say so, and that no repo linter runs there, which is why `/epics` calls the checker directly.

## 0.3.0

### BREAKING

The plugin, its commands, and its agents have been renamed, and the vendored corporate
style guide has been replaced by a vendor-neutral baseline with a pluggable overlay.
**Every old name is gone — there are no aliases and no deprecation period.** Update any
caller before upgrading.

| Old name | New name |
|---|---|
| plugin `dt-style-guide` | plugin `prose-style` |
| agent `dt-style-checker` | agent `prose-style-checker` |
| agent `dt-doc-fixer` | agent `prose-fixer` |
| command `/dt-review-pr` | command `/prose-review-pr` |
| command `/dt-review-docs` | command `/prose-review-docs` |
| command `/dt-style-refresh` | command `/prose-style-refresh` |
| skill `dt-style-rules` | skill `prose-style-rules` |
| rule prefix `DT.*` | rule prefix `Prose.*` |
| output `checker: dt-style-guide` | output `checker: prose-style` |
| output `checker_source: dt-style-checker` | output `checker_source: prose-style-checker` |

Individual rule identifiers changed with the prefix, and several were renamed for
neutrality — `DT.WordList.BannedWord` is now `Prose.WordList.ExcludedWord`,
`DT.WordList.BritishSpelling` is now `Prose.WordList.SpellingVariant`, and
`DT.Accessibility.RacistTerm` is now `Prose.Accessibility.ExcludedTerm`. Anything
matching on rule strings needs updating.

### Added

- **Overlay mechanism.** The plugin now resolves an organization's own style guide on
  top of the shipped baseline. Resolution order, first hit wins: the `rules_path` input
  (`--rules <path>` on the review commands) → `<repo-root>/.prose-style/rules/` →
  `$PROSE_STYLE_PATH` → no overlay. The baseline at `${CLAUDE_PLUGIN_ROOT}/references/`
  is always loaded underneath.
- **Documented precedence.** The overlay augments and overrides the baseline per file
  name: both are in force, the overlay wins on conflict, an `## Allowed` section
  suppresses a baseline rule, a file whose first line is `<!-- prose-style: replace -->`
  supersedes its baseline counterpart outright, and a file with an unmatched name is an
  additional rule source.
- **Silent fallback as a hard rule.** Every resolution miss — missing directory, unset
  variable, unreadable path, no markdown inside — falls through without an error,
  warning, or prompt. The overlay is never a gate. Only a missing baseline *and* no
  overlay is an error.
- **`rules_source` output field** on `prose-style-checker` (`baseline` or
  `overlay:<path>`), surfaced as a one-line `Rules:` entry in both review commands.
- **`--rules <path>`** on `/prose-review-pr` and `/prose-review-docs`, for a one-off
  overlay override.
- **Entry schemas** in `references/word-list.md` and `references/terminology.md`, so an
  organization can declare its own terms, product names, trademarks, deprecated terms,
  severity overrides, and allowed exceptions in tables the checker reads structurally.
- **Prose-accessibility rules** grounded in WCAG 2.2 — alt text (1.1.1), link text
  (2.4.4, 2.4.9), sensory-only instructions (1.3.3), color-only signals (1.4.1), heading
  structure (1.3.1, 2.4.6), abbreviations (3.1.4) — with the matching
  `Prose.Accessibility.*` rules.

### Changed

- **The eight reference docs were rewritten from scratch as a vendor-neutral baseline**,
  grounded in public authorities named in each file: the Microsoft Writing Style Guide,
  the Google developer documentation style guide, the Apple Style Guide, The Chicago
  Manual of Style and AP, the Conscious Style Guide, plainlanguage.gov, and W3C WCAG 2.2.
  Where two authorities disagree — the serial comma, spaced em dashes, "click" vs.
  "select", US vs. non-US spelling — the baseline picks one, names the split, and marks
  it as an overlay point.
- **`/prose-style-refresh` refreshes from your configured source**, declared in
  `<overlay>/source.yml` (web URLs, a git repository, or a local directory) or passed as
  `--source` / `--from`. It carries no hardcoded style-guide URL: with nothing
  configured it asks. It writes into the overlay directory and **never** into the shipped
  baseline, which fixes the old command's central flaw — refreshed rules used to land in
  the plugin's install directory and vanish on the next reinstall.
- `prose-fixer` now applies the `suggestion` it is handed and never re-derives a rule, so
  an overlay override reaches the fix unchanged. It also skips text inside bolded UI
  labels, which are quotations of the product.
- Severity calibration gained rows for prose accessibility and for vague/inflated
  language, and the trademark row now never fires when the active rule set declares no
  marks.
- `README.md` rewritten around the overlay, with a worked example.

### Removed

- All Dynatrace product, solution, app, SKU, and license terminology, and the
  Dynatrace-specific pitfall table. The baseline ships **no** organization-specific
  terms by design; `terminology.md` now holds naming rules plus the schema for
  declaring your own.
- The registered-trademark inventory. Trademark handling is still enforced, but only
  against marks the active rule set declares.
- The hardcoded `styleguide.dynatrace.com` URL map in the refresh command.
- Entries with no defensible neutral equivalent: "around the clock" for 24/7, and
  `timeframe` as one word (standard English is two).

## 0.2.4

### Fixed

- **Stale `dev-workflows` command names and phase numbers.** `README.md` "How it fits with
  dev-workflows" and `agents/dt-style-checker.md` "When to invoke" still referenced the retired
  `/impl:jira:docs` / `/impl:jira:epics` / `/impl` names and a non-existent "Phase 6.7". Corrected to
  `/document` (Jira mode) **Phase 6.4** and `/epics` **Phase 6.2**, and the `/document` mechanism
  restated accurately: `docs-style-checker` runs the primary linter **and** `dt-style-checker` as a
  complementary pass internally, merging both finding sets — `/document` never invokes
  `dt-style-checker` separately, and `NOT_CONFIGURED` means neither was available. Also names the other
  direct callers (`/create-vi`, `/update-vi`, `/release-notes`).

## 0.2.3

- Synced curated terminology from the `mgd-specifications` `dynatrace-content-style`
  digest: `timeframe selector`, `Strato Design System`, `around the clock` (replaces
  `24/7` / `24x7`), `Dynatrace Operator`, `Hosts page`, `Synthetic Monitoring` vs.
  `Digital Experience Management`, `network zone`, `Full-Stack Monitoring`,
  `Premium High Availability add-on`, `Dynatrace web UI` vs. `interface`,
  `Health overview`.
- Corrected `timeframe` to one word (was listed as `time frame` in `word-list.md`),
  matching the curated digest, current Dynatrace product usage, and the added
  `timeframe selector` term — resolves a prior word-list-vs-digest contradiction.

## 0.2.2

- Updated `/dt-review-pr` `--repo` examples from `/repos/dynatrace-docs` to
  `/workspace/dynatrace-docs` to match the AI container's single-umbrella mount
  layout.

## 0.2.1

- Fixed agent/skill/command references to use `${CLAUDE_PLUGIN_ROOT}` instead of the
  non-resolving `~/.claude/plugins/data/...@.../` path convention; `dt-style-checker`
  is now invoked by `subagent_type` where called cross-plugin.

## 0.2.0

- Added `/dt-review-pr` command — reviews doc changes from a pull request
- Added `/dt-review-docs` command — reviews files/directories with optional `--fix`
- Added `dt-doc-fixer` agent — applies safe mechanical fixes for style violations
- Added `checker_source` field to `dt-style-checker` output for cross-plugin disambiguation
- Documented integration with `dev-workflows` (`docs-style-checker` fallback + Epic primary)

## 0.1.0

- Initial release
- `dt-style-checker` agent — LLM-based Dynatrace style guide checker
- `dt-style-rules` skill — writing aid for agents producing Dynatrace content
- `/dt-style-refresh` command — updates vendored references from styleguide.dynatrace.com
- 8 vendored reference docs (terminology, word-list, voice-and-tone, grammar, formatting, ui-interactions, accessibility, top-10-tips)

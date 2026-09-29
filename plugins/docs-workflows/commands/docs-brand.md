---
name: docs-brand
description: Extract a logo and a rough primary/accent colour pair from a product's own code and apply them to a documentation site's Material for MkDocs theme. Walks a fixed colour-source precedence (Tailwind config, CSS custom properties, a MUI theme, a web-app manifest, SCSS/LESS variables) and a fixed logo-search order, prints every extracted value with its file and line before applying anything, checks the pair against WCAG 2.2 contrast thresholds, and copies assets into docs/assets/ rather than linking back into the code repo. Runs standalone (branch, commit, drafted PR, never pushed) or --inline from /docs-init, which folds its diff and its contrast finding into that command's own review and PR — a rebrand should never require re-scaffolding the whole site.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Brand the documentation site: $ARGUMENTS

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

`/docs-brand` extracts a logo and a rough primary/accent colour pair from a product's own code and applies them to a documentation site's Material for MkDocs theme. Expectations are deliberately modest: a mark and a colour pair, not a design system. It runs two ways: **standalone**, reviewing its own diff and finishing on a branch with a drafted pull request the same way `/docs-workflows:docs-profile` does; and **`--inline`**, dispatched by `/docs-workflows:docs-init` Phase 5, where it skips its own preflight, its own review gate, its own pull request, and its own emitter tail entirely, and returns its diff plus its contrast finding for the caller's single review and single PR to absorb, or — where it cannot brand — `no branding applied: <reason>` under the failure contract below, which never ends the caller's run. Rebrands happen, and re-scaffolding a whole docs site to pick up a new logo would be absurd (D14).

**Signature:** `/docs-brand [<docs-repo-path>] [--from <code-repo-path>] [--inline] [--skip-costs] [--skip-feedback] [--enforce-model=<model>]`

**The `--inline` contract.** A caller passes the docs-repo path it just scaffolded as the positional token, explicitly — it is not required to, since Phase 0's `resolve-docs-repo` ladder below would otherwise resolve one on its own, but a ladder resolving independently of what the caller already has open is exactly the kind of drift this contract exists to prevent. `/docs-workflows:docs-init` is this contract's one consumer today.

**The `--inline` failure contract — an `--inline` run never ends its caller's run.** It returns exactly one of two results. **Branding applied**: the Phase 8 diff and the Phase 6 contrast finding. **No branding applied**: every stop an `--inline` run can reach — `DOCS_BRAND_NOT_A_GIT_WORKTREE`, `DOCS_BRAND_REPO_NOT_WRITEABLE`, `DOCS_BRAND_NOT_MKDOCS`, `DOCS_BRAND_NO_CODE_REPO`, `DOCS_BRAND_NOTHING_TO_APPLY` — and a Cancel at any of its prompts (Phases 3 through 6 each offer one) returns to the caller as `no branding applied: <reason>`, the reason being the stop's own ID and message or the prompt the operator cancelled at, with an **empty diff and no contrast finding**. Every one of those exits precedes Phase 8, so nothing was written and there is nothing to undo. `DOCS_BRAND_UNRESOLVED_BLOCKER` is not among them: it belongs to Phase 9's review gate, which an `--inline` run skips, and it fires only after Phase 8 has written. Under `--inline` the stop is *reported*, not *raised*: what the caller does with it is the caller's contract — `/docs-workflows:docs-init` Phase 5 continues its scaffold as if `--no-brand` had been passed and records the reason — and an API or CLI product with no frontend reaches `DOCS_BRAND_NOTHING_TO_APPLY` routinely, which must not cost anyone a scaffold. On a standalone run each stop ends the run exactly as written below.

---

## Phase 0 — Resolve and validate

**Strip the run flags first, standalone only — where `$ARGUMENTS` carries no `--inline` token.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS`: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. **`--inline` does not re-strip and inherits its caller's `run_flags` instead.** `/docs-workflows:docs-init` Phase 5 constructs this run's whole `$ARGUMENTS` explicitly — the resolved docs-repo root, `--from <path>` and `--inline` — from values it already holds, so that string never carries a run-flag token of its own to find; a fresh strip would resolve each flag to its env default, losing the caller's explicit flags. Instead this run reuses the `run_flags` record `/docs-init` already resolved at its own Phase 0, unchanged, for every step below that reads one.

0. **Flags.** Strip `--from <code-repo-path>` (together with the path token immediately after it) and `--inline` from `$ARGUMENTS` wherever they appear, before reading a positional token. Record `inline = true` when `--inline` was present, and `from_repo` when `--from` was. What remains is the optional `<docs-repo-path>`.

1. Execute **`resolve-docs-repo`** from `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §1 — the signal-positive form, since branding applies to a site that already exists. Do not restate its ladder here; the entry point owns it. Report which rung answered, per its own hard rule — a command that quietly works in an unexpected directory is expensive to unpick afterwards. Record the resolved absolute path as `<repo>`. **An `--inline` caller's positional token is this ladder's rung 1** — see the `--inline` contract above — so this ladder only ever runs its own independent search on a standalone invocation, or on an `--inline` caller that violated the contract.

2. **Validate the resolved repo is a writeable git work tree.** `git -C <repo> rev-parse --is-inside-work-tree` must print `true`; if it errors or prints anything else, stop: `DOCS_BRAND_NOT_A_GIT_WORKTREE: <repo> is not inside a git work tree.` `test -w <repo>` must succeed; if not, stop: `DOCS_BRAND_REPO_NOT_WRITEABLE: <repo> is not writeable.` Resolve and record the git root as `<repo-root>` (`git -C <repo> rev-parse --show-toplevel`). From here on, every git call this run makes in the docs repository runs as `git -C <repo-root>`, and the profile is read there, since `<repo-root>/.dev-workflows/docs-profile.yml` is its one home (`${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`, **Where the profile lives**). **The site's own files are not placed relative to `<repo-root>`**: a site can sit below it — a monorepo's `site/` — so step 3 finds the MkDocs configs, and every path this run reads or writes in the site derives from where each config sits and from its `docs_dir`.

3. **Find the MkDocs configs, and validate they have a Material theme to brand.** Where `<repo-root>/.dev-workflows/docs-profile.yml` exists and records `builds[]`, the configs are each entry's `config`, a path relative to `<repo-root>` (the schema's **Where the profile lives**). Otherwise they are those of `mkdocs.yml` and `mkdocs.internal.yml` that exist in `<repo>`. For every config found, read its **effective** `theme.name`: where the config carries `INHERIT: <parent>` and sets no `theme.name` of its own, it takes its parent's value, followed up the `INHERIT` chain to the config that inherits nothing — MkDocs' own merge, in which a child's keys override its parent's and an absent key is inherited, and in which `<parent>` is a path relative to the directory of the config that names it. Each effective value must read `material`. **Read the literal key and this command refuses the repository `/docs-workflows:docs-init` just scaffolded**: that command's `mkdocs.internal.yml` is `INHERIT: mkdocs.yml` with no `theme:` block of its own, by design (`${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/scaffold-tree.md` §6), and its Phase 5 runs this command `--inline` on exactly that tree. This is a config-file test, not a branch on the profile's `generator` field — see the D9 note below. No config found, or a found config whose effective `theme.name` reads anything but `material` → stop: `DOCS_BRAND_NOT_MKDOCS: <repo>'s MkDocs config does not resolve to theme: name: material (checked <each config path this step looked for>, following INHERIT). /docs-workflows:docs-brand writes Material-only palette options and --md-* CSS variable names — scaffold a Material site with /docs-workflows:docs-init first, or point this run at one that already has one.`

   **Where the site's files are.** For every config found, record its effective `docs_dir`: its own `docs_dir` key, else the one its `INHERIT` chain sets, else MkDocs' default `docs` — resolved against the directory of the config found, never of a parent that set it, which is how MkDocs resolves it for the config it builds. `extra_css`, `theme.logo` and `theme.favicon` name files relative to that directory, so Phase 8 writes the stylesheet and copies the assets under it. On a repository `/docs-workflows:docs-init` scaffolded, both configs sit at the top level and set no `docs_dir`, so it is `<repo-root>/docs` for both; on a site in a monorepo's `site/`, it is `site/docs`.

   **D9 exception, stated once.** D9 says nothing else in this family decides what to write into a repository from which generator it uses — every other consumer works through the profile's `commands.*`/`dev_servers.*` abstraction instead of the generator's own vocabulary. This command is the family's one exception: §7.2 requires writing generator-**native** theme configuration — `palette: primary: custom`, `--md-primary-fg-color` and its siblings — that no profile field abstracts, and `docs-profile-schema.md`'s own `generator` field states plainly that it is informational and no consumer branches on it (`docs-profile-schema.md` field rules) — this gate branches on a config value it is about to edit, never on that field, so it stays compatible with D9's rule rather than breaking it. The exception retires the day a profile field abstracts theme vocabulary the way `commands.*` already abstracts build and serve; until then this is the one place in the family that reads a repository's generator vocabulary **in order to decide what to write into it** beyond the profile, and it exists because a repo whose `mkdocs.yml` merely *exists* but names a different theme would silently receive an option that theme does not recognise. **Reading generator-native configuration at all is not the exception, and this paragraph used to say it was.** Two siblings do it without breaking D9, because neither decides what to write into the repository from what it reads: `/docs-workflows:docs-serve` reads an MkDocs config's `site_name` — its own key or its `INHERIT` parent's — to tell two servers apart when nothing else does, and `/docs-workflows:docs-profile` reads a generator's own config (an `astro.config.*` for `strictPort`, a docusaurus/mkdocs/eleventy/vitepress config for a port or a base path) to describe what it found. Neither writes generator-native configuration: `/docs-workflows:docs-profile` writes the profile, which is the abstraction D9 is about, and `/docs-workflows:docs-serve` writes no repository configuration at all — only its own state file, its server logs, one line in the repository's local git exclude file that keeps that state file out of `git status`, and, in `--build` mode, whatever the profile's build command writes. (`/docs-workflows:docs-init` names a generator too, but as the picker D9 appoints — it validates its own `--generator` argument and records the choice in the profile; it reads no repository's theme config, because it is the run that writes one.)

4. **`--inline` skips the rest of this phase.** The specs-repo preflight below runs for a standalone invocation only — an `--inline` run is a phase of a caller (`/docs-workflows:docs-init`) that already ran its own at its own Phase 0, and running a second one here would be ceremony over the same repo.

**Specs-repo preflight (standalone only).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git specs-preflight")` and execute its `specs-preflight` entry point (§3) inline: flush any leftover session artifacts from an earlier run, retry an artifact commit that failed to push, and settle the branch. This runs against `$SPECS_PATH` only — `git -C "$SPECS_PATH"`, never a `cd`, so the docs repo and the code repo this run reads are untouched (§1 rule 1). Prompt-free and silent when the specs repo is clean and on its default branch. If a guard fires, emit its §5 notice; if it returns `specs_git: blocked` (§3.3 G0), carry that flag for the whole run — the terminal `commit-artifacts` step skips on it. This family creates no branch of its own in `$SPECS_PATH` — its deliverable lives in the docs repo — so this preflight only ever settles a branch that already exists; it never switches onto one this run made.

---

## Phase 1 — Model routing

Invoke the `model-routing` skill (Skill tool, `skill: "workflows-core:model-routing"`), then classify the task.

`/docs-brand` is **MODERATE** — deterministic extraction against a fixed precedence order, applied through a small, templated diff (two MkDocs configs at most, one CSS file, a handful of copied assets). State the classification and a one-line reason.

**The review gate is Opus regardless of class, unless `run_flags.enforced_model` is set (§10, which pins the reviewer dispatch to the enforced id instead).** The family rule (D17, D20) is that every artefact-writing command of the docs-workflow family the 2026-08-29 design's §4 table lists (`/docs-init`, `/docs-brand`, `/docs-audit` and the artefact-writing commands that design plans after them — **not** every command in this plugin: `/document` in direct mode takes a style check and no review gate, `/release-notes` a light gate, `/docs-profile` no review gate at all, and `/docs-serve` writes no artefact and runs none) passes a high-tier review with no tiering by unit — a MODERATE classification lowers which model plans and executes, never which model reviews. Record a `model_routing` block:

```yaml
model_routing:
  classification: MODERATE
  reason: "deterministic extraction against a fixed precedence order; templated application"
  current_model: <the model this orchestrator is running under>
  enforced_model: <run_flags.enforced_model, or omit>   # §10: when set, every dispatched-step *_model below equals it (inline authoring_model / implementation_model keep the session model) and routing: bypassed
  defect_model: <§2.2 cheap chain — only under --skip-feedback; under §10, run_flags.enforced_model>
  detection_model: <§2.1 Sonnet chain: claude-sonnet-5, fallback claude-sonnet-4-6/4-5>   # impl-maintenance
  review_model: <the §2 Opus chain — claude-opus-5-5, fallback per §2 — pinned regardless of MODERATE classification, per D17/D20>
  opus_available: true | false
  notes: <any §2 degradation, e.g. "Opus unavailable; docs-scaffold-reviewer fell back to Sonnet 5">
```

Phase 9 dispatches `docs-scaffold-reviewer`, which is already pinned to Opus by its own frontmatter — no dispatch override is needed unless Opus is unavailable, or unless `run_flags.enforced_model` is set (§10), in which case the fallback or the enforced id is announced here and again in the final report. This block is computed on both paths, but on `--inline` neither `review_model` nor `detection_model` reaches a dispatch this command makes itself — Phase 9 (the reviewer) and Phase 12 (`impl-maintenance`) are both standalone-only, so the block is inert there, carried along for whoever reads it rather than acted on.

---

## Phase 2 — Resolve the code repo to extract from

Resolve **one** code repository to read from, in order:

1. **`--from <code-repo-path>`**, when given. Taken as given — the operator (or, on `--inline`, the caller) named it. An `--inline` caller is expected to pass this explicitly, reusing the code repo `/docs-workflows:docs-init` already resolved in its own Phase 2; the rungs below still apply for a standalone run or an `--inline` caller that omits it.
2. **Else the resolved docs-profile's recorded source-repo set** — `source_repos[]` in `<repo-root>/.dev-workflows/docs-profile.yml` (Phase 0 step 2, when a profile was found). `/docs-init` writes that key from the set it confirmed, and `/docs-audit` writes it where it was absent, so on a portal either of them touched this rung usually answers. **Resolve each entry by `${CLAUDE_PLUGIN_ROOT}/references/docs-profiles/docs-profile-schema.md`'s own order — `path`, else `origin` matched against the clones under `${REPOS_PATH:-/workspace}`, else ask — never by `name`, which is a label.** Then:
   - **No profile, no `source_repos[]` key, or an empty one** — this rung passes through to rung 3, which is the ordinary case for a repository profiled by `/docs-profile`.
   - **Exactly one entry that resolves** — take it, with a one-line notice naming it and saying the profile supplied it.
   - **More than one** — this command extracts from **one** repository, so pick among the resolved entries using rung 3's picker exactly as written below, over the recorded entries in place of the `${REPOS_PATH:-/workspace}` listing. The ladder is not restated here; a second copy of an arity rule is a second thing to keep in step.
   - **An entry that resolves to nothing on this machine** — name it and say which of `path` and `origin` failed, then carry on with the rest. That is the schema's *reported, never silently dropped* rule, and it matters here for the same reason it matters there: a run that quietly skipped the one recorded repository would extract a brand from whatever rung 3 happened to find and never say so.
3. **Else `ls ${REPOS_PATH:-/workspace}`, one level deep, and confirm with the operator.** The listing is unbounded, so apply `workflows-core:epic-picker`'s pattern (`Skill(skill: "workflows-core:reference", args: "epic-picker")`) rather than rendering one option per entry — the same shape `/docs-workflows:docs-serve`'s own Phase 1 step 3 already uses for an unbounded servable-space list. Print every candidate directory as prose above the prompt, one line each, then:
   - **Exactly one candidate** — no picker; auto-select it, with a one-line notice naming it, per `epic-picker`'s own "auto-select at one" rule — never a one-option `choices:` array, which is below the harness's `minItems: 2`.
   - **Two or three candidates** — the array carries them all: `choices: ["<repo-1> (Recommended)", "<repo-2>", "<repo-3>"]` (2 or 3 options, matching however many are recorded).
   - **Four or more candidates** — the array carries the first three plus the overflow option: `choices: ["<repo-1> (Recommended)", "<repo-2>", "<repo-3>", "Another repo from the list above — name it"]`.

   The typed answer is resolved against the directory names just printed — never parsed out of the free text.

Nothing resolves and the operator declines to name one → stop: `DOCS_BRAND_NO_CODE_REPO: no code repository resolved to extract from (checked --from, the docs profile's source-repo set, and ${REPOS_PATH:-/workspace}). Pass --from <path> explicitly, or mount the product's code repo under $REPOS_PATH.`

Validate the resolved code repo is readable (`test -r <repo>`). It is read **only** — nothing in this run writes into it, and the docs build never reaches into it at build time (Phase 8 step 3).

---

## Phase 3 — Extract colour

Walk this precedence in order; **first hit wins, and the source — file and line — is recorded with it.** Exclude `node_modules/`, `dist/`, `build/`, `vendor/`, and `.git/` from every search below.

1. **Tailwind config `theme.extend.colors`.** `Glob` for `tailwind.config.{js,ts,cjs,mjs}` (repo root, then one level deep). Read `theme.extend.colors`; take the `primary` key if present, else `brand`, else the first key whose name is not one of Tailwind's own neutral-family names (`gray`, `grey`, `slate`, `zinc`, `neutral`, `stone`). A shade object (`{50: …, 500: '#…', 900: …}`) takes its `500` shade — Tailwind's own "base" convention; a flat string value is used as-is.
2. **CSS custom properties matching `--(color-)?(primary|brand|accent)`.** `Grep` `**/*.css` for the pattern with a hex value (e.g. `--primary: #1565C0;`, `--color-brand: #1565c0;`). The first match, by file path, wins.
3. **A MUI `createTheme({ palette: { primary, secondary } })` call.** `Grep` `**/*.{js,jsx,ts,tsx}` for `createTheme(` calls carrying a `palette:` block; extract `primary.main`.
4. **`manifest.json` / `site.webmanifest` `theme_color`.** `Glob` for either filename; read the `theme_color` field.
5. **SCSS/LESS variables matching `$(primary|brand|accent)`.** `Grep` `**/*.scss`, `**/*.less` for `$primary:` / `$brand:` / `$accent:` assignments carrying a hex value.

**Accent is extracted independently**, by the same three rules that name it explicitly — CSS custom properties' `accent` group (rule 2), MUI's `secondary.main` (rule 3), and SCSS/LESS's `$accent` (rule 5) — walked in that order, regardless of which rule supplied the primary. **No explicit accent source found → accent defaults to the primary value.** This is never a silent substitution: Phase 5 confirms it like any extracted value, and states plainly that it is a default rather than a find.

**Light and dark variants are derived from the confirmed primary**, never from accent (the source supplies only one primary value in the ordinary case, per the design's own §7.2): convert to HSL, lift lightness by 15 percentage points (capped at 95%) for the light variant and drop it by 15 points (floored at 10%) for the dark variant, then convert back to hex. State the formula in the report; it is arithmetic, not a design choice, so a reader can check it the way `contrast.md` §2's own worked example is meant to be checked.

**No colour source matches any of the five rules** → ask:
```
"No brand colour was found in <code-repo> (checked Tailwind config, CSS custom properties, a MUI theme, manifest theme_color, and SCSS/LESS variables). How should I proceed?"
choices: ["Enter a primary colour myself", "Skip colour branding — logo only", "Cancel"]
```

---

## Phase 4 — Extract logo

Search, in this order, for logo candidates: `public/`, `src/assets/`, `static/`, any file matching `logo*`, `brand*`, or `icon*`, any `favicon.*`, and every entry of a found manifest's `icons[]`. Exclude the same four directories Phase 3 excludes.

Rank every candidate found **SVG over PNG over any other format, and — within one format — larger over smaller** (`wc -c`). This picker is the one place a logo is chosen from among the candidates — Phase 5 confirms whatever it settles on and never re-offers the alternatives, though its **Edit a value before applying** takes a typed path in place of it:

- **Exactly one candidate** — no picker; carry it forward as the proposal, with a one-line notice naming it, per `epic-picker`'s own "auto-select at one" rule.
- **Two or three candidates** — print each as prose above the prompt (path, format, size), then offer them literally: `choices: ["<candidate-1> — <format>, <size> (Recommended — ranks first)", "<candidate-2> — <format>, <size>", "<candidate-3> — <format>, <size>"]`.
- **Four or more candidates** — the same prose listing, capped per `workflows-core:epic-picker` *The cap*: `choices: ["<candidate-1> — <format>, <size> (Recommended — ranks first)", "<candidate-2> — <format>, <size>", "<candidate-3> — <format>, <size>", "Another candidate from the list above — name it"]`.

The typed answer is resolved against the candidates just printed — never parsed out of the free text.

**No logo candidate found** → ask:
```
"No logo was found in <code-repo> (checked public/, src/assets/, static/, logo*/brand*/icon* filenames, favicon.*, and manifest icons[]). How should I proceed?"
choices: ["Enter a logo path myself", "Skip logo — colour only", "Cancel"]
```

**Both colour and logo end up absent or declined** → stop: `DOCS_BRAND_NOTHING_TO_APPLY: no colour and no logo to apply — Phase 3 and Phase 4 both came back empty or declined. There is nothing for this run to brand.`

---

## Phase 5 — Confirm (never applies silently)

Print every value Phases 3–4 settled on, each with the file and line (or path) it came from — and, for a defaulted accent or a manually entered value, say plainly that it was defaulted or entered rather than found. Then confirm:

```
"Extracted from <code-repo>:
  primary: #1565C0  (tailwind.config.js:12, theme.extend.colors.primary)
  accent:  #1565C0  (defaulted from primary — no --accent / secondary.main / $accent found)
  logo:    src/assets/logo.svg  (296 KB, ranked over 2 smaller PNG candidates)
Apply these to <docs-repo>?"
choices: ["Apply as shown (Recommended)", "Edit a value before applying", "Cancel"]
```

"Edit a value" re-asks per value as free text — the harness's own escape — and the typed answer becomes the new value rather than being parsed out of anything. A wrong brand colour applied quietly is worse than no branding, which is the whole reason this phase exists as its own step rather than folding confirmation into Phase 8.

---

## Phase 6 — Contrast check

Execute **the thresholds**, **the formula**, and **the adjudication** from `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/contrast.md` — do not restate them here; the file exists precisely so this command and any later image-contrast check share one copy.

Check every derived colour against `#FFFFFF`, the scaffold's one light background — the scaffold declares no dark colour scheme, so there is no second background to check: the confirmed **primary**, its derived **primary-light** and **primary-dark**, and the confirmed **accent** (accent carries no derived variant — Phase 3 derives light/dark from primary only). All four are checked against `contrast.md` §1's **body-text row** — a docs-site primary/accent pair, and the light/dark variants that share its role, are read as text (link colour, header titles), not merely a decorative fill. Report each ratio to two decimal places.

For each colour that **fails**:
```
"<label> #<hex> on white measures <ratio>:1 against contrast.md §1's body-text minimum — it will read as low-contrast text. Apply it anyway?"
choices: ["Apply anyway — it's the brand", "Choose a different value", "Cancel"]
```

A confirmed failing colour is **still applied** — never silently corrected — and the finding (the ratio, the pair, the criterion) is carried into the Phase 10 PR message and the Phase 11 report. A **passing** colour produces no prompt at all — it is applied without a confirmation — but its ratio is still reported beside the failing ones, in the PR message and in the report, because the number is the interface (`contrast.md` §2, §3). Where Phase 3 ended in "Skip colour branding — logo only", there is no colour to check: record that in place of the four ratios rather than reporting a pass.

---

## Phase 7 — Branch (standalone only)

**`--inline` creates no branch of its own.** It writes into the caller's branch — `/docs-workflows:docs-init` creates it at its own Phase 2.5, **before** its Phase 3 writes anything, and its Phase 8 commits and drafts the pull request; that command owns the branch's whole lifecycle, and this run never switches, creates, or otherwise touches git here. Skip to Phase 8.

**Standalone** creates the branch here, **before Phase 8 writes anything** — the family invariant that a branch is created before any file is touched, and the same order `/docs-workflows:docs-profile`'s own Phase 5 uses (branch at step 2, write at step 3):

1. **Resolve the branch name.** When the resolved `.dev-workflows/docs-profile.yml` carries `branch_naming.pattern`, fill its placeholders — the identity placeholder from `Skill(skill: "workflows-core:reference", args: "branch-naming")` §2's ladder, and the issue-key segment takes that pattern's documented no-issue literal, since branding has no ticket. Otherwise use `<prefix>/NOISSUE-docs-brand`, `<prefix>` from the same §2 ladder, fallback `docs/`. Always confirm the final name: `choices: ["Use proposed branch <name> (Recommended)", "Edit the name"]`.
2. **Prepare the working tree.** `git -C <repo-root> status --porcelain`; nothing of this run has written anything yet, so a non-empty result here genuinely is pre-existing dirt: `choices: ["Stash changes and continue (Recommended)", "Proceed anyway — pre-existing changes will appear in the diff", "Cancel"]`. Base the branch on the repo's default branch. `<base>` is that branch's **name**, never its `origin/<name>` ref, which `git switch` refuses: resolve it by `workflows-core:read-only-repos` §3's chain, run against `<repo-root>`, and its **A switch takes the name** rule — rung 1 prints `origin/<name>` and `<base>` is what follows `origin/`; where rung 1 fails — `origin/HEAD` unset, or naming a ref that no longer exists (§3 rung 1) — `<base>` is the literal `main` or `master` whose ref rungs 2–3 find. Then `git -C <repo-root> switch <base>` + `git -C <repo-root> pull --ff-only`. Where the chain is exhausted — no `origin`, or one holding neither branch — this command's own fallback applies: `<base>` is the local `main`, then `master`, whichever `git -C <repo-root> rev-parse --verify --quiet refs/heads/<name> >/dev/null` finds, switched to without the pull, there being no remote branch to bring it up to; with neither, `<base>` is the branch HEAD is on and nothing is switched. Then create the branch (`git -C <repo-root> switch -c <name>`, or `git -C <repo-root> switch <name>` if it already exists).

**Cancel here ends the standalone run with nothing written and nothing committed.** Skip Phase 8 (Apply), Phase 9 (Review gate), and Phase 10 (Finish) entirely — there is nothing to write, review, or commit — and go straight to Phase 11's report, which states plainly that Phase 7 was cancelled. The emitter tail (Phases 12–14) still runs regardless, so this run's cost and any feedback are still recorded.

---

## Phase 8 — Apply

Nothing in this phase touches the code repo — every write below lands only in the resolved docs repo, on the branch Phase 7 created (standalone) or the caller's own branch (`--inline`), and logo assets are **copied**, never linked, so the docs build never reaches into the code repo at build time.

1. **Theme block — written only into a config that inherits nothing.** For each config Phase 0 step 3 found, the write target is the config at the top of its `INHERIT` chain — the one that inherits nothing, which is the config itself where it carries no `INHERIT:` key, and the same chain Phase 0 step 3 followed. On a repository `/docs-workflows:docs-init` scaffolded, both chains end at `mkdocs.yml`, so that is the one file written. **A config carrying `INHERIT:` receives nothing**, because it already takes `theme` and `extra_css` from its parent through MkDocs' merge, and a `theme` block of its own there is exactly the divergent-theme defect `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/scaffold-tree.md` §6 names: the inherited value would be silently overridden, and the two builds would differ in their content source from the first edit someone makes to one block and not the other. Into each write target, set:
   ```yaml
   theme:
     palette:            # only when Phase 5 confirmed a colour
       primary: custom
       accent: custom
     logo: assets/<logo-filename>          # only when Phase 5 confirmed a logo
     favicon: assets/<favicon-filename>    # only when Phase 5 confirmed a logo
   extra_css:            # only when Phase 5 confirmed a colour — it loads step 2's block
     - stylesheets/extra.css
   ```
   **Write each key only for what this run is actually applying.** `palette` and the `extra_css` entry go in only when a colour was confirmed, and `logo` and `favicon` only when a logo was — step 3 is what puts those files under `assets/` in the site's `docs_dir`, and a key naming a file nothing wrote is a broken reference the build carries silently. `/docs-workflows:docs-init`'s scaffold writes neither key for that reason (`scaffold-tree.md` §5), so on a scaffolded repository this step is where they first appear. **Edit into the existing block — never a literal replacement.** Phase 0 step 3 already confirmed the effective `theme.name` is `material`; preserve it, and preserve any existing `features:` list or other `theme:` sub-keys untouched, adding only the keys above (and merging into `extra_css:` if it already lists other files, rather than overwriting the list). A literal replacement of the whole `theme:` key would silently drop `name: material` itself, and the brand would then do nothing — exactly the failure Phase 0 step 3 exists to prevent, reintroduced one step later by a careless write.
   Where **two** configs were found and **neither** inherits — a hand-built two-config site — both are write targets and receive the **same** block, which is what keeps their `theme` and `extra_css` identical (`docs-scaffold-reviewer` dimension 2, build-config parity). Named Material for MkDocs palette colours do not accept hex values, which is the thing that silently does nothing if this step is skipped: `primary: custom` / `accent: custom` is what makes the CSS variables below take effect at all.
2. **CSS variables — only when Phase 5 confirmed a colour.** Create `stylesheets/extra.css` under the effective `docs_dir` Phase 0 step 3 recorded — under each, where the configs found record more than one — if it does not already exist (a repo `/docs-workflows:docs-init` scaffolded has `docs/stylesheets/extra.css`); write or update a block:
   ```css
   :root > * {
     --md-primary-fg-color:        #<primary>;
     --md-primary-fg-color--light: #<primary-light>;
     --md-primary-fg-color--dark:  #<primary-dark>;
     --md-accent-fg-color:         #<accent>;
   }
   ```
   Hand edits below this block are preserved; only this block is replaced on a re-run — `scaffold-tree.md` §3.13 already names this file as what a later rebrand reconciles.
3. **Assets — only when Phase 5 confirmed a logo.** Copy the confirmed logo (and a favicon, when the source is distinguishable from the logo — e.g. a dedicated `favicon.*` candidate — else the logo doubles as both) into `assets/` under the effective `docs_dir` Phase 0 step 3 recorded — under each, where there is more than one; `docs/assets/` on a scaffolded repo — overwriting the same filename on a re-run rather than adding a new one beside it. This is D16's `in-repo` overwrite-in-place rule, applied here unconditionally: a logo is a persistent brand asset rather than a documentation screenshot on a churn lifecycle, so this step does not read the profile's `images.policy` at all — the design's own §7.3 names `docs/assets/` directly, with no policy branch.

---

## Phase 9 — Review gate (standalone only)

**`--inline` skips this phase entirely.** Its diff and its Phase 6 contrast finding are contributed to the caller's own review instead — the design's own §7.4 states this directly: "an `--inline` run from `/docs-init` contributes its diff to that command's Phase 7.5 review rather than running a second one." Everything below is the standalone path.

Dispatch `docs-scaffold-reviewer` — pinned to Opus by its own frontmatter, per Phase 1:

→ Agent (subagent_type: "docs-workflows:docs-scaffold-reviewer", model: `<review_model — §2 Opus chain, equal to docs-scaffold-reviewer's frontmatter pin; under §10, run_flags.enforced_model>`):  # recorded in model_routing as review_model above, frontmatter-pinned, no override added unless §10 enforces a model
  > "Review the documentation-repository scaffold changes from this brief:
  >
  > Task description: [/docs-brand standalone run — theme colours and a logo extracted from <code-repo> and applied to <docs-repo>]
  > Written file paths: [absolute paths of every file Phase 8 wrote: the config(s) that inherit nothing and so received the theme block — never an INHERIT-ing config, which Phase 8 leaves untouched by design — stylesheets/extra.css under each docs_dir Phase 0 step 3 recorded where a colour was applied, and every copied asset under its assets/ where a logo was]
  > docs_tree: [Glob ** under each docs_dir Phase 0 step 3 recorded]
  > profile: [the resolved .dev-workflows/docs-profile.yml, or 'absent — this repo carries no profile; images.policy/root/max_bytes defaults assumed (in-repo, docs/assets, 307200)' when none exists]"

**Triage before applying anything** — invoke `Skill(skill: "workflows-core:reference", args: "finding-triage")` and follow it: for each finding, verify its claimed consequence at the location it names; keep or dismiss with a reason that disposes of that finding's own claim; carry survivors only into the next step, and every dismissal into the Phase 11 report. Where triage empties the survivor set entirely on a non-PASS verdict, follow the reference's own disposition — surface it and let the operator settle the verdict; never silently promote it to PASS.

**There is no dedicated fixer for this diff (D17, D25) — the orchestrator applies survivors itself**, editing the named file directly, bound by `finding-triage.md`'s patch gate: fix only a defect a finding actually demonstrated, never guard state it did not show. A survivor whose fix is not a safe mechanical patch is surfaced rather than guessed at:
```
"docs-scaffold-reviewer flagged <finding> as <SEVERITY>, and the fix isn't a safe mechanical patch: <why>. How should I proceed?"
choices: ["Describe the fix yourself — I'll apply it", "Defer — note it in the report, run continues", "Override — accept the finding as-is", "Cancel this run"]
```
A **BLOCKER** left deferred (neither fixed nor overridden) stops the run before Phase 10: `DOCS_BRAND_UNRESOLVED_BLOCKER: a BLOCKER finding from docs-scaffold-reviewer was neither fixed nor overridden — resolve it and re-run.` A BLOCKER that is fixed, or explicitly overridden by the operator, proceeds. MAJOR survivors are applied the same way; MINOR / NIT are deferred to the report without a prompt.

There is no re-review cycle — with no fixer, there is no second pass to gate against: the orchestrator's direct edit is the fix, applied against the same finding it answers, and Phase 10 proceeds once every BLOCKER survivor is resolved or overridden.

---

## Phase 10 — Finish

**`--inline` returns here instead of running any of this** — or, where it stopped or was cancelled earlier, returned already with `no branding applied: <reason>` under the `--inline` failure contract above. Its diff (Phase 8) and its contrast finding (Phase 6) are returned to the caller — `/docs-workflows:docs-init` branched at its Phase 2.5 before any of this ran, and its Phase 8 commits and drafts the single pull request for the whole scaffold, this diff included. Nothing below runs on `--inline`: no commit, no PR, and — see Phases 12–14 — no emitter tail. **A standalone run that cancelled at Phase 7 never reaches this phase either** — see Phase 7's cancel path, which jumps straight to Phase 11.

**Standalone** commits what Phase 7's branch and Phase 8's writes produced, then drafts a PR message — **never push, never merge**:

1. **Ignore test, then commit.** Immediately before staging, run `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/scaffold-tree.md` §7's commit-time ignore test over the files Phase 8 wrote and Phase 9 edited. A docs repository's own `.gitignore` may ignore an image or a stylesheet (`*.svg`, `*.css`): such a path is left unstaged, never force-added, and the config key naming it — `theme.logo`, `theme.favicon` or the `extra_css` entry — is removed first, so the committed config never names a file the commit leaves out. Then `git -C <repo-root> add` — only the remaining files Phase 8 wrote or Phase 9 edited — and `git -C <repo-root> commit -m "docs: apply brand colours and logo (docs-brand)"`.
2. **Draft the PR message.** Detect the host (`git -C <repo-root> remote get-url origin`); draft a copy-paste-ready title + body for Bitbucket or GitHub. The body states the extracted values and their sources (Phase 5), the review verdict and every applied or dismissed finding (Phase 9), any written path step 1 left uncommitted (the path, the ignoring `.gitignore` line with its number, and the config key removed for it), and — **always, whether it passed or failed** — the Phase 6 contrast findings, so a reviewer sees a confirmed-failing colour before it ships. **Do not push, do not open the PR via any CLI** — present the branch name and the drafted message for the operator to push and open themselves.

---

## Phase 11 — Report

**`--inline` reports nothing of its own** — control returns to `/docs-workflows:docs-init`, whose Phase 8.5 produces the consolidated report; this run returns straight to Phase 6's contrast finding and Phase 8's diff, no report of its own.

**Standalone** produces:

```
## Docs-brand Report

### Classification
MODERATE — deterministic extraction against a fixed precedence order; templated application (review gate is Opus regardless, D17/D20, unless run_flags.enforced_model is set — §10)

### Model Routing
Detection model (§2.1): <detection_model>   Review model (§2): <review_model>   Notes: <any §2 fallback, or "none">
Opus available: <true | false>
[Under `run_flags.enforced_model`: `Model routing: bypassed — enforced <id> (flag|env)` in place of the Detection model / Review model line above — both dispatched steps already carry the enforced id, per `workflows-core:model-routing/classification` §10. `Opus available` is unaffected by enforcement (§10: a property of the environment, not of the enforcement choice) and is reported on its own line exactly as it stands.]
Run flags: [the `Run flags: …` line, repeated, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — omit this line otherwise. The `Session feedback: …` skip line is Phase 12's own output; the `Session cost: …` skip line is Phase 14's own output, printed after this report and not restated in it.]

### Source
Code repo: <resolved path>
Docs repo: <resolved path>  (resolved via: <which resolve-docs-repo rung answered>)

### Extracted
- primary: #<hex>  (<source file:line, or "entered manually", or "unchanged — declined to edit">)
- accent:  #<hex>  (<source file:line, or "defaulted from primary">)
- primary-light / primary-dark: #<hex> / #<hex>  (derived, HSL lightness ±15 points)
- logo: <path>  (<why it ranked first, or "entered manually">)
- favicon: <path | "reused the logo">

### Contrast
- primary        vs #FFFFFF: <ratio>:1 — <PASS | FAIL, applied anyway — operator confirmed | FAIL, not applied>
- primary-light  vs #FFFFFF: <ratio>:1 — <PASS | FAIL, applied anyway — operator confirmed | FAIL, not applied>
- primary-dark   vs #FFFFFF: <ratio>:1 — <PASS | FAIL, applied anyway — operator confirmed | FAIL, not applied>
- accent         vs #FFFFFF: <ratio>:1 — <PASS | FAIL, applied anyway — operator confirmed | FAIL, not applied>
(When colour branding was skipped — "logo only" — this section reads instead: "no colour applied — nothing to check.")

### Review
Verdict: <PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | "N/A — cancelled at Phase 7, never reached">
Findings: <N reviewed, M survived triage, K applied, J deferred or overridden with reason | "N/A">

### Branch
<branch name — N commit(s), NOT pushed and NOT merged | "cancelled at Phase 7 — no branch created, nothing written or committed">
Left uncommitted: <"none" | <path> — ignored by .gitignore:<N> `<line>`; config key removed: <key> — the committed config differs from the reviewed one by exactly that key>

### PR draft (copy-paste)
**Title:** <title>

<body>

(When Phase 7 was cancelled, this whole section reads instead: "none — no branch exists to open a pull request against.")

### Next step
[per `workflows-core:next-phase-offer` — guidance only, never auto-invoked. **When a branch and a drafted PR exist:** once the drafted pull request above is pushed and merged, `/docs-workflows:docs-serve` previews the branded site. This offer carries no `<merge-clause>` — the pull request this run drafted targets the docs repo, not `$SPECS_PATH`, and this family creates no `$SPECS_PATH` branch of its own and runs neither `handoff-to-main` nor `require-on-main` against a docs-repo PR, so there is no downstream gate to name a clause against — the same reasoning `/docs-workflows:docs-serve`'s own closing section gives for the same omission. **When Phase 7 was cancelled (no branch, no PR):** state that plainly — nothing to preview or merge — and stop there.]
```

---

## Phase 12 — Session maintenance & feedback (standalone only)

**`--inline` skips this phase and everything after it** — the caller's own emitter tail covers the whole run, this diff included.

Terminal phase — runs AFTER the Phase 11 report; NEVER interrupts an earlier phase.

**Under `run_flags.skip_feedback`** (`workflows-core:run-flags` §4), dispatch `workflows-core:defect-reporter` instead of `impl-maintenance` in step 1, with the same handoff plus `Plugin root: ${CLAUDE_PLUGIN_ROOT}` (literal — it expands in command bodies to this command's own plugin location), and `model: <§2.2 cheap chain, or run_flags.enforced_model>`; if it returns at least one defect, persist them with `emit-bugs` (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`, otherwise load nothing. Surface `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` in place of step 3's persisted-path line. Capture-at-block (`emit-block`) is unaffected by the flag.

1. **Invoke `impl-maintenance`** (subagent_type: "workflows-core:impl-maintenance", model: `<Sonnet detection chain — claude-sonnet-5, fallback claude-sonnet-4-6 / 4-5; under §10, run_flags.enforced_model>`):
   > "Analyse this session and return a Lessons Learned report.
   >
   > Session handoff:
   > - Command run: /docs-brand
   > - What was done: [one-paragraph summary — colour/logo extracted from <code-repo>, applied to <docs-repo>, contrast passed or applied over a finding, or cancelled at Phase 7 with nothing written]
   > - Key events: [a failing contrast confirmed anyway, a defaulted accent, a manually entered value, a deferred or overridden review finding, a Phase 7 cancellation — or 'none']
   > - Workarounds used: [manual steps not automated by the workflow — or 'none']
   > - Review verdict: [PASS | PASS WITH RECOMMENDATIONS | BLOCK, resolved | N/A — cancelled before Phase 9]
   > - Test result: N/A (no tests in /docs-brand)
   > - Project root: [the resolved docs repo root]"
2. **Persist plugin feedback (automatic).** Invoke `Skill(skill: "workflows-core:reference", args: "feedback-emission emit-auto")` and call its `emit-auto` entry point (§6), passing the Lessons Learned report, `command: /docs-brand`, `key: null` (this run resolves no PRD/Epic key), `source: none`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). With no PRD dir to match, `feedback-emission.md` §2 tier 2's **documentation branch** — which names this command's standalone path explicitly — applies: the entry lands at `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/feedback/<date>.md` — `<docs-repo-slug>` being the one-segment name `workflows-core:specs-repo-git` §2.1 defines — filed against the docs repo rather than unfiled at the specs-repo root, because that repository is this family's unit of attribution (design D19).
3. **Surface** the persisted path (or "no plugin-facing signal — nothing persisted") as this phase's only output.

ADDITIVE — this phase NEVER fails the run, NEVER commits, NEVER makes an external API call, and NEVER writes into a docs repo, a code repo, or the current working directory, where it is not the specs repository.

---

## Phase 13 — Emit follow-up tasks (standalone only)

Terminal phase — runs AFTER Phase 11 and Phase 12; NEVER interrupts an earlier phase. Invoke `Skill(skill: "workflows-core:reference", args: "followup-emission")` and execute its steps inline.

1. **Collect** the qualifying follow-ups: the mandatory manual step ("push `<branch>` and open the pull request" — only when Phase 10 reached), and any deferred or overridden review finding from Phase 9.
2. **Filter** them with the reference's §6 qualifying predicate.
3. This run resolves **no PRD or Epic folder** — `followup-emission.md` §2's "no folder resolved" rung applies: report-only, kept in the Phase 11 report, with the one-line notice `⚠ No resolved folder — N follow-up(s) kept in this report only.`

ADDITIVE — this phase NEVER fails the run, NEVER commits, and NEVER writes into a docs repo, a code repo, or the current working directory, where it is not the specs repository.

---

## Phase 14 — Session cost (standalone only)

Terminal phase — the final operational phase; runs after Phase 13 and NEVER interrupts an earlier phase. Records this command's token-cost contribution — through `emit-cost`, or, under `run_flags.skip_costs`, by advancing the checkpoint alone. **Cost ALWAYS runs on the standalone path — including a run that cancelled at Phase 7 — unless `run_flags.skip_costs` (see below).**

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The resume-pointer write and the terminal `commit-artifacts` step below run unchanged either way.

Otherwise (not skipping), invoke `Skill(skill: "workflows-core:reference", args: "cost-emission emit-cost")` and call `emit-cost` with `command: /docs-brand`, `phase: docs-scaffold`, `role: dev` — a **fixed** pair (`workflows-core:cost-emission` §7), never `inferred`. **Only the standalone path emits.** An `--inline` run's cost belongs to `/docs-workflows:docs-init`'s own entry; emitting a second time would double-count one run, which is exactly why Phases 12–14 are skipped there rather than run with a key-less variant of the same call. Pass `key: null`, `source: none`, and `plugin_version` (read from `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`). With no PRD dir, `cost-emission.md` §8 rung 2's **documentation branch** — which names this command's standalone path explicitly — applies: the entry lands at `$SPECS_PATH/documentation/<docs-repo-slug>/dev-workflows/cost/<sid8>.md`, where `<docs-repo-slug>` is the one-segment name `workflows-core:specs-repo-git` §2.1 defines for the resolved docs repo — cited rather than re-derived here, because that section's staging rule admits exactly one segment and a second derivation is how the two drift (design D19). That rung is inserted before pending precisely because documentation work on a docs repo alone frequently has no PRD and never will, so a pending entry from it would await a reconciliation that is never coming; the pending file (§9) is now only for a genuinely keyless run that may still acquire a key. `specs-repo-git.md` §2.1's `$SPECS_PATH/documentation/<docs-repo-slug>/…` shape is what stages it.

**Then write the resume pointer.** Invoke `Skill(skill: "workflows-core:reference", args: "session-hygiene")` §1. With no PRD dir, rung 2 applies: skip the file, rely on the printed `### Next step`.

**Then commit session artifacts (terminal).** Invoke `Skill(skill: "workflows-core:reference", args: "specs-repo-git commit-artifacts")` and execute its `commit-artifacts` entry point (§4) inline — the LAST action of the run. It stages ONLY the §2.1 bounded artifact paths inside `$SPECS_PATH` (here: the documentation-run feedback and cost files above, under §2.1's `$SPECS_PATH/documentation/<docs-repo-slug>/…` shape), commits, and pushes per §4 step 5. It NEVER touches the docs repo or the code repo; NEVER force-pushes; NEVER fails the run; and skips entirely when the run carries `specs_git: blocked` (§3.3 G0), re-emitting that notice. Print its §6 outcome line here, as the run's last output — prefixed `Specs repo:`, with any guard notice repeated in full.

---

## Invariants (always enforced)

- ALWAYS resolve the docs repo via `resolve-docs-repo` (`${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/repo-resolution.md` §1) and report which rung answered
- ALWAYS validate that every MkDocs config Phase 0 step 3 finds resolves to an **effective** `theme.name: material` — `INHERIT` followed, so an inheriting config takes its parent's value — before doing anything else (Phase 0 step 3); the family's one D9 exception — the one command whose write into the repository, beyond the profile, is decided by generator-native configuration it read (`/docs-workflows:docs-profile` reads it too, and writes only the profile, which is the abstraction D9 is about — Phase 0 step 3), since Phase 8 writes Material-only configuration no profile field abstracts; never a branch on the profile's `generator` field itself, and never a literal-key read that refuses the inheriting `mkdocs.internal.yml` `/docs-workflows:docs-init` scaffolds
- ALWAYS create the branch (standalone only, Phase 7) before Phase 8 writes anything — never the other way around
- ALWAYS print every extracted value with its file and line (or path) and confirm before applying it (Phase 5) — NEVER applies silently
- ALWAYS check every derived colour (primary, primary-light, primary-dark, accent) against `${CLAUDE_PLUGIN_ROOT}/references/docs-workflow/contrast.md`'s thresholds, report each ratio to two decimals, and carry a failing finding into the PR message and the report — NEVER silently accept and NEVER silently correct a failing colour; it IS still applied if the operator confirms
- ALWAYS copy logo/favicon assets into `assets/` under the site's `docs_dir` (`docs/assets/` on the default layout); NEVER reference the code repo by path from the docs build
- ALWAYS find the MkDocs configs through the profile's `builds[]` where it records one, else in the resolved directory, and derive every path in the site — the configs followed through `INHERIT`, the stylesheet, the assets — from where each config sits and its `docs_dir`, never from the git top level, where the profile is read and every git call in the docs repository runs (Phase 0 steps 2–3)
- ALWAYS write `theme` and `extra_css` only into a config that inherits nothing, NEVER into one carrying `INHERIT:` — it already takes both from its parent, and a block of its own there is the divergent-theme defect (`scaffold-tree.md` §6); where two configs both inherit nothing, write the same block into both. ALWAYS edit into the existing `theme:` block rather than replacing it — a literal replacement drops `name: material` and the brand silently does nothing — and write `palette`/`extra_css` only for a confirmed colour and `logo`/`favicon` only for a confirmed logo
- NEVER let an `--inline` run's stop or Cancel end the caller's run — it returns `no branding applied: <reason>` with an empty diff and no contrast finding (the `--inline` failure contract, above)
- ALWAYS dispatch `docs-scaffold-reviewer` at Opus for a standalone run (D17, D20 — no tiering by unit) unless `run_flags.enforced_model` is set (§10 enforces a model, and the dispatch then carries that id instead); NEVER for `--inline`, whose diff joins the caller's own review instead
- ALWAYS triage `docs-scaffold-reviewer`'s findings (`workflows-core:finding-triage`) before applying anything; there is NO dedicated fixer (D25) — the orchestrator applies survivors itself, bound by the patch gate, and surfaces a survivor it cannot safely patch rather than guessing
- ALWAYS use `choices` arrays for a genuine decision point; 2–4 options, and NEVER author an "Other" option — the harness supplies the free-text escape itself. Where the candidate set is unbounded (Phase 2's repo listing, Phase 4's logo listing) the array is never sized to the list itself: a single candidate is auto-selected with a notice, never offered as a one-option array; otherwise print every candidate as prose first, then cap at three concrete rows plus one overflow option, per `workflows-core:epic-picker` *The cap*
- ALWAYS run `specs-preflight` at Phase 0 (standalone only) and `commit-artifacts` as the last action (standalone only) (`workflows-core:specs-repo-git`) — bounded to `$SPECS_PATH`'s artifact paths and to plugin-created branches, of which this family creates none; always `git -C "$SPECS_PATH"` and never a `cd`; never force-pushing; never failing the run
- NEVER push or auto-merge the docs-repo branch — output a reviewable PR (branch + commit + drafted message) for the operator to push, the same discipline as `/docs-workflows:docs-profile`
- NEVER let `--inline` run its own preflight, branch, review gate, PR, or emitter tail (Phase 0 step 4, Phase 7, Phase 9, Phase 10, Phases 12–14) — it returns its diff and its contrast finding to the caller, whose own single review and single PR cover it
- NEVER let the standalone path skip its cost entry except under `run_flags.skip_costs` (Phase 14), and NEVER let `--inline` emit one — emitting on both paths would double-count one run (`workflows-core:cost-emission` §7)
- ALWAYS end a standalone Phase 11 report with a `### Next step` recommendation (per `Skill(skill: "workflows-core:reference", args: "next-phase-offer")`) — guidance only, never auto-invoked, and conditional on whether Phase 7 actually produced a branch and a drafted PR; `--inline` prints none, since control returns to the caller's own report
- ALWAYS reference this plugin's own bundled files with `${CLAUDE_PLUGIN_ROOT}`; every `workflows-core:<name>` citation is loaded through `Skill(skill: "workflows-core:reference", args: "<name>")`, never by path

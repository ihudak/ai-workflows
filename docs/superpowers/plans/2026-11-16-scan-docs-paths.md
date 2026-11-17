# The commit scan reads a repository that holds the documentation — implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/docs-workflows:document` and `/docs-workflows:release-notes` scan the repository that holds the documentation, and leave out only the commits whose every path is documentation.

**Architecture:** `key-discovery.py` learns the documentation root and its content paths (`--docs-root`, `--docs-content`), works out the documentation set itself, and applies it as exclude pathspecs with `--full-history` to the count of commits scanned there, and tests each matched commit and each commit a pull request landed there against the same set. `key-discovery.md` states what the two commands pass and print; the commands cite it. A second subcommand, `docs-check`, lets `/document` test its own commit against the same set with git's own path matching.

**Tech stack:** Python 3 standard library, git ≥ 2.13 pathspec magic, the script's own `--selftest`; command and reference prose.

**Spec:** `docs/superpowers/specs/2026-11-16-scan-docs-paths-design.md` (cited as *D §n*, its calls as *L1*–*L13*). Measurements: `docs/superpowers/specs/2026-11-16-scan-docs-paths-measurements.md` (cited as *M §n*). Both are approved and binding; where this plan and the design disagree, the design wins and the disagreement is reported.

## Global Constraints

- **Prose is executed.** Command, reference and page prose is run literally. A false sentence is a defect. Every sentence a task writes is derived from the thing that runs it, read on this branch.
- **One noun per thing, across every file:** *the documentation root* (the directory passed as `--docs-root`), *the documentation-holding repository* (its git top level), *content path* (D L2 sources 1 and 2), *the family's own paths* (D L2 source 3, the fixed list), *the documentation set* (all three together), *documentation-only commit*.
- **The fixed list is stated once**, in `plugins/docs-workflows/references/key-discovery.md` §1, in one fenced block; the script holds the same list as a constant and its self-test compares the two. Every other file cites §1 and never repeats the list.
- **The second-run case must hold** (D §4): a commit naming the key that touches only paths in the documentation set is never a commit found.
- **A file type is never the rule** (L1). The one exception is markdown at the repository's top level (L2).
- **No guess at a generator's content folder** (D §8 anti-goal). Where no content path is known the repository is left out whole and the run says why (L3).
- **`--exclude` keeps its meaning and its behaviour**, byte for byte, for the specs repository (L6). Every existing self-test case still passes unchanged, save `case_cli`'s pinned key sets.
- **`CLAUDE.md` and `.claude/rules/docs-workflows.md` do not change.** `CLAUDE.md` holds 35,989 of 36,000 characters and the rules file 19,998 of 20,000 (`LC_ALL=C.UTF-8 wc -m`).
- **No tracker is named** in any file check 13 reads; requirement IDs keep the bracketed form; every `choices:` array stays as it is — this change adds no question.
- **Nothing about when the nothing-built question is put changes** (D §5.3): no block in scope, and no commit found.
- **Scratch files** go in the implementer's own subdirectory of the session scratchpad, never in the worktree.
- **Character budgets are measured with `LC_ALL=C.UTF-8 wc -m`.**
- **After editing any file under `plugins/workflows-core/references/`**, run `python3 scripts/reference-parts.py generate` and commit what it changes.
- **The gate chain** each task runs before its last commit, as one `&&` chain whose own exit code is read:
  `./scripts/check-docs.sh --root . && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --root . --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/validate-catalog.py && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/docs-workflows/scripts/key-discovery.py --selftest`
- **Commits:** verify `git branch --show-current` is `feat/scan-docs-paths` before each; trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. A file under `.claude/` is committed by naming its path on `git commit` (the directory is ignored for `git add`).
- **D §10's "the script and its reference change in one commit" is met at the pull request**: the script stays backward compatible commit by commit (`--exclude` unchanged, the new flags optional), so no commit on the branch pairs a reference with a script that cannot run it.

## Review Focus

1. **A content path holding pathspec or glob characters** (`docs/[draft]`, a leading `:`, a space, a `*`): it is matched as the literal path, never as a pattern. Test in Task 1 (`case_docs_content_is_literal`).
2. **A content path that is the whole repository** (`.`, empty after normalising), **absolute, or holding a `..` segment**: the first leaves the repository out whole with its reason; the other two are rejected, listed and not used. Tests in Task 1 (`case_docs_content_whole_repository`, `case_docs_content_rejected`).
3. **A documentation root that is not in a git work tree**: nothing is excluded, nothing fails, and `docs` is null. Test in Task 1 (`case_docs_root_outside_a_repository`).
4. **A root commit or an octopus merge naming the key in the documentation-holding repository**: the probe's first-parent test must not raise on a commit with no first parent, and must keep a merge that brought in code. Test in Task 1 (`case_docs_probe_merges`).
5. **A rebase-landed pull request in the documentation-holding repository whose commits are mixed** — one documentation-only, one code: each landed commit is filtered on its own; the code one is read. Test in Task 1 (`case_docs_pull_requests`).

---

## File structure

| File | What changes |
|---|---|
| `plugins/docs-workflows/scripts/key-discovery.py` | `--docs-root`, `--docs-content`, the documentation set, pathspec walks, the pull-request filter, the probe's merge test, new output fields, the `docs-check` subcommand, self-test cases |
| `plugins/docs-workflows/references/key-discovery.md` | §1's call template and *Never code*; the fixed list; §2–§5; a new §6 for `docs-check` |
| `plugins/workflows-core/references/implementation-format.md` | §4's sentence on which repositories the scan covers (L8) |
| `plugins/docs-workflows/commands/document.md` | Phase 0 step 3a, Phase 3, Phase 4 re-runs, Phase 8.5, Phase 9, the `pr-draft.md` clauses |
| `plugins/docs-workflows/commands/release-notes.md` | Phase 3 step 2, the report line |
| `plugins/docs-workflows/docs/commands/document.md`, `…/release-notes.md`, `…/docs/reference/references.md`, `plugins/docs-workflows/agents/diff-summarizer.md` | wherever each states the exclusion or describes the script |
| `docs/maintainers/rationale.md`, `docs/superpowers/to-fix.md`, `docs/superpowers/to-test-on-real-project.md` | reasons recorded; entry closed; live checks |
| `plugins/*/.claude-plugin/plugin.json`, `plugins/*/CHANGELOG.md`, `.claude-plugin/marketplace.json`, `.claude/rules/plugin-updates-coupling.md` | the release |

---

### Task 1: The script

**Files:**
- Modify: `plugins/docs-workflows/scripts/key-discovery.py`

**Interfaces — produces (Tasks 2–4 write these names into prose; do not rename without reporting):**

CLI:
```
key-discovery.py scan … [--exclude <dir> …] [--docs-root <dir> [--docs-content <path> …]] …
key-discovery.py docs-check --docs-root <dir> [--docs-content <path> …] --base <rev> [--head <rev>]
```
- `--docs-root <dir>`: the documentation root — the site's own directory, or the repository's top level. At most one; it must be an existing directory. The script takes it to its git top level itself (`rev-parse --show-toplevel`); where it lies below the top level, its path relative to the top level is a content path (L2 source 1).
- `--docs-content <path>` (repeatable): a content path relative to the top level (L2 source 2). Without `--docs-root` it is a usage error (exit 2). Normalised: a leading `./` and trailing `/` dropped.
- Exit codes as today: 0 it ran, 2 it could not run.

The documentation set and the rule (D §4):
- content paths = source 1 ∪ the accepted `--docs-content` values;
- no content path → the top level is treated exactly as an `--exclude` of it: `docs.rule` is `left-out`, `docs.reason` is `no content path`, its slug is in `excluded`;
- a content path that is the whole repository (`.` or empty) → `left-out`, `docs.reason` is `the content path is the whole repository`;
- otherwise `docs.rule` is `paths`: every `--repo` clone whose realpath is the top level **or whose `origin` slug equals the top level's** (L10) is read under the documentation set = content paths ∪ `FAMILY_DOC_PATHS`;
- a repository that `--exclude` also names stays excluded whole.

`FAMILY_DOC_PATHS` — a module constant, a tuple of `(magic, pattern)` pairs, `magic` one of `literal` or `glob`. Start from this list; verify each entry against M §6 and the commands that write it, add what M §6 shows is missing, and report every entry added or dropped with its reason:
```
.dev-workflows            literal   (top level)
.claude                   literal   (top level)
docs                      literal   (top level)
.docstack                 literal   (top level)
*.md                      glob      (top level only — glob magic stops `*` at `/`)
**/_snippets/**           glob
mkdocs.yml                literal   (top level)
mkdocs.*.yml              glob      (top level)
docusaurus.config.js / .ts / .mjs / .cjs     literal (top level)
sidebars.js / .ts / .mjs / .cjs              literal (top level)
**/_category_.json, **/_category_.yml        glob
antora.yml                literal   (top level)
**/antora.yml, **/nav.adoc                   glob
**/.pages                 glob
**/SUMMARY.md             glob
.vale, _vale, vale.ini, .vale.ini, _vale.ini literal (top level)
```
Each becomes an exclude pathspec with `top` magic (`:(exclude,top,literal)<path>` or `:(exclude,top,glob)<pattern>`); each content path becomes `:(exclude,top,literal)<path>`. A positive pathspec for the whole tree goes with them, so the walk does not depend on git's implied default.

JSON (additions only; every existing field keeps its meaning save `scanned`, below):
- top level `docs`: `null` where no `--docs-root` was given or it is in no git work tree; else an object with `root` (as given), `top`, `repo` (the slug, or the basename where there is no `origin`), `rule` (`paths` | `left-out`), `reason` (null under `paths`), `content_paths` (the accepted ones, source 1 first), `rejected` (`[{path, why}]`), `clones` (the paths of the `--repo` clones read under the rule), `docs_only` (`[{repo, sha, date, subject, keys}]` — each non-merge commit on the ref whose message names a token whole and which touches no path outside the documentation set).
- `repos[].docs_rule`: `true` on a clone read under the rule, else `false`. There `scanned` counts the non-merge commits touching at least one path outside the documentation set, and `matched` the commits kept.
- each pull request gains `landed_docs_only`: the SHAs the path filter removed from `landed` (empty elsewhere). A merged pull request whose every landed commit was removed has `landed: []` and `reason: "landed documentation only"`.
- `docs-check` prints one JSON document: `{"docs": <the same object, without clones and docs_only>, "base": …, "head": …, "outside": [<path> …]}` — the paths that `git diff --name-only --no-renames <base> <head>` lists outside the documentation set (`head` defaults to `HEAD`). Under `left-out` or a null `docs`, `outside` is `[]`.

Behaviour under `paths`, per clone read under the rule:
- **Every walk takes the exclude pathspecs and `--full-history`**: the `rev-list --count` behind `scanned`, the scan's `log`, and the probe's `log` (M §5). Never `--name-only`.
- **`docs_only`** is the scan's `log` without the pathspec, less the same `log` with it.
- **The probe** keeps its bare-token match and merges. A merge commit is dropped only where `git diff --quiet <M>^1 <M> -- <the pathspecs>` exits 0 — it brought in nothing outside the set relative to its first parent. A commit with no first parent is kept.
- **The pull-request layer**: where at least one clone is read under the rule, pull requests in that repository are no longer dropped by name; each one's `landed` SHAs are filtered in one call per pull request (`git log --no-walk=unsorted --format=%H <shas> -- <the pathspecs>`), the removed ones going to `landed_docs_only`. A commit a pull request accounts for — its merge commit or any landed commit, filtered or not — still leaves the probe. **Where no `--repo` clone is that repository (L12), its pull requests are dropped by name exactly as `--exclude` drops them today.**

- [ ] **Step 1: Give `_commit` nested paths.** `_commit(repo, message, name=None)` creates the parent directory of `name` before writing. Run `python3 plugins/docs-workflows/scripts/key-discovery.py --selftest`; expected `selftest: 42/42 passed`.

- [ ] **Step 2: Write the failing cases.** Each builds its fixture with `_repo`/`_commit`/`_merge` and calls `discover(...)` (extended with `docs_root=None, docs_content=()`) or `_main([...])`. Names and assertions:

| Case | Fixture and call | Asserts |
|---|---|---|
| `case_docs_second_run` (D §7.1) | repo `mono` with `src/app.py`, `website/docs/a.md`, `website/mkdocs.yml`; commit `ACME-7 Document intake` touching `website/docs/intake.md`, `website/mkdocs.yml`, `.dev-workflows/docs-profile.yml`; `docs_root=mono/website` | `commits == []`; `docs["rule"] == "paths"`; `docs["content_paths"] == ["website"]`; `[d["sha"] for d in docs["docs_only"]] == [that sha]`; `excluded == []`; `repos[0]["docs_rule"] is True` |
| `case_docs_code_and_mixed_commits` (D §7.2) | same layout; one commit touching `src/a.py`, one touching `src/b.py` and `website/docs/x.md`, both naming the key | both SHAs in `commits`, `via == "message"`; `docs_only == []` |
| `case_docs_side_branch_net_zero` (D §7.3) | M §5's `simp` fixture: branch `side` adds `src/e.py` and reverts it, both `[ACME-9]`; main gets a docs commit, then merges `side` | both side commits in `commits` |
| `case_docs_probe_merges` (D §7.4, Review Focus 4) | `docs_root` with a content path; no whole-key match; branch `feat/ACME-7-x` with a keyless code commit merged `--no-ff` as `Merge feat/ACME-7-x`; branch `docs/ACME-7-y` with a keyless docs commit merged `--no-ff` after a code commit on main; a root commit whose message holds `ACME-7x` | probe subjects contain the code merge; do not contain the docs merge; the root commit is present and nothing raised (`probe_error is None`) |
| `case_docs_pull_requests` (D §7.5, Review Focus 5) | `_github_clone`; three merged pull requests through `_gh`/`_merged_view`: a squash that touched only `docs/`, a squash that touched `src/`, a rebase of two keyless commits — one docs-only, one code; `docs_root` = the clone's top level, `docs_content=["handbook"]`, the documentation commits under `handbook/` | first: `landed == []`, `reason == "landed documentation only"`, one SHA in `landed_docs_only`, no commit from it; second: its commit in `commits` (`via: pull-request`); third: exactly the code commit in `commits`, the other in `landed_docs_only` |
| `case_docs_markdown_outside_the_set_is_code` (D §7.6) | content path `website`; commit naming the key touching `plugins/x/commands/run.md` | found |
| `case_docs_no_content_path` (D §7.7) | `docs_root` = the repository's top level, no `docs_content` | `excluded == [slug]`; `docs["rule"] == "left-out"`; `docs["reason"] == "no content path"`; the clone has no `repos[]` entry; a pull request in a repository of that name is dropped |
| `case_docs_second_clone_by_slug` (D §7.8) | two clones with the same `origin`; `docs_root` in the first, `--repo` the second only | the second is read under the rule: a docs-only commit there is in `docs_only`, a code commit is found; `docs["clones"] == [second]` |
| `case_docs_top_level_markdown` (D §7.9) | content path `website`; commit touching `README.md` only; commit touching `src/notes/DESIGN.md` only; both name the key | first in `docs_only`; second in `commits` |
| `case_docs_content_is_literal` (Review Focus 1) | content paths `docs site/[draft]` and `:odd`; commits under each; a commit under `docs site/d` (which `[draft]` would match as a class) | the first two are documentation-only; the third is found |
| `case_docs_content_whole_repository` (Review Focus 2) | `docs_content=["."]` | `rule == "left-out"`, `reason == "the content path is the whole repository"`, slug in `excluded` |
| `case_docs_content_rejected` (Review Focus 2) | `docs_content=["/etc", "a/../b", "website"]` | `rejected` names the first two with a `why`; `content_paths == ["website"]`; `rule == "paths"` |
| `case_docs_root_outside_a_repository` (Review Focus 3) | `docs_root` = a plain directory | `docs is None`; the scan's result equals the same call without the flag |
| `case_docs_no_clone_of_it_scanned` (L12) | `docs_root` with a content path in a GitHub clone that is **not** a `--repo`; another clone is; a pull request in the docs repository names the key | that pull request is absent from `github.prs`; `docs["clones"] == []` |
| `case_docs_excluded_too` | the same top level as `--exclude` and `--docs-root` with a content path | left out whole: in `excluded`, no `repos[]` entry |
| `case_docs_check` | a branch with one commit touching `website/docs/a.md`, `README.md` and `assets/shot.png`; `_main(["docs-check", "--docs-root", <mono/website>, "--base", <base sha>])` | exit 0; `outside == ["assets/shot.png"]`; with `--docs-content assets` → `[]`; under `left-out` → `[]` |
| `case_docs_content_without_root_is_a_usage_error` | `_main(["scan", …, "--docs-content", "x"])` | exit 2, one stderr line |

Also extend `case_cli`'s pinned key sets for the new fields.

- [ ] **Step 3: Run the self-test and see the new cases fail.** Expected: the 42 existing cases pass, each new case fails (an unknown argument, a missing key, or an assertion).

- [ ] **Step 4: Implement.** `discover(keys, clones, scope, probe=False, github=True, excludes=(), owners_of=(), docs_root=None, docs_content=())`; a helper that resolves the documentation rule once (`top`, `rule`, `reason`, `content_paths`, `rejected`, the pathspec list); `_log`, `scan_clone` and `probe_clone` take an optional pathspec list; `github_layer` takes the clones under the rule and their pathspecs; `main` gains the two flags and the `docs-check` subcommand; the module docstring's usage and prose say what the new flags do. Keep every git call through `_git_in`.

- [ ] **Step 5: Run the self-test.** Expected: `selftest: 59/59 passed` (42 + 17; state the real count if a case was added or merged, with the reason).

- [ ] **Step 6: Time it.** On a clone with at least 10,000 commits under `/workspace` (pick one with `git rev-list --count HEAD`), run `scan --scope head --probe --no-github` once without and once with `--docs-root`/`--docs-content`; report both wall-clock times. Expected: the second within a few seconds of the first (M §5d measured 0.3–0.7 s per walk on 60k–100k commits).

- [ ] **Step 7: Run the gate chain and commit** — `feat(docs-workflows): key-discovery.py reads the documentation-holding repository by path`.

---

### Task 2: The reference and the shared definition

**Files:**
- Modify: `plugins/docs-workflows/references/key-discovery.md`
- Modify: `plugins/workflows-core/references/implementation-format.md` (§4, the sentence *never the specs repository or the docs repository …*)
- Modify: `plugins/docs-workflows/scripts/key-discovery.py` (one new self-test case, `case_docs_family_paths_match_the_reference`; nothing else)
- Modify where they describe the script or state the exclusion: `plugins/docs-workflows/agents/diff-summarizer.md`, `plugins/docs-workflows/docs/reference/references.md`

**Interfaces:**
- Consumes: Task 1's CLI, JSON fields and `FAMILY_DOC_PATHS` — read them off the script on this branch, never off this plan.
- Produces: the section names and line forms Tasks 3 and 4 cite. Keep §1–§5's numbers; add `## 6. The documentation paths check`.

What `key-discovery.md` must say after this task (the wording is yours; the content is not):

- [ ] **Step 1: §1's call template** passes `--exclude <specs repository> --docs-root <the documentation root> --docs-content <content path> …`.

- [ ] **Step 2: Rewrite *Never code*** as two paragraphs.
  - **The specs repository** — left out whole, as today, with today's reason (its commits and pull requests carry the tokens by the family's conventions) and its limit stated (L6): code committed inside the specs tree's repository is never scanned; that layout is unsupported (`workflows-core:specs-repo-git`, *A specs tree inside a larger repository*).
  - **The documentation-holding repository** — D §4's rule. State: what the documentation root is for each caller (`/document`: `docs_repo_resolved`; `/release-notes`: `--docs <path>`, else `${DOCS_PATH:-/workspace/docs}`, **whether documentation grounding is on or off** — L13), left off where that directory does not exist; that it is passed **whether or not `implementation.md` names the repository** (L4); the content paths to pass and where they come from — the profile's `spaces[].content_root` and `snippet_root`, `images.root`, `builds[].config`, `announcement_pages[].path`, from the profile readable when the scan runs (L11): for `/document` Phase 0 step 3a the in-repo `<docs_repo_path>/.dev-workflows/docs-profile.yml` where it exists, else the built-in one where `is_known_docs_repo`, else none; for its Phase 3 and Phase 4 scans the profile step 4 loaded or generated; for `/release-notes` the in-repo file at the documentation-holding repository's top level where it exists, else none (L5); that the script adds the site's own directory where the root lies below the top level; the fixed list; that a commit touching a documentation path and a code path is kept; L3, with the reason the run prints; L10; L12.
  - The sentence *nothing the run holds tells the two apart* is gone, and so is *Pass either only where it is a git checkout's top level and not a repository `implementation.md` names*.

- [ ] **Step 3: The fixed list**, once, as a fenced block directly under the line `<!-- family-doc-paths -->`, one pattern per line, exactly the patterns of `FAMILY_DOC_PATHS`, with one sentence above it saying what the list is (what the family itself writes into a documentation repository, and the configuration and navigation files of the generators its docs signals name) and that a path outside it and outside the content paths is code. Then add the self-test case `case_docs_family_paths_match_the_reference`: it reads `../references/key-discovery.md` beside the script, takes the lines of the fenced block that follows the marker line, and asserts that the set of patterns there equals the set in `FAMILY_DOC_PATHS`; a missing marker fails it. Run it against a scratch copy of the reference with one pattern removed and see it fail; expected after: `selftest: 61/61 passed`.

- [ ] **Step 4: §2** gains `docs`, `repos[].docs_rule` and `landed_docs_only`, and says what `scanned` means on a clone read under the rule. **§3** says a documentation-only commit is never a commit found. **§4** says a merged pull request that landed only documentation is listed as that and never read, and that the documentation-holding repository's pull requests are dropped by name where no scanned clone is that repository.

- [ ] **Step 5: §5's report lines** (L7). Fix these forms here; Tasks 3 and 4 use them verbatim:
  - under `paths`, for each clone in `docs.clones`: one line naming the repository, the content paths taken as documentation, that the family's own paths (§1) are taken too, and that `scanned` there counts only commits touching a path outside them;
  - where `docs.docs_only` is non-empty: one line giving the count, then each commit by SHA, date and subject, saying they name a token and were left out as documentation only;
  - where `docs.rejected` is non-empty: one line naming each rejected path and why;
  - `Left out as never code:` names only repositories left out whole. Where the documentation-holding repository is among them, its slug carries the reason: for `no content path`, that no profile yet says where its documentation lives and `/docs-workflows:docs-profile` makes the scan possible; for the whole-repository case, that its profile takes the whole repository as documentation.

- [ ] **Step 6: §6, the documentation paths check** — how `/document` Phase 8.5 runs `docs-check` (the flags, the same content paths as the scan, `--base`), what `outside` means, and the line the run prints for a non-empty `outside` (L9): each path, and that a later run's scan will read this commit as built work unless the profile names that path.

- [ ] **Step 7: `implementation-format.md` §4** — the scan covers the repositories the record names or, when it names none, those resolved from `$REPOS_PATH`; never the specs repository; and in the repository that holds the documentation, never a commit that touches documentation paths alone (cite `docs-workflows`' `key-discovery.md` §1 as where those paths are stated, in the form that file already uses for a cross-plugin mention — read how §4 names the script today). Check the *pull-request layer* paragraph of the same section against Task 1's filter and add one clause if it now states less than the truth. Run `python3 scripts/reference-parts.py generate`.

- [ ] **Step 8: Sweep** `agents/diff-summarizer.md` and `docs/reference/references.md` for a statement of the exclusion or of the script's flags; correct what is now false; change nothing that is still true.

- [ ] **Step 9: Run the gate chain and commit** — `docs(docs-workflows, workflows-core): key-discovery.md and implementation-format §4 state the documentation path rule`.

---

### Task 3: `/document`

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md`
- Modify: `plugins/docs-workflows/docs/commands/document.md`
- Modify if it states the squash step's contents: `plugins/docs-workflows/references/finish-and-handoff.md` (§2–§3 only)
- Modify: `plugins/docs-workflows/agents/diff-summarizer.md` and its handoff reference `plugins/docs-workflows/references/handoff/diff-summarizer.md` (Step 3a only)

**Interfaces:**
- Consumes: `key-discovery.md` §1, §5 and §6 as Task 2 left them — cite them; copy a line form only where the command prints it.

M §8's *Commands* list is the population: every `DOC:` entry there is a site to read and disposition. Line numbers in M are from commit `e1761361`; find each by its quoted phrase.

- [ ] **Step 1: Phase 0 step 3a, the call.** In place of *`--exclude` the specs repository and `docs_repo_path`*: `--exclude` the specs repository; `--docs-root <docs_repo_resolved>`; and each content path `key-discovery.md` §1 names for this step. The sentence giving step 3a's place (*after step 2 because the scan leaves out the documentation repository step 2 resolves*) is re-stated against the rule.

- [ ] **Step 2: Step 3a's lines above the question.** The scan lines follow `key-discovery.md` §5: the documentation paths line, the documentation-only commits line, the rejected line; `Left out as never code:` with the reason for the documentation-holding repository. A documentation-only commit is **not** a commit found: say so where step 3a defines *work found*. Re-read the three forms of the last line and the four `Commit scan:` forms against each case the rule now produces: (a) the documentation-holding repository read under the rule with none found; (b) left out whole for want of a content path; (c) it is the only clone in the map and is left out. The `<slug>: <scanned> commits on HEAD …` line says, on a clone read under the rule, that the count is of commits touching a path outside the documentation paths.

- [ ] **Step 3: Phase 3 step 2 and Phase 4's re-runs.** *never the specs or the docs repository* and *the same exclusions* are re-stated: each scan passes the documentation root and the content paths of the profile the run holds when it runs (L11). **A run whose record holds a block passes them too** (L4) — read how that run passes `--exclude` today and replace it. A commit the scan found in the documentation-holding repository is handed on as any other; `docs.docs_only` commits are never handed to `diff-summarizer`.

- [ ] **Step 3a: The key-commit fallback never reads a documentation-only commit.** `diff-summarizer`'s *Key-commit fallback* greps `git log --all` for each key and reads every match as an unresolvable element's content; `/document` passes it `keys_hierarchy`, so in a repository holding both code and documentation it would read an earlier run's documentation-only commits as code (D §8's second goal). Add one optional handoff field carrying, for that repository, the SHAs of the scan's `docs.docs_only` commits; `/document` Phase 4 fills it where the scan returned any for that clone; the agent drops a match whose SHA is in it before it treats the matches as the element's content, and where that leaves none, the element goes where an empty fallback goes today. Name the field once and use that name in the command, the agent and the handoff reference; read how `/release-notes` dispatches the agent and change nothing there unless it passes keys (its text says it does not). State the limit where the field is defined: a documentation-only commit on a branch the scanned ref does not hold is not in the list.

- [ ] **Step 4: Phase 8.5, the check (L9).** In Step 1, **after the squash commit is made and before Step 2 offers the push**, run `docs-check` as `key-discovery.md` §6 says, with `--base` the merge-base Step 1 item 2 computes against `base_branch` (so an inline-profiling run's profile commit is checked with the squash). For a non-empty `outside`, print §6's line and go on; carry the paths to Phase 9. Where git refused the commit, or the script could not run, say the check did not run and why. *Ruling to record in your report: the design words this as "before it makes it"; the check is placed after the commit so that it reads the commit itself — deletions included, another person's staged changes excluded — with git's own path matching. The operator still sees the line before the push is offered.*

- [ ] **Step 5: Phase 9 and `pr-draft.md`.** The report's `Left out as never code:` line, the *ran and left every clone … out as the specs or the documentation repository* clause, the Assumptions clauses and the `pr-draft.md` clauses that name left-out slugs: each re-read against the rule. The report gains the documentation paths line, the documentation-only commits, and Phase 8.5's check result. **Where step 3a left the documentation-holding repository out for want of a content path and step 4(c) then generated a profile on this run**, the reason reads that the profile this run wrote, once merged, makes the scan possible (D §11).

- [ ] **Step 6: The Readiness row and every other `DOC:` entry of M §8** not covered above: read, and change where false.

- [ ] **Step 7: The page.** `docs/commands/document.md`'s two sentences (M §8 *Pages*) are rewritten from the command as it now reads; add what an operator needs to know: which paths count as documentation, that a commit touching nothing else is not counted, the first-run limit (L3), and Phase 8.5's warning.

- [ ] **Step 8: Walk the layouts** (D §7) and put the walk in your report: for each of — site in a subfolder; site at the top level with an in-repo profile; site at the top level with no profile; a documentation-only repository with a profile; a repository `implementation.md` names — what step 3a or Phase 3 passes and what the run prints, each read off the text you wrote.

- [ ] **Step 9: Count** the literal strings you replaced, before and after, across `plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/` (`.claude/rules/claim-sweep.md` refinement 7), wrap-insensitively: at least `never the specs or the docs repository`, `the same exclusions`, `left out as the specs or the documentation repository`. Report each count.

- [ ] **Step 10: Run the gate chain and commit** — `feat(docs-workflows): /document passes the documentation path rule to the commit scan and checks its own commit against it`.

---

### Task 4: `/release-notes`

**Files:**
- Modify: `plugins/docs-workflows/commands/release-notes.md`
- Modify: `plugins/docs-workflows/docs/commands/release-notes.md`

**Interfaces:**
- Consumes: `key-discovery.md` §1 and §5 as Task 2 left them.

- [ ] **Step 1: Phase 3 step 2.** *never the specs or the docs repository* is re-stated: the specs repository is left out; the documentation-holding repository is read by `key-discovery.md` §1's rule. State what this command passes: the documentation root by L13 — `--docs <path>`, else `${DOCS_PATH:-/workspace/docs}`, resolved here whether or not documentation grounding is on, left off where the directory does not exist — and the content paths of the in-repo profile at that repository's top level where one exists (L5). Read Phase 1 and Phase 2 for where `--docs` is parsed and where grounding resolves the root, and make this step's resolution agree with both, `--no-docs` included.

- [ ] **Step 2: The report line** (M §8 `RN:760`): `left out as never code:` names only repositories left out whole, with the reason for the documentation-holding repository; the line gains the documentation paths and the documentation-only commits in `key-discovery.md` §5's forms.

- [ ] **Step 3: The read set.** Read Phase 3–Phase 5 for every place a scan commit enters the provisional read set or the note's `read:` scope comment, and confirm from the text that a `docs.docs_only` commit enters neither. Add a clause only where the text would otherwise let one in.

- [ ] **Step 4: The page.** Add to `docs/commands/release-notes.md` what an operator needs: the scan now reads a repository that holds both code and documentation, by path; and the one consequence D §5.3 names — the first run after this change, in such a repository whose record names no repository, reads code commits no earlier note read, so its note can describe work an earlier note already covered.

- [ ] **Step 5: Walk** `/release-notes` with a subfolder documentation root, with a top-level one with an in-repo profile, with a top-level one with none, and with `--no-docs`: what is passed and what is printed. Put the walk in your report.

- [ ] **Step 6: Check the rules file is still true.** Read `.claude/rules/release-notes.md` with the Read tool; report any sentence the change falsifies. Do not edit it unless one is false; if one is, fix that sentence alone and keep the file under 20,000 characters.

- [ ] **Step 7: Run the gate chain and commit** — `feat(docs-workflows): /release-notes passes the documentation path rule to the commit scan`.

---

### Task 5: The sweep, the records and the release

**Files:**
- Modify: `docs/maintainers/rationale.md`, `docs/superpowers/to-fix.md`, `docs/superpowers/to-test-on-real-project.md`
- Modify: `plugins/docs-workflows/.claude-plugin/plugin.json`, `plugins/workflows-core/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, both plugins' `CHANGELOG.md`, `.claude/rules/plugin-updates-coupling.md`

The controller merges `origin/main` into the branch before this task and tells you the versions `main` then holds.

- [ ] **Step 1: The claim sweep.** Run M §8's search (its last paragraph gives the command) over `plugins/`, `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`, and an exclusivity probe (`.claude/rules/claim-sweep.md` refinement 3) on the scan's subject. For every hit about this scan: true as it stands, or fix it. Read `.claude/rules/claim-sweep.md` and `.claude/rules/docs-workflows.md` with the Read tool first. A hit in a rules file that is now false is reported to the controller before it is edited — `docs-workflows.md` has two characters of room.

- [ ] **Step 2: `rationale.md`.** Rewrite the sentence batch 3 wrote on this limit (M §8, *Instruction tiers*) and record this change's reasons: why paths and never a file type; why the repository is left out whole where no content path is known; why `--full-history`; why the check on `/document`'s own commit; what was refused (D §9).

- [ ] **Step 3: `to-fix.md`.** Close `DOCS-IN-CODE-REPO-SCAN` in the file's own form for a closed entry, naming what remains: the first-run limit (L3) and the specs repository (L6).

- [ ] **Step 4: Live checks.** In `to-test-on-real-project.md`: correct the batch 3 check M §8 names as expecting the old behaviour, and add one check per layout of D §7's last paragraph, plus the second-run case, Phase 8.5's warning, and `/release-notes`' first run after the change. Each says what to set up, what to run and what to expect, in the file's own form.

- [ ] **Step 5: Versions.** `docs-workflows` takes a minor version and `workflows-core` a patch, each above what `main` holds; `plugin.json` and the `marketplace.json` entry agree.

- [ ] **Step 6: Changelogs**, dated today (never `Unreleased`). `docs-workflows`: what changed for `/document` and `/release-notes`; which paths count as documentation; the first-run limit; the consequence for `/release-notes`' first run; in a documentation-only repository, a commit naming the key that touches a path outside the documentation set now counts as built work. `workflows-core`: `implementation-format` §4's new meaning.

- [ ] **Step 7: The coupling bullet** in `.claude/rules/plugin-updates-coupling.md`, in the file's own form: which side breaks what when older. Measure the file after; it must stay under 20,000 characters.

- [ ] **Step 8: Run the gate chain, then every `run:` step of `.github/workflows/validate-catalog.yml` in order as one `&&` chain**, and commit — `release: the commit scan reads the documentation-holding repository — docs-workflows <x.y.0>, workflows-core <a.b.c>`.

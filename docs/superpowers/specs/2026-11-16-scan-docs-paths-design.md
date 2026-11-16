# The commit scan reads a repository that holds the documentation — design

Status: approved by the maintainer, 2026-11-16. Plan: `docs/superpowers/plans/2026-11-16-scan-docs-paths.md`. Closes `DOCS-IN-CODE-REPO-SCAN` (`docs/superpowers/to-fix.md`). Measured against the tree on 2026-11-16: `docs/superpowers/specs/2026-11-16-scan-docs-paths-measurements.md`, cited below as *M §n*.

## 1. Intent

`/docs-workflows:document <KEY>` and `/docs-workflows:release-notes` look for the work built for a key by scanning commit messages in code repositories (`plugins/docs-workflows/scripts/key-discovery.py`; recipe `plugins/docs-workflows/references/key-discovery.md` §1; semantics `workflows-core:implementation-format` §4). The documentation repository is left out of that scan whole, because `/document`'s own commits there name the key, and a second run must not take the first run's pages for the work they describe.

Where the documentation lives inside a code repository, leaving the repository out leaves the code out. Work built there by hand is invisible whatever its commit messages say. Since `docs-workflows` 1.40.0 such a run asks the nothing-built question with *Stop* recommended; before it, the run wrote from the PRD alone and said nothing.

**After this change the scan reads such a repository and ignores only the commits that touch nothing but documentation.**

## 2. What the measurement changed

The to-fix entry understated the defect (M §0):

- It dates from `docs-workflows` 1.13.0, when the exclusion shipped, not from 1.40.0.
- `/release-notes` has it in both directions. Its docs root is never taken to a git top level, and the exclusion applies only to a top level: a docs root that is a product repository's top level leaves the code out; one that is a subfolder (`website/`) leaves nothing out, so `/document`'s earlier commits there are read as code.
- Where `implementation.md` names the repository that holds the documentation, the repository is scanned whole today, and `/document`'s own squash commits come back as unrecorded work and go to `diff-summarizer` as code. No text accepts that.
- A plain code repository can be taken as the documentation repository more easily than the entry says: the docs signals include any `package.json` script matching `*:start`, `*:build` or `*:lint`, and *Use cwd anyway* takes a repository with no signal at all.
- A documentation commit can be told from a code commit only by its paths. The family writes no trailer and no fixed subject, and the author is the operator.

## 3. Decisions

**The maintainer's, 2026-11-16.**

| # | Decision |
|---|---|
| M1 | **Fixed as its own change, after LADDER-ORDER batch 3 and ahead of batch 4.** |
| M2 | **Approach A: scan the documentation-holding repository and ignore the commits whose every path is documentation.** Refused: *B*, the same scan with the commits found there shown above the question and never counted until the operator takes them; *C*, no script change — scan the repository whole where it shows it holds code, which brings back the second-run false "built". The cost of A was put with the question and accepted: a documentation path the rule does not know counts as built work. |

**The lead's calls**, shown to the maintainer with the approaches and not corrected. Each is checked while reading.

| # | Call | Why |
|---|---|---|
| L1 | **What counts as documentation is a set of paths the run can name, never a file type.** A markdown file outside those paths is code. | A product whose code is markdown — this marketplace is one — would otherwise read as never built (M §5f). |
| L2 | **The set has three sources**, each relative to the repository's top level: (1) the site's own directory, where the run resolved one below the top level; (2) what the docs profile records, where a profile is readable when the scan runs — `spaces[].content_root` and `snippet_root`, `images.root`, `builds[].config`, `announcement_pages[].path`; (3) a fixed list of what the family itself writes and of the navigation files of the generators it knows, stated once in `key-discovery.md` §1. | (1) and (2) are what the run already holds (M §3). (3) covers what no profile field records (M §6): `.dev-workflows/`, `.claude/`, every markdown file at the repository's top level and the top-level `docs/` folder — the reach of `/document`'s own Phase 8 edits, `README.md`, `CHANGELOG.md` and `CLAUDE.md` among them — `_snippets/` at any depth, and the generators' own configuration and navigation files. Top-level markdown is the one place a file type enters the set, and only at the top level: a product whose code is markdown keeps its code below it. |
| L3 | **Where neither (1) nor (2) names a content path, the repository is left out whole, as today, and the run says why**: no profile yet says where its documentation lives, and `/docs-workflows:docs-profile` makes the scan possible. | A site at a repository's top level with no profile is the one layout where the run cannot name the content folder when the scan runs — the profile is generated after it, by design (M §3). Guessing a generator's default folder is a parse of free text. The limit is the first run in such a repository; once its profile is on the default branch the path rule applies. |
| L4 | **The path rule replaces the whole-repository exclusion wherever L2 names a content path — for a repository that holds only documentation too, and whether or not `implementation.md` names the repository.** | One rule, no test of whether a repository "is code". It also closes the false "unrecorded work" on a named repository (§2). Cost, accepted with M2: in a documentation-only repository, a commit that names the key and touches a path outside the set — a CI change, a navigation file the list does not know — counts as built work, where today it is ignored. |
| L5 | **`/release-notes` takes the same rule.** Its docs root is taken to its git top level to name the repository; the content paths are the docs root's own subtree where it lies below that top level, and an in-repo profile's where `<top>/.dev-workflows/docs-profile.yml` exists. Otherwise L3. | It shares the scan and has no profile step of its own (M §3, §7). |
| L6 | **The specs repository keeps its whole exclusion.** The limit is stated where the exclusion is: code committed inside the specs tree's repository is never scanned. | The layout is unsupported (`workflows-core:specs-repo-git`: a specs tree inside a larger repository sets `specs_git: misrooted`), and the specs tree's own commits name every key by the family's conventions. |
| L7 | **What the run prints says what the rule did**: for the documentation-holding repository, how many commits it read outside the documentation paths, the commits naming a token that it left out as documentation only — counted and listed — and the paths it took as documentation. `Left out as never code:` names only a repository left out whole. | The cost of L4 is a silent false "built"; the count and the paths are what let an operator see one. |
| L8 | **`workflows-core:implementation-format` §4 states the new meaning**: never the documentation repository's documentation commits, in place of never the documentation repository. | It owns the scan's semantics (M §9). |
| L9 | **`/document` checks its own commit against the set before it makes it.** Where a path Phase 8.5 is about to commit lies outside the documentation paths, the run says so — the path, and that a later run's scan will read this commit as built work unless the profile names that path — and goes on. | L2's set cannot be proved complete: an image directory a writer chose, or a navigation file of a generator the list does not know, is recorded nowhere (M §6). The miss is silent and lasts for that key. The run that creates it is the one place it can be seen. |
| L10 | **The rule attaches to a clone as the exclusion does today: by its path or by its `origin` slug.** A second clone of the documentation repository is read by the same rule. | The scan reads one clone per slug, often not the one `/document` writes in (M §2); a rule attached by path alone would read the other clone whole. |
| L11 | **The documentation paths are worked out at each scan, not once.** A scan in Phase 3 or Phase 4 runs after the profile step and takes the profile that step loaded or generated; L3 can then apply only at Phase 0 step 3a and in `/release-notes`. | L2 says *readable when the scan runs*; a profile generated at step 4(c) exists by Phase 3. |
| L12 | **The rule changes how the documentation-holding repository is read, never whether it is covered.** Where no clone of it is among those the scan reads, nothing is added, and its pull requests are still dropped by name. | Landed commits can be filtered by path only in a clone the scan holds; unfiltered, every earlier `/document` pull request would be listed as found and not read. |
| L13 | **For `/release-notes` the documentation root is `--docs <path>`, else `${DOCS_PATH:-/workspace/docs}`, whether documentation grounding is on or off.** | With `--no-docs`, grounding resolves no root, and the scan would read a documentation clone whole (M §2). |

## 4. The rule

For the repository that holds the documentation — `/document`'s `docs_repo_path`, `/release-notes`' docs root taken to its top level:

| What the run can name | What the scan does there |
|---|---|
| At least one content path (L2's source 1 or 2) | Reads the repository. A commit counts where its message names a token **and** it touches at least one path outside the documentation set (L2's three sources together). A commit touching only documentation paths is left out and counted. |
| No content path | Leaves the repository out whole, as today, and says so (L3). |

A commit that touches a documentation path and a code path is kept: a person changed code and named the key (M §5e). `/document` itself writes only documentation paths, so its own commits are left out wherever the set covers what it wrote.

**The second-run case is the one the rule must not break** (LADDER-ORDER batch 3's ruling R1). After a first run answered *Go on* and published pages, a second run on the same key must still be asked. That holds exactly where every path the first run committed is in the set; §7's first live check and the script's self-test pin it.

## 5. The changes

### 5.1 The script — `plugins/docs-workflows/scripts/key-discovery.py`

- **A way to pass the rule**: the documentation-holding repository's top level and its documentation paths, in place of `--exclude` for that repository; it attaches by path or by slug (L10). The flag names are the builder's.
- **For that clone, every walk takes the paths as exclusions**: the count of commits scanned, the scan itself, and the report-only probe.
- **`--full-history` wherever a pathspec is added.** Measured (M §5): without it git simplifies history and a side branch's key-naming commits vanish; the probe loses the merge commits it exists to show.
- **The pull-request layer**, where a clone of that repository is read (L12), stops dropping its pull requests by name, and filters the commits each one landed by the same paths; a pull request that landed only documentation is listed as that and never read. Without it a merge-commit landing of `/document`'s own pull request brings back its keyless profile commit (M §0 item 7).
- **The output** gains, for that repository, the paths taken as documentation and the commits naming a token that were left out as documentation only (L7). `scanned` there means commits touching at least one path outside the set; the reference and the commands say so.
- **The self-test** gains the cases of §7. It runs in CI already.
- No other script changes. `key-discovery.py` is not one of the copied scripts (M §9).

### 5.2 The reference — `plugins/docs-workflows/references/key-discovery.md`

- §1's *Never code* paragraph is rewritten: the specs repository is left out whole (L6, with its limit stated); the documentation-holding repository takes §4's rule; the fixed list (L2 source 3) is stated here, once, and every other file cites it.
- The sentence *nothing the run holds tells the two apart* goes: it is false in two of the three layouts (M §0 item 4).
- §5's report lines follow L7.

### 5.3 The commands

- **`/document`** (`plugins/docs-workflows/commands/document.md`): Phase 0 step 3a, Phase 3 and Phase 4's re-runs pass the rule in place of the exclusion, each working the paths out when it runs (L11). Phase 8.5 checks the paths it is about to commit against the set (L9). Step 3a's lines above the nothing-built question, the question's own last line, the Readiness row, the `pr-draft.md` line and Phase 9's report follow L7. Where the repository is left out whole for want of a content path, the lines say L3's reason and name `/docs-workflows:docs-profile`. A run whose record holds a block passes the rule too (L4).
- **`/release-notes`** (`plugins/docs-workflows/commands/release-notes.md`): Phase 3's scan passes the rule by L5 and L13; its report line follows L7. One consequence is stated in the changelog: the first run after this change, on a repository that holds code and documentation and whose record names no repository, reads code commits no earlier note read, and its note can describe work an earlier note already covered.
- Nothing about when the nothing-built question is put changes: no block in scope, and no commit found.

### 5.4 The shared reference, pages, rationale, release

- `workflows-core:implementation-format` §4 (L8).
- The `/document` and `/release-notes` pages, wherever they state the exclusion.
- `docs/maintainers/rationale.md`: the sentence batch 3 wrote on this limit is rewritten, and this change's reasons recorded.
- No rules file changes: `.claude/rules/docs-workflows.md` has no room and `CLAUDE.md` has eleven characters; `key-discovery.md` is the authority.
- `docs/superpowers/to-fix.md`: the entry closed, with what remains (L3's first-run limit; L6).
- Versions: `docs-workflows` takes a minor version, `workflows-core` a patch, with a coupling bullet for the pair.

## 6. What stays as it is

- The specs repository's exclusion (L6).
- A repository that is not the documentation repository: scanned as today.
- The nothing-built question's test, its two answers, and where it sits.
- `/document`'s resolution of the documentation repository and its docs signals. That a plain code repository can be taken as the documentation repository (§2) is not changed here; under the rule it costs far less, since its code is read wherever a content path is known.
- The `Commit scan:` forms for a scan that did not run.

## 7. Done when

The script's self-test holds, each in a fixture repository:

1. **Second run.** A repository holding code and a site: a commit naming the key that touches only the site's folder, its navigation file and `.dev-workflows/` is left out; the scan finds none.
2. A commit naming the key that touches code only is found; one touching code and a page is found.
3. A side branch whose net effect on code is nothing — a change and its revert, both naming the key — is still found (`--full-history`).
4. The probe still shows a merge commit that names the key and brought in code.
5. A merged pull request that landed only documentation is listed and not read; one that landed code is read.
6. A markdown file outside the documentation set is code.
7. No content path given: the repository is left out whole and named as today.
8. A second clone of the documentation-holding repository, read in place of the first, takes the same rule (L10).
9. A commit naming the key that touches only a top-level markdown file is left out; one touching a markdown file below the top level, outside the set, is found.

And, read from the commands: Phase 8.5's check (L9) on a commit that holds a path outside the set; and a walk of each layout — site in a subfolder; site at the top level with an in-repo profile; site at the top level with no profile (L3); a documentation-only repository with a profile; a repository `implementation.md` names; `/release-notes` with a subfolder docs root and with a top-level one — states what is passed and what is printed. Live checks for each are added to `docs/superpowers/to-test-on-real-project.md`.

## 8. Goals, non-goals, anti-goals

- **Goal:** work built by hand in a repository that also holds its documentation is found by `/document` and `/release-notes`.
- **Goal:** `/document`'s own commits are never taken for the work they describe, in any layout where the run can name the content paths.
- **Non-goal:** telling documentation from code by file type, by commit message or by author.
- **Non-goal:** scanning code inside the specs repository.
- **Non-goal:** changing how the documentation repository is resolved.
- **Anti-goal:** a second run that finds the first run's pages and stops asking.
- **Anti-goal:** a guess at where a generator keeps its content.
- **Anti-goal:** a silent change of what a line means — every line whose number changes meaning (`scanned`, *left out*) says so.

## 9. Approaches

- **A — ignore documentation-only commits by path. Chosen (M2).** One mechanism for `/document`, `/release-notes` and the named-repository false positive; needs no state; costs a fraction of a second on a hundred thousand commits (M §5d). Weakness: a documentation path outside the set counts as built work.
- **B — the same scan, shown and not counted.** Removes A's silent miss on the question's path at the cost of a third option on every such run and wiring through Phase 3. Refused.
- **C — no script change; scan a documentation repository whole where it shows it holds code.** Smallest; brings back the second-run false "built" and keeps `/release-notes`' two faults. Refused.
- **A marker on `/document`'s commits** was measured and set aside: every squash made before the marker's release is unmarked, a host's squash can drop a trailer, and a writer's own commit `<KEY> document intake` carries none (M §10 B).

## 10. Constraints

- The script and its reference change in one commit; prose is executed (`CLAUDE.md` § Editing discipline).
- `CLAUDE.md` and `.claude/rules/docs-workflows.md` do not grow.
- No tracker is named; requirement IDs keep the bracketed form.
- The claim sweep covers every statement of the exclusion (M §8 lists them).
- Both internal editions carry `key-discovery.py` and the same whole-repository exclusion (checked 2026-11-16, on the maintainer's pointer). The fix is ported to each after it merges here, as its own change.

## 11. Left to the builder

- The flag names, the output's field names, and how the probe treats a merge that brought in only documentation (it is report-only; it must never drop a merge that brought in a path outside the set).
- The exact fixed list (L2 source 3): start from M §6's inventory of every path the family commits into a documentation repository and the navigation files of the generators the docs signals name, and verify each against the commands.
- How a profile is read when the scan runs — it is a file at `<top>/.dev-workflows/docs-profile.yml`, the built-in one where the repository is a known docs repository, or the one step 4 loaded or generated (L11) — and what is done where the file is unreadable (L3 applies).
- What L3's line says where step 4(c) has just generated a profile on this run: that the profile this run wrote, once merged, makes the scan possible.
- The wording of every line under L7.

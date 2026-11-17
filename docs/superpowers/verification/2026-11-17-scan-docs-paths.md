# DOCS-IN-CODE-REPO-SCAN — the commit scan reads the documentation-holding repository — verification record

**Plan:** `docs/superpowers/plans/2026-11-16-scan-docs-paths.md`. **Design:** `docs/superpowers/specs/2026-11-16-scan-docs-paths-design.md`, with its §12 *Settled while building*, added by this close-out. **Measurements:** `docs/superpowers/specs/2026-11-16-scan-docs-paths-measurements.md`. **Release:** `docs-workflows` 1.41.0, `workflows-core` 1.96.1 and `dev-workflows` 4.70.1, each changelog section dated 2026-11-17 — `workflows-core` released at first as 1.95.2 and renumbered above `origin/main`'s after it was merged, and `dev-workflows` added by the final fix wave. **Branch:** `feat/scan-docs-paths`, cut from `main` at `e1761361`, with `origin/main` at `6d6518b7` (pull request #207, returned-intake) merged into it at `ffa8db0c`. Measured at `aa8ba5b2`, the head, after the final fix wave, its re-review, the touch-up, the narrow check and the controller's six sentences — the one commit on which the full CI chain had not been run. Every figure below was obtained here, on that tree, with its command beside it; where a figure is the ledger's or a report's and was not re-run, the sentence says so.

The rulings summary is `2026-11-17-scan-docs-paths-rulings.md` beside this file, and the controller's ledger, verbatim, is `2026-11-17-scan-docs-paths-ledger.md`: `awk '/^```text$/{f=1;next} /^```$/{f=0} f' docs/superpowers/verification/2026-11-17-scan-docs-paths-ledger.md | diff - .superpowers/sdd/2026-11-16-scan-docs-paths/progress.md` prints nothing and exits 0, and both hash to md5 `94986fbaef2a311f59e203ff82021859`, 111 lines. Every *ledger line* below is a line of that file: `progress.md`'s line *n* is its line *n* + 5. *Ruling N* is row N of the rulings file's table.

**Where and how it was measured.** One 12-core machine (`nproc`), Python 3.15.2, git 2.43.0, node v26.13.0, uid 502 (`id -u`). Every command ran from the worktree root, `/workspace/.worktrees/scan-docs-paths`, on the tree `aa8ba5b2` commits: `git branch --show-current` printed `feat/scan-docs-paths`, `git log --oneline -1` printed `aa8ba5b2`, and `git status --short` printed nothing, before the checks and after them. `git fetch origin` updated no ref; `git rev-parse origin/main` and `git merge-base HEAD origin/main` both print `6d6518b7ddfec28b8635e9b4458259b3c700bc5a`, and `git log --oneline HEAD..origin/main | wc -l` prints 0: **`origin/main` has not moved since `6d6518b7`**, and the branch holds all of it. `$S` below is a scratch directory outside the repository; `$S/main-tree` is `origin/main` unpacked there with `git archive 6d6518b7 | tar -x -C $S/main-tree`, and `$S/base-tree` is `e1761361`, where the branch was cut, unpacked the same way. Below, DOC and RN are `plugins/docs-workflows/commands/document.md` and `release-notes.md`; KD is `plugins/docs-workflows/references/key-discovery.md` and KDP the script, `plugins/docs-workflows/scripts/key-discovery.py`; IF is `plugins/workflows-core/references/implementation-format.md`; DES the design; TT `docs/superpowers/to-test-on-real-project.md`; CPL `.claude/rules/plugin-updates-coupling.md`; DW-CL, WC-CL and DV-CL the newest changelog sections of `docs-workflows` (1.41.0), `workflows-core` (1.96.1) and `dev-workflows` (4.70.1). Every line number is at `aa8ba5b2`.

## What was verified

**The branch.** `git log --oneline --first-parent origin/main..HEAD | wc -l` gives 29, and so does `git log --oneline origin/main..HEAD | wc -l` — `origin/main`'s own 27 commits since the cut (`git log --oneline e1761361..6d6518b7 | wc -l`) are reachable from both and not counted; `git log --merges --format='%h %p' origin/main..HEAD` prints one merge, `ffa8db0c 29a579c6 6d6518b7`, whose first parent is the branch and second `origin/main`. The 29, by task:

- the design, its approval and the plan, outside any task: `44ea2bf9` (the design and the measurements), `294a29f1` (the design approved, and the plan); the plan's three edits during the build, `c64eaf87` (the reference-comparison case moved to Task 2, before dispatch), `94455807` (the architecture line and Task 2's case count, after Task 1) and `b6efcd98` (Task 3's Step 3a, ruling 11);
- Task 1, the script: `30946c38`, the timing change `21c35f9b` (ruling 6), fix round `9d7df2a3`;
- Task 2, the reference and IF §4: `d55b8cec`, fix round `6555b558`, touch-ups `399570c7` and `918f5e1c` (rulings 15, 16);
- Task 3, `/document`: `0d4ad93a`, fix rounds `39ede2f5` and `b223b25e`;
- Task 4, `/release-notes`: `c470e915`, touch-up `a3f0cab4`;
- Task 5, the release: `29a579c6`;
- the merge of `origin/main`, `ffa8db0c`, and the renumbering, `e318d4f7` (ruling 25);
- the final fix wave: `f5f7c2bf`, `b828ada8`, `2eae1a5a`, `ca0ddc84`, `e30c2d2c`, `0f61a5ec`;
- the touch-up: `a9454f0a`, `13fb0571`;
- the controller's six sentences: `aa8ba5b2` (ruling 34).

**The files — what the pull request will show.** `git diff --stat origin/main HEAD | tail -1` prints `30 files changed, 2248 insertions(+), 144 deletions(-)`; `git diff --name-only origin/main HEAD` lists: 14 under `plugins/docs-workflows` (the commands `document.md` and `release-notes.md`; the references `key-discovery.md`, `finish-and-handoff.md` and `handoff/diff-summarizer.md`; the agent `diff-summarizer.md`; the script `key-discovery.py`; the pages `docs/commands/document.md`, `docs/commands/release-notes.md`, `docs/getting-started.md`, `docs/reference/environment.md` and `docs/reference/references.md`; the changelog and `plugin.json`), 4 under `plugins/workflows-core` (IF, `docs/reference/references.md`, the changelog, `plugin.json`), 3 under `plugins/dev-workflows` (`docs/reference/commit-convention.md`, the changelog, `plugin.json`), CPL, `docs/maintainers/rationale.md`, the repo-root `README.md`, five under `docs/superpowers` (the design, the measurements, the plan, `to-fix.md`, TT) and `.claude-plugin/marketplace.json` — 14 + 4 + 3 + 1 + 1 + 1 + 5 + 1 = 30. `git diff --name-only origin/main HEAD -- 'plugins/*/scripts/*' 'plugins/*/agents/*'` lists KDP and the agent alone, and `git diff --name-only origin/main HEAD -- 'plugins/*/hooks/*' 'plugins/*/skills/*' 'scripts/*' '.github/*'` prints nothing: no hook, no skill, no repository script and no workflow changed. The figures are taken before the commit that carries these three records and the design's §12.

## The merge of `origin/main`

**What was merged.** `6d6518b7`, pull request #207 (returned-intake), 27 commits and 41 files since the cut (`git diff --name-only e1761361 6d6518b7 | wc -l`), releasing `workflows-core` 1.96.0, `product-workflows` 3.84.0 and `dev-workflows` 4.70.0, four minutes after this branch's release commit `29a579c6` (Task 5's review, C1). The merge is `ffa8db0c` (2026-11-17 02:58 UTC); the renumbering, `e318d4f7`, took `workflows-core` from 1.95.2 to 1.96.1 (`merge-report.md`: 13 occurrences on 9 lines in 8 files, 0 after).

**The five conflicted files**, as `merge-report.md` lists them: `.claude-plugin/marketplace.json` and `plugins/workflows-core/.claude-plugin/plugin.json` (the version line), the `workflows-core` changelog (the branch's section above `origin/main`'s 1.96.0), CPL (`origin/main`'s three bullets first, then the branch's, then the `prose-style` bullets) and TT (`origin/main`'s RETURNED-INTAKE section, then the branch's). Two more files both sides changed merged without a conflict, `docs/superpowers/to-fix.md` and `plugins/workflows-core/docs/reference/references.md`.

**What this record re-checked**, on `aa8ba5b2`. `git diff --name-only e1761361 6d6518b7` and `… e1761361 29a579c6`, compared with `comm`: 34 files only `origin/main` changed, 20 only the branch had changed before the merge, 7 both. Of the 34, 32 are byte-equal to `origin/main`'s at the head (`git diff --quiet 6d6518b7 HEAD -- <file>` for each); the other two are `plugins/dev-workflows/.claude-plugin/plugin.json` and `plugins/dev-workflows/CHANGELOG.md`, which the wave's 4.70.1 release changed after the merge — the changelog with its first section removed equals `origin/main`'s byte for byte (*Versions*). For the 7, every non-blank line `origin/main` added since `e1761361` is present at the head, save its three version lines — `"version": "4.70.0"` and `"version": "1.96.0"` in the marketplace, `"version": "1.96.0"` in `plugin.json` — which 4.70.1 and 1.96.1 supersede by design. The merge's semantic reading — no sentence `origin/main` brought made false by this change — is the merger's and the wave's (its item 32), and the re-review's second half verified the resolutions (ledger line 108); this record did not re-read `origin/main`'s 930 added lines by subject.

## The gates

**The task gate chain, run here**, as one `&&` chain whose own exit status was read, from 05:11:23 to 05:13:17 UTC on 2026-11-17, `git status --short` printing nothing before and after:

```
./scripts/check-docs.sh --root . && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --root . --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/validate-catalog.py && node scripts/mermaid/check-mermaid.mjs --root . && python3 plugins/docs-workflows/scripts/key-discovery.py --selftest
```

It printed **`TASK_CHAIN_EXIT=0`**. Among its lines: check-docs' `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`, twice (each run also printing two `check 9 cost-emitting-commands assertion not applicable` lines, for `plugins/guideline-reviewers` and `plugins/prose-style`, which ship no `docs/reference/session-cost.md`); `PASS: no dash-form requirement IDs under .`, twice; `reference-parts check-parts: PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 117 `FLAG` lines (`grep -c '^FLAG'`), which it prints and does not fail on; `reference-parts check-citations: PASS -- 4 split reference(s)`; `reference-parts check-questions: PASS -- 37 command(s) load the question rules before their first question`; `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: all 50 mermaid blocks in 1254 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`; and `selftest: 76/76 passed`.

**Every `run:` step of `.github/workflows/validate-catalog.yml`, in order, as one `&&` chain.** Neither parent changed the workflow (`git diff --stat e1761361 HEAD -- .github` and `git diff --stat origin/main HEAD -- .github` print nothing). `grep -c 'run:'` on it gives 37; two of them, at lines 342 and 343, are inside a `#` comment and are not steps, so the file holds **35 steps**. With no `yaml` module in this container, the steps were extracted by batch 3's record's script — a step is a line whose first text is `run:`, after an optional `- `, and not a `#` comment; a block step (`run: |`) is the deeper-indented lines after it — which writes each to `$S/steps/step-NN.sh` and prints the chain, a `### step NN` line echoed before each, every step run as a workflow step's default Linux shell runs it, `bash --noprofile --norc -eo pipefail <step file>`. It extracts 35 steps at workflow lines 82, 85, 88, 91, 96, 99, 112, 123, 131, 144, 152, 157, 160, 162, 164, 171, 186, 194, 198, 205, 211, 218, 225, 235, 242, 249, 256, 263, 269, 277, 288, 295, 320, 345 and 354 — the two block steps at 171 and 295 among them, the mermaid parser's `npm ci` at 160. `ASSERT_PUBLISHED` was exported empty, as the workflow's `env:` sets it on a branch push. The chain ran as `bash -c "<the chain>"`, then `rc=$?; echo "CHAIN_EXIT=$rc steps=<the count of ### step lines>"`, from 05:13:31 to 05:25:17 UTC on 2026-11-17, `git status --short` printing nothing before and after, and printed **`CHAIN_EXIT=0 steps=35`**, all 35 `### step` lines reached. Among its lines: `0 error(s), 0 warning(s) across 1 repo(s).`; `PASS: no dash-form requirement IDs under .`; `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`; check-docs' `PASS: docs are consistent with the plugin(s) under …`, unarmed; the four `reference-parts` checks' PASS lines (36 generated files fresh; 4 split references' citations; 37 commands load the question rules; 24 run `branch-check`); `PASS: all 50 mermaid blocks in 1254 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)`; step 27's `selftest: 76/76 passed`, the key-discovery self-test; `run-state selftest: PASS (252 checks)`; `specs-git selftest: PASS (1201 checks)`; and `mutants: 23 checked, 0 stale`. This is the first run of the full chain on `aa8ba5b2`: the ledger records the touch-up's on `13fb0571` (line 110: *all 35 CI steps 0*) and the controller's gate chain on `aa8ba5b2` (line 114: *exit 0, self-test 76/76*), not the full chain.

**Re-run with these three records and the design's §12 in the work tree and staged**, the same task gate chain, from 05:30:11 to 05:32:05 UTC: **`TASK_CHAIN_EXIT=0`**, its lines as above save the mermaid gate's, `PASS: all 50 mermaid blocks in 1257 tracked markdown files parse`, the three records now among them (none holds a mermaid block). Beside it, `./scripts/check-id-grammar.sh --baseline` as the workflow runs it printed `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt`, and `git diff --cached --check` printed nothing. The task gate chain was run once more after this paragraph was written, with the same results.

## The self-test

`python3 plugins/docs-workflows/scripts/key-discovery.py --selftest` prints one `ok` line per case and `selftest: 76/76 passed`, exit 0, in about 2.0 s (`time`): `grep -c '^ok '` on its output gives 76. `grep -c '^def case_' plugins/docs-workflows/scripts/key-discovery.py` gives **76** — 42 at `e1761361` (`git show e1761361:<the script> | grep -c '^def case_'`), and 34 new, every one named `case_docs_…` (`grep -c '^def case_docs_'` gives 34); of the 42, a script comparing each case's body at `e1761361` and at the head finds `case_cli` alone changed, its pinned key sets extended for the new fields, as the plan allowed. The count by stage, from the ledger: 59 after Task 1's first commit (line 33), 60 after its fix round (line 42), 61 after Task 2 (line 46), 65 after Task 2's fix round (line 54), 76 after the wave (line 104), 76 after the touch-up (line 110). Its mutation runs — Task 1's, Task 2's, final review A's (19 of 24 killed, line 97) and the wave's (every mutant killed, its report) — were not re-run here.

## The fixed list

KD §1 holds the line `<!-- family-doc-paths -->` once, at KD:38, with a fenced block on KD:39 to :63; a script reading that block's non-empty lines as `<magic> <pattern>` pairs and loading KDP's `FAMILY_DOC_PATHS` (KDP:105) finds **23 entries** in each — 9 `literal`, all top-level (`.dev-workflows`, `.claude`, `docs`, `.docstack`, `.vale`, `_vale`, `vale.ini`, `.vale.ini`, `_vale.ini`), and 14 `glob` (`*.md`, `**/_snippets/**`, `**/mkdocs.yml`, `**/mkdocs.*.yml`, `**/docusaurus.config.[jt]s`, `**/docusaurus.config.[cm]js`, `**/sidebars.[jt]s`, `**/sidebars.[cm]js`, `**/_category_.json`, `**/_category_.yml`, `**/antora.yml`, `**/nav.adoc`, `**/.pages`, `**/SUMMARY.md`) — the two sets equal, and in the same order. The self-test case that compares them is **`case_docs_family_paths_match_the_reference`** (KDP:1215), which reads the reference beside the script, requires exactly one marker line, a fence under it and a closing fence, and asserts the sets equal and no line stated twice; it passes (`ok   case_docs_family_paths_match_the_reference`). The list went from the plan's 28 entries to 27 in Task 1's first build, literal `antora.yml` dropped since `**/antora.yml` covers the top level (ruling 7), and to 23 when generator files moved to any depth (ruling 8).

## The line forms

Every line form KD §5 and §6 quote was looked for, character for character after collapsing whitespace in both texts, in each command that prints it, by a script that takes each form as the one code span of its section beginning with a given prefix (fenced blocks set aside — they hold the calls, not printed lines) and counts it in DOC and RN. **21 forms**, in **32 form–command pairs**; **0 missing**:

- **§5, printed by both commands (11)**: the merged-pull-request suffix `; left out as documentation only: <those SHAs>`; the `read by path` line; the two `read whole` lines; the `Left out as documentation only:` line and its `<sha> <date> <subject>`; the `Not taken as content paths in <slug>:` line; the `<slug>: not read — no clone of the documentation-holding repository …` line; and the three reasons a left-out slug carries for `no content path`, `the content path is the whole repository` and `--exclude names it too` — each once in DOC and once in RN.
- **§5, printed by `/document` only (2)**: `Left out as never code: <the excluded slugs>` (`/release-notes` prints its own lower-case `left out as never code:` entry in its `Pull requests:` line, unchanged in kind since `e1761361`), and the step-4(c) reason `<slug> (no content path was known there when the scan ran; …)` — once each in DOC.
- **§6, printed by `/document` only (8)**: the six `Documentation paths check:` lines — paths outside, none outside, left out, read whole, `docs` null, not run — once each in DOC, and the two `<reason>` texts of the read-whole line, twice each in DOC.

KD §5's one other line form, `ok — <owners>, <queries> queries, <n> kept, <dropped_loose> loose matches dropped`, is in neither command verbatim: both write `<dropped>` for `<dropped_loose>`, as they did at `e1761361` (`git show e1761361:<file> | grep -o 'ok — <owners>[^`]*'` for each of the three). §6's remaining spans over 25 characters — `--docs-content=<content path>`, `git -C <docs_repo_path> merge-base <base_branch> HEAD` and `git diff --name-only --no-renames <base> <head>` — are arguments and commands, not printed lines.

## Versions

Each version from its `plugin.json` (`python3 -c "import json; print(json.load(open('plugins/<p>/.claude-plugin/plugin.json'))['version'])"`), its `.claude-plugin/marketplace.json` entry, and the first `## [` heading of its changelog (`grep -m1 -n '^## \[' plugins/<p>/CHANGELOG.md`), against `origin/main`'s (`git show origin/main:plugins/<p>/.claude-plugin/plugin.json`) and the base's:

| Plugin | `plugin.json` | marketplace | Changelog heading | `origin/main` `6d6518b7` | Base `e1761361` | First released on the branch as |
|---|---|---|---|---|---|---|
| `docs-workflows` | 1.41.0 | 1.41.0 | `8:## [1.41.0] — 2026-11-17` | 1.40.0 | 1.40.0 | 1.41.0 (`29a579c6`) |
| `workflows-core` | 1.96.1 | 1.96.1 | `8:## [1.96.1] — 2026-11-17` | 1.96.0 | 1.95.1 | 1.95.2 (`29a579c6`), renumbered in `e318d4f7` |
| `dev-workflows` | 4.70.1 | 4.70.1 | `8:## [4.70.1] — 2026-11-17` | 4.70.0 | 4.69.1 | 4.70.1 (`ca0ddc84`) |

Each of the three stands above `origin/main`'s. `git diff origin/main HEAD -- .claude-plugin/marketplace.json` changes exactly three lines, each a `version` line (`4.70.0` → `4.70.1`, `1.96.0` → `1.96.1`, `1.40.0` → `1.41.0`). **No other plugin took a version on the branch**: `git diff --stat origin/main HEAD -- plugins/<name>` prints nothing for `acli`, `guideline-reviewers`, `prose-style`, `security-workflows` and `product-workflows`, at 0.1.4, 1.2.10, 0.8.3, 0.12.6 and 3.84.0, `origin/main`'s own. **The changelogs**: for each of the three, a script found the first section to be the new one, dated 2026-11-17, and the file with that section removed equal to `origin/main`'s byte for byte (109, 195 and 301 headings at the head, one more than `origin/main`'s each); `grep -n '^## .*Unreleased' plugins/*/CHANGELOG.md | wc -l` gives 0. The coupling bullet for the release is CPL's last before the two `prose-style` bullets, *Update `workflows-core` 1.96.1 with `docs-workflows` 1.41.0*, naming `dev-workflows` 4.70.1 in its body; `git show origin/main:` of `.claude/rules/plugin-updates.md` and the four history files equals the head's (`git diff --stat origin/main HEAD -- .claude/rules/plugin-updates*.md` lists CPL alone). `1.95.2`, the release's first number, counts 0 in every tracked file (`git ls-files | xargs grep -noP '(?<![0-9.])1\.95\.2(?![0-9]|\.[0-9])'` prints nothing), before the commit that carries these records and the design's §12, which quote it as history.

## Budgets

`LC_ALL=C.UTF-8 wc -m`, since a bare `wc -m` counts bytes in this container (`wc -c` gives 36,229 for `CLAUDE.md`); `scripts/validate-catalog.py` sets `CLAUDE_MD_WARN = 36_000`, `CLAUDE_MD_MAX = 40_000` and `RULES_FILE_WARN = 20_000`, in characters (its lines 131 to 133). The files: `CLAUDE.md`, `.claude/rules/docs-workflows.md`, and every `.claude/rules/` file `git diff --name-only origin/main HEAD -- .claude CLAUDE.md` lists, which is CPL alone.

| File | `aa8ba5b2` | `origin/main` `6d6518b7` (`git show origin/main:<file> \| LC_ALL=C.UTF-8 wc -m`) | Base `e1761361` | Limit | Under the warning by |
|---|---|---|---|---|---|
| `CLAUDE.md` | 35,978 | 35,978 | 35,989 | warns 36,000, fails 40,000 | 22 |
| `.claude/rules/docs-workflows.md` | 19,998 | 19,998 | 19,998 | warns 20,000 | **2** |
| `.claude/rules/plugin-updates-coupling.md` | 19,503 | 18,175 | 18,293 | warns 20,000 | 497 |

**The two frozen files.** The plan's constraint is that `CLAUDE.md` and `.claude/rules/docs-workflows.md` do not change. **`git diff --stat e1761361 HEAD -- CLAUDE.md .claude/rules/docs-workflows.md` is not empty**: it prints `CLAUDE.md | 4 ++--`. That change is `origin/main`'s, brought in by the merge — two table cells of `CLAUDE.md`'s rules table, `references/threat-model-format.md` → `references/threat-*.md` and `1.90.2` → `1.91.1`, made by `6f9deb2f` and `8782cad2` (`git log --oneline e1761361..origin/main -- CLAUDE.md`), which is why the file measures 35,978 where the base measured 35,989. The branch's own changes touch neither file: `git diff --stat origin/main HEAD -- CLAUDE.md .claude/rules/docs-workflows.md`, `git diff --stat e1761361 29a579c6 -- …` (the branch before the merge) and `git diff --stat ffa8db0c HEAD -- …` (after it) each print nothing. `.claude/rules/docs-workflows.md` is byte-equal at the base, at `origin/main` and at the head.

**CPL over the build** (`git show <sha>:<file> | LC_ALL=C.UTF-8 wc -m`): 19,255 at `29a579c6`, 19,137 at `ffa8db0c`, 19,333 at `e318d4f7`, 19,493 at `0f61a5ec`, 19,503 at `13fb0571` and at `aa8ba5b2` — each the figure the ledger (lines 89, 103, 104) and the reports give for the same commit.

## The claim sweep's counts

Counted at `aa8ba5b2`, in `$S/main-tree` and in `$S/base-tree`, each string wrap-insensitively — whitespace collapsed across each whole file and across the string, a match mapped back to its source line — over `plugins/`, `CLAUDE.md`, `.claude/rules/`, `docs/maintainers/` and `README.md`, every file that decodes as UTF-8, each hit put in one bucket: *history* (any `CHANGELOG.md`, any `.claude/rules/plugin-updates-coupling*.md`), *generated* (`plugins/workflows-core/reference-parts/`), else *live*. The script is batch 3's record's, run as `python3 -I $S/wic.py '<string>' …` from the root of the tree measured:

```python
import os, re, sys
def files():
    for r in ["plugins", "CLAUDE.md", ".claude/rules", "docs/maintainers", "README.md"]:
        if os.path.isfile(r): yield r; continue
        for d, ds, fs in os.walk(r):
            ds[:] = sorted(x for x in ds if x not in ("node_modules", "__pycache__")); yield from (os.path.join(d, f) for f in sorted(fs))
T = []
for p in files():
    try: raw = open(p, encoding="utf-8").read()
    except (UnicodeDecodeError, OSError): continue
    out, idx, ws = [], [], False
    for k, ch in enumerate(raw):
        if ch.isspace():
            if ws: continue
            ws = True; out.append(" ")
        else: ws = False; out.append(ch)
        idx.append(k)
    b = "history" if p.endswith("CHANGELOG.md") or re.match(r"\.claude/rules/plugin-updates-coupling.*\.md$", p) else "generated" if "/reference-parts/" in p else "live"
    T.append((p, raw, "".join(out), idx, b))
for a in sys.argv[1:]:
    s = re.sub(r"\s+", " ", a).strip(); H = {"live": [], "generated": [], "history": []}
    for p, raw, c, idx, b in T:
        j = c.find(s)
        while j >= 0: H[b].append(f"{p}:{raw.count(chr(10), 0, idx[j]) + 1}"); j = c.find(s, j + 1)
    print(f"== {a!r}: " + ", ".join(f"{k} {len(v)}" for k, v in H.items()))
    for k, v in H.items(): print("".join(f"   {k}: {h}\n" for h in v), end="")
```

| String | Base `e1761361` (live / generated / history) | `origin/main` `6d6518b7` | `aa8ba5b2` | The hits at the base |
|---|---|---|---|---|
| `nothing the run holds tells the two apart` | 2 / 0 / 0 | 2 / 0 / 0 | **0 / 0 / 0** | KD:23 and `docs/maintainers/rationale.md:690` (DES §5.2: *it is false in two of the three layouts*) |
| `never the specs or the docs repository` | 2 / 0 / 0 | 2 / 0 / 0 | **0 / 0 / 0** | DOC:527 and RN:393, the scan's coverage clause in each Phase 3 |
| `the same exclusions` | 1 / 0 / 0 | 1 / 0 / 0 | **0 / 0 / 0** | DOC:539, the *Revise plan* re-scan |
| `other than the whole repository` | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** | — (Task 2's touch-up wording, retired by NB1, ruling 16) |
| `by its documentation paths` | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** | — (the noun the build retired for *read by path*; six copies at `e318d4f7`, the wave's report) |
| `1.95.2` | 0 / 0 / 0 | 0 / 0 / 0 | **0 / 0 / 0** | — (the release's first `workflows-core` number, 13 copies at `29a579c6`, `merge-report.md`) |

Each of the six counts **0** at the head in every bucket, so no remaining hit needs explaining. The middle column equals the base's for all six: `origin/main` changed none of them.

## What the design's §7 asks, and what covers it

DES §7 *Done when*: the script's self-test holds each of nine cases in a fixture repository, and, read from the commands, Phase 8.5's check and a walk of each layout, with live checks added. Each case below is in KDP and passes in the run above.

| §7 | Covered by |
|---|---|
| 1. **Second run**: a commit naming the key that touches only the site's folder, its navigation file and `.dev-workflows/` is left out; the scan finds none | **`case_docs_second_run`** (KDP:887): the commit touches `website/docs/intake.md`, `website/mkdocs.yml` and `.dev-workflows/docs-profile.yml`; `commits == []`, the commit is the one `docs_only` entry, `probe == []`, `scanned == 1`, `matched == 0`. Its shallow form: `case_docs_shallow_boundary_is_never_documentation_only` (KDP:1325) |
| 2. Code only is found; code and a page is found | **`case_docs_code_and_mixed_commits`** (KDP:903): both SHAs found `via: message`, `docs_only == []` |
| 3. A side branch whose net effect on code is nothing is still found (`--full-history`) | **`case_docs_side_branch_net_zero`** (KDP:912): both side commits found; `scanned == 3` pins the count walk's `--full-history` (ruling 6) |
| 4. The probe still shows a merge that names the key and brought in code | **`case_docs_probe_merges`** (KDP:927): the code merge and an octopus merge kept, the documentation merge dropped, the root commit kept, `probe_error` None; and `case_docs_a_merge_git_cannot_compare_stays_in_the_probe` (KDP:1404) |
| 5. A merged pull request that landed only documentation is listed and not read; one that landed code is read | **`case_docs_pull_requests`** (KDP:954), two squash landings and a mixed rebase; **`case_docs_a_merge_landing_read_by_path`** (KDP:1432), the merge-commit landings; and `case_docs_shallow_boundary_pull_request` (KDP:1359) |
| 6. A markdown file outside the documentation set is code | **`case_docs_markdown_outside_the_set_is_code`** (KDP:980) |
| 7. No content path: the repository is left out whole and named as today | **`case_docs_no_content_path`** (KDP:987): `excluded == ["site"]`, `left-out`, `no content path`, no `repos[]` entry, its pull request dropped; where the record names it, **`case_docs_named_repository_is_read_whole`** (KDP:1114), the outcome ruling 12 added |
| 8. A second clone of the documentation-holding repository takes the same rule (L10) | **`case_docs_second_clone_by_slug`** (KDP:1003); and `case_docs_a_clone_given_below_its_top_level` (KDP:1420) |
| 9. Top-level markdown alone is left out; markdown below the top level, outside the set, is found | **`case_docs_top_level_markdown`** (KDP:1018) |
| Phase 8.5's check (L9) on a commit holding a path outside the set | **`case_docs_check`** (KDP:1174): `outside == ["assets/shot.png"]`, `[]` with `--docs-content assets` and under `left-out`, a rename as both paths; in the command, DOC:1428 to :1436 (Step 1 item 4, its six lines, after the commit and before the push offer) |
| A walk of each layout, stating what is passed and printed | The passages: `/document`'s step 3a call (DOC:256), Phase 3's *What every scan from here on passes* (DOC:543 to :550) and *Say how the documentation-holding repository was read* (DOC:581 to :597); `/release-notes`' *What this scan passes* (RN:414 to :429) and its *Say how* (RN:462 to :483). Walked by Task 3's implementer — site in a subfolder; at the top level with an in-repo profile; with no profile; a documentation-only repository with a profile; a repository `implementation.md` names (`task-3-report.md` §3) — and Task 4's, with fixture repositories — a subfolder root, a top-level root with a profile, one without, `--no-docs` (`task-4-report.md` §3). **Not re-walked here** |
| Live checks for each | TT:239 to :251 (below) |

## The reviews

From the ledger, whose counts are the reviews'; read here, not re-derived. Each review's findings by severity as the ledger gives them.

| Review | Model | Head reviewed | Verdict and findings | Fix rounds | Final state |
|---|---|---|---|---|---|
| Pre-flight scan of the plan | the controller | the plan (`294a29f1`) | eleven rows; one conflict, the comparison case's task, settled in the table and the plan edited (`c64eaf87`); rulings 1 to 5 (lines 12 to 30) | — | — |
| Task 1, the script | Opus | `21c35f9b`, range `c64eaf87..21c35f9b` (after the timing change, ruling 6) | spec met; 1 Important (plan-mandated), 3 Minor, 4 cross-task notes (line 37) | 1: `9d7df2a3`, re-reviewed on Sonnet (4 addressed, 0 open, line 44) | clean (line 45) |
| Task 2, the reference and IF §4 | Opus | `d55b8cec`, range `94455807..d55b8cec` | spec not met: 2 Important (one plan-mandated), 5 Minor (line 49) | 1: `6555b558`, re-reviewed on Opus (7 addressed, 0 open; 5 Minor, 1 nit, 3 out-of-scope observations, lines 55, 56); touch-up `399570c7`, narrow-checked on Opus (items 1 to 9 addressed; 1 Important, NB1, and 1 Minor, NB2, line 60); touch-up 2 `918f5e1c`, with no narrow check (line 64) | clean after one round and two touch-ups (line 65) |
| Task 3, `/document` | Opus | `0d4ad93a`, range `399570c7..0d4ad93a` | spec not met: 1 Important, 5 Minor (line 67) | 1: `39ede2f5`, re-reviewed on Opus (7 addressed, 1 open; 2 Minor, 2 out-of-scope, line 81); 2: `b223b25e`, a touch-up, narrow-checked on Sonnet (7 addressed, 0 open; 1 Minor, line 86) | clean after two rounds, 1 Minor deferred to the wave (lines 87, 88) |
| Task 4, `/release-notes` | Opus | `c470e915`, range `918f5e1c..c470e915` | spec met, Approved: 0 Critical, 0 Important, 5 Minor (line 74) | touch-up `a3f0cab4`, with no narrow check (line 78) | complete (line 79) |
| Task 5, the release | Opus | `29a579c6`, range `b223b25e..29a579c6` | 1 Critical (C1, `origin/main` moved), 1 Important (I1), 8 Minor (line 94) | none of its own: to the wave (ruling 23) | fixed in the wave (line 115) |
| Final review, half B — the two commands and the pages | Fable | `29a579c6`, range `e1761361..29a579c6` | ready with fixes: 0 Critical, 4 Important (B1 to B4), 4 Minor; the deferred minor triaged *fix* (line 93) | the wave (rulings 24, 29) | below |
| Final review, half A — the script and its contract | Fable | `29a579c6` | ready with fixes: 0 Critical, 2 Important (A1, A2), 6 Minor; 19 of 24 mutants killed (line 97) | the wave (rulings 26 to 29) | below |
| The merge of `origin/main` | Opus (merger) | `29a579c6` with `6d6518b7` | five files conflicted, both sides kept; `ffa8db0c`, then `e318d4f7` renumbering to 1.96.1; all 35 CI steps exit 0 (line 103) | — | read by the wave's re-review, half 2 (line 108) |
| The final fix wave | Opus (fixer) | from `e318d4f7` | 32 items in six commits, `f5f7c2bf` to `0f61a5ec`; two not exactly as ruled (line 104) | — | rulings 30, 31 |
| The wave's re-review, half 1 — the script, the reference, the agent | Opus | `0f61a5ec`, range `e318d4f7..0f61a5ec` | its items addressed; 0 Critical, 0 Important, 5 Minor; the parked `scan_ref` reasoning holds (line 108) | the touch-up (ruling 32) | — |
| The wave's re-review, half 2 — the commands, the pages, the records, the merge | Opus | the same | its items addressed; 0 Critical, 0 Important, 9 Minor (N1 to N9), 1 out-of-scope observation; the merge verified (line 108) | the touch-up (ruling 32) | — |
| The touch-up | Opus (fixer) | from `0f61a5ec` | 15 items in two commits, `a9454f0a` and `13fb0571` (line 110) | — | — |
| The narrow check of the touch-up | Opus | `13fb0571`, range `0f61a5ec..13fb0571` | all fifteen addressed; 0 Critical, 0 Important, 6 Minor (M1 to M6), each with a replacement sentence (line 113) | the controller's six sentences, `aa8ba5b2` (ruling 34) | read by no reviewer after they were applied (line 114) |

Summed from the rows: **1 Critical**, **12 Important** (Task 1's 1, Task 2's 2 and NB1, Task 3's 1, Task 5's 1, B's 4, A's 2) and **65 Minor** (3, 5, 5, 1, 5, 2, 1, 5, 8, 4, 6, 5, 9, 6, in the table's order), beside one nit, six out-of-scope observations and Task 1's four cross-task notes. **The controller's six sentences**, `aa8ba5b2`: `git show --stat` lists four files and eight changed lines — `docs/maintainers/rationale.md` (1), DW-CL (2), DOC (4: its lines 406, 554 to 555 and 715) and WC-CL (1); `git diff --word-diff=plain 13fb0571 aa8ba5b2` shows only insertions and replacements inside those sentences. The narrow check's findings are not saved as a file in the run's directory (its listing holds none), so the sentences were compared here with nothing but the ledger's description (line 114); no reviewer read them after they were applied.

## What remains open by design

- **The first-run limit (L3).** Where no content path is known in the documentation-holding repository — a site at its top level with no docs profile, as on the first `/document` run there, which generates the profile after its scan — or one is the whole repository, it is left out whole as before, or read whole where `implementation.md` names it, and the run says why. Recorded in `docs/superpowers/to-fix.md:269` (the closed entry's *What remains*), KD:67 to :70 and DW-CL:34.
- **The specs repository (L6)** keeps its whole exclusion: code committed inside the specs tree's repository is never scanned where `implementation.md` does not name it — a layout the family does not support. `to-fix.md:269`, KD:24, DW-CL:37.
- **Parked** (ledger line 116): A-Minor 6's second half, a count walk that times out discarding that clone's scan (ruling 28; DW-CL:40); and the `scan_ref` residual gap, an inline-profiling run moving `HEAD` between step 3a's scan and Phase 5 (ruling 30), checked by the re-review and found to hold, recorded in the ledger and the rulings file only.
- **Not filed** (line 116): `/release-notes`' Branch-name probe report line, which can read *not fired — the scan matched in every repository* where the scan read no repository — older than this change and not an ordinary setup (line 72).
- **The accepted costs**, stated in DW-CL's *Known limits*: a commit in a documentation-only repository that touches a path outside the set counts as built work (L4, DW-CL:36); `/release-notes`' first run after the release in such a layout can describe work an earlier note covered (DW-CL:35); a shallow clone's boundary (DW-CL:39); `scan_ref`'s reach (DW-CL:38).
- **The internal editions**: DES §10 says both carry `key-discovery.py` and the same exclusion, and the fix is ported to each after it merges here, as its own change.
- `.claude/rules/docs-workflows.md` stands 2 characters under its warning, and `CLAUDE.md` 22.

## What was not verified

- **The live checks have not been run.** TT:235 opens the section *DOCS-IN-CODE-REPO-SCAN — `docs-workflows` 1.41.0, `workflows-core` 1.96.1, `dev-workflows` 4.70.1*, whose intro (TT:237) says *no item below has been run*; it holds **13** checks (`awk '/^## DOCS-IN-CODE-REPO-SCAN/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'` gives 13, TT:239 to :251) — nine Task 5 added, four the wave added (TT:248 to :251). The change also **corrected four checks** of the LADDER-ORDER batch 3 section, TT:206, :207, :211 and :214, which expected the old `Left out as never code:` line, and that section's intro, TT:204 (`git diff -U0 origin/main HEAD -- docs/superpowers/to-test-on-real-project.md`). **None of the 17 has been run** on a real project, and the ledger records no choice of when they run.
- **The layout walks** of DES §7 are the implementers' (`task-3-report.md` §3, `task-4-report.md` §3), not re-walked here, and every walk a reviewer made is theirs.
- **The controller's six sentences** (`aa8ba5b2`) were read by no reviewer after they were applied; this record ran the full chain on them, and found the word diff to touch only those sentences, but holds no copy of the narrow check's wording to compare them with.
- **The merge's semantic reading** — that nothing `origin/main` brought is made false by this change — is the merger's and the wave's (item 32); this record re-checked the merge mechanically (*The merge*) and did not re-read `origin/main`'s added lines by subject.
- **Not re-derived here:** the mutation runs and the timings in the reports (6.2 s, 2.5 s, 3.1 s on `/workspace/docs`); the scratch fixtures behind the reports' and reviews' findings; the reviews' finding counts, which are the ledger's; the implementers', the fixers' and the merger's earlier chain runs. This record, the rulings summary, the ledger copy and the design's §12 were not reviewed before they were committed.

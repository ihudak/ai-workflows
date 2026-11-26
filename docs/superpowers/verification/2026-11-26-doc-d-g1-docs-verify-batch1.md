# DOC-D-G1 sub-project 2, batch 1 — the backlog runs' shared steps and the line reader's new flags — verification record

**Plan:** `docs/superpowers/plans/2026-11-17-doc-d-g1-docs-verify.md`, batch 1 (Tasks 1.1 to 1.5), with its amendments `6018f8b73` and `3b08f614a`. **Design:** `docs/superpowers/specs/2026-11-17-doc-d-g1-sp2-docs-verify-design.md`, revision 3, its S2-D15 (*Batches and releases*), whose batch 1 leaves `/docs-write`'s behaviour unchanged — "D15" below, as in the reviews. **Release:** `docs-workflows` 1.44.0, its changelog section dated 2026-11-26; no other plugin. **Branch:** `feat/doc-d-g1-docs-verify`, cut from `main` at `74d3e8d1e`, with `origin/main` at `f3702976a` merged into it at `eeb2e54db`. **Measured at `3b08f614a`**, the head, after the final whole-branch review, whose three findings were all in the pull request's text, so no fix wave touched the tree. Every figure below was obtained on that tree, on 2026-11-26, by the command beside it; none is copied from the close report, the reviews or another record. Where a figure or a reading is a review's and was not re-run here, the sentence says so.

The record holds **41 checks**, C1 to C41. Each gives the check, the command that produces it, the value expected — the figure the shipped text or the design states, re-derived by running that command at the head — and the result.

## Where and how it was measured

One 12-core machine (`nproc`), Python 3.15.2, git 2.56.1, uid 1000 (`id -u`), and **no `node` or `npm`** (`command -v node npm` prints nothing). Every command ran from the worktree root, `/home/ihudak/dev/ai-tools/ai-workflows-wt/doc-d-g1-verify`, unless it says otherwise.

`$S` below is a scratch directory outside the repository. `$S/main` is `origin/main` unpacked there with `git archive origin/main | tar -x -C $S/main`. The harnesses named below are scratch scripts, not part of the tree: `render.py`, `stays.py`, `programs.py`, `fixrun.py`, `count.py` and `probe.py` are the close task's, and `progs.py`, `battery.py` and `run10.py` the final review's, each copied into a fresh `$S/vr/` and run there on fresh inputs. Those inputs are `git show origin/main:<DW>`, `git show HEAD:<DW>`, `git show HEAD:<BR>` and, for C24, `git show origin/main:<BLP>` and `git show HEAD:<BLP>`. The sha256 of each HEAD copy equals the worktree file's. The rendered BR the harness writes is byte-equal (`cmp`) to the one the close task's run wrote at `1ba24663d`, since `git diff --stat 1ba24663d 3b08f614a` lists the plan alone.

Abbreviations, every line number at `3b08f614a`:

| Short | File |
|---|---|
| DW | `plugins/docs-workflows/commands/docs-write.md` |
| BR | `plugins/docs-workflows/references/docs-iteration/backlog-run.md` |
| FH | `plugins/docs-workflows/references/finish-and-handoff.md` |
| UB | `plugins/docs-workflows/references/docs-iteration/unit-brief.md` |
| EC | `plugins/docs-workflows/references/docs-audit/evidence-contract.md` |
| VIS | `plugins/docs-workflows/references/docs-workflow/visibility.md` |
| BLP | `plugins/docs-workflows/scripts/backlog-lines.py` |
| BKR | `.claude/rules/docs-workflows-backlog.md` |
| CL | `plugins/docs-workflows/CHANGELOG.md`, its `## [1.44.0] — 2026-11-26` section |
| TT | `docs/superpowers/to-test-on-real-project.md` |
| SDD | `.superpowers/sdd/2026-11-17-doc-d-g1-docs-verify/`, the run's directory, git-ignored (`.gitignore:18`) |

## 1. The tree

- **C1. The branch, the head, a clean tree.** Commands: `git branch --show-current`, `git rev-parse HEAD`, `git status --short`. Expected: `feat/doc-d-g1-docs-verify`, `3b08f614a`, nothing. Result: `feat/doc-d-g1-docs-verify`, `3b08f614a596a2f7dd5e6b267052fa1bd45f3b9e`, nothing, before the checks and after them.
- **C2. `main` has not moved.** Commands: `git fetch origin`, then `git rev-parse origin/main`, `git merge-base origin/main HEAD` and `git log --oneline HEAD..origin/main | wc -l`. Expected: one commit for both, and 0, so no merge is owed and the release's number stands. Result: `git fetch` updated no ref; both print `f3702976a0474d9ced20fc9a57abef439b97c002`; 0. The next free `docs-workflows` minor above `origin/main`'s 1.43.3 is 1.44.0 (C30).
- **C3. The branch's commits.** Commands: `git log --oneline origin/main..HEAD | wc -l`, `git log --oneline --first-parent origin/main..HEAD | wc -l` and `git log --merges --format='%h %p' origin/main..HEAD`. Expected: one merge, of `origin/main` at `f3702976a`. Result: 21, 21, and `eeb2e54db cac361af0 f3702976a`. The merge brought 134 commits (`git log --oneline cac361af0..f3702976a | wc -l`). The 21, by task:
  - the design and the plan: `b90e55c26`, `045fda591`, `929ff00a4`, `2ca797de5` (the design, its two reviews' revisions and its approval), and `fe5cc8f8e`, `bde7839f3`, `b21049881` (the plan, its two reviews' revisions);
  - Task 1.1, the line reader's flags: `024fb8c43`, fix round `cac361af0`, the controller's `565c73c18`;
  - the merge of `origin/main`: `eeb2e54db`;
  - Task 1.2, the extraction: `06fdd6398`, the plan amendment `6018f8b73`, fix round `2e556971e`, the controller's `fe3343643`;
  - Task 1.3, FH §6: `70d473a52`, the controller's `2a8f8b184`;
  - Task 1.4, the sweep and the release: `8d73247c6`, fix round `71106bfa5`, the controller's `1ba24663d`;
  - Task 1.5, the close: no commit; the plan amendment it reported, `3b08f614a`.
- **C4. The files.** Command: `git diff --stat origin/main...HEAD | tail -1`, and `git diff --name-only origin/main...HEAD`. Expected: batch 1's files and no other plugin's. Result: `23 files changed, 2520 insertions(+), 209 deletions(-)`, before the commit that carries this record. The 23 are 12 under `plugins/docs-workflows/` (DW; BR, new; FH; UB; EC; VIS; BLP; `README.md`; `docs/README.md`; `docs/reference/references.md`; the changelog; `plugin.json`), four rules files (`docs-workflows-backlog.md`, `docs-workflows.md`, `threat-model.md`, `workflows-core-read-only.md`), `CLAUDE.md`, `.claude-plugin/marketplace.json`, and five under `docs/superpowers/` (the plan, the design, `reviews/2026-10-26-feature-gaps-review.md`, `to-fix.md`, TT): 12 + 4 + 1 + 1 + 5 = 23. `git diff --name-only origin/main...HEAD -- 'plugins/*/scripts/*' 'plugins/*/agents/*' 'plugins/*/hooks/*' 'plugins/*/skills/*'` lists BLP alone: no agent, hook or skill changed.

## 2. The gates

- **C5. Every `run:` step of `.github/workflows/validate-catalog.yml`, as one `&&` chain, then `claude plugin validate .`.** The steps were extracted by a script (`$S/vr/extract.py`): a step is a line whose first text is `run:`, after an optional `- `, and not a `#` comment, and a block step (`run: |`) is the deeper-indented lines after it. `grep -c 'run:'` gives 39 on the workflow, two of them inside the comment at its lines 358 to 360, so it holds **37 steps**, at lines 82, 85, 88, 91, 96, 99, 112, 123, 131, 144, 152, 157, 160, 162, 164, 171, 186, 194, 198, 205, 211, 218, 225, 235, 242, 249, 256, 263, 270, 276, 284, 293, 304, 311, 336, 361 and 370; the branch did not change it (`git diff --name-only origin/main...HEAD -- .github` prints nothing). The three mermaid steps were left out (C7). The other 34 ran in file order, from the worktree root, as one `&&` chain under `set -o pipefail`, each as a workflow step's default Linux shell runs it, `bash --noprofile --norc -eo pipefail <step file>`, with `ASSERT_PUBLISHED` exported empty, as the workflow's `env:` sets it on a branch push; `./scripts/check-id-grammar.sh --baseline` ran alone, as its own step 5. `claude plugin validate .` came last, then `echo "EXIT=$rc"` of the chain's own status. It ran from 12:02:26 to 12:38:18 UTC, `git status --short` printing nothing at its start and end. Expected: EXIT=0. Result: **`EXIT=0`**, all 35 `###` lines reached, each step's exit 0:

  | # | Line | Step | Time | Its last line |
  |---|---|---|---|---|
  | 1 | 82 | Self-test the catalog validator | 0 s | `SELFTEST PASS` |
  | 2 | 85 | Validate manifests and catalog | 2 s | `0 error(s), 0 warning(s) across 1 repo(s).` |
  | 3 | 88 | Self-test the requirement-ID gate | 0 s | `SELFTEST PASS` |
  | 4 | 91 | Check requirement-ID grammar | 0 s | `PASS: no dash-form requirement IDs under .` |
  | 5 | 96 | Check the spec-ID census against its baseline | 0 s | `PASS: the spec-ID census under . equals scripts/spec-id-baseline.txt` |
  | 6 | 99 | Self-test the docs gate | 1,511 s | `SELFTEST PASS` |
  | 7 | 112 | Check docs against the plugin tree | 193 s | `PASS: docs are consistent with the plugin(s) under …`, its other lines the two check 9 notes of C6 |
  | 8 | 123 | Self-test the reference-parts gate | 10 s | `SELFTEST PASS` |
  | 9 | 131 | `check-parts` | 0 s | `PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh`, after 127 `FLAG` lines, which it prints and does not fail on |
  | 10 | 144 | `check-citations` | 5 s | `PASS -- 4 split reference(s)` |
  | 11 | 152 | `check-questions` | 0 s | `PASS -- 38 command(s) load the question rules before their first question` |
  | 12 | 157 | `check-branch-check` | 0 s | `PASS -- 24 command(s) run branch-check` |
  | 13–15 | 160–164 | the mermaid gate | — | not run here: no `node` (C7) |
  | 16 | 171 | Self-test the session-cost window splitter | 1 s | `SELFTEST PASS` |
  | 17 | 186 | Self-test the secret scan | 1 s | `secret-scan selftest: PASS` |
  | 18 | 194 | Self-test the run-state file | 3 s | `run-state selftest: PASS (252 checks)` |
  | 19 | 198 | Self-test the design pieces reader | 5 s | `pieces selftest: PASS (77 checks)` |
  | 20 | 205 | Self-test the architecture harvest | 1 s | `architecture-harvest selftest: PASS` |
  | 21 | 211 | Self-test the promotion signals | 1 s | `promotion-signals selftest: PASS` |
  | 22 | 218 | Self-test the proposal record | 1 s | `selftest: 44/44 passed` |
  | 23 | 225 | Self-test the ledger evidence writer | 0 s | `selftest: 20/20 passed` |
  | 24 | 235 | Self-test the bundle scanner | 1 s | `SELFTEST PASS (102 cases, 0 failed)` |
  | 25 | 242 | Self-test the security register | 8 s | `selftest: 121/121 passed` |
  | 26 | 249 | Self-test the weakness classes reader | 2 s | `selftest: 57/57 passed` |
  | 27 | 256 | Self-test the key discovery | 5 s | `selftest: 76/76 passed` |
  | 28 | 263 | Self-test the backlog line reader | 3 s | **`selftest: 75 passed`** |
  | 29 | 270 | Self-test the bounded run | 11 s | `SELFTEST PASS (23 cases, 0 failed)` |
  | 30 | 276 | Self-test the document lineage script | 2 s | `selftest: 62 passed` |
  | 31 | 284 | Self-test the tree snapshot | 1 s | `PASS` |
  | 32 | 293 | Self-test the run folder | 33 s | 68 lines, each `PASS` (`grep -c '^PASS'` 68, `grep -vc '^PASS'` 0) |
  | 33 | 304 | Self-test the status line's plan usage | 2 s | `statusline selftest: 19 passed, 0 failed` |
  | 34 | 311 | Every plugin's copied scripts are the same | 0 s | no output: no `::error` line |
  | 35 | 336 | Self-test the session branch | 85 s | `session-branch selftest: PASS` |
  | 36 | 361 | Self-test the specs-repo git primitives | 264 s | `specs-git selftest: PASS (1201 checks)` |
  | 37 | 370 | Check the specs-git mutants are not stale | 0 s | `mutants: 23 checked, 0 stale` |
  | — | — | `claude plugin validate .` | 1 s | `✔ Validation passed` |

  This record's first draft stood in the work tree, untracked, during part of step 6, which builds and reads its own fixtures, and was moved out of the tree before step 7 began, so every step from 7 on ran on the clean tree. The chain was run once more with this record in the work tree and staged, before its commit (*After this record was written*, below).
- **C6. The docs check armed as the push to `main` arms it.** Command: `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`. Expected: PASS, check 18 finding no `— Unreleased` section. Result: exit 0 in 207 s, `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`, its only other lines the two `check 9 cost-emitting-commands assertion not applicable` notes, for `plugins/guideline-reviewers` and `plugins/prose-style`.
- **C7. The mermaid gate is CI's.** The workflow's three mermaid steps (its lines 160, 162 and 164: `npm ci --prefix scripts/mermaid …`, `node scripts/mermaid/check-mermaid.mjs --selftest` and `--root .`) need `node`, which this machine lacks, so they were not run here and CI runs them on the pull request. In their place, by hand: `command grep -c '^ *```mermaid'` over each of the 20 markdown files `git diff --name-only origin/main...HEAD -- '*.md'` lists gives 0 in each, and `git diff origin/main...HEAD -- '*.md' | command grep -c '^[-+].*```mermaid'` gives 0. Expected: no diagram edited. Result: none is; this record holds none either.

## 3. The self-test

- **C8. The count at the head.** Command: `python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest`. Expected: 75, CL's "The self-test grows from 57 cases to 75". Result: exit 0, last line `selftest: 75 passed`; `command grep -c '^ok '` on its output gives 75, and `command grep -vc '^ok '` gives 1, that summary line.
- **C9. The count at the base.** Command: `cd $S/main && python3 plugins/docs-workflows/scripts/backlog-lines.py --selftest`, run inside the archive, since the script reads the references beside it. Expected: 57. Result: `selftest: 57 passed`.
- **C10. Task 1.1's eighteen cases each print `ok`.** Command: `command grep -cx 'ok   <name>'` on C8's output, for each of `own_moves_open_draft_branch`, `own_moves_real_move`, `own_moves_no_merge_base`, `own_moves_merge_base_unreadable`, `own_moves_unchanged_without_flag`, `own_moves_bad_args`, `edit_from_refused`, `edit_from_ok`, `edit_walkthrough_unset`, `edit_walkthrough_other`, `edit_walkthrough_same`, `edit_no_walkthrough_key`, `edit_block_sets`, `edit_block_refused`, `edit_no_blocked_by_key`, `edit_record_noop`, `edit_new_flags_bad_args` and `visibility_marker_pinned`. Expected: 1 each. Result: 1 for each of the 18.
- **C11. The cases the self-test runs.** Command: a script reading the names in BLP's `CASES` tuple (BLP:2438), at the head and in `$S/main`. Expected: 57 + 18 = 75, the 18 added, none removed. Result: 75 distinct at the head, 57 at the base; the names the head adds are exactly C10's 18, in that order; none of the 57 is removed. `command grep -c '^def case_'` gives 75 and 57 too.

## 4. The pins

What `case_marker_phrase_pinned` and `case_visibility_marker_pinned` assert, counted here by hand; both print `ok` in C8.

- **C12. The marker phrase.** Command: ``command grep -c "character for character: \`(" <BR> <DW>``, and the same on `$S/main`'s DW. Expected: 2 and 0, BR's §10.1 and §10.2 programs and no program in DW (CL: "finds no program searching by it in `docs-write.md`"). Result: BR 2, DW 0; DW at `origin/main` 2, the two programs the move took.
- **C13. The visibility marker's literal.** Command: `command grep -cF '"<!-- docs-visibility: internal -->"' <BR> <DW>`, and on `$S/main`'s DW. Expected: 1 and 0 (CL: "finds the literal nowhere in `docs-write.md`"). Result: BR 1 (BR:125, §10.2's program), DW 0; DW at `origin/main` 1. The marker unquoted stands in DW at :254 and :266 as prose naming what the run requires on a page, which the pin, matching the quoted literal, rightly leaves alone.
- **C14. VIS §5 states the marker on a line of its own.** Command: `awk '/^## 5\. /{f=1} /^## 6\. /{f=0} f' <VIS> | command grep -cxF '<!-- docs-visibility: internal -->'`. Expected: 1. Result: 1, at VIS:102.

## 5. D15 — `/docs-write` unchanged

- **C15. The rendering.** Command: `python3 -I render.py`, which writes BR with `/docs-write`'s values — `<RUN>` → `DOCS_WRITE`, `<run>-` → `dw-docs-write-`, `'<plugin root>/…'` → `"${CLAUDE_PLUGIN_ROOT}/…"`, the reach set → "the unit's page and its placement targets" — and token-diffs each of §2 to §10.2 against `origin/main`'s DW:22, :24–63, :160, :162 and :164–168, :144, :148, :231–235, :263 and :265, :110–116 and :383–395. Expected: every difference a bold lead the heading now carries, a re-point of a phase reference to a parameter, a re-point a task review ruled, or text that stays in DW (C16); none a rule. Result, tokens before → after and differences: §2 330 → 282, 3; §3 662 → 662, 4; §4 62 → 60, 1; §5 923 → 774, 8; §6 164 → 128, 4; §7 138 → 80, 4; §8 167 → 134, 3; §9 359 → 244, 3; §10.1 159 → 63, 4; §10.2 179 → 144, 3; **37 in all**. Each of the 37 was read here, and each falls in one of those four classes:
  - the bold leads `**Untrusted input.**`, `**Classes and tests.**`, `**The base.**`, `**Sources.**`, `3. **No page carries its id.**`, `7. **Its walkthrough, …**`, `1. **Artifacts.**`, and the leads of Phase 0 step 12 and Phase 9 step 1;
  - re-points to a parameter: "(Phases 0, 2 and 7)" → "(the phases its command names)", "(Phase 0 step 7)" → "(the command's content roots)", "Phase 0 step 9's" → "the command's", "Phase 4's" → "the scan phase's", twice, "(Phase 4 step 3)" → "(the scan phase's handling of a return)", and the *Copies* file list → "each file its command names";
  - re-points a review ruled: "this body" → "this file or of its command's body", "with the reason above" → "with `DOCS_WRITE_EVIDENCE`, its reason a recorded path that fails the clone test", "the id" → "the walkthrough id", "neither" → "outside the reach set", "run as it stands:" → "run as it stands but for `<plugin root>`, …", "Phase 9's" → "§10.2's", §10.2's "This program tests that" and "— fails:", and §6's closing sentence, "The read gives, per candidate, *equal* … beside each program's `exit`";
  - text staying in DW: the full `DOCS_WRITE_ARTIFACT`, `_EVIDENCE`, `_PAGE_TAGGED`, `_WALKTHROUGH` and `_NO_MARKER` lines, the who-sees-what sentence, the three consequences and the third reach test.

  The final review's own tokeniser gives 39 differing spans in the same classes (`final-review-batch1.md`, D15 part 1).
- **C16. The sentences that stay in DW.** Command: `python3 -I stays.py`, which counts each of 16 sentences the move left in DW, whole, in DW and in BR. Expected: 1 and 0 each. Result: 1 and 0 for all 16, at DW:22 (who sees what; "being Phases 0, 2 and 7"), :119 (the `DOCS_WRITE_ARTIFACT` line), :120 (`DOCS_WRITE_EVIDENCE`), :99 (unit test 3's consequence; the `PAGE_TAGGED` line), :103 (the `WALKTHROUGH` line; unit test 7's consequence), :183 ("a stop (*Units and their ends*)"; Phase 4 step 1's consequence), :211 (*Copies*' files), :213 (the third reach test), :71 (step 12's lead; the `NO_MARKER` line) and :331 (the Phase 9 rationale; "Exit 0 holds; exit 1 is a unit-level end."). The three consequences — a candidate that cannot be read counts as a match, a walkthrough's `result:` values are ignored, and an `ard.md` neither the commit nor the working tree holds is reported while the unit goes on — are among them.
- **C17. The moved programs, byte for byte under R2.** Command: `python3 -I programs.py`, which cuts each program from `origin/main`'s DW, gives it R2's `'<plugin root>/…'` form where it takes the root, and counts it whole. Expected: each once in BR, none left in DW, and only the plugin-root argument changed. Result, for the class test (13 lines), the containment test (4), §6's page-tag read, §7's admission, §10.1's read, §10.2's test (7), §9's `tree-snapshot.py … snapshot` and `… compare` lines, and §9's `command cp -- …` / `command mkdir -p -- …` span: 1 in old DW, 1 in BR, 0 in DW now, each. R2 changes four of the nine — §10.1, §10.2 and the two `tree-snapshot.py` lines — and no other byte.
- **C18. Every program and command span of the old command.** Command: `python3 -I progs.py`, which takes every fenced `bash` block, inline `python3 -I -c` program, `tree-snapshot.py` call and `command`, `git` or `test` span from old DW, new DW and BR. Expected: each old one in new DW or in rendered BR. Result: 51 in old DW, 23 in new DW, 29 in BR; **0 missing**; one span new, BR §1's bare `command mktemp`.
- **C19. The programs DW keeps.** Same command as C17. Expected: 1 and 1. Result: the third reach test's program, the `unfinished/` listing and Phase 0 step 1's here-document each stand once in old DW and once in DW now, and the third reach test's 0 times in BR.
- **C20. The moved programs, run old against new.** Command: `python3 -I fixrun.py <worktree>`, which runs each moved program in its `origin/main` DW form (`${CLAUDE_PLUGIN_ROOT}` substituted) and its BR form (`'<plugin root>'` given the same root) through `bash -c`, on a throwaway repository holding a CRLF page tagged by hand, a body line that only looks like a tag, an untracked `café.md`, a page with the marker, a CRLF internal page with both markers, a page without the marker, a walkthrough and a symbolic link to it, and a plugin root whose `evidence-contract.md` lacks the phrase. Expected: identical exit, stdout and stderr in every case. Result: **26 of 26 identical** — the marker read 0 and 1; the marker test 0, 0, 1, 1, 1; the page-tag read printing `{"exit": 0, "paths": ["docs/guide/caf\u00e9.md", "docs/guide/other.md", "docs/guide/tagged.md"]}` (`json.dumps` escaping the `é` of the untracked `café.md`), then `exit` 1 and 128; the admission 0, 1, 1; the class test 1, 0, 1, 0, 1, 1, 1, 0; the containment test `outside`, `inside`, `equal` and, for an empty path, exit 2; and a `PATH` without `python3`, exit 127 in both.
- **C21. R2 under a hostile plugin root.** Command: `python3 -I run10.py '<root>'`, the final review's script, with BR's §10.1 and §10.2 programs taken from a copy of the plugin's `references/` under a root named ``odd $(touch PWNED) `touch PWNED2` it's``, the root single-quoted as BR §2 says. Expected: the read exits 0, the test gives each page its expected exit, and nothing in the root runs. Result: §10.1 exit 0; §10.2 on a public page with the marker 0, one whose first body line is not the marker 1, an internal page with both markers 0, an internal page lacking the visibility marker 1, a CRLF page with a byte-order mark 0, a page with no frontmatter 1; neither `PWNED` nor `PWNED2` exists afterwards, in the working directory or under the root (`ls -A`).
- **C22. The stop codes.** Command: `command grep -o 'DOCS_WRITE_[A-Z_]*' <file> | sort -u`, over old DW, DW now and rendered BR, then `diff`. Expected: CL's "the same 31 stop codes", the set unchanged. Result: 32 entries in old DW and 32 in DW now — the 31 codes and the bare prefix of `DOCS_WRITE_*` (`command grep -oE 'DOCS_WRITE_[A-Z_]*[A-Z]' | sort -u | wc -l` gives 31) — and 4 in rendered BR, the prefix, `ARTIFACT`, `BACKLOG_UNREADABLE` and `EVIDENCE`. `diff` of the old set against DW's prints nothing, so DW alone still holds every code, and against the union of DW's and BR's prints nothing too. Lines holding `DOCS_WRITE_` (`command grep -c`): 39 → 38, since two §5 mentions became `<RUN>_EVIDENCE` and three *Sources* lines became two.
- **C23. The stop lines.** Command: ``command grep -oE '`DOCS_WRITE_[A-Z_]+: [^`]*`' <file>`` over old DW and DW now, each into a file, then `cmp`. Expected: CL's "the same 32 lines", equal as an ordered list. Result: 32 and 32, `cmp` silent; the codes they open (`sed -E 's/^.(DOCS_WRITE_[A-Z_]+):.*/\1/' | sort -u | wc -l`) are 31; rendered BR holds none.
- **C24. The line reader without a new flag, against `origin/main`'s script.** Command: `python3 -I battery.py`, the final review's script, with `bl-old.py` from `git show origin/main:<BLP>` and `bl-new.py` from `git show HEAD:<BLP>`, over identical copies of one repository whose `main` has seven units and eight other refs: a branch moving `U-001`, an out-of-shape backlog, a deleted backlog, an absent unit, a status out of class, an orphan, a merged branch and a name outside the branch class. It makes 456 calls: `check`; `moved` over every set of one to three of seven ids, and its error cases; and `edit` over nine ids and six statuses, with and without each of six `--page-path` values, and the usage errors. Expected: CL's "Without the flags every output is what it was, byte for byte". Result: **`calls 456 differences 0`** — exit, stdout, stderr and the backlog's bytes afterwards identical in each. Beside it, the head's `moved --own-moves` drops `docs/a` from `U-002`, a branch cut before `main` moved that unit, which `moved` without the flag lists; and the old script refuses `--own-moves` with exit 2 and its usage line, so the flag reaches no older reader silently.
- **C25. `/docs-write` passes none of the four flags.** Commands: ``command grep -noE 'python3 "\$\{CLAUDE_PLUGIN_ROOT\}/scripts/backlog-lines\.py" [a-z]+' <DW>``; `command grep -cE -- '--own-moves|--from |--walkthrough|--block' <DW>`; and `command grep -rnE -- 'backlog-lines\.py.*(--own-moves|--from |--walkthrough|--block)' plugins/*/commands plugins/*/agents plugins/*/references | wc -l`. Expected: BKR:25's "`/docs-workflows:docs-write` passes none of the four", and CL's "which no command of this release passes". Result: three call lines, DW:52 `check`, :112 `moved` and :334 `edit … --status drafted`; 0; 0. No file under `plugins/docs-workflows/commands` is named `docs-verify.md` (`ls`: eight commands), so CL's "`/docs-verify`, which is not in this release" holds.
- **C26. The loader.** Commands: `python3 scripts/reference-parts.py --root <tree> check-citations --verbose` with `<tree>` `$S/main` and `.`, then `diff`; `python3 scripts/reference-parts.py --root <tree> check-questions` on both. Expected: equal output, D15 asking that no loaded rule of `/docs-write` change; BR carries the preamble and the load-by-part paragraph (BR:3 and :5). Result: 20 lines each, exit 0, `diff` silent: `escalation-rules` placed 324, whole 2; `finding-triage` 74, 2; `next-phase-offer` 115, 3; `session-hygiene` 142, 4; entry-point requests 502, 30 distinct; the three `phase-handoff` entry files 20/273, 28/318 and 25/141; and the 11 `WHOLE` lines. `check-questions` gives `PASS -- 38 command(s)` on both.

## 6. The hunks

- **C27. What changed in the commands and references.** Command: `git diff -U0 origin/main...HEAD -- plugins/docs-workflows/commands plugins/docs-workflows/references`, its `@@` lines counted per file. Expected: DW changed only at the moved blocks' sites, FH only at its §6 wording. Result: **26 hunks over 6 files** — DW 13 (`-14 +14`, `-22 +22`, `-24,40 +24`, `-110,7 +71`, `-144 +99`, `-148 +103`, `-160 +115`, `-162 +117`, `-164,5 +119,2`, `-231,5 +183`, `-263 +211`, `-265 +213`, `-383,13 +331`); FH 8 (lines 151, 173, 175, 177, 182, 187, 197 and 201, each `-n +n`); UB 2 (38, 40); EC 1 (7); VIS 1 (5); BR new, `+1,129`. `git diff --stat` over the same paths: `6 files changed, 155 insertions(+), 90 deletions(-)`. These are the positions the close report's hunk table conditions, one by one, and the final review's D15 parts 5 and 6 list; the condition each hunk acts under, and the R2 reachability argument — a root holding `$`, a backtick, `\` or `"` already stops at DW:52's double-quoted `check`, before any moved program runs — are the close report's reading (`task-1.5-report.md`, *Every hunk*), not re-read hunk by hunk here. The one new act is DW:14's Read of BR, whole, before Phase 0.

## 7. The GIT-G1 audit

- **C28. No GIT-G1 file.** Command: `git diff --name-only origin/main...HEAD | command grep -cE '^(plugins/workflows-core/|\.github/|\.claude/rules/workflows-core-(git|handoff)\.md|scripts/selftests/|scripts/reference-parts)'`. Expected: 0 — the batch makes no GIT-G1 edit; G1 to G4 are batch 2's (SDD `progress.md`, line 5). Result: 0.
- **C29. Nothing under `plugins/workflows-core/`, `.github/` or `scripts/`, and no other plugin.** Commands: `git diff --name-only origin/main...HEAD -- plugins/workflows-core .github scripts | wc -l`, and `git diff --name-only origin/main...HEAD -- plugins | cut -d/ -f2 | sort | uniq -c`. Expected: 0, and `docs-workflows` alone. Result: 0, and `12 docs-workflows`. The four rules files the branch changes are C4's; `workflows-core-read-only.md` changes at one line, `@@ -24 +24 @@`, the sentence naming `/docs-write` among the readers of `read-only-repos` §3, now through BR (the Task 1.2 review's M4); it is not a GIT-G1 file.

## 8. The release

- **C30. The versions.** Command: a script reading each `plugins/<p>/.claude-plugin/plugin.json`, its `.claude-plugin/marketplace.json` entry, and the same two files at `origin/main` (`git show origin/main:<file>`). Expected: `docs-workflows` 1.44.0 in both files, above `origin/main`'s 1.43.3; every other plugin at `origin/main`'s version. Result:

  | Plugin | `plugin.json` | marketplace | `origin/main` |
  |---|---|---|---|
  | `docs-workflows` | **1.44.0** | **1.44.0** | 1.43.3 |
  | `workflows-core` | 1.100.0 | 1.100.0 | 1.100.0 |
  | `dev-workflows` | 4.71.0 | 4.71.0 | 4.71.0 |
  | `product-workflows` | 3.88.0 | 3.88.0 | 3.88.0 |
  | `security-workflows` | 0.13.0 | 0.13.0 | 0.13.0 |
  | `prose-style` | 0.8.4 | 0.8.4 | 0.8.4 |
  | `guideline-reviewers` | 1.2.11 | 1.2.11 | 1.2.11 |
  | `acli` | 0.1.4 | 0.1.4 | 0.1.4 |
- **C31. The catalog's one change.** Command: `git diff origin/main...HEAD -- .claude-plugin/marketplace.json | command grep '^[-+] '`. Expected: the version line alone. Result: `-      "version": "1.43.3",` and `+      "version": "1.44.0",`.
- **C32. The description.** Command: the same script, `len()` of each `description`. Expected: equal in `plugin.json` and the marketplace entry, under the 900-character warning, and unchanged, since the batch adds no capability a user runs. Result: 895 and 895, equal, and equal to `origin/main`'s. Every other plugin's two descriptions are equal too.
- **C33. The changelog.** Commands: `grep -m1 -n '^## \[' plugins/docs-workflows/CHANGELOG.md`; a script removing that first section and comparing the rest with `git show origin/main:plugins/docs-workflows/CHANGELOG.md`; `grep -n '^## .*Unreleased' plugins/*/CHANGELOG.md | wc -l`. Expected: the new section first, dated 2026-11-26, the rest untouched, and no `Unreleased` heading anywhere. Result: `8:## [1.44.0] — 2026-11-26`; equal, byte for byte (115 `## [` headings, `origin/main` 114); 0. The date holds if the merge lands on 2026-11-26 (UTC), as the final review's O3 says of it and of TT:270's "Released 2026-11-26".

## 9. Sizes

- **C34. `CLAUDE.md` and the rules files the branch changes.** Command: `LC_ALL=C.UTF-8 wc -m <file>`, and `git show origin/main:<file> | LC_ALL=C.UTF-8 wc -m`. Expected: under `scripts/validate-catalog.py`'s `CLAUDE_MD_WARN = 36_000` and `RULES_FILE_WARN = 20_000` (its lines 132 and 133). Result:

  | File | Head | `origin/main` | Warns at | Under it by |
  |---|---|---|---|---|
  | `CLAUDE.md` | 35,979 | 35,980 | 36,000 | 21 |
  | `.claude/rules/docs-workflows.md` | 18,774 | 18,775 | 20,000 | 1,226 |
  | `.claude/rules/threat-model.md` | 18,630 | 18,561 | 20,000 | 1,370 |
  | `.claude/rules/docs-workflows-backlog.md` | 10,304 | 9,329 | 20,000 | 9,696 |
  | `.claude/rules/workflows-core-read-only.md` | 5,167 | 5,046 | 20,000 | 14,833 |

  The largest rules file in the tree is 19,991 characters, `gates.md` and `dev-workflows-implement.md` alike, neither touched by the batch. `CLAUDE.md`'s one changed line is `twenty-five reference files` → `twenty-six reference files`.

## 10. The sweep's counts

- **C35. Every literal string batch 1 changed, before and after.** Command: `python3 -I count.py <worktree> $S/main`, which collapses whitespace in each file and in each string and counts over refinement 4's scope — `git ls-tree -r` of `plugins` (every `CHANGELOG.md` included), `README.md`, `CLAUDE.md`, `.claude/rules` and `docs/maintainers` — at `origin/main` and at the head. Expected: each string at the count its task's edit intended. Result: 68 strings; 67 carry an intended count, and **62 of them stand at it**. The other five:
  - two are the harness's own search strings, written with a stray leading backtick: counted again without it (`count2.py`, the same counting), "backlog-run.md` §3's rule" gives 0 → 1 (UB) and "backlog-run.md` §5" 0 → 4 (BKR 2, DW 1, UB 1), each at its intended count;
  - three count higher than the task intended by hits in CL, which came after that task's count, each true: "the gate registry" 0 → 1, CL:14's sentence saying an amendment removed it; "26 reference files" 0 → 2, `docs/README.md:67` and CL:24; "page-path test" 8 → 13, where DW 7, BR 1, UB 1 and VIS 1 make Task 1.4's 10 and CL:14 and :22 (twice) the other 3.

  Among the 62: "a path it names that is neither" 1 → 0 and "outside the reach set" 0 → 1; "five references cite it too" 1 → 0 and "six references cite it too" 0 → 1; FH §6's eight old phrases 1 → 0 and its nine new ones 0 → 1, "commits this run made" 3 → 3 and "docs: draft <unit-id>" 5 → 4; EC:7's old recipe 1 → 0 and the new one 0 → 1; "lists every copy, and no other file" 1 → 0 and "which are no copies" 0 → 1; "the same 32 stop codes" 0 → 0 and "the same 32 lines, over the same 31 stop codes" 0 → 1; `"version": "1.43.3"` 1 → 0.
- **C36. The written counts of the plugin's files.** Commands: `ls plugins/docs-workflows/commands | wc -l`, `ls plugins/docs-workflows/agents | wc -l`, `find plugins/docs-workflows/references -type f | wc -l`, the same with `-name '*.md'`, the same per subtree, and `command grep -noE` for each written copy. Expected: each copy equal to the tree. Result: 8 commands, 11 agents, 26 reference files, 24 of them markdown (the other two `docs-profiles/default-owners.txt` and `docs-profile.default.yml`), `docs-iteration/` 2, and the subtrees 5 + 4 + 4 + 3 + 2 = 18 markdown pages beside 6 top-level ones. The copies: `CLAUDE.md:37` "twenty-six reference files"; `.claude/rules/docs-workflows.md:19` "twenty-four markdown pages"; `plugins/docs-workflows/README.md:26` "twenty-four reference pages" and "twenty-four markdown pages"; `plugins/docs-workflows/docs/README.md:67` "26 reference files"; `docs/reference/references.md:3` "26 files", "6 + 18 = 24" and :50 "`docs-iteration/` (2)". Each agrees.

## 11. The probe

- **C37. The exclusivity probe over the new lines.** Command: `python3 -I probe.py <worktree> $S/main`, refinement 3's set, the plan's phrases and batch 1's own claim words (`does not pass`, `passes none`, `no command of this release`, `not in this release`, `one writer`, `the one line reader`, `only … alone`, and others) over refinement 4's scope, on every line of a changed file whose text the same file at `origin/main` lacks. Expected: each new claim true against the thing that runs it. Result: **50 hits**, 14 of them on `workflows-core-read-only.md:24`, edited for the Task 1.2 review's M4 (C29). Four claims are new:
  - BKR:25, "`/docs-workflows:docs-write` passes none of the four" — C25;
  - CL:15, "four flags, which no command of this release passes" — C25;
  - CL:10, "`/docs-verify`, which is not in this release", and "four flags `/docs-write` does not pass" — C25;
  - BLP:41's "With --own-moves it is moved only where the ref changed that status itself" and :47's "moved names only the ids some ref moved" — C24's sample, and the self-test's `own_moves_*` cases (C10).

  The rest are words that already stood on a line edited for another reason: BR's moved "only where", FH:151's "reads only" and FH:177's "no other placeholder". FH:187's "its one writer" counts 1 at `origin/main` too. The close report's second pass, over unchanged lines naming a batch subject, is not reproduced here: the saved `probe.py` prints the first pass alone, and a second pass written here with its subject pattern gives 523 hits across the family, which no reading here went through. That pass stands as the close report's (69 hits, `task-1.5-report.md`, Step 4) and the final review's own probe (121 hits within 150 characters of a batch subject, `final-review-batch1.md`, *Sweep*), each finding none false.

## 12. The consumer recipes

- **C38. EC:7's recipe.** Command: `grep -rlE 'evidence-contract|docs-iteration/backlog-run\.md' plugins/docs-workflows/commands plugins/docs-workflows/agents`. Expected: the readers EC:7 names, `/docs-audit`, `/docs-write` and `docs-audit-reviewer`. Result: `agents/docs-audit-reviewer.md`, `commands/docs-audit.md`, `commands/docs-write.md`.
- **C39. VIS:5's recipe.** Command: `grep -rl 'visibility\.md' plugins/docs-workflows/commands plugins/docs-workflows/agents plugins/docs-workflows/references`. Expected: VIS:5's "every reader but `/docs-write`" — `/docs-init`, `docs-scaffold-reviewer`, `/document`, `docs-audit-reviewer` — and its "six references": `render-verification.md`, `scaffold-tree.md`, `frontmatter-guidelines.md`, `backlog-format.md`, `unit-brief.md` and BR. Result: those ten files, and not DW.

## 13. The run folder

- **C40. Nothing in batch 1 reads against the run-folder rules.** Commands: `grep -l 'args: "run-folder ' plugins/*/commands/*.md`; `command grep -rlE 'run-folder|run folder' plugins/docs-workflows | wc -l`; `cmp plugins/workflows-core/scripts/tree-snapshot.py plugins/docs-workflows/scripts/tree-snapshot.py`; `command grep -rl 'scripts/tree-snapshot\.py' plugins/docs-workflows/commands plugins/docs-workflows/agents plugins/docs-workflows/references`. Expected: no `docs-workflows` file keeps a run folder; its copy of `tree-snapshot.py` equal to `workflows-core`'s; the copied-scripts step still sees the call that moved into BR. Result: seven commands keep a run folder, `vuln`, `upgrade`, `conformance`, `ready`, `design`, `prd-ground` and `scan`, none of `docs-workflows`; 0; `cmp` silent; `commands/document.md` and BR, which CI's *Every plugin's copied scripts are the same* step greps under `references/` too, and which passes in C5. The ledger's ruling (SDD `progress.md`, line 18) — `/docs-verify` keeps its `mktemp` scratch under `workflows-core:run-flags` §7, and the run-folder design's Part 2b, another track, may cover it — is stated in the pull request's *The run folder*, worded as the final review's M3 asked.

## 14. The live check

- **C41. Batch 1's live check is written and not run.** Commands: `grep -n 'DOC-D-G1 sub-project 2, batch 1' docs/superpowers/to-test-on-real-project.md`, and `awk '/^## DOC-D-G1 sub-project 2, batch 1/{f=1;next} /^## /{f=0} f' docs/superpowers/to-test-on-real-project.md | grep -c '^- \*\*'`. Expected: TT's section, marked not run. Result: TT:268, `## DOC-D-G1 sub-project 2, batch 1 — \`docs-workflows\` 1.44.0`; its intro (TT:270) opens "Released 2026-11-26; not run"; 2 bullets, the one check — the 1.43.0 `--next` check again on 1.44.0, the session's transcript showing a Read of BR, whole, before Phase 0's first step, and the plugin root single-quoted in §10.1's read, §9's tree reads and §10.2's test — and what a miss looks like. **It has not been run.**

## The reviews

Each review's verdict and counts are its file's and the ledger's (SDD `progress.md`, the line named); none was re-derived here. The review files are under `.superpowers/` and SDD, git-ignored.

| Review | File | Model | Reviewed | Verdict and findings | What followed |
|---|---|---|---|---|---|
| Design review 1 | `.superpowers/design-review-1.md` | Fable (`045fda591`'s subject) | the design at `b90e55c26` | With fixes: 1 Critical, 13 Important, 12 Minor | revision 2, `045fda591` |
| Design review 2 | `.superpowers/design-review-2.md` | not named in the file | the design at `045fda591` | With fixes: 0 Critical, 2 Important, 7 Minor | revision 3, `929ff00a4`; the maintainer's answers, `2ca797de5` |
| Plan review 1 | `.superpowers/plan-review-1.md` | Fable (line 2) | the plan at `fe5cc8f8e` | With fixes: 0 Critical, 5 Important, 7 Minor | revision 2, `bde7839f3` |
| Plan review 2 | `.superpowers/plan-review-2.md` | Fable (line 2) | the plan at `bde7839f3` | With fixes: 0 Critical, 2 Important, 5 Minor | revision 3, `b21049881` |
| Task 1.1 | SDD `task-1.1-review.md` | Fable | `b21049881..024fb8c43` | matches the brief; 0 Critical, 0 Important, 3 Minor (line 13) | fix round `cac361af0`; re-check 1 (line 19) found one new Minor, fixed by the controller in `565c73c18` |
| Task 1.2 | SDD `task-1.2-review.md` | Fable | `565c73c18..06fdd6398` | matches the brief, D15 holds; 0 Critical, 2 Important, 5 Minor (line 26) | fix round `2e556971e`; plan amendment `6018f8b73`; re-check 1 (line 30) left one residual, N1, fixed by the controller in `fe3343643` |
| Task 1.3 | SDD `task-1.3-review.md` | Fable | `fe3343643..70d473a52` | PASS; 0 Critical, 1 Important (a carry, moved to Task 2.5), 1 Minor, 1 style (line 36) | M1 fixed by the controller in `2a8f8b184`; the style finding stays, named |
| Task 1.4 | SDD `task-1.4-review.md` | Opus | `2a8f8b184..8d73247c6` | 2 Critical (two false changelog lines), 3 Minor, 1 style (line 43) | fix round `71106bfa5`; re-check 1 (line 46) found one new item, N1, fixed by the controller in `1ba24663d` |
| Task 1.5, the close | SDD `task-1.5-report.md` (no review file of its own) | Opus | — | DONE, no commit; reported the plan's stale Task 1.2 file list (line 50) | fixed by the controller in `3b08f614a`; the close reviewed inside the final review |
| Final whole-branch review | SDD `final-review-batch1.md` | Fable | `f3702976a..3b08f614a` | With fixes: 0 Critical, 0 Important, 3 Minor (M1–M3, all in SDD `pr-body-batch1.md`), 1 style (S1, `backlog-lines.py:80`'s 131-column docstring line, may stay), 4 observations (line 53) | M1–M3 fixed in the pull request's text (line 54); no commit to the tree |

**The three Minor fixes are in the pull request's text.** In SDD `pr-body-batch1.md`: `command grep -c 'Three of the new cases'` gives 0, and its line 72 reads "Three cases pin text, two of them new" (M1). Lines 12 and 155 name both plan amendments, `6018f8b73` and `3b08f614a` (M2). Lines 179 to 185 say Part 2b's plan is not yet written, and that whichever lands second owes the adoption (M3). Each review's D15 measurement was its own; this record's C15 to C26 are this record's.

## After this record was written

C5's chain — the same 34 steps, `--baseline` alone as step 5, then `claude plugin validate .` — was run once more on this tree with this record written in full, staged and uncommitted, as the last act before its commit, so that every gate reading the repository's markdown read this file too. Its result is not written here, since writing it would change the file that run read; it is reported with the commit. Nothing in this file was edited after that run.

## What was not verified

- **The live check (C41)** has not been run on a real project. The transcript evidence it names — the Read of BR before Phase 0, and the plugin root arriving single-quoted in the three places — is shown by no measurement here: C20 and C21 run the programs by hand, never through an orchestrator reading BR.
- **The mermaid gate** ran nowhere on this machine (C7). CI runs it on the pull request.
- **The hunk conditions and the R2 reachability argument** (C27) are the close report's reading, re-checked here only for the hunks' positions.
- **The probe's second pass** (C37) is the close report's and the final review's, not re-run.
- **The reviews' counts** are their files' and the ledger's, as is each review's own D15 measurement; this record re-derived D15 with the close task's and the final review's harnesses on fresh inputs, not by a method of its own. The review's eight pin mutants and the fixers' mutation runs were not re-run.
- **The pull request's text** was checked here only for M1 to M3. This record was not reviewed before it was committed.

# RUN-FOLDER-PART1 — a stopped `/prd-ground` resumes — verification record

**Branch:** `iv-gu/run-folder`, head `0da5d56a9` (the final tree after every task review and the final whole-branch review's fix wave), cut from the merge base `c4d31daeb` of `origin/main`. **Release:** `workflows-core` 1.99.0 and `product-workflows` 3.87.0, both dated 2026-11-24. **Design:** `docs/superpowers/specs/2026-11-24-run-folder-design.md`; **plan:** `docs/superpowers/plans/2026-11-24-run-folder-part1.md`. Every figure below was obtained on that tree, on 2026-11-24, by the command beside it; none is copied from another record. `git status --short` printed nothing before the gates ran. This record covers Part 1 only: `/prd-ground` is the one command that keeps a run folder.

`git diff --stat c4d31daeb HEAD | tail -1` prints `30 files changed, 4537 insertions(+), 74 deletions(-)`, before the commit that carries this record.

## The six Review Focus lines

Each line names the self-test case in `plugins/workflows-core/scripts/run-folder.py --selftest` that pins the mechanism, and the text that makes the command use it. Commands and references are cited by heading and a short quoted snippet.

1. **Two projects of one container group with the same KEY get two run folders.**
   - Case `identity-specs-origin`: the specs repository's `origin` URL is part of the identity, so two specs repositories holding one key give two folders. Companions: `identity-specs-path` (the physical path, for a repository with no `origin`), `identity-workdir-optional`, `run-key-shape`.
   - Text: `plugins/workflows-core/references/run-folder.md`, *1. The script, the folder and its key*, "so two specs repositories holding one key never share a folder" (quoted from the 1.99.0 changelog's description of the same section); `prd-ground.md`, *Phase 0 — Resolve inputs and gate on main*, the step that opens the folder, keyed on "the command, the key and the specs repository and not on the directory it is started in".
2. **A session killed after an agent wrote its result file but before `done` recorded it re-dispatches that agent.**
   - Case `result-unrecorded-not-reused`: a result file with no completion record is not reused. Companions: `reuse-after-done` (a recorded one is), `done-missing-result`, `result-nonce-old-agent` (an agent of an earlier dispatch writes a file nothing reads).
   - Text: `run-folder.md`, *Entry point: `run-dispatch`*, "A result file with no completion record is not a result"; step 4, "only a return the command goes on with ... which stays unrecorded so that a resume dispatches it again".
3. **An older session still running after another resumed stops at its next write and writes nothing to the specs repository.**
   - Cases `owner-guard`, `owner-guard-writes`, `write-after-discard-exits-9`: a writing call from a session other than the owner exits 9 with nothing written. Companions: `owner-null-passes`, `discard-waits-for-writer`, `concurrent-writes`.
   - Text: `prd-ground.md`, the stop `PRD_GROUND_RUN_TAKEN_OVER: another session (<id>) took this run over — stopping without writing.`; *Ending early* in Phase 0 and `run-folder.md` §2 (exit 9 "so the command stops at once and writes nothing more", no cost entry, no terminal commit, no Final report). Phase 8 owner-checks each write: "`log <folder> 'p8-write <the file>'`, so that a session another ...".
4. **A repository pulled between two sessions redoes only that repository's grounding and verification.**
   - Cases `fingerprint-changes-with-input` (the input names the repository's commit, so the fingerprint moves and only that dispatch is redone), `fingerprint-attach`, `fingerprint-agent-and-model`.
   - Text: `prd-ground.md`, Phase 3, *This run's own pins*: "the repository moved since this run pinned it, Phase 5 and Phase 7 dispatch it at the new commit, so its grounding and verification are redone, ... every other repository's saved results are" reused. A pin on file in `grounding/baselines.md` decides first.
   - Stated limit, not hidden: every design pass is redone as well, because its input carries every repository's findings (the changelog's known limits).
5. **A derive verifier cannot find the grounders' answers in the run folder.**
   - Case `area-blind-separate`: a `blind`-area dispatch's input and result lie under `blind/`, apart from `main/`.
   - Text: `prd-ground.md`, Phase 5, *Saved dispatches*, "The area: `blind` for a `mode: derive` dispatch, so that its result lies apart from every" grounder's; `agents/grounding-verifier.md`, "In derive mode, read nothing under the run folder that holds `result_path` except the file at `result_path` itself."
6. **A run stopped inside Phase 8's writes does not append its findings twice.**
   - Case `effect-states` (`none`, `started`, `done`, and the transitions between them). Companion: `done-from-stdin`.
   - Text: `prd-ground.md`, Phase 8, *Guarded*: the effect `p8-write`, each file copied into `scratch/p8-before` before the first write, `effect <folder> p8-write start`, and `effect <folder> p8-write done` after *The record*. Phase 0, *A run Phase 8 began*: `done` means "Phases 1 to 8 do not run" and the run goes on at Phase 9 or 10; `started` asks "Restore the files to how they were before and write again (Recommended)" or *Stop* (`PRD_GROUND_WRITE_INTERRUPTED`).

The self-test also covers the lock and file-handling cases the review rounds added: `open-exclusive`, `concurrent-writes`, `discard-waits-for-writer`, `close-unlocks-before-removing`, `unparseable-run-json-noted`, `resume-args`, `args-flag-shaped`, `bad-command-or-key`, `bad-id`, `prune-30-days`.

## The gates on this tree

| Gate | Result |
|---|---|
| `python3 plugins/workflows-core/scripts/run-folder.py --selftest` | 43 lines, each `PASS`; no other line (`grep -c '^PASS'` prints 43, `grep -v '^PASS'` prints nothing) |
| `cmp plugins/workflows-core/scripts/run-folder.py plugins/product-workflows/scripts/run-folder.py` | no output, exit 0: the two copies are identical |
| `./scripts/check-docs.sh --root .` | `PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows plugins/security-workflows plugins/prose-style`, exit 0 (run before this record was written and again after it: exit 0 both times) |
| `./scripts/check-id-grammar.sh --root .` | `PASS: no dash-form requirement IDs under .` |
| `python3 scripts/validate-catalog.py` | `0 error(s), 0 warning(s) across 1 repo(s).` |
| `python3 scripts/reference-parts.py check-parts` | `PASS -- 4 split reference(s), 3 entry file(s), 36 generated file(s) fresh` |
| `python3 scripts/reference-parts.py check-citations` | `PASS -- 4 split reference(s)` |
| `python3 scripts/reference-parts.py check-questions` | `PASS -- 38 command(s) load the question rules before their first question` |
| `python3 scripts/reference-parts.py check-branch-check` | `PASS -- 24 command(s) run branch-check` |

**Not run here: `node scripts/mermaid/check-mermaid.mjs --root .`.** It needs its parser installed with `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund`, and `scripts/mermaid/node_modules` does not exist on this machine; it was not installed. This branch adds no mermaid block: `git diff c4d31daeb HEAD | grep -c '^+.*```mermaid'` prints 0. CI runs the check on the pull request.

The other self-tests in `.github/workflows/validate-catalog.yml` (`check-docs.sh --selftest`, the other plugins' scripts, `mutants.py --check`) were not run: the branch changes none of those scripts, and the brief asked for the gates above. CI runs them.

## Owed — only a live run can show

None of the following has been run; each is owed, and nothing above claims it.

1. **A real `/product-workflows:prd-ground <KEY>` interrupted mid-Phase 7 and resumed in a new session.** Passing: the new session asks *Resume* or *Start over*, names the earlier run's phase and results; on *Resume* it does not re-ground, the Final report's `Resumed:` line shows saved results reused greater than zero and fewer dispatches made than a fresh run makes, Phase 8 writes each finding once, and the folder is gone after the terminal commit.
2. **The same in a restarted container** (the state directory kept, as the 1.99.0 changelog requires). Passing: the same as 1, with `$XDG_STATE_HOME` or `~/.local/state` on a directory the container keeps; and, in a container that does not keep it, a fresh run after the one-line note, not an error.
3. **A resume after pulling one repository.** Passing: the question names that repository as moved and how many saved results that leaves unused; the Final report names it; only its grounders and verifiers, and the design passes, are dispatched again, every other repository's results counted as reused.
4. **A resume after a plugin update that changes `agents/grounding-verifier.md`.** Passing: `changed-agents` counts the saved verifier results; at 10 or fewer they are redone without asking, above 10 it asks; a verifier result written below Opus is redone whatever the answer; the Final report names any kept.
5. **Two sessions on one run.** Passing: the older session stops at its next write with `PRD_GROUND_RUN_TAKEN_OVER`, writes nothing to the specs repository, and prints no cost entry, commit or Final report; the newer session finishes normally.

## Known limits shipping with the release

From `plugins/product-workflows/CHANGELOG.md` 3.87.0:

- Only `/prd-ground` keeps a run folder in this release; the other commands follow in the design's second part.
- A shared reference an agent reads is not part of a result's fingerprint: a change to `grounding-format` between two sessions leaves `grounding-verifier`'s saved results reused.
- A moved repository redoes every design pass, so a pull between two sessions redoes the design work too.
- A name whose id form another name shares only in one session (two repositories or frame sets differing only in case or in characters other than `a`-`z` and `0`-`9`) takes a suffix in that session and none in the next, which redoes that name's saved results.

From `plugins/workflows-core/CHANGELOG.md` 1.99.0 (stated in its description, not a separate list): the folder lies under `$XDG_STATE_HOME` or `~/.local/state`, so in a container that directory must be kept across restarts or the run cannot be resumed; a run that cannot make or write its folder goes on without it after a one-line note and cannot then be resumed; `/dev-workflows:implement` keeps its own resume, untouched.

Left open at the final review, and fixed the same day in `workflows-core` 1.99.1 and `product-workflows` 3.87.1 (self-test cases `lock-failure-exits-2`, `lock-failure-keeps-folder` and `lock-retry-bounded`, each seen failing before the fix):

- `write_lock` in `plugins/workflows-core/scripts/run-folder.py` ran a write **unlocked** when `fcntl.flock` itself failed, for example an NFS home without a lock manager. It now ends the call with exit 2 before anything is written, which the run meets as the folder becoming unusable.
- `write_lock`'s inode-recheck retry loop had no bound. It now stops after `LOCK_ATTEMPTS` (5) attempts with exit 2.

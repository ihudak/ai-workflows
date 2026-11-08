# Live-check round 3 fixes (LC29–LC37, and the round's other known bugs) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every defect the 2026-11-04 live-check round found: the nine filed in to-fix as LC29–LC37, R1's plan-conflict question, and the five more (K1–K5) its run feedback shows in the shipped text. The next live round can then verify them.

**Architecture:** A fix batch over five plugins:
1. Two new shared pieces in `workflows-core`, a script and a reference, then their callers.
2. One task per remaining area.
3. One closing task for the release bookkeeping.

Almost every change is command, agent or reference prose. Two Python scripts change, one new and one fixed, each with a selftest.

**Tech Stack:**
- Markdown command, agent and reference files, which agents execute.
- Python 3 (standard library only) scripts with `--selftest`: the new `tree-snapshot.py`, and `run-state.py`.
- The repository's gate chain.

**Spec:**
- `docs/superpowers/to-fix.md` § *From the live checks of 2026-11-04* (LC29–LC37).
- Evidence: `docs/superpowers/verification/2026-11-04-live-checks.md`.
- The plan review of 2026-11-08 (READY WITH CHANGES; 11 MAJOR, 12 MINOR, 8 NIT) is folded in below.
- The user's rulings of 2026-11-08:
  - **LC31.** The two preflight prints (the session-branch creation line and G1's notice at detection) are folded into GIT-G1's design as required outputs. This batch fixes only LC31's third case, `/specify`'s Final report.
  - **LC36.** After the review cap is spent, `/design`, `/specify` and `/update-spec` dispatch `overlap-reader` over the edits made after the last review. `/epics` keeps reporting them.
  - **R1's plan-conflict question.** `/implement` recommends *Revise the plan* where the finding contradicts neither `design.md` nor the specification.
  - **LC34.** One script in `workflows-core`, copied into `dev-workflows`, `product-workflows` and `docs-workflows`, with a CI check that the copies are equal (the `bounded.py` pattern).
  - **"All known bugs must be fixed."**

**The round's other known bugs.** Each row is taken from the round's run feedback (ids in the e2e specs copy) and was checked against the shipped text at `8e110fc1`. Each one this batch takes is a place where the text gives no answer, or a contradictory one.

| Id | Where | Source | Disposition |
|---|---|---|---|
| K1 | `run-state.py append` takes an array value silently, as one entry | `BOOK-1-01-implement-run-state-append-nests-list` (R1) | **Taken** (Task 9): `append` refuses an array value |
| K2 | `/epics` names no ranking for its per-Epic cap of three decision markers | `BOOK-6-epics-marker-cap-ranking` (R2) | **Taken** (Task 10) |
| K3 | `/epics` Phase 6.2 has no rule for a style result with nothing at `MAJOR` | `BOOK-6-epics-style-fixer-empty-set` (R2) | **Taken** (Task 10) |
| K4 | "the folder read" is routed to a Sonnet scanning step that no command dispatches. It is residue of the retired reader agent (`68c26cf80`), and in S5a it made `/ready` dispatch one | `BOOK-4-01-ready-folder-read-dispatch-unstated` (S5a) | **Taken, family-wide** (Task 9) |
| K5 | `/ready` never states what `readiness-reviewer` may read beyond its brief | `BOOK-4-01-ready-reviewer-read-scope-unstated` (S5a) | **Taken** (Task 9) |
| K6 | `/ready` Phase 3(a) finds no PRD ID below the Epic | `BOOK-4-01-ready-coverage-grep-id-namespace` (S5a) | **Not taken.** `ready.md:362–365` records the miss and names the limitation, and the reviewer's full read covered it, as designed. Below the Epic the grep is empty by format. |
| K7 | `/implement`'s check-run read is improvised | `BOOK-1-01-implement-check-run-tree-helper` (R1) | **Taken under LC34** (Task 2): the same class, the same script |
| K8 | `/frames` read its folder before the preflight | `BOOK-7-frames-preflight-read-boundary` (S6a) | **Not taken.** `frames.md:136–137` already orders the preflight before the carrier and kind tests. The run slipped against it, and the feedback files itself as `unfollowed-rule`. |
| K9 | The apply offer recommended *Apply them* while the run's prose advised leaving one finding out | `BOOK-9-specify-apply-offer-no-subset` (S2) | **Not taken.** No reviewer emits an "optional" marker, and the rule already takes a free-text subset (`escalation-rules.md:547`). The run's prose departed from the fixed array. |

**Also considered and not taken:**
- **Wishes, not defects:**
  - thin grounding not surfaced at Phase 6.1;
  - scanner output copied into `scanner_file` by hand;
  - the Stage 4 Rule read re-run after its own settlements (the play-back must carry a read of the draft it plays back);
  - the Epic size count not shown at the offer (Phase 7's final count caught it);
  - the cross-PRD route overlap, which the test bed's copy PRDs created;
  - docs grounding on an unrelated root, which comes from the environment;
  - `BOOK-1-01-implement-unrun-suites-premerge-item`.
- **Model slips against an existing rule:**
  - an unverified session fact;
  - a post-review edit's false code claim;
  - `code-scanner` line numbers, which the premise rule caught;
  - writer suggestions;
  - the guard criterion that pre-empted a decision;
  - S2's report opening sentence, which contradicted its own Next step (LC23's rule holds).
- **Harness and environment:** "placeholder" handbacks; a stale upstream inherited through the read-only `.git/config`.
- **Taken elsewhere:** `BOOK-4-01-ready-phase-handoff-reference-oversize` goes to GIT-G1, with PR10.
- **Covered by LC33:** `/specify`'s dirty-tree question offers no by-ref read. Once the refresh question recommends reading the session's own repository by ref, that repository no longer reaches the dirty-tree stop; another dirty clone keeps today's list.
- **Not a defect:** `/specify` asks its refresh question in Phase 1, before Step A's picker. Its configuration phase asks all its questions before the reads.

**The branch.** `fix/live-checks-r3` at `8e110fc1` (main, with PR #175 merged). Line numbers below are at `f8a357f6`, and every plugin file there equals `8e110fc1`. Re-locate each by its quoted text.

## Global Constraints

**Process**
- Follow `docs/superpowers/reviews/2026-10-26-fix-batches.md` § *How to run a batch*, steps 2–8.
- Read the area's `.claude/rules/` file with the Read tool before editing there (`CLAUDE.md`'s table).
- Work in `/workspace/.worktrees/lc-r3-fix` on `fix/live-checks-r3`. Run `git branch --show-current` immediately before every commit. Never `git checkout` in `/workspace/ai-workflows`. Never bare `git stash`.
- Commit as `git -c user.name="Ivan Gudak" -c user.email=ihudak@gmail.com commit …`, with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Editing discipline (`CLAUDE.md` § Editing discipline binds every edit)**
- Run the claim-expiry sweep with all eight refinements of `.claude/rules/claim-sweep.md`, including refinement 7's before-and-after count of each changed literal string, over `plugins/` (every `CHANGELOG.md` included), the repo-root `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`.
- Apply the sentence-context checks, extent face and pointer face.
- `workflows-core:instruction-file-maintenance` binds edits to `references/*.md`, `.claude/rules/*.md` and `CLAUDE.md`. Re-derive every number you write there, with the command beside it.
- **Rules-file budget.** `scripts/validate-catalog.py` warns on a rules file above 20,000 characters (`len(open(f, encoding='utf-8').read())`). At `8e110fc1`, `.claude/rules/workflows-core.md`, `dev-workflows.md` and `gates.md` each have under 5 characters of headroom. An edit there that adds characters removes as many elsewhere in the same file, without changing any rule's meaning: tighten a sentence, or move evidence behind its existing `why` link. Never exceed the warning.

**Generated files**
- Never edit `plugins/workflows-core/reference-parts/` by hand. After editing `escalation-rules`, `finding-triage`, `next-phase-offer`, `session-hygiene` or `phase-handoff`, run `python3 scripts/reference-parts.py generate`.

**Questions**
- Every `choices:` array has 2–4 options and no "Other". `(Recommended)` marks only a recommended option; where none is recommended, the question's own text says why (`escalation-rules` *When no option is safe to recommend*).
- Each question's own text carries what the person needs to answer it, never "above".

**Snapshots**
- Every `git status` read this plan adds or moves uses `--porcelain -z --untracked-files=all`, and `--no-optional-locks` on a repository the run does not own.

**Content rules**
- Every behaviour change updates its docs page under `plugins/<plugin>/docs/`, each claim derived from the command, agent or reference text.
- No tracker vendor names without a marker (check 13).
- Never name the organisation the plugins were extracted from, nor any corporate email domain or Java package path from the e2e copies.
- Never hard-wrap prose in new text.

**Tracking records**
- House step 8: in the same commit as each fix, delete from `docs/superpowers/to-fix.md` the items it fixes. K1–K5 have no to-fix entry; the commit message names each feedback id it answers.
- Each task adds a to-test item for each fix it makes, under a new section `## Live-check fixes LC29–LC37, R1 and K1–K5 — <versions Task 11 sets>` in `docs/superpowers/to-test-on-real-project.md`, placed after the LC12–LC28 section. Task 11 fills in the versions.

**Gates**
- At each task's end, run `./scripts/check-docs.sh --root .`, `./scripts/check-id-grammar.sh --root .`, `python3 scripts/validate-catalog.py` and every `reference-parts.py` check. Run the selftest of any script the task changed.
- Task 11 runs the full chain: `.github/workflows/validate-catalog.yml`'s `run:` steps as one `&&` chain, reading the printed `EXIT=`.

## Review Focus

1. **A path git quotes or splits.** A path with a space, a `"`, a non-ASCII character, a newline or a non-UTF-8 byte, or a rename record, must survive `tree-snapshot.py`'s read and comparison unchanged. A reasonable person expects the agent-edit check to name that exact path. Task 1's selftest pins each case.
2. **A file an agent or a check run created, beside a clean one.** "No record before" is not "committed and clean". A created file must never be handed off as an agent's edit, and on `/implement` a created file keeps its *Delete* option. Task 1's `in_head` and `created` fields, and their selftest cases, pin it.
3. **The session's repository on a detached HEAD, or with `origin/HEAD` unset.**
   - On a detached HEAD with a known default, `scan-refresh` takes the known-default form, its `<branch>` naming the detached commit.
   - With `origin/HEAD` unset, it takes the unknown-default form.

   Task 3's to-test items name both cases.
4. **A copied script drifting.** The four copies of `tree-snapshot.py` must stay byte-equal, and a plugin whose files call it must ship one. Task 1's CI step fails either case. Task 11 runs it.
5. **A post-cap overlap read that finds nothing.** The run then goes on with no question, and its version line names the read and its count of zero. Task 6's to-test item covers it.

---

### Task 1: `tree-snapshot.py` — the shared before-and-after read (LC34, K7, part 1)

**Files:**
- Create: `plugins/workflows-core/scripts/tree-snapshot.py`
- Create, byte-equal copies: `plugins/dev-workflows/scripts/tree-snapshot.py`, `plugins/product-workflows/scripts/tree-snapshot.py`, `plugins/docs-workflows/scripts/tree-snapshot.py`
- Modify: `.github/workflows/validate-catalog.yml`. Add a selftest step after *Self-test the bounded run*. Generalise *Every plugin's bounded run is the same script* (`:264–279`) into a loop over `bounded.py tree-snapshot.py`, its `name:` and comment saying so, with both error messages kept per name.
- Modify: `.claude/rules/workflows-core-bounded-run.md`. It states the bounded copy rule at `:12–14`. Widen it to "the copied scripts", naming `tree-snapshot.py` and what it does in one sentence, and add `plugins/*/scripts/tree-snapshot.py` to its `paths:`.
- Modify: `CLAUDE.md`'s rules-table row for `workflows-core-bounded-run.md`, so its paths and its *Holds* column say the same as that file.

**Interfaces:**
- Produces:
  - **`snapshot`.** `tree-snapshot.py snapshot --dir <dir> [--path <path relative to dir>]`. With no `--path`, the read is limited to `<dir>` itself (pathspec `:(literal).`). It prints one JSON object:
    ```
    {"dir": <abs dir>, "top": <toplevel>, "prefix": <show-prefix>,
     "records": [{"xy": "<two chars>", "paths": ["<p>", ...]}],
     "fingerprints": {"<p>": "<sha>|-"}, "in_head": {"<p>": true|false}}
    ```
    Every path is relative to `<dir>`, with the prefix stripped. A rename record whose other path lies outside `<dir>` keeps that path, written relative to `<dir>` with `../`.
  - **`compare`.** `tree-snapshot.py compare <before.json> <after.json>` prints `{"paths": [{"path", "before_xy", "after_xy", "before_fp", "after_fp", "in_head", "changed", "clean_before", "created"}]}`, one entry per path in either snapshot, sorted by path.
    - `before_xy` is `null` where the path had no record before.
    - `clean_before` = `before_xy == null and in_head`.
    - `created` = `before_xy == null and not in_head and after_xy != null`.
    - `changed` = `before_xy != after_xy or before_fp != after_fp`.
  - **Exit codes:** `0` done; `2` cannot run (not a git work tree, bad arguments, an unreadable snapshot file).
  - **Encoding.** Path bytes are decoded with `surrogateescape`, and `json.dumps` carries the surrogates as escapes, so `compare` reads a non-UTF-8 path back to the same key.

- [ ] **Step 1: Write the failing selftest** `tree-snapshot.py --selftest`. It builds temporary repositories and asserts each of the following:
  - **Records and fingerprints.** A modified tracked file, an untracked file inside an untracked directory, and a deleted file each give their own record. Their fingerprints are the `git hash-object --no-filters` sha, the same sha form, and `-`.
  - **Paths survive byte for byte.** A path with a space, one with `"`, one with `é`, one with a newline, and one with the byte `\xff` each come back byte-equal through `snapshot` and `compare`.
  - **Renames.** A staged rename (`git mv`) yields one record with both paths, both fingerprinted.
  - **Symlinks.** A symlink is fingerprinted as `readlink -n` piped to `hash-object --stdin`, not as its target.
  - **A subdirectory `--dir`.** Every path has the subdirectory prefix stripped, and with no `--path` a change outside `--dir` is not listed.
  - **A vanished path.** A path removed between the `status` read and its fingerprint is fingerprinted `-`.
  - **`compare` classifies:**
    - an edit to a clean tracked file: `changed: true, clean_before: true, created: false`;
    - a further edit to an already dirty file: `changed: true, clean_before: false`;
    - an untouched dirty file: `changed: false`;
    - a file created untracked: `created: true, clean_before: false`;
    - a git-ignored file created, which has no record on either side: absent from `paths`. The callers test it, as Task 2 says.
- [ ] **Step 2:** Run `python3 plugins/workflows-core/scripts/tree-snapshot.py --selftest`. Expected: it fails, because the file does not exist yet.
- [ ] **Step 3: Implement the script.**
  - **Git calls.** Every call is `git --no-optional-locks -C <dir> …` with `:(literal)` pathspecs.
  - **The read.** `status --porcelain -z --untracked-files=all -- <pathspec>`, parsed as NUL records. An `R` or `C` in either column carries a second NUL-terminated path.
  - **The prefix.** `rev-parse --show-prefix`, stripped from each path.
  - **Fingerprints.** The recipe `plugins/dev-workflows/references/code-handoff.md` §2.2 defines (`:65`), which `epics.md:922` repeats: `hash-object --no-filters -- <path>` with `-C <dir>`; for a symlink, `readlink` piped to `hash-object --stdin`; `-` for anything else.
  - **`in_head`.** `cat-file -e HEAD:./<path>`, run with `-C <dir>`.
  - **Constraints.** No `shell=True`; standard library only.
- [ ] **Step 4:** Run the selftest. Expected: `PASS`. Copy the file into the other three plugins with `cp`, then run `cmp` on each pair.
- [ ] **Step 5: CI and the rules.**
  - Add `- name: Self-test the tree snapshot`, running the selftest. Its comment says what silently fails without it: an agent's edit goes unreported, or the operator's own edit is handed off as the agent's.
  - Make the copy-check and rules-file edits above, re-deriving any count.
- [ ] **Step 6:** Run the gates, then commit: `feat(workflows-core): tree-snapshot.py, the before-and-after read of a tree, copied into three plugins (LC34, K7)`.

### Task 2: every multi-path porcelain-and-fingerprint read goes through `tree-snapshot.py` (LC34, K7, part 2)

**Files** (enumerate the sites with `grep -rn -- '--no-filters' plugins/*/commands plugins/*/references` before editing; the list below is the expected set):
- `plugins/product-workflows/commands/epics.md`: Phase 7.4 step c, `:915–925`, and its comparison paragraph after the agents return, `:927`.
- `plugins/dev-workflows/commands/ready.md`: Phase 5 step 2a, `:491–503`.
- `plugins/dev-workflows/commands/conformance.md`: Phase 5.5, `:421–429`.
- `plugins/docs-workflows/commands/document.md`:
  - Mode A's Phase 8 step c, `:1186–1189`, and its comparison;
  - Mode B's step c, `:1785`, and its comparison paragraph, `:1841`.
- `plugins/dev-workflows/commands/implement.md`:
  - Phase 1.4 step 1's `pre_existing_dirty` capture, and its Pre-Phase 3.5 re-read, `:756`;
  - the *A check run's files* rule, `:760–775`.
- `plugins/dev-workflows/commands/vuln.md` Step 1.5 and `plugins/dev-workflows/commands/upgrade.md` Phase 0.5, where each takes the same many-path read.
- `plugins/dev-workflows/references/code-handoff.md` §2.2, `:63–73`. It stays the **definition** of the fingerprint. It gains one sentence saying that a read of many paths is taken with `tree-snapshot.py`, which implements this recipe byte for byte. Carve-out 1's single-path fingerprint at commit time (`:65`) stays a one-path command.
- `plugins/dev-workflows/scripts/run-state.py`: the `files` members below, in `KEYS`, `KEYS_LINE` and the selftest's key list.
- Each command's docs page, where it describes the read.

**Interfaces:**
- Consumes: Task 1's `snapshot` and `compare`, called as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tree-snapshot.py" …`. The variable expands in command bodies (`CLAUDE.md` § Internal reference convention).
- Produces: `run-state.py` `files` members `snapshot_before` and `snapshot_after`, typed as file paths like the other `files` members. Their files are named from the template `dw-impl-snapshot-XXXXXX`, so `remove` deletes them.

- [ ] **Step 1:** At each site, replace the prose that spells out the porcelain parsing, the prefix stripping and the per-path fingerprint commands with:
  - one `snapshot` call per read the site already takes, its output in a `command mktemp -t <template>` file under the session's scratchpad (`workflows-core:run-flags` §7). The templates are `dw-impl-snapshot-XXXXXX` for `/implement`, `/vuln` and `/upgrade`; `dw-epics-snapshot-XXXXXX` for `/epics`, listed in its `temp_files` (`epics.md:894`); and each other command's existing temp-file convention, removed where it removes its own;
  - after the agents return, or after the check run, the same calls again, then `compare`.

  `/implement` records both paths in run state (`files.snapshot_before` / `files.snapshot_after`), so a compaction during a long check run cannot lose them.
- [ ] **Step 2:** Keep each site's own rules, which the script does not decide: which reads it takes, which set each agent may edit, how each changed path is reported, and each *why* sentence (the live-run evidence), unless the script now makes one untrue. Re-word the site over `compare`'s fields:
  - *stood committed and clean before* is `clean_before`;
  - *a file the agent created* is `created`;
  - *changed while the agents ran* is `changed`.

  On `/implement`:
  - **absent** is `created`;
  - **clean tracked** is `clean_before`;
  - **dirty before** is `before_xy != null`.

  Each site's check of the paths an agent **returned** still tests `HEAD` itself (`git cat-file -e "HEAD:./<path>"`) for a returned path the snapshots do not list, since an ignored file an agent created has no record on either side.
- [ ] **Step 3:** Sweep the moved literal strings across `plugins/`, counting each before and after (refinement 7): `hash-object --no-filters`, `readlink -n`, `IFS=`, `show-prefix`, `--untracked-files=all`. Every remaining copy must be one the script does not replace (a single-path read, `code-handoff` §2.2's definition, `phase-handoff` §2.3's staging read), and the commit message says why each stays.
- [ ] **Step 4:** In to-fix, delete LC34. Add to-test items:
  - On `/ready`, `/epics`, `/conformance` and `/document` (Mode A, and Mode B from the code copy), an agent edit to a path with a space is named exactly.
  - An agent that creates a page is reported, not handed off.
  - On `/implement`, a check run's created file is asked with *Delete*, and a rewritten tracked file without it, as LC16's run saw.

  The items name R1, R2 and S5 of the 2026-11-04 record as the setups.
- [ ] **Step 5:** Run `run-state.py --selftest` and the gates, then commit: `fix: every many-path before-and-after read goes through tree-snapshot.py (LC34, K7)`.

### Task 3: `workflows-core:scan-refresh` — one refresh rule for every scanning command (LC33)

**Files:**
- Create: `plugins/workflows-core/references/scan-refresh.md`.
- Modify `plugins/product-workflows/commands/epics.md`:
  - the refresh bullet, `:333–349`;
  - the brief's refresh lines, `:636–638`;
  - the failed by-ref read, `:655`, and its report line, `:1068`;
  - Phase 4 step 4's late join, `:610`, and the `REPO_MISSING` re-dispatch, `:643`, both of which cite the reference's late-join entry point.
- Modify `plugins/product-workflows/commands/specify.md`: Phase 1 step 3, `:425–433`; the brief, `:875–879`; the `prep` handling, `:901`, and its report line.
- Modify `plugins/dev-workflows/commands/design.md`:
  - Phase 1 step 3, `:151–152`;
  - the brief, `:283–286`;
  - the `prep` handling, `:301`;
  - the scanned-commit record, `:303`: no `with uncommitted changes` mark after a read by ref, citing `read-only-repos` §7 (`read-only-repos.md:117`);
  - the report line.
- Modify `plugins/product-workflows/commands/create-ard.md`: `:369`; the brief, `:595`; the `prep` handling, `:605`; the report line.
- Modify `plugins/product-workflows/commands/update-spec.md`: `:68`, which asks `/specify`'s question. Name the reference there.
- Modify `plugins/docs-workflows/commands/docs-audit.md`: `:117`.
- Modify the count sentences:
  - `plugins/workflows-core/docs/reference/references.md`: a row for the new file (check 4), and the count at `:3` (check 9);
  - `plugins/workflows-core/README.md:9`;
  - `plugins/workflows-core/docs/README.md:41`;
  - `.claude/rules/workflows-core.md` *Plugin facts*, within the rules-file budget.

  Re-derive the count with `find plugins/workflows-core/references -type f | wc -l`.
- Modify: `.claude/rules/docs-workflows.md:79`, the "never fail silently" line for a failed by-ref read, widened to every caller; and `:40`, `/docs-audit`'s map line, if the wording changes.
- Modify: the docs pages of `/specify`, `/design`, `/create-ard`, `/epics`, `/update-spec` and `/docs-audit` where they describe the refresh question or the stale-ref report.

**Interfaces:**
- Produces: `scan-refresh` with two entry points. The loader recognises each as the first word of a code span in a heading (`plugins/workflows-core/skills/reference/SKILL.md:9–11`):
  - `### Entry point: \`refresh-question\``, loaded as `Skill(skill: "workflows-core:reference", args: "scan-refresh refresh-question")`. The caller supplies `session_repo` (its top level and slug, or `none`) and `asks` (`true`, or `false` for a caller with a fixed policy). Every asking caller's list is treated as not yet known: each one's repository gate can add repositories after the question. It returns the answer and, per repository, the brief's `refresh:` block: `switch_to_default_branch`, `pull`, and `read_default_by_ref` where true.
  - `### Entry point: \`late-join\``, run once a caller's repository list settles. Where the session's repository joined the list after the question was answered with an answer that did not consider it, it asks the four-option question then, as `/epics`' Phase 4 step 4 does today.

- [ ] **Step 1: Write the reference.**
  - **Move `/epics`' text into it, unchanged in meaning:**
    - the three-option question;
    - the two four-option forms;
    - the *read … by ref* and *scan … as it stands* paragraphs;
    - the branch tests: a detached HEAD counts as another branch, and takes the **known**-default form where `origin/HEAD` resolves, its `<branch>` reading `its detached HEAD at <short commit>`; an `origin/HEAD` that does not resolve takes the unknown-default form;
    - the brief mapping, `epics.md:636–638`;
    - the handling of a failed by-ref read, `epics.md:655`, with its report line `:1068`: not a failure, nothing asked, and the report saying the scan read a stale default ref and naming the failure.
  - **The fixed-policy case.** Where `asks: false`, the session's own repository on another branch is always read by ref (`read_default_by_ref: true`). `code-scanner` resolves the ref itself with `remote set-head --auto` and `read-only-repos` §3's chain, returning `REFRESH_BLOCKED` only where the chain is exhausted (`code-scanner.md:62–63`).
  - **The authority boundary.** Keep `read-only-repos` §4 as the authority on how a read by ref is done; this reference decides only when.
- [ ] **Step 2: Rewire the callers.**
  - `/epics`, `/specify`, `/design` and `/create-ard` replace their refresh step with the citation. `/update-spec` names it where it asks `/specify`'s question.
  - Each brief's `refresh:` lines become "per `scan-refresh`'s mapping for this repository".
  - Each caller's `prep` handling cites the failed-read handling, and its report gains the stale-ref line.
  - `/docs-audit` cites the fixed-policy case.
  - Every architecture-repository override line stays as it is (`design.md:290`, `specify.md:883`).
  - `/design`'s scanned-commit record gives no `with uncommitted changes` mark after a read by ref. Sweep "with uncommitted changes" across `dev-workflows`, `design-reviewer` and `design-format.md` included (refinement 6).
- [ ] **Step 3: Sweep** `fetch + pull default branch`, `switch_to_default_branch` and `read_default_by_ref` across `plugins/` (refinements 4, 6–8). The question's subject is the code scan's refresh. Every remaining copy must be one of:
  - the reference's own text;
  - a brief's citation;
  - `/document`'s `diff-summarizer` question, which recommends *fetch only*; its *fetch + pull* switches only on the user's explicit choice.

  The commit message says why each stays.
- [ ] **Step 4:** In to-fix, delete LC33. Add to-test items:
  - `/specify` and `/design` from the code copy on a feature branch: the four-option question recommending the by-ref read, the checkout unmoved, and `scanned_ref` the default ref. On `/design` from a dirty feature branch, the record reads `<slug> @ <commit>` with no `with uncommitted changes` mark.
  - The same on a detached HEAD with `origin/HEAD` set: the known-default form naming the detached commit.
  - With `origin/HEAD` unset: the unknown-default form.
  - `/specify` with `E2E_CODE_FETCH_UNREACHABLE=1` on the by-ref answer: no question, and the report naming the stale ref and the failure.
  - `/docs-audit` from a feature branch: no question, and the report naming the read by ref.
- [ ] **Step 5:** Run the gates (checks 4, 9 and 16 in particular), then commit: `feat(workflows-core): scan-refresh, the refresh question every scanning command asks (LC33)`.

### Task 4: `/security-workflows:scan` — the evidence line gets a slot (LC29)

**Files:**
- Modify: `plugins/security-workflows/commands/scan.md`: the step at `:330`, and the `### Register` template at `:482–486`.
- Modify: `plugins/security-workflows/docs/commands/scan.md`, wherever it shows the report.

- [ ] **Step 1:** Add this line to the `### Register` template, after *Awaiting security review*:
  ``- False positives decided: [each finding this run recorded false-positive, under the [SEC#n] it stands under after any replay, one line each — the evidence `<path>:<line>` at <evidence commit, short>, the line quoted as code, and the finding's own `<file>:<line>`; a cited line in another file, or more than 10 lines from the finding's, says so in one plain sentence — or "none"]``
- [ ] **Step 2:** In ***Show the evidence line***, keep the next question's text where a question follows. Add that, where none follows, the reply is the report's *False positives decided* line. That line quotes the line the check's `git show` read, never the person's evidence text.
- [ ] **Step 3:** Sweep "the text of the reply" and "evidence line" across `security-workflows` (refinements 6–8).
- [ ] **Step 4:** In to-fix, delete LC29. Add the to-test item: S4's setup in the 2026-11-04 record. The report's *False positives decided* line names `[SEC#3]` after the replay, and quotes `this.ratings = data;` with both locations.
- [ ] **Step 5:** Run the gates, then commit: `fix(security-workflows): the report's False positives decided line carries the evidence line (LC29)`.

### Task 5: `/design` — a rollback target per workload, and what a write adds (LC30, LC37)

**Files:**
- Modify `plugins/dev-workflows/commands/design.md`: `:344`, *Release verification*; `:315`, the whole-artifact gate rule.
- Modify `plugins/dev-workflows/references/design-format.md`: `:24–32`, the existing-system claim rule; and section 11, wherever it says "the rollback target".
- Modify: `plugins/dev-workflows/docs/commands/design.md`, where it describes either rule.

- [ ] **Step 1 (LC30).** At `:344`, change "its recommended answer naming the rollback target as an immutable reference …". The recommended answer names a rollback target for **each** workload a moved tag reaches, each as an immutable reference, wherever publishing moves the tags that workload pulls. The question's per-workload "what a restart of it would then pull" is already required there; leave it. Sweep "the rollback target" and "rollback target" across `dev-workflows` (refinement 8), including `design-format.md` §11.
- [ ] **Step 2 (LC37).**
  - In `design-format.md`'s claim rule, add: a statement of what changed between two commits is such a claim. It rests on an unfiltered `git -C <repo> diff --name-only <old> <new>`, named beside it, and never on a diff limited to the paths a scan was asked about.
  - In `design.md:315`, after "A change or addition the writing makes to anything a gate confirmed … goes to the whole-artifact gate", add two sentences:
    - "A sentence the writing adds that states a fact about the existing system — a premise, a provenance line, what changed between two scanned commits — is such an addition."
    - "A confirmed fix applied to every occurrence its own wording reaches is not a change; where the play-back miscounted the occurrences, the session file corrects the count."
- [ ] **Step 3:** In to-fix, delete LC30 and LC37. Add to-test items:
  - S3's setup: one rollback target per workload a moved tag reaches, and the web Deployment's restart named as shipping the unreleased web changes.
  - A resumed design whose header states what changed between commits: the claim names its unfiltered diff, and the whole-artifact gate plays the sentence back.

  In to-test LC4, replace "Run S3 … did not settle the first case below; its section says why." with a sentence saying `design.md:315` now decides what S3 left unclear. The no-change case stays in *Still to see*.
- [ ] **Step 4:** Run the gates, then commit: `fix(dev-workflows): /design names a rollback target per workload and plays back what its write adds (LC30, LC37)`.

### Task 6: the read after the review cap (LC36)

**Files:**
- Modify `plugins/workflows-core/references/escalation-rules.md`:
  - part `version-line`, the paragraph at `:515` (**Once the cap is spent, this is deliberately a reporting rule and not another cycle.**);
  - part `review`, *Edits after a verdict that is not BLOCK — the unspent re-review*, `:627–676`.

  Then regenerate the parts.
- Modify `plugins/workflows-core/agents/overlap-reader.md`: its `description`, its first paragraph, and the `caller` input at `:12`. `validate-catalog.py`'s `ENTRY_DESC_WARN` is 600, and the description is 561 characters now.
- Modify each command's cap text:
  - `plugins/dev-workflows/commands/design.md`, the cap paragraph at `:529–530`;
  - `plugins/product-workflows/commands/specify.md`, the cap paragraph in Phase 6 step 2;
  - `plugins/product-workflows/commands/update-spec.md`, at `:131`, where it follows `/specify` Phase 6 step 2.
- Modify the workflow-map lines that name each `overlap-reader` dispatch, within the rules-file budget: `.claude/rules/dev-workflows.md:36` (`/design`), `.claude/rules/product-workflows.md:45–46` (`/specify`, `/update-spec`), and `.claude/rules/workflows-core.md`'s `overlap-reader` line.
- Modify: `plugins/workflows-core/docs/reference/agents.md` (its row), and the three commands' docs pages.

- [ ] **Step 1 (part `version-line`, `:515`).** Amend the paragraph in place. Once the cap is spent, this stays a reporting rule for every command, save that `/design`, `/specify` and `/update-spec` first take one `overlap-reader` read of the edits that followed the last review. That read is not a review and raises no cap. The version line then names the read and its count of conflicts, and still says the verdict predates the edits.
- [ ] **Step 2 (part `review`).** Add a paragraph after "an edit after it falls back to the reporting rule above, the cap now spent", headed **The read after the last review**. It says:
  - **When it fires.** Where an edit answering the cap's last review's findings, or a decision settled at its question, follows that review, a command that dispatches `overlap-reader` (`/design`, `/specify`, `/update-spec`) dispatches it once more, before the handoff.
  - **The brief.** `caller` set to the read after the last review, and `scope: all`. `changed` lists each edit made after that review: its id or section, and its source (`review`, or `decision`). The command's own inputs come as its play-back read passes them: `artifact_path`; `session_path` (absent on `/update-spec`); `spec_path` (on `/design` only); `ard_paths` and `applicable_ard`.
  - **Its conflicts.** Each conflict it returns is asked at its own question, as the command asks a play-back's conflicts. A read that returns none asks nothing.
  - **No loop.** Edits that answer this read's own conflicts are read by the orchestrator's inline rule (*An inline fix is read against what it overlaps*), which runs on every edit as before, and are not read by the agent again.
  - **The declined case.** Where the unspent re-review was declined, so the cap was never spent, no such read follows. The version line says the verdict predates the edits, as now: the person chose to go on without a review.
  - **The other commands.** Every other command reports as now. Do not write a list; re-derive which commands the rule reaches from its own text.
- [ ] **Step 3: The agent.** Add the caller value to `overlap-reader`'s `caller` input. Widen its `description` and first paragraph from "before a play-back gate" to cover this read, keeping the description under 600 characters. Update the three workflow-map lines and the agents page.
- [ ] **Step 4: The commands.**
  - In `/design`'s and `/specify`'s cap paragraphs, add one sentence citing the rule, with no copy of its text.
  - In `/update-spec`, at `:131`, add one sentence saying that its read after the last review omits `session_path`, as its play-back read does (`:111`).
- [ ] **Step 5:** Run `python3 scripts/reference-parts.py generate`. Sweep "deliberately a reporting rule", "Once the cap is spent", "the cap now spent", "has not been reviewed" and "no review follows" (refinements 6–8).
- [ ] **Step 6:** In to-fix, delete LC36. Add to-test items:
  - S3's shape: decisions after the re-review bring one `overlap-reader` dispatch, its brief's `changed` naming them; each conflict is asked, and the version line names the read.
  - A post-cap read that returns no conflict: no question, and the version line naming a read with 0 conflicts.
  - A declined unspent re-review: no read.
  - `/epics` after its re-review: reported as before.
- [ ] **Step 7:** Run the gates, then commit: `fix: an overlap read follows edits made after the last review the cap allows (LC36)`.

### Task 7: `/specify` — its report's required lines, and the lineage of a PRD-level spec (LC31's third case, LC32); GIT-G1 takes the preflight's prints

**Files:**
- Modify `plugins/product-workflows/commands/specify.md`: the *Report:* paragraph, `:1282`; Phase 2.5, `:799`.
- Modify `docs/superpowers/specs/2026-11-08-git-g1-shared-specs-git-design.md`: §5.1.
- Modify: `plugins/product-workflows/docs/commands/specify.md`, where it lists the report or the lineage inputs.

- [ ] **Step 1 (LC31's third case).** In the command file, write the *Report:* paragraph's required lines as a template, shown in a fenced block under the heading `### Run details`.
  - **How the run prints it.** The heading `### Run details`, then each line filled in as plain markdown lines, not in a code fence. The block closes the Final report, after `commit-artifacts` has run, since it carries the `Specs repo:` line. A prose summary above it never replaces it.
  - **Its lines, in the paragraph's order:**
    - `Feature folder:`;
    - the `Lineage:` line in `document-lineage` §7's form;
    - `PRD gate:`, with the return value, and whether an authored `prd.md` was read;
    - the `architecture grounding:` and `team decisions:` lines;
    - `Spec review:` with the `spec-reviewer` verdict;
    - `Model routing:`;
    - `Run flags:`, only where Phase 0 printed one;
    - `Phase handoff:`, one per handoff;
    - `Session feedback:` and `Session cost:`, where printed;
    - `Specs repo:`, with any guard notice repeated in full.
  - **What stays prose.** The counts, the archives, the advisories, and the BRD-route and grounding additions keep their paragraphs.
- [ ] **Step 2 (LC32).** In Phase 2.5, capture and upstream-check each `epic.md` Step B read only where `focus_key` is set, that is, for an Epic-level specification. Add a sentence saying that at PRD level none is recorded, because `document-lineage` §4 puts `epic.md` below a PRD-level specification (`document-lineage.md:23`, `:67`). Sweep "each `epic.md`" across `product-workflows` (refinements 6–8), `/update-spec` included.
- [ ] **Step 3 (LC31's first two cases).** In the GIT-G1 design's §5.1, add one bullet requiring the start call to print two lines as script output, each at the point it fires: the session branch's creation line (`specs-repo-git` §3.4, `specs-repo-git.md:442`), and each guard's four-part §5 notice at detection. Cite LC31 as the reason: three live runs dropped them when they rested on the run remembering a rule.
- [ ] **Step 4:** In to-fix:
  - delete LC32;
  - narrow LC31 to its first two cases, with a closing line in PR10's form: **Taken up by GIT-G1** (2026-11-08), naming the design and §5.1.

  Add to-test items:
  - S1's run: the `### Run details` block whole;
  - S2's run: `lineage.py capture` with `prd.md` and `ard.md` only, and no conflict reported.
- [ ] **Step 5:** Run the gates, then commit: `fix(product-workflows): /specify prints its run details as a block and records no epic.md under a PRD-level spec (LC31, LC32)`.

### Task 8: the waiting marker on a merge-conditioned item (LC35)

**Files:**
- Modify `plugins/workflows-core/references/session-hygiene.md`, `:195–196`; then regenerate the parts.
- Modify: `plugins/workflows-core/docs/reference/session-cost.md` or whichever page describes the resume pointer's carry (`grep -rln 'waiting since' plugins/*/docs`).

- [ ] **Step 1:** After "An item that asks for a command to run is carried with its line ending `(waiting since <ISO datetime>)`", add: this holds whatever else the item waits on, a pull request's merge included, and its waiting datetime is the one the item was first carried with. Three live pointers in a row (S3, S5a, S5b) carried such an item with no marker.
- [ ] **Step 2:** Run `python3 scripts/reference-parts.py generate`. Sweep "waiting since" (refinement 7).
- [ ] **Step 3:** In to-fix, delete LC35. Add the to-test item: S5's chain, where the merge-conditioned PE item carries its marker in each pointer.
- [ ] **Step 4:** Run the gates, then commit: `fix(workflows-core): a merge-conditioned command item keeps its waiting marker (LC35)`.

### Task 9: `dev-workflows` and model routing — the plan-conflict recommendation, `run-state.py append`, the folder-read residue, and the reviewer's scope (R1, K1, K4, K5)

**Files:**
- Modify `plugins/dev-workflows/commands/implement.md`:
  - `:1108`, the plan-conflict question;
  - `:379`, the `append` note;
  - the routing comment `:493`;
  - the invariant `:1542`.
- Modify `plugins/dev-workflows/scripts/run-state.py`: `append`, and its docstring, `:40–44`.
- Modify `plugins/dev-workflows/commands/ready.md`:
  - the Phase 1.5 routing comment (`:221`);
  - the report template's *Detection steps* line (`:550`);
  - Phase 4's brief (`:419–425`).
- Modify `plugins/dev-workflows/agents/readiness-reviewer.md`: its read scope.
- Modify `plugins/product-workflows/commands/epics.md`: the routing comment `:381`, and the invariant `:1244`.
- Modify `plugins/product-workflows/commands/specify.md`: the routing comment `:481`.
- Modify `plugins/workflows-core/references/model-routing/classification.md`: §8.2, §8.3, §9.2 and §9.4 (`:408`, `:420`, `:562`, `:590`).
- Modify: the docs pages of `/implement`, `/ready`, `/epics` and `/specify` where they route the folder read; `plugins/workflows-core/docs/` where it describes model routing; and the agents page row for `readiness-reviewer`.

- [ ] **Step 1 (K1).** Write a failing selftest case:
  - `append triage '[<a>, <b>]'` exits 2 with a message naming `set`, or one value per pair, and leaves the file unchanged;
  - the stdin object `{"triage": [<a>, <b>]}` does the same.

  Run it and see it fail. Then implement: `append` refuses any JSON array value with exit 2, before any write. The contract already says each value is one entry; the script now refuses the slip silently taken in R1. See it pass. Update the docstring and `implement.md:379`.
- [ ] **Step 2 (R1).**
  - **The rule.** Where every deferred finding contradicts only the plan's own text, and neither `design.md` (where the run has one) nor the specification, present `choices: ["Revise the plan (the finding governs) (Recommended)", "Apply the fix, keep the plan text (logged in Phase 5)"]`. Where any one also contradicts `design.md` or the specification, present the unmarked array, its question's own text naming which finding and why no option is recommended.
  - **The writing.** Write both arrays out, each with the condition that selects it.
  - **The sweep.** Sweep the question's labels across `dev-workflows`, its docs page included.
- [ ] **Step 3 (K4).** The folder read is the orchestrator's own inline work in every command: the reader agent it was once routed to was retired, and `68c26cf80` renamed the routing lines rather than removing them.
  - Remove "the folder read" from the routing comments and invariants named above, and from `/ready`'s report template line.
  - Re-word `classification.md` §8.2–§9.4 so that `code-scanner`, and nothing called "the folder read", is pinned to the §2.1 detection chain, and the folder read is the orchestrator's.
  - Sweep "folder read" across `plugins/` and the rules files (refinement 6). The commit message cites `68c26cf80`.
- [ ] **Step 4 (K5).** State the reviewer's read scope in Phase 4's brief and in `readiness-reviewer.md`. It reads:
  - every artifact path its brief names;
  - every artifact `derived_phase` names, each in-scope `implementation.md` included;
  - the `dev-workflows/` bookkeeping of the unit folder and the PRD folder.

  It reads nothing in a code repository, and a fact it cannot see there it reports as unverified.
- [ ] **Step 5:** Add to-test items:
  - an `/implement` plan conflict on plan detail alone recommends *Revise the plan*, and one touching `design.md` recommends nothing and says why;
  - `/ready BOOK-4-01` dispatches no folder-read agent, and its reviewer reads no code repository.

  `run-state.py` is covered by its selftest alone.
- [ ] **Step 6:** Run `python3 plugins/dev-workflows/scripts/run-state.py --selftest` and the gates, then commit: `fix(dev-workflows): plan-conflict recommendation, run-state append refuses an array, the folder-read routing residue, readiness-reviewer's scope (R1, K1, K4, K5)`.

### Task 10: `/epics` — the marker cap's ranking, and a style result with nothing for the fixer (K2, K3)

**Files:**
- Modify `plugins/product-workflows/commands/epics.md`:
  - the marker cap at `:880`;
  - Phase 6.2, `:784–796`;
  - `### Deferred items`, `:1129`, which already names each finding a marker past the cap left there. Only the ranking is new.
- Modify `plugins/workflows-core/references/escalation-rules.md`, `:749–752`, where the shared rule states the cap; then regenerate the parts.
- Modify: `plugins/product-workflows/docs/commands/epics.md`.

- [ ] **Step 1 (K2).** Where the cap is stated, both in `/epics` and in the shared rule, add the ranking: the cap's three markers go to the open findings needing a decision, ranked highest severity first, then in the order the review listed them.
- [ ] **Step 2 (K3).** In Phase 6.2, add a sentence for a `VIOLATIONS_FOUND` result that holds no finding the fixer would take, that is, no `MAJOR` left after the `fixed_headings` and user-resolved-text exclusions. Then no `doc-fixer` is dispatched, nothing is re-run, and the findings go to the Phase 9 report. Cite `workflows-core:finding-triage` § *When triage empties the survivor set* as the same principle, with no copy of it.
- [ ] **Step 3:** Add to-test items:
  - R2's shape, six decision findings against a cap of three: markers go by severity, then review order;
  - a NIT-only style result: no fixer dispatched.
- [ ] **Step 4:** Run the gates, then commit: `fix(product-workflows): /epics ranks its marker cap and skips an empty style-fix pass (K2, K3)`.

### Task 11: release bookkeeping

**Files:**
- Modify: each touched plugin's `.claude-plugin/plugin.json` and its `.claude-plugin/marketplace.json` entry. The expected bumps are minor everywhere, since each adds behaviour:
  - `workflows-core` 1.78.16 → 1.79.0;
  - `dev-workflows` 4.59.7 → 4.60.0;
  - `product-workflows` 3.78.9 → 3.79.0;
  - `docs-workflows` 1.35.9 → 1.36.0;
  - `security-workflows` 0.10.11 → 0.11.0.

  Re-check each against `main` at execution time, since another batch may land first.
- Modify: each touched plugin's `CHANGELOG.md`, a dated section (`— 2026-11-<day>`).
- Modify: `.claude/rules/plugin-updates-coupling.md`. Add one bullet: `workflows-core` 1.79.0 with `dev-workflows` 4.60.0, `product-workflows` 3.79.0 and `docs-workflows` 1.36.0, both directions. It names:
  - the `scan-refresh` reference and its two entry points;
  - the escalation rule's read after the last review, and `overlap-reader`'s new `caller` value;
  - the `classification.md` re-wording;
  - that the dependents call their own copy of `tree-snapshot.py`.

  Keep `security-workflows` 0.11.0 out of the bullet unless it relies on new `workflows-core` text.
- Modify: `docs/superpowers/to-test-on-real-project.md`, so the new section's heading carries its versions.

- [ ] **Step 1:** Bump the versions, then write the CHANGELOG sections and the coupling bullet. Every CHANGELOG fix line names its LC, R1 or K id.
- [ ] **Step 2:** Check two things: that to-fix holds no LC29–LC37 item save LC31's narrowed GIT-G1 line, and that every task's to-test items sit under the new section.
- [ ] **Step 3:** Run the full gate chain from `.github/workflows/validate-catalog.yml`, the new tree-snapshot steps included, as one `&&` chain ending `echo "EXIT=$?"`. Read `EXIT=0`.
- [ ] **Step 4:** Commit: `chore: release workflows-core 1.79.0, dev-workflows 4.60.0, product-workflows 3.79.0, docs-workflows 1.36.0, security-workflows 0.11.0 (LC29–LC37, R1, K1–K5, K7)`.

---

**After Task 11:**
- run the whole-branch Opus review, with one fix pass and a scoped re-review;
- preserve the SDD rulings in `docs/superpowers/verification/`;
- push, and open the pull request without waiting.

# Live-check round 2 fixes (LC12–LC28, D39) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every defect the 2026-10-29 live-check round filed (to-fix LC12–LC28) and D39, so the next live round can verify them alongside the to-test items still open.

**Architecture:** A fix batch over five plugins, in this order:
1. Shared machinery in `workflows-core`: the review-decision rule, the code scanner's read-by-ref mode, the Rule-only overlap read, and two scripts.
2. The commands that consume it, one task per plugin.
3. One closing task for the release bookkeeping.

All changes are to command, agent and reference prose, plus two Python scripts with self-tests.

**Tech Stack:**
- Markdown command, agent and reference files, which agents execute.
- Python 3 scripts with `--selftest`: `lineage.py` and `session-branch.py`.
- The repository's gate chain.

**Spec:**
- `docs/superpowers/to-fix.md`: § *From the live checks of 2026-10-29* (LC12–LC28), and D39 in § *Design-level*.
- Evidence: `docs/superpowers/verification/2026-10-29-live-checks.md`.
- The plan review of 2026-11-03 (READY WITH CHANGES) is folded in below.

The user's rulings of 2026-11-03:
- Fix all the items in one batch.
- LC17: `/specify` and `/design` ask the user about each review finding that needs a decision, offering the reviewer's options plus *Leave it open*.
- LC19: `/epics` recommends reading the default branch's tip by ref, without moving the checkout.

## Global Constraints

**Process**
- Follow `docs/superpowers/reviews/2026-10-26-fix-batches.md` § *How to run a batch*, steps 2–8.
- Read the area's `.claude/rules/` file with the Read tool before editing there.
- Re-locate each defect by its quoted text. Line numbers below are at `db769a23`.

**Editing discipline (`CLAUDE.md` § Editing discipline binds every edit)**
- Run the claim-expiry sweep with all eight refinements of `.claude/rules/claim-sweep.md`, including refinement 7's before-and-after count of each changed literal string.
- Apply the sentence-context checks, extent face and pointer face.
- `workflows-core:instruction-file-maintenance` binds edits to `references/*.md` and to `.claude/rules/*.md`. Re-derive any number you write there.

**Generated files**
- Never edit `plugins/workflows-core/reference-parts/` by hand.
- After editing any `workflows-core` reference, run `python3 scripts/reference-parts.py generate`. The references split by part are `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. `phase-handoff` has entry-point files.

**Questions**
- Every `choices:` array has 2–4 options and no "Other".
- `(Recommended)` marks only a recommended option. Where none is recommended, the question's own text says so.
- Each question's own text carries what the person needs to answer it. It never points at "above".

**Snapshots**
- Every `git status` snapshot this plan adds uses `--porcelain -z --untracked-files=all`, as the existing re-reads do (`implement.md:744`, `code-handoff.md:63`).

**Content rules**
- Every behaviour change updates its docs page under `plugins/<plugin>/docs/`. Each claim on the page is derived from the command or agent text.
- No tracker vendor names without a marker.
- Never name the organisation the plugins were extracted from, and never use a corporate email domain.

**Tracking records**
- House step 8: each task deletes the to-fix items it fixes from `docs/superpowers/to-fix.md` in its own commit.
- None of these items has a review-file entry. D39 came from the D30 review, which is recorded only in commit `1ccb1fc7`'s message.
- Version bumps, `CHANGELOG.md`, `marketplace.json`, the coupling bullet and `to-test-on-real-project.md` belong to Task 7 alone.

**Commits**
- Before each commit, `git branch --show-current` must print `fix/live-checks-r2` (worktree `/workspace/.worktrees/lc-r2-fix`).
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

**Task gates.** Each task runs these before its commit, and all must pass:
- `./scripts/check-docs.sh --root .`
- `./scripts/check-id-grammar.sh --root .`
- `python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check`
- `node scripts/mermaid/check-mermaid.mjs --root .`, after `npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund` once
- `python3 scripts/validate-catalog.py`
- the task's own scripts' `--selftest`

Task 7 runs the full chain.

## Review Focus

1. **LC28, a session branch that does not exist.** A no-op flush on a specs repository with no `session/<identity>` creates nothing, prints `committed: null, created: false, sync: null`, and pushes nothing. A later `lift`, `put-back` or `commit` still works. *Task 1 self-test.*
2. **LC24, mixed flag forms.** A `capture` with several paths after one `--from-disk`, then `--from-disk` repeated, records every path once. *Task 1 self-test.*
3. **LC19, a fetch that fails.** On the read-by-ref answer, a fetch that fails or times out still scans the stale default ref. It returns `refreshed: false` and names the failure, and never falls back to the working tree. *Task 2 decision, Task 7 to-test item.*
4. **LC22, mixed index sets.** A run that wrote one index identical to `<default-ref>`'s and one that differs or is absent there still asks the handoff question. *Task 3 decision, Task 7 to-test item.*
5. **LC16, a path that already existed.** A test run that changes a path existing before it never gets *Delete* offered, and no option is recommended. *Task 5 decision, Task 7 to-test item.*

---

### Task 1: `workflows-core` scripts — LC24 and LC28

**Files:**
- `plugins/workflows-core/scripts/lineage.py`: the `capture` sub-parser (~1259–1263) and `selftest`
- `plugins/workflows-core/references/document-lineage.md` §5 step 1 (~76)
- `plugins/workflows-core/scripts/session-branch.py`: `commit` (~843, creation at ~846–850), `sync` (~750, ~904–907) and `selftest`
- `plugins/workflows-core/references/specs-repo-git.md`:
  - §8.2 step 1 (~1314) and the output sentence after the steps (~1319)
  - §3.4's session-mode flush push (~436–440)
  - §8.4's push measure (~1336)

**Decisions:**

**LC24.**
- `--from-ref` and `--from-disk` take `action="extend", nargs="+"`, so several paths may follow one flag and either flag may also be repeated.
- In §5 step 1, write `--from-ref <path> [<path> …] --from-disk <path> [<path> …]` and add "either flag may also be repeated".

**LC28.**
- `commit` computes the would-be base (`git merge-base HEAD <default-ref>`) without creating the ref.
- It creates `refs/heads/<branch>` at the commit itself: `git update-ref refs/heads/<branch> <new commit> 0000000000000000000000000000000000000000`. So a call whose paths all end in `unsettled` creates no empty branch either.
- Where nothing is committed and the branch did not exist:
  - step 3's merges and step 4 are skipped;
  - the result is `committed: null, created: false, sync: null`.
- Spec text to change:
  - §8.2 step 1 says the branch is created only by a commit.
  - §3.4 and §8.4 each gain: "where the session branch does not exist, nothing is pushed". Today §8.4's `rev-list … refs/heads/<session branch>` exits 128 on a missing ref.
- Check `lift` and `put-back` against an absent branch.

**Steps:**
- [ ] **Step 1:** Write the failing self-test `capture_several_paths_per_flag`.
  - Setup: a specs repository with `a.md`, `b.md`, `c.md` and `d.md` committed.
  - Call: `capture --from-disk a.md b.md --from-disk c.md --from-ref d.md --out <f>`.
  - Assert: exit 0, and all four paths recorded, each once. The output does not say which flag an entry came from (`lineage.py:337–356`).
- [ ] **Step 2:** Run `python3 plugins/workflows-core/scripts/lineage.py --selftest`. Expect FAIL: a FAIL line naming `unrecognized arguments`, or a crash on argparse's `SystemExit(2)`.
- [ ] **Step 3:** Change both `add_argument` calls, and edit §5 step 1.
- [ ] **Step 4:** Run the self-test again. Expect PASS.
- [ ] **Step 5:** Write the failing self-test `noop_commit_creates_no_branch`. On a repository with no session branch:
  - With no session-file change, `commit --branch session/zz --default-ref main` prints `committed: null`, `created: false` and `sync: null`, and `git rev-parse --verify --quiet refs/heads/session/zz` fails.
  - With only a path that ends `unsettled`, no branch is created either.
  - With a session-file change, `commit` prints `created: true` and a commit, and `lift` and `put-back` on the branch exit 0.
- [ ] **Step 6:** Run `python3 plugins/workflows-core/scripts/session-branch.py --selftest`. Expect FAIL.
- [ ] **Step 7:** Implement the change and edit §8.2, §3.4 and §8.4. Delete LC24 and LC28 from `to-fix.md`.
- [ ] **Step 8:** Run both self-tests and the task gates. Expect PASS.
- [ ] **Step 9:** Commit: `fix(workflows-core): lineage capture takes several paths per flag; a no-op session flush creates no branch (LC24, LC28)`.

### Task 2: `workflows-core` shared rules — LC17, LC19, LC25

**Files:**
- `plugins/workflows-core/references/escalation-rules.md`:
  - *Findings a review leaves open — the offer to apply them* (~526–561)
  - *A finding left open that needs a decision is recorded in the artifact* (~666–720)
  - *A BLOCK review's other findings — folded into its fix cycle* (~722+)
- `plugins/workflows-core/agents/code-scanner.md`:
  - the brief's `refresh:` block (~28)
  - Process step 2 (prep), step 3 (scan; on a writable mount it is "pure filesystem search" today, `:62`), step 4 (read candidates) and step 7 (line bounds at `scanned_ref`)
  - the return block
  - the hard rules: `:128`, the allowed prep, gains the capped fetch; `:130`, "does not accept a branch override", names its one exception
- `plugins/workflows-core/references/handoff/code-scanner.md`, the format file (`:16–18`, `:34–35`, `:77`)
- `plugins/workflows-core/references/read-only-repos.md`: `:7` (the claim that ref reading is for read-only mounts only), `:100` (the writable `scanned_ref` definition), `:107` and `:113` (the uncommitted-changes rule), §6 and §7
- `.claude/rules/workflows-core-read-only.md`: its authority paragraph
- `plugins/workflows-core/agents/overlap-reader.md`:
  - inputs (`:12–15`) and `caller` list (`:12`)
  - Method steps 3 and 5 (`:25`, `:30`)
  - return
  - `description`, which is 627 characters; trim it below the 600-character warning
- `.claude/rules/product-workflows.md:45` and `.claude/rules/workflows-core.md:76`, the overlap-reader map lines
- `workflows-core` docs pages that describe any of these: `grep -rln "code-scanner\|overlap-reader\|left open" plugins/workflows-core/docs`

#### Interface 1: the asking set (consumed by Tasks 4 and 5)

The commands in `escalation-rules` that put a decision-needing finding to the user become `/create-prd`, `/update-prd`, `/create-ard`, `/specify` and `/design`. This applies at the offer after a review whose verdict is not `BLOCK`, and in a `BLOCK`'s *Fold* cycle.

**The triggers widen with it.**
- The offer fires where the review leaves open at least one finding whose fix is only an edit, or, in the asking set, at least one whose fix needs a decision.
- That trigger is worded at `escalation-rules.md:537–540`, and copied in `specify.md:1029–1030` and `:1058–1060`, `design.md:470–471` and `:493–495`, and in the three PRD/ARD commands.
- For the asking set, the *Fold* question's "which stays open whatever the answer" goes (`specify.md:1033–1034`, `design.md:474–475`).
- The decision questions are asked whatever the offer's answer, *Go on without applying them* included, since each carries its own *Leave it open*.
- Where no edit-only finding is open, no offer is made and only the decision questions are asked.
- A decision the person left open is not carried into the re-review's offer again (`escalation-rules.md:549–550`).

**Question shape: one question per finding.**
- The question's text names the finding: its severity, where it is, and the decision it needs.
- The array carries the reviewer's options for that decision. Where the reviewer gives none, the run drafts answers as its grill would. At most three are carried.
- The recommended option gets the per-showing `(Recommended)` placeholder (`escalation-rules.md:174–182`) where the reviewer or the run recommends one. Where nothing is recommended, the question's text says so (`:184–186`).
- The last option is `"Leave it open"`.
- Where there are more than three options, the question's text lists them all.

**After the answer.**
- An answer is applied as an edit, read against what it overlaps.
- In a *Fold* cycle the re-review covers the edit. After the last review, the version line names it among the edits the verdict predates.
- *Leave it open* records the finding as *A finding left open … is recorded in the artifact* says:
  - `/specify`: a `- [ ]` open question;
  - `/design`: the final report and the pull request, as today;
  - `/create-prd` on the BRD route keeps its `[AS#n]` triage.

**This goes beyond the ruling for `/create-prd`, `/update-prd` and `/create-ard`.** They already ask these decisions (`create-prd.md:829–830`, `update-prd.md:177`, `create-ard.md:732`) but offer no deferral. They gain the explicit *Leave it open* and nothing else. Say so in the CHANGELOG and the PR body, so the user can veto it.

#### Interface 2: the code scanner reads the default branch by ref

The `refresh:` block gains `read_default_by_ref: true`, optional, default `false`. It is a boolean, not a ref, so `code-scanner.md:130`'s no-branch-override rule still holds: the scanner can read only the default branch's tip.

When it is `true`:
- `switch_to_default_branch` and `pull` are ignored.
- One capped fetch runs: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/bounded.py" <N> git -C "<repo_path>" fetch --quiet origin`, with `<N>` written explicitly. Today `code-scanner` caps no network call.
- `<default-ref>` is resolved by `read-only-repos.md` §3's chain.
- The scanner reads at `<default-ref>` by §2–§4's write-free reading. That works on a writable clone too. It never switches or pulls, and never reads the working tree.

It returns:
- `read_only: false`
- `scanned_ref: <default-ref>`
- `refreshed: true`
- `refresh_note: "read <default-ref> by ref; checkout left on <branch>"`

Failures:
- A failed or timed-out fetch still reads the stale `<default-ref>`, with `refreshed: false` and the failure named in `refresh_note`.
- A default ref that does not resolve returns `status: REFRESH_BLOCKED`, with a note.

#### Interface 3: overlap-reader's Rule-only read

- `scope: all | rules`, default `all`.
- `draft_path`, optional: a file holding a draft not yet written to the artifact. `/specify` writes a stage's section only after its gate (`specify.md:919`), so Stage 4's criteria are not on disk at its play-back.
- A Stage 4 `caller` value.

Under `scope: rules`, the reader checks only the inherited `[AD#N]` Rules against the artifact, the draft and the run's decisions, confirmed inferences included. It returns the `ad_rules` list, the Rule count and each Rule departure, and no other kind's list.

**Steps:**
- [ ] **Step 1:** Edit `escalation-rules.md`'s three sections to the asking set, the widened triggers and the question shape. Then re-read the *Used by* lines (556–561 and 719–720) for the extent face. "`/design` is not among them" stays true for recording, since `/design` writes no open question. Keep it, and add that `/design` now asks first.
- [ ] **Step 2:** Sweep. Count `` `/create-prd`, `/update-prd`, `/create-ard`) `` and "every other records it" across refinement 4's scope, before and after. Update every copy of the asking set in `workflows-core`, docs pages included. The command copies belong to Tasks 4 and 5.
- [ ] **Step 3:** Edit `code-scanner.md`, `handoff/code-scanner.md`, `read-only-repos.md` and `.claude/rules/workflows-core-read-only.md`. Sweep "read-only mount" exclusivity claims (refinement 3).
- [ ] **Step 4:** Edit `overlap-reader.md` and the two map lines. Trim the description below 600 characters, keeping what the agent does, when to use it and what it is not for.
- [ ] **Step 5:** Run `python3 scripts/reference-parts.py generate`, then the task gates. `validate-catalog.py` should no longer warn on `overlap-reader`.
- [ ] **Step 6:** Commit: `fix(workflows-core): grill commands ask a review's decisions; code-scanner reads the default tip by ref on a writable clone; overlap-reader's Rule-only read (LC17, LC19, LC25)`. LC17, LC19 and LC25 stay in to-fix until Tasks 4 and 5 finish them.

### Task 3: `workflows-core` text fixes — LC13, LC20, LC22, LC26

**Files:**
- `plugins/workflows-core/references/epic-picker.md`: *The picker* (~30–45) and *The cap* (~60–95)
- `plugins/workflows-core/references/escalation-rules.md`: the noun list of the unspent re-review option (`:591–592`, the only list; no command carries its own)
- `plugins/workflows-core/commands/frames.md`: Phase 3 (~332) and the Final report (~478–483)
- `plugins/workflows-core/docs/commands/frames.md`
- `plugins/workflows-core/references/specs-repo-git.md` §6 (~1195–1253)

**Decisions:**

**LC13: the Epic picker.**
- The remainder option *Another Epic (you'll be prompted for its key)* is the array's last option, after any option the command adds. *The cap* says so.
- Rows show the bare key. *The picker* already says each row carries "its `key` read from frontmatter" (`:39–41`). *The cap*'s example contradicts that, so rewrite it to bare keys: `◐ ACME-77-02 order intake`.
- A typed prefixed key is read through `addressing`' `read-key` before it is matched against the listed keys.
- Grep `/specify`, `/design` and `/implement` for prefixed-form row examples, and fix any found.

**LC20: the re-review option's label.**
- Keep the template `"Re-review the edited <artifact> once (Recommended)"`.
- In the noun list at `:591–592`, strip each leading article, and use `pages` for "the pages written".
- Add that `<artifact>` is a bare noun phrase.

**LC22: when `/frames` offers a handoff.**
- Phase 3 fires only where at least one written index is absent from `<default-ref>` or differs from it there.
- Reuse the existing "already on `<default>`" test, `git -C "$SPECS_PATH" diff --quiet <default-ref> -- <paths>` (`phase-handoff.md:111`). Confirm that an absent path counts as differing.
- Cite `<default-ref>` from `workflows-core:specs-repo-git` §3.2.
- Where every written index matches, print: `Phase handoff: not offered — every index this run wrote is already on <default> as written.`
- A5b's shape still asks.
- Update the Final report's "A run that wrote no index prints neither", and the docs page's mermaid label "(only where an index was written)".

**LC26: "(1 files)".**
- Keep `(<N> files)`.
- Add one sentence before §6's table that also covers the two rows after it (`:1251`, `:1253`): where `<N>` is 1, the line reads `(1 file)`.
- First grep `scripts/` and `plugins/*/scripts/` for a parser matching `files)`. If one exists, report it and stop rather than change it.

**Steps:**
- [ ] **Step 1:** Make the four edits. Sweep each by phrase with refinement 7's counts. Delete LC13, LC20, LC22 and LC26 from `to-fix.md`.
- [ ] **Step 2:** Run `python3 scripts/reference-parts.py generate`, then the task gates.
- [ ] **Step 3:** Commit: `fix(workflows-core): picker remainder last and bare keys; re-review label; /frames offers a handoff only for an index not on the default branch; "1 file" (LC13, LC20, LC22, LC26)`.

### Task 4: `product-workflows` — LC14 + D39 (`/epics`), LC17, LC18, LC19, LC21, LC23, LC25, LC27

**Files:**
- `plugins/product-workflows/commands/epics.md`:
  - Phase 2's plan approval (~384–398)
  - the repo-refresh variant (~333)
  - Phase 5's brief for the session repository
  - Phase 7.4's agent briefs (~900–925) and §4.0's register check
  - the report heading (~1016)
  - the *Clarifications* line (~1077)
- `plugins/product-workflows/commands/specify.md`:
  - the review-finding offers and the *Fold* question (~1029–1060)
  - Stage 4's overlap read
  - the `### Next step` paragraph (~1273)
- `plugins/product-workflows/commands/create-prd.md` (~829–830), `update-prd.md` (~177) and `create-ard.md` (~732): LC17's widened triggers and *Leave it open*
- `plugins/product-workflows/docs/commands/{epics,specify,create-prd,update-prd,create-ard}.md`, wherever they describe any of the above

**Interfaces consumed:** from Task 2, the asking set, the triggers and the question shape; `refresh.read_default_by_ref`; and `overlap-reader`'s `scope: rules`, `draft_path` and Stage 4 `caller`.

**Decisions:**

**LC14 + D39: `/epics` Phase 7.4.**
- In every Phase 7.4 brief (`:909–922`), replace "project root" with "the PRD folder". Add: "The session's working directory may be a code repository; never edit anything outside the PRD folder."
- Snapshot before the agents are dispatched, with `git hash-object` fingerprints of each dirty path in both:
  - `git -C "$SPECS_PATH" status --porcelain -z --untracked-files=all -- <prd_dir>`;
  - where the session's working directory is in a git repository other than the specs repository: `git -C "<session top level>" status --porcelain -z --untracked-files=all`.
- After the agents return:
  - A returned path that was dirty before is reported, never declared as a deliverable. So is one absent before, meaning missing from the before-snapshot and from `HEAD`, and `??` after.
  - A session-repository path whose status or fingerprint changed is reported as an edit outside the PRD folder.
- Where the session's directory is the specs repository, or no repository at all, only the first snapshot is taken.
- D39's last sentence: §4.0's register check gets the by-path match that `/ready` and `/conformance` use.

**LC17: the PRD, ARD and spec commands.**
- `/specify`, `/create-prd`, `/update-prd` and `/create-ard` apply Task 2's triggers and question shape at the offer and in the *Fold* cycle.
- In `/specify`, remove "which stays open whatever the answer", and any sentence that writes such findings as open questions without asking.
- *Leave it open* keeps today's recording.

**LC18: plan approval.** The question's own text carries the whole concise plan Phase 2 presents (`:384–398`), including existing Epics, the docs-grounding line and the size limit. The orchestrator also prints it.

**LC19: the refresh question.**
- Where the session repository is on another branch and its default branch is known, ask:
  `choices: ["fetch + pull default branch, but read <session-slug> at origin/<default> by ref — your checkout stays on <branch> (Recommended)", "fetch + pull default branch, but scan <session-slug> on <branch> as it stands", "fetch + pull default branch, <session-slug> included", "no refresh"]`
- *fetch only* leaves this variant. The question's text says a typed *fetch only* still applies to every repository.
- On the recommended answer, Phase 5's brief for the session repository carries `refresh: {read_default_by_ref: true}`.
- Fix the Phase 5 brief's "'fetch only', in either form".
- Where the default branch is unknown, keep today's four options and recommendation. The question's text says that with no known default branch there is no ref to read.

**LC21: report heading.** `## keyed Epic Drafting Report` becomes `## Epic Drafting Report`.

**LC23: the Epic-designing design offer.** This is the `/dev-workflows:design <PRD>` offer on a multi-component PRD with an Epic's spec on `<default>`.
- It carries no `<merge-clause>`.
- It gains one clause: the Epic's specification predates this PRD-level one, which `/product-workflows:epics <PRD>` folds into the Epics, so a design started now starts from the older Epic specification.
- The flat-spec offer keeps its clause.

**LC25: Stage 4's overlap read.**
- At Stage 4's play-back, write the Stage 4 draft (criteria, and the inferences being played back) to a temporary file where `workflows-core:run-flags` puts the run's files.
- Dispatch `workflows-core:overlap-reader` with `scope: rules`, the Stage 4 `caller` and `draft_path`.
- The play-back line takes its `[AD#N] Rules` count and its departures from the return. The inline read keeps triggers, imports and failure paths.
- Each departure is put to the user before the gate, offered only as an ARD deviation.
- The whole-specification read is unchanged.

**LC27: the *Clarifications* line.**
- It becomes `[Phase 6.1's clarifications — resolved: <n>; deferred (became blockers): <n>] — or "none raised"`.
- Where the review left markers, add `The review's markers: see ### Deferred items.`

**Steps:**
- [ ] **Step 1:** Make the `epics.md` edits. Count "project root" in `epics.md` before and after; it should be 0 in the briefs afterwards.
- [ ] **Step 2:** Make the `specify.md`, `create-prd.md`, `update-prd.md` and `create-ard.md` edits. Sweep these across refinement 4's scope: "stays open whatever the answer", "open questions without", and `<merge-clause>` on `/dev-workflows:design`.
- [ ] **Step 3:** Update the five docs pages. Delete LC18, LC19, LC21 (the `/epics` part only; Task 6 owns `document.md`), LC23, LC25 and LC27 from `to-fix.md`. LC17 and LC14/D39 wait for Task 5. Run the task gates.
- [ ] **Step 4:** Commit: `fix(product-workflows): /epics plan in its question, read-by-ref refresh, PRD-folder briefs, report wording; /specify and the PRD/ARD commands ask review decisions, Stage 4 Rule read, honest design offer (LC14, LC17–LC19, LC21, LC23, LC25, LC27, D39)`.

### Task 5: `dev-workflows` — LC14 + D39 (`/ready`, `/conformance`), LC15, LC16, LC17

**Files:**
- `plugins/dev-workflows/commands/ready.md` Phase 5 step 2a (~495–520)
- `plugins/dev-workflows/commands/conformance.md` Phase 5.5 (~421–430)
- `plugins/dev-workflows/commands/design.md`:
  - *Release verification* and the Phase 4 deploy-surface theme brief (LC15)
  - the review-finding offers and the *Fold* question (~470–495) (LC17)
- `plugins/dev-workflows/commands/implement.md`: Pre-Phase 3.5 (~744) and Phase 3.5's verify step (LC16)
- `plugins/dev-workflows/references/code-handoff.md`, only if the handoff line's naming of `pre_existing_dirty` paths needs a reason (LC16)
- the matching docs pages under `plugins/dev-workflows/docs/`

**Interfaces consumed:** from Task 2, the asking set, the triggers and the question shape.

**Decisions:**

**LC14 + D39.** As in Task 4's `/epics` copy:
- "project root" becomes `unit_folder`'s folder, at `ready.md:501–514` and the dispatch at `conformance.md:421`;
- both snapshots are taken with fingerprints and `--untracked-files=all`;
- returned paths are reported, never declared;
- session-repository changes are reported.

**LC15: the rollout's reach.**
- The deploy-surface theme brief adds: "every image the release builds, publishes or retags, and every workload in the deploy manifests that pulls any of those images, with the tag it pulls and its pull policy".
- *Release verification* plays each such workload back as a premise at `file:line`.
- The rollout question names each workload a moved tag reaches.

**LC16: files a test run touches.** This uses the plan review's simpler form: no new run-state key, and no change to `code-handoff` §2.2's carve-out.
- Just before and just after each test-baseliner run (the Pre-Phase 3.5 capture and each Phase 3.5 verify run), read `git status --porcelain -z --untracked-files=all` and fingerprint each listed path.
- A path new to the after-read, or whose fingerprint changed, was touched by that test run. Tracked files count too.
- Ask once per test run. The question's text lists each such path and what it was before: absent, clean tracked, edited by this run, or dirty before the run.
  - Paths the test run created: `choices: ["Leave them out of the commit (Recommended)", "Delete them", "Commit them with the change"]`.
  - Paths that existed before and the test run changed: `choices: ["Keep the test run's change in the commit", "Leave the file out of the commit"]`. No option is recommended, and the question's text says so. *Delete* is never offered for a path that existed before.
- *Leave out* adds the path to `pre_existing_dirty` with its after-read fingerprint, as S7's orchestrator did by hand, so §2.2's carve-out keeps it out. It also adds an `assumptions` line naming the path as written by a test run.
- *Delete them* removes only created paths.
- *Commit* records nothing.
- Check how the handoff line names `pre_existing_dirty` paths. Where an entry can carry a reason cheaply, have it say "written by a test run".

**LC17: `/design`.** Apply Task 2's triggers and shape at the offer and in the *Fold* cycle, and remove "which stays open whatever the answer". *Leave it open* leaves the finding in the final report and the pull request.

**Steps:**
- [ ] **Step 1:** Make the `implement.md` edits, and the `code-handoff.md` edit if it is needed. Sweep `pre_existing_dirty`'s statements across refinement 4's scope.
- [ ] **Step 2:** Make the `ready.md`, `conformance.md` and `design.md` edits. Sweep "project root" and the asking-set copies.
- [ ] **Step 3:** Update the docs pages. Delete LC14, LC15, LC16, LC17 and D39 from `to-fix.md`. Run the task gates, including `python3 plugins/dev-workflows/scripts/run-state.py --selftest`, which checks that `implement.md` quotes its keys.
- [ ] **Step 4:** Commit: `fix(dev-workflows): /implement asks about a test run's files before its commit; /design's rollout reads every workload an image move reaches and asks review decisions; folder-scoped maintenance briefs (LC14–LC17, D39)`.

### Task 6: `docs-workflows` and `security-workflows` — LC21, LC12

**Files:**
- `plugins/docs-workflows/commands/document.md` (~1309)
- `plugins/security-workflows/commands/scan.md`: the *False positive* paragraph (~329), the move check's instruction (~381) and the report template (~490)
- `plugins/security-workflows/docs/` pages that describe the false-positive evidence display, if any

**Decisions:**

**LC21: report heading.** `## keyed Documentation Report` becomes `## Documentation Report`.

**LC12: the false positive's evidence line.**
- Showing the evidence line becomes its own sub-bullet, *Show the evidence line*, after the check.
- The quoted line, as code, and the finding's own `file:line` go into the text of the question that follows. Where no question follows, they go into the reply's text. Never only into a command's output or the run's thinking.
- The move check is printed verbatim. Its "after each pull into it, or each replay that brings `origin`'s records in" is reproduced, never shortened.

**Steps:**
- [ ] **Step 1:** Make both edits and sweep. Delete LC12 and LC21 from `to-fix.md`. Run the task gates.
- [ ] **Step 2:** Commit: `fix(docs-workflows, security-workflows): report heading; the false positive's evidence line shown in the question (LC12, LC21)`.

### Task 7: Release bookkeeping, tracking records and the full gate chain (controller)

**Files:**
- `plugin.json` and the `.claude-plugin/marketplace.json` entry of each plugin:

  | Plugin | From | To |
  |---|---|---|
  | workflows-core | 1.75.0 | 1.76.0 |
  | product-workflows | 3.72.0 | 3.73.0 |
  | dev-workflows | 4.57.2 | 4.58.0 |
  | docs-workflows | 1.31.1 | 1.31.2 |
  | security-workflows | 0.10.1 | 0.10.2 |

- Each of those plugins' `CHANGELOG.md`, with a section dated `2026-11-03`. product-workflows' section names LC17's extension to `/create-prd`, `/update-prd` and `/create-ard`.
- `.claude/rules/plugin-updates-coupling.md`: one bullet, written in both directions as the file requires (`:12`).
  - product-workflows 3.73.0 and dev-workflows 4.58.0 need workflows-core 1.76.0, for the asking set, `read_default_by_ref`, and `scope: rules` with `draft_path`.
  - workflows-core 1.76.0 beside older product or dev text contradicts that text's "stays open whatever the answer", and offers no read-by-ref answer.
- `docs/superpowers/to-fix.md`: remove the § *From the live checks of 2026-10-29* heading if it is empty, and check that nothing cites a deleted item.
- `docs/superpowers/to-test-on-real-project.md`: add `## Live-check fixes LC12–LC28, D39 — <the five versions>`.
  - One live check, with setup and expectation, for each behaviour change: LC12, LC13, LC14/D39, LC15, LC16, LC17, LC18, LC19, LC22, LC23, LC24, LC25, LC27 and LC28.
  - LC20, LC21 and LC26 change wording only, so each gets a one-line item.
  - Fold in Review Focus items 3–5.

**Steps:**
- [ ] **Step 1:** Make the bumps, write the CHANGELOGs and add the coupling bullet.
- [ ] **Step 2:** Update the tracking records.
- [ ] **Step 3:** Run the full gate chain: every `run:` step of `.github/workflows/validate-catalog.yml` as one `&&` chain, plus `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`. The printed `EXIT=` must be 0.
- [ ] **Step 4:** Commit: `release: live-check round 2 fixes (workflows-core 1.76.0, product-workflows 3.73.0, dev-workflows 4.58.0, docs-workflows 1.31.2, security-workflows 0.10.2)`.

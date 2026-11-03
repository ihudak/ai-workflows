# Live-check round 2 fixes (LC12–LC28, D39) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix every defect the 2026-10-29 live-check round filed (to-fix LC12–LC28) and D39, so the next live round can verify them alongside the to-test items still open.

**Architecture:** This is a fix batch over five plugins. The shared machinery changes first in `workflows-core`: the review-decision rule, the code scanner's read-at-ref mode, the Rule-only overlap read, and the two scripts. The commands that consume it follow, per plugin. One closing task does the release bookkeeping. All changes are to command, agent and reference prose, plus two Python scripts with self-tests.

**Tech Stack:** Markdown command, agent and reference files executed by agents. Python 3 scripts (`lineage.py`, `session-branch.py`, `run-state.py`) with `--selftest`. The repository's gate chain.

**Spec:** `docs/superpowers/to-fix.md` § *From the live checks of 2026-10-29* (LC12–LC28) and § *Design-level* D39. The evidence is `docs/superpowers/verification/2026-10-29-live-checks.md`. The user's rulings, 2026-11-03:
- Fix all of them in one batch.
- **LC17:** `/specify` and `/design` ask each decision-needing finding, with the reviewer's options plus *Leave it open*.
- **LC19:** `/epics` recommends reading the default branch's tip by ref without moving the checkout.

## Global Constraints

- **Process.** Follow `docs/superpowers/reviews/2026-10-26-fix-batches.md` § *How to run a batch*, steps 2 to 8.
- **Rules first.** Read the area's `.claude/rules/` file with the Read tool, by opening a file in the area, before editing there.
- **Re-locate by quoted text.** Find each defect by its quoted text; to-fix's line numbers are at `533037e0`.
- **`CLAUDE.md` § Editing discipline binds every edit.**
  - Run the claim-expiry sweep with all eight refinements of `.claude/rules/claim-sweep.md`, including refinement 7's before-and-after count of each changed literal string.
  - Apply the sentence-context checks: the extent face (enumerate every case a widened trigger now reaches) and the pointer face.
  - `workflows-core:instruction-file-maintenance` binds edits to `references/*.md`.
- **Generated files.** Never edit `plugins/workflows-core/reference-parts/` by hand. After editing `escalation-rules.md`, `phase-handoff.md`, `specs-repo-git.md` or `session-hygiene.md`, run `python3 scripts/reference-parts.py generate`.
- **Questions.** Every `choices:` array has 2 to 4 options and no "Other". The `(Recommended)` marker sits only on a recommended option. Each question's own text carries what the person needs to answer it; nothing points at "above".
- **Docs pages.** Every behaviour change updates its docs page under `plugins/<plugin>/docs/`. Each claim there is derived from the command or agent text, never from memory.
- **Forbidden names.** No tracker vendor names without a marker. Never the organisation the plugins were extracted from. No corporate email domain.
- **No bookkeeping in task commits.** Tasks 1 to 6 do not bump versions or touch any `CHANGELOG.md`, `marketplace.json`, `to-fix.md` or `to-test-on-real-project.md`; Task 7 owns all of those.
- **Commits.** Verify the branch before each commit: `git branch --show-current` must print `fix/live-checks-r2`. The worktree is `/workspace/.worktrees/lc-r2-fix`. Each commit message ends with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Gates.** Each task runs `./scripts/check-docs.sh --root .`, `./scripts/check-id-grammar.sh --root .`, `python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions`, and its scripts' `--selftest`. All must pass before the commit. Task 7 runs the full chain.

## Review Focus

1. **LC28, a session branch that does not exist.** A no-op flush on a specs repository with no `session/<identity>` creates nothing and prints `committed: null, created: false`. A later `lift`, `put-back` or `commit` on that repository still works. Task 1 adds this self-test.
2. **LC24, mixed flag forms.** A `capture` call that gives several paths after one `--from-disk`, then repeats `--from-disk` with one more path, records every path once. Task 1 adds this self-test.
3. **LC19, unknown default branch.** Where the session repository's default branch is unknown (`origin/HEAD` unset), there is no ref to read. The read-by-ref option is not offered, and the question's text says why. Task 4 pins this.
4. **LC22, mixed index sets.** A run that wrote one index identical to `<default-ref>`'s and one that differs, or one absent there, still asks the handoff question. Only a run whose every written index is byte-identical to `<default-ref>`'s skips it. Task 3 pins this.
5. **LC16, tracked files.** A test run that modifies a tracked file, rather than creating a path, is caught by the before-and-after read just like a new path, since both show in `git status --porcelain`. Task 5 pins this.

---

### Task 1: `workflows-core` scripts — LC24 and LC28

**Files:**
- Modify: `plugins/workflows-core/scripts/lineage.py` (the `capture` sub-parser, about lines 1259–1263; its `selftest`)
- Modify: `plugins/workflows-core/references/document-lineage.md` §5 step 1 (about line 76)
- Modify: `plugins/workflows-core/scripts/session-branch.py` (`commit`, about line 843; its `selftest`)
- Modify: `plugins/workflows-core/references/specs-repo-git.md` §8.2 step 1 (about line 1314) and the sentence after the steps that describes `created`

**Decisions:**
- **LC24.** `--from-ref` and `--from-disk` take `action="extend", nargs="+"`, so both forms work: several paths after one flag, and the flag repeated. Rewrite §5 step 1's syntax as `--from-ref <path> [<path> …] --from-disk <path> [<path> …]` and add one clause: "either flag may also be repeated".
- **LC28.** `commit` computes the would-be base (`git merge-base HEAD <default-ref>`) without creating the ref. It creates `refs/heads/<branch>` only once `paths` is non-empty, immediately before it commits. Where nothing is committed and the branch did not exist, step 3's merges and step 4 are skipped, and the result has `committed: null, created: false`. Rewrite §8.2 step 1 to say the branch is created only where step 2 has something to commit.

- [ ] **Step 1:** Write the failing self-test `capture_several_paths_per_flag`. It builds a specs repository with three files and calls `capture --from-disk a.md b.md --from-disk c.md --from-ref a.md --out <f>`. It asserts exit 0, three `--from-disk` entries and one `--from-ref` entry, each path once.
- [ ] **Step 2:** Run `python3 plugins/workflows-core/scripts/lineage.py --selftest`. Expect a FAIL naming `unrecognized arguments`.
- [ ] **Step 3:** Change both `add_argument` calls, and edit §5 step 1.
- [ ] **Step 4:** Run the self-test again and expect PASS.
- [ ] **Step 5:** Write the failing self-test `noop_commit_creates_no_branch`, in `session-branch.py`'s `selftest` style. On a repository with no session branch and no session-file change, `commit --branch session/zz --default-ref main` prints `committed: null`, `created: false`, and `git rev-parse --verify --quiet refs/heads/session/zz` fails. Then a session-file change and `commit` again print `created: true` and a commit, and `lift` and `put-back` on the branch exit 0.
- [ ] **Step 6:** Run `python3 plugins/workflows-core/scripts/session-branch.py --selftest` and expect a FAIL.
- [ ] **Step 7:** Implement the deferred creation, and check `lift`, `put-back` and any `sync` path against an absent branch. Edit §8.2 step 1 and its output sentence, then run `python3 scripts/reference-parts.py generate`.
- [ ] **Step 8:** Run both self-tests, `reference-parts.py check-parts`, and the Global Constraints gates. Expect all to pass.
- [ ] **Step 9:** Commit: `fix(workflows-core): lineage capture takes several paths per flag; a no-op session flush creates no branch (LC24, LC28)`.

### Task 2: `workflows-core` shared rules for the consumers — LC17, LC19, LC25

**Files:**
- Modify: `plugins/workflows-core/references/escalation-rules.md`:
  - *Findings a review leaves open — the offer to apply them* (about line 526)
  - *A finding left open that needs a decision is recorded in the artifact* (about line 666)
  - *A BLOCK review's other findings — folded into its fix cycle* (about line 722)
- Modify: `plugins/workflows-core/agents/code-scanner.md`: the brief's `refresh:` block (about line 28), Process step 2 (prep), and the return block's `refresh_note` and `scanned_ref` lines
- Modify: `plugins/workflows-core/references/read-only-repos.md`, only where it states that ref reading is for read-only mounts alone
- Modify: `plugins/workflows-core/agents/overlap-reader.md`: its input block, its return, and its frontmatter `description`, which is 627 characters today against the 600-character warning
- Modify: the `workflows-core` docs pages that describe these, if any. Find them with `grep -rln "code-scanner\|overlap-reader\|left open" plugins/workflows-core/docs`.

**Interfaces (produced, consumed by Tasks 4 and 5):**
- **Asking set.** `escalation-rules`' set of commands that put a decision-needing finding to the user becomes `/create-prd`, `/update-prd`, `/create-ard`, `/specify` and `/design`. This applies at the offer after a review whose verdict is not `BLOCK`, and in a `BLOCK`'s *Fold* cycle.
- **One question per finding, one shape:**
  - The question's own text names the finding: its severity, where it is, and the decision it needs.
  - The array carries the reviewer's options for that decision, or, where the reviewer gives none, the answers the run drafts as its grill would. At most three of these are carried, with the recommended one marked where the reviewer or the run recommends one. Where there are more than three, the question's text lists them all.
  - The array's last option is `"Leave it open"`.
  - An answer is applied as an edit, read against what it overlaps.
  - In a *Fold* cycle, the re-review covers the answer. After the last review, the version line names the answer among the edits the verdict predates.
  - *Leave it open* records the finding as *A finding left open … is recorded in the artifact* says: `/specify` writes a `- [ ]` open question; `/design` leaves it in its final report and pull request, as today.
  - Where `/create-prd`, `/update-prd` or `/create-ard` already words an equivalent deferral, align that wording to this shape rather than adding a second one.
- **`code-scanner` read-at-ref mode.** The brief's `refresh:` block gains `read_ref: <ref>`, optional, default unset, e.g. `origin/main`. When it is set:
  - `switch_to_default_branch` and `pull` are ignored.
  - The scanner runs one bounded `git -C "<repo_path>" fetch --quiet origin`, the same way it bounds its other network calls.
  - It reads at `<ref>` by `read-only-repos.md` §2–§4's write-free reading, on a writable clone, never switching or pulling.
  - It returns `read_only: false`, `refreshed: true`, `scanned_ref: <ref>` and `refresh_note: "read <ref> by ref; checkout left on <branch>"`.
  - A `<ref>` that does not resolve after the fetch returns `status: REFRESH_BLOCKED`, with a note naming the ref.
- **`overlap-reader` scope.** The input gains `scope: all | rules`, default `all`. Under `rules` it reads only the inherited `[AD#N]` Rules against the draft and the run's decisions, the confirmed inferences included. It returns the `ad_rules` list, the Rule count and each Rule departure, with no other kind of list.

- [ ] **Step 1:** Edit `escalation-rules.md`'s three sections to the asking set and question shape above. Re-read *Used by* lines 556–561 and 719–720 for the extent face. The sentence "`/design` is not among them" stays true for *recording*, since `/design` writes no open question; keep it and add that `/design` now asks first.
- [ ] **Step 2:** Run the sweep. Count, before and after, `` `/create-prd`, `/update-prd`, `/create-ard`) `` and "every other records it" across refinement 4's scope. Update every copy of the asking set, the docs pages included.
- [ ] **Step 3:** Edit `code-scanner.md` and `read-only-repos.md` for `read_ref`, then sweep "read-only mount" sentences that claim exclusivity, as refinement 3 asks.
- [ ] **Step 4:** Edit `overlap-reader.md` for `scope`, and trim its `description` under 600 characters, keeping what it does, when to use it and what it is not for.
- [ ] **Step 5:** Run `python3 scripts/reference-parts.py generate`, then the Global Constraints gates. Confirm `validate-catalog.py` no longer warns on `overlap-reader`.
- [ ] **Step 6:** Commit: `fix(workflows-core): grill commands ask a review's decisions; code-scanner reads at a ref on a writable clone; overlap-reader's Rule-only scope (LC17, LC19, LC25)`.

### Task 3: `workflows-core` text fixes — LC13, LC20, LC22, LC26

**Files:**
- Modify: `plugins/workflows-core/references/epic-picker.md`, *The picker* and *The cap* (about lines 30–95)
- Modify: `plugins/workflows-core/references/escalation-rules.md`, *Edits after a verdict that is not BLOCK — the unspent re-review* (about line 589), and every caller's noun for `<artifact>`. Find the callers with `grep -rn "Re-review the edited" plugins`.
- Modify: `plugins/workflows-core/commands/frames.md` Phase 3 (about line 332), and `plugins/workflows-core/docs/commands/frames.md`
- Modify: `plugins/workflows-core/references/specs-repo-git.md` §6 (the `Specs repo:` rows, about lines 1199–1253)

**Decisions:**
- **LC13.** The remainder option *Another Epic (you'll be prompted for its key)* is the array's **last** option, after any option the command adds; state this in *The cap*. Each row shows the Epic's **bare key**, never the `EPIC-`-prefixed form: `EPIC-<key>` fails `addressing` §1's grammar, and the remainder asks for a key. Rewrite *The cap*'s example rows to bare keys, e.g. `◐ ACME-77-02 order intake`. Grep the three picker commands (`/specify`, `/design`, `/implement`) for prefixed-form row examples and fix any.
- **LC20.** Keep the template `"Re-review the edited <artifact> once (Recommended)"`. Strip the leading article from every caller's noun (`the Epic drafts` → `Epic drafts`, and so on) and state in the rule that `<artifact>` is a bare noun phrase. Count the callers before and after.
- **LC22.** Phase 3 fires only where at least one written index is absent on `<default-ref>` or differs from its blob there. Test with `git -C "$SPECS_PATH" rev-parse --verify --quiet "<default-ref>:./<path>"` against `git -C "$SPECS_PATH" hash-object "<path>"`, where `<default-ref>` is `phase-handoff` §3.2's. Where every written index matches, offer no handoff and print one line: `No handoff: every index this run wrote is already on <default> as written.` A5b's shape, an index committed only on an unpushed plugin branch, is absent on `<default-ref>`, so it still asks.
- **LC26.** Keep the rows' `(<N> files)`. Add one sentence to §6 before the table: where `<N>` is 1, the line reads `(1 file)`. Grep `scripts/` and `plugins/*/scripts/` for any parser that matches `files)` first. If one exists, report it and stop rather than change it.

- [ ] **Step 1:** Make the four edits, sweeping each by phrase with refinement 7's counts.
- [ ] **Step 2:** Run `python3 scripts/reference-parts.py generate`, then the Global Constraints gates.
- [ ] **Step 3:** Commit: `fix(workflows-core): picker remainder last and bare keys; re-review label article; /frames asks only for an index not on the default branch; "1 file" (LC13, LC20, LC22, LC26)`.

### Task 4: `product-workflows` — LC14 + D39 (`/epics`), LC17, LC18, LC19, LC21, LC23, LC25, LC27

**Files:**
- Modify: `plugins/product-workflows/commands/epics.md`:
  - Phase 2 plan approval (LC18)
  - the repo-refresh variant, about line 333 (LC19)
  - Phase 5's brief for the session repository (LC19)
  - Phase 7.4's agent briefs, about lines 900–925 (LC14, D39)
  - the report heading, about line 1016 (LC21)
  - the *Clarifications* line, about line 1077 (LC27)
- Modify: `plugins/product-workflows/commands/specify.md`:
  - the review-finding offers (LC17)
  - Stage 4's overlap read (LC25)
  - the `### Next step` paragraph, about line 1273 (LC23)
- Modify: `plugins/product-workflows/docs/commands/epics.md` and `plugins/product-workflows/docs/commands/specify.md`, wherever they describe any of the above

**Interfaces consumed:** Task 2's asking set and question shape, `refresh.read_ref`, and `overlap-reader`'s `scope: rules`.

**Decisions:**
- **LC14 + D39 (`/epics` copy).**
  - Replace "project root" with "the PRD folder" in every Phase 7.4 brief, and add: "The session's working directory may be a code repository; never edit anything outside the PRD folder."
  - Before dispatching the agents, snapshot `git -C "$SPECS_PATH" status --porcelain -z -- <prd_dir>` and `git -C "<session top level>" status --porcelain -z`, with `git hash-object` fingerprints of each dirty path in both.
  - After the agents return, report, never declare, any returned path that was dirty or absent before.
  - Report any session-repository path whose status or fingerprint changed.
  - Also D39's last sentence: give `/epics`' §4.0 register check the by-path match that `/ready` and `/conformance` use, so a page named `index.md` is never taken for the frame-set `index.md` row.
- **LC17 (`/specify`).** Apply Task 2's shape at the offer and in the *Fold* cycle. Remove the "`/specify` doesn't settle decisions while applying findings" behaviour, and any sentence saying such findings become open questions without asking. *Leave it open* writes the open question as today.
- **LC18.** The plan-approval question's own text carries the plan: Epic count, each Epic's key, title and one-line scope, the repositories to scan, and the refresh policy. The orchestrator also prints it before the question.
- **LC19.** Where the session repository is on another branch and its default branch is known:
  - The question becomes `choices: ["fetch + pull default branch, but read <session-slug> at origin/<default> by ref — your checkout stays on <branch> (Recommended)", "fetch + pull default branch, but scan <session-slug> on <branch> as it stands", "fetch + pull default branch, <session-slug> included", "no refresh"]`.
  - *fetch only* leaves this variant. The question's text says a typed *fetch only* still applies to every repository.
  - On the recommended answer, Phase 5's brief for the session repository carries `refresh: {read_ref: origin/<default>}`.
  - Where the default branch is unknown, keep today's four options and recommendation, and the question's text says that with no default branch known there is no ref to read.
- **LC21.** `## keyed Epic Drafting Report` becomes `## Epic Drafting Report`.
- **LC23.** On the Epic-designing `/dev-workflows:design <PRD>` offer, which applies to a multi-component PRD with an Epic's spec on `<default>`:
  - It carries **no** `<merge-clause>`.
  - It adds one clause: the Epic's specification predates this PRD-level one, which `/product-workflows:epics <PRD>` folds into the Epics, so a design started now starts from the older Epic specification.
  - The flat-spec offer, *Design across components anyway*, keeps its clause.
- **LC25.** At Stage 4's play-back, dispatch `workflows-core:overlap-reader` with `scope: rules` on the specification as drafted through Stage 4, the confirmed inferences included. Take the line's `[AD#N] Rules` count and its Rule departures from that return; the inline read keeps triggers, imports and failure paths. Each departure is put to the user before the gate, offered only as an ARD deviation, as the whole-specification read does. The whole-specification read stays as it is.
- **LC27.** The line becomes `### Clarifications` / `[Phase 6.1's clarifications — resolved: <n>; deferred (became blockers): <n>] — or "none raised"`, plus, where the review left markers, `The review's markers: see ### Deferred items.`

- [ ] **Step 1:** Make the `epics.md` edits, then sweep: count "project root" in `epics.md` before and after; the after-count should be 0 in the briefs.
- [ ] **Step 2:** Make the `specify.md` edits, then sweep "doesn't settle decisions", "open questions without", and `<merge-clause>` on `/dev-workflows:design` across refinement 4's scope.
- [ ] **Step 3:** Update both docs pages, then run the Global Constraints gates.
- [ ] **Step 4:** Commit: `fix(product-workflows): /epics plan in its question, read-at-ref refresh, PRD-folder briefs, report wording; /specify asks review decisions, Stage 4 Rule read, honest design offer (LC14, LC17–LC19, LC21, LC23, LC25, LC27, D39)`.

### Task 5: `dev-workflows` — LC14 + D39 (`/ready`, `/conformance`), LC15, LC16, LC17

**Files:**
- Modify: `plugins/dev-workflows/commands/ready.md` Phase 5 step 2a (about lines 495–520) and `plugins/dev-workflows/commands/conformance.md` Phase 5.5 (about line 421)
- Modify: `plugins/dev-workflows/commands/design.md`: *Release verification*, and the Phase 4 deploy-surface theme brief (LC15); the review-finding offers (LC17)
- Modify: `plugins/dev-workflows/commands/implement.md` Pre-Phase 3.5 and Phase 3.5's verify step (LC16)
- Modify: `plugins/dev-workflows/references/code-handoff.md` §2.2 (LC16)
- Modify: `plugins/dev-workflows/scripts/run-state.py` (the key list, about line 120, and its `selftest`)
- Modify: the matching docs pages under `plugins/dev-workflows/docs/`

**Interfaces consumed:** Task 2's asking set and question shape.

**Decisions:**
- **LC14 + D39.** Same as Task 4's `/epics` copy: drop "project root" for the folder named (`unit_folder`), snapshot both repositories with fingerprints before the dispatch, report rather than declare, and report session-repository changes.
- **LC15.** The deploy-surface theme brief adds: "every image the release builds, publishes or retags, and every workload in the deploy manifests that pulls any of those images, with the tag it pulls and its pull policy". *Release verification* plays each such workload back as a premise at `file:line`, and the rollout question names each one that a moved tag reaches.
- **LC16.**
  - Read `git status --porcelain -z` and fingerprint each listed path just before and just after each test-baseliner run: the Pre-Phase 3.5 capture and each Phase 3.5 verify run. A path new to the after-read, or whose fingerprint changed, was touched by that test run; this covers tracked files.
  - Ask once per test run, the question's text listing each such path: `choices: ["Leave them out of the commit (Recommended)", "Delete them", "Commit them with the change"]`.
  - *Leave out* records the paths under the run-state key `test_byproducts`, which `code-handoff` §2.2 subtracts from the run set, and which the handoff line names as `left out of the commit: <paths> (written by a test run)`.
  - *Delete* removes only those paths.
  - *Commit* records nothing, so §2.2 takes them as today.
  - Add `test_byproducts` (default `None`) to `run-state.py`'s key list, with a self-test that sets and reads it back.
- **LC17 (`/design`).** Apply Task 2's shape at the offer and in the *Fold* cycle. *Leave it open* leaves the finding in the final report and pull request.

- [ ] **Step 1:** Write the failing self-test `test_byproducts_round_trip` in `run-state.py`, then run `python3 plugins/dev-workflows/scripts/run-state.py --selftest` and expect a FAIL on the unknown key.
- [ ] **Step 2:** Add the key, then run the self-test and expect PASS.
- [ ] **Step 3:** Make the `implement.md` and `code-handoff.md` edits, then sweep `pre_existing_dirty`'s statements of the run set across refinement 4's scope.
- [ ] **Step 4:** Make the `ready.md`, `conformance.md` and `design.md` edits, then sweep "project root" and the asking-set copies.
- [ ] **Step 5:** Update the docs pages, then run the Global Constraints gates.
- [ ] **Step 6:** Commit: `fix(dev-workflows): /implement keeps a test run's files out of its commit; /design's rollout reads every workload an image move reaches and asks review decisions; folder-scoped maintenance briefs (LC14–LC17, D39)`.

### Task 6: `docs-workflows` and `security-workflows` — LC21, LC12

**Files:**
- Modify: `plugins/docs-workflows/commands/document.md`, about line 1309 (LC21)
- Modify: `plugins/security-workflows/commands/scan.md`: Phase 5 step 5's *False positive* paragraph, about line 329; the move check's instruction, about line 381; the report template, about line 490 (LC12)
- Modify: `plugins/security-workflows/docs/` pages that describe the false-positive evidence display, if any

**Decisions:**
- **LC21.** `## keyed Documentation Report` becomes `## Documentation Report`.
- **LC12.** Split showing the evidence line out of the check paragraph into its own sub-bullet: *Show the evidence line.* The quoted line, as code, and the finding's own `file:line` go into the text of the question that follows. Where no question follows, they go into the reply's text, and never only into a command's output or the run's thinking. The printed move check is verbatim. Its "after each pull into it, or each replay that brings `origin`'s records in" is reproduced, never shortened.

- [ ] **Step 1:** Make both edits, sweep, and run the Global Constraints gates.
- [ ] **Step 2:** Commit: `fix(docs-workflows, security-workflows): report heading; the false positive's evidence line shown in the question (LC12, LC21)`.

### Task 7: Release bookkeeping, tracking records and the full gate chain (controller)

**Files:**
- Modify: `plugin.json` and the `.claude-plugin/marketplace.json` entry for each plugin:
  - workflows-core 1.75.0 → 1.76.0
  - product-workflows 3.72.0 → 3.73.0
  - dev-workflows 4.57.2 → 4.58.0
  - docs-workflows 1.31.1 → 1.31.2
  - security-workflows 0.10.1 → 0.10.2
- Modify: each of those plugins' `CHANGELOG.md`, adding a section dated `2026-11-03`
- Modify: `.claude/rules/plugin-updates-coupling.md`. Add one bullet: product-workflows 3.73.0 and dev-workflows 4.58.0 need workflows-core 1.76.0, because of the asking set, `read_ref` and `scope: rules`.
- Modify: `docs/superpowers/to-fix.md`. Delete LC12–LC28 and D39, and the § *From the live checks of 2026-10-29* heading if it is left empty.
- Modify: `docs/superpowers/to-test-on-real-project.md`. Add a section `## Live-check fixes LC12–LC28, D39 — <the five versions>` with one live check per behaviour change: LC12, LC13, LC14/D39, LC15, LC16, LC17, LC18, LC19, LC22, LC23, LC24, LC25, LC27, LC28. Each item gets a setup and what to expect. LC20, LC21 and LC26 are wording changes, and their item is one line seen in any run.

- [ ] **Step 1:** Make the bumps, CHANGELOGs and coupling bullet.
- [ ] **Step 2:** Update the tracking records.
- [ ] **Step 3:** Run the full gate chain: every `run:` step of `.github/workflows/validate-catalog.yml` as one `&&` chain, plus `ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root .`. Read the printed `EXIT=`, which must be 0.
- [ ] **Step 4:** Commit: `release: live-check round 2 fixes (workflows-core 1.76.0, product-workflows 3.73.0, dev-workflows 4.58.0, docs-workflows 1.31.2, security-workflows 0.10.2)`.

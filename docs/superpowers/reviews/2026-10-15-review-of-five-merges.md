# Review of five merges — 2026-10-15

Scope: everything `main` gained from `e4491695` to `7c13ce05` — 25 commits, five merges, 95 files, +1267/−577:

| Merge | Topic | Releases |
|---|---|---|
| `d3a609f4` (+ `c5f17766`) | review-1013: `/epics` size gate, `/conformance` routing, *Ground now* clones, `/brd-reconcile` review order, `/release-notes` decline cost | workflows-core 1.39.2, dev-workflows 4.24.3, product-workflows 3.33.3, docs-workflows 1.15.1 |
| `159bb596` | class-wording: epic-picker's second set, commit-artifacts-last for every run | workflows-core 1.39.3 |
| `e32a891b` | prompt-text: REPOS_PATH asked only where nothing resolves; a selection carries no text; check 12's promised-text part | workflows-core 1.40.0, dev-workflows 4.25.0, product-workflows 3.34.0, docs-workflows 1.16.0 |
| `a3f2ff08` | conformance-merged: `/conformance` traces merged code only; `withdraws:` | dev-workflows 4.26.0, workflows-core 1.40.1, product-workflows 3.34.1 |
| `7c13ce05` | stale-resume: `require-on-main` row B′ | workflows-core 1.41.0, dev-workflows 4.27.0, product-workflows 3.34.2 |

Method: six read-only reviewers, one per merge or slice of one (`e32a891b` split three ways: the gate and `escalation-rules`, the dev/docs prose, the product prose), each told to verify a finding against the tree at `7c13ce05` and state its failure scenario. Every MAJOR below was re-read against the cited lines before it was recorded. The gate chain (`validate-catalog.yml`'s steps, `ASSERT_PUBLISHED=1`) passed on `7c13ce05`, and versions agreed across `plugin.json`, `marketplace.json`, the changelogs and `.claude/rules/plugin-updates.md`.

Line numbers are at `7c13ce05`.

## Verdict

Six MAJOR, about two dozen MINOR, no BLOCKER. Fixed on `iv-gu/review-1015`: five of the six MAJORs and the MINORs that are a label, a docs-page line or a self-test case. **Deferred:** every `/conformance` finding, because another agent is reworking `/conformance` so an Epic run traces unmerged branches, which changes the ground most of them stand on — re-review them against that work when it lands — and the design-level MINORs listed under *Deferred*.

## Fixed

### F1 — MAJOR — row B′ never reached an ARD that merged after the branch was cut

`workflows-core:ard-resolution` step 2 collected candidate ARD files from the working tree only (`ard-resolution.md:27-28`), and `:76` returns `status: none` when none resolves. A `/specify`, `/design` or `/ready` run resuming on its own branch, cut before `/create-ard`'s ARD merged, resolved `none`, never asked `require-on-main`, and skipped ARD conformance silently — the `CLAUDE.md` hard constraint that these commands respect the applicable ARD. workflows-core 1.41.0's changelog line "A document that reached the default branch after the cut, missing from the branch's working tree, stops the same way" was false for the ARD.

**Fix:** step 2 lists each folder on `<default-ref>` as well (`git ls-tree --name-only`); a ref-only candidate goes through the gate, which stops on B′. `/ready`'s B′ finding and its docs page name the added-ARD case.

### F2 — MAJOR — row B′'s merge remedy conflicted outside session-branch mode

Outside session-branch mode the plugin branch carries the run's session files (`specs-repo-git.md` §4.1), so `dev-workflows/resume.md` — which every run rewrites — has changed on both sides by the time B′ fires. The reviewer reproduced `CONFLICT (content): Merge conflict in specifications/PRD-1-x/dev-workflows/resume.md` from `git merge origin/main`; re-running on the unfinished merge then meets row A and every path-limited commit fails (`fatal: cannot do a partial commit during a merge`).

**Fix:** the plain-form stop says to keep both sides of an appended session file and either side of `resume.md`, then commit the merge before re-running; row B′'s paragraph says why.

### F3 — MAJOR — `/brd-reconcile`'s *Correct it* let the operator write the customer's reason

`brd-reconcile.md:912` asked the operator for the corrected row's `chosen` **and its reason**, which froze an operator-typed reason as the customer's `[CD#n]` argumentation — the failure `:1053-1057` of the same file names as the one the mandatory field exists to prevent. This is one of the four pickers through which a customer's authority enters the register.

**Fix:** *Correct it* asks only for the corrected `chosen`; the reason is quoted from the customer's text or is `not stated`, which takes the corrected row to the missing-reason picker exactly as *Confirm* does.

### F4 — MAJOR — check 12 contradicted the rule it gates

`escalation-rules` §0 forbids wording the text as a promise in a label (`I'll say which`, `give the reason`, `— name it`, `(enter the path)`) whatever else the label says; `check-docs.sh:1536` excused any label carrying `(you'll be prompted`, and a green self-test case required `"Correct a field — I'll say which (you'll be prompted)"` — §0's own forbidden example — to pass. Two red cases (a label wrapped across lines, a typographic apostrophe) and the `I'll say` case also matched a second family, so each stayed red with the normalisation it claimed to test removed.

**Fix:** the families split into `ASKS` (a label opening with a verb that asks for the text — Enter/Re-enter/Describe, Edit, Specify, List…manually), which the marker excuses, and `PROMISES` (every other family), which it never does. Measured at `7c13ce05`: 191 marked labels, 52 matching a family, all 52 an `ASKS` family — the split fires on no label in the tree. The green case is red now; each weak case carries a label one family matches and asserts that family by name; mutants removing each normalisation, or moving a family between the lists, each fail exactly their cases. **The change is in the shared body below `FAILURES=0`, so it reaches the internal Claude and Copilot editions only by `cp`** — measure their marked labels first, since a label there like `… — I'll say which (you'll be prompted)` fails after the copy.

### F5 — MAJOR — the three preload hooks still said REPOS_PATH "the command will confirm or ask"

`preload-context.sh` in `dev-workflows` (`:109`), `docs-workflows` (`:79`) and `product-workflows` (`:68`) injected that line ahead of every keyed run whose command now says "resolved, never asked", and labelled a set `REPOS_PATH` "(default …)" too.

**Fix:** the hook prints the variable as set, or the default with no claim of a question.

### Fixed MINORs

- `/release-notes`' *Also ground in the recorded refs' diffs (you'll pick repos)* promised a pick nothing asks for (`release-notes.md:184`) — suffix dropped.
- `/brd-interview`'s *Yes — record a defect and cite it here* (`:1522`) and *Re-base it on a current finding* (`:1731`) need typed text and carried no `(you'll be prompted…)` marker.
- `/brd-split`'s prompted options (`:887`, and *Reject* / *Mark superseded*) promised a prompt the body forbade where nothing is eligible (`:1035`, `:1047-1048`).
- `/epics`' *Let me list the repos manually (you'll be prompted)* (`:307`) was asked only in Phase 4 (`:558`), not at once as §0 requires.
- The B′ forms of `*_REGISTER_NOT_ON_MAIN` in `/create-prd` (`:365`), `/create-ard` (`:296`) and `/specify` (`:342`) said every run of all three commands from the branch stops the same way; B′ applies only to the command whose prefix the branch carries.
- Docs pages: `docs-workflows/docs/commands/document.md:63` (every missing repo gets a gate — not after *Proceed without the repos*), `product-workflows/docs/commands/epics.md:87` (asks for the output directory; derives repos from sibling Epics' PR links), `product-workflows/docs/commands/create-ard.md:49` (the mount gate is skipped after *Ground only the confirmed-mounted set*).

## Deferred — `/conformance`, pending the Epic-on-unmerged-branches rework

Re-review each against the rework before acting on it; several may be moot.

- **C1 — MAJOR — an Epic run can be stuck for good after a keyless squash merge.** The merged test (`conformance.md:95`) needs the recorded commit to be an ancestor of the default branch, or a later default-branch subject carrying `[<key>]`. A squash whose title was edited, or a forge whose default squash subject is not the pull-request title, passes neither; the Epic run then stops `CONFORMANCE_NOT_MERGED` (`:99-100`) with no override, while the PRD run asks (`:104-108`) and the design spec's Risks line (`docs/superpowers/specs/2026-10-12-conformance-design.md:102`) promises both runs ask. The *gone without merging* note (`:101`) also mislabels this case when the branch was deleted.
- **C2 — MINOR — any later commit carrying the key counts as the merge.** `:95`'s date only excludes commits before the block; `implementation-format.md:140` asks people outside the plugin to use the key, so a teammate's `[<key>]` commit, or an earlier pull request merging after a later run, reads the latest block as merged.
- **C3 — MINOR — "asks and scans nothing first" (`:56`) is false**: step 4's `require-on-main` row C offers its switch-and-pull repair, and step 2's `SPECS_PATH` prompt, before step 5's record check. The step order is right; the sentence and the merge title overclaim.
- **C4 — MINOR — *gone without merging* (`:101`) fires on a `pushed: false` block traced from another clone**, telling the operator a pull request closed when none was opened.
- **C5 — MINOR — confirming a Dev fix-code line not yet in the checkout is undefined** (`:257-261`): it can re-queue a duplicate `— confirmed:` line beside the original once the Dev's branch merges.
- **C6 — MINOR — the design spec contradicts the amended D5**: its worked example says "while its pull request is still open (D5)" (`:72`) and "traces the branch tip" (`:75`).
- **C7 — MINOR — "no Epic covers" is never defined** (`conformance.md:241`, `:255-257`, `:415`) though *Fix the code*'s Epic question now turns on it; the command never reads an Epic's `## Covers` or `_coverage.md`.

## Deferred — design-level MINORs

- **D1 — row B still reads a stale copy where both sides changed the path** (`phase-handoff.md:232`): `/design` amended the spec on its branch, a refine merged on the default branch, B passes and reads the copy without it. `git diff --quiet <merge-base> <default-ref> -- ./<path>` exits 1 exactly there.
- **D2 — row B′ prints its merge command under `specs_git: misrooted` and on a read-only mount**, where row C withholds its own write remedy (`phase-handoff.md:221`, `:301`; `specs-repo-git.md:445`).
- **D3 — artifacts other than the ARD that a consumer finds by listing the working tree share F1's class**: a `specification.md` that merged after `/ready`'s own `ready/` branch was cut is reported missing rather than stopping on B′. Measure which consumers list rather than gate before widening.
- **D4 — `/document`: a base named at *Revise plan* does not undo Phase 1's *Proceed without the repos*** (`document.md:320` against `:510`, `:569`), and the plan's `Repos:` line (`:390`) has no PRD-only form.
- **D5 — *Set SPECS_PATH* in `/design` (`:80`), `/ready` (`:98-99`) and `/conformance` (`:38`) carries any typed path** without citing the rule that re-asks until it names an existing directory (`escalation-rules.md:209-211`).
- **D6 — the refresh-policy question is asked after a no-code answer** — `/create-ard` Phase 1 step 4 (`:350`), `/epics` Phase 3.5 (`:538`), `/specify` step 3 before step 4.
- **D7 — a REPOS_PATH answered at `/brd-split`'s *Ground now* does not reach the child `/prd-ground` runs** (`brd-split.md:1469-1472`, `:1715`; `prd-ground.md:522-529`), so each child asks again.
- **D8 — `/epics`' final count can split an Epic after the review** (`epics.md:783`, `:814`) with no re-review offer, against `escalation-rules.md:488-497`.
- **D9 — renaming an origin-less clone loops** between `PRD_GROUND_AMBIGUOUS_PIN` and the path question, or records it twice (`prd-ground.md:699-704`, `:820-837`; `grounding-format.md` §4); 3.33.3 carries no upgrade note.
- **D10 — `/prd-ground` matches the specs and docs repos by bare path** (`prd-ground.md:668-671`), with no `realpath` as `release-notes.md:551` uses.
- **D11 — `epic-writer`'s `kept_whole` sentence** (`epic-writer.md:40`) reads as blocking a component split; "never split it by size" would remove the ambiguity.
- **D12 — check 12's marker-loss blind spot**: with the marker removed, 74 of the 100 distinct marked labels at `7c13ce05` still pass. Cheap additions that fire on nothing there: `\(describe\b`, `^provide\b`, `^name\b`, `^quote\b` (`^add\b` fires on four correct labels).
- **D13 — §0's "never a picker built for text" was applied to one picker**: 41 two-option text-plus-Cancel arrays remain (`escalation-rules.md:187`, `:203`, `epics.md:665` among them). Either say an array with a real alternative is not "built for" the text, or convert them.

## Re-review of the fix commit `cb19fa38`

Two independent reviewers re-read the fix wave after it was merged as `c231cb9f`. They found two MAJORs and eleven MINORs, none a BLOCKER, every one fixed in the follow-up (workflows-core 1.41.2, dev-workflows 4.27.2, product-workflows 3.34.4):

- **MAJOR — `ard-resolution` said a ref-only ARD the gate passes "is not used"**, but row C's repair passes one too and leaves it readable; read literally, F1's silent skip came back. Only row B leaves nothing to read. The new `ls-tree` listing also lacked the `2>/dev/null` every §3.2 primitive carries, for rows H and G.
- **MAJOR — `/brd-reconcile`'s *Correct it* still took operator-typed customer words through `chosen`**: an answer outside the options, written in the marked form the propagation sweep later reads as the customer's verbatim words. Older than the fix, the same class as F3. Both fields are now copied out of the returned review; the reason may come from anywhere in it, not only the quotation the reader returned, and a reason that only restates the answer is refused (`decision-register-format.md` §2).
- Row B′'s conflict advice kept "both sides" of `follow-ups.md`, which `/conformance` ticks in place — a ticked follow-up survived beside its open twin; the three register stop templates still summarised the old remedy and named the re-run twice.
- The `dev-workflows` hook's new line went to `/implement` alone, which reads no `REPOS_PATH`; the line is gone there.
- Check 12's split left the label-opening forms of *name it* and *supply the* in `PROMISES`, so *Name its key (you'll be prompted)* failed — a gate firing only on correct content. Both opening forms are `ASKS` now.
- `/brd-interview`'s new defect question omitted `blocked_on` for a `conditional` entry; its *Re-base* question accepted a superseded finding and could only re-ask where none qualified.
- `/brd-split`'s missing-id notice reached the root walk alone; a mistyped id was undefined.
- `/brd-reconcile`'s docs page still said only a *confirmed* `not stated` candidate takes the missing-reason routes.

Noted by the re-review and deferred with the rest:

- **D14 — after the operator merges the default branch into a plugin branch as row B′ asks, the next `commit-artifacts` does not push that branch**: `push-scope` measures against `origin/<branch>` alone, so the default branch's commits and the merge read as non-session commits. A later deliverable handoff push clears it. Older than this review.

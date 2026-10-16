# To fix — every known unfixed issue

**This file is the one list of known, unfixed issues in this repository and of the work it owes the editions kept elsewhere.** A review records what it found and how each finding was disposed of; whatever it leaves unfixed is listed here, in full, and nowhere else. **Read it before starting work on any edition.** Each item says where it can be done, what is wrong or owed, and where it came from. When an item is fixed, delete it here in the same commit that fixes it; when one turns out not to be a defect, delete it with a line in that commit's message saying why.

The repository's three editions of the family: this public one; an internal Claude edition and a Copilot edition, both reachable only from the maintainer's corporate machine. `CLAUDE.md` § Hard constraints and `.claude/rules/gates.md` § *One body, three editions* hold the parity rules.

Line numbers below are at the commit each item names; re-locate by content before acting, since the files have moved on.

**Coverage, as of 2026-10-15:** everything the 2026-10-15 review and its re-review found and left unfixed, everything its reviewers saw and did not report, and the work owed the other editions. The older records under `docs/superpowers/` — `verification/`, `harvest/NEXT.md`, `brd-route-follow-ups.md` — have not been swept into this list; a sweep that moves a still-open item of theirs here says so in its commit.

## Ports to the other editions — the corporate machine

### E1 — Port `check-docs.sh`'s shared body to the internal Claude and Copilot editions

**Source:** this repository at `main` from `030e0f05` on — commits `cb19fa38` and `d0829c80` changed the body.

Everything from the `FAILURES=0` line down (line 185 at `030e0f05`) is byte-identical in all three editions; only the config block above it and `scripts/fixtures/docs/fixture.env` differ. The two commits changed check 12's promised-text part: the families split into `ASKS` (a label *opening* with a verb that asks for text — Enter/Re-enter/Describe, Edit, Specify a path or command, List…manually, Name it/its, Supply the/a), which the `(you'll be prompted` marker excuses, and `PROMISES` (every other family — `I'll <verb>`, `say which`, `give the reason`, `— name it`, a mid-label `supply the`, `(enter`, …), which it **never** excuses, since `escalation-rules` §0 forbids wording the text as a promise whatever else the label says. The selftest gained cases for both.

1. On a branch of the edition, replace the body: keep the edition's lines above `FAILURES=0`, then append this repository's body — `sed -n '/^FAILURES=0$/,$p' <this-repo>/scripts/check-docs.sh`.
2. Run `./scripts/check-docs.sh --root .`. Where check 12 now reports *"promises text the selection cannot carry … the marker never excuses a promise"*, the label is wrong by §0, not the gate: drop the promise phrase and keep the marker — *Correct a field — I'll say which (you'll be prompted)* becomes *Correct a field (you'll be prompted for which)* — and check that the run asks for the text at once after the array. Where it reports *"asks for text"*, add the marker. Here, 191 marked labels at `7c13ce05` matched no `PROMISES` family; an edition's own labels have not been measured.
3. Prove parity: `cmp <(sed -n '/^FAILURES=0$/,$p' scripts/check-docs.sh) <(sed -n '/^FAILURES=0$/,$p' <this-repo>/scripts/check-docs.sh)` prints nothing.
4. Run the edition's whole gate chain, `--selftest` included. Here `--selftest` prints 334 `ok` lines at `030e0f05`; an edition's count differs only by cases its own config switches off.

### E2 — Port the 2026-10-15 review's plugin fixes to the editions that carry the same text

**Source:** `cb19fa38`, `d0829c80` and `16acc463`; what each fixes and why is in `docs/superpowers/reviews/2026-10-15-review-of-five-merges.md` (F1–F5, the fixed MINORs, and *Re-review of the fix commit*). List the files with `git show --stat <sha>` for each, and read each change with `git show <sha> -- <file>`.

Port a change only where the edition holds the passage it edits. Several sit on features this repository shipped in the five merges reviewed (`e4491695..7c13ce05`) — row B′ of `require-on-main`, the *A selection carries no text* rule and its `(you'll be prompted…)` labels, `/conformance`'s merged-code test — so an edition that has not taken those merges has nothing to port the fix onto: take the merge first, or skip the fix and say so in the edition's record. The groups, by file:

- `workflows-core`: `references/ard-resolution.md` (an ARD only the default branch holds reaches `require-on-main`; only row B leaves it unread), `references/phase-handoff.md` (row B′'s session-file conflict advice).
- `dev-workflows`: `commands/ready.md` and `docs/commands/ready.md` (the added-ARD B′ finding), `hooks/preload-context.sh` and `docs/reference/hooks.md` (no `REPOS_PATH` line for `/implement`).
- `docs-workflows`: `hooks/preload-context.sh`, `commands/release-notes.md`, `docs/commands/document.md`.
- `product-workflows`: `hooks/preload-context.sh`; `commands/brd-reconcile.md` and its docs page (*Correct it* copies `chosen` and the reason out of the review, and the record names every *Correct it* pick); `commands/brd-interview.md`, `commands/brd-split.md`, `commands/epics.md` and its docs page, `commands/create-prd.md`, `commands/create-ard.md` and its docs page, `commands/specify.md`.

Each edition keeps its own versions and changelog. Run its gate chain after. Where an edition carries the text of an item below, its fix is ported the same way once it lands here.

## The merged test — `workflows-core:implementation-format` §5

Found by the 2026-10-15 review against `/conformance`'s own copy of the merged test (line numbers at `7c13ce05`). That copy is gone: the test now lives in `implementation-format` §5, read by every `unit-branch` consumer — `/dev-workflows:implement`, `/dev-workflows:conformance` and `/security-workflows:scan` — and by `/conformance`'s PRD run, so the item below is to be fixed there, never in a consumer.

- **C2 — MINOR — any later commit carrying the key counts as the merge.** The subject leg's date excludes only commits made before the block, and `implementation-format` §3 asks people outside the plugin to use the key, so a teammate's `[<key>]` commit, or an earlier pull request merging after a later run, passes the latest block while its pull request is still open. What follows:
  - **The PRD run** passes the Epic without asking, whether the branch resolves or not: its merged test never reads the branch.
  - **Where the branch is gone,** `unit-branch` reads `merged`, since the merged test alone decides there. `/conformance`'s Epic run then traces a default branch without the work, and the scan stops as on a merged Epic.
  - **Where the branch resolves,** step 2's tip test finds the tip adding work, so `unit-branch` reports `after_merge` true. `/conformance`'s Epic run traces the right branch, but its report says the pull request has merged; and `/implement` does not offer to continue on it.

## Design-level — any machine, after a re-review

Found by the 2026-10-15 review or its re-review (line numbers at `7c13ce05` unless named). The user deferred these with the `/conformance` items, to be re-reviewed together once the `/conformance` rework is on `main`, which it reaches with the `iv-gu/security-workflows-scan` merge. Of those items only C2, in the section above, is still open. None of these needs another machine.

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
- **D12 — check 12's marker-loss blind spot**: with the marker removed, 74 of the 100 distinct marked labels at `7c13ce05` still pass. Cheap additions that fired on nothing there: `\(describe\b`, `^provide\b`, `^quote\b` (`^add\b` fires on four correct labels). Since `d0829c80` the `ASKS` list holds `^name its?` itself. Remeasure before adding, and port the body as E1 says.
- **D13 — §0's "never a picker built for text" was applied to one picker**: 41 two-option text-plus-Cancel arrays remain (`escalation-rules.md:187`, `:203`, `epics.md:665` among them). Either say an array with a real alternative is not "built for" the text, or convert them.
- **D14 — a decision owed: should the plugin push a branch the operator merged into?** Row B′ stops a command resuming on its own specs-repo branch — `design/…`, `spec/…`, `prd/…`, the branch its pull request was opened from — where a document it reads changed on the default branch after that branch was cut, and tells the operator to merge the default branch into it. After that merge, the next run's `commit-artifacts` commits its session files on that branch and does not push it: `push-scope` (`workflows-core:specs-repo-git` §4 step 5) publishes session-file commits alone, and the operator's merge commit — possibly carrying their conflict resolutions — and the default branch's commits behind it are not. The run reports *Committed, not pushed*, and the next deliverable handoff push clears it, so nothing is lost or silent. Two ways to close it:
  - **(a) Say it in the stop, keep the rule.** Row B′'s plain form adds that the merge is pushed by the operator — `git -C "$SPECS_PATH" push origin <branch>`, where the branch is on `origin` — or by the next handoff, and that session commits wait until then. The plugin still never publishes a commit it did not make. **Recommended.**
  - **(b) Widen `push-scope` on a plugin branch** to leave out commits the default ref already holds and to admit a merge whose second parent is on it. That makes the plugin publish a commit the operator authored, against the rule's whole reason (`docs/maintainers/rationale.md#specs-push-scope`), and needs that rule re-argued first.
- **D15 — row B′ fires on a git-ignored copy at a gated path.** Its untracked-copy test, `git ls-files --others --exclude-standard`, does not list an ignored file, so a copy the operator wrote there under a `.gitignore` rule reads as the branch never having changed the path. Nothing in the family writes `.gitignore`, so no run is known to reach it; the review that found it (`7c13ce05`'s, demonstrated in a throwaway repository) left it out on that ground. Fix only with a measured case.
- **D16 — to verify: the non-B′ forms of `*_REGISTER_NOT_ON_MAIN`** in `/create-prd` (`create-prd.md:361` at `25a3373c`), `/create-ard` (`:292`) and `/specify` (`:338`) end "Ignored, every /create-prd, /create-ard and /specify run on this slice from <branch> stops here the same way." `cb19fa38` corrected the B′ forms, where that was false; for the general form a run of another of the three from another command's branch may meet row C, whose switch-and-pull offer it can take, rather than the same stop. Check each row the general form reports (D, E, the C rows) before editing.

## Accepted — known, not to fix

- **Which of the customer's sentences is the reason** a `/brd-reconcile` *Correct it* copies out of the review is a reading no test can make. product-workflows 3.34.5 records every *Correct it* pick in the reconciliation record — the reader's row, the corrected `chosen` and reason, and where in the review each was copied from — so the pick can be checked, as a re-point already is. Nothing further can be done in the command; a reviewer of the record is the check.

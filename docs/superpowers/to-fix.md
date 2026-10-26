# To fix — every known unfixed issue

**This file is the one list of known, unfixed issues in this repository and of the work it owes the editions kept elsewhere.** A review records what it found and how each finding was disposed of; whatever it leaves unfixed is listed here, in full, and nowhere else. **Read it before starting work on any edition.** Each item says where it can be done, what is wrong or owed, and where it came from. When an item is fixed, delete it here in the same commit that fixes it; when one turns out not to be a defect, delete it with a line in that commit's message saying why.

The repository's three editions of the family: this public one; an internal Claude edition and a Copilot edition, both reachable only from the maintainer's corporate machine. `CLAUDE.md` § Hard constraints and `.claude/rules/gates.md` § *One body, three editions* hold the parity rules.

Line numbers below are at the commit each item names; re-locate by content before acting, since the files have moved on.

**Coverage, as of 2026-10-15:** everything the 2026-10-15 review and its re-review found and left unfixed, everything its reviewers saw and did not report, and the work owed the other editions. The older records under `docs/superpowers/` — `verification/`, `harvest/NEXT.md`, `brd-route-follow-ups.md` — have not been swept into this list; a sweep that moves a still-open item of theirs here says so in its commit. E4, L2 and the last two *Accepted* entries were added on 2026-10-24, after lean context D merged (`56a3c842`).

**The whole-tree review of 2026-10-26, at `0e02e28b`, keeps its findings in two files of its own, not here:** `docs/superpowers/reviews/2026-10-26-bugs-review.md` (273 defects — the documentation-quality pass included — each with `path:line`, failure scenario and suggested fix; its *Cross-reference* section gives every item below its status at `0e02e28b` — none fixed, D6 partly — and notes where this file's own text is stale) and `docs/superpowers/reviews/2026-10-26-feature-gaps-review.md` (64 gaps against the designs since 2026-09-22 and in the documentation). Until those are swept in, read them with this file: together they are the list of known unfixed issues. When a fix lands for one of their entries, mark it fixed in the review file in the same commit. The order to fix them in — 34 batches, each placing the items below that its text touches, plus the design tracks and the decisions owed — is `docs/superpowers/reviews/2026-10-26-fix-batches.md`.

## Ports to the other editions — the corporate machine

### E1 — Port `check-docs.sh`'s shared body to the internal Claude and Copilot editions

**Source:** this repository at `main` from `030e0f05` on — commits `cb19fa38` and `d0829c80` changed the body.

Everything from the `FAILURES=0` line down (line 185 at `030e0f05`) is byte-identical in all three editions; only the config block above it and `scripts/fixtures/docs/fixture.env` differ. The two commits changed check 12's promised-text part: the families split into `ASKS` (a label *opening* with a verb that asks for text — Enter/Re-enter/Describe, Edit, Specify a path or command, List…manually, Name it/its, Supply the/a), which the `(you'll be prompted` marker excuses, and `PROMISES` (every other family — `I'll <verb>`, `say which`, `give the reason`, `— name it`, a mid-label `supply the`, `(enter`, …), which it **never** excuses, since `escalation-rules` §0 forbids wording the text as a promise whatever else the label says. The selftest gained cases for both. Later commits changed the body too: E3's, `11a4fa70`, and lean context D's (`56a3c842`; check 16's header census, now "500 of this tree's 643", a comment). The one `cp` of the body carries them all.

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

### E3 — Port check 9's singular count to the internal Claude and Copilot editions

**Source:** branch `iv-gu/security-workflows-scan`, the review round 1 fix of its docs task; `git log -S'command emits' --oneline -- scripts/check-docs.sh` names the commit. It changed the shared body: check 9's commands pattern now ends `slash commands?`, its cost-emitting pattern `(commands emit|command emits) a cost entry`, so a plugin of one command can write "One slash command" and "One command emits a cost entry"; and the selftest gained two rewording-only `expect_pass_after` cases and one `expect_fail` twin. One port carries this and E1 together, since each replaces the whole body.

1. **Re-measure `head -1` on each edition's gated files before porting.** For every plugin README in the edition's `PLUGIN_RELS` and every `docs/reference/session-cost.md`, take the first match of the old pattern and of the new one (`grep -ohEi … | head -1`) and compare them. Where they differ, check 9 would compare a different sentence after the port: fix that file in the edition first. Here they were the same in all six gated READMEs, all five session-cost pages and the fixture.
2. **Port by `cp` of the body, then verify with `cmp`.** Keep the edition's lines above `FAILURES=0`, append this repository's body, `sed -n '/^FAILURES=0$/,$p' <this-repo>/scripts/check-docs.sh`, and prove parity as E1 step 3 does: the `cmp` of the two bodies prints nothing.
3. Run the edition's whole gate chain, `--selftest` included. An edition whose config sets `HAS_COST=0` prints `skip` for the singular cost case.
4. **The internal Claude edition lands by pull request only**: push a branch and open a pull request there; never merge it, and never push its default branch.

### E4 — Port this repository's merges since `7c13ce05` to both editions

**Source:** `git log --first-parent --oneline 7c13ce05..56a3c842`. The editions' last port reached `7c13ce05`, the stale-resume row B′ round (workflows-core 1.41.0, dev-workflows 4.27.0), as the internal Claude edition's 2.107.0 and the Copilot edition's 2.72.0. Classify each merge by the editions' port scope before taking it: bug fixes and generic workflow changes are ported. The BRD-to-PRD route is never ported, and neither is addressing's `key-summary` (in both editions keys come from the editions' tracker): that means `/brd-*`, `/prd-ground`, `grounding-format`, `bundle-packaging`, the coverage ledger and customer review. Ask about a feature that fits neither bucket. Each edition keeps its own versions and changelog. The internal Claude edition lands by pull request only (E3 step 4).

**Decide one question first:** whether the editions take the load-by-part machinery at all, meaning part 1's `reference-parts/`, its rule index and `scripts/reference-parts.py`, and D's `require-on-main` file and `check-questions`. Lean context D's verification record (`docs/superpowers/verification/2026-10-22-lean-context-handoff-part.md` §4) found that splitting references by part has not clearly paid on cost. The quality gains of parts 1 and D came from rule fixes, which port without the machinery.

| Merge | What it carries | Port? |
|---|---|---|
| `c231cb9f`, `030e0f05` | the 2026-10-15 review and its re-review | E2 |
| `25a3373c`, `5b462ebc` | this list; `/brd-reconcile`'s *Correct it* record (product-workflows 3.34.5) | no: this repository's list, and the BRD route |
| `c3cd9d3e` | the `security-workflows` plugin (0.1.0). It also brings `implementation-format` §5's `unit-branch`, which `/implement` and `/conformance` read; `/implement` continuing on an Epic's open branch; `cost-emission`'s `/scan` row; and check 9's singular count (workflows-core 1.42.0, dev-workflows 4.28.0) | ask: a new plugin fits neither bucket. `unit-branch` and the `/conformance` rework onto it are generic and ported with it or alone. Check 9 is E3. |
| `40e6b9ea` | `/implement` codes through `code-writer` subagents on a class-chosen coding model, keeps `run-state.py`'s run-state file, and reviews `MODERATE` work with the Opus gate (workflows-core 1.43.0, dev-workflows 4.29.0) | generic. The sub-project after D restructures exactly this, to one `code-writer` per plan and Epics sized by coupling, so port after that lands rather than twice. |
| `b1f3adba` | verification records | no |
| `0f68a91e` | lean context part 1: the loader reuses a reference already read, four rulebooks load by part, and `scripts/reference-parts.py` gates them (workflows-core 1.44.0, dev-workflows 4.30.0, product-workflows 3.35.0, docs-workflows 1.17.0, security-workflows 0.2.0) | per the question above. The loader's reuse rules (Rulings 68, 69) port either way. |
| `cd015961` | `handoff/test-baseliner.md` drops a preamble it no longer needs (dev-workflows 4.30.1) | yes |
| `11a4fa70` | check 16's header comment | E1's `cp` |
| `56a3c842` | lean context D (workflows-core 1.45.0, dev-workflows 4.31.0, product-workflows 3.36.0, docs-workflows 1.18.0, security-workflows 0.3.0) | split by feature, below |

D, by feature. Its `CHANGELOG.md` sections dated 2026-10-24 list every change with its files; check this split against them before porting, since it names features, not every bullet:
- **Port:**
  - every asking command's **Load the question rules.** step;
  - the loader's one-turn paragraph;
  - `/conformance`'s Epic-scope rule for a both-component ARD rule (8a);
  - `design-reviewer` re-deriving claims about the existing system from the scanned commit, with `/design`'s premise read and `grilling-technique`'s three rules (8d);
  - the rest of 8d: `design-format` §11's post-release checks, `/design` leaving a product-decision spec question open, and its interface fan-out recommendation checked against the ARD;
  - `/implement`'s `specs_merged_branch` run-state key, and its re-triage note for a *Declined to judge* line;
  - the report invariants of `/implement`, `/epics` and `/document` (with `specs-repo-git` §4 step 7, below);
  - `session-hygiene` §1's resume-pointer carry and settle rule, with its `(waiting since …)` marker and *Last completed*'s UTC offset (8f, 8h, 8j);
  - `workitem_key` read only from the folder's field;
  - `next-phase-offer`'s remaining Epics named in landing order;
  - `specs-repo-git` §4 step 7, on what may follow a report printed before the tail;
  - `phase-handoff` §2.6.1's `owner-repo`.
- **Per the question above:** the `require-on-main` entry-point file, `entry-files.md` and `check-questions`.
- **Not ported (BRD route):** 8b's ground-tier and local-path rule, 8e's grounding rules, 8i's `/prd-ground` fixes and `scripts/ledger-evidence.py`, and `bundle-packaging`'s model-id row.
- **With `security-workflows`:** `/scan`'s changes, if the editions take the plugin.

Check `.claude/rules/plugin-updates.md`'s coupling bullets for each version pair the editions take, as their own versions will differ.

## The merged test — `workflows-core:implementation-format` §5

Found by the 2026-10-15 review against `/conformance`'s own copy of the merged test (line numbers at `7c13ce05`). That copy is gone: the test now lives in `implementation-format` §5, read by every `unit-branch` consumer — `/dev-workflows:implement`, `/dev-workflows:conformance` and `/security-workflows:scan` — and by `/conformance`'s PRD run, so the items below are to be fixed there, never in a consumer.

- **C2 — MINOR — any later commit carrying the key counts as the merge.** The subject leg's date excludes only commits made before the block, and `implementation-format` §3 asks people outside the plugin to use the key, so a teammate's `[<key>]` commit, or an earlier pull request merging after a later run, passes the latest block while its pull request is still open. What follows, for the PRD run and each of the three `unit-branch` consumers, against all of which the §5 fix is to be verified:
  - **The PRD run** passes the Epic without asking, whether the branch resolves or not: its merged test never reads the branch.
  - **Where the branch is gone,** `unit-branch` reads `merged`, since the merged test alone decides there. `/conformance`'s Epic run then traces a default branch without the work, and `/security-workflows:scan`'s change scan stops with `SECURITY_EPIC_MERGED`, as on a merged Epic.
  - **Where the branch resolves,** step 2's tip test finds the tip adding work, so `unit-branch` reports `after_merge` true. `/conformance`'s Epic run traces the right branch, but its report says the pull request has merged; and `/implement` does not offer to continue on it. `/security-workflows:scan`'s change scan scans the branch, but tells the Dev that its pull request has merged and the branch has gone on since — Phase 1's `after_merge` line, carried into Phase 3's confirmation — and its `### Next step` offers no review and merge of the pull request ("none under `after_merge`") and sends a fix to "the pull request that run opens", all while the Epic's pull request is still open.
- **C9 — MINOR — the PRD run's parity with `unit-branch`: it does not take the third leg.** Found by the second review of the `/conformance` rework (`4069aa29`). `unit-branch`'s step 2 reads a squash merge whose subject lost `[<key>]` as `merged` where the branch survives and its tip adds nothing to `<ref>`. `/conformance`'s PRD run runs the merged test alone, which cannot see that merge. So an Epic its Epic run traced as merged by that leg is "not shown merged" to the PRD run, which recommends *Stop until it is merged* — an answer nothing can lift, since the merge has happened — and only *Trace anyway* goes on; its label says such an Epic's requirements "may show as missing where it has not merged". The fix is parity, in §5: the merged test itself gains the third leg, so the PRD run, which reads that test, sees the merge `unit-branch` sees.

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

- **D17 — `next-phase-offer`'s `pa` lane offers `/dev-workflows:design <EPIC>` after an Epic-level `/create-ard` unconditionally** (`plugins/workflows-core/references/next-phase-offer.md`, the *PA — architecture (optional)* lane: "`/create-ard <EPIC>` (Epic-level) → `/specify <EPIC>` (recommended) or Dev → `/dev-workflows:design <EPIC>`"). Since product-workflows 3.37.0 (batch B07) `/create-ard` offers `/design` only where the Epic's `specification.md` is on the default branch, because `/design` stops with `DESIGN_NO_SPEC` without one; the lane and the command now disagree. The command is the more specific and wins at runtime. Fix in `workflows-core` with its next release: state the same condition in the lane and regenerate `reference-parts/next-phase-offer/` (`scripts/reference-parts.py generate`). The `pe` lane has the matching gap: its PRD-level `/specify` line names only `/product-workflows:epics <PRD>`, while `/specify` since 3.37.0 also offers `/dev-workflows:design <PRD>` to design the spec whole, on both routes; add it there in the same release. Found by the Opus reviews of B07.

## From lean context D — any machine

Found while D was built and run (`docs/superpowers/verification/2026-10-22-lean-context-handoff-part.md` §7).

- **L2 — to verify in the next live run that writes a resume pointer:** that runs write and read back what D's `session-hygiene` §1 adds. That is the `(waiting since …)` marker beside a carried command item, *Last completed* with its UTC offset, and the register slug beside each Security Engineer offer. No gate checks these. Only a live run's `resume.md` and the next run's carry show them working.

## Accepted — known, not to fix

- **Which of the customer's sentences is the reason** a `/brd-reconcile` *Correct it* copies out of the review is a reading no test can make. product-workflows 3.34.5 records every *Correct it* pick in the reconciliation record — the reader's row, the corrected `chosen` and reason, and where in the review each was copied from — so the pick can be checked, as a re-point already is. Nothing further can be done in the command; a reviewer of the record is the check.
- **The resume pointer's settle rule errs to carrying where it cannot tell who wrote a record or when.**
  - It also names a few cases that can leave sooner. Both lists are stated by class in `session-hygiene` §1: the stay-longer list, and the sentence beginning *One can leave sooner*.
  - Ruling 39 of lean context D stopped the rule there. Each further round traded one git-dating edge for another, and a squash can always defeat git dating.
  - A case outside those lists is a defect, and goes above.
- **A `/prd-ground` run killed inside `ledger-evidence.py`'s write window can leave a hidden `.coverage-ledger.*.tmp` beside the ledger.** It is never staged, and later preflights list it as a dirty path until someone deletes it (Ruling 37 of lean context D).

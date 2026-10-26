# Feature-gaps review — 0e02e28b (2026-10-26)

**Reviewed state:** `main` at `0e02e28b` (`0e02e28b1b83e362c592dd45cbf287195508b7cb`). **Window:** the designs, plans and verification records under `docs/superpowers/` for the work since 2026-09-22 (the 17 `specs/*-design.md` files from `2026-09-22-claude-md-split` to `2026-10-22-lean-context-handoff-part`, with their `plans/` and `verification/` records), the older follow-up lists `brd-route-follow-ups.md`, `harvest/NEXT.md` and `harvest/INDEX.md` for items still open in the reviewed areas, and the missing-capability entries in the field feedback from the `bookstore-specs` runs. **Companion file:** `2026-10-26-bugs-review.md`, which also cross-references `docs/superpowers/to-fix.md`.

## What counts as a gap here

A goal, requirement or promised follow-up that a design, plan or verification record states and the tree at `0e02e28b` does not carry, in whole or in part — unless it was later dropped or superseded on the record (a ruling, a later spec, a changelog entry), in which case it is not listed. Each entry says whether it is still worth doing. Entries from field feedback (`FBA-G*`, and the `FBB-*` entries titled *Gap:*, which keep the severity their reviewer gave) are capabilities an operator had to improvise in a live run.

## Summary

64 gaps. The ones that matter most:

- **Planned sub-projects that never started.** Lean context "part 3" — turning the `specs-repo-git` preflight/commit and `emit-cost` procedures into scripts, named "the lever" by both lean-context specs and D's cost record (GIT-G1). The post-D `/implement` restructure — one `code-writer` per plan, Epics sized by coupling — that `to-fix.md` E4 waits on, with no spec or plan (IMP-G1; since resolved by dev-workflows 4.32.0, piece review). `/conformance` Plan 2, the *Delivery verified* stage and the documentation readers of `_conformance.md` (DEV-G1, DEV-G2). docs-workflows' Spec 2 (`/docs-write`, `/docs-capture`, `/docs-verify`) and Spec 3 (`/docs-drift`) (DOC-D-G1, DOC-D-G2) — Spec 2's absence is also the cause of the MAJOR bug DOC-C-B1. security-workflows' sub-projects B–E (SEC-G1, SEC-G2).
- **Promised verification never recorded:** no verification record for security-workflows' sub-project A (SEC-G3) or for implement-coding-subagents, whose cost target was missed (IMP-G2); the Epic size limit's live calibration (PRD-G2); live runs of the docs increment-2 commands, the `/vuln` baseline symmetry and blind grounding verification (DOC-D-G4, VU-G2, BRD-G2, BRD-G3).
- **Documentation:** a plugin and its docs that no user can find their way into — `prose-style`, a declared dependency of two plugins, has no `docs/` tree (DQW-G1); the BRD route has no ordered walkthrough (DQP-G1); getting-started stops before `/implement` (DQD-G1); no glossary, no *what it offers next* sections, no security feedback page (DQP-G3, DQP-G4, DQD-G2). These came from the documentation-quality pass added after `cf139b47`.
- **Deferred design items:** `implementation-format` §4's wider key boundary (CORE-G2), the `untrusted-content` split (SCR-G2), Fable escalation (IMP-G3), install-time-code safety for Poetry, uv, PDM, Hatch, Composer and Bundler (VU-G1).

## Index

| ID | Area | Title |
|---|---|---|
| SEC-G1 | security-workflows | Sub-project E, the architecture feedback loop, never started |
| SEC-G2 | security-workflows | Sub-projects B, C and D (threat models and security conformance) not started |
| SEC-G3 | security-workflows | No verification record for sub-project A |
| SEC-G4 | security-workflows | False-positive evidence is never compared with the finding's own location |
| SEC-G5 | security-workflows | A patch verified on review alone reaches `/implement` with no caveat |
| SEC-G6 | security-workflows | The run's scratch directory and worktree ignore the harness scratchpad |
| SEC-G7 | security-workflows | "linked to the fix commit" is not recorded |
| GIT-G1 | workflows-core — git, handoff, resume pointer | Lean context "part 3": the `specs-repo-git` procedures turned into a script — deferred and never landed |
| GIT-G2 | workflows-core — git, handoff, resume pointer | The generated `require-on-main` file does not carry its line count (worse-cost M3's optional extra) |
| CORE-G2 | workflows-core — routing, cost, feedback, loader, family commands, instruction tiers | `implementation-format` §4's widened key boundary (a squash commit naming the branch) was deferred as "its own change to make" and never made |
| SCR-G2 | scripts, gates and hooks | `untrusted-content` split, deferred "for later" by part 1, never taken up |
| IMP-G1 | dev-workflows — /implement | The post-D `/implement` restructure ("one `code-writer` per plan, Epics sized by coupling") has no design, plan or code — resolved by 4.32.0 |
| IMP-G2 | dev-workflows — /implement | implement-coding-subagents' *Success* cost bar was never met, and no verification record closes it |
| IMP-G3 | dev-workflows — /implement | Sub-project F part 2, Fable escalation, deferred and never picked up |
| IMP-G4 | dev-workflows — /implement | No gate checks that every `code-writer` / `review-fixer` dispatch in `implement.md` names a model |
| IMP-G5 | dev-workflows — /implement | Resuming a crashed run from the run-state file (explicitly a possible later feature) |
| DEV-G1 | dev-workflows — /design, /ready, /conformance | `/conformance` Plan 2, part 1: the optional *Delivery verified* stage in `workflow-states` and `/ready` was never built |
| DEV-G2 | dev-workflows — /design, /ready, /conformance | `/conformance` Plan 2, part 2: the documentation readers never take a recorded decision (D18) |
| VU-G1 | dev-workflows — /vuln, /upgrade | Poetry, uv, PDM, Hatch, Composer and Bundler still install with their install-time code |
| VU-G2 | dev-workflows — /vuln, /upgrade | The `/vuln` baseline-symmetry change has never been run live |
| VU-G3 | dev-workflows — /vuln, /upgrade | `/upgrade` cannot be tied to a unit (no address token) |
| PRD-G2 | product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals | the live calibration of the Epic size limit was never recorded |
| PRD2-SPEC-G1 | product-workflows — /create-prd, /create-ard, /specify, proposals (second pass) | `spec-reviewer` is given no contract input, so the multi-component rule that a crossing criterion names its `[AD#N]` is unreviewed |
| BRD-G1 | product-workflows — BRD route | `/brd-interview` has no carry-forward for a `needs-a-human` item that `/brd-reconcile`'s sweep raises (follow-up E-8, still open, not in to-fix.md) |
| BRD-G2 | product-workflows — BRD route | Blind-verification live checks the verifier-blind record deferred, never re-run |
| BRD-G3 | product-workflows — BRD route | BRD-figures case rows the 2026-09-22 record left unverified on the shipping tree |
| DOC-D-G1 | docs-workflows and the smaller plugins | Spec 2, the iteration engine (`/docs-write`, `/docs-capture`, `/docs-verify`), never shipped |
| DOC-D-G2 | docs-workflows and the smaller plugins | Spec 3, `/docs-drift`, never shipped |
| DOC-D-G4 | docs-workflows and the smaller plugins | the increment-2 commands' behaviour has still never been executed |
| DOC-D-G5 | docs-workflows and the smaller plugins | `/release-notes` drops the PRD's starting-state fact, and no record tracks it |
| FBA-G1 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | prose-style baseline flags British spelling and spaced dashes in a British-English specs tree with no overlay |
| FBA-G2 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/epics` review and fixer briefs still "paste" large prior outputs instead of passing a file path |
| FBA-G3 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | No check of an ARD's landing order against its own contract rows |
| FBA-G4 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/epics` has no step for a cross-component call missing from the ARD's Contracts table |
| FBA-G5 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | The `code-scanner` brief asks for no dependency-coupling list for `/specify` and `/design` |
| FBA-G6 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | No guidance or helper for renumbering ACs/TCs in a large specification |
| FBA-G7 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | The design pre-lint has no advisory for an unscoped `kubectl` operational command |
| FBA-G8 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `/brd-split`'s uniform-answer offer never fires with two or more slices, even where the instruction placed every row |
| FBA-G9 | field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs | `slices.md` has no defined layout |
| FBB-B7 | field feedback — BOOK-2-01 runs | Gap: `/create-prd` has no rule for a customer decision taken outside the register, or one already carried out |
| FBB-B10 | field feedback — BOOK-2-01 runs | Gap: no check that a decision is attributed to whoever made it in proposal prose |
| FBB-B11 | field feedback — BOOK-2-01 runs | Gap: the defect sweep does not quote conflicts with out-of-scope items or decided records |
| FBB-B12 | field feedback — BOOK-2-01 runs | Gap: nothing requires success measures to be traced in a proposal |
| FBB-B14 | field feedback — BOOK-2-01 runs | Gap: `specification-format` does not name three recurring shapes |
| FBB-B16 | field feedback — BOOK-2-01 runs | Gap: no shipped tooling for mechanical spec edits and checks |
| FBB-B21 | field feedback — BOOK-2-01 runs | Gap: `/epics` cannot apply MINOR or NIT findings a review leaves open |
| FBB-B23 | field feedback — BOOK-2-01 runs | Gap: `/design` does not prompt for framework auto-configuration defaults |
| FBB-B25 | field feedback — BOOK-2-01 runs | Gap: `design-format`'s rollback-ratio rule ignores who else feeds the denominator and the mixed-client window |
| FBB-B26 | field feedback — BOOK-2-01 runs | Gap: `/conformance` does not group discrepancies that share a cause |
| FBB-B30 | field feedback — BOOK-2-01 runs | Gap: after a push refused for permissions, the handoff offers no next step |
| FBB-B31 | field feedback — BOOK-2-01 runs | Gap: `/implement` has no rule for a large test set (parallel `test-writer` dispatches) |
| FBB-B33 | field feedback — BOOK-2-01 runs | Gap: no route for a review survivor whose fix lies in a specs-repository document |
| FBB-B35 | field feedback — BOOK-2-01 runs | Gap: tests that do not compile reach the Opus review |
| FBB-B37 | field feedback — BOOK-2-01 runs | Gap: verbatim design markup is not checked against the target's CSS framework |
| FBB-B40 | field feedback — BOOK-2-01 runs | Gap: `grounding/baselines.md` has no canonical entry layout |
| FBB-B44 | field feedback — BOOK-2-01 runs | Gap: no command closes `unsourced` defects that a verified finding settles |
| DQD-G1 | documentation quality — dev-workflows and security-workflows | Getting started stops at `/design`; nothing takes a new user through a first `/implement` or tells them what it needs |
| DQD-G2 | documentation quality — dev-workflows and security-workflows | security-workflows has no page for the feedback, follow-up and resume-pointer files its command writes, which every sibling with a pipeline command documents |
| DQP-G1 | documentation quality — product-workflows | No walkthrough for a first BRD-route run |
| DQP-G2 | documentation quality — product-workflows | Conformance design D22 is only partly reflected in `product-workflows/docs/workflow.md` |
| DQP-G3 | documentation quality — product-workflows | No glossary; route vocabulary is used before it is defined |
| DQP-G4 | documentation quality — product-workflows | Command pages lack a "What it offers next" section (only `/brd-reconcile` has one) |
| DQP-G5 | documentation quality — product-workflows | Getting started has no "Where to run it" or untrusted-input note, though this plugin reads more customer-supplied content than its siblings |
| DQW-G1 | documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki | The small plugins that a family plugin depends on have no `docs/` tree |

# Gaps, by area

## security-workflows

### SEC-G1 — Sub-project E, the architecture feedback loop, never started
- **Designed in:** `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md` § The roadmap (row **E**: "`architecture-grounder` reads the registers … returns a `known-weakness` challenge to `/create-ard`, `/specify` and `/design` … A weakness class that recurs among accepted risks becomes a follow-up for the PA … `promotion-scout` flags weakness classes that recur across teams' registers"); plan `docs/superpowers/plans/2026-10-15-security-workflows-scan.md` Task 13 Step 3 names it as one of the "two follow-ups [that] come next".
- **Current state:** No spec or plan for it under `docs/superpowers/specs|plans` (only the A spec mentions "known-weakness"); `architecture-grounder` and `promotion-scout` do not read `security/<repo-slug>/register.json`. The register was put in `workflows-core` (D2) to prepare for it.
- **Still worth doing?:** yes — it is what turns accepted risks into decisions; the register already holds the data.
- **Suggested scope:** its own spec, per the roadmap's three parts.

### SEC-G2 — Sub-projects B, C and D (threat models and security conformance) not started
- **Designed in:** same spec § The roadmap (rows B "ARD threat model", C "Design threat review", D "Security conformance"); CHANGELOG 0.1.0 *Not built yet* says the same.
- **Current state:** nothing shipped; no specs.
- **Still worth doing?:** yes, as roadmap items (each needs its own spec; D depends on B or C).
- **Suggested scope:** B first, per the dependency column.

### SEC-G3 — No verification record for sub-project A
- **Designed in:** spec § Verification ("An end-to-end run on the bookstore demo … covering the key, path, `--import`, `--triage` and `--verify-fixes` routes … two scans recorded from two clones before either pushed"; "A clean install … must bring in both"); plan Task 12 Steps 4–5; `CLAUDE.md` § Editing discipline ("A sub-project's verification record is written last").
- **Current state:** `docs/superpowers/verification/` holds no security-workflows record. The demo's register was removed from `bookstore-specs` (commit `955d968`, "Remove the security-workflows end-to-end demo's register and notes"), so what Task 12 established — notably route 7 (two clones racing, the give-way/collision path that SEC-B1 lives on) and the clean install — is recorded nowhere. The feedback entries show routes 2, 4 and 6 ran.
- **Still worth doing?:** yes — the renumbering race is the hardest part of `register.py` and is evidenced only by selftests.
- **Suggested scope:** write the record from the Task 12 session's notes; where route 7 or the clean install was not run, run them.

### SEC-G4 — False-positive evidence is never compared with the finding's own location — **Done in security-workflows 0.4.0 (batch B04)**
- **Designed in:** user feedback `NOKEY-scan-fp-evidence-path-not-matched-to-finding` (`/home/ihudak/dev/demo/bookstore-specs/dev-workflows-feedback/2026-10-16.md`) and the part of `BOOK-2-01-scan-false-positive-evidence-unchecked` (`…/PRD-BOOK-2-01-verified-ratings/dev-workflows/BOOK-2-01-feedback.md`) asking to show the cited line "beside the finding's own `file:line`".
- **Current state:** `scan.md:326` checks that the cited `<path>:<line>` exists in the evidence commit and shows that line, then records the evidence "as given". It never shows the finding's own `file:line` beside it, nor notes a different file or a distant line. A citation of an unrelated file is accepted silently.
- **Still worth doing?:** yes — it is a mechanical comparison, not the judgement the command deliberately declines ("the run judges nothing").
- **Suggested scope:** in step 5 (and in step 4's unconfirmed-row display), print the finding's `path:line` beside the cited line, and where the path differs or the line is more than `NEAR` (10) lines away, say so in one plain sentence before recording; no new picker needed.

### SEC-G5 — A patch verified on review alone reaches `/implement` with no caveat — **Done in security-workflows 0.4.0 (batch B04)**
- **Designed in:** user feedback `BOOK-2-01-scan-untested-patch-not-in-followup` (`BOOK-2-01-feedback.md`).
- **Current state:** Phase 6 copies `<report dir>/patches/` (with `patches.jsonl`, which carries `untested`) into the scan folder (`scan.md:358`), but `register.py`'s `_followup_line` (register.py:458-466) builds only "starting from `<patch>`", and `/implement`'s read-back (implement.md:247) does not read the patch header's coverage notice. `grep -rn untested plugins/security-workflows` finds nothing.
- **Still worth doing?:** yes, cheap — `/implement` still runs its own tests, but the planner should know the patch was never test-run.
- **Suggested scope:** `register.py commit` reads `scans/<folder>/patches/patches.jsonl` and appends a fixed structured clause (e.g. "— the patch was verified on review only") where the unit's `untested` is true; never text from the file.

### SEC-G6 — The run's scratch directory and worktree ignore the harness scratchpad
- **Designed in:** user feedback `BOOK-2-01-scan-run-dir-tmp-vs-harness-scratchpad` (`BOOK-2-01-feedback.md`).
- **Current state:** `scan.md:96` (`mktemp -d -t security-workflows-run.XXXXXX`) and `:233` (`mktemp -d -t security-workflows.<repo-slug>-<commit7>.XXXXXX`) say nothing about `$TMPDIR` or a session scratchpad; both name templates and the removal guards (`*/security-workflows-run.*`, Phase 0 step 7's last-component prefix) would work unchanged under any parent.
- **Still worth doing?:** low priority — a one-sentence note; the same pattern is family-wide (`dw-impl-*` in `/implement`), so fix it once in a shared place.
- **Suggested scope:** say the `-t` form honours `$TMPDIR`, and that where the session names a scratchpad the call sets `TMPDIR` to it, keeping the templates.

### SEC-G7 — "linked to the fix commit" is not recorded — **Closed in batch B04 by correcting the spec: D10 and the worked example now say the closing scan is linked, which is what the register records**
- **Designed in:** spec D10 ("The fix commit is linked when a covering codebase scan, usually `--verify-fixes`, moves the finding to `fixed`") and § Worked example step 8 ("`[SEC#1]` becomes `fixed`, linked to the fix commit").
- **Current state:** a closure records only `links.fixed_in_scan` (the scan id; register.py:1148-1149, `:1167`), and `register.md`'s *Fixed* table shows "Closed by scan". No fix commit is ever derived or stored. (D7's field list says "the scan that fixed it", so the spec is internally inconsistent.)
- **Still worth doing?:** marginal — the scan's commit bounds the fix; deriving the fix commit would need the `[<key>]` subject search.
- **Suggested scope:** either correct D10 and the worked example to "linked to the scan that closed it", or record the newest `[<key>]` commit touching the file between the sighting and the scan.

## workflows-core — git, handoff, resume pointer

### GIT-G1 — Lean context "part 3": the `specs-repo-git` procedures turned into a script — deferred and never landed
- **Also found as:** CORE-G1, SCR-G1 (merged here)
- **Designed in:** `docs/superpowers/specs/2026-10-22-lean-context-handoff-part-design.md` § Why: "Part 3, which turns procedures into scripts, follows D and is not in it", and "`specs-repo-git` (120k) … **Not split.** … Part 3's script is the way to stop reading it." § Non-goals: "part 3 takes `specs-repo-git` first". Also `verification/2026-10-22-lean-context-handoff-part-worse-cost.md:199` (M4: "Part 3's script is the lever, as planned") and `specs/2026-10-20-lean-context-loader-design.md:47`.
- **Current state:** nothing ships. `specs-repo-git.md` (120,699 characters) is still executed as prose by every one of the 34 writers. `scripts/` holds `session-branch.py` for §8 only. D's record §4 drops lean context's queued part 2 (the `implement.md` split) and names a different next sub-project, but says nothing about part 3, so it is deferred, not dropped.
- **Still worth doing?:** yes. The worse-cost investigation measured the whole Phase-0 read of `specs-repo-git` as "the largest single reference cost, $1.0–1.6 a run". A script would also make edge cases such as GIT-B1 and GIT-B2 self-testable, as `session-branch.py --selftest` does for §8.
- **Suggested scope:** script `branch-merged`, `branch-key`, `push-scope` and §2.1's classifier first. These are pure, testable functions behind many prose call sites. Then decide `specs-preflight` and `commit-artifacts`.

### GIT-G2 — The generated `require-on-main` file does not carry its line count (worse-cost M3's optional extra)
- **Designed in:** `verification/2026-10-22-lean-context-handoff-part-worse-cost.md` M3: "have the generator write the file's line count in the line under its title, so that both ranges go out at once without `wc -l` … low priority".
- **Current state:** `reference-parts/phase-handoff/require-on-main.md:5`'s header names the sections and no line count. The file is 229 lines and 69,819 bytes, over one Read.
- **Still worth doing?:** low (about $0.06 a run by that record's own estimate).
- **Suggested scope:** one line in `scripts/reference-parts.py generate`, plus check-parts' freshness comparison.

## workflows-core — routing, cost, feedback, loader, family commands, instruction tiers

### CORE-G2 — `implementation-format` §4's widened key boundary (a squash commit naming the branch) was deferred as "its own change to make" and never made
- **Designed in:** `docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md` § *Amended during review (rounds 5–6)*: "The anchored key boundary stays, and §4 now says what a wider one would add — a one-parent commit naming a branch, which on a forge that writes the branch into a squash commit (`Merged in <branch> (pull request #N)`) is that branch's whole landed work — and why it is not taken here: it changes the one boundary every reader of `implementation-format` shares, which is its own change to make. Until then the branch-name probe reports such a commit on a repository the scan left at zero matches; elsewhere that work shows nowhere."
- **Current state:** the deferral still stands in the shipped text, `plugins/workflows-core/references/implementation-format.md:214-218`: "…that branch's whole landed work. It is not taken here because it changes the one boundary every reader of this file shares, which is its own change to make; until then the probe below reports such a commit on a repository the scan left at zero matches." No spec, plan or to-fix item takes it up. The residual is real: on a repository where the scan found some other matches, a squash-merged branch whose own commits carry no key is silently missing from `/document` and `/release-notes` (implementation-format.md:220, "What that costs").
- **Still worth doing?:** low to medium. It matters only on forges that write the branch name into the squash subject, for branches whose commits carry no key. It also touches a boundary shared with `unit-branch`, where C2 and C9 are already open. Worth a to-fix entry, so the "until then" has an owner.
- **Suggested scope:** record it in `to-fix.md` next to C2 and C9 (both are `implementation-format` boundary issues). If taken up, it needs its own short design that measures the readers of the boundary first (the CLAUDE.md "measure the population" rule).

## scripts, gates and hooks

### SCR-G2 — `untrusted-content` split, deferred "for later" by part 1, never taken up
- **Designed in:** `docs/superpowers/specs/2026-10-20-lean-context-loader-design.md:46` ("`untrusted-content` (9.5k, 28 command loads, about 4k saved each): check 20 pins it as one file; left for later").
- **Current state:** `plugins/workflows-core/references/untrusted-content.md` is still one 9,589-byte file. No later spec, ruling or changelog picks it up or drops it.
- **Still worth doing?:** marginal. D measured that splitting has not clearly paid, and check 20 pins the block byte for byte, so a split also needs a check-20 change. Record it as dropped or keep it in to-fix.md, so it does not stay an open "later".
- **Suggested scope:** Either an explicit drop in to-fix.md's Accepted section, or a load-by-part declaration whose block part check 20 reads.

## dev-workflows — /implement

### IMP-G1 — The post-D `/implement` restructure ("one `code-writer` per plan, Epics sized by coupling") has no design, plan or code — **Resolved by dev-workflows 4.32.0 (piece review)**: designed on 2026-10-24 (`docs/superpowers/specs/2026-10-24-implement-one-writer-design.md`), part (a) built, measured in a live A/B and shelved, its per-piece and overall review scopes shipped as piece review, and the `/epics` coupling cut and a mandatory `/specify` dropped by the user — `docs/superpowers/verification/2026-10-25-implement-piece-review.md`
- **Also found as:** PRD-G1 (merged here)
- **Designed in:** not designed. The only record is the user's decision of 2026-10-24 08:07Z in `docs/superpowers/verification/2026-10-22-lean-context-handoff-part.md:228` (and its ledger `:252`, rulings `:92`): "after D, brainstorm one sub-project — `/implement` codes through one `code-writer` for the whole plan (two only where `/design` finds loosely coupled parts), and Epics are sized by coupling (the repository and module cut stays; within a component, split only where the parts share no files or data model and each could ship as its own pull request; `size_limit` becomes a warning, not a cut; whether the PRD-level `/specify` becomes mandatory is open) — proven by an A/B on the e2e copies with a blind judge and measured cost." The same record, `:215`, dropped the queued `implement.md` split because of it. `to-fix.md` E4 defers porting `40e6b9ea` until it lands.
- **Current state:** at the review's commit `0e02e28b` — since superseded by the resolution in the heading — no spec under `docs/superpowers/specs/` (latest is `2026-10-22-lean-context-handoff-part-design.md`), no plan, no branch/commit (`git log --all` grep for coupling / per plan / one code-writer finds none). Shipped `/implement` still groups by Ruling 60's five-files/ten-steps bound (`implement.md:767`), and `/epics` still cuts on `size_limit`.
- **Still worth doing?:** yes — it is the user's queued next sub-project and E4's port is blocked on it. The evidence it rests on is recorded: 17 `code-writer` groups duplicating helpers (Ruling 43), route 3's five dispatches for one coupled three-file change (Ruling 60), and IMP-G2's unmet cost bar.
- **Suggested scope:** brainstorm → spec covering (a) one `code-writer` dispatch per approved plan (or per `/design`-declared loosely coupled part), with the compaction risk the spec's *One coding subagent per plan step* decision guarded against re-argued; (b) `/epics` sizing by coupling with `size_limit` as a warning; (c) the open PRD-level `/specify` question; (d) the A/B on the e2e copies with a blind judge and cost measurement as acceptance.

### IMP-G2 — implement-coding-subagents' *Success* cost bar was never met, and no verification record closes it
- **Designed in:** `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md` § Success: "the entry's total no higher than route 3's $15.63 for comparable work … a costlier run there is the anti-goal *a costlier run that is no better*", and "the orchestrator's own transcript with materially fewer cache-read tokens than route 3's whole run, 36.6M".
- **Current state:** the like-for-like route-3 re-run cost **$33.42** (calc $35.31) against $15.63, 184 main turns against 121, median context 446k against 324k (`verification/2026-10-17-implement-coding-subagents-ledger.md:276`); the Epic run cost $93.92 with 114.0M main cache-read (`:229`, marked "not comparable"). The blind A/B judged the new run better (ledger, fix round 2 header), so the anti-goal is arguably avoided, and Ruling 54 attacked one cause (44 run-state-only turns, ~20.8M cache-read). But no re-measurement after Rulings 54–89 is recorded, and there is no `verification/2026-10-17-implement-coding-subagents.md` record — only the ledger and rulings — so the Success section has no stated disposition.
- **Still worth doing?:** yes, as part of IMP-G1's A/B rather than separately.
- **Suggested scope:** measure the current `/implement` on the route-3 copy once, record it against the bar, and either accept the higher cost explicitly (a ruling) or fold the target into IMP-G1.

### IMP-G3 — Sub-project F part 2, Fable escalation, deferred and never picked up
- **Designed in:** `specs/2026-10-17-implement-coding-subagents-design.md` § Non-goals: "**No Fable escalation (part 2 of F).** Deferred. No run so far has shown Opus falling short…"; header: "Part 2, Fable escalation, is deferred".
- **Current state:** absent; only the "never below the session" clause (a Fable session codes on Fable, `classification.md` §4) ships. No later spec revisits it.
- **Still worth doing?:** no for now — the deferral's own ground (no measured Opus shortfall) still holds; keep it listed as deferred.
- **Suggested scope:** revisit only with a measured case.

### IMP-G4 — No gate checks that every `code-writer` / `review-fixer` dispatch in `implement.md` names a model
- **Designed in:** `specs/2026-10-17-implement-coding-subagents-design.md` § Left to the builder: "**Verification beyond the live runs,** such as a scripted check that every dispatch in `implement.md` names a model." § Success: "every coding and fix dispatch with an explicit `model:`".
- **Current state:** no such check in `scripts/check-docs.sh`, `validate-catalog.py` or `reference-parts.py` (grep). The text does name a model at every dispatch today (`implement.md:771`, `:906`, `:936`, `:1000`), and Ruling 74's motivating Sonnet run "dispatched the coding subagent with no `model:`" — a live failure, though of model-following rather than of the text.
- **Still worth doing?:** marginal — it guards the text, not the run, and the run-time failure is addressed by Phase 0's session-model gate. Cheap if added.
- **Suggested scope:** a check that each `→ Agent (subagent_type: "dev-workflows:code-writer"…` and `"dev-workflows:review-fixer"` line carries `model:`.

### IMP-G5 — Resuming a crashed run from the run-state file (explicitly a possible later feature)
- **Designed in:** `specs/2026-10-17-implement-coding-subagents-design.md` § Non-goals: "**No resuming of a crashed or abandoned run** from the run-state file … Using it to resume is a possible later feature, and is out of scope."
- **Current state:** not built: `init` moves any leftover file aside unread (`implement.md:311`).
- **Still worth doing?:** low — listed so the deferral is visible; IMP-G1 may change the state model anyway.
- **Suggested scope:** none now.

## dev-workflows — /design, /ready, /conformance

### DEV-G1 — `/conformance` Plan 2, part 1: the optional *Delivery verified* stage in `workflow-states` and `/ready` was never built
- **Designed in:** `docs/superpowers/specs/2026-10-12-conformance-design.md` D17 ("A new **optional** rung, *Delivery verified*, in `dev-workflows:workflow-states`' PRD ladder, between *Implementation* and *Release Preparation*. `/ready` reaches it where the PRD-level `_conformance.md` is on the default branch, every entry is `final`, and no `fix-code` entry is still unresolved … `/ready` notes *"delivery not verified"*"). Goal 3 says `_conformance.md` is a record "that `/ready` reads for a new optional stage". D19 assigns this to Plan 2, and D21 assigns the `/ready` docs page for it.
- **Current state:** `docs/superpowers/plans/` holds only `2026-10-12-conformance-plan-1.md`, whose line 17 lists this as "Out of scope here (Plan 2)". No Plan 2 exists. `grep -rn "Delivery verified" plugins` returns nothing. `references/workflow-states.md:22` still reads `Implementation → Release Preparation → Post GA`. `commands/ready.md` never reads `_conformance.md` (not in `grep -rl _conformance.md plugins`). No later spec, CHANGELOG entry or ruling drops it.
- **Still worth doing?:** yes. Without it, a PE's settled PRD record has no reader that gates or reports progress, and `/ready` cannot say whether delivery was verified.
- **Suggested scope:** the D17 rung in `workflow-states.md` (optional, skippable), `/ready` Phase 2/3 reading the PRD-level `_conformance.md` on `<default>` with an advisory "delivery not verified" note, the `readiness-reviewer` rubric line, and the `/ready` docs page. Also update the ladder wherever a page draws it (D22).

### DEV-G2 — `/conformance` Plan 2, part 2: the documentation readers never take a recorded decision (D18)
- **Also found as:** DOC-D-G3 (merged here)
- **Designed in:** the same spec, D18: "`doc-planner` records the requirement each claim comes from … In `/document` Phase 5.8 and in `/release-notes`, a claim whose requirement has a decision in a `_conformance.md` under the PRD takes that decision without asking … `source-truth` §7 states the mapping once." Goal 3: "`/document` and `/release-notes` read so they do not ask again". Spec Verification: "`/document BOOK-1` reusing a decision without asking". The worked example, step 5, depends on it.
- **Current state:** not implemented. Neither `docs-workflows` (`/document`, `/release-notes`, `doc-planner`) nor `workflows-core:source-truth` mentions `_conformance.md`; `grep -rl _conformance.md plugins` hits only dev-workflows, core handoff/hygiene/next-phase-offer and product-workflows roles pages. `docs-workflows/docs/workflow.md` has no `/conformance` reader edge (D22 "Readers" line). The PE therefore settles a discrepancy once in `/conformance` and is asked about it again by `/document`'s Phase 5.8.
- **Still worth doing?:** yes. It is the second half of Goal 3, and the spec presents it as the reason the record is durable.
- **Suggested scope:** Plan 2 as D18/D19 define it. Add `doc-planner`'s requirement field, the `source-truth` §7 mapping (`amend-document`/`accept` → `document-as-code`, an unresolved `fix-code` → `skip-and-report`, `final` over `proposed`, how far the default branch has moved past the traced commit), reads in `/document` Phase 5.8 and `/release-notes`, and the docs-workflows docs and diagram. This crosses into the docs-workflows slice.

(Checked and found shipped: the `/design` parts of `2026-10-04-multi-component-epics-design.md` (D19 as amended: the multi-component picker shape and its *Split / Design across components anyway / Cancel* array, the targeted Epic's single-repository scan, Re-split / Add the component first / *Add anyway* recording `Target span`, the design header's `- **Target**:`, `design-reviewer`'s *Target & contract*). Also the dev-workflows parts of `2026-10-02-harvest-round-4-review-pipeline-design.md`: the unverified triage outcome and the § Reporting line in `/vuln` and `/upgrade`, `code-review`'s `### Declined to judge`, standards discovery and the four new dimension-4 checks (also in `classification.md` §6 item 4), `risk-planner`/`test-writer`/`code-review` `### Review focus`, and `/design`'s citation of *Review verdict BLOCK … — commands that fix inline*. No gap was found in either.)

## dev-workflows — /vuln, /upgrade

### VU-G1 — Poetry, uv, PDM, Hatch, Composer and Bundler still install with their install-time code
- **Designed in:** `plugins/dev-workflows/references/install-time-code.md:18` ("Bundler builds native extensions as a matter of course, and Poetry, uv, PDM, Hatch and Composer have their own no-build or no-scripts settings that this file does not yet adopt"); CHANGELOG 4.14.0 ("Bundler, Poetry, uv, PDM, Hatch, Composer … install unchanged"). There is no design spec for install-time code (none in `docs/superpowers/specs/`), so this deferral is the only record.
- **Current state:** `ecosystems.md:184` (`poetry add` / `poetry install`), `:286` (`bundle install`), `:347-368` (`composer require`/`update`/`install`, which run Composer plugins and root scripts), and `build-systems.md:167`/`:245`. None of these stops install-time code. Check 21 holds only npm, pnpm, yarn, pip and pipenv.
- **Still worth doing?:** yes. Composer plugins and scripts and Poetry/uv source builds are the same supply-chain path the 4.14.0 entry calls "the supply-chain path these two commands open themselves". The fix is partly cheap: `composer … --no-scripts --no-plugins`, `uv … --no-build` / `--only-binary :all:`, and Poetry's `installer.no-binary` / `only-binary` configuration.
- **Suggested scope:** rows for uv and Composer first (each has a clear flag), then Poetry. Extend check 21, and update the `Install scripts` paragraph on both docs pages.

### VU-G2 — The `/vuln` baseline-symmetry change has never been run live
- **Designed in:** `docs/superpowers/verification/2026-09-22-vuln-baseline-symmetry.md:29-33` ("The shipping tree has never been executed … the last commit, `fdc73f53`, closes the eight residuals and is **unrun**"; "No live `/vuln` or `/upgrade` run was made against a real repository").
- **Current state:** no later verification record covers `/vuln` or `/upgrade` (`grep -rln "/vuln\|/upgrade" docs/superpowers/verification/` finds no later run of either). The `--allow-install-scripts` rerun path and the berry hooks were measured (CHANGELOG 4.15.2), but not as an end-to-end `/vuln` run. "Open findings: None" in the record is correct only within those stated limits.
- **Still worth doing?:** yes. VU-B1, VU-B2 and VU-B4 would show up on a first live run against a fixture with an API-breaking bump and a stale local `main`.
- **Suggested scope:** one live `/vuln` and one `/upgrade` against the bookstore fixture: a MODERATE bump with a test the bump breaks, a local `main` behind `origin`, and an annotated-tag action pin.

### VU-G3 — `/upgrade` cannot be tied to a unit (no address token)
- **Designed in:** nothing promises it. The prose assumes it (VU-B10), and `implementation-format` §3 says "All three code-changing commands … write a compliant subject" with `[<key>]`.
- **Current state:** `/upgrade` commits never carry `[<key>]`, so `/release-notes` and `/document`'s two-source read (`implementation-format` §4) never find an upgrade made for an Epic.
- **Still worth doing?:** low priority. Either add `ADDRESS:` like `/vuln`, or drop the dead prose (VU-B10's fix). Recorded so that dropping the prose is a deliberate choice.
- **Suggested scope:** decide, then make one of the two edits.

## product-workflows — idea → PRD → ARD → spec → epics, decisions, proposals

### PRD-G2 — the live calibration of the Epic size limit was never recorded
- **Designed in:** `docs/superpowers/specs/2026-10-12-epic-sizing-design.md` §4 (*"Calibration, live: `/epics` on the BOOK-2-01 demo PRD, then its `/conformance` results — discrepancies per Epic against Epic size — to confirm or move the limit"*) and §5 (*"The limit is a guess until calibrated"*).
- **Current state:**
  - The spec has no verification record. `docs/superpowers/verification/` holds none for epic-sizing.
  - No calibration result appears in the CHANGELOG or in to-fix.md. `grep -rni calibrat` over them finds nothing relevant.
  - The limit is still the guessed 5/4 (`epics.md:645`, `docs/commands/epics.md:55`).
- **Still worth doing?:** Partly. G1's redesign would make the count a warning and could supersede the cut, but the warning still needs calibrated numbers.
- **Suggested scope:** Fold the calibration into G1's A/B, or record a ruling that drops it.

## product-workflows — /create-prd, /create-ard, /specify, proposals (second pass)

### PRD2-SPEC-G1 — `spec-reviewer` is given no contract input, so the multi-component rule that a crossing criterion names its `[AD#N]` is unreviewed — **Done in product-workflows 3.38.0 (batch B08)**
- **Designed in:** the multi-component-epics design (D-series, product side), as shipped into `/specify` Phase 5 at `specify.md:886`: *"An acceptance criterion or test case that crosses components names, in its own text, the `[AD#N]` interface it crosses, so `/epics` can split it per side"*. The docs page restates it at `docs/commands/specify.md:62`.
- **Current state:**
  - Phase 6 passes `spec-reviewer` only the path, the maturity and `applicable_ard` (`specify.md:966-970`).
  - `spec-reviewer` has no check for cross-component criteria and receives no `components`/`contracts` (`agents/spec-reviewer.md:16-61`).
  - `ard-reviewer` and `epic-reviewer` each gained a contract check (PRD.md "Checked and clean"); the spec gate did not.
  - `/epics` then splits a criterion that names no `[AD#N]` on guesswork.
- **Still worth doing?:** Yes, but low urgency. It closes the last unreviewed link of the contract chain on a multi-component PRD-level spec.
- **Suggested scope:** Pass `contracts` rows and `components` to `spec-reviewer` on a multi-component PRD-level run. Add a *Contract citation* check: a criterion whose behaviour spans two components names the `[AD#N]` → MAJOR.

## product-workflows — BRD route

### BRD-G1 — `/brd-interview` has no carry-forward for a `needs-a-human` item that `/brd-reconcile`'s sweep raises (follow-up E-8, still open, not in to-fix.md)
- **Designed in:** `docs/superpowers/brd-route-follow-ups.md` § E-8: "`/brd-interview` does not read the reconciliation record … So the operator carries it between runs by reading a report … Whether a report line is a strong enough guarantee that a `conditional` `[CDF#n]` is re-settled before packaging — or whether the trigger should widen to include an entry the last reconciliation flagged."
- **Current state:** Still undecided and unimplemented. `/brd-interview` reads no `reconciliation-<date>.md`: `grep -n "reconciliation-" plugins/product-workflows/commands/brd-interview.md` returns nothing. Its only "what still needs a human" uses are its own (`brd-interview.md:1620`, `:1884`). to-fix.md's coverage line says `brd-route-follow-ups.md` was never swept, and E-8 is not listed there.
- **Still worth doing?:** Yes, at least as a recorded decision. The entry names the risky case: no interview round is planned before packaging, and an item carried only in a report is lost.
- **Suggested scope:** Decide on the within-parent common path, as E-8 asks. Either record "a report line is sufficient" with a sentence in `/brd-package`'s gate, or widen `/brd-interview`'s re-disposition trigger to `[CDF#n]` entries the latest reconciliation record flagged `needs-a-human`. Move the item into to-fix.md either way.

### BRD-G2 — Blind-verification live checks the verifier-blind record deferred, never re-run
- **Designed in:** `docs/superpowers/verification/2026-10-02-verifier-blind-batched.md` §4.1 and §8 (*Known residuals*): "`INPUT_UNBLIND` has not been re-run since 9A"; R21 (a control-forced `contradict` is never disputable) and R22(b) (a dispute settled `unprovable` has notes that state the disagreement only) are "Verified by reading only"; and "A headless Phase 1 compresses its printed lines" (the cost statement went unprinted in four headless runs).
- **Current state:** The design is fully shipped. `INPUT_UNBLIND`, `blind_disputed`, `PRD_GROUND_VERIFY_INCOMPLETE`, the cap of 25 with its five quoting sites, the Phase 1 cost statement (`prd-ground.md:640-644`), the Final report's `Verification:` block (`:2306-2310`) and the rationale section all match the spec. Lean context D's re-runs (8e) exercised the dispute machinery. No record shows a live `INPUT_UNBLIND` refusal, or a control-forced `contradict` left undisputed, on a current tree.
- **Still worth doing?:** Low priority. It is a verification gap, not a missing feature, and the next live `/prd-ground` run could cover it cheaply with one direct derive dispatch carrying an `evidence` field.
- **Suggested scope:** One direct `grounding-verifier` derive dispatch with an answer field, plus one planted control-forced `contradict`. Record both in the next verification record.

### BRD-G3 — BRD-figures case rows the 2026-09-22 record left unverified on the shipping tree
- **Designed in:** `docs/superpowers/verification/2026-09-22-brd-figures-execution-runs.md`, Tier 2 and Tier 3 tables:
  - B1/B2/B2′: "The **re-run** path is the one half of `/brd-intake` no later run took".
  - E1–E5: "nothing E2 reported has been re-executed".
  - C1/C2 (*Only the document's own folder*) and D1/D2 (`BRD_INTAKE_UNREAD_ATTACHMENTS` writes nothing): "not trustworthy as a claim about today's text".
- **Current state:** The record's own §6 closed F1 (F6 runs) and P1 (P5 run). The `/brd-intake` re-run path, the interview/reconcile defect path (E1–E5), and `/brd-intake` Phase 1's other-file answers have no later live run in any record under `docs/superpowers/verification/`. `brd-intake.md` has changed +244 lines since 2026-09-25.
- **Still worth doing?:** Yes, for the `/brd-intake` re-run path: it rewrites an existing ledger whole (`coverage-ledger-format.md:91`), which is where data loss would show.
- **Suggested scope:** One fixture re-intake (B-row), and one `/brd-intake` run taking *Stop and convert them first* and checking that nothing is written.

## docs-workflows and the smaller plugins

### DOC-D-G1 — Spec 2, the iteration engine (`/docs-write`, `/docs-capture`, `/docs-verify`), never shipped
- **Also found as:** DOC-C-G1 (merged here)
- **Designed in:** `docs/superpowers/specs/2026-08-29-docs-workflow-family-design.md` §2 ("Three specs, built in order … **2 — Iteration engine** (contracts only) | `/docs-write`, `/docs-verify` | Pages published, claims confirmed, image slots filled") and §12.1–§12.3 (`/docs-write <unit-id>|--next|--batch <n>`; `/docs-capture` in interactive and folder modes, with the `missing → captured` edge; `/docs-verify` with user and engineering backends, `drafted → verified`, and the "v2 browser driver"). Decisions D3, D4 and D22.
- **Current state:** `plugins/docs-workflows/commands/` holds seven commands and none of the three. The tree says so honestly: `docs/docs-workflow.md:113`, `:155` and `:192` ("*Later: … It is not part of this release.*"); `references/docs-audit/backlog-format.md:102-103` (the `missing→drafted` and `drafted→verified` edges owned by "Spec 2's `/docs-write`" / "`/docs-verify`"); `references/docs-audit/evidence-contract.md:99` ("Nothing in this increment composes a walkthrough"); `references/docs-profiles/frontmatter-guidelines.md:108` (`unit:` "has a reader today and no automated writer"); `references/docs-workflow/scaffold-tree.md:464` (nav regeneration on write). Route steps 4, 5 and 6 are all manual (`docs/workflow.md:66`). The backlog schema's `captured` status is not in the enum. It was deliberately left for "a later spec" (increment-2 record, *What the design itself got wrong*, bullet 4).
- **Still worth doing?:** yes. It is the half of the family that turns the backlog into pages. Today the backlog `/docs-audit` writes is worked entirely by hand, and B1 is one consequence. Nothing records it as dropped: the design was removed for the name scrub, and the shipped references still cite it as the authority.
- **Suggested scope:** start with `/docs-write --next`, the existing `/document` chain behind a backlog front end. It writes `unit:`, `evidence:` and `review_by`, regenerates the nav (fixes B1), and moves `missing → drafted`. Then `/docs-verify` (the user backend renders the frozen walkthrough), then `/docs-capture`. Revive the design from `git show c5ca8a09^:docs/superpowers/specs/2026-08-29-docs-workflow-family-design.md` §8 and §12, scrubbed.

### DOC-D-G2 — Spec 3, `/docs-drift`, never shipped
- **Designed in:** the same design, §12.4 ("For each surface, diff `sources[].ref` → `HEAD` restricted to the surface's evidence paths … marks that surface's units `stale` … `docs-audit-reviewer` at Opus reviews the staleness calls").
- **Current state:** absent. `references/docs-audit/coverage-model.md:93` ("`/docs-drift`, when that command ships"), `references/docs-audit/backlog-format.md:105-106` (the `published→stale` and `stale→drafted` edges are owned by "Spec 3's `/docs-drift`"), and `docs/docs-workflow.md:210` ("*Later: `/docs-drift` is specified …*"). Route step 8 (re-read pages by `review_by`) is the only drift defence, and it is calendar-only.
- **Still worth doing?:** yes, after G1. The design itself says it "is meaningless before pages exist", and pages exist today only by hand.
- **Suggested scope:** as §12.4. `diff-summarizer` over each surface's evidence paths from the backlog's `sources[].ref`; `sources[].ref` advances only after re-verification; `docs-audit-reviewer` gates the staleness calls.

### DOC-D-G4 — the increment-2 commands' behaviour has still never been executed
- **Designed in:** `docs/superpowers/verification/2026-09-22-docs-family-increment-2.md` *What is NOT verified* 1 ("No command body was executed … The first real invocation is the first execution") and 4 ("`/docs-brand` rung 2's new behaviour is specified, not exercised").
- **Current state:** no verification record, review or ledger since then records a run of `/docs-audit`, `/docs-init` with `source_repos[]`, or `/docs-brand` rung 2. `grep -rln 'docs-audit\|docs-init' docs/superpowers/verification docs/superpowers/reviews` finds only records about counts and caller sets. The live runs of lean context part 1 and D covered `/release-notes` and no cold-start command. `plugins/docs-workflows/CHANGELOG.md` mentions no live run of any of the four.
- **Still worth doing?:** yes. These are the family's most prose-heavy commands (`/docs-audit`: thirteen phases, three agents, a schema with edge rules), and B1 is the kind of defect a single end-to-end run of the route would surface.
- **Suggested scope:** one bookstore-demo pass through `docs-workflow.md` steps 1–4 and 7: `/docs-init`, `/docs-serve`, `/docs-audit`, a hand-written unit, then `/docs-audit --refresh`. Record what fails.

### DOC-D-G5 — `/release-notes` drops the PRD's starting-state fact, and no record tracks it
- **Also found as:** FBB-B8 (merged here)
- **Designed in:** none. It was observed in `docs/superpowers/verification/2026-10-20-lean-context-loader.md:91` ("only its run noticed that all three notes drop the PRD's starting-state fact … the gap is not part 1's") and in the ledger, `2026-10-20-lean-context-loader-ledger.md:357` ("All three miss the PRD's starting-state fact; only B (1.14.3) noticed and filed it").
- **Current state:** the finding was attributed away from part 1 and never filed. It is not in `docs/superpowers/to-fix.md`, and nothing in `release-note-types.md` or `release-notes-writer` was changed for it. The note quality has regressed since docs-workflows 1.14.3 on a known input (demo `BOOK-2-01`).
- **Still worth doing?:** yes, as a filed item at least. What the "starting-state fact" is cannot be recovered from the tree; the blind verdict file under `live/release-notes/blind/` is not checked in.
- **Suggested scope:** recover the verdict, then decide whether `release-note-types` §-rules need a "state before the change" requirement for a Changed or Fixed entry. Add the item to `to-fix.md` either way.
- **Confidence:** low on the cause; high that it is recorded as observed and untracked.

## field feedback — BOOK-1, BOOK-2, BOOK-2-02 runs

### FBA-G1 — prose-style baseline flags British spelling and spaced dashes in a British-English specs tree with no overlay
- **Designed in:** feedback `BOOK-1-epics-style-check-baseline-dialect-noise` in F1 (the `fixed_headings` half of that entry is fixed: `plugins/product-workflows/commands/epics.md:723` adds `## Contract`)
- **Current state:** `plugins/prose-style/references/word-list.md:199-219` says "The baseline is **American English**", with only an *Overlay point*. `/epics` Phase 6.2 (`epics.md:713-740`) passes no dialect and does not skip dialect or dash rules where no overlay exists. On BOOK-1 that produced 19 mostly-noise NITs.
- **Still worth doing?:** yes, cheaply. Every specs tree written in British English gets this noise on every `/epics`, `/create-prd` and `/specify` style pass.
- **Suggested scope:** With no overlay configured, have the callers (or the checker) skip `Prose.WordList.SpellingVariant` and the dash-spacing rule, or infer the variant from the artifact's sources. Say so in the report.
- **Source:** feedback `BOOK-1-epics-style-check-baseline-dialect-noise` in F1

### FBA-G2 — `/epics` review and fixer briefs still "paste" large prior outputs instead of passing a file path
- **Designed in:** feedback `BOOK-1-epics-paste-full-output-slots` in F1
- **Current state:** The writer handoff is already a temp file (`epics.md:645`). The `epic-reviewer` brief still says "`code-scanner output: [paste array of per-repo scanner outputs from Phase 5 …]`" and "`requirements: [paste the requirements[] array from Phase 3]`" (`epics.md:774-775`). The `doc-fixer` briefs say "`[paste the full prose-style-checker output …]`" (`:736`) and "`[paste the triaged survivor list …]`" (`:807`). On BOOK-1 that was about 25 KB of YAML plus 99 rows, which the orchestrator worked around with scratchpad paths.
- **Still worth doing?:** yes. Pasting costs orchestrator context on the most expensive command.
- **Suggested scope:** Let each slot take a `mktemp` path, as the writer handoff does, and name one temp file per intermediate (scanner outputs, requirements, survivors).
- **Source:** feedback `BOOK-1-epics-paste-full-output-slots` in F1

### FBA-G3 — No check of an ARD's landing order against its own contract rows
- **Designed in:** feedback `BOOK-1-epics-landing-order-producer-after-consumers` in F1
- **Current state:** Partly addressed by `2cafd00b` (merge `5a4b1b70`). `epic-writer.md:43-44` allows the one forward dependency "a consumer of a `new` or `changed` interface whose `artifact` is null". Nothing in `/epics`, `ard-resolution`, `components` or `ard-reviewer` tests whether the landing order places a producer after a consumer when the artifact is not null (`grep -i "landing order"` finds no such test). No report or refine pointer is emitted for it.
- **Still worth doing?:** yes, low priority. Where the artifact is not null, epic-writer's "none depends on a later one" and the ARD's landing order cannot both hold.
- **Suggested scope:** In `/epics` Phase 2.5, compare `landing_order` with the producer and consumer of each contract row. Name each inversion in the plan and the final report, with `/product-workflows:create-ard <PRD>` (refine) as the remedy.
- **Source:** feedback `BOOK-1-epics-landing-order-producer-after-consumers` in F1

### FBA-G4 — `/epics` has no step for a cross-component call missing from the ARD's Contracts table
- **Designed in:** feedback `BOOK-1-epics-ard-contract-omission-handling` in F1
- **Current state:** No phase in `epics.md` (Phases 2.5, 5 and 6) lists calls that the code scan shows but `## Contracts` lacks. `epic-writer` and `epic-reviewer` receive no "known omissions". The orchestrator told the writer ad hoc not to invent `[AD#N]` rows.
- **Still worth doing?:** yes. An ARD that omits `exists` rows is common, and the writer is otherwise free to invent rows.
- **Suggested scope:** Add a Phase 2.5/5 step that diffs the scanned cross-component calls against the contract rows, passes the result to the writer and reviewer as `contract_omissions`, and names `/create-ard <PRD>` refine in the report.
- **Source:** feedback `BOOK-1-epics-ard-contract-omission-handling` in F1

### FBA-G5 — The `code-scanner` brief asks for no dependency-coupling list for `/specify` and `/design`
- **Designed in:** feedback `BOOK-1-specify-scan-dependency-coupling` in F1
- **Current state:** `plugins/workflows-core/agents/code-scanner.md` returns capabilities and gaps per theme. `grep -i "coupling\|which other services"` across code-scanner.md, specify.md and design.md finds nothing. `grilling-technique.md:14`'s premise-read rule covers premises in questions, options and rationales, not test-case setups written afterwards.
- **Still worth doing?:** yes, small. A fault-isolation TC (one dependency fails while another succeeds) is invalid wherever the "other" calls the first, and that was found only by hand on BOOK-1.
- **Suggested scope:** Add an optional `dependency_coupling: true` brief field. For each consumed or changed endpoint, the scanner lists the services it calls on reads and on writes, and the grill checks fault-isolation setups against that list.
- **Source:** feedback `BOOK-1-specify-scan-dependency-coupling` in F1

### FBA-G6 — No guidance or helper for renumbering ACs/TCs in a large specification — **Done in product-workflows 3.38.0 (batch B08)**
- **Designed in:** feedback `BOOK-1-specify-large-spec-renumbering` in F1
- **Current state:** `specify.md:956` only "inline-fix[es] the mechanical ones (renumber a duplicate …)". There is no note for a fix cycle that renumbers a whole story in a 60–80 KB spec, and no helper script.
- **Still worth doing?:** marginal. It is a manual workaround with polish impact.
- **Suggested scope:** Add a note in Phases 5/6: rewrite a renumbered story as a whole section, then re-run Phase 5.5's ID checks. Optionally add a `renumber.py` that reports the mapping.
- **Source:** feedback `BOOK-1-specify-large-spec-renumbering` in F1

### FBA-G7 — The design pre-lint has no advisory for an unscoped `kubectl` operational command
- **Designed in:** feedback `BOOK-1-design-prelint-unscoped-kubectl` in F1
- **Current state:** The pre-lint design block (`plugins/workflows-core/references/pre-lint.md:102-112`) checks only headings and the open-question count. `grep -i "kubectl\|namespace\|selector"` finds nothing in pre-lint, `design-reviewer` or `design-format`. The overlap-read rule now covers operational steps (`escalation-rules.md:589-593`, see Dropped), but that rule is judgement, not a grep.
- **Still worth doing?:** yes. It is cheap and the defect class is grep-expressible.
- **Suggested scope:** Add an advisory MAJOR in the design block for `kubectl (rollout restart|delete|scale)` carrying only `-n`, `--namespace` or `--all`, with no resource name and no `-l`.
- **Source:** feedback `BOOK-1-design-prelint-unscoped-kubectl` in F1

### FBA-G8 — `/brd-split`'s uniform-answer offer never fires with two or more slices, even where the instruction placed every row
- **Designed in:** feedback `BOOK-2-brd-split-bulk-offer-skips-instruction-placed-multi-slice` in F2
- **Current state:** `brd-split.md:741` (the `full` row) requires "**exactly one** slice". `:748-750` says: "**With two or more slices standing it does not fire at all**, and that is not a limitation for a later edit to generalise away". So 19 rows that Phase 1.5 placed and Phase 2 confirmed still cost 19 prompts whose answers are already determined.
- **Still worth doing?:** yes, but it is a design decision. The current text refuses it deliberately, and the re-cut row (`:742`, `:758`) shows the "confirmed targets" reasoning the feedback asks for already exists on another path.
- **Suggested scope:** Add a `full`-mode row for two or more slices that fires only where every offered row was placed by Phase 1.5 on a child Phase 2 keyed. Make it one confirmation that lists each row with its own target. Rewrite `:748-750` rather than append to it.
- **Source:** feedback `BOOK-2-brd-split-bulk-offer-skips-instruction-placed-multi-slice` in F2

### FBA-G9 — `slices.md` has no defined layout
- **Designed in:** feedback `BOOK-2-brd-split-slices-md-format-undefined` in F2
- **Current state:** `brd-split.md:1285-1330` lists the blocks the file must carry but sets no frontmatter, headings or order. No reference defines it (`grep -l slices.md` in `references/` finds only passing mentions in `coverage-ledger-format.md:18` and `bundle-packaging.md:164`). `/brd-reconcile` corrects it in place (`brd-reconcile.md:1727`).
- **Still worth doing?:** yes, small. Readers treat it as prose today, so the risk is drift between runs, not a parse failure.
- **Suggested scope:** Add a short `slices-format` section, or a section in `coverage-ledger-format.md`, with frontmatter (`kind: slices`, `key:`), one heading per block type, and their order. Alternatively, state explicitly that the layout is free-form.
- **Source:** feedback `BOOK-2-brd-split-slices-md-format-undefined` in F2

## field feedback — BOOK-2-01 runs

### FBB-B7 — MINOR — Gap: `/create-prd` has no rule for a customer decision taken outside the register, or one already carried out
- **Where:** the contradiction paragraph at `plugins/product-workflows/commands/create-prd.md:640-649`.
- **What is wrong:** It covers only a contradiction the run believes. It does not cover a decision taken in a meeting, or an outcome that has already happened in production.
- **Failure scenario:** The operator reports a reversal from a meeting. The run improvises, and the operator's position shifts three times.
- **Evidence:** `grep -n -i 'meeting\|already happened' create-prd.md` returns nothing.
- **Suggested fix:** Offer stop-and-reconcile, since `/brd-reconcile`'s free-text mode reads meeting notes. Record an outcome that has already happened as a fact the customer must be told, and log only the operator's final position.
- **Source:** feedback `create-prd-contradicted-cd-already-happened` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B10 — MINOR — Gap: no check that a decision is attributed to whoever made it in proposal prose — **Done in product-workflows 3.39.0 (batch B09)**
- **Where:** `plugins/product-workflows/commands/prd-proposal.md` (Phases 7 and 9); `agents/proposal-reviewer.md`.
- **What is wrong:** The rule that `[VD#n]` belongs to the delivery team and `[CD#n]` to the customer is mechanical to check, but nothing checks it. After manual fix notes on a BLOCK, nothing re-checks it either.
- **Failure scenario:** `[ED#9]` credited the customer with a `[VD#6]` decision. It shipped under unreviewed manual fix notes.
- **Evidence:** A grep for an attribution check in both files returns nothing.
- **Suggested fix:** Add a check to Phase 7 or pre-lint, and re-run it over manual fix notes.
- **Source:** feedback `prd-proposal-attribution-unchecked-before-review` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B11 — NIT — Gap: the defect sweep does not quote conflicts with out-of-scope items or decided records — **Done in product-workflows 3.39.0 (batch B09)**
- **Where:** `plugins/product-workflows/commands/prd-proposal.md` Phase 4 step 3.
- **What is wrong:** A source-2 or source-3 candidate is put to the operator with no check against the PRD's out-of-scope list or the `[VD#n]`/`[CD#n]` records.
- **Failure scenario:** The operator confirmed `[SR#6]` as mandatory scope against `[VD#5]`, then reversed it.
- **Evidence:** `grep -n -i 'out-of-scope\|out of scope' prd-proposal.md` returns nothing.
- **Suggested fix:** Quote any conflict in the confirmation question.
- **Source:** feedback `prd-proposal-source3-conflict-not-surfaced` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B12 — NIT — Gap: nothing requires success measures to be traced in a proposal — **Done in product-workflows 3.39.0 (batch B09)**
- **Where:** `plugins/product-workflows/references/proposal-format.md` §4 section 21; `agents/proposal-reviewer.md`.
- **What is wrong:** Nothing requires every live `[SM#n]`/`[SMC#n]` to trace to a `[WP#n]` or an exclusion.
- **Evidence:** A grep for `SM#n|SMC#` in both files returns nothing.
- **Suggested fix:** Add a format rule and a reviewer check.
- **Source:** feedback `prd-proposal-success-metrics-untraced` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B14 — MINOR — Gap: `specification-format` does not name three recurring shapes — **Done in product-workflows 3.38.0 (batch B08)**
- **Where:** `plugins/product-workflows/references/specification-format.md:106`, `:123` (test-case expected result); `:62` (the paired-state rule covers only state-changing behaviour).
- **What is wrong:** (a) A test may assert something its criterion does not state. (b) The spec does not require a single-fault exact-message criterion to be scoped "with no other fault", or the check order to be stated. (c) Loading and empty states need not say how a bounded wait ends them, and a control's state (disabled or hidden) need not state its inverse.
- **Failure scenario:** BLOCKERs and re-review findings repeat on the BOOK-2-01-01 and -02 specs.
- **Evidence:** A grep of `specification-format.md` for `no other fault|precedence|bounded wait|criterion lacks` returns nothing.
- **Suggested fix:** Add the three lines the feedback proposes.
- **Source:** feedback `specify-tc-assertion-absent-from-ac`, `specify-fault-precedence-unspecified`, `specify-sibling-states-and-inverse-unstated` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B16 — NIT — Gap: no shipped tooling for mechanical spec edits and checks
- **Where:** `plugins/product-workflows/scripts/` (holds `architecture-harvest.py`, `bounded.py`, `ledger-evidence.py`, `promotion-signals.py`, `proposal-record.py`; there is no spec tool).
- **What is wrong:** Every large `/specify` run rewrites ad-hoc Python for inserting test cases, exact-match replacements, and structural checks.
- **Suggested fix:** Ship a `spec-tool.py` with `insert-tcs`, `replace` and `check`, and call it from `/specify`. This overlaps B13's deterministic checks.
- **Source:** feedback `specify-scratch-scripts-for-tc-and-fixes` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B21 — MINOR — Gap: `/epics` cannot apply MINOR or NIT findings a review leaves open
- **Where:** `plugins/workflows-core/references/escalation-rules.md:515-518` (the apply offer is "Used by" `/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`, `/prd-proposal`, `/brd-proposal` and `/implement`, but not `/epics`); `plugins/product-workflows/commands/epics.md:800-813` (`doc-fixer` gets MAJOR only; "MINOR / NIT findings are deferred").
- **What is wrong:** A contradictory criterion that the fixer itself introduced shipped open in the pull request.
- **Evidence:** I read both files.
- **Suggested fix:** Give `/epics` the offer, applied through `doc-fixer` with every severity in one bounded pass.
- **Source:** feedback `epics-no-offer-to-apply-open-findings` in `BOOK-2-01-feedback.md`
- **Confidence:** high

### FBB-B23 — MINOR — Gap: `/design` does not prompt for framework auto-configuration defaults
- **Where:** `plugins/dev-workflows/commands/design.md` Phase 4 (the scanner brief) and Phase 5 (the gap scan). A grep for `open-in-view|auto-configuration|framework default` in `design.md`, `design-format.md` and `design-reviewer.md` returns nothing.
- **What is wrong:** Decisions resting on transaction and connection scope were false under Spring's default `open-in-view=true`. Only the Opus review caught it, at the cost of a fix cycle.
- **Suggested fix:** Where the stack auto-configures, list the defaults that bear on the decisions, each marked kept or overridden.
- **Source:** feedback `design-framework-defaults-unprompted` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B25 — NIT — Gap: `design-format`'s rollback-ratio rule ignores who else feeds the denominator and the mixed-client window
- **Where:** `plugins/dev-workflows/references/design-format.md:169-187` (Post-release checks, Rollback signal).
- **What is wrong:** Both design-reviewer passes raised a MAJOR in this class.
- **Suggested fix:** Require each ratio to name its numerator and denominator callers, and the window in which old and new clients coexist.
- **Source:** feedback `design-observability-ratio-contamination` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B26 — MINOR — Gap: `/conformance` does not group discrepancies that share a cause
- **Where:** `plugins/dev-workflows/commands/conformance.md:262` ("put one `AskUserQuestion` to the person per item"); `references/conformance-format.md` §3 (no `shared-cause` field).
- **What is wrong:** One root cause restated in six places becomes six walk questions and six `fix-code` follow-ups for a one-line fix.
- **Suggested fix:** Cluster discrepancies by evidence `file:line`, ask once per cluster (still splittable), and keep one entry per requirement plus one follow-up per cluster.
- **Source:** feedback `conformance-shared-cause-grouping` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B30 — NIT — Gap: after a push refused for permissions, the handoff offers no next step
- **Where:** `plugins/workflows-core/references/phase-handoff.md:102-108` (§2.5 Push; it has no permission-denied handling beyond "not handed off").
- **What is wrong:** When the SSH identity can fetch but not push, a local commit is left for the operator to push by hand.
- **Suggested fix:** Name the branch and commit left behind, and offer a consented retry or a push through `gh`'s credentials.
- **Source:** feedback `conformance-push-refused-after-commit` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B31 — MINOR — Gap: `/implement` has no rule for a large test set (parallel `test-writer` dispatches)
- **Where:** `plugins/dev-workflows/commands/implement.md:854` (Phase 3.5 step 1: one `test-writer` dispatch).
- **What is wrong:** With 134 test cases, the orchestrator improvised five parallel writers and wrote the shared test support itself, with no rule to stop two writers sharing a file.
- **Suggested fix:** Above a threshold, write the shared support first, then dispatch N writers that each own disjoint files and test-case ids, and run one verify.
- **Source:** feedback `implement-parallel-test-writers` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B33 — MINOR — Gap: no route for a review survivor whose fix lies in a specs-repository document
- **Where:** `plugins/dev-workflows/commands/implement.md:987` (routes only another code repository's findings) and `:1018` (step 7.5: conformance gaps only).
- **What is wrong:** A MAJOR in `design.md`'s rollback runbook had no rule, so it was handled by judgement.
- **Suggested fix:** Hand it to no fixer, name it in the report and `body_facts`, and emit a Phase 6 follow-up for it.
- **Source:** feedback `implement-specs-doc-finding-unrouted` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B35 — MINOR — Gap: tests that do not compile reach the Opus review
- **Where:** `plugins/dev-workflows/commands/implement.md:872` (type-checks run with lint and build in Phase 3.5 step 3, after the review); `code-writer` and `test-writer` run none.
- **What is wrong:** `test-writer` output that fails `tsc` is reviewed as written. The review then spends findings on compile errors. The design deliberately places every check after the review, so this is a gap, not a contradiction.
- **Suggested fix:** Allow a non-running type-check of test sources before the review diff, stating that it is not a test run, or record why this is refused.
- **Source:** feedback `implement-spec-typecheck-before-review` in `BOOK-2-01-feedback.md`
- **Confidence:** low (the fix is a design decision)

### FBB-B37 — NIT — Gap: verbatim design markup is not checked against the target's CSS framework
- **Where:** `plugins/dev-workflows/commands/implement.md` Phases 3A/3B; `agents/code-writer.md`.
- **What is wrong:** A verbatim template rendered cramped under Bootstrap 5.3, and only the review caught it.
- **Suggested fix:** Check verbatim markup against the target's CSS framework at implementation time, and raise any departure as a decision or an assumption.
- **Source:** feedback `implement-design-markup-vs-css-framework` in `BOOK-2-01-feedback.md`
- **Confidence:** low

### FBB-B40 — MINOR — Gap: `grounding/baselines.md` has no canonical entry layout
- **Where:** `plugins/workflows-core/references/grounding-format.md:491-510` (§4 step 1 names the fields in prose); `plugins/product-workflows/commands/prd-ground.md:895-898`, `:1725`.
- **What is wrong:** The file is parsed by later runs (Phase 3's pin test, Phase 8's supersession, and `/brd-interview:1028`), but its layout (YAML block or table, and the field names) is improvised by each run.
- **Failure scenario:** Two runs write different shapes, and a later reader misparses the pin.
- **Suggested fix:** Fix one serialised layout in §4, as §2.1 does for findings.
- **Source:** feedback `prd-ground-baselines-layout-unspecified` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

### FBB-B44 — NIT — Gap: no command closes `unsourced` defects that a verified finding settles
- **Where:** `plugins/product-workflows/commands/brd-interview.md:878` ("stays `open` until a person resolves it"); `references/brd-format.md:917`.
- **What is wrong:** `[DEF#2]` and `[DEF#15]` stay `open` in the log the customer receives, although `[CG#2]` and `[CG#12]` settle them.
- **Suggested fix:** Offer, with confirmation, to write `resolved-by: <SLICE-KEY>/[CG#n]`, or print the exact line to write by hand.
- **Source:** feedback `brd-interview-unsourced-defects-no-closure` in `BOOK-2-01-feedback.md`
- **Confidence:** medium

## documentation quality — dev-workflows and security-workflows

### DQD-G1 — Getting started stops at `/design`; nothing takes a new user through a first `/implement` or tells them what it needs
- **Designed in:** the brief's reader criterion: "a getting-started page that would not get a new user to a first successful run". `plugins/dev-workflows/README.md:25` advertises the page as "your first `/design` run". The plugin's spine is `/design → /implement`.
- **Current state:** `plugins/dev-workflows/docs/getting-started.md:92-112` ends at "Once that lands, `/implement EPIC-98760` picks up the design and starts the code change". It uses the bare form, two lines after the page explains why the qualified form is needed. Nothing on the page tells the user what `/implement` needs that `/design` did not:
  - a clean working tree in the code repository (Phase 1.4);
  - a session on Opus, or the session-model question it asks first (`commands/implement.md` Phase 0);
  - a test suite `test-baseliner` can detect, or the Pre-Phase 3.5 prompt that asks for one;
  - `gh` and an `origin` for the pull request;
  - one `/implement` run at a time per working tree.

  These facts are spread over a 54k-character command page (`docs/commands/implement.md`). The getting-started page also gives no way to obtain a `specification.md` without `product-workflows`, and no description of what a minimal specs repository holds. The repo-root README covers neither.
- **Still worth doing?:** yes. The plugin's own README promises a first run, and `/implement` is the command most likely to stop a first-time user (dirty tree, Sonnet session, no detected tests).
- **Suggested scope:** add a "Your first `/implement`" subsection to `getting-started.md` (5-8 lines: the qualified command, the five preconditions above as a checklist, and what the run ends with: a committed branch, a push and PR question, `implementation.md`, and the next step `/dev-workflows:conformance`). Add a line pointing to `/product-workflows:specify` or describing the minimum specs-repo layout (`environment.md`'s *Directory layout*).

### DQD-G2 — security-workflows has no page for the feedback, follow-up and resume-pointer files its command writes, which every sibling with a pipeline command documents
- **Designed in:** the parity criterion in BRIEF-DOCS.md. `dev-workflows` and `product-workflows` each ship `reference/session-feedback.md` and `reference/resume-and-checkpoints.md`, and `dev-workflows` ships `reference/follow-ups.md`.
- **Current state:** `/security-workflows:scan` runs feedback, follow-ups, cost and the resume pointer in its tail (`docs/commands/scan.md:63`, `:168`). It takes `--skip-feedback` (`:29`). `docs/commands/scan.md:166` explains at length how the resume pointer carries its Security Engineer offers. The plugin's 8 pages still have no page saying where feedback lands, what `--skip-feedback` keeps, or what `resume.md` is and where it lives. `grep -rn -i 'resume.md\|session feedback' plugins/security-workflows/docs` finds only passing mentions. A user who installs only `security-workflows` plus its dependencies has no `dev-workflows` pages to fall back on.
- **Still worth doing?:** yes, at low cost. A short page, or links to `workflows-core`'s equivalents if that plugin's docs carry them, closes the gap. `.claude/rules/security-workflows.md` fixes the page count at 8, so a new page means updating that count too.
- **Suggested scope:** one `reference/session-feedback.md`, or a *Session bookkeeping* section on `session-cost.md`, covering feedback, the resume pointer and the follow-up file location, each linked from `scan.md`'s *The tail*.

## documentation quality — product-workflows

### DQP-G1 — No walkthrough for a first BRD-route run
- **Designed in:** the docs addendum's bar (*"a getting-started page that would not get a new user to a first successful run"*). No spec covers it.
- **Current state:** `getting-started.md:82` gives one sentence: *"`/brd-intake` in place of `/idea`"*. `brd-workflow.md` has the diagram, a parameter table and long prose, but no ordered list of commands with one key carried through. The list should run intake → merge → `/brd-split <BRD> "<instruction>"` → merge → `/prd-ground <SLICE> --repos …` → merge → `/brd-split <SLICE>` → `/brd-interview` → `/brd-package` → send → `/brd-reconcile`. Nor does any page say what to do before `/prd-ground`: clone the code under `$REPOS_PATH`, export design frames into `design/<set>/`, and run `/workflows-core:frames` to index them (the frame need is mentioned only at `brd-workflow.md:355` and `prd-ground.md:566`).
- **Still worth doing?:** yes. The route has nine runs and several merges, and a first-time PM cannot reconstruct the order from six long pages.
- **Suggested scope:** A "Your first BRD run" section in `getting-started.md` or at the top of `brd-workflow.md`: one key family, one line per command, the merge between steps, and the prerequisites for `/prd-ground`.

### DQP-G2 — Conformance design D22 is only partly reflected in `product-workflows/docs/workflow.md`
- **Designed in:** `docs/superpowers/specs/2026-10-12-conformance-design.md` D22: *"**PE:** `product-workflows/docs/workflow.md`'s two diagrams, as the PE step … (`/conformance <PRD>` after every Epic's `/implement`, feeding `/update-prd`, `/specify`, `/epics` and the docs commands)"*.
- **Current state:** `workflow.md:34`, `:67-70` draw `conformanceprd` feeding `specify`, `epics` and `updatevi`, but not the docs node. The docs edge still leaves from `implement` (`:91`). The second diagram (architecture knowledge base) has no conformance node. That may be deliberate, since it is an architecture diagram.
- **Still worth doing?:** yes, for the docs edge (see DQP-B5). The second-diagram half is probably superseded, because that diagram is not the pipeline.
- **Suggested scope:** One edge `conformanceprd -.-> docsplugin`, and drop `implement -.-> docsplugin`.

### DQP-G3 — No glossary; route vocabulary is used before it is defined
- **Designed in:** the docs addendum (*"jargon used before it is defined"*).
- **Current state:** `README.md:3` and `:12-16` use BRD, PRD, ARD, PM/PA/PE, "slice", "grounding" and "ledger" before any page defines them. BRD is first spelled out at `brd-workflow.md:5`, and PM/PA/PE only in `roles-and-phases.md` headings. Terms such as root, slice, `covered-here`, `allocate-only`, `[G]`/`[V]`/`[C]`, horizon/`will-change`, readiness tier and `<merge-clause>` are defined only inside individual command pages. `grep -i glossary` over the docs finds nothing.
- **Still worth doing?:** yes. Every BRD page assumes the reader already knows these terms.
- **Suggested scope:** A `docs/reference/glossary.md` (about 25 terms, each linked to the page that owns it), linked from the README and the index. Expand BRD/PRD/ARD/PM/PA/PE at first use in the README.

### DQP-G4 — Command pages lack a "What it offers next" section (only `/brd-reconcile` has one)
- **Current state:** Of the 16 pages, only `commands/brd-reconcile.md` has a section for its next step (*"Where the route goes next"*). The others leave it to a *See also* bullet (`idea.md:180`), to prose inside *Gates* or *Example* (`prd-ground.md:580-587`), or say nothing. This is how DQP-B6's missing edges stay invisible.
- **Still worth doing?:** yes. Each command's next-step offer is its most useful fact for a new user.
- **Suggested scope:** A short "Next step" section on each page, listing the offers from that command's next-step phase with their conditions.

### DQP-G5 — Getting started has no "Where to run it" or untrusted-input note, though this plugin reads more customer-supplied content than its siblings
- **Current state:** `dev-workflows/docs/getting-started.md:86-90` and `docs-workflows/docs/getting-started.md:65-69` both have *"Where to run it"*. It recommends a container and says that agents treat repository text as data. `product-workflows` has no such section, yet `/brd-intake` and `/idea` walk and transcribe customer-supplied documents, their links and their images. The only related note is in `reference/agents.md`.
- **Still worth doing?:** yes, as a short parity section.
- **Suggested scope:** Add a "Where to run it" section that matches its siblings, adapted for customer BRDs and community posts.

## documentation quality — docs-workflows, guideline-reviewers, prose-style, acli, obsidian-llm-wiki

### DQW-G1 — The small plugins that a family plugin depends on have no `docs/` tree
- **Designed in:** No design spec covers it. The parity expectation comes from `BRIEF-DOCS.md` and `CLAUDE.md`'s docs-tree hard constraint, which binds only `PLUGIN_RELS`. `prose-style` is a declared dependency of `docs-workflows` and `product-workflows` (`plugins/docs-workflows/.claude-plugin/plugin.json`), and `scripts/check-docs.sh:93-95` already treats it as family for check 20.
- **Current state:** `prose-style`, `acli` and `obsidian-llm-wiki` ship a README only. The prose-style README is about 400 lines and holds the command, agent, overlay and schema documentation that siblings split into `docs/commands/*` and `docs/reference/*`. Its `/prose-style-refresh` `source.yml` schema is reachable only by pointing the reader at the command prompt itself (`README.md:206`).
- **Still worth doing?:** Yes for `prose-style`, which every docs-workflows and product-workflows user installs. Optional for `acli` and `obsidian-llm-wiki`, which are standalone and have their own upstream shape.
- **Suggested scope:** Give `prose-style` a `docs/` tree (index, getting-started with install, update and `PROSE_STYLE_PATH`, three command pages, an overlay reference) and add it to `PLUGIN_RELS`.

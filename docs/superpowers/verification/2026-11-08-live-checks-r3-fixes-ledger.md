# SDD ledger — live-check round 3 fixes (LC29–LC37, R1, K1–K5, K7)

This is the ledger of branch `fix/live-checks-r3`, cut from `main` at `8e110fc1`.
- The plan is `docs/superpowers/plans/2026-11-08-live-checks-r3-fixes.md`.
- The defects it fixes were filed by `docs/superpowers/verification/2026-11-04-live-checks.md` as to-fix items LC29 to LC37, plus R1 and K1–K5 from that round's runs.

The branch was run with `superpowers:subagent-driven-development`. That skill keeps its ledger in a git-ignored scratch directory and deletes the directory when the branch finishes, so the ledger is copied here.
- **Copied as it stood, except for one change:** each subagent's internal id is replaced with `<agent>`.
- **The rulings summary** is in `2026-11-08-live-checks-r3-fixes-rulings.md` beside this file.

---

# SDD ledger — plan: /workspace/.worktrees/lc-r3-fix/docs/superpowers/plans/2026-11-08-live-checks-r3-fixes.md
# SDD ledger — plan: /workspace/.worktrees/lc-r3-fix/docs/superpowers/plans/2026-11-08-live-checks-r3-fixes.md

Spec: docs/superpowers/to-fix.md § From the live checks of 2026-11-04 (LC29–LC37) + docs/superpowers/verification/2026-11-04-live-checks.md; user rulings in the plan's Spec section. Branch fix/live-checks-r3, start f7415b52 (main 8e110fc1 + plan commits).

## Pre-flight scan

| Pair / task | Shared file or interface | Finding |
|---|---|---|
| T1→T2 | tree-snapshot.py snapshot/compare JSON (in_head, clean_before, created) | T2 consumes exactly T1's fields; consistent |
| T2↔T9 | dev-workflows/scripts/run-state.py | T2 adds files.snapshot_before/after (KEYS, KEYS_LINE, selftest); T9 makes append refuse arrays. Sequential; T9 must keep T2's KEYS. No conflict |
| T2↔T9 | implement.md | T2 :756–775 (reads); T9 :379, :493, :1108, :1542. Disjoint |
| T2↔T3↔T9↔T10 | epics.md | T2 7.4c (:915–927); T3 refresh bullet :333–349, brief :636–638, :610, :643, :655, :1068; T9 routing :381, invariant :1244; T10 :784–796, :880, :1129. Disjoint regions, sequential |
| T3↔T5↔T6 | design.md | T3 :151–152, :283–286, :301, :303, report; T5 :315, :344; T6 :529–530. Disjoint |
| T3↔T6↔T7↔T9 | specify.md | T3 :425–433, :875–879, :901; T6 Phase 6 cap; T7 :799, :1282; T9 :481. Disjoint |
| T6↔T10 | escalation-rules.md (+ reference-parts regen) | T6 :515 (version-line part), :627–676 (review part); T10 :749–752. Each regenerates parts; sequential. No conflict |
| T3↔T6 | .claude/rules/workflows-core.md (19,996 chars) | T3 count sentence; T6 overlap-reader map line. Budget rule in Global Constraints binds both |
| T1↔(T3) | CLAUDE.md rules table row (bounded-run) | only T1 edits it |
| T2..T10 | to-test new section | first task to add an item creates the section (heading placeholder `<versions Task 11 sets>`); later tasks append; T11 fills versions |
| T2..T8 | to-fix § From the live checks of 2026-11-04 | each deletes its items; T7 narrows LC31; after T8 only LC31 (narrowed) remains; section intro stays |
| T1 self | creates script + copies + CI + rules | consistent |
| T2 self | sites enumerated by grep at run time; list is expected set | consistent (grep governs) |
| T3 self | reference + 6 callers + counts | consistent; late-join for `known` callers only |
| T4 self | template line + step | consistent |
| T5 self | :344, :315, design-format | consistent |
| T6 self | version-line amend + review-part paragraph + agent + 3 commands + maps | consistent with N1–N3 fixes |
| T7 self | report template + 2.5 + GIT-G1 design + to-fix | consistent |
| T8 self | session-hygiene one sentence | consistent |
| T9 self | R1, K1 (refuse), K4 family-wide, K5 | consistent |
| T10 self | K2 ranking (two places), K3 | consistent |
| T11 self | versions/changelog/coupling/gates | consistent |

Scan clean: no rulings needed before Task 1.

## Model plan
Implementers: T1 sonnet; T2, T3, T6, T9 opus; T4, T5, T7, T8, T10, T11 sonnet. Task reviewers: opus for T2, T3, T6, T9; sonnet for the rest. Final review: opus.

## Progress
Task 1: dispatched (BASE f7415b52, implementer sonnet, agent <agent>)
Task 1: implementer DONE_WITH_CONCERNS (1de2e849): TDD not red-first; rename outside --dir shows as add without wider --path; LC34 deletion left to Task 2 (correct per plan). Review dispatched (sonnet, agent <agent>).
Task 1: review Approved (sonnet). ⚠️ copies byte-equal — verified by cmp (controller).
Task 1: minor (deferred): load() does not validate record shape → KeyError/traceback exit 1 instead of 2 on a malformed snapshot (tree-snapshot.py:303-310)
Task 1: minor (deferred): selftest's hand-rolled os.walk removal named shutil_rm — use shutil.rmtree (:373-379)
Task 1: minor (deferred): vanished-path selftest fingerprints a never-existing path, not the status→fingerprint window (:441)
Task 1: minor (deferred): posixpath.relpath depends on process cwd (:265)
Task 1: note for Task 2: with no --path a rename whose other half is outside --dir shows as a plain add; callers needing the ../ form pass a wider --path
Task 1: complete (commits f7415b52..1de2e849, review clean)
Task 2: dispatched (BASE 1de2e849, implementer opus, agent <agent>)
Task 2: implementer DONE_WITH_CONCERNS (36bf0ce9): Install-them-now read (--untracked-files=no) left hand-written; no exit-2 rule at sites; /vuln Step 3 moved too; CI comment names only dev commands (Task 11).
Task 2: review Needs fixes (opus): Important 1 — "snapshot" names two things in /implement; code-handoff §2.2's new sentence false for Install-them-now's tracked-only read (implement.md:679, :406, code-handoff.md:65; also vuln.md:151 pre_edit_tree). Minors: Phase 4 removal list misses snapshot_before/after (implement.md:1132); no exit-2 rule at sites; K7 to-test expectation wrong mid-run (to-test:40); report templates say "first read"/"reads" not "snapshot" (ready 610, conformance 539, epics 1120, document 1417/1925); docs colon misplaced (dev docs conformance.md:102).
Ruling: Install-them-now's tracked-only read stays hand-written (no tracked-only mode; untracked dependency dirs would cost and misfire) but is renamed so it is not "a snapshot", and §2.2's sentence names exactly the reads it covers — why: removes the contradiction without a new script mode — cost if wrong: one hand-written -z read stays (LC34's class) at one site.
Ruling: the Task 2 minors go into fix round 1 with the Important — why: user's standing rule "fix all known bugs before push" and the implementer holds the context now — cost if wrong: a slightly larger fix diff to re-review.
Task 2: fix round 1/5 (6 addressed, 0 open; new: 1 Important — failed Pre-Phase 3.5 re-read runs Phase 4.6 and commits the user's unrecorded edits (implement.md:406, :1267); 3 Minor — "no path declared" reaches the run's own deliverable in ready/conformance/epics; vuln.md:295 reason false where the branch was never cut; document.md:1571/:2039 and docs document.md:68 invariants not updated; commits 36bf0ce9..7bf16c66)
Task 2: minor (deferred to final wave, Task 1 script): fingerprint() lets OSError escape (tree-snapshot.py:59-66) → exit 1, empty stdout, outside the 0/2 contract
Task 2: out-of-scope taken into round 2: ready.md "snapshot" also names _readiness.md (:22, :141, :511–:534) beside the script read — same class as finding 1; vuln.md:53 "Snapshot repo context" third sense (cosmetic)
Task 2: fix round 2 committed 0fffbd45 (boundary set at the run's first edit, not end of Pre-Phase 3.5 re-read; 'tree read' in all four maintenance commands, /implement keeps 'snapshot'); re-review dispatched (opus, agent <agent>)
Task 2: fix round 2/5 (6 addressed, 0 open; commits 7bf16c66..0fffbd45)
Task 2: minor (deferred): .claude/rules/dev-workflows-tests.md:17 "the one it deliberately leaves out, Pre-Phase 3.5's Cancel" now false (failed pre-edit snapshot also left out)
Task 2: minor (deferred): implement.md:402 Stash bullet's list of non-4.6 stops omits the failed snapshot (:394) and step 1's own capture failure
Task 2: minor (deferred): implement.md:406/:1271 reason "nothing of the run's is in the tree" — a pre-edit check run may have written files; say what that run may have left
Task 2: minor (deferred): implement.md:394 "being the post-branch exits Phase 4.6 excludes" exhaustive claim omits exit 4 pre-edit and continued-branch Phase 1.7/2A/2B Cancels — use "among"
Task 2: minor (deferred): document.md:1571 says "where a read fails twice"; templates :1421/:1927 say "read or comparison" (nit)
Task 2: complete (commits 1de2e849..0fffbd45, review clean after 2 fix rounds)
Task 3: dispatched (BASE 0fffbd45, implementer opus, agent <agent>)
Task 3: implementer DONE_WITH_CONCERNS (96c6ca0c): ard-reviewer working-tree existence check vs by-ref read (false BLOCKER risk); /docs-audit Continue after REFRESH_BLOCKED reads branch (existing meaning); /epics report template keeps §7 text verbatim beside citation; extra edits design-reviewer, /design at-scan tests, epics REFRESH_BLOCKED moved to §6, rules sentence.
Task 3: review Needs fixes (opus): Important 1 — ard-reviewer's working-tree existence check (ard-reviewer.md:27,:32; brief create-ard.md:730–735 passes no commit) raises false "fabricated" BLOCKER after /create-ard's now-recommended by-ref read. Minors: architecture-grounding.md:65 stack_facts and interface-designer.md:62–71 read the working tree; epics.md:333 summary drops "and may be scanned"; five callers cite §7's report wording with no slot (LC31's class); /docs-audit Continue after by-ref REFRESH_BLOCKED reads the branch against its stance (:125).
Ruling: ard-reviewer gets each repository's scanned commit and read mode in its brief, and the three write-free git reads design-reviewer uses (cat-file -e / show / git grep at the commit; Bash added to its tools for those alone); a repository with no commit in the brief is checked in the working tree as before — why: the same contract design-reviewer already has; keeps the existence check strong — cost if wrong: one agent gains Bash (read-only use stated).
Ruling: /docs-audit's REFRESH_BLOCKED question after a by-ref read omits "Continue with current local state", its text saying why (docs-audit.md:125's stance) — why: a coverage denominator must be the shipped default branch — cost if wrong: one fewer way past a blocked refresh (Skip/Cancel remain).
Ruling: Task 3's minors go into fix round 1 (user's fix-all rule).
Task 3: fix round 1 committed 4c4f13f8; re-review dispatched (opus, agent <agent>)
Task 3: fix round 1/5 (5 addressed, 0 open; commits 96c6ca0c..4c4f13f8)
Task 3: minor (deferred): scan-refresh.md §7 last paragraph — "a change to it here changes every slot" false (must be made in every slot); "after its status" no longer matches the four Final-report `Read by ref:` slots
Task 3: minor (deferred): docs-audit.md:~131 Skip/Cancel list — question text must itself say no option is marked and why (escalation-rules.md:184–186); clause reads as a note to the author
Task 3: minor (deferred, pre-existing): create-ard.md:~589–591 BRD route — a claim cited at a baselines.md pinned commit is checked by ard-reviewer at the scanned commit only → could read fabricated; pass the pinned commit for such claims
Task 3: complete (commits 0fffbd45..4c4f13f8, review clean after 1 fix round)
Task 4: dispatched (BASE 4c4f13f8, implementer sonnet, agent <agent>)
Task 4: implementer DONE (8d017933)
Task 4: review Approved (sonnet); ⚠️ to-test section header exists — verified by grep (controller).
Task 4: minor (deferred): scan.md:330 step does not name which [SEC#n] (post-replay) the reply line uses — add "under the [SEC#n] the template names"
Task 4: minor (deferred, pre-existing): scan.md:330 a triage that ends early prints no report — what does the person see of the evidence line?
Task 4: complete (commits 4c4f13f8..8d017933, review clean)
Task 5: dispatched (BASE 8d017933, implementer sonnet, agent <agent>)
Task 5: implementer DONE (99db4688)
Task 5: review Approved (sonnet)
Task 5: minor (deferred): "two scanned commits" (design.md:317) vs "two commits" (design-format.md:~24) — one noun across copies
Task 5: minor (deferred): design.md's gate sentence names the claim class but not how it is established (only via design-format citation)
Task 5: complete (commits 8d017933..99db4688, review clean)
Task 6: dispatched (BASE 99db4688, implementer opus, agent <agent>)
Task 6: implementer DONE (5930e55d): extra ERROR fallback (orchestrator reads itself); manual fix notes after 2nd BLOCK trigger the read; /update-spec change list marks decision edits as review; agents row trimmed; product-workflows.md 9 chars headroom.
Task 6: review Approved (opus)
Task 6: minor (deferred): escalation-rules.md:681 — `first` input neither passed nor excluded explicitly ("those its whole-artifact read passes" vs the list)
Task 6: minor (deferred): escalation-rules.md:520 (version-line) lacks "names each such edit as read by nothing further" (only in part review :683)
Task 6: minor (deferred): escalation-rules.md:679 bold trigger "an edit answering its findings" narrower than the definition (carried first-review findings at the re-review's offer, S1's path) — say "an edit applied at its offer"; same at overlap-reader.md:18
Task 6: minor (deferred): escalation-rules.md:851 and :883 manual-fix-notes sites carry no pointer to the read; :883 "Everything after is unchanged" omits it
Task 6: minor (deferred): design.md:530, specify.md:1107, overlap-reader.md:8/:12 shorthand "the edits after its last review" wider than the rule
Task 6: minor (deferred): .claude/rules/dev-workflows.md:14 pointer "Its one prose-style user" now points at product-workflows — name dev-workflows
Task 6: complete (commits 99db4688..5930e55d, review clean)
Task 7: dispatched (BASE 5930e55d, implementer sonnet, agent <agent>)
Task 7: implementer DONE (ab14c798)
Task 7: review Needs fixes (sonnet): Important — "closing block of the Final report" contradicts the grounding/BRD additions and ### Next step that follow it (specify.md:1282/:1296; docs page). Minors: feature folder + verdict duplicated in prose and block; docs "the last four only where printed" lumps Phase handoff in; GIT-G1 bullet "three live runs" names four.
Task 7: ⚠️ commit-artifacts before the Final report — resolved by controller: canonical terminal order (workflows-core-git invariants: … resume.md → commit-artifacts → the run's last printed output); a stop's message is not the Final report.
Task 7: fix round 1/5 (4 addressed, 0 open; commits ab14c798..be0b4dca)
Task 7: complete (commits 5930e55d..be0b4dca, review clean after 1 fix round)
Ruling: Tasks 8 and 10 dispatched as one batch to one implementer (two commits) — why: both are small wording additions with parts regeneration, disjoint files save escalation-rules regions (T10 :749–752 only) — cost if wrong: one combined review instead of two.
Tasks 8+10: dispatched as one batch (BASE be0b4dca, implementer sonnet, agent <agent>)
Tasks 8+10: implementer DONE (8da5144b, 01c6201e); extra: L2 line in to-fix reworded (LC35 fixed)
Tasks 8+10: review Approved both (sonnet); ⚠️ to-test section placement — verified by grep (after LC12–LC28 section) (controller)
Task 10: minor (deferred): K2 ranking worded differently — epics.md:864 "the open slots going to…" vs escalation-rules.md:761 "the three going to…" (ignores existing markers) — use one phrase
Task 10: minor (deferred): K3 — VIOLATIONS_FOUND bullet still writes the temp file and dispatches before the exception (epics.md:771–778); "every finding goes to the Phase 9 report" — say "every finding the user did not settle"
Task 8: complete (commits be0b4dca..8da5144b, review clean)
Task 10: complete (commits 8da5144b..01c6201e, review clean)
Task 9: dispatched (BASE 01c6201e, implementer opus, agent <agent>)
Task 9: implementer DONE (22fd20c4): extra K4 sites create-ard routing + epics Detection steps; rubric added to reviewer scope; /specify routing comment names impl-maintenance; epic-writer/release-notes-writer 'folder read handoff' left (data, not routing)
Task 9: review Approved (opus)
Task 9: minor (deferred, behaviour): implement.md:1111 R1 recommended case reads only design.md + spec, not the applicable ARD — a fix breaking an [AD#N] Rule gets "Revise the plan" recommended, then the re-review blocks; add the ARD (spec_context.applicable_ard / ard_paths) or narrow the reason
Task 9: minor (deferred): implement.md:1112 "naming each such finding" reads as every deferred finding — say each that also contradicts design.md or the spec
Task 9: minor (deferred, behaviour): readiness-reviewer.md:52 / ready.md:410,:431 — "report unverified" covers only code-repo facts; a fact only an out-of-scope specs file shows (sibling Epic's spec/design for Cross-Epic contract coverage, readiness-reviewer.md:78) has no handling — widen to "a fact you cannot see in what this scope lets you read"
Task 9: minor (deferred): specify.md:475 routing comment omits docs-grounder (also create-ard.md:383, epics.md:365)
Task 9: minor (deferred): ready.md:410 "no clone under ${REPOS_PATH}" also covers the specs checkout — say "no code repository's clone" (and readiness-reviewer.md:52)
Task 9: minor (deferred): ready.md:846–847 edited invariant keeps a hard wrap
Task 9: complete (commits 01c6201e..22fd20c4, review clean)
Ruling: main moved (PR #177 /conformance Plan 2: core 1.79.0, dev 4.60.0, product 3.78.10, docs 1.36.0, security 0.10.11). Merge origin/main into the branch before Task 11 as its own step (implementer opus + review), and Task 11 bumps to core 1.80.0, dev 4.61.0, product 3.79.0, docs 1.37.0, security 0.11.0 — why: CHANGELOG order and coupling bullets must sit on top of main's release; the plan's versions are taken — cost if wrong: re-bump at PR time.
Merge step: trial merge shows 6 conflicts (.claude/rules/dev-workflows.md, docs-workflows.md, workflows-core-read-only.md, CLAUDE.md, dev docs ready.md, docs docs document.md); auto-merged overlap: conformance.md, ready.md, document.md, readiness-reviewer.md, docs conformance.md, workflows-core.md rules, references.md, to-fix.md.
Merge step: DONE 2f293cf6 (parents 22fd20c4, 172e5cf8); full chain EXIT=0; docs-workflows.md tightened 20,244→19,979; CLAUDE.md 35,926.
Ruling: confirm the merge's exclusion of the PRD's _conformance.md from readiness-reviewer's read scope (main reads it only from the default branch) — why: two sides' rules clash; main's default-branch-only reading is the newer, deliberate rule — cost if wrong: the reviewer cannot see a working-tree-only conformance record (which main says it must never read anyway).
Merge step: note — /docs-audit's map line points at "the docs-grounding bullet" now in .claude/rules/docs-grounding.md (pre-existing; final wave)
Merge step: review Approved (opus)
Merge: minor (deferred): _conformance.md exception sits only on the derived_phase clause — make it scope-wide (readiness-reviewer.md:49-50, ready.md:446, :468 read_scope line)
Merge: minor (deferred): K5 to-test item (to-test:63) should also expect the reviewer never reads the PRD folder's _conformance.md
Merge: note for Task 11 — .claude/rules/plugin-updates-coupling.md at 19,975 chars; a new bullet needs older bullets moved to plugin-updates-coupling-history-2.md (update its version range in CLAUDE.md's table row and plugin-updates.md)
Task 11: dispatched (BASE 2f293cf6, implementer sonnet, agent <agent>) with versions core 1.80.0, dev 4.61.0, product 3.79.0, docs 1.37.0, security 0.11.0
Task 11: implementer DONE_WITH_CONCERNS (15c8d8c3): coupling 1.65.0–1.67.0 bullets moved to history-2; added K1/K4/K5 to-test items (possible duplicates of Task 9's); no claim-sweep counts
Task 11: review Needs fixes (sonnet): history.md:10 stale range (1.64.0 → 1.67.0); to-test K1 item unrequested (selftest only), K5 item duplicates Task 9's; new K4 item overlaps (keep for /implement, /epics, /specify scope, say so); stray blank line.
Task 11: fix round 1/5 (3 addressed, 0 open; commits 15c8d8c3..971550c2)
Task 11: complete (commits 2f293cf6..971550c2, review clean after 1 fix round)
Final review: dispatched (opus, agent <agent>) over 172e5cf8..971550c2 with the 33 deferred minors
Final review: Ready with fixes (opus): 0 Critical, 0 Important, 6 new Minor (product-workflows.md:45 map line "each epic.md read"; four false CHANGELOG lines; R1 unmarked-question text misleads; /specify Run details lacks the version-line slot; hard-wrapped new prose in three references; stale pointer docs-workflows.md:38); 27 of 33 deferred minors "fix before merge".
Final: parked — deferred #2 (shutil_rm naming) — Ruling: not a defect; folded into the script edit as style since the file is reopened
Final: parked — deferred #3 (vanished-path selftest) — Ruling: regular-file window already pinned by the deleted-fp check; symlink window covered by #5's fix and its test
Final: parked — deferred #14 (scan.md:330 [SEC#n]) — Ruling: not a defect; the template fixes the post-replay number, and before a replay the current number is right
Final: parked — deferred #15 (triage that ends early) — Ruling: not a defect; a stop records no false positive, so LC29's harm cannot arise
Final: parked — deferred #16 ("two scanned commits" vs "two commits") — Ruling: not two copies of one claim; the narrower case sits inside the general rule
Final: parked — deferred #17 (design.md gate sentence lacks the how) — Ruling: by plan the how is stated once in design-format's claim rule
Final: fix wave dispatched — one implementer, all 6 new + 27 deferred minors (final-review.md)
Final fix wave: DONE 42a6ea9c (40 files, chain EXIT=0 incl. mermaid); extra: row-21 pointer at design.md:501; K7 to-test chmod 000 setup
Final fix wave: re-review — all 33 ADDRESSED (opus); new Minor in fix diff: (1) tree-snapshot.py:62–71 try wraps git hash-object → OSError starting git gives "-" exit 0 (on /implement a dirty user file could commit as the run's); (2) implement.md:406 naming duty has no source for Commit/Keep answers (not in run-state) or a failed after-read's own check run; (3) dev-workflows-tests.md:17 "the two it deliberately leaves out" count short; (4) K7 to-test chmod item imprecise (no version path, --plugin-dir miss, conditional restore, agent may "correct" the chmod). Out of scope: update-spec.md:73 routing omits docs-grounder; R1 ARD arm — either answer leaves a fix against an [AD#N] Rule and the one re-review blocks; question text doesn't say.
Ruling: one more small fix pass for these six — why: user's standing rule "fix all known bugs before push" overrides the skill's single-wave limit; (1) is a correctness hazard — cost if wrong: one extra pass and re-review.
Ruling: R1 ARD arm — where a deferred finding's fix contradicts an [AD#N] Rule, the question's own text says the one re-review will block on it unless the departure is recorded, and "Apply the fix, keep the plan text" records the `- ARD deviation:` line as implement.md's existing deviation rule does and passes it to code-review where code-review takes ard_deviations; if code-review takes no such input, the text-only change alone — why: the user must not be steered into a guaranteed block — cost if wrong: one more deviation record per such run.
Final fix pass 2: DONE 5ea24dfd (chain EXIT=0); check_run_answers run-state key; ard_deviations now passed to every code-review dispatch (concern); extra routing fixes update-spec architecture-grounder, release-notes docs-grounder
Final fix pass 2: re-review — 1–3, 5, 6 ADDRESSED; 4 partly (to-test :39 script path relative; pyenv shim note); new Minor: implement.md:1116 "the one re-review will block" → "where it runs"; :351 "records nothing anywhere else" false for a default Keep (assumptions); :793 missing (writes run-state check_run_answers) marker; code-review.md:62 vs :234–235 wording (unreachable, optional). ard_deviations to every dispatch judged correct (latent bug fixed).
Ruling: one last tiny pass for these wording items, including the optional code-review alignment — why: fix-all rule; each is a one-line edit — cost if wrong: one more cheap re-review.
Final fix pass 3: DONE 428baf55 (wording; gates pass)
Final fix pass 3: re-review — 4 ADDRESSED, no new breakage (sonnet)
Final review: clean after the fix wave and two further passes (commits 971550c2..428baf55)
Rulings + ledger committed (docs/superpowers/verification/2026-11-08-live-checks-r3-fixes-*.md)
Ruling: main moved again (PR #179 D49: core 1.80.1, dev 4.61.0, product 3.78.11, docs 1.37.0 — colliding with this batch's 1.80.0/4.61.0/1.37.0). Second merge step (opus + review); re-version to core 1.81.0, dev 4.62.0, product 3.79.0, docs 1.38.0, security 0.11.0 — why: the batch's versions are taken; CHANGELOG/coupling must sit on main's — cost if wrong: another re-bump if main moves again before merge.
Merge step 2: DONE bdc4e718 (parents 22525a5c, 763fe131), re-versioned in the merge: core 1.81.0, dev 4.62.0, product 3.79.0, docs 1.38.0, security 0.11.0 (dated 2026-11-09); chain EXIT=0. New ruling 11 (merger): PRD folder's pr-draft.md and release-notes.md excluded from readiness-reviewer's read scope (D49 names them in derived_phase; /ready reads them only from the default branch). Flag: main's own coupling bullet says /ready reads release-notes.md off the working copy — looks false.
Merge step 2: review Needs fixes (opus): merge, re-version and ruling 11 hold. Minor: main's coupling bullet (plugin-updates-coupling.md:39) inverts the claim; behind it, stale exclusivity D49 left: phase-handoff.md:429 ("the one reader for which … does not hold" — /ready also reads release-notes.md from <default-ref> only) and release-notes.md:696/:703 ("/docs-workflows:docs-audit excepted").
Ruling: fix main's bullet sentence and the two stale statements in this release (workflows-core 1.81.0, docs-workflows 1.38.0 ship now) — why: fix-all rule; executed text tells the user a false thing before a decline choice — cost if wrong: a few lines.
Merge step 2 fix: c3931f68 (main's coupling sentence; /ready second default-branch reader in phase-handoff §4.0 and /release-notes; chain EXIT=0)
Merge step 2 fix: re-review — both ADDRESSED, no new breakage (sonnet)
Final: branch complete at c3931f68 + ledger refresh; ready to push

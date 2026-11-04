# SDD ledger — live-check round 2 fixes (LC12–LC28, D39)

This is the ledger of branch `fix/live-checks-r2`, cut from `main` at `db769a23`.
- The plan is `docs/superpowers/plans/2026-11-03-live-checks-r2-fixes.md`.
- The defects it fixes were filed by `docs/superpowers/verification/2026-10-29-live-checks.md` as to-fix items LC12 to LC28 and D39.

The branch was run with `superpowers:subagent-driven-development`. That skill keeps its ledger in a git-ignored scratch directory and deletes the directory when the branch finishes, so the ledger is copied here.
- **Copied as it stood, except for one change:** each subagent's internal id is replaced with `<agent>`.
- **Scratch paths are gone:** paths under `.superpowers/sdd/`, `.worktrees/` and `/tmp/` no longer exist.
- **Commits survive:** the commits the ledger names are on the branch.

The rulings are summarised beside this file, in `2026-11-04-live-checks-r2-fixes-rulings.md`.

```text
# SDD ledger — plan: /workspace/.worktrees/lc-r2-fix/docs/superpowers/plans/2026-11-03-live-checks-r2-fixes.md

Spec: docs/superpowers/to-fix.md (LC12–LC28, D39) + user rulings 2026-11-03 (in plan header). Plan Opus-reviewed (READY WITH CHANGES), revised at 6bc07b34. Branch base: main db769a23.

## Pre-flight scan
| Pair / task | Shared file or interface | Finding |
|---|---|---|
| T2 ↔ T3 | escalation-rules.md: T2 edits offer/recorded/Fold sections (~526–760); T3 edits the re-review noun list (:591–592) | disjoint sections; T3 runs after T2 — re-locate by text. OK |
| T1 ↔ T3 | specs-repo-git.md: T1 §3.4/§8.2/§8.4; T3 §6 | disjoint. OK |
| T2 → T4 | asking set + triggers + question shape; read_default_by_ref; overlap-reader scope/draft_path/caller | names match across tasks. OK |
| T2 → T5 | asking set + triggers + shape | OK |
| T4 ↔ T6 | LC21 split: epics.md heading (T4) vs document.md heading (T6); both say they delete LC21 from to-fix | CONFLICT on the to-fix deletion |
| T1–T6 ↔ T7 | to-fix deletions per task; T7 removes empty heading | OK |
| T1 self | tests ↔ code (argparse extend; deferred ref creation) consistent | OK |
| T2 self | files list covers code-scanner steps 2/3/4/7 + hard rules + handoff format + read-only-repos + rules file | OK |
| T3 self | LC22 docs mermaid label → mermaid gate in task gates | OK |
| T4 self | to-fix deletions list vs items fixed: LC17 and LC14/D39 deferred to T5 | OK |
| T5 self | LC16 simpler form: no run-state change; run-state selftest still run (checks implement.md quotes KEYS) | OK |
| T6 self | OK |
- Ruling: LC21's to-fix entry is deleted by Task 6 only (Task 4 fixes the epics.md heading but leaves the entry) — an item is deleted whole once both its sites are fixed — costs nothing if wrong (one-line move).

## Models
T1 opus (session-branch.py subtle), T2 opus, T3 sonnet, T4 opus, T5 opus, T6 sonnet; task reviews opus for T1/T2/T4/T5, sonnet for T3/T6; re-reviews sonnet.
Task 1: dispatched (opus implementer <agent>; BASE 6bc07b34)
Task 1: implementer NEEDS_CONTEXT — LC24 done; the brief's LC28 design (defer branch creation) regresses R1 (a second clone never takes in origin's session branch until it commits) and R2 (lift on an absent branch skips moves → handoff refused after a hand-deleted session file); reproduced old vs new.
- Ruling: LC28 takes to-fix's second fix, not the deferral — keep session-branch.py's creation as today (revert the deferred creation and its test; keep LC24), and make the creation reported: the preflight's `Specs preflight:` line on §3.4's flush, and §6's line on a terminal commit, say the session branch was created where `commit` returns `created: true` (with nothing committed: "created local session/<id> at <base>; no session file to commit yet"). No push-test change needed. — why: the deferral breaks §8.1's two-clone case and §8.3's lift-then-move, and Option A rewrites unpreserved()'s contract; LC28's complaint is that the creation is silent — what it costs if wrong: the empty local branch still appears (now explained); deferral can come later with a design of its own.
Task 1: implementer DONE_WITH_CONCERNS at f9d30817 (LC24 extend/nargs + selftest; LC28 per ruling: creation reported via run-carried session_branch_created on every session-mode §6 line + §3.4 preflight line; feedback.md/frames.md docs "otherwise silent" gain a 5th condition; residual: commit exit 2 before creation → §3.4 push measure meets missing ref (reported, git-failure only)). Task review dispatched (opus <agent>).
- Note for Task 7: CHANGELOG names the new Specs preflight: line and the §6 appended clause.
Task 1: review Approved (opus): spec ✅; 0 Critical/Important; 3 Minor.
Task 1: minor (deferred → carried): M1 environment.md:23 misses §3.4 catch-up's lift-created branch (reword: preflight line where the flush created it, otherwise Specs repo line) → Task 3 dispatch.
Task 1: minor (deferred → carried): M2 session_branch_created has no home in /implement's run-state (add to run-state.py KEYS + implement.md:360 list) → Task 5 dispatch.
Task 1: minor (deferred → carried): M3 session-branch.py:2484-2489 selftest "at the base" can't fail wrongly (run from a checkout whose HEAD is behind origin/main; assert reported base) → Task 3 dispatch.
Task 1: complete (commits 6bc07b34..f9d30817, review clean; 3 minors carried)
Task 2: dispatched (opus implementer <agent>; BASE f9d30817)
Task 2: implementer DONE_WITH_CONCERNS at c5dcffbd (gates pass; overlap-reader desc 627→561). Concerns: /update-spec follows /specify Phase 6 step 2 "exactly" but not in asking set; CHANGELOG/PR must name the PRD/ARD extension; design.md:467 and rules/docs-workflows.md:79 true only because those never set read_default_by_ref; failed by-ref fetch only visible as prep.refreshed:false → /epics report should show it (carry to Task 4); unrequested: bounded-run.md consumer list + /vuln, agents.md rows shortened (check 6).
Task 2: review dispatched (opus <agent>; package review-f9d30817..c5dcffbd.diff)
- Ruling: /update-spec joins escalation-rules' asking set by name (update-spec.md:129 acts "exactly as /specify Phase 6 step 2 and the paragraphs after it say", so it asks once Task 4 lands; an unnamed member is a drift) — sent with Task 2's fix round; Task 4 sweeps update-spec's docs page — costs: one more command in the set; its Leave it open records a - [ ] open question like /specify.
- Carry to Task 4: /epics' report surfaces a failed by-ref fetch (prep.refreshed:false + refresh_note) for the session repo.
Task 2: review Needs fixes (opus): 2 Important (I1 unverified finding's fate in decision questions undefined → Ruling: survivors only, unverified recorded/listed as today; I2 code-scanner step 6 coupling not tied to ref mode), 5 Minor (order re-review offer after decisions; free-text that settles nothing → re-ask once then Leave it open; escalation-rules:473 scan-target claim; docs references.md:38 "on Fold"; set-head --auto under bounded.py on by-ref path). All sent in fix round 1 with the /update-spec ruling (FIX_BASE c5dcffbd).
Task 2: fix round 1 committed e5e91268 (implementer extended /update-spec to the "fix inline" lists + Defer sentences, counts 7→8/5→6/4→5; set-head unconditional on by-ref path). Re-review dispatched (sonnet <agent>).
- Carry to Task 4: check /update-spec's docs page for the asking behaviour.
Task 2: fix round 1/5 (7 addressed + ruling 8 addressed, 0 open; commits c5dcffbd..e5e91268)
Task 2: minor (deferred → carried to Task 3): escalation-rules.md:779 /design Used-by sentence clumsy (colon inside colon; run-together clauses).
Task 2: complete (commits f9d30817..e5e91268, review clean)
Task 3: dispatched (sonnet implementer <agent>; BASE e5e91268; carries C1=T1M1, C2=T1M3, C3=T2 residual)
Task 3: implementer DONE_WITH_CONCERNS at da0dc111 (LC22: diff --quiet exits 0 for a path absent from ref AND index → tests absence first with cat-file -e, then diff --quiet — plan premise corrected; /epics carried its own "the Epic drafts" noun → changed (product-workflows touched → Task 7 counts it); LC26 no parser; C2 mutation check failed the selftest as intended).
Task 3: review dispatched (sonnet <agent>; package review-e5e91268..da0dc111.diff)
Task 3: review Needs fixes (sonnet): Important frames.md cat-file/diff paths lack ./ (phase-handoff §3.2); Minor implement.md:130 <EPIC-KEY> placeholder; Minor specify.md:581 + implement.md:144 restate remainder-last. All sent in fix round 1 (FIX_BASE da0dc111).
Task 3: fix round 1 committed ad533a7f (./ paths stated by rule wording — check-citations rejects a §3.2 cite from Phase 3; placeholders; remainder-last clauses). Re-review dispatched (sonnet <agent>).
Task 3: fix round 1/5 (3 addressed, 0 open; commits da0dc111..ad533a7f)
Task 3: minor (deferred → final review): frames.md Phase 3 quotes phase-handoff §3.2's ./ rule (a copy; check-citations forbids citing §3.2 from Phase 3) — drift risk; implement.md:144 sentence heavy.
Task 3: complete (commits e5e91268..ad533a7f, review clean)
Task 4: dispatched (opus implementer <agent>; BASE ad533a7f; carries: /epics report surfaces failed by-ref fetch; /update-spec docs page asking behaviour; epics.md re-review noun already changed by Task 3)
Task 4: implementer DONE_WITH_CONCERNS at c9973eb8 (beyond brief: Phase 7.4 reports PRD-folder paths changed but unreturned; /epics REFRESH_BLOCKED on by-ref → "Continue with current local state" re-dispatches as-it-stands; edited .claude/rules/docs-workflows.md:79 invariant; LC27 "none raised" labelled; Task 7: stage rules files with git add -u; K3 note: PRD/ARD commands gain Leave it open + one-question shape + questions without edit-only findings + re-review offer after them).
- Carry to Task 5: copy Phase 7.4's "PRD-folder path changed but unreturned → reported" to /ready + /conformance if the reviewer keeps it.
Task 4: review dispatched (opus <agent>; package review-ad533a7f..c9973eb8.diff)
Task 4: review Needs fixes (opus): all 6 risks ✅, 4 additions judged sound (keep; carry the unreturned-change report to Task 5). Important: epics.md:1104/:1111 Phase 9 fate bracket false for reported-not-handed-off paths. Minors: :632 by-ref parenthetical Phase 1 only; docs specify.md:97 stale merge-clause copy; :918 enumeration vs principle (ignored agent-created file); docs specify.md:103 missing re-review-BLOCK case. All sent in fix round 1 (FIX_BASE c9973eb8).
Task 4: fix round 1 committed 707d3e36 (+3 extra copies fixed: Phase 7.4 closing sentence; create-prd/create-ard docs lists). Carry to Task 5: positive record rule + fate bracket limited to maintenance_paths + unreturned-change report.
Task 4: fix round 1/5 (5 addressed + 3 copies, 0 open; commits c9973eb8..707d3e36)
Task 4: complete (commits ad533a7f..707d3e36, review clean)
Task 5: dispatched (opus implementer <agent>; BASE 707d3e36; carries K4 = T1 M2 session_branch_created run-state key; mirror of Task 4's Phase 7.4 rules)
Task 5: implementer DONE_WITH_CONCERNS at b5b8cbc8 (/design has no triage → asks every decision finding (my dispatch was wrong; escalation-rules' "where the command triages" clauses handle it); K4 default None (value is base sha); LC16 one question per existing path).
- Ruling: Task 5's fix round also takes the gaps it named, as LC14/LC16-class defects — (a) LC16: a path the first read listed and the second does not (reverted/deleted by the run) is reported; (b) LC16 wraps Phase 3.5's lint and build runs too; (c) nested $SPECS_PATH: porcelain paths are repo-root-relative while maintenance_paths/HEAD:./ are $SPECS_PATH-relative → strip `git rev-parse --show-prefix` (in /ready, /conformance AND /epics); (d) /epics Phase 7.5 body_facts limited to maintenance_paths. Task 6 takes /document's "project root" (LC14 class, docs-workflows). — why: same defect class, found by this batch, fix-before-push rule — costs: Task 5 scope grows; reviewed in its re-review.
Task 5: review dispatched (opus)
Task 5: review Needs fixes (opus): Important implement.md pre-dirty+edited label; Minors: stale handoff-scope sentences (docs conformance.md:90, ready.md:635, conformance.md:626), one question per run, --no-optional-locks status on session repo (also /epics), bounded free-text re-ask; + rulings (a)–(d) incl. Phase 3B step 8 repro re-run wrapped. All sent in fix round 1 (FIX_BASE b5b8cbc8).
Task 5: fix round 1 committed b4c979e9 ("test run"→"check run" rename across; product-workflows edited too; unwrapped: risk-planner's repro before first edit, code-writer's own installs/codegen/formatters by design).
Task 5: re-review dispatched (opus <agent>)
Task 5: fix round 1/5 (9 addressed, 2 new Minor open — risk-planner repro reachable (bug-diagnosis.md:50-51) → wrap Phase 2B on task_shape bug + heading "every check"; docs implement.md:54 noun; commits b5b8cbc8..b4c979e9)
Task 5: fix round 2 dispatched with the 2 Minors + out-of-scope: conditional "handed off with it" in agent prompts (ready/conformance/epics); announce the Keep default (FIX_BASE b4c979e9)
Task 5: fix round 2 committed 8f3c6f62 (planner repro check run offers Leave out/Delete only — Commit would be undone by Pre-Phase 3.5 re-read; re-read adds only paths not already held; Phase 2B dependency install keeps its own snapshot, unwrapped).
Task 5: fix round 2/5 (4 addressed, 0 open; commits b4c979e9..8f3c6f62)
Task 5: minor (deferred → final review): implement.md:775 should key on "before Pre-Phase 3.5's re-read" not "a Phase 2B risk-planner dispatch" (Revise-before-first-edit edge); docs implement.md:99 "at most two questions per run" → per check run.
Task 5: complete (commits 707d3e36..8f3c6f62, review clean; 2 minors to final review)
Task 6: dispatched (opus; BASE 8f3c6f62; + carried K5: /document "project root" in pre-handoff Agent 1/Agent 3, Mode A ~:1164/:1190 and Mode B ~:1742/:1768 — LC14 class)
Task 6: implementer DONE_WITH_CONCERNS at 84d52bc0 (LC21, LC12, K5; + D39-class fix at /document Phase 8.5 staging; + Agent 2 .claude/memory/ same class; "project root" 7→3 (history/Astro term)). Open: Phase 6.3 commits an operator-dirtied writer page under Proceed anyway vs Phase 8.5 "somebody else's changes stay out of the squash" (contradiction, needs ruling); direct mode reads only the session repo (unreported Agent 1 edit in target folder unlisted).
- Ruling: /document Proceed-anyway contradiction — the option says "pre-existing changes will appear in the diff" (document.md:837), so a page the writer wrote over the operator's dirty state is committed whole (Phase 6.3 stands); Phase 8.5's "somebody else's changes stay out of the squash" is narrowed to files this run did not write — costs: one clause; if wrong, operator edits on a written page ship in the docs PR (which the option already promised).
Task 6: review dispatched (opus)
Task 6: review Needs fixes (opus): Important — run's own page changed-unreturned gets wrong fate (writer page committed by path while reported uncommitted; doc-fixer page dropped by step 3's broad exclusion) → /epics-style exception + narrow exclusion; Minors: docs page wording, Mode B out-of-scope line, relative-path comparison; + Proceed-anyway ruling ("neither doc-writer nor doc-fixer wrote"). Fix round 1 sent (FIX_BASE 84d52bc0).
Task 6: fix round 1 committed 778abb6b (+ nested-repo skip for the cwd read).
- Ruling: docs-workflows bumps to 1.32.0 (minor), not the plan's 1.31.2 — Task 6 changed /document's behaviour (K5 net, Phase 8.5 staging), not only a heading — costs nothing if wrong.
Task 6: fix round 1/5 (5 addressed + skip correct, 0 open; commits 84d52bc0..778abb6b)
Task 6: minor (deferred → final review): document.md:1390 Phase 9 line long with nested bracketed alternative.
Task 6: complete (commits 8f3c6f62..778abb6b, review clean)
Task 7: started (controller)
Task 7: complete (4dfe5eb9; full gate chain EXIT=0)
Final review dispatched (opus <agent>; range db769a23..4dfe5eb9)
Final review: fixes needed (0 Critical, 2 Important, 6 Minor; deferred triage: fix implement.md keying + docs per check; frames.md copy and document.md:1390 acceptable). One fix dispatch with final-findings.md.
Final fix wave dispatched (opus <agent>; FIX_BASE 4dfe5eb9)
Final fix wave committed ddda665f (finding 9 adapted per bug-diagnosis.md: pre-first-edit planner repro runs on the working tree, so the check run stays every pre-first-edit dispatch; no-Commit keyed on before the re-read; parenthetical says scratch checkout only for a re-plan once the run has edited). Scoped re-review dispatched.
Final fix wave re-review: 9/10 addressed; open: finding 9 (implement.md:674/:750 claim a re-plan's repro runs on the working tree; risk-planner.md:35 runs it in the scratch checkout; bug-diagnosis.md:61-62 ambiguous). New Minor: coupling :36 "only where an edit-only finding is open too" false on BLOCK path. Out-of-scope Minor: workflows-core CHANGELOG:13 "offer … now also fires where only decision findings are left" contradicts escalation-rules:569-570.
- Ruling: one more narrow fix pass beyond SDD's single wave — the user's fix-all-known-bugs-before-push rule outranks the skill; exact edits given; re-verified by a scoped re-review — costs one short dispatch.
Residual fix pass committed cb213ffb (3 findings; sweep 7 phrasings → 0). Same agent resumed for rules/dev-workflows.md:22 + risk-planner.md:192 (same gap).
Residual pass 2 committed 13f55237 (rules map + risk-planner:192). Scoped re-review of ddda665f..13f55237 dispatched.
Residual re-review: all findings addressed (sonnet). Final review clean.
- Ruling: the controller trimmed .claude/rules/dev-workflows.md:22 itself (20136 → 19998 chars; validate-catalog warned past 20000 after the residual pass), restating the planner-repro clause compactly with its "from the first edit" anchor made explicit — why: a gate warning this batch caused; a 138-char compaction with no change of meaning — costs: a controller edit no subagent reviewed; the gate chain checked it (EXIT=0, 0 warnings).
Records: rulings + ledger committed to docs/superpowers/verification/2026-11-04-live-checks-r2-fixes-{rulings,ledger}.md. Push + PR next.
```

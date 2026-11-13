# GIT-G1 Part 3 — the scripted handoff and gates, and what a command typed mid-run does

**Date:** 2026-11-13. **Status:** design, for approval. **Track:** GIT-G1, Part 3 of `2026-11-08-git-g1-shared-specs-git-design.md` §7 (below, *the parent design*). **Brief:** `2026-11-12-git-g1-part3-brief.md`, beside this file. **Base:** `main` at `84527132` (`workflows-core` 1.85.0). Below, SRG is `plugins/workflows-core/references/specs-repo-git.md`, PH is `plugins/workflows-core/references/phase-handoff.md`, and `specs-git.py`, `specs_git_state.py` and `specs_git_lines.py` are in `plugins/workflows-core/scripts/`.

## 1. Intent

Part 3 finishes what the parent design set out to do: the handover (`handoff-to-main`, with its consent choice and outcome line) and the two gates (`require-on-main`, `branch-check`) run in `specs-git.py` through the `specs-git` skill, as a run's start and end have since Part 2a. The parent design's reason stands: one implementation, so a fix lands once.

Since the parent design was written, the STAY-2 and MIDRUN-B4 batch (PR #185) taught three things, and this design is shaped by them:

- **The hard part was telling runs apart.** That batch needed five fix rounds on one task and three final-review passes, each finding a new order in which runs of one session can nest. Part 3 must not add nesting orders.
- **`specs-git.py` has outgrown one file.** It is 18,105 lines, of which the built-in test, `selftest()`, is the last 13,000 (`wc -l`; `grep -n '^def selftest'` prints line 5093).
- **Four defects were left for this part** in `docs/superpowers/to-fix.md`: MIDRUN-HANDOFF, MIDRUN-LATEWRITE and RO-SIZE (*From GIT-G1 Part 2a*), and D15 (*Design-level*), which the brief does not list.

## 2. Decisions

**The maintainer's, 2026-11-12 and 2026-11-13.** P1, P2, P3 and P5 were the lead's recommendations, accepted. P4 is the maintainer's own direction: they asked why a command should run at all beside one that has not finished, and widened the lead's first proposal.

| # | Decided |
|---|---|
| P1 | **Order.** (1) Split the selftest out of `specs-git.py`. (2) Script the handoff and the two gates. (3) Slim each command's wrapper. (4) Turn the two references into contracts. |
| P2 | **Record identity is not rewritten in Part 3.** The `started` stamp, parking and the 15-minute `resumable` window stay as 1.84.0 shipped them, since no live run has exercised them yet. Every new call takes the explicit `--started` stamp and adds no inference of its own. Whether to rewrite identity is decided after the r4 rehearsal. |
| P3 | **MIDRUN-LATEWRITE moves to TAIL-G1.** Part 3 does not build a per-run list of written paths (§6). |
| P4 | **A command typed while another run of the session is open asks before it starts, and never runs beside that run** (§4). Only the five logging commands are exempt: `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me` and `/diagnose-session`. This replaces "hand off and switch back" (decision S4 of the STAY-2 design, the research memo's option F2). The maintainer first agreed it for the 23 producers, then widened it to the seven other pipeline commands on 2026-11-13: starting a pipeline command while another is unfinished is a mistake to stop, whichever command it is. The cost is accepted: no second pipeline command runs as a side task while one is in progress on the same checkout. |
| P5 | **TAIL-G1 follows Part 3's last batch**, and the lead builds it. §5.3's slimming batches and TAIL-G1 each edit every command's tail, so before batch 3 is planned the lead asks the maintainer whether the two should be one pass per command. Until that is answered, the order is as stated here. |

**The lead's calls.** L1, L2, L4 and L5 were shown to the maintainer on 2026-11-13 and not objected to. L3, L6, L7 and L8 were made after that, two of them on a reviewer's findings, and are the maintainer's to confirm on reading this document. A builder may revisit one only by showing what it breaks.

| # | Call |
|---|---|
| L1 | **Every caller switches at once in batch 2**, by the route Part 2a took under its decision D1: the `reference` loader sends `phase-handoff handoff-to-main`, `phase-handoff require-on-main` and `phase-handoff branch-check` to the skill. `main` never holds some commands on the script and others on the prose. One producer makes no such request: `/promote-decisions` reaches the handoff through a prose citation in `architecture-promotion.md` §11.2, which the loader reads as the whole reference, so that step is edited in batch 2 to make the request. |
| L2 | **Wrapper slimming is merged with Part 2's 2b+ batches**, so each command file is edited once for its start, end, handoff and gate wrappers together. |
| L3 | **Whether a command asks is resolved from `--command` against the exempt set of five, which the script holds.** Any other command asks, so a new command asks by default. It is never a flag a run must remember to pass: four live runs dropped lines that rested on the run remembering (LC31). This changes the mechanism told to the maintainer on 2026-11-13, a flag each command passes, and keeps its point: nothing is inferred. |
| L4 | **Batch 1 does not wait for the r4 rehearsal; batch 2's plan does.** |
| L6 | **The handoff asks too.** P4's exemption of the five logging commands was agreed on the lead's statement that they finish before the run they were typed under goes on. That is false: each of the five can wait on the user while its run is open (§3), and so the outer run could hand off and switch the checkout under one. So the handoff's prepare call makes the open-run test again, over every other run of the session, and asks the same question before the consent choice (§4.4). Moving each logging command's start call below its last question was considered and refused: `/prompt` does free-form work on the open run's files after its question, a question of `/diagnose-session` is held in a reference where no gate on the command's text sees it, and the move would reverse `CLAUDE.md`'s rule that the preflight runs at run start. |
| L7 | **D15 is closed in batch 2 by one shared read.** Git overwrites a git-ignored copy at a gated path in a switch, a merge or a fast-forward pull without a word. Row B′ already tests for such a copy. The scripted gates make the same read before every switch, merge or pull they run or name. That set is derived at build time from PH §4.4's per-row commands, row C's repair and §6.1's stops, never from a list in this document. No run is known to reach D15, and `to-fix.md` says to fix it only with a measured case; it is taken here because the read is a few lines once the gates are in the script, where it was a paragraph per row in prose. |
| L8 | **The start's question fires only on a first start.** A call that carries the answer, a `--rerun`, and a `--resume` that finds its run's record keep 1.84.0's identity rules untouched (P2), so a run is never asked about itself. A `--rerun` or a `--resume` that finds no record of its own is its run's first start, and asks. That covers the skill's remake of a first start the harness stopped: the first call saved nothing, so its remake finds no record. |
| L5 | **The three open rule gaps of the parent design's §6** are settled in the design-questions step of the batch that needs each, as that section says: (i) and (iii) in batch 2, (ii) with `/brd-package`'s preparation. |

## 3. What was measured

- **Callers.** 23 producers hand off: `grep -lE 'phase-handoff handoff-to-main' plugins/*/commands/*.md` returns 22, and `/promote-decisions` reaches the handoff through `architecture-promotion` §11.2. 16 consumers call `require-on-main`, and 24 commands run `branch-check`, 19 of them passing a prefix (`python3 scripts/reference-parts.py check-branch-check`).
- **Every consumer is a producer.** The 16 files matching `phase-handoff require-on-main` are all among the 22 matching `phase-handoff handoff-to-main` (`comm -13` of the two sorted lists prints nothing). §4 leans on this.
- **Non-producers.** Of the 35 commands that run a start and an end, 12 hand nothing off in the specs repository: seven pipeline commands (`/upgrade`, `/vuln`, `/docs-audit`, `/docs-brand`, `/docs-init`, `/document`, `/security-workflows:scan`) and the five logging commands (`/diagnose-session`, `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`). So 30 commands ask under P4 and 5 do not.
- **The logging commands can wait on the user while open.** In each of the five, a question stands between the start call and the end call: `/feedback` asks at its line 41 and in its grouped prompt at 50 (its start at 30, its end at 96); the three `/prompt` commands ask for the target, and `/prompt` then does the correction itself, free-form work on the open run's files, before its end; `/diagnose-session` asks its problem intake from line 31 (start at 27, end at 80), and once more through `session-diagnosis.md` (its line 33). Line numbers are at this design's base. The STAY-2 research memo counted these commands as asking nothing there; its text search did not match a prompt stated in prose.
- **No logging command runs `branch-check`.** Its 24 callers resolve a folder, and none of the five does.
- **What a run reads today.** The generated entry files are 79,947 bytes (`handoff-to-main`), 94,927 (`require-on-main`) and 34,282 (`branch-check`); PH is 202,499 and SRG 273,941 (`wc -c`). The `require-on-main` file is over the Read tool's limit, which is RO-SIZE.
- **Room in the rules file.** `.claude/rules/workflows-core-git.md` is 19,960 characters against a 20,000 warning (`LC_ALL=C.UTF-8 wc -m`); `.claude/rules/workflows-core-handoff.md` is 5,231.
- **Who writes the session files.** Only the cost entry (`session-cost.py`) and the security register (`register.py`) are written by scripts. Feedback, follow-ups, `resume.md`, `implementation.md` and the drafts are written by the run's own Write calls. The cost file is one per session (`cost/<sid8>.md`), so two runs of one session append to the same file.
- **Background writers.** No command, agent or reference asks for a background dispatch (`grep -rliE 'run_in_background|in the background|background agent'` over `plugins/*/commands`, `agents`, `references` and `skills` finds only `/docs-serve`'s server, `bounded-run` and an unrelated guideline page). Of the eleven agents granted Write or Edit, only `doc-writer` names a session-file shape.

## 4. A command typed while another run is open

### 4.1 The rule (P4)

**Where the command being started is not one of the five exempt commands, and SRG §3.5's open-run test finds a run of this session open on HEAD's branch, the start does nothing and returns a question.** The test is `_open_run` as it stands, applied to every record of the session, the command's own records and parked ones included. Nothing is flushed, parked, saved or switched before the answer.

The skill presents the question as an `AskUserQuestion` call of two options. It names each open run it found, with its command and when it started. The wording is fixed in SRG first and pinned in `specs_git_lines.py`, as every line the script prints is.

- **Finished or abandoned.** A second call ends the protection of each run found, by the `protects: false` mark the open-run test already reads, and the start then proceeds as a plain start: no `midrun`, the ordinary flush and branch disposition. Such a run's record still serves its own end, should that run go on after all, as a restarted run's record does today. Its files are then no longer protected, by the user's own answer; its own handoff still asks before it moves the checkout (§4.4).
- **Still in progress.** The typed command stops before its preflight and writes nothing into the specs repository. Its stop line names the open run and says to finish it first.

A free-text answer is normalised into one of the two or asked again, never acted on as written (`workflows-core:escalation-rules` §0). Several open runs get one question, and its answer covers them all.

The question fires only on a first start (L8).

**What the answer call does to the earlier run's record is settled in batch 2's design questions**, bound by two requirements. That run no longer protects its branch. And its own end still finds its record: where the same command was typed again, the earlier record is parked unprotecting, as a restart parks it today, never marked in place, since a plain start overwrites a record of its own command that the open-run test no longer passes.

### 4.2 What it replaces, and what it leaves alone

- **The five logging commands are unchanged at their start.** Typed mid-run, they keep decision S3 as 1.84.0 shipped it: they switch nothing and commit only their own change, by the landing or the here form. Commenting on a run in progress is what they are for.
- **No pipeline command runs mid-run again.** After the question, either the open run no longer protects, or the typed command has stopped. So a producer's own handoff never moves the checkout under an open run, which was MIDRUN-HANDOFF's case, and its shared-key case with it.
- **No gate runs under an open run.** Every `require-on-main` caller is a producer (§3), and no `branch-check` caller is a logging command. PH §3.3's *Row B′'s remedy* and §4.4's per-row commands keep their wording. PH §6.1's mid-run stop forms become unreachable: batch 2 verifies the caller set again and retires them in its claim sweep.
- **A prerequisite still in progress is caught.** Today, `/specify` typed while `/create-ard` still waits on a question for the same key reads the ARD as absent and carries on without it. Under P4 it asks first.
- **The same command typed again gets the same question.** For the 30 commands that ask, this replaces the key-set comparison (the STAY-2 rulings' M1). M1's keyless gap, a keyed run retyped with no key reading as a restart, can then arise only among the five logging commands. It stays listed, and P2's identity question after the rehearsal settles it.

### 4.3 Edges the builder must settle or verify

- **No command may start a pipeline command while its own record is open.** A run that starts another command itself (`/brd-split`'s *Ground now*, a next-phase offer the user accepts) ends first, so its record is gone and nothing is asked. Verify this for every command that asks before the build; a command found starting one with its record open is brought to the maintainer.
- **The prose path.** With no session id there are no records. SRG already states an observable trigger for a run typed mid-run by hand (§3.5: another run of this conversation has printed its preflight's `Environment:` line, and no `Specs repo:` line since); the question is asked on that trigger too.
- **The question rules.** A command that asks must have loaded the question rules before its start call. Both reviews of this design read that step ahead of the start call in all 30 commands that ask. `check-questions` holds the step above a command's first question, not above its start call, so batch 2 either adds that test or states that review holds it.

### 4.4 The handoff asks too (L6)

**Before the consent choice, the handoff's prepare call applies the open-run test to every other record of the session**, whichever run started first. Where one passes, it returns §4.1's question, and the skill asks it before presenting the consent array.

- **Finished or abandoned.** The answer call of §4.1 runs, and the handoff goes on to its consent choice.
- **Still in progress.** The handoff is not made while that run stands. The run says so, names the other run, and waits; when the user says to go on, it makes the prepare call again.

This closes three cases with one test:

- **A logging command left open at its own question** while the user goes back to the run it was typed under.
- **`/prompt` in the middle of its correction.**
- **A run the user reported finished that goes on after all.** Its own handoff then finds the later run open, and asks.

**What it does not close:** an earlier run's end commits the session files it finds dirty, a later open run's unfinished ones included, under its own message. Nothing is lost and no checkout moves. Telling those files apart is MIDRUN-LATEWRITE's subject, and goes to TAIL-G1 with it (§6).

## 5. The batches

Each batch goes through the family's cycle: design questions, plan, plan review, build with task reviews, a final whole-branch review, gates, pull request. Release versions are derived at release time, never fixed in a plan.

### 5.1 Batch 1 — the selftest out of `specs-git.py`

- **Move `selftest()` and everything only it uses into a module of its own.** `python3 plugins/workflows-core/scripts/specs-git.py --selftest` stays the entry CI runs, and prints the same PASS line with the same check count as the tree it was split from (1,176 at `fdafe85e`, as the brief records; re-derive it on the batch's base).
- **No behaviour changes.** The script's non-test code is not edited beyond what the move needs.
- **Prove the tests kept their teeth.** A split can leave a check that no longer exercises the code. After the split, at least one mutant per scenario group must still fail its check. The groups are the fifteen `scenarios_*` calls at the end of `selftest()`. Take each mutant from the appendix of the Part 2a or the STAY-2 verification record where it holds one for the group, and write a one-line mutant where it holds none.
- **Write the eight missing mutants.** The STAY-2 record names eight Done-when checks with no mutant of their own: `e_land_refused`, `e_land_stopped`, `e_land_offline`, `e_land_no_origin`, `t_midrun_keyed_other`, `t_held_journal`, `e_midrun_here_kill` and `e_midrun_here_no_resume`. Each gets a one-line mutant shown to fail it, recorded in the batch's verification record.
- **Let one scenario group run alone.** The whole selftest takes about three minutes; an implementer working on one area should not wait for all of it. CI still runs everything.

### 5.2 Batch 2 — the scripted handoff and gates, every caller at once

**Its plan is written after the r4 rehearsal's findings are in.** A defect the rehearsal finds in the start or end is fixed before this batch, under the bugs-first policy.

What the script and the skill must support is the parent design's §5.2, §5.4 and §5.5, unchanged. This design adds:

- **Prepare, ask, act.** Four questions stay in the conversation: the consent choice (PH §4.3), `require-on-main` row C's repair offer, `branch-check` §6.2's reuse question, and §4's open-run question. For each, one script call does the reads and returns the lines to print above the question and which array to present; the skill asks; a second call acts on the answer. No script call asks anything.
- **The pull request is a call of its own.** Its body is written by the run, and filling a repository's template is the run's judgment (PH §2.7.1), so the commit-and-push call returns, the run writes the body, and a further call opens the pull request.
- **Judgment stays with the run, and its text moves beside the skill.** Choosing the consent class (PH §4.0), the title and body facts, the template fill, and what a caller does on `absent` are not scripted. What a run must read to make them lives in the skill's text or in small files beside it, as `run-key-set.md` does for the run key set.
- **The record gains what the handoff and gates share.** The branch this run created or reused (row B's ownership test reads it), a consent answer carried to a later phase, and the gate results a later step reads. Each call names its record by `--started` (P2).
- **§4's question**, at the start with the exempt set of L3, and at the handoff (§4.4).
- **The loader's routing (L1)**, and with it the fate of the three generated entry files. The citations of PH that the skill's text and the script's output serve, and those that still read a file, are stated in the loader's paragraph, as they are for SRG. `scripts/reference-parts.py`'s entry-file checks change in the same batch, so the gates stay green.
- **D15 (L7).** One primitive reads whether an ignored copy stands at a gated path, and each scripted row that runs or names a switch, a merge or a pull warns as row B′ does, with `git add -f` and a commit first. `/update-spec`'s own pending-change test, which lists no ignored file, is routed through the same read. The fourth bullet of D15, a read-only mount refreshed from outside, is outside any run's reach, and moves to `to-fix.md`'s *Accepted* section in the commit that closes the rest.
- **RO-SIZE closes here.** Done when no ordinary run of any of the 16 consumers makes a read over the Read tool's limit. Show it by listing every citation of PH in those commands with the text that serves each, and by measuring the bytes a producer and a consumer read for their handoff and gates before and after (the parent design's §8).
- **`/brd-package`'s preparation**: consent in its Phase 7, execution in Phase 9 on the carried answer, and rule gap (ii).
- **The references stay executable.** PH keeps its step-by-step text in this batch, as the text a run follows by hand where the script cannot start. Only its mid-run statements change (below).
- **Room in the rules file first.** Move a paragraph of `workflows-core-git.md` into a rules file beside it before writing a word into it.
- **A claim sweep, by subject** (`.claude/rules/claim-sweep.md`): every statement about what a run typed mid-run does that P4 makes true of the five logging commands alone, and every statement that such a run hands off, moves HEAD by its own handoff, or commits as any run's whose HEAD moved, across SRG (§3.5, §4 step 1), PH, the skill, the rules files, the rationale's `stay-landing` section, PH §6.1, the plugins' docs pages and `to-test-on-real-project.md`. Each is rewritten against what the shipped question enforces.
- **`to-fix.md`**: MIDRUN-HANDOFF, RO-SIZE and D15 deleted in the commit that closes each; live-test items for the question added to `to-test-on-real-project.md`.

**If one batch proves too large**, split it by entry point, the two gates first and the handoff second. Never split it by command.

### 5.3 Batch 3 onward — wrapper slimming, with 2b+

One plugin or command family per batch. Each command keeps a start call, an end call, a handoff call with its parameters, its gate calls, and the work that is its own. No call site restates a rule of the shared step (the parent design's §2 anti-goals and §8). The per-phase call that records `inputs_read` (the parent design's §5.5) lands here, where each command's *Record what the run reads* sentence is rewritten anyway.

### 5.4 The last batch — the references become contracts

SRG and PH lose their step-by-step procedures and keep what each entry point guarantees, its inputs and outputs, its variation points and the reasons for its rules. **Its design questions must settle what a run does where the script cannot start**, since the by-hand text is what goes. State each reference's bytes before and after, and show that no run reads either whole.

## 6. MIDRUN-LATEWRITE moves to TAIL-G1 (P3)

The fix `to-fix.md` named was a per-run list of the paths each run wrote. The measurements of §3 say it does not belong here:

- **A list of paths cannot attribute a shared file.** Two runs of one session append to the same cost file, so ownership is per entry. The snapshot comparison already works per entry.
- **It would rest on the run remembering.** Most session files are written by the run's own Write calls, so the run would have to report each one, and LC31 is that kind of rule being dropped.
- **Almost nothing reaches it.** One of its two routes needs a background writer of session files, which the family does not have. The other needs three runs open on one branch, ended out of order.
- **The handoff does not need it.** A producer passes its deliverable paths explicitly, and after P4 no pipeline command runs beside an open run at all.
- **TAIL-G1 gives it a natural home.** That track puts the tail's writers under the skill. A script that makes the writes can record them without relying on the run.

## 7. Goals, non-goals, anti-goals

The parent design's §2 stands. For Part 3:

**Goals**

1. The handoff and both gates have one implementation, tested, with every caller on it.
2. A run reads less to hand off or to gate than it does today, and nothing over the Read tool's limit.
3. Fewer reachable states than today, not more: after P4, the only run that can start beside an open run is a logging command, and after L6 no handoff moves the checkout under any open run without the user's answer.
4. `specs-git.py` is a file an implementer can read and a reviewer can check.

**Non-goals**

- Rewriting record identity (P2).
- MIDRUN-LATEWRITE (P3), and the rest of the end-of-run sequence, which is TAIL-G1.
- MIDRUN-2S, two sessions on one checkout, which stays accepted.
- Changing what a handoff or a gate does for a run with no other run open. A behaviour change found necessary on the way is a separate, named decision, as in the parent design.
- Ports to the internal editions.

**Anti-goals**

- A handoff that moves the checkout under a run that is still open, without the user having said that run is finished or abandoned.
- A test of which commands ask that rests on a flag, a naming pattern, or anything a run must remember (L3).
- A new record field or call that infers which run it belongs to (P2).
- A gate that reads more after this part than before it.

## 8. Constraints

The parent design's §3 stands: the plugin-root boundary, Python 3 standard library only, bounded runs, questions in the conversation, state outside the conversation, green gates, the prose rules. In addition:

- **The exempt set of L3** is held in the script, and a selftest case fails where a name in it is no command the tree holds. A command outside the set asks, so a new command needs no entry anywhere.
- **Every new line the script prints** is worded in SRG or PH first and pinned in `specs_git_lines.py`.
- **`workflows-core-git.md`** gets room before it gets text (§5.2).
- **The rehearsal's findings** are read before batch 2's plan is written (L4).

## 9. Done when

- **Batch 1:** the selftest lives outside `specs-git.py`; the check count is unchanged; a mutant per scenario group still fails its check; the eight named checks each have a mutant on record; one group can be run alone; CI is green.
- **Batch 2:** all 23 producers, 16 consumers and 24 `branch-check` callers run through the skill; §4's question has a selftest for each answer, for several open runs, for the same command typed again with the earlier run's end still finding its record, for a re-run and a continuation that find their record and are not asked, for a remade first start that finds none and is, and for a logging command left unchanged; the handoff's test (§4.4) has one for each answer, with the other run started before and started after; RO-SIZE is shown closed as §5.2 says; D15's read has a selftest for each row that uses it; MIDRUN-HANDOFF, RO-SIZE and D15 are gone from `to-fix.md`, D15's read-only-mount bullet moved to its *Accepted* section; the claim sweep's before and after counts are on record; the gate chain exits 0.
- **Batches 3 onward:** the parent design's §8 measurements, before and after each batch.
- **The last batch:** neither reference is read whole by any run, and each one's size is stated before and after.
- **Each batch:** a verification record written last, the rulings and the verbatim ledger committed before the workspace goes, dated changelogs, and a coupling bullet for each `workflows-core` release.

## 10. Left to the builder

- Where the selftest module lives and how it reaches the script's names. Beside the script it ships to every user's plugin cache, about 800 KB that no command runs; outside the plugin it needs a path CI can find. The lead leans to outside the plugin.
- The script's new subcommands and JSON fields, and the skill's new entry points and their wording.
- Whether batch 2 is one batch or two (§5.2).
- Which paragraph leaves `workflows-core-git.md`, and for where.
- The question's exact wording, and whether either option carries `(Recommended)`.
- Whether the three generated entry files survive batch 2 as lookup text, shrink, or go.

## 11. How it is run

From the brief, which holds the full list of evidence to read:

- **Models (maintainer, 2026-11-12):** Fable 5.2 for the design, each plan and their reviews, and for the final whole-branch review and its re-reviews. Opus for implementers and task reviews.
- **Execution:** `superpowers:writing-plans` with an independent plan review, then `superpowers:subagent-driven-development`, with a ledger, a text-only backup of the workspace to a host path, Opus task reviews and a final whole-branch review.
- **Git:** a feature branch in a worktree, never a `git checkout` in the shared checkout. A reviewed branch is pushed and its pull request opened without waiting; merges are the maintainer's.
- **Lessons carried:** derive versions at release time; measure the population a fix serves before designing it; write the verification record last; commit the rulings and the ledger before the workspace goes.

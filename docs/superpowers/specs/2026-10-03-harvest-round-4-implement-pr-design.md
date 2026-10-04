# Upstream harvest round 4 — Round 3: `/implement` looks before asking, and the code pull-request body

Date: 2026-10-03. Status: design approved in conversation; spec awaiting review. Branch: `iv-gu/harvest-r4-impl-pr` in all three editions.

## Background

Rounds 1 and 2 of harvest round 4 shipped (`docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md`, `docs/superpowers/specs/2026-10-02-harvest-round-4-review-pipeline-design.md`). `docs/superpowers/harvest/NEXT.md` § *Harvest round 4* keeps items 13–21 of the survey as backlog. This round takes two of them, the two that change what every `/implement` run does:

- **Backlog item 13** — `/implement` looks before asking, and can re-classify upward after exploring (BMAD `7e571784`, `124ea1af`, `2c10d5ba`).
- **Backlog item 15** — the pull-request body: merge danger, before/after evidence, the repository's own template (mattpocock `pr`, and the "My repo already has a PR template" answer in its `docs/engineering/pr.md`).

The backlog's numbering is kept: "item 13" here is the backlog's, not Round 2's item 13 (the escalation heading).

The three editions are as in Rounds 1–2: **this repository** (canonical — `workflows-core`, `dev-workflows`, `product-workflows`, `docs-workflows`), **the internal edition** (one `plugins/dev-workflows` plugin) and **the Copilot edition** (`ihudak-copilot-plugins`: `dev-workflows/skills/<name>/SKILL.md`, `skills/_shared/`, `agents/`). A path written for this edition maps onto the other two as Round 1's spec describes; this repository's `dev-workflows:code-handoff` is `references/code-repo-handoff.md` in the internal edition and `skills/_shared/code-repo-handoff.md` in the Copilot edition. Every surface this round changes exists in all three.

### What is wrong today

1. **Phase 1 asks before it looks.** `/implement` Phase 1 — *"Rule: Ask, don't guess. This rule is absolute."* — analyses the description alone and asks about every ambiguity it finds, before anything is read. A question whose answer is written in the repository (which framework, where a thing lives, what the convention is) reaches the user, and nothing separates it from a decision only the user can make.
2. **The class is fixed before anything is explored.** Phase 1.5 classifies from the description, but several `workflows-core:model-routing/classification` §1.1 triggers cannot be known then — *"Changes touching more than 3–5 non-test files"*, and whether the change touches authentication, a schema, a public contract or concurrency. Re-classification runs one way only: `risk-planner` and `code-review` may return `### Re-classification` **down**. A `SIMPLE`/`MODERATE` run whose Phase 2A exploration shows a §1.1 trigger still plans and implements as `SIMPLE`/`MODERATE`, which has no Opus review gate.
3. **Mid-implementation, a trigger the plan missed changes nothing.** Phase 3A step 5's only rule is *"If a new ambiguity emerges mid-implementation: STOP, ask"*. A `MODERATE` run that discovers, while editing, that the change needs a migration or reaches an authentication path finishes as `MODERATE` and ships with no review.
4. **The code pull-request body states facts but not evidence or danger.** `dev-workflows:code-handoff` §2.7's body is what the run produced, the files changed, the review verdict and the test result. It shows no before beside the after, says nothing about how hard the change is to walk back, and ignores the repository's own pull-request template — which `gh pr create --body-file` replaces outright on the `gh` path, and which a web UI prefills beside the pasted body on §3.2's fallback path.

## Goals

1. Each of the four failures above is unreachable in every edition.
2. Every statement of each changed claim is found and rewritten — the whole population, the `docs/` pages and the instruction tiers included (`CLAUDE.md` § Editing discipline, refinements 4, 6 and 8).
3. Every check is shown red on the pre-change tree and green after it.
4. A run that meets no trigger asks no question it did not ask before, and gains no prompt.

## Non-goals

- **The other commands that carry "Ask, don't guess."** `/design`, `/specify`, `/epics`, `/document` (both modes), `/ready`, `/release-notes` and `/docs-profile` keep their Phase 1 rule this round; `NEXT.md` records them as a follow-up candidate.
- **`/vuln` and `/upgrade` classification.** Each classifies on its own rubric (`/vuln` Step 0's per-CVE fix size; `/upgrade`'s per-component planner) and is unchanged.
- **A user-pinned route or class** (BMAD `2c10d5ba`'s `workflow.route` lever) — rejected again for the reason the survey gave: it bypasses the classification gate.
- **BMAD's token-count split prompt and its Open Questions drain.** Phase 1's choices rules already batch the questions; no new prompt is added.
- **The specs-repo and docs-repo pull-request bodies** (`workflows-core:phase-handoff` §2.7, `docs-workflows:finish-and-handoff`). This round's template rule reaches code pull requests only; `NEXT.md` records the other two as a follow-up candidate.
- **mattpocock's Summary picture menu and Mermaid** — rejected again.
- `references/specification-format.md` (frozen).

## Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | Phase 1's rule (item 13) | **"Look, then ask; never guess."** The description is the starting intent however brief it is; the run never asks the user to restate it. Phase 1 still lists every candidate ambiguity under its five headings, and first tries to settle each from what the run can read — the inputs Phase 0 resolved, the code, the repository's own `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and `README.md`, and `git log` — looking only as far as each question needs. This is not Phase 2A's or 2B's exploration |
| D2 | What is asked (item 13) | A candidate the reading settles is **missing evidence**: no question; the plan records it with where it was found. A candidate the evidence leaves open, whose answer changes what the user would notice in the result — behaviour, scope, an interface, compatibility, a constraint nobody wrote down — is a **decision**, and is asked under Phase 1's existing `choices` rules. A candidate the evidence leaves open whose answer the user would not notice is settled by the run and listed in the plan's Assumptions. Nothing that changes the result is assumed |
| D3 | The invariant (item 13) | *"NEVER make assumptions that could have been asked — ask instead"* becomes: never assume what the evidence leaves open and the user would notice — look first, then ask; never ask what the repository already answers |
| D4 | Re-test after exploration (item 13) | In Phase 2A, once the exploration returns (or the orchestrator's own reads stand in for it), the Phase 1.5 class is tested again against §1.1 with the file map. Where a §1.1 trigger now applies, the class is raised — to `SIGNIFICANT`, or `HIGH-RISK` under §1.1's multiplier — and the run announces `Re-classified upward after exploration: <trigger> (<path>)`, updates `model_routing`'s `classification` and `reason`, and continues at Phase 2B's `risk-planner` dispatch with the exploration as its codebase summary. No second exploration. No file has been written yet |
| D5 | When the re-test does not run | When Phase 2A was entered from a down-classification the user accepted at Phase 2B. That acceptance is the plan-approval override — the sanctioned exit from Phase 1.6's floor — and a re-test would undo it |
| D6 | Phase 2A's summary file | Phase 2A writes its exploration output to `summary_file` (a `command mktemp -t dw-impl-summary-XXXXXX` path outside any repository tree), as Phase 2B already does, so D4 and D8 hand `risk-planner` a path. Removed with the run's other handoff files |
| D7 | Phase 3A's mid-implementation rule (item 13) | Phase 3A step 5 splits three ways. **(a)** The work reaches a §1.1 trigger the approved plan did not state — a fact its Steps and Files did not name: a schema change, an authentication or authorisation path, a public contract, concurrency, the non-test file count passing 3–5 — → the re-plan (D8). **(b)** A decision (D2's test) the repository cannot settle → stop and ask, as today. **(c)** Anything else → look, and continue. Phase 3B step 4 keeps (b) and (c) |
| D8 | The re-plan (item 13) | Stop editing. Raise the class (D4's rule and announcement, with `during implementation` for `after exploration`). Write the diff so far — `git add -N . && git diff` — to a `command mktemp -t dw-impl-partial-XXXXXX` path outside any repository tree, recorded as `partial_diff_file`. Dispatch `risk-planner` with the complete Phase 2B brief, its `Classification` reason naming the trigger and its path, plus `Work so far: read the diff at <partial_diff_file>`. Its return is handled as Phase 2B handles one: **Approve** → the new plan replaces `plan_file` and the run continues at Phase 3B step 1; Pre-Phase 3 and Pre-Phase 3.5 are not run again, and the baseline still predates every edit. **Accept revised classification** (a down-classification) → Phase 3A resumes where it stopped, on the plan already approved. **Revise** and **Override** → `risk-planner` re-dispatched with the complete brief, `Work so far` included. At most once per run: a second trigger after it is asked about under (b) |
| D9 | `risk-planner`'s new input (item 13) | An optional `Work so far` field: the path to a diff of edits already on the branch. They are part of this change and stay; the planner plans from the tree as it stands — a step may revise what the diff wrote, and the plan never assumes a clean tree. On a bug-shaped task the partial edits may already turn the repro green, which is the existing *Ranking withheld* return and its prompt |
| D10 | Stops after files were written (item 13) | On the re-plan path, Phase 2B's three **Cancel** arms — the re-classification prompt's, the withheld-repro prompt's and the plan-approval prompt's — stop after files were written. They join Phase 4.6's `"Every run"` list, so each commits through Phase 4.6 with `clean_finish: false` and the stop's reason as the blocking fact; the `clean_finish` row's first condition cites that list and needs no copy. Phase 4.6's *"Two Cancels are not in that set"* paragraph, which says Phase 2B's repro prompt runs before Pre-Phase 3, is rewritten to hold on this path too. |
| D11 | The report (item 13) | The Phase 5 report's `### Classification` section records every raise — after exploration or during implementation — with its trigger and the evidence path |
| D12 | The body's shape (item 15) | `dev-workflows:code-handoff` §2.7 defines it once; the callers fill it. No preamble: the body opens on §2.9's banner where the run did not finish clean, and otherwise on its first heading. Four sections, in order: **Summary** (what changed, one line per notable item, and the files changed), **Evidence** (D13), **Merge danger** (D14), **Review** (the verdict, the triage summary and every finding not applied — what the body carries today, under a heading) |
| D13 | Evidence (item 15) | A **Before** and an **After**, taken only from what the run observed. `/implement`: the Pre-Phase 3.5 baseline against the Phase 3.5 verify result; on a bug-shaped run, before is `risk-planner`'s red repro (command and output) and after is the regression test passing in the verify run. `/vuln`: the vulnerable version inside the range against the fixed version outside it, and the test counts before and after. `/upgrade`: each component's versions, and the test counts against the Phase 2 prep baseline. Where the run has no before or no after — the operator's *Skip tests*, an unverified run — the section says so and why. "Tests pass" alone is a claim, not evidence |
| D14 | Merge danger (item 15) | **Door** — `one-way` when the change includes a step that reverting its commit does not undo: a migration that drops or rewrites data, removing a public contract consumers outside the repository use, writing persisted data in a new format, or anything that ships outward (sends, publishes, deletes); `two-way` otherwise; **where the run cannot tell, `one-way`, with the reason** — so the reader slows down rather than skims. One line of why beside it. **Blast radius** — a short phrase naming what breaks if the change is wrong (an API's consumers, a data store, a screen, the build), with one line of what that would look like. The definition lives in §2.7 alone; each caller applies it to its own change |
| D15 | The repository's template (item 15) | §2.7 resolves a template against a fixed set of paths in the committed tree, matching the file name case-insensitively — never by searching free text: `pull_request_template.md` in `.github/`, at the root, or in `docs/`, first found wins; otherwise a `PULL_REQUEST_TEMPLATE/` directory in one of those three places holding exactly one `.md` file; otherwise `.gitlab/merge_request_templates/Default.md`. Where one resolves, the body **is that template filled**: its headings kept in order, each section answered from the run's facts; a section the run has nothing for says so and why, never left as the template's placeholder; a checkbox ticked only where the run can show it, never deleted; each D12 section placed in the template section that asks for it, and every D12 section no template section asks for appended after the template, in D12's order. §2.9's banner stays the first line. A directory holding several templates names no default: none is applied, and the body's last line says the repository offers several, naming the directory |
| D16 | The callers (item 15) | `/implement` Phase 4.6, `/vuln` Step 3.9 and `/upgrade` step 7.5 add to `body_facts` what D13 and D14 need. §2.11's `body_facts` row names the four sections. The commit message (§2.3) is unchanged |
| D17 | Versions | New behaviour → minor. This edition: `dev-workflows` 4.7.0; `workflows-core`, `product-workflows` and `docs-workflows` only where the population sweep finds a statement of a changed claim in them. Internal edition `dev-workflows` 2.68.0. Copilot edition `dev-workflows` 2.37.0 |
| D18 | Order and landing | As Rounds 1–2: this edition, then the internal edition, then the Copilot edition (hand-adapted, never `cp`). Each: gates green, a whole-branch review to zero findings, then merge, push, delete the branch |

## Item 13 — `/implement` looks before asking, and re-classifies upward

**Phase 1** (D1–D3). The five candidate headings stay — ambiguous scope, missing constraints, several valid approaches, undefined integration points, missing acceptance criteria. What changes is the step between finding a candidate and asking it: each is first looked up, and only a decision reaches the user. The `choices` rules (2–4 options, the harness's free-text escape, a `(Recommended)` default, related decisions grouped) are unchanged, and so is *"Do not proceed until all questions are answered"*. A run whose description and repository answer everything asks nothing, as a run with no ambiguity does today.

**After exploration** (D4–D6). Phase 2A's exploration is where §1.1's file-count trigger, and most of its area triggers, first become knowable. The re-test runs before the Phase 2A plan is written: it reads the exploration's file map — the files the change will need to touch, and what they do — against §1.1, and raises the class where a trigger applies. Phase 1.6's multi-source floor already sends every multi-source run to `SIGNIFICANT`, so the re-test matters on direct-mode runs with one repository and no directory input — the only runs that reach Phase 2A from Phase 1.5. Down-classification keeps its route: `risk-planner` proposes it, the user accepts or overrides.

**During implementation** (D7–D11). The re-plan is BMAD's "replan to full when the work is larger than anticipated", in this command's terms: the run stops at Phase 3A, before Phase 3.5, so no `test-writer` or verify has run; the branch and the baseline exist; `risk-planner` plans the rest with the diff so far; the user approves the raised plan at Phase 2B's gate; Phase 3B takes over, and its review reads the whole diff, the Phase 3A edits included. The trigger is a fact the approved plan did not state, so a user who accepted a down-classification for a plan naming the trigger is not asked again.

## Item 15 — the code pull-request body

**Shape** (D12–D14). The body answers the reviewer's four questions — what changed, how it was verified, what could break, whether it is safe to merge — in that order, with no preamble. The Review section keeps every fact §2.7 renders today; nothing is dropped.

**The door call is the agent grading its own work**, and reversibility is often invisible in a diff (rolling back a commit does not unsend a batch of messages; a flagged rollout stays two-way only until the first write lands in the new format). D14 gives a definition rather than a checklist, and points the uncertain case at `one-way`.

**The template** (D15). The repository's template wins because it is what the repository's reviewers expect, and because writing the run's own shape would delete it (`gh pr create --body-file`) or clash with it (the web UI prefill on §3.2's path). The run never removes a template section or checkbox, and never ticks a box it cannot show.

## Release

- **Changelogs and versions** per D17, each `CHANGELOG.md` section dated before it reaches `main` (check 18). Copilot: `dev-workflows/.plugin/plugin.json` and its marketplace entry.
- **Harvest record.** `docs/superpowers/harvest/NEXT.md` § *Harvest round 4* gains *Round 3 SHIPPED*: each edition's merge commit and version, backlog items 13 and 15 marked shipped, and the two follow-up candidates from the non-goals added to the backlog. Written last, after the final fix wave.
- **Installed copies.** After pushing: `claude plugin update dev-workflows@shipwright` (and any other plugin D17 bumped), then a restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

## Verification

- **Gates.** Each edition's own chain, run as one `&&` chain and read by its printed exit code.
- **Red-before, green-after.** For each retired string — *"Ask, don't guess. This rule is absolute."* in `/implement`, *"NEVER make assumptions that could have been asked"*, the docs page's *"(set at classification)"*, and §2.7's body sentence — an after-count of 0 in its stated scope; for each new rule's name — `Look, then ask`, `Re-classified upward`, `Work so far`, `partial_diff_file`, `Merge danger`, `pull_request_template.md` — an after-count of at least 1 in every file of its population. Every count states its command and scope beside the number, and runs wrap-insensitively.
- **Behaviour walk-through.** No executable surface, so the plan carries a written trace of four runs, each showing the old text's outcome against the new: a `MODERATE` direct-mode run whose exploration lists six non-test files; a `MODERATE` run that meets a migration in Phase 3A and whose user cancels the re-plan (old: ships unreviewed; new: commits through Phase 4.6 as a draft carrying the banner); a repository with `.github/pull_request_template.md` holding a checklist; and a `/vuln` run on a repository with no template.
- **Dry run.** Every edit file dry-run against all three trees and the whole round applied to throwaway copies, gates green, before the plan is written.
- **Review.** A whole-branch review per edition, fixed to zero findings, minors and nits included, before merge. Cross-edition parity checked by diffing each changed passage against this edition's, dialect aside.

## Risks

- **"Decision" against "missing evidence" is a judgement.** D2's guard is its last clause: what the evidence leaves open and the user would notice is asked, so the rule never licenses a guess on a result-changing question. The cost of a wrong call the other way is one question the repository could have answered — today's behaviour.
- **Looking costs reads in Phase 1.** D1 bounds them to what each question needs; Phase 2A/2B's exploration still runs.
- **The re-plan plans on a dirty tree.** D9 makes that explicit to the planner; the Pre-Phase 3.5 baseline predates every edit, so Phase 3B's verify still compares against a clean before.
- **New stops after files were written** are the class of text Round 2 spent most review rounds on. D10 adds the three Cancel arms to the one list `clean_finish` already cites, and rewrites the one paragraph that said Phase 2B runs before the branch exists.
- **A self-graded door call.** D14 states a definition and sends the uncertain case to `one-way`; the call is a claim the reviewer can disagree with, stated where they read it first.
- **Filling a free-form template is a judgement.** D15 never deletes a section or a checkbox and never ticks what the run cannot show, so the worst case is a section answered thinly, in the reviewer's view.
- **The Copilot shared instructions stand at 19,998 of 20,000 characters.** Any edit there trims before it adds; the plan states each instruction file's length before and after.

## Amended during planning

Every edit file was dry-run against all three trees and the whole round applied to throwaway copies (gates `EXIT=0`, `check.py` green in each) before the plan was written. Doing so found:

1. **The other two editions' Phase 4.6 carried two defects where D10 edits.** Their `"Every run"` list named the **Cancel** arm of Phase 2B's repro prompt — which runs before Pre-Phase 3 creates the branch — and that of Pre-Phase 3.5's framework prompt, which comes before the first edit, among stops "after files were written"; and it named, as "the one exit that does not reach Phase 4.6", an *"Abandon implementation and restore to pre-impl state"* arm their own Phase 3B says is no longer offered. The rewrite keeps the framework prompt's Cancel in the list, as a stop before the first edit — those editions have no rule naming a stash on a stop that skips Phase 4.6 — names the repro prompt's Cancel only on the re-plan, and replaces the Abandon sentence with *a stop before Pre-Phase 3 creates the branch is outside that set*.
2. **The other two editions' Phase 3.5 step 3 read its lint and build commands from Phase 2A's exploration**, which a run on the Phase 2B path never had (Phase 3B step 8 re-enters the step there); it takes this repository's wording. This repository's own reason there — *"where Phase 2A never ran"* — is rewritten too, since a re-planned run reaches Phase 3B having run Phase 2A's exploration.
3. **`summary_file`'s removal.** The other two editions removed it *"once Phase 2B has read it"*; the re-plan reads it again, so Phase 4.6 removes it with the run's other temp files, and a run that stops before Pre-Phase 3 removes it as it stops. `partial_diff_file` joins the removal list in all three editions.
4. **`risk-planner`'s mutation rule** said a plan is produced *"before the user has approved any action"* — false on the re-plan, where an earlier plan was approved and edits exist. It now says *"before the user has approved it"*.
5. **D8, made explicit:** every re-dispatch on the re-plan path — **Override**, **Revise**, **Help construct a repro** — carries the complete brief, its `Work so far:` line included; **Accept revised classification** resumes Phase 3A where it stopped. Phase 2B opens with a pointer: the re-plan also runs it, and Phase 3A step 5 says where each arm leads on it.
6. **D6, made explicit:** Phase 2A's write-and-re-test paragraph is skipped whole where Phase 2A was entered from an accepted down-classification — `summary_file` already holds the exploration there.
7. **Phase 2B's acceptance sentence** called accepting a down-classification the override *"of the multi-source SIGNIFICANT floor"* alone; reached from a raise, there is no floor, so it now names the floor or a raise.
8. **Docs.** The body's shape is described once per edition, in `references.md`'s entry for the code handoff; the command pages say nothing the change makes false. The workflow maps in the rules tiers name neither the clarification step nor when the class is set, and are unchanged.
9. **D17 resolved:** the population sweep found no statement of a changed claim outside `dev-workflows` in this repository, so only `dev-workflows` is bumped. The Copilot edition's instruction files are untouched (19,998 and 19,846 characters).

## Amended during review

Each whole-branch review round's findings were fixed before the next round; these change a decision above rather than its wording.

1. **D4–D6: the re-test reads the written plan.** Phase 2A still writes its exploration to `summary_file` first, but the class is re-tested on the plan it then writes — its Steps and Files to create/modify, and what the exploration found those files do — before the approval prompt and again after every **Revise**, announcing `Re-classified upward at planning`. A re-test on the file map alone missed a trigger that enters through the plan: a file the change creates, or a migration the user asks for at Revise; on this reading every trigger an approved plan states has been tested, which is what Phase 3A step 5's "did not state" exemption assumes. Skipped, as before, where Phase 2A was entered from an accepted down-classification.
2. **D2: what the run settles reaches the Phase 2B plan.** The `risk-planner` brief gains a `Settled by the run:` line, and `risk-planner` an input of that name: the facts the reading found, with where, and the open questions the run settled itself — in Phase 1, or at Phase 3A step 5 before a re-plan — the latter listed under `### Assumptions`. Phase 2A's plan cites the found facts under Approach. A question the run settles mid-implementation is recorded in the Phase 5 report's `### Assumptions & limitations`.
3. **D7–D8, the re-plan.** Its trigger excludes §1.1's last item (*Unclear requirements, large unknowns, or otherwise high blast radius*), which is a decision, and *Multi-source input*, which is Phase 1.6's. Its brief also carries every answer given at step 5's decision arm and the `pre_existing_dirty` paths, whose earlier content the plan neither reverts nor counts as this change's. **Approve** writes both plans into `plan_file` rather than replacing the first — the re-plan governing only where the two contradict, every other item in either still standing, both plans' Review focus lines included — and `test-writer`'s and `code-review`'s Plan input say so; the re-plan reads the earlier plan too and keeps its Out of scope and Assumptions unless the trigger forces a change. **Accept revised classification** records the revised class, and the trigger and its §1.1 item then count as stated.
4. **D8, a trigger after the one re-plan** is its own arm, not the decision arm, whose test it fails: announced, then `["Continue at the current class — this change ships without the review", "Stop here — the work so far is committed through Phase 4.6"]`. **Continue** records it, settles it as Accept does, and names it in the pull-request body as the reason no review ran; **Stop** is in Phase 4.6's `"Every run"` list and in Phase 4's cleanup.
5. **D11 widened:** the Phase 5 report records every change of class after Phase 1.5 — the multi-source floor, at planning, during implementation, or a down-classification accepted at plan approval or at review — with, for a raise, its trigger and paths.
6. **D12–D16, the body.** The Review section names the classification and, where no review ran, says so and why. The template ladder lists candidates through `git ls-tree -r -z | tr | grep`, so non-ASCII names are not lost; a template without headings is one section; an HTML comment is followed, then removed. §3.2 tells the user to paste the body in place of what the web UI prefills. `/vuln` and `/upgrade` bound their door facts to their research report or upgrade plan and the diff — "none of them shows it" is §2.7's one-way — and carry triage, unapplied findings and kept regressions. `/implement` keeps `plan_file` until Phase 4.6 has rendered the body from it.
7. **The user's decision: one repository per run.** `/implement` changes code only in the repository Pre-Phase 3 branches, the working directory's. Another code repository a multi-source run is given is read-only context. A change one needs:
   - is planned out of scope: Phase 2A's item 8, and the `risk-planner` brief's `Constraints:` line, which names the top level;
   - is named in the pull-request body's Summary as a companion change and weighed in Merge danger;
   - becomes a follow-up through the Phase 5 report's Session learnings, Phase 6 and the Next step, addressed to the unit itself;
   - on an early stop, is named beside the stop's §3.1 line.

   An invariant binds every writer to this, including Phase 3.5's fixes and `review-fixer`. `followup-emission` §6 and the follow-ups docs page name this kind of follow-up.

   Phase 4.6's paragraph for a repository the run wrote and never branched is gone, and so is its Phase 5 report line. `workflows-core:implementation-format` records one repository per run. Per D17's sweep, `workflows-core` therefore takes a patch, 1.11.1, and each changelog tells the user to update the other plugin with it. Review had first tried capturing every repository's diff, but that broke `test-writer`'s, `code-review`'s and `review-fixer`'s single-repository contracts; it was reverted.
8. **The user's decision: the ARD in Phase 1 (D1 widened).** On a keyed run, Phase 1 first runs Phase 1.8's ARD resolution, stopping on `unmerged`, and its look reads the ARD's rules. Phase 1.8 acts on the result, and resolves the ARD itself where Phase 1 did not.
9. **The user's decision: a unit commit that does not land ends `code-handoff` §2.12's split.** "Does not land" covers three cases:
   - a hook rejects the commit;
   - git fails to write it, as on a signing failure;
   - §2.2's `git add` is refused, as on a held lock, which leaves the changes in the working tree rather than staged.
   - `/upgrade` step 6.5 stops its loop there, and later components do not run.
   - The terminal call stages nothing at §2.2. It goes on at §2.4 where an earlier unit committed, and otherwise ends on the *Commit rejected by a hook* row.
   - §2.9 lists the case, so any pull request is a draft.
   - A §3.1 append row names the unit. The *Commit rejected* row, renamed from *Commit rejected by a hook*, says who rejected the commit and where the changes are.
   - `/upgrade`'s pull-request body covers only the components that committed, as its title does.
10. **D12, D16: the title.** §2.7's title is the commit subject, or on a §2.12 terminal call the caller's `title`:
    - `/vuln`'s title is the subject §2.3 writes from the template, version included.
    - `/upgrade`'s title is step 6.5's subject for one component, or `upgrade <first> and <N> more [<key>]` over the components it committed.

    This fixes a contradiction older than this branch, in all three editions.
11. **D12, Review.** The body's Review section and the Phase 5 report's Deferred items carry a `MAJOR` or `BLOCKER` that `review-fixer` deferred. Both had dropped it before this branch.
12. **§2.11's `repo` is the work tree's top level**, resolved with `git rev-parse --show-toplevel`. §2.7's template listing takes `--full-tree`, and the blast-radius greps take the `:/` pathspec. Before this branch, a run from a subdirectory missed root files, and §2.2's carve-out failed on root-relative paths.
13. **D10 widened:** the **Cancel** arm of Phase 3B step 7's re-classification prompt joins Phase 4.6's `"Every run"` list in all three editions. Before this branch, that stop was left undefined.
14. **D8's capture and every root, at the top of the work tree.** Every diff this round's commands capture runs `git add -N :/ && git diff`; `/vuln`'s and `/upgrade`'s captures and `test-writer`'s input change the same way. Before this, `git add -N .` from a subdirectory marked only that directory's untracked files, so new files elsewhere never reached `test-writer` or `code-review`. By the user's decision, every root follows the diff: `/implement`'s test baseline, and every root that `/implement`, `/vuln` and `/upgrade` pass to an agent, is the repository's top level. Several things follow from it:
    - the test-command prompts of all three commands say so;
    - Phase 3.5 runs lint and build from the directory the exploration found them in, in a subshell by absolute path;
    - the working directory, where it lies below the top level, is a place for exploration and the scan to start;
    - `risk-planner` runs its commands from the top level;
    - `code-scanner`, the explorer, Phase 4's agents and the maintenance handoffs take the top level too. A monorepo run started from one service's directory therefore baselines and verifies every suite.
15. **D17 widened.** `workflows-core` 1.11.1 also fixes `followup-emission` §8. That section, `/implement`, `/ready`, `/epics`, `/prd-proposal`, `/brd-proposal`, `/document` and `/release-notes` named §4 for the follow-up target ladder, which is §2. So `product-workflows` takes a patch (3.12.1) and `docs-workflows` takes a patch (1.5.1). Every new changelog section is dated 2026-10-04, the day it reaches `main`.
16. **The companion change reaches review.** `code-review`'s brief carries a `Deferred to another code repository` line, and `code-review` defines that input. A new paragraph in Phase 3B step 7, *Another code repository's findings*, runs after triage on every review and re-review. It records each survivor whose fix lies in another code repository as Phase 3B step 2 says, and no fixer receives it.
    - Such a finding is a fourth class of unapplied finding, in the body and in Deferred items.
    - A `BLOCKER` among those findings leaves the review blocked, whatever else survives. The stop names every other survivor, and a fifth unapplied class carries them: a survivor of a review that stopped before any fixer ran.
    - On the first review, if nothing that needs a fix is left, no fixer is dispatched. A `PASS WITH RECOMMENDATIONS` continues. A `BLOCK` asks `finding-triage`'s first settle prompt.
    - `followup-emission` §6's exclusion of deferred `BLOCKER`s spares such a finding.
17. **Phase 1.6 counts distinct repositories, at every copy of the multi-source floor.** This covers `classification` §1.1, the docs and the rules tiers; they also name folder inputs rather than "any directory input". `repo_count` counts by top level, so an `@path` inside a repository already counted adds none. Before this, such a path set off the multi-source floor and a second scan of the same repository. Phase 1.7 now scans each repository once. An inner `@path` is a search hint, relative to the top level, for that scan and for the Phase 2A/2B explorer.
18. **Pre-existing, fixed: the *Stash* answer at `/implement`'s and `/upgrade`'s dirty-tree prompt.**
    - It stashes tracked changes, and `/implement` leaves the run's own `@path` inputs in place.
    - It records every path it leaves dirty as `pre_existing_dirty`, which keeps that path out of the commit unless the run edits it.
    - A stash git refuses stops the run before anything is branched. `stash_ref` is set only where git made a stash.
    - Before this, untracked files stayed in the tree unrecorded, and the commit swept them in.
    - The run's own files changed (the `--stat` paths, less any untouched pre-existing path) are defined once, at Phase 4 step a.
19. **A plan with no step in this repository.** Such a plan is one written before any edit (Phase 2A's, or Phase 2B's at its full-plan gate after the repro branch; never the re-plan) whose Steps change no file in this repository.
    - Its own question replaces the approval question: *Stop here, nothing written* (Recommended), or *Revise plan*. Every **Revise** and re-dispatch handles its return through every arm.
    - **Stop** names one follow-up per other repository and stops as **Cancel** does, with nothing written.
    - The follow-up for another repository is keyed by that repository, named by its origin slug, and by the unit. Its action is one run from there.
    - Every stop after the plan names the companion changes.
    - Step 7.5 annotates only a spec in `$SPECS_PATH` or in this repository. A note in this repository is committed with the code, and Phase 4.5 hands off only the notes in `$SPECS_PATH`.
    - `finding-triage`'s *stayed blocked*, its rules-tier copy and `code-handoff` §2.9 admit a first review's `BLOCKER` whose fix lies in another code repository.
20. **Phase 0's classification.** The rows are tested top to bottom, and the first match wins.
    - The working directory, inside a work tree, and any directory at a work tree's top level are always code repositories.
    - A working directory outside every work tree stops the run.
    - A top-level spec folder read as a code repository is announced, with the remedy of naming its spec files directly.
21. **The user's decision (2026-10-04) on finishing the review loop.** From round 30, a finding in the branch's own items or decisions is fixed. A finding in one of four pre-existing areas goes to the NEXT.md follow-up backlog, each one named:
    - the *Stash* answer;
    - Phase 0's classification order;
    - follow-up dedupe keys;
    - subdirectory roots.
22. **Pre-existing, fixed: the code commit and the review diffs (rounds 32–40).**
    - Every diff capture is `git add -N --ignore-removal :/ && git -c diff.relative=false diff --no-ext-diff --no-color <HEAD, or the empty tree before a first commit>`. Before, a deletion was staged out of the diff's sight, and a user's diff configuration could alter the capture.
    - `code-handoff` §2.2's carve-out 1 commits its enumerated paths as one pathspec commit. It never stages the index first, so a user's staged change stays out.
      - Each path is named `:(literal)<path>`, never through the global flag a commit hook would inherit.
      - It drops an intent-to-add entry the run created and removed again.
      - After the commit it brings the index back in step with `git restore --staged`.
    - *Nothing to commit* is defined on both of §2.2's paths, and the commit never runs with an empty path list.
    - The clean-tree test lists untracked files whatever the user's configuration. The prompt shows them with each directory on one line.
    - §2.7 item 1 reads the pull request's file list from git, and names commits on the branch the run did not make.
23. **`finding-triage` and `next-phase-offer` follow `/implement`'s other-repository rules.**
    - `finding-triage`: on a first-review `BLOCK`, survivors kept from the fixer, none of them a `BLOCKER`, that leave no `BLOCKER` or `MAJOR` for it, ask the first settle prompt.
    - `next-phase-offer`: the routing graph and its rule 5 name the run from another repository, addressed to the Epic itself, first.
24. **The user's decision (2026-10-04, after round 40): the commit-and-staging area joins the filed areas.** From round 41, a finding there goes to the NEXT.md backlog.

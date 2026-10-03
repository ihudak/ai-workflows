# Upstream harvest round 4 — Round 2: the review pipeline

Date: 2026-10-02. Status: design approved in conversation; spec awaiting review. Branch: `iv-gu/harvest-r4-review` in all three editions.

## Background

Round 1 of harvest round 4 (`docs/superpowers/specs/2026-10-02-harvest-round-4-defects-design.md`, shipped) fixed six defects in shipped text and recorded items 7–21 of the survey as backlog in `docs/superpowers/harvest/NEXT.md`. This round takes items 7–12 — the six that change how a review's findings travel from an Opus reviewer, through the orchestrator's triage, to a fixer and back — plus one defect found while reading them (item 13).

The three editions are as in Round 1: **this repository** (canonical — `workflows-core`, `dev-workflows`, `product-workflows`, `docs-workflows`), **the internal edition** (one `plugins/dev-workflows` plugin) and **the Copilot edition** (`ihudak-copilot-plugins`: `dev-workflows/skills/<name>/SKILL.md`, `skills/_shared/`, `agents/`). Paths are relative to each edition's repository root; a path written for this edition maps onto the other two as Round 1's spec describes (`plugins/workflows-core/references/<n>.md` → `plugins/dev-workflows/references/<n>.md` → `dev-workflows/skills/_shared/<n>.md`; a command → a skill).

**Triage callers per edition** (`grep -l finding-triage` over the command or skill files): this edition — `/implement`, `/vuln`, `/upgrade`, `/document`, `/epics`, `/prd-proposal`, `/brd-proposal`, `/docs-init`, `/docs-brand`, `/docs-audit`; the internal and Copilot editions — `implement`, `vuln`, `upgrade`, `document`, `epics`.

### What is wrong today

1. **A serious claim triage cannot settle vanishes.** `finding-triage` step 2 dismisses "claims it could not substantiate". A `BLOCKER` the orchestrator could neither confirm nor refute is dropped with a reason, and reaches the user as a dismissal.
2. **A re-review can stop the run on a `BLOCKER` triage already refuted.** The second review is not triaged at all (`/implement` step 7's triage sub-step runs "before any fixer dispatch", and none follows a re-review), and every caller's stop reads the verdict word — "If the second verdict is still BLOCK, stop". A reviewer that re-raises the finding triage dismissed stops the run on it. `finding-triage` admits the re-raise for the proposal commands and states no rule for it.
3. **A finding the spec is silent on is graded by the spec, not by its effect.** `code-review` has no severity rule outside dimensions 9–11; a crash on an input the spec never mentions can be filed `MINOR`, and `MINOR` is deferred. Triage can only dismiss, never raise a grade, and the reviewer has no place to say what it set aside.
4. **No input class the plan implies is pinned before review.** Neither `risk-planner`'s plan nor `/implement`'s Phase 2A plan names the inputs no step's tests exercise, so `test-writer` and `code-review` dimension 4 hunt for them from scratch.
5. **Dimension 4 misses four edge-case classes** an upstream reviewer prompt checks mechanically: the unnamed members of a fixed value set, a re-check of something already held, a call that disagrees with its callee's declaration, and removed code whose contract nothing replaced.
6. **"A documented standard overrides" with no rule for finding one.** `code-review` dimension 3 defers to a documented standard and never says where to look — a pointer whose trigger the reviewer must judge (`workflows-core:instruction-file-maintenance` §3).
7. **(item 13) Seven commands cite an escalation rule that does not exist.** `/create-prd`, `/update-prd`, `/create-ard`, `/prd-proposal` and `/brd-proposal` escalate "per the `Review verdict BLOCK` rule" — `escalation-rules` has only the `— /document` and `— /epics` variants. `/design` cites the `— /epics` variant, whose "Defer" appends a refinement note to the draft — into a `design.md` its own Phase 7 then refuses to hand off while an item in it is open (`/specify` cites the same variant on purpose; § Amended during planning, 2). The internal and Copilot editions carry the same gap in `create-vi`, `update-vi` and `create-ard`, and the same `/epics` citation in `design`.

## Goals

1. Each of the seven failures above is unreachable in every edition that carries the affected file.
2. Every statement of each changed claim is found and rewritten — the whole population, the `docs/` pages and the instruction tiers included (`CLAUDE.md` § Editing discipline, refinements 4, 6 and 8).
3. Every check is shown red on the pre-change tree and green after it.
4. No new review cycle: the cap stays one fix cycle plus one re-review wherever a caller has one, and `/docs-init`, `/docs-brand` and `/docs-audit` still run no re-review.

## Non-goals

- **BMAD's severity reset.** BMAD discards every reviewer severity because its reviewers lack context; ours are Opus with the plan, the diff and the code. Reviewer grades stand, raised only by item 9's rule.
- **BMAD's follow-up review recommendation.** Our re-review after a `BLOCK` fix cycle is already automatic and capped.
- **Grouping findings by root cause.** Triage stays per finding ("before any grouping or deduplication").
- Rejected again from the survey: a review-depth switch, a finding floor by diff size, verifying a fix by test instead of re-review.
- **Triage for the inline-fix authoring commands** (`/create-prd`, `/update-prd`, `/create-ard`, `/specify`, `/design`). Item 13 fixes their escalation pointer; it does not attach `finding-triage` to them.
- `references/specification-format.md` (frozen).

## Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | The third triage outcome (item 7) | **`unverified`** — verification could not tell whether the claimed consequence occurs, and the finding would be `MAJOR` or `BLOCKER` if true. Recorded at that grade marked `(unverified)`, with what would settle it. Never handed to a fixer; changes neither the verdict nor `clean_finish`. A finding that would be only `MINOR` or `NIT` if true is dismissed with the same note |
| D2 | When "could not tell" is allowed | Only where the diff and the surrounding code leave the question open; where they are enough to decide, the finding is kept or dismissed. "No path to the claimed consequence at the named site" stays a **dismissal** — it is a refutation, checked, not a failure to check |
| D3 | Patch gate on instruction files (item 7) | A fix that would edit a file telling agents or contributors how to work in the repository — `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md`, a file under `.claude/rules/` or `.github/instructions/`, `CONTRIBUTING.md`, `CODING_STANDARDS.md` — **that the change under review did not itself edit** is surfaced for a human decision, never patched. The same list in all three editions |
| D4 | Triage accounting (item 7) | Per review pass: survived + unverified + dismissed = findings reviewed. A finding in none of the three is a triage failure |
| D5 | Which reviews are re-reviews (item 8) | Every review a run dispatches after a fix cycle or an orchestrator edit over the same artifact — the capped re-review, a re-review the user chose at the emptied-set prompt, and `/implement` Phase 3B step 8's review of the Phase 3.5 delta |
| D6 | A re-raised finding (item 8) | Same code site (line numbers may have moved) and same claim as a row this run already logged, and the code there still reads as the row describes → keeps the row's outcome, marked `carried`; not verified again, never handed to a fixer again. A row whose fix changed the code no longer matches and is verified afresh |
| D7 | A re-review's survivors (item 8) | Never handed to a fixer — the cap is reached. Each is recorded in the triage line at its own severity |
| D8 | The second-verdict stop (item 8) | Acts on a **`BLOCKER` that survives the re-review's triage**, never on the verdict word. Where the second verdict is `BLOCK` and none survives, the verdict is one its own findings no longer support, and the user settles it with `["Proceed — no BLOCKER survived triage, and every disposition is recorded (Recommended)", "Keep the verdict and stop for a human decision", "Cancel"]`. **Refinement of the in-chat design:** the emptied-set prompt's re-review arm is not offered here, because this *is* the re-review the cap allows. *Keep the verdict* takes the caller's existing second-`BLOCK` path, over the `BLOCKER`s the reviewer raised |
| D9 | Severity by effect (item 9) | `code-review`: where no dimension fixes a grade, a finding's severity is what a reasonable person using the software meets if the change ships as it stands; the spec's, plan's or task's silence on the triggering input is not permission. Dimension 3's fixed `MINOR`/`NIT`, 9's, 10's and 11's own rules still govern |
| D10 | Triage may raise a grade (item 9) | Upward only, by effect, and to `MAJOR` at most — a `BLOCKER` changes the verdict, which triage does not restate. An unverified finding is recorded at the reviewer's grade raised by the same rule. Every raise is recorded with its reason |
| D11 | "Declined to judge" (item 9) | `code-review` returns a `### Declined to judge` section: every behaviour it considered and set aside as outside the plan, the spec or the task, one line each with the reason, or `none`. The orchestrator rules on each line: it **stands** (recorded with why), or it is a **defect** — recorded with its effect grade and what shows it. Never patched automatically |
| D12 | Review focus (item 10) | A `### Review focus` section in `risk-planner`'s plan and a ninth item in `/implement`'s Phase 2A plan: up to five input classes or failure modes the task implies and no step's tests exercise, most likely to bite first, each with the behaviour a reasonable user would expect — or `none — checked`. `test-writer` writes a test per line or names the line in `### Notes` with why not; `code-review` dimension 4 checks each line deliberately |
| D13 | Dimension 4's new checks (item 11) | Implicit branches; handle lifetime; call against declaration (tests included); removed contracts. In `code-review` dimension 4 and in `model-routing/classification` §6 item 4, the fallback reviewer's copy of the checklist |
| D14 | Where `code-review` finds standards (item 12) | Before dimension 3: `CLAUDE.md` and `AGENTS.md` at the project root and in every directory between it and a changed file; `CONTRIBUTING.md` at the root, in `.github/` or in `docs/`; `CODING_STANDARDS.md` at the root; and every file under `.claude/rules/` whose `paths:` matches a changed file or which has no `paths:`. The Copilot edition reads `.github/copilot-instructions.md` and every `.github/instructions/*.instructions.md` whose `applyTo:` matches a changed file, in place of `.claude/rules/`. A rule the repository's own lint, format or type-check configuration already enforces is that tool's to report |
| D15 | Item 13's fix | One new heading, `## Review verdict BLOCK (unresolved after one fix cycle) — commands that fix inline`, carrying `["Provide manual fix notes (you'll be prompted)", "Defer to a follow-up issue (record in the final report)", "Override and accept the finding", "Cancel the whole run"]` and its four resolutions; every command that fixes its reviewer's findings inline and defines no "Defer" of its own cites it. `/create-prd`'s inline copy of its array is rewritten to match it verbatim |
| D16 | Versions | New behaviour → minor. This edition: `workflows-core` 1.11.0, `dev-workflows` 4.6.0, `product-workflows` 3.12.0, `docs-workflows` 1.5.0. Internal edition `dev-workflows` 2.67.0. Copilot edition `dev-workflows` 2.36.0 |
| D17 | Order and landing | As Round 1: this edition, then the internal edition, then the Copilot edition (hand-adapted, never `cp`). Each: gates green, a whole-branch review to zero findings, then merge, push, delete the branch |

## Item 7 — triage gets a third outcome

**Source.** BMAD `3433612d`, `b0d27c3c` — `skills/bmad-code-review/step-03-triage.md`, `skills/bmad-build-auto/step-04-review.md`: the `maybe-false` verdict, deferred when serious if true; fixes to agent-context files deferred; the triage log's row count equal to the findings reported.

**Change — `finding-triage` (all three editions).**

- **§ The step, step 2** becomes *Keep, mark unverified, or dismiss* (D1, D2). The rule that a dismissal "must dispose of that finding's own claim" stays and is reworded for three outcomes: a true fact about neighbouring code that leaves the claim standing settles nothing — the finding is kept where verification confirmed it, and is otherwise one verification could not settle.
- **Step 3** records every dismissal **and every unverified finding**, each with its reason; "never drop a finding silently" stands.
- **"Only survivors are handed to the fixer"** stands; it now also excludes unverified findings, and the sentence says so.
- **§ When triage empties the survivor set** — the trigger is unchanged ("every finding behind a non-`PASS` verdict" now reads "dismissed or unverified"), and what step 3 surfaces gains every unverified finding with what would settle it.
- **§ The patch gate** gains D3's clause, with its reason: item 12 makes the reviewer read those files, so a finding that the change contradicts one of them becomes likely, and editing the file to agree with the code is the fix that makes such a finding go away.
- **§ Reporting** is rewritten as the authority for the triage line (D4): per review pass, findings reviewed and how many survived, are unverified and were dismissed (and, on a re-review, how many were carried); every dismissal with its reason; every unverified finding with its if-true grade and what would settle it; every raise (D10); and, where the review carried one, each Declined-to-judge line with its ruling (D11).

**Callers.** Every triage caller's report template takes the new line. Code callers (`/implement`, `/vuln`, `/upgrade`):

`- **Review triage:** [one line per review pass — N findings reviewed: M survived, U unverified, X dismissed (C carried, on a re-review)] — dismissals: [...] — unverified: [`finding — if-true severity — what would settle it`, or "none"] — raised: [`finding — from → to — effect`, or "none"] — set aside by the reviewer: [`behaviour — ruling`, or "none"]`

`/document` and `/epics` take the same line without the last field; the prose report descriptions (`/prd-proposal`, `/brd-proposal`, `/docs-init`, `/docs-brand`, `/docs-audit`) cite `finding-triage` § Reporting instead of restating it. Each caller's one-sentence summary of the triage step ("verify …; keep or dismiss; record every dismissal …") is rewritten for three outcomes.

**Population** (refinement 8) — every statement of the outcome set or the patch gate, in each edition: `finding-triage` itself; every triage caller's triage sentence and report template; `review-fixer` and `doc-fixer` (each restates the patch gate); `docs-scaffold-reviewer`, `docs-audit-reviewer` and `proposal-reviewer` (each states what its caller's triage does — `proposal-reviewer`'s "keep or dismiss" verbatim); `model-routing/classification` §6 ("a disposition is either a fix or a dismissal"); the `docs/` pages that describe the step (the command pages of every caller, and the references pages); and the instruction tiers — here `.claude/rules/workflows-core.md`, `dev-workflows.md` and `docs-workflows.md`; in the internal edition `.claude/rules/dev-workflows-code.md` and `dev-workflows-docs.md`; in the Copilot edition `.github/instructions/dev-workflows-shared.instructions.md` and `dev-workflows-skill-map.instructions.md`, each kept under 20,000 characters (both are within 200 of it today, so every edit there is length-neutral). The plan enumerates the sites per file, by phrase.

## Item 8 — a re-review keeps earlier rulings

**Source.** BMAD `7c3e5827` (`step-04-review.md`: a finding matching a logged row keeps its verdict and route, is written again `carried`, and is never patched or deferred again), `85d968fc` (the follow-up pass).

**Change — `finding-triage` gains `## On re-review`** (all three editions): D5's scope, D6's matching rule, D7's disposal of survivors, and D8's settle prompt with the reason it has no re-review arm. It names each caller's existing second-`BLOCK` path as what *Keep the verdict* takes, by citation rather than restatement. The paragraph that says `/prd-proposal`'s and `/brd-proposal`'s re-review "can re-raise a finding triage dropped" is rewritten to point at the new section. The "partly emptied set" paragraph is scoped to the first review, since on a re-review D8 decides instead.

**Callers.** Each caller's second-verdict sentence becomes: triage the re-review per `finding-triage` § On re-review; if a `BLOCKER` survives it, take the existing stop or escalation; otherwise § On re-review's prompt settles the verdict. The sites, in this edition: `/implement` Phase 3B step 7 (and step 8's delta review, which has no verdict handling today — D5 gives it this one), `/vuln` Step 3, `/upgrade` step 4, `/document` Phase 7, `/epics` Phase 7, `/prd-proposal` and `/brd-proposal` triage step 3; in the other two editions, the same sites of their five callers.

**Population** — every statement of the stop's trigger, by its subject (the stop after the one re-review), rewritten to D8's noun, *a `BLOCKER` surviving the re-review's triage*: in `/implement`, the stop itself, Phase 4's cleanup list, Phase 4.6's `"Every run"` list and `clean_finish` row (including its arithmetic about *a second verdict still `BLOCK`*), the `### Next step` placeholder, and the invariants line; `/vuln`'s and `/upgrade`'s loop-exit lists; `dev-workflows:code-handoff` §2.9's `clean_finish` list ("still `BLOCK` after its single allowed fix cycle plus re-review"); `escalation-rules`' `— /document` and `— /epics` entries ("returns BLOCK a second time"); the `docs/` command pages; and the instruction tiers. The plan enumerates each by phrase, in each edition.

## Item 9 — severity by effect, and "Declined to judge"

**Source.** superpowers `5bf4e780` (#2319): `skills/requesting-code-review/code-reviewer.md` (*The spec is a vision document*; *Declined to judge*) and `skills/executing-plans/SKILL.md` (*Re-grade first, by effect*).

**Change.**

- **`code-review`** (all three editions): `## Review method` step 4 gains D9's grading rule; a new step before the verdict collects the Declined-to-judge list; `## Output` gains `### Declined to judge` after `### Findings`; `## Hard rules` gains "NEVER set a behaviour aside silently — it goes in `### Declined to judge`". The down-classification return and the `Diff: unreadable` return carry no such section, and the template says so.
- **`finding-triage`** (all three editions): § The step gains D10's raise and D11's ruling, both recorded per § Reporting.
- **`/implement`'s `PASS WITH RECOMMENDATIONS` arm** ("MINOR / NIT findings may be deferred") is unchanged in text: a raised finding is `MAJOR` and reaches the fixer by the arm's own first clause.

## Item 10 — a "Review focus" section in the plan

**Source.** superpowers `5bf4e780` (#2319): `skills/writing-plans/SKILL.md` § Review Focus and self-review step 4.

**Change.**

- **`risk-planner`** (all three editions): `### Review focus` in the output template, after `### Acceptance checks`, with D12's content; a `## Planning discipline` bullet saying how to choose the lines (from the spec, the task and the code the steps touch; most likely to bite first; an empty list means checked, not skipped). The proportion check (Round 1) measures `### Steps` only, and the bullet says the new section is not measured against the change either.
- **`/implement` Phase 2A** (all three editions): a ninth plan item, **Review focus**, with the same content.
- **`test-writer`** step 3 (all three editions): where the plan carries a Review focus section, each line is a behaviour to cover — write the test that pins it under step 5's rules, or name the line in `### Notes` with why it cannot be tested in isolation.
- **`code-review`** dimension 4 (all three editions): where the plan carries a Review focus section, check each line deliberately and report a finding for each one the change does not handle.
- **Population** — `references/handoff/` files that describe `risk-planner`'s output or `test-writer`'s inputs, and the `docs/` pages that list the plan's sections, swept by subject.

## Item 11 — four edge-case checks in dimension 4

**Source.** BMAD `44e0f806`: `skills/bmad-code-review/review-prompts/edge-case-hunter.md` (implicit branches, handle lifetime, call against declaration) and `references/deletion-check.md`.

**Change — `code-review` dimension 4** (all three editions), after the missing-adoption gap:

1. **Implicit branches** — where the change special-cases some members of a fixed value set (enum values, status codes, sentinels, type tags, flags, value ranges), the members it does not name are branches too: say what each one meets.
2. **Handle lifetime** — where the changed code re-checks, re-fetches or re-validates something it already holds (a handle, an index, an id, a pointer), name the intervening call that can invalidate it, what that call does to it, and what the code skips when the re-check fails.
3. **Call against declaration** — at every call site the diff adds or changes, tests included, read the callee's declaration and check argument count, order, types and defaults.
4. **Removed contracts** — for code the diff removes or replaces (not a pure rename or whitespace), did it carry a behaviour or a contract the change neither re-establishes nor intentionally retires? A regression, an orphaned reference or newly dead code is a finding.

`model-routing/classification` §6 item 4 gains the four in one clause (D13).

## Item 12 — `code-review` finds the repository's documented standards

**Source.** BMAD `23f134e2` (`skills/bmad-code-review/customize.toml`: read the agent instruction files at the root and in the directories the diff touches); mattpocock `skills/engineering/code-review/SKILL.md` step 3 (standards sources; skip what tooling enforces).

**Change — `code-review` dimension 3** (all three editions): opens with D14's discovery rule, and "a documented standard overrides this list" becomes "a standard documented in one of those files overrides this list". Placed in the dimension rather than as a new `## Review method` step, because the claims-file input cites `## Review method` step 3 by number.

## Item 13 — the missing escalation heading

**Change — `escalation-rules`** (all three editions): D15's heading, placed before the `— /document` entry, naming its callers and saying `Escalate per unresolved BLOCKER individually`.

**Callers.** This edition: `/create-prd`, `/update-prd`, `/create-ard`, `/prd-proposal`, `/brd-proposal` (citing the bare `Review verdict BLOCK`), `/design` (citing `— /epics`). Internal and Copilot editions: `create-vi`, `update-vi`, `create-ard`, `design`. `/specify` is not a caller (§ Amended during planning, 2). Each cites the new heading by its full name. The `docs/` pages that paraphrase the escalation (`create-prd`, `update-prd`, `create-vi`, `update-vi` and the rest found by the sweep) are checked against it.

## Release

- **Changelogs and versions** per D16, each `CHANGELOG.md` section dated before it reaches `main` (check 18). Copilot: `dev-workflows/.plugin/plugin.json` and its marketplace entry.
- **Harvest record.** `docs/superpowers/harvest/NEXT.md` § *Harvest round 4* gains *Round 2 SHIPPED*: each edition's merge commit and version, items 7–12 and 13 marked shipped, and the non-goals above recorded as divergences. Written last, after the final fix wave.
- **Installed copies.** After pushing: `claude plugin update` for `workflows-core`, `dev-workflows`, `product-workflows` and `docs-workflows` `@shipwright`, then a restart; `copilot plugin update dev-workflows@ihudak-copilot-plugins`; the internal edition wherever it is installed.

## Verification

- **Gates.** Each edition's own chain, run as one `&&` chain and read by its printed exit code.
- **Red-before, green-after.** Per item: a grep for the retired string (`could not substantiate`, `keep or dismiss`, `If the second verdict is still BLOCK`, `the \`Review verdict BLOCK\` rule`, `a documented standard **overrides**`) with an after-count of 0 in its stated scope; and a grep for each new rule's name (`unverified`, `## On re-review`, `### Declined to judge`, `### Review focus`, `Handle lifetime`, `CODING_STANDARDS.md`, `— commands that fix inline`) with an after-count of at least 1 in every file of its population. Every count states its command and scope beside the number, and runs wrap-insensitively.
- **Behaviour walk-through.** Item 8 has no executable surface, so the plan carries a written trace of three runs through `/implement` step 7 — a re-raised dismissed `BLOCKER` alone, a re-raised dismissed `BLOCKER` beside a new `MINOR`, and a fix that did not change the code — each showing the old text's outcome (stop, stop, stop) against the new (settle prompt, settle prompt, stop).
- **Review.** A whole-branch review per edition, fixed to zero findings, minors and nits included, before merge. Cross-edition parity checked by diffing each changed passage against this edition's, dialect aside.

## Risks

- **The re-review match (D6) is a judgement.** "Same claim" across two reviews is not a string match. The rule's guard is its last clause — the code must still read as the row describes — so a fix that changed the code always forces fresh verification, and the only cost of a false match is a finding carried at the disposition it already had.
- **The `unverified` outcome could become a place to park hard findings.** D2 is the guard, and § Reporting puts every unverified finding in front of the user with what would settle it, so parking one is visible.
- **The Declined-to-judge list adds output** to every `code-review` return. It is one line per set-aside behaviour, `none` when empty.
- **The Copilot instruction files sit within 200 characters of their 20,000 limit.** Any edit there must be length-neutral; the plan states each file's before and after length.
- **Item 12 adds reads** to every `code-review` run — at most two files per directory on the path to each changed file, plus the root files and the matching rules files.

## Amended during planning

Each edit was proven before the plan was written — applied to a throwaway copy of every edition, gated (`EXIT=0` in all three), and checked red before and green after. Reading the sites closely changed six things:

1. **The stop has one name: the review *stayed blocked*.** D8's noun, *a `BLOCKER` surviving the re-review's triage*, names one of the two ways the stop is reached; the user keeping the verdict at § On re-review's prompt is the other. `finding-triage` § On re-review defines **stayed blocked** as either, and every caller and every statement of the stop uses that noun.
2. **Item 13 leaves `/specify` alone, in all three editions.** It cites the `— /epics` rule on purpose: its own text defines "Defer" as a `## Refinement notes` section in `specification.md` that "mirrors `/epics`' Epic-refinement note". `/design` defines no "Defer", and its Phase 7 refuses to hand off a `design.md` with an open `- [ ]`, so the `/epics` meaning is wrong there — `/design` moves to the new heading, `/specify` does not. The new heading's callers are the commands that fix inline **and define no "Defer" of their own**.
3. **`/implement`'s early-stop lists name both settle prompts' stopping arms.** The first-review prompt's *Keep the verdict* and *Cancel* were already stops after files were written that no list named, so neither committed the work; the entry that names the re-review prompt's arms names both prompts' (the Phase 4 cleanup list and Phase 4.6's `"Every run"` paragraph, whose history note about *six of seven* is rewritten as history).
4. **The Copilot edition's new escalation array ends with `"Other… (describe)"`**, as that edition's `escalation-rules` asks of every array; the other two editions' carries four options, as theirs asks.
5. **The population was wider than the spec listed** in three places, all in the plan: `/upgrade`'s `clean_finish` sentence (*"or with a review still `BLOCK`"*), the Copilot edition's `implement:` docs page (which said an unresolved BLOCKER "is escalated individually" — `implement:` stops), and `docs-audit-reviewer` (*"a second copy of its three steps"* — the reference no longer has three).
6. **`finding-triage`'s first-review section is scoped**: it now says it governs the first review and that § On re-review settles a re-review's verdict, and both prompts are named the reference's *settle prompts* so callers can cite them.

## Amended during review

1. **D9 names a finding whose effect falls on the people who maintain or operate the software** (approved by the user on 2026-10-03, after review round 18). D9 grades by what a reasonable person *using* the software meets, and read literally that could grade a violated documented standard, a missing test or a missing rollback path at `MINOR` or `NIT` — below the fixer's `BLOCKER`/`MAJOR` floor — since a user meets none of them on the day the change ships. `code-review` now grades such a finding by the worse of what those people meet and the failure its gap lets reach users, in the same sentence as the general rule, so the two cannot be read as competing rules. Triage's raise (D10) is unchanged: it only raises, so a narrow reading of it costs a raise, never a grade.
2. **D14's directories are those on a changed file's path** (review round 22). "Every directory between it and a changed file" could be read as leaving out the file's own directory; `code-review` now says "every directory on a changed file's path", as the changelogs already did. No design change.

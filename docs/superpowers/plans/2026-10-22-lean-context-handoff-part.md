# Lean context D Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A consumer's Phase-0 `require-on-main` reads its own generated part of `phase-handoff` (about half the file, §2.2 included) instead of the whole file. Every command that presents a choice list loads `escalation-rules core` as a step of its own before its first question. A fail-closed gate holds both.

**Architecture:** `scripts/reference-parts.py` gains a second, narrower mechanism beside part 1's split rulebooks: an **entry-point file**. A declaration in an unsplit reference names one entry point and the sections it needs. Region markers select those lines, and `generate` writes them, in source order, to `plugins/workflows-core/reference-parts/<ref>/<entry>.md`. No rule index and no citation placement are involved: every other request, and every citation, still means the whole file. The loader skill names the one entry-point file. `check-citations` gains two checks: an out-of-part citation inside a check section, and a missing question-rules load step.

**Tech Stack:** Markdown prose that agents execute literally; Python 3 (`scripts/reference-parts.py`, its fixture-tree selftest under `scripts/fixtures/reference-parts/`); the repository gate chain (`.github/workflows/validate-catalog.yml`).

**Spec:** `docs/superpowers/specs/2026-10-22-lean-context-handoff-part-design.md`

## Global Constraints

- Quality first, within reason: "keeping the quality above the costs (as long as it's reasonable)". No split without a reason and a better outcome.
- Nothing a run does changes, beyond loading the question rules where it did not before (spec, Goal 3).
- The source stays one file, `plugins/workflows-core/references/phase-handoff.md`. Checks 11, 16 and 20 keep passing unchanged in what they enforce.
- Only `args: "phase-handoff require-on-main"` changes what it reads. `args: "phase-handoff"`, `args: "phase-handoff handoff-to-main"` and every citation of `phase-handoff` read the whole source, as today.
- `require-on-main` looks up its `specs-repo-git` rules (§3.1, §3.2, §3.3, §8) and `read-only-repos` from any read made in this run. It loads `specs-repo-git` whole only where no read of it is in the conversation, which is today's behaviour.
- §3.4 stays whole in the entry-point file.
- A generated file is never edited by hand: edit the source and run `python3 scripts/reference-parts.py generate`.
- Prose is executed. Re-read every moved sentence where it lands, for both faces of `CLAUDE.md` § Editing discipline's *A sentence is true in the context it was written in*. Run the claim sweep (`.claude/rules/claim-sweep.md`) on every claim that a request on a reference that does not load by part reads the whole file, or that `require-on-main` reads all of `phase-handoff`. Part 1's verification record is history and is not edited.
- Versions:
  - workflows-core 1.44.0 → 1.45.0
  - dev-workflows 4.30.1 → 4.31.0
  - product-workflows 3.35.0 → 3.36.0
  - docs-workflows 1.17.0 → 1.18.0
  - security-workflows 0.2.0 → 0.3.0

  Each gets a `## [x.y.z] — Unreleased` section, dated at the merge.
- Never name the organisation this plugin was extracted from (check 14). No tracker name under `plugins/` without a `vendor-token-ok` marker (check 13). Requirement IDs keep the `[PREFIX#N]` form.
- Run the gates as one chain:
  - **Per task:** `bash ~/e2e-live/lean-context-part1/gates-unreleased.sh <worktree>`, which must print `EXIT=0`.
  - **At the merge:** `bash ~/e2e-live/lean-context-part1/gates.sh <worktree>`, which runs with `ASSERT_PUBLISHED=1`.
- Git:
  - Run `git branch --show-current` and confirm `iv-gu/lean-context-handoff-part` before every commit.
  - Never `git checkout` in `/workspace/ai-workflows`, and never use a bare `git stash`.
  - New `.claude/` files need `git add -f`.
  - Commits end with `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Review Focus

1. **A citation of a section the file holds only in part.** In a check section, `workflows-core:phase-handoff` §4.0 cited without the *Never infer* rule is out of the file and must fail. §4.0 cited with that rule passes. Pinned in Task 3, cases `entry_cite_partial_without_phrase` and `entry_cite_partial_with_phrase`.
2. **A question before the first `##` heading.** `/implement` asks its session-model question at line 26, before its first phase heading. The load step must come before that question, not merely under the first heading. Pinned in Task 4, case `question_rules_before_intro_question`.
3. **A `choices:` array inside a fenced block** counts as a question. The check fails closed rather than skipping fences. Pinned in Task 4, case `question_rules_fenced_array`.
4. **A whole load in the same section** — `args: "phase-handoff"` at or before the sentence — makes an out-of-part citation after it pass. One after it does not. Pinned in Task 3, cases `entry_cite_after_whole_load` and `entry_cite_before_whole_load`.
5. **Only `require-on-main` reads its own file:**
   - a `handoff-to-main` request reads the whole reference;
   - so does a later citation of a section the entry-point file lacks;
   - a read of the whole reference covers the entry-point file.

   The loader's prose decides this, so it is held by the Task 6 reading and the live runs. Task 2's step 6 pins the loader's wording against these three cases.

---

### Task 1: Entry-point files in `reference-parts.py`

**Files:**
- Modify: `scripts/reference-parts.py`. The module docstring (the marker syntax lives there and nowhere else), the parser, `generate`, `check-parts`, the `check-citations` skill-list check, and `CASES`.
- Create: fixture trees under `scripts/fixtures/reference-parts/`: `entry_minimal`, `entry_stale`, `entry_not_entry_point`, `entry_section_not_covered`, `entry_partial_phrase_missing`, `entry_skill_list_mismatch`, `entry_region_errors`.

**Interfaces:**
- Produces, as the source syntax that Task 2 writes into `phase-handoff.md`:
  ```
  <!-- reference-entry-files
  entry <entry> holds=<§>[,<§>...]
  partial <entry> <§> "<phrase>"[ "<phrase>"...]
  -->
  ```
  - The block sits directly after the H1 line.
  - `holds=` lists § numbers held whole. A number covers its subsections (`3` covers `3.1`–`3.7`).
  - `partial` lines name sections held in part, each with the phrases that identify the held text.
  - Region markers are `<!-- entry: <entry> -->` … `<!-- /entry -->`. They never nest and never close inside a fence. Lines outside every region belong to no entry file. (This is unlike a split reference, where every line must lie in a part.)
- Produces the generated file `plugins/workflows-core/reference-parts/<ref>/<entry>.md`, laid out as:
  1. the generated-file header line, worded as part 1's;
  2. the title `# <source H1 text> — entry point <entry>`;
  3. the line ``This file holds entry point `<entry>` of `<ref>`: §<holds, in order>, and in part §<partial> (<phrases>). Any other section is in the whole reference: `Skill(skill: "workflows-core:reference", args: "<ref>")`.``;
  4. the `${CLAUDE_PLUGIN_ROOT}` sentence, worded as part 1's;
  5. the regions' text in source order.
- Produces the loader-skill sentence the gate reads: ``These entry points read their own file: `<ref> <entry>`[, ...].``
- Produces an internal helper `entry_files(root) -> dict[str, dict[str, EntryDecl]]`. It maps reference to entry to the declaration, with `holds: list[str]`, `partial: dict[str, list[str]]` and `regions: list[tuple[int, int]]`. Task 3 consumes it.

- [ ] **Step 1: Write the fixture cases (red)**

  Add these `CASES` entries in the existing `Step` style. Each case asserts the exit code, what must be printed and the ERROR count.
  - **`entry_minimal`:** the reference `gamma.md` declares `entry check-it holds=1,3 partial check-it 4.0 "never infer"`. Its heading `## 3. \`check-it\` — the entry point` makes `check-it` an entry point. The loader skill carries the entry sentence.
    - `check-parts` → exit 0; `check-parts: PASS`; `_order` on `reference-parts/gamma/check-it.md` gives the title, then the holds line, then §1's heading text, then §3's.
    - `check-citations` → exit 0.
    - `generate` on a copy → `0 written, 0 removed`.
  - **`entry_stale`:** the committed `check-it.md` lacks one line of the source region. `check-parts` → exit 1, printing a message that names `reference-parts/gamma/check-it.md` as stale, with errors=1.
  - **`entry_not_entry_point`:** `entry nope holds=1`, where no heading code span starts with `nope`. Exit 1, the message names `nope`, errors=1.
  - **`entry_section_not_covered`:** `holds=3`, but one line of §3.2 lies outside every `check-it` region. Exit 1, the message names §3 and the line, errors=1.
  - **`entry_partial_phrase_missing`:** `partial check-it 4.0 "never infer"`, but no region text holds the phrase (normalised as the rule index normalises names). Exit 1, errors=1.
  - **`entry_skill_list_mismatch`:** the skill sentence names `gamma other` with no such declaration. `check-citations` → exit 1, errors=1.
  - **`entry_region_errors`:**
    - a region opened inside another;
    - a region closed inside a fence;
    - a `<!-- entry: undeclared -->` marker.

    Exit 1, errors=3.

- [ ] **Step 2: Run the selftest and see the new cases fail**

  Run: `python3 scripts/reference-parts.py --selftest`
  Expected: the seven new cases report `FAIL`, every existing case reports `ok`, and the last line is `SELFTEST FAIL`.

- [ ] **Step 3: Implement the declaration parser, region parser, generator, `check-parts` checks and the skill-list check**
  - **Shared helpers.** Reuse part 1's fence tracking and name normalisation.
  - **Stale files.** `generate` keeps deleting every file under `reference-parts/` that no declaration produces, and must now count entry files as produced.
  - **The skill sentence.** The check finds it like the split list (`SKILL_OPENING` style). Its absence, with any entry declared, is an error.
  - **Fail-closed.** It does not extend to entry files: a tree with no entry declaration passes this part.
  - **The docstring** documents the syntax, the generated layout and each check, in the existing docstring's style.

- [ ] **Step 4: Run the selftest and see it pass**

  Run: `python3 scripts/reference-parts.py --selftest`
  Expected: every case `ok`; `SELFTEST PASS`.

- [ ] **Step 5: Run the gate chain on the real tree**

  Run: `bash ~/e2e-live/lean-context-part1/gates-unreleased.sh /workspace/ai-workflows/.worktrees/lean-context-handoff-part`
  Expected: `EXIT=0`. No entry is declared yet, so nothing changes on the tree.

- [ ] **Step 6: Commit**

  `feat(gate): reference-parts.py serves an entry-point file — a declared entry point and the sections it needs, generated from region markers in an unsplit reference, gated for freshness, coverage and the loader's list`

---

### Task 2: `phase-handoff`'s `require-on-main` file, and the loader that serves it

**Files:**
- Modify: `plugins/workflows-core/references/phase-handoff.md`. This means the restructure, the declaration, the region markers, and a cross-file-needs paragraph opening §3.
- Create (generated, never hand-edited): `plugins/workflows-core/reference-parts/phase-handoff/require-on-main.md`.
- Modify: `plugins/workflows-core/skills/reference/SKILL.md`. The `model-routing` skill states no loader rule of its own, so it does not change.
- Modify: `plugins/product-workflows/commands/brd-interview.md`, Phase 0 step 6. It gets an explicit request.
- Modify: any other consumer that executes `require-on-main` with no loader call at its check. Re-derive the set: grep each command's check steps for "execute `require-on-main`" or "§3" with no `args: "phase-handoff require-on-main"` in the same step.

**Interfaces:**
- Consumes Task 1's declaration syntax, region markers and generator.
- Produces the entry-point file, and the `holds=` / `partial` values that Task 3's check reads.

- [ ] **Step 1: Restructure `phase-handoff.md` so the file's needs are visible** (spec A; map `docs/superpowers/research/2026-10-20-lean-context-loader-maps/phase-handoff.md` §2.2 and §2.5)
  - **Stop contract.** §3 says, by name, that every stopping row's message follows §4.4's stop contract. Either §4.4 moves under §3, or §3.3 or §3.7 names it. Builder's choice; either way, §4.4's text is held.
  - **The *Never infer* rule.** Keep §4.0's *Never infer an artifact's merged-ness from a sibling's gate* where it is, and hold it as `partial 4.0 "never infer"`. Or state it in §3, in which case §4.0 keeps a pointer.
  - **The `OWNER_REPO` derivation.** §2.6's derivation (lines 110–135 at `11a4fa70`) becomes a named block, for example a `#### \`owner-repo\` — deriving \`OWNER_REPO\`` heading. §3.5, `dev-workflows:code-handoff`, `docs-workflows:finish-and-handoff` and `workflows-core:architecture-promotion` can then name it. Update those four mentions to the name.
  - **§3's opening paragraph** states its cross-file needs. `specs-repo-git` §3.1, §3.2, §3.3 and §8, and `read-only-repos`, are looked up from any read of them made in this run, and loaded whole only where none is in the conversation (Global Constraints).
  - **Positional pointers** in the held text that would point outside the file become names. Run `check-parts` and read each `FLAG` line.

- [ ] **Step 2: Declare the entry and mark its regions**
  - **Holds:** the preamble (lines before §1), §1, §2.2, the `owner-repo` block, all of §3, §4.4, and §5's header with rules 2 and 3. These are the map's needs plus §2.2.
  - **The preamble and §5 have no § numbers of their own.** Mark their regions, and record §5 as `partial 5 "rule 2" "rule 3"`.
  - **No `holds=` number may cover text outside the regions.**

- [ ] **Step 3: Generate the file and check it**

  Run: `python3 scripts/reference-parts.py generate && python3 scripts/reference-parts.py check-parts`
  Expected: `1 written`, then `check-parts: PASS`.
  Report: the generated file's size (`wc -c`) against `phase-handoff.md`'s. The spec expects about 67k of 137k, under half. A file over 50% of the source is a finding to report before going on, not a pass.

- [ ] **Step 4: The loader serves the file**

  In `SKILL.md`, after part 1's split-list paragraph, add a paragraph that opens with the exact sentence ``These entry points read their own file: `phase-handoff require-on-main`.`` and says:
  - **The read.** For one of these, read `${CLAUDE_PLUGIN_ROOT}/reference-parts/<the first argument>/<the second argument>.md` and execute the entry point from it. The file names the sections it holds in the line under its title.
  - **Coverage.** A read of the whole reference covers it.
  - **Every other request** on that reference — no second argument, or any other entry point — reads the whole reference, as the paragraph after says.
  - **A section the file does not hold.** A step that cites one reads the whole reference.

  Then sweep `SKILL.md`'s own sentence "On a reference that does not load by part, the text a request needs is the whole file, whichever entry point the request names". Count the string before and after the edit. It now holds "save an entry point that reads its own file", and the paragraph that sends requests to the whole reference names the exception.

- [ ] **Step 5: Make the hidden `require-on-main` executions explicit**

  At `/brd-interview` Phase 0 step 6, and at every other site this task's **Files** grep found, the step executes `require-on-main` with `Skill(skill: "workflows-core:reference", args: "phase-handoff require-on-main")`. Nothing else in the step changes.

- [ ] **Step 6: Pin the loader's wording against Review Focus 5**

  Read the new `SKILL.md` paragraph against the three cases in Review Focus 5. Write one sentence per case, in the task report, saying which line of `SKILL.md` decides it.

- [ ] **Step 7: Gates**

  Run: `bash ~/e2e-live/lean-context-part1/gates-unreleased.sh /workspace/ai-workflows/.worktrees/lean-context-handoff-part`
  Expected: `EXIT=0`, check 11 and check 16 included.

- [ ] **Step 8: Commit**

  `feat(workflows-core): require-on-main reads its own generated part of phase-handoff — the check, its stop contract, the owner-repo derivation, §2.2's ownership tests and the never-infer rule, about half the file; every other request still reads the whole`

---

### Task 3: The out-of-part citation check, and the citations it finds

**Files:**
- Modify: `scripts/reference-parts.py` (`check-citations`, the docstring, `CASES`)
- Create: fixture trees `entry_cite_held`, `entry_cite_out_of_file`, `entry_cite_partial_without_phrase`, `entry_cite_partial_with_phrase`, `entry_cite_bare`, `entry_cite_after_whole_load`, `entry_cite_before_whole_load`, `entry_cite_other_section_unaffected`
- Modify: the consumer commands whose check sections the check fails on. At `11a4fa70` these are expected in `/brd-package`, `/brd-split`, `/create-prd` and `/prd-ground`. The check's own output is the list.

**Interfaces:**
- Consumes `entry_files(root)` (Task 1) and part 1's citation scan: sentence splitting, `§` references that belong to a citation, loader calls.
- Produces the error line ``ERROR <file>:<line>: cites workflows-core:<ref> §<n>, which the <entry> file does not hold, in a section that reads only that file -- name a section it holds, load the whole reference at or before this sentence, or reword it so it implies no load``. A citation naming no section uses the same error with `§<n>` replaced by `with no section`.
- Produces the census line `entry-point file <ref> <entry>: N request section(s), M citation(s) checked`.

- [ ] **Step 1: Write the fixture cases (red)**

  Each fixture is a consumer command with a `## Phase 0` section that holds `args: "gamma check-it"`. The declaration is `entry_minimal`'s: holds §1 and §3, plus `partial 4.0 "never infer"`.
  - **`entry_cite_held`:** a sentence citing `workflows-core:gamma` §3.2 → exit 0.
  - **`entry_cite_out_of_file`:** a sentence citing `workflows-core:gamma` §2.3 → exit 1, errors=1, the line printed.
  - **`entry_cite_partial_without_phrase`:** §4.0 cited with "classes it advisory" → exit 1, errors=1.
  - **`entry_cite_partial_with_phrase`:** §4.0 cited with "never infer an artifact's merged-ness" → exit 0.
  - **`entry_cite_bare`:** a sentence citing `workflows-core:gamma` with no § → exit 1, errors=1, the message holding `with no section`.
  - **`entry_cite_after_whole_load`:** `args: "gamma"` in an earlier sentence of the section, then §2.3 → exit 0.
  - **`entry_cite_before_whole_load`:** §2.3, then `args: "gamma"` in a later sentence → exit 1, errors=1.
  - **`entry_cite_other_section_unaffected`:** §2.3 cited in a `## Phase 9` section with no `check-it` request → exit 0.

- [ ] **Step 2: Run the selftest and see the new cases fail**

  Run: `python3 scripts/reference-parts.py --selftest`
  Expected: the eight new cases `FAIL`, every other case `ok`.

- [ ] **Step 3: Implement the check in `check-citations`**
  - **Scope.** It runs over the files `check-citations` already scans. The unit is the `##` section holding an explicit `args: "<ref> <entry>"` request for a declared entry. Every sentence in it citing `workflows-core:<ref>` is judged by its own § references.
  - **A sentence passes** where each § reference is either:
    - under a `holds` number; or
    - a `partial` section whose phrase occurs in that sentence, normalised;

    or where an explicit whole load of `<ref>` comes at or before it in the section.
  - **Census and docstring.** Print the census line, and document the check in the docstring, including what it cannot see.

- [ ] **Step 4: Run the selftest and see it pass**

  Expected: `SELFTEST PASS`.

- [ ] **Step 5: Run it on the real tree, and fix what it finds**

  Run: `python3 scripts/reference-parts.py check-citations`
  - **List each ERROR in the task report**, with your reading of whether the sentence *applies* the rule it cites or only *explains*.
  - **A sentence that applies a rule the file lacks** is not reworded. Report it as a finding for the controller: the file may need the section (spec A).
  - **A sentence that only explains** is reworded so it implies no load. Name the handoff contract in words, with no `workflows-core:phase-handoff` token or loader call, and keep its meaning. This follows part 1's precedent: the three reviewer agents' `finding-triage` citations became plain statements that load nothing. Re-read each reworded sentence in its paragraph.
  - **Check 16** must still pass. Check 16's relation 3 still sees the file cite `phase-handoff` elsewhere, so its preamble stays.

  Expected after the fixes: `check-citations: PASS`, with the census line reporting every consumer's check section.

- [ ] **Step 6: Gates**

  Run: `bash ~/e2e-live/lean-context-part1/gates-unreleased.sh /workspace/ai-workflows/.worktrees/lean-context-handoff-part`
  Expected: `EXIT=0`.

- [ ] **Step 7: Commit**

  `feat(gate): check-citations fails a citation of a section the entry-point file lacks inside the section that reads only that file; the explanatory citations in the consumers' check steps imply no load`

---

### Task 4: The question-rules load step, and its check

**Files:**
- Modify: `scripts/reference-parts.py` (`check-citations`, the docstring, `CASES`)
- Create: fixture trees `question_rules_loaded`, `question_rules_missing`, `question_rules_after_question`, `question_rules_before_intro_question`, `question_rules_fenced_array`, `question_rules_parenthetical_only`, `question_rules_presents_handoff_array`, `question_rules_no_asking_command`
- Modify: every command that presents a choice list: the 31 commands holding a `choices:` array at `11a4fa70`, plus `plugins/workflows-core/commands/frames.md`. Re-derive the set with the check itself. Where a converted command did not carry them before, add part 1's two preambles: **Core references.** (check 16) and the load-by-part paragraph (`check-citations`).

**Interfaces:**
- Produces the exact step paragraph, the same in every command:

  > **Load the question rules.** Load `escalation-rules core` now, with `Skill(skill: "workflows-core:reference", args: "escalation-rules core")`, before this run asks the user anything: every question it asks follows them — two to four options, presented verbatim with the `(Recommended)` marker where one is recommended, and a selection that carries no text.

- Produces the error line ``ERROR <file>:<line>: asks the user a question before its **Load the question rules.** step -- add the step before this line``.
- Produces the census line `question rules: N command(s) present a choice list, N load the rules first`.

- [ ] **Step 1: Write the fixture cases (red)**
  - **`question_rules_loaded`:** the step paragraph, then a `choices:` array → exit 0.
  - **`question_rules_missing`:** a `choices:` array and no step → exit 1, errors=1.
  - **`question_rules_after_question`:** the step after the first array → exit 1, errors=1.
  - **`question_rules_before_intro_question`:** a `choices:` array before the first `##` heading, with the step under `## Phase 0` → exit 1, errors=1. With the step before the array → exit 0, as a second step on a copy.
  - **`question_rules_fenced_array`:** the only `choices:` is inside a fenced block, with no step → exit 1, errors=1.
  - **`question_rules_parenthetical_only`:** a rule statement citing `args: "escalation-rules core"` in parentheses, then an array → exit 1, errors=1. A citation is not the step.
  - **`question_rules_presents_handoff_array`:** a workflows-core command citing `phase-handoff` §4.3's array with no `choices:` of its own, and no step → exit 1, errors=1.
  - **`question_rules_no_asking_command`:** a tree in which no command presents a choice list → exit 1, the message saying the scan matched nothing (fail closed).

- [ ] **Step 2: Run the selftest and see the new cases fail**

  Expected: the new cases `FAIL`, every other case `ok`.

- [ ] **Step 3: Implement the check**
  - **The scan.** Over `plugins/*/commands/*.md` of the family plugins (dev-workflows, product-workflows, docs-workflows, security-workflows, workflows-core), find the first question line: the first line, fenced or not, holding `choices:`; or the first line holding both `phase-handoff` and `§4.3`, whichever comes first.
  - **The rule.** A paragraph that opens with `**Load the question rules.**` and holds `args: "escalation-rules core"` must start on an earlier line.
  - **Census and docstring.** Print the census line, and document the check, including what it cannot see: whether a run executes the step.

- [ ] **Step 4: Run the selftest and see it pass**

  Expected: `SELFTEST PASS`.

- [ ] **Step 5: Add the step to every command the check fails**
  - **Where it goes.** Place the paragraph immediately after the command's `strip-run-flags` step where it has one, since that step asks nothing. Otherwise make it the command's first run step. Either way it must sit before the first question line.
  - **Re-read the neighbours.** A neighbouring sentence that claims to come "straight after `strip-run-flags`" or "before anything else" — `/implement`'s session-model gate says both — is reworded so the order it states is true. Count each such string before and after the edit.
  - **What stays.** Leave every existing citation of `escalation-rules core` in place.

- [ ] **Step 6: Run it on the real tree**

  Run: `python3 scripts/reference-parts.py check-citations`
  Expected: `question rules: 32 command(s) present a choice list, 32 load the rules first` (re-derived), and `check-citations: PASS`.

- [ ] **Step 7: Gates**

  Run the chain. Expected: `EXIT=0`, with check 16, check 12 and checks 4/9 included.

- [ ] **Step 8: Commit**

  `feat: every command that presents a choice list loads escalation-rules core as a step of its own before its first question, and check-citations fails one that does not`

---

### Task 5: Versions, changelogs, docs, rules, rationale and the claim sweep

**Files:**
- Modify: the five `plugins/<name>/.claude-plugin/plugin.json` files and `.claude-plugin/marketplace.json`, to the versions in Global Constraints.
- Modify: the five `CHANGELOG.md` files, each with a new `## [x.y.z] — Unreleased` section.
- Modify:
  - `plugins/workflows-core/docs/reference/references.md`, for the entry-point file and the two new checks;
  - the docs pages of dependents that describe how references load (`plugins/{dev,product,docs}-workflows/docs/reference/references.md`), where a sentence there is now false;
  - `.claude/rules/gates-reference-parts.md`, for the entry-point file, the two checks and what they cannot see;
  - `.claude/rules/workflows-core-git.md`, where the `phase-handoff` paragraph should say that `require-on-main` reads its own file;
  - `.claude/rules/workflows-core.md`, wherever it describes the loader;
  - `CLAUDE.md`'s *Internal reference convention* bullet. Name the one entry-point file next to the part sentence, and keep `CLAUDE.md` under 36,000 characters;
  - `docs/maintainers/rationale.md` § `reference-parts`. Record why an entry-point file and not a split, with the spec's measurements, and why the question rules load as a step;
  - `.claude/rules/plugin-updates.md`.

- [ ] **Step 1: Bump the versions** in `plugin.json` and `marketplace.json`.

  Run: `python3 scripts/validate-catalog.py`
  Expected: no error.

- [ ] **Step 2: Write each changelog section**
  - **Content.** Say what a user sees: what changed, with the measured reason; the improvement where a run is better; what an older or newer neighbour does.
  - **workflows-core:**
    - the entry-point file;
    - the loader;
    - the two checks (a repository gate, not shipped; say so);
    - `/frames` and `/statusline`'s load step.
  - **Each dependent:** its commands' load step, and its reworded citations.

- [ ] **Step 3: Write the coupling line in `plugin-updates.md`**
  - **Re-derive the coupling.** Do the dependents' new steps need workflows-core 1.45.0, or does 1.44.0's `escalation-rules core` part already serve them? Does an older dependent beside 1.45.0 read more than it should? An unreworded explanatory citation in a check section pulls the whole file in after the part.
  - **Write it in the existing lines' style**, stating each direction measured.

- [ ] **Step 4: Run the claim sweep**
  - **Scope.** Refinement 4: `plugins/` with every `CHANGELOG.md`, the root `README.md`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`.
  - **Subjects** (refinement 6):
    - "the text a request needs is the whole file";
    - "whichever entry point";
    - "procedure references stay whole";
    - "`require-on-main` reads/loads `phase-handoff`";
    - "`args: \"phase-handoff require-on-main\"` reads the whole".
  - **Rewrite** each live statement against what the loader now does. Count each string before and after (refinement 7) and list the counts in the report. Part 1's CHANGELOG sections are history: leave them as written.

- [ ] **Step 5: Docs, rules and the rationale**

  Write each page from the thing that runs it: the loader's paragraph and the script's docstring. Re-derive any number written into `CLAUDE.md` or `.claude/rules/`, with its command beside it.

- [ ] **Step 6: Gates**

  Expected: `EXIT=0`, `validate-catalog.py` with no warning, `check-docs.sh` checks 1–4, 9 and 16, and check 13.

- [ ] **Step 7: Commit**

  `docs: versions, changelogs, docs, rules and rationale for lean context D (workflows-core 1.45.0, dev-workflows 4.31.0, product-workflows 3.36.0, docs-workflows 1.18.0, security-workflows 0.3.0)`

---

### Task 6: The rule-by-rule reading

The controller dispatches it with read-only Opus readers, as part 1's Task 12 did. Two strands:

- **The `require-on-main` strand.** For every consumer (the 14 files with the request, `/brd-interview`, and any site Task 2 converted), read the consumer's check step and the rows it applies against the generated `require-on-main.md`.
  - Is every rule the step applies — the row, the stop format, the owner/repo probe, the §2.2 tests, §5 rules 2–3, *Never infer* — in the file or in a load the step makes?
  - Are the cross-file lookups (`specs-repo-git` §3.1/§3.2/§3.3/§8, `read-only-repos`) reached as today?
  - Classify each difference WORSE, BETTER or NEUTRAL, with file:line.
- **The question-rules strand.** For each of the 32 commands, read the new step's place against the command's first question, and against the neighbouring order claims Task 4 reworded. Classify each.

- [ ] **Step 1: Dispatch the two readers.** Each writes `reading-<strand>.md` into the SDD workspace.
- [ ] **Step 2: Fix every WORSE row** with a fix dispatch, re-review it scoped, and record a ruling per row.
- [ ] **Step 3: Ledger the counts per strand** and the rulings that fixed each WORSE row.

---

### Task 7: The final whole-branch review

- [ ] **Step 1: Dispatch the final reviewer** (most capable model) on `origin/main..HEAD` with the spec, this plan and the reading files. The fix wave and the scoped re-review follow the SDD skill.
- [ ] **Step 2: Gates after the fix wave.** Expected: `EXIT=0`.

---

### Task 8: The five live runs, with the user

- [ ] **Step 1: Restore and launch, run by run**
  - **Restore.** For each of `conformance`, `prd-ground`, `scan`, `route3` and `design`, read `~/e2e-live/lean-context-part1/<run>/start-state.md` and `restore.sh`. Then run the restore with `</dev/null`, after the user has closed the previous session.
  - **Copies only.** Restores and pushes reach only `ihudak-e2e/bookstore` and `ihudak-e2e/bookstore-specs`.
  - **Launch.** Give the user `E2E_PLUGIN_SRC=/workspace/ai-workflows/.worktrees/lean-context-handoff-part/plugins ~/e2e-copies.sh claude-opus-5-5 --permission-mode auto`, the invocation and the answers, as part 1 did. `/design` needs its mirror step from `design/restore.sh`.
- [ ] **Step 2: Measure each run**

  Run `live-measure.py` and `refcost.py` from `~/e2e-live/lean-context-part1/`, against part 1's session. Report three things:
  - **The Phase-0 `phase-handoff` read,** at the entry-point file's size in the four consumer runs.
  - **The `escalation-rules core` load** before the first question in all five runs.
  - **Cost,** total and main, against part 1's run.
- [ ] **Step 3: Judge each run blind against part 1's run**

  Mask the inputs with the `blindprep.py` pattern. A result judged worse is attributed from the transcripts first. A re-run of part 1 on the same inputs is the fallback.
- [ ] **Step 4: Clean up**

  Return the copies to their pre-test state with `~/e2e-live/lean-context-part1/cleanup/cleanup.sh`, adapted to this round's branches and PRs, and re-check `~/e2e-implement-snapshot.sh --check` at 18/18.

---

### Task 9: Record and merge

- [ ] **Step 1: Write the verification record last**

  Write `docs/superpowers/verification/2026-10-22-lean-context-handoff-part.md`:
  - the four done-criteria with their evidence;
  - the reading's counts;
  - each run's measurements and verdict;
  - the user's decisions.

  Re-derive every value against the tree being merged.
- [ ] **Step 2: Preserve the rulings and the ledger**

  Copy them unchanged into `docs/superpowers/verification/`, the ledger in a `text` block, as part 1's were.
- [ ] **Step 3: Date and merge**
  - Date every `— Unreleased` section with the merge date.
  - Run `gates.sh` with `ASSERT_PUBLISHED=1`, and expect `EXIT=0`.
  - Merge `--no-ff` in a temporary worktree on `origin/main`, never `git checkout`, and run the gates on the merged tree.
- [ ] **Step 4: Push and update**
  - Ask the user before `git push origin main`.
  - After the push, wait for CI.
  - Then give `claude plugin update <name>@shipwright` for each bumped plugin, and a restart.

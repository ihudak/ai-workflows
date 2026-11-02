# D31 (1) — /brd-package flag gate: implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/brd-package` never packages a slice with an unanswered `needs-a-human` flag on one of its `[CDF#n]` unless the operator chooses to. `/brd-interview` can always answer such a flag, because an unanswered flag opens a round.

**Architecture:** The rule for "flagged" and "answered" moves from `/brd-interview` into `code-defect-log-format.md` as a new §7, and both commands cite it. `/brd-interview`'s *Every round is closed* branch treats an unanswered flag as askable. `/brd-package` Phase 0 gains step 7a, which reads the flags and asks.

**Tech stack:** Markdown command prose, run literally by agents. The gates are `scripts/*.sh` and `scripts/*.py`.

**Spec:** `docs/superpowers/specs/2026-11-02-d31-package-flag-gate-design.md`

## Global constraints

- **Questions:** `choices:` arrays have 2–4 options and no "Other", and are presented verbatim. `/brd-package` already loads the question rules at Phase 0 step 1 (line ~126), before the new step.
- **No new writes:** `/brd-package` writes neither `code-defect-log.md` nor any round record.
- **Reading records:** round and reconciliation records are read through `decision-register-format.md` §8, so no torn write counts.
- **Sibling records:** read from disk (the working tree), with no `require-on-main` on them.
- **Ids:** a hit's `<entry>` is resolved against the log's own ids and never parsed out.
- **Customer artifacts:** the bundle, the customer prompt and the delivery note never name a flag.
- **Release:** product-workflows 3.66.0 → **3.67.0**, in `plugin.json`, `marketplace.json` and `CHANGELOG.md` (dated 2026-11-02). No workflows-core change, so no coupling bullet.
- **Stop codes:**
  - `BRD_PACKAGE_FLAGGED_DEFECTS`: the operator chose to stop.
  - `BRD_PACKAGE_RECONCILIATION_UNREADABLE`: a sibling record exists and cannot be read.
- **Final report line:** `Flagged code defects shipped: [CDF#n] (<record> › <hit>), …`, printed only on "Ship anyway".

## Review focus

1. **A hit whose `<entry>` names no id in the log.** It is reported in the gate's printout, not counted as a flag, and never stops the run alone. Task 3 step 2 checks this.
2. **A flag answered by a round, and a later reconciliation of the same sibling hitting the same entry again.** The later hit is a new flag (§7: "a hit a later record writes is a flag of its own"). The gate fires again. Task 1 keeps the sentence, and Task 3's walk-through covers it.
3. **The slice's own reconciliation record ("this one included").** Its hits count too. Task 3 checks this.
4. **`--round <highest+1>` with only a flag outstanding.** The bare run and the `--round` run must take the same branch. Task 2 step 3 checks it.
5. **The no-new-round path.** A run with an unanswered flag no longer reaches it, so its "report as waiting" sentence is removed, not left as a dead branch. Task 2 checks it.

---

### Task 1: The shared rule, `code-defect-log-format.md` §7

**Files:**
- Modify: `plugins/product-workflows/references/code-defect-log-format.md`: add `## 7. Flags a reconciliation raises` before `## 6. Non-goals`, or after it. *Ruling for the executor:* append it as §7 and leave §6's number alone, so existing citations stay valid.
- Modify: `plugins/product-workflows/commands/brd-interview.md:1638-1662`. Keep the paragraph's role (the re-disposition trigger) and replace the rule's text with a citation of §7.

**Interfaces:**
- **Produces:** `code-defect-log-format.md` §7, which defines:
  - *flagged entry*: a hit line in the latest reconciliation record of any slice under the parent, this one included, whose path slot is `<slice folder>/code-defect-log.md`, whose outcome slot reads `needs-a-human`, and whose `<entry>` resolves to an id this log holds;
  - *answered*: a counted round record's `code defects:` line carries `flag answered [CDF#n] <record> › <review file>`;
  - *an unresolved hit*: one whose `<entry>` names no id in the log;
  - *an unreadable record*: one whose flags are undecidable;
  - the pre-3.58.0 note.

  The definition text moves from `brd-interview.md:1638-1662` and is not paraphrased. Only "this BRD's" becomes "the slice's".
- **Consumes:** none.

- [ ] **Step 1: Count before editing.** Run `python3 $S/sweep.py` (recreate it if the scratchpad move lost it: a wrap-insensitive phrase count over `plugins/`, `CLAUDE.md`, `.claude/rules/` and `docs/maintainers/`) for each of:
  - `An entry is flagged where`;
  - `reaches the operator only on a run that works a round`;
  - `as waiting for the next run of this command that works a round`.

  Record the counts in the ledger.
- [ ] **Step 2: Move the text, and cite it.** In `brd-interview.md`, the paragraph opening `**An entry is flagged where` becomes one sentence citing `code-defect-log-format.md` §7. It keeps where step 9 reads the records.
- [ ] **Step 3: Verify.** Read §7 against `decision-register-format.md` §9's worked example and check that each slot in the example's hit line resolves under §7. Then run `./scripts/check-docs.sh --root .` (`PASS`) and `python3 scripts/reference-parts.py check-citations` (`PASS`).
- [ ] **Step 4: Commit:** `feat(product-workflows): code-defect-log-format §7 states what flags an entry and what answers it`.

### Task 2: `/brd-interview` opens a round for an unanswered flag

**Files:**
- Modify: `plugins/product-workflows/commands/brd-interview.md`:
  - *Every round is closed* (line ~608): after the round's questions are generated, an unanswered flag (§7) makes the round non-empty;
  - the no-new-round path (lines ~681–684): remove the *Report, too, every `code-defect-log.md` entry a reconciliation record flagged* sentence, or rewrite it to say the path never meets a flag;
  - lines ~1664–1669: *This is the carry-forward…* and *A flagged entry reaches the operator only on a run that works a round*. Rewrite them to say an unanswered flag opens a round when every round is closed.
- Modify: `plugins/product-workflows/docs/commands/brd-interview.md`: add the new trigger.

**Interfaces:**
- **Consumes:** Task 1's §7 definitions.
- **Produces:** a round `<highest+1>` holding at least one `[V]` re-disposition question per unanswered flag. Its round record's `code defects:` line carries `flag answered` for each. Where the round holds no `[C]`, it is closed in the same write, as the round-1 no-question branch (lines ~575–583) is.

- [ ] **Step 1: Read the whole of *Resolve the round*,** including the `--round N` mirror rule (lines ~723–730) and the re-open path. Ledger which branch a run takes when every round is closed and the only askable thing is a flag, before and after the change.
- [ ] **Step 2: Edit the three sites** listed under Files.
- [ ] **Step 3: Trace three cases**, against the edited text, and write each outcome in the ledger:
  - **(a) bare run,** every round closed, one unanswered flag: expect round `<highest+1>` to open, the flag to be put, and `flag answered` to be written;
  - **(b) `--round <highest+1>`,** same state: expect the same branch as (a);
  - **(c) bare run,** every round closed, no flag and nothing else askable: expect the no-new-round path, unchanged.
- [ ] **Step 4: Claim sweep.** Rerun Task 1 step 1's counts. Expected after:
  - `reaches the operator only on a run that works a round`: 0;
  - `as waiting for the next run of this command that works a round`: 0.

  Then check that `check-docs.sh` and `check-citations` both print `PASS`.
- [ ] **Step 5: Commit:** `feat(product-workflows): /brd-interview opens a round for a reconciliation's unanswered code-defect flag`.

### Task 3: `/brd-package` Phase 0 step 7a, the flag gate

**Files:**
- Modify: `plugins/product-workflows/commands/brd-package.md`:
  - Phase 0: a new step **7a** after step 7 and before step 8;
  - Final report (line ~2035): add the shipped-flags line;
  - the stop-code list, if the command has one.
- Modify: `plugins/product-workflows/docs/commands/brd-package.md`: the gate, both stop codes, the question, and the fact that "Ship anyway" is asked again on every run.

**Interfaces:**
- **Consumes:** §7 (Task 1); the round records step 7 already read.
- **Produces:** a `flags_shipped` list, `[CDF#n]` plus record plus hit, which the Final report prints.

**Step 7a's text pins these:**
- **Scope:** it runs only where the folder holds `code-defect-log.md`.
- **What it reads:** the latest reconciliation record of every slice under the parent, this one included, from disk and through §8. It does not run `require-on-main` on them.
- **An unreadable record:** stop with `BRD_PACKAGE_RECONCILIATION_UNREADABLE: <BRD-KEY>'s flags cannot be decided — <path> exists and cannot be read.`
- **Unresolved hits:** printed as `hit names no entry of this log: <record> › <hit>`, and never a flag.
- **No unanswered flags:** print nothing and proceed.
- **Otherwise:** print each flag as `[CDF#n] — <record> › <what was found>`, then ask once:

  ```
  choices: ["Stop — re-disposition them first with /product-workflows:brd-interview <BRD-KEY> (Recommended)", "Ship anyway — name them in the Final report"]
  ```

  - **Stop:** stop with `BRD_PACKAGE_FLAGGED_DEFECTS: <BRD-KEY>'s code-defect log holds <n> flag(s) a reconciliation raised that no interview round answered — run /product-workflows:brd-interview <BRD-KEY>, which opens a round for them, then package again.` Nothing has been written, so there is no handoff.
  - **Ship anyway:** carry the list to the Final report.
- Step 6's *Do not send the operator back to `/brd-interview`* stays as it is; it covers a register that is not on file. Re-read it next to step 7a and add a clause only if a reader could take it to forbid step 7a's offer.

- [ ] **Step 1: Write step 7a,** the Final report line and the docs page.
- [ ] **Step 2: Walk through the case in `decision-register-format.md` §9,** against the edited text, and ledger each outcome:
  - **(a)** the sibling's record carries the hit and no round answers it: expect the gate to fire, and "Stop" to give `BRD_PACKAGE_FLAGGED_DEFECTS`;
  - **(b)** after Task 2's round writes `flag answered`: expect the gate to pass silently;
  - **(c)** a later reconciliation hits the same entry again: expect the gate to fire again;
  - **(d)** a hit naming `[CDF#9]`, which the log does not hold: expect it printed as unresolved, with no flag and no stop;
  - **(e)** the slice's own record carries the hit: expect it to count.
- [ ] **Step 3: Run the quick gates:**
  - `check-questions`: PASS, with the count unchanged at 37 commands, since `/brd-package` already presents choices;
  - `check-citations`: PASS;
  - `check-docs.sh --root .`: PASS.
- [ ] **Step 4: Commit:** `feat(product-workflows): /brd-package asks before packaging a slice whose code-defect log a reconciliation flagged`.

### Task 4: Release, to-fix, follow-ups, full gates

**Files:**
- Modify: `plugins/product-workflows/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (3.67.0), and `plugins/product-workflows/CHANGELOG.md` (`## [3.67.0] — 2026-11-02`).
- Modify: `docs/superpowers/to-fix.md`, the D31 entry. Mark part (1) done in 3.67.0, and keep parts (2)–(4) open as written.
- Modify: `docs/superpowers/brd-route-follow-ups.md`, E-8. Add a dated line saying its no-further-round case is closed by 3.67.0.
- Check, and edit only if a sentence is now false: `.claude/rules/brd-route.md` and `.claude/rules/product-workflows.md`. These are the map lines for `/brd-package` gates and `/brd-interview` triggers.

- [ ] **Step 1: Edit the files above.**
- [ ] **Step 2: Run the full gate chain** in the background: `bash $S/gates-nonode.sh > $S/g-d31.log 2>&1; echo "EXIT=$?" >> $S/g-d31.log`. Expected: `EXIT=0`.
- [ ] **Step 3: Commit:** `release: product-workflows 3.67.0 — to-fix D31 (1)`. Then push and open the PR (`env -u GITHUB_TOKEN gh pr create --base main`).
- [ ] **Step 4: Final review:** an independent Opus review of the branch, with this plan's review focus. Fix its findings and re-review the fixes until it is clean.

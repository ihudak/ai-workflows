# IMP-G3 Fable Escalation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Precondition:** IMP-G5 merged; merge origin/main and re-derive sites by phrase before Task 1.
- `git merge origin/main` into `feat/imp-g3-fable-escalation`. Never rebase it.
- IMP-G5 rewrites `run-state.py` and `implement.md` (format 2, `peek`, `persist`, `init --resume`, exits 8 and 9, `step`, tree records, Phase 0's resume path, `## Resuming a stopped run`). Every site below is named by phrase. Where a phrase this plan names is missing after the merge, stop and report it; never guess a site.

**Goal:** at HIGH-RISK, `/dev-workflows:implement`'s `code-writer` and `review-fixer` run on Fable, where Fable is reachable, nothing else already decides the model, the run fixes no security finding, and the user agreed once — for the run, or for all runs through a setting.

**Architecture:**
- `workflows-core`: `classification` §4 gains a third coding-model clause, read from `/implement`'s run-state. `run-flags` gains §8, the `WORKFLOWS_FABLE_ESCALATION` setting, outside `strip-run-flags`.
- `dev-workflows`: `run-state.py` gains `fable_escalation` and fills a key an older file lacks. `implement.md` gains one section, `## The Fable escalation guard`, cited before every `code-writer` and `review-fixer` dispatch. It resolves the escalation once a run, records it, falls back once, reports it, and carries it across an IMP-G5 resume.

**Tech Stack:** Python 3.11 standard library (`run-state.py` and its selftest); markdown prose that agents execute; the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-13-imp-g3-fable-escalation-design.md`, revision 3, approved 2026-11-13. Read it whole first; § numbers below are its own. IMP-G5's plan (`docs/superpowers/plans/2026-11-13-imp-g5-implement-resume.md`) states the run-state facts this plan builds on.

**Where this plan and the spec differ, this plan's Rulings rule.** Each ruling is marked for Fable's plan review.

## Global Constraints

### The setting (§3.1)
- **Name and values.** `WORKFLOWS_FABLE_ESCALATION`. `ask` is the default: unset, empty or only whitespace. The others are `always` and `never`. Values are matched case-insensitively after trimming. Any other value reads as `ask`, and the guard prints one line saying so, once.
- **Who reads it.** `/implement` alone, only at its guard, by `printenv WORKFLOWS_FABLE_ESCALATION`; an unset variable prints nothing, which reads as empty.
  - `strip-run-flags` never reads it.
  - It adds no `run_flags` member, no `Run flags:` line, no command-line flag.
  - No other command reads it.
- **Spelling (check 5).** Every `dev-workflows` file names it bare, with no `$`. `run-flags` §8 writes it `$WORKFLOWS_FABLE_ESCALATION`. No `dev-workflows` file writes the `$` form of any `workflows-core` variable either (the price-table override included): cite `run-flags` §2 instead.
- **No per-run override.** `--enforce-model=fable` is the one-run route. It also pins the planner, the reviewer and the scanners, and `workflows-core`'s environment page says so.

### The record (§3.6)
- **The key.** `KEYS` gains `("fable_escalation", {"source": None, "choice": None})`, immediately after `coding_model`. `KEYS_LINE` then reads `… coding_model fable_escalation{source choice} branch_answer{…} …`. `implement.md`'s quote changes in Task 1's commit.
- **Its members.** `source` is `answer`, `setting`, `fallback`, `security` or `unreachable`. `choice` is the escalated value or the unescalated one.
- **A Fable value** is a `claude-fable-*` id, or the family `fable`. **The escalated value** is the highest listed `claude-fable-*` id by version number; in a family-only harness, `fable`. **The unescalated value** is §4's `implementation_model` without the third clause: Opus, or the Sonnet floor where no Opus is available.
- **`load` fills** each absent top-level `KEYS` key with its default, on read — never `format`, so a file with no `format` still exits 8 from `peek`. The file on disk changes only when a call writes it.
- **`step_groups[].model`.** Each entry gains `model`: the run-state `coding_model` the dispatch passed, in the record form `routing.block` keeps (classification §5), never the dispatch form. An entry without `model` (an older file's) is not a Fable dispatch.
- **Unchanged:** `format` stays 2, and IMP-G5's `RESUME_KEYS` stays as it is.

### The guard (§3.2, §3.3, §3.5)
- **When.** Before every `code-writer` and `review-fixer` dispatch, and before that dispatch's own records (the `step_groups` append, IMP-G5's `before dispatch:<agent>` tree record). It acts where all of these hold:
  - run-state `class` is HIGH-RISK;
  - `fable_escalation.choice` is null;
  - neither of the table's first two rows holds.
- **The table.** The first row that holds decides:
  1. `--enforce-model` set: no guard. §10 overrides every clause.
  2. `current_model` is Fable or Mythos: no guard.
  3. A security-finding run: write `{security, <unescalated>}`.
  4. Fable not reachable: write `{unreachable, <unescalated>}`. Under `always`, also print `WORKFLOWS_FABLE_ESCALATION=always, but Fable is not reachable — coding on <unescalated model>`.
  5. Otherwise the setting decides:
     - `always` writes `{setting, <escalated>}` and `never` writes `{setting, <unescalated>}`. Each prints one line naming the setting and the model chosen.
     - `ask` puts the question, then writes `{answer, <the value chosen>}`.
- **Fable reachable** is classification §2's reading of the `task` tool's `model` parameter: a listed `claude-fable-*` id, or, in a family-only harness, the listed `fable` family. Neither reading stops the run.
- **A security-finding run** is one where either holds:
  - `grep -qE '\[SEC#[0-9]+\]'` hits the file `files.task_description_file` names, or any `report.phase1_tasks` entry;
  - `patches` is non-empty.

  One such task makes the whole run unescalated, and a passing mention counts.
- **The auth sentence.** Where `routing.block.reason` cites a §1.1 authentication or security trigger (Ruling R10), the question and the `always` line add: *Fable's safety filters may re-run some of this run's requests on Opus.*
- **An escalating write** sets `routing.block`'s `implementation_model` and `fixes_model`, and `coding_model`, to the escalated value, and appends to the block's `notes`. It also prices the escalated value as `run-flags` §2's *Unpriced reachable id* paragraph does, and prints that paragraph's warning where it is unpriced.
- **Class changes.** A fall below HIGH-RISK drops the escalation for later dispatches; the key stays. A rise back applies the recorded choice and never asks again.

### The question (§3.2, verbatim)
```
This change is HIGH-RISK. Its code can be written on Fable (<resolved Fable id or family>), the strongest model reachable, at <multiple> the per-token price of <unescalated model>, or on <unescalated model> as planned.
choices: ["Write it on Fable (Recommended)", "Write it on <unescalated model>"]
```
- **`<unescalated model>`** is the unescalated value, its id or family as resolved.
- **`<multiple>`** is Fable's `input` price over the unescalated model's `input` price, from the price table `run-flags` §2 resolves, rounded to one decimal place and written `2.0×`. In a family-only harness it is `about twice or more`. For an unpriced model, see Ruling R1.
- **A free-text answer** is normalised to one of the two options or re-asked (`workflows-core:escalation-rules`, closed-vocabulary pickers). It never writes the setting.

### The fallback (§3.4)
- **When it fires.** All three must hold:
  1. the dispatch was escalated: its `step_groups` entry's `model`, or, for `review-fixer`, `routing.block.fixes_model` (Ruling R7), is a Fable value;
  2. it failed outright: the tool call returned an error and no agent reply;
  3. no `step_groups` entry whose `model` is a Fable value has a readable status: `done`, `needs_decision`, `trigger` or `blocked` (Ruling R6).
- **What it does.** It is the one retry, made on the unescalated value:
  - re-resolve by the unescalated rule;
  - write `{fallback, <unescalated>}`, the block and `coding_model` in one `set`;
  - re-dispatch;
  - the report says so.
- **What it leaves alone.** Every other unreadable return keeps its same-model retry. A retried fix attempt keeps its number, so the fallback costs no Phase 3.5 attempt.

### The report (§3.6)
- **The line.** One line in `### Classification`, beside the §10 bypass line, from the key, worded as one of:
  1. `HIGH-RISK coding on Fable (<value>) — you chose it`
  2. `HIGH-RISK coding on Fable (<value>) — WORKFLOWS_FABLE_ESCALATION=always`
  3. `HIGH-RISK coding on <unescalated model> — you chose it`
  4. `HIGH-RISK coding on <unescalated model> — WORKFLOWS_FABLE_ESCALATION=never`
  5. `HIGH-RISK coding on <unescalated model> — Fable not reachable`
  6. `HIGH-RISK coding on <unescalated model> — Fable was not available (fallback)`
  7. A security-finding run: `HIGH-RISK coding on <unescalated model> — security-finding fixes are not escalated`
- **Mixed models.** Where step groups ran on different models, the line names how many ran on each (`step_groups[].model`).
- **No line.** A run that was never HIGH-RISK prints none. For a null `choice`, see Ruling R5.

### Text the spec fixes elsewhere
- **Classification §4's clause:** "at HIGH-RISK, a `current_model` that is not Fable or Mythos is escalated where `/implement`'s run-state `fable_escalation.choice` is a Fable value". It goes before `--enforce-model`, which overrides all three.
- **The `to-fix.md` follow-up:** "measure the escalated runs: whether Opus review of Fable code misses what Fable review would catch, and how often Fable's filters re-run a request".
- **Non-goals:**
  - nothing escalates to Mythos, and a harness listing no Fable id escalates nothing;
  - `risk-planner` and `code-review` keep their models;
  - no other command is escalated.

### Repository rules
- **Prose is executed.** Read a file with the Read tool before editing in its area, so its rules file loads. Locate sites by phrase. Pages carry no `§`, D-numbers or review ids.
- **Shared references** are cited `workflows-core:<name>` and loaded through `Skill(skill: "workflows-core:reference", args: "<name>")`, never by path.
- **`choices:` arity.** 2 to 4 options, no "Other". `implement.md` already loads `escalation-rules core` before its first question; do not move that load.
- **GIT-G1's sections are not edited**, in any file: Ending early, the specs preflight, `branch-check`, `require-on-main`, the specs handover, the terminal `commit-artifacts`. Never edit:
  - `specs-repo-git.md`;
  - `phase-handoff.md`;
  - `scripts/specs-git.py`;
  - `.github/workflows/validate-catalog.yml`;
  - `.claude/rules/workflows-core-git.md`.
- **Rules files** stay under 20,000 characters, and nothing is cut to fit. Measure with `python3 -c "print(len(open('<f>',encoding='utf-8').read()))"`.
- **Regexes.** Every executed regex uses `[0-9]`, never `\d`. Vendor neutrality holds: name no tracker.
- **The gate chain**, before every commit. Expected: `EXIT=0`, and 0 warnings from `validate-catalog.py`.
  ```bash
  bash -c 'set -o pipefail; python3 scripts/validate-catalog.py && ./scripts/check-id-grammar.sh --root . && ./scripts/check-id-grammar.sh --baseline && python3 scripts/reference-parts.py check-parts && python3 scripts/reference-parts.py check-citations && python3 scripts/reference-parts.py check-questions && python3 scripts/reference-parts.py check-branch-check && ./scripts/check-docs.sh --root . && python3 plugins/dev-workflows/scripts/run-state.py --selftest'; echo "EXIT=$?"
  ```
- **Commits.**
  - `git branch --show-current` must print `feat/imp-g3-fable-escalation` immediately before each commit.
  - Every message ends with:
    ```
    Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01EcAVqApJxfCBcAbv5iWuu7
    ```
  - Do not push.
- **The claim sweep.** The population is every statement of `/implement`'s coding model, and every statement of "Opus is otherwise reserved for planning and review". It is swept by subject (claim-sweep refinements 4, 6, 7 and 8).
  - **The recipe.** Run it from the repository root, before and after each task's edits, over the files that task owns; Task 6 runs it over the whole scope. It is wrap-insensitive, since `classification.md` is hard-wrapped.
    ```bash
    python3 - <<'PY'
    import os, re
    subj = re.compile(r"code-writer|review-fixer|coding[- ]model|implementation_model|fixes_model|\bcodes? on\b|coded on|otherwise reserved")
    model = re.compile(r"Opus|Sonnet|Fable|Mythos|current_model|session's (own )?model")
    n = 0
    for root in ("plugins", "README.md", "CLAUDE.md", ".claude/rules", "docs/maintainers"):
        walk = os.walk(root) if os.path.isdir(root) else [(os.path.dirname(root), [], [os.path.basename(root)])]
        for d, _, fs in walk:
            for f in fs:
                p = os.path.join(d, f)
                if not p.endswith(".md"):
                    continue
                for s in re.split(r"(?<=[.;])\s", re.sub(r"\s+", " ", open(p, encoding="utf-8").read())):
                    if subj.search(s) and model.search(s):
                        n += 1
                        print("%s: %s" % (p, s[:160]))
    print("TOTAL", n)
    PY
    ```
  - **Dispositions.** Record each hit as one of:
    - rewritten;
    - true as it stands (it cites §4's rule, which now holds the clause);
    - another command's own field;
    - history (`CHANGELOG.md` and the `plugin-updates-coupling-history*` files, never edited).
  - **Generated parts.** A hit under `reference-parts/` is fixed in its source reference; then run `python3 scripts/reference-parts.py generate`.

## Rulings (where the design is silent — for Fable's plan review)

- **R1 — the unpriced wording.** The question's template with "a higher" reads "at a higher the per-token price of …". Where either model is unpriced, the clause reads `at a higher per-token price than <unescalated model>` instead. *A design wording defect, fixed here.*
- **R2 — on a resume, the record is settled in Phase 0 and written by `set`.** `fable_escalation` is not added to `RESUME_KEYS`. Phase 0's resume path settles it from `peek`'s record (Task 5's rules), then re-resolves `routing` and `coding_model` with it for `init --resume`'s stdin. After `init --resume`, one `set fable_escalation` follows wherever the settled record differs from the file's. A death between the two re-settles it on the next resume, to the same value.
- **R3 — when the setting differs between the runs.**
  - `answer` and `fallback` are kept, whatever the new setting says (§3.7).
  - `setting` follows the new setting: under `ask` the record goes back to `{null, null}`, so the guard asks.
  - `security` and `unreachable` are re-tested at once by rows 3 to 5. Only an `ask` outcome goes back to `{null, null}`.

  Re-testing at once, not at the next dispatch, keeps the record and its report line where no coding dispatch follows. Resetting the whole key, not only `choice`, gives one "unresolved" state.
- **R4 — the rest of the resume.**
  - An escalated `choice` whose Fable is no longer reachable becomes `{unreachable, <unescalated>}`, from any source, with a printed note (§3.7).
  - A `choice` that is not a Fable value is rewritten to this invocation's unescalated value, so the report names this session's model.
  - Under rows 1 or 2 on this invocation, the record is kept untouched.
- **R5 — a null `choice` at the report.** It prints no line, save one case: a run that was HIGH-RISK (`class`, or a `routing.history` line naming HIGH-RISK) and whose `step_groups` record models, because a resume reset the record and no coding dispatch followed. That run's line names each model by count, with no reason clause.
- **R6 — "readable" is a `step_groups` status.** Condition 3 reads `step_groups` alone. A readable `review-fixer` return is recorded nowhere new. Every route found to a run's first escalated dispatch reaches a `code-writer` step group first: the class rises to HIGH-RISK only before step groups or through a re-plan, and `code-review` re-classifies only to SIMPLE. The one exception is a resume that re-decides the escalation past the last group. There a later `code-writer` outright failure falls back rather than retrying on Fable: the cheaper direction, and reported.
- **R7 — `review-fixer`'s recorded model** is `routing.block.fixes_model` at its dispatch, which the escalation rewrites.
- **R8 — `review-fixer` takes `code-writer`'s retry.**
  - A `review-fixer` dispatch that fails outright is retried once with the same brief: on the unescalated value where the fallback fires, else on the same model.
  - A second outright failure stops the run as `Stop condition flag: NEEDS HUMAN` does, naming the failed dispatch.
  - §3.4 says the fallback *is* the one retry, so the agent needs one.
- **R9 — a `failed` mark written by a resume is no outright failure.** It is IMP-G5's mark on an entry left in flight. The tool call returned nothing in this session, so the fallback never fires on it.
- **R10 — the auth-trigger test.** `routing.block.reason` is resolved against §1.1's list, never by keyword. The test holds where the reason cites any of:
  - the authentication item;
  - the payment, billing, audit, compliance, PII and security-sensitive-logic item;
  - the vulnerability-fix item.
- **R11 — the guard's place and its write.**
  - The guard runs before the dispatch's records, so a question never leaves an appended entry with no model.
  - Its write is one `set` of `fable_escalation`, `routing` (the block whole: `set` merges `routing`'s members, so `history` stays) and `coding_model`. It is sent with the run's next tool call (Phase 1.4's write rule).
  - The question is the guard's only turn.
- **R12 — where the text goes.**
  - The guard is a new top-level section, `## The Fable escalation guard`, placed immediately before `## Invariants (always enforced)`.
  - The setting is `run-flags` §8.
  - `classification` §4's clause also gets a bullet in `.claude/rules/workflows-core-model-routing.md`, the authority's rules file.
  - `dev-workflows-implement.md` gains only a short clause, since it is near its limit.

## Review Focus

These are the five cases no task's selftest exercises that are most likely to bite. Each owning task's verification step quotes the sentence that decides it.

1. **A resume over an escalated `code-writer` the dead session left in flight.** The entry is marked `failed` and re-dispatched on Fable, with no fallback and no `source: fallback` (R9). Owners: Tasks 4 and 5.
2. **`WORKFLOWS_FABLE_ESCALATION` set to ` Always `, `NEVER`, `yes` or empty.** These read as `always`, `never`, `ask` with the one-line notice, and `ask` silently. Owner: Task 3.
3. **Claude Code's family-only harness.** Fable is reachable only where `fable` is listed. The escalated value, the recorded `model` and the dispatch argument are all `fable`, and `<multiple>` is `about twice or more`. Owners: Tasks 2 (§5) and 3.
4. **An escalated dispatch fails outright after an earlier Fable step group returned `done`.** It gets an ordinary same-model retry, with no fallback. Owner: Task 4.
5. **A free-text answer to the question** ("the cheap one"). It is normalised to *Write it on <unescalated model>* or re-asked. The setting is never written. Owner: Task 3.

---

### Task 1: `run-state.py` — the key, and `load`'s fill

**Files:**
- Modify `plugins/dev-workflows/scripts/run-state.py`:
  - `KEYS`, and the list-shapes comment above it (`step_groups` entries carry `model`, written by the run);
  - `load()`;
  - the docstring paragraph that opens "A key is a top-level name";
  - `selftest()`.
- Modify `plugins/dev-workflows/commands/implement.md`: only the `KEYS_LINE` quote after "which `run-state.py`'s `KEYS` defines, and no other:".

**Interfaces:** produces `fable_escalation` `{source, choice}`, and `load(f) -> dict`, which fills each absent top-level `KEYS` key but `format`.

- [ ] **Step 1: Write the failing selftest cases**, one `check(...)` each, passing `session` explicitly, as IMP-G5's cases do:
  - `KEYS holds fable_escalation after coding_model`: its index is one past `coding_model`'s, and its default is `{"source": None, "choice": None}`.
  - `KEYS_LINE names fable_escalation{source choice}`: `" coding_model fable_escalation{source choice} " in " %s " % KEYS_LINE`.
  - `init gives fable_escalation its default`.
  - `set` cases:
    - `set fable_escalation '{"source": "answer", "choice": "fable"}'` exits 0 and reads back equal;
    - `set fable_escalation.choice '"claude-fable-5-2"'` exits 0 and keeps `source`;
    - `set fable_escalation '{"model": "x"}'` exits 3;
    - `set fable_escalation '"fable"'` exits 3.
  - `init --resume` cases:
    - with `{"fable_escalation": {…}}` on stdin it exits 3 and leaves the file's bytes unchanged;
    - a recorded `fable_escalation` survives `init --resume` with `{"routing": {"block": {}}, "coding_model": "opus"}`.
  - **The fill.** Take a file `init` wrote, and delete `fable_escalation` from its JSON on disk. Then:
    - `read fable_escalation` exits 0 and prints the default;
    - `peek` exits 0, prints the default, and leaves the file's bytes unchanged;
    - `set fable_escalation.choice '"fable"'` exits 0 and the file holds `{"source": None, "choice": "fable"}`;
    - on a second such file, `init --resume` with `{}` exits 0 and writes the default.
  - **No fill of `format`.** Delete `format` from a file: `peek` exits 8, and so does `init --resume`.
- [ ] **Step 2: Run** `python3 plugins/dev-workflows/scripts/run-state.py --selftest`. Expected: the new cases fail, every existing case PASSES, and "implement.md quotes KEYS exactly" now fails.
- [ ] **Step 3: Implement.**
  - The `KEYS` entry.
  - `load`: once the object parses, give each absent `(k, default)` in `KEYS`, `k != "format"`, `copy.deepcopy(default)`.
  - One docstring sentence: a file lacking a top-level key `KEYS` holds (an earlier release's) reads as holding its default, `format` excepted; nothing is written until a call writes.
  - The comment line, and the quote in `implement.md`.
  - An existing case that breaks only because it relied on a `KEYS` key staying absent after `load`: switch it to a key `KEYS` lacks, and name it in the report.
- [ ] **Step 4: Run the selftest.** Expected: PASS, every case.
- [ ] **Step 5: Gates.** Expected: `EXIT=0`.
- [ ] **Step 6: Commit**: `feat(imp-g3): run-state.py — fable_escalation, and load fills a key an older file lacks`.

### Task 2: `workflows-core` — the clause, the setting, their pages

**Files:**
- Modify `plugins/workflows-core/references/model-routing/classification.md`:
  - §3.2 step 3;
  - §4's coding-model bullets and its closing paragraph ("So from MODERATE up a Fable or Mythos session codes on its own model");
  - §5's dispatch-rule sentence "a family-level §10 value is recorded as the family";
  - §9.1's `code-writer` bullet;
  - §9.2's `/implement` row.
- Modify `plugins/workflows-core/references/run-flags.md`:
  - its opening line;
  - §2's *Unpriced reachable id* paragraph;
  - a new `## 8.` section after §7.
- Modify `plugins/workflows-core/docs/reference/environment.md`, `docs/getting-started.md` and `docs/reference/references.md` (its `run-flags.md` entry).

**Interfaces:** produces classification §4's third clause, and `run-flags` §8. Tasks 3 to 6 cite both.

- [ ] **Step 1: Inventory.** Run the sweep recipe; record the `workflows-core` hits, each with a disposition, and the before-count.
- [ ] **Step 2: Classification.**
  - **§4's bullets.** Add the clause verbatim as the third bullet. Then `--enforce-model` "overrides all three (§10)".
  - **One sentence after the bullets:** what a Fable value is; that `/implement`'s guard and fallback alone write the key; that nothing escalates to Mythos.
  - **The closing paragraph:** at HIGH-RISK, an Opus, Sonnet or Haiku session's `/implement` codes on Fable once the run chose it. A fall below HIGH-RISK drops the escalation, and a rise back applies the recorded choice.
  - **§5:** an escalated family value `fable` is recorded as the family, beside §10's.
  - **§3.2 step 3, §9.1 and §9.2:** each statement of the rule gains the HIGH-RISK escalation, citing §4.
  - **Read the rest (extent face).** Read §10 and §3.2's closing blockquote against the clause. Change a sentence only where it states "both", or a coding model the clause now changes.
- [ ] **Step 3: `run-flags` §8,** `## 8. Fable escalation — \`$WORKFLOWS_FABLE_ESCALATION\``. It says:
  - the values and how they are matched;
  - that `/implement` alone reads it, at its guard, as classification §4's third clause;
  - that it is set in the session's environment;
  - what it is not: no run flag, no `run_flags` member, no `Run flags:` line, no command-line flag, and no other command's Phase 0 touches it;
  - the one-run route, `--enforce-model=fable`, and what that also pins.

  The opening line names §8. §2's unpriced paragraph reaches "the Fable value `/implement`'s escalation takes (§8), which its guard prices the same way". Re-read that whole paragraph against the wider extent.
- [ ] **Step 4: Pages.**
  - **`environment.md`:**
    - a `## \`$WORKFLOWS_FABLE_ESCALATION\`` section in the page's per-variable shape (Resolution, When unset, when the value is bad, unreadable "not applicable"), saying where it is set and the `--enforce-model=fable` route;
    - "nine" becomes "ten" at every count of the variables;
    - "Four of the nine are …" names the setting;
    - the sentence saying each variable "is read by a reference this plugin ships" is rewritten true for a variable `/implement` alone reads;
    - the `dev-workflows` bullet gains it.
  - **`getting-started.md`:** a `### WORKFLOWS_FABLE_ESCALATION` entry, and both of its "nine"s.
  - **`references.md`:** the `run-flags.md` entry names §8.
- [ ] **Step 5: Re-count.** Run the sweep recipe; record the after-count, and re-read every hit. Then `grep -rn 'nine' plugins/workflows-core/docs`; expect no count of variables.
- [ ] **Step 6: Gates.** Expected: `EXIT=0`. Check 5 now finds a reader for the documented variable, and check 9's "ten user-settable" agrees.
- [ ] **Step 7: Commit**: `feat(imp-g3): workflows-core — §4's Fable escalation clause and run-flags §8, WORKFLOWS_FABLE_ESCALATION`.

### Task 3: `implement.md` — the guard, cited at every dispatch

**Files:** modify `plugins/dev-workflows/commands/implement.md`:
- the new section `## The Fable escalation guard`, placed by R12;
- Phase 1.5's `model_routing` block (its `implementation_model:` comment), and the paragraph after the block ("the code-writing ones — `code-writer` and `review-fixer` — pass `implementation_model`");
- the run-state contract:
  - a `fable_escalation` bullet after the `routing` bullet;
  - the `step_groups` bullet's member list and meaning;
  - one sentence beside the `KEYS` paragraph: a key an earlier release's file lacks reads as its default;
- every `code-writer` and `review-fixer` dispatch site, and Phase 3A step 1's *Each dispatch* append object.

**Interfaces:**
- Consumes Task 1's key and fill, and Task 2's §4 clause and `run-flags` §8.
- Produces the section and its paragraphs, *When it runs*, *Who is escalated*, *The setting*, *The question* and *What it writes*. Task 4 adds *The fallback*, and Task 5 *On a resume*.

- [ ] **Step 1: Inventory.**
  - Count `→ Agent (subagent_type: "dev-workflows:code-writer"` (3 on IMP-G5's branch) and `"dev-workflows:review-fixer"` (1).
  - List every prose dispatch of `review-fixer` ("dispatches `review-fixer`", "dispatch `review-fixer` as above"). Each must either cite the guard or dispatch "as" a site that does; record which.
  - Run the sweep recipe over this file, and record its before-count.
- [ ] **Step 2: Write the section's five paragraphs**, exactly as the Global Constraints' guard, setting, question and record state them.
  - **Self-contained.** It names the three values and the `printenv` read itself, so it needs no `run-flags` reload after a compaction.
  - **The price.** It loads `run-flags` through the loader only for §2's price table and its unpriced warning.
  - **The question.** It is presented verbatim, with R1's unpriced wording, then the free-text rule.
  - **The write.** R11's one `set`.
  - **The setting's notice.** An unrecognised value prints its one line in the same guard run.
- [ ] **Step 3: Cite the guard at each dispatch.**
  - **Each arrow line.** It is preceded by "First run *The Fable escalation guard*." Its `model:` placeholder gains "; at HIGH-RISK, the Fable value `fable_escalation.choice` holds, where it holds one".
  - **The append objects.** Phase 3A step 1's *Each dispatch* object gains `"model": "<run-state coding_model>"`. Phase 3.5's fix attempt appends "as Phase 3A step 1 makes one"; confirm it, and change it only if it lists the members.
- [ ] **Step 4: Phase 1.5 and the contract**, as Files lists. The `step_groups` bullet says what `model` holds, by the Global Constraints' wording.
- [ ] **Step 5: Review Focus 2, 3 and 5.** Quote, in the report, the sentence that decides each. A case with no deciding sentence is a gap to fix now.
- [ ] **Step 6: Close.**
  - Re-count the arrows. Each must be preceded, within two lines, by the citation: `grep -B2 -E '→ Agent \(subagent_type: "dev-workflows:(code-writer|review-fixer)"' plugins/dev-workflows/commands/implement.md | grep -c 'Fable escalation guard'` equals the arrow count.
  - Run the sweep, and record the after-count.
  - `grep -n '\$WORKFLOWS_FABLE_ESCALATION' plugins/dev-workflows -r` prints nothing.
- [ ] **Step 7: Gates.** Expected: `EXIT=0`, `check-questions` passing.
- [ ] **Step 8: Commit**: `feat(imp-g3): /implement's Fable escalation guard, before every code-writer and review-fixer dispatch`.

### Task 4: `implement.md` — the fallback, the report, the invariants

**Files:** modify `plugins/dev-workflows/commands/implement.md`:
- the guard section's *The fallback* paragraph;
- Phase 3A step 1's *Read the return* rule ("It is **unreadable** where the dispatch failed outright" and "An unreadable return is retried once with the same request");
- Phase 3B step 7's Review-fixer sub-step ("Wait for the fix report.");
- Phase 3B's opening paragraph ("The code is written by `code-writer` on `implementation_model`");
- Phase 5's `### Classification`, beside the `Model routing: bypassed` line;
- `## Invariants`: the "ALWAYS dispatch `code-writer` and `review-fixer` with `model: <implementation_model>`" bullet, and one new ALWAYS bullet for the guard.

**Interfaces:** consumes Task 3's section and `step_groups[].model`. It produces *The fallback*, which Task 5's R9 sentence names.

- [ ] **Step 1: Inventory.** Run the sweep recipe over this file, and record the before-count and every hit not yet rewritten.
- [ ] **Step 2: *The fallback*.** Write the Global Constraints' three conditions and four actions, the readable statuses, R6, R7, and the kept attempt number.
- [ ] **Step 3: Hook it in.**
  - **`code-writer`'s retry.** It goes "on the unescalated value where *The fallback* fires, else on the same model". The retried entry's `model` is the model it passes.
  - **`review-fixer`.** It gains R8, after "Wait for the fix report."
- [ ] **Step 4: The report line.** Use the seven wordings and the mixed-model counts, read from `fable_escalation` and `step_groups[].model`. R5 decides a null `choice`.
- [ ] **Step 5: The invariants and Phase 3B's opening.**
  - The ALWAYS bullet gains the clause. Re-read its "Opus is otherwise reserved for planning and review" against Fable coding, and keep it true.
  - The new bullet: the guard before every `code-writer` and `review-fixer` dispatch, asked at most once a run; security-finding runs never escalated.
- [ ] **Step 6: Review Focus 4.** Quote its deciding sentence. Run the sweep, and record the after-count.
- [ ] **Step 7: Gates.** Expected: `EXIT=0`.
- [ ] **Step 8: Commit**: `feat(imp-g3): /implement falls back once from Fable, reports the escalation, and states it as an invariant`.

### Task 5: `implement.md` — the escalation across an IMP-G5 resume

**Files:** modify `plugins/dev-workflows/commands/implement.md`:
- the guard section's *On a resume* paragraph;
- Phase 0's resume path, at the step that builds `init --resume`'s stdin from re-resolved `routing` and `coding_model`;
- `## Resuming a stopped run`: its Phase 2A/2B rows, and its step-group and `3B.8, or 3.5` rows' "marked `failed`" sentences.

**Interfaces:** consumes IMP-G5's `peek`, `init --resume` and restart table, and Tasks 3 and 4.

- [ ] **Step 1: Locate each site by phrase.** Name each in the report.
- [ ] **Step 2: *On a resume*,** by R2 to R4. These settle it from `peek`'s record, a file without the key reading `{null, null}`, against this invocation's flags, `current_model` and reachability. The first rule that holds decides:
  1. Rows 1 or 2 hold: keep the record.
  2. `choice` is null: keep it.
  3. An escalated `choice`, with Fable unreachable now: `{unreachable, <unescalated>}`, and print a note naming the change.
  4. `answer` or `fallback`: keep it, a choice that is not a Fable value rewritten to this invocation's unescalated value.
  5. `setting`: re-read the setting.
     - `always` gives `{setting, <escalated>}`; where Fable is unreachable, it gives row 4's record and line.
     - `never` gives `{setting, <unescalated>}`.
     - `ask` gives `{null, null}`.
  6. `security` or `unreachable`: rows 3 to 5 now, an `ask` outcome giving `{null, null}`.
- [ ] **Step 3: The resume path.** Before re-resolving `routing` and `coding_model`, settle the record by *On a resume*. Re-resolve them with it. After `init --resume`, send `set fable_escalation` with the next tool call wherever the record changed.
- [ ] **Step 4: The restart table.**
  - **The Phase 2A/2B rows:** the guard runs before the first coding dispatch, so a resume past *Approve* still meets it.
  - **One sentence for every row that re-dispatches `code-writer` or `review-fixer`:** it meets the guard as any dispatch does, and a `failed` mark the resume writes is no outright failure (R9).
- [ ] **Step 5: Review Focus 1, and four scenarios.** For each, quote the deciding sentence:
  - an `answer` kept under a changed setting;
  - `setting: always` resumed under `ask`;
  - an escalated record with Fable now unreachable;
  - an IMP-G5-release file without the key.
- [ ] **Step 6: Gates.** Expected: `EXIT=0`.
- [ ] **Step 7: Commit**: `feat(imp-g3): /implement carries the Fable escalation across a resume`.

### Task 6: Pages, the handoff, rules, pointers — and the sweep's close

**Files:**
- `plugins/dev-workflows/docs/commands/implement.md`: the paragraph "`code-writer` and `review-fixer` run on the run's coding model".
- `plugins/dev-workflows/docs/reference/model-routing.md`: its sentences on `/implement`'s coding model.
- `plugins/dev-workflows/docs/reference/environment.md`: its opening sentence, "Nothing else it reads is yours to set".
- `plugins/dev-workflows/references/handoff/code-writer.md`: the `implementation_model:` line's comment.
- `.claude/rules/dev-workflows-implement.md`: the coding-model sentence in the "orchestrator writes no source code" bullet.
- `.claude/rules/workflows-core.md`: the `run-flags.md` paragraph.
- `.claude/rules/workflows-core-model-routing.md`: a §4 bullet (R12).
- `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md`: a pointer at its superseded non-goal.
- `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`: a pointer at row F part 2.

**Interfaces:** consumes every earlier task's names.

- [ ] **Step 1: The sweep, whole scope.** Run the recipe and record the before-count. Every hit not dispositioned by Tasks 2 to 5 gets one here; any other page the run finds joins Files.
- [ ] **Step 2: Pages.**
  - **The `/implement` page:** the escalation, the question and its two answers, the setting (bare, documented by the companion `workflows-core` plugin), security-finding runs, the one fallback, the report line, and the `--enforce-model=fable` route.
  - **The model-routing page:** the HIGH-RISK clause.
  - **The environment page:** the setting `/implement` reads, documented by `workflows-core`.
  - **Diagrams.** A changed mermaid label quotes `[ ] ( ) { } |` and `#`.
- [ ] **Step 3: The handoff.** The comment says `implementation_model` can be the escalated Fable value at HIGH-RISK.
- [ ] **Step 4: Rules.** Measure each file before and after; keep each under 20,000 characters, cutting nothing.
  - **`dev-workflows-implement.md`:** at most about 150 characters — "; at `HIGH-RISK`, Fable where the run chose it (`.claude/rules/workflows-core-model-routing.md`)" — and "`--enforce-model` over all three".
  - **`workflows-core.md`:** §8's setting, read by `/implement` alone at its guard, outside `strip-run-flags`.
  - **`workflows-core-model-routing.md`:** the clause, the guard as its one writer, and security fixes unescalated.
- [ ] **Step 5: The pointers.** Each is one line naming this design.
- [ ] **Step 6: Close the sweep.** Record the after-count against the before-count, and the number rewritten. Re-read each rewritten paragraph whole (extent face).
- [ ] **Step 7: Gates**, plus `node scripts/mermaid/check-mermaid.mjs --root .` where `node` exists. Expected: `EXIT=0`.
- [ ] **Step 8: Commit**: `docs(imp-g3): pages, the code-writer handoff, rules and pointers for the Fable escalation`.

### Task 7: Release

**Files:**
- both `plugin.json` files, and `.claude-plugin/marketplace.json`;
- both `CHANGELOG.md` files;
- `.claude/rules/plugin-updates-coupling.md`;
- `docs/superpowers/to-fix.md`.

- [ ] **Step 1: Versions.** Run `git fetch origin`, then take the next free **minor** of `workflows-core` and of `dev-workflows`, read from `origin/main` after IMP-G5. `plugin.json` must equal `marketplace.json`. Each CHANGELOG section is dated with the landing day (UTC), never left `— Unreleased`.
- [ ] **Step 2: The coupling bullet.** `**Update \`workflows-core\` <X> with \`dev-workflows\` <Y>**`, saying both directions:
  - a newer `/implement` beside an older `workflows-core` cites a §4 clause and a `run-flags` §8 setting that do not exist;
  - a newer `workflows-core` beside an older `/implement` names an escalation the command never makes.

  Measure the file. Above 19,000 characters, move its oldest bullets byte for byte into `plugin-updates-coupling-history-3.md`, and update every range pointer: the coupling file's intro, `history-3.md`'s title and intro, `plugin-updates.md`, and `CLAUDE.md`'s table.
- [ ] **Step 3: `to-fix.md`.** Delete the IMP-G3 entry. In its place, add `**IMP-G3-MEASURE**` with the follow-up text verbatim.
- [ ] **Step 4: Gates.** Measure the rules files and `CLAUDE.md`. Expected: `EXIT=0`, and 0 warnings.
- [ ] **Step 5: Commit**: `release(imp-g3): workflows-core <X>, dev-workflows <Y>`.

### Task 8: Close

- [ ] **Step 1: Consistency.**
  - `implement.md`'s `fable_escalation` bullet lists exactly the five `source` values. Every record the guard section writes (in *Who is escalated*, *The fallback* and *On a resume*) uses one of them, and so does every report wording.
  - The question text in `implement.md` equals the Global Constraints' verbatim.
  - No `dev-workflows` file holds `$WORKFLOWS_FABLE_ESCALATION`.
  - No added executed regex holds `\d`: `git diff origin/main...HEAD | grep '^+' | grep -F '\d'` is empty.
  - The guard citations equal the dispatch arrows.
- [ ] **Step 2: GIT-G1.** `git diff --stat origin/main...HEAD` names none of the five never-edit files. No `implement.md` hunk falls in Ending early, the specs preflight, `branch-check`, `require-on-main`, the specs handover or the terminal `commit-artifacts`: name each hunk's section.
- [ ] **Step 3: The full CI list.** Every `run:` step of `.github/workflows/validate-catalog.yml`, with its `--selftest`s, mermaid where `node` exists.
- [ ] **Step 4: The whole-branch review.** This is the controller's job, with Fable as the final reviewer, handed this plan's Rulings and Review Focus.

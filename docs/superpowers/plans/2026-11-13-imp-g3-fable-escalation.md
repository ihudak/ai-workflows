# IMP-G3 Fable Escalation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Precondition — met.** IMP-G5 merged (#188, `3016ead8`; dev-workflows 4.64.0, workflows-core 1.85.1), and `origin/main` is merged into `feat/imp-g3-fable-escalation` at `265094b6`. Never rebase the branch.
- IMP-G5 rewrote `run-state.py` and `implement.md` (format 2, `peek`, `persist`, `init --resume`, exits 8 and 9, `step`, `stopping`, `review_in_hand`, `conformance.note_blobs`, tree records, Phase 0's resume path, `## Resuming a stopped run`, the agents' resume note). Every site below was re-derived by phrase on `265094b6`, wrap-insensitively; the site table is `.superpowers/sdd/2026-11-13-imp-g3-fable-escalation/preflight-report.md`. A `:N` beside a phrase is that tree's line, a hint only: locate by the phrase. Where a phrase this plan names is missing when you reach it, stop and report it; never guess a site.

**Goal:** at HIGH-RISK, `/dev-workflows:implement`'s `code-writer` and `review-fixer` run on Fable, where Fable is reachable, nothing else already decides the model, the run fixes no security finding, and the user agreed once — for the run, or for all runs through a setting.

**Architecture:**
- `workflows-core`: `classification` §4 gains a third coding-model clause, read from `/implement`'s run-state. `run-flags` gains §8, the `WORKFLOWS_FABLE_ESCALATION` setting, outside `strip-run-flags`.
- `dev-workflows`: `run-state.py` gains `fable_escalation` and fills it in a file that lacks it. `implement.md` gains one section, `## The Fable escalation guard`, cited before every `code-writer` and `review-fixer` dispatch. It resolves the escalation once a run, records it, falls back once, reports it, and carries it across an IMP-G5 resume.

**Tech Stack:** Python 3.11 standard library (`run-state.py` and its selftest); markdown prose that agents execute; the repository gates.

**Spec:** `docs/superpowers/specs/2026-11-13-imp-g3-fable-escalation-design.md`, revision 3, approved 2026-11-13. Read it whole first; § numbers below are its own. The run-state facts this plan builds on are the shipped `run-state.py` and `implement.md`, which rule over IMP-G5's plan (`docs/superpowers/plans/2026-11-13-imp-g5-implement-resume.md`) wherever the two differ.

**Reviewed:** by Fable on 2026-11-13, against IMP-G5 at `893d9349`: *approve with changes*. Every item is folded in. **Re-derived** on the merged tree at `265094b6` on 2026-11-13: facts, sites and versions only. The controller then ruled on the three items that pre-flight raised: R14 to R16, which amend R8 and R12.

**Where this plan and the spec differ, this plan's Rulings rule.** Each ruling is marked for Fable's plan review.

**Each implementer is handed this plan's header** — Global Constraints, Rulings and Review Focus — with its task. Tasks 3 to 5 rely on them.

## Global Constraints

### The setting (§3.1)
- **Name and values.** `WORKFLOWS_FABLE_ESCALATION`. `ask` is the default: unset, empty or only whitespace. The others are `always` and `never`. Values are matched case-insensitively after trimming. Any other value reads as `ask`, and the run prints one line saying so, wherever it reads the setting: at the guard, and on a resume (Task 5).
- **Who reads it.** `/implement` alone, at its guard and on a resume, by `printenv WORKFLOWS_FABLE_ESCALATION || true`. `printenv` exits 1 on an unset variable, which would break a `&&` chain; it prints nothing then, which reads as empty. Never `${WORKFLOWS_FABLE_ESCALATION-}`, which check 5 reads as a `$` variable.
  - `strip-run-flags` never reads it.
  - It adds no `run_flags` member, no `Run flags:` line, no command-line flag.
  - No other command reads it.
- **Spelling (check 5).** Every `dev-workflows` file names it bare, with no `$`. `run-flags` §8 writes it `$WORKFLOWS_FABLE_ESCALATION`. No `dev-workflows` file writes the `$` form of any `workflows-core` variable either (the price-table override included): cite `run-flags` §2 instead.
- **No per-run override.** `--enforce-model=fable` is the one-run route. It also pins the planner, the reviewer and the scanners, and `workflows-core`'s environment page says so.

### The record (§3.6)
- **The key.** `KEYS` gains `("fable_escalation", {"source": None, "choice": None})`, immediately after `coding_model`. `KEYS_LINE` then reads `… coding_model fable_escalation{source choice} branch_answer{answer moves lines} …`. `implement.md`'s quote (Phase 1.4, after "which `run-state.py`'s `KEYS` defines, and no other:", `:470`) changes in Task 1's commit.
- **Its members.** `source` is `answer`, `setting`, `fallback`, `security` or `unreachable`. `choice` is the escalated value or the unescalated one.
- **A Fable value** is a `claude-fable-*` id, or the family `fable`. **The escalated value** is the highest listed `claude-fable-*` id by version number; in a family-only harness, `fable`. **The unescalated value** is §4's `implementation_model` without the third clause: Opus, or the Sonnet floor where no Opus is available.
- **`load` fills** only the keys of a named tuple, `FILLED = ("fable_escalation",)` — the keys added since format 2 — each absent one with its `KEYS` default, on read.
  - It never fills `format`, or any key outside `FILLED`. A damaged file missing `phase` or `clean_finish` must not read as `"Phase 1.4"` or `true`, and a missing top-level key stays exit 3, a defect of this command.
  - The file on disk changes only when a call writes it.
  - The fill is kept rather than a format bump.
- **`step_groups[].model`.** Each entry gains `model`: the run-state `coding_model` the dispatch passed, in the record form `routing.block` keeps (classification §5), never the dispatch form. An entry without `model` (an older file's) is not a Fable dispatch.
- **Unchanged:** `format` stays 2, and IMP-G5's `RESUME_KEYS` stays as it is.

### The guard (§3.2, §3.3, §3.5)
- **When.** Before every `code-writer` and `review-fixer` dispatch, and before the first record that dispatch makes (the `step_groups` append, the fix attempt's `failure_file`, IMP-G5's `before dispatch:<agent>` tree record). It acts where all of these hold:
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
- **A security-finding run** is one where any holds:
  - `grep -qE '\[SEC#[0-9]+\]'` hits the file `files.task_description_file` names, or any `report.phase1_tasks` entry;
  - `files.task_description_file` is null, or names no readable file: the run cannot prove it fixes no finding;
  - `patches` is non-empty.

  One such task makes the whole run unescalated, and a passing mention counts.
- **The guard's own calls.**
  - Its reads (the setting, the security grep, the reachability reading) go in one Bash call.
  - It loads `run-flags` only under `ask`, or where the outcome escalates: for the price table and the unpriced warning.
  - Its `set` is chained onto the run's next Bash command after the guard, whatever it is, so an answer never sits unwritten — Phase 1.4's *A write never takes a turn of its own* applied. On the merged tree *Each dispatch* opens with the report file's `mktemp`, which the `step_groups` append then records, so there the `set` is chained before whichever of the two the run's next Bash command makes (`set … && …`); at the Phase 3.5 fix attempt that command is the `failure_file` mktemp and its write, which come before that attempt's append. Either way a refused `set` (exit 3 or 9) stops the chain before the record. At the Review-fixer sub-step it is the `review_file` mktemp.
- **The auth sentence.** Where `routing.block.reason` cites a §1.1 authentication or security trigger (Ruling R10), the question and the `always` line add: *Fable's safety filters may re-run some of this run's requests on Opus.*
- **An escalating write** sets `routing.block`'s `implementation_model` and `fixes_model`, and `coding_model`, to the escalated value, and appends to the block's `notes`. It also prices the escalated value as `run-flags` §2's *Unpriced reachable id* paragraph does, and prints that paragraph's warning where it is unpriced.
- **Class changes.**
  - A fall below HIGH-RISK drops the escalation for later dispatches; the key stays. A rise back applies the recorded choice and never asks again.
  - **The guard does not apply a recorded choice**: it acts only on a null `choice`. The six sites that write `routing`, `class` and `coding_model` do, by re-resolving with §4, whose clause reads the record (Task 3 Step 1 lists them). On a resume, Phase 0's *Resuming* step 8 re-resolves `routing` and `coding_model` too, with the record Task 5 settles, for `init --resume` (no `class` write; Task 5 owns it).

### The question (§3.2, verbatim)
```
This change is HIGH-RISK. Its code can be written on Fable (<resolved Fable id or family>), the strongest model reachable, at <multiple> the per-token price of <unescalated model>, or on <unescalated model> as planned.
choices: ["Write it on Fable (Recommended)", "Write it on <unescalated model>"]
```
- **`<unescalated model>`** is the unescalated value, its id or family as resolved.
- **`<multiple>`** is Fable's `input` price over the unescalated model's `input` price, from the price table `run-flags` §2 resolves, rounded to one decimal place and written `2.0×`. In a family-only harness it is `about twice or more`. For an unpriced model, see Ruling R1.
- **A free-text answer** is normalised to one of the two options or re-asked (`workflows-core:escalation-rules`, *Closed-vocabulary pickers must normalise the free-text answer* — cite it by that exact rule name, as `implement.md`'s other citations of it do: its rule index maps it to part `pickers`, which `implement.md`'s load-by-part paragraph loads before the rule is applied). It never writes the setting.

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
  8. A `security` record held only because the task description could not be read (Ruling R13): `HIGH-RISK coding on <unescalated model>: not escalated, since the task description could not be read to rule out a security finding`
- **Mixed models.** Where step groups ran on different models, the line names how many ran on each (`step_groups[].model`). The counts leave out `failed` entries, and count no `review-fixer` dispatch.
- **No line.** A run that was never HIGH-RISK prints none. For a null `choice`, see Ruling R5; under rows 1 or 2 at report time, Ruling R4.

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
  - `plugins/workflows-core/scripts/specs-git.py` (no `scripts/specs-git.py` exists at the repository root);
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
  - **On the merged tree** (`265094b6`) the recipe prints `TOTAL 106`: `implement.md` 14 (IMP-G5's *Resuming* step 8 among them), `classification.md` 8, the `/implement` page 6, the `dev-workflows` model-routing page 2, `.claude/rules/dev-workflows-implement.md` 1, `.claude/rules/plugin-updates-coupling.md` 1; `references/handoff/code-writer.md` has none (its `claude-opus-5-5` comment is lower-case). Each task still records its own before-count.
  - **The expected after-count** is the before-count plus the sentences the task adds, each listed in the report. A difference is explained, hit by hit.
  - **Dispositions.** Record each hit as one of:
    - rewritten;
    - true as it stands (it cites §4's rule, which now holds the clause);
    - another command's own field;
    - history (`CHANGELOG.md` and the `plugin-updates-coupling-history*` files, never edited).
  - **Generated parts.** A hit under `reference-parts/` is fixed in its source reference; then run `python3 scripts/reference-parts.py generate`.

## Rulings (where the design is silent — for Fable's plan review)

- **R1 — the unpriced wording.** The question's template with "a higher" reads "at a higher the per-token price of …". Where either model is unpriced, the clause reads `at a higher per-token price than <unescalated model>` instead. *A design wording defect, fixed here.*
- **R2 — on a resume, the record is settled around `init --resume` and written by `set`.**
  - `fable_escalation` is not added to `RESUME_KEYS`.
  - Phase 0's resume path settles what it can from `peek`'s record without reading a file (Task 5's rules), then re-resolves `routing` and `coding_model` with it for `init --resume`'s stdin.
  - Whatever reads a file — the `unreachable` re-test's security grep — runs after `init --resume`, which has repointed or nulled the paths.
  - One `set` then follows wherever the settled record differs from the file's. A death between the calls re-settles it on the next resume, to the same value.
- **R3 — when the setting differs between the runs.**
  - `answer` and `fallback` are kept, whatever the new setting says (§3.7).
  - `setting` follows the new setting: under `ask` the record goes back to `{null, null}`, so the guard asks. A `setting` record needs no security test: the guard tests row 3 before row 5, so a security-finding run never wrote one, and its inputs cannot lose a `[SEC#n]`.
  - `security` is **kept, never re-tested**. Before `init --resume`, `files.task_description_file` still names the dead session's temp path, which a reboot removes. A re-test there would miss the `[SEC#n]` and, under `always`, escalate a security fix, which design ruling 6 forbids.
  - `unreachable` alone is re-tested at once by rows 3 to 5, **after** `init --resume`. By then `task_description_file` is repointed to its durable copy or nulled, and a null one makes row 3 hold. Only an `ask` outcome goes back to `{null, null}`.

  Re-testing at once, not at the next dispatch, keeps the record and its report line where no coding dispatch follows. Resetting the whole key, not only `choice`, gives one "unresolved" state.
- **R4 — the rest of the resume, and rows 1 and 2 at report time.**
  - An escalated `choice` whose Fable is no longer reachable becomes `{unreachable, <unescalated>}`, from any source, with a printed note (§3.7).
  - A `choice` that is not a Fable value is rewritten to this invocation's unescalated value, so the report names this session's model.
  - Under rows 1 or 2 on this invocation, the record is kept untouched.
  - Under rows 1 or 2 at report time, where `choice` is not null, the record's reason would be false: an `{answer, <Opus>}` record reported from a Fable session would say "you chose it". The line then gives the counts only — `HIGH-RISK coding — <n> step group(s) on <model>, <m> on <model>` — and nothing where no step group ran.
- **R5 — a null `choice` at the report.** It prints no line, save one case: a run that was HIGH-RISK (`class`, or a `routing.history` line naming HIGH-RISK) and whose `step_groups` record models, because a resume reset the record and no coding dispatch followed. That run's line reads `HIGH-RISK coding — <n> step group(s) on <model>, <m> on <model>; the escalation was not decided again after the resume`.
- **R6 — "readable" is a `step_groups` status.** Condition 3 reads `step_groups` alone. A readable `review-fixer` return is recorded nowhere new. Every route found to a run's first escalated dispatch reaches a `code-writer` step group first: the class rises to HIGH-RISK only before step groups or through a re-plan, and `code-review` re-classifies only to SIMPLE. The one exception is a resume that re-decides the escalation past the last group. There a later `code-writer` outright failure falls back rather than retrying on Fable: the cheaper direction, and reported.
- **R7 — `review-fixer`'s recorded model** is `routing.block.fixes_model` at its dispatch, which the escalation rewrites.
- **R8 — `review-fixer` takes `code-writer`'s retry, worded as `code-writer`'s is** (amended by the controller's R15 and R16, below).
  - A `review-fixer` dispatch that fails outright is retried once with the same brief and the resume note line R15 adds: on the unescalated value where the fallback fires, else on the same model, between its own `before dispatch:review-fixer` and `after dispatch:review-fixer` records, as every `review-fixer` dispatch is.
  - The retry re-captures nothing the brief names, since the brief hands `review_file`, not a diff. The failed attempt may have edited the tree, which is why R15's note goes with it.
  - A second outright failure stops the run "as the `NEEDS HUMAN` stop does, what needs the human being that no fix report came back", on **every** pass (R16): the same `review-fixer` `NEEDS HUMAN` stop, so no new stop, and no edit to Ending early or the "Every run" list, which names "the `review-fixer` `NEEDS HUMAN` stop" for every pass alike. That stop writes no `claims_file`.
  - §3.4 says the fallback *is* the one retry, so the agent needs one.
- **R9 — a `failed` mark written by a resume is no outright failure.** It is IMP-G5's mark on an entry left in flight. The tool call returned nothing in this session, so the fallback never fires on it.
- **R10 — the auth-trigger test.** `routing.block.reason` is resolved against §1.1's list, never by keyword. The test holds where the reason cites any of:
  - the authentication item;
  - the payment, billing, audit, compliance, PII and security-sensitive-logic item;
  - the vulnerability-fix item.

  Where the reason is unclear against that list, print the sentence.
- **R11 — the guard's place and its calls.**
  - **Place.** The guard runs before the dispatch's first record, so an appended entry never records the coding model from before the guard ran:
    - at Phase 3A step 1, it opens the *Each dispatch* paragraph (`:941`), before its report file and `step_groups` append; IMP-G5's `before dispatch:code-writer` record comes later in that paragraph;
    - at the Phase 3.5 fix attempt, it comes before the `failure_file` and append text (`:1078`), whose `before dispatch:code-writer` record follows the append;
    - at the Review-fixer sub-step, it opens the sub-step (`:1207`), before its `review_file` mktemp; IMP-G5's sentence "Every `review-fixer` dispatch — the one below, a plan ruling's second dispatch (below) and the pass an **Apply** makes (step 7's offer, above) — is made between two tree records" follows the `review_file` persist.
  - **Reads.** They go in one Bash call. It loads `run-flags` only under `ask` or an escalating outcome.
  - **Write.** One `set` of `fable_escalation`, `routing` (the block whole: `set` merges `routing`'s members, so `history` stays) and `coding_model`. It is chained onto the run's next Bash command after the guard, whatever it is, so under `ask` the answer never waits on a later record. At *Each dispatch* that command makes the report file and the `step_groups` append, and at the fix attempt the `failure_file`, so a refused `set` refuses the record too; at the Review-fixer sub-step it is the `review_file` mktemp.
- **R13 — a `security` record from an unreadable task description.** The record keeps the design's `source: security`, so the five values stand. The report tells the two cases apart from state at Phase 5. Where `patches` is empty and no `[SEC#n]` is found in `report.phase1_tasks` or in a readable `task_description_file`, the line is wording 8, not wording 7, which might be false.
- **R12 — where the text goes.**
  - The guard is a new top-level section, `## The Fable escalation guard`, placed immediately before `## Invariants (always enforced)` (`:1670`): on the merged tree that is after IMP-G5's `## Resuming a stopped run` and the `---` that closes it (`:1668`), the new section closed by its own `---`.
  - The setting is `run-flags` §8.
  - `classification` §4's clause also gets a bullet in `.claude/rules/workflows-core-model-routing.md`, the authority's rules file.
  - `dev-workflows-implement.md` gains only a short clause, since it is near its limit. Where fewer than 150 characters are left after the merge, the clause goes only in `workflows-core-model-routing.md`, and the task report says so. **Measured on the merged tree: 19,959 characters, 41 left — the fallback applies**: the clause goes only in `workflows-core-model-routing.md`. The bullet's two-clause restatement ("…else the §2 Opus chain's first available row; `--enforce-model` over both") is amended in place by R14, the one edit made there.
- **R14 — the rules file's restatement (controller ruling A, 2026-11-13).** In `.claude/rules/dev-workflows-implement.md`'s "orchestrator writes no source code" bullet, replace "; `--enforce-model` over both" with "; at `HIGH-RISK`, Fable where chosen; `--enforce-model` over all" — the one occurrence, else a two-clause restatement would stand false beside a three-clause rule. The file goes from 19,959 to 19,994 characters by Python `len`, leaving **6 characters of headroom** below `validate-catalog.py`'s 20,000 warning. Every later edit to that file must cut or move text out first, and the `dev-workflows` release notes (Task 7) say so. R12's fallback otherwise stands: the clause in full lives in `workflows-core-model-routing.md`. Owner: Task 6 (the edit), Task 7 (the note).
- **R15 — R8's retry carries the resume note (controller ruling B, 2026-11-13).** The retry of a `review-fixer` dispatch that failed outright ends, one line more after the brief's last, with IMP-G5's general resume note, verbatim: `Resume note: An earlier attempt may have partly edited the files this task covers; read them as they stand and complete the work.` The failed attempt may have applied part of its fixes, and the brief, which hands `review_file` and no diff, shows none of them. `plugins/dev-workflows/agents/review-fixer.md`'s existing section, `## A re-dispatch on a resume`, gains one widened clause in its opening sentence, so that it covers this retry too: `/implement` also dispatches it once more, with that same line, for a fix pass whose dispatch failed outright with no reply. Nothing else in that section changes, its heading included. Owner: Task 4.
- **R16 — no pass carries on without a Fix Report (controller ruling C, 2026-11-13).** A second outright failure of **any** `review-fixer` dispatch stops the run the way the `NEEDS HUMAN` stop does, the reason given being that no fix report came back: the BLOCK branch's pass; the PASS WITH RECOMMENDATIONS branch's pass, with any `NIT`s an **Apply** after the first review adds to it or a pass made for them alone; a plan ruling's second dispatch; and the pass an **Apply** after the re-review makes. The rule is written once, in the Review-fixer sub-step, as a paragraph led ***No fix report.***, and each pass's own site cites it in the same words, "(the Review-fixer sub-step's *No fix report*)", so each site reads one way:
  - the stop: no re-review and none of the steps that read a Fix Report (the diff re-capture, `claims_file`, the deferrals, `followed_by`); it surfaces to the user that no fix report came back, naming the findings `review_file` handed the pass and saying the tree may hold part of the pass; and it stops as the BLOCK branch's `NEEDS HUMAN` stop does — Phase 4.6 first, with `clean_finish: false`, as Phase 4.6's "Every run" list already says of "the `review-fixer` `NEEDS HUMAN` stop";
  - the BLOCK branch: its `NEEDS HUMAN` sentence, which surfaces "the deferred BLOCKER(s) … with the reason `review-fixer` gave", gains the no-report case, which surfaces that no fix report came back instead;
  - the PASS WITH RECOMMENDATIONS branch: one sentence saying a pass with no fix report stops the run, never going on to the offer, the unspent re-review or step 7.5;
  - the post-re-review **Apply** bullet: "its `Stop condition flag` stops nothing" gains "save where no fix report came back, which stops the run";
  - a plan ruling's second dispatch ("dispatch `review-fixer` as above"): the BLOCK branch's two-report flag test that follows it is never reached where that dispatch brought no report, which the test's sentence says, citing the rule in the same words.

  Owner: Task 4.

## Review Focus

These are the five cases no task's selftest exercises that are most likely to bite. Each owning task's verification step quotes the sentence that decides it.

1. **A resume over an escalated `code-writer` the dead session left in flight.** The entry is written `failed` (the step-group row's "the `null` written `failed` first") and its group re-dispatched on Fable, with no fallback and no `source: fallback` (R9). Owners: Tasks 4 and 5.
2. **`WORKFLOWS_FABLE_ESCALATION` set to ` Always `, `NEVER`, `yes` or empty.** These read as `always`, `never`, `ask` with the one-line notice, and `ask` silently. Owners: Tasks 3 and 5.
3. **Claude Code's family-only harness.** Fable is reachable only where `fable` is listed. The escalated value, the recorded `model` and the dispatch argument are all `fable`, and `<multiple>` is `about twice or more`. Owners: Tasks 2 (§5) and 3.
4. **An escalated dispatch fails outright after an earlier Fable step group returned `done`.** It gets an ordinary same-model retry, with no fallback. Owner: Task 4.
5. **A security-finding run, resumed after a reboot under `always`.** Its `security` record is kept, never re-tested. A guard that meets a null or unreadable `task_description_file` takes row 3. The run is never escalated. Owners: Tasks 3 and 5.

## Controller rulings on the pre-flight (merged tree, 2026-11-13) — settled

The pre-flight on the merged tree raised three items; the controller ruled on each as recommended, and each is a ruling above:

- **A** — `dev-workflows-implement.md`'s two-clause restatement, which an escalated HIGH-RISK run falsified: **R14**, in Tasks 6 and 7.
- **B** — R8's retry and IMP-G5's resume note: **R15**, in Task 4.
- **C** — R8's `NEEDS HUMAN` outcome on the passes with no `NEEDS HUMAN` branch (only the BLOCK branch tested `Stop condition flag`; the PASS branch did not, and the post-re-review **Apply** pass's flag "stops nothing"): **R16**, in Task 4.

---

### Task 1: `run-state.py` — the key, and `load`'s fill

**Files:**
- Modify `plugins/dev-workflows/scripts/run-state.py`:
  - `KEYS` (`("coding_model", None)` is followed by `("branch_answer", …)` in the `routing` row), and the list-shapes comment above it — its `step_groups` line, which says each entry is stamped `started` (`step_groups` entries carry `model`, written by the run);
  - a new `FILLED` tuple beside `KEYS`, and `load()` — on the merged tree it is `require`, read, `json.loads`, the not-an-object check, `return d`; `peek` and `init --resume` reach it through `resumable()`, which tests `format` after it, and `read`, `open`, `set`, `append`, `persist`, `remove`'s `remove_file()` and `init --recover` call it directly;
  - the docstring paragraph that opens "A key is a top-level name";
  - `selftest()`.
- Modify `plugins/dev-workflows/commands/implement.md`: only the `KEYS_LINE` quote after "which `run-state.py`'s `KEYS` defines, and no other:" (`:470`).

**Interfaces:** produces `fable_escalation` `{source, choice}`, `FILLED = ("fable_escalation",)`, and `load(f) -> dict`, which fills each absent key of `FILLED` and no other.

- [ ] **Step 1: Write the failing selftest cases**, one `check(...)` each, passing `session` explicitly, as IMP-G5's cases do:
  - `KEYS holds fable_escalation after coding_model`: its index is one past `coding_model`'s, and its default is `{"source": None, "choice": None}`.
  - `KEYS_LINE names fable_escalation{source choice}`: `" coding_model fable_escalation{source choice} " in " %s " % KEYS_LINE`.
  - `FILLED holds only keys KEYS holds, never format`.
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
  - **No fill outside `FILLED`.** Delete `phase` from a file: `read phase` exits 3.
- [ ] **Step 2: Run** `python3 plugins/dev-workflows/scripts/run-state.py --selftest`. Expected: the new cases fail and every existing case passes — "implement.md quotes KEYS exactly" among them, since `KEYS` and the quote change together in Step 3. On the merged tree, before Step 1, it prints `run-state selftest: PASS (231 checks)`.
- [ ] **Step 3: Implement.**
  - The `KEYS` entry.
  - `FILLED`, with a comment: the keys added since format 2, which a file an earlier format-2 release wrote can lack.
  - `load`: once the object parses, give each absent key of `FILLED` a `copy.deepcopy` of its `KEYS` default.
  - One docstring sentence: a file lacking a `FILLED` key (an earlier release's) reads as holding its default; any other missing key is still exit 3; nothing is written until a call writes.
  - The comment line, and the quote in `implement.md`.
- [ ] **Step 4: Run the selftest.** Expected: PASS, every case.
- [ ] **Step 5: Gates.** Expected: `EXIT=0`.
- [ ] **Step 6: Commit**: `feat(imp-g3): run-state.py — fable_escalation, and load fills it in an older file`.

### Task 2: `workflows-core` — the clause, the setting, their pages

**Files:**
- Modify `plugins/workflows-core/references/model-routing/classification.md` (IMP-G5 did not touch it):
  - §3.2 step 3 (`:166`);
  - §4's coding-model bullets (`:236`–`:238`, "`--enforce-model` overrides both (§10)") and its closing paragraph ("So from MODERATE up a Fable or Mythos session codes on its own model", `:251`);
  - §5's dispatch-rule sentence "a family-level §10 value is recorded as the family" (`:311`);
  - §9.1's `code-writer` bullet (`:549`);
  - §9.2's `/implement` row (`:563`).
- Modify `plugins/workflows-core/references/run-flags.md` (not a reference that loads by part):
  - its opening line ("Single source of truth for the three run flags", `:3`);
  - §2's *Unpriced reachable id* paragraph (`:58`);
  - a new `## 8.` section after `## 7. Temporary files` (`:130`), the file's last section.
- Modify `plugins/workflows-core/docs/reference/environment.md`, `docs/getting-started.md` and `docs/reference/references.md` (its `run-flags.md` entry, `:70`).

**Interfaces:** produces classification §4's third clause, and `run-flags` §8. Tasks 3 to 6 cite both.

- [ ] **Step 1: Inventory.** Run the sweep recipe; record the `workflows-core` hits, each with a disposition, and the before-count.
- [ ] **Step 2: Classification.**
  - **§4's bullets.** Add the clause verbatim as the third bullet. Then `--enforce-model` "overrides all three (§10)".
  - **One sentence after the bullets:** what a Fable value is; that `/implement`'s guard, fallback and resume alone write the key; that nothing escalates to Mythos.
  - **The closing paragraph:** at HIGH-RISK, an Opus, Sonnet or Haiku session's `/implement` codes on Fable once the run chose it. A fall below HIGH-RISK drops the escalation, and a rise back applies the recorded choice.
  - **§5:** an escalated family value `fable` is recorded as the family, beside §10's.
  - **§3.2 step 3, §9.1 and §9.2:** each statement of the rule gains the HIGH-RISK escalation, citing §4.
  - **Read the rest (extent face).** Read §10 and §3.2's closing blockquote against the clause. Change a sentence only where it states "both", or a coding model the clause now changes.
- [ ] **Step 3: `run-flags` §8,** `## 8. Fable escalation — \`$WORKFLOWS_FABLE_ESCALATION\``. It says:
  - the values and how they are matched;
  - that `/implement` alone reads it, at its guard and on a resume, as classification §4's third clause;
  - that it is set in the session's environment;
  - what it is not: no run flag, no `run_flags` member, no `Run flags:` line, no command-line flag, and no other command's Phase 0 touches it;
  - the one-run route, `--enforce-model=fable`, and what that also pins.

  The opening line names §8. §2's unpriced paragraph reaches "the Fable value `/implement`'s escalation takes (§8), which its guard prices the same way". Re-read that whole paragraph against the wider extent.
- [ ] **Step 4: Pages.**
  - **`environment.md`:**
    - a `## \`$WORKFLOWS_FABLE_ESCALATION\`` section in the page's per-variable shape (Resolution, When unset, when the value is bad, unreadable "not applicable"), saying where it is set and the `--enforce-model=fable` route;
    - it sits outside the page's `## Run flags` group (the flags' three defaults: `## Run flags` at `:105`, then the three `$WORKFLOWS_*` sections, all at `##`, running to the page's end, so a section appended after them reads as one of the group), so re-read that group's intro and keep it true: the new variable is no run flag's default;
    - "nine" becomes "ten" at every count of the variables: on the merged tree four, at `:3` ("reads nine user-settable variables", check 9's sentence), `:5` twice and `:99`;
    - "Four of the nine are …" names the setting;
    - the sentence saying each variable "is read by a reference this plugin ships" is rewritten true for a variable `/implement` alone reads;
    - the `dev-workflows` bullet gains it.
  - **`getting-started.md`:** a ``### `WORKFLOWS_FABLE_ESCALATION` `` entry, backticked as its neighbours' headings are (the variables' `###` headings run `:31` to `:63`, under `## What you set on your machine`), and both of its "nine"s (`:29`, `:53`).
  - **`references.md`:** the `run-flags.md` entry names §8.
- [ ] **Step 5: Re-count.** Run the sweep recipe; record the after-count against the expected one, and re-read every hit. Then `grep -rn 'nine' plugins/workflows-core/docs`; expect no count of variables.
- [ ] **Step 6: Gates.** Expected: `EXIT=0`. Check 5 now finds a reader for the documented variable, and check 9's "ten user-settable" agrees.
- [ ] **Step 7: Commit**: `feat(imp-g3): workflows-core — §4's Fable escalation clause and run-flags §8, WORKFLOWS_FABLE_ESCALATION`.

### Task 3: `implement.md` — the guard, cited at every dispatch

**Files:** modify `plugins/dev-workflows/commands/implement.md`:
- the new section `## The Fable escalation guard`, placed by R12;
- Phase 1.5's `model_routing` block (its `implementation_model:` comment, `:603`), and the paragraph after the block ("the code-writing ones — `code-writer` and `review-fixer` — pass `implementation_model`", `:609`);
- the run-state contract, in Phase 1.4's *What it holds*:
  - a `fable_escalation` bullet after the `routing` bullet (`:441`, "`routing` — `{"block", "history"}`"), before the `branch_answer` bullet;
  - the `step_groups` bullet's member list and meaning (`:454`, "`step_groups` — `[{"steps", "plan", "attempt", "status", "report", "answer", "left_to_caller"}]`");
  - one sentence beside the `KEYS` paragraph ("The file holds exactly these keys", `:470`): `fable_escalation` reads as its default in a file an earlier release wrote without it;
- every dispatch site of `code-writer` and `review-fixer`, and Phase 3A step 1's *Each dispatch* append object;
- any of the six class-change sites (Step 1) whose re-resolution does not already cite §4's rule.

**Interfaces:**
- Consumes Task 1's key and fill, and Task 2's §4 clause and `run-flags` §8.
- Produces the section and its paragraphs, *When it runs*, *Who is escalated*, *The setting*, *The question* and *What it writes*. Task 4 adds *The fallback*, and Task 5 *On a resume*.

- [ ] **Step 1: Inventory.**
  - **Dispatch sites.** For each dispatch, list the first record it makes (`step_groups` append, `failure_file`, `before dispatch:` tree record) and the arrow line: Phase 3A step 1's *Each dispatch* (`:941`, arrow `:943`), Phase 3B step 1 (`:1108`, arrow `:1110`), the Phase 3.5 fix attempt (`:1078`, arrow `:1080`), the Review-fixer sub-step (`:1207`, arrow `:1209`) — four arrows in all. On the merged tree Phase 3B step 1 dispatches "with the request Phase 3A step 1 writes, between the `before dispatch:code-writer` and `after dispatch:code-writer` tree records that step takes around each dispatch": it names no record of its own. Also list every prose dispatch of `review-fixer`; each must dispatch "as" a site that cites the guard. On the merged tree they are "invoke the review-fixer agent" twice (`:1188` BLOCK, `:1189` PASS WITH RECOMMENDATIONS, each "see Review-fixer sub-step below"), "as the Review-fixer sub-step makes one" (`:1203`), "dispatches `review-fixer` once more … as the Review-fixer sub-step dispatches one" (`:1204`) and "dispatch `review-fixer` as above" (`:1226`, the plan ruling's second dispatch); IMP-G5's sentence "Every `review-fixer` dispatch — the one below, a plan ruling's second dispatch (below) and the pass an **Apply** makes" (`:1207`) enumerates them. The `code-writer` prose dispatches are Phase 3.5's two directed fixes, "made as step 6 makes one" (`:1074`) and "made as an attempt is" (`:1091`); the restart table's re-dispatches are Task 5's. Record the counts.
  - **The six class-change sites** that write `routing`, `class` and `coding_model`: five tagged ``writes run-state `routing`, `class`, `coding_model` `` (`:631`, `:740`, `:811`, `:995`, `:1187` — the last now reads "…`coding_model`, and `review_in_hand`: `null`, … in one `set`"), and Phase 1.5's ``writes run-state `routing.block`, `class`, `coding_model` `` (`:591`). On the merged tree these are:
    - Phase 1.5's *Resolve the per-step routing* (`:591`);
    - Phase 1.6's `fan_out = true` floor (`:631`);
    - Phase 2A's *Re-test the class against the plan* (`:740`);
    - Phase 2B's `### Re-classification` ("If the return contains `### Re-classification`", `:811`);
    - Phase 3A step 5's raise ("Re-classified upward during implementation", `:995`, its sub-step 1 — step 5, not step 1);
    - Phase 3B step 7's accepted `### Re-classification` ("Accept revised classification (Recommended)", `:1187` — step 7, *Act on the return*, which reads step 6's review).

    Quote each one's §4 citation; on the merged tree only `:995` says "by §4's coding-model rule". A site that re-resolves `implementation_model` without citing §4's rule gains "by §4's coding-model rule". Phase 0's *Resuming* step 8 (`:95`, "**Routing** is resolved again") re-resolves `routing` and `coding_model` as Phase 1.5 does, untagged and with no `class` write: it is no seventh site here, and Task 5 owns it.
  - Run the sweep recipe over this file, and record its before-count.
- [ ] **Step 2: Write the section's five paragraphs**, exactly as the Global Constraints' guard, setting, question and record state them.
  - **Self-contained.** It names the three values and the `printenv WORKFLOWS_FABLE_ESCALATION || true` read itself, so it needs no `run-flags` reload after a compaction.
  - **Its calls**, by R11: the reads in one Bash call; `run-flags` loaded only under `ask` or an escalating outcome; the `set` chained onto the run's next Bash command after the guard.
  - **The question.** It is presented verbatim, with R1's unpriced wording, then the free-text rule.
  - **The setting's notice.** An unrecognised value prints its one line in the same guard run.
  - **One sentence:** the six class-change sites, not the guard, apply a recorded choice, by re-resolving with §4.
- [ ] **Step 3: Cite the guard at each dispatch**, with "First run *The Fable escalation guard*.", where R11 places it.
  - At Phase 3A step 1, at the opening of the *Each dispatch* paragraph.
  - At the Phase 3.5 fix attempt, before its `failure_file` and append text.
  - At the opening of the Review-fixer sub-step.
  - At Phase 3B step 1, where its own records begin, unless it makes them through Phase 3A step 1's *Each dispatch*.
  - **The `model:` placeholders.** Each arrow line's placeholder gains "; at HIGH-RISK, the Fable value `fable_escalation.choice` holds, where it holds one".
  - **The append object.** Phase 3A step 1's *Each dispatch* object gains `"model": "<run-state coding_model>"`. Phase 3.5's fix attempt appends "as Phase 3A step 1 makes one"; confirm it, and change it only if it lists the members. On the merged tree it reads "Then make the dispatch as Phase 3A step 1 makes one — its report file, its `step_groups` entry appended before it, here with `"steps": []`, `"plan": null` and `"attempt"` that number, the diff so far, and its two tree records": it names only the three members it overrides, so `model` comes with Phase 3A step 1's object.
- [ ] **Step 4: Phase 1.5 and the contract**, as Files lists. The `step_groups` bullet says what `model` holds, by the Global Constraints' wording.
- [ ] **Step 5: Review Focus 2, 3 and 5, and the free-text answer.** Quote, in the report, the sentence that decides each. A case with no deciding sentence is a gap to fix now.
- [ ] **Step 6: Close.**
  - **Order, by offset.** *Each dispatch* is one long line, so line numbers cannot order the citation against the append. For each site, compare offsets in the whitespace-collapsed text: the last "Fable escalation guard" before the site's first record, against that record, and against the site's IMP-G5 `before dispatch:` tree record, which on the merged tree follows that record at all three sites. Add Phase 3B step 1's pair where it makes its own records. A phrase that changed raises `ValueError`: re-derive it, never drop the site. On the merged tree each anchor below resolves: every opening phrase once; `"steps": [` at `:941` and `:1078`, `dw-impl-review-XXXXXX` at `:1207` and `:1225`, each first match after its opening being the site's own.
    ```bash
    python3 - <<'PY'
    import re
    t = re.sub(r"\s+", " ", open("plugins/dev-workflows/commands/implement.md", encoding="utf-8").read())
    sites = [  # (the site's opening phrase, its first record)
        ("**Each dispatch.**", '"steps": ['),
        ("**Each fix attempt is a `code-writer` dispatch", "dw-impl-failure-XXXXXX"),
        ("**Review-fixer sub-step**", "dw-impl-review-XXXXXX"),
    ]
    for head, rec in sites:
        h = t.index(head)
        r = t.index(rec, h)
        b = t.index("before dispatch:", h)
        g = t.rfind("Fable escalation guard", 0, r)
        print(head, g, r, b)
        assert h - 300 <= g < r < b, head
    PY
    ```
  - Each arrow's placeholder carries the clause, and the citation count equals Step 1's site count.
  - Run the sweep, and record the after-count against the expected one.
  - `grep -rn '\$WORKFLOWS_FABLE_ESCALATION\|WORKFLOWS_FABLE_ESCALATION-' plugins/dev-workflows` prints nothing.
- [ ] **Step 7: Gates.** Expected: `EXIT=0`, `check-questions` passing.
- [ ] **Step 8: Commit**: `feat(imp-g3): /implement's Fable escalation guard, before every code-writer and review-fixer dispatch`.

### Task 4: `implement.md` — the fallback, the report, the invariants

**Files:** modify `plugins/dev-workflows/commands/implement.md`:
- the guard section's *The fallback* paragraph;
- Phase 3A step 1's *Read the return* rule ("It is **unreadable** where the dispatch failed outright" and "An unreadable return is retried once with the same request", both `:964`);
- Phase 3B step 7's Review-fixer sub-step ("Wait for the fix report.", `:1218`), and IMP-G5's sentence opening "Every `review-fixer` dispatch — the one below, a plan ruling's second dispatch (below) and the pass an **Apply** makes" (`:1207`): R8's retry is a `review-fixer` dispatch too, made between its own `before dispatch:review-fixer` and `after dispatch:review-fixer` records, so it joins that sentence's list — as `code-writer`'s retry already sits in *Each dispatch*'s "Every dispatch of this step — a retry, and each dispatch afresh after a return, included — is made between two tree records";
- R16's pass sites in Phase 3B step 7: the BLOCK branch's `NEEDS HUMAN` sentence ("If `Stop condition flag` is `NEEDS HUMAN`, do not re-review: surface the deferred BLOCKER(s) to the user with the reason `review-fixer` gave and stop", `:1188`); the PASS WITH RECOMMENDATIONS branch ("**PASS WITH RECOMMENDATIONS** — invoke the review-fixer agent", `:1189`); the post-re-review **Apply** bullet ("**After the re-review**, **Apply** dispatches `review-fixer` once more", whose "No review follows and its `Stop condition flag` stops nothing", `:1204`); and, after a plan ruling's second dispatch, "The BLOCK branch's `Stop condition flag` test then reads the two reports together" (`:1229`);
- Phase 3B's opening paragraph ("The code is written by `code-writer` on `implementation_model`", `:1103`);
- Phase 5's `### Classification`, beside the `Model routing: bypassed` line (`:1462`);
- `## Invariants`: the "ALWAYS dispatch `code-writer` and `review-fixer` with `model: <implementation_model>`" bullet (`:1677`, which ends "Opus is otherwise reserved for planning and review"), and one new ALWAYS bullet for the guard.

Also modify `plugins/dev-workflows/agents/review-fixer.md` (R15): the opening sentence of its `## A re-dispatch on a resume` section (`:99`–`:103`, hard-wrapped), "`/implement` can resume a run that stopped part-way — crashed, killed, or its session lost — and dispatch you again for the fix pass that run died in.", gains one clause covering R8's retry. Read the file with the Read tool first, so `.claude/rules/dev-workflows.md` and `dev-workflows-implement.md` load.

**Interfaces:** consumes Task 3's section and `step_groups[].model`. It produces *The fallback*, which Task 5's R9 sentence names, and the Review-fixer sub-step's *No fix report* paragraph (R16).

- [ ] **Step 1: Inventory.** Run the sweep recipe over this file, and record the before-count and every hit not yet rewritten.
- [ ] **Step 2: *The fallback*.** Write the Global Constraints' three conditions and four actions, the readable statuses, R6, R7, and the kept attempt number.
- [ ] **Step 3: Hook it in.**
  - **`code-writer`'s retry.** It goes "on the unescalated value where *The fallback* fires, else on the same model". The retried entry's `model` is the model it passes.
  - **`review-fixer`'s retry (R8, R15).** After "Wait for the fix report.", the Review-fixer sub-step gains R8's retry, worded as `code-writer`'s is: a dispatch that failed outright — the tool call returned an error and no agent reply — is retried once with the same brief, on the unescalated value where *The fallback* fires, else on the same model, and the retry's brief ends with one line more after its last, verbatim, `Resume note: An earlier attempt may have partly edited the files this task covers; read them as they stand and complete the work.` (R15), since the failed attempt may have applied part of its fixes and the brief shows none. The retry is a `review-fixer` dispatch, so it joins IMP-G5's list "Every `review-fixer` dispatch — the one below, a plan ruling's second dispatch (below) and the pass an **Apply** makes" (`:1207`) and is made between its own two tree records.
  - **`review-fixer.md` (R15).** Widen the opening sentence of `## A re-dispatch on a resume` by one clause, so that it also covers that retry — for instance "… and dispatch you again for the fix pass that run died in — and, within a run, dispatch you once more for a fix pass whose dispatch failed outright with no reply." Keep the file's hard wrap. Change nothing else in the section, the heading included: what the note means ("an earlier dispatch of yours with these same findings may have applied some of them and stopped before its Fix Report came back") and the three bullets hold for the retry as written. Re-read them to confirm.
  - ***No fix report* (R16).** After the retry, write the rule once in the Review-fixer sub-step, as a paragraph led ***No fix report.***: a second outright failure of any `review-fixer` dispatch — the BLOCK branch's pass, the PASS WITH RECOMMENDATIONS branch's pass (with any `NIT`s an **Apply** after the first review adds, or a pass made for them alone), a plan ruling's second dispatch, and the pass an **Apply** after the re-review makes — is the `review-fixer` `NEEDS HUMAN` stop, its reason that no fix report came back. It re-reviews nothing and runs none of the steps that read a Fix Report (the diff re-capture, `claims_file`, the deferrals, `followed_by`); it surfaces to the user that no fix report came back, naming the findings `review_file` handed the pass and saying the tree may hold part of the pass; and it stops as the BLOCK branch's `NEEDS HUMAN` stop does: Phase 4.6 first, with `clean_finish: false` (writes run-state `clean_finish`).
  - **Each pass's site (R16)** cites the rule in the same words, "(the Review-fixer sub-step's *No fix report*)", so each reads one way:
    - the BLOCK branch's `NEEDS HUMAN` sentence (`:1188`) reads the Fix Report ("the deferred BLOCKER(s) … with the reason `review-fixer` gave"); it gains the no-report case, which surfaces that no fix report came back instead. Quote, in the report, the sentence as it was and as it now reads;
    - the PASS WITH RECOMMENDATIONS branch (`:1189`) gains one sentence: a pass with no fix report stops the run, and never goes on to the offer to apply what a review leaves open, the unspent re-review or step 7.5;
    - the post-re-review **Apply** bullet (`:1204`): "No review follows and its `Stop condition flag` stops nothing" becomes "… stops nothing, save where no fix report came back, which stops the run (the Review-fixer sub-step's *No fix report*)";
    - "The BLOCK branch's `Stop condition flag` test then reads the two reports together" (`:1229`) says it is not reached where a plan ruling's second dispatch brought no report, that dispatch having stopped the run (the Review-fixer sub-step's *No fix report*).
  - **No other stop list changes.** Both lists that name "the `review-fixer` `NEEDS HUMAN` stop" — Phase 4.6's "Every run" list (`:1387`) and the list at `:1255` — name it for every pass alike, so they stay as they are, as do Ending early and every GIT-G1 section.
  - **The resume note's other statements (claim sweep, by subject).** Before and after the edits, list every statement of the resume note: `grep -rn 'Resume note\|A re-dispatch on a resume\|earlier attempt may have partly' plugins/dev-workflows`, and `## Resuming a stopped run`'s *The resume note* paragraph (`implement.md:1630`) and the `/implement` page's *How a resume goes on* (`docs/commands/implement.md:96`). Re-read each against R15; none says the note goes only with a resume's re-dispatch on the merged tree, so expect no other change, and change one only where it now says so. `CHANGELOG.md` entries are history, never edited.
- [ ] **Step 4: The report line.** Use the eight wordings (R13 tells 7 from 8), R4's and R5's counts-only lines, and the mixed-model counts (no `failed` entry, no `review-fixer` dispatch), read from `fable_escalation` and `step_groups[].model`.
- [ ] **Step 5: The invariants and Phase 3B's opening.**
  - The ALWAYS bullet gains the clause. Re-read its "Opus is otherwise reserved for planning and review" against Fable coding, and keep it true.
  - The new bullet: the guard before every `code-writer` and `review-fixer` dispatch, asked at most once a run; security-finding runs never escalated.
- [ ] **Step 6: Review Focus 4.** Quote its deciding sentence. Run the sweep, and record the after-count against the expected one.
- [ ] **Step 7: Gates.** Expected: `EXIT=0`.
- [ ] **Step 8: Commit**: `feat(imp-g3): /implement falls back once from Fable, reports the escalation, and states it as an invariant`.

### Task 5: `implement.md` — the escalation across an IMP-G5 resume

**Files:** modify `plugins/dev-workflows/commands/implement.md` — the sites as the merged tree names them:
- the guard section's *On a resume* paragraph;
- Phase 0's *Resuming* steps (the numbered list after "**Resuming.** On *Resume*", `:86`–`:116`). Its steps are cited by number across the file (*Resuming* steps 1, 5, 7, 8, 9, 10 and 11, "its step 9", "its step 11"), so add no numbered step and renumber none:
  - step 8 (`:95`), "**The lineage check** runs as on any run, into a new check file. **Routing** is resolved again where the file's `class` is set: the `model_routing` block, as Phase 1.5's *Resolve the per-step routing* resolves it, …, with `coding_model` its `implementation_model`." The settle (Step 2) goes here, before its **Routing** sentence, and that sentence re-resolves with the settled record — it is what builds the stdin's `routing` and `coding_model`;
  - step 9 (`:96`), "**Take the file over** with `init --resume`": its stdin keys stay as they are (`RESUME_KEYS` unchanged; `routing` as `{"block": <the block>}`, and `coding_model`, "where step 8 resolved them"); its tail paragraph, "Once it has exited `0`, read `step` as the file now holds it" (`:113`), is the step right after `init --resume`, where the `unreachable` re-test and the `set` go, beside the writes that tail already makes ("write what steps 4 and 5 left to write; append each line Phase 0 recorded");
- `## Resuming a stopped run` (`:1622`):
  - *What a re-entered step asks* (`:1628`), whose list "an answer in `clarifications.answers`, a `step_groups` entry's `answer`, a `triage` entry's `settled` or `offered`, a `check_run_answers` entry, `test_decision`, `branch_answer.answer`" names the answers the file holds: a `fable_escalation` whose `source` is `answer` is one, so it joins the list (extent face: the guard's question is now one a re-entered step can reach);
  - its two Phase 2A/2B rows, "`Phase 2A` or `Phase 2B`, `step_groups` empty" (`:1645`) and "`Phase 2A` or `Phase 2B`, `step_groups` not empty" (`:1646`);
  - the rows that dispatch `code-writer` or `review-fixer` again, and their `failed` writes — the merged tree says "written `failed`", never "marked `failed`" (0 hits): the step-group row "`3A.1`, `3A.5` or `3B.1`, or `Phase 3A` or `Phase 3B` with `step` `null`" (`:1649`, "dispatching that group again, with the resume note, as the step retries an unreadable return, the `null` written `failed` first and a fresh entry appended"); the row "`3B.7`, with `review_in_hand` `null`" (`:1655`, "a `review-fixer` pass, where one is due …, dispatched again, with the resume note"), which writes no `failed`; and the row "`3B.8` with `review_in_hand` `null`, `3.5.3` to `3.5.6`, or `Phase 3.5` with `step` `null`" (`:1657`, "the attempt the run died in, written `failed` first", and the directed fix's "It is written `failed`"). The "`Phase 2A` or `Phase 2B`, `step_groups` not empty" row reaches `code-writer` too, at "On approval the run returns to the phase that re-planned".

**Interfaces:** consumes IMP-G5's `peek`, `init --resume` and restart table, and Tasks 3 and 4. On the merged tree: the run writes nothing into the run-state file before step 9's `init --resume` (the *Resuming* opening paragraph says so); `peek` prints the whole file and, after Task 1, a file without the key with `fable_escalation` at its default; `init --resume` repoints each path location to its durable copy or nulls it, and Phase 1.4 persists `files.task_description_file`, so R3's "repointed to its durable copy or nulled" holds; every `set` after `init --resume` is this session's, the session guard (exit 9) applying.

- [ ] **Step 1: Locate each site by phrase.** Name each in the report.
- [ ] **Step 2: *On a resume*, before `init --resume`,** by R2 to R4. It settles the record from `peek`'s record (a file without the key reads `{null, null}`), against this invocation's flags, `current_model`, setting and reachability. It reads no file. The first rule that holds decides:
  1. Rows 1 or 2 hold: keep the record.
  2. `choice` is null: keep it.
  3. An escalated `choice`, with Fable unreachable now: `{unreachable, <unescalated>}`, and print a note naming the change.
  4. `answer`, `fallback` or `security`: keep it, a choice that is not a Fable value rewritten to this invocation's unescalated value. `security` is never re-tested.
  5. `setting`: re-read the setting, by the guard's read, its bad-value notice printed here too.
     - `always` gives `{setting, <escalated>}`; where Fable is unreachable, it gives row 4's record and line.
     - `never` gives `{setting, <unescalated>}`.
     - `ask` gives `{null, null}`.
  6. `unreachable`: keep it for now, its choice rewritten to this invocation's unescalated value. It is re-tested after `init --resume` (Step 3).
- [ ] **Step 3: The resume path**, on *Resuming*'s own steps.
  1. Settle the record by Step 2 — at *Resuming* step 8, before its **Routing** sentence, as part of that step.
  2. Re-resolve `routing` and `coding_model` with it, for `init --resume`'s stdin — step 8's **Routing** sentence, which then says it resolves with the record *On a resume* settled, never the file's (§4's clause reads run-state `fable_escalation`, and until step 9 the file is the earlier session's).
  3. Run `init --resume` — step 9, unchanged.
  4. On an `unreachable` record the file held (rule 6), never one rule 3 wrote in this resume, run rows 3 to 5 against the paths `init --resume` repointed or nulled — in step 9's "Once it has exited `0`" tail. A null or unreadable `task_description_file` makes row 3 hold; an `ask` outcome gives `{null, null}`.
  5. Send one `set` of the record, the block and `coding_model` with the next tool call, wherever the record changed from the file's — in that same tail, in one `set` with the writes it already makes there, where they fall in one call.
- [ ] **Step 4: The restart table.**
  - **The Phase 2A/2B rows** (both: `step_groups` empty and not empty): the guard runs before the first coding dispatch, so a resume past *Approve* still meets it.
  - **One sentence for every row that re-dispatches `code-writer` or `review-fixer`**, saying it meets the guard as any dispatch does, and that a `failed` the resume writes is no outright failure (R9). On the merged tree those rows are the step-group row (`3A.1`, `3A.5` or `3B.1`, …), the `3B.7` row with `review_in_hand` `null`, and the `3B.8`/`3.5.3`–`3.5.6` row; the "`step_groups` not empty" row reaches the step-group dispatches through its re-plan, which the Phase 2A/2B sentence above covers. On the step-group row the guard comes after "the `null` written `failed` first" and before "a fresh entry appended": the fresh entry is the re-dispatch's first record (R11), the `failed` write the dead entry's.
  - **What a re-entered step asks:** its list of answers the file holds gains `fable_escalation` where its `source` is `answer`.
- [ ] **Step 5: Review Focus 1, 2 and 5, and four scenarios.** For each, quote the deciding sentence:
  - an `answer` kept under a changed setting;
  - `setting: always` resumed under `ask`;
  - an escalated record with Fable now unreachable;
  - an IMP-G5-release file without the key.
- [ ] **Step 6: Gates.** Expected: `EXIT=0`.
- [ ] **Step 7: Commit**: `feat(imp-g3): /implement carries the Fable escalation across a resume`.

### Task 6: Pages, the handoff, rules, pointers — and the sweep's close

**Files:**
- `plugins/dev-workflows/docs/commands/implement.md`, at three sites:
  - the subagent paragraph's "`code-writer` and `review-fixer` run on the run's coding model (*Who writes the code*, below)" (`:46`);
  - the paragraph "`code-writer` and `review-fixer` run on the run's coding model, which the class decides" (`:52`, under `### Who writes the code`);
  - the related-pages line "as `code-writer` and `review-fixer` do from `MODERATE` up on a session not already on Opus, Fable or Mythos" (`:163`).

  IMP-G5 added the page's `### Resuming a stopped run` (`:67`); its *How a resume goes on* says "a question whose answer the file holds is not asked again", which the escalation keeps true, and names no model.
- `plugins/dev-workflows/docs/reference/model-routing.md`: its sentences on `/implement`'s coding model (`:22`, `:39`).
- `plugins/dev-workflows/docs/reference/environment.md`: its opening sentence, "Nothing else it reads is yours to set" (`:3`).
- `plugins/dev-workflows/references/handoff/code-writer.md`: the `implementation_model:` line's comment (`:84`; IMP-G5's *The resume note* paragraph now follows the request block).
- `.claude/rules/dev-workflows-implement.md`: the coding-model sentence in the "orchestrator writes no source code" bullet ("Both run on `workflows-core:model-routing/classification` §4's `implementation_model` — … `--enforce-model` over both"), amended by R14 alone; R12's fallback adds nothing else there (41 characters left before, 6 after).
- `.claude/rules/workflows-core.md`: the `run-flags.md` paragraph (`:30`, "`plugins/workflows-core/references/run-flags.md` is the **single source of truth** for the three run flags").
- `.claude/rules/workflows-core-model-routing.md`: a §4 bullet (R12), in its `## Model routing reference` list.
- `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md`: a pointer at its superseded non-goal (`:48`, "**No Fable escalation (part 2 of F).**"). IMP-G5 set the form at that file's resume non-goal: "*Later built as IMP-G5:* `docs/superpowers/specs/2026-11-12-imp-g5-implement-resume-design.md`".
- `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`: a pointer at row F part 2 (`:105`, the `| **F** |` row).

**Interfaces:** consumes every earlier task's names.

- [ ] **Step 1: The sweep, whole scope.** Run the recipe and record the before-count. Every hit not dispositioned by Tasks 2 to 5 gets one here; any other page the run finds joins Files.
- [ ] **Step 2: Pages.**
  - **The `/implement` page, all three sites:** the escalation, the question and its two answers, the setting (bare, documented by the companion `workflows-core` plugin), security-finding runs, the one fallback, the report line, and the `--enforce-model=fable` route.
  - **The model-routing page:** the HIGH-RISK clause.
  - **The `dev-workflows` environment page:** the setting `/implement` reads, documented by `workflows-core`. Name the variable in plain backticks: never as a heading and never bold-backticked, either of which check 5's reverse direction reads as documented here.
  - **Diagrams.** A changed mermaid label quotes `[ ] ( ) { } |` and `#`.
- [ ] **Step 3: The handoff.** The comment says `implementation_model` can be the escalated Fable value at HIGH-RISK.
- [ ] **Step 4: Rules.** Measure each file before and after; keep each under 20,000 characters, cutting nothing (`validate-catalog.py` warns above 20,000). On the merged tree: `dev-workflows-implement.md` 19,959, `workflows-core.md` 18,205, `workflows-core-model-routing.md` 4,548.
  - **`dev-workflows-implement.md` (R12's fallback, R14).** Fewer than 150 characters are left (41 on the merged tree), so R12's clause is not added here: it lives only in `workflows-core-model-routing.md`, and the report says so. The one edit here is R14's:
    1. Measure: `python3 -c "print(len(open('.claude/rules/dev-workflows-implement.md',encoding='utf-8').read()))"`. Expected `19959`; a different number means the file moved since the pre-flight — re-derive the headroom before going on.
    2. Count the old string: ``; `--enforce-model` over both`` occurs exactly once (the "orchestrator writes no source code" bullet). Replace it with ``; at `HIGH-RISK`, Fable where chosen; `--enforce-model` over all``.
    3. Measure again with the same command. Expected `19994`: the file then has **6 characters of headroom** below the 20,000 warning. The report states both numbers and the 6, and that every later edit to this file must cut or move text out first (Task 7 puts that in the release notes).
    4. Re-read the whole bullet (extent face): "Both run on … — `current_model` at `SIMPLE`; from `MODERATE` up, …; at `HIGH-RISK`, Fable where chosen; `--enforce-model` over all — re-resolved at every class change for the dispatches after it" must read true against §4's three clauses. Its sweep disposition is *rewritten*.
  - **`workflows-core.md`:** §8's setting, read by `/implement` alone at its guard, outside `strip-run-flags`.
  - **`workflows-core-model-routing.md`:** the clause, the guard, fallback and resume as its writers, and security fixes unescalated.
- [ ] **Step 5: The pointers.** Each is one line naming this design.
- [ ] **Step 6: Close the sweep.** Record the after-count against the expected one, and the number rewritten. Re-read each rewritten paragraph whole (extent face).
- [ ] **Step 7: Gates**, plus `node scripts/mermaid/check-mermaid.mjs --root .` where `node` exists. Expected: `EXIT=0`.
- [ ] **Step 8: Commit**: `docs(imp-g3): pages, the code-writer handoff, rules and pointers for the Fable escalation`.

### Task 7: Release

**Files:**
- both `plugin.json` files, and `.claude-plugin/marketplace.json`;
- both `CHANGELOG.md` files;
- `.claude/rules/plugin-updates-coupling.md`, and the history file and pointers Step 2 names where a move is needed;
- `docs/superpowers/to-fix.md`.

- [ ] **Step 1: Versions.** Run `git fetch origin`, then take the next free **minor** of `workflows-core` and of `dev-workflows`, read from `origin/main` after IMP-G5. On `origin/main` at `3016ead8` they are dev-workflows 4.64.0 and workflows-core 1.85.1 (both `plugin.json`s equal to `marketplace.json`), so the next free minors are **dev-workflows 4.65.0** and **workflows-core 1.86.0** — re-read them at release, since other branches land on `main`. `plugin.json` must equal `marketplace.json`. Each CHANGELOG section is dated with the landing day (UTC), never left `— Unreleased`. **R14's note:** the `dev-workflows` section says, in one bullet under its `### Changed`, that `.claude/rules/dev-workflows-implement.md` now stands at 19,994 characters, 6 below `validate-catalog.py`'s 20,000 warning, so every later edit to it must cut or move text out first. Measure the file again before writing the numbers, with Task 6's command; where it differs from 19,994, write what it measures.
- [ ] **Step 2: The coupling bullet.** `**Update \`workflows-core\` <X> with \`dev-workflows\` <Y>**`, saying both directions:
  - a newer `/implement` beside an older `workflows-core` cites a §4 clause and a `run-flags` §8 setting that do not exist;
  - a newer `workflows-core` beside an older `/implement` names an escalation the command never makes.

  It goes after the last `workflows-core` bullet (on the merged tree "**Update `workflows-core` 1.85.1 with `dev-workflows` 4.64.0**", IMP-G5's) and before the two `prose-style` bullets that close the list. Measure the file. Above 19,000 characters, move its oldest bullets byte for byte into the highest-numbered `plugin-updates-coupling-history-*.md`, or into a new one where adding to it would pass 20,000 characters. Then update every range pointer: the coupling file's intro, the receiving file's title and intro, and `plugin-updates.md`. A new history file also needs:
  - the shared `paths:` frontmatter;
  - the "Read all N" count in `plugin-updates.md` and in the coupling file's intro;
  - its row in `CLAUDE.md`'s rules table. `CLAUDE.md` is at 34,608 characters against its 36,000 warning, so measure it after.

  On the merged tree no move is due: `plugin-updates-coupling.md` is 16,715 characters (12 bullets, its oldest `dev-workflows` 4.61.0's), so a bullet under about 2,280 characters leaves it below 19,000. For reference, the coupling set is four files — `plugin-updates.md` says "Read all four" — and the highest-numbered history file is `plugin-updates-coupling-history-3.md`, 10,549 characters, holding the bullets for `workflows-core` 1.75.0 to 1.80.0; `-history-2.md` is 19,965 and `plugin-updates-coupling-history.md` 19,359, neither with room.
- [ ] **Step 3: `to-fix.md`.** Delete the IMP-G3 entry ("**IMP-G3 — deferred: Fable escalation, sub-project F part 2, is not picked up.**", `:173`). In its place, add `**IMP-G3-MEASURE**` with the follow-up text verbatim.
- [ ] **Step 4: Gates.** Measure the rules files and `CLAUDE.md`. Expected: `EXIT=0`, and 0 warnings.
- [ ] **Step 5: Commit**: `release(imp-g3): workflows-core <X>, dev-workflows <Y>`.

### Task 8: Close

- [ ] **Step 1: Consistency.**
  - `implement.md`'s `fable_escalation` bullet lists exactly the five `source` values. Every record the guard section writes (in *Who is escalated*, *The fallback* and *On a resume*) uses one of them, and so does every report wording.
  - The question text in `implement.md` equals the Global Constraints' verbatim.
  - No `dev-workflows` file holds `$WORKFLOWS_FABLE_ESCALATION` or `WORKFLOWS_FABLE_ESCALATION-`.
  - No added executed regex holds `\d`: `git diff origin/main...HEAD -- plugins | grep '^+' | grep -F '\d'` is empty. (Scoped to `plugins/`: unscoped, it always hits this plan's own lines that name `\d`, the plan and the design being on the branch and not on `main`.)
  - At every dispatch site, the guard's citation precedes the dispatch's first record (Task 3 Step 6's offset check, re-run).
  - R14: `.claude/rules/dev-workflows-implement.md` measures 19,994 characters by Task 6's command (6 of headroom), and the `dev-workflows` CHANGELOG section says every later edit there must cut first.
  - R15: the `review-fixer` retry's brief carries the `Resume note:` line verbatim, and `agents/review-fixer.md`'s `## A re-dispatch on a resume` opening covers the retry.
  - R16: "(the Review-fixer sub-step's *No fix report*)" stands, in those words, at the BLOCK branch's `NEEDS HUMAN` sentence, the PASS WITH RECOMMENDATIONS branch, the post-re-review **Apply** bullet and the two-report flag test, and no `review-fixer` pass's site goes on without a Fix Report.
- [ ] **Step 2: GIT-G1.** `git diff --stat origin/main...HEAD` names none of the five never-edit files. No `implement.md` hunk falls in Ending early (the bold paragraph "**Ending early.**" before Phase 0, `:16`), the specs preflight, `branch-check`, `require-on-main`, the specs handover or the terminal `commit-artifacts`: name each hunk's section.
- [ ] **Step 3: The full CI list.** Every `run:` step of `.github/workflows/validate-catalog.yml`, with its `--selftest`s, mermaid where `node` exists.
- [ ] **Step 4: The whole-branch review.** This is the controller's job, with Fable as the final reviewer, handed this plan's Rulings and Review Focus.

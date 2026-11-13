# IMP-G3 — escalate `/implement`'s HIGH-RISK coding to Fable

**Date:** 2026-11-13. **Status:** design, revision 3, approved by the maintainer on 2026-11-13. It folds in two Fable design reviews of 2026-11-13, both *approve with changes*.

**Fixes:** IMP-G3 in `docs/superpowers/to-fix.md`. On 2026-11-12 the maintainer chose to build it despite the deferral; delete the entry when this lands.

**Completes:** sub-project F part 2 of `docs/superpowers/specs/2026-10-15-security-workflows-scan-design.md`, row F. It supersedes the non-goal at `docs/superpowers/specs/2026-10-17-implement-coding-subagents-design.md:48`.

## 1. The problem

`/dev-workflows:implement` writes its code through `code-writer`, and fixes through `review-fixer`. That covers review findings, every Phase 3.5 fix attempt and step 8's fix delta. Both run on `implementation_model`, which `workflows-core:model-routing/classification` §4 sets:
- at SIMPLE, `current_model`;
- from MODERATE up, `current_model` where it is Opus-tier (Opus, Fable or Mythos), else the §2 Opus chain.

So a session on Opus, or below it, codes HIGH-RISK work on its unescalated model, even where a stronger one is reachable. Fable code comes only from a Fable session, from a Mythos session, which codes on its own model, or from `--enforce-model=fable`.

Row F part 2 planned to escalate. It was deferred because no run had shown Opus falling short, and because a question before every HIGH-RISK run is friction. The maintainer has now chosen to build it. This design keeps the question but lets a user settle it once.

## 2. Goals, non-goals, anti-goals

- **Goal.** At HIGH-RISK, `/implement`'s `code-writer` and `review-fixer` run on Fable where all of these hold:
  - Fable is reachable;
  - the session is not on Fable or Mythos;
  - no `--enforce-model` is set;
  - the run is not a security-finding fix (§3.5);
  - the user agreed, once for the run or for all runs.

  This covers every dispatch of the two agents in the run: step groups, Phase 3.5 fix attempts, review fixes and step 8's fix delta. That is a decision, not an accident: the fixes touch the same risky code.
- **Goal.** One setting settles the question: always, never, or ask.
- **Non-goal: other roles.** `risk-planner` and `code-review` keep their own model. `code-review` is frontmatter-pinned `model: opus`.
- **Non-goal: other commands.** `/design`, `/specify` and `/vuln` are not escalated.
- **Non-goal: escalating to Mythos.** A harness that lists a `claude-mythos-*` id but no Fable id does not escalate.
- **Non-goal: a per-run override.** A user on `never` who wants Fable once has `--enforce-model=fable`. It also pins the planner, the reviewer and the scanners, and the environment page says so.
- **Anti-goal: spending silently.** Fable costs more than Opus, so the default asks and states the price multiple.

## 3. The design — decided

### 3.1 The setting: `WORKFLOWS_FABLE_ESCALATION`

**Where it is defined.** `workflows-core:run-flags` gets a new section, **outside** `strip-run-flags`. It says what the variable is: its values, how it is read, and that only `/implement` reads it.
- No other command's Phase 0 touches it.
- `strip-run-flags`, its `run_flags` record and its `Run flags:` line are unchanged.

**Values.**
- `ask` is the default: unset, empty, or only whitespace.
- `always`.
- `never`.

They are matched case-insensitively after trimming. Any other value is read as `ask`, and the guard reports it once (§3.2).

**Where it is read.** Only at the guard.
- **Spelling.** `/implement` names it bare, with no `$`, so `check-docs` check 5 asks for no `dev-workflows` environment entry. The `run-flags` section writes it **with** the `$`, `$WORKFLOWS_FABLE_ESCALATION`, so check 5's reverse direction finds a reader for `workflows-core`'s documented variable.
- **Self-contained guard text.** The guard can run after a compaction, when the Phase 0 `run-flags` text may be gone. So the guard paragraph in `implement.md` states the three values and the read itself; it does not rely on a reload.

**Where it is documented.** `workflows-core`'s `docs/reference/environment.md` gets its own section, including where the variable is set: the session's environment. Its user-settable count goes up by one. `workflows-core`'s `docs/getting-started.md` lists the variable too, as check 5 requires.

### 3.2 The guard — a state test, not a position

**When it runs.** Before **every** dispatch of `code-writer` or `review-fixer`, `/implement` runs this guard. It runs where all of these hold:
- run-state `class` is HIGH-RISK;
- run-state `fable_escalation.choice` is null;
- §3.3's table says the setting decides.

**What it does.** It resolves the escalation once and writes `fable_escalation`:
- **Under `always` or `never`:** apply the setting. Print one line naming it, with the model chosen.
- **Under `ask`:** ask the question below.

**Why a guard.** A guard covers every route to a HIGH-RISK dispatch the same way:
- Phase 2B's *Approve*;
- Phase 3A step 5's re-plan;
- a blocked return's *Revise*;
- a resume (IMP-G5);
- a compaction.

So the question can never be skipped, and it is asked at most once a run.

**The question:**
```
This change is HIGH-RISK. Its code can be written on Fable (<resolved Fable id or family>), the strongest model reachable, at <multiple> the per-token price of <unescalated model>, or on <unescalated model> as planned.
choices: ["Write it on Fable (Recommended)", "Write it on <unescalated model>"]
```
- **`<unescalated model>`** is §4's unescalated `implementation_model`, with its id or family as resolved. It is Opus, or the Sonnet floor where no Opus is available.
- **`<multiple>`** is Fable's input price over the unescalated model's input price, from the price table (`cost-prices.yaml`, resolved as the cost engine resolves it), rounded to one decimal place as `2.0×`.
  - **In a family-only harness**, where the versions are unknown, it is "about twice or more".
  - **Where either model is unpriced**, it is "a higher".
- **A free-text answer** is normalised to one of the two options or re-asked. It never writes the setting.

**What an escalation rewrites.** An answer or setting that escalates rewrites run-state `routing.block.implementation_model`, `routing.block.fixes_model` and `coding_model` to the escalated value. It appends to the `model_routing` block's `notes`.

**The class changes.**
- **A re-classification below HIGH-RISK** drops the escalation for the dispatches after it. `fable_escalation` stays recorded, and §4's clause no longer applies.
- **A later rise back to HIGH-RISK** applies the recorded choice. It never asks twice.

### 3.3 Who is escalated

The table is read at the guard.

| Case | Result |
|---|---|
| `--enforce-model` set | §10 overrides every clause. No guard. |
| `current_model` is Fable or Mythos | §4 already codes on the session's own model. No guard. |
| The run fixes a security finding (§3.5) | Not escalated. The guard writes `fable_escalation: {source: security, choice: <unescalated>}`, so the report states it once, from the key. |
| Fable not reachable | Not escalated. The guard writes `{source: unreachable, choice: <unescalated>}`. Under `always`, it also reports `WORKFLOWS_FABLE_ESCALATION=always, but Fable is not reachable — coding on <unescalated model>`. That happens once, because the key is now set. |
| Otherwise | The setting decides (§3.2). |

**Fable reachable.** This is `classification` §2's reading of the `task` tool's `model` parameter. Fable is reachable where the parameter lists a `claude-fable-*` id. In a family-only harness, Claude Code's, it is reachable where the parameter lists the `fable` family. Neither reading involves a stop.

**The escalated value.**
- Where ids are taken: the highest listed `claude-fable-*` id by version number.
- In a family-only harness: the family `fable`.

`classification` §5's dispatch rule passes either one.

### 3.4 When the escalated dispatch fails — a state test

**When it fires.** The fallback fires where all three hold:
1. the dispatch was escalated (its `step_groups` entry's `model`, or the `review-fixer` dispatch's recorded model, is the Fable value);
2. it **failed outright**: the tool call returned an error and no agent reply. That is `implement.md`'s own term for a `code-writer` dispatch (its unreadable-return rule, around line 858). This design gives `review-fixer` the same rule, which it lacks today: a `review-fixer` dispatch whose tool call returns an error and no reply has failed outright;
3. no escalated dispatch of this run has yet returned a readable result. That is checkable from the `model` the entries record. A Fable dispatch that once worked means the account has Fable, so a later outright failure is an ordinary failure, not unavailability.

**What it does.** The fallback **is** `implement.md`'s one retry for that failure, made on the unescalated model instead of the same one:
1. re-resolve `implementation_model` by the unescalated rule;
2. re-dispatch;
3. write `fable_escalation: {source: fallback, choice: <unescalated>}`;
4. add the report line.

Every other unreadable return keeps today's same-model retry. The failed attempt does not count against Phase 3.5's cap of 2.

### 3.5 Security-finding fixes are not escalated

**The rule.** A run is a security-finding fix where run-state shows either of these:
- a `[SEC#n]` in the task description (`files.task_description_file`), or in any `report.phase1_tasks` entry, as `implement.md` defines the run's own tasks (around line 270);
- `patches` non-empty, meaning a scan patch the run starts from (around line 268).

One such task among several makes the whole run unescalated, and a `[SEC#n]` mentioned only in passing still counts. That is the conservative reading. Such a run is coded on its unescalated model, whatever the setting is.

**Why.** Fable's cyber safety filters flag security requests, which Claude Code re-runs on Opus. The run would pay Fable's price for Opus code, and the record would say Fable. The scan design ruled the same way: the scan never escalates to Fable (`2026-10-15-security-workflows-scan-design.md`, around line 315).

**Other HIGH-RISK triggers** — data, contracts, concurrency, migrations, and authentication without a finding — are escalated as §3.3 says. Where `routing.block.reason` names an authentication or security trigger, the question adds one sentence: *Fable's safety filters may re-run some of this run's requests on Opus.* The `always` line carries the same sentence.

### 3.6 The record and the report

- **Run-state** gains `fable_escalation`, declared in `KEYS` as `{"source": null, "choice": null}`:
  - `source` is `answer`, `setting`, `fallback`, `security` or `unreachable`;
  - `choice` is the escalated value or the unescalated one.

  **A file that lacks the key.** Only `init` merges `KEYS` defaults; `load` returns the file as it is. So `run-state.py`'s `load` fills absent `KEYS` defaults on read, with a selftest case. A file written before this change then reads `fable_escalation` as `{source: null, choice: null}`.
- **Each `step_groups` entry** gains `model`: the model that dispatch passed. A report that says what was coded on Fable is then exact when the class changes mid-run.
- **`implement.md`'s report.** `### Classification` gains one line, beside the §10 bypass line, with one of six fixed wordings:
  1. `HIGH-RISK coding on Fable (<value>) — you chose it`
  2. `HIGH-RISK coding on Fable (<value>) — WORKFLOWS_FABLE_ESCALATION=always`
  3. `HIGH-RISK coding on <unescalated model> — you chose it`
  4. `HIGH-RISK coding on <unescalated model> — WORKFLOWS_FABLE_ESCALATION=never`
  5. `HIGH-RISK coding on <unescalated model> — Fable not reachable`
  6. `HIGH-RISK coding on <unescalated model> — Fable was not available (fallback)`

  A security-finding run says `HIGH-RISK coding on <unescalated model> — security-finding fixes are not escalated`. Where step groups ran on different models, the line names how many ran on each. A run that was never HIGH-RISK prints no such line.
- **The unpriced-id warning.** `run-flags`' unpriced-id warning covers an escalated id too, not only an enforced one.

### 3.7 On a resume (IMP-G5)

The resume carries `fable_escalation` from the file, then:
- **`source: answer` or `fallback`:** kept for the run, and never re-asked.
- **`source: setting`:** re-resolved from this invocation's setting, as IMP-G5 replaces per-invocation run flags. Where it now reads `ask`, `choice` is written back to null, so the guard asks.
- **`source: security` or `unreachable`:** re-tested by the guard's table on this invocation.
- **`choice` escalated, but Fable no longer reachable:** written as `{source: unreachable, choice: <unescalated>}`, with a note.

IMP-G5's restart table, Phase 2A/2B row, says the guard runs before the first coding dispatch, so a resume past *Approve* still meets it.

## 4. What changes where

- **`workflows-core:model-routing/classification`:**
  - §4's coding-model rule gains its third clause, before `--enforce-model`, which overrides all three: "at HIGH-RISK, a `current_model` that is not Fable or Mythos is escalated where `/implement`'s run-state `fable_escalation.choice` is a Fable value".
  - §5's record sentence names an escalated family value beside §10's.
  - The §4 closing paragraph, §9.1, the §9.2 row and §3.2 step 3 follow.
- **`workflows-core:run-flags`:** the new section (§3.1), and the unpriced-id warning's reach (§3.6).
- **`dev-workflows`:**
  - **`implement.md`:**
    - the guard before every `code-writer` and `review-fixer` dispatch;
    - the question;
    - the fallback, with `review-fixer`'s new failed-outright rule;
    - the security rule;
    - the record;
    - the report line;
    - the invariants;
    - the run-state contract's two bullets: the new `fable_escalation` key, and `step_groups` gaining `model`;
    - every restatement of the coding-model rule, located by phrase.
  - **`run-state.py`:** `KEYS`; the `KEYS_LINE` quote; and `load` filling absent defaults, with its selftest case.
  - **`references/handoff/code-writer.md`:** its model line.
- **Rules:** `.claude/rules/dev-workflows-implement.md` and `.claude/rules/workflows-core.md`'s `run-flags` paragraph.
- **Pages:** `workflows-core`'s `environment.md` and `getting-started.md`; `dev-workflows`' `/implement` page and `model-routing` page; any other page the grep finds.
- **`to-fix.md`:**
  - delete IMP-G3;
  - add the follow-up "measure the escalated runs: whether Opus review of Fable code misses what Fable review would catch, and how often Fable's filters re-run a request".
- **The claim sweep.** The population is every statement of the coding-model rule and of "Opus is otherwise reserved for planning and review". Derive it by grep across the claim-sweep scope. The review found these sites, which are where to start, not the whole set:
  - `classification` §4's closing paragraph, §9.1, the §9.2 row and §3.2 step 3;
  - `implement.md` around lines 481, 499, 837, 974, 997, 1004, 1103 and 1516;
  - `.claude/rules/dev-workflows-implement.md` and `.claude/rules/workflows-core.md`;
  - `dev-workflows/docs/reference/model-routing.md` and `docs/commands/implement.md`;
  - `references/handoff/code-writer.md:84`.
- **Release:**
  - `workflows-core` minor (the setting and the clause);
  - `dev-workflows` minor;
  - CHANGELOGs;
  - a coupling bullet. A newer `/implement` beside an older `workflows-core` reads a clause and a setting that do not exist, and the reverse names an escalation the command never makes.

## 5. Left to the builder

- The exact prose of the setting's section and the environment page.
- Where the guard's sentence sits in each dispatch's text. One shared paragraph should be cited at each dispatch.

## 6. Rulings (to check)

1. **HIGH-RISK only.** It is the policy's class for security-, data- and contract-sensitive work.
2. **Coding and fixing only,** including every fix loop. Planning and review keep their models.
3. **Fable is recommended when asked,** and the price multiple is stated.
4. **A setting read only by `/implement`, outside `strip-run-flags`.** No other command is touched.
5. **A guard on state, not a question at a position.** It is asked at most once, and survives a resume and a compaction.
6. **Security-finding fixes are not escalated** (§3.5), to match the scan's ruling, because Fable's cyber filters would make them pay twice. *This is the ruling most worth the maintainer's check.*
7. **One fallback re-dispatch** when Fable is unavailable to the account.
8. **Mythos sessions are not escalated, and nothing escalates to Mythos.**

## 7. Order and an open risk

**Order.** Build after IMP-G5. Both edit `run-state.py`'s `KEYS`, and IMP-G5's restart table must name the guard. The run-state machinery already exists on `main`, so the order avoids a conflict; it is not a dependency.

**Open risk.** The `code-review` gate stays on Opus while it reviews code Fable wrote. That is not new: `code-review` is frontmatter-pinned `model: opus`, so every Fable or Mythos session already ships its code under an Opus review. It is accepted, and recorded for measurement (§4, `to-fix`).

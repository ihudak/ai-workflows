---
name: prompt-grill-me
description: Log a corrective interaction as plugin feedback, then grill the fix inline — a bounded one-question-at-a-time interrogation (≤5 questions) of the correction following the embedded grilling technique. Self-contained; no plugin dependency.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Log a corrective interaction, then grill the fix: $ARGUMENTS

`/prompt-grill-me` is for when a command of this plugin family produced something wrong
and you want a **bounded one-question-at-a-time interrogation** (≤5 questions) of
the correction. It captures the **corrective triple** as plugin feedback, then
grills the fix **inline** following the embedded grilling technique
(`${CLAUDE_PLUGIN_ROOT}/references/grilling-technique.md`). `origin: prompt`.

The interrogation is self-contained — this command owns the grill and has **no
plugin dependency**.

Usage: `/prompt-grill-me <corrective request> [--skip-costs]`

---

## Phase 0 — Specs-repo preflight

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step, including the **verbatim** User prompt below, reads only the stripped string this leaves. Because this command's argument is free prose kept verbatim, a run-flag token is stripped only before or after the corrective request, never inside it (`workflows-core:run-flags` §3 step 1) — stripping consumes a **leading run** of run-flag tokens up to the first token that is neither a run flag nor the value of a preceding `--enforce-model`, plus a **trailing run** — the longest suffix of `$ARGUMENTS` that parses left to right as complete run-flag tokens, a trailing `--enforce-model <value>` pair counting as one unit and consuming whatever token follows it (§1) — at the very end; everything between is the corrective request, kept exactly as typed even where it contains a flag name. This command dispatches no `impl-maintenance` and invokes no model-routing skill, so an explicit `--skip-feedback` or `--enforce-model` fails `strip-run-flags`' applicability test and is reported `Run flags: --<flag> does not apply to /prompt-grill-me — ignored`; only `--skip-costs` applies.

Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its
`specs-preflight` entry point (§3) inline: flush any leftover session
artifacts from an earlier run, retry an artifact commit that failed to push,
and settle the branch. This runs against `$SPECS_PATH` only — `git -C
"$SPECS_PATH"`, never a `cd`, so whatever repository you are standing in is
untouched (§1 rule 1). Prompt-free, and silent unless it acts, a guard fires, or §3.1 reports a misconfigured `$SPECS_PATH`. If a guard fires, emit its §5 notice; if it returns
`specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1), carry that flag — the terminal
`commit-artifacts` step skips on it.

---

## Phase 1 — Identify the target

Infer the target command from recent context — which command's output you are
correcting. Ask only if genuinely ambiguous (one grouped prompt of 2–4 options; the
harness supplies the free-text escape). If no command applies, use `n/a`.

## Phase 2 — Persist the corrective triple

Cite `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` and call its
`emit-prompt` entry point (§6). Provide:
- **Friction** — what the command produced that was wrong.
- **User prompt** — `$ARGUMENTS`, **verbatim** (never paraphrased).
- **Resolution** — `Grilled the fix inline`.
- `command` (Phase 1), an inferred `category` (§1 vocab, reuse-first), `impact`,
  `key` (or `null`), `source`.

`emit-prompt` resolves the write target via the §2 specs-first ladder, formats
the entry with the two extra prose blocks (`origin: prompt`), appends per §3
(never silently skipped), and writes silently. Surface the persisted path.

**Then defer the cost entry.** This command cedes the session at Phase 3 and never regains control, so it
cannot measure its own spend. Record what a cost phase would have claimed, and
let the next cost-emitting run in this session claim it — cite
`${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md` §13 and write its §13.1
intent record now, before ceding:

- `command: /prompt-grill-me`, `phase: inferred`, `role: inferred` — the labels are
  resolved from `target_command` by §7 when the entry is finally written, exactly
  as they are for `/prompt` and `/feedback`.
- `target_command` — the Phase 1 target, as the bare §7 row name (`/document`,
  never `/document (keyed mode)`), so it matches the `command:` the feedback
  entry already carries.
- `key` (or `null`), `epic` (when the resolved kind is `epic`, else
  `null`), `source`, `plugin_version`, and `ceded_at`.
- `plugin` — this plugin's own `name`, from the same `.claude-plugin/plugin.json`
  the version is read from. The replay pairs a claim with a boundary by bare
  command name, which is unambiguous only because each command has one home in
  this marketplace; recording the home makes that a property of the record rather
  than of the current allocation.

Under `run_flags.skip_costs`, write the record with `"skip": true` (`workflows-core:cost-emission` §13.1): the next measured run still carves this segment out of its own window and then writes no entry for it.

**Append — never overwrite.** The file holds a JSON **array**: read it if it
exists, append this record, write it back; create it with a one-element array
when absent. A session may cede more than once, and a record that replaces its
predecessor destroys an attribution nothing can reconstruct.

The file is local, transient and **never committed** — the same status as the §3
checkpoint beside it. Writing it is silent; **it computes no cost and prints no
figure here**, because the spend this record stands for has not happened yet.

**Then commit session artifacts (terminal).** Cite
`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its
`commit-artifacts` entry point (§4) inline — before the Phase 3 grill, which is
interactive and may run long. It stages ONLY the §2.1 bounded artifact paths
inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session artifacts
(/prompt-grill-me)` — or `NOISSUE …` when no `key` resolved — and pushes.
It NEVER touches a code/docs repo, or the current working
directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; and skips entirely when
the run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice.
Print its §6 outcome line here, prefixed `Specs repo:`, with any guard notice
repeated in full. Repeat the `Run flags: …` line here too, whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6) — this is the run's last printed output before the Phase 3 grill takes over the session.

## Phase 3 — Grill the fix (inline)

Interrogate the correction directly, following
`${CLAUDE_PLUGIN_ROOT}/references/grilling-technique.md`:
- **Depth:** **bounded** — a capped set (≤5) of the highest Impact×Uncertainty
  questions about the fix, then stop; record any leftover high-impact gaps.
- **Stage:** the correction itself — why the original output was wrong, what the
  right shape is, and what should change so the mistake does not recur.

Follow the technique's mechanics (one question at a time, a recommended answer
each time, fact-vs-decision split, dependency order). This command NEVER
commits into a docs/code repo or the current working directory, where it is not the specs repository.
The Phase 2 `commit-artifacts` step commits ONLY `$SPECS_PATH`'s bounded
artifact paths (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §2.1).

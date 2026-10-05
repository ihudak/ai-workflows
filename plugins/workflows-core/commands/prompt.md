---
name: prompt
description: Log a corrective interaction — a command produced something wrong and you're fixing it — as plugin feedback, then act on your correction directly. Captures the friction, your verbatim prompt (secrets and private hosts redacted), and the resolution to the specs repo for the maintainer.
allowed-tools: Read Edit Write Bash Glob Grep Task Skill
---

Log a corrective interaction and act on it: $ARGUMENTS

`/prompt` is for when a command of this plugin family (`/specify`, `/design`,
`/implement`, `/document`, …) produced something wrong and you want to correct
it directly. It captures the **corrective triple** as plugin feedback, then
performs the correction. `origin: prompt`.

Captured (per `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` §1):
1. **Friction** — what the command produced that was wrong.
2. **User prompt** — your corrective request, **verbatim** (`$ARGUMENTS`), save the secrets, email addresses, internal hosts and home paths §1.1 of that reference redacts.
3. **Resolution** — what the AI actually did.

Usage: `/prompt <corrective request> [--skip-costs]`

---

## Phase 0 — Specs-repo preflight

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step, including the **verbatim** User prompt above, reads only the stripped string this leaves. Because this command's argument is free prose kept verbatim, a run-flag token is stripped only before or after the corrective request, never inside it (`workflows-core:run-flags` §3 step 1) — stripping consumes a **leading run** of run-flag tokens up to the first token that is neither a run flag nor the value of a preceding `--enforce-model`, plus a **trailing run** — the longest suffix of `$ARGUMENTS` that parses left to right as complete run-flag tokens, a trailing `--enforce-model <value>` pair counting as one unit and consuming whatever token follows it (§1) — at the very end; everything between is the corrective request, kept exactly as typed even where it contains a flag name. This command dispatches no `impl-maintenance` and invokes no model-routing skill, so an explicit `--skip-feedback` or `--enforce-model` fails `strip-run-flags`' applicability test and is reported `Run flags: --<flag> does not apply to /prompt — ignored`; only `--skip-costs` applies.

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
harness supplies the free-text escape). If no command applies, use `n/a`. **Normalise the answer
before it travels:** `target_command` must be a bare `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md`
§7 row name (`/document`, never `/document (keyed mode)`), so map a free-text
answer onto the row it names and use `n/a` when it names none — an unnormalised
value matches no row and silently degrades the entry to `plugin-feedback`/`n/a`.

## Phase 2 — Act on the correction

Perform the corrective request in `$ARGUMENTS` directly (the quick correction).
Keep a one-line summary of what you did — this becomes the **Resolution** block.

## Phase 3 — Persist the corrective triple

Cite `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` and call its
`emit-prompt` entry point (§6). Provide:
- **Friction** — what the command produced that was wrong.
- **User prompt** — `$ARGUMENTS`, **verbatim** (never paraphrased, and never redacted here: `emit-prompt` applies `feedback-emission.md` §1.1's redactions as it writes).
- **Resolution** — the one-line summary of the correction you just applied.
- `command` (Phase 1), an inferred `category` (§1 vocab, reuse-first), `impact`,
  `key` (or `null`), `source`.

`emit-prompt` resolves the write target via the §2 specs-first ladder, formats
the entry with the two extra prose blocks (`origin: prompt`), and appends per §3
(prompt entries are never silently skipped). Write silently — a single append.

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The terminal `commit-artifacts` step below runs unchanged either way.

**Otherwise, emit session cost.** Cite `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md`
and call its `emit-cost` entry point with `command: /prompt`, `phase: inferred`,
`role: inferred`, `target_command: <the Phase 1 target command, or `n/a`>`, the run's
`key` (or `null`) and `source`, and `plugin_version`. **`target_command` is
required** — §7 has no other source for it, so omitting it silently mis-attributes
every correction to `plugin-feedback`/`n/a`. The cost phase resolves the real labels from the **target
command** recorded above, per §7: a target with a fixed `phase`/`role` is
inherited outright, so correcting a `/specify` output is priced as
`specification`/`pe`; a target of `n/a`, a target with no §7 row, or a target
that is itself one of the four feedback commands resolves to
`phase: plugin-feedback`, `role: n/a`. A keyless run lands in §9's pending file
exactly as `/idea`'s does. Surface the persisted path (or the report-only
notice). This runs BEFORE the commit step below, per the emitter tail in
`${CLAUDE_PLUGIN_ROOT}/references/session-hygiene.md` §5 (feedback -> follow-ups ->
cost -> `resume.md` -> `commit-artifacts`; this command has no follow-ups or
`resume.md` step, so it goes feedback -> cost -> commit).

**Then commit session artifacts (terminal).** Cite
`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its
`commit-artifacts` entry point (§4) inline. It stages ONLY the §2.1 bounded
artifact paths inside `$SPECS_PATH`, commits `<KEY> Add dev-workflows session
artifacts (/prompt)` — or `NOISSUE …` when no `key` resolved — and pushes per §4 step 5. It NEVER touches a code/docs repo, or the current working
directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; and skips entirely when the
run carries `specs_git: blocked` (§3.3 G0) or `specs_git: misrooted` (§3.1, or `specs-root-check`'s stop), re-emitting that notice. Hold its
§6 outcome line for Phase 4.

## Phase 4 — Report

Repeat the `Run flags: …` line whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6). Surface the persisted path and any degradation notice (or, under `--skip-costs`, the `Session cost: …` line in its place), then the `Specs repo:`
outcome line from `commit-artifacts`
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §6), with any guard
notice repeated in full.

This command NEVER commits into a docs/code repo, or the current
working directory, where it is not the specs repository — only the correction itself edits your target files, as
you requested, and those edits are never staged. The terminal
`commit-artifacts` step commits ONLY `$SPECS_PATH`'s bounded artifact paths
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §2.1).

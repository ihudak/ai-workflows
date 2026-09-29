---
name: feedback
description: Log a manual note about this plugin family itself — friction you hit or an improvement you want — to the per-PRD feedback file in the specs repo, for the plugin maintainer to aggregate. Tied to no command; run any time.
allowed-tools: Read Edit Write Bash Glob Grep Skill
---

Log session feedback about this plugin family: $ARGUMENTS

`/feedback` captures a **manual note about this plugin family itself** — `workflows-core` and any plugin that declares it, whichever of the family's commands prompted the note —
friction you hit, or an improvement you want — and persists it per-PRD into the
specs repo so the plugin maintainer can aggregate feedback across engineers. It
is tied to **no command** and can be run any time. You author the prose; the
command fills the metadata and writes the entry. `origin: manual`.

This command captures signal about **the plugin**, not about your target
project. Target-project tooling advice does not belong here (see
`${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` §4).

Usage: `/feedback [<note>] [--skip-costs]`

---

## Phase 0 — Specs-repo preflight

**Strip the run flags first.** Execute `strip-run-flags` (`Skill(skill: "workflows-core:reference", args: "run-flags strip-run-flags")`) on `$ARGUMENTS` before anything else reads a token: it removes `--skip-costs`, `--skip-feedback` and `--enforce-model` (with any `=value`), resolves each against its environment default, and returns the `run_flags` record this run carries to its maintenance, cost and routing steps — or stops with `RUN_FLAGS_BAD_MODEL` / `RUN_FLAGS_MODEL_UNAVAILABLE` before any write. Every later step parses only what it leaves. Because this command's argument is free prose kept verbatim, a run-flag token is stripped only before or after the note, never inside it (`workflows-core:run-flags` §3 step 1) — stripping consumes a **leading run** of run-flag tokens up to the first token that is neither a run flag nor the value of a preceding `--enforce-model`, plus a **trailing run** of run-flag tokens at the very end of `$ARGUMENTS`; everything between is the note text, kept exactly as typed even where it contains a flag name. This command dispatches no `impl-maintenance` and invokes no `workflows-core:model-routing`, so an explicit `--skip-feedback` or `--enforce-model` fails `strip-run-flags`' applicability test and is reported `Run flags: --<flag> does not apply to /feedback — ignored`; only `--skip-costs` applies.

Cite `${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` and execute its
`specs-preflight` entry point (§3) inline: flush any leftover session
artifacts from an earlier run, retry an artifact commit that failed to push,
and settle the branch. This runs against `$SPECS_PATH` only — `git -C
"$SPECS_PATH"`, never a `cd`, so whatever repository you are standing in is
untouched (§1 rule 1). Prompt-free and silent when the specs repo is clean and
on its default branch. If a guard fires, emit its §5 notice; if it returns
`specs_git: blocked` (§3.3 G0), carry that flag — the terminal
`commit-artifacts` step skips on it.

---

## Phase 1 — Compose the note

1. `$ARGUMENTS` here is Phase 0's stripped string (leading run only — see above), so it may still contain a flag-shaped token if you wrote one inside the note itself. If it is empty, ask the user for the note (the friction and the
   improvement they want). Do not guess.
2. From the user's text, author two prose blocks — you may lightly tidy wording
   but never invent content the user did not express:
   - **Friction** — what about the plugin was wrong, slow, or missing.
   - **Suggested improvement** — the change they want.

## Phase 2 — Fill the metadata

Resolve, then confirm with the user in one grouped prompt (2–4 options; the harness
supplies the free-text escape):

- **`command`** — the exact slash-command name this note is about, inferred from
  recent context; or `n/a` if it is not about a specific command. Confirm.
- **`category`** — inferred from the controlled vocab in
  `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` §1
  (`missing-capability`, `wrong-output`, `ambiguous-prompt`,
  `missing-reference-doc`, `model-routing`, `manual-workaround`,
  `false-positive`, `docs-ux`, `other`); reuse an existing value when it fits.
  Confirm.
- **`impact`** — `blocker | friction | polish`.
- **`author`** — `git config user.email` run in the specs repo (best-effort;
  `unknown` if unset).
- **`plugin_version`** — read from
  `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`.

Also resolve `key` (from recent context, or `null`) and `source` (`specs | directory | none`).

## Phase 3 — Persist

Cite `${CLAUDE_PLUGIN_ROOT}/references/feedback-emission.md` and call its
`emit-manual` entry point (§6): resolve the write target via the §2 specs-first
ladder using `key` and `source`, format the entry per §1 (`origin:
manual`), and append per §3 (manual entries are never silently skipped — on an
`id` collision append a numeric suffix and warn). Write silently.

**Under `run_flags.skip_costs`**, do not call `emit-cost` and do not load `cost-emission`: execute `skip-cost` (`Skill(skill: "workflows-core:reference", args: "run-flags skip-cost")`) instead, which advances the checkpoint and drops any deferred record, and surface `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`). The terminal `commit-artifacts` step below runs unchanged either way.

**Otherwise, emit session cost.** Cite `${CLAUDE_PLUGIN_ROOT}/references/cost-emission.md`
and call its `emit-cost` entry point with `command: /feedback`, `phase: inferred`,
`role: inferred`, `target_command: <the Phase 2 `command` metadata field, or `n/a`>`, the run's
`key` (or `null`) and `source`, and `plugin_version`. **`target_command` is
required** — §7 has no other source for it, so omitting it silently mis-attributes
every note to `plugin-feedback`/`n/a`. The cost phase resolves the real labels from the **target
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
artifacts (/feedback)` — or `NOISSUE …` when no `key` resolved — and
pushes. It NEVER touches a code/docs repo, or the current working
directory, where it is not the specs repository; NEVER force-pushes; NEVER fails the run; and skips entirely when the
run carries `specs_git: blocked` (§3.3 G0), re-emitting that notice. Hold its
§6 outcome line for Phase 4.

## Phase 4 — Report

Repeat the `Run flags: …` line whenever Phase 0 printed one during this run (`workflows-core:run-flags` §6). Surface the persisted path and any degradation notice (e.g. the report-only tier, or, under `--skip-costs`, the `Session cost: …` line in its place), then the `Specs repo:` outcome line from
`commit-artifacts` (`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §6),
with any guard notice repeated in full.

This command NEVER commits into a docs/code repo, or the current
working directory, where it is not the specs repository. The terminal `commit-artifacts` step commits ONLY
`$SPECS_PATH`'s bounded artifact paths
(`${CLAUDE_PLUGIN_ROOT}/references/specs-repo-git.md` §2.1).

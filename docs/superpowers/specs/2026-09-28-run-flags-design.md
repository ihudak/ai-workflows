# Run flags — `--skip-costs`, `--skip-feedback`, `--enforce-model`

Date: 2026-09-28. Status: approved design, pending plan.

## Problem

Session cost and session feedback run on every pipeline command, and both are expensive: the cost phase loads the 772-line `workflows-core:cost-emission` reference through the loader (which reads the whole file) and reasons over it, and the feedback phase dispatches the `impl-maintenance` subagent. On a tight budget they eat into it quickly. Separately, model routing picks a model per step with no way for the user to say "run all of this on one model".

## Goals

1. A per-run way to skip the cost report — without misattributing this run's spend to the next command.
2. A per-run way to skip feedback collection — **except real defects**: a bug fixable in the plugin family or in ai-containers is still captured. Friction, wishes, polish, human mistakes and anything neither repo can fix are not.
3. A per-run way to enforce one model for every subagent the command dispatches, bypassing model routing's model selection. `--enforce-model=opus5.5` runs everything on Opus 5.5; `--enforce-model=opus` picks the highest reachable Opus.
4. Persistent defaults via environment variables, overridable per run.

## Non-goals

- Changing which steps a run executes. Classification still decides the process; enforcement changes models only.
- Switching the orchestrator's own model (impossible from inside a running command).
- Changing `emit-block` (capture-at-block), `resume.md`, or `commit-artifacts`.

## Decisions

| # | Decision | Chosen |
|---|---|---|
| D1 | Bug capture under `--skip-feedback` | A dedicated cheap subagent (`defect-reporter`), not a mode of `impl-maintenance` |
| D2 | `--enforce-model` scope | Models only; classification and gates unchanged |
| D3 | Enforced model unreachable | Stop at Phase 0 |
| D4 | Defaults | Flags **and** environment variables; a flag beats the env |
| D5 | Architecture | One shared authority `workflows-core:run-flags`, plus hooks into `classification.md`, `feedback-emission.md`, `session-cost.py` |

## 1. The flags and the run record (`workflows-core:run-flags`)

A new reference `plugins/workflows-core/references/run-flags.md` is the single source of truth for flag grammar, env resolution, model aliases, the `run_flags` record, and the skipped-cost path (§2 below).

| Flag | Env default | Values |
|---|---|---|
| `--skip-costs` | `WORKFLOWS_SKIP_COSTS` | bare = `true`; `--skip-costs=true\|false` |
| `--skip-feedback` | `WORKFLOWS_SKIP_FEEDBACK` | bare = `true`; `--skip-feedback=true\|false` |
| `--enforce-model=<m>` | `WORKFLOWS_ENFORCE_MODEL` | alias, full model id, or `routing` |

- **Precedence:** flag > env > off. `=false` and `=routing` exist to override an env default for one run. An env value is truthy for `1|true|yes` (case-insensitive); anything else is off.
- **Aliases:** `opus5.5` → `claude-opus-5-5`, `opus5` → `claude-opus-5`, `sonnet5` → `claude-sonnet-5`, `haiku4.5` → `claude-haiku-4-5`, and generally `<family><major>[.<minor>]` → `claude-<family>-<major>[-<minor>]`. The bare family names `opus`, `sonnet`, `haiku` resolve to the highest reachable model of that family (`opus`, `sonnet` walk the `classification.md` §2 / §2.1 chains top-down; `haiku` the §2.2 chain). A full id (`claude-…`) passes through. Anything else → `RUN_FLAGS_BAD_MODEL` (lists the accepted forms).
- **Reachability:** determined the way `classification.md` §2 already does — from the Agent tool's `model` parameter documentation. An enforced model that is not reachable → `RUN_FLAGS_MODEL_UNAVAILABLE`, naming the reachable models of that family. Both stops happen in Phase 0, before any work, write or preflight.
- **Parsing:** every command strips the three flags (with any `=value`) **first**, before any positional-argument classification — the `--docs` pattern from `workflows-core:docs-grounding` *Flags first*.
- **Applicability:**
  - `--skip-feedback` → the 25 commands that dispatch `impl-maintenance` (`grep -l 'workflows-core:impl-maintenance' plugins/*/commands/*.md`).
  - `--skip-costs` → the 27 commands with a `cost-emission` §7 row: the 25 that call `emit-cost`, plus `/prompt-brainstorm` and `/prompt-grill-me`, which defer.
  - `--enforce-model` → the 26 commands that load `workflows-core:model-routing`.
  - A flag given explicitly to a command it does not apply to is accepted and ignored with a one-line notice; an env default outside its set is silently ignored — so env defaults never break `/docs-serve`, `/feedback`, `/statusline` or `/docs-profile`.
- **The record:** Phase 0 builds `run_flags: {skip_costs, skip_feedback, enforced_model, source: {<flag>: flag|env}}`. It prints one `Run flags:` line only when any is non-default, and the final report repeats it.

## 2. `--skip-costs`

1. **No `emit-cost`, and `cost-emission.md` is not loaded.** The command's cost phase instead runs `run-flags` `skip-cost` inline: advance the checkpoint, then the existing `resume.md` write and `commit-artifacts` exactly as today.
2. **The checkpoint still advances**, so the next measured command's window does not absorb this run's spend (the misattribution `cost-emission` §3 exists to prevent). `session-cost.py` gains `--advance-only`: compute `new_checkpoint`, write it to `--checkpoint` itself, print one line. One Bash call, no reasoning.
3. **No specs-repo cost write**: no entry, no pending file, no §9 reconciliation offer.
4. **Deferred records** (`deferred-<session_id>.json`, `cost-emission` §13.1) waiting for this run to replay them become unmatchable once the checkpoint passes their boundary. The skipping run deletes the file and prints one line per record: `cost attribution for <command> dropped (--skip-costs)`.
5. **`/prompt-brainstorm` / `/prompt-grill-me` with `--skip-costs`** write their deferred record with `"skip": true`. The next measured run's `emit-cost` carves the segment out exactly as today (so the grill's spend is not filed under the following command) and then discards it instead of writing an entry. `cost-emission` §13.1/§13.3 document the field. If the next run also skips costs, rule 4 drops it.
6. **Report:** `Session cost: skipped (--skip-costs)` (or `(WORKFLOWS_SKIP_COSTS)`).

## 3. `--skip-feedback`

1. **New agent `workflows-core:defect-reporter`** — Read/Glob/Grep, no frontmatter model pin, short single-purpose prompt. Input: the same compact session handoff `impl-maintenance` takes. Output: a `### Defects` section, each entry with *location* (plugin file path, or the ai-containers repo), *evidence* from the session, and a *minimal repro* — or `none`.
2. **Under `--skip-feedback`** the maintenance phase dispatches `defect-reporter` instead of `impl-maintenance`. `impl-maintenance` is unchanged.
3. **Model:** a new `classification.md` §2.2 cheap chain — `claude-haiku-4-5`, then the §2.1 Sonnet chain. `--enforce-model` overrides it.
4. **Defect predicate** (owned by `feedback-emission.md` §4; `defect-reporter` cites it, never copies it) — fixable in the plugin family or ai-containers:
   - a wrong or self-contradictory instruction; a broken script, gate or hook; a missing or wrong reference; a command contradicting its own documentation; a crash;
   - a container environment defect: a missing tool, a wrong mount, a bad default.

   Excluded: friction, wishes, improvements, polish; user mistakes (wrong argument, typo, misaddressed key); target-project issues; Claude Code / model / external-service issues neither repo can fix.
5. **`emit-bugs`** — a new `feedback-emission.md` entry point: `origin: auto` entries through the same §2 ladder, §3 dedup and stable `id`; `impact` is `blocker | friction`, never `polish`. The §1 category vocabulary gains `environment-defect`. The orchestrator loads `feedback-emission.md` only when `defect-reporter` returned at least one defect.
6. **`emit-block` is unchanged** and fires with or without the flag.
7. **§4 widening applies to every run:** the plugin-facing predicate is widened to include ai-containers defects on full `emit-auto` runs too, so container bugs are no longer dropped.
8. **Lost under the flag:** the in-session Lessons Learned report (including target-project advice). Report: `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects`.

## 4. `--enforce-model`

1. **`classification.md` §10 "Enforced model":** when `run_flags.enforced_model` is set, every chain resolution — §2, §2.1, §2.2, and §8.3's oversized-slice escalation — returns that id. The `model_routing` block's every `*_model` field takes it, and gains `enforced_model: <id>` and `routing: bypassed`. `opus_available` stays truthful.
2. **Every dispatch passes `model: <enforced>` explicitly**, including the 19 agents pinned `model: opus` in frontmatter (the Agent tool's `model:` argument overrides frontmatter). The sites that say a dispatch is "frontmatter-pinned … no override" (43 lines across 17 command files by `grep -n "frontmatter-pinned" plugins/*/commands/*.md`, re-derive at plan time) are reworded to "no override unless §10 enforces a model", so no live sentence contradicts §10.
3. **Nested dispatch:** agents that dispatch agents (`docs-style-checker` → `prose-style-checker`; `upgrade-executor`, `vuln-fixer` via Task) receive the enforced id in their handoff and pass it on.
4. **Steps unchanged:** classification still runs; a SIGNIFICANT task still gets its plan and review gates, on the enforced model.
5. **Orchestrator:** stays on the session model. When `current_model` ≠ the enforced id, Phase 0 prints one advisory: `orchestrator runs on <session>; relaunch after /model <x> to enforce it there too`, and continues.
6. **Opus-session gates** (`/design`, `/create-ard` HARD gates; `/create-prd`'s degrade path) do not fire under enforcement — the user chose the model. (Testing the enforced id instead would pass an Opus gate on a Sonnet session, since the grill runs on the session model.) The §5 advisory is the only notice of a session/enforced mismatch.
7. **Degradation notices** (§2 "no Opus available", §9.3) are suppressed under enforcement; the final report says `Model routing: bypassed — enforced <id> (flag|env)`.
8. **Unpriced ids:** a reachable full id absent from `cost-prices.yaml` gets a Phase 0 warning; `cost-emission` §6.1's dominance warning covers the report.

## Files touched (indicative; the plan re-derives)

- New: `plugins/workflows-core/references/run-flags.md`, `plugins/workflows-core/agents/defect-reporter.md`, `plugins/workflows-core/references/handoff/defect-reporter.md` (if the handoff pattern applies).
- `plugins/workflows-core/references/model-routing/classification.md` (§2.2, §10), `feedback-emission.md` (§1 vocab, §4 widening, `emit-bugs`), `cost-emission.md` (§13 `skip` field, a pointer to `run-flags` skip-cost), `plugins/workflows-core/scripts/session-cost.py` (`--advance-only`, `skip` claims, selftests).
- Every applicable command: usage line, Phase 0 flag strip + `run_flags`, maintenance-phase and cost-phase guards, dispatch-site wording.
- Agents with nested dispatch: enforced-id propagation.
- Docs: each command's `docs/commands/*.md` synopsis; `workflows-core` `docs/reference/environment.md` (the three variables — check 5 requires the documenting plugin to read them, so only `workflows-core` documents them and the other plugins' environment pages link there); `session-cost.md`, `session-feedback.md`, `model-routing.md` reference pages; `agents.md` for `defect-reporter`.
- Instruction tiers: `CLAUDE.md` and `.claude/rules/workflows-core.md` agent/reference counts and the workflow map (re-derived, with the count command beside each number).
- `CHANGELOG.md` + version bump in all four plugins; `marketplace.json` in sync.

## Testing

- `session-cost.py --selftest` gains cases: `--advance-only` writes the same checkpoint a full run would, prices nothing, and refuses a missing `--checkpoint`. (`skip: true` claims need no script change — carving is identical; the discard is `emit-cost` prose.)
- The full gate chain from `.github/workflows/validate-catalog.yml`, run as one `&&` chain.
- A claim-expiry sweep (`CLAUDE.md` § Editing discipline) for "Cost ALWAYS runs", "cost ALWAYS runs", "frontmatter-pinned", "no override", "plugin family itself", and the `impl-maintenance` caller counts — each rewritten against the shipped behaviour, with before/after literal counts.

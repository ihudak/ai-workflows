# Run flags — `--skip-costs`, `--skip-feedback`, `--enforce-model`

Date: 2026-09-28. Status: implemented (branch `iv-gu/run-flags`).

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
| `--enforce-model=<m>` (or the pair form `--enforce-model <m>`) | `WORKFLOWS_ENFORCE_MODEL` | alias, full model id, or `routing`; missing/empty → `RUN_FLAGS_BAD_MODEL` |

- **Precedence:** flag > env > off. `=false` and `=routing` exist to override an env default for one run. An env value is truthy for `1|true|yes` (case-insensitive); anything else is off.
- **Aliases:** `opus5.5` → `claude-opus-5-5`, `opus5` → `claude-opus-5`, `sonnet5` → `claude-sonnet-5`, `haiku4.5` → `claude-haiku-4-5`, and generally `<family><major>[.<minor>]` → `claude-<family>-<major>[-<minor>]`. The bare family names `opus`, `sonnet`, `haiku` resolve to the highest reachable model of that family (`opus`, `sonnet` walk the `classification.md` §2 / §2.1 chains top-down; `haiku` the §2.2 chain). A full id (`claude-…`) passes through. Anything else → `RUN_FLAGS_BAD_MODEL` (lists the accepted forms).
- **Reachability:** determined the way `classification.md` §2 already does — from the Agent tool's `model` parameter documentation. An enforced model that is not reachable → `RUN_FLAGS_MODEL_UNAVAILABLE`, naming the reachable models of that family. Both stops happen in Phase 0, before any work, write or preflight.
- **Parsing:** every command strips the three flags **first**, before any positional-argument classification — the `--docs` pattern from `workflows-core:docs-grounding` *Flags first*. `--skip-costs` and `--skip-feedback` take any `=value`; `--enforce-model` takes `=value` or the two-token pair form `--enforce-model <value>`, which consumes the very next token as its value unconditionally. A bare trailing `--enforce-model`, or `--enforce-model=` with nothing after the `=`, is a missing value.
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

1. **New agent `workflows-core:defect-reporter`** — Read/Glob/Grep, no frontmatter model pin, short single-purpose prompt. Input: the same compact session handoff `impl-maintenance` takes, plus one field that handoff does not carry — `Plugin root:` (the dispatching command's own `${CLAUDE_PLUGIN_ROOT}`), since `defect-reporter`'s own `${CLAUDE_PLUGIN_ROOT}` always resolves to `workflows-core`'s installed files, never a sibling plugin's. Output: a `### Defects` section, each entry with *location* (a plugin file path confirmed against the Plugin root or `defect-reporter`'s own root, `ai-containers (<component>)` for a container candidate checked against the session's own observed evidence rather than a file, or the path as the session evidence states it, marked `location unverified`, where neither root reaches it), *evidence* from the session, and a *minimal repro* — or `none`.
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

1. **`classification.md` §10 "Enforced model":** when `run_flags.enforced_model` is set, every chain resolution — §2, §2.1, §2.2, and §8.3's oversized-slice escalation — returns that id. Every `*_model` field of the `model_routing` block that names a **dispatched** step takes it — `planning_model`, `review_model`, `detection_model`, `fixes_model`, `defect_model` (set only under `--skip-feedback`), and `implementation_model` where it names a delegated writer or executor — and the block gains `enforced_model: <id>` and `routing: bypassed`. A field recording the orchestrator's own inline work keeps the session model instead: `current_model` always, and `implementation_model` / `authoring_model` wherever a command codes or authors inline rather than delegating (`/implement`, `/prd-proposal`, `/brd-proposal` among them). `opus_available` stays truthful.
2. **Every dispatch passes `model: <enforced>` explicitly**, including the 19 agents pinned `model: opus` in frontmatter (the Agent tool's `model:` argument overrides frontmatter). The sites that say a dispatch is "frontmatter-pinned … no override" (43 lines across 17 command files by `grep -n "frontmatter-pinned" plugins/*/commands/*.md`, re-derive at plan time) are reworded to "no override unless §10 enforces a model", so no live sentence contradicts §10.
3. **Nested dispatch:** agents that dispatch agents (`docs-style-checker` → `prose-style-checker`; `upgrade-executor`, `vuln-fixer` via Task) receive the enforced id in their handoff and pass it on.
4. **Steps unchanged:** classification still runs; a SIGNIFICANT task still gets its plan and review gates, on the enforced model.
5. **Orchestrator:** stays on the session model. When `current_model` ≠ the enforced id, Phase 0 prints one advisory: `orchestrator runs on <session>; relaunch after /model <x> to enforce it there too`, and continues.
6. **Opus-session gates:** every gate or degrade path that tests `current_model` for an Opus session — not a named list, the whole class of them — does not fire under enforcement, since the user already chose the model. Examples that exist today: `/design`'s and `/create-ard`'s HARD gates, `/prd-proposal`'s and `/brd-proposal`'s stops, and `/create-prd`'s degrade path. (Testing the enforced id instead would pass an Opus gate on a Sonnet session, since the grill runs on the session model.) The §5 advisory is the only notice of a session/enforced mismatch.
7. **Degradation notices** (§2 "no Opus available", §9.3) are suppressed under enforcement; the final report says `Model routing: bypassed — enforced <id> (flag|env)`.
8. **Unpriced ids:** a reachable full id absent from `cost-prices.yaml` gets a Phase 0 warning; `cost-emission` §6.1's dominance warning covers the report.

## Amendments during implementation

Ten rulings changed this design's own text during implementation; two of them (the pair form and the `defect-reporter` handoff field) are also folded directly into §1 and §3 above, since the design's own table, Parsing bullet and Input sentence would otherwise still read the original, un-amended form — the other eight are recorded only here. One post-release fix (workflows-core 1.8.1, the last bullet) followed, recorded only here as well. Each is listed once so the approved design and the shipped behaviour do not silently diverge.

- **Free-text rule (new).** §1 "Parsing" assumed every command strips the three flags uniformly before any positional-argument classification. Implementation found a class of commands that keeps part of its argument as prose, kept verbatim — `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`, `/implement`, `/idea`, `/brd-split`, and `/document` in direct mode — so `strip-run-flags` strips only the **leading** and the **trailing** run of flag tokens around that prose span; every interior token, flag-shaped or not, is kept verbatim, and prose that genuinely ends in a flag name loses it to the trailing strip (`run-flags.md` §3 step 1).
- **Applicability is tested against the running command's own body, never a runtime grep.** §1's "Applicability" bullet gave the three `grep -l` recipes as though a running command executes them; an agent's cwd is the user's project and the installed plugin tree lives under `~/.claude/plugins/cache/`, so no such grep resolves at runtime. The three recipes are maintainer-only re-derivation tools; the runtime test reads the *running command's own body*, already in its context (`run-flags.md` §3 step 3).
- **Applicability is resolved before any flag value is validated — new.** §1 lists Aliases and Reachability validation ahead of Applicability, reading as if a value is checked before its command's applicability is even known. In fact applicability is resolved first, for all three flags, and only a flag found applicable ever reaches the alias/reachability validation: an explicit `--enforce-model` on a command outside its set is reported ignored and resolves to its default, **unvalidated**, so a malformed or unreachable value there stops nothing (`run-flags.md` §3 steps 3–4).
- **An out-of-set environment default is silently ignored, with no notice — unlike an out-of-set explicit flag.** An explicit flag outside a command's applicable set still prints the one-line `Run flags: --<flag> does not apply to /<command> — ignored` notice, but an environment variable set outside a command's set prints nothing, since the variable is global and would otherwise print on every run of every command that does not use it.
- **`--enforce-model` also takes the two-token pair form, resolved identically to `=value` — new.** §1's table and Parsing bullet originally named only the `=value` form. The pair form `--enforce-model <value>` consumes the very next token as its value unconditionally — so `/implement --enforce-model PROJ-12` treats `PROJ-12` as the requested model, never as a positional argument — and a bare trailing `--enforce-model` with no token after it, or `--enforce-model=` with nothing after the `=`, is a missing value that stops `RUN_FLAGS_BAD_MODEL` once the flag is confirmed applicable (`run-flags.md` §1, §3 step 1).
- **D3's ai-containers exception is narrower than "any missing tool."** The Non-goals section says `emit-block` (capture-at-block) is unchanged; its predicate in fact widened once, to a halt on a tool the `ihudak/ai-containers` image is meant to provide and lacks, captured as `category: environment-defect` — never a tool missing on the user's own machine or from any container not built from ai-containers, which stays an ordinary environment halt outside `emit-block`'s scope.
- **The `defect-reporter` handoff carries one field `impl-maintenance`'s does not: `Plugin root:` — new.** §3 item 1 said the agent takes "the same compact session handoff `impl-maintenance` takes"; in fact the dispatching command also passes its own `${CLAUDE_PLUGIN_ROOT}` as `Plugin root:`, since `defect-reporter`'s own `${CLAUDE_PLUGIN_ROOT}` always resolves to `workflows-core`'s installed files and never a sibling plugin's. The agent searches both roots to confirm a plugin candidate; one naming a path neither root reaches is **kept, not dropped** — reported with the path as the session evidence states it and marked `location unverified`. A container candidate has no file to confirm against: the session's own observed evidence is the check, and its location is `ai-containers (<component>)` (`run-flags.md` §4; `defect-reporter.md`).
- **`model_routing` fields split by dispatched-vs-inline.** §4 item 1 read as if every `*_model` field resolves to the enforced id under `--enforce-model`. A field that instead records the orchestrator's own inline work — `current_model` always, and `implementation_model` / `authoring_model` wherever a command codes or authors inline rather than delegating (`/implement`'s inline coding, `/prd-proposal`'s and `/brd-proposal`'s inline grill + authoring) — keeps the session model instead, because enforcement pins subagent dispatches, never the orchestrator's own session.
- **The Opus-session gate suppression is a class, not the named list.** §4 item 6's "Examples that exist today" reads as an enumeration; the shipped rule (`classification.md` §10) suppresses the whole *class* of gate or degrade paths that test `current_model` to require or prefer an Opus session, found by `grep -n "current_model" plugins/*/commands/*.md` and read one by one to tell a gate of this class from an ordinary routing record or report line — never by matching the examples' names.
- **`cost-emission.md` §13.4's "a command that can measure itself must" gains an exception — new.** That sentence stood unconditional there, which would forbid ever skipping a command's own cost phase; it now reads "…must — unless the user skipped it (`workflows-core:run-flags` §5)", so `--skip-costs` is a sanctioned way to skip cost measurement and §13's deferral machinery (for the two commands that provably cannot measure themselves at all) remains the only *other* exception.
- **Post-release fix (workflows-core 1.8.1): model selection is by family where the agent tool accepts only family names.** §1's Aliases and Reachability bullets assumed the Agent tool's `model` parameter lists resolved ids; it enumerates only `sonnet | opus | haiku | fable`, so `--enforce-model=opus5.5` could not be matched against it and a full id passed as `model:` failed the tool's schema. `classification.md` §2 now defines a family-only harness (a chain row is available when its family is listed; the harness picks the version) and §5 a dispatch rule (the record keeps the resolved id, `model:` passes its family name where the tool takes only families); `run-flags` §2 honours a bare family alias, and a version-specific form only when it is its family's newest chain row (passed as the family), stopping `RUN_FLAGS_MODEL_UNAVAILABLE` with a family-only message otherwise; `fable` gained an alias row; and the `Model routing: bypassed` line reports what was passed plus the requested value where they differ. This design's "`--enforce-model=opus5.5` runs everything on Opus 5.5" holds only where the tool accepts ids; in a family-only harness it runs on the harness's Opus.

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

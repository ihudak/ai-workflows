# Run Flags — Shared Reference

Single source of truth for the three run flags every applicable command accepts, their environment defaults, the model aliases, the `run_flags` record, and the skipped-cost path. Read through the loader; commands execute `strip-run-flags` in Phase 0 and `skip-cost` in their cost phase.

## 1. The flags

| Flag | Env default | Values |
|---|---|---|
| `--skip-costs` | `$WORKFLOWS_SKIP_COSTS` | bare = `true`; `--skip-costs=true\|false` |
| `--skip-feedback` | `$WORKFLOWS_SKIP_FEEDBACK` | bare = `true`; `--skip-feedback=true\|false` |
| `--enforce-model=<m>` | `$WORKFLOWS_ENFORCE_MODEL` | alias, full model id, or `routing` |

**Precedence: flag > env > off.** A flag given on the command line always wins over the corresponding environment variable, and an unset flag with an unset environment variable resolves to off (`skip_costs: false`, `skip_feedback: false`, `enforced_model: null`).

**Boolean flags (`--skip-costs`, `--skip-feedback`), stated explicitly because nothing elsewhere in the family parses a flag this way:** the bare form (`--skip-costs`, no `=`) resolves to `true`; `--skip-costs=false` resolves to `false`; any other `=value` (`--skip-costs=1`, `--skip-costs=yes`, `--skip-costs=anything-else`) resolves to `true`. The same three cases apply to `--skip-feedback`.

**Env booleans** (`$WORKFLOWS_SKIP_COSTS`, `$WORKFLOWS_SKIP_FEEDBACK`): `1`, `true` or `yes`, matched case-insensitively, resolve to on; every other value, and an unset variable, resolves to off.

**`--enforce-model` takes two equivalent forms:** `--enforce-model=<value>`, and the two-token pair `--enforce-model <value>` (a plain space, not `=`) — §3 strips either and resolves them identically. **The pair form always consumes the very next token as its value, whatever that token looks like** — so `/implement --enforce-model PROJ-12` treats `PROJ-12` as the requested model, never as a positional argument, and the run stops `RUN_FLAGS_BAD_MODEL` once `PROJ-12` fails every form in §2's table. A bare trailing `--enforce-model` with no token after it, and `--enforce-model=` with nothing after the `=`, are both a missing value; each stops `RUN_FLAGS_BAD_MODEL` — but, per §3's applicability step, only once `--enforce-model` is confirmed to apply to the running command, exactly like every other malformed or unreachable value. `--enforce-model=routing`, `$WORKFLOWS_ENFORCE_MODEL=routing`, and an unset flag with an unset environment variable all resolve to no enforcement (`enforced_model: null`).

**Flags may appear anywhere in the argument list** — before, after, or interleaved with a command's own positional arguments and other flags.

## 2. Model aliases

| Alias form | Resolves to |
|---|---|
| `opus` | the highest reachable model in `classification.md` §2 (the Opus rows only) |
| `sonnet` | the highest reachable model in `classification.md` §2.1 |
| `haiku` | the highest reachable model in `classification.md` §2.2 (the Haiku rows only) |
| `<family><major>` | `claude-<family>-<major>` |
| `<family><major>.<minor>` | `claude-<family>-<major>-<minor>` |
| `claude-…` | itself, unchanged |

`family` ∈ `opus | sonnet | haiku | fable`. Anything else given to `--enforce-model` or `$WORKFLOWS_ENFORCE_MODEL` — a form matching none of the six rows above — stops the run with `RUN_FLAGS_BAD_MODEL`, listing these six accepted forms.

**Reachability** is read exactly the way `classification.md` §2 already reads it — from the Agent tool's `model` parameter documentation, never assumed. A resolved id that is not reachable in the current environment stops the run with `RUN_FLAGS_MODEL_UNAVAILABLE`, naming the models of that family that are reachable.

**Both stops — and every validation in this section — apply only to an `--enforce-model` (or `$WORKFLOWS_ENFORCE_MODEL`) that §3's applicability step has already found applicable to the running command.** An inapplicable one — an explicit flag on a command outside its set, or an env default anywhere outside its set — is never parsed against this table, never reachability-checked, and never stopped on; §3 disposes of it first, before this section is ever reached for it.

**Both stops happen in Phase 0, before `specs-preflight` and before any write, and emit no feedback entry** — a bad or unreachable model name is a defect in the user's own invocation, not a gap in the plugin.

**Unpriced reachable id.** A reachable id that resolves but carries no key — exact or longest-prefix, per `cost-emission.md` §4 — in `cost-prices.yaml` does not stop the run: print one warning line, `⚠ <id> is unpriced in cost-prices.yaml — its cost will be recorded as null`, and continue. Like the two stops above, this warning is reached only for an applicable, enforced model — an inapplicable `--enforce-model` never resolves far enough to trigger it.

## 3. `strip-run-flags` entry point

1. **Strip the tokens, capturing whatever raw value each carries without judging it yet.** Remove every token matching `^--skip-costs(=.*)?$` or `^--skip-feedback(=.*)?$` (§1's boolean grammar reads whatever followed the `=`, if anything, once the later steps reach it). For `--enforce-model`, remove whichever of these is present: a token matching `^--enforce-model=(.*)$` (the captured group is the raw value, possibly empty), or the bare token `--enforce-model` together with the single token immediately following it, consumed as a pair regardless of what that following token looks like (§1) — and where a bare trailing `--enforce-model` has no token after it at all, remove just that one token, carrying no value forward. None of this — including a missing or empty value — is judged yet; that is step 4's job, and only for a flag step 3 has found applicable.

   **Free-text commands strip only a leading run.** Four commands capture the remainder of `$ARGUMENTS` as free prose kept verbatim rather than parsed into further positional arguments — `/feedback`, `/prompt`, `/prompt-brainstorm`, `/prompt-grill-me`. For these four, this step does not apply §1's "anywhere, interleaved" rule: it strips only the **leading run** of run-flag tokens — the pair form's `--enforce-model <value>` value included — and stops at the first token that is neither a run flag nor the value of a preceding `--enforce-model`. Everything from that token on is the user's own prose, kept verbatim even where it contains a flag name: these four commands have already finished stripping by the time such a token is reached, so it is text, not a flag.
2. **Determine each flag's raw source, per §1's precedence, resolving nothing yet.** For each of the three flags: `flag` when step 1 found an explicit token for it (whatever raw value it carried, including none/empty for `--enforce-model`); else `env` when the corresponding environment variable (§1's table) is set (whatever its value); else `default` (neither present). This step only records *where* a value would come from.
3. **Applicability — resolved before anything is validated.** Test each flag against the *running command's own body*, already in the executing agent's context, never by shelling out: a `grep -l … plugins/*/commands/*.md` does not resolve at runtime, since the agent's cwd is the user's project and the installed plugin tree lives under `~/.claude/plugins/cache/`, not under a repo-relative `plugins/` path. The runtime test, per flag: `--skip-feedback` applies iff the running command's own body cites `workflows-core:impl-maintenance`; `--skip-costs` applies iff the running command's own body calls `emit-cost`, or the running command is `/prompt-brainstorm` or `/prompt-grill-me`; `--enforce-model` applies iff the running command's own body invokes `workflows-core:model-routing`. A maintainer re-deriving these three sets from outside a live run — never the running command itself, which already has its own body in context — uses the three `grep` recipes instead, kept here as **that recipe and nothing more**, never as the runtime test: `--skip-feedback`'s set is `grep -l 'workflows-core:impl-maintenance' plugins/*/commands/*.md`; `--skip-costs`'s set is `grep -l 'emit-cost' plugins/*/commands/*.md` minus `statusline.md`, plus `prompt-brainstorm.md` and `prompt-grill-me.md`; `--enforce-model`'s set is `grep -l 'workflows-core:model-routing' plugins/*/commands/*.md`. A flag given **explicitly** to a command whose own body fails its test prints `Run flags: --<flag> does not apply to /<command> — ignored` and resolves to that flag's default for this run, **unvalidated** — step 4 never looks at its raw value at all, so a malformed or unreachable one on an inapplicable command stops nothing. An env default whose flag fails its test is silently treated as unset — no notice, same unvalidated default resolution — so setting `$WORKFLOWS_SKIP_COSTS` globally never breaks `/docs-serve`, `/feedback`, `/statusline` or `/docs-profile`. Only a flag that passes its test proceeds to step 4 at all.
4. **Resolve every flag step 3 found applicable, and only those.** `skip_costs` and `skip_feedback` resolve per §1's boolean grammar. `enforce_model` resolves per §2's alias table and reachability check: a missing or empty value (step 1) or a value matching none of §2's six forms stops `RUN_FLAGS_BAD_MODEL`; a resolved-but-unreachable id stops `RUN_FLAGS_MODEL_UNAVAILABLE`; a resolved, reachable id absent from `cost-prices.yaml` prints §2's unpriced-model warning and continues. A flag step 3 found inapplicable never reaches this step — its record value (step 5) is simply the default, whatever step 2 found.
5. **Build the record:**
   ```yaml
   run_flags:
     skip_costs: <bool>
     skip_feedback: <bool>
     enforced_model: <id>|null
     source:
       skip_costs: flag|env|default
       skip_feedback: flag|env|default
       enforce_model: flag|env|default
   ```
   For a flag step 3 found inapplicable, its `source` here is always `default`, whatever step 2 determined — the explicit-vs-env distinction only matters for a flag that actually applied, since an inapplicable one never produced a resolved, non-default value to attribute.
6. **Report when non-default.** When any of `skip_costs`, `skip_feedback` or `enforced_model` is non-default, print one line: `Run flags: skip-costs=<on|off>(<source>) skip-feedback=<on|off>(<source>) enforce-model=<id|routing>(<source>)`. When all three are default, print nothing here.
7. **Report an orchestrator/session-model mismatch.** When `enforced_model` is set and differs from the model the orchestrator is itself running under, print `Run flags: orchestrator runs on <session-model>; relaunch after /model <alias> to enforce it there too`, and continue the run unchanged.

Return `run_flags` and the stripped argument string — every later parsing step in the command reads only what this entry point leaves behind.

## 4. Skip-feedback

Under `run_flags.skip_feedback`, the command's maintenance phase dispatches `workflows-core:defect-reporter` in place of `impl-maintenance`, with the same compact session handoff `impl-maintenance` would have received, plus `Plugin root:` (the dispatching command's own `${CLAUDE_PLUGIN_ROOT}`, which `defect-reporter` searches for the command's, reference's, or agent's file a candidate names — its own `${CLAUDE_PLUGIN_ROOT}` reaches only `workflows-core`'s own installed files, never a sibling plugin's), on `model: run_flags.enforced_model` when it is set, else the `classification.md` §2.2 cheap chain. When `defect-reporter` returns at least one defect, persist them with `feedback-emission`'s `emit-bugs` entry point (`Skill(skill: "workflows-core:reference", args: "feedback-emission emit-bugs")`) in place of `emit-auto`; when it returns none, load `feedback-emission` not at all. `emit-block` (capture-at-block) is unaffected by the flag and fires exactly as it would without it. **What the user loses under this flag: the in-session Lessons Learned report** — `defect-reporter` returns defects only, never workflow advice, agent/skill suggestions, or target-project tooling notes.

## 5. `skip-cost` entry point

1. **Resolve session artifacts** exactly as `cost-emission.md` §1 names them — restated here, in full, because this path must never load `cost-emission.md`:
   - **`<cwd-slug>`** — the absolute `cwd` with every `/` and `.` replaced by `-`.
   - **Main transcript** — the newest `*.jsonl` directly under `~/.claude/projects/<cwd-slug>/`; its basename minus `.jsonl` is `session_id`.
   - **Subagents dir** — `~/.claude/projects/<cwd-slug>/<session_id>/subagents/`.
2. **Advance the checkpoint, and nothing else:**
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/session-cost.py" \
     --transcript <main transcript> --subagents-dir <subagents dir> \
     --checkpoint ~/.claude/dev-workflows/cost-state/<session_id>.json \
     --snapshot ~/.claude/dev-workflows/cost-snapshots/<session_id>.json \
     --now-ts <current UTC ISO8601> --advance-only
   ```
   `${CLAUDE_PLUGIN_ROOT}` here resolves to `workflows-core`, which ships `session-cost.py` — correct, since this reference is read through the loader skill regardless of which plugin's command is running.
3. **Drop any deferred claim.** If `~/.claude/dev-workflows/cost-state/deferred-<session_id>.json` exists, print `cost attribution for <command> dropped (--skip-costs)` once per record it holds, then delete the file — a checkpoint that has already advanced past those records' boundaries could never match them anyway.
4. **Write nothing into `$SPECS_PATH`.** No cost entry, no pending file, no §9-style reconciliation offer — none of `cost-emission.md`'s persistence ladder runs.
5. **Never fail the run.** A `session-cost.py` failure of any kind prints one line naming the failure and the run continues unaffected.

**`/prompt-brainstorm` and `/prompt-grill-me` never run `skip-cost`**, because both cede the session at their own Phase 3, before any cost phase could run at all. Under `--skip-costs` (or `$WORKFLOWS_SKIP_COSTS`) each instead writes its `cost-emission.md` §13.1 deferred record with `"skip": true`, so the replaying run's `emit-cost` still carves the ceded segment out of its own window — attribution stays correct — but then discards that segment instead of writing an entry for it.

## 6. Reporting

Four report lines, each printed only where the step that produces it fires:

- `Run flags: …` — §3 step 6 (non-default flags) and/or §3 step 7 (orchestrator/session-model mismatch).
- `Session cost: skipped (--skip-costs)` or `Session cost: skipped (WORKFLOWS_SKIP_COSTS)` — the command's cost phase, under `run_flags.skip_costs`, naming the source that set it.
- `Session feedback: bugs-only (--skip-feedback) — N defect(s) persisted` or `— no defects` — the command's maintenance phase, under `run_flags.skip_feedback` (§4).
- `Model routing: bypassed — enforced <id> (flag|env)` — wherever a command's final report would otherwise state its model-routing degradation, under `run_flags.enforced_model`.

**The final report repeats the `Run flags:` line** whenever §3 printed one during the run, so a reader of the report alone — without having watched the run live — still sees which flags were non-default and why.

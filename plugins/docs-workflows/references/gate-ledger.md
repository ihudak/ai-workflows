# Gate ledger (shared)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.

These shared references load by part — `escalation-rules`, `finding-triage`, `next-phase-offer` and `session-hygiene`. A citation of one names a rule: before applying it, load the part that holds it, `Skill(skill: "workflows-core:reference", args: "<name> <part>")`, the part its rule index names (`args: "<name> index"` loads the index; every part carries it), unless that part is already in this conversation word for word. A citation that names no rule the index holds loads the whole reference, `args: "<name>"`. Never apply a rule of these references from memory.

Single source of truth for how a command records whether each of its verification gates actually ran.

Consumed by `/document` (both modes), and by the two agents that read the ledger it produces: `doc-reviewer` (§4 and §6, for its verification-gate-integrity dimension) and `docs-style-checker`. Written generically so other commands can adopt it — see §6.

---

## 1. The problem it solves

A phase that says "Mandatory — never skip on your own judgement" is still skipped when the
orchestrator finds a plausible-sounding reason. `/document` Phase 6.4 has carried that exact wording
since v2.0.0 and was skipped anyway, and Phase 6.5's `(Recommended)` marker was moved onto the Skip
option on the same run. Emphasis is not enforcement.

The ledger removes the cell in which a run can write *"I decided this wasn't necessary."* Every gate
ends in one of six outcomes, and every non-run path terminates in a **named missing precondition**, a
**named missing tool**, or a **verbatim user decision**.

## 2. Outcomes

| Outcome | Means | Assignable by |
|---|---|---|
| `RAN` | The gate's primary mechanism executed. | evidence only |
| `DEGRADED` | Only a fallback executed. Records what did not run, why, and what CI will still check, or that nothing will. | evidence only |
| `FAILED` | Ran and found blocking problems. Feeds the caller's existing fix loops. | evidence only |
| `UNAVAILABLE` | Neither the primary nor a fallback ran, with the precondition met. **Not a resting state** — see §5. | the orchestrator, but never as a final answer |
| `SKIPPED_BY_USER` | The user chose to skip. Carries their decision quoted verbatim. | the user only |
| `NOT_APPLICABLE` | A named precondition is unmet. | evidence only |

There is no orchestrator-assignable "skipped". "Flaky, and the static analysis was sufficient" has
nowhere to go.

`DEGRADED` proceeds — a weaker check is not a documentation defect, and the final report prints the
row's `ci_still_checks` line: what CI will check that the run did not, or that nothing will (§6).
Total absence of coverage does not proceed.

**One gate, one outcome: `FAILED` outranks `DEGRADED`.** A gate that runs in parts — `build_check`
over several builds, `render_smoke_check` over several spaces — can end with one part `FAILED` and
another `DEGRADED`: one build fails on its content while another build's tool is missing, or one
space answers a 5xx while another times out. The row is `FAILED`, because a content failure is what
feeds the caller's fix loop, and the degraded part is still recorded in the row's `not_run` and
`ci_still_checks`, which such a row fills as a `DEGRADED` row does.

**`FAILED` also outranks a decision to proceed without another part.** Where one part failed on its
content and another did not run and the user declined it — a §5 conversion answered "Proceed without
this check", the toolchain preflight's decision on the same missing tool kept in its place, or a
Skip that declined that part's only remaining proof — the row is `FAILED`, not
`SKIPPED_BY_USER`: a content failure is never hidden behind a skip. The declined part is recorded in
`not_run` and `ci_still_checks` as a degraded part is, and the decision is kept in the row's
`user_decision`, quoted verbatim.

## 3. Row schema

The ledger is an in-context YAML block. The orchestrator **appends a row at the moment each gate
completes** — never reconstructs the ledger at report time from memory.

**One row per gate, created once.** The first writer to reach a gate creates its row; every later writer **rewrites that row in place** and never appends a second one. A row Phase 0's toolchain preflight pre-seeded is that gate's row — carry its `user_decision` forward rather than discarding it, whatever outcome the gate's own phase then rewrites around it, until the user answers a later question that itself decides that gate's outcome, or the part of it a `FAILED` row records as declined (§2): the row then quotes that answer in its place. Two rows for one gate id is a defect even though §6 does not name it: the report table reads every row, so a duplicate silently misstates what happened.

A phase whose outcome is not yet known at append time may write a **provisional** row, but only when a named later step in that same phase rewrites it before the phase ends — Phase 5.8's `Ledger (final)` and Phase 6.5's `Ledger (final)` are the two sanctioned cases. A provisional row is never the outcome a later reader sees.

```yaml
gate_ledger:
  - gate: <registry id from §4>
    phase: "<the phase that owns it>"
    outcome: RAN | DEGRADED | FAILED | UNAVAILABLE | SKIPPED_BY_USER | NOT_APPLICABLE
    mechanism: <what actually executed; omitted when nothing did>
    not_run:                                        # DEGRADED, or FAILED with a degraded or declined part (§2); non-empty
      - mechanism: <the primary mechanism that did not run>
        reason:    <why>
    ci_still_checks: <one line>                     # wherever not_run is; non-empty
    precondition_unmet: <the named precondition>    # NOT_APPLICABLE only, non-empty
    user_decision: "<the user's choice, verbatim>"  # SKIPPED_BY_USER, or FAILED with a declined part
                                                    # (§2): required, non-empty. Any other outcome: kept
                                                    # where Phase 0's toolchain preflight pre-seeded the
                                                    # row (above)
    findings: <count>                               # RAN / DEGRADED / FAILED -- see below
```

**`findings` records what this run saw; it is not a reproducible property of the files.** For a gate whose ladder is entirely deterministic — `toolchain_preflight`'s `command -v` probes, a repo linter with a pinned config — the count is a measurement and re-running it returns the same number. For a gate with an LLM in its ladder it is a **sample**. `style_check` is the live case: two `docs-style-checker` runs in one session against byte-identical files returned 2 findings and then 3, and the same defect came back under two different rule ids. That is expected of a semantic checker and is not a fault in it.

So: **read a `findings` count as "what this run reported", never as "how many defects the files contain"**, and never compare two runs' counts to conclude that something changed. A reviewer checking that a gate ran should look at the `outcome` and the `mechanism`, which are stable, rather than at a number that is not. The count stays in the ledger because it is a faithful record of the run — dropping it would lose that — but a consumer treating it as reproducible is reading it wrong.

## 4. The `/document` gate registry

| Gate id | Phase | Precondition | Primary | Fallback |
|---|---|---|---|---|
| `toolchain_preflight` | 0 | always (runs after profile resolution) | the required set's checks, as `toolchain-preflight.md` §2–§3 define them | none |
| `source_truth_verification` | 5.8 | ≥1 entry in `code_repos` | claim-class verification per `workflows-core:source-truth` §2–§3 | one supplementary direct grep against the resolved local path |
| `style_check` | 6.4 | ≥1 file written | the repo linter ladder **plus** `prose-style-checker` complementary | `prose-style-checker` alone |
| `repo_checklist` | 6.4 | the repo publishes authoring/verification guidance | `repo_verification_gates` applied to the written files | none |
| `build_check` | 6.5 S1 | write context is a buildable repo — `docs_repo`, or a confirmed `non_docs_repo`; a profile that records no build command still meets it | every `builds[]` entry's `command` where the profile records `builds[]`; else `commands.per_space.<space>.build` for every space in the render verification set, else whole-repo `commands.build` (`docs-profiles/render-verification.md` §1–§2) | the Step 2 dev-server boot |
| `render_smoke_check` | 6.5 S2 | buildable repo with ≥1 affected page | the dev server that publishes each affected page — one per page, never picked by space alone (`docs-profiles/render-verification.md` §2) | the manual pages-to-visit table |
| `image_review` | 5.6 | ≥1 candidate image (to add or possibly-stale) | the two-list review with per-occurrence decisions | none |

The registry mixes three shapes. Most entries are **output-verification** gates — they hold written (or about-to-be-written) content against a source of truth: `source_truth_verification`, `style_check`, `repo_checklist`, `build_check`, `render_smoke_check`. `toolchain_preflight` is an **environment preflight** — it runs before the run has any content at all, and checks the tools the other gates need rather than any output. `image_review` is an **input-side** gate — it accounts for a decision about what goes in, not a check on what came out. All three shapes are registered because the accountability need is identical: an unattributed image skip, like an unattributed missing tool, is exactly the failure mode this ledger exists to prevent.

The **Phase** column above is keyed mode's. Direct mode runs the same gate ids at different phases — `toolchain_preflight` at Phase 0, and both `style_check` and `repo_checklist` at Phase 3.5 (the checklist is *extracted* at Phase 0 but its row completes when the written files are held against it) — as the paragraph below sets out. A row's `phase:` field always names the phase where the gate **completes**, not where its inputs were gathered.

A gate whose precondition is unmet records `NOT_APPLICABLE` with the precondition named. It is never
silently absent from the ledger.

**Direct mode** (`/document` Mode B) registers exactly three gates: `toolchain_preflight` (Phase 0),
`repo_checklist` (Phase 0 extraction, checked at Phase 3.5), and `style_check` (Phase 3.5). The
other **four** ids never appear in a direct-mode ledger — not even as `NOT_APPLICABLE`:

- `source_truth_verification` — direct mode has no Phase 5.8, no folder read, and no `code_repos`.
- `build_check` and `render_smoke_check` — direct mode has no Phase 6.5 and no resolved profile to take build or dev-server commands from.
- `image_review` — direct mode has no Phase 5.6, and none of the sources that phase builds its two lists from (the specs scan, the folder attachments, the `<project_dir>` scan and the user's manual paths for the add list, and the `extend-existing` write targets Phase 5.5 confirms for the existing-image list). The candidate lists are the orchestrator's own in both modes — `doc-planner` neither supplies nor reads them — so their absence here is about the missing phase and its missing inputs, not about the planner.

Direct mode has no `doc-planner`, so its orchestrator extracts `repo_verification_gates` itself per
`${CLAUDE_PLUGIN_ROOT}/references/repo-verification-gates.md` §5.

## 5. Converting `UNAVAILABLE`

`UNAVAILABLE` — neither the primary nor a fallback ran, with the precondition met (§2) — is a real
coverage hole. The orchestrator converts it before the run continues, with a choice list bound by the
"Choice lists are presented verbatim" rule in `workflows-core:escalation-rules`:

```
choices: ["Install <named tool> and retry this gate", "Proceed without this check — record my decision", "Cancel the run"]
```

- "Install and retry" → re-run the gate and rewrite its row.
- "Proceed without this check" → rewrite the row as `SKIPPED_BY_USER` with the user's choice quoted
  verbatim in `user_decision` — or, where another part of the gate failed on its content, as
  `FAILED` with that choice in `user_decision` and the declined part in `not_run` (§2).
- "Cancel the run" → stop.

The orchestrator never selects among these on the user's behalf.

## 6. The reviewer contract

The caller passes the completed `gate_ledger` to its review gate. For `/document` that is
`doc-reviewer`'s **Verification-gate integrity** dimension. The reviewer raises a **BLOCKER** when any
of these holds:

- a registry gate has **no row** in the ledger;
- a row's outcome is `UNAVAILABLE` (§5 never converted it);
- `SKIPPED_BY_USER`, or `FAILED` with a declined part (§2), with an empty or absent `user_decision`;
- `NOT_APPLICABLE` with an empty or absent `precondition_unmet`;
- `DEGRADED`, or `FAILED` with a degraded or declined part (§2), with an empty `not_run` or an empty
  `ci_still_checks` — wherever §2 requires those fields, whatever the row's outcome.

**A `ci_still_checks` line that says no CI check runs, and why, is filled, not empty.** Where CI
runs nothing in the gate's place — the repository has no CI build, its CI runs no linter, or it
configures no repo-level linter at all — a line saying so with its reason ("none runs: the
repository has no CI build") is the record §2 asks for. Only an absent or blank field is empty. What
the line must never carry is a claim about CI that the repository cannot support: a line that names
a build or a linter CI runs on the pull request names one the repository's CI actually runs.

`DEGRADED` is otherwise not a finding — the reviewer notes it, and the final report prints its
`ci_still_checks` line.

## 7. Adopting this in another command

A command adopting the ledger declares its own registry table in the shape of §4 (gate id, phase,
precondition, primary, fallback), appends rows per §3, converts `UNAVAILABLE` per §5, and passes the
block to its review gate with the §6 contract. Nothing in §2, §3, or §5 is `/document`-specific.

## 8. Hard rules

- NEVER write a ledger row from memory at report time. Append it when the gate completes.
- NEVER record an outcome the evidence does not support — a gate that did not execute is not `RAN`.
- NEVER leave `UNAVAILABLE` as a final outcome; §5 always converts it.
- NEVER paraphrase the user's words in `user_decision`; quote the option they chose.
- NEVER omit a registry gate's row because it seemed irrelevant — record `NOT_APPLICABLE` and name the
  precondition.
- NEVER promote `DEGRADED` to a finding on its own; the reviewer's §6 list is exhaustive.

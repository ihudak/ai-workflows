# Model Routing by Task Complexity (Shared Policy)

This document is the **single source of truth** for how the pipeline commands of this plugin and of every plugin that depends on it (`/implement`, `/vuln`, `/upgrade`, `/frames`, and related commands) and their sub-agents classify tasks and route them to the
appropriate model. Every top-level orchestrator MUST load and follow this policy
before doing any planning, implementation, or review work.

---

## 1. Complexity Classes

Every task MUST be classified into exactly one of:

| Class         | Plain meaning                                                                 |
|---------------|-------------------------------------------------------------------------------|
| `SIMPLE`      | Trivial, mechanical, low blast radius (typo, comment, single-line tweak).     |
| `MODERATE`    | Localized feature/fix in 1–3 files, well-understood, no security implications.|
| `SIGNIFICANT` | Multi-file or cross-cutting, non-trivial design, real correctness risk.       |
| `HIGH-RISK`   | Security-, data-, or contract-sensitive; mistakes cause outages or breaches.  |

### 1.1 Classify as `SIGNIFICANT` or `HIGH-RISK` if **any** of the following apply

- Major framework or library upgrade (any **major** version bump, e.g. Spring Boot 2→3, React 17→18, Java 11→21).
- Vulnerability fix that requires a **major** dependency version bump or **source-code changes** in the repo (API renames, signature changes, deprecation removals, behaviour adaptations). See the "Vulnerability-fix exception" below — a CVE's category alone (RCE, deserialization, auth bypass, etc.) does **not** force this class regardless of which orchestrator (`/vuln`, `/implement`, `/upgrade`) is invoking the rubric; what matters is the size of the actual fix.
- Touches authentication, authorization, sessions, tokens, OAuth/OIDC, JWT, cookies, CSRF, CORS, or permissions.
- Touches database schema, migrations, or data integrity (DDL, foreign keys, indexes, backfills).
- Public API or wire-protocol contract changes (REST/GraphQL/gRPC routes, request/response shape, event schemas, SDK signatures).
- Broad refactoring across multiple modules.
- Concurrency, caching, transactions, locking, retries, idempotency, async/queue processing.
- Payment, billing, audit, compliance, PII, or other security-sensitive logic.
- Changes touching **more than 3–5 non-test files**.
- **Multi-source input** — `/implement` was given more than one code repository, or any directory input (a saved file folder, or a spec/design folder). Large multi-source briefs are cross-cutting by nature; this floors the task at `SIGNIFICANT`. See §8 for the fan-out scan this triggers. The floor is overridable at plan approval if the user judges the work genuinely smaller than its input footprint.
- Unclear requirements, large unknowns, or otherwise high blast radius.

`HIGH-RISK` is the same list with an additional severity multiplier — pick it
when the change is **production-critical, security-critical, or data-irreversible**
(e.g. an auth bypass CVE in a public service; a destructive DB migration).

### 1.2 Classify as `MODERATE` when

- 1–3 files; well-scoped feature, bugfix, or refactor; no items from §1.1 apply.

### 1.3 Classify as `SIMPLE` when

- Single trivial edit (typo, formatting, log message, comment, dead-code removal)
  with no behavioural impact.

> **When in doubt, escalate one level.** Misclassifying upward is cheap; the
> only cost is one extra Opus call. Misclassifying downward can ship bugs.

> **Vulnerability-fix exception — classify by fix size, not CVE category.**
> Two distinct rules apply here:
>
> **(a) Universal — CVE category never forces SIGNIFICANT/HIGH-RISK.** A
> CVE's category (RCE, deserialization, auth bypass, etc.) drives *attention*
> but does **not** by itself force a SIGNIFICANT/HIGH-RISK class, regardless
> of which orchestrator (`/vuln`, `/implement`, `/upgrade`) is invoking the
> rubric. Most CVEs are remediated by a patch or minor dependency bump with
> no source-code changes — those are MODERATE.
>
> **(b) Per-CVE size analysis — `/vuln` orchestrator only.** Only `/vuln`
> performs per-CVE fix-size analysis. In `/vuln`, escalate to SIGNIFICANT
> when the fix requires a major version bump or actual code changes in the
> repo (API renames, signature changes, deprecation removals, behaviour
> adaptations). Escalate to HIGH-RISK when a major bump targets a
> security-critical library (auth/authn frameworks, crypto, deserializers,
> JWT, OAuth, session libs). See `/dev-workflows:vuln`
> "Step 0 — Classify & Route" for the full vulnerability rubric.
>
> **For `/implement` and `/upgrade` orchestrators**, the standard rubric in §1.1
> applies — there is no per-CVE size analysis available at classification
> time. If the user wants CVE-aware sizing, route the work through `/vuln`.

---

## 2. Model fallback chain ("strongest available reasoning model")

Use the first model in this list that is available in the environment:

1. `claude-opus-5-5`
2. `claude-opus-5`
3. `claude-opus-4-8`
4. `claude-opus-4-7`
5. `claude-opus-4-6`
6. `claude-sonnet-5-5` (fallback only — note in the report that no Opus was available)
7. `claude-sonnet-5` (further fallback)
8. `claude-sonnet-4-6` (further fallback)
9. `claude-sonnet-4-5` (further fallback — note "no Opus or Sonnet 5.5/5/4.6 available")

Sonnet 4.5 is the floor (§10 excepted — under an enforced model this chain is
not walked, and the enforced id may sit below it); if no model in the list is
available, abort the SIGNIFICANT/HIGH-RISK gates and ask the user how to proceed
rather than silently downgrading.

The list of available models can be inspected from the `task` tool's `model`
parameter documentation. **Where that parameter enumerates only family names**
(`opus`, `sonnet`, `haiku`, `fable`) — a **family-only harness**, which is what
Claude Code's Agent tool is today — a chain row counts as available when its
family is listed, and the harness, not this policy, decides which version of the
family runs. Every chain here and in §2.1 therefore resolves to its first
row of a listed family, and §5 says what such a resolution passes as `model:`.
If none of the Opus models are available **and** the
task is `SIGNIFICANT` / `HIGH-RISK`, proceed with Sonnet but **announce the
degradation** in the Phase 0 / Step 0 routing record and again in the final report.

The "currently selected model" is whatever the orchestrator itself is running
under. Sub-agents inherit it unless the orchestrator explicitly overrides via
the `task` tool's `model` argument (and under §10 every dispatch overrides it).

---

## 2.1 Mid-tier ("detection / throughput") fallback chain

Some steps are deliberately **not** reasoning-heavy — mechanical detection,
repo scanning, transcription, formatting. Pin these to the strongest **Sonnet**
model available via the `task` tool's `model:` override; do **not** let them
inherit the session model (an Opus session would otherwise run "cheap" steps on
Opus, defeating the point).

Use the first available:

1. `claude-sonnet-5-5` (latest Sonnet)
2. `claude-sonnet-5` (fallback)
3. `claude-sonnet-4-6` (further fallback)
4. `claude-sonnet-4-5` (further fallback — note the degradation in the report)

If no Sonnet is available, fall back to the session model and announce it.
Record the chosen model as `detection_model:` in the `model_routing` block.

**`defect-reporter` runs on this chain too**, under `--skip-feedback`
(`workflows-core:run-flags` §4), recorded as `defect_model:`. Telling a defect from
friction and confirming the wrong line in the plugin's source is judgement, not
throughput; it takes this chain because it is the tier `impl-maintenance`, the agent it
replaces, runs on. No chain in this file names Haiku; `run-flags` §2 carries the Haiku
rows an enforced Haiku value resolves against.

---

## 3. Routing rules

### 3.1 SIMPLE / MODERATE

- Continue with the currently selected model.
- Do **not** add mandatory Opus steps.
- Proceed with normal planning, implementation, testing, and fixes.
- Skip the dedicated Opus code review. **`risk-planner` is not dispatched on this path at
  all** — §3.2 step 2 is its only route, and the agent's own file forbids the call in terms
  (*"Do NOT use for SIMPLE / MODERATE tasks."*) — so nothing in this section selects its
  tier: wherever it *is* called it runs on its frontmatter `model: opus` pin, per §4's
  closing bullet (under §10 the dispatch's `model:` overrides it).

### 3.2 SIGNIFICANT / HIGH-RISK — mandatory sequence

The orchestrator MUST execute these steps in order:

1. **Classify** the task and record the decision (see §4).
2. **Plan with Opus.** Delegate planning (or planning critique) to a sub-agent
   running on the strongest available reasoning model from §2. See §5 for the
   exact `task` invocation pattern.
3. **Implement** with the currently selected model **or** Sonnet (Sonnet is fine
   for raw coding throughput; Opus is not required here). Sub-agents that do
   the actual file edits inherit the orchestrator's model unless overridden.
4. **Opus code review** of the completed implementation. This is a dedicated
   `code-review` sub-agent invocation pinned to Opus. It MUST cover every item
   in the §6 checklist. Tests MUST NOT be run until this review completes.
5. **Run tests** (build + test suite per the executor / fixer workflow).
6. **Apply review fixes** — fixes flagged by the Opus review may be implemented
   by the currently selected model **or** Sonnet (no Opus required for the fix
   edits themselves).
7. **Re-run tests** if any review fixes were applied.
8. **Final summary** — include the classification, the Opus models used at each
   step (or the Sonnet fallback notice), and a one-line outcome per checklist
   item from §6.

> **Do not use Opus for routine implementation steps unless the user explicitly
> requested it.** Opus is reserved for the planning and the dedicated review.

---

## 4. The `model_routing` handoff block

Every orchestrator MUST record its routing decision and pass it to every
sub-agent that reads one — the list below. An agent whose handoff file declares
no `model_routing:` input is not sent one; its tier is pinned by the dispatch's
own `model:` argument. Format:

```yaml
model_routing:
  classification: SIMPLE | MODERATE | SIGNIFICANT | HIGH-RISK
  reason: <one-line justification citing the §1 trigger that applied>
  current_model: <e.g. claude-opus-5-5>        # the model the orchestrator is running
  planning_model: <e.g. claude-opus-5-5>       # only set for SIGNIFICANT/HIGH-RISK
  review_model:   <e.g. claude-opus-5-5>       # only set for SIGNIFICANT/HIGH-RISK
  implementation_model: <e.g. claude-sonnet-5-5 or current_model>
  detection_model: <e.g. claude-sonnet-5-5>  # mid-tier steps (§2.1); never the session model
  defect_model:   <e.g. claude-sonnet-5-5>   # §2.1 chain; set only under --skip-feedback
  fixes_model:    <same as implementation_model>
  opus_available: true | false
  enforced_model: <e.g. claude-opus-5-5, or opus>  # §10: set only when run_flags.enforced_model is set
  routing: bypassed                          # §10: present only alongside enforced_model
  gate_tests_on_review: true | false   # optional; default false. Only meaningful for SIGNIFICANT/HIGH-RISK.
                                       # When true, the executor/fixer sub-agent stops after the build,
                                       # returns status: AWAITING_REVIEW, and waits for a follow-up call
                                       # with phase: verify-resume to run tests / commit / PR.
  notes: <optional — e.g. "Opus 5.5 unavailable, fell back to Opus 5">
```

The `phase` field used to resume an executor/fixer after the Opus review is
completed is **`verify-resume`** (harmonised across `/upgrade` and `/vuln`
workflows). The executor/fixer must accept this value and run all remaining
steps (verify tests; for the fixer also commit + PR).

For SIMPLE/MODERATE the `planning_model` and `review_model` fields MAY be omitted
or set to `current_model`.

Sub-agents that receive a `model_routing` block:

- Research / planning sub-agents (NVD lookup, detect, compatibility checks):
  record the block in their output; their tier is the `model:` argument on the
  dispatch, resolved by step nature per §9. Both agents this parenthetical names
  take the `detection_model` on their first dispatch, because each is invoked
  before its command's per-unit classification exists — and they diverge once it
  does. `/upgrade`'s `upgrade-planner` **always** runs on the `detection_model`:
  for a `SIGNIFICANT`/`HIGH-RISK` component `/upgrade` escalates through the
  separate `risk-planner` on Opus and does not re-invoke `upgrade-planner`
  itself. `/vuln` re-invokes `vuln-research` on Opus once the per-CVE class is
  final — MUST for `HIGH-RISK`, SHOULD for `SIGNIFICANT` where the major bump or
  breaking-change surface is non-trivial (`/vuln` Step 2).
- Executor / fixer sub-agents: **do not run tests** until the orchestrator
  has confirmed the Opus review has completed (when classification is
  SIGNIFICANT/HIGH-RISK). The orchestrator achieves this by invoking the
  executor/fixer **without** the build+test phase first (apply changes only),
  then running the review, then invoking the executor/fixer again to run tests.
  Equivalently, the orchestrator may invoke a single combined call with a
  `gate_tests_on_review: true` flag — both styles are acceptable.
- `release-notes-writer`: receives the block; behaviour is unchanged by it, and its
  return declares no echo of it.
- **A sub-agent whose handoff file declares no `model_routing:` input is sent
  none, and reads no field of one.** Its tier is fixed either by its own
  frontmatter `model:` pin (the Opus reviewers) or by the `model:` argument on
  the dispatch, and the orchestrator's own `model_routing` record names the
  chain it resolved. Under §10 the dispatch always carries a `model:` argument,
  and that argument overrides a frontmatter pin.

---

## 5. Delegating to a model via the `task` tool

The CLI's `task` tool accepts an explicit `model:` override. Use it like this:

```
task(
  # the two `dev-workflows:` forms are dispatchable from `dev-workflows`'s own commands, and
  # from a plugin that depends on it; every other reader uses "general-purpose" — see the note below
  subagent_type: "dev-workflows:risk-planner" | "dev-workflows:code-review" | "general-purpose",
  model:      "opus",            # the dispatch form of claude-opus-5-5 (the highest available per §2;
                                 # under §10, the enforced value) in a family-only harness; where the
                                 # parameter accepts ids, the id itself: "claude-opus-5-5"
  prompt:     "<full self-contained context — sub-agent has no memory>",
  description:"Opus planning critique" | "Opus code review",
  mode:       "sync"               # always sync for plan/review gates
)
```

**The dispatch rule — the record keeps the id, the argument passes what the tool accepts.** The `model_routing` record (§4) keeps the resolved id — it is the record of intent, and a family-level §10 value is recorded as the family. The `task` tool's `model:` argument passes the **dispatch form** of that id: the id itself where the tool's `model` parameter accepts ids, and otherwise — in a §2 family-only harness — that id's **family name** (`claude-opus-*` → `opus`, `claude-sonnet-*` → `sonnet`, `claude-haiku-*` → `haiku`, `claude-fable-*` → `fable`; a value that already is a family name passes unchanged). This one rule covers every dispatch in every command and agent of the family: wherever a command, an agent or this file says a dispatch passes, carries or is pinned to an id — a chain's resolution, §10's enforced id, or a `model: <…>` placeholder naming one — that id is what the record says, and the argument is its dispatch form.

**`risk-planner` and `code-review` belong to `dev-workflows`, not to the plugin that ships this file.** **`dev-workflows`'s own commands name them directly and nothing here conditions that** — some name them by that exact `dev-workflows:` form and some by bare name, and either reaches the agent because a command's own plugin is installed whenever that command runs, so the owning plugin is never the *dependency* case this note is about. **No per-command list of which form each uses stands here on purpose:** it would be a census of three commands' call sites inside a shared reference, going stale on the next edit to any of them, and the rule it was offered as evidence for does not turn on it. Any *other* plugin can count on naming them as a `subagent_type` only by declaring `dev-workflows` in its `dependencies`, which is what installs it alongside; a reader in `workflows-core` — or in any other plugin that neither ships those agents nor declares `dev-workflows` — has no such agent to count on and takes the `general-purpose` fallback below. For those readers the fallback is not a degraded path bolted on for a missing environment: it is the *normal* one, and the §6 checklist this file already carries is complete for them, because none of them hands `code-review` any of the three optional inputs that add a dimension beyond §6's eight — `applicable_ard` and `applicable_spec` (`/implement` only) and `claims_file` (all three of `dev-workflows`'s code-changing commands). **A caller that does pass one and still has to fall back — on the environment half of the trigger below — carries that dimension into the fallback prompt itself**, because §6 does not list it.

- For **planning** on SIGNIFICANT/HIGH-RISK tasks, prefer `subagent_type: "dev-workflows:risk-planner"`
  with Opus (under §10, the enforced id), asking it to critique the proposed plan — available in `dev-workflows` itself, and
  elsewhere only where the calling plugin depends on it.
- For **post-implementation review** on SIGNIFICANT/HIGH-RISK tasks, use
  `subagent_type: "dev-workflows:code-review"` with Opus (under §10, the enforced id), passing the diff and §6 checklist —
  again, in `dev-workflows` itself and elsewhere only where the calling plugin depends on it.
- Where either agent is unreachable — the calling plugin neither ships it nor depends on
  `dev-workflows`, or the agent is unavailable in the environment — fall back to
  `subagent_type: "general-purpose"` with the same Opus model (under §10, the enforced id), the same prompt, and the explicit §6
  checklist embedded in that prompt, plus any conditional dimension the caller's own inputs trigger.

---

## 6. Mandatory Opus code-review checklist (SIGNIFICANT / HIGH-RISK)

The post-implementation Opus review MUST explicitly comment on each of:

1. **Correctness** — does the change actually do what was planned, including all
   listed acceptance criteria and edge cases?
2. **Security impact** — new attack surface, authn/authz changes, secret
   handling, input validation, deserialization, injection vectors, supply chain.
3. **Architectural consistency** — boundaries respected, abstractions intact,
   no leaking concerns, idiomatic for the codebase.
4. **Missed edge cases** — empty/null/zero/negative/very-large inputs, partial
   failures, concurrent access, time-zone / DST / locale, off-by-one, retries.
5. **Migration risks** — schema changes, data backfills, feature flags, ordering
   between deploy and migration, forward/backward compatibility windows.
6. **Dependency risks** — new transitive deps, license changes, abandoned
   packages, known CVEs in the new versions, lockfile drift.
7. **Test adequacy** — does the test suite actually cover the new behaviour?
   Are negative tests and boundary tests present? Are tests deterministic?
8. **Rollback considerations** — how is this change reverted? Are migrations
   reversible? Is there a feature flag? What is the worst-case incident playbook?

The review output MUST include a verdict per item: `OK` / `CONCERN` / `BLOCKER`,
plus a free-text comment for any non-`OK` finding. Before proceeding to tests the
orchestrator MUST **dispose of** every `BLOCKER` — and document the disposition of
each `CONCERN` — where a disposition is either a fix or a dismissal recorded with a
reason that disposes of that finding's own claim, per
`${CLAUDE_PLUGIN_ROOT}/references/finding-triage.md`. Only survivors are handed to
the fixer; no `BLOCKER` may be left undisposed, and none may be dropped silently.

---

## 7. Reporting

The orchestrator's final report MUST include a `### Model Routing` section:

```
### Model Routing
- Classification: <class>
- Reason: <trigger>
- Planning model: <model>
- Implementation model: <model>
- Review model: <model>  (or "n/a — SIMPLE/MODERATE")
- Opus checklist verdicts:
  - Correctness: OK | CONCERN | BLOCKER
  - Security: ...
  - Architecture: ...
  - Edge cases: ...
  - Migration: ...
  - Dependencies: ...
  - Tests: ...
  - Rollback: ...
- Notes: <degradation, fallbacks, deferred items>
```

For SIMPLE/MODERATE tasks the verdict list MAY be omitted; the classification
and reason are still required.

---

## 8. Large-input scan fan-out

When a scanning step must digest more than a single working tree, a single
explorer subagent on a weak session model comprehends it poorly. This section
is the shared policy for that case. It generalizes the pattern `/epics`
already used; the commands that run §8.2 and those that also adopt §8.5 are
named in §8.5's *Opt-in* paragraph, which is the one list of them.

### 8.1 Trigger (input shape, not measured volume)

Fan out when **any** of these structural facts hold for the invocation:

- more than one code repository is referenced;
- a saved file folder is supplied;
- a spec/design folder is supplied.

Counting files or bytes is explicitly **not** used — the trigger is the shape
of the input, which is cheap to detect and easy to explain. A single repo with
inline/`@file` text only does **not** trigger fan-out; the caller keeps its
normal single-explorer path.

### 8.2 The fan-out pattern

1. the folder read reads each resolved specs folder (read-only) → themes, plus
   the `EPIC-` folders under a PRD folder, which are the whole of the hierarchy.
   No PR reference is collected here: a run's refs live in `implementation.md`.
2. Spec/design folders are read inline and folded into the themes.
3. `code-scanner` is fanned out **one instance per repository, in a single
   response, capped at 4 concurrent**. Each instance receives the themes and
   its own repo path; it returns capabilities, gaps, and relevant files.
4. The orchestrator synthesizes the folder read output, all scanner reports,
   and the spec into one codebase summary that feeds the Opus planner.

### 8.3 Model routing inside the fan-out

- the folder read and `code-scanner` are **pinned to the §2.1 detection (Sonnet)
  chain** via the `task` tool `model:` override — the same rule as every other
  mechanical step (§2.1, §9.1). Scanning is mechanical filesystem work; it must
  not inherit the session model (an Opus session would otherwise burn Opus on a
  cheap step), and its tier must not depend on which model the session happens
  to run under.
- Because the trigger floors the task at `SIGNIFICANT` (§1.1), synthesis and
  planning run on the strongest available reasoning model via `risk-planner`
  (§2 chain). That is where reasoning power is applied — the mechanical scan
  that feeds it does not need it.
- **Optional escalation:** if a single repo slice is itself oversized for the
  detection tier to comprehend, the orchestrator MAY pin that one `code-scanner`
  to Opus via the `task` tool `model:` override. This is a size-driven, judgment-
  based exception — not session-driven.

### 8.4 Honesty

A referenced directory that is missing, or is neither a recognized folder type
nor a git repository, MUST be surfaced to the user — never silently skipped
(mirrors the `REFRESH_BLOCKED` honesty rule used by the keyed flows).

### 8.5 Broad, then narrow (the seeded second round)

A broad prompt lets each scanner defer to the layer it did not scan. Round 1
asks every repo the same wide question, and a capability spanning two layers can
come back attributed to the *other* layer by both scanners — a pair of confident
answers that together say nothing. Naming a verified anchor removes the escape.

**Round 1** is the §8.2 fan-out unchanged: one `code-scanner` per repository,
broad themes, single response, cap 4 concurrent.

**Inconclusive** describes a round-1 theme whose `classification` is `partial`,
`absent`, or `error`, **or** for which **two or more** scanners' per-theme
`capability_map[].gap_summary` texts point at each other's repo in a cycle, or
at a component/subsystem that no scanned repo covers.

**Round 2** fires for an inconclusive theme when round 1 produced at least one
evidence anchor to seed from. It dispatches the **same** `code-scanner` agent
with a narrowed brief:

- `capability_themes` holds exactly **one** question — not the broad theme, but
  the single thing round 1 failed to settle;
- `search_hints.paths` / `.symbols` / `.keywords` are seeded from round 1's
  verified `evidence[].path` and `.symbols`; where an evidence entry carries
  `lines`, name the anchor as `<path>:<line>` in the round-2 `context` prose,
  since `search_hints` has no line-number field.

No new agent and no input-contract change: the narrowing lives entirely in what
the caller puts in the existing fields.

The narrowed brief changes only those fields: every other field of round 1's
dispatch — **including `refresh:`** — is reused verbatim, so a caller that
pinned a read-only posture in round 1 keeps it in round 2.

**Bounds.** Round 2 is capped at **4 dispatches** and is **one round only**.
There is no round 3. A theme still inconclusive after round 2 is reported
unresolved — never guessed at. **Precedence: mutual deferral and `error` are
unresolved regardless of whether a round-1 evidence anchor existed to seed a
round 2** — a theme with no anchor never gets a round-2 attempt, but the
absence of an attempt is not itself a resolution. A theme confirmed `absent`
— by round 2, or by round 1 when no anchor existed to seed one — is a
**resolved** finding, and the outside-deferral qualifier below is
caller-scoped. For **`/implement`** it is resolved only when that `absent`
carries **no deferral to a repo or layer outside the scanned set**, because
that caller's premise is that the capability lives somewhere across the repos
in scope. For **`/idea`** it is resolved unconditionally — the confirmed repo
set *is* the world the idea grounds against (see the altitude paragraph that
follows) — and it belongs in Section 7's *What's missing*, not in Open
questions. For **`/docs-audit`** it is likewise resolved unconditionally, and
for the same reason under a different name: the confirmed source-repo set is
that command's **coverage denominator**, so `absent` everywhere scanned is an
answer about the product — a surface kind it genuinely has none of, recorded as
`absent` rather than enumerated — and never a theme carried forward as
unsettled. `[NEEDS CLARIFICATION]` (or the caller's equivalent) is for a theme
the scan could not settle — mutual deferral, `error`, or, **for `/implement`
only**, `absent` everywhere scanned **plus** a deferral outside the scanned
set.

The altitude differs by caller. For `/idea --ground-code`, the confirmed repo
set **is** the world the idea is grounding against, so `absent` everywhere
scanned genuinely means missing. For `/docs-audit`, the same holds of its
confirmed source-repo set, which is what the coverage figure is a fraction of:
`absent` everywhere scanned means the product has no surface of that kind, and
recording it as anything else would put a false statement into the denominator.
For `/implement`'s fan-out, the premise is
that the capability lives *somewhere* across the repos in scope — so `absent`
everywhere scanned **plus** a deferral outside the scanned set means "the scan
could not tell," not "the capability does not exist."

**Opt-in.** §8.5 is a shared procedure a caller adopts by saying so in its own
body. Its consumers are `/idea` (Phase 2.6), `/implement` (Phase 1.7) and
`/docs-audit` (Phase 2). `/epics`, `/create-ard`, `/specify`, and `/design` run
§8.2 alone and are unaffected by this section. **A caller joining this list also
answers the three caller-scoped paragraphs around it** — the two above, which
say what a confirmed `absent` resolves to and the altitude that decides it, and
the one below, which says what each caller passes a still-unresolved theme on
in — because none of the three has a default a new caller could fall back on.

**Round 2 resolves; it does not license a guess.** A caller that adopts §8.5
also owes its downstream consumer the truth about what stayed unresolved. An
inconclusive theme is not a gap: a gap asserts the capability is absent, an
unresolved theme asserts only that the scan could not tell, and flattening the
second into the first hands the next step a confident-looking answer that was
never earned. Name unresolved themes explicitly in whatever the caller passes
on — `/idea` carries them into `[NEEDS CLARIFICATION]`, `/implement` into the
codebase summary's `## Unresolved` section and from there into the plan's
risks, and `/docs-audit` into `docs-auditor`'s `unresolved[]`, which
`ia-planner` echoes and the run's own report names — never into a surface, a
unit, or a covered cell.

---

## 9. Per-step routing (every command)

Steps differ in nature — some judgment-heavy, some mechanical — and a command
MUST NOT let every step inherit the session model. Apply this policy in every
command, resolving each model against the §2 (Opus) and §2.1 (Sonnet) fallback
chains. The keyed authoring pipelines (`/document` and `/epics`) run long phase
sequences and are the motivating case, not the scope — §9.4 is the governing
rule.

### 9.1 Principle

- **Judgment-heavy authoring / synthesis** steps run on the §2 reasoning (Opus)
  chain — escalate to Opus even when the session is Sonnet.
- **Mechanical detection / throughput / fix** steps run on the §2.1 detection
  (Sonnet) chain — de-escalate off the session model even when the session is
  Opus (otherwise an Opus session burns Opus on cheap work).
- **Orchestrator-executed** judgment steps — the inline prose writing and the
  interactive gates, plus the orchestration itself — run on the session model
  and CANNOT be overridden from inside a running command. Except under §10, where none of the rest of this bullet fires — no advisory, no gate, no degrade path, for any command that carries one (§10's *Opus-session gates do not fire* bullet is the general rule, and `workflows-core:run-flags` §3 step 7's advisory is the only notice) — handle them with an
  **advisory** (recommend relaunching on the §2 chain), never an override. This advisory applies when the task is SIGNIFICANT/HIGH-RISK. Where the authoring step is the orchestrator itself, how it is discharged is the command's own to state and differs: `/design` and `/create-ard` make it a HARD gate on `current_model` that stops and offers a relaunch, while `/create-prd` degrades to the best available model and records the degradation instead of stopping. Read the command rather than assuming a gate. Where the writing is delegated to a writer on its own Opus pin, the writing is already off the session model and the residual risk is the orchestrator's own context window, so the advisory narrows there to a large non-Opus run, as in `/document`. At SIMPLE/MODERATE §3.1 requires none, and requires nothing against one either: it asks only that no *mandatory* Opus step be added, so a command that offers a soft advisory anyway (`/design`) is stricter by its own choice and not in breach.

### 9.2 Role → chain map

| Role | Chain |
|------|-------|
| Synthesis / planner (e.g. `doc-planner`) | §2 reasoning (Opus) |
| Reader / summarizer / locator / style-checker / fixer / maintenance (the folder read, `diff-summarizer`, `doc-location-finder`, `docs-style-checker`, `doc-fixer`, maintenance agents) | §2.1 detection (Sonnet) |
| Domain reviewer (`doc-reviewer`, `epic-reviewer`) | §2 review (Opus) — usually already frontmatter-pinned; the orchestrator records it and adds **no** override — unless §10 enforces a model |
| Delegated writer (`doc-writer` / `epic-writer`) | §2 reasoning (Opus) for SIGNIFICANT/judgment writing; §2.1 detection (Sonnet) for MODERATE writing |
| Coordination + interactive gates (the orchestrator itself) | session model; where the writing is delegated, a narrowed window advisory for large non-Opus runs; where the authoring is inline, the command's own (§9.1) |

### 9.3 No-Opus degradation

When no Opus model is available (per §2), run the reasoning / review roles on the
Sonnet floor, **skip** the relaunch advisory (there is nothing to relaunch onto),
and announce the degradation in the `model_routing` record and the final report —
the same rule as §2.

**`opus_available` is a property of the environment, never of the session**, and
the two are separate fields of the same block. §2 resolves it against what the
`task` tool can reach; the session's own tier is `current_model`, which §2 names
separately as "whatever the orchestrator itself is running under". Two
consequences, and a command that confuses the fields gets both wrong at once.
A gate that exists to **require an Opus session** — an inline-authoring
command's HARD gate — tests `current_model`, the tier a relaunch does change,
and never `opus_available`, which is true on every Sonnet session that merely
*could* dispatch Opus and so lets the gate miss the one state it was written
for. And where such a gate fires with `opus_available` **also** false, the
relaunch option is dropped rather than recommended: that is this section's skip
rule, and the array offers only what remains reachable —
`choices: ["Proceed on the Sonnet floor — the degradation is recorded in `notes` and the final report (Recommended)", "Cancel"]`.

### 9.4 One rule across commands (`/implement` included)

Routing is by **step nature**, not by pipeline or session: the folder read and
`code-scanner` are mechanical, so they run on the §2.1 detection (Sonnet) chain
in **every** command — `/implement`'s fan-out (§8.3), `/epics`, and `/document`
alike. There is no "inherit the session model" for scanning and no per-command
exception. A step's downstream consumer does not change its tier: a mechanical
scan that feeds an Opus synthesis (e.g. `/implement`'s `risk-planner`) still runs
on Sonnet — the reasoning power is applied in the synthesis step, not the scan.
The only carve-out is size-driven, not session-driven: escalate a single
oversized repo slice's `code-scanner` to Opus (§8.3).

---

## 10. Enforced model

`run_flags.enforced_model` (`workflows-core:run-flags`) lets a run pin every subagent dispatch to one model, bypassing model routing's own per-step selection. Classification and the routing rules above are unchanged in what they select — this section changes only which model each selection resolves to.

- **Chain resolution.** When `run_flags.enforced_model` is set, every resolution of §2, §2.1 and §8.3's oversized-slice escalation returns that id instead of walking its own chain — or that family, where `workflows-core:run-flags` §2 resolved a bare family alias in a §2 family-only harness to the family itself (`opus`); every "enforced id" in this section and in the commands that cite it covers that family value too. Every `*_model` field of the §4 `model_routing` block that names a **dispatched** step equals it — `planning_model`, `review_model`, `detection_model`, `fixes_model`, `defect_model` (present only under `--skip-feedback`, §2.1), and `implementation_model` wherever it names a delegated writer or executor rather than inline coding — and the block gains `enforced_model: <id>` and `routing: bypassed`. A field that instead records the orchestrator's own inline work keeps the session model, never the enforced id, because enforcement pins subagent dispatches and not the orchestrator's own session: `current_model` always does, and so does `implementation_model` / `authoring_model` wherever a command codes or authors inline rather than delegating — `/implement`'s `implementation_model` (inline coding) and `/prd-proposal`'s and `/brd-proposal`'s `authoring_model` (inline grill + authoring) among them. `opus_available` is still resolved and reported truthfully: it is a property of the environment (§9.3), not of the enforcement choice, so it is never rewritten to agree with the enforced id.
- **Every dispatch.** Every `task` tool dispatch passes `model: <enforced>` explicitly, in §5's dispatch form — the enforced id itself where the tool's `model` parameter accepts ids, its family name in a §2 family-only harness — including the agents whose frontmatter pins `model: opus`: the dispatch's `model:` argument overrides the frontmatter pin. The `model_routing` fields above keep the enforced value as `run-flags` §2 resolved it, never the translated argument. Every "frontmatter-pinned … no override" statement at a command's dispatch site reads "no override unless §10 enforces a model", so no live sentence contradicts this section.
- **Nested dispatch.** An agent that itself dispatches another agent (`docs-style-checker` → `prose-style-checker`; `upgrade-executor` / `vuln-fixer` → `test-baseliner` via the `task` tool) receives `enforced_model` in its prompt and passes it as `model:` on its own dispatch, in §5's dispatch form, so enforcement reaches every model a run touches, not only the orchestrator's own direct calls.
- **Steps unchanged.** Classification (§1) still runs and still selects the §3 sequence for the task's class — a SIGNIFICANT/HIGH-RISK task still gets its plan and review gates, a SIMPLE/MODERATE task still skips them. Enforcement changes which model each selected step runs on, never whether the step runs.
- **The orchestrator.** The orchestrator itself stays on the session model; it cannot be switched from inside a running command, exactly as §2's "currently selected model" already says. `workflows-core:run-flags` §3 step 7 prints the one relaunch advisory when the enforced id differs from `current_model`; its wording is that step's, not restated here.
- **Opus-session gates do not fire.** Every gate or degrade path that tests `current_model` for an Opus session does not fire under enforcement — not a named list, but the whole class of them, since each exists to require or prefer an Opus-tier session and the user has already chosen the model. Examples that exist today: §9.1's HARD gates in `/design` and `/create-ard`, `/prd-proposal`'s and `/brd-proposal`'s stops, and `/create-prd`'s degrade path (a maintainer finds the candidates with `grep -n "current_model" plugins/*/commands/*.md`, which lists every mention of the field — routing records and reports as well as gates — so each hit is read to tell a gate of this class from the rest). Testing the enforced id in a gate's place would let a Sonnet session pass an Opus gate, since the inline grill or authoring these gates protect still runs on the session model, not the enforced one. The `run-flags` §3 step 7 advisory is the only notice of a session/enforced mismatch; §9.1's own relaunch advisory is not issued alongside it.
- **Degradation notices are suppressed.** §2's "no Opus available" notice and §9.3's no-Opus degradation notice are not emitted under enforcement — there is no fallback to announce, since every resolution already returns the enforced id. §7's report carries `Model routing: bypassed — enforced <id> (flag|env)` in its `Notes:` field, in place of the degradation or fallback that field would otherwise record; `<id>` there is rendered as `workflows-core:run-flags` §6 defines it — what the dispatches were actually passed, plus the requested value where the two differ (`enforced opus (from opus5.5; the harness picks the version) (flag)`).
- **Unpriced ids.** A reachable enforced id absent from `cost-prices.yaml` does not stop the run: `workflows-core:run-flags` §2 prints the Phase 0 unpriced-model warning, and `workflows-core:cost-emission` §6.1's dominance warning covers it in the final report.

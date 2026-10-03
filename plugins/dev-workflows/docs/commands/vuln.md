# /vuln

Researches CVEs via NVD, applies dependency and code fixes one at a time, and verifies each fix with an Opus code review and tests.

## Who runs it

`/vuln` runs **outside the PRD pipeline** — it has no cost-attribution phase and no role. It emits **no cost attribution at all**: it has no Product Requirements Document to attribute spend to, and `workflows-core:cost-emission` records that exemption by name rather than passing over it in silence — the rule lived only on this page until it was restated there. The `phase:` values it does pass to `vuln-research` and `vuln-fixer` — `full`, `verify-resume`, `regression-resume` — belong to a completely different vocabulary: the model-routing **resume protocol**, saying how much of a single command's own re-entered work must be redone after a review or a failed test, not where a run sits in the product lifecycle. The two vocabularies share the field name `phase` and nothing else — see [Roles and phases](../roles-and-phases.md#cost-attribution-phases) for the fuller distinction.

## Synopsis

```
/vuln <ADDRESS:CVE-ID | CVE-ID> [<ADDRESS:CVE-ID | CVE-ID>…] [--skip-feedback] [--enforce-model=<model>]
```

Each argument token is either `ADDRESS:CVE-ID` (e.g. `PROJ-2423:CVE-2023-46604`) or a bare `CVE-ID` (e.g. `CVE-2023-46604`) — multiple tokens fix multiple CVEs in one run. A non-CVE token (`CWE-*`, an OWASP pattern) is filtered out with a warning rather than passed through. Every token is parsed and every CVE researched **before** any fix is applied.

Two of the three run flags apply to this command — `--skip-costs` does not, since `/vuln` emits no cost attribution at all (see [Who runs it](#who-runs-it) above). `--skip-feedback` (or `WORKFLOWS_SKIP_FEEDBACK`) narrows Step 4's maintenance to bugs-only, dispatching `defect-reporter` in place of `impl-maintenance` — see [Session feedback](../reference/session-feedback.md). `--enforce-model=<model>` (or `WORKFLOWS_ENFORCE_MODEL`) pins every dispatched agent in this run — `code-review` included, overriding its frontmatter Opus pin, and reaching `vuln-fixer`'s own nested `test-baseliner` dispatch too — see [Model routing](../reference/model-routing.md).

## How it runs

`/vuln` is the plugin's **only `## Step N` command** — five steps, where every other command that uses either heading dialect uses `## Phase N`; the diagram below adapts its Step headings rather than reproducing them verbatim — it drops Step 0's "(mandatory)" qualifier, and splits Step 3's single heading into two rewritten labels, one per classification path.

```mermaid
flowchart TD
    s0["Step 0 — Classify & Route"] --> s1["Step 1 — Prepare"]
    s1 --> s2["Step 2 — Research (parallel)"]
    s2 --> d1{"Finalized per-CVE class?"}
    d1 -->|"SIMPLE · MODERATE"| s3a["Step 3 — Fix: vuln-fixer"]
    d1 -->|"SIGNIFICANT · HIGH-RISK"| s3b["Step 3 — Fix: vuln-fixer, Opus code-review → triage → review-fixer, before tests"]
    s3a --> tv["Verify against the run's baseline"]
    s3b -->|"review cleared — verify-resume"| tv
    tv --> s4["Step 4 — Summarise"]
```

Two subagents are dispatched explicitly by name in Step 2 and Step 3: `vuln-research` (Step 2, one instance per valid CVE, single batched message) and `vuln-fixer` (Step 3, one CVE at a time — sequential, to avoid conflicting edits to the same dependency files). Step 3 also dispatches `test-baseliner` once for the run, before the first fix and whatever the classifications are. The `SIGNIFICANT`/`HIGH-RISK` path additionally dispatches `code-review` (Opus, frontmatter-pinned) and, on a surviving finding, `review-fixer` — the same review/triage/fixer machinery `/implement` and `/upgrade` use. Classification (Step 0) is **per CVE**, based on the size of the required repository change from the research report, not the CVE category alone — research starts under a provisional `MODERATE` routing block and the classification is finalized once the fix shape is known, before any fix is applied.

## What it needs

- **One or more CVE tokens**, each optionally paired with an **address** — a key resolved against `$SPECS_PATH`, never a tracker lookup. A token with no address falls back to whichever no-address placeholder the repo already writes (`NOISSUE` / `NOJIRA` / `NO-JIRA`), detected from recent branch names and commit history in Step 1. <!-- vendor-token-ok: placeholder literals a repo may already write, recognised rather than minted -->
- **The target repo(s)** — inferred from the working context; each `vuln-research`/`vuln-fixer` dispatch carries an absolute repo path.
- **`$SPECS_PATH`** — for the Step 0 specs-repo preflight, run on the keys the tokens carry (none where no token carries one), and the terminal artifact commit; this repo is never the one being fixed, and the code repo is untouched by any specs-repo step.
- **A test suite `test-baseliner` can run** — wanted on both paths, captured **once for the run** before the first CVE is worked, and a prerequisite on neither: where the capture cannot run, the run asks you rather than deciding it. **This is not a prerequisite either path enforces on its own, and it used to be one of them** — the `SIMPLE`/`MODERATE` path once had `vuln-fixer` take its own capture and abandon the CVE where it failed, leaving a patch-level vulnerability unfixed for want of a test runner while a major bump of a security-critical library went ahead on the other path. Both paths now reach the same question, asked before anything is branched or edited: supply a test command, apply the fixes unverified, or cancel. Applying unverified works every CVE and finishes each `TESTS_NOT_RUN`, so each pull request is a draft carrying the DO-NOT-MERGE line (see [Gates](#gates)). A repository that simply has no tests is not this case at all — the capture returns cleanly, nothing is asked, and no CVE is marked down. And a suite that runs for one language and not another is no reason to leave a CVE in the other unfixed: the run names what it did not verify in the Step 4 table's `Notes` column rather than stopping.

## What it produces

One feature branch and commit **per fixed CVE, in the code repo itself** — then a push where you said so, the repository has an `origin`, and the push itself succeeded, and a pull request where you asked for one and the run could open it at all, that CVE's own `Code repo:` outcome line being what says which of those happened. Each CVE is branched from the resolved base rather than from the previous CVE's branch, so its diff, its review, and its PR carry only its own fix. `vuln-fixer` creates the branch before its first edit and stops there; the commit, push, and pull request are Step 3.9's, and never push directly to `main`/`master`. The push-and-PR consent choice is asked once for the whole run rather than once per CVE, and is put again wherever a later CVE's outcome differs from the one your answer was given under — blocked after clean, and equally clean after blocked, so a decline given on a blocked CVE never silently withholds the good fixes behind it. Branch and commit conventions are resolved per `workflows-core:branch-naming`, preferring the repo's own documented convention. A Step 4 result table (CVE, library, version change, classification, result, PR, and a `Notes` column naming any suite the run did not verify, on either path — so a CVE is never reported fixed with a stack silently unchecked) and a `### Review triage` section, one line per review pass, counting every finding reviewed and naming each one dismissed or left unverified, with its reason, for CVEs that went through Opus review. An `workflows-core:impl-maintenance` Lessons Learned report, always tagged `Command run: /vuln`.

No cost entry is ever written (see [Who runs it](#who-runs-it) above), and no `resume.md` is written for `/vuln` — its durable state is already the branch and PR on disk, not a PRD-scoped artifact. The terminal `commit-artifacts` step still runs, committing only `$SPECS_PATH`'s bounded session-artifact paths — never the code repo this run just fixed.

## Gates

Step 3 captures a test baseline **once, before the first fix is applied**, and every CVE on either path verifies against that one block. For each `SIGNIFICANT`/`HIGH-RISK` CVE it then dispatches `vuln-fixer` with review gating enabled. On `AWAITING_REVIEW`, the Opus `code-review` gate runs **before any test verification** — the plugin's invariant that tests never run on risky work until review returns a non-`BLOCK` verdict, or you settle a `BLOCK` that no surviving `BLOCKER` supports. Between the review and any fixer dispatch, the orchestrator runs its own finding triage (`workflows-core:finding-triage`) — each finding verified at the location it names and kept, marked unverified or dismissed, every unverified finding and every dismissal recorded with a reason; `review-fixer` is handed **survivors only**. A `BLOCK` or `PASS WITH RECOMMENDATIONS` verdict invokes `review-fixer` for the surviving `BLOCKER`/`MAJOR` findings, then one re-review against the refreshed diff; the re-review is triaged too, carrying forward what triage already ruled, and a review that stayed blocked — a `BLOCKER` surviving that triage, or a verdict you chose to keep — stops work on that CVE rather than looping; a second `BLOCK` that no surviving `BLOCKER` supports is yours to settle, and a Cancel at that prompt also stops only that CVE while the run goes on. The `SIMPLE`/`MODERATE` path skips this gate entirely — `vuln-fixer` fixes and verifies against the same baseline, with no Opus review.

A `TEST_REGRESSION` result on either path hands the decision to the orchestrator (never the fixer, which cannot prompt): apply the fix anyway and flag the failures, revert and skip the CVE, or investigate further — looping at the orchestrator until a decision is made. A `TESTS_NOT_RUN` result is the different case where the verify call compared nothing at all — a runner that could not start, not a test that failed — and nothing is reverted on it: the fix is committed and handed off unverified, and where the run opens a pull request at all it is a draft carrying a DO-NOT-MERGE line. Whether one is opened is the consent choice's answer, and then whether `gh` can open one at all — a remote `gh` cannot target, a `gh` that is absent or not authenticated, or a pull request already open on the branch each end the run with none opened by it. A repository whose base branch cannot be resolved gets no pull request either way: one with an `origin` whose branch ladder is exhausted still reaches the push, subject to the same consent choice, while one with no `origin` at all has nothing to push and keeps the commit locally.

## Example

Fix one CVE tied to an address and one bare CVE in the same run:

```
/dev-workflows:vuln PROJ-2423:CVE-2023-46604 CVE-2024-99999
```

Both CVEs are researched in parallel via `vuln-research`; each `READY` result is finalized to a classification and fixed sequentially — `PROJ-2423:CVE-2023-46604` typically as a dependency-only `MODERATE` bump verified against the run's baseline, `CVE-2024-99999` escalated if its fix requires code changes, gated by Opus review and triage before tests. Each CVE is committed in Step 3.9 — and pushed there where you said so, the repository has an `origin`, and the push itself succeeded, the consent choice being asked on the first CVE and reused for the second, unless the two end differently — blocked after clean, or clean after blocked — which puts the choice to you again — with its own `Code repo:` outcome line, which is what says which of the three happened; Step 4 prints the result table, review triage, and the `impl-maintenance` report; the run closes with the `Specs repo:` outcome line for the bounded session-artifact commit.

## See also

- [`/upgrade`](upgrade.md) — the plugin's other maintenance command outside the PRD pipeline, sharing the same no-cost-attribution fact, the same resume-phase vocabulary, and the same review/triage/fixer/test gate shape for version bumps instead of CVEs.
- [`/implement`](implement.md) — the pipeline command `/vuln` borrows its review machinery from: `code-review`, `review-fixer`, and `workflows-core:finding-triage`.
- [Roles and phases](../roles-and-phases.md#cost-attribution-phases) — the closing note distinguishing the cost-attribution `phase:` vocabulary from the resume-protocol `phase:` vocabulary `/vuln` passes.
- [Session cost](../reference/session-cost.md) — states plainly that `/vuln` and `/upgrade` emit no cost attribution at all.
- [Session feedback](../reference/session-feedback.md) — how the terminal `emit-auto` step persists plugin-facing lessons from this run.
- [Resume and checkpoints](../reference/resume-and-checkpoints.md) — why `/vuln` writes no `resume.md` and gets a plain end-of-run `/compact` suggestion instead.
- [Model routing](../reference/model-routing.md) — the per-CVE classification rules and the Opus fallback chain `code-review` resolves against.
- `workflows-core:finding-triage` — the triage step run between `code-review` and `review-fixer`.

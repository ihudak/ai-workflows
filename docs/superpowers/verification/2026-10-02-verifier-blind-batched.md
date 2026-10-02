# Blind, batched grounding verification — verification record

Branch `iv-gu/verifier-blind` (GitHub issues #73 and #74), HEAD `d2fea465`, 41 commits ahead of local `main` (`0dae2071`); `origin/main` (`fbd68872`, change #70's merge) was merged into the branch at `1c3a5a37` (ruling R16). Plan `docs/superpowers/plans/2026-10-01-verifier-blind-batched.md`, spec `docs/superpowers/specs/2026-10-01-verifier-blind-batched-design.md`. Written **last**, after the final whole-branch review's fix wave and every later wave (`2eec5305`, `4c35d197`, `90dd7434`, `248613f0`, `d77186a4`, `f763bcb0`, `d2fea465`), per `CLAUDE.md` § Editing discipline. Every command in sections 2 and 3 was run against the tree at `d2fea465` in this session; no expected value is copied from the plan, the ledger or any report. Where a figure in sections 4 to 8 comes from a smoke run, a review or a ruling, it is attributed to that source and to the commit it ran on, because it describes that commit and not necessarily this one.

**Addendum (final tree `7d6edef5`):** a last live run on `cca78582` passed and found one blindness leak, fixed in `7d6edef5` and verified by reading (section 4.10); the gate chain passes at `7d6edef5`.

**Status: the static checks pass on the final tree; the live checks pass on earlier trees and did not all run again on the final one.** The gate chain printed `EXIT=0` at `d2fea465`, and every re-derived count matched its expectation. The last live `/prd-ground` run was at `d77186a4`; two commits changed plugin prose after it (`f763bcb0`, `d2fea465`), and section 4 says which of their effects were seen live and which were verified by reading only. One check failed live and was **not** fixed in the way it was first meant to be: Phase 1's cost statement was never printed by a headless run (section 4.9).

## 1. What was verified, at which commit

The tree at `d2fea465` — the final tree. The branch makes `/prd-ground`'s grounding verification **blind by construction** (#73) and **batched** (#74):

- `product-workflows:grounding-verifier` has two modes. `derive` re-derives a finding from its source from the claim alone, and refuses a dispatch that carries any of the answer fields (`INPUT_UNBLIND`). `compare` receives the original and the blind result and returns one of `agree`, `extend`, `contradict`, `unprovable`, with `INCOMPLETE` for a blind result lacking only its owed control.
- `/prd-ground` Phase 7 dispatches one derive batch and then one compare batch per group (repository or frame set), at most 25 findings each, with one retry per finding in each verification pass and in each second opinion.
- Later waves added a second blind opinion on a disputed `contradict` (`blind_disputed`, ruling R19), a Final report verification block, and an echo check on structured values only.
- Release: product-workflows `3.11.0` and workflows-core `1.9.0`, both dated `2026-10-02`.

## 2. Full gate chain

Run as one `&&` chain in the worktree, in the order `.github/workflows/validate-catalog.yml`'s `run:` steps list (setup steps aside), with `ASSERT_PUBLISHED=1` exported for the whole chain, so `check-docs.sh --root .` ran with check 18 armed. `npm ci` writes only `scripts/mermaid/node_modules/`, which `.gitignore` excludes, so the chain ran in the worktree itself and not in a scratch clone (`git status --short` was clean afterwards).

```
$ ASSERT_PUBLISHED=1 bash -c 'python3 scripts/validate-catalog.py --selftest && \
  python3 scripts/validate-catalog.py && \
  ./scripts/check-id-grammar.sh --selftest && \
  ./scripts/check-id-grammar.sh --root . && \
  ./scripts/check-docs.sh --selftest && \
  ./scripts/check-docs.sh --root . && \
  npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund && \
  node scripts/mermaid/check-mermaid.mjs --selftest && \
  node scripts/mermaid/check-mermaid.mjs --root . && \
  ( mapfile -t hits < <(find plugins -type f -name session-cost.py | sort); \
    [ "${#hits[@]}" -eq 1 ] && python3 "${hits[0]}" --selftest ); \
  echo "EXIT=$?"'
```

Summary lines, in order of appearance:

```
0 error(s), 0 warning(s) across 1 repo(s).
PASS: no dash-form requirement IDs under .
  check 9 cost-emitting-commands assertion not applicable: plugins/guideline-reviewers ships no docs/reference/session-cost.md
PASS: docs are consistent with the plugin(s) under plugins/dev-workflows plugins/guideline-reviewers plugins/workflows-core plugins/docs-workflows plugins/product-workflows
PASS: all 35 mermaid blocks in 426 tracked markdown files parse (mermaid 11.17.2, marked 16.4.2)
SELFTEST PASS
EXIT=0
```

Every `--selftest` printed `SELFTEST PASS` (validate-catalog, id-grammar, docs, mermaid, session-cost). The one informational line is expected: `guideline-reviewers` is outside this change and carries no session-cost page. **`EXIT=0`**, read from the chain's own printed value. This record was committed after a second run of the two gates that read it (`check-id-grammar.sh --root .` and `check-docs.sh --root .`); see the commit.

## 3. Retired and sole phrases, re-derived

Counted with the wrap-insensitive counter `python3 .superpowers/sdd/2026-10-01-verifier-blind-batched/vb-count.py "<phrase>"`, over `CLAUDE.md` refinement 4's scope (`plugins/` with every `CHANGELOG.md`, `.claude/rules/`, `docs/maintainers/`, `README.md`, `CLAUDE.md`). Expectations were fixed by the brief for this record before the counts were run.

| Phrase | Expected | Got | Where |
|---|---|---|---|
| `One instance per finding` | 0 | **0** | — |
| `exactly as the agent's own Inputs contract declares it` | 1 | **1** | `plugins/product-workflows/commands/brd-package.md:582`, about `brd-package-reviewer`, a different agent |
| `DO NOT READ before Process step 2` | 0 | **0** | — |
| `Process step 2` | 0 | **0** | — |
| `provenance: own-run \| inherited` | 0 | **0** | — |
| `discard your search and restart it` | 0 | **0** | — |
| `The cap is defined here` | 1 | **1** | `plugins/product-workflows/commands/prd-ground.md:1125` |

**No count differed from its expectation.**

## 4. Live smoke runs

Every live run used the headless CLI with `--plugin-dir <worktree>/plugins` and a `--settings` JSON disabling the installed copies of the family's plugins, on a throwaway fixture under `.superpowers/sdd/2026-10-01-verifier-blind-batched/smoke/`. Results were read from `--output-format stream-json --verbose`, never from the plain-text result (section 9 says why). The results files are `smoke/task-9a-results.md`, `smoke/task-9b-results.md`, `smoke/final/results.md` and `smoke/dispute/results.md`.

### 4.1 Tree evolution: which checks still describe the final tree

Four smoke rounds ran, each on a tree that later fixes superseded. **No live run was made on `d2fea465`.**

| Round | Tree | Spend | What it ran |
|---|---|---|---|
| Task 9A | about `321cbf94` (after Task 7, before the merge of `origin/main`; the results file records no SHA) | not recorded (budget caps $1, $3, $3) | direct agent dispatches: precedence, `INPUT_UNBLIND`, `INCOMPLETE` |
| Task 9B | `25d32a05` | $20.27 | two `/prd-ground` fixture runs, plus one refused attempt |
| Final re-run | `248613f0` | $15.49 | two `/prd-ground` runs |
| Dispute | `d77186a4` | $13.27 | two direct compare dispatches, one `/prd-ground` run |

Total recorded spend: **$49.03**, excluding 9A. (9B's per-run figures sum to $20.26; the results file states $20.27.)

What changed on the agent and Phase 7 after each round, and so what the earlier result still proves:

- **`INPUT_UNBLIND` (9A, about `321cbf94`).** Not re-run live since. The agent file changed afterwards — the minors wave (`011bcc9d`: step 1's lead-in, the `mode` refusal, "no usable blind result"), the `blind_disputed` step (`d77186a4`), and the `:222` hard rule (`f763bcb0`) — none of them touches the field check that precedes step 1. The structural proof is that every later full run observed 0 answer fields across all derive dispatches, so a blind dispatch is what the orchestrator sends, but a dispatch that carried an answer field was **not** exercised again after 9A.
- **`INCOMPLETE` (9A, then D1 at `d77186a4`).** Re-observed on `d77186a4`: D1 returned `status: INCOMPLETE` with an `outcome` and `own_*` byte-identical to the input. Changes since are scoped to `blind_disputed` and the control-forced rule; the shape was not re-run on `d2fea465`.
- **Verified by reading only, after the last live run.**
  - R21, the control-forced `contradict` is never disputable (`f763bcb0`), including its copies in the agent's `blind_disputed` hard rule, `grounding-format` §8, the spec, the docs page, both CHANGELOGs and the `brd-route.md` map line.
  - The disagreement-note rule: on a dispute settled `unprovable`, the record's `notes` state the disagreement and nothing else (`f763bcb0`). The live run had shown notes from the second compare arguing `agree` beside `outcome: unprovable`; the fix was read, not re-run (ruling R22(b)).
  - The per-pass and per-second-opinion retry wording, the Final report's "which route or routes of the three forced it", and the agent's `:222` hard rule narrowed to match steps 5a and 6.
  - The three clause slips of `d2fea465` (Phase 8's closed field list, "route or routes", a second opinion's entry under *Retry once*), which the controller checked by reading the word diff and no reviewer subagent re-read.
- **Still true of the final tree because the code did not change since:** nothing in `d77186a4..d2fea465` touched Phase 3, the baseline rules (§4.1), supersession or the batching rule, so the 9B/final results for those stand up to the commits in between that changed them (see 4.7).

### 4.2 Precedence: the worktree copy loaded, not the installed one (9A)

A dispatch asking for the first sentence of `product-workflows:grounding-verifier`'s description returned the new one — "Independently re-derives grounding findings in batches — [CG#n] from one pinned repository, [DG#n] from one exported frame set — in two dispatches its caller makes in order." The brief's expected substring "in batches" is present, and "derive mode" is in the second sentence, not the first; the check passes on "in batches" alone, which the old description never carried. Later rounds corroborate it without a dedicated check: `blind_disputed` exists only in the worktree copy, and D1 and D2 returned it.

### 4.3 Blindness: 0 answer fields across every derive dispatch observed

`chk.py` counts, in each stream, the verifier dispatches and how many derive dispatches carry `verdict:`, `evidence:`, `control:` or `cites:`:

| Run | Tree | Dispatches | Derive dispatches with an answer field |
|---|---|---|---|
| 9B run 1 | `25d32a05` | derive, compare, compare | 0 |
| 9B run 2 | `25d32a05` | derive, compare | 0 |
| Final run 1 | `248613f0` | derive, compare | 0 |
| Final run 2 | `248613f0` | derive, compare, compare | 0 |
| Dispute F | `d77186a4` | derive, compare, derive, compare | 0 |

**0 of 5 runs, 0 of every derive dispatch.** Each derive entry carried only `id`, `claim` and `commit` (plus `mode` and `repo_path` per batch).

### 4.4 `INPUT_UNBLIND` and `INCOMPLETE`: the direct checks (9A)

- **`INPUT_UNBLIND` (step 5): PASS.** A `mode: derive` dispatch whose CG#99 carried `evidence` returned batch `status: INPUT_UNBLIND`, `field: evidence`, `finding: CG#99`, no `findings`, with **0 tool calls**, so no repository was read after the answer had been seen.
- **`INCOMPLETE` (step 6): PASS under the revised expectation.** A `mode: compare` dispatch whose `derived` carried an `own_verdict` of `REWRITTEN` resting on an absence and no `own_control` returned the finding `status: INCOMPLETE` with `own_verdict` and `own_evidence` byte-identical to the input, no invented `own_control`, and `outcome: agree` with `control_outcome: fired`. The brief's expectation "no outcome" predates ruling R5, which makes compare run step 6 on an `INCOMPLETE` entry and return the outcome so Phase 7 can use it after the retry; the check was marked against R5.

### 4.5 Supersession: the planted wrong finding was superseded (9B step 4)

In the fixture's specs repo `[CG#3]` (the `[FR#2]` finding) was changed to `verdict: REWRITTEN` with a false premise ("a new order starts in status pending"). A re-run produced `[CG#3]` as `verdict: SUPERSEDED`, `prior_verdict: REWRITTEN`, and the successor `[CG#7]` as `CONFIRMED`, `outcome: contradict`, notes `supersedes [CG#3]`. The re-run re-verified 6 findings in one batch (1 derive, 1 compare, no retry) and the derive carried 0 answer fields. Run on `25d32a05`.

### 4.6 `/prd-ground` fixture runs (9B, `25d32a05`)

Run 1 produced five findings, every one with an outcome: `[CG#1]` baseline, `[CG#2]` `[FR#1]` `extend`, `[CG#3]` `[FR#2]` `agree`, `[CG#4]` `[FR#3]` `REWRITTEN`/`agree`, `[CG#5]` `[FR#4]` `REWRITTEN`/`contradict`. Its tally line read "agree 2, extend 1, contradict 2, unprovable 0". The second compare was a retry because the orchestrator model had reworded note text when relaying `derived`; Phase 7 counted that `INCOMPLETE` and re-sent once with exact copies. The retry path worked, by accident.

### 4.7 Baselines: no owed control, and one live baseline after a re-run

Both came out of the 9B run and were **fixed after it**, then re-checked on `248613f0`:

- **Found (9B).** A baseline finding (`grounding-format` §4.1) has no search to control, yet the verifier returned `contradict` for it on every first run, because §2.2 and the Phase 3 writer spec did not say a baseline owes no control; and a plain re-run added a second live baseline beside the first.
- **Fixed.** `011bcc9d`: §2.2 gained the rule that a baseline owes no control (§4.1 rule 4), and each run supersedes the repository's earlier baselines (§4.1, Phase 8 *Supersede the earlier baselines*). `2eec5305` and `90dd7434` made the supersession resolve ids against `baselines.md` rather than parse them out of a `claim`, and fixed `baselines.md`'s repository identifier as the remote slug.
- **Re-checked live on `248613f0`:** (b) the baseline `[CG#1]` is `CONFIRMED`, carries no `control`, `outcome: agree`, with a note that it owes none; (e) after a re-run `[CG#1]` reads `SUPERSEDED`, `prior_verdict: CONFIRMED`, and `[CG#6]` is the one live baseline, both entries in `baselines.md`; (f) the re-run's derive carried `CG#6, CG#2, CG#3, CG#4, CG#5` and never `CG#1`, so the earlier baseline was not re-verified.

### 4.8 Disputes (`d77186a4`)

- **D1, a positive dispute: PASS.** A compare whose `derived` claimed `REWRITTEN` on the absence of database code with no control returned `outcome: contradict` and `blind_disputed: true`, citing "a REWRITTEN resting on an absence no fired control backs", with `own_*` unrevised. The verifier also noted the original's control was missing, which became R21.
- **D2, a negative case: PASS.** A compare where only the original differed from a well-supported blind `CONFIRMED` returned `outcome: contradict` and `blind_disputed: false`, because the test is the blind record's own consistency and never the original's disagreement.
- **A natural dispute settling `unprovable`: PASS.** In the full run `[CG#5]` (`[FR#4]`) came back from the first compare as `contradict` with `blind_disputed: true`; one fresh derive and compare produced a second blind verdict of `NOT-PROVABLE`; the two disagreed, so the outcome settled `unprovable`, the original `NOT-PROVABLE` verdict was kept, and the Final report flagged "inconclusive: two blind re-derivations disagreed". The same run's `[CG#1]` to `[CG#3]` were `agree`, `[CG#4]` `agree` with `REWRITTEN`.
- **Echo on structured values.** In that run the orchestrator paraphrased the free-text `notes` of `derived` in the first compare relay and said so, and the echo check passed (change C), where on `248613f0` the same paraphrase had forced a retry.

### 4.9 The verification block prints; the cost statement does not

- **The verification block: PASS (`d77186a4`).** The Final report printed "Verification: 1 repositories × 4 claims · batches: tinyapp 1; frame sets: none · dispatches: 2 derive, 2 compare, of which 0 retries and 1 second opinions (1 derive + 1 compare) · on-file claim findings re-verified: 0 (Phase 1's M: 0)". The arithmetic matches the run's dispatch list.
- **The cost statement was NOT printed by a headless Phase 1: FAIL, four runs.** Phase 1's "This requirement set has N claims …" statement did not appear in the assistant text of either 9B run (`25d32a05`) or either `248613f0` run, the latter being the first runs after item 13 moved it to the phase's opening paragraph. In the `248613f0` runs the `docs grounding:` line printed beside it was missing too. So the fix of `011bcc9d` item 13 did not make a headless run print it. The dispute run's results file records only the Final report block, so whether Phase 1's statement printed on `d77186a4` is **unobserved**. The user's decision at that point (decision 2 below) was to make the **Final report** print the actual arithmetic, which is the block above, and which a headless run does print. The statement at Phase 1 is kept in the command and no live run has shown it on screen.

### 4.10 The final tree (`cca78582`, plugin content of `d2fea465`), and the leak it found

Run at the user's request before the merge, two `/prd-ground` runs on a fresh fixture, $17.87 (results: the ledger's `smoke/finaltree/results.md`).

- **Run 1: PASS, one check inconclusive.** Blindness held (0 derive dispatches carried an answer field); all 5 findings carry an outcome; the Final report's verification block printed with real numbers ("1 repositories × 4 claims · batches: tinyapp 1 · dispatches: 1 derive, 1 compare, of which 0 retries and 0 second opinions · on-file claim findings re-verified: 0 (Phase 1's M: 0)"). **No dispute occurred** — every `blind_disputed` was `false` — so the rule that a disagreement-settled `unprovable` records both blind verdicts and the first compare's dispute reason (`f763bcb0`) was **not exercised live**; it is verified by reading only. The dispute path itself ran live on `d77186a4` (4.8).
- **Run 2, R21: PASS.** An on-file `[CG#5]` (`[FR#4]`) planted as `REWRITTEN` asserting an absence with no `control` came back `control_outcome: missing`, outcome `contradict`, `blind_disputed: false`; no second-opinion derive was dispatched; the on-file `contradict` branch superseded it (`prior_verdict: REWRITTEN`) and its successor `[CG#7]` carries the blind verdict and the verifier's own control. The case R21 exists for — a dispute raised on a control-forced `contradict` — did not arise, because `blind_disputed` was `false`; that branch is verified by reading only.
- **A blindness leak found live, and fixed (`7d6edef5`).** The run's session had the fixture's specs repository as its working directory, and the blind derive agent read that repository's commit history — a bare `git` command rather than `git -C "<repo_path>"` — and saw the plant's commit subject naming the planted verdict. The derive dispatch itself carried nothing. The agent's rules said to name every command's source and to read nothing under `$SPECS_PATH`, framed as correctness; `7d6edef5` adds a hard rule, in both modes and stated as a blindness rule, that no command reads the session's working directory (every `git` is `git -C "<repo_path>"`; every `Read`/`Grep`/`Glob` takes an absolute path or one under `repo_path` or `frame_set_dir`), and `grounding-format` §8 now lists the specs repository's files and history among what the blind step is never given. This fix is **verified by reading only**; no live run followed it. The outcome of run 2 did not depend on the leak, since the control route that decided it is deterministic.

## 5. Fixture adjustments the plan did not anticipate

- **Key `SMOKE-1`.** The plan's `PRD-SMOKE-1` is not a valid key: `-SMOKE` is not followed by digits, against `^[A-Z][A-Z0-9_]*(-\d+)+$`. The first attempt stopped verbatim on `PRD_GROUND_NEEDS_KEY`. The fixture now has frontmatter `key: SMOKE-1`, the folder `PRD-SMOKE-1-tiny-orders`, and the command invoked as `prd-ground SMOKE-1`.
- **`## Functional requirements` heading.** The route-fork step reads `[FR#n]` only under that heading (and `[AC#n]` under `## Acceptance Criteria`); the plan's `## Requirements` heading was renamed.
- **A 6-line `app/orders.py`.** The plan's `app/orders.py` has 6 lines and its Step 6 citations use `lines: [7]`, a line that does not exist; the verifier noticed and flagged it in `notes` while returning `own_evidence` unrevised. The correct line is 6. The plan was not corrected; this record states it.
- Smaller, mechanical: bare origins created with `git init --bare -b main` and `git remote set-head origin main` on the specs repo (so `origin/HEAD` resolves); the prompt's `--no-docs.` split onto its own paragraph so the token is not `--no-docs.`; the run's output path made absolute because `run.sh` changes into the specs repo.

## 6. Review history

The ledger is `.superpowers/sdd/2026-10-01-verifier-blind-batched/progress.md`. Implementers were Sonnet; reviewers Opus, except where noted. Counts below are from the ledger and the fix reports and are as it reports them; the ledger does not number every minor, so where it does not, a figure is marked.

**Per task**

| Task | Commits | Review 1 | Fix rounds |
|---|---|---|---|
| 1 `grounding-format` §8 and §4.1 | `511d1a1b` → `25a87761` | needs fixes: 1 Critical (paragraph inserted mid-sentence), 1 Important (§4.1 rewrapped), a stray `.backup` file | round 1: 2 addressed, 1 open (a 111-column line); round 2: 0 open. Clean |
| 2 | folded into Task 4 step 1 | — | no dispatch |
| 3 `grounding-verifier` agent | `f6b15366`, `749003ff` | needs fixes: 1 Important (`INCOMPLETE` returned no outcome, so Task 4's branches were unreachable; became R5), 5 Minor | round 1: 6 addressed. Clean |
| 4 Phase 7 dispatch | `c53b357c`, `da17c56b`, `29ee87eb` | needs fixes: 3 Important, 10 Minor | round 1: 10 addressed, 2 open, 1 new Important, 3 new Minor; round 2: 5 addressed. Clean |
| 5 Phase 1 cost statement | `707026a9`, `418b6942` | needs fixes: 2 Important (N named only the BRD route's step; the `--no-code` reason was false), 3 Minor | round 1: 5 addressed. Clean |
| 6 docs, rules, rationale | `e2326c3f`, `3cbd9f04` | needs fixes: 2 Important, 2 Minor | round 1: 4 addressed. Clean |
| 7 count sweep | `321cbf94` | no findings; 1 live stale sentence fixed by the implementer | none |
| 8 release | `25d32a05` | approved; 1 Minor, dismissed | none |

**Wave over the whole branch**

- **Minors wave** (`011bcc9d`, Opus): every minor deferred by the per-task reviews, the design spec's stale sentences, and four smoke defects the user ruled to fix in this branch (the missing cost statement, a baseline owing a control, a second live baseline after a re-run, a stale `Claude Opus 5` trailer in `phase-handoff` §2.4): 16 items, all done.
- **Final whole-branch review** (Opus, over `fbd68872..011bcc9d`): **Ready to merge with fixes — 0 Critical, 0 Important, 8 Minor**, gates `EXIT=0`, every deferred minor fixed, rulings R2, R5 to R11 and R13 implemented. It also put nine decisions to the controller (DJ1 to DJ9); see the dismissals below.
- **Final fix wave** (`2eec5305`): the 8 Minor plus DJ1 and DJ6, reported as nine numbered items, all done.
- **Residual fix** (`4c35d197`, ruling R17): the two residuals that wave left (the equal-pin stop moved to Phase 3; spec §4 updated). Scoped re-review over `011bcc9d..4c35d197`: **all 10 addressed**, 5 new Minor and 1 pre-existing one.
- **Precision fix** (`90dd7434`): those six. Scoped re-review over `4c35d197..90dd7434` (Sonnet): **all 6 addressed**, 2 new omissions.
- **Omission fix** (`248613f0`): the two. Checked by the controller reading the two-sentence word diff. The review cycle closed.
- **Smoke-driven wave** (`d77186a4`, rulings R19, R20): the live re-run on `248613f0` failed (a) and (g), the cost statement, and showed a lossy relay of `derived` and a blind `REWRITTEN` overriding an original `NOT-PROVABLE` the compare notes called an overreach. The user decided (decision 1 to 3 below); the wave added the second blind opinion, the Final report block and the structured-value echo. Scoped re-review (Opus): **A, B and C addressed, 6 Minor**.
- **Final batch** (`f763bcb0`, rulings R21, R22): those six, R21, and two smoke items. Scoped re-review over `d77186a4..f763bcb0`: **all addressed**, 3 one-clause slips.
- **Clause wave** (`d2fea465`): the three slips. Checked by the controller reading the word diff; **no reviewer subagent re-read it**. The review cycle closed there.

**Tally.** Fixed: every finding any reviewer raised, with none left open at the close. By the ledger's own counts the per-task rounds fixed 36 (Task 1: 4; Task 3: 6; Task 4: 17, being 13 plus 4 new at its re-review; Task 5: 5; Task 6: 4), the minors wave 16 items, and the final fix wave 10 (8 Minor, DJ1, DJ6). The scoped re-reviews then raised 5 plus 1, 2, 6 and 3 further items, all fixed in the waves above. Those are the ledger's counts, not a re-count of the diffs. **Dismissed: 9 items**, below.

**Dismissed, with the reason:**

- Task 5's minor 6 ("a baseline can add a batch"): the cost line already says "about", and the final wave later made the arithmetic exact anyway (DJ1).
- Task 8's minor ("4 of 8 rests on the spec alone"): the primary record is issue #73's body, which the rationale's "Blind by construction (#73)" section cites.
- Phase 8's second and third not-written kinds overlapping (a Task 4 deferral, then DJ7): both keep the existing outcome, so the behaviour is identical and no reader is misled.
- DJ2 (the class-4 sweep re-derives although the derive input is unchanged): kept, because spec §3 step 6 requires both steps and a re-derivation is never wrong, only costlier.
- DJ3 (the agent recognises a baseline by its §4.1 claim text): kept, because the claim is the premise it re-derives, not an id parsed from text.
- DJ4 (a decision citing a baseline would reopen on a re-run): not a defect, because §4.1 rule 3 says nothing consumes a baseline, so no decision may cite one.
- DJ5 (`--rebaseline`'s "the old findings" reading): kept; it matches the command's existing wording.
- DJ8 (the invariant says "Opus" without a `--enforce-model` carve-out): kept; it is the family-wide way to state the pin.
- DJ9 (no up-front synopsis argument for repositories): outside this spec; the Final report block makes the cost visible regardless.

## 7. Rulings and the user's decisions

One line each: what it decided, then its cost if wrong.

- **R1:** run Task 0 steps 2–3 at once and defer step 1 (confirm #70 on main, record the versions) to before Task 8, since #70 needs the user's approval to merge; cost: one rebase conflict in `prd-ground.md`, resolved by hand.
- **R2:** Task 4's batch-level `INPUT_MISSING` bullet also names a `[CG#n]` batch naming more than one commit, since Task 3's contract returns it; cost: one extra clause.
- **R3:** Task 1 verifies the retired §4.1 phrase with the wrap-insensitive counter, because a plain grep is vacuous on a wrapped phrase; cost: none.
- **R4:** accept the subagent's `Co-Authored-By: Claude Sonnet 5.5` trailer, since it names the model that wrote the commit; cost: inconsistent trailers in history, cosmetic.
- **R5:** compare marks `INCOMPLETE` but still runs step 6 and returns `outcome` and `control_outcome`, so spec §3.5's after-retry outcome is readable; cost: an `INCOMPLETE` entry carries an outcome a careless caller might act on before the retry, which Phase 7 retries first by rule.
- **R6:** Task 4 adds `INPUT_UNBLIND` beside `INPUT_MISSING` in Phase 11's "getting its own dispatch contract wrong" list, as spec §3.4 routes it to `emit-block`; cost: one clause.
- **R7:** Task 3's five minors go into its fix round instead of being deferred, under the standing fix-all-known-bugs rule; cost: a slightly larger fix diff.
- **R8:** Phase 7's status lead-in refuses only batch statuses other than `OK` and a finding's `INPUT_MISSING`; an `INCOMPLETE` compare entry may carry an outcome and is settled by *Retry once*; cost: none.
- **R9:** after its retry, `INCOMPLETE` plus `unprovable` proceeds like `agree` and `extend` through reconciliation and normalisation, and the Final report notes the missing blind control, because spec §3.5 has an incomplete-return rule only under `contradict` and stopping would discard the pass in the commonest state; cost: an `unprovable` finding proceeds whose blind `NOT-PROVABLE` lacked a control, changing no record.
- **R10:** the class-4 sweep cites the cap instead of restating 25, so the plan's "stated here and nowhere else" holds; cost: none.
- **R11:** Task 4's minors 4 to 11 and 13 go into fix round 1, and minor 12 is adopted: an on-file finding still incomplete after its retry writes nothing, keeps its outcome, is reported "not verified by this run" and the run continues, while an own-run one stops; cost: an on-file finding keeps an earlier run's outcome for one more run, and the report says so.
- **R12:** a finding left incomplete by its derive return goes straight to its retry derive, and "a batch of its own" means one batch per group holding that group's incomplete findings, under the cap; cost: one extra small dispatch.
- **R13:** Task 5's Phase 1 cost line quotes the cap's value, and Phase 7's exclusivity claim becomes "The cap is defined here; Phase 1's cost line quotes it and must change with it"; cost: none.
- **R14:** accept the shortened `agents.md` row for the grounding-verifier (191 characters), because check 6 fails any cell above 200 and the plan's text was 327; cost: the row omits "from their source" and "refusing a dispatch that carries it", which the command page and the agent both carry.
- **R15:** split Task 9, running the three agent-only checks before #70 merged and the `/prd-ground` runs on the final tree after Task 8, to avoid idling and running the costly smoke twice; cost: the agent-only checks re-run if the agent file changes (it did change afterwards; section 4.1 says what was and was not re-run).
- **R16:** Task 0 step 1 merges `origin/main` into the branch instead of rebasing, because the branch was already pushed as a backup and a rebase would need a force-push; cost: one extra merge commit in the branch history.
- **R17:** fix both residuals of the final fix wave before its scoped re-review, overriding the skill's single-fix-wave limit under the user's zero-known-bug rule, and move the equal-pin stop to Phase 3 so the mapping is unique by construction; cost: one more small commit.
- **R18:** accept that pre-slug `baselines.md` entries (a path or a directory name) may be missed by Phase 3's shared-pin stop, because the check is purely additive, no record shows how old entries were written, and a false fire needs a directory name equal to another repository's slug at the identical SHA; cost: a legacy folder misses one stop it never had.
- **R19:** compare sets `blind_disputed` only where the blind result's own evidence does not establish its own verdict under `grounding-format` §3, never because the original differs; only a `contradict` from a differing `own_verdict` is disputable; a dispute triggers one fresh derive and compare; agreement stands, disagreement settles `unprovable` with the original kept and flagged inconclusive; cost: one extra derive and compare per dispute.
- **R20:** accept that a disputed `contradict` whose blind verdict also lacks its owed control gets the second opinion before the incomplete-return stop, which is better than stopping the run; cost: one finding settles `unprovable` instead of stopping.
- **R21:** a `contradict` that control normalisation forces is never disputable, even where `own_verdict` also differs, because the control route is deterministic and this removes a double path; cost: a `contradict` whose blind verdict might also be disputable proceeds on the control route.
- **R22:** accept (a) the agent setting `blind_disputed` on a control-forced `contradict` that Phase 7 ignores, since the flag stays a true statement about the blind record; (b) verifying the disagreement note by reading and not by another live run; (c) the illustrative return-field lists in `/brd-split` and `/brd-interview` not naming `blind_disputed`, since the closed-field gate refuses it; cost: (b) a note-content slip caught on first real use.
- **One ruling that was not numbered** (change #70's, recorded in the ledger): `phase-handoff` §2.1's gate treats `specs_git: misrooted` as blocked, and the preflight performs no write under it but still runs its fetch and read-only classification. It belongs to #70, not to this branch.

**The user's decisions**

- Pause at 13:47 and resume at 14:46; both branches pushed as backups.
- #70: fix all four findings of the waves 6 to 7 review, keeping the left-behind line (the zero-known-bug policy); one more whole-branch review by a clean-context reviewer; then approve the merge (it landed as `fbd68872`) and delete the merged branches.
- Task 9 smoke defects: fix all four in this branch (the missing cost statement, a baseline owing a control, a second live baseline, the stale trailer).
- After the re-run on `248613f0` (08:5x): (1) a blind dispute gets a second blind opinion; (2) the Final report prints the actual cost arithmetic; (3) the echo is compared on structured values only; then a scoped re-review and one more live run.
- The standing rule from the user's memory: deferred review minors get a fix wave before the final review and the push.

## 8. Known residuals

- **A headless Phase 1 compresses its printed lines.** The cost statement and the `docs grounding:` line did not appear in four headless runs (section 4.9). The Final report block prints. An interactive session has not been observed either way here.
- **Pre-slug `baselines.md` entries may be missed by the shared-pin stop (R18).** The stop is new, so a legacy folder only misses a check it never had.
- **The relay of `derived` is lossy.** The orchestrator model paraphrased `derived`'s free-text notes in at least four of the five full runs (9B run 1, both `248613f0` runs, the dispute run); the structured-value echo makes that harmless where it is observed (one run, section 4.8), and a second opinion's relay was byte-for-byte, but the paraphrasing itself is not prevented.
- **Verified by reading only:** R21 and the disagreement note (R22(b)), the per-pass retry wording, the `:222` hard rule, and the three clause slips of `d2fea465`, which only the controller read.
- **`INPUT_UNBLIND` has not been re-run since 9A.**
- **Accepted by ruling:** R9 (an `unprovable` proceeds after a retry with its blind control missing), R11 (an on-file finding keeps an earlier outcome and is reported), R14 (the shortened agents row), R20, R22(a) and (c).
- **Accepted by dismissal:** DJ2 (a sweep re-derivation that costs an extra dispatch on a rare path) and DJ4 (a decision that cites a baseline would reopen on a re-run, which §4.1 rule 3 forbids).
- **Cost is approximate by design.** The Phase 1 statement's arithmetic excludes retries, the class-4 sweep, Phase 6 successors and second opinions, and says so.
- **Spend** on live runs was $49.03 on four rounds, plus 9A's unrecorded spend under its $7 of budget caps.

## 9. The external side effect

Every headless `claude -p` run triggered the user's Stop hook, which writes `/workspace/vault/wiki/hot.md` in a vault outside this repository. The runs were five `/prd-ground` runs on three trees, one refused attempt (the invalid key), and the direct dispatches (three in 9A, two in the dispute round); the hook also turned each plain-text result into that wiki message, which is why results were read from `--output-format stream-json`. The user was told when it was first noticed (Task 9A) and accepted it. Nothing else outside the repository was written, and the plugin repository itself is unchanged by any run.

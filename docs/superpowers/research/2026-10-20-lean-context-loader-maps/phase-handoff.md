# Loader map: `workflows-core:phase-handoff`

File: `/workspace/ai-workflows/plugins/workflows-core/references/phase-handoff.md`. It has 517 lines, **136,511 characters** (137,770 bytes; `wc -c` counts bytes). Every character count below counts Unicode characters including each line's newline, measured with `/tmp/claude-502/-workspace-ai-workflows/80e0a056-a775-409e-9cb9-213f6b475bf7/scratchpad/ph_ranges.py` and `/tmp/claude-502/-workspace-ai-workflows/80e0a056-a775-409e-9cb9-213f6b475bf7/scratchpad/ph_sets.py` (run them as `python3 -I <script> <file> name=a-b …`). Line ranges are inclusive.

## 0. Section map

| Section | Lines | Chars |
|---|---|---|
| Title + preamble (scope L3, *The principle* L5, relation to `specs-repo-git` L7, relation to `code-handoff` L9) | 1–10 | 1,994 |
| §1 Hard rules (rules 1–4 inherited, 5–7 divergent) | 11–25 | 2,909 |
| §2 `handoff-to-main` (intro 26–29) | 26–183 | 29,038 |
| — §2.1 Gate (gate 30–35, push-target probe 36–37, why `origin` 38–39) | 30–39 | 2,945 |
| — §2.2 Branch resolution and collision rule | 40–60 | 6,702 |
| — §2.3 Staging | 61–85 | 6,033 |
| — §2.4 Commit | 86–91 | 1,322 |
| — §2.5 Push | 92–99 | 1,210 |
| — §2.6 Open the pull request (existing-PR probe 104–109, `OWNER_REPO` derivation 110–129, SSH alias 130–131, host kept + slug test 132–134, expression history 135, capability probe 136–139) | 100–139 | 5,108 |
| — §2.7 Title and body | 140–145 | 774 |
| — §2.7.1 Pull-request template | 146–168 | 2,945 |
| — §2.8 Failure discipline | 169–172 | 286 |
| — §2.9 Caller-supplied inputs | 173–183 | 1,199 |
| §3 `require-on-main` (intro 184–187) | 184–319 | 49,049 |
| — §3.1 Gate | 188–191 | 337 |
| — §3.2 Inputs and primitives (inputs 194, `./` rule 196, `<default-ref>` 198, four primitives 200–206) | 192–206 | 4,779 |
| — §3.3 State table (table 207–225, prose 226–247) | 207–247 | 12,080 |
| — §3.4 Row F delegation (intro 250–253, table 254–279, BRD prose 280–289) | 248–289 | 26,316 |
| — §3.5 Locating branch and PR | 290–297 | 708 |
| — §3.6 Degraded verification | 298–303 | 1,701 |
| — §3.7 Return value | 304–319 | 2,780 |
| §4 heading | 320–321 | 17 |
| — §4.0 Three downstream classes (class table 322–331, *What this table is* 332–335, register 336–366, *Never infer* 367–372, set rule 373–374, classify-by-reader 375–376) | 322–376 | 23,076 |
| — §4.1 Outcome line (scope 377–414, table 415–430, Declined naming 431–432, committed-paths list 433–434, `<downstream-clause>` 435–436, `<next-phase-clause>` 437–443, *Row F is the next phase's reading only where* 444–445, PRD note 446–447, set-span 448–449, closing 450–451) | 377–451 | 14,219 |
| — §4.2 No-`gh` fallback text | 452–461 | 462 |
| — §4.3 Consent choice (arity 464–467, *not the whole of this section* 468–469, refused remedy 470–471, four arrays 472–487, parenthetical 488–489, selection 490–491, flag line 492–497, probe + no-remote line 498–501, no-reword 502–503, option meanings 504–505) | 462–505 | 12,597 |
| — §4.4 Stop contract | 506–509 | 389 |
| §5 Caller contract (rules 1–4 at L514–517) | 510–517 | 2,761 |

## 0.1 Caller census, re-derived

Matched whitespace-insensitively, which a one-line grep is not (`/brd-interview`'s `handoff-to-main` call wraps a line):

- **whole file (`args: "phase-handoff"`)**: 21 call sites in 20 command files (`/brd-reconcile` twice), plus one non-call mention inside the reference itself (L470, a grep recipe).
- **`handoff-to-main`**: 20 call sites in 19 files. The scratchpad's "19" counts files, or misses the wrapped one.
- **`require-on-main`**: 18 call sites in 14 files (`/create-ard`, `/create-prd`, `/specify` and `/prd-ground` twice each).

**Callers the census does not see**, because they reach the file by citation (the "Core references" preamble loads the whole file with no entry point) or by path:

- `/brd-interview` Phase 0 step 6 executes `require-on-main` (§3) with no loader call at that step. Its only loader call is the Phase 10 whole-file one. This brings the consumer count to 15, which matches `.claude/rules/workflows-core-git.md`.
- `/idea` Phase 5 executes `handoff-to-main` (§2) only after its whole-file load, with no entry-point call.
- `/promote-decisions`, through `workflows-core:architecture-promotion` L84 and L229, uses §4.3's probe, the **gated — stopping** array, `handoff-to-main` (§2), and §2.6's `OWNER_REPO` derivation applied to the *architecture* repository.
- `/frames` (`workflows-core`) reads the file by `${CLAUDE_PLUGIN_ROOT}` path and uses §2, §3.4, §4.0, §4.1 and §4.3.
- `dev-workflows:code-handoff` uses §1 rules 2, 6 and 7 as contrast, §2.3's `-z` reason, §2.6 (SSH alias, host kept), §2.7.1 (template) and §3.5's primitive. It serves `/implement`, `/vuln` and `/upgrade`.
- `docs-workflows:finish-and-handoff` and `/document` use §2.6's alias rule and §2.7.1.
- `docs-auditor` and `docs-audit-reviewer` use §3.2's `./` rule only.
- Citation-only users: `ard-resolution` (§3, §3.2, §3.4 ARD row), `next-phase-offer` (§3, §3.4, §4.1's emitted line), `components` (§3), `context-management` (§3.4), `dependencies` (§2.6), `escalation-rules` (§2 `body_facts`) and `bundle-packaging` (§1 rule 7, §2, §2.1, §4.3).

**Structural fact that matters for the design.** Every one of the 20 `handoff-to-main` call sites runs in the same Handoff phase, right after a whole-file load used to present the §4.3 array. Today a run that takes option 1 therefore reads the whole 136.5k-character file **twice** in that phase. As a result, `handoff-to-main` has never run without §4.0–§4.3 already in context, so no shipped run has tested whether §2 stands on its own.

---

## 1. `handoff-to-main`

### 1.1 Where it is defined
`## 2. \`handoff-to-main\` — the producer entry point` names it literally. It spans **L26–183, 29,038 characters**, including §2.1–§2.9. §2.7.1 is also run by `code-handoff` §2.7 and `finish-and-handoff` §5 under their own consent (L28).

### 1.2 What it needs from the rest of this file

| Part | Lines | Chars | Reason |
|---|---|---|---|
| Preamble | 1–10 | 1,994 | L3 gives the scope. L7 says this file owns *deliverables* and `specs-repo-git` owns *bookkeeping*. L9 guards against carrying `code-handoff`'s repository-scope staging and prompt-free commit back into §2. No § reference reaches L9; it is a guard, counted under "when in doubt". |
| §1 Hard rules | 11–25 | 2,909 | Rule 1 is `git -C` always, `gh -R`, and the §2.7.1 exception. Rule 2 forbids `add -A` at repository scope (§2.3 restates it). Rule 3 is the prefix set, which bounds §2.9's `prefix` row. Rule 4 is never-destructive, widened with `stash` and `checkout --`. §2.2's switch carries the uncommitted deliverable, and §2.4's `restore --staged` carve-out and the `lift` exception are stated here. Rule 5: not fatal, but must report "not handed off". Rule 6 is cited by §2.4. Rule 7 is restated in §2's intro. |
| §3.2 `<default-ref>` paragraph | 198–199 | 662 | `<default-ref>` is used undefined in §2.2: the keyless `kb` rule, rule 3's merge test, *Where a new branch is cut* (whose `switch --no-track -c <name> <default-ref>` and `diff --quiet <default-ref>...HEAD` cite "(§3.2)"), and §4.1's *Stacked* clause. The paragraph delegates to `specs-repo-git` §3.2. |
| §4.0 Downstream classes | 322–376 | 23,076 | §4.1's `<downstream-clause>`, printed on the PR-opened, already-existed and PR-not-opened rows, is "resolved from §4.0's class" (L435). The strongest-class rule (L373) decides a mixed `deliverable_paths` set. The operative part is the class test (L326–330), the register's Artifact and Class columns, and L373–375. The register's Derivation column (most of 16,179 chars) is evidence. L367–372 is a consumer rule this entry point does not need. |
| §4.1 Outcome line, scope + table + clauses | 377–436 | 8,227 | Everything §2 produces is reported through §4.1's rows. The rows §2 reaches are *Gate failed*, *Nothing to commit*, *Commit failed*, *Push failed*, *No remote*, PR opened, *already existed* and *PR not opened*, plus the appended clauses *Branch name substituted*, *Stacked*, *Declaration unaccounted for* and *Record unreadable*. Also needed: the committed-paths list (L433), the count rule of one line per offered handoff with each line naming its handoff, live for `/brd-reconcile`'s two handoffs (L379–408), and `<downstream-clause>` (L435). The *Declined* row and its `<artifacts>` naming (L428, L431–432, 1,025 chars) belong to the producer's decline path and are never reached by §2. They are kept only because they sit inside the table unit. |
| §4.2 No-`gh` fallback text | 452–461 | 462 | §2.6: "on any failure fall back to §4.2's instruction"; a non-`gh` slug goes "skip to §4.2". |
| §4.3 probe paragraph | 498–501 | 796 | §2.1 says the push-target probe runs at §4.3, before the choice, and that this entry point carries the `remote` value it set. L498 also defines the case where `rev-parse` fails and nothing is printed. Duplicates L36 in part; counted because §2.1 defers to it. |
| *Conditional*: §3.4 | 248–289 | 26,316 | Needed only when (a) a declared path is absent from §4.0's register, since §4.0 L332 says to classify it by naming its reader and §4.0's test asks whether a §3.4 row names it, or (b) §2.7's body must decide whether "the caller has" a next command, given that "a producer whose artifact has no §3.4 row has no next command to name". |

**Not needed:** §3 apart from L198, §4.4, and §5. §5 rule 1 is the producer's authoring obligation, which every caller already applies with "Emit its §4.1 outcome line". The §3.5 and §3.2 mentions inside §2 (L38, L52, L108, L132) are informational, except the `<default-ref>` row above. **Ambiguity:** L52's "for the same reason §3.2 gives for its own probe" does not say whether it means this file's §3.2 (the `2>/dev/null` rationale at L203) or `specs-repo-git` §3.2. The rule itself (`2>/dev/null`) is stated inline, so nothing operative depends on resolving it.

### 1.3 Other reference files it relies on
- **`workflows-core:specs-repo-git`**, the heaviest dependency:
  - §1 rules 1–4, 6 and 7, which §1 here inherits or contrasts.
  - §2.1: session-file shapes (`inputs_read`, the stack test) and the `-z` hazard statement (§2.3).
  - §2.2: branch set.
  - §3.1: the `misrooted` notice re-emitted on gate failure.
  - §3.2: default branch, run key set, `<default-ref>` resolution.
  - §3.3: G0 (`specs_git: blocked`) and G2 (named non-plugin branch).
  - **§3.5's `branch-key` and `branch-merged`**: rule 3's ownership and merged tests. Ancestry, rebase and squash detection live only there.
  - B2 and B3.
  - §3.6: stacks.
  - **§4 step 4, commit by pathspec with `:(literal)` and the post-commit index restore**: §2.4 says "listed, committed and followed by the index restore exactly as `specs-repo-git.md` §4 step 4 does". About 3,033 chars at L664–710 there. The mechanics are not restated here.
  - §4 step 5: upstream fallback.
  - §4.1.
  - §8 and **§8.3 `lift` / `put-back`**, around §2.2's switch.
- `dev-workflows:code-handoff` §2.2, §2.6 and §2.7 (contrast and co-callers); `docs-workflows:finish-and-handoff` §4 and §5 (contrast and co-caller).
- `product-workflows:idea-format` (*Vendored sources*) and `workflows-core:grounding-format` §6.2, both examples in §2.3. `workflows-core:escalation-rules` (*Choice lists are presented verbatim*, via §4.3).
- Through §4.0, if it is included: `ard-resolution`, `components` §6, `architecture-promotion` §1.4, `architecture-grounding`, `implementation-format`, `followup-emission`, `product-workflows:bundle-packaging` §1.1/§2.1/§5, `brd-format` §1.1/§2.1, `proposal-format` §2/§7, `coverage-ledger-format` §3. These are cited as evidence for a class, not as steps.
- In practice the `specs-repo-git` parts are in context only if the run's `specs-preflight` load delivered them. `specs-preflight` §3.4's flush runs "per §4 steps 2–6", so a correct narrowing of that file pulls §4 step 4 in too. The dependency still has to be declared, because `handoff-to-main` runs at the end of a long run, typically after compaction.

### 1.4 Minimal safe set
- **Strict:** entry point plus preamble, §1, L198, §4.0, §4.1 L377–436, §4.2 and L498–501 = **67,164 / 136,511 (49.2%)**.
- With the conditional §3.4: **93,480 (68.5%)**.
- **After the restructure in 1.5:** class as an input, so §4.0 is dropped, and §4.1 trimmed to L377–430 + 433–436 = **43,063 (31.5%)**.

### 1.5 Verdict: **SAFE-WITH-RESTRUCTURE**
A heading extract of §2 alone loses the whole reporting contract (§4.1, §4.2) and the definition of `<default-ref>`. Declaring the list above makes it lossless, but at 49% of the file. Small edits that make it both lossless and narrow:
1. Add a `class` input to §2.9: the `<next-phase-clause>` / §4.3 array value the consent step already chose. `<downstream-clause>` is then read from it and §4.0 drops out. Every caller has just made that choice.
2. Split §4.1 so the decline-only parts (Declined row L428, `<artifacts>` naming L431, `<next-phase-clause>` L437–451) are separable from the outcome rows `handoff-to-main` emits.
3. Have `body_facts` carry the next command where there is one (`/epics` already does), which removes §2.7's §3.4 lookup.
4. Declare the cross-file dependencies explicitly: `specs-repo-git` §3.5 (`branch-key`, `branch-merged`), §4 step 4, §8.3 and §3.2. Alternatively, make §2.4 self-sufficient by naming the `:(literal)`/index-restore procedure as an entry point of `specs-repo-git` that both callers load.
5. Resolve L52's ambiguous "§3.2". This is cosmetic.

### 1.6 Rationale, history and examples inside the strict set

| Where | Lines | ≈Chars | Kind | Needed for edge cases? |
|---|---|---|---|---|
| *The principle* | 5 | 562 | rationale | No, for the producer. |
| Relation to `code-handoff` | 9 | 851 | rationale/guard | Yes, as a guard: stops repository-scope staging being imported when `code-handoff` is also in context. |
| §1 rule 4's justification of the widening | 18 | 406 | rationale | No. The rule list in the same paragraph is operative. |
| §1 L20 "a reader who corrects one breaks this contract" | 20 | ~150 | guard | Weakly. |
| §2.1 why `origin` specifically, "observed live" | 38–39 | 734 | rule + history | Yes. A remote under another name counts as `remote: none`, and the probe is not optional. |
| §2.2 collision premise | 46 | ~520 | rationale | Partly. It says why `branch -D`/force are not the answer. |
| §2.2 squash/rebase rationale | 52 | 230 | rationale | Yes. Without it, a model may "simplify" to an ancestry test. |
| §2.2 why the remote ref alone is not enough | 54 | 611 | rationale (measured) | Yes, the delete-branch-on-merge edge. Rule 1 states the step. |
| §2.2 three dots / `--no-track` explanations | 57 | 244 + 385 | rationale | Yes. Both are "load-bearing" guards against simplification and a read-only `.git/config`. |
| §2.2 producer examples | 57 | 230 | example | Helpful, not required. |
| §2.2 "Cutting at HEAD everywhere…" | 57 | 279 | history | No. |
| §2.3 `-A` justification (git 2.0) | 67 | 415 | rationale | No. |
| §2.3 step 4 "Do not test existence…" incl. measurement | 68 | 1,161 (286 of it the measurement) | rule + rationale + history | Yes, the rule: never an existence test. The measurement, no. |
| §2.3 `-z` paragraph | 70–71 | 1,444 | rationale + rule | Yes. The rename/copy second field is a step; `core.quotepath=false` is a prohibition. |
| §2.3 *What this closes* | 72–73 | 441 | history | No. |
| §2.3 declared-path rule with `/idea` and `/frames` examples | 74–83 | 851 | rule + examples | Yes, the rule. Examples optional. |
| §2.5 read-only `.git/config` | 96 | ~700 | edge-case rule | Yes, container case: a push is not a failure. |
| §2.6 SSH alias, measured example | 130 | 275 of 1,006 | example | The rule, yes. The `github-ig.com` anecdote, no. |
| §2.6 host-kept rationale | 132 | ~500 of 815 | rationale | Yes, as a guard against stripping the host and mistargeting github.com. |
| §2.6 expression history "Do not simplify it back" | 135 | 430 | history/maintainer | No for execution, yes for an editor. |
| §2.6 capability-probe rationale and the `gh` allowance | 136–139 | ~600 | rationale | Partly. The operative clause "on any failure fall back to §4.2" sits inside it. |
| §2.7.1 "The template wins because…" | 167–168 | 267 | rationale | No. |
| §4.0 register Derivation column | 338–365 | most of 16,179 | evidence/history ("classed unread for one commit") | No, if the class is supplied. Yes, if the producer must classify an unlisted path. |
| §4.0 *What this table is* | 332–335 | 1,574 | maintainer | No. |
| §4.1 three-states history | 409–413 | ~300 | history | No. |
| §4.1 committed-paths "positive half" history | 433 | 302 | history | No. |
| §4.1 `/frames` story inside `<downstream-clause>` | 435 | 604 | history | No. |

---

## 2. `require-on-main`

### 2.1 Where it is defined
`## 3. \`require-on-main\` — the consumer entry point` names it literally. It spans **L184–319, 49,049 characters** (§3.1–§3.7). §3.4 alone is 26,316 chars (54% of §3), and each caller needs only its own row or rows of it.

### 2.2 What it needs from the rest of this file

| Part | Lines | Chars | Reason |
|---|---|---|---|
| Preamble | 1–10 | 1,994 | L5 *The principle* states a scope rule no § reference reaches: "The gate applies even when the role does not change — it may be a different human of the same role, and even the same human should have to confirm". L3 gives the row-F exception. |
| §1 Hard rules | 11–25 | 2,909 | Rule 1 (`git -C` in every primitive, `gh -R` in §3.5) is implicit. Rule 3 is cited in §3.4 L250 (the "eleven prefixes"). Rule 4 is cited by row B′ (L217) and restated in row C's repair (L240). **Rule 5, "`require-on-main` is fatal by design", is cited nowhere in §3**; §3.7's "every caller then stops" relies on it. Rules 2, 6 and 7 are not needed but are inside the unit. |
| §2.6 `OWNER_REPO` derivation | 110–135 | 3,516 | §3.5: "Derive `$OWNER_REPO` first (§2.6), and skip this probe when the derivation does not validate. §2.6's slug test…". This covers the derivation (L110–129), the SSH-alias resolution (L130), host kept plus slug validation (L132–134) and the expression note (L135). Without it, the D/E probe can mistarget a GitHub Enterprise remote onto github.com and report another repository's pull request. |
| **§4.4 Stop contract** | 506–509 | 389 | The four-part stop format: what was found, what was not done, exact commands, the consequence of ignoring it. **No line inside §3 references §4.4.** It is reached only from callers ("stop per §4.4" in `/design`, `/implement`, `/create-ard` ×2, `/create-prd`, `/specify` ×2 and `/epics`). An extractor that follows §-references out of §3 cannot find it. |
| §4.0 *Never infer an artifact's merged-ness from a sibling's gate* | 367–372 | 1,877 | A consumer rule housed in the producer-side §4.0. It binds `/brd-split` (steps 6/7), `/prd-ground` (step 6) and `/brd-interview` (step 6), which each state the sibling implication with a limiting clause. Reached from §3 only through the `/brd-package` round row's "per §4.0" (L274). Following that reference transitively pulls in all of §4.0 (23,076). |
| §5 header + rules 2–3 | 510–513, 515–516 | 723 | Rule 2 is "before its first subagent dispatch, code scan, docs-grounding retrieval, or grill question", cited by `/conformance`, `/create-prd`, `/implement` and `/brd-interview`, with `/implement`'s and `/epics`' recorded deviations. Rule 3, "no consumer turns an optional input into a prerequisite", is cited by §3.4 L272 and L288. |

**Not needed:**
- §2 apart from L110–135. §3.2's references to §2.2, §2.5, §2.8 and §4.1 (L205) are rationale. Row B's "created … via this caller's own `handoff-to-main`" is a fact, not a step. §3.4's Epic row cites §2.2's *Where a new branch is cut* as explanation.
- §4.1 to §4.3. One exception: a producing caller of `require-on-main`, for example `/epics`, consults §4.1's *Row F is the next phase's reading* rule at its own Handoff, not at its gate.

**Within §3 itself:** §3.2's four primitives feed §3.3's rows. G must precede F; L202 and L228 state why, and that is operative. §3.5 serves rows D and E. §3.6 modifies rows: no fetch on a read-only mount, and **row C stops instead of offering its repair** there. §3.7 is the return contract, including the two caller exceptions (`/ready`, `/brd-reconcile`) and "No other caller may take either exception", which binds every caller. §3.4 holds the row-F semantics (L250–252) plus the per-caller rows.

**Mapping fact for per-row narrowing:** `/conformance`, a consumer with 1 call site, **has no §3.4 row**. Its `absent` behaviour ("traces what exists, names each document it could not read") is written in its own command and cites §3.4's general rule (L250–252). A per-caller row extractor must therefore always include L250–253.

### 2.3 Other reference files it relies on
- **`workflows-core:specs-repo-git`**:
  - §3.2: default branch, best-effort fetch, `<default-ref>` resolution, the offline clause, run key set.
  - §3.1: `specs_git: misrooted` (row C has no offer under it).
  - §3.3 G0 / §3.7: the `blocked` notice that row I re-emits.
  - §3.5 B3: row B's ownership test.
  - §2.1: session files, which C′ does not count.
  - §4.1.
  - §5: the four-part notice that §4.4 copies.
  - §8 and §8.3: `session_branch`, `lift` / `put-back` around row C's repair, and B′'s remedy.
  - §3.4: history only.
- `workflows-core:read-only-repos`: §3.6's read-only mount, read as `references/read-only-repos.md`.
- `scripts/session-branch.py`: B′'s remedy names it, via `${CLAUDE_PLUGIN_ROOT}`, "resolved".
- `workflows-core:escalation-rules`: row C's `choices:` array is presented verbatim. This is a family-wide rule, not cited in §3.
- Per-row: `ard-resolution` (ARD row, §3.7's `/ready` parallel), `components` §6 (`/epics` row), `followup-emission` (B′ rationale), `product-workflows:coverage-ledger-format` §3/§5/§5.1, `decision-register-format` §8, `addressing` §4.1/§5, and the callers' own phase steps. §3.4 states those steps, so they must be read in the command.

### 2.4 Minimal safe set
- **Strict:** all of §3 plus preamble, §1, §2.6 L110–135, §4.4, §4.0 L367–372 and §5 header + rules 2–3 = **60,457 / 136,511 (44.3%)**.
- Per caller, with only its own §3.4 rows plus L250–253: about **36,131 + its rows**. The rows range from 115 chars (`/create-ard` PRD) to 2,016 (`decisions.md` BRD row); `/prd-ground` carries 3 rows totalling 3,971. That gives about **36–41k (27–30%)**.

### 2.5 Verdict: **SAFE-WITH-RESTRUCTURE**
A heading extract of §3 silently loses §4.4, the stop contract every caller's stop depends on, because no reference inside §3 points at it. It also loses the preamble's role-scope rule and §1 rule 5, which nothing inside §3 cites. The rest is reachable by following explicit §-references. Edits:
1. Move §4.4 under §3 (as §3.8), or add an explicit "every stopping row's message follows §4.4" to §3.3 or §3.7.
2. Move §4.0 L367–372 into §3, since it is a consumer rule, or declare it.
3. Lift §2.6's derivation (L110–135) into a named block, say `owner-repo`, cited by §2.6, §3.5, `code-handoff`, `finish-and-handoff` and `architecture-promotion`.
4. Declare L5, §1, and §5 rules 2–3.

Per-row narrowing of §3.4 is possible, keyed on column 1, but fragile:
- Rows are multi-caller (`/create-ard` `/specify` (an Epic); the ARD row has five callers).
- `/conformance` has none.
- L280–288 carries caller-specific interpretive rules: `/create-prd`'s ordering of its container refusal versus the gate; route qualification is "per row rather than per command".

Keep §3.4 whole unless rows are tagged.

### 2.6 Rationale, history and examples inside the strict set

| Where | Lines | ≈Chars | Kind | Needed for edge cases? |
|---|---|---|---|---|
| §3.2 `./` rule | 196 | 819 | rule + rationale | Yes, for a specs tree nested in a larger repository. |
| §3.2 `<default-ref>` ownership rationale | 198 | ~400 of 662 | rationale | No. The first sentence is the rule. |
| §3.2 ordering of the ref-existence primitive | 202 | ~400 | rationale | Yes. It says why G runs before F. |
| §3.2 "This is not cosmetic: … row D unreachable" | 205 | 373 | history | No. The "strip `origin/`" rule is in the same bullet. |
| §3.3 *not on ref* column semantics | 226 | 464 | interpretive rule | Yes: test `stopped` first. |
| §3.3 row order, incl. `f5a9713` | 228 | 1,057 (103 history) | rationale | Partly. The order itself is the table's. |
| §3.3 *Row B is load-bearing* | 230 | 387 | guard rationale | Yes, as a guard against folding B into C. |
| §3.3 B′ explanation | 232 | 2,518 | rationale + edge cases + merge guidance | **Yes.** Covers an artifact absent at the fork point but present on `<default-ref>`, an untracked copy, why `lift` comes first in session-branch mode, and how to resolve the merge's session-file conflicts. |
| §3.3 *Row C″ exists because* | 238 | 710 | rationale | Weakly. It names the remedy (commit, stash or discard), which the row states. |
| §3.3 *Three states the C-row family used to misclassify* | 242–247 | 1,795 | history ("recorded so the narrowing is not undone") | No for execution. It explains why C′ tests the pull too and why I tests state as well as flag; both are already in the rows. |
| §3.4 intro, second paragraph | 252 | ~600 | rationale | Partly. |
| §3.4 row bodies | 254–279 | parts of 17,055 | rule + per-row rationale ("declared rather than smuggled", "never optional because…") | Each caller's own row, yes. |
| §3.4 *No count is kept here …* + check 11 | 280 | 499 | maintainer | No. |
| §3.4 route vs build-ladder prose | 282–286 | ~4,200 | interpretive rules + rationale | Yes, for BRD-route callers and `/create-prd`, `/prd-proposal`, `/brd-proposal`. |
| §3.4 *For the consumers that predate this gate* | 288 | 2,508 | history of behaviour change + rule-3 qualification | Mostly no. The closing qualification of rule 3 is interpretive. |
| §3.6 "Saying only that freshness degrades was false…" | 301 | 74 | history | No. |
| §3.7 `/ready` and `/brd-reconcile` exceptions | 314 | 1,487 | rule + rationale | Yes. Two callers act on it; all others are barred by it. |
| §2.6 expression history and alias anecdote | 135, 130 | 430 + 275 | history/example | No. |
| §4.0 L369–371 | 369–371 | ~1,200 of 1,877 | history/rationale ("found by the defect", "condemned eight correct commands") | The distinction "does this command *claim*" (L371) is interpretive, so yes. |

---

## 3. The whole-file callers (21 call sites, 20 commands)

**All 21 are the producer's Handoff phase, the consent step that precedes `handoff-to-main`.** None of them needs §3.1, §3.3, §3.5–§3.7 or §4.4. What each uses, read from the lines around each call:

| Call site | What it uses |
|---|---|
| `dev-workflows/commands/design.md:422` | §4.3 **gated — stopping** array. The decline line comes from §4.1. |
| `dev-workflows/commands/implement.md:1124` | §4.3, two arrays. §4.1 set rule and *Row F is the next phase's reading only where …*. §3.2's `cat-file -e "<default-ref>:./<path>"`. §3.4's `design.md` rows. |
| `dev-workflows/commands/ready.md:441` | §4.3 **advisory** array. §4.0 class. §2.2 collision expectations. §4.1 line. |
| `dev-workflows/commands/conformance.md:351` | §4.0 strongest-class rule over the set. §4.3 arrays (stopping or advisory). |
| `docs-workflows/commands/release-notes.md:564` | §4.3 **advisory** array plus placement of its own line relative to §4.3's flag and no-remote lines. §2.1 gate (work-tree test). §4.0. |
| `product-workflows/commands/idea.md:627` | §4.3 **gated — falling back** array. §4.1 bullet 2 quantifier. §3.4's first row. Row-F reading rule. §3.3's C rows. Then executes §2 with no entry-point call. §4.1 *Declined* line. |
| `product-workflows/commands/create-prd.md:803` | §4.3 gated — stopping. |
| `product-workflows/commands/update-prd.md:170` | §4.3 gated — stopping. |
| `product-workflows/commands/create-ard.md:736` | §4.3, two arrays. §4.1 set rule and Row-F rule. §3.2 primitive. §3.4 ARD rows. |
| `product-workflows/commands/specify.md:1028` | §4.3 gated — stopping. |
| `product-workflows/commands/epics.md:823` | Per-run choice of array (§4.1). §3.4 Epic rows. §4.0's `_coverage.md` unread. §3.2 primitive. Row-F rule. §4.1 *Declined* line. |
| `product-workflows/commands/brd-intake.md:1435` | §4.3 gated — stopping. §3.4's `brd-defect-log.md` row. §4.0. |
| `product-workflows/commands/brd-interview.md:2075` | **§4.3 in full**: §2.1 probe, flag line, no-remote line, then the array. §3.4. |
| `product-workflows/commands/brd-package.md:1212` | §2.1 gate conditions ("each is a read"). Probe. §4.3 flag and no-remote lines. Stopping array. |
| `product-workflows/commands/brd-split.md:1341` | §4.0 strongest class. §4.3 stopping or advisory. §3.4 slice rows. |
| `product-workflows/commands/brd-reconcile.md:716` | §4.3 advisory. §4.0. §3.4 (the row targets the prompt, not the review). §2.3 step 3 (staging a deletion). |
| `product-workflows/commands/brd-reconcile.md:2587` | §4.3 stopping. §4.1 two-lines rule. |
| `product-workflows/commands/prd-ground.md:1879` | §4.3 stopping. §4.0 strongest class. §3.4's conditional `/brd-split` row. |
| `product-workflows/commands/prd-proposal.md:663` | §4.3 stopping. §3.4's `/brd-proposal` row. §4.0. |
| `product-workflows/commands/brd-proposal.md:755` | §4.3 advisory. §4.0, the advisory-versus-unread reasoning. |
| `product-workflows/commands/harvest-decisions.md:42` | §4.3 probe plus stopping array. §4.0 (the guard case). |

**What the group as a whole needs:**
- §4.3 whole. That means the arrays, plus the three pre-array steps at L468, L492–497 and L498–501, which "run before whichever array is selected", and the option meanings at L504.
- §2.1, for its gate conditions and the probe at L36–38.
- §4.0, for the class, the strongest-class rule and the register.
- §4.1, for the *Declined* row with `<artifacts>` naming, `<next-phase-clause>` (four values), the Row-F reading rule and the set-span rule.
- §3.2 L196–199, the `./` form and `<default-ref>` for the "already carried" test.
- §3.4, because §4.1's gated split is "a quantifier over that artifact's rows" (L437) and L446 says "Read the rows; never carry either membership list".
- §1 rule 7.

**Coverage.** No existing entry point covers this: `handoff-to-main` is §2 and `require-on-main` is §3. A **new named entry point**, say `offer-handoff`, would cover all 21, plus `/frames` and `/promote-decisions`' consent step. Its sizes:
- **Strict** (preamble + §1 + §2 intro + §2.1 + §3.2 L196–199 + §3.4 + §4.0 + §4.1 + §4.3): **86,051 (63.0%)**.
- **Without §3.4 and §4.0's register** (the class table, L367–376, §4.1 and §4.3 kept): 41,933 (30.7%). That version is **unsafe** by the reference's own rule. It drops the authority each producer's array choice is checked against. Every command does state its class inline, but §4.0 and §3.4 are what that statement is checked against (§5 rule 4: "a command that disagrees with it is the defective half").

**The risk specific to this group.** §4.3 L468–471 records a deliberate, measured decision: the push-target probe and its no-remote and flag lines were **not** copied into producers. Every producer quotes the array right after a whole-file load, so §4.3's pre-array steps are already in front of it. Only 3 of the 20 producers name the probe (`/brd-interview`, `/brd-package`, `/harvest-decisions`), and only 5 commands name the *Declined by the user* line. The other producers get both from the loaded text. An entry point that returns the array without L468, L492–501 and §2.1 L36–38 brings back the live defect L468 and §2.1 L38 record: a `(Recommended)` push-and-open-PR offered on a specs repository with no `origin`, with no notice. Today the "no entry point" form returns the whole file, so none of this is at risk unless these callers are migrated.

**Other implicit whole-file loaders, and what would cover them:**
- `code-handoff`, `finish-and-handoff` and `/document`'s keyed PR draft use §2.7.1. A `pr-template` entry point would be **2,945 (2.2%)**.
- §3.5, `code-handoff` §2.6, `finish-and-handoff` §4 and `architecture-promotion` L84 use §2.6's derivation. An `owner-repo` entry point would be **3,516 (2.6%)**.
- `docs-auditor` and `docs-audit-reviewer` use §3.2's `./` rule; `ard-resolution` uses `<default-ref>`. A `default-ref` entry point (L196–199) would be **1,481 (1.1%)**.
- `/brd-interview`'s Phase 0 gate, `/idea`'s §2 run and `/frames` would need to switch to the entry-point form (`require-on-main`, `handoff-to-main`) to benefit at all.

**Efficiency note.** One Handoff phase that runs `offer-handoff` and then `handoff-to-main` needs their union, **112,092 (82.1%)**. Today it reads 2 × 136,511. A loader that skips parts already returned in the same run would cut that phase to about 112k. All three entry points together cover **134,456 (98.5%)** of the file. Only §5 rules 1 and 4, the authoring contract, fall outside the union.

## 4. Parts no caller needs at run time

- Authoring and maintainer-only text, **5,311 chars (3.9%)**:
  - §4.0 *What this table is* (L332–335, 1,574): "a producer adding a deliverable adds its row here".
  - §4.3's arity history (L466–467, 696).
  - §4.3's refused-remedy measurement (L470–471, 1,003). It matters to a loader designer, since it is the record of the dependency in §3 above.
  - §5 rule 1 (L514, 347) and rule 4 (L517, 1,691), which are obligations on command authors.
- History paragraphs that no step needs, all inside entry-point headings: §3.3 L242–247 (1,795), §2.3 L72–73 (441), §2.6 L135 (430), §3.4 L280's "No count is kept here" (499), most of §3.4 L288 (2,508), and the history fragments listed in 1.6 and 2.6.
- §2.7.1 (2,945) is needed by `handoff-to-main` only where `$SPECS_PATH` carries a PR template. It is mostly needed by `code-handoff` and `finish-and-handoff`.

## 5. Checks whose common outcome is "nothing to do"

1. **§2.1 push-target probe**: usually `remote: origin`. No notice; §2.5 and §2.6 run.
2. **§4.3 flag line**: usually no `specs_git: blocked`/`misrooted`, so nothing is printed.
3. **§4.3 no-remote line**: usually there is an `origin`, so nothing is printed.
4. **§2.2 collision rule 1**: usually neither ref exists, so the intended name is used. Exception: `/ready`, whose `_readiness.md` collides on most re-runs.
5. **§2.2 rule 3 reuse / `branch-merged`**: only on a collision.
6. **§2.2 *Where a new branch is cut* stack test**: only when HEAD is another plugin branch. Usually HEAD is the default branch, so the branch is cut at HEAD.
7. **§2.2 session-branch `lift`/`put-back`**: only in session-branch mode.
8. **§2.3 step 4, account for every declared path**: usually every path is staged, so no clause.
9. **§2.3 rename/copy second NUL field**: rare.
10. **§2.4 index restore after a pathspec commit**: usually no path is left to restore. **§2.4 *Commit failed***: rare.
11. **§2.5 read-only `.git/config` message**: container only. The push still succeeds and nothing is said.
12. **§2.6 existing-PR probe**: usually no open PR on a first run. It is common on re-runs, though.
13. **§2.6 SSH-alias resolution**: usually `github.com` or `https`, so a no-op.
14. **§2.6 slug validation**: usually valid.
15. **§2.7.1 template**: usually none in a specs repository.
16. **§4.1 appended clauses** (*substituted*, *stacked*, *declaration unaccounted for*, *record unreadable*): usually none.
17. **§3.1 gate / row H**: usually passes.
18. **§3.3 rows I and G**: rare.
19. **Row B′**: reached only when the worktree differs from `<default-ref>` and the run owns the branch.
20. **Rows C′/C″**: only on a dirty or local divergence.
21. **§3.5**: only for rows D and E.
22. **§3.6 degraded verification**: only on fetch failure or a read-only mount.
23. **The `./` form's nested-repository case (§3.2 L196)**: a no-op difference in the supported layout.
24. **§4.1 *Row F is the next phase's reading only where …* test** (`cat-file -e "<default-ref>:./<path>"`): usually the copy is new, so the falling-back array stands. Only refine, amend and annotate runs flip it.

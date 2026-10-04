# Multi-component PRDs: one target per Epic, the contract in the ARD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a PRD that changes more than one component — two repositories, or two modules of one — split into one Epic per component, fix the interfaces between them in the PRD-level ARD's `## Contracts`, and check that the Epics fit together in `/epics`, `/implement` and `/ready`, in this repository, the internal edition and the Copilot edition.

**Architecture:**
- **One new shared reference** in this edition, `workflows-core:components`, owns:
  - the component definition;
  - module enumeration;
  - the multi-component test;
  - the ride-along rule;
  - the read-only check `multi-component-prereqs`.
- **The ARD carries the contract.** Its format gains `components:` and `## Contracts`. `/create-ard` authors both, `ard-reviewer` and pre-lint check them, and `ard-resolution` returns them to every consumer.
- **The commands use the contract.**
  - `/epics` and its two agents give each Epic one `target:` and a `## Contract`.
  - `/specify` and `/design` narrow to the target.
  - `/ready` and `/implement` run `multi-component-prereqs`.
- **How edits are applied.** Every edit is applied with `wsub.py` (a whitespace-insensitive replace) from the edit files in Appendix B, in eight groups, one per task.
  - The whole round was dry-run against this tree and applied to a trial copy before this plan was written: `check.py` passed 75 of 75 and the gate chain gave `EXIT=0` with 0 warnings.
- **The two ports are written after this edition's review converges** (Tasks 11–12), from its reviewed text through a dialect table.
  - The ports' `/epics`, `/design` and `/create-ard` differ in structure: a VI rather than a PRD, Epic files that are bound for a tracker, and no flat-spec precedence in `/design`. So their anchors have to be found in those trees.
  - Writing their edits now would also mean writing them twice, once here and again after review.

**Tech Stack:** Markdown prose executed by agents; git; bash; python3 (helpers, gates); node (mermaid gate).

**Spec:** `docs/superpowers/specs/2026-10-04-multi-component-epics-design.md`, including § *Amended during planning*.

## Global Constraints

- **Never name the internal edition in this repository.** Check 19 rejects, anywhere in the work tree, the pattern `EDITION_FORBIDDEN_B64` decodes to in `scripts/check-docs.sh`. Write "the internal edition" and `$IE`. Never write the Copilot edition's second remote's name here.
- **Prose is executed.** Every sentence added must be true of what the run does; a false one is a defect.
- **Apply edits only with `wsub.py`, from Appendix B's files.** A fix found later is a new edit block, or a hand edit recorded as a `Ruling:` in the ledger. `wsub.py` aborts with nothing written when a block's match count is wrong. That means stop and look, never loosen the block.
- **Copilot dialect.** In `$CE`:
  - skills are named `epics:`, `create-ard:`, `specify:`, `design:`, `ready:`, `implement:`;
  - shared references are `~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/<name>.md`;
  - `${CLAUDE_PLUGIN_ROOT}` never appears;
  - every `choices` array ends with `"Other… (describe)"`;
  - each `.github/instructions/*.md` stays under 20,000 characters. Both are at 19,998, and `check.py ce` asserts the limit.
- **Size limits in this repository.**
  - `CLAUDE.md` must stay under 36,000 characters. It is 35,990 now and 35,984 after this round.
  - `.claude/rules/docs-workflows.md` (19,967) and `.claude/rules/gates.md` (19,988) are not touched.
- **Git discipline in this repository.**
  - Never `git checkout` or `git switch` in `/workspace/ai-workflows`; work in `$AW`.
  - Run `git branch --show-current` immediately before every commit.
  - Never use a bare `git stash`.
  - Stage `.claude/rules/*` with `git add -f`.
- **Commit trailers:** `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01Au7DfL9asXxZqvnrH2znsY`.
- **Do not edit** `references/specification-format.md` (frozen) or `~/.claude/claude-config/` (retired).
- **Every `CHANGELOG.md` section is dated** before it reaches `main` (check 18). `release.py <ed> <root> <YYYY-MM-DD>` re-dates the sections to the landing day.
- **Zero known bugs, with the review budget the user agreed (spec D27).**
  - This edition is reviewed until a round returns zero findings.
  - As soon as two consecutive rounds turn up new edge cases only in pre-existing behaviour, put the "fix this round, file the area" choice to the user that same round.
  - Each port gets one review round, with its findings fixed and no re-review.

## Review Focus

These five input classes are ones no check exercises, because `check.py` tests text presence only. Each is pinned by a trace step in the task that owns its text.

1. **A PRD split under the `/epics` override, then designed and implemented**: no ARD, two Epics with different `target:` values.
   - `multi-component-test` returns `true` from the `epic-targets` source.
   - `/design <PRD>` goes to the Epic picker.
   - `/implement` Phase 1 asks about the missing `ard_contract` and `prd_spec`.
   - `/ready` caps the verdict below *Ready for Implementation*.
   - Nothing checks a target against a set the ARD never supplied.
   - Pinned by Task 7 Step 5's trace.
2. **A one-component PRD with code scan on and no ARD** (spec example C).
   - Phase 5.5 proposes one component and asks nothing.
   - Every Epic gets `target:`, no stop fires, and `/design <PRD>` keeps the flat-spec precedence.
   - Pinned by Task 3 Step 5's trace C.
3. **A change in a deploy component of another repository** (a separate gitops repository).
   - `epic-writer` splits it into its own Epic.
   - `epic-reviewer` raises a BLOCKER on an `Also touches:` line that names it.
   - Pinned by Task 3 Step 5's trace G.
4. **`/implement` run in a repository with no `origin`.**
   - `target_repo_matches: unknown`, one line, no question; the prerequisite rows are still checked.
   - Pinned by Task 7 Step 5's trace.
5. **An ARD with two components and no interface between them**: `bookstore:orders` plus `bookstore:k8s`, a ride-along only.
   - Pre-lint requires `## Contracts` with its three subsections. The table may be empty.
   - `ard-reviewer` finds no crossing capability.
   - `contracts` is not null, so `ard_contract` is `present` and `/epics` Phase 2.7 says nothing.
   - Pinned by Task 2 Step 5's trace.

---

### Task 0: Variables, helpers, workspace

**Files:**
- Create (scratch, never committed): `$S/{wsub.py,check.py,apply.sh,gates.sh,release.py}`, `$S/files/components.md`, `$S/edits/*`, `$S/cl/*`.

**Interfaces:**
- Produces:
  - the variables `$AW`, `$IE`, `$CE`, `$S` and `$PLAN`;
  - `wsub.py TARGET EDITFILE [--dry]`: exits 1, with nothing written, on any count mismatch;
  - `check.py aw|ie|ce ROOT`: prints each failing check as `FAIL …`, then `<ed>: N passed, M failed`;
  - `apply.sh aw ROOT GROUP [--dry]`, where GROUP is `core | ard | epics | specify | design | ready | implement | tiers | all`;
  - `gates.sh aw|ie|ce ROOT`: the edition's CI chain as one `&&` chain;
  - `release.py aw|ie|ce ROOT [DATE]`.

- [ ] **Step 1: Set the variables.** Every later task assumes them.

```bash
AW=/workspace/.worktrees/ai-workflows-multi-component   # this repository's worktree, branch iv-gu/multi-component-epics
IE=<the internal edition's checkout root under /workspace>  # not written here: check 19
CE=/workspace/ihudak-copilot-plugins
S=<a scratch directory outside every repository>
PLAN=$AW/docs/superpowers/plans/2026-10-04-multi-component-epics.md
```

- [ ] **Step 2: Extract the helpers, the new file, the edit files and the changelog sections from this plan** (Appendices A–D).

```bash
mkdir -p "$S/edits" "$S/cl" "$S/files" && python3 - "$PLAN" "$S" <<'EOF'
import os, re, sys
plan, S = sys.argv[1], sys.argv[2]
n = 0
for m in re.finditer(r'^#### `(scripts|edits|cl|files)/([^`]+)`\n\n`````[a-z]*\n(.*?)\n`````$', open(plan).read(), re.S | re.M):
    d = S if m.group(1) == 'scripts' else os.path.join(S, m.group(1))
    open(os.path.join(d, m.group(2)), 'w').write(m.group(3) + '\n'); n += 1
print(n, 'files')
EOF
chmod +x "$S"/*.sh "$S"/*.py
```
Expected: `40 files`.

- [ ] **Step 3: Confirm the tree, then dry-run every group.**

```bash
cd "$AW" && test "$(git branch --show-current)" = iv-gu/multi-component-epics && test -z "$(git status --porcelain)" && echo CLEAN
"$S/apply.sh" aw "$AW" all --dry | grep -c '^checked'
```
Expected: `CLEAN`, then `32` (every file `checked`, none `ABORT`).

- [ ] **Step 4: RED.**

```bash
python3 "$S/check.py" aw "$AW" | tail -1
```
Expected: `aw: 0 passed, 75 failed`. Each task below is measured by `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'`.

- [ ] **Step 5: Open the ledger.** Run the executing skill's `sdd-workspace` script on `$PLAN`, and write the ledger's first line, `# SDD ledger — plan: <PLAN path>`.

---

### Task 1: The `components` reference and the shared references (`core`)

**Files:**
- Create: `plugins/workflows-core/references/components.md`.
- Modify:
  - `plugins/workflows-core/references/{ard-resolution,pre-lint,grilling-technique,epic-picker}.md`;
  - `plugins/workflows-core/docs/reference/references.md`.

**Interfaces:**
- Produces (every later task cites these):
  - **`components.md`** (`Skill(skill: "workflows-core:reference", args: "components")`), with entry points `enumerate-components` (§2), `component-of` (§1.1), `multi-component-test` (§3, returning `{multi_component, set, set_source}`) and `multi-component-prereqs` (§6, returning `multi_component`, `prerequisites[]`, `target`, `targets[]` and `coverage_gaps[]`).
  - **`ard-resolution`**'s new `components` field (`[{id, kind, paths}]`) and `contracts` field (`{rows: [{ad, producer, consumers, kind, status, artifact}], landing_order}`, or null).

- [ ] **Step 1: RED.** `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `75`.
- [ ] **Step 2: Dry-run.** `"$S/apply.sh" aw "$AW" core --dry | grep -c '^checked'` → `6`.
- [ ] **Step 3: Apply.** `"$S/apply.sh" aw "$AW" core | grep -c '^applied\|^created'` → `6`.
- [ ] **Step 4: GREEN for this task.** `python3 "$S/check.py" aw "$AW" | grep -c '^FAIL'` → `60`.
- [ ] **Step 5: Read `components.md` end to end against spec D1–D5 and D21.**
  - §3's three sources are in the order D3 states, and only `ard` makes a target checkable *in* the set.
  - §6 never prompts and never stops.
  - Its presence test uses `phase-handoff` §3.2's primitives, never `require-on-main`.
  - "The earliest missing command" names the ladder order D14 and D22 recommend.
  - Ledger any deviation as a `Ruling:`.
- [ ] **Step 6: Commit.** Verify the branch, then `git -C "$AW" add plugins/workflows-core` and commit with `feat(workflows-core): the components reference; ard-resolution returns components and contracts` and the trailers.

### Task 2: The ARD (`ard`)

**Files:**
- Modify:
  - `plugins/product-workflows/references/ard-format.md`;
  - `plugins/product-workflows/commands/create-ard.md`;
  - `plugins/product-workflows/agents/ard-reviewer.md`;
  - `plugins/product-workflows/docs/commands/create-ard.md`;
  - `plugins/product-workflows/docs/reference/references.md`.

**Interfaces:**
- Consumes: Task 1's `components.md` §1, §2 and §5, and `ard-resolution`'s `contracts`.
- Produces:
  - the ARD's `components:` frontmatter;
  - the `## Contracts` section: interface table `| AD | Producer | Consumers | Kind | Status | Artifact |`, then `### Schema ownership`, `### Versioning and compatibility` and `### Landing order`.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `60`.
- [ ] **Step 2: Dry-run.** `apply.sh aw "$AW" ard --dry | grep -c '^checked'` → `5`.
- [ ] **Step 3: Apply.** `apply.sh aw "$AW" ard` → `5` applied.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `48`.
- [ ] **Step 5: Trace Review Focus 5**, an ARD with `components:` of `bookstore:orders` and `bookstore:k8s` (`kind: deploy`) and no crossing capability, through `/create-ard` Phase 4, pre-lint's ARD block, `ard-reviewer`'s *Contract completeness*, and `ard-resolution` step 4. Ledger it as `Task 2: trace ARD-2-no-interface: <outcome at each>`.
  - Expected:
    - the grill writes `## Contracts` with an empty table and the three subsections;
    - pre-lint is satisfied;
    - the reviewer finds no crossing capability;
    - `contracts` is `{rows: [], landing_order: […]}`, not null.
- [ ] **Step 6: Read-through.** Read `/create-ard` Phase 3 → 4 → 7 as one run at PRD level and at Epic level.
  - The Epic level writes no `components:`.
  - The Phase 7 swap applies only where this run wrote two or more components and the PRD has 0 Epics.
- [ ] **Step 7: Commit.** Use `feat(product-workflows): the ARD carries components and a contract section`.

### Task 3: Epics (`epics`)

**Files:**
- Modify:
  - `plugins/product-workflows/agents/epic-writer.md`;
  - `plugins/product-workflows/agents/epic-reviewer.md`;
  - `plugins/product-workflows/commands/epics.md`;
  - `plugins/product-workflows/docs/commands/epics.md`.

**Interfaces:**
- Consumes: `components.md` §3, §4 and §6 (scope `epics`), and `ard-resolution`'s `components` and `contracts`.
- Produces:
  - the Epic's frontmatter `target: <component id>`;
  - its `## Contract` lines `- Produces: [AD#N] — …` and `- Consumes: [AD#N] — …`;
  - `- Also touches: <component id> — <why>` under `### In scope`.
  - `/ready` and `/implement` read all three through §6.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `48`.
- [ ] **Step 2: Dry-run.** `apply.sh … epics --dry` → `4`.
- [ ] **Step 3: Apply.** `apply.sh … epics` → `4`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `35`.
- [ ] **Step 5: Trace through `/epics` as edited**, citing the sentence that decides each step. Ledger each as `Task 3: trace <C|G|B>: <outcome>`.
  - **Trace C** (Review Focus 2): a bookstore PRD in `clients`, no ARD, code scan on. Phase 5.5 proposes one component and asks nothing, Phase 2.7 never runs, and every Epic carries `target: bookstore:clients` with no `## Contract`.
  - **Trace G** (Review Focus 3): an ARD whose components are `orders-svc` and `gitops:apps/orders` (`kind: deploy`, another repository). `epic-writer`'s ride-along rule makes `gitops` its own Epic, and `epic-reviewer` raises a BLOCKER on an `Also touches: gitops:apps/orders` line.
  - **Trace B** (spec example B): a contract Epic on `bookstore:common` comes first; `carts` consumes `[AD#3]` with a stub and depends on the `orders` Epic; `k8s` rides along.
- [ ] **Step 6: Read-through.** Read the phases `/epics` now runs in order: 2.5 → 2.6 → 2.7 → … → 5 → 5.5 → 6 → 7 → 9.
  - Phase 2.7 runs once at most per run: at 2.7 where the ARD supplied the set, otherwise from 5.5.
  - The *Split without* override reaches Phase 9's `### Targets`.
  - The invariants still describe the run.
  - The docs page's count reads 22 `## Phase` headings: `grep -c '^## Phase' plugins/product-workflows/commands/epics.md` → `22`.
- [ ] **Step 7: Commit.** Use `feat(product-workflows): one target per Epic, and the contract each Epic produces or consumes`.

### Task 4: `/specify` (`specify`)

**Files:** `plugins/product-workflows/commands/specify.md`, `plugins/product-workflows/docs/commands/specify.md`.

**Interfaces:** Consumes the Epic's `target:` (Task 3), and `components` and `contracts` (Task 1).

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `35`.
- [ ] **Step 2: Dry-run.** `apply.sh … specify --dry` → `2`.
- [ ] **Step 3: Apply.** `apply.sh … specify` → `2`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `32`.
- [ ] **Step 5: Read-through.** On an Epic with a target, Phase 3's narrowing reaches step 4's soft gate unchanged: an unmounted target repository is still a feasibility open question, never a stop.
- [ ] **Step 6: Commit.** Use `feat(product-workflows): /specify narrows an Epic to its target`.

### Task 5: `/design` and the readiness rubric (`design`)

**Files:**
- Modify:
  - `plugins/dev-workflows/references/{design-format,workflow-states}.md`;
  - `plugins/dev-workflows/agents/design-reviewer.md`;
  - `plugins/dev-workflows/commands/design.md`;
  - `plugins/dev-workflows/docs/commands/design.md`;
  - `plugins/dev-workflows/docs/reference/references.md`.

**Interfaces:**
- Consumes: `multi-component-test` (§3), and the Epic's `target:`.
- Produces:
  - `design.md`'s `- **Target**:` header line;
  - the `- Target span: <component> — <why>` risk line;
  - `workflow-states.md`'s multi-component clause of *Ready for Implementation*, which Task 6 reads.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `32`.
- [ ] **Step 2: Dry-run.** `apply.sh … design --dry` → `6`.
- [ ] **Step 3: Apply.** `apply.sh … design` → `6`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `20`.
- [ ] **Step 5: Read-through.** Read Phase 0 step 4 from its first bullet. The multi-component bullet runs before the flat-spec bullet, and its *Design across components anyway* reaches the Final report's new clause. The rewritten *taken first* sentence is now true of the bullet order.
- [ ] **Step 6: Commit.** Use `feat(dev-workflows): /design keeps an Epic in its target; a multi-component PRD's flat spec is a requirements source`.

### Task 6: `/ready` (`ready`)

**Files:**
- Modify:
  - `plugins/dev-workflows/agents/readiness-reviewer.md`;
  - `plugins/dev-workflows/commands/ready.md`;
  - `plugins/dev-workflows/docs/commands/ready.md`.

**Interfaces:**
- Consumes: `multi-component-prereqs` at `ready` scope (`targets[]`, `coverage_gaps[]`), and Task 5's rubric clause.
- Produces: Phase 3(d)'s Targets and Contract coverage tables, passed to `readiness-reviewer` as `multi_component`.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `20`.
- [ ] **Step 2: Dry-run.** `apply.sh … ready --dry` → `3`.
- [ ] **Step 3: Apply.** `apply.sh … ready` → `3`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `13`.
- [ ] **Step 5: Read-through.** On a multi-component PRD, check each of these:
  - Phase 1 step 2 locates no slice `design.md`.
  - Phase 2 carries no slice row.
  - Phase 3(0) derives the PRD's phase from the multi-component clause.
  - Phase 3(b) marks a missing `## Contracts` ❌.
  - Phase 3(d) does not repeat that ❌.
  - The report's two new sections are omitted where 3(d) recorded N/A.
- [ ] **Step 6: Commit.** Use `feat(dev-workflows): /ready checks targets and cross-Epic contract coverage`.

### Task 7: `/implement` (`implement`)

**Files:** `plugins/dev-workflows/commands/implement.md`, `plugins/dev-workflows/docs/commands/implement.md`.

**Interfaces:**
- Consumes: `multi-component-test`, and `multi-component-prereqs` at `implement` scope (`prerequisites[]`, `target`, `coverage_gaps[]`).
- Produces: the overridden gap, carried in `body_facts` for `code-handoff` §2.7's *Merge danger*.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `13`.
- [ ] **Step 2: Dry-run.** `apply.sh … implement --dry` → `2`.
- [ ] **Step 3: Apply.** `apply.sh … implement` → `2`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `9`.
- [ ] **Step 5: Trace Review Focus 1 and 4** through `/implement` as edited, and ledger each.
  - **Review Focus 1:** with no ARD and two Epic targets, the picker withholds the slice, and Phase 1 asks once, naming `ard_contract` and `prd_spec`. On *Implement without them*, both reach `### Assumptions & limitations` and `body_facts`.
  - **Review Focus 4:** with no `origin`, one line prints and nothing is asked about the target.
- [ ] **Step 6: Read-through.** Verify that nothing else in `/implement` changed:
  - `git -C "$AW" diff --stat -- plugins/dev-workflows/commands/implement.md` shows three hunks.
  - Phase 3A/3B, Phase 4.6 and the invariants are untouched apart from `body_facts`' one clause.
- [ ] **Step 7: Commit.** Use `feat(dev-workflows): /implement checks an Epic's target, prerequisites and contract coverage on a multi-component PRD`.

### Task 8: The instruction tiers (`tiers`)

**Files:**
- `.claude/rules/{product-workflows,dev-workflows,workflows-core}.md`, staged with `git add -f`;
- `CLAUDE.md`.

- [ ] **Step 1: RED.** `grep -c '^FAIL'` → `9`.
- [ ] **Step 2: Dry-run.** `apply.sh … tiers --dry` → `4`.
- [ ] **Step 3: Apply.** `apply.sh … tiers` → `4`.
- [ ] **Step 4: GREEN for this task.** `grep -c '^FAIL'` → `3`: the three changelog sections Task 9 writes.
- [ ] **Step 5: Re-derive every number these files state that this round touches**, by the command each one cites.
  - `find plugins/workflows-core/references -type f | wc -l` → `31`.
  - `python3 -c "print(len(open('CLAUDE.md').read()))"` → `35984`.
  - Each rules file stays under 20,000 characters.
- [ ] **Step 6: Commit.** Use `docs(rules): the components authority, the multi-component invariants and map lines`.

### Task 9: Release this edition, gates, and the worked examples

- [ ] **Step 1: Bump and write the changelogs.** Run `python3 "$S/release.py" aw "$AW" <landing day, YYYY-MM-DD>`.
  - Expected output: `dev-workflows 4.8.0 4.8.0`, `workflows-core 1.12.0 1.12.0`, `product-workflows 3.13.0 3.13.0`.
- [ ] **Step 2: GREEN.** `python3 "$S/check.py" aw "$AW" | tail -1` → `aw: 75 passed, 0 failed`.
- [ ] **Step 3: Check each changelog entry against the diff.** Read `git -C "$AW" diff main...HEAD --stat` beside the three new sections. Every claim in them names a change the diff makes.
- [ ] **Step 4: Gates.** Run `"$S/gates.sh" aw "$AW"; echo "EXIT=$?"`, which must print `EXIT=0`. Allow a timeout of at least 300 s.
  - `grep -E '[1-9][0-9]* warning' <output>` must return nothing.
- [ ] **Step 5: Trace the spec's three worked examples (A, B, C)** through every command as edited, phase by phase. Ledger each as `Task 9: trace example <A|B|C>: <outcome per command>`. A phase whose text does not expect the state is a finding for Task 10's first round.
- [ ] **Step 6: Commit.** Commit `.claude-plugin/marketplace.json`, the three `plugin.json` files and the three `CHANGELOG.md` files, with `chore(release): workflows-core 1.12.0, product-workflows 3.13.0, dev-workflows 4.8.0`. Verify the branch first.

### Task 10: Whole-branch review of this edition

- [ ] **Step 1: Dispatch a fresh reviewer** (Opus, general-purpose, in the background). Give it:
  - the spec path, including § *Amended during planning*;
  - the plan path;
  - `git -C "$AW" diff main...HEAD`;
  - the ledger's `Ruling:` lines and traces;
  - this brief: *"Review this branch as a whole. The prose is executed by agents in order, so a false or ambiguous sentence is a defect. Check every changed sentence against what the run does, every pointer (`this`, `it`, `above`, an ordinal, a section number) against what it now points at, each claim whose extent changed against every copy of it (changelog, docs page, rules summary), and the spec's decisions against the text. Trace spec examples A, B and C through the commands. Report each finding with file:line, severity, and the failure it causes; list what you declined to judge."*
- [ ] **Step 2: Triage each finding** at the location it names.
  - Fix every confirmed one, minors and nits included, with an edit block or a ledgered hand edit.
  - Record any dismissal with a reason that disposes of that finding's own claim.
- [ ] **Step 3: Re-read each fix where it lands**, then re-run `check.py` (`aw: 75 passed, 0 failed`) and the gate chain (`EXIT=0`).
  - Commit the wave as `fix: review round N — …`, verifying the branch first.
  - Ledger the round's finding count, and how many of the findings sit in pre-existing behaviour.
- [ ] **Step 4: Repeat Steps 1–3 until a round returns zero findings.**
  - **Once two consecutive rounds' findings are all new edge cases in pre-existing behaviour, stop and ask the user** that same round: `choices: ["Fix this round, then file the area in NEXT.md (Recommended)", "Keep reviewing to zero"]`.
  - Findings in this round's own decisions are always fixed.

### Task 11: Port to the internal edition

**Files:**
- `$IE/plugins/dev-workflows/references/{components (new),ard-resolution,pre-lint,grilling-technique,ard-format,design-format,workflow-states,epic-picker (if present)}.md`;
- `$IE/plugins/dev-workflows/commands/{create-ard,epics,specify,design,ready,implement}.md`;
- `$IE/plugins/dev-workflows/agents/{ard-reviewer,epic-writer,epic-reviewer,design-reviewer,readiness-reviewer}.md`;
- `$IE/plugins/dev-workflows/docs/commands/{create-ard,epics,specify,design,ready,implement}.md`;
- `$IE/plugins/dev-workflows/docs/reference/references.md`;
- `$IE/.claude/rules/dev-workflows-*.md` where a map line or invariant names these commands;
- `$IE/plugins/dev-workflows/{.claude-plugin/plugin.json,CHANGELOG.md}` and `$IE/.claude-plugin/marketplace.json`.

**The dialect table** (this edition → the internal edition):

| This edition | The internal edition |
|---|---|
| PRD, `<PRD>`, PRD-level | VI, `<VI>`, VI-level |
| `workflows-core:components`, `Skill(… args: "components …")` | `${CLAUDE_PLUGIN_ROOT}/references/components.md` |
| `/product-workflows:<cmd>`, `/dev-workflows:<cmd>` | `/dev-workflows:<cmd>` |
| Epic frontmatter `target:` | a `**Target:** <component id>` line under the H1, beside `**Team:**` |
| `epic.md` files directly under the PRD folder | the Epic definition files that edition's `/epics` writes and reads (its `output_dir` and its import) |

- [ ] **Step 1: Branch.** `test -z "$(git -C "$IE" status --porcelain)" && git -C "$IE" switch -c iv-gu/multi-component-epics`.
- [ ] **Step 2: RED.** `python3 "$S/check.py" ie "$IE" | tail -1` → `ie: 0 passed, 61 failed`.
- [ ] **Step 3: Write `$S/edits/ie-*.txt`, one per counterpart file, from this edition's reviewed edit files.**
  - Each block's NEW is this edition's NEW put through the dialect table, anchored at the counterpart passage.
  - Find each anchor by the subject of this edition's OLD, never by its wording.
  - Where the internal edition's passage differs in structure, adapt the step to that structure and ledger a `Ruling:`. Known cases: its `/epics` reads Epic definitions out of an import and an output directory, and its `/design` may have no flat-spec precedence.
  - Write `components.md` from this edition's file the same way.
  - Add an `ie)` branch to `apply.sh` listing them, then `apply.sh ie "$IE" all --dry` → every file `checked`.
- [ ] **Step 4: Apply, then GREEN before the release.** `check.py ie` → `ie: 60 passed, 1 failed`; the one is the changelog section.
- [ ] **Step 5: Sweep by subject** over `$IE`'s `plugins/`, `README.md`, `CLAUDE.md` and `.claude/rules/`:
  - *theme → repo*;
  - every statement that a flat VI-level spec is designed or implemented as one unit;
  - *VI-level `/specify` remains optional*;
  - the no-regression rule's *MUST behave exactly as it did*.
  - Read each hit in place, and rewrite it where the change falsifies it.
- [ ] **Step 6: Release.** Write `$S/cl/ie-dev-workflows.md` (`## [2.69.0] — <landing day>`) from this edition's three sections in that edition's vocabulary. Then:
  - `python3 "$S/release.py" ie "$IE"` → `dev-workflows 2.69.0 2.69.0`;
  - `check.py ie` → `ie: 61 passed, 0 failed`;
  - `"$S/gates.sh" ie "$IE"; echo "EXIT=$?"` → `EXIT=0`.
- [ ] **Step 7: Commit.** Verify the branch, then commit with `feat(dev-workflows): multi-component VIs — one target per Epic, the contract in the ARD (dev-workflows 2.69.0)` and the trailers.
- [ ] **Step 8: One review round** (spec D27), against `git -C "$IE" diff main...HEAD`, with Task 10's brief plus: *"Compare each changed passage with this repository's counterpart; a difference beyond dialect is a finding unless the ledger records a ruling for it."*
  - Fix every finding without a re-review.
  - Re-run `check.py ie` and the gate chain.
  - Commit as `fix: review — …`.

### Task 12: Port to the Copilot edition

**Files:**
- `$CE/dev-workflows/skills/_shared/{components (new),ard-resolution,pre-lint,grilling-technique,ard-format,design-format,workflow-states,epic-picker (if present)}.md`;
- `$CE/dev-workflows/skills/{create-ard,epics,specify,design,ready,implement}/SKILL.md`;
- `$CE/dev-workflows/agents/{ard-reviewer,epic-writer,epic-reviewer,design-reviewer,readiness-reviewer}.md`;
- `$CE/dev-workflows/docs/skills/{create-ard,epics,specify,design,ready,implement}.md`;
- `$CE/dev-workflows/docs/reference/references.md`;
- `$CE/dev-workflows/{.plugin/plugin.json,CHANGELOG.md}` and `$CE/.github/plugin/marketplace.json`.

**The dialect table**, the internal edition's plus:

| This edition | The Copilot edition |
|---|---|
| `/epics`, `/create-ard`, `/specify`, `/design`, `/ready`, `/implement` | `epics:`, `create-ard:`, `specify:`, `design:`, `ready:`, `implement:` |
| `${CLAUDE_PLUGIN_ROOT}/references/<name>.md`, `workflows-core:<name>` | `~/.copilot/installed-plugins/ihudak-copilot-plugins/dev-workflows/skills/_shared/<name>.md` |
| a `choices` array | the same array ending with `"Other… (describe)"` |
| Read | view |

- [ ] **Step 1: Branch.** Run Task 11 Step 1 on `$CE`.
- [ ] **Step 2: RED.** `check.py ce "$CE" | tail -1` → `ce: 2 passed, 61 failed`. The two that pass are the instruction-file limits.
- [ ] **Step 3: Write `$S/edits/ce-*.txt` and `_shared/components.md`** from the internal edition's ported text, which already carries the VI vocabulary, through the table above.
  - Add a `ce)` branch to `apply.sh`.
  - Dry-run every file.
  - Leave the two `.github/instructions` files untouched unless an entry there is unavoidable. If it is, pay for it inside the same file and keep it under 20,000 characters.
- [ ] **Step 4: Apply, then GREEN before the release.** `check.py ce` → `ce: 62 passed, 1 failed`.
- [ ] **Step 5: Dialect sweep.** Run `grep -n -E '/epics|/create-ard|/specify|/design|/ready|/implement|CLAUDE_PLUGIN_ROOT|workflows-core:' $(git -C "$CE" diff --name-only | grep -v CHANGELOG | sed "s#^#$CE/#")`. It must return nothing on a changed line that a Copilot reader would act on wrongly. Then run the subject sweep from Task 11 Step 5.
- [ ] **Step 6: Release.** Write `$S/cl/ce-dev-workflows.md` (`## [2.38.0] — <landing day>`). Then:
  - `release.py ce "$CE"` → `dev-workflows 2.38.0 2.38.0`;
  - `check.py ce` → `ce: 63 passed, 0 failed`;
  - `gates.sh ce "$CE"` → `EXIT=0`.
- [ ] **Step 7: Commit.** Run Task 11 Step 7 with `(dev-workflows 2.38.0)`.
- [ ] **Step 8: One review round** as in Task 11 Step 8. The dialect is `epics:`-style names, `_shared/` paths, and the trailing `"Other… (describe)"` arm.

### Task 13: Record, merge, push, clean up

- [ ] **Step 1: Merge and push the other two editions.** In each, from its own checkout:
  - `git switch main && git merge --no-ff iv-gu/multi-component-epics -m "Merge iv-gu/multi-component-epics: multi-component VIs — one target per Epic, the contract in the ARD (dev-workflows <version>)"`;
  - push to every remote `git remote` lists (the internal edition's protected-branch bypass notice is expected);
  - `git branch -d iv-gu/multi-component-epics`;
  - record each merge commit.
- [ ] **Step 2: Write the record** in `$AW/docs/superpowers/harvest/NEXT.md`, never naming the internal edition:
  - mark the *Multi-repository features* follow-up as shipped, with each edition's merge commit and version;
  - the review-round counts;
  - the findings worth keeping;
  - any area filed under Task 10 Step 4.
- [ ] **Step 3: Commit, gate, merge, push.**
  - Commit the record as `docs(harvest): record the multi-component round in three editions`.
  - Re-run `gates.sh aw "$AW"` → `EXIT=0` and `check.py aw` → `aw: 75 passed, 0 failed`.
  - From `/workspace/ai-workflows`, which stands on `main`: `git pull --ff-only && git merge --no-ff iv-gu/multi-component-epics`, verifying the branch first.
  - Push, then `gh run watch` the CI run to success.
- [ ] **Step 4: Clean up.**
  - Copy the ledger out first.
  - Run `git -C /workspace/ai-workflows worktree remove --force "$AW" && git -C /workspace/ai-workflows branch -d iv-gu/multi-component-epics`.
  - Confirm each repository is on `main`, clean, with `main` equal to every remote's `main`, and has no branch left from this round.
- [ ] **Step 5: The final message.**
  - **"Rulings I made"**, grouped, with the full list saved to a file.
  - **"Deferred minors".**
  - **The update commands:**
    - `claude plugin update workflows-core@shipwright`
    - `claude plugin update product-workflows@shipwright`
    - `claude plugin update dev-workflows@shipwright`
    - the internal edition's `claude plugin update dev-workflows@<its marketplace>`
    - then a restart
    - `copilot plugin update dev-workflows@ihudak-copilot-plugins`

## Appendix A — helper scripts

Extracted by Task 0 Step 2 into `$S`.

#### `scripts/wsub.py`

`````python
#!/usr/bin/env python3
"""Apply whitespace-insensitive replacements to one file.

usage: wsub.py TARGET EDITFILE [--dry]

EDITFILE holds one or more blocks:
    <<<<<<< OLD <n>
    old text
    =======
    new text
    >>>>>>> NEW
<n> is how many times OLD must match TARGET. A run of whitespace in OLD matches any run of
whitespace in TARGET, so a passage wrapped differently in another edition still matches;
NEW is written with its outer whitespace stripped (the file's own indentation before the match
stays). A count mismatch on any block aborts before anything is written.
"""
import re, sys

target, editfile = sys.argv[1], sys.argv[2]
dry = '--dry' in sys.argv[3:]
blocks, cur, mode = [], None, None
for line in open(editfile).read().split('\n'):
    m = re.fullmatch(r'<<<<<<< OLD (\d+)', line)
    if m:
        cur, mode = {'n': int(m.group(1)), 'old': [], 'new': []}, 'old'
        continue
    if cur is not None and line == '=======':
        mode = 'new'
        continue
    if cur is not None and line == '>>>>>>> NEW':
        blocks.append(cur)
        cur, mode = None, None
        continue
    if mode:
        cur[mode].append(line)
if cur is not None or not blocks:
    sys.exit(f'ABORT {editfile}: unterminated or empty edit file')
text = open(target).read()
for b in blocks:
    old, new = '\n'.join(b['old']), '\n'.join(b['new']).strip()  # the match spans no outer whitespace, so NEW carries none
    pat = re.compile(r'\s+'.join(map(re.escape, old.split())))
    found = len(pat.findall(text))
    if found != b['n']:
        sys.exit(f"ABORT {target}: expected {b['n']} match(es), found {found}, OLD begins {old[:80]!r}")
    text = pat.sub(lambda _m: new, text)
if not dry:
    open(target, 'w').write(text)
print(f"{'checked' if dry else 'applied'} {len(blocks)} block(s): {target}")
`````

#### `scripts/check.py`

`````python
#!/usr/bin/env python3
"""check.py EDITION ROOT — multi-component round: each new marker present at its site, each retired string at 0,
counted wrap-insensitively (whitespace collapsed on both sides); the Copilot instruction files under 20,000 characters."""
import re, sys
ed, root = sys.argv[1], sys.argv[2]
def ports(base, cmd, shared, docs):
    return dict(COMP=f'{shared}/components.md', ARDRES=f'{shared}/ard-resolution.md', PRELINT=f'{shared}/pre-lint.md',
                GRILL=f'{shared}/grilling-technique.md', ARDFMT=f'{shared}/ard-format.md', DFMT=f'{shared}/design-format.md',
                WS=f'{shared}/workflow-states.md', CARD=cmd('create-ard'), EPICS=cmd('epics'), SPEC=cmd('specify'),
                DESIGN=cmd('design'), READY=cmd('ready'), IMPL=cmd('implement'),
                EW=f'{base}/agents/epic-writer.md', ER=f'{base}/agents/epic-reviewer.md', ARDREV=f'{base}/agents/ard-reviewer.md',
                DREV=f'{base}/agents/design-reviewer.md', RREV=f'{base}/agents/readiness-reviewer.md',
                REFS=f'{base}/docs/reference/references.md', CL=f'{base}/CHANGELOG.md',
                **{f'DOC_{n}': f'{base}/docs/{docs}/{n}.md' for n in ('create-ard', 'epics', 'specify', 'design', 'ready', 'implement')})
if ed == 'aw':
    W, PW, DW = 'plugins/workflows-core', 'plugins/product-workflows', 'plugins/dev-workflows'
    P = dict(COMP=f'{W}/references/components.md', ARDRES=f'{W}/references/ard-resolution.md', PRELINT=f'{W}/references/pre-lint.md',
             GRILL=f'{W}/references/grilling-technique.md', ARDFMT=f'{PW}/references/ard-format.md', DFMT=f'{DW}/references/design-format.md',
             WS=f'{DW}/references/workflow-states.md', CARD=f'{PW}/commands/create-ard.md', EPICS=f'{PW}/commands/epics.md',
             SPEC=f'{PW}/commands/specify.md', DESIGN=f'{DW}/commands/design.md', READY=f'{DW}/commands/ready.md', IMPL=f'{DW}/commands/implement.md',
             EW=f'{PW}/agents/epic-writer.md', ER=f'{PW}/agents/epic-reviewer.md', ARDREV=f'{PW}/agents/ard-reviewer.md',
             DREV=f'{DW}/agents/design-reviewer.md', RREV=f'{DW}/agents/readiness-reviewer.md',
             REFS=f'{W}/docs/reference/references.md', PWREFS=f'{PW}/docs/reference/references.md', DWREFS=f'{DW}/docs/reference/references.md',
             CL=f'{W}/CHANGELOG.md', PWCL=f'{PW}/CHANGELOG.md', DWCL=f'{DW}/CHANGELOG.md',
             CLAUDE='CLAUDE.md', PICKER=f'{W}/references/epic-picker.md',
             RPW='.claude/rules/product-workflows.md', RDW='.claude/rules/dev-workflows.md', RWC='.claude/rules/workflows-core.md',
             **{f'DOC_{n}': f'{PW if n in ("create-ard", "epics", "specify") else DW}/docs/commands/{n}.md'
                for n in ('create-ard', 'epics', 'specify', 'design', 'ready', 'implement')})
elif ed == 'ie':
    B = 'plugins/dev-workflows'
    P = ports(B, lambda n: f'{B}/commands/{n}.md', f'{B}/references', 'commands')
else:
    B = 'dev-workflows'
    P = ports(B, lambda n: f'{B}/skills/{n}/SKILL.md', f'{B}/skills/_shared', 'skills')
col = lambda s: re.sub(r'\s+', ' ', s)
txt = {}
for k, v in P.items():
    try: txt[k] = col(open(f'{root}/{v}').read())
    except FileNotFoundError: txt[k] = None
ok = bad = 0
def has(key, s, want=None):
    """want=None: present at least once; want=n: exactly n."""
    global ok, bad
    t = txt[key]; n = -1 if t is None else t.count(col(s))
    good = (n >= 1) if want is None else (n == want)
    if good: ok += 1
    else:
        bad += 1; print(f'FAIL {key} {P[key]}: {s[:70]!r} count {n}, want {"≥1" if want is None else want}')
TARGET = 'target:' if ed == 'aw' else '**Target:**'
for s in ('enumerate-components', 'multi-component-test', 'multi-component-prereqs', 'component-of', 'Also touches:', 'coverage_gaps'):
    has('COMP', s)
for s in ('landing_order', 'contracts:'): has('ARDRES', s)
has('PRELINT', '## Contracts'); has('GRILL', '**Cross-component**')
for s in ('components:', '## Contracts', '### Landing order', 'an interface that crosses two components'): has('ARDFMT', s)
for s in ('theme → component', 'enumerate-components', '**Components and contracts.**'): has('CARD', s)
has('CARD', 'propose a `theme → repo` mapping', 0)
has('ARDREV', '**Contract completeness')
for s in (TARGET, '## Contract', 'Also touches:', '**A contract Epic**'): has('EW', s)
for s in ('Single target (conditional)', 'Contract citation (conditional)', '**Exception (multi-component):**'): has('ER', s)
for s in ('Phase 2.7 — Multi-component prerequisites', 'Phase 5.5 — Components', '### Targets', 'multi-component-prereqs'): has('EPICS', s)
for s in ('**An Epic with a target.**', 'A multi-component PRD at PRD level'): has('SPEC', s)
for s in ('multi-component-test', 'Target span', 'Re-split'): has('DESIGN', s)
for s in ('**Target**:', 'Target span'): has('DFMT', s)
has('DREV', '**Target & contract')
for s in ('**On a multi-component PRD**', '**requirements source**', '**Except on a multi-component PRD**'): has('WS', s)
for s in ('**(d) Targets and contract coverage', '## Contract coverage', '### Contract coverage', 'multi-component-prereqs'): has('READY', s)
for s in ('Cross-Epic contract coverage (conditional)', '#### Cross-Epic contract coverage'): has('RREV', s)
for s in ('the multi-component check', 'multi-component-prereqs', 'Split into Epics first'): has('IMPL', s)
for n in ('create-ard', 'epics', 'specify', 'design', 'ready', 'implement'): has(f'DOC_{n}', '### Multi-component')
has('REFS', '`components.md`')
has('DOC_create-ard', 'theme-to-repo', 0)
has('EPICS', {'aw': 'PRD-level `/specify` remains optional.', 'ie': 'VI-level `/specify` remains optional.', 'ce': 'VI-level `specify:` remains optional.'}[ed], 0)
if ed == 'aw': has('DESIGN', 'This bullet is taken first, so a PRD folder', 0)
has('ARDRES', 'One stated exception asks rather than stays silent')
if ed == 'aw':
    has('REFS', 'bundles 31 files'); has('REFS', 'bundles 30 files', 0)
    has('PWREFS', '`## Contracts`'); has('DWREFS', 'names its `Target`')
    has('RPW', 'theme→repo proposal', 0); has('RPW', '**On a multi-component PRD**')
    has('RDW', '### Multi-component PRDs'); has('RWC', 'thirty-one reference files'); has('RWC', 'references/components.md` is the **single source of truth**')
    has('CLAUDE', 'a multi-component PRD asks first'); has('PICKER', 'never on a multi-component PRD')
    has('CL', '## [1.12.0]'); has('PWCL', '## [3.13.0]'); has('DWCL', '## [4.8.0]')
else:
    has('CL', '## [2.69.0]' if ed == 'ie' else '## [2.38.0]')
if ed == 'ce':
    for f in ('.github/instructions/dev-workflows-shared.instructions.md', '.github/instructions/dev-workflows-skill-map.instructions.md'):
        n = len(open(f'{root}/{f}').read())
        if n < 20000: ok += 1
        else: bad += 1; print(f'FAIL {f}: {n} characters, want < 20000')
print(f'{ed}: {ok} passed, {bad} failed')
`````

#### `scripts/apply.sh`

`````bash
#!/usr/bin/env bash
# apply.sh EDITION ROOT GROUP [--dry] — apply one group of this round's edit files to one edition, in order;
# GROUP is core | ard | epics | specify | design | ready | implement | tiers | all. Stops at the first mismatch.
# The internal and Copilot editions' lists are added by Tasks 11 and 12, from this edition's reviewed text.
set -euo pipefail
ed=$1; R=$2; grp=$3; dry=${4:-}; S=$(cd "$(dirname "$0")" && pwd); E=$S/edits
w(){ python3 "$S/wsub.py" "$R/$1" "$E/$2" $dry; }
new(){ if [ -z "$dry" ]; then cp "$S/files/$2" "$R/$1"; echo "created $R/$1"; else test ! -e "$R/$1" && echo "checked new file: $R/$1"; fi; }
W=plugins/workflows-core; PW=plugins/product-workflows; DW=plugins/dev-workflows
g_core(){ new $W/references/components.md components.md; w $W/references/ard-resolution.md aw-ard-resolution.txt
  w $W/references/pre-lint.md aw-prelint.txt; w $W/references/grilling-technique.md aw-grilling.txt
  w $W/references/epic-picker.md aw-epic-picker.txt; w $W/docs/reference/references.md aw-wc-references.txt; }
g_ard(){ w $PW/references/ard-format.md aw-ard-format.txt; w $PW/commands/create-ard.md aw-create-ard.txt
  w $PW/agents/ard-reviewer.md aw-ard-reviewer.txt; w $PW/docs/commands/create-ard.md aw-doc-create-ard.txt
  w $PW/docs/reference/references.md aw-doc-pw-references.txt; }
g_epics(){ w $PW/agents/epic-writer.md aw-epic-writer.txt; w $PW/agents/epic-reviewer.md aw-epic-reviewer.txt
  w $PW/commands/epics.md aw-epics.txt; w $PW/docs/commands/epics.md aw-doc-epics.txt; }
g_specify(){ w $PW/commands/specify.md aw-specify.txt; w $PW/docs/commands/specify.md aw-doc-specify.txt; }
g_design(){ w $DW/references/design-format.md aw-design-format.txt; w $DW/references/workflow-states.md aw-workflow-states.txt
  w $DW/agents/design-reviewer.md aw-design-reviewer.txt; w $DW/commands/design.md aw-design.txt
  w $DW/docs/commands/design.md aw-doc-design.txt; w $DW/docs/reference/references.md aw-doc-dw-references.txt; }
g_ready(){ w $DW/agents/readiness-reviewer.md aw-readiness-reviewer.txt; w $DW/commands/ready.md aw-ready.txt
  w $DW/docs/commands/ready.md aw-doc-ready.txt; }
g_implement(){ w $DW/commands/implement.md aw-implement.txt; w $DW/docs/commands/implement.md aw-doc-implement.txt; }
g_tiers(){ w .claude/rules/product-workflows.md aw-rules-pw.txt; w .claude/rules/dev-workflows.md aw-rules-dw.txt
  w .claude/rules/workflows-core.md aw-rules-wc.txt; w CLAUDE.md aw-claude-md.txt; }
case $ed in
aw) if [ "$grp" = all ]; then for x in core ard epics specify design ready implement tiers; do "g_$x"; done; else "g_$grp"; fi ;;
*) echo "apply.sh: no edit list for $ed yet — Tasks 11 and 12 write it"; exit 2 ;;
esac
`````

#### `scripts/gates.sh`

`````bash
#!/usr/bin/env bash
# gates.sh EDITION ROOT — the edition's CI gate chain (its .github/workflows run: steps), as one && chain.
ed=$1; cd "$2" || exit 2
python3 scripts/validate-catalog.py --selftest && python3 scripts/validate-catalog.py \
 && ./scripts/check-id-grammar.sh --selftest && ./scripts/check-id-grammar.sh --root . \
 && ./scripts/check-docs.sh --selftest && ASSERT_PUBLISHED=1 ./scripts/check-docs.sh --root . \
 && { test -d scripts/mermaid/node_modules || npm ci --prefix scripts/mermaid --ignore-scripts --no-audit --no-fund >/dev/null; } \
 && node scripts/mermaid/check-mermaid.mjs --selftest && node scripts/mermaid/check-mermaid.mjs --root . \
 && case $ed in aw) python3 "$(find plugins -type f -name session-cost.py)" --selftest ;; ie) python3 plugins/dev-workflows/scripts/session-cost.py --selftest ;; ce) true ;; esac
`````

#### `scripts/release.py`

`````python
#!/usr/bin/env python3
"""release.py EDITION ROOT [DATE] — bump this round's versions and insert its changelog sections ($S/cl/<ed>-<plugin>.md),
re-dating each to DATE (default: the date written in the section) so it ships dated (CLAUDE.md, check 18)."""
import json, os, re, sys
ed, root = sys.argv[1], sys.argv[2]; date = sys.argv[3] if len(sys.argv) > 3 else None
S = os.path.dirname(os.path.abspath(__file__))
R = {'aw': ('.claude-plugin/marketplace.json', {
         'workflows-core': ('1.11.1', '1.12.0', 'plugins/workflows-core/.claude-plugin/plugin.json', 'plugins/workflows-core/CHANGELOG.md'),
         'product-workflows': ('3.12.1', '3.13.0', 'plugins/product-workflows/.claude-plugin/plugin.json', 'plugins/product-workflows/CHANGELOG.md'),
         'dev-workflows': ('4.7.0', '4.8.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md')}),
     'ie': ('.claude-plugin/marketplace.json', {
         'dev-workflows': ('2.68.0', '2.69.0', 'plugins/dev-workflows/.claude-plugin/plugin.json', 'plugins/dev-workflows/CHANGELOG.md')}),
     'ce': ('.github/plugin/marketplace.json', {
         'dev-workflows': ('2.37.0', '2.38.0', 'dev-workflows/.plugin/plugin.json', 'dev-workflows/CHANGELOG.md')})}[ed]
market, plugins = R
m = open(f'{root}/{market}').read()
for name, (old, new, pj, cl) in plugins.items():
    s = open(f'{root}/{pj}').read()
    assert s.count(f'"version": "{old}"') == 1, (pj, old)
    open(f'{root}/{pj}', 'w').write(s.replace(f'"version": "{old}"', f'"version": "{new}"'))
    pat = re.compile(r'("name":\s*"' + re.escape(name) + r'"[^}]*?"version":\s*")' + re.escape(old) + '"', re.S)
    m, n = pat.subn(lambda mm: mm.group(1) + new + '"', m)
    assert n == 1, (market, name, n)
    c = open(f'{root}/{cl}').read(); i = c.index('\n## [')
    sec = open(f'{S}/cl/{ed}-{name}.md').read().rstrip('\n')
    if date: sec = re.sub(r'^(## \[[^\]]+\] — )\d{4}-\d{2}-\d{2}', r'\g<1>' + date, sec, count=1)
    open(f'{root}/{cl}', 'w').write(c[:i + 1] + sec + '\n\n' + c[i + 1:])
open(f'{root}/{market}', 'w').write(m)
for e in json.load(open(f'{root}/{market}'))['plugins']:
    if e['name'] in plugins: print(e['name'], e['version'], json.load(open(f"{root}/{plugins[e['name']][2]}"))['version'])
`````

## Appendix B — edit files

Extracted by Task 0 Step 2 into `$S/edits`. Each block is `<<<<<<< OLD <n>` (the text, matched whitespace-insensitively, `n` times), `=======`, the replacement, `>>>>>>> NEW`. Every file is this edition's (`aw-`); the ports' files are written in Tasks 11 and 12.

#### `edits/aw-ard-format.txt`

`````text
<<<<<<< OLD 1
- **Per-area** — a big Epic spanning separable areas in one repo (e.g. backend `server/` + frontend `ui/`) may split into `ard-<area>.md` beside the folder's `ard.md` (grill-decided).
=======
- **Per-area** — a big Epic spanning separable areas in one repo (e.g. backend `server/` + frontend `ui/`) may split into `ard-<area>.md` beside the folder's `ard.md` (grill-decided).
- **Multi-component** — a PRD-level ARD whose `components:` lists two or more components (`workflows-core:components` §3) also carries `## Contracts`: the interfaces between those components, fixed here so that the one-component Epics on either side fit together once each is implemented on its own.
>>>>>>> NEW
<<<<<<< OLD 1
grounded_repos:
  - <repo-slug @ absolute path>
=======
grounded_repos:
  - <repo-slug @ absolute path>
components:                  # PRD level only — the components this PRD touches (workflows-core:components §5)
  - id: <repo-slug> | <repo-slug>:<path>
    kind: code | deploy      # optional; default code
    paths: [<path>, ...]     # optional; default the id's own path, or the whole repository for a bare slug
>>>>>>> NEW
<<<<<<< OLD 1
**Unknown frontmatter keys are preserved.**
=======
**`components:` is the known set every Epic target is resolved against.** The architect confirms it in `/create-ard` Phase 3, and it lists the components this PRD touches, never every module a repository has. Every entry's repository is in `grounded_repos` or is named under `## Open questions`. It is written at PRD level only: an Epic-level ARD carries none, and the PRD-level ARD's set applies to its Epics. An ARD with no `components:` key — every ARD written before the key existed — supplies no set, and each consumer then behaves exactly as it did before (`workflows-core:components` §3).

**Unknown frontmatter keys are preserved.**
>>>>>>> NEW
<<<<<<< OLD 1
- `## Cross-repo / component approach` — the Capability→Architecture map (which capability lands in which repo/component).
=======
- `## Cross-repo / component approach` — the Capability→Architecture map (which capability lands in which repo/component). On a multi-component ARD each capability names the component ids it lands in, and one that lands in two or more is a capability `## Contracts` must give an interface row.
- `## Contracts` — **PRD level, and only when `components:` has two or more entries.** An interface table, then three subsections:

  | AD | Producer | Consumers | Kind | Status | Artifact |
  |---|---|---|---|---|---|
  | [AD#3] | bookstore:orders | bookstore:carts, bookstore:web | REST | new | — |

  `AD` is the `[AD#N]` whose Rule states the interface; `Producer` is one component id and `Consumers` one or more, all from `components:`; `Kind` is `REST`, `message`, `shared schema`, `shared library` or `generated client`; `Status` is `new`, `changed`, or `exists` (already in the code, cited under Grounding findings); `Artifact` is the path in the producer where the contract is a code file — an OpenAPI or `.proto` file, an entity module, a generated client — else `—`. Then `### Schema ownership` (which component owns each shared shape), `### Versioning and compatibility` (how each interface changes without breaking the other side), and `### Landing order` (an ordered list of component ids; a producer whose `Artifact` is a code file comes before every one of its consumers). **The table is the one place producer, consumers and status are written**; each row's `AD#N` stays under `## Architecture decisions` with its Binds, Prevents and Rule, so the `AD#N` series stays single. An Epic-level ARD inherits these rows read-only, as it inherits PRD-level `AD#N`.
>>>>>>> NEW
<<<<<<< OLD 1
- An `AD#N` earns its place only when the decision is **hard to reverse** AND **surprising without context** AND the result of a **real trade-off**; a decision missing any of the three is an ordinary implementation choice (leave it to `/design`), not an architecture decision.
=======
- An `AD#N` earns its place only when the decision is **hard to reverse** AND **surprising without context** AND the result of a **real trade-off**; a decision missing any of the three is an ordinary implementation choice (leave it to `/design`), not an architecture decision. **One stated case meets the bar by what it is:** an interface row's `AD#N` — an interface that crosses two components, which both sides ship against and so cannot reverse alone.
- On a multi-component ARD, every capability the Capability→Architecture map lands in two or more components has an interface row, and every row's components are in `components:`.
>>>>>>> NEW
`````

#### `edits/aw-ard-resolution.txt`

`````text
<<<<<<< OLD 1
   no ARD existed — a binding architecture document enforcing nothing, under a run that reports success.
=======
   no ARD existed — a binding architecture document enforcing nothing, under a run that reports success.
4. From the PRD folder's `ard.md` alone — on an Epic-level resolution too, since an Epic-level ARD carries neither (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §5) — read the frontmatter `components:` list into `components`, and the `## Contracts` section into `contracts`: one row per line of its interface table (`| AD | Producer | Consumers | Kind | Status | Artifact |`, the `Consumers` cell split on commas, an `Artifact` of `—` read as null) and the ids of its `### Landing order` list, in order. Accept `[AD#N]` and the legacy dash form in the `AD` column exactly as step 3 does, emitting the `#` form. An ARD with no `components:` key yields `components: []`; one with no `## Contracts` heading yields `contracts: null`.
>>>>>>> NEW
<<<<<<< OLD 1
guidance_summary: <short prose: the ARD's non-AD#N architecture guidance the consumer should heed>
```
=======
guidance_summary: <short prose: the ARD's non-AD#N architecture guidance the consumer should heed>
components:          # the PRD-level ARD's `components:` (step 4), or []
  - id: <component id>
    kind: code | deploy
    paths: [ <path>, ... ]
contracts:           # the PRD-level ARD's `## Contracts` (step 4), or null
  rows:
    - ad: AD#N
      producer: <component id>
      consumers: [ <component id>, ... ]
      kind: REST | message | shared schema | shared library | generated client
      status: new | changed | exists
      artifact: <path in the producer> | null
  landing_order: [ <component id>, ... ]
```
>>>>>>> NEW
<<<<<<< OLD 1
`status: none` when no ARD file resolves (the common case — `/create-ard` is optional).
=======
`status: none` when no ARD file resolves (the common case — `/create-ard` is optional), and `components` is then `[]` and `contracts` `null`.
>>>>>>> NEW
<<<<<<< OLD 1
The other five pass `invariants` to their reviewer as `applicable_ard`;
=======
`components` and `contracts` are read by `${CLAUDE_PLUGIN_ROOT}/references/components.md` §3 and §6 and passed on by `/epics` to `epic-writer` and `epic-reviewer`; a caller that reads neither field behaves exactly as it did before they existed.

The other five pass `invariants` to their reviewer as `applicable_ard`;
>>>>>>> NEW
<<<<<<< OLD 1
extra phase output, no reviewer dimension. The ARD steps are strictly additive and guarded on
`status: found`.
=======
extra phase output, no reviewer dimension. The ARD steps are strictly additive and guarded on
`status: found`.

**One stated exception asks rather than stays silent.** On a multi-component PRD (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §3), an ARD without `## Contracts` — `none` included — leaves the Epics with no contract to fit together by, so `/epics` (Phases 2.7 and 5.5) and `/implement` (Phase 1) ask whether to stop and author it first (`components.md` §6). Each offers to continue without it, and continuing proceeds exactly as `none` does here: the ARD is still never a prerequisite. `/ready` asks nothing and caps its verdict instead.
>>>>>>> NEW
`````

#### `edits/aw-ard-reviewer.txt`

`````text
<<<<<<< OLD 1
- **Identifier integrity:** `[AD#N]` unique + contiguous; cross-references point at existing IDs.
=======
- **Contract completeness (conditional — only when the PRD-level frontmatter `components:` has two or more entries; otherwise report `N/A — single component`):** the interface rules of `${CLAUDE_PLUGIN_ROOT}/references/ard-format.md` § Sections (`## Contracts`) and `workflows-core:components` §5. **BLOCKER:** a capability the Capability→Architecture map lands in two or more components with no interface row; a row whose `AD` names an `[AD#N]` with no `### [AD#N]` block. **MAJOR:** a `Producer` or `Consumers` value not in `components:`; an empty `### Versioning and compatibility` or `### Landing order`; a component whose repository is neither in `grounded_repos` nor under Open questions; a row with `Status: exists` that no Grounding finding cites; a row whose `Artifact` is a code file and whose producer does not come before every one of its consumers in `### Landing order`.
- **Identifier integrity:** `[AD#N]` unique + contiguous; cross-references point at existing IDs.
>>>>>>> NEW
`````

#### `edits/aw-claude-md.txt`

`````text
<<<<<<< OLD 1
an absent optional input still delegates to the command's pre-existing behaviour and never becomes a prerequisite.
=======
an absent optional input still delegates to the command's pre-existing behaviour and never becomes a prerequisite (a multi-component PRD asks first: `workflows-core:components` §6).
>>>>>>> NEW
<<<<<<< OLD 1
After editing files in this repo and pushing, update the affected plugin on
each machine so Claude Code picks up the new command, agent, hook, and
reference content:
=======
After pushing an edit, update the affected plugin on each machine so Claude Code picks up the new content:
>>>>>>> NEW
<<<<<<< OLD 1
These notes complement the user-scope Claude guidance. They add only the
marketplace-specific behaviors that are easy to forget during workflow edits.
=======
These notes add to the user-scope Claude guidance only the marketplace-specific behaviors that are easy to forget during workflow edits.
>>>>>>> NEW
`````

#### `edits/aw-create-ard.txt`

`````text
<<<<<<< OLD 1
   propose a `theme → repo` mapping against those dirs, and **ask the architect to confirm / correct /
   add**. For any requirement that maps to no obvious repo, **ask outright**: "which repo covers `<X>`?"
=======
   propose a `theme → component` mapping against those dirs, and **ask the architect to confirm / correct / add / group**. A component is a repository or a module inside one (`workflows-core:components` §1). On a PRD-level run, run `enumerate-components` (§2) over each repository a theme reaches and propose the modules the themes touch, never every module the repository declares; a repository that declares none is proposed whole. On an Epic-level run the proposal starts from the Epic's `target:` and from the producer of every interface its `## Contract` consumes. For any requirement that maps to no obvious component, **ask outright**: "which repo, or which module of it, covers `<X>`?" On a PRD-level run the confirmed list is the ARD's `components:` (§5) — each entry's `paths` passed to step 4's scan as `search_hints.paths` — and with two or more, Phase 4 authors `## Contracts`.
>>>>>>> NEW
<<<<<<< OLD 1
→ Architecture decisions (`AD#N`: Binds/Prevents/Rule) → Cross-repo/component approach → Stack & invariants
=======
→ Architecture decisions (`AD#N`: Binds/Prevents/Rule) → Cross-repo/component approach → Contracts (PRD level, two or more components) → Stack & invariants
>>>>>>> NEW
<<<<<<< OLD 1
At Epic level, list inherited PRD-level ADs read-only and never contradict them; PRD level stays at invariants/frame (no per-repo detailed solutions).
=======
At Epic level, list inherited PRD-level ADs read-only and never contradict them; PRD level stays at invariants/frame (no per-repo detailed solutions).

**Components and contracts.** On a PRD-level run, write `components:` as Phase 3 confirmed it (`workflows-core:components` §5). Where it has two or more entries, author `## Contracts` (`${CLAUDE_PLUGIN_ROOT}/references/ard-format.md` § Sections): for every capability the Capability→Architecture map lands in two or more components, settle the interface — its kind, producer, consumers, schema owner, versioning and compatibility, and whether the contract is a code artifact and where — and write it as an `AD#N` whose Rule states it, with its row in the interface table; then the landing order. The grill's *Cross-component* gap category (`workflows-core:grilling-technique`) applies here. An Epic-level ARD carries no `components:`, and its inherited interface rows are read-only, like its inherited `AD#N`.
>>>>>>> NEW
<<<<<<< OLD 1
offer `/product-workflows:specify <PRD>` (PE) carrying the same `<merge-clause>`. *(No `/design` — no Epics yet.)*
=======
offer `/product-workflows:specify <PRD>` (PE) carrying the same `<merge-clause>`. *(No `/design` — no Epics yet.)* **Where this run wrote `components:` with two or more entries and the PRD has 0 Epics**, the first two options swap and the marker moves with them — `choices: ["Author a PRD-level spec — /product-workflows:specify <PRD> (PE) (Recommended) <merge-clause>", "Hand to a Product Engineer — /product-workflows:epics <ADDRESS> (PE) <merge-clause>", "Stop here"]` — because the end-to-end acceptance criteria a PRD-level spec states are what `/epics` splits across the components, and `/epics` stops to recommend that spec where it is missing (`workflows-core:components` §6). Where the `prd.md` precondition above fails, the array above applies unchanged.
>>>>>>> NEW
`````

#### `edits/aw-design-format.txt`

`````text
<<<<<<< OLD 1
- **Repos**: <the confirmed implementation repos this design spans>
=======
- **Repos**: <the confirmed implementation repos this design spans>
- **Target**: <the Epic's `target:` component id — omit the line where the Epic carries none>
>>>>>>> NEW
<<<<<<< OLD 1
4. **## Interfaces / contracts** (core) — exact signatures, API shapes, schemas, events, config keys
   the change introduces or alters. Concrete types, not prose promises.
=======
4. **## Interfaces / contracts** (core) — exact signatures, API shapes, schemas, events, config keys
   the change introduces or alters. Concrete types, not prose promises. On a multi-component PRD (`workflows-core:components` §3), also name each interface the Epic's `## Contract` produces — its `[AD#N]`, and how this design meets that row's Rule — and each it consumes — its `[AD#N]`, and the stub or test double `## Test strategy` uses for it.
>>>>>>> NEW
<<<<<<< OLD 1
9. **## Risks & mitigations** (scaled) — engineering risks (performance, concurrency, data-loss, blast
   radius) and the mitigation or explicit acceptance for each.
=======
9. **## Risks & mitigations** (scaled) — engineering risks (performance, concurrency, data-loss, blast
   radius) and the mitigation or explicit acceptance for each. A repository added to a targeted Epic's design at `/design` Phase 3 is recorded here as `- Target span: <component> — <why>`: `/implement` will plan its change as a companion change in that repository, and the line is what says so before it does.
>>>>>>> NEW
`````

#### `edits/aw-design-reviewer.txt`

`````text
<<<<<<< OLD 1
## Output contract
=======
- **Target & contract (conditional — only when the design's header carries `- **Target**:`; otherwise skip silently):** the design's implementation stays inside its target component — the repository the id names before any `:`, and within it the module path after it. Exempt: a change to deployment or configuration files of the same repository that exists only to deploy or configure the target — a ride-along, which the Epic names in an `- Also touches:` line. Implementation beyond the target with **no** matching `- Target span:` line under `## Risks & mitigations` → **BLOCKER**; with one → allowed-but-flagged (name it in the Summary). Where `## Interfaces / contracts` names a consumed `[AD#N]` with no stub or test double for it in `## Test strategy` → **MAJOR**. A produced interface that breaks its `AD#N` Rule is the ARD-conformance dimension's BLOCKER, not this one's.

## Output contract
>>>>>>> NEW
`````

#### `edits/aw-design.txt`

`````text
<<<<<<< OLD 1
   - **`<EPIC>` null** → inspect the resolved PRD dir in the specs repo:
=======
   - **`<EPIC>` null on a multi-component PRD.** First run `multi-component-test` (`Skill(skill: "workflows-core:reference", args: "components multi-component-test")`, §3) on the resolved PRD dir. Where it returns `multi_component: true`, a flat `specification.md` is a requirements source the PRD's Epics are designed from, never one unit designed whole (`${CLAUDE_PLUGIN_ROOT}/references/workflow-states.md`, *Ready for Implementation*): skip the flat-spec bullet below and take its Epic-subfolder bullet. Where no Epic subfolder holds a `specification.md` on `<default>`, ask instead:
     `choices: ["Split into Epics first — /product-workflows:epics <PRD> (Recommended)", "Design across components anyway", "Cancel"]`
     **Split** stops, naming that command; **Cancel** stops; **Design across components anyway** takes the flat-spec bullet below, and the Final report names the override. Where it returns `multi_component: false`, nothing here applies.
   - **`<EPIC>` null** → inspect the resolved PRD dir in the specs repo:
>>>>>>> NEW
<<<<<<< OLD 1
1. **Auto-derive candidate repos** from the spec's themes / component mentions / any referenced code
   paths.
=======
1. **Auto-derive candidate repos** from the spec's themes / component mentions / any referenced code
   paths — **or, where `<EPIC>` is set and its `epic.md` carries a `target:`** (`workflows-core:components` §1), the target's repository alone, the Epic's other needs being the interfaces the PRD-level ARD's `contracts` fixes.
>>>>>>> NEW
<<<<<<< OLD 1
   `choices: ["Confirm this set (Recommended)", "Add repos (you'll be prompted)", "Remove repos (you'll be prompted)", "Cancel"]`
=======
   `choices: ["Confirm this set (Recommended)", "Add repos (you'll be prompted)", "Remove repos (you'll be prompted)", "Cancel"]`
   **On an Epic with a target, "Add repos" asks first**, because a second repository makes the design span two components:
   `choices: ["Re-split — /product-workflows:epics <EPIC> (Recommended)", "Add anyway (recorded as a target span)", "Cancel"]`
   **Re-split** stops, naming that command, whose refine mode re-drafts this Epic; **Cancel** stops; **Add anyway** takes the added repositories, and Phase 5 records each under `## Risks & mitigations` as `- Target span: <component> — <why>`, which `design-reviewer` flags.
>>>>>>> NEW
<<<<<<< OLD 1
  >   paths:    [globs inferred from themes, or []]
=======
  >   paths:    [the target's `paths` where Phase 3 took an Epic's target, else globs inferred from themes, or []]
>>>>>>> NEW
<<<<<<< OLD 1
On `status: found`, carry the returned `invariants` (PRD-level inherited + Epic-level `AD#N`) and `guidance_summary` into Phase 5
=======
On `status: found`, carry the returned `invariants` (PRD-level inherited + Epic-level `AD#N`), `guidance_summary` and `contracts` into Phase 5
>>>>>>> NEW
<<<<<<< OLD 1
  Risks & mitigations, Migration / rollout / backward-compatibility, Out of scope. Omit a
  non-applicable section with a one-line `_N/A — why_`.
=======
  Risks & mitigations, Migration / rollout / backward-compatibility, Out of scope. Omit a
  non-applicable section with a one-line `_N/A — why_`.
- **Target and contract.** Where the Epic carries a `target:`, the header's `- **Target**:` names it. Where Phase 2.5 carried `contracts` and the Epic's `## Contract` cites rows, `## Interfaces / contracts` names each interface the Epic produces — its `[AD#N]`, and how the design meets that Rule — and each it consumes — its `[AD#N]`, and the stub or test double `## Test strategy` uses for it (`${CLAUDE_PLUGIN_ROOT}/references/design-format.md`).
>>>>>>> NEW
<<<<<<< OLD 1
confirmed repo set (and any removed-from-scope);
=======
confirmed repo set (and any removed-from-scope), the Epic's target and any `Target span` added at Phase 3, and any multi-component override taken at Phase 0;
>>>>>>> NEW
<<<<<<< OLD 1
**This bullet is taken first, so a PRD folder holding a flat `specification.md` *and* Epic subfolders designs the slice and never reaches the picker**
=======
**This bullet is taken first after the multi-component bullet above, so a single-component PRD folder holding a flat `specification.md` *and* Epic subfolders designs the slice and never reaches the picker**
>>>>>>> NEW
`````

#### `edits/aw-doc-create-ard.txt`

`````text
<<<<<<< OLD 1
## What it needs
=======
### Multi-component PRDs

A **component** is a repository, or a module inside one — a Gradle or Maven module, a workspace package, a top-level directory with its own build file, or a deploy directory such as `k8s/`. At PRD level the run proposes the components the PRD's themes touch, reading each repository's own module declarations, and you confirm, correct, add or group them; the confirmed list becomes the ARD's `components:` frontmatter. With two or more components the grill also writes `## Contracts`: one row per interface between components — its `[AD#N]`, producer, consumers, kind, status and, where the contract is a code file, its path — then schema ownership, versioning and compatibility, and the landing order. `ard-reviewer` blocks a capability that crosses components with no interface row. With two or more components and no Epics yet, the next-step offer recommends a PRD-level `/specify` before `/epics`.

## What it needs
>>>>>>> NEW
<<<<<<< OLD 1
proposes a theme-to-repo mapping and asks you to confirm it
=======
proposes a theme-to-component mapping — repositories, or modules inside them — and asks you to confirm it
>>>>>>> NEW
<<<<<<< OLD 1
proposes a theme-to-repo mapping from the PRD/Epic's capability themes, and asks the architect to confirm, correct, or add to it.
=======
proposes a theme-to-component mapping — repositories, or modules inside them — from the PRD/Epic's capability themes, and asks the architect to confirm, correct, add to or group it.
>>>>>>> NEW
<<<<<<< OLD 1
A theme that maps to no obvious repo is asked about outright.
=======
A theme that maps to no obvious repository or module is asked about outright.
>>>>>>> NEW
`````

#### `edits/aw-doc-design.txt`

`````text
<<<<<<< OLD 1
## What it needs

- **`$SPECS_PATH`** — must resolve;
=======
### Multi-component PRDs

On a PRD with two or more components, `/design <PRD>` never designs the PRD-level specification as one unit: it goes to the Epic picker, and with no specified Epic it recommends `/epics` first. At Epic level the repository set starts from the Epic's `target:`; adding a second repository asks whether to re-split the Epic, and adding it anyway records a `Target span` risk that `design-reviewer` flags. The design header names the target, and `## Interfaces / contracts` names each interface the Epic produces or consumes, with the stub its test strategy uses for each one it consumes.

## What it needs

- **`$SPECS_PATH`** — must resolve;
>>>>>>> NEW
<<<<<<< OLD 1
**and it is tested first, so a PRD folder holding both that file and Epic subfolders designs the slice and is never offered an Epic here**
=======
**and on a single-component PRD it is tested first, so a PRD folder holding both that file and Epic subfolders designs the slice and is never offered an Epic here** (a multi-component one goes to the Epic picker — see *Multi-component PRDs*)
>>>>>>> NEW
`````

#### `edits/aw-doc-dw-references.txt`

`````text
<<<<<<< OLD 1
`interface-designer` reads its `## Seams` categories, and `/ready` reads its repos header.
=======
`interface-designer` reads its `## Seams` categories, and `/ready` reads its repos header. A targeted Epic's design also names its `Target` in the header, and its `## Interfaces / contracts` names the ARD interfaces it produces and consumes.
>>>>>>> NEW
<<<<<<< OLD 1
and the artifacts expected to exist at that status; the rubric `readiness-reviewer` applies.
=======
and the artifacts expected to exist at that status; the rubric `readiness-reviewer` applies. On a multi-component PRD its *Ready for Implementation* rung expects the ARD with `## Contracts` and the PRD-level specification, and no PRD-level design.
>>>>>>> NEW
`````

#### `edits/aw-doc-epics.txt`

`````text
<<<<<<< OLD 1
## What it needs
=======
### Multi-component PRDs

Every Epic gets one `target:` — the one component it changes — from the PRD-level ARD's `components:`, or, with no ARD, from the components you confirm after the code scan, which asks only when the scan finds two or more. A capability that spans components becomes one Epic per component, linked through `## Dependencies` in the ARD's landing order. With two or more components, each Epic's `## Contract` cites the ARD interfaces it produces or consumes, a consumer's Independent Test runs against a stub of each, and an interface whose contract is a code file gets its own Epic, first in order. A change to a deploy directory of the same repository that exists only to deploy the Epic's target rides along as an `- Also touches:` line instead of becoming an Epic. Before drafting, the run checks that the ARD's `## Contracts` and a PRD-level `specification.md` are on the specs repo's default branch and recommends running whichever is missing first; you can split without them, and the final report records that you did. `epic-reviewer` blocks an Epic with no target or one whose scope spans components.

## What it needs
>>>>>>> NEW
<<<<<<< OLD 1
`/epics` has 20 `## Phase` headings
=======
`/epics` has 22 `## Phase` headings
>>>>>>> NEW
<<<<<<< OLD 1
    p2 --> p2526["Phase 2.5 — Resolve applicable ARD (optional) / Phase 2.6 — PRD-level spec enrichment (optional)"]
=======
    p2 --> p2526["Phase 2.5 — Resolve applicable ARD (optional) / Phase 2.6 — PRD-level spec enrichment (optional) / Phase 2.7 — Multi-component prerequisites (ARD set only)"]
>>>>>>> NEW
<<<<<<< OLD 1
    d1 -- "on" --> p45["Phase 4 — Resolve repos (conditional) / Phase 5 — Parallel code scanning (conditional)"]
    d1 -- "off" --> p6["Phase 6 — Write Epics"]
    p45 --> p6
=======
    d1 -- "on" --> p45["Phase 4 — Resolve repos (conditional) / Phase 5 — Parallel code scanning (conditional)"]
    d1 -- "off" --> p6["Phase 6 — Write Epics"]
    p45 --> p55["Phase 5.5 — Components (only without an ARD set)"]
    p55 --> p6
>>>>>>> NEW
`````

#### `edits/aw-doc-implement.txt`

`````text
<<<<<<< OLD 1
## What it needs
=======
### Multi-component PRDs

On a keyed run for an Epic of a PRD with two or more components, Phase 1 checks that the Epic's target is in this repository; that the ARD's `## Contracts`, the PRD-level specification, and the Epic's own specification and design are on the specs repo's default branch; and that every interface the Epic consumes is produced by some Epic. A gap asks whether to stop and run the missing step first (recommended) or to continue, and continuing names the gap under the pull request's *Merge danger*. Addressed by its PRD, a multi-component PRD's flat specification is never offered as a slice to implement.

## What it needs
>>>>>>> NEW
<<<<<<< OLD 1
When the PRD is bare, a cheap folder read classifies it:
=======
When the PRD is bare, a cheap folder read classifies it (on a multi-component PRD the flat-specification cases below never arise — see *Multi-component PRDs*):
>>>>>>> NEW
`````

#### `edits/aw-doc-pw-references.txt`

`````text
<<<<<<< OLD 1
and `dev-workflows:ready` reads its `grounded_repos:` frontmatter.
=======
and `dev-workflows:ready` reads its `grounded_repos:` frontmatter. At PRD level it also carries `components:` — the components the PRD touches — and, with two or more, a `## Contracts` section fixing the interfaces between them, which `/epics`, `/specify`, `/design`, `/ready` and `/implement` read.
>>>>>>> NEW
`````

#### `edits/aw-doc-ready.txt`

`````text
<<<<<<< OLD 1
## What it needs
=======
### Multi-component PRDs

On a PRD with two or more components, *Ready for Implementation* expects the ARD with `## Contracts`, the PRD-level specification, and a specification and design for every in-scope Epic — and no PRD-level design, because there the PRD-level specification is designed and implemented only through its Epics. The report adds a `Contract coverage` section: each Epic's target, and every interface a consumer uses that no Epic produces, one produced by an Epic that does not target its producer, and a consumer that does not depend on its producer.

## What it needs
>>>>>>> NEW
<<<<<<< OLD 1
**A PRD folder holding a flat `specification.md` is a broad PRD-level slice beside its Epics** — the unit `/design` designs and `/implement` implements as one —
=======
**A PRD folder holding a flat `specification.md` is a broad PRD-level slice beside its Epics** — the unit `/design` designs and `/implement` implements as one, save on a multi-component PRD (see *Multi-component PRDs*) —
>>>>>>> NEW
`````

#### `edits/aw-doc-specify.txt`

`````text
<<<<<<< OLD 1
## What it needs
=======
### Multi-component PRDs

At PRD level on a PRD with two or more components, the ARD's interfaces are ground truth: an acceptance criterion or test case that crosses components names the `[AD#N]` it crosses, so `/epics` can split it per side. At Epic level, an Epic with a `target:` narrows the scan to its target's repository and paths; what it needs from another component is read from the ARD's `## Contracts`, not by scanning that component.

## What it needs
>>>>>>> NEW
`````

#### `edits/aw-epic-picker.txt`

`````text
<<<<<<< OLD 1
  also holds a flat `specification.md`, the broad slice `/design` designs as one unit (`/implement`
  Phase 0).
=======
  also holds a flat `specification.md`, the broad slice `/design` designs as one unit (`/implement`
  Phase 0) — never on a multi-component PRD, where that file is a requirements source and no slice (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §3).
>>>>>>> NEW
`````

#### `edits/aw-epic-reviewer.txt`

`````text
<<<<<<< OLD 1
- **`applicable_ard`** — the PRD-level ARD `invariants` (AD#N), or omitted. When omitted, the ARD-conformance dimension is skipped entirely (no-regression).
=======
- **`applicable_ard`** — the PRD-level ARD `invariants` (AD#N), or omitted. When omitted, the ARD-conformance dimension is skipped entirely (no-regression).
- **`components`** (optional) — the run's known set of components, each `{id, kind, paths}` (an `id` is `<repo-slug>` or `<repo-slug>:<path>`), with `multi_component` and, where the ARD has them, `contracts` — its interface rows (`{ad, producer, consumers, kind, status, artifact}`) and `landing_order`. When omitted, the *Single target* and *Contract citation* dimensions report `N/A — no component set`.
>>>>>>> NEW
<<<<<<< OLD 1
| Epic independence | Each Epic delivers its value without any not-yet-built Epic. A forward dependency on an Epic that does not yet exist → MAJOR (resequence/merge). **Exception (refinement mode):** a dependency between two Epics in the same refined `refinement_targets` set is legal (it encodes real build order) and is judged by the Inter-target dependency sanity dimension, not flagged here. |
=======
| Epic independence | Each Epic delivers its value without any not-yet-built Epic. A forward dependency on an Epic that does not yet exist → MAJOR (resequence/merge). **Exception (refinement mode):** a dependency between two Epics in the same refined `refinement_targets` set is legal (it encodes real build order) and is judged by the Inter-target dependency sanity dimension, not flagged here. **Exception (multi-component):** a consumer's dependency on the Epic that produces an interface its `## Contract` consumes is legal — it encodes landing order — provided its Independent Test runs against a stub of that interface; the Contract citation dimension judges it, not this one. |
>>>>>>> NEW
<<<<<<< OLD 1
| Refinement completeness (conditional) |
=======
| Single target (conditional) | Only when the brief carries `components`. Each drafted Epic has exactly one `target:` naming an `id` in `components`, and its in-scope work lands in that component alone — a component's extent being its `paths` inside the id's repository (the part before `:`). Exempt: an `- Also touches: <id> — <why>` line under In scope naming a component whose `kind` is `deploy` and whose repository is the target's (a ride-along). **BLOCKER:** no `target:`; a target outside `components`; in-scope work landing in a second component other than such a ride-along; an `Also touches` line naming a `kind: code` component or a component of another repository. Absent → `N/A — no component set`. |
| Contract citation (conditional) | Only when `multi_component` is true and the brief carries `contracts`. **MAJOR:** a `Produces`/`Consumes` line citing an `[AD#N]` that is not a row of `contracts`; a `Produces` line on an Epic whose target is not that row's producer; a consumer of a `new` or `changed` row whose Independent Test names no stub for it, or whose Dependencies do not name the Epic that produces it; an interface the Epic's scope plainly uses but its `## Contract` does not cite; a row whose `artifact` is not null with no Epic targeting its producer and producing it, or with a consumer that does not depend on that Epic. Absent → `N/A — no contract`. |
| Refinement completeness (conditional) |
>>>>>>> NEW
<<<<<<< OLD 1
#### Refinement completeness
=======
#### Single target
- _"N/A — no component set"_ when the brief omitted `components`, else findings.

#### Contract citation
- _"N/A — no contract"_ when `multi_component` is false or the brief carries no `contracts`, else findings.

#### Refinement completeness
>>>>>>> NEW
`````

#### `edits/aw-epic-writer.txt`

`````text
<<<<<<< OLD 1
- `docs_grounding` — the `docs-grounder` digest
=======
- `components` — the known set (`workflows-core:components` §3), each entry `{id, kind, paths}`, or absent where the run had none; `multi_component` — true where it has two or more entries; `contracts` — the PRD-level ARD's interface `rows` and `landing_order` (`workflows-core:ard-resolution`), or absent where the ARD has no `## Contracts` or no ARD resolved. See *Components and contracts* below.
- `docs_grounding` — the `docs-grounder` digest
>>>>>>> NEW
<<<<<<< OLD 1
key: <this Epic's key — must match the folder name>
---
=======
key: <this Epic's key — must match the folder name>
target: <one component id from the handoff's `components` — omit this line where the handoff carries none>
---
>>>>>>> NEW
<<<<<<< OLD 1
## Dependencies
- <other Epics under this PRD or elsewhere, repos, teams, external systems — named>
- ...
=======
## Dependencies
- <other Epics under this PRD or elsewhere, repos, teams, external systems — named>
- ...

## Contract
- Produces: [AD#N] — <what this Epic implements of that interface>
- Consumes: [AD#N] — <the stub this Epic's Independent Test runs against>
>>>>>>> NEW
<<<<<<< OLD 1
## ARD conformance (only when `applicable_ard` is present)
=======
## Components and contracts (only when `components` is present)

The rules are `workflows-core:components`'; what follows is how they shape a draft.

- **One target per Epic.** Write exactly one `target:`, an `id` from `components`, never one outside it. A capability that lands in two or more components becomes one Epic per component, each linked to the others it needs by key in `## Dependencies` — in `contracts.landing_order` where the handoff carries `contracts`.
- **Ride-along** (§4). Where an Epic's target needs a change in a `kind: deploy` component **of the same repository** that exists only to deploy or configure the target, write it under `### In scope` as `- Also touches: <component id> — <why>`, and do not split it out. A change in a `kind: code` component, or in a component of another repository, is a second target: split it.
- **`## Contract`** — only where `multi_component` is true and the handoff carries `contracts`; omit the section otherwise. One line per interface row the Epic implements (`- Produces:`) or calls (`- Consumes:`), each citing the row's `[AD#N]`. An Epic produces only rows whose producer is its own target. A consumer's `## Independent Test` runs against a stub of each `new` or `changed` interface it consumes, named there, and its `## Dependencies` names the Epic that produces each one.
- **A contract Epic** exists only where a row's `artifact` is not null — the contract is a code file (an OpenAPI or `.proto` file, a shared entity module, a generated client). It targets the row's producer, produces that row, and comes first: every consumer of the row depends on it. A row whose artifact is null gets no Epic of its own; its producer's ordinary Epic produces it.
- **Multi-component without `contracts`** (the `/epics` prerequisites stop's override): still one target per Epic and still linked through `## Dependencies`, with no `## Contract` section.
- A capability you cannot place in one component of `components` is a `[NEEDS CLARIFICATION]` marker in the affected Epic's Scope, under the cap of three — never a guessed target.

## ARD conformance (only when `applicable_ard` is present)
>>>>>>> NEW
<<<<<<< OLD 1
emit `epic.md` inside it, carrying `kind: epic` and `key:` frontmatter (`workflows-core:addressing` §4):
=======
emit `epic.md` inside it, carrying `kind: epic` and `key:` frontmatter (`workflows-core:addressing` §4), and `target:` where the handoff carries `components`. The `## Contract` section below is written only where *Components and contracts* says so, and omitted otherwise:
>>>>>>> NEW
`````

#### `edits/aw-epics.txt`

`````text
<<<<<<< OLD 1
  and surfaced in the Phase 9 report — never edit the ARD.
=======
  and surfaced in the Phase 9 report — never edit the ARD.
- On `status: found`, also carry the returned `components` and `contracts`. Where `components` has entries, it is this run's **known set** (`Skill(skill: "workflows-core:reference", args: "components")` §3, source `ard`): Phase 4 scans its repositories, Phase 6 gives every Epic one `target:` from it, and Phase 5.5 does not run.
>>>>>>> NEW
<<<<<<< OLD 1
## Phase 3 — Read the PRD folder
=======
## Phase 2.7 — Multi-component prerequisites (ARD set only)

Runs only where Phase 2.5 supplied a known set; otherwise skip silently — Phase 5.5 takes this step once it has a set. Run `multi-component-prereqs` (`Skill(skill: "workflows-core:reference", args: "components multi-component-prereqs")`, §6) at `epics` scope. On `multi_component: false`, or where every prerequisite row is `present`, say nothing and continue.

Otherwise the PRD spans two or more components without the artifacts that fix how they fit together — the ARD's `## Contracts` and a PRD-level `specification.md`. Ask once, naming each row that is not `present` with its state:

```
"This PRD spans <N> components, and <each missing artifact, with its state> is not on the specs repo's default branch. Epics split without them are designed in isolation and may not fit together after /implement."
choices: ["Stop — run <the earliest missing command, §6> first (Recommended)", "Split without <the missing artifacts>", "Cancel"]
```

- **Stop** → stop, naming that command and every other missing artifact in ladder order.
- **Split without** → record the override for Phase 9's `### Targets` and continue: every Epic still gets one target, and where `ard_contract` is not `present`, no Epic gets a `## Contract` section.
- **Cancel** → stop.

---

## Phase 3 — Read the PRD folder
>>>>>>> NEW
<<<<<<< OLD 1
If the auto-derived list is empty, fall back to asking the user.
=======
If the auto-derived list is empty, fall back to asking the user. **Where Phase 2.5 supplied a known set**, add its components' repositories to whichever list this step derived, deduped, so every component the ARD names is scanned, and carry each component's `paths` to that repository's Phase 5 brief.
>>>>>>> NEW
<<<<<<< OLD 1
  >   paths:    [directory globs inferred from themes, or []]
=======
  >   paths:    [the `paths` of this repository's known-set components where Phase 2.5 supplied a set, else directory globs inferred from themes, or []]
>>>>>>> NEW
<<<<<<< OLD 1
## Phase 6 — Write Epics
=======
## Phase 5.5 — Components (only without an ARD set)

Skip where Phase 2.5 supplied a known set. Where code scan is OFF there is nothing to propose from: the run has **no known set**, Phase 6 writes no `target:`, and Phase 9's `### Targets` says so.

1. For each repository Phase 5 scanned, run `enumerate-components` (`workflows-core:components` §2) and place each scanner evidence path with `component-of` (§1.1). Propose the components that evidence and the PRD themes touch — never every module a repository declares.
2. **One component proposed** → it is the run's known set, and nothing is asked: a one-component PRD meets no question it did not meet before.
3. **Two or more** → show each with the themes and evidence paths that placed it, and ask:
   ```
   "This PRD touches <N> components. Each Epic will target exactly one of them."
   choices: ["Confirm these components (Recommended)", "Adjust the list (you'll be prompted)", "Cancel"]
   ```
   **Adjust** → take free text to keep, drop, add or group components (§5), re-show the list, and ask again. The confirmed list is the run's known set (§3, source `epics-run`). **Cancel** → stop.
4. **None proposed** (no evidence path falls in any component) → no known set; Phase 9 says why.
5. With two or more confirmed, run Phase 2.7 now, exactly as written there; with no ARD, its `ard_contract` row is `missing`.

---

## Phase 6 — Write Epics
>>>>>>> NEW
<<<<<<< OLD 1
and `docs_grounding` (the Phase 3.6 digest, or omit when OFF/EMPTY). Record its absolute path.
=======
`components`, `multi_component` and `contracts` (the known set from Phase 2.5 or 5.5, whether it has two or more entries, and the ARD's interface rows with their landing order — omit each where the run has none), and `docs_grounding` (the Phase 3.6 digest, or omit when OFF/EMPTY). Record its absolute path.
>>>>>>> NEW
<<<<<<< OLD 1
  > applicable_ard:       [the Phase 2.5 invariants, or omit if status was none]"
=======
  > applicable_ard:       [the Phase 2.5 invariants, or omit if status was none]
  > components:           [the known set, `multi_component`, and the ARD's `contracts` where present — or omit entirely where the run has no known set]"
>>>>>>> NEW
<<<<<<< OLD 1
### Epic review verdict
=======
### Targets
- Known set: [<N> components — from the ARD | confirmed at Phase 5.5] — _or_ "none — <no ARD set and code scan off | no component proposed>"
- [<EPIC-KEY>] → <target> — produces [AD#…]; consumes [AD#…]
- ...
- Contract: [present | N/A — one component | split without <the missing artifacts> at the Phase 2.7 stop]

### Epic review verdict
>>>>>>> NEW
<<<<<<< OLD 1
- ARD steps (Phase 2.5, writer/reviewer `applicable_ard`, the Phase 9 ARD section) are ADDITIVE and guarded on `status: found` — a run with no ARD is byte-identical to before
=======
- ARD steps (Phase 2.5, writer/reviewer `applicable_ard`, the Phase 9 ARD section) are ADDITIVE and guarded on `status: found` — a run with no ARD is byte-identical to before, save three things the components rules add: Phase 5.5, which asks only where a scan proposes two or more components; the `target:` a known set puts on each Epic; and Phase 9's `### Targets` section
- ALWAYS give every Epic exactly one `target:` from the known set where the run has one (`workflows-core:components`), and NEVER a target outside it; a capability spanning components is split into one Epic per component
>>>>>>> NEW
<<<<<<< OLD 1
this is the common case, and PRD-level `/specify` remains optional.
=======
this is the common case, and PRD-level `/specify` remains optional — save on a multi-component PRD, where Phase 2.7 asks for it.
>>>>>>> NEW
<<<<<<< OLD 1
  proceed exactly as before.** No prompt, no extra output.
=======
  proceed exactly as before.** No prompt, no extra output — save Phases 2.7 and 5.5 on a multi-component PRD, the one exception `workflows-core:ard-resolution`'s no-regression rule states.
>>>>>>> NEW
`````

#### `edits/aw-grilling.txt`

`````text
<<<<<<< OLD 1
- **Engineering altitude** (`/specify`, `/design`): the full **NFR** set (performance, scalability, reliability, observability, security/compliance); **integration / external-dependency** gaps; **implicit enum branch** (a field with N values where only some are specified — the rest are an untested branch).
=======
- **Engineering altitude** (`/specify`, `/design`): the full **NFR** set (performance, scalability, reliability, observability, security/compliance); **integration / external-dependency** gaps; **implicit enum branch** (a field with N values where only some are specified — the rest are an untested branch).
- **Cross-component** (any caller whose run has two or more components — `${CLAUDE_PLUGIN_ROOT}/references/components.md` §3; in practice `/create-ard`, `/specify` and `/design`): an **interface with no producer**; a **consumer with no stub** to test against; a shape with **no version or compatibility rule**; an **unstated landing order**; **schema ownership** claimed by two sides, or by none.
>>>>>>> NEW
`````

#### `edits/aw-implement.txt`

`````text
<<<<<<< OLD 1
  - **PRD with exactly 1 Epic** → no picker; set `focus_key` to that Epic and proceed, with the
=======
  - **On a multi-component PRD** — `multi-component-test` (`Skill(skill: "workflows-core:reference", args: "components multi-component-test")`, §3) run on the PRD folder returns `multi_component: true` — a flat `specification.md` is a requirements source, never a unit implemented whole (`${CLAUDE_PLUGIN_ROOT}/references/workflow-states.md`, *Ready for Implementation*). So every branch below reads as though the PRD folder held no flat `specification.md` — exactly 1 Epic is auto-selected, and ≥2 Epics show the picker without the broad-slice choice — save **0 Epics**, which asks `choices: ["Split into Epics first — /product-workflows:epics <PRD> (Recommended)", "Implement one broad PRD-level slice anyway"]`. On `multi_component: false`, nothing here applies.
  - **PRD with exactly 1 Epic** → no picker; set `focus_key` to that Epic and proceed, with the
>>>>>>> NEW
<<<<<<< OLD 1
so the look below can read the ARD's rules; Phase 1.8 acts on what it found.
=======
so the look below can read the ARD's rules; Phase 1.8 acts on what it found.

**Then, on a keyed run whose unit is an Epic (`focus_key` set), the multi-component check.** Run `multi-component-prereqs` (`Skill(skill: "workflows-core:reference", args: "components multi-component-prereqs")`, §6) at `implement` scope. On `multi_component: false`, say nothing: the run is unchanged. Otherwise — the one place a keyed run asks about an ARD that Phase 1.8 found `none`, the exception `workflows-core:ard-resolution`'s no-regression rule states — print one line naming the Epic's target, then:

- **`target_repo_matches: false`** → ask `choices: ["Stop — run /dev-workflows:implement <EPIC> in <the target's repository> (Recommended)", "Implement here anyway", "Cancel"]`. **Stop** and **Cancel** stop.
- **`target_repo_matches: unknown`** → one line saying the target was not compared, this repository having no `origin`; no question.
- **A prerequisite row that is not `present`, or a `coverage_gaps` entry naming this Epic** → ask once, naming each: `choices: ["Stop — run <the earliest missing command, §6> first (Recommended)", "Implement without them", "Cancel"]`. **Stop** and **Cancel** stop.

On **Implement here anyway** or **Implement without them**, carry what was overridden — the target mismatch, each missing artifact with its state, each coverage gap by `AD#N` — to the Phase 5 report's `### Assumptions & limitations` and to Phase 4.6's `body_facts`, which names it under the pull request's *Merge danger*.
>>>>>>> NEW
<<<<<<< OLD 1
that trigger and the paths that show it, as the reason no review ran.
=======
that trigger and the paths that show it, as the reason no review ran; and, where Phase 1's multi-component check was overridden, what was overridden — the target mismatch, each missing artifact, each contract gap by `AD#N` — which Merge danger names.
>>>>>>> NEW
`````

#### `edits/aw-prelint.txt`

`````text
<<<<<<< OLD 1
- Each `### [AD#N]` block carries all three sub-fields `**Binds:**`, `**Prevents:**`, `**Rule:**`
  (a missing one → MAJOR).
=======
- Each `### [AD#N]` block carries all three sub-fields `**Binds:**`, `**Prevents:**`, `**Rule:**`
  (a missing one → MAJOR).
- **Contracts — only when the frontmatter `components:` has two or more entries** (`${CLAUDE_PLUGIN_ROOT}/references/components.md` §5). `## Contracts` is then a required heading (missing → BLOCKER), with `### Schema ownership`, `### Versioning and compatibility` and `### Landing order` under it (a missing one → MAJOR). Every interface-table row's `AD` cell names an `[AD#N]` that has a `### [AD#N]` heading (else BLOCKER); every `Producer` and `Consumers` value is an `id` in `components:` (else MAJOR); every `Status` is `new`, `changed` or `exists` (else MAJOR). With fewer than two entries `## Contracts` is not required, and its absence is not reported.
>>>>>>> NEW
`````

#### `edits/aw-readiness-reviewer.txt`

`````text
<<<<<<< OLD 1
- **Phase 3 skeleton** — the coverage matrix, the status-expectation table, and the repo-availability
  result assembled before this reviewer runs.
=======
- **Phase 3 skeleton** — the coverage matrix, the status-expectation table, and the repo-availability
  result assembled before this reviewer runs.
- **`multi_component`** (optional) — Phase 3(d)'s Targets and Contract coverage tables, present only on a PRD whose components are two or more. When omitted, the *Cross-Epic contract coverage* dimension reports `N/A — one component`.
>>>>>>> NEW
<<<<<<< OLD 1
| Repo availability (best-effort) |
=======
| Cross-Epic contract coverage (conditional) | Only when `multi_component` is provided. Every finding its tables carry stands, at no less than MAJOR: an Epic with no target or one outside the set; an interface a consumer uses that no Epic produces; one produced by an Epic that does not target its producer; a consumer whose Dependencies do not name its producer. Then what a table cannot see, each MAJOR: an Epic whose scope or spec plainly uses an interface its `## Contract` does not cite; a contract Epic (one producing a row whose artifact is a code file) that does not come before its consumers in the ARD's landing order; two Epics whose specs or designs describe one interface differently. |
| Repo availability (best-effort) |
>>>>>>> NEW
<<<<<<< OLD 1
#### Repo availability
=======
#### Cross-Epic contract coverage
- _"N/A — one component"_ when `multi_component` was omitted, else findings.

#### Repo availability
>>>>>>> NEW
`````

#### `edits/aw-ready.txt`

`````text
<<<<<<< OLD 1
**Where that `specification.md` is present, the PRD folder is a broad PRD-level slice beside its Epics**
=======
**On a multi-component PRD** — `multi-component-test` (`Skill(skill: "workflows-core:reference", args: "components multi-component-test")`, §3) run on `<PRD-dir>` returns `multi_component: true` — that `specification.md` is a requirements source and never a slice (`${CLAUDE_PLUGIN_ROOT}/references/workflow-states.md`, *Ready for Implementation*): no `design.md` is located for it, Phase 2 carries no slice row for it, and it counts instead among the PRD row's own expected artifacts. **Otherwise, where that `specification.md` is present, the PRD folder is a broad PRD-level slice beside its Epics**
>>>>>>> NEW
<<<<<<< OLD 1
one more row for the **broad
  PRD-level slice** (Phase 1 step 2),
=======
one more row for the **broad PRD-level slice** (Phase 1 step 2 — never on a multi-component PRD),
>>>>>>> NEW
<<<<<<< OLD 1
- **`status: found`** → carry the returned `invariants`
=======
- **On `status: found` or `unmerged`**, also carry the returned `components` and `contracts` to Phase 3(d).
- **`status: found`** → carry the returned `invariants`
>>>>>>> NEW
<<<<<<< OLD 1
1. Derive candidate repo names from: each in-scope Epic's `implementation.md` entries, and the
=======
1. Derive candidate repo names from: each in-scope Epic's `target:` repository (the id up to any `:`, `workflows-core:components` §1); each in-scope Epic's `implementation.md` entries, and the
>>>>>>> NEW
<<<<<<< OLD 1
normal case pre-implementation and must not read as a gap.
=======
normal case pre-implementation and must not read as a gap.

**(d) Targets and contract coverage (multi-component PRDs only).** Run `multi-component-prereqs` (`Skill(skill: "workflows-core:reference", args: "components multi-component-prereqs")`, §6) at `ready` scope. On `multi_component: false`, record `N/A — one component` and add nothing. Otherwise build two tables, orchestrator-inline:

- **Targets** — one row per Epic: its target, or `none`, and whether it is in the set where the ARD supplied it. An Epic with no target, or one outside the set, is a finding at no less than MAJOR.
- **Contract coverage** — one row per interface row of the ARD's `contracts` (its `AD#N`, producer, consumers and status) with the Epics that produce and consume it, then every `coverage_gaps` entry by `AD#N`, each a finding at no less than MAJOR. Where the ARD has no `## Contracts`, the table reads `no contract`: Phase 3(b) already marks that expected artifact ❌, and this table adds nothing to it.
>>>>>>> NEW
<<<<<<< OLD 1
  > repo_availability:       [paste Phase 3(c)]
=======
  > repo_availability:       [paste Phase 3(c)]
  > multi_component:         [paste Phase 3(d)'s two tables — or omit this line entirely where it recorded N/A]
>>>>>>> NEW
<<<<<<< OLD 1
   ## Repo availability
   <Phase 3(c) result>
=======
   ## Contract coverage
   <Phase 3(d)'s two tables — omit this section where it recorded N/A>

   ## Repo availability
   <Phase 3(c) result>
>>>>>>> NEW
<<<<<<< OLD 1
   ### Repo availability
   [Phase 3(c) result]
=======
   ### Contract coverage
   [Phase 3(d)'s two tables] — _omit this whole section where Phase 3(d) recorded N/A_

   ### Repo availability
   [Phase 3(c) result]
>>>>>>> NEW
<<<<<<< OLD 1
(a PRD-level spec is optional per `workflow-states.md`)
=======
(a PRD-level spec is optional per `workflow-states.md`, save on a multi-component PRD)
>>>>>>> NEW
`````

#### `edits/aw-rules-dw.txt`

`````text
<<<<<<< OLD 1
/implement           → [require-on-main: in-scope specification.md/design.md] →
=======
/implement           → [require-on-main: in-scope specification.md/design.md] → [keyed Epic of a multi-component PRD: multi-component-prereqs at implement scope — target repository, prerequisites, this Epic's contract coverage; a gap asks Stop (Recommended) / continue] →
>>>>>>> NEW
<<<<<<< OLD 1
/design              → [require-on-main: specification.md] → [code-scanner×N (parallel, cap 4, STRICT gate)]
=======
/design              → [require-on-main: specification.md; a multi-component PRD's flat spec is never designed whole — Epic picker] → [an Epic's target: its repository alone] → [code-scanner×N (parallel, cap 4, STRICT gate)]
>>>>>>> NEW
<<<<<<< OLD 1
→ read the resolved folder → verify ARD/spec/design → [readiness-reviewer@Opus]
=======
→ read the resolved folder → verify ARD/spec/design → [multi-component PRD: multi-component-prereqs at ready scope — targets + contract coverage] → [readiness-reviewer@Opus]
>>>>>>> NEW
<<<<<<< OLD 1
### Key invariants for `/implement` specifically
=======
### Multi-component PRDs (`workflows-core:components`)

- On a multi-component PRD the flat PRD-level `specification.md` is a requirements source: `/design <PRD>` and `/implement <PRD>` never take it as one unit (Epic picker; with no Epic, `/epics` first is recommended), and `workflow-states.md`'s *Ready for Implementation* expects no PRD-level `design.md`
- `/design` keeps a targeted Epic's design in its target's repository; a second repository is a `Target span` risk `design-reviewer` flags. `/implement`'s Phase 1 check and `/ready`'s Phase 3(d) run one definition, `multi-component-prereqs` (§6), which writes nothing and never stops — the caller decides

### Key invariants for `/implement` specifically
>>>>>>> NEW
`````

#### `edits/aw-rules-pw.txt`

`````text
<<<<<<< OLD 1
→ [require-on-main: PRD-level specification.md] → read the resolved folder → [docs-grounder] → [code-scanner×N (parallel, optional)] → writing →
=======
→ [require-on-main: PRD-level specification.md] → [multi-component-prereqs: Contracts + PRD-level spec, where the ARD's components are ≥2] → read the resolved folder → [docs-grounder] → [code-scanner×N (parallel, optional)] → [no ARD set: confirm components, asked only where ≥2 are proposed; then the same prereqs] → writing (one target per Epic) →
>>>>>>> NEW
<<<<<<< OLD 1
[ls $REPOS_PATH → code-scanner×N (confirmed set, parallel, cap 4)]
=======
[ls $REPOS_PATH → enumerate-components → confirm components → code-scanner×N (confirmed set, parallel, cap 4)]
>>>>>>> NEW
<<<<<<< OLD 1
- `/create-ard` grounds on mounted repos it discovers (`$REPOS_PATH` listing + theme→repo proposal + confirm/mount-or-descope); it never reads PRs
=======
- `/create-ard` grounds on mounted repos it discovers (`$REPOS_PATH` listing + theme→component proposal, `workflows-core:components` §2 + confirm/mount-or-descope); it never reads PRs. At PRD level it writes the confirmed list to `components:` and, with two or more, authors `## Contracts`
- **On a multi-component PRD** (`workflows-core:components` §3) every Epic has one `target:`, the PRD-level ARD carries `## Contracts`, and the PRD-level spec is a requirements source designed and implemented only through its Epics. `/epics` and `/implement` stop with a recommended way forward where the contract or a prerequisite artifact is missing, offering to continue without it; `/ready` caps its verdict instead. A single-component PRD meets none of this beyond the `target:` on its Epics
>>>>>>> NEW
`````

#### `edits/aw-rules-wc.txt`

`````text
<<<<<<< OLD 1
`workflows-core` carries thirty reference files
=======
`workflows-core` carries thirty-one reference files
>>>>>>> NEW
<<<<<<< OLD 1
## Workflow map

The `workflows-core` command's line of the family workflow map
=======
`plugins/workflows-core/references/components.md` is the **single source of truth** for what a **component** is — a repository, or a set of paths inside one — and its id; `enumerate-components`, which proposes a repository's modules from what it declares and nothing else; the **multi-component test** and its three sources, of which only the ARD's `components:` is a set a target can be checked *in*; the **ride-along** rule for same-repository deploy components; the ARD `components:` entry; and `multi-component-prereqs`, the read-only check `/epics` (at `epics` scope), `/implement` and `/ready` share, which writes nothing, asks nothing and never stops. Its citing files are what `grep -l 'workflows-core:components\|args: "components' plugins/*/commands/*.md plugins/*/agents/*.md plugins/*/references/*.md` lists; `epic-reviewer`, `design-reviewer` and `readiness-reviewer` apply its rules from their briefs without loading it.

## Workflow map

The `workflows-core` command's line of the family workflow map
>>>>>>> NEW
`````

#### `edits/aw-specify.txt`

`````text
<<<<<<< OLD 1
Pass the `invariants` to `spec-reviewer` in Phase 6 as `applicable_ard`.
=======
Pass the `invariants` to `spec-reviewer` in Phase 6 as `applicable_ard`. Also carry the returned `contracts` (`workflows-core:components` §3, §6) into Phase 5.
>>>>>>> NEW
<<<<<<< OLD 1
2. **Build the slug→clone map** (`/epics`-style).
=======
   **An Epic with a target.** Where `focus_key` is set and the Epic's `epic.md` carries a `target:` (`Skill(skill: "workflows-core:reference", args: "components")` §1), the candidate list is that target's repository alone, and the themes add no other: what the Epic needs from another component is the interface the PRD-level ARD's `contracts` fixes, read there and never by scanning its producer. Phase 4's scan of the repository passes the target's `paths` (the ARD's `components` entry for it, else the id's own path) as `search_hints.paths`.

2. **Build the slug→clone map** (`/epics`-style).
>>>>>>> NEW
<<<<<<< OLD 1
  >   paths:    [directory globs inferred from themes, or []]
=======
  >   paths:    [the target's `paths` where Phase 3 narrowed to an Epic's target, else directory globs inferred from themes, or []]
>>>>>>> NEW
<<<<<<< OLD 1
5. **Test cases** (`[TCxx]`)
=======
5. **Test cases** (`[TCxx]`)

**A multi-component PRD at PRD level** (`workflows-core:components` §3, with `focus_key` null): the ARD's interface rows carried from Phase 2.5 are grill ground truth. An acceptance criterion or test case that crosses components names, in its own text, the `[AD#N]` interface it crosses, so `/epics` can split it per side and each side's Epic can test against it; the grill's *Cross-component* gap category applies (`workflows-core:grilling-technique`). The specification format is unchanged.
>>>>>>> NEW
`````

#### `edits/aw-wc-references.txt`

`````text
<<<<<<< OLD 1
`workflows-core` bundles 30 files under `references/` — 26 top-level markdown files, `cost-prices.yaml`, one file under `model-routing/`, and one bundled subtree. This page enumerates every file except the two under `handoff/` (28 of the 30 — the 26 top-level files plus `cost-prices.yaml` plus `model-routing/classification.md`), grouped by concern below, then counts that one subtree rather than listing each file inside it. The arithmetic: 28 named individually, plus 2 markdown pages counted (not enumerated) in `handoff/` — 28 + 2 = 30, against 30 files on disk.
=======
`workflows-core` bundles 31 files under `references/` — 27 top-level markdown files, `cost-prices.yaml`, one file under `model-routing/`, and one bundled subtree. This page enumerates every file except the two under `handoff/` (29 of the 31 — the 27 top-level files plus `cost-prices.yaml` plus `model-routing/classification.md`), grouped by concern below, then counts that one subtree rather than listing each file inside it. The arithmetic: 29 named individually, plus 2 markdown pages counted (not enumerated) in `handoff/` — 29 + 2 = 31, against 31 files on disk.
>>>>>>> NEW
<<<<<<< OLD 1
cited by every command that must honor an ARD's invariants as implementation guardrails.
=======
cited by every command that must honor an ARD's invariants as implementation guardrails. It also returns the PRD-level ARD's `components` and `contracts`, which `components.md` reads.
- `components.md` — what a component is (a repository, or a set of paths inside one) and its id; `enumerate-components`, which proposes a repository's modules from what it declares; the multi-component test and its three sources; the ride-along rule for deploy components; the ARD `components:` entry; and `multi-component-prereqs`, the read-only check `/epics`, `/implement` and `/ready` share. Cited by `/create-ard`, `/epics`, `/specify`, `/design`, `/ready` and `/implement`, and by `epic-writer`, `epic-reviewer` and `design-reviewer`.
>>>>>>> NEW
`````

#### `edits/aw-workflow-states.txt`

`````text
<<<<<<< OLD 1
# Workflow states (embedded — shared reference)
=======
# Workflow states (embedded — shared reference)

**Core references.** A citation of the form `workflows-core:<name>` names a shared reference in the `workflows-core` plugin. Load it with `Skill(skill: "workflows-core:reference", args: "<name>")` — never by path: `${CLAUDE_PLUGIN_ROOT}` resolves to this plugin, which does not carry it.
>>>>>>> NEW
<<<<<<< OLD 1
| Ready for Implementation | PE→Dev | /epics, /specify, /design | Epics defined, or a broad PRD-level slice — the PRD folder holding a flat specification.md — or both; each in-scope Epic, and the slice where one stands, Refined+ with specification.md AND design.md; coverage complete; ARD (if any) respected; no cross-artifact contradictions |
=======
| Ready for Implementation | PE→Dev | /epics, /specify, /design | Epics defined, or a broad PRD-level slice — the PRD folder holding a flat specification.md — or both; each in-scope Epic, and the slice where one stands, Refined+ with specification.md AND design.md; coverage complete; ARD (if any) respected; no cross-artifact contradictions. **On a multi-component PRD** (below): the ARD with `## Contracts`, the PRD-level specification.md, Epics defined, and each in-scope Epic Refined+ with specification.md AND design.md — no PRD-level design.md |
>>>>>>> NEW
<<<<<<< OLD 1
## Epic status ladder
=======
**A multi-component PRD** (`workflows-core:components` §3 — its known set has two or more components) reads the *Ready for Implementation* row's second clause. There the flat `specification.md` is a **requirements source**: its end-to-end acceptance criteria are split across one-component Epics, each designed and implemented on its own, so the slice is never a unit of design or implementation and no PRD-level `design.md` is expected. The ARD's `## Contracts` is what makes those Epics fit together, which is why it is expected there rather than optional. A single-component PRD reads the first clause, unchanged.

## Epic status ladder
>>>>>>> NEW
<<<<<<< OLD 1
The rubric is advisory: an org may skip an optional artifact (e.g. no ARD) — that downgrades to a MINOR finding, never a hard block on its own.
=======
The rubric is advisory: an org may skip an optional artifact (e.g. no ARD) — that downgrades to a MINOR finding, never a hard block on its own. **Except on a multi-component PRD**, where the ARD with `## Contracts` and the PRD-level specification are expected artifacts of *Ready for Implementation* (above): their absence leaves the PRD below that rung, as any other missing expected artifact does.
>>>>>>> NEW
`````

## Appendix C — the new reference

Extracted by Task 0 Step 2 into `$S/files`; Task 1 copies it to `plugins/workflows-core/references/components.md`.

#### `files/components.md`

`````markdown
# Components (embedded — shared reference)

Single source of truth for what a **component** is, how a repository's components are proposed, when a PRD is **multi-component**, the **ride-along** rule, and the `multi-component-prereqs` check. `/create-ard`, `/epics`, `/specify`, `/design`, `/ready` and `/implement` cite this file, as do `epic-writer`, `epic-reviewer` and `design-reviewer`. None of them keeps a copy of a rule stated here.

**Why it exists.** `/implement` changes code in one repository per run, so an Epic that spans two repositories is half a companion change before any code is written. A PRD that changes a client and a server, or several modules of one repository, is therefore split into one Epic per component, and the interfaces between the components are fixed in the PRD-level ARD's `## Contracts` section (`product-workflows:ard-format`) so that the Epics on either side fit together after each is implemented on its own.

## 1. Component and id

A **component** is a repository, or a set of paths inside one repository, that an Epic can target. Its **id** is:

- `<repo-slug>` for a whole repository — `client-repo`;
- `<repo-slug>:<path>` for a module inside one — `bookstore:orders`, `bookstore:k8s`, `bookstore:.github/workflows`.

`<repo-slug>` is derived the way every slug→clone map in this family derives it: `timeout 5 git -C <dir> remote get-url origin 2>/dev/null`, a trailing `.git` stripped, the URL's last path segment. `<path>` is relative to the repository's top level, POSIX-separated, with no leading `./` and no trailing `/`.

A component also has a **kind** — `code` (the default) or `deploy` — and its **paths**: the id's own `<path>`, the whole repository for a bare slug, or the list a confirmer grouped under it (§5).

### 1.1 `component-of <repo-slug> <path>`

A path inside a repository belongs to the component of that repository whose paths hold the **longest** prefix of it, compared segment by segment; a bare-slug component holds every path of its repository. A path no component of the set holds belongs to none, and is reported as such — never assigned to the nearest-looking one.

## 2. `enumerate-components <repository top level>`

Proposes the components a repository **declares**. It reads these, and nothing else:

| Source | Read | Each entry becomes |
|---|---|---|
| Gradle | `settings.gradle` / `settings.gradle.kts` `include` entries | `:a:b` → path `a/b`. Where `project(':x').projectDir` is set to a literal path, that path; where it is set any other way, the module is proposed with a note that its path is unresolved, and the confirmer supplies it |
| Maven | the top-level `pom.xml` `<modules>` | each `<module>` path |
| npm / yarn | the top-level `package.json` `workspaces` (array, or its `packages` field) | each glob, expanded against the tree |
| pnpm | `pnpm-workspace.yaml` `packages` | each glob, expanded against the tree |
| Cargo | the top-level `Cargo.toml` `[workspace] members` | each glob, expanded |
| Go | `go.work` `use` | each directory |
| Top-level build file | every top-level directory not already proposed holding `package.json`, `pom.xml`, `build.gradle`, `build.gradle.kts`, `Cargo.toml`, `go.mod` or `pyproject.toml` | that directory, `kind: code` |
| Deploy or config | the top-level directories `k8s`, `helm`, `charts`, `terraform`, `deploy`, and `.github/workflows` | that directory, `kind: deploy` |

Every build-system entry is `kind: code`. A repository with none of these is **one component**, its id the bare slug.

**The output is a proposal, never a set.** The confirmer — the architect in `/create-ard`, the user in `/epics` Phase 5.5 — keeps, drops, adds and groups entries (§5). A directory the table does not name (a lambda folder with only scripts, a `database/` of init files) is not proposed; the confirmer adds it where a PRD touches it. That gap is the honest result of reading only what the repository declares, and a wider pattern is not the answer to it (`CLAUDE.md` § Editing discipline, *resolve an identifier against a known set*).

Worked example: `bookstore` (a Gradle multi-project) proposes fourteen — its eleven `include`d modules, `web` (code, through `web/package.json`), and `k8s` and `.github/workflows` (deploy).

## 3. `multi-component-test <PRD folder>`

Returns `{multi_component, set, set_source}`. The **known set** comes from the first of these that exists:

1. **`ard`** — the PRD-level ARD's `components:` (`product-workflows:ard-format`), read through `workflows-core:ard-resolution`'s `components` field. An ARD with no `components:` key (every ARD written before this reference existed) supplies nothing, and the next source is tried.
2. **`epics-run`** — inside one `/epics` run with no ARD set, the set its Phase 5.5 confirmed.
3. **`epic-targets`** — the distinct `target:` values of the `epic.md` files directly under the PRD folder.

`multi_component` is true when the set has **two or more** entries. With no source, the set is empty and the PRD is not multi-component.

The third source is what keeps a PRD that `/epics` split without an ARD — its prerequisites stop's override (§6) — multi-component for `/design`, `/ready` and `/implement`, which have no ARD set to read. **A target is checked as being *in* the set only where the source is `ard`**; the other two sources are the targets themselves.

## 4. Ride-along

An Epic may change files of a `kind: deploy` component **in the same repository as its target**, where those files exist only to deploy or configure the target — its Deployment manifest, its environment variable, its pipeline job — without that component counting as a second target. It declares each one under `### In scope`:

    - Also touches: <component id> — <why>

Two limits, both enforced by `epic-reviewer` and `design-reviewer`:

- **Same repository only.** A deploy component in another repository (a separate gitops repository) is never ridden along: `/implement` cannot change it in the same run, so it is its own Epic.
- **`kind: deploy` only.** A `kind: code` component is never ridden along; a change there is a second target, and the Epic splits.

A deploy component is still a target in its own right — for an infrastructure-only PRD, or where a change there is the work rather than support for it.

## 5. The ARD `components:` entry

The PRD-level ARD's `components:` frontmatter (`product-workflows:ard-format`) lists the components **this PRD touches** — not every module the repository has:

```yaml
components:
  - id: bookstore:orders
  - id: bookstore:common
    paths: [common, exceptions]
  - id: bookstore:k8s
    kind: deploy
```

`kind` defaults to `code`; `paths` defaults to the id's own path, or the whole repository for a bare slug. **`paths` is how a confirmer groups**: two modules that always change together become one component, so they are never forced into two Epics. A grouped component's id names one of its paths. Every entry's repository is in the ARD's `grounded_repos`, or is named under its `## Open questions`.

## 6. `multi-component-prereqs`

Inputs: the resolved PRD folder and its key, the Epic key (or null), and `scope` — `epics`, `implement` or `ready`. **It writes nothing, dispatches no agent, asks nothing and never stops**; each caller decides what a returned row means.

1. Run §3. Where `multi_component` is false, return `{multi_component: false}` and nothing else — the caller proceeds exactly as it did before this reference existed.
2. **Prerequisites** (`epics` and `implement` scope; at `ready` scope the Ready rung of `dev-workflows:workflow-states` already lists them). Each row is `present`, `not_on_default` (the file exists in the `$SPECS_PATH` worktree but not on `<default-ref>`) or `missing`, tested with `workflows-core:phase-handoff` §3.2's two read-only primitives — the ref-existence test, then `git -C "$SPECS_PATH" cat-file -e "<default-ref>:./<path>" 2>/dev/null` — and never with `require-on-main`, whose repair offer is a prompt. Where `<default-ref>` itself does not exist, every row is `unverified` with that reason.
   - `ard_contract` — the PRD folder's `ard.md`, **and** `ard-resolution`'s `contracts` not null. An ARD present without a `## Contracts` section is `missing`.
   - `prd_spec` — the PRD folder's flat `specification.md`.
   - `epic_spec`, `epic_design` (`implement` scope) — the Epic folder's `specification.md` and `design.md`.
3. **Target** (`implement` scope): the Epic's `target:`, or `none`; `in_set` where `set_source` is `ard`; and `target_repo_matches` — the target's `<repo-slug>` against the slug of the repository the run stands in (§1's derivation, from its top level): `true`, `false`, or `unknown` where that repository has no `origin`.
4. **Targets** (`ready` scope): one row per `epic.md` directly under the PRD folder — its key, its `target:` or `none`, and `in_set` where `set_source` is `ard`.
5. **Contract coverage**, where `ard-resolution`'s `contracts` is not null. Read every `epic.md` directly under the PRD folder for its `target:`, its `## Contract` lines (`- Produces: [AD#N] — …`, `- Consumes: [AD#N] — …`; every `[AD#N]` on such a line counts) and its `## Dependencies`. Then report each gap by `AD#N`:
   - `unknown_ad` — an Epic cites an `[AD#N]` that is not an interface row;
   - `consumed_unproduced` — an Epic consumes a row whose status is `new` or `changed`, and no Epic whose target is the row's producer produces it;
   - `produced_off_target` — an Epic produces a row whose producer is not its target;
   - `consumer_not_dependent` — a consumer's `## Dependencies` does not name, by key, the Epic that produces what it consumes;
   - `unproduced_row` (`ready` scope only) — a `new` or `changed` row no Epic produces.

   At `implement` scope only gaps naming this Epic — as consumer or producer — are returned. A row with status `exists` is satisfied by the code, so consuming it is never a gap.

Return shape:

```yaml
multi_component: true | false
set_source: ard | epics-run | epic-targets
prerequisites:            # epics and implement scope
  - {name: ard_contract | prd_spec | epic_spec | epic_design, state: present | not_on_default | missing | unverified, path: <path>, reason: <text or null>}
target: {id: <id or none>, in_set: true | false | null, target_repo_matches: true | false | unknown}   # implement scope
targets: [{epic: <key>, id: <id or none>, in_set: true | false | null}]                                 # ready scope
coverage_gaps: [{kind: unknown_ad | consumed_unproduced | produced_off_target | consumer_not_dependent | unproduced_row, ad: AD#N, epic: <key or null>, detail: <text>}]
```

**The earliest missing command**, which `/epics` and `/implement` recommend, is the first missing or `not_on_default` row in ladder order — `ard_contract` → `/product-workflows:create-ard <PRD>`, `prd_spec` → `/product-workflows:specify <PRD>`, `epic_spec` → `/product-workflows:specify <EPIC>`, `epic_design` → `/dev-workflows:design <EPIC>` — and, for a coverage gap alone, `/product-workflows:epics <PRD>`.

## Consumers (informative)

- `/create-ard` — Phase 3 proposes theme→component with §2 and writes the confirmed list to `components:` (§5); Phase 4 authors `## Contracts` when there are two or more.
- `/epics` — §3 for the known set; Phase 5.5 with §2 and §1.1 where no ARD supplies one; §6 at `epics` scope for its prerequisites stop; §4 in `epic-writer`'s rules.
- `/specify`, `/design` — the Epic's target narrows the repositories and the scan; §3 decides whether `/design <PRD>` designs a flat spec.
- `/ready` — §6 at `ready` scope for its targets and contract-coverage tables.
- `/implement` — §3 in its picker; §6 at `implement` scope at the start of Phase 1.
- `epic-writer`, `epic-reviewer`, `design-reviewer` — §1, §4 and §5.
`````

## Appendix D — changelog sections

Extracted by Task 0 Step 2 into `$S/cl`; `release.py` inserts each above its plugin's current top section, re-dated to the landing day.

#### `cl/aw-dev-workflows.md`

`````markdown
## [4.8.0] — 2026-10-04

**Update `workflows-core` to 1.12.0 with this release**, which carries the `components` reference these commands load.

### Added
- **Multi-component PRDs** (see `product-workflows` 3.13.0).
  - **`/implement`**: on a keyed run for an Epic of a multi-component PRD, Phase 1 checks the Epic's target against this repository, the ARD's contract, the PRD-level spec and the Epic's own spec and design, and this Epic's contract coverage; a gap asks Stop (Recommended) or continue, and continuing names the gap under the pull request's *Merge danger*.
  - **`/ready`**: a new Phase 3(d) builds Targets and Contract coverage tables, and the report gains a `Contract coverage` section; `readiness-reviewer` gains *Cross-Epic contract coverage*.
  - **`design-reviewer`** gains *Target & contract*.

### Changed
- **`/design <PRD>` and `/implement <PRD>` on a multi-component PRD** never take the flat PRD-level specification as one unit: they go to the Epic picker, and with no Epic recommend `/epics` first.
- **`/design` keeps a targeted Epic in its target's repository**: adding a second repository asks whether to re-split, and adding it anyway records a `Target span` risk.
- **`design-format`**: a `Target` header line, and `## Interfaces / contracts` names the ARD interfaces a design produces and consumes.
- **`workflow-states`**: on a multi-component PRD, *Ready for Implementation* expects the ARD with `## Contracts` and the PRD-level specification, and no PRD-level design.
`````

#### `cl/aw-product-workflows.md`

`````markdown
## [3.13.0] — 2026-10-04

**Update `workflows-core` to 1.12.0 with this release**, which carries the `components` reference these commands load.

### Added
- **Multi-component PRDs: one target per Epic, the contract in the ARD.** A PRD that changes more than one component — two repositories, or two modules of one repository — is split into one Epic per component, and the interfaces between them are fixed in the PRD-level ARD so the Epics fit together once each is implemented on its own.
  - **`/create-ard`** proposes theme→component, reading each repository's module declarations; the architect confirms, corrects, adds or groups, and the list is written to the ARD's new `components:` frontmatter. With two or more components the grill authors a new `## Contracts` section — an interface table (`AD#N`, producer, consumers, kind, status, artifact), schema ownership, versioning and compatibility, and landing order — and the next-step offer recommends a PRD-level `/specify` before `/epics`.
  - **`/epics`** gives every Epic one `target:` from the known set: the ARD's components, or, with no ARD, the components a new Phase 5.5 confirms after the scan (asked only where two or more are proposed). A new Phase 2.7 stops a multi-component PRD that lacks the ARD's contract or a PRD-level spec, recommending the earliest missing step, with "Split without them" recorded in the report's new `### Targets` section.
  - **`epic-writer`** splits a capability that spans components into one Epic per component in landing order, writes a `## Contract` section citing the interfaces each Epic produces or consumes, tests a consumer against a stub, puts a code-artifact contract in its own Epic first, and records a same-repository deploy change as an `- Also touches:` ride-along.
  - **`epic-reviewer`** gains *Single target* (a BLOCKER for no target, one outside the set, or scope spanning components) and *Contract citation*; *Epic independence* allows a consumer's dependency on its producer.
  - **`ard-reviewer`** gains *Contract completeness*.
  - **`/specify`** narrows an Epic's scan to its target, and at PRD level has cross-component acceptance criteria cite the interface they cross.

### Changed
- **`ard-format`**: the `components:` frontmatter and the `## Contracts` section; an interface row's `AD#N` meets the admission bar by being a cross-component interface.
`````

#### `cl/aw-workflows-core.md`

`````markdown
## [1.12.0] — 2026-10-04

**Update `product-workflows` to 3.13.0 and `dev-workflows` to 4.8.0 with this release**: their commands load `components`, which a `workflows-core` older than 1.12.0 does not carry.

### Added
- **`components`**, a new shared reference: a component is a repository or a set of paths inside one; `enumerate-components` proposes a repository's modules from what it declares (Gradle, Maven, npm/yarn/pnpm workspaces, Cargo, Go, top-level build files, deploy directories); the multi-component test reads the known set from the ARD's `components:`, from an `/epics` run's confirmed set, or from the Epics' `target:` values; the ride-along rule lets an Epic change a same-repository deploy directory that exists only to deploy its target; and `multi-component-prereqs` is the read-only check `/epics`, `/implement` and `/ready` share.
- **`grilling-technique`'s gap taxonomy gains a Cross-component category**: an interface with no producer, a consumer with no stub, an unversioned shape, an unstated landing order, and contested schema ownership.

### Changed
- **`ard-resolution` returns the PRD-level ARD's `components` and `contracts`** beside its invariants, on Epic-level resolutions too; `status: none` returns them empty, and a caller that ignores them is unchanged.
- **`pre-lint`'s ARD block requires `## Contracts` where `components:` has two or more entries**, and checks each interface row's `AD#N`, components and status.
`````
